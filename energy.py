"""Energy measurement on NVIDIA GPUs and edge devices, without extra dependencies.

Backends (picked automatically):
  nvml    - DGX Spark and other NVML GPUs. Reads the hardware energy counter
            (nvmlDeviceGetTotalEnergyConsumption). Covers the GPU only: CPU,
            memory and the rest of the system are not included. NVML reports
            the whole device, so other processes on the same GPU are counted too.
  jetson  - Jetson Orin / Xavier (ina3221 hwmon) and the original Nano / TX2
            (ina3221x iio). There is no energy counter, so power is sampled and
            integrated. The module input rail (VDD_IN / POM_5V_IN) is used when
            present; otherwise all rails are summed (e.g. AGX Orin).

Usage:
    meter = EnergyMeter()            # or EnergyMeter.create(), None if unsupported
    idle_w = meter.idle_power(10)
    with meter:
        run_workload()
    print(phase_metrics(meter.report(), idle_w, tokens))
"""
import ctypes
import glob
import logging
import os
import threading
import time
from typing import Dict, Optional

TOTAL_RAILS = ("VDD_IN", "POM_5V_IN")


def _read(path: str) -> float:
    with open(path) as f:
        return float(f.read())


class NvmlBackend:
    name = "nvml"

    def __init__(self, index: int = 0):
        self.lib = ctypes.CDLL("libnvidia-ml.so.1")
        if self.lib.nvmlInit_v2() != 0:
            raise RuntimeError("nvmlInit failed")
        self.handle = ctypes.c_void_p()
        if self.lib.nvmlDeviceGetHandleByIndex_v2(index, ctypes.byref(self.handle)) != 0:
            raise RuntimeError(f"no NVML device {index}")
        if self.energy_counter_j() is None:
            raise RuntimeError("NVML energy counter not supported")
        self.scope = "GPU"
        # nvidia-smi documents NVML power as accurate to within +/- 5 W
        self.power_uncertainty_w, self.power_uncertainty_rel = 5.0, 0.0

    def rails(self) -> Dict[str, float]:
        mw = ctypes.c_uint()
        self.lib.nvmlDeviceGetPowerUsage(self.handle, ctypes.byref(mw))
        return {"GPU": mw.value / 1000.0}

    def energy_counter_j(self) -> Optional[float]:
        mj = ctypes.c_ulonglong()
        if self.lib.nvmlDeviceGetTotalEnergyConsumption(self.handle, ctypes.byref(mj)) != 0:
            return None
        return mj.value / 1000.0


class JetsonBackend:
    name = "jetson"

    def __init__(self):
        self.sensors = []  # (label, reader returning watts)
        # Orin / Xavier, JetPack 5-6: hwmon reports mV and mA per channel
        for label_file in sorted(glob.glob("/sys/bus/i2c/drivers/ina3221/*/hwmon/hwmon*/in*_label")):
            folder = os.path.dirname(label_file)
            channel = os.path.basename(label_file)[2:-len("_label")]
            volts, amps = f"{folder}/in{channel}_input", f"{folder}/curr{channel}_input"
            label = open(label_file).read().strip()
            # Channel 7 is the "sum of shunt voltages", not a rail
            if os.path.exists(amps) and not label.lower().startswith("sum"):
                self.sensors.append((label, lambda v=volts, a=amps: _read(v) * _read(a) / 1e6))
        # Original Nano / TX1 / TX2, JetPack 4: iio reports mW per rail
        for power_file in sorted(glob.glob("/sys/bus/i2c/drivers/ina3221x/*/iio:device*/in_power*_input")):
            n = power_file.rsplit("in_power", 1)[1].split("_")[0]
            label = open(f"{os.path.dirname(power_file)}/rail_name_{n}").read().strip()
            self.sensors.append((label, lambda p=power_file: _read(p) / 1000.0))
        if not self.sensors:
            raise RuntimeError("no ina3221 sensors found")
        labels = [label for label, _ in self.sensors]
        self.total_rail = next((r for r in TOTAL_RAILS if r in labels), None)
        self.scope = self.total_rail or "sum of " + ", ".join(labels)
        # No published end-to-end accuracy for the module sensors; assume +/- 5 %
        self.power_uncertainty_w, self.power_uncertainty_rel = 0.0, 0.05

    def rails(self) -> Dict[str, float]:
        return {label: read() for label, read in self.sensors}

    def energy_counter_j(self) -> Optional[float]:
        return None


class EnergyMeter:
    """Context manager measuring energy over a block of code.

    Uses the hardware energy counter when the backend has one. Otherwise it
    integrates sampled power, which lags load changes by about the sensor's
    averaging window, so keep measured blocks several seconds long.
    """

    def __init__(self, backend=None, interval: float = 0.05):
        self.backend = backend or (
            JetsonBackend() if glob.glob("/sys/bus/i2c/drivers/ina3221*") else NvmlBackend()
        )
        self.interval = interval
        self.samples = []

    @classmethod
    def create(cls, **kwargs) -> Optional["EnergyMeter"]:
        try:
            return cls(**kwargs)
        except Exception as e:
            logging.warning(f"Energy measurement disabled: {e}")
            return None

    def _sample_loop(self):
        while not self._stop.is_set():
            self.samples.append((time.perf_counter(), self.backend.rails()))
            self._stop.wait(self.interval)

    def __enter__(self):
        self.samples = []
        self._stop = threading.Event()
        self.counter_start = self.backend.energy_counter_j()
        self.t_start = time.perf_counter()
        self.unix_start = time.time()  # wall clock, to look up grid carbon intensity
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.t_end = time.perf_counter()
        self.counter_end = self.backend.energy_counter_j()
        self._stop.set()
        self._thread.join()
        self.samples.append((self.t_end, self.backend.rails()))

    def rail_energy_j(self) -> Dict[str, float]:
        # Trapezoidal integration of sampled power per rail
        energy = {}
        for (ta, pa), (tb, pb) in zip(self.samples, self.samples[1:]):
            for rail in pa:
                energy[rail] = energy.get(rail, 0.0) + (pa[rail] + pb[rail]) / 2 * (tb - ta)
        return energy

    def report(self) -> Dict:
        duration = self.t_end - self.t_start
        rails = self.rail_energy_j()
        if self.counter_start is not None and self.counter_end is not None:
            total = self.counter_end - self.counter_start
        elif getattr(self.backend, "total_rail", None):
            total = rails[self.backend.total_rail]
        else:
            total = sum(rails.values())
        return {
            "backend": self.backend.name,
            "scope": self.backend.scope,
            "power_uncertainty_w": self.backend.power_uncertainty_w,
            "power_uncertainty_rel": self.backend.power_uncertainty_rel,
            "start_unix": self.unix_start,
            "end_unix": self.unix_start + duration,
            "duration_s": duration,
            "samples": len(self.samples),
            "total_energy_j": total,
            "avg_power_w": total / duration if duration > 0 else None,
            "rail_energy_j": rails,
        }

    def idle_power(self, seconds: float) -> float:
        """Average power while nothing runs in this process (the idle baseline)."""
        with self:
            time.sleep(seconds)
        return self.report()["avg_power_w"]


def phase_metrics(report: Dict, idle_power_w: Optional[float], tokens: Optional[int]) -> Dict:
    """Energy for one phase, with the idle baseline subtracted (net_*)."""
    duration = report["duration_s"]
    metrics = dict(report, tokens=tokens)
    if idle_power_w is not None:
        net = report["total_energy_j"] - idle_power_w * duration
        metrics["net_energy_j"] = net
        metrics["net_avg_power_w"] = net / duration if duration > 0 else None
        metrics["net_j_per_token"] = net / tokens if tokens else None
    metrics["total_j_per_token"] = report["total_energy_j"] / tokens if tokens else None
    return metrics


def _duty_cycle_load(fraction: float, stop: threading.Event, n: int = 4096):
    # Busy for `fraction` of every 100 ms, so the GPU sits at a steady partial load
    import torch

    a = torch.randn(n, n, device="cuda", dtype=torch.bfloat16)
    b = torch.randn_like(a)
    while not stop.is_set():
        busy_until = time.perf_counter() + 0.1 * fraction
        while time.perf_counter() < busy_until:
            a @ b
            torch.cuda.synchronize()
        stop.wait(0.1 * (1 - fraction))


def calibrate(levels=(0.0, 0.33, 0.66, 1.0), settle_s: float = 20.0, measure_s: float = 60.0):
    """Fit wall power = offset + factor x sensor power, against a wall-plug meter.

    Runs a GPU load at each level, measures sensor power, and asks for the
    wall-meter reading. Prints the --scope-* flags for train.py.
    """
    meter = EnergyMeter()
    points = []
    for level in levels:
        stop = threading.Event()
        load = None
        if level > 0:
            load = threading.Thread(target=_duty_cycle_load, args=(level, stop), daemon=True)
            load.start()
        print(f"Load {level:.0%}: settling {settle_s:g}s, then measuring {measure_s:g}s ...", flush=True)
        time.sleep(settle_s)
        with meter:
            time.sleep(measure_s)
        sensor_w = meter.report()["avg_power_w"]
        wall_w = float(input(f"  sensor {sensor_w:.1f} W. Wall-meter reading now (W): "))
        stop.set()
        if load:
            load.join()
        points.append((sensor_w, wall_w))

    n = len(points)
    mean_s = sum(s for s, _ in points) / n
    mean_w = sum(w for _, w in points) / n
    var_s = sum((s - mean_s) ** 2 for s, _ in points)
    factor = sum((s - mean_s) * (w - mean_w) for s, w in points) / var_s
    offset = mean_w - factor * mean_s
    worst = max(abs(offset + factor * s - w) / w for s, w in points)
    print(f"\nwall = {offset:.1f} W + {factor:.3f} x sensor; worst fit error {worst:.1%}")
    print(f"--scope-factor {factor:.3f} --scope-offset-w {offset:.1f} "
          f"--scope-uncertainty {max(worst, 0.02):.2f}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Energy meter utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", help="Show the detected backend and current power")
    cal = sub.add_parser("calibrate", help="Fit sensor power to a wall-plug power meter")
    cal.add_argument("--settle-seconds", type=float, default=20.0)
    cal.add_argument("--measure-seconds", type=float, default=60.0)
    args = parser.parse_args()
    if args.command == "probe":
        m = EnergyMeter()
        print(m.backend.name, m.backend.scope, m.backend.rails())
    else:
        calibrate(settle_s=args.settle_seconds, measure_s=args.measure_seconds)
