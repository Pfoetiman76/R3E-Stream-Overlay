"""Zustandsaufbau: LiveSample -> Protokoll-Dict (Qt-frei, getestet).

build_state() ist die einzige Stelle, die entscheidet, welche Werte
der Agent ins Netzwerk sendet. Alle Zeiten in Sekunden, alle Werte
entweder plausibel oder None (Overlay zeigt '--').
"""
from __future__ import annotations

from .format import fuel_laps_left


def build_state(s) -> dict:
    """Aus einem LiveSample (raceroom_sm) ein kompaktes Overlay-Dict bauen."""
    return {
        # Kopf
        "track": s.track_name or "",
        "layout": s.layout_name or "",
        "session_type": s.session_type or "",
        "player": s.player_name or "",
        # Kacheln
        "lap_nr": max(0, int(s.completed_laps or 0)) + 1,
        "lap_current_s": s.lap_time_current_s or None,
        "lap_last_s": (s.lap_time_previous_s if (s.lap_time_previous_s or 0) > 0 else None),
        "lap_last_valid": bool(s.prev_lap_valid),
        "lap_best_s": s.lap_time_best_s,
        "delta_best_s": s.delta_best_s,
        "fuel_left_l": s.fuel_left or None,
        "fuel_capacity_l": s.fuel_capacity or None,
        "fuel_per_lap_l": s.fuel_per_lap or None,
        "fuel_laps_left": fuel_laps_left(s.fuel_left, s.fuel_per_lap),
        "place": (s.place if s.place else None),
        "place_class": (s.place_class if s.place_class else None),
        "num_cars": s.num_cars or 0,
        # Sektoren (3er-Listen, None = nicht gesetzt)
        "sector_cur": list(s.sector_current or []),
        "sector_last": list(s.sector_previous or []),
        "sector_best": list(s.sector_best or []),
        # Sitzung
        "session_time_left_s": s.session_time_remaining,
        "speed_kmh": s.speed or None,
    }


# --------------------------------------------------------------------------- --
# Selbsttest
# --------------------------------------------------------------------------- --
def _sample(**kw):
    from types import SimpleNamespace
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


def _selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  FEHLER: {name}")

    st = build_state(_sample())
    check("Rundennr = Runden+1", st["lap_nr"] == 7)
    check("Letzte Runde", abs(st["lap_last_s"] - 99.102) < 1e-9)
    check("Ungueltig-Flag", st["lap_last_valid"] is False)
    check("Bestzeit", st["lap_best_s"] == 97.845)
    check("Delta", st["delta_best_s"] == -0.213)
    check("Restrunden", st["fuel_laps_left"] == 5)
    check("Platz", st["place"] == 3 and st["num_cars"] == 14)
    check("Sektoren", st["sector_cur"][0] == 28.4 and st["sector_cur"][2] is None)
    # Runde 0, keine Bestzeit, keine Werte
    st2 = build_state(_sample(completed_laps=0, lap_time_previous_s=0.0,
                              prev_lap_valid=1, lap_time_best_s=None, delta_best_s=0.0,
                              fuel_left=0.0, fuel_per_lap=0.0, place=0, num_cars=0,
                              session_time_remaining=0.0))
    check("Runde 1", st2["lap_nr"] == 1)
    check("Keine letzte Runde", st2["lap_last_s"] is None)
    check("Gueltig-Flag", st2["lap_last_valid"] is True)
    check("Keine Bestzeit", st2["lap_best_s"] is None)
    check("Keine Restrunden", st2["fuel_laps_left"] is None)
    check("Kein Platz", st2["place"] is None)
    print("state-Selbsttest:", "OK" if ok else "FEHLER")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
