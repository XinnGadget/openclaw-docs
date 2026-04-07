---
read_when:
    - Agregar o modificar migraciones de doctor
    - Introducir cambios incompatibles en la configuración
summary: 'Comando Doctor: comprobaciones de estado, migraciones de configuración y pasos de reparación'
title: Doctor
x-i18n:
    generated_at: "2026-04-07T05:03:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: a834dc7aec79c20d17bc23d37fb5f5e99e628d964d55bd8cf24525a7ee57130c
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` es la herramienta de reparación + migración de OpenClaw. Corrige configuraciones y estados obsoletos, comprueba el estado y proporciona pasos de reparación accionables.

## Inicio rápido

```bash
openclaw doctor
```

### Modo sin interfaz / automatización

```bash
openclaw doctor --yes
```

Acepta los valores predeterminados sin solicitar confirmación (incluidos los pasos de reparación de reinicio/servicio/sandbox cuando corresponda).

```bash
openclaw doctor --repair
```

Aplica las reparaciones recomendadas sin solicitar confirmación (reparaciones + reinicios cuando sea seguro).

```bash
openclaw doctor --repair --force
```

Aplica también reparaciones agresivas (sobrescribe configuraciones personalizadas del supervisor).

```bash
openclaw doctor --non-interactive
```

Se ejecuta sin solicitudes y solo aplica migraciones seguras (normalización de configuración + movimientos de estado en disco). Omite acciones de reinicio/servicio/sandbox que requieren confirmación humana.
Las migraciones de estado heredado se ejecutan automáticamente cuando se detectan.

```bash
openclaw doctor --deep
```

Analiza los servicios del sistema para detectar instalaciones adicionales de gateway (launchd/systemd/schtasks).

Si quieres revisar los cambios antes de escribir, abre primero el archivo de configuración:

```bash
cat ~/.openclaw/openclaw.json
```

## Qué hace (resumen)

- Actualización opcional previa a la ejecución para instalaciones desde git (solo interactivo).
- Comprobación de vigencia del protocolo de la UI (reconstruye Control UI cuando el esquema de protocolo es más reciente).
- Comprobación de estado + solicitud de reinicio.
- Resumen del estado de Skills (elegibles/faltantes/bloqueadas) y estado de plugins.
- Normalización de configuración para valores heredados.
- Migración de la configuración de Talk desde campos planos heredados `talk.*` a `talk.provider` + `talk.providers.<provider>`.
- Comprobaciones de migración del navegador para configuraciones heredadas de la extensión de Chrome y preparación de Chrome MCP.
- Advertencias de anulación del proveedor OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- Comprobación de requisitos previos de TLS para OAuth de OpenAI Codex.
- Migración de estado heredado en disco (sesiones/directorio de agente/autenticación de WhatsApp).
- Migración heredada de claves de contrato en manifiestos de plugins (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Migración heredada del almacén de cron (`jobId`, `schedule.cron`, campos `delivery`/`payload` de nivel superior, `provider` en `payload`, trabajos heredados de respaldo webhook simples con `notify: true`).
- Inspección de archivos de bloqueo de sesión y limpieza de bloqueos obsoletos.
- Comprobaciones de integridad y permisos del estado (sesiones, transcripciones, directorio de estado).
- Comprobaciones de permisos del archivo de configuración (`chmod 600`) al ejecutarse localmente.
- Estado de autenticación de modelos: comprueba el vencimiento de OAuth, puede actualizar tokens a punto de expirar e informa estados de enfriamiento/deshabilitación de perfiles de autenticación.
- Detección de directorios de espacio de trabajo adicionales (`~/openclaw`).
- Reparación de imagen de sandbox cuando el sandboxing está habilitado.
- Migración de servicios heredados y detección de gateways adicionales.
- Migración de estado heredado del canal Matrix (en modo `--fix` / `--repair`).
- Comprobaciones de tiempo de ejecución del gateway (servicio instalado pero no en ejecución; etiqueta launchd en caché).
- Advertencias de estado de canales (sondeadas desde el gateway en ejecución).
- Auditoría de configuración del supervisor (launchd/systemd/schtasks) con reparación opcional.
- Comprobaciones de buenas prácticas del tiempo de ejecución del gateway (Node frente a Bun, rutas de gestores de versiones).
- Diagnóstico de colisión de puertos del gateway (predeterminado `18789`).
- Advertencias de seguridad para políticas de mensajes directos abiertas.
- Comprobaciones de autenticación del gateway para el modo de token local (ofrece generar un token cuando no existe ninguna fuente de token; no sobrescribe configuraciones de token SecretRef).
- Comprobación de `systemd linger` en Linux.
- Comprobación del tamaño de archivos bootstrap del espacio de trabajo (advertencias de truncamiento/cercanía al límite para archivos de contexto).
- Comprobación del estado de autocompletado del shell e instalación/actualización automática.
- Comprobación de preparación del proveedor de embeddings para búsqueda en memoria (modelo local, clave de API remota o binario QMD).
- Comprobaciones de instalación desde código fuente (desajuste del espacio de trabajo pnpm, recursos de UI faltantes, binario tsx faltante).
- Escribe la configuración actualizada + metadatos del asistente.

## Comportamiento detallado y justificación

### 0) Actualización opcional (instalaciones desde git)

Si se trata de un clon de git y doctor se ejecuta de forma interactiva, ofrece actualizar (fetch/rebase/build) antes de ejecutar doctor.

### 1) Normalización de configuración

Si la configuración contiene formas de valores heredados (por ejemplo `messages.ackReaction`
sin una anulación específica del canal), doctor las normaliza al esquema actual.

Eso incluye campos planos heredados de Talk. La configuración pública actual de Talk es
`talk.provider` + `talk.providers.<provider>`. Doctor reescribe las formas antiguas
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` en el mapa del proveedor.

### 2) Migraciones de claves de configuración heredadas

Cuando la configuración contiene claves obsoletas, otros comandos se niegan a ejecutarse y te piden
que ejecutes `openclaw doctor`.

Doctor hará lo siguiente:

- Explicar qué claves heredadas se encontraron.
- Mostrar la migración que aplicó.
- Reescribir `~/.openclaw/openclaw.json` con el esquema actualizado.

El Gateway también ejecuta automáticamente las migraciones de doctor al iniciarse cuando detecta un
formato de configuración heredado, por lo que las configuraciones obsoletas se reparan sin intervención manual.
Las migraciones del almacén de trabajos cron las gestiona `openclaw doctor --fix`.

Migraciones actuales:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → `bindings` de nivel superior
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- heredado `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- Para los canales con `accounts` con nombre pero con valores de canal de cuenta única aún presentes en el nivel superior, mover esos valores con ámbito de cuenta a la cuenta promovida elegida para ese canal (`accounts.default` para la mayoría de los canales; Matrix puede conservar un destino con nombre/predeterminado ya existente que coincida)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- eliminar `browser.relayBindHost` (ajuste heredado de relay de la extensión)

Las advertencias de doctor también incluyen orientación sobre cuentas predeterminadas para canales con múltiples cuentas:

- Si se configuran dos o más entradas `channels.<channel>.accounts` sin `channels.<channel>.defaultAccount` ni `accounts.default`, doctor advierte que el enrutamiento de respaldo puede elegir una cuenta inesperada.
- Si `channels.<channel>.defaultAccount` está establecido en un ID de cuenta desconocido, doctor advierte y enumera los ID de cuenta configurados.

### 2b) Anulaciones del proveedor OpenCode

Si añadiste manualmente `models.providers.opencode`, `opencode-zen` o `opencode-go`,
eso anula el catálogo integrado de OpenCode de `@mariozechner/pi-ai`.
Eso puede forzar modelos a usar la API incorrecta o dejar los costos en cero. Doctor advierte para que
puedas eliminar la anulación y restaurar el enrutamiento por API por modelo + los costos.

### 2c) Migración del navegador y preparación de Chrome MCP

Si tu configuración del navegador sigue apuntando a la ruta eliminada de la extensión de Chrome, doctor
la normaliza al modelo actual de adjuntar Chrome MCP local al host:

- `browser.profiles.*.driver: "extension"` pasa a ser `"existing-session"`
- se elimina `browser.relayBindHost`

Doctor también audita la ruta local al host de Chrome MCP cuando usas `defaultProfile:
"user"` o un perfil `existing-session` configurado:

- comprueba si Google Chrome está instalado en el mismo host para perfiles de
  conexión automática predeterminados
- comprueba la versión de Chrome detectada y advierte cuando es inferior a Chrome 144
- recuerda habilitar la depuración remota en la página de inspección del navegador (por
  ejemplo `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  o `edge://inspect/#remote-debugging`)

Doctor no puede habilitar por ti la configuración del lado de Chrome. Chrome MCP local al host
sigue requiriendo:

- un navegador basado en Chromium 144+ en el host del gateway/nodo
- el navegador ejecutándose localmente
- depuración remota habilitada en ese navegador
- aprobar la primera solicitud de consentimiento de conexión en el navegador

La preparación aquí solo se refiere a los requisitos previos de conexión local. Existing-session mantiene
los límites actuales de ruta de Chrome MCP; las rutas avanzadas como `responsebody`, exportación a PDF,
intercepción de descargas y acciones por lotes siguen requiriendo un navegador administrado
o un perfil CDP sin procesar.

Esta comprobación **no** se aplica a Docker, sandbox, navegador remoto ni otros
flujos sin interfaz. Esos siguen usando CDP sin procesar.

### 2d) Requisitos previos de TLS para OAuth

Cuando se configura un perfil OAuth de OpenAI Codex, doctor sondea el endpoint de autorización de OpenAI
para verificar que la pila TLS local de Node/OpenSSL puede validar la cadena de certificados. Si el sondeo falla con un error de certificado (por
ejemplo `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, certificado vencido o certificado autofirmado),
doctor muestra orientación de corrección específica de la plataforma. En macOS con Node instalado por Homebrew, la
solución suele ser `brew postinstall ca-certificates`. Con `--deep`, el sondeo se ejecuta
incluso si el gateway está en buen estado.

### 3) Migraciones de estado heredado (distribución en disco)

Doctor puede migrar distribuciones antiguas en disco a la estructura actual:

- Almacén de sesiones + transcripciones:
  - de `~/.openclaw/sessions/` a `~/.openclaw/agents/<agentId>/sessions/`
- Directorio del agente:
  - de `~/.openclaw/agent/` a `~/.openclaw/agents/<agentId>/agent/`
- Estado de autenticación de WhatsApp (Baileys):
  - desde `~/.openclaw/credentials/*.json` heredado (excepto `oauth.json`)
  - a `~/.openclaw/credentials/whatsapp/<accountId>/...` (ID de cuenta predeterminado: `default`)

Estas migraciones se hacen con el mejor esfuerzo y son idempotentes; doctor emitirá advertencias cuando
deje carpetas heredadas como copias de seguridad. Gateway/CLI también migra automáticamente
las sesiones heredadas + el directorio del agente al iniciarse para que el historial/la autenticación/los modelos queden en la
ruta por agente sin necesidad de ejecutar doctor manualmente. La autenticación de WhatsApp se migra
intencionalmente solo mediante `openclaw doctor`. La normalización de Talk por proveedor/mapa de proveedores ahora
compara por igualdad estructural, por lo que las diferencias solo en el orden de claves ya no provocan
cambios repetidos de no operación con `doctor --fix`.

### 3a) Migraciones heredadas de manifiestos de plugins

Doctor analiza todos los manifiestos de plugins instalados para detectar claves de capacidad obsoletas
de nivel superior (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Cuando las encuentra, ofrece moverlas al objeto `contracts`
y reescribir el archivo del manifiesto en el sitio. Esta migración es idempotente;
si la clave `contracts` ya tiene los mismos valores, la clave heredada se elimina
sin duplicar los datos.

### 3b) Migraciones heredadas del almacén de cron

Doctor también comprueba el almacén de trabajos cron (`~/.openclaw/cron/jobs.json` de forma predeterminada,
o `cron.store` cuando se sobrescribe) para detectar formas antiguas de trabajo que el programador todavía
acepta por compatibilidad.

Las limpiezas actuales de cron incluyen:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- campos `payload` de nivel superior (`message`, `model`, `thinking`, ...) → `payload`
- campos `delivery` de nivel superior (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- alias de entrega `provider` en payload → `delivery.channel` explícito
- trabajos heredados simples de respaldo webhook con `notify: true` → `delivery.mode="webhook"` explícito con `delivery.to=cron.webhook`

Doctor solo migra automáticamente trabajos `notify: true` cuando puede hacerlo sin
cambiar el comportamiento. Si un trabajo combina el respaldo heredado de notify con un
modo de entrega no webhook ya existente, doctor advierte y deja ese trabajo para revisión manual.

### 3c) Limpieza de bloqueos de sesión

Doctor analiza todos los directorios de sesión de agentes en busca de archivos de bloqueo de escritura obsoletos:
archivos dejados atrás cuando una sesión terminó de forma anómala. Por cada archivo de bloqueo encontrado informa:
la ruta, PID, si el PID sigue activo, antigüedad del bloqueo y si se
considera obsoleto (PID muerto o más de 30 minutos). En modo `--fix` / `--repair`
elimina automáticamente los archivos de bloqueo obsoletos; de lo contrario imprime una nota e
indica volver a ejecutar con `--fix`.

### 4) Comprobaciones de integridad del estado (persistencia de sesión, enrutamiento y seguridad)

El directorio de estado es el tronco operativo principal. Si desaparece, pierdes
sesiones, credenciales, registros y configuración (a menos que tengas copias de seguridad en otro lugar).

Doctor comprueba:

- **Falta el directorio de estado**: advierte sobre pérdida catastrófica del estado, solicita recrear
  el directorio y recuerda que no puede recuperar datos faltantes.
- **Permisos del directorio de estado**: verifica que se pueda escribir; ofrece reparar permisos
  (y emite una sugerencia de `chown` cuando detecta una discrepancia de propietario/grupo).
- **Directorio de estado sincronizado con la nube en macOS**: advierte cuando el estado se resuelve bajo iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) o
  `~/Library/CloudStorage/...` porque las rutas respaldadas por sincronización pueden causar E/S más lenta
  y carreras de bloqueo/sincronización.
- **Directorio de estado en SD o eMMC en Linux**: advierte cuando el estado se resuelve a una fuente de montaje `mmcblk*`,
  porque la E/S aleatoria respaldada por SD o eMMC puede ser más lenta y desgastarse
  más rápido con escrituras de sesión y credenciales.
- **Faltan directorios de sesión**: `sessions/` y el directorio del almacén de sesiones son
  necesarios para conservar el historial y evitar fallos `ENOENT`.
- **Desajuste de transcripciones**: advierte cuando entradas recientes de sesión tienen
  archivos de transcripción faltantes.
- **Sesión principal “JSONL de 1 línea”**: marca cuando la transcripción principal tiene solo una
  línea (el historial no se está acumulando).
- **Múltiples directorios de estado**: advierte cuando existen varias carpetas `~/.openclaw` en distintos
  directorios personales o cuando `OPENCLAW_STATE_DIR` apunta a otro lugar (el historial puede
  dividirse entre instalaciones).
- **Recordatorio de modo remoto**: si `gateway.mode=remote`, doctor recuerda ejecutarlo
  en el host remoto (el estado reside allí).
- **Permisos del archivo de configuración**: advierte si `~/.openclaw/openclaw.json` es
  legible por grupo/todos y ofrece restringirlo a `600`.

### 5) Estado de autenticación de modelos (vencimiento de OAuth)

Doctor inspecciona los perfiles OAuth en el almacén de autenticación, advierte cuando los tokens
están próximos a vencer o vencidos, y puede actualizarlos cuando es seguro. Si el perfil OAuth/token de Anthropic
está obsoleto, sugiere una clave de API de Anthropic o la
ruta de token de configuración de Anthropic.
Las solicitudes de actualización solo aparecen cuando se ejecuta de forma interactiva (TTY); `--non-interactive`
omite los intentos de actualización.

Doctor también informa perfiles de autenticación temporalmente inutilizables debido a:

- enfriamientos cortos (límites de tasa/tiempos de espera/fallos de autenticación)
- deshabilitaciones más largas (fallos de facturación/crédito)

### 6) Validación de modelo de hooks

Si `hooks.gmail.model` está configurado, doctor valida la referencia del modelo respecto al
catálogo y la lista de permitidos y advierte cuando no se resolverá o no está permitido.

### 7) Reparación de imagen de sandbox

Cuando el sandboxing está habilitado, doctor comprueba las imágenes de Docker y ofrece compilarlas o
cambiar a nombres heredados si la imagen actual falta.

### 7b) Dependencias de tiempo de ejecución de plugins incluidos

Doctor verifica que las dependencias de tiempo de ejecución de plugins incluidos (por ejemplo los
paquetes de tiempo de ejecución del plugin de Discord) estén presentes en la raíz de instalación de OpenClaw.
Si falta alguna, doctor informa los paquetes y los instala en
modo `openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) Migraciones de servicios de gateway y sugerencias de limpieza

Doctor detecta servicios heredados de gateway (launchd/systemd/schtasks) y
ofrece eliminarlos e instalar el servicio OpenClaw usando el puerto actual del gateway.
También puede analizar servicios adicionales similares a gateways e imprimir sugerencias de limpieza.
Los servicios gateway de OpenClaw con nombre de perfil se consideran de primera clase y no
se marcan como "adicionales".

### 8b) Migración de Matrix al inicio

Cuando una cuenta de canal Matrix tiene una migración de estado heredado pendiente o accionable,
doctor (en modo `--fix` / `--repair`) crea una instantánea previa a la migración y luego
ejecuta los pasos de migración con el mejor esfuerzo: migración del estado heredado de Matrix y preparación heredada de estado cifrado. Ambos pasos no son fatales; los errores se registran y
el inicio continúa. En modo de solo lectura (`openclaw doctor` sin `--fix`) esta comprobación
se omite por completo.

### 9) Advertencias de seguridad

Doctor emite advertencias cuando un proveedor está abierto a mensajes directos sin una lista de permitidos, o
cuando una política está configurada de forma peligrosa.

### 10) `systemd linger` (Linux)

Si se ejecuta como servicio de usuario systemd, doctor garantiza que lingering esté habilitado para que el
gateway siga activo después de cerrar sesión.

### 11) Estado del espacio de trabajo (Skills, plugins y directorios heredados)

Doctor muestra un resumen del estado del espacio de trabajo para el agente predeterminado:

- **Estado de Skills**: cuenta Skills elegibles, con requisitos faltantes y bloqueadas por la lista de permitidos.
- **Directorios heredados del espacio de trabajo**: advierte cuando `~/openclaw` u otros directorios heredados del espacio de trabajo
  existen junto al espacio de trabajo actual.
- **Estado de plugins**: cuenta plugins cargados/deshabilitados/con error; enumera los ID de plugin para cualquier
  error; informa capacidades de plugins del paquete.
- **Advertencias de compatibilidad de plugins**: marca plugins que tienen problemas de compatibilidad con
  el tiempo de ejecución actual.
- **Diagnósticos de plugins**: muestra advertencias o errores emitidos durante la carga por el
  registro de plugins.

### 11b) Tamaño del archivo bootstrap

Doctor comprueba si los archivos bootstrap del espacio de trabajo (por ejemplo `AGENTS.md`,
`CLAUDE.md` u otros archivos de contexto inyectados) están cerca o por encima del
presupuesto configurado de caracteres. Informa por archivo los recuentos de caracteres brutos frente a inyectados, el
porcentaje de truncamiento, la causa del truncamiento (`max/file` o `max/total`) y el total de caracteres
inyectados como fracción del presupuesto total. Cuando los archivos están truncados o cerca
del límite, doctor muestra consejos para ajustar `agents.defaults.bootstrapMaxChars`
y `agents.defaults.bootstrapTotalMaxChars`.

### 11c) Autocompletado del shell

Doctor comprueba si el autocompletado con tabulador está instalado para el shell actual
(zsh, bash, fish o PowerShell):

- Si el perfil del shell usa un patrón lento de autocompletado dinámico
  (`source <(openclaw completion ...)`), doctor lo actualiza a la variante más rápida
  de archivo en caché.
- Si el autocompletado está configurado en el perfil pero falta el archivo de caché,
  doctor regenera automáticamente la caché.
- Si no hay autocompletado configurado, doctor solicita instalarlo
  (solo modo interactivo; se omite con `--non-interactive`).

Ejecuta `openclaw completion --write-state` para regenerar la caché manualmente.

### 12) Comprobaciones de autenticación del gateway (token local)

Doctor comprueba la preparación de autenticación por token del gateway local.

- Si el modo token necesita un token y no existe ninguna fuente de token, doctor ofrece generar uno.
- Si `gateway.auth.token` se gestiona mediante SecretRef pero no está disponible, doctor advierte y no lo sobrescribe con texto sin formato.
- `openclaw doctor --generate-gateway-token` fuerza la generación solo cuando no hay ningún token SecretRef configurado.

### 12b) Reparaciones de solo lectura con reconocimiento de SecretRef

Algunos flujos de reparación necesitan inspeccionar credenciales configuradas sin debilitar el comportamiento de error rápido del tiempo de ejecución.

- `openclaw doctor --fix` ahora usa el mismo modelo de resumen SecretRef de solo lectura que los comandos de la familia status para reparaciones de configuración específicas.
- Ejemplo: la reparación de `allowFrom` / `groupAllowFrom` con `@username` de Telegram intenta usar credenciales del bot configuradas cuando están disponibles.
- Si el token del bot de Telegram está configurado mediante SecretRef pero no está disponible en la ruta actual del comando, doctor informa que la credencial está configurada pero no disponible y omite la resolución automática en lugar de fallar o informar erróneamente que falta el token.

### 13) Comprobación de estado del gateway + reinicio

Doctor ejecuta una comprobación de estado y ofrece reiniciar el gateway cuando parece
no estar en buen estado.

### 13b) Preparación de búsqueda en memoria

Doctor comprueba si el proveedor configurado de embeddings para búsqueda en memoria está listo
para el agente predeterminado. El comportamiento depende del backend y proveedor configurados:

- **Backend QMD**: sondea si el binario `qmd` está disponible y se puede iniciar.
  Si no, muestra orientación de corrección, incluido el paquete npm y una opción manual de ruta al binario.
- **Proveedor local explícito**: comprueba si existe un archivo de modelo local o una URL de modelo remota/descargable reconocida. Si falta, sugiere cambiar a un proveedor remoto.
- **Proveedor remoto explícito** (`openai`, `voyage`, etc.): verifica que haya una clave de API
  presente en el entorno o en el almacén de autenticación. Muestra sugerencias de corrección accionables si falta.
- **Proveedor automático**: comprueba primero la disponibilidad del modelo local y luego prueba cada
  proveedor remoto en orden de selección automática.

Cuando hay disponible un resultado de sondeo del gateway (el gateway estaba en buen estado en el momento de la
comprobación), doctor cruza su resultado con la configuración visible para CLI y señala
cualquier discrepancia.

Usa `openclaw memory status --deep` para verificar en tiempo de ejecución la preparación de embeddings.

### 14) Advertencias de estado de canales

Si el gateway está en buen estado, doctor ejecuta un sondeo del estado de canales y muestra
advertencias con correcciones sugeridas.

### 15) Auditoría de configuración del supervisor + reparación

Doctor comprueba que la configuración instalada del supervisor (launchd/systemd/schtasks) no tenga
valores predeterminados faltantes u obsoletos (por ejemplo, dependencias systemd de network-online y
retraso de reinicio). Cuando encuentra una discrepancia, recomienda una actualización y puede
reescribir el archivo de servicio/tarea a los valores predeterminados actuales.

Notas:

- `openclaw doctor` solicita confirmación antes de reescribir la configuración del supervisor.
- `openclaw doctor --yes` acepta las solicitudes de reparación predeterminadas.
- `openclaw doctor --repair` aplica las correcciones recomendadas sin solicitudes.
- `openclaw doctor --repair --force` sobrescribe configuraciones personalizadas del supervisor.
- Si la autenticación por token requiere un token y `gateway.auth.token` se gestiona mediante SecretRef, la instalación/reparación del servicio de doctor valida SecretRef, pero no persiste los valores resueltos de token en texto sin formato en los metadatos del entorno del servicio supervisor.
- Si la autenticación por token requiere un token y el token SecretRef configurado no está resuelto, doctor bloquea la ruta de instalación/reparación con orientación accionable.
- Si tanto `gateway.auth.token` como `gateway.auth.password` están configurados y `gateway.auth.mode` no está establecido, doctor bloquea la instalación/reparación hasta que el modo se configure explícitamente.
- Para unidades user-systemd de Linux, las comprobaciones de deriva de token de doctor ahora incluyen tanto fuentes `Environment=` como `EnvironmentFile=` al comparar metadatos de autenticación del servicio.
- Siempre puedes forzar una reescritura completa mediante `openclaw gateway install --force`.

### 16) Diagnósticos del tiempo de ejecución + puerto del gateway

Doctor inspecciona el tiempo de ejecución del servicio (PID, último estado de salida) y advierte cuando el
servicio está instalado pero en realidad no se está ejecutando. También comprueba colisiones de puerto
en el puerto del gateway (predeterminado `18789`) e informa causas probables (gateway ya
en ejecución, túnel SSH).

### 17) Buenas prácticas del tiempo de ejecución del gateway

Doctor advierte cuando el servicio gateway se ejecuta en Bun o en una ruta de Node gestionada por un gestor de versiones
(`nvm`, `fnm`, `volta`, `asdf`, etc.). Los canales de WhatsApp + Telegram requieren Node,
y las rutas de gestores de versiones pueden fallar después de actualizaciones porque el servicio no
carga la inicialización de tu shell. Doctor ofrece migrar a una instalación de Node del sistema cuando
esté disponible (Homebrew/apt/choco).

### 18) Escritura de configuración + metadatos del asistente

Doctor persiste cualquier cambio de configuración y marca metadatos del asistente para registrar la
ejecución de doctor.

### 19) Consejos del espacio de trabajo (copia de seguridad + sistema de memoria)

Doctor sugiere un sistema de memoria del espacio de trabajo cuando falta y muestra un consejo de copia de seguridad
si el espacio de trabajo aún no está bajo git.

Consulta [/concepts/agent-workspace](/es/concepts/agent-workspace) para obtener una guía completa de la
estructura del espacio de trabajo y la copia de seguridad con git (se recomienda GitHub o GitLab privados).
