---
read_when:
    - Sie möchten eine zuverlässige Ausweichlösung, wenn API-Anbieter ausfallen
    - Sie verwenden Codex CLI oder andere lokale AI-CLIs und möchten sie wiederverwenden
    - Sie möchten die MCP-loopback-Bridge für den Tool-Zugriff des CLI-Backends verstehen
summary: 'CLI-Backends: lokale AI-CLI-Ausweichlösung mit optionaler MCP-Tool-Bridge'
title: CLI-Backends
x-i18n:
    generated_at: "2026-04-16T19:31:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# CLI-Backends (Ausweich-Runtime)

OpenClaw kann **lokale AI-CLIs** als **reine Text-Ausweichlösung** ausführen, wenn API-Anbieter ausgefallen sind,
ratelimited werden oder sich vorübergehend fehlerhaft verhalten. Das ist bewusst konservativ:

- **OpenClaw-Tools werden nicht direkt injiziert**, aber Backends mit `bundleMcp: true`
  können Gateway-Tools über eine loopback-MCP-Bridge empfangen.
- **JSONL-Streaming** für CLIs, die es unterstützen.
- **Sitzungen werden unterstützt** (damit Folgedurchläufe konsistent bleiben).
- **Bilder können durchgereicht werden**, wenn die CLI Bildpfade akzeptiert.

Dies ist als **Sicherheitsnetz** und nicht als primärer Pfad gedacht. Verwenden Sie es, wenn Sie
„funktioniert immer“-Textantworten möchten, ohne auf externe APIs angewiesen zu sein.

Wenn Sie eine vollständige Harness-Runtime mit ACP-Sitzungssteuerung, Hintergrundaufgaben,
Thread-/Konversationsbindung und persistenten externen Coding-Sitzungen benötigen, verwenden Sie
stattdessen [ACP Agents](/de/tools/acp-agents). CLI-Backends sind kein ACP.

## Einsteigerfreundlicher Schnellstart

Sie können Codex CLI **ohne Konfiguration** verwenden (das gebündelte OpenAI-Plugin
registriert ein Standard-Backend):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Wenn Ihr Gateway unter launchd/systemd läuft und PATH minimal ist, fügen Sie nur den
Befehlspfad hinzu:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

Das ist alles. Keine Schlüssel, keine zusätzliche Auth-Konfiguration erforderlich, außer der CLI selbst.

Wenn Sie ein gebündeltes CLI-Backend als **primären Nachrichtenanbieter** auf einem
Gateway-Host verwenden, lädt OpenClaw jetzt automatisch das zugehörige gebündelte Plugin, wenn Ihre Konfiguration
dieses Backend explizit in einer Modell-Referenz oder unter
`agents.defaults.cliBackends` referenziert.

## Verwendung als Ausweichlösung

Fügen Sie Ihrer Ausweichliste ein CLI-Backend hinzu, damit es nur ausgeführt wird, wenn primäre Modelle fehlschlagen:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Hinweise:

- Wenn Sie `agents.defaults.models` (Allowlist) verwenden, müssen Sie dort auch Ihre CLI-Backend-Modelle aufnehmen.
- Wenn der primäre Anbieter fehlschlägt (Authentifizierung, Ratenlimits, Timeouts), versucht OpenClaw
  als Nächstes das CLI-Backend.

## Konfigurationsüberblick

Alle CLI-Backends befinden sich unter:

```
agents.defaults.cliBackends
```

Jeder Eintrag ist über eine **Provider-ID** verschlüsselt (z. B. `codex-cli`, `my-cli`).
Die Provider-ID wird zur linken Seite Ihrer Modell-Referenz:

```
<provider>/<model>
```

### Beispielkonfiguration

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          // CLIs im Codex-Stil können stattdessen auf eine Prompt-Datei verweisen:
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## So funktioniert es

1. **Wählt ein Backend aus** basierend auf dem Provider-Präfix (`codex-cli/...`).
2. **Erstellt einen System-Prompt** mit demselben OpenClaw-Prompt + Workspace-Kontext.
3. **Führt die CLI aus** mit einer Sitzungs-ID (falls unterstützt), damit der Verlauf konsistent bleibt.
4. **Parst die Ausgabe** (JSON oder Klartext) und gibt den finalen Text zurück.
5. **Speichert Sitzungs-IDs** pro Backend, damit Folgedurchläufe dieselbe CLI-Sitzung wiederverwenden.

<Note>
Das gebündelte Anthropic-`claude-cli`-Backend wird wieder unterstützt. Anthropic-Mitarbeitende
haben uns mitgeteilt, dass die Nutzung von Claude CLI im OpenClaw-Stil wieder zulässig ist, daher behandelt OpenClaw
die Nutzung von `claude -p` für diese Integration als genehmigt, sofern Anthropic
keine neue Richtlinie veröffentlicht.
</Note>

Das gebündelte OpenAI-`codex-cli`-Backend übergibt den System-Prompt von OpenClaw über
die Codex-Konfigurationsüberschreibung `model_instructions_file` (`-c
model_instructions_file="..."`). Codex stellt kein Claude-ähnliches
Flag `--append-system-prompt` bereit, daher schreibt OpenClaw den zusammengesetzten Prompt
für jede neue Codex-CLI-Sitzung in eine temporäre Datei.

Das gebündelte Anthropic-`claude-cli`-Backend erhält den OpenClaw-Skills-Snapshot
auf zwei Wegen: den kompakten OpenClaw-Skills-Katalog im angehängten System-Prompt sowie
ein temporäres Claude-Code-Plugin, das mit `--plugin-dir` übergeben wird. Das Plugin enthält
nur die zulässigen Skills für diesen Agenten bzw. diese Sitzung, sodass der native Skill-Resolver von Claude Code
dieselbe gefilterte Menge sieht, die OpenClaw ansonsten im Prompt bewerben würde.
Skill-Umgebungs-/API-Key-Überschreibungen werden von OpenClaw weiterhin auf die
Umgebung des Child-Prozesses für den Lauf angewendet.

## Sitzungen

- Wenn die CLI Sitzungen unterstützt, setzen Sie `sessionArg` (z. B. `--session-id`) oder
  `sessionArgs` (Platzhalter `{sessionId}`), wenn die ID in mehrere Flags eingefügt
  werden muss.
- Wenn die CLI einen **Resume-Unterbefehl** mit anderen Flags verwendet, setzen Sie
  `resumeArgs` (ersetzt `args` beim Fortsetzen) und optional `resumeOutput`
  (für nicht-JSON-Resumes).
- `sessionMode`:
  - `always`: immer eine Sitzungs-ID senden (neue UUID, wenn keine gespeichert ist).
  - `existing`: nur dann eine Sitzungs-ID senden, wenn zuvor bereits eine gespeichert wurde.
  - `none`: niemals eine Sitzungs-ID senden.

Hinweise zur Serialisierung:

- `serialize: true` hält Läufe auf derselben Lane in geordneter Reihenfolge.
- Die meisten CLIs serialisieren auf einer Provider-Lane.
- OpenClaw verwirft die Wiederverwendung gespeicherter CLI-Sitzungen, wenn sich der Auth-Status des Backends ändert, einschließlich erneuter Anmeldung, Token-Rotation oder geänderter Zugangsdaten eines Auth-Profils.

## Bilder (Pass-through)

Wenn Ihre CLI Bildpfade akzeptiert, setzen Sie `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw schreibt base64-Bilder in temporäre Dateien. Wenn `imageArg` gesetzt ist, werden diese
Pfade als CLI-Argumente übergeben. Wenn `imageArg` fehlt, hängt OpenClaw die
Dateipfade an den Prompt an (Pfad-Injektion), was für CLIs ausreicht, die lokale
Dateien aus einfachen Pfaden automatisch laden.

## Ein- / Ausgaben

- `output: "json"` (Standard) versucht, JSON zu parsen und Text + Sitzungs-ID zu extrahieren.
- Für die JSON-Ausgabe von Gemini CLI liest OpenClaw Antworttext aus `response` und
  Nutzungsdaten aus `stats`, wenn `usage` fehlt oder leer ist.
- `output: "jsonl"` parst JSONL-Streams (zum Beispiel Codex CLI `--json`) und extrahiert die finale Agent-Nachricht sowie Sitzungs-
  Kennungen, sofern vorhanden.
- `output: "text"` behandelt stdout als finale Antwort.

Eingabemodi:

- `input: "arg"` (Standard) übergibt den Prompt als letztes CLI-Argument.
- `input: "stdin"` sendet den Prompt über stdin.
- Wenn der Prompt sehr lang ist und `maxPromptArgChars` gesetzt ist, wird stdin verwendet.

## Standards (plugin-eigen)

Das gebündelte OpenAI-Plugin registriert außerdem einen Standardwert für `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

Das gebündelte Google-Plugin registriert außerdem einen Standardwert für `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Voraussetzung: Die lokale Gemini CLI muss installiert und als
`gemini` auf `PATH` verfügbar sein (`brew install gemini-cli` oder
`npm install -g @google/gemini-cli`).

Hinweise zur Gemini-CLI-JSON-Ausgabe:

- Antworttext wird aus dem JSON-Feld `response` gelesen.
- Die Nutzung greift auf `stats` zurück, wenn `usage` fehlt oder leer ist.
- `stats.cached` wird zu OpenClaw-`cacheRead` normalisiert.
- Wenn `stats.input` fehlt, leitet OpenClaw Eingabe-Token aus
  `stats.input_tokens - stats.cached` ab.

Nur bei Bedarf überschreiben (üblich: absoluter `command`-Pfad).

## Plugin-eigene Standards

CLI-Backend-Standards sind jetzt Teil der Plugin-Oberfläche:

- Plugins registrieren sie mit `api.registerCliBackend(...)`.
- Die Backend-`id` wird zum Provider-Präfix in Modell-Referenzen.
- Benutzerkonfiguration unter `agents.defaults.cliBackends.<id>` überschreibt weiterhin den Plugin-Standard.
- Backend-spezifische Konfigurationsbereinigung bleibt über den optionalen
  Hook `normalizeConfig` plugin-eigen.

Plugins, die kleine Kompatibilitäts-Shims für Prompts/Nachrichten benötigen, können
bidirektionale Texttransformationen deklarieren, ohne einen Provider oder ein CLI-Backend zu ersetzen:

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

`input` schreibt den an die CLI übergebenen System-Prompt und Benutzer-Prompt um. `output`
schreibt gestreamte Assistant-Deltas und geparsten finalen Text um, bevor OpenClaw
seine eigenen Kontrollmarker und die Channel-Auslieferung verarbeitet.

Für CLIs, die mit Claude Code stream-json kompatibles JSONL ausgeben, setzen Sie
`jsonlDialect: "claude-stream-json"` in der Konfiguration dieses Backends.

## Bundle-MCP-Overlays

CLI-Backends erhalten **keine** direkten OpenClaw-Tool-Aufrufe, aber ein Backend kann
sich mit `bundleMcp: true` für ein generiertes MCP-Konfigurations-Overlay anmelden.

Aktuelles gebündeltes Verhalten:

- `claude-cli`: generierte strikte MCP-Konfigurationsdatei
- `codex-cli`: Inline-Konfigurationsüberschreibungen für `mcp_servers`
- `google-gemini-cli`: generierte Gemini-Systemeinstellungsdatei

Wenn Bundle MCP aktiviert ist, führt OpenClaw Folgendes aus:

- es startet einen loopback-HTTP-MCP-Server, der Gateway-Tools für den CLI-Prozess bereitstellt
- es authentifiziert die Bridge mit einem Token pro Sitzung (`OPENCLAW_MCP_TOKEN`)
- es begrenzt den Tool-Zugriff auf die aktuelle Sitzung sowie den Account- und Channel-Kontext
- es lädt aktivierte Bundle-MCP-Server für den aktuellen Workspace
- es führt sie mit einer vorhandenen backend-spezifischen MCP-Konfigurations-/Einstellungsstruktur zusammen
- es schreibt die Startkonfiguration mit dem backend-eigenen Integrationsmodus der zugehörigen Erweiterung um

Wenn keine MCP-Server aktiviert sind, injiziert OpenClaw dennoch eine strikte Konfiguration, wenn sich ein
Backend für Bundle MCP anmeldet, damit Hintergrundläufe isoliert bleiben.

## Einschränkungen

- **Keine direkten OpenClaw-Tool-Aufrufe.** OpenClaw injiziert keine Tool-Aufrufe in
  das CLI-Backend-Protokoll. Backends sehen Gateway-Tools nur dann, wenn sie sich für
  `bundleMcp: true` anmelden.
- **Streaming ist backend-spezifisch.** Manche Backends streamen JSONL, andere puffern
  bis zum Beenden.
- **Strukturierte Ausgaben** hängen vom JSON-Format der CLI ab.
- **Codex-CLI-Sitzungen** werden über Textausgabe fortgesetzt (kein JSONL), was weniger
  strukturiert ist als der anfängliche `--json`-Lauf. OpenClaw-Sitzungen funktionieren
  weiterhin normal.

## Fehlerbehebung

- **CLI nicht gefunden**: Setzen Sie `command` auf einen vollständigen Pfad.
- **Falscher Modellname**: Verwenden Sie `modelAliases`, um `provider/model` → CLI-Modell zuzuordnen.
- **Keine Sitzungskontinuität**: Stellen Sie sicher, dass `sessionArg` gesetzt ist und `sessionMode` nicht
  `none` ist (Codex CLI kann derzeit nicht mit JSON-Ausgabe fortsetzen).
- **Bilder werden ignoriert**: Setzen Sie `imageArg` (und prüfen Sie, ob die CLI Dateipfade unterstützt).
