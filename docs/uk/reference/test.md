---
read_when:
    - Запуск або виправлення тестів
summary: Як локально запускати тести (vitest) і коли використовувати режими force/coverage
title: Тести
x-i18n:
    generated_at: "2026-04-06T18:33:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: c79db92c10593192ba95b199dad3b5eae3da1a2e6b873e5ed124839f4f72050c
    source_path: reference/test.md
    workflow: 15
---

# Тести

- Повний набір для тестування (набори, live, Docker): [Тестування](/uk/help/testing)

- `pnpm test:force`: Завершує будь-який завислий процес gateway, який утримує типовий control port, а потім запускає повний набір Vitest з ізольованим портом gateway, щоб серверні тести не конфліктували із запущеним екземпляром. Використовуйте це, якщо попередній запуск gateway залишив порт 18789 зайнятим.
- `pnpm test:coverage`: Запускає набір unit-тестів із покриттям V8 (через `vitest.unit.config.ts`). Глобальні пороги становлять 70% для рядків/гілок/функцій/інструкцій. Із покриття виключено entrypoint-и з великою інтеграційною складовою (обв’язка CLI, мости gateway/telegram, статичний сервер webchat), щоб зосередити ціль на логіці, придатній для unit-тестування.
- `pnpm test:coverage:changed`: Запускає unit coverage лише для файлів, змінених відносно `origin/main`.
- `pnpm test:changed`: розгортає змінені git-шляхи в scoped lanes Vitest, коли diff торкається лише routable файлів source/test. Зміни config/setup, як і раніше, повертаються до нативного запуску root projects, щоб за потреби зміни в обв’язці перезапускали ширший набір.
- `pnpm test`: спрямовує явні цілі файлів/каталогів через scoped lanes Vitest. Нетаргетовані запуски тепер виконують вісім послідовних shard configs (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`) замість одного великого процесу root-project.
- Вибрані тестові файли `plugin-sdk` і `commands` тепер спрямовуються через окремі легкі lanes, які залишають тільки `test/setup.ts`, а runtime-важкі сценарії лишаються у своїх наявних lanes.
- Вибрані допоміжні source-файли `plugin-sdk` і `commands` також зіставляють `pnpm test:changed` з явними sibling-тестами у цих легких lanes, тож невеликі зміни допоміжних файлів не змушують повторно запускати важкі набори з підтримкою runtime.
- `auto-reply` тепер також поділено на три окремі configs (`core`, `top-level`, `reply`), тож harness reply більше не домінує над легшими top-level тестами status/token/helper.
- Базова config Vitest тепер типово використовує `pool: "threads"` та `isolate: false`, а спільний non-isolated runner увімкнено в усіх configs репозиторію.
- `pnpm test:channels` запускає `vitest.channels.config.ts`.
- `pnpm test:extensions` запускає `vitest.extensions.config.ts`.
- `pnpm test:extensions`: запускає набори extension/plugin.
- `pnpm test:perf:imports`: вмикає звітування Vitest про тривалість імпорту та деталізацію імпорту, і водночас продовжує використовувати scoped lane routing для явних цілей файлів/каталогів.
- `pnpm test:perf:imports:changed`: той самий профайлінг імпорту, але лише для файлів, змінених відносно `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` вимірює продуктивність маршрутизованого шляху changed-mode порівняно з нативним запуском root-project для того самого закоміченого git diff.
- `pnpm test:perf:changed:bench -- --worktree` вимірює продуктивність поточного набору змін worktree без попереднього коміту.
- `pnpm test:perf:profile:main`: записує CPU profile для головного потоку Vitest (`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: записує CPU + heap profiles для unit runner (`.artifacts/vitest-runner-profile`).
- Інтеграція gateway: вмикається через `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` або `pnpm test:gateway`.
- `pnpm test:e2e`: Запускає наскрізні smoke-тести gateway (сполучення multi-instance WS/HTTP/node). Типово використовує `threads` + `isolate: false` з адаптивною кількістю workers у `vitest.e2e.config.ts`; налаштовуйте через `OPENCLAW_E2E_WORKERS=<n>` і встановіть `OPENCLAW_E2E_VERBOSE=1` для докладних логів.
- `pnpm test:live`: Запускає live-тести провайдерів (minimax/zai). Потребує API-ключів і `LIVE=1` (або провайдер-специфічного `*_LIVE_TEST=1`) для зняття пропуску.
- `pnpm test:docker:openwebui`: Запускає Dockerized OpenClaw + Open WebUI, входить через Open WebUI, перевіряє `/api/models`, а потім запускає реальний проксійований чат через `/api/chat/completions`. Потребує придатного ключа live-моделі (наприклад, OpenAI у `~/.profile`), завантажує зовнішній образ Open WebUI і не вважається стабільним для CI так, як звичайні набори unit/e2e.
- `pnpm test:docker:mcp-channels`: Запускає seeded контейнер Gateway і другий клієнтський контейнер, який запускає `openclaw mcp serve`, а потім перевіряє виявлення маршрутизованих розмов, читання транскриптів, метадані вкладень, поведінку live event queue, маршрутизацію вихідних надсилань, а також сповіщення про канал і дозволи в стилі Claude через реальний міст stdio. Перевірка сповіщень Claude читає необроблені stdio MCP frames напряму, щоб smoke-тест відображав те, що міст реально надсилає.

## Локальний gate для PR

Для локальних перевірок PR land/gate запустіть:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

Якщо `pnpm test` нестабільно працює на завантаженому хості, перезапустіть його один раз, перш ніж вважати це регресією, а потім ізолюйте через `pnpm test <path/to/test>`. Для хостів з обмеженою пам’яттю використовуйте:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## Бенчмарк затримки моделі (локальні ключі)

Скрипт: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

Використання:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- Необов’язкові env: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- Типовий prompt: “Відповідай одним словом: ok. Без розділових знаків чи зайвого тексту.”

Останній запуск (2025-12-31, 20 прогонів):

- minimax median 1279ms (min 1114, max 2431)
- opus median 2454ms (min 1224, max 3170)

## Бенчмарк запуску CLI

Скрипт: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

Використання:

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

Пресети:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: обидва пресети

Вивід містить `sampleCount`, avg, p50, p95, min/max, розподіл exit-code/signal і зведення максимального RSS для кожної команди. Необов’язковий `--cpu-prof-dir` / `--heap-prof-dir` записує профілі V8 для кожного прогону, щоб вимірювання часу і збір профілів використовували той самий harness.

Умовні позначення для збереженого виводу:

- `pnpm test:startup:bench:smoke` записує цільовий smoke-артефакт у `.artifacts/cli-startup-bench-smoke.json`
- `pnpm test:startup:bench:save` записує артефакт повного набору в `.artifacts/cli-startup-bench-all.json` з використанням `runs=5` і `warmup=1`
- `pnpm test:startup:bench:update` оновлює закомічений baseline fixture у `test/fixtures/cli-startup-bench.json` з використанням `runs=5` і `warmup=1`

Fixture, закомічений у репозиторій:

- `test/fixtures/cli-startup-bench.json`
- Оновіть через `pnpm test:startup:bench:update`
- Порівняйте поточні результати з fixture через `pnpm test:startup:bench:check`

## Onboarding E2E (Docker)

Docker не є обов’язковим; це потрібно лише для containerized onboarding smoke-тестів.

Повний cold-start flow у чистому Linux-контейнері:

```bash
scripts/e2e/onboard-docker.sh
```

Цей скрипт керує інтерактивним майстром через pseudo-tty, перевіряє файли config/workspace/session, потім запускає gateway і виконує `openclaw health`.

## Smoke-тест імпорту QR (Docker)

Гарантує, що `qrcode-terminal` завантажується в підтримуваних Docker runtime Node (типово Node 24, сумісний Node 22):

```bash
pnpm test:docker:qr
```
