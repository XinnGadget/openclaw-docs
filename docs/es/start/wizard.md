---
read_when:
    - Ejecutar o configurar la incorporación por CLI
    - Configurar una máquina nueva
sidebarTitle: 'Onboarding: CLI'
summary: 'Incorporación por CLI: configuración guiada para gateway, espacio de trabajo, canales y Skills'
title: Incorporación (CLI)
x-i18n:
    generated_at: "2026-04-05T10:47:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 81e33fb4f8be30e7c2c6e0024bf9bdcf48583ca58eaf5fff5afd37a1cd628523
    source_path: start/wizard.md
    workflow: 15
---

# Incorporación (CLI)

La incorporación por CLI es la forma **recomendada** de configurar OpenClaw en macOS,
Linux o Windows (mediante WSL2; muy recomendable).
Configura una Gateway local o una conexión a Gateway remota, además de canales, Skills
y valores predeterminados del espacio de trabajo en un único flujo guiado.

```bash
openclaw onboard
```

<Info>
La forma más rápida de tener el primer chat: abre la IU de control (no hace falta configurar ningún canal). Ejecuta
`openclaw dashboard` y chatea en el navegador. Documentación: [Panel](/web/dashboard).
</Info>

Para volver a configurar más adelante:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json` no implica modo no interactivo. Para scripts, usa `--non-interactive`.
</Note>

<Tip>
La incorporación por CLI incluye un paso de búsqueda web en el que puedes elegir un proveedor
como Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG o Tavily. Algunos proveedores requieren una
clave de API, mientras que otros no. También puedes configurarlo más adelante con
`openclaw configure --section web`. Documentación: [Herramientas web](/tools/web).
</Tip>

## QuickStart frente a Avanzado

La incorporación empieza con **QuickStart** (predeterminados) frente a **Avanzado** (control total).

<Tabs>
  <Tab title="QuickStart (predeterminados)">
    - Gateway local (loopback)
    - Espacio de trabajo predeterminado (o espacio de trabajo existente)
    - Puerto de Gateway **18789**
    - Autenticación de Gateway **Token** (generado automáticamente, incluso en loopback)
    - Política de herramientas predeterminada para nuevas configuraciones locales: `tools.profile: "coding"` (se conserva cualquier perfil explícito existente)
    - Aislamiento de mensajes directos predeterminado: la incorporación local escribe `session.dmScope: "per-channel-peer"` cuando no está configurado. Detalles: [Referencia de configuración de CLI](/start/wizard-cli-reference#outputs-and-internals)
    - Exposición mediante Tailscale **Desactivada**
    - Los mensajes directos de Telegram y WhatsApp usan **allowlist** de forma predeterminada (se te pedirá tu número de teléfono)
  </Tab>
  <Tab title="Avanzado (control total)">
    - Expone cada paso (modo, espacio de trabajo, gateway, canales, daemon, Skills).
  </Tab>
</Tabs>

## Lo que configura la incorporación

**Modo local (predeterminado)** te guía por estos pasos:

1. **Modelo/Autenticación** — elige cualquier proveedor admitido o flujo de autenticación (clave de API, OAuth o autenticación manual específica del proveedor), incluido Custom Provider
   (compatible con OpenAI, compatible con Anthropic o Unknown con detección automática). Elige un modelo predeterminado.
   Nota de seguridad: si este agente va a ejecutar herramientas o procesar contenido de webhooks/hooks, prefiere el modelo más sólido de última generación disponible y mantén estricta la política de herramientas. Los niveles más débiles o antiguos son más fáciles de atacar mediante prompt injection.
   Para ejecuciones no interactivas, `--secret-input-mode ref` almacena referencias respaldadas por variables de entorno en los perfiles de autenticación en lugar de valores de claves de API en texto plano.
   En el modo `ref` no interactivo, la variable de entorno del proveedor debe estar configurada; pasar flags de claves en línea sin esa variable de entorno produce un fallo inmediato.
   En ejecuciones interactivas, elegir el modo de referencia secreta te permite apuntar a una variable de entorno o a una referencia de proveedor configurada (`file` o `exec`), con una validación preliminar rápida antes de guardar.
   Para Anthropic, la incorporación/configuración interactiva ofrece **Anthropic Claude CLI** como alternativa local y **Anthropic API key** como ruta de producción recomendada. Anthropic setup-token también vuelve a estar disponible como ruta heredada/manual específica de OpenClaw, con la expectativa de facturación **Extra Usage** específica de OpenClaw de Anthropic.
2. **Espacio de trabajo** — ubicación de los archivos del agente (predeterminada: `~/.openclaw/workspace`). Inicializa los archivos de arranque.
3. **Gateway** — puerto, dirección de enlace, modo de autenticación, exposición mediante Tailscale.
   En el modo interactivo con token, elige el almacenamiento predeterminado en texto plano o usa SecretRef.
   Ruta de SecretRef para token no interactivo: `--gateway-token-ref-env <ENV_VAR>`.
4. **Canales** — canales de chat integrados e incluidos como BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp y más.
5. **Daemon** — instala un LaunchAgent (macOS), una unidad de usuario de systemd (Linux/WSL2) o una tarea programada nativa de Windows con alternativa por usuario en la carpeta Inicio.
   Si la autenticación con token requiere un token y `gateway.auth.token` está gestionado por SecretRef, la instalación del daemon lo valida pero no conserva el token resuelto en los metadatos del entorno del servicio supervisor.
   Si la autenticación con token requiere un token y la SecretRef de token configurada no se puede resolver, la instalación del daemon se bloquea con instrucciones prácticas.
   Si tanto `gateway.auth.token` como `gateway.auth.password` están configurados y `gateway.auth.mode` no está definido, la instalación del daemon se bloquea hasta que el modo se establezca explícitamente.
6. **Comprobación de estado** — inicia la Gateway y verifica que está funcionando.
7. **Skills** — instala las Skills recomendadas y las dependencias opcionales.

<Note>
Volver a ejecutar la incorporación **no** borra nada a menos que elijas explícitamente **Reset** (o pases `--reset`).
CLI `--reset` usa de forma predeterminada configuración, credenciales y sesiones; usa `--reset-scope full` para incluir el espacio de trabajo.
Si la configuración no es válida o contiene claves heredadas, la incorporación te pide que ejecutes primero `openclaw doctor`.
</Note>

El **modo remoto** solo configura el cliente local para conectarse a una Gateway en otro lugar.
**No** instala ni cambia nada en el host remoto.

## Añadir otro agente

Usa `openclaw agents add <name>` para crear un agente independiente con su propio espacio de trabajo,
sesiones y perfiles de autenticación. Ejecutarlo sin `--workspace` inicia la incorporación.

Lo que establece:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Notas:

- Los espacios de trabajo predeterminados siguen el patrón `~/.openclaw/workspace-<agentId>`.
- Añade `bindings` para enrutar mensajes entrantes (la incorporación puede hacerlo).
- Flags no interactivos: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Referencia completa

Para ver desgloses detallados paso a paso y resultados de configuración, consulta
[Referencia de configuración de CLI](/start/wizard-cli-reference).
Para ejemplos no interactivos, consulta [Automatización por CLI](/start/wizard-cli-automation).
Para la referencia técnica más profunda, incluidos los detalles de RPC, consulta
[Referencia de incorporación](/reference/wizard).

## Documentación relacionada

- Referencia de comandos CLI: [`openclaw onboard`](/cli/onboard)
- Descripción general de la incorporación: [Resumen de incorporación](/start/onboarding-overview)
- Incorporación en la app de macOS: [Incorporación](/start/onboarding)
- Ritual de primera ejecución del agente: [Inicialización del agente](/start/bootstrapping)
