import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rso.format import (delta_class, fmt_delta, fmt_fuel, fmt_lap,  # noqa: E402
                        fmt_sector, fmt_session_time, fuel_laps_left)


class TestFormat(unittest.TestCase):
    def test_lap(self):
        self.assertEqual("1:37.845", fmt_lap(97.845))
        self.assertEqual("1:05.400", fmt_lap(65.4))
        self.assertEqual("0:59.999", fmt_lap(59.999))
        self.assertEqual("--.---", fmt_lap(None))
        self.assertEqual("--.---", fmt_lap(0))

    def test_sector(self):
        self.assertEqual("28.412", fmt_sector(28.412))
        self.assertEqual("--.---", fmt_sector(None))

    def test_delta(self):
        self.assertEqual("-0.213", fmt_delta(-0.213))
        self.assertEqual("+0.400", fmt_delta(0.4))
        self.assertEqual("--.---", fmt_delta(None))
        self.assertEqual("--.---", fmt_delta(0))

    def test_delta_class(self):
        self.assertEqual("pos", delta_class(-0.1))
        self.assertEqual("neg", delta_class(0.1))
        self.assertEqual("none", delta_class(None))

    def test_fuel(self):
        self.assertEqual("18.4 l", fmt_fuel(18.4))
        self.assertEqual("-- l", fmt_fuel(None))

    def test_fuel_laps(self):
        self.assertEqual(5, fuel_laps_left(18.4, 3.1))
        self.assertIsNone(fuel_laps_left(None, 3.1))
        self.assertIsNone(fuel_laps_left(18.0, 0.0))

    def test_session_time(self):
        self.assertEqual("1:02:05", fmt_session_time(3725))
        self.assertEqual("01:05", fmt_session_time(65))
        self.assertEqual("--:--", fmt_session_time(None))


if __name__ == "__main__":
    unittest.main()
