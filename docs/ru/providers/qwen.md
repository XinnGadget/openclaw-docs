---
summary: "Использовать Qwen Cloud через встроенный провайдер Qwen в OpenClaw"
read_when:
  - Вы хотите использовать Qwen с OpenClaw
  - Ранее вы использовали Qwen OAuth
title: "Qwen"
---

# Qwen

<Warning>

**Qwen OAuth удалён.** Интеграция с бесплатным уровнем OAuth (`qwen-portal`), которая использовала эндпоинты `portal.qwen.ai`, больше недоступна.
См. [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) для подробностей.

</Warning>

## Рекомендовано: Qwen Cloud

Теперь OpenClaw рассматривает Qwen как встроенного провайдера первого класса с каноническим ID `qwen`. Встроенный провайдер нацелен на эндпоинты Qwen Cloud / Alibaba DashScope и Coding Plan и сохраняет работоспособность устаревших ID `modelstudio` в качестве алиасов совместимости.

- Провайдер: `qwen`
- Предпочтительная переменная окружения: `QWEN_API_KEY`
- Также принимаются для совместимости: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Стиль API: совместимый с OpenAI

Если вам нужен `qwen3.6-plus`, предпочтительнее использовать эндпоинт **Standard (оплата по факту использования)**. Поддержка Coding Plan может отставать от публичного каталога.

```bash
# Глобальный эндпоинт Coding Plan
openclaw onboard --auth-choice qwen-api-key

# Эндпоинт Coding Plan для Китая
openclaw onboard --auth-choice qwen-api-key-cn

# Глобальный эндпоинт Standard (оплата по факту использования)
openclaw onboard --auth-choice qwen-standard-api-key

# Эндпоинт Standard (оплата по факту использования) для Китая
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

Устаревшие ID выбора аутентификации `modelstudio-*` и ссылки на модели `modelstudio/...` по-прежнему работают как алиасы совместимости, но в новых процессах настройки следует отдавать предпочтение каноническим ID выбора аутентификации `qwen-*` и ссылкам на модели `qwen/...`.

После подключения установите модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## Типы планов и эндпоинты

| План | Регион | Выбор аутентификации | Эндпоинт |
| --- | --- | --- | --- |
| Standard (оплата по факту использования) | Китай | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1` |
| Standard (оплата по факту использования) | Глобальный | `qwen-standard-api-key` | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (подписка) | Китай | `qwen-api-key-cn` | `coding.dashscope.aliyuncs.com/v1` |
| Coding Plan (подписка) | Глобальный | `qwen-api-key` | `coding-intl.dashscope.aliyuncs.com/v1` |

Провайдер автоматически выбирает эндпоинт на основе вашего выбора аутентификации. Канонические варианты используют семейство `qwen-*`; `modelstudio-*` остаётся только для совместимости. Вы можете переопределить выбор, указав собственный `baseUrl` в конфигурации.

Нативные эндпоинты Model Studio заявляют о совместимости с потоковой передачей данных через транспорт `openai-completions`. OpenClaw теперь ориентируется на возможности эндпоинтов, поэтому пользовательские ID провайдеров, совместимые с DashScope и нацеленные на те же нативные хосты, наследуют такое же поведение при потоковой передаче, вместо того чтобы требовать использования встроенного ID провайдера `qwen`.

## Получение API-ключа

- **Управление ключами**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **Документация**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## Встроенный каталог

OpenClaw в настоящее время поставляется со встроенным каталогом Qwen. Настроенная версия каталога учитывает эндпоинты: конфигурации Coding Plan исключают модели, которые, как известно, работают только на эндпоинте Standard.

| Ссылка на модель | Ввод | Контекст | Примечания |
| --- | --- | --- | --- |
| `qwen/qwen3.5-plus` | текст, изображение | 1 000 000 | Модель по умолчанию |
| `qwen/qwen3.6-plus` | текст, изображение | 1 000 000 | При необходимости этой модели предпочтительнее использовать эндпоинты Standard |
| `qwen/qwen3-max-2026-01-23` | текст | 262 144 | Линейка Qwen Max |
| `qwen/qwen3-coder-next` | текст | 262 144 | Для кодирования |
| `qwen/qwen3-coder-plus` | текст | 1 000 000 | Для кодирования |
| `qwen/MiniMax-M2.5` | текст | 1 000 000 | Включено рассуждение |
| `qwen/glm-5` | текст | 202 752 | GLM |
| `qwen/glm-4.7` | текст | 202 752 | GLM |
| `qwen/kimi-k2.5` | текст, изображение | 262 144 | Moonshot AI через Alibaba |

Доступность может варьироваться в зависимости от эндпоинта и тарифного плана, даже если модель присутствует во встроенном каталоге.

Совместимость с нативной потоковой передачей данных применяется как к хостам Coding Plan, так и к хостам Standard, совместимым с DashScope:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Доступность Qwen 3.6 Plus

`qwen3.6-plus` доступен на эндпоинтах Standard (оплата по факту использования) Model Studio:

- Китай: `dashscope.aliyuncs.com/compatible-mode/v1`
- Глобальный: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Если эндпоинты Coding Plan возвращают ошибку "модель не поддерживается" для `qwen3.6-plus`, переключитесь на Standard (оплата по факту использования) вместо пары эндпоинт/ключ Coding Plan.

## План возможностей

Расширение `qwen` позиционируется как основная площадка для полного охвата Qwen Cloud, а не только для моделей кодирования/текста.

- Модели для текста/чата: уже включены
- Вызов инструментов, структурированный вывод, рассуждение: унаследованы от транспорта, совместимого с OpenAI
- Генерация изображений: планируется на уровне плагина провайдера
- Понимание изображений/видео: уже включено на эндпоинте Standard
- Речь/аудио: планируется на уровне плагина провайдера
- Вложение памяти/переранжирование: планируется через поверхность адаптера вложений
- Генерация видео: уже включена через общую возможность генерации видео

## Мультимодальные дополнения

Расширение `qwen` теперь также предоставляет:

- Понимание видео через `qwen-vl-max-latest`
- Генерацию видео через:
  - `wan2.6-t2v` (по умолчанию)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

Эти мультимодальные поверхности используют эндпоинты DashScope **Standard**, а не Coding Plan.

- Базовый URL для глобального/международного Standard: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Базовый URL для Standard в Китае: `https://dashscope.aliyuncs.com/compatible-mode/v1`

Для генерации видео OpenClaw сопоставляет настроенную область Qwen с соответствующим хостом DashScope AIGC перед отправкой задания:

- Глобальный/международный: `https://dashscope-intl.aliyuncs.com`
- Китай: `https://dashscope.aliyuncs.com`

Это означает, что обычный `models.providers.qwen.baseUrl`, указывающий на хосты Coding Plan