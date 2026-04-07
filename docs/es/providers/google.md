---
read_when:
    - Quieres usar modelos Google Gemini con OpenClaw
    - Necesitas la API key o el flujo de autenticación OAuth
summary: Configuración de Google Gemini (API key + OAuth, generación de imágenes, comprensión multimedia, búsqueda web)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-07T05:05:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 36cc7c7d8d19f6d4a3fb223af36c8402364fc309d14ffe922bd004203ceb1754
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

El plugin de Google proporciona acceso a modelos Gemini a través de Google AI Studio, además de
generación de imágenes, comprensión multimedia (imagen/audio/video) y búsqueda web mediante
Gemini Grounding.

- Proveedor: `google`
- Autenticación: `GEMINI_API_KEY` o `GOOGLE_API_KEY`
- API: API de Google Gemini
- Proveedor alternativo: `google-gemini-cli` (OAuth)

## Inicio rápido

1. Configura la API key:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Configura un modelo predeterminado:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Ejemplo no interactivo

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth (Gemini CLI)

Un proveedor alternativo `google-gemini-cli` usa OAuth con PKCE en lugar de una API
key. Esta es una integración no oficial; algunos usuarios informan de
restricciones de cuenta. Úsalo bajo tu propia responsabilidad.

- Modelo predeterminado: `google-gemini-cli/gemini-3.1-pro-preview`
- Alias: `gemini-cli`
- Requisito previo de instalación: Gemini CLI local disponible como `gemini`
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Inicio de sesión:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Variables de entorno:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(O las variantes `GEMINI_CLI_*`).

Si las solicitudes de OAuth de Gemini CLI fallan después de iniciar sesión, establece
`GOOGLE_CLOUD_PROJECT` o `GOOGLE_CLOUD_PROJECT_ID` en el host de Gateway y
vuelve a intentarlo.

Si el inicio de sesión falla antes de que comience el flujo del navegador, asegúrate de que el comando local `gemini`
esté instalado y en `PATH`. OpenClaw admite tanto instalaciones de Homebrew
como instalaciones globales de npm, incluidos diseños comunes de Windows/npm.

Notas sobre el uso de JSON de Gemini CLI:

- El texto de respuesta proviene del campo JSON `response` de la CLI.
- El uso recurre a `stats` cuando la CLI deja `usage` vacío.
- `stats.cached` se normaliza en OpenClaw como `cacheRead`.
- Si falta `stats.input`, OpenClaw deriva los tokens de entrada a partir de
  `stats.input_tokens - stats.cached`.

## Capacidades

| Capacidad               | Compatible        |
| ----------------------- | ----------------- |
| Finalizaciones de chat  | Sí                |
| Generación de imágenes  | Sí                |
| Generación de música    | Sí                |
| Comprensión de imágenes | Sí                |
| Transcripción de audio  | Sí                |
| Comprensión de video    | Sí                |
| Búsqueda web (Grounding) | Sí               |
| Pensamiento/razonamiento | Sí (Gemini 3.1+) |

## Reutilización directa de caché de Gemini

Para ejecuciones directas de la API de Gemini (`api: "google-generative-ai"`), OpenClaw ahora
pasa un identificador `cachedContent` configurado a las solicitudes de Gemini.

- Configura parámetros por modelo o globales con
  `cachedContent` o el heredado `cached_content`
- Si ambos están presentes, prevalece `cachedContent`
- Valor de ejemplo: `cachedContents/prebuilt-context`
- El uso por acierto de caché de Gemini se normaliza en OpenClaw como `cacheRead` a partir de
  `cachedContentTokenCount` de upstream

Ejemplo:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## Generación de imágenes

El proveedor empaquetado de generación de imágenes `google` usa de forma predeterminada
`google/gemini-3.1-flash-image-preview`.

- También admite `google/gemini-3-pro-image-preview`
- Generación: hasta 4 imágenes por solicitud
- Modo de edición: habilitado, hasta 5 imágenes de entrada
- Controles de geometría: `size`, `aspectRatio` y `resolution`

El proveedor `google-gemini-cli`, solo con OAuth, es una superficie separada
de inferencia de texto. La generación de imágenes, la comprensión multimedia y Gemini Grounding permanecen en
el id de proveedor `google`.

Para usar Google como proveedor de imágenes predeterminado:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

Consulta [Generación de imágenes](/es/tools/image-generation) para los parámetros
compartidos de herramientas, la selección de proveedor y el comportamiento de failover.

## Generación de video

El plugin empaquetado `google` también registra generación de video a través de la herramienta compartida
`video_generate`.

- Modelo de video predeterminado: `google/veo-3.1-fast-generate-preview`
- Modos: texto a video, imagen a video y flujos con referencia de video único
- Admite `aspectRatio`, `resolution` y `audio`
- Límite actual de duración: **de 4 a 8 segundos**

Para usar Google como proveedor de video predeterminado:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

Consulta [Generación de video](/es/tools/video-generation) para los parámetros
compartidos de herramientas, la selección de proveedor y el comportamiento de failover.

## Generación de música

El plugin empaquetado `google` también registra generación de música a través de la herramienta compartida
`music_generate`.

- Modelo de música predeterminado: `google/lyria-3-clip-preview`
- También admite `google/lyria-3-pro-preview`
- Controles del prompt: `lyrics` e `instrumental`
- Formato de salida: `mp3` de forma predeterminada, además de `wav` en `google/lyria-3-pro-preview`
- Entradas de referencia: hasta 10 imágenes
- Las ejecuciones respaldadas por sesión se desacoplan mediante el flujo compartido de tarea/estado, incluido `action: "status"`

Para usar Google como proveedor de música predeterminado:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

Consulta [Generación de música](/es/tools/music-generation) para los parámetros
compartidos de herramientas, la selección de proveedor y el comportamiento de failover.

## Nota sobre el entorno

Si Gateway se ejecuta como un daemon (launchd/systemd), asegúrate de que `GEMINI_API_KEY`
esté disponible para ese proceso (por ejemplo, en `~/.openclaw/.env` o mediante
`env.shellEnv`).
