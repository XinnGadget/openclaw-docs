---
summary: "Поддержка Linux + статус сопутствующего приложения"
read_when:
  - Ищете информацию о статусе сопутствующего приложения для Linux
  - Планируете охват платформ или вклад в разработку
title: "Приложение для Linux"
---

# Приложение для Linux

Gateway полностью поддерживается в Linux. **В качестве среды выполнения рекомендуется использовать Node.**
Использование Bun для Gateway не рекомендуется (ошибки в WhatsApp/Telegram).

Планируется разработка нативных сопутствующих приложений для Linux. Если вы хотите помочь в их создании — ваш вклад приветствуется.

## Быстрый старт для начинающих (VPS)

1. Установите Node 24 (рекомендуется; для совместимости по-прежнему подходит Node 22 LTS, текущая версия — `22.14+`).
2. Выполните команду: `npm i -g openclaw@latest`.
3. Выполните команду: `openclaw onboard --install-daemon`.
4. С вашего ноутбука выполните: `ssh -N -L 18789:127.0.0.1:18789 <user>@<host>`.
5. Откройте `http://127.0.0.1:18789/` и пройдите аутентификацию с использованием настроенного общего секрета (по умолчанию — токен; пароль, если вы установили `gateway.auth.mode: "password"`).

Полное руководство по настройке Linux-сервера: [Linux Server](/vps). Пошаговый пример настройки VPS: [exe.dev](/install/exe-dev).

## Установка

- [Начало работы](/start/getting-started)
- [Установка и обновления](/install/updating)
- Дополнительные варианты: [Bun (экспериментальный)](/install/bun), [Nix](/install/nix), [Docker](/install/docker)

## Gateway

- [Руководство по работе с Gateway](/gateway)
- [Конфигурация](/gateway/configuration)

## Установка службы Gateway (CLI)

Используйте одну из следующих команд:

```
openclaw onboard --install-daemon
```

Или:

```
openclaw gateway install
```

Или:

```
openclaw configure
```

При запросе выберите **Gateway service**.

Восстановление/миграция:

```
openclaw doctor
```

## Управление системой (юнит systemd для пользователя)

По умолчанию OpenClaw устанавливает **пользовательскую** службу systemd. Для общих серверов или серверов, работающих постоянно, используйте **системную** службу. Команды `openclaw gateway install` и `openclaw onboard --install-daemon` уже формируют текущий канонический юнит; создавайте его вручную только в случае необходимости настройки пользовательского системного менеджера служб. Полное руководство по настройке службы содержится в [руководстве по работе с Gateway](/gateway).

Минимальная настройка:

Создайте файл `~/.config/systemd/user/openclaw-gateway[-<profile>].service`:

```
[Unit]
Description=OpenClaw Gateway (профиль: <profile>, v<version>)
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

Включите его:

```
systemctl --user enable --now openclaw-gateway[-<profile>].service
```