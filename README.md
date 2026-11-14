# <img src="./.github/assets/icon.jpg" alt="EmbeddedScripts Logo" width="42" align="center" /> EmbeddedScripts

**License:** PolyForm Noncommercial 1.0.0

A collection of helpful scripts and automation tools for embedded systems development.

### 📂 Available Scripts & Tools

| Project / Folder | Script File | Supported OS | Version | Description |
| :--- | :--- | :--- | :--- | :--- |
| [**`ZephyrSetup/`**](./ZephyrSetup/) | [`setup_zephyr.py`](./ZephyrSetup/setup_zephyr.py) | Ubuntu & Windows | `v1.0.0` | Cross-platform Python script to set up a Zephyr RTOS workspace & matching SDK. *(Recommended)* |
| | [`setup_zephyr.sh`](./ZephyrSetup/setup_zephyr.sh) | Ubuntu (Linux) | `v1.0.0` | Native Bash shell script to set up a Zephyr RTOS workspace & matching SDK. |
| | [`setup_zephyr.bat`](./ZephyrSetup/setup_zephyr.bat) | Windows 10 / 11 | `v1.0.0` | Native Windows Batch script to set up a Zephyr RTOS workspace & matching SDK. |
|[**`SetWinDriverTestMode/`**](./SetWinDriverTestMode/) | [`SetDriverTestMode.bat`](./SetWinDriverTestMode/SetDriverTestMode.bat) | Windows 10 / 11 | `v1.0.0` | Windows driver test-signing mode utility |
|[**`WindowsSystemAudit/`**](./WindowsSystemAudit/) | [`WindowsSystemAudit.bat`](./WindowsSystemAudit/WindowsSystemAudit.bat) | Windows 10 / 11 | `v1.0.0` | Creates a log, separate registry exports, and driver lists. |
|[**`BinHexConverter/`**](./BinHexConverter/) | [`bin_hex_converter.py`](./BinHexConverter/bin_hex_converter.py) | Windows, Linux, macOS | `v1.0.0` | Zero-dependency Python tool to convert firmware `.bin` files to Intel `.hex` (or raw hex) and vice versa. |

### 📄 License

This repository is licensed under the **PolyForm Noncommercial License 1.0.0**.
You are free to use, modify, and distribute this software for **noncommercial and personal purposes only**. Any commercial or business use is strictly prohibited. See the [LICENSE](LICENSE) file for full details.