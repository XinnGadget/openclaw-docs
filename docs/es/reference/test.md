---
read_when:
    - Ejecutar o corregir pruebas
summary: Cómo ejecutar pruebas localmente (vitest) y cuándo usar los modos force/coverage
title: Pruebas
x-i18n:
    generated_at: "2026-04-07T05:06:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: a25236a707860307cc324f32752ad13a53e448bee9341d8df2e11655561e841c
    source_path: reference/test.md
    workflow: 15
---

# Pruebas

- Kit completo de pruebas (suites, live, Docker): [Testing](/es/help/testing)

- `pnpm test:force`: finaliza cualquier proceso de gateway persistente que mantenga ocupado el puerto de control predeterminado y luego ejecuta la suite completa de Vitest con un puerto de gateway aislado para que las pruebas del servidor no colisionen con una instancia en ejecución. Úsalo cuando una ejecución anterior del gateway haya dejado ocupado el puerto 18789.
- `pnpm test:coverage`: ejecuta la suite unitaria con cobertura de V8 (mediante `vitest.unit.config.ts`). Los umbrales globales son 70% de líneas/ramas/funciones/sentencias. La cobertura excluye entrypoints con mucha integración (cableado de CLI, puentes de gateway/Telegram, servidor estático de webchat) para mantener el objetivo centrado en lógica comprobable mediante pruebas unitarias.
- `pnpm test:coverage:changed`: ejecuta cobertura unitaria solo para los archivos modificados desde `origin/main`.
- `pnpm test:changed`: expande las rutas de git modificadas en lanes acotados de Vitest cuando el diff solo toca archivos de origen/prueba enrutable. Los cambios de configuración/setup siguen recurriendo a la ejecución nativa del proyecto raíz para que las ediciones de cableado vuelvan a ejecutarse ampliamente cuando sea necesario.
- `pnpm test`: enruta objetivos explícitos de archivo/directorio a través de lanes acotados de Vitest. Las ejecuciones sin objetivo ahora ejecutan diez configuraciones de shards secuenciales (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`) en lugar de un único proceso gigante del proyecto raíz.
- Los archivos de prueba seleccionados de `plugin-sdk` y `commands` ahora se enrutan mediante lanes ligeros dedicados que conservan solo `test/setup.ts`, dejando los casos pesados de tiempo de ejecución en sus lanes existentes.
- Los archivos fuente auxiliares seleccionados de `plugin-sdk` y `commands` también asignan `pnpm test:changed` a pruebas hermanas explícitas en esos lanes ligeros, para que ediciones pequeñas en helpers eviten volver a ejecutar las suites pesadas respaldadas por tiempo de ejecución.
- `auto-reply` ahora también se divide en tres configuraciones dedicadas (`core`, `top-level`, `reply`) para que el arnés de respuesta no domine las pruebas más ligeras de estado/token/helper de nivel superior.
- La configuración base de Vitest ahora usa por defecto `pool: "threads"` e `isolate: false`, con el ejecutor compartido no aislado habilitado en todas las configuraciones del repositorio.
- `pnpm test:channels` ejecuta `vitest.channels.config.ts`.
- `pnpm test:extensions` ejecuta `vitest.extensions.config.ts`.
- `pnpm test:extensions`: ejecuta suites de extensiones/plugins.
- `pnpm test:perf:imports`: habilita la generación de informes de duración de importación + desglose de importaciones en Vitest, a la vez que sigue usando el enrutamiento por lanes acotados para objetivos explícitos de archivo/directorio.
- `pnpm test:perf:imports:changed`: el mismo perfilado de importaciones, pero solo para archivos modificados desde `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` compara mediante benchmark la ruta en modo changed enrutada con la ejecución nativa del proyecto raíz para el mismo diff de git ya confirmado.
- `pnpm test:perf:changed:bench -- --worktree` compara mediante benchmark el conjunto de cambios actual del worktree sin confirmarlo primero.
- `pnpm test:perf:profile:main`: escribe un perfil de CPU para el hilo principal de Vitest (`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: escribe perfiles de CPU + heap para el ejecutor unitario (`.artifacts/vitest-runner-profile`).
- Integración de Gateway: activación opcional mediante `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` o `pnpm test:gateway`.
- `pnpm test:e2e`: ejecuta pruebas smoke end-to-end del gateway (emparejamiento WS/HTTP/nodo multiinstancia). Usa por defecto `threads` + `isolate: false` con trabajadores adaptativos en `vitest.e2e.config.ts`; ajústalo con `OPENCLAW_E2E_WORKERS=<n>` y establece `OPENCLAW_E2E_VERBOSE=1` para registros detallados.
- `pnpm test:live`: ejecuta pruebas live de proveedores (minimax/zai). Requiere claves de API y `LIVE=1` (o `*_LIVE_TEST=1` específico del proveedor) para dejar de omitirlas.
- `pnpm test:docker:openwebui`: inicia OpenClaw + Open WebUI en Docker, inicia sesión a través de Open WebUI, comprueba `/api/models` y luego ejecuta un chat real con proxy a través de `/api/chat/completions`. Requiere una clave de modelo live utilizable (por ejemplo OpenAI en `~/.profile`), extrae una imagen externa de Open WebUI y no se espera que sea estable en CI como las suites normales unitarias/e2e.
- `pnpm test:docker:mcp-channels`: inicia un contenedor de Gateway sembrado y un segundo contenedor cliente que lanza `openclaw mcp serve`, luego verifica el descubrimiento de conversaciones enrutadas, lecturas de transcripciones, metadatos de adjuntos, comportamiento live de la cola de eventos, enrutamiento de envío saliente y notificaciones de canal + permisos de estilo Claude sobre el puente stdio real. La aserción de notificación de Claude lee directamente los frames MCP stdio sin procesar para que la prueba smoke refleje lo que realmente emite el puente.

## Puerta local de PR

Para comprobaciones locales de aterrizaje/puerta de PR, ejecuta:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

Si `pnpm test` falla de forma intermitente en un host cargado, vuelve a ejecutarlo una vez antes de tratarlo como una regresión, y luego aíslalo con `pnpm test <path/to/test>`. Para hosts con memoria limitada, usa:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## Benchmark de latencia de modelo (claves locales)

Script: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

Uso:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- Entorno opcional: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- Prompt predeterminado: “Responde con una sola palabra: ok. Sin puntuación ni texto adicional.”

Última ejecución (2025-12-31, 20 ejecuciones):

- median minimax 1279ms (mín 1114, máx 2431)
- median opus 2454ms (mín 1224, máx 3170)

## Benchmark de inicio de CLI

Script: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

Uso:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist/entry.js --preset all`
- `pnpm tsx scripts/bench-cli-startup.ts --preset all --output .artifacts/cli-startup-bench-all.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case gatewayStatusJson --output .artifacts/cli-startup-bench-smoke.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --cpu-prof-dir .artifacts/cli-cpu`
- `pnpm tsx scripts/bench-cli-startup.ts --json`

Preajustes:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: ambos preajustes

La salida incluye `sampleCount`, avg, p50, p95, distribución de mín/máx, exit-code/signal y resúmenes de RSS máximo para cada comando. `--cpu-prof-dir` / `--heap-prof-dir` opcionales escriben perfiles V8 por ejecución para que la medición de tiempo y la captura de perfiles usen el mismo arnés.

Convenciones de salida guardada:

- `pnpm test:startup:bench:smoke` escribe el artefacto smoke objetivo en `.artifacts/cli-startup-bench-smoke.json`
- `pnpm test:startup:bench:save` escribe el artefacto de la suite completa en `.artifacts/cli-startup-bench-all.json` usando `runs=5` y `warmup=1`
- `pnpm test:startup:bench:update` actualiza el fixture de referencia versionado en `test/fixtures/cli-startup-bench.json` usando `runs=5` y `warmup=1`

Fixture versionado:

- `test/fixtures/cli-startup-bench.json`
- Actualízalo con `pnpm test:startup:bench:update`
- Compara los resultados actuales con el fixture mediante `pnpm test:startup:bench:check`

## E2E de incorporación (Docker)

Docker es opcional; esto solo se necesita para pruebas smoke de incorporación en contenedores.

Flujo completo de arranque en frío en un contenedor Linux limpio:

```bash
scripts/e2e/onboard-docker.sh
```

Este script controla el asistente interactivo mediante un pseudo-TTY, verifica archivos de configuración/espacio de trabajo/sesión y luego inicia el gateway y ejecuta `openclaw health`.

## Prueba smoke de importación de QR (Docker)

Garantiza que `qrcode-terminal` se cargue bajo los runtimes Node compatibles de Docker (Node 24 predeterminado, Node 22 compatible):

```bash
pnpm test:docker:qr
```
