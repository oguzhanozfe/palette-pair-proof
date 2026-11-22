import unittest
from project import analyze, luminance, ratio


class PaletteTests(unittest.TestCase):
    def test_black_white(self):
        self.assertAlmostEqual(ratio(luminance("#000000"),luminance("#ffffff")),21)

    def test_real_alternative(self):
        r=analyze({"palette":{"ink":"#000000","light":"#eeeeee","paper":"#ffffff"},"pairs":[{"label":"label","foreground":"light","background":"paper"}]})
        self.assertEqual(r["rows"][0]["Try foreground"],"ink")

    def test_bad_hex(self):
        with self.assertRaises(ValueError):
            luminance("#xyz")
