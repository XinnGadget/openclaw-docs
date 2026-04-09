---
summary: "iMessage через сервер BlueBubbles для macOS (отправка/приём через REST, индикация набора текста, реакции, сопряжение, расширенные действия)".
read_when:
  - Настройка канала BlueBubbles.
  - Устранение неполадок при сопряжении вебхуков.
  - Настройка iMessage на macOS.
title: "BlueBubbles"
---

# BlueBubbles (macOS REST)

Статус: встроенный плагин, взаимодействующий с сервером BlueBubbles для macOS по HTTP. **Рекомендуется для интеграции с iMessage** благодаря более богатому API и более простой настройке по сравнению с устаревшим каналом imsg.

## Встроенный плагин

В текущих версиях OpenClaw плагин BlueBubbles включён в комплект, поэтому для стандартных сборок не требуется отдельный шаг `openclaw plugins install`.

## Обзор

- Работает на macOS через вспомогательное приложение BlueBubbles ([bluebubbles.app](https://bluebubbles.app)).
- Рекомендовано/протестировано: macOS Sequoia (15). macOS Tahoe (26) работает; в Tahoe в настоящее время нарушена работа редактирования, а обновления значков групп могут сообщать об успехе, но не синхронизироваться.
- OpenClaw взаимодействует с ним через REST API (`GET /api/v1/ping`, `POST /message/text`, `POST /chat/:id/*`).
- Входящие сообщения поступают через вебхуки; исходящие ответы, индикаторы набора текста, уведомления о прочтении и реакции отправляются через REST-запросы.
- Вложения и стикеры принимаются как входящие медиафайлы (и предоставляются агенту, когда это возможно).
- Сопряжение/список разрешённых отправителей работает так же, как и в других каналах (`/channels/pairing` и т. д.) с `channels.bluebubbles.allowFrom` + кодами сопряжения.
- Реакции предоставляются как системные события (аналогично Slack/Telegram), чтобы агенты могли "упоминать" их перед ответом.
- Расширенные функции: редактирование, отмена отправки, цепочки ответов, эффекты сообщений, управление группами.

## Быстрый старт

1. Установите сервер BlueBubbles на свой Mac (следуйте инструкциям на [bluebubbles.app/install](https://bluebubbles.app/install)).
2. В конфигурации BlueBubbles включите веб-API и задайте пароль.
3. Запустите `openclaw onboard` и выберите BlueBubbles или настройте вручную:

   ```json5
   {
     channels: {
       bluebubbles: {
         enabled: true,
         serverUrl: "http://192.168.1.100:1234",
         password: "example-password",
         webhookPath: "/bluebubbles-webhook",
       },
     },
   }
   ```

4. Настройте вебхуки BlueBubbles на ваш шлюз (пример: `https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`).
5. Запустите шлюз; он зарегистрирует обработчик вебхуков и начнёт сопряжение.

Примечание по безопасности:

- Всегда устанавливайте пароль для вебхука.
- Аутентификация вебхука обязательна. OpenClaw отклоняет запросы вебхуков BlueBubbles, если они не содержат пароль/guid, соответствующий `channels.bluebubbles.password` (например, `?password=<password>` или `x-password`), независимо от топологии loopback/proxy.
- Проверка пароля выполняется до чтения/анализа полного содержимого вебхука.

## Поддержание активности Messages.app (виртуальные машины / безголовые конфигурации)

В некоторых конфигурациях macOS (виртуальные машины / постоянно работающие системы) приложение Messages.app может перейти в режим "ожидания" (входящие события прекращаются до тех пор, пока приложение не будет открыто/выведено на передний план). Простой способ обойти это — **отправлять запрос к Messages каждые 5 минут** с помощью AppleScript + LaunchAgent.

### 1) Сохраните AppleScript

Сохраните скрипт как:

- `~/Scripts/poke-messages.scpt`

Пример скрипта (неинтерактивный; не захватывает фокус):

```applescript
try
  tell application "Messages"
    if not running then
      launch
    end if

    -- Коснуться интерфейса скриптинга, чтобы поддерживать отзывчивость процесса.
    set _chatCount to (count of chats)
  end tell
on error
  -- Игнорировать временные сбои (подсказки при первом запуске, заблокированная сессия и т. д.).
end try
```

### 2) Установите LaunchAgent

Сохраните как:

- `~/Library/LaunchAgents/com.user.poke-messages.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>com.user.poke-messages</string>

    <key>ProgramArguments</key>
    <array>
      <string>/bin/bash</string>
      <string>-lc</string>
      <string>/usr/bin/osascript &quot;$HOME/Scripts/poke-messages.scpt&quot;</string>
    </array>

    <key>RunAtLoad</key>
    <true/>

    <key>StartInterval</key>
    <integer>300</integer>

    <key>StandardOutPath</key>
    <string>/tmp/poke-messages.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/poke-messages.err</string>
  </dict>
</plist>
```

Примечания:

- Скрипт выполняется **каждые 300 секунд** и **при входе в систему**.
- При первом запуске могут появиться подсказки macOS **Automation** (`osascript` → Messages). Подтвердите их в той же пользовательской сессии, в которой запущен LaunchAgent.

Загрузите его:

```bash
launchctl unload ~/Library/LaunchAgents/com.user.poke-messages.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.user.poke-messages.plist
```

## Подключение

BlueBubbles доступен в интерактивном процессе подключения:

```
openclaw onboard
```

Мастер запрашивает:

- **URL сервера** (обязательно): адрес сервера BlueBubbles (например, `http://192.168.1.100:1234`).
- **Пароль** (обязательно): пароль API из настроек сервера BlueBubbles.
- **Путь к вебхуку** (необязательно): по умолчанию `/bluebubbles-webhook`.
- **Политика DM**: сопряжение, список разрешённых отправителей, открытый доступ или отключено.
- **Список разрешённых отправителей**: номера телефонов, электронные адреса или цели чата.

Вы также можете добавить BlueBubbles через CLI:

```
openclaw channels add bluebubbles --http-url http://192.168.1.100:1234 --password <password>
```

## Контроль доступа (DM и группы)

DM:

- По умолчанию: `channels.bluebubbles.dmPolicy = "pairing"`.
- Неизвестные отправители получают код сопряжения; сообщения игнорируются до утверждения (коды истекают через 1 час).
- Утверждение через:
  - `openclaw pairing list bluebubbles`
  - `openclaw pairing approve bluebubbles <CODE>`
- Сопряжение — это обмен токенами по умолчанию. Подробности: [Сопряжение](/channels/pairing).

Группы:

- `channels.bluebubbles.groupPolicy = open | allowlist | disabled` (по умолчанию: `allowlist`).
- `channels.bluebubbles.groupAllowFrom` управляет тем, кто может инициировать действия в группах при установленном значении `allowlist`.

### Обогащение имён контактов (macOS, необязательно)

Вебхуки групп BlueBubbles часто содержат только необработанные адреса участников. Если вы хотите, чтобы в контексте `GroupMembers` отображались локальные имена контактов, вы можете включить обогащение контактов из локальной адресной книги на macOS:

- `channels.bluebubbles.enrichGroupParticipantsFromContacts = true` включает поиск. По умолчанию: `false`.
- Поиск выполняется только после того, как доступ к группе, авторизация команд и фильтрация упоминаний позволили сообщению пройти.
- Обогащаются только участники без имён.
- Необработанные номера телефонов остаются в качестве запасного варианта, если локальное соответствие не найдено.

```json5
{
  channels: {
    bluebubbles: {
      enrichGroupParticipantsFromContacts: true,
    },
  },
}
```

### Фильтрация упоминаний (группы)

BlueBubbles поддерживает фильтрацию упоминаний для групповых чатов