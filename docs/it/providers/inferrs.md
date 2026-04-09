---
read_when:
    - Vuoi eseguire OpenClaw su un server inferrs locale
    - Stai servendo Gemma o un altro modello tramite inferrs
    - Hai bisogno degli esatti flag di compatibilità OpenClaw per inferrs
summary: Esegui OpenClaw tramite inferrs (server locale compatibile con OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-09T01:29:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 03b9d5a9935c75fd369068bacb7807a5308cd0bd74303b664227fb664c3a2098
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) può servire modelli locali dietro un'API
`/v1` compatibile con OpenAI. OpenClaw funziona con `inferrs` tramite il percorso generico
`openai-completions`.

Attualmente `inferrs` è meglio trattarlo come un backend personalizzato self-hosted compatibile con OpenAI,
non come un plugin provider OpenClaw dedicato.

## Avvio rapido

1. Avvia `inferrs` con un modello.

Esempio:

```bash
inferrs serve google/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. Verifica che il server sia raggiungibile.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. Aggiungi una voce provider OpenClaw esplicita e punta a essa il tuo modello predefinito.

## Esempio di configurazione completo

Questo esempio usa Gemma 4 su un server `inferrs` locale.

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

## Perché `requiresStringContent` è importante

Alcuni percorsi `inferrs` Chat Completions accettano solo
`messages[].content` stringa, non array strutturati di parti di contenuto.

Se le esecuzioni OpenClaw falliscono con un errore come:

```text
messages[1].content: invalid type: sequence, expected a string
```

imposta:

```json5
compat: {
  requiresStringContent: true
}
```

OpenClaw appiattirà le parti di contenuto di puro testo in stringhe semplici prima di inviare
la richiesta.

## Avvertenza su Gemma e sullo schema degli strumenti

Alcune combinazioni attuali di `inferrs` + Gemma accettano piccole richieste dirette
`/v1/chat/completions` ma falliscono comunque nei turni completi del runtime agente
di OpenClaw.

Se succede, prova prima questo:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

Questo disabilita la superficie dello schema degli strumenti di OpenClaw per il modello e può ridurre la pressione del prompt
sui backend locali più rigidi.

Se le piccole richieste dirette continuano a funzionare ma i normali turni agente OpenClaw continuano a
bloccarsi dentro `inferrs`, il problema residuo di solito riguarda il comportamento upstream del modello/server
più che il layer di transport di OpenClaw.

## Smoke test manuale

Una volta configurato, testa entrambi i layer:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/google/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

Se il primo comando funziona ma il secondo no, usa le note di risoluzione dei problemi
qui sotto.

## Risoluzione dei problemi

- `curl /v1/models` fallisce: `inferrs` non è in esecuzione, non è raggiungibile oppure non
  è associato all'host/porta previsti.
- `messages[].content ... expected a string`: imposta
  `compat.requiresStringContent: true`.
- Le piccole chiamate dirette `/v1/chat/completions` passano, ma `openclaw infer model run`
  fallisce: prova `compat.supportsTools: false`.
- OpenClaw non riceve più errori di schema, ma `inferrs` continua a bloccarsi su turni agente
  più grandi: trattalo come un limite upstream di `inferrs` o del modello e riduci
  la pressione del prompt oppure cambia backend/modello locale.

## Comportamento in stile proxy

`inferrs` viene trattato come un backend `/v1` compatibile con OpenAI in stile proxy, non come un
endpoint OpenAI nativo.

- il model shaping delle richieste nativo solo OpenAI non si applica qui
- niente `service_tier`, niente `store` di Responses, niente suggerimenti di prompt cache e nessun
  model shaping del payload di compatibilità con il reasoning di OpenAI
- gli header di attribuzione OpenClaw nascosti (`originator`, `version`, `User-Agent`)
  non vengono iniettati sui base URL `inferrs` personalizzati

## Vedi anche

- [Modelli locali](/it/gateway/local-models)
- [Risoluzione dei problemi del gateway](/it/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Provider di modelli](/it/concepts/model-providers)
