---
summary: "Разверните OpenClaw на Raspberry Pi для постоянного самохостинга"
read_when:
  - Настройка OpenClaw на Raspberry Pi
  - Запуск OpenClaw на устройствах с архитектурой ARM
  - Создание недорогого персонального ИИ с постоянным доступом
title: "Raspberry Pi"
---

# Raspberry Pi

Запустите постоянно работающий шлюз OpenClaw Gateway на Raspberry Pi. Поскольку Pi выполняет роль только шлюза (модели работают в облаке через API), даже устройство с невысокой производительностью хорошо справляется с нагрузкой.

## Предварительные требования

- Raspberry Pi 4 или 5 с объёмом ОЗУ 2 ГБ и более (рекомендуется 4 ГБ)
- Карта MicroSD (от 16 ГБ) или USB SSD (обеспечивает лучшую производительность)
- Официальный блок питания для Pi
- Подключение к сети (Ethernet или Wi-Fi)
- 64-битная ОС Raspberry Pi OS (обязательно — 32-битная версия не подходит)
- Около 30 минут времени

## Настройка

<Steps>
  <Step title="Запись ОС на носитель">
    Используйте **Raspberry Pi OS Lite (64-битная версия)** — для бессерверного режима рабочий стол не нужен.

    1. Загрузите [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
    2. Выберите ОС: **Raspberry Pi OS Lite (64-битная версия)**.
    3. В диалоговом окне настроек предварительно сконфигурируйте:
       - Имя хоста: `gateway-host`
       - Включите SSH
       - Задайте имя пользователя и пароль
       - Настройте Wi-Fi (если не используете Ethernet)
    4. Запишите образ на карту SD или USB-накопитель, вставьте его и загрузите Pi.

  </Step>

  <Step title="Подключение через SSH">
    ```bash
    ssh user@gateway-host
    ```
  </Step>

  <Step title="Обновление системы">
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y git curl build-essential

    # Установите часовой пояс (важно для cron и напоминаний)
    sudo timedatectl set-timezone America/Chicago
    ```

  </Step>

  <Step title="Установка Node.js 24">
    ```bash
    curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
    sudo apt install -y nodejs
    node --version
    ```
  </Step>

  <Step title="Добавление swap (важно для устройств с 2 ГБ ОЗУ или меньше)">
    ```bash
    sudo fallocate -l 2G /swapfile
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

    # Уменьшите значение swappiness для устройств с малым объёмом ОЗУ
    echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
    ```

  </Step>

  <Step title="Установка OpenClaw">
    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    ```
  </Step>

  <Step title="Запуск процесса настройки">
    ```bash
    openclaw onboard --install-daemon
    ```

    Следуйте инструкциям мастера. Для бессерверных устройств рекомендуется использовать API-ключи вместо OAuth. Проще всего начать с Telegram.

  </Step>

  <Step title="Проверка">
    ```bash
    openclaw status
    systemctl --user status openclaw-gateway.service
    journalctl --user -u openclaw-gateway.service -f
    ```
  </Step>

  <Step title="Доступ к интерфейсу управления">
    На своём компьютере получите URL панели управления с Pi:

    ```bash
    ssh user@gateway-host 'openclaw dashboard --no-open'
    ```

    Затем создайте SSH-туннель в другом терминале:

    ```bash
    ssh -N -L 18789:127.0.0.1:18789 user@gateway-host
    ```

    Откройте выведенный URL в локальном браузере. Для постоянного удалённого доступа см. [интеграцию с Tailscale](/gateway/tailscale).

  </Step>
</Steps>

## Советы по повышению производительности

**Используйте USB SSD** — карты SD работают медленно и изнашиваются. USB SSD значительно повышает производительность. См. [руководство по загрузке с USB для Pi](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-mass-storage-boot).

**Включите кэш компиляции модулей** — ускоряет повторные вызовы CLI на Pi с низкой производительностью:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF' # pragma: allowlist secret
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

**Снизите использование памяти** — для бессерверных конфигураций освободите память GPU и отключите неиспользуемые службы:

```bash
echo 'gpu_mem=16' | sudo tee -a /boot/config.txt
sudo systemctl disable bluetooth
```

## Устранение неполадок

**Нехватка памяти** — проверьте активность swap с помощью `free -h`. Отключите неиспользуемые службы (`sudo systemctl disable cups bluetooth avahi-daemon`). Используйте только модели на основе API.

**Низкая производительность** — используйте USB SSD вместо карты SD. Проверьте наличие дросселирования CPU с помощью `vcgencmd get_throttled` (должно возвращаться `0x0`).

**Служба не запускается** — проверьте журналы с помощью `journalctl --user -u openclaw-gateway.service --no-pager -n 100` и выполните `openclaw doctor --non-interactive`. Если это бессерверный Pi, также проверьте, включена ли функция lingering: `sudo loginctl enable-linger "$(whoami)"`.

**Проблемы с бинарными файлами ARM** — если навык завершается с ошибкой "exec format error", проверьте, есть ли сборка бинарного файла для ARM64. Проверьте архитектуру с помощью `uname -m` (должно отображаться `aarch64`).

**Обрывы соединения Wi-Fi** — отключите управление питанием Wi-Fi: `sudo iwconfig wlan0 power off`.

## Следующие шаги

- [Каналы](/channels) — подключите Telegram, WhatsApp, Discord и другие
- [Настройка шлюза](/gateway/configuration) — все параметры конфигурации
- [Обновление](/install/updating) — поддерживайте OpenClaw в актуальном состоянии