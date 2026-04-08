---
read_when:
    - Sie möchten dauerhaftes Wissen über einfache MEMORY.md-Notizen hinaus
    - Sie konfigurieren das gebündelte memory-wiki-Plugin
    - Sie möchten wiki_search, wiki_get oder den Bridge-Modus verstehen
summary: 'memory-wiki: kompilierter Wissensspeicher mit Herkunftsnachweisen, Claims, Dashboards und Bridge-Modus'
title: Memory Wiki
x-i18n:
    generated_at: "2026-04-08T06:01:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: b78dd6a4ef4451dae6b53197bf0c7c2a2ba846b08e4a3a93c1026366b1598d82
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Memory Wiki

`memory-wiki` ist ein gebündeltes Plugin, das dauerhaften Speicher in einen kompilierten Wissensspeicher verwandelt.

Es ersetzt **nicht** das aktive Speicher-Plugin. Das aktive Speicher-Plugin ist weiterhin für Recall, Promotion, Indizierung und Dreaming zuständig. `memory-wiki` steht daneben und kompiliert dauerhaftes Wissen in ein navigierbares Wiki mit deterministischen Seiten, strukturierten Claims, Herkunftsnachweisen, Dashboards und maschinenlesbaren Digests.

Verwenden Sie es, wenn sich Speicher eher wie eine gepflegte Wissensebene und weniger wie ein Haufen Markdown-Dateien verhalten soll.

## Was es hinzufügt

- Einen dedizierten Wiki-Speicher mit deterministischem Seitenlayout
- Strukturierte Claim- und Evidenzmetadaten statt nur Fließtext
- Herkunftsnachweise, Konfidenz, Widersprüche und offene Fragen auf Seitenebene
- Kompilierte Digests für Agenten- und Laufzeit-Consumer
- Wiki-native Search-/Get-/Apply-/Lint-Tools
- Optionalen Bridge-Modus, der öffentliche Artefakte aus dem aktiven Speicher-Plugin importiert
- Optionalen Obsidian-freundlichen Rendermodus und CLI-Integration

## Wie es mit Speicher zusammenpasst

Stellen Sie sich die Aufteilung so vor:

| Ebene                                                   | Zuständig für                                                                              |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Aktives Speicher-Plugin (`memory-core`, QMD, Honcho usw.) | Recall, semantische Suche, Promotion, Dreaming, Speicher-Laufzeit                          |
| `memory-wiki`                                           | Kompilierte Wiki-Seiten, Synthesen mit Herkunftsnachweisen, Dashboards, wiki-spezifische Search/Get/Apply |

Wenn das aktive Speicher-Plugin gemeinsame Recall-Artefakte bereitstellt, kann OpenClaw mit `memory_search corpus=all` beide Ebenen in einem Durchlauf durchsuchen.

Wenn Sie wiki-spezifisches Ranking, Herkunftsnachweise oder direkten Seitenzugriff benötigen, verwenden Sie stattdessen die wiki-nativen Tools.

## Speicher-Modi

`memory-wiki` unterstützt drei Speicher-Modi:

### `isolated`

Eigener Speicher, eigene Quellen, keine Abhängigkeit von `memory-core`.

Verwenden Sie diesen Modus, wenn das Wiki ein eigener kuratierter Wissensspeicher sein soll.

### `bridge`

Liest öffentliche Speicher-Artefakte und Speicher-Ereignisse aus dem aktiven Speicher-Plugin über öffentliche Plugin-SDK-Schnittstellen.

Verwenden Sie diesen Modus, wenn das Wiki die exportierten Artefakte des Speicher-Plugins kompilieren und organisieren soll, ohne auf private Plugin-Interna zuzugreifen.

Der Bridge-Modus kann Folgendes indizieren:

- exportierte Speicher-Artefakte
- Dreaming-Berichte
- tägliche Notizen
- Dateien im Speicher-Stammverzeichnis
- Speicher-Ereignisprotokolle

### `unsafe-local`

Expliziter Escape Hatch auf demselben Rechner für lokale private Pfade.

Dieser Modus ist absichtlich experimentell und nicht portabel. Verwenden Sie ihn nur, wenn Sie die Vertrauensgrenze verstehen und ausdrücklich lokalen Dateisystemzugriff benötigen, den der Bridge-Modus nicht bereitstellen kann.

## Speicher-Layout

Das Plugin initialisiert einen Speicher wie diesen:

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

Verwaltete Inhalte bleiben innerhalb generierter Blöcke. Von Menschen erstellte Notizblöcke bleiben erhalten.

Die wichtigsten Seitengruppen sind:

- `sources/` für importiertes Rohmaterial und Bridge-gestützte Seiten
- `entities/` für dauerhafte Dinge, Personen, Systeme, Projekte und Objekte
- `concepts/` für Ideen, Abstraktionen, Muster und Richtlinien
- `syntheses/` für kompilierte Zusammenfassungen und gepflegte Übersichten
- `reports/` für generierte Dashboards

## Strukturierte Claims und Evidenz

Seiten können strukturiertes `claims`-Frontmatter tragen, nicht nur Freitext.

Jeder Claim kann Folgendes enthalten:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

Evidenz-Einträge können Folgendes enthalten:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

Dadurch verhält sich das Wiki eher wie eine Überzeugungsebene als wie eine passive Notizablage. Claims können verfolgt, bewertet, angefochten und auf Quellen zurückgeführt werden.

## Kompilierungs-Pipeline

Der Kompilierungsschritt liest Wiki-Seiten, normalisiert Zusammenfassungen und erzeugt stabile, maschinenorientierte Artefakte unter:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Diese Digests existieren, damit Agenten und Laufzeitcode nicht Markdown-Seiten scrapen müssen.

Die kompilierte Ausgabe unterstützt außerdem:

- Wiki-Indizierung im ersten Durchlauf für Search/Get-Abläufe
- Claim-ID-Lookup zurück zu den besitzenden Seiten
- kompakte Prompt-Ergänzungen
- Generierung von Berichten/Dashboards

## Dashboards und Zustandsberichte

Wenn `render.createDashboards` aktiviert ist, pflegt die Kompilierung Dashboards unter `reports/`.

Integrierte Berichte umfassen:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Diese Berichte verfolgen Dinge wie:

- Cluster von Widerspruchsnotizen
- konkurrierende Claim-Cluster
- Claims ohne strukturierte Evidenz
- Seiten und Claims mit niedriger Konfidenz
- veraltete oder unbekannte Aktualität
- Seiten mit ungelösten Fragen

## Suche und Abruf

`memory-wiki` unterstützt zwei Such-Backends:

- `shared`: verwendet den gemeinsamen Speicher-Suchablauf, wenn verfügbar
- `local`: durchsucht das Wiki lokal

Es unterstützt außerdem drei Korpora:

- `wiki`
- `memory`
- `all`

Wichtiges Verhalten:

- `wiki_search` und `wiki_get` verwenden nach Möglichkeit kompilierte Digests als ersten Durchlauf
- Claim-IDs können zur besitzenden Seite aufgelöst werden
- umstrittene/veraltete/aktuelle Claims beeinflussen das Ranking
- Herkunftslabels können in die Ergebnisse übernommen werden

Praktische Regel:

- verwenden Sie `memory_search corpus=all` für einen breiten Recall-Durchlauf
- verwenden Sie `wiki_search` + `wiki_get`, wenn wiki-spezifisches Ranking, Herkunftsnachweise oder Seitenstrukturen für Überzeugungen wichtig sind

## Agenten-Tools

Das Plugin registriert diese Tools:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Was sie tun:

- `wiki_status`: aktueller Speicher-Modus, Zustand, Verfügbarkeit der Obsidian-CLI
- `wiki_search`: durchsucht Wiki-Seiten und, wenn konfiguriert, gemeinsame Speicher-Korpora
- `wiki_get`: liest eine Wiki-Seite nach ID/Pfad oder greift als Fallback auf das gemeinsame Speicher-Korpus zurück
- `wiki_apply`: enge Synthese-/Metadaten-Mutationen ohne freie Seitenbearbeitung
- `wiki_lint`: strukturelle Prüfungen, Lücken bei Herkunftsnachweisen, Widersprüche, offene Fragen

Das Plugin registriert außerdem eine nicht-exklusive Speicher-Korpus-Ergänzung, sodass gemeinsames `memory_search` und `memory_get` das Wiki erreichen können, wenn das aktive Speicher-Plugin Korpusauswahl unterstützt.

## Verhalten bei Prompt und Kontext

Wenn `context.includeCompiledDigestPrompt` aktiviert ist, hängen Speicher-Prompt-Abschnitte einen kompakten kompilierten Schnappschuss aus `agent-digest.json` an.

Dieser Schnappschuss ist absichtlich klein und signalstark:

- nur Top-Seiten
- nur Top-Claims
- Anzahl der Widersprüche
- Anzahl der Fragen
- Konfidenz-/Aktualitätsqualifikatoren

Dies ist optional, weil es die Prompt-Form verändert und hauptsächlich für Kontext-Engines oder ältere Prompt-Zusammenstellung nützlich ist, die Speicher-Ergänzungen ausdrücklich verwenden.

## Konfiguration

Legen Sie die Konfiguration unter `plugins.entries.memory-wiki.config` ab:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

Wichtige Schalter:

- `vaultMode`: `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode`: `native` oder `obsidian`
- `bridge.readMemoryArtifacts`: öffentliche Artefakte des aktiven Speicher-Plugins importieren
- `bridge.followMemoryEvents`: Ereignisprotokolle im Bridge-Modus einschließen
- `search.backend`: `shared` oder `local`
- `search.corpus`: `wiki`, `memory` oder `all`
- `context.includeCompiledDigestPrompt`: kompakten Digest-Schnappschuss an Speicher-Prompt-Abschnitte anhängen
- `render.createBacklinks`: deterministische Verwandt-Blöcke generieren
- `render.createDashboards`: Dashboard-Seiten generieren

## CLI

`memory-wiki` stellt außerdem eine Oberfläche der obersten Ebene in der CLI bereit:

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

Die vollständige Befehlsreferenz finden Sie unter [CLI: wiki](/cli/wiki).

## Obsidian-Unterstützung

Wenn `vault.renderMode` auf `obsidian` gesetzt ist, schreibt das Plugin Obsidian-freundliches Markdown und kann optional die offizielle `obsidian`-CLI verwenden.

Unterstützte Abläufe umfassen:

- Statusprüfung
- Speicher-Suche
- Öffnen einer Seite
- Aufrufen eines Obsidian-Befehls
- Sprung zur täglichen Notiz

Dies ist optional. Das Wiki funktioniert im nativen Modus auch ohne Obsidian.

## Empfohlener Workflow

1. Behalten Sie Ihr aktives Speicher-Plugin für Recall/Promotion/Dreaming.
2. Aktivieren Sie `memory-wiki`.
3. Beginnen Sie mit dem Modus `isolated`, sofern Sie nicht ausdrücklich den Bridge-Modus möchten.
4. Verwenden Sie `wiki_search` / `wiki_get`, wenn Herkunftsnachweise wichtig sind.
5. Verwenden Sie `wiki_apply` für enge Synthesen oder Metadatenaktualisierungen.
6. Führen Sie nach sinnvollen Änderungen `wiki_lint` aus.
7. Aktivieren Sie Dashboards, wenn Sie Sichtbarkeit für veraltete Inhalte/Widersprüche möchten.

## Verwandte Dokumentation

- [Memory Overview](/de/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Plugin SDK overview](/de/plugins/sdk-overview)
