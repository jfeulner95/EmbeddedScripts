# Windows System Audit

`WindowsSystemAudit.bat` creates a technical inventory of a Windows system. The
script displays a startup banner with the current version and logs the audit
output. When the `registry` category is selected, registry exports are stored in
the same output directory.

## Version

Current version: `1.0.0`

This version number is shown on startup and written to the log file.

## Information Captured

- Windows version, build, computer name, user, and `systeminfo`
- CPU, memory, BIOS, motherboard, drives, partitions, and graphics cards
- Network adapters and full IP configuration
- Processes, services, scheduled tasks, boot configuration, and power plans
- Installed programs from common 32-/64-bit uninstall keys
- `winget list` when `winget` is available
- Drivers via `driverquery`, `pnputil /enum-drivers`, and WMI/CIM
- Registry hives `HKLM`, `HKCU`, `HKCR`, and `HKU` as `.reg` files
- Additional recursive queries of `HKLM` and `HKCU` in the log

## Usage

Run the script from Command Prompt or PowerShell with one or more category
parameters:

```bat
.\WindowsSystemAudit.bat hardware software
```

Available categories are `identity`, `hardware`, `system`, `software`,
`drivers`, and `registry`. Use `all` by itself to collect every category.
Omitting parameters also collects everything, preserving the original behavior.

- `identity`: permissions and system identification
- `hardware`: CPU, memory, BIOS, motherboard, storage, and network
- `system`: Windows configuration, processes, services, and scheduled tasks
- `software`: installed programs and `winget` inventory
- `drivers`: installed driver inventory
- `registry`: registry exports and recursive registry queries

1. Copy `WindowsSystemAudit.bat` to the target system.
2. Open Command Prompt or PowerShell, change to the script's folder, and run it
  with the desired category parameters. Run as administrator for the most
  complete results.
3. Wait until the `Finished` message appears.
4. Open the generated folder `Windows-System-Audit_<ComputerName>_<Timestamp>`.

At startup, the script prints a banner similar to:

```bat
Windows System Audit v1.0.0
Version: 1.0.0
Computer: <hostname>
Output folder: ...
```

The most important file is `SystemAudit.log`. When the `registry` category is
selected, registry exports are stored alongside it as `HKLM.reg`, `HKCU.reg`,
`HKCR.reg`, and `HKU.reg`.

## Rights and Privacy Notes

- Without administrator rights, drivers, services, BCD, protected registry
  areas, and some hardware details may be incomplete.
- The log may contain usernames, computer names, IP addresses, drive details,
  installed software, tasks, services, and registry contents. Treat the output
  folder as confidential.
- Registry exports and recursive registry output can become very large. Ensure
  enough free disk space.
- `winget` is not present on every Windows installation; errors in this section
  are expected and are recorded in the log.
- The script reads data and does not make changes to the system. However, the
  output of `set` can include environment variables with credentials if such
  variables are present on the system.

## Compatibility

The script is intended for Windows 10 and Windows 11. The CIM queries use
`powershell.exe`, which is available by default on these versions. Some older or
optional commands may be missing depending on the edition; those errors are
logged without aborting the audit.
