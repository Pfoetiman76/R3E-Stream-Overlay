"""Testsuite: R3E-Stream-Overlay (Qt-frei)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rso import APP_VERSION  # noqa: E402


def suite():
    from tests import (test_protocol, test_format, test_state,
                       test_history, test_agent, test_raceroom_sm)
    s = unittest.TestSuite()
    for mod in (test_protocol, test_format, test_state, test_history,
                test_agent, test_raceroom_sm):
        s.addTests(unittest.defaultTestLoader.loadTestsFromModule(mod))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=1)
    ok = runner.run(suite()).wasSuccessful()
    print(f"APP_VERSION: {APP_VERSION}")
    sys.exit(0 if ok else 1)
