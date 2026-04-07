---
read_when:
    - Estás creando un nuevo plugin de proveedor de modelos
    - Quieres añadir un proxy compatible con OpenAI o un LLM personalizado a OpenClaw
    - Necesitas entender la autenticación del proveedor, los catálogos y los hooks de tiempo de ejecución
sidebarTitle: Provider Plugins
summary: Guía paso a paso para crear un plugin de proveedor de modelos para OpenClaw
title: Creación de plugins de proveedor
x-i18n:
    generated_at: "2026-04-07T05:06:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4da82a353e1bf4fe6dc09e14b8614133ac96565679627de51415926014bd3990
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Creación de plugins de proveedor

Esta guía explica cómo crear un plugin de proveedor que añada un proveedor de modelos
(LLM) a OpenClaw. Al final tendrás un proveedor con un catálogo de modelos,
autenticación por clave de API y resolución dinámica de modelos.

<Info>
  Si todavía no has creado ningún plugin de OpenClaw, lee primero
  [Primeros pasos](/es/plugins/building-plugins) para ver la estructura básica del
  paquete y la configuración del manifiesto.
</Info>

## Tutorial

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paquete y manifiesto">
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
      "description": "Proveedor de modelos Acme AI",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Clave de API de Acme AI",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Clave de API de Acme AI"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    El manifiesto declara `providerAuthEnvVars` para que OpenClaw pueda detectar
    credenciales sin cargar el tiempo de ejecución de tu plugin. `modelSupport` es opcional
    y permite que OpenClaw cargue automáticamente tu plugin de proveedor a partir de IDs abreviados de modelo
    como `acme-large` antes de que existan hooks de tiempo de ejecución. Si publicas el
    proveedor en ClawHub, esos campos `openclaw.compat` y `openclaw.build`
    son obligatorios en `package.json`.

  </Step>

  <Step title="Registrar el proveedor">
    Un proveedor mínimo necesita `id`, `label`, `auth` y `catalog`:

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

    Ese es un proveedor funcional. Los usuarios ahora pueden ejecutar
    `openclaw onboard --acme-ai-api-key <key>` y seleccionar
    `acme-ai/acme-large` como modelo.

    Para proveedores integrados que solo registran un proveedor de texto con
    autenticación por clave de API más un único tiempo de ejecución respaldado por catálogo, prefiere el helper
    más específico `defineSingleProviderPluginEntry(...)`:

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

    Si tu flujo de autenticación también necesita modificar `models.providers.*`, alias y
    el modelo predeterminado del agente durante la incorporación, usa los helpers predefinidos de
    `openclaw/plugin-sdk/provider-onboard`. Los helpers más específicos son
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` y
    `createModelCatalogPresetAppliers(...)`.

    Cuando el endpoint nativo de un proveedor admite bloques de uso en streaming en el
    transporte normal `openai-completions`, prefiere los helpers compartidos de catálogo en
    `openclaw/plugin-sdk/provider-catalog-shared` en lugar de codificar comprobaciones
    de ID de proveedor. `supportsNativeStreamingUsageCompat(...)` y
    `applyProviderNativeStreamingUsageCompat(...)` detectan la compatibilidad a partir del mapa
    de capacidades del endpoint, por lo que los endpoints nativos de estilo Moonshot/DashScope siguen
    pudiendo activarse incluso cuando un plugin usa un ID de proveedor personalizado.

  </Step>

  <Step title="Añadir resolución dinámica de modelos">
    Si tu proveedor acepta IDs arbitrarios de modelo (como un proxy o router),
    añade `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog from above

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

    Si la resolución requiere una llamada de red, usa `prepareDynamicModel` para el
    calentamiento asíncrono: `resolveDynamicModel` se vuelve a ejecutar después de que se complete.

  </Step>

  <Step title="Añadir hooks de tiempo de ejecución (según sea necesario)">
    La mayoría de los proveedores solo necesitan `catalog` + `resolveDynamicModel`. Añade hooks
    de forma incremental a medida que tu proveedor los necesite.

    Los constructores de helpers compartidos ahora cubren las familias más comunes de
    compatibilidad de repetición/herramientas, por lo que normalmente los plugins no necesitan conectar
    manualmente cada hook uno por uno:

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

    Familias de repetición disponibles actualmente:

    | Family | What it wires in |
    | --- | --- |
    | `openai-compatible` | Política compartida de repetición estilo OpenAI para transportes compatibles con OpenAI, incluido el saneamiento de IDs de llamadas a herramientas, correcciones del orden con el asistente primero y validación genérica de turnos Gemini cuando el transporte lo necesita |
    | `anthropic-by-model` | Política de repetición compatible con Claude elegida por `modelId`, para que los transportes `anthropic-message` solo apliquen limpieza de bloques de pensamiento específica de Claude cuando el modelo resuelto sea realmente un ID de Claude |
    | `google-gemini` | Política nativa de repetición de Gemini más saneamiento de repetición de arranque y modo de salida de razonamiento etiquetado |
    | `passthrough-gemini` | Saneamiento de firmas de pensamiento de Gemini para modelos Gemini que se ejecutan a través de transportes proxy compatibles con OpenAI; no habilita la validación nativa de repetición de Gemini ni las reescrituras de arranque |
    | `hybrid-anthropic-openai` | Política híbrida para proveedores que mezclan superficies de modelo `anthropic-message` y compatibles con OpenAI en un solo plugin; la eliminación opcional de bloques de pensamiento solo para Claude sigue limitada al lado Anthropic |

    Ejemplos integrados reales:

    - `google` y `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` y `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` y `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` y `zai`: `openai-compatible`

    Familias de streaming disponibles actualmente:

    | Family | What it wires in |
    | --- | --- |
    | `google-thinking` | Normalización de la carga útil de pensamiento de Gemini en la ruta de streaming compartida |
    | `kilocode-thinking` | Envoltorio de razonamiento de Kilo en la ruta de streaming proxy compartida, con `kilo/auto` e IDs de razonamiento proxy no compatibles omitiendo el pensamiento inyectado |
    | `moonshot-thinking` | Asignación de carga útil de pensamiento nativo binario de Moonshot a partir de la configuración + nivel de `/think` |
    | `minimax-fast-mode` | Reescritura de modelo de modo rápido de MiniMax en la ruta de streaming compartida |
    | `openai-responses-defaults` | Envoltorios compartidos de Responses nativas de OpenAI/Codex: encabezados de atribución, `/fast`/`serviceTier`, verbosidad del texto, búsqueda web nativa de Codex, conformación de carga útil de compatibilidad de razonamiento y gestión del contexto de Responses |
    | `openrouter-thinking` | Envoltorio de razonamiento de OpenRouter para rutas proxy, con los saltos de modelo no compatible/`auto` gestionados de forma centralizada |
    | `tool-stream-default-on` | Envoltorio `tool_stream` activado por defecto para proveedores como Z.AI que quieren streaming de herramientas salvo que se desactive explícitamente |

    Ejemplos integrados reales:

    - `google` y `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` y `minimax-portal`: `minimax-fast-mode`
    - `openai` y `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` también exporta el enum de familia
    de repetición más los helpers compartidos sobre los que se construyen esas familias. Las
    exportaciones públicas más comunes incluyen:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - constructores compartidos de repetición como `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` y
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - helpers de repetición de Gemini como `sanitizeGoogleGeminiReplayHistory(...)`
      y `resolveTaggedReasoningOutputMode()`
    - helpers de endpoint/modelo como `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` y
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` expone tanto el constructor de familias como
    los helpers públicos de envoltorio que esas familias reutilizan. Las exportaciones públicas
    más comunes incluyen:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - envoltorios compartidos de OpenAI/Codex como
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` y
      `createCodexNativeWebSearchWrapper(...)`
    - envoltorios compartidos de proxy/proveedor como `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` y `createMinimaxFastModeWrapper(...)`

    Algunos helpers de streaming permanecen intencionadamente locales al proveedor. Ejemplo
    integrado actual: `@openclaw/anthropic-provider` exporta
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` y los
    constructores de envoltorios Anthropic de nivel inferior desde su interfaz pública `api.ts` /
    `contract-api.ts`. Esos helpers siguen siendo específicos de Anthropic porque
    también codifican el manejo de betas de Claude OAuth y la restricción de `context1m`.

    Otros proveedores integrados también mantienen locales los envoltorios específicos del transporte cuando
    el comportamiento no se comparte limpiamente entre familias. Ejemplo actual: el
    plugin integrado de xAI mantiene en su propio
    `wrapStreamFn` la conformación nativa de xAI Responses, incluidas las reescrituras de alias `/fast`, el valor predeterminado de `tool_stream`,
    la limpieza de herramientas estrictas no compatibles y la eliminación
    de carga útil de razonamiento específica de xAI.

    `openclaw/plugin-sdk/provider-tools` actualmente expone una familia compartida
    de esquemas de herramientas más helpers compartidos de esquema/compatibilidad:

    - `ProviderToolCompatFamily` documenta el inventario actual de familias compartidas.
    - `buildProviderToolCompatFamilyHooks("gemini")` conecta la
      limpieza + diagnóstico de esquemas de Gemini para proveedores que necesitan esquemas de herramientas seguros para Gemini.
    - `normalizeGeminiToolSchemas(...)` e `inspectGeminiToolSchemas(...)`
      son los helpers públicos subyacentes del esquema Gemini.
    - `resolveXaiModelCompatPatch()` devuelve el parche de compatibilidad integrado de xAI:
      `toolSchemaProfile: "xai"`, palabras clave de esquema no compatibles, compatibilidad
      nativa con `web_search` y decodificación de argumentos de llamadas a herramientas con entidades HTML.
    - `applyXaiModelCompat(model)` aplica ese mismo parche de compatibilidad de xAI a un
      modelo resuelto antes de que llegue al ejecutor.

    Ejemplo integrado real: el plugin de xAI usa `normalizeResolvedModel` más
    `contributeResolvedModelCompat` para que esos metadatos de compatibilidad sigan siendo propiedad del
    proveedor en lugar de codificar reglas de xAI en el núcleo.

    El mismo patrón de raíz de paquete también sustenta otros proveedores integrados:

    - `@openclaw/openai-provider`: `api.ts` exporta constructores de proveedor,
      helpers de modelos predeterminados y constructores de proveedores en tiempo real
    - `@openclaw/openrouter-provider`: `api.ts` exporta el constructor de proveedor
      más helpers de incorporación/configuración

    <Tabs>
      <Tab title="Intercambio de tokens">
        Para proveedores que necesitan un intercambio de tokens antes de cada llamada de inferencia:

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
      <Tab title="Encabezados personalizados">
        Para proveedores que necesitan encabezados de solicitud personalizados o modificaciones del cuerpo:

        ```typescript
        // wrapStreamFn returns a StreamFn derived from ctx.streamFn
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
      <Tab title="Identidad de transporte nativo">
        Para proveedores que necesitan encabezados o metadatos nativos de solicitud/sesión en
        transportes HTTP o WebSocket genéricos:

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
      <Tab title="Uso y facturación">
        Para proveedores que exponen datos de uso/facturación:

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

    <Accordion title="Todos los hooks de proveedor disponibles">
      OpenClaw llama a los hooks en este orden. La mayoría de los proveedores solo usan 2-3:

      | # | Hook | Cuándo usarlo |
      | --- | --- | --- |
      | 1 | `catalog` | Catálogo de modelos o valores predeterminados de URL base |
      | 2 | `applyConfigDefaults` | Valores globales predeterminados controlados por el proveedor durante la materialización de la configuración |
      | 3 | `normalizeModelId` | Limpieza de alias de IDs de modelo heredados/de vista previa antes de la búsqueda |
      | 4 | `normalizeTransport` | Limpieza de `api` / `baseUrl` de la familia de proveedor antes del ensamblado genérico del modelo |
      | 5 | `normalizeConfig` | Normalizar la configuración `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Reescrituras de compatibilidad de uso de streaming nativo para proveedores configurados |
      | 7 | `resolveConfigApiKey` | Resolución de autenticación de marcador de entorno controlada por el proveedor |
      | 8 | `resolveSyntheticAuth` | Autenticación sintética local/autohospedada o basada en configuración |
      | 9 | `shouldDeferSyntheticProfileAuth` | Colocar marcadores de posición sintéticos de perfiles almacenados por detrás de la autenticación de entorno/configuración |
      | 10 | `resolveDynamicModel` | Aceptar IDs arbitrarios de modelo ascendente |
      | 11 | `prepareDynamicModel` | Obtención asíncrona de metadatos antes de resolver |
      | 12 | `normalizeResolvedModel` | Reescrituras de transporte antes del ejecutor |

    Notas sobre el comportamiento de respaldo en tiempo de ejecución:

    - `normalizeConfig` comprueba primero el proveedor coincidente y después otros
      plugins de proveedor con capacidad de hook hasta que uno cambie realmente la configuración.
      Si ningún hook de proveedor reescribe una entrada de configuración compatible de la familia Google,
      se sigue aplicando el normalizador integrado de configuración de Google.
    - `resolveConfigApiKey` usa el hook del proveedor cuando está expuesto. La ruta integrada
      `amazon-bedrock` también tiene aquí un resolvedor integrado de marcadores
      de entorno de AWS, aunque la autenticación en tiempo de ejecución de Bedrock siga usando la
      cadena predeterminada del SDK de AWS.
      | 13 | `contributeResolvedModelCompat` | Banderas de compatibilidad para modelos del proveedor detrás de otro transporte compatible |
      | 14 | `capabilities` | Bolsa heredada de capacidades estáticas; solo para compatibilidad |
      | 15 | `normalizeToolSchemas` | Limpieza de esquemas de herramientas controlada por el proveedor antes del registro |
      | 16 | `inspectToolSchemas` | Diagnóstico de esquemas de herramientas controlado por el proveedor |
      | 17 | `resolveReasoningOutputMode` | Contrato de salida de razonamiento etiquetado frente a nativo |
      | 18 | `prepareExtraParams` | Parámetros de solicitud predeterminados |
      | 19 | `createStreamFn` | Transporte `StreamFn` totalmente personalizado |
      | 20 | `wrapStreamFn` | Envoltorios personalizados de encabezados/cuerpo en la ruta normal de streaming |
      | 21 | `resolveTransportTurnState` | Encabezados/metadatos nativos por turno |
      | 22 | `resolveWebSocketSessionPolicy` | Encabezados nativos de sesión WS/enfriamiento |
      | 23 | `formatApiKey` | Forma personalizada del token en tiempo de ejecución |
      | 24 | `refreshOAuth` | Actualización personalizada de OAuth |
      | 25 | `buildAuthDoctorHint` | Orientación para reparar autenticación |
      | 26 | `matchesContextOverflowError` | Detección de desbordamiento controlada por el proveedor |
      | 27 | `classifyFailoverReason` | Clasificación de límite de velocidad/sobrecarga controlada por el proveedor |
      | 28 | `isCacheTtlEligible` | Control de TTL de la caché de prompts |
      | 29 | `buildMissingAuthMessage` | Pista personalizada para autenticación faltante |
      | 30 | `suppressBuiltInModel` | Ocultar filas ascendentes obsoletas |
      | 31 | `augmentModelCatalog` | Filas sintéticas de compatibilidad anticipada |
      | 32 | `isBinaryThinking` | Pensamiento binario activado/desactivado |
      | 33 | `supportsXHighThinking` | Compatibilidad de razonamiento `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Política predeterminada de `/think` |
      | 35 | `isModernModelRef` | Coincidencia de modelos live/smoke |
      | 36 | `prepareRuntimeAuth` | Intercambio de tokens antes de la inferencia |
      | 37 | `resolveUsageAuth` | Análisis personalizado de credenciales de uso |
      | 38 | `fetchUsageSnapshot` | Endpoint de uso personalizado |
      | 39 | `createEmbeddingProvider` | Adaptador de embeddings controlado por el proveedor para memoria/búsqueda |
      | 40 | `buildReplayPolicy` | Política personalizada de repetición/compactación de transcripciones |
      | 41 | `sanitizeReplayHistory` | Reescrituras de repetición específicas del proveedor después de la limpieza genérica |
      | 42 | `validateReplayTurns` | Validación estricta de turnos de repetición antes del ejecutor integrado |
      | 43 | `onModelSelected` | Callback posterior a la selección (por ejemplo, telemetría) |

      Nota sobre ajuste de prompts:

      - `resolveSystemPromptContribution` permite que un proveedor inyecte
        orientación de system prompt consciente de la caché para una familia de modelos. Prefiérelo frente a
        `before_prompt_build` cuando el comportamiento pertenezca a un proveedor/familia de modelos
        y deba preservar la división estable/dinámica de la caché.

      Para descripciones detalladas y ejemplos reales, consulta
      [Internals: Provider Runtime Hooks](/es/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Añadir capacidades adicionales (opcional)">
    <a id="step-5-add-extra-capabilities"></a>
    Un plugin de proveedor puede registrar voz, transcripción en tiempo real, voz
    en tiempo real, comprensión multimedia, generación de imágenes, generación de video, web fetch
    y búsqueda web junto con inferencia de texto:

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
        hint: "Fetch pages through Acme's rendering backend.",
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
          description: "Fetch a page through Acme Fetch.",
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

    OpenClaw clasifica esto como un plugin de **capacidad híbrida**. Este es el
    patrón recomendado para plugins de empresa (un plugin por proveedor). Consulta
    [Internals: Capability Ownership](/es/plugins/architecture#capability-ownership-model).

    Para la generación de video, prefiere la forma de capacidades consciente del modo que se muestra arriba:
    `generate`, `imageToVideo` y `videoToVideo`. Los campos agregados planos como
    `maxInputImages`, `maxInputVideos` y `maxDurationSeconds` no
    bastan para anunciar claramente compatibilidad con modos de transformación o modos deshabilitados.

    Los proveedores de generación musical deben seguir el mismo patrón:
    `generate` para generación solo con prompt y `edit` para generación basada en imagen
    de referencia. Los campos agregados planos como `maxInputImages`,
    `supportsLyrics` y `supportsFormat` no bastan para anunciar compatibilidad
    con edición; los bloques explícitos `generate` / `edit` son el contrato esperado.

  </Step>

  <Step title="Probar">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Export your provider config object from index.ts or a dedicated file
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Publicar en ClawHub

Los plugins de proveedor se publican igual que cualquier otro plugin de código externo:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

No uses aquí el alias heredado de publicación solo para Skills; los paquetes de plugins deben usar
`clawhub package publish`.

## Estructura de archivos

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers metadata
├── openclaw.plugin.json      # Manifest with providerAuthEnvVars
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Tests
    └── usage.ts              # Usage endpoint (optional)
```

## Referencia del orden del catálogo

`catalog.order` controla cuándo se fusiona tu catálogo respecto a los proveedores
integrados:

| Order     | When          | Use case                                        |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | Primera pasada | Proveedores simples con clave de API           |
| `profile` | Después de simple  | Proveedores condicionados por perfiles de autenticación |
| `paired`  | Después de profile | Sintetizar varias entradas relacionadas        |
| `late`    | Última pasada     | Sobrescribir proveedores existentes (gana en caso de colisión) |

## Siguientes pasos

- [Plugins de canal](/es/plugins/sdk-channel-plugins) — si tu plugin también proporciona un canal
- [SDK Runtime](/es/plugins/sdk-runtime) — helpers de `api.runtime` (TTS, búsqueda, subagente)
- [SDK Overview](/es/plugins/sdk-overview) — referencia completa de importaciones por subruta
- [Plugin Internals](/es/plugins/architecture#provider-runtime-hooks) — detalles de hooks y ejemplos integrados
