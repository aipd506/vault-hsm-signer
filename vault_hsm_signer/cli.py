"""Command-line interface for vault-hsm-signer."""

import argparse
import sys
from .luhn import validate_luhn, detect_card_network, calculate_luhn_check_digit
from .pin_block import (
    create_pin_block_format_0,
    extract_pin_format_0,
    create_pin_block_format_1,
    extract_pin_format_1,
    create_pin_block_format_3,
    extract_pin_format_3,
)
from .cvv_engine import generate_cvv, verify_cvv
from .pvv_engine import generate_pvv, verify_pvv
from .emv_arqc import generate_arqc, generate_arpc


def cmd_luhn(args) -> int:
    pan = args.pan.strip().replace(" ", "").replace("-", "")
    is_valid = validate_luhn(pan)
    network = detect_card_network(pan)

    status = "VALID" if is_valid else "INVALID"
    print(f"PAN:      {pan}")
    print(f"Network:  {network}")
    print(f"Checksum: {status}")

    if not is_valid and len(pan) >= 12:
        expected = calculate_luhn_check_digit(pan[:-1])
        print(f"Expected check digit was '{expected}', found '{pan[-1]}'")

    return 0 if is_valid else 1


def cmd_pinblock_create(args) -> int:
    fmt = args.format
    pin = args.pin.strip()
    pan = args.pan.strip().replace(" ", "").replace("-", "") if args.pan else ""

    try:
        if fmt == 0:
            if not pan:
                sys.stderr.write("Error: Format 0 requires --pan\n")
                return 1
            block = create_pin_block_format_0(pin, pan)
        elif fmt == 1:
            block = create_pin_block_format_1(pin)
        elif fmt == 3:
            if not pan:
                sys.stderr.write("Error: Format 3 requires --pan\n")
                return 1
            block = create_pin_block_format_3(pin, pan)
        else:
            sys.stderr.write(f"Error: Unsupported format {fmt}\n")
            return 1

        print(f"ISO 9564 PIN Block (Format {fmt}): {block}")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def cmd_pinblock_extract(args) -> int:
    fmt = args.format
    block = args.block.strip().upper()
    pan = args.pan.strip().replace(" ", "").replace("-", "") if args.pan else ""

    try:
        if fmt == 0:
            if not pan:
                sys.stderr.write("Error: Format 0 requires --pan\n")
                return 1
            pin = extract_pin_format_0(block, pan)
        elif fmt == 1:
            pin = extract_pin_format_1(block)
        elif fmt == 3:
            if not pan:
                sys.stderr.write("Error: Format 3 requires --pan\n")
                return 1
            pin = extract_pin_format_3(block, pan)
        else:
            sys.stderr.write(f"Error: Unsupported format {fmt}\n")
            return 1

        print(f"Extracted PIN: {pin}")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error extracting PIN: {e}\n")
        return 1


def cmd_cvv_generate(args) -> int:
    try:
        cvv = generate_cvv(args.pan, args.exp, args.service)
        print(f"Generated CVV: {cvv}")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def cmd_cvv_verify(args) -> int:
    valid = verify_cvv(args.pan, args.exp, args.service, args.cvv)
    status = "VERIFIED" if valid else "FAILED"
    print(f"CVV Verification: {status}")
    return 0 if valid else 1


def cmd_pvv_generate(args) -> int:
    try:
        pvv = generate_pvv(args.pan, args.pin, args.pvki)
        print(f"Generated Visa PVV: {pvv} (PVKI: {args.pvki})")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


def cmd_pvv_verify(args) -> int:
    valid = verify_pvv(args.pan, args.pin, args.pvki, args.pvv)
    status = "VERIFIED" if valid else "FAILED"
    print(f"PVV Verification: {status}")
    return 0 if valid else 1


def cmd_arqc(args) -> int:
    amount_cents = int(args.amount * 100)
    atc = args.atc
    arqc = generate_arqc(amount_cents=amount_cents, atc=atc)
    arpc = generate_arpc(arqc, arc="00", atc=atc)

    print("=" * 60)
    print("EMV CHIP TRANSACTION CRYPTOGRAM")
    print("=" * 60)
    print(f"Transaction Amount:  ${args.amount:.2f}")
    print(f"Counter (ATC):       {atc}")
    print(f"Generated ARQC:      {arqc}")
    print(f"Host Response ARPC:  {arpc} (ARC: 00 Approved)")
    print("=" * 60)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="bankhsm",
        description="Software-defined payment Hardware Security Module (HSM) simulator for card issuing and acquiring",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # luhn
    p_luhn = subparsers.add_parser("luhn", help="Validate Primary Account Number (PAN) check digit")
    p_luhn.add_argument("pan", help="Card PAN digits")
    p_luhn.set_defaults(func=cmd_luhn)

    # pinblock
    p_pb = subparsers.add_parser("pinblock", help="Manage ISO 9564 PIN blocks")
    pb_sub = p_pb.add_subparsers(dest="pb_cmd", required=True)
    p_pb_create = pb_sub.add_parser("create", help="Create ISO 9564 PIN block")
    p_pb_create.add_argument("--pin", required=True, help="Clear PIN digits")
    p_pb_create.add_argument("--pan", help="Card PAN (required for Format 0 and 3)")
    p_pb_create.add_argument("--format", type=int, choices=[0, 1, 3], default=0, help="Format (default: 0)")
    p_pb_create.set_defaults(func=cmd_pinblock_create)

    p_pb_ext = pb_sub.add_parser("extract", help="Extract clear PIN from ISO 9564 PIN block")
    p_pb_ext.add_argument("--block", required=True, help="16-hex char PIN block")
    p_pb_ext.add_argument("--pan", help="Card PAN")
    p_pb_ext.add_argument("--format", type=int, choices=[0, 1, 3], default=0, help="Format (default: 0)")
    p_pb_ext.set_defaults(func=cmd_pinblock_extract)

    # cvv
    p_cvv = subparsers.add_parser("cvv", help="Derive or verify Card Verification Value (CVV)")
    cvv_sub = p_cvv.add_subparsers(dest="cvv_cmd", required=True)
    p_cvv_gen = cvv_sub.add_parser("generate", help="Generate CVV")
    p_cvv_gen.add_argument("--pan", required=True, help="Card PAN")
    p_cvv_gen.add_argument("--exp", required=True, help="Expiration date YYMM")
    p_cvv_gen.add_argument("--service", default="101", help="Service code (default: 101)")
    p_cvv_gen.set_defaults(func=cmd_cvv_generate)

    p_cvv_ver = cvv_sub.add_parser("verify", help="Verify CVV")
    p_cvv_ver.add_argument("--pan", required=True, help="Card PAN")
    p_cvv_ver.add_argument("--exp", required=True, help="Expiration date YYMM")
    p_cvv_ver.add_argument("--service", default="101", help="Service code (default: 101)")
    p_cvv_ver.add_argument("--cvv", required=True, help="CVV to verify")
    p_cvv_ver.set_defaults(func=cmd_cvv_verify)

    # pvv
    p_pvv = subparsers.add_parser("pvv", help="Derive or verify Visa PIN Verification Value (PVV)")
    pvv_sub = p_pvv.add_subparsers(dest="pvv_cmd", required=True)
    p_pvv_gen = pvv_sub.add_parser("generate", help="Generate PVV")
    p_pvv_gen.add_argument("--pan", required=True, help="Card PAN")
    p_pvv_gen.add_argument("--pin", required=True, help="Clear 4-digit PIN")
    p_pvv_gen.add_argument("--pvki", type=int, default=1, help="PVKI index (default: 1)")
    p_pvv_gen.set_defaults(func=cmd_pvv_generate)

    p_pvv_ver = pvv_sub.add_parser("verify", help="Verify PVV")
    p_pvv_ver.add_argument("--pan", required=True, help="Card PAN")
    p_pvv_ver.add_argument("--pin", required=True, help="Clear 4-digit PIN")
    p_pvv_ver.add_argument("--pvki", type=int, default=1, help="PVKI index (default: 1)")
    p_pvv_ver.add_argument("--pvv", required=True, help="Expected PVV")
    p_pvv_ver.set_defaults(func=cmd_pvv_verify)

    # arqc
    p_arqc = subparsers.add_parser("arqc", help="Simulate EMV Application Cryptogram (ARQC/ARPC)")
    p_arqc.add_argument("--amount", type=float, default=45.50, help="Amount in dollars")
    p_arqc.add_argument("--atc", type=int, default=1, help="Application Transaction Counter (ATC)")
    p_arqc.set_defaults(func=cmd_arqc)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
