#!/usr/bin/env python3
"""
Zephyr RTOS & SDK Automatic Setup Script
Version: 1.0.0
License: PolyForm Noncommercial License 1.0.0
Copyright (c) 2026 Johannes Feulner
Author: Johannes Feulner
Note: Interactive setup script to automatically install a chosen
      Zephyr RTOS release, workspace, dependencies, and the matching Zephyr SDK.
"""

import os
import sys
import platform
import subprocess
import urllib.request
import tarfile
import shutil
from pathlib import Path


def run_command(cmd, cwd=None, shell=False):
    """Execute a shell command and exit on failure."""
    print(f"--> Running: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    try:
        subprocess.run(cmd, cwd=cwd, shell=shell, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed with exit code {e.returncode}.")
        sys.exit(1)


def download_file(url, dest_path):
    """Download a file with a simple console progress indicator."""
    print(f"Downloading from: {url}")

    def reporthook(block_num, block_size, total_size):
        if total_size > 0:
            downloaded = block_num * block_size
            percent = min(100, int(downloaded * 100 / total_size))
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            sys.stdout.write(
                f"\rProgress: {percent}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)"
            )
            sys.stdout.flush()

    try:
        urllib.request.urlretrieve(url, dest_path, reporthook=reporthook)
        print()  # Newline after progress
    except Exception as e:
        print(f"\nError downloading file: {e}")
        sys.exit(1)


def install_system_dependencies(os_type):
    """Install required OS-level packages."""
    print("\n[1/6] Installing required system dependencies...")
    if os_type == "Linux":
        print("Updating apt and installing packages (sudo password may be required)...")
        run_command(["sudo", "apt-get", "update"])
        packages = [
            "git", "cmake", "ninja-build", "gperf", "ccache", "dfu-util",
            "device-tree-compiler", "wget", "python3-dev", "python3-pip",
            "python3-setuptools", "python3-tk", "python3-wheel", "python3-venv",
            "xz-utils", "file", "make", "gcc", "gcc-multilib", "g++-multilib",
            "libsdl2-dev", "libmagic1"
        ]
        run_command(["sudo", "apt-get", "install", "-y", "--no-install-recommends"] + packages)

    elif os_type == "Windows":
        print("Installing required Windows dependencies via winget...")
        print("Note: Existing packages will be skipped automatically.")
        winget_ids = [
            "Kitware.CMake",
            "Ninja-build.Ninja",
            "oss-winget.gperf",
            "Git.Git",
            "oss-winget.dtc",
            "7zip.7zip"
        ]
        for pkg_id in winget_ids:
            subprocess.run([
                "winget", "install", "-e", "--id", pkg_id,
                "--accept-package-agreements", "--accept-source-agreements", "--silent"
            ], check=False)
    else:
        print(f"Unsupported operating system: {os_type}")
        sys.exit(1)


def main():
    print("==================================================")
    print("   Zephyr RTOS & SDK Automatic Setup (Python)     ")
    print("==================================================\n")

    os_type = platform.system()
    machine = platform.machine().lower()

    if machine in ("x86_64", "amd64"):
        sdk_arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        sdk_arch = "aarch64"
    else:
        print(f"Error: Unsupported architecture '{machine}'.")
        sys.exit(1)

    # 1. Prompt for the desired Zephyr release
    zephyr_ref = input(
        "Which Zephyr release do you want to install? (e.g. v3.7.0, v4.0.0, or 'main'): "
    ).strip()

    if not zephyr_ref:
        print("Error: No release specified. Aborting.")
        sys.exit(1)

    # Define directory paths
    home_dir = Path.home()
    base_dir = home_dir / "sandbox" / "zephyr"
    workspace_dir = base_dir / "zephyrproject"
    venv_dir = base_dir / ".venv"
    sdk_install_dir = home_dir

    # Step 1: System dependencies
    install_system_dependencies(os_type)

    # Step 2: Create working directory
    print(f"\n[2/6] Creating working directory at {base_dir}...")
    base_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Create virtual environment and install west
    print("\n[3/6] Creating Python virtual environment and installing 'west'...")
    if not venv_dir.exists():
        run_command([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print(f"Virtual environment already exists at {venv_dir}.")

    if os_type == "Windows":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_west = venv_dir / "Scripts" / "west.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_west = venv_dir / "bin" / "west"

    run_command([str(venv_python), "-m", "pip", "install", "--upgrade", "pip"])
    run_command([str(venv_python), "-m", "pip", "install", "west"])

    # Step 4: Initialize Zephyr workspace
    print(f"\n[4/6] Initializing Zephyr workspace for release '{zephyr_ref}'...")
    if workspace_dir.exists():
        print(f"Warning: {workspace_dir} already exists. Skipping 'west init'...")
    else:
        run_command([
            str(venv_west), "init",
            "-m", "https://github.com/zephyrproject-rtos/zephyr",
            "--mr", zephyr_ref,
            str(workspace_dir)
        ])

    print("Downloading Zephyr modules (this may take a few minutes)...")
    run_command([str(venv_west), "update"], cwd=workspace_dir)

    print("Exporting Zephyr CMake packages...")
    run_command([str(venv_west), "zephyr-export"], cwd=workspace_dir)

    print("Installing Python dependencies for the selected release...")
    req_file = workspace_dir / "zephyr" / "scripts" / "requirements.txt"
    run_command([str(venv_python), "-m", "pip", "install", "-r", str(req_file)])

    # Step 5: Detect and install matching Zephyr SDK
    print("\n[5/6] Detecting and installing matching Zephyr SDK...")
    sdk_version_file = workspace_dir / "zephyr" / "SDK_VERSION"

    if not sdk_version_file.exists():
        print(f"Error: SDK_VERSION file not found at {sdk_version_file}")
        sys.exit(1)

    sdk_version = sdk_version_file.read_text(encoding="utf-8").strip()
    print(f"Required SDK version according to Zephyr repository: {sdk_version}")

    sdk_dir = sdk_install_dir / f"zephyr-sdk-{sdk_version}"

    if sdk_dir.exists():
        print(f"Zephyr SDK {sdk_version} is already installed at {sdk_dir}.")
    else:
        if os_type == "Linux":
            sdk_archive_name = f"zephyr-sdk-{sdk_version}_linux-{sdk_arch}.tar.xz"
            sdk_url = f"https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v{sdk_version}/{sdk_archive_name}"
            archive_path = base_dir / sdk_archive_name

            download_file(sdk_url, archive_path)

            print(f"Extracting SDK to {sdk_install_dir} (this may take a moment)...")
            with tarfile.open(archive_path, "r:xz") as tar:
                tar.extractall(path=sdk_install_dir)
            archive_path.unlink()

            print("Running SDK setup...")
            run_command(["./setup.sh", "-t", "all", "-h", "-c"], cwd=sdk_dir)

        elif os_type == "Windows":
            sdk_archive_name = f"zephyr-sdk-{sdk_version}_windows-{sdk_arch}.7z"
            sdk_url = f"https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v{sdk_version}/{sdk_archive_name}"
            archive_path = base_dir / sdk_archive_name

            download_file(sdk_url, archive_path)

            print(f"Extracting SDK to {sdk_install_dir} (this may take a moment)...")
            seven_zip = shutil.which("7z") or r"C:\Program Files\7-Zip\7z.exe"
            if not Path(seven_zip).exists():
                print("Error: 7-Zip not found. Please restart your terminal or install 7-Zip manually.")
                sys.exit(1)

            run_command([seven_zip, "x", str(archive_path), f"-o{sdk_install_dir}", "-y"])
            archive_path.unlink()

            print("Running SDK setup...")
            run_command(["cmd.exe", "/c", "setup.cmd", "/t", "all", "/h", "/c"], cwd=sdk_dir)

    # Step 6: Create convenience activation script
    print("\n[6/6] Creating convenience activation script...")
    if os_type == "Linux":
        act_script = base_dir / "activate_zephyr.sh"
        act_content = (
            "#!/usr/bin/env bash\n"
            f'source "{venv_dir}/bin/activate"\n'
            f'source "{workspace_dir}/zephyr/zephyr-env.sh"\n'
            f'cd "{workspace_dir}/zephyr"\n'
            f'echo "Zephyr environment ({zephyr_ref}) is active!"\n'
        )
        act_script.write_text(act_content, encoding="utf-8")
        act_script.chmod(0o755)
        activate_hint = f"source {act_script}"

    elif os_type == "Windows":
        act_script = base_dir / "activate_zephyr.bat"
        act_content = (
            "@echo off\n"
            f'call "{venv_dir}\\Scripts\\activate.bat"\n'
            f'set "ZEPHYR_BASE={workspace_dir}\\zephyr"\n'
            f'cd /d "{workspace_dir}\\zephyr"\n'
            f'echo Zephyr environment ({zephyr_ref}) is active!\n'
        )
        act_script.write_text(act_content, encoding="utf-8")
        activate_hint = f'call "{act_script}"'

    print("\n==================================================")
    print(" Installation completed successfully!             ")
    print("==================================================")
    print(f"Workspace path : {workspace_dir}")
    print(f"SDK path       : {sdk_dir}")
    print("\nTo use the environment in the future, simply run:")
    print(f"  {activate_hint}\n")


if __name__ == "__main__":
    main()