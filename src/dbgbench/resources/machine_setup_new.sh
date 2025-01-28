#!/usr/bin/env bash
set -e

apt-get update
apt-get --yes upgrade

# Install dependencies and Python directly
apt-get install -y --no-install-recommends \
    software-properties-common \
    python3 \
    python3-pip \
    python3-dev \
    libffi-dev \
    zlib1g \
    zlib1g-dev \
    libbz2-dev \
    liblzma-dev \
    uuid-dev

# Upgrade pip and install Python packages
python3 -m pip install -U pip
python3 -m pip install numpy pandas

# Set up directories
mkdir -p /root/Desktop/alhazen_scripts/
mkdir -p /root/Desktop/alhazen_scripts/alhazen/
mkdir -p /root/Desktop/alhazen_samples/

# Create a basic startup script
printf '#!/bin/bash\nwhile [ 1 ]; do\n/bin/bash\ndone\n' > /startup.sh
chmod +x /startup.sh
