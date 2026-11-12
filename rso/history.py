"""Rundenhistorie fuer das Overlay (Qt-frei, getestet).

Der Agent sendet nur Momentaufnahmen; das Overlay haelt sich die
letzten Runden selbst (neueste zuerst). erkannt wird ein Rundenwechsel
am Anstieg von lap_nr zusammen mit lap_last_s.
"""
from __future__ import annotations

MAX_LAPS = 5


class LapHistory:
    """Rundenliste aus Zustands-Dicts (rso.state.build_state) aufbauen."""

    def __init__(self, max_laps: int = MAX_LAPS):
        self.max_laps = max_laps
        self.laps: list[dict] = []
        self._last_nr = None

    def feed(self, state: dict) -> list[dict]:
        """Neuen Zustand einspeisen; liefert die aktuelle Rundenliste."""
        if not state:
            self.laps = []
            self._last_nr = None
            return self.laps
        nr = state.get("lap_nr")
        last = state.get("lap_last_s")
        if nr is None:
            return self.laps
        if self._last_nr is not None and nr < self._last_nr:
            # Sitzungswechsel: Rundenzzaehler faellt zurueck -> Liste leeren
            self.laps = []
        if self._last_nr is not None and nr > self._last_nr and last:
            eintrag = {
                "nr": self._last_nr,
                "time_s": last,
                "valid": bool(state.get("lap_last_valid")),
                "sectors": list(state.get("sector_last") or []),
                "fuel_l": state.get("fuel_left_l"),
                "best_s": state.get("lap_best_s"),
            }
            if not self.laps or self.laps[0]["nr"] != eintrag["nr"]:
                self.laps.insert(0, eintrag)
                self.laps = self.laps[: self.max_laps]
        elif self.laps and last and self.laps[0]["nr"] == nr - 1 \
                and not self.laps[0].get("time_s"):
            # Nachtrag: Zeit der vorherigen Runde kam erst einen Tick spaeter
            self.laps[0]["time_s"] = last
            self.laps[0]["valid"] = bool(state.get("lap_last_valid"))
            self.laps[0]["sectors"] = list(state.get("sector_last") or [])
        self._last_nr = nr
        return self.laps

    def reset(self):
        self.laps = []
        self._last_nr = None


# --------------------------------------------------------------------------- --
# Selbsttest
# --------------------------------------------------------------------------- --
def _lap(nr, last, valid=True, best=None, sectors=(28.0, 31.0, 33.0), fuel=20.0):
    return {"lap_nr": nr, "lap_last_s": last, "lap_last_valid": valid,
            "lap_best_s": best, "sector_last": list(sectors), "fuel_left_l": fuel}


def _selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  FEHLER: {name}")

    h = LapHistory()
    h.feed(_lap(5, 100.0))
    check("Noch keine Runde", h.laps == [])
    h.feed(_lap(6, 99.0, valid=False))
    check("Runde 5 aufgenommen", len(h.laps) == 1 and h.laps[0]["nr"] == 5)
    check("Zeit der Runde 5", abs(h.laps[0]["time_s"] - 99.0) < 1e-9)
    check("Ungueltig", h.laps[0]["valid"] is False)
    h.feed(_lap(7, 98.0))
    check("Neueste zuerst", len(h.laps) == 2 and h.laps[0]["nr"] == 6)
    for n in range(8, 20):
        h.feed(_lap(n, 95.0))
    check("Deckel 5", len(h.laps) == 5 and h.laps[0]["nr"] == 18)
    # Sitzungswechsel: lap_nr faellt zurueck -> Liste wird geleert
    h.feed(_lap(1, None))
    check("Leerung bei Sitzungswechsel", h.laps == [] and h._last_nr == 1)
    h.feed(_lap(2, 90.0))
    check("Neue Sitzung aufgenommen", len(h.laps) == 1 and h.laps[0]["nr"] == 1)
    # Reset
    h.reset()
    check("Reset", h.laps == [] and h._last_nr is None)
    print("history-Selbsttest:", "OK" if ok else "FEHLER")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
