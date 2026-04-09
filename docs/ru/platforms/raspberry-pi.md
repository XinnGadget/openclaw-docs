---
summary: "OpenClaw на Raspberry Pi (бюджетная локальная установка)"
read_when:
  - Настройка OpenClaw на Raspberry Pi
  - Запуск OpenClaw на устройствах с архитектурой ARM
  - Создание недорогого постоянно работающего персонального ИИ
title: "Raspberry Pi (платформа)"
---

# OpenClaw на Raspberry Pi

## Цель

Запустить постоянно работающий шлюз OpenClaw Gateway на Raspberry Pi с единовременными затратами **~35–80 долларов** (без ежемесячных платежей).

Идеально подходит для:

- персонального ИИ-ассистента, работающего 24/7;
- центра автоматизации умного дома;
- энергоэффективного, всегда доступного бота для Telegram/WhatsApp.

## Требования к оборудованию

| Модель Pi | ОЗУ | Работает? | Примечания |
| --------------- | ------- | -------- | ---------------------------------- |
| **Pi 5** | 4 ГБ/8 ГБ | ✅ Лучше всего | Самая высокая производительность, рекомендуется |
| **Pi 4** | 4 ГБ | ✅ Хорошо | Оптимальный вариант для большинства пользователей |
| **Pi 4** | 2 ГБ | ✅ Нормально | Работает, требуется добавление swap |
| **Pi 4** | 1 ГБ | ⚠️ С трудом | Возможно с swap, минимальная конфигурация |
| **Pi 3B+** | 1 ГБ | ⚠️ Медленно | Работает, но медленно |
| **Pi Zero 2 W** | 512 МБ | ❌ | Не рекомендуется |

**Минимальные требования:** 1 ГБ ОЗУ, 1 ядро, 500 МБ дискового пространства  
**Рекомендуемые требования:** 2 ГБ+ ОЗУ, 64-битная ОС, SD-карта на 16 ГБ+ (или USB SSD)

## Что вам понадобится

- Raspberry Pi 4 или 5 (рекомендуется 2 ГБ+ ОЗУ);
- microSD-карта (16 ГБ+) или USB SSD (обеспечивает лучшую производительность);
- блок питания (рекомендуется официальный блок питания для Pi);
- подключение к сети (Ethernet или Wi-Fi);
- около 30 минут времени.

## 1) Запись ОС на носитель

Используйте **Raspberry Pi OS Lite (64-битная версия)** — графический интерфейс не нужен для бессерверного режима.

1. Скачайте [Raspberry Pi Imager](https://www.raspberrypi.com/software/).
2. Выберите ОС: **Raspberry Pi OS Lite (64-битная версия)**.
3. Нажмите на значок шестерёнки (⚙️), чтобы предварительно настроить:
   - задайте имя хоста: `gateway-host`;
   - включите SSH;
   - задайте имя пользователя и пароль;
   - настройте Wi-Fi (если не используете Ethernet).
4. Запишите ОС на SD-карту или USB-накопитель.
5. Вставьте носитель и запустите Pi.

## 2) Подключение по SSH

```bash
ssh user@gateway-host
# или используйте IP-адрес
ssh user@192.168.x.x
```

## 3) Настройка системы

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y git curl build-essential

# Установка часового пояса (важно для cron/напоминаний)
sudo timedatectl set-timezone America/Chicago  # Замените на свой часовой пояс
```

## 4) Установка Node.js 24 (ARM64)

```bash
# Установка Node.js через NodeSource
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Проверка
node --version  # Должна отобразиться версия v24.x.x
npm --version
```

## 5) Добавление swap (важно для устройств с 2 ГБ ОЗУ и меньше)

Swap предотвращает сбои из-за нехватки памяти:

```bash
# Создание файла swap размером 2 ГБ
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Сделать swap постоянным
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Оптимизация для малого объёма ОЗУ (снижение активности swap)
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 6) Установка OpenClaw

### Вариант А: стандартная установка (рекомендуется)

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

### Вариант Б: установка с возможностью внесения изменений (для экспериментов)

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
npm install
npm run build
npm link
```

Установка с возможностью внесения изменений даёт прямой доступ к журналам и коду — это полезно для отладки проблем, специфичных для ARM.

## 7) Запуск процесса настройки

```bash
openclaw onboard --install-daemon
```

Следуйте инструкциям мастера:

1. **Режим шлюза:** локальный.
2. **Аутентификация:** рекомендуется использовать API-ключи (OAuth может работать нестабильно на бессерверном Pi).
3. **Каналы:** проще всего начать с Telegram.
4. **Демон:** да (systemd).

## 8) Проверка установки

```bash
# Проверка статуса
openclaw status

# Проверка службы (стандартная установка = юнит systemd для пользователя)
systemctl --user status openclaw-gateway.service

# Просмотр журналов
journalctl --user -u openclaw-gateway.service -f
```

## 9) Доступ к панели управления OpenClaw

Замените `user@gateway-host` на имя пользователя и имя хоста или IP-адрес вашего Pi.

На своём компьютере попросите Pi вывести свежий URL панели управления:

```bash
ssh user@gateway-host 'openclaw dashboard --no-open'
```

Команда выведет `Dashboard URL:`. В зависимости от настройки `gateway.auth.token` URL может быть простой ссылкой `http://127.0.0.1:18789/` или содержать `#token=...`.

В другом терминале на своём компьютере создайте SSH-туннель:

```bash
ssh -N -L 18789:127.0.0.1:18789 user@gateway-host
```

Затем откройте выведенный URL панели управления в локальном браузере.

Если интерфейс запрашивает аутентификацию с общим секретом, вставьте настроенное значение токена или пароля в настройки Control UI. Для аутентификации по токену используйте `gateway.auth.token` (или `OPENCLAW_GATEWAY_TOKEN`).

Для постоянного удалённого доступа см. [Tailscale](/gateway/tailscale).

---

## Оптимизация производительности

### Использование USB SSD (значительное улучшение)

SD-карты работают медленно и изнашиваются. USB SSD значительно повышает производительность:

```bash
# Проверка загрузки с USB
lsblk
```

См. [руководство по загрузке с USB для Pi](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#usb-mass-storage-boot) для настройки.

### Ускорение запуска CLI (кэш компиляции модулей)

На Pi с низкой производительностью включите кэш компиляции модулей Node, чтобы ускорить повторные запуски CLI:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF' # pragma: allowlist secret
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

Примечания:

- `NODE_COMPILE_CACHE` ускоряет последующие запуски (`status`, `health`, `--help`).
- `/var/tmp` лучше сохраняет данные после перезагрузки, чем `/tmp`.
- `OPENCLAW_NO_RESPAWN=1` позволяет избежать дополнительных затрат на запуск из-за самоперезапуска CLI.
- Первый запуск заполняет кэш, последующие запуски получают наибольшую выгоду.

### Настройка запуска через systemd (необязательно)

Если Pi в основном используется для запуска OpenClaw, добавьте настройку сервиса, чтобы уменьшить колебания при перезапуске и сохранить стабильность среды запуска:

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

Затем примените изменения:

```bash
systemctl --user daemon-reload
systemctl --user