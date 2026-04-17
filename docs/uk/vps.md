---
read_when:
    - Ви хочете запустити Gateway на сервері Linux або хмарному VPS
    - Вам потрібен короткий огляд посібників із розміщення
    - Вам потрібне загальне налаштування сервера Linux для OpenClaw
sidebarTitle: Linux Server
summary: Запустіть OpenClaw на сервері Linux або хмарному VPS — вибір провайдера, архітектура та налаштування продуктивності
title: Сервер Linux
x-i18n:
    generated_at: "2026-04-13T13:14:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Сервер Linux

Запустіть Gateway OpenClaw на будь-якому сервері Linux або хмарному VPS. Ця сторінка допоможе вам
вибрати провайдера, пояснює, як працюють хмарні розгортання, і охоплює загальні
налаштування Linux, які застосовуються всюди.

## Вибір провайдера

<CardGroup cols={2}>
  <Card title="Railway" href="/uk/install/railway">Налаштування в браузері в один клік</Card>
  <Card title="Northflank" href="/uk/install/northflank">Налаштування в браузері в один клік</Card>
  <Card title="DigitalOcean" href="/uk/install/digitalocean">Простий платний VPS</Card>
  <Card title="Oracle Cloud" href="/uk/install/oracle">Завжди безкоштовний ARM-рівень</Card>
  <Card title="Fly.io" href="/uk/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/uk/install/hetzner">Docker на VPS Hetzner</Card>
  <Card title="Hostinger" href="/uk/install/hostinger">VPS із налаштуванням в один клік</Card>
  <Card title="GCP" href="/uk/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/uk/install/azure">Віртуальна машина Linux</Card>
  <Card title="exe.dev" href="/uk/install/exe-dev">Віртуальна машина з HTTPS-проксі</Card>
  <Card title="Raspberry Pi" href="/uk/install/raspberry-pi">ARM на власному хостингу</Card>
</CardGroup>

**AWS (EC2 / Lightsail / безкоштовний рівень)** також добре працює.
Доступне відеооглядове керівництво від спільноти за адресою
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(ресурс спільноти — може стати недоступним).

## Як працюють хмарні налаштування

- **Gateway працює на VPS** і керує станом + робочим простором.
- Ви підключаєтеся з ноутбука або телефона через **Control UI** чи **Tailscale/SSH**.
- Сприймайте VPS як джерело істини та регулярно **створюйте резервні копії** стану + робочого простору.
- Безпечний варіант за замовчуванням: тримайте Gateway на loopback-інтерфейсі та отримуйте доступ через SSH-тунель або Tailscale Serve.
  Якщо ви прив’язуєтеся до `lan` або `tailnet`, обов’язково використовуйте `gateway.auth.token` або `gateway.auth.password`.

Пов’язані сторінки: [Віддалений доступ до Gateway](/uk/gateway/remote), [Центр платформ](/uk/platforms).

## Спільний агент компанії на VPS

Запуск одного агента для команди — це припустимий варіант, якщо всі користувачі перебувають у межах однакової моделі довіри, а агент використовується лише для бізнесу.

- Тримайте його в окремому середовищі виконання (VPS/VM/контейнер + окремий користувач ОС/облікові записи).
- Не входьте в цьому середовищі до особистих облікових записів Apple/Google або особистих профілів браузера/менеджера паролів.
- Якщо користувачі є взаємно недовіреними, розділяйте за gateway/хостом/користувачем ОС.

Деталі моделі безпеки: [Безпека](/uk/gateway/security).

## Використання Node із VPS

Ви можете тримати Gateway у хмарі та під’єднувати **Node** на своїх локальних пристроях
(Mac/iOS/Android/headless). Node надають локальні можливості екрана/камери/canvas і `system.run`,
тоді як Gateway залишається у хмарі.

Документація: [Node](/uk/nodes), [CLI Node](/cli/nodes).

## Налаштування запуску для малих VM і ARM-хостів

Якщо команди CLI здаються повільними на малопотужних VM (або ARM-хостах), увімкніть кеш компіляції модулів Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` пришвидшує повторний запуск команд.
- `OPENCLAW_NO_RESPAWN=1` усуває додаткові накладні витрати запуску через шлях самоперезапуску.
- Перший запуск команди прогріває кеш; наступні запуски швидші.
- Для особливостей Raspberry Pi дивіться [Raspberry Pi](/uk/install/raspberry-pi).

### Контрольний список налаштування systemd (необов’язково)

Для VM-хостів, що використовують `systemd`, варто розглянути таке:

- Додайте змінні середовища сервісу для стабільного шляху запуску:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Явно задайте поведінку перезапуску:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Віддавайте перевагу дискам на SSD для шляхів стану/кешу, щоб зменшити штрафи холодного запуску через випадковий I/O.

Для стандартного шляху `openclaw onboard --install-daemon` відредагуйте користувацький unit:

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

Якщо натомість ви навмисно встановили системний unit, відредагуйте
`openclaw-gateway.service` через `sudo systemctl edit openclaw-gateway.service`.

Як політики `Restart=` допомагають автоматизованому відновленню:
[systemd може автоматизувати відновлення сервісу](https://www.redhat.com/en/blog/systemd-automate-recovery).
