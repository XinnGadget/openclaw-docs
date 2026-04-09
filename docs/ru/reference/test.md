---
summary: "Как запускать тесты локально (vitest) и когда использовать режимы force/coverage"
read_when:
  - Запуск или исправление тестов
title: "Тесты"
---

# Тесты

- Полный набор тестов (suites, live, Docker): [Тестирование](/help/testing)

- `pnpm test:force`: Завершает любой оставшийся процесс шлюза, занимающий порт управления по умолчанию, затем запускает полный набор тестов Vitest с изолированным портом шлюза, чтобы тесты сервера не конфликтовали с работающим экземпляром. Используйте эту команду, если предыдущий запуск шлюза оставил порт 18789 занятым.
- `pnpm test:coverage`: Запускает набор юнит-тестов с покрытием V8 (через `vitest.unit.config.ts`). Глобальные пороги — 70 % для строк/ветвей/функций/операторов. Покрытие исключает точки входа с интенсивной интеграцией (настройка CLI, мосты шлюза/Telegram, статический сервер веб-чата), чтобы сосредоточиться на логике, тестируемой юнит-тестами.
- `pnpm test:coverage:changed`: Запускает покрытие юнит-тестов только для файлов, изменённых с момента `origin/main`.
- `pnpm test:changed`: преобразует изменённые пути Git в scoped-полосы Vitest, если diff затрагивает только маршрутизируемые исходные файлы/файлы тестов. Изменения в конфигурации/настройке по-прежнему возвращаются к запуску корневых проектов, чтобы при необходимости широко перезапускать правки в проводке.
- `pnpm test`: направляет явные цели (файлы/каталоги) через scoped-полосы Vitest. Незаданные запуски теперь выполняют одиннадцать последовательных конфигураций шардов (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-support-boundary.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`) вместо одного гигантского процесса корневого проекта.
- Выбранные тестовые файлы `plugin-sdk` и `commands` теперь направляются через выделенные лёгкие полосы, в которых остаётся только `test/setup.ts`, оставляя ресурсоёмкие случаи в их существующих полосах.
- Выбранные вспомогательные исходные файлы `plugin-sdk` и `commands` также сопоставляют `pnpm test:changed` с явными соседними тестами в этих лёгких полосах, поэтому небольшие правки вспомогательных файлов не приводят к перезапуску ресурсоёмких наборов тестов с поддержкой среды выполнения.
- `auto-reply` теперь также разделяется на три выделенные конфигурации (`core`, `top-level`, `reply`), чтобы набор для ответов не доминировал над более лёгкими тестами верхнего уровня (статус/токен/вспомогательные функции).
- Базовая конфигурация Vitest теперь по умолчанию использует `pool: "threads"` и `isolate: false`, при этом общий неизолированный раннер включён во всех конфигурациях репозитория.
- `pnpm test:channels` запускает `vitest.channels.config.ts`.
- `pnpm test:extensions` запускает `vitest.extensions.config.ts`.
- `pnpm test:extensions`: запускает наборы тестов расширений/плагинов.
- `pnpm test:perf:imports`: включает отчётность Vitest о длительности импорта и разбивке импорта, при этом используя маршрутизацию по scoped-полосам для явных целей (файлы/каталоги).
- `pnpm test:perf:imports:changed`: то же профилирование импорта, но только для файлов, изменённых с момента `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` сравнивает производительность маршрута в режиме изменённых файлов с запуском корневого проекта для того же зафиксированного diff в Git.
- `pnpm test:perf:changed:bench -- --worktree` сравнивает набор изменений в текущем рабочем дереве без предварительной фиксации.
- `pnpm test:perf:profile:main`: создаёт профиль ЦП для основного потока Vitest (`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: создаёт профили ЦП и кучи для раннера юнит-тестов (`.artifacts/vitest-runner-profile`).
- Интеграция шлюза: включается опционально через `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` или `pnpm test:gateway`.
- `pnpm test:e2e`: запускает сквозные дымовые тесты шлюза (многоэкземплярный WS/HTTP/node-паринг). По умолчанию используются `threads` + `isolate: false` с адаптивными рабочими процессами в `vitest.e2e.config.ts`; настройка через `OPENCLAW_E2E_WORKERS=<n>` и `OPENCLAW_E2E_VERBOSE=1` для подробных логов.
- `pnpm test:live`: запускает тесты провайдеров в реальном времени (minimax/zai). Требуют API-ключей и `LIVE=1` (или специфичных для провайдера `*_LIVE_TEST=1`) для отмены пропуска.
- `pnpm test:docker:openwebui`: запускает Docker-контейнеры OpenClaw + Open WebUI, выполняет вход через Open WebUI, проверяет `/api/models`, затем запускает реальный проксированный чат через `/api/chat/completions`. Требует действующего ключа модели (например, OpenAI в `~/.profile`), загружает внешний образ Open WebUI и не гарантирует стабильность в CI, как обычные наборы юнит-тестов/e2e.
- `pnpm test:docker:mcp-channels`: запускает инициализированный контейнер шлюза и второй клиентский контейнер, который запускает `openclaw mcp serve`, затем проверяет обнаружение маршрутизируемых разговоров, чтение транскриптов, метаданные вложений, поведение очереди живых событий, маршрутизацию исходящих отправлений и уведомления о каналах и разрешениях в стиле Claude через реальный мост stdio. Проверка уведомлений Claude считывает необработанные кадры stdio MCP напрямую, чтобы дымовой тест отражал то, что фактически выдаёт мост.

## Локальный шлюз PR

Для локальных проверок шлюза PR выполните:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

Если `pnpm test` даёт сбои на загруженном хосте, перезапустите один раз, прежде чем считать это регрессией, затем изолируйте с помощью `pnpm test <path/to/test>`. Для хостов с ограниченным объёмом памяти используйте:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## Бенчмарк задержки модели (локальные ключи)

Скрипт: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

Использование:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- Опциональные переменные окружения: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- Запрос по умолчанию: "Ответьте одним словом: ok. Без пунктуации и дополнительного текста".

Последний запуск (2025-12-31, 20 запусков):

- minimax, медиана — 1279 мс (минимум — 1114, максимум — 2431)
- opus, медиана — 2454 мс (минимум — 1224, максимум — 3170)

## Бенчмарк запуска CLI

Скрипт: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

Использование:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist