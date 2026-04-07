---
read_when:
    - Quieres usar modelos de Anthropic en OpenClaw
summary: Usa Anthropic Claude mediante claves API o Claude CLI en OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-07T05:05:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 423928fd36c66729985208d4d3f53aff1f94f63b908df85072988bdc41d5cf46
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic desarrolla la familia de modelos **Claude** y proporciona acceso mediante una API y
Claude CLI. En OpenClaw, se admiten tanto las claves API de Anthropic como la
reutilización de Claude CLI. Los perfiles heredados de token de Anthropic existentes siguen siendo válidos
en tiempo de ejecución si ya están configurados.

<Warning>
El personal de Anthropic nos dijo que el uso de Claude CLI al estilo de OpenClaw vuelve a estar permitido, por lo que
OpenClaw considera la reutilización de Claude CLI y el uso de `claude -p` como autorizados para
esta integración, a menos que Anthropic publique una nueva política.

Para hosts de gateway de larga duración, las claves API de Anthropic siguen siendo la ruta de producción
más clara y predecible. Si ya usas Claude CLI en el host,
OpenClaw puede reutilizar ese inicio de sesión directamente.

La documentación pública actual de Anthropic:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

Si quieres la ruta de facturación más clara, usa en su lugar una clave API de Anthropic.
OpenClaw también admite otras opciones de estilo suscripción, incluidas [OpenAI
Codex](/es/providers/openai), [Qwen Cloud Coding Plan](/es/providers/qwen),
[MiniMax Coding Plan](/es/providers/minimax) y [Z.AI / GLM Coding
Plan](/es/providers/glm).
</Warning>

## Opción A: clave API de Anthropic

**Ideal para:** acceso estándar a la API y facturación por uso.
Crea tu clave API en la consola de Anthropic.

### Configuración por CLI

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Fragmento de configuración de Anthropic

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Valores predeterminados de thinking (Claude 4.6)

- Los modelos Anthropic Claude 4.6 usan `adaptive` thinking de forma predeterminada en OpenClaw cuando no se establece un nivel explícito de thinking.
- Puedes anularlo por mensaje (`/think:<level>`) o en los parámetros del modelo:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- Documentación relacionada de Anthropic:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Modo rápido (API de Anthropic)

La opción compartida `/fast` de OpenClaw también admite tráfico público directo de Anthropic, incluidas solicitudes autenticadas con clave API y OAuth enviadas a `api.anthropic.com`.

- `/fast on` se asigna a `service_tier: "auto"`
- `/fast off` se asigna a `service_tier: "standard_only"`
- Configuración predeterminada:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

Límites importantes:

- OpenClaw solo inyecta niveles de servicio de Anthropic para solicitudes directas a `api.anthropic.com`. Si enrutas `anthropic/*` a través de un proxy o gateway, `/fast` deja `service_tier` sin cambios.
- Los parámetros explícitos del modelo `serviceTier` o `service_tier` de Anthropic anulan el valor predeterminado de `/fast` cuando ambos están establecidos.
- Anthropic informa el nivel efectivo en la respuesta bajo `usage.service_tier`. En cuentas sin capacidad de Priority Tier, `service_tier: "auto"` puede seguir resolviéndose como `standard`.

## Caché de prompt (API de Anthropic)

OpenClaw admite la función de caché de prompt de Anthropic. Esto es **solo para API**; la autenticación heredada por token de Anthropic no respeta la configuración de caché.

### Configuración

Usa el parámetro `cacheRetention` en la configuración de tu modelo:

| Valor   | Duración de la caché | Descripción                     |
| ------- | -------------------- | ------------------------------- |
| `none`  | Sin caché            | Deshabilitar caché de prompt    |
| `short` | 5 minutos            | Predeterminado para clave API   |
| `long`  | 1 hora               | Caché extendida                 |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### Valores predeterminados

Al usar autenticación con clave API de Anthropic, OpenClaw aplica automáticamente `cacheRetention: "short"` (caché de 5 minutos) para todos los modelos de Anthropic. Puedes anular esto configurando explícitamente `cacheRetention` en tu configuración.

### Anulaciones de cacheRetention por agente

Usa parámetros a nivel de modelo como base y luego anula agentes específicos mediante `agents.list[].params`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // base para la mayoría de los agentes
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // anulación solo para este agente
    ],
  },
}
```

Orden de combinación de configuración para parámetros relacionados con caché:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (coincidencia por `id`, anula por clave)

Esto permite que un agente mantenga una caché de larga duración mientras otro agente en el mismo modelo deshabilita la caché para evitar costes de escritura en tráfico intermitente o de baja reutilización.

### Notas sobre Bedrock Claude

- Los modelos Anthropic Claude en Bedrock (`amazon-bedrock/*anthropic.claude*`) aceptan el paso directo de `cacheRetention` cuando está configurado.
- En tiempo de ejecución, los modelos de Bedrock que no son de Anthropic se fuerzan a `cacheRetention: "none"`.
- Los valores predeterminados inteligentes de clave API de Anthropic también inicializan `cacheRetention: "short"` para referencias de modelos Claude-on-Bedrock cuando no se establece ningún valor explícito.

## Ventana de contexto de 1M (beta de Anthropic)

La ventana de contexto de 1M de Anthropic está restringida por beta. En OpenClaw, actívala por modelo
con `params.context1m: true` para los modelos Opus/Sonnet compatibles.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw asigna esto a `anthropic-beta: context-1m-2025-08-07` en las solicitudes
a Anthropic.

Esto solo se activa cuando `params.context1m` se establece explícitamente en `true` para
ese modelo.

Requisito: Anthropic debe permitir el uso de contexto largo con esa credencial.

Nota: Anthropic rechaza actualmente las solicitudes beta `context-1m-*` cuando se usa
la autenticación heredada por token de Anthropic (`sk-ant-oat-*`). Si configuras
`context1m: true` con ese modo de autenticación heredado, OpenClaw registra una advertencia y
recurre a la ventana de contexto estándar omitiendo la cabecera beta `context1m`
mientras mantiene las betas OAuth necesarias.

## Backend de Claude CLI

El backend incluido `claude-cli` de Anthropic es compatible con OpenClaw.

- El personal de Anthropic nos dijo que este uso vuelve a estar permitido.
- Por lo tanto, OpenClaw considera la reutilización de Claude CLI y el uso de `claude -p` como
  autorizados para esta integración, a menos que Anthropic publique una nueva política.
- Las claves API de Anthropic siguen siendo la ruta de producción más clara para hosts de gateway
  siempre activos y para un control explícito de la facturación del lado del servidor.
- Los detalles de configuración y tiempo de ejecución están en [/gateway/cli-backends](/es/gateway/cli-backends).

## Notas

- La documentación pública de Claude Code de Anthropic sigue documentando el uso directo de CLI como
  `claude -p`, y el personal de Anthropic nos dijo que el uso de Claude CLI al estilo de OpenClaw vuelve a estar
  permitido. Estamos considerando esta orientación como establecida salvo que Anthropic
  publique un nuevo cambio de política.
- El setup-token de Anthropic sigue disponible en OpenClaw como una ruta compatible de autenticación por token, pero OpenClaw ahora prefiere la reutilización de Claude CLI y `claude -p` cuando están disponibles.
- Los detalles de autenticación y las reglas de reutilización están en [/concepts/oauth](/es/concepts/oauth).

## Solución de problemas

**Errores 401 / token repentinamente no válido**

- La autenticación por token de Anthropic puede caducar o ser revocada.
- Para una configuración nueva, migra a una clave API de Anthropic.

**No API key found for provider "anthropic"**

- La autenticación es **por agente**. Los agentes nuevos no heredan las claves del agente principal.
- Vuelve a ejecutar la incorporación para ese agente, o configura una clave API en el host
  del gateway y luego verifica con `openclaw models status`.

**No credentials found for profile `anthropic:default`**

- Ejecuta `openclaw models status` para ver qué perfil de autenticación está activo.
- Vuelve a ejecutar la incorporación, o configura una clave API para esa ruta de perfil.

**No available auth profile (all in cooldown/unavailable)**

- Comprueba `openclaw models status --json` para ver `auth.unusableProfiles`.
- Los periodos de espera por límite de tasa de Anthropic pueden limitarse por modelo, por lo que otro modelo Anthropic relacionado
  puede seguir siendo utilizable aunque el actual esté en enfriamiento.
- Añade otro perfil de Anthropic o espera a que termine el enfriamiento.

Más información: [/gateway/troubleshooting](/es/gateway/troubleshooting) y [/help/faq](/es/help/faq).
