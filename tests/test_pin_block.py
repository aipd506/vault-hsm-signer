"""Unit tests for ISO 9564 PIN blocks (Format 0, 1, 3)."""

import unittest
from vault_hsm_signer.pin_block import (
    create_pin_block_format_0,
    extract_pin_format_0,
    create_pin_block_format_1,
    extract_pin_format_1,
    create_pin_block_format_3,
    extract_pin_format_3,
)

PAN = "4000123456789010"
PIN_4 = "1234"
PIN_6 = "987654"


class TestPINBlock(unittest.TestCase):
    def test_format_0_roundtrip(self):
        block = create_pin_block_format_0(PIN_4, PAN)
        self.assertEqual(len(block), 16)
        extracted = extract_pin_format_0(block, PAN)
        self.assertEqual(extracted, PIN_4)

        # Test 6-digit PIN
        block6 = create_pin_block_format_0(PIN_6, PAN)
        extracted6 = extract_pin_format_0(block6, PAN)
        self.assertEqual(extracted6, PIN_6)

    def test_format_1_roundtrip(self):
        block = create_pin_block_format_1(PIN_4)
        self.assertEqual(len(block), 16)
        extracted = extract_pin_format_1(block)
        self.assertEqual(extracted, PIN_4)

    def test_format_3_roundtrip(self):
        block = create_pin_block_format_3(PIN_4, PAN)
        self.assertEqual(len(block), 16)
        extracted = extract_pin_format_3(block, PAN)
        self.assertEqual(extracted, PIN_4)

    def test_wrong_pan_fails_format_0_extraction(self):
        block = create_pin_block_format_0(PIN_4, PAN)
        wrong_pan = "4000999999999010"
        with self.assertRaises(ValueError):
            extract_pin_format_0(block, wrong_pan)


if __name__ == "__main__":
    unittest.main()
