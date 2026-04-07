---
read_when:
    - Quieres entender qué significa “context” en OpenClaw
    - Estás depurando por qué el modelo “sabe” algo (o lo olvidó)
    - Quieres reducir la sobrecarga de contexto (`/context`, `/status`, `/compact`)
summary: 'Contexto: lo que ve el modelo, cómo se construye y cómo inspeccionarlo'
title: Contexto
x-i18n:
    generated_at: "2026-04-07T05:01:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: a75b4cd65bf6385d46265b9ce1643310bc99d220e35ec4b4924096bed3ca4aa0
    source_path: concepts/context.md
    workflow: 15
---

# Contexto

“Context” es **todo lo que OpenClaw envía al modelo para una ejecución**. Está limitado por la **ventana de contexto** del modelo (límite de tokens).

Modelo mental para principiantes:

- **Prompt del sistema** (construido por OpenClaw): reglas, herramientas, lista de Skills, hora/entorno de ejecución y archivos del espacio de trabajo inyectados.
- **Historial de conversación**: tus mensajes + los mensajes del asistente para esta sesión.
- **Llamadas/resultados de herramientas + adjuntos**: salida de comandos, lecturas de archivos, imágenes/audio, etc.

El contexto _no es lo mismo_ que la “memoria”: la memoria puede almacenarse en disco y volver a cargarse más tarde; el contexto es lo que está dentro de la ventana actual del modelo.

## Inicio rápido (inspeccionar el contexto)

- `/status` → vista rápida de “¿qué tan llena está mi ventana?” + configuración de la sesión.
- `/context list` → qué está inyectado + tamaños aproximados (por archivo + totales).
- `/context detail` → desglose más profundo: tamaños por archivo, tamaños por esquema de herramienta, tamaños por entrada de Skill y tamaño del prompt del sistema.
- `/usage tokens` → añade un pie de uso por respuesta a las respuestas normales.
- `/compact` → resume el historial anterior en una entrada compacta para liberar espacio en la ventana.

Consulta también: [Comandos slash](/es/tools/slash-commands), [Uso y costos de tokens](/es/reference/token-use), [Compactación](/es/concepts/compaction).

## Salida de ejemplo

Los valores varían según el modelo, el proveedor, la política de herramientas y lo que haya en tu espacio de trabajo.

### `/context list`

```
🧠 Desglose del contexto
Espacio de trabajo: <workspaceDir>
Máx./archivo de bootstrap: 20,000 caracteres
Sandbox: mode=non-main sandboxed=false
Prompt del sistema (ejecución): 38,412 caracteres (~9,603 tok) (Project Context 23,901 caracteres (~5,976 tok))

Archivos del espacio de trabajo inyectados:
- AGENTS.md: OK | bruto 1,742 caracteres (~436 tok) | inyectado 1,742 caracteres (~436 tok)
- SOUL.md: OK | bruto 912 caracteres (~228 tok) | inyectado 912 caracteres (~228 tok)
- TOOLS.md: TRUNCADO | bruto 54,210 caracteres (~13,553 tok) | inyectado 20,962 caracteres (~5,241 tok)
- IDENTITY.md: OK | bruto 211 caracteres (~53 tok) | inyectado 211 caracteres (~53 tok)
- USER.md: OK | bruto 388 caracteres (~97 tok) | inyectado 388 caracteres (~97 tok)
- HEARTBEAT.md: AUSENTE | bruto 0 | inyectado 0
- BOOTSTRAP.md: OK | bruto 0 caracteres (~0 tok) | inyectado 0 caracteres (~0 tok)

Lista de Skills (texto del prompt del sistema): 2,184 caracteres (~546 tok) (12 skills)
Herramientas: read, edit, write, exec, process, browser, message, sessions_send, …
Lista de herramientas (texto del prompt del sistema): 1,032 caracteres (~258 tok)
Esquemas de herramientas (JSON): 31,988 caracteres (~7,997 tok) (cuentan para el contexto; no se muestran como texto)
Herramientas: (igual que arriba)

Tokens de sesión (en caché): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Desglose del contexto (detallado)
…
Principales Skills (tamaño de entrada en el prompt):
- frontend-design: 412 caracteres (~103 tok)
- oracle: 401 caracteres (~101 tok)
… (+10 más skills)

Principales herramientas (tamaño del esquema):
- browser: 9,812 caracteres (~2,453 tok)
- exec: 6,240 caracteres (~1,560 tok)
… (+N más herramientas)
```

## Qué cuenta para la ventana de contexto

Todo lo que recibe el modelo cuenta, incluido lo siguiente:

- Prompt del sistema (todas las secciones).
- Historial de conversación.
- Llamadas de herramientas + resultados de herramientas.
- Adjuntos/transcripciones (imágenes/audio/archivos).
- Resúmenes de compactación y artefactos de poda.
- “Wrappers” del proveedor o encabezados ocultos (no visibles, pero siguen contando).

## Cómo OpenClaw construye el prompt del sistema

El prompt del sistema **pertenece a OpenClaw** y se reconstruye en cada ejecución. Incluye:

- Lista de herramientas + descripciones breves.
- Lista de Skills (solo metadatos; ver abajo).
- Ubicación del espacio de trabajo.
- Hora (UTC + hora del usuario convertida si está configurada).
- Metadatos del entorno de ejecución (host/SO/modelo/thinking).
- Archivos bootstrap del espacio de trabajo inyectados en **Project Context**.

Desglose completo: [Prompt del sistema](/es/concepts/system-prompt).

## Archivos del espacio de trabajo inyectados (Project Context)

De forma predeterminada, OpenClaw inyecta un conjunto fijo de archivos del espacio de trabajo (si están presentes):

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (solo en la primera ejecución)

Los archivos grandes se truncan por archivo usando `agents.defaults.bootstrapMaxChars` (valor predeterminado: `20000` caracteres). OpenClaw también aplica un límite total de inyección de bootstrap entre archivos con `agents.defaults.bootstrapTotalMaxChars` (valor predeterminado: `150000` caracteres). `/context` muestra los tamaños **bruto vs. inyectado** y si hubo truncamiento.

Cuando se produce truncamiento, el entorno de ejecución puede inyectar un bloque de advertencia dentro del prompt en Project Context. Configúralo con `agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`; valor predeterminado `once`).

## Skills: inyectadas vs. cargadas bajo demanda

El prompt del sistema incluye una **lista de Skills** compacta (nombre + descripción + ubicación). Esta lista tiene una sobrecarga real.

Las instrucciones de la Skill _no_ se incluyen de forma predeterminada. Se espera que el modelo haga `read` del `SKILL.md` de la Skill **solo cuando sea necesario**.

## Herramientas: hay dos costos

Las herramientas afectan al contexto de dos maneras:

1. **Texto de la lista de herramientas** en el prompt del sistema (lo que ves como “Tooling”).
2. **Esquemas de herramientas** (JSON). Estos se envían al modelo para que pueda llamar herramientas. Cuentan para el contexto aunque no los veas como texto plano.

`/context detail` desglosa los esquemas de herramientas más grandes para que puedas ver qué es lo que más pesa.

## Comandos, directivas y "atajos en línea"

Los comandos slash los gestiona el Gateway. Hay varios comportamientos distintos:

- **Comandos independientes**: un mensaje que es solo `/...` se ejecuta como un comando.
- **Directivas**: `/think`, `/verbose`, `/reasoning`, `/elevated`, `/model`, `/queue` se eliminan antes de que el modelo vea el mensaje.
  - Los mensajes que contienen solo directivas conservan la configuración de la sesión.
  - Las directivas en línea dentro de un mensaje normal actúan como sugerencias por mensaje.
- **Atajos en línea** (solo remitentes incluidos en la allowlist): ciertos tokens `/...` dentro de un mensaje normal pueden ejecutarse de inmediato (ejemplo: “hey /status”), y se eliminan antes de que el modelo vea el texto restante.

Detalles: [Comandos slash](/es/tools/slash-commands).

## Sesiones, compactación y poda (qué persiste)

Lo que persiste entre mensajes depende del mecanismo:

- **El historial normal** persiste en la transcripción de la sesión hasta que se compacta o se poda según la política.
- **La compactación** conserva un resumen en la transcripción y mantiene intactos los mensajes recientes.
- **La poda** elimina resultados antiguos de herramientas del prompt _en memoria_ para una ejecución, pero no reescribe la transcripción.

Documentación: [Sesión](/es/concepts/session), [Compactación](/es/concepts/compaction), [Poda de sesión](/es/concepts/session-pruning).

De forma predeterminada, OpenClaw usa el motor de contexto `legacy` integrado para el ensamblado y la compactación. Si instalas un plugin que proporciona `kind: "context-engine"` y lo seleccionas con `plugins.slots.contextEngine`, OpenClaw delega el ensamblado del contexto, `/compact` y los hooks relacionados del ciclo de vida del contexto del subagente a ese motor. `ownsCompaction: false` no vuelve automáticamente al motor legacy; el motor activo aún debe implementar `compact()` correctamente. Consulta [Context Engine](/es/concepts/context-engine) para ver la interfaz conectable completa, los hooks del ciclo de vida y la configuración.

## Qué informa realmente `/context`

`/context` prefiere el informe más reciente del prompt del sistema **construido en ejecución** cuando está disponible:

- `System prompt (run)` = capturado de la última ejecución embebida (con capacidad de herramientas) y persistido en el almacenamiento de la sesión.
- `System prompt (estimate)` = calculado sobre la marcha cuando no existe un informe de ejecución (o cuando se ejecuta mediante un backend CLI que no genera el informe).

En ambos casos, informa los tamaños y los principales contribuyentes; **no** vuelca el prompt del sistema completo ni los esquemas de herramientas.

## Relacionado

- [Context Engine](/es/concepts/context-engine) — inyección de contexto personalizada mediante plugins
- [Compactación](/es/concepts/compaction) — resumir conversaciones largas
- [Prompt del sistema](/es/concepts/system-prompt) — cómo se construye el prompt del sistema
- [Bucle del agente](/es/concepts/agent-loop) — el ciclo completo de ejecución del agente
