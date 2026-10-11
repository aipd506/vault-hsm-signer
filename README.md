# vault-hsm-signer

Software-defined payment Hardware Security Module (HSM) simulator for payment card issuing, acquiring, POS terminal verification, and EMV chip authorization.

Simulates financial cryptography operations typically executed inside specialized banking security hardware (e.g. Thales payShield, Atalla, SafeNet HSMs) with zero external runtime dependencies.

## Key Capabilities

1. ISO 9564 PIN Block Engine:
   - Format 0 (ANSI X9.8): Standard PIN block with PAN XOR masking and trailing `F` padding integrity checks.
   - Format 1: Random padded PIN block for transactions where PAN is not available.
   - Format 3: Enhanced PIN block with random hexadecimal filler and PAN XOR.
   - Clean extraction and length verification.
2. Luhn Algorithm MOD-10 (ISO/IEC 7812):
   - Validates Primary Account Number (PAN) parity check digits.
   - Calculates missing check digits for new card issuance.
   - Detects card brands: Visa, Mastercard, American Express, Discover, JCB.
3. Card Verification Value (CVV / CVC / CVV2) Engine:
   - Derives 3-digit verification values from PAN, Expiration Date (YYMM), and Service Code.
   - Implements the standard banking Decimalization Table (extracting 0-9 and mapping A-F to 0-5).
   - Validates CVV inputs with constant-time cryptographic comparison (`hmac.compare_digest`).
4. Visa PIN Verification Value (PVV):
   - Computes 4-digit PVV using rightmost 11 digits of PAN, PVKI (1-6), and clear PIN.
   - Verifies customer PIN entries against stored reference PVV.
5. EMV Chip & Contactless Cryptogram Simulator:
   - Session key diversification from Card Master Key (MK_AC) and Application Transaction Counter (ATC).
   - Generates 8-byte (16-hex) Application Request Cryptograms (ARQC).
   - Generates 4-byte Authorization Response Cryptograms (ARPC).
6. Zero External Dependencies: Built entirely in pure Python standard library (`hashlib`, `hmac`, `secrets`, `binascii`, `argparse`).

## Installation

```bash
pip install vault-hsm-signer
```

Or install locally in editable mode:

```bash
git clone https://github.com/aipd506/vault-hsm-signer.git
cd vault-hsm-signer
pip install -e .
```

## Quick Start

### 1. Validate Card Number (Luhn MOD-10)

```bash
bankhsm luhn 4000001234567899
```

Output:
```text
PAN:      4000001234567899
Network:  Visa
Checksum: VALID
```

### 2. Create ISO 9564 Format 0 PIN Block

```bash
bankhsm pinblock create --pin 1234 --pan 4000123456789010 --format 0
```

Output:
```text
ISO 9564 PIN Block (Format 0): 041235DCBA9876FE
```

### 3. Extract Clear PIN from Format 0 Block

```bash
bankhsm pinblock extract --block 041235DCBA9876FE --pan 4000123456789010 --format 0
```

Output:
```text
Extracted PIN: 1234
```

### 4. Generate & Verify Card Verification Value (CVV)

```bash
# Generate
bankhsm cvv generate --pan 4000123456789010 --exp 2812 --service 101

# Verify
bankhsm cvv verify --pan 4000123456789010 --exp 2812 --service 101 --cvv 150
```

Output:
```text
CVV Verification: VERIFIED
```

### 5. Generate & Verify Visa PVV

```bash
bankhsm pvv generate --pan 4000123456789010 --pin 1234 --pvki 1
```

Output:
```text
Generated Visa PVV: 0237 (PVKI: 1)
```

### 6. Simulate EMV Chip Cryptogram (ARQC & ARPC)

```bash
bankhsm arqc --amount 75.00 --atc 14
```

Output:
```text
============================================================
EMV CHIP TRANSACTION CRYPTOGRAM
============================================================
Transaction Amount:  $75.00
Counter (ATC):       14
Generated ARQC:      4B81A7D1C2E9F034
Host Response ARPC:  8C0F2A11 (ARC: 00 Approved)
============================================================
```

## Python API Usage

```python
from vault_hsm_signer import (
    validate_luhn,
    create_pin_block_format_0,
    extract_pin_format_0,
    generate_cvv,
    verify_cvv,
)

# Luhn check
assert validate_luhn("4000001234567899")

# PIN Block
pan = "4000123456789010"
pin_block = create_pin_block_format_0("1234", pan)
clear_pin = extract_pin_format_0(pin_block, pan)
assert clear_pin == "1234"

# CVV
cvv = generate_cvv(pan, "2812", "101")
assert verify_cvv(pan, "2812", "101", cvv)
```

## License

Apache-2.0
