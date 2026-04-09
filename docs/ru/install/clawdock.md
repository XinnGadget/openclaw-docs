---
summary: "Вспомогательные скрипты ClawDock для установки OpenClaw на базе Docker"
read_when:
  - Вы часто запускаете OpenClaw с Docker и хотите сократить повседневные команды
  - Вам нужен вспомогательный слой для панели управления, логов, настройки токенов и процессов сопряжения
title: "ClawDock"
---

# ClawDock

ClawDock — это небольшой слой вспомогательных скриптов для установок OpenClaw на базе Docker.

Он предоставляет короткие команды, такие как `clawdock-start`, `clawdock-dashboard` и `clawdock-fix-token`, вместо более длинных вызовов `docker compose ...`.

Если вы ещё не настроили Docker, начните с [Docker](/install/docker).

## Установка

Используйте канонический путь к вспомогательным скриптам:

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/clawdock/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

Если вы ранее устанавливали ClawDock из `scripts/shell-helpers/clawdock-helpers.sh`, переустановите его из нового пути `scripts/clawdock/clawdock-helpers.sh`. Старый путь к сырым файлам на GitHub был удалён.

## Что вы получаете

### Основные операции

| Команда | Описание |
| ------------------ | ---------------------- |
| `clawdock-start` | Запустить шлюз |
| `clawdock-stop` | Остановить шлюз |
| `clawdock-restart` | Перезапустить шлюз |
| `clawdock-status` | Проверить статус контейнера |
| `clawdock-logs` | Следить за логами шлюза |

### Доступ к контейнеру

| Команда | Описание |
| ------------------------- | --------------------------------------------- |
| `clawdock-shell` | Открыть оболочку внутри контейнера шлюза |
| `clawdock-cli <command>` | Выполнить команды OpenClaw CLI в Docker |
| `clawdock-exec <command>` | Выполнить произвольную команду в контейнере |

### Веб-интерфейс и сопряжение

| Команда | Описание |
| ----------------------- | ---------------------------- |
| `clawdock-dashboard` | Открыть URL панели управления |
| `clawdock-devices` | Вывести список ожидающих сопряжений устройств |
| `clawdock-approve <id>` | Одобрить запрос на сопряжение |

### Настройка и обслуживание

| Команда | Описание |
| -------------------- | ------------------------------------------------ |
| `clawdock-fix-token` | Настроить токен шлюза внутри контейнера |
| `clawdock-update` | Загрузить, пересобрать и перезапустить |
| `clawdock-rebuild` | Пересобрать только образ Docker |
| `clawdock-clean` | Удалить контейнеры и тома |

### Утилиты

| Команда | Описание |
| ---------------------- | --------------------------------------- |
| `clawdock-health` | Выполнить проверку работоспособности шлюза |
| `clawdock-token` | Вывести токен шлюза |
| `clawdock-cd` | Перейти в каталог проекта OpenClaw |
| `clawdock-config` | Открыть `~/.openclaw` |
| `clawdock-show-config` | Вывести файлы конфигурации с замаскированными значениями |
| `clawdock-workspace` | Открыть каталог рабочей области |

## Первый запуск

```bash
clawdock-start
clawdock-fix-token
clawdock-dashboard
```

Если в браузере указано, что требуется сопряжение:

```bash
clawdock-devices
clawdock-approve <request-id>
```

## Конфигурация и секреты

ClawDock работает с тем же разделением конфигурации Docker, которое описано в [Docker](/install/docker):

- `<project>/.env` — для значений, специфичных для Docker (название образа, порты и токен шлюза);
- `~/.openclaw/.env` — для ключей провайдеров и токенов ботов, поддерживаемых окружением;
- `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` — для сохранённых данных аутентификации OAuth/API-ключей провайдеров;
- `~/.openclaw/openclaw.json` — для конфигурации поведения.

Используйте `clawdock-show-config`, если хотите быстро просмотреть файлы `.env` и `openclaw.json`. В выводимых данных значения из `.env` будут замаскированы.

## Связанные страницы

- [Docker](/install/docker)
- [Docker VM Runtime](/install/docker-vm-runtime)
- [Updating](/install/updating)