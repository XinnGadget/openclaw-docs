---
read_when:
    - Ejecutar pruebas localmente o en CI
    - Agregar regresiones para errores de modelo/proveedor
    - Depurar el comportamiento del gateway + agente
summary: 'Kit de pruebas: suites unitarias/e2e/live, ejecutores de Docker y qué cubre cada prueba'
title: Pruebas
x-i18n:
    generated_at: "2026-04-10T05:12:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 21b78e59a5189f4e8e6e1b490d350f4735c0395da31d21fc5d10b825313026b4
    source_path: help/testing.md
    workflow: 15
---

# Pruebas

OpenClaw tiene tres suites de Vitest (unit/integration, e2e, live) y un pequeño conjunto de ejecutores de Docker.

Este documento es una guía de “cómo probamos”:

- Qué cubre cada suite (y qué _no_ cubre deliberadamente)
- Qué comandos ejecutar para flujos de trabajo comunes (local, antes de hacer push, depuración)
- Cómo las pruebas live descubren credenciales y seleccionan modelos/proveedores
- Cómo agregar regresiones para problemas reales de modelo/proveedor

## Inicio rápido

La mayoría de los días:

- Puerta completa (esperada antes de hacer push): `pnpm build && pnpm check && pnpm test`
- Ejecución local más rápida de la suite completa en una máquina con buenos recursos: `pnpm test:max`
- Bucle directo de observación de Vitest: `pnpm test:watch`
- El direccionamiento directo a archivos ahora también enruta rutas de extensiones/canales: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Prefiere primero ejecuciones dirigidas cuando estás iterando sobre un único fallo.
- Sitio de QA respaldado por Docker: `pnpm qa:lab:up`
- Lane de QA respaldado por VM Linux: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Cuando tocas pruebas o quieres más confianza:

- Puerta de cobertura: `pnpm test:coverage`
- Suite E2E: `pnpm test:e2e`

Cuando depuras proveedores/modelos reales (requiere credenciales reales):

- Suite live (modelos + sondas de herramientas/imágenes del gateway): `pnpm test:live`
- Dirigir silenciosamente a un archivo live: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Consejo: cuando solo necesitas un caso fallido, prefiere acotar las pruebas live mediante las variables de entorno de allowlist descritas abajo.

## Ejecutores específicos de QA

Estos comandos están junto a las suites de prueba principales cuando necesitas el realismo de qa-lab:

- `pnpm openclaw qa suite`
  - Ejecuta escenarios de QA respaldados por el repositorio directamente en el host.
- `pnpm openclaw qa suite --runner multipass`
  - Ejecuta la misma suite de QA dentro de una VM Linux desechable de Multipass.
  - Mantiene el mismo comportamiento de selección de escenarios que `qa suite` en el host.
  - Reutiliza las mismas banderas de selección de proveedor/modelo que `qa suite`.
  - Las ejecuciones live reenvían las entradas de autenticación de QA compatibles que son prácticas para el invitado:
    claves de proveedor basadas en entorno, la ruta de configuración del proveedor live de QA y `CODEX_HOME`
    cuando está presente.
  - Los directorios de salida deben permanecer bajo la raíz del repositorio para que el invitado pueda escribir de vuelta a través
    del espacio de trabajo montado.
  - Escribe el informe y el resumen normales de QA más los registros de Multipass en
    `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - Inicia el sitio de QA respaldado por Docker para trabajo de QA estilo operador.

## Suites de prueba (qué se ejecuta dónde)

Piensa en las suites como “realismo creciente” (y mayor inestabilidad/costo):

### Unit / integration (predeterminada)

- Comando: `pnpm test`
- Configuración: diez ejecuciones secuenciales por fragmentos (`vitest.full-*.config.ts`) sobre los proyectos acotados existentes de Vitest
- Archivos: inventarios core/unit en `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` y las pruebas de nodo de `ui` incluidas en la allowlist cubiertas por `vitest.unit.config.ts`
- Alcance:
  - Pruebas unitarias puras
  - Pruebas de integración en proceso (auth del gateway, enrutamiento, herramientas, análisis, configuración)
  - Regresiones deterministas para errores conocidos
- Expectativas:
  - Se ejecuta en CI
  - No requiere claves reales
  - Debe ser rápida y estable
- Nota sobre proyectos:
  - `pnpm test` sin destino ahora ejecuta once configuraciones de fragmentos más pequeñas (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) en lugar de un único proceso gigante del proyecto raíz nativo. Esto reduce el RSS máximo en máquinas cargadas y evita que el trabajo de auto-reply/extensiones deje sin recursos a suites no relacionadas.
  - `pnpm test --watch` sigue usando el grafo de proyectos raíz nativo de `vitest.config.ts`, porque un bucle de observación de múltiples fragmentos no es práctico.
  - `pnpm test`, `pnpm test:watch` y `pnpm test:perf:imports` enrutan primero los destinos explícitos de archivo/directorio mediante lanes acotados, por lo que `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` evita pagar el costo de arranque completo del proyecto raíz.
  - `pnpm test:changed` expande las rutas git modificadas en los mismos lanes acotados cuando el diff solo toca archivos de código fuente/prueba enrutable; las ediciones de configuración/setup siguen recurriendo a la reejecución amplia del proyecto raíz.
  - Algunas pruebas seleccionadas de `plugin-sdk` y `commands` también se enrutan por lanes ligeros dedicados que omiten `test/setup-openclaw-runtime.ts`; los archivos con estado o de runtime pesado permanecen en los lanes existentes.
  - Algunos archivos fuente auxiliares seleccionados de `plugin-sdk` y `commands` también asignan las ejecuciones en modo changed a pruebas hermanas explícitas en esos lanes ligeros, de modo que las ediciones auxiliares evitan reejecutar la suite pesada completa para ese directorio.
  - `auto-reply` ahora tiene tres buckets dedicados: auxiliares core de nivel superior, pruebas de integración `reply.*` de nivel superior y el subárbol `src/auto-reply/reply/**`. Esto mantiene el trabajo más pesado del arnés de respuestas fuera de las pruebas baratas de estado/fragmentos/tokens.
- Nota sobre el ejecutor integrado:
  - Cuando cambies las entradas de descubrimiento de herramientas de mensajes o el contexto de runtime de compactación,
    mantén ambos niveles de cobertura.
  - Agrega regresiones auxiliares enfocadas para límites puros de enrutamiento/normalización.
  - Mantén también saludables las suites de integración del ejecutor integrado:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` y
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Esas suites verifican que los id acotados y el comportamiento de compactación sigan fluyendo
    a través de las rutas reales `run.ts` / `compact.ts`; las pruebas solo de auxiliares no son un
    sustituto suficiente para esas rutas de integración.
- Nota sobre el pool:
  - La configuración base de Vitest ahora usa `threads` de forma predeterminada.
  - La configuración compartida de Vitest también fija `isolate: false` y usa el ejecutor no aislado en los proyectos raíz, las configuraciones e2e y live.
  - El lane UI raíz mantiene su configuración `jsdom` y optimizador, pero ahora también se ejecuta en el ejecutor compartido no aislado.
  - Cada fragmento de `pnpm test` hereda los mismos valores predeterminados `threads` + `isolate: false` de la configuración compartida de Vitest.
  - El lanzador compartido `scripts/run-vitest.mjs` ahora también agrega `--no-maglev` para los procesos Node hijos de Vitest de forma predeterminada para reducir la rotación de compilación de V8 durante grandes ejecuciones locales. Establece `OPENCLAW_VITEST_ENABLE_MAGLEV=1` si necesitas comparar con el comportamiento estándar de V8.
- Nota de iteración local rápida:
  - `pnpm test:changed` enruta mediante lanes acotados cuando las rutas modificadas se asignan claramente a una suite más pequeña.
  - `pnpm test:max` y `pnpm test:changed:max` mantienen el mismo comportamiento de enrutamiento, solo que con un límite mayor de workers.
  - El autoescalado local de workers ahora es deliberadamente conservador y también reduce la carga cuando el promedio de carga del host ya es alto, de modo que múltiples ejecuciones concurrentes de Vitest hagan menos daño de forma predeterminada.
  - La configuración base de Vitest marca los archivos de proyectos/configuración como `forceRerunTriggers` para que las reejecuciones en modo changed sigan siendo correctas cuando cambia el cableado de pruebas.
  - La configuración mantiene `OPENCLAW_VITEST_FS_MODULE_CACHE` habilitado en hosts compatibles; establece `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` si quieres una ubicación de caché explícita para perfilado directo.
- Nota de depuración de rendimiento:
  - `pnpm test:perf:imports` habilita informes de duración de importación de Vitest más salida de desglose de importaciones.
  - `pnpm test:perf:imports:changed` limita la misma vista de perfilado a los archivos modificados desde `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` compara `test:changed` enrutado con la ruta nativa del proyecto raíz para ese diff confirmado e imprime el tiempo total más el RSS máximo de macOS.
- `pnpm test:perf:changed:bench -- --worktree` evalúa el árbol de trabajo actual con cambios enrutando la lista de archivos modificados a través de `scripts/test-projects.mjs` y la configuración raíz de Vitest.
  - `pnpm test:perf:profile:main` escribe un perfil de CPU del hilo principal para la sobrecarga de arranque y transformación de Vitest/Vite.
  - `pnpm test:perf:profile:runner` escribe perfiles de CPU+heap del ejecutor para la suite unitaria con el paralelismo de archivos deshabilitado.

### E2E (smoke del gateway)

- Comando: `pnpm test:e2e`
- Configuración: `vitest.e2e.config.ts`
- Archivos: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Valores predeterminados del runtime:
  - Usa Vitest `threads` con `isolate: false`, igual que el resto del repositorio.
  - Usa workers adaptativos (CI: hasta 2, local: 1 de forma predeterminada).
  - Se ejecuta en modo silencioso de forma predeterminada para reducir la sobrecarga de E/S de consola.
- Reemplazos útiles:
  - `OPENCLAW_E2E_WORKERS=<n>` para forzar el número de workers (limitado a 16).
  - `OPENCLAW_E2E_VERBOSE=1` para volver a habilitar la salida detallada en consola.
- Alcance:
  - Comportamiento end-to-end del gateway con múltiples instancias
  - Superficies WebSocket/HTTP, emparejamiento de nodos y redes más pesadas
- Expectativas:
  - Se ejecuta en CI (cuando está habilitado en la canalización)
  - No requiere claves reales
  - Tiene más partes móviles que las pruebas unitarias (puede ser más lenta)

### E2E: smoke del backend OpenShell

- Comando: `pnpm test:e2e:openshell`
- Archivo: `test/openshell-sandbox.e2e.test.ts`
- Alcance:
  - Inicia en el host un gateway OpenShell aislado mediante Docker
  - Crea un sandbox a partir de un Dockerfile local temporal
  - Ejercita el backend OpenShell de OpenClaw sobre `sandbox ssh-config` + ejecución SSH real
  - Verifica el comportamiento canónico del sistema de archivos remoto a través del puente fs del sandbox
- Expectativas:
  - Solo opt-in; no forma parte de la ejecución predeterminada de `pnpm test:e2e`
  - Requiere un `openshell` CLI local más un daemon Docker funcional
  - Usa `HOME` / `XDG_CONFIG_HOME` aislados y luego destruye el gateway de prueba y el sandbox
- Reemplazos útiles:
  - `OPENCLAW_E2E_OPENSHELL=1` para habilitar la prueba al ejecutar manualmente la suite e2e más amplia
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` para apuntar a un binario CLI no predeterminado o a un script contenedor

### Live (proveedores reales + modelos reales)

- Comando: `pnpm test:live`
- Configuración: `vitest.live.config.ts`
- Archivos: `src/**/*.live.test.ts`
- Predeterminado: **habilitado** por `pnpm test:live` (establece `OPENCLAW_LIVE_TEST=1`)
- Alcance:
  - “¿Este proveedor/modelo realmente funciona _hoy_ con credenciales reales?”
  - Detectar cambios de formato del proveedor, peculiaridades de llamada de herramientas, problemas de auth y comportamiento de límites de tasa
- Expectativas:
  - No es estable en CI por diseño (redes reales, políticas reales de proveedores, cuotas, interrupciones)
  - Cuesta dinero / usa límites de tasa
  - Prefiere ejecutar subconjuntos acotados en lugar de “todo”
- Las ejecuciones live obtienen `~/.profile` para recoger claves de API faltantes.
- De forma predeterminada, las ejecuciones live siguen aislando `HOME` y copian el material de configuración/auth a un home temporal de prueba para que los fixtures unitarios no puedan modificar tu `~/.openclaw` real.
- Establece `OPENCLAW_LIVE_USE_REAL_HOME=1` solo cuando intencionalmente necesites que las pruebas live usen tu directorio home real.
- `pnpm test:live` ahora usa de forma predeterminada un modo más silencioso: mantiene la salida de progreso `[live] ...`, pero suprime el aviso adicional de `~/.profile` y silencia los registros de arranque del gateway/el tráfico Bonjour. Establece `OPENCLAW_LIVE_TEST_QUIET=0` si quieres recuperar los registros completos de inicio.
- Rotación de claves de API (específica por proveedor): establece `*_API_KEYS` con formato coma/punto y coma o `*_API_KEY_1`, `*_API_KEY_2` (por ejemplo `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) o una anulación por live mediante `OPENCLAW_LIVE_*_KEY`; las pruebas reintentan cuando reciben respuestas de límite de tasa.
- Salida de progreso/heartbeat:
  - Las suites live ahora emiten líneas de progreso a stderr para que las llamadas largas al proveedor se vean activas incluso cuando la captura de consola de Vitest está en modo silencioso.
  - `vitest.live.config.ts` deshabilita la interceptación de consola de Vitest para que las líneas de progreso del proveedor/gateway se transmitan inmediatamente durante las ejecuciones live.
  - Ajusta los heartbeats de modelo directo con `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Ajusta los heartbeats de gateway/sonda con `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## ¿Qué suite debo ejecutar?

Usa esta tabla de decisión:

- Editar lógica/pruebas: ejecuta `pnpm test` (y `pnpm test:coverage` si cambiaste mucho)
- Tocar redes del gateway / protocolo WS / emparejamiento: agrega `pnpm test:e2e`
- Depurar “mi bot está caído” / fallos específicos del proveedor / llamada de herramientas: ejecuta un `pnpm test:live` acotado

## Live: barrido de capacidades de nodos Android

- Prueba: `src/gateway/android-node.capabilities.live.test.ts`
- Script: `pnpm android:test:integration`
- Objetivo: invocar **cada comando anunciado actualmente** por un nodo Android conectado y afirmar el comportamiento del contrato de comandos.
- Alcance:
  - Configuración manual/preacondicionada (la suite no instala/ejecuta/empareja la app).
  - Validación `node.invoke` del gateway comando por comando para el nodo Android seleccionado.
- Configuración previa obligatoria:
  - App de Android ya conectada + emparejada con el gateway.
  - App mantenida en primer plano.
  - Permisos/consentimiento de captura concedidos para las capacidades que esperas que pasen.
- Reemplazos opcionales del objetivo:
  - `OPENCLAW_ANDROID_NODE_ID` o `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Detalles completos de la configuración de Android: [Android App](/es/platforms/android)

## Live: smoke de modelos (claves de perfil)

Las pruebas live se dividen en dos capas para que podamos aislar fallos:

- “Modelo directo” nos dice si el proveedor/modelo puede responder en absoluto con la clave dada.
- “Smoke del gateway” nos dice si toda la canalización gateway+agente funciona para ese modelo (sesiones, historial, herramientas, política de sandbox, etc.).

### Capa 1: finalización directa del modelo (sin gateway)

- Prueba: `src/agents/models.profiles.live.test.ts`
- Objetivo:
  - Enumerar los modelos detectados
  - Usar `getApiKeyForModel` para seleccionar modelos para los que tienes credenciales
  - Ejecutar una pequeña finalización por modelo (y regresiones dirigidas cuando sea necesario)
- Cómo habilitar:
  - `pnpm test:live` (o `OPENCLAW_LIVE_TEST=1` si invocas Vitest directamente)
- Establece `OPENCLAW_LIVE_MODELS=modern` (o `all`, alias de modern) para ejecutar realmente esta suite; de lo contrario, se omite para mantener `pnpm test:live` centrado en el smoke del gateway
- Cómo seleccionar modelos:
  - `OPENCLAW_LIVE_MODELS=modern` para ejecutar la allowlist moderna (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` es un alias de la allowlist moderna
  - o `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist separada por comas)
  - Los barridos modern/all usan de forma predeterminada un límite curado de alta señal; establece `OPENCLAW_LIVE_MAX_MODELS=0` para un barrido moderno exhaustivo o un número positivo para un límite más pequeño.
- Cómo seleccionar proveedores:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist separada por comas)
- De dónde salen las claves:
  - De forma predeterminada: almacenamiento de perfiles y alternativas por entorno
  - Establece `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` para exigir **solo almacenamiento de perfiles**
- Por qué existe:
  - Separa “la API del proveedor está rota / la clave no es válida” de “la canalización del agente gateway está rota”
  - Contiene regresiones pequeñas y aisladas (ejemplo: reproducción de razonamiento de OpenAI Responses/Codex Responses + flujos de llamada de herramientas)

### Capa 2: smoke del gateway + agente dev (lo que realmente hace "@openclaw")

- Prueba: `src/gateway/gateway-models.profiles.live.test.ts`
- Objetivo:
  - Iniciar un gateway en proceso
  - Crear/parchear una sesión `agent:dev:*` (reemplazo de modelo por ejecución)
  - Iterar modelos-con-claves y afirmar:
    - respuesta “significativa” (sin herramientas)
    - que funcione una invocación real de herramienta (sonda de lectura)
    - sondas opcionales de herramientas adicionales (sonda exec+read)
    - que las rutas de regresión de OpenAI (solo tool-call → seguimiento) sigan funcionando
- Detalles de las sondas (para que puedas explicar fallos rápidamente):
  - Sonda `read`: la prueba escribe un archivo nonce en el espacio de trabajo y le pide al agente que lo `read` y devuelva el nonce.
  - Sonda `exec+read`: la prueba le pide al agente que escriba un nonce en un archivo temporal con `exec` y luego lo lea de vuelta con `read`.
  - Sonda de imagen: la prueba adjunta un PNG generado (gato + código aleatorizado) y espera que el modelo devuelva `cat <CODE>`.
  - Referencia de implementación: `src/gateway/gateway-models.profiles.live.test.ts` y `src/gateway/live-image-probe.ts`.
- Cómo habilitar:
  - `pnpm test:live` (o `OPENCLAW_LIVE_TEST=1` si invocas Vitest directamente)
- Cómo seleccionar modelos:
  - Predeterminado: allowlist moderna (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` es un alias de la allowlist moderna
  - O establece `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (o una lista separada por comas) para acotar
  - Los barridos modernos/all del gateway usan de forma predeterminada un límite curado de alta señal; establece `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` para un barrido moderno exhaustivo o un número positivo para un límite más pequeño.
- Cómo seleccionar proveedores (evitar “todo OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist separada por comas)
- Las sondas de herramientas + imagen siempre están activadas en esta prueba live:
  - sonda `read` + sonda `exec+read` (estrés de herramientas)
  - la sonda de imagen se ejecuta cuando el modelo anuncia compatibilidad con entrada de imagen
  - Flujo (alto nivel):
    - La prueba genera un PNG diminuto con “CAT” + código aleatorio (`src/gateway/live-image-probe.ts`)
    - Lo envía mediante `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - El gateway analiza los adjuntos en `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - El agente integrado reenvía un mensaje de usuario multimodal al modelo
    - Afirmación: la respuesta contiene `cat` + el código (tolerancia OCR: se permiten errores menores)

Consejo: para ver qué puedes probar en tu máquina (y los id exactos `provider/model`), ejecuta:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke del backend CLI (Claude, Codex, Gemini u otros CLI locales)

- Prueba: `src/gateway/gateway-cli-backend.live.test.ts`
- Objetivo: validar la canalización Gateway + agente usando un backend CLI local, sin tocar tu configuración predeterminada.
- Los valores predeterminados de smoke específicos del backend viven con la definición `cli-backend.ts` de la extensión propietaria.
- Habilitar:
  - `pnpm test:live` (o `OPENCLAW_LIVE_TEST=1` si invocas Vitest directamente)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Predeterminados:
  - Proveedor/modelo predeterminado: `claude-cli/claude-sonnet-4-6`
  - El comportamiento de comando/args/imagen proviene de los metadatos del plugin propietario del backend CLI.
- Reemplazos opcionales:
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` para enviar un adjunto de imagen real (las rutas se inyectan en el prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` para pasar rutas de archivos de imagen como args de CLI en lugar de inyección en el prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (o `"list"`) para controlar cómo se pasan los args de imagen cuando `IMAGE_ARG` está establecido.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` para enviar un segundo turno y validar el flujo de reanudación.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` para deshabilitar la sonda predeterminada de continuidad en la misma sesión Claude Sonnet -> Opus (establece `1` para forzarla cuando el modelo seleccionado admita un destino de cambio).

Ejemplo:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Receta de Docker:

```bash
pnpm test:docker:live-cli-backend
```

Recetas de Docker de proveedor único:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Notas:

- El ejecutor de Docker está en `scripts/test-live-cli-backend-docker.sh`.
- Ejecuta el smoke live del backend CLI dentro de la imagen Docker del repositorio como el usuario no root `node`.
- Resuelve los metadatos del smoke CLI desde la extensión propietaria y luego instala el paquete CLI Linux correspondiente (`@anthropic-ai/claude-code`, `@openai/codex` o `@google/gemini-cli`) en un prefijo escribible con caché en `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (predeterminado: `~/.cache/openclaw/docker-cli-tools`).
- El smoke live del backend CLI ahora ejercita el mismo flujo end-to-end para Claude, Codex y Gemini: turno de texto, turno de clasificación de imagen y luego llamada a la herramienta MCP `cron` verificada a través del CLI del gateway.
- El smoke predeterminado de Claude también parchea la sesión de Sonnet a Opus y verifica que la sesión reanudada siga recordando una nota anterior.

## Live: smoke de enlace ACP (`/acp spawn ... --bind here`)

- Prueba: `src/gateway/gateway-acp-bind.live.test.ts`
- Objetivo: validar el flujo real de conversation-bind de ACP con un agente ACP live:
  - enviar `/acp spawn <agent> --bind here`
  - enlazar en sitio una conversación sintética de canal de mensajes
  - enviar un seguimiento normal en esa misma conversación
  - verificar que el seguimiento llegue a la transcripción de la sesión ACP enlazada
- Habilitar:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Predeterminados:
  - Agentes ACP en Docker: `claude,codex,gemini`
  - Agente ACP para `pnpm test:live ...` directo: `claude`
  - Canal sintético: contexto de conversación estilo DM de Slack
  - Backend ACP: `acpx`
- Reemplazos:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Notas:
  - Este lane usa la superficie `chat.send` del gateway con campos sintéticos de ruta de origen solo para administradores para que las pruebas puedan adjuntar contexto de canal de mensajes sin fingir una entrega externa.
  - Cuando `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` no está establecido, la prueba usa el registro integrado de agentes del plugin `acpx` incrustado para el agente de arnés ACP seleccionado.

Ejemplo:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Receta de Docker:

```bash
pnpm test:docker:live-acp-bind
```

Recetas de Docker de agente único:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Notas de Docker:

- El ejecutor de Docker está en `scripts/test-live-acp-bind-docker.sh`.
- De forma predeterminada, ejecuta el smoke de enlace ACP contra todos los agentes CLI live compatibles en secuencia: `claude`, `codex` y luego `gemini`.
- Usa `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` o `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` para acotar la matriz.
- Obtiene `~/.profile`, prepara en el contenedor el material de auth CLI correspondiente, instala `acpx` en un prefijo npm escribible y luego instala el CLI live solicitado (`@anthropic-ai/claude-code`, `@openai/codex` o `@google/gemini-cli`) si falta.
- Dentro de Docker, el ejecutor establece `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` para que acpx mantenga disponibles para el CLI hijo del arnés las variables de entorno del proveedor obtenidas desde el perfil cargado.

### Recetas live recomendadas

Las allowlists acotadas y explícitas son las más rápidas y las menos inestables:

- Un solo modelo, directo (sin gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Un solo modelo, smoke del gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Llamada de herramientas en varios proveedores:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Enfoque en Google (clave de API de Gemini + Antigravity):
  - Gemini (clave de API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Notas:

- `google/...` usa la API de Gemini (clave de API).
- `google-antigravity/...` usa el puente OAuth de Antigravity (endpoint de agente estilo Cloud Code Assist).
- `google-gemini-cli/...` usa el CLI local de Gemini en tu máquina (auth separada + peculiaridades propias de herramientas).
- API de Gemini vs CLI de Gemini:
  - API: OpenClaw llama a la API alojada de Gemini de Google por HTTP (clave de API / auth de perfil); esto es lo que la mayoría de los usuarios quiere decir con “Gemini”.
  - CLI: OpenClaw ejecuta un binario local `gemini`; tiene su propia auth y puede comportarse de forma distinta (streaming/soporte de herramientas/desfase de versión).

## Live: matriz de modelos (lo que cubrimos)

No hay una “lista fija de modelos de CI” (live es opt-in), pero estos son los modelos **recomendados** para cubrir regularmente en una máquina de desarrollo con claves.

### Conjunto smoke moderno (llamada de herramientas + imagen)

Esta es la ejecución de “modelos comunes” que esperamos mantener funcionando:

- OpenAI (no-Codex): `openai/gpt-5.4` (opcional: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (o `anthropic/claude-sonnet-4-6`)
- Google (API de Gemini): `google/gemini-3.1-pro-preview` y `google/gemini-3-flash-preview` (evita modelos Gemini 2.x más antiguos)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` y `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Ejecuta el smoke del gateway con herramientas + imagen:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Línea base: llamada de herramientas (Read + Exec opcional)

Elige al menos uno por familia de proveedores:

- OpenAI: `openai/gpt-5.4` (o `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (o `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (o `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Cobertura adicional opcional (conveniente tenerla):

- xAI: `xai/grok-4` (o la última disponible)
- Mistral: `mistral/`… (elige un modelo con capacidad de “tools” que tengas habilitado)
- Cerebras: `cerebras/`… (si tienes acceso)
- LM Studio: `lmstudio/`… (local; la llamada de herramientas depende del modo de API)

### Vision: envío de imagen (adjunto → mensaje multimodal)

Incluye al menos un modelo con capacidad de imagen en `OPENCLAW_LIVE_GATEWAY_MODELS` (variantes de Claude/Gemini/OpenAI con capacidad de visión, etc.) para ejercitar la sonda de imagen.

### Agregadores / gateways alternativos

Si tienes claves habilitadas, también admitimos pruebas mediante:

- OpenRouter: `openrouter/...` (cientos de modelos; usa `openclaw models scan` para encontrar candidatos con capacidad de herramientas+imagen)
- OpenCode: `opencode/...` para Zen y `opencode-go/...` para Go (auth mediante `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Más proveedores que puedes incluir en la matriz live (si tienes credenciales/configuración):

- Integrados: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Mediante `models.providers` (endpoints personalizados): `minimax` (cloud/API), más cualquier proxy compatible con OpenAI/Anthropic (LM Studio, vLLM, LiteLLM, etc.)

Consejo: no intentes codificar “todos los modelos” en la documentación. La lista autorizada es lo que devuelva `discoverModels(...)` en tu máquina + las claves que estén disponibles.

## Credenciales (nunca hacer commit)

Las pruebas live descubren credenciales de la misma forma que el CLI. Implicaciones prácticas:

- Si el CLI funciona, las pruebas live deberían encontrar las mismas claves.
- Si una prueba live dice “no creds”, depúralo igual que depurarías `openclaw models list` / selección de modelo.

- Perfiles de auth por agente: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (esto es lo que significa “profile keys” en las pruebas live)
- Configuración: `~/.openclaw/openclaw.json` (o `OPENCLAW_CONFIG_PATH`)
- Directorio de estado heredado: `~/.openclaw/credentials/` (se copia al home live preparado cuando está presente, pero no es el almacenamiento principal de claves de perfil)
- Las ejecuciones live locales copian de forma predeterminada la configuración activa, los archivos `auth-profiles.json` por agente, el directorio heredado `credentials/` y los directorios de auth CLI externos compatibles a un home temporal de prueba; los homes live preparados omiten `workspace/` y `sandboxes/`, y se eliminan las anulaciones de ruta `agents.*.workspace` / `agentDir` para que las sondas no usen tu espacio de trabajo real del host.

Si quieres basarte en claves de entorno (por ejemplo, exportadas en tu `~/.profile`), ejecuta las pruebas locales después de `source ~/.profile`, o usa los ejecutores de Docker de abajo (pueden montar `~/.profile` dentro del contenedor).

## Deepgram live (transcripción de audio)

- Prueba: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Habilitar: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- Prueba: `src/agents/byteplus.live.test.ts`
- Habilitar: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Reemplazo opcional de modelo: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- Prueba: `extensions/comfy/comfy.live.test.ts`
- Habilitar: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Alcance:
  - Ejercita las rutas de imagen, video y `music_generate` del paquete comfy integrado
  - Omite cada capacidad salvo que `models.providers.comfy.<capability>` esté configurado
  - Útil después de cambiar el envío de flujos de trabajo comfy, el polling, las descargas o el registro del plugin

## Image generation live

- Prueba: `src/image-generation/runtime.live.test.ts`
- Comando: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Arnés: `pnpm test:live:media image`
- Alcance:
  - Enumera cada plugin de proveedor de generación de imágenes registrado
  - Carga variables de entorno faltantes del proveedor desde tu shell de inicio de sesión (`~/.profile`) antes de sondear
  - Usa de forma predeterminada claves de API live/de entorno antes que perfiles de auth almacenados, para que claves de prueba obsoletas en `auth-profiles.json` no oculten credenciales reales del shell
  - Omite proveedores sin auth/perfil/modelo utilizable
  - Ejecuta las variantes estándar de generación de imágenes mediante la capacidad compartida de runtime:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Proveedores integrados cubiertos actualmente:
  - `openai`
  - `google`
- Acotación opcional:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Comportamiento opcional de auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` para forzar la auth del almacén de perfiles e ignorar las anulaciones solo de entorno

## Music generation live

- Prueba: `extensions/music-generation-providers.live.test.ts`
- Habilitar: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Arnés: `pnpm test:live:media music`
- Alcance:
  - Ejercita la ruta compartida integrada de proveedores de generación musical
  - Actualmente cubre Google y MiniMax
  - Carga variables de entorno del proveedor desde tu shell de inicio de sesión (`~/.profile`) antes de sondear
  - Usa de forma predeterminada claves de API live/de entorno antes que perfiles de auth almacenados, para que claves de prueba obsoletas en `auth-profiles.json` no oculten credenciales reales del shell
  - Omite proveedores sin auth/perfil/modelo utilizable
  - Ejecuta ambos modos de runtime declarados cuando están disponibles:
    - `generate` con entrada solo de prompt
    - `edit` cuando el proveedor declara `capabilities.edit.enabled`
  - Cobertura actual del carril compartido:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: archivo live de Comfy separado, no este barrido compartido
- Acotación opcional:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Comportamiento opcional de auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` para forzar la auth del almacén de perfiles e ignorar las anulaciones solo de entorno

## Video generation live

- Prueba: `extensions/video-generation-providers.live.test.ts`
- Habilitar: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Arnés: `pnpm test:live:media video`
- Alcance:
  - Ejercita la ruta compartida integrada de proveedores de generación de video
  - Carga variables de entorno del proveedor desde tu shell de inicio de sesión (`~/.profile`) antes de sondear
  - Usa de forma predeterminada claves de API live/de entorno antes que perfiles de auth almacenados, para que claves de prueba obsoletas en `auth-profiles.json` no oculten credenciales reales del shell
  - Omite proveedores sin auth/perfil/modelo utilizable
  - Ejecuta ambos modos de runtime declarados cuando están disponibles:
    - `generate` con entrada solo de prompt
    - `imageToVideo` cuando el proveedor declara `capabilities.imageToVideo.enabled` y el proveedor/modelo seleccionado acepta entrada de imagen local basada en búfer en el barrido compartido
    - `videoToVideo` cuando el proveedor declara `capabilities.videoToVideo.enabled` y el proveedor/modelo seleccionado acepta entrada de video local basada en búfer en el barrido compartido
  - Proveedores `imageToVideo` declarados actualmente pero omitidos en el barrido compartido:
    - `vydra` porque el `veo3` integrado es solo texto y el `kling` integrado requiere una URL de imagen remota
  - Cobertura específica de proveedor para Vydra:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - ese archivo ejecuta `veo3` de texto a video más un carril `kling` que usa de forma predeterminada un fixture de URL de imagen remota
  - Cobertura live actual de `videoToVideo`:
    - solo `runway` cuando el modelo seleccionado es `runway/gen4_aleph`
  - Proveedores `videoToVideo` declarados actualmente pero omitidos en el barrido compartido:
    - `alibaba`, `qwen`, `xai` porque esas rutas actualmente requieren URLs de referencia remotas `http(s)` / MP4
    - `google` porque el carril compartido actual Gemini/Veo usa entrada local basada en búfer y esa ruta no se acepta en el barrido compartido
    - `openai` porque el carril compartido actual carece de garantías de acceso específicas de la organización para inpaint/remix de video
- Acotación opcional:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- Comportamiento opcional de auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` para forzar la auth del almacén de perfiles e ignorar las anulaciones solo de entorno

## Arnés live de medios

- Comando: `pnpm test:live:media`
- Propósito:
  - Ejecuta las suites live compartidas de imagen, música y video a través de un único punto de entrada nativo del repositorio
  - Carga automáticamente variables de entorno faltantes del proveedor desde `~/.profile`
  - Acota automáticamente cada suite a los proveedores que actualmente tienen auth utilizable de forma predeterminada
  - Reutiliza `scripts/test-live.mjs`, de modo que el comportamiento de heartbeat y modo silencioso siga siendo consistente
- Ejemplos:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Ejecutores de Docker (comprobaciones opcionales de "funciona en Linux")

Estos ejecutores de Docker se dividen en dos grupos:

- Ejecutores live de modelos: `test:docker:live-models` y `test:docker:live-gateway` ejecutan solo su archivo live de claves de perfil correspondiente dentro de la imagen Docker del repositorio (`src/agents/models.profiles.live.test.ts` y `src/gateway/gateway-models.profiles.live.test.ts`), montando tu directorio local de configuración y espacio de trabajo (y obteniendo `~/.profile` si está montado). Los puntos de entrada locales correspondientes son `test:live:models-profiles` y `test:live:gateway-profiles`.
- Los ejecutores Docker live usan de forma predeterminada un límite smoke más pequeño para que un barrido completo en Docker siga siendo práctico:
  `test:docker:live-models` usa por defecto `OPENCLAW_LIVE_MAX_MODELS=12`, y
  `test:docker:live-gateway` usa por defecto `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` y
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Anula esas variables de entorno cuando
  quieras explícitamente el barrido exhaustivo más grande.
- `test:docker:all` compila una vez la imagen Docker live mediante `test:docker:live-build`, y luego la reutiliza para los dos lanes Docker live.
- Ejecutores smoke de contenedor: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` y `test:docker:plugins` inician uno o más contenedores reales y verifican rutas de integración de nivel superior.

Los ejecutores Docker live de modelos también montan mediante bind solo los homes de auth CLI necesarios (o todos los compatibles cuando la ejecución no está acotada), y luego los copian al home del contenedor antes de la ejecución para que el OAuth de CLI externa pueda refrescar tokens sin modificar el almacén de auth del host:

- Modelos directos: `pnpm test:docker:live-models` (script: `scripts/test-live-models-docker.sh`)
- Smoke de enlace ACP: `pnpm test:docker:live-acp-bind` (script: `scripts/test-live-acp-bind-docker.sh`)
- Smoke del backend CLI: `pnpm test:docker:live-cli-backend` (script: `scripts/test-live-cli-backend-docker.sh`)
- Gateway + agente dev: `pnpm test:docker:live-gateway` (script: `scripts/test-live-gateway-models-docker.sh`)
- Smoke live de Open WebUI: `pnpm test:docker:openwebui` (script: `scripts/e2e/openwebui-docker.sh`)
- Asistente de onboarding (TTY, andamiaje completo): `pnpm test:docker:onboard` (script: `scripts/e2e/onboard-docker.sh`)
- Redes del gateway (dos contenedores, auth WS + salud): `pnpm test:docker:gateway-network` (script: `scripts/e2e/gateway-network-docker.sh`)
- Puente de canal MCP (Gateway sembrado + puente stdio + smoke sin procesar de marcos de notificación Claude): `pnpm test:docker:mcp-channels` (script: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (smoke de instalación + alias `/plugin` + semántica de reinicio del paquete Claude): `pnpm test:docker:plugins` (script: `scripts/e2e/plugins-docker.sh`)

Los ejecutores Docker live de modelos también montan mediante bind la extracción actual en modo de solo lectura y
la preparan en un directorio temporal de trabajo dentro del contenedor. Esto mantiene ligera la imagen de runtime
aunque sigue ejecutando Vitest contra tu código fuente/configuración local exactos.
El paso de preparación omite grandes cachés solo locales y salidas de compilación de la app como
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` y directorios de salida Gradle o `.build` locales de la app para que las ejecuciones
live de Docker no pasen minutos copiando artefactos específicos de la máquina.
También establecen `OPENCLAW_SKIP_CHANNELS=1` para que las sondas live del gateway no inicien
workers reales de canales Telegram/Discord/etc. dentro del contenedor.
`test:docker:live-models` sigue ejecutando `pnpm test:live`, así que pasa también
`OPENCLAW_LIVE_GATEWAY_*` cuando necesites acotar o excluir la cobertura
live del gateway de ese lane Docker.
`test:docker:openwebui` es un smoke de compatibilidad de nivel superior: inicia un
contenedor gateway de OpenClaw con los endpoints HTTP compatibles con OpenAI habilitados,
inicia un contenedor fijado de Open WebUI contra ese gateway, inicia sesión a través de
Open WebUI, verifica que `/api/models` expone `openclaw/default`, y luego envía una
solicitud de chat real mediante el proxy `/api/chat/completions` de Open WebUI.
La primera ejecución puede ser notablemente más lenta porque Docker puede necesitar descargar la
imagen de Open WebUI y Open WebUI puede necesitar completar su propia configuración de arranque en frío.
Este lane espera una clave de modelo live utilizable, y `OPENCLAW_PROFILE_FILE`
(`~/.profile` de forma predeterminada) es la forma principal de proporcionarla en ejecuciones dockerizadas.
Las ejecuciones exitosas imprimen una pequeña carga JSON como `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` es intencionalmente determinista y no necesita una
cuenta real de Telegram, Discord o iMessage. Inicia un contenedor Gateway
sembrado, inicia un segundo contenedor que ejecuta `openclaw mcp serve`, y luego
verifica el descubrimiento de conversaciones enrutadas, lecturas de transcripción, metadatos de adjuntos,
comportamiento de cola de eventos live, enrutamiento de envíos salientes y notificaciones
de canal + permisos al estilo Claude sobre el puente MCP stdio real. La comprobación de notificaciones
inspecciona directamente los marcos MCP stdio sin procesar, de modo que el smoke valida lo que
el puente realmente emite, no solo lo que una SDK cliente específica casualmente expone.

Smoke manual de hilo ACP en lenguaje natural (no CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Conserva este script para flujos de regresión/depuración. Puede volver a ser necesario para validar el enrutamiento de hilos ACP, así que no lo elimines.

Variables de entorno útiles:

- `OPENCLAW_CONFIG_DIR=...` (predeterminado: `~/.openclaw`) montado en `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (predeterminado: `~/.openclaw/workspace`) montado en `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (predeterminado: `~/.profile`) montado en `/home/node/.profile` y obtenido antes de ejecutar las pruebas
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (predeterminado: `~/.cache/openclaw/docker-cli-tools`) montado en `/home/node/.npm-global` para instalaciones de CLI en caché dentro de Docker
- Los directorios/archivos de auth CLI externa bajo `$HOME` se montan en solo lectura bajo `/host-auth...`, y luego se copian a `/home/node/...` antes de que empiecen las pruebas
  - Directorios predeterminados: `.minimax`
  - Archivos predeterminados: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Las ejecuciones de proveedor acotado montan solo los directorios/archivos necesarios inferidos de `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Anula manualmente con `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` o una lista separada por comas como `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` para acotar la ejecución
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` para filtrar proveedores dentro del contenedor
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` para garantizar que las credenciales provengan del almacén de perfiles (no del entorno)
- `OPENCLAW_OPENWEBUI_MODEL=...` para elegir el modelo expuesto por el gateway para el smoke de Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...` para anular el prompt de comprobación nonce usado por el smoke de Open WebUI
- `OPENWEBUI_IMAGE=...` para anular la etiqueta fijada de imagen de Open WebUI

## Cordura de la documentación

Ejecuta las comprobaciones de documentación después de editar documentación: `pnpm check:docs`.
Ejecuta la validación completa de anclas de Mintlify cuando también necesites comprobaciones de encabezados dentro de la página: `pnpm docs:check-links:anchors`.

## Regresión offline (segura para CI)

Estas son regresiones de “canalización real” sin proveedores reales:

- Llamada de herramientas del gateway (OpenAI simulado, gateway real + bucle de agente): `src/gateway/gateway.test.ts` (caso: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Asistente del gateway (WS `wizard.start`/`wizard.next`, escribe configuración + auth forzada): `src/gateway/gateway.test.ts` (caso: "runs wizard over ws and writes auth token config")

## Evaluaciones de confiabilidad del agente (Skills)

Ya tenemos algunas pruebas seguras para CI que se comportan como “evaluaciones de confiabilidad del agente”:

- Llamada de herramientas simulada a través del gateway real + bucle de agente (`src/gateway/gateway.test.ts`).
- Flujos end-to-end del asistente que validan el cableado de la sesión y los efectos de configuración (`src/gateway/gateway.test.ts`).

Lo que aún falta para Skills (ver [Skills](/es/tools/skills)):

- **Toma de decisiones:** cuando las Skills aparecen en el prompt, ¿el agente elige la Skill correcta (o evita las irrelevantes)?
- **Cumplimiento:** ¿el agente lee `SKILL.md` antes de usarla y sigue los pasos/args requeridos?
- **Contratos de flujo de trabajo:** escenarios de varios turnos que afirman el orden de herramientas, el arrastre del historial de sesión y los límites del sandbox.

Las evaluaciones futuras deberían seguir siendo deterministas primero:

- Un ejecutor de escenarios que use proveedores simulados para afirmar llamadas de herramientas + orden, lecturas de archivos de Skill y cableado de sesión.
- Una pequeña suite de escenarios centrados en Skills (usar vs evitar, gating, inyección de prompt).
- Evaluaciones live opcionales (opt-in, controladas por entorno) solo después de que la suite segura para CI ya esté implementada.

## Pruebas de contrato (forma de plugin y canal)

Las pruebas de contrato verifican que cada plugin y canal registrado se ajuste a su
contrato de interfaz. Iteran sobre todos los plugins detectados y ejecutan una suite de
afirmaciones de forma y comportamiento. El lane unitario predeterminado `pnpm test`
omite intencionalmente estos archivos compartidos de seams y smoke; ejecuta los comandos de contrato explícitamente
cuando toques superficies compartidas de canal o proveedor.

### Comandos

- Todos los contratos: `pnpm test:contracts`
- Solo contratos de canal: `pnpm test:contracts:channels`
- Solo contratos de proveedor: `pnpm test:contracts:plugins`

### Contratos de canal

Ubicados en `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Forma básica del plugin (id, nombre, capacidades)
- **setup** - Contrato del asistente de configuración
- **session-binding** - Comportamiento de enlace de sesión
- **outbound-payload** - Estructura de carga de mensaje
- **inbound** - Manejo de mensajes entrantes
- **actions** - Manejadores de acciones de canal
- **threading** - Manejo de ID de hilo
- **directory** - API de directorio/lista
- **group-policy** - Aplicación de la política de grupo

### Contratos de estado del proveedor

Ubicados en `src/plugins/contracts/*.contract.test.ts`.

- **status** - Sondas de estado del canal
- **registry** - Forma del registro de plugins

### Contratos de proveedor

Ubicados en `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Contrato de flujo de auth
- **auth-choice** - Elección/selección de auth
- **catalog** - API de catálogo de modelos
- **discovery** - Detección de plugins
- **loader** - Carga de plugins
- **runtime** - Runtime del proveedor
- **shape** - Forma/interfaz del plugin
- **wizard** - Asistente de configuración

### Cuándo ejecutarlas

- Después de cambiar exportaciones o subrutas de plugin-sdk
- Después de agregar o modificar un plugin de canal o proveedor
- Después de refactorizar el registro o la detección de plugins

Las pruebas de contrato se ejecutan en CI y no requieren claves de API reales.

## Agregar regresiones (guía)

Cuando corrijas un problema de proveedor/modelo descubierto en live:

- Agrega una regresión segura para CI si es posible (proveedor simulado/stub, o captura de la transformación exacta de la forma de la solicitud)
- Si es inherentemente solo live (límites de tasa, políticas de auth), mantén la prueba live acotada y opt-in mediante variables de entorno
- Prefiere dirigirte a la capa más pequeña que detecte el error:
  - error de conversión/reproducción de solicitud del proveedor → prueba de modelos directos
  - error de la canalización de sesión/historial/herramientas del gateway → smoke live del gateway o prueba simulada del gateway segura para CI
- Barandilla de recorrido de SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` deriva un objetivo de muestra por clase SecretRef a partir de los metadatos del registro (`listSecretTargetRegistryEntries()`), y luego afirma que se rechazan los id exec de segmento de recorrido.
  - Si agregas una nueva familia de objetivos SecretRef `includeInPlan` en `src/secrets/target-registry-data.ts`, actualiza `classifyTargetClass` en esa prueba. La prueba falla intencionalmente con id de objetivo no clasificados para que las clases nuevas no puedan omitirse en silencio.
