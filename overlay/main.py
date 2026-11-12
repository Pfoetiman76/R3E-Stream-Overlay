"""R3E Stream-Overlay (Streaming-PC) — Hauptprogramm.

Fensterloses, immer im Vordergrund liegendes Overlay, das die UDP-Pakete
des Agents (Gaming-PC) empfängt und anzeigt. Ohne OBS und ohne jedes
weitere Programm lauffaehig.

Bedienung:
  - Fenster verschieben: mit der Maus ziehen
  - Skalierung: Strg + Mausrad (30–300 %)
  - Ein-/Ausblenden: Hotkey (Standard F8, konfigurierbar)
  - Automatisch: ohne Sitzung/Pakete blendet sich das Overlay aus

Konfiguration (Dokumente\\R3E Stream-Overlay\\overlay_config.json):
  {"scale": 1.0, "x": 18, "y": 18, "hotkey_vk": 119}
"""
from __future__ import annotations

import json
import socket
import sys
import time
from pathlib import Path

if not getattr(sys, "frozen", False):  # als Skript: Projektwurzel in den Pfad
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from rso import APP_VERSION  # noqa: E402
from rso.history import LapHistory  # noqa: E402
from rso.panel import Panel, qss  # noqa: E402
from rso.protocol import DEFAULT_PORT, decode_state  # noqa: E402

HIDE_TIMEOUT_S = 3.0          # ohne Pakete so lange -> Overlay ausblenden
POLL_MS = 60                  # Hotkey-/Auto-Timer
DEFAULT_HOTKEY_VK = 0x77      # F8

_scale_min, _scale_max = 0.3, 3.0


def config_dir() -> Path:
    base = Path.home() / "Documents" / "R3E Stream-Overlay"
    base.mkdir(parents=True, exist_ok=True)
    return base


def load_config() -> dict:
    p = config_dir() / "overlay_config.json"
    cfg = {"scale": 1.0, "x": None, "y": None, "hotkey_vk": DEFAULT_HOTKEY_VK}
    try:
        cfg.update(json.loads(p.read_text(encoding="utf-8")))
    except Exception:
        pass
    return cfg


def save_config(cfg: dict):
    p = config_dir() / "overlay_config.json"
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    tmp.replace(p)


class Listener(QThread):
    """UDP-Empfang im Hintergrundthread; state_ready(dict|None)."""

    state_ready = Signal(object)

    def __init__(self, port=DEFAULT_PORT):
        super().__init__()
        self.port = port
        self._stop = False
        self.last_packet = 0.0

    def run(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(("", self.port))
        except OSError:
            self.state_ready.emit(None)
            return
        sock.settimeout(0.2)
        while not self._stop:
            try:
                data, _addr = sock.recvfrom(8192)
            except socket.timeout:
                continue
            except OSError:
                break
            self.last_packet = time.time()
            ok, state = decode_state(data)
            if ok:
                self.state_ready.emit(state)
        sock.close()

    def stop(self):
        self._stop = True
        self.wait(1500)


class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.manual_off = False
        self.has_state = False
        self.last_state_time = 0.0
        self.history = LapHistory()
        self.scale = float(self.cfg.get("scale", 1.0))

        self.setWindowTitle(f"R3E Stream-Overlay {APP_VERSION}")
        self.setWindowFlags(Qt.FramelessWindowHint
                            | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentAttribute, True)

        self.panel = Panel()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.panel)

        self._apply_scale(self.scale)

        self.listener = Listener(int(self.cfg.get("port", DEFAULT_PORT)))
        self.listener.state_ready.connect(self._on_state)
        self.listener.start()

        self._hk = None
        if sys.platform == "win32":
            import ctypes
            self._user32 = ctypes.windll.user32
        else:
            self._user32 = None
        self._hk_down = False

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(POLL_MS)

        if self.cfg.get("x") is not None and self.cfg.get("y") is not None:
            self.move(int(self.cfg["x"]), int(self.cfg["y"]))

    # ----- Daten -------------------------------------------------------------
    def _on_state(self, state):
        if state is None:
            self.has_state = False
            self.panel.update(None, [])
            return
        self.has_state = True
        self.last_state_time = time.time()
        laps = self.history.feed(state)
        self.panel.update(state, laps)
        if not self.isVisible() and not self.manual_off:
            self.show()

    # ----- Hotkey / Auto-Ausblendung ------------------------------------------
    def _tick(self):
        self._poll_hotkey()
        if (self.isVisible()
                and time.time() - self.last_state_time > HIDE_TIMEOUT_S):
            self.hide()  # keine Sitzung / Agent weg -> still ausblenden
        elif (not self.isVisible() and not self.manual_off
              and time.time() - self.last_state_time < HIDE_TIMEOUT_S
              and self.has_state):
            self.show()

    def _poll_hotkey(self):
        if not self._user32:
            return
        vk = int(self.cfg.get("hotkey_vk", DEFAULT_HOTKEY_VK))
        down = bool(self._user32.GetAsyncKeyState(vk) & 0x8000)
        if down and not self._hk_down:  # Flanke
            if self.isVisible():
                self.manual_off = True
                self.hide()
            else:
                self.manual_off = False
                self.show()
        self._hk_down = down

    # ----- Fenstersteuerung ----------------------------------------------------
    def _apply_scale(self, scale):
        self.scale = min(_scale_max, max(_scale_min, scale))
        self.setFixedWidth(int(340 * self.scale))
        self.setStyleSheet(qss(self.scale))
        self.adjustSize()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self._drag = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if e.buttons() & Qt.LeftButton and getattr(self, "_drag", None):
            self.move(e.globalPos() - self._drag)
            e.accept()

    def mouseReleaseEvent(self, e):
        self._drag = None
        self.cfg["x"], self.cfg["y"] = self.x(), self.y()
        save_config(self.cfg)

    def wheelEvent(self, e):
        if e.modifiers() & Qt.ControlModifier:
            self._apply_scale(self.scale + (0.1 if e.angleDelta().y() > 0 else -0.1))
            self.cfg["scale"] = round(self.scale, 2)
            save_config(self.cfg)
            e.accept()
        else:
            e.ignore()

    def closeEvent(self, e):
        self.cfg["x"], self.cfg["y"] = self.x(), self.y()
        save_config(self.cfg)
        self.listener.stop()
        e.accept()


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    win = OverlayWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
