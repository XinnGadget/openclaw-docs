---
read_when:
    - Sie möchten verstehen, wie der Speicher funktioniert
    - Sie möchten wissen, welche Speicherdateien geschrieben werden sollen
summary: Wie OpenClaw sich Dinge sitzungsübergreifend merkt
title: Speicherübersicht
x-i18n:
    generated_at: "2026-04-15T14:40:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Speicherübersicht

OpenClaw merkt sich Dinge, indem es **einfache Markdown-Dateien** im Workspace Ihres Agenten schreibt. Das Modell „erinnert“ sich nur an das, was auf der Festplatte gespeichert wird -- es gibt keinen versteckten Zustand.

## So funktioniert es

Ihr Agent hat drei speicherbezogene Dateien:

- **`MEMORY.md`** -- Langzeitspeicher. Dauerhafte Fakten, Präferenzen und Entscheidungen. Wird zu Beginn jeder DM-Sitzung geladen.
- **`memory/YYYY-MM-DD.md`** -- tägliche Notizen. Laufender Kontext und Beobachtungen. Die Notizen von heute und gestern werden automatisch geladen.
- **`DREAMS.md`** (optional) -- Dream Diary und Zusammenfassungen von Dreaming-Durchläufen zur menschlichen Überprüfung, einschließlich fundierter historischer Backfill-Einträge.

Diese Dateien befinden sich im Agent-Workspace (Standard: `~/.openclaw/workspace`).

<Tip>
Wenn Sie möchten, dass Ihr Agent sich etwas merkt, sagen Sie es ihm einfach: „Merke dir, dass ich TypeScript bevorzuge.“ Er schreibt es in die passende Datei.
</Tip>

## Speicher-Tools

Der Agent verfügt über zwei Tools für die Arbeit mit Speicher:

- **`memory_search`** -- findet relevante Notizen mithilfe semantischer Suche, auch wenn die Formulierung vom Original abweicht.
- **`memory_get`** -- liest eine bestimmte Speicherdatei oder einen bestimmten Zeilenbereich.

Beide Tools werden vom aktiven Memory-Plugin bereitgestellt (Standard: `memory-core`).

## Begleit-Plugin Memory Wiki

Wenn sich dauerhafter Speicher eher wie eine gepflegte Wissensdatenbank als nur wie rohe Notizen verhalten soll, verwenden Sie das gebündelte Plugin `memory-wiki`.

`memory-wiki` kompiliert dauerhaftes Wissen in einen Wiki-Tresor mit:

- deterministischer Seitenstruktur
- strukturierten Aussagen und Belegen
- Widerspruchs- und Aktualitätsverfolgung
- generierten Dashboards
- kompilierten Übersichten für Agent-/Laufzeit-Consumer
- wiki-nativen Tools wie `wiki_search`, `wiki_get`, `wiki_apply` und `wiki_lint`

Es ersetzt nicht das aktive Memory-Plugin. Das aktive Memory-Plugin bleibt weiterhin für Abruf, Überführung und Dreaming zuständig. `memory-wiki` ergänzt daneben eine wissensschicht mit reicher Herkunftsnachverfolgbarkeit.

Siehe [Memory Wiki](/de/plugins/memory-wiki).

## Speichersuche

Wenn ein Embedding-Provider konfiguriert ist, verwendet `memory_search` **hybride Suche** -- eine Kombination aus Vektorähnlichkeit (semantische Bedeutung) und Schlüsselwortabgleich (exakte Begriffe wie IDs und Code-Symbole). Das funktioniert sofort, sobald Sie einen API-Schlüssel für einen unterstützten Provider haben.

<Info>
OpenClaw erkennt Ihren Embedding-Provider automatisch anhand verfügbarer API-Schlüssel. Wenn Sie einen OpenAI-, Gemini-, Voyage- oder Mistral-Schlüssel konfiguriert haben, ist die Speichersuche automatisch aktiviert.
</Info>

Einzelheiten dazu, wie die Suche funktioniert, zu Abstimmungsoptionen und zur Provider-Einrichtung finden Sie unter [Memory Search](/de/concepts/memory-search).

## Speicher-Backends

<CardGroup cols={3}>
<Card title="Integriert (Standard)" icon="database" href="/de/concepts/memory-builtin">
SQLite-basiert. Funktioniert sofort mit Schlüsselwortsuche, Vektorähnlichkeit und hybrider Suche. Keine zusätzlichen Abhängigkeiten.
</Card>
<Card title="QMD" icon="search" href="/de/concepts/memory-qmd">
Local-first-Sidecar mit Reranking, Query-Erweiterung und der Möglichkeit, Verzeichnisse außerhalb des Workspace zu indexieren.
</Card>
<Card title="Honcho" icon="brain" href="/de/concepts/memory-honcho">
KI-native sitzungsübergreifende Erinnerung mit Benutzermodellierung, semantischer Suche und Multi-Agent-Bewusstsein. Plugin-Installation.
</Card>
</CardGroup>

## Wissens-Wiki-Ebene

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/de/plugins/memory-wiki">
Kompiliert dauerhaften Speicher in einen Wiki-Tresor mit reichhaltiger Herkunftsnachverfolgbarkeit, mit Aussagen, Dashboards, Bridge-Modus und Obsidian-freundlichen Workflows.
</Card>
</CardGroup>

## Automatische Speicherleerung

Bevor [Compaction](/de/concepts/compaction) Ihre Unterhaltung zusammenfasst, führt OpenClaw einen stillen Turn aus, der den Agenten daran erinnert, wichtigen Kontext in Speicherdateien zu speichern. Dies ist standardmäßig aktiviert -- Sie müssen nichts konfigurieren.

<Tip>
Die Speicherleerung verhindert Kontextverlust während der Compaction. Wenn Ihr Agent wichtige Fakten in der Unterhaltung hat, die noch nicht in eine Datei geschrieben wurden, werden sie automatisch gespeichert, bevor die Zusammenfassung erfolgt.
</Tip>

## Dreaming

Dreaming ist ein optionaler Hintergrunddurchlauf zur Konsolidierung von Speicher. Dabei werden kurzfristige Signale gesammelt, Kandidaten bewertet und nur qualifizierte Elemente in den Langzeitspeicher (`MEMORY.md`) übernommen.

Es ist darauf ausgelegt, den Langzeitspeicher signalstark zu halten:

- **Opt-in**: standardmäßig deaktiviert.
- **Geplant**: wenn aktiviert, verwaltet `memory-core` automatisch einen wiederkehrenden Cron-Job für einen vollständigen Dreaming-Durchlauf.
- **Schwellenwertbasiert**: Übernahmen müssen Grenzwerte für Punktzahl, Abruffrequenz und Query-Diversität erfüllen.
- **Überprüfbar**: Phasenzusammenfassungen und Tagebucheinträge werden zur menschlichen Überprüfung in `DREAMS.md` geschrieben.

Weitere Informationen zum Phasenverhalten, zu Bewertungssignalen und zu Dream-Diary-Details finden Sie unter [Dreaming](/de/concepts/dreaming).

## Fundierter Backfill und Live-Überführung

Das Dreaming-System verfügt jetzt über zwei eng verwandte Prüfpfade:

- **Live Dreaming** arbeitet mit dem kurzfristigen Dreaming-Speicher unter `memory/.dreams/` und wird von der normalen Deep-Phase verwendet, wenn entschieden wird, was in `MEMORY.md` übernommen werden kann.
- **Fundierter Backfill** liest historische Notizen aus `memory/YYYY-MM-DD.md` als eigenständige Tagesdateien und schreibt strukturierte Prüfausgaben in `DREAMS.md`.

Fundierter Backfill ist nützlich, wenn Sie ältere Notizen erneut abspielen und prüfen möchten, was das System für dauerhaft hält, ohne `MEMORY.md` manuell zu bearbeiten.

Wenn Sie Folgendes verwenden:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

werden die fundierten dauerhaften Kandidaten nicht direkt übernommen. Sie werden in denselben kurzfristigen Dreaming-Speicher eingestuft, den die normale Deep-Phase bereits verwendet. Das bedeutet:

- `DREAMS.md` bleibt die Oberfläche für die menschliche Überprüfung.
- der kurzfristige Speicher bleibt die maschinenseitige Oberfläche für das Ranking.
- `MEMORY.md` wird weiterhin nur durch Deep-Überführung geschrieben.

Wenn Sie entscheiden, dass das erneute Abspielen nicht nützlich war, können Sie die eingestuften Artefakte entfernen, ohne gewöhnliche Tagebucheinträge oder den normalen Abrufzustand zu verändern:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Indexstatus und Provider prüfen
openclaw memory search "query"  # Über die Befehlszeile suchen
openclaw memory index --force   # Den Index neu aufbauen
```

## Weiterführende Informationen

- [Builtin Memory Engine](/de/concepts/memory-builtin) -- standardmäßiges SQLite-Backend
- [QMD Memory Engine](/de/concepts/memory-qmd) -- fortgeschrittener Local-first-Sidecar
- [Honcho Memory](/de/concepts/memory-honcho) -- KI-native sitzungsübergreifende Erinnerung
- [Memory Wiki](/de/plugins/memory-wiki) -- kompilierter Wissenstresor und wiki-native Tools
- [Memory Search](/de/concepts/memory-search) -- Suchpipeline, Provider und Abstimmung
- [Dreaming](/de/concepts/dreaming) -- Hintergrundüberführung
  vom kurzfristigen Abruf in den Langzeitspeicher
- [Referenz zur Speicherkonfiguration](/de/reference/memory-config) -- alle Konfigurationsoptionen
- [Compaction](/de/concepts/compaction) -- wie Compaction mit Speicher interagiert
