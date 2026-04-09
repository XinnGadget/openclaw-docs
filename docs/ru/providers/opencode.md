---
summary: "Использовать каталоги OpenCode Zen и Go с OpenClaw"
read_when:
  - Вам нужен доступ к моделям, размещённым на OpenCode
  - Вы хотите выбрать между каталогами Zen и Go
title: "OpenCode"
---

# OpenCode

OpenCode предоставляет два размещённых каталога в OpenClaw:

- `opencode/...` — для каталога **Zen**;
- `opencode-go/...` — для каталога **Go**.

Оба каталога используют один и тот же API-ключ OpenCode. OpenClaw разделяет идентификаторы провайдеров среды выполнения, чтобы маршрутизация для каждой модели оставалась корректной. При этом в процессе подключения и в документации они рассматриваются как единая настройка OpenCode.

## Настройка через CLI

### Каталог Zen

```bash
openclaw onboard --auth-choice opencode-zen
openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
```

### Каталог Go

```bash
openclaw onboard --auth-choice opencode-go
openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
```

## Фрагмент конфигурации

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## Каталоги

### Zen

- Провайдер среды выполнения: `opencode`.
- Примеры моделей: `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro`.
- Подходит, если вам нужен кураторский мультимодельный прокси OpenCode.

### Go

- Провайдер среды выполнения: `opencode-go`.
- Примеры моделей: `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5`.
- Подходит, если вам нужна линейка моделей Kimi/GLM/MiniMax, размещённая на OpenCode.

## Примечания

- Также поддерживается `OPENCODE_ZEN_API_KEY`.
- При вводе одного ключа OpenCode в процессе настройки учётные данные сохраняются для обоих провайдеров среды выполнения.
- Вам нужно войти в OpenCode, добавить платёжные данные и скопировать свой API-ключ.
- Управление биллингом и доступностью каталогов осуществляется через панель управления OpenCode.
- Ссылки OpenCode на основе Gemini остаются на пути прокси-Gemini, поэтому OpenClaw сохраняет очистку сигнатур мыслей Gemini без включения нативной проверки повторов Gemini или перезаписи начальной загрузки.
- Для ссылок OpenCode, не связанных с Gemini, действует минимальная политика повторов, совместимая с OpenAI.