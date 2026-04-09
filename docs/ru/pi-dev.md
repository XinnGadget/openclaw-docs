---
title: "Рабочий процесс разработки Pi"
summary: "Рабочий процесс разработчика для интеграции Pi: сборка, тестирование и проверка в рабочей среде"
read_when:
  - Работа над кодом или тестами для интеграции Pi
  - Запуск проверок lint, проверки типов и тестов в рабочей среде, специфичных для Pi
---

# Рабочий процесс разработки Pi

В этом руководстве описан рациональный рабочий процесс для работы над интеграцией Pi в OpenClaw.

## Проверка типов и линтинг

- Локальный шлюз по умолчанию: `pnpm check`
- Шлюз сборки: `pnpm build` — выполняется, если изменения могут повлиять на вывод сборки, упаковку или границы ленивой загрузки/модулей
- Полный шлюз для значительных изменений, связанных с Pi: `pnpm check && pnpm test`

## Запуск тестов Pi

Запустите набор тестов, ориентированных на Pi, напрямую с помощью Vitest:

```bash
pnpm test \
  "src/agents/pi-*.test.ts" \
  "src/agents/pi-embedded-*.test.ts" \
  "src/agents/pi-tools*.test.ts" \
  "src/agents/pi-settings.test.ts" \
  "src/agents/pi-tool-definition-adapter*.test.ts" \
  "src/agents/pi-hooks/**/*.test.ts"
```

Чтобы включить проверку провайдера в рабочей среде:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test src/agents/pi-embedded-runner-extraparams.live.test.ts
```

Это охватывает основные наборы модульных тестов Pi:

- `src/agents/pi-*.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-tool-definition-adapter.test.ts`
- `src/agents/pi-hooks/*.test.ts`

## Ручное тестирование

Рекомендуемый порядок действий:

- Запустите шлюз в режиме разработки:
  - `pnpm gateway:dev`
- Запустите агента напрямую:
  - `pnpm openclaw agent --message "Hello" --thinking low`
- Используйте TUI для интерактивной отладки:
  - `pnpm tui`

Для проверки поведения вызова инструментов запросите действие `read` или `exec`, чтобы увидеть потоковую передачу инструментов и обработку полезных данных.

## Сброс до исходного состояния

Состояние хранится в каталоге состояния OpenClaw. По умолчанию это `~/.openclaw`. Если задана переменная `OPENCLAW_STATE_DIR`, используйте указанный в ней каталог.

Чтобы сбросить всё:

- `openclaw.json` — конфигурация;
- `agents/<agentId>/agent/auth-profiles.json` — профили аутентификации модели (API-ключи + OAuth);
- `credentials/` — состояние провайдера/канала, которое по-прежнему хранится вне хранилища профилей аутентификации;
- `agents/<agentId>/sessions/` — история сеансов агента;
- `agents/<agentId>/sessions/sessions.json` — индекс сеансов;
- `sessions/` — если существуют устаревшие пути;
- `workspace/` — если требуется пустое рабочее пространство.

Если вы хотите сбросить только сеансы, удалите каталог `agents/<agentId>/sessions/` для соответствующего агента. Если вы хотите сохранить аутентификацию, оставьте файл `agents/<agentId>/agent/auth-profiles.json` и состояние провайдера в каталоге `credentials/`.

## Ссылки

- [Тестирование](/help/testing)
- [Начало работы](/start/getting-started)