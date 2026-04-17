---
read_when:
    - Sie ändern die Laufzeit oder das Harness-Register des eingebetteten Agenten
    - Sie registrieren ein Agent-Harness aus einem gebündelten oder vertrauenswürdigen Plugin
    - Sie müssen verstehen, wie sich das Codex-Plugin zu Modellanbietern verhält
sidebarTitle: Agent Harness
summary: Experimentelle SDK-Oberfläche für Plugins, die den Low-Level-Executor des eingebetteten Agenten ersetzen
title: Agent-Harness-Plugins
x-i18n:
    generated_at: "2026-04-12T00:18:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Agent-Harness-Plugins

Ein **Agent-Harness** ist der Low-Level-Executor für einen vorbereiteten OpenClaw-Agenten-Turn. Es ist kein Modellanbieter, kein Kanal und kein Tool-Register.

Verwenden Sie diese Oberfläche nur für gebündelte oder vertrauenswürdige native Plugins. Der Vertrag ist weiterhin experimentell, weil die Parametertypen absichtlich den aktuellen eingebetteten Runner widerspiegeln.

## Wann ein Harness verwendet werden sollte

Registrieren Sie ein Agent-Harness, wenn eine Modellfamilie eine eigene native Sitzungs-Laufzeit hat und der normale OpenClaw-Anbietertransport die falsche Abstraktion ist.

Beispiele:

- ein nativer Coding-Agent-Server, der Threads und Kompaktierung verwaltet
- eine lokale CLI oder ein Daemon, die bzw. der native Planungs-, Reasoning- und Tool-Ereignisse streamen muss
- eine Modell-Laufzeit, die zusätzlich zum OpenClaw-Sitzungstranskript eine eigene Resume-ID benötigt

Registrieren Sie **kein** Harness, nur um eine neue LLM-API hinzuzufügen. Für normale HTTP- oder WebSocket-Modell-APIs erstellen Sie ein [Anbieter-Plugin](/de/plugins/sdk-provider-plugins).

## Was der Core weiterhin verwaltet

Bevor ein Harness ausgewählt wird, hat OpenClaw bereits Folgendes aufgelöst:

- Anbieter und Modell
- Laufzeit-Authentifizierungsstatus
- Thinking-Level und Kontextbudget
- das OpenClaw-Transkript bzw. die Sitzungsdatei
- Workspace-, Sandbox- und Tool-Richtlinie
- Kanal-Antwort-Callbacks und Streaming-Callbacks
- Modell-Fallback- und Live-Modellwechsel-Richtlinie

Diese Aufteilung ist beabsichtigt. Ein Harness führt einen vorbereiteten Versuch aus; es wählt keine Anbieter aus, ersetzt nicht die Kanalauslieferung und wechselt nicht stillschweigend Modelle.

## Ein Harness registrieren

**Import:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Auswahlrichtlinie

OpenClaw wählt ein Harness nach der Anbieter-/Modellauflösung aus:

1. `OPENCLAW_AGENT_RUNTIME=<id>` erzwingt ein registriertes Harness mit dieser ID.
2. `OPENCLAW_AGENT_RUNTIME=pi` erzwingt das integrierte PI-Harness.
3. `OPENCLAW_AGENT_RUNTIME=auto` fragt registrierte Harnesses, ob sie den aufgelösten Anbieter/das aufgelöste Modell unterstützen.
4. Wenn kein registriertes Harness passt, verwendet OpenClaw PI, sofern der PI-Fallback nicht deaktiviert ist.

Fehler bei erzwungenen Plugin-Harnesses werden als Ausführungsfehler angezeigt. Im `auto`-Modus kann OpenClaw auf PI zurückfallen, wenn das ausgewählte Plugin-Harness fehlschlägt, bevor ein Turn Seiteneffekte erzeugt hat. Setzen Sie `OPENCLAW_AGENT_HARNESS_FALLBACK=none` oder `embeddedHarness.fallback: "none"`, damit dieser Fallback stattdessen ein harter Fehler ist.

Das gebündelte Codex-Plugin registriert `codex` als seine Harness-ID. Der Core behandelt dies als eine gewöhnliche Plugin-Harness-ID; Codex-spezifische Aliasse gehören in das Plugin oder die Operator-Konfiguration, nicht in den gemeinsamen Laufzeit-Selektor.

## Anbieter- plus Harness-Kopplung

Die meisten Harnesses sollten auch einen Anbieter registrieren. Der Anbieter macht Modell-Referenzen, Authentifizierungsstatus, Modellmetadaten und die `/model`-Auswahl für den Rest von OpenClaw sichtbar. Das Harness beansprucht dann diesen Anbieter in `supports(...)`.

Das gebündelte Codex-Plugin folgt diesem Muster:

- Anbieter-ID: `codex`
- Benutzer-Modell-Referenzen: `codex/gpt-5.4`, `codex/gpt-5.2` oder ein anderes Modell, das vom Codex-App-Server zurückgegeben wird
- Harness-ID: `codex`
- Authentifizierung: synthetische Anbieter-Verfügbarkeit, weil das Codex-Harness den nativen Codex-Login bzw. die native Codex-Sitzung verwaltet
- App-Server-Anfrage: OpenClaw sendet die reine Modell-ID an Codex und lässt das Harness mit dem nativen App-Server-Protokoll sprechen

Das Codex-Plugin ist additiv. Einfache `openai/gpt-*`-Referenzen bleiben OpenAI-Anbieter-Referenzen und verwenden weiterhin den normalen OpenClaw-Anbieterpfad. Wählen Sie `codex/gpt-*`, wenn Sie von Codex verwaltete Authentifizierung, Codex-Modellerkennung, native Threads und Codex-App-Server-Ausführung möchten. `/model` kann zwischen den vom Codex-App-Server zurückgegebenen Codex-Modellen wechseln, ohne OpenAI-Anbieter-Anmeldedaten zu erfordern.

Zur Operator-Einrichtung, zu Beispielen für Modellpräfixe und zu Codex-spezifischen Konfigurationen siehe [Codex-Harness](/de/plugins/codex-harness).

OpenClaw erfordert Codex-App-Server `0.118.0` oder neuer. Das Codex-Plugin prüft den Initialize-Handshake des App-Servers und blockiert ältere oder nicht versionierte Server, sodass OpenClaw nur gegen die Protokolloberfläche läuft, mit der es getestet wurde.

### Nativer Codex-Harness-Modus

Das gebündelte `codex`-Harness ist der native Codex-Modus für eingebettete OpenClaw-Agenten-Turns. Aktivieren Sie zuerst das gebündelte `codex`-Plugin und nehmen Sie `codex` in `plugins.allow` auf, wenn Ihre Konfiguration eine restriktive Allowlist verwendet. Es unterscheidet sich von `openai-codex/*`:

- `openai-codex/*` verwendet ChatGPT/Codex-OAuth über den normalen OpenClaw-Anbieterpfad.
- `codex/*` verwendet den gebündelten Codex-Anbieter und leitet den Turn über den Codex-App-Server.

Wenn dieser Modus ausgeführt wird, verwaltet Codex die native Thread-ID, das Resume-Verhalten, die Kompaktierung und die App-Server-Ausführung. OpenClaw verwaltet weiterhin den Chat-Kanal, den sichtbaren Transkript-Spiegel, die Tool-Richtlinie, Genehmigungen, Medienauslieferung und Sitzungsauswahl. Verwenden Sie `embeddedHarness.runtime: "codex"` mit `embeddedHarness.fallback: "none"`, wenn Sie nachweisen müssen, dass der Codex-App-Server-Pfad verwendet wird und ein PI-Fallback kein defektes natives Harness verdeckt.

## PI-Fallback deaktivieren

Standardmäßig führt OpenClaw eingebettete Agenten mit `agents.defaults.embeddedHarness` aus, das auf `{ runtime: "auto", fallback: "pi" }` gesetzt ist. Im `auto`-Modus können registrierte Plugin-Harnesses ein Anbieter-/Modell-Paar beanspruchen. Wenn keines passt oder wenn ein automatisch ausgewähltes Plugin-Harness fehlschlägt, bevor es Ausgabe erzeugt, fällt OpenClaw auf PI zurück.

Setzen Sie `fallback: "none"`, wenn Sie nachweisen müssen, dass ein Plugin-Harness die einzige verwendete Laufzeit ist. Dadurch wird der automatische PI-Fallback deaktiviert; ein explizites `runtime: "pi"` oder `OPENCLAW_AGENT_RUNTIME=pi` wird dadurch nicht blockiert.

Für eingebettete Codex-only-Ausführungen:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Wenn Sie möchten, dass jedes registrierte Plugin-Harness passende Modelle beanspruchen kann, aber nie wollen, dass OpenClaw stillschweigend auf PI zurückfällt, belassen Sie `runtime: "auto"` und deaktivieren Sie den Fallback:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Pro-Agent-Überschreibungen verwenden dieselbe Form:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` überschreibt weiterhin die konfigurierte Laufzeit. Verwenden Sie `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, um den PI-Fallback über die Umgebung zu deaktivieren.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Bei deaktiviertem Fallback schlägt eine Sitzung frühzeitig fehl, wenn das angeforderte Harness nicht registriert ist, den aufgelösten Anbieter/das aufgelöste Modell nicht unterstützt oder fehlschlägt, bevor Seiteneffekte des Turns erzeugt werden. Das ist für Codex-only-Bereitstellungen und für Live-Tests beabsichtigt, die nachweisen müssen, dass der Codex-App-Server-Pfad tatsächlich verwendet wird.

Diese Einstellung steuert nur das eingebettete Agent-Harness. Sie deaktiviert nicht bild-, video-, musik-, TTS-, PDF- oder anderes anbieterspezifisches Modell-Routing.

## Native Sitzungen und Transkript-Spiegel

Ein Harness kann eine native Sitzungs-ID, Thread-ID oder ein Daemon-seitiges Resume-Token beibehalten. Halten Sie diese Bindung explizit der OpenClaw-Sitzung zugeordnet, und spiegeln Sie weiterhin benutzersichtbare Assistenten-/Tool-Ausgaben in das OpenClaw-Transkript.

Das OpenClaw-Transkript bleibt die Kompatibilitätsschicht für:

- kanal-sichtbaren Sitzungsverlauf
- Transkript-Suche und -Indexierung
- das Zurückwechseln zum integrierten PI-Harness in einem späteren Turn
- generisches `/new`-, `/reset`- und Sitzungs-Löschverhalten

Wenn Ihr Harness eine Sidecar-Bindung speichert, implementieren Sie `reset(...)`, damit OpenClaw sie löschen kann, wenn die zugehörige OpenClaw-Sitzung zurückgesetzt wird.

## Tool- und Medienergebnisse

Der Core erstellt die OpenClaw-Tool-Liste und übergibt sie an den vorbereiteten Versuch. Wenn ein Harness einen dynamischen Tool-Aufruf ausführt, geben Sie das Tool-Ergebnis über die Ergebnisform des Harness zurück, statt Kanalmedien selbst zu senden.

Dadurch bleiben Text-, Bild-, Video-, Musik-, TTS-, Genehmigungs- und Messaging-Tool-Ausgaben auf demselben Auslieferungspfad wie bei PI-gestützten Ausführungen.

## Aktuelle Einschränkungen

- Der öffentliche Importpfad ist generisch, aber einige Typaliasse für Versuche/Ergebnisse tragen aus Kompatibilitätsgründen weiterhin `Pi`-Namen.
- Die Installation von Harnesses durch Dritte ist experimentell. Bevorzugen Sie Anbieter-Plugins, bis Sie eine native Sitzungs-Laufzeit benötigen.
- Das Wechseln von Harnesses zwischen Turns wird unterstützt. Wechseln Sie Harnesses nicht mitten in einem Turn, nachdem native Tools, Genehmigungen, Assistententext oder Nachrichtenversand begonnen haben.

## Verwandt

- [SDK-Überblick](/de/plugins/sdk-overview)
- [Laufzeit-Helfer](/de/plugins/sdk-runtime)
- [Anbieter-Plugins](/de/plugins/sdk-provider-plugins)
- [Codex-Harness](/de/plugins/codex-harness)
- [Modellanbieter](/de/concepts/model-providers)
