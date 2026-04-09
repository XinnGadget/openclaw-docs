---
summary: "Полностью удалить OpenClaw (CLI, сервис, состояние, рабочее пространство)"
read_when:
  - Вы хотите удалить OpenClaw с компьютера
  - Сервис шлюза продолжает работать после удаления
title: "Удаление"
---

# Удаление

Есть два способа:

- **Простой способ**, если `openclaw` всё ещё установлен.
- **Ручное удаление сервиса**, если CLI удалён, но сервис продолжает работать.

## Простой способ (CLI всё ещё установлен)

Рекомендуется использовать встроенный деинсталлятор:

```bash
openclaw uninstall
```

Неинтерактивный режим (автоматизация / npx):

```bash
openclaw uninstall --all --yes --non-interactive
npx -y openclaw uninstall --all --yes --non-interactive
```

Ручные шаги (результат тот же):

1. Остановить сервис шлюза:

```bash
openclaw gateway stop
```

2. Удалить сервис шлюза (launchd/systemd/schtasks):

```bash
openclaw gateway uninstall
```

3. Удалить состояние и конфигурацию:

```bash
rm -rf "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
```

Если вы задали `OPENCLAW_CONFIG_PATH` в нестандартное расположение вне каталога состояния, удалите и этот файл.

4. Удалить рабочее пространство (необязательно, удаляет файлы агента):

```bash
rm -rf ~/.openclaw/workspace
```

5. Удалить установку CLI (выберите тот вариант, который вы использовали):

```bash
npm rm -g openclaw
pnpm remove -g openclaw
bun remove -g openclaw
```

6. Если вы установили приложение для macOS:

```bash
rm -rf /Applications/OpenClaw.app
```

Примечания:

- Если вы использовали профили (`--profile` / `OPENCLAW_PROFILE`), повторите шаг 3 для каждого каталога состояния (по умолчанию — `~/.openclaw-<профиль>`).
- В удалённом режиме каталог состояния находится на **хосте шлюза**, поэтому выполните шаги 1–4 также на нём.

## Ручное удаление сервиса (CLI не установлен)

Используйте этот способ, если сервис шлюза продолжает работать, но `openclaw` отсутствует.

### macOS (launchd)

Метка по умолчанию — `ai.openclaw.gateway` (или `ai.openclaw.<профиль>`; могут по-прежнему существовать устаревшие метки вида `com.openclaw.*`):

```bash
launchctl bootout gui/$UID/ai.openclaw.gateway
rm -f ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

Если вы использовали профиль, замените метку и имя plist-файла на `ai.openclaw.<профиль>`. Удалите любые устаревшие plist-файлы вида `com.openclaw.*`, если они есть.

### Linux (пользовательский юнит systemd)

Имя юнита по умолчанию — `openclaw-gateway.service` (или `openclaw-gateway-<профиль>.service`):

```bash
systemctl --user disable --now openclaw-gateway.service
rm -f ~/.config/systemd/user/openclaw-gateway.service
systemctl --user daemon-reload
```

### Windows (запланированная задача)

Имя задачи по умолчанию — `OpenClaw Gateway` (или `OpenClaw Gateway (<профиль>)`).
Скрипт задачи находится в вашем каталоге состояния.

```powershell
schtasks /Delete /F /TN "OpenClaw Gateway"
Remove-Item -Force "$env:USERPROFILE\.openclaw\gateway.cmd"
```

Если вы использовали профиль, удалите соответствующую задачу и файл `~\.openclaw-<профиль>\gateway.cmd`.

## Обычная установка и клонирование исходного кода

### Обычная установка (install.sh / npm / pnpm / bun)

Если вы использовали `https://openclaw.ai/install.sh` или `install.ps1`, CLI был установлен командой `npm install -g openclaw@latest`.
Удалите его с помощью `npm rm -g openclaw` (или `pnpm remove -g` / `bun remove -g`, если вы использовали эти инструменты).

### Клонирование исходного кода (git clone)

Если вы запускали программу из клонированного репозитория (`git clone` + `openclaw ...` / `bun run openclaw ...`):

1. Удалите сервис шлюза **до** удаления репозитория (используйте простой способ, описанный выше, или ручное удаление сервиса).
2. Удалите каталог репозитория.
3. Удалите состояние и рабочее пространство, как показано выше.