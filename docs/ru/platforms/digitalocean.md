---
summary: "OpenClaw на DigitalOcean (простой платный вариант VPS)"
read_when:
  - Настройка OpenClaw на DigitalOcean
  - Поиск дешёвого хостинга VPS для OpenClaw
title: "DigitalOcean (платформа)"
---

# OpenClaw на DigitalOcean

## Цель

Запустить постоянный OpenClaw Gateway на DigitalOcean за **6 долларов в месяц** (или за 4 доллара в месяц при резервировании тарифа).

Если вам нужен вариант за 0 долларов в месяц и вы не против использования ARM и специфичной для провайдера настройки, см. [руководство по Oracle Cloud](/platforms/oracle).

## Сравнение стоимости (2026)

| Провайдер | План | Характеристики | Цена в месяц | Примечания |
| ------------ | --------------- | ---------------------- | ----------- | ------------------------------------- |
| Oracle Cloud | Always Free ARM | до 4 OCPU, 24 ГБ ОЗУ | 0 долларов | ARM, ограниченная ёмкость / особенности регистрации |
| Hetzner | CX22 | 2 vCPU, 4 ГБ ОЗУ | 3,79 евро (~4 доллара) | Самый дешёвый платный вариант |
| DigitalOcean | Basic | 1 vCPU, 1 ГБ ОЗУ | 6 долларов | Простой интерфейс, хорошая документация |
| Vultr | Cloud Compute | 1 vCPU, 1 ГБ ОЗУ | 6 долларов | Много локаций |
| Linode | Nanode | 1 vCPU, 1 ГБ ОЗУ | 5 долларов | Теперь часть Akamai |

**Выбор провайдера:**

- DigitalOcean: самый простой UX и предсказуемая настройка (это руководство);
- Hetzner: хорошее соотношение цены и производительности (см. [руководство по Hetzner](/install/hetzner));
- Oracle Cloud: может быть за 0 долларов в месяц, но более капризный и только ARM (см. [руководство по Oracle](/platforms/oracle)).

---

## Предварительные требования

- Аккаунт DigitalOcean ([регистрация с бесплатным кредитом в 200 долларов](https://m.do.co/c/signup));
- Пара SSH-ключей (или готовность использовать аутентификацию по паролю);
- Около 20 минут.

## 1) Создание дроплета

<Warning>
Используйте чистый базовый образ (Ubuntu 24.04 LTS). Избегайте сторонних образов из Marketplace с установкой в один клик, если вы не проверили их скрипты запуска и настройки брандмауэра.
</Warning>

1. Войдите в [DigitalOcean](https://cloud.digitalocean.com/).
2. Нажмите **Create → Droplets**.
3. Выберите:
   - **Регион:** ближайший к вам (или к вашим пользователям);
   - **Образ:** Ubuntu 24.04 LTS;
   - **Размер:** Basic → Regular → **6 долларов в месяц** (1 vCPU, 1 ГБ ОЗУ, 25 ГБ SSD);
   - **Аутентификация:** SSH-ключ (рекомендуется) или пароль.
4. Нажмите **Create Droplet**.
5. Запишите IP-адрес.

## 2) Подключение через SSH

```bash
ssh root@ВАШ_IP_ДРОПЛЕТА
```

## 3) Установка OpenClaw

```bash
# Обновление системы
apt update && apt upgrade -y

# Установка Node.js 24
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# Установка OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Проверка
openclaw --version
```

## 4) Запуск онбординга

```bash
openclaw onboard --install-daemon
```

Мастер проведёт вас через следующие шаги:

- Аутентификация модели (API-ключи или OAuth);
- Настройка каналов (Telegram, WhatsApp, Discord и т. д.);
- Токен шлюза (генерируется автоматически);
- Установка демона (systemd).

## 5) Проверка шлюза

```bash
# Проверка статуса
openclaw status

# Проверка службы
systemctl --user status openclaw-gateway.service

# Просмотр журналов
journalctl --user -u openclaw-gateway.service -f
```

## 6) Доступ к панели управления

По умолчанию шлюз привязывается к loopback. Чтобы получить доступ к интерфейсу управления:

**Вариант А: SSH-туннель (рекомендуется)**

```bash
# С вашего локального компьютера
ssh -L 18789:localhost:18789 root@ВАШ_IP_ДРОПЛЕТА

# Затем откройте: http://localhost:18789
```

**Вариант Б: Tailscale Serve (HTTPS, только loopback)**

```bash
# На дроплете
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# Настройка шлюза для использования Tailscale Serve
openclaw config set gateway.tailscale.mode serve
openclaw gateway restart
```

Откройте: `https://<magicdns>/`

Примечания:

- Serve сохраняет шлюз только для loopback и аутентифицирует трафик интерфейса управления / WebSocket через заголовки идентификации Tailscale (аутентификация без токенов предполагает доверенный хост шлюза; HTTP-API не используют эти заголовки Tailscale и вместо этого следуют обычному режиму HTTP-аутентификации шлюза).
- Чтобы требовать явные учётные данные с общим секретом, установите `gateway.auth.allowTailscale: false` и используйте `gateway.auth.mode: "token"` или `"password"`.

**Вариант В: Привязка к Tailnet (без Serve)**

```bash
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

Откройте: `http://<tailscale-ip>:18789` (требуется токен).

## 7) Подключение ваших каналов

### Telegram

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <КОД>
```

### WhatsApp

```bash
openclaw channels login whatsapp
# Отсканируйте QR-код
```

См. [Каналы](/channels) для других провайдеров.

---

## Оптимизация для 1 ГБ ОЗУ

Дроплет за 6 долларов имеет только 1 ГБ ОЗУ. Чтобы система работала стабильно:

### Добавление swap (рекомендуется)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Использование более лёгкой модели

Если вы сталкиваетесь с ошибками OOM, рассмотрите следующие варианты:

- использование моделей на основе API (Claude, GPT) вместо локальных моделей;
- установка `agents.defaults.model.primary` на более лёгкую модель.

### Мониторинг памяти

```bash
free -h
htop
```

---

## Сохранение состояния

Всё состояние хранится в:

- `~/.openclaw/` — `openclaw.json`, профили аутентификации для каждого агента `auth-profiles.json`, состояние каналов/провайдеров и данные сессии;
- `~/.openclaw/workspace/` — рабочее пространство (SOUL.md, память и т. д.).

Эти данные сохраняются после перезагрузки. Периодически создавайте их резервные копии:

```bash
openclaw backup create
```

---

## Бесплатная альтернатива Oracle Cloud

Oracle Cloud предлагает **Always Free** ARM-инстансы, которые значительно мощнее любых платных вариантов, представленных здесь, — за 0 долларов в месяц.

| Что вы получаете | Характеристики |
| ----------------- | ---------------------- |
| **4 OCPU** | ARM Ampere A1 |
| **24 ГБ ОЗУ** | Более чем достаточно |
| **200 ГБ хранилища** | Блочное хранилище |
| **Навсегда бесплатно** | Без списания средств с кредитной карты |

**Ограничения:**

- Регистрация может быть проблематичной (попробуйте ещё раз, если не получится);
- Архитектура ARM — большинство вещей работает, но для некоторых бинарных файлов требуются сборки для ARM.

Полное руководство по настройке см. в [Oracle Cloud](/platforms/oracle). Советы по регистрации и устранению неполадок в процессе регистрации см. в этом [руководстве сообщества](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd).

---

## Устранение неполадок

### Шлюз не запускается

```bash
openclaw gateway status
openclaw doctor --non-interactive
journalctl --user -u openclaw-gateway.service --no-pager -n 50
```

### Порт уже используется

```bash
lsof