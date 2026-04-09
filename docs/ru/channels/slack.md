---
summary: "Настройка Slack и поведение во время выполнения (Socket Mode + HTTP Request URLs)"
read_when:
  - Настройка Slack или отладка работы Slack в режиме socket/HTTP
title: "Slack"
---

# Slack

Статус: готов к использованию в продакшене для личных сообщений (DM) и каналов через интеграции приложения Slack. Режим по умолчанию — Socket Mode; также поддерживается использование HTTP Request URLs.

<CardGroup cols={3}>
  <Card title="Сопряжение" icon="link" href="/channels/pairing">
    В личных сообщениях Slack по умолчанию используется режим сопряжения.
  </Card>
  <Card title="Команды с косой чертой" icon="terminal" href="/tools/slash-commands">
    Поведение встроенных команд и каталог команд.
  </Card>
  <Card title="Устранение неполадок в каналах" icon="wrench" href="/channels/troubleshooting">
    Диагностика и инструкции по устранению неполадок для разных каналов.
  </Card>
</CardGroup>

## Быстрая настройка

<Tabs>
  <Tab title="Socket Mode (по умолчанию)">
    <Steps>
      <Step title="Создайте новое приложение Slack">
        В настройках приложения Slack нажмите кнопку **[Create New App](https://api.slack.com/apps/new)**:

        - выберите **from a manifest** и укажите рабочее пространство для вашего приложения;
        - вставьте [пример манифеста](#manifest-and-scope-checklist) ниже и продолжите создание;
        - сгенерируйте **App-Level Token** (`xapp-...`) с правом `connections:write`;
        - установите приложение и скопируйте показанный **Bot Token** (`xoxb-...`).
      </Step>

      <Step title="Настройте OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "socket",
      appToken: "xapp-...",
      botToken: "xoxb-...",
    },
  },
}
```

        Резервный вариант через переменные окружения (только для учётной записи по умолчанию):

```bash
SLACK_APP_TOKEN=xapp-...
SLACK_BOT_TOKEN=xoxb-...
```

      </Step>

      <Step title="Запустите шлюз">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>

  <Tab title="HTTP Request URLs">
    <Steps>
      <Step title="Создайте новое приложение Slack">
        В настройках приложения Slack нажмите кнопку **[Create New App](https://api.slack.com/apps/new)**:

        - выберите **from a manifest** и укажите рабочее пространство для вашего приложения;
        - вставьте [пример манифеста](#manifest-and-scope-checklist) и обновите URL-адреса перед созданием;
        - сохраните **Signing Secret** для проверки запросов;
        - установите приложение и скопируйте показанный **Bot Token** (`xoxb-...`).

      </Step>

      <Step title="Настройте OpenClaw">

```json5
{
  channels: {
    slack: {
      enabled: true,
      mode: "http",
      botToken: "xoxb-...",
      signingSecret: "your-signing-secret",
      webhookPath: "/slack/events",
    },
  },
}
```

        <Note>
        Используйте уникальные пути webhook для нескольких учётных записей в HTTP.

        Укажите для каждой учётной записи отдельный `webhookPath` (по умолчанию `/slack/events`), чтобы избежать конфликтов при регистрации.
        </Note>

      </Step>

      <Step title="Запустите шлюз">

```bash
openclaw gateway
```

      </Step>
    </Steps>

  </Tab>
</Tabs>

## Манифест и список областей доступа

<Tabs>
  <Tab title="Socket Mode (по умолчанию)">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Соединитель Slack для OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Отправить сообщение в OpenClaw",
        "should_escape": false
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "socket_mode_enabled": true,
    "event_subscriptions": {
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    }
  }
}
```

  </Tab>

  <Tab title="HTTP Request URLs">

```json
{
  "display_information": {
    "name": "OpenClaw",
    "description": "Соединитель Slack для OpenClaw"
  },
  "features": {
    "bot_user": {
      "display_name": "OpenClaw",
      "always_online": true
    },
    "app_home": {
      "messages_tab_enabled": true,
      "messages_tab_read_only_enabled": false
    },
    "slash_commands": [
      {
        "command": "/openclaw",
        "description": "Отправить сообщение в OpenClaw",
        "should_escape": false,
        "url": "https://gateway-host.example.com/slack/events"
      }
    ]
  },
  "oauth_config": {
    "scopes": {
      "bot": [
        "app_mentions:read",
        "assistant:write",
        "channels:history",
        "channels:read",
        "chat:write",
        "commands",
        "emoji:read",
        "files:read",
        "files:write",
        "groups:history",
        "groups:read",
        "im:history",
        "im:read",
        "im:write",
        "mpim:history",
        "mpim:read",
        "mpim:write",
        "pins:read",
        "pins:write",
        "reactions:read",
        "reactions:write",
        "users:read"
      ]
    }
  },
  "settings": {
    "event_subscriptions": {
      "request_url": "https://gateway-host.example.com/slack/events",
      "bot_events": [
        "app_mention",
        "channel_rename",
        "member_joined_channel",
        "member_left_channel",
        "message.channels",
        "message.groups",
        "message.im",
        "message.mpim",
        "pin_added",
        "pin_removed",
        "reaction_added",
        "reaction_removed"
      ]
    },
    "interactivity": {
      "is_enabled": true,
      "request_url": "https://gateway-host.example.com/slack/events",
      "message_menu_options_url": "https://gateway-host.example.com/slack/events"
    }
  }
}
```

  </Tab>
</Tabs>

<AccordionGroup>
  <Accordion title="Дополнительные области доступа для автора (операции записи)">
    Добавьте область доступа `chat:write.customize` для бота, если хотите