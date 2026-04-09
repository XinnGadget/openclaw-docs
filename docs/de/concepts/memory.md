---
read_when:
    - Sie möchten verstehen, wie der Speicher funktioniert
    - Sie möchten wissen, welche Speicherdateien geschrieben werden
summary: Wie OpenClaw Dinge sitzungsübergreifend behält
title: Überblick über den Speicher
x-i18n:
    generated_at: "2026-04-09T01:27:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2fe47910f5bf1c44be379e971c605f1cb3a29befcf2a7ee11fb3833cbe3b9059
    source_path: concepts/memory.md
    workflow: 15
---

# Überblick über den Speicher

OpenClaw merkt sich Dinge, indem es **einfache Markdown-Dateien** im Workspace
Ihres Agenten schreibt. Das Modell „erinnert“ sich nur an das, was auf der
Festplatte gespeichert wird – es gibt keinen verborgenen Zustand.

## So funktioniert es

Ihr Agent verfügt über drei speicherbezogene Dateien:

- **`MEMORY.md`** – Langzeitspeicher. Dauerhafte Fakten, Präferenzen und
  Entscheidungen. Wird zu Beginn jeder DM-Sitzung geladen.
- **`memory/YYYY-MM-DD.md`** – tägliche Notizen. Laufender Kontext und
  Beobachtungen. Die Notizen von heute und gestern werden automatisch geladen.
- **`DREAMS.md`** (experimentell, optional) – Traumtagebuch und
  Zusammenfassungen der Dreaming-Durchläufe zur menschlichen Überprüfung,
  einschließlich fundierter historischer Backfill-Einträge.

Diese Dateien befinden sich im Agent-Workspace (standardmäßig `~/.openclaw/workspace`).

<Tip>
Wenn Sie möchten, dass sich Ihr Agent etwas merkt, sagen Sie es ihm einfach:
„Merke dir, dass ich TypeScript bevorzuge.“ Er schreibt es in die passende
Datei.
</Tip>

## Speicher-Tools

Der Agent hat zwei Tools für die Arbeit mit Speicher:

- **`memory_search`** – findet relevante Notizen mithilfe semantischer Suche,
  auch wenn die Formulierung vom Original abweicht.
- **`memory_get`** – liest eine bestimmte Speicherdatei oder einen
  Zeilenbereich.

Beide Tools werden vom aktiven Speicher-Plugin bereitgestellt
(Standard: `memory-core`).

## Begleit-Plugin „Memory Wiki“

Wenn sich dauerhafter Speicher eher wie eine gepflegte Wissensdatenbank als
nur wie rohe Notizen verhalten soll, verwenden Sie das gebündelte Plugin
`memory-wiki`.

`memory-wiki` kompiliert dauerhaftes Wissen in einen Wiki-Vault mit:

- deterministischer Seitenstruktur
- strukturierten Aussagen und Belegen
- Verfolgung von Widersprüchen und Aktualität
- generierten Dashboards
- kompilierten Digests für Agent-/Runtime-Konsumenten
- wiki-nativen Tools wie `wiki_search`, `wiki_get`, `wiki_apply` und `wiki_lint`

Es ersetzt nicht das aktive Speicher-Plugin. Das aktive Speicher-Plugin ist
weiterhin für Abruf, Promotion und Dreaming zuständig. `memory-wiki` fügt
daneben eine wissensreiche Ebene mit Herkunftsnachweisen hinzu.

Siehe [Memory Wiki](/de/plugins/memory-wiki).

## Speichersuche

Wenn ein Embedding-Provider konfiguriert ist, verwendet `memory_search` eine
**hybride Suche** – eine Kombination aus Vektorähnlichkeit (semantische
Bedeutung) und Schlüsselwortabgleich (exakte Begriffe wie IDs und Codesymbole).
Das funktioniert sofort, sobald Sie einen API-Schlüssel für einen
unterstützten Provider haben.

<Info>
OpenClaw erkennt Ihren Embedding-Provider automatisch anhand verfügbarer
API-Schlüssel. Wenn Sie einen konfigurierten Schlüssel für OpenAI, Gemini,
Voyage oder Mistral haben, wird die Speichersuche automatisch aktiviert.
</Info>

Einzelheiten dazu, wie die Suche funktioniert, zu Abstimmungsoptionen und zur
Provider-Einrichtung finden Sie unter
[Memory Search](/de/concepts/memory-search).

## Speicher-Backends

<CardGroup cols={3}>
<Card title="Integriert (Standard)" icon="database" href="/de/concepts/memory-builtin">
SQLite-basiert. Funktioniert sofort mit Schlüsselwortsuche, Vektorähnlichkeit
und hybrider Suche. Keine zusätzlichen Abhängigkeiten.
</Card>
<Card title="QMD" icon="search" href="/de/concepts/memory-qmd">
Lokaler Sidecar mit Reranking, Query-Erweiterung und der Möglichkeit,
Verzeichnisse außerhalb des Workspace zu indizieren.
</Card>
<Card title="Honcho" icon="brain" href="/de/concepts/memory-honcho">
KI-nativer sitzungsübergreifender Speicher mit Benutzermodellierung,
semantischer Suche und Multi-Agent-Unterstützung. Plugin-Installation.
</Card>
</CardGroup>

## Wissens-Wiki-Ebene

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/de/plugins/memory-wiki">
Kompiliert dauerhaften Speicher in einen herkunftsreichen Wiki-Vault mit
Aussagen, Dashboards, Bridge-Modus und Obsidian-freundlichen Workflows.
</Card>
</CardGroup>

## Automatische Speicherleerung

Bevor [Kompaktierung](/de/concepts/compaction) Ihre Unterhaltung zusammenfasst,
führt OpenClaw einen stillen Turn aus, der den Agenten daran erinnert,
wichtigen Kontext in Speicherdateien zu speichern. Dies ist standardmäßig
aktiviert – Sie müssen nichts konfigurieren.

<Tip>
Die Speicherleerung verhindert Kontextverlust während der Kompaktierung. Wenn
Ihr Agent wichtige Fakten in der Unterhaltung hat, die noch nicht in eine Datei
geschrieben wurden, werden sie automatisch gespeichert, bevor die
Zusammenfassung erfolgt.
</Tip>

## Dreaming (experimentell)

Dreaming ist ein optionaler Hintergrunddurchlauf zur Konsolidierung von
Speicher. Es sammelt kurzfristige Signale, bewertet Kandidaten und überführt nur
qualifizierte Elemente in den Langzeitspeicher (`MEMORY.md`).

Es wurde entwickelt, um den Langzeitspeicher signalstark zu halten:

- **Opt-in**: standardmäßig deaktiviert.
- **Geplant**: wenn aktiviert, verwaltet `memory-core` automatisch einen
  wiederkehrenden Cron-Job für einen vollständigen Dreaming-Durchlauf.
- **Schwellenwertbasiert**: Promotions müssen Gates für Punktzahl,
  Abruffrequenz und Abfragevielfalt bestehen.
- **Überprüfbar**: Phasenzusammenfassungen und Tagebucheinträge werden zur
  menschlichen Überprüfung in `DREAMS.md` geschrieben.

Details zum Phasenverhalten, zu Bewertungssignalen und zum Traumtagebuch finden
Sie unter [Dreaming (experimental)](/de/concepts/dreaming).

## Fundiertes Backfill und Live-Promotion

Das Dreaming-System hat jetzt zwei eng verwandte Überprüfungspfade:

- **Live Dreaming** arbeitet mit dem kurzfristigen Dreaming-Speicher unter
  `memory/.dreams/` und wird von der normalen tiefen Phase verwendet, wenn
  entschieden wird, was in `MEMORY.md` übernommen werden kann.
- **Fundiertes Backfill** liest historische Notizen aus
  `memory/YYYY-MM-DD.md` als eigenständige Tagesdateien und schreibt
  strukturierten Überprüfungsausgabe in `DREAMS.md`.

Fundiertes Backfill ist nützlich, wenn Sie ältere Notizen erneut durchlaufen und
prüfen möchten, was das System für dauerhaft hält, ohne `MEMORY.md` manuell zu
bearbeiten.

Wenn Sie Folgendes verwenden:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

werden die fundierten dauerhaften Kandidaten nicht direkt übernommen. Sie werden
in denselben kurzfristigen Dreaming-Speicher eingestuft, den die normale tiefe
Phase bereits verwendet. Das bedeutet:

- `DREAMS.md` bleibt die Oberfläche für die menschliche Überprüfung.
- der kurzfristige Speicher bleibt die maschinenseitige Oberfläche für das Ranking.
- `MEMORY.md` wird weiterhin nur durch tiefe Promotion geschrieben.

Wenn Sie entscheiden, dass die Wiederholung nicht nützlich war, können Sie die
bereitgestellten Artefakte entfernen, ohne gewöhnliche Tagebucheinträge oder den
normalen Abrufstatus zu berühren:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Indexstatus und Provider prüfen
openclaw memory search "query"  # Über die Befehlszeile suchen
openclaw memory index --force   # Den Index neu erstellen
```

## Weiterführende Informationen

- [Builtin Memory Engine](/de/concepts/memory-builtin) – Standard-Backend mit SQLite
- [QMD Memory Engine](/de/concepts/memory-qmd) – erweiterter lokaler Sidecar
- [Honcho Memory](/de/concepts/memory-honcho) – KI-nativer sitzungsübergreifender Speicher
- [Memory Wiki](/de/plugins/memory-wiki) – kompilierter Wissens-Vault und wiki-native Tools
- [Memory Search](/de/concepts/memory-search) – Suchpipeline, Provider und
  Abstimmung
- [Dreaming (experimental)](/de/concepts/dreaming) – Hintergrund-Promotion
  vom kurzfristigen Abruf in den Langzeitspeicher
- [Referenz zur Speicherkonfiguration](/de/reference/memory-config) – alle Konfigurationsoptionen
- [Kompaktierung](/de/concepts/compaction) – wie Kompaktierung mit Speicher interagiert
