---
title: "Kilo Gateway"
summary: "Используйте унифицированный API Kilo Gateway для доступа к множеству моделей в OpenClaw"
read_when:
  - Вам нужен один API-ключ для множества LLM
  - Вы хотите запускать модели через Kilo Gateway в OpenClaw
---

# Kilo Gateway

Kilo Gateway предоставляет **унифицированный API**, который направляет запросы к множеству моделей через единую конечную точку и API-ключ. Он совместим с OpenAI, поэтому большинство SDK OpenAI работают после смены базового URL.

## Получение API-ключа

1. Перейдите на [app.kilo.ai](https://app.kilo.ai).
2. Войдите в аккаунт или создайте его.
3. Перейдите в раздел API Keys и сгенерируйте новый ключ.

## Настройка CLI

```bash
openclaw onboard --auth-choice kilocode-api-key
```

Или задайте переменную окружения:

```bash
export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
```

## Фрагмент конфигурации

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

## Модель по умолчанию

Модель по умолчанию — `kilocode/kilo/auto`, это управляемая Kilo Gateway модель с интеллектуальной маршрутизацией, принадлежащая провайдеру.

OpenClaw рассматривает `kilocode/kilo/auto` как стабильный эталон по умолчанию, но не публикует сопоставление задач с вышестоящей моделью для этого маршрута.

## Доступные модели

OpenClaw динамически обнаруживает доступные модели в Kilo Gateway при запуске. Чтобы увидеть полный список моделей, доступных для вашего аккаунта, используйте команду `/models kilocode`.

Любую модель, доступную в шлюзе, можно использовать с префиксом `kilocode/`:

```
kilocode/kilo/auto              (по умолчанию — интеллектуальная маршрутизация)
kilocode/anthropic/claude-sonnet-4
kilocode/openai/gpt-5.4
kilocode/google/gemini-3-pro-preview
...и многие другие
```

## Примечания

- Ссылки на модели имеют вид `kilocode/<model-id>` (например, `kilocode/anthropic/claude-sonnet-4`).
- Модель по умолчанию: `kilocode/kilo/auto`.
- Базовый URL: `https://api.kilo.ai/api/gateway/`.
- В bundled fallback catalog всегда включена `kilocode/kilo/auto` (`Kilo Auto`) со следующими параметрами: `input: ["text", "image"]`, `reasoning: true`, `contextWindow: 1000000` и `maxTokens: 128000`.
- При запуске OpenClaw выполняет запрос `GET https://api.kilo.ai/api/gateway/models` и объединяет обнаруженные модели с статическим fallback catalog.
- Точная маршрутизация на уровне вышестоящих сервисов за `kilocode/kilo/auto` контролируется Kilo Gateway, а не жёстко задана в OpenClaw.
- Kilo Gateway в исходном коде описан как совместимый с OpenRouter, поэтому он следует пути, совместимому с OpenAI в стиле прокси, а не формирует запросы в нативном формате OpenAI.
- Ссылки Kilo на основе Gemini следуют пути proxy-Gemini, поэтому OpenClaw сохраняет очистку сигнатур мыслей Gemini без включения нативной проверки воспроизведения Gemini или перезаписи начальной загрузки.
- Общий обёртки потока Kilo добавляет заголовок приложения провайдера и нормализует полезные нагрузки рассуждений для поддерживаемых конкретных ссылок на модели. `kilocode/kilo/auto` и другие ссылки, не поддерживающие proxy-reasoning, пропускают эту инъекцию рассуждений.
- Дополнительные варианты моделей и провайдеров см. в [/concepts/model-providers](/concepts/model-providers).
- Kilo Gateway использует токен Bearer с вашим API-ключом на внутреннем уровне.