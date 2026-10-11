"""Visa PIN Verification Value (PVV) computation and verification engine."""

import hashlib
import hmac
from .cvv_engine import decimalize_hex

DEFAULT_PVK = "11223344556677889900AABBCCDDEEFF"


def generate_pvv(
    pan: str,
    pin: str,
    pvki: int = 1,
    pvk_hex: str = DEFAULT_PVK,
) -> str:
    """Generate 4-digit Visa PIN Verification Value (PVV)."""
    clean_pan = pan.strip().replace(" ", "").replace("-", "")
    clean_pin = pin.strip()

    if not (1 <= pvki <= 6):
        raise ValueError(f"PVKI must be between 1 and 6, got {pvki}")
    if len(clean_pin) != 4 or not clean_pin.isdigit():
        raise ValueError(f"PIN for PVV must be 4 digits, got '{pin}'")
    if len(clean_pan) < 13:
        raise ValueError(f"PAN must be at least 13 digits, got '{pan}'")

    # Exclude check digit and take rightmost 11 digits
    eleven_digits = clean_pan[-12:-1]

    # Data: 11 digits of PAN + 1 digit PVKI + 4 digit PIN = 16 digits
    data_str = f"{eleven_digits}{pvki}{clean_pin}"

    key_bytes = bytes.fromhex(pvk_hex.strip().ljust(32, "0")[:32])
    h = hmac.new(key_bytes, data_str.encode("utf-8"), hashlib.sha256).hexdigest().upper()

    decimalized = decimalize_hex(h)
    return decimalized[:4]


def verify_pvv(
    pan: str,
    pin: str,
    pvki: int,
    expected_pvv: str,
    pvk_hex: str = DEFAULT_PVK,
) -> bool:
    """Verify customer PIN input against stored PVV."""
    calculated = generate_pvv(pan, pin, pvki, pvk_hex)
    return hmac.compare_digest(calculated, expected_pvv.strip())
