---
read_when:
    - Hai bisogno di un riferimento per la configurazione dei modelli provider per provider
    - Vuoi configurazioni di esempio o comandi CLI di onboarding per i provider di modelli
summary: Panoramica dei provider di modelli con configurazioni di esempio + flussi CLI
title: Provider di modelli
x-i18n:
    generated_at: "2026-04-08T06:02:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 558ac9e34b67fcc3dd6791a01bebc17e1c34152fa6c5611593d681e8cfa532d9
    source_path: concepts/model-providers.md
    workflow: 15
---

# Provider di modelli

Questa pagina tratta i **provider LLM/modello** (non i canali di chat come WhatsApp/Telegram).
Per le regole di selezione del modello, vedi [/concepts/models](/it/concepts/models).

## Regole rapide

- I riferimenti ai modelli usano `provider/model` (esempio: `opencode/claude-opus-4-6`).
- Se imposti `agents.defaults.models`, diventa la allowlist.
- Helper CLI: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Le regole di runtime per il fallback, i probe di cooldown e la persistenza
  della sovrascrittura di sessione sono documentate in [/concepts/model-failover](/it/concepts/model-failover).
- `models.providers.*.models[].contextWindow` sono metadati nativi del modello;
  `models.providers.*.models[].contextTokens` è il limite effettivo di runtime.
- I plugin provider possono iniettare cataloghi di modelli tramite `registerProvider({ catalog })`;
  OpenClaw unisce quell'output in `models.providers` prima di scrivere
  `models.json`.
- I manifest dei provider possono dichiarare `providerAuthEnvVars` in modo che i probe generici
  di autenticazione basati su env non debbano caricare il runtime del plugin. La mappa restante
  delle variabili env del core ora serve solo per provider non-plugin/core e per alcuni casi
  di precedenza generica, come l'onboarding Anthropic con priorità alla chiave API.
- I plugin provider possono anche gestire il comportamento runtime del provider tramite
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, e
  `onModelSelected`.
- Nota: il runtime `capabilities` del provider è metadato condiviso del runner (famiglia
  del provider, particolarità di transcript/tooling, suggerimenti su transport/cache). Non è la
  stessa cosa del [modello pubblico delle capability](/it/plugins/architecture#public-capability-model)
  che descrive ciò che un plugin registra (inferenza testuale, voce, ecc.).

## Comportamento del provider gestito dal plugin

I plugin provider possono ora gestire la maggior parte della logica specifica del provider, mentre OpenClaw mantiene
il loop di inferenza generico.

Suddivisione tipica:

- `auth[].run` / `auth[].runNonInteractive`: il provider gestisce i flussi di onboarding/login
  per `openclaw onboard`, `openclaw models auth` e la configurazione headless
- `wizard.setup` / `wizard.modelPicker`: il provider gestisce etichette di scelta dell'autenticazione,
  alias legacy, suggerimenti di allowlist per l'onboarding e voci di configurazione nei selettori di onboarding/modello
- `catalog`: il provider compare in `models.providers`
- `normalizeModelId`: il provider normalizza gli id dei modelli legacy/preview prima
  della ricerca o della canonizzazione
- `normalizeTransport`: il provider normalizza `api` / `baseUrl` della famiglia di transport
  prima dell'assemblaggio generico del modello; OpenClaw controlla prima il provider corrispondente,
  poi gli altri plugin provider compatibili con hook finché uno non modifica effettivamente il
  transport
- `normalizeConfig`: il provider normalizza la configurazione `models.providers.<id>` prima
  che il runtime la usi; OpenClaw controlla prima il provider corrispondente, poi gli altri
  plugin provider compatibili con hook finché uno non modifica effettivamente la configurazione. Se nessun
  hook provider riscrive la configurazione, gli helper Google-family inclusi continuano comunque
  a normalizzare le voci provider Google supportate.
- `applyNativeStreamingUsageCompat`: il provider applica riscritture di compatibilità per l'uso dello streaming nativo guidate dall'endpoint per i provider di configurazione
- `resolveConfigApiKey`: il provider risolve l'autenticazione tramite marker env per i provider di configurazione
  senza forzare il caricamento completo dell'autenticazione runtime. `amazon-bedrock` ha anche un
  risolutore integrato di marker env AWS qui, anche se l'autenticazione runtime di Bedrock usa
  la catena predefinita dell'SDK AWS.
- `resolveSyntheticAuth`: il provider può esporre la disponibilità di autenticazione locale/self-hosted o di altro tipo
  basata sulla configurazione senza persistere segreti in chiaro
- `shouldDeferSyntheticProfileAuth`: il provider può contrassegnare i placeholder di profilo sintetico memorizzati
  come a precedenza più bassa rispetto all'autenticazione basata su env/config
- `resolveDynamicModel`: il provider accetta id di modelli non ancora presenti nel catalogo statico locale
- `prepareDynamicModel`: il provider richiede un aggiornamento dei metadati prima di ritentare
  la risoluzione dinamica
- `normalizeResolvedModel`: il provider richiede riscritture di transport o URL base
- `contributeResolvedModelCompat`: il provider contribuisce flag di compatibilità per i propri
  modelli vendor anche quando arrivano tramite un altro transport compatibile
- `capabilities`: il provider pubblica particolarità di transcript/tooling/famiglia provider
- `normalizeToolSchemas`: il provider ripulisce gli schemi degli strumenti prima che il runner
  incorporato li veda
- `inspectToolSchemas`: il provider espone avvisi di schema specifici del transport
  dopo la normalizzazione
- `resolveReasoningOutputMode`: il provider sceglie contratti di output di reasoning
  nativi o con tag
- `prepareExtraParams`: il provider imposta valori predefiniti o normalizza parametri di richiesta per modello
- `createStreamFn`: il provider sostituisce il normale percorso di stream con un transport
  completamente personalizzato
- `wrapStreamFn`: il provider applica wrapper di compatibilità a header/body/modello della richiesta
- `resolveTransportTurnState`: il provider fornisce header o metadati nativi del transport
  per turno
- `resolveWebSocketSessionPolicy`: il provider fornisce header di sessione WebSocket nativi
  o una policy di cool-down della sessione
- `createEmbeddingProvider`: il provider gestisce il comportamento degli embedding di memoria quando
  deve appartenere al plugin provider invece che allo switchboard embedding del core
- `formatApiKey`: il provider formatta i profili di autenticazione memorizzati nella stringa runtime
  `apiKey` attesa dal transport
- `refreshOAuth`: il provider gestisce l'aggiornamento OAuth quando i refresher condivisi
  `pi-ai` non sono sufficienti
- `buildAuthDoctorHint`: il provider aggiunge indicazioni di riparazione quando l'aggiornamento OAuth
  fallisce
- `matchesContextOverflowError`: il provider riconosce errori di overflow della finestra di contesto
  specifici del provider che le euristiche generiche non intercetterebbero
- `classifyFailoverReason`: il provider mappa errori raw di transport/API specifici del provider
  in motivi di failover come limite di frequenza o sovraccarico
- `isCacheTtlEligible`: il provider decide quali id di modelli upstream supportano il TTL della cache dei prompt
- `buildMissingAuthMessage`: il provider sostituisce l'errore generico dell'auth-store
  con un suggerimento di recupero specifico del provider
- `suppressBuiltInModel`: il provider nasconde righe upstream obsolete e può restituire un
  errore gestito dal vendor per errori di risoluzione diretta
- `augmentModelCatalog`: il provider aggiunge righe di catalogo sintetiche/finali dopo
  discovery e merge della configurazione
- `isBinaryThinking`: il provider gestisce l'esperienza utente thinking binaria on/off
- `supportsXHighThinking`: il provider abilita `xhigh` per i modelli selezionati
- `resolveDefaultThinkingLevel`: il provider gestisce la policy predefinita di `/think` per una
  famiglia di modelli
- `applyConfigDefaults`: il provider applica valori globali predefiniti specifici del provider
  durante la materializzazione della configurazione in base alla modalità auth, all'env o alla famiglia di modelli
- `isModernModelRef`: il provider gestisce il matching del modello preferito per live/smoke
- `prepareRuntimeAuth`: il provider trasforma una credenziale configurata in un token runtime
  di breve durata
- `resolveUsageAuth`: il provider risolve le credenziali di utilizzo/quota per `/usage`
  e le relative superfici di stato/reporting
- `fetchUsageSnapshot`: il provider gestisce il fetch/parsing dell'endpoint di utilizzo mentre
  il core continua a gestire shell di riepilogo e formattazione
- `onModelSelected`: il provider esegue effetti collaterali post-selezione come
  telemetria o bookkeeping di sessione gestito dal provider

Esempi inclusi attuali:

- `anthropic`: fallback forward-compat per Claude 4.6, suggerimenti di riparazione auth, fetch dell'endpoint
  di utilizzo, metadati cache-TTL/famiglia provider e valori predefiniti globali di configurazione
  consapevoli dell'autenticazione
- `amazon-bedrock`: rilevamento dell'overflow di contesto e classificazione dei
  motivi di failover gestiti dal provider per errori throttle/not-ready specifici di Bedrock, più
  la famiglia di replay condivisa `anthropic-by-model` per protezioni di replay-policy
  solo Claude sul traffico Anthropic
- `anthropic-vertex`: protezioni di replay-policy solo Claude sul traffico
  Anthropic-message
- `openrouter`: id modello pass-through, wrapper di richiesta, suggerimenti di capability del provider,
  sanificazione della thought-signature Gemini su traffico Gemini via proxy, iniezione del
  reasoning via proxy tramite la famiglia stream `openrouter-thinking`, inoltro dei metadati
  di routing e policy cache-TTL
- `github-copilot`: onboarding/login del dispositivo, fallback modello forward-compat,
  suggerimenti transcript Claude-thinking, scambio token runtime e fetch dell'endpoint
  di utilizzo
- `openai`: fallback forward-compat GPT-5.4, normalizzazione diretta del transport OpenAI,
  suggerimenti missing-auth consapevoli di Codex, soppressione di Spark, righe di catalogo sintetiche
  OpenAI/Codex, policy thinking/live-model, normalizzazione degli alias dei token di utilizzo
  (`input` / `output` e famiglie `prompt` / `completion`), la famiglia stream condivisa
  `openai-responses-defaults` per wrapper nativi OpenAI/Codex,
  metadati di famiglia provider, registrazione inclusa del provider di generazione immagini
  per `gpt-image-1` e registrazione inclusa del provider di generazione video
  per `sora-2`
- `google` e `google-gemini-cli`: fallback forward-compat Gemini 3.1,
  validazione del replay Gemini nativo, sanificazione del replay bootstrap, modalità
  di output reasoning con tag, matching del modello moderno, registrazione inclusa del provider
  di generazione immagini per modelli Gemini image-preview e registrazione inclusa del
  provider di generazione video per modelli Veo; Gemini CLI OAuth inoltre
  gestisce la formattazione del token del profilo auth, il parsing del token di utilizzo e il fetch
  dell'endpoint quota per le superfici di utilizzo
- `moonshot`: transport condiviso, normalizzazione del payload thinking gestita dal plugin
- `kilocode`: transport condiviso, header di richiesta gestiti dal plugin, normalizzazione del payload di reasoning,
  sanificazione della thought-signature Gemini via proxy e policy cache-TTL
- `zai`: fallback forward-compat GLM-5, valori predefiniti `tool_stream`, policy cache-TTL,
  policy binary-thinking/live-model e autenticazione utilizzo + fetch quota;
  gli id sconosciuti `glm-5*` vengono sintetizzati dal template incluso `glm-4.7`
- `xai`: normalizzazione del transport Responses nativo, riscritture dell'alias `/fast` per
  varianti Grok fast, `tool_stream` predefinito, pulizia degli schemi strumento /
  payload di reasoning specifica xAI e registrazione inclusa del provider di generazione video
  per `grok-imagine-video`
- `mistral`: metadati capability gestiti dal plugin
- `opencode` e `opencode-go`: metadati capability gestiti dal plugin più
  sanificazione della thought-signature Gemini via proxy
- `alibaba`: catalogo di generazione video gestito dal plugin per riferimenti diretti a modelli Wan
  come `alibaba/wan2.6-t2v`
- `byteplus`: cataloghi gestiti dal plugin più registrazione inclusa del provider di generazione video
  per modelli Seedance text-to-video/image-to-video
- `fal`: registrazione inclusa del provider di generazione video per provider ospitati di terze parti
  registrazione del provider di generazione immagini per modelli immagine FLUX più registrazione inclusa
  del provider di generazione video per modelli video ospitati di terze parti
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` e `volcengine`:
  solo cataloghi gestiti dal plugin
- `qwen`: cataloghi gestiti dal plugin per modelli testuali più registrazioni condivise
  dei provider media-understanding e video-generation per le sue superfici multimodali;
  la generazione video Qwen usa gli endpoint video Standard DashScope con modelli Wan inclusi
  come `wan2.6-t2v` e `wan2.7-r2v`
- `runway`: registrazione del provider di generazione video gestita dal plugin per modelli nativi
  basati su task Runway come `gen4.5`
- `minimax`: cataloghi gestiti dal plugin, registrazione inclusa del provider di generazione video
  per modelli video Hailuo, registrazione inclusa del provider di generazione immagini
  per `image-01`, selezione ibrida della replay-policy Anthropic/OpenAI
  e logica auth/snapshot di utilizzo
- `together`: cataloghi gestiti dal plugin più registrazione inclusa del provider di generazione video
  per modelli video Wan
- `xiaomi`: cataloghi gestiti dal plugin più logica auth/snapshot di utilizzo

Il plugin incluso `openai` ora gestisce entrambi gli id provider: `openai` e
`openai-codex`.

Questo copre i provider che rientrano ancora nei transport normali di OpenClaw. Un provider
che necessita di un esecutore di richieste totalmente personalizzato è una superficie di estensione
separata e più profonda.

## Rotazione delle chiavi API

- Supporta la rotazione generica del provider per provider selezionati.
- Configura più chiavi tramite:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (singolo override live, priorità più alta)
  - `<PROVIDER>_API_KEYS` (lista separata da virgole o punti e virgola)
  - `<PROVIDER>_API_KEY` (chiave primaria)
  - `<PROVIDER>_API_KEY_*` (lista numerata, per esempio `<PROVIDER>_API_KEY_1`)
- Per i provider Google, `GOOGLE_API_KEY` è incluso anche come fallback.
- L'ordine di selezione delle chiavi preserva la priorità e deduplica i valori.
- Le richieste vengono ritentate con la chiave successiva solo in caso di risposte con rate limit (per
  esempio `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` o messaggi periodici di limite d'uso).
- Gli errori non dovuti a rate limit falliscono immediatamente; non viene tentata alcuna rotazione delle chiavi.
- Quando tutte le chiavi candidate falliscono, viene restituito l'errore finale dell'ultimo tentativo.

## Provider integrati (catalogo pi-ai)

OpenClaw include il catalogo pi-ai. Questi provider non richiedono alcuna configurazione
`models.providers`; basta impostare l'autenticazione e scegliere un modello.

### OpenAI

- Provider: `openai`
- Auth: `OPENAI_API_KEY`
- Rotazione opzionale: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, più `OPENCLAW_LIVE_OPENAI_KEY` (singolo override)
- Modelli di esempio: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Il transport predefinito è `auto` (prima WebSocket, fallback SSE)
- Override per modello tramite `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` o `"auto"`)
- Il warm-up WebSocket di OpenAI Responses è abilitato per impostazione predefinita tramite `params.openaiWsWarmup` (`true`/`false`)
- L'elaborazione prioritaria OpenAI può essere abilitata tramite `agents.defaults.models["openai/<model>"].params.serviceTier`
- `/fast` e `params.fastMode` mappano le richieste dirette `openai/*` Responses a `service_tier=priority` su `api.openai.com`
- Usa `params.serviceTier` quando vuoi un livello esplicito invece del toggle condiviso `/fast`
- Gli header di attribuzione OpenClaw nascosti (`originator`, `version`,
  `User-Agent`) si applicano solo al traffico nativo OpenAI verso `api.openai.com`, non
  ai proxy generici compatibili con OpenAI
- I percorsi OpenAI nativi mantengono anche `store` di Responses, suggerimenti per la cache dei prompt e
  modellazione del payload di compatibilità reasoning OpenAI; i percorsi proxy no
- `openai/gpt-5.3-codex-spark` è intenzionalmente soppresso in OpenClaw perché l'API OpenAI live lo rifiuta; Spark è trattato come solo Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Provider: `anthropic`
- Auth: `ANTHROPIC_API_KEY`
- Rotazione opzionale: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, più `OPENCLAW_LIVE_ANTHROPIC_KEY` (singolo override)
- Modello di esempio: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Le richieste Anthropic pubbliche dirette supportano il toggle condiviso `/fast` e `params.fastMode`, incluso il traffico autenticato con chiave API e OAuth inviato a `api.anthropic.com`; OpenClaw lo mappa a Anthropic `service_tier` (`auto` vs `standard_only`)
- Nota Anthropic: il personale Anthropic ci ha detto che l'uso in stile Claude CLI di OpenClaw è di nuovo consentito, quindi OpenClaw tratta il riuso di Claude CLI e l'uso di `claude -p` come autorizzati per questa integrazione, a meno che Anthropic non pubblichi una nuova policy.
- Il setup-token Anthropic rimane disponibile come percorso token OpenClaw supportato, ma OpenClaw ora preferisce il riuso di Claude CLI e `claude -p` quando disponibili.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Provider: `openai-codex`
- Auth: OAuth (ChatGPT)
- Modello di esempio: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` o `openclaw models auth login --provider openai-codex`
- Il transport predefinito è `auto` (prima WebSocket, fallback SSE)
- Override per modello tramite `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` o `"auto"`)
- `params.serviceTier` viene inoltrato anche sulle richieste native Codex Responses (`chatgpt.com/backend-api`)
- Gli header di attribuzione OpenClaw nascosti (`originator`, `version`,
  `User-Agent`) vengono allegati solo sul traffico Codex nativo verso
  `chatgpt.com/backend-api`, non ai proxy generici compatibili con OpenAI
- Condivide lo stesso toggle `/fast` e la stessa configurazione `params.fastMode` di `openai/*` diretto; OpenClaw lo mappa a `service_tier=priority`
- `openai-codex/gpt-5.3-codex-spark` rimane disponibile quando il catalogo OAuth Codex lo espone; dipende dai diritti
- `openai-codex/gpt-5.4` mantiene `contextWindow = 1050000` nativo e un `contextTokens = 272000` di runtime predefinito; sovrascrivi il limite runtime con `models.providers.openai-codex.models[].contextTokens`
- Nota sulla policy: OpenAI Codex OAuth è esplicitamente supportato per strumenti/workflow esterni come OpenClaw.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Altre opzioni ospitate in stile abbonamento

- [Qwen Cloud](/it/providers/qwen): superficie provider Qwen Cloud più mapping degli endpoint Alibaba DashScope e Coding Plan
- [MiniMax](/it/providers/minimax): accesso MiniMax Coding Plan OAuth o tramite chiave API
- [GLM Models](/it/providers/glm): endpoint Z.AI Coding Plan o API generali

### OpenCode

- Auth: `OPENCODE_API_KEY` (o `OPENCODE_ZEN_API_KEY`)
- Provider runtime Zen: `opencode`
- Provider runtime Go: `opencode-go`
- Modelli di esempio: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` o `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (chiave API)

- Provider: `google`
- Auth: `GEMINI_API_KEY`
- Rotazione opzionale: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, fallback `GOOGLE_API_KEY` e `OPENCLAW_LIVE_GEMINI_KEY` (singolo override)
- Modelli di esempio: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Compatibilità: la configurazione legacy di OpenClaw che usa `google/gemini-3.1-flash-preview` viene normalizzata in `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Le esecuzioni Gemini dirette accettano anche `agents.defaults.models["google/<model>"].params.cachedContent`
  (o il legacy `cached_content`) per inoltrare un handle
  `cachedContents/...` nativo del provider; gli hit della cache Gemini emergono come OpenClaw `cacheRead`

### Google Vertex e Gemini CLI

- Provider: `google-vertex`, `google-gemini-cli`
- Auth: Vertex usa gcloud ADC; Gemini CLI usa il suo flusso OAuth
- Attenzione: Gemini CLI OAuth in OpenClaw è un'integrazione non ufficiale. Alcuni utenti hanno segnalato restrizioni sugli account Google dopo aver usato client di terze parti. Consulta i termini di Google e usa un account non critico se scegli di procedere.
- Gemini CLI OAuth è incluso come parte del plugin `google`.
  - Installa prima Gemini CLI:
    - `brew install gemini-cli`
    - oppure `npm install -g @google/gemini-cli`
  - Abilita: `openclaw plugins enable google`
  - Login: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Modello predefinito: `google-gemini-cli/gemini-3-flash-preview`
  - Nota: **non** incolli un client id o secret in `openclaw.json`. Il flusso di login CLI memorizza
    i token nei profili di autenticazione sull'host gateway.
  - Se le richieste falliscono dopo il login, imposta `GOOGLE_CLOUD_PROJECT` o `GOOGLE_CLOUD_PROJECT_ID` sull'host gateway.
  - Le risposte JSON di Gemini CLI vengono parse da `response`; l'utilizzo usa come fallback
    `stats`, con `stats.cached` normalizzato in OpenClaw `cacheRead`.

### Z.AI (GLM)

- Provider: `zai`
- Auth: `ZAI_API_KEY`
- Modello di esempio: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Alias: `z.ai/*` e `z-ai/*` vengono normalizzati in `zai/*`
  - `zai-api-key` rileva automaticamente l'endpoint Z.AI corrispondente; `zai-coding-global`, `zai-coding-cn`, `zai-global` e `zai-cn` forzano una superficie specifica

### Vercel AI Gateway

- Provider: `vercel-ai-gateway`
- Auth: `AI_GATEWAY_API_KEY`
- Modello di esempio: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Provider: `kilocode`
- Auth: `KILOCODE_API_KEY`
- Modello di esempio: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- URL base: `https://api.kilo.ai/api/gateway/`
- Il catalogo di fallback statico include `kilocode/kilo/auto`; la discovery live di
  `https://api.kilo.ai/api/gateway/models` può espandere ulteriormente il catalogo
  runtime.
- Il routing upstream esatto dietro `kilocode/kilo/auto` è gestito da Kilo Gateway,
  non codificato rigidamente in OpenClaw.

Vedi [/providers/kilocode](/it/providers/kilocode) per i dettagli di configurazione.

### Altri plugin provider inclusi

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Modello di esempio: `openrouter/auto`
- OpenClaw applica gli header di attribuzione app documentati da OpenRouter solo quando
  la richiesta punta effettivamente a `openrouter.ai`
- I marker `cache_control` specifici di OpenRouter per Anthropic sono analogamente limitati
  alle route OpenRouter verificate, non a URL proxy arbitrari
- OpenRouter rimane sul percorso in stile proxy compatibile con OpenAI, quindi la modellazione
  nativa delle richieste solo OpenAI (`serviceTier`, `store` di Responses,
  suggerimenti per la cache dei prompt, payload di compatibilità reasoning OpenAI) non viene inoltrata
- I riferimenti OpenRouter basati su Gemini mantengono solo la sanificazione della thought-signature
  proxy-Gemini; la validazione del replay Gemini nativo e le riscritture bootstrap restano disattivate
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Modello di esempio: `kilocode/kilo/auto`
- I riferimenti Kilo basati su Gemini mantengono lo stesso percorso di sanificazione della
  thought-signature proxy-Gemini; `kilocode/kilo/auto` e altri suggerimenti proxy che non supportano reasoning
  saltano l'iniezione di reasoning via proxy
- MiniMax: `minimax` (chiave API) e `minimax-portal` (OAuth)
- Auth: `MINIMAX_API_KEY` per `minimax`; `MINIMAX_OAUTH_TOKEN` o `MINIMAX_API_KEY` per `minimax-portal`
- Modello di esempio: `minimax/MiniMax-M2.7` o `minimax-portal/MiniMax-M2.7`
- L'onboarding/configurazione con chiave API di MiniMax scrive definizioni esplicite dei modelli M2.7 con
  `input: ["text", "image"]`; il catalogo provider incluso mantiene i riferimenti chat
  solo testo finché quella configurazione provider non viene materializzata
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- Modello di esempio: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` o `KIMICODE_API_KEY`)
- Modello di esempio: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- Modello di esempio: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY` o `DASHSCOPE_API_KEY`)
- Modello di esempio: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- Modello di esempio: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Modelli di esempio: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- Modello di esempio: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- Modello di esempio: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` o `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Modello di esempio: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- Modello di esempio: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - Le richieste xAI native incluse usano il percorso xAI Responses
  - `/fast` o `params.fastMode: true` riscrivono `grok-3`, `grok-3-mini`,
    `grok-4` e `grok-4-0709` nelle rispettive varianti `*-fast`
  - `tool_stream` è attivo per impostazione predefinita; imposta
    `agents.defaults.models["xai/<model>"].params.tool_stream` su `false` per
    disabilitarlo
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Modello di esempio: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - I modelli GLM su Cerebras usano gli id `zai-glm-4.7` e `zai-glm-4.6`.
  - URL base compatibile con OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Modello di esempio Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Vedi [Hugging Face (Inference)](/it/providers/huggingface).

## Provider tramite `models.providers` (URL base/personalizzato)

Usa `models.providers` (o `models.json`) per aggiungere provider **personalizzati** o
proxy compatibili con OpenAI/Anthropic.

Molti dei plugin provider inclusi qui sotto pubblicano già un catalogo predefinito.
Usa voci esplicite `models.providers.<id>` solo quando vuoi sovrascrivere
l'URL base, gli header o la lista di modelli predefiniti.

### Moonshot AI (Kimi)

Moonshot è incluso come plugin provider. Usa il provider integrato per
impostazione predefinita e aggiungi una voce esplicita `models.providers.moonshot` solo quando
devi sovrascrivere l'URL base o i metadati del modello:

- Provider: `moonshot`
- Auth: `MOONSHOT_API_KEY`
- Modello di esempio: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` o `openclaw onboard --auth-choice moonshot-api-key-cn`

ID modello Kimi K2:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding usa l'endpoint compatibile con Anthropic di Moonshot AI:

- Provider: `kimi`
- Auth: `KIMI_API_KEY`
- Modello di esempio: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Il legacy `kimi/k2p5` continua a essere accettato come id modello di compatibilità.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) fornisce accesso a Doubao e ad altri modelli in Cina.

- Provider: `volcengine` (coding: `volcengine-plan`)
- Auth: `VOLCANO_ENGINE_API_KEY`
- Modello di esempio: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

L'onboarding usa per impostazione predefinita la superficie coding, ma il catalogo generale `volcengine/*`
viene registrato contemporaneamente.

Nei selettori di onboarding/configurazione del modello, la scelta auth Volcengine preferisce sia le righe
`volcengine/*` sia quelle `volcengine-plan/*`. Se questi modelli non sono ancora caricati,
OpenClaw ripiega sul catalogo non filtrato invece di mostrare un selettore
vuoto con ambito provider.

Modelli disponibili:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Modelli coding (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (internazionale)

BytePlus ARK fornisce accesso agli stessi modelli di Volcano Engine per gli utenti internazionali.

- Provider: `byteplus` (coding: `byteplus-plan`)
- Auth: `BYTEPLUS_API_KEY`
- Modello di esempio: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

L'onboarding usa per impostazione predefinita la superficie coding, ma il catalogo generale `byteplus/*`
viene registrato contemporaneamente.

Nei selettori di onboarding/configurazione del modello, la scelta auth BytePlus preferisce sia le righe
`byteplus/*` sia quelle `byteplus-plan/*`. Se questi modelli non sono ancora caricati,
OpenClaw ripiega sul catalogo non filtrato invece di mostrare un selettore
vuoto con ambito provider.

Modelli disponibili:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Modelli coding (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic fornisce modelli compatibili con Anthropic dietro il provider `synthetic`:

- Provider: `synthetic`
- Auth: `SYNTHETIC_API_KEY`
- Modello di esempio: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax è configurato tramite `models.providers` perché usa endpoint personalizzati:

- MiniMax OAuth (globale): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- Chiave API MiniMax (globale): `--auth-choice minimax-global-api`
- Chiave API MiniMax (CN): `--auth-choice minimax-cn-api`
- Auth: `MINIMAX_API_KEY` per `minimax`; `MINIMAX_OAUTH_TOKEN` o
  `MINIMAX_API_KEY` per `minimax-portal`

Vedi [/providers/minimax](/it/providers/minimax) per dettagli di configurazione, opzioni dei modelli e snippet di configurazione.

Sul percorso di streaming compatibile con Anthropic di MiniMax, OpenClaw disabilita thinking per
impostazione predefinita a meno che tu non lo imposti esplicitamente, e `/fast on` riscrive
`MiniMax-M2.7` in `MiniMax-M2.7-highspeed`.

Suddivisione delle capability gestita dal plugin:

- I valori predefiniti testo/chat restano su `minimax/MiniMax-M2.7`
- La generazione immagini è `minimax/image-01` o `minimax-portal/image-01`
- La comprensione immagini è `MiniMax-VL-01` gestito dal plugin su entrambi i percorsi auth MiniMax
- La ricerca web resta sull'id provider `minimax`

### Ollama

Ollama è incluso come plugin provider e usa l'API nativa di Ollama:

- Provider: `ollama`
- Auth: Nessuna richiesta (server locale)
- Modello di esempio: `ollama/llama3.3`
- Installazione: [https://ollama.com/download](https://ollama.com/download)

```bash
# Installa Ollama, poi scarica un modello:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama viene rilevato localmente su `http://127.0.0.1:11434` quando scegli di attivarlo con
`OLLAMA_API_KEY`, e il plugin provider incluso aggiunge Ollama direttamente a
`openclaw onboard` e al selettore di modelli. Vedi [/providers/ollama](/it/providers/ollama)
per onboarding, modalità cloud/locale e configurazione personalizzata.

### vLLM

vLLM è incluso come plugin provider per server locali/self-hosted compatibili con OpenAI:

- Provider: `vllm`
- Auth: Opzionale (dipende dal tuo server)
- URL base predefinito: `http://127.0.0.1:8000/v1`

Per attivare l'auto-discovery locale (qualsiasi valore va bene se il tuo server non impone l'autenticazione):

```bash
export VLLM_API_KEY="vllm-local"
```

Poi imposta un modello (sostituisci con uno degli ID restituiti da `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Vedi [/providers/vllm](/it/providers/vllm) per i dettagli.

### SGLang

SGLang è incluso come plugin provider per server self-hosted veloci
compatibili con OpenAI:

- Provider: `sglang`
- Auth: Opzionale (dipende dal tuo server)
- URL base predefinito: `http://127.0.0.1:30000/v1`

Per attivare l'auto-discovery locale (qualsiasi valore va bene se il tuo server non
impone l'autenticazione):

```bash
export SGLANG_API_KEY="sglang-local"
```

Poi imposta un modello (sostituisci con uno degli ID restituiti da `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Vedi [/providers/sglang](/it/providers/sglang) per i dettagli.

### Proxy locali (LM Studio, vLLM, LiteLLM, ecc.)

Esempio (compatibile con OpenAI):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Note:

- Per i provider personalizzati, `reasoning`, `input`, `cost`, `contextWindow` e `maxTokens` sono facoltativi.
  Se omessi, OpenClaw usa i seguenti valori predefiniti:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Consigliato: imposta valori espliciti che corrispondano ai limiti del tuo proxy/modello.
- Per `api: "openai-completions"` su endpoint non nativi (qualsiasi `baseUrl` non vuoto il cui host non sia `api.openai.com`), OpenClaw forza `compat.supportsDeveloperRole: false` per evitare errori provider 400 dovuti a ruoli `developer` non supportati.
- I percorsi in stile proxy compatibili con OpenAI saltano anche la modellazione delle richieste nativa solo OpenAI:
  niente `service_tier`, niente `store` di Responses, niente suggerimenti per la cache dei prompt, niente
  modellazione del payload di compatibilità reasoning OpenAI e nessun header di attribuzione OpenClaw
  nascosto.
- Se `baseUrl` è vuoto/omesso, OpenClaw mantiene il comportamento OpenAI predefinito (che risolve a `api.openai.com`).
- Per sicurezza, un `compat.supportsDeveloperRole: true` esplicito viene comunque sovrascritto sugli endpoint `openai-completions` non nativi.

## Esempi CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Vedi anche: [/gateway/configuration](/it/gateway/configuration) per esempi completi di configurazione.

## Correlati

- [Models](/it/concepts/models) — configurazione e alias dei modelli
- [Model Failover](/it/concepts/model-failover) — catene di fallback e comportamento dei tentativi
- [Configuration Reference](/it/gateway/configuration-reference#agent-defaults) — chiavi di configurazione del modello
- [Providers](/it/providers) — guide di configurazione per provider
