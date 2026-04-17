---
read_when:
    - Ви хочете використовувати підписку Claude Max з інструментами, сумісними з OpenAI
    - Ви хочете локальний API-сервер, який обгортає CLI Claude Code
    - Ви хочете оцінити доступ Anthropic на основі підписки порівняно з доступом на основі API-ключа
summary: Проксі від спільноти для надання облікових даних підписки Claude як сумісної з OpenAI кінцевої точки
title: Проксі API Claude Max
x-i18n:
    generated_at: "2026-04-12T10:19:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Проксі API Claude Max

**claude-max-api-proxy** — це інструмент спільноти, який надає вашу підписку Claude Max/Pro як API-ендпойнт, сумісний з OpenAI. Це дає змогу використовувати вашу підписку з будь-яким інструментом, що підтримує формат API OpenAI.

<Warning>
Цей шлях є лише технічною сумісністю. У минулому Anthropic блокував певне
використання підписки поза Claude Code. Ви повинні самостійно вирішити, чи
використовувати це, і перевірити актуальні умови Anthropic, перш ніж покладатися на нього.
</Warning>

## Навіщо це використовувати?

| Підхід                  | Вартість                                            | Найкраще підходить для                    |
| ----------------------- | --------------------------------------------------- | ----------------------------------------- |
| API Anthropic           | Оплата за токен (~$15/млн вхідних, $75/млн вихідних для Opus) | Продакшн-застосунків, великих обсягів     |
| Підписка Claude Max     | $200/місяць фіксовано                               | Особистого використання, розробки, необмеженого використання |

Якщо у вас є підписка Claude Max і ви хочете використовувати її з інструментами, сумісними з OpenAI, цей проксі може зменшити витрати для деяких робочих процесів. API-ключі залишаються більш зрозумілим шляхом з погляду політик для використання у продакшні.

## Як це працює

```plaintext
Ваш застосунок → claude-max-api-proxy → CLI Claude Code → Anthropic (через підписку)
     (формат OpenAI)                 (перетворює формат)     (використовує ваш вхід)
```

Проксі:

1. Приймає запити у форматі OpenAI на `http://localhost:3456/v1/chat/completions`
2. Перетворює їх на команди CLI Claude Code
3. Повертає відповіді у форматі OpenAI (підтримується потокова передача)

## Початок роботи

<Steps>
  <Step title="Встановіть проксі">
    Потрібні Node.js 20+ і CLI Claude Code.

    ```bash
    npm install -g claude-max-api-proxy

    # Verify Claude CLI is authenticated
    claude --version
    ```

  </Step>
  <Step title="Запустіть сервер">
    ```bash
    claude-max-api
    # Server runs at http://localhost:3456
    ```
  </Step>
  <Step title="Перевірте проксі">
    ```bash
    # Health check
    curl http://localhost:3456/health

    # List models
    curl http://localhost:3456/v1/models

    # Chat completion
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="Налаштуйте OpenClaw">
    Спрямуйте OpenClaw на проксі як на користувацький ендпойнт, сумісний з OpenAI:

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

  </Step>
</Steps>

## Доступні моделі

| ID моделі         | Відповідає      |
| ----------------- | --------------- |
| `claude-opus-4`   | Claude Opus 4   |
| `claude-sonnet-4` | Claude Sonnet 4 |
| `claude-haiku-4`  | Claude Haiku 4  |

## Додатково

<AccordionGroup>
  <Accordion title="Нотатки щодо проксі-стилю сумісності з OpenAI">
    Цей шлях використовує той самий маршрут сумісності з OpenAI у стилі проксі, що й інші користувацькі
    бекенди `/v1`:

    - Власне OpenAI-специфічне формування запитів не застосовується
    - Немає `service_tier`, немає Responses `store`, немає підказок кешу промптів і немає
      формування payload сумісності міркування OpenAI
    - Приховані заголовки атрибуції OpenClaw (`originator`, `version`, `User-Agent`)
      не додаються до URL проксі

  </Accordion>

  <Accordion title="Автозапуск на macOS за допомогою LaunchAgent">
    Створіть LaunchAgent, щоб автоматично запускати проксі:

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

  </Accordion>
</AccordionGroup>

## Посилання

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Проблеми:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## Примітки

- Це **інструмент спільноти**, який не підтримується офіційно Anthropic або OpenClaw
- Потрібна активна підписка Claude Max/Pro з автентифікованим CLI Claude Code
- Проксі працює локально й не надсилає дані на жодні сторонні сервери
- Потокові відповіді повністю підтримуються

<Note>
Для нативної інтеграції Anthropic з CLI Claude або API-ключами див. [провайдер Anthropic](/uk/providers/anthropic). Для підписок OpenAI/Codex див. [провайдер OpenAI](/uk/providers/openai).
</Note>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Провайдер Anthropic" href="/uk/providers/anthropic" icon="bolt">
    Нативна інтеграція OpenClaw з CLI Claude або API-ключами.
  </Card>
  <Card title="Провайдер OpenAI" href="/uk/providers/openai" icon="robot">
    Для підписок OpenAI/Codex.
  </Card>
  <Card title="Провайдери моделей" href="/uk/concepts/model-providers" icon="layers">
    Огляд усіх провайдерів, посилань на моделі та поведінки відмовостійкості.
  </Card>
  <Card title="Налаштування" href="/uk/gateway/configuration" icon="gear">
    Повний довідник з конфігурації.
  </Card>
</CardGroup>
