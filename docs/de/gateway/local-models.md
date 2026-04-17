---
read_when:
    - Du möchtest Modelle von deiner eigenen GPU-Maschine bereitstellen.
    - Du richtest LM Studio oder einen OpenAI-kompatiblen Proxy ein.
    - Du benötigst die sicherste Anleitung für lokale Modelle.
summary: OpenClaw auf lokalen LLMs ausführen (LM Studio, vLLM, LiteLLM, benutzerdefinierte OpenAI-Endpunkte)
title: Lokale Modelle
x-i18n:
    generated_at: "2026-04-15T14:40:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# Lokale Modelle

Lokal ist machbar, aber OpenClaw erwartet großen Kontext und starke Abwehrmechanismen gegen Prompt-Injection. Kleine Grafikkarten beschneiden den Kontext und schwächen die Sicherheit. Setze hoch an: **≥2 voll ausgestattete Mac Studios oder ein vergleichbares GPU-System (~30.000 $+)**. Eine einzelne **24-GB**-GPU funktioniert nur für leichtere Prompts bei höherer Latenz. Verwende die **größte / vollwertige Modellvariante, die du ausführen kannst**; stark quantisierte oder „kleine“ Checkpoints erhöhen das Prompt-Injection-Risiko (siehe [Sicherheit](/de/gateway/security)).

Wenn du die lokale Einrichtung mit der geringsten Reibung möchtest, beginne mit [LM Studio](/de/providers/lmstudio) oder [Ollama](/de/providers/ollama) und `openclaw onboard`. Diese Seite ist der meinungsstarke Leitfaden für leistungsstärkere lokale Stacks und benutzerdefinierte OpenAI-kompatible lokale Server.

## Empfohlen: LM Studio + großes lokales Modell (Responses API)

Der derzeit beste lokale Stack. Lade ein großes Modell in LM Studio (zum Beispiel einen vollwertigen Qwen-, DeepSeek- oder Llama-Build), aktiviere den lokalen Server (Standard: `http://127.0.0.1:1234`) und verwende die Responses API, damit das Reasoning vom finalen Text getrennt bleibt.

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**Checkliste für die Einrichtung**

- Installiere LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- Lade in LM Studio den **größten verfügbaren Modell-Build** herunter (vermeide „small“-/stark quantisierte Varianten), starte den Server und bestätige, dass `http://127.0.0.1:1234/v1/models` ihn auflistet.
- Ersetze `my-local-model` durch die tatsächliche Modell-ID, die in LM Studio angezeigt wird.
- Halte das Modell geladen; Kaltstarts erhöhen die Startlatenz.
- Passe `contextWindow`/`maxTokens` an, wenn sich dein LM-Studio-Build unterscheidet.
- Für WhatsApp solltest du bei der Responses API bleiben, damit nur der finale Text gesendet wird.

Lass gehostete Modelle auch dann konfiguriert, wenn du lokal ausführst; verwende `models.mode: "merge"`, damit Fallbacks verfügbar bleiben.

### Hybride Konfiguration: gehostet als primär, lokal als Fallback

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### Lokal zuerst mit gehostetem Sicherheitsnetz

Tausche die Reihenfolge von primärem Modell und Fallback aus; behalte denselben Provider-Block und `models.mode: "merge"` bei, damit du auf Sonnet oder Opus zurückfallen kannst, wenn die lokale Maschine ausfällt.

### Regionales Hosting / Datenrouting

- Gehostete MiniMax-/Kimi-/GLM-Varianten gibt es auch auf OpenRouter mit regional festgelegten Endpunkten (z. B. in den USA gehostet). Wähle dort die regionale Variante, damit der Datenverkehr in deiner gewählten Jurisdiktion bleibt, und nutze weiterhin `models.mode: "merge"` für Anthropic-/OpenAI-Fallbacks.
- Nur lokal bleibt der stärkste Weg für Datenschutz; gehostetes regionales Routing ist der Mittelweg, wenn du Provider-Funktionen brauchst, aber den Datenfluss kontrollieren möchtest.

## Andere OpenAI-kompatible lokale Proxys

vLLM, LiteLLM, OAI-proxy oder benutzerdefinierte Gateways funktionieren, wenn sie einen OpenAI-artigen `/v1`-Endpunkt bereitstellen. Ersetze den obigen Provider-Block durch deinen Endpunkt und deine Modell-ID:

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Behalte `models.mode: "merge"` bei, damit gehostete Modelle als Fallbacks verfügbar bleiben.

Verhaltenshinweis für lokale/proxied `/v1`-Backends:

- OpenClaw behandelt diese als proxyartige OpenAI-kompatible Routen, nicht als native OpenAI-Endpunkte
- natives, nur für OpenAI geltendes Request-Shaping greift hier nicht: kein
  `service_tier`, kein Responses-`store`, kein OpenAI-Reasoning-kompatibles Payload-Shaping
  und keine Prompt-Cache-Hinweise
- versteckte OpenClaw-Attributions-Header (`originator`, `version`, `User-Agent`)
  werden auf diesen benutzerdefinierten Proxy-URLs nicht injiziert

Kompatibilitätshinweise für strengere OpenAI-kompatible Backends:

- Einige Server akzeptieren bei Chat Completions nur `messages[].content` als String, nicht
  strukturierte Content-Part-Arrays. Setze
  `models.providers.<provider>.models[].compat.requiresStringContent: true` für
  diese Endpunkte.
- Einige kleinere oder strengere lokale Backends sind mit der vollständigen
  Prompt-Form des OpenClaw-Agent-Runtimes instabil, insbesondere wenn Tool-Schemas enthalten sind. Wenn das
  Backend für kleine direkte `/v1/chat/completions`-Aufrufe funktioniert, aber bei normalen
  OpenClaw-Agent-Turns fehlschlägt, probiere zuerst
  `agents.defaults.experimental.localModelLean: true`, um schwergewichtige
  Standard-Tools wie `browser`, `cron` und `message` zu entfernen; dies ist ein experimentelles
  Flag, keine stabile Einstellung für den Standardmodus. Siehe
  [Experimentelle Funktionen](/de/concepts/experimental-features). Wenn das weiterhin fehlschlägt, versuche
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- Wenn das Backend weiterhin nur bei größeren OpenClaw-Läufen fehlschlägt, liegt das verbleibende Problem
  in der Regel an der Upstream-Modell-/Server-Kapazität oder an einem Backend-Fehler, nicht an der
  Transportebene von OpenClaw.

## Fehlerbehebung

- Kann Gateway den Proxy erreichen? `curl http://127.0.0.1:1234/v1/models`.
- Modell in LM Studio entladen? Lade es erneut; Kaltstart ist eine häufige Ursache für „Hängenbleiben“.
- OpenClaw warnt, wenn das erkannte Kontextfenster unter **32k** liegt, und blockiert unter **16k**. Wenn du auf diese Vorabprüfung triffst, erhöhe das Kontextlimit des Servers/Modells oder wähle ein größeres Modell.
- Kontextfehler? Verringere `contextWindow` oder erhöhe dein Serverlimit.
- OpenAI-kompatibler Server gibt `messages[].content ... expected a string` zurück?
  Füge `compat.requiresStringContent: true` bei diesem Modelleintrag hinzu.
- Kleine direkte `/v1/chat/completions`-Aufrufe funktionieren, aber `openclaw infer model run`
  schlägt bei Gemma oder einem anderen lokalen Modell fehl? Deaktiviere zuerst Tool-Schemas mit
  `compat.supportsTools: false` und teste dann erneut. Wenn der Server weiterhin nur
  bei größeren OpenClaw-Prompts abstürzt, behandle das als Einschränkung des Upstream-Servers/Modells.
- Sicherheit: Lokale Modelle überspringen providerseitige Filter; halte Agenten eng gefasst und Compaction aktiviert, um den Schadensradius von Prompt-Injection zu begrenzen.
