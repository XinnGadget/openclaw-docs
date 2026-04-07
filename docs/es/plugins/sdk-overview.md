---
read_when:
    - Necesitas saber desde qué subruta del SDK importar
    - Quieres una referencia de todos los métodos de registro en OpenClawPluginApi
    - Estás buscando una exportación específica del SDK
sidebarTitle: SDK Overview
summary: Mapa de importaciones, referencia de la API de registro y arquitectura del SDK
title: Resumen del Plugin SDK
x-i18n:
    generated_at: "2026-04-07T05:05:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe1fe41beaf73a7bdf807e281d181df7a5da5819343823c4011651fb234b0905
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Resumen del Plugin SDK

El SDK de plugins es el contrato tipado entre los plugins y el núcleo. Esta página es la
referencia de **qué importar** y **qué puedes registrar**.

<Tip>
  **¿Buscas una guía práctica?**
  - ¿Primer plugin? Empieza con [Primeros pasos](/es/plugins/building-plugins)
  - ¿Plugin de canal? Consulta [Plugins de canal](/es/plugins/sdk-channel-plugins)
  - ¿Plugin de proveedor? Consulta [Plugins de proveedor](/es/plugins/sdk-provider-plugins)
</Tip>

## Convención de importación

Importa siempre desde una subruta específica:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Cada subruta es un módulo pequeño y autocontenido. Esto mantiene un inicio rápido y
evita problemas de dependencias circulares. Para helpers de entrada/compilación específicos de canal,
prefiere `openclaw/plugin-sdk/channel-core`; reserva `openclaw/plugin-sdk/core` para
la superficie paraguas más amplia y helpers compartidos como
`buildChannelConfigSchema`.

No agregues ni dependas de interfaces de conveniencia con nombre de proveedor como
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` ni
interfaces helper con marca de canal. Los plugins incluidos deben componer subrutas genéricas del
SDK dentro de sus propios barrels `api.ts` o `runtime-api.ts`, y el núcleo
debe usar esos barrels locales del plugin o agregar un contrato estrecho y genérico del SDK
cuando la necesidad sea realmente entre canales.

El mapa de exportaciones generado todavía contiene un pequeño conjunto de interfaces helper
de plugins incluidos, como `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` y `plugin-sdk/matrix*`. Esas
subrutas existen solo para mantenimiento y compatibilidad de plugins incluidos; se
omiten intencionalmente de la tabla común a continuación y no son la ruta de importación
recomendada para nuevos plugins de terceros.

## Referencia de subrutas

Las subrutas de uso más frecuente, agrupadas por propósito. La lista completa generada de
más de 200 subrutas se encuentra en `scripts/lib/plugin-sdk-entrypoints.json`.

Las subrutas reservadas de helpers para plugins incluidos siguen apareciendo en esa lista generada.
Trátalas como superficies de detalle de implementación/compatibilidad, salvo que una página de documentación
promueva explícitamente una como pública.

### Entrada de plugin

| Subruta                    | Exportaciones clave                                                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                   |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                      |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="Subrutas de canal">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Exportación del esquema Zod raíz de `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, además de `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helpers compartidos del asistente de configuración, solicitudes de lista de permitidos, constructores de estado de configuración |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helpers de compuertas de acción/configuración multicuenta, helpers de respaldo de cuenta predeterminada |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helpers de normalización de ID de cuenta |
    | `plugin-sdk/account-resolution` | Búsqueda de cuentas + helpers de respaldo predeterminado |
    | `plugin-sdk/account-helpers` | Helpers limitados para lista de cuentas/acciones de cuenta |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipos de esquema de configuración de canal |
    | `plugin-sdk/telegram-command-config` | Helpers de normalización/validación de comandos personalizados de Telegram con respaldo de contrato incluido |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helpers compartidos para enrutamiento entrante y construcción de sobres |
    | `plugin-sdk/inbound-reply-dispatch` | Helpers compartidos para registrar y despachar entradas |
    | `plugin-sdk/messaging-targets` | Helpers de análisis/coincidencia de destinos |
    | `plugin-sdk/outbound-media` | Helpers compartidos para cargar medios salientes |
    | `plugin-sdk/outbound-runtime` | Helpers de identidad saliente/delegados de envío |
    | `plugin-sdk/thread-bindings-runtime` | Helpers de ciclo de vida y adaptadores para asociaciones de hilos |
    | `plugin-sdk/agent-media-payload` | Constructor heredado de payload de medios de agente |
    | `plugin-sdk/conversation-runtime` | Helpers de asociación de conversación/hilo, emparejamiento y configuración de asociaciones |
    | `plugin-sdk/runtime-config-snapshot` | Helper de instantánea de configuración en tiempo de ejecución |
    | `plugin-sdk/runtime-group-policy` | Helpers de resolución de política de grupo en tiempo de ejecución |
    | `plugin-sdk/channel-status` | Helpers compartidos de instantánea/resumen del estado del canal |
    | `plugin-sdk/channel-config-primitives` | Primitivas limitadas de esquema de configuración de canal |
    | `plugin-sdk/channel-config-writes` | Helpers de autorización para escritura de configuración de canal |
    | `plugin-sdk/channel-plugin-common` | Exportaciones compartidas de preludio para plugins de canal |
    | `plugin-sdk/allowlist-config-edit` | Helpers de lectura/edición de configuración de lista de permitidos |
    | `plugin-sdk/group-access` | Helpers compartidos de decisión de acceso a grupos |
    | `plugin-sdk/direct-dm` | Helpers compartidos de autenticación/guardas para mensajes directos |
    | `plugin-sdk/interactive-runtime` | Helpers de normalización/reducción de payloads de respuesta interactiva |
    | `plugin-sdk/channel-inbound` | Helpers de debounce, coincidencia de menciones y sobres |
    | `plugin-sdk/channel-send-result` | Tipos de resultados de respuesta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helpers de análisis/coincidencia de destinos |
    | `plugin-sdk/channel-contract` | Tipos de contrato de canal |
    | `plugin-sdk/channel-feedback` | Integración de comentarios/reacciones |
    | `plugin-sdk/channel-secret-runtime` | Helpers limitados de contrato de secretos, como `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` y tipos de destino de secretos |
  </Accordion>

  <Accordion title="Subrutas de proveedor">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helpers seleccionados de configuración para proveedores locales/autohospedados |
    | `plugin-sdk/self-hosted-provider-setup` | Helpers específicos de configuración para proveedores autohospedados compatibles con OpenAI |
    | `plugin-sdk/cli-backend` | Valores predeterminados de backend de CLI + constantes de watchdog |
    | `plugin-sdk/provider-auth-runtime` | Helpers de tiempo de ejecución para resolución de claves de API en plugins de proveedor |
    | `plugin-sdk/provider-auth-api-key` | Helpers para incorporación/escritura de perfiles de clave de API, como `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Constructor estándar de resultados de autenticación OAuth |
    | `plugin-sdk/provider-auth-login` | Helpers interactivos compartidos de inicio de sesión para plugins de proveedor |
    | `plugin-sdk/provider-env-vars` | Helpers de búsqueda de variables de entorno de autenticación del proveedor |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, constructores compartidos de políticas de reintento, helpers de endpoints de proveedor y helpers de normalización de ID de modelo como `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helpers genéricos para capacidades HTTP/endpoints de proveedor |
    | `plugin-sdk/provider-web-fetch` | Helpers de registro/caché para proveedores de obtención web |
    | `plugin-sdk/provider-web-search-contract` | Helpers limitados de contrato de configuración/credenciales de búsqueda web como `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` y getters/setters con alcance definido para credenciales |
    | `plugin-sdk/provider-web-search` | Helpers de registro/caché/tiempo de ejecución para proveedores de búsqueda web |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, limpieza + diagnósticos de esquemas Gemini y helpers de compatibilidad de xAI como `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` y similares |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipos de wrappers de flujo y helpers compartidos de wrappers Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helpers de parcheo de configuración durante la incorporación |
    | `plugin-sdk/global-singleton` | Helpers de singleton/mapa/caché locales al proceso |
  </Accordion>

  <Accordion title="Subrutas de autenticación y seguridad">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helpers de registro de comandos, helpers de autorización del remitente |
    | `plugin-sdk/approval-auth-runtime` | Resolución de aprobadores y helpers de autenticación de acciones en el mismo chat |
    | `plugin-sdk/approval-client-runtime` | Helpers nativos de perfil/filtro de aprobación de ejecución |
    | `plugin-sdk/approval-delivery-runtime` | Adaptadores nativos de capacidad/entrega de aprobaciones |
    | `plugin-sdk/approval-native-runtime` | Helpers nativos de destino de aprobación y asociación de cuentas |
    | `plugin-sdk/approval-reply-runtime` | Helpers de payload de respuesta para aprobaciones de ejecución/plugin |
    | `plugin-sdk/command-auth-native` | Helpers nativos de autenticación de comandos + destinos de sesión nativos |
    | `plugin-sdk/command-detection` | Helpers compartidos de detección de comandos |
    | `plugin-sdk/command-surface` | Helpers de normalización del cuerpo del comando y de superficie de comando |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Helpers limitados de recopilación de contratos de secretos para superficies secretas de canal/plugin |
    | `plugin-sdk/security-runtime` | Helpers compartidos de confianza, compuertas de MD, contenido externo y recopilación de secretos |
    | `plugin-sdk/ssrf-policy` | Helpers de lista de permitidos de host y política SSRF de red privada |
    | `plugin-sdk/ssrf-runtime` | Helpers de dispatcher fijado, fetch protegido por SSRF y política SSRF |
    | `plugin-sdk/secret-input` | Helpers de análisis de entradas secretas |
    | `plugin-sdk/webhook-ingress` | Helpers de solicitud/destino de webhook |
    | `plugin-sdk/webhook-request-guards` | Helpers de tamaño de cuerpo/tiempo de espera de solicitud |
  </Accordion>

  <Accordion title="Subrutas de tiempo de ejecución y almacenamiento">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/runtime` | Helpers amplios de tiempo de ejecución/logging/copias de seguridad/instalación de plugins |
    | `plugin-sdk/runtime-env` | Helpers limitados de entorno de tiempo de ejecución, logger, timeout, reintento y backoff |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helpers compartidos para comandos/hooks/http/interacciones de plugins |
    | `plugin-sdk/hook-runtime` | Helpers compartidos de canalización de hooks webhook/internos |
    | `plugin-sdk/lazy-runtime` | Helpers de importación/asociación perezosa de tiempo de ejecución como `createLazyRuntimeModule`, `createLazyRuntimeMethod` y `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helpers de ejecución de procesos |
    | `plugin-sdk/cli-runtime` | Helpers de formato, espera y versión para CLI |
    | `plugin-sdk/gateway-runtime` | Cliente de gateway y helpers de parcheo de estado de canales |
    | `plugin-sdk/config-runtime` | Helpers de carga/escritura de configuración |
    | `plugin-sdk/telegram-command-config` | Helpers de normalización de nombre/descripción de comandos de Telegram y comprobaciones de duplicados/conflictos, incluso cuando la superficie de contrato de Telegram incluida no está disponible |
    | `plugin-sdk/approval-runtime` | Helpers de aprobación de ejecución/plugin, constructores de capacidad de aprobación, helpers de autenticación/perfil, helpers nativos de enrutamiento/tiempo de ejecución |
    | `plugin-sdk/reply-runtime` | Helpers compartidos de tiempo de ejecución para entradas/respuestas, fragmentación, despacho, heartbeat, planificador de respuestas |
    | `plugin-sdk/reply-dispatch-runtime` | Helpers limitados para despachar/finalizar respuestas |
    | `plugin-sdk/reply-history` | Helpers compartidos de historial de respuestas de ventana corta, como `buildHistoryContext`, `recordPendingHistoryEntry` y `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helpers limitados para fragmentación de texto/markdown |
    | `plugin-sdk/session-store-runtime` | Helpers de ruta y `updated-at` del almacén de sesiones |
    | `plugin-sdk/state-paths` | Helpers de rutas de directorio de estado/OAuth |
    | `plugin-sdk/routing` | Helpers de enrutamiento/clave de sesión/asociación de cuentas como `resolveAgentRoute`, `buildAgentSessionKey` y `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helpers compartidos de resumen de estado de canal/cuenta, valores predeterminados del estado de tiempo de ejecución y helpers de metadatos de incidencias |
    | `plugin-sdk/target-resolver-runtime` | Helpers compartidos de resolución de destinos |
    | `plugin-sdk/string-normalization-runtime` | Helpers de normalización de slug/cadenas |
    | `plugin-sdk/request-url` | Extrae URLs de cadena de entradas tipo fetch/request |
    | `plugin-sdk/run-command` | Ejecutor de comandos temporizado con resultados normalizados de stdout/stderr |
    | `plugin-sdk/param-readers` | Lectores comunes de parámetros para herramientas/CLI |
    | `plugin-sdk/tool-send` | Extrae campos canónicos de destino de envío de argumentos de herramientas |
    | `plugin-sdk/temp-path` | Helpers compartidos para rutas temporales de descarga |
    | `plugin-sdk/logging-core` | Logger de subsistema y helpers de redacción |
    | `plugin-sdk/markdown-table-runtime` | Helpers de modo de tablas Markdown |
    | `plugin-sdk/json-store` | Pequeños helpers de lectura/escritura de estado JSON |
    | `plugin-sdk/file-lock` | Helpers de bloqueo de archivos reentrante |
    | `plugin-sdk/persistent-dedupe` | Helpers de caché de deduplicación respaldada en disco |
    | `plugin-sdk/acp-runtime` | Helpers de ACP para tiempo de ejecución/sesión y despacho de respuestas |
    | `plugin-sdk/agent-config-primitives` | Primitivas limitadas de esquema de configuración de agente en tiempo de ejecución |
    | `plugin-sdk/boolean-param` | Lector flexible de parámetros booleanos |
    | `plugin-sdk/dangerous-name-runtime` | Helpers de resolución de coincidencias de nombres peligrosos |
    | `plugin-sdk/device-bootstrap` | Helpers de bootstrap del dispositivo y tokens de emparejamiento |
    | `plugin-sdk/extension-shared` | Primitivas helper compartidas para canales pasivos, estado y proxy ambiental |
    | `plugin-sdk/models-provider-runtime` | Helpers de respuesta de proveedor/comando `/models` |
    | `plugin-sdk/skill-commands-runtime` | Helpers de listado de comandos de Skills |
    | `plugin-sdk/native-command-registry` | Helpers nativos de registro/construcción/serialización de comandos |
    | `plugin-sdk/provider-zai-endpoint` | Helpers de detección de endpoints Z.A.I |
    | `plugin-sdk/infra-runtime` | Helpers de eventos del sistema/heartbeat |
    | `plugin-sdk/collection-runtime` | Pequeños helpers de caché acotada |
    | `plugin-sdk/diagnostic-runtime` | Helpers de indicadores y eventos de diagnóstico |
    | `plugin-sdk/error-runtime` | Grafo de errores, formato, helpers compartidos de clasificación de errores, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Fetch envuelto, proxy y helpers de búsqueda fijada |
    | `plugin-sdk/host-runtime` | Helpers de normalización de nombre de host y host SCP |
    | `plugin-sdk/retry-runtime` | Helpers de configuración y ejecución de reintentos |
    | `plugin-sdk/agent-runtime` | Helpers de directorio/identidad/espacio de trabajo del agente |
    | `plugin-sdk/directory-runtime` | Consulta/deduplicación de directorios respaldada por configuración |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Subrutas de capacidades y pruebas">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helpers compartidos para obtención/transformación/almacenamiento de medios, además de constructores de payload de medios |
    | `plugin-sdk/media-generation-runtime` | Helpers compartidos para respaldo de generación de medios, selección de candidatos y mensajes de modelo faltante |
    | `plugin-sdk/media-understanding` | Tipos de proveedor de comprensión de medios además de exportaciones helper para imágenes/audio orientadas al proveedor |
    | `plugin-sdk/text-runtime` | Helpers compartidos de texto/markdown/logging, como eliminación de texto visible para el asistente, helpers de renderizado/fragmentación/tablas Markdown, helpers de redacción, helpers de etiquetas de directivas y utilidades de texto seguro |
    | `plugin-sdk/text-chunking` | Helper de fragmentación de texto saliente |
    | `plugin-sdk/speech` | Tipos de proveedor de voz además de helpers orientados al proveedor para directivas, registro y validación |
    | `plugin-sdk/speech-core` | Tipos compartidos de proveedor de voz, registro, directivas y helpers de normalización |
    | `plugin-sdk/realtime-transcription` | Tipos de proveedor de transcripción en tiempo real y helpers de registro |
    | `plugin-sdk/realtime-voice` | Tipos de proveedor de voz en tiempo real y helpers de registro |
    | `plugin-sdk/image-generation` | Tipos de proveedor de generación de imágenes |
    | `plugin-sdk/image-generation-core` | Tipos compartidos de generación de imágenes, respaldo, autenticación y helpers de registro |
    | `plugin-sdk/music-generation` | Tipos de proveedor/solicitud/resultado de generación de música |
    | `plugin-sdk/music-generation-core` | Tipos compartidos de generación de música, helpers de respaldo, búsqueda de proveedores y análisis de referencias de modelos |
    | `plugin-sdk/video-generation` | Tipos de proveedor/solicitud/resultado de generación de video |
    | `plugin-sdk/video-generation-core` | Tipos compartidos de generación de video, helpers de respaldo, búsqueda de proveedores y análisis de referencias de modelos |
    | `plugin-sdk/webhook-targets` | Registro de destinos webhook y helpers de instalación de rutas |
    | `plugin-sdk/webhook-path` | Helpers de normalización de rutas webhook |
    | `plugin-sdk/web-media` | Helpers compartidos para cargar medios remotos/locales |
    | `plugin-sdk/zod` | `zod` reexportado para consumidores del Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Subrutas de memoria">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie helper incluida de memory-core para helpers de administrador/configuración/archivo/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Fachada de tiempo de ejecución para índice/búsqueda de memoria |
    | `plugin-sdk/memory-core-host-engine-foundation` | Exportaciones del motor base del host de memoria |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Exportaciones del motor de embeddings del host de memoria |
    | `plugin-sdk/memory-core-host-engine-qmd` | Exportaciones del motor QMD del host de memoria |
    | `plugin-sdk/memory-core-host-engine-storage` | Exportaciones del motor de almacenamiento del host de memoria |
    | `plugin-sdk/memory-core-host-multimodal` | Helpers multimodales del host de memoria |
    | `plugin-sdk/memory-core-host-query` | Helpers de consulta del host de memoria |
    | `plugin-sdk/memory-core-host-secret` | Helpers de secretos del host de memoria |
    | `plugin-sdk/memory-core-host-events` | Helpers del diario de eventos del host de memoria |
    | `plugin-sdk/memory-core-host-status` | Helpers de estado del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helpers de tiempo de ejecución de CLI del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-core` | Helpers centrales de tiempo de ejecución del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-files` | Helpers de archivos/tiempo de ejecución del host de memoria |
    | `plugin-sdk/memory-host-core` | Alias neutral respecto al proveedor para helpers centrales de tiempo de ejecución del host de memoria |
    | `plugin-sdk/memory-host-events` | Alias neutral respecto al proveedor para helpers del diario de eventos del host de memoria |
    | `plugin-sdk/memory-host-files` | Alias neutral respecto al proveedor para helpers de archivos/tiempo de ejecución del host de memoria |
    | `plugin-sdk/memory-host-markdown` | Helpers compartidos de markdown administrado para plugins adyacentes a memoria |
    | `plugin-sdk/memory-host-search` | Fachada activa de tiempo de ejecución de memoria para acceso al administrador de búsqueda |
    | `plugin-sdk/memory-host-status` | Alias neutral respecto al proveedor para helpers de estado del host de memoria |
    | `plugin-sdk/memory-lancedb` | Superficie helper incluida de memory-lancedb |
  </Accordion>

  <Accordion title="Subrutas reservadas de helpers incluidos">
    | Familia | Subrutas actuales | Uso previsto |
    | --- | --- | --- |
    | Navegador | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helpers de soporte para el plugin incluido de navegador (`browser-support` sigue siendo el barrel de compatibilidad) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie helper/de tiempo de ejecución incluida de Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie helper/de tiempo de ejecución incluida de LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie helper incluida de IRC |
    | Helpers específicos de canal | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Interfaces helper/de compatibilidad de canales incluidos |
    | Helpers específicos de autenticación/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Interfaces helper de funciones/plugins incluidos; `plugin-sdk/github-copilot-token` actualmente exporta `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` y `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API de registro

La devolución de llamada `register(api)` recibe un objeto `OpenClawPluginApi` con estos
métodos:

### Registro de capacidades

| Método                                           | Qué registra                     |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Inferencia de texto (LLM)        |
| `api.registerCliBackend(...)`                    | Backend local de inferencia CLI  |
| `api.registerChannel(...)`                       | Canal de mensajería              |
| `api.registerSpeechProvider(...)`                | Síntesis de texto a voz / STT    |
| `api.registerRealtimeTranscriptionProvider(...)` | Transcripción en tiempo real por streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sesiones de voz en tiempo real dúplex |
| `api.registerMediaUnderstandingProvider(...)`    | Análisis de imagen/audio/video   |
| `api.registerImageGenerationProvider(...)`       | Generación de imágenes           |
| `api.registerMusicGenerationProvider(...)`       | Generación de música             |
| `api.registerVideoGenerationProvider(...)`       | Generación de video              |
| `api.registerWebFetchProvider(...)`              | Proveedor de obtención / scraping web |
| `api.registerWebSearchProvider(...)`             | Búsqueda web                     |

### Herramientas y comandos

| Método                          | Qué registra                                  |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Herramienta de agente (obligatoria o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizado (omite el LLM)          |

### Infraestructura

| Método                                         | Qué registra                          |
| ---------------------------------------------- | ------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook de evento                        |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del gateway             |
| `api.registerGatewayMethod(name, handler)`     | Método RPC del gateway                |
| `api.registerCli(registrar, opts?)`            | Subcomando de CLI                     |
| `api.registerService(service)`                 | Servicio en segundo plano             |
| `api.registerInteractiveHandler(registration)` | Controlador interactivo               |
| `api.registerMemoryPromptSupplement(builder)`  | Sección adicional del prompt adyacente a memoria |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus adicional de búsqueda/lectura en memoria |

Los espacios de nombres administrativos reservados del núcleo (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) siempre permanecen en `operator.admin`, incluso si un plugin intenta asignar
un alcance más limitado a un método del gateway. Prefiere prefijos específicos del plugin para
métodos que pertenecen al plugin.

### Metadatos de registro de CLI

`api.registerCli(registrar, opts?)` acepta dos tipos de metadatos de nivel superior:

- `commands`: raíces de comandos explícitas que pertenecen al registrador
- `descriptors`: descriptores de comandos en tiempo de análisis usados para ayuda del CLI raíz,
  enrutamiento y registro diferido de CLI de plugins

Si quieres que un comando de plugin permanezca cargado de forma diferida en la ruta normal del CLI raíz,
proporciona `descriptors` que cubran cada raíz de comando de nivel superior expuesta por ese
registrador.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Manage Matrix accounts, verification, devices, and profile state",
        hasSubcommands: true,
      },
    ],
  },
);
```

Usa `commands` por sí solo únicamente cuando no necesites registro diferido del CLI raíz.
Esa ruta de compatibilidad ansiosa sigue siendo compatible, pero no instala
marcadores respaldados por descriptores para carga diferida en tiempo de análisis.

### Registro de backend de CLI

`api.registerCliBackend(...)` permite que un plugin posea la configuración predeterminada de un
backend local de CLI de IA, como `codex-cli`.

- El `id` del backend se convierte en el prefijo del proveedor en referencias de modelo como `codex-cli/gpt-5`.
- La `config` del backend usa la misma forma que `agents.defaults.cliBackends.<id>`.
- La configuración del usuario sigue teniendo prioridad. OpenClaw fusiona `agents.defaults.cliBackends.<id>` sobre el
  valor predeterminado del plugin antes de ejecutar la CLI.
- Usa `normalizeConfig` cuando un backend necesite reescrituras de compatibilidad después de la fusión
  (por ejemplo, normalizar formas antiguas de flags).

### Ranuras exclusivas

| Método                                     | Qué registra                          |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Motor de contexto (uno activo a la vez) |
| `api.registerMemoryPromptSection(builder)` | Constructor de sección de prompt de memoria |
| `api.registerMemoryFlushPlan(resolver)`    | Resolutor de plan de vaciado de memoria |
| `api.registerMemoryRuntime(runtime)`       | Adaptador de tiempo de ejecución de memoria |

### Adaptadores de embeddings de memoria

| Método                                         | Qué registra                                   |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adaptador de embeddings de memoria para el plugin activo |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` y
  `registerMemoryRuntime` son exclusivos de plugins de memoria.
- `registerMemoryEmbeddingProvider` permite al plugin de memoria activo registrar uno
  o más id de adaptadores de embeddings (por ejemplo `openai`, `gemini` o un id personalizado definido por el plugin).
- La configuración del usuario, como `agents.defaults.memorySearch.provider` y
  `agents.defaults.memorySearch.fallback`, se resuelve contra esos id de adaptadores
  registrados.

### Eventos y ciclo de vida

| Método                                       | Qué hace                     |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook de ciclo de vida tipado |
| `api.onConversationBindingResolved(handler)` | Callback de asociación de conversación |

### Semántica de decisiones de hooks

- `before_tool_call`: devolver `{ block: true }` es terminal. Una vez que cualquier controlador lo establece, se omiten los controladores de menor prioridad.
- `before_tool_call`: devolver `{ block: false }` se trata como sin decisión (igual que omitir `block`), no como una anulación.
- `before_install`: devolver `{ block: true }` es terminal. Una vez que cualquier controlador lo establece, se omiten los controladores de menor prioridad.
- `before_install`: devolver `{ block: false }` se trata como sin decisión (igual que omitir `block`), no como una anulación.
- `reply_dispatch`: devolver `{ handled: true, ... }` es terminal. Una vez que cualquier controlador reclama el despacho, se omiten los controladores de menor prioridad y la ruta predeterminada de despacho del modelo.
- `message_sending`: devolver `{ cancel: true }` es terminal. Una vez que cualquier controlador lo establece, se omiten los controladores de menor prioridad.
- `message_sending`: devolver `{ cancel: false }` se trata como sin decisión (igual que omitir `cancel`), no como una anulación.

### Campos del objeto API

| Campo                    | Tipo                      | Descripción                                                                                |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | ID del plugin                                                                              |
| `api.name`               | `string`                  | Nombre para mostrar                                                                        |
| `api.version`            | `string?`                 | Versión del plugin (opcional)                                                              |
| `api.description`        | `string?`                 | Descripción del plugin (opcional)                                                          |
| `api.source`             | `string`                  | Ruta de origen del plugin                                                                  |
| `api.rootDir`            | `string?`                 | Directorio raíz del plugin (opcional)                                                      |
| `api.config`             | `OpenClawConfig`          | Instantánea actual de configuración (instantánea activa en memoria del tiempo de ejecución cuando está disponible) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configuración específica del plugin desde `plugins.entries.<id>.config`                    |
| `api.runtime`            | `PluginRuntime`           | [Helpers de tiempo de ejecución](/es/plugins/sdk-runtime)                                     |
| `api.logger`             | `PluginLogger`            | Logger con alcance (`debug`, `info`, `warn`, `error`)                                      |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modo de carga actual; `"setup-runtime"` es la ventana ligera de inicio/configuración previa a la entrada completa |
| `api.resolvePath(input)` | `(string) => string`      | Resuelve una ruta relativa a la raíz del plugin                                            |

## Convención de módulos internos

Dentro de tu plugin, usa archivos barrel locales para las importaciones internas:

```
my-plugin/
  api.ts            # Exportaciones públicas para consumidores externos
  runtime-api.ts    # Exportaciones internas solo para tiempo de ejecución
  index.ts          # Punto de entrada del plugin
  setup-entry.ts    # Entrada ligera solo para configuración (opcional)
```

<Warning>
  Nunca importes tu propio plugin mediante `openclaw/plugin-sdk/<your-plugin>`
  desde código de producción. Enruta las importaciones internas mediante `./api.ts` o
  `./runtime-api.ts`. La ruta del SDK es solo el contrato externo.
</Warning>

Las superficies públicas de plugins incluidos cargadas mediante fachada (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` y archivos de entrada públicos similares) ahora prefieren la
instantánea activa de configuración en tiempo de ejecución cuando OpenClaw ya está en funcionamiento. Si todavía
no existe una instantánea de tiempo de ejecución, recurren al archivo de configuración resuelto en disco.

Los plugins de proveedor también pueden exponer un barrel de contrato local del plugin cuando un
helper es intencionalmente específico del proveedor y todavía no pertenece a una subruta genérica del SDK.
Ejemplo incluido actual: el proveedor Anthropic mantiene sus helpers de flujo de Claude
en su propia interfaz pública `api.ts` / `contract-api.ts` en lugar de
promover la lógica de encabezados beta de Anthropic y `service_tier` a un contrato genérico
`plugin-sdk/*`.

Otros ejemplos incluidos actuales:

- `@openclaw/openai-provider`: `api.ts` exporta constructores de proveedores,
  helpers de modelos predeterminados y constructores de proveedores en tiempo real
- `@openclaw/openrouter-provider`: `api.ts` exporta el constructor del proveedor más
  helpers de incorporación/configuración

<Warning>
  El código de producción de extensiones también debe evitar importaciones de `openclaw/plugin-sdk/<other-plugin>`.
  Si un helper es realmente compartido, promuévelo a una subruta neutral del SDK
  como `openclaw/plugin-sdk/speech`, `.../provider-model-shared` u otra
  superficie orientada a capacidades, en lugar de acoplar dos plugins entre sí.
</Warning>

## Relacionado

- [Puntos de entrada](/es/plugins/sdk-entrypoints) — opciones de `definePluginEntry` y `defineChannelPluginEntry`
- [Helpers de tiempo de ejecución](/es/plugins/sdk-runtime) — referencia completa del espacio de nombres `api.runtime`
- [Configuración y setup](/es/plugins/sdk-setup) — empaquetado, manifiestos, esquemas de configuración
- [Pruebas](/es/plugins/sdk-testing) — utilidades de prueba y reglas de lint
- [Migración del SDK](/es/plugins/sdk-migration) — migración desde superficies obsoletas
- [Internals de plugins](/es/plugins/architecture) — arquitectura profunda y modelo de capacidades
