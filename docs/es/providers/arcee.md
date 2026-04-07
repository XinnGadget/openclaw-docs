---
read_when:
    - Quieres usar Arcee AI con OpenClaw
    - Necesitas la variable de entorno de la API key o la opción de autenticación de la CLI
summary: Configuración de Arcee AI (autenticación + selección de modelo)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-07T05:05:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) proporciona acceso a la familia Trinity de modelos mixture-of-experts a través de una API compatible con OpenAI. Todos los modelos Trinity tienen licencia Apache 2.0.

Se puede acceder a los modelos de Arcee AI directamente a través de la plataforma Arcee o mediante [OpenRouter](/es/providers/openrouter).

- Proveedor: `arcee`
- Autenticación: `ARCEEAI_API_KEY` (directo) o `OPENROUTER_API_KEY` (mediante OpenRouter)
- API: compatible con OpenAI
- URL base: `https://api.arcee.ai/api/v1` (directo) o `https://openrouter.ai/api/v1` (OpenRouter)

## Inicio rápido

1. Obtén una API key de [Arcee AI](https://chat.arcee.ai/) o [OpenRouter](https://openrouter.ai/keys).

2. Configura la API key (recomendado: almacenarla para Gateway):

```bash
# Directo (plataforma Arcee)
openclaw onboard --auth-choice arceeai-api-key

# Mediante OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. Configura un modelo predeterminado:

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## Ejemplo no interactivo

```bash
# Directo (plataforma Arcee)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Mediante OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## Nota sobre el entorno

Si Gateway se ejecuta como un daemon (launchd/systemd), asegúrate de que `ARCEEAI_API_KEY`
(o `OPENROUTER_API_KEY`) esté disponible para ese proceso (por ejemplo, en
`~/.openclaw/.env` o mediante `env.shellEnv`).

## Catálogo integrado

OpenClaw actualmente incluye este catálogo empaquetado de Arcee:

| Referencia de modelo           | Nombre                 | Entrada | Contexto | Costo (entrada/salida por 1M) | Notas                                     |
| ------------------------------ | ---------------------- | ------- | -------- | ----------------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text    | 256K     | $0.25 / $0.90                 | Modelo predeterminado; razonamiento habilitado |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text    | 128K     | $0.25 / $1.00                 | Uso general; 400B parámetros, 13B activos |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text    | 128K     | $0.045 / $0.15                | Rápido y rentable; llamada de funciones |

Las mismas referencias de modelo funcionan tanto para configuraciones directas como con OpenRouter (por ejemplo, `arcee/trinity-large-thinking`).

El preset de incorporación configura `arcee/trinity-large-thinking` como modelo predeterminado.

## Funciones compatibles

- Streaming
- Uso de herramientas / llamada de funciones
- Salida estructurada (modo JSON y esquema JSON)
- Pensamiento extendido (Trinity Large Thinking)
