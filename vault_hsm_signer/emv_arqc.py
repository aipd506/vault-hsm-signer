"""EMV Book 2 / Book 3 Application Cryptogram (ARQC & ARPC) simulation engine."""

import hashlib
import hmac
import secrets
from typing import Tuple

DEFAULT_MK_AC = "0102030405060708090A0B0C0D0E0F10"


def derive_emv_session_key(master_key_hex: str, atc: int) -> bytes:
    """Derive 16-byte session key from Master Cryptogram Key (MK_AC) and Application Transaction Counter (ATC)."""
    mk_bytes = bytes.fromhex(master_key_hex.strip().ljust(32, "0")[:32])
    atc_bytes = atc.to_bytes(2, "big")
    diversifier = atc_bytes + b"\xF0" + atc_bytes + b"\x0F"
    return hmac.new(mk_bytes, diversifier, hashlib.sha256).digest()[:16]


def generate_arqc(
    amount_cents: int,
    atc: int,
    unpredictable_number_hex: str = "",
    currency_code: int = 840,  # USD
    transaction_date_yymmdd: str = "261011",
    master_key_hex: str = DEFAULT_MK_AC,
) -> str:
    """Generate 8-byte (16-hex) EMV Application Request Cryptogram (ARQC)."""
    # Generate 4-byte unpredictable number if not provided
    un_hex = unpredictable_number_hex or secrets.token_hex(4).upper()
    un_bytes = bytes.fromhex(un_hex.strip()[:8].ljust(8, "0"))

    # Pack transaction data elements
    amt_bytes = amount_cents.to_bytes(6, "big")
    amt_other = (0).to_bytes(6, "big")
    country_code = (840).to_bytes(2, "big")
    tvr = bytes.fromhex("0000000000")  # Terminal Verification Results (5 bytes)
    cur_bytes = currency_code.to_bytes(2, "big")
    date_bytes = bytes.fromhex(transaction_date_yymmdd.strip()[:6].ljust(6, "0"))
    tx_type = b"\x00"  # 00 = Purchase
    atc_bytes = atc.to_bytes(2, "big")

    payload = (
        amt_bytes
        + amt_other
        + country_code
        + tvr
        + cur_bytes
        + date_bytes
        + tx_type
        + un_bytes
        + atc_bytes
    )

    session_key = derive_emv_session_key(master_key_hex, atc)
    arqc_full = hmac.new(session_key, payload, hashlib.sha256).digest()

    # EMV cryptogram is 8 bytes (16 hex chars)
    return arqc_full[:8].hex().upper()


def generate_arpc(
    arqc_hex: str,
    arc: str = "00",
    master_key_hex: str = DEFAULT_MK_AC,
    atc: int = 1,
) -> str:
    """Generate 4-byte (8-hex) EMV Authorization Response Cryptogram (ARPC)."""
    arqc_bytes = bytes.fromhex(arqc_hex.strip()[:16].ljust(16, "0"))
    arc_bytes = arc.encode("ascii")[:2].ljust(2, b" ")

    session_key = derive_emv_session_key(master_key_hex, atc)
    payload = arqc_bytes + arc_bytes
    arpc_full = hmac.new(session_key, payload, hashlib.sha256).digest()

    return arpc_full[:4].hex().upper()
