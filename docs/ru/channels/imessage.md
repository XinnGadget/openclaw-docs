---
summary: "Поддержка устаревшей версии iMessage через imsg (JSON-RPC через stdio). Для новых установок следует использовать BlueBubbles".
read_when:
  - Настройка поддержки iMessage
  - Отладка отправки/получения сообщений iMessage
title: "iMessage"
---

# iMessage (устаревшая версия: imsg)

<Warning>
Для новых развёртываний iMessage используйте <a href="/channels/bluebubbles">BlueBubbles</a>.

Интеграция `imsg` является устаревшей и может быть удалена в будущих версиях.
</Warning>

Статус: устаревшая внешняя интеграция CLI. Шлюз запускает `imsg rpc` и взаимодействует через JSON-RPC на stdio (без отдельного демона/порта).

<CardGroup cols={3}>
  <Card title="BlueBubbles (рекомендуется)" icon="message-circle" href="/channels/bluebubbles">
    Предпочтительный способ настройки iMessage для новых установок.
  </Card>
  <Card title="Сопряжение" icon="link" href="/channels/pairing">
    По умолчанию для личных сообщений iMessage используется режим сопряжения.
  </Card>
  <Card title="Справочник по конфигурации" icon="settings" href="/gateway/configuration-reference#imessage">
    Полный справочник по полям iMessage.
  </Card>
</CardGroup>

## Быстрая настройка

<Tabs>
  <Tab title="Локальный Mac (быстрый способ)">
    <Steps>
      <Step title="Установите и проверьте imsg">

```bash
brew install steipete/tap/imsg
imsg rpc --help
```

      </Step>

      <Step title="Настройте OpenClaw">

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "/usr/local/bin/imsg",
      dbPath: "/Users/<you>/Library/Messages/chat.db",
    },
  },
}
```

      </Step>

      <Step title="Запустите шлюз">

```bash
openclaw gateway
```

      </Step>

      <Step title="Одобрите первое сопряжение для личных сообщений (политика dmPolicy по умолчанию)">

```bash
openclaw pairing list imessage
openclaw pairing approve imessage <CODE>
```

        Запросы на сопряжение истекают через 1 час.
      </Step>
    </Steps>

  </Tab>

  <Tab title="Удалённый Mac через SSH">
    OpenClaw требует только совместимый с stdio `cliPath`, поэтому вы можете указать `cliPath` на скрипт-обёртку, который подключается по SSH к удалённому Mac и запускает `imsg`.

```bash
#!/usr/bin/env bash
exec ssh -T gateway-host imsg "$@"
```

    Рекомендуемая конфигурация при включённой поддержке вложений:

```json5
{
  channels: {
    imessage: {
      enabled: true,
      cliPath: "~/.openclaw/scripts/imsg-ssh",
      remoteHost: "user@gateway-host", // используется для загрузки вложений через SCP
      includeAttachments: true,
      // Опционально: переопределите разрешённые корневые каталоги для вложений.
      // По умолчанию включены /Users/*/Library/Messages/Attachments
      attachmentRoots: ["/Users/*/Library/Messages/Attachments"],
      remoteAttachmentRoots: ["/Users/*/Library/Messages/Attachments"],
    },
  },
}
```

    Если `remoteHost` не задан, OpenClaw попытается автоматически определить его, проанализировав скрипт-обёртку SSH.
    `remoteHost` должен быть указан как `host` или `user@host` (без пробелов или опций SSH).
    OpenClaw использует строгую проверку ключей хоста для SCP, поэтому ключ хоста-реле должен уже присутствовать в `~/.ssh/known_hosts`.
    Пути к вложениям проверяются на соответствие разрешённым корневым каталогам (`attachmentRoots` / `remoteAttachmentRoots`).

  </Tab>
</Tabs>

## Требования и разрешения (macOS)

- В приложении Messages на Mac, где запущен `imsg`, должен быть выполнен вход.
- Для процесса, в контексте которого запущен OpenClaw/`imsg` (доступ к базе данных Messages), требуется полный доступ к диску.
- Для отправки сообщений через Messages.app требуется разрешение на автоматизацию.

<Tip>
Разрешения предоставляются для каждого контекста процесса. Если шлюз работает в фоновом режиме (LaunchAgent/SSH), выполните одноразовую интерактивную команду в том же контексте, чтобы вызвать запросы на предоставление разрешений:

```bash
imsg chats --limit 1
# или
imsg send <handle> "test"
```

</Tip>

## Контроль доступа и маршрутизация

<Tabs>
  <Tab title="Политика личных сообщений">
    `channels.imessage.dmPolicy` управляет личными сообщениями:

    - `pairing` (по умолчанию)
    - `allowlist`
    - `open` (требуется, чтобы `allowFrom` включал `"*"`)
    - `disabled`

    Поле списка разрешённых: `channels.imessage.allowFrom`.

    Элементы списка разрешённых могут быть идентификаторами или целями чата (`chat_id:*`, `chat_guid:*`, `chat_identifier:*`).

  </Tab>

  <Tab title="Политика групп + упоминания">
    `channels.imessage.groupPolicy` управляет обработкой групп:

    - `allowlist` (по умолчанию при настройке)
    - `open`
    - `disabled`

    Список разрешённых отправителей для групп: `channels.imessage.groupAllowFrom`.

    Резервный вариант во время выполнения: если `groupAllowFrom` не задан, проверка отправителей групповых сообщений iMessage возвращается к `allowFrom`, если он доступен.
    Примечание во время выполнения: если `channels.imessage` полностью отсутствует, во время выполнения используется `groupPolicy="allowlist"` и выводится предупреждение (даже если задан `channels.defaults.groupPolicy`).

    Контроль упоминаний в группах:

    - В iMessage нет собственных метаданных об упоминаниях
    - Для обнаружения упоминаний используются шаблоны регулярных выражений (`agents.list[].groupChat.mentionPatterns`, резервный вариант `messages.groupChat.mentionPatterns`)
    - Если шаблоны не настроены, контроль упоминаний не может быть применён

    Команды управления от авторизованных отправителей могут обходить контроль упоминаний в группах.

  </Tab>

  <Tab title="Сессии и детерминированные ответы">
    - Личные сообщения используют прямую маршрутизацию; группы — групповую маршрутизацию.
    - При значении по умолчанию `session.dmScope=main` личные сообщения iMessage объединяются в основную сессию агента.
    - Групповые сессии изолированы (`agent:<agentId>:imessage:group:<chat_id>`).
    - Ответы направляются обратно в iMessage с использованием метаданных исходного канала/цели.

    Поведение потоков, похожих на групповые:

    Некоторые многопользовательские потоки iMessage могут поступать с `is_group=false`.
    Если этот `chat_id` явно настроен в `channels.imessage.groups`, OpenClaw обрабатывает его как групповой трафик (групповой контроль + изоляция групповой сессии).

  </Tab>
</Tabs>

## Привязки разговоров ACP

Устаревшие чаты iMessage также можно привязать к сессиям ACP.

Быстрый поток оператора:

- Выполните `/acp spawn codex --bind here` внутри личного сообщения или разрешённого группового чата.
- Будущие сообщения в этом же разговоре iMessage будут направляться в созданную сессию ACP.
- Команды `/new` и `/reset` сбрасывают ту же привязанную сессию ACP на месте.
- Команда `/acp close` закрывает сессию ACP и удаляет привязку.

Настроенные постоянные привязки поддерживаются через записи верхнего уровня `bindings[]` с `type: "acp"` и `match.channel: "imessage"`.

`match.peer.id` может использовать:

- нормализованный идентификатор личного сообщения, например `+15555550123` или `user@example.com`
- `chat_id:<id>` (рекомендуется для стабильных групповых привязок)
- `chat_guid:<guid>`
- `chat_identifier:<identifier>`

Пример:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: { agent: "codex", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "imessage",
        accountId: "default",
        peer: { kind: "group", id: "