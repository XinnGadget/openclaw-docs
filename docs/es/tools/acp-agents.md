---
read_when:
    - Ejecutar harnesses de codificación mediante ACP
    - Configurar sesiones ACP vinculadas a conversaciones en canales de mensajería
    - Vincular una conversación de un canal de mensajes a una sesión ACP persistente
    - Solucionar problemas del backend ACP y del cableado del plugin
    - Operar comandos `/acp` desde el chat
summary: Usa sesiones de tiempo de ejecución ACP para Codex, Claude Code, Cursor, Gemini CLI, OpenClaw ACP y otros agentes de harness
title: Agentes ACP
x-i18n:
    generated_at: "2026-04-07T05:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb651ab39b05e537398623ee06cb952a5a07730fc75d3f7e0de20dd3128e72c6
    source_path: tools/acp-agents.md
    workflow: 15
---

# Agentes ACP

Las sesiones de [Agent Client Protocol (ACP)](https://agentclientprotocol.com/) permiten que OpenClaw ejecute harnesses de codificación externos (por ejemplo Pi, Claude Code, Codex, Cursor, Copilot, OpenClaw ACP, OpenCode, Gemini CLI y otros harnesses ACPX compatibles) mediante un plugin de backend ACP.

Si le pides a OpenClaw en lenguaje natural que "ejecute esto en Codex" o "inicie Claude Code en un hilo", OpenClaw debería enrutar esa solicitud al tiempo de ejecución ACP (no al tiempo de ejecución nativo de subagentes). Cada creación de sesión ACP se rastrea como una [tarea en segundo plano](/es/automation/tasks).

Si quieres que Codex o Claude Code se conecten como cliente MCP externo directamente
a conversaciones de canal existentes de OpenClaw, usa [`openclaw mcp serve`](/cli/mcp)
en lugar de ACP.

## ¿Qué página quiero?

Hay tres superficies cercanas que es fácil confundir:

| Quieres...                                                                     | Usa esto                              | Notas                                                                                                       |
| ---------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Ejecutar Codex, Claude Code, Gemini CLI u otro harness externo _a través de_ OpenClaw | Esta página: Agentes ACP                 | Sesiones vinculadas al chat, `/acp spawn`, `sessions_spawn({ runtime: "acp" })`, tareas en segundo plano, controles de tiempo de ejecución |
| Exponer una sesión de OpenClaw Gateway _como_ servidor ACP para un editor o cliente      | [`openclaw acp`](/cli/acp)            | Modo puente. El IDE/cliente se comunica con OpenClaw mediante ACP sobre stdio/WebSocket                                          |
| Reutilizar una CLI local de IA como modelo de respaldo de solo texto                                 | [Backends CLI](/es/gateway/cli-backends) | No es ACP. Sin herramientas de OpenClaw, sin controles ACP, sin tiempo de ejecución de harness                                             |

## ¿Esto funciona de inmediato?

Normalmente sí.

- Las instalaciones nuevas ahora incluyen el plugin agrupado de tiempo de ejecución `acpx` habilitado de forma predeterminada.
- El plugin agrupado `acpx` prefiere su binario `acpx` fijado local al plugin.
- Al iniciar, OpenClaw sondea ese binario y lo autorrepara si hace falta.
- Empieza con `/acp doctor` si quieres una comprobación rápida de disponibilidad.

Lo que todavía puede ocurrir en el primer uso:

- Un adaptador de harness de destino puede descargarse bajo demanda con `npx` la primera vez que uses ese harness.
- La autenticación del proveedor sigue teniendo que existir en el host para ese harness.
- Si el host no tiene acceso a npm/red, las descargas del adaptador en la primera ejecución pueden fallar hasta que se precalienten las cachés o se instale el adaptador de otra forma.

Ejemplos:

- `/acp spawn codex`: OpenClaw debería estar listo para inicializar `acpx`, pero el adaptador ACP de Codex aún puede necesitar una descarga en la primera ejecución.
- `/acp spawn claude`: igual para el adaptador ACP de Claude, además de la autenticación del lado de Claude en ese host.

## Flujo rápido para operadores

Usa esto cuando quieras un runbook práctico de `/acp`:

1. Crea una sesión:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. Trabaja en la conversación o hilo vinculado (o apunta explícitamente a esa clave de sesión).
3. Comprueba el estado del tiempo de ejecución:
   - `/acp status`
4. Ajusta las opciones del tiempo de ejecución según sea necesario:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. Da una indicación a una sesión activa sin reemplazar el contexto:
   - `/acp steer tighten logging and continue`
6. Detén el trabajo:
   - `/acp cancel` (detiene el turno actual), o
   - `/acp close` (cierra la sesión + elimina vínculos)

## Inicio rápido para personas

Ejemplos de solicitudes naturales:

- "Vincula este canal de Discord a Codex."
- "Inicia una sesión persistente de Codex en un hilo aquí y mantenla enfocada."
- "Ejecuta esto como una sesión ACP de Claude Code de una sola vez y resume el resultado."
- "Vincula este chat de iMessage a Codex y mantén los seguimientos en el mismo espacio de trabajo."
- "Usa Gemini CLI para esta tarea en un hilo y luego mantén los seguimientos en ese mismo hilo."

Lo que OpenClaw debería hacer:

1. Elegir `runtime: "acp"`.
2. Resolver el destino de harness solicitado (`agentId`, por ejemplo `codex`).
3. Si se solicita un vínculo a la conversación actual y el canal activo lo admite, vincular la sesión ACP a esa conversación.
4. En caso contrario, si se solicita vínculo a hilo y el canal actual lo admite, vincular la sesión ACP al hilo.
5. Enrutar los mensajes vinculados de seguimiento a esa misma sesión ACP hasta que se desenfoque/cierre/caduque.

## ACP frente a subagentes

Usa ACP cuando quieras un tiempo de ejecución de harness externo. Usa subagentes cuando quieras ejecuciones delegadas nativas de OpenClaw.

| Área          | Sesión ACP                           | Ejecución de subagente                      |
| ------------- | ------------------------------------- | ---------------------------------- |
| Tiempo de ejecución       | Plugin de backend ACP (por ejemplo acpx) | Tiempo de ejecución nativo de subagente de OpenClaw  |
| Clave de sesión   | `agent:<agentId>:acp:<uuid>`          | `agent:<agentId>:subagent:<uuid>`  |
| Comandos principales | `/acp ...`                            | `/subagents ...`                   |
| Herramienta de creación    | `sessions_spawn` con `runtime:"acp"` | `sessions_spawn` (tiempo de ejecución predeterminado) |

Consulta también [Subagentes](/es/tools/subagents).

## Cómo ejecuta ACP Claude Code

Para Claude Code mediante ACP, la pila es:

1. Plano de control de sesión ACP de OpenClaw
2. plugin agrupado de tiempo de ejecución `acpx`
3. Adaptador ACP de Claude
4. Maquinaria de tiempo de ejecución/sesión del lado de Claude

Distinción importante:

- ACP Claude es una sesión de harness con controles ACP, reanudación de sesión, seguimiento de tareas en segundo plano y vínculo opcional a conversación/hilo.
- Los backends CLI son tiempos de ejecución locales de respaldo de solo texto independientes. Consulta [Backends CLI](/es/gateway/cli-backends).

Para operadores, la regla práctica es:

- si quieres `/acp spawn`, sesiones vinculables, controles de tiempo de ejecución o trabajo persistente de harness: usa ACP
- si quieres un respaldo local simple de texto mediante la CLI sin procesar: usa backends CLI

## Sesiones vinculadas

### Vínculos a la conversación actual

Usa `/acp spawn <harness> --bind here` cuando quieras que la conversación actual se convierta en un espacio de trabajo ACP duradero sin crear un hilo hijo.

Comportamiento:

- OpenClaw sigue siendo dueño del transporte del canal, la autenticación, la seguridad y la entrega.
- La conversación actual se fija a la clave de sesión ACP creada.
- Los mensajes de seguimiento en esa conversación se enrutan a la misma sesión ACP.
- `/new` y `/reset` restablecen esa misma sesión ACP vinculada en su lugar.
- `/acp close` cierra la sesión y elimina el vínculo con la conversación actual.

Qué significa esto en la práctica:

- `--bind here` mantiene la misma superficie de chat. En Discord, el canal actual sigue siendo el canal actual.
- `--bind here` aún puede crear una nueva sesión ACP si estás iniciando trabajo nuevo. El vínculo adjunta esa sesión a la conversación actual.
- `--bind here` no crea por sí solo un hilo hijo de Discord ni un tema de Telegram.
- El tiempo de ejecución ACP aún puede tener su propio directorio de trabajo (`cwd`) o espacio de trabajo en disco gestionado por el backend. Ese espacio de trabajo del tiempo de ejecución está separado de la superficie de chat y no implica un nuevo hilo de mensajería.
- Si creas una sesión para otro agente ACP y no pasas `--cwd`, OpenClaw hereda de forma predeterminada el espacio de trabajo del **agente de destino**, no el del solicitante.
- Si falta la ruta heredada del espacio de trabajo (`ENOENT`/`ENOTDIR`), OpenClaw recurre al `cwd` predeterminado del backend en lugar de reutilizar silenciosamente el árbol equivocado.
- Si el espacio de trabajo heredado existe pero no se puede acceder a él (por ejemplo `EACCES`), la creación devuelve el error real de acceso en lugar de omitir `cwd`.

Modelo mental:

- superficie de chat: donde la gente sigue hablando (`canal de Discord`, `tema de Telegram`, `chat de iMessage`)
- sesión ACP: el estado duradero del tiempo de ejecución Codex/Claude/Gemini al que OpenClaw enruta
- hilo/tema hijo: una superficie adicional opcional de mensajería creada solo por `--thread ...`
- espacio de trabajo del tiempo de ejecución: la ubicación del sistema de archivos donde se ejecuta el harness (`cwd`, checkout del repositorio, espacio de trabajo del backend)

Ejemplos:

- `/acp spawn codex --bind here`: mantén este chat, crea o adjunta una sesión ACP de Codex y enruta futuros mensajes aquí hacia ella
- `/acp spawn codex --thread auto`: OpenClaw puede crear un hilo/tema hijo y vincular allí la sesión ACP
- `/acp spawn codex --bind here --cwd /workspace/repo`: mismo vínculo de chat que arriba, pero Codex se ejecuta en `/workspace/repo`

Compatibilidad del vínculo a la conversación actual:

- Los canales de chat/mensajes que anuncian compatibilidad con vínculo a la conversación actual pueden usar `--bind here` a través de la ruta compartida de vínculo de conversación.
- Los canales con semántica personalizada de hilos/temas aún pueden proporcionar canonicalización específica del canal detrás de la misma interfaz compartida.
- `--bind here` siempre significa "vincular la conversación actual en su lugar".
- Los vínculos genéricos a la conversación actual usan el almacén compartido de vínculos de OpenClaw y sobreviven a reinicios normales del gateway.

Notas:

- `--bind here` y `--thread ...` son mutuamente excluyentes en `/acp spawn`.
- En Discord, `--bind here` vincula el canal o hilo actual en su lugar. `spawnAcpSessions` solo es necesario cuando OpenClaw necesita crear un hilo hijo para `--thread auto|here`.
- Si el canal activo no expone vínculos ACP a la conversación actual, OpenClaw devuelve un mensaje claro de no compatibilidad.
- `resume` y las preguntas de "nueva sesión" son preguntas de sesión ACP, no del canal. Puedes reutilizar o reemplazar el estado del tiempo de ejecución sin cambiar la superficie actual del chat.

### Sesiones vinculadas a hilos

Cuando los vínculos de hilo están habilitados para un adaptador de canal, las sesiones ACP pueden vincularse a hilos:

- OpenClaw vincula un hilo a una sesión ACP de destino.
- Los mensajes de seguimiento en ese hilo se enrutan a la sesión ACP vinculada.
- La salida ACP se entrega de vuelta al mismo hilo.
- Desenfocar/cerrar/archivar/caducidad por inactividad o por edad máxima elimina el vínculo.

La compatibilidad con vínculos de hilo es específica del adaptador. Si el adaptador de canal activo no admite vínculos de hilo, OpenClaw devuelve un mensaje claro de no compatibilidad/no disponibilidad.

Indicadores de función obligatorios para ACP vinculado a hilos:

- `acp.enabled=true`
- `acp.dispatch.enabled` está activado de forma predeterminada (establece `false` para pausar el despacho ACP)
- Indicador del adaptador de canal para creación de hilos ACP habilitado (específico del adaptador)
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### Canales compatibles con hilos

- Cualquier adaptador de canal que exponga capacidad de vínculo de sesión/hilo.
- Compatibilidad integrada actual:
  - Hilos/canales de Discord
  - Temas de Telegram (temas de foro en grupos/supergrupos y temas de MD)
- Los canales de plugin pueden agregar compatibilidad mediante la misma interfaz de vínculo.

## Configuración específica del canal

Para flujos no efímeros, configura vínculos ACP persistentes en entradas `bindings[]` de nivel superior.

### Modelo de vínculo

- `bindings[].type="acp"` marca un vínculo persistente de conversación ACP.
- `bindings[].match` identifica la conversación de destino:
  - Canal o hilo de Discord: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Tema de foro de Telegram: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - Chat grupal/MD de BlueBubbles: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Prefiere `chat_id:*` o `chat_identifier:*` para vínculos grupales estables.
  - Chat grupal/MD de iMessage: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    Prefiere `chat_id:*` para vínculos grupales estables.
- `bindings[].agentId` es el id del agente OpenClaw propietario.
- Las sobrescrituras ACP opcionales viven en `bindings[].acp`:
  - `mode` (`persistent` o `oneshot`)
  - `label`
  - `cwd`
  - `backend`

### Valores predeterminados de tiempo de ejecución por agente

Usa `agents.list[].runtime` para definir una vez los valores predeterminados ACP por agente:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent` (id de harness, por ejemplo `codex` o `claude`)
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

Precedencia de sobrescritura para sesiones ACP vinculadas:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. Valores predeterminados globales ACP (por ejemplo `acp.backend`)

Ejemplo:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

Comportamiento:

- OpenClaw garantiza que la sesión ACP configurada exista antes de usarla.
- Los mensajes en ese canal o tema se enrutan a la sesión ACP configurada.
- En conversaciones vinculadas, `/new` y `/reset` restablecen la misma clave de sesión ACP en su lugar.
- Los vínculos temporales de tiempo de ejecución (por ejemplo creados por flujos de enfoque de hilo) siguen aplicándose donde existan.
- Para creaciones ACP entre agentes sin `cwd` explícito, OpenClaw hereda el espacio de trabajo del agente de destino desde la configuración del agente.
- Las rutas de espacio de trabajo heredadas que faltan recurren al `cwd` predeterminado del backend; los fallos reales de acceso aparecen como errores de creación.

## Iniciar sesiones ACP (interfaces)

### Desde `sessions_spawn`

Usa `runtime: "acp"` para iniciar una sesión ACP desde un turno de agente o una llamada de herramienta.

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

Notas:

- `runtime` usa `subagent` de forma predeterminada, así que establece `runtime: "acp"` explícitamente para sesiones ACP.
- Si se omite `agentId`, OpenClaw usa `acp.defaultAgent` cuando está configurado.
- `mode: "session"` requiere `thread: true` para mantener una conversación persistente vinculada.

Detalles de la interfaz:

- `task` (obligatorio): prompt inicial enviado a la sesión ACP.
- `runtime` (obligatorio para ACP): debe ser `"acp"`.
- `agentId` (opcional): id del harness ACP de destino. Recurre a `acp.defaultAgent` si está configurado.
- `thread` (opcional, predeterminado `false`): solicita flujo de vínculo a hilo donde sea compatible.
- `mode` (opcional): `run` (una sola vez) o `session` (persistente).
  - el valor predeterminado es `run`
  - si `thread: true` y se omite el modo, OpenClaw puede usar comportamiento persistente de forma predeterminada según la ruta del tiempo de ejecución
  - `mode: "session"` requiere `thread: true`
- `cwd` (opcional): directorio de trabajo solicitado para el tiempo de ejecución (validado por la política del backend/tiempo de ejecución). Si se omite, la creación ACP hereda el espacio de trabajo del agente de destino cuando está configurado; las rutas heredadas que faltan recurren a los valores predeterminados del backend, mientras que los errores reales de acceso se devuelven.
- `label` (opcional): etiqueta visible para operadores usada en el texto de sesión/banner.
- `resumeSessionId` (opcional): reanuda una sesión ACP existente en lugar de crear una nueva. El agente reproduce su historial de conversación mediante `session/load`. Requiere `runtime: "acp"`.
- `streamTo` (opcional): `"parent"` transmite resúmenes del progreso inicial de la ejecución ACP de vuelta a la sesión solicitante como eventos del sistema.
  - Cuando está disponible, las respuestas aceptadas incluyen `streamLogPath` que apunta a un registro JSONL con alcance de sesión (`<sessionId>.acp-stream.jsonl`) que puedes seguir para ver el historial completo de retransmisión.

### Reanudar una sesión existente

Usa `resumeSessionId` para continuar una sesión ACP anterior en lugar de empezar desde cero. El agente reproduce su historial de conversación mediante `session/load`, así que retoma con el contexto completo de lo anterior.

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

Casos de uso comunes:

- Pasar una sesión de Codex de tu portátil a tu teléfono — decirle a tu agente que retome donde lo dejaste
- Continuar una sesión de codificación que empezaste de forma interactiva en la CLI, ahora de forma desatendida mediante tu agente
- Retomar trabajo que fue interrumpido por un reinicio del gateway o por tiempo de inactividad agotado

Notas:

- `resumeSessionId` requiere `runtime: "acp"` — devuelve un error si se usa con el tiempo de ejecución de subagente.
- `resumeSessionId` restaura el historial de conversación ACP ascendente; `thread` y `mode` siguen aplicándose normalmente a la nueva sesión OpenClaw que estás creando, así que `mode: "session"` sigue requiriendo `thread: true`.
- El agente de destino debe admitir `session/load` (Codex y Claude Code lo hacen).
- Si no se encuentra el id de sesión, la creación falla con un error claro — no hay recurso silencioso a una sesión nueva.

### Prueba smoke para operadores

Usa esto después de desplegar un gateway cuando quieras una comprobación live rápida de que la creación ACP
realmente funciona de extremo a extremo, no solo que pase pruebas unitarias.

Compuerta recomendada:

1. Verifica la versión/commit del gateway desplegado en el host de destino.
2. Confirma que el código fuente desplegado incluye la aceptación de linaje ACP en
   `src/gateway/sessions-patch.ts` (`subagent:* or acp:* sessions`).
3. Abre una sesión puente ACPX temporal hacia un agente live (por ejemplo
   `razor(main)` en `jpclawhq`).
4. Pídele a ese agente que llame a `sessions_spawn` con:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - tarea: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. Verifica que el agente informa:
   - `accepted=yes`
   - un `childSessionKey` real
   - sin error de validador
6. Limpia la sesión puente ACPX temporal.

Prompt de ejemplo para el agente live:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

Notas:

- Mantén esta prueba smoke en `mode: "run"` a menos que estés probando intencionadamente
  sesiones ACP persistentes vinculadas a hilos.
- No exijas `streamTo: "parent"` para la compuerta básica. Esa ruta depende de
  capacidades de la sesión/solicitante y es una comprobación de integración aparte.
- Trata las pruebas de `mode: "session"` vinculadas a hilos como una segunda pasada
  de integración más rica desde un hilo real de Discord o un tema de Telegram.

## Compatibilidad con sandbox

Actualmente, las sesiones ACP se ejecutan en el tiempo de ejecución del host, no dentro del sandbox de OpenClaw.

Limitaciones actuales:

- Si la sesión solicitante está en sandbox, la creación ACP se bloquea tanto para `sessions_spawn({ runtime: "acp" })` como para `/acp spawn`.
  - Error: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `sessions_spawn` con `runtime: "acp"` no admite `sandbox: "require"`.
  - Error: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

Usa `runtime: "subagent"` cuando necesites ejecución obligatoriamente dentro de sandbox.

### Desde el comando `/acp`

Usa `/acp spawn` para control explícito del operador desde el chat cuando sea necesario.

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

Indicadores clave:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

Consulta [Comandos slash](/es/tools/slash-commands).

## Resolución de destino de sesión

La mayoría de las acciones `/acp` aceptan un destino de sesión opcional (`session-key`, `session-id` o `session-label`).

Orden de resolución:

1. Argumento explícito de destino (o `--session` para `/acp steer`)
   - intenta por clave
   - luego por id de sesión con forma UUID
   - luego por etiqueta
2. Vínculo del hilo actual (si esta conversación/hilo está vinculado a una sesión ACP)
3. Recurso a la sesión solicitante actual

Los vínculos a la conversación actual y los vínculos a hilos participan ambos en el paso 2.

Si no se resuelve ningún destino, OpenClaw devuelve un error claro (`Unable to resolve session target: ...`).

## Modos de vínculo de creación

`/acp spawn` admite `--bind here|off`.

| Modo   | Comportamiento                                                               |
| ------ | ---------------------------------------------------------------------- |
| `here` | Vincula en su lugar la conversación activa actual; falla si no hay ninguna activa. |
| `off`  | No crea un vínculo a la conversación actual.                          |

Notas:

- `--bind here` es la ruta más simple para operadores para "hacer que este canal o chat esté respaldado por Codex".
- `--bind here` no crea un hilo hijo.
- `--bind here` solo está disponible en canales que exponen compatibilidad con vínculos a la conversación actual.
- `--bind` y `--thread` no pueden combinarse en la misma llamada `/acp spawn`.

## Modos de hilo de creación

`/acp spawn` admite `--thread auto|here|off`.

| Modo   | Comportamiento                                                                                            |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | En un hilo activo: vincula ese hilo. Fuera de un hilo: crea/vincula un hilo hijo cuando sea compatible. |
| `here` | Requiere el hilo activo actual; falla si no estás en uno.                                                  |
| `off`  | Sin vínculo. La sesión se inicia sin vincular.                                                                 |

Notas:

- En superficies sin vínculo a hilos, el comportamiento predeterminado es efectivamente `off`.
- La creación vinculada a hilos requiere compatibilidad de la política del canal:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- Usa `--bind here` cuando quieras fijar la conversación actual sin crear un hilo hijo.

## Controles ACP

Familia de comandos disponible:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status` muestra las opciones efectivas del tiempo de ejecución y, cuando están disponibles, tanto los identificadores de sesión a nivel de tiempo de ejecución como a nivel de backend.

Algunos controles dependen de las capacidades del backend. Si un backend no admite un control, OpenClaw devuelve un error claro de control no compatible.

## Recetario de comandos ACP

| Comando              | Qué hace                                              | Ejemplo                                                       |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn`         | Crea una sesión ACP; vínculo actual opcional o vínculo a hilo. | `/acp spawn codex --bind here --cwd /repo`                    |
| `/acp cancel`        | Cancela el turno en curso de la sesión de destino.                 | `/acp cancel agent:codex:acp:<uuid>`                          |
| `/acp steer`         | Envía una instrucción de dirección a la sesión en ejecución.                | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | Cierra la sesión y desvincula los destinos de hilo.                  | `/acp close`                                                  |
| `/acp status`        | Muestra backend, modo, estado, opciones de tiempo de ejecución y capacidades. | `/acp status`                                                 |
| `/acp set-mode`      | Establece el modo de tiempo de ejecución para la sesión de destino.                      | `/acp set-mode plan`                                          |
| `/acp set`           | Escritura genérica de opción de configuración del tiempo de ejecución.                      | `/acp set model openai/gpt-5.4`                               |
| `/acp cwd`           | Establece la sobrescritura del directorio de trabajo del tiempo de ejecución.                   | `/acp cwd /Users/user/Projects/repo`                          |
| `/acp permissions`   | Establece el perfil de política de aprobación.                              | `/acp permissions strict`                                     |
| `/acp timeout`       | Establece el tiempo de espera del tiempo de ejecución (segundos).                            | `/acp timeout 120`                                            |
| `/acp model`         | Establece la sobrescritura del modelo del tiempo de ejecución.                               | `/acp model anthropic/claude-opus-4-6`                        |
| `/acp reset-options` | Elimina sobrescrituras de opciones del tiempo de ejecución de la sesión.                  | `/acp reset-options`                                          |
| `/acp sessions`      | Lista sesiones ACP recientes del almacén.                      | `/acp sessions`                                               |
| `/acp doctor`        | Estado del backend, capacidades, correcciones accionables.           | `/acp doctor`                                                 |
| `/acp install`       | Imprime pasos deterministas de instalación y habilitación.             | `/acp install`                                                |

`/acp sessions` lee el almacén para la sesión actual vinculada o solicitante. Los comandos que aceptan tokens `session-key`, `session-id` o `session-label` resuelven destinos mediante el descubrimiento de sesiones del gateway, incluidas raíces personalizadas `session.store` por agente.

## Asignación de opciones de tiempo de ejecución

`/acp` tiene comandos de conveniencia y un configurador genérico.

Operaciones equivalentes:

- `/acp model <id>` se asigna a la clave de configuración del tiempo de ejecución `model`.
- `/acp permissions <profile>` se asigna a la clave de configuración del tiempo de ejecución `approval_policy`.
- `/acp timeout <seconds>` se asigna a la clave de configuración del tiempo de ejecución `timeout`.
- `/acp cwd <path>` actualiza directamente la sobrescritura de cwd del tiempo de ejecución.
- `/acp set <key> <value>` es la ruta genérica.
  - Caso especial: `key=cwd` usa la ruta de sobrescritura de cwd.
- `/acp reset-options` borra todas las sobrescrituras de tiempo de ejecución de la sesión de destino.

## Compatibilidad actual de harnesses acpx

Alias integrados actuales de harness en acpx:

- `claude`
- `codex`
- `copilot`
- `cursor` (Cursor CLI: `cursor-agent acp`)
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

Cuando OpenClaw usa el backend acpx, prefiere estos valores para `agentId` a menos que tu configuración de acpx defina alias de agentes personalizados.
Si tu instalación local de Cursor aún expone ACP como `agent acp`, sobrescribe el comando del agente `cursor` en tu configuración de acpx en lugar de cambiar el valor predeterminado integrado.

El uso directo de la CLI acpx también puede apuntar a adaptadores arbitrarios mediante `--agent <command>`, pero esa vía de escape sin procesar es una función de la CLI acpx (no la ruta normal `agentId` de OpenClaw).

## Configuración obligatoria

Línea base central de ACP:

```json5
{
  acp: {
    enabled: true,
    // Opcional. El valor predeterminado es true; establece false para pausar el despacho ACP mientras mantienes los controles /acp.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

La configuración de vínculo a hilos es específica del adaptador de canal. Ejemplo para Discord:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

Si la creación ACP vinculada a hilos no funciona, verifica primero el indicador de función del adaptador:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

Los vínculos a la conversación actual no requieren creación de hilo hijo. Requieren un contexto de conversación activo y un adaptador de canal que exponga vínculos ACP de conversación.

Consulta [Referencia de configuración](/es/gateway/configuration-reference).

## Configuración del plugin para el backend acpx

Las instalaciones nuevas incluyen el plugin agrupado de tiempo de ejecución `acpx` habilitado de forma predeterminada, así que ACP
normalmente funciona sin un paso manual de instalación del plugin.

Empieza con:

```text
/acp doctor
```

Si deshabilitaste `acpx`, lo denegaste mediante `plugins.allow` / `plugins.deny`, o quieres
cambiar a un checkout local de desarrollo, usa la ruta explícita del plugin:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

Instalación desde espacio de trabajo local durante el desarrollo:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

Luego verifica el estado del backend:

```text
/acp doctor
```

### Configuración de comando y versión de acpx

De forma predeterminada, el plugin agrupado de backend acpx (`acpx`) usa el binario fijado local al plugin:

1. El comando usa por defecto `node_modules/.bin/acpx` local al plugin dentro del paquete del plugin ACPX.
2. La versión esperada usa por defecto el pin de la extensión.
3. El inicio registra el backend ACP inmediatamente como no listo.
4. Un trabajo de verificación en segundo plano verifica `acpx --version`.
5. Si falta el binario local al plugin o hay una versión distinta, ejecuta:
   `npm install --omit=dev --no-save acpx@<pinned>` y vuelve a verificar.

Puedes sobrescribir comando/versión en la configuración del plugin:

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

Notas:

- `command` acepta una ruta absoluta, una ruta relativa o un nombre de comando (`acpx`).
- Las rutas relativas se resuelven desde el directorio de espacio de trabajo de OpenClaw.
- `expectedVersion: "any"` deshabilita la comprobación estricta de versión.
- Cuando `command` apunta a un binario/ruta personalizados, se deshabilita la autoinstalación local al plugin.
- El inicio de OpenClaw sigue sin bloquearse mientras se ejecuta la comprobación de estado del backend.

Consulta [Plugins](/es/tools/plugin).

### Instalación automática de dependencias

Cuando instalas OpenClaw globalmente con `npm install -g openclaw`, las dependencias de tiempo de ejecución de acpx
(binarios específicos de la plataforma) se instalan automáticamente
mediante un hook postinstall. Si falla la instalación automática, el gateway
sigue iniciándose normalmente e informa de la dependencia faltante mediante `openclaw acp doctor`.

### Puente MCP de herramientas de plugins

De forma predeterminada, las sesiones ACPX **no** exponen a
harnesses ACP las herramientas registradas por plugins de OpenClaw.

Si quieres que agentes ACP como Codex o Claude Code puedan llamar a
herramientas de plugins instalados de OpenClaw, como recuperación/almacenamiento de memoria, habilita el puente dedicado:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

Qué hace esto:

- Inyecta un servidor MCP integrado llamado `openclaw-plugin-tools` en el
  bootstrap de la sesión ACPX.
- Expone las herramientas de plugins ya registradas por plugins OpenClaw instalados y habilitados.
- Mantiene la función explícita y desactivada de forma predeterminada.

Notas de seguridad y confianza:

- Esto amplía la superficie de herramientas del harness ACP.
- Los agentes ACP obtienen acceso solo a las herramientas de plugins ya activas en el gateway.
- Trátalo como el mismo límite de confianza que permitir que esos plugins se ejecuten dentro
  del propio OpenClaw.
- Revisa los plugins instalados antes de habilitarlo.

Los `mcpServers` personalizados siguen funcionando como antes. El puente integrado de herramientas de plugins es una
comodidad adicional opt-in, no un reemplazo de la configuración genérica del servidor MCP.

## Configuración de permisos

Las sesiones ACP se ejecutan de forma no interactiva: no hay TTY para aprobar o denegar prompts de permisos de escritura de archivos y ejecución de shell. El plugin acpx proporciona dos claves de configuración que controlan cómo se gestionan los permisos:

Estos permisos de harness ACPX son independientes de las aprobaciones exec de OpenClaw y separados de indicadores de omisión del proveedor de backends CLI como Claude CLI `--permission-mode bypassPermissions`. ACPX `approve-all` es el interruptor de emergencia a nivel de harness para sesiones ACP.

### `permissionMode`

Controla qué operaciones puede realizar el agente de harness sin solicitar aprobación.

| Valor           | Comportamiento                                                  |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | Aprueba automáticamente todas las escrituras de archivos y comandos de shell.          |
| `approve-reads` | Aprueba automáticamente solo lecturas; las escrituras y `exec` requieren prompts. |
| `deny-all`      | Deniega todos los prompts de permisos.                              |

### `nonInteractivePermissions`

Controla qué ocurre cuando se mostraría un prompt de permisos pero no hay un TTY interactivo disponible (que es siempre el caso en las sesiones ACP).

| Valor  | Comportamiento                                                          |
| ------ | ----------------------------------------------------------------- |
| `fail` | Interrumpe la sesión con `AcpRuntimeError`. **(predeterminado)**           |
| `deny` | Deniega silenciosamente el permiso y continúa (degradación elegante). |

### Configuración

Configúralo mediante la configuración del plugin:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

Reinicia el gateway después de cambiar estos valores.

> **Importante:** OpenClaw actualmente usa de forma predeterminada `permissionMode=approve-reads` y `nonInteractivePermissions=fail`. En sesiones ACP no interactivas, cualquier escritura o ejecución que active un prompt de permisos puede fallar con `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`.
>
> Si necesitas restringir permisos, establece `nonInteractivePermissions` en `deny` para que las sesiones se degraden de forma elegante en lugar de fallar.

## Solución de problemas

| Síntoma                                                                     | Causa probable                                                                    | Solución                                                                                                                                                               |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | Falta el plugin de backend o está deshabilitado.                                             | Instala y habilita el plugin de backend, luego ejecuta `/acp doctor`.                                                                                                        |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP está deshabilitado globalmente.                                                          | Establece `acp.enabled=true`.                                                                                                                                           |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | El despacho desde mensajes normales del hilo está deshabilitado.                                  | Establece `acp.dispatch.enabled=true`.                                                                                                                                  |
| `ACP agent "<id>" is not allowed by policy`                                 | El agente no está en la lista permitida.                                                         | Usa un `agentId` permitido o actualiza `acp.allowedAgents`.                                                                                                              |
| `Unable to resolve session target: ...`                                     | Token de clave/id/etiqueta incorrecto.                                                         | Ejecuta `/acp sessions`, copia la clave/etiqueta exacta y vuelve a intentarlo.                                                                                                                 |
| `--bind here requires running /acp spawn inside an active ... conversation` | Se usó `--bind here` sin una conversación activa vinculable.                     | Muévete al chat/canal de destino y vuelve a intentarlo, o usa una creación sin vínculo.                                                                                                  |
| `Conversation bindings are unavailable for <channel>.`                      | El adaptador no tiene capacidad de vínculos ACP a la conversación actual.                      | Usa `/acp spawn ... --thread ...` donde sea compatible, configura `bindings[]` de nivel superior o muévete a un canal compatible.                                              |
| `--thread here requires running /acp spawn inside an active ... thread`     | Se usó `--thread here` fuera de un contexto de hilo.                                  | Muévete al hilo de destino o usa `--thread auto`/`off`.                                                                                                               |
| `Only <user-id> can rebind this channel/conversation/thread.`               | Otro usuario es dueño del destino de vínculo activo.                                    | Rehaz el vínculo como propietario o usa una conversación o hilo diferente.                                                                                                        |
| `Thread bindings are unavailable for <channel>.`                            | El adaptador no tiene capacidad de vínculo a hilos.                                        | Usa `--thread off` o muévete a un adaptador/canal compatible.                                                                                                          |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | El tiempo de ejecución ACP se ejecuta en el host; la sesión solicitante está en sandbox.                       | Usa `runtime="subagent"` desde sesiones en sandbox, o ejecuta la creación ACP desde una sesión fuera de sandbox.                                                                  |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | Se solicitó `sandbox="require"` para el tiempo de ejecución ACP.                                  | Usa `runtime="subagent"` para sandbox obligatorio, o usa ACP con `sandbox="inherit"` desde una sesión fuera de sandbox.                                               |
| Faltan metadatos ACP para la sesión vinculada                                      | Metadatos ACP obsoletos/eliminados de la sesión.                                             | Vuelve a crearla con `/acp spawn`, luego vuelve a vincular/enfocar el hilo.                                                                                                             |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode` bloquea escrituras/exec en una sesión ACP no interactiva.             | Establece `plugins.entries.acpx.config.permissionMode` en `approve-all` y reinicia el gateway. Consulta [Configuración de permisos](#permission-configuration).                 |
| La sesión ACP falla pronto con poca salida                                  | Los prompts de permisos están bloqueados por `permissionMode`/`nonInteractivePermissions`. | Revisa los logs del gateway para `AcpRuntimeError`. Para permisos completos, establece `permissionMode=approve-all`; para degradación elegante, establece `nonInteractivePermissions=deny`. |
| La sesión ACP se queda detenida indefinidamente después de completar el trabajo                       | El proceso del harness terminó pero la sesión ACP no informó de su finalización.             | Monitoriza con `ps aux \| grep acpx`; mata manualmente los procesos obsoletos.                                                                                                |
