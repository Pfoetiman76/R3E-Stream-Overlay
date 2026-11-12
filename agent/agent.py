"""R3E Stream-Overlay Agent (Gaming-PC, fensterlos).

Liest das RaceRoom-Shared-Memory ($R3E) und sendet die Overlay-Daten
10x pro Sekunde als UDP-Broadcast ins lokale Netzwerk. Laeuft keine
Sitzung (Hauptmenue, Replay, Spiel zu), sendet der Agent einmal pro
Sekunde ein Idle-Herzschlag-Paket, damit das Overlay sich ausblendet
und weiss, dass der Agent noch lebt.

Aufruf:
    python agent.py                  # Standard: Broadcast 255.255.255.255:53197
    python agent.py --port 53197 --broadcast 192.168.1.255 --rate 10
    python agent.py --verbose        # Statuszeilen auf der Konsole

Als EXE (PyInstaller, --noconsole) einfach mit Windows starten; der
Installer legt optional einen Autostart-Eintrag an.
"""
from __future__ import annotations

import argparse
import socket
import sys
import time
from pathlib import Path

if not getattr(sys, "frozen", False):  # als Skript: Projektwurzel in den Pfad
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rso import APP_VERSION  # noqa: E402
from rso.protocol import (DEFAULT_BROADCAST, DEFAULT_PORT, MAX_PACKET_BYTES,  # noqa: E402
                          encode_idle, encode_state)
from rso.raceroom_sm import R3EReader  # noqa: E402
from rso.state import build_state  # noqa: E402

IDLE_HZ = 1.0  # Herzschlag, wenn keine Sitzung laeuft


class Agent:
    """Lesen->Senden-Schleife; trennbar fuer Tests (reader/Socket injizierbar)."""

    def __init__(self, reader, sock=None, addr=(DEFAULT_BROADCAST, DEFAULT_PORT),
                 rate_hz=10.0):
        self.reader = reader
        self.sock = sock
        self.addr = addr
        self.rate = rate_hz
        self.last_send = 0.0
        self.sent = 0
        self.last_error = ""

    def _send(self, data: bytes) -> bool:
        if self.sock is None:
            return False
        try:
            self.sock.sendto(data[:MAX_PACKET_BYTES], self.addr)
            self.sent += 1
            return True
        except OSError as e:
            self.last_error = str(e)
            return False

    def tick(self, now: float | None = None) -> bool:
        """Ein Arbeitsschritt; True, wenn ein Paket gesendet wurde."""
        now = time.monotonic() if now is None else now
        try:
            sample = self.reader.read()
        except Exception as e:  # Spiel laeuft nicht / Shared Memory weg
            self.last_error = str(e)
            sample = None
            state = None
        else:
            state = build_state(sample) if sample is not None else None
        min_abstand = 1.0 / IDLE_HZ if state is None else 1.0 / max(0.5, self.rate)
        if now - self.last_send < min_abstand:
            return False
        ok = self._send(encode_state(state) if state else encode_idle())
        if ok:
            self.last_send = now
        return ok


def make_socket():
    """UDP-Broadcast-Socket anlegen (SO_BROADCAST, ohne Bindung)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.setblocking(False)
    return s


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="R3E Stream-Overlay Agent")
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--broadcast", default=DEFAULT_BROADCAST)
    p.add_argument("--rate", type=float, default=10.0)
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args(argv)

    if args.verbose:
        print(f"R3E Stream-Overlay Agent {APP_VERSION} "
              f"-> udp://{args.broadcast}:{args.port} @{args.rate:.0f} Hz")
    sock = make_socket()
    agent = Agent(R3EReader(), sock, (args.broadcast, args.port), args.rate)
    try:
        while True:
            agent.tick()
            time.sleep(0.01)
    except KeyboardInterrupt:
        if args.verbose:
            print("Agent beendet.")
        return 0
    finally:
        sock.close()


if __name__ == "__main__":
    sys.exit(main())
