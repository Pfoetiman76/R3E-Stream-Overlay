# R3E Stream-Overlay

Eigenständiges RaceRoom-Overlay für Zwei-PC-Streaming — **ohne OBS**, **ohne PitBoss** und **ohne den Results Companion** auf dem Streaming-PC.

Zwei Komponenten:

| Komponente | PC | Aufgabe |
|---|---|---|
| **Agent** (fensterlos) | Gaming-PC | Liest das RaceRoom-Shared-Memory (`$R3E`, 10 Hz) und sendet die Daten als UDP-Broadcast ins LAN |
| **Overlay** | Streaming-PC | Eigenes Fenster (immer im Vordergrund), zeigt Rundenzeiten, Sektoren, Kraftstoff, Position |

Beide Programme sind bewusst schlank getrennt und greifen auf keinerlei andere App des R3E-Ökosystems zu. Der Agent ist eine Kopie des bewährten Readers aus R3E-Resultate/PitBoss R3E (315/315 Offsets verifiziert), erweitert um Position, Fahrzeugzahl und Sitzungszeit.

## Installation

### Gaming-PC: Agent
1. `R3E-Stream-Agent-Setup-x.y.z.exe` ausführen
2. Haken „Agent mit Windows starten" gesetzt lassen — der Agent läuft ab dann unsichtbar im Hintergrund und sendet, sobald RaceRoom läuft

### Streaming-PC: Overlay
1. `R3E-Stream-Overlay-Setup-x.y.z.exe` ausführen
2. `R3E-Stream-Overlay.exe` starten
3. Beide PCs müssen sich im selben Netzwerk befinden (Standard-UDP-Broadcast an Port 53197)

Firewall-Hinweis: Windows fragt beim ersten Start des Agents nach Netzwerkzugriff — zulassen (private Netzwerke genügen).

## Overlay-Anzeige

- Kopf: Strecke · Layout · Sitzungstyp + LIVE-Badge
- Kacheln: laufende Runde (+ Rundennr.), letzte Runde (rot/„ungültig"), Sitzungs-Bestzeit (gold), Live-Delta (grün/rot), Kraftstoff (+ geschätzte Restrunden), Position (P n von m)
- Sektorentabelle: aktuell / letzte / beste (grün = unter Bestwert, gold = Bestwert)
- Rundenliste: laufende Runde (weiß) + die letzten 5 Runden (gold = Bestzeit, hellrot = ungültig)

## Bedienung (Overlay, Streaming-PC)

- **Verschieben**: Fenster mit der Maus ziehen
- **Skalierung**: Strg + Mausrad (30–300 %)
- **Ein-/Ausblenden**: Hotkey F8 (frei belegbar über `hotkey_vk` in der Konfiguration, virtueller Tastencode)
- **Automatik**: Ohne laufende Sitzung oder ohne Agent-Pakete blendet sich das Overlay nach 3 Sekunden selbst aus und kommt beim nächsten Rennen automatisch zurück

Konfigurationsdatei: `Dokumente\R3E Stream-Overlay\overlay_config.json` (`scale`, `x`, `y`, `hotkey_vk`).

## Agent-Optionen (nur bei Bedarf)

```
R3E-Stream-Agent.exe [--port 53197] [--broadcast 255.255.255.255] [--rate 10] [--verbose]
```

Bei Netzwerkproblemen mit dem generischen Broadcast kann die Broadcast-Adresse des eigenen Subnetzes gesetzt werden (z. B. `--broadcast 192.168.1.255`). Der Agent sendet zusätzlich 1× pro Sekunde ein Idle-Herzschlag, wenn RaceRoom läuft, aber keine Sitzung aktiv ist.

## Protokoll (für eigene Erweiterungen)

UTF-8-JSON pro UDP-Paket: `{"magic":"R3ESO","v":1,"state":{…}|null}` — `state` ist `null`, wenn keine Sitzung läuft. Alle Zeiten in Sekunden; nicht gesetzte Werte sind `null` (Overlay zeigt `--`). Details: `rso/protocol.py`, Feldliste: `rso/state.py`. Damit kann jedes eigene Tool (z. B. ein Stream-Deck-Skript) dieselben Daten mithören — der Broadcast erreicht alle Empfänger im LAN gleichzeitig.

## Entwicklung

```
python tests/run_all.py        # 30 Tests (Qt-frei)
python -m rso.protocol         # Selbsttest Protokoll
python -m rso.raceroom_sm      # Selbsttest Shared-Memory-Reader
```

Release: Tag `v<APP_VERSION>` auf `main` → GitHub Actions baut beide Installer und hängt sie ans Release. Das Overlay benötigt PySide6, der Agent ausschließlich die Standardbibliothek.

## Versionshistorie

- **0.1.1** — Fix: voll qualifizierte PySide6-Enums (Absturz des Overlay beim Fenster-Attribut behoben); CI: PySide6-Smoketest ergänzt.
- **0.1.0** — Erste Version: Agent (10 Hz, UDP-Broadcast, Idle-Herzschlag), Overlay (Kacheln, Sektoren, Rundenliste, Hotkey F8, Drag/Skalierung, Auto-Ausblendung), CI mit zwei Installern.
