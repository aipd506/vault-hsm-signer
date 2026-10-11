"""ISO 9564 payment PIN block generation, encoding, and extraction."""

import secrets
from typing import Tuple


def _xor_hex(hex1: str, hex2: str) -> str:
    """XOR two equal-length hex strings and return uppercase hex result."""
    assert len(hex1) == len(hex2)
    val1 = int(hex1, 16)
    val2 = int(hex2, 16)
    res = val1 ^ val2
    return f"{res:0{len(hex1)}X}"


def get_pan_field(pan: str) -> str:
    """Extract 16-hex character PAN field: 4 zeros + 12 rightmost digits of PAN excluding check digit."""
    clean = pan.strip().replace(" ", "").replace("-", "")
    if len(clean) < 13:
        raise ValueError(f"PAN must be at least 13 digits for ISO 9564, got '{pan}'")

    # Exclude check digit (clean[-1]), take 12 digits immediately to the left
    twelve_digits = clean[-13:-1]
    return "0000" + twelve_digits


def create_pin_block_format_0(pin: str, pan: str) -> str:
    """Encode clear PIN into 16-character ISO 9564-1 Format 0 (ANSI X9.8) PIN block."""
    clean_pin = pin.strip()
    if not (4 <= len(clean_pin) <= 12) or not clean_pin.isdigit():
        raise ValueError(f"PIN must be 4 to 12 numeric digits, got '{pin}'")

    pin_len_hex = f"{len(clean_pin):X}"
    pin_field = f"0{pin_len_hex}{clean_pin}".ljust(16, "F").upper()

    pan_field = get_pan_field(pan)
    return _xor_hex(pin_field, pan_field)


def extract_pin_format_0(pin_block_hex: str, pan: str) -> str:
    """Extract clear PIN from an ISO 9564-1 Format 0 PIN block using the PAN."""
    clean_block = pin_block_hex.strip().upper()
    if len(clean_block) != 16:
        raise ValueError(f"PIN block must be exactly 16 hex characters, got '{pin_block_hex}'")

    pan_field = get_pan_field(pan)
    pin_field = _xor_hex(clean_block, pan_field)

    if pin_field[0] != "0":
        raise ValueError(f"Invalid Format 0 block: first nibble '{pin_field[0]}' != '0'")

    pin_len = int(pin_field[1], 16)
    if not (4 <= pin_len <= 12):
        raise ValueError(f"Invalid PIN length indicator: {pin_len}")

    pin_digits = pin_field[2 : 2 + pin_len]
    if not pin_digits.isdigit():
        raise ValueError(f"Extracted PIN contains non-digit characters: {pin_digits}")

    padding = pin_field[2 + pin_len :]
    if padding and padding != "F" * len(padding):
        raise ValueError("Invalid Format 0 block: padding corrupted (incorrect PAN)")

    return pin_digits


def create_pin_block_format_1(pin: str) -> str:
    """Encode clear PIN into 16-character ISO 9564-1 Format 1 PIN block (random padding, no PAN)."""
    clean_pin = pin.strip()
    if not (4 <= len(clean_pin) <= 12) or not clean_pin.isdigit():
        raise ValueError(f"PIN must be 4 to 12 numeric digits, got '{pin}'")

    pin_len_hex = f"{len(clean_pin):X}"
    prefix = f"1{pin_len_hex}{clean_pin}"
    pad_len = 16 - len(prefix)
    random_pad = "".join(f"{secrets.randbelow(16):X}" for _ in range(pad_len))
    return (prefix + random_pad).upper()


def extract_pin_format_1(pin_block_hex: str) -> str:
    """Extract clear PIN from an ISO 9564-1 Format 1 PIN block."""
    clean_block = pin_block_hex.strip().upper()
    if len(clean_block) != 16:
        raise ValueError(f"PIN block must be exactly 16 hex characters, got '{pin_block_hex}'")

    if clean_block[0] != "1":
        raise ValueError(f"Invalid Format 1 block: first nibble '{clean_block[0]}' != '1'")

    pin_len = int(clean_block[1], 16)
    if not (4 <= pin_len <= 12):
        raise ValueError(f"Invalid PIN length indicator: {pin_len}")

    return clean_block[2 : 2 + pin_len]


def create_pin_block_format_3(pin: str, pan: str) -> str:
    """Encode clear PIN into 16-character ISO 9564-1 Format 3 PIN block."""
    clean_pin = pin.strip()
    if not (4 <= len(clean_pin) <= 12) or not clean_pin.isdigit():
        raise ValueError(f"PIN must be 4 to 12 numeric digits, got '{pin}'")

    pin_len_hex = f"{len(clean_pin):X}"
    prefix = f"3{pin_len_hex}{clean_pin}"
    pad_len = 16 - len(prefix)
    # Filler is random hex digits 10-15 (A-F)
    filler = "".join(f"{secrets.choice([10, 11, 12, 13, 14, 15]):X}" for _ in range(pad_len))
    pin_field = (prefix + filler).upper()

    pan_field = get_pan_field(pan)
    return _xor_hex(pin_field, pan_field)


def extract_pin_format_3(pin_block_hex: str, pan: str) -> str:
    """Extract clear PIN from an ISO 9564-1 Format 3 PIN block."""
    clean_block = pin_block_hex.strip().upper()
    if len(clean_block) != 16:
        raise ValueError(f"PIN block must be exactly 16 hex characters, got '{pin_block_hex}'")

    pan_field = get_pan_field(pan)
    pin_field = _xor_hex(clean_block, pan_field)

    if pin_field[0] != "3":
        raise ValueError(f"Invalid Format 3 block: first nibble '{pin_field[0]}' != '3'")

    pin_len = int(pin_field[1], 16)
    if not (4 <= pin_len <= 12):
        raise ValueError(f"Invalid PIN length indicator: {pin_len}")

    return pin_field[2 : 2 + pin_len]
