"""Panel-Darstellung des R3E-Stream-Overlays (PySide6).

Baut die Oberflaeche nach der freigegebenen Vorschau auf:
Kopf (Strecke + LIVE), 6 Kacheln, Sektorentabelle, Rundenliste.
Alle Werte werden ueber update() gesetzt; Formatierung passiert in
rso.format (Qt-frei).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFrame, QGridLayout, QHBoxLayout, QLabel,
                               QVBoxLayout, QWidget)

from rso.format import (delta_class, fmt_delta, fmt_fuel, fmt_lap,
                        fmt_sector, fmt_session_time)

# Farbwerte aus der freigegebenen Vorschau (PitBoss-/R3E-Schema)
C_BG = "#131318"
C_PANEL = "#1a1a20"
C_KACHEL = "#202027"
C_KOPF = "#2a2a32"
C_GITTER = "#26262e"
C_ROT = "#e8212b"
C_ROT_HELL = "#ff5a63"
C_GOLD = "#e8c34a"
C_GRUEN = "#4cd964"
C_TEXT = "#e9e9ef"
C_GEDAMPFT = "#9a9aa5"
C_MONO = "Consolas"


def _lbl(text="", klasse="", mono=False, fett=False):
    l = QLabel(text)
    l.setProperty("cssClass", klasse)
    if mono:
        l.setProperty("mono", True)
    if fett:
        l.setProperty("bold", True)
    l.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
    return l


class Tile(QFrame):
    """Eine Kachel: Label oben, grosser Wert, Zusatz darunter."""

    def __init__(self, label):
        super().__init__()
        self.setProperty("cssClass", "tile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 7, 10, 6)
        lay.setSpacing(0)
        self.lbl = _lbl(label, "dim")
        self.lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.wert = _lbl("--", "wert", mono=True, fett=True)
        self.wert.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.zusatz = _lbl("", "dim small")
        self.zusatz.setAlignment(Qt.AlignmentFlag.AlignLeft)
        lay.addWidget(self.lbl)
        lay.addWidget(self.wert)
        lay.addWidget(self.zusatz)

    def set_wert(self, text, color=None):
        self.wert.setText(text)
        self.wert.setStyleSheet(f"color: {color};" if color else "")

    def set_zusatz(self, text, color=None):
        self.zusatz.setText(text)
        self.zusatz.setStyleSheet(f"color: {color};" if color else "")


class Panel(QWidget):
    """Gesamtes Overlay-Panel; update() setzt alle Anzeigen."""

    def __init__(self):
        super().__init__()
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setObjectName("panelRoot")

        # ---- Kopfzeile -----------------------------------------------------
        kopf = QFrame()
        kopf.setProperty("cssClass", "kopf")
        klay = QHBoxLayout(kopf)
        klay.setContentsMargins(12, 7, 12, 7)
        self.strecke = _lbl("", "fett")
        self.strecke.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.live = _lbl("LIVE", "live", fett=True)
        klay.addWidget(self.strecke, 1)
        klay.addWidget(self.live)

        # ---- Kacheln -------------------------------------------------------
        kacheln = QWidget()
        kgrid = QGridLayout(kacheln)
        kgrid.setContentsMargins(0, 0, 0, 0)
        kgrid.setSpacing(0)
        self.t_lap = Tile("Laufende Runde")
        self.t_last = Tile("Letzte Runde")
        self.t_best = Tile("Bestzeit")
        self.t_delta = Tile("Delta")
        self.t_fuel = Tile("Kraftstoff")
        self.t_pos = Tile("Position")
        for i, t in enumerate((self.t_lap, self.t_last, self.t_best,
                               self.t_delta, self.t_fuel, self.t_pos)):
            kgrid.addWidget(t, i // 3, i % 3)

        # ---- Sektoren ------------------------------------------------------
        sek = QWidget()
        sek.setProperty("cssClass", "block")
        sig = QVBoxLayout(sek)
        sig.setContentsMargins(12, 6, 12, 4)
        sgrid = QGridLayout()
        sgrid.setHorizontalSpacing(18)
        sgrid.setVerticalSpacing(1)
        sig.addLayout(sgrid)
        for j, titel in enumerate(("Sektor", "Aktuell", "Letzte", "Beste")):
            h = _lbl(titel, "dim small")
            sgrid.addWidget(h, 0, j)
        self.sek_zellen = {}
        for i in range(3):
            nr = _lbl(f"S{i + 1}", "mono")
            nr.setAlignment(Qt.AlignmentFlag.AlignLeft)
            sgrid.addWidget(nr, i + 1, 0)
            self.sek_zellen[i] = {}
            for j, art in enumerate(("cur", "last", "best")):
                z = _lbl("--.---", "mono")
                sgrid.addWidget(z, i + 1, j + 1)
                self.sek_zellen[i][art] = z

        # ---- Rundenliste ---------------------------------------------------
        rund = QWidget()
        rund.setProperty("cssClass", "block")
        rlay = QVBoxLayout(rund)
        rlay.setContentsMargins(12, 4, 12, 8)
        rgrid = QGridLayout()
        rgrid.setHorizontalSpacing(14)
        rgrid.setVerticalSpacing(1)
        rlay.addLayout(rgrid)
        for j, titel in enumerate(("Runde", "Zeit", "S1", "S2", "S3", "Kraftstoff")):
            h = _lbl(titel, "dim small")
            rgrid.addWidget(h, 0, j)
        self.rund_zeilen = []
        for i in range(6):  # 1 laufende + 5 fertige Runden
            zellen = []
            for j in range(6):
                z = _lbl("", "mono")
                if j > 0:
                    z.setProperty("mono", True)
                if j == 0:
                    z.setAlignment(Qt.AlignmentFlag.AlignLeft)
                rgrid.addWidget(z, i + 1, j)
                zellen.append(z)
            self.rund_zeilen.append(zellen)

        for w in (kopf, kacheln, sek, rund):
            root.addWidget(w)

    # ----- Anzeige ----------------------------------------------------------
    def update(self, state, laps):
        """state: Protokoll-Dict (rso.state.build_state) oder None."""
        if not state:
            self.strecke.setText("Warten auf Agent …")
            self.live.setText("")
            for t in (self.t_lap, self.t_last, self.t_best, self.t_delta,
                      self.t_fuel, self.t_pos):
                t.set_wert("--")
                t.set_zusatz("")
            return
        self.strecke.setText(f"{state.get('track') or '—'}"
                            f"  ·  {state.get('layout') or ''}"
                            f"  ·  {state.get('session_type') or ''}")
        self.live.setText("LIVE")

        self.t_lap.set_wert(fmt_lap(state.get("lap_current_s")))
        self.t_lap.set_zusatz(f"Runde {state.get('lap_nr', 0)}")

        letzte = fmt_lap(state.get("lap_last_s"))
        farbe = None
        if state.get("lap_last_s"):
            farbe = C_TEXT if state.get("lap_last_valid") else C_ROT_HELL
        self.t_last.set_wert(letzte, farbe)
        self.t_last.set_zusatz("" if state.get("lap_last_valid") else "ungültig",
                               None if state.get("lap_last_valid") else C_ROT_HELL)

        self.t_best.set_wert(fmt_lap(state.get("lap_best_s")), C_GOLD)
        self.t_best.set_zusatz("Sitzung")

        d = state.get("delta_best_s")
        self.t_delta.set_wert(fmt_delta(d),
                              {("pos",): C_GRUEN, ("neg",): C_ROT_HELL,
                               ("none",): None}.get((delta_class(d),), None))
        self.t_delta.set_zusatz("zur Bestzeit")

        self.t_fuel.set_wert(fmt_fuel(state.get("fuel_left_l")))
        rest = state.get("fuel_laps_left")
        self.t_fuel.set_zusatz(f"≈ {rest} Runden" if rest is not None else "")

        platz = state.get("place")
        self.t_pos.set_wert(f"P{platz}" if platz else "--")
        self.t_pos.set_zusatz(f"von {state.get('num_cars', 0)}"
                              if state.get("num_cars") else "")

        # Sektoren
        cur, last, best = (state.get("sector_cur") or [],
                          state.get("sector_last") or [],
                          state.get("sector_best") or [])
        for i in range(3):
            c, l, b = (cur[i] if i < len(cur) else None,
                       last[i] if i < len(last) else None,
                       best[i] if i < len(best) else None)
            farbe_c = C_GRUEN if (c and b and c < b) else (C_ROT_HELL if (c and b and c > b) else None)
            self.sek_zellen[i]["cur"].setText(fmt_sector(c))
            self.sek_zellen[i]["cur"].setStyleSheet(f"color: {farbe_c};" if farbe_c else "")
            self.sek_zellen[i]["last"].setText(fmt_sector(l))
            self.sek_zellen[i]["last"].setStyleSheet("")
            self.sek_zellen[i]["best"].setText(fmt_sector(b))
            self.sek_zellen[i]["best"].setStyleSheet(f"color: {C_GOLD};" if b else "")

        # Rundenliste: laufende Zeile + Historie
        for i, zellen in enumerate(self.rund_zeilen):
            for z in zellen:
                z.setText("")
                z.setStyleSheet("")
        if state.get("lap_current_s") or state.get("lap_nr"):
            z = self.rund_zeilen[0]
            z[0].setText(str(state.get("lap_nr", "")))
            z[0].setStyleSheet(f"color: #ffffff;")
            z[1].setText(fmt_lap(state.get("lap_current_s")))
            for i in range(3):
                c = (state.get("sector_cur") or [None, None, None])
                if i < len(c) and c[i]:
                    z[2 + i].setText(fmt_sector(c[i]))
            z[5].setText(fmt_fuel(state.get("fuel_left_l")))
        best_s = state.get("lap_best_s")
        for r, eintrag in enumerate(laps[:5], start=1):
            z = self.rund_zeilen[r]
            z[0].setText(str(eintrag.get("nr", "")))
            z[1].setText(fmt_lap(eintrag.get("time_s")))
            farbe = C_TEXT
            if eintrag.get("time_s") and best_s and abs(eintrag["time_s"] - best_s) < 1e-6:
                farbe = C_GOLD
            elif eintrag.get("valid") is False:
                farbe = C_ROT_HELL
            z[1].setStyleSheet(f"color: {farbe};")
            for i in range(3):
                s = (eintrag.get("sectors") or [])
                z[2 + i].setText(fmt_sector(s[i]) if i < len(s) and s[i] else "")
            z[5].setText(fmt_fuel(eintrag.get("fuel_l")))


def qss(scale: float = 1.0) -> str:
    """Stylesheet mit skalierungsfaktor (1.0 = Vorschau-Groesse)."""
    px = lambda n: max(6, int(round(n * scale)))
    return f"""
    #panelRoot {{
        background: {C_BG};
        border: 1px solid {C_GITTER};
        border-radius: {px(8)}px;
    }}
    QLabel {{ color: {C_TEXT}; font-family: "Segoe UI"; font-size: {px(12)}px; }}
    QLabel[mono="true"] {{ font-family: "{C_MONO}"; }}
    QLabel[bold="true"] {{ font-weight: 600; }}
    QLabel[cssClass="dim"] {{ color: {C_GEDAMPFT}; font-size: {px(10)}px;
        text-transform: uppercase; letter-spacing: {px(1)}px; }}
    QLabel[cssClass="dim small"] {{ color: {C_GEDAMPFT}; font-size: {px(10)}px;
        text-transform: uppercase; letter-spacing: {px(1)}px; }}
    QLabel[cssClass="wert"] {{ font-family: "{C_MONO}"; font-size: {px(16)}px;
        font-weight: 600; color: #ffffff; }}
    QLabel[cssClass="live"] {{ color: {C_ROT_HELL}; font-size: {px(11)}px;
        font-weight: 700; letter-spacing: {px(1)}px; }}
    QLabel[cssClass="fett"] {{ color: #ffffff; font-size: {px(13)}px; font-weight: 600; }}
    QFrame[cssClass="kopf"] {{ background: {C_KOPF};
        border-bottom: 2px solid {C_ROT}; border-radius: 0; }}
    QWidget[cssClass="block"] {{ border-bottom: 1px solid {C_GITTER}; }}
    QFrame[cssClass="tile"] {{ background: transparent;
        border-right: 1px solid {C_GITTER}; border-bottom: 1px solid {C_GITTER}; }}
    """
