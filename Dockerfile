FROM ubuntu:22.04

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies, including pre-compiled PyQt5, lxml, and PyEnchant
# to avoid compiling PyQt5 from source on aarch64/ARM64 architectures.
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-pyqt5 \
    python3-lxml \
    python3-enchant \
    build-essential \
    qtbase5-dev \
    qt5-qmake \
    libxml2-dev \
    libxslt1-dev \
    mesa-utils \
    libgl1 \
    libgl1-mesa-dev \
    libxcb-xinerama0-dev \
    xvfb \
    rsync \
    dpkg-dev \
    rpm \
    enchant-2 \
    libenchant-2-dev \
    hunspell \
    git \
    zip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Allow passwordless sudo for root inside the container
# This is needed by package/create_deb.sh which runs sudo chown
RUN echo "root ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/nopasswd

WORKDIR /workspace

# Install python packages that are safe and fast to install via pip
RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel
RUN pip3 install --no-cache-dir pyinstaller pytest pytest-faulthandler markdown language_tool_python symspellpy pyspellchecker

# Set environment variable for PyQt5 offscreen running
ENV QT_QPA_PLATFORM=offscreen

# Default command: run pytest with offscreen cache configuration and ignore build dirs
CMD ["pytest", "-vs", "-o", "cache_dir=/tmp/pytest_cache", "--ignore=rpmbuild", "--ignore=dist"]
