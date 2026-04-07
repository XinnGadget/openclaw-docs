---
read_when:
    - Ejecutando o depurando el proceso de gateway
summary: Runbook para el servicio Gateway, su ciclo de vida y operaciones
title: Runbook de Gateway
x-i18n:
    generated_at: "2026-04-07T05:02:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: fd2c21036e88612861ef2195b8ff7205aca31386bb11558614ade8d1a54fdebd
    source_path: gateway/index.md
    workflow: 15
---

# Runbook de Gateway

Usa esta página para el arranque del día 1 y las operaciones del día 2 del servicio Gateway.

<CardGroup cols={2}>
  <Card title="Solución de problemas en profundidad" icon="siren" href="/es/gateway/troubleshooting">
    Diagnósticos orientados por síntomas con secuencias exactas de comandos y firmas de registro.
  </Card>
  <Card title="Configuración" icon="sliders" href="/es/gateway/configuration">
    Guía de configuración orientada a tareas + referencia completa de configuración.
  </Card>
  <Card title="Gestión de secretos" icon="key-round" href="/es/gateway/secrets">
    Contrato de SecretRef, comportamiento de instantáneas en tiempo de ejecución y operaciones de migración/recarga.
  </Card>
  <Card title="Contrato del plan de secretos" icon="shield-check" href="/es/gateway/secrets-plan-contract">
    Reglas exactas de destino/ruta de `secrets apply` y comportamiento de perfiles de autenticación solo con referencias.
  </Card>
</CardGroup>

## Inicio local en 5 minutos

<Steps>
  <Step title="Iniciar Gateway">

```bash
openclaw gateway --port 18789
# debug/trace reflejado en stdio
openclaw gateway --port 18789 --verbose
# fuerza la finalización del listener en el puerto seleccionado y luego inicia
openclaw gateway --force
```

  </Step>

  <Step title="Verificar el estado del servicio">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

Referencia de estado saludable: `Runtime: running` y `RPC probe: ok`.

  </Step>

  <Step title="Validar la preparación del canal">

```bash
openclaw channels status --probe
```

Con un gateway accesible, esto ejecuta sondeos en vivo por cuenta del canal y auditorías opcionales.
Si el gateway no es accesible, la CLI recurre a resúmenes del canal basados solo en la configuración
en lugar de mostrar la salida de sondeo en vivo.

  </Step>
</Steps>

<Note>
La recarga de configuración de Gateway observa la ruta activa del archivo de configuración (resuelta a partir de los valores predeterminados del perfil/estado, o `OPENCLAW_CONFIG_PATH` cuando está establecido).
El modo predeterminado es `gateway.reload.mode="hybrid"`.
Después de la primera carga correcta, el proceso en ejecución sirve la instantánea activa de configuración en memoria; una recarga correcta intercambia esa instantánea de forma atómica.
</Note>

## Modelo de tiempo de ejecución

- Un proceso siempre activo para el enrutamiento, el plano de control y las conexiones de canal.
- Un único puerto multiplexado para:
  - control/RPC por WebSocket
  - APIs HTTP, compatibles con OpenAI (`/v1/models`, `/v1/embeddings`, `/v1/chat/completions`, `/v1/responses`, `/tools/invoke`)
  - Control UI y hooks
- Modo de enlace predeterminado: `loopback`.
- La autenticación es obligatoria de forma predeterminada. Las configuraciones con secreto compartido usan
  `gateway.auth.token` / `gateway.auth.password` (o
  `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`), y las configuraciones
  con proxy inverso sin loopback pueden usar `gateway.auth.mode: "trusted-proxy"`.

## Endpoints compatibles con OpenAI

La superficie de compatibilidad de mayor impacto de OpenClaw ahora es:

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

Por qué este conjunto importa:

- La mayoría de las integraciones de Open WebUI, LobeChat y LibreChat sondean primero `/v1/models`.
- Muchos flujos de RAG y de memoria esperan `/v1/embeddings`.
- Los clientes nativos de agentes prefieren cada vez más `/v1/responses`.

Nota de planificación:

- `/v1/models` está orientado a agentes: devuelve `openclaw`, `openclaw/default` y `openclaw/<agentId>`.
- `openclaw/default` es el alias estable que siempre se asigna al agente predeterminado configurado.
- Usa `x-openclaw-model` cuando quieras una anulación de proveedor/modelo de backend; en caso contrario, el modelo normal y la configuración de embeddings del agente seleccionado siguen teniendo el control.

Todo esto se ejecuta en el puerto principal de Gateway y usa el mismo límite de autenticación de operador confiable que el resto de la API HTTP de Gateway.

### Precedencia de puerto y enlace

| Configuración   | Orden de resolución                                            |
| --------------- | -------------------------------------------------------------- |
| Puerto Gateway  | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| Modo de enlace  | CLI/override → `gateway.bind` → `loopback`                    |

### Modos de recarga en caliente

| `gateway.reload.mode` | Comportamiento                              |
| --------------------- | ------------------------------------------- |
| `off`                 | Sin recarga de configuración                |
| `hot`                 | Aplicar solo cambios seguros en caliente    |
| `restart`             | Reiniciar en cambios que requieran recarga  |
| `hybrid` (default)    | Aplicar en caliente cuando sea seguro, reiniciar cuando sea necesario |

## Conjunto de comandos del operador

```bash
openclaw gateway status
openclaw gateway status --deep   # agrega un análisis del servicio a nivel del sistema
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

`gateway status --deep` es para descubrimiento adicional de servicios (LaunchDaemons/unidades systemd del sistema
/schtasks), no para un sondeo de estado RPC más profundo.

## Varios gateways (mismo host)

La mayoría de las instalaciones deben ejecutar un gateway por máquina. Un solo gateway puede alojar varios
agentes y canales.

Solo necesitas varios gateways cuando deseas intencionalmente aislamiento o un bot de rescate.

Comprobaciones útiles:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

Qué esperar:

- `gateway status --deep` puede informar `Other gateway-like services detected (best effort)`
  e imprimir sugerencias de limpieza cuando aún hay instalaciones obsoletas de launchd/systemd/schtasks.
- `gateway probe` puede advertir sobre `multiple reachable gateways` cuando responde más de un destino.
- Si eso es intencional, aísla puertos, configuración/estado y raíces del espacio de trabajo por gateway.

Configuración detallada: [/gateway/multiple-gateways](/es/gateway/multiple-gateways).

## Acceso remoto

Preferido: Tailscale/VPN.
Alternativa: túnel SSH.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

Luego conecta los clientes localmente a `ws://127.0.0.1:18789`.

<Warning>
Los túneles SSH no omiten la autenticación de gateway. Para autenticación con secreto compartido, los clientes aún
deben enviar `token`/`password` incluso a través del túnel. Para los modos con identidad,
la solicitud aún tiene que satisfacer esa ruta de autenticación.
</Warning>

Ver: [Gateway remoto](/es/gateway/remote), [Autenticación](/es/gateway/authentication), [Tailscale](/es/gateway/tailscale).

## Supervisión y ciclo de vida del servicio

Usa ejecuciones supervisadas para una confiabilidad similar a producción.

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

Las etiquetas de LaunchAgent son `ai.openclaw.gateway` (predeterminada) o `ai.openclaw.<profile>` (perfil con nombre). `openclaw doctor` audita y repara desviaciones de configuración del servicio.

  </Tab>

  <Tab title="Linux (systemd de usuario)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

Para persistencia después del cierre de sesión, habilita lingering:

```bash
sudo loginctl enable-linger <user>
```

Ejemplo manual de unidad de usuario cuando necesitas una ruta de instalación personalizada:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

  </Tab>

  <Tab title="Windows (nativo)">

```powershell
openclaw gateway install
openclaw gateway status --json
openclaw gateway restart
openclaw gateway stop
```

El inicio administrado nativo de Windows usa una tarea programada llamada `OpenClaw Gateway`
(o `OpenClaw Gateway (<profile>)` para perfiles con nombre). Si se deniega la creación de la tarea programada,
OpenClaw recurre a un iniciador por usuario en la carpeta de Inicio
que apunta a `gateway.cmd` dentro del directorio de estado.

  </Tab>

  <Tab title="Linux (servicio del sistema)">

Usa una unidad del sistema para hosts multiusuario o siempre activos.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

Usa el mismo cuerpo de servicio que la unidad de usuario, pero instálalo en
`/etc/systemd/system/openclaw-gateway[-<profile>].service` y ajusta
`ExecStart=` si tu binario `openclaw` está en otra ubicación.

  </Tab>
</Tabs>

## Varios gateways en un host

La mayoría de las configuraciones deben ejecutar **un** Gateway.
Usa varios solo para aislamiento o redundancia estrictos (por ejemplo, un perfil de rescate).

Lista de verificación por instancia:

- `gateway.port` único
- `OPENCLAW_CONFIG_PATH` único
- `OPENCLAW_STATE_DIR` único
- `agents.defaults.workspace` único

Ejemplo:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

Ver: [Varios gateways](/es/gateway/multiple-gateways).

### Ruta rápida del perfil de desarrollo

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

Los valores predeterminados incluyen estado/configuración aislados y el puerto base de gateway `19001`.

## Referencia rápida del protocolo (vista del operador)

- La primera trama del cliente debe ser `connect`.
- Gateway devuelve la instantánea `hello-ok` (`presence`, `health`, `stateVersion`, `uptimeMs`, limits/policy).
- `hello-ok.features.methods` / `events` son una lista de descubrimiento conservadora, no
  un volcado generado de cada ruta auxiliar invocable.
- Solicitudes: `req(method, params)` → `res(ok/payload|error)`.
- Los eventos comunes incluyen `connect.challenge`, `agent`, `chat`,
  `session.message`, `session.tool`, `sessions.changed`, `presence`, `tick`,
  `health`, `heartbeat`, eventos del ciclo de vida de vinculación/aprobación y `shutdown`.

Las ejecuciones del agente tienen dos etapas:

1. Acuse inmediato de aceptación (`status:"accepted"`)
2. Respuesta final de finalización (`status:"ok"|"error"`), con eventos `agent` transmitidos entre medias.

Consulta la documentación completa del protocolo: [Protocolo de Gateway](/es/gateway/protocol).

## Comprobaciones operativas

### Disponibilidad

- Abre WS y envía `connect`.
- Espera una respuesta `hello-ok` con instantánea.

### Preparación

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### Recuperación ante huecos

Los eventos no se vuelven a reproducir. En huecos de secuencia, actualiza el estado (`health`, `system-presence`) antes de continuar.

## Firmas comunes de fallo

| Firma                                                         | Problema probable                                                                 |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `refusing to bind gateway ... without auth`                   | Enlace sin loopback sin una ruta válida de autenticación de gateway               |
| `another gateway instance is already listening` / `EADDRINUSE` | Conflicto de puerto                                                               |
| `Gateway start blocked: set gateway.mode=local`               | La configuración está en modo remoto, o falta la marca de modo local en una configuración dañada |
| `unauthorized` during connect                                 | Incompatibilidad de autenticación entre cliente y gateway                         |

Para secuencias completas de diagnóstico, usa [Solución de problemas de Gateway](/es/gateway/troubleshooting).

## Garantías de seguridad

- Los clientes del protocolo Gateway fallan rápidamente cuando Gateway no está disponible (sin alternativa implícita a canal directo).
- Las primeras tramas inválidas o distintas de `connect` se rechazan y se cierran.
- El apagado ordenado emite el evento `shutdown` antes del cierre del socket.

---

Relacionado:

- [Solución de problemas](/es/gateway/troubleshooting)
- [Proceso en segundo plano](/es/gateway/background-process)
- [Configuración](/es/gateway/configuration)
- [Estado](/es/gateway/health)
- [Doctor](/es/gateway/doctor)
- [Autenticación](/es/gateway/authentication)
