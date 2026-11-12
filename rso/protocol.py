"""UDP-Protokoll v1 zwischen Agent (Gaming-PC) und Overlay (Streaming-PC).

Paketaufbau: UTF-8-JSON mit Pflichtfeldern

    {"magic": "R3ESO", "v": 1, "state": {...}|null}

"state" ist null, wenn der Agent lebt, aber keine Sitzung laeuft
(Hauptmenue/Replay). Das Overlay blendet sich dann selbst aus.

encode_state()/decode_state() sind bewusst Qt-frei und fuer Tests
geeignet; decode_state() validiert Magic und Version und liefert bei
unpassendem oder korruptem Paket None statt eine Ausnahme.
"""
from __future__ import annotations

import json

MAGIC = "R3ESO"
PROTOCOL_VERSION = 1
DEFAULT_PORT = 53197
DEFAULT_BROADCAST = "255.255.255.255"
MAX_PACKET_BYTES = 8192


def encode_state(state: dict | None) -> bytes:
    """Zustands-Dict (oder None = Idle) in UDP-Bytes wandeln."""
    msg = {"magic": MAGIC, "v": PROTOCOL_VERSION, "state": state}
    return json.dumps(msg, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def decode_state(data: bytes):
    """UDP-Bytes in (state|None) wandeln; None-Rueckgabe mit Flag.

    Rueckgabe: (ok, state) — ok=False bei unpassendem/korruptem Paket,
    state=None wenn der Agent leerlaeuft (keine Sitzung)."""
    try:
        msg = json.loads(data.decode("utf-8"))
    except Exception:
        return (False, None)
    if not isinstance(msg, dict) or msg.get("magic") != MAGIC:
        return (False, None)
    if int(msg.get("v", 0)) != PROTOCOL_VERSION:
        return (False, None)
    state = msg.get("state")
    if state is not None and not isinstance(state, dict):
        return (False, None)
    return (True, state)


def encode_idle() -> bytes:
    """Herzschlag-Paket ohne Sitzung."""
    return encode_state(None)


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

    s = {"track": "Nuerburgring", "lap_best_s": 97.845}
    raw = encode_state(s)
    check("Kompakt", len(raw) < 400)
    ok1, st = decode_state(raw)
    check("Roundtrip ok", ok1 and st == s)
    ok2, idle = decode_state(encode_idle())
    check("Idle", ok2 and idle is None)
    ok3, _ = decode_state(b"kein json")
    check("Muell abgewiesen", not ok3)
    ok4, _ = decode_state(json.dumps({"magic": "ANDERES", "v": 1}).encode())
    check("Magic abgewiesen", not ok4)
    ok5, _ = decode_state(json.dumps({"magic": MAGIC, "v": 99}).encode())
    check("Version abgewiesen", not ok5)
    print("protocol-Selbsttest:", "OK" if ok else "FEHLER")
    return ok


if __name__ == "__main__":
    import sys
    sys.exit(0 if _selftest() else 1)
