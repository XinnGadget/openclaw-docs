---
read_when:
    - Extender qa-lab o qa-channel
    - Agregar escenarios de QA respaldados por el repositorio
    - Crear automatización de QA de mayor realismo en torno al panel de Gateway
summary: Forma de la automatización de QA privada para qa-lab, qa-channel, escenarios con semillas e informes de protocolo
title: Automatización E2E de QA
x-i18n:
    generated_at: "2026-04-11T02:44:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5427b505e26bfd542e984e3920c3f7cb825473959195ba9737eff5da944c60d0
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatización E2E de QA

La pila de QA privada está pensada para ejercitar OpenClaw de una forma más realista,
con forma de canal, que la que puede ofrecer una sola prueba unitaria.

Componentes actuales:

- `extensions/qa-channel`: canal de mensajes sintético con superficies de MD, canal, hilo,
  reacción, edición y eliminación.
- `extensions/qa-lab`: interfaz de depuración y bus de QA para observar la transcripción,
  inyectar mensajes entrantes y exportar un informe en Markdown.
- `qa/`: recursos semilla respaldados por el repositorio para la tarea inicial y los
  escenarios base de QA.

El flujo actual del operador de QA es un sitio de QA de dos paneles:

- Izquierda: panel de Gateway (Control UI) con el agente.
- Derecha: QA Lab, que muestra la transcripción con estilo de Slack y el plan del escenario.

Ejecútalo con:

```bash
pnpm qa:lab:up
```

Eso compila el sitio de QA, inicia la ruta de Gateway respaldada por Docker y expone la
página de QA Lab donde un operador o un bucle de automatización puede asignarle al agente una
misión de QA, observar el comportamiento real del canal y registrar qué funcionó, qué falló o
qué siguió bloqueado.

Para una iteración más rápida de la interfaz de QA Lab sin reconstruir la imagen de Docker cada vez,
inicia la pila con un paquete de QA Lab montado mediante bind mount:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene los servicios de Docker sobre una imagen precompilada y monta mediante bind mount
`extensions/qa-lab/web/dist` en el contenedor `qa-lab`. `qa:lab:watch`
recompila ese paquete cuando hay cambios, y el navegador se recarga automáticamente cuando cambia el hash de recursos de QA Lab.

Para una ruta de smoke de Matrix con transporte real, ejecuta:

```bash
pnpm openclaw qa matrix
```

Esa ruta aprovisiona un homeserver Tuwunel desechable en Docker, registra
usuarios temporales de controlador, SUT y observador, crea una sala privada y luego ejecuta
el plugin real de Matrix dentro de un proceso hijo de Gateway de QA. La ruta de transporte en vivo mantiene
la configuración del proceso hijo limitada al transporte en prueba, por lo que Matrix se ejecuta sin
`qa-channel` en la configuración del proceso hijo.

Para una ruta de smoke de Telegram con transporte real, ejecuta:

```bash
pnpm openclaw qa telegram
```

Esa ruta usa un grupo privado real de Telegram en lugar de aprovisionar un servidor desechable.
Requiere `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` y
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, además de dos bots distintos en el mismo
grupo privado. El bot SUT debe tener un nombre de usuario de Telegram, y la observación entre bots
funciona mejor cuando ambos bots tienen habilitado el Modo de comunicación bot a bot
en `@BotFather`.

Las rutas de transporte en vivo ahora comparten un contrato más pequeño en lugar de que cada una invente
su propia forma de lista de escenarios.

`qa-channel` sigue siendo la suite amplia de comportamiento sintético del producto y no forma parte
de la matriz de cobertura de transporte en vivo.

| Ruta     | Canary | Restricción por mención | Bloqueo por allowlist | Respuesta de nivel superior | Reanudación tras reinicio | Seguimiento en hilo | Aislamiento de hilo | Observación de reacciones | Comando de ayuda |
| -------- | ------ | ----------------------- | --------------------- | --------------------------- | ------------------------- | ------------------- | ------------------- | ------------------------- | ---------------- |
| Matrix   | x      | x                       | x                     | x                           | x                         | x                   | x                   | x                         |                  |
| Telegram | x      |                         |                       |                             |                           |                     |                     |                           | x                |

Esto mantiene `qa-channel` como la suite amplia de comportamiento del producto, mientras que Matrix,
Telegram y futuros transportes en vivo comparten una lista explícita de verificación del contrato de transporte.

Para una ruta de VM Linux desechable sin incorporar Docker en la ruta de QA, ejecuta:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Esto inicia un guest nuevo de Multipass, instala dependencias, compila OpenClaw
dentro del guest, ejecuta `qa suite` y luego copia el informe y
resumen normales de QA de vuelta a `.artifacts/qa-e2e/...` en el host.
Reutiliza el mismo comportamiento de selección de escenarios que `qa suite` en el host.
Las ejecuciones en host y en Multipass ejecutan varios escenarios seleccionados en paralelo
con workers de Gateway aislados de forma predeterminada, hasta 64 workers o la cantidad de
escenarios seleccionados. Usa `--concurrency <count>` para ajustar la cantidad de workers, o
`--concurrency 1` para una ejecución en serie.
Las ejecuciones en vivo reenvían las entradas de autenticación de QA compatibles que son prácticas para el
guest: claves de proveedor basadas en variables de entorno, la ruta de configuración del proveedor en vivo de QA y
`CODEX_HOME` cuando está presente. Mantén `--output-dir` bajo la raíz del repositorio para que el guest
pueda escribir de vuelta a través del espacio de trabajo montado.

## Semillas respaldadas por el repositorio

Los recursos semilla viven en `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Estos están intencionalmente en git para que el plan de QA sea visible tanto para las personas como para el
agente. La lista base debe seguir siendo lo suficientemente amplia como para cubrir:

- chat por MD y por canal
- comportamiento de hilos
- ciclo de vida de acciones de mensajes
- callbacks de cron
- recuperación de memoria
- cambio de modelo
- transferencia a subagente
- lectura del repositorio y de la documentación
- una pequeña tarea de compilación como Lobster Invaders

## Informes

`qa-lab` exporta un informe de protocolo en Markdown a partir de la cronología observada del bus.
El informe debe responder:

- Qué funcionó
- Qué falló
- Qué siguió bloqueado
- Qué escenarios de seguimiento vale la pena agregar

Para verificaciones de carácter y estilo, ejecuta el mismo escenario con varias referencias de modelos en vivo
y escribe un informe evaluado en Markdown:

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

El comando ejecuta procesos hijo locales de Gateway de QA, no Docker. Los
escenarios de evaluación de carácter deben establecer la persona mediante `SOUL.md`, y luego ejecutar turnos
ordinarios de usuario como chat, ayuda sobre el espacio de trabajo y pequeñas tareas sobre archivos. No se debe informar
al modelo candidato de que está siendo evaluado. El comando conserva cada transcripción
completa, registra estadísticas básicas de ejecución y luego pide a los modelos jueces en modo fast con
razonamiento `xhigh` que clasifiquen las ejecuciones por naturalidad, vibra y humor.
Usa `--blind-judge-models` al comparar proveedores: el prompt del juez sigue recibiendo
cada transcripción y estado de ejecución, pero las referencias candidatas se sustituyen por etiquetas
neutras como `candidate-01`; el informe vuelve a mapear las clasificaciones a las referencias reales después
del análisis.
Las ejecuciones candidatas usan de forma predeterminada razonamiento `high`, con `xhigh` para modelos de OpenAI que
lo admiten. Sobrescribe un candidato específico en línea con
`--model provider/model,thinking=<level>`. `--thinking <level>` sigue estableciendo un
valor de respaldo global, y la forma antigua `--model-thinking <provider/model=level>` se
mantiene por compatibilidad.
Las referencias candidatas de OpenAI usan de forma predeterminada el modo fast para que se use procesamiento prioritario
cuando el proveedor lo admita. Agrega `,fast`, `,no-fast` o `,fast=false` en línea cuando un
solo candidato o juez necesite una sobrescritura. Pasa `--fast` solo cuando quieras
forzar el modo fast para todos los modelos candidatos. Las duraciones de candidatos y jueces se
registran en el informe para análisis comparativo, pero los prompts de los jueces indican explícitamente
que no deben clasificar por velocidad.
Tanto las ejecuciones de modelos candidatos como las de jueces usan de forma predeterminada concurrencia 16. Reduce
`--concurrency` o `--judge-concurrency` cuando los límites del proveedor o la presión del Gateway local
hagan que una ejecución tenga demasiado ruido.
Cuando no se pasa ningún `--model` candidato, la evaluación de carácter usa por defecto
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` y
`google/gemini-3.1-pro-preview` cuando no se pasa `--model`.
Cuando no se pasa `--judge-model`, los jueces usan por defecto
`openai/gpt-5.4,thinking=xhigh,fast` y
`anthropic/claude-opus-4-6,thinking=high`.

## Documentación relacionada

- [Testing](/es/help/testing)
- [QA Channel](/es/channels/qa-channel)
- [Panel](/web/dashboard)
