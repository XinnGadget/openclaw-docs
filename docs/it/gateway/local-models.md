---
read_when:
    - Vuoi servire modelli dal tuo box GPU personale
    - Stai configurando LM Studio o un proxy compatibile con OpenAI
    - Hai bisogno della guida più sicura per i modelli locali
summary: Esegui OpenClaw su LLM locali (LM Studio, vLLM, LiteLLM, endpoint OpenAI personalizzati)
title: Modelli locali
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# Modelli locali

Il locale è fattibile, ma OpenClaw si aspetta un contesto ampio e difese robuste contro il prompt injection. Le schede piccole troncano il contesto e indeboliscono la sicurezza. Punta in alto: **≥2 Mac Studio al massimo della configurazione o un rig GPU equivalente (~$30k+)**. Una singola GPU da **24 GB** funziona solo con prompt più leggeri e con latenza più alta. Usa la **variante di modello più grande / full-size che riesci a eseguire**; i checkpoint fortemente quantizzati o “small” aumentano il rischio di prompt injection (vedi [Sicurezza](/it/gateway/security)).

Se vuoi la configurazione locale con meno attrito, inizia con [LM Studio](/it/providers/lmstudio) o [Ollama](/it/providers/ollama) e `openclaw onboard`. Questa pagina è la guida con indicazioni precise per stack locali di fascia più alta e server locali personalizzati compatibili con OpenAI.

## Consigliato: LM Studio + modello locale grande (Responses API)

Il miglior stack locale attuale. Carica un modello grande in LM Studio (per esempio, una build full-size di Qwen, DeepSeek o Llama), abilita il server locale (predefinito `http://127.0.0.1:1234`) e usa la Responses API per mantenere separato il ragionamento dal testo finale.

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
- In LM Studio, scarica la **build di modello più grande disponibile** (evita le varianti “small”/fortemente quantizzate), avvia il server e conferma che `http://127.0.0.1:1234/v1/models` lo elenchi.
- Sostituisci `my-local-model` con l'ID modello effettivo mostrato in LM Studio.
- Mantieni il modello caricato; il caricamento a freddo aggiunge latenza di avvio.
- Regola `contextWindow`/`maxTokens` se la tua build di LM Studio è diversa.
- Per WhatsApp, usa la Responses API così viene inviato solo il testo finale.

Mantieni configurati anche i modelli ospitati quando esegui in locale; usa `models.mode: "merge"` così i fallback restano disponibili.

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

Inverti l'ordine tra primario e fallback; mantieni lo stesso blocco providers e `models.mode: "merge"` così puoi ripiegare su Sonnet o Opus quando il box locale non è disponibile.

### Hosting regionale / instradamento dei dati

- Esistono anche varianti MiniMax/Kimi/GLM ospitate su OpenRouter con endpoint vincolati per regione (per esempio, ospitati negli Stati Uniti). Scegli lì la variante regionale per mantenere il traffico nella giurisdizione desiderata, continuando a usare `models.mode: "merge"` per i fallback Anthropic/OpenAI.
- Il solo locale resta la strada migliore per la privacy; l'instradamento regionale ospitato è la via di mezzo quando hai bisogno delle funzionalità del provider ma vuoi controllare il flusso dei dati.

## Altri proxy locali compatibili con OpenAI

vLLM, LiteLLM, OAI-proxy o Gateway personalizzati funzionano se espongono un endpoint `/v1` in stile OpenAI. Sostituisci il blocco provider sopra con il tuo endpoint e l'ID del modello:

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

Mantieni `models.mode: "merge"` così i modelli ospitati restano disponibili come fallback.

Nota di comportamento per i backend locali/proxati `/v1`:

- OpenClaw li tratta come route proxy in stile OpenAI-compatible, non come endpoint OpenAI nativi
- il model shaping delle richieste riservato a OpenAI nativo non si applica qui: niente `service_tier`, niente `store` della Responses API, niente shaping del payload di compatibilità per il ragionamento OpenAI e nessun suggerimento di prompt-cache
- gli header nascosti di attribuzione OpenClaw (`originator`, `version`, `User-Agent`) non vengono inseriti su questi URL proxy personalizzati

Note di compatibilità per backend compatibili con OpenAI più restrittivi:

- Alcuni server accettano solo `messages[].content` come stringa nelle Chat Completions, non array strutturati di content-part. Imposta `models.providers.<provider>.models[].compat.requiresStringContent: true` per quegli endpoint.
- Alcuni backend locali più piccoli o più rigidi sono instabili con la forma completa del prompt del runtime agente di OpenClaw, specialmente quando sono inclusi gli schemi degli strumenti. Se il backend funziona per chiamate dirette minime a `/v1/chat/completions` ma fallisce nei normali turni agente di OpenClaw, prova prima `agents.defaults.experimental.localModelLean: true` per rimuovere strumenti predefiniti pesanti come `browser`, `cron` e `message`; questo è un flag sperimentale, non un'impostazione stabile della modalità predefinita. Vedi [Funzionalità sperimentali](/it/concepts/experimental-features). Se ancora non basta, prova `models.providers.<provider>.models[].compat.supportsTools: false`.
- Se il backend continua a fallire solo nelle esecuzioni OpenClaw più grandi, il problema residuo di solito è la capacità del modello/server a monte o un bug del backend, non il livello di trasporto di OpenClaw.

## Risoluzione dei problemi

- Il Gateway riesce a raggiungere il proxy? `curl http://127.0.0.1:1234/v1/models`.
- Il modello LM Studio è stato scaricato dalla memoria? Ricaricalo; l'avvio a freddo è una causa comune di “blocco”.
- OpenClaw avvisa quando la finestra di contesto rilevata è sotto **32k** e blocca sotto **16k**. Se incontri questo controllo preliminare, aumenta il limite di contesto del server/modello o scegli un modello più grande.
- Errori di contesto? Riduci `contextWindow` o aumenta il limite del server.
- Il server compatibile con OpenAI restituisce `messages[].content ... expected a string`?
  Aggiungi `compat.requiresStringContent: true` a quella voce del modello.
- Le chiamate dirette minime a `/v1/chat/completions` funzionano, ma `openclaw infer model run`
  fallisce con Gemma o un altro modello locale? Disabilita prima gli schemi degli strumenti con
  `compat.supportsTools: false`, poi riprova. Se il server continua a bloccarsi solo
  con prompt OpenClaw più grandi, trattalo come un limite del server/modello a monte.
- Sicurezza: i modelli locali saltano i filtri lato provider; mantieni gli agenti ristretti e Compaction attivo per limitare l'impatto del prompt injection.
