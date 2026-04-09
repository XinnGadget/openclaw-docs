---
summary: "Настройка и конфигурирование бота для чата Twitch"
read_when:
  - Настройка интеграции чата Twitch для OpenClaw
title: "Twitch"
---

# Twitch

Поддержка чата Twitch через подключение по IRC. OpenClaw подключается как пользователь Twitch (учётная запись бота), чтобы получать и отправлять сообщения в каналах.

## Встроенный плагин

Плагин Twitch включён в состав текущих версий OpenClaw, поэтому для стандартных сборок отдельная установка не требуется.

Если вы используете более старую сборку или кастомную установку, в которой нет Twitch, установите плагин вручную:

Установка через CLI (реестр npm):

```bash
openclaw plugins install @openclaw/twitch
```

Локальная установка (при работе из git-репозитория):

```bash
openclaw plugins install ./path/to/local/twitch-plugin
```

Подробности: [Плагины](/tools/plugin)

## Быстрая настройка (для начинающих)

1. Убедитесь, что плагин Twitch доступен:
   - В текущих стандартных сборках OpenClaw он уже включён.
   - В более старых или кастомных сборках его можно добавить вручную с помощью команд выше.
2. Создайте отдельную учётную запись Twitch для бота (или используйте существующую).
3. Сгенерируйте учётные данные: [Twitch Token Generator](https://twitchtokengenerator.com/):
   - Выберите **Bot Token**.
   - Убедитесь, что выбраны области доступа `chat:read` и `chat:write`.
   - Скопируйте **Client ID** и **Access Token**.
4. Узнайте свой ID пользователя Twitch: [https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/).
5. Настройте токен:
   - Через переменную окружения: `OPENCLAW_TWITCH_ACCESS_TOKEN=...` (только для учётной записи по умолчанию).
   - Или через конфигурацию: `channels.twitch.accessToken`.
   - Если заданы оба варианта, приоритет имеет конфигурация (переменная окружения используется только для учётной записи по умолчанию).
6. Запустите шлюз.

**⚠️ Важно:** Добавьте контроль доступа (`allowFrom` или `allowedRoles`), чтобы предотвратить запуск бота неавторизованными пользователями. По умолчанию `requireMention` имеет значение `true`.

Минимальная конфигурация:

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw", // Учётная запись бота в Twitch
      accessToken: "oauth:abc123...", // OAuth Access Token (или используйте переменную окружения OPENCLAW_TWITCH_ACCESS_TOKEN)
      clientId: "xyz789...", // Client ID из Token Generator
      channel: "vevisk", // Канал Twitch, в чат которого нужно подключиться (обязательно)
      allowFrom: ["123456789"], // (рекомендуется) Только ваш ID пользователя Twitch — получите его по ссылке https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/
    },
  },
}
```

## Что это такое

- Канал Twitch, принадлежащий шлюзу.
- Детерминированная маршрутизация: ответы всегда возвращаются в Twitch.
- Каждая учётная запись сопоставляется с изолированным ключом сессии `agent:<agentId>:twitch:<accountName>`.
- `username` — учётная запись бота (используется для аутентификации), `channel` — чат, в который нужно подключиться.

## Настройка (подробно)

### Генерация учётных данных

Используйте [Twitch Token Generator](https://twitchtokengenerator.com/):

- Выберите **Bot Token**.
- Убедитесь, что выбраны области доступа `chat:read` и `chat:write`.
- Скопируйте **Client ID** и **Access Token**.

Ручная регистрация приложения не требуется. Токены истекают через несколько часов.

### Настройка бота

**Переменная окружения (только для учётной записи по умолчанию):**

```bash
OPENCLAW_TWITCH_ACCESS_TOKEN=oauth:abc123...
```

**Или конфигурация:**

```json5
{
  channels: {
    twitch: {
      enabled: true,
      username: "openclaw",
      accessToken: "oauth:abc123...",
      clientId: "xyz789...",
      channel: "vevisk",
    },
  },
}
```

Если заданы и переменная окружения, и конфигурация, приоритет имеет конфигурация.

### Контроль доступа (рекомендуется)

```json5
{
  channels: {
    twitch: {
      allowFrom: ["123456789"], // (рекомендуется) Только ваш ID пользователя Twitch
    },
  },
}
```

Предпочтительно использовать `allowFrom` для жёсткого белого списка. Если вы хотите контроль доступа на основе ролей, используйте `allowedRoles`.

**Доступные роли:** `"moderator"`, `"owner"`, `"vip"`, `"subscriber"`, `"all"`.

**Почему ID пользователей?** Имена пользователей могут меняться, что позволяет имитировать другого пользователя. ID пользователей неизменны.

Узнайте свой ID пользователя Twitch: [https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/](https://www.streamweasels.com/tools/convert-twitch-username-to-user-id/) (преобразуйте имя пользователя Twitch в ID).

## Обновление токена (опционально)

Токены, полученные через [Twitch Token Generator](https://twitchtokengenerator.com/), нельзя обновить автоматически — при истечении срока действия их нужно сгенерировать заново.

Для автоматического обновления токенов создайте собственное приложение Twitch в [Twitch Developer Console](https://dev.twitch.tv/console) и добавьте в конфигурацию:

```json5
{
  channels: {
    twitch: {
      clientSecret: "your_client_secret",
      refreshToken: "your_refresh_token",
    },
  },
}
```

Бот автоматически обновляет токены до истечения срока их действия и регистрирует события обновления.

## Поддержка нескольких учётных записей

Используйте `channels.twitch.accounts` с токенами для каждой учётной записи. См. [`gateway/configuration`](/gateway/configuration) для общего шаблона.

Пример (одна учётная запись бота в двух каналах):

```json5
{
  channels: {
    twitch: {
      accounts: {
        channel1: {
          username: "openclaw",
          accessToken: "oauth:abc123...",
          clientId: "xyz789...",
          channel: "vevisk",
        },
        channel2: {
          username: "openclaw",
          accessToken: "oauth:def456...",
          clientId: "uvw012...",
          channel: "secondchannel",
        },
      },
    },
  },
}
```

**Примечание:** Для каждой учётной записи требуется свой токен (один токен на канал).

## Контроль доступа

### Ограничения на основе ролей

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowedRoles: ["moderator", "vip"],
        },
      },
    },
  },
}
```

### Белый список по ID пользователя (наиболее безопасный способ)

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowFrom: ["123456789", "987654321"],
        },
      },
    },
  },
}
```

### Доступ на основе ролей (альтернативный вариант)

`allowFrom` — это жёсткий белый список. Если он задан, разрешены только указанные ID пользователей.
Если вы хотите доступ на основе ролей, не задавайте `allowFrom` и настройте `allowedRoles`:

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          allowedRoles: ["moderator"],
        },
      },
    },
  },
}
```

### Отключение требования упоминания (@mention)

По умолчанию `requireMention` имеет значение `true`. Чтобы отключить и отвечать на все сообщения:

```json5
{
  channels: {
    twitch: {
      accounts: {
        default: {
          requireMention: false,
        },
      },
    },
  },
}
```

## Устранение неполадок

Сначала выполните диагностические команды:

```bash
openclaw doctor
openclaw channels status --probe
```

### Бот не отвечает на сообщения

**Проверьте контроль доступа:** убедитесь, что ваш ID пользователя указан в `allowFrom`, или временно удалите `allowFrom` и установите `allowedRoles: ["all"]` для тестирования.

**Проверьте, что бот находится в канале:** бот должен подключиться к каналу, указанному в `channel`.