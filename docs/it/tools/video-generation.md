---
read_when:
    - Generazione di video tramite l'agente
    - Configurazione dei provider e dei modelli per la generazione video
    - Comprensione dei parametri dello strumento video_generate
summary: Genera video da testo, immagini o video esistenti utilizzando 12 backend provider
title: Generazione video
x-i18n:
    generated_at: "2026-04-06T08:15:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 90d8a392b35adbd899232b02c55c10895b9d7ffc9858d6ca448f2e4e4a57f12f
    source_path: tools/video-generation.md
    workflow: 15
---

# Generazione video

Gli agenti OpenClaw possono generare video da prompt di testo, immagini di riferimento o video esistenti. Sono supportati dodici backend provider, ciascuno con diverse opzioni di modello, modalità di input e set di funzionalità. L'agente sceglie automaticamente il provider corretto in base alla tua configurazione e alle chiavi API disponibili.

<Note>
Lo strumento `video_generate` appare solo quando è disponibile almeno un provider per la generazione video. Se non lo vedi tra gli strumenti del tuo agente, imposta una chiave API del provider o configura `agents.defaults.videoGenerationModel`.
</Note>

## Avvio rapido

1. Imposta una chiave API per qualsiasi provider supportato:

```bash
export GEMINI_API_KEY="your-key"
```

2. Facoltativamente, fissa un modello predefinito:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Chiedi all'agente:

> Genera un video cinematografico di 5 secondi di un'aragosta amichevole che fa surf al tramonto.

L'agente chiama automaticamente `video_generate`. Non è necessaria alcuna allowlist degli strumenti.

## Cosa succede quando generi un video

La generazione video è asincrona. Quando l'agente chiama `video_generate` in una sessione:

1. OpenClaw invia la richiesta al provider e restituisce immediatamente un ID attività.
2. Il provider elabora il lavoro in background (in genere da 30 secondi a 5 minuti a seconda del provider e della risoluzione).
3. Quando il video è pronto, OpenClaw riattiva la stessa sessione con un evento interno di completamento.
4. L'agente pubblica il video completato nella conversazione originale.

Mentre un'attività è in corso, le chiamate duplicate a `video_generate` nella stessa sessione restituiscono lo stato corrente dell'attività invece di avviare un'altra generazione. Usa `openclaw tasks list` o `openclaw tasks show <taskId>` per controllare l'avanzamento dalla CLI.

Al di fuori delle esecuzioni dell'agente supportate da sessione (ad esempio, invocazioni dirette degli strumenti), lo strumento torna alla generazione inline e restituisce il percorso finale del file multimediale nello stesso turno.

## Provider supportati

| Provider | Modello predefinito             | Testo | Immagine rif.     | Video rif.       | Chiave API                                |
| -------- | ------------------------------- | ----- | ----------------- | ---------------- | ----------------------------------------- |
| Alibaba  | `wan2.6-t2v`                    | Sì    | Sì (URL remoto)   | Sì (URL remoto)  | `MODELSTUDIO_API_KEY`                     |
| BytePlus | `seedance-1-0-lite-t2v-250428`  | Sì    | 1 immagine        | No               | `BYTEPLUS_API_KEY`                        |
| ComfyUI  | `workflow`                      | Sì    | 1 immagine        | No               | `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY`   |
| fal      | `fal-ai/minimax/video-01-live`  | Sì    | 1 immagine        | No               | `FAL_KEY`                                 |
| Google   | `veo-3.1-fast-generate-preview` | Sì    | 1 immagine        | 1 video          | `GEMINI_API_KEY`                          |
| MiniMax  | `MiniMax-Hailuo-2.3`            | Sì    | 1 immagine        | No               | `MINIMAX_API_KEY`                         |
| OpenAI   | `sora-2`                        | Sì    | 1 immagine        | 1 video          | `OPENAI_API_KEY`                          |
| Qwen     | `wan2.6-t2v`                    | Sì    | Sì (URL remoto)   | Sì (URL remoto)  | `QWEN_API_KEY`                            |
| Runway   | `gen4.5`                        | Sì    | 1 immagine        | 1 video          | `RUNWAYML_API_SECRET`                     |
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | Sì    | 1 immagine        | No               | `TOGETHER_API_KEY`                        |
| Vydra    | `veo3`                          | Sì    | 1 immagine (`kling`) | No            | `VYDRA_API_KEY`                           |
| xAI      | `grok-imagine-video`            | Sì    | 1 immagine        | 1 video          | `XAI_API_KEY`                             |

Alcuni provider accettano variabili d'ambiente aggiuntive o alternative per la chiave API. Consulta le singole [pagine dei provider](#related) per i dettagli.

Esegui `video_generate action=list` per esaminare i provider e i modelli disponibili in fase di esecuzione.

## Parametri dello strumento

### Obbligatori

| Parametro | Tipo   | Descrizione                                                                 |
| --------- | ------ | --------------------------------------------------------------------------- |
| `prompt`  | string | Descrizione testuale del video da generare (obbligatoria per `action: "generate"`) |

### Input di contenuto

| Parametro | Tipo     | Descrizione                             |
| --------- | -------- | --------------------------------------- |
| `image`   | string   | Singola immagine di riferimento (percorso o URL) |
| `images`  | string[] | Immagini di riferimento multiple (fino a 5) |
| `video`   | string   | Singolo video di riferimento (percorso o URL) |
| `videos`  | string[] | Video di riferimento multipli (fino a 4) |

### Controlli di stile

| Parametro        | Tipo    | Descrizione                                                            |
| ---------------- | ------- | ---------------------------------------------------------------------- |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P` o `1080P`                                               |
| `durationSeconds`| number  | Durata target in secondi (arrotondata al valore supportato dal provider più vicino) |
| `size`           | string  | Indicazione di dimensione quando il provider la supporta               |
| `audio`          | boolean | Abilita l'audio generato quando supportato                             |
| `watermark`      | boolean | Attiva o disattiva il watermark del provider quando supportato         |

### Avanzati

| Parametro  | Tipo   | Descrizione                                      |
| ---------- | ------ | ------------------------------------------------ |
| `action`   | string | `"generate"` (predefinito), `"status"` o `"list"` |
| `model`    | string | Override di provider/modello (ad es. `runway/gen4.5`) |
| `filename` | string | Suggerimento per il nome del file di output      |

Non tutti i provider supportano tutti i parametri. Gli override non supportati vengono ignorati in base al miglior sforzo e segnalati come avvisi nel risultato dello strumento. I limiti rigidi di capacità (come un numero eccessivo di input di riferimento) falliscono prima dell'invio.

## Azioni

- **generate** (predefinita) -- crea un video a partire dal prompt fornito e dagli input di riferimento facoltativi.
- **status** -- controlla lo stato dell'attività video in corso per la sessione corrente senza avviare un'altra generazione.
- **list** -- mostra i provider, i modelli e le relative capacità disponibili.

## Selezione del modello

Quando genera un video, OpenClaw risolve il modello in questo ordine:

1. **Parametro dello strumento `model`** -- se l'agente ne specifica uno nella chiamata.
2. **`videoGenerationModel.primary`** -- dalla configurazione.
3. **`videoGenerationModel.fallbacks`** -- provati in ordine.
4. **Rilevamento automatico** -- usa i provider con autenticazione valida, iniziando dal provider predefinito corrente, poi i provider rimanenti in ordine alfabetico.

Se un provider fallisce, il candidato successivo viene provato automaticamente. Se tutti i candidati falliscono, l'errore include i dettagli di ogni tentativo.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Note sui provider

| Provider | Note                                                                                                                                                          |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | Usa l'endpoint asincrono DashScope/Model Studio. Le immagini e i video di riferimento devono essere URL `http(s)` remoti.                                   |
| BytePlus | Solo un'immagine di riferimento.                                                                                                                              |
| ComfyUI  | Esecuzione locale o cloud basata su workflow. Supporta text-to-video e image-to-video tramite il grafo configurato.                                         |
| fal      | Usa un flusso supportato da coda per lavori di lunga durata. Solo un'immagine di riferimento.                                                                |
| Google   | Usa Gemini/Veo. Supporta un'immagine o un video di riferimento.                                                                                               |
| MiniMax  | Solo un'immagine di riferimento.                                                                                                                              |
| OpenAI   | Viene inoltrato solo l'override `size`. Gli altri override di stile (`aspectRatio`, `resolution`, `audio`, `watermark`) vengono ignorati con un avviso.     |
| Qwen     | Stesso backend DashScope di Alibaba. Gli input di riferimento devono essere URL `http(s)` remoti; i file locali vengono rifiutati in anticipo.              |
| Runway   | Supporta file locali tramite URI di dati. Video-to-video richiede `runway/gen4_aleph`. Le esecuzioni solo testo espongono i rapporti d'aspetto `16:9` e `9:16`. |
| Together | Solo un'immagine di riferimento.                                                                                                                              |
| Vydra    | Usa direttamente `https://www.vydra.ai/api/v1` per evitare reindirizzamenti che eliminano l'autenticazione. `veo3` è incluso solo come text-to-video; `kling` richiede un URL immagine remoto. |
| xAI      | Supporta flussi text-to-video, image-to-video e di modifica/estensione video remota.                                                                         |

## Configurazione

Imposta il modello predefinito per la generazione video nella configurazione di OpenClaw:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

Oppure tramite la CLI:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## Correlati

- [Panoramica degli strumenti](/it/tools)
- [Attività in background](/it/automation/tasks) -- monitoraggio delle attività per la generazione video asincrona
- [Alibaba Model Studio](/it/providers/alibaba)
- [BytePlus](/it/concepts/model-providers#byteplus-international)
- [ComfyUI](/it/providers/comfy)
- [fal](/it/providers/fal)
- [Google (Gemini)](/it/providers/google)
- [MiniMax](/it/providers/minimax)
- [OpenAI](/it/providers/openai)
- [Qwen](/it/providers/qwen)
- [Runway](/it/providers/runway)
- [Together AI](/it/providers/together)
- [Vydra](/it/providers/vydra)
- [xAI](/it/providers/xai)
- [Riferimento della configurazione](/it/gateway/configuration-reference#agent-defaults)
- [Modelli](/it/concepts/models)
