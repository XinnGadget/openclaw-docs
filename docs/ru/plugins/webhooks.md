---
summary: "Плагин Webhooks: аутентифицированный вход в TaskFlow для доверенной внешней автоматизации"
read_when:
  - Вам нужно запускать TaskFlow или управлять ими из внешней системы
  - Вы настраиваете встроенный плагин webhooks
title: "Плагин Webhooks"
---

# Webhooks (плагин)

Плагин Webhooks добавляет аутентифицированные HTTP-маршруты, которые связывают внешнюю автоматизацию с OpenClaw TaskFlow.

Используйте его, если вам нужно, чтобы доверенная система (например, Zapier, n8n, задание CI или внутренний сервис) создавала управляемые TaskFlow и управляла ими — без предварительной разработки собственного плагина.

## Где выполняется плагин

Плагин Webhooks выполняется внутри процесса Gateway.

Если ваш Gateway работает на другом компьютере, установите и настройте плагин на хосте Gateway, затем перезапустите Gateway.

## Настройка маршрутов

Задайте конфигурацию в `plugins.entries.webhooks.config`:

```json5
{
  plugins: {
    entries: {
      webhooks: {
        enabled: true,
        config: {
          routes: {
            zapier: {
              path: "/plugins/webhooks/zapier",
              sessionKey: "agent:main:main",
              secret: {
                source: "env",
                provider: "default",
                id: "OPENCLAW_WEBHOOK_SECRET",
              },
              controllerId: "webhooks/zapier",
              description: "Мост Zapier для TaskFlow",
            },
          },
        },
      },
    },
  },
}
```

Поля маршрута:

- `enabled`: необязательное, по умолчанию `true`
- `path`: необязательное, по умолчанию `/plugins/webhooks/<routeId>`
- `sessionKey`: обязательный сеанс, которому принадлежат привязанные TaskFlow
- `secret`: обязательный общий секрет или SecretRef
- `controllerId`: необязательный идентификатор контроллера для создаваемых управляемых потоков
- `description`: необязательная заметка для оператора

Поддерживаемые входные данные для `secret`:

- Простая строка
- SecretRef с `source: "env" | "file" | "exec"`

Если маршрут, использующий секрет, не может разрешить секрет при запуске, плагин пропускает этот маршрут и записывает предупреждение — вместо того, чтобы раскрывать нерабочий эндпоинт.

## Модель безопасности

Каждый маршрут считается доверенным и действует с полномочиями TaskFlow, заданными в `sessionKey`.

Это означает, что маршрут может просматривать и изменять TaskFlow, принадлежащие этому сеансу. Поэтому следует:

- Использовать надёжный уникальный секрет для каждого маршрута
- Предпочитать ссылки на секреты встроенным текстовым секретам
- Привязывать маршруты к максимально узкому сеансу, соответствующему рабочему процессу
- Открывать только тот путь webhook, который вам действительно нужен

Плагин применяет:

- Аутентификацию по общему секрету
- Ограничения размера тела запроса и времени ожидания
- Ограничение частоты запросов с фиксированным окном
- Ограничение количества одновременных запросов
- Доступ к TaskFlow, привязанный к владельцу, через `api.runtime.taskFlow.bindSession(...)`

## Формат запроса

Отправляйте запросы `POST` со следующими заголовками:

- `Content-Type: application/json`
- `Authorization: Bearer <secret>` или `x-openclaw-webhook-secret: <secret>`

Пример:

```bash
curl -X POST https://gateway.example.com/plugins/webhooks/zapier \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_SHARED_SECRET' \
  -d '{"action":"create_flow","goal":"Review inbound queue"}'
```

## Поддерживаемые действия

В настоящее время плагин принимает следующие значения `action` в формате JSON:

- `create_flow`
- `get_flow`
- `list_flows`
- `find_latest_flow`
- `resolve_flow`
- `get_task_summary`
- `set_waiting`
- `resume_flow`
- `finish_flow`
- `fail_flow`
- `request_cancel`
- `cancel_flow`
- `run_task`

### `create_flow`

Создаёт управляемый TaskFlow для сеанса, привязанного к маршруту.

Пример:

```json
{
  "action": "create_flow",
  "goal": "Review inbound queue",
  "status": "queued",
  "notifyPolicy": "done_only"
}
```

### `run_task`

Создаёт управляемую дочернюю задачу внутри существующего управляемого TaskFlow.

Допустимые среды выполнения:

- `subagent`
- `acp`

Пример:

```json
{
  "action": "run_task",
  "flowId": "flow_123",
  "runtime": "acp",
  "childSessionKey": "agent:main:acp:worker",
  "task": "Inspect the next message batch"
}
```

## Форма ответа

В случае успешного выполнения возвращаются ответы следующего вида:

```json
{
  "ok": true,
  "routeId": "zapier",
  "result": {}
}
```

В случае отклонения запроса возвращаются ответы следующего вида:

```json
{
  "ok": false,
  "routeId": "zapier",
  "code": "not_found",
  "error": "TaskFlow not found.",
  "result": {}
}
```

Плагин намеренно удаляет метаданные владельца/сеанса из ответов webhook.

## Связанные документы

- [SDK времени выполнения плагина](/plugins/sdk-runtime)
- [Обзор хуков и webhooks](/automation/hooks)
- [Webhooks в CLI](/cli/webhooks)