---
read_when:
    - Estás creando un plugin de OpenClaw
    - Necesitas publicar un esquema de configuración del plugin o depurar errores de validación del plugin
summary: Manifiesto del plugin + requisitos del esquema JSON (validación estricta de configuración)
title: Manifiesto del plugin
x-i18n:
    generated_at: "2026-04-11T02:46:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6b254c121d1eb5ea19adbd4148243cf47339c960442ab1ca0e0bfd52e0154c88
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifiesto del plugin (`openclaw.plugin.json`)

Esta página es solo para el **manifiesto nativo de plugin de OpenClaw**.

Para diseños de paquete compatibles, consulta [Paquetes de plugins](/es/plugins/bundles).

Los formatos de paquete compatibles usan archivos de manifiesto diferentes:

- Paquete de Codex: `.codex-plugin/plugin.json`
- Paquete de Claude: `.claude-plugin/plugin.json` o el diseño predeterminado de componentes de Claude
  sin manifiesto
- Paquete de Cursor: `.cursor-plugin/plugin.json`

OpenClaw también detecta automáticamente esos diseños de paquete, pero no se validan
contra el esquema de `openclaw.plugin.json` descrito aquí.

Para los paquetes compatibles, OpenClaw actualmente lee los metadatos del paquete más las
raíces de Skills declaradas, las raíces de comandos de Claude, los valores predeterminados de `settings.json` del paquete de Claude,
los valores predeterminados de LSP del paquete de Claude y los paquetes de hooks compatibles cuando el diseño coincide con
las expectativas del entorno de ejecución de OpenClaw.

Todo plugin nativo de OpenClaw **debe** incluir un archivo `openclaw.plugin.json` en la
**raíz del plugin**. OpenClaw usa este manifiesto para validar la configuración
**sin ejecutar código del plugin**. Los manifiestos faltantes o no válidos se tratan como
errores del plugin y bloquean la validación de configuración.

Consulta la guía completa del sistema de plugins: [Plugins](/es/tools/plugin).
Para el modelo nativo de capacidades y la guía actual de compatibilidad externa:
[Modelo de capacidades](/es/plugins/architecture#public-capability-model).

## Qué hace este archivo

`openclaw.plugin.json` son los metadatos que OpenClaw lee antes de cargar el
código de tu plugin.

Úsalo para:

- identidad del plugin
- validación de configuración
- metadatos de autenticación y onboarding que deben estar disponibles sin iniciar el
  entorno de ejecución del plugin
- metadatos de alias y autoactivación que deben resolverse antes de que se cargue el entorno de ejecución del plugin
- metadatos abreviados de propiedad de familias de modelos que deben activar automáticamente el
  plugin antes de que se cargue el entorno de ejecución
- instantáneas estáticas de propiedad de capacidades usadas para cableado de compatibilidad integrado y
  cobertura de contratos
- metadatos de configuración específicos de canal que deben combinarse en las superficies
  de catálogo y validación sin cargar el entorno de ejecución
- sugerencias de UI de configuración

No lo uses para:

- registrar comportamiento en tiempo de ejecución
- declarar puntos de entrada de código
- metadatos de instalación de npm

Eso pertenece al código de tu plugin y a `package.json`.

## Ejemplo mínimo

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Ejemplo completo

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin de proveedor de OpenRouter",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "Clave de API de OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Clave de API de OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Clave de API",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Referencia de campos de nivel superior

| Campo                               | Obligatorio | Tipo                             | Qué significa                                                                                                                                                                                                     |
| ----------------------------------- | ----------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | Sí          | `string`                         | Id canónico del plugin. Este es el id usado en `plugins.entries.<id>`.                                                                                                                                            |
| `configSchema`                      | Sí          | `object`                         | Esquema JSON en línea para la configuración de este plugin.                                                                                                                                                       |
| `enabledByDefault`                  | No          | `true`                           | Marca un plugin integrado como habilitado de forma predeterminada. Omítelo, o establece cualquier valor distinto de `true`, para dejar el plugin deshabilitado de forma predeterminada.                       |
| `legacyPluginIds`                   | No          | `string[]`                       | Id heredados que se normalizan a este id canónico de plugin.                                                                                                                                                      |
| `autoEnableWhenConfiguredProviders` | No          | `string[]`                       | Id de proveedor que deben habilitar automáticamente este plugin cuando la autenticación, la configuración o las referencias de modelo los mencionan.                                                             |
| `kind`                              | No          | `"memory"` \| `"context-engine"` | Declara un tipo exclusivo de plugin usado por `plugins.slots.*`.                                                                                                                                                  |
| `channels`                          | No          | `string[]`                       | Id de canal propiedad de este plugin. Se usan para descubrimiento y validación de configuración.                                                                                                                  |
| `providers`                         | No          | `string[]`                       | Id de proveedor propiedad de este plugin.                                                                                                                                                                         |
| `modelSupport`                      | No          | `object`                         | Metadatos abreviados de familias de modelos propiedad del manifiesto usados para cargar automáticamente el plugin antes del entorno de ejecución.                                                                |
| `cliBackends`                       | No          | `string[]`                       | Id de backend de inferencia CLI propiedad de este plugin. Se usan para autoactivación al inicio a partir de referencias de configuración explícitas.                                                            |
| `commandAliases`                    | No          | `object[]`                       | Nombres de comando propiedad de este plugin que deben producir configuración y diagnósticos de CLI con reconocimiento del plugin antes de que se cargue el entorno de ejecución.                                |
| `providerAuthEnvVars`               | No          | `Record<string, string[]>`       | Metadatos ligeros de variables de entorno de autenticación de proveedor que OpenClaw puede inspeccionar sin cargar código del plugin.                                                                            |
| `providerAuthAliases`               | No          | `Record<string, string>`         | Id de proveedor que deben reutilizar otro id de proveedor para la búsqueda de autenticación, por ejemplo, un proveedor de programación que comparte la clave de API y los perfiles de autenticación del proveedor base. |
| `channelEnvVars`                    | No          | `Record<string, string[]>`       | Metadatos ligeros de variables de entorno de canal que OpenClaw puede inspeccionar sin cargar código del plugin. Úsalo para superficies de autenticación o configuración de canal basadas en entorno que los ayudantes genéricos de inicio/configuración deban ver. |
| `providerAuthChoices`               | No          | `object[]`                       | Metadatos ligeros de opciones de autenticación para selectores de onboarding, resolución de proveedor preferido y cableado simple de marcas de CLI.                                                             |
| `contracts`                         | No          | `object`                         | Instantánea estática de capacidades integradas para voz, transcripción en tiempo real, voz en tiempo real, comprensión de medios, generación de imágenes, generación de música, generación de video, obtención web, búsqueda web y propiedad de herramientas. |
| `channelConfigs`                    | No          | `Record<string, object>`         | Metadatos de configuración de canal propiedad del manifiesto combinados en las superficies de descubrimiento y validación antes de que se cargue el entorno de ejecución.                                       |
| `skills`                            | No          | `string[]`                       | Directorios de Skills que se deben cargar, relativos a la raíz del plugin.                                                                                                                                        |
| `name`                              | No          | `string`                         | Nombre legible del plugin.                                                                                                                                                                                        |
| `description`                       | No          | `string`                         | Resumen corto que se muestra en las superficies del plugin.                                                                                                                                                       |
| `version`                           | No          | `string`                         | Versión informativa del plugin.                                                                                                                                                                                   |
| `uiHints`                           | No          | `Record<string, object>`         | Etiquetas de UI, marcadores de posición y sugerencias de sensibilidad para campos de configuración.                                                                                                               |

## Referencia de `providerAuthChoices`

Cada entrada de `providerAuthChoices` describe una opción de onboarding o autenticación.
OpenClaw la lee antes de que se cargue el entorno de ejecución del proveedor.

| Campo                 | Obligatorio | Tipo                                            | Qué significa                                                                                           |
| --------------------- | ----------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `provider`            | Sí          | `string`                                        | Id del proveedor al que pertenece esta opción.                                                          |
| `method`              | Sí          | `string`                                        | Id del método de autenticación al que se enviará.                                                       |
| `choiceId`            | Sí          | `string`                                        | Id estable de opción de autenticación usado por los flujos de onboarding y CLI.                         |
| `choiceLabel`         | No          | `string`                                        | Etiqueta visible para el usuario. Si se omite, OpenClaw recurre a `choiceId`.                           |
| `choiceHint`          | No          | `string`                                        | Texto breve de ayuda para el selector.                                                                  |
| `assistantPriority`   | No          | `number`                                        | Los valores más bajos se ordenan antes en selectores interactivos controlados por el asistente.        |
| `assistantVisibility` | No          | `"visible"` \| `"manual-only"`                  | Oculta la opción de los selectores del asistente, pero sigue permitiendo la selección manual en la CLI. |
| `deprecatedChoiceIds` | No          | `string[]`                                      | Id heredados de opciones que deben redirigir a los usuarios a esta opción de reemplazo.                |
| `groupId`             | No          | `string`                                        | Id opcional de grupo para agrupar opciones relacionadas.                                                |
| `groupLabel`          | No          | `string`                                        | Etiqueta visible para el usuario de ese grupo.                                                          |
| `groupHint`           | No          | `string`                                        | Texto breve de ayuda para el grupo.                                                                     |
| `optionKey`           | No          | `string`                                        | Clave interna de opción para flujos simples de autenticación con una sola marca.                        |
| `cliFlag`             | No          | `string`                                        | Nombre de la marca de CLI, como `--openrouter-api-key`.                                                 |
| `cliOption`           | No          | `string`                                        | Forma completa de la opción de CLI, como `--openrouter-api-key <key>`.                                  |
| `cliDescription`      | No          | `string`                                        | Descripción usada en la ayuda de la CLI.                                                                |
| `onboardingScopes`    | No          | `Array<"text-inference" \| "image-generation">` | En qué superficies de onboarding debe aparecer esta opción. Si se omite, el valor predeterminado es `["text-inference"]`. |

## Referencia de `commandAliases`

Usa `commandAliases` cuando un plugin es propietario de un nombre de comando de entorno de ejecución que los usuarios podrían
poner por error en `plugins.allow` o intentar ejecutar como un comando raíz de CLI. OpenClaw
usa estos metadatos para diagnósticos sin importar el código del entorno de ejecución del plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Campo        | Obligatorio | Tipo              | Qué significa                                                            |
| ------------ | ----------- | ----------------- | ------------------------------------------------------------------------ |
| `name`       | Sí          | `string`          | Nombre del comando que pertenece a este plugin.                          |
| `kind`       | No          | `"runtime-slash"` | Marca el alias como un comando slash de chat en lugar de un comando raíz de CLI. |
| `cliCommand` | No          | `string`          | Comando raíz de CLI relacionado que se debe sugerir para operaciones de CLI, si existe. |

## Referencia de `uiHints`

`uiHints` es un mapa de nombres de campos de configuración a pequeñas sugerencias de renderizado.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Cada sugerencia de campo puede incluir:

| Campo         | Tipo       | Qué significa                            |
| ------------- | ---------- | ---------------------------------------- |
| `label`       | `string`   | Etiqueta del campo visible para el usuario. |
| `help`        | `string`   | Texto breve de ayuda.                    |
| `tags`        | `string[]` | Etiquetas de UI opcionales.              |
| `advanced`    | `boolean`  | Marca el campo como avanzado.            |
| `sensitive`   | `boolean`  | Marca el campo como secreto o sensible.  |
| `placeholder` | `string`   | Texto de marcador de posición para entradas de formulario. |

## Referencia de `contracts`

Usa `contracts` solo para metadatos estáticos de propiedad de capacidades que OpenClaw puede
leer sin importar el entorno de ejecución del plugin.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Cada lista es opcional:

| Campo                            | Tipo       | Qué significa                                                   |
| -------------------------------- | ---------- | --------------------------------------------------------------- |
| `speechProviders`                | `string[]` | Id de proveedor de voz del que este plugin es propietario.      |
| `realtimeTranscriptionProviders` | `string[]` | Id de proveedor de transcripción en tiempo real del que este plugin es propietario. |
| `realtimeVoiceProviders`         | `string[]` | Id de proveedor de voz en tiempo real del que este plugin es propietario. |
| `mediaUnderstandingProviders`    | `string[]` | Id de proveedor de comprensión de medios del que este plugin es propietario. |
| `imageGenerationProviders`       | `string[]` | Id de proveedor de generación de imágenes del que este plugin es propietario. |
| `videoGenerationProviders`       | `string[]` | Id de proveedor de generación de video del que este plugin es propietario. |
| `webFetchProviders`              | `string[]` | Id de proveedor de obtención web del que este plugin es propietario. |
| `webSearchProviders`             | `string[]` | Id de proveedor de búsqueda web del que este plugin es propietario. |
| `tools`                          | `string[]` | Nombres de herramientas del agente del que este plugin es propietario para comprobaciones de contratos integrados. |

## Referencia de `channelConfigs`

Usa `channelConfigs` cuando un plugin de canal necesita metadatos de configuración ligeros antes
de que se cargue el entorno de ejecución.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "URL del homeserver",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Conexión al homeserver de Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Cada entrada de canal puede incluir:

| Campo         | Tipo                     | Qué significa                                                                              |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | Esquema JSON para `channels.<id>`. Obligatorio para cada entrada declarada de configuración de canal. |
| `uiHints`     | `Record<string, object>` | Etiquetas/placeholders/sugerencias de sensibilidad de UI opcionales para esa sección de configuración del canal. |
| `label`       | `string`                 | Etiqueta del canal combinada en las superficies de selector e inspección cuando los metadatos del entorno de ejecución no están listos. |
| `description` | `string`                 | Descripción corta del canal para las superficies de inspección y catálogo.                 |
| `preferOver`  | `string[]`               | Id heredados o de menor prioridad a los que este canal debe superar en las superficies de selección. |

## Referencia de `modelSupport`

Usa `modelSupport` cuando OpenClaw deba inferir tu plugin de proveedor a partir de
id abreviados de modelos como `gpt-5.4` o `claude-sonnet-4.6` antes de que se cargue el entorno de ejecución del plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw aplica esta precedencia:

- las referencias explícitas `provider/model` usan los metadatos `providers` del manifiesto propietario
- `modelPatterns` tienen prioridad sobre `modelPrefixes`
- si coinciden un plugin no integrado y uno integrado, gana el plugin no integrado
- la ambigüedad restante se ignora hasta que el usuario o la configuración especifiquen un proveedor

Campos:

| Campo           | Tipo       | Qué significa                                                                    |
| --------------- | ---------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefijos comparados con `startsWith` frente a id abreviados de modelos.          |
| `modelPatterns` | `string[]` | Fuentes regex comparadas con id abreviados de modelos después de eliminar el sufijo del perfil. |

Las claves heredadas de capacidades de nivel superior están obsoletas. Usa `openclaw doctor --fix` para
mover `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` y `webSearchProviders` bajo `contracts`; la carga normal del
manifiesto ya no trata esos campos de nivel superior como
propiedad de capacidades.

## Manifiesto frente a package.json

Los dos archivos cumplen funciones distintas:

| Archivo                | Úsalo para                                                                                                                        |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Descubrimiento, validación de configuración, metadatos de opciones de autenticación y sugerencias de UI que deben existir antes de que se ejecute el código del plugin |
| `package.json`         | Metadatos de npm, instalación de dependencias y el bloque `openclaw` usado para puntos de entrada, control de instalación, configuración o metadatos de catálogo |

Si no estás seguro de dónde debe ir una parte de los metadatos, usa esta regla:

- si OpenClaw debe conocerlos antes de cargar el código del plugin, ponlos en `openclaw.plugin.json`
- si se trata de empaquetado, archivos de entrada o comportamiento de instalación de npm, ponlos en `package.json`

### Campos de package.json que afectan al descubrimiento

Algunos metadatos del plugin previos al entorno de ejecución viven intencionalmente en `package.json` bajo el
bloque `openclaw` en lugar de `openclaw.plugin.json`.

Ejemplos importantes:

| Campo                                                             | Qué significa                                                                                                                              |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.extensions`                                             | Declara puntos de entrada de plugins nativos.                                                                                              |
| `openclaw.setupEntry`                                             | Punto de entrada liviano solo para configuración usado durante onboarding y el inicio diferido de canales.                                |
| `openclaw.channel`                                                | Metadatos ligeros del catálogo de canales, como etiquetas, rutas de documentación, alias y texto de selección.                            |
| `openclaw.channel.configuredState`                                | Metadatos ligeros del comprobador de estado configurado que pueden responder “¿ya existe una configuración solo por entorno?” sin cargar el entorno de ejecución completo del canal. |
| `openclaw.channel.persistedAuthState`                             | Metadatos ligeros del comprobador de autenticación persistida que pueden responder “¿ya hay algo con sesión iniciada?” sin cargar el entorno de ejecución completo del canal. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Sugerencias de instalación/actualización para plugins integrados y publicados externamente.                                               |
| `openclaw.install.defaultChoice`                                  | Ruta de instalación preferida cuando hay varias fuentes de instalación disponibles.                                                        |
| `openclaw.install.minHostVersion`                                 | Versión mínima compatible del host de OpenClaw, usando un mínimo semver como `>=2026.3.22`.                                               |
| `openclaw.install.allowInvalidConfigRecovery`                     | Permite una ruta de recuperación estrecha de reinstalación de plugin integrado cuando la configuración no es válida.                      |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permite que las superficies del canal solo de configuración se carguen antes que el plugin completo del canal durante el inicio.         |

`openclaw.install.minHostVersion` se aplica durante la instalación y la carga del
registro de manifiestos. Los valores no válidos se rechazan; los valores válidos pero más recientes omiten el
plugin en hosts más antiguos.

`openclaw.install.allowInvalidConfigRecovery` es intencionalmente estrecho. No
hace instalables configuraciones rotas arbitrarias. Hoy solo permite que los flujos de instalación
se recuperen de fallos específicos y obsoletos de actualización de plugins integrados, como una
ruta faltante del plugin integrado o una entrada obsoleta `channels.<id>` para ese mismo
plugin integrado. Los errores de configuración no relacionados siguen bloqueando la instalación y envían a los operadores
a `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` es metadato de paquete para un pequeño módulo comprobador:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Úsalo cuando los flujos de configuración, doctor o estado configurado necesiten una sonda de autenticación
de sí/no barata antes de que se cargue el plugin completo del canal. La exportación de destino debe ser una función pequeña que solo lea el estado persistido; no la enrutes mediante el barrel completo del entorno de ejecución del canal.

`openclaw.channel.configuredState` sigue la misma forma para comprobaciones ligeras de estado configurado solo por entorno:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Úsalo cuando un canal pueda responder el estado configurado a partir del entorno u otras
entradas pequeñas que no sean del entorno de ejecución. Si la comprobación necesita resolución completa de configuración o el entorno de ejecución
real del canal, mantén esa lógica en el hook `config.hasConfiguredState` del plugin.

## Requisitos del esquema JSON

- **Todo plugin debe incluir un esquema JSON**, incluso si no acepta configuración.
- Se acepta un esquema vacío (por ejemplo, `{ "type": "object", "additionalProperties": false }`).
- Los esquemas se validan al leer/escribir configuración, no en tiempo de ejecución.

## Comportamiento de validación

- Las claves desconocidas `channels.*` son **errores**, salvo que el id del canal esté declarado por
  un manifiesto de plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` y `plugins.slots.*`
  deben hacer referencia a id de plugin **detectables**. Los id desconocidos son **errores**.
- Si un plugin está instalado pero tiene un manifiesto o esquema roto o faltante,
  la validación falla y Doctor informa el error del plugin.
- Si existe configuración del plugin pero el plugin está **deshabilitado**, la configuración se conserva y
  se muestra una **advertencia** en Doctor + registros.

Consulta [Referencia de configuración](/es/gateway/configuration) para ver el esquema completo de `plugins.*`.

## Notas

- El manifiesto es **obligatorio para los plugins nativos de OpenClaw**, incluidas las cargas desde el sistema de archivos local.
- El entorno de ejecución sigue cargando el módulo del plugin por separado; el manifiesto es solo para
  descubrimiento + validación.
- Los manifiestos nativos se analizan con JSON5, por lo que se aceptan comentarios, comas finales y
  claves sin comillas, siempre que el valor final siga siendo un objeto.
- El cargador de manifiestos solo lee los campos documentados del manifiesto. Evita agregar
  aquí claves personalizadas de nivel superior.
- `providerAuthEnvVars` es la ruta de metadatos ligeros para sondas de autenticación, validación de marcadores
  de variables de entorno y superficies similares de autenticación de proveedor que no deberían iniciar el entorno de ejecución del plugin solo para inspeccionar nombres de variables de entorno.
- `providerAuthAliases` permite que variantes de proveedor reutilicen las variables de entorno de autenticación,
  perfiles de autenticación, autenticación basada en configuración y opción de onboarding de clave de API
  de otro proveedor sin codificar esa relación de forma rígida en el núcleo.
- `channelEnvVars` es la ruta de metadatos ligeros para respaldo por variables de entorno del shell, prompts
  de configuración y superficies similares de canal que no deberían iniciar el entorno de ejecución del plugin
  solo para inspeccionar nombres de variables de entorno.
- `providerAuthChoices` es la ruta de metadatos ligeros para selectores de opciones de autenticación,
  resolución de `--auth-choice`, asignación de proveedor preferido y registro simple de
  marcas de CLI de onboarding antes de que se cargue el entorno de ejecución del proveedor. Para metadatos
  de asistente en tiempo de ejecución que requieren código del proveedor, consulta
  [Hooks de entorno de ejecución del proveedor](/es/plugins/architecture#provider-runtime-hooks).
- Los tipos exclusivos de plugins se seleccionan mediante `plugins.slots.*`.
  - `kind: "memory"` se selecciona mediante `plugins.slots.memory`.
  - `kind: "context-engine"` se selecciona mediante `plugins.slots.contextEngine`
    (predeterminado: `legacy` integrado).
- `channels`, `providers`, `cliBackends` y `skills` pueden omitirse cuando un
  plugin no los necesita.
- Si tu plugin depende de módulos nativos, documenta los pasos de compilación y cualquier
  requisito de lista de permitidos del gestor de paquetes (por ejemplo, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Relacionado

- [Creación de plugins](/es/plugins/building-plugins) — introducción a los plugins
- [Arquitectura de plugins](/es/plugins/architecture) — arquitectura interna
- [Resumen del SDK](/es/plugins/sdk-overview) — referencia del SDK de plugins
