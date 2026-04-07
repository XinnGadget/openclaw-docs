---
read_when:
    - Quieres crear un nuevo plugin de OpenClaw
    - Necesitas una guía de inicio rápido para el desarrollo de plugins
    - Estás agregando un nuevo canal, proveedor, herramienta u otra capacidad a OpenClaw
sidebarTitle: Getting Started
summary: Crea tu primer plugin de OpenClaw en minutos
title: Creación de plugins
x-i18n:
    generated_at: "2026-04-07T05:04:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 509c1f5abe1a0a74966054ed79b71a1a7ee637a43b1214c424acfe62ddf48eef
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Creación de plugins

Los plugins amplían OpenClaw con nuevas capacidades: canales, proveedores de modelos,
voz, transcripción en tiempo real, voz en tiempo real, comprensión de medios, generación de imágenes,
generación de video, obtención web, búsqueda web, herramientas de agente o cualquier
combinación.

No necesitas agregar tu plugin al repositorio de OpenClaw. Publícalo en
[ClawHub](/es/tools/clawhub) o npm y los usuarios lo instalan con
`openclaw plugins install <package-name>`. OpenClaw intenta primero con ClawHub y
recurre automáticamente a npm si es necesario.

## Requisitos previos

- Node >= 22 y un administrador de paquetes (npm o pnpm)
- Familiaridad con TypeScript (ESM)
- Para plugins dentro del repositorio: repositorio clonado y `pnpm install` ejecutado

## ¿Qué tipo de plugin?

<CardGroup cols={3}>
  <Card title="Plugin de canal" icon="messages-square" href="/es/plugins/sdk-channel-plugins">
    Conecta OpenClaw a una plataforma de mensajería (Discord, IRC, etc.)
  </Card>
  <Card title="Plugin de proveedor" icon="cpu" href="/es/plugins/sdk-provider-plugins">
    Agrega un proveedor de modelos (LLM, proxy o endpoint personalizado)
  </Card>
  <Card title="Plugin de herramienta / hook" icon="wrench">
    Registra herramientas de agente, hooks de eventos o servicios — continúa abajo
  </Card>
</CardGroup>

Si un plugin de canal es opcional y puede no estar instalado cuando se ejecuta la incorporación/configuración,
usa `createOptionalChannelSetupSurface(...)` de
`openclaw/plugin-sdk/channel-setup`. Produce un par adaptador + asistente de configuración
que anuncia el requisito de instalación y falla de forma segura en escrituras reales de configuración
hasta que el plugin esté instalado.

## Inicio rápido: plugin de herramienta

Este recorrido crea un plugin mínimo que registra una herramienta de agente. Los plugins de canal
y proveedor tienen guías dedicadas enlazadas arriba.

<Steps>
  <Step title="Crea el paquete y el manifiesto">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-my-plugin",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Todo plugin necesita un manifiesto, incluso sin configuración. Consulta
    [Manifest](/es/plugins/manifest) para ver el esquema completo. Los fragmentos canónicos de publicación
    en ClawHub se encuentran en `docs/snippets/plugin-publish/`.

  </Step>

  <Step title="Escribe el punto de entrada">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry` es para plugins que no son de canal. Para canales, usa
    `defineChannelPluginEntry` — consulta [Plugins de canal](/es/plugins/sdk-channel-plugins).
    Para ver todas las opciones del punto de entrada, consulta [Puntos de entrada](/es/plugins/sdk-entrypoints).

  </Step>

  <Step title="Prueba y publica">

    **Plugins externos:** valida y publica con ClawHub, luego instala:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw también comprueba ClawHub antes que npm para especificaciones de paquete simples como
    `@myorg/openclaw-my-plugin`.

    **Plugins dentro del repositorio:** colócalos bajo el árbol del espacio de trabajo de plugins incluidos — se descubren automáticamente.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Capacidades del plugin

Un único plugin puede registrar cualquier cantidad de capacidades mediante el objeto `api`:

| Capacidad              | Método de registro                              | Guía detallada                                                                 |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------ |
| Inferencia de texto (LLM) | `api.registerProvider(...)`                   | [Plugins de proveedor](/es/plugins/sdk-provider-plugins)                          |
| Backend de inferencia de CLI | `api.registerCliBackend(...)`              | [Backends de CLI](/es/gateway/cli-backends)                                       |
| Canal / mensajería     | `api.registerChannel(...)`                       | [Plugins de canal](/es/plugins/sdk-channel-plugins)                               |
| Voz (TTS/STT)          | `api.registerSpeechProvider(...)`                | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Transcripción en tiempo real | `api.registerRealtimeTranscriptionProvider(...)` | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Voz en tiempo real     | `api.registerRealtimeVoiceProvider(...)`         | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Comprensión de medios  | `api.registerMediaUnderstandingProvider(...)`    | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Generación de imágenes | `api.registerImageGenerationProvider(...)`       | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Generación de música   | `api.registerMusicGenerationProvider(...)`       | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Generación de video    | `api.registerVideoGenerationProvider(...)`       | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Obtención web          | `api.registerWebFetchProvider(...)`              | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Búsqueda web           | `api.registerWebSearchProvider(...)`             | [Plugins de proveedor](/es/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Herramientas de agente | `api.registerTool(...)`                          | Más abajo                                                                      |
| Comandos personalizados | `api.registerCommand(...)`                      | [Puntos de entrada](/es/plugins/sdk-entrypoints)                                  |
| Hooks de eventos       | `api.registerHook(...)`                          | [Puntos de entrada](/es/plugins/sdk-entrypoints)                                  |
| Rutas HTTP             | `api.registerHttpRoute(...)`                     | [Internals](/es/plugins/architecture#gateway-http-routes)                         |
| Subcomandos de CLI     | `api.registerCli(...)`                           | [Puntos de entrada](/es/plugins/sdk-entrypoints)                                  |

Para la API de registro completa, consulta [Resumen del SDK](/es/plugins/sdk-overview#registration-api).

Si tu plugin registra métodos RPC personalizados del gateway, mantenlos en un
prefijo específico del plugin. Los espacios de nombres administrativos del núcleo (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) permanecen reservados y siempre se resuelven a
`operator.admin`, incluso si un plugin solicita un alcance más limitado.

Semántica de guardas de hooks a tener en cuenta:

- `before_tool_call`: `{ block: true }` es terminal y detiene los controladores de menor prioridad.
- `before_tool_call`: `{ block: false }` se trata como sin decisión.
- `before_tool_call`: `{ requireApproval: true }` pausa la ejecución del agente y solicita aprobación del usuario mediante la superposición de aprobación de ejecución, botones de Telegram, interacciones de Discord o el comando `/approve` en cualquier canal.
- `before_install`: `{ block: true }` es terminal y detiene los controladores de menor prioridad.
- `before_install`: `{ block: false }` se trata como sin decisión.
- `message_sending`: `{ cancel: true }` es terminal y detiene los controladores de menor prioridad.
- `message_sending`: `{ cancel: false }` se trata como sin decisión.

El comando `/approve` gestiona tanto aprobaciones de ejecución como de plugins con un respaldo acotado: cuando no se encuentra un id de aprobación de ejecución, OpenClaw vuelve a intentar el mismo id mediante las aprobaciones del plugin. El reenvío de aprobaciones del plugin puede configurarse de forma independiente mediante `approvals.plugin` en la configuración.

Si una lógica personalizada de aprobación necesita detectar ese mismo caso de respaldo acotado,
prefiere `isApprovalNotFoundError` de `openclaw/plugin-sdk/error-runtime`
en lugar de comparar manualmente cadenas de vencimiento de aprobación.

Consulta [semántica de decisiones de hooks del Resumen del SDK](/es/plugins/sdk-overview#hook-decision-semantics) para obtener detalles.

## Registro de herramientas de agente

Las herramientas son funciones tipadas que el LLM puede invocar. Pueden ser obligatorias (siempre
disponibles) u opcionales (activación del usuario):

```typescript
register(api) {
  // Herramienta obligatoria — siempre disponible
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Herramienta opcional — el usuario debe agregarla a la lista de permitidos
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

Los usuarios habilitan herramientas opcionales en la configuración:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- Los nombres de herramientas no deben entrar en conflicto con las herramientas del núcleo (los conflictos se omiten)
- Usa `optional: true` para herramientas con efectos secundarios o requisitos binarios adicionales
- Los usuarios pueden habilitar todas las herramientas de un plugin agregando el id del plugin a `tools.allow`

## Convenciones de importación

Importa siempre desde rutas específicas `openclaw/plugin-sdk/<subpath>`:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Incorrecto: raíz monolítica (obsoleta, se eliminará)
import { ... } from "openclaw/plugin-sdk";
```

Para la referencia completa de subrutas, consulta [Resumen del SDK](/es/plugins/sdk-overview).

Dentro de tu plugin, usa archivos barrel locales (`api.ts`, `runtime-api.ts`) para
importaciones internas; nunca importes tu propio plugin mediante su ruta del SDK.

Para plugins de proveedor, mantén los helpers específicos del proveedor en esos barrels
de raíz del paquete, a menos que la interfaz sea realmente genérica. Ejemplos actuales incluidos:

- Anthropic: envoltorios de flujo de Claude y helpers de `service_tier` / beta
- OpenAI: constructores de proveedores, helpers de modelos predeterminados, proveedores en tiempo real
- OpenRouter: constructor de proveedor más helpers de incorporación/configuración

Si un helper solo es útil dentro de un paquete de proveedor incluido, mantenlo en esa
interfaz de raíz del paquete en lugar de promoverlo a `openclaw/plugin-sdk/*`.

Algunas interfaces helper generadas `openclaw/plugin-sdk/<bundled-id>` todavía existen para
mantenimiento y compatibilidad de plugins incluidos, por ejemplo
`plugin-sdk/feishu-setup` o `plugin-sdk/zalo-setup`. Trátalas como superficies
reservadas, no como el patrón predeterminado para nuevos plugins de terceros.

## Lista de comprobación previa al envío

<Check>**package.json** tiene los metadatos `openclaw` correctos</Check>
<Check>El manifiesto **openclaw.plugin.json** está presente y es válido</Check>
<Check>El punto de entrada usa `defineChannelPluginEntry` o `definePluginEntry`</Check>
<Check>Todas las importaciones usan rutas específicas `plugin-sdk/<subpath>`</Check>
<Check>Las importaciones internas usan módulos locales, no autoimportaciones del SDK</Check>
<Check>Las pruebas pasan (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` pasa (plugins dentro del repositorio)</Check>

## Pruebas de versiones beta

1. Observa las etiquetas de versiones de GitHub en [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) y suscríbete mediante `Watch` > `Releases`. Las etiquetas beta tienen este aspecto: `v2026.3.N-beta.1`. También puedes activar notificaciones para la cuenta oficial de OpenClaw en X [@openclaw](https://x.com/openclaw) para recibir anuncios de versiones.
2. Prueba tu plugin con la etiqueta beta en cuanto aparezca. El margen antes de la versión estable suele ser de solo unas horas.
3. Publica en el hilo de tu plugin en el canal `plugin-forum` de Discord después de probar con `all good` o indicando qué falló. Si todavía no tienes un hilo, crea uno.
4. Si algo falla, abre o actualiza una incidencia titulada `Beta blocker: <plugin-name> - <summary>` y aplica la etiqueta `beta-blocker`. Pon el enlace de la incidencia en tu hilo.
5. Abre un PR a `main` titulado `fix(<plugin-id>): beta blocker - <summary>` y enlaza la incidencia tanto en el PR como en tu hilo de Discord. Los colaboradores no pueden etiquetar PRs, así que el título es la señal del lado del PR para mantenedores y automatización. Los bloqueadores con PR se fusionan; los bloqueadores sin PR podrían enviarse igualmente. Los mantenedores observan estos hilos durante las pruebas beta.
6. El silencio significa verde. Si pierdes la ventana, tu corrección probablemente llegue en el siguiente ciclo.

## Siguientes pasos

<CardGroup cols={2}>
  <Card title="Plugins de canal" icon="messages-square" href="/es/plugins/sdk-channel-plugins">
    Crea un plugin de canal de mensajería
  </Card>
  <Card title="Plugins de proveedor" icon="cpu" href="/es/plugins/sdk-provider-plugins">
    Crea un plugin de proveedor de modelos
  </Card>
  <Card title="Resumen del SDK" icon="book-open" href="/es/plugins/sdk-overview">
    Referencia del mapa de importaciones y de la API de registro
  </Card>
  <Card title="Helpers de tiempo de ejecución" icon="settings" href="/es/plugins/sdk-runtime">
    TTS, búsqueda, subagente mediante api.runtime
  </Card>
  <Card title="Pruebas" icon="test-tubes" href="/es/plugins/sdk-testing">
    Utilidades y patrones de prueba
  </Card>
  <Card title="Manifiesto del plugin" icon="file-json" href="/es/plugins/manifest">
    Referencia completa del esquema del manifiesto
  </Card>
</CardGroup>

## Relacionado

- [Arquitectura de plugins](/es/plugins/architecture) — análisis en profundidad de la arquitectura interna
- [Resumen del SDK](/es/plugins/sdk-overview) — referencia del Plugin SDK
- [Manifest](/es/plugins/manifest) — formato del manifiesto del plugin
- [Plugins de canal](/es/plugins/sdk-channel-plugins) — creación de plugins de canal
- [Plugins de proveedor](/es/plugins/sdk-provider-plugins) — creación de plugins de proveedor
