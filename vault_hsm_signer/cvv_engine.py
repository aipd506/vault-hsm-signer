"""Card Verification Value (CVV / CVC / CVV2) derivation and verification engine."""

import hashlib
import hmac
from typing import Tuple

DEFAULT_CVK = "0123456789ABCDEFFEDCBA9876543210"


def decimalize_hex(hex_str: str) -> str:
    """Standard banking decimalization table: extract 0-9 first, then map A-F to 0-5."""
    clean = hex_str.strip().upper()
    digits = []

    # First pass: collect existing 0-9 digits
    for ch in clean:
        if ch.isdigit():
            digits.append(ch)

    # Second pass: convert A-F to 0-5
    for ch in clean:
        if ch in "ABCDEF":
            mapped_digit = str(ord(ch) - ord("A"))
            digits.append(mapped_digit)

    return "".join(digits)


def generate_cvv(
    pan: str,
    expiration_yymm: str,
    service_code: str,
    cvk_hex: str = DEFAULT_CVK,
) -> str:
    """Generate 3-digit Card Verification Value (CVV / CVC / CVV2)."""
    clean_pan = pan.strip().replace(" ", "").replace("-", "")
    clean_exp = expiration_yymm.strip()
    clean_srv = service_code.strip()

    if len(clean_exp) != 4 or not clean_exp.isdigit():
        raise ValueError(f"Expiration date must be 4 digits YYMM, got '{expiration_yymm}'")
    if len(clean_srv) != 3 or not clean_srv.isdigit():
        raise ValueError(f"Service code must be 3 digits, got '{service_code}'")

    # Data block: PAN + Expiration + Service Code
    data_str = f"{clean_pan}{clean_exp}{clean_srv}"
    key_bytes = bytes.fromhex(cvk_hex.strip().ljust(32, "0")[:32])

    # Compute keyed HMAC hash
    h = hmac.new(key_bytes, data_str.encode("utf-8"), hashlib.sha256).hexdigest().upper()

    # Decimalize and take first 3 digits
    decimalized = decimalize_hex(h)
    return decimalized[:3]


def verify_cvv(
    pan: str,
    expiration_yymm: str,
    service_code: str,
    cvv: str,
    cvk_hex: str = DEFAULT_CVK,
) -> bool:
    """Verify customer CVV input against derived value."""
    expected = generate_cvv(pan, expiration_yymm, service_code, cvk_hex)
    return hmac.compare_digest(expected, cvv.strip())
