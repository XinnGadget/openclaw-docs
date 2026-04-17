---
read_when:
    - Stai creando un nuovo plugin provider di modelli
    - Vuoi aggiungere un proxy compatibile con OpenAI o un LLM personalizzato a OpenClaw
    - Devi comprendere l'autenticazione del provider, i cataloghi e gli hook di runtime
sidebarTitle: Provider Plugins
summary: Guida passo passo per creare un plugin provider di modelli per OpenClaw
title: Creazione di plugin provider
x-i18n:
    generated_at: "2026-04-11T02:46:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06d7c5da6556dc3d9673a31142ff65eb67ddc97fc0c1a6f4826a2c7693ecd5e3
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Creazione di plugin provider

Questa guida descrive passo dopo passo come creare un plugin provider che aggiunge un provider di modelli
(LLM) a OpenClaw. Alla fine avrai un provider con un catalogo modelli,
autenticazione tramite chiave API e risoluzione dinamica dei modelli.

<Info>
  Se non hai mai creato prima un plugin OpenClaw, leggi prima
  [Per iniziare](/it/plugins/building-plugins) per la struttura di base del package
  e l'impostazione del manifest.
</Info>

<Tip>
  I plugin provider aggiungono modelli al normale ciclo di inferenza di OpenClaw. Se il modello
  deve essere eseguito tramite un demone agente nativo che gestisce thread, compattazione
  o eventi degli strumenti, abbina il provider a un [agent harness](/it/plugins/sdk-agent-harness)
  invece di inserire i dettagli del protocollo del demone nel core.
</Tip>

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
      "description": "Acme AI model provider",
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
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Il manifest dichiara `providerAuthEnvVars` in modo che OpenClaw possa rilevare
    le credenziali senza caricare il runtime del tuo plugin. Aggiungi `providerAuthAliases`
    quando una variante di provider deve riutilizzare l'autenticazione di un altro id provider. `modelSupport`
    è facoltativo e consente a OpenClaw di caricare automaticamente il tuo plugin provider da id modello abbreviati come `acme-large` prima che esistano hook di runtime. Se pubblichi il
    provider su ClawHub, quei campi `openclaw.compat` e `openclaw.build`
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
      description: "Acme AI model provider",
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
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
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
    `openclaw onboard --acme-ai-api-key <key>` e selezionare
    `acme-ai/acme-large` come proprio modello.

    Se il provider upstream usa token di controllo diversi da quelli di OpenClaw, aggiungi una
    piccola trasformazione bidirezionale del testo invece di sostituire il percorso di streaming:

    ```typescript
    api.registerTextTransforms({
      input: [
        { from: /red basket/g, to: "blue basket" },
        { from: /paper ticket/g, to: "digital ticket" },
        { from: /left shelf/g, to: "right shelf" },
      ],
      output: [
        { from: /blue basket/g, to: "red basket" },
        { from: /digital ticket/g, to: "paper ticket" },
        { from: /right shelf/g, to: "left shelf" },
      ],
    });
    ```

    `input` riscrive il prompt di sistema finale e il contenuto dei messaggi di testo prima
    del trasporto. `output` riscrive i delta del testo dell'assistente e il testo finale prima che
    OpenClaw analizzi i propri marcatori di controllo o lo consegni al canale.

    Per provider inclusi che registrano solo un provider di testo con
    autenticazione tramite chiave API più un singolo runtime basato su catalogo, preferisci l'helper più ristretto
    `defineSingleProviderPluginEntry(...)`:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
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

    Se il tuo flusso di autenticazione deve anche aggiornare `models.providers.*`, alias
    e il modello predefinito dell'agente durante l'onboarding, usa gli helper preset da
    `openclaw/plugin-sdk/provider-onboard`. Gli helper più mirati sono
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` e
    `createModelCatalogPresetAppliers(...)`.

    Quando l'endpoint nativo di un provider supporta blocchi di utilizzo in streaming sul
    normale trasporto `openai-completions`, preferisci gli helper di catalogo condivisi in
    `openclaw/plugin-sdk/provider-catalog-shared` invece di codificare controlli sull'id provider. `supportsNativeStreamingUsageCompat(...)` e
    `applyProviderNativeStreamingUsageCompat(...)` rilevano il supporto dalla mappa delle capacità dell'endpoint, quindi anche endpoint nativi in stile Moonshot/DashScope possono aderire anche quando un plugin usa un id provider personalizzato.

  </Step>

  <Step title="Aggiungi la risoluzione dinamica dei modelli">
    Se il tuo provider accetta id modello arbitrari (come un proxy o un router),
    aggiungi `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog come sopra

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
    warm-up asincrono — `resolveDynamicModel` viene eseguito di nuovo dopo il completamento.

  </Step>

  <Step title="Aggiungi hook di runtime (se necessario)">
    La maggior parte dei provider richiede solo `catalog` + `resolveDynamicModel`. Aggiungi hook
    in modo incrementale secondo le esigenze del tuo provider.

    I builder di helper condivisi ora coprono le famiglie più comuni di replay/tool-compat,
    quindi in genere i plugin non devono collegare a mano ogni hook uno per uno:

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

    Famiglie di replay disponibili oggi:

    | Family | Cosa collega |
    | --- | --- |
    | `openai-compatible` | Policy di replay condivisa in stile OpenAI per trasporti compatibili con OpenAI, inclusa sanitizzazione di tool-call-id, correzioni dell'ordinamento assistant-first e validazione generica dei turni Gemini dove il trasporto lo richiede |
    | `anthropic-by-model` | Policy di replay consapevole di Claude scelta da `modelId`, così i trasporti Anthropic-message ricevono la pulizia specifica dei blocchi di thinking di Claude solo quando il modello risolto è realmente un id Claude |
    | `google-gemini` | Policy di replay Gemini nativa più sanitizzazione del replay di bootstrap e modalità di output del ragionamento con tag |
    | `passthrough-gemini` | Sanitizzazione della thought-signature di Gemini per modelli Gemini eseguiti tramite trasporti proxy compatibili con OpenAI; non abilita la validazione di replay Gemini nativa né le riscritture di bootstrap |
    | `hybrid-anthropic-openai` | Policy ibrida per provider che combinano superfici modello Anthropic-message e compatibili con OpenAI in un unico plugin; l'eliminazione facoltativa dei blocchi di thinking solo Claude resta limitata al lato Anthropic |

    Esempi reali inclusi:

    - `google` e `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` e `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` e `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` e `zai`: `openai-compatible`

    Famiglie di stream disponibili oggi:

    | Family | Cosa collega |
    | --- | --- |
    | `google-thinking` | Normalizzazione del payload di thinking Gemini sul percorso di stream condiviso |
    | `kilocode-thinking` | Wrapper di reasoning Kilo sul percorso di stream proxy condiviso, con `kilo/auto` e id di reasoning proxy non supportati che saltano il thinking iniettato |
    | `moonshot-thinking` | Mappatura del payload native-thinking binario Moonshot da configurazione + livello `/think` |
    | `minimax-fast-mode` | Riscrittura del modello MiniMax fast-mode sul percorso di stream condiviso |
    | `openai-responses-defaults` | Wrapper nativi condivisi OpenAI/Codex Responses: header di attribuzione, `/fast`/`serviceTier`, verbosità del testo, ricerca web nativa Codex, shaping del payload reasoning-compat e gestione del contesto Responses |
    | `openrouter-thinking` | Wrapper di reasoning OpenRouter per percorsi proxy, con skip di modello non supportato/`auto` gestiti centralmente |
    | `tool-stream-default-on` | Wrapper `tool_stream` attivo per impostazione predefinita per provider come Z.AI che vogliono lo streaming degli strumenti salvo disattivazione esplicita |

    Esempi reali inclusi:

    - `google` e `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` e `minimax-portal`: `minimax-fast-mode`
    - `openai` e `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` esporta anche l'enum della
    famiglia di replay più gli helper condivisi da cui queste famiglie sono costruite. Le esportazioni pubbliche comuni
    includono:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - builder di replay condivisi come `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` e
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - helper di replay Gemini come `sanitizeGoogleGeminiReplayHistory(...)`
      e `resolveTaggedReasoningOutputMode()`
    - helper per endpoint/modelli come `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` e
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` espone sia il builder della famiglia sia
    gli helper wrapper pubblici che queste famiglie riutilizzano. Le esportazioni pubbliche comuni
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
    - wrapper proxy/provider condivisi come `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` e `createMinimaxFastModeWrapper(...)`

    Alcuni helper di stream restano intenzionalmente locali al provider. Esempio
    attuale incluso: `@openclaw/anthropic-provider` esporta
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` e i
    builder wrapper Anthropic di livello inferiore dalla propria interfaccia pubblica `api.ts` /
    `contract-api.ts`. Questi helper restano specifici di Anthropic perché
    codificano anche la gestione beta di Claude OAuth e il gating `context1m`.

    Anche altri provider inclusi mantengono locali i wrapper specifici del trasporto quando
    il comportamento non è condivisibile in modo pulito tra le famiglie. Esempio attuale: il
    plugin xAI incluso mantiene il shaping nativo di xAI Responses nel proprio
    `wrapStreamFn`, inclusi riscritture degli alias `/fast`, `tool_stream`
    predefinito, pulizia degli strict-tool non supportati e rimozione del
    payload di reasoning specifico xAI.

    `openclaw/plugin-sdk/provider-tools` al momento espone una famiglia condivisa
    di schema strumenti più helper condivisi di schema/compatibilità:

    - `ProviderToolCompatFamily` documenta oggi l'inventario delle famiglie condivise.
    - `buildProviderToolCompatFamilyHooks("gemini")` collega la
      pulizia dello schema Gemini + la diagnostica per provider che hanno bisogno di schemi strumenti sicuri per Gemini.
    - `normalizeGeminiToolSchemas(...)` e `inspectGeminiToolSchemas(...)`
      sono gli helper pubblici sottostanti per lo schema Gemini.
    - `resolveXaiModelCompatPatch()` restituisce la patch compat xAI inclusa:
      `toolSchemaProfile: "xai"`, keyword di schema non supportate, supporto nativo
      `web_search` e decodifica degli argomenti delle chiamate strumento con entità HTML.
    - `applyXaiModelCompat(model)` applica la stessa patch compat xAI a un
      modello risolto prima che raggiunga il runner.

    Esempio reale incluso: il plugin xAI usa `normalizeResolvedModel` più
    `contributeResolvedModelCompat` per mantenere questi metadati compat sotto la responsabilità del
    provider invece di codificare regole xAI nel core.

    Lo stesso schema package-root supporta anche altri provider inclusi:

    - `@openclaw/openai-provider`: `api.ts` esporta builder di provider,
      helper per il modello predefinito e builder di provider realtime
    - `@openclaw/openrouter-provider`: `api.ts` esporta il builder del provider
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
        Per provider che richiedono header di richiesta personalizzati o modifiche al body:

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
      | 1 | `catalog` | Catalogo modelli o valori predefiniti del base URL |
      | 2 | `applyConfigDefaults` | Valori predefiniti globali posseduti dal provider durante la materializzazione della configurazione |
      | 3 | `normalizeModelId` | Pulizia degli alias legacy/preview degli id modello prima della ricerca |
      | 4 | `normalizeTransport` | Pulizia di `api` / `baseUrl` della famiglia provider prima dell'assemblaggio generico del modello |
      | 5 | `normalizeConfig` | Normalizza la configurazione `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Riscritture di compatibilità per l'utilizzo streaming nativo per provider di configurazione |
      | 7 | `resolveConfigApiKey` | Risoluzione dell'autenticazione env-marker posseduta dal provider |
      | 8 | `resolveSyntheticAuth` | Autenticazione sintetica locale/self-hosted o supportata da configurazione |
      | 9 | `shouldDeferSyntheticProfileAuth` | Abbassa i placeholder sintetici di profilo memorizzato dietro autenticazione env/config |
      | 10 | `resolveDynamicModel` | Accetta id modello upstream arbitrari |
      | 11 | `prepareDynamicModel` | Recupero asincrono dei metadati prima della risoluzione |
      | 12 | `normalizeResolvedModel` | Riscritture del trasporto prima del runner |

    Note sul fallback runtime:

    - `normalizeConfig` controlla prima il provider corrispondente, poi altri
      plugin provider con hook finché uno non modifica effettivamente la configurazione.
      Se nessun hook provider riscrive una voce di configurazione supportata della famiglia Google, continua comunque ad applicarsi il normalizzatore di configurazione Google incluso.
    - `resolveConfigApiKey` usa l'hook provider quando esposto. Il percorso incluso
      `amazon-bedrock` ha anche qui un resolver integrato per env-marker AWS,
      anche se l'autenticazione runtime di Bedrock continua comunque a usare la catena predefinita dell'SDK AWS.
      | 13 | `contributeResolvedModelCompat` | Flag compat per modelli vendor dietro un altro trasporto compatibile |
      | 14 | `capabilities` | Contenitore statico legacy delle capacità; solo compatibilità |
      | 15 | `normalizeToolSchemas` | Pulizia degli schemi strumenti posseduta dal provider prima della registrazione |
      | 16 | `inspectToolSchemas` | Diagnostica degli schemi strumenti posseduta dal provider |
      | 17 | `resolveReasoningOutputMode` | Contratto di output reasoning con tag vs nativo |
      | 18 | `prepareExtraParams` | Parametri di richiesta predefiniti |
      | 19 | `createStreamFn` | Trasporto StreamFn completamente personalizzato |
      | 20 | `wrapStreamFn` | Wrapper personalizzati di header/body sul normale percorso di stream |
      | 21 | `resolveTransportTurnState` | Header/metadati nativi per turno |
      | 22 | `resolveWebSocketSessionPolicy` | Header di sessione WS nativi/cool-down |
      | 23 | `formatApiKey` | Forma personalizzata del token runtime |
      | 24 | `refreshOAuth` | Refresh OAuth personalizzato |
      | 25 | `buildAuthDoctorHint` | Guida per la riparazione dell'autenticazione |
      | 26 | `matchesContextOverflowError` | Rilevamento overflow posseduto dal provider |
      | 27 | `classifyFailoverReason` | Classificazione del rate-limit/sovraccarico posseduta dal provider |
      | 28 | `isCacheTtlEligible` | Gating TTL della cache dei prompt |
      | 29 | `buildMissingAuthMessage` | Suggerimento personalizzato per autenticazione mancante |
      | 30 | `suppressBuiltInModel` | Nasconde righe upstream obsolete |
      | 31 | `augmentModelCatalog` | Righe sintetiche di forward-compat |
      | 32 | `isBinaryThinking` | Thinking binario attivo/disattivo |
      | 33 | `supportsXHighThinking` | Supporto al reasoning `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Policy `/think` predefinita |
      | 35 | `isModernModelRef` | Corrispondenza live/smoke dei modelli |
      | 36 | `prepareRuntimeAuth` | Scambio di token prima dell'inferenza |
      | 37 | `resolveUsageAuth` | Parsing personalizzato delle credenziali di utilizzo |
      | 38 | `fetchUsageSnapshot` | Endpoint di utilizzo personalizzato |
      | 39 | `createEmbeddingProvider` | Adapter di embedding posseduto dal provider per memoria/ricerca |
      | 40 | `buildReplayPolicy` | Policy personalizzata di replay/compattazione del transcript |
      | 41 | `sanitizeReplayHistory` | Riscritture specifiche del provider sulla cronologia replay dopo la pulizia generica |
      | 42 | `validateReplayTurns` | Validazione rigorosa dei turni replay prima del runner integrato |
      | 43 | `onModelSelected` | Callback post-selezione (ad esempio telemetry) |

      Nota sul tuning del prompt:

      - `resolveSystemPromptContribution` consente a un provider di iniettare
        istruzioni di prompt di sistema cache-aware per una famiglia di modelli. Preferiscilo a
        `before_prompt_build` quando il comportamento appartiene a una famiglia provider/modello
        e dovrebbe preservare la separazione stabile/dinamica della cache.

      Per descrizioni dettagliate ed esempi reali, consulta
      [Internals: Provider Runtime Hooks](/it/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Aggiungi capacità extra (facoltativo)">
    <a id="step-5-add-extra-capabilities"></a>
    Un plugin provider può registrare speech, trascrizione realtime, voce realtime,
    comprensione dei media, generazione di immagini, generazione video, web fetch
    e web search insieme all'inferenza testuale:

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
        describeImage: async (req) => ({ text: "Una foto di..." }),
        transcribeAudio: async (req) => ({ text: "Trascrizione..." }),
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

    OpenClaw classifica questo come plugin **hybrid-capability**. Questo è il
    modello consigliato per i plugin aziendali (un plugin per vendor). Consulta
    [Internals: Capability Ownership](/it/plugins/architecture#capability-ownership-model).

    Per la generazione video, preferisci la forma di capacità mostrata sopra, consapevole della modalità:
    `generate`, `imageToVideo` e `videoToVideo`. Campi aggregati piatti come
    `maxInputImages`, `maxInputVideos` e `maxDurationSeconds` non
    sono sufficienti per pubblicizzare in modo chiaro il supporto alla modalità di trasformazione o le modalità disabilitate.

    I provider di generazione musicale dovrebbero seguire lo stesso schema:
    `generate` per la generazione basata solo su prompt ed `edit` per la generazione basata su immagine di riferimento.
    Campi aggregati piatti come `maxInputImages`,
    `supportsLyrics` e `supportsFormat` non sono sufficienti per pubblicizzare il supporto a
    edit; i blocchi espliciti `generate` / `edit` sono il contratto previsto.

  </Step>

  <Step title="Test">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Esporta il tuo oggetto di configurazione provider da index.ts o da un file dedicato
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("risolve modelli dinamici", () => {
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

      it("restituisce un catalogo null quando non c'è la chiave", async () => {
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

Non usare qui il vecchio alias di pubblicazione solo-Skills; i package plugin devono usare
`clawhub package publish`.

## Struttura dei file

```
<bundled-plugin-root>/acme-ai/
├── package.json              # metadati openclaw.providers
├── openclaw.plugin.json      # Manifest con metadati auth del provider
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Test
    └── usage.ts              # Endpoint di utilizzo (facoltativo)
```

## Riferimento per l'ordine del catalogo

`catalog.order` controlla quando il tuo catalogo viene unito rispetto ai
provider integrati:

| Ordine    | Quando         | Caso d'uso                                      |
| --------- | -------------- | ----------------------------------------------- |
| `simple`  | Primo passaggio | Provider semplici con chiave API                |
| `profile` | Dopo simple    | Provider vincolati a profili auth               |
| `paired`  | Dopo profile   | Sintetizzare più voci correlate                 |
| `late`    | Ultimo passaggio | Sovrascrivere provider esistenti (vince in caso di collisione) |

## Passaggi successivi

- [Plugin canale](/it/plugins/sdk-channel-plugins) — se il tuo plugin fornisce anche un canale
- [SDK Runtime](/it/plugins/sdk-runtime) — helper `api.runtime` (TTS, search, subagent)
- [Panoramica SDK](/it/plugins/sdk-overview) — riferimento completo agli import dei sottopercorsi
- [Internals dei plugin](/it/plugins/architecture#provider-runtime-hooks) — dettagli sugli hook ed esempi inclusi
