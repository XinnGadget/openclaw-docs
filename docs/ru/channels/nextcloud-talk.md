---
summary: "Статус поддержки, возможности и конфигурация Nextcloud Talk"
read_when:
  - Работа над функциями канала Nextcloud Talk
title: "Nextcloud Talk"
---

# Nextcloud Talk

Статус: плагин в комплекте (webhook-бот). Поддерживаются прямые сообщения, комнаты, реакции и сообщения в формате Markdown.

## Плагин в комплекте

Nextcloud Talk поставляется в качестве плагина в комплекте с текущими версиями OpenClaw, поэтому для обычных упакованных сборок отдельная установка не требуется.

Если вы используете более старую сборку или кастомную установку, в которой отсутствует Nextcloud Talk, установите его вручную:

Установка через CLI (реестр npm):

```bash
openclaw plugins install @openclaw/nextcloud-talk
```

Локальная проверка (при работе из репозитория git):

```bash
openclaw plugins install ./path/to/local/nextcloud-talk-plugin
```

Подробности: [Плагины](/tools/plugin)

## Быстрая настройка (для начинающих)

1. Убедитесь, что плагин Nextcloud Talk доступен:
   - В текущих упакованных версиях OpenClaw он уже включён.
   - В более старых или кастомных установках его можно добавить вручную с помощью команд, приведённых выше.
2. На сервере Nextcloud создайте бота:

   ```bash
   ./occ talk:bot:install "OpenClaw" "<shared-secret>" "<webhook-url>" --feature reaction
   ```

3. Включите бота в настройках целевой комнаты.
4. Настройте OpenClaw:
   - Конфигурация: `channels.nextcloud-talk.baseUrl` + `channels.nextcloud-talk.botSecret`
   - Или переменные окружения: `NEXTCLOUD_TALK_BOT_SECRET` (только для учётной записи по умолчанию)
5. Перезапустите шлюз (или завершите настройку).

Минимальная конфигурация:

```json5
{
  channels: {
    "nextcloud-talk": {
      enabled: true,
      baseUrl: "https://cloud.example.com",
      botSecret: "shared-secret",
      dmPolicy: "pairing",
    },
  },
}
```

## Примечания

- Боты не могут инициировать прямые сообщения (DM). Пользователь должен первым отправить сообщение боту.
- URL webhook должен быть доступен для шлюза; установите `webhookPublicUrl`, если вы находитесь за прокси-сервером.
- Загрузка медиафайлов не поддерживается API бота; медиафайлы отправляются в виде URL.
- Полезная нагрузка webhook не различает DM и комнаты; установите `apiUser` + `apiPassword`, чтобы включить поиск по типу комнаты (в противном случае DM будут рассматриваться как комнаты).

## Контроль доступа (DM)

- По умолчанию: `channels.nextcloud-talk.dmPolicy = "pairing"`. Неизвестные отправители получают код для сопряжения.
- Одобрение через:
  - `openclaw pairing list nextcloud-talk`
  - `openclaw pairing approve nextcloud-talk <CODE>`
- Открытые DM: `channels.nextcloud-talk.dmPolicy="open"` плюс `channels.nextcloud-talk.allowFrom=["*"]`.
- `allowFrom` сопоставляется только с идентификаторами пользователей Nextcloud; отображаемые имена игнорируются.

## Комнаты (группы)

- По умолчанию: `channels.nextcloud-talk.groupPolicy = "allowlist"` (с ограничением по упоминаниям).
- Разрешите комнаты с помощью `channels.nextcloud-talk.rooms`:

```json5
{
  channels: {
    "nextcloud-talk": {
      rooms: {
        "room-token": { requireMention: true },
      },
    },
  },
}
```

- Чтобы не разрешать ни одну комнату, оставьте список разрешённых пустым или установите `channels.nextcloud-talk.groupPolicy="disabled"`.

## Возможности

| Функция | Статус |
| --------------- | ------------- |
| Прямые сообщения | Поддерживается |
| Комнаты | Поддерживается |
| Потоки (threads) | Не поддерживается |
| Медиа | Только URL |
| Реакции | Поддерживается |
| Нативные команды | Не поддерживается |

## Справочная информация по конфигурации (Nextcloud Talk)

Полная конфигурация: [Конфигурация](/gateway/configuration)

Параметры провайдера:

- `channels.nextcloud-talk.enabled`: включение/отключение запуска канала.
- `channels.nextcloud-talk.baseUrl`: URL экземпляра Nextcloud.
- `channels.nextcloud-talk.botSecret`: общий секрет бота.
- `channels.nextcloud-talk.botSecretFile`: путь к файлу с секретом. Символьные ссылки не допускаются.
- `channels.nextcloud-talk.apiUser`: пользователь API для поиска комнат (обнаружение DM).
- `channels.nextcloud-talk.apiPassword`: пароль API/приложения для поиска комнат.
- `channels.nextcloud-talk.apiPasswordFile`: путь к файлу с паролем API.
- `channels.nextcloud-talk.webhookPort`: порт слушателя webhook (по умолчанию: 8788).
- `channels.nextcloud-talk.webhookHost`: хост webhook (по умолчанию: 0.0.0.0).
- `channels.nextcloud-talk.webhookPath`: путь webhook (по умолчанию: /nextcloud-talk-webhook).
- `channels.nextcloud-talk.webhookPublicUrl`: внешний URL webhook, доступный извне.
- `channels.nextcloud-talk.dmPolicy`: `pairing | allowlist | open | disabled`.
- `channels.nextcloud-talk.allowFrom`: список разрешённых для DM (идентификаторы пользователей). Для `open` требуется `"*"`.
- `channels.nextcloud-talk.groupPolicy`: `allowlist | open | disabled`.
- `channels.nextcloud-talk.groupAllowFrom`: список разрешённых для групп (идентификаторы пользователей).
- `channels.nextcloud-talk.rooms`: настройки для каждой комнаты и список разрешённых.
- `channels.nextcloud-talk.historyLimit`: ограничение истории для групп (0 отключает).
- `channels.nextcloud-talk.dmHistoryLimit`: ограничение истории для DM (0 отключает).
- `channels.nextcloud-talk.dms`: переопределение для каждого DM (historyLimit).
- `channels.nextcloud-talk.textChunkLimit`: размер фрагмента исходящего текста (в символах).
- `channels.nextcloud-talk.chunkMode`: `length` (по умолчанию) или `newline` для разделения по пустым строкам (границы абзацев) перед разбиением по длине.
- `channels.nextcloud-talk.blockStreaming`: отключение потоковой передачи блоков для этого канала.
- `channels.nextcloud-talk.blockStreamingCoalesce`: настройка объединения потоковой передачи блоков.
- `channels.nextcloud-talk.mediaMaxMb`: ограничение на входящий медиаконтент (в МБ).

## Связанные материалы

- [Обзор каналов](/channels) — все поддерживаемые каналы
- [Сопряжение](/channels/pairing) — аутентификация DM и процесс сопряжения
- [Группы](/channels/groups) — поведение групповых чатов и ограничение по упоминаниям
- [Маршрутизация каналов](/channels/channel-routing) — маршрутизация сеансов для сообщений
- [Безопасность](/gateway/security) — модель доступа и усиление защиты