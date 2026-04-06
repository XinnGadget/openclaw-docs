---
read_when:
    - Ves la advertencia OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Ves la advertencia OPENCLAW_EXTENSION_API_DEPRECATED
    - Estás actualizando un plugin a la arquitectura moderna de plugins
    - Mantienes un plugin externo de OpenClaw
sidebarTitle: Migrate to SDK
summary: Migra de la capa heredada de compatibilidad con versiones anteriores al moderno plugin SDK
title: Migración de Plugin SDK
x-i18n:
    generated_at: "2026-04-06T05:13:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 94f12d1376edd8184714cc4dbea4a88fa8ed652f65e9365ede6176f3bf441b33
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migración de Plugin SDK

OpenClaw ha pasado de una amplia capa de compatibilidad con versiones anteriores a una arquitectura moderna de plugins
con importaciones específicas y documentadas. Si tu plugin se creó antes de
la nueva arquitectura, esta guía te ayudará a migrarlo.

## Qué está cambiando

El sistema de plugins anterior proporcionaba dos superficies muy abiertas que permitían a los plugins importar
todo lo que necesitaban desde un único punto de entrada:

- **`openclaw/plugin-sdk/compat`** — una sola importación que reexportaba decenas de
  utilidades. Se introdujo para mantener en funcionamiento los plugins antiguos basados en hooks mientras se
  construía la nueva arquitectura de plugins.
- **`openclaw/extension-api`** — un puente que daba a los plugins acceso directo a
  utilidades del lado del host, como el ejecutor de agentes embebido.

Ambas superficies ahora están **obsoletas**. Siguen funcionando en tiempo de ejecución, pero los plugins nuevos
no deben usarlas, y los plugins existentes deberían migrar antes de que la próxima
versión principal las elimine.

<Warning>
  La capa de compatibilidad con versiones anteriores se eliminará en una futura versión principal.
  Los plugins que sigan importando desde estas superficies dejarán de funcionar cuando eso ocurra.
</Warning>

## Por qué cambió esto

El enfoque anterior causaba problemas:

- **Inicio lento** — importar una utilidad cargaba docenas de módulos no relacionados
- **Dependencias circulares** — las reexportaciones amplias hacían fácil crear ciclos de importación
- **Superficie de API poco clara** — no había forma de saber qué exportaciones eran estables y cuáles eran internas

El moderno plugin SDK corrige esto: cada ruta de importación (`openclaw/plugin-sdk/\<subpath\>`)
es un módulo pequeño y autónomo con un propósito claro y un contrato documentado.

Las interfaces heredadas de conveniencia para providers de canales integrados también han desaparecido. Importaciones
como `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
interfaces de utilidades con marca de canal, y
`openclaw/plugin-sdk/telegram-core` eran atajos privados del mono-repo, no
contratos estables para plugins. Usa en su lugar subrutas genéricas y específicas del SDK. Dentro del
espacio de trabajo de plugins integrados, mantén las utilidades propias del provider en el propio
`api.ts` o `runtime-api.ts` de ese plugin.

Ejemplos actuales de providers integrados:

- Anthropic mantiene las utilidades de flujo específicas de Claude en su propia interfaz `api.ts` /
  `contract-api.ts`
- OpenAI mantiene los builders de provider, las utilidades de modelo predeterminado y los builders del provider
  realtime en su propio `api.ts`
- OpenRouter mantiene el builder del provider y las utilidades de onboarding/configuración en su propio
  `api.ts`

## Cómo migrar

<Steps>
  <Step title="Audita el comportamiento de reserva del wrapper de Windows">
    Si tu plugin usa `openclaw/plugin-sdk/windows-spawn`, los wrappers no resueltos de Windows
    `.cmd`/`.bat` ahora fallan de forma cerrada a menos que pases explícitamente
    `allowShellFallback: true`.

    ```typescript
    // Antes
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Después
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Establece esto solo para llamadores de compatibilidad confiables que
      // aceptan intencionalmente la reserva mediada por shell.
      allowShellFallback: true,
    });
    ```

    Si tu llamador no depende intencionalmente de la reserva por shell, no establezcas
    `allowShellFallback` y maneja en su lugar el error lanzado.

  </Step>

  <Step title="Encuentra las importaciones obsoletas">
    Busca en tu plugin las importaciones desde cualquiera de las dos superficies obsoletas:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Sustitúyelas por importaciones específicas">
    Cada exportación de la superficie anterior corresponde a una ruta de importación moderna específica:

    ```typescript
    // Antes (capa obsoleta de compatibilidad con versiones anteriores)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Después (importaciones modernas y específicas)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Para las utilidades del lado del host, usa el runtime del plugin inyectado en lugar de importar
    directamente:

    ```typescript
    // Antes (puente obsoleto extension-api)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Después (runtime inyectado)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    El mismo patrón se aplica a otras utilidades heredadas del puente:

    | Importación anterior | Equivalente moderno |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | utilidades del almacén de sesiones | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Compila y prueba">
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
  | `plugin-sdk/plugin-entry` | Utilidad canónica de entrada de plugin | `definePluginEntry` |
  | `plugin-sdk/core` | Reexportación general heredada para definiciones/builders de entradas de canal | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Exportación del esquema de configuración raíz | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Utilidad de entrada para un solo provider | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definiciones y builders específicos para entradas de canal | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Utilidades compartidas del asistente de configuración | Prompts de lista de permitidos, builders de estado de configuración |
  | `plugin-sdk/setup-runtime` | Utilidades de runtime para el tiempo de configuración | Adaptadores de parche de configuración seguros para importación, utilidades lookup-note, `promptResolvedAllowFrom`, `splitSetupEntries`, proxies de configuración delegada |
  | `plugin-sdk/setup-adapter-runtime` | Utilidades de adaptador de configuración | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Utilidades de herramientas de configuración | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Utilidades para múltiples cuentas | Utilidades de lista/configuración/puerta de acciones de cuenta |
  | `plugin-sdk/account-id` | Utilidades de ID de cuenta | `DEFAULT_ACCOUNT_ID`, normalización de ID de cuenta |
  | `plugin-sdk/account-resolution` | Utilidades de búsqueda de cuentas | Utilidades de búsqueda de cuentas + reserva predeterminada |
  | `plugin-sdk/account-helpers` | Utilidades específicas de cuenta | Utilidades de lista de cuentas/acción de cuenta |
  | `plugin-sdk/channel-setup` | Adaptadores del asistente de configuración | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, además de `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitivas de emparejamiento de DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Cableado de prefijo de respuesta + escritura | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Fábricas de adaptadores de configuración | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builders de esquemas de configuración | Tipos de esquema de configuración de canal |
  | `plugin-sdk/telegram-command-config` | Utilidades de configuración de comandos de Telegram | Normalización de nombres de comando, recorte de descripciones, validación de duplicados/conflictos |
  | `plugin-sdk/channel-policy` | Resolución de políticas de grupo/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Seguimiento de estado de cuenta | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Utilidades de envoltura de entrada | Utilidades compartidas de ruta + builder de envoltura |
  | `plugin-sdk/inbound-reply-dispatch` | Utilidades de respuesta entrante | Utilidades compartidas de registrar y despachar |
  | `plugin-sdk/messaging-targets` | Análisis de destinos de mensajería | Utilidades de análisis/coincidencia de destinos |
  | `plugin-sdk/outbound-media` | Utilidades de medios salientes | Carga compartida de medios salientes |
  | `plugin-sdk/outbound-runtime` | Utilidades de runtime saliente | Utilidades de identidad saliente/delegado de envío |
  | `plugin-sdk/thread-bindings-runtime` | Utilidades de vinculación de hilos | Utilidades de ciclo de vida y adaptador de vinculación de hilos |
  | `plugin-sdk/agent-media-payload` | Utilidades heredadas de payload de medios | Builder de payload de medios de agente para diseños heredados de campos |
  | `plugin-sdk/channel-runtime` | Shim de compatibilidad obsoleto | Solo utilidades heredadas de runtime de canal |
  | `plugin-sdk/channel-send-result` | Tipos de resultado de envío | Tipos de resultado de respuesta |
  | `plugin-sdk/runtime-store` | Almacenamiento persistente de plugins | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Utilidades amplias de runtime | Utilidades de runtime/logging/respaldo/instalación de plugins |
  | `plugin-sdk/runtime-env` | Utilidades específicas de entorno de runtime | Entorno logger/runtime, utilidades de timeout, retry y backoff |
  | `plugin-sdk/plugin-runtime` | Utilidades compartidas de runtime de plugins | Utilidades de comandos/hooks/http/interacción de plugins |
  | `plugin-sdk/hook-runtime` | Utilidades de pipeline de hooks | Utilidades compartidas de pipeline de webhook/hook interno |
  | `plugin-sdk/lazy-runtime` | Utilidades de runtime diferido | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Utilidades de procesos | Utilidades compartidas de ejecución |
  | `plugin-sdk/cli-runtime` | Utilidades de runtime de CLI | Formato de comandos, esperas, utilidades de versión |
  | `plugin-sdk/gateway-runtime` | Utilidades de gateway | Cliente de gateway y utilidades de parche de estado de canal |
  | `plugin-sdk/config-runtime` | Utilidades de configuración | Utilidades de carga/escritura de configuración |
  | `plugin-sdk/telegram-command-config` | Utilidades de comandos de Telegram | Utilidades de validación de comandos de Telegram con reserva estable cuando la superficie de contrato integrada de Telegram no está disponible |
  | `plugin-sdk/approval-runtime` | Utilidades de prompts de aprobación | Payload de aprobación de ejecución/plugin, utilidades de capacidad/perfil de aprobación, utilidades nativas de enrutamiento/runtime de aprobación |
  | `plugin-sdk/approval-auth-runtime` | Utilidades de autenticación de aprobación | Resolución de aprobador, autenticación de acciones en el mismo chat |
  | `plugin-sdk/approval-client-runtime` | Utilidades de cliente de aprobación | Utilidades nativas de perfil/filtro de aprobación de ejecución |
  | `plugin-sdk/approval-delivery-runtime` | Utilidades de entrega de aprobación | Adaptadores nativos de capacidad/entrega de aprobación |
  | `plugin-sdk/approval-native-runtime` | Utilidades de destino de aprobación | Utilidades nativas de vinculación de destino/cuenta de aprobación |
  | `plugin-sdk/approval-reply-runtime` | Utilidades de respuesta de aprobación | Utilidades de payload de respuesta de aprobación de ejecución/plugin |
  | `plugin-sdk/security-runtime` | Utilidades de seguridad | Utilidades compartidas de confianza, control de DM, contenido externo y recolección de secretos |
  | `plugin-sdk/ssrf-policy` | Utilidades de política SSRF | Utilidades de lista de permitidos de hosts y política de red privada |
  | `plugin-sdk/ssrf-runtime` | Utilidades de runtime SSRF | Dispatcher fijado, fetch protegido, utilidades de política SSRF |
  | `plugin-sdk/collection-runtime` | Utilidades de caché acotada | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Utilidades de control de diagnósticos | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Utilidades de formateo de errores | `formatUncaughtError`, `isApprovalNotFoundError`, utilidades de grafo de errores |
  | `plugin-sdk/fetch-runtime` | Utilidades de fetch/proxy envuelto | `resolveFetch`, utilidades de proxy |
  | `plugin-sdk/host-runtime` | Utilidades de normalización del host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Utilidades de retry | `RetryConfig`, `retryAsync`, ejecutores de políticas |
  | `plugin-sdk/allow-from` | Formato de lista de permitidos | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Mapeo de entradas de lista de permitidos | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Control de comandos y utilidades de superficie de comandos | `resolveControlCommandGate`, utilidades de autorización del remitente, utilidades de registro de comandos |
  | `plugin-sdk/secret-input` | Análisis de entrada secreta | Utilidades de entrada secreta |
  | `plugin-sdk/webhook-ingress` | Utilidades de solicitudes webhook | Utilidades de destino de webhook |
  | `plugin-sdk/webhook-request-guards` | Utilidades de guardas del cuerpo webhook | Utilidades de lectura/límite del cuerpo de la solicitud |
  | `plugin-sdk/reply-runtime` | Runtime compartido de respuesta | Despacho entrante, heartbeat, planificador de respuesta, fragmentación |
  | `plugin-sdk/reply-dispatch-runtime` | Utilidades específicas de despacho de respuesta | Utilidades de finalización + despacho de provider |
  | `plugin-sdk/reply-history` | Utilidades de historial de respuestas | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Planificación de referencias de respuesta | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Utilidades de fragmentación de respuestas | Utilidades de fragmentación de texto/markdown |
  | `plugin-sdk/session-store-runtime` | Utilidades de almacén de sesiones | Utilidades de ruta del almacén + fecha de actualización |
  | `plugin-sdk/state-paths` | Utilidades de rutas de estado | Utilidades de directorios de estado y OAuth |
  | `plugin-sdk/routing` | Utilidades de enrutamiento/clave de sesión | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, utilidades de normalización de clave de sesión |
  | `plugin-sdk/status-helpers` | Utilidades de estado de canal | Builders de resumen de estado de canal/cuenta, valores predeterminados de estado de runtime, utilidades de metadatos de incidencias |
  | `plugin-sdk/target-resolver-runtime` | Utilidades de resolución de destinos | Utilidades compartidas de resolución de destinos |
  | `plugin-sdk/string-normalization-runtime` | Utilidades de normalización de cadenas | Utilidades de normalización de slug/cadenas |
  | `plugin-sdk/request-url` | Utilidades de URL de solicitud | Extraer URL de cadena de entradas similares a solicitudes |
  | `plugin-sdk/run-command` | Utilidades de comandos temporizados | Ejecutor de comandos temporizados con stdout/stderr normalizados |
  | `plugin-sdk/param-readers` | Lectores de parámetros | Lectores comunes de parámetros de herramienta/CLI |
  | `plugin-sdk/tool-send` | Extracción de envío de herramientas | Extraer campos canónicos de destino de envío de argumentos de herramientas |
  | `plugin-sdk/temp-path` | Utilidades de rutas temporales | Utilidades compartidas de rutas temporales de descarga |
  | `plugin-sdk/logging-core` | Utilidades de logging | Logger de subsistema y utilidades de redacción |
  | `plugin-sdk/markdown-table-runtime` | Utilidades de tablas Markdown | Utilidades de modo de tabla Markdown |
  | `plugin-sdk/reply-payload` | Tipos de respuesta de mensajes | Tipos de payload de respuesta |
  | `plugin-sdk/provider-setup` | Utilidades seleccionadas de configuración de provider local/autohospedado | Utilidades de detección/configuración de provider autohospedado |
  | `plugin-sdk/self-hosted-provider-setup` | Utilidades específicas de configuración de provider autohospedado compatible con OpenAI | Las mismas utilidades de detección/configuración de provider autohospedado |
  | `plugin-sdk/provider-auth-runtime` | Utilidades de autenticación de runtime de provider | Utilidades de resolución de API key en runtime |
  | `plugin-sdk/provider-auth-api-key` | Utilidades de configuración de API key de provider | Utilidades de onboarding/escritura de perfil de API key |
  | `plugin-sdk/provider-auth-result` | Utilidades de resultado de autenticación de provider | Builder estándar de resultado de autenticación OAuth |
  | `plugin-sdk/provider-auth-login` | Utilidades de inicio de sesión interactivo de provider | Utilidades compartidas de inicio de sesión interactivo |
  | `plugin-sdk/provider-env-vars` | Utilidades de variables de entorno de provider | Utilidades de búsqueda de variables de entorno de autenticación de provider |
  | `plugin-sdk/provider-model-shared` | Utilidades compartidas de modelo/replay de provider | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builders compartidos de política de replay, utilidades de endpoint de provider y utilidades de normalización de ID de modelo |
  | `plugin-sdk/provider-catalog-shared` | Utilidades compartidas de catálogo de provider | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Parches de onboarding de provider | Utilidades de configuración de onboarding |
  | `plugin-sdk/provider-http` | Utilidades HTTP de provider | Utilidades genéricas HTTP/capacidad de endpoint de provider |
  | `plugin-sdk/provider-web-fetch` | Utilidades web-fetch de provider | Utilidades de registro/caché de provider web-fetch |
  | `plugin-sdk/provider-web-search` | Utilidades web-search de provider | Utilidades de registro/caché/configuración de provider web-search |
  | `plugin-sdk/provider-tools` | Utilidades de compatibilidad de herramientas/esquemas de provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, limpieza de esquemas Gemini + diagnósticos, y utilidades de compatibilidad de xAI como `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Utilidades de uso de provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` y otras utilidades de uso de provider |
  | `plugin-sdk/provider-stream` | Utilidades wrapper de streams de provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipos de wrapper de stream y utilidades wrapper compartidas de Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Cola asíncrona ordenada | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Utilidades compartidas de medios | Utilidades de fetch/transformación/almacenamiento de medios además de builders de payload de medios |
  | `plugin-sdk/media-generation-runtime` | Utilidades compartidas de generación de medios | Utilidades compartidas de failover, selección de candidatos y mensajes de modelo faltante para generación de imagen/video/música |
  | `plugin-sdk/media-understanding` | Utilidades de comprensión de medios | Tipos de provider de comprensión de medios además de exportaciones de utilidades de imagen/audio orientadas al provider |
  | `plugin-sdk/text-runtime` | Utilidades compartidas de texto | Eliminación de texto visible para el asistente, utilidades de renderizado/fragmentación/tablas Markdown, utilidades de redacción, utilidades de etiquetas de directivas, utilidades de texto seguro y utilidades relacionadas de texto/logging |
  | `plugin-sdk/text-chunking` | Utilidades de fragmentación de texto | Utilidad de fragmentación de texto saliente |
  | `plugin-sdk/speech` | Utilidades de voz | Tipos de provider de voz además de utilidades de directivas, registro y validación orientadas al provider |
  | `plugin-sdk/speech-core` | Núcleo compartido de voz | Tipos de provider de voz, registro, directivas, normalización |
  | `plugin-sdk/realtime-transcription` | Utilidades de transcripción en tiempo real | Tipos de provider y utilidades de registro |
  | `plugin-sdk/realtime-voice` | Utilidades de voz en tiempo real | Tipos de provider y utilidades de registro |
  | `plugin-sdk/image-generation-core` | Núcleo compartido de generación de imágenes | Tipos de generación de imágenes, failover, autenticación y utilidades de registro |
  | `plugin-sdk/music-generation` | Utilidades de generación de música | Tipos de provider/solicitud/resultado para generación de música |
  | `plugin-sdk/music-generation-core` | Núcleo compartido de generación de música | Tipos de generación de música, utilidades de failover, búsqueda de provider y análisis de model-ref |
  | `plugin-sdk/video-generation` | Utilidades de generación de video | Tipos de provider/solicitud/resultado para generación de video |
  | `plugin-sdk/video-generation-core` | Núcleo compartido de generación de video | Tipos de generación de video, utilidades de failover, búsqueda de provider y análisis de model-ref |
  | `plugin-sdk/interactive-runtime` | Utilidades de respuestas interactivas | Normalización/reducción de payload de respuesta interactiva |
  | `plugin-sdk/channel-config-primitives` | Primitivas de configuración de canal | Primitivas específicas de config-schema de canal |
  | `plugin-sdk/channel-config-writes` | Utilidades de escritura de configuración de canal | Utilidades de autorización para escritura de configuración de canal |
  | `plugin-sdk/channel-plugin-common` | Preludio compartido de canal | Exportaciones compartidas de preludio de plugin de canal |
  | `plugin-sdk/channel-status` | Utilidades de estado de canal | Utilidades compartidas de instantánea/resumen de estado de canal |
  | `plugin-sdk/allowlist-config-edit` | Utilidades de configuración de lista de permitidos | Utilidades de edición/lectura de configuración de lista de permitidos |
  | `plugin-sdk/group-access` | Utilidades de acceso a grupos | Utilidades compartidas de decisión de acceso a grupos |
  | `plugin-sdk/direct-dm` | Utilidades de DM directo | Utilidades compartidas de autenticación/protección de DM directo |
  | `plugin-sdk/extension-shared` | Utilidades compartidas de extensiones | Primitivas auxiliares de canal/estado pasivo |
  | `plugin-sdk/webhook-targets` | Utilidades de destinos webhook | Registro de destinos webhook y utilidades de instalación de rutas |
  | `plugin-sdk/webhook-path` | Utilidades de rutas webhook | Utilidades de normalización de rutas webhook |
  | `plugin-sdk/web-media` | Utilidades compartidas de medios web | Utilidades de carga de medios remotos/locales |
  | `plugin-sdk/zod` | Reexportación de Zod | `zod` reexportado para consumidores de plugin SDK |
  | `plugin-sdk/memory-core` | Utilidades integradas de memory-core | Superficie de utilidades de administrador/configuración/archivo/CLI de memoria |
  | `plugin-sdk/memory-core-engine-runtime` | Fachada de runtime del motor de memoria | Fachada de runtime de índice/búsqueda de memoria |
  | `plugin-sdk/memory-core-host-engine-foundation` | Motor base del host de memoria | Exportaciones del motor base del host de memoria |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Motor de embeddings del host de memoria | Exportaciones del motor de embeddings del host de memoria |
  | `plugin-sdk/memory-core-host-engine-qmd` | Motor QMD del host de memoria | Exportaciones del motor QMD del host de memoria |
  | `plugin-sdk/memory-core-host-engine-storage` | Motor de almacenamiento del host de memoria | Exportaciones del motor de almacenamiento del host de memoria |
  | `plugin-sdk/memory-core-host-multimodal` | Utilidades multimodales del host de memoria | Utilidades multimodales del host de memoria |
  | `plugin-sdk/memory-core-host-query` | Utilidades de consulta del host de memoria | Utilidades de consulta del host de memoria |
  | `plugin-sdk/memory-core-host-secret` | Utilidades de secretos del host de memoria | Utilidades de secretos del host de memoria |
  | `plugin-sdk/memory-core-host-events` | Utilidades de diario de eventos del host de memoria | Utilidades de diario de eventos del host de memoria |
  | `plugin-sdk/memory-core-host-status` | Utilidades de estado del host de memoria | Utilidades de estado del host de memoria |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI del host de memoria | Utilidades de runtime CLI del host de memoria |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime principal del host de memoria | Utilidades de runtime principal del host de memoria |
  | `plugin-sdk/memory-core-host-runtime-files` | Utilidades de archivos/runtime del host de memoria | Utilidades de archivos/runtime del host de memoria |
  | `plugin-sdk/memory-host-core` | Alias de runtime principal del host de memoria | Alias neutral respecto al proveedor para utilidades de runtime principal del host de memoria |
  | `plugin-sdk/memory-host-events` | Alias de diario de eventos del host de memoria | Alias neutral respecto al proveedor para utilidades de diario de eventos del host de memoria |
  | `plugin-sdk/memory-host-files` | Alias de archivos/runtime del host de memoria | Alias neutral respecto al proveedor para utilidades de archivos/runtime del host de memoria |
  | `plugin-sdk/memory-host-markdown` | Utilidades de markdown administrado | Utilidades compartidas de markdown administrado para plugins adyacentes a memoria |
  | `plugin-sdk/memory-host-search` | Fachada de búsqueda de memoria activa | Fachada de runtime diferido del administrador de búsqueda de memoria activa |
  | `plugin-sdk/memory-host-status` | Alias de estado del host de memoria | Alias neutral respecto al proveedor para utilidades de estado del host de memoria |
  | `plugin-sdk/memory-lancedb` | Utilidades integradas de memory-lancedb | Superficie de utilidades de memory-lancedb |
  | `plugin-sdk/testing` | Utilidades de prueba | Utilidades y mocks de prueba |
</Accordion>

Esta tabla es intencionalmente el subconjunto común de migración, no la superficie completa del SDK.
La lista completa de más de 200 puntos de entrada se encuentra en
`scripts/lib/plugin-sdk-entrypoints.json`.

Esa lista todavía incluye algunas interfaces de utilidades de plugins integrados como
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` y `plugin-sdk/matrix*`. Estas siguen exportándose para
mantenimiento y compatibilidad de plugins integrados, pero se omiten intencionalmente
de la tabla común de migración y no son el destino recomendado para
código nuevo de plugins.

La misma regla se aplica a otras familias de utilidades integradas como:

- utilidades de compatibilidad con browser: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- superficies de utilidades/plugins integrados como `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` y `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` actualmente expone la superficie específica de utilidades de token
`DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` y `resolveCopilotApiToken`.

Usa la importación más específica que coincida con la tarea. Si no encuentras una exportación,
revisa la fuente en `src/plugin-sdk/` o pregunta en Discord.

## Cronograma de eliminación

| Cuándo                 | Qué sucede                                                             |
| ---------------------- | ---------------------------------------------------------------------- |
| **Ahora**              | Las superficies obsoletas emiten advertencias en tiempo de ejecución   |
| **Próxima versión principal** | Las superficies obsoletas se eliminarán; los plugins que aún las usen fallarán |

Todos los plugins principales ya se migraron. Los plugins externos deberían migrar
antes de la próxima versión principal.

## Suprimir temporalmente las advertencias

Establece estas variables de entorno mientras trabajas en la migración:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Esta es una vía de escape temporal, no una solución permanente.

## Relacionado

- [Primeros pasos](/es/plugins/building-plugins) — crea tu primer plugin
- [Descripción general del SDK](/es/plugins/sdk-overview) — referencia completa de importaciones por subruta
- [Plugins de canal](/es/plugins/sdk-channel-plugins) — creación de plugins de canal
- [Plugins de provider](/es/plugins/sdk-provider-plugins) — creación de plugins de provider
- [Aspectos internos de plugins](/es/plugins/architecture) — análisis profundo de la arquitectura
- [Manifiesto de plugin](/es/plugins/manifest) — referencia del esquema del manifiesto
