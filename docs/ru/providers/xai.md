---
summary: "Использовать модели xAI Grok в OpenClaw"
read_when:
  - Вы хотите использовать модели Grok в OpenClaw
  - Вы настраиваете аутентификацию xAI или идентификаторы моделей
title: "xAI"
---

# xAI

В OpenClaw включён встроенный плагин-провайдер `xai` для моделей Grok.

## Настройка

1. Создайте API-ключ в консоли xAI.
2. Задайте переменную `XAI_API_KEY` или выполните команду:

```bash
openclaw onboard --auth-choice xai-api-key
```

3. Выберите модель, например:

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

Теперь OpenClaw использует API ответов xAI в качестве встроенного транспорта xAI. Тот же ключ `XAI_API_KEY` можно использовать для функций `web_search` на базе Grok, первоклассного `x_search` и удалённого `code_execution`.

Если вы сохраните ключ xAI в `plugins.entries.xai.config.webSearch.apiKey`, встроенный провайдер моделей xAI будет использовать этот ключ в качестве запасного варианта.

Настройка `code_execution` находится в `plugins.entries.xai.config.codeExecution`.

## Текущий каталог встроенных моделей

OpenClaw включает следующие семейства моделей xAI "из коробки":

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

Плагин также поддерживает новые идентификаторы `grok-4*` и `grok-code-fast*`, если они соответствуют той же структуре API.

Примечания о быстрых моделях:

- `grok-4-fast`, `grok-4-1-fast` и варианты `grok-4.20-beta-*` — текущие версии Grok с поддержкой изображений во встроенном каталоге.
- `/fast on` или `agents.defaults.models["xai/<model>"].params.fastMode: true` преобразуют родные запросы xAI следующим образом:
  - `grok-3` → `grok-3-fast`
  - `grok-3-mini` → `grok-3-mini-fast`
  - `grok-4` → `grok-4-fast`
  - `grok-4-0709` → `grok-4-fast`

Устаревшие псевдонимы совместимости по-прежнему нормализуются до канонических встроенных идентификаторов. Например:

- `grok-4-fast-reasoning` → `grok-4-fast`
- `grok-4-1-fast-reasoning` → `grok-4-1-fast`
- `grok-4.20-reasoning` → `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` → `grok-4.20-beta-latest-non-reasoning`

## Веб-поиск

Встроенный провайдер веб-поиска `grok` также использует `XAI_API_KEY`:

```bash
openclaw config set tools.web.search.provider grok
```

## Генерация видео

Встроенный плагин `xai` также регистрирует генерацию видео через общий инструмент `video_generate`.

- Модель видео по умолчанию: `xai/grok-imagine-video`
- Режимы: текст-в-видео, изображение-в-видео и удалённые потоки редактирования/расширения видео
- Поддерживает параметры `aspectRatio` и `resolution`
- Текущее ограничение: локальные буферы видео не принимаются; используйте удалённые URL-адреса `http(s)` для ввода ссылок на видео/редактирования

Чтобы использовать xAI в качестве провайдера видео по умолчанию:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "xai/grok-imagine-video",
      },
    },
  },
}
```

См. раздел [Генерация видео](/tools/video-generation) для ознакомления с параметрами общего инструмента, выбором провайдера и поведением при отказоустойчивости.

## Известные ограничения

- Аутентификация осуществляется только через API-ключ. В OpenClaw пока нет потока xAI OAuth/device-code.
- Модель `grok-4.20-multi-agent-experimental-beta-0304` не поддерживается на обычном пути провайдера xAI, поскольку требует другого интерфейса API, отличного от стандартного транспорта xAI в OpenClaw.

## Примечания

- OpenClaw автоматически применяет исправления совместимости схем инструментов и вызовов инструментов, специфичные для xAI, на общем пути выполнения.
- В родных запросах xAI по умолчанию установлено значение `tool_stream: true`. Чтобы отключить его, задайте `agents.defaults.models["xai/<model>"].params.tool_stream` как `false`.
- Встроенный обёртки xAI удаляет неподдерживаемые строгие флаги схемы инструментов и ключи полезной нагрузки рассуждений перед отправкой родных запросов xAI.
- `web_search`, `x_search` и `code_execution` представлены в OpenClaw как инструменты. OpenClaw активирует необходимые встроенные функции xAI внутри каждого запроса инструмента, вместо того чтобы прикреплять все родные инструменты к каждому ходу чата.
- `x_search` и `code_execution` управляются встроенным плагином xAI, а не жёстко закодированы в основной среде выполнения модели.
- `code_execution` — это удалённое выполнение в песочнице xAI, а не локальное [`exec`](/tools/exec).
- Для общего обзора провайдеров см. раздел [Провайдеры моделей](/providers/index).