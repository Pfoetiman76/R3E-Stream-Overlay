import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rso.state import build_state  # noqa: E402


def sample(**kw):
    base = dict(
        track_name="Nuerburgring", layout_name="Grand Prix", session_type="Practice",
        player_name="Marcel", completed_laps=6, lap_time_current_s=98.4,
        lap_time_previous_s=99.102, prev_lap_valid=0, lap_time_best_s=97.845,
        delta_best_s=-0.213, fuel_left=18.4, fuel_capacity=60.0, fuel_per_lap=3.1,
        place=3, place_class=3, num_cars=14, session_time_remaining=1800.0,
        sector_current=[28.4, 31.1, None], sector_previous=[28.8, 31.4, 33.7],
        sector_best=[28.2, 31.0, 33.6], speed=214.0,
    )
    base.update(kw)
    return SimpleNamespace(**base)


class TestState(unittest.TestCase):
    def test_vollstaendig(self):
        st = build_state(sample())
        self.assertEqual(7, st["lap_nr"])
        self.assertAlmostEqual(99.102, st["lap_last_s"])
        self.assertFalse(st["lap_last_valid"])
        self.assertEqual(97.845, st["lap_best_s"])
        self.assertEqual(-0.213, st["delta_best_s"])
        self.assertEqual(5, st["fuel_laps_left"])
        self.assertEqual(3, st["place"])
        self.assertEqual(14, st["num_cars"])
        self.assertEqual([28.4, 31.1, None], st["sector_cur"])
        self.assertEqual(1800.0, st["session_time_left_s"])

    def test_leere_werte(self):
        st = build_state(sample(completed_laps=0, lap_time_previous_s=0.0,
                                prev_lap_valid=1, lap_time_best_s=None,
                                delta_best_s=0.0, fuel_left=0.0, fuel_per_lap=0.0,
                                place=0, num_cars=0, session_time_remaining=0.0))
        self.assertEqual(1, st["lap_nr"])
        self.assertIsNone(st["lap_last_s"])
        self.assertTrue(st["lap_last_valid"])
        self.assertIsNone(st["lap_best_s"])
        self.assertIsNone(st["fuel_laps_left"])
        self.assertIsNone(st["place"])
        self.assertEqual(0, st["num_cars"])


if __name__ == "__main__":
    unittest.main()
