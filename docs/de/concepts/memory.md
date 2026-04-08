---
read_when:
    - Sie möchten verstehen, wie Speicher funktioniert
    - Sie möchten wissen, welche Speicherdateien geschrieben werden
summary: Wie OpenClaw sich Dinge sitzungsübergreifend merkt
title: Überblick über den Speicher
x-i18n:
    generated_at: "2026-04-08T06:01:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bb8552341b0b651609edaaae826a22fdc535d240aed4fad4af4b069454004af
    source_path: concepts/memory.md
    workflow: 15
---

# Überblick über den Speicher

OpenClaw merkt sich Dinge, indem **einfache Markdown-Dateien** im Workspace
Ihres Agenten geschrieben werden. Das Modell „erinnert“ sich nur an das, was
auf der Festplatte gespeichert wird – es gibt keinen versteckten Zustand.

## So funktioniert es

Ihr Agent hat drei speicherbezogene Dateien:

- **`MEMORY.md`** -- Langzeitspeicher. Dauerhafte Fakten, Präferenzen und
  Entscheidungen. Wird zu Beginn jeder DM-Sitzung geladen.
- **`memory/YYYY-MM-DD.md`** -- tägliche Notizen. Laufender Kontext und
  Beobachtungen. Die Notizen von heute und gestern werden automatisch geladen.
- **`DREAMS.md`** (experimentell, optional) -- Dream Diary und Zusammenfassungen
  von Dreaming-Durchläufen zur menschlichen Überprüfung.

Diese Dateien befinden sich im Agent-Workspace (standardmäßig `~/.openclaw/workspace`).

<Tip>
Wenn Sie möchten, dass sich Ihr Agent etwas merkt, bitten Sie ihn einfach darum: „Merke dir, dass ich
TypeScript bevorzuge.“ Er schreibt es in die passende Datei.
</Tip>

## Speicher-Tools

Der Agent verfügt über zwei Tools für die Arbeit mit Speicher:

- **`memory_search`** -- findet relevante Notizen mithilfe semantischer Suche,
  auch wenn die Formulierung vom Original abweicht.
- **`memory_get`** -- liest eine bestimmte Speicherdatei oder einen
  Zeilenbereich.

Beide Tools werden vom aktiven Speicher-Plugin bereitgestellt (standardmäßig: `memory-core`).

## Begleit-Plugin Memory Wiki

Wenn sich dauerhafter Speicher eher wie eine gepflegte Wissensdatenbank als
nur wie rohe Notizen verhalten soll, verwenden Sie das gebündelte Plugin `memory-wiki`.

`memory-wiki` kompiliert dauerhaftes Wissen in einen Wiki-Tresor mit:

- deterministischer Seitenstruktur
- strukturierten Aussagen und Belegen
- Verfolgung von Widersprüchen und Aktualität
- generierten Dashboards
- kompilierten Digests für Agent-/Runtime-Konsumenten
- wiki-nativen Tools wie `wiki_search`, `wiki_get`, `wiki_apply` und `wiki_lint`

Es ersetzt nicht das aktive Speicher-Plugin. Das aktive Speicher-Plugin ist
weiterhin für Abruf, Promotion und Dreaming zuständig. `memory-wiki` ergänzt es
um eine wissensbezogene Ebene mit Herkunftsnachweisen.

Siehe [Memory Wiki](/de/plugins/memory-wiki).

## Speichersuche

Wenn ein Embedding-Anbieter konfiguriert ist, verwendet `memory_search` eine
**hybride Suche** – eine Kombination aus Vektorähnlichkeit (semantische
Bedeutung) und Schlüsselwortabgleich (exakte Begriffe wie IDs und Codesymbole).
Das funktioniert sofort, sobald Sie einen API-Schlüssel für einen unterstützten
Anbieter haben.

<Info>
OpenClaw erkennt Ihren Embedding-Anbieter automatisch anhand verfügbarer API-Schlüssel. Wenn Sie
einen OpenAI-, Gemini-, Voyage- oder Mistral-Schlüssel konfiguriert haben, ist
die Speichersuche automatisch aktiviert.
</Info>

Ausführliche Informationen zur Funktionsweise der Suche, zu
Optimierungsoptionen und zur Einrichtung von Anbietern finden Sie unter
[Memory Search](/de/concepts/memory-search).

## Speicher-Backends

<CardGroup cols={3}>
<Card title="Integriert (Standard)" icon="database" href="/de/concepts/memory-builtin">
SQLite-basiert. Funktioniert sofort mit Schlüsselwortsuche, Vektorähnlichkeit und
hybrider Suche. Keine zusätzlichen Abhängigkeiten.
</Card>
<Card title="QMD" icon="search" href="/de/concepts/memory-qmd">
Lokaler Sidecar mit Reranking, Query-Erweiterung und der Möglichkeit,
Verzeichnisse außerhalb des Workspace zu indizieren.
</Card>
<Card title="Honcho" icon="brain" href="/de/concepts/memory-honcho">
KI-nativer sitzungsübergreifender Speicher mit Benutzermodellierung,
semantischer Suche und Multi-Agent-Bewusstsein. Plugin-Installation.
</Card>
</CardGroup>

## Wissens-Wiki-Ebene

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/de/plugins/memory-wiki">
Kompiliert dauerhaften Speicher in einen Wiki-Tresor mit Herkunftsnachweisen,
Dashboards, Bridge-Modus und Obsidian-freundlichen Workflows.
</Card>
</CardGroup>

## Automatische Speicherleerung

Bevor [Kompaktierung](/de/concepts/compaction) Ihre Unterhaltung zusammenfasst,
führt OpenClaw einen stillen Turn aus, der den Agenten daran erinnert, wichtigen
Kontext in Speicherdateien zu sichern. Dies ist standardmäßig aktiviert – Sie
müssen nichts konfigurieren.

<Tip>
Die Speicherleerung verhindert Kontextverlust während der Kompaktierung. Wenn Ihr Agent wichtige
Fakten in der Unterhaltung hat, die noch nicht in eine Datei geschrieben wurden,
werden sie automatisch gespeichert, bevor die Zusammenfassung erfolgt.
</Tip>

## Dreaming (experimentell)

Dreaming ist ein optionaler Hintergrunddurchlauf zur Konsolidierung von
Speicher. Dabei werden kurzfristige Signale gesammelt, Kandidaten bewertet und
nur qualifizierte Elemente in den Langzeitspeicher (`MEMORY.md`) übernommen.

Es soll dafür sorgen, dass der Langzeitspeicher ein starkes Signal-Rausch-Verhältnis behält:

- **Opt-in**: standardmäßig deaktiviert.
- **Geplant**: wenn aktiviert, verwaltet `memory-core` automatisch einen
  wiederkehrenden Cron-Job für einen vollständigen Dreaming-Durchlauf.
- **Schwellenwertbasiert**: Übernahmen müssen Grenzwerte für Bewertung,
  Abruffrequenz und Query-Diversität erfüllen.
- **Überprüfbar**: Phasenzusammenfassungen und Tagebucheinträge werden zur
  menschlichen Überprüfung in `DREAMS.md` geschrieben.

Informationen zum Phasenverhalten, zu Bewertungssignalen und Details zum Dream Diary finden Sie unter
[Dreaming (experimental)](/de/concepts/dreaming).

## CLI

```bash
openclaw memory status          # Check index status and provider
openclaw memory search "query"  # Search from the command line
openclaw memory index --force   # Rebuild the index
```

## Weiterführende Informationen

- [Builtin Memory Engine](/de/concepts/memory-builtin) -- standardmäßiges SQLite-Backend
- [QMD Memory Engine](/de/concepts/memory-qmd) -- fortgeschrittener lokaler Sidecar
- [Honcho Memory](/de/concepts/memory-honcho) -- KI-nativer sitzungsübergreifender Speicher
- [Memory Wiki](/de/plugins/memory-wiki) -- kompilierter Wissens-Tresor und wiki-native Tools
- [Memory Search](/de/concepts/memory-search) -- Suchpipeline, Anbieter und
  Optimierung
- [Dreaming (experimental)](/de/concepts/dreaming) -- Hintergrund-Promotion
  von kurzfristigem Abruf in den Langzeitspeicher
- [Referenz zur Speicherkonfiguration](/de/reference/memory-config) -- alle Konfigurationsoptionen
- [Kompaktierung](/de/concepts/compaction) -- wie Kompaktierung mit Speicher interagiert
