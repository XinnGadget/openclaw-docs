 ---
summary: "Песочница для каждого агента + ограничения инструментов, приоритет и примеры"
title: Песочница и инструменты для мультиагентной системы
read_when: "Вам нужна песочница для каждого агента или политики разрешения/запрета инструментов для каждого агента в мультиагентном шлюзе"
status: active
---

# Конфигурация песочницы и инструментов для мультиагентной системы

Каждый агент в мультиагентной конфигурации может переопределить глобальную политику песочницы и инструментов. На этой странице описаны настройки для отдельных агентов, правила приоритета и примеры.

- **Бэкенды и режимы песочницы**: см. [Песочница](/gateway/sandboxing).
- **Отладка заблокированных инструментов**: см. [Песочница против политики инструментов против повышенного режима](/gateway/sandbox-vs-tool-policy-vs-elevated) и `openclaw sandbox explain`.
- **Повышенный режим выполнения (Elevated exec)**: см. [Повышенный режим](/tools/elevated).

Аутентификация выполняется для каждого агента: каждый агент считывает данные из собственного хранилища аутентификации `agentDir` по пути `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`.

Учётные данные **не** передаются между агентами. Никогда не используйте один и тот же `agentDir` для разных агентов. Если вы хотите поделиться учётными данными, скопируйте `auth-profiles.json` в `agentDir` другого агента.

---

## Примеры конфигурации

### Пример 1: Личный агент + ограниченный семейный агент

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Личный ассистент",
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "family",
        "name": "Семейный бот",
        "workspace": "~/.openclaw/workspace-family",
        "sandbox": {
          "mode": "all",
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch", "process", "browser"]
        }
      }
    ]
  },
  "bindings": [
    {
      "agentId": "family",
      "match": {
        "provider": "whatsapp",
        "accountId": "*",
        "peer": {
          "kind": "group",
          "id": "120363424282127706@g.us"
        }
      }
    }
  ]
}
```

**Результат:**

- агент `main`: работает на хосте, полный доступ к инструментам;
- агент `family`: работает в Docker (один контейнер на агента), доступен только инструмент `read`.

---

### Пример 2: Рабочий агент с общей песочницей

```json
{
  "agents": {
    "list": [
      {
        "id": "personal",
        "workspace": "~/.openclaw/workspace-personal",
        "sandbox": { "mode": "off" }
      },
      {
        "id": "work",
        "workspace": "~/.openclaw/workspace-work",
        "sandbox": {
          "mode": "all",
          "scope": "shared",
          "workspaceRoot": "/tmp/work-sandboxes"
        },
        "tools": {
          "allow": ["read", "write", "apply_patch", "exec"],
          "deny": ["browser", "gateway", "discord"]
        }
      }
    ]
  }
}
```

---

### Пример 2b: Глобальный профиль для кодирования + агент только для обмена сообщениями

```json
{
  "tools": { "profile": "coding" },
  "agents": {
    "list": [
      {
        "id": "support",
        "tools": { "profile": "messaging", "allow": ["slack"] }
      }
    ]
  }
}
```

**Результат:**

- агенты по умолчанию получают инструменты для кодирования;
- агент `support` предназначен только для обмена сообщениями (+ инструмент Slack).

---

### Пример 3: Разные режимы песочницы для разных агентов

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main", // Глобальное значение по умолчанию
        "scope": "session"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "sandbox": {
          "mode": "off" // Переопределение: основной агент никогда не помещается в песочницу
        }
      },
      {
        "id": "public",
        "workspace": "~/.openclaw/workspace-public",
        "sandbox": {
          "mode": "all", // Переопределение: публичный агент всегда помещается в песочницу
          "scope": "agent"
        },
        "tools": {
          "allow": ["read"],
          "deny": ["exec", "write", "edit", "apply_patch"]
        }
      }
    ]
  }
}
```

---

## Приоритет конфигурации

Если существуют и глобальные (`agents.defaults.*`), и специфичные для агента (`agents.list[].*`) настройки:

### Конфигурация песочницы

Настройки для конкретного агента переопределяют глобальные:

```
agents.list[].sandbox.mode > agents.defaults.sandbox.mode
agents.list[].sandbox.scope > agents.defaults.sandbox.scope
agents.list[].sandbox.workspaceRoot > agents.defaults.sandbox.workspaceRoot
agents.list[].sandbox.workspaceAccess > agents.defaults.sandbox.workspaceAccess
agents.list[].sandbox.docker.* > agents.defaults.sandbox.docker.*
agents.list[].sandbox.browser.* > agents.defaults.sandbox.browser.*
agents.list[].sandbox.prune.* > agents.defaults.sandbox.prune.*
```

**Примечания:**

- `agents.list[].sandbox.{docker,browser,prune}.*` переопределяет `agents.defaults.sandbox.{docker,browser,prune}.*` для этого агента (игнорируется, если область песочницы соответствует `"shared"`).

### Ограничения инструментов

Порядок фильтрации:

1. **Профиль инструментов** (`tools.profile` или `agents.list[].tools.profile`).
2. **Профиль инструментов провайдера** (`tools.byProvider[provider].profile` или `agents.list[].tools.byProvider[provider].profile`).
3. **Глобальная политика инструментов** (`tools.allow` / `tools.deny`).
4. **Политика инструментов провайдера** (`tools.byProvider[provider].allow/deny`).
5. **Политика инструментов для конкретного агента** (`agents.list[].tools.allow/deny`).
6. **Политика провайдера для агента** (`agents.list[].tools.byProvider[provider].allow/deny`).
7. **Политика инструментов песочницы** (`tools.sandbox.tools` или `agents.list[].tools.sandbox.tools`).
8. **Политика инструментов субагента** (`tools.subagents.tools`, если применимо).

Каждый уровень может дополнительно ограничивать инструменты, но не может вернуть доступ к инструментам, запрещённым на более ранних уровнях.

Если задано `agents.list[].tools.sandbox.tools`, оно заменяет `tools.sandbox.tools` для этого агента.

Если задано `agents.list[].tools.profile`, оно переопределяет `tools.profile` для этого агента.

Ключи инструментов провайдера принимают либо `provider` (например, `google-antigravity`), либо `provider/model` (например, `openai/gpt-5.4`).

Политики инструментов поддерживают сокращения `group:*`, которые расширяются до нескольких инструментов. Полный список см. в разделе [Группы инструментов](/gateway/sandbox-vs-tool-policy-vs-elevated#tool-groups-shorthands).

Переопределения повышенного режима для отдельных агентов (`agents.list[].tools.elevated`) могут дополнительно ограничивать повышенный режим выполнения для конкретных агентов. Подробнее см. в разделе [Повышенный режим](/tools/elevated).

---

## Миграция с одноагентной системы

**До (одноагентная система):**

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace",
      "sandbox": {
        "mode": "non-main"
      }
    }
  },
  "tools": {
    "sandbox": {
      "tools": {
        "allow": ["read", "write", "apply_patch", "exec"],
        "deny": []
      }
    }
  }
}
```

**После (мультиагентная система с разными профилями):**

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/.openclaw/workspace",
        "sandbox": { "mode": "off" }
      }
    ]
  }
}
```

Устаревшие настройки `agent.*` переносятся с помощью `openclaw doctor`; в дальнейшем предпочтительно использовать `agents.defaults` + `agents.list`.

---

## Примеры ограничений инструментов

### Агент только для чтения

```json
{
  "tools": {
    "allow": ["read"],
    "deny": ["exec", "write", "edit", "apply_patch", "process"]
  }
}
```

### Агент безопасного выполнения (без изменения файлов)

```json
{
  "tools": {
    "allow": ["read", "exec", "process"],
    "deny": ["write", "edit", "apply_patch", "browser", "gateway"]
  }
}
```

### Агент только для коммуникации

```json
{
  "tools": {
    "sessions": { "visibility": "tree" },
    "allow": ["sessions_list", "sessions_send", "sessions_history", "session_status"],
    "deny": ["exec", "write", "edit", "apply_patch", "read", "browser"]
  }
}
```

В этом профиле `sessions_history` по-прежнему возвращает ограниченный, очищенный обзор истории вместо полного дампа транскрипции. При извлечении данных ассистент удаляет теги размышлений, разметку `<relevant-memories>`, XML-данные вызовов инструментов в виде обычного текста (включая `<tool_call>...</tool_call>`, `<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>`), усечённые блоки вызовов инструментов, упрощённую разметку вызовов инструментов, утечки управляющих токенов ASCII/полноширинных токенов модели и некорректные XML-данные вызовов инструментов MiniMax до маскирования/усечения.

---

## Распространённая ошибка: "non-main"

`agents.defaults.sandbox.mode: "non-main"` зависит от `session.mainKey` (по умолчанию `"main"`), а не от идентификатора агента. Сессии групп/каналов всегда получают собственные ключи, поэтому они считаются не-основными и помещаются в песочницу. Если вы хотите, чтобы агент никогда не помещался в песочницу, установите `agents.list[].sandbox.mode: "off"`.

---

## Тестирование

После настройки песочницы и инструментов для мультиагентной системы:

1. **Проверьте определение агента:**

   ```exec
   openclaw agents list --bindings
   ```

2. **Убедитесь в наличии контейнеров песочницы:**

   ```exec
   docker ps --filter "name=openclaw-sbx-"
   ```

3. **Протестируйте ограничения инструментов:**
   - отправьте сообщение, требующее использования ограниченных инструментов;
   - убедитесь, что агент не может использовать запрещённые инструменты.

4. **Отслеживайте логи:**

   ```exec
   tail -f "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/logs/gateway.log" | grep -E "routing|sandbox|tools"
   ```

---

## Устранение неполадок

### Агент не помещён в песочницу, несмотря на `mode: "all"`

- проверьте, нет ли глобальной настройки `agents.defaults.sandbox.mode`, которая её переопределяет;
- конфигурация для конкретного агента имеет приоритет, поэтому установите `agents.list[].sandbox.mode: "all"`.

### Инструменты по-прежнему доступны, несмотря на список запретов

- проверьте порядок фильтрации инструментов: глобальный → агент → песочница → субагент;
- каждый уровень может только дополнительно ограничивать, но не возвращать доступ;
- проверьте логи: `[tools] filtering tools for agent:${agentId}`.

### Контейнер не изолирован для каждого агента

- установите `scope: "agent"` в конфигурации песочницы для конкретного агента;
- по умолчанию используется `"session"`, что создаёт один контейнер на сессию.

---

## См. также

- [Песочница](/gateway/sandboxing) — полная справочная информация о песочнице (режимы, области, бэкенды, образы);
- [Песочница против политики инструментов против повышенного режима](/gateway/sandbox-vs-tool-policy-vs-elevated) — отладка ситуации "почему это заблокировано?";
- [Повышенный режим](/tools/elevated);
- [Маршрутизация в мультиагентной системе](/concepts/multi-agent);
- [Конфигурация песочницы](/gateway/configuration-reference#agentsdefaultssandbox);
- [Управление сессиями](/concepts/session).