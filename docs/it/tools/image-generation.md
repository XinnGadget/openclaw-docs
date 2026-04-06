---
read_when:
    - Generazione di immagini tramite l'agente
    - Configurazione dei provider e dei modelli per la generazione di immagini
    - Comprensione dei parametri dello strumento image_generate
summary: Genera e modifica immagini utilizzando i provider configurati (OpenAI, Google Gemini, fal, MiniMax, ComfyUI, Vydra)
title: Generazione di immagini
x-i18n:
    generated_at: "2026-04-06T08:15:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 903cc522c283a8da2cbd449ae3e25f349a74d00ecfdaf0f323fd8aa3f2107aea
    source_path: tools/image-generation.md
    workflow: 15
---

# Generazione di immagini

Lo strumento `image_generate` consente all'agente di creare e modificare immagini utilizzando i provider configurati. Le immagini generate vengono recapitate automaticamente come allegati multimediali nella risposta dell'agente.

<Note>
Lo strumento appare solo quando è disponibile almeno un provider per la generazione di immagini. Se non vedi `image_generate` tra gli strumenti del tuo agente, configura `agents.defaults.imageGenerationModel` oppure imposta una chiave API di un provider.
</Note>

## Avvio rapido

1. Imposta una chiave API per almeno un provider, ad esempio `OPENAI_API_KEY` o `GEMINI_API_KEY`.
2. Facoltativamente, imposta il modello preferito:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

3. Chiedi all'agente: _"Genera un'immagine di una simpatica mascotte aragosta."_

L'agente chiama automaticamente `image_generate`. Non è necessario alcun allowlist degli strumenti: è abilitato per impostazione predefinita quando è disponibile un provider.

## Provider supportati

| Provider | Modello predefinito               | Supporto per la modifica            | Chiave API                                            |
| -------- | -------------------------------- | ----------------------------------- | ----------------------------------------------------- |
| OpenAI   | `gpt-image-1`                    | Sì (fino a 5 immagini)              | `OPENAI_API_KEY`                                      |
| Google   | `gemini-3.1-flash-image-preview` | Sì                                  | `GEMINI_API_KEY` o `GOOGLE_API_KEY`                   |
| fal      | `fal-ai/flux/dev`                | Sì                                  | `FAL_KEY`                                             |
| MiniMax  | `image-01`                       | Sì (riferimento al soggetto)        | `MINIMAX_API_KEY` o OAuth MiniMax (`minimax-portal`) |
| ComfyUI  | `workflow`                       | Sì (1 immagine, configurata tramite workflow) | `COMFY_API_KEY` o `COMFY_CLOUD_API_KEY` per il cloud  |
| Vydra    | `grok-imagine`                   | No                                  | `VYDRA_API_KEY`                                       |

Usa `action: "list"` per esaminare i provider e i modelli disponibili in fase di esecuzione:

```
/tool image_generate action=list
```

## Parametri dello strumento

| Parametro     | Tipo     | Descrizione                                                                          |
| ------------- | -------- | ------------------------------------------------------------------------------------ |
| `prompt`      | string   | Prompt per la generazione di immagini (obbligatorio per `action: "generate"`)       |
| `action`      | string   | `"generate"` (predefinito) oppure `"list"` per esaminare i provider                 |
| `model`       | string   | Override di provider/modello, ad esempio `openai/gpt-image-1`                        |
| `image`       | string   | Percorso o URL di una singola immagine di riferimento per la modalità modifica       |
| `images`      | string[] | Più immagini di riferimento per la modalità modifica (fino a 5)                      |
| `size`        | string   | Indicazione della dimensione: `1024x1024`, `1536x1024`, `1024x1536`, `1024x1792`, `1792x1024` |
| `aspectRatio` | string   | Rapporto d'aspetto: `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`  | string   | Indicazione della risoluzione: `1K`, `2K` o `4K`                                     |
| `count`       | number   | Numero di immagini da generare (1–4)                                                 |
| `filename`    | string   | Indicazione del nome file di output                                                  |

Non tutti i provider supportano tutti i parametri. Lo strumento passa ciò che ogni provider supporta, ignora il resto e segnala gli override scartati nel risultato dello strumento.

## Configurazione

### Selezione del modello

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
        fallbacks: ["google/gemini-3.1-flash-image-preview", "fal/fal-ai/flux/dev"],
      },
    },
  },
}
```

### Ordine di selezione dei provider

Quando genera un'immagine, OpenClaw prova i provider in questo ordine:

1. **Parametro `model`** della chiamata allo strumento (se l'agente ne specifica uno)
2. **`imageGenerationModel.primary`** dalla configurazione
3. **`imageGenerationModel.fallbacks`** nell'ordine indicato
4. **Rilevamento automatico** — usa solo i provider predefiniti supportati dall'autenticazione:
   - prima il provider predefinito corrente
   - poi i restanti provider di generazione di immagini registrati, in ordine di provider id

Se un provider non riesce (errore di autenticazione, limite di velocità, ecc.), viene provato automaticamente il candidato successivo. Se falliscono tutti, l'errore include i dettagli di ogni tentativo.

Note:

- Il rilevamento automatico è consapevole dell'autenticazione. Un provider predefinito entra nell'elenco dei candidati solo quando OpenClaw può effettivamente autenticare quel provider.
- Usa `action: "list"` per esaminare i provider attualmente registrati, i loro modelli predefiniti e i suggerimenti sulle variabili d'ambiente per l'autenticazione.

### Modifica delle immagini

OpenAI, Google, fal, MiniMax e ComfyUI supportano la modifica di immagini di riferimento. Passa un percorso o un URL di un'immagine di riferimento:

```
"Genera una versione ad acquerello di questa foto" + image: "/path/to/photo.jpg"
```

OpenAI e Google supportano fino a 5 immagini di riferimento tramite il parametro `images`. fal, MiniMax e ComfyUI ne supportano 1.

La generazione di immagini MiniMax è disponibile tramite entrambi i percorsi di autenticazione MiniMax inclusi:

- `minimax/image-01` per le configurazioni con chiave API
- `minimax-portal/image-01` per le configurazioni con OAuth

## Capacità dei provider

| Capacità              | OpenAI               | Google               | fal                 | MiniMax                    | ComfyUI                            | Vydra   |
| --------------------- | -------------------- | -------------------- | ------------------- | -------------------------- | ---------------------------------- | ------- |
| Generazione           | Sì (fino a 4)        | Sì (fino a 4)        | Sì (fino a 4)       | Sì (fino a 9)              | Sì (output definiti dal workflow)  | Sì (1)  |
| Modifica/riferimento  | Sì (fino a 5 immagini) | Sì (fino a 5 immagini) | Sì (1 immagine)   | Sì (1 immagine, rif. soggetto) | Sì (1 immagine, configurata tramite workflow) | No      |
| Controllo dimensione  | Sì                   | Sì                   | Sì                  | No                         | No                                 | No      |
| Rapporto d'aspetto    | No                   | Sì                   | Sì (solo generazione) | Sì                      | No                                 | No      |
| Risoluzione (1K/2K/4K) | No                  | Sì                   | Sì                  | No                         | No                                 | No      |

## Correlati

- [Panoramica degli strumenti](/it/tools) — tutti gli strumenti dell'agente disponibili
- [fal](/it/providers/fal) — configurazione del provider di immagini e video fal
- [ComfyUI](/it/providers/comfy) — configurazione locale di ComfyUI e dei workflow Comfy Cloud
- [Google (Gemini)](/it/providers/google) — configurazione del provider di immagini Gemini
- [MiniMax](/it/providers/minimax) — configurazione del provider di immagini MiniMax
- [OpenAI](/it/providers/openai) — configurazione del provider OpenAI Images
- [Vydra](/it/providers/vydra) — configurazione di immagini, video e voce per Vydra
- [Riferimento della configurazione](/it/gateway/configuration-reference#agent-defaults) — configurazione `imageGenerationModel`
- [Modelli](/it/concepts/models) — configurazione dei modelli e failover
