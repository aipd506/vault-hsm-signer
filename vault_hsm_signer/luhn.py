"""ISO/IEC 7812 Luhn Algorithm MOD-10 verification and PAN generation."""

import random
from typing import Tuple


def validate_luhn(pan: str) -> bool:
    """Validate Primary Account Number (PAN) using the Luhn MOD-10 algorithm."""
    clean = pan.strip().replace(" ", "").replace("-", "")
    if len(clean) < 12 or not clean.isdigit():
        return False

    digits = [int(d) for d in clean]
    checksum = 0
    # Process from right to left
    reverse_digits = digits[::-1]

    for idx, d in enumerate(reverse_digits):
        if idx % 2 == 1:
            doubled = d * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += d

    return checksum % 10 == 0


def calculate_luhn_check_digit(partial_pan: str) -> str:
    """Calculate the check digit for a partial PAN (all digits except the last)."""
    clean = partial_pan.strip().replace(" ", "").replace("-", "")
    if not clean.isdigit():
        raise ValueError(f"Partial PAN must contain only digits, got '{partial_pan}'")

    # In calculation mode, the first digit to double from the right is the very last digit of partial_pan
    digits = [int(d) for d in clean]
    checksum = 0
    reverse_digits = digits[::-1]

    for idx, d in enumerate(reverse_digits):
        if idx % 2 == 0:  # Because the check digit at pos 0 is missing, pos 1 becomes pos 0
            doubled = d * 2
            checksum += (doubled - 9) if doubled > 9 else doubled
        else:
            checksum += d

    check_digit = (10 - (checksum % 10)) % 10
    return str(check_digit)


def detect_card_network(pan: str) -> str:
    """Detect payment card network from PAN prefix."""
    clean = pan.strip().replace(" ", "").replace("-", "")
    if clean.startswith("4"):
        return "Visa"
    elif clean.startswith(("51", "52", "53", "54", "55")) or (
        len(clean) >= 4 and 2221 <= int(clean[:4]) <= 2720
    ):
        return "Mastercard"
    elif clean.startswith(("34", "37")):
        return "American Express"
    elif clean.startswith(("6011", "65")) or (
        len(clean) >= 3 and 644 <= int(clean[:3]) <= 649
    ):
        return "Discover"
    elif clean.startswith(("3528", "3589")):
        return "JCB"
    return "Generic/Unknown"


def generate_valid_pan(network: str = "Visa") -> str:
    """Generate a mathematically valid synthetic PAN for testing."""
    net = network.capitalize()
    if net == "Visa":
        prefix = "4"
        length = 16
    elif net == "Mastercard":
        prefix = "52"
        length = 16
    elif net == "American express" or net == "Amex":
        prefix = "37"
        length = 15
    else:
        prefix = "4000"
        length = 16

    num_random_digits = length - len(prefix) - 1
    random_middle = "".join(str(random.randint(0, 9)) for _ in range(num_random_digits))
    partial = prefix + random_middle
    check_digit = calculate_luhn_check_digit(partial)
    return partial + check_digit
