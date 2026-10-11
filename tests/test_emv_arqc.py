"""Unit tests for EMV Application Cryptograms (ARQC & ARPC)."""

import unittest
from vault_hsm_signer.emv_arqc import generate_arqc, generate_arpc, derive_emv_session_key


class TestEMVARQC(unittest.TestCase):
    def test_session_key_derivation(self):
        mk = "0102030405060708090A0B0C0D0E0F10"
        sk1 = derive_emv_session_key(mk, 1)
        sk2 = derive_emv_session_key(mk, 2)
        self.assertEqual(len(sk1), 16)
        # Different ATCs produce different session keys
        self.assertNotEqual(sk1, sk2)

    def test_generate_arqc_and_arpc(self):
        arqc = generate_arqc(amount_cents=5000, atc=1, unpredictable_number_hex="A1B2C3D4")
        self.assertEqual(len(arqc), 16)

        arpc = generate_arpc(arqc, arc="00", atc=1)
        self.assertEqual(len(arpc), 8)


if __name__ == "__main__":
    unittest.main()
