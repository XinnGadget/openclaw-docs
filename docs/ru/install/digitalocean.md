---
summary: "Развёртывание OpenClaw на сервере DigitalOcean Droplet"
read_when:
  - Настройка OpenClaw на DigitalOcean
  - Поиск простого платного VPS для OpenClaw
title: "DigitalOcean"
---

# DigitalOcean

Запустите постоянный шлюз OpenClaw на сервере DigitalOcean Droplet.

## Предварительные требования

- Аккаунт DigitalOcean ([регистрация](https://cloud.digitalocean.com/registrations/new))
- Пара SSH-ключей (или готовность использовать аутентификацию по паролю)
- Около 20 минут

## Настройка

<Steps>
  <Step title="Создание Droplet">
    <Warning>
    Используйте чистый базовый образ (Ubuntu 24.04 LTS). Избегайте сторонних образов из Marketplace с установкой в один клик, если вы не проверили их скрипты запуска и настройки брандмауэра.
    </Warning>

    1. Войдите в [DigitalOcean](https://cloud.digitalocean.com/).
    2. Нажмите **Create > Droplets**.
    3. Выберите:
       - **Регион:** ближайший к вам
       - **Образ:** Ubuntu 24.04 LTS
       - **Размер:** Basic, Regular, 1 vCPU / 1 ГБ ОЗУ / 25 ГБ SSD
       - **Аутентификация:** SSH-ключ (рекомендуется) или пароль
    4. Нажмите **Create Droplet** и запишите IP-адрес.

  </Step>

  <Step title="Подключение и установка">
    ```bash
    ssh root@YOUR_DROPLET_IP

    apt update && apt upgrade -y

    # Установка Node.js 24
    curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
    apt install -y nodejs

    # Установка OpenClaw
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw --version
    ```

  </Step>

  <Step title="Запуск процесса настройки">
    ```bash
    openclaw onboard --install-daemon
    ```

    Мастер проведёт вас через этапы аутентификации модели, настройки каналов, генерации токена шлюза и установки демона (systemd).

  </Step>

  <Step title="Добавление swap (рекомендуется для Droplet с 1 ГБ ОЗУ)">
    ```bash
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    ```
  </Step>

  <Step title="Проверка шлюза">
    ```bash
    openclaw status
    systemctl --user status openclaw-gateway.service
    journalctl --user -u openclaw-gateway.service -f
    ```
  </Step>

  <Step title="Доступ к интерфейсу управления">
    По умолчанию шлюз привязан к loopback. Выберите один из следующих вариантов.

    **Вариант A: SSH-туннель (самый простой)**

    ```bash
    # С вашего локального компьютера
    ssh -L 18789:localhost:18789 root@YOUR_DROPLET_IP
    ```

    Затем откройте `http://localhost:18789`.

    **Вариант B: Tailscale Serve**

    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    tailscale up
    openclaw config set gateway.tailscale.mode serve
    openclaw gateway restart
    ```

    Затем откройте `https://<magicdns>/` с любого устройства в вашем tailnet.

    **Вариант C: Привязка к tailnet (без Serve)**

    ```bash
    openclaw config set gateway.bind tailnet
    openclaw gateway restart
    ```

    Затем откройте `http://<tailscale-ip>:18789` (требуется токен).

  </Step>
</Steps>

## Устранение неполадок

**Шлюз не запускается** — выполните `openclaw doctor --non-interactive` и проверьте журналы с помощью `journalctl --user -u openclaw-gateway.service -n 50`.

**Порт уже используется** — выполните `lsof -i :18789`, чтобы найти процесс, затем остановите его.

**Недостаточно памяти** — проверьте, активен ли swap, с помощью `free -h`. Если проблема с нехваткой памяти сохраняется, используйте модели на основе API (Claude, GPT) вместо локальных моделей или перейдите на Droplet с 2 ГБ ОЗУ.

## Следующие шаги

- [Каналы](/channels) — подключение Telegram, WhatsApp, Discord и других
- [Настройка шлюза](/gateway/configuration) — все параметры конфигурации
- [Обновление](/install/updating) — поддержание OpenClaw в актуальном состоянии