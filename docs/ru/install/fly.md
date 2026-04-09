---
title: Fly.io
summary: "Поэтапное развёртывание OpenClaw на Fly.io с постоянным хранилищем и HTTPS"
read_when:
  - Развёртывание OpenClaw на Fly.io
  - Настройка томов, секретов и начальной конфигурации на Fly
---

# Развёртывание на Fly.io

**Цель:** запустить OpenClaw Gateway на машине [Fly.io](https://fly.io) с постоянным хранилищем, автоматическим HTTPS и доступом к Discord/каналам.

## Что потребуется

- Установленный [flyctl CLI](https://fly.io/docs/hands-on/install-flyctl/)
- Аккаунт Fly.io (подходит бесплатный тариф)
- Ключ API для выбранного поставщика моделей (модельная аутентификация)
- Токены каналов: токен бота Discord, токен Telegram и т. д.

## Быстрый старт для новичков

1. Клонируйте репозиторий → настройте `fly.toml`
2. Создайте приложение и том → задайте секреты
3. Разверните с помощью `fly deploy`
4. Подключитесь по SSH, чтобы создать конфигурацию, или используйте Control UI

<Steps>
  <Step title="Создание приложения Fly">
    ```bash
    # Клонируйте репозиторий
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw

    # Создайте новое приложение Fly (выберите своё имя)
    fly apps create my-openclaw

    # Создайте постоянный том (обычно достаточно 1 ГБ)
    fly volumes create openclaw_data --size 1 --region iad
    ```

    **Совет:** выберите регион, ближайший к вам. Распространённые варианты: `lhr` (Лондон), `iad` (Вирджиния), `sjc` (Сан-Хосе).

  </Step>

  <Step title="Настройка fly.toml">
    Отредактируйте `fly.toml`, чтобы он соответствовал имени вашего приложения и требованиям.

    **Примечание по безопасности:** конфигурация по умолчанию предоставляет публичный URL. Для защищённого развёртывания без публичного IP см. раздел [Приватное развёртывание (защищённое)](#private-deployment-hardened) или используйте `fly.private.toml`.

    ```toml
    app = "my-openclaw"  # Имя вашего приложения
    primary_region = "iad"

    [build]
      dockerfile = "Dockerfile"

    [env]
      NODE_ENV = "production"
      OPENCLAW_PREFER_PNPM = "1"
      OPENCLAW_STATE_DIR = "/data"
      NODE_OPTIONS = "--max-old-space-size=1536"

    [processes]
      app = "node dist/index.js gateway --allow-unconfigured --port 3000 --bind lan"

    [http_service]
      internal_port = 3000
      force_https = true
      auto_stop_machines = false
      auto_start_machines = true
      min_machines_running = 1
      processes = ["app"]

    [[vm]]
      size = "shared-cpu-2x"
      memory = "2048mb"

    [mounts]
      source = "openclaw_data"
      destination = "/data"
    ```

    **Ключевые настройки:**

    | Настройка | Обоснование |
    | --- | --- |
    | `--bind lan` | Привязывает к `0.0.0.0`, чтобы прокси Fly мог получить доступ к шлюзу |
    | `--allow-unconfigured` | Запускает без файла конфигурации (вы создадите его позже) |
    | `internal_port = 3000` | Должен совпадать с `--port 3000` (или `OPENCLAW_GATEWAY_PORT`) для проверок работоспособности Fly |
    | `memory = "2048mb"` | 512 МБ недостаточно; рекомендуется 2 ГБ |
    | `OPENCLAW_STATE_DIR = "/data"` | Сохраняет состояние на томе |

  </Step>

  <Step title="Задание секретов">
    ```bash
    # Обязательно: токен шлюза (для привязки не через loopback)
    fly secrets set OPENCLAW_GATEWAY_TOKEN=$(openssl rand -hex 32)

    # Ключи API поставщиков моделей
    fly secrets set ANTHROPIC_API_KEY=sk-ant-...

    # Опционально: другие поставщики
    fly secrets set OPENAI_API_KEY=sk-...
    fly secrets set GOOGLE_API_KEY=...

    # Токены каналов
    fly secrets set DISCORD_BOT_TOKEN=MTQ...
    ```

    **Примечания:**

    - Привязки не через loopback (`--bind lan`) требуют действительного пути аутентификации шлюза. В этом примере Fly.io используется `OPENCLAW_GATEWAY_TOKEN`, но также подойдут `gateway.auth.password` или правильно настроенное развёртывание `trusted-proxy` не через loopback.
    - Обращайтесь с этими токенами как с паролями.
    - **Предпочитайте переменные окружения файлу конфигурации** для всех ключей API и токенов. Это позволит избежать попадания секретов в `openclaw.json`, где они могут быть случайно раскрыты или записаны в лог.

  </Step>

  <Step title="Развёртывание">
    ```bash
    fly deploy
    ```

    При первом развёртывании создаётся образ Docker (около 2–3 минут). Последующие развёртывания выполняются быстрее.

    После развёртывания проверьте:

    ```bash
    fly status
    fly logs
    ```

    Вы должны увидеть:

    ```
    [gateway] listening on ws://0.0.0.0:3000 (PID xxx)
    [discord] logged in to discord as xxx
    ```

  </Step>

  <Step title="Создание файла конфигурации">
    Подключитесь к машине по SSH, чтобы создать правильную конфигурацию:

    ```bash
    fly ssh console
    ```

    Создайте каталог и файл конфигурации:

    ```bash
    mkdir -p /data
    cat > /data/openclaw.json << 'EOF'
    {
      "agents": {
        "defaults": {
          "model": {
            "primary": "anthropic/claude-opus-4-6",
            "fallbacks": ["anthropic/claude-sonnet-4-6", "openai/gpt-5.4"]
          },
          "maxConcurrent": 4
        },
        "list": [
          {
            "id": "main",
            "default": true
          }
        ]
      },
      "auth": {
        "profiles": {
          "anthropic:default": { "mode": "token", "provider": "anthropic" },
          "openai:default": { "mode": "token", "provider": "openai" }
        }
      },
      "bindings": [
        {
          "agentId": "main",
          "match": { "channel": "discord" }
        }
      ],
      "channels": {
        "discord": {
          "enabled": true,
          "groupPolicy": "allowlist",
          "guilds": {
            "YOUR_GUILD_ID": {
              "channels": { "general": { "allow": true } },
              "requireMention": false
            }
          }
        }
      },
      "gateway": {
        "mode": "local",
        "bind": "auto"
      },
      "meta": {}
    }
    EOF
    ```

    **Примечание:** при `OPENCLAW_STATE_DIR=/data` путь к конфигурации — `/data/openclaw.json`.

    **Примечание:** токен Discord может быть взят из:

    - Переменной окружения: `DISCORD_BOT_TOKEN` (рекомендуется для секретов)
    - Файла конфигурации: `channels.discord.token`

    Если используется переменная окружения, добавлять токен в конфигурацию не нужно. Шлюз автоматически считывает `DISCORD_BOT_TOKEN`.

    Перезапустите, чтобы применить изменения:

    ```bash
    exit
    fly machine restart <machine-id>
    ```

  </Step>

  <Step title="Доступ к шлюзу">
    ### Control UI

    Откройте в браузере:

    ```bash
    fly open
    ```

    Или перейдите по адресу `https://my-openclaw.fly.dev/`

    Пройдите аутентификацию с помощью настроенного общего секрета. В этом руководстве используется токен шлюза из `OPENCLAW_GATEWAY_TOKEN`; если вы перешли на аутентификацию по паролю, используйте этот пароль.

    ### Логи

    ```bash
    fly logs              # Живые логи
    fly logs --no-tail    # Последние логи
    