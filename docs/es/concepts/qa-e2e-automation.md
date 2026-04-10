---
read_when:
    - Ampliación de qa-lab o qa-channel
    - Agregar escenarios de QA respaldados por el repositorio
    - Creación de automatización de QA de mayor realismo en torno al panel del Gateway
summary: Forma de la automatización privada de QA para qa-lab, qa-channel, escenarios con semilla e informes de protocolo
title: Automatización E2E de QA
x-i18n:
    generated_at: "2026-04-10T05:12:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 357d6698304ff7a8c4aa8a7be97f684d50f72b524740050aa761ac0ee68266de
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatización E2E de QA

La pila privada de QA está pensada para ejercitar OpenClaw de una forma más realista,
con forma de canal, que la que puede cubrir una sola prueba unitaria.

Piezas actuales:

- `extensions/qa-channel`: canal de mensajes sintético con superficies de MD, canal, hilo,
  reacción, edición y eliminación.
- `extensions/qa-lab`: interfaz de depuración y bus de QA para observar la transcripción,
  inyectar mensajes entrantes y exportar un informe en Markdown.
- `qa/`: recursos semilla respaldados por el repositorio para la tarea inicial y los
  escenarios de QA base.

El flujo actual del operador de QA es un sitio de QA de dos paneles:

- Izquierda: panel del Gateway (Control UI) con el agente.
- Derecha: QA Lab, que muestra la transcripción estilo Slack y el plan del escenario.

Ejecútalo con:

```bash
pnpm qa:lab:up
```

Eso compila el sitio de QA, inicia la ruta del gateway respaldada por Docker y expone la
página de QA Lab donde un operador o un bucle de automatización puede darle al agente una
misión de QA, observar el comportamiento real del canal y registrar qué funcionó, qué falló
o qué siguió bloqueado.

Para iterar más rápido en la interfaz de QA Lab sin reconstruir la imagen de Docker cada vez,
inicia la pila con un paquete de QA Lab montado por enlace:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene los servicios de Docker sobre una imagen precompilada y monta por enlace
`extensions/qa-lab/web/dist` dentro del contenedor `qa-lab`. `qa:lab:watch`
recompila ese paquete cuando hay cambios, y el navegador se recarga automáticamente cuando cambia el hash
del recurso de QA Lab.

Para una ruta desechable en una VM Linux sin incorporar Docker en la ruta de QA, ejecuta:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Esto arranca un guest nuevo de Multipass, instala dependencias, compila OpenClaw dentro del guest,
ejecuta `qa suite` y luego copia el informe y el resumen normales de QA de vuelta a `.artifacts/qa-e2e/...` en el host.
Reutiliza el mismo comportamiento de selección de escenarios que `qa suite` en el host.
Las ejecuciones en vivo reenvían las entradas de autenticación de QA compatibles que son prácticas para el
guest: claves de proveedor basadas en variables de entorno, la ruta de configuración del proveedor en vivo de QA y
`CODEX_HOME` cuando está presente. Mantén `--output-dir` bajo la raíz del repositorio para que el guest
pueda escribir de vuelta a través del espacio de trabajo montado.

## Semillas respaldadas por el repositorio

Los recursos semilla viven en `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Estos están intencionalmente en git para que el plan de QA sea visible tanto para las personas como para el
agente. La lista base debe seguir siendo lo bastante amplia para cubrir:

- chat por MD y por canal
- comportamiento de hilos
- ciclo de vida de acciones de mensajes
- callbacks de cron
- recuperación de memoria
- cambio de modelo
- traspaso a subagente
- lectura del repositorio y de la documentación
- una pequeña tarea de compilación como Lobster Invaders

## Informes

`qa-lab` exporta un informe de protocolo en Markdown a partir de la línea temporal observada del bus.
El informe debe responder:

- Qué funcionó
- Qué falló
- Qué siguió bloqueado
- Qué escenarios de seguimiento vale la pena agregar

Para comprobaciones de carácter y estilo, ejecuta el mismo escenario con múltiples referencias de modelos en vivo
y escribe un informe en Markdown evaluado:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

El comando ejecuta procesos secundarios locales del gateway de QA, no Docker. Los escenarios de evaluación de carácter
deben establecer la personalidad mediante `SOUL.md` y luego ejecutar turnos de usuario normales
como chat, ayuda del espacio de trabajo y pequeñas tareas sobre archivos. No se le debe indicar al modelo
candidato que está siendo evaluado. El comando conserva cada transcripción completa, registra estadísticas básicas de ejecución y
luego pide a los modelos jueces en modo rápido con razonamiento `xhigh` que clasifiquen las ejecuciones según
naturalidad, vibra y humor.
Usa `--blind-judge-models` al comparar proveedores: el prompt del juez sigue recibiendo
cada transcripción y el estado de la ejecución, pero las referencias candidatas se reemplazan por etiquetas neutrales
como `candidate-01`; el informe vuelve a asociar las clasificaciones con las referencias reales después
del análisis.
Las ejecuciones candidatas usan por defecto pensamiento `high`, con `xhigh` para modelos de OpenAI que
lo admiten. Sobrescribe un candidato específico en línea con
`--model provider/model,thinking=<level>`. `--thinking <level>` sigue estableciendo un
valor de respaldo global, y la forma anterior `--model-thinking <provider/model=level>` se
mantiene por compatibilidad.
Las referencias candidatas de OpenAI usan por defecto modo rápido para que se utilice el procesamiento prioritario cuando
el proveedor lo admite. Agrega `,fast`, `,no-fast` o `,fast=false` en línea cuando un
solo candidato o juez necesite una sobrescritura. Pasa `--fast` solo cuando quieras
forzar el modo rápido para todos los modelos candidatos. Las duraciones de candidatos y jueces se
registran en el informe para análisis comparativo, pero los prompts de los jueces indican explícitamente
que no deben clasificar por velocidad.
Tanto las ejecuciones de modelos candidatos como las de jueces usan por defecto concurrencia 16. Reduce
`--concurrency` o `--judge-concurrency` cuando los límites del proveedor o la presión local sobre el gateway
hagan que una ejecución sea demasiado ruidosa.
Cuando no se pasa ningún `--model` candidato, la evaluación de carácter usa por defecto
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` y
`google/gemini-3.1-pro-preview` cuando no se pasa ningún `--model`.
Cuando no se pasa ningún `--judge-model`, los jueces usan por defecto
`openai/gpt-5.4,thinking=xhigh,fast` y
`anthropic/claude-opus-4-6,thinking=high`.

## Documentación relacionada

- [Pruebas](/es/help/testing)
- [Canal de QA](/es/channels/qa-channel)
- [Panel](/web/dashboard)
