---
read_when:
    - Explicar el uso de tokens, los costos o las ventanas de contexto
    - Depurar el crecimiento del contexto o el comportamiento de compactación
summary: Cómo OpenClaw construye el contexto del prompt y reporta el uso de tokens + costos
title: Uso de tokens y costos
x-i18n:
    generated_at: "2026-04-07T05:06:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0683693d6c6fcde7d5fba236064ba97dd4b317ae6bea3069db969fcd178119d9
    source_path: reference/token-use.md
    workflow: 15
---

# Uso de tokens y costos

OpenClaw rastrea **tokens**, no caracteres. Los tokens son específicos del modelo, pero la mayoría de los
modelos de estilo OpenAI promedian ~4 caracteres por token para texto en inglés.

## Cómo se construye el prompt del sistema

OpenClaw ensambla su propio prompt del sistema en cada ejecución. Incluye:

- Lista de herramientas + descripciones breves
- Lista de Skills (solo metadatos; las instrucciones se cargan bajo demanda con `read`)
- Instrucciones de autoactualización
- Espacio de trabajo + archivos de arranque (`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, `BOOTSTRAP.md` cuando son nuevos, más `MEMORY.md` cuando está presente o `memory.md` como respaldo en minúsculas). Los archivos grandes se truncan mediante `agents.defaults.bootstrapMaxChars` (predeterminado: 20000), y la inyección total de arranque está limitada por `agents.defaults.bootstrapTotalMaxChars` (predeterminado: 150000). Los archivos `memory/*.md` se cargan bajo demanda mediante herramientas de memoria y no se inyectan automáticamente.
- Hora (UTC + zona horaria del usuario)
- Etiquetas de respuesta + comportamiento de heartbeat
- Metadatos de tiempo de ejecución (host/OS/model/thinking)

Consulta el desglose completo en [Prompt del sistema](/es/concepts/system-prompt).

## Qué cuenta en la ventana de contexto

Todo lo que recibe el modelo cuenta para el límite de contexto:

- Prompt del sistema (todas las secciones listadas arriba)
- Historial de conversación (mensajes de usuario + asistente)
- Llamadas a herramientas y resultados de herramientas
- Adjuntos/transcripciones (imágenes, audio, archivos)
- Resúmenes de compactación y artefactos de poda
- Wrappers del proveedor o encabezados de seguridad (no visibles, pero igualmente contados)

Para imágenes, OpenClaw reduce la escala de las cargas de imágenes de transcripción/herramientas antes de las llamadas al proveedor.
Usa `agents.defaults.imageMaxDimensionPx` (predeterminado: `1200`) para ajustarlo:

- Los valores más bajos normalmente reducen el uso de vision-tokens y el tamaño de la carga útil.
- Los valores más altos conservan más detalle visual para OCR/capturas de pantalla con mucha interfaz.

Para un desglose práctico (por archivo inyectado, herramientas, Skills y tamaño del prompt del sistema), usa `/context list` o `/context detail`. Consulta [Contexto](/es/concepts/context).

## Cómo ver el uso actual de tokens

Usa estos comandos en el chat:

- `/status` → **tarjeta de estado rica en emojis** con el modelo de la sesión, uso de contexto,
  tokens de entrada/salida de la última respuesta y **costo estimado** (solo con clave API).
- `/usage off|tokens|full` → añade un **pie de uso por respuesta** a cada respuesta.
  - Persiste por sesión (almacenado como `responseUsage`).
  - La autenticación OAuth **oculta el costo** (solo tokens).
- `/usage cost` → muestra un resumen local de costos a partir de los registros de sesión de OpenClaw.

Otras superficies:

- **TUI/Web TUI:** `/status` + `/usage` están admitidos.
- **CLI:** `openclaw status --usage` y `openclaw channels list` muestran
  ventanas de cuota del proveedor normalizadas (`X% left`, no costos por respuesta).
  Proveedores actuales con ventana de uso: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi y z.ai.

Las superficies de uso normalizan alias comunes de campos nativos del proveedor antes de mostrarlos.
Para el tráfico Responses de la familia OpenAI, eso incluye tanto `input_tokens` /
`output_tokens` como `prompt_tokens` / `completion_tokens`, para que los nombres de campos
específicos del transporte no cambien `/status`, `/usage` ni los resúmenes de sesión.
El uso JSON de Gemini CLI también se normaliza: el texto de la respuesta viene de `response`, y
`stats.cached` se asigna a `cacheRead`, usando `stats.input_tokens - stats.cached`
cuando el CLI omite un campo explícito `stats.input`.
Para el tráfico Responses nativo de la familia OpenAI, los alias de uso de WebSocket/SSE se
normalizan de la misma forma, y los totales vuelven a entrada + salida normalizadas cuando
falta `total_tokens` o es `0`.
Cuando la instantánea actual de la sesión es escasa, `/status` y `session_status` también pueden
recuperar contadores de tokens/caché y la etiqueta del modelo activo de tiempo de ejecución desde el
registro de uso más reciente de la transcripción. Los valores live existentes distintos de cero siguen teniendo
prioridad sobre los valores de respaldo de la transcripción, y los totales orientados al prompt más grandes
de la transcripción pueden prevalecer cuando faltan los totales almacenados o son menores.
La autenticación de uso para ventanas de cuota del proveedor proviene de hooks específicos del proveedor cuando
están disponibles; de lo contrario, OpenClaw vuelve a credenciales OAuth/clave API coincidentes de
perfiles de autenticación, entorno o configuración.

## Estimación de costos (cuando se muestra)

Los costos se estiman a partir de tu configuración de precios del modelo:

```
models.providers.<provider>.models[].cost
```

Estos son **USD por 1M de tokens** para `input`, `output`, `cacheRead` y
`cacheWrite`. Si faltan los precios, OpenClaw muestra solo los tokens. Los tokens OAuth
nunca muestran costo en dólares.

## TTL de caché e impacto de la poda

El almacenamiento en caché del prompt del proveedor solo se aplica dentro de la ventana TTL de la caché. OpenClaw puede
ejecutar opcionalmente **poda de cache-ttl**: poda la sesión una vez que el TTL de la caché
ha expirado y luego restablece la ventana de caché para que las solicitudes posteriores puedan reutilizar el
contexto recién almacenado en caché en lugar de volver a almacenar el historial completo. Esto mantiene los
costos de escritura de caché más bajos cuando una sesión queda inactiva después del TTL.

Configúralo en [Configuración del gateway](/es/gateway/configuration) y consulta los
detalles del comportamiento en [Poda de sesiones](/es/concepts/session-pruning).

Heartbeat puede mantener la caché **activa** durante períodos de inactividad. Si el TTL de caché de tu modelo
es `1h`, establecer el intervalo de heartbeat justo por debajo de eso (por ejemplo, `55m`) puede evitar
volver a almacenar el prompt completo, reduciendo los costos de escritura de caché.

En configuraciones con varios agentes, puedes mantener una configuración de modelo compartida y ajustar el comportamiento de caché
por agente con `agents.list[].params.cacheRetention`.

Para una guía completa opción por opción, consulta [Almacenamiento en caché de prompts](/es/reference/prompt-caching).

Para los precios de la API de Anthropic, las lecturas de caché son significativamente más baratas que los
tokens de entrada, mientras que las escrituras de caché se facturan con un multiplicador más alto. Consulta los
precios de almacenamiento en caché de prompts de Anthropic para ver las tarifas y multiplicadores TTL más recientes:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### Ejemplo: mantener activa la caché de 1h con heartbeat

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### Ejemplo: tráfico mixto con estrategia de caché por agente

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # línea base predeterminada para la mayoría de los agentes
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # mantener activa la caché larga para sesiones profundas
    - id: "alerts"
      params:
        cacheRetention: "none" # evitar escrituras de caché para notificaciones en ráfagas
```

`agents.list[].params` se fusiona sobre `params` del modelo seleccionado, así que puedes
sobrescribir solo `cacheRetention` y heredar sin cambios otros valores predeterminados del modelo.

### Ejemplo: habilitar el encabezado beta de contexto 1M de Anthropic

La ventana de contexto 1M de Anthropic está actualmente restringida por beta. OpenClaw puede inyectar el
valor requerido de `anthropic-beta` cuando habilitas `context1m` en modelos Opus
o Sonnet compatibles.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

Esto se asigna al encabezado beta `context-1m-2025-08-07` de Anthropic.

Esto solo se aplica cuando `context1m: true` está configurado en esa entrada del modelo.

Requisito: la credencial debe ser apta para uso de contexto largo. Si no lo es,
Anthropic responde con un error de límite de tasa del lado del proveedor para esa solicitud.

Si autenticas Anthropic con tokens OAuth/de suscripción (`sk-ant-oat-*`),
OpenClaw omite el encabezado beta `context-1m-*` porque Anthropic actualmente
rechaza esa combinación con HTTP 401.

## Consejos para reducir la presión de tokens

- Usa `/compact` para resumir sesiones largas.
- Recorta salidas grandes de herramientas en tus flujos de trabajo.
- Reduce `agents.defaults.imageMaxDimensionPx` para sesiones con muchas capturas de pantalla.
- Mantén breves las descripciones de Skills (la lista de Skills se inyecta en el prompt).
- Prefiere modelos más pequeños para trabajo exploratorio y verboso.

Consulta [Skills](/es/tools/skills) para la fórmula exacta de sobrecarga de la lista de Skills.
