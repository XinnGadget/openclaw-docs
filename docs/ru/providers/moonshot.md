---
summary: "Настройка Moonshot K2 и Kimi Coding (отдельные провайдеры + ключи)"
read_when:
  - Вам нужна настройка Moonshot K2 (Moonshot Open Platform) и Kimi Coding
  - Вам необходимо разобраться в отдельных эндпоинтах, ключах и ссылках на модели
  - Вам нужен готовый к копированию и вставке конфиг для любого из провайдеров
title: "Moonshot AI"
---

# Moonshot AI (Kimi)

Moonshot предоставляет API Kimi с эндпоинтами, совместимыми с OpenAI. Настройте провайдера и задайте модель по умолчанию — `moonshot/kimi-k2.5`, либо используйте Kimi Coding с `kimi/kimi-code`.

Текущие идентификаторы моделей Kimi K2:

[//]: # "moonshot-kimi-k2-ids:start"

- `kimi-k2.5`
- `kimi-k2-thinking`
- `kimi-k2-thinking-turbo`
- `kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-ids:end"

```bash
openclaw onboard --auth-choice moonshot-api-key
# или
openclaw onboard --auth-choice moonshot-api-key-cn
```

Kimi Coding:

```bash
openclaw onboard --auth-choice kimi-code-api-key
```

Примечание: Moonshot и Kimi Coding — отдельные провайдеры. Ключи не взаимозаменяемы, эндпоинты различаются, ссылки на модели тоже (Moonshot использует `moonshot/...`, Kimi Coding — `kimi/...`).

Поиск в интернете через Kimi также использует плагин Moonshot:

```bash
openclaw configure --section web
```

Выберите **Kimi** в разделе поиска в интернете, чтобы сохранить настройки в `plugins.entries.moonshot.config.webSearch.*`.

## Фрагмент конфигурации (Moonshot API)

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: {
        // moonshot-kimi-k2-aliases:start
        "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
        "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
        "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
        "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
        // moonshot-kimi-k2-aliases:end
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          // moonshot-kimi-k2-models:start
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-thinking",
            name: "Kimi K2 Thinking",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-thinking-turbo",
            name: "Kimi K2 Thinking Turbo",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-turbo",
            name: "Kimi K2 Turbo",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 16384,
          },
          // moonshot-kimi-k2-models:end
        ],
      },
    },
  },
}
```

## Kimi Coding

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: {
        "kimi/kimi-code": { alias: "Kimi" },
      },
    },
  },
}
```

## Поиск в интернете через Kimi

OpenClaw также предоставляет **Kimi** в качестве провайдера `web_search`, работающего на базе поиска в интернете Moonshot.

Интерактивная настройка может запросить:

- регион API Moonshot:
  - `https://api.moonshot.ai/v1`
  - `https://api.moonshot.cn/v1`
- модель поиска в интернете Kimi по умолчанию (по умолчанию — `kimi-k2.5`)

Настройки хранятся в `plugins.entries.moonshot.config.webSearch`:

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // или используйте KIMI_API_KEY / MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## Примечания

- Ссылки на модели Moonshot используют формат `moonshot/<modelId>`. Ссылки на модели Kimi Coding используют формат `kimi/<modelId>`.
- Текущая модель Kimi Coding по умолчанию — `kimi/kimi-code`. Устаревший идентификатор модели `kimi/k2p5` по-прежнему поддерживается для обеспечения совместимости.
- Для поиска в интернете через Kimi используется `KIMI_API_KEY` или `MOONSHOT_API_KEY`, по умолчанию используется эндпоинт `https://api.moonshot.ai/v1` и модель `kimi-k2.5`.
- Нативные эндпоинты Moonshot (`https://api.moonshot.ai/v1` и `https://api.moonshot.cn/v1`) поддерживают потоковую передачу данных через транспорт `openai-completions`. OpenClaw теперь определяет это на основе возможностей эндпоинта, поэтому совместимые пользовательские идентификаторы провайдера, нацеленные на те же нативные хосты Moonshot, наследуют такое же поведение при потоковой передаче.
- При необходимости переопределите ценовые параметры и метаданные контекста в `models.providers`.
- Если Moonshot опубликует другие ограничения контекста для модели, скорректируйте значение `contextWindow` соответствующим образом.
- Используйте `https://api.moonshot.ai/v1` для международного эндпоинта и `https://api.moonshot.cn/v1` для эндпоинта в Китае.
- Варианты при регистрации:
  - `moonshot-api-key` для `https://api.moonshot.ai/v1`
  - `moonshot-api-key-cn` для `https://api.moonshot.cn/v1`

## Нативный режим мышления (Moonshot)

Moonshot Kimi поддерживает бинарный нативный режим мышления:

- `thinking: { type: "enabled" }`
- `thinking: { type: "disabled" }`

Настройте его для каждой модели через `agents.defaults.models.<provider/model>.params`:

```json5
{
  agents: {
    defaults: {
      models: {
        "moonshot/kimi-k2.5": {
          params: {
            thinking: { type: "disabled" },
          },
        },
      },
    },
  },
