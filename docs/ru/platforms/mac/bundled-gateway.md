---
summary: "Среда выполнения Gateway в macOS (внешняя служба launchd)"
read_when:
  - Упаковка OpenClaw.app
  - Отладка службы launchd шлюза в macOS
  - Установка CLI шлюза для macOS
title: "Gateway в macOS"
---

# Gateway в macOS (внешняя launchd)

OpenClaw.app больше не включает в себя Node/Bun или среду выполнения Gateway. Приложение для macOS предполагает наличие **внешней** установки CLI `openclaw`, не запускает Gateway как дочерний процесс и управляет службой launchd для каждого пользователя, чтобы поддерживать работу Gateway (или подключается к уже работающему локальному Gateway, если таковой имеется).

## Установка CLI (требуется для локального режима)

По умолчанию в Mac используется среда выполнения Node 24. Для обеспечения совместимости по‑прежнему подходит Node 22 LTS (в настоящее время — `22.14+`). Затем установите `openclaw` глобально:

```bash
npm install -g openclaw@<version>
```

Кнопка **Install CLI** в приложении для macOS запускает тот же процесс глобальной установки, который приложение использует внутри: сначала предпочтение отдаётся npm, затем pnpm, а затем bun — если это единственный обнаруженный менеджер пакетов. Node остаётся рекомендуемой средой выполнения для Gateway.

## Launchd (Gateway как LaunchAgent)

Метка:

- `ai.openclaw.gateway` (или `ai.openclaw.<profile>`; устаревшие метки вида `com.openclaw.*` могут сохраняться)

Расположение plist (для каждого пользователя):

- `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
  (или `~/Library/LaunchAgents/ai.openclaw.<profile>.plist`)

Управление:

- Приложение для macOS отвечает за установку/обновление LaunchAgent в локальном режиме.
- CLI также может установить его: `openclaw gateway install`.

Поведение:

- "OpenClaw Active" включает/отключает LaunchAgent.
- Завершение работы приложения **не** останавливает шлюз (launchd поддерживает его работу).
- Если Gateway уже запущен на настроенном порту, приложение подключается к нему, а не запускает новый экземпляр.

Логирование:

- stdout/err launchd: `/tmp/openclaw/openclaw-gateway.log`

## Совместимость версий

Приложение для macOS проверяет версию шлюза на соответствие собственной версии. Если они несовместимы, обновите глобальный CLI, чтобы он соответствовал версии приложения.

## Проверка работоспособности (smoke check)

```bash
openclaw --version

OPENCLAW_SKIP_CHANNELS=1 \
OPENCLAW_SKIP_CANVAS_HOST=1 \
openclaw gateway --port 18999 --bind loopback
```

Затем:

```bash
openclaw gateway call health --url ws://127.0.0.1:18999 --timeout 3000
```