---
read_when:
    - Sie möchten, dass die Speicherpromotion automatisch ausgeführt wird
    - Sie möchten verstehen, was jede Träumphase bewirkt
    - Sie möchten die Konsolidierung abstimmen, ohne `MEMORY.md` zu überladen
summary: Hintergrundkonsolidierung von Speicherinhalten mit Light-, Deep- und REM-Phasen sowie einem Traumtagebuch
title: Träumen (experimentell)
x-i18n:
    generated_at: "2026-04-09T01:27:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 26476eddb8260e1554098a6adbb069cf7f5e284cf2e09479c6d9d8f8b93280ef
    source_path: concepts/dreaming.md
    workflow: 15
---

# Träumen (experimentell)

Träumen ist das Hintergrundsystem zur Konsolidierung von Speicherinhalten in `memory-core`.
Es hilft OpenClaw dabei, starke kurzfristige Signale in dauerhafte Speicherinhalte zu überführen, während
der Prozess nachvollziehbar und überprüfbar bleibt.

Träumen ist **optional** und standardmäßig deaktiviert.

## Was Träumen schreibt

Träumen verwaltet zwei Arten von Ausgaben:

- **Maschinenzustand** in `memory/.dreams/` (Recall-Speicher, Phasensignale, Ingestion-Prüfpunkte, Sperren).
- **Menschenlesbare Ausgabe** in `DREAMS.md` (oder vorhandener `dreams.md`) und optionalen Phasenberichtdateien unter `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Die langfristige Promotion schreibt weiterhin nur in `MEMORY.md`.

## Phasenmodell

Träumen verwendet drei kooperative Phasen:

| Phase | Zweck                                     | Dauerhafter Schreibvorgang |
| ----- | ----------------------------------------- | -------------------------- |
| Light | Jüngstes kurzfristiges Material sortieren und vorbereiten | Nein                       |
| Deep  | Dauerhafte Kandidaten bewerten und befördern | Ja (`MEMORY.md`)           |
| REM   | Über Themen und wiederkehrende Ideen reflektieren | Nein                       |

Diese Phasen sind interne Implementierungsdetails, keine separat vom Benutzer konfigurierbaren
„Modi“.

### Light-Phase

Die Light-Phase erfasst aktuelle tägliche Speichersignale und Recall-Traces, dedupliziert sie
und bereitet Kandidatenzeilen vor.

- Liest aus kurzfristigem Recall-Zustand, aktuellen täglichen Speicherdateien und redigierten Sitzungsabschriften, sofern verfügbar.
- Schreibt einen verwalteten Block `## Light Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Zeichnet Verstärkungssignale für die spätere Deep-Rangfolge auf.
- Schreibt niemals in `MEMORY.md`.

### Deep-Phase

Die Deep-Phase entscheidet, was zu langfristigem Speicher wird.

- Ordnet Kandidaten mithilfe gewichteter Bewertung und Schwellenwert-Gates ein.
- Erfordert, dass `minScore`, `minRecallCount` und `minUniqueQueries` erfüllt werden.
- Stellt Snippets vor dem Schreiben aus aktiven täglichen Dateien wieder her, sodass veraltete oder gelöschte Snippets übersprungen werden.
- Hängt beförderte Einträge an `MEMORY.md` an.
- Schreibt eine Zusammenfassung `## Deep Sleep` in `DREAMS.md` und schreibt optional `memory/dreaming/deep/YYYY-MM-DD.md`.

### REM-Phase

Die REM-Phase extrahiert Muster und reflektierende Signale.

- Erstellt Themen- und Reflexionszusammenfassungen aus aktuellen kurzfristigen Traces.
- Schreibt einen verwalteten Block `## REM Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Zeichnet REM-Verstärkungssignale auf, die von der Deep-Rangfolge verwendet werden.
- Schreibt niemals in `MEMORY.md`.

## Aufnahme von Sitzungsabschriften

Träumen kann redigierte Sitzungsabschriften in den Träum-Korpus aufnehmen. Wenn
Abschriften verfügbar sind, werden sie zusammen mit täglichen
Speichersignalen und Recall-Traces in die Light-Phase eingespeist. Persönliche und sensible Inhalte werden vor der Aufnahme redigiert.

## Traumtagebuch

Träumen führt außerdem ein erzählerisches **Traumtagebuch** in `DREAMS.md`.
Nachdem jede Phase genügend Material hat, führt `memory-core` im Hintergrund nach bestem Bemühen einen
Subagenten-Durchlauf aus (unter Verwendung des Standard-Laufzeitmodells) und hängt einen kurzen Tagebucheintrag an.

Dieses Tagebuch ist für menschliches Lesen in der Dreams-Benutzeroberfläche gedacht, nicht als Promotionsquelle.

Es gibt außerdem einen fundierten historischen Backfill-Pfad für Prüf- und Wiederherstellungsarbeiten:

- `memory rem-harness --path ... --grounded` zeigt eine Vorschau der fundierten Tagebuchausgabe aus historischen Notizen `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` schreibt reversible fundierte Tagebucheinträge in `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` stellt fundierte dauerhafte Kandidaten in denselben kurzfristigen Evidenzspeicher ein, den die normale Deep-Phase bereits verwendet.
- `memory rem-backfill --rollback` und `--rollback-short-term` entfernen diese bereitgestellten Backfill-Artefakte, ohne normale Tagebucheinträge oder aktiven kurzfristigen Recall zu berühren.

Die Control UI bietet denselben Tagebuch-Backfill-/Zurücksetzen-Ablauf, damit Sie
Ergebnisse in der Dreams-Ansicht prüfen können, bevor Sie entscheiden, ob die fundierten Kandidaten
eine Promotion verdienen. Die Ansicht zeigt außerdem einen separaten fundierten Pfad, damit Sie sehen können,
welche bereitgestellten kurzfristigen Einträge aus historischem Replay stammen, welche beförderten
Elemente fundiert ausgelöst wurden, und fundiert-only bereitgestellte Einträge löschen können, ohne
den normalen aktiven kurzfristigen Zustand zu berühren.

## Deep-Rangfolgesignale

Die Deep-Rangfolge verwendet sechs gewichtete Basissignale plus Phasenverstärkung:

| Signal              | Gewicht | Beschreibung                                     |
| ------------------- | ------- | ------------------------------------------------ |
| Häufigkeit          | 0.24    | Wie viele kurzfristige Signale der Eintrag gesammelt hat |
| Relevanz            | 0.30    | Durchschnittliche Abrufqualität für den Eintrag  |
| Abfragevielfalt     | 0.15    | Unterschiedliche Abfrage-/Tageskontexte, in denen er erschien |
| Aktualität          | 0.15    | Zeitlich abklingender Frischewert                |
| Konsolidierung      | 0.10    | Stärke des Wiederauftretens über mehrere Tage    |
| Konzeptionelle Dichte | 0.06  | Dichte der Konzept-Tags aus Snippet/Pfad         |

Treffer aus der Light- und REM-Phase fügen einen kleinen, mit der Aktualität abklingenden Boost aus
`memory/.dreams/phase-signals.json` hinzu.

## Planung

Wenn aktiviert, verwaltet `memory-core` automatisch einen Cron-Job für einen vollständigen
Träum-Durchlauf. Jeder Durchlauf führt die Phasen der Reihe nach aus: light -> REM -> deep.

Standardverhalten für die Taktung:

| Einstellung          | Standard    |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Schnellstart

Träumen aktivieren:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Träumen mit benutzerdefinierter Durchlauf-Taktung aktivieren:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Slash-Befehl

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## CLI-Workflow

Verwenden Sie die CLI-Promotion für Vorschau oder manuelle Anwendung:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Die manuelle Verwendung von `memory promote` nutzt standardmäßig die Schwellenwerte der Deep-Phase, sofern diese
nicht mit CLI-Flags überschrieben werden.

Erklären, warum ein bestimmter Kandidat befördert würde oder nicht:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

REM-Reflexionen, Kandidatenwahrheiten und die Ausgabe der Deep-Promotion als Vorschau anzeigen, ohne
etwas zu schreiben:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Wichtige Standardwerte

Alle Einstellungen befinden sich unter `plugins.entries.memory-core.config.dreaming`.

| Schlüssel   | Standard    |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

Phasenrichtlinie, Schwellenwerte und Speicherverhalten sind interne Implementierungsdetails
(keine benutzerseitige Konfiguration).

Siehe [Referenz zur Speicherkonfiguration](/de/reference/memory-config#dreaming-experimental)
für die vollständige Liste der Schlüssel.

## Dreams-Benutzeroberfläche

Wenn aktiviert, zeigt der Gateway-Tab **Dreams** Folgendes an:

- aktuellen Aktivierungsstatus von Träumen
- Status auf Phasenebene und Vorhandensein des verwalteten Durchlaufs
- Anzahlen für kurzfristige, fundierte, Signal- und heute beförderte Einträge
- Zeitpunkt des nächsten geplanten Durchlaufs
- einen separaten fundierten Szenenpfad für bereitgestellte historische Replay-Einträge
- einen aufklappbaren Traumtagebuch-Leser auf Basis von `doctor.memory.dreamDiary`

## Verwandt

- [Speicher](/de/concepts/memory)
- [Speichersuche](/de/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Referenz zur Speicherkonfiguration](/de/reference/memory-config)
