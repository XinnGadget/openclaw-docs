---
read_when:
    - Sie möchten OpenClaw gegen einen lokalen inferrs-Server ausführen
    - Sie stellen Gemma oder ein anderes Modell über inferrs bereit
    - Sie benötigen die genauen OpenClaw-Kompatibilitäts-Flags für inferrs
summary: OpenClaw über inferrs ausführen (OpenAI-kompatibler lokaler Server)
title: inferrs
x-i18n:
    generated_at: "2026-04-09T01:30:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 03b9d5a9935c75fd369068bacb7807a5308cd0bd74303b664227fb664c3a2098
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) kann lokale Modelle hinter einer
OpenAI-kompatiblen `/v1`-API bereitstellen. OpenClaw funktioniert mit `inferrs` über den generischen
Pfad `openai-completions`.

`inferrs` sollte derzeit am besten als benutzerdefiniertes selbstgehostetes
OpenAI-kompatibles Backend behandelt werden, nicht als dediziertes OpenClaw-Provider-Plugin.

## Schnellstart

1. Starten Sie `inferrs` mit einem Modell.

Beispiel:

```bash
inferrs serve google/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. Verifizieren Sie, dass der Server erreichbar ist.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. Fügen Sie einen expliziten OpenClaw-Provider-Eintrag hinzu und verweisen Sie Ihr Standardmodell darauf.

## Vollständiges Konfigurationsbeispiel

Dieses Beispiel verwendet Gemma 4 auf einem lokalen `inferrs`-Server.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Warum `requiresStringContent` wichtig ist

Einige `inferrs`-Chat-Completions-Routen akzeptieren nur String-Werte in
`messages[].content`, nicht strukturierte Inhalts-Arrays mit Content-Parts.

Wenn OpenClaw-Ausführungen mit einem Fehler wie diesem fehlschlagen:

```text
messages[1].content: invalid type: sequence, expected a string
```

setzen Sie:

```json5
compat: {
  requiresStringContent: true
}
```

OpenClaw reduziert dann reine Text-Content-Parts vor dem Senden der Anfrage auf einfache Strings.

## Gemma- und Tool-Schema-Einschränkung

Einige aktuelle Kombinationen aus `inferrs` und Gemma akzeptieren kleine direkte
`/v1/chat/completions`-Anfragen, schlagen aber trotzdem bei vollständigen OpenClaw-Agent-Runtime-
Turns fehl.

Wenn das passiert, versuchen Sie zuerst Folgendes:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

Dadurch wird die Tool-Schema-Oberfläche von OpenClaw für das Modell deaktiviert und der Prompt-Druck
auf strengeren lokalen Backends kann reduziert werden.

Wenn sehr kleine direkte Anfragen weiterhin funktionieren, normale OpenClaw-Agent-Turns aber in
`inferrs` weiterhin abstürzen, liegt das verbleibende Problem normalerweise eher am Upstream-Verhalten von Modell/Server als an der Transportebene von OpenClaw.

## Manueller Smoke-Test

Sobald alles konfiguriert ist, testen Sie beide Ebenen:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/google/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

Wenn der erste Befehl funktioniert, der zweite aber fehlschlägt, verwenden Sie die unten stehenden
Hinweise zur Fehlerbehebung.

## Fehlerbehebung

- `curl /v1/models` schlägt fehl: `inferrs` läuft nicht, ist nicht erreichbar oder
  nicht an den erwarteten Host/Port gebunden.
- `messages[].content ... expected a string`: setzen Sie
  `compat.requiresStringContent: true`.
- Direkte kleine `/v1/chat/completions`-Aufrufe funktionieren, aber `openclaw infer model run`
  schlägt fehl: versuchen Sie `compat.supportsTools: false`.
- OpenClaw erhält keine Schemafehler mehr, aber `inferrs` stürzt bei größeren
  Agent-Turns weiterhin ab: behandeln Sie es als Upstream-Einschränkung von `inferrs` oder des Modells und reduzieren Sie
  den Prompt-Druck oder wechseln Sie Backend/Modell.

## Proxy-artiges Verhalten

`inferrs` wird als proxy-artiges OpenAI-kompatibles `/v1`-Backend behandelt, nicht als
nativer OpenAI-Endpunkt.

- nur für natives OpenAI vorgesehene Anfrageformung gilt hier nicht
- kein `service_tier`, kein Responses-`store`, keine Prompt-Cache-Hinweise und keine
  OpenAI-Reasoning-Kompatibilitäts-Payload-Formung
- versteckte OpenClaw-Attributions-Header (`originator`, `version`, `User-Agent`)
  werden bei benutzerdefinierten `inferrs`-Basis-URLs nicht eingefügt

## Siehe auch

- [Local models](/de/gateway/local-models)
- [Gateway troubleshooting](/de/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Model providers](/de/concepts/model-providers)
