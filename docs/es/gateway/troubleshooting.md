---
read_when:
    - El centro de solución de problemas te remitió aquí para un diagnóstico más profundo
    - Necesitas secciones estables del manual según los síntomas con comandos exactos
summary: Guía detallada de solución de problemas para gateway, canales, automatización, nodos y navegador
title: Solución de problemas
x-i18n:
    generated_at: "2026-04-07T05:03:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0202e8858310a0bfc1c994cd37b01c3b2d6c73c8a74740094e92dc3c4c36729
    source_path: gateway/troubleshooting.md
    workflow: 15
---

# Solución de problemas del Gateway

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
- `openclaw doctor` informa que no hay problemas bloqueantes de configuración/servicio.
- `openclaw channels status --probe` muestra el estado de transporte en vivo por cuenta y,
  cuando es compatible, resultados de sondeo/auditoría como `works` o `audit ok`.

## Anthropic 429: se requiere uso adicional para contexto largo

Úsalo cuando los registros/errores incluyan:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

```bash
openclaw logs --follow
openclaw models status
openclaw config get agents.defaults.models
```

Busca lo siguiente:

- El modelo Anthropic Opus/Sonnet seleccionado tiene `params.context1m: true`.
- La credencial actual de Anthropic no es apta para uso de contexto largo.
- Las solicitudes fallan solo en sesiones largas/ejecuciones de modelo que necesitan la ruta beta de 1M.

Opciones para solucionarlo:

1. Desactiva `context1m` para ese modelo para volver a la ventana de contexto normal.
2. Usa una credencial de Anthropic apta para solicitudes de contexto largo, o cambia a una clave de API de Anthropic.
3. Configura modelos de respaldo para que las ejecuciones continúen cuando se rechacen solicitudes de contexto largo de Anthropic.

Relacionado:

- [/providers/anthropic](/es/providers/anthropic)
- [/reference/token-use](/es/reference/token-use)
- [/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic](/es/help/faq#why-am-i-seeing-http-429-ratelimiterror-from-anthropic)

## Sin respuestas

Si los canales están activos pero no responde nada, comprueba el enrutamiento y la política antes de reconectar nada.

```bash
openclaw status
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw config get channels
openclaw logs --follow
```

Busca lo siguiente:

- Emparejamiento pendiente para remitentes de MD.
- Restricción por mención en grupos (`requireMention`, `mentionPatterns`).
- Desajustes en allowlist de canal/grupo.

Firmas comunes:

- `drop guild message (mention required` → mensaje de grupo ignorado hasta que haya una mención.
- `pairing request` → el remitente necesita aprobación.
- `blocked` / `allowlist` → el remitente/canal fue filtrado por la política.

Relacionado:

- [/channels/troubleshooting](/es/channels/troubleshooting)
- [/channels/pairing](/es/channels/pairing)
- [/channels/groups](/es/channels/groups)

## Conectividad del panel de control UI

Cuando el panel/control UI no se conecta, valida la URL, el modo de autenticación y los supuestos de contexto seguro.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --json
```

Busca lo siguiente:

- URL de sondeo y URL del panel correctas.
- Desajuste de modo de autenticación/token entre el cliente y el gateway.
- Uso de HTTP donde se requiere identidad de dispositivo.

Firmas comunes:

- `device identity required` → contexto no seguro o falta autenticación de dispositivo.
- `origin not allowed` → `Origin` del navegador no está en `gateway.controlUi.allowedOrigins`
  (o te estás conectando desde un origen de navegador no loopback sin una
  allowlist explícita).
- `device nonce required` / `device nonce mismatch` → el cliente no está completando el
  flujo de autenticación de dispositivo basado en desafío (`connect.challenge` + `device.nonce`).
- `device signature invalid` / `device signature expired` → el cliente firmó la carga útil incorrecta
  (o una marca de tiempo obsoleta) para el handshake actual.
- `AUTH_TOKEN_MISMATCH` con `canRetryWithDeviceToken=true` → el cliente puede hacer un reintento de confianza con token de dispositivo en caché.
- Ese reintento con token en caché reutiliza el conjunto de alcances en caché almacenado con el token de dispositivo emparejado. Los llamadores con `deviceToken` explícito / `scopes` explícitos conservan en cambio su conjunto de alcances solicitado.
- Fuera de esa ruta de reintento, la precedencia de autenticación de conexión es primero
  token/contraseña compartidos explícitos, luego `deviceToken` explícito, luego token de dispositivo almacenado,
  y después token de arranque.
- En la ruta asíncrona de Control UI de Tailscale Serve, los intentos fallidos para el mismo
  `{scope, ip}` se serializan antes de que el limitador registre el fallo. Por lo tanto, dos malos reintentos concurrentes del mismo cliente pueden mostrar `retry later`
  en el segundo intento en lugar de dos desajustes simples.
- `too many failed authentication attempts (retry later)` desde un cliente loopback con origen de navegador
  → los fallos repetidos desde ese mismo `Origin` normalizado se bloquean temporalmente; otro origen localhost usa un bucket separado.
- `unauthorized` repetido después de ese reintento → deriva de token compartido/token de dispositivo; actualiza la configuración del token y vuelve a aprobar/rotar el token de dispositivo si hace falta.
- `gateway connect failed:` → objetivo de host/puerto/url incorrecto.

### Mapa rápido de códigos de detalle de autenticación

Usa `error.details.code` de la respuesta fallida de `connect` para elegir la siguiente acción:

| Código de detalle             | Significado                                              | Acción recomendada                                                                                                                                                                                                                                                                           |
| ----------------------------- | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `AUTH_TOKEN_MISSING`          | El cliente no envió un token compartido requerido.       | Pega/configura el token en el cliente y vuelve a intentarlo. Para rutas del panel: `openclaw config get gateway.auth.token` y luego pégalo en la configuración de Control UI.                                                                                                              |
| `AUTH_TOKEN_MISMATCH`         | El token compartido no coincide con el token auth del gateway. | Si `canRetryWithDeviceToken=true`, permite un reintento de confianza. Los reintentos con token en caché reutilizan los alcances aprobados almacenados; los llamadores con `deviceToken` / `scopes` explícitos conservan los alcances solicitados. Si sigue fallando, ejecuta la [lista de recuperación por deriva de token](/cli/devices#token-drift-recovery-checklist). |
| `AUTH_DEVICE_TOKEN_MISMATCH`  | El token por dispositivo en caché está obsoleto o revocado. | Rota/vuelve a aprobar el token de dispositivo usando [CLI de dispositivos](/cli/devices), luego vuelve a conectarte.                                                                                                                                                                       |
| `PAIRING_REQUIRED`            | La identidad del dispositivo se conoce, pero no está aprobada para este rol. | Aprueba la solicitud pendiente: `openclaw devices list` y luego `openclaw devices approve <requestId>`.                                                                                                                                                                                   |

Comprobación de migración a autenticación de dispositivo v2:

```bash
openclaw --version
openclaw doctor
openclaw gateway status
```

Si los registros muestran errores de nonce/firma, actualiza el cliente que se conecta y verifica que:

1. espera a `connect.challenge`
2. firma la carga útil vinculada al desafío
3. envía `connect.params.device.nonce` con el mismo nonce del desafío

Si `openclaw devices rotate` / `revoke` / `remove` se deniega inesperadamente:

- las sesiones de token de dispositivo emparejado solo pueden gestionar **su propio** dispositivo, a menos que el llamador también tenga `operator.admin`
- `openclaw devices rotate --scope ...` solo puede solicitar alcances de operador que
  la sesión llamadora ya tenga

Relacionado:

- [/web/control-ui](/web/control-ui)
- [/gateway/configuration](/es/gateway/configuration) (modos de autenticación del gateway)
- [/gateway/trusted-proxy-auth](/es/gateway/trusted-proxy-auth)
- [/gateway/remote](/es/gateway/remote)
- [/cli/devices](/cli/devices)

## El servicio Gateway no se está ejecutando

Úsalo cuando el servicio está instalado pero el proceso no permanece activo.

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
openclaw doctor
openclaw gateway status --deep   # también examina servicios a nivel del sistema
```

Busca lo siguiente:

- `Runtime: stopped` con pistas de salida.
- Desajuste de configuración del servicio (`Config (cli)` frente a `Config (service)`).
- Conflictos de puerto/listener.
- Instalaciones adicionales de launchd/systemd/schtasks cuando se usa `--deep`.
- Pistas de limpieza de `Other gateway-like services detected (best effort)`.

Firmas comunes:

- `Gateway start blocked: set gateway.mode=local` o `existing config is missing gateway.mode` → el modo de gateway local no está habilitado, o el archivo de configuración fue sobrescrito y perdió `gateway.mode`. Solución: configura `gateway.mode="local"` en tu configuración, o vuelve a ejecutar `openclaw onboard --mode local` / `openclaw setup` para volver a aplicar la configuración esperada de modo local. Si ejecutas OpenClaw mediante Podman, la ruta de configuración predeterminada es `~/.openclaw/openclaw.json`.
- `refusing to bind gateway ... without auth` → enlace no loopback sin una ruta válida de autenticación del gateway (token/contraseña, o trusted-proxy donde esté configurado).
- `another gateway instance is already listening` / `EADDRINUSE` → conflicto de puerto.
- `Other gateway-like services detected (best effort)` → existen unidades launchd/systemd/schtasks obsoletas o paralelas. La mayoría de configuraciones deberían mantener un gateway por máquina; si realmente necesitas más de uno, aísla puertos + configuración/estado/espacio de trabajo. Consulta [/gateway#multiple-gateways-same-host](/es/gateway#multiple-gateways-same-host).

Relacionado:

- [/gateway/background-process](/es/gateway/background-process)
- [/gateway/configuration](/es/gateway/configuration)
- [/gateway/doctor](/es/gateway/doctor)

## Advertencias del sondeo del Gateway

Úsalo cuando `openclaw gateway probe` llega a algo, pero aun así imprime un bloque de advertencia.

```bash
openclaw gateway probe
openclaw gateway probe --json
openclaw gateway probe --ssh user@gateway-host
```

Busca lo siguiente:

- `warnings[].code` y `primaryTargetId` en la salida JSON.
- Si la advertencia trata sobre respaldo por SSH, múltiples gateways, alcances faltantes o referencias de autenticación no resueltas.

Firmas comunes:

- `SSH tunnel failed to start; falling back to direct probes.` → la configuración de SSH falló, pero el comando aun así probó objetivos configurados/directos de loopback.
- `multiple reachable gateways detected` → respondió más de un objetivo. Normalmente esto significa una configuración intencionada de varios gateways o listeners obsoletos/duplicados.
- `Probe diagnostics are limited by gateway scopes (missing operator.read)` → la conexión funcionó, pero el RPC de detalle está limitado por alcances; empareja la identidad del dispositivo o usa credenciales con `operator.read`.
- texto de advertencia no resuelta de SecretRef `gateway.auth.*` / `gateway.remote.*` → el material de autenticación no estaba disponible en esta ruta de comando para el objetivo fallido.

Relacionado:

- [/cli/gateway](/cli/gateway)
- [/gateway#multiple-gateways-same-host](/es/gateway#multiple-gateways-same-host)
- [/gateway/remote](/es/gateway/remote)

## Canal conectado pero los mensajes no fluyen

Si el estado del canal es conectado pero el flujo de mensajes está muerto, céntrate en la política, los permisos y las reglas de entrega específicas del canal.

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel> [--account <id>]
openclaw status --deep
openclaw logs --follow
openclaw config get channels
```

Busca lo siguiente:

- Política de MD (`pairing`, `allowlist`, `open`, `disabled`).
- Allowlist de grupo y requisitos de mención.
- Permisos/alcances de API del canal ausentes.

Firmas comunes:

- `mention required` → mensaje ignorado por la política de mención en grupo.
- `pairing` / trazas de aprobación pendiente → el remitente no está aprobado.
- `missing_scope`, `not_in_channel`, `Forbidden`, `401/403` → problema de autenticación/permisos del canal.

Relacionado:

- [/channels/troubleshooting](/es/channels/troubleshooting)
- [/channels/whatsapp](/es/channels/whatsapp)
- [/channels/telegram](/es/channels/telegram)
- [/channels/discord](/es/channels/discord)

## Entrega de cron y heartbeat

Si cron o heartbeat no se ejecutaron o no se entregaron, verifica primero el estado del planificador y luego el objetivo de entrega.

```bash
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
```

Busca lo siguiente:

- Cron habilitado y siguiente activación presente.
- Estado del historial de ejecución de trabajos (`ok`, `skipped`, `error`).
- Motivos de omisión de heartbeat (`quiet-hours`, `requests-in-flight`, `alerts-disabled`, `empty-heartbeat-file`, `no-tasks-due`).

Firmas comunes:

- `cron: scheduler disabled; jobs will not run automatically` → cron deshabilitado.
- `cron: timer tick failed` → falló el tick del planificador; revisa errores de archivos/registros/entorno de ejecución.
- `heartbeat skipped` con `reason=quiet-hours` → fuera de la ventana de horas activas.
- `heartbeat skipped` con `reason=empty-heartbeat-file` → `HEARTBEAT.md` existe pero solo contiene líneas en blanco / encabezados Markdown, por lo que OpenClaw omite la llamada al modelo.
- `heartbeat skipped` con `reason=no-tasks-due` → `HEARTBEAT.md` contiene un bloque `tasks:`, pero ninguna de las tareas vence en este tick.
- `heartbeat: unknown accountId` → id de cuenta no válido para el objetivo de entrega del heartbeat.
- `heartbeat skipped` con `reason=dm-blocked` → el objetivo de heartbeat se resolvió como un destino de estilo MD mientras `agents.defaults.heartbeat.directPolicy` (o la anulación por agente) está configurado como `block`.

Relacionado:

- [/automation/cron-jobs#troubleshooting](/es/automation/cron-jobs#troubleshooting)
- [/automation/cron-jobs](/es/automation/cron-jobs)
- [/gateway/heartbeat](/es/gateway/heartbeat)

## Falla la herramienta de nodo emparejado

Si un nodo está emparejado pero las herramientas fallan, aísla el estado de primer plano, permisos y aprobación.

```bash
openclaw nodes status
openclaw nodes describe --node <idOrNameOrIp>
openclaw approvals get --node <idOrNameOrIp>
openclaw logs --follow
openclaw status
```

Busca lo siguiente:

- Nodo en línea con las capacidades esperadas.
- Concesiones de permisos del SO para cámara/micrófono/ubicación/pantalla.
- Estado de aprobaciones de exec y allowlist.

Firmas comunes:

- `NODE_BACKGROUND_UNAVAILABLE` → la app del nodo debe estar en primer plano.
- `*_PERMISSION_REQUIRED` / `LOCATION_PERMISSION_REQUIRED` → falta un permiso del SO.
- `SYSTEM_RUN_DENIED: approval required` → aprobación de exec pendiente.
- `SYSTEM_RUN_DENIED: allowlist miss` → comando bloqueado por la allowlist.

Relacionado:

- [/nodes/troubleshooting](/es/nodes/troubleshooting)
- [/nodes/index](/es/nodes/index)
- [/tools/exec-approvals](/es/tools/exec-approvals)

## Falla la herramienta de navegador

Úsalo cuando las acciones de la herramienta de navegador fallen aunque el gateway en sí esté en buen estado.

```bash
openclaw browser status
openclaw browser start --browser-profile openclaw
openclaw browser profiles
openclaw logs --follow
openclaw doctor
```

Busca lo siguiente:

- Si `plugins.allow` está configurado e incluye `browser`.
- Ruta válida al ejecutable del navegador.
- Alcanzabilidad del perfil CDP.
- Disponibilidad de Chrome local para perfiles `existing-session` / `user`.

Firmas comunes:

- `unknown command "browser"` o `unknown command 'browser'` → el plugin integrado de navegador está excluido por `plugins.allow`.
- herramienta de navegador ausente / no disponible mientras `browser.enabled=true` → `plugins.allow` excluye `browser`, así que el plugin nunca se cargó.
- `Failed to start Chrome CDP on port` → el proceso del navegador no pudo iniciarse.
- `browser.executablePath not found` → la ruta configurada no es válida.
- `browser.cdpUrl must be http(s) or ws(s)` → la URL de CDP configurada usa un esquema no compatible como `file:` o `ftp:`.
- `browser.cdpUrl has invalid port` → la URL de CDP configurada tiene un puerto incorrecto o fuera de rango.
- `No Chrome tabs found for profile="user"` → el perfil de adjuntar Chrome MCP no tiene pestañas locales de Chrome abiertas.
- `Remote CDP for profile "<name>" is not reachable` → el endpoint remoto de CDP configurado no es alcanzable desde el host del gateway.
- `Browser attachOnly is enabled ... not reachable` o `Browser attachOnly is enabled and CDP websocket ... is not reachable` → el perfil solo de adjuntar no tiene un objetivo alcanzable, o el endpoint HTTP respondió pero aun así no se pudo abrir el WebSocket CDP.
- `Playwright is not available in this gateway build; '<feature>' is unsupported.` → la instalación actual del gateway no tiene el paquete completo de Playwright; las instantáneas ARIA y las capturas básicas de página todavía pueden funcionar, pero la navegación, las instantáneas de IA, las capturas de elementos por selector CSS y la exportación a PDF seguirán sin estar disponibles.
- `fullPage is not supported for element screenshots` → la solicitud de captura mezcló `--full-page` con `--ref` o `--element`.
- `element screenshots are not supported for existing-session profiles; use ref from snapshot.` → las llamadas de captura de Chrome MCP / `existing-session` deben usar captura de página o un `--ref` de instantánea, no `--element` CSS.
- `existing-session file uploads do not support element selectors; use ref/inputRef.` → los hooks de carga de archivos de Chrome MCP necesitan referencias de instantánea, no selectores CSS.
- `existing-session file uploads currently support one file at a time.` → envía una carga por llamada en perfiles Chrome MCP.
- `existing-session dialog handling does not support timeoutMs.` → los hooks de diálogo en perfiles Chrome MCP no admiten anulación de timeout.
- `response body is not supported for existing-session profiles yet.` → `responsebody` todavía requiere un navegador gestionado o un perfil CDP sin procesar.
- anulaciones obsoletas de viewport / modo oscuro / configuración regional / modo sin conexión en perfiles solo de adjuntar o CDP remoto → ejecuta `openclaw browser stop --browser-profile <name>` para cerrar la sesión de control activa y liberar el estado de emulación de Playwright/CDP sin reiniciar todo el gateway.

Relacionado:

- [/tools/browser-linux-troubleshooting](/es/tools/browser-linux-troubleshooting)
- [/tools/browser](/es/tools/browser)

## Si actualizaste y algo se rompió de repente

La mayoría de los fallos tras una actualización se deben a deriva de configuración o a que ahora se aplican valores predeterminados más estrictos.

### 1) Cambió el comportamiento de autenticación y anulación de URL

```bash
openclaw gateway status
openclaw config get gateway.mode
openclaw config get gateway.remote.url
openclaw config get gateway.auth.mode
```

Qué comprobar:

- Si `gateway.mode=remote`, es posible que las llamadas de CLI estén apuntando a remoto mientras tu servicio local está bien.
- Las llamadas explícitas con `--url` no recurren a credenciales almacenadas.

Firmas comunes:

- `gateway connect failed:` → objetivo URL incorrecto.
- `unauthorized` → endpoint alcanzable pero autenticación incorrecta.

### 2) Las protecciones de enlace y autenticación son más estrictas

```bash
openclaw config get gateway.bind
openclaw config get gateway.auth.mode
openclaw config get gateway.auth.token
openclaw gateway status
openclaw logs --follow
```

Qué comprobar:

- Los enlaces no loopback (`lan`, `tailnet`, `custom`) necesitan una ruta válida de autenticación del gateway: autenticación con token/contraseña compartidos, o un despliegue `trusted-proxy` no loopback configurado correctamente.
- Claves antiguas como `gateway.token` no sustituyen a `gateway.auth.token`.

Firmas comunes:

- `refusing to bind gateway ... without auth` → enlace no loopback sin una ruta válida de autenticación del gateway.
- `RPC probe: failed` mientras el entorno de ejecución está activo → gateway vivo pero inaccesible con la autenticación/url actual.

### 3) Cambió el estado de emparejamiento e identidad de dispositivo

```bash
openclaw devices list
openclaw pairing list --channel <channel> [--account <id>]
openclaw logs --follow
openclaw doctor
```

Qué comprobar:

- Aprobaciones de dispositivos pendientes para panel/nodos.
- Aprobaciones de emparejamiento de MD pendientes tras cambios de política o identidad.

Firmas comunes:

- `device identity required` → no se cumple la autenticación de dispositivo.
- `pairing required` → el remitente/dispositivo debe estar aprobado.

Si la configuración del servicio y el entorno de ejecución siguen sin coincidir después de las comprobaciones, reinstala los metadatos del servicio desde el mismo directorio de perfil/estado:

```bash
openclaw gateway install --force
openclaw gateway restart
```

Relacionado:

- [/gateway/pairing](/es/gateway/pairing)
- [/gateway/authentication](/es/gateway/authentication)
- [/gateway/background-process](/es/gateway/background-process)
