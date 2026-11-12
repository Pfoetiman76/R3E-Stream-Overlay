"""Formatier-Helfer (Qt-frei, getestet): Zeiten, Deltas, Kraftstoff.

Zeiten liegen im Protokoll als Sekunden (float) vor; RaceRoom meldet
nicht gesetzte Werte bereits als None (siehe raceroom_sm._pos).
"""
from __future__ import annotations


def fmt_lap(sec) -> str:
    """Rundenzeit 97.845 -> '1:37.845'; 65.4 -> '1:05.400'; None -> '--.---'."""
    if sec is None or sec <= 0:
        return "--.---"
    sec = float(sec)
    m = int(sec // 60)
    s = sec - m * 60
    return f"{m}:{s:06.3f}"


def fmt_sector(sec) -> str:
    """Sektorzeit 28.412 -> '28.412'; None -> '--.---'."""
    if sec is None or sec < 0:
        return "--.---"
    return f"{float(sec):.3f}"


def fmt_delta(sec) -> str:
    """Live-Delta: -0.213 -> '-0.213', 0.4 -> '+0.400'; None -> '--.---'."""
    if sec is None or sec == 0:
        return "--.---"
    sign = "+" if sec > 0 else "-"
    return f"{sign}{abs(float(sec)):.3f}"


def delta_class(sec) -> str:
    """CSS-artige Klasse: 'pos' (unter Bestzeit), 'neg', 'none'."""
    if sec is None or sec == 0:
        return "none"
    return "pos" if sec < 0 else "neg"


def fmt_fuel(liters) -> str:
    """18.4 -> '18.4 l'; None -> '-- l'."""
    if liters is None or liters < 0:
        return "-- l"
    return f"{float(liters):.1f} l"


def fuel_laps_left(fuel_left, fuel_per_lap) -> int | None:
    """Geschaetzte Restrunden; None ohne sinnvolle Werte."""
    if not fuel_left or not fuel_per_lap or fuel_per_lap <= 0 or fuel_left < 0:
        return None
    return int(fuel_left / fuel_per_lap)


def fmt_session_time(sec) -> str:
    """Verbleibende Sitzungszeit 3725.0 -> '1:02:05'; None -> '--'.  """
    if sec is None or sec < 0:
        return "--:--"
    sec = int(sec)
    h, rest = divmod(sec, 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


# --------------------------------------------------------------------------- --
# Selbsttest
# --------------------------------------------------------------------------- --
def _selftest():
    ok = True

    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print(f"  FEHLER: {name}")

    check("Lap 1", fmt_lap(97.845) == "1:37.845")
    check("Lap 2", fmt_lap(65.4) == "1:05.400")
    check("Lap 3", fmt_lap(59.999) == "0:59.999")
    check("Lap None", fmt_lap(None) == "--.---")
    check("Sektor", fmt_sector(28.412) == "28.412")
    check("Sektor None", fmt_sector(None) == "--.---")
    check("Delta pos", fmt_delta(-0.213) == "-0.213")
    check("Delta neg", fmt_delta(0.4) == "+0.400")
    check("Klasse pos", delta_class(-0.213) == "pos")
    check("Klasse neg", delta_class(0.4) == "neg")
    check("Klasse none", delta_class(None) == "none")
    check("Fuel", fmt_fuel(18.4) == "18.4 l")
    check("Fuel None", fmt_fuel(None) == "-- l")
    check("Runden Rest", fuel_laps_left(18.4, 3.1) == 5)
    check("Runden Rest None", fuel_laps_left(None, 3.1) is None)
    check("Runden Rest 0-Verbrauch", fuel_laps_left(18.0, 0.0) is None)
    check("Session", fmt_session_time(3725) == "1:02:05")
    check("Session kurz", fmt_session_time(65) == "01:05")
    check("Session None", fmt_session_time(None) == "--:--")
    print("format-Selbsttest:", "OK" if ok else "FEHLER")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
