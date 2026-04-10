---
read_when:
    - Desea configurar proveedores de búsqueda de memoria o modelos de embeddings
    - Desea configurar el backend de QMD
    - Desea ajustar la búsqueda híbrida, MMR o el decaimiento temporal
    - Desea habilitar la indexación de memoria multimodal
summary: Todos los parámetros de configuración para la búsqueda de memoria, los proveedores de embeddings, QMD, la búsqueda híbrida y la indexación multimodal
title: Referencia de configuración de memoria
x-i18n:
    generated_at: "2026-04-10T05:12:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5f9076bdfad95b87bd70625821bf401326f8eaeb53842b70823881419dbe43cb
    source_path: reference/memory-config.md
    workflow: 15
---

# Referencia de configuración de memoria

Esta página enumera todos los parámetros de configuración para la búsqueda de memoria de OpenClaw. Para obtener vistas conceptuales generales, consulte:

- [Descripción general de la memoria](/es/concepts/memory) -- cómo funciona la memoria
- [Motor integrado](/es/concepts/memory-builtin) -- backend SQLite predeterminado
- [Motor QMD](/es/concepts/memory-qmd) -- sidecar local-first
- [Búsqueda de memoria](/es/concepts/memory-search) -- canalización de búsqueda y ajuste
- [Memoria activa](/es/concepts/active-memory) -- habilitar el subagente de memoria para sesiones interactivas

Todos los ajustes de búsqueda de memoria se encuentran en `agents.defaults.memorySearch` en
`openclaw.json`, a menos que se indique lo contrario.

Si busca el interruptor de función de **memoria activa** y la configuración del subagente,
se encuentran en `plugins.entries.active-memory` en lugar de `memorySearch`.

La memoria activa usa un modelo de dos puertas:

1. el plugin debe estar habilitado y apuntar al id del agente actual
2. la solicitud debe ser una sesión de chat persistente e interactiva elegible

Consulte [Memoria activa](/es/concepts/active-memory) para ver el modelo de activación,
la configuración propiedad del plugin, la persistencia de transcripciones y el patrón de implementación segura.

---

## Selección de proveedor

| Key        | Type      | Default          | Description                                                                                 |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------- |
| `provider` | `string`  | detectado automáticamente | ID del adaptador de embeddings: `openai`, `gemini`, `voyage`, `mistral`, `bedrock`, `ollama`, `local` |
| `model`    | `string`  | predeterminado del proveedor | Nombre del modelo de embeddings                                                                        |
| `fallback` | `string`  | `"none"`         | ID del adaptador de respaldo cuando falla el principal                                                  |
| `enabled`  | `boolean` | `true`           | Habilitar o deshabilitar la búsqueda de memoria                                                             |

### Orden de detección automática

Cuando `provider` no está configurado, OpenClaw selecciona el primero disponible:

1. `local` -- si `memorySearch.local.modelPath` está configurado y el archivo existe.
2. `openai` -- si se puede resolver una clave de OpenAI.
3. `gemini` -- si se puede resolver una clave de Gemini.
4. `voyage` -- si se puede resolver una clave de Voyage.
5. `mistral` -- si se puede resolver una clave de Mistral.
6. `bedrock` -- si la cadena de credenciales del SDK de AWS se resuelve (rol de instancia, claves de acceso, perfil, SSO, identidad web o configuración compartida).

`ollama` es compatible, pero no se detecta automáticamente (configúrelo explícitamente).

### Resolución de claves de API

Los embeddings remotos requieren una clave de API. Bedrock usa la cadena de credenciales predeterminada del SDK de AWS
en su lugar (roles de instancia, SSO, claves de acceso).

| Provider | Env var                        | Config key                        |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Bedrock  | cadena de credenciales de AWS           | No se necesita clave de API                 |
| Ollama   | `OLLAMA_API_KEY` (marcador de posición) | --                                |

Codex OAuth solo cubre chat/completions y no satisface las solicitudes
de embeddings.

---

## Configuración de endpoint remoto

Para endpoints personalizados compatibles con OpenAI o para sobrescribir los valores predeterminados del proveedor:

| Key              | Type     | Description                                        |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | URL base de API personalizada                                |
| `remote.apiKey`  | `string` | Sobrescribir la clave de API                                   |
| `remote.headers` | `object` | Encabezados HTTP adicionales (fusionados con los valores predeterminados del proveedor) |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Configuración específica de Gemini

| Key                    | Type     | Default                | Description                                |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | También es compatible con `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Para Embedding 2: 768, 1536 o 3072        |

<Warning>
Cambiar el modelo o `outputDimensionality` desencadena una reindexación completa automática.
</Warning>

---

## Configuración de embeddings de Bedrock

Bedrock usa la cadena de credenciales predeterminada del SDK de AWS -- no se necesitan claves de API.
Si OpenClaw se ejecuta en EC2 con un rol de instancia habilitado para Bedrock, solo configure el
proveedor y el modelo:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| Key                    | Type     | Default                        | Description                     |
| ---------------------- | -------- | ------------------------------ | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Cualquier ID de modelo de embeddings de Bedrock  |
| `outputDimensionality` | `number` | predeterminado del modelo                  | Para Titan V2: 256, 512 o 1024 |

### Modelos compatibles

Los siguientes modelos son compatibles (con detección de familia y valores predeterminados
de dimensiones):

| Model ID                                   | Provider   | Default Dims | Configurable Dims    |
| ------------------------------------------ | ---------- | ------------ | -------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024         | 256, 512, 1024       |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536         | --                   |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536         | --                   |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024         | --                   |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024         | 256, 384, 1024, 3072 |
| `cohere.embed-english-v3`                  | Cohere     | 1024         | --                   |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024         | --                   |
| `cohere.embed-v4:0`                        | Cohere     | 1536         | 256-1536             |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512          | --                   |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024         | --                   |

Las variantes con sufijo de rendimiento (por ejemplo, `amazon.titan-embed-text-v1:2:8k`) heredan
la configuración del modelo base.

### Autenticación

La autenticación de Bedrock usa el orden estándar de resolución de credenciales del SDK de AWS:

1. Variables de entorno (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Caché de tokens de SSO
3. Credenciales de token de identidad web
4. Archivos compartidos de credenciales y configuración
5. Credenciales de metadatos de ECS o EC2

La región se resuelve a partir de `AWS_REGION`, `AWS_DEFAULT_REGION`, la
`baseUrl` del proveedor `amazon-bedrock`, o usa `us-east-1` de forma predeterminada.

### Permisos de IAM

El rol o usuario de IAM necesita:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Para aplicar el principio de privilegio mínimo, limite `InvokeModel` al modelo específico:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Configuración de embeddings locales

| Key                   | Type     | Default                | Description                     |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | descargado automáticamente        | Ruta al archivo del modelo GGUF         |
| `local.modelCacheDir` | `string` | valor predeterminado de node-llama-cpp | Directorio de caché para los modelos descargados |

Modelo predeterminado: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, se descarga automáticamente).
Requiere compilación nativa: `pnpm approve-builds` y luego `pnpm rebuild node-llama-cpp`.

---

## Configuración de búsqueda híbrida

Todo bajo `memorySearch.query.hybrid`:

| Key                   | Type      | Default | Description                        |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | Habilitar la búsqueda híbrida BM25 + vectorial |
| `vectorWeight`        | `number`  | `0.7`   | Peso para las puntuaciones vectoriales (0-1)     |
| `textWeight`          | `number`  | `0.3`   | Peso para las puntuaciones BM25 (0-1)       |
| `candidateMultiplier` | `number`  | `4`     | Multiplicador del tamaño del conjunto de candidatos     |

### MMR (diversidad)

| Key           | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Habilitar la reclasificación MMR                |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = máxima diversidad, 1 = máxima relevancia |

### Decaimiento temporal (recencia)

| Key                          | Type      | Default | Description               |
| ---------------------------- | --------- | ------- | ------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Habilitar el impulso por recencia      |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | La puntuación se reduce a la mitad cada N días |

Los archivos perennes (`MEMORY.md`, archivos sin fecha en `memory/`) nunca se ven afectados por el decaimiento.

### Ejemplo completo

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## Rutas de memoria adicionales

| Key          | Type       | Description                              |
| ------------ | ---------- | ---------------------------------------- |
| `extraPaths` | `string[]` | Directorios o archivos adicionales para indexar |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

Las rutas pueden ser absolutas o relativas al workspace. Los directorios se exploran
de forma recursiva en busca de archivos `.md`. El manejo de enlaces simbólicos depende del backend activo:
el motor integrado ignora los enlaces simbólicos, mientras que QMD sigue el comportamiento del
escáner QMD subyacente.

Para la búsqueda de transcripciones entre agentes con alcance por agente, use
`agents.list[].memorySearch.qmd.extraCollections` en lugar de `memory.qmd.paths`.
Esas colecciones adicionales siguen la misma forma `{ path, name, pattern? }`, pero
se combinan por agente y pueden conservar nombres compartidos explícitos cuando la ruta
apunta fuera del workspace actual.
Si la misma ruta resuelta aparece tanto en `memory.qmd.paths` como en
`memorySearch.qmd.extraCollections`, QMD conserva la primera entrada y omite el
duplicado.

---

## Memoria multimodal (Gemini)

Indexe imágenes y audio junto con Markdown usando Gemini Embedding 2:

| Key                       | Type       | Default    | Description                            |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Habilitar la indexación multimodal             |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` o `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Tamaño máximo de archivo para indexación             |

Solo se aplica a los archivos en `extraPaths`. Las raíces de memoria predeterminadas siguen siendo solo de Markdown.
Requiere `gemini-embedding-2-preview`. `fallback` debe ser `"none"`.

Formatos compatibles: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(imágenes); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (audio).

---

## Caché de embeddings

| Clave              | Tipo      | Predeterminado | Descripción                      |
| ------------------ | --------- | -------------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false`        | Almacenar en caché embeddings de fragmentos en SQLite |
| `cache.maxEntries` | `number`  | `50000`        | Máximo de embeddings en caché            |

Evita volver a generar embeddings para texto sin cambios durante la reindexación o las actualizaciones de transcripciones.

---

## Indexación por lotes

| Clave                         | Tipo      | Predeterminado | Descripción                |
| ----------------------------- | --------- | -------------- | -------------------------- |
| `remote.batch.enabled`        | `boolean` | `false`        | Habilitar la API de embeddings por lotes |
| `remote.batch.concurrency`    | `number`  | `2`            | Trabajos por lotes en paralelo        |
| `remote.batch.wait`           | `boolean` | `true`         | Esperar a que termine el lote  |
| `remote.batch.pollIntervalMs` | `number`  | --             | Intervalo de sondeo              |
| `remote.batch.timeoutMinutes` | `number`  | --             | Tiempo de espera del lote              |

Disponible para `openai`, `gemini` y `voyage`. El procesamiento por lotes de OpenAI suele ser
el más rápido y económico para grandes backfills.

---

## Búsqueda de memoria de sesión (experimental)

Indexe transcripciones de sesión y muéstrelas a través de `memory_search`:

| Clave                         | Tipo       | Predeterminado | Descripción                             |
| ----------------------------- | ---------- | -------------- | --------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`        | Habilitar la indexación de sesiones                 |
| `sources`                     | `string[]` | `["memory"]`   | Agregue `"sessions"` para incluir transcripciones |
| `sync.sessions.deltaBytes`    | `number`   | `100000`       | Umbral de bytes para reindexar              |
| `sync.sessions.deltaMessages` | `number`   | `50`           | Umbral de mensajes para reindexar           |

La indexación de sesiones es opcional y se ejecuta de forma asíncrona. Los resultados pueden quedar
ligeramente desactualizados. Los registros de sesión se almacenan en disco, así que trate el acceso al sistema de archivos
como el límite de confianza.

---

## Aceleración vectorial de SQLite (sqlite-vec)

| Clave                        | Tipo      | Predeterminado | Descripción                       |
| ---------------------------- | --------- | -------------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`         | Usar sqlite-vec para consultas vectoriales |
| `store.vector.extensionPath` | `string`  | integrado       | Sobrescribir la ruta de sqlite-vec          |

Cuando sqlite-vec no está disponible, OpenClaw recurre automáticamente a la similitud
de coseno en proceso.

---

## Almacenamiento del índice

| Clave               | Tipo     | Predeterminado                         | Descripción                                 |
| ------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`        | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Ubicación del índice (admite el token `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                         | Tokenizador FTS5 (`unicode61` o `trigram`)   |

---

## Configuración del backend de QMD

Configure `memory.backend = "qmd"` para habilitarlo. Todos los ajustes de QMD se encuentran en
`memory.qmd`:

| Clave                    | Tipo      | Predeterminado | Descripción                                  |
| ------------------------ | --------- | -------------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`          | Ruta del ejecutable de QMD                          |
| `searchMode`             | `string`  | `search`       | Comando de búsqueda: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`         | Indexar automáticamente `MEMORY.md` + `memory/**/*.md`    |
| `paths[]`                | `array`   | --             | Rutas adicionales: `{ name, path, pattern? }`      |
| `sessions.enabled`       | `boolean` | `false`        | Indexar transcripciones de sesión                    |
| `sessions.retentionDays` | `number`  | --             | Retención de transcripciones                         |
| `sessions.exportDir`     | `string`  | --             | Directorio de exportación                             |

OpenClaw prefiere las formas actuales de colecciones de QMD y consultas de MCP, pero mantiene
las versiones anteriores de QMD funcionando mediante retroceso a las marcas heredadas de colección `--mask`
y a nombres anteriores de herramientas MCP cuando es necesario.

Las sobrescrituras de modelo de QMD permanecen del lado de QMD, no en la configuración de OpenClaw. Si necesita
sobrescribir globalmente los modelos de QMD, configure variables de entorno como
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` y `QMD_GENERATE_MODEL` en el entorno de ejecución
del gateway.

### Programación de actualizaciones

| Clave                     | Tipo      | Predeterminado | Descripción                           |
| ------------------------- | --------- | -------------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`           | Intervalo de actualización                      |
| `update.debounceMs`       | `number`  | `15000`        | Debounce de cambios de archivos                 |
| `update.onBoot`           | `boolean` | `true`         | Actualizar al iniciar                    |
| `update.waitForBootSync`  | `boolean` | `false`        | Bloquear el inicio hasta que termine la actualización |
| `update.embedInterval`    | `string`  | --             | Cadencia separada para embeddings                |
| `update.commandTimeoutMs` | `number`  | --             | Tiempo de espera para comandos de QMD              |
| `update.updateTimeoutMs`  | `number`  | --             | Tiempo de espera para operaciones de actualización de QMD     |
| `update.embedTimeoutMs`   | `number`  | --             | Tiempo de espera para operaciones de embeddings de QMD      |

### Límites

| Clave                     | Tipo     | Predeterminado | Descripción                |
| ------------------------- | -------- | -------------- | -------------------------- |
| `limits.maxResults`       | `number` | `6`            | Máximo de resultados de búsqueda         |
| `limits.maxSnippetChars`  | `number` | --             | Limitar la longitud del fragmento       |
| `limits.maxInjectedChars` | `number` | --             | Limitar el total de caracteres inyectados |
| `limits.timeoutMs`        | `number` | `4000`         | Tiempo de espera de búsqueda             |

### Alcance

Controla qué sesiones pueden recibir resultados de búsqueda de QMD. El mismo esquema que
[`session.sendPolicy`](/es/gateway/configuration-reference#session):

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

El valor predeterminado es solo DM. `match.keyPrefix` coincide con la clave de sesión normalizada;
`match.rawKeyPrefix` coincide con la clave sin procesar, incluido `agent:<id>:`.

### Citas

`memory.citations` se aplica a todos los backends:

| Valor            | Comportamiento                                            |
| ---------------- | --------------------------------------------------------- |
| `auto` (predeterminado) | Incluir el pie `Source: <path#line>` en los fragmentos    |
| `on`             | Incluir siempre el pie                               |
| `off`            | Omitir el pie (la ruta sigue pasándose al agente internamente) |

### Ejemplo completo de QMD

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming (experimental)

Dreaming se configura en `plugins.entries.memory-core.config.dreaming`,
no en `agents.defaults.memorySearch`.

Dreaming se ejecuta como un barrido programado y usa fases internas light/deep/REM como
detalle de implementación.

Para el comportamiento conceptual y los comandos con barra, consulte [Dreaming](/es/concepts/dreaming).

### Ajustes del usuario

| Clave       | Tipo      | Predeterminado | Descripción                                       |
| ----------- | --------- | -------------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`        | Habilitar o deshabilitar completamente Dreaming               |
| `frequency` | `string`  | `0 3 * * *`    | Cadencia cron opcional para el barrido completo de Dreaming |

### Ejemplo

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

Notas:

- Dreaming escribe el estado de la máquina en `memory/.dreams/`.
- Dreaming escribe la salida narrativa legible para humanos en `DREAMS.md` (o `dreams.md` existente).
- La política y los umbrales de las fases light/deep/REM son comportamiento interno, no configuración orientada al usuario.
