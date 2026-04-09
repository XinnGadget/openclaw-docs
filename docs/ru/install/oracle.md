---
summary: "Разместить OpenClaw на тарифе Always Free ARM в Oracle Cloud"
read_when:
  - Настройка OpenClaw в Oracle Cloud
  - Поиск бесплатного хостинга VPS для OpenClaw
  - Желание запустить OpenClaw круглосуточно на небольшом сервере
title: "Oracle Cloud"
---

# Oracle Cloud

Запустите постоянный шлюз OpenClaw в тарифе **Always Free** ARM в Oracle Cloud (до 4 OCPU, 24 ГБ ОЗУ, 200 ГБ хранилища) бесплатно.

## Предварительные требования

- Аккаунт Oracle Cloud ([регистрация](https://www.oracle.com/cloud/free/)) — если возникнут проблемы, ознакомьтесь с [руководством по регистрации в сообществе](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd)
- Аккаунт Tailscale (бесплатно на [tailscale.com](https://tailscale.com))
- Пара ключей SSH
- Около 30 минут времени

## Настройка

<Steps>
  <Step title="Создать инстанс OCI">
    1. Войдите в [консоль Oracle Cloud](https://cloud.oracle.com/).
    2. Перейдите в **Compute > Instances > Create Instance**.
    3. Настройте:
       - **Name:** `openclaw`
       - **Image:** Ubuntu 24.04 (aarch64)
       - **Shape:** `VM.Standard.A1.Flex` (Ampere ARM)
       - **OCPUs:** 2 (или до 4)
       - **Memory:** 12 ГБ (или до 24 ГБ)
       - **Boot volume:** 50 ГБ (до 200 ГБ бесплатно)
       - **SSH key:** добавьте свой публичный ключ
    4. Нажмите **Create** и запишите публичный IP-адрес.

    <Tip>
    Если создание инстанса завершается ошибкой "Out of capacity", попробуйте другой домен доступности или повторите попытку позже. Ресурсы бесплатного тарифа ограничены.
    </Tip>

  </Step>

  <Step title="Подключиться и обновить систему">
    ```bash
    ssh ubuntu@YOUR_PUBLIC_IP

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y build-essential
    ```

    Пакет `build-essential` необходим для компиляции некоторых зависимостей на ARM.

  </Step>

  <Step title="Настроить пользователя и имя хоста">
    ```bash
    sudo hostnamectl set-hostname openclaw
    sudo passwd ubuntu
    sudo loginctl enable-linger ubuntu
    ```

    Включение linger позволяет сервисам пользователя работать после выхода из системы.

  </Step>

  <Step title="Установить Tailscale">
    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --ssh --hostname=openclaw
    ```

    С этого момента подключайтесь через Tailscale: `ssh ubuntu@openclaw`.

  </Step>

  <Step title="Установить OpenClaw">
    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    source ~/.bashrc
    ```

    Когда появится запрос "How do you want to hatch your bot?", выберите **Do this later**.

  </Step>

  <Step title="Настроить шлюз">
    Используйте аутентификацию по токену с Tailscale Serve для безопасного удалённого доступа.

    ```bash
    openclaw config set gateway.bind loopback
    openclaw config set gateway.auth.mode token
    openclaw doctor --generate-gateway-token
    openclaw config set gateway.tailscale.mode serve
    openclaw config set gateway.trustedProxies '["127.0.0.1"]'

    systemctl --user restart openclaw-gateway.service
    ```

    Параметр `gateway.trustedProxies=["127.0.0.1"]` здесь предназначен только для обработки переадресованных IP-адресов/локальных клиентов прокси-сервера Tailscale Serve. Это **не** `gateway.auth.mode: "trusted-proxy"`. В данной настройке маршруты просмотра Diff сохраняют поведение "fail-closed": необработанные запросы просмотра `127.0.0.1` без заголовков переадресованного прокси могут возвращать `Diff not found`. Используйте `mode=file` / `mode=both` для вложений или намеренно включите удалённых просмотрщиков и задайте `plugins.entries.diffs.config.viewerBaseUrl` (или передайте прокси `baseUrl`), если вам нужны общие ссылки на просмотр.

  </Step>

  <Step title="Ограничить безопасность VCN">
    Заблокируйте весь трафик, кроме Tailscale, на сетевом периметре:

    1. Перейдите в **Networking > Virtual Cloud Networks** в консоли OCI.
    2. Выберите свой VCN, затем **Security Lists > Default Security List**.
    3. **Удалите** все правила входящего трафика, кроме `0.0.0.0/0 UDP 41641` (Tailscale).
    4. Оставьте правила исходящего трафика по умолчанию (разрешить весь исходящий трафик).

    Это заблокирует SSH на порту 22, HTTP, HTTPS и всё остальное на сетевом периметре. С этого момента вы сможете подключаться только через Tailscale.

  </Step>

  <Step title="Проверить">
    ```bash
    openclaw --version
    systemctl --user status openclaw-gateway.service
    tailscale serve status
    curl http://localhost:18789
    ```

    Получите доступ к интерфейсу управления с любого устройства в вашей tailnet:

    ```
    https://openclaw.<tailnet-name>.ts.net/
    ```

    Замените `<tailnet-name>` на имя вашей tailnet (отображается в `tailscale status`).

  </Step>
</Steps>

## Резервный вариант: SSH-туннель

Если Tailscale Serve не работает, используйте SSH-туннель с вашего локального компьютера:

```bash
ssh -L 18789:127.0.0.1:18789 ubuntu@openclaw
```

Затем откройте `http://localhost:18789`.

## Устранение неполадок

**Ошибка создания инстанса ("Out of capacity")** — инстансы ARM бесплатного тарифа популярны. Попробуйте другой домен доступности или повторите попытку в непиковые часы.

**Tailscale не подключается** — выполните `sudo tailscale up --ssh --hostname=openclaw --reset` для повторной аутентификации.

**Шлюз не запускается** — выполните `openclaw doctor --non-interactive` и проверьте журналы с помощью `journalctl --user -u openclaw-gateway.service -n 50`.

**Проблемы с бинарными файлами ARM** — большинство пакетов npm работают на ARM64. Для нативных бинарных файлов ищите выпуски `linux-arm64` или `aarch64`. Проверьте архитектуру с помощью `uname -m`.

## Следующие шаги

- [Каналы](/channels) — подключите Telegram, WhatsApp, Discord и другие
- [Настройка шлюза](/gateway/configuration) — все параметры конфигурации
- [Обновление](/install/updating) — поддерживайте OpenClaw в актуальном состоянии