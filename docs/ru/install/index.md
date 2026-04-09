---
summary: "Установка OpenClaw — скрипт установки, npm/pnpm/bun, из исходного кода, Docker и др."
read_when:
  - Вам нужен способ установки, отличный от быстрого старта в разделе "Начало работы"
  - Вы хотите развернуть систему на облачной платформе
  - Вам нужно обновить, перенести или удалить программу
title: "Установка"
---

# Установка

## Рекомендованный способ: скрипт установки

Самый быстрый способ установки. Скрипт определяет вашу ОС, при необходимости устанавливает Node, устанавливает OpenClaw и запускает процесс ознакомления.

<Tabs>
  <Tab title="macOS / Linux / WSL2">
    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    ```
  </Tab>
  <Tab title="Windows (PowerShell)">
    ```powershell
    iwr -useb https://openclaw.ai/install.ps1 | iex
    ```
  </Tab>
</Tabs>

Чтобы установить без запуска процесса ознакомления:

<Tabs>
  <Tab title="macOS / Linux / WSL2">
    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard
    ```
  </Tab>
  <Tab title="Windows (PowerShell)">
    ```powershell
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    ```
  </Tab>
</Tabs>

О всех флагах и опциях для CI/автоматизации см. [Внутреннее устройство установщика](/install/installer).

## Системные требования

- **Node 24** (рекомендуется) или Node 22.14+ — скрипт установки обрабатывает это автоматически;
- **macOS, Linux или Windows** — поддерживаются как нативная Windows, так и WSL2; WSL2 более стабильна. См. [Windows](/platforms/windows).
- `pnpm` требуется только в случае сборки из исходного кода.

## Альтернативные способы установки

### Установщик с локальным префиксом (`install-cli.sh`)

Используйте этот способ, если вы хотите, чтобы OpenClaw и Node находились в локальном префиксе (например, `~/.openclaw`), не завися от системной установки Node:

```bash
curl -fsSL https://openclaw.ai/install-cli.sh | bash
```

По умолчанию поддерживается установка через npm, а также установка через git-checkout в рамках того же потока с префиксом. Полная справка: [Внутреннее устройство установщика](/install/installer#install-clish).

### npm, pnpm или bun

Если вы уже самостоятельно управляете Node:

<Tabs>
  <Tab title="npm">
    ```bash
    npm install -g openclaw@latest
    openclaw onboard --install-daemon
    ```
  </Tab>
  <Tab title="pnpm">
    ```bash
    pnpm add -g openclaw@latest
    pnpm approve-builds -g
    openclaw onboard --install-daemon
    ```

    <Note>
    Для pnpm требуется явное одобрение пакетов со скриптами сборки. После первой установки выполните команду `pnpm approve-builds -g`.
    </Note>

  </Tab>
  <Tab title="bun">
    ```bash
    bun add -g openclaw@latest
    openclaw onboard --install-daemon
    ```

    <Note>
    Bun поддерживается для установки глобального CLI. Для среды выполнения Gateway рекомендуется использовать Node в качестве демона.
    </Note>

  </Tab>
</Tabs>

<Accordion title="Устранение неполадок: ошибки сборки sharp (npm)">
  Если возникает ошибка в `sharp` из-за глобально установленной libvips:

```bash
SHARP_IGNORE_GLOBAL_LIBVIPS=1 npm install -g openclaw@latest
```

</Accordion>

### Из исходного кода

Для участников проекта или тех, кто хочет запустить программу из локальной копии:

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install && pnpm ui:build && pnpm build
pnpm link --global
openclaw onboard --install-daemon
```

Или пропустите этап link и используйте `pnpm openclaw ...` внутри репозитория. См. [Настройка](/start/setup) для ознакомления с полными рабочими процессами разработки.

### Установка из основной ветки GitHub

```bash
npm install -g github:openclaw/openclaw#main
```

### Контейнеры и менеджеры пакетов

<CardGroup cols={2}>
  <Card title="Docker" href="/install/docker" icon="container">
    Развёртывание в контейнерах или без графического интерфейса.
  </Card>
  <Card title="Podman" href="/install/podman" icon="container">
    Альтернатива Docker для контейнеров без прав root.
  </Card>
  <Card title="Nix" href="/install/nix" icon="snowflake">
    Декларативная установка через Nix flake.
  </Card>
  <Card title="Ansible" href="/install/ansible" icon="server">
    Автоматизированная подготовка парка устройств.
  </Card>
  <Card title="Bun" href="/install/bun" icon="zap">
    Использование только CLI через среду выполнения Bun.
  </Card>
</CardGroup>

## Проверка установки

```bash
openclaw --version      # убедитесь, что CLI доступен
openclaw doctor         # проверьте наличие проблем с конфигурацией
openclaw gateway status # убедитесь, что Gateway запущен
```

Если вы хотите настроить автоматический запуск после установки:

- macOS: LaunchAgent через `openclaw onboard --install-daemon` или `openclaw gateway install`;
- Linux/WSL2: пользовательская служба systemd через те же команды;
- Нативная Windows: сначала запланированная задача, а если создание задачи запрещено — элемент входа в папку автозагрузки для каждого пользователя.

## Хостинг и развёртывание

Разверните OpenClaw на облачном сервере или VPS:

<CardGroup cols={3}>
  <Card title="VPS" href="/vps">Любой Linux VPS</Card>
  <Card title="Docker VM" href="/install/docker-vm-runtime">Общие шаги для Docker</Card>
  <Card title="Kubernetes" href="/install/kubernetes">K8s</Card>
  <Card title="Fly.io" href="/install/fly">Fly.io</Card>
  <Card title="Hetzner" href="/install/hetzner">Hetzner</Card>
  <Card title="GCP" href="/install/gcp">Google Cloud</Card>
  <Card title="Azure" href="/install/azure">Azure</Card>
  <Card title="Railway" href="/install/railway">Railway</Card>
  <Card title="Render" href="/install/render">Render</Card>
  <Card title="Northflank" href="/install/northflank">Northflank</Card>
</CardGroup>

## Обновление, перенос или удаление

<CardGroup cols={3}>
  <Card title="Обновление" href="/install/updating" icon="refresh-cw">
    Поддерживайте OpenClaw в актуальном состоянии.
  </Card>
  <Card title="Перенос" href="/install/migrating" icon="arrow-right">
    Перенесите данные на новый компьютер.
  </Card>
  <Card title="Удаление" href="/install/uninstall" icon="trash-2">
    Полностью удалите OpenClaw.
  </Card>
</CardGroup>

## Устранение неполадок: команда `openclaw` не найдена

Если установка прошла успешно, но команда `openclaw` не найдена в терминале:

```bash
node -v           # Установлен ли Node?
npm prefix -g     # Где находятся глобальные пакеты?
echo "$PATH"      # Находится ли каталог глобальных исполняемых файлов в PATH?
```

Если `$(npm prefix -g)/bin` отсутствует в `$PATH`, добавьте его в файл запуска оболочки (`~/.zshrc` или `~/.bashrc`):

```bash
export PATH="$(npm prefix -g)/bin:$PATH"
```

Затем откройте новый терминал. Подробнее см. в разделе [Настройка Node](/install/node).