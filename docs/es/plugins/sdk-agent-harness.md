---
read_when:
    - Estás cambiando el tiempo de ejecución integrado del agente o el registro del harness
    - Estás registrando un harness de agente desde un plugin incluido o de confianza
    - Necesitas entender cómo se relaciona el plugin Codex con los proveedores de modelos
sidebarTitle: Agent Harness
summary: Superficie experimental del SDK para plugins que reemplazan el ejecutor integrado de agentes de bajo nivel
title: Plugins de Agent Harness
x-i18n:
    generated_at: "2026-04-12T00:19:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugins de Agent Harness

Un **agent harness** es el ejecutor de bajo nivel para un turno preparado de un agente de OpenClaw. No es un proveedor de modelos, no es un canal y no es un registro de herramientas.

Usa esta superficie solo para plugins nativos incluidos o de confianza. El contrato sigue siendo experimental porque los tipos de parámetros reflejan intencionalmente el ejecutor integrado actual.

## Cuándo usar un harness

Registra un agent harness cuando una familia de modelos tiene su propio tiempo de ejecución de sesión nativo y el transporte normal de proveedores de OpenClaw es la abstracción incorrecta.

Ejemplos:

- un servidor nativo de agente de programación que administra hilos y compactación
- una CLI o un daemon local que debe transmitir eventos nativos de plan/razonamiento/herramientas
- un tiempo de ejecución de modelos que necesita su propio id de reanudación además del transcrito de sesión de OpenClaw

**No** registres un harness solo para agregar una nueva API de LLM. Para APIs de modelos HTTP o WebSocket normales, crea un [plugin de proveedor](/es/plugins/sdk-provider-plugins).

## Lo que el núcleo sigue administrando

Antes de que se seleccione un harness, OpenClaw ya ha resuelto:

- proveedor y modelo
- estado de autenticación del tiempo de ejecución
- nivel de razonamiento y presupuesto de contexto
- el archivo de transcripción/sesión de OpenClaw
- espacio de trabajo, sandbox y política de herramientas
- callbacks de respuesta del canal y callbacks de transmisión
- política de fallback de modelo y cambio de modelo en vivo

Esta separación es intencional. Un harness ejecuta un intento preparado; no elige proveedores, no reemplaza la entrega del canal ni cambia modelos silenciosamente.

## Registrar un harness

**Importación:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Política de selección

OpenClaw elige un harness después de la resolución de proveedor/modelo:

1. `OPENCLAW_AGENT_RUNTIME=<id>` fuerza un harness registrado con ese id.
2. `OPENCLAW_AGENT_RUNTIME=pi` fuerza el harness PI integrado.
3. `OPENCLAW_AGENT_RUNTIME=auto` pide a los harnesses registrados si admiten el proveedor/modelo resuelto.
4. Si ningún harness registrado coincide, OpenClaw usa PI a menos que el fallback a PI esté deshabilitado.

Los fallos de un harness de plugin forzado se muestran como fallos de ejecución. En modo `auto`, OpenClaw puede volver a PI cuando el harness de plugin seleccionado falla antes de que un turno haya producido efectos secundarios. Configura `OPENCLAW_AGENT_HARNESS_FALLBACK=none` o `embeddedHarness.fallback: "none"` para que ese fallback sea en cambio un fallo definitivo.

El plugin Codex incluido registra `codex` como su id de harness. El núcleo trata eso como un id de harness de plugin normal; los alias específicos de Codex pertenecen al plugin o a la configuración del operador, no al selector de tiempo de ejecución compartido.

## Emparejamiento de proveedor y harness

La mayoría de los harnesses también deberían registrar un proveedor. El proveedor hace que las referencias de modelos, el estado de autenticación, los metadatos del modelo y la selección de `/model` sean visibles para el resto de OpenClaw. Luego, el harness reclama ese proveedor en `supports(...)`.

El plugin Codex incluido sigue este patrón:

- id del proveedor: `codex`
- referencias de modelos del usuario: `codex/gpt-5.4`, `codex/gpt-5.2` u otro modelo devuelto por el servidor de aplicaciones de Codex
- id del harness: `codex`
- autenticación: disponibilidad sintética del proveedor, porque el harness de Codex administra el inicio de sesión/sesión nativos de Codex
- solicitud al servidor de aplicaciones: OpenClaw envía el id de modelo sin prefijo a Codex y permite que el harness hable con el protocolo nativo del servidor de aplicaciones

El plugin Codex es aditivo. Las referencias simples `openai/gpt-*` siguen siendo referencias del proveedor OpenAI y continúan usando la ruta normal de proveedores de OpenClaw. Selecciona `codex/gpt-*` cuando quieras autenticación administrada por Codex, descubrimiento de modelos de Codex, hilos nativos y ejecución del servidor de aplicaciones de Codex. `/model` puede cambiar entre los modelos de Codex devueltos por el servidor de aplicaciones de Codex sin requerir credenciales del proveedor OpenAI.

Para la configuración del operador, ejemplos de prefijos de modelo y configuraciones exclusivas de Codex, consulta [Codex Harness](/es/plugins/codex-harness).

OpenClaw requiere Codex app-server `0.118.0` o una versión más reciente. El plugin Codex verifica el handshake de inicialización del servidor de aplicaciones y bloquea servidores más antiguos o sin versión para que OpenClaw solo se ejecute contra la superficie de protocolo con la que se ha probado.

### Modo de harness nativo de Codex

El harness `codex` incluido es el modo nativo de Codex para los turnos integrados de agentes de OpenClaw. Primero habilita el plugin `codex` incluido e incluye `codex` en `plugins.allow` si tu configuración usa una allowlist restrictiva. Es diferente de `openai-codex/*`:

- `openai-codex/*` usa OAuth de ChatGPT/Codex a través de la ruta normal de proveedores de OpenClaw.
- `codex/*` usa el proveedor Codex incluido y enruta el turno a través de Codex app-server.

Cuando se ejecuta este modo, Codex administra el id del hilo nativo, el comportamiento de reanudación, la compactación y la ejecución del servidor de aplicaciones. OpenClaw sigue administrando el canal de chat, el espejo visible de la transcripción, la política de herramientas, las aprobaciones, la entrega de medios y la selección de sesión. Usa `embeddedHarness.runtime: "codex"` con `embeddedHarness.fallback: "none"` cuando necesites demostrar que se usa la ruta de Codex app-server y que el fallback a PI no está ocultando un harness nativo defectuoso.

## Deshabilitar el fallback a PI

De forma predeterminada, OpenClaw ejecuta agentes integrados con `agents.defaults.embeddedHarness` configurado como `{ runtime: "auto", fallback: "pi" }`. En el modo `auto`, los harnesses de plugin registrados pueden reclamar un par proveedor/modelo. Si ninguno coincide, o si un harness de plugin seleccionado automáticamente falla antes de producir salida, OpenClaw vuelve a PI.

Configura `fallback: "none"` cuando necesites demostrar que un harness de plugin es el único tiempo de ejecución que se está usando. Esto deshabilita el fallback automático a PI; no bloquea un `runtime: "pi"` explícito ni `OPENCLAW_AGENT_RUNTIME=pi`.

Para ejecuciones integradas exclusivas de Codex:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Si quieres que cualquier harness de plugin registrado reclame modelos coincidentes pero nunca quieres que OpenClaw vuelva silenciosamente a PI, mantén `runtime: "auto"` y deshabilita el fallback:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Las anulaciones por agente usan la misma forma:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` sigue anulando el tiempo de ejecución configurado. Usa `OPENCLAW_AGENT_HARNESS_FALLBACK=none` para deshabilitar el fallback a PI desde el entorno.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Con el fallback deshabilitado, una sesión falla pronto cuando el harness solicitado no está registrado, no admite el proveedor/modelo resuelto o falla antes de producir efectos secundarios del turno. Eso es intencional para implementaciones exclusivas de Codex y para pruebas en vivo que deben demostrar que la ruta de Codex app-server realmente está en uso.

Esta configuración solo controla el harness integrado del agente. No deshabilita el enrutamiento específico del proveedor para modelos de imagen, video, música, TTS, PDF u otros.

## Sesiones nativas y espejo de transcripción

Un harness puede conservar un id de sesión nativo, id de hilo o token de reanudación del lado del daemon. Mantén esa vinculación asociada explícitamente con la sesión de OpenClaw y sigue reflejando en la transcripción de OpenClaw la salida visible para el usuario del asistente/herramienta.

La transcripción de OpenClaw sigue siendo la capa de compatibilidad para:

- historial de sesión visible en el canal
- búsqueda e indexación de transcripciones
- volver al harness PI integrado en un turno posterior
- comportamiento genérico de `/new`, `/reset` y eliminación de sesión

Si tu harness almacena una vinculación sidecar, implementa `reset(...)` para que OpenClaw pueda borrarla cuando se restablezca la sesión de OpenClaw propietaria.

## Resultados de herramientas y medios

El núcleo construye la lista de herramientas de OpenClaw y la pasa al intento preparado. Cuando un harness ejecuta una llamada de herramienta dinámica, devuelve el resultado de la herramienta a través de la forma de resultado del harness en lugar de enviar tú mismo los medios del canal.

Esto mantiene las salidas de texto, imagen, video, música, TTS, aprobación y herramientas de mensajería en la misma ruta de entrega que las ejecuciones respaldadas por PI.

## Limitaciones actuales

- La ruta de importación pública es genérica, pero algunos alias de tipos de intento/resultado todavía llevan nombres `Pi` por compatibilidad.
- La instalación de harnesses de terceros es experimental. Prefiere plugins de proveedor hasta que necesites un tiempo de ejecución de sesión nativo.
- Se admite el cambio de harness entre turnos. No cambies de harness en medio de un turno después de que hayan comenzado herramientas nativas, aprobaciones, texto del asistente o envíos de mensajes.

## Relacionado

- [Resumen del SDK](/es/plugins/sdk-overview)
- [Helpers de tiempo de ejecución](/es/plugins/sdk-runtime)
- [Plugins de proveedor](/es/plugins/sdk-provider-plugins)
- [Codex Harness](/es/plugins/codex-harness)
- [Proveedores de modelos](/es/concepts/model-providers)
