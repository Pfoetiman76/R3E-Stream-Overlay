import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.agent import Agent, IDLE_HZ  # noqa: E402
from rso.protocol import decode_state  # noqa: E402


class FakeSock:
    def __init__(self):
        self.pakete = []

    def sendto(self, data, addr):
        self.pakete.append((bytes(data), addr))
        return len(data)


def sample():
    return SimpleNamespace(
        track_name="Spa", layout_name="GP", session_type="Race",
        player_name="Marcel", completed_laps=2, lap_time_current_s=100.0,
        lap_time_previous_s=99.0, prev_lap_valid=1, lap_time_best_s=98.0,
        delta_best_s=-1.0, fuel_left=40.0, fuel_capacity=60.0, fuel_per_lap=4.0,
        place=1, place_class=1, num_cars=20, session_time_remaining=600.0,
        sector_current=[30.0, None, None], sector_previous=[30.0, 33.0, 36.0],
        sector_best=[29.0, 32.0, 35.0], speed=200.0,
    )


class FakeReader:
    def __init__(self, sample_obj=None, error=None):
        self.sample_obj = sample_obj
        self.error = error

    def read(self):
        if self.error:
            raise RuntimeError(self.error)
        return self.sample_obj


class TestAgent(unittest.TestCase):
    def test_sendet_state(self):
        sock = FakeSock()
        a = Agent(FakeReader(sample()), sock, ("1.2.3.4", 5000), 10.0)
        self.assertTrue(a.tick(now=100.0))
        ok, state = decode_state(sock.pakete[0][0])
        self.assertTrue(ok)
        self.assertEqual("Spa", state["track"])
        self.assertEqual(3, state["lap_nr"])

    def test_takt_10hz(self):
        sock = FakeSock()
        a = Agent(FakeReader(sample()), sock, ("1.2.3.4", 5000), 10.0)
        a.tick(now=100.0)
        self.assertFalse(a.tick(now=100.05))   # 0.05 s < 0.1 s
        self.assertTrue(a.tick(now=100.15))

    def test_idle_sitzt(self):
        sock = FakeSock()
        a = Agent(FakeReader(None), sock, ("1.2.3.4", 5000), 10.0)
        a.tick(now=100.0)
        self.assertFalse(a.tick(now=100.2))    # Idle: nur 1 Hz
        ok, state = decode_state(sock.pakete[0][0])
        self.assertTrue(ok)
        self.assertIsNone(state)

    def test_fehler_wie_idle(self):
        sock = FakeSock()
        a = Agent(FakeReader(error="kein Spiel"), sock, ("1.2.3.4", 5000))
        a.tick(now=100.0)
        ok, state = decode_state(sock.pakete[0][0])
        self.assertTrue(ok)
        self.assertIsNone(state)
        self.assertIn("kein Spiel", a.last_error)
        self.assertFalse(a.tick(now=100.2))   # Idle-Takt nach Fehler

    def test_adresse(self):
        sock = FakeSock()
        a = Agent(FakeReader(sample()), sock, ("255.255.255.255", 53197))
        a.tick(now=100.0)
        self.assertEqual(("255.255.255.255", 53197), sock.pakete[0][1])


if __name__ == "__main__":
    unittest.main()
