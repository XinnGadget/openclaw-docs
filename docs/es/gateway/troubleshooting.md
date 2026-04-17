---
read_when:
    - El centro de solución de problemas te dirigió aquí para un diagnóstico más profundo
    - Necesitas secciones de guía basadas en síntomas y estables, con comandos exactos
summary: Guía detallada de solución de problemas para gateway, canales, automatización, nodos y navegador
title: Solución de problemas
x-i18n:
    generated_at: "2026-04-11T02:44:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7ef2faccba26ede307861504043a6415bc1f12dc64407771106f63ddc5b107f5
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Solución de problemas del gateway

Esta página es la guía detallada.
Empieza en [/help/troubleshooting](/es/help/troubleshooting) si primero quieres el flujo rápido de triaje.

## Escalera de comandos

Ejecuta estos primero, en este orden:

```bash
openclaw status
openclaw gateway status
openclaw logs --follow
openclaw doctor
openclaw channels status --probe
```

Señales esperadas de buen estado:

- `openclaw gateway status` muestra `Runtime: running` y `RPC probe: ok`.
- `openclaw doctor` no informa problemas bloqueantes de configuración/servicio.
- `openclaw channels status --probe` muestra el estado en vivo del transporte por cuenta y,
  donde se admita, resultados de sonda/auditoría como `works` o `audit ok`.

## Anthropic 429 requiere uso adicional para contexto largo

Usa esto cuando los registros/errores incluyan:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

Busca:

- El modelo Opus/Sonnet de Anthropic seleccionado tiene `params.context1m: true`.
- La credencial actual de Anthropic no es apta para el uso de contexto largo.
- Las solicitudes fallan solo en sesiones largas/ejecuciones de modelo que necesitan la ruta beta de 1M.

Opciones para corregir:

1. Desactiva `context1m` para ese modelo para volver a la ventana de contexto normal.
2. Usa una credencial de Anthropic apta para solicitudes de contexto largo, o cambia a una clave de API de Anthropic.
3. Configura modelos de respaldo para que las ejecuciones continúen cuando se rechacen solicitudes de contexto largo de Anthropic.

Relacionado:

- [/providers/anthropic](/es/providers/anthropic)
- [/reference/token-use](/es/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/es/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## Un backend local compatible con OpenAI supera las sondas directas, pero fallan las ejecuciones del agente

Usa esto cuando:

- `curl ... /v1/models` funciona
- funcionan llamadas directas pequeñas a `/v1/chat/completions`
- las ejecuciones de modelo de OpenClaw fallan solo en turnos normales del agente

```bash
curl http://127.0.0.1:1234/v1/models
curl http://127.0.0.1:1234/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"<id>","messages":[{"role":"user","content":"hi"}],"stream":false}'
openclaw infer model run --model <provider/model> --prompt "hi" --json
openclaw logs --follow
```

Busca:

- las llamadas directas pequeñas tienen éxito, pero las ejecuciones de OpenClaw fallan solo con prompts más grandes
- errores del backend sobre `messages[].content` que espera una cadena
- fallos del backend que aparecen solo con recuentos mayores de tokens del prompt o con prompts completos del entorno del agente

Firmas comunes:

- `messages[...].content: invalid type: sequence, expected a string` → el backend
  rechaza partes estructuradas de contenido de Chat Completions. Solución: establece
  `models.providers.<provider>.models[].compat.requiresStringContent: true`.
- las solicitudes directas pequeñas tienen éxito, pero las ejecuciones del agente de OpenClaw fallan con
  fallos del backend/modelo (por ejemplo, Gemma en algunas compilaciones de `inferrs`) → el transporte de OpenClaw
  probablemente ya sea correcto; el backend está fallando con la forma del prompt
  más grande del entorno del agente.
- los fallos disminuyen después de desactivar herramientas, pero no desaparecen → los esquemas de herramientas
  formaban parte de la presión, pero el problema restante sigue siendo una limitación
  del modelo/servidor ascendente o un error del backend.

Opciones para corregir:

1. Establece `compat.requiresStringContent: true` para backends de Chat Completions que solo aceptan cadenas.
2. Establece `compat.supportsTools: false` para modelos/backends que no pueden manejar de forma
   fiable la superficie de esquemas de herramientas de OpenClaw.
3. Reduce la presión del prompt cuando sea posible: arranque de espacio de trabajo más pequeño, historial
   de sesión más corto, modelo local más liviano o un backend con mejor soporte de contexto largo.
4. Si las solicitudes directas pequeñas siguen funcionando mientras los turnos del agente de OpenClaw continúan fallando
   dentro del backend, trátalo como una limitación del servidor/modelo ascendente y presenta
   allí una reproducción con la forma de carga útil aceptada.

Relacionado:

- [/gateway/local-models](/es/gateway/local-models)
- [/gateway/configuration](/es/gateway/configuration)
- [/gateway/configuration-reference#openai-compatible-endpoints](/es/gateway/configuration-reference#openai-compatible-endpoints)

## Sin respuestas

Si los canales están activos pero no responde nada, revisa el enrutamiento y la política antes de volver a conectar nada.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

Busca:

- Emparejamiento pendiente para remitentes de mensajes directos.
- Restricción por mención en grupos (`requireMention`, `mentionPatterns`).
- Desajustes en la lista de permitidos de canal/grupo.

Firmas comunes:

- `drop guild message (mention required` → el mensaje del grupo se ignoró hasta que haya mención.
- `pairing request` → el remitente necesita aprobación.
- `blocked` / `allowlist` → el remitente/canal fue filtrado por la política.

Relacionado:

- [/channels/troubleshooting](/es/channels/troubleshooting)
- [/channels/pairing](/es/channels/pairing)
- [/channels/groups](/es/channels/groups)

## Conectividad de la dashboard/control UI

Cuando la dashboard/control UI no se conecta, valida la URL, el modo de autenticación y las suposiciones de contexto seguro.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

Busca:

- URL de sonda y URL de dashboard correctas.
- Desajuste de modo/token de autenticación entre el cliente y el gateway.
- Uso de HTTP donde se requiere identidad del dispositivo.

Firmas comunes:

- `device identity required` → contexto no seguro o falta autenticación del dispositivo.
- `origin not allowed` → el `Origin` del navegador no está en `gateway.controlUi.allowedOrigins`
  (o te estás conectando desde un origen de navegador que no es loopback sin una
  lista de permitidos explícita).
- `device nonce required` / `device nonce mismatch` → el cliente no está completando el
  flujo de autenticación de dispositivo basado en desafío (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → el cliente firmó la carga útil incorrecta
  (o una marca de tiempo obsoleta) para el handshake actual.
- `AUTH_TOKEN_MISMATCH` con `canRetryWithDeviceToken=true` → el cliente puede hacer un reintento de confianza con el token de dispositivo almacenado en caché.
- Ese reintento con token en caché reutiliza el conjunto de alcances almacenado con el token
  de dispositivo emparejado. Los llamadores con `deviceToken` explícito / `scopes` explícitos mantienen su
  conjunto de alcances solicitado.
- Fuera de esa ruta de reintento, la precedencia de autenticación de conexión es token/contraseña compartidos explícitos
  primero, luego `deviceToken` explícito, luego token de dispositivo almacenado, y
  por último token de arranque.
- En la ruta asíncrona de Control UI de Tailscale Serve, los intentos fallidos para el mismo
  `{scope, ip}` se serializan antes de que el limitador registre el fallo. Por lo tanto, dos malos reintentos
  concurrentes del mismo cliente pueden mostrar `retry later`
  en el segundo intento en lugar de dos desajustes normales.
- `too many failed authentication attempts (retry later)` desde un cliente loopback con origen de navegador
  → los fallos repetidos desde ese mismo `Origin` normalizado quedan bloqueados temporalmente; otro origen localhost usa un bucket separado.
- `repeated unauthorized` después de ese reintento → deriva de token compartido/token de dispositivo; actualiza la configuración del token y vuelve a aprobar/rotar el token del dispositivo si hace falta.
- `gateway connect failed:` → objetivo incorrecto de host/puerto/url.

### Mapa rápido de códigos de detalle de autenticación

Usa `error.details.code` de la respuesta fallida de `connect` para elegir la siguiente acción:

| Código de detalle            | Significado                                             | Acción recomendada                                                                                                                                                                                                                                                                            |
| ---------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`         | El cliente no envió un token compartido requerido.      | Pega/configura el token en el cliente y vuelve a intentarlo. Para rutas de dashboard: `openclaw config get gateway.auth.token` y luego pégalo en la configuración de Control UI.                                                                                                            |
| `AUTH_TOKEN_MISMATCH`        | El token compartido no coincidió con el token del gateway. | Si `canRetryWithDeviceToken=true`, permite un reintento de confianza. Los reintentos con token en caché reutilizan los alcances aprobados almacenados; los llamadores con `deviceToken` / `scopes` explícitos mantienen los alcances solicitados. Si sigue fallando, ejecuta la [lista de verificación para recuperar deriva de token](/cli/devices#token-drift-recovery-checklist). |
| `AUTH_DEVICE_TOKEN_MISMATCH` | El token por dispositivo almacenado en caché está obsoleto o revocado. | Rota/vuelve a aprobar el token del dispositivo con la [CLI de dispositivos](/cli/devices), luego vuelve a conectar.                                                                                                                                                                           |
| `PAIRING_REQUIRED`           | La identidad del dispositivo es conocida, pero no está aprobada para este rol. | Aprueba la solicitud pendiente: `openclaw devices list` y luego `openclaw devices approve <requestId>`.                                                                                                                                                                                       |

Comprobación de migración de autenticación de dispositivo v2:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

Si los registros muestran errores de nonce/firma, actualiza el cliente que se conecta y verifica que:

1. espere a `connect.challenge`
2. firme la carga útil vinculada al desafío
3. envíe `connect.params.device.nonce` con el mismo nonce del desafío

Si `openclaw devices rotate` / `revoke` / `remove` se deniega inesperadamente:

- las sesiones con token de dispositivo emparejado solo pueden administrar **su propio** dispositivo, a menos que el
  llamador también tenga `operator.admin`
- `openclaw devices rotate --scope ...` solo puede solicitar alcances de operador que
  la sesión del llamador ya tenga

Relacionado:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/es/gateway/configuration) (modos de autenticación del gateway)
- [/gateway/trusted-proxy-auth](/es/gateway/trusted-proxy-auth)
- [/gateway/remote](/es/gateway/remote)
- [/cli/devices](/cli/devices)

## El servicio del gateway no se está ejecutando

Usa esto cuando el servicio está instalado pero el proceso no permanece activo.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # también analiza servicios a nivel del sistema
```

Busca:

- `Runtime: stopped` con pistas de salida.
- Desajuste de configuración del servicio (`Config (cli)` frente a `Config (service)`).
- Conflictos de puerto/escucha.
- Instalaciones adicionales de launchd/systemd/schtasks cuando se usa `--deep`.
- Pistas de limpieza de `Other gateway-like services detected (best effort)`.

Firmas comunes:

- `Gateway start blocked: set gateway.mode=local` o `existing config is missing gateway.mode` → el modo de gateway local no está habilitado, o el archivo de configuración fue sobrescrito y perdió `gateway.mode`. Solución: establece `gateway.mode="local"` en tu configuración, o vuelve a ejecutar `openclaw onboard --mode local` / `openclaw setup` para volver a sellar la configuración esperada de modo local. Si ejecutas OpenClaw mediante Podman, la ruta de configuración predeterminada es `~/.openclaw/openclaw.json`.
- `refusing to bind gateway ... without auth` → enlace fuera de loopback sin una ruta válida de autenticación del gateway (token/contraseña, o trusted-proxy donde esté configurado).
- `another gateway instance is already listening` / `EADDRINUSE` → conflicto de puerto.
- `Other gateway-like services detected (best effort)` → existen unidades launchd/systemd/schtasks obsoletas o paralelas. La mayoría de las configuraciones deberían mantener un gateway por máquina; si realmente necesitas más de uno, aísla puertos + configuración/estado/espacio de trabajo. Consulta [/gateway#multiple-gateways-same-host](/es/gateway#multiple-gateways-same-host).

Relacionado:

- [/gateway/background-process](/es/gateway/background-process)
- [/gateway/configuration](/es/gateway/configuration)
- [/gateway/doctor](/es/gateway/doctor)

## Advertencias de sonda del gateway

Usa esto cuando `openclaw gateway probe` llega a algo, pero aun así imprime un bloque de advertencia.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

Busca:

- `warnings[].code` y `primaryTargetId` en la salida JSON.
- Si la advertencia es sobre respaldo por SSH, múltiples gateways, alcances faltantes o referencias de autenticación sin resolver.

Firmas comunes:

- `SSH tunnel failed to start; falling back to direct probes.` → la configuración de SSH falló, pero el comando aun así probó los destinos directos configurados/de loopback.
- `multiple reachable gateways detected` → respondió más de un destino. Por lo general, esto significa una configuración intencional con varios gateways o listeners obsoletos/duplicados.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → la conexión funcionó, pero el RPC de detalle está limitado por alcances; empareja la identidad del dispositivo o usa credenciales con `operator.read`.
- texto de advertencia de SecretRef sin resolver en `gateway.auth.*` / `gateway.remote.*` → el material de autenticación no estaba disponible en esta ruta de comando para el destino fallido.

Relacionado:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/es/gateway#multiple-gateways-same-host)
- [/gateway/remote](/es/gateway/remote)

## El canal está conectado, pero los mensajes no fluyen

Si el estado del canal es conectado pero el flujo de mensajes está muerto, céntrate en la política, los permisos y las reglas de entrega específicas del canal.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

Busca:

- Política de DM (`pairing`, `allowlist`, `open`, `disabled`).
- Lista de permitidos del grupo y requisitos de mención.
- Permisos/alcances de API del canal faltantes.

Firmas comunes:

- `mention required` → el mensaje se ignoró por la política de mención del grupo.
- rastros de `pairing` / aprobación pendiente → el remitente no está aprobado.
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → problema de autenticación/permisos del canal.

Relacionado:

- [/channels/troubleshooting](/es/channels/troubleshooting)
- [/channels/whatsapp](/es/channels/whatsapp)
- [/channels/telegram](/es/channels/telegram)
- [/channels/discord](/es/channels/discord)

## Entrega de cron y heartbeat

Si cron o heartbeat no se ejecutaron o no se entregaron, primero verifica el estado del programador y luego el destino de entrega.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

Busca:

- Cron habilitado y próxima activación presente.
- Estado del historial de ejecuciones del trabajo (`ok`, `skipped`, `error`).
- Motivos de omisión de heartbeat (`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

Firmas comunes:

- `cron: scheduler disabled; jobs will not run automatically` → cron deshabilitado.
- `cron: timer tick failed` → falló el tick del programador; revisa errores de archivo/registro/entorno de ejecución.
- `heartbeat skipped` con `reason=quiet-hours` → fuera de la ventana de horas activas.
- `heartbeat skipped` con `reason=empty-heartbeat-file` → `HEARTBEAT.md` existe, pero solo contiene líneas en blanco / encabezados de Markdown, así que OpenClaw omite la llamada al modelo.
- `heartbeat skipped` con `reason=no-tasks-due` → `HEARTBEAT.md` contiene un bloque `tasks:`, pero ninguna de las tareas vence en este tick.
- `heartbeat: unknown accountId` → id de cuenta no válido para el destino de entrega de heartbeat.
- `heartbeat skipped` con `reason=dm-blocked` → el destino de heartbeat se resolvió a un destino de estilo DM mientras `agents.defaults.heartbeat.directPolicy` (o la anulación por agente) está establecido en `block`.

Relacionado:

- [/automation/cron-jobs#troubleshooting](/es/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/es/automation/cron-jobs)
- [/gateway/heartbeat](/es/gateway/heartbeat)

## Falla una herramienta de nodo emparejado

Si un nodo está emparejado pero fallan las herramientas, aísla el estado de primer plano, permisos y aprobación.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

Busca:

- Nodo en línea con las capacidades esperadas.
- Concesiones de permisos del sistema operativo para cámara/micrófono/ubicación/pantalla.
- Estado de aprobaciones de ejecución y de lista de permitidos.

Firmas comunes:

- `NODE_BACKGROUND_UNAVAILABLE` → la app del nodo debe estar en primer plano.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → falta un permiso del sistema operativo.
- `SYSTEM_RUN_DENIED: approval required` → aprobación de ejecución pendiente.
- `SYSTEM_RUN_DENIED: allowlist miss` → comando bloqueado por la lista de permitidos.

Relacionado:

- [/nodes/troubleshooting](/es/nodes/troubleshooting)
- [/nodes/index](/es/nodes/index)
- [/tools/exec-approvals](/es/tools/exec-approvals)

## Falla la herramienta del navegador

Usa esto cuando fallan las acciones de la herramienta del navegador aunque el propio gateway esté en buen estado.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

Busca:

- Si `plugins.allow` está establecido e incluye `browser`.
- Ruta válida al ejecutable del navegador.
- Alcance del perfil CDP.
- Disponibilidad de Chrome local para perfiles `existing-session` / `user`.

Firmas comunes:

- `unknown command "browser"` o `unknown command 'browser'` → el plugin integrado del navegador está excluido por `plugins.allow`.
- herramienta del navegador faltante / no disponible mientras `browser.enabled=true` → `plugins.allow` excluye `browser`, por lo que el plugin nunca se cargó.
- `Failed to start Chrome CDP on port` → el proceso del navegador no pudo iniciarse.
- `browser.executablePath not found` → la ruta configurada no es válida.
- `browser.cdpUrl must be http(s) or ws(s)` → la URL CDP configurada usa un esquema no compatible como `file:` o `ftp:`.
- `browser.cdpUrl has invalid port` → la URL CDP configurada tiene un puerto incorrecto o fuera de rango.
- `No Chrome tabs found for profile="user"` → el perfil de adjuntar Chrome MCP no tiene pestañas locales de Chrome abiertas.
- `Remote CDP for profile "<name>" is not reachable` → el endpoint remoto de CDP configurado no es accesible desde el host del gateway.
- `Browser attachOnly is enabled ... not reachable` o `Browser attachOnly is enabled and CDP websocket ... is not reachable` → el perfil solo de adjuntar no tiene un destino accesible, o el endpoint HTTP respondió pero aun así no se pudo abrir el WebSocket de CDP.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → la instalación actual del gateway no tiene el paquete completo de Playwright; las instantáneas ARIA y las capturas básicas de página todavía pueden funcionar, pero la navegación, las instantáneas de IA, las capturas de elementos con selector CSS y la exportación a PDF siguen sin estar disponibles.
- `fullPage is not supported for element screenshots` → la solicitud de captura mezcló `--full-page` con `--ref` o `--element`.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → las llamadas de captura de Chrome MCP / `existing-session` deben usar captura de página o un `--ref` de instantánea, no `--element` CSS.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → los hooks de carga de archivos de Chrome MCP necesitan referencias de instantánea, no selectores CSS.
- `existing-session file uploads currently support one file at a time.` → envía una carga por llamada en perfiles de Chrome MCP.
- `existing-session dialog handling does not support timeoutMs.` → los hooks de diálogo en perfiles de Chrome MCP no admiten anulaciones de tiempo de espera.
- `response body is not supported for existing-session profiles yet.` → `responsebody` todavía requiere un navegador administrado o un perfil CDP sin procesar.
- anulaciones obsoletas de viewport / modo oscuro / configuración regional / sin conexión en perfiles attach-only o CDP remotos → ejecuta `openclaw browser stop --browser-profile <name>` para cerrar la sesión de control activa y liberar el estado de emulación de Playwright/CDP sin reiniciar todo el gateway.

Relacionado:

- [/tools/browser-linux-troubleshooting](/es/tools/browser-linux-troubleshooting)
- [/tools/browser](/es/tools/browser)

## Si actualizaste y algo se rompió de repente

La mayoría de las roturas posteriores a una actualización se deben a deriva de configuración o a valores predeterminados más estrictos que ahora se están aplicando.

### 1) Cambió el comportamiento de autenticación y anulación de URL

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

Qué revisar:

- Si `gateway.mode=remote`, las llamadas de CLI pueden estar apuntando al remoto mientras tu servicio local está bien.
- Las llamadas explícitas con `--url` no recurren a las credenciales almacenadas.

Firmas comunes:

- `gateway connect failed:` → destino de URL incorrecto.
- `unauthorized` → endpoint accesible, pero autenticación incorrecta.

### 2) Las protecciones de bind y autenticación son más estrictas

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

Qué revisar:

- Los binds fuera de loopback (`lan`, `tailnet`, `custom`) necesitan una ruta válida de autenticación del gateway: autenticación por token/contraseña compartidos, o una implementación `trusted-proxy` fuera de loopback correctamente configurada.
- Claves antiguas como `gateway.token` no reemplazan `gateway.auth.token`.

Firmas comunes:

- `refusing to bind gateway ... without auth` → bind fuera de loopback sin una ruta válida de autenticación del gateway.
- `RPC probe: failed` mientras el entorno de ejecución está activo → gateway vivo, pero inaccesible con la autenticación/URL actuales.

### 3) Cambió el estado de emparejamiento e identidad del dispositivo

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

Qué revisar:

- Aprobaciones de dispositivos pendientes para dashboard/nodos.
- Aprobaciones de emparejamiento DM pendientes después de cambios de política o identidad.

Firmas comunes:

- `device identity required` → no se cumple la autenticación del dispositivo.
- `pairing required` → el remitente/dispositivo debe aprobarse.

Si la configuración del servicio y el entorno de ejecución siguen sin coincidir después de las comprobaciones, reinstala los metadatos del servicio desde el mismo directorio de perfil/estado:

```bash
openclaw gateway install --force
openclaw gateway restart
```

Relacionado:

- [/gateway/pairing](/es/gateway/pairing)
- [/gateway/authentication](/es/gateway/authentication)
- [/gateway/background-process](/es/gateway/background-process)
