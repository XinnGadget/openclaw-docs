---
summary: "Запустить OpenClaw в контейнере Podman без прав root"
read_when:
  - Вам нужен контейнерный шлюз с Podman вместо Docker
title: "Podman"
---

# Podman

Запустите OpenClaw Gateway в контейнере Podman без прав root, управляемом текущим пользователем без привилегий суперпользователя.

Предполагаемая модель:

- Podman запускает контейнер шлюза.
- Ваш хостовый CLI `openclaw` — это плоскость управления.
- Постоянное состояние по умолчанию хранится на хосте в каталоге `~/.openclaw`.
- Повседневное управление осуществляется с помощью `openclaw --container <имя> ...` вместо `sudo -u openclaw`, `podman exec` или отдельного сервисного пользователя.

## Предварительные требования

- **Podman** в режиме без прав root
- **OpenClaw CLI**, установленный на хосте
- **Опционально:** `systemd --user`, если вы хотите автозапуск, управляемый Quadlet
- **Опционально:** `sudo` — только если вы хотите выполнить `loginctl enable-linger "$(whoami)"` для сохранения работы при загрузке на безголовом хосте

## Быстрый старт

<Steps>
  <Step title="Одноразовая настройка">
    Из корня репозитория выполните `./scripts/podman/setup.sh`.
  </Step>

  <Step title="Запуск контейнера шлюза">
    Запустите контейнер с помощью `./scripts/run-openclaw-podman.sh launch`.
  </Step>

  <Step title="Выполнение начальной настройки внутри контейнера">
    Выполните `./scripts/run-openclaw-podman.sh launch setup`, затем откройте `http://127.0.0.1:18789/`.
  </Step>

  <Step title="Управление работающим контейнером из CLI хоста">
    Установите `OPENCLAW_CONTAINER=openclaw`, затем используйте обычные команды `openclaw` с хоста.
  </Step>
</Steps>

Детали настройки:

- `./scripts/podman/setup.sh` по умолчанию собирает `openclaw:local` в вашем хранилище Podman без прав root или использует `OPENCLAW_IMAGE` / `OPENCLAW_PODMAN_IMAGE`, если вы их задали.
- Создаёт файл `~/.openclaw/openclaw.json` с `gateway.mode: "local"`, если его нет.
- Создаёт файл `~/.openclaw/.env` с `OPENCLAW_GATEWAY_TOKEN`, если его нет.
- Для ручного запуска вспомогательный скрипт считывает только небольшой список разрешённых ключей, связанных с Podman, из `~/.openclaw/.env` и передаёт явные переменные окружения во время выполнения в контейнер; он не передаёт полный файл окружения в Podman.

Настройка с управлением через Quadlet:

```bash
./scripts/podman/setup.sh --quadlet
```

Quadlet — опция только для Linux, поскольку она зависит от пользовательских сервисов systemd.

Вы также можете установить `OPENCLAW_PODMAN_QUADLET=1`.

Дополнительные переменные окружения для сборки/настройки:

- `OPENCLAW_IMAGE` или `OPENCLAW_PODMAN_IMAGE` — используйте существующий/загруженный образ вместо сборки `openclaw:local`
- `OPENCLAW_DOCKER_APT_PACKAGES` — установите дополнительные пакеты apt во время сборки образа
- `OPENCLAW_EXTENSIONS` — предварительно установите зависимости расширений во время сборки

Запуск контейнера:

```bash
./scripts/run-openclaw-podman.sh launch
```

Скрипт запускает контейнер с вашим текущим uid/gid с параметром `--userns=keep-id` и подключает состояние OpenClaw к контейнеру через bind-mount.

Начальная настройка:

```bash
./scripts/run-openclaw-podman.sh launch setup
```

Затем откройте `http://127.0.0.1:18789/` и используйте токен из `~/.openclaw/.env`.

Настройка CLI хоста по умолчанию:

```bash
export OPENCLAW_CONTAINER=openclaw
```

После этого команды вроде следующих будут выполняться внутри этого контейнера автоматически:

```bash
openclaw dashboard --no-open
openclaw gateway status --deep   # включает дополнительное сканирование сервисов
openclaw doctor
openclaw channels login
```

На macOS Podman machine может привести к тому, что браузер будет восприниматься шлюзом как нелокальный.
Если в Control UI после запуска появляются ошибки аутентификации устройства, воспользуйтесь рекомендациями по работе с Tailscale в разделе
[Podman + Tailscale](#podman--tailscale).

<a id="podman--tailscale"></a>

## Podman + Tailscale

Для HTTPS или удалённого доступа через браузер следуйте основным документам Tailscale.

Примечание для Podman:

- Оставьте хост публикации Podman как `127.0.0.1`.
- Предпочитайте управляемый хостом `tailscale serve` вместо `openclaw gateway --tailscale serve`.
- На macOS, если контекст аутентификации устройства в локальном браузере ненадёжен, используйте доступ через Tailscale вместо временных решений с локальным туннелем.

Смотрите:

- [Tailscale](/gateway/tailscale)
- [Control UI](/web/control-ui)

## Systemd (Quadlet, опционально)

Если вы выполнили `./scripts/podman/setup.sh --quadlet`, настройка установит файл Quadlet по адресу:

```bash
~/.config/containers/systemd/openclaw.container
```

Полезные команды:

- **Запуск:** `systemctl --user start openclaw.service`
- **Остановка:** `systemctl --user stop openclaw.service`
- **Статус:** `systemctl --user status openclaw.service`
- **Логи:** `journalctl --user -u openclaw.service -f`

После редактирования файла Quadlet:

```bash
systemctl --user daemon-reload
systemctl --user restart openclaw.service
```

Для сохранения работы при загрузке на SSH/безголовых хостах включите lingering для вашего текущего пользователя:

```bash
sudo loginctl enable-linger "$(whoami)"
```

## Конфигурация, окружение и хранилище

- **Каталог конфигурации:** `~/.openclaw`
- **Каталог рабочей области:** `~/.openclaw/workspace`
- **Файл токена:** `~/.openclaw/.env`
- **Вспомогательный скрипт запуска:** `./scripts/run-openclaw-podman.sh`

Скрипт запуска и Quadlet подключают состояние хоста к контейнеру через bind-mount:

- `OPENCLAW_CONFIG_DIR` -> `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR` -> `/home/node/.openclaw/workspace`

По умолчанию это каталоги хоста, а не анонимное состояние контейнера, поэтому `openclaw.json`, `auth-profiles.json` для каждого агента, состояние каналов/провайдеров, сессии и рабочая область сохраняются при замене контейнера.
Настройка Podman также задаёт `gateway.controlUi.allowedOrigins` для `127.0.0.1` и `localhost` на опубликованном порту шлюза, чтобы локальная панель управления работала с нелокальным bind контейнера.

Полезные переменные окружения для ручного запуска:

- `OPENCLAW_PODMAN_CONTAINER` — имя контейнера (`openclaw` по умолчанию)
- `OPENCLAW_PODMAN_IMAGE` / `OPENCLAW_IMAGE` — образ для запуска
- `OPENCLAW_PODMAN_GATEWAY_HOST_PORT` — порт хоста, сопоставленный с портом контейнера `18789`
- `OPENCLAW_PODMAN_BRIDGE_HOST_PORT` — порт хоста, сопоставленный с портом контейнера `18790`
- `OPENCLAW_PODMAN_PUBLISH_HOST` — интерфейс хоста для опубликованных портов; по умолчанию `127.0.0.1`
- `OPENCLAW_GATEWAY_BIND` — режим привязки шлюза внутри контейнера; по умолчанию `lan`
- `OPENCLAW_PODMAN_USERNS` — `keep-id` (по умолчанию), `auto` или `host`

Ручной запуск считывает `~/.openclaw/.env` перед окончательным определением значений по умолчанию для контейнера/образа, поэтому вы можете сохранить их там.

Если вы используете нестандартный `OPENCLAW_CONFIG_DIR` или `OPENCLAW_WORKSPACE_DIR`, задайте те же переменные как для `./scripts/podman/setup.sh`, так и для последующих команд `./scripts/run-openclaw-podman.sh launch`. Локальный для репозитория скрипт запуска не сохраняет переопределения пользовательских путей между оболочками.

Примечание о Quadlet:

- Сгенерированный сервис Quadlet намеренно сохраняет фиксированную, усиленную конфигурацию по умолчанию: порты, опубликованные на `127.0.0.1`, `--bind lan` внутри контейнера и пространство имён пользователя `keep-id`.
- Он задаёт `OPENCLAW_NO