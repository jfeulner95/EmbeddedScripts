## Description

<!-- Provide a brief summary of the script/tooling changes and why they are needed. -->

## Related Issue(s)

<!-- Link any related issues (e.g., Fixes #123, Closes #456). -->
- Fixes #

## Type of Change

- [ ] New script / utility
- [ ] Bug fix in existing script
- [ ] Feature addition / CLI enhancement
- [ ] Flashing / Debugging / Probe tooling (e.g., OpenOCD, J-Link, pyOCD, GDB)
- [ ] Communication / Protocol script (e.g., Serial/UART, CAN, BLE, USB, Saleae)
- [ ] Build / Code-gen / Binary analysis script (e.g., ELF/Map/Hex parsing, CRC/signing)
- [ ] Test automation / HIL runner
- [ ] Breaking change (CLI arguments, config format, or output format changed)
- [ ] Refactor / Dependency update / Documentation

## Environment & Compatibility

- **Host OS Tested:** <!-- e.g., Windows, Linux, macOS -->
- **Scripting Runtime / Version:** <!-- e.g., Python 3.11+, PowerShell 7, Bash -->
- **External Tools / Drivers Required:** <!-- e.g., J-Link Commander, arm-none-eabi-objdump, pyserial, cantools -->
- **Target Hardware / Interface (if applicable):** <!-- e.g., STM32 via ST-Link, UART @ 115200, SocketCAN -->

## How Has This Been Verified?

- [ ] Tested against live hardware / target board
- [ ] Tested with mock data / captured logs / dry-run mode
- [ ] Automated unit / pytest checks

**Example Usage / Test Command:**
```bash
# Paste the command(s) used to test this script
```

## Sample Output / Logs (if applicable)

<!-- Paste terminal output, generated files, or screenshots if relevant. -->

## Checklist

- [ ] Script includes `--help` usage details or header documentation
- [ ] Cross-platform path and serial port handling is respected (where applicable)
- [ ] New dependencies or external tool requirements are documented (e.g., `requirements.txt`, `README.md`)
- [ ] Error handling covers missing tools, disconnected hardware, or serial/bus timeouts gracefully
- [ ] Linter / Formatter checks pass (e.g., `ruff`, `flake8`, `black`, `shellcheck`)
- [ ] Existing workflows or CI pipelines using this script remain compatible
