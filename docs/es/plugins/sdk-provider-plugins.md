---
read_when:
    - Estás creando un nuevo plugin de proveedor de modelos
    - Quieres agregar un proxy compatible con OpenAI o un LLM personalizado a OpenClaw
    - Necesitas entender la autenticación del proveedor, los catálogos y los hooks de runtime
sidebarTitle: Provider Plugins
summary: Guía paso a paso para crear un plugin de proveedor de modelos para OpenClaw
title: Crear plugins de proveedor
x-i18n:
    generated_at: "2026-04-11T02:46:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06d7c5da6556dc3d9673a31142ff65eb67ddc97fc0c1a6f4826a2c7693ecd5e3
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Crear plugins de proveedor

Esta guía explica paso a paso cómo crear un plugin de proveedor que agregue un proveedor de modelos
(LLM) a OpenClaw. Al final tendrás un proveedor con un catálogo de modelos,
autenticación con clave API y resolución dinámica de modelos.

<Info>
  Si todavía no has creado ningún plugin de OpenClaw, lee primero
  [Primeros pasos](/es/plugins/building-plugins) para conocer la estructura básica
  del paquete y la configuración del manifiesto.
</Info>

<Tip>
  Los plugins de proveedor agregan modelos al ciclo de inferencia normal de OpenClaw. Si el modelo
  debe ejecutarse a través de un daemon nativo de agente que controle hilos, compactación
  o eventos de herramientas, combina el proveedor con un [arnés de agente](/es/plugins/sdk-agent-harness)
  en lugar de poner los detalles del protocolo del daemon en el núcleo.
</Tip>

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

    El manifiesto declara `providerAuthEnvVars` para que OpenClaw pueda detectar
    credenciales sin cargar el runtime de tu plugin. Agrega `providerAuthAliases`
    cuando una variante del proveedor deba reutilizar la autenticación de otro id de proveedor. `modelSupport`
    es opcional y permite que OpenClaw cargue automáticamente tu plugin de proveedor a partir de ids de modelo abreviados
    como `acme-large` antes de que existan hooks de runtime. Si publicas el
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
    `acme-ai/acme-large` como su modelo.

    Si el proveedor upstream usa tokens de control distintos de los de OpenClaw, agrega una
    pequeña transformación bidireccional de texto en lugar de reemplazar la ruta del stream:

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

    `input` reescribe el prompt final del sistema y el contenido de los mensajes de texto antes
    del transporte. `output` reescribe los deltas de texto del asistente y el texto final antes de que
    OpenClaw analice sus propios marcadores de control o entregue el contenido al canal.

    Para proveedores incluidos que solo registran un proveedor de texto con autenticación por clave API
    más un único runtime respaldado por catálogo, prefiere el helper más acotado
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

    Si tu flujo de autenticación también necesita parchear `models.providers.*`, alias y
    el modelo predeterminado del agente durante la incorporación, usa los helpers predefinidos de
    `openclaw/plugin-sdk/provider-onboard`. Los helpers más acotados son
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` y
    `createModelCatalogPresetAppliers(...)`.

    Cuando el endpoint nativo de un proveedor admite bloques de uso en streaming en el
    transporte normal `openai-completions`, prefiere los helpers de catálogo compartidos en
    `openclaw/plugin-sdk/provider-catalog-shared` en lugar de codificar verificaciones por id de proveedor. `supportsNativeStreamingUsageCompat(...)` y
    `applyProviderNativeStreamingUsageCompat(...)` detectan la compatibilidad a partir del mapa de capacidades del endpoint,
    por lo que los endpoints nativos al estilo Moonshot/DashScope también optan por esta función incluso cuando un plugin usa un id de proveedor personalizado.

  </Step>

  <Step title="Agregar resolución dinámica de modelos">
    Si tu proveedor acepta ids de modelo arbitrarios (como un proxy o router),
    agrega `resolveDynamicModel`:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog de arriba

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

    Si la resolución requiere una llamada de red, usa `prepareDynamicModel` para un
    calentamiento asíncrono: `resolveDynamicModel` se ejecuta de nuevo después de que termine.

  </Step>

  <Step title="Agregar hooks de runtime (según sea necesario)">
    La mayoría de los proveedores solo necesitan `catalog` + `resolveDynamicModel`. Agrega hooks
    de forma incremental según lo requiera tu proveedor.

    Los constructores de helpers compartidos ahora cubren las familias más comunes de replay y compatibilidad de herramientas,
    por lo que normalmente los plugins no necesitan cablear cada hook uno por uno:

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

    Familias de replay disponibles hoy:

    | Family | Qué configura |
    | --- | --- |
    | `openai-compatible` | Política compartida de replay al estilo OpenAI para transportes compatibles con OpenAI, incluida la sanitización de tool-call-id, correcciones del orden asistente-primero y validación genérica de turnos Gemini cuando el transporte la necesita |
    | `anthropic-by-model` | Política de replay consciente de Claude elegida por `modelId`, para que los transportes de mensajes de Anthropic solo reciban limpieza de bloques de pensamiento específica de Claude cuando el modelo resuelto sea realmente un id de Claude |
    | `google-gemini` | Política nativa de replay de Gemini más sanitización de replay de arranque y modo etiquetado de salida de razonamiento |
    | `passthrough-gemini` | Sanitización de thought-signature de Gemini para modelos Gemini que se ejecutan a través de transportes proxy compatibles con OpenAI; no habilita validación nativa de replay de Gemini ni reescrituras de arranque |
    | `hybrid-anthropic-openai` | Política híbrida para proveedores que mezclan superficies de modelos de mensajes Anthropic y compatibles con OpenAI en un mismo plugin; la eliminación opcional de bloques de pensamiento solo para Claude se mantiene limitada al lado Anthropic |

    Ejemplos reales incluidos:

    - `google` y `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` y `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` y `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` y `zai`: `openai-compatible`

    Familias de stream disponibles hoy:

    | Family | Qué configura |
    | --- | --- |
    | `google-thinking` | Normalización de la carga útil de razonamiento de Gemini en la ruta de stream compartida |
    | `kilocode-thinking` | Envoltura de razonamiento de Kilo en la ruta de stream proxy compartida, con `kilo/auto` e ids de razonamiento de proxy no compatibles omitiendo el razonamiento inyectado |
    | `moonshot-thinking` | Mapeo de la carga útil nativa de razonamiento binario de Moonshot desde la configuración + nivel de `/think` |
    | `minimax-fast-mode` | Reescritura de modelo de modo rápido de MiniMax en la ruta de stream compartida |
    | `openai-responses-defaults` | Envolturas nativas compartidas de OpenAI/Codex Responses: encabezados de atribución, `/fast`/`serviceTier`, verbosidad de texto, búsqueda web nativa de Codex, conformación de carga útil de compatibilidad de razonamiento y gestión de contexto de Responses |
    | `openrouter-thinking` | Envoltura de razonamiento de OpenRouter para rutas proxy, con omisiones de modelos no compatibles/`auto` gestionadas de forma central |
    | `tool-stream-default-on` | Envoltura `tool_stream` activada por defecto para proveedores como Z.AI que quieren streaming de herramientas salvo que se desactive explícitamente |

    Ejemplos reales incluidos:

    - `google` y `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` y `minimax-portal`: `minimax-fast-mode`
    - `openai` y `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` también exporta el enum de familia
    de replay además de los helpers compartidos sobre los que se construyen esas familias. Entre las
    exportaciones públicas comunes se incluyen:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - constructores compartidos de replay como `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` y
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - helpers de replay de Gemini como `sanitizeGoogleGeminiReplayHistory(...)`
      y `resolveTaggedReasoningOutputMode()`
    - helpers de endpoint/modelo como `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` y
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` expone tanto el constructor de familias como
    los helpers públicos de envoltura que esas familias reutilizan. Entre las exportaciones públicas
    comunes se incluyen:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - envolturas compartidas de OpenAI/Codex como
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` y
      `createCodexNativeWebSearchWrapper(...)`
    - envolturas compartidas de proxy/proveedor como `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` y `createMinimaxFastModeWrapper(...)`

    Algunos helpers de stream siguen siendo locales al proveedor intencionalmente. Ejemplo
    incluido actual: `@openclaw/anthropic-provider` exporta
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` y los
    constructores de envoltura de Anthropic de nivel inferior desde su interfaz pública `api.ts` /
    `contract-api.ts`. Esos helpers siguen siendo específicos de Anthropic porque
    también codifican el manejo beta de Claude OAuth y el control de `context1m`.

    Otros proveedores incluidos también mantienen locales las envolturas específicas del transporte cuando
    el comportamiento no se comparte limpiamente entre familias. Ejemplo actual: el
    plugin xAI incluido mantiene la conformación nativa de xAI Responses en su propio
    `wrapStreamFn`, incluida la reescritura de alias `/fast`, `tool_stream` por defecto,
    limpieza de herramientas estrictas no compatibles y eliminación de
    carga útil de razonamiento específica de xAI.

    `openclaw/plugin-sdk/provider-tools` actualmente expone una familia compartida
    de esquemas de herramientas más helpers compartidos de esquema/compatibilidad:

    - `ProviderToolCompatFamily` documenta hoy el inventario compartido de familias.
    - `buildProviderToolCompatFamilyHooks("gemini")` configura la
      limpieza de esquemas de Gemini + diagnósticos para proveedores que necesitan esquemas de herramientas seguros para Gemini.
    - `normalizeGeminiToolSchemas(...)` y `inspectGeminiToolSchemas(...)`
      son los helpers públicos subyacentes para esquemas de Gemini.
    - `resolveXaiModelCompatPatch()` devuelve el parche de compatibilidad de xAI incluido:
      `toolSchemaProfile: "xai"`, palabras clave de esquema no compatibles, soporte nativo de
      `web_search` y decodificación de argumentos de llamadas a herramientas con entidades HTML.
    - `applyXaiModelCompat(model)` aplica ese mismo parche de compatibilidad de xAI a un
      modelo resuelto antes de que llegue al runner.

    Ejemplo real incluido: el plugin xAI usa `normalizeResolvedModel` más
    `contributeResolvedModelCompat` para que esa metadata de compatibilidad siga siendo propiedad del
    proveedor en lugar de codificar reglas de xAI en el núcleo.

    El mismo patrón de raíz de paquete también respalda a otros proveedores incluidos:

    - `@openclaw/openai-provider`: `api.ts` exporta constructores de proveedor,
      helpers de modelo predeterminado y constructores de proveedores realtime
    - `@openclaw/openrouter-provider`: `api.ts` exporta el constructor del proveedor
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
        // wrapStreamFn devuelve una StreamFn derivada de ctx.streamFn
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
      <Tab title="Identidad nativa del transporte">
        Para proveedores que necesitan encabezados o metadata nativos de solicitud/sesión en
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
      OpenClaw llama a los hooks en este orden. La mayoría de los proveedores solo usan 2 o 3:

      | # | Hook | Cuándo usarlo |
      | --- | --- | --- |
      | 1 | `catalog` | Catálogo de modelos o valores predeterminados de base URL |
      | 2 | `applyConfigDefaults` | Valores predeterminados globales del proveedor durante la materialización de la configuración |
      | 3 | `normalizeModelId` | Limpieza de alias de ids de modelo heredados/preview antes de la búsqueda |
      | 4 | `normalizeTransport` | Limpieza de `api` / `baseUrl` de la familia de proveedores antes del ensamblado genérico del modelo |
      | 5 | `normalizeConfig` | Normalizar la configuración `models.providers.<id>` |
      | 6 | `applyNativeStreamingUsageCompat` | Reescrituras de compatibilidad de uso nativo en streaming para proveedores de configuración |
      | 7 | `resolveConfigApiKey` | Resolución de autenticación de marcador env propiedad del proveedor |
      | 8 | `resolveSyntheticAuth` | Autenticación sintética local/alojada por cuenta propia o respaldada por configuración |
      | 9 | `shouldDeferSyntheticProfileAuth` | Relega marcadores sintéticos almacenados de perfil detrás de autenticación env/config |
      | 10 | `resolveDynamicModel` | Aceptar ids de modelo upstream arbitrarios |
      | 11 | `prepareDynamicModel` | Obtención asíncrona de metadata antes de resolver |
      | 12 | `normalizeResolvedModel` | Reescrituras de transporte antes del runner |

    Notas sobre el respaldo en runtime:

    - `normalizeConfig` comprueba primero el proveedor coincidente y luego otros
      plugins de proveedor con capacidad de hooks hasta que uno realmente cambie la configuración.
      Si ningún hook de proveedor reescribe una entrada de configuración compatible de la familia Google, aún
      se aplica el normalizador de configuración de Google incluido.
    - `resolveConfigApiKey` usa el hook del proveedor cuando está expuesto. La ruta incluida
      `amazon-bedrock` también tiene aquí un resolvedor integrado de marcadores env de AWS,
      aunque la autenticación de runtime de Bedrock en sí sigue usando la cadena predeterminada del AWS SDK.
      | 13 | `contributeResolvedModelCompat` | Marcas de compatibilidad para modelos del proveedor detrás de otro transporte compatible |
      | 14 | `capabilities` | Bolsa estática heredada de capacidades; solo compatibilidad |
      | 15 | `normalizeToolSchemas` | Limpieza de esquemas de herramientas propiedad del proveedor antes del registro |
      | 16 | `inspectToolSchemas` | Diagnósticos de esquemas de herramientas propiedad del proveedor |
      | 17 | `resolveReasoningOutputMode` | Contrato de salida de razonamiento etiquetado frente a nativo |
      | 18 | `prepareExtraParams` | Parámetros de solicitud predeterminados |
      | 19 | `createStreamFn` | Transporte StreamFn totalmente personalizado |
      | 20 | `wrapStreamFn` | Envolturas de encabezados/cuerpo personalizados en la ruta de stream normal |
      | 21 | `resolveTransportTurnState` | Encabezados/metadata nativos por turno |
      | 22 | `resolveWebSocketSessionPolicy` | Encabezados de sesión WS nativos/enfriamiento |
      | 23 | `formatApiKey` | Forma personalizada del token de runtime |
      | 24 | `refreshOAuth` | Actualización personalizada de OAuth |
      | 25 | `buildAuthDoctorHint` | Guía de reparación de autenticación |
      | 26 | `matchesContextOverflowError` | Detección de desbordamiento propiedad del proveedor |
      | 27 | `classifyFailoverReason` | Clasificación de límite de velocidad/sobrecarga propiedad del proveedor |
      | 28 | `isCacheTtlEligible` | Control de TTL de caché de prompts |
      | 29 | `buildMissingAuthMessage` | Sugerencia personalizada para autenticación faltante |
      | 30 | `suppressBuiltInModel` | Ocultar filas upstream obsoletas |
      | 31 | `augmentModelCatalog` | Filas sintéticas de compatibilidad futura |
      | 32 | `isBinaryThinking` | Razonamiento binario activado/desactivado |
      | 33 | `supportsXHighThinking` | Compatibilidad de razonamiento `xhigh` |
      | 34 | `resolveDefaultThinkingLevel` | Política predeterminada de `/think` |
      | 35 | `isModernModelRef` | Coincidencia de modelos live/smoke |
      | 36 | `prepareRuntimeAuth` | Intercambio de tokens antes de la inferencia |
      | 37 | `resolveUsageAuth` | Análisis personalizado de credenciales de uso |
      | 38 | `fetchUsageSnapshot` | Endpoint de uso personalizado |
      | 39 | `createEmbeddingProvider` | Adaptador de embeddings propiedad del proveedor para memoria/búsqueda |
      | 40 | `buildReplayPolicy` | Política personalizada de replay/compactación de transcripción |
      | 41 | `sanitizeReplayHistory` | Reescrituras de replay específicas del proveedor después de la limpieza genérica |
      | 42 | `validateReplayTurns` | Validación estricta de turnos de replay antes del runner integrado |
      | 43 | `onModelSelected` | Callback posterior a la selección (por ejemplo, telemetría) |

      Nota sobre el ajuste de prompts:

      - `resolveSystemPromptContribution` permite que un proveedor inyecte
        guía del prompt del sistema consciente de la caché para una familia de modelos. Prefiérelo frente a
        `before_prompt_build` cuando el comportamiento pertenezca a una familia proveedor/modelo
        y deba preservar la separación estable/dinámica de la caché.

      Para ver descripciones detalladas y ejemplos del mundo real, consulta
      [Internals: Hooks de runtime de proveedores](/es/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Agregar capacidades adicionales (opcional)">
    <a id="step-5-add-extra-capabilities"></a>
    Un plugin de proveedor puede registrar voz, transcripción realtime, voz realtime,
    comprensión de medios, generación de imágenes, generación de video, obtención web
    y búsqueda web junto con la inferencia de texto:

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
        hint: "Obtener páginas a través del backend de renderizado de Acme.",
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
          description: "Obtener una página mediante Acme Fetch.",
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

    OpenClaw clasifica esto como un plugin de **capacidades híbridas**. Este es el
    patrón recomendado para plugins de empresa (un plugin por proveedor). Consulta
    [Internals: Capability Ownership](/es/plugins/architecture#capability-ownership-model).

    Para la generación de video, prefiere la forma de capacidades consciente del modo que se muestra arriba:
    `generate`, `imageToVideo` y `videoToVideo`. Los campos agregados planos como
    `maxInputImages`, `maxInputVideos` y `maxDurationSeconds` no
    bastan para anunciar de forma limpia la compatibilidad con modos de transformación o los modos desactivados.

    Los proveedores de generación de música deben seguir el mismo patrón:
    `generate` para la generación solo con prompt y `edit` para la generación
    basada en imagen de referencia. Los campos agregados planos como `maxInputImages`,
    `supportsLyrics` y `supportsFormat` no bastan para anunciar la compatibilidad con edición;
    el contrato esperado son bloques explícitos `generate` / `edit`.

  </Step>

  <Step title="Probar">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Exporta tu objeto de configuración del proveedor desde index.ts o un archivo dedicado
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

No uses aquí el alias heredado de publicación solo de Skills; los paquetes de plugins deben usar
`clawhub package publish`.

## Estructura de archivos

```
<bundled-plugin-root>/acme-ai/
├── package.json              # metadata de openclaw.providers
├── openclaw.plugin.json      # Manifiesto con metadata de autenticación del proveedor
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Pruebas
    └── usage.ts              # Endpoint de uso (opcional)
```

## Referencia del orden del catálogo

`catalog.order` controla cuándo se fusiona tu catálogo respecto de los
proveedores integrados:

| Order     | Cuándo       | Caso de uso                                     |
| --------- | ------------ | ----------------------------------------------- |
| `simple`  | Primera pasada | Proveedores simples con clave API             |
| `profile` | Después de simple | Proveedores condicionados por perfiles de autenticación |
| `paired`  | Después de profile | Sintetizar varias entradas relacionadas   |
| `late`    | Última pasada | Anular proveedores existentes (gana en caso de colisión) |

## Siguientes pasos

- [Plugins de canal](/es/plugins/sdk-channel-plugins) — si tu plugin también proporciona un canal
- [SDK Runtime](/es/plugins/sdk-runtime) — helpers de `api.runtime` (TTS, búsqueda, subagente)
- [Resumen del SDK](/es/plugins/sdk-overview) — referencia completa de importaciones por subruta
- [Internals del plugin](/es/plugins/architecture#provider-runtime-hooks) — detalles de hooks y ejemplos incluidos
