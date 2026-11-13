REM Copyright (c) 2026 Johannes Feulner
REM
REM SPDX-License-Identifier: PolyForm Noncommercial License 1.0.0
REM
REM Author: Johannes Feulner
REM
REM Name: WindowsSystemAudit.bat
REM
REM Version: 1.0.0
REM
REM Creates a log, separate registry exports, and driver lists.

@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "SCRIPT_NAME=%~nx0"
set "DO_IDENTITY=0"
set "DO_HARDWARE=0"
set "DO_SYSTEM=0"
set "DO_SOFTWARE=0"
set "DO_DRIVERS=0"
set "DO_REGISTRY=0"
set "DO_ALL=0"
set "ARG_COUNT=0"
set "ARG_SEEN=0"

:parse_args
if "%~1"=="" goto args_done
set "ARG_SEEN=1"
set /a ARG_COUNT+=1
if /i "%~1"=="all" goto arg_all
if /i "%~1"=="identity" goto arg_identity
if /i "%~1"=="hardware" goto arg_hardware
if /i "%~1"=="system" goto arg_system
if /i "%~1"=="software" goto arg_software
if /i "%~1"=="drivers" goto arg_drivers
if /i "%~1"=="registry" goto arg_registry
goto usage_error

:arg_all
set "DO_ALL=1"
goto arg_consumed
:arg_identity
set "DO_IDENTITY=1"
goto arg_consumed
:arg_hardware
set "DO_HARDWARE=1"
goto arg_consumed
:arg_system
set "DO_SYSTEM=1"
goto arg_consumed
:arg_software
set "DO_SOFTWARE=1"
goto arg_consumed
:arg_drivers
set "DO_DRIVERS=1"
goto arg_consumed
:arg_registry
set "DO_REGISTRY=1"
:arg_consumed
shift
goto parse_args

:args_done
if "%DO_ALL%"=="1" if not "%ARG_COUNT%"=="1" goto usage_error
if "%ARG_SEEN%"=="0" set "DO_ALL=1"
if "%DO_ALL%"=="1" (
    set "DO_IDENTITY=1"
    set "DO_HARDWARE=1"
    set "DO_SYSTEM=1"
    set "DO_SOFTWARE=1"
    set "DO_DRIVERS=1"
    set "DO_REGISTRY=1"
)

set "PROGRESS_TOTAL=1"
if "%DO_IDENTITY%"=="1" set /a PROGRESS_TOTAL+=1
if "%DO_HARDWARE%"=="1" set /a PROGRESS_TOTAL+=1
if "%DO_SYSTEM%"=="1" set /a PROGRESS_TOTAL+=1
if "%DO_SOFTWARE%"=="1" set /a PROGRESS_TOTAL+=1
if "%DO_DRIVERS%"=="1" set /a PROGRESS_TOTAL+=1
if "%DO_REGISTRY%"=="1" set /a PROGRESS_TOTAL+=1

set "VERSION=1.0.0"
set "PROGRESS_DONE=0"
set "SCRIPT_DIR=%~dp0"
for /f "usebackq delims=" %%I in (`powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "(Get-Date).ToString('yyyyMMdd_HHmmss')"`) do set "STAMP=%%I"
if not defined STAMP set "STAMP=without_timestamp"

set "OUTDIR=%SCRIPT_DIR%Windows-System-Audit_%COMPUTERNAME%_%STAMP%"
set "LOG=%OUTDIR%\SystemAudit.log"

if not exist "%OUTDIR%" mkdir "%OUTDIR%" >nul 2>&1
if not exist "%OUTDIR%" (
    echo ERROR: Unable to create output folder: "%OUTDIR%"
    exit /b 1
)

echo Windows System Audit v%VERSION%
echo Version: %VERSION%
echo Computer: %COMPUTERNAME%
if "%DO_ALL%"=="1" echo Categories: all
if not "%DO_ALL%"=="1" echo Categories: %*
echo Output folder: %OUTDIR%

> "%LOG%" echo Windows System Audit v%VERSION%
>>"%LOG%" echo Version: %VERSION%
>>"%LOG%" echo Computer: %COMPUTERNAME%
if "%DO_ALL%"=="1" >>"%LOG%" echo Categories: all
if not "%DO_ALL%"=="1" >>"%LOG%" echo Categories: %*
>>"%LOG%" echo Start: %DATE% %TIME%
>>"%LOG%" echo Output folder: %OUTDIR%
>>"%LOG%" echo.

if not "%DO_IDENTITY%"=="1" goto skip_identity
call :show_progress "Permissions and system identification"
call :section "Permissions and system identification"
call :run "whoami /all"
call :run "ver"
call :run "systeminfo"
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-ComputerInfo"""
:skip_identity

if not "%DO_HARDWARE%"=="1" goto skip_hardware
call :show_progress "Hardware - CPU, RAM, BIOS, motherboard, storage, and network"
call :section "Hardware - CPU, RAM, BIOS, motherboard, storage, and network"
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_Processor"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_PhysicalMemory"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_BIOS"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_BaseBoard"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_DiskDrive"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_LogicalDisk"""
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_VideoController"""
call :run "ipconfig /all"
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-NetAdapter"""
:skip_hardware

if not "%DO_SYSTEM%"=="1" goto skip_system
call :show_progress "Windows configuration and services"
call :section "Windows configuration and services"
call :run "set"
call :run "tasklist /v"
call :run "sc query type= all state= all"
call :run "schtasks /query /fo LIST /v"
call :run "bcdedit /enum all"
call :run "powercfg /list"
call :run "net accounts"
call :run "net localgroup administrators"
call :run "net user"
:skip_system

if not "%DO_SOFTWARE%"=="1" goto skip_software
call :show_progress "Installed software"
call :section "Installed software"
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""$paths='HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'; Get-ItemProperty $paths -ErrorAction SilentlyContinue"""
call :run "winget list --accept-source-agreements"
:skip_software

if not "%DO_DRIVERS%"=="1" goto skip_drivers
call :show_progress "Installed drivers"
call :section "Installed drivers"
call :run "driverquery /v /fo list"
call :run "pnputil /enum-drivers"
call :run "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command ""Get-CimInstance Win32_PnPSignedDriver"""
:skip_drivers

if not "%DO_REGISTRY%"=="1" goto skip_registry
call :show_progress "Registry - complete exports"
call :section "Registry - complete exports"
>>"%LOG%" echo Note: The following exports may be very large and are stored separately in the output folder.
reg export HKLM "%OUTDIR%\HKLM.reg" /y >>"%LOG%" 2>&1
if errorlevel 1 >>"%LOG%" echo ERROR while exporting HKLM.
reg export HKCU "%OUTDIR%\HKCU.reg" /y >>"%LOG%" 2>&1
if errorlevel 1 >>"%LOG%" echo ERROR while exporting HKCU.
reg export HKCR "%OUTDIR%\HKCR.reg" /y >>"%LOG%" 2>&1
if errorlevel 1 >>"%LOG%" echo ERROR while exporting HKCR.
reg export HKU "%OUTDIR%\HKU.reg" /y >>"%LOG%" 2>&1
if errorlevel 1 >>"%LOG%" echo ERROR while exporting HKU.
call :run "reg query HKLM /s"
call :run "reg query HKCU /s"
:skip_registry

call :show_progress "Completion"
call :section "Completion"
>>"%LOG%" echo End: %DATE% %TIME%
if "%DO_REGISTRY%"=="1" >>"%LOG%" echo Registry files: HKLM.reg, HKCU.reg, HKCR.reg, HKU.reg
if not "%DO_REGISTRY%"=="1" >>"%LOG%" echo Registry exports: not requested.
echo.
echo Finished. Report: "%LOG%"
if "%DO_REGISTRY%"=="1" echo Registry exports and log file are located in: "%OUTDIR%"
if not "%DO_REGISTRY%"=="1" echo Log file is located in: "%OUTDIR%"
exit /b 0

:usage_error
echo Usage: %SCRIPT_NAME% [all^|identity^|hardware^|system^|software^|drivers^|registry ...]
echo Specify one or more categories. Use "all" by itself, or omit arguments for all categories.
exit /b 2

:show_progress
set /a "PROGRESS_DONE+=1"
set /a "PROGRESS_PERCENT=PROGRESS_DONE*100/PROGRESS_TOTAL"
echo [Progress: %PROGRESS_PERCENT%%%] %~1
exit /b 0

:section
>>"%LOG%" echo.
>>"%LOG%" echo ============================================================
>>"%LOG%" echo %~1
>>"%LOG%" echo ============================================================
exit /b 0

:run
>>"%LOG%" echo.
>>"%LOG%" echo --- %~1 ---
>>"%LOG%" 2>&1 %~1
if errorlevel 1 >>"%LOG%" echo [Note] Command returned an error code or requires administrator privileges.
exit /b 0
