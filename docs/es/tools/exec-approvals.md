---
read_when:
    - Configurar aprobaciones o allowlists de exec
    - Implementar la UX de aprobación de exec en la app de macOS
    - Revisar los prompts de salida del sandbox y sus implicaciones
summary: Aprobaciones de exec, allowlists y prompts de salida del sandbox
title: Aprobaciones de exec
x-i18n:
    generated_at: "2026-04-11T02:47:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5f4a2e2f1f3c13a1d1926c9de0720513ea8a74d1ca571dbe74b188d8c560c14c
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Aprobaciones de exec

Las aprobaciones de exec son la **protección de la app complementaria / host del nodo** para permitir que un agente en sandbox ejecute
comandos en un host real (`gateway` o `node`). Piensa en ello como un interbloqueo de seguridad:
los comandos solo se permiten cuando la política + la allowlist + la aprobación del usuario (opcional) coinciden.
Las aprobaciones de exec son **adicionales** a la política de herramientas y al control elevated (salvo que elevated se establezca en `full`, que omite las aprobaciones).
La política efectiva es la **más estricta** entre `tools.exec.*` y los valores predeterminados de aprobaciones; si se omite un campo de aprobaciones, se usa el valor de `tools.exec`.
La ejecución en host también usa el estado local de aprobaciones en esa máquina. Un valor local del host
`ask: "always"` en `~/.openclaw/exec-approvals.json` sigue mostrando prompts incluso si
la sesión o los valores predeterminados de la configuración solicitan `ask: "on-miss"`.
Usa `openclaw approvals get`, `openclaw approvals get --gateway` o
`openclaw approvals get --node <id|name|ip>` para inspeccionar la política solicitada,
las fuentes de política del host y el resultado efectivo.
Para la máquina local, `openclaw exec-policy show` expone la misma vista fusionada y
`openclaw exec-policy set|preset` puede sincronizar en un solo paso la política solicitada local con el
archivo local de aprobaciones del host. Cuando un alcance local solicita `host=node`,
`openclaw exec-policy show` informa ese alcance como administrado por el nodo en runtime en lugar de
pretender que el archivo local de aprobaciones sea la fuente de verdad efectiva.

Si la UI de la app complementaria **no está disponible**, cualquier solicitud que requiera un prompt se
resuelve mediante el **respaldo de ask** (predeterminado: denegar).

Los clientes nativos de aprobación en chat también pueden exponer affordances específicas del canal en el
mensaje de aprobación pendiente. Por ejemplo, Matrix puede sembrar accesos directos por reacciones en el
prompt de aprobación (`✅` permitir una vez, `❌` denegar y `♾️` permitir siempre cuando esté disponible),
sin dejar de mantener los comandos `/approve ...` en el mensaje como respaldo.

## Dónde se aplica

Las aprobaciones de exec se aplican localmente en el host de ejecución:

- **host del gateway** → proceso `openclaw` en la máquina del gateway
- **host del nodo** → runner del nodo (app complementaria de macOS o host de nodo sin interfaz)

Nota sobre el modelo de confianza:

- Los llamadores autenticados en el gateway son operadores de confianza para ese Gateway.
- Los nodos emparejados extienden esa capacidad de operador de confianza al host del nodo.
- Las aprobaciones de exec reducen el riesgo de ejecución accidental, pero no son un límite de autenticación por usuario.
- Las ejecuciones aprobadas en host de nodo vinculan el contexto canónico de ejecución: cwd canónico, argv exacto, vinculación de env
  cuando está presente y ruta fijada del ejecutable cuando corresponde.
- Para scripts de shell e invocaciones directas de archivos de intérprete/runtime, OpenClaw también intenta vincular
  un operando concreto de archivo local. Si ese archivo vinculado cambia después de la aprobación pero antes de la ejecución,
  la ejecución se deniega en lugar de ejecutar contenido modificado.
- Esta vinculación de archivos es intencionalmente de mejor esfuerzo, no un modelo semántico completo de cada
  ruta de carga de intérprete/runtime. Si el modo de aprobación no puede identificar exactamente un único
  archivo local concreto para vincular, se niega a emitir una ejecución respaldada por aprobación en lugar de fingir cobertura total.

División en macOS:

- El **servicio de host del nodo** reenvía `system.run` a la **app de macOS** mediante IPC local.
- La **app de macOS** aplica aprobaciones + ejecuta el comando en el contexto de la UI.

## Configuración y almacenamiento

Las aprobaciones se almacenan en un archivo JSON local en el host de ejecución:

`~/.openclaw/exec-approvals.json`

Ejemplo de esquema:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## Modo "YOLO" sin aprobaciones

Si quieres que la ejecución en host se realice sin prompts de aprobación, debes abrir **ambas** capas de política:

- política solicitada de exec en la configuración de OpenClaw (`tools.exec.*`)
- política local de aprobaciones del host en `~/.openclaw/exec-approvals.json`

Este es ahora el comportamiento predeterminado del host, salvo que lo restrinjas explícitamente:

- `tools.exec.security`: `full` en `gateway`/`node`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Distinción importante:

- `tools.exec.host=auto` elige dónde se ejecuta exec: en sandbox cuando está disponible; en caso contrario, en gateway.
- YOLO elige cómo se aprueba la ejecución en host: `security=full` más `ask=off`.
- En modo YOLO, OpenClaw no agrega una puerta de aprobación heurística separada por ofuscación de comandos por encima de la política configurada de ejecución en host.
- `auto` no convierte el enrutamiento al gateway en una anulación libre desde una sesión en sandbox. Se permite una solicitud por llamada `host=node` desde `auto`, y `host=gateway` solo se permite desde `auto` cuando no hay un runtime de sandbox activo. Si quieres un valor predeterminado estable distinto de auto, establece `tools.exec.host` o usa `/exec host=...` explícitamente.

Si quieres una configuración más conservadora, vuelve a restringir cualquiera de las dos capas a `allowlist` / `on-miss`
o `deny`.

Configuración persistente de "nunca preguntar" para host del gateway:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Luego haz que el archivo de aprobaciones del host coincida:

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Acceso directo local para la misma política de host del gateway en la máquina actual:

```bash
openclaw exec-policy preset yolo
```

Ese acceso directo local actualiza ambos:

- `tools.exec.host/security/ask` local
- valores predeterminados locales de `~/.openclaw/exec-approvals.json`

Está limitado intencionalmente al ámbito local. Si necesitas cambiar las aprobaciones del host del gateway o del host del nodo
de forma remota, sigue usando `openclaw approvals set --gateway` o
`openclaw approvals set --node <id|name|ip>`.

Para un host del nodo, aplica en su lugar el mismo archivo de aprobaciones en ese nodo:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Limitación importante solo local:

- `openclaw exec-policy` no sincroniza aprobaciones del nodo
- `openclaw exec-policy set --host node` se rechaza
- las aprobaciones de exec del nodo se obtienen del nodo en runtime, por lo que las actualizaciones dirigidas al nodo deben usar `openclaw approvals --node ...`

Acceso directo solo para la sesión:

- `/exec security=full ask=off` cambia solo la sesión actual.
- `/elevated full` es un acceso directo de emergencia que también omite las aprobaciones de exec para esa sesión.

Si el archivo de aprobaciones del host sigue siendo más estricto que la configuración, la política más estricta del host sigue prevaleciendo.

## Controles de política

### Seguridad (`exec.security`)

- **deny**: bloquea todas las solicitudes de ejecución en host.
- **allowlist**: permite solo comandos de la allowlist.
- **full**: permite todo (equivalente a elevated).

### Ask (`exec.ask`)

- **off**: nunca mostrar prompts.
- **on-miss**: mostrar prompt solo cuando la allowlist no coincida.
- **always**: mostrar prompt en cada comando.
- La confianza duradera `allow-always` no suprime los prompts cuando el modo efectivo de ask es `always`

### Respaldo de ask (`askFallback`)

Si se requiere un prompt pero no hay ninguna UI accesible, el respaldo decide:

- **deny**: bloquear.
- **allowlist**: permitir solo si la allowlist coincide.
- **full**: permitir.

### Endurecimiento de eval inline de intérprete (`tools.exec.strictInlineEval`)

Cuando `tools.exec.strictInlineEval=true`, OpenClaw trata las formas de evaluación inline de código como solo-aprobación, incluso si el binario del intérprete en sí está en la allowlist.

Ejemplos:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

Esto es defensa en profundidad para cargadores de intérpretes que no se asignan limpiamente a un único operando de archivo estable. En modo estricto:

- estos comandos siguen necesitando aprobación explícita;
- `allow-always` no conserva automáticamente nuevas entradas de allowlist para ellos.

## Allowlist (por agente)

Las allowlists son **por agente**. Si existen varios agentes, cambia el agente que estás
editando en la app de macOS. Los patrones son **coincidencias glob sin distinción entre mayúsculas y minúsculas**.
Los patrones deben resolverse a **rutas de binarios** (las entradas solo con basename se ignoran).
Las entradas heredadas `agents.default` se migran a `agents.main` al cargarse.
Las cadenas de shell como `echo ok && pwd` siguen necesitando que cada segmento de nivel superior cumpla las reglas de la allowlist.

Ejemplos:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Cada entrada de allowlist rastrea:

- **id** UUID estable usado para la identidad en la UI (opcional)
- **último uso** marca de tiempo
- **último comando usado**
- **última ruta resuelta**

## Autoallow de CLIs de Skills

Cuando **Auto-allow skill CLIs** está habilitado, los ejecutables referenciados por Skills conocidas
se tratan como si estuvieran en la allowlist en nodos (nodo macOS o host de nodo sin interfaz). Esto usa
`skills.bins` sobre el Gateway RPC para obtener la lista de binarios de Skills. Desactívalo si quieres allowlists manuales estrictas.

Notas importantes de confianza:

- Esta es una **allowlist implícita de conveniencia**, separada de las entradas manuales de allowlist por ruta.
- Está pensada para entornos de operador de confianza donde Gateway y nodo están en el mismo límite de confianza.
- Si necesitas confianza explícita estricta, mantén `autoAllowSkills: false` y usa solo entradas manuales de allowlist por ruta.

## Safe bins (solo stdin)

`tools.exec.safeBins` define una lista pequeña de binarios **solo stdin** (por ejemplo `cut`)
que pueden ejecutarse en modo allowlist **sin** entradas explícitas en la allowlist. Los safe bins rechazan
args posicionales de archivo y tokens con forma de ruta, por lo que solo pueden operar sobre el stream entrante.
Trata esto como una vía rápida limitada para filtros de stream, no como una lista de confianza general.
**No** agregues binarios de intérprete o runtime (por ejemplo `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) a `safeBins`.
Si un comando puede evaluar código, ejecutar subcomandos o leer archivos por diseño, prefiere entradas explícitas de allowlist y mantén habilitados los prompts de aprobación.
Los safe bins personalizados deben definir un perfil explícito en `tools.exec.safeBinProfiles.<bin>`.
La validación es determinista solo a partir de la forma de argv (sin comprobaciones de existencia del sistema de archivos del host), lo que
evita el comportamiento de oráculo de existencia de archivos a partir de diferencias entre permitir/denegar.
Las opciones orientadas a archivos se deniegan para los safe bins predeterminados (por ejemplo `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Los safe bins también aplican una política explícita de banderas por binario para opciones que rompen el
comportamiento solo stdin (por ejemplo `sort -o/--output/--compress-program` y las banderas recursivas de grep).
Las opciones largas se validan en modo fail-closed en modo safe-bin: las banderas desconocidas y las abreviaturas ambiguas se rechazan.
Banderas denegadas por perfil de safe-bin:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Los safe bins también obligan a que los tokens de argv se traten como **texto literal** en tiempo de ejecución (sin globbing
ni expansión de `$VARS`) para los segmentos solo stdin, de modo que patrones como `*` o `$HOME/...` no puedan
usarse para introducir lecturas de archivos.
Los safe bins también deben resolverse desde directorios de binarios de confianza (valores predeterminados del sistema más
`tools.exec.safeBinTrustedDirs` opcional). Las entradas de `PATH` nunca se consideran de confianza automáticamente.
Los directorios predeterminados de confianza para safe bins son intencionalmente mínimos: `/bin`, `/usr/bin`.
Si tu ejecutable safe-bin vive en rutas de usuario o de gestores de paquetes (por ejemplo
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), agrégalas explícitamente
a `tools.exec.safeBinTrustedDirs`.
Las cadenas de shell y las redirecciones no se permiten automáticamente en modo allowlist.

Las cadenas de shell (`&&`, `||`, `;`) se permiten cuando cada segmento de nivel superior cumple la allowlist
(incluidos safe bins o autoallow de Skills). Las redirecciones siguen sin ser compatibles en modo allowlist.
La sustitución de comandos (`$()` / backticks) se rechaza durante el análisis de allowlist, incluso dentro de
comillas dobles; usa comillas simples si necesitas texto literal `$()`.
En las aprobaciones de la app complementaria de macOS, el texto raw del shell que contiene sintaxis de control o expansión del shell
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) se trata como fallo de allowlist, salvo que
el propio binario del shell esté en la allowlist.
Para los wrappers de shell (`bash|sh|zsh ... -c/-lc`), las anulaciones de env limitadas a la solicitud se reducen a una
pequeña allowlist explícita (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Para decisiones de allow-always en modo allowlist, los wrappers de despacho conocidos
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) conservan las rutas del ejecutable interno en lugar de las
rutas del wrapper. Los multiplexores de shell (`busybox`, `toybox`) también se desenrollan para los applets de shell (`sh`, `ash`,
etc.), de modo que se conserven los ejecutables internos en lugar de los binarios multiplexores. Si un wrapper o
multiplexor no puede desenrollarse de forma segura, no se conserva automáticamente ninguna entrada de allowlist.
Si pones en la allowlist intérpretes como `python3` o `node`, prefiere `tools.exec.strictInlineEval=true` para que el eval inline siga requiriendo aprobación explícita. En modo estricto, `allow-always` todavía puede conservar invocaciones benignas de intérprete/script, pero los portadores de eval inline no se conservan automáticamente.

Safe bins predeterminados:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` y `sort` no están en la lista predeterminada. Si decides incluirlos, mantén entradas explícitas de allowlist para
sus flujos de trabajo que no sean solo stdin.
Para `grep` en modo safe-bin, proporciona el patrón con `-e`/`--regexp`; la forma de patrón posicional se
rechaza para que los operandos de archivo no puedan introducirse como posicionales ambiguos.

### Safe bins frente a allowlist

| Tema             | `tools.exec.safeBins`                                  | Allowlist (`exec-approvals.json`)                            |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Objetivo         | Permitir automáticamente filtros limitados de stdin    | Confiar explícitamente en ejecutables específicos            |
| Tipo de coincidencia | Nombre del ejecutable + política argv del safe-bin | Patrón glob de la ruta resuelta del ejecutable               |
| Alcance de argumentos | Restringido por el perfil del safe-bin y reglas de tokens literales | Solo coincidencia de ruta; por lo demás, los argumentos son tu responsabilidad |
| Ejemplos típicos | `head`, `tail`, `tr`, `wc`                             | `jq`, `python3`, `node`, `ffmpeg`, CLIs personalizados       |
| Mejor uso        | Transformaciones de texto de bajo riesgo en pipelines  | Cualquier herramienta con comportamiento más amplio o efectos secundarios |

Ubicación de la configuración:

- `safeBins` proviene de la configuración (`tools.exec.safeBins` o por agente `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` proviene de la configuración (`tools.exec.safeBinTrustedDirs` o por agente `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` proviene de la configuración (`tools.exec.safeBinProfiles` o por agente `agents.list[].tools.exec.safeBinProfiles`). Las claves de perfil por agente anulan las claves globales.
- Las entradas de allowlist viven en `~/.openclaw/exec-approvals.json` local del host, en `agents.<id>.allowlist` (o mediante Control UI / `openclaw approvals allowlist ...`).
- `openclaw security audit` advierte con `tools.exec.safe_bins_interpreter_unprofiled` cuando aparecen binarios de intérprete/runtime en `safeBins` sin perfiles explícitos.
- `openclaw doctor --fix` puede generar entradas faltantes de `safeBinProfiles.<bin>` como `{}` (revísalas y ajústalas después). Los binarios de intérprete/runtime no se generan automáticamente.

Ejemplo de perfil personalizado:
__OC_I18N_900005__
Si incluyes explícitamente `jq` en `safeBins`, OpenClaw sigue rechazando el builtin `env` en modo safe-bin
para que `jq -n env` no pueda volcar el entorno del proceso host sin una ruta explícita en la allowlist
o un prompt de aprobación.

## Edición en Control UI

Usa la tarjeta **Control UI → Nodes → Exec approvals** para editar valores predeterminados, anulaciones
por agente y allowlists. Elige un alcance (Predeterminados o un agente), ajusta la política,
agrega/elimina patrones de allowlist y luego haz clic en **Save**. La UI muestra metadata de **último uso**
por patrón para que puedas mantener la lista ordenada.

El selector de destino elige **Gateway** (aprobaciones locales) o un **Node**. Los nodos
deben anunciar `system.execApprovals.get/set` (app de macOS o host de nodo sin interfaz).
Si un nodo todavía no anuncia aprobaciones de exec, edita directamente su archivo local
`~/.openclaw/exec-approvals.json`.

CLI: `openclaw approvals` admite edición de gateway o nodo (consulta [Approvals CLI](/cli/approvals)).

## Flujo de aprobación

Cuando se requiere un prompt, el gateway difunde `exec.approval.requested` a los clientes operadores.
La UI de Control y la app de macOS lo resuelven mediante `exec.approval.resolve`, y luego el gateway reenvía la
solicitud aprobada al host del nodo.

Para `host=node`, las solicitudes de aprobación incluyen una carga útil canónica `systemRunPlan`. El gateway usa
ese plan como el contexto autoritativo de comando/cwd/sesión al reenviar solicitudes `system.run`
aprobadas.

Eso importa para la latencia de aprobación asíncrona:

- la ruta de exec del nodo prepara por adelantado un único plan canónico
- el registro de aprobación almacena ese plan y su metadata de vinculación
- una vez aprobada, la llamada `system.run` final reenviada reutiliza el plan almacenado
  en lugar de confiar en ediciones posteriores del llamador
- si el llamador cambia `command`, `rawCommand`, `cwd`, `agentId` o
  `sessionKey` después de que se haya creado la solicitud de aprobación, el gateway rechaza la
  ejecución reenviada por discrepancia de aprobación

## Comandos de intérprete/runtime

Las ejecuciones de intérprete/runtime respaldadas por aprobación son intencionalmente conservadoras:

- El contexto exacto de argv/cwd/env siempre queda vinculado.
- Las formas directas de script de shell y de archivo de runtime directo se vinculan, en el mejor de los casos, a una única instantánea concreta de archivo local.
- Las formas comunes de wrappers de gestores de paquetes que aun así se resuelven a un único archivo local directo (por ejemplo
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`) se desenrollan antes de la vinculación.
- Si OpenClaw no puede identificar exactamente un único archivo local concreto para un comando de intérprete/runtime
  (por ejemplo scripts de paquetes, formas eval, cadenas de cargadores específicas del runtime o formas
  ambiguas de múltiples archivos), la ejecución respaldada por aprobación se deniega en lugar de afirmar una cobertura semántica que no
  tiene.
- Para esos flujos de trabajo, prefiere sandboxing, un límite de host independiente o un flujo explícito de
  allowlist/full de confianza donde el operador acepte la semántica más amplia del runtime.

Cuando se requieren aprobaciones, la herramienta exec devuelve inmediatamente un id de aprobación. Usa ese id para
correlacionar eventos posteriores del sistema (`Exec finished` / `Exec denied`). Si no llega ninguna decisión antes del
tiempo de espera, la solicitud se trata como tiempo de espera de aprobación y se muestra como motivo de denegación.

### Comportamiento de entrega de seguimiento

Después de que termine una ejecución asíncrona aprobada, OpenClaw envía un turno de `agent` de seguimiento a la misma sesión.

- Si existe un destino de entrega externo válido (canal entregable más destino `to`), la entrega de seguimiento usa ese canal.
- En flujos solo webchat o de sesión interna sin destino externo, la entrega de seguimiento sigue siendo solo de sesión (`deliver: false`).
- Si un llamador solicita explícitamente entrega externa estricta y no hay un canal externo resoluble, la solicitud falla con `INVALID_REQUEST`.
- Si `bestEffortDeliver` está habilitado y no se puede resolver un canal externo, la entrega se degrada a solo sesión en lugar de fallar.

El cuadro de diálogo de confirmación incluye:

- comando + args
- cwd
- id del agente
- ruta resuelta del ejecutable
- host + metadata de política

Acciones:

- **Allow once** → ejecutar ahora
- **Always allow** → agregar a la allowlist + ejecutar
- **Deny** → bloquear

## Reenvío de aprobaciones a canales de chat

Puedes reenviar prompts de aprobación de exec a cualquier canal de chat (incluidos canales de plugins) y aprobarlos
con `/approve`. Esto usa el flujo normal de entrega saliente.

Configuración:
__OC_I18N_900006__
Responder en el chat:
__OC_I18N_900007__
El comando `/approve` maneja tanto aprobaciones de exec como aprobaciones de plugins. Si el ID no coincide con una aprobación de exec pendiente, comprueba automáticamente las aprobaciones de plugins.

### Reenvío de aprobaciones de plugins

El reenvío de aprobaciones de plugins usa el mismo flujo de entrega que las aprobaciones de exec, pero tiene su propia
configuración independiente en `approvals.plugin`. Habilitar o deshabilitar uno no afecta al otro.
__OC_I18N_900008__
La forma de la configuración es idéntica a `approvals.exec`: `enabled`, `mode`, `agentFilter`,
`sessionFilter` y `targets` funcionan igual.

Los canales que admiten respuestas interactivas compartidas muestran los mismos botones de aprobación tanto para exec como para
aprobaciones de plugins. Los canales sin UI interactiva compartida recurren a texto sin formato con instrucciones de `/approve`.

### Aprobaciones en el mismo chat en cualquier canal

Cuando una solicitud de aprobación de exec o de plugin se origina desde una superficie de chat entregable, ese mismo chat
ahora puede aprobarla con `/approve` de forma predeterminada. Esto se aplica a canales como Slack, Matrix y
Microsoft Teams, además de los flujos ya existentes de Web UI y terminal UI.

Esta ruta compartida de comando de texto usa el modelo normal de autenticación del canal para esa conversación. Si el
chat de origen ya puede enviar comandos y recibir respuestas, las solicitudes de aprobación ya no necesitan un
adaptador de entrega nativo independiente solo para permanecer pendientes.

Discord y Telegram también admiten `/approve` en el mismo chat, pero esos canales siguen usando su
lista resuelta de aprobadores para autorización incluso cuando la entrega nativa de aprobaciones está deshabilitada.

Para Telegram y otros clientes nativos de aprobación que llaman directamente al Gateway,
este respaldo está intencionalmente limitado a fallos de tipo "approval not found". Una denegación/error real
de aprobación de exec no reintenta silenciosamente como aprobación de plugin.

### Entrega nativa de aprobaciones

Algunos canales también pueden actuar como clientes nativos de aprobación. Los clientes nativos agregan MD de aprobadores, fanout al chat de origen
y UX interactiva de aprobación específica del canal por encima del flujo compartido de `/approve` en el mismo chat.

Cuando hay tarjetas/botones nativos de aprobación disponibles, esa UI nativa es la ruta principal
de cara al agente. El agente no debe repetir además un comando de chat plano duplicado
`/approve`, salvo que el resultado de la herramienta indique que las aprobaciones por chat no están disponibles o que la
aprobación manual sea la única ruta restante.

Modelo genérico:

- la política de ejecución en host sigue decidiendo si se requiere aprobación de exec
- `approvals.exec` controla el reenvío de prompts de aprobación a otros destinos de chat
- `channels.<channel>.execApprovals` controla si ese canal actúa como cliente nativo de aprobación

Los clientes nativos de aprobación habilitan automáticamente la entrega prioritaria por MD cuando se cumplen todas estas condiciones:

- el canal admite entrega nativa de aprobaciones
- los aprobadores pueden resolverse a partir de `execApprovals.approvers` explícito o de las
  fuentes de respaldo documentadas para ese canal
- `channels.<channel>.execApprovals.enabled` no está establecido o es `"auto"`

Establece `enabled: false` para desactivar explícitamente un cliente nativo de aprobación. Establece `enabled: true` para forzarlo
cuando se resuelvan aprobadores. La entrega pública al chat de origen sigue siendo explícita mediante
`channels.<channel>.execApprovals.target`.

FAQ: [¿Por qué hay dos configuraciones de aprobación de exec para aprobaciones por chat?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Estos clientes nativos de aprobación agregan enrutamiento por MD y fanout opcional al canal por encima del flujo compartido
de `/approve` en el mismo chat y de los botones de aprobación compartidos.

Comportamiento compartido:

- Slack, Matrix, Microsoft Teams y chats entregables similares usan el modelo normal de autenticación del canal
  para `/approve` en el mismo chat
- cuando un cliente nativo de aprobación se habilita automáticamente, el destino nativo predeterminado de entrega son las MD de los aprobadores
- para Discord y Telegram, solo los aprobadores resueltos pueden aprobar o denegar
- los aprobadores de Discord pueden ser explícitos (`execApprovals.approvers`) o inferirse de `commands.ownerAllowFrom`
- los aprobadores de Telegram pueden ser explícitos (`execApprovals.approvers`) o inferirse de la configuración existente de propietario (`allowFrom`, además de `defaultTo` de mensaje directo cuando sea compatible)
- los aprobadores de Slack pueden ser explícitos (`execApprovals.approvers`) o inferirse de `commands.ownerAllowFrom`
- los botones nativos de Slack conservan el tipo de id de aprobación, por lo que los ids `plugin:` pueden resolver aprobaciones de plugins
  sin una segunda capa local de respaldo específica de Slack
- el enrutamiento nativo de MD/canal y los atajos por reacciones de Matrix manejan tanto aprobaciones de exec como de plugins;
  la autorización de plugins sigue viniendo de `channels.matrix.dm.allowFrom`
- el solicitante no necesita ser un aprobador
- el chat de origen puede aprobar directamente con `/approve` cuando ese chat ya admite comandos y respuestas
- los botones nativos de aprobación de Discord enrutan según el tipo de id de aprobación: los ids `plugin:` van
  directamente a aprobaciones de plugins, todo lo demás va a aprobaciones de exec
- los botones nativos de aprobación de Telegram siguen el mismo respaldo acotado de exec a plugin que `/approve`
- cuando `target` nativo habilita la entrega al chat de origen, los prompts de aprobación incluyen el texto del comando
- las aprobaciones de exec pendientes caducan después de 30 minutos de forma predeterminada
- si ninguna UI de operador ni cliente de aprobación configurado puede aceptar la solicitud, el prompt recurre a `askFallback`

Telegram usa de forma predeterminada las MD de los aprobadores (`target: "dm"`). Puedes cambiar a `channel` o `both` cuando
quieras que los prompts de aprobación aparezcan también en el chat/tema de Telegram de origen. Para los
temas de foro de Telegram, OpenClaw conserva el tema para el prompt de aprobación y el seguimiento posterior a la aprobación.

Consulta:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### Flujo de IPC en macOS
__OC_I18N_900009__
Notas de seguridad:

- Modo de socket Unix `0600`, token almacenado en `exec-approvals.json`.
- Comprobación de peer con el mismo UID.
- Desafío/respuesta (nonce + token HMAC + hash de la solicitud) + TTL corto.

## Eventos del sistema

El ciclo de vida de exec se muestra como mensajes del sistema:

- `Exec running` (solo si el comando supera el umbral del aviso de ejecución)
- `Exec finished`
- `Exec denied`

Estos se publican en la sesión del agente después de que el nodo informe el evento.
Las aprobaciones de exec en host del gateway emiten los mismos eventos de ciclo de vida cuando termina el comando (y opcionalmente cuando permanece en ejecución más tiempo que el umbral).
Los exec controlados por aprobación reutilizan el id de aprobación como `runId` en estos mensajes para facilitar la correlación.

## Comportamiento ante aprobación denegada

Cuando se deniega una aprobación de exec asíncrona, OpenClaw evita que el agente reutilice
la salida de cualquier ejecución anterior del mismo comando en la sesión. El motivo de denegación
se transmite con una guía explícita de que no hay salida de comando disponible, lo que impide
que el agente afirme que hay una salida nueva o que repita el comando denegado con
resultados obsoletos de una ejecución anterior exitosa.

## Implicaciones

- **full** es potente; prefiere allowlists cuando sea posible.
- **ask** te mantiene dentro del circuito y sigue permitiendo aprobaciones rápidas.
- Las allowlists por agente evitan que las aprobaciones de un agente se filtren a otros.
- Las aprobaciones solo se aplican a solicitudes de ejecución en host de **remitentes autorizados**. Los remitentes no autorizados no pueden emitir `/exec`.
- `/exec security=full` es una comodidad a nivel de sesión para operadores autorizados y omite aprobaciones por diseño.
  Para bloquear por completo la ejecución en host, establece la seguridad de aprobaciones en `deny` o deniega la herramienta `exec` mediante política de herramientas.

Relacionado:

- [Herramienta Exec](/es/tools/exec)
- [Modo Elevated](/es/tools/elevated)
- [Skills](/es/tools/skills)

## Relacionado

- [Exec](/es/tools/exec) — herramienta de ejecución de comandos de shell
- [Sandboxing](/es/gateway/sandboxing) — modos de sandbox y acceso al workspace
- [Security](/es/gateway/security) — modelo de seguridad y endurecimiento
- [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated) — cuándo usar cada uno
