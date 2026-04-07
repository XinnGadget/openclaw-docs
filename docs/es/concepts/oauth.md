---
read_when:
    - Quieres entender OAuth de OpenClaw de extremo a extremo
    - Te encontraste con problemas de invalidación de tokens / cierre de sesión
    - Quieres flujos de autenticación de Claude CLI o OAuth
    - Quieres múltiples cuentas o enrutamiento de perfiles
summary: 'OAuth en OpenClaw: intercambio de tokens, almacenamiento y patrones de múltiples cuentas'
title: OAuth
x-i18n:
    generated_at: "2026-04-07T05:02:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4117fee70e3e64fd3a762403454ac2b78de695d2b85a7146750c6de615921e02
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw admite “autenticación por suscripción” mediante OAuth para los proveedores que la ofrecen
(en particular, **OpenAI Codex (ChatGPT OAuth)**). Para Anthropic, la división práctica
ahora es:

- **Clave de API de Anthropic**: facturación normal de la API de Anthropic
- **Autenticación por suscripción / Claude CLI de Anthropic dentro de OpenClaw**: el personal de Anthropic
  nos dijo que este uso vuelve a estar permitido

OpenAI Codex OAuth es compatible explícitamente para su uso en herramientas externas como
OpenClaw. Esta página explica:

Para Anthropic en producción, la autenticación con clave de API es la ruta recomendada más segura.

- cómo funciona el **intercambio de tokens** de OAuth (PKCE)
- dónde se **almacenan** los tokens (y por qué)
- cómo manejar **múltiples cuentas** (perfiles + reemplazos por sesión)

OpenClaw también admite **plugins de proveedor** que incluyen sus propios flujos de OAuth o clave de API.
Ejecútalos con:

```bash
openclaw models auth login --provider <id>
```

## El sumidero de tokens (por qué existe)

Los proveedores OAuth suelen emitir un **nuevo token de actualización** durante los flujos de inicio de sesión o actualización. Algunos proveedores (o clientes OAuth) pueden invalidar tokens de actualización anteriores cuando se emite uno nuevo para el mismo usuario/aplicación.

Síntoma práctico:

- inicias sesión mediante OpenClaw _y_ mediante Claude Code / Codex CLI → uno de ellos aleatoriamente queda “desconectado” más tarde

Para reducir eso, OpenClaw trata `auth-profiles.json` como un **sumidero de tokens**:

- el runtime lee las credenciales desde **un solo lugar**
- podemos mantener varios perfiles y enrutar entre ellos de forma determinista
- cuando las credenciales se reutilizan desde una CLI externa como Codex CLI, OpenClaw
  las refleja con procedencia y vuelve a leer esa fuente externa en lugar de
  rotar el token de actualización por sí mismo

## Almacenamiento (dónde viven los tokens)

Los secretos se almacenan **por agente**:

- Perfiles de autenticación (OAuth + claves de API + referencias opcionales a nivel de valor): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Archivo de compatibilidad heredado: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (las entradas estáticas `api_key` se depuran cuando se detectan)

Archivo heredado solo para importación (sigue siendo compatible, pero no es el almacenamiento principal):

- `~/.openclaw/credentials/oauth.json` (se importa a `auth-profiles.json` en el primer uso)

Todo lo anterior también respeta `$OPENCLAW_STATE_DIR` (reemplazo del directorio de estado). Referencia completa: [/gateway/configuration](/es/gateway/configuration-reference#auth-storage)

Para referencias estáticas a secretos y el comportamiento de activación de instantáneas del runtime, consulta [Gestión de secretos](/es/gateway/secrets).

## Compatibilidad heredada de tokens de Anthropic

<Warning>
La documentación pública de Claude Code de Anthropic dice que el uso directo de Claude Code se mantiene dentro
de los límites de suscripción de Claude, y el personal de Anthropic nos dijo que el uso de Claude
CLI al estilo OpenClaw vuelve a estar permitido. Por lo tanto, OpenClaw trata la reutilización de Claude CLI y
el uso de `claude -p` como autorizados para esta integración, a menos que Anthropic
publique una política nueva.

Para la documentación actual de Anthropic sobre planes directos de Claude Code, consulta [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
y [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

Si quieres otras opciones de estilo suscripción en OpenClaw, consulta [OpenAI
Codex](/es/providers/openai), [Qwen Cloud Coding
Plan](/es/providers/qwen), [MiniMax Coding Plan](/es/providers/minimax),
y [Z.AI / GLM Coding Plan](/es/providers/glm).
</Warning>

OpenClaw también expone setup-token de Anthropic como una ruta compatible de autenticación por token, pero ahora prefiere la reutilización de Claude CLI y `claude -p` cuando están disponibles.

## Migración de Anthropic Claude CLI

OpenClaw vuelve a admitir la reutilización de Anthropic Claude CLI. Si ya tienes un inicio de sesión local
de Claude en el host, onboarding/configure puede reutilizarlo directamente.

## Intercambio OAuth (cómo funciona el inicio de sesión)

Los flujos de inicio de sesión interactivo de OpenClaw se implementan en `@mariozechner/pi-ai` y se conectan a los asistentes/comandos.

### Setup-token de Anthropic

Forma del flujo:

1. inicia setup-token de Anthropic o pega el token desde OpenClaw
2. OpenClaw almacena la credencial de Anthropic resultante en un perfil de autenticación
3. la selección del modelo permanece en `anthropic/...`
4. los perfiles de autenticación existentes de Anthropic siguen disponibles para control de reversión/orden

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth es compatible explícitamente para su uso fuera de Codex CLI, incluidos los flujos de trabajo de OpenClaw.

Forma del flujo (PKCE):

1. genera un verificador/desafío PKCE + `state` aleatorio
2. abre `https://auth.openai.com/oauth/authorize?...`
3. intenta capturar la devolución de llamada en `http://127.0.0.1:1455/auth/callback`
4. si la devolución de llamada no puede vincularse (o estás en remoto/sin interfaz), pega la URL/código de redirección
5. intercambia en `https://auth.openai.com/oauth/token`
6. extrae `accountId` del token de acceso y almacena `{ access, refresh, expires, accountId }`

La ruta del asistente es `openclaw onboard` → opción de autenticación `openai-codex`.

## Actualización + vencimiento

Los perfiles almacenan una marca de tiempo `expires`.

En tiempo de ejecución:

- si `expires` está en el futuro → usa el token de acceso almacenado
- si ha vencido → actualiza (bajo un bloqueo de archivo) y sobrescribe las credenciales almacenadas
- excepción: las credenciales reutilizadas de una CLI externa siguen gestionadas externamente; OpenClaw
  vuelve a leer el almacén de autenticación de la CLI y nunca consume por sí mismo el token de actualización copiado

El flujo de actualización es automático; por lo general no necesitas administrar los tokens manualmente.

## Múltiples cuentas (perfiles) + enrutamiento

Dos patrones:

### 1) Preferido: agentes separados

Si quieres que “personal” y “trabajo” nunca interactúen, usa agentes aislados (sesiones + credenciales + espacio de trabajo separados):

```bash
openclaw agents add work
openclaw agents add personal
```

Luego configura la autenticación por agente (asistente) y enruta los chats al agente correcto.

### 2) Avanzado: varios perfiles en un agente

`auth-profiles.json` admite varios ID de perfil para el mismo proveedor.

Elige qué perfil se usa:

- globalmente mediante el orden de configuración (`auth.order`)
- por sesión mediante `/model ...@<profileId>`

Ejemplo (reemplazo por sesión):

- `/model Opus@anthropic:work`

Cómo ver qué ID de perfil existen:

- `openclaw channels list --json` (muestra `auth[]`)

Documentación relacionada:

- [/concepts/model-failover](/es/concepts/model-failover) (reglas de rotación + enfriamiento)
- [/tools/slash-commands](/es/tools/slash-commands) (superficie de comandos)

## Relacionado

- [Autenticación](/es/gateway/authentication) — resumen de autenticación de proveedores de modelos
- [Secretos](/es/gateway/secrets) — almacenamiento de credenciales y SecretRef
- [Referencia de configuración](/es/gateway/configuration-reference#auth-storage) — claves de configuración de autenticación
