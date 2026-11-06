FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/cache

# Install Python (Ubuntu 22.04 ships Python 3.10) and basic dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install the CUDA 11.8 build of torch to match the base image, then the
# rest of the pinned requirements (torch is already satisfied by then)
COPY requirements.txt .
RUN pip3 install --no-cache-dir torch==2.4.1 --index-url https://download.pytorch.org/whl/cu118 \
    && pip3 install --no-cache-dir -r requirements.txt

# Copy project files
COPY train.py models.json datasets.json ./

# Run as an unprivileged user (train.py writes experiments.log to /app, so it
# needs to own the directory)
RUN useradd --create-home --uid 1000 slmbench \
    && mkdir -p experiment_results cache logs \
    && chown -R slmbench:slmbench /app
USER slmbench

# Mount these to keep results and downloaded models outside the container
VOLUME ["/app/experiment_results", "/app/cache"]

# Default command
ENTRYPOINT ["python3", "train.py"]
