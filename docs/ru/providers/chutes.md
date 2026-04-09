---
title: "Chutes"
summary: "Настройка Chutes (OAuth или API-ключ, обнаружение моделей, псевдонимы)"
read_when:
  - Вы хотите использовать Chutes с OpenClaw
  - Вам нужен путь настройки OAuth или API-ключа
  - Вы хотите узнать о модели по умолчанию, псевдонимах или поведении при обнаружении моделей
---

# Chutes

[Chutes](https://chutes.ai) предоставляет каталоги моделей с открытым исходным кодом через API, совместимый с OpenAI. OpenClaw поддерживает как OAuth в браузере, так и прямую аутентификацию по API-ключу для встроенного провайдера `chutes`.

- Провайдер: `chutes`
- API: совместим с OpenAI
- Базовый URL: `https://llm.chutes.ai/v1`
- Аутентификация:
  - OAuth через `openclaw onboard --auth-choice chutes`
  - API-ключ через `openclaw onboard --auth-choice chutes-api-key`
  - Переменные окружения во время выполнения: `CHUTES_API_KEY`, `CHUTES_OAUTH_TOKEN`

## Быстрый старт

### OAuth

```bash
openclaw onboard --auth-choice chutes
```

OpenClaw запускает поток в браузере локально или отображает URL + поток с перенаправлением и вставкой на удалённых/безголовых хостах. Токены OAuth автоматически обновляются через профили аутентификации OpenClaw.

Дополнительные параметры для переопределения OAuth:

- `CHUTES_CLIENT_ID`
- `CHUTES_CLIENT_SECRET`
- `CHUTES_OAUTH_REDIRECT_URI`
- `CHUTES_OAUTH_SCOPES`

### API-ключ

```bash
openclaw onboard --auth-choice chutes-api-key
```

Получите свой ключ на [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys).

Оба способа аутентификации регистрируют встроенный каталог Chutes и устанавливают модель по умолчанию — `chutes/zai-org/GLM-4.7-TEE`.

## Поведение при обнаружении моделей

Когда аутентификация Chutes доступна, OpenClaw запрашивает каталог Chutes с использованием этих учётных данных и использует обнаруженные модели. Если обнаружение завершается ошибкой, OpenClaw переходит к встроенному статическому каталогу, чтобы процесс начальной настройки и запуска по-прежнему работал.

## Псевдонимы по умолчанию

OpenClaw также регистрирует три удобных псевдонима для встроенного каталога Chutes:

- `chutes-fast` → `chutes/zai-org/GLM-4.7-FP8`
- `chutes-pro` → `chutes/deepseek-ai/DeepSeek-V3.2-TEE`
- `chutes-vision` → `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506`

## Встроенный стартовый каталог

Встроенный резервный каталог включает актуальные ссылки Chutes, такие как:

- `chutes/zai-org/GLM-4.7-TEE`
- `chutes/zai-org/GLM-5-TEE`
- `chutes/deepseek-ai/DeepSeek-V3.2-TEE`
- `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`
- `chutes/moonshotai/Kimi-K2.5-TEE`
- `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506`
- `chutes/Qwen/Qwen3-Coder-Next-TEE`
- `chutes/openai/gpt-oss-120b-TEE`

## Пример конфигурации

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

## Примечания

- Справка по OAuth и требования к приложению с перенаправлением: [документация Chutes OAuth](https://chutes.ai/docs/sign-in-with-chutes/overview)
- Обнаружение по API-ключу и OAuth использует один и тот же идентификатор провайдера `chutes`.
- Модели Chutes регистрируются как `chutes/<model-id>`.