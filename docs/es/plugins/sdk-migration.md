---
read_when:
    - Ves la advertencia OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Ves la advertencia OPENCLAW_EXTENSION_API_DEPRECATED
    - Estás actualizando un plugin a la arquitectura moderna de plugins
    - Mantienes un plugin externo de OpenClaw
sidebarTitle: Migrate to SDK
summary: Migra desde la capa heredada de compatibilidad hacia el SDK moderno de plugins
title: Migración del SDK de plugins
x-i18n:
    generated_at: "2026-04-07T05:05:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3691060e9dc00ca8bee49240a047f0479398691bd14fb96e9204cc9243fdb32c
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migración del SDK de plugins

OpenClaw ha pasado de una amplia capa heredada de compatibilidad a una arquitectura moderna
de plugins con importaciones enfocadas y documentadas. Si tu plugin se creó antes de
la nueva arquitectura, esta guía te ayudará a migrarlo.

## Qué está cambiando

El sistema antiguo de plugins proporcionaba dos superficies completamente abiertas que permitían a los plugins importar
todo lo que necesitaban desde un único punto de entrada:

- **`openclaw/plugin-sdk/compat`** — una única importación que reexportaba decenas de
  helpers. Se introdujo para mantener el funcionamiento de los plugins más antiguos basados en hooks mientras se construía
  la nueva arquitectura de plugins.
- **`openclaw/extension-api`** — un puente que daba a los plugins acceso directo a
  helpers del lado del host, como el ejecutor integrado de agentes.

Ambas superficies ahora están **obsoletas**. Siguen funcionando en tiempo de ejecución, pero los plugins nuevos
no deben usarlas, y los plugins existentes deben migrar antes de que la próxima
versión mayor las elimine.

<Warning>
  La capa heredada de compatibilidad se eliminará en una futura versión mayor.
  Los plugins que sigan importando desde estas superficies dejarán de funcionar cuando eso ocurra.
</Warning>

## Por qué cambió esto

El enfoque antiguo causaba problemas:

- **Inicio lento** — importar un helper cargaba docenas de módulos no relacionados
- **Dependencias circulares** — las reexportaciones amplias facilitaban la creación de ciclos de importación
- **Superficie de API poco clara** — no había forma de distinguir qué exportaciones eran estables frente a cuáles eran internas

El SDK moderno de plugins soluciona esto: cada ruta de importación (`openclaw/plugin-sdk/\<subpath\>`)
es un módulo pequeño, autocontenido, con un propósito claro y un contrato documentado.

Las uniones heredadas de conveniencia de proveedores para canales empaquetados también han desaparecido. Importaciones
como `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
las uniones helper con marca de canal, y
`openclaw/plugin-sdk/telegram-core` eran atajos privados del mono-repo, no
contratos estables de plugins. Usa en su lugar subrutas genéricas y acotadas del SDK. Dentro del
workspace de plugins empaquetados, mantén los helpers propiedad del proveedor en el propio
`api.ts` o `runtime-api.ts` de ese plugin.

Ejemplos actuales de proveedores empaquetados:

- Anthropic mantiene helpers de flujo específicos de Claude en su propia unión `api.ts` /
  `contract-api.ts`
- OpenAI mantiene constructores de proveedores, helpers de modelos predeterminados y constructores de proveedores
  realtime en su propio `api.ts`
- OpenRouter mantiene el constructor del proveedor y los helpers de incorporación/configuración en su propio
  `api.ts`

## Cómo migrar

<Steps>
  <Step title="Auditar el comportamiento alternativo del wrapper de Windows">
    Si tu plugin usa `openclaw/plugin-sdk/windows-spawn`, los wrappers de Windows
    `.cmd`/`.bat` no resueltos ahora fallan de forma cerrada a menos que pases explícitamente
    `allowShellFallback: true`.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Only set this for trusted compatibility callers that intentionally
      // accept shell-mediated fallback.
      allowShellFallback: true,
    });
    ```

    Si tu llamador no depende intencionadamente del modo alternativo del shell, no establezcas
    `allowShellFallback` y maneja en su lugar el error lanzado.

  </Step>

  <Step title="Buscar importaciones obsoletas">
    Busca en tu plugin importaciones desde cualquiera de las dos superficies obsoletas:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Reemplazar por importaciones enfocadas">
    Cada exportación de la superficie antigua se corresponde con una ruta de importación moderna específica:

    ```typescript
    // Before (deprecated backwards-compatibility layer)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (modern focused imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Para los helpers del lado del host, usa el runtime del plugin inyectado en lugar de importar
    directamente:

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    El mismo patrón se aplica a otros helpers heredados del puente:

    | Importación antigua | Equivalente moderno |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helpers del almacén de sesiones | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Compilar y probar">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Referencia de rutas de importación

<Accordion title="Tabla de rutas de importación comunes">
  | Ruta de importación | Propósito | Exportaciones clave |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper canónico de entrada del plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Reexportación heredada paraguas para definiciones/constructores de entrada de canal | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Exportación del esquema de configuración raíz | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper de entrada de proveedor único | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definiciones y constructores enfocados de entrada de canal | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helpers compartidos del asistente de configuración | Prompts de lista de permitidos, constructores de estado de configuración |
  | `plugin-sdk/setup-runtime` | Helpers de runtime en tiempo de configuración | Adaptadores de parche de configuración seguros para importación, helpers de notas de búsqueda, `promptResolvedAllowFrom`, `splitSetupEntries`, proxies de configuración delegados |
  | `plugin-sdk/setup-adapter-runtime` | Helpers del adaptador de configuración | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helpers de herramientas de configuración | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helpers para varias cuentas | Helpers de lista/configuración/cierres de acciones de cuentas |
  | `plugin-sdk/account-id` | Helpers de ID de cuenta | `DEFAULT_ACCOUNT_ID`, normalización de ID de cuenta |
  | `plugin-sdk/account-resolution` | Helpers de búsqueda de cuenta | Helpers de búsqueda de cuenta + alternativa predeterminada |
  | `plugin-sdk/account-helpers` | Helpers acotados de cuenta | Helpers de lista de cuentas/acciones de cuenta |
  | `plugin-sdk/channel-setup` | Adaptadores del asistente de configuración | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, además de `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitivas de vinculación para mensajes directos | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Cableado de prefijo de respuesta + escritura | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Fábricas de adaptadores de configuración | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Constructores de esquemas de configuración | Tipos de esquema de configuración de canal |
  | `plugin-sdk/telegram-command-config` | Helpers de configuración de comandos de Telegram | Normalización de nombres de comandos, recorte de descripciones, validación de duplicados/conflictos |
  | `plugin-sdk/channel-policy` | Resolución de políticas de grupo/mensajes directos | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Seguimiento de estado de cuenta | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helpers de sobre entrante | Helpers compartidos de ruta + constructor de sobre |
  | `plugin-sdk/inbound-reply-dispatch` | Helpers de respuesta entrante | Helpers compartidos de registrar y despachar |
  | `plugin-sdk/messaging-targets` | Análisis de objetivos de mensajería | Helpers de análisis/coincidencia de objetivos |
  | `plugin-sdk/outbound-media` | Helpers de multimedia saliente | Carga compartida de multimedia saliente |
  | `plugin-sdk/outbound-runtime` | Helpers de runtime saliente | Helpers de identidad/despacho saliente |
  | `plugin-sdk/thread-bindings-runtime` | Helpers de vínculo de hilos | Ciclo de vida de vínculos de hilos y helpers de adaptador |
  | `plugin-sdk/agent-media-payload` | Helpers heredados de carga multimedia | Constructor de carga multimedia del agente para diseños heredados de campos |
  | `plugin-sdk/channel-runtime` | Shim de compatibilidad obsoleto | Solo utilidades heredadas de runtime de canal |
  | `plugin-sdk/channel-send-result` | Tipos de resultado de envío | Tipos de resultado de respuesta |
  | `plugin-sdk/runtime-store` | Almacenamiento persistente de plugins | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helpers amplios de runtime | Helpers de runtime/logging/backup/instalación de plugins |
  | `plugin-sdk/runtime-env` | Helpers acotados de entorno de runtime | Logger/entorno de runtime, timeout, retry y helpers de backoff |
  | `plugin-sdk/plugin-runtime` | Helpers compartidos de runtime de plugins | Helpers de comandos/hooks/http/interactivos de plugins |
  | `plugin-sdk/hook-runtime` | Helpers de canalización de hooks | Helpers compartidos de canalización de webhook/hooks internos |
  | `plugin-sdk/lazy-runtime` | Helpers de runtime diferido | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helpers de procesos | Helpers compartidos de exec |
  | `plugin-sdk/cli-runtime` | Helpers de runtime de CLI | Formateo de comandos, esperas, helpers de versión |
  | `plugin-sdk/gateway-runtime` | Helpers de Gateway | Cliente de Gateway y helpers de parche de estado de canal |
  | `plugin-sdk/config-runtime` | Helpers de configuración | Helpers de carga/escritura de configuración |
  | `plugin-sdk/telegram-command-config` | Helpers de comandos de Telegram | Helpers de validación de comandos de Telegram estables como alternativa cuando la superficie de contrato empaquetada de Telegram no está disponible |
  | `plugin-sdk/approval-runtime` | Helpers de prompts de aprobación | Carga útil de aprobación de exec/plugin, helpers de capacidad/perfil de aprobación, helpers nativos de enrutamiento/runtime de aprobación |
  | `plugin-sdk/approval-auth-runtime` | Helpers de autenticación de aprobación | Resolución de aprobador, autenticación de acción en el mismo chat |
  | `plugin-sdk/approval-client-runtime` | Helpers de cliente de aprobación | Helpers nativos de perfil/filtro de aprobación de exec |
  | `plugin-sdk/approval-delivery-runtime` | Helpers de entrega de aprobación | Adaptadores nativos de capacidad/entrega de aprobación |
  | `plugin-sdk/approval-native-runtime` | Helpers de objetivo de aprobación | Helpers nativos de objetivo de aprobación/vinculación de cuenta |
  | `plugin-sdk/approval-reply-runtime` | Helpers de respuesta de aprobación | Helpers de carga útil de respuesta de aprobación de exec/plugin |
  | `plugin-sdk/security-runtime` | Helpers de seguridad | Helpers compartidos de confianza, cierre de mensajes directos, contenido externo y recopilación de secretos |
  | `plugin-sdk/ssrf-policy` | Helpers de política SSRF | Helpers de lista de permitidos de hosts y política de red privada |
  | `plugin-sdk/ssrf-runtime` | Helpers de runtime SSRF | Helpers de dispatcher fijado, fetch protegido y política SSRF |
  | `plugin-sdk/collection-runtime` | Helpers de caché acotada | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helpers de cierre de diagnóstico | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helpers de formato de errores | `formatUncaughtError`, `isApprovalNotFoundError`, helpers de grafo de errores |
  | `plugin-sdk/fetch-runtime` | Helpers de fetch/proxy envueltos | `resolveFetch`, helpers de proxy |
  | `plugin-sdk/host-runtime` | Helpers de normalización de host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helpers de reintento | `RetryConfig`, `retryAsync`, ejecutores de políticas |
  | `plugin-sdk/allow-from` | Formato de lista de permitidos | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapeo de entradas de lista de permitidos | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Cierre de comandos y helpers de superficie de comandos | `resolveControlCommandGate`, helpers de autorización de remitente, helpers de registro de comandos |
  | `plugin-sdk/secret-input` | Análisis de entrada de secretos | Helpers de entrada de secretos |
  | `plugin-sdk/webhook-ingress` | Helpers de solicitudes webhook | Utilidades de destino webhook |
  | `plugin-sdk/webhook-request-guards` | Helpers de guardas de solicitudes webhook | Helpers de lectura/límite de cuerpo de solicitud |
  | `plugin-sdk/reply-runtime` | Runtime compartido de respuestas | Despacho entrante, heartbeat, planificador de respuestas, fragmentación |
  | `plugin-sdk/reply-dispatch-runtime` | Helpers acotados de despacho de respuestas | Helpers de finalización + despacho de proveedor |
  | `plugin-sdk/reply-history` | Helpers de historial de respuestas | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Planificación de referencias de respuesta | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helpers de fragmentación de respuestas | Helpers de fragmentación de texto/markdown |
  | `plugin-sdk/session-store-runtime` | Helpers de almacén de sesiones | Ruta del almacén + helpers de updated-at |
  | `plugin-sdk/state-paths` | Helpers de rutas de estado | Helpers de estado y directorio OAuth |
  | `plugin-sdk/routing` | Helpers de enrutamiento/clave de sesión | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helpers de normalización de clave de sesión |
  | `plugin-sdk/status-helpers` | Helpers de estado de canal | Constructores de resúmenes de estado de canal/cuenta, valores predeterminados de estado de runtime, helpers de metadatos de incidencias |
  | `plugin-sdk/target-resolver-runtime` | Helpers de resolución de objetivos | Helpers compartidos de resolución de objetivos |
  | `plugin-sdk/string-normalization-runtime` | Helpers de normalización de cadenas | Helpers de normalización de slug/cadenas |
  | `plugin-sdk/request-url` | Helpers de URL de solicitud | Extraer URLs de cadena de entradas similares a solicitud |
  | `plugin-sdk/run-command` | Helpers de comandos temporizados | Ejecutor de comandos temporizados con stdout/stderr normalizados |
  | `plugin-sdk/param-readers` | Lectores de parámetros | Lectores comunes de parámetros de herramientas/CLI |
  | `plugin-sdk/tool-send` | Extracción de envío de herramienta | Extraer campos canónicos de objetivo de envío de argumentos de herramienta |
  | `plugin-sdk/temp-path` | Helpers de rutas temporales | Helpers compartidos de rutas temporales de descarga |
  | `plugin-sdk/logging-core` | Helpers de logging | Logger de subsistema y helpers de redacción |
  | `plugin-sdk/markdown-table-runtime` | Helpers de tablas Markdown | Helpers de modo de tabla Markdown |
  | `plugin-sdk/reply-payload` | Tipos de respuestas de mensajes | Tipos de carga útil de respuesta |
  | `plugin-sdk/provider-setup` | Helpers seleccionados de configuración de proveedores locales/alojados por uno mismo | Helpers de descubrimiento/configuración de proveedores autoalojados |
  | `plugin-sdk/self-hosted-provider-setup` | Helpers enfocados de configuración de proveedores autoalojados compatibles con OpenAI | Los mismos helpers de descubrimiento/configuración de proveedores autoalojados |
  | `plugin-sdk/provider-auth-runtime` | Helpers de autenticación de runtime del proveedor | Helpers de resolución de API key en runtime |
  | `plugin-sdk/provider-auth-api-key` | Helpers de configuración de API key del proveedor | Helpers de incorporación/escritura de perfil de API key |
  | `plugin-sdk/provider-auth-result` | Helpers de resultado de autenticación del proveedor | Constructor estándar de resultados de autenticación OAuth |
  | `plugin-sdk/provider-auth-login` | Helpers de inicio de sesión interactivo del proveedor | Helpers compartidos de inicio de sesión interactivo |
  | `plugin-sdk/provider-env-vars` | Helpers de variables de entorno del proveedor | Helpers de búsqueda de variables de entorno de autenticación del proveedor |
  | `plugin-sdk/provider-model-shared` | Helpers compartidos de modelo/repetición de proveedor | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, constructores compartidos de políticas de repetición, helpers de endpoints de proveedor y helpers de normalización de IDs de modelo |
  | `plugin-sdk/provider-catalog-shared` | Helpers compartidos de catálogo de proveedor | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Parches de incorporación de proveedor | Helpers de configuración de incorporación |
  | `plugin-sdk/provider-http` | Helpers HTTP de proveedor | Helpers genéricos de capacidades HTTP/endpoint de proveedor |
  | `plugin-sdk/provider-web-fetch` | Helpers de web-fetch de proveedor | Helpers de registro/caché de proveedores de web-fetch |
  | `plugin-sdk/provider-web-search-contract` | Helpers de contrato de web-search de proveedor | Helpers acotados de contrato de configuración/credenciales de web-search como `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` y setters/getters de credenciales acotados |
  | `plugin-sdk/provider-web-search` | Helpers de web-search de proveedor | Helpers de registro/caché/runtime de proveedores de web-search |
  | `plugin-sdk/provider-tools` | Helpers de compatibilidad de herramientas/esquemas de proveedor | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, limpieza + diagnósticos de esquema Gemini y helpers de compatibilidad de xAI como `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helpers de uso de proveedor | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` y otros helpers de uso de proveedor |
  | `plugin-sdk/provider-stream` | Helpers de wrapper de stream de proveedor | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipos de wrapper de stream y helpers compartidos de wrappers para Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Cola asíncrona ordenada | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helpers compartidos de multimedia | Helpers de fetch/transformación/almacenamiento de multimedia más constructores de carga multimedia |
  | `plugin-sdk/media-generation-runtime` | Helpers compartidos de generación multimedia | Helpers compartidos de failover, selección de candidatos y mensajes de modelo faltante para generación de imagen/video/música |
  | `plugin-sdk/media-understanding` | Helpers de comprensión multimedia | Tipos de proveedor de comprensión multimedia más exportaciones helper orientadas a proveedor para imagen/audio |
  | `plugin-sdk/text-runtime` | Helpers compartidos de texto | Eliminación de texto visible para el asistente, helpers de renderizado/fragmentación/tabla de markdown, helpers de redacción, helpers de etiquetas directivas, utilidades de texto seguro y helpers relacionados de texto/logging |
  | `plugin-sdk/text-chunking` | Helpers de fragmentación de texto | Helper de fragmentación de texto saliente |
  | `plugin-sdk/speech` | Helpers de voz | Tipos de proveedor de voz más exportaciones helper orientadas a proveedor para directivas, registro y validación |
  | `plugin-sdk/speech-core` | Núcleo compartido de voz | Tipos de proveedor de voz, registro, directivas, normalización |
  | `plugin-sdk/realtime-transcription` | Helpers de transcripción realtime | Tipos de proveedor y helpers de registro |
  | `plugin-sdk/realtime-voice` | Helpers de voz realtime | Tipos de proveedor y helpers de registro |
  | `plugin-sdk/image-generation-core` | Núcleo compartido de generación de imágenes | Tipos de generación de imágenes, failover, autenticación y helpers de registro |
  | `plugin-sdk/music-generation` | Helpers de generación de música | Tipos de proveedor/solicitud/resultado de generación de música |
  | `plugin-sdk/music-generation-core` | Núcleo compartido de generación de música | Tipos de generación de música, helpers de failover, búsqueda de proveedor y análisis de model-ref |
  | `plugin-sdk/video-generation` | Helpers de generación de video | Tipos de proveedor/solicitud/resultado de generación de video |
  | `plugin-sdk/video-generation-core` | Núcleo compartido de generación de video | Tipos de generación de video, helpers de failover, búsqueda de proveedor y análisis de model-ref |
  | `plugin-sdk/interactive-runtime` | Helpers de respuesta interactiva | Normalización/reducción de carga útil de respuesta interactiva |
  | `plugin-sdk/channel-config-primitives` | Primitivas de configuración de canal | Primitivas acotadas de config-schema de canal |
  | `plugin-sdk/channel-config-writes` | Helpers de escritura de configuración de canal | Helpers de autorización de escritura de configuración de canal |
  | `plugin-sdk/channel-plugin-common` | Preludio compartido de canal | Exportaciones compartidas del preludio de plugin de canal |
  | `plugin-sdk/channel-status` | Helpers de estado de canal | Helpers compartidos de instantánea/resumen de estado de canal |
  | `plugin-sdk/allowlist-config-edit` | Helpers de configuración de lista de permitidos | Helpers de edición/lectura de configuración de lista de permitidos |
  | `plugin-sdk/group-access` | Helpers de acceso a grupos | Helpers compartidos de decisión de acceso a grupos |
  | `plugin-sdk/direct-dm` | Helpers de DM directo | Helpers compartidos de autenticación/guarda de DM directo |
  | `plugin-sdk/extension-shared` | Helpers compartidos de extensiones | Primitivas de canales/estado pasivos y helpers de proxy ambiental |
  | `plugin-sdk/webhook-targets` | Helpers de objetivos webhook | Registro de objetivos webhook y helpers de instalación de rutas |
  | `plugin-sdk/webhook-path` | Helpers de rutas webhook | Helpers de normalización de rutas webhook |
  | `plugin-sdk/web-media` | Helpers compartidos de multimedia web | Helpers de carga de multimedia remota/local |
  | `plugin-sdk/zod` | Reexportación de Zod | `zod` reexportado para consumidores del SDK de plugins |
  | `plugin-sdk/memory-core` | Helpers empaquetados de memory-core | Superficie helper de gestor/configuración/archivo/CLI de memoria |
  | `plugin-sdk/memory-core-engine-runtime` | Fachada de runtime del motor de memoria | Fachada de runtime de index/search de memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motor base de host de memoria | Exportaciones del motor base de host de memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motor de embeddings de host de memoria | Exportaciones del motor de embeddings de host de memoria |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motor QMD de host de memoria | Exportaciones del motor QMD de host de memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motor de almacenamiento de host de memoria | Exportaciones del motor de almacenamiento de host de memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Helpers multimodales de host de memoria | Helpers multimodales de host de memoria |
  | `plugin-sdk/memory-core-host-query` | Helpers de consulta de host de memoria | Helpers de consulta de host de memoria |
  | `plugin-sdk/memory-core-host-secret` | Helpers de secretos de host de memoria | Helpers de secretos de host de memoria |
  | `plugin-sdk/memory-core-host-events` | Helpers de diario de eventos de host de memoria | Helpers de diario de eventos de host de memoria |
  | `plugin-sdk/memory-core-host-status` | Helpers de estado de host de memoria | Helpers de estado de host de memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI de host de memoria | Helpers de runtime CLI de host de memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime principal de host de memoria | Helpers de runtime principal de host de memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Helpers de archivos/runtime de host de memoria | Helpers de archivos/runtime de host de memoria |
  | `plugin-sdk/memory-host-core` | Alias de runtime principal de host de memoria | Alias neutral respecto al proveedor para helpers de runtime principal de host de memoria |
  | `plugin-sdk/memory-host-events` | Alias de diario de eventos de host de memoria | Alias neutral respecto al proveedor para helpers de diario de eventos de host de memoria |
  | `plugin-sdk/memory-host-files` | Alias de archivos/runtime de host de memoria | Alias neutral respecto al proveedor para helpers de archivos/runtime de host de memoria |
  | `plugin-sdk/memory-host-markdown` | Helpers de markdown administrado | Helpers compartidos de markdown administrado para plugins adyacentes a memoria |
  | `plugin-sdk/memory-host-search` | Fachada de búsqueda activa de memoria | Fachada de runtime diferido del gestor de búsqueda de memoria activa |
  | `plugin-sdk/memory-host-status` | Alias de estado de host de memoria | Alias neutral respecto al proveedor para helpers de estado de host de memoria |
  | `plugin-sdk/memory-lancedb` | Helpers empaquetados de memory-lancedb | Superficie helper de memory-lancedb |
  | `plugin-sdk/testing` | Utilidades de prueba | Helpers y mocks de prueba |
</Accordion>

Esta tabla es intencionadamente el subconjunto común de migración, no la superficie
completa del SDK. La lista completa de más de 200 entrypoints se encuentra en
`scripts/lib/plugin-sdk-entrypoints.json`.

Esa lista todavía incluye algunas uniones helper de plugins empaquetados como
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` y `plugin-sdk/matrix*`. Siguen exportándose para
mantenimiento y compatibilidad de plugins empaquetados, pero se omiten intencionadamente de la tabla de migración común y no son el objetivo recomendado para
código nuevo de plugins.

La misma regla se aplica a otras familias de helpers empaquetados como:

- helpers de compatibilidad con navegador: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- superficies helper/plugin empaquetadas como `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` y `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` actualmente expone la superficie acotada
de helper de token `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` y `resolveCopilotApiToken`.

Usa la importación más acotada que coincida con la tarea. Si no puedes encontrar una exportación,
revisa el código fuente en `src/plugin-sdk/` o pregunta en Discord.

## Cronograma de eliminación

| Cuándo                 | Qué ocurre                                                             |
| ---------------------- | ---------------------------------------------------------------------- |
| **Ahora**              | Las superficies obsoletas emiten advertencias en tiempo de ejecución   |
| **Próxima versión mayor** | Las superficies obsoletas se eliminarán; los plugins que aún las usen fallarán |

Todos los plugins principales ya han sido migrados. Los plugins externos deberían migrarse
antes de la próxima versión mayor.

## Suprimir temporalmente las advertencias

Establece estas variables de entorno mientras trabajas en la migración:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Esta es una vía de escape temporal, no una solución permanente.

## Relacionado

- [Primeros pasos](/es/plugins/building-plugins) — crea tu primer plugin
- [Descripción general del SDK](/es/plugins/sdk-overview) — referencia completa de importación por subrutas
- [Plugins de canal](/es/plugins/sdk-channel-plugins) — creación de plugins de canal
- [Plugins de proveedor](/es/plugins/sdk-provider-plugins) — creación de plugins de proveedor
- [Internos de plugins](/es/plugins/architecture) — análisis profundo de la arquitectura
- [Manifiesto del plugin](/es/plugins/manifest) — referencia del esquema del manifiesto
