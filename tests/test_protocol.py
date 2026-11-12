import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from rso import APP_VERSION  # noqa: E402
from rso.protocol import decode_state, encode_idle, encode_state  # noqa: E402


class TestProtocol(unittest.TestCase):
    def test_version(self):
        self.assertEqual(0, APP_VERSION.count("\n"))

    def test_roundtrip(self):
        s = {"track": "Spa", "lap_best_s": 137.845, "sector_cur": [28.4, None, None]}
        ok, st = decode_state(encode_state(s))
        self.assertTrue(ok)
        self.assertEqual(s, st)

    def test_idle(self):
        ok, st = decode_state(encode_idle())
        self.assertTrue(ok)
        self.assertIsNone(st)

    def test_muell(self):
        self.assertFalse(decode_state(b"")[0])
        self.assertFalse(decode_state(b"{ kein json")[0])

    def test_falsche_magic(self):
        import json
        raw = json.dumps({"magic": "XXX", "v": 1, "state": {}}).encode()
        self.assertFalse(decode_state(raw)[0])

    def test_falsche_version(self):
        import json
        raw = json.dumps({"magic": "R3ESO", "v": 2, "state": {}}).encode()
        self.assertFalse(decode_state(raw)[0])

    def test_state_kein_dict(self):
        import json
        raw = json.dumps({"magic": "R3ESO", "v": 1, "state": [1, 2]}).encode()
        self.assertFalse(decode_state(raw)[0])

    def test_kompakt(self):
        s = {"track": "N" * 50, "layout": "L" * 50}
        self.assertLess(len(encode_state(s)), 300)


if __name__ == "__main__":
    unittest.main()
