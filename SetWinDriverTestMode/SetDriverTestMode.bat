REM Copyright (c) 2026 Johannes Feulner
REM
REM SPDX-License-Identifier: PolyForm Noncommercial License 1.0.0
REM
REM Author: Johannes Feulner
REM
REM Name: SetDriverTestMode.bat
REM
REM Version: 1.0.0
REM
REM SetDriverTestMode - Windows driver test-signing mode utility
REM Run from an elevated Command Prompt for controlled driver testing.

@echo off
setlocal
set "Version=1.0.0"
set "ScriptName=SetDriverTestMode"

fltmc >nul 2>&1
if errorlevel 1 (
	echo.
	echo [ERROR] Administrator privileges are required.
	echo         Open an elevated Command Prompt and run %ScriptName%.bat again.
	pause
	exit /b 1
)

title %ScriptName% %Version%
echo ============================================================
echo  %ScriptName% v%Version%
echo  Windows driver test-signing mode utility
echo ============================================================
echo.
echo [CURRENT BOOT CONFIGURATION]
bcdedit /enum {current} | findstr /i "testsigning nointegritychecks"
if errorlevel 1 echo Unable to read the current boot configuration.
echo.
choice /c SU /n /m "Is the driver signed? [S]igned/[U]nsigned: "
if errorlevel 2 set "Signed=0"
if errorlevel 1 if not defined Signed set "Signed=1"
echo.

if "%Signed%" == "1" (
	echo [ACTION] Disabling test-signing mode and no-integrity-checks...
	bcdedit /set testsigning off
	if errorlevel 1 goto :BcdError
	bcdedit /set nointegritychecks off
	if errorlevel 1 goto :BcdError
	echo [OK] Test-signing mode and no-integrity-checks are off.
) else (
	echo [ACTION] Enabling test-signing mode and no-integrity-checks...
	bcdedit /set testsigning on
	if errorlevel 1 goto :BcdError
	bcdedit /set nointegritychecks on
	if errorlevel 1 goto :BcdError
	echo [OK] Test-signing mode and no-integrity-checks are on.
)

echo.
echo [NEXT STEP] Restart Windows for the boot configuration to take effect.
choice /c YN /n /m "Restart the computer now? [Y]es/[N]o: "
if errorlevel 2 goto :NoReboot
if errorlevel 1 (
	echo Restarting Windows in 0 seconds...
	shutdown.exe /r /t 00
)
goto :eof

:NoReboot
echo Please restart Windows later to apply the change.
pause
goto :eof

:BcdError
echo.
echo [ERROR] Failed to update the boot configuration.
echo         No reboot was started. Review the BCDEdit error above.
pause
exit /b 1