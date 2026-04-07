---
read_when:
    - Estás creando un plugin de OpenClaw
    - Necesitas distribuir un esquema de configuración del plugin o depurar errores de validación del plugin
summary: Manifiesto del plugin + requisitos del esquema JSON (validación estricta de configuración)
title: Manifiesto del plugin
x-i18n:
    generated_at: "2026-04-07T05:04:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 22d41b9f8748b1b1b066ee856be4a8f41e88b9a8bc073d74fc79d2bb0982f01a
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifiesto del plugin (openclaw.plugin.json)

Esta página es solo para el **manifiesto nativo de plugins de OpenClaw**.

Para diseños de paquetes compatibles, consulta [Paquetes de plugins](/es/plugins/bundles).

Los formatos de paquetes compatibles usan archivos de manifiesto distintos:

- Paquete Codex: `.codex-plugin/plugin.json`
- Paquete Claude: `.claude-plugin/plugin.json` o el diseño predeterminado de componentes de Claude
  sin manifiesto
- Paquete Cursor: `.cursor-plugin/plugin.json`

OpenClaw también detecta automáticamente esos diseños de paquetes, pero no se validan
contra el esquema `openclaw.plugin.json` descrito aquí.

Para los paquetes compatibles, OpenClaw actualmente lee los metadatos del paquete más las raíces de
Skills declaradas, las raíces de comandos de Claude, los valores predeterminados de `settings.json` del paquete Claude,
los valores predeterminados de LSP del paquete Claude y los paquetes de hooks compatibles cuando el diseño coincide
con las expectativas de ejecución de OpenClaw.

Todo plugin nativo de OpenClaw **debe** incluir un archivo `openclaw.plugin.json` en la
**raíz del plugin**. OpenClaw usa este manifiesto para validar la configuración
**sin ejecutar código del plugin**. Los manifiestos ausentes o no válidos se tratan como
errores del plugin y bloquean la validación de la configuración.

Consulta la guía completa del sistema de plugins: [Plugins](/es/tools/plugin).
Para el modelo de capacidades nativas y la guía actual de compatibilidad externa:
[Modelo de capacidades](/es/plugins/architecture#public-capability-model).

## Qué hace este archivo

`openclaw.plugin.json` son los metadatos que OpenClaw lee antes de cargar el
código de tu plugin.

Úsalo para:

- identidad del plugin
- validación de configuración
- metadatos de autenticación e incorporación que deban estar disponibles sin iniciar el
  tiempo de ejecución del plugin
- metadatos de alias y activación automática que deban resolverse antes de que se cargue el tiempo de ejecución del plugin
- metadatos abreviados de propiedad de familias de modelos que deban activar automáticamente el
  plugin antes de que se cargue el tiempo de ejecución
- instantáneas estáticas de propiedad de capacidades usadas para el cableado de compatibilidad integrado y
  la cobertura de contratos
- metadatos de configuración específicos del canal que deban fusionarse en las superficies
  de catálogo y validación sin cargar el tiempo de ejecución
- pistas de UI de configuración

No lo uses para:

- registrar comportamiento en tiempo de ejecución
- declarar entrypoints de código
- metadatos de instalación npm

Eso corresponde al código de tu plugin y a `package.json`.

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

| Field                               | Required | Type                             | What it means                                                                                                                                                                                                |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Sí       | `string`                         | ID canónico del plugin. Este es el ID usado en `plugins.entries.<id>`.                                                                                                                                        |
| `configSchema`                      | Sí       | `object`                         | JSON Schema en línea para la configuración de este plugin.                                                                                                                                                    |
| `enabledByDefault`                  | No       | `true`                           | Marca un plugin integrado como habilitado de forma predeterminada. Omítelo, o establece cualquier valor distinto de `true`, para dejar el plugin deshabilitado de forma predeterminada.                     |
| `legacyPluginIds`                   | No       | `string[]`                       | IDs heredados que se normalizan a este ID canónico del plugin.                                                                                                                                               |
| `autoEnableWhenConfiguredProviders` | No       | `string[]`                       | IDs de proveedor que deberían habilitar automáticamente este plugin cuando la autenticación, la configuración o las referencias de modelo los mencionen.                                                    |
| `kind`                              | No       | `"memory"` \| `"context-engine"` | Declara un tipo exclusivo de plugin usado por `plugins.slots.*`.                                                                                                                                             |
| `channels`                          | No       | `string[]`                       | IDs de canal controlados por este plugin. Se usan para descubrimiento y validación de configuración.                                                                                                         |
| `providers`                         | No       | `string[]`                       | IDs de proveedor controlados por este plugin.                                                                                                                                                                |
| `modelSupport`                      | No       | `object`                         | Metadatos abreviados de familia de modelos controlados por el manifiesto usados para cargar automáticamente el plugin antes del tiempo de ejecución.                                                        |
| `cliBackends`                       | No       | `string[]`                       | IDs de backend de inferencia de CLI controlados por este plugin. Se usan para la activación automática al inicio a partir de referencias explícitas de configuración.                                       |
| `providerAuthEnvVars`               | No       | `Record<string, string[]>`       | Metadatos ligeros de autenticación de proveedor en variables de entorno que OpenClaw puede inspeccionar sin cargar el código del plugin.                                                                    |
| `channelEnvVars`                    | No       | `Record<string, string[]>`       | Metadatos ligeros de variables de entorno del canal que OpenClaw puede inspeccionar sin cargar el código del plugin. Usa esto para superficies de configuración o autenticación de canal basadas en entorno que los ayudantes genéricos de inicio/configuración deberían ver. |
| `providerAuthChoices`               | No       | `object[]`                       | Metadatos ligeros de opciones de autenticación para selectores de incorporación, resolución de proveedor preferido y cableado simple de flags de CLI.                                                       |
| `contracts`                         | No       | `object`                         | Instantánea estática de capacidades integradas para voz, transcripción en tiempo real, voz en tiempo real, comprensión multimedia, generación de imágenes, generación de música, generación de video, web-fetch, búsqueda web y propiedad de herramientas. |
| `channelConfigs`                    | No       | `Record<string, object>`         | Metadatos de configuración de canal controlados por el manifiesto que se fusionan en las superficies de descubrimiento y validación antes de que se cargue el tiempo de ejecución.                         |
| `skills`                            | No       | `string[]`                       | Directorios de Skills que se deben cargar, relativos a la raíz del plugin.                                                                                                                                    |
| `name`                              | No       | `string`                         | Nombre legible del plugin.                                                                                                                                                                                   |
| `description`                       | No       | `string`                         | Resumen breve mostrado en las superficies del plugin.                                                                                                                                                        |
| `version`                           | No       | `string`                         | Versión informativa del plugin.                                                                                                                                                                              |
| `uiHints`                           | No       | `Record<string, object>`         | Etiquetas de UI, placeholders y pistas de sensibilidad para campos de configuración.                                                                                                                          |

## Referencia de `providerAuthChoices`

Cada entrada de `providerAuthChoices` describe una opción de incorporación o autenticación.
OpenClaw la lee antes de que se cargue el tiempo de ejecución del proveedor.

| Field                 | Required | Type                                            | What it means                                                                                            |
| --------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Sí       | `string`                                        | ID del proveedor al que pertenece esta opción.                                                           |
| `method`              | Sí       | `string`                                        | ID del método de autenticación al que se enviará.                                                        |
| `choiceId`            | Sí       | `string`                                        | ID estable de opción de autenticación usado por los flujos de incorporación y CLI.                      |
| `choiceLabel`         | No       | `string`                                        | Etiqueta visible para el usuario. Si se omite, OpenClaw usa `choiceId` como respaldo.                   |
| `choiceHint`          | No       | `string`                                        | Texto de ayuda breve para el selector.                                                                   |
| `assistantPriority`   | No       | `number`                                        | Los valores más bajos se ordenan antes en los selectores interactivos guiados por el asistente.         |
| `assistantVisibility` | No       | `"visible"` \| `"manual-only"`                  | Oculta la opción en los selectores del asistente, pero sigue permitiendo la selección manual por CLI.   |
| `deprecatedChoiceIds` | No       | `string[]`                                      | IDs heredados de opciones que deberían redirigir a los usuarios a esta opción de reemplazo.             |
| `groupId`             | No       | `string`                                        | ID de grupo opcional para agrupar opciones relacionadas.                                                 |
| `groupLabel`          | No       | `string`                                        | Etiqueta visible para el usuario de ese grupo.                                                           |
| `groupHint`           | No       | `string`                                        | Texto de ayuda breve para el grupo.                                                                      |
| `optionKey`           | No       | `string`                                        | Clave de opción interna para flujos simples de autenticación con un solo flag.                           |
| `cliFlag`             | No       | `string`                                        | Nombre del flag de CLI, como `--openrouter-api-key`.                                                     |
| `cliOption`           | No       | `string`                                        | Forma completa de la opción de CLI, como `--openrouter-api-key <key>`.                                   |
| `cliDescription`      | No       | `string`                                        | Descripción usada en la ayuda de CLI.                                                                    |
| `onboardingScopes`    | No       | `Array<"text-inference" \| "image-generation">` | En qué superficies de incorporación debe aparecer esta opción. Si se omite, el valor predeterminado es `["text-inference"]`. |

## Referencia de `uiHints`

`uiHints` es un mapa de nombres de campos de configuración a pequeñas pistas de renderizado.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Clave de API",
      "help": "Se usa para solicitudes de OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Cada pista de campo puede incluir:

| Field         | Type       | What it means                           |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Etiqueta del campo visible para el usuario. |
| `help`        | `string`   | Texto de ayuda breve.                   |
| `tags`        | `string[]` | Etiquetas opcionales de UI.             |
| `advanced`    | `boolean`  | Marca el campo como avanzado.           |
| `sensitive`   | `boolean`  | Marca el campo como secreto o sensible. |
| `placeholder` | `string`   | Texto de placeholder para entradas de formularios. |

## Referencia de `contracts`

Usa `contracts` solo para metadatos estáticos de propiedad de capacidades que OpenClaw pueda
leer sin importar el tiempo de ejecución del plugin.

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

| Field                            | Type       | What it means                                                  |
| -------------------------------- | ---------- | -------------------------------------------------------------- |
| `speechProviders`                | `string[]` | IDs de proveedor de voz que controla este plugin.              |
| `realtimeTranscriptionProviders` | `string[]` | IDs de proveedor de transcripción en tiempo real que controla este plugin. |
| `realtimeVoiceProviders`         | `string[]` | IDs de proveedor de voz en tiempo real que controla este plugin. |
| `mediaUnderstandingProviders`    | `string[]` | IDs de proveedor de comprensión multimedia que controla este plugin. |
| `imageGenerationProviders`       | `string[]` | IDs de proveedor de generación de imágenes que controla este plugin. |
| `videoGenerationProviders`       | `string[]` | IDs de proveedor de generación de video que controla este plugin. |
| `webFetchProviders`              | `string[]` | IDs de proveedor de web-fetch que controla este plugin.        |
| `webSearchProviders`             | `string[]` | IDs de proveedor de búsqueda web que controla este plugin.     |
| `tools`                          | `string[]` | Nombres de herramientas del agente que controla este plugin para comprobaciones integradas de contratos. |

## Referencia de `channelConfigs`

Usa `channelConfigs` cuando un plugin de canal necesite metadatos de configuración ligeros antes de que
se cargue el tiempo de ejecución.

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

| Field         | Type                     | What it means                                                                             |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema para `channels.<id>`. Obligatorio para cada entrada de configuración de canal declarada. |
| `uiHints`     | `Record<string, object>` | Etiquetas/placeholders/pistas de sensibilidad de UI opcionales para esa sección de configuración del canal. |
| `label`       | `string`                 | Etiqueta del canal fusionada en superficies de selector e inspección cuando los metadatos de tiempo de ejecución no están listos. |
| `description` | `string`                 | Descripción breve del canal para superficies de inspección y catálogo.                    |
| `preferOver`  | `string[]`               | IDs heredados o de menor prioridad de plugins que este canal debe superar en las superficies de selección. |

## Referencia de `modelSupport`

Usa `modelSupport` cuando OpenClaw deba inferir tu plugin de proveedor a partir de
IDs abreviados de modelo como `gpt-5.4` o `claude-sonnet-4.6` antes de que se cargue el tiempo de ejecución del plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw aplica esta precedencia:

- las referencias explícitas `provider/model` usan los metadatos de manifiesto `providers` del propietario
- `modelPatterns` tienen prioridad sobre `modelPrefixes`
- si coinciden un plugin no integrado y uno integrado, gana el plugin no integrado
- la ambigüedad restante se ignora hasta que el usuario o la configuración especifiquen un proveedor

Campos:

| Field           | Type       | What it means                                                                   |
| --------------- | ---------- | ------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefijos comparados con `startsWith` frente a IDs abreviados de modelo.         |
| `modelPatterns` | `string[]` | Fuentes regex comparadas con IDs abreviados de modelo después de eliminar el sufijo del perfil. |

Las claves heredadas de capacidades de nivel superior están obsoletas. Usa `openclaw doctor --fix` para
mover `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` y `webSearchProviders` bajo `contracts`; la carga normal
del manifiesto ya no trata esos campos de nivel superior como propiedad
de capacidades.

## Manifiesto frente a package.json

Los dos archivos tienen funciones distintas:

| File                   | Use it for                                                                                                                       |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Descubrimiento, validación de configuración, metadatos de opciones de autenticación y pistas de UI que deben existir antes de que se ejecute el código del plugin |
| `package.json`         | Metadatos npm, instalación de dependencias y el bloque `openclaw` usado para entrypoints, control de instalación, configuración o metadatos de catálogo |

Si no tienes claro dónde debe ir un dato, usa esta regla:

- si OpenClaw debe conocerlo antes de cargar el código del plugin, colócalo en `openclaw.plugin.json`
- si trata sobre empaquetado, archivos de entrada o comportamiento de instalación npm, colócalo en `package.json`

### Campos de package.json que afectan al descubrimiento

Algunos metadatos del plugin previos al tiempo de ejecución viven intencionadamente en `package.json` dentro del
bloque `openclaw` en lugar de `openclaw.plugin.json`.

Ejemplos importantes:

| Field                                                             | What it means                                                                                                                                |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Declara entrypoints nativos del plugin.                                                                                                      |
| `openclaw.setupEntry`                                             | Entrypoint ligero solo de configuración usado durante la incorporación y el inicio diferido de canales.                                     |
| `openclaw.channel`                                                | Metadatos ligeros del catálogo de canales, como etiquetas, rutas de documentación, alias y texto de selección.                             |
| `openclaw.channel.configuredState`                                | Metadatos ligeros del comprobador de estado configurado que pueden responder a "¿ya existe una configuración solo con entorno?" sin cargar el tiempo de ejecución completo del canal. |
| `openclaw.channel.persistedAuthState`                             | Metadatos ligeros del comprobador de autenticación persistida que pueden responder a "¿ya hay algo con sesión iniciada?" sin cargar el tiempo de ejecución completo del canal. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Pistas de instalación/actualización para plugins integrados y publicados externamente.                                                      |
| `openclaw.install.defaultChoice`                                  | Ruta de instalación preferida cuando hay varias fuentes de instalación disponibles.                                                          |
| `openclaw.install.minHostVersion`                                 | Versión mínima compatible del host de OpenClaw, usando un piso semver como `>=2026.3.22`.                                                  |
| `openclaw.install.allowInvalidConfigRecovery`                     | Permite una ruta de recuperación de reinstalación limitada para plugins integrados cuando la configuración no es válida.                    |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permite que las superficies del canal solo de configuración se carguen antes del plugin completo del canal durante el inicio.              |

`openclaw.install.minHostVersion` se aplica durante la instalación y la carga del registro
del manifiesto. Los valores no válidos se rechazan; los valores válidos pero más recientes omiten el
plugin en hosts más antiguos.

`openclaw.install.allowInvalidConfigRecovery` es intencionadamente limitado. No
hace instalables configuraciones rotas arbitrarias. Hoy solo permite que los flujos de instalación
se recuperen de fallos concretos de actualización de plugins integrados obsoletos, como una
ruta faltante del plugin integrado o una entrada obsoleta `channels.<id>` para ese mismo
plugin integrado. Los errores de configuración no relacionados siguen bloqueando la instalación y envían a los operadores
a `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` es un metadato de paquete para un módulo
comprobador diminuto:

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
ligera de sí/no antes de que se cargue el plugin completo del canal. La exportación de destino debe ser una
función pequeña que lea solo el estado persistido; no la encamines a través del barrel completo
de tiempo de ejecución del canal.

`openclaw.channel.configuredState` sigue la misma forma para comprobaciones ligeras
de estado configurado solo con entorno:

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

Úsalo cuando un canal pueda responder al estado configurado desde el entorno u otras entradas
mínimas no relacionadas con el tiempo de ejecución. Si la comprobación necesita resolución completa de configuración o el
tiempo de ejecución real del canal, mantén esa lógica en el hook `config.hasConfiguredState`
del plugin.

## Requisitos de JSON Schema

- **Todo plugin debe incluir un JSON Schema**, incluso si no acepta configuración.
- Se acepta un esquema vacío (por ejemplo, `{ "type": "object", "additionalProperties": false }`).
- Los esquemas se validan en el momento de lectura/escritura de la configuración, no en tiempo de ejecución.

## Comportamiento de validación

- Las claves desconocidas `channels.*` son **errores**, salvo que el ID del canal esté declarado por
  un manifiesto de plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` y `plugins.slots.*`
  deben hacer referencia a IDs de plugin **detectables**. Los IDs desconocidos son **errores**.
- Si un plugin está instalado pero tiene un manifiesto o esquema roto o ausente,
  la validación falla y Doctor informa del error del plugin.
- Si existe configuración del plugin pero el plugin está **deshabilitado**, la configuración se conserva y
  se muestra una **advertencia** en Doctor + los registros.

Consulta [Referencia de configuración](/es/gateway/configuration) para ver el esquema completo de `plugins.*`.

## Notas

- El manifiesto es **obligatorio para los plugins nativos de OpenClaw**, incluidas las cargas desde el sistema de archivos local.
- El tiempo de ejecución sigue cargando el módulo del plugin por separado; el manifiesto es solo para
  descubrimiento + validación.
- Los manifiestos nativos se analizan con JSON5, por lo que se aceptan comentarios, comas finales y
  claves sin comillas siempre que el valor final siga siendo un objeto.
- El cargador de manifiestos solo lee los campos de manifiesto documentados. Evita añadir
  aquí claves personalizadas de nivel superior.
- `providerAuthEnvVars` es la ruta ligera de metadatos para sondas de autenticación, validación
  de marcadores de entorno y superficies similares de autenticación de proveedor que no deberían iniciar el
  tiempo de ejecución del plugin solo para inspeccionar nombres de variables de entorno.
- `channelEnvVars` es la ruta ligera de metadatos para respaldo de variables de entorno del shell, prompts
  de configuración y superficies similares de canal que no deberían iniciar el tiempo de ejecución del plugin
  solo para inspeccionar nombres de variables de entorno.
- `providerAuthChoices` es la ruta ligera de metadatos para selectores de opciones de autenticación,
  resolución de `--auth-choice`, asignación de proveedor preferido y registro simple
  de flags de CLI de incorporación antes de que se cargue el tiempo de ejecución del proveedor. Para metadatos
  del asistente en tiempo de ejecución que requieran código del proveedor, consulta
  [Hooks de tiempo de ejecución del proveedor](/es/plugins/architecture#provider-runtime-hooks).
- Los tipos exclusivos de plugins se seleccionan mediante `plugins.slots.*`.
  - `kind: "memory"` se selecciona mediante `plugins.slots.memory`.
  - `kind: "context-engine"` se selecciona mediante `plugins.slots.contextEngine`
    (predeterminado: `legacy` integrado).
- `channels`, `providers`, `cliBackends` y `skills` pueden omitirse cuando un
  plugin no los necesite.
- Si tu plugin depende de módulos nativos, documenta los pasos de compilación y cualquier
  requisito de lista permitida del gestor de paquetes (por ejemplo, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Relacionado

- [Building Plugins](/es/plugins/building-plugins) — primeros pasos con plugins
- [Plugin Architecture](/es/plugins/architecture) — arquitectura interna
- [SDK Overview](/es/plugins/sdk-overview) — referencia del SDK de plugins
