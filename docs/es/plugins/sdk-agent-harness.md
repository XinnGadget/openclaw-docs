---
read_when:
    - Estás cambiando el runtime del agente integrado o el registro del arnés
    - Estás registrando un arnés de agente desde un plugin integrado o de confianza
    - Necesitas entender cómo se relaciona el plugin Codex con los proveedores de modelos
sidebarTitle: Agent Harness
summary: Superficie experimental del SDK para plugins que reemplazan el ejecutor de agente integrado de bajo nivel
title: Plugins de arnés de agente
x-i18n:
    generated_at: "2026-04-11T02:46:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 43c1f2c087230398b0162ed98449f239c8db1e822e51c7dcd40c54fa6c3374e1
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugins de arnés de agente

Un **arnés de agente** es el ejecutor de bajo nivel para un turno preparado de un agente de OpenClaw.
No es un proveedor de modelos, ni un canal, ni un registro de herramientas.

Usa esta superficie solo para plugins nativos integrados o de confianza. El contrato
sigue siendo experimental porque los tipos de parámetros reflejan intencionalmente el ejecutor
integrado actual.

## Cuándo usar un arnés

Registra un arnés de agente cuando una familia de modelos tiene su propio runtime
nativo de sesión y el transporte normal de proveedor de OpenClaw es la abstracción incorrecta.

Ejemplos:

- un servidor nativo de agente de coding que gestiona hilos y compactación
- una CLI o daemon local que debe transmitir eventos nativos de plan/razonamiento/herramientas
- un runtime de modelo que necesita su propio ID de reanudación además de la
  transcripción de sesión de OpenClaw

**No** registres un arnés solo para agregar una nueva API de LLM. Para APIs normales de modelos por HTTP o
WebSocket, crea un [plugin de proveedor](/es/plugins/sdk-provider-plugins).

## Qué sigue gestionando el núcleo

Antes de que se seleccione un arnés, OpenClaw ya ha resuelto:

- proveedor y modelo
- estado de autenticación de runtime
- nivel de pensamiento y presupuesto de contexto
- la transcripción/archivo de sesión de OpenClaw
- espacio de trabajo, sandbox y política de herramientas
- callbacks de respuesta del canal y callbacks de streaming
- política de respaldo de modelos y cambio de modelos en vivo

Esa división es intencional. Un arnés ejecuta un intento preparado; no elige
proveedores, no reemplaza la entrega por canal ni cambia modelos silenciosamente.

## Registrar un arnés

**Importación:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "Mi arnés de agente nativo",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Inicia o reanuda tu hilo nativo.
    // Usa params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent y los demás campos del intento preparado.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "Mi agente nativo",
  description: "Ejecuta modelos seleccionados mediante un daemon nativo de agente.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Política de selección

OpenClaw elige un arnés después de resolver proveedor/modelo:

1. `OPENCLAW_AGENT_RUNTIME=<id>` fuerza un arnés registrado con ese id.
2. `OPENCLAW_AGENT_RUNTIME=pi` fuerza el arnés PI integrado.
3. `OPENCLAW_AGENT_RUNTIME=auto` pide a los arneses registrados si admiten el
   proveedor/modelo resuelto.
4. Si ningún arnés registrado coincide, OpenClaw usa PI a menos que el respaldo a PI
   esté desactivado.

Los fallos de arneses de plugin forzados aparecen como fallos de ejecución. En modo `auto`,
OpenClaw puede recurrir a PI cuando el arnés de plugin seleccionado falla antes de que un
turno haya producido efectos secundarios. Configura `OPENCLAW_AGENT_HARNESS_FALLBACK=none` o
`embeddedHarness.fallback: "none"` para convertir ese respaldo en un fallo definitivo.

El plugin Codex integrado registra `codex` como su ID de arnés. El núcleo trata eso
como un ID ordinario de arnés de plugin; los alias específicos de Codex pertenecen al plugin
o a la configuración del operador, no al selector de runtime compartido.

## Emparejamiento de proveedor y arnés

La mayoría de los arneses también deberían registrar un proveedor. El proveedor hace visibles al resto de
OpenClaw las referencias de modelo, el estado de autenticación, los metadatos del modelo y la selección de `/model`.
Luego el arnés reclama ese proveedor en `supports(...)`.

El plugin Codex integrado sigue este patrón:

- ID de proveedor: `codex`
- referencias de modelo para el usuario: `codex/gpt-5.4`, `codex/gpt-5.2` u otro modelo devuelto
  por el servidor de aplicaciones de Codex
- ID de arnés: `codex`
- autenticación: disponibilidad sintética del proveedor, porque el arnés Codex gestiona el
  inicio de sesión/sesión nativos de Codex
- solicitud al servidor de aplicaciones: OpenClaw envía el ID de modelo sin prefijo a Codex y deja que el
  arnés hable con el protocolo nativo del servidor de aplicaciones

El plugin Codex es aditivo. Las referencias simples `openai/gpt-*` siguen siendo referencias del proveedor OpenAI
y continúan usando la ruta normal de proveedor de OpenClaw. Selecciona `codex/gpt-*`
cuando quieras autenticación gestionada por Codex, detección de modelos de Codex, hilos nativos y
ejecución en servidor de aplicaciones de Codex. `/model` puede cambiar entre los modelos de Codex devueltos
por el servidor de aplicaciones de Codex sin requerir credenciales del proveedor OpenAI.

Para la configuración del operador, ejemplos de prefijos de modelo y configuraciones solo de Codex, consulta
[Codex Harness](/es/plugins/codex-harness).

OpenClaw requiere Codex app-server `0.118.0` o posterior. El plugin Codex verifica el handshake
de inicialización del servidor de aplicaciones y bloquea servidores más antiguos o sin versión para que
OpenClaw solo se ejecute sobre la superficie de protocolo con la que se ha probado.

## Desactivar el respaldo a PI

De forma predeterminada, OpenClaw ejecuta agentes integrados con `agents.defaults.embeddedHarness`
configurado como `{ runtime: "auto", fallback: "pi" }`. En modo `auto`, los plugins registrados
de arnés pueden reclamar un par proveedor/modelo. Si ninguno coincide, o si un
arnés de plugin seleccionado automáticamente falla antes de producir salida, OpenClaw recurre a PI.

Configura `fallback: "none"` cuando necesites demostrar que un arnés de plugin es el único
runtime que se está usando. Esto desactiva el respaldo automático a PI; no bloquea
un `runtime: "pi"` explícito ni `OPENCLAW_AGENT_RUNTIME=pi`.

Para ejecuciones integradas solo con Codex:

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

Si quieres que cualquier arnés de plugin registrado reclame modelos coincidentes pero nunca
quieres que OpenClaw recurra silenciosamente a PI, mantén `runtime: "auto"` y desactiva
el respaldo:

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

`OPENCLAW_AGENT_RUNTIME` sigue anulando el runtime configurado. Usa
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` para desactivar el respaldo a PI desde el
entorno.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Con el respaldo desactivado, una sesión falla temprano cuando el arnés solicitado no está
registrado, no admite el proveedor/modelo resuelto o falla antes de
producir efectos secundarios del turno. Eso es intencional para despliegues solo con Codex y
para pruebas en vivo que deben demostrar que realmente se está usando la ruta del servidor de aplicaciones de Codex.

Esta configuración solo controla el arnés de agente integrado. No desactiva
el enrutamiento específico de modelos para imagen, video, música, TTS, PDF u otros proveedores.

## Sesiones nativas y espejo de transcripción

Un arnés puede conservar un ID de sesión nativa, ID de hilo o token de reanudación del lado del daemon.
Mantén esa asociación vinculada explícitamente con la sesión de OpenClaw y sigue
reflejando la salida visible para el usuario del asistente/herramienta en la transcripción de OpenClaw.

La transcripción de OpenClaw sigue siendo la capa de compatibilidad para:

- historial de sesión visible en el canal
- búsqueda e indexación de transcripciones
- volver al arnés PI integrado en un turno posterior
- comportamiento genérico de `/new`, `/reset` y eliminación de sesiones

Si tu arnés almacena una asociación auxiliar, implementa `reset(...)` para que OpenClaw pueda
borrarla cuando se restablezca la sesión de OpenClaw propietaria.

## Resultados de herramientas y medios

El núcleo construye la lista de herramientas de OpenClaw y la pasa al intento preparado.
Cuando un arnés ejecuta una llamada de herramienta dinámica, devuelve el resultado de la herramienta mediante
la forma de resultado del arnés en lugar de enviar tú mismo el contenido multimedia por el canal.

Esto mantiene las salidas de texto, imagen, video, música, TTS, aprobación y herramientas de mensajería
en la misma ruta de entrega que las ejecuciones respaldadas por PI.

## Limitaciones actuales

- La ruta pública de importación es genérica, pero algunos alias de tipos de intento/resultado todavía
  llevan nombres `Pi` por compatibilidad.
- La instalación de arneses de terceros es experimental. Prefiere plugins de proveedor
  hasta que necesites un runtime de sesión nativa.
- Se admite el cambio de arnés entre turnos. No cambies de arnés en medio de un
  turno después de que hayan comenzado herramientas nativas, aprobaciones, texto del asistente o
  envíos de mensajes.

## Relacionado

- [SDK Overview](/es/plugins/sdk-overview)
- [Runtime Helpers](/es/plugins/sdk-runtime)
- [Provider Plugins](/es/plugins/sdk-provider-plugins)
- [Codex Harness](/es/plugins/codex-harness)
- [Model Providers](/es/concepts/model-providers)
