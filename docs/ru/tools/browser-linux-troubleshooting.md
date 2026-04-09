 ---
summary: "Устранение проблем с запуском CDP в Chrome/Brave/Edge/Chromium для управления браузером OpenClaw в Linux"
read_when: "Управление браузером не работает в Linux, особенно при использовании Chromium из snap"
title: "Устранение неполадок с браузером"
---

# Устранение неполадок с браузером (Linux)

## Проблема: "Не удалось запустить Chrome CDP на порту 18800"

Сервер управления браузером OpenClaw не может запустить Chrome/Brave/Edge/Chromium с ошибкой:

```
{"error":"Error: Failed to start Chrome CDP on port 18800 for profile \"openclaw\"."}
```

### Основная причина

В Ubuntu (и многих дистрибутивах Linux) по умолчанию Chromium устанавливается как **snap-пакет**. Ограничения AppArmor в snap мешают OpenClaw запускать и отслеживать процесс браузера.

Команда `apt install chromium` устанавливает заглушку, которая перенаправляет на snap:

```
Note, selecting 'chromium-browser' instead of 'chromium'
chromium-browser is already the newest version (2:1snap1-0ubuntu2).
```

Это НЕ настоящий браузер — это лишь оболочка.

### Решение 1: Установить Google Chrome (рекомендуется)

Установите официальный пакет Google Chrome в формате `.deb`, который не ограничивается snap:

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt --fix-broken install -y  # если есть ошибки зависимостей
```

Затем обновите конфигурацию OpenClaw (`~/.openclaw/openclaw.json`):

```json
{
  "browser": {
    "enabled": true,
    "executablePath": "/usr/bin/google-chrome-stable",
    "headless": true,
    "noSandbox": true
  }
}
```

### Решение 2: Использовать Chromium из snap в режиме только подключения (Attach-Only)

Если необходимо использовать Chromium из snap, настройте OpenClaw на подключение к браузеру, запущенному вручную:

1. Обновите конфигурацию:

```json
{
  "browser": {
    "enabled": true,
    "attachOnly": true,
    "headless": true,
    "noSandbox": true
  }
}
```

2. Запустите Chromium вручную:

```bash
chromium-browser --headless --no-sandbox --disable-gpu \
  --remote-debugging-port=18800 \
  --user-data-dir=$HOME/.openclaw/browser/openclaw/user-data \
  about:blank &
```

3. При необходимости создайте пользовательский сервис systemd для автоматического запуска Chrome:

```ini
# ~/.config/systemd/user/openclaw-browser.service
[Unit]
Description=OpenClaw Browser (Chrome CDP)
After=network.target

[Service]
ExecStart=/snap/bin/chromium --headless --no-sandbox --disable-gpu --remote-debugging-port=18800 --user-data-dir=%h/.openclaw/browser/openclaw/user-data about:blank
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Активируйте с помощью: `systemctl --user enable --now openclaw-browser.service`

### Проверка работоспособности браузера

Проверьте статус:

```bash
curl -s http://127.0.0.1:18791/ | jq '{running, pid, chosenBrowser}'
```

Протестируйте работу браузера:

```bash
curl -s -X POST http://127.0.0.1:18791/start
curl -s http://127.0.0.1:18791/tabs
```

### Справочная информация по конфигурации

| Параметр | Описание | Значение по умолчанию |
| ------------------------ | -------------------------------------------------------------------- | ----------------------------------------------------------- |
| `browser.enabled` | Включить управление браузером | `true` |
| `browser.executablePath` | Путь к исполняемому файлу браузера на базе Chromium (Chrome/Brave/Edge/Chromium) | Автоопределение (предпочитает браузер по умолчанию, если он на базе Chromium) |
| `browser.headless` | Запускать без графического интерфейса | `false` |
| `browser.noSandbox` | Добавить флаг `--no-sandbox` (требуется для некоторых конфигураций Linux) | `false` |
| `browser.attachOnly` | Не запускать браузер, а только подключаться к существующему | `false` |
| `browser.cdpPort` | Порт протокола Chrome DevTools (CDP) | `18800` |

### Проблема: "Не найдено вкладок Chrome для профиля="user""

Вы используете профиль `existing-session` / Chrome MCP. OpenClaw видит локальный Chrome, но нет открытых вкладок, к которым можно подключиться.

Варианты решения:

1. **Использовать управляемый браузер:** `openclaw browser start --browser-profile openclaw` (или установить `browser.defaultProfile: "openclaw"`).
2. **Использовать Chrome MCP:** убедитесь, что локальный Chrome запущен и в нём открыта хотя бы одна вкладка, затем повторите попытку с `--browser-profile user`.

Примечания:

* `user` работает только на хосте. Для Linux-серверов, контейнеров или удалённых хостов предпочтительнее использовать профили CDP.
* Профили `user` и другие профили `existing-session` сохраняют текущие ограничения Chrome MCP: действия, управляемые ссылками, хуки загрузки одного файла, отсутствие переопределения тайм-аута диалогов, отсутствие поддержки `wait --load networkidle`, а также отсутствие поддержки `responsebody`, экспорта в PDF, перехвата загрузок и пакетных действий.
* Локальные профили `openclaw` автоматически назначают `cdpPort`/`cdpUrl`; эти параметры следует задавать только для удалённого CDP.
* Удалённые профили CDP поддерживают протоколы `http://`, `https://`, `ws://` и `wss://`. Используйте HTTP(S) для обнаружения через `/json/version` либо WS(S), если сервис браузера предоставляет прямой URL сокета DevTools.