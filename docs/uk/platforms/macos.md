---
read_when:
    - Реалізація функцій додатка macOS
    - Зміна життєвого циклу Gateway або мостового з’єднання Node на macOS
summary: Додаток-супутник OpenClaw для macOS (рядок меню + брокер Gateway)
title: Додаток macOS
x-i18n:
    generated_at: "2026-04-17T07:59:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: d637df2f73ced110223c48ea3c934045d782e150a46495f434cf924a6a00baf0
    source_path: platforms/macos.md
    workflow: 15
---

# Супутник OpenClaw для macOS (рядок меню + брокер Gateway)

Додаток macOS є **супутником у рядку меню** для OpenClaw. Він відповідає за дозволи,
керує Gateway локально або під’єднується до нього (через launchd або вручну), а також надає можливості macOS
агенту як Node.

## Що він робить

- Показує нативні сповіщення та статус у рядку меню.
- Керує запитами TCC (Сповіщення, Універсальний доступ, Запис екрана, Мікрофон,
  Розпізнавання мовлення, Automation/AppleScript).
- Запускає Gateway або під’єднується до нього (локального чи віддаленого).
- Надає інструменти лише для macOS (Canvas, Camera, Screen Recording, `system.run`).
- Запускає локальну службу хоста Node у режимі **remote** (launchd) і зупиняє її в режимі **local**.
- За потреби розміщує **PeekabooBridge** для автоматизації UI.
- За запитом встановлює глобальний CLI (`openclaw`) через npm, pnpm або bun (додаток надає перевагу npm, потім pnpm, потім bun; Node лишається рекомендованим середовищем виконання для Gateway).

## Режим local і remote

- **Local** (типово): додаток під’єднується до запущеного локального Gateway, якщо він є;
  інакше вмикає службу launchd через `openclaw gateway install`.
- **Remote**: додаток під’єднується до Gateway через SSH/Tailscale і ніколи не запускає
  локальний процес.
  Додаток запускає локальну **службу хоста Node**, щоб віддалений Gateway міг отримати доступ до цього Mac.
  Додаток не породжує Gateway як дочірній процес.
  Виявлення Gateway тепер надає перевагу іменам Tailscale MagicDNS замість сирих IP-адрес tailnet,
  тому додаток для Mac надійніше відновлюється, коли IP-адреси tailnet змінюються.

## Керування launchd

Додаток керує користувацьким LaunchAgent з міткою `ai.openclaw.gateway`
(або `ai.openclaw.<profile>` при використанні `--profile`/`OPENCLAW_PROFILE`; застарілі `com.openclaw.*` усе ще вивантажуються).

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.gateway
launchctl bootout gui/$UID/ai.openclaw.gateway
```

Замініть мітку на `ai.openclaw.<profile>`, якщо використовуєте іменований профіль.

Якщо LaunchAgent не встановлено, увімкніть його в додатку або виконайте
`openclaw gateway install`.

## Можливості Node (mac)

Додаток macOS представляє себе як Node. Поширені команди:

- Canvas: `canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
- Camera: `camera.snap`, `camera.clip`
- Screen: `screen.snapshot`, `screen.record`
- System: `system.run`, `system.notify`

Node повідомляє карту `permissions`, щоб агенти могли визначити, що дозволено.

Служба Node + IPC додатка:

- Коли працює безголова служба хоста Node (режим remote), вона під’єднується до Gateway WS як Node.
- `system.run` виконується в додатку macOS (контекст UI/TCC) через локальний Unix-сокет; запити та вивід залишаються в межах додатка.

Діаграма (SCI):

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## Підтвердження виконання (system.run)

`system.run` керується через **Exec approvals** у додатку macOS (Settings → Exec approvals).
Параметри security + ask + allowlist зберігаються локально на Mac у:

```
~/.openclaw/exec-approvals.json
```

Приклад:

```json
{
  "version": 1,
  "defaults": {
    "security": "deny",
    "ask": "on-miss"
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [{ "pattern": "/opt/homebrew/bin/rg" }]
    }
  }
}
```

Примітки:

- Записи `allowlist` — це glob-шаблони для визначених шляхів до бінарних файлів.
- Сирий текст shell-команди, що містить керувальний або розширювальний синтаксис shell (`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`), вважається промахом по allowlist і потребує явного підтвердження (або додавання бінарного файлу shell до allowlist).
- Вибір “Always Allow” у запиті додає цю команду до allowlist.
- Перевизначення середовища для `system.run` фільтруються (відкидаються `PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`, `SHELLOPTS`, `PS4`), а потім об’єднуються із середовищем додатка.
- Для оболонкових обгорток (`bash|sh|zsh ... -c/-lc`) перевизначення середовища в межах запиту зводяться до невеликого явного allowlist (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
- Для рішень allow-always у режимі allowlist відомі обгортки диспетчеризації (`env`, `nice`, `nohup`, `stdbuf`, `timeout`) зберігають внутрішні шляхи до виконуваних файлів, а не шляхи обгорток. Якщо безпечне розгортання неможливе, запис allowlist автоматично не зберігається.

## Глибокі посилання

Додаток реєструє URL-схему `openclaw://` для локальних дій.

### `openclaw://agent`

Запускає запит `agent` до Gateway.
__OC_I18N_900004__
Параметри запиту:

- `message` (обов’язковий)
- `sessionKey` (необов’язковий)
- `thinking` (необов’язковий)
- `deliver` / `to` / `channel` (необов’язкові)
- `timeoutSeconds` (необов’язковий)
- `key` (необов’язковий ключ для unattended mode)

Безпека:

- Без `key` додаток запитує підтвердження.
- Без `key` додаток застосовує коротке обмеження довжини повідомлення для запиту підтвердження й ігнорує `deliver` / `to` / `channel`.
- Із чинним `key` виконання відбувається в unattended mode (призначено для персональних автоматизацій).

## Процес початкового налаштування (типовий)

1. Встановіть і запустіть **OpenClaw.app**.
2. Пройдіть контрольний список дозволів (запити TCC).
3. Переконайтеся, що активний режим **Local** і Gateway запущено.
4. Встановіть CLI, якщо хочете доступ із термінала.

## Розміщення каталогу стану (macOS)

Уникайте розміщення каталогу стану OpenClaw в iCloud або інших папках, що синхронізуються з хмарою.
Шляхи з увімкненою синхронізацією можуть додавати затримку й інколи спричиняти конфлікти блокувань файлів або синхронізації
для сесій і облікових даних.

Надавайте перевагу локальному шляху стану без синхронізації, наприклад:
__OC_I18N_900005__
Якщо `openclaw doctor` виявить стан у:

- `~/Library/Mobile Documents/com~apple~CloudDocs/...`
- `~/Library/CloudStorage/...`

він покаже попередження й порекомендує повернутися до локального шляху.

## Робочий процес збирання та розробки (нативний)

- `cd apps/macos && swift build`
- `swift run OpenClaw` (або Xcode)
- Пакування додатка: `scripts/package-mac-app.sh`

## Налагодження з’єднання з Gateway (macOS CLI)

Використовуйте CLI для налагодження, щоб перевірити те саме рукостискання WebSocket Gateway і логіку виявлення,
які використовує додаток macOS, не запускаючи сам додаток.
__OC_I18N_900006__
Параметри connect:

- `--url <ws://host:port>`: перевизначити конфігурацію
- `--mode <local|remote>`: визначити з конфігурації (типово: конфігурація або local)
- `--probe`: примусово виконати нову перевірку стану
- `--timeout <ms>`: час очікування запиту (типово: `15000`)
- `--json`: структурований вивід для порівняння

Параметри discovery:

- `--include-local`: включити Gateway, які інакше були б відфільтровані як “local”
- `--timeout <ms>`: загальне вікно виявлення (типово: `2000`)
- `--json`: структурований вивід для порівняння

Порада: порівняйте з `openclaw gateway discover --json`, щоб побачити, чи
конвеєр виявлення додатка macOS (`local.` плюс налаштований wide-area domain із
резервними варіантами wide-area і Tailscale Serve) відрізняється від
виявлення на основі `dns-sd` у Node CLI.

## Внутрішня логіка віддаленого з’єднання (SSH-тунелі)

Коли додаток macOS працює в режимі **Remote**, він відкриває SSH-тунель, щоб локальні компоненти UI
могли взаємодіяти з віддаленим Gateway так, ніби він працює на localhost.

### Керувальний тунель (порт WebSocket Gateway)

- **Призначення:** перевірки стану, статус, Web Chat, конфігурація та інші виклики control-plane.
- **Локальний порт:** порт Gateway (типово `18789`), завжди сталий.
- **Віддалений порт:** той самий порт Gateway на віддаленому хості.
- **Поведінка:** без випадкового локального порту; додаток повторно використовує наявний справний тунель
  або перезапускає його за потреби.
- **Форма SSH:** `ssh -N -L <local>:127.0.0.1:<remote>` з параметрами BatchMode +
  ExitOnForwardFailure + keepalive.
- **Звітування про IP:** SSH-тунель використовує loopback, тому gateway бачитиме IP
  Node як `127.0.0.1`. Використовуйте транспорт **Direct (ws/wss)**, якщо хочете, щоб відображалася
  справжня IP-адреса клієнта (див. [віддалений доступ macOS](/uk/platforms/mac/remote)).

Інструкції з налаштування див. у [віддалений доступ macOS](/uk/platforms/mac/remote). Докладніше про протокол —
у [протокол Gateway](/uk/gateway/protocol).

## Пов’язана документація

- [Інструкція з Gateway](/uk/gateway)
- [Gateway (macOS)](/uk/platforms/mac/bundled-gateway)
- [Дозволи macOS](/uk/platforms/mac/permissions)
- [Canvas](/uk/platforms/mac/canvas)
