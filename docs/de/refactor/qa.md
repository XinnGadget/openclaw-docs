---
x-i18n:
    generated_at: "2026-04-08T06:01:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# QA-Refaktorierung

Status: grundlegende Migration abgeschlossen.

## Ziel

QA in OpenClaw von einem Modell mit geteilten Definitionen zu einer einzigen
Quelle der Wahrheit verschieben:

- Szenario-Metadaten
- an das Modell gesendete Prompts
- Setup und Teardown
- Harness-Logik
- Assertions und Erfolgskriterien
- Artefakte und Hinweise für Berichte

Der gewünschte Endzustand ist ein generisches QA-Harness, das leistungsfähige
Szenario-Definitionsdateien lädt, anstatt den Großteil des Verhaltens in
TypeScript fest zu codieren.

## Aktueller Stand

Die primäre Quelle der Wahrheit liegt jetzt in `qa/scenarios/index.md` plus
einer Datei pro Szenario unter `qa/scenarios/*.md`.

Implementiert:

- `qa/scenarios/index.md`
  - kanonische Metadaten des QA-Pakets
  - Operator-Identität
  - Startmission
- `qa/scenarios/*.md`
  - eine Markdown-Datei pro Szenario
  - Szenario-Metadaten
  - Handler-Bindings
  - szenariospezifische Ausführungskonfiguration
- `extensions/qa-lab/src/scenario-catalog.ts`
  - Markdown-Paketparser + zod-Validierung
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - Plan-Rendering aus dem Markdown-Paket
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - erzeugt Kompatibilitätsdateien plus `QA_SCENARIOS.md`
- `extensions/qa-lab/src/suite.ts`
  - wählt ausführbare Szenarien über in Markdown definierte Handler-Bindings aus
- QA-Bus-Protokoll + UI
  - generische Inline-Anhänge für das Rendern von Bild/Video/Audio/Datei

Verbleibende geteilte Oberflächen:

- `extensions/qa-lab/src/suite.ts`
  - enthält weiterhin den Großteil der ausführbaren benutzerdefinierten Handler-Logik
- `extensions/qa-lab/src/report.ts`
  - leitet die Berichtsstruktur weiterhin aus Laufzeitausgaben ab

Damit ist die Aufteilung der Quelle der Wahrheit behoben, aber die Ausführung ist
weiterhin größtenteils handlergestützt statt vollständig deklarativ.

## Wie die echte Szenario-Oberfläche aussieht

Beim Lesen der aktuellen Suite zeigen sich einige unterschiedliche
Szenarioklassen.

### Einfache Interaktion

- Kanal-Basislinie
- DM-Basislinie
- Thread-Follow-up
- Modellwechsel
- Genehmigungs-Follow-through
- Reaktion/Bearbeiten/Löschen

### Konfigurations- und Laufzeitmutationen

- Skill-Deaktivierung per Config-Patch
- Weckvorgang bei Neustart nach Config-Anwendung
- Fähigkeitsumschaltung bei Config-Neustart
- Laufzeit-Inventardrift-Prüfung

### Dateisystem- und Repository-Assertions

- Quell-/Dokumentations-Discovery-Bericht
- Lobster Invaders bauen
- Suche nach generierten Bildartefakten

### Memory-Orchestrierung

- Memory-Abruf
- Memory-Tools im Kanalkontext
- Fallback bei Memory-Fehler
- Ranking von Sitzungs-Memory
- Isolation von Thread-Memory
- Memory-Dreaming-Durchlauf

### Tool- und Plugin-Integration

- MCP-Plugin-Tools-Aufruf
- Skill-Sichtbarkeit
- Skill-Hot-Install
- native Bildgenerierung
- Bild-Roundtrip
- Bildverständnis aus Anhang

### Multi-Turn und Multi-Akteur

- Subagent-Übergabe
- Subagent-Fanout-Synthese
- Stilflüsse für Wiederherstellung nach Neustart

Diese Kategorien sind wichtig, weil sie die DSL-Anforderungen bestimmen. Eine
flache Liste mit Prompt + erwartetem Text reicht nicht aus.

## Richtung

### Eine einzige Quelle der Wahrheit

`qa/scenarios/index.md` plus `qa/scenarios/*.md` als verfasste Quelle der
Wahrheit verwenden.

Das Paket sollte bleiben:

- für Reviews menschenlesbar
- maschinenlesbar
- reich genug, um Folgendes zu steuern:
  - Suite-Ausführung
  - Bootstrap des QA-Workspace
  - QA-Lab-UI-Metadaten
  - Dokumentations-/Discovery-Prompts
  - Berichtserstellung

### Bevorzugtes Authoring-Format

Markdown als Top-Level-Format mit strukturiertem YAML darin verwenden.

Empfohlene Form:

- YAML-Frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - Modell-/Provider-Überschreibungen
  - Voraussetzungen
- Prosa-Abschnitte
  - Ziel
  - Hinweise
  - Debugging-Hinweise
- abgegrenzte YAML-Blöcke
  - setup
  - steps
  - assertions
  - cleanup

Das bietet:

- bessere PR-Lesbarkeit als riesiges JSON
- mehr Kontext als reines YAML
- striktes Parsing und zod-Validierung

Rohes JSON ist nur als zwischengenerierte Form akzeptabel.

## Vorgeschlagene Form der Szenariodatei

Beispiel:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## Runner-Fähigkeiten, die die DSL abdecken muss

Basierend auf der aktuellen Suite benötigt der generische Runner mehr als nur
Prompt-Ausführung.

### Umgebungs- und Setup-Aktionen

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### Agent-Turn-Aktionen

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### Konfigurations- und Laufzeitaktionen

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### Datei- und Artefaktaktionen

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### Memory- und Cron-Aktionen

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### MCP-Aktionen

- `mcp.callTool`

### Assertions

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## Variablen und Artefakt-Referenzen

Die DSL muss gespeicherte Ausgaben und spätere Referenzen unterstützen.

Beispiele aus der aktuellen Suite:

- einen Thread erstellen und dann `threadId` wiederverwenden
- eine Sitzung erstellen und dann `sessionKey` wiederverwenden
- ein Bild generieren und die Datei dann im nächsten Turn anhängen
- eine Wake-Marker-Zeichenfolge erzeugen und dann prüfen, dass sie später erscheint

Benötigte Fähigkeiten:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- typisierte Referenzen für Pfade, Sitzungsschlüssel, Thread-IDs, Marker,
  Tool-Ausgaben

Ohne Variablenunterstützung wird die Harness-Szenariologik weiter zurück in
TypeScript auslaufen.

## Was als Escape Hatches bleiben sollte

Ein vollständig rein deklarativer Runner ist in Phase 1 nicht realistisch.

Einige Szenarien sind naturgemäß stark orchestrierungsorientiert:

- Memory-Dreaming-Durchlauf
- Weckvorgang bei Neustart nach Config-Anwendung
- Fähigkeitsumschaltung bei Config-Neustart
- Auflösung generierter Bildartefakte nach Zeitstempel/Pfad
- Auswertung von Discovery-Berichten

Diese sollten vorerst explizite benutzerdefinierte Handler verwenden.

Empfohlene Regel:

- 85–90 % deklarativ
- explizite `customHandler`-Schritte für den schwierigen Rest
- nur benannte und dokumentierte benutzerdefinierte Handler
- kein anonymer Inline-Code in der Szenariodatei

Das hält die generische Engine sauber und ermöglicht trotzdem Fortschritt.

## Architekturänderung

### Aktuell

Markdown für Szenarien ist bereits die Quelle der Wahrheit für:

- Suite-Ausführung
- Bootstrap-Dateien des Workspace
- Szenariokatalog der QA-Lab-UI
- Berichtsmetadaten
- Discovery-Prompts

Erzeugte Kompatibilität:

- der initialisierte Workspace enthält weiterhin `QA_KICKOFF_TASK.md`
- der initialisierte Workspace enthält weiterhin `QA_SCENARIO_PLAN.md`
- der initialisierte Workspace enthält jetzt zusätzlich `QA_SCENARIOS.md`

## Refaktorierungsplan

### Phase 1: Loader und Schema

Erledigt.

- `qa/scenarios/index.md` hinzugefügt
- Szenarien in `qa/scenarios/*.md` aufgeteilt
- Parser für benannten Markdown-YAML-Paketinhalt hinzugefügt
- mit zod validiert
- Consumer auf das geparste Paket umgestellt
- `qa/seed-scenarios.json` und `qa/QA_KICKOFF_TASK.md` auf Repository-Ebene entfernt

### Phase 2: generische Engine

- `extensions/qa-lab/src/suite.ts` aufteilen in:
  - Loader
  - Engine
  - Aktions-Registry
  - Assertion-Registry
  - benutzerdefinierte Handler
- vorhandene Hilfsfunktionen als Engine-Operationen beibehalten

Ergebnis:

- Engine führt einfache deklarative Szenarien aus

Mit Szenarien beginnen, die größtenteils Prompt + Warten + Assertion sind:

- Thread-Follow-up
- Bildverständnis aus Anhang
- Skill-Sichtbarkeit und -Aufruf
- Kanal-Basislinie

Ergebnis:

- erste echte markdowndefinierte Szenarien, die über die generische Engine ausgeliefert werden

### Phase 4: mittlere Szenarien migrieren

- Bildgenerierungs-Roundtrip
- Memory-Tools im Kanalkontext
- Ranking von Sitzungs-Memory
- Subagent-Übergabe
- Subagent-Fanout-Synthese

Ergebnis:

- Variablen, Artefakte, Tool-Assertions und Request-Log-Assertions praktisch belegt

### Phase 5: schwierige Szenarien auf benutzerdefinierten Handlern belassen

- Memory-Dreaming-Durchlauf
- Weckvorgang bei Neustart nach Config-Anwendung
- Fähigkeitsumschaltung bei Config-Neustart
- Laufzeit-Inventardrift

Ergebnis:

- gleiches Authoring-Format, aber bei Bedarf mit expliziten
  benutzerdefinierten Step-Blöcken

### Phase 6: hartcodierte Szenario-Map löschen

Sobald die Paketabdeckung gut genug ist:

- den Großteil des szenariospezifischen TypeScript-Branchings aus `extensions/qa-lab/src/suite.ts` entfernen

## Fake-Slack- / Rich-Media-Unterstützung

Der aktuelle QA-Bus ist textorientiert.

Relevante Dateien:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Heute unterstützt der QA-Bus:

- Text
- Reaktionen
- Threads

Inline-Medienanhänge werden noch nicht modelliert.

### Benötigter Transportvertrag

Ein generisches QA-Bus-Anhangsmodell hinzufügen:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

Dann `attachments?: QaBusAttachment[]` hinzufügen zu:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### Warum zuerst generisch

Kein nur für Slack bestimmtes Medienmodell bauen.

Stattdessen:

- ein generisches QA-Transportmodell
- mehrere Renderer darauf aufbauend
  - aktueller QA-Lab-Chat
  - zukünftiges Fake-Slack-Web
  - beliebige andere Fake-Transportansichten

Das verhindert doppelte Logik und sorgt dafür, dass Medienszenarien
transportagnostisch bleiben.

### Erforderliche UI-Arbeit

Die QA-UI so aktualisieren, dass sie Folgendes rendert:

- Inline-Bildvorschau
- Inline-Audioplayer
- Inline-Videoplayer
- Dateianhang-Chip

Die aktuelle UI kann bereits Threads und Reaktionen rendern, daher sollte das
Rendern von Anhängen auf dasselbe Nachrichtenkartenmodell aufsetzen.

### Durch Medientransport ermöglichte Szenarioarbeit

Sobald Anhänge durch den QA-Bus fließen, können wir reichhaltigere
Fake-Chat-Szenarien hinzufügen:

- Inline-Bildantwort in Fake Slack
- Verständnis von Audioanhängen
- Verständnis von Videoanhängen
- gemischte Anhangsreihenfolge
- Thread-Antwort mit beibehaltenen Medien

## Empfehlung

Der nächste Implementierungsblock sollte sein:

1. Markdown-Szenario-Loader + zod-Schema hinzufügen
2. den aktuellen Katalog aus Markdown erzeugen
3. zuerst einige einfache Szenarien migrieren
4. generische QA-Bus-Anhangsunterstützung hinzufügen
5. Inline-Bild in der QA-UI rendern
6. dann auf Audio und Video erweitern

Das ist der kleinste Weg, der beide Ziele belegt:

- generische markdowndefinierte QA
- reichhaltigere Fake-Messaging-Oberflächen

## Offene Fragen

- ob Szenariodateien eingebettete Markdown-Prompt-Templates mit
  Variableninterpolation erlauben sollten
- ob Setup/Cleanup benannte Abschnitte oder einfach geordnete Aktionslisten
  sein sollten
- ob Artefakt-Referenzen im Schema stark typisiert oder zeichenfolgenbasiert
  sein sollten
- ob benutzerdefinierte Handler in einer Registry oder in Registries pro
  Oberfläche liegen sollten
- ob die generierte JSON-Kompatibilitätsdatei während der Migration weiterhin
  eingecheckt bleiben sollte
