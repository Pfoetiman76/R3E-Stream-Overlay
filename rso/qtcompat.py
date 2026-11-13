"""Qt-Enum-Kompatibilitaet fuer unterschiedliche PySide6-Versionen.

Je nach PySide6-Version sind Qt-Enums nur "flach" (Qt.WA_...), nur
qualifiziert (Qt.WidgetAttribute.WA_...) oder in beiden Formen verfuegbar.
Diese Schicht loest alle benoetigten Konstanten zur Importzeit auf und
schlaegt bei fehlenden Pflichtwerten mit einer klaren Meldung fehl
(fail-loud). Optionale Werte (z. B. Translucency) fallen auf None zurueck;
der Aufrufer muss das beruecksichtigen.
"""
from __future__ import annotations

import PySide6
from PySide6.QtCore import Qt

__all__ = ["WINDOW_FLAGS", "WA_TRANSLUCENT_ATTRIBUTE", "MOUSE_LEFT", "CTRL",
           "ALIGN_LEFT", "ALIGN_RIGHT", "ALIGN_VCENTER", "ALIGN_RIGHT_VCENTER"]


def _resolve(container_name: str, member_name: str, optional: bool = False):
    """Qt.<container>.<member> bevorzugen, sonst Qt.<member> (flach)."""
    scoped = getattr(getattr(Qt, container_name, None), member_name, None)
    flat = getattr(Qt, member_name, None)
    value = scoped if scoped is not None else flat
    if value is None and not optional:
        raise AttributeError(
            f"Weder Qt.{container_name}.{member_name} noch Qt.{member_name} "
            f"sind in PySide6 {PySide6.__version__} verfuegbar."
        )
    return value


# Fenster (Overlay): rahmenlos, immer im Vordergrund, ohne Taskleiste
WINDOW_FLAGS = (_resolve("WindowType", "FramelessWindowHint")
                | _resolve("WindowType", "WindowStaysOnTopHint")
                | _resolve("WindowType", "Tool"))

# Optional: transparenter Fensterhintergrund (runde Ecken).
# Fehlt das Attribut in einer PySide6-Version, laeuft das Overlay mit
# dichtem Hintergrund weiter (rein kosmetischer Unterschied).
WA_TRANSLUCENT_ATTRIBUTE = _resolve("WidgetAttribute",
                                    "WA_TranslucentAttribute", optional=True)

# Maus / Tastatur
MOUSE_LEFT = _resolve("MouseButton", "LeftButton")
CTRL = _resolve("KeyboardModifier", "ControlModifier")

# Ausrichtung (Panel)
ALIGN_LEFT = _resolve("AlignmentFlag", "AlignLeft")
ALIGN_RIGHT = _resolve("AlignmentFlag", "AlignRight")
ALIGN_VCENTER = _resolve("AlignmentFlag", "AlignVCenter")
ALIGN_RIGHT_VCENTER = ALIGN_RIGHT | ALIGN_VCENTER
