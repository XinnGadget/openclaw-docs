---
read_when:
    - Sie möchten, dass die Erinnerungs-Promotion automatisch ausgeführt wird
    - Sie möchten verstehen, was jede Dreaming-Phase bewirkt
    - Sie möchten die Konsolidierung abstimmen, ohne `MEMORY.md` zu überladen
summary: Hintergrund-Konsolidierung von Erinnerungen mit Light-, Deep- und REM-Phasen sowie einem Dream Diary
title: Dreaming (experimentell)
x-i18n:
    generated_at: "2026-04-06T06:21:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36c4b1e70801d662090dc8ce20608c2f141c23cd7ce53c54e3dcf332c801fd4e
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming (experimentell)

Dreaming ist das Hintergrundsystem zur Konsolidierung von Erinnerungen in `memory-core`.
Es hilft OpenClaw dabei, starke kurzfristige Signale in dauerhafte Erinnerungen zu überführen,
während der Prozess nachvollziehbar und überprüfbar bleibt.

Dreaming ist **optional** und standardmäßig deaktiviert.

## Was Dreaming schreibt

Dreaming verwaltet zwei Arten von Ausgaben:

- **Maschinenzustand** in `memory/.dreams/` (Recall-Speicher, Phasensignale, Ingestion-Checkpoints, Sperren).
- **Menschenlesbare Ausgabe** in `DREAMS.md` (oder vorhandenem `dreams.md`) und optionalen Phasenberichtdateien unter `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Die langfristige Promotion schreibt weiterhin nur in `MEMORY.md`.

## Phasenmodell

Dreaming verwendet drei kooperative Phasen:

| Phase | Zweck                                            | Dauerhafter Schreibvorgang |
| ----- | ------------------------------------------------ | -------------------------- |
| Light | Aktuelles kurzfristiges Material sortieren und vorbereiten | Nein                       |
| Deep  | Dauerhafte Kandidaten bewerten und promovieren   | Ja (`MEMORY.md`)           |
| REM   | Über Themen und wiederkehrende Ideen reflektieren | Nein                       |

Diese Phasen sind interne Implementierungsdetails, keine separaten, vom Benutzer konfigurierbaren
„Modi“.

### Light-Phase

Die Light-Phase erfasst aktuelle tägliche Erinnerungssignale und Recall-Traces, entfernt Duplikate
und bereitet Kandidatenzeilen vor.

- Liest aus dem kurzfristigen Recall-Zustand und aktuellen täglichen Erinnerungsdateien.
- Schreibt einen verwalteten Block `## Light Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Erfasst Verstärkungssignale für ein späteres Deep-Ranking.
- Schreibt niemals in `MEMORY.md`.

### Deep-Phase

Die Deep-Phase entscheidet, was zu einer langfristigen Erinnerung wird.

- Bewertet Kandidaten anhand gewichteter Scores und Schwellenwert-Gates.
- Erfordert das Bestehen von `minScore`, `minRecallCount` und `minUniqueQueries`.
- Hydriert Snippets vor dem Schreiben aus aktiven Tagesdateien erneut, sodass veraltete/gelöschte Snippets übersprungen werden.
- Hängt promovierte Einträge an `MEMORY.md` an.
- Schreibt eine Zusammenfassung `## Deep Sleep` in `DREAMS.md` und optional `memory/dreaming/deep/YYYY-MM-DD.md`.

### REM-Phase

Die REM-Phase extrahiert Muster und reflektierende Signale.

- Erstellt Themen- und Reflexionszusammenfassungen aus aktuellen kurzfristigen Traces.
- Schreibt einen verwalteten Block `## REM Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Erfasst REM-Verstärkungssignale, die vom Deep-Ranking verwendet werden.
- Schreibt niemals in `MEMORY.md`.

## Dream Diary

Dreaming führt außerdem ein erzählerisches **Dream Diary** in `DREAMS.md`.
Sobald nach jeder Phase genügend Material vorhanden ist, führt `memory-core` im Hintergrund
best-effort einen Subagent-Durchlauf aus (mit dem Standard-Laufzeitmodell) und hängt einen kurzen Tagebucheintrag an.

Dieses Tagebuch ist zum Lesen durch Menschen in der Dreams-UI gedacht, nicht als Quelle für Promotion.

## Deep-Ranking-Signale

Das Deep-Ranking verwendet sechs gewichtete Basissignale plus Phasenverstärkung:

| Signal              | Gewicht | Beschreibung                                    |
| ------------------- | ------- | ----------------------------------------------- |
| Häufigkeit          | 0.24    | Wie viele kurzfristige Signale der Eintrag angesammelt hat |
| Relevanz            | 0.30    | Durchschnittliche Abrufqualität für den Eintrag |
| Anfragevielfalt     | 0.15    | Unterschiedliche Anfrage-/Tageskontexte, in denen er auftauchte |
| Aktualität          | 0.15    | Zeitabklingender Frische-Score                  |
| Konsolidierung      | 0.10    | Stärke des Wiederauftretens über mehrere Tage   |
| Konzeptuelle Dichte | 0.06    | Dichte von Konzept-Tags aus Snippet/Pfad        |

Treffer aus der Light- und REM-Phase fügen einen kleinen, zeitabklingenden Boost aus
`memory/.dreams/phase-signals.json` hinzu.

## Zeitplanung

Wenn aktiviert, verwaltet `memory-core` automatisch einen Cron-Job für einen vollständigen Dreaming-Durchlauf.
Jeder Durchlauf führt die Phasen in dieser Reihenfolge aus: light -> REM -> deep.

Standardverhalten für die Ausführungsfrequenz:

| Einstellung          | Standard    |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Schnellstart

Dreaming aktivieren:

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

Dreaming mit einer benutzerdefinierten Durchlauf-Frequenz aktivieren:

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

Die manuelle Ausführung von `memory promote` verwendet standardmäßig die Schwellenwerte der Deep-Phase, sofern sie
nicht mit CLI-Flags überschrieben werden.

Erklären, warum ein bestimmter Kandidat promoviert würde oder nicht:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

REM-Reflexionen, Kandidatenwahrheiten und Deep-Promotion-Ausgaben in der Vorschau anzeigen, ohne
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

Die vollständige Schlüsselliste finden Sie unter [Referenz zur Memory-Konfiguration](/de/reference/memory-config#dreaming-experimental).

## Dreams-UI

Wenn aktiviert, zeigt der Gateway-Tab **Dreams** Folgendes an:

- aktueller Aktivierungsstatus von Dreaming
- Status auf Phasenebene und Vorhandensein verwalteter Durchläufe
- Anzahl kurzfristiger, langfristiger und heute promovierter Erinnerungen
- Zeitpunkt des nächsten geplanten Durchlaufs
- einen aufklappbaren Dream-Diary-Reader, der auf `doctor.memory.dreamDiary` basiert

## Verwandt

- [Memory](/de/concepts/memory)
- [Memory Search](/de/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Referenz zur Memory-Konfiguration](/de/reference/memory-config)
