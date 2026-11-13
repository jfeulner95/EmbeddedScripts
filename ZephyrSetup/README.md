# Zephyr RTOS & SDK Setup (Ubuntu & Windows)

**Script Version:** `v1.0.0` | **License:** PolyForm Noncommercial 1.0.0

🇬🇧 [**English Version**](#english-version) | 🇩🇪 [**Deutsche Version**](#deutsche-version)

---

## 🇬🇧 English Version

This project contains a cross-platform Python installation script (`setup_zephyr.py`, currently **v1.0.0**) to set up an isolated [Zephyr RTOS](https://www.zephyrproject.org/) development environment on both **Ubuntu (Linux)** and **Windows**.

The script interactively prompts for the desired Zephyr version (tag or branch), installs all required system and Python dependencies into a virtual environment, and automatically downloads and configures the exact matching Zephyr SDK.

### 📋 Prerequisites

* **Operating System:**
  * **Linux:** Ubuntu (tested on 22.04 LTS / 24.04 LTS)
  * **Windows:** Windows 10 / 11 (with `winget` available)
* **Python:** Python 3.8 or newer (`python3` on Ubuntu / `python` on Windows)
* **Architecture:** `x86_64` (`AMD64`) or `aarch64` (`ARM64`)
* **Permissions:**
  * **Ubuntu:** `sudo` privileges (required for installing `apt` system packages)
  * **Windows:** Standard user rights (UAC prompt may appear once during `winget` installations)
* **Disk Space:** Approx. 10–15 GB of free disk space (depending on downloaded modules and toolchains)
* **Network:** Stable internet connection

### 🚀 Installation

#### Option A: Ubuntu (Linux)

1. **Run the Python setup script:**
   Open a terminal, navigate to the directory containing `setup_zephyr.py`, and run it as a regular user (**do not** run directly with `sudo`, otherwise directories will be created under `/root` instead of your home directory):
   ```bash
   python3 setup_zephyr.py
   ```
   *(Optional: You can also make it executable with `chmod +x setup_zephyr.py` and run `./setup_zephyr.py`.)*

#### Option B: Windows (Command Prompt / PowerShell)

1. **Open a Terminal (`cmd.exe` or PowerShell):**
   Navigate to the directory containing `setup_zephyr.py`. *(Tip: Run as a regular user—do not run as Administrator, otherwise the home directory might point to a different account).*

2. **Run the Python setup script:**
   ```cmd
   python setup_zephyr.py
   ```

#### Selecting a Release (Both Platforms)

When prompted, enter the desired Git tag or branch, for example:
* `v3.7.0` (LTS Release)
* `v4.0.0` (Standard Release)
* `main` (Latest development state)

> **Note:** Downloading the Zephyr modules (`west update`) and the Zephyr SDK (approx. 1–2 GB) may take several minutes depending on your internet speed.

### 📁 Directory Structure

After a successful installation, the following folder structure is created in your user home directory (`~` on Ubuntu / `%USERPROFILE%` on Windows):

```text
<HOME_DIRECTORY>/
├── zephyr-sdk-<VERSION>/              # Installed Zephyr SDK & Toolchains
└── sandbox/
    └── zephyr/
        ├── .venv/                     # Isolated Python Virtual Environment (west, etc.)
        ├── activate_zephyr.[sh|bat]   # Helper script to activate the environment
        └── zephyrproject/             # Zephyr Workspace
            ├── zephyr/                # Main Zephyr repository
            ├── modules/               # HALs, drivers, and third-party libraries
            └── tools/                 # Additional build tools
```

### 💻 Daily Usage

#### 1. Activate the Environment

Before starting development or running `west` commands, load the generated activation script in every new terminal session:

* **Ubuntu:**
  ```bash
  source ~/sandbox/zephyr/activate_zephyr.sh
  ```

* **Windows (CMD):**
  ```cmd
  call "%USERPROFILE%\sandbox\zephyr\activate_zephyr.bat"
  ```

This activates the Python virtual environment and sets all required Zephyr environment variables.

#### 2. Build a Sample Project (Hello World)

To verify that everything works properly, you can compile the included *Hello World* sample (e.g., for QEMU or a physical board):

```bash
# 1. Activate environment (use the command for your OS shown above)

# 2. Build project for an emulated ARM Cortex-M3 board
west build -p always -b qemu_cortex_m3 samples/hello_world

# 3. Run in QEMU (Exit with Ctrl+A, then X)
west build -t run
```

### 🔧 Troubleshooting & Tips

* **Using multiple Zephyr versions side-by-side:**
  Since everything is encapsulated under `sandbox/zephyr`, you can adjust `base_dir` in `setup_zephyr.py` (e.g., `home_dir / "sandbox" / "zephyr-v3.7"`) to maintain separate releases cleanly. The SDK is stored version-specifically in your home directory (`zephyr-sdk-0.16.8`, etc.) and will not conflict.

* **Ubuntu – USB permissions for debuggers (udev rules):**
  If you want to flash hardware directly via USB on Ubuntu (e.g., using OpenOCD, J-Link, or ST-Link), copy the udev rules from the SDK once:
  ```bash
  sudo cp ~/zephyr-sdk-*/sysroots/x86_64-pokysdk-linux/usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/
  sudo udevadm control --reload
  ```

* **Windows – Long Paths Support:**
  Zephyr builds can generate deeply nested file paths. If you encounter path length errors on Windows, enable Win32 long paths in PowerShell (as Administrator):
  ```powershell
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```

### 📄 License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**.
You are free to use, modify, and distribute this software for **noncommercial and personal purposes only**. Any commercial or business use is strictly prohibited. See the [LICENSE](LICENSE) file for full details.

---

## 🇩🇪 Deutsche Version

Dieses Projekt enthält ein plattformübergreifendes Python-Installationsskript (`setup_zephyr.py`, aktuell **v1.0.0**), um eine isolierte [Zephyr RTOS](https://www.zephyrproject.org/) Entwicklungsumgebung sowohl unter **Ubuntu (Linux)** als auch unter **Windows** einzurichten.

Das Skript fragt interaktiv nach der gewünschten Zephyr-Version (Tag oder Branch), installiert alle benötigten System- sowie Python-Abhängigkeiten in einer virtuellen Umgebung und lädt automatisch das exakt passende Zephyr SDK herunter.

### 📋 Voraussetzungen

* **Betriebssystem:**
  * **Linux:** Ubuntu (getestet ab 22.04 LTS / 24.04 LTS)
  * **Windows:** Windows 10 / 11 (mit installiertem `winget`)
* **Python:** Python 3.8 oder neuer (`python3` unter Ubuntu / `python` unter Windows)
* **Architektur:** `x86_64` (`AMD64`) oder `aarch64` (`ARM64`)
* **Rechte:**
  * **Ubuntu:** `sudo`-Berechtigungen (für die Installation der `apt`-Systempakete)
  * **Windows:** Normale Benutzerrechte (bei `winget`-Installationen erscheint ggf. einmalig eine Benutzerkontensteuerungs-Abfrage)
* **Speicherplatz:** Ca. 10–15 GB freier Speicherplatz (je nach Anzahl der heruntergeladenen Module und Toolchains)
* **Netzwerk:** Stabile Internetverbindung

### 🚀 Installation

#### Option A: Ubuntu (Linux)

1. **Python-Skript starten:**
   Öffne ein Terminal, navigiere in das Verzeichnis mit `setup_zephyr.py` und führe es als normaler Benutzer aus (**nicht** direkt mit `sudo` starten, da sonst die Verzeichnisse unter `/root` statt in deinem Home-Verzeichnis angelegt werden):
   ```bash
   python3 setup_zephyr.py
   ```
   *(Optional: Du kannst das Skript auch mit `chmod +x setup_zephyr.py` ausführbar machen und direkt per `./setup_zephyr.py` starten.)*

#### Option B: Windows (Eingabeaufforderung / PowerShell)

1. **Terminal (`cmd.exe` oder PowerShell) öffnen:**
   Navigiere in das Verzeichnis, in dem sich `setup_zephyr.py` befindet. *(Tipp: Als normaler Benutzer ausführen – nicht als Administrator, da das Benutzerverzeichnis bei separaten Admin-Konten sonst auf ein anderes Konto verweist).*

2. **Python-Skript starten:**
   ```cmd
   python setup_zephyr.py
   ```

#### Release auswählen (Beide Plattformen)

Gib bei der Aufforderung den gewünschten Git-Tag oder Branch ein, zum Beispiel:
* `v3.7.0` (LTS Release)
* `v4.0.0` (Aktueller Release)
* `main` (Aktueller Entwicklungsstand)

> **Hinweis:** Das Herunterladen der Zephyr-Module (`west update`) und des Zephyr SDKs (ca. 1–2 GB) kann je nach Internetgeschwindigkeit mehrere Minuten in Anspruch nehmen.

### 📁 Verzeichnisstruktur

Nach erfolgreicher Installation ergibt sich folgende Ordnerstruktur in deinem Benutzerverzeichnis (`~` unter Ubuntu / `%USERPROFILE%` unter Windows):

```text
<BENUTZERVERZEICHNIS>/
├── zephyr-sdk-<VERSION>/              # Installiertes Zephyr SDK & Toolchains
└── sandbox/
    └── zephyr/
        ├── .venv/                     # Isoliertes Python Virtual Environment (west, etc.)
        ├── activate_zephyr.[sh|bat]   # Hilfsskript zum Aktivieren der Umgebung
        └── zephyrproject/             # Zephyr Workspace
            ├── zephyr/                # Zephyr Haupt-Repository
            ├── modules/               # HALs, Treiber und Drittanbieter-Bibliotheken
            └── tools/                 # Zusätzliche Build-Tools
```

### 💻 Verwendung im Alltag

#### 1. Umgebung aktivieren

Bevor du mit der Entwicklung beginnst oder `west`-Befehle ausführst, musst du in jedem neuen Terminal das generierte Aktivierungs-Skript laden:

* **Ubuntu:**
  ```bash
  source ~/sandbox/zephyr/activate_zephyr.sh
  ```

* **Windows (CMD):**
  ```cmd
  call "%USERPROFILE%\sandbox\zephyr\activate_zephyr.bat"
  ```

Dadurch wird das Python Virtual Environment aktiviert und alle benötigten Zephyr-Umgebungsvariablen werden gesetzt.

#### 2. Beispielprojekt kompilieren (Hello World)

Um zu testen, ob alles korrekt funktioniert, kannst du das mitgelieferte *Hello World*-Beispiel (z. B. für QEMU oder ein physisches Board) kompilieren:

```bash
# 1. Umgebung aktivieren (passenden Befehl für dein Betriebssystem von oben nutzen)

# 2. Projekt für ein emuliertes ARM Cortex-M3 Board bauen
west build -p always -b qemu_cortex_m3 samples/hello_world

# 3. In QEMU ausführen (Beenden mit Strg+A, danach X)
west build -t run
```

### 🔧 Fehlerbehebung & Tipps

* **Mehrere Zephyr-Versionen parallel nutzen:**
  Da alles unter `sandbox/zephyr` gekapselt ist, kannst du bei Bedarf `base_dir` in `setup_zephyr.py` anpassen (z. B. `home_dir / "sandbox" / "zephyr-v3.7"`), um verschiedene Releases sauber voneinander getrennt zu betreiben. Das SDK wird im Benutzerverzeichnis versionsspezifisch abgelegt (`zephyr-sdk-0.16.8` etc.) und kollidiert nicht miteinander.

* **Ubuntu – USB-Rechte für Debugger (udev-Regeln):**
  Falls du Hardware unter Ubuntu direkt über USB flashen möchtest (z. B. über OpenOCD, J-Link oder ST-Link), solltest du einmalig die udev-Regeln aus dem SDK kopieren:
  ```bash
  sudo cp ~/zephyr-sdk-*/sysroots/x86_64-pokysdk-linux/usr/share/openocd/contrib/60-openocd.rules /etc/udev/rules.d/
  sudo udevadm control --reload
  ```

* **Windows – Unterstützung für lange Dateipfade (Long Paths):**
  Beim Bauen von Zephyr-Projekten entstehen oft sehr tief verschachtelte Ordnerpfade. Falls unter Windows Fehler wegen zu langer Pfade auftreten, aktiviere *Long Paths* einmalig in einer PowerShell (als Administrator):
  ```powershell
  New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
  ```

### 📄 Lizenz

Dieses Projekt steht unter der **PolyForm Noncommercial License 1.0.0**.
Die Nutzung, Veränderung und Weitergabe dieser Software ist ausschließlich für **nicht-kommerzielle und private Zwecke** gestattet. Jede gewerbliche oder geschäftliche Nutzung ist untersagt. Weitere Details findest du in der Datei [LICENSE](LICENSE).