---
read_when:
    - Agregando automatización del navegador controlada por el agente
    - Depurando por qué openclaw está interfiriendo con tu propio Chrome
    - Implementando la configuración y el ciclo de vida del navegador en la app de macOS
summary: Servicio integrado de control del navegador + comandos de acción
title: Browser (gestionado por OpenClaw)
x-i18n:
    generated_at: "2026-04-11T02:47:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: da6fed36a6f40a50e825f90e5616778954545bd7e52397f7e088b85251ee024f
    source_path: tools/browser.md
    workflow: 15
---

# Browser (gestionado por openclaw)

OpenClaw puede ejecutar un **perfil dedicado de Chrome/Brave/Edge/Chromium** que el agente controla.
Está aislado de tu navegador personal y se gestiona mediante un pequeño servicio local
de control dentro de la Gateway (solo loopback).

Vista para principiantes:

- Piensa en ello como un **navegador separado, solo para el agente**.
- El perfil `openclaw` **no** toca tu perfil personal del navegador.
- El agente puede **abrir pestañas, leer páginas, hacer clic y escribir** en una vía segura.
- El perfil integrado `user` se conecta a tu sesión real de Chrome con sesión iniciada mediante Chrome MCP.

## Qué obtienes

- Un perfil de navegador separado llamado **openclaw** (acento naranja de forma predeterminada).
- Control determinista de pestañas (listar/abrir/enfocar/cerrar).
- Acciones del agente (clic/escribir/arrastrar/seleccionar), instantáneas, capturas de pantalla, PDF.
- Soporte opcional para varios perfiles (`openclaw`, `work`, `remote`, ...).

Este navegador **no** es tu navegador principal de uso diario. Es una superficie segura y aislada para
automatización y verificación del agente.

## Inicio rápido

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Si aparece “Browser disabled”, actívalo en la configuración (ver abajo) y reinicia la
Gateway.

Si `openclaw browser` falta por completo, o el agente dice que la herramienta de navegador
no está disponible, ve a [Missing browser command or tool](/es/tools/browser#missing-browser-command-or-tool).

## Control del plugin

La herramienta predeterminada `browser` ahora es un plugin integrado que se incluye activado por
defecto. Eso significa que puedes desactivarlo o reemplazarlo sin quitar el resto del
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

Desactiva el plugin integrado antes de instalar otro plugin que proporcione el
mismo nombre de herramienta `browser`. La experiencia predeterminada del navegador necesita ambos:

- `plugins.entries.browser.enabled` no desactivado
- `browser.enabled=true`

Si desactivas solo el plugin, la CLI de navegador incluida (`openclaw browser`),
el método de gateway (`browser.request`), la herramienta del agente y el servicio predeterminado
de control del navegador desaparecen juntos. Tu configuración `browser.*` permanece intacta para que un
plugin de reemplazo la reutilice.

El plugin integrado del navegador ahora también se encarga de la implementación del runtime del navegador.
El núcleo conserva solo los ayudantes compartidos del Plugin SDK más reexportaciones de compatibilidad para
rutas de importación internas antiguas. En la práctica, quitar o reemplazar el paquete del plugin del navegador
elimina el conjunto de funciones del navegador en lugar de dejar un segundo runtime
gestionado por el núcleo.

Los cambios en la configuración del navegador siguen requiriendo un reinicio de la Gateway para que el plugin integrado
pueda volver a registrar su servicio de navegador con la nueva configuración.

## Comando o herramienta de navegador faltante

Si `openclaw browser` de repente pasa a ser un comando desconocido después de una actualización, o
el agente informa que falta la herramienta de navegador, la causa más común es una lista restrictiva
`plugins.allow` que no incluye `browser`.

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

- `browser.enabled=true` no es suficiente por sí solo cuando `plugins.allow` está configurado.
- `plugins.entries.browser.enabled=true` tampoco es suficiente por sí solo cuando `plugins.allow` está configurado.
- `tools.alsoAllow: ["browser"]` **no** carga el plugin integrado del navegador. Solo ajusta la política de herramientas después de que el plugin ya se ha cargado.
- Si no necesitas una lista restrictiva de plugins permitidos, eliminar `plugins.allow` también restaura el comportamiento predeterminado del navegador integrado.

Síntomas típicos:

- `openclaw browser` es un comando desconocido.
- falta `browser.request`.
- El agente informa que la herramienta de navegador no está disponible o falta.

## Perfiles: `openclaw` frente a `user`

- `openclaw`: navegador gestionado y aislado (no requiere extensión).
- `user`: perfil integrado de conexión Chrome MCP para tu **sesión real de Chrome con sesión iniciada**.

Para llamadas de herramientas de navegador del agente:

- Predeterminado: usa el navegador aislado `openclaw`.
- Prefiere `profile="user"` cuando importen las sesiones ya iniciadas y el usuario
  esté en el equipo para hacer clic/aprobar cualquier solicitud de conexión.
- `profile` es la anulación explícita cuando quieres un modo de navegador específico.

Configura `browser.defaultProfile: "openclaw"` si quieres el modo gestionado como predeterminado.

## Configuración

La configuración del navegador vive en `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // predeterminado: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // habilítalo solo si confías en el acceso del navegador a la red privada
      // allowPrivateNetwork: true, // alias heredado
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // anulación heredada de un solo perfil
    remoteCdpTimeoutMs: 1500, // tiempo de espera HTTP de CDP remoto (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // tiempo de espera del handshake WebSocket de CDP remoto (ms)
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
- Si anulas el puerto de la Gateway (`gateway.port` o `OPENCLAW_GATEWAY_PORT`),
  los puertos derivados del navegador cambian para permanecer en la misma “familia”.
- `cdpUrl` usa por defecto el puerto CDP local gestionado cuando no está configurado.
- `remoteCdpTimeoutMs` se aplica a las comprobaciones de accesibilidad de CDP remotas (no loopback).
- `remoteCdpHandshakeTimeoutMs` se aplica a las comprobaciones de accesibilidad del handshake WebSocket de CDP remoto.
- La navegación/apertura de pestañas del navegador está protegida contra SSRF antes de navegar y se vuelve a comprobar en la medida de lo posible en la URL final `http(s)` después de navegar.
- En modo SSRF estricto, la detección/sondeo de endpoints remotos de CDP (`cdpUrl`, incluidas las búsquedas de `/json/version`) también se comprueban.
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` está desactivado de forma predeterminada. Configúralo en `true` solo cuando confíes intencionalmente en el acceso del navegador a la red privada.
- `browser.ssrfPolicy.allowPrivateNetwork` sigue siendo compatible como alias heredado por compatibilidad.
- `attachOnly: true` significa “nunca iniciar un navegador local; solo conectarse si ya se está ejecutando”.
- `color` + `color` por perfil tiñen la interfaz del navegador para que puedas ver qué perfil está activo.
- El perfil predeterminado es `openclaw` (navegador independiente gestionado por OpenClaw). Usa `defaultProfile: "user"` para optar por el navegador del usuario con sesión iniciada.
- Orden de detección automática: navegador predeterminado del sistema si está basado en Chromium; si no, Chrome → Brave → Edge → Chromium → Chrome Canary.
- Los perfiles locales `openclaw` asignan automáticamente `cdpPort`/`cdpUrl`; configúralos solo para CDP remoto.
- `driver: "existing-session"` usa Chrome DevTools MCP en lugar de CDP sin procesar. No
  configures `cdpUrl` para ese driver.
- Configura `browser.profiles.<name>.userDataDir` cuando un perfil `existing-session`
  deba conectarse a un perfil de usuario no predeterminado de Chromium, como Brave o Edge.

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

- **Control local (predeterminado):** la Gateway inicia el servicio de control loopback y puede lanzar un navegador local.
- **Control remoto (host de nodo):** ejecuta un host de nodo en la máquina que tiene el navegador; la Gateway envía a ese host las acciones del navegador.
- **CDP remoto:** configura `browser.profiles.<name>.cdpUrl` (o `browser.cdpUrl`) para
  conectarte a un navegador remoto basado en Chromium. En este caso, OpenClaw no iniciará un navegador local.

El comportamiento al detener difiere según el modo de perfil:

- perfiles locales gestionados: `openclaw browser stop` detiene el proceso del navegador que
  OpenClaw inició
- perfiles solo de conexión y perfiles CDP remotos: `openclaw browser stop` cierra la
  sesión de control activa y libera las anulaciones de emulación de Playwright/CDP (viewport,
  esquema de color, configuración regional, zona horaria, modo sin conexión y estado similar), aunque
  OpenClaw no haya iniciado ningún proceso de navegador

Las URL CDP remotas pueden incluir autenticación:

- Tokens de consulta (por ejemplo, `https://provider.example?token=<token>`)
- Autenticación HTTP Basic (por ejemplo, `https://user:pass@provider.example`)

OpenClaw conserva la autenticación al llamar a los endpoints `/json/*` y al conectarse
al WebSocket CDP. Prefiere variables de entorno o gestores de secretos para
los tokens en lugar de confirmarlos en archivos de configuración.

## Proxy de navegador de nodo (predeterminado sin configuración)

Si ejecutas un **host de nodo** en la máquina que tiene tu navegador, OpenClaw puede
redirigir automáticamente las llamadas de la herramienta de navegador a ese nodo sin ninguna configuración adicional del navegador.
Esta es la ruta predeterminada para gateways remotas.

Notas:

- El host de nodo expone su servidor local de control del navegador mediante un **comando proxy**.
- Los perfiles provienen de la propia configuración `browser.profiles` del nodo (igual que en local).
- `nodeHost.browserProxy.allowProfiles` es opcional. Déjalo vacío para el comportamiento heredado/predeterminado: todos los perfiles configurados siguen siendo accesibles a través del proxy, incluidas las rutas de crear/eliminar perfiles.
- Si configuras `nodeHost.browserProxy.allowProfiles`, OpenClaw lo trata como un límite de privilegio mínimo: solo se pueden usar como destino los perfiles permitidos, y las rutas persistentes de crear/eliminar perfiles se bloquean en la superficie del proxy.
- Desactívalo si no lo quieres:
  - En el nodo: `nodeHost.browserProxy.enabled=false`
  - En la gateway: `gateway.nodes.browser.mode="off"`

## Browserless (CDP remoto alojado)

[Browserless](https://browserless.io) es un servicio de Chromium alojado que expone
URL de conexión CDP mediante HTTPS y WebSocket. OpenClaw puede usar cualquiera de las dos formas, pero
para un perfil de navegador remoto la opción más simple es la URL WebSocket directa
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

- Sustituye `<BROWSERLESS_API_KEY>` por tu token real de Browserless.
- Elige el endpoint regional que coincida con tu cuenta de Browserless (consulta su documentación).
- Si Browserless te da una URL base HTTPS, puedes convertirla a
  `wss://` para una conexión CDP directa o conservar la URL HTTPS y dejar que OpenClaw
  detecte `/json/version`.

## Proveedores CDP WebSocket directos

Algunos servicios alojados de navegador exponen un endpoint **WebSocket** directo en lugar de
la detección CDP estándar basada en HTTP (`/json/version`). OpenClaw admite ambos:

- **Endpoints HTTP(S)** — OpenClaw llama a `/json/version` para descubrir la
  URL del depurador WebSocket y luego se conecta.
- **Endpoints WebSocket** (`ws://` / `wss://`) — OpenClaw se conecta directamente,
  omitiendo `/json/version`. Úsalo para servicios como
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com) o cualquier proveedor que te dé una
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) es una plataforma en la nube para ejecutar
navegadores headless con resolución de CAPTCHA integrada, modo furtivo y proxies
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
  desde el [panel Overview](https://www.browserbase.com/overview).
- Sustituye `<BROWSERBASE_API_KEY>` por tu clave de API real de Browserbase.
- Browserbase crea automáticamente una sesión del navegador al conectarse por WebSocket, por lo que no
  se necesita ningún paso manual de creación de sesión.
- El nivel gratuito permite una sesión simultánea y una hora de navegador por mes.
  Consulta [pricing](https://www.browserbase.com/pricing) para ver los límites de los planes de pago.
- Consulta la [documentación de Browserbase](https://docs.browserbase.com) para ver la
  referencia completa de la API, guías del SDK y ejemplos de integración.

## Seguridad

Ideas clave:

- El control del navegador es solo loopback; el acceso fluye a través de la autenticación de la Gateway o del emparejamiento de nodos.
- La API HTTP independiente del navegador en loopback usa **solo autenticación con secreto compartido**:
  autenticación bearer con token de gateway, `x-openclaw-password` o autenticación HTTP Basic con la
  contraseña de gateway configurada.
- Los encabezados de identidad de Tailscale Serve y `gateway.auth.mode: "trusted-proxy"` **no**
  autentican esta API independiente del navegador en loopback.
- Si el control del navegador está habilitado y no hay autenticación de secreto compartido configurada, OpenClaw
  genera automáticamente `gateway.auth.token` al iniciar y lo persiste en la configuración.
- OpenClaw **no** genera automáticamente ese token cuando `gateway.auth.mode` ya es
  `password`, `none` o `trusted-proxy`.
- Mantén la Gateway y cualquier host de nodo en una red privada (Tailscale); evita la exposición pública.
- Trata las URL/tokens remotos de CDP como secretos; prefiere variables de entorno o un gestor de secretos.

Consejos para CDP remoto:

- Prefiere endpoints cifrados (HTTPS o WSS) y tokens de corta duración cuando sea posible.
- Evita incrustar tokens de larga duración directamente en archivos de configuración.

## Perfiles (varios navegadores)

OpenClaw admite varios perfiles nombrados (configuraciones de enrutamiento). Los perfiles pueden ser:

- **gestionados por openclaw**: una instancia dedicada de navegador basado en Chromium con su propio directorio de datos de usuario + puerto CDP
- **remotos**: una URL CDP explícita (navegador basado en Chromium ejecutándose en otro lugar)
- **sesión existente**: tu perfil existente de Chrome mediante conexión automática con Chrome DevTools MCP

Valores predeterminados:

- El perfil `openclaw` se crea automáticamente si falta.
- El perfil `user` está integrado para la conexión a sesión existente con Chrome MCP.
- Los perfiles de sesión existente requieren habilitación explícita más allá de `user`; créalos con `--driver existing-session`.
- Los puertos CDP locales se asignan desde **18800–18899** de forma predeterminada.
- Eliminar un perfil mueve su directorio local de datos a la Papelera.

Todos los endpoints de control aceptan `?profile=<name>`; la CLI usa `--browser-profile`.

## Sesión existente mediante Chrome DevTools MCP

OpenClaw también puede conectarse a un perfil en ejecución de navegador basado en Chromium mediante el
servidor oficial Chrome DevTools MCP. Esto reutiliza las pestañas y el estado de inicio de sesión
ya abiertos en ese perfil del navegador.

Referencias oficiales de contexto y configuración:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Perfil integrado:

- `user`

Opcional: crea tu propio perfil personalizado de sesión existente si quieres un
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

Así se ve el éxito:

- `status` muestra `driver: existing-session`
- `status` muestra `transport: chrome-mcp`
- `status` muestra `running: true`
- `tabs` lista las pestañas del navegador que ya están abiertas
- `snapshot` devuelve referencias de la pestaña activa seleccionada

Qué comprobar si la conexión no funciona:

- el navegador basado en Chromium objetivo es versión `144+`
- la depuración remota está habilitada en la página de inspección de ese navegador
- el navegador mostró y aceptaste la solicitud de consentimiento de conexión
- `openclaw doctor` migra la configuración antigua del navegador basada en extensiones y comprueba que
  Chrome esté instalado localmente para perfiles predeterminados de conexión automática, pero no puede
  habilitar por ti la depuración remota del lado del navegador

Uso por el agente:

- Usa `profile="user"` cuando necesites el estado del navegador del usuario con sesión iniciada.
- Si usas un perfil personalizado de sesión existente, pasa ese nombre de perfil explícito.
- Elige este modo solo cuando el usuario esté en el equipo para aprobar la
  solicitud de conexión.
- la Gateway o el host de nodo pueden ejecutar `npx chrome-devtools-mcp@latest --autoConnect`

Notas:

- Esta ruta es de mayor riesgo que el perfil aislado `openclaw` porque puede
  actuar dentro de tu sesión iniciada del navegador.
- OpenClaw no inicia el navegador para este driver; solo se conecta a una
  sesión existente.
- OpenClaw usa aquí el flujo oficial `--autoConnect` de Chrome DevTools MCP. Si
  `userDataDir` está configurado, OpenClaw lo pasa para apuntar a ese directorio
  explícito de datos de usuario de Chromium.
- Las capturas de pantalla de sesión existente admiten capturas de página y capturas de elementos con `--ref`
  a partir de instantáneas, pero no selectores CSS `--element`.
- Las capturas de pantalla de páginas de sesión existente funcionan sin Playwright mediante Chrome MCP.
  Las capturas de elementos basadas en referencias (`--ref`) también funcionan ahí, pero `--full-page`
  no se puede combinar con `--ref` ni con `--element`.
- Las acciones de sesión existente siguen siendo más limitadas que la ruta del navegador
  gestionado:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` y `select` requieren
    referencias de instantánea en lugar de selectores CSS
  - `click` solo es con botón izquierdo (sin anulaciones de botón ni modificadores)
  - `type` no admite `slowly=true`; usa `fill` o `press`
  - `press` no admite `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` y `evaluate` no
    admiten anulaciones de tiempo de espera por llamada
  - `select` actualmente admite solo un valor
- `wait --url` de sesión existente admite patrones exactos, de subcadena y glob
  como otros drivers de navegador. `wait --load networkidle` aún no es compatible.
- Los hooks de carga de archivos de sesión existente requieren `ref` o `inputRef`, admiten
  un archivo a la vez y no admiten selección CSS con `element`.
- Los hooks de diálogo de sesión existente no admiten anulaciones de tiempo de espera.
- Algunas funciones siguen requiriendo la ruta del navegador gestionado, incluidas acciones
  por lotes, exportación a PDF, interceptación de descargas y `responsebody`.
- La sesión existente es local al host. Si Chrome está en otra máquina o en un
  espacio de nombres de red diferente, usa CDP remoto o un host de nodo en su lugar.

## Garantías de aislamiento

- **Directorio de datos de usuario dedicado**: nunca toca tu perfil personal del navegador.
- **Puertos dedicados**: evita `9222` para prevenir colisiones con flujos de trabajo de desarrollo.
- **Control determinista de pestañas**: apunta a las pestañas por `targetId`, no por “última pestaña”.

## Selección del navegador

Al iniciarse localmente, OpenClaw elige el primero disponible:

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

Solo para integraciones locales, la Gateway expone una pequeña API HTTP en loopback:

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

Si la autenticación de gateway con secreto compartido está configurada, las rutas HTTP del navegador también requieren autenticación:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` o autenticación HTTP Basic con esa contraseña

Notas:

- Esta API independiente del navegador en loopback **no** consume encabezados de identidad de proxy confiable ni
  de Tailscale Serve.
- Si `gateway.auth.mode` es `none` o `trusted-proxy`, estas rutas del navegador en loopback
  no heredan esos modos con identidad; mantenlas solo en loopback.

### Contrato de error de `/act`

`POST /act` usa una respuesta de error estructurada para validación a nivel de ruta y
fallos de política:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Valores actuales de `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): falta `kind` o no se reconoce.
- `ACT_INVALID_REQUEST` (HTTP 400): la carga útil de la acción falló en la normalización o validación.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): se usó `selector` con un tipo de acción no compatible.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (o `wait --fn`) está desactivado por configuración.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): el `targetId` de nivel superior o por lotes entra en conflicto con el destino de la solicitud.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): la acción no es compatible con perfiles de sesión existente.

Otros fallos de runtime pueden seguir devolviendo `{ "error": "<message>" }` sin un
campo `code`.

### Requisito de Playwright

Algunas funciones (navigate/act/AI snapshot/role snapshot, capturas de pantalla de elementos,
PDF) requieren Playwright. Si Playwright no está instalado, esos endpoints devuelven
un error 501 claro.

Qué sigue funcionando sin Playwright:

- instantáneas ARIA
- capturas de pantalla de página para el navegador gestionado `openclaw` cuando hay un WebSocket
  CDP por pestaña disponible
- capturas de pantalla de página para perfiles `existing-session` / Chrome MCP
- capturas de pantalla basadas en referencias (`--ref`) de `existing-session` a partir de la salida de instantánea

Qué sigue necesitando Playwright:

- `navigate`
- `act`
- instantáneas AI / instantáneas de rol
- capturas de pantalla de elementos con selector CSS (`--element`)
- exportación completa de PDF del navegador

Las capturas de pantalla de elementos también rechazan `--full-page`; la ruta devuelve `fullPage is
not supported for element screenshots`.

Si ves `Playwright is not available in this gateway build`, instala el paquete completo de
Playwright (no `playwright-core`) y reinicia la gateway, o vuelve a instalar
OpenClaw con soporte de navegador.

#### Instalación de Playwright en Docker

Si tu Gateway se ejecuta en Docker, evita `npx playwright` (conflictos con anulaciones de npm).
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
- Para acciones avanzadas (clic/escribir/instantánea/PDF), usa **Playwright** sobre
  CDP.
- Cuando falta Playwright, solo están disponibles las operaciones que no dependen de Playwright.

Este diseño mantiene al agente en una interfaz estable y determinista, al tiempo que te permite
intercambiar navegadores y perfiles locales/remotos.

## Referencia rápida de CLI

Todos los comandos aceptan `--browser-profile <name>` para apuntar a un perfil específico.
Todos los comandos también aceptan `--json` para salida legible por máquina (cargas útiles estables).

Básicos:

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

- Para perfiles solo de conexión y perfiles CDP remotos, `openclaw browser stop` sigue siendo el
  comando correcto de limpieza después de las pruebas. Cierra la sesión de control activa y
  borra anulaciones temporales de emulación en lugar de matar el navegador
  subyacente.
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

- `upload` y `dialog` son llamadas de **preparación**; ejecútalas antes del clic/pulsación
  que activa el selector/diálogo.
- Las rutas de salida de descargas y trazas están restringidas a raíces temporales de OpenClaw:
  - trazas: `/tmp/openclaw` (respaldo: `${os.tmpdir()}/openclaw`)
  - descargas: `/tmp/openclaw/downloads` (respaldo: `${os.tmpdir()}/openclaw/downloads`)
- Las rutas de carga están restringidas a una raíz temporal de cargas de OpenClaw:
  - cargas: `/tmp/openclaw/uploads` (respaldo: `${os.tmpdir()}/openclaw/uploads`)
- `upload` también puede configurar directamente entradas de archivo mediante `--input-ref` o `--element`.
- `snapshot`:
  - `--format ai` (predeterminado cuando Playwright está instalado): devuelve una instantánea AI con referencias numéricas (`aria-ref="<n>"`).
  - `--format aria`: devuelve el árbol de accesibilidad (sin referencias; solo inspección).
  - `--efficient` (o `--mode efficient`): ajuste preestablecido compacto de instantánea por rol (interactiva + compacta + profundidad + menor `maxChars`).
  - Predeterminado de configuración (solo herramienta/CLI): configura `browser.snapshotDefaults.mode: "efficient"` para usar instantáneas eficientes cuando quien llama no pase un modo (consulta [Gateway configuration](/es/gateway/configuration-reference#browser)).
  - Las opciones de instantánea por rol (`--interactive`, `--compact`, `--depth`, `--selector`) fuerzan una instantánea basada en roles con referencias como `ref=e12`.
  - `--frame "<iframe selector>"` limita las instantáneas por rol a un iframe (se combina con referencias de rol como `e12`).
  - `--interactive` produce una lista plana y fácil de elegir de elementos interactivos (mejor para ejecutar acciones).
  - `--labels` agrega una captura de pantalla solo del viewport con etiquetas de referencia superpuestas (imprime `MEDIA:<path>`).
- `click`/`type`/etc. requieren una `ref` de `snapshot` (ya sea numérica `12` o de rol `e12`).
  Los selectores CSS intencionalmente no se admiten para acciones.

## Instantáneas y referencias

OpenClaw admite dos estilos de “instantánea”:

- **Instantánea AI (referencias numéricas)**: `openclaw browser snapshot` (predeterminada; `--format ai`)
  - Salida: una instantánea de texto que incluye referencias numéricas.
  - Acciones: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Internamente, la referencia se resuelve mediante `aria-ref` de Playwright.

- **Instantánea por rol (referencias de rol como `e12`)**: `openclaw browser snapshot --interactive` (o `--compact`, `--depth`, `--selector`, `--frame`)
  - Salida: una lista/árbol basado en roles con `[ref=e12]` (y opcionalmente `[nth=1]`).
  - Acciones: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Internamente, la referencia se resuelve mediante `getByRole(...)` (más `nth()` para duplicados).
  - Agrega `--labels` para incluir una captura de pantalla del viewport con etiquetas `e12` superpuestas.

Comportamiento de las referencias:

- Las referencias **no son estables entre navegaciones**; si algo falla, vuelve a ejecutar `snapshot` y usa una referencia nueva.
- Si la instantánea por rol se tomó con `--frame`, las referencias de rol quedan limitadas a ese iframe hasta la siguiente instantánea por rol.

## Mejoras para `wait`

Puedes esperar algo más que tiempo/texto:

- Esperar una URL (se admiten globs de Playwright):
  - `openclaw browser wait --url "**/dash"`
- Esperar un estado de carga:
  - `openclaw browser wait --load networkidle`
- Esperar un predicado JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Esperar a que un selector se vuelva visible:
  - `openclaw browser wait "#main"`

Estas opciones se pueden combinar:

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
2. Usa `click <ref>` / `type <ref>` (prefiere referencias de rol en modo interactivo)
3. Si sigue fallando: `openclaw browser highlight <ref>` para ver a qué apunta Playwright
4. Si la página se comporta de forma extraña:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Para depuración profunda: graba una traza:
   - `openclaw browser trace start`
   - reproduce el problema
   - `openclaw browser trace stop` (imprime `TRACE:<path>`)

## Salida JSON

`--json` es para scripting y herramientas estructuradas.

Ejemplos:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Las instantáneas por rol en JSON incluyen `refs` más un pequeño bloque `stats` (líneas/caracteres/referencias/interactivos) para que las herramientas puedan razonar sobre el tamaño y la densidad de la carga útil.

## Controles de estado y entorno

Son útiles para flujos de trabajo del tipo “hacer que el sitio se comporte como X”:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Sin conexión: `set offline on|off`
- Encabezados: `set headers --headers-json '{"X-Debug":"1"}'` (el heredado `set headers --json '{"X-Debug":"1"}'` sigue siendo compatible)
- Autenticación HTTP Basic: `set credentials user pass` (o `--clear`)
- Geolocalización: `set geo <lat> <lon> --origin "https://example.com"` (o `--clear`)
- Multimedia: `set media dark|light|no-preference|none`
- Zona horaria / configuración regional: `set timezone ...`, `set locale ...`
- Dispositivo / viewport:
  - `set device "iPhone 14"` (preajustes de dispositivos de Playwright)
  - `set viewport 1280 720`

## Seguridad y privacidad

- El perfil del navegador openclaw puede contener sesiones iniciadas; trátalo como información sensible.
- `browser act kind=evaluate` / `openclaw browser evaluate` y `wait --fn`
  ejecutan JavaScript arbitrario en el contexto de la página. La inyección de prompts puede dirigir
  esto. Desactívalo con `browser.evaluateEnabled=false` si no lo necesitas.
- Para inicios de sesión y notas anti-bot (X/Twitter, etc.), consulta [Browser login + X/Twitter posting](/es/tools/browser-login).
- Mantén privada la Gateway/el host de nodo (solo loopback o tailnet).
- Los endpoints CDP remotos son potentes; protégelos y túnelizalos.

Ejemplo de modo estricto (bloquea destinos privados/internos de forma predeterminada):

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
[Browser troubleshooting](/es/tools/browser-linux-troubleshooting).

Para configuraciones divididas entre Gateway en WSL2 + Chrome en Windows, consulta
[WSL2 + Windows + remote Chrome CDP troubleshooting](/es/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

## Herramientas del agente + cómo funciona el control

El agente recibe **una herramienta** para automatización del navegador:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Cómo se asigna:

- `browser snapshot` devuelve un árbol de interfaz estable (AI o ARIA).
- `browser act` usa los ID `ref` de la instantánea para hacer clic/escribir/arrastrar/seleccionar.
- `browser screenshot` captura píxeles (página completa o elemento).
- `browser` acepta:
  - `profile` para elegir un perfil de navegador nombrado (openclaw, chrome o CDP remoto).
  - `target` (`sandbox` | `host` | `node`) para seleccionar dónde vive el navegador.
  - En sesiones con sandbox, `target: "host"` requiere `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Si se omite `target`: las sesiones con sandbox usan por defecto `sandbox`, las sesiones sin sandbox usan por defecto `host`.
  - Si hay un nodo conectado con capacidad de navegador, la herramienta puede redirigirse automáticamente a él salvo que fijes `target="host"` o `target="node"`.

Esto mantiene al agente determinista y evita selectores frágiles.

## Relacionado

- [Tools Overview](/es/tools) — todas las herramientas de agente disponibles
- [Sandboxing](/es/gateway/sandboxing) — control del navegador en entornos con sandbox
- [Security](/es/gateway/security) — riesgos y endurecimiento del control del navegador
