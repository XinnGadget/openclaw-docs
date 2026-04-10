---
read_when:
    - Agregar automatización del navegador controlada por el agente
    - Depurar por qué openclaw está interfiriendo con tu propio Chrome
    - Implementar la configuración del navegador + el ciclo de vida en la app de macOS
summary: Servicio de control del navegador integrado + comandos de acción
title: Navegador (gestionado por OpenClaw)
x-i18n:
    generated_at: "2026-04-10T05:12:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd3424f62178bbf25923b8bc8e4d9f70e330f35428d01fe153574e5fa45d7604
    source_path: tools/browser.md
    workflow: 15
---

# Navegador (gestionado por openclaw)

OpenClaw puede ejecutar un **perfil dedicado de Chrome/Brave/Edge/Chromium** que el agente controla.
Está aislado de tu navegador personal y se gestiona mediante un pequeño
servicio de control local dentro del Gateway (solo loopback).

Vista para principiantes:

- Piensa en él como un **navegador separado, solo para el agente**.
- El perfil `openclaw` **no** toca tu perfil personal del navegador.
- El agente puede **abrir pestañas, leer páginas, hacer clic y escribir** en un entorno seguro.
- El perfil integrado `user` se conecta a tu sesión real de Chrome con inicio de sesión mediante Chrome MCP.

## Lo que obtienes

- Un perfil de navegador separado llamado **openclaw** (acento naranja de forma predeterminada).
- Control determinista de pestañas (listar/abrir/enfocar/cerrar).
- Acciones del agente (clic/escritura/arrastrar/seleccionar), instantáneas, capturas de pantalla y PDF.
- Compatibilidad opcional con varios perfiles (`openclaw`, `work`, `remote`, ...).

Este navegador **no** es tu navegador de uso diario. Es una superficie segura y aislada para
la automatización y verificación del agente.

## Inicio rápido

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Si aparece “Browser disabled”, actívalo en la configuración (consulta más abajo) y reinicia el
Gateway.

Si `openclaw browser` no aparece en absoluto, o el agente dice que la herramienta de navegador
no está disponible, ve a [Falta el comando o la herramienta del navegador](/es/tools/browser#missing-browser-command-or-tool).

## Control del plugin

La herramienta `browser` predeterminada ahora es un plugin incluido que se envía habilitado de
forma predeterminada. Eso significa que puedes desactivarlo o reemplazarlo sin eliminar el resto del
sistema de plugins de OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Desactiva el plugin incluido antes de instalar otro plugin que proporcione el
mismo nombre de herramienta `browser`. La experiencia predeterminada del navegador necesita ambos:

- `plugins.entries.browser.enabled` no deshabilitado
- `browser.enabled=true`

Si desactivas solo el plugin, el CLI de navegador incluido (`openclaw browser`),
el método del gateway (`browser.request`), la herramienta del agente y el servicio predeterminado de control del navegador
desaparecen juntos. Tu configuración `browser.*` permanece intacta para que un
plugin de reemplazo la reutilice.

El plugin de navegador incluido también es ahora el propietario de la implementación del tiempo de ejecución del navegador.
El núcleo conserva solo los helpers compartidos del Plugin SDK más las reexportaciones de compatibilidad para
rutas de importación internas antiguas. En la práctica, eliminar o reemplazar el paquete del plugin de navegador
elimina el conjunto de funciones del navegador en lugar de dejar detrás un segundo tiempo de ejecución
propiedad del núcleo.

Los cambios de configuración del navegador siguen requiriendo un reinicio del Gateway para que el plugin incluido
pueda volver a registrar su servicio de navegador con la nueva configuración.

## Falta el comando o la herramienta del navegador

Si `openclaw browser` de repente pasa a ser un comando desconocido después de una actualización, o
el agente informa que falta la herramienta de navegador, la causa más común es una
lista restrictiva `plugins.allow` que no incluye `browser`.

Ejemplo de configuración incorrecta:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Corrígelo agregando `browser` a la lista de permitidos de plugins:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Notas importantes:

- `browser.enabled=true` por sí solo no es suficiente cuando `plugins.allow` está configurado.
- `plugins.entries.browser.enabled=true` por sí solo tampoco es suficiente cuando `plugins.allow` está configurado.
- `tools.alsoAllow: ["browser"]` **no** carga el plugin de navegador incluido. Solo ajusta la política de herramientas después de que el plugin ya esté cargado.
- Si no necesitas una lista restrictiva de plugins permitidos, quitar `plugins.allow` también restaura el comportamiento predeterminado del navegador incluido.

Síntomas típicos:

- `openclaw browser` es un comando desconocido.
- Falta `browser.request`.
- El agente informa que la herramienta de navegador no está disponible o falta.

## Perfiles: `openclaw` frente a `user`

- `openclaw`: navegador gestionado y aislado (no requiere extensión).
- `user`: perfil integrado de conexión Chrome MCP para tu **sesión real de Chrome con inicio de sesión**.

Para llamadas a la herramienta de navegador del agente:

- Predeterminado: usar el navegador aislado `openclaw`.
- Preferir `profile="user"` cuando importan las sesiones existentes con inicio de sesión y el usuario
  está en la computadora para hacer clic o aprobar cualquier solicitud de conexión.
- `profile` es la anulación explícita cuando quieres un modo de navegador específico.

Establece `browser.defaultProfile: "openclaw"` si quieres el modo gestionado como predeterminado.

## Configuración

La configuración del navegador se encuentra en `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // predeterminado: true
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: true, // modo predeterminado de red de confianza
      // allowPrivateNetwork: true, // alias heredado
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // anulación heredada de perfil único
    remoteCdpTimeoutMs: 1500, // tiempo de espera HTTP de CDP remoto (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // tiempo de espera del protocolo de enlace WebSocket de CDP remoto (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Notas:

- El servicio de control del navegador se enlaza a loopback en un puerto derivado de `gateway.port`
  (predeterminado: `18791`, que es gateway + 2).
- Si anulas el puerto del Gateway (`gateway.port` o `OPENCLAW_GATEWAY_PORT`),
  los puertos derivados del navegador se desplazan para permanecer en la misma “familia”.
- `cdpUrl` usa de forma predeterminada el puerto CDP local gestionado cuando no está configurado.
- `remoteCdpTimeoutMs` se aplica a las comprobaciones de accesibilidad de CDP remoto (no loopback).
- `remoteCdpHandshakeTimeoutMs` se aplica a las comprobaciones de accesibilidad del WebSocket de CDP remoto.
- La navegación/apertura de pestañas del navegador está protegida contra SSRF antes de la navegación y se vuelve a verificar en la medida de lo posible en la URL final `http(s)` después de la navegación.
- En el modo SSRF estricto, también se comprueban el descubrimiento y las sondas del endpoint CDP remoto (`cdpUrl`, incluidas las búsquedas de `/json/version`).
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` usa `true` de forma predeterminada (modelo de red de confianza). Establécelo en `false` para navegación estricta solo pública.
- `browser.ssrfPolicy.allowPrivateNetwork` sigue siendo compatible como alias heredado por compatibilidad.
- `attachOnly: true` significa “nunca iniciar un navegador local; solo conectarse si ya está en ejecución”.
- `color` + `color` por perfil tiñen la interfaz del navegador para que puedas ver qué perfil está activo.
- El perfil predeterminado es `openclaw` (navegador independiente gestionado por OpenClaw). Usa `defaultProfile: "user"` para optar por el navegador del usuario con inicio de sesión.
- Orden de detección automática: navegador predeterminado del sistema si está basado en Chromium; en caso contrario Chrome → Brave → Edge → Chromium → Chrome Canary.
- Los perfiles `openclaw` locales asignan automáticamente `cdpPort`/`cdpUrl`; configúralos solo para CDP remoto.
- `driver: "existing-session"` usa Chrome DevTools MCP en lugar de CDP sin procesar. No
  configures `cdpUrl` para ese controlador.
- Configura `browser.profiles.<name>.userDataDir` cuando un perfil existing-session
  deba conectarse a un perfil de usuario Chromium no predeterminado como Brave o Edge.

## Usar Brave (u otro navegador basado en Chromium)

Si tu navegador **predeterminado del sistema** está basado en Chromium (Chrome/Brave/Edge/etc.),
OpenClaw lo usa automáticamente. Configura `browser.executablePath` para anular la
detección automática:

Ejemplo de CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Control local frente a remoto

- **Control local (predeterminado):** el Gateway inicia el servicio de control de loopback y puede iniciar un navegador local.
- **Control remoto (host de nodo):** ejecuta un host de nodo en la máquina que tiene el navegador; el Gateway redirige las acciones del navegador a él.
- **CDP remoto:** configura `browser.profiles.<name>.cdpUrl` (o `browser.cdpUrl`) para
  conectarte a un navegador remoto basado en Chromium. En este caso, OpenClaw no iniciará un navegador local.

El comportamiento de detención varía según el modo del perfil:

- perfiles locales gestionados: `openclaw browser stop` detiene el proceso del navegador que
  OpenClaw inició
- perfiles de solo conexión y CDP remoto: `openclaw browser stop` cierra la sesión de control activa
  y libera las anulaciones de emulación de Playwright/CDP (viewport,
  combinación de colores, configuración regional, zona horaria, modo sin conexión y estado similar), aunque
  OpenClaw no haya iniciado ningún proceso del navegador

Las URL de CDP remoto pueden incluir autenticación:

- Tokens de consulta (por ejemplo, `https://provider.example?token=<token>`)
- Autenticación HTTP Basic (por ejemplo, `https://user:pass@provider.example`)

OpenClaw conserva la autenticación al llamar a los endpoints `/json/*` y al conectarse
al WebSocket de CDP. Prefiere variables de entorno o gestores de secretos para los
tokens en lugar de confirmarlos en archivos de configuración.

## Proxy de navegador del nodo (predeterminado sin configuración)

Si ejecutas un **host de nodo** en la máquina que tiene tu navegador, OpenClaw puede
redirigir automáticamente las llamadas de la herramienta de navegador a ese nodo sin ninguna configuración adicional del navegador.
Esta es la ruta predeterminada para gateways remotos.

Notas:

- El host de nodo expone su servidor local de control del navegador mediante un **comando proxy**.
- Los perfiles provienen de la propia configuración `browser.profiles` del nodo (igual que en local).
- `nodeHost.browserProxy.allowProfiles` es opcional. Déjalo vacío para el comportamiento heredado/predeterminado: todos los perfiles configurados siguen siendo accesibles a través del proxy, incluidas las rutas de creación/eliminación de perfiles.
- Si configuras `nodeHost.browserProxy.allowProfiles`, OpenClaw lo trata como un límite de privilegio mínimo: solo se pueden dirigir los perfiles permitidos, y las rutas persistentes de creación/eliminación de perfiles se bloquean en la superficie del proxy.
- Desactívalo si no lo quieres:
  - En el nodo: `nodeHost.browserProxy.enabled=false`
  - En el gateway: `gateway.nodes.browser.mode="off"`

## Browserless (CDP remoto alojado)

[Browserless](https://browserless.io) es un servicio Chromium alojado que expone
URL de conexión CDP mediante HTTPS y WebSocket. OpenClaw puede usar cualquiera de las dos formas, pero
para un perfil de navegador remoto la opción más sencilla es la URL WebSocket directa
de la documentación de conexión de Browserless.

Ejemplo:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Notas:

- Reemplaza `<BROWSERLESS_API_KEY>` por tu token real de Browserless.
- Elige el endpoint regional que coincida con tu cuenta de Browserless (consulta su documentación).
- Si Browserless te proporciona una URL base HTTPS, puedes convertirla a
  `wss://` para una conexión CDP directa o conservar la URL HTTPS y dejar que OpenClaw
  descubra `/json/version`.

## Proveedores CDP WebSocket directos

Algunos servicios de navegador alojados exponen un endpoint **WebSocket directo** en lugar de
la detección CDP estándar basada en HTTP (`/json/version`). OpenClaw es compatible con ambos:

- **Endpoints HTTP(S)** — OpenClaw llama a `/json/version` para descubrir la
  URL del depurador WebSocket y luego se conecta.
- **Endpoints WebSocket** (`ws://` / `wss://`) — OpenClaw se conecta directamente,
  omitiendo `/json/version`. Úsalo para servicios como
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com), o cualquier proveedor que te dé una
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) es una plataforma en la nube para ejecutar
navegadores headless con resolución de CAPTCHA integrada, modo sigiloso y proxies
residenciales.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Notas:

- [Regístrate](https://www.browserbase.com/sign-up) y copia tu **API Key**
  desde el [panel de Overview](https://www.browserbase.com/overview).
- Reemplaza `<BROWSERBASE_API_KEY>` con tu clave API real de Browserbase.
- Browserbase crea automáticamente una sesión del navegador al conectarse por WebSocket, por lo que no
  se necesita ningún paso manual de creación de sesión.
- El nivel gratuito permite una sesión simultánea y una hora de navegador al mes.
  Consulta [pricing](https://www.browserbase.com/pricing) para los límites de los planes de pago.
- Consulta la [documentación de Browserbase](https://docs.browserbase.com) para la referencia completa de la API,
  las guías del SDK y los ejemplos de integración.

## Seguridad

Ideas clave:

- El control del navegador es solo por loopback; el acceso fluye a través de la autenticación del Gateway o del emparejamiento de nodos.
- La API HTTP independiente del navegador en loopback usa **solo autenticación con secreto compartido**:
  autenticación Bearer con token del gateway, `x-openclaw-password`, o autenticación HTTP Basic con la
  contraseña del gateway configurada.
- Los encabezados de identidad de Tailscale Serve y `gateway.auth.mode: "trusted-proxy"` **no**
  autentican esta API independiente del navegador en loopback.
- Si el control del navegador está habilitado y no hay autenticación con secreto compartido configurada, OpenClaw
  genera automáticamente `gateway.auth.token` al inicio y lo conserva en la configuración.
- OpenClaw **no** genera automáticamente ese token cuando `gateway.auth.mode` ya es
  `password`, `none`, o `trusted-proxy`.
- Mantén el Gateway y cualquier host de nodo en una red privada (Tailscale); evita la exposición pública.
- Trata las URL/tokens de CDP remoto como secretos; prefiere variables de entorno o un gestor de secretos.

Consejos para CDP remoto:

- Prefiere endpoints cifrados (HTTPS o WSS) y tokens de corta duración cuando sea posible.
- Evita incrustar tokens de larga duración directamente en los archivos de configuración.

## Perfiles (multinavegador)

OpenClaw admite varios perfiles con nombre (configuraciones de enrutamiento). Los perfiles pueden ser:

- **gestionados por openclaw**: una instancia dedicada de navegador basado en Chromium con su propio directorio de datos de usuario + puerto CDP
- **remoto**: una URL CDP explícita (navegador basado en Chromium ejecutándose en otro lugar)
- **sesión existente**: tu perfil existente de Chrome mediante conexión automática con Chrome DevTools MCP

Valores predeterminados:

- El perfil `openclaw` se crea automáticamente si falta.
- El perfil `user` está integrado para la conexión existing-session de Chrome MCP.
- Los perfiles existing-session son optativos además de `user`; créalos con `--driver existing-session`.
- Los puertos CDP locales se asignan desde **18800–18899** de forma predeterminada.
- Eliminar un perfil mueve su directorio de datos local a la Papelera.

Todos los endpoints de control aceptan `?profile=<name>`; la CLI usa `--browser-profile`.

## Existing-session mediante Chrome DevTools MCP

OpenClaw también puede conectarse a un perfil de navegador basado en Chromium en ejecución mediante el
servidor oficial Chrome DevTools MCP. Esto reutiliza las pestañas y el estado de inicio de sesión
ya abiertos en ese perfil del navegador.

Referencias oficiales de contexto y configuración:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Perfil integrado:

- `user`

Opcional: crea tu propio perfil existing-session personalizado si quieres un
nombre, color o directorio de datos del navegador diferente.

Comportamiento predeterminado:

- El perfil integrado `user` usa conexión automática de Chrome MCP, que apunta al
  perfil local predeterminado de Google Chrome.

Usa `userDataDir` para Brave, Edge, Chromium o un perfil de Chrome no predeterminado:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Luego, en el navegador correspondiente:

1. Abre la página de inspección de ese navegador para depuración remota.
2. Habilita la depuración remota.
3. Mantén el navegador en ejecución y aprueba la solicitud de conexión cuando OpenClaw se conecte.

Páginas de inspección habituales:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Prueba rápida de conexión en vivo:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Cómo se ve cuando funciona correctamente:

- `status` muestra `driver: existing-session`
- `status` muestra `transport: chrome-mcp`
- `status` muestra `running: true`
- `tabs` enumera las pestañas del navegador que ya tienes abiertas
- `snapshot` devuelve refs de la pestaña activa seleccionada

Qué comprobar si la conexión no funciona:

- el navegador basado en Chromium de destino es versión `144+`
- la depuración remota está habilitada en la página de inspección de ese navegador
- el navegador mostró la solicitud de consentimiento de conexión y la aceptaste
- `openclaw doctor` migra la configuración antigua del navegador basada en extensiones y comprueba que
  Chrome esté instalado localmente para los perfiles predeterminados con conexión automática, pero no puede
  habilitar por ti la depuración remota del lado del navegador

Uso por parte del agente:

- Usa `profile="user"` cuando necesites el estado del navegador del usuario con sesión iniciada.
- Si usas un perfil existing-session personalizado, pasa ese nombre de perfil explícito.
- Elige este modo solo cuando el usuario esté en la computadora para aprobar la
  solicitud de conexión.
- el Gateway o el host de nodo pueden iniciar `npx chrome-devtools-mcp@latest --autoConnect`

Notas:

- Esta ruta tiene más riesgo que el perfil aislado `openclaw` porque puede
  actuar dentro de tu sesión de navegador con inicio de sesión.
- OpenClaw no inicia el navegador para este controlador; se conecta únicamente a una
  sesión existente.
- OpenClaw usa aquí el flujo oficial `--autoConnect` de Chrome DevTools MCP. Si
  `userDataDir` está configurado, OpenClaw lo pasa para apuntar a ese directorio
  explícito de datos de usuario de Chromium.
- Las capturas de pantalla de existing-session admiten capturas de página y capturas de elementos con `--ref`
  desde instantáneas, pero no selectores CSS `--element`.
- Las capturas de página de existing-session funcionan sin Playwright mediante Chrome MCP.
  Las capturas de elementos basadas en ref (`--ref`) también funcionan ahí, pero `--full-page`
  no se puede combinar con `--ref` ni con `--element`.
- Las acciones de existing-session siguen siendo más limitadas que la ruta del navegador
  gestionado:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` y `select` requieren
    refs de instantánea en lugar de selectores CSS
  - `click` es solo con el botón izquierdo (sin anulaciones de botón ni modificadores)
  - `type` no admite `slowly=true`; usa `fill` o `press`
  - `press` no admite `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` y `evaluate` no
    admiten anulaciones de tiempo de espera por llamada
  - `select` actualmente admite solo un único valor
- `wait --url` en existing-session admite patrones exactos, de subcadena y glob
  como otros controladores de navegador. `wait --load networkidle` aún no es compatible.
- Los hooks de carga de archivos en existing-session requieren `ref` o `inputRef`, admiten un archivo a la vez y no admiten el direccionamiento CSS `element`.
- Los hooks de diálogo en existing-session no admiten anulaciones de tiempo de espera.
- Algunas funciones aún requieren la ruta del navegador gestionado, incluidas acciones por lotes, exportación a PDF, interceptación de descargas y `responsebody`.
- Existing-session es local al host. Si Chrome está en otra máquina o en un
  espacio de nombres de red diferente, usa CDP remoto o un host de nodo en su lugar.

## Garantías de aislamiento

- **Directorio de datos de usuario dedicado**: nunca toca tu perfil personal del navegador.
- **Puertos dedicados**: evita `9222` para impedir colisiones con flujos de trabajo de desarrollo.
- **Control determinista de pestañas**: apunta a las pestañas por `targetId`, no por “la última pestaña”.

## Selección del navegador

Al iniciar localmente, OpenClaw elige el primero disponible:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Puedes anularlo con `browser.executablePath`.

Plataformas:

- macOS: comprueba `/Applications` y `~/Applications`.
- Linux: busca `google-chrome`, `brave`, `microsoft-edge`, `chromium`, etc.
- Windows: comprueba ubicaciones de instalación habituales.

## API de control (opcional)

Solo para integraciones locales, el Gateway expone una pequeña API HTTP en loopback:

- Estado/inicio/detención: `GET /`, `POST /start`, `POST /stop`
- Pestañas: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Instantánea/captura de pantalla: `GET /snapshot`, `POST /screenshot`
- Acciones: `POST /navigate`, `POST /act`
- Hooks: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Descargas: `POST /download`, `POST /wait/download`
- Depuración: `GET /console`, `POST /pdf`
- Depuración: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Red: `POST /response/body`
- Estado: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Estado: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Configuración: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Todos los endpoints aceptan `?profile=<name>`.

Si está configurada la autenticación del gateway con secreto compartido, las rutas HTTP del navegador también requieren autenticación:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` o autenticación HTTP Basic con esa contraseña

Notas:

- Esta API independiente del navegador en loopback **no** consume trusted-proxy ni
  encabezados de identidad de Tailscale Serve.
- Si `gateway.auth.mode` es `none` o `trusted-proxy`, estas rutas del navegador en loopback
  no heredan esos modos con identidad; mantenlas solo en loopback.

### Contrato de error de `/act`

`POST /act` usa una respuesta de error estructurada para la validación a nivel de ruta y
los errores de política:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Valores actuales de `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): falta `kind` o no se reconoce.
- `ACT_INVALID_REQUEST` (HTTP 400): la carga útil de la acción no superó la normalización o validación.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): se usó `selector` con un tipo de acción no compatible.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (o `wait --fn`) está deshabilitado por la configuración.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): `targetId` de nivel superior o por lotes entra en conflicto con el destino de la solicitud.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): la acción no es compatible con perfiles existing-session.

Otros errores de tiempo de ejecución aún pueden devolver `{ "error": "<message>" }` sin un
campo `code`.

### Requisito de Playwright

Algunas funciones (navigate/act/instantánea AI/instantánea de rol, capturas de pantalla de elementos,
PDF) requieren Playwright. Si Playwright no está instalado, esos endpoints devuelven
un error 501 claro.

Lo que sigue funcionando sin Playwright:

- Instantáneas ARIA
- Capturas de pantalla de página para el navegador gestionado `openclaw` cuando hay disponible un
  WebSocket CDP por pestaña
- Capturas de pantalla de página para perfiles `existing-session` / Chrome MCP
- Capturas de pantalla basadas en ref (`--ref`) de `existing-session` desde la salida de instantáneas

Lo que sigue necesitando Playwright:

- `navigate`
- `act`
- Instantáneas AI / instantáneas de rol
- Capturas de pantalla de elementos con selector CSS (`--element`)
- Exportación completa de PDF del navegador

Las capturas de pantalla de elementos también rechazan `--full-page`; la ruta devuelve `fullPage is
not supported for element screenshots`.

Si ves `Playwright is not available in this gateway build`, instala el paquete completo de
Playwright (no `playwright-core`) y reinicia el gateway, o reinstala
OpenClaw con compatibilidad para navegador.

#### Instalación de Playwright en Docker

Si tu Gateway se ejecuta en Docker, evita `npx playwright` (conflictos con las anulaciones de npm).
Usa la CLI incluida en su lugar:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Para conservar las descargas del navegador, configura `PLAYWRIGHT_BROWSERS_PATH` (por ejemplo,
`/home/node/.cache/ms-playwright`) y asegúrate de que `/home/node` se conserve mediante
`OPENCLAW_HOME_VOLUME` o un bind mount. Consulta [Docker](/es/install/docker).

## Cómo funciona (interno)

Flujo de alto nivel:

- Un pequeño **servidor de control** acepta solicitudes HTTP.
- Se conecta a navegadores basados en Chromium (Chrome/Brave/Edge/Chromium) mediante **CDP**.
- Para acciones avanzadas (clic/escritura/instantánea/PDF), usa **Playwright** sobre
  CDP.
- Cuando falta Playwright, solo están disponibles las operaciones que no usan Playwright.

Este diseño mantiene al agente sobre una interfaz estable y determinista, al tiempo que te permite
intercambiar navegadores y perfiles locales/remotos.

## Referencia rápida de la CLI

Todos los comandos aceptan `--browser-profile <name>` para apuntar a un perfil específico.
Todos los comandos también aceptan `--json` para salida legible por máquina (cargas útiles estables).

Aspectos básicos:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Inspección:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Nota sobre el ciclo de vida:

- Para perfiles de solo conexión y CDP remoto, `openclaw browser stop` sigue siendo el
  comando de limpieza correcto después de las pruebas. Cierra la sesión de control activa y
  borra las anulaciones temporales de emulación en lugar de cerrar el
  navegador subyacente.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Acciones:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Estado:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Notas:

- `upload` y `dialog` son llamadas de **preparación**; ejecútalas antes del clic/tecla
  que activa el selector de archivos o el cuadro de diálogo.
- Las rutas de salida de descargas y trazas están restringidas a las raíces temporales de OpenClaw:
  - trazas: `/tmp/openclaw` (alternativa: `${os.tmpdir()}/openclaw`)
  - descargas: `/tmp/openclaw/downloads` (alternativa: `${os.tmpdir()}/openclaw/downloads`)
- Las rutas de carga están restringidas a una raíz temporal de cargas de OpenClaw:
  - cargas: `/tmp/openclaw/uploads` (alternativa: `${os.tmpdir()}/openclaw/uploads`)
- `upload` también puede configurar entradas de archivo directamente mediante `--input-ref` o `--element`.
- `snapshot`:
  - `--format ai` (predeterminado cuando Playwright está instalado): devuelve una instantánea AI con refs numéricas (`aria-ref="<n>"`).
  - `--format aria`: devuelve el árbol de accesibilidad (sin refs; solo inspección).
  - `--efficient` (o `--mode efficient`): preajuste de instantánea compacta por rol (interactiva + compacta + profundidad + `maxChars` más bajo).
  - Predeterminado de configuración (solo herramienta/CLI): configura `browser.snapshotDefaults.mode: "efficient"` para usar instantáneas eficientes cuando quien llama no pasa un modo (consulta [Configuración del Gateway](/es/gateway/configuration-reference#browser)).
  - Las opciones de instantánea por rol (`--interactive`, `--compact`, `--depth`, `--selector`) fuerzan una instantánea basada en roles con refs como `ref=e12`.
  - `--frame "<iframe selector>"` limita las instantáneas por rol a un iframe (se combina con refs por rol como `e12`).
  - `--interactive` genera una lista plana y fácil de elegir de elementos interactivos (lo mejor para ejecutar acciones).
  - `--labels` agrega una captura de pantalla solo de la ventana gráfica con etiquetas ref superpuestas (imprime `MEDIA:<path>`).
- `click`/`type`/etc. requieren una `ref` de `snapshot` (ya sea numérica `12` o ref por rol `e12`).
  Los selectores CSS no se admiten intencionalmente para acciones.

## Instantáneas y refs

OpenClaw admite dos estilos de “snapshot”:

- **Instantánea AI (refs numéricas)**: `openclaw browser snapshot` (predeterminado; `--format ai`)
  - Salida: una instantánea de texto que incluye refs numéricas.
  - Acciones: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Internamente, la ref se resuelve mediante `aria-ref` de Playwright.

- **Instantánea por rol (refs por rol como `e12`)**: `openclaw browser snapshot --interactive` (o `--compact`, `--depth`, `--selector`, `--frame`)
  - Salida: una lista/árbol basado en roles con `[ref=e12]` (y opcionalmente `[nth=1]`).
  - Acciones: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Internamente, la ref se resuelve mediante `getByRole(...)` (más `nth()` para duplicados).
  - Agrega `--labels` para incluir una captura de pantalla de la ventana gráfica con etiquetas `e12` superpuestas.

Comportamiento de las refs:

- Las refs **no son estables entre navegaciones**; si algo falla, vuelve a ejecutar `snapshot` y usa una ref nueva.
- Si la instantánea por rol se tomó con `--frame`, las refs por rol quedan limitadas a ese iframe hasta la siguiente instantánea por rol.

## Mejoras de `wait`

Puedes esperar algo más que solo tiempo/texto:

- Esperar URL (globs compatibles con Playwright):
  - `openclaw browser wait --url "**/dash"`
- Esperar estado de carga:
  - `openclaw browser wait --load networkidle`
- Esperar un predicado de JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Esperar a que un selector se vuelva visible:
  - `openclaw browser wait "#main"`

Se pueden combinar:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Flujos de depuración

Cuando falla una acción (por ejemplo, “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. Usa `click <ref>` / `type <ref>` (prefiere refs por rol en modo interactivo)
3. Si sigue fallando: `openclaw browser highlight <ref>` para ver a qué apunta Playwright
4. Si la página se comporta de forma extraña:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Para una depuración profunda: graba una traza:
   - `openclaw browser trace start`
   - reproduce el problema
   - `openclaw browser trace stop` (imprime `TRACE:<path>`)

## Salida JSON

`--json` es para scripts y herramientas estructuradas.

Ejemplos:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Las instantáneas por rol en JSON incluyen `refs` más un pequeño bloque `stats` (líneas/caracteres/refs/interactivos) para que las herramientas puedan razonar sobre el tamaño y la densidad de la carga útil.

## Controles de estado y entorno

Son útiles para flujos de trabajo de “hacer que el sitio se comporte como X”:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Sin conexión: `set offline on|off`
- Encabezados: `set headers --headers-json '{"X-Debug":"1"}'` (el heredado `set headers --json '{"X-Debug":"1"}'` sigue siendo compatible)
- Autenticación HTTP Basic: `set credentials user pass` (o `--clear`)
- Geolocalización: `set geo <lat> <lon> --origin "https://example.com"` (o `--clear`)
- Medios: `set media dark|light|no-preference|none`
- Zona horaria / configuración regional: `set timezone ...`, `set locale ...`
- Dispositivo / ventana gráfica:
  - `set device "iPhone 14"` (preajustes de dispositivos de Playwright)
  - `set viewport 1280 720`

## Seguridad y privacidad

- El perfil de navegador openclaw puede contener sesiones con inicio de sesión; trátalo como información sensible.
- `browser act kind=evaluate` / `openclaw browser evaluate` y `wait --fn`
  ejecutan JavaScript arbitrario en el contexto de la página. La inyección de prompts puede dirigir
  esto. Desactívalo con `browser.evaluateEnabled=false` si no lo necesitas.
- Para inicios de sesión y notas anti-bot (X/Twitter, etc.), consulta [Inicio de sesión en navegador + publicación en X/Twitter](/es/tools/browser-login).
- Mantén el Gateway/host de nodo privado (solo loopback o tailnet).
- Los endpoints CDP remotos son potentes; túnelalos y protégelos.

Ejemplo de modo estricto (bloquear destinos privados/internos de forma predeterminada):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // permiso exacto opcional
    },
  },
}
```

## Solución de problemas

Para problemas específicos de Linux (especialmente Chromium de snap), consulta
[Solución de problemas del navegador](/es/tools/browser-linux-troubleshooting).

Para configuraciones divididas entre Gateway en WSL2 + Chrome en Windows, consulta
[Solución de problemas de WSL2 + Windows + Chrome remoto por CDP](/es/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

## Herramientas del agente + cómo funciona el control

El agente obtiene **una herramienta** para la automatización del navegador:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Cómo se asigna:

- `browser snapshot` devuelve un árbol de UI estable (AI o ARIA).
- `browser act` usa los ID `ref` de la instantánea para hacer clic/escribir/arrastrar/seleccionar.
- `browser screenshot` captura píxeles (página completa o elemento).
- `browser` acepta:
  - `profile` para elegir un perfil de navegador con nombre (openclaw, chrome o CDP remoto).
  - `target` (`sandbox` | `host` | `node`) para seleccionar dónde vive el navegador.
  - En sesiones aisladas en sandbox, `target: "host"` requiere `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Si se omite `target`: las sesiones en sandbox usan `sandbox` de forma predeterminada, las sesiones sin sandbox usan `host`.
  - Si hay conectado un nodo con capacidad de navegador, la herramienta puede redirigirse automáticamente a él a menos que fijes `target="host"` o `target="node"`.

Esto mantiene al agente determinista y evita selectores frágiles.

## Relacionado

- [Resumen de herramientas](/es/tools) — todas las herramientas del agente disponibles
- [Sandboxing](/es/gateway/sandboxing) — control del navegador en entornos aislados
- [Security](/es/gateway/security) — riesgos y endurecimiento del control del navegador
