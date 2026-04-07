---
read_when:
    - Responder preguntas comunes de soporte sobre configuración, instalación, onboarding o runtime
    - Clasificar problemas reportados por usuarios antes de una depuración más profunda
summary: Preguntas frecuentes sobre la configuración, instalación, onboarding y uso de OpenClaw
title: Preguntas frecuentes
x-i18n:
    generated_at: "2026-04-07T05:08:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: bddcde55cf4bcec4913aadab4c665b235538104010e445e4c99915a1672b1148
    source_path: help/faq.md
    workflow: 15
---

# Preguntas frecuentes

Respuestas rápidas más solución de problemas más profunda para configuraciones del mundo real (desarrollo local, VPS, multiagente, OAuth/claves de API, failover de modelos). Para diagnósticos del runtime, consulta [Troubleshooting](/es/gateway/troubleshooting). Para la referencia completa de configuración, consulta [Configuration](/es/gateway/configuration).

## Primeros 60 segundos si algo está roto

1. **Estado rápido (primera comprobación)**

   ```bash
   openclaw status
   ```

   Resumen local rápido: SO + actualización, accesibilidad de gateway/servicio, agentes/sesiones, configuración del proveedor + problemas de runtime (cuando el gateway es accesible).

2. **Informe fácil de compartir (seguro para compartir)**

   ```bash
   openclaw status --all
   ```

   Diagnóstico de solo lectura con cola de logs (tokens censurados).

3. **Estado del demonio + puerto**

   ```bash
   openclaw gateway status
   ```

   Muestra el runtime del supervisor frente a la accesibilidad RPC, la URL de destino de la sonda y qué configuración probablemente usó el servicio.

4. **Sondas profundas**

   ```bash
   openclaw status --deep
   ```

   Ejecuta una sonda de estado del gateway en vivo, incluidas sondas de canal cuando son compatibles
   (requiere un gateway accesible). Consulta [Health](/es/gateway/health).

5. **Seguir el último log**

   ```bash
   openclaw logs --follow
   ```

   Si RPC está caído, usa como alternativa:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Los logs de archivo son independientes de los logs del servicio; consulta [Logging](/es/logging) y [Troubleshooting](/es/gateway/troubleshooting).

6. **Ejecuta Doctor (reparaciones)**

   ```bash
   openclaw doctor
   ```

   Repara/migra configuración/estado + ejecuta comprobaciones de estado. Consulta [Doctor](/es/gateway/doctor).

7. **Instantánea del gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # muestra la URL de destino + la ruta de configuración en caso de errores
   ```

   Pide al gateway en ejecución una instantánea completa (solo WS). Consulta [Health](/es/gateway/health).

## Inicio rápido y configuración de la primera ejecución

<AccordionGroup>
  <Accordion title="Estoy atascado, ¿cuál es la forma más rápida de salir?">
    Usa un agente de IA local que pueda **ver tu máquina**. Eso es mucho más efectivo que preguntar
    en Discord, porque la mayoría de los casos de “estoy atascado” son **problemas locales de configuración o entorno** que
    los ayudantes remotos no pueden inspeccionar.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Estas herramientas pueden leer el repositorio, ejecutar comandos, inspeccionar logs y ayudar a corregir la configuración
    de tu máquina (PATH, servicios, permisos, archivos de autenticación). Dales el **checkout completo del código fuente** mediante
    la instalación modificable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Esto instala OpenClaw **desde un checkout de git**, para que el agente pueda leer el código + la documentación y
    razonar sobre la versión exacta que estás ejecutando. Siempre puedes volver a stable más adelante
    volviendo a ejecutar el instalador sin `--install-method git`.

    Consejo: pídele al agente que **planifique y supervise** la corrección (paso a paso), y luego ejecute solo los
    comandos necesarios. Eso mantiene los cambios pequeños y más fáciles de auditar.

    Si descubres un error real o una corrección, por favor abre un issue de GitHub o envía un PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Comienza con estos comandos (comparte las salidas cuando pidas ayuda):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Qué hacen:

    - `openclaw status`: instantánea rápida del estado del gateway/agente + configuración básica.
    - `openclaw models status`: comprueba la autenticación del proveedor + disponibilidad del modelo.
    - `openclaw doctor`: valida y repara problemas comunes de configuración/estado.

    Otras comprobaciones útiles de la CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Bucle rápido de depuración: [Primeros 60 segundos si algo está roto](#primeros-60-segundos-si-algo-está-roto).
    Documentación de instalación: [Install](/es/install), [Installer flags](/es/install/installer), [Updating](/es/install/updating).

  </Accordion>

  <Accordion title="Heartbeat sigue omitiéndose. ¿Qué significan los motivos de omisión?">
    Motivos comunes de omisión de heartbeat:

    - `quiet-hours`: fuera de la ventana configurada de horas activas
    - `empty-heartbeat-file`: `HEARTBEAT.md` existe pero solo contiene estructura vacía o solo encabezados
    - `no-tasks-due`: el modo de tareas de `HEARTBEAT.md` está activo pero todavía no vence ninguno de los intervalos de tarea
    - `alerts-disabled`: toda la visibilidad de heartbeat está desactivada (`showOk`, `showAlerts` y `useIndicator` están desactivados)

    En el modo de tareas, las marcas de tiempo de vencimiento solo se adelantan después de que una ejecución real de heartbeat
    se completa. Las ejecuciones omitidas no marcan tareas como completadas.

    Documentación: [Heartbeat](/es/gateway/heartbeat), [Automation & Tasks](/es/automation).

  </Accordion>

  <Accordion title="Forma recomendada de instalar y configurar OpenClaw">
    El repositorio recomienda ejecutar desde el código fuente y usar onboarding:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    El asistente también puede compilar recursos de la UI automáticamente. Después del onboarding, normalmente ejecutas Gateway en el puerto **18789**.

    Desde el código fuente (colaboradores/desarrollo):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # instala automáticamente las dependencias de la UI en la primera ejecución
    openclaw onboard
    ```

    Si todavía no tienes una instalación global, ejecútalo mediante `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="¿Cómo abro el panel después del onboarding?">
    El asistente abre tu navegador con una URL limpia del panel (sin token) justo después del onboarding y también imprime el enlace en el resumen. Mantén esa pestaña abierta; si no se abrió, copia/pega la URL impresa en la misma máquina.
  </Accordion>

  <Accordion title="¿Cómo autentico el panel en localhost frente a remoto?">
    **Localhost (misma máquina):**

    - Abre `http://127.0.0.1:18789/`.
    - Si pide autenticación con secreto compartido, pega el token o la contraseña configurados en la configuración de Control UI.
    - Origen del token: `gateway.auth.token` (o `OPENCLAW_GATEWAY_TOKEN`).
    - Origen de la contraseña: `gateway.auth.password` (o `OPENCLAW_GATEWAY_PASSWORD`).
    - Si todavía no hay configurado un secreto compartido, genera un token con `openclaw doctor --generate-gateway-token`.

    **No en localhost:**

    - **Tailscale Serve** (recomendado): mantén el bind en loopback, ejecuta `openclaw gateway --tailscale serve`, abre `https://<magicdns>/`. Si `gateway.auth.allowTailscale` es `true`, los encabezados de identidad satisfacen la autenticación de Control UI/WebSocket (sin pegar un secreto compartido, asume un host de gateway confiable); las API HTTP siguen requiriendo autenticación con secreto compartido salvo que uses deliberadamente `none` en el ingreso privado o autenticación HTTP de proxy confiable.
      Los intentos simultáneos incorrectos de autenticación de Serve desde el mismo cliente se serializan antes de que el limitador de autenticación fallida los registre, por lo que el segundo reintento incorrecto ya puede mostrar `retry later`.
    - **Bind de tailnet**: ejecuta `openclaw gateway --bind tailnet --token "<token>"` (o configura autenticación con contraseña), abre `http://<tailscale-ip>:18789/`, y luego pega el secreto compartido correspondiente en la configuración del panel.
    - **Proxy inverso con reconocimiento de identidad**: mantén Gateway detrás de un proxy confiable no loopback, configura `gateway.auth.mode: "trusted-proxy"`, y luego abre la URL del proxy.
    - **Túnel SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host` y luego abre `http://127.0.0.1:18789/`. La autenticación con secreto compartido sigue aplicándose sobre el túnel; pega el token o la contraseña configurados si te los pide.

    Consulta [Dashboard](/web/dashboard) y [Web surfaces](/web) para los modos de bind y los detalles de autenticación.

  </Accordion>

  <Accordion title="¿Por qué hay dos configuraciones de aprobación de exec para aprobaciones por chat?">
    Controlan capas diferentes:

    - `approvals.exec`: reenvía solicitudes de aprobación a destinos de chat
    - `channels.<channel>.execApprovals`: hace que ese canal actúe como un cliente nativo de aprobación para aprobaciones de exec

    La política de exec del host sigue siendo la puerta de aprobación real. La configuración del chat solo controla dónde aparecen las
    solicitudes de aprobación y cómo puede responder la gente.

    En la mayoría de las configuraciones **no** necesitas ambas:

    - Si el chat ya admite comandos y respuestas, `/approve` en el mismo chat funciona a través de la ruta compartida.
    - Si un canal nativo compatible puede inferir aprobadores de forma segura, OpenClaw ahora habilita automáticamente aprobaciones nativas priorizando DM cuando `channels.<channel>.execApprovals.enabled` no está configurado o es `"auto"`.
    - Cuando hay disponibles tarjetas/botones de aprobación nativos, esa UI nativa es la ruta principal; el agente solo debe incluir un comando manual `/approve` si el resultado de la herramienta dice que las aprobaciones por chat no están disponibles o que la aprobación manual es la única ruta.
    - Usa `approvals.exec` solo cuando las solicitudes también deban reenviarse a otros chats o salas de operaciones explícitas.
    - Usa `channels.<channel>.execApprovals.target: "channel"` o `"both"` solo cuando quieras explícitamente que las solicitudes de aprobación se publiquen de vuelta en la sala/tema de origen.
    - Las aprobaciones de plugins son independientes otra vez: usan `/approve` en el mismo chat de forma predeterminada, reenvío opcional con `approvals.plugin`, y solo algunos canales nativos mantienen encima el manejo nativo de aprobación de plugins.

    Versión corta: el reenvío es para el enrutamiento, la configuración del cliente nativo es para una UX específica del canal más rica.
    Consulta [Exec Approvals](/es/tools/exec-approvals).

  </Accordion>

  <Accordion title="¿Qué runtime necesito?">
    Se requiere Node **>= 22**. Se recomienda `pnpm`. Bun **no se recomienda** para Gateway.
  </Accordion>

  <Accordion title="¿Funciona en Raspberry Pi?">
    Sí. Gateway es ligero: la documentación indica que **512 MB-1 GB de RAM**, **1 núcleo** y unos **500 MB**
    de disco son suficientes para uso personal, y señala que una **Raspberry Pi 4 puede ejecutarlo**.

    Si quieres margen adicional (logs, medios, otros servicios), se recomiendan **2 GB**, pero
    no es un mínimo estricto.

    Consejo: una Pi/VPS pequeña puede alojar Gateway, y puedes emparejar **nodos** en tu portátil/teléfono para
    pantalla/cámara/canvas local o ejecución de comandos. Consulta [Nodes](/es/nodes).

  </Accordion>

  <Accordion title="¿Algún consejo para instalaciones en Raspberry Pi?">
    Versión corta: funciona, pero espera algunos bordes ásperos.

    - Usa un SO de **64 bits** y mantén Node >= 22.
    - Prefiere la **instalación modificable (git)** para poder ver logs y actualizar rápido.
    - Empieza sin canales/Skills, luego añádelos uno por uno.
    - Si te encuentras con problemas binarios extraños, normalmente es un problema de **compatibilidad ARM**.

    Documentación: [Linux](/es/platforms/linux), [Install](/es/install).

  </Accordion>

  <Accordion title="Está atascado en wake up my friend / onboarding no termina. ¿Y ahora qué?">
    Esa pantalla depende de que el Gateway sea accesible y esté autenticado. La TUI también envía
    "Wake up, my friend!" automáticamente en la primera activación. Si ves esa línea **sin respuesta**
    y los tokens se quedan en 0, el agente nunca se ejecutó.

    1. Reinicia Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Comprueba estado + autenticación:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Si sigue colgado, ejecuta:

    ```bash
    openclaw doctor
    ```

    Si Gateway es remoto, asegúrate de que el túnel/la conexión de Tailscale esté activa y de que la UI
    apunte al Gateway correcto. Consulta [Remote access](/es/gateway/remote).

  </Accordion>

  <Accordion title="¿Puedo migrar mi configuración a una máquina nueva (Mac mini) sin rehacer el onboarding?">
    Sí. Copia el **directorio de estado** y el **espacio de trabajo**, luego ejecuta Doctor una vez. Esto
    mantiene tu bot “exactamente igual” (memoria, historial de sesión, autenticación y
    estado del canal) siempre que copies **ambas** ubicaciones:

    1. Instala OpenClaw en la máquina nueva.
    2. Copia `$OPENCLAW_STATE_DIR` (predeterminado: `~/.openclaw`) desde la máquina antigua.
    3. Copia tu espacio de trabajo (predeterminado: `~/.openclaw/workspace`).
    4. Ejecuta `openclaw doctor` y reinicia el servicio Gateway.

    Eso conserva la configuración, perfiles de autenticación, credenciales de WhatsApp, sesiones y memoria. Si estás en
    modo remoto, recuerda que el host del gateway es propietario del almacén de sesiones y del espacio de trabajo.

    **Importante:** si solo haces commit/push de tu espacio de trabajo a GitHub, estás haciendo copia de seguridad
    de **memoria + archivos de arranque**, pero **no** del historial de sesiones ni de la autenticación. Esos viven
    bajo `~/.openclaw/` (por ejemplo `~/.openclaw/agents/<agentId>/sessions/`).

    Relacionado: [Migrating](/es/install/migrating), [Dónde viven las cosas en disco](#dónde-viven-las-cosas-en-disco),
    [Agent workspace](/es/concepts/agent-workspace), [Doctor](/es/gateway/doctor),
    [Remote mode](/es/gateway/remote).

  </Accordion>

  <Accordion title="¿Dónde veo las novedades de la última versión?">
    Consulta el changelog de GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Las entradas más nuevas están arriba. Si la sección superior está marcada como **Unreleased**, la siguiente sección
    con fecha es la última versión publicada. Las entradas se agrupan por **Highlights**, **Changes** y
    **Fixes** (más secciones de documentación/u otras cuando hace falta).

  </Accordion>

  <Accordion title="No puedo acceder a docs.openclaw.ai (error SSL)">
    Algunas conexiones de Comcast/Xfinity bloquean incorrectamente `docs.openclaw.ai` mediante Xfinity
    Advanced Security. Desactívalo o añade `docs.openclaw.ai` a la lista de permitidos y vuelve a intentarlo.
    Ayúdanos a desbloquearlo informándolo aquí: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Si todavía no puedes acceder al sitio, la documentación está reflejada en GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Diferencia entre stable y beta">
    **Stable** y **beta** son **npm dist-tags**, no líneas de código separadas:

    - `latest` = stable
    - `beta` = compilación temprana para pruebas

    Habitualmente, una versión stable llega primero a **beta**, luego un paso explícito
    de promoción mueve esa misma versión a `latest`. Los maintainers también pueden
    publicar directamente en `latest` cuando hace falta. Por eso beta y stable pueden
    apuntar a la **misma versión** después de la promoción.

    Mira qué cambió:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Para los one-liners de instalación y la diferencia entre beta y dev, consulta el acordeón inferior.

  </Accordion>

  <Accordion title="¿Cómo instalo la versión beta y cuál es la diferencia entre beta y dev?">
    **Beta** es el npm dist-tag `beta` (puede coincidir con `latest` después de la promoción).
    **Dev** es la cabeza móvil de `main` (git); cuando se publica, usa el npm dist-tag `dev`.

    One-liners (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Instalador de Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Más detalle: [Development channels](/es/install/development-channels) y [Installer flags](/es/install/installer).

  </Accordion>

  <Accordion title="¿Cómo pruebo lo último?">
    Dos opciones:

    1. **Canal dev (checkout de git):**

    ```bash
    openclaw update --channel dev
    ```

    Esto cambia a la rama `main` y actualiza desde el código fuente.

    2. **Instalación modificable (desde el sitio del instalador):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Eso te da un repositorio local que puedes editar y luego actualizar mediante git.

    Si prefieres un clon limpio manual, usa:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Documentación: [Update](/cli/update), [Development channels](/es/install/development-channels),
    [Install](/es/install).

  </Accordion>

  <Accordion title="¿Cuánto suelen tardar la instalación y el onboarding?">
    Guía aproximada:

    - **Instalación:** 2-5 minutos
    - **Onboarding:** 5-15 minutos según cuántos canales/modelos configures

    Si se cuelga, usa [Installer stuck](#inicio-rápido-y-configuración-de-la-primera-ejecución)
    y el bucle rápido de depuración en [Estoy atascado](#inicio-rápido-y-configuración-de-la-primera-ejecución).

  </Accordion>

  <Accordion title="¿Instalador atascado? ¿Cómo obtengo más información?">
    Vuelve a ejecutar el instalador con **salida detallada**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Instalación beta con salida detallada:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Para una instalación modificable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Equivalente en Windows (PowerShell):

    ```powershell
    # install.ps1 todavía no tiene un flag -Verbose específico.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Más opciones: [Installer flags](/es/install/installer).

  </Accordion>

  <Accordion title="La instalación en Windows dice git not found o openclaw not recognized">
    Dos problemas comunes en Windows:

    **1) error de npm spawn git / git not found**

    - Instala **Git for Windows** y asegúrate de que `git` esté en tu PATH.
    - Cierra y vuelve a abrir PowerShell, luego vuelve a ejecutar el instalador.

    **2) openclaw is not recognized después de la instalación**

    - Tu carpeta global bin de npm no está en PATH.
    - Comprueba la ruta:

      ```powershell
      npm config get prefix
      ```

    - Añade ese directorio a tu PATH de usuario (no hace falta el sufijo `\bin` en Windows; en la mayoría de los sistemas es `%AppData%\npm`).
    - Cierra y vuelve a abrir PowerShell después de actualizar PATH.

    Si quieres la configuración más fluida en Windows, usa **WSL2** en lugar de Windows nativo.
    Documentación: [Windows](/es/platforms/windows).

  </Accordion>

  <Accordion title="La salida de exec en Windows muestra texto chino corrupto: ¿qué debo hacer?">
    Normalmente esto es un desajuste de página de códigos de la consola en shells nativos de Windows.

    Síntomas:

    - La salida de `system.run`/`exec` muestra el chino como mojibake
    - El mismo comando se ve bien en otro perfil de terminal

    Solución rápida en PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Luego reinicia Gateway y vuelve a intentar el comando:

    ```powershell
    openclaw gateway restart
    ```

    Si sigues reproduciendo esto en la última versión de OpenClaw, haz seguimiento/informa en:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="La documentación no respondió mi pregunta. ¿Cómo consigo una mejor respuesta?">
    Usa la **instalación modificable (git)** para tener el código fuente y la documentación completos localmente, luego pregunta
    a tu bot (o a Claude/Codex) _desde esa carpeta_ para que pueda leer el repositorio y responder con precisión.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Más detalle: [Install](/es/install) y [Installer flags](/es/install/installer).

  </Accordion>

  <Accordion title="¿Cómo instalo OpenClaw en Linux?">
    Respuesta corta: sigue la guía de Linux y luego ejecuta onboarding.

    - Ruta rápida de Linux + instalación del servicio: [Linux](/es/platforms/linux).
    - Recorrido completo: [Getting Started](/es/start/getting-started).
    - Instalador + actualizaciones: [Install & updates](/es/install/updating).

  </Accordion>

  <Accordion title="¿Cómo instalo OpenClaw en un VPS?">
    Cualquier VPS Linux funciona. Instálalo en el servidor y luego usa SSH/Tailscale para acceder a Gateway.

    Guías: [exe.dev](/es/install/exe-dev), [Hetzner](/es/install/hetzner), [Fly.io](/es/install/fly).
    Acceso remoto: [Gateway remote](/es/gateway/remote).

  </Accordion>

  <Accordion title="¿Dónde están las guías de instalación en la nube/VPS?">
    Mantenemos un **hub de alojamiento** con los proveedores habituales. Elige uno y sigue la guía:

    - [VPS hosting](/es/vps) (todos los proveedores en un solo lugar)
    - [Fly.io](/es/install/fly)
    - [Hetzner](/es/install/hetzner)
    - [exe.dev](/es/install/exe-dev)

    Cómo funciona en la nube: el **Gateway se ejecuta en el servidor**, y accedes a él
    desde tu portátil/teléfono mediante la Control UI (o Tailscale/SSH). Tu estado + espacio de trabajo
    viven en el servidor, así que trata el host como la fuente de verdad y haz copias de seguridad.

    Puedes emparejar **nodos** (Mac/iOS/Android/headless) con ese Gateway en la nube para acceder a
    pantalla/cámara/canvas locales o ejecutar comandos en tu portátil mientras mantienes
    el Gateway en la nube.

    Hub: [Platforms](/es/platforms). Acceso remoto: [Gateway remote](/es/gateway/remote).
    Nodos: [Nodes](/es/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="¿Puedo pedirle a OpenClaw que se actualice a sí mismo?">
    Respuesta corta: **posible, no recomendado**. El flujo de actualización puede reiniciar
    Gateway (lo que corta la sesión activa), puede necesitar un checkout de git limpio, y
    puede pedir confirmación. Más seguro: ejecutar las actualizaciones desde un shell como operador.

    Usa la CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Si debes automatizar desde un agente:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Documentación: [Update](/cli/update), [Updating](/es/install/updating).

  </Accordion>

  <Accordion title="¿Qué hace realmente onboarding?">
    `openclaw onboard` es la ruta de configuración recomendada. En **modo local** te guía por:

    - **Configuración de modelo/autenticación** (OAuth del proveedor, claves de API, setup-token de Anthropic, más opciones de modelo local como LM Studio)
    - Ubicación del **espacio de trabajo** + archivos de arranque
    - **Configuración de Gateway** (bind/puerto/autenticación/tailscale)
    - **Canales** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, más plugins de canal incluidos como QQ Bot)
    - **Instalación del demonio** (LaunchAgent en macOS; unidad de usuario systemd en Linux/WSL2)
    - **Comprobaciones de estado** y selección de **Skills**

    También avisa si tu modelo configurado es desconocido o si le falta autenticación.

  </Accordion>

  <Accordion title="¿Necesito una suscripción de Claude u OpenAI para ejecutar esto?">
    No. Puedes ejecutar OpenClaw con **claves de API** (Anthropic/OpenAI/otros) o con
    **modelos solo locales** para que tus datos permanezcan en tu dispositivo. Las suscripciones (Claude
    Pro/Max o OpenAI Codex) son formas opcionales de autenticar esos proveedores.

    Para Anthropic en OpenClaw, la división práctica es:

    - **Clave de API de Anthropic**: facturación normal de la API de Anthropic
    - **Claude CLI / autenticación de suscripción de Claude en OpenClaw**: el personal de Anthropic
      nos dijo que este uso vuelve a estar permitido, y OpenClaw está tratando el uso de `claude -p`
      como autorizado para esta integración salvo que Anthropic publique una nueva
      política

    Para hosts de gateway de larga duración, las claves de API de Anthropic siguen siendo la configuración
    más predecible. OpenAI Codex OAuth es compatible explícitamente para herramientas externas
    como OpenClaw.

    OpenClaw también admite otras opciones alojadas de estilo suscripción, incluidas
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** y
    **Z.AI / GLM Coding Plan**.

    Documentación: [Anthropic](/es/providers/anthropic), [OpenAI](/es/providers/openai),
    [Qwen Cloud](/es/providers/qwen),
    [MiniMax](/es/providers/minimax), [GLM Models](/es/providers/glm),
    [Local models](/es/gateway/local-models), [Models](/es/concepts/models).

  </Accordion>

  <Accordion title="¿Puedo usar la suscripción Claude Max sin una clave de API?">
    Sí.

    El personal de Anthropic nos dijo que el uso de Claude CLI al estilo OpenClaw vuelve a estar permitido, por lo que
    OpenClaw trata la autenticación por suscripción de Claude y el uso de `claude -p` como autorizados
    para esta integración salvo que Anthropic publique una nueva política. Si quieres
    la configuración del lado del servidor más predecible, usa una clave de API de Anthropic en su lugar.

  </Accordion>

  <Accordion title="¿Admiten autenticación por suscripción de Claude (Claude Pro o Max)?">
    Sí.

    El personal de Anthropic nos dijo que este uso vuelve a estar permitido, por lo que OpenClaw trata
    la reutilización de Claude CLI y el uso de `claude -p` como autorizados para esta integración
    salvo que Anthropic publique una nueva política.

    El setup-token de Anthropic sigue estando disponible como ruta compatible de token de OpenClaw, pero OpenClaw ahora prefiere la reutilización de Claude CLI y `claude -p` cuando están disponibles.
    Para producción o cargas de trabajo multiusuario, la autenticación con clave de API de Anthropic sigue siendo la
    opción más segura y predecible. Si quieres otras opciones alojadas de estilo suscripción
    en OpenClaw, consulta [OpenAI](/es/providers/openai), [Qwen / Model
    Cloud](/es/providers/qwen), [MiniMax](/es/providers/minimax), y [GLM
    Models](/es/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="¿Por qué veo HTTP 429 rate_limit_error de Anthropic?">
Eso significa que tu **cuota/límite de tasa de Anthropic** se agotó para la ventana actual. Si
usas **Claude CLI**, espera a que la ventana se restablezca o mejora tu plan. Si
usas una **clave de API de Anthropic**, revisa Anthropic Console
para ver uso/facturación y aumenta los límites según sea necesario.

    Si el mensaje es específicamente:
    `Extra usage is required for long context requests`, la solicitud está intentando usar
    la beta de contexto 1M de Anthropic (`context1m: true`). Eso solo funciona cuando tu
    credencial es apta para facturación de contexto largo (facturación con clave de API o la
    ruta de inicio de sesión Claude de OpenClaw con Extra Usage habilitado).

    Consejo: configura un **modelo de respaldo** para que OpenClaw pueda seguir respondiendo mientras un proveedor está limitado por tasa.
    Consulta [Models](/cli/models), [OAuth](/es/concepts/oauth), y
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/es/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="¿AWS Bedrock es compatible?">
    Sí. OpenClaw tiene un proveedor incluido de **Amazon Bedrock (Converse)**. Con marcadores de entorno de AWS presentes, OpenClaw puede autodetectar el catálogo Bedrock de streaming/texto y fusionarlo como un proveedor implícito `amazon-bedrock`; de lo contrario, puedes habilitar explícitamente `plugins.entries.amazon-bedrock.config.discovery.enabled` o añadir una entrada manual de proveedor. Consulta [Amazon Bedrock](/es/providers/bedrock) y [Model providers](/es/providers/models). Si prefieres un flujo de claves administradas, un proxy compatible con OpenAI delante de Bedrock sigue siendo una opción válida.
  </Accordion>

  <Accordion title="¿Cómo funciona la autenticación de Codex?">
    OpenClaw admite **OpenAI Code (Codex)** mediante OAuth (inicio de sesión de ChatGPT). Onboarding puede ejecutar el flujo OAuth y establecerá el modelo predeterminado en `openai-codex/gpt-5.4` cuando corresponda. Consulta [Model providers](/es/concepts/model-providers) y [Onboarding (CLI)](/es/start/wizard).
  </Accordion>

  <Accordion title="¿Por qué ChatGPT GPT-5.4 no desbloquea openai/gpt-5.4 en OpenClaw?">
    OpenClaw trata las dos rutas por separado:

    - `openai-codex/gpt-5.4` = OAuth de ChatGPT/Codex
    - `openai/gpt-5.4` = API directa de OpenAI Platform

    En OpenClaw, el inicio de sesión de ChatGPT/Codex está conectado a la ruta `openai-codex/*`,
    no a la ruta directa `openai/*`. Si quieres la ruta de API directa en
    OpenClaw, configura `OPENAI_API_KEY` (o la configuración equivalente del proveedor OpenAI).
    Si quieres el inicio de sesión de ChatGPT/Codex en OpenClaw, usa `openai-codex/*`.

  </Accordion>

  <Accordion title="¿Por qué los límites de Codex OAuth pueden diferir de ChatGPT web?">
    `openai-codex/*` usa la ruta OAuth de Codex, y sus ventanas de cuota utilizables están
    gestionadas por OpenAI y dependen del plan. En la práctica, esos límites pueden diferir de
    la experiencia del sitio/app de ChatGPT, incluso cuando ambos están vinculados a la misma cuenta.

    OpenClaw puede mostrar las ventanas de uso/cuota visibles actualmente del proveedor en
    `openclaw models status`, pero no inventa ni normaliza
    permisos de ChatGPT web en acceso directo a la API. Si quieres la ruta directa de
    facturación/límites de OpenAI Platform, usa `openai/*` con una clave de API.

  </Accordion>

  <Accordion title="¿Admiten autenticación por suscripción de OpenAI (Codex OAuth)?">
    Sí. OpenClaw admite completamente **OAuth por suscripción de OpenAI Code (Codex)**.
    OpenAI permite explícitamente el uso de OAuth por suscripción en herramientas/flujos de trabajo externos
    como OpenClaw. Onboarding puede ejecutar ese flujo OAuth por ti.

    Consulta [OAuth](/es/concepts/oauth), [Model providers](/es/concepts/model-providers), y [Onboarding (CLI)](/es/start/wizard).

  </Accordion>

  <Accordion title="¿Cómo configuro OAuth de Gemini CLI?">
    Gemini CLI usa un **flujo de autenticación del plugin**, no un client id ni un secret en `openclaw.json`.

    Pasos:

    1. Instala Gemini CLI localmente para que `gemini` esté en `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Habilita el plugin: `openclaw plugins enable google`
    3. Inicia sesión: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Modelo predeterminado después del inicio de sesión: `google-gemini-cli/gemini-3.1-pro-preview`
    5. Si las solicitudes fallan, configura `GOOGLE_CLOUD_PROJECT` o `GOOGLE_CLOUD_PROJECT_ID` en el host del gateway

    Esto almacena los tokens OAuth en perfiles de autenticación en el host del gateway. Detalles: [Model providers](/es/concepts/model-providers).

  </Accordion>

  <Accordion title="¿Un modelo local sirve para chats casuales?">
    Normalmente no. OpenClaw necesita un contexto grande + una seguridad sólida; las tarjetas pequeñas truncan y filtran. Si es imprescindible, ejecuta la compilación de modelo **más grande** que puedas localmente (LM Studio) y consulta [/gateway/local-models](/es/gateway/local-models). Los modelos más pequeños/cuantizados aumentan el riesgo de inyección de prompts: consulta [Security](/es/gateway/security).
  </Accordion>

  <Accordion title="¿Cómo mantengo el tráfico de modelos alojados en una región específica?">
    Elige endpoints fijados por región. OpenRouter ofrece opciones alojadas en EE. UU. para MiniMax, Kimi y GLM; elige la variante alojada en EE. UU. para mantener los datos en la región. Aun así, puedes listar Anthropic/OpenAI junto con estos usando `models.mode: "merge"` para que los respaldos sigan disponibles mientras respetas el proveedor regional que selecciones.
  </Accordion>

  <Accordion title="¿Tengo que comprar un Mac Mini para instalar esto?">
    No. OpenClaw se ejecuta en macOS o Linux (Windows mediante WSL2). Un Mac mini es opcional: algunas personas
    compran uno como host siempre activo, pero también sirve un VPS pequeño, servidor doméstico o máquina de clase Raspberry Pi.

    Solo necesitas un Mac **para herramientas exclusivas de macOS**. Para iMessage, usa [BlueBubbles](/es/channels/bluebubbles) (recomendado): el servidor BlueBubbles se ejecuta en cualquier Mac, y Gateway puede ejecutarse en Linux o en otro lugar. Si quieres otras herramientas exclusivas de macOS, ejecuta Gateway en un Mac o empareja un nodo macOS.

    Documentación: [BlueBubbles](/es/channels/bluebubbles), [Nodes](/es/nodes), [Mac remote mode](/es/platforms/mac/remote).

  </Accordion>

  <Accordion title="¿Necesito un Mac mini para compatibilidad con iMessage?">
    Necesitas **algún dispositivo macOS** con sesión iniciada en Messages. **No** tiene que ser un Mac mini:
    cualquier Mac sirve. **Usa [BlueBubbles](/es/channels/bluebubbles)** (recomendado) para iMessage: el servidor BlueBubbles se ejecuta en macOS, mientras que Gateway puede ejecutarse en Linux o en otro lugar.

    Configuraciones habituales:

    - Ejecuta Gateway en Linux/VPS y el servidor BlueBubbles en cualquier Mac con sesión iniciada en Messages.
    - Ejecuta todo en el Mac si quieres la configuración más simple de una sola máquina.

    Documentación: [BlueBubbles](/es/channels/bluebubbles), [Nodes](/es/nodes),
    [Mac remote mode](/es/platforms/mac/remote).

  </Accordion>

  <Accordion title="Si compro un Mac mini para ejecutar OpenClaw, ¿puedo conectarlo a mi MacBook Pro?">
    Sí. El **Mac mini puede ejecutar Gateway**, y tu MacBook Pro puede conectarse como
    **nodo** (dispositivo complementario). Los nodos no ejecutan Gateway: proporcionan capacidades
    extra como pantalla/cámara/canvas y `system.run` en ese dispositivo.

    Patrón habitual:

    - Gateway en el Mac mini (siempre activo).
    - MacBook Pro ejecuta la app de macOS o un host de nodo y se empareja con Gateway.
    - Usa `openclaw nodes status` / `openclaw nodes list` para verlo.

    Documentación: [Nodes](/es/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="¿Puedo usar Bun?">
    Bun **no se recomienda**. Vemos errores de runtime, especialmente con WhatsApp y Telegram.
    Usa **Node** para gateways estables.

    Si aun así quieres experimentar con Bun, hazlo en un gateway no productivo
    sin WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: ¿qué va en allowFrom?">
    `channels.telegram.allowFrom` es **el ID de usuario de Telegram del remitente humano** (numérico). No es el nombre de usuario del bot.

    Onboarding acepta entrada `@username` y la resuelve a un ID numérico, pero la autorización de OpenClaw usa solo IDs numéricos.

    Más seguro (sin bot de terceros):

    - Envía un DM a tu bot, luego ejecuta `openclaw logs --follow` y lee `from.id`.

    API oficial de Bot:

    - Envía un DM a tu bot, luego llama a `https://api.telegram.org/bot<bot_token>/getUpdates` y lee `message.from.id`.

    Terceros (menos privado):

    - Envía un DM a `@userinfobot` o `@getidsbot`.

    Consulta [/channels/telegram](/es/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="¿Pueden varias personas usar un número de WhatsApp con distintas instancias de OpenClaw?">
    Sí, mediante **enrutamiento multiagente**. Vincula el **DM** de WhatsApp de cada remitente (peer `kind: "direct"`, remitente E.164 como `+15551234567`) a un `agentId` diferente, para que cada persona tenga su propio espacio de trabajo y almacén de sesiones. Las respuestas siguen saliendo desde la **misma cuenta de WhatsApp**, y el control de acceso DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) es global por cuenta de WhatsApp. Consulta [Multi-Agent Routing](/es/concepts/multi-agent) y [WhatsApp](/es/channels/whatsapp).
  </Accordion>

  <Accordion title='¿Puedo ejecutar un agente de "chat rápido" y otro "Opus para programar"?'>
    Sí. Usa enrutamiento multiagente: da a cada agente su propio modelo predeterminado y luego vincula las rutas entrantes (cuenta del proveedor o peers específicos) a cada agente. La configuración de ejemplo está en [Multi-Agent Routing](/es/concepts/multi-agent). Consulta también [Models](/es/concepts/models) y [Configuration](/es/gateway/configuration).
  </Accordion>

  <Accordion title="¿Homebrew funciona en Linux?">
    Sí. Homebrew admite Linux (Linuxbrew). Configuración rápida:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Si ejecutas OpenClaw mediante systemd, asegúrate de que el PATH del servicio incluya `/home/linuxbrew/.linuxbrew/bin` (o tu prefijo brew) para que las herramientas instaladas con `brew` se resuelvan en shells no interactivos.
    Las compilaciones recientes también anteponen directorios bin de usuario comunes en servicios Linux systemd (por ejemplo `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) y respetan `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` y `FNM_DIR` cuando están configurados.

  </Accordion>

  <Accordion title="Diferencia entre la instalación modificable con git y npm install">
    - **Instalación modificable (git):** checkout completo del código fuente, editable, mejor para colaboradores.
      Ejecutas compilaciones localmente y puedes modificar código/documentación.
    - **npm install:** instalación global de CLI, sin repositorio, mejor para “simplemente ejecutarlo”.
      Las actualizaciones vienen de npm dist-tags.

    Documentación: [Getting started](/es/start/getting-started), [Updating](/es/install/updating).

  </Accordion>

  <Accordion title="¿Puedo cambiar entre instalaciones npm y git más adelante?">
    Sí. Instala la otra variante y luego ejecuta Doctor para que el servicio gateway apunte al nuevo entrypoint.
    Esto **no elimina tus datos**: solo cambia la instalación de código de OpenClaw. Tu estado
    (`~/.openclaw`) y espacio de trabajo (`~/.openclaw/workspace`) permanecen intactos.

    De npm a git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    De git a npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor detecta un desajuste entre el entrypoint del servicio gateway y ofrece reescribir la configuración del servicio para que coincida con la instalación actual (usa `--repair` en automatización).

    Consejos de copia de seguridad: consulta [Estrategia de copia de seguridad](#dónde-viven-las-cosas-en-disco).

  </Accordion>

  <Accordion title="¿Debería ejecutar Gateway en mi portátil o en un VPS?">
    Respuesta corta: **si quieres fiabilidad 24/7, usa un VPS**. Si quieres la
    menor fricción y no te importan reposos/reinicios, ejecútalo localmente.

    **Portátil (Gateway local)**

    - **Ventajas:** sin coste de servidor, acceso directo a archivos locales, ventana visible del navegador.
    - **Desventajas:** reposo/caídas de red = desconexiones, las actualizaciones/reinicios del SO interrumpen, debe permanecer despierto.

    **VPS / nube**

    - **Ventajas:** siempre activo, red estable, sin problemas de reposo del portátil, más fácil de mantener en marcha.
    - **Desventajas:** a menudo se ejecuta sin interfaz (usa capturas de pantalla), acceso solo a archivos remotos, debes usar SSH para las actualizaciones.

    **Nota específica de OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord funcionan bien desde un VPS. La única diferencia real es **navegador headless** frente a una ventana visible. Consulta [Browser](/es/tools/browser).

    **Predeterminado recomendado:** VPS si antes tuviste desconexiones del gateway. Local es excelente cuando estás usando activamente el Mac y quieres acceso a archivos locales o automatización de UI con un navegador visible.

  </Accordion>

  <Accordion title="¿Qué tan importante es ejecutar OpenClaw en una máquina dedicada?">
    No es obligatorio, pero **se recomienda por fiabilidad y aislamiento**.

    - **Host dedicado (VPS/Mac mini/Pi):** siempre activo, menos interrupciones por reposo/reinicio, permisos más limpios, más fácil de mantener en marcha.
    - **Portátil/escritorio compartido:** perfectamente válido para pruebas y uso activo, pero espera pausas cuando la máquina entre en reposo o se actualice.

    Si quieres lo mejor de ambos mundos, mantén Gateway en un host dedicado y empareja tu portátil como **nodo** para herramientas locales de pantalla/cámara/exec. Consulta [Nodes](/es/nodes).
    Para la guía de seguridad, lee [Security](/es/gateway/security).

  </Accordion>

  <Accordion title="¿Cuáles son los requisitos mínimos de VPS y el SO recomendado?">
    OpenClaw es ligero. Para un Gateway básico + un canal de chat:

    - **Mínimo absoluto:** 1 vCPU, 1 GB de RAM, ~500 MB de disco.
    - **Recomendado:** 1-2 vCPU, 2 GB de RAM o más para margen (logs, medios, varios canales). Las herramientas de nodo y la automatización del navegador pueden consumir bastantes recursos.

    SO: usa **Ubuntu LTS** (o cualquier Debian/Ubuntu moderno). La ruta de instalación de Linux está mejor probada ahí.

    Documentación: [Linux](/es/platforms/linux), [VPS hosting](/es/vps).

  </Accordion>

  <Accordion title="¿Puedo ejecutar OpenClaw en una VM y cuáles son los requisitos?">
    Sí. Trata una VM igual que un VPS: debe estar siempre encendida, ser accesible y tener suficiente
    RAM para Gateway y cualquier canal que habilites.

    Orientación base:

    - **Mínimo absoluto:** 1 vCPU, 1 GB de RAM.
    - **Recomendado:** 2 GB de RAM o más si ejecutas varios canales, automatización del navegador o herramientas multimedia.
    - **SO:** Ubuntu LTS u otro Debian/Ubuntu moderno.

    Si estás en Windows, **WSL2 es la configuración tipo VM más sencilla** y tiene la mejor
    compatibilidad de herramientas. Consulta [Windows](/es/platforms/windows), [VPS hosting](/es/vps).
    Si ejecutas macOS en una VM, consulta [macOS VM](/es/install/macos-vm).

  </Accordion>
</AccordionGroup>

## ¿Qué es OpenClaw?

<AccordionGroup>
  <Accordion title="¿Qué es OpenClaw, en un párrafo?">
    OpenClaw es un asistente personal de IA que ejecutas en tus propios dispositivos. Responde en las superficies de mensajería que ya usas (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat y plugins de canal incluidos como QQ Bot) y también puede hacer voz + un Canvas en vivo en las plataformas compatibles. El **Gateway** es el plano de control siempre activo; el asistente es el producto.
  </Accordion>

  <Accordion title="Propuesta de valor">
    OpenClaw no es “solo un wrapper de Claude”. Es un **plano de control local-first** que te permite ejecutar un
    asistente capaz en **tu propio hardware**, accesible desde las apps de chat que ya usas, con
    sesiones con estado, memoria y herramientas, sin ceder el control de tus flujos de trabajo a un
    SaaS alojado.

    Aspectos destacados:

    - **Tus dispositivos, tus datos:** ejecuta Gateway donde quieras (Mac, Linux, VPS) y mantén
      el espacio de trabajo + historial de sesiones locales.
    - **Canales reales, no un sandbox web:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/etc.,
      además de voz móvil y Canvas en plataformas compatibles.
    - **Agnóstico respecto al modelo:** usa Anthropic, OpenAI, MiniMax, OpenRouter, etc., con enrutamiento
      y failover por agente.
    - **Opción solo local:** ejecuta modelos locales para que **todos los datos puedan permanecer en tu dispositivo** si quieres.
    - **Enrutamiento multiagente:** separa agentes por canal, cuenta o tarea, cada uno con su propio
      espacio de trabajo y valores predeterminados.
    - **Código abierto y modificable:** inspecciona, amplía y autoaloja sin dependencia de proveedores.

    Documentación: [Gateway](/es/gateway), [Channels](/es/channels), [Multi-agent](/es/concepts/multi-agent),
    [Memory](/es/concepts/memory).

  </Accordion>

  <Accordion title="Acabo de configurarlo. ¿Qué debería hacer primero?">
    Buenos primeros proyectos:

    - Crear un sitio web (WordPress, Shopify o un sitio estático simple).
    - Prototipar una app móvil (esquema, pantallas, plan de API).
    - Organizar archivos y carpetas (limpieza, nombres, etiquetas).
    - Conectar Gmail y automatizar resúmenes o seguimientos.

    Puede manejar tareas grandes, pero funciona mejor cuando las divides en fases y
    usas subagentes para trabajo en paralelo.

  </Accordion>

  <Accordion title="¿Cuáles son los cinco casos de uso cotidianos principales de OpenClaw?">
    Las victorias cotidianas suelen verse así:

    - **Briefings personales:** resúmenes de la bandeja de entrada, calendario y noticias que te importan.
    - **Investigación y redacción:** investigación rápida, resúmenes y primeros borradores para correos o documentos.
    - **Recordatorios y seguimientos:** avisos y listas de verificación impulsados por cron o heartbeat.
    - **Automatización del navegador:** rellenar formularios, recopilar datos y repetir tareas web.
    - **Coordinación entre dispositivos:** envía una tarea desde tu teléfono, deja que Gateway la ejecute en un servidor y recibe el resultado de vuelta en el chat.

  </Accordion>

  <Accordion title="¿Puede OpenClaw ayudar con lead gen, outreach, anuncios y blogs para un SaaS?">
    Sí, para **investigación, calificación y redacción**. Puede analizar sitios, crear listas cortas,
    resumir prospectos y redactar borradores de mensajes de outreach o de anuncios.

    Para **outreach o campañas publicitarias**, mantén a un humano en el circuito. Evita el spam, sigue las leyes locales y
    las políticas de la plataforma, y revisa todo antes de enviarlo. El patrón más seguro es dejar que
    OpenClaw redacte y que tú apruebes.

    Documentación: [Security](/es/gateway/security).

  </Accordion>

  <Accordion title="¿Cuáles son las ventajas frente a Claude Code para desarrollo web?">
    OpenClaw es un **asistente personal** y una capa de coordinación, no un reemplazo del IDE. Usa
    Claude Code o Codex para el bucle de programación directa más rápido dentro de un repositorio. Usa OpenClaw cuando
    quieras memoria duradera, acceso entre dispositivos y orquestación de herramientas.

    Ventajas:

    - **Memoria + espacio de trabajo persistentes** entre sesiones
    - **Acceso multiplataforma** (WhatsApp, Telegram, TUI, WebChat)
    - **Orquestación de herramientas** (navegador, archivos, programación, hooks)
    - **Gateway siempre activo** (ejecútalo en un VPS, interactúa desde cualquier lugar)
    - **Nodos** para navegador/pantalla/cámara/exec locales

    Showcase: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills y automatización

<AccordionGroup>
  <Accordion title="¿Cómo personalizo Skills sin mantener el repositorio sucio?">
    Usa reemplazos administrados en lugar de editar la copia del repositorio. Coloca tus cambios en `~/.openclaw/skills/<name>/SKILL.md` (o añade una carpeta mediante `skills.load.extraDirs` en `~/.openclaw/openclaw.json`). La precedencia es `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → incluidos → `skills.load.extraDirs`, por lo que los reemplazos administrados siguen prevaleciendo sobre los Skills incluidos sin tocar git. Si necesitas que el Skill esté instalado globalmente pero solo visible para algunos agentes, mantén la copia compartida en `~/.openclaw/skills` y controla la visibilidad con `agents.defaults.skills` y `agents.list[].skills`. Solo los cambios dignos de upstream deberían vivir en el repositorio y salir como PR.
  </Accordion>

  <Accordion title="¿Puedo cargar Skills desde una carpeta personalizada?">
    Sí. Añade directorios extra mediante `skills.load.extraDirs` en `~/.openclaw/openclaw.json` (precedencia más baja). La precedencia predeterminada es `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → incluidos → `skills.load.extraDirs`. `clawhub` instala por defecto en `./skills`, que OpenClaw trata como `<workspace>/skills` en la siguiente sesión. Si el Skill solo debe ser visible para ciertos agentes, combínalo con `agents.defaults.skills` o `agents.list[].skills`.
  </Accordion>

  <Accordion title="¿Cómo puedo usar distintos modelos para distintas tareas?">
    Hoy los patrones compatibles son:

    - **Trabajos cron**: los trabajos aislados pueden establecer un reemplazo `model` por trabajo.
    - **Subagentes**: enruta tareas a agentes separados con distintos modelos predeterminados.
    - **Cambio bajo demanda**: usa `/model` para cambiar el modelo de la sesión actual en cualquier momento.

    Consulta [Cron jobs](/es/automation/cron-jobs), [Multi-Agent Routing](/es/concepts/multi-agent), y [Slash commands](/es/tools/slash-commands).

  </Accordion>

  <Accordion title="El bot se congela mientras hace trabajo pesado. ¿Cómo lo descargo?">
    Usa **subagentes** para tareas largas o paralelas. Los subagentes se ejecutan en su propia sesión,
    devuelven un resumen y mantienen tu chat principal receptivo.

    Pídele a tu bot que “cree un subagente para esta tarea” o usa `/subagents`.
    Usa `/status` en el chat para ver qué está haciendo Gateway ahora mismo (y si está ocupado).

    Consejo sobre tokens: tanto las tareas largas como los subagentes consumen tokens. Si el coste es una preocupación, configura un
    modelo más barato para subagentes mediante `agents.defaults.subagents.model`.

    Documentación: [Sub-agents](/es/tools/subagents), [Background Tasks](/es/automation/tasks).

  </Accordion>

  <Accordion title="¿Cómo funcionan las sesiones de subagente vinculadas a hilos en Discord?">
    Usa vínculos de hilos. Puedes vincular un hilo de Discord a un subagente o a un objetivo de sesión para que los mensajes de seguimiento en ese hilo permanezcan en esa sesión vinculada.

    Flujo básico:

    - Crea con `sessions_spawn` usando `thread: true` (y opcionalmente `mode: "session"` para seguimiento persistente).
    - O vincula manualmente con `/focus <target>`.
    - Usa `/agents` para inspeccionar el estado del vínculo.
    - Usa `/session idle <duration|off>` y `/session max-age <duration|off>` para controlar el desenfoque automático.
    - Usa `/unfocus` para desvincular el hilo.

    Configuración requerida:

    - Valores predeterminados globales: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Reemplazos de Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Vinculación automática al crear: configura `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Documentación: [Sub-agents](/es/tools/subagents), [Discord](/es/channels/discord), [Configuration Reference](/es/gateway/configuration-reference), [Slash commands](/es/tools/slash-commands).

  </Accordion>

  <Accordion title="Un subagente terminó, pero la actualización de finalización fue al lugar equivocado o nunca se publicó. ¿Qué debería comprobar?">
    Primero comprueba la ruta del solicitante resuelta:

    - La entrega del subagente en modo de finalización prefiere cualquier hilo vinculado o ruta de conversación cuando existe.
    - Si el origen de la finalización solo lleva un canal, OpenClaw recurre a la ruta almacenada de la sesión solicitante (`lastChannel` / `lastTo` / `lastAccountId`) para que la entrega directa aún pueda tener éxito.
    - Si no existe ni una ruta vinculada ni una ruta almacenada utilizable, la entrega directa puede fallar y el resultado vuelve a la entrega en cola de sesión en lugar de publicarse inmediatamente en el chat.
    - Los objetivos no válidos o obsoletos todavía pueden forzar la vuelta a la cola o el fallo final de la entrega.
    - Si la última respuesta visible del asistente del hijo es exactamente el token silencioso `NO_REPLY` / `no_reply`, o exactamente `ANNOUNCE_SKIP`, OpenClaw suprime intencionalmente el anuncio en lugar de publicar un progreso anterior obsoleto.
    - Si el hijo agotó el tiempo después de solo llamadas a herramientas, el anuncio puede colapsar eso en un breve resumen de progreso parcial en lugar de reproducir salida bruta de herramientas.

    Depuración:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentación: [Sub-agents](/es/tools/subagents), [Background Tasks](/es/automation/tasks), [Session Tools](/es/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron o los recordatorios no se activan. ¿Qué debería comprobar?">
    Cron se ejecuta dentro del proceso Gateway. Si Gateway no está en ejecución continua,
    los trabajos programados no se ejecutarán.

    Lista de comprobación:

    - Confirma que cron esté habilitado (`cron.enabled`) y que `OPENCLAW_SKIP_CRON` no esté configurado.
    - Comprueba que Gateway se esté ejecutando 24/7 (sin reposos/reinicios).
    - Verifica la configuración de zona horaria del trabajo (`--tz` frente a la zona horaria del host).

    Depuración:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Documentación: [Cron jobs](/es/automation/cron-jobs), [Automation & Tasks](/es/automation).

  </Accordion>

  <Accordion title="Cron se activó, pero no se envió nada al canal. ¿Por qué?">
    Primero comprueba el modo de entrega:

    - `--no-deliver` / `delivery.mode: "none"` significa que no se espera ningún mensaje externo.
    - Un objetivo de anuncio faltante o no válido (`channel` / `to`) significa que el ejecutor omitió la entrega saliente.
    - Errores de autenticación del canal (`unauthorized`, `Forbidden`) significan que el ejecutor intentó entregar, pero las credenciales lo bloquearon.
    - Un resultado aislado silencioso (`NO_REPLY` / `no_reply` solamente) se trata como intencionadamente no entregable, así que el ejecutor también suprime la entrega alternativa en cola.

    Para trabajos cron aislados, el ejecutor es propietario de la entrega final. Se espera
    que el agente devuelva un resumen en texto plano para que el ejecutor lo envíe. `--no-deliver` mantiene
    ese resultado interno; no permite que el agente envíe directamente con la
    herramienta de mensajes.

    Depuración:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentación: [Cron jobs](/es/automation/cron-jobs), [Background Tasks](/es/automation/tasks).

  </Accordion>

  <Accordion title="¿Por qué una ejecución cron aislada cambió de modelo o reintentó una vez?">
    Normalmente esa es la ruta de cambio de modelo en vivo, no una programación duplicada.

    Cron aislado puede persistir un traspaso de modelo en runtime y reintentar cuando la
    ejecución activa lanza `LiveSessionModelSwitchError`. El reintento mantiene el
    proveedor/modelo cambiado, y si el cambio incluía un nuevo reemplazo del perfil de autenticación, cron
    también lo persiste antes de reintentar.

    Reglas de selección relacionadas:

    - El reemplazo de modelo del hook de Gmail gana primero cuando corresponde.
    - Luego `model` por trabajo.
    - Luego cualquier reemplazo de modelo de sesión cron almacenado.
    - Luego la selección normal de modelo predeterminado/agente.

    El bucle de reintento es limitado. Tras el intento inicial más 2 reintentos por cambio,
    cron aborta en lugar de entrar en un bucle infinito.

    Depuración:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentación: [Cron jobs](/es/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="¿Cómo instalo Skills en Linux?">
    Usa comandos nativos `openclaw skills` o deja Skills en tu espacio de trabajo. La UI de Skills de macOS no está disponible en Linux.
    Explora Skills en [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    La instalación nativa `openclaw skills install` escribe en el directorio `skills/`
    del espacio de trabajo activo. Instala la CLI separada `clawhub` solo si quieres publicar o
    sincronizar tus propios Skills. Para instalaciones compartidas entre agentes, coloca el Skill bajo
    `~/.openclaw/skills` y usa `agents.defaults.skills` o
    `agents.list[].skills` si quieres limitar qué agentes pueden verlo.

  </Accordion>

  <Accordion title="¿Puede OpenClaw ejecutar tareas en un horario o continuamente en segundo plano?">
    Sí. Usa el programador de Gateway:

    - **Trabajos cron** para tareas programadas o recurrentes (persisten tras reinicios).
    - **Heartbeat** para comprobaciones periódicas de la “sesión principal”.
    - **Trabajos aislados** para agentes autónomos que publican resúmenes o entregan a chats.

    Documentación: [Cron jobs](/es/automation/cron-jobs), [Automation & Tasks](/es/automation),
    [Heartbeat](/es/gateway/heartbeat).

  </Accordion>

  <Accordion title="¿Puedo ejecutar Skills exclusivos de Apple macOS desde Linux?">
    No directamente. Los Skills de macOS están restringidos por `metadata.openclaw.os` más los binarios requeridos, y los Skills solo aparecen en el prompt del sistema cuando son elegibles en el **host de Gateway**. En Linux, los Skills solo para `darwin` (como `apple-notes`, `apple-reminders`, `things-mac`) no se cargarán salvo que reemplaces la restricción.

    Tienes tres patrones compatibles:

    **Opción A: ejecutar Gateway en un Mac (más simple).**
    Ejecuta Gateway donde existan los binarios de macOS, luego conéctate desde Linux en [modo remoto](#gateway-ya-en-ejecución-y-modo-remoto) o mediante Tailscale. Los Skills se cargan normalmente porque el host de Gateway es macOS.

    **Opción B: usar un nodo macOS (sin SSH).**
    Ejecuta Gateway en Linux, empareja un nodo macOS (app de barra de menús) y configura **Node Run Commands** en “Always Ask” o “Always Allow” en el Mac. OpenClaw puede tratar los Skills exclusivos de macOS como elegibles cuando los binarios requeridos existen en el nodo. El agente ejecuta esos Skills mediante la herramienta `nodes`. Si eliges “Always Ask”, aprobar “Always Allow” en el prompt añade ese comando a la lista de permitidos.

    **Opción C: hacer proxy de binarios macOS mediante SSH (avanzado).**
    Mantén Gateway en Linux, pero haz que los binarios CLI requeridos se resuelvan a wrappers SSH que se ejecuten en un Mac. Luego reemplaza el Skill para permitir Linux y así siga siendo elegible.

    1. Crea un wrapper SSH para el binario (ejemplo: `memo` para Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Pon el wrapper en `PATH` en el host Linux (por ejemplo `~/bin/memo`).
    3. Reemplaza los metadatos del Skill (espacio de trabajo o `~/.openclaw/skills`) para permitir Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Inicia una nueva sesión para que se actualice la instantánea de Skills.

  </Accordion>

  <Accordion title="¿Tienen una integración con Notion o HeyGen?">
    No integrada hoy.

    Opciones:

    - **Skill / plugin personalizado:** mejor para acceso fiable a la API (tanto Notion como HeyGen tienen API).
    - **Automatización del navegador:** funciona sin código, pero es más lenta y frágil.

    Si quieres mantener contexto por cliente (flujos de trabajo de agencia), un patrón simple es:

    - Una página de Notion por cliente (contexto + preferencias + trabajo activo).
    - Pedir al agente que recupere esa página al comienzo de una sesión.

    Si quieres una integración nativa, abre una solicitud de funcionalidad o crea un Skill
    dirigido a esas API.

    Instalar Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Las instalaciones nativas van al directorio `skills/` del espacio de trabajo activo. Para Skills compartidos entre agentes, colócalos en `~/.openclaw/skills/<name>/SKILL.md`. Si solo algunos agentes deberían ver una instalación compartida, configura `agents.defaults.skills` o `agents.list[].skills`. Algunos Skills esperan binarios instalados mediante Homebrew; en Linux eso significa Linuxbrew (consulta la entrada del FAQ de Homebrew en Linux anterior). Consulta [Skills](/es/tools/skills), [Skills config](/es/tools/skills-config), y [ClawHub](/es/tools/clawhub).

  </Accordion>

  <Accordion title="¿Cómo uso mi Chrome con sesión iniciada existente con OpenClaw?">
    Usa el perfil de navegador integrado `user`, que se conecta mediante Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Si quieres un nombre personalizado, crea un perfil MCP explícito:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Esta ruta es local al host. Si Gateway se ejecuta en otro lugar, ejecuta un host de nodo en la máquina del navegador o usa CDP remoto en su lugar.

    Límites actuales de `existing-session` / `user`:

    - las acciones están impulsadas por referencias, no por selectores CSS
    - las cargas requieren `ref` / `inputRef` y actualmente admiten un archivo cada vez
    - `responsebody`, exportación a PDF, interceptación de descargas y acciones por lotes todavía necesitan un navegador administrado o un perfil CDP sin procesar

  </Accordion>
</AccordionGroup>

## Sandboxing y memoria

<AccordionGroup>
  <Accordion title="¿Hay una documentación dedicada al sandboxing?">
    Sí. Consulta [Sandboxing](/es/gateway/sandboxing). Para configuración específica de Docker (gateway completo en Docker o imágenes de sandbox), consulta [Docker](/es/install/docker).
  </Accordion>

  <Accordion title="Docker se siente limitado. ¿Cómo habilito funciones completas?">
    La imagen predeterminada prioriza la seguridad y se ejecuta como el usuario `node`, así que no
    incluye paquetes del sistema, Homebrew ni navegadores incluidos. Para una configuración más completa:

    - Persiste `/home/node` con `OPENCLAW_HOME_VOLUME` para que sobrevivan las cachés.
    - Incorpora dependencias del sistema a la imagen con `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Instala navegadores Playwright mediante la CLI incluida:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Configura `PLAYWRIGHT_BROWSERS_PATH` y asegúrate de que la ruta se persista.

    Documentación: [Docker](/es/install/docker), [Browser](/es/tools/browser).

  </Accordion>

  <Accordion title="¿Puedo mantener los DM personales pero hacer públicos/sandboxed los grupos con un solo agente?">
    Sí, si tu tráfico privado son **DM** y tu tráfico público son **grupos**.

    Usa `agents.defaults.sandbox.mode: "non-main"` para que las sesiones de grupo/canal (claves no principales) se ejecuten en Docker, mientras la sesión principal DM permanece en el host. Luego restringe qué herramientas están disponibles en sesiones en sandbox mediante `tools.sandbox.tools`.

    Recorrido de configuración + ejemplo: [Groups: personal DMs + public groups](/es/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Referencia de configuración clave: [Gateway configuration](/es/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="¿Cómo vinculo una carpeta del host al sandbox?">
    Configura `agents.defaults.sandbox.docker.binds` como `["host:path:mode"]` (por ejemplo, `"/home/user/src:/src:ro"`). Los vínculos globales + por agente se fusionan; los vínculos por agente se ignoran cuando `scope: "shared"`. Usa `:ro` para cualquier cosa sensible y recuerda que los vínculos eluden las paredes del sistema de archivos del sandbox.

    OpenClaw valida los orígenes de los vínculos tanto respecto a la ruta normalizada como a la ruta canónica resuelta a través del ancestro existente más profundo. Eso significa que las fugas por padres con symlink siguen cerrándose incluso cuando el último segmento de la ruta todavía no existe, y las comprobaciones de raíces permitidas siguen aplicándose después de la resolución de symlinks.

    Consulta [Sandboxing](/es/gateway/sandboxing#custom-bind-mounts) y [Sandbox vs Tool Policy vs Elevated](/es/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) para ejemplos y notas de seguridad.

  </Accordion>

  <Accordion title="¿Cómo funciona la memoria?">
    La memoria de OpenClaw son simplemente archivos Markdown en el espacio de trabajo del agente:

    - Notas diarias en `memory/YYYY-MM-DD.md`
    - Notas curadas a largo plazo en `MEMORY.md` (solo sesiones principales/privadas)

    OpenClaw también ejecuta un **vaciado silencioso de memoria previo a la compactación** para recordar al modelo
    que escriba notas duraderas antes de la compactación automática. Esto solo se ejecuta cuando el espacio de trabajo
    es escribible (los sandboxes de solo lectura lo omiten). Consulta [Memory](/es/concepts/memory).

  </Accordion>

  <Accordion title="La memoria sigue olvidando cosas. ¿Cómo hago que se fijen?">
    Pídele al bot que **escriba el hecho en memoria**. Las notas de largo plazo van en `MEMORY.md`,
    el contexto de corto plazo va en `memory/YYYY-MM-DD.md`.

    Esta es todavía un área que estamos mejorando. Ayuda recordarle al modelo que almacene recuerdos;
    sabrá qué hacer. Si sigue olvidando, verifica que Gateway esté usando el mismo
    espacio de trabajo en cada ejecución.

    Documentación: [Memory](/es/concepts/memory), [Agent workspace](/es/concepts/agent-workspace).

  </Accordion>

  <Accordion title="¿La memoria persiste para siempre? ¿Cuáles son los límites?">
    Los archivos de memoria viven en disco y persisten hasta que los eliminas. El límite es tu
    almacenamiento, no el modelo. El **contexto de la sesión** sigue estando limitado por la ventana de contexto
    del modelo, por lo que las conversaciones largas pueden compactarse o truncarse. Por eso
    existe la búsqueda de memoria: recupera solo las partes relevantes al contexto.

    Documentación: [Memory](/es/concepts/memory), [Context](/es/concepts/context).

  </Accordion>

  <Accordion title="¿La búsqueda semántica de memoria requiere una clave de API de OpenAI?">
    Solo si usas **embeddings de OpenAI**. Codex OAuth cubre chat/completions y
    **no** concede acceso a embeddings, por lo que **iniciar sesión con Codex (OAuth o el
    inicio de sesión de Codex CLI)** no ayuda para la búsqueda semántica de memoria. Los embeddings de OpenAI
    siguen necesitando una clave de API real (`OPENAI_API_KEY` o `models.providers.openai.apiKey`).

    Si no configuras un proveedor explícitamente, OpenClaw selecciona automáticamente un proveedor cuando
    puede resolver una clave de API (perfiles de autenticación, `models.providers.*.apiKey` o variables de entorno).
    Prefiere OpenAI si se resuelve una clave de OpenAI; en caso contrario Gemini si se
    resuelve una clave de Gemini; luego Voyage; luego Mistral. Si no hay ninguna clave remota disponible, la búsqueda de memoria
    permanece deshabilitada hasta que la configures. Si tienes configurada y presente
    una ruta de modelo local, OpenClaw
    prefiere `local`. Ollama es compatible cuando configuras explícitamente
    `memorySearch.provider = "ollama"`.

    Si prefieres seguir en local, configura `memorySearch.provider = "local"` (y opcionalmente
    `memorySearch.fallback = "none"`). Si quieres embeddings de Gemini, configura
    `memorySearch.provider = "gemini"` y proporciona `GEMINI_API_KEY` (o
    `memorySearch.remote.apiKey`). Admitimos modelos de embeddings de **OpenAI, Gemini, Voyage, Mistral, Ollama o local**:
    consulta [Memory](/es/concepts/memory) para los detalles de configuración.

  </Accordion>
</AccordionGroup>

## Dónde viven las cosas en disco

<AccordionGroup>
  <Accordion title="¿Todos los datos usados con OpenClaw se guardan localmente?">
    No: **el estado de OpenClaw es local**, pero **los servicios externos siguen viendo lo que les envías**.

    - **Local por defecto:** las sesiones, archivos de memoria, configuración y espacio de trabajo viven en el host de Gateway
      (`~/.openclaw` + tu directorio de espacio de trabajo).
    - **Remoto por necesidad:** los mensajes que envías a proveedores de modelos (Anthropic/OpenAI/etc.) van a
      sus API, y las plataformas de chat (WhatsApp/Telegram/Slack/etc.) almacenan los datos de mensajes en sus
      servidores.
    - **Tú controlas la huella:** usar modelos locales mantiene los prompts en tu máquina, pero el
      tráfico del canal sigue pasando por los servidores del canal.

    Relacionado: [Agent workspace](/es/concepts/agent-workspace), [Memory](/es/concepts/memory).

  </Accordion>

  <Accordion title="¿Dónde almacena OpenClaw sus datos?">
    Todo vive bajo `$OPENCLAW_STATE_DIR` (predeterminado: `~/.openclaw`):

    | Ruta                                                            | Propósito                                                          |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Configuración principal (JSON5)                                    |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Importación heredada de OAuth (copiada a perfiles de autenticación en el primer uso) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Perfiles de autenticación (OAuth, claves de API y `keyRef`/`tokenRef` opcionales) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Carga útil opcional de secretos basada en archivo para proveedores `file` SecretRef |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Archivo heredado de compatibilidad (se depuran las entradas estáticas `api_key`) |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Estado del proveedor (p. ej. `whatsapp/<accountId>/creds.json`)    |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Estado por agente (`agentDir` + sesiones)                          |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Historial y estado de conversaciones (por agente)                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Metadatos de sesión (por agente)                                   |

    Ruta heredada de agente único: `~/.openclaw/agent/*` (migrada por `openclaw doctor`).

    Tu **espacio de trabajo** (`AGENTS.md`, archivos de memoria, Skills, etc.) es independiente y se configura mediante `agents.defaults.workspace` (predeterminado: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="¿Dónde deberían vivir AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Estos archivos viven en el **espacio de trabajo del agente**, no en `~/.openclaw`.

    - **Espacio de trabajo (por agente)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (o el fallback heredado `memory.md` cuando falta `MEMORY.md`),
      `memory/YYYY-MM-DD.md`, `HEARTBEAT.md` opcional.
    - **Directorio de estado (`~/.openclaw`)**: configuración, estado de canales/proveedores, perfiles de autenticación, sesiones, logs
      y Skills compartidos (`~/.openclaw/skills`).

    El espacio de trabajo predeterminado es `~/.openclaw/workspace`, configurable mediante:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Si el bot “olvida” después de un reinicio, confirma que Gateway esté usando el mismo
    espacio de trabajo en cada arranque (y recuerda: el modo remoto usa el espacio de trabajo del
    **host del gateway**, no el de tu portátil local).

    Consejo: si quieres un comportamiento o preferencia duraderos, pídele al bot que **lo escriba en
    AGENTS.md o MEMORY.md** en lugar de confiar en el historial del chat.

    Consulta [Agent workspace](/es/concepts/agent-workspace) y [Memory](/es/concepts/memory).

  </Accordion>

  <Accordion title="Estrategia de copia de seguridad recomendada">
    Pon tu **espacio de trabajo del agente** en un repositorio git **privado** y haz copia de seguridad en algún lugar
    privado (por ejemplo GitHub privado). Esto captura memoria + archivos AGENTS/SOUL/USER
    y te permite restaurar la “mente” del asistente más adelante.

    **No** hagas commit de nada bajo `~/.openclaw` (credenciales, sesiones, tokens o cargas cifradas de secretos).
    Si necesitas una restauración completa, haz copia de seguridad tanto del espacio de trabajo como del directorio de estado
    por separado (consulta la pregunta de migración anterior).

    Documentación: [Agent workspace](/es/concepts/agent-workspace).

  </Accordion>

  <Accordion title="¿Cómo desinstalo completamente OpenClaw?">
    Consulta la guía dedicada: [Uninstall](/es/install/uninstall).
  </Accordion>

  <Accordion title="¿Pueden los agentes trabajar fuera del espacio de trabajo?">
    Sí. El espacio de trabajo es el **cwd predeterminado** y el ancla de memoria, no un sandbox rígido.
    Las rutas relativas se resuelven dentro del espacio de trabajo, pero las rutas absolutas pueden acceder a otras
    ubicaciones del host salvo que el sandboxing esté habilitado. Si necesitas aislamiento, usa
    [`agents.defaults.sandbox`](/es/gateway/sandboxing) o configuración de sandbox por agente. Si quieres
    que un repositorio sea el directorio de trabajo predeterminado, apunta el
    `workspace` de ese agente a la raíz del repositorio. El repositorio de OpenClaw es solo código fuente; mantén el
    espacio de trabajo separado salvo que intencionadamente quieras que el agente trabaje dentro de él.

    Ejemplo (repositorio como cwd predeterminado):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Modo remoto: ¿dónde está el almacén de sesiones?">
    El estado de la sesión es propiedad del **host del gateway**. Si estás en modo remoto, el almacén de sesiones que te importa está en la máquina remota, no en tu portátil local. Consulta [Session management](/es/concepts/session).
  </Accordion>
</AccordionGroup>

## Conceptos básicos de configuración

<AccordionGroup>
  <Accordion title="¿Qué formato tiene la configuración? ¿Dónde está?">
    OpenClaw lee una configuración **JSON5** opcional desde `$OPENCLAW_CONFIG_PATH` (predeterminado: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Si el archivo no existe, usa valores predeterminados razonablemente seguros (incluido un espacio de trabajo predeterminado de `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Configuré gateway.bind: "lan" (o "tailnet") y ahora no escucha nada / la UI dice unauthorized'>
    Los binds no loopback **requieren una ruta válida de autenticación del gateway**. En la práctica eso significa:

    - autenticación con secreto compartido: token o contraseña
    - `gateway.auth.mode: "trusted-proxy"` detrás de un proxy inverso no loopback configurado correctamente y con reconocimiento de identidad

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Notas:

    - `gateway.remote.token` / `.password` **no** habilitan por sí solos la autenticación local del gateway.
    - Las rutas de llamada locales pueden usar `gateway.remote.*` como fallback solo cuando `gateway.auth.*` no está configurado.
    - Para autenticación con contraseña, configura `gateway.auth.mode: "password"` más `gateway.auth.password` (o `OPENCLAW_GATEWAY_PASSWORD`) en su lugar.
    - Si `gateway.auth.token` / `gateway.auth.password` se configuran explícitamente mediante SecretRef y no se resuelven, la resolución falla de forma cerrada (sin que el fallback remoto lo enmascare).
    - Las configuraciones de Control UI con secreto compartido se autentican mediante `connect.params.auth.token` o `connect.params.auth.password` (almacenados en la configuración de la app/UI). Los modos con identidad, como Tailscale Serve o `trusted-proxy`, usan en su lugar encabezados de solicitud. Evita poner secretos compartidos en URLs.
    - Con `gateway.auth.mode: "trusted-proxy"`, los proxies inversos loopback en el mismo host siguen **sin** satisfacer la autenticación trusted-proxy. El proxy confiable debe ser una fuente no loopback configurada.

  </Accordion>

  <Accordion title="¿Por qué ahora necesito un token en localhost?">
    OpenClaw aplica autenticación de gateway de forma predeterminada, incluido loopback. En la ruta predeterminada normal eso significa autenticación por token: si no se configura ninguna ruta de autenticación explícita, el arranque del gateway se resuelve al modo token y genera uno automáticamente, guardándolo en `gateway.auth.token`, por lo que **los clientes WS locales deben autenticarse**. Esto bloquea a otros procesos locales de llamar al Gateway.

    Si prefieres una ruta de autenticación diferente, puedes elegir explícitamente el modo contraseña (o, para proxies inversos no loopback con reconocimiento de identidad, `trusted-proxy`). Si **de verdad** quieres loopback abierto, configura `gateway.auth.mode: "none"` explícitamente en tu configuración. Doctor puede generarte un token en cualquier momento: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="¿Tengo que reiniciar después de cambiar la configuración?">
    Gateway observa la configuración y admite recarga en caliente:

    - `gateway.reload.mode: "hybrid"` (predeterminado): aplica en caliente cambios seguros, reinicia para los críticos
    - También se admiten `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="¿Cómo desactivo los eslóganes graciosos de la CLI?">
    Configura `cli.banner.taglineMode` en la configuración:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: oculta el texto del eslogan pero conserva la línea de título/versión del banner.
    - `default`: usa `All your chats, one OpenClaw.` siempre.
    - `random`: eslóganes rotativos divertidos/de temporada (comportamiento predeterminado).
    - Si no quieres ningún banner, configura la variable de entorno `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="¿Cómo habilito la búsqueda web (y la recuperación web)?">
    `web_fetch` funciona sin clave de API. `web_search` depende del
    proveedor seleccionado:

    - Los proveedores respaldados por API como Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity y Tavily requieren su configuración normal de clave de API.
    - Ollama Web Search no requiere clave, pero usa tu host Ollama configurado y requiere `ollama signin`.
    - DuckDuckGo no requiere clave, pero es una integración no oficial basada en HTML.
    - SearXNG no requiere clave/es autoalojado; configura `SEARXNG_BASE_URL` o `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Recomendado:** ejecuta `openclaw configure --section web` y elige un proveedor.
    Alternativas mediante variables de entorno:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` o `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, o `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` o `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // opcional; omitir para autodetección
            },
          },
        },
    }
    ```

    La configuración específica del proveedor para búsqueda web ahora vive en `plugins.entries.<plugin>.config.webSearch.*`.
    Las rutas heredadas del proveedor `tools.web.search.*` todavía se cargan temporalmente por compatibilidad, pero no deben usarse en configuraciones nuevas.
    La configuración fallback de recuperación web de Firecrawl vive en `plugins.entries.firecrawl.config.webFetch.*`.

    Notas:

    - Si usas listas de permitidos, añade `web_search`/`web_fetch`/`x_search` o `group:web`.
    - `web_fetch` está habilitado por defecto (salvo que se desactive explícitamente).
    - Si se omite `tools.web.fetch.provider`, OpenClaw autodetecta el primer proveedor fallback de recuperación listo a partir de las credenciales disponibles. Hoy el proveedor incluido es Firecrawl.
    - Los demonios leen variables de entorno desde `~/.openclaw/.env` (o el entorno del servicio).

    Documentación: [Web tools](/es/tools/web).

  </Accordion>

  <Accordion title="config.apply borró mi configuración. ¿Cómo recupero y evito esto?">
    `config.apply` reemplaza la **configuración completa**. Si envías un objeto parcial, todo
    lo demás se elimina.

    Recuperar:

    - Restaura desde una copia de seguridad (git o una copia de `~/.openclaw/openclaw.json`).
    - Si no tienes copia de seguridad, vuelve a ejecutar `openclaw doctor` y reconfigura canales/modelos.
    - Si esto fue inesperado, informa de un bug e incluye tu última configuración conocida o cualquier copia.
    - Un agente de programación local a menudo puede reconstruir una configuración funcional a partir de logs o historial.

    Evitarlo:

    - Usa `openclaw config set` para cambios pequeños.
    - Usa `openclaw configure` para ediciones interactivas.
    - Usa primero `config.schema.lookup` cuando no estés seguro de una ruta exacta o de la forma de un campo; devuelve un nodo de esquema superficial más resúmenes de los hijos inmediatos para profundizar.
    - Usa `config.patch` para ediciones RPC parciales; reserva `config.apply` solo para reemplazo completo de configuración.
    - Si estás usando la herramienta `gateway` solo para propietarios desde una ejecución de agente, seguirá rechazando escrituras en `tools.exec.ask` / `tools.exec.security` (incluidos los alias heredados `tools.bash.*` que se normalizan a las mismas rutas protegidas de exec).

    Documentación: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/es/gateway/doctor).

  </Accordion>

  <Accordion title="¿Cómo ejecuto un Gateway central con workers especializados en distintos dispositivos?">
    El patrón habitual es **un Gateway** (p. ej., Raspberry Pi) más **nodos** y **agentes**:

    - **Gateway (central):** es propietario de canales (Signal/WhatsApp), enrutamiento y sesiones.
    - **Nodos (dispositivos):** Macs/iOS/Android se conectan como periféricos y exponen herramientas locales (`system.run`, `canvas`, `camera`).
    - **Agentes (workers):** cerebros/espacios de trabajo separados para roles especiales (p. ej., “operaciones Hetzner”, “datos personales”).
    - **Subagentes:** generan trabajo en segundo plano desde un agente principal cuando quieres paralelismo.
    - **TUI:** conéctate al Gateway y cambia agentes/sesiones.

    Documentación: [Nodes](/es/nodes), [Remote access](/es/gateway/remote), [Multi-Agent Routing](/es/concepts/multi-agent), [Sub-agents](/es/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="¿Puede el navegador de OpenClaw ejecutarse en headless?">
    Sí. Es una opción de configuración:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    El valor predeterminado es `false` (con interfaz). Headless tiene más probabilidades de activar comprobaciones anti-bot en algunos sitios. Consulta [Browser](/es/tools/browser).

    Headless usa el **mismo motor Chromium** y funciona para la mayoría de la automatización (formularios, clics, scraping, inicios de sesión). Las diferencias principales:

    - No hay ventana visible del navegador (usa capturas de pantalla si necesitas elementos visuales).
    - Algunos sitios son más estrictos con la automatización en modo headless (CAPTCHA, anti-bot).
      Por ejemplo, X/Twitter suele bloquear sesiones headless.

  </Accordion>

  <Accordion title="¿Cómo uso Brave para controlar el navegador?">
    Configura `browser.executablePath` con tu binario de Brave (o cualquier navegador basado en Chromium) y reinicia Gateway.
    Consulta los ejemplos completos de configuración en [Browser](/es/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Gateways remotos y nodos

<AccordionGroup>
  <Accordion title="¿Cómo se propagan los comandos entre Telegram, el gateway y los nodos?">
    Los mensajes de Telegram los maneja el **gateway**. El gateway ejecuta el agente y
    solo entonces llama a nodos sobre el **WebSocket del Gateway** cuando se necesita una herramienta de nodo:

    Telegram → Gateway → Agente → `node.*` → Nodo → Gateway → Telegram

    Los nodos no ven el tráfico entrante del proveedor; solo reciben llamadas RPC de nodo.

  </Accordion>

  <Accordion title="¿Cómo puede mi agente acceder a mi ordenador si el Gateway está alojado remotamente?">
    Respuesta corta: **empareja tu ordenador como nodo**. Gateway se ejecuta en otro lugar, pero puede
    llamar a herramientas `node.*` (pantalla, cámara, sistema) en tu máquina local mediante el WebSocket del Gateway.

    Configuración típica:

    1. Ejecuta Gateway en el host siempre activo (VPS/servidor doméstico).
    2. Pon el host del Gateway + tu ordenador en la misma tailnet.
    3. Asegúrate de que el WS del Gateway sea accesible (bind tailnet o túnel SSH).
    4. Abre la app de macOS localmente y conéctate en modo **Remote over SSH** (o tailnet directo)
       para que pueda registrarse como nodo.
    5. Aprueba el nodo en Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    No hace falta un puente TCP aparte; los nodos se conectan mediante el WebSocket del Gateway.

    Recordatorio de seguridad: emparejar un nodo macOS permite `system.run` en esa máquina. Empareja
    solo dispositivos en los que confíes y revisa [Security](/es/gateway/security).

    Documentación: [Nodes](/es/nodes), [Gateway protocol](/es/gateway/protocol), [macOS remote mode](/es/platforms/mac/remote), [Security](/es/gateway/security).

  </Accordion>

  <Accordion title="Tailscale está conectado pero no recibo respuestas. ¿Y ahora qué?">
    Comprueba lo básico:

    - Gateway está en ejecución: `openclaw gateway status`
    - Estado de Gateway: `openclaw status`
    - Estado del canal: `openclaw channels status`

    Luego verifica autenticación y enrutamiento:

    - Si usas Tailscale Serve, asegúrate de que `gateway.auth.allowTailscale` esté configurado correctamente.
    - Si te conectas mediante túnel SSH, confirma que el túnel local esté activo y apunte al puerto correcto.
    - Confirma que tus listas de permitidos (DM o grupo) incluyan tu cuenta.

    Documentación: [Tailscale](/es/gateway/tailscale), [Remote access](/es/gateway/remote), [Channels](/es/channels).

  </Accordion>

  <Accordion title="¿Pueden hablar entre sí dos instancias de OpenClaw (local + VPS)?">
    Sí. No hay un puente “bot a bot” integrado, pero puedes conectarlo de varias
    maneras fiables:

    **Lo más sencillo:** usa un canal de chat normal al que ambos bots puedan acceder (Telegram/Slack/WhatsApp).
    Haz que el Bot A envíe un mensaje al Bot B, y luego deja que el Bot B responda como de costumbre.

    **Puente CLI (genérico):** ejecuta un script que llame al otro Gateway con
    `openclaw agent --message ... --deliver`, dirigido a un chat donde el otro bot
    escucha. Si uno de los bots está en un VPS remoto, apunta tu CLI a ese Gateway remoto
    mediante SSH/Tailscale (consulta [Remote access](/es/gateway/remote)).

    Patrón de ejemplo (ejecutar desde una máquina que pueda llegar al Gateway de destino):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Consejo: añade una barandilla para que los dos bots no entren en un bucle infinito (solo mención, listas
    de permitidos del canal o una regla de “no responder a mensajes de bots”).

    Documentación: [Remote access](/es/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/es/tools/agent-send).

  </Accordion>

  <Accordion title="¿Necesito VPS separados para varios agentes?">
    No. Un Gateway puede alojar varios agentes, cada uno con su propio espacio de trabajo, valores predeterminados de modelo
    y enrutamiento. Esa es la configuración normal y es mucho más barata y más simple que ejecutar
    un VPS por agente.

    Usa VPS separados solo cuando necesites aislamiento estricto (límites de seguridad) o
    configuraciones muy distintas que no quieras compartir. En caso contrario, mantén un solo Gateway y
    usa varios agentes o subagentes.

  </Accordion>

  <Accordion title="¿Tiene alguna ventaja usar un nodo en mi portátil personal en lugar de SSH desde un VPS?">
    Sí: los nodos son la forma de primera clase de llegar a tu portátil desde un Gateway remoto, y
    desbloquean más que acceso shell. Gateway se ejecuta en macOS/Linux (Windows mediante WSL2) y es
    ligero (un VPS pequeño o una máquina de clase Raspberry Pi sirven; 4 GB de RAM son más que suficientes), así que una
    configuración habitual es un host siempre activo más tu portátil como nodo.

    - **No se necesita SSH entrante.** Los nodos se conectan hacia fuera al WebSocket del Gateway y usan emparejamiento de dispositivos.
    - **Controles de ejecución más seguros.** `system.run` está restringido por listas de permitidos/aprobaciones del nodo en ese portátil.
    - **Más herramientas de dispositivo.** Los nodos exponen `canvas`, `camera` y `screen` además de `system.run`.
    - **Automatización local del navegador.** Mantén Gateway en un VPS, pero ejecuta Chrome localmente mediante un host de nodo en el portátil, o conéctate al Chrome local del host mediante Chrome MCP.

    SSH está bien para acceso shell puntual, pero los nodos son más simples para flujos de trabajo continuos del agente y
    automatización del dispositivo.

    Documentación: [Nodes](/es/nodes), [Nodes CLI](/cli/nodes), [Browser](/es/tools/browser).

  </Accordion>

  <Accordion title="¿Los nodos ejecutan un servicio gateway?">
    No. Solo debe ejecutarse **un gateway** por host salvo que intencionadamente ejecutes perfiles aislados (consulta [Multiple gateways](/es/gateway/multiple-gateways)). Los nodos son periféricos que se conectan
    al gateway (nodos iOS/Android, o “modo nodo” de macOS en la app de barra de menús). Para hosts de nodo headless
    y control por CLI, consulta [Node host CLI](/cli/node).

    Se requiere un reinicio completo para cambios en `gateway`, `discovery` y `canvasHost`.

  </Accordion>

  <Accordion title="¿Hay una forma API / RPC de aplicar configuración?">
    Sí.

    - `config.schema.lookup`: inspecciona un subárbol de configuración con su nodo de esquema superficial, pista de UI coincidente y resúmenes de hijos inmediatos antes de escribir
    - `config.get`: obtiene la instantánea actual + hash
    - `config.patch`: actualización parcial segura (preferida para la mayoría de las ediciones RPC)
    - `config.apply`: valida + reemplaza la configuración completa, luego reinicia
    - La herramienta de runtime `gateway`, solo para propietarios, sigue negándose a reescribir `tools.exec.ask` / `tools.exec.security`; los alias heredados `tools.bash.*` se normalizan a las mismas rutas protegidas de exec

  </Accordion>

  <Accordion title="Configuración mínima razonable para una primera instalación">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Esto configura tu espacio de trabajo y restringe quién puede activar el bot.

  </Accordion>

  <Accordion title="¿Cómo configuro Tailscale en un VPS y me conecto desde mi Mac?">
    Pasos mínimos:

    1. **Instalar + iniciar sesión en el VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Instalar + iniciar sesión en tu Mac**
       - Usa la app de Tailscale e inicia sesión en la misma tailnet.
    3. **Habilitar MagicDNS (recomendado)**
       - En la consola de administración de Tailscale, habilita MagicDNS para que el VPS tenga un nombre estable.
    4. **Usar el hostname de tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Si quieres la Control UI sin SSH, usa Tailscale Serve en el VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Esto mantiene el gateway vinculado a loopback y expone HTTPS mediante Tailscale. Consulta [Tailscale](/es/gateway/tailscale).

  </Accordion>

  <Accordion title="¿Cómo conecto un nodo Mac a un Gateway remoto (Tailscale Serve)?">
    Serve expone la **Control UI + WS del Gateway**. Los nodos se conectan mediante el mismo endpoint WS del Gateway.

    Configuración recomendada:

    1. **Asegúrate de que el VPS + Mac estén en la misma tailnet**.
    2. **Usa la app de macOS en modo Remote** (el objetivo SSH puede ser el hostname de tailnet).
       La app tunelizará el puerto del Gateway y se conectará como nodo.
    3. **Aprueba el nodo** en el gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Documentación: [Gateway protocol](/es/gateway/protocol), [Discovery](/es/gateway/discovery), [macOS remote mode](/es/platforms/mac/remote).

  </Accordion>

  <Accordion title="¿Debería instalar en un segundo portátil o simplemente añadir un nodo?">
    Si solo necesitas **herramientas locales** (pantalla/cámara/exec) en el segundo portátil, añádelo como
    **nodo**. Eso mantiene un solo Gateway y evita configuración duplicada. Las herramientas locales de nodo son
    actualmente solo para macOS, pero planeamos ampliarlas a otros SO.

    Instala un segundo Gateway solo cuando necesites **aislamiento estricto** o dos bots totalmente separados.

    Documentación: [Nodes](/es/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/es/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Variables de entorno y carga de .env

<AccordionGroup>
  <Accordion title="¿Cómo carga OpenClaw las variables de entorno?">
    OpenClaw lee las variables de entorno del proceso padre (shell, launchd/systemd, CI, etc.) y además carga:

    - `.env` desde el directorio de trabajo actual
    - un `.env` global de fallback desde `~/.openclaw/.env` (también conocido como `$OPENCLAW_STATE_DIR/.env`)

    Ninguno de los archivos `.env` sobrescribe variables de entorno existentes.

    También puedes definir variables de entorno inline en la configuración (se aplican solo si faltan en el entorno del proceso):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Consulta [/environment](/es/help/environment) para la precedencia completa y las fuentes.

  </Accordion>

  <Accordion title="Inicié Gateway mediante el servicio y mis variables de entorno desaparecieron. ¿Y ahora qué?">
    Dos soluciones comunes:

    1. Coloca las claves que faltan en `~/.openclaw/.env` para que se recojan incluso cuando el servicio no hereda el entorno de tu shell.
    2. Habilita la importación del shell (comodidad opt-in):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Esto ejecuta tu shell de inicio de sesión e importa solo las claves esperadas que falten (nunca sobrescribe). Equivalentes en variables de entorno:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Configuré COPILOT_GITHUB_TOKEN, pero models status muestra "Shell env: off." ¿Por qué?'>
    `openclaw models status` informa si la **importación del entorno del shell** está habilitada. “Shell env: off”
    **no** significa que falten tus variables de entorno; solo significa que OpenClaw no cargará
    tu shell de inicio de sesión automáticamente.

    Si Gateway se ejecuta como servicio (launchd/systemd), no heredará tu shell
    environment. Solución haciendo una de estas cosas:

    1. Pon el token en `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. O habilita la importación del shell (`env.shellEnv.enabled: true`).
    3. O añádelo al bloque `env` de tu configuración (se aplica solo si falta).

    Luego reinicia el gateway y vuelve a comprobar:

    ```bash
    openclaw models status
    ```

    Los tokens de Copilot se leen de `COPILOT_GITHUB_TOKEN` (también `GH_TOKEN` / `GITHUB_TOKEN`).
    Consulta [/concepts/model-providers](/es/concepts/model-providers) y [/environment](/es/help/environment).

  </Accordion>
</AccordionGroup>

## Sesiones y varios chats

<AccordionGroup>
  <Accordion title="¿Cómo inicio una conversación nueva?">
    Envía `/new` o `/reset` como mensaje independiente. Consulta [Session management](/es/concepts/session).
  </Accordion>

  <Accordion title="¿Las sesiones se reinician automáticamente si nunca envío /new?">
    Las sesiones pueden caducar después de `session.idleMinutes`, pero esto está **desactivado por defecto** (valor predeterminado **0**).
    Configúralo con un valor positivo para habilitar la caducidad por inactividad. Cuando está habilitado, el **siguiente**
    mensaje después del periodo de inactividad inicia un ID de sesión nuevo para esa clave de chat.
    Esto no elimina transcripciones; solo inicia una sesión nueva.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="¿Hay alguna forma de crear un equipo de instancias de OpenClaw (un CEO y muchos agentes)?">
    Sí, mediante **enrutamiento multiagente** y **subagentes**. Puedes crear un agente coordinador
    y varios agentes workers con sus propios espacios de trabajo y modelos.

    Dicho esto, es mejor verlo como un **experimento divertido**. Consume muchos tokens y a menudo
    es menos eficiente que usar un solo bot con sesiones separadas. El modelo típico que
    imaginamos es un bot con el que hablas, con distintas sesiones para trabajo en paralelo. Ese
    bot también puede generar subagentes cuando haga falta.

    Documentación: [Multi-agent routing](/es/concepts/multi-agent), [Sub-agents](/es/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="¿Por qué se truncó el contexto a mitad de la tarea? ¿Cómo lo evito?">
    El contexto de la sesión está limitado por la ventana del modelo. Chats largos, salidas grandes de herramientas o muchos
    archivos pueden activar compactación o truncado.

    Qué ayuda:

    - Pide al bot que resuma el estado actual y lo escriba en un archivo.
    - Usa `/compact` antes de tareas largas y `/new` al cambiar de tema.
    - Mantén el contexto importante en el espacio de trabajo y pide al bot que lo vuelva a leer.
    - Usa subagentes para trabajo largo o paralelo para que el chat principal siga siendo más pequeño.
    - Elige un modelo con una ventana de contexto mayor si esto ocurre con frecuencia.

  </Accordion>

  <Accordion title="¿Cómo reinicio completamente OpenClaw pero mantengo la instalación?">
    Usa el comando de reinicio:

    ```bash
    openclaw reset
    ```

    Reinicio completo no interactivo:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Luego vuelve a ejecutar la configuración:

    ```bash
    openclaw onboard --install-daemon
    ```

    Notas:

    - Onboarding también ofrece **Reset** si detecta una configuración existente. Consulta [Onboarding (CLI)](/es/start/wizard).
    - Si usaste perfiles (`--profile` / `OPENCLAW_PROFILE`), reinicia cada directorio de estado (los predeterminados son `~/.openclaw-<profile>`).
    - Reinicio dev: `openclaw gateway --dev --reset` (solo dev; borra configuración, credenciales, sesiones y espacio de trabajo dev).

  </Accordion>

  <Accordion title='Recibo errores de "context too large": ¿cómo reinicio o compacto?'>
    Usa una de estas opciones:

    - **Compactar** (mantiene la conversación pero resume los turnos anteriores):

      ```
      /compact
      ```

      o `/compact <instructions>` para guiar el resumen.

    - **Reiniciar** (ID de sesión nuevo para la misma clave de chat):

      ```
      /new
      /reset
      ```

    Si sigue ocurriendo:

    - Habilita o ajusta la **poda de sesión** (`agents.defaults.contextPruning`) para recortar la salida vieja de herramientas.
    - Usa un modelo con una ventana de contexto mayor.

    Documentación: [Compaction](/es/concepts/compaction), [Session pruning](/es/concepts/session-pruning), [Session management](/es/concepts/session).

  </Accordion>

  <Accordion title='¿Por qué veo "LLM request rejected: messages.content.tool_use.input field required"?'>
    Esto es un error de validación del proveedor: el modelo emitió un bloque `tool_use` sin el `input`
    requerido. Normalmente significa que el historial de la sesión está obsoleto o corrupto (a menudo tras hilos largos
    o un cambio de herramienta/esquema).

    Solución: inicia una sesión nueva con `/new` (mensaje independiente).

  </Accordion>

  <Accordion title="¿Por qué recibo mensajes de heartbeat cada 30 minutos?">
    Los heartbeat se ejecutan cada **30 m** por defecto (**1 h** al usar autenticación OAuth). Ajústalos o desactívalos:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // o "0m" para desactivar
          },
        },
      },
    }
    ```

    Si existe `HEARTBEAT.md` pero está prácticamente vacío (solo líneas en blanco y
    encabezados markdown como `# Heading`), OpenClaw omite la ejecución de heartbeat para ahorrar llamadas a la API.
    Si el archivo falta, heartbeat sigue ejecutándose y el modelo decide qué hacer.

    Los reemplazos por agente usan `agents.list[].heartbeat`. Documentación: [Heartbeat](/es/gateway/heartbeat).

  </Accordion>

  <Accordion title='¿Necesito añadir una "cuenta bot" a un grupo de WhatsApp?'>
    No. OpenClaw se ejecuta con **tu propia cuenta**, así que si estás en el grupo, OpenClaw puede verlo.
    Por defecto, las respuestas en grupos están bloqueadas hasta que permites remitentes (`groupPolicy: "allowlist"`).

    Si quieres que solo **tú** puedas activar respuestas en grupos:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="¿Cómo obtengo el JID de un grupo de WhatsApp?">
    Opción 1 (más rápida): sigue los logs y envía un mensaje de prueba al grupo:

    ```bash
    openclaw logs --follow --json
    ```

    Busca `chatId` (o `from`) terminado en `@g.us`, como:
    `1234567890-1234567890@g.us`.

    Opción 2 (si ya está configurado/en allowlist): lista grupos desde la configuración:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Documentación: [WhatsApp](/es/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="¿Por qué OpenClaw no responde en un grupo?">
    Dos causas comunes:

    - El control por mención está activado (predeterminado). Debes mencionar con @ al bot (o coincidir con `mentionPatterns`).
    - Configuraste `channels.whatsapp.groups` sin `"*"` y el grupo no está en la lista de permitidos.

    Consulta [Groups](/es/channels/groups) y [Group messages](/es/channels/group-messages).

  </Accordion>

  <Accordion title="¿Los grupos/hilos comparten contexto con los DM?">
    Los chats directos se reducen a la sesión principal por defecto. Los grupos/canales tienen sus propias claves de sesión, y los temas de Telegram / hilos de Discord son sesiones independientes. Consulta [Groups](/es/channels/groups) y [Group messages](/es/channels/group-messages).
  </Accordion>

  <Accordion title="¿Cuántos espacios de trabajo y agentes puedo crear?">
    No hay límites estrictos. Decenas (incluso cientos) están bien, pero vigila:

    - **Crecimiento del disco:** las sesiones + transcripciones viven bajo `~/.openclaw/agents/<agentId>/sessions/`.
    - **Coste de tokens:** más agentes significa más uso concurrente del modelo.
    - **Sobrecarga operativa:** perfiles de autenticación, espacios de trabajo y enrutamiento de canales por agente.

    Consejos:

    - Mantén un espacio de trabajo **activo** por agente (`agents.defaults.workspace`).
    - Poda sesiones antiguas (elimina JSONL o entradas de almacén) si crece el disco.
    - Usa `openclaw doctor` para detectar espacios de trabajo extraviados y desajustes de perfiles.

  </Accordion>

  <Accordion title="¿Puedo ejecutar varios bots o chats al mismo tiempo (Slack), y cómo debería configurarlo?">
    Sí. Usa **Multi-Agent Routing** para ejecutar varios agentes aislados y enrutar mensajes entrantes por
    canal/cuenta/peer. Slack se admite como canal y puede vincularse a agentes específicos.

    El acceso al navegador es potente, pero no es “hacer cualquier cosa que pueda hacer un humano”: anti-bot, CAPTCHA y MFA
    aún pueden bloquear la automatización. Para el control de navegador más fiable, usa Chrome MCP local en el host,
    o usa CDP en la máquina que realmente ejecuta el navegador.

    Configuración de buenas prácticas:

    - Host Gateway siempre activo (VPS/Mac mini).
    - Un agente por rol (vínculos).
    - Canal(es) de Slack vinculados a esos agentes.
    - Navegador local mediante Chrome MCP o un nodo cuando sea necesario.

    Documentación: [Multi-Agent Routing](/es/concepts/multi-agent), [Slack](/es/channels/slack),
    [Browser](/es/tools/browser), [Nodes](/es/nodes).

  </Accordion>
</AccordionGroup>

## Modelos: valores predeterminados, selección, alias, cambio

<AccordionGroup>
  <Accordion title='¿Qué es el "modelo predeterminado"?'>
    El modelo predeterminado de OpenClaw es lo que configures como:

    ```
    agents.defaults.model.primary
    ```

    Los modelos se referencian como `provider/model` (ejemplo: `openai/gpt-5.4`). Si omites el proveedor, OpenClaw primero intenta un alias, luego una coincidencia única de proveedor configurado para ese id de modelo exacto, y solo después recurre al proveedor predeterminado configurado como una ruta heredada de compatibilidad ya obsoleta. Si ese proveedor ya no expone el modelo predeterminado configurado, OpenClaw recurre al primer proveedor/modelo configurado en lugar de mostrar un valor predeterminado obsoleto de un proveedor eliminado. Aun así, deberías configurar explícitamente `provider/model`.

  </Accordion>

  <Accordion title="¿Qué modelo recomiendan?">
    **Predeterminado recomendado:** usa el modelo más potente y de última generación disponible en tu pila de proveedores.
    **Para agentes con herramientas habilitadas o con entradas no confiables:** prioriza la calidad del modelo sobre el coste.
    **Para chat rutinario/de bajo riesgo:** usa modelos fallback más baratos y enruta por rol de agente.

    MiniMax tiene su propia documentación: [MiniMax](/es/providers/minimax) y
    [Local models](/es/gateway/local-models).

    Regla práctica: usa el **mejor modelo que puedas permitirte** para trabajo de alto riesgo, y un modelo más barato
    para chat rutinario o resúmenes. Puedes enrutar modelos por agente y usar subagentes para
    paralelizar tareas largas (cada subagente consume tokens). Consulta [Models](/es/concepts/models) y
    [Sub-agents](/es/tools/subagents).

    Advertencia importante: los modelos más débiles o demasiado cuantizados son más vulnerables a la inyección de prompts y al comportamiento inseguro. Consulta [Security](/es/gateway/security).

    Más contexto: [Models](/es/concepts/models).

  </Accordion>

  <Accordion title="¿Cómo cambio de modelo sin borrar mi configuración?">
    Usa **comandos de modelo** o edita solo los campos de **modelo**. Evita reemplazos completos de configuración.

    Opciones seguras:

    - `/model` en el chat (rápido, por sesión)
    - `openclaw models set ...` (actualiza solo la configuración del modelo)
    - `openclaw configure --section model` (interactivo)
    - edita `agents.defaults.model` en `~/.openclaw/openclaw.json`

    Evita `config.apply` con un objeto parcial salvo que realmente quieras reemplazar toda la configuración.
    Para ediciones RPC, inspecciona primero con `config.schema.lookup` y prefiere `config.patch`. La carga de lookup te da la ruta normalizada, documentación/restricciones del esquema superficial y resúmenes de los hijos inmediatos
    para actualizaciones parciales.
    Si sobrescribiste la configuración, restaura desde una copia de seguridad o vuelve a ejecutar `openclaw doctor` para reparar.

    Documentación: [Models](/es/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/es/gateway/doctor).

  </Accordion>

  <Accordion title="¿Puedo usar modelos autoalojados (llama.cpp, vLLM, Ollama)?">
    Sí. Ollama es la ruta más fácil para modelos locales.

    Configuración más rápida:

    1. Instala Ollama desde `https://ollama.com/download`
    2. Descarga un modelo local como `ollama pull glm-4.7-flash`
    3. Si quieres también modelos en la nube, ejecuta `ollama signin`
    4. Ejecuta `openclaw onboard` y elige `Ollama`
    5. Elige `Local` o `Cloud + Local`

    Notas:

    - `Cloud + Local` te da modelos en la nube más tus modelos locales de Ollama
    - los modelos en la nube como `kimi-k2.5:cloud` no necesitan descarga local
    - para cambio manual, usa `openclaw models list` y `openclaw models set ollama/<model>`

    Nota de seguridad: los modelos más pequeños o muy cuantizados son más vulnerables a la inyección de prompts. Recomendamos firmemente **modelos grandes** para cualquier bot que pueda usar herramientas.
    Si aun así quieres modelos pequeños, habilita sandboxing y listas estrictas de herramientas permitidas.

    Documentación: [Ollama](/es/providers/ollama), [Local models](/es/gateway/local-models),
    [Model providers](/es/concepts/model-providers), [Security](/es/gateway/security),
    [Sandboxing](/es/gateway/sandboxing).

  </Accordion>

  <Accordion title="¿Qué usan OpenClaw, Flawd y Krill para modelos?">
    - Estas implementaciones pueden diferir y cambiar con el tiempo; no hay una recomendación fija de proveedor.
    - Comprueba la configuración actual de runtime en cada gateway con `openclaw models status`.
    - Para agentes sensibles a la seguridad/con herramientas habilitadas, usa el modelo más potente y de última generación disponible.
  </Accordion>

  <Accordion title="¿Cómo cambio modelos sobre la marcha (sin reiniciar)?">
    Usa el comando `/model` como mensaje independiente:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Estos son los alias integrados. Se pueden añadir alias personalizados mediante `agents.defaults.models`.

    Puedes listar los modelos disponibles con `/model`, `/model list` o `/model status`.

    `/model` (y `/model list`) muestra un selector compacto y numerado. Selecciona por número:

    ```
    /model 3
    ```

    También puedes forzar un perfil de autenticación específico para el proveedor (por sesión):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Consejo: `/model status` muestra qué agente está activo, qué archivo `auth-profiles.json` se está usando y qué perfil de autenticación se intentará a continuación.
    También muestra el endpoint del proveedor configurado (`baseUrl`) y el modo API (`api`) cuando están disponibles.

    **¿Cómo quito la fijación de un perfil que configuré con @profile?**

    Vuelve a ejecutar `/model` **sin** el sufijo `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Si quieres volver al valor predeterminado, selecciónalo desde `/model` (o envía `/model <default provider/model>`).
    Usa `/model status` para confirmar qué perfil de autenticación está activo.

  </Accordion>

  <Accordion title="¿Puedo usar GPT 5.2 para tareas diarias y Codex 5.3 para programar?">
    Sí. Configura uno como predeterminado y cambia según lo necesites:

    - **Cambio rápido (por sesión):** `/model gpt-5.4` para tareas diarias, `/model openai-codex/gpt-5.4` para programar con Codex OAuth.
    - **Predeterminado + cambio:** configura `agents.defaults.model.primary` en `openai/gpt-5.4`, luego cambia a `openai-codex/gpt-5.4` al programar (o al revés).
    - **Subagentes:** enruta las tareas de programación a subagentes con un modelo predeterminado diferente.

    Consulta [Models](/es/concepts/models) y [Slash commands](/es/tools/slash-commands).

  </Accordion>

  <Accordion title="¿Cómo configuro el modo rápido para GPT 5.4?">
    Usa un cambio por sesión o un valor predeterminado de configuración:

    - **Por sesión:** envía `/fast on` mientras la sesión usa `openai/gpt-5.4` o `openai-codex/gpt-5.4`.
    - **Predeterminado por modelo:** configura `agents.defaults.models["openai/gpt-5.4"].params.fastMode` en `true`.
    - **También para Codex OAuth:** si también usas `openai-codex/gpt-5.4`, configura el mismo flag allí.

    Ejemplo:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    Para OpenAI, el modo rápido se asigna a `service_tier = "priority"` en solicitudes nativas Responses compatibles. Los reemplazos de sesión `/fast` prevalecen sobre los valores predeterminados de configuración.

    Consulta [Thinking and fast mode](/es/tools/thinking) y [OpenAI fast mode](/es/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='¿Por qué veo "Model ... is not allowed" y luego no hay respuesta?'>
    Si `agents.defaults.models` está configurado, se convierte en la **lista de permitidos** para `/model` y cualquier
    reemplazo de sesión. Elegir un modelo que no esté en esa lista devuelve:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Ese error se devuelve **en lugar** de una respuesta normal. Solución: añade el modelo a
    `agents.defaults.models`, elimina la lista de permitidos o elige un modelo de `/model list`.

  </Accordion>

  <Accordion title='¿Por qué veo "Unknown model: minimax/MiniMax-M2.7"?'>
    Esto significa que el **proveedor no está configurado** (no se encontró ninguna configuración del proveedor MiniMax ni
    ningún perfil de autenticación), por lo que el modelo no puede resolverse.

    Lista de comprobación de solución:

    1. Actualiza a una versión actual de OpenClaw (o ejecuta desde el código fuente `main`), luego reinicia el gateway.
    2. Asegúrate de que MiniMax esté configurado (asistente o JSON), o de que exista autenticación
       de MiniMax en el entorno/perfiles de autenticación para que se pueda inyectar el
       proveedor coincidente (`MINIMAX_API_KEY` para `minimax`, `MINIMAX_OAUTH_TOKEN` o MiniMax
       OAuth almacenado para `minimax-portal`).
    3. Usa el id de modelo exacto (sensible a mayúsculas/minúsculas) para tu ruta de autenticación:
       `minimax/MiniMax-M2.7` o `minimax/MiniMax-M2.7-highspeed` para configuración
       con clave de API, o `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` para configuración OAuth.
    4. Ejecuta:

       ```bash
       openclaw models list
       ```

       y elige de la lista (o `/model list` en el chat).

    Consulta [MiniMax](/es/providers/minimax) y [Models](/es/concepts/models).

  </Accordion>

  <Accordion title="¿Puedo usar MiniMax como predeterminado y OpenAI para tareas complejas?">
    Sí. Usa **MiniMax como predeterminado** y cambia de modelo **por sesión** cuando sea necesario.
    Los respaldos son para **errores**, no para “tareas difíciles”, así que usa `/model` o un agente aparte.

    **Opción A: cambiar por sesión**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Luego:

    ```
    /model gpt
    ```

    **Opción B: agentes separados**

    - Predeterminado del agente A: MiniMax
    - Predeterminado del agente B: OpenAI
    - Enruta por agente o usa `/agent` para cambiar

    Documentación: [Models](/es/concepts/models), [Multi-Agent Routing](/es/concepts/multi-agent), [MiniMax](/es/providers/minimax), [OpenAI](/es/providers/openai).

  </Accordion>

  <Accordion title="¿opus / sonnet / gpt son atajos integrados?">
    Sí. OpenClaw incluye algunos atajos predeterminados (solo se aplican cuando el modelo existe en `agents.defaults.models`):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Si configuras tu propio alias con el mismo nombre, prevalece tu valor.

  </Accordion>

  <Accordion title="¿Cómo defino/reemplazo atajos (alias) de modelos?">
    Los alias vienen de `agents.defaults.models.<modelId>.alias`. Ejemplo:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Entonces `/model sonnet` (o `/<alias>` cuando sea compatible) se resuelve a ese ID de modelo.

  </Accordion>

  <Accordion title="¿Cómo añado modelos de otros proveedores como OpenRouter o Z.AI?">
    OpenRouter (pago por token; muchos modelos):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (modelos GLM):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    Si haces referencia a un proveedor/modelo pero falta la clave requerida del proveedor, obtendrás un error de autenticación en runtime (por ejemplo `No API key found for provider "zai"`).

    **No API key found for provider después de añadir un agente nuevo**

    Normalmente esto significa que el **agente nuevo** tiene un almacén de autenticación vacío. La autenticación es por agente y
    se almacena en:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    Opciones de solución:

    - Ejecuta `openclaw agents add <id>` y configura la autenticación durante el asistente.
    - O copia `auth-profiles.json` desde el `agentDir` del agente principal al `agentDir` del agente nuevo.

    **No** reutilices `agentDir` entre agentes; causa colisiones de autenticación/sesión.

  </Accordion>
</AccordionGroup>

## Failover de modelos y "All models failed"

<AccordionGroup>
  <Accordion title="¿Cómo funciona el failover?">
    El failover ocurre en dos etapas:

    1. **Rotación del perfil de autenticación** dentro del mismo proveedor.
    2. **Fallback del modelo** al siguiente modelo en `agents.defaults.model.fallbacks`.

    Se aplican enfriamientos a los perfiles que fallan (retroceso exponencial), para que OpenClaw pueda seguir respondiendo incluso cuando un proveedor está limitado por tasa o falla temporalmente.

    El bucket de límite de tasa incluye más que simples respuestas `429`. OpenClaw
    también trata mensajes como `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted`, y límites
    periódicos de ventana de uso (`weekly/monthly limit reached`) como
    límites de tasa dignos de failover.

    Algunas respuestas que parecen de facturación no son `402`, y algunas respuestas HTTP `402`
    también permanecen en ese bucket transitorio. Si un proveedor devuelve
    texto explícito de facturación en `401` o `403`, OpenClaw puede seguir manteniéndolo en
    la vía de facturación, pero los comparadores de texto específicos del proveedor siguen limitados al
    proveedor que los posee (por ejemplo, OpenRouter `Key limit exceeded`). Si en cambio un mensaje `402`
    parece una ventana de uso reintentable o un límite de gasto de organización/espacio de trabajo
    (`daily limit reached, resets tomorrow`,
    `organization spending limit exceeded`), OpenClaw lo trata como
    `rate_limit`, no como una desactivación larga por facturación.

    Los errores de desbordamiento de contexto son diferentes: firmas como
    `request_too_large`, `input exceeds the maximum number of tokens`,
    `input token count exceeds the maximum number of input tokens`,
    `input is too long for the model`, o `ollama error: context length
    exceeded` permanecen en la ruta de compactación/reintento en lugar de avanzar al
    fallback de modelo.

    El texto genérico de error del servidor es intencionadamente más estrecho que “cualquier cosa con
    unknown/error dentro”. OpenClaw sí trata formas transitorias con alcance de proveedor
    como el bare `An unknown error occurred` de Anthropic, el bare de OpenRouter
    `Provider returned error`, errores de stop-reason como `Unhandled stop reason:
    error`, cargas JSON `api_error` con texto transitorio del servidor
    (`internal server error`, `unknown error, 520`, `upstream error`, `backend
    error`), y errores de proveedor ocupado como `ModelNotReadyException` como
    señales de timeout/sobrecarga dignas de failover cuando el contexto del proveedor
    coincide.
    El texto fallback interno genérico como `LLM request failed with an unknown
    error.` sigue siendo conservador y no activa por sí solo el fallback del modelo.

  </Accordion>

  <Accordion title='¿Qué significa "No credentials found for profile anthropic:default"?'>
    Significa que el sistema intentó usar el ID de perfil de autenticación `anthropic:default`, pero no pudo encontrar credenciales para él en el almacén de autenticación esperado.

    **Lista de comprobación de solución:**

    - **Confirma dónde viven los perfiles de autenticación** (rutas nuevas frente a heredadas)
      - Actual: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - Heredada: `~/.openclaw/agent/*` (migrada por `openclaw doctor`)
    - **Confirma que tu variable de entorno está cargada por Gateway**
      - Si configuraste `ANTHROPIC_API_KEY` en tu shell pero ejecutas Gateway mediante systemd/launchd, puede que no la herede. Ponla en `~/.openclaw/.env` o habilita `env.shellEnv`.
    - **Asegúrate de que estás editando el agente correcto**
      - En configuraciones multiagente puede haber varios archivos `auth-profiles.json`.
    - **Haz una comprobación básica del estado de modelo/autenticación**
      - Usa `openclaw models status` para ver los modelos configurados y si los proveedores están autenticados.

    **Lista de comprobación de solución para "No credentials found for profile anthropic"**

    Esto significa que la ejecución está fijada a un perfil de autenticación de Anthropic, pero Gateway
    no puede encontrarlo en su almacén de autenticación.

    - **Usa Claude CLI**
      - Ejecuta `openclaw models auth login --provider anthropic --method cli --set-default` en el host del gateway.
    - **Si quieres usar una clave de API en su lugar**
      - Pon `ANTHROPIC_API_KEY` en `~/.openclaw/.env` en el **host del gateway**.
      - Borra cualquier orden fijado que fuerce un perfil que falta:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **Confirma que estás ejecutando los comandos en el host del gateway**
      - En modo remoto, los perfiles de autenticación viven en la máquina gateway, no en tu portátil.

  </Accordion>

  <Accordion title="¿Por qué también intentó Google Gemini y falló?">
    Si tu configuración de modelos incluye Google Gemini como fallback (o cambiaste a un atajo de Gemini), OpenClaw lo intentará durante el fallback del modelo. Si no has configurado credenciales de Google, verás `No API key found for provider "google"`.

    Solución: proporciona autenticación de Google o elimina/evita modelos de Google en `agents.defaults.model.fallbacks` / alias para que el fallback no vaya por ahí.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    Causa: el historial de la sesión contiene **bloques de thinking sin firmas** (a menudo de
    un stream abortado/parcial). Google Antigravity exige firmas para los bloques de thinking.

    Solución: OpenClaw ahora elimina los bloques de thinking sin firma para Google Antigravity Claude. Si sigue apareciendo, inicia una **sesión nueva** o configura `/thinking off` para ese agente.

  </Accordion>
</