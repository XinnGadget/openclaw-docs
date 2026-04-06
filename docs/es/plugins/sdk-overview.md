---
read_when:
    - Necesitas saber desde qué subruta del SDK importar
    - Quieres una referencia para todos los métodos de registro en OpenClawPluginApi
    - Estás buscando una exportación específica del SDK
sidebarTitle: SDK Overview
summary: Mapa de importación, referencia de la API de registro y arquitectura del SDK
title: Descripción general del SDK de plugins
x-i18n:
    generated_at: "2026-04-06T05:13:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: acd2887ef52c66b2f234858d812bb04197ecd0bfb3e4f7bf3622f8fdc765acad
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Descripción general del SDK de plugins

El SDK de plugins es el contrato tipado entre los plugins y el núcleo. Esta página es la
referencia de **qué importar** y **qué puedes registrar**.

<Tip>
  **¿Buscas una guía práctica?**
  - ¿Primer plugin? Empieza con [Getting Started](/es/plugins/building-plugins)
  - ¿Plugin de canal? Consulta [Channel Plugins](/es/plugins/sdk-channel-plugins)
  - ¿Plugin de proveedor? Consulta [Provider Plugins](/es/plugins/sdk-provider-plugins)
</Tip>

## Convención de importación

Importa siempre desde una subruta específica:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Cada subruta es un módulo pequeño y autocontenido. Esto mantiene un inicio rápido y
evita problemas de dependencias circulares. Para los ayudantes de entrada/construcción específicos de canal,
prefiere `openclaw/plugin-sdk/channel-core`; deja `openclaw/plugin-sdk/core` para
la superficie paraguas más amplia y los ayudantes compartidos como
`buildChannelConfigSchema`.

No agregues ni dependas de interfaces de conveniencia con nombre de proveedor como
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, ni de
interfaces auxiliares con marca de canal. Los plugins incluidos deben componer subrutas genéricas
del SDK dentro de sus propios barrels `api.ts` o `runtime-api.ts`, y el núcleo
debe usar esos barrels locales del plugin o agregar un contrato genérico y reducido del SDK
cuando la necesidad sea realmente transversal a varios canales.

El mapa de exportaciones generado todavía contiene un pequeño conjunto de
interfaces auxiliares para plugins incluidos como `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` y `plugin-sdk/matrix*`. Esas
subrutas existen solo para mantenimiento y compatibilidad de plugins incluidos; se
omiten intencionalmente de la tabla común de abajo y no son la ruta de importación
recomendada para nuevos plugins de terceros.

## Referencia de subrutas

Las subrutas más usadas con frecuencia, agrupadas por propósito. La lista completa generada de
más de 200 subrutas está en `scripts/lib/plugin-sdk-entrypoints.json`.

Las subrutas auxiliares reservadas para plugins incluidos siguen apareciendo en esa lista generada.
Trátalas como superficies de detalle de implementación/compatibilidad salvo que una página de documentación
promueva explícitamente alguna como pública.

### Entrada del plugin

| Subruta                    | Exportaciones clave                                                                                                                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`  | `definePluginEntry`                                                                                                                   |
| `plugin-sdk/core`          | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema` | `OpenClawSchema`                                                                                                                      |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="Subrutas de canal">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Exportación del esquema Zod raíz de `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, además de `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Ayudantes compartidos del asistente de configuración, indicaciones de allowlist, constructores de estado de configuración |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Ayudantes de configuración/puerta de acción para varias cuentas, ayudantes de respaldo de cuenta predeterminada |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, ayudantes de normalización de ID de cuenta |
    | `plugin-sdk/account-resolution` | Búsqueda de cuentas + ayudantes de respaldo predeterminado |
    | `plugin-sdk/account-helpers` | Ayudantes específicos para lista de cuentas/acciones de cuenta |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipos de esquema de configuración de canal |
    | `plugin-sdk/telegram-command-config` | Ayudantes de normalización/validación de comandos personalizados de Telegram con respaldo del contrato incluido |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Ayudantes compartidos para rutas de entrada + creación de sobres |
    | `plugin-sdk/inbound-reply-dispatch` | Ayudantes compartidos para registrar y despachar entradas |
    | `plugin-sdk/messaging-targets` | Ayudantes para analizar/emparejar destinos |
    | `plugin-sdk/outbound-media` | Ayudantes compartidos para cargar medios salientes |
    | `plugin-sdk/outbound-runtime` | Ayudantes de identidad saliente/del delegado de envío |
    | `plugin-sdk/thread-bindings-runtime` | Ciclo de vida de vinculaciones de hilos y ayudantes de adaptador |
    | `plugin-sdk/agent-media-payload` | Constructor heredado de carga útil de medios del agente |
    | `plugin-sdk/conversation-runtime` | Ayudantes de vinculación de conversación/hilo, emparejamiento y vinculación configurada |
    | `plugin-sdk/runtime-config-snapshot` | Ayudante de instantánea de configuración en tiempo de ejecución |
    | `plugin-sdk/runtime-group-policy` | Ayudantes de resolución de políticas de grupo en tiempo de ejecución |
    | `plugin-sdk/channel-status` | Ayudantes compartidos para instantáneas/resúmenes de estado de canal |
    | `plugin-sdk/channel-config-primitives` | Primitivas específicas del esquema de configuración de canal |
    | `plugin-sdk/channel-config-writes` | Ayudantes de autorización de escritura de configuración de canal |
    | `plugin-sdk/channel-plugin-common` | Exportaciones de preludio compartidas para plugins de canal |
    | `plugin-sdk/allowlist-config-edit` | Ayudantes para editar/leer configuración de allowlist |
    | `plugin-sdk/group-access` | Ayudantes compartidos para decisiones de acceso a grupos |
    | `plugin-sdk/direct-dm` | Ayudantes compartidos para autenticación/protección de mensajes directos |
    | `plugin-sdk/interactive-runtime` | Ayudantes para normalización/reducción de cargas útiles de respuestas interactivas |
    | `plugin-sdk/channel-inbound` | Debounce, coincidencia de menciones, ayudantes de sobres |
    | `plugin-sdk/channel-send-result` | Tipos de resultado de respuesta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Ayudantes para analizar/emparejar destinos |
    | `plugin-sdk/channel-contract` | Tipos de contrato de canal |
    | `plugin-sdk/channel-feedback` | Integración de comentarios/reacciones |
  </Accordion>

  <Accordion title="Subrutas de proveedor">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Ayudantes seleccionados de configuración para proveedores locales/autohospedados |
    | `plugin-sdk/self-hosted-provider-setup` | Ayudantes enfocados de configuración para proveedores autohospedados compatibles con OpenAI |
    | `plugin-sdk/provider-auth-runtime` | Ayudantes de resolución de claves API en tiempo de ejecución para plugins de proveedor |
    | `plugin-sdk/provider-auth-api-key` | Ayudantes de incorporación/escritura de perfil de clave API |
    | `plugin-sdk/provider-auth-result` | Constructor estándar de resultado de autenticación OAuth |
    | `plugin-sdk/provider-auth-login` | Ayudantes compartidos de inicio de sesión interactivo para plugins de proveedor |
    | `plugin-sdk/provider-env-vars` | Ayudantes de búsqueda de variables de entorno de autenticación de proveedor |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, constructores compartidos de políticas de repetición, ayudantes de endpoints de proveedor y ayudantes de normalización de ID de modelo como `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Ayudantes genéricos de capacidades HTTP/endpoint de proveedor |
    | `plugin-sdk/provider-web-fetch` | Ayudantes de registro/caché para proveedores de captura web |
    | `plugin-sdk/provider-web-search` | Ayudantes de registro/caché/configuración para proveedores de búsqueda web |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, limpieza de esquemas Gemini + diagnósticos y ayudantes de compatibilidad de xAI como `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` y similares |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipos de envoltorios de flujo y ayudantes compartidos de envoltorios para Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Ayudantes de parcheo de configuración de incorporación |
    | `plugin-sdk/global-singleton` | Ayudantes de singleton/mapa/caché local al proceso |
  </Accordion>

  <Accordion title="Subrutas de autenticación y seguridad">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, ayudantes del registro de comandos, ayudantes de autorización del remitente |
    | `plugin-sdk/approval-auth-runtime` | Ayudantes para resolución de aprobadores y autenticación de acciones en el mismo chat |
    | `plugin-sdk/approval-client-runtime` | Ayudantes de perfil/filtro de aprobación de ejecución nativa |
    | `plugin-sdk/approval-delivery-runtime` | Adaptadores nativos de capacidad/entrega de aprobación |
    | `plugin-sdk/approval-native-runtime` | Ayudantes nativos de destino de aprobación + vinculación de cuenta |
    | `plugin-sdk/approval-reply-runtime` | Ayudantes de carga útil de respuesta para aprobación de ejecución/plugin |
    | `plugin-sdk/command-auth-native` | Autenticación de comandos nativos + ayudantes nativos de destino de sesión |
    | `plugin-sdk/command-detection` | Ayudantes compartidos de detección de comandos |
    | `plugin-sdk/command-surface` | Normalización del cuerpo de comandos y ayudantes de superficie de comandos |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Ayudantes compartidos para confianza, bloqueo de mensajes directos, contenido externo y recolección de secretos |
    | `plugin-sdk/ssrf-policy` | Ayudantes de allowlist de hosts y política SSRF de red privada |
    | `plugin-sdk/ssrf-runtime` | Ayudantes de dispatcher fijado, fetch con protección SSRF y política SSRF |
    | `plugin-sdk/secret-input` | Ayudantes de análisis de entrada secreta |
    | `plugin-sdk/webhook-ingress` | Ayudantes de solicitud/destino de webhook |
    | `plugin-sdk/webhook-request-guards` | Ayudantes de tamaño de cuerpo/tiempo de espera de solicitud |
  </Accordion>

  <Accordion title="Subrutas de runtime y almacenamiento">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/runtime` | Ayudantes amplios de runtime, registro, copias de seguridad e instalación de plugins |
    | `plugin-sdk/runtime-env` | Ayudantes específicos de entorno de runtime, logger, tiempo de espera, reintento y retroceso |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Ayudantes compartidos para comandos, hooks, HTTP e interacciones de plugins |
    | `plugin-sdk/hook-runtime` | Ayudantes compartidos del flujo de hooks webhook/internos |
    | `plugin-sdk/lazy-runtime` | Ayudantes de importación/vinculación perezosa en tiempo de ejecución como `createLazyRuntimeModule`, `createLazyRuntimeMethod` y `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Ayudantes de ejecución de procesos |
    | `plugin-sdk/cli-runtime` | Ayudantes de formato, espera y versión para CLI |
    | `plugin-sdk/gateway-runtime` | Ayudantes de cliente de gateway y parcheo de estado de canal |
    | `plugin-sdk/config-runtime` | Ayudantes para cargar/escribir configuración |
    | `plugin-sdk/telegram-command-config` | Normalización de nombre/descripción de comandos de Telegram y comprobaciones de duplicados/conflictos, incluso cuando la superficie del contrato incluido de Telegram no está disponible |
    | `plugin-sdk/approval-runtime` | Ayudantes de aprobación de ejecución/plugin, constructores de capacidad de aprobación, ayudantes de autenticación/perfil, ayudantes nativos de enrutamiento/runtime |
    | `plugin-sdk/reply-runtime` | Ayudantes compartidos de runtime de entrada/respuesta, fragmentación, despacho, latido, planificador de respuestas |
    | `plugin-sdk/reply-dispatch-runtime` | Ayudantes específicos para despacho/finalización de respuestas |
    | `plugin-sdk/reply-history` | Ayudantes compartidos de historial de respuestas de ventana corta como `buildHistoryContext`, `recordPendingHistoryEntry` y `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Ayudantes específicos para fragmentación de texto/markdown |
    | `plugin-sdk/session-store-runtime` | Ayudantes de ruta de almacén de sesión + `updated-at` |
    | `plugin-sdk/state-paths` | Ayudantes de rutas de directorios de estado/OAuth |
    | `plugin-sdk/routing` | Ayudantes de ruta/clave de sesión/vinculación de cuenta como `resolveAgentRoute`, `buildAgentSessionKey` y `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Ayudantes compartidos para resúmenes de estado de canal/cuenta, valores predeterminados de estado de runtime y ayudantes de metadatos de incidencias |
    | `plugin-sdk/target-resolver-runtime` | Ayudantes compartidos de resolución de destinos |
    | `plugin-sdk/string-normalization-runtime` | Ayudantes de normalización de slug/cadenas |
    | `plugin-sdk/request-url` | Extraer URL en formato cadena de entradas tipo fetch/request |
    | `plugin-sdk/run-command` | Ejecutor de comandos temporizado con resultados normalizados de stdout/stderr |
    | `plugin-sdk/param-readers` | Lectores comunes de parámetros para herramientas/CLI |
    | `plugin-sdk/tool-send` | Extraer campos canónicos del destino de envío desde argumentos de herramientas |
    | `plugin-sdk/temp-path` | Ayudantes compartidos de rutas temporales de descarga |
    | `plugin-sdk/logging-core` | Logger de subsistema y ayudantes de redacción |
    | `plugin-sdk/markdown-table-runtime` | Ayudantes de modo de tabla Markdown |
    | `plugin-sdk/json-store` | Ayudantes pequeños para leer/escribir estado JSON |
    | `plugin-sdk/file-lock` | Ayudantes de bloqueo de archivos reentrantes |
    | `plugin-sdk/persistent-dedupe` | Ayudantes de caché de deduplicación respaldada en disco |
    | `plugin-sdk/acp-runtime` | Ayudantes de runtime/sesión ACP y despacho de respuestas |
    | `plugin-sdk/agent-config-primitives` | Primitivas específicas del esquema de configuración de runtime de agentes |
    | `plugin-sdk/boolean-param` | Lector flexible de parámetros booleanos |
    | `plugin-sdk/dangerous-name-runtime` | Ayudantes de resolución de coincidencias de nombres peligrosos |
    | `plugin-sdk/device-bootstrap` | Ayudantes de inicialización de dispositivos y tokens de emparejamiento |
    | `plugin-sdk/extension-shared` | Primitivas compartidas para canales pasivos y ayudantes de estado |
    | `plugin-sdk/models-provider-runtime` | Ayudantes de respuesta para el comando `/models` y proveedores |
    | `plugin-sdk/skill-commands-runtime` | Ayudantes de listado de comandos de Skills |
    | `plugin-sdk/native-command-registry` | Ayudantes para registrar/construir/serializar comandos nativos |
    | `plugin-sdk/provider-zai-endpoint` | Ayudantes de detección de endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Ayudantes de eventos del sistema/latido |
    | `plugin-sdk/collection-runtime` | Ayudantes de caché acotada pequeña |
    | `plugin-sdk/diagnostic-runtime` | Ayudantes de indicadores y eventos de diagnóstico |
    | `plugin-sdk/error-runtime` | Grafo de errores, formato, ayudantes compartidos de clasificación de errores, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Ayudantes de fetch envuelto, proxy y búsqueda fijada |
    | `plugin-sdk/host-runtime` | Ayudantes de normalización de nombre de host y host SCP |
    | `plugin-sdk/retry-runtime` | Ayudantes de configuración y ejecución de reintentos |
    | `plugin-sdk/agent-runtime` | Ayudantes de directorio/identidad/espacio de trabajo del agente |
    | `plugin-sdk/directory-runtime` | Consulta/deduplicación de directorios respaldados por configuración |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Subrutas de capacidades y pruebas">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Ayudantes compartidos para obtener/transformar/almacenar medios, además de constructores de cargas útiles de medios |
    | `plugin-sdk/media-generation-runtime` | Ayudantes compartidos para failover de generación de medios, selección de candidatos y mensajes de modelo faltante |
    | `plugin-sdk/media-understanding` | Tipos de proveedor para comprensión de medios más exportaciones de ayudantes de imagen/audio orientadas a proveedores |
    | `plugin-sdk/text-runtime` | Ayudantes compartidos de texto/markdown/logging como eliminación de texto visible para el asistente, ayudantes de renderizado/fragmentación/tablas de markdown, ayudantes de redacción, ayudantes de etiquetas de directivas y utilidades de texto seguro |
    | `plugin-sdk/text-chunking` | Ayudante de fragmentación de texto saliente |
    | `plugin-sdk/speech` | Tipos de proveedor de voz más ayudantes orientados a proveedores para directivas, registro y validación |
    | `plugin-sdk/speech-core` | Tipos compartidos de proveedor de voz, registro, directivas y ayudantes de normalización |
    | `plugin-sdk/realtime-transcription` | Tipos de proveedor de transcripción en tiempo real y ayudantes de registro |
    | `plugin-sdk/realtime-voice` | Tipos de proveedor de voz en tiempo real y ayudantes de registro |
    | `plugin-sdk/image-generation` | Tipos de proveedor de generación de imágenes |
    | `plugin-sdk/image-generation-core` | Tipos compartidos de generación de imágenes, failover, autenticación y ayudantes de registro |
    | `plugin-sdk/music-generation` | Tipos de proveedor/solicitud/resultado de generación musical |
    | `plugin-sdk/music-generation-core` | Tipos compartidos de generación musical, ayudantes de failover, búsqueda de proveedores y análisis de referencias de modelos |
    | `plugin-sdk/video-generation` | Tipos de proveedor/solicitud/resultado de generación de video |
    | `plugin-sdk/video-generation-core` | Tipos compartidos de generación de video, ayudantes de failover, búsqueda de proveedores y análisis de referencias de modelos |
    | `plugin-sdk/webhook-targets` | Registro de destinos de webhook y ayudantes de instalación de rutas |
    | `plugin-sdk/webhook-path` | Ayudantes de normalización de rutas de webhook |
    | `plugin-sdk/web-media` | Ayudantes compartidos para carga de medios remotos/locales |
    | `plugin-sdk/zod` | `zod` reexportado para consumidores del SDK de plugins |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Subrutas de memoria">
    | Subruta | Exportaciones clave |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superficie auxiliar `memory-core` incluida para ayudantes de administrador/configuración/archivo/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Fachada de runtime para indexación/búsqueda de memoria |
    | `plugin-sdk/memory-core-host-engine-foundation` | Exportaciones del motor base del host de memoria |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Exportaciones del motor de embeddings del host de memoria |
    | `plugin-sdk/memory-core-host-engine-qmd` | Exportaciones del motor QMD del host de memoria |
    | `plugin-sdk/memory-core-host-engine-storage` | Exportaciones del motor de almacenamiento del host de memoria |
    | `plugin-sdk/memory-core-host-multimodal` | Ayudantes multimodales del host de memoria |
    | `plugin-sdk/memory-core-host-query` | Ayudantes de consulta del host de memoria |
    | `plugin-sdk/memory-core-host-secret` | Ayudantes de secretos del host de memoria |
    | `plugin-sdk/memory-core-host-events` | Ayudantes de diario de eventos del host de memoria |
    | `plugin-sdk/memory-core-host-status` | Ayudantes de estado del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-cli` | Ayudantes de runtime CLI del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-core` | Ayudantes de runtime central del host de memoria |
    | `plugin-sdk/memory-core-host-runtime-files` | Ayudantes de archivos/runtime del host de memoria |
    | `plugin-sdk/memory-host-core` | Alias neutral al proveedor para ayudantes de runtime central del host de memoria |
    | `plugin-sdk/memory-host-events` | Alias neutral al proveedor para ayudantes del diario de eventos del host de memoria |
    | `plugin-sdk/memory-host-files` | Alias neutral al proveedor para ayudantes de archivos/runtime del host de memoria |
    | `plugin-sdk/memory-host-markdown` | Ayudantes compartidos de markdown gestionado para plugins adyacentes a memoria |
    | `plugin-sdk/memory-host-search` | Fachada de runtime de memoria activa para acceso al administrador de búsqueda |
    | `plugin-sdk/memory-host-status` | Alias neutral al proveedor para ayudantes de estado del host de memoria |
    | `plugin-sdk/memory-lancedb` | Superficie auxiliar `memory-lancedb` incluida |
  </Accordion>

  <Accordion title="Subrutas reservadas de ayudantes incluidos">
    | Familia | Subrutas actuales | Uso previsto |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Ayudantes de soporte para el plugin Browser incluido (`browser-support` sigue siendo el barrel de compatibilidad) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superficie auxiliar/de runtime de Matrix incluida |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superficie auxiliar/de runtime de LINE incluida |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superficie auxiliar de IRC incluida |
    | Ayudantes específicos de canal | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Interfaces auxiliares/de compatibilidad de canales incluidos |
    | Ayudantes específicos de autenticación/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Interfaces auxiliares de funciones/plugins incluidos; `plugin-sdk/github-copilot-token` exporta actualmente `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` y `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API de registro

La devolución de llamada `register(api)` recibe un objeto `OpenClawPluginApi` con estos
métodos:

### Registro de capacidades

| Método                                           | Qué registra                    |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | Inferencia de texto (LLM)       |
| `api.registerChannel(...)`                       | Canal de mensajería             |
| `api.registerSpeechProvider(...)`                | Síntesis de texto a voz / STT   |
| `api.registerRealtimeTranscriptionProvider(...)` | Transcripción en tiempo real por streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sesiones de voz dúplex en tiempo real |
| `api.registerMediaUnderstandingProvider(...)`    | Análisis de imagen/audio/video  |
| `api.registerImageGenerationProvider(...)`       | Generación de imágenes          |
| `api.registerMusicGenerationProvider(...)`       | Generación de música            |
| `api.registerVideoGenerationProvider(...)`       | Generación de video             |
| `api.registerWebFetchProvider(...)`              | Proveedor de captura / scraping web |
| `api.registerWebSearchProvider(...)`             | Búsqueda web                    |

### Herramientas y comandos

| Método                          | Qué registra                                  |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Herramienta del agente (obligatoria o `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizado (omite el LLM)          |

### Infraestructura

| Método                                         | Qué registra                            |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook de eventos                         |
| `api.registerHttpRoute(params)`                | Endpoint HTTP del gateway               |
| `api.registerGatewayMethod(name, handler)`     | Método RPC del gateway                  |
| `api.registerCli(registrar, opts?)`            | Subcomando de CLI                       |
| `api.registerService(service)`                 | Servicio en segundo plano               |
| `api.registerInteractiveHandler(registration)` | Manejador interactivo                   |
| `api.registerMemoryPromptSupplement(builder)`  | Sección adicional del prompt adyacente a memoria |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus adicional de búsqueda/lectura de memoria |

Los espacios de nombres administrativos reservados del núcleo (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) siempre permanecen como `operator.admin`, incluso si un plugin intenta asignar un
alcance más limitado al método del gateway. Prefiere prefijos específicos del plugin para
métodos propios del plugin.

### Metadatos de registro de CLI

`api.registerCli(registrar, opts?)` acepta dos tipos de metadatos de nivel superior:

- `commands`: raíces de comandos explícitas propiedad del registrador
- `descriptors`: descriptores de comandos en tiempo de análisis usados para la ayuda del CLI raíz,
  enrutamiento y registro perezoso del CLI del plugin

Si quieres que un comando del plugin permanezca con carga perezosa en la ruta normal del CLI raíz,
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

Usa `commands` por sí solo solo cuando no necesites registro perezoso en el CLI raíz.
Esa ruta de compatibilidad ansiosa sigue siendo compatible, pero no instala
marcadores respaldados por descriptores para carga perezosa en tiempo de análisis.

### Ranuras exclusivas

| Método                                     | Qué registra                         |
| ------------------------------------------ | ------------------------------------ |
| `api.registerContextEngine(id, factory)`   | Motor de contexto (solo uno activo a la vez) |
| `api.registerMemoryPromptSection(builder)` | Constructor de sección de prompt de memoria |
| `api.registerMemoryFlushPlan(resolver)`    | Resolutor del plan de vaciado de memoria |
| `api.registerMemoryRuntime(runtime)`       | Adaptador de runtime de memoria      |

### Adaptadores de embeddings de memoria

| Método                                         | Qué registra                                   |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adaptador de embeddings de memoria para el plugin activo |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` y
  `registerMemoryRuntime` son exclusivos para plugins de memoria.
- `registerMemoryEmbeddingProvider` permite que el plugin de memoria activo registre uno
  o más ID de adaptadores de embeddings (por ejemplo `openai`, `gemini` o un ID personalizado
  definido por el plugin).
- La configuración del usuario como `agents.defaults.memorySearch.provider` y
  `agents.defaults.memorySearch.fallback` se resuelve contra esos ID de adaptadores
  registrados.

### Eventos y ciclo de vida

| Método                                       | Qué hace                     |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook tipado del ciclo de vida |
| `api.onConversationBindingResolved(handler)` | Devolución de llamada de vinculación de conversación |

### Semántica de decisión de hooks

- `before_tool_call`: devolver `{ block: true }` es terminal. Una vez que cualquier manejador lo establece, se omiten los manejadores de menor prioridad.
- `before_tool_call`: devolver `{ block: false }` se trata como ausencia de decisión (igual que omitir `block`), no como una anulación.
- `before_install`: devolver `{ block: true }` es terminal. Una vez que cualquier manejador lo establece, se omiten los manejadores de menor prioridad.
- `before_install`: devolver `{ block: false }` se trata como ausencia de decisión (igual que omitir `block`), no como una anulación.
- `reply_dispatch`: devolver `{ handled: true, ... }` es terminal. Una vez que cualquier manejador reclama el despacho, se omiten los manejadores de menor prioridad y la ruta predeterminada de despacho del modelo.
- `message_sending`: devolver `{ cancel: true }` es terminal. Una vez que cualquier manejador lo establece, se omiten los manejadores de menor prioridad.
- `message_sending`: devolver `{ cancel: false }` se trata como ausencia de decisión (igual que omitir `cancel`), no como una anulación.

### Campos del objeto API

| Campo                    | Tipo                      | Descripción                                                                                |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | ID del plugin                                                                              |
| `api.name`               | `string`                  | Nombre para mostrar                                                                        |
| `api.version`            | `string?`                 | Versión del plugin (opcional)                                                              |
| `api.description`        | `string?`                 | Descripción del plugin (opcional)                                                          |
| `api.source`             | `string`                  | Ruta de origen del plugin                                                                  |
| `api.rootDir`            | `string?`                 | Directorio raíz del plugin (opcional)                                                      |
| `api.config`             | `OpenClawConfig`          | Instantánea de configuración actual (instantánea activa en memoria en tiempo de ejecución cuando está disponible) |
| `api.pluginConfig`       | `Record<string, unknown>` | Configuración específica del plugin de `plugins.entries.<id>.config`                       |
| `api.runtime`            | `PluginRuntime`           | [Ayudantes de runtime](/es/plugins/sdk-runtime)                                               |
| `api.logger`             | `PluginLogger`            | Logger con alcance (`debug`, `info`, `warn`, `error`)                                      |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modo de carga actual; `"setup-runtime"` es la ventana ligera de inicio/configuración previa a la entrada completa |
| `api.resolvePath(input)` | `(string) => string`      | Resuelve una ruta relativa a la raíz del plugin                                            |

## Convención de módulos internos

Dentro de tu plugin, usa archivos barrel locales para las importaciones internas:

```
my-plugin/
  api.ts            # Exportaciones públicas para consumidores externos
  runtime-api.ts    # Exportaciones internas solo para runtime
  index.ts          # Punto de entrada del plugin
  setup-entry.ts    # Entrada ligera solo para configuración (opcional)
```

<Warning>
  Nunca importes tu propio plugin mediante `openclaw/plugin-sdk/<your-plugin>`
  desde código de producción. Enruta las importaciones internas a través de `./api.ts` o
  `./runtime-api.ts`. La ruta del SDK es solo el contrato externo.
</Warning>

Las superficies públicas de plugins incluidos cargadas mediante fachada (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` y archivos de entrada públicos similares) ahora prefieren la
instantánea activa de configuración en tiempo de ejecución cuando OpenClaw ya está en ejecución. Si todavía
no existe una instantánea de runtime, recurren al archivo de configuración resuelto en disco.

Los plugins de proveedor también pueden exponer un barrel de contrato local y específico del plugin cuando un
ayudante es intencionalmente específico del proveedor y todavía no pertenece a una subruta genérica del SDK.
Ejemplo incluido actual: el proveedor Anthropic mantiene sus ayudantes de flujo Claude
en su propia interfaz pública `api.ts` / `contract-api.ts` en lugar de
promover la lógica de encabezados beta de Anthropic y `service_tier` a un contrato genérico
`plugin-sdk/*`.

Otros ejemplos incluidos actuales:

- `@openclaw/openai-provider`: `api.ts` exporta constructores de proveedor,
  ayudantes de modelo predeterminado y constructores de proveedor en tiempo real
- `@openclaw/openrouter-provider`: `api.ts` exporta el constructor del proveedor más
  ayudantes de incorporación/configuración

<Warning>
  El código de producción de extensiones también debe evitar importaciones de `openclaw/plugin-sdk/<other-plugin>`.
  Si un ayudante es realmente compartido, promuévelo a una subruta neutral del SDK
  como `openclaw/plugin-sdk/speech`, `.../provider-model-shared` u otra
  superficie orientada a capacidades, en lugar de acoplar dos plugins entre sí.
</Warning>

## Relacionado

- [Entry Points](/es/plugins/sdk-entrypoints) — opciones de `definePluginEntry` y `defineChannelPluginEntry`
- [Runtime Helpers](/es/plugins/sdk-runtime) — referencia completa del espacio de nombres `api.runtime`
- [Setup and Config](/es/plugins/sdk-setup) — empaquetado, manifiestos, esquemas de configuración
- [Testing](/es/plugins/sdk-testing) — utilidades de prueba y reglas de lint
- [SDK Migration](/es/plugins/sdk-migration) — migración desde superficies obsoletas
- [Plugin Internals](/es/plugins/architecture) — arquitectura profunda y modelo de capacidades
