"""Unit tests for CVV/CVC derivation and decimalization."""

import unittest
from vault_hsm_signer.cvv_engine import generate_cvv, verify_cvv, decimalize_hex


class TestCVV(unittest.TestCase):
    def test_decimalization_table(self):
        # 12AB -> 1, 2, A->0, B->1 -> 1201
        self.assertEqual(decimalize_hex("12AB"), "1201")
        # 9F3C -> 9, 3, F->5, C->2 -> 9352
        self.assertEqual(decimalize_hex("9F3C"), "9352")

    def test_generate_and_verify_cvv(self):
        pan = "4000123456789010"
        exp = "2812"
        srv = "101"

        cvv = generate_cvv(pan, exp, srv)
        self.assertEqual(len(cvv), 3)
        self.assertTrue(cvv.isdigit())

        # Verification succeeds
        self.assertTrue(verify_cvv(pan, exp, srv, cvv))

        # Corrupted CVV fails
        wrong_cvv = "999" if cvv != "999" else "000"
        self.assertFalse(verify_cvv(pan, exp, srv, wrong_cvv))

        # Tampered expiration fails
        self.assertFalse(verify_cvv(pan, "2912", srv, cvv))


if __name__ == "__main__":
    unittest.main()
