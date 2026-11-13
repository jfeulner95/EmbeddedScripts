# SetDriverTestMode

`SetDriverTestMode.bat` enables or disables Windows driver test-signing mode and can optionally restart the computer.

## Version

`1.0.0`

## Requirements

- Windows
- An administrator Command Prompt
- A reboot after changing the boot configuration

The script checks for administrator privileges before making changes. It does not automatically elevate itself.

When it starts, the script displays the current `testsigning` and `nointegritychecks` values. It labels the requested action and reports whether each configuration update succeeded.

## Usage

1. Open **Command Prompt as administrator**.
2. Change to the directory containing the script.
3. Run:

   ```bat
   SetDriverTestMode.bat
   ```

4. Choose whether the driver is signed:
   - **S**igned: turns test-signing mode and `nointegritychecks` off.
   - **U**nsigned: turns test-signing mode and `nointegritychecks` on.
5. Choose whether to restart immediately. The changes take effect after reboot.

## Important security note

Enabling test-signing mode and `nointegritychecks` weakens Windows driver-signature enforcement. Use this only for controlled driver development or testing. Turn both settings off when testing is complete, then restart Windows.

## What the script changes

The script uses BCDEdit to change these boot options:

```text
bcdedit /set testsigning on|off
bcdedit /set nointegritychecks on|off
```

If either BCDEdit command fails, the script reports the error and does not start a reboot.

## Possible future improvements

- Offer a separate explicit `Enable` or `Disable` mode instead of deriving the action from signed-driver status.
- Add an optional automatic elevation prompt.
- Record a log of the commands and their results.
