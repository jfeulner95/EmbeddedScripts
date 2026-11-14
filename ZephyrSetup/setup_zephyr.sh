#!/usr/bin/env bash
#
# Copyright (c) 2026 Johannes Feulner
#
# SPDX-License-Identifier: PolyForm Noncommercial License 1.0.0
#
# Author: Johannes Feulner
#
# Name: setup_zephyr.sh
#
# Version: 1.0.0
#
# Interactive setup scripts (Ubuntu & Windows) to automatically
# install a chosen Zephyr RTOS release, workspace, dependencies,
# and the matching Zephyr SDK.


# Exit immediately if a command exits with a non-zero status
set -e

echo "=================================================="
echo "   Zephyr RTOS & SDK Automatic Setup (Ubuntu)     "
echo "=================================================="
echo ""

# 1. Prompt for the desired Zephyr release
read -r -p "Which Zephyr release do you want to install? (e.g. v3.7.0, v4.0.0, or 'main'): " ZEPHYR_REF

if [ -z "$ZEPHYR_REF" ]; then
    echo "Error: No release specified. Aborting."
    exit 1
fi

# Define directory paths
BASE_DIR="$HOME/sandbox/zephyr"
WORKSPACE_DIR="$BASE_DIR/zephyrproject"
VENV_DIR="$BASE_DIR/.venv"
# Default path where Zephyr automatically searches for the SDK
SDK_INSTALL_DIR="$HOME"

echo ""
echo "[1/6] Installing required Ubuntu system packages (sudo password may be required)..."
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
    git cmake ninja-build gperf ccache dfu-util device-tree-compiler wget \
    python3-dev python3-pip python3-setuptools python3-tk python3-wheel \
    python3-venv xz-utils file make gcc gcc-multilib g++-multilib libsdl2-dev libmagic1

echo ""
echo "[2/6] Creating working directory at $BASE_DIR..."
mkdir -p "$BASE_DIR"
cd "$BASE_DIR"

echo ""
echo "[3/6] Creating Python virtual environment and installing 'west'..."
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install west

echo ""
echo "[4/6] Initializing Zephyr workspace for release '$ZEPHYR_REF'..."
if [ -d "$WORKSPACE_DIR" ]; then
    echo "Warning: $WORKSPACE_DIR already exists. Skipping 'west init'..."
else
    west init -m https://github.com/zephyrproject-rtos/zephyr --mr "$ZEPHYR_REF" "$WORKSPACE_DIR"
fi

cd "$WORKSPACE_DIR"
echo "Downloading Zephyr modules (this may take a few minutes)..."
west update

echo "Exporting Zephyr CMake packages..."
west zephyr-export

echo "Installing Python dependencies for the selected release..."
pip install -r "$WORKSPACE_DIR/zephyr/scripts/requirements.txt"

echo ""
echo "[5/6] Detecting and installing matching Zephyr SDK..."
SDK_VERSION_FILE="$WORKSPACE_DIR/zephyr/SDK_VERSION"

if [ -f "$SDK_VERSION_FILE" ]; then
    # Read version number and strip whitespace
    SDK_VERSION=$(tr -d '[:space:]' < "$SDK_VERSION_FILE")
    echo "Required SDK version according to Zephyr repository: $SDK_VERSION"
else
    echo "Error: SDK_VERSION file not found at $SDK_VERSION_FILE"
    exit 1
fi

# Detect system architecture (x86_64 or aarch64)
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    SDK_ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ]; then
    SDK_ARCH="aarch64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

SDK_DIR="$SDK_INSTALL_DIR/zephyr-sdk-${SDK_VERSION}"

if [ -d "$SDK_DIR" ]; then
    echo "Zephyr SDK $SDK_VERSION is already installed at $SDK_DIR."
else
    SDK_ARCHIVE="zephyr-sdk-${SDK_VERSION}_linux-${SDK_ARCH}.tar.xz"
    SDK_URL="https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v${SDK_VERSION}/${SDK_ARCHIVE}"

    cd "$BASE_DIR"
    echo "Downloading SDK from: $SDK_URL"
    wget -q --show-progress "$SDK_URL"

    echo "Extracting SDK to $SDK_INSTALL_DIR..."
    tar -xf "$SDK_ARCHIVE" -C "$SDK_INSTALL_DIR"
    rm "$SDK_ARCHIVE"

    echo "Running SDK setup..."
    cd "$SDK_DIR"
    # -t all installs all toolchains, -h installs host tools, -c registers CMake packages
    ./setup.sh -t all -h -c
fi

echo ""
echo "[6/6] Creating convenience activation script..."
cat <<EOF > "$BASE_DIR/activate_zephyr.sh"
#!/usr/bin/env bash
# Activates the Python virtual environment and sets Zephyr environment variables
source "$VENV_DIR/bin/activate"
source "$WORKSPACE_DIR/zephyr/zephyr-env.sh"
cd "$WORKSPACE_DIR/zephyr"
echo "Zephyr environment ($ZEPHYR_REF) is active!"
EOF
chmod +x "$BASE_DIR/activate_zephyr.sh"

echo ""
echo "=================================================="
echo " Installation completed successfully!             "
echo "=================================================="
echo "Workspace path : $WORKSPACE_DIR"
echo "SDK path       : $SDK_DIR"
echo ""
echo "To use the environment in the future, simply run:"
echo "  source $BASE_DIR/activate_zephyr.sh"
echo ""