---
read_when:
    - Vuoi eseguire OpenClaw su un server inferrs locale
    - Stai servendo Gemma o un altro modello tramite inferrs
    - Hai bisogno dei flag di compatibilità esatti di OpenClaw per inferrs
summary: Esegui OpenClaw tramite inferrs (server locale compatibile con OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-08T02:17:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: d84f660d49a682d0c0878707eebe1bc1e83dd115850687076ea3938b9f9c86c6
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) può servire modelli locali dietro un'API
`/v1` compatibile con OpenAI. OpenClaw funziona con `inferrs` tramite il percorso generico
`openai-completions`.

Attualmente `inferrs` è trattato al meglio come backend personalizzato self-hosted compatibile con OpenAI,
non come un plugin provider dedicato di OpenClaw.

## Avvio rapido

1. Avvia `inferrs` con un modello.

Esempio:

```bash
inferrs serve gg-hf-gg/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. Verifica che il server sia raggiungibile.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. Aggiungi una voce provider OpenClaw esplicita e fai puntare a essa il tuo modello predefinito.

## Esempio completo di configurazione

Questo esempio usa Gemma 4 su un server `inferrs` locale.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/gg-hf-gg/gemma-4-E2B-it" },
      models: {
        "inferrs/gg-hf-gg/gemma-4-E2B-it": {
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
            id: "gg-hf-gg/gemma-4-E2B-it",
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

Alcuni percorsi Chat Completions di `inferrs` accettano solo
`messages[].content` come stringa, non array strutturati di parti di contenuto.

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

## Gemma e limitazione dello schema degli strumenti

Alcune combinazioni attuali di `inferrs` + Gemma accettano piccole richieste dirette
`/v1/chat/completions` ma continuano a fallire nei turni completi del runtime agent di OpenClaw.

Se succede, prova prima questo:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

Questo disabilita la superficie dello schema degli strumenti di OpenClaw per il modello e può ridurre la pressione del prompt
sui backend locali più rigidi.

Se richieste dirette molto piccole continuano a funzionare ma i normali turni agent di OpenClaw continuano a
andare in crash dentro `inferrs`, il problema rimanente è di solito un comportamento upstream del modello/server
più che del livello di trasporto di OpenClaw.

## Smoke test manuale

Una volta configurato, testa entrambi i livelli:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"gg-hf-gg/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/gg-hf-gg/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

Se il primo comando funziona ma il secondo fallisce, usa le note di risoluzione dei problemi
qui sotto.

## Risoluzione dei problemi

- `curl /v1/models` fallisce: `inferrs` non è in esecuzione, non è raggiungibile oppure non
  è associato all'host/porta previsti.
- `messages[].content ... expected a string`: imposta
  `compat.requiresStringContent: true`.
- Le piccole chiamate dirette a `/v1/chat/completions` passano, ma `openclaw infer model run`
  fallisce: prova `compat.supportsTools: false`.
- OpenClaw non riceve più errori di schema, ma `inferrs` continua ad andare in crash su turni
  agent più grandi: trattalo come una limitazione upstream di `inferrs` o del modello e riduci
  la pressione del prompt oppure cambia backend/modello locale.

## Comportamento in stile proxy

`inferrs` è trattato come backend `/v1` compatibile con OpenAI in stile proxy, non come
endpoint OpenAI nativo.

- qui non si applica la modellazione delle richieste solo OpenAI native
- niente `service_tier`, niente `store` di Responses, niente hint per la prompt-cache e nessuna
  modellazione del payload di compatibilità reasoning di OpenAI
- gli header di attribuzione nascosti di OpenClaw (`originator`, `version`, `User-Agent`)
  non vengono iniettati su URL base `inferrs` personalizzati

## Vedi anche

- [Modelli locali](/it/gateway/local-models)
- [Risoluzione dei problemi del gateway](/it/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Provider di modelli](/it/concepts/model-providers)
