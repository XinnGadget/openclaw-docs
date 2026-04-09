---
summary: "Поддержка Windows: нативные способы установки и установка через WSL2, демон и текущие ограничения"
read_when:
  - Установка OpenClaw на Windows
  - Выбор между нативной Windows и WSL2
  - Поиск информации о статусе сопутствующего приложения для Windows
title: "Windows"
---

# Windows

OpenClaw поддерживает как **нативную Windows**, так и **WSL2**. WSL2 — более стабильный вариант, рекомендуемый для полноценного использования: CLI, Gateway и инструменты работают в среде Linux с полной совместимостью. Нативная Windows подходит для базового использования CLI и Gateway, однако с некоторыми ограничениями, указанными ниже.

Планируется выпуск сопутствующих приложений для нативной Windows.

## WSL2 (рекомендуется)

- [Начало работы](/start/getting-started) (использовать внутри WSL)
- [Установка и обновления](/install/updating)
- Официальное руководство по WSL2 (Microsoft): [https://learn.microsoft.com/windows/wsl/install](https://learn.microsoft.com/windows/wsl/install)

## Статус нативной Windows

Функциональность CLI в нативной Windows совершенствуется, но WSL2 по-прежнему остаётся рекомендуемым вариантом.

Что хорошо работает в нативной Windows на текущий момент:

- установщик веб-сайта через `install.ps1`;
- локальное использование CLI, например: `openclaw --version`, `openclaw doctor`, `openclaw plugins list --json`;
- встроенные проверки локального агента/провайдера, например:

```powershell
openclaw agent --local --agent main --thinking low -m "Reply with exactly WINDOWS-HATCH-OK."
```

Текущие ограничения:

- `openclaw onboard --non-interactive` по-прежнему требует доступного локального шлюза, если не передан параметр `--skip-health`;
- `openclaw onboard --non-interactive --install-daemon` и `openclaw gateway install` сначала пытаются использовать планировщик задач Windows;
- если создание задачи в планировщике отклонено, OpenClaw переключается на элемент автозагрузки в папке "Автозагрузка" для текущего пользователя и запускает шлюз немедленно;
- если `schtasks` зависает или перестаёт отвечать, OpenClaw теперь быстро прерывает этот процесс и переключается на альтернативный вариант, вместо того чтобы бесконечно ждать;
- планировщик задач по-прежнему предпочтительнее, когда он доступен, поскольку обеспечивает более качественный статус супервизора.

Если вам нужен только нативный CLI без установки службы шлюза, используйте один из следующих вариантов:

```powershell
openclaw onboard --non-interactive --skip-health
openclaw gateway run
```

Если вы хотите управляемую автозагрузку в нативной Windows:

```powershell
openclaw gateway install
openclaw gateway status --json
```

Если создание задачи в планировщике заблокировано, резервный режим службы по-прежнему автоматически запускается после входа в систему через папку "Автозагрузка" текущего пользователя.

## Gateway

- [Руководство по Gateway](/gateway)
- [Конфигурация](/gateway/configuration)

## Установка службы Gateway (CLI)

Внутри WSL2:

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

## Автозапуск Gateway до входа в Windows

Для безголовых установок убедитесь, что полная цепочка загрузки выполняется, даже если никто не входит в Windows.

### 1) Сохранение работы пользовательских служб без входа в систему

Внутри WSL:

```bash
sudo loginctl enable-linger "$(whoami)"
```

### 2) Установка пользовательской службы Gateway OpenClaw

Внутри WSL:

```bash
openclaw gateway install
```

### 3) Автоматический запуск WSL при загрузке Windows

В PowerShell от имени администратора:

```powershell
schtasks /create /tn "WSL Boot" /tr "wsl.exe -d Ubuntu --exec /bin/true" /sc onstart /ru SYSTEM
```

Замените `Ubuntu` на название вашего дистрибутива из списка:

```powershell
wsl --list --verbose
```

### Проверка цепочки запуска

После перезагрузки (до входа в Windows) проверьте из WSL:

```bash
systemctl --user is-enabled openclaw-gateway.service
systemctl --user status openclaw-gateway.service --no-pager
```

## Дополнительно: предоставление доступа к службам WSL через локальную сеть (portproxy)

WSL имеет собственную виртуальную сеть. Если другой компьютер должен получить доступ к службе, работающей **внутри WSL** (SSH, локальный сервер TTS или Gateway), необходимо перенаправить порт Windows на текущий IP-адрес WSL. IP-адрес WSL меняется после перезагрузки, поэтому может потребоваться обновление правила перенаправления.

Пример (PowerShell **от имени администратора**):

```powershell
$Distro = "Ubuntu-24.04"
$ListenPort = 2222
$TargetPort = 22

$WslIp = (wsl -d $Distro -- hostname -I).Trim().Split(" ")[0]
if (-not $WslIp) { throw "WSL IP not found." }

netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=$ListenPort `
  connectaddress=$WslIp connectport=$TargetPort
```

Разрешите порт в брандмауэре Windows (однократно):

```powershell
New-NetFirewallRule -DisplayName "WSL SSH $ListenPort" -Direction Inbound `
  -Protocol TCP -LocalPort $ListenPort -Action Allow
```

Обновите portproxy после перезагрузки WSL:

```powershell
netsh interface portproxy delete v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 | Out-Null
netsh interface portproxy add v4tov4 listenport=$ListenPort listenaddress=0.0.0.0 `
  connectaddress=$WslIp connectport=$TargetPort | Out-Null
```

Примечания:

- SSH с другого компьютера направлен на **IP-адрес хоста Windows** (например: `ssh user@windows-host -p 2222`).
- Удалённым узлам необходимо указать **доступный** URL шлюза (не `127.0.0.1`); используйте `openclaw status --all` для проверки.
- Используйте `listenaddress=0.0.0.0` для доступа через локальную сеть; `127.0.0.1` ограничивает доступ только локальной машиной.
- Если вы хотите автоматизировать этот процесс, зарегистрируйте задачу в планировщике задач для выполнения шага обновления при входе в систему.

## Пошаговая установка WSL2

### 1) Установка WSL2 + Ubuntu

Откройте PowerShell (от имени администратора):

```powershell
wsl --install
# Или выберите дистрибутив явно:
wsl --list --online
wsl --install -d Ubuntu-24.04
```

Перезагрузите компьютер, если Windows попросит об этом.

### 2) Включение systemd (требуется для установки шлюза)

В терминале WSL:

```bash
sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
```

Затем в PowerShell:

```powershell
wsl --shutdown
```

Снова откройте Ubuntu и проверьте:

```bash
systemctl --user status
```

### 3) Установка OpenClaw (внутри WSL)

Следуйте инструкции "Начало работы" для Linux внутри WSL:

```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build # автоматически устанавливает зависимости UI при первом запуске
pnpm build
openclaw onboard
```

Полное руководство: [Начало работы](/start/getting-started)

## Сопутствующее приложение для Windows

На данный момент сопутствующего приложения для Windows нет. Если вы хотите поучаствовать в его разработке — ваши вклады приветствуются.