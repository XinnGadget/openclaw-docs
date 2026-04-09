---
title: "Архитектура интеграции Pi"
summary: "Архитектура встроенной интеграции агента Pi в OpenClaw и жизненный цикл сессии"
read_when:
  - Изучение дизайна интеграции Pi SDK в OpenClaw
  - Модификация жизненного цикла сессии агента, инструментов или настройки провайдеров для Pi
---

# Архитектура интеграции Pi

В этом документе описано, как OpenClaw интегрируется с [pi-coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) и сопутствующими пакетами (`pi-ai`, `pi-agent-core`, `pi-tui`) для реализации возможностей ИИ-агента.

## Обзор

OpenClaw использует Pi SDK для встраивания ИИ-агента для кодирования в архитектуру шлюза обмена сообщениями. Вместо запуска Pi в качестве подпроцесса или использования режима RPC, OpenClaw напрямую импортирует и создаёт экземпляр `AgentSession` из Pi с помощью функции `createAgentSession()`. Такой встроенный подход обеспечивает:

- Полный контроль над жизненным циклом сессии и обработкой событий;
- Внедрение пользовательских инструментов (обмен сообщениями, песочница, действия, специфичные для канала);
- Настройку системных подсказок для каждого канала/контекста;
- Сохранение сессии с поддержкой ветвления и уплотнения;
- Ротацию профилей аутентификации для нескольких учётных записей с отказоустойчивостью;
- Переключение моделей независимо от провайдера.

## Зависимости пакетов

```json
{
  "@mariozechner/pi-agent-core": "0.64.0",
  "@mariozechner/pi-ai": "0.64.0",
  "@mariozechner/pi-coding-agent": "0.64.0",
  "@mariozechner/pi-tui": "0.64.0"
}
```

| Пакет | Назначение |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| `pi-ai` | Основные абстракции LLM: `Model`, `streamSimple`, типы сообщений, API провайдеров |
| `pi-agent-core` | Цикл агента, выполнение инструментов, типы `AgentMessage` |
| `pi-coding-agent` | Высокоуровневый SDK: `createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, встроенные инструменты |
| `pi-tui` | Компоненты терминала UI (используются в локальном режиме TUI OpenClaw) |

## Структура файлов

```
src/agents/
├── pi-embedded-runner.ts          # Повторный экспорт из pi-embedded-runner/
├── pi-embedded-runner/
│   ├── run.ts                     # Основная точка входа: runEmbeddedPiAgent()
│   ├── run/
│   │   ├── attempt.ts             # Логика одиночной попытки с настройкой сессии
│   │   ├── params.ts              # Тип RunEmbeddedPiAgentParams
│   │   ├── payloads.ts            # Формирование полезных нагрузок ответа из результатов выполнения
│   │   ├── images.ts              # Внедрение изображений для модели зрения
│   │   └── types.ts               # EmbeddedRunAttemptResult
│   ├── abort.ts                   # Обнаружение ошибок прерывания
│   ├── cache-ttl.ts               # Отслеживание TTL кэша для обрезки контекста
│   ├── compact.ts                 # Логика ручного/автоматического уплотнения
│   ├── extensions.ts              # Загрузка расширений Pi для встроенных запусков
│   ├── extra-params.ts            # Параметры потока, специфичные для провайдера
│   ├── google.ts                  # Исправление порядка ходов для Google/Gemini
│   ├── history.ts                 # Ограничение истории (DM против группы)
│   ├── lanes.ts                   # Каналы команд сессии/глобальные
│   ├── logger.ts                  # Логгер подсистемы
│   ├── model.ts                   # Разрешение модели через ModelRegistry
│   ├── runs.ts                    # Отслеживание активных запусков, прерывание, очередь
│   ├── sandbox-info.ts            # Информация о песочнице для системной подсказки
│   ├── session-manager-cache.ts   # Кэширование экземпляра SessionManager
│   ├── session-manager-init.ts    # Инициализация файла сессии
│   ├── system-prompt.ts           # Конструктор системной подсказки
│   ├── tool-split.ts              # Разделение инструментов на встроенные и пользовательские
│   ├── types.ts                   # EmbeddedPiAgentMeta, EmbeddedPiRunResult
│   └── utils.ts                   # Сопоставление ThinkLevel, описание ошибок
├── pi-embedded-subscribe.ts       # Подписка на события сессии/диспетчеризация
├── pi-embedded-subscribe.types.ts # SubscribeEmbeddedPiSessionParams
├── pi-embedded-subscribe.handlers.ts # Фабрика обработчиков событий
├── pi-embedded-subscribe.handlers.lifecycle.ts
├── pi-embedded-subscribe.handlers.types.ts
├── pi-embedded-block-chunker.ts   # Разбиение потоковых блоков ответа
├── pi-embedded-messaging.ts       # Отслеживание отправки инструментов обмена сообщениями
├── pi-embedded-helpers.ts         # Классификация ошибок, проверка хода
├── pi-embedded-helpers/           # Вспомогательные модули
├── pi-embedded-utils.ts           # Утилиты форматирования
├── pi-tools.ts                    # createOpenClawCodingTools()
├── pi-tools.abort.ts              # Обёртка AbortSignal для инструментов
├── pi-tools.policy.ts             # Политика разрешённых/запрещённых инструментов
├── pi-tools.read.ts               # Настройка инструмента чтения
├── pi-tools.schema.ts             # Нормализация схемы инструментов
├── pi-tools.types.ts              # Псевдоним типа AnyAgentTool
├── pi-tool-definition-adapter.ts  # Адаптер AgentTool -> ToolDefinition
├── pi-settings.ts                 # Переопределение настроек
├── pi-hooks/                      # Пользовательские хуки Pi
│   ├── compaction-safeguard.ts    # Защита расширения
│   ├── compaction-safeguard-runtime.ts
│   ├── context-pruning.ts         # Расширение обрезки контекста на основе TTL кэша
│   └── context-pruning/
├── model-auth.ts                  # Разрешение профиля аутентификации
├── auth-profiles.ts               # Хранилище профилей, охлаждение, отказоустойчивость
├── model-selection.ts             # Разрешение модели по умолчанию
├── models-config.ts               # Генерация models.json
├── model-catalog.ts               # Кэш каталога моделей
├── context-window-guard.ts        # Проверка окна контекста
├── failover-error.ts              # Класс FailoverError
├── defaults.ts                    # DEFAULT_PROVIDER, DEFAULT_MODEL
├── system-prompt.ts               # buildAgentSystemPrompt()
├── system-prompt-params.ts        # Разрешение параметров системной подсказки
├── system-prompt-report.ts        # Генерация отчёта для отладки
├── tool-summaries.ts              # Краткие описания инструментов
├── tool-policy.ts                 # Разрешение политики инструментов
├── transcript-policy.ts           # Политика проверки транскриптов
├── skills.ts                      # Создание моментального снимка навыков/подсказки
├── skills/                        # Подсистема навыков
├── sandbox.ts                     # Разрешение контекста песочницы
├── sandbox/                       # Подсистема песочницы
├── channel-tools.ts               # Внедрение инструментов, специфичных для канала
├── openclaw-tools.ts              # Инструменты, специфичные для OpenClaw
├── bash-tools.ts                  # Инструменты exec/process
├── apply-patch.ts                 # Инструмент apply_patch (OpenAI)
├── tools/                         # Отдельные реализации инструментов
│   ├── browser-tool.ts
│   ├── canvas-tool.ts
│   ├── cron-tool.ts
│   ├── gateway-tool.ts
│   ├── image-tool.ts
│   ├── message-tool.ts
│   ├── nodes-tool.ts
│   ├── session*.ts
│   ├── web-*.ts
│   └── ...
└── ...
```

Времена выполнения действий сообщений, специфичных для канала, теперь находятся в каталогах расширений, принадлежащих плагинам, а не в `src/agents/tools`, например:

- файлы времени выполнения действий плагина Discord;
- файл времени выполнения действий плагина Slack;
- файл времени выполнения действий плагина Telegram;
- файл времени выполнения действий плагина WhatsApp.

## Основной поток интеграции

### 1. Запуск встроенного агента

Основная точка входа — `runEmbeddedPiAgent()` в `pi-embedded-runner/run.ts`:

```typescript
import { runEmbeddedPiAgent } from "./agents/pi-embedded-runner.js";

const result = await runEmbeddedPiAgent({
  sessionId: "user-123",
  sessionKey: "main:whatsapp:+1234567890",
  sessionFile: "/path/to/session.jsonl",
  workspaceDir: "/path/to/workspace",
  config: openclawConfig,
  prompt: "Hello, how are you?",
  provider: "anthropic",
  model: "claude-sonnet