---
summary: "Запустить OpenClaw Gateway на exe.dev (виртуальная машина + HTTPS-прокси) для удалённого доступа"
read_when:
  - Вам нужен недорогой постоянно работающий хост на Linux для Gateway
  - Вам нужен удалённый доступ к интерфейсу управления (Control UI) без развёртывания собственного VPS
title: "exe.dev"
---

# exe.dev

Цель: запустить OpenClaw Gateway на виртуальной машине exe.dev, чтобы получить к нему доступ с ноутбука по адресу: `https://<vm-name>.exe.xyz`

В этом руководстве предполагается использование образа **exeuntu** по умолчанию от exe.dev. Если вы выбрали другой дистрибутив, адаптируйте установку пакетов соответствующим образом.

## Быстрый старт для начинающих

1. [https://exe.new/openclaw](https://exe.new/openclaw)
2. Введите ключ аутентификации/токен, если это необходимо
3. Нажмите "Agent" рядом с вашей виртуальной машиной и дождитесь, пока Shelley завершит подготовку
4. Откройте `https://<vm-name>.exe.xyz/` и пройдите аутентификацию с использованием настроенного общего секрета (в этом руководстве по умолчанию используется аутентификация по токену, но также возможна аутентификация по паролю — для этого измените параметр `gateway.auth.mode`)
5. Подтвердите все ожидающие запросы на сопряжение устройств с помощью команды `openclaw devices approve <requestId>`

## Что вам понадобится

- учётная запись exe.dev;
- доступ по `ssh exe.dev` к виртуальным машинам [exe.dev](https://exe.dev) (необязательно).

## Автоматическая установка с помощью Shelley

Shelley — агент [exe.dev](https://exe.dev) — может мгновенно установить OpenClaw с помощью следующего промпта:

```
Установите OpenClaw (https://docs.openclaw.ai/install) на эту виртуальную машину. Используйте флаги non-interactive и accept-risk для подключения к OpenClaw. Добавьте предоставленный ключ аутентификации или токен, если это необходимо. Настройте nginx для перенаправления с порта по умолчанию 18789 на корневую директорию в конфигурации сайта по умолчанию, убедившись, что поддержка WebSocket включена. Сопряжение выполняется с помощью команд "openclaw devices list" и "openclaw devices approve <request id>". Убедитесь, что на панели управления отображается статус работоспособности OpenClaw как "OK". exe.dev выполняет перенаправление с порта 8000 на порты 80/443 и обеспечивает HTTPS, поэтому конечный "доступный" адрес должен быть <vm-name>.exe.xyz без указания порта.
```

## Ручная установка

## 1) Создание виртуальной машины

С вашего устройства выполните:

```bash
ssh exe.dev new
```

Затем подключитесь:

```bash
ssh <vm-name>.exe.xyz
```

Совет: сохраняйте эту виртуальную машину **stateful**. OpenClaw хранит файлы `openclaw.json`, `auth-profiles.json` (для каждого агента), сессии, а также состояние каналов и провайдеров в каталоге `~/.openclaw/`, а рабочее пространство — в `~/.openclaw/workspace/`.

## 2) Установка предварительных требований (на виртуальной машине)

```bash
sudo apt-get update
sudo apt-get install -y git curl jq ca-certificates openssl
```

## 3) Установка OpenClaw

Запустите скрипт установки OpenClaw:

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

## 4) Настройка nginx для проксирования OpenClaw на порт 8000

Отредактируйте файл `/etc/nginx/sites-enabled/default`, добавив следующее:

```
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    listen 8000;
    listen [::]:8000;

    server_name _;

    location / {
        proxy_pass http://127.0.0.1:18789;
        proxy_http_version 1.1;

        # Поддержка WebSocket
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Стандартные заголовки прокси
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Настройки тайм-аута для долгоживущих соединений
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

Перезапишите заголовки перенаправления вместо сохранения цепочек, предоставленных клиентом. OpenClaw доверяет метаданным IP-адреса, переданным только от явно настроенных прокси-серверов, а цепочки `X-Forwarded-For` в стиле добавления рассматриваются как угроза безопасности.

## 5) Доступ к OpenClaw и предоставление привилегий

Перейдите по адресу `https://<vm-name>.exe.xyz/` (см. вывод интерфейса управления (Control UI) при подключении). Если появится запрос на аутентификацию, вставьте настроенные общий секрет из виртуальной машины. В этом руководстве используется аутентификация по токену, поэтому получите `gateway.auth.token` с помощью команды `openclaw config get gateway.auth.token` (или сгенерируйте его с помощью `openclaw doctor --generate-gateway-token`). Если вы переключили шлюз на аутентификацию по паролю, используйте `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`.

Подтвердите устройства с помощью команд `openclaw devices list` и `openclaw devices approve <requestId>`. Если вы не уверены в чём-то, воспользуйтесь Shelley в браузере!

## Удалённый доступ

Удалённый доступ обеспечивается аутентификацией [exe.dev](https://exe.dev). По умолчанию HTTP-трафик с порта 8000 перенаправляется на `https://<vm-name>.exe.xyz` с аутентификацией по электронной почте.

## Обновление

```bash
npm i -g openclaw@latest
openclaw doctor
openclaw gateway restart
openclaw health
```

Руководство: [Обновление](/install/updating)