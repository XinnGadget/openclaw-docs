---
read_when: You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox.
status: active
summary: 'Cómo funciona el sandboxing de OpenClaw: modos, alcances, acceso al espacio de trabajo e imágenes'
title: Sandboxing
x-i18n:
    generated_at: "2026-04-14T02:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2573d0d7462f63a68eb1750e5432211522ff5b42989a17379d3e188468bbce52
    source_path: gateway/sandboxing.md
    workflow: 15
---

# Sandboxing

OpenClaw puede ejecutar **herramientas dentro de backends de sandbox** para reducir el radio de impacto.
Esto es **opcional** y se controla mediante la configuración (`agents.defaults.sandbox` o
`agents.list[].sandbox`). Si el sandboxing está desactivado, las herramientas se ejecutan en el host.
El Gateway permanece en el host; la ejecución de herramientas se realiza en un sandbox aislado
cuando está habilitado.

Esto no es un límite de seguridad perfecto, pero limita de forma significativa el acceso
al sistema de archivos y a los procesos cuando el modelo hace algo torpe.

## Qué se sandboxea

- Ejecución de herramientas (`exec`, `read`, `write`, `edit`, `apply_patch`, `process`, etc.).
- Navegador sandbox opcional (`agents.defaults.sandbox.browser`).
  - De forma predeterminada, el navegador del sandbox se inicia automáticamente (asegura que CDP sea accesible) cuando la herramienta del navegador lo necesita.
    Configúralo mediante `agents.defaults.sandbox.browser.autoStart` y `agents.defaults.sandbox.browser.autoStartTimeoutMs`.
  - De forma predeterminada, los contenedores del navegador del sandbox usan una red de Docker dedicada (`openclaw-sandbox-browser`) en lugar de la red global `bridge`.
    Configúralo con `agents.defaults.sandbox.browser.network`.
  - El valor opcional `agents.defaults.sandbox.browser.cdpSourceRange` restringe el ingreso de CDP en el borde del contenedor con una lista de permitidos CIDR (por ejemplo, `172.21.0.1/32`).
  - El acceso de observador de noVNC está protegido con contraseña de forma predeterminada; OpenClaw emite una URL con token de corta duración que sirve una página bootstrap local y abre noVNC con la contraseña en el fragmento de la URL (no en registros de query/header).
  - `agents.defaults.sandbox.browser.allowHostControl` permite que las sesiones sandboxeadas apunten explícitamente al navegador del host.
  - Listas de permitidos opcionales controlan `target: "custom"`: `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`.

No se sandboxea:

- El propio proceso Gateway.
- Cualquier herramienta a la que se le permita explícitamente ejecutarse fuera del sandbox (por ejemplo, `tools.elevated`).
  - **Elevated exec omite el sandboxing y usa la ruta de escape configurada (`gateway` de forma predeterminada, o `node` cuando el destino de exec es `node`).**
  - Si el sandboxing está desactivado, `tools.elevated` no cambia la ejecución (ya está en el host). Consulta [Elevated Mode](/es/tools/elevated).

## Modos

`agents.defaults.sandbox.mode` controla **cuándo** se usa el sandboxing:

- `"off"`: sin sandboxing.
- `"non-main"`: sandboxea solo las sesiones **no principales** (valor predeterminado si quieres chats normales en el host).
- `"all"`: cada sesión se ejecuta en un sandbox.
  Nota: `"non-main"` se basa en `session.mainKey` (valor predeterminado `"main"`), no en el id del agente.
  Las sesiones de grupo/canal usan sus propias claves, por lo que cuentan como no principales y serán sandboxeadas.

## Alcance

`agents.defaults.sandbox.scope` controla **cuántos contenedores** se crean:

- `"agent"` (predeterminado): un contenedor por agente.
- `"session"`: un contenedor por sesión.
- `"shared"`: un contenedor compartido por todas las sesiones sandboxeadas.

## Backend

`agents.defaults.sandbox.backend` controla **qué runtime** proporciona el sandbox:

- `"docker"` (predeterminado): runtime de sandbox local respaldado por Docker.
- `"ssh"`: runtime de sandbox remoto genérico respaldado por SSH.
- `"openshell"`: runtime de sandbox respaldado por OpenShell.

La configuración específica de SSH está en `agents.defaults.sandbox.ssh`.
La configuración específica de OpenShell está en `plugins.entries.openshell.config`.

### Elegir un backend

|                     | Docker                           | SSH                            | OpenShell                                                  |
| ------------------- | -------------------------------- | ------------------------------ | ---------------------------------------------------------- |
| **Dónde se ejecuta** | Contenedor local                 | Cualquier host accesible por SSH | Sandbox administrado por OpenShell                         |
| **Configuración**   | `scripts/sandbox-setup.sh`       | Clave SSH + host de destino    | Plugin de OpenShell habilitado                             |
| **Modelo de espacio de trabajo** | Montaje bind o copia            | Remoto canónico (siembra una vez) | `mirror` o `remote`                                        |
| **Control de red**  | `docker.network` (predeterminado: ninguno) | Depende del host remoto        | Depende de OpenShell                                       |
| **Sandbox del navegador** | Compatible                        | No compatible                  | Aún no compatible                                          |
| **Montajes bind**   | `docker.binds`                   | N/A                            | N/A                                                        |
| **Ideal para**      | Desarrollo local, aislamiento completo | Descargar trabajo a una máquina remota | Sandboxes remotos administrados con sincronización bidireccional opcional |

### Backend de Docker

El backend de Docker es el runtime predeterminado y ejecuta herramientas y navegadores sandbox localmente a través del socket del daemon de Docker (`/var/run/docker.sock`). El aislamiento del contenedor sandbox está determinado por los namespaces de Docker.

**Restricciones de Docker-out-of-Docker (DooD)**:
Si implementas el propio Gateway de OpenClaw como un contenedor Docker, este orquesta contenedores sandbox hermanos usando el socket Docker del host (DooD). Esto introduce una restricción específica de mapeo de rutas:

- **La configuración requiere rutas del host**: la configuración `workspace` de `openclaw.json` DEBE contener la **ruta absoluta del host** (por ejemplo, `/home/user/.openclaw/workspaces`), no la ruta interna del contenedor Gateway. Cuando OpenClaw pide al daemon de Docker que cree un sandbox, el daemon evalúa las rutas con respecto al espacio de nombres del SO host, no al espacio de nombres del Gateway.
- **Paridad del puente de FS (mismo mapa de volúmenes)**: el proceso nativo del Gateway de OpenClaw también escribe archivos de heartbeat y puente en el directorio `workspace`. Como el Gateway evalúa la misma cadena exacta (la ruta del host) desde dentro de su propio entorno en contenedor, la implementación del Gateway DEBE incluir un mapa de volúmenes idéntico que vincule el espacio de nombres del host de forma nativa (`-v /home/user/.openclaw:/home/user/.openclaw`).

Si mapeas rutas internamente sin paridad absoluta con el host, OpenClaw lanza de forma nativa un error de permisos `EACCES` al intentar escribir su heartbeat dentro del entorno del contenedor porque la cadena de ruta completamente calificada no existe de forma nativa.

### Backend de SSH

Usa `backend: "ssh"` cuando quieras que OpenClaw sandboxee `exec`, las herramientas de archivos y las lecturas de medios en
una máquina arbitraria accesible por SSH.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // O usa SecretRefs / contenido en línea en lugar de archivos locales:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

Cómo funciona:

- OpenClaw crea una raíz remota por alcance en `sandbox.ssh.workspaceRoot`.
- En el primer uso después de crear o recrear, OpenClaw siembra ese espacio de trabajo remoto desde el espacio de trabajo local una sola vez.
- Después de eso, `exec`, `read`, `write`, `edit`, `apply_patch`, las lecturas de medios del prompt y la preparación de medios entrantes se ejecutan directamente sobre el espacio de trabajo remoto mediante SSH.
- OpenClaw no sincroniza automáticamente los cambios remotos de vuelta al espacio de trabajo local.

Material de autenticación:

- `identityFile`, `certificateFile`, `knownHostsFile`: usan archivos locales existentes y los pasan mediante la configuración de OpenSSH.
- `identityData`, `certificateData`, `knownHostsData`: usan cadenas en línea o SecretRefs. OpenClaw las resuelve mediante el snapshot normal del runtime de secretos, las escribe en archivos temporales con `0600` y las elimina cuando termina la sesión SSH.
- Si `*File` y `*Data` están configurados para el mismo elemento, `*Data` tiene prioridad para esa sesión SSH.

Este es un modelo **remoto canónico**. El espacio de trabajo SSH remoto se convierte en el estado real del sandbox después de la siembra inicial.

Consecuencias importantes:

- Las ediciones locales en el host hechas fuera de OpenClaw después del paso de siembra no son visibles de forma remota hasta que recrees el sandbox.
- `openclaw sandbox recreate` elimina la raíz remota por alcance y vuelve a sembrar desde local en el siguiente uso.
- El sandboxing del navegador no es compatible con el backend de SSH.
- La configuración `sandbox.docker.*` no se aplica al backend de SSH.

### Backend de OpenShell

Usa `backend: "openshell"` cuando quieras que OpenClaw sandboxee herramientas en un
entorno remoto administrado por OpenShell. Para la guía completa de configuración,
la referencia de configuración y la comparación de modos de espacio de trabajo, consulta la
[página de OpenShell](/es/gateway/openshell).

OpenShell reutiliza el mismo transporte SSH central y el mismo puente de sistema de archivos remoto que el
backend genérico de SSH, y agrega el ciclo de vida específico de OpenShell
(`sandbox create/get/delete`, `sandbox ssh-config`) además del modo de espacio de trabajo opcional `mirror`.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote", // mirror | remote
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
        },
      },
    },
  },
}
```

Modos de OpenShell:

- `mirror` (predeterminado): el espacio de trabajo local sigue siendo el canónico. OpenClaw sincroniza los archivos locales hacia OpenShell antes de `exec` y sincroniza el espacio de trabajo remoto de vuelta después de `exec`.
- `remote`: el espacio de trabajo de OpenShell es canónico después de crear el sandbox. OpenClaw siembra el espacio de trabajo remoto una vez desde el espacio de trabajo local, y luego las herramientas de archivos y `exec` se ejecutan directamente contra el sandbox remoto sin sincronizar los cambios de vuelta.

Detalles del transporte remoto:

- OpenClaw pide a OpenShell la configuración SSH específica del sandbox mediante `openshell sandbox ssh-config <name>`.
- El núcleo escribe esa configuración SSH en un archivo temporal, abre la sesión SSH y reutiliza el mismo puente de sistema de archivos remoto usado por `backend: "ssh"`.
- En el modo `mirror`, solo difiere el ciclo de vida: sincroniza de local a remoto antes de `exec`, y luego sincroniza de vuelta después de `exec`.

Limitaciones actuales de OpenShell:

- el navegador sandbox aún no es compatible
- `sandbox.docker.binds` no es compatible con el backend de OpenShell
- los controles de runtime específicos de Docker en `sandbox.docker.*` siguen aplicándose solo al backend de Docker

#### Modos de espacio de trabajo

OpenShell tiene dos modelos de espacio de trabajo. Esta es la parte que más importa en la práctica.

##### `mirror`

Usa `plugins.entries.openshell.config.mode: "mirror"` cuando quieras que el **espacio de trabajo local siga siendo canónico**.

Comportamiento:

- Antes de `exec`, OpenClaw sincroniza el espacio de trabajo local hacia el sandbox de OpenShell.
- Después de `exec`, OpenClaw sincroniza el espacio de trabajo remoto de vuelta al espacio de trabajo local.
- Las herramientas de archivos siguen operando a través del puente del sandbox, pero el espacio de trabajo local sigue siendo la fuente de verdad entre turnos.

Usa esto cuando:

- editas archivos localmente fuera de OpenClaw y quieres que esos cambios aparezcan automáticamente en el sandbox
- quieres que el sandbox de OpenShell se comporte lo más parecido posible al backend de Docker
- quieres que el espacio de trabajo del host refleje las escrituras del sandbox después de cada turno de exec

Compensación:

- costo adicional de sincronización antes y después de exec

##### `remote`

Usa `plugins.entries.openshell.config.mode: "remote"` cuando quieras que el **espacio de trabajo de OpenShell se vuelva canónico**.

Comportamiento:

- Cuando el sandbox se crea por primera vez, OpenClaw siembra el espacio de trabajo remoto desde el espacio de trabajo local una sola vez.
- Después de eso, `exec`, `read`, `write`, `edit` y `apply_patch` operan directamente contra el espacio de trabajo remoto de OpenShell.
- OpenClaw **no** sincroniza los cambios remotos de vuelta al espacio de trabajo local después de `exec`.
- Las lecturas de medios en tiempo de prompt siguen funcionando porque las herramientas de archivos y medios leen a través del puente del sandbox en lugar de asumir una ruta local del host.
- El transporte es SSH al sandbox de OpenShell devuelto por `openshell sandbox ssh-config`.

Consecuencias importantes:

- Si editas archivos en el host fuera de OpenClaw después del paso de siembra, el sandbox remoto **no** verá esos cambios automáticamente.
- Si el sandbox se recrea, el espacio de trabajo remoto se vuelve a sembrar desde el espacio de trabajo local.
- Con `scope: "agent"` o `scope: "shared"`, ese espacio de trabajo remoto se comparte en ese mismo alcance.

Usa esto cuando:

- el sandbox deba vivir principalmente en el lado remoto de OpenShell
- quieras una menor sobrecarga de sincronización por turno
- no quieras que las ediciones locales en el host sobrescriban silenciosamente el estado remoto del sandbox

Elige `mirror` si piensas en el sandbox como un entorno de ejecución temporal.
Elige `remote` si piensas en el sandbox como el espacio de trabajo real.

#### Ciclo de vida de OpenShell

Los sandboxes de OpenShell siguen administrándose mediante el ciclo de vida normal del sandbox:

- `openclaw sandbox list` muestra runtimes de OpenShell además de runtimes de Docker
- `openclaw sandbox recreate` elimina el runtime actual y permite que OpenClaw lo recree en el siguiente uso
- la lógica de limpieza (`prune`) también conoce el backend

Para el modo `remote`, recreate es especialmente importante:

- recreate elimina el espacio de trabajo remoto canónico para ese alcance
- el siguiente uso siembra un espacio de trabajo remoto nuevo desde el espacio de trabajo local

Para el modo `mirror`, recreate principalmente restablece el entorno de ejecución remoto
porque el espacio de trabajo local sigue siendo canónico de todos modos.

## Acceso al espacio de trabajo

`agents.defaults.sandbox.workspaceAccess` controla **qué puede ver** el sandbox:

- `"none"` (predeterminado): las herramientas ven un espacio de trabajo de sandbox en `~/.openclaw/sandboxes`.
- `"ro"`: monta el espacio de trabajo del agente como solo lectura en `/agent` (desactiva `write`/`edit`/`apply_patch`).
- `"rw"`: monta el espacio de trabajo del agente con lectura/escritura en `/workspace`.

Con el backend de OpenShell:

- el modo `mirror` sigue usando el espacio de trabajo local como fuente canónica entre turnos de exec
- el modo `remote` usa el espacio de trabajo remoto de OpenShell como fuente canónica después de la siembra inicial
- `workspaceAccess: "ro"` y `"none"` siguen restringiendo el comportamiento de escritura de la misma manera

Los medios entrantes se copian al espacio de trabajo activo del sandbox (`media/inbound/*`).
Nota sobre Skills: la herramienta `read` está enraizada en el sandbox. Con `workspaceAccess: "none"`,
OpenClaw refleja los Skills aptos en el espacio de trabajo del sandbox (`.../skills`) para
que se puedan leer. Con `"rw"`, los Skills del espacio de trabajo se pueden leer desde
`/workspace/skills`.

## Montajes bind personalizados

`agents.defaults.sandbox.docker.binds` monta directorios adicionales del host dentro del contenedor.
Formato: `host:container:mode` (por ejemplo, `"/home/user/source:/source:rw"`).

Los montajes globales y por agente se **fusionan** (no se reemplazan). En `scope: "shared"`, los montajes por agente se ignoran.

`agents.defaults.sandbox.browser.binds` monta directorios adicionales del host solo en el contenedor del **navegador sandbox**.

- Cuando está configurado (incluido `[]`), reemplaza `agents.defaults.sandbox.docker.binds` para el contenedor del navegador.
- Cuando se omite, el contenedor del navegador recurre a `agents.defaults.sandbox.docker.binds` (compatible con versiones anteriores).

Ejemplo (fuente de solo lectura + un directorio de datos adicional):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

Notas de seguridad:

- Los montajes bind omiten el sistema de archivos del sandbox: exponen rutas del host con el modo que configures (`:ro` o `:rw`).
- OpenClaw bloquea orígenes de montaje bind peligrosos (por ejemplo: `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev` y montajes padre que los expondrían).
- OpenClaw también bloquea raíces comunes de credenciales en el directorio home como `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm` y `~/.ssh`.
- La validación de montajes bind no es solo comparación de cadenas. OpenClaw normaliza la ruta de origen y luego la resuelve de nuevo a través del ancestro existente más profundo antes de volver a verificar rutas bloqueadas y raíces permitidas.
- Eso significa que los escapes mediante padres con symlink siguen fallando de forma segura incluso cuando la hoja final aún no existe. Ejemplo: `/workspace/run-link/new-file` seguirá resolviéndose como `/var/run/...` si `run-link` apunta allí.
- Las raíces de origen permitidas se canonizan de la misma manera, por lo que una ruta que solo parece estar dentro de la lista permitida antes de la resolución de symlink igualmente se rechaza como `outside allowed roots`.
- Los montajes sensibles (secretos, claves SSH, credenciales de servicio) deberían ser `:ro` salvo que sea absolutamente necesario.
- Combínalo con `workspaceAccess: "ro"` si solo necesitas acceso de lectura al espacio de trabajo; los modos de montaje bind siguen siendo independientes.
- Consulta [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated) para ver cómo interactúan los montajes bind con la política de herramientas y elevated exec.

## Imágenes + configuración

Imagen predeterminada de Docker: `openclaw-sandbox:bookworm-slim`

Compílala una vez:

```bash
scripts/sandbox-setup.sh
```

Nota: la imagen predeterminada **no** incluye Node. Si un Skill necesita Node (u
otros runtimes), crea una imagen personalizada o instala mediante
`sandbox.docker.setupCommand` (requiere salida de red + raíz escribible +
usuario root).

Si quieres una imagen de sandbox más funcional con herramientas comunes (por ejemplo,
`curl`, `jq`, `nodejs`, `python3`, `git`), compila:

```bash
scripts/sandbox-common-setup.sh
```

Luego configura `agents.defaults.sandbox.docker.image` como
`openclaw-sandbox-common:bookworm-slim`.

Imagen del navegador sandbox:

```bash
scripts/sandbox-browser-setup.sh
```

De forma predeterminada, los contenedores Docker del sandbox se ejecutan **sin red**.
Anúlalo con `agents.defaults.sandbox.docker.network`.

La imagen incluida del navegador sandbox también aplica valores predeterminados conservadores de inicio de Chromium
para cargas de trabajo en contenedores. Los valores predeterminados actuales del contenedor incluyen:

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` y `--disable-setuid-sandbox` cuando `noSandbox` está habilitado.
- Las tres flags de endurecimiento gráfico (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) son opcionales y son útiles
  cuando los contenedores no tienen soporte GPU. Configura `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`
  si tu carga de trabajo requiere WebGL u otras funciones 3D/del navegador.
- `--disable-extensions` está habilitado de forma predeterminada y puede deshabilitarse con
  `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` para flujos que dependan de extensiones.
- `--renderer-process-limit=2` se controla con
  `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`, donde `0` mantiene el valor predeterminado de Chromium.

Si necesitas un perfil de runtime diferente, usa una imagen de navegador personalizada y proporciona
tu propio entrypoint. Para perfiles locales de Chromium (sin contenedor), usa
`browser.extraArgs` para agregar flags de inicio adicionales.

Valores predeterminados de seguridad:

- `network: "host"` está bloqueado.
- `network: "container:<id>"` está bloqueado de forma predeterminada (riesgo de omitir el aislamiento al unirse al namespace).
- Anulación de emergencia: `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`.

Las instalaciones de Docker y el gateway en contenedor se documentan aquí:
[Docker](/es/install/docker)

Para implementaciones del gateway con Docker, `scripts/docker/setup.sh` puede inicializar la configuración del sandbox.
Configura `OPENCLAW_SANDBOX=1` (o `true`/`yes`/`on`) para habilitar esa ruta. Puedes
anular la ubicación del socket con `OPENCLAW_DOCKER_SOCKET`. Referencia completa de
configuración y variables de entorno: [Docker](/es/install/docker#agent-sandbox).

## setupCommand (configuración única del contenedor)

`setupCommand` se ejecuta **una vez** después de que se crea el contenedor sandbox (no en cada ejecución).
Se ejecuta dentro del contenedor mediante `sh -lc`.

Rutas:

- Global: `agents.defaults.sandbox.docker.setupCommand`
- Por agente: `agents.list[].sandbox.docker.setupCommand`

Problemas comunes:

- El valor predeterminado de `docker.network` es `"none"` (sin salida de red), por lo que las instalaciones de paquetes fallarán.
- `docker.network: "container:<id>"` requiere `dangerouslyAllowContainerNamespaceJoin: true` y es solo para casos de emergencia.
- `readOnlyRoot: true` impide escrituras; configura `readOnlyRoot: false` o crea una imagen personalizada.
- `user` debe ser root para instalaciones de paquetes (omite `user` o configura `user: "0:0"`).
- El exec del sandbox **no** hereda `process.env` del host. Usa
  `agents.defaults.sandbox.docker.env` (o una imagen personalizada) para las claves API de Skills.

## Política de herramientas + vías de escape

Las políticas de permitir/denegar herramientas siguen aplicándose antes de las reglas del sandbox. Si una herramienta está denegada
globalmente o por agente, el sandboxing no la recupera.

`tools.elevated` es una vía de escape explícita que ejecuta `exec` fuera del sandbox (`gateway` de forma predeterminada, o `node` cuando el destino de exec es `node`).
Las directivas `/exec` solo se aplican a remitentes autorizados y persisten por sesión; para deshabilitar por completo
`exec`, usa una denegación en la política de herramientas (consulta [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated)).

Depuración:

- Usa `openclaw sandbox explain` para inspeccionar el modo efectivo del sandbox, la política de herramientas y las claves de configuración para corregirlo.
- Consulta [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated) para el modelo mental de “¿por qué está bloqueado?”.
  Mantenlo restringido.

## Sobrescrituras multiagente

Cada agente puede sobrescribir sandbox + herramientas:
`agents.list[].sandbox` y `agents.list[].tools` (además de `agents.list[].tools.sandbox.tools` para la política de herramientas del sandbox).
Consulta [Multi-Agent Sandbox & Tools](/es/tools/multi-agent-sandbox-tools) para la precedencia.

## Ejemplo mínimo de habilitación

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Documentación relacionada

- [OpenShell](/es/gateway/openshell) -- configuración del backend de sandbox administrado, modos de espacio de trabajo y referencia de configuración
- [Sandbox Configuration](/es/gateway/configuration-reference#agentsdefaultssandbox)
- [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated) -- depuración de “¿por qué está bloqueado?”
- [Multi-Agent Sandbox & Tools](/es/tools/multi-agent-sandbox-tools) -- sobrescrituras por agente y precedencia
- [Security](/es/gateway/security)
