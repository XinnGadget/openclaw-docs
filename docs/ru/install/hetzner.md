---
summary: "Запустить OpenClaw Gateway круглосуточно на недорогом VPS от Hetzner (Docker) с устойчивым состоянием и встроенными бинарными файлами"
read_when:
  - Вам нужно, чтобы OpenClaw работал круглосуточно на облачном VPS (не на ноутбуке)
  - Вам нужен Gateway промышленного уровня, работающий без остановок, на вашем собственном VPS
  - Вам нужен полный контроль над сохранением состояния, бинарными файлами и поведением при перезапуске
  - Вы запускаете OpenClaw в Docker на Hetzner или аналогичном провайдере
title: "Hetzner"
---

# OpenClaw на Hetzner (Docker, руководство по развёртыванию на VPS)

## Цель

Запустить устойчивый OpenClaw Gateway на VPS от Hetzner с использованием Docker, обеспечив устойчивое состояние, встроенные бинарные файлы и безопасное поведение при перезапуске.

Если вам нужно "OpenClaw 24/7 примерно за 5 долларов", это самая простая надёжная конфигурация.
Цены Hetzner могут меняться; выберите самый недорогой VPS с Debian/Ubuntu и увеличьте ресурсы, если столкнётесь с ошибкой нехватки памяти (OOM).

Напоминание о модели безопасности:

- Агенты, используемые совместно в компании, допустимы, если все находятся в одной зоне доверия и среда выполнения используется только для бизнес-задач.
- Соблюдайте строгую изоляцию: отдельный VPS/среда выполнения + отдельные учётные записи; не используйте личные профили Apple/Google/браузера/менеджера паролей на этом хосте.
- Если пользователи потенциально враждебны по отношению друг к другу, разделите их по шлюзу/хосту/пользователю ОС.

См. [Безопасность](/gateway/security) и [Хостинг VPS](/vps).

## Что мы делаем (простыми словами)?

- Арендовать небольшой Linux-сервер (VPS от Hetzner)
- Установить Docker (изолированная среда выполнения приложений)
- Запустить OpenClaw Gateway в Docker
- Сохранить `~/.openclaw` + `~/.openclaw/workspace` на хосте (данные сохраняются при перезапусках/пересборах)
- Получить доступ к интерфейсу управления с ноутбука через SSH-туннель

Подключённое состояние `~/.openclaw` включает `openclaw.json`, файлы `agents/<agentId>/agent/auth-profiles.json` для каждого агента и `.env`.

Доступ к Gateway можно получить следующими способами:

- Через переадресацию портов SSH с ноутбука
- Через прямой доступ к порту, если вы самостоятельно управляете брандмауэром и токенами

В этом руководстве предполагается использование Ubuntu или Debian на Hetzner.
Если вы используете другой Linux VPS, адаптируйте пакеты соответствующим образом.
Для общего процесса работы с Docker см. [Docker](/install/docker).

---

## Быстрый путь (для опытных операторов)

1. Развёртывание VPS от Hetzner
2. Установка Docker
3. Клонирование репозитория OpenClaw
4. Создание устойчивых каталогов на хосте
5. Настройка `.env` и `docker-compose.yml`
6. Встраивание необходимых бинарных файлов в образ
7. `docker compose up -d`
8. Проверка сохранения состояния и доступа к Gateway

---

## Что вам понадобится

- VPS от Hetzner с доступом root
- Доступ по SSH с ноутбука
- Базовые навыки работы с SSH (копирование/вставка)
- Около 20 минут времени
- Docker и Docker Compose
- Учётные данные для аутентификации модели
- Опциональные учётные данные провайдера:
  - QR-код WhatsApp
  - Токен бота Telegram
  - OAuth для Gmail

---

<Steps>
  <Step title="Развёртывание VPS">
    Создайте VPS с Ubuntu или Debian на Hetzner.

    Подключитесь как root:

    ```bash
    ssh root@YOUR_VPS_IP
    ```

    В этом руководстве предполагается, что VPS имеет устойчивое состояние.
    Не рассматривайте его как одноразовую инфраструктуру.

  </Step>

  <Step title="Установка Docker (на VPS)">
    ```bash
    apt-get update
    apt-get install -y git curl ca-certificates
    curl -fsSL https://get.docker.com | sh
    ```

    Проверка:

    ```bash
    docker --version
    docker compose version
    ```

  </Step>

  <Step title="Клонирование репозитория OpenClaw">
    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    ```

    В этом руководстве предполагается, что вы соберёте собственный образ, чтобы гарантировать сохранение бинарных файлов.

  </Step>

  <Step title="Создание устойчивых каталогов на хосте">
    Контейнеры Docker эфемерны.
    Все долгосрочные данные должны храниться на хосте.

    ```bash
    mkdir -p /root/.openclaw/workspace

    # Назначить владельца — пользователя контейнера (uid 1000):
    chown -R 1000:1000 /root/.openclaw
    ```

  </Step>

  <Step title="Настройка переменных окружения">
    Создайте файл `.env` в корне репозитория.

    ```bash
    OPENCLAW_IMAGE=openclaw:latest
    OPENCLAW_GATEWAY_TOKEN=change-me-now
    OPENCLAW_GATEWAY_BIND=lan
    OPENCLAW_GATEWAY_PORT=18789

    OPENCLAW_CONFIG_DIR=/root/.openclaw
    OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace

    GOG_KEYRING_PASSWORD=change-me-now
    XDG_CONFIG_HOME=/home/node/.openclaw
    ```

    Сгенерируйте надёжные секреты:

    ```bash
    openssl rand -hex 32
    ```

    **Не добавляйте этот файл в систему контроля версий.**

    Этот файл `.env` предназначен для переменных окружения контейнера/среды выполнения, таких как `OPENCLAW_GATEWAY_TOKEN`.
    Сохранённые учётные данные OAuth/API-ключей провайдера хранятся в подключённом каталоге `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`.

  </Step>

  <Step title="Настройка Docker Compose">
    Создайте или обновите файл `docker-compose.yml`.

    ```yaml
    services:
      openclaw-gateway:
        image: ${OPENCLAW_IMAGE}
        build: .
        restart: unless-stopped
        env_file:
          - .env
        environment:
          - HOME=/home/node
          - NODE_ENV=production
          - TERM=xterm-256color
          - OPENCLAW_GATEWAY_BIND=${OPENCLAW_GATEWAY_BIND}
          - OPENCLAW_GATEWAY_PORT=${OPENCLAW_GATEWAY_PORT}
          - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
          - GOG_KEYRING_PASSWORD=${GOG_KEYRING_PASSWORD}
          - XDG_CONFIG_HOME=${XDG_CONFIG_HOME}
          - PATH=/home/linuxbrew/.linuxbrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        volumes:
          - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
          - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
        ports:
          # Рекомендуется: оставить Gateway доступным только через loopback на VPS; доступ через SSH-туннель.
          # Чтобы открыть доступ публично, удалите префикс `127.0.0.1:` и настройте брандмауэр соответствующим образом.
          - "127.0.0.1:${OPENCLAW_GATEWAY_PORT}:18789"
        command:
          [
            "node",
            "dist/index.js",
            "gateway",
            "--bind",
            "${OPENCLAW_GATEWAY_BIND}",
            "--port",
            "${OPENCLAW_GATEWAY_PORT}",
            "--allow-unconfigured",
          ]
    ```

    Параметр `--allow-unconfigured` предназначен только для удобства начальной настройки, он не заменяет надлежащую конфигурацию шлюза. Обязательно настройте аутентификацию (`gateway.auth.token` или пароль) и используйте безопасные настройки привязки для вашего развёртывания.

  </Step>

  <Step title="Общие шаги для среды выполнения Docker VM">
    Используйте руководство по общей среде выполнения Docker для стандартного процесса работы с хостом Docker:

    - [Встраивание необходимых бинарных файлов в образ](/install/docker-vm-runtime#bake-required-binaries-into-the-image)
    - [Сборка и запуск](/install/docker-vm-runtime#build-and-launch)
    - [Что и где сохраняется](/install/docker-vm-