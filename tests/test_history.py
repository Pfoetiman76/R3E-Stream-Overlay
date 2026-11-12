import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rso.history import LapHistory  # noqa: E402


def lap(nr, last, valid=True, best=None, sectors=(28.0, 31.0, 33.0), fuel=20.0):
    return {"lap_nr": nr, "lap_last_s": last, "lap_last_valid": valid,
            "lap_best_s": best, "sector_last": list(sectors), "fuel_left_l": fuel}


class TestHistory(unittest.TestCase):
    def test_rundenaufnahme(self):
        h = LapHistory()
        h.feed(lap(5, 100.0))
        self.assertEqual([], h.laps)
        h.feed(lap(6, 99.0, valid=False))
        self.assertEqual(1, len(h.laps))
        self.assertEqual(5, h.laps[0]["nr"])
        self.assertAlmostEqual(99.0, h.laps[0]["time_s"])
        self.assertFalse(h.laps[0]["valid"])
        h.feed(lap(7, 98.0))
        self.assertEqual(6, h.laps[0]["nr"])

    def test_deckel(self):
        h = LapHistory()
        for n in range(2, 40):
            h.feed(lap(n, 95.0))
        self.assertEqual(5, len(h.laps))
        self.assertEqual(38, h.laps[0]["nr"])

    def test_sitzungswechsel(self):
        h = LapHistory()
        h.feed(lap(10, 90.0))
        h.feed(lap(11, 91.0))
        self.assertEqual(1, len(h.laps))
        h.feed(lap(1, None))
        self.assertEqual([], h.laps)
        self.assertEqual(1, h._last_nr)
        h.feed(lap(2, 88.0))
        self.assertEqual(1, len(h.laps))
        self.assertEqual(1, h.laps[0]["nr"])

    def test_keine_zeit(self):
        h = LapHistory()
        h.feed(lap(5, None))
        h.feed(lap(6, None))
        self.assertEqual([], h.laps)

    def test_reset(self):
        h = LapHistory()
        h.feed(lap(5, 100.0))
        h.feed(lap(6, 99.0))
        h.reset()
        self.assertEqual([], h.laps)
        self.assertIsNone(h._last_nr)


if __name__ == "__main__":
    unittest.main()
