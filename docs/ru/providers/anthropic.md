---
summary: "Использовать Anthropic Claude через API-ключи или Claude CLI в OpenClaw"
read_when:
  - Вы хотите использовать модели Anthropic в OpenClaw
title: "Anthropic"
---

# Anthropic (Claude)

Компания Anthropic разрабатывает семейство моделей **Claude** и предоставляет к ним доступ через API и Claude CLI. В OpenClaw поддерживаются как API-ключи Anthropic, так и повторное использование Claude CLI. Уже настроенные устаревшие профили токенов Anthropic по-прежнему учитываются во время выполнения.

<Предупреждение>
Сотрудники Anthropic сообщили, что использование Claude CLI в стиле OpenClaw снова разрешено, поэтому OpenClaw считает повторное использование Claude CLI и команду `claude -p` допустимыми для данной интеграции — до тех пор, пока Anthropic не опубликует новую политику.

Для долго работающих хостов-шлюзов наиболее чётким и предсказуемым способом работы в продакшене по-прежнему остаются API-ключи Anthropic. Если вы уже используете Claude CLI на хосте, OpenClaw может напрямую повторно использовать этот вход в систему.

Актуальные публичные документы Anthropic:

- [Справочник по Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Обзор Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Использование Claude Code с тарифным планом Pro или Max](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Использование Claude Code с тарифным планом Team или Enterprise](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

Если вам нужен наиболее прозрачный способ учёта расходов, используйте API-ключ Anthropic.

OpenClaw также поддерживает другие варианты с подпиской, включая [OpenAI Codex](/providers/openai), [Qwen Cloud Coding Plan](/providers/qwen), [MiniMax Coding Plan](/providers/minimax) и [Z.AI / GLM Coding Plan](/providers/glm).
</Предупреждение>

## Вариант A: API-ключ Anthropic

**Оптимально для:** стандартного доступа через API и тарификации на основе использования.
Создайте свой API-ключ в консоли Anthropic.

### Настройка CLI

```bash
openclaw onboard
# выберите: API-ключ Anthropic

# или в неинтерактивном режиме
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Фрагмент конфигурации Anthropic

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Настройки мышления по умолчанию (Claude 4.6)

- Модели Anthropic Claude 4.6 в OpenClaw по умолчанию используют режим мышления `adaptive`, если явно не задан уровень мышления.
- Вы можете переопределить уровень для каждого сообщения (`/think:<level>`) или в параметрах модели: `agents.defaults.models["anthropic/<model>"].params.thinking`.
- Соответствующие документы Anthropic:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Быстрый режим (API Anthropic)

Переключатель `/fast`, общий для OpenClaw, также поддерживает прямой публичный трафик Anthropic, включая запросы с аутентификацией через API-ключ и OAuth, отправляемые на `api.anthropic.com`.

- `/fast on` соответствует `service_tier: "auto"`
- `/fast off` соответствует `service_tier: "standard_only"`
- Настройка по умолчанию:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

Важные ограничения:

- OpenClaw внедряет уровни сервиса Anthropic только для прямых запросов к `api.anthropic.com`. Если вы направляете запросы `anthropic/*` через прокси или шлюз, `/fast` не изменяет `service_tier`.
- Явные параметры модели Anthropic `serviceTier` или `service_tier` переопределяют значение по умолчанию `/fast`, если оба параметра заданы.
- Anthropic указывает действующий уровень в ответе в поле `usage.service_tier`. На аккаунтах без возможности использования Priority Tier значение `service_tier: "auto"` может по-прежнему соответствовать `standard`.

## Кэширование промтов (API Anthropic)

OpenClaw поддерживает функцию кэширования промтов от Anthropic. Это **доступно только через API**; устаревшая аутентификация через токен Anthropic не учитывает настройки кэша.

### Настройка

Используйте параметр `cacheRetention` в конфигурации модели:

| Значение | Длительность кэширования | Описание |
| -------- | ------------------------ | -------- |
| `none`   | Нет кэширования          | Отключает кэширование промтов |
| `short`  | 5 минут                  | Значение по умолчанию для аутентификации через API-ключ |
| `long`   | 1 час                    | Расширенное кэширование |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### Значения по умолчанию

При использовании аутентификации через API-ключ Anthropic OpenClaw автоматически применяет `cacheRetention: "short"` (кэш на 5 минут) для всех моделей Anthropic. Вы можете переопределить это, явно задав `cacheRetention` в конфигурации.

### Переопределение cacheRetention для отдельных агентов

Используйте параметры на уровне модели в качестве базового значения, затем переопределите их для конкретных агентов через `agents.list[].params`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // базовое значение для большинства агентов
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // переопределение только для этого агента
    ],
  },
}
```

Порядок объединения конфигураций для параметров, связанных с кэшем:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (соответствие по `id`, переопределение по ключу)

Это позволяет одному агенту использовать долгосрочный кэш, а другому агенту на той же модели — отключить кэширование, чтобы избежать затрат на запись при трафике с низкой повторной использованием.

### Примечания по Bedrock Claude

- Модели Anthropic Claude на Bedrock (`amazon-bedrock/*anthropic.claude*`) принимают параметр `cacheRetention` при настройке.
- Для моделей Bedrock, не относящихся к Anthropic, в среде выполнения принудительно устанавливается `cacheRetention: "none"`.
- Умные значения по умолчанию для API-ключа Anthropic также устанавливают `cacheRetention: "short"` для ссылок на модели Claude на Bedrock, если явное значение не задано.

## Окно контекста на 1 млн токенов (бета-версия Anthropic)

Окно контекста на 1 млн токенов в Anthropic находится в стадии бета-тестирования. В OpenClaw его можно включить для каждой модели с помощью `params.context1m: true` для поддерживаемых моделей Opus/Sonnet.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw преобразует это в `anthropic-beta: context-1m-2025-08-07` в запросах к Anthropic.

Это активируется только в том случае, если для модели явно задано `params.context1m: true`.

Требование: Anthropic должен разрешить использование длинного контекста для этих учётных данных.

Примечание: Anthropic в настоящее время отклоняет запросы бета-версии `context-1m-*` при использовании устаревшей аутентификации через токен Anthropic (`sk-ant-oat-*`). Если вы настроите `context1m: true` с этим устаревшим режимом аутентификации, OpenClaw вы