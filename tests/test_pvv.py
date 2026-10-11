"""Unit tests for Visa PIN Verification Value (PVV)."""

import unittest
from vault_hsm_signer.pvv_engine import generate_pvv, verify_pvv


class TestPVV(unittest.TestCase):
    def test_generate_and_verify_pvv(self):
        pan = "4000123456789010"
        pin = "4321"
        pvki = 1

        pvv = generate_pvv(pan, pin, pvki)
        self.assertEqual(len(pvv), 4)
        self.assertTrue(pvv.isdigit())

        # Correct PIN verifies
        self.assertTrue(verify_pvv(pan, pin, pvki, pvv))

        # Wrong PIN fails
        self.assertFalse(verify_pvv(pan, "9999", pvki, pvv))

        # Wrong PVKI fails
        self.assertFalse(verify_pvv(pan, pin, 2, pvv))


if __name__ == "__main__":
    unittest.main()
