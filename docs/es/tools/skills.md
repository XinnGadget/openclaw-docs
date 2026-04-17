---
read_when:
    - Agregar o modificar Skills
    - Cambiar las reglas de control o carga de Skills
summary: 'Skills: administradas vs del espacio de trabajo, reglas de control y conexión de config/env'
title: Skills
x-i18n:
    generated_at: "2026-04-11T02:47:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1eaf130966950b6eb24f859d9a77ecbf81c6cb80deaaa6a3a79d2c16d83115d
    source_path: tools/skills.md
    workflow: 15
---

# Skills (OpenClaw)

OpenClaw usa carpetas de Skills **compatibles con [AgentSkills](https://agentskills.io)** para enseñar al agente a usar herramientas. Cada Skill es un directorio que contiene un `SKILL.md` con frontmatter YAML e instrucciones. OpenClaw carga **Skills integradas** más anulaciones locales opcionales, y las filtra en tiempo de carga según el entorno, la configuración y la presencia de binarios.

## Ubicaciones y precedencia

OpenClaw carga Skills desde estas fuentes:

1. **Carpetas de Skills adicionales**: configuradas con `skills.load.extraDirs`
2. **Skills integradas**: incluidas con la instalación (paquete npm o OpenClaw.app)
3. **Skills administradas/locales**: `~/.openclaw/skills`
4. **Skills personales del agente**: `~/.agents/skills`
5. **Skills del agente del proyecto**: `<workspace>/.agents/skills`
6. **Skills del espacio de trabajo**: `<workspace>/skills`

Si hay conflicto de nombre de Skill, la precedencia es:

`<workspace>/skills` (máxima) → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → Skills integradas → `skills.load.extraDirs` (mínima)

## Skills por agente frente a compartidas

En configuraciones de **varios agentes**, cada agente tiene su propio espacio de trabajo. Eso significa:

- Las **Skills por agente** viven en `<workspace>/skills` solo para ese agente.
- Las **Skills del agente del proyecto** viven en `<workspace>/.agents/skills` y se aplican a
  ese espacio de trabajo antes de la carpeta normal `skills/` del espacio de trabajo.
- Las **Skills personales del agente** viven en `~/.agents/skills` y se aplican en todos los
  espacios de trabajo de esa máquina.
- Las **Skills compartidas** viven en `~/.openclaw/skills` (administradas/locales) y son visibles
  para **todos los agentes** de la misma máquina.
- Las **carpetas compartidas** también pueden agregarse mediante `skills.load.extraDirs` (precedencia
  mínima) si quieres un paquete común de Skills usado por varios agentes.

Si el mismo nombre de Skill existe en más de un lugar, se aplica la precedencia
habitual: gana el espacio de trabajo, luego las Skills del agente del proyecto, luego las Skills personales del agente,
después las administradas/locales, luego las integradas y al final los directorios extra.

## Listas de permitidos de Skills por agente

La **ubicación** de la Skill y la **visibilidad** de la Skill son controles separados.

- La ubicación/precedencia decide qué copia gana cuando una Skill tiene el mismo nombre.
- Las listas de permitidos del agente deciden qué Skills visibles puede usar realmente un agente.

Usa `agents.defaults.skills` para una base compartida y luego anula por agente con
`agents.list[].skills`:

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // hereda github, weather
      { id: "docs", skills: ["docs-search"] }, // reemplaza los valores predeterminados
      { id: "locked-down", skills: [] }, // sin Skills
    ],
  },
}
```

Reglas:

- Omite `agents.defaults.skills` para que las Skills no tengan restricciones de forma predeterminada.
- Omite `agents.list[].skills` para heredar `agents.defaults.skills`.
- Establece `agents.list[].skills: []` para no tener Skills.
- Una lista no vacía en `agents.list[].skills` es el conjunto final para ese agente; no
  se combina con los valores predeterminados.

OpenClaw aplica el conjunto efectivo de Skills del agente en la construcción del prompt, el
descubrimiento de comandos slash de Skills, la sincronización de sandbox y las instantáneas de Skills.

## Plugins + Skills

Los plugins pueden incluir sus propias Skills listando directorios `skills` en
`openclaw.plugin.json` (rutas relativas a la raíz del plugin). Las Skills del plugin se cargan
cuando el plugin está habilitado. Hoy esos directorios se fusionan en la misma ruta de baja
precedencia que `skills.load.extraDirs`, por lo que una Skill integrada, administrada,
de agente o de espacio de trabajo con el mismo nombre las anula.
Puedes controlarlas mediante `metadata.openclaw.requires.config` en la entrada de configuración
del plugin. Consulta [Plugins](/es/tools/plugin) para descubrimiento/configuración y [Herramientas](/es/tools) para la
superficie de herramientas que enseñan esas Skills.

## ClawHub (instalación + sincronización)

ClawHub es el registro público de Skills para OpenClaw. Explóralo en
[https://clawhub.ai](https://clawhub.ai). Usa los comandos nativos `openclaw skills`
para descubrir/instalar/actualizar Skills, o la CLI separada `clawhub` cuando
necesites flujos de publicación/sincronización.
Guía completa: [ClawHub](/es/tools/clawhub).

Flujos comunes:

- Instalar una Skill en tu espacio de trabajo:
  - `openclaw skills install <skill-slug>`
- Actualizar todas las Skills instaladas:
  - `openclaw skills update --all`
- Sincronizar (analizar + publicar actualizaciones):
  - `clawhub sync --all`

`openclaw skills install` nativo instala en el directorio `skills/`
del espacio de trabajo activo. La CLI separada `clawhub` también instala en `./skills` bajo tu
directorio de trabajo actual (o recurre al espacio de trabajo de OpenClaw configurado).
OpenClaw lo recogerá como `<workspace>/skills` en la siguiente sesión.

## Notas de seguridad

- Trata las Skills de terceros como **código no confiable**. Léelas antes de habilitarlas.
- Prefiere ejecuciones con sandbox para entradas no confiables y herramientas riesgosas. Consulta [Sandboxing](/es/gateway/sandboxing).
- El descubrimiento de Skills en espacio de trabajo y directorios extra solo acepta raíces de Skills y archivos `SKILL.md` cuyo realpath resuelto permanezca dentro de la raíz configurada.
- Las instalaciones de dependencias de Skills respaldadas por el gateway (`skills.install`, onboarding y la UI de configuración de Skills) ejecutan el escáner integrado de código peligroso antes de ejecutar metadatos de instalación. Los hallazgos `critical` bloquean de forma predeterminada salvo que el llamador establezca explícitamente la anulación de peligro; los hallazgos sospechosos siguen siendo solo advertencias.
- `openclaw skills install <slug>` es diferente: descarga una carpeta de Skill de ClawHub al espacio de trabajo y no usa la ruta de metadatos de instalación anterior.
- `skills.entries.*.env` y `skills.entries.*.apiKey` inyectan secretos en el proceso **host**
  para ese turno del agente (no en el sandbox). Mantén los secretos fuera de los prompts y registros.
- Para un modelo de amenazas más amplio y listas de verificación, consulta [Seguridad](/es/gateway/security).

## Formato (AgentSkills + compatible con Pi)

`SKILL.md` debe incluir al menos:

```markdown
---
name: image-lab
description: Generar o editar imágenes mediante un flujo de trabajo de imágenes respaldado por un proveedor
---
```

Notas:

- Seguimos la especificación AgentSkills para el diseño/la intención.
- El analizador usado por el agente integrado admite claves de frontmatter **de una sola línea** únicamente.
- `metadata` debe ser un **objeto JSON de una sola línea**.
- Usa `{baseDir}` en las instrucciones para hacer referencia a la ruta de la carpeta de la Skill.
- Claves opcionales de frontmatter:
  - `homepage` — URL mostrada como “Website” en la UI de Skills de macOS (también compatible mediante `metadata.openclaw.homepage`).
  - `user-invocable` — `true|false` (predeterminado: `true`). Cuando es `true`, la Skill se expone como un comando slash de usuario.
  - `disable-model-invocation` — `true|false` (predeterminado: `false`). Cuando es `true`, la Skill se excluye del prompt del modelo (sigue disponible mediante invocación del usuario).
  - `command-dispatch` — `tool` (opcional). Cuando se establece en `tool`, el comando slash omite el modelo y se envía directamente a una herramienta.
  - `command-tool` — nombre de la herramienta que se debe invocar cuando `command-dispatch: tool` está establecido.
  - `command-arg-mode` — `raw` (predeterminado). Para el envío a herramientas, reenvía la cadena de argumentos sin procesar a la herramienta (sin análisis del núcleo).

    La herramienta se invoca con parámetros:
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`.

## Control de acceso (filtros en tiempo de carga)

OpenClaw **filtra Skills en tiempo de carga** usando `metadata` (JSON de una sola línea):

```markdown
---
name: image-lab
description: Generar o editar imágenes mediante un flujo de trabajo de imágenes respaldado por un proveedor
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

Campos bajo `metadata.openclaw`:

- `always: true` — siempre incluye la Skill (omite los demás controles).
- `emoji` — emoji opcional usado por la UI de Skills de macOS.
- `homepage` — URL opcional mostrada como “Website” en la UI de Skills de macOS.
- `os` — lista opcional de plataformas (`darwin`, `linux`, `win32`). Si se establece, la Skill solo es apta en esos sistemas operativos.
- `requires.bins` — lista; cada uno debe existir en `PATH`.
- `requires.anyBins` — lista; al menos uno debe existir en `PATH`.
- `requires.env` — lista; la variable de entorno debe existir **o** proporcionarse en la configuración.
- `requires.config` — lista de rutas de `openclaw.json` que deben ser verdaderas.
- `primaryEnv` — nombre de la variable de entorno asociada con `skills.entries.<name>.apiKey`.
- `install` — arreglo opcional de especificaciones de instalador usado por la UI de Skills de macOS (brew/node/go/uv/download).

Nota sobre sandboxing:

- `requires.bins` se comprueba en el **host** en tiempo de carga de la Skill.
- Si un agente usa sandbox, el binario también debe existir **dentro del contenedor**.
  Instálalo mediante `agents.defaults.sandbox.docker.setupCommand` (o una imagen personalizada).
  `setupCommand` se ejecuta una vez después de crear el contenedor.
  Las instalaciones de paquetes también requieren salida de red, un sistema de archivos raíz escribible y un usuario root en el sandbox.
  Ejemplo: la Skill `summarize` (`skills/summarize/SKILL.md`) necesita la CLI `summarize`
  en el contenedor sandbox para ejecutarse allí.

Ejemplo de instalador:

```markdown
---
name: gemini
description: Usar Gemini CLI para ayuda con programación y búsquedas en Google.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Instalar Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

Notas:

- Si se listan varios instaladores, el gateway elige una **única** opción preferida (brew cuando está disponible; en caso contrario, node).
- Si todos los instaladores son `download`, OpenClaw lista cada entrada para que puedas ver los artefactos disponibles.
- Las especificaciones de instalador pueden incluir `os: ["darwin"|"linux"|"win32"]` para filtrar opciones por plataforma.
- Las instalaciones con Node respetan `skills.install.nodeManager` en `openclaw.json` (predeterminado: npm; opciones: npm/pnpm/yarn/bun).
  Esto solo afecta a las **instalaciones de Skills**; el entorno de ejecución del Gateway debe seguir siendo Node
  (Bun no se recomienda para WhatsApp/Telegram).
- La selección de instaladores respaldada por el gateway está guiada por preferencias, no solo por node:
  cuando las especificaciones de instalación mezclan tipos, OpenClaw prefiere Homebrew cuando
  `skills.install.preferBrew` está habilitado y `brew` existe, luego `uv`, luego el
  gestor de node configurado y después otros respaldos como `go` o `download`.
- Si todas las especificaciones de instalación son `download`, OpenClaw muestra todas las opciones de descarga
  en lugar de reducirlas a un único instalador preferido.
- Instalaciones con Go: si falta `go` y `brew` está disponible, el gateway instala primero Go mediante Homebrew y establece `GOBIN` en `bin` de Homebrew cuando es posible.
- Instalaciones por descarga: `url` (obligatorio), `archive` (`tar.gz` | `tar.bz2` | `zip`), `extract` (predeterminado: automático cuando se detecta archivo), `stripComponents`, `targetDir` (predeterminado: `~/.openclaw/tools/<skillKey>`).

Si no hay `metadata.openclaw`, la Skill siempre es apta (salvo que
esté deshabilitada en la configuración o bloqueada por `skills.allowBundled` en el caso de Skills integradas).

## Anulaciones de configuración (`~/.openclaw/openclaw.json`)

Las Skills integradas/administradas pueden activarse o desactivarse y recibir valores de entorno:

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // o cadena de texto sin formato
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

Nota: si el nombre de la Skill contiene guiones, pon la clave entre comillas (JSON5 permite claves entrecomilladas).

Si quieres generación/edición de imágenes estándar dentro del propio OpenClaw, usa la
herramienta central `image_generate` con `agents.defaults.imageGenerationModel` en lugar de una
Skill integrada. Los ejemplos de Skills aquí son para flujos personalizados o de terceros.

Para análisis nativo de imágenes, usa la herramienta `image` con `agents.defaults.imageModel`.
Para generación/edición nativa de imágenes, usa `image_generate` con
`agents.defaults.imageGenerationModel`. Si eliges `openai/*`, `google/*`,
`fal/*` u otro modelo de imagen específico de proveedor, añade también la autenticación/clave de API
de ese proveedor.

Las claves de configuración coinciden con el **nombre de la Skill** de forma predeterminada. Si una Skill define
`metadata.openclaw.skillKey`, usa esa clave bajo `skills.entries`.

Reglas:

- `enabled: false` deshabilita la Skill incluso si está integrada/instalada.
- `env`: se inyecta **solo si** la variable aún no está establecida en el proceso.
- `apiKey`: comodidad para Skills que declaran `metadata.openclaw.primaryEnv`.
  Admite cadena de texto sin formato u objeto SecretRef (`{ source, provider, id }`).
- `config`: contenedor opcional para campos personalizados por Skill; las claves personalizadas deben vivir aquí.
- `allowBundled`: lista de permitidos opcional solo para Skills **integradas**. Si se establece, solo
  las Skills integradas de la lista serán aptas (las Skills administradas/del espacio de trabajo no se ven afectadas).

## Inyección de entorno (por ejecución de agente)

Cuando comienza una ejecución de agente, OpenClaw:

1. Lee los metadatos de la Skill.
2. Aplica cualquier `skills.entries.<key>.env` o `skills.entries.<key>.apiKey` a
   `process.env`.
3. Construye el prompt del sistema con las Skills **aptas**.
4. Restaura el entorno original cuando termina la ejecución.

Esto está **delimitado a la ejecución del agente**, no a un entorno global del shell.

Para el backend integrado `claude-cli`, OpenClaw también materializa la misma
instantánea apta como un plugin temporal de Claude Code y la pasa con
`--plugin-dir`. Claude Code puede entonces usar su resolvedor nativo de skills mientras
OpenClaw sigue siendo propietario de la precedencia, las listas de permitidos por agente, el control de acceso y la
inyección de env/claves de API de `skills.entries.*`. Los demás backends de CLI usan solo el catálogo del prompt.

## Instantánea de sesión (rendimiento)

OpenClaw toma una instantánea de las Skills aptas **cuando se inicia una sesión** y reutiliza esa lista para los turnos posteriores de la misma sesión. Los cambios en Skills o configuración surten efecto en la siguiente sesión nueva.

Las Skills también pueden actualizarse a mitad de sesión cuando el observador de Skills está habilitado o cuando aparece un nuevo nodo remoto apto (ver abajo). Piensa en esto como una **recarga en caliente**: la lista actualizada se recoge en el siguiente turno del agente.

Si cambia la lista efectiva de Skills permitidas del agente para esa sesión, OpenClaw
actualiza la instantánea para que las Skills visibles sigan alineadas con el
agente actual.

## Nodos macOS remotos (gateway Linux)

Si el Gateway se ejecuta en Linux pero hay un **nodo macOS** conectado **con `system.run` permitido** (la seguridad de aprobaciones de Exec no está establecida en `deny`), OpenClaw puede tratar las Skills exclusivas de macOS como aptas cuando los binarios requeridos están presentes en ese nodo. El agente debe ejecutar esas Skills mediante la herramienta `exec` con `host=node`.

Esto depende de que el nodo informe su compatibilidad de comandos y de una sonda de binarios mediante `system.run`. Si el nodo macOS se desconecta más tarde, las Skills siguen siendo visibles; las invocaciones pueden fallar hasta que el nodo vuelva a conectarse.

## Observador de Skills (actualización automática)

De forma predeterminada, OpenClaw observa las carpetas de Skills y actualiza la instantánea de Skills cuando cambian los archivos `SKILL.md`. Configúralo en `skills.load`:

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## Impacto en tokens (lista de Skills)

Cuando las Skills son aptas, OpenClaw inyecta una lista XML compacta de las Skills disponibles en el prompt del sistema (mediante `formatSkillsForPrompt` en `pi-coding-agent`). El costo es determinista:

- **Sobrecarga base (solo cuando hay ≥1 Skill):** 195 caracteres.
- **Por Skill:** 97 caracteres + la longitud de los valores escapados en XML de `<name>`, `<description>` y `<location>`.

Fórmula (caracteres):

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

Notas:

- El escape XML expande `& < > " '` a entidades (`&amp;`, `&lt;`, etc.), aumentando la longitud.
- El recuento de tokens varía según el tokenizador del modelo. Una estimación aproximada estilo OpenAI es ~4 caracteres/token, por lo que **97 caracteres ≈ 24 tokens** por Skill más las longitudes reales de tus campos.

## Ciclo de vida de Skills administradas

OpenClaw incluye un conjunto base de Skills como **Skills integradas** como parte de la
instalación (paquete npm o OpenClaw.app). `~/.openclaw/skills` existe para
anulaciones locales (por ejemplo, fijar/parchear una Skill sin cambiar la copia
integrada). Las Skills del espacio de trabajo son propiedad del usuario y anulan a ambas cuando hay conflictos de nombre.

## Referencia de configuración

Consulta [Configuración de Skills](/es/tools/skills-config) para ver el esquema completo de configuración.

## ¿Buscas más Skills?

Explora [https://clawhub.ai](https://clawhub.ai).

---

## Relacionado

- [Creación de Skills](/es/tools/creating-skills) — crear Skills personalizadas
- [Configuración de Skills](/es/tools/skills-config) — referencia de configuración de Skills
- [Comandos slash](/es/tools/slash-commands) — todos los comandos slash disponibles
- [Plugins](/es/tools/plugin) — resumen del sistema de plugins
