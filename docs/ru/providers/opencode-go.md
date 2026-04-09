---
summary: "Использовать каталог OpenCode Go с общей настройкой OpenCode"
read_when:
  - Вам нужен каталог OpenCode Go
  - Вам нужны ссылки на модели времени выполнения для моделей, размещённых на Go
title: "OpenCode Go"
---

# OpenCode Go

OpenCode Go — это каталог на Go в рамках [OpenCode](/providers/opencode).
Он использует тот же `OPENCODE_API_KEY`, что и каталог Zen, но сохраняет идентификатор провайдера времени выполнения `opencode-go`, чтобы маршрутизация для каждой модели на вышестоящем уровне оставалась корректной.

## Поддерживаемые модели

- `opencode-go/kimi-k2.5`
- `opencode-go/glm-5`
- `opencode-go/minimax-m2.5`

## Настройка CLI

```bash
openclaw onboard --auth-choice opencode-go
# или в неинтерактивном режиме
openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
```

## Фрагмент конфигурации

```json5
{
  env: { OPENCODE_API_KEY: "YOUR_API_KEY_HERE" }, // pragma: allowlist secret
  agents: { defaults: { model: { primary: "opencode-go/kimi-k2.5" } } },
}
```

## Поведение маршрутизации

OpenClaw автоматически обрабатывает маршрутизацию для каждой модели, если в ссылке на модель используется `opencode-go/...`.

## Примечания

- Используйте [OpenCode](/providers/opencode) для общей регистрации и обзора каталога.
- Ссылки на время выполнения остаются явными: `opencode/...` для Zen, `opencode-go/...` для Go.