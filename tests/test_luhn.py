"""Unit tests for Luhn MOD-10 algorithm and PAN detection."""

import unittest
from vault_hsm_signer.luhn import (
    validate_luhn,
    calculate_luhn_check_digit,
    detect_card_network,
    generate_valid_pan,
)


class TestLuhn(unittest.TestCase):
    def test_known_valid_pans(self):
        # Visa test number
        self.assertTrue(validate_luhn("4000001234567899"))
        # Mastercard test number
        self.assertTrue(validate_luhn("5105105105105100"))
        # Amex test number
        self.assertTrue(validate_luhn("378282246310005"))

    def test_corrupted_pan_fails(self):
        # 4000001234567899 -> change last digit to 8
        self.assertFalse(validate_luhn("4000001234567898"))

    def test_calculate_check_digit(self):
        partial = "400000123456789"
        chk = calculate_luhn_check_digit(partial)
        self.assertEqual(chk, "9")
        self.assertTrue(validate_luhn(partial + chk))

    def test_detect_card_network(self):
        self.assertEqual(detect_card_network("4111111111111111"), "Visa")
        self.assertEqual(detect_card_network("5500000000000004"), "Mastercard")
        self.assertEqual(detect_card_network("370000000000004"), "American Express")

    def test_generate_valid_pans(self):
        for net in ["Visa", "Mastercard", "Amex"]:
            pan = generate_valid_pan(net)
            self.assertTrue(validate_luhn(pan), f"Generated PAN {pan} failed Luhn for {net}")


if __name__ == "__main__":
    unittest.main()
