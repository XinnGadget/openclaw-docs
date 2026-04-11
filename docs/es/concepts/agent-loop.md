---
read_when:
    - Necesitas una guía exacta del bucle del agente o de los eventos del ciclo de vida
summary: Ciclo de vida del bucle del agente, flujos y semántica de espera
title: Bucle del agente
x-i18n:
    generated_at: "2026-04-11T02:44:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: b6831a5b11e9100e49f650feca51ab44a2bef242ce1b5db2766d0b3b5c5ba729
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Bucle del agente (OpenClaw)

Un bucle agéntico es la ejecución “real” completa de un agente: entrada → ensamblaje de contexto → inferencia del modelo →
ejecución de herramientas → respuestas en streaming → persistencia. Es la ruta autoritativa que convierte un mensaje
en acciones y una respuesta final, mientras mantiene coherente el estado de la sesión.

En OpenClaw, un bucle es una ejecución única y serializada por sesión que emite eventos de ciclo de vida y de stream
mientras el modelo razona, llama herramientas y transmite salida. Este documento explica cómo está conectado ese bucle
auténtico de extremo a extremo.

## Puntos de entrada

- RPC del Gateway: `agent` y `agent.wait`.
- CLI: comando `agent`.

## Cómo funciona (alto nivel)

1. El RPC `agent` valida los parámetros, resuelve la sesión (`sessionKey`/`sessionId`), persiste los metadatos de la sesión y devuelve `{ runId, acceptedAt }` de inmediato.
2. `agentCommand` ejecuta el agente:
   - resuelve el modelo + valores predeterminados de thinking/verbose
   - carga la instantánea de Skills
   - llama a `runEmbeddedPiAgent` (runtime de pi-agent-core)
   - emite **lifecycle end/error** si el bucle embebido no emite uno
3. `runEmbeddedPiAgent`:
   - serializa las ejecuciones mediante colas por sesión + globales
   - resuelve el modelo + perfil de autenticación y construye la sesión de pi
   - se suscribe a los eventos de pi y transmite deltas del asistente/herramientas
   - aplica el tiempo de espera -> aborta la ejecución si se supera
   - devuelve cargas útiles + metadatos de uso
4. `subscribeEmbeddedPiSession` conecta los eventos de pi-agent-core con el stream `agent` de OpenClaw:
   - eventos de herramientas => `stream: "tool"`
   - deltas del asistente => `stream: "assistant"`
   - eventos de ciclo de vida => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` usa `waitForAgentRun`:
   - espera **lifecycle end/error** para `runId`
   - devuelve `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## Encolado + concurrencia

- Las ejecuciones se serializan por clave de sesión (carril de sesión) y opcionalmente mediante un carril global.
- Esto evita carreras de herramientas/sesión y mantiene coherente el historial de la sesión.
- Los canales de mensajería pueden elegir modos de cola (collect/steer/followup) que alimentan este sistema de carriles.
  Consulta [Command Queue](/es/concepts/queue).

## Preparación de sesión + espacio de trabajo

- El espacio de trabajo se resuelve y se crea; las ejecuciones en sandbox pueden redirigir a una raíz de espacio de trabajo en sandbox.
- Se cargan las Skills (o se reutilizan desde una instantánea) y se inyectan en el entorno y en el prompt.
- Los archivos de bootstrap/contexto se resuelven y se inyectan en el informe del system prompt.
- Se adquiere un bloqueo de escritura de sesión; `SessionManager` se abre y se prepara antes del streaming.

## Ensamblaje del prompt + system prompt

- El system prompt se construye a partir del prompt base de OpenClaw, el prompt de Skills, el contexto de bootstrap y las anulaciones por ejecución.
- Se aplican límites específicos del modelo y reservas de tokens para compaction.
- Consulta [System prompt](/es/concepts/system-prompt) para ver lo que ve el modelo.

## Puntos de hook (donde puedes interceptar)

OpenClaw tiene dos sistemas de hooks:

- **Hooks internos** (hooks del Gateway): scripts orientados a eventos para comandos y eventos de ciclo de vida.
- **Hooks de plugin**: puntos de extensión dentro del ciclo de vida del agente/herramienta y de la canalización del gateway.

### Hooks internos (hooks del Gateway)

- **`agent:bootstrap`**: se ejecuta mientras se construyen los archivos de bootstrap antes de que se finalice el system prompt.
  Úsalo para agregar o quitar archivos de contexto de bootstrap.
- **Hooks de comandos**: `/new`, `/reset`, `/stop` y otros eventos de comandos (consulta la documentación de Hooks).

Consulta [Hooks](/es/automation/hooks) para ver la configuración y ejemplos.

### Hooks de plugin (ciclo de vida del agente + gateway)

Estos se ejecutan dentro del bucle del agente o de la canalización del gateway:

- **`before_model_resolve`**: se ejecuta antes de la sesión (sin `messages`) para anular de forma determinista el proveedor/modelo antes de la resolución del modelo.
- **`before_prompt_build`**: se ejecuta después de cargar la sesión (con `messages`) para inyectar `prependContext`, `systemPrompt`, `prependSystemContext` o `appendSystemContext` antes de enviar el prompt. Usa `prependContext` para texto dinámico por turno y los campos de contexto del sistema para una guía estable que deba ubicarse en el espacio del system prompt.
- **`before_agent_start`**: hook heredado de compatibilidad que puede ejecutarse en cualquiera de las dos fases; prefiere los hooks explícitos anteriores.
- **`before_agent_reply`**: se ejecuta después de las acciones inline y antes de la llamada al LLM, lo que permite que un plugin reclame el turno y devuelva una respuesta sintética o silencie por completo el turno.
- **`agent_end`**: inspecciona la lista final de mensajes y los metadatos de la ejecución después de completarse.
- **`before_compaction` / `after_compaction`**: observan o anotan ciclos de compaction.
- **`before_tool_call` / `after_tool_call`**: interceptan parámetros/resultados de herramientas.
- **`before_install`**: inspecciona los hallazgos del escaneo integrado y, opcionalmente, bloquea instalaciones de Skills o plugins.
- **`tool_result_persist`**: transforma sincrónicamente los resultados de herramientas antes de que se escriban en la transcripción de la sesión.
- **`message_received` / `message_sending` / `message_sent`**: hooks de mensajes entrantes + salientes.
- **`session_start` / `session_end`**: límites del ciclo de vida de la sesión.
- **`gateway_start` / `gateway_stop`**: eventos del ciclo de vida del gateway.

Reglas de decisión de hooks para protecciones de salida/herramientas:

- `before_tool_call`: `{ block: true }` es terminal y detiene los controladores de menor prioridad.
- `before_tool_call`: `{ block: false }` no hace nada y no elimina un bloqueo previo.
- `before_install`: `{ block: true }` es terminal y detiene los controladores de menor prioridad.
- `before_install`: `{ block: false }` no hace nada y no elimina un bloqueo previo.
- `message_sending`: `{ cancel: true }` es terminal y detiene los controladores de menor prioridad.
- `message_sending`: `{ cancel: false }` no hace nada y no elimina una cancelación previa.

Consulta [Plugin hooks](/es/plugins/architecture#provider-runtime-hooks) para la API de hooks y los detalles de registro.

## Streaming + respuestas parciales

- Los deltas del asistente se transmiten desde pi-agent-core y se emiten como eventos `assistant`.
- El streaming por bloques puede emitir respuestas parciales en `text_end` o en `message_end`.
- El streaming de razonamiento puede emitirse como un stream independiente o como respuestas por bloques.
- Consulta [Streaming](/es/concepts/streaming) para ver el comportamiento de fragmentación y respuestas por bloques.

## Ejecución de herramientas + herramientas de mensajería

- Los eventos de inicio/actualización/fin de herramientas se emiten en el stream `tool`.
- Los resultados de herramientas se sanitizan por tamaño y cargas útiles de imagen antes de registrarse/emitirse.
- Los envíos de herramientas de mensajería se rastrean para suprimir confirmaciones duplicadas del asistente.

## Moldeado de respuestas + supresión

- Las cargas útiles finales se ensamblan a partir de:
  - texto del asistente (y razonamiento opcional)
  - resúmenes inline de herramientas (cuando verbose + permitido)
  - texto de error del asistente cuando el modelo genera un error
- El token silencioso exacto `NO_REPLY` / `no_reply` se filtra de las
  cargas útiles salientes.
- Los duplicados de herramientas de mensajería se eliminan de la lista final de cargas útiles.
- Si no quedan cargas útiles renderizables y una herramienta produjo un error, se emite
  una respuesta alternativa de error de herramienta
  (a menos que una herramienta de mensajería ya haya enviado una respuesta visible para el usuario).

## Compaction + reintentos

- La compaction automática emite eventos de stream `compaction` y puede activar un reintento.
- En el reintento, los búferes en memoria y los resúmenes de herramientas se restablecen para evitar salida duplicada.
- Consulta [Compaction](/es/concepts/compaction) para ver la canalización de compaction.

## Streams de eventos (actualmente)

- `lifecycle`: emitido por `subscribeEmbeddedPiSession` (y como alternativa por `agentCommand`)
- `assistant`: deltas transmitidos desde pi-agent-core
- `tool`: eventos de herramientas transmitidos desde pi-agent-core

## Manejo del canal de chat

- Los deltas del asistente se almacenan en búfer en mensajes `delta` de chat.
- Un `final` de chat se emite en **lifecycle end/error**.

## Tiempos de espera

- Valor predeterminado de `agent.wait`: 30 s (solo la espera). El parámetro `timeoutMs` lo anula.
- Runtime del agente: valor predeterminado de `agents.defaults.timeoutSeconds` 172800 s (48 horas); se aplica en el temporizador de aborto de `runEmbeddedPiAgent`.
- Tiempo de espera de inactividad del LLM: `agents.defaults.llm.idleTimeoutSeconds` aborta una solicitud al modelo cuando no llegan fragmentos de respuesta antes de la ventana de inactividad. Configúralo explícitamente para modelos locales lentos o proveedores de razonamiento/llamada de herramientas; configúralo en 0 para desactivarlo. Si no está configurado, OpenClaw usa `agents.defaults.timeoutSeconds` cuando está configurado; de lo contrario, 120 s. Las ejecuciones activadas por cron sin un tiempo de espera explícito del LLM o del agente desactivan el watchdog de inactividad y dependen del tiempo de espera externo del cron.

## Dónde las cosas pueden terminar antes de tiempo

- Tiempo de espera del agente (aborto)
- AbortSignal (cancelación)
- Desconexión del gateway o tiempo de espera del RPC
- Tiempo de espera de `agent.wait` (solo de espera, no detiene al agente)

## Relacionado

- [Tools](/es/tools) — herramientas de agente disponibles
- [Hooks](/es/automation/hooks) — scripts orientados a eventos activados por eventos del ciclo de vida del agente
- [Compaction](/es/concepts/compaction) — cómo se resumen las conversaciones largas
- [Exec Approvals](/es/tools/exec-approvals) — puertas de aprobación para comandos de shell
- [Thinking](/es/tools/thinking) — configuración del nivel de thinking/razonamiento
