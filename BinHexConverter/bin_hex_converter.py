#!/usr/bin/env python3
"""
Firmware Binary <-> Intel HEX Converter
Version: 1.0.0
License: PolyForm Noncommercial License 1.0.0
Copyright (c) 2026 Johannes Feulner
Author: Johannes Feulner
Note: Zero-dependency utility to convert raw firmware binaries (.bin) to
      Intel HEX (.hex) files and vice versa (also supports raw ASCII hex dumps).
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def compute_ihex_checksum(record_bytes: bytes) -> int:
    """Calculate the two's complement Intel HEX checksum for a byte sequence."""
    return ((~sum(record_bytes) + 1) & 0xFF)


def format_ihex_record(record_type: int, address: int, data: bytes = b"") -> str:
    """Create a formatted Intel HEX record line (including ':' and checksum)."""
    length = len(data)
    header = bytes([length, (address >> 8) & 0xFF, address & 0xFF, record_type])
    payload = header + data
    checksum = compute_ihex_checksum(payload)
    return f":{payload.hex().upper()}{checksum:02X}"


def bin_to_ihex(
    bin_data: bytes,
    base_address: int = 0x00000000,
    byte_count: int = 16,
) -> str:
    """
    Convert raw binary bytes into Intel HEX (IHEX32) format.

    :param bin_data: Raw binary payload.
    :param base_address: Starting memory address (e.g., 0x08000000 for STM32).
    :param byte_count: Number of data bytes per record line (typically 16 or 32).
    :return: Intel HEX string content.
    """
    if byte_count <= 0 or byte_count > 255:
        raise ValueError("byte_count must be between 1 and 255.")
    if base_address < 0 or base_address + len(bin_data) > 0x100000000:
        raise ValueError("Address range exceeds 32-bit Intel HEX address space.")

    lines: List[str] = []
    current_upper_address: Optional[int] = None
    total_len = len(bin_data)
    offset = 0

    # If the base address has a non-zero upper 16-bit address even for an empty file, emit it
    if total_len == 0 and (base_address >> 16) != 0:
        upper = (base_address >> 16) & 0xFFFF
        lines.append(format_ihex_record(0x04, 0x0000, upper.to_bytes(2, "big")))

    while offset < total_len:
        abs_addr = base_address + offset
        upper_addr = (abs_addr >> 16) & 0xFFFF
        lower_addr = abs_addr & 0xFFFF

        # Emit Extended Linear Address record (04) when upper 16 bits change
        if upper_addr != current_upper_address:
            if upper_addr != 0 or current_upper_address is not None:
                lines.append(
                    format_ihex_record(0x04, 0x0000, upper_addr.to_bytes(2, "big"))
                )
            current_upper_address = upper_addr

        # Do not cross a 64 KB boundary within a single data record
        bytes_until_boundary = 0x10000 - lower_addr
        chunk_len = min(byte_count, total_len - offset, bytes_until_boundary)
        chunk = bin_data[offset : offset + chunk_len]

        lines.append(format_ihex_record(0x00, lower_addr, chunk))
        offset += chunk_len

    # End Of File record (01)
    lines.append(format_ihex_record(0x01, 0x0000))
    return "\n".join(lines) + "\n"


def ihex_to_bin(
    ihex_text: str,
    fill_byte: int = 0xFF,
    ignore_checksum: bool = False,
) -> Tuple[bytes, int, int, Optional[int]]:
    """
    Convert Intel HEX content into a contiguous raw binary buffer.

    :param ihex_text: Content of the Intel HEX file.
    :param fill_byte: Padding byte used for gaps between segments (default 0xFF).
    :param ignore_checksum: If True, do not fail on checksum mismatches.
    :return: Tuple of (binary_data, min_address, max_address, start_linear_address).
    """
    if not (0 <= fill_byte <= 0xFF):
        raise ValueError("fill_byte must be between 0x00 and 0xFF.")

    chunks: List[Tuple[int, bytes]] = []
    upper_address = 0
    start_linear_addr: Optional[int] = None
    eof_seen = False

    for line_num, raw_line in enumerate(ihex_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue

        if not line.startswith(":"):
            raise ValueError(f"Line {line_num}: Missing start code ':' -> {line!r}")

        hex_part = line[1:]
        if len(hex_part) < 10 or len(hex_part) % 2 != 0:
            raise ValueError(f"Line {line_num}: Invalid record length -> {line!r}")

        try:
            raw_bytes = bytes.fromhex(hex_part)
        except ValueError as exc:
            raise ValueError(f"Line {line_num}: Invalid hex characters -> {exc}") from exc

        byte_count = raw_bytes[0]
        if len(raw_bytes) != byte_count + 5:
            raise ValueError(
                f"Line {line_num}: Byte count mismatch (expected {byte_count} data bytes, "
                f"got {len(raw_bytes) - 5})."
            )

        if not ignore_checksum:
            expected_crc = compute_ihex_checksum(raw_bytes[:-1])
            actual_crc = raw_bytes[-1]
            if expected_crc != actual_crc:
                raise ValueError(
                    f"Line {line_num}: Checksum error (expected 0x{expected_crc:02X}, "
                    f"got 0x{actual_crc:02X})."
                )

        address = (raw_bytes[1] << 8) | raw_bytes[2]
        record_type = raw_bytes[3]
        data = raw_bytes[4:-1]

        if record_type == 0x00:  # Data record
            abs_addr = upper_address + address
            chunks.append((abs_addr, data))
        elif record_type == 0x01:  # End Of File
            eof_seen = True
            break
        elif record_type == 0x02:  # Extended Segment Address
            if byte_count != 2:
                raise ValueError(f"Line {line_num}: Record type 02 requires 2 data bytes.")
            upper_address = int.from_bytes(data, "big") << 4
        elif record_type == 0x03:  # Start Segment Address (CS:IP)
            if byte_count != 4:
                raise ValueError(f"Line {line_num}: Record type 03 requires 4 data bytes.")
            start_linear_addr = int.from_bytes(data, "big")
        elif record_type == 0x04:  # Extended Linear Address
            if byte_count != 2:
                raise ValueError(f"Line {line_num}: Record type 04 requires 2 data bytes.")
            upper_address = int.from_bytes(data, "big") << 16
        elif record_type == 0x05:  # Start Linear Address (EIP)
            if byte_count != 4:
                raise ValueError(f"Line {line_num}: Record type 05 requires 4 data bytes.")
            start_linear_addr = int.from_bytes(data, "big")
        else:
            raise ValueError(f"Line {line_num}: Unsupported record type 0x{record_type:02X}.")

    if not eof_seen:
        print(
            "Warning: Intel HEX file is missing an End-Of-File (:00000001FF) record.",
            file=sys.stderr,
        )

    if not chunks:
        return b"", 0, 0, start_linear_addr

    min_addr = min(addr for addr, _ in chunks)
    max_addr = max(addr + len(data) for addr, data in chunks)
    total_size = max_addr - min_addr

    buffer = bytearray([fill_byte] * total_size)
    for addr, data in chunks:
        start = addr - min_addr
        buffer[start : start + len(data)] = data

    return bytes(buffer), min_addr, max_addr, start_linear_addr


def bin_to_raw_hex(bin_data: bytes, bytes_per_line: int = 16) -> str:
    """Convert raw binary bytes to a plain ASCII hexadecimal dump."""
    if bytes_per_line <= 0:
        return bin_data.hex().upper() + "\n"
    lines = [
        bin_data[i : i + bytes_per_line].hex().upper()
        for i in range(0, len(bin_data), bytes_per_line)
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def raw_hex_to_bin(hex_text: str) -> bytes:
    """Convert a plain ASCII hexadecimal string/dump (ignoring whitespace/0x) into binary bytes."""
    cleaned_tokens: List[str] = []
    for line in hex_text.splitlines():
        # Strip comments starting with # or //
        line = line.split("#", 1)[0].split("//", 1)[0]
        for token in line.replace(",", " ").split():
            if token.lower().startswith("0x"):
                token = token[2:]
            cleaned_tokens.append(token)
    joined = "".join(cleaned_tokens)
    if len(joined) % 2 != 0:
        raise ValueError("Raw hex input contains an odd number of hex digits.")
    return bytes.fromhex(joined)


def parse_int(value: str) -> int:
    """Parse an integer from decimal or hexadecimal (0x...) string."""
    try:
        return int(value, 0)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid integer or hex value: {value!r}") from exc


def detect_mode(input_path: Path, output_path: Optional[Path]) -> str:
    """Auto-detect conversion direction from file extensions."""
    in_ext = input_path.suffix.lower()
    out_ext = output_path.suffix.lower() if output_path else ""

    if in_ext in {".hex", ".ihex", ".ihx"} or out_ext == ".bin":
        return "hex2bin"
    if in_ext == ".bin" or out_ext in {".hex", ".ihex", ".ihx"}:
        return "bin2hex"
    raise ValueError(
        f"Cannot auto-detect conversion mode from '{input_path.name}'. "
        "Please specify '--mode bin2hex' or '--mode hex2bin'."
    )


def default_output_path(input_path: Path, mode: str) -> Path:
    """Generate default output path by swapping extension."""
    target_ext = ".hex" if mode == "bin2hex" else ".bin"
    return input_path.with_suffix(target_ext)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert firmware binary (.bin) files to Intel HEX (.hex) and vice versa.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Auto-detect .bin -> .hex (default base address 0x00000000)\n"
            "  python bin_hex_converter.py firmware.bin\n\n"
            "  # Convert .bin -> .hex with STM32 Flash base address 0x08000000\n"
            "  python bin_hex_converter.py firmware.bin firmware.hex --base-address 0x08000000\n\n"
            "  # Convert .hex -> .bin (gaps padded with 0xFF)\n"
            "  python bin_hex_converter.py firmware.hex firmware.bin\n\n"
            "  # Convert .bin -> plain raw ASCII hex dump\n"
            "  python bin_hex_converter.py firmware.bin dump.txt --format raw\n"
        ),
    )
    parser.add_argument(
        "input",
        nargs="?",
        type=Path,
        help="Path to the input file (.bin or .hex).",
    )
    parser.add_argument(
        "output",
        nargs="?",
        type=Path,
        help="Path to the output file (optional; defaults to swapping extension).",
    )
    parser.add_argument(
        "-m",
        "--mode",
        choices=["bin2hex", "hex2bin"],
        help="Conversion direction (auto-detected from file extension if omitted).",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["ihex", "raw"],
        default="ihex",
        help="Hex format: 'ihex' for Intel HEX (default) or 'raw' for plain ASCII hex bytes.",
    )
    parser.add_argument(
        "-b",
        "--base-address",
        type=parse_int,
        default=0x00000000,
        help="Base/start address for bin2hex in IHEX mode (default: 0x00000000, e.g. 0x08000000).",
    )
    parser.add_argument(
        "-c",
        "--byte-count",
        type=parse_int,
        default=16,
        help="Number of bytes per line/record (default: 16).",
    )
    parser.add_argument(
        "-p",
        "--pad",
        type=parse_int,
        default=0xFF,
        help="Fill/pad byte for memory gaps in hex2bin mode (default: 0xFF).",
    )
    parser.add_argument(
        "--ignore-checksum",
        action="store_true",
        help="Ignore Intel HEX record checksum errors during hex2bin conversion.",
    )
    return parser


def run_interactive() -> int:
    """Interactive console mode when executed without CLI arguments."""
    print("====================================================")
    print("      Firmware Binary <-> HEX Converter (v1.0.0)    ")
    print("====================================================")
    print("1) Convert Firmware Binary (.bin) -> Intel HEX (.hex)")
    print("2) Convert Intel HEX (.hex)       -> Firmware Binary (.bin)")
    print("3) Convert Firmware Binary (.bin) -> Raw ASCII Hex")
    print("4) Convert Raw ASCII Hex          -> Firmware Binary (.bin)")

    choice = input("\nSelect an option [1-4]: ").strip()
    mapping = {
        "1": ("bin2hex", "ihex"),
        "2": ("hex2bin", "ihex"),
        "3": ("bin2hex", "raw"),
        "4": ("hex2bin", "raw"),
    }
    if choice not in mapping:
        print("Error: Invalid selection.", file=sys.stderr)
        return 1

    mode, fmt = mapping[choice]
    in_str = input("Enter input file path: ").strip().strip('"')
    if not in_str:
        print("Error: Input file path is required.", file=sys.stderr)
        return 1

    input_path = Path(in_str)
    default_out = default_output_path(input_path, mode)
    out_str = input(f"Enter output file path [{default_out}]: ").strip().strip('"')
    output_path = Path(out_str) if out_str else default_out

    base_address = 0x00000000
    if mode == "bin2hex" and fmt == "ihex":
        addr_str = input("Enter base address [0x00000000]: ").strip()
        if addr_str:
            base_address = int(addr_str, 0)

    return execute_conversion(
        input_path=input_path,
        output_path=output_path,
        mode=mode,
        fmt=fmt,
        base_address=base_address,
        byte_count=16,
        pad_byte=0xFF,
        ignore_checksum=False,
    )


def execute_conversion(
    input_path: Path,
    output_path: Path,
    mode: str,
    fmt: str,
    base_address: int,
    byte_count: int,
    pad_byte: int,
    ignore_checksum: bool,
) -> int:
    """Perform the requested conversion and print a summary."""
    if not input_path.is_file():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        return 1

    try:
        if mode == "bin2hex":
            bin_data = input_path.read_bytes()
            if fmt == "ihex":
                hex_output = bin_to_ihex(
                    bin_data,
                    base_address=base_address,
                    byte_count=byte_count,
                )
            else:
                hex_output = bin_to_raw_hex(bin_data, bytes_per_line=byte_count)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(hex_output, encoding="ascii")

            end_addr = base_address + len(bin_data)
            print(f"Successfully converted BIN -> HEX ({fmt.upper()})")
            print(f"  Input file   : {input_path} ({len(bin_data):,} bytes)")
            print(f"  Output file  : {output_path}")
            if fmt == "ihex":
                print(f"  Address range: 0x{base_address:08X} - 0x{end_addr:08X}")

        elif mode == "hex2bin":
            hex_text = input_path.read_text(encoding="utf-8", errors="replace")
            if fmt == "ihex":
                bin_data, min_addr, max_addr, start_addr = ihex_to_bin(
                    hex_text,
                    fill_byte=pad_byte,
                    ignore_checksum=ignore_checksum,
                )
            else:
                bin_data = raw_hex_to_bin(hex_text)
                min_addr, max_addr, start_addr = 0, len(bin_data), None

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_bytes(bin_data)

            print(f"Successfully converted HEX ({fmt.upper()}) -> BIN")
            print(f"  Input file   : {input_path}")
            print(f"  Output file  : {output_path} ({len(bin_data):,} bytes)")
            if fmt == "ihex" and bin_data:
                print(f"  Address range: 0x{min_addr:08X} - 0x{max_addr:08X}")
                if start_addr is not None:
                    print(f"  Entry point  : 0x{start_addr:08X}")

    except Exception as exc:
        print(f"Error during conversion: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.input is None:
        return run_interactive()

    try:
        mode = args.mode or detect_mode(args.input, args.output)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    output_path = args.output or default_output_path(args.input, mode)
    return execute_conversion(
        input_path=args.input,
        output_path=output_path,
        mode=mode,
        fmt=args.format,
        base_address=args.base_address,
        byte_count=args.byte_count,
        pad_byte=args.pad,
        ignore_checksum=args.ignore_checksum,
    )


if __name__ == "__main__":
    sys.exit(main())
