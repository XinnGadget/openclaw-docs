---
read_when:
    - Ejecutando o configurando la incorporación en la CLI
    - Configurando una máquina nueva
sidebarTitle: 'Onboarding: CLI'
summary: 'Incorporación en la CLI: configuración guiada para gateway, workspace, canales y Skills'
title: Incorporación (CLI)
x-i18n:
    generated_at: "2026-04-07T05:06:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6773b07afa8babf1b5ac94d857063d08094a962ee21ec96ca966e99ad57d107d
    source_path: start/wizard.md
    workflow: 15
---

# Incorporación (CLI)

La incorporación en la CLI es la forma **recomendada** de configurar OpenClaw en macOS,
Linux o Windows (mediante WSL2; muy recomendable).
Configura un Gateway local o una conexión a un Gateway remoto, además de canales, Skills
y valores predeterminados del workspace en un único flujo guiado.

```bash
openclaw onboard
```

<Info>
La forma más rápida de iniciar el primer chat: abre la Control UI (no se necesita configurar ningún canal). Ejecuta
`openclaw dashboard` y chatea en el navegador. Documentación: [Dashboard](/web/dashboard).
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
La incorporación en la CLI incluye un paso de búsqueda web donde puedes elegir un proveedor
como Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG o Tavily. Algunos proveedores requieren una
API key, mientras que otros no. También puedes configurarlo más adelante con
`openclaw configure --section web`. Documentación: [Herramientas web](/es/tools/web).
</Tip>

## QuickStart frente a Advanced

La incorporación comienza con **QuickStart** (valores predeterminados) frente a **Advanced** (control total).

<Tabs>
  <Tab title="QuickStart (valores predeterminados)">
    - Gateway local (`loopback`)
    - Workspace predeterminado (o workspace existente)
    - Puerto de Gateway **18789**
    - Autenticación de Gateway **Token** (generado automáticamente, incluso en loopback)
    - Política de herramientas predeterminada para nuevas configuraciones locales: `tools.profile: "coding"` (se conserva cualquier perfil explícito existente)
    - Aislamiento de mensajes directos predeterminado: la incorporación local escribe `session.dmScope: "per-channel-peer"` cuando no está establecido. Detalles: [Referencia de configuración de CLI](/es/start/wizard-cli-reference#outputs-and-internals)
    - Exposición con Tailscale **Desactivada**
    - Los mensajes directos de Telegram + WhatsApp usan **allowlist** de forma predeterminada (se te pedirá tu número de teléfono)
  </Tab>
  <Tab title="Advanced (control total)">
    - Expone cada paso (modo, workspace, gateway, canales, daemon, Skills).
  </Tab>
</Tabs>

## Qué configura la incorporación

**Modo local (predeterminado)** te guía por estos pasos:

1. **Modelo/Autenticación** — elige cualquier flujo de proveedor/autenticación compatible (API key, OAuth o autenticación manual específica del proveedor), incluido Proveedor personalizado
   (compatible con OpenAI, compatible con Anthropic o detección automática Unknown). Elige un modelo predeterminado.
   Nota de seguridad: si este agente va a ejecutar herramientas o procesar contenido de webhook/hooks, prefiere el modelo más fuerte de última generación disponible y mantén estricta la política de herramientas. Las versiones más débiles o antiguas son más fáciles de atacar con prompt injection.
   Para ejecuciones no interactivas, `--secret-input-mode ref` almacena referencias respaldadas por variables de entorno en perfiles de autenticación en lugar de valores de API key en texto plano.
   En modo no interactivo `ref`, la variable de entorno del proveedor debe estar establecida; pasar flags de clave en línea sin esa variable de entorno provoca un fallo inmediato.
   En ejecuciones interactivas, elegir el modo de referencia secreta te permite apuntar a una variable de entorno o a una referencia de proveedor configurada (`file` o `exec`), con una validación previa rápida antes de guardar.
   Para Anthropic, la incorporación/configuración interactiva ofrece **Anthropic Claude CLI** como la ruta local preferida y **Anthropic API key** como la ruta de producción recomendada. Anthropic setup-token también sigue disponible como ruta compatible de autenticación por token.
2. **Workspace** — ubicación para los archivos del agente (predeterminado `~/.openclaw/workspace`). Inicializa archivos de arranque.
3. **Gateway** — puerto, dirección de enlace, modo de autenticación, exposición con Tailscale.
   En modo interactivo con token, elige entre el almacenamiento predeterminado del token en texto plano o activar SecretRef.
   Ruta no interactiva de SecretRef para token: `--gateway-token-ref-env <ENV_VAR>`.
4. **Canales** — canales de chat integrados y empaquetados como BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp y más.
5. **Daemon** — instala un LaunchAgent (macOS), una unidad de usuario systemd (Linux/WSL2) o una Scheduled Task nativa de Windows con alternativa por usuario en la carpeta de Inicio.
   Si la autenticación por token requiere un token y `gateway.auth.token` está gestionado por SecretRef, la instalación del daemon lo valida pero no conserva el token resuelto en los metadatos de entorno del servicio supervisor.
   Si la autenticación por token requiere un token y la referencia SecretRef configurada para el token no se resuelve, se bloquea la instalación del daemon con orientación práctica.
   Si están configurados tanto `gateway.auth.token` como `gateway.auth.password` y `gateway.auth.mode` no está establecido, la instalación del daemon se bloquea hasta que el modo se establezca explícitamente.
6. **Comprobación de estado** — inicia Gateway y verifica que esté en ejecución.
7. **Skills** — instala las Skills recomendadas y las dependencias opcionales.

<Note>
Volver a ejecutar la incorporación **no** borra nada a menos que elijas explícitamente **Reset** (o pases `--reset`).
CLI `--reset` usa por defecto configuración, credenciales y sesiones; usa `--reset-scope full` para incluir el workspace.
Si la configuración no es válida o contiene claves heredadas, la incorporación te pide que ejecutes primero `openclaw doctor`.
</Note>

**Modo remoto** solo configura el cliente local para conectarse a un Gateway que está en otro lugar.
**No** instala ni cambia nada en el host remoto.

## Agregar otro agente

Usa `openclaw agents add <name>` para crear un agente separado con su propio workspace,
sesiones y perfiles de autenticación. Ejecutarlo sin `--workspace` inicia la incorporación.

Lo que establece:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Notas:

- Los workspaces predeterminados siguen el patrón `~/.openclaw/workspace-<agentId>`.
- Agrega `bindings` para enrutar mensajes entrantes (la incorporación puede hacerlo).
- Flags no interactivos: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Referencia completa

Para desgloses detallados paso a paso y salidas de configuración, consulta
[Referencia de configuración de CLI](/es/start/wizard-cli-reference).
Para ejemplos no interactivos, consulta [Automatización de CLI](/es/start/wizard-cli-automation).
Para la referencia técnica más profunda, incluidos los detalles de RPC, consulta
[Referencia de incorporación](/es/reference/wizard).

## Documentos relacionados

- Referencia de comandos de la CLI: [`openclaw onboard`](/cli/onboard)
- Descripción general de la incorporación: [Resumen de incorporación](/es/start/onboarding-overview)
- Incorporación en la app de macOS: [Incorporación](/es/start/onboarding)
- Ritual de primera ejecución del agente: [Inicialización del agente](/es/start/bootstrapping)
