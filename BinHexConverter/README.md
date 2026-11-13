# BinHexConverter

**Script Version:** `v1.0.0` | **License:** PolyForm Noncommercial 1.0.0

`bin_hex_converter.py` is a lightweight, cross-platform Python utility to convert raw firmware binary files (`.bin`) into Intel HEX files (`.hex` / `.ihex`) or raw ASCII hex dumps, and vice versa.

## Features

- **Zero External Dependencies**: Uses only the Python standard library—no `pip install` or `requirements.txt` needed.
- **Bidirectional Conversion**:
  - **`.bin` → `.hex`**: Converts raw binary files into 32-bit Intel HEX (`IHEX32`) or plain ASCII hex dumps.
  - **`.hex` → `.bin`**: Parses Intel HEX records (or raw ASCII hex dumps) back into a contiguous raw binary image.
- **Embedded-Friendly Options**:
  - Configurable Flash base/start address (`--base-address`, e.g., `0x08000000` for STM32).
  - Automatic Extended Linear Address (`04`) record generation across 64 KB boundaries.
  - Configurable gap padding byte (`--pad`, defaults to `0xFF` matching erased NOR/MCU Flash).
  - Automatic two's complement record checksum calculation and verification.
- **CLI & Interactive Modes**: Run directly via command-line arguments in build/CI pipelines, or launch without arguments for an interactive prompt.

## Prerequisites

- **Operating System**: Windows, Linux, or macOS
- **Python**: Python 3.8 or newer (`python` on Windows / `python3` on Linux & macOS)
- **External Packages**: None (standard library only)

## Usage

### 1. Interactive Mode

Run the script without arguments to open the interactive step-by-step menu:

```bash
python bin_hex_converter.py
```

### 2. Command-Line Interface (CLI)

The script automatically detects the conversion direction (`bin2hex` or `hex2bin`) based on the file extensions if `--mode` is omitted.

#### Convert Firmware Binary (`.bin`) to Intel HEX (`.hex`)

```bash
# Default base address (0x00000000), outputs firmware.hex
python bin_hex_converter.py firmware.bin

# Specify output path and custom MCU Flash base address (e.g., STM32 at 0x08000000)
python bin_hex_converter.py firmware.bin build/firmware.hex --base-address 0x08000000

# Use 32 data bytes per Intel HEX record line instead of the default 16
python bin_hex_converter.py firmware.bin firmware.hex --base-address 0x08000000 --byte-count 32
```

#### Convert Intel HEX (`.hex`) to Firmware Binary (`.bin`)

```bash
# Auto-detects hex2bin and outputs firmware.bin (gaps filled with 0xFF)
python bin_hex_converter.py firmware.hex

# Specify output path and custom gap fill byte (0x00 instead of 0xFF)
python bin_hex_converter.py firmware.hex build/firmware.bin --pad 0x00
```

#### Convert To / From Raw ASCII Hex Dump

```bash
# Convert .bin to a plain ASCII hex dump (16 bytes per line)
python bin_hex_converter.py firmware.bin firmware_dump.txt --mode bin2hex --format raw

# Convert a plain ASCII hex dump back to a raw .bin file
python bin_hex_converter.py firmware_dump.txt firmware.bin --mode hex2bin --format raw
```

## CLI Arguments Reference

| Argument | Short | Default | Description |
| :--- | :--- | :--- | :--- |
| `input` | — | *(Interactive)* | Path to the input file (`.bin`, `.hex`, etc.). |
| `output` | — | Auto (`.hex`/`.bin`) | Path to the output file. Defaults to swapping the input extension. |
| `--mode` | `-m` | Auto-detected | Explicitly set conversion direction: `bin2hex` or `hex2bin`. |
| `--format` | `-f` | `ihex` | Hex format: `ihex` (Intel HEX) or `raw` (plain ASCII hex bytes). |
| `--base-address` | `-b` | `0x00000000` | Starting memory address for `bin2hex` in Intel HEX mode (accepts hex `0x...` or decimal). |
| `--byte-count` | `-c` | `16` | Number of data bytes per line/record (`1`–`255`). |
| `--pad` | `-p` | `0xFF` | Byte value used to fill address gaps when converting sparse Intel HEX files to `.bin`. |
| `--ignore-checksum` | — | `False` | Ignore checksum mismatches when parsing Intel HEX files. |
| `--help` | `-h` | — | Show help message and usage examples. |

## License

This project is licensed under the **PolyForm Noncommercial License 1.0.0**. See the [LICENSE](LICENSE) file for details.
