FROM nvidia/cuda:13.0.1-base-ubuntu24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/cache

# Install Python (Ubuntu 24.04 ships Python 3.12) and basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

# Ubuntu 24.04 blocks system-wide pip installs, so use a virtualenv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install the CUDA 13.0 build of torch (bundles its own CUDA libraries; needs
# an NVIDIA driver >= 580 on the host), then the rest of the pinned requirements
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cu130 \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY train.py models.json datasets.json ./

# Run as an unprivileged user (train.py writes experiments.log to /app, so it
# needs to own the directory). Replace the image's default "ubuntu" user, which
# holds UID 1000 and sits in admin groups, with one that has no extra groups.
RUN userdel --remove ubuntu \
    && useradd --create-home --uid 1000 slmbench \
    && mkdir -p experiment_results cache logs \
    && chown -R slmbench:slmbench /app
USER slmbench

# Mount these to keep results and downloaded models outside the container
VOLUME ["/app/experiment_results", "/app/cache"]

# Default command
ENTRYPOINT ["python3", "train.py"]
