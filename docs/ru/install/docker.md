---
summary: "Необязательная настройка и ввод в эксплуатацию OpenClaw на базе Docker"
read_when:
  - Вам нужен шлюз в контейнере вместо локальной установки
  - Вы проверяете рабочий процесс с Docker
title: "Docker"
---

# Docker (необязательный компонент)

Docker **необязателен**. Используйте его только в том случае, если вам нужен шлюз в контейнере или вы хотите проверить рабочий процесс с Docker.

## Подходит ли мне Docker?

- **Да**: вам нужна изолированная временная среда шлюза или вы хотите запустить OpenClaw на хосте без локальных установок.
- **Нет**: вы работаете на собственном компьютере и хотите максимально ускорить цикл разработки. В этом случае используйте обычный процесс установки.
- **Примечание о песочнице**: для изоляции агентов тоже используется Docker, но для этого **не** требуется запускать весь шлюз в Docker. См. [Песочница](/gateway/sandboxing).

## Предварительные требования

- Docker Desktop (или Docker Engine) + Docker Compose v2;
- Не менее 2 ГБ ОЗУ для сборки образа (при 1 ГБ на хосте команда `pnpm install` может быть прервана из-за нехватки памяти с кодом выхода 137);
- Достаточно места на диске для образов и журналов;
- Если вы работаете на VPS/публичном хосте, ознакомьтесь с разделом [Усиление безопасности при сетевом доступе](/gateway/security), особенно с политикой брандмауэра Docker `DOCKER-USER`.

## Шлюз в контейнере

<Steps>
  <Step title="Сборка образа">
    Из корневой директории репозитория запустите скрипт настройки:

    ```bash
    ./scripts/docker/setup.sh
    ```

    Это соберёт образ шлюза локально. Чтобы вместо этого использовать предварительно собранный образ:

    ```bash
    export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
    ./scripts/docker/setup.sh
    ```

    Предварительно собранные образы публикуются в [реестре контейнеров GitHub](https://github.com/openclaw/openclaw/pkgs/container/openclaw).
    Распространённые теги: `main`, `latest`, `<версия>` (например, `2026.2.26`).

  </Step>

  <Step title="Завершение ввода в эксплуатацию">
    Скрипт настройки автоматически выполняет ввод в эксплуатацию. Он:

    - запросит ключи API провайдера;
    - сгенерирует токен шлюза и запишет его в файл `.env`;
    - запустит шлюз через Docker Compose.

    Во время настройки предварительные действия перед запуском и запись конфигурации выполняются напрямую через `openclaw-gateway`. `openclaw-cli` предназначен для команд, которые вы выполняете после того, как контейнер шлюза уже создан.

  </Step>

  <Step title="Открытие интерфейса управления">
    Откройте в браузере `http://127.0.0.1:18789/` и вставьте сконфигурированный общий секрет в настройки. По умолчанию скрипт настройки записывает токен в файл `.env`; если вы переключили конфигурацию контейнера на аутентификацию по паролю, используйте этот пароль.

    Нужно снова получить URL?

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    ```

  </Step>

  <Step title="Настройка каналов (необязательно)">
    Используйте контейнер CLI для добавления каналов обмена сообщениями:

    ```bash
    # WhatsApp (QR)
    docker compose run --rm openclaw-cli channels login

    # Telegram
    docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

    # Discord
    docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
    ```

    Документация: [WhatsApp](/channels/whatsapp), [Telegram](/channels/telegram), [Discord](/channels/discord)

  </Step>
</Steps>

### Ручной процесс

Если вы предпочитаете выполнять каждый шаг самостоятельно, а не использовать скрипт настройки:

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"},{"path":"gateway.controlUi.allowedOrigins","value":["http://localhost:18789","http://127.0.0.1:18789"]}]'
docker compose up -d openclaw-gateway
```

<Note>
Запускайте `docker compose` из корневой директории репозитория. Если вы включили `OPENCLAW_EXTRA_MOUNTS` или `OPENCLAW_HOME_VOLUME`, скрипт настройки создаст файл `docker-compose.extra.yml`; включите его с помощью `-f docker-compose.yml -f docker-compose.extra.yml`.
</Note>

<Note>
Поскольку `openclaw-cli` использует то же сетевое пространство имён, что и `openclaw-gateway`, это инструмент для работы после запуска. До выполнения `docker compose up -d openclaw-gateway` выполните ввод в эксплуатацию и настройку конфигурации через `openclaw-gateway` с параметрами `--no-deps --entrypoint node`.
</Note>

### Переменные окружения

Скрипт настройки поддерживает следующие необязательные переменные окружения:

| Переменная | Назначение |
| --- | --- |
| `OPENCLAW_IMAGE` | Использовать удалённый образ вместо локальной сборки |
| `OPENCLAW_DOCKER_APT_PACKAGES` | Установить дополнительные пакеты apt во время сборки (через пробел) |
| `OPENCLAW_EXTENSIONS` | Предварительно установить зависимости расширений во время сборки (через пробел, указать имена) |
| `OPENCLAW_EXTRA_MOUNTS` | Дополнительные привязки хоста (через запятую, формат `source:target[:opts]`) |
| `OPENCLAW_HOME_VOLUME` | Сохранить `/home/node` в именованном томе Docker |
| `OPENCLAW_SANDBOX` | Включить загрузку песочницы (`1`, `true`, `yes`, `on`) |
| `OPENCLAW_DOCKER_SOCKET` | Переопределить путь к сокету Docker |

### Проверка работоспособности

Конечные точки для проверки контейнеров (аутентификация не требуется):

```bash
curl -fsS http://127.0.0.1:18789/healthz   # проверка живучести
curl -fsS http://127.0.0.1:18789/readyz     # проверка готовности
```

Образ Docker включает встроенную проверку `HEALTHCHECK`, которая отправляет запрос на `/healthz`.
Если проверки продолжают завершаться сбоем, Docker помечает контейнер как `неработоспособный`, и системы оркестрации могут перезапустить или заменить его.

Аутентифицированный подробный снимок состояния работоспособности:

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### LAN против loopback

Скрипт `scripts/docker/setup.sh` по умолчанию устанавливает `OPENCLAW_GATEWAY_BIND=lan`, чтобы доступ хоста к `http://127.0.0.1:18789` работал с публикацией портов Docker.

- `lan` (по умолчанию): браузер хоста и CLI хоста могут получить доступ к опубликованному порту шлюза.
- `loopback`: только процессы внутри сетевого пространства имён контейнера могут напрямую получить доступ к шлюзу.

<Note>
Используйте значения режима привязки в `gateway.bind` (`lan` / `loopback` / `custom` / `tailnet` / `auto`), а не псевдонимы хоста, такие как `0.0.0.0` или `127.0.0.1`.
</Note>

### Хранение данных и сохранение состояния

Docker Compose привязывает `OPENCLAW_CONFIG_DIR` к `/home/node/.openclaw` и `OPENCLAW_WORKSPACE_DIR` к `/home/node/.openclaw/workspace`, поэтому эти пути сохраняются при замене контейнера.

В смонтированном каталоге конфигурации OpenClaw хранит:

- `openclaw.json` — конфигурация поведения;
- `agents/<agentId>/agent/auth-profiles.json` — сохранённые данные аутентификации провайдера (OAuth/ключи API);
- `.env` — секреты времени выполнения, хранящиеся в переменных окружения, такие как `OPENCLAW_GATEWAY_TOKEN`.

Для получения подробной информации о сохранении состояния при развёртывании на виртуальной машине см. раздел [Docker VM Runtime — что и где сохраняется](/install/docker-vm-runtime#what-persists-where).

**Области активного роста диска:** следите за каталогами `media/`, файлами сеансов JSONL, `cron/runs/*.jsonl` и журналами с ротацией в каталоге `/tmp/open