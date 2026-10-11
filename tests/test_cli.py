"""Unit tests for the bankhsm CLI."""

import unittest
from vault_hsm_signer.cli import main


class TestCLI(unittest.TestCase):
    def test_cli_commands(self):
        # 1. Luhn
        ret_luhn = main(["luhn", "4000001234567899"])
        self.assertEqual(ret_luhn, 0)

        # 2. PIN block create
        ret_pb_create = main(["pinblock", "create", "--pin", "1234", "--pan", "4000123456789010", "--format", "0"])
        self.assertEqual(ret_pb_create, 0)

        # 3. CVV generate & verify
        ret_cvv_gen = main(["cvv", "generate", "--pan", "4000123456789010", "--exp", "2812", "--service", "101"])
        self.assertEqual(ret_cvv_gen, 0)

        # 4. PVV generate & verify
        ret_pvv_gen = main(["pvv", "generate", "--pan", "4000123456789010", "--pin", "1234", "--pvki", "1"])
        self.assertEqual(ret_pvv_gen, 0)

        # 5. ARQC simulate
        ret_arqc = main(["arqc", "--amount", "25.00", "--atc", "1"])
        self.assertEqual(ret_arqc, 0)


if __name__ == "__main__":
    unittest.main()
