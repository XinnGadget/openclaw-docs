---
read_when:
    - Vuoi usare Qwen con OpenClaw
    - In precedenza usavi Qwen OAuth
summary: Usa Qwen Cloud tramite il provider qwen bundled di OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-09T01:30:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4786df2cb6ec1ab29d191d012c61dcb0e5468bf0f8561fbbb50eed741efad325
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth è stato rimosso.** L'integrazione OAuth del livello gratuito
(`qwen-portal`) che usava gli endpoint `portal.qwen.ai` non è più disponibile.
Vedi [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) per il
contesto.

</Warning>

## Consigliato: Qwen Cloud

OpenClaw ora tratta Qwen come un provider bundled di prima classe con id canonico
`qwen`. Il provider bundled punta agli endpoint Qwen Cloud / Alibaba DashScope e
Coding Plan e mantiene funzionanti gli id legacy `modelstudio` come alias di
compatibilità.

- Provider: `qwen`
- Variabile env preferita: `QWEN_API_KEY`
- Accettate anche per compatibilità: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Stile API: compatibile con OpenAI

Se vuoi `qwen3.6-plus`, preferisci l'endpoint **Standard (pay-as-you-go)**.
Il supporto Coding Plan può essere in ritardo rispetto al catalogo pubblico.

```bash
# Endpoint Global Coding Plan
openclaw onboard --auth-choice qwen-api-key

# Endpoint China Coding Plan
openclaw onboard --auth-choice qwen-api-key-cn

# Endpoint Global Standard (pay-as-you-go)
openclaw onboard --auth-choice qwen-standard-api-key

# Endpoint China Standard (pay-as-you-go)
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

Gli id legacy `modelstudio-*` per `auth-choice` e i model ref `modelstudio/...` continuano a
funzionare come alias di compatibilità, ma i nuovi flussi di configurazione dovrebbero preferire gli id canonici
`qwen-*` per `auth-choice` e i model ref `qwen/...`.

Dopo l'onboarding, imposta un modello predefinito:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## Tipi di piano ed endpoint

| Piano                      | Regione | Auth choice                | Endpoint                                         |
| -------------------------- | ------- | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | Cina    | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global  | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (abbonamento)  | Cina    | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (abbonamento)  | Global  | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Il provider seleziona automaticamente l'endpoint in base al tuo auth choice. Le scelte canoniche
usano la famiglia `qwen-*`; `modelstudio-*` resta solo per compatibilità.
Puoi eseguire l'override con un `baseUrl` personalizzato nella configurazione.

Gli endpoint nativi Model Studio pubblicizzano la compatibilità di usage in streaming sul
transport condiviso `openai-completions`. OpenClaw ora basa questo comportamento sulle
capability dell'endpoint, quindi gli id provider personalizzati compatibili con DashScope che puntano agli
stessi host nativi ereditano lo stesso comportamento di usage in streaming invece di
richiedere specificamente l'id provider integrato `qwen`.

## Ottieni la tua chiave API

- **Gestisci le chiavi**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **Documentazione**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## Catalogo integrato

OpenClaw attualmente include questo catalogo Qwen bundled. Il catalogo configurato è
consapevole dell'endpoint: le configurazioni Coding Plan omettono i modelli che sono noti
per funzionare solo sull'endpoint Standard.

| Model ref                   | Input       | Contesto | Note                                               |
| --------------------------- | ----------- | -------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | testo, immagine | 1,000,000 | Modello predefinito                             |
| `qwen/qwen3.6-plus`         | testo, immagine | 1,000,000 | Preferisci gli endpoint Standard quando ti serve questo modello |
| `qwen/qwen3-max-2026-01-23` | testo        | 262,144  | Linea Qwen Max                                     |
| `qwen/qwen3-coder-next`     | testo        | 262,144  | Coding                                             |
| `qwen/qwen3-coder-plus`     | testo        | 1,000,000 | Coding                                            |
| `qwen/MiniMax-M2.5`         | testo        | 1,000,000 | Reasoning abilitato                              |
| `qwen/glm-5`                | testo        | 202,752  | GLM                                                |
| `qwen/glm-4.7`              | testo        | 202,752  | GLM                                                |
| `qwen/kimi-k2.5`            | testo, immagine | 262,144 | Moonshot AI tramite Alibaba                      |

La disponibilità può comunque variare in base all'endpoint e al piano di fatturazione anche quando un modello è
presente nel catalogo bundled.

La compatibilità di usage in streaming nativo si applica sia agli host Coding Plan sia agli host
Standard compatibili con DashScope:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Disponibilità di Qwen 3.6 Plus

`qwen3.6-plus` è disponibile sugli endpoint Model Studio Standard (pay-as-you-go):

- Cina: `dashscope.aliyuncs.com/compatible-mode/v1`
- Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Se gli endpoint Coding Plan restituiscono un errore "unsupported model" per
`qwen3.6-plus`, passa a Standard (pay-as-you-go) invece della coppia
endpoint/chiave Coding Plan.

## Piano delle capability

L'estensione `qwen` sta venendo posizionata come sede vendor per l'intera superficie Qwen
Cloud, non solo per i modelli coding/testo.

- Modelli testo/chat: bundled ora
- Chiamata strumenti, output strutturato, thinking: ereditati dal transport compatibile con OpenAI
- Generazione immagini: pianificata al livello del provider plugin
- Comprensione immagini/video: bundled ora sull'endpoint Standard
- Voce/audio: pianificati al livello del provider plugin
- Embedding/reranking della memoria: pianificati tramite la superficie dell'adapter embedding
- Generazione video: bundled ora tramite la capability condivisa di generazione video

## Componenti aggiuntivi multimodali

L'estensione `qwen` ora espone anche:

- Comprensione video tramite `qwen-vl-max-latest`
- Generazione video Wan tramite:
  - `wan2.6-t2v` (predefinito)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

Queste superfici multimodali usano gli endpoint DashScope **Standard**, non gli
endpoint Coding Plan.

- Base URL Standard Global/Intl: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Base URL Standard Cina: `https://dashscope.aliyuncs.com/compatible-mode/v1`

Per la generazione video, OpenClaw mappa la regione Qwen configurata all'host
DashScope AIGC corrispondente prima di inviare il job:

- Global/Intl: `https://dashscope-intl.aliyuncs.com`
- Cina: `https://dashscope.aliyuncs.com`

Questo significa che un normale `models.providers.qwen.baseUrl` che punta a uno dei
host Qwen Coding Plan o Standard continua comunque a mantenere la generazione video sul corretto
endpoint video DashScope regionale.

Per la generazione video, imposta esplicitamente un modello predefinito:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

Limiti attuali bundled per la generazione video Qwen:

- Fino a **1** video di output per richiesta
- Fino a **1** immagine di input
- Fino a **4** video di input
- Fino a **10 secondi** di durata
- Supporta `size`, `aspectRatio`, `resolution`, `audio` e `watermark`
- La modalità immagine/video di riferimento attualmente richiede **URL http(s) remoti**. I
  percorsi di file locali vengono rifiutati subito perché l'endpoint video DashScope non
  accetta buffer locali caricati per questi riferimenti.

Vedi [Video Generation](/it/tools/video-generation) per i parametri condivisi dello
strumento, la selezione del provider e il comportamento di failover.

## Nota sull'ambiente

Se il Gateway è in esecuzione come demone (launchd/systemd), assicurati che `QWEN_API_KEY` sia
disponibile per quel processo (ad esempio in `~/.openclaw/.env` o tramite
`env.shellEnv`).
