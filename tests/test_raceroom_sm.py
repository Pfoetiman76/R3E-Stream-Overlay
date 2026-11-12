import ctypes
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rso import APP_VERSION  # noqa: E402
from rso.raceroom_sm import R3E_VERSION_MAJOR, R3EReader, R3EShared  # noqa: E402


class TestReaderErweiterung(unittest.TestCase):
    """Position/Fahrzeugzahl/Sitzungszeit: die Overlay-Erweiterungen."""

    def test_platz_und_feldgroesse(self):
        d = R3EShared()
        d.version_major, d.version_minor = 3, 5
        d.game_in_menus = d.game_in_replay = 0
        d.position = 3
        d.position_class = 3
        d.num_cars = 14
        d.session_time_remaining = 1800.0
        s = R3EReader(raw_provider=lambda: bytes(d)).read()
        self.assertEqual(3, s.place)
        self.assertEqual(3, s.place_class)
        self.assertEqual(14, s.num_cars)
        self.assertAlmostEqual(1800.0, s.session_time_remaining)

    def test_platz_null_als_none(self):
        d = R3EShared()
        d.version_major, d.version_minor = 3, 5
        d.game_in_menus = d.game_in_replay = 0
        d.position = 0
        d.num_cars = 0
        s = R3EReader(raw_provider=lambda: bytes(d)).read()
        self.assertIsNone(s.place)
        self.assertEqual(0, s.num_cars)

    def test_sitzungszeit_null_als_none(self):
        d = R3EShared()
        d.version_major, d.version_minor = 3, 5
        d.game_in_menus = d.game_in_replay = 0
        s = R3EReader(raw_provider=lambda: bytes(d)).read()
        self.assertIsNone(s.session_time_remaining)


if __name__ == "__main__":
    unittest.main()
