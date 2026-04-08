---
read_when:
    - Vuoi servire modelli dal tuo box GPU personale
    - Stai configurando LM Studio o un proxy compatibile con OpenAI
    - Hai bisogno della guida più sicura per i modelli locali
summary: Esegui OpenClaw su LLM locali (LM Studio, vLLM, LiteLLM, endpoint OpenAI personalizzati)
title: Modelli locali
x-i18n:
    generated_at: "2026-04-08T02:14:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: d619d72b0e06914ebacb7e9f38b746caf1b9ce8908c9c6638c3acdddbaa025e8
    source_path: gateway/local-models.md
    workflow: 15
---

# Modelli locali

Il locale è fattibile, ma OpenClaw si aspetta un contesto ampio e forti difese contro il prompt injection. Le schede più piccole troncano il contesto e indeboliscono la sicurezza. Punta in alto: **≥2 Mac Studio al massimo della configurazione o una configurazione GPU equivalente (~$30k+)**. Una singola GPU da **24 GB** funziona solo con prompt più leggeri e con latenza più elevata. Usa la **variante di modello più grande / completa che riesci a eseguire**; checkpoint fortemente quantizzati o “small” aumentano il rischio di prompt injection (vedi [Sicurezza](/it/gateway/security)).

Se vuoi la configurazione locale con meno attrito, inizia con [Ollama](/it/providers/ollama) e `openclaw onboard`. Questa pagina è la guida con indicazioni precise per stack locali di fascia più alta e server locali personalizzati compatibili con OpenAI.

## Consigliato: LM Studio + modello locale grande (Responses API)

Il miglior stack locale attuale. Carica un modello grande in LM Studio (ad esempio, una build completa di Qwen, DeepSeek o Llama), abilita il server locale (predefinito `http://127.0.0.1:1234`) e usa Responses API per mantenere il ragionamento separato dal testo finale.

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

**Checklist di configurazione**

- Installa LM Studio: [https://lmstudio.ai](https://lmstudio.ai)
- In LM Studio, scarica la **build di modello più grande disponibile** (evita varianti “small”/fortemente quantizzate), avvia il server e conferma che `http://127.0.0.1:1234/v1/models` lo elenchi.
- Sostituisci `my-local-model` con l'ID effettivo del modello mostrato in LM Studio.
- Mantieni il modello caricato; il caricamento a freddo aggiunge latenza all'avvio.
- Regola `contextWindow`/`maxTokens` se la tua build di LM Studio è diversa.
- Per WhatsApp, usa Responses API in modo che venga inviato solo il testo finale.

Mantieni configurati anche i modelli ospitati quando esegui in locale; usa `models.mode: "merge"` in modo che i fallback restino disponibili.

### Configurazione ibrida: primario ospitato, fallback locale

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

### Priorità al locale con rete di sicurezza ospitata

Inverti l'ordine tra primario e fallback; mantieni lo stesso blocco `providers` e `models.mode: "merge"` così puoi usare come fallback Sonnet o Opus quando la macchina locale non è disponibile.

### Hosting regionale / instradamento dei dati

- Esistono anche varianti MiniMax/Kimi/GLM ospitate su OpenRouter con endpoint vincolati a una regione (ad esempio, ospitati negli Stati Uniti). Scegli lì la variante regionale per mantenere il traffico nella giurisdizione che preferisci continuando a usare `models.mode: "merge"` per i fallback Anthropic/OpenAI.
- Solo locale resta il percorso più forte per la privacy; l'instradamento regionale ospitato è la via di mezzo quando hai bisogno di funzionalità del provider ma vuoi controllare il flusso dei dati.

## Altri proxy locali compatibili con OpenAI

vLLM, LiteLLM, OAI-proxy o gateway personalizzati funzionano se espongono un endpoint `/v1` in stile OpenAI. Sostituisci il blocco provider sopra con il tuo endpoint e l'ID del modello:

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

Mantieni `models.mode: "merge"` in modo che i modelli ospitati restino disponibili come fallback.

Nota sul comportamento per backend `/v1` locali/con proxy:

- OpenClaw li tratta come route compatibili con OpenAI in stile proxy, non come endpoint OpenAI nativi
- il model shaping delle richieste riservato al solo OpenAI nativo non si applica qui: niente
  `service_tier`, niente `store` di Responses, niente model shaping del payload di compatibilità per il ragionamento OpenAI
  e niente suggerimenti per la cache dei prompt
- le intestazioni di attribuzione nascoste di OpenClaw (`originator`, `version`, `User-Agent`)
  non vengono iniettate su questi URL proxy personalizzati

Note di compatibilità per backend compatibili con OpenAI più rigidi:

- Alcuni server accettano solo `messages[].content` come stringa su Chat Completions, non
  array strutturati di parti di contenuto. Imposta
  `models.providers.<provider>.models[].compat.requiresStringContent: true` per
  questi endpoint.
- Alcuni backend locali più piccoli o più rigidi sono instabili con la forma completa dei prompt del runtime
  agente di OpenClaw, soprattutto quando sono inclusi gli schemi degli strumenti. Se il
  backend funziona per chiamate dirette minime a `/v1/chat/completions` ma fallisce nei normali
  turni agente di OpenClaw, prova prima con
  `models.providers.<provider>.models[].compat.supportsTools: false`.
- Se il backend continua a fallire solo su esecuzioni OpenClaw più grandi, il problema residuo
  di solito è la capacità del modello/server a monte o un bug del backend, non il layer di trasporto di OpenClaw.

## Risoluzione dei problemi

- Il gateway riesce a raggiungere il proxy? `curl http://127.0.0.1:1234/v1/models`.
- Modello LM Studio scaricato dalla memoria? Ricaricalo; l'avvio a freddo è una causa comune di “blocco”.
- Errori di contesto? Riduci `contextWindow` o aumenta il limite del tuo server.
- Il server compatibile con OpenAI restituisce `messages[].content ... expected a string`?
  Aggiungi `compat.requiresStringContent: true` a quella voce di modello.
- Le chiamate dirette minime a `/v1/chat/completions` funzionano, ma `openclaw infer model run`
  fallisce su Gemma o su un altro modello locale? Disabilita prima gli schemi degli strumenti con
  `compat.supportsTools: false`, poi riprova. Se il server continua a bloccarsi solo
  su prompt OpenClaw più grandi, trattalo come una limitazione del server/modello a monte.
- Sicurezza: i modelli locali saltano i filtri lato provider; mantieni gli agenti limitati e la compattazione attiva per limitare l'impatto del prompt injection.
