"""Turn measured energy into CO2 and electricity cost.

For each phase (train, eval):
    system energy   = scope_factor x measured + scope_offset_w x duration  (total)
                    = scope_factor x net measured                            (net: the offset
                      is constant, so it cancels against the idle baseline)
    facility energy = system energy x PUE
    CO2             = facility energy x grid carbon intensity averaged over the phase

"net" is the energy the experiment added on top of idle (marginal view); "total"
also charges the idle power drawn while it ran (attributional view). The low and
high values are worst-case bounds combining sensor accuracy, scope calibration
error and grid-intensity uncertainty, not a statistical confidence interval.

Grid carbon intensity sources:
  fixed            - one value (--carbon-intensity), e.g. a national annual average
  energy-charts    - Fraunhofer ISE Energy-Charts: 15-min CO2eq intensity of public
                     net generation, European countries, no API key. Actual values
                     are published with a delay of about two hours; until then the
                     forecast is used.
  electricity-maps - Electricity Maps lifecycle intensity, any zone. Needs
                     ELECTRICITYMAPS_API_KEY; the free tier covers the last 24 h.
Any part of a phase a time-resolved source doesn't cover (offline, too old, not
published) uses the fixed value, and the result records how much did.

Recompute stored results later, e.g. once actual grid data replaces the forecast
or after calibrating the scope factor:
    python carbon.py update experiment_results [--scope-factor 1.8 ...]
"""
import argparse
import datetime
import glob
import json
import logging
import os
import time
import urllib.request
from typing import Dict, List, Optional, Tuple

# Assumed relative uncertainty of each kind of grid intensity value
INTENSITY_UNCERTAINTY = {"actual": 0.10, "estimated": 0.15, "forecast": 0.20, "fixed": 0.30}

# Settings, keyed by argparse dest; stored with each result so it can be recomputed
DEFAULTS = {
    "carbon_source": "fixed",
    "carbon_zone": None,
    "fixed_carbon_intensity": 480.0,  # gCO2/kWh, roughly the world average
    "carbon_intensity_uncertainty": None,  # None: per kind, see INTENSITY_UNCERTAINTY
    "pue": 1.0,
    "scope_factor": 1.0,
    "scope_offset_w": 0.0,
    "scope_uncertainty": 0.0,
    "electricity_price": 0.15,  # USD/kWh, placeholder
}

Point = Tuple[float, float, str]  # (unix start of interval, gCO2/kWh, kind)


def _get_json(url: str, headers: Optional[Dict] = None):
    request = urllib.request.Request(url, headers={"User-Agent": "SLM-Bench", **(headers or {})})
    with urllib.request.urlopen(request, timeout=15) as response:
        return json.load(response)


class EnergyCharts:
    name = "energy-charts"
    resolution_s = 900

    def __init__(self, zone: str):
        self.country = zone.lower()

    def points(self, start: float, end: float) -> List[Point]:
        def iso(t):
            return datetime.datetime.fromtimestamp(t, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

        data = _get_json(
            f"https://api.energy-charts.info/co2eq?country={self.country}"
            f"&start={iso(start)}&end={iso(end)}"
        )
        forecasts = data.get("co2eq_forecast") or [None] * len(data["unix_seconds"])
        points = []
        for t, actual, forecast in zip(data["unix_seconds"], data["co2eq"], forecasts):
            if actual is not None:
                points.append((t, actual, "actual"))
            elif forecast is not None:
                points.append((t, forecast, "forecast"))
        return points


class ElectricityMaps:
    name = "electricity-maps"
    resolution_s = 3600
    base = "https://api.electricitymaps.com/v3/carbon-intensity"

    def __init__(self, zone: str):
        self.zone = zone.upper()
        self.token = os.environ.get("ELECTRICITYMAPS_API_KEY")
        if not self.token:
            raise SystemExit("--carbon-source electricity-maps needs ELECTRICITYMAPS_API_KEY")

    def points(self, start: float, end: float) -> List[Point]:
        headers = {"auth-token": self.token}
        rows = _get_json(f"{self.base}/history?zone={self.zone}", headers).get("history", [])
        if end > time.time() - self.resolution_s:  # the current hour isn't in history yet
            rows.append(_get_json(f"{self.base}/latest?zone={self.zone}", headers))
        points = {}
        for row in rows:
            t = datetime.datetime.fromisoformat(row["datetime"].replace("Z", "+00:00")).timestamp()
            t -= t % self.resolution_s
            kind = "estimated" if row.get("isEstimated") else "actual"
            points[t] = (t, row["carbonIntensity"], kind)
        return list(points.values())


PROVIDERS = {p.name: p for p in (EnergyCharts, ElectricityMaps)}


def window_intensity(
    points: List[Point], resolution_s: float, start: float, end: float, fallback: float
) -> Tuple[float, Dict[str, float]]:
    """Time-weighted mean intensity over [start, end] and the share of each kind.

    Time no point covers uses `fallback` and counts as kind "fixed".
    """
    end = max(end, start + 1e-3)
    weighted, seconds = 0.0, {}
    for t, value, kind in points:
        overlap = min(end, t + resolution_s) - max(start, t)
        if overlap > 0:
            weighted += value * overlap
            seconds[kind] = seconds.get(kind, 0.0) + overlap
    span = end - start
    missing = span - sum(seconds.values())
    if missing > 1e-6:
        weighted += fallback * missing
        seconds["fixed"] = seconds.get("fixed", 0.0) + missing
    return weighted / span, {kind: s / span for kind, s in seconds.items()}


class GridIntensity:
    # Fetched points per (source, zone), shared so train/eval and many result
    # files reuse one request: (fetched_at, start, end, points)
    _cache: Dict[Tuple[str, str], List] = {}

    def __init__(self, source: str, zone: Optional[str], fixed: float):
        self.fixed = fixed
        self.provider = None
        if source != "fixed":
            if not zone:
                raise SystemExit(f"--carbon-source {source} needs --carbon-zone (e.g. DE)")
            self.provider = PROVIDERS[source](zone)
            self.key = (source, zone.upper())

    def _points(self, start: float, end: float) -> List[Point]:
        cached = self._cache.get(self.key)
        # Refetch after 10 minutes: forecasts get replaced by actual values
        if not (cached and cached[1] <= start and end <= cached[2] and time.time() - cached[0] < 600):
            lo, hi = start - 3600, max(end, time.time()) + 3600
            cached = [time.time(), lo, hi, self.provider.points(lo, hi)]
            self._cache[self.key] = cached
        return cached[3]

    def over(self, start: Optional[float], end: Optional[float]) -> Dict:
        points, error = [], None
        if start is None:
            error = "phase has no timestamps"
            start, end = 0.0, 1.0
        elif self.provider:
            try:
                points = self._points(start, end)
            except Exception as e:  # network or API trouble: fall back, don't fail the run
                error = f"{self.provider.name}: {e}"
                logging.warning(f"Grid intensity lookup failed ({error}); using {self.fixed:g} gCO2/kWh")
        resolution = self.provider.resolution_s if self.provider else 1.0
        mean, kinds = window_intensity(points, resolution, start, end, self.fixed)
        out = {"carbon_intensity_g_per_kwh": mean, "carbon_intensity_kinds": kinds}
        if error:
            out["carbon_intensity_error"] = error
        return out


class CarbonAccountant:
    def __init__(self, **settings):
        self.settings = dict(DEFAULTS, **settings)
        s = self.settings
        self.grid = GridIntensity(s["carbon_source"], s["carbon_zone"], s["fixed_carbon_intensity"])

    def config(self) -> Dict:
        return dict(self.settings, computed_at=datetime.datetime.now().isoformat())

    def phase(self, p: Dict) -> Dict:
        """CO2 and cost for one phase from energy.phase_metrics output."""
        s = self.settings
        duration = p["duration_s"]
        out = self.grid.over(p.get("start_unix"), p.get("end_unix"))
        ci = out["carbon_intensity_g_per_kwh"]
        ci_unc = s["carbon_intensity_uncertainty"]
        if ci_unc is None:
            ci_unc = sum(share * INTENSITY_UNCERTAINTY[k] for k, share in out["carbon_intensity_kinds"].items())
        out["carbon_intensity_rel_uncertainty"] = ci_unc

        bases = {"total": (p["total_energy_j"], s["scope_offset_w"] * duration)}
        if p.get("net_energy_j") is not None:
            bases["net"] = (p["net_energy_j"], 0.0)
        for basis, (measured, offset_j) in bases.items():
            sensor_err = p.get("power_uncertainty_w", 0.0) * duration + p.get("power_uncertainty_rel", 0.0) * abs(measured)
            system = s["scope_factor"] * measured + offset_j
            low = (s["scope_factor"] * (measured - sensor_err) + offset_j) * (1 - s["scope_uncertainty"])
            high = (s["scope_factor"] * (measured + sensor_err) + offset_j) * (1 + s["scope_uncertainty"])
            low = min(max(low, 0.0), system)
            kwh, kwh_low, kwh_high = (e * s["pue"] / 3.6e6 for e in (system, low, high))
            out[f"{basis}_facility_kwh"] = kwh
            out[f"{basis}_co2_kg"] = kwh * ci / 1000
            out[f"{basis}_co2_kg_low"] = kwh_low * ci * (1 - ci_unc) / 1000
            out[f"{basis}_co2_kg_high"] = kwh_high * ci * (1 + ci_unc) / 1000
            out[f"{basis}_cost_usd"] = kwh * s["electricity_price"]
        return out

    def apply(self, energy: Dict) -> Dict:
        """Add CO2/cost to each phase of a results `energy` block; returns the experiment sum."""
        # Fields from the earlier fixed-factor format
        for key in ("footprint_basis", "carbon_intensity_g_per_kwh", "electricity_price_usd_per_kwh"):
            energy.pop(key, None)
        totals = {}
        for phase in ("train", "eval"):
            for key in ("energy_kwh", "co2_kg", "cost_usd"):
                energy[phase].pop(key, None)
            footprint = self.phase(energy[phase])
            energy[phase].update(footprint)
            for key, value in footprint.items():
                if key.startswith(("net_", "total_")):  # energy, CO2 (with bounds) and cost
                    totals[key] = totals.get(key, 0.0) + value
        energy["experiment"] = totals
        energy["carbon"] = self.config()
        return totals


def add_carbon_args(parser: argparse.ArgumentParser):
    """CO2/cost flags; all default to None so stored settings can fill the gaps."""
    g = parser.add_argument_group("CO2 and cost")
    g.add_argument("--carbon-source", choices=["fixed", *PROVIDERS],
                   help="Grid intensity source (default: fixed, or energy-charts when --carbon-zone is set)")
    g.add_argument("--carbon-zone", help="Country/zone for time-resolved intensity, e.g. DE")
    g.add_argument("--carbon-intensity", dest="fixed_carbon_intensity", type=float,
                   help="Fixed grid intensity in gCO2/kWh, also the fallback (default 480, ~world average)")
    g.add_argument("--carbon-intensity-uncertainty", type=float,
                   help="Relative uncertainty of grid intensity (default: by data kind, 0.10-0.30)")
    g.add_argument("--pue", type=float, help="Facility overhead factor (default 1.0, no data-centre overhead)")
    g.add_argument("--scope-factor", type=float,
                   help="System power per unit of sensor power, from `python energy.py calibrate` (default 1.0)")
    g.add_argument("--scope-offset-w", type=float,
                   help="System power not seen by the sensor, in W (default 0)")
    g.add_argument("--scope-uncertainty", type=float, help="Relative error of the scope calibration (default 0)")
    g.add_argument("--electricity-price", type=float, help="Electricity price in USD/kWh (default 0.15)")


def accountant_from_args(args: argparse.Namespace, stored: Optional[Dict] = None) -> CarbonAccountant:
    """Command-line flags win, then settings stored with a result, then defaults."""
    settings = {k: v for k, v in (stored or {}).items() if k in DEFAULTS}
    settings.update({k: v for k, v in vars(args).items() if k in DEFAULTS and v is not None})
    # A zone without a source means the keyless time-resolved source
    if args.carbon_zone and not args.carbon_source and settings.get("carbon_source", "fixed") == "fixed":
        settings["carbon_source"] = "energy-charts"
    return CarbonAccountant(**settings)


def _stored_settings(energy: Dict) -> Dict:
    if "carbon" in energy:
        return energy["carbon"]
    # Earlier fixed-factor format
    legacy = {"fixed_carbon_intensity": energy.get("carbon_intensity_g_per_kwh"),
              "electricity_price": energy.get("electricity_price_usd_per_kwh")}
    return {k: v for k, v in legacy.items() if v is not None}


def describe(fp: Dict) -> str:
    def grams(basis):
        return (f"{fp[f'{basis}_co2_kg'] * 1000:.3f} g "
                f"[{fp[f'{basis}_co2_kg_low'] * 1000:.3f}-{fp[f'{basis}_co2_kg_high'] * 1000:.3f}]")
    parts = [f"net {grams('net')}"] if "net_co2_kg" in fp else []
    parts.append(f"total {grams('total')}")
    return "CO2 " + ", ".join(parts) + f", total cost ${fp['total_cost_usd']:.5f}"


def update_results(paths: List[str], args: argparse.Namespace):
    files = []
    for path in paths:
        files += sorted(glob.glob(os.path.join(path, "*_results.json"))) if os.path.isdir(path) else [path]
    for path in files:
        with open(path) as f:
            result = json.load(f)
        energy = result.get("energy")
        if not energy:
            print(f"{path}: no energy measurements, skipped")
            continue
        totals = accountant_from_args(args, _stored_settings(energy)).apply(energy)
        with open(path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"{os.path.basename(path)}: {describe(totals)}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="CO2 and cost from SLM-Bench energy results")
    sub = parser.add_subparsers(dest="command", required=True)
    update = sub.add_parser("update", help="Recompute CO2/cost in results JSON files in place")
    update.add_argument("paths", nargs="+", help="Results JSON files or directories")
    add_carbon_args(update)
    args = parser.parse_args()
    update_results(args.paths, args)
