---
title: "Volcengine (Doubao)"
summary: "Настройка Volcano Engine (модели Doubao, общие эндпоинты и эндпоинты для кодирования)"
read_when:
  - Вы хотите использовать Volcano Engine или модели Doubao с OpenClaw
  - Вам нужно настроить API-ключ Volcengine
---

# Volcengine (Doubao)

Поставщик Volcengine предоставляет доступ к моделям Doubao и сторонним моделям, размещённым на Volcano Engine, с отдельными эндпоинтами для общих задач и задач кодирования.

- Поставщики: `volcengine` (общий) + `volcengine-plan` (для кодирования)
- Аутентификация: `VOLCANO_ENGINE_API_KEY`
- API: совместимый с OpenAI

## Быстрый старт

1. Установите API-ключ:

```bash
openclaw onboard --auth-choice volcengine-api-key
```

2. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "volcengine-plan/ark-code-latest" },
    },
  },
}
```

## Пример в неинтерактивном режиме

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice volcengine-api-key \
  --volcengine-api-key "$VOLCANO_ENGINE_API_KEY"
```

## Поставщики и эндпоинты

| Поставщик | Эндпоинт | Сценарий использования |
| ----------------- | ----------------------------------------- | -------------- |
| `volcengine` | `ark.cn-beijing.volces.com/api/v3` | Общие модели |
| `volcengine-plan` | `ark.cn-beijing.volces.com/api/coding/v3` | Модели для кодирования |

Оба поставщика настраиваются с использованием одного API-ключа. При настройке оба регистрируются автоматически.

## Доступные модели

Общий поставщик (`volcengine`):

| Ссылка на модель | Название | Входные данные | Контекст |
| -------------------------------------------- | ------------------------------- | ----------- | ------- |
| `volcengine/doubao-seed-1-8-251228` | Doubao Seed 1.8 | текст, изображение | 256 000 |
| `volcengine/doubao-seed-code-preview-251028` | doubao-seed-code-preview-251028 | текст, изображение | 256 000 |
| `volcengine/kimi-k2-5-260127` | Kimi K2.5 | текст, изображение | 256 000 |
| `volcengine/glm-4-7-251222` | GLM 4.7 | текст, изображение | 200 000 |
| `volcengine/deepseek-v3-2-251201` | DeepSeek V3.2 | текст, изображение | 128 000 |

Поставщик для кодирования (`volcengine-plan`):

| Ссылка на модель | Название | Входные данные | Контекст |
| ------------------------------------------------- | ------------------------ | ----- | ------- |
| `volcengine-plan/ark-code-latest` | Ark Coding Plan | текст | 256 000 |
| `volcengine-plan/doubao-seed-code` | Doubao Seed Code | текст | 256 000 |
| `volcengine-plan/glm-4.7` | GLM 4.7 Coding | текст | 200 000 |
| `volcengine-plan/kimi-k2-thinking` | Kimi K2 Thinking | текст | 256 000 |
| `volcengine-plan/kimi-k2.5` | Kimi K2.5 Coding | текст | 256 000 |
| `volcengine-plan/doubao-seed-code-preview-251028` | Doubao Seed Code Preview | текст | 256 000 |

Команда `openclaw onboard --auth-choice volcengine-api-key` в настоящее время устанавливает `volcengine-plan/ark-code-latest` в качестве модели по умолчанию, одновременно регистрируя общий каталог `volcengine`.

При настройке/выборе модели вариант аутентификации Volcengine отдаёт предпочтение строкам `volcengine/*` и `volcengine-plan/*`. Если эти модели ещё не загружены, OpenClaw переходит к нефильтрованному каталогу вместо отображения пустого селектора, ограниченного поставщиком.

## Примечание об окружении

Если шлюз работает как демон (launchd/systemd), убедитесь, что переменная `VOLCANO_ENGINE_API_KEY` доступна для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).