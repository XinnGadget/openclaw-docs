---
summary: "Прокси-сервер сообщества для предоставления учётных данных подписки Claude в виде конечной точки, совместимой с OpenAI"
read_when:
  - Вы хотите использовать подписку Claude Max с инструментами, совместимыми с OpenAI
  - Вам нужен локальный API-сервер, который оборачивает Claude Code CLI
  - Вы хотите сравнить доступ к Anthropic по подписке и по API-ключу
title: "Прокси-сервер Claude Max API"
---

# Прокси-сервер Claude Max API

**claude-max-api-proxy** — это инструмент сообщества, который предоставляет вашу подписку Claude Max/Pro в виде API-конечной точки, совместимой с OpenAI. Это позволяет использовать подписку с любым инструментом, поддерживающим формат API OpenAI.

<Warning>
Это обеспечивает только техническую совместимость. В прошлом Anthropic блокировала использование подписки вне Claude Code. Вы должны самостоятельно принять решение о том, использовать ли этот инструмент, и проверить текущие условия использования Anthropic, прежде чем полагаться на него.
</Warning>

## Зачем это использовать?

| Подход | Стоимость | Для чего лучше подходит |
| --- | --- | --- |
| API Anthropic | Оплата за токен (~15 долларов за 1 млн входных токенов, 75 долларов за 1 млн выходных токенов для Opus) | Производственные приложения, большой объём запросов |
| Подписка Claude Max | Фиксированная плата — 200 долларов в месяц | Личное использование, разработка, неограниченное использование |

Если у вас есть подписка Claude Max и вы хотите использовать её с инструментами, совместимыми с OpenAI, этот прокси-сервер может снизить затраты для некоторых рабочих процессов. Для производственного использования более чётким вариантом с точки зрения политики остаётся использование API-ключей.

## Как это работает

```
Ваше приложение → claude-max-api-proxy → Claude Code CLI → Anthropic (через подписку)
     (формат OpenAI)              (преобразует формат)      (использует ваши учётные данные)
```

Прокси-сервер:

1. Принимает запросы в формате OpenAI по адресу `http://localhost:3456/v1/chat/completions`.
2. Преобразует их в команды Claude Code CLI.
3. Возвращает ответы в формате OpenAI (поддерживается потоковая передача).

## Установка

```bash
# Требуется Node.js 20+ и Claude Code CLI
npm install -g claude-max-api-proxy

# Проверьте, что Claude CLI аутентифицирован
claude --version
```

## Использование

### Запуск сервера

```bash
claude-max-api
# Сервер работает по адресу http://localhost:3456
```

### Проверка работы

```bash
# Проверка работоспособности
curl http://localhost:3456/health

# Вывод списка моделей
curl http://localhost:3456/v1/models

# Получение ответа в чате
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### С OpenClaw

Вы можете указать OpenClaw на прокси-сервер как на пользовательскую конечную точку, совместимую с OpenAI:

```json5
{
  env: {
    OPENAI_API_KEY: "not-needed",
    OPENAI_BASE_URL: "http://localhost:3456/v1",
  },
  agents: {
    defaults: {
      model: { primary: "openai/claude-opus-4" },
    },
  },
}
```

Этот способ использует тот же прокси-стиль конечной точки, совместимой с OpenAI, что и другие пользовательские бэкенды `/v1`:

- собственное формирование запросов только для OpenAI не применяется;
- отсутствуют `service_tier`, хранилище ответов (`store`), подсказки кэширования промтов и формирование полезной нагрузки, совместимой с рассуждениями OpenAI;
- скрытые заголовки атрибуции OpenClaw (`originator`, `version`, `User-Agent`) не добавляются в URL прокси-сервера.

## Доступные модели

| ID модели | Соответствует |
| --- | --- |
| `claude-opus-4` | Claude Opus 4 |
| `claude-sonnet-4` | Claude Sonnet 4 |
| `claude-haiku-4` | Claude Haiku 4 |

## Автоматический запуск на macOS

Создайте LaunchAgent для автоматического запуска прокси-сервера:

```bash
cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.claude-max-api</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/node</string>
    <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
```

## Ссылки

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Проблемы:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## Примечания

- Это **инструмент сообщества**, официально не поддерживаемый Anthropic или OpenClaw.
- Требуется активная подписка Claude Max/Pro с аутентифицированным Claude Code CLI.
- Прокси-сервер работает локально и не отправляет данные на сторонние серверы.
- Потоковая передача ответов полностью поддерживается.

## См. также

- [Поставщик Anthropic](/providers/anthropic) — нативная интеграция OpenClaw с Claude CLI или API-ключами.
- [Поставщик OpenAI](/providers/openai) — для подписок OpenAI/Codex.