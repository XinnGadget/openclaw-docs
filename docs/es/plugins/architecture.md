---
read_when:
    - Crear o depurar plugins nativos de OpenClaw
    - Comprender el modelo de capacidades de plugins o los límites de propiedad
    - Trabajar en el canal de carga o el registro de plugins
    - Implementar hooks de entorno de ejecución de proveedores o plugins de canal
sidebarTitle: Internals
summary: 'Aspectos internos de plugins: modelo de capacidades, propiedad, contratos, canal de carga y asistentes de entorno de ejecución'
title: Aspectos internos de plugins
x-i18n:
    generated_at: "2026-04-07T05:06:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9c4b0602df12965a29881eab33b0885f991aeefa2a3fdf3cefc1a7770d6dabe0
    source_path: plugins/architecture.md
    workflow: 15
---

# Aspectos internos de plugins

<Info>
  Esta es la **referencia profunda de arquitectura**. Para guías prácticas, consulta:
  - [Instalar y usar plugins](/es/tools/plugin) — guía del usuario
  - [Primeros pasos](/es/plugins/building-plugins) — tutorial del primer plugin
  - [Plugins de canal](/es/plugins/sdk-channel-plugins) — crear un canal de mensajería
  - [Plugins de proveedor](/es/plugins/sdk-provider-plugins) — crear un proveedor de modelos
  - [Descripción general del SDK](/es/plugins/sdk-overview) — mapa de importación y API de registro
</Info>

Esta página cubre la arquitectura interna del sistema de plugins de OpenClaw.

## Modelo público de capacidades

Las capacidades son el modelo público de **plugins nativos** dentro de OpenClaw. Cada
plugin nativo de OpenClaw se registra frente a uno o más tipos de capacidad:

| Capacidad             | Método de registro                              | Plugins de ejemplo                    |
| --------------------- | ----------------------------------------------- | ------------------------------------- |
| Inferencia de texto   | `api.registerProvider(...)`                     | `openai`, `anthropic`                 |
| Backend de inferencia CLI | `api.registerCliBackend(...)`               | `openai`, `anthropic`                 |
| Voz                   | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`             |
| Transcripción en tiempo real | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                      |
| Voz en tiempo real    | `api.registerRealtimeVoiceProvider(...)`        | `openai`                              |
| Comprensión de medios | `api.registerMediaUnderstandingProvider(...)`   | `openai`, `google`                    |
| Generación de imágenes | `api.registerImageGenerationProvider(...)`     | `openai`, `google`, `fal`, `minimax`  |
| Generación de música  | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                   |
| Generación de video   | `api.registerVideoGenerationProvider(...)`      | `qwen`                                |
| Obtención web         | `api.registerWebFetchProvider(...)`             | `firecrawl`                           |
| Búsqueda web          | `api.registerWebSearchProvider(...)`            | `google`                              |
| Canal / mensajería    | `api.registerChannel(...)`                      | `msteams`, `matrix`                   |

Un plugin que registra cero capacidades pero proporciona hooks, herramientas o
servicios es un plugin **legacy solo de hooks**. Ese patrón sigue siendo totalmente compatible.

### Postura de compatibilidad externa

El modelo de capacidades ya está incorporado en el core y hoy lo usan plugins
integrados/nativos, pero la compatibilidad de plugins externos todavía necesita una vara
más estricta que “está exportado, por lo tanto está congelado”.

Guía actual:

- **plugins externos existentes:** mantener funcionando las integraciones basadas en hooks; tratar
  esto como la base de compatibilidad
- **nuevos plugins integrados/nativos:** preferir el registro explícito de capacidades frente a
  accesos específicos de proveedor o nuevos diseños solo con hooks
- **plugins externos que adopten registro de capacidades:** está permitido, pero tratar las
  superficies auxiliares específicas de capacidad como algo cambiante, salvo que la documentación marque explícitamente un
  contrato como estable

Regla práctica:

- las APIs de registro de capacidades son la dirección deseada
- los hooks legacy siguen siendo el camino más seguro para evitar roturas en plugins externos durante
  la transición
- no todos los subpaths auxiliares exportados son iguales; prefiere el contrato documentado y
  específico, no exportaciones auxiliares incidentales

### Formas de plugins

OpenClaw clasifica cada plugin cargado en una forma según su comportamiento de
registro real (no solo sus metadatos estáticos):

- **plain-capability** -- registra exactamente un tipo de capacidad (por ejemplo, un
  plugin solo de proveedor como `mistral`)
- **hybrid-capability** -- registra múltiples tipos de capacidad (por ejemplo
  `openai` posee inferencia de texto, voz, comprensión de medios y generación de
  imágenes)
- **hook-only** -- registra solo hooks (tipados o personalizados), sin capacidades,
  herramientas, comandos ni servicios
- **non-capability** -- registra herramientas, comandos, servicios o rutas, pero no
  capacidades

Usa `openclaw plugins inspect <id>` para ver la forma de un plugin y el desglose de
capacidades. Consulta [referencia de CLI](/cli/plugins#inspect) para más detalles.

### Hooks legacy

El hook `before_agent_start` sigue siendo compatible como ruta de compatibilidad para
plugins solo con hooks. Plugins legacy del mundo real todavía dependen de él.

Dirección:

- mantenerlo funcionando
- documentarlo como legacy
- preferir `before_model_resolve` para trabajo de anulación de modelo/proveedor
- preferir `before_prompt_build` para trabajo de mutación de prompts
- eliminarlo solo después de que el uso real baje y la cobertura con fixtures pruebe una migración segura

### Señales de compatibilidad

Cuando ejecutes `openclaw doctor` o `openclaw plugins inspect <id>`, puedes ver
una de estas etiquetas:

| Señal                      | Significado                                                  |
| -------------------------- | ------------------------------------------------------------ |
| **config valid**           | La configuración se analiza bien y los plugins se resuelven  |
| **compatibility advisory** | El plugin usa un patrón compatible pero más antiguo (por ejemplo `hook-only`) |
| **legacy warning**         | El plugin usa `before_agent_start`, que está obsoleto        |
| **hard error**             | La configuración no es válida o el plugin no se cargó        |

Ni `hook-only` ni `before_agent_start` romperán tu plugin hoy --
`hook-only` es informativo, y `before_agent_start` solo activa una advertencia. Estas
señales también aparecen en `openclaw status --all` y `openclaw plugins doctor`.

## Descripción general de la arquitectura

El sistema de plugins de OpenClaw tiene cuatro capas:

1. **Manifest + descubrimiento**
   OpenClaw encuentra plugins candidatos a partir de rutas configuradas, raíces de espacios de trabajo,
   raíces globales de extensiones y extensiones integradas. El descubrimiento lee primero los
   manifests nativos `openclaw.plugin.json` y los manifests de bundles compatibles.
2. **Habilitación + validación**
   El core decide si un plugin descubierto está habilitado, deshabilitado, bloqueado o
   seleccionado para un slot exclusivo como memoria.
3. **Carga en tiempo de ejecución**
   Los plugins nativos de OpenClaw se cargan dentro del proceso mediante jiti y registran
   capacidades en un registro central. Los bundles compatibles se normalizan en
   registros del registro sin importar código de entorno de ejecución.
4. **Consumo de superficies**
   El resto de OpenClaw lee el registro para exponer herramientas, canales, configuración
   de proveedores, hooks, rutas HTTP, comandos CLI y servicios.

Para la CLI de plugins en concreto, el descubrimiento de comandos raíz se divide en dos fases:

- los metadatos en tiempo de análisis vienen de `registerCli(..., { descriptors: [...] })`
- el módulo real de CLI del plugin puede seguir siendo diferido y registrarse en la primera invocación

Eso mantiene el código de CLI propiedad del plugin dentro del plugin y, al mismo tiempo, permite que OpenClaw
reserve nombres de comandos raíz antes del análisis.

El límite de diseño importante:

- el descubrimiento y la validación de configuración deben funcionar a partir de **metadatos de manifest/schema**
  sin ejecutar código del plugin
- el comportamiento nativo en tiempo de ejecución proviene de la ruta `register(api)` del módulo del plugin

Esa separación permite a OpenClaw validar la configuración, explicar plugins faltantes/deshabilitados y
construir sugerencias de UI/schema antes de que el entorno de ejecución completo esté activo.

### Plugins de canal y la herramienta compartida de mensajes

Los plugins de canal no necesitan registrar una herramienta separada de enviar/editar/reaccionar para
acciones normales de chat. OpenClaw mantiene una herramienta `message` compartida en el core, y
los plugins de canal poseen el descubrimiento y la ejecución específicos del canal detrás de ella.

El límite actual es:

- el core posee el host compartido de la herramienta `message`, la conexión con el prompt, la gestión
  de sesión/hilo y el despacho de ejecución
- los plugins de canal poseen el descubrimiento de acciones con alcance, el descubrimiento de capacidades y
  cualquier fragmento de schema específico del canal
- los plugins de canal poseen la gramática de conversación de sesión específica del proveedor, como
  cómo los ids de conversación codifican ids de hilos o heredan de conversaciones padre
- los plugins de canal ejecutan la acción final mediante su adaptador de acciones

Para plugins de canal, la superficie del SDK es
`ChannelMessageActionAdapter.describeMessageTool(...)`. Esa llamada unificada de descubrimiento
permite que un plugin devuelva juntas sus acciones visibles, capacidades y contribuciones de schema,
para que esas piezas no se desalineen.

El core pasa el alcance del entorno de ejecución a ese paso de descubrimiento. Los campos importantes incluyen:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` entrante de confianza

Eso importa para plugins sensibles al contexto. Un canal puede ocultar o exponer
acciones de mensaje según la cuenta activa, la sala/hilo/mensaje actual o
la identidad confiable del solicitante, sin codificar ramas específicas del canal en la
herramienta `message` del core.

Por eso los cambios de enrutamiento del ejecutor embebido siguen siendo trabajo del plugin: el ejecutor es
responsable de reenviar la identidad actual de chat/sesión al límite de descubrimiento del plugin
para que la herramienta `message` compartida exponga la superficie correcta, propiedad del canal,
para el turno actual.

Para asistentes de ejecución propiedad del canal, los plugins integrados deben mantener el entorno de ejecución
de la ejecución dentro de sus propios módulos de extensión. El core ya no posee los entornos de ejecución
de acciones de mensajes de Discord, Slack, Telegram o WhatsApp en `src/agents/tools`.
No publicamos subpaths separados `plugin-sdk/*-action-runtime`, y los plugins integrados
deben importar su propio código local de entorno de ejecución directamente desde sus
módulos propiedad de la extensión.

El mismo límite se aplica en general a las costuras del SDK nombradas por proveedor: el core no
debe importar barrels de conveniencia específicos de canal para Slack, Discord, Signal,
WhatsApp o extensiones similares. Si el core necesita un comportamiento, debe consumir el
barrel `api.ts` / `runtime-api.ts` del propio plugin integrado o promover la necesidad
a una capacidad genérica y específica en el SDK compartido.

En el caso concreto de encuestas, hay dos rutas de ejecución:

- `outbound.sendPoll` es la base compartida para los canales que encajan en el modelo
  común de encuestas
- `actions.handleAction("poll")` es la ruta preferida para semánticas de encuesta específicas del canal o parámetros extra

El core ahora aplaza el análisis compartido de encuestas hasta después de que el despacho de encuestas del plugin
rechace la acción, para que los manejadores de encuestas propiedad del plugin puedan aceptar
campos de encuesta específicos del canal sin quedar bloqueados primero por el analizador genérico de encuestas.

Consulta [Canal de carga](#load-pipeline) para ver la secuencia completa de inicio.

## Modelo de propiedad de capacidades

OpenClaw trata a un plugin nativo como el límite de propiedad de una **empresa** o una
**funcionalidad**, no como una bolsa de integraciones no relacionadas.

Eso significa:

- un plugin de empresa normalmente debe poseer todas las superficies de OpenClaw orientadas a esa empresa
- un plugin de funcionalidad normalmente debe poseer toda la superficie de la funcionalidad que introduce
- los canales deben consumir capacidades compartidas del core en lugar de volver a implementar
  comportamiento de proveedor de forma ad hoc

Ejemplos:

- el plugin integrado `openai` posee el comportamiento del proveedor de modelos OpenAI y el comportamiento de OpenAI
  para voz + voz en tiempo real + comprensión de medios + generación de imágenes
- el plugin integrado `elevenlabs` posee el comportamiento de voz de ElevenLabs
- el plugin integrado `microsoft` posee el comportamiento de voz de Microsoft
- el plugin integrado `google` posee el comportamiento del proveedor de modelos Google además del comportamiento de Google
  para comprensión de medios + generación de imágenes + búsqueda web
- el plugin integrado `firecrawl` posee el comportamiento de obtención web de Firecrawl
- los plugins integrados `minimax`, `mistral`, `moonshot` y `zai` poseen sus
  backends de comprensión de medios
- el plugin `voice-call` es un plugin de funcionalidad: posee el transporte de llamadas, herramientas,
  CLI, rutas y el puente Twilio media-stream, pero consume capacidades compartidas de voz
  más transcripción en tiempo real y voz en tiempo real en vez de importar plugins de proveedores directamente

El estado final deseado es:

- OpenAI vive en un único plugin incluso si abarca modelos de texto, voz, imágenes y
  video futuro
- otro proveedor puede hacer lo mismo para su propia área de superficie
- a los canales no les importa qué plugin de proveedor posee el proveedor; consumen el
  contrato de capacidad compartido expuesto por el core

Esta es la distinción clave:

- **plugin** = límite de propiedad
- **capacidad** = contrato del core que múltiples plugins pueden implementar o consumir

Así, si OpenClaw añade un nuevo dominio como video, la primera pregunta no es
“¿qué proveedor debería codificar de forma rígida el manejo de video?” La primera pregunta es “¿cuál es
el contrato de capacidad central para video?” Una vez que ese contrato existe, los plugins de proveedor
pueden registrarse contra él y los plugins de canal/funcionalidad pueden consumirlo.

Si la capacidad aún no existe, lo correcto normalmente es:

1. definir la capacidad faltante en el core
2. exponerla mediante la API/el entorno de ejecución del plugin de forma tipada
3. conectar canales/funcionalidades contra esa capacidad
4. dejar que los plugins de proveedor registren implementaciones

Esto mantiene la propiedad explícita y evita al mismo tiempo que el comportamiento del core dependa de un
solo proveedor o de una ruta de código específica de un plugin concreto.

### Estratificación de capacidades

Usa este modelo mental al decidir dónde debe ir el código:

- **capa de capacidad del core**: orquestación compartida, política, respaldo, reglas de fusión de configuración,
  semántica de entrega y contratos tipados
- **capa de plugin de proveedor**: APIs específicas del proveedor, autenticación, catálogos de modelos, síntesis de voz,
  generación de imágenes, futuros backends de video, endpoints de uso
- **capa de plugin de canal/funcionalidad**: integración de Slack/Discord/voice-call/etc.
  que consume capacidades del core y las presenta en una superficie

Por ejemplo, TTS sigue esta forma:

- el core posee la política de TTS al responder, el orden de respaldo, las preferencias y la entrega por canal
- `openai`, `elevenlabs` y `microsoft` poseen las implementaciones de síntesis
- `voice-call` consume el asistente de entorno de ejecución de TTS para telefonía

Ese mismo patrón debe preferirse para capacidades futuras.

### Ejemplo de plugin de empresa con múltiples capacidades

Un plugin de empresa debe sentirse cohesivo desde fuera. Si OpenClaw tiene contratos compartidos
para modelos, voz, transcripción en tiempo real, voz en tiempo real, comprensión de medios,
generación de imágenes, generación de video, obtención web y búsqueda web,
un proveedor puede poseer todas sus superficies en un solo lugar:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // hooks de autenticación/catálogo de modelos/entorno de ejecución
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // configuración de voz del proveedor — implementar directamente la interfaz SpeechProviderPlugin
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // lógica de credenciales + obtención
      }),
    );
  },
};

export default plugin;
```

Lo importante no son los nombres exactos de los asistentes. Importa la forma:

- un plugin posee la superficie del proveedor
- el core sigue poseyendo los contratos de capacidad
- los canales y plugins de funcionalidad consumen asistentes `api.runtime.*`, no código del proveedor
- las pruebas de contrato pueden verificar que el plugin registró las capacidades que
  afirma poseer

### Ejemplo de capacidad: comprensión de video

OpenClaw ya trata la comprensión de imagen/audio/video como una única
capacidad compartida. El mismo modelo de propiedad se aplica aquí:

1. el core define el contrato de comprensión de medios
2. los plugins de proveedor registran `describeImage`, `transcribeAudio` y
   `describeVideo` según corresponda
3. los plugins de canal y funcionalidad consumen el comportamiento compartido del core en vez de
   conectarse directamente al código del proveedor

Eso evita incorporar al core las suposiciones de video de un proveedor en particular. El plugin posee
la superficie del proveedor; el core posee el contrato de capacidad y el comportamiento de respaldo.

La generación de video ya usa esa misma secuencia: el core posee el contrato de
capacidad tipado y el asistente de entorno de ejecución, y los plugins de proveedor registran
implementaciones `api.registerVideoGenerationProvider(...)` frente a él.

¿Necesitas una lista concreta para el despliegue? Consulta
[Recetario de capacidades](/es/plugins/architecture).

## Contratos y cumplimiento

La superficie de la API de plugins está intencionadamente tipada y centralizada en
`OpenClawPluginApi`. Ese contrato define los puntos de registro compatibles y
los asistentes de entorno de ejecución en los que puede apoyarse un plugin.

Por qué importa esto:

- los autores de plugins obtienen un único estándar interno estable
- el core puede rechazar propiedad duplicada, como dos plugins que registran el mismo
  id de proveedor
- el inicio puede mostrar diagnósticos útiles para registros mal formados
- las pruebas de contrato pueden imponer la propiedad de plugins integrados y evitar desviaciones silenciosas

Hay dos capas de cumplimiento:

1. **cumplimiento del registro en tiempo de ejecución**
   El registro de plugins valida los registros a medida que se cargan los plugins. Ejemplos:
   ids de proveedor duplicados, ids de proveedor de voz duplicados y registros
   mal formados producen diagnósticos del plugin en lugar de comportamiento indefinido.
2. **pruebas de contrato**
   Los plugins integrados se capturan en registros de contrato durante las ejecuciones de prueba para que
   OpenClaw pueda afirmar la propiedad explícitamente. Hoy esto se usa para proveedores de modelos,
   proveedores de voz, proveedores de búsqueda web y propiedad de registros integrados.

El efecto práctico es que OpenClaw sabe, desde el principio, qué plugin posee qué
superficie. Eso permite que el core y los canales compongan sin fricción porque la propiedad está
declarada, tipada y es comprobable, en vez de implícita.

### Qué debe pertenecer a un contrato

Los buenos contratos de plugins son:

- tipados
- pequeños
- específicos de capacidad
- propiedad del core
- reutilizables por múltiples plugins
- consumibles por canales/funcionalidades sin conocimiento del proveedor

Los malos contratos de plugins son:

- política específica del proveedor oculta en el core
- vías de escape únicas de un plugin que eluden el registro
- código de canal que accede directamente a una implementación de proveedor
- objetos de entorno de ejecución ad hoc que no forman parte de `OpenClawPluginApi` ni de
  `api.runtime`

En caso de duda, eleva el nivel de abstracción: define primero la capacidad y luego
deja que los plugins se conecten a ella.

## Modelo de ejecución

Los plugins nativos de OpenClaw se ejecutan **dentro del proceso** con el Gateway. No están
aislados. Un plugin nativo cargado tiene el mismo límite de confianza a nivel de proceso que
el código del core.

Implicaciones:

- un plugin nativo puede registrar herramientas, manejadores de red, hooks y servicios
- un error en un plugin nativo puede hacer caer o desestabilizar el gateway
- un plugin nativo malicioso equivale a ejecución arbitraria de código dentro
  del proceso de OpenClaw

Los bundles compatibles son más seguros por defecto porque OpenClaw actualmente los trata
como paquetes de metadatos/contenido. En las versiones actuales, eso significa principalmente
Skills integradas.

Usa allowlists y rutas explícitas de instalación/carga para plugins no integrados. Trata
los plugins del espacio de trabajo como código de desarrollo, no como valores predeterminados de producción.

Para nombres de paquetes de espacios de trabajo integrados, mantén el id del plugin anclado en el
nombre npm: `@openclaw/<id>` de forma predeterminada, o un sufijo tipado aprobado como
`-provider`, `-plugin`, `-speech`, `-sandbox` o `-media-understanding` cuando
el paquete exponga intencionalmente un rol de plugin más específico.

Nota importante de confianza:

- `plugins.allow` confía en **ids de plugin**, no en el origen de la procedencia.
- Un plugin del espacio de trabajo con el mismo id que un plugin integrado, intencionalmente oculta
  la copia integrada cuando ese plugin del espacio de trabajo está habilitado/incluido en allowlist.
- Esto es normal y útil para desarrollo local, pruebas de parches y hotfixes.

## Límite de exportación

OpenClaw exporta capacidades, no conveniencias de implementación.

Mantén público el registro de capacidades. Reduce exportaciones auxiliares que no sean contratos:

- subpaths auxiliares específicos de plugins integrados
- subpaths de infraestructura del entorno de ejecución no destinados a API pública
- asistentes de conveniencia específicos del proveedor
- asistentes de configuración/onboarding que son detalles de implementación

Algunos subpaths auxiliares de plugins integrados siguen presentes en el mapa de exportaciones
generado del SDK por compatibilidad y mantenimiento de plugins integrados. Ejemplos actuales incluyen
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` y varias costuras `plugin-sdk/matrix*`. Trátalos como
exportaciones reservadas y de detalle de implementación, no como el patrón de SDK recomendado para
nuevos plugins de terceros.

## Canal de carga

En el arranque, OpenClaw hace aproximadamente esto:

1. descubrir raíces candidatas de plugins
2. leer manifests nativos o de bundles compatibles y metadatos de paquetes
3. rechazar candidatos inseguros
4. normalizar la configuración de plugins (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decidir la habilitación de cada candidato
6. cargar módulos nativos habilitados mediante jiti
7. llamar a los hooks nativos `register(api)` (o `activate(api)` — un alias legacy) y recopilar registros en el registro de plugins
8. exponer el registro a superficies de comandos/entorno de ejecución

<Note>
`activate` es un alias legacy de `register`: el cargador resuelve el que esté presente (`def.register ?? def.activate`) y lo llama en el mismo punto. Todos los plugins integrados usan `register`; prefiere `register` para plugins nuevos.
</Note>

Las puertas de seguridad ocurren **antes** de la ejecución en tiempo de ejecución. Los candidatos se bloquean
cuando la entrada escapa de la raíz del plugin, la ruta es escribible globalmente o la
propiedad de la ruta parece sospechosa para plugins no integrados.

### Comportamiento orientado al manifest

El manifest es la fuente de verdad del plano de control. OpenClaw lo usa para:

- identificar el plugin
- descubrir canales/Skills/schema de configuración declarados o capacidades del bundle
- validar `plugins.entries.<id>.config`
- ampliar etiquetas/placeholders de Control UI
- mostrar metadatos de instalación/catálogo

Para plugins nativos, el módulo de entorno de ejecución es la parte del plano de datos. Registra
el comportamiento real, como hooks, herramientas, comandos o flujos de proveedor.

### Qué almacena en caché el cargador

OpenClaw mantiene cachés breves dentro del proceso para:

- resultados de descubrimiento
- datos de registro de manifests
- registros de plugins cargados

Estas cachés reducen los picos de inicio y la sobrecarga de comandos repetidos. Es seguro
pensar en ellas como cachés de rendimiento de vida corta, no como persistencia.

Nota de rendimiento:

- Configura `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` o
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` para desactivar estas cachés.
- Ajusta las ventanas de caché con `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` y
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Modelo de registro

Los plugins cargados no mutan directamente variables globales aleatorias del core. Se registran en un
registro central de plugins.

El registro hace seguimiento de:

- registros de plugins (identidad, origen, procedencia, estado, diagnósticos)
- herramientas
- hooks legacy y hooks tipados
- canales
- proveedores
- manejadores RPC del gateway
- rutas HTTP
- registradores CLI
- servicios en segundo plano
- comandos propiedad del plugin

Luego, las funciones del core leen de ese registro en lugar de hablar con módulos del plugin
directamente. Esto mantiene la carga en una sola dirección:

- módulo del plugin -> registro en el registro
- entorno de ejecución del core -> consumo del registro

Esa separación importa para la mantenibilidad. Significa que la mayoría de las superficies del core solo
necesitan un único punto de integración: “leer el registro”, no “hacer un caso especial para cada módulo de plugin”.

## Callbacks de vinculación de conversación

Los plugins que vinculan una conversación pueden reaccionar cuando se resuelve una aprobación.

Usa `api.onConversationBindingResolved(...)` para recibir un callback después de que una solicitud de vinculación sea aprobada o denegada:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // Ahora existe una vinculación para este plugin + conversación.
        console.log(event.binding?.conversationId);
        return;
      }

      // La solicitud fue denegada; borra cualquier estado local pendiente.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Campos de la carga útil del callback:

- `status`: `"approved"` o `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` o `"deny"`
- `binding`: la vinculación resuelta para solicitudes aprobadas
- `request`: el resumen de la solicitud original, pista de desacoplamiento, id del remitente y
  metadatos de la conversación

Este callback es solo de notificación. No cambia quién tiene permitido vincular una
conversación y se ejecuta después de que termine el manejo de aprobación del core.

## Hooks de entorno de ejecución de proveedores

Los plugins de proveedores ahora tienen dos capas:

- metadatos del manifest: `providerAuthEnvVars` para búsqueda barata de autenticación del proveedor por entorno
  antes de cargar el entorno de ejecución, `channelEnvVars` para búsqueda barata de entorno/configuración del canal
  antes de cargar el entorno de ejecución, además de `providerAuthChoices` para etiquetas
  baratas de onboarding/elección de autenticación y metadatos de flags de CLI antes de cargar el entorno de ejecución
- hooks en tiempo de configuración: `catalog` / `discovery` legacy más `applyConfigDefaults`
- hooks en tiempo de ejecución: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw sigue poseyendo el bucle genérico del agente, el failover, el manejo de transcripciones y la
política de herramientas. Estos hooks son la superficie de extensión para el comportamiento específico del proveedor sin
necesidad de un transporte de inferencia completamente personalizado.

Usa el `providerAuthEnvVars` del manifest cuando el proveedor tiene credenciales basadas en entorno
que las rutas genéricas de autenticación/estado/selector de modelos deben ver sin cargar el entorno de ejecución del plugin.
Usa `providerAuthChoices` del manifest cuando las superficies de CLI de onboarding/elección de autenticación
deben conocer el id de elección del proveedor, etiquetas de grupo y la conexión simple de autenticación
con un único flag sin cargar el entorno de ejecución del proveedor. Mantén `envVars` del entorno de ejecución del proveedor para
sugerencias orientadas al operador, como etiquetas de onboarding o variables de configuración
de client-id/client-secret de OAuth.

Usa `channelEnvVars` del manifest cuando un canal tenga autenticación o configuración impulsada por entorno y
las rutas genéricas de respaldo de shell-env, comprobaciones de config/status o prompts de configuración deban verla
sin cargar el entorno de ejecución del canal.

### Orden y uso de hooks

Para plugins de modelos/proveedores, OpenClaw llama a los hooks aproximadamente en este orden.
La columna “Cuándo usarlo” es la guía rápida de decisión.

| #   | Hook                              | Qué hace                                                                                                       | Cuándo usarlo                                                                                                                              |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | Publica la configuración del proveedor en `models.providers` durante la generación de `models.json`           | El proveedor posee un catálogo o valores predeterminados de URL base                                                                       |
| 2   | `applyConfigDefaults`             | Aplica valores predeterminados globales propiedad del proveedor durante la materialización de la configuración | Los valores predeterminados dependen del modo de autenticación, el entorno o la semántica de la familia de modelos del proveedor          |
| --  | _(búsqueda de modelo integrada)_  | OpenClaw prueba primero la ruta normal de registro/catálogo                                                    | _(no es un hook de plugin)_                                                                                                                |
| 3   | `normalizeModelId`                | Normaliza alias legacy o de vista previa de ids de modelo antes de la búsqueda                                | El proveedor posee la limpieza de alias antes de la resolución canónica del modelo                                                         |
| 4   | `normalizeTransport`              | Normaliza `api` / `baseUrl` de una familia de proveedores antes del ensamblado genérico del modelo            | El proveedor posee la limpieza del transporte para ids de proveedor personalizados en la misma familia de transporte                      |
| 5   | `normalizeConfig`                 | Normaliza `models.providers.<id>` antes de la resolución en tiempo de ejecución/del proveedor                 | El proveedor necesita limpieza de configuración que debe vivir con el plugin; los asistentes integrados de la familia Google también respaldan entradas compatibles de configuración de Google |
| 6   | `applyNativeStreamingUsageCompat` | Aplica reescrituras de compatibilidad de uso de streaming nativo a proveedores de configuración               | El proveedor necesita correcciones de metadatos de uso nativo de streaming impulsadas por endpoint                                         |
| 7   | `resolveConfigApiKey`             | Resuelve autenticación de marcador de entorno para proveedores de configuración antes de cargar la autenticación del entorno de ejecución | El proveedor tiene resolución propiedad del proveedor para claves de API con marcador de entorno; `amazon-bedrock` también tiene aquí un resolvedor integrado de marcador de entorno AWS |
| 8   | `resolveSyntheticAuth`            | Expone autenticación local/self-hosted o respaldada por configuración sin persistir texto plano               | El proveedor puede operar con un marcador de credencial sintética/local                                                                    |
| 9   | `resolveExternalAuthProfiles`     | Superpone perfiles de autenticación externos propiedad del proveedor; la `persistence` predeterminada es `runtime-only` para credenciales propiedad de CLI/app | El proveedor reutiliza credenciales de autenticación externas sin persistir refresh tokens copiados                                       |
| 10  | `shouldDeferSyntheticProfileAuth` | Relega placeholders sintéticos almacenados detrás de autenticación respaldada por entorno/configuración       | El proveedor almacena perfiles placeholder sintéticos que no deberían ganar precedencia                                                    |
| 11  | `resolveDynamicModel`             | Respaldo sincrónico para ids de modelo propiedad del proveedor que aún no están en el registro local          | El proveedor acepta ids arbitrarios de modelos upstream                                                                                    |
| 12  | `prepareDynamicModel`             | Calentamiento asíncrono y luego `resolveDynamicModel` se ejecuta otra vez                                     | El proveedor necesita metadatos de red antes de resolver ids desconocidos                                                                  |
| 13  | `normalizeResolvedModel`          | Reescritura final antes de que el ejecutor embebido use el modelo resuelto                                    | El proveedor necesita reescrituras de transporte, pero sigue usando un transporte del core                                                |
| 14  | `contributeResolvedModelCompat`   | Aporta flags de compatibilidad para modelos del proveedor detrás de otro transporte compatible                 | El proveedor reconoce sus propios modelos en transportes proxy sin asumir el control del proveedor                                        |
| 15  | `capabilities`                    | Metadatos de transcripción/herramientas propiedad del proveedor usados por lógica compartida del core         | El proveedor necesita particularidades de transcripción/familia de proveedor                                                               |
| 16  | `normalizeToolSchemas`            | Normaliza schemas de herramientas antes de que el ejecutor embebido los vea                                   | El proveedor necesita limpieza de schemas por familia de transporte                                                                        |
| 17  | `inspectToolSchemas`              | Expone diagnósticos de schema propiedad del proveedor después de la normalización                             | El proveedor quiere advertencias de palabras clave sin enseñar reglas específicas del proveedor al core                                   |
| 18  | `resolveReasoningOutputMode`      | Selecciona contrato de salida de razonamiento nativo frente a etiquetado                                      | El proveedor necesita razonamiento etiquetado/salida final en lugar de campos nativos                                                     |
| 19  | `prepareExtraParams`              | Normalización de parámetros de solicitud antes de los wrappers genéricos de opciones de stream                | El proveedor necesita parámetros de solicitud predeterminados o limpieza de parámetros por proveedor                                       |
| 20  | `createStreamFn`                  | Reemplaza por completo la ruta normal de stream con un transporte personalizado                               | El proveedor necesita un protocolo cableado personalizado, no solo un wrapper                                                              |
| 21  | `wrapStreamFn`                    | Wrapper del stream después de aplicar wrappers genéricos                                                      | El proveedor necesita wrappers de compatibilidad de encabezados/cuerpo/modelo de solicitud sin un transporte personalizado                |
| 22  | `resolveTransportTurnState`       | Adjunta encabezados nativos por turno o metadatos al transporte                                               | El proveedor quiere que los transportes genéricos envíen identidad de turno nativa del proveedor                                          |
| 23  | `resolveWebSocketSessionPolicy`   | Adjunta encabezados nativos de WebSocket o política de enfriamiento de sesión                                 | El proveedor quiere que los transportes genéricos de WS ajusten encabezados de sesión o política de respaldo                              |
| 24  | `formatApiKey`                    | Formateador de perfil de autenticación: el perfil almacenado se convierte en la cadena `apiKey` del entorno de ejecución | El proveedor almacena metadatos extra de autenticación y necesita una forma personalizada del token en tiempo de ejecución                |
| 25  | `refreshOAuth`                    | Anulación de refresco OAuth para endpoints de refresco personalizados o política de error de refresco         | El proveedor no encaja en los refrescadores compartidos `pi-ai`                                                                            |
| 26  | `buildAuthDoctorHint`             | Sugerencia de reparación anexada cuando falla el refresco OAuth                                               | El proveedor necesita una guía de reparación de autenticación propiedad del proveedor tras un fallo de refresco                            |
| 27  | `matchesContextOverflowError`     | Comparador propiedad del proveedor para desbordamiento de la ventana de contexto                              | El proveedor tiene errores de desbordamiento sin procesar que las heurísticas genéricas no detectarían                                    |
| 28  | `classifyFailoverReason`          | Clasificación propiedad del proveedor de la razón de failover                                                 | El proveedor puede mapear errores sin procesar de API/transporte a rate-limit/sobrecarga/etc.                                             |
| 29  | `isCacheTtlEligible`              | Política de caché de prompts para proveedores proxy/backhaul                                                  | El proveedor necesita una puerta TTL de caché específica de proxy                                                                          |
| 30  | `buildMissingAuthMessage`         | Sustituto del mensaje genérico de recuperación por falta de autenticación                                     | El proveedor necesita una sugerencia específica del proveedor para recuperar autenticación faltante                                        |
| 31  | `suppressBuiltInModel`            | Supresión de modelo upstream obsoleto con sugerencia opcional orientada al usuario                            | El proveedor necesita ocultar filas obsoletas upstream o reemplazarlas por una sugerencia del proveedor                                   |
| 32  | `augmentModelCatalog`             | Filas sintéticas/finales de catálogo añadidas tras el descubrimiento                                          | El proveedor necesita filas sintéticas de compatibilidad futura en `models list` y selectores                                             |
| 33  | `isBinaryThinking`                | Conmutador de razonamiento encendido/apagado para proveedores de razonamiento binario                         | El proveedor solo expone razonamiento binario activado/desactivado                                                                         |
| 34  | `supportsXHighThinking`           | Compatibilidad con razonamiento `xhigh` para modelos seleccionados                                            | El proveedor quiere `xhigh` solo en un subconjunto de modelos                                                                              |
| 35  | `resolveDefaultThinkingLevel`     | Nivel predeterminado de `/think` para una familia concreta de modelos                                         | El proveedor posee la política predeterminada de `/think` para una familia de modelos                                                     |
| 36  | `isModernModelRef`                | Comparador de modelo moderno para filtros de perfiles en vivo y selección de smoke                            | El proveedor posee la coincidencia de modelos preferidos para live/smoke                                                                   |
| 37  | `prepareRuntimeAuth`              | Intercambia una credencial configurada por el token/clave real del entorno de ejecución justo antes de la inferencia | El proveedor necesita un intercambio de token o una credencial efímera para la solicitud                                                  |
| 38  | `resolveUsageAuth`                | Resuelve credenciales de uso/facturación para `/usage` y superficies de estado relacionadas                   | El proveedor necesita análisis personalizado de token de uso/cuota o una credencial de uso distinta                                       |
| 39  | `fetchUsageSnapshot`              | Obtiene y normaliza instantáneas de uso/cuota específicas del proveedor tras resolver la autenticación        | El proveedor necesita un endpoint de uso específico del proveedor o un analizador de payload                                               |
| 40  | `createEmbeddingProvider`         | Construye un adaptador de embeddings propiedad del proveedor para memoria/búsqueda                            | El comportamiento de embeddings de memoria debe vivir con el plugin del proveedor                                                          |
| 41  | `buildReplayPolicy`               | Devuelve una política de repetición que controla el manejo de transcripciones para el proveedor               | El proveedor necesita una política personalizada de transcripción (por ejemplo, eliminar bloques de thinking)                             |
| 42  | `sanitizeReplayHistory`           | Reescribe el historial de repetición tras la limpieza genérica de transcripciones                             | El proveedor necesita reescrituras específicas del proveedor más allá de los asistentes compartidos de compactación                       |
| 43  | `validateReplayTurns`             | Validación o remodelado final de turnos de repetición antes del ejecutor embebido                             | El transporte del proveedor necesita una validación de turnos más estricta tras la sanitización genérica                                  |
| 44  | `onModelSelected`                 | Ejecuta efectos secundarios propiedad del proveedor tras la selección                                         | El proveedor necesita telemetría o estado propio del proveedor cuando un modelo pasa a estar activo                                       |

`normalizeModelId`, `normalizeTransport` y `normalizeConfig` comprueban primero el
plugin de proveedor coincidente y luego recorren otros plugins de proveedor con capacidad de hooks
hasta que uno realmente cambie el id del modelo o el transporte/configuración. Eso mantiene
funcionando los shim de alias/compatibilidad de proveedor sin exigir que quien llama sepa qué
plugin integrado posee la reescritura. Si ningún hook de proveedor reescribe una entrada compatible
de configuración de la familia Google, el normalizador integrado de configuración de Google
sigue aplicando esa limpieza de compatibilidad.

Si el proveedor necesita un protocolo cableado completamente personalizado o un ejecutor de solicitudes
personalizado, eso es una clase distinta de extensión. Estos hooks son para comportamiento de proveedor
que sigue ejecutándose en el bucle normal de inferencia de OpenClaw.

### Ejemplo de proveedor

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Ejemplos integrados

- Anthropic usa `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  y `wrapStreamFn` porque posee compatibilidad futura con Claude 4.6,
  sugerencias de familia de proveedor, guía de reparación de autenticación, integración con endpoint de uso,
  elegibilidad de caché de prompts, valores predeterminados de configuración con reconocimiento de autenticación, política predeterminada/adaptativa de thinking para Claude,
  y modelado de stream específico de Anthropic para encabezados beta,
  `/fast` / `serviceTier` y `context1m`.
- Los asistentes de stream específicos de Claude en Anthropic permanecen por ahora en la
  costura pública `api.ts` / `contract-api.ts` del propio plugin integrado.
  Esa superficie del paquete exporta `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` y los builders de wrappers de Anthropic
  de nivel inferior, en lugar de ampliar el SDK genérico en torno a las reglas de encabezados beta de un solo
  proveedor.
- OpenAI usa `resolveDynamicModel`, `normalizeResolvedModel` y
  `capabilities` además de `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` e `isModernModelRef`
  porque posee compatibilidad futura con GPT-5.4, la normalización directa
  `openai-completions` -> `openai-responses`, sugerencias de autenticación con reconocimiento de Codex,
  supresión de Spark, filas sintéticas de lista de OpenAI y la política de thinking/modelo en vivo de GPT-5; la familia de stream `openai-responses-defaults` posee los wrappers nativos compartidos de OpenAI Responses para encabezados de atribución,
  `/fast`/`serviceTier`, verbosidad de texto, búsqueda web nativa de Codex,
  modelado de payload de compatibilidad de razonamiento y gestión de contexto de Responses.
- OpenRouter usa `catalog` además de `resolveDynamicModel` y
  `prepareDynamicModel` porque el proveedor es de paso y puede exponer nuevos
  ids de modelo antes de que se actualice el catálogo estático de OpenClaw; también usa
  `capabilities`, `wrapStreamFn` e `isCacheTtlEligible` para mantener
  encabezados de solicitud específicos del proveedor, metadatos de enrutamiento, parches de razonamiento y política de caché de prompts fuera del core. Su política de repetición viene de la
  familia `passthrough-gemini`, mientras que la familia de stream `openrouter-thinking`
  posee la inyección de razonamiento del proxy y los omisos de modelo no compatible / `auto`.
- GitHub Copilot usa `catalog`, `auth`, `resolveDynamicModel` y
  `capabilities` además de `prepareRuntimeAuth` y `fetchUsageSnapshot` porque
  necesita inicio de sesión de dispositivo propiedad del proveedor, comportamiento de respaldo de modelos, peculiaridades de transcripción de Claude, un intercambio
  de token GitHub -> token Copilot y un endpoint de uso propiedad del proveedor.
- OpenAI Codex usa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` y `augmentModelCatalog` además de
  `prepareExtraParams`, `resolveUsageAuth` y `fetchUsageSnapshot` porque
  sigue ejecutándose sobre transportes OpenAI del core pero posee su normalización
  de transporte/base URL, política de respaldo de refresco OAuth, elección predeterminada de transporte,
  filas sintéticas de catálogo de Codex e integración con endpoint de uso de ChatGPT; comparte la misma familia de stream `openai-responses-defaults` que OpenAI directo.
- Google AI Studio y Gemini CLI OAuth usan `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` e `isModernModelRef` porque la
  familia de repetición `google-gemini` posee respaldo de compatibilidad futura de Gemini 3.1,
  validación nativa de repetición de Gemini, sanitización de repetición de bootstrap,
  modo etiquetado de salida de razonamiento y coincidencia de modelo moderno, mientras que la
  familia de stream `google-thinking` posee la normalización del payload de thinking de Gemini;
  Gemini CLI OAuth también usa `formatApiKey`, `resolveUsageAuth` y
  `fetchUsageSnapshot` para formateo de token, análisis de token y conexión con endpoint de cuota.
- Anthropic Vertex usa `buildReplayPolicy` mediante la
  familia de repetición `anthropic-by-model` para que la limpieza de repetición específica de Claude siga
  acotada a ids de Claude en lugar de a cada transporte `anthropic-messages`.
- Amazon Bedrock usa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` y `resolveDefaultThinkingLevel` porque posee la clasificación específica de Bedrock
  para errores de limitación/no listo/desbordamiento de contexto
  en tráfico Anthropic-on-Bedrock; su política de repetición sigue compartiendo la misma guarda
  `anthropic-by-model` solo para Claude.
- OpenRouter, Kilocode, Opencode y Opencode Go usan `buildReplayPolicy`
  mediante la familia de repetición `passthrough-gemini` porque hacen proxy de modelos Gemini
  a través de transportes compatibles con OpenAI y necesitan sanitización de firma de pensamiento
  de Gemini sin validación nativa de repetición de Gemini ni reescrituras de bootstrap.
- MiniMax usa `buildReplayPolicy` mediante la
  familia de repetición `hybrid-anthropic-openai` porque un proveedor posee tanto semántica de
  mensajes Anthropic como semántica compatible con OpenAI; mantiene la eliminación
  de bloques thinking solo para Claude en el lado Anthropic mientras anula el modo de salida de razonamiento de vuelta a nativo, y la familia de stream `minimax-fast-mode` posee las reescrituras de modelos fast-mode en la ruta de stream compartida.
- Moonshot usa `catalog` más `wrapStreamFn` porque sigue usando el transporte
  compartido de OpenAI pero necesita normalización del payload de thinking propiedad del proveedor; la
  familia de stream `moonshot-thinking` mapea la configuración más el estado `/think` a su payload binario nativo de thinking.
- Kilocode usa `catalog`, `capabilities`, `wrapStreamFn` e
  `isCacheTtlEligible` porque necesita encabezados de solicitud propiedad del proveedor,
  normalización de payload de razonamiento, sugerencias de transcripción de Gemini y
  puerta TTL de caché de Anthropic; la familia de stream `kilocode-thinking` mantiene la
  inyección de thinking de Kilo en la ruta de stream proxy compartida mientras omite `kilo/auto` y
  otros ids de modelos proxy que no admiten payloads explícitos de razonamiento.
- Z.AI usa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` y `fetchUsageSnapshot` porque posee respaldo GLM-5,
  valores predeterminados de `tool_stream`, UX de thinking binario, coincidencia de modelo moderno y tanto
  autenticación de uso como obtención de cuota; la familia de stream `tool-stream-default-on` mantiene
  el wrapper predeterminado de `tool_stream` fuera del pegamento manuscrito por proveedor.
- xAI usa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` e `isModernModelRef`
  porque posee la normalización nativa del transporte xAI Responses, reescrituras de alias fast-mode de Grok, `tool_stream` predeterminado, limpieza de herramientas estrictas / payload de razonamiento,
  reutilización de autenticación de respaldo para herramientas propiedad del plugin, resolución futura de
  modelos Grok y parches de compatibilidad propiedad del proveedor como el perfil de schema de herramientas de xAI,
  palabras clave de schema no compatibles, `web_search` nativo y decodificación de argumentos
  de llamadas a herramientas con entidades HTML.
- Mistral, OpenCode Zen y OpenCode Go usan solo `capabilities` para mantener
  particularidades de transcripción/herramientas fuera del core.
- Los proveedores integrados solo de catálogo, como `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` y `volcengine`, usan
  solo `catalog`.
- Qwen usa `catalog` para su proveedor de texto además de registros compartidos de comprensión de medios y
  generación de video para sus superficies multimodales.
- MiniMax y Xiaomi usan `catalog` más hooks de uso porque su comportamiento `/usage`
  es propiedad del plugin aunque la inferencia siga ejecutándose mediante los transportes compartidos.

## Asistentes de entorno de ejecución

Los plugins pueden acceder a asistentes seleccionados del core mediante `api.runtime`. Para TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Notas:

- `textToSpeech` devuelve el payload de salida TTS normal del core para superficies de archivo/nota de voz.
- Usa la configuración central `messages.tts` y la selección de proveedor.
- Devuelve buffer de audio PCM + frecuencia de muestreo. Los plugins deben remuestrear/codificar para proveedores.
- `listVoices` es opcional por proveedor. Úsalo para selectores de voz o flujos de configuración propiedad del proveedor.
- Las listas de voces pueden incluir metadatos más ricos, como configuración regional, género y etiquetas de personalidad para selectores con reconocimiento del proveedor.
- OpenAI y ElevenLabs admiten telefonía hoy. Microsoft no.

Los plugins también pueden registrar proveedores de voz mediante `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Notas:

- Mantén la política TTS, el respaldo y la entrega de respuestas en el core.
- Usa proveedores de voz para comportamiento de síntesis propiedad del proveedor.
- La entrada legacy `edge` de Microsoft se normaliza al id de proveedor `microsoft`.
- El modelo de propiedad preferido está orientado a la empresa: un plugin de proveedor puede poseer
  texto, voz, imagen y futuros proveedores de medios a medida que OpenClaw añade esos contratos
  de capacidad.

Para comprensión de imagen/audio/video, los plugins registran un único proveedor tipado de
comprensión de medios en lugar de una bolsa genérica clave/valor:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Notas:

- Mantén la orquestación, el respaldo, la configuración y la conexión de canales en el core.
- Mantén el comportamiento del proveedor en el plugin del proveedor.
- La expansión aditiva debe seguir tipada: nuevos métodos opcionales, nuevos campos opcionales
  de resultado, nuevas capacidades opcionales.
- La generación de video ya sigue el mismo patrón:
  - el core posee el contrato de capacidad y el asistente de entorno de ejecución
  - los plugins de proveedor registran `api.registerVideoGenerationProvider(...)`
  - los plugins de funcionalidad/canal consumen `api.runtime.videoGeneration.*`

Para los asistentes de entorno de ejecución de comprensión de medios, los plugins pueden llamar a:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Para transcripción de audio, los plugins pueden usar el entorno de ejecución de comprensión de medios
o el alias STT anterior:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Opcional cuando el MIME no se puede inferir de forma fiable:
  mime: "audio/ogg",
});
```

Notas:

- `api.runtime.mediaUnderstanding.*` es la superficie compartida preferida para
  comprensión de imagen/audio/video.
- Usa la configuración central de audio de comprensión de medios (`tools.media.audio`) y el orden de respaldo del proveedor.
- Devuelve `{ text: undefined }` cuando no se produce salida de transcripción (por ejemplo entrada omitida/no compatible).
- `api.runtime.stt.transcribeAudioFile(...)` se mantiene como alias de compatibilidad.

Los plugins también pueden lanzar ejecuciones de subagente en segundo plano mediante `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Notas:

- `provider` y `model` son anulaciones opcionales por ejecución, no cambios persistentes de sesión.
- OpenClaw solo respeta esos campos de anulación para llamadores de confianza.
- Para ejecuciones de respaldo propiedad del plugin, los operadores deben optar por ello con `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Usa `plugins.entries.<id>.subagent.allowedModels` para restringir plugins confiables a objetivos canónicos concretos `provider/model`, o `"*"` para permitir cualquier objetivo explícitamente.
- Las ejecuciones de subagente de plugins no confiables siguen funcionando, pero las solicitudes de anulación se rechazan en lugar de recurrir silenciosamente a un respaldo.

Para búsqueda web, los plugins pueden consumir el asistente compartido de entorno de ejecución en lugar de
acceder a la conexión de herramientas del agente:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Los plugins también pueden registrar proveedores de búsqueda web mediante
`api.registerWebSearchProvider(...)`.

Notas:

- Mantén en el core la selección de proveedor, resolución de credenciales y semántica compartida de solicitudes.
- Usa proveedores de búsqueda web para transportes de búsqueda específicos del proveedor.
- `api.runtime.webSearch.*` es la superficie compartida preferida para plugins de funcionalidad/canal que necesitan comportamiento de búsqueda sin depender del wrapper de herramientas del agente.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: genera una imagen usando la cadena configurada de proveedores de generación de imágenes.
- `listProviders(...)`: enumera los proveedores disponibles de generación de imágenes y sus capacidades.

## Rutas HTTP del Gateway

Los plugins pueden exponer endpoints HTTP con `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Campos de la ruta:

- `path`: ruta bajo el servidor HTTP del gateway.
- `auth`: obligatorio. Usa `"gateway"` para requerir autenticación normal del gateway, o `"plugin"` para autenticación gestionada por plugin/verificación de webhook.
- `match`: opcional. `"exact"` (predeterminado) o `"prefix"`.
- `replaceExisting`: opcional. Permite que el mismo plugin reemplace su propio registro de ruta existente.
- `handler`: devuelve `true` cuando la ruta manejó la solicitud.

Notas:

- `api.registerHttpHandler(...)` fue eliminado y provocará un error de carga del plugin. Usa `api.registerHttpRoute(...)` en su lugar.
- Las rutas de plugin deben declarar `auth` explícitamente.
- Los conflictos exactos `path + match` se rechazan a menos que `replaceExisting: true`, y un plugin no puede reemplazar la ruta de otro plugin.
- Las rutas superpuestas con distintos niveles de `auth` se rechazan. Mantén las cadenas de caída `exact`/`prefix` solo en el mismo nivel de autenticación.
- Las rutas `auth: "plugin"` **no** reciben automáticamente alcances de entorno de ejecución de operador. Son para webhooks/verificación de firmas gestionados por plugin, no para llamadas privilegiadas de asistencia del Gateway.
- Las rutas `auth: "gateway"` se ejecutan dentro de un alcance de entorno de ejecución de solicitud del Gateway, pero ese alcance es intencionadamente conservador:
  - la autenticación bearer con secreto compartido (`gateway.auth.mode = "token"` / `"password"`) mantiene los alcances de entorno de ejecución de rutas de plugin fijados a `operator.write`, incluso si el llamador envía `x-openclaw-scopes`
  - los modos HTTP de confianza con identidad (por ejemplo `trusted-proxy` o `gateway.auth.mode = "none"` en un ingreso privado) respetan `x-openclaw-scopes` solo cuando el encabezado está presente explícitamente
  - si `x-openclaw-scopes` está ausente en esas solicitudes de rutas de plugin con identidad, el alcance del entorno de ejecución vuelve a `operator.write`
- Regla práctica: no asumas que una ruta de plugin con autenticación de gateway es una superficie de administración implícita. Si tu ruta necesita comportamiento solo de administración, exige un modo de autenticación con identidad y documenta el contrato explícito del encabezado `x-openclaw-scopes`.

## Rutas de importación del Plugin SDK

Usa subpaths del SDK en lugar de la importación monolítica `openclaw/plugin-sdk` al
crear plugins:

- `openclaw/plugin-sdk/plugin-entry` para primitivas de registro de plugins.
- `openclaw/plugin-sdk/core` para el contrato compartido genérico orientado al plugin.
- `openclaw/plugin-sdk/config-schema` para la exportación del schema Zod raíz de `openclaw.json`
  (`OpenClawSchema`).
- Primitivas de canal estables como `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` y
  `openclaw/plugin-sdk/webhook-ingress` para conexión compartida de
  configuración/autenticación/respuesta/webhook. `channel-inbound` es el hogar compartido de debounce, coincidencia de menciones,
  formato de envelope y asistentes de contexto de envelope entrante.
  `channel-setup` es la costura de configuración estrecha y opcional para instalación.
  `setup-runtime` es la superficie de configuración segura para el entorno de ejecución usada por `setupEntry` /
  inicio diferido, incluidos los adaptadores de parches de configuración seguros para importación.
  `setup-adapter-runtime` es la costura del adaptador de configuración de cuentas con reconocimiento del entorno.
  `setup-tools` es la pequeña costura auxiliar de CLI/archivo/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Subpaths de dominio como `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` y
  `openclaw/plugin-sdk/directory-runtime` para asistentes compartidos de entorno de ejecución/configuración.
  `telegram-command-config` es la costura pública estrecha para la normalización/validación de comandos personalizados de Telegram y sigue disponible incluso si la superficie de contrato integrada de Telegram no está temporalmente disponible.
  `text-runtime` es la costura compartida de texto/Markdown/registro, incluida la
  eliminación de texto visible para el asistente, asistentes de renderizado/fragmentación de Markdown, asistentes de redacción, asistentes de etiquetas de directivas y utilidades de texto seguro.
- Las costuras de canal específicas de aprobación deben preferir un único contrato `approvalCapability`
  en el plugin. El core entonces lee autenticación, entrega, renderizado y comportamiento de
  enrutamiento nativo de la aprobación a través de esa única capacidad, en lugar de mezclar
  comportamiento de aprobación en campos del plugin no relacionados.
- `openclaw/plugin-sdk/channel-runtime` está obsoleto y se mantiene solo como
  shim de compatibilidad para plugins antiguos. El código nuevo debe importar en su lugar las primitivas genéricas más estrechas, y el código del repositorio no debe añadir nuevas importaciones del shim.
- Los elementos internos de extensiones integradas siguen siendo privados. Los plugins externos deben usar solo subpaths `openclaw/plugin-sdk/*`. El código/pruebas del core de OpenClaw puede usar los puntos de entrada públicos del repositorio bajo la raíz de un paquete de plugin, como `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` y archivos de alcance estrecho como
  `login-qr-api.js`. Nunca importes el `src/*` de un paquete de plugin desde el core o desde otra extensión.
- División de puntos de entrada del repositorio:
  `<plugin-package-root>/api.js` es el barrel de asistentes/tipos,
  `<plugin-package-root>/runtime-api.js` es el barrel solo de entorno de ejecución,
  `<plugin-package-root>/index.js` es la entrada del plugin integrado,
  y `<plugin-package-root>/setup-entry.js` es la entrada del plugin de configuración.
- Ejemplos actuales de proveedores integrados:
  - Anthropic usa `api.js` / `contract-api.js` para asistentes de stream de Claude como
    `wrapAnthropicProviderStream`, asistentes de encabezados beta y análisis de `service_tier`.
  - OpenAI usa `api.js` para builders de proveedores, asistentes de modelo predeterminado y builders de proveedor en tiempo real.
  - OpenRouter usa `api.js` para su builder de proveedor además de asistentes de onboarding/configuración,
    mientras que `register.runtime.js` puede seguir reexportando asistentes genéricos
    `plugin-sdk/provider-stream` para uso local del repositorio.
- Los puntos de entrada públicos cargados mediante fachada prefieren la instantánea de configuración activa del entorno de ejecución cuando existe y, de lo contrario, recurren al archivo de configuración resuelto en disco cuando OpenClaw aún no está sirviendo una instantánea del entorno de ejecución.
- Las primitivas compartidas genéricas siguen siendo el contrato público preferido del SDK. Todavía existe un pequeño conjunto reservado de costuras auxiliares con marca de canal por compatibilidad. Trátalas como costuras de mantenimiento/compatibilidad integrada, no como nuevos objetivos de importación de terceros; los nuevos contratos compartidos entre canales deben seguir aterrizando en subpaths genéricos `plugin-sdk/*` o en los barrels locales `api.js` /
  `runtime-api.js` del plugin.

Nota de compatibilidad:

- Evita el barrel raíz `openclaw/plugin-sdk` en código nuevo.
- Prefiere primero las primitivas estables y estrechas. Los subpaths más recientes de setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool son el contrato previsto para trabajo nuevo de plugins
  integrados y externos.
  El análisis/coincidencia de objetivos pertenece a `openclaw/plugin-sdk/channel-targets`.
  Las puertas de acciones de mensajes y los asistentes de id de mensaje de reacción pertenecen a
  `openclaw/plugin-sdk/channel-actions`.
- Los barrels auxiliares específicos de extensiones integradas no son estables por defecto. Si un
  asistente solo lo necesita una extensión integrada, mantenlo detrás de la costura local `api.js` o `runtime-api.js`
  de la extensión, en lugar de promoverlo a `openclaw/plugin-sdk/<extension>`.
- Las nuevas costuras auxiliares compartidas deben ser genéricas, no con marca de canal. El análisis compartido de objetivos pertenece a `openclaw/plugin-sdk/channel-targets`; los
  elementos internos específicos del canal permanecen detrás de la costura local `api.js` o `runtime-api.js`
  del plugin propietario.
- Existen subpaths específicos de capacidad como `image-generation`,
  `media-understanding` y `speech` porque los plugins integrados/nativos los usan hoy. Su presencia no significa por sí sola que cada asistente exportado sea un contrato externo congelado a largo plazo.

## Schemas de la herramienta de mensajes

Los plugins deben poseer contribuciones de schema específicas del canal en
`describeMessageTool(...)`. Mantén los campos específicos del proveedor en el plugin, no en el core compartido.

Para fragmentos compartidos y portables de schema, reutiliza los asistentes genéricos exportados mediante
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` para payloads tipo cuadrícula de botones
- `createMessageToolCardSchema()` para payloads de tarjetas estructuradas

Si una forma de schema solo tiene sentido para un proveedor, defínela en el
propio código fuente de ese plugin en lugar de promoverla al SDK compartido.

## Resolución de objetivos de canal

Los plugins de canal deben poseer la semántica específica del objetivo de canal. Mantén genérico el
host compartido de salida y usa la superficie del adaptador de mensajería para reglas del proveedor:

- `messaging.inferTargetChatType({ to })` decide si un objetivo normalizado
  debe tratarse como `direct`, `group` o `channel` antes de la búsqueda en directorio.
- `messaging.targetResolver.looksLikeId(raw, normalized)` indica al core si una
  entrada debe saltarse directamente a una resolución tipo id en lugar de a una búsqueda en directorio.
- `messaging.targetResolver.resolveTarget(...)` es el respaldo del plugin cuando
  el core necesita una resolución final propiedad del proveedor tras la normalización o tras un fallo del directorio.
- `messaging.resolveOutboundSessionRoute(...)` posee la construcción de ruta de sesión específica del proveedor una vez que se resuelve un objetivo.

División recomendada:

- Usa `inferTargetChatType` para decisiones de categoría que deban ocurrir antes de
  buscar pares/grupos.
- Usa `looksLikeId` para comprobaciones de “tratar esto como un id de objetivo explícito/nativo”.
- Usa `resolveTarget` como respaldo de normalización específica del proveedor, no para
  búsqueda amplia en directorio.
- Mantén ids nativos del proveedor como ids de chat, ids de hilo, JIDs, handles e ids de sala dentro de valores `target` o parámetros específicos del proveedor, no en campos genéricos del SDK.

## Directorios respaldados por configuración

Los plugins que derivan entradas de directorio a partir de configuración deben mantener esa lógica en el
plugin y reutilizar los asistentes compartidos de
`openclaw/plugin-sdk/directory-runtime`.

Usa esto cuando un canal necesite pares/grupos respaldados por configuración, como:

- pares de MD guiados por allowlist
- mapas configurados de canales/grupos
- respaldos estáticos de directorio por ámbito de cuenta

Los asistentes compartidos de `directory-runtime` solo manejan operaciones genéricas:

- filtrado de consultas
- aplicación de límites
- asistentes de deduplicación/normalización
- creación de `ChannelDirectoryEntry[]`

La inspección de cuentas y la normalización de ids específicas del canal deben permanecer en la
implementación del plugin.

## Catálogos de proveedores

Los plugins de proveedores pueden definir catálogos de modelos para inferencia con
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` devuelve la misma forma que OpenClaw escribe en
`models.providers`:

- `{ provider }` para una entrada de proveedor
- `{ providers }` para múltiples entradas de proveedor

Usa `catalog` cuando el plugin posea ids de modelo específicos del proveedor, valores predeterminados de URL base o metadatos de modelos condicionados por autenticación.

`catalog.order` controla cuándo se fusiona el catálogo de un plugin respecto a los proveedores implícitos integrados de OpenClaw:

- `simple`: proveedores simples impulsados por clave de API o entorno
- `profile`: proveedores que aparecen cuando existen perfiles de autenticación
- `paired`: proveedores que sintetizan múltiples entradas de proveedor relacionadas
- `late`: última pasada, después de otros proveedores implícitos

Los proveedores posteriores ganan en caso de colisión de claves, por lo que los plugins pueden anular intencionalmente una entrada de proveedor integrada con el mismo id de proveedor.

Compatibilidad:

- `discovery` sigue funcionando como alias legacy
- si se registran tanto `catalog` como `discovery`, OpenClaw usa `catalog`

## Inspección de canales de solo lectura

Si tu plugin registra un canal, es preferible implementar
`plugin.config.inspectAccount(cfg, accountId)` junto con `resolveAccount(...)`.

Por qué:

- `resolveAccount(...)` es la ruta en tiempo de ejecución. Puede asumir que las credenciales
  están completamente materializadas y puede fallar rápido cuando faltan secretos requeridos.
- Rutas de comandos de solo lectura como `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` y flujos de doctor/reparación de configuración
  no deberían necesitar materializar credenciales del entorno de ejecución solo para
  describir la configuración.

Comportamiento recomendado de `inspectAccount(...)`:

- Devuelve solo el estado descriptivo de la cuenta.
- Conserva `enabled` y `configured`.
- Incluye campos de origen/estado de credenciales cuando sea relevante, como:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- No necesitas devolver valores sin procesar de tokens solo para informar disponibilidad de solo lectura. Devolver `tokenStatus: "available"` (y el campo de origen correspondiente) es suficiente para comandos de tipo estado.
- Usa `configured_unavailable` cuando una credencial esté configurada mediante SecretRef pero
  no esté disponible en la ruta de comando actual.

Eso permite que los comandos de solo lectura informen “configurado pero no disponible en esta ruta de comando” en lugar de fallar o informar incorrectamente que la cuenta no está configurada.

## Paquetes pack

Un directorio de plugin puede incluir un `package.json` con `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Cada entrada se convierte en un plugin. Si el pack enumera múltiples extensiones, el id del plugin
pasa a ser `name/<fileBase>`.

Si tu plugin importa dependencias npm, instálalas en ese directorio para que
`node_modules` esté disponible (`npm install` / `pnpm install`).

Protección de seguridad: cada entrada `openclaw.extensions` debe permanecer dentro del directorio del plugin
después de resolver symlinks. Se rechazan las entradas que escapan del directorio del paquete.

Nota de seguridad: `openclaw plugins install` instala dependencias de plugins con
`npm install --omit=dev --ignore-scripts` (sin scripts de ciclo de vida ni dependencias de desarrollo en tiempo de ejecución). Mantén los árboles de dependencias de plugins como “JS/TS puros” y evita paquetes que requieran compilaciones `postinstall`.

Opcional: `openclaw.setupEntry` puede apuntar a un módulo ligero solo de configuración.
Cuando OpenClaw necesita superficies de configuración para un plugin de canal deshabilitado, o
cuando un plugin de canal está habilitado pero aún sin configurar, carga `setupEntry`
en lugar de la entrada completa del plugin. Esto mantiene más ligero el inicio y la configuración
cuando la entrada principal del plugin también conecta herramientas, hooks u otro código
solo de tiempo de ejecución.

Opcional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
puede hacer que un plugin de canal use la misma ruta `setupEntry` durante la
fase de preescucha del inicio del gateway, incluso cuando el canal ya está configurado.

Úsalo solo cuando `setupEntry` cubra por completo la superficie de inicio que debe existir
antes de que el gateway empiece a escuchar. En la práctica, eso significa que la entrada de configuración
debe registrar toda capacidad propiedad del canal de la que dependa el inicio, como:

- el propio registro del canal
- cualquier ruta HTTP que deba estar disponible antes de que el gateway empiece a escuchar
- cualquier método, herramienta o servicio del gateway que deba existir durante esa misma ventana

Si tu entrada completa sigue poseyendo cualquier capacidad de inicio requerida, no habilites
este flag. Mantén el comportamiento predeterminado del plugin y deja que OpenClaw cargue
la entrada completa durante el inicio.

Los canales integrados también pueden publicar asistentes de superficie de contrato solo de configuración que el core
puede consultar antes de que se cargue el entorno de ejecución completo del canal. La superficie actual de promoción de configuración es:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

El core usa esa superficie cuando necesita promover una configuración legacy de canal de cuenta única
a `channels.<id>.accounts.*` sin cargar la entrada completa del plugin.
Matrix es el ejemplo integrado actual: mueve solo claves de autenticación/bootstrap a una
cuenta promovida con nombre cuando ya existen cuentas con nombre, y puede conservar una
clave configurada de cuenta predeterminada no canónica en lugar de crear siempre
`accounts.default`.

Esos adaptadores de parches de configuración mantienen diferido el descubrimiento de la superficie de contrato integrada.
El tiempo de importación sigue siendo ligero; la superficie de promoción se carga solo en su primer uso, en lugar de reentrar en el inicio del canal integrado al importar el módulo.

Cuando esas superficies de inicio incluyen métodos RPC del gateway, mantenlas en un
prefijo específico del plugin. Los espacios de nombres administrativos del core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) siguen estando reservados y siempre se resuelven
a `operator.admin`, aunque un plugin solicite un alcance más limitado.

Ejemplo:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadatos de catálogo de canal

Los plugins de canal pueden anunciar metadatos de configuración/descubrimiento mediante `openclaw.channel` y
sugerencias de instalación mediante `openclaw.install`. Esto mantiene el núcleo libre de datos de catálogo.

Ejemplo:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Campos útiles de `openclaw.channel` además del ejemplo mínimo:

- `detailLabel`: etiqueta secundaria para superficies más ricas de catálogo/estado
- `docsLabel`: anula el texto del enlace a documentación
- `preferOver`: ids de plugin/canal de menor prioridad a los que esta entrada de catálogo debe superar
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: controles de copia para la superficie de selección
- `markdownCapable`: marca el canal como compatible con Markdown para decisiones de formato de salida
- `exposure.configured`: oculta el canal de superficies de listado de canales configurados cuando se establece en `false`
- `exposure.setup`: oculta el canal de selectores interactivos de configuración cuando se establece en `false`
- `exposure.docs`: marca el canal como interno/privado para superficies de navegación de documentación
- `showConfigured` / `showInSetup`: alias legacy aún aceptados por compatibilidad; prefiere `exposure`
- `quickstartAllowFrom`: incorpora el canal al flujo estándar rápido `allowFrom`
- `forceAccountBinding`: requiere vinculación explícita de cuenta incluso cuando solo existe una cuenta
- `preferSessionLookupForAnnounceTarget`: prefiere búsqueda de sesión al resolver objetivos de anuncios

OpenClaw también puede fusionar **catálogos de canal externos** (por ejemplo, una
exportación de registro MPM). Coloca un archivo JSON en una de estas rutas:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

O apunta `OPENCLAW_PLUGIN_CATALOG_PATHS` (o `OPENCLAW_MPM_CATALOG_PATHS`) a
uno o más archivos JSON (delimitados por comas/punto y coma/`PATH`). Cada archivo debe
contener `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. El analizador también acepta `"packages"` o `"plugins"` como alias legacy para la clave `"entries"`.

## Plugins de motor de contexto

Los plugins de motor de contexto poseen la orquestación del contexto de sesión para ingestión, ensamblado
y compactación. Regístralos desde tu plugin con
`api.registerContextEngine(id, factory)` y luego selecciona el motor activo con
`plugins.slots.contextEngine`.

Usa esto cuando tu plugin necesite reemplazar o ampliar el canal predeterminado de
contexto en lugar de simplemente añadir búsqueda de memoria o hooks.

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Si tu motor **no** posee el algoritmo de compactación, mantén `compact()`
implementado y delega explícitamente:

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Añadir una nueva capacidad

Cuando un plugin necesita un comportamiento que no encaja en la API actual, no eludas
el sistema de plugins con un acceso privado. Añade la capacidad que falta.

Secuencia recomendada:

1. define el contrato del core
   Decide qué comportamiento compartido debe poseer el core: política, respaldo, fusión de configuración,
   ciclo de vida, semántica orientada al canal y forma del asistente de entorno de ejecución.
2. añade superficies tipadas de registro/entorno de ejecución de plugins
   Amplía `OpenClawPluginApi` y/o `api.runtime` con la superficie tipada de capacidad
   más pequeña que resulte útil.
3. conecta consumidores del core + canal/funcionalidad
   Los canales y plugins de funcionalidad deben consumir la nueva capacidad a través del core,
   no importando directamente una implementación de proveedor.
4. registra implementaciones de proveedor
   Los plugins de proveedor registran después sus backends frente a la capacidad.
5. añade cobertura de contrato
   Añade pruebas para que la propiedad y la forma del registro sigan siendo explícitas con el tiempo.

Así es como OpenClaw mantiene una opinión sin volverse rígido respecto a la visión del mundo
de un solo proveedor. Consulta el [Recetario de capacidades](/es/plugins/architecture)
para ver una lista concreta de archivos y un ejemplo resuelto.

### Lista de verificación de capacidad

Cuando añadas una nueva capacidad, la implementación normalmente debe tocar estas
superficies juntas:

- tipos del contrato del core en `src/<capability>/types.ts`
- ejecutor/asistente de entorno de ejecución del core en `src/<capability>/runtime.ts`
- superficie de registro de API de plugins en `src/plugins/types.ts`
- conexión del registro de plugins en `src/plugins/registry.ts`
- exposición del entorno de ejecución de plugins en `src/plugins/runtime/*` cuando los plugins de funcionalidad/canal necesiten consumirlo
- asistentes de captura/prueba en `src/test-utils/plugin-registration.ts`
- aserciones de propiedad/contrato en `src/plugins/contracts/registry.ts`
- documentación para operadores/plugins en `docs/`

Si falta una de esas superficies, normalmente es señal de que la capacidad
todavía no está completamente integrada.

### Plantilla de capacidad

Patrón mínimo:

```ts
// contrato del core
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// API de plugin
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// asistente compartido de entorno de ejecución para plugins de funcionalidad/canal
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Patrón de prueba de contrato:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Eso mantiene simple la regla:

- el core posee el contrato de capacidad + la orquestación
- los plugins de proveedor poseen las implementaciones del proveedor
- los plugins de funcionalidad/canal consumen asistentes de entorno de ejecución
- las pruebas de contrato mantienen la propiedad explícita
