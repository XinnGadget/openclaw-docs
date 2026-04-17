---
read_when:
    - Sie möchten, dass die Gedächtnisförderung automatisch ausgeführt wird
    - Sie möchten verstehen, was jede Dreaming-Phase bewirkt
    - Sie möchten die Konsolidierung abstimmen, ohne `MEMORY.md` zu verunreinigen
summary: Hintergrundkonsolidierung des Gedächtnisses mit leichten, tiefen und REM-Phasen sowie einem Traumtagebuch
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming ist das Hintergrundsystem zur Gedächtniskonsolidierung in `memory-core`.
Es hilft OpenClaw dabei, starke kurzfristige Signale in dauerhaftes Gedächtnis zu überführen, während
der Prozess nachvollziehbar und überprüfbar bleibt.

Dreaming ist **optional** und standardmäßig deaktiviert.

## Was Dreaming schreibt

Dreaming speichert zwei Arten von Ausgaben:

- **Maschinenstatus** in `memory/.dreams/` (Recall-Speicher, Phasensignale, Ingestion-Prüfpunkte, Sperren).
- **Menschenlesbare Ausgabe** in `DREAMS.md` (oder vorhandener `dreams.md`) und optionalen Phasenberichtdateien unter `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Die langfristige Überführung schreibt weiterhin nur in `MEMORY.md`.

## Phasenmodell

Dreaming verwendet drei kooperative Phasen:

| Phase | Zweck                                     | Dauerhafter Schreibvorgang |
| ----- | ----------------------------------------- | -------------------------- |
| Light | Aktuelles kurzfristiges Material sortieren und vorbereiten | Nein                       |
| Deep  | Dauerhafte Kandidaten bewerten und überführen | Ja (`MEMORY.md`)           |
| REM   | Über Themen und wiederkehrende Ideen reflektieren | Nein                       |

Diese Phasen sind interne Implementierungsdetails, keine separaten benutzerkonfigurierbaren
„Modi“.

### Light-Phase

Die Light-Phase nimmt aktuelle tägliche Gedächtnissignale und Recall-Spuren auf, dedupliziert sie
und bereitet Kandidatenzeilen vor.

- Liest aus dem kurzfristigen Recall-Status, aktuellen täglichen Gedächtnisdateien und redigierten Sitzungsprotokollen, wenn verfügbar.
- Schreibt einen verwalteten Block `## Light Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Zeichnet Verstärkungssignale für spätere Deep-Bewertung auf.
- Schreibt niemals in `MEMORY.md`.

### Deep-Phase

Die Deep-Phase entscheidet, was zum Langzeitgedächtnis wird.

- Bewertet Kandidaten mithilfe gewichteter Scores und Schwellenwerte.
- Erfordert, dass `minScore`, `minRecallCount` und `minUniqueQueries` erfüllt sind.
- Stellt Snippets vor dem Schreiben aus aktiven Tagesdateien wieder her, sodass veraltete/gelöschte Snippets übersprungen werden.
- Hängt überführte Einträge an `MEMORY.md` an.
- Schreibt eine Zusammenfassung `## Deep Sleep` in `DREAMS.md` und schreibt optional `memory/dreaming/deep/YYYY-MM-DD.md`.

### REM-Phase

Die REM-Phase extrahiert Muster und reflektierende Signale.

- Erstellt Themen- und Reflexionszusammenfassungen aus aktuellen kurzfristigen Spuren.
- Schreibt einen verwalteten Block `## REM Sleep`, wenn der Speicher Inline-Ausgabe enthält.
- Zeichnet REM-Verstärkungssignale auf, die bei der Deep-Bewertung verwendet werden.
- Schreibt niemals in `MEMORY.md`.

## Aufnahme von Sitzungsprotokollen

Dreaming kann redigierte Sitzungsprotokolle in den Dreaming-Korpus aufnehmen. Wenn
Protokolle verfügbar sind, werden sie zusammen mit täglichen
Gedächtnissignalen und Recall-Spuren in die Light-Phase eingespeist. Persönliche und sensible Inhalte werden vor
der Aufnahme redigiert.

## Traumtagebuch

Dreaming führt außerdem ein erzählerisches **Traumtagebuch** in `DREAMS.md`.
Sobald nach jeder Phase genügend Material vorhanden ist, führt `memory-core` im Hintergrund
einen Best-Effort-Subagent-Durchlauf aus (unter Verwendung des Standard-Laufzeitmodells) und hängt einen kurzen Tagebucheintrag an.

Dieses Tagebuch ist für Menschen zum Lesen in der Dreams-UI gedacht, nicht als Quelle für Überführungen.
Von Dreaming erzeugte Tagebuch-/Berichtsartefakte sind von der kurzfristigen
Überführung ausgeschlossen. Nur fundierte Gedächtnis-Snippets kommen für eine Überführung in
`MEMORY.md` infrage.

Es gibt außerdem einen fundierten historischen Backfill-Pfad für Prüf- und Wiederherstellungsarbeiten:

- `memory rem-harness --path ... --grounded` zeigt fundierte Tagebuchausgaben aus historischen Notizen `YYYY-MM-DD.md` als Vorschau an.
- `memory rem-backfill --path ...` schreibt reversible fundierte Tagebucheinträge in `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` stellt fundierte dauerhafte Kandidaten in denselben kurzfristigen Evidenzspeicher bereit, den die normale Deep-Phase bereits verwendet.
- `memory rem-backfill --rollback` und `--rollback-short-term` entfernen diese bereitgestellten Backfill-Artefakte, ohne gewöhnliche Tagebucheinträge oder aktiven kurzfristigen Recall zu berühren.

Die Control UI stellt denselben Backfill-/Zurücksetzen-Ablauf für das Tagebuch bereit, sodass Sie die
Ergebnisse in der Dreams-Szene prüfen können, bevor Sie entscheiden, ob die fundierten Kandidaten
eine Überführung verdienen. Die Szene zeigt außerdem einen separaten fundierten Pfad, damit Sie sehen können,
welche bereitgestellten kurzfristigen Einträge aus historischer Wiederholung stammen, welche überführten
Elemente fundiert geführt waren, und nur fundierte bereitgestellte Einträge löschen können, ohne
den gewöhnlichen aktiven kurzfristigen Status zu berühren.

## Deep-Bewertungssignale

Die Deep-Bewertung verwendet sechs gewichtete Basissignale plus Phasenverstärkung:

| Signal              | Gewicht | Beschreibung                                   |
| ------------------- | ------ | ---------------------------------------------- |
| Häufigkeit          | 0.24   | Wie viele kurzfristige Signale der Eintrag gesammelt hat |
| Relevanz            | 0.30   | Durchschnittliche Abrufqualität für den Eintrag |
| Abfragevielfalt     | 0.15   | Unterschiedliche Abfrage-/Tageskontexte, in denen er aufgetaucht ist |
| Aktualität          | 0.15   | Zeitlich abklingender Frische-Score            |
| Konsolidierung      | 0.10   | Stärke des mehrtägigen Wiederauftretens        |
| Konzeptioneller Reichtum | 0.06   | Dichte der Konzept-Tags aus Snippet/Pfad      |

Treffer in der Light- und REM-Phase fügen einen kleinen, nach Aktualität abklingenden Boost aus
`memory/.dreams/phase-signals.json` hinzu.

## Zeitplanung

Wenn aktiviert, verwaltet `memory-core` automatisch einen Cron-Job für einen vollständigen Dreaming-Durchlauf.
Jeder Durchlauf führt die Phasen der Reihe nach aus: light -> REM -> deep.

Standardverhalten für die Taktung:

| Einstellung         | Standard    |
| ------------------- | ----------- |
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

Dreaming mit einer benutzerdefinierten Durchlauf-Taktung aktivieren:

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

Verwenden Sie die CLI-Überführung für Vorschau oder manuelle Anwendung:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Das manuelle `memory promote` verwendet standardmäßig die Schwellenwerte der Deep-Phase, sofern sie nicht
mit CLI-Flags überschrieben werden.

Erklären, warum ein bestimmter Kandidat überführt würde oder nicht:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

REM-Reflexionen, Kandidatenwahrheiten und Deep-Überführungsausgabe in der Vorschau anzeigen, ohne
irgendetwas zu schreiben:

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

Die vollständige Liste der Schlüssel finden Sie unter [Referenz zur Gedächtniskonfiguration](/de/reference/memory-config#dreaming).

## Dreams-UI

Wenn aktiviert, zeigt der Gateway-Tab **Dreams** Folgendes an:

- aktuellen Dreaming-Aktivierungsstatus
- Status auf Phasenebene und Vorhandensein eines verwalteten Durchlaufs
- Zähler für kurzfristig, fundiert, Signal und heute überführt
- Zeitpunkt des nächsten geplanten Durchlaufs
- einen separaten fundierten Szenenpfad für bereitgestellte historische Wiederholungseinträge
- einen ausklappbaren Leser für das Traumtagebuch, der von `doctor.memory.dreamDiary` gestützt wird

## Verwandt

- [Gedächtnis](/de/concepts/memory)
- [Gedächtnissuche](/de/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Referenz zur Gedächtniskonfiguration](/de/reference/memory-config)
