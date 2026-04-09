---
summary: "Настройка вебхука Synology Chat и конфигурация OpenClaw"
read_when:
  - Настройка Synology Chat с OpenClaw
  - Отладка маршрутизации вебхуков Synology Chat
title: "Synology Chat"
---

# Synology Chat

Статус: плагин, включённый в комплект, канал прямых сообщений с использованием вебхуков Synology Chat.
Плагин принимает входящие сообщения от исходящих вебхуков Synology Chat и отправляет ответы через входящий вебхук Synology Chat.

## Плагин, включённый в комплект

Synology Chat поставляется как плагин, включённый в комплект текущих версий OpenClaw, поэтому для обычных упакованных сборок отдельная установка не требуется.

Если вы используете более старую сборку или пользовательскую установку, в которой отсутствует Synology Chat, установите его вручную:

Установка из локального репозитория:

```bash
openclaw plugins install ./path/to/local/synology-chat-plugin
```

Подробности: [Плагины](/tools/plugin)

## Быстрая настройка

1. Убедитесь, что плагин Synology Chat доступен:
   - В текущих упакованных версиях OpenClaw он уже включён в комплект.
   - В более старых или пользовательских установках его можно добавить вручную из исходного кода с помощью команды, приведённой выше.
   - Команда `openclaw onboard` теперь отображает Synology Chat в том же списке настройки каналов, что и `openclaw channels add`.
   - Неинтерактивная настройка: `openclaw channels add --channel synology-chat --token <token> --url <incoming-webhook-url>`.
2. В интеграциях Synology Chat:
   - Создайте входящий вебхук и скопируйте его URL.
   - Создайте исходящий вебхук с вашим секретным токеном.
3. Укажите URL исходящего вебхука для шлюза OpenClaw:
   - По умолчанию: `https://gateway-host/webhook/synology`.
   - Или ваш пользовательский `channels.synology-chat.webhookPath`.
4. Завершите настройку в OpenClaw:
   - Пошаговая настройка: `openclaw onboard`.
   - Прямая настройка: `openclaw channels add --channel synology-chat --token <token> --url <incoming-webhook-url>`.
5. Перезапустите шлюз и отправьте прямое сообщение боту Synology Chat.

Детали аутентификации вебхука:

- OpenClaw принимает токен исходящего вебхука из `body.token`, затем из `?token=...`, затем из заголовков.
- Допустимые формы заголовков:
  - `x-synology-token`
  - `x-webhook-token`
  - `x-openclaw-token`
  - `Authorization: Bearer <token>`
- Пустые или отсутствующие токены приводят к отказу в доступе.

Минимальная конфигурация:

```json5
{
  channels: {
    "synology-chat": {
      enabled: true,
      token: "synology-outgoing-token",
      incomingUrl: "https://nas.example.com/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=...",
      webhookPath: "/webhook/synology",
      dmPolicy: "allowlist",
      allowedUserIds: ["123456"],
      rateLimitPerMinute: 30,
      allowInsecureSsl: false,
    },
  },
}
```

## Переменные окружения

Для учётной записи по умолчанию можно использовать переменные окружения:

- `SYNOLOGY_CHAT_TOKEN`
- `SYNOLOGY_CHAT_INCOMING_URL`
- `SYNOLOGY_NAS_HOST`
- `SYNOLOGY_ALLOWED_USER_IDS` (через запятую)
- `SYNOLOGY_RATE_LIMIT`
- `OPENCLAW_BOT_NAME`

Значения конфигурации имеют приоритет над переменными окружения.

## Политика прямых сообщений и контроль доступа

- `dmPolicy: "allowlist"` — рекомендуемое значение по умолчанию.
- `allowedUserIds` принимает список (или строку через запятую) идентификаторов пользователей Synology.
- В режиме `allowlist` пустой список `allowedUserIds` считается неправильной конфигурацией, и маршрут вебхука не будет запущен (для разрешения всех сообщений используйте `dmPolicy: "open"`).
- `dmPolicy: "open"` разрешает сообщения от любого отправителя.
- `dmPolicy: "disabled"` блокирует прямые сообщения.
- Привязка получателя ответа по умолчанию осуществляется по стабильному числовому `user_id`. Параметр `channels.synology-chat.dangerouslyAllowNameMatching: true` — режим совместимости "на крайний случай", который повторно включает поиск по изменяемым именам пользователей/никнеймам для доставки ответов.
- Утверждения парных подключений работают с помощью:
  - `openclaw pairing list synology-chat`
  - `openclaw pairing approve synology-chat <CODE>`

## Отправка исходящих сообщений

Используйте числовые идентификаторы пользователей Synology Chat в качестве целевых.

Примеры:

```bash
openclaw message send --channel synology-chat --target 123456 --text "Hello from OpenClaw"
openclaw message send --channel synology-chat --target synology-chat:123456 --text "Hello again"
```

Отправка медиафайлов поддерживается через доставку файлов по URL.

## Несколько учётных записей

Поддерживается несколько учётных записей Synology Chat в разделе `channels.synology-chat.accounts`.
Каждая учётная запись может переопределить токен, входящий URL, путь вебхука, политику прямых сообщений и ограничения.
Сессии прямых сообщений изолированы для каждой учётной записи и пользователя, поэтому один и тот же числовой `user_id` в двух разных учётных записях Synology не будет иметь общего состояния переписки.
Присвойте каждой включённой учётной записи отдельный `webhookPath`. OpenClaw теперь отклоняет дублирующиеся точные пути и отказывается запускать именованные учётные записи, которые наследуют только общий путь вебхука в настройках с несколькими учётными записями.
Если вам намеренно нужна унаследованная совместимость для именованной учётной записи, установите `dangerouslyAllowInheritedWebhookPath: true` для этой учётной записи или для `channels.synology-chat`, но дублирующиеся точные пути по-прежнему будут отклонены с отказом в доступе. Предпочитайте явные пути для каждой учётной записи.

```json5
{
  channels: {
    "synology-chat": {
      enabled: true,
      accounts: {
        default: {
          token: "token-a",
          incomingUrl: "https://nas-a.example.com/...token=...",
        },
        alerts: {
          token: "token-b",
          incomingUrl: "https://nas-b.example.com/...token=...",
          webhookPath: "/webhook/synology-alerts",
          dmPolicy: "allowlist",
          allowedUserIds: ["987654"],
        },
      },
    },
  },
}
```

## Примечания по безопасности

- Сохраняйте токен (`token`) в секрете и меняйте его в случае утечки.
- Оставьте `allowInsecureSsl: false`, если вы явно не доверяете самоподписанному сертификату локального NAS.
- Входящие запросы вебхука проверяются по токену и ограничиваются по количеству запросов от отправителя.
- Проверка недействительных токенов использует сравнение секретов с постоянным временем и приводит к отказу в доступе.
- Для продакшена предпочтительнее использовать `dmPolicy: "allowlist"`.
- Оставьте `dangerouslyAllowNameMatching` отключённым, если вам явно не нужна доставка ответов на основе имён пользователей в устаревшем формате.
- Оставьте `dangerouslyAllowInheritedWebhookPath` отключённым, если вы явно не принимаете риск маршрутизации с общим путём в настройке с несколькими учётными записями.

## Устранение неполадок

- `Missing required fields (token, user_id, text)` ("Отсутствуют обязательные поля (token, user_id, text)"):
  - в полезной нагрузке исходящего вебхука отсутствует одно из обязательных полей;
  - если Synology отправляет токен в заголовках, убедитесь, что шлюз/прокси сохраняет эти заголовки.
- `Invalid token` ("Недействительный токен"):
  - секретный токен исходящего вебхука не соответствует `channels.synology-chat.token`;
  - запрос направлен на неправильную учётную запись/путь вебхука;
  - обратный прокси удалил заголовок токена до того, как запрос достиг OpenClaw.
- `Rate limit exceeded` ("Превышен лимит скорости"):
  - слишком много попыток с недействительными токенами от одного источника могут временно заблокировать этот источник;
  - для аутентифицированных отправителей также действует отдельное ограничение скорости отправки сообщений для каждого пользователя.
- `Allowlist is empty. Configure allowedUserIds or use dmPolicy=open.` ("Список разрешённых пуст. Настройте allowedUserIds или используйте dmPolicy=open."):
  - включена `dmPolicy="allowlist