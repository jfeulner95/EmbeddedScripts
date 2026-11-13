REM Copyright (c) 2026 Johannes Feulner
REM
REM SPDX-License-Identifier: PolyForm Noncommercial License 1.0.0
REM
REM Author: Johannes Feulner
REM
REM Name: setup_zephyr.sh
REM
REM Version: 1.0.0
REM
REM Interactive setup scripts (Ubuntu & Windows) to automatically
REM install a chosen Zephyr RTOS release, workspace, dependencies,
REM and the matching Zephyr SDK.


@echo off
setlocal EnableDelayedExpansion

echo ==================================================
echo    Zephyr RTOS ^& SDK Automatic Setup (Windows)    
echo ==================================================
echo.

:: 1. Prompt for the desired Zephyr release
set /p ZEPHYR_REF="Which Zephyr release do you want to install? (e.g. v3.7.0, v4.0.0, or 'main'): "

if "%ZEPHYR_REF%"=="" (
    echo Error: No release specified. Aborting.
    exit /b 1
)

:: Define directory paths
set "BASE_DIR=%USERPROFILE%\sandbox\zephyr"
set "WORKSPACE_DIR=%BASE_DIR%\zephyrproject"
set "VENV_DIR=%BASE_DIR%\.venv"
:: Default path where Zephyr automatically searches for the SDK on Windows
set "SDK_INSTALL_DIR=%USERPROFILE%"

echo.
echo [1/6] Installing required Windows dependencies via winget...
echo Note: Existing packages will be skipped automatically.
winget install -e --id Kitware.CMake --accept-package-agreements --accept-source-agreements --silent
winget install -e --id Ninja-build.Ninja --accept-package-agreements --accept-source-agreements --silent
winget install -e --id oss-winget.gperf --accept-package-agreements --accept-source-agreements --silent
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements --silent
winget install -e --id Git.Git --accept-package-agreements --accept-source-agreements --silent
winget install -e --id oss-winget.dtc --accept-package-agreements --accept-source-agreements --silent
winget install -e --id wget --accept-package-agreements --accept-source-agreements --silent
winget install -e --id 7zip.7zip --accept-package-agreements --accept-source-agreements --silent

:: Refresh PATH for the current session so newly installed tools are immediately available
for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SYS_PATH=%%b"
for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "USR_PATH=%%b"
set "PATH=%SYS_PATH%;%USR_PATH%;%ProgramFiles%\7-Zip"

echo.
echo [2/6] Creating working directory at %BASE_DIR%...
if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"
cd /d "%BASE_DIR%"

echo.
echo [3/6] Creating Python virtual environment and installing 'west'...
python -m venv "%VENV_DIR%"
if errorlevel 1 (
    echo Error: Failed to create Python virtual environment. Please restart your terminal if Python was just installed.
    exit /b 1
)

call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install west

echo.
echo [4/6] Initializing Zephyr workspace for release '%ZEPHYR_REF%'...
if exist "%WORKSPACE_DIR%" (
    echo Warning: %WORKSPACE_DIR% already exists. Skipping 'west init'...
) else (
    west init -m https://github.com/zephyrproject-rtos/zephyr --mr "%ZEPHYR_REF%" "%WORKSPACE_DIR%"
    if errorlevel 1 (
        echo Error: 'west init' failed. Check the release name and your internet connection.
        exit /b 1
    )
)

cd /d "%WORKSPACE_DIR%"
echo Downloading Zephyr modules (this may take a few minutes)...
west update
if errorlevel 1 exit /b 1

echo Exporting Zephyr CMake packages...
west zephyr-export

echo Installing Python dependencies for the selected release...
pip install -r "%WORKSPACE_DIR%\zephyr\scripts\requirements.txt"

echo.
echo [5/6] Detecting and installing matching Zephyr SDK...
set "SDK_VERSION_FILE=%WORKSPACE_DIR%\zephyr\SDK_VERSION"

if not exist "%SDK_VERSION_FILE%" (
    echo Error: SDK_VERSION file not found at %SDK_VERSION_FILE%
    exit /b 1
)

:: Read version number and strip whitespace
set /p SDK_VERSION=<"%SDK_VERSION_FILE%"
set "SDK_VERSION=%SDK_VERSION: =%"
echo Required SDK version according to Zephyr repository: %SDK_VERSION%

:: Detect Windows architecture (x86_64 or aarch64)
if /i "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "SDK_ARCH=x86_64"
) else if /i "%PROCESSOR_ARCHITECTURE%"=="ARM64" (
    set "SDK_ARCH=aarch64"
) else (
    echo Unsupported architecture: %PROCESSOR_ARCHITECTURE%
    exit /b 1
)

set "SDK_DIR=%SDK_INSTALL_DIR%\zephyr-sdk-%SDK_VERSION%"

if exist "%SDK_DIR%" (
    echo Zephyr SDK %SDK_VERSION% is already installed at %SDK_DIR%.
) else (
    set "SDK_ARCHIVE=zephyr-sdk-%SDK_VERSION%_windows-%SDK_ARCH%.7z"
    set "SDK_URL=https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v%SDK_VERSION%/!SDK_ARCHIVE!"

    cd /d "%BASE_DIR%"
    echo Downloading SDK from: !SDK_URL!
    curl.exe -L -o "!SDK_ARCHIVE!" "!SDK_URL!"
    if errorlevel 1 (
        echo Error: Failed to download the Zephyr SDK.
        exit /b 1
    )

    echo Extracting SDK to %SDK_INSTALL_DIR% (this may take a moment)...
    7z x "!SDK_ARCHIVE!" -o"%SDK_INSTALL_DIR%" -y >nul
    del "!SDK_ARCHIVE!"

    echo Running SDK setup...
    cd /d "%SDK_DIR%"
    :: /t all installs all toolchains, /h installs host tools, /c registers CMake packages
    call setup.cmd /t all /h /c
)

echo.
echo [6/6] Creating convenience activation script...
(
    echo @echo off
    echo call "%VENV_DIR%\Scripts\activate.bat"
    echo set "ZEPHYR_BASE=%WORKSPACE_DIR%\zephyr"
    echo cd /d "%WORKSPACE_DIR%\zephyr"
    echo echo Zephyr environment ^(%ZEPHYR_REF%^) is active!
) > "%BASE_DIR%\activate_zephyr.bat"

echo.
echo ==================================================
echo  Installation completed successfully!             
echo ==================================================
echo Workspace path : %WORKSPACE_DIR%
echo SDK path       : %SDK_DIR%
echo.
echo To use the environment in the future, simply run:
echo   call "%BASE_DIR%\activate_zephyr.bat"
echo.
pause