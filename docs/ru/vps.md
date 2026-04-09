---
summary: "Запустить OpenClaw на Linux-сервере или облачном VPS — выбор провайдера, архитектура и настройка"
read_when:
  - Вы хотите запустить Gateway на Linux-сервере или облачном VPS
  - Вам нужна краткая сводка руководств по хостингу
  - Вы хотите узнать об общей настройке Linux-сервера для OpenClaw
title: "Linux-сервер"
sidebarTitle: "Linux-сервер"
---

# Linux-сервер

Запустите OpenClaw Gateway на любом Linux-сервере или облачном VPS. На этой странице вы найдёте помощь в выборе провайдера, объяснение того, как работают облачные развёртывания, а также общие рекомендации по настройке Linux, применимые в любых условиях.

## Выбор провайдера

<CardGroup cols={2}>
  <Card title="Railway" href="/install/railway">Настройка в один клик через браузер</Card>
  <Card title="Northflank" href="/install/northflank">Настройка в один клик через браузер</Card>
  <Card title="DigitalOcean" href="/install/digitalocean">Простой платный VPS</Card>
  <Card title="Oracle Cloud" href="/install/oracle">Бесплатный уровень ARM (Always Free)</Card>
  <Card title="Fly.io" href="/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/install/hetzner">Docker на Hetzner VPS</Card>
  <Card title="GCP" href="/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/install/azure">Linux VM</Card>
  <Card title="exe.dev" href="/install/exe-dev">VM с HTTPS-прокси</Card>
  <Card title="Raspberry Pi" href="/install/raspberry-pi">ARM, самостоятельное размещение</Card>
</CardGroup>

**AWS (EC2 / Lightsail / бесплатный уровень)** также хорошо подходит.
Доступно видеоруководство от сообщества по ссылке:
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(ресурс сообщества — может стать недоступным).

## Как работают облачные настройки

- **Gateway запускается на VPS** и управляет состоянием и рабочим пространством.
- Вы подключаетесь с ноутбука или телефона через **Control UI** или **Tailscale/SSH**.
- Рассматривайте VPS как источник достоверных данных и **регулярно создавайте резервные копии** состояния и рабочего пространства.
- Стандартная безопасность: держите Gateway на loopback и подключайтесь к нему через SSH-туннель или Tailscale Serve.
  Если вы привязываетесь к `lan` или `tailnet`, используйте `gateway.auth.token` или `gateway.auth.password`.

Связанные страницы: [Удалённый доступ к Gateway](/gateway/remote), [Хаб платформ](/platforms).

## Общий агент компании на VPS

Запуск одного агента для команды допустим, если все пользователи находятся в одной зоне доверия и агент используется только в бизнес-целях.

- Держите его на выделенной среде выполнения (VPS/VM/контейнер + выделенный пользователь ОС/учётные записи).
- Не подключайте эту среду выполнения к личным учётным записям Apple/Google или личным профилям браузера/менеджера паролей.
- Если пользователи потенциально враждебны друг к другу, разделите их по gateway/хосту/пользователю ОС.

Подробности модели безопасности: [Безопасность](/gateway/security).

## Использование узлов с VPS

Вы можете оставить Gateway в облаке и подключить **узлы** на своих локальных устройствах (Mac/iOS/Android/безголовые системы). Узлы предоставляют локальные возможности работы с экраном/камерой/холстом и функции `system.run`, в то время как Gateway остаётся в облаке.

Документация: [Узлы](/nodes), [CLI для узлов](/cli/nodes).

## Настройка запуска для небольших ВМ и ARM-хостов

Если команды CLI выполняются медленно на маломощных ВМ (или ARM-хостах), включите кэш компиляции модулей Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` ускоряет запуск повторяющихся команд.
- `OPENCLAW_NO_RESPAWN=1` позволяет избежать дополнительных накладных расходов на запуск из-за пути самоперезапуска.
- При первом запуске команды кэш прогревается; последующие запуски выполняются быстрее.
- Для подробностей о Raspberry Pi см. [Raspberry Pi](/install/raspberry-pi).

### Чек-лист настройки systemd (необязательно)

Для хостов ВМ, использующих `systemd`, рассмотрите следующие шаги:

- Добавьте переменные окружения для стабильного пути запуска:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Чётко определите поведение перезапуска:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Предпочитайте диски на базе SSD для путей к состоянию/кэшу, чтобы уменьшить штрафы за случайный ввод-вывод при холодном старте.

Для стандартного пути `openclaw onboard --install-daemon` отредактируйте пользовательский юнит:

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

Если вы намеренно установили системный юнит, отредактируйте `openclaw-gateway.service` с помощью команды `sudo systemctl edit openclaw-gateway.service`.

Как политики `Restart=` помогают автоматизировать восстановление:
[systemd может автоматизировать восстановление служб](https://www.redhat.com/en/blog/systemd-automate-recovery).