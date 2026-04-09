---
read_when:
    - Stai creando un nuovo plugin provider di modelli
    - Vuoi aggiungere a OpenClaw un proxy compatibile con OpenAI o un LLM personalizzato
    - Devi comprendere autenticazione del provider, cataloghi e hook di runtime
sidebarTitle: Provider Plugins
summary: Guida passo passo per creare un plugin provider di modelli per OpenClaw
title: Creare plugin provider
x-i18n:
    generated_at: "2026-04-09T01:30:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 38d9af522dc19e49c81203a83a4096f01c2398b1df771c848a30ad98f251e9e1
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Creare plugin provider

Questa guida illustra come creare un plugin provider che aggiunge un provider di modelli
(LLM) a OpenClaw. Al termine avrai un provider con un catalogo di modelli,
autenticazione con chiave API e risoluzione dinamica dei modelli.

<Info>
  Se non hai mai creato prima un plugin OpenClaw, leggi prima
  [Primi passi](/it/plugins/building-plugins) per la struttura di base del package
  e la configurazione del manifest.
</Info>

## Procedura guidata

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Package e manifest">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Provider di modelli Acme AI",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Chiave API Acme AI",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Chiave API Acme AI"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Il manifest dichiara `providerAuthEnvVars` così OpenClaw può rilevare
    le credenziali senza caricare il runtime del tuo plugin. Aggiungi `providerAuthAliases`
    quando una variante del provider deve riutilizzare l'autenticazione di un altro ID provider. `modelSupport`
    è facoltativo e consente a OpenClaw di caricare automaticamente il tuo plugin provider da ID
    di modelli abbreviati come `acme-large` prima che esistano gli hook di runtime. Se pubblichi il
    provider su ClawHub, i campi `openclaw.compat` e `openclaw.build`
    sono obbligatori in `package.json`.

  </Step>

  <Step title="Registra il provider">
    Un provider minimo richiede `id`, `label`, `auth` e `catalog`:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Provider di modelli Acme AI",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Chiave API Acme AI",
              hint: "Chiave API dalla tua dashboard Acme AI",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Inserisci la tua chiave API Acme AI",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    Questo è un provider funzionante. Gli utenti ora possono
    eseguire `openclaw onboard --acme-ai-api-key <key>` e selezionare
    `acme-ai/acme-large` come modello.

    Per i provider bundle che registrano solo un provider di testo con
    autenticazione tramite chiave API più un singolo runtime basato su catalogo, preferisci l'helper
    più mirato `defineSingleProviderPluginEntry(...)`:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Provider di modelli Acme AI",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Chiave API Acme AI",
            hint: "Chiave API dalla tua dashboard Acme AI",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Inserisci la tua chiave API Acme AI",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Se il tuo flusso di autenticazione deve anche aggiornare `models.providers.*`, alias e
    il modello predefinito dell'agente durante l'onboarding, usa gli helper preset da
    `openclaw/plugin-sdk/provider-onboard`. Gli helper più mirati sono
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` e
    `createModelCatalogPresetAppliers(...)`.

    Quando l'endpoint nativo di un provider supporta blocchi di utilizzo in streaming sul
    normale trasporto `openai-completions`, preferisci gli helper di catalogo condivisi in
    `openclaw/plugin-sdk/provider-catalog-shared` invece di codificare controlli basati sull'ID
    del provider. `supportsNativeStreamingUsageCompat(...)` e
    `applyProviderNativeStreamingUsageCompat(...)` rilevano il supporto dalla mappa delle capability
    dell'endpoint, quindi anche endpoint nativi in stile Moonshot/DashScope possono aderire
    quando un plugin usa un ID provider personalizzato.

  </Step>

  <Step title="Aggiungi la risoluzione dinamica dei modelli">
    Se il tuo provider accetta ID di modelli arbitrari (come un proxy o un router),
    aggiungi `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog di cui sopra

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    Se la risoluzione richiede una chiamata di rete, usa `prepareDynamicModel` per il
    warm-up asincrono: `resolveDynamicModel` viene eseguito di nuovo al completamento.

  </Step>

  <Step title="Aggiungi hook di runtime (se necessario)">
    La maggior parte dei provider richiede solo `catalog` + `resolveDynamicModel`. Aggiungi hook
    in modo incrementale in base alle esigenze del tuo provider.

    I builder di helper condivisi ora coprono le famiglie più comuni di compatibilità replay/strumenti,
    quindi i plugin di solito non devono collegare manualmente ogni hook uno per uno:

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    Famiglie replay disponibili oggi:

    | Famiglia | Cosa collega |
    | --- | --- |
    | `openai-compatible` | Policy replay condivisa in stile OpenAI per trasporti compatibili con OpenAI, inclusa la sanificazione di `tool-call-id`, correzioni dell'ordinamento assistant-first e convalida generica dei turni Gemini dove il trasporto lo richiede |
    | `anthropic-by-model` | Policy replay compatibile con Claude scelta da `modelId`, così i trasporti Anthropic-message ricevono la pulizia dei blocchi di thinking specifica per Claude solo quando il modello risolto è effettivamente un ID Claude |
    | `google-gemini` | Policy replay Gemini nativa più sanificazione del replay bootstrap e modalità di output del ragionamento con tag |
    | `passthrough-gemini` | Sanificazione della firma di thinking Gemini per modelli Gemini eseguiti tramite trasporti proxy compatibili con OpenAI; non abilita la convalida replay Gemini nativa né le riscritture bootstrap |
    | `hybrid-anthropic-openai` | Policy ibrida per provider che combinano superfici di modelli Anthropic-message e compatibili con OpenAI in un solo plugin; l'eliminazione facoltativa dei blocchi di thinking solo-Claude resta limitata al lato Anthropic |

    Esempi reali bundle:

    - `google` e `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` e `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` e `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` e `zai`: `openai-compatible`

    Famiglie stream disponibili oggi:

    | Famiglia | Cosa collega |
    | --- | --- |
    | `google-thinking` | Normalizzazione del payload di thinking Gemini nel percorso stream condiviso |
    | `kilocode-thinking` | Wrapper di ragionamento Kilo nel percorso stream proxy condiviso, con `kilo/auto` e ID di ragionamento proxy non supportati che saltano il thinking iniettato |
    | `moonshot-thinking` | Mappatura del payload native-thinking binario Moonshot da configurazione + livello `/think` |
    | `minimax-fast-mode` | Riscrittura del modello fast-mode MiniMax nel percorso stream condiviso |
    | `openai-responses-defaults` | Wrapper condivisi per Responses nativi OpenAI/Codex: header di attribuzione, `/fast`/`serviceTier`, verbosità del testo, ricerca web Codex nativa, modellazione del payload di compatibilità del ragionamento e gestione del contesto Responses |
    | `openrouter-thinking` | Wrapper di ragionamento OpenRouter per percorsi proxy, con skip di modello non supportato/`auto` gestiti centralmente |
    | `tool-stream-default-on` | Wrapper `tool_stream` attivo per impostazione predefinita per provider come Z.AI che vogliono lo streaming degli strumenti salvo disabilitazione esplicita |

    Esempi reali bundle:

    - `google` e `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` e `minimax-portal`: `minimax-fast-mode`
    - `openai` e `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` esporta anche l'enum delle famiglie replay
    insieme agli helper condivisi su cui tali famiglie sono costruite. Le esportazioni pubbliche comuni
    includono:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - builder replay condivisi come `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` e
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - helper replay Gemini come `sanitizeGoogleGeminiReplayHistory(...)`
      e `resolveTaggedReasoningOutputMode()`
    - helper endpoint/modello come `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` e
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` espone sia il builder di famiglia sia
    gli helper wrapper pubblici riutilizzati da tali famiglie. Le esportazioni pubbliche comuni
    includono:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - wrapper condivisi OpenAI/Codex come
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` e
      `createCodexNativeWebSearchWrapper(...)`
    - wrapper condivisi proxy/provider come `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` e `createMinimaxFastModeWrapper(...)`

    Alcuni helper stream restano intenzionalmente locali al provider. Esempio bundle
    attuale: `@openclaw/anthropic-provider` esporta
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` e i
    builder wrapper Anthropic di livello inferiore dal suo seam pubblico `api.ts` /
    `contract-api.ts`. Questi helper restano specifici di Anthropic perché
    codificano anche la gestione beta di Claude OAuth e il gating `context1m`.

    Anche altri provider bundle mantengono wrapper specifici del trasporto in locale quando
    il comportamento non è condivisibile in modo pulito tra famiglie. Esempio attuale: il
    plugin xAI bundle mantiene la modellazione nativa di xAI Responses nel proprio
    `wrapStreamFn`, inclusi riscritture di alias `/fast`, `tool_stream` predefinito,
    pulizia di strict-tool non supportato e rimozione del payload di ragionamento
    specifica di xAI.

    `openclaw/plugin-sdk/provider-tools` attualmente espone una famiglia condivisa per gli schemi
    degli strumenti più helper condivisi per schema/compatibilità:

    - `ProviderToolCompatFamily` documenta oggi l'inventario condiviso delle famiglie.
    - `buildProviderToolCompatFamilyHooks("gemini")` collega pulizia dello schema Gemini
      + diagnostica per provider che necessitano di schemi degli strumenti compatibili con Gemini.
    - `normalizeGeminiToolSchemas(...)` e `inspectGeminiToolSchemas(...)`
      sono gli helper pubblici Gemini sottostanti per gli schemi.
    - `resolveXaiModelCompatPatch()` restituisce la patch di compatibilità xAI bundle:
      `toolSchemaProfile: "xai"`, parole chiave dello schema non supportate, supporto nativo
      `web_search` e decodifica degli argomenti delle chiamate strumento con entità HTML.
    - `applyXaiModelCompat(model)` applica la stessa patch di compatibilità xAI a un
      modello risolto prima che raggiunga il runner.

    Esempio reale bundle: il plugin xAI usa `normalizeResolvedModel` più
    `contributeResolvedModelCompat` per mantenere questi metadati di compatibilità di proprietà
    del provider invece di codificare rigidamente le regole xAI nel core.

    Lo stesso pattern di root del package supporta anche altri provider bundle:

    - `@openclaw/openai-provider`: `api.ts` esporta builder provider,
      helper del modello predefinito e builder per provider realtime
    - `@openclaw/openrouter-provider`: `api.ts` esporta il builder provider
      più helper di onboarding/configurazione

    <Tabs>
      <Tab title="Scambio di token">
        Per provider che richiedono uno scambio di token prima di ogni chiamata di inferenza:

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="Header personalizzati">
        Per provider che richiedono header di richiesta personalizzati o modifiche del body:

        ```typescript
        // wrapStreamFn restituisce uno StreamFn derivato da ctx.streamFn
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="Identità del trasporto nativo">
        Per provider che richiedono header o metadati nativi di richiesta/sessione su
        trasporti HTTP o WebSocket generici:

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="Utilizzo e fatturazione">
        Per provider che espongono dati di utilizzo/fatturazione:

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="Tutti gli hook provider disponibili">
      OpenClaw chiama gli hook in questo ordine. La maggior parte dei provider ne usa solo 2-3:

      | # | Hook | Quando usarlo |
      | --- | --- | --- |
      | 1 | `catalog` | Catalogo dei modelli o valori predefiniti di base URL |
      | 2 | `applyConfigDefaults` | Valori predefiniti globali di proprietà del provider durante la materializzazione della configurazione |
      | 3 | `normalizeModelId` | Pulizia degli alias legacy/preview degli ID modello prima della ricerca |
      | 4 | `normalizeTransport` | Pulizia di `api` / `baseUrl` della famiglia provider prima dell'assemblaggio generico del modello |
      | 5 | `normalizeConfig` | Normalizza la configurazione `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Riscritture di compatibilità native per streaming-usage per i provider di configurazione |
      | 7 | `resolveConfigApiKey` | Risoluzione dell'autenticazione env-marker di proprietà del provider |
      | 8 | `resolveSyntheticAuth` | Autenticazione sintetica locale/self-hosted o basata sulla configurazione |
      | 9 | `shouldDeferSyntheticProfileAuth` | Abbassa la priorità dei placeholder sintetici dei profili memorizzati rispetto all'autenticazione env/config |
      | 10 | `resolveDynamicModel` | Accetta ID di modelli upstream arbitrari |
      | 11 | `prepareDynamicModel` | Recupero asincrono dei metadati prima della risoluzione |
      | 12 | `normalizeResolvedModel` | Riscritture del trasporto prima del runner |

    Note sul fallback di runtime:

    - `normalizeConfig` controlla prima il provider corrispondente, poi gli altri
      plugin provider dotati di hook finché uno non modifica realmente la configurazione.
      Se nessun hook provider riscrive una voce di configurazione supportata della famiglia Google, il
      normalizzatore di configurazione Google bundle continua comunque ad applicarsi.
    - `resolveConfigApiKey` usa l'hook provider quando esposto. Il percorso bundle
      `amazon-bedrock` ha anche un resolver integrato per env-marker AWS qui,
      anche se l'autenticazione runtime Bedrock continua a usare la catena predefinita dell'AWS SDK.
      | 13 | `contributeResolvedModelCompat` | Flag di compatibilità per modelli del fornitore dietro un altro trasporto compatibile |
      | 14 | `capabilities` | Bag legacy di capability statiche; solo compatibilità |
      | 15 | `normalizeToolSchemas` | Pulizia degli schemi degli strumenti di proprietà del provider prima della registrazione |
      | 16 | `inspectToolSchemas` | Diagnostica degli schemi degli strumenti di proprietà del provider |
      | 17 | `resolveReasoningOutputMode` | Contratto dell'output di ragionamento con tag vs nativo |
      | 18 | `prepareExtraParams` | Parametri di richiesta predefiniti |
      | 19 | `createStreamFn` | Trasporto StreamFn completamente personalizzato |
      | 20 | `wrapStreamFn` | Wrapper personalizzati di header/body sul percorso stream normale |
      | 21 | `resolveTransportTurnState` | Header/metadati nativi per turno |
      | 22 | `resolveWebSocketSessionPolicy` | Header/sessione WS nativi e cool-down |
      | 23 | `formatApiKey` | Forma personalizzata del token runtime |
      | 24 | `refreshOAuth` | Refresh OAuth personalizzato |
      | 25 | `buildAuthDoctorHint` | Indicazioni per la riparazione dell'autenticazione |
      | 26 | `matchesContextOverflowError` | Rilevamento overflow di proprietà del provider |
      | 27 | `classifyFailoverReason` | Classificazione di rate-limit/sovraccarico di proprietà del provider |
      | 28 | `isCacheTtlEligible` | Gating TTL della cache del prompt |
      | 29 | `buildMissingAuthMessage` | Suggerimento personalizzato per autenticazione mancante |
      | 30 | `suppressBuiltInModel` | Nasconde righe upstream obsolete |
      | 31 | `augmentModelCatalog` | Righe sintetiche di compatibilità forward |
      | 32 | `isBinaryThinking` | Thinking binario attivo/disattivo |
      | 33 | `supportsXHighThinking` | Supporto al ragionamento `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Policy predefinita di `/think` |
      | 35 | `isModernModelRef` | Corrispondenza del modello live/smoke |
      | 36 | `prepareRuntimeAuth` | Scambio di token prima dell'inferenza |
      | 37 | `resolveUsageAuth` | Parsing personalizzato delle credenziali di utilizzo |
      | 38 | `fetchUsageSnapshot` | Endpoint di utilizzo personalizzato |
      | 39 | `createEmbeddingProvider` | Adattatore embedding di proprietà del provider per memoria/ricerca |
      | 40 | `buildReplayPolicy` | Policy personalizzata di replay/compattazione della trascrizione |
      | 41 | `sanitizeReplayHistory` | Riscritture replay specifiche del provider dopo la pulizia generica |
      | 42 | `validateReplayTurns` | Convalida rigorosa dei turni replay prima del runner incorporato |
      | 43 | `onModelSelected` | Callback post-selezione (ad esempio telemetria) |

      Nota sulla regolazione del prompt:

      - `resolveSystemPromptContribution` consente a un provider di iniettare indicazioni del
        prompt di sistema consapevoli della cache per una famiglia di modelli. Preferiscilo a
        `before_prompt_build` quando il comportamento appartiene a una famiglia specifica di provider/modelli
        e deve preservare la divisione stabile/dinamica della cache.

      Per descrizioni dettagliate ed esempi del mondo reale, vedi
      [Interni: Hook runtime del provider](/it/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Aggiungi capability extra (facoltativo)">
    <a id="step-5-add-extra-capabilities"></a>
    Un plugin provider può registrare speech, trascrizione in tempo reale, voce
    in tempo reale, media understanding, generazione immagini, generazione video, web fetch
    e ricerca web oltre all'inferenza testuale:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          generate: {
            maxVideos: 1,
            maxDurationSeconds: 10,
            supportsResolution: true,
          },
          imageToVideo: {
            enabled: true,
            maxVideos: 1,
            maxInputImages: 1,
            maxDurationSeconds: 5,
          },
          videoToVideo: {
            enabled: false,
          },
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Recupera pagine tramite il backend di rendering di Acme.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Recupera una pagina tramite Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw lo classifica come plugin **hybrid-capability**. Questo è il
    pattern consigliato per i plugin aziendali (un plugin per vendor). Vedi
    [Interni: Proprietà delle capability](/it/plugins/architecture#capability-ownership-model).

    Per la generazione video, preferisci la struttura di capability consapevole della modalità mostrata sopra:
    `generate`, `imageToVideo` e `videoToVideo`. Campi aggregati piatti come
    `maxInputImages`, `maxInputVideos` e `maxDurationSeconds` non sono
    sufficienti per pubblicizzare chiaramente il supporto delle modalità di trasformazione o delle modalità disabilitate.

    I provider di generazione musicale devono seguire lo stesso pattern:
    `generate` per la generazione basata solo su prompt ed `edit` per la
    generazione basata su immagini di riferimento. Campi aggregati piatti come `maxInputImages`,
    `supportsLyrics` e `supportsFormat` non sono sufficienti per pubblicizzare il supporto a edit;
    i blocchi espliciti `generate` / `edit` sono il contratto previsto.

  </Step>

  <Step title="Test">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Esporta il tuo oggetto di configurazione del provider da index.ts o da un file dedicato
    import { acmeProvider } from "./provider.js";

    describe("provider acme-ai", () => {
      it("risolve i modelli dinamici", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("restituisce il catalogo quando la chiave è disponibile", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("restituisce un catalogo null quando non c'è chiave", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Pubblicare su ClawHub

I plugin provider si pubblicano allo stesso modo di qualsiasi altro plugin di codice esterno:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Non usare qui il vecchio alias di pubblicazione solo per skill; i package plugin devono usare
`clawhub package publish`.

## Struttura dei file

```
<bundled-plugin-root>/acme-ai/
├── package.json              # metadati openclaw.providers
├── openclaw.plugin.json      # Manifest con metadati di autenticazione del provider
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Test
    └── usage.ts              # Endpoint di utilizzo (facoltativo)
```

## Riferimento per l'ordine del catalogo

`catalog.order` controlla quando il tuo catalogo viene unito rispetto ai
provider integrati:

| Ordine    | Quando            | Caso d'uso                                   |
| --------- | ----------------- | -------------------------------------------- |
| `simple`  | Primo passaggio   | Provider semplici con chiave API             |
| `profile` | Dopo `simple`     | Provider vincolati a profili di autenticazione |
| `paired`  | Dopo `profile`    | Sintetizzare più voci correlate              |
| `late`    | Ultimo passaggio  | Sostituire provider esistenti (vince in caso di collisione) |

## Prossimi passi

- [Plugin di canale](/it/plugins/sdk-channel-plugins) — se il tuo plugin fornisce anche un canale
- [Runtime SDK](/it/plugins/sdk-runtime) — helper `api.runtime` (TTS, ricerca, subagent)
- [Panoramica SDK](/it/plugins/sdk-overview) — riferimento completo per gli import dei sottopercorsi
- [Interni dei plugin](/it/plugins/architecture#provider-runtime-hooks) — dettagli sugli hook ed esempi bundle
