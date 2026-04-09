---
summary: "Схемы TypeBox как единый источник истины для протокола шлюза"
read_when:
  - Обновление схем протокола или кодогенерации
title: "TypeBox"
---

# TypeBox как источник истины для протокола

Последнее обновление: 2026-01-10

TypeBox — библиотека схем, ориентированная на TypeScript. Мы используем её для определения **протокола Gateway WebSocket** (рукопожатие, запросы/ответы, события сервера). Эти схемы лежат в основе **валидации во время выполнения**, **экспорта в JSON Schema** и **генерации кода на Swift** для приложения macOS. Единый источник истины; всё остальное генерируется.

Если вам нужен контекст протокола более высокого уровня, начните с раздела [Архитектура шлюза](/concepts/architecture).

## Концептуальная модель (30 секунд)

Каждое сообщение Gateway WS представляет собой один из трёх фреймов:

- **Запрос**: `{ type: "req", id, method, params }`
- **Ответ**: `{ type: "res", id, ok, payload | error }`
- **Событие**: `{ type: "event", event, payload, seq?, stateVersion? }`

Первый фрейм **должен** быть запросом `connect`. После этого клиенты могут вызывать методы (например, `health`, `send`, `chat.send`) и подписываться на события (например, `presence`, `tick`, `agent`).

Поток подключения (минимальный):

```
Клиент                    Шлюз
  |---- req:connect -------->|
  |<---- res:hello-ok --------|
  |<---- event:tick ----------|
  |---- req:health ---------->|
  |<---- res:health ----------|
```

Распространённые методы и события:

| Категория | Примеры | Примечания |
| --- | --- | --- |
| Core | `connect`, `health`, `status` | `connect` должен быть первым |
| Messaging | `send`, `agent`, `agent.wait`, `system-event`, `logs.tail` | Для побочных эффектов требуется `idempotencyKey` |
| Chat | `chat.history`, `chat.send`, `chat.abort` | Используются в WebChat |
| Sessions | `sessions.list`, `sessions.patch`, `sessions.delete` | Администрирование сессий |
| Automation | `wake`, `cron.list`, `cron.run`, `cron.runs` | Управление пробуждением и cron |
| Nodes | `node.list`, `node.invoke`, `node.pair.*` | Gateway WS и действия узлов |
| Events | `tick`, `presence`, `agent`, `chat`, `health`, `shutdown` | Отправка сервером |

Официальный реестр **обнаружения** находится в файле `src/gateway/server-methods-list.ts` (`listGatewayMethods`, `GATEWAY_EVENTS`).

## Где находятся схемы

- Источник: `src/gateway/protocol/schema.ts`
- Валидаторы во время выполнения (AJV): `src/gateway/protocol/index.ts`
- Реестр объявленных функций/обнаружения: `src/gateway/server-methods-list.ts`
- Рукопожатие сервера и диспетчеризация методов: `src/gateway/server.impl.ts`
- Клиент узла: `src/gateway/client.ts`
- Сгенерированная JSON Schema: `dist/protocol.schema.json`
- Сгенерированные модели Swift: `apps/macos/Sources/OpenClawProtocol/GatewayModels.swift`

## Текущий пайплайн

- `pnpm protocol:gen`
  - записывает JSON Schema (draft-07) в `dist/protocol.schema.json`
- `pnpm protocol:gen:swift`
  - генерирует модели шлюза на Swift
- `pnpm protocol:check`
  - запускает оба генератора и проверяет, что вывод зафиксирован

## Как схемы используются во время выполнения

- **На стороне сервера**: каждый входящий фрейм валидируется с помощью AJV. Рукопожатие принимает только запрос `connect`, параметры которого соответствуют `ConnectParams`.
- **На стороне клиента**: JS-клиент валидирует фреймы событий и ответов перед их использованием.
- **Обнаружение функций**: шлюз отправляет консервативный список `features.methods` и `features.events` в `hello-ok` из `listGatewayMethods()` и `GATEWAY_EVENTS`.
- Этот список обнаружения не является сгенерированным дампом всех вызываемых вспомогательных функций в `coreGatewayHandlers`; некоторые вспомогательные RPC реализованы в `src/gateway/server-methods/*.ts` без включения в объявленный список функций.

## Примеры фреймов

Connect (первое сообщение):

```json
{
  "type": "req",
  "id": "c1",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "openclaw-macos",
      "displayName": "macos",
      "version": "1.0.0",
      "platform": "macos 15.1",
      "mode": "ui",
      "instanceId": "A1B2"
    }
  }
}
```

Ответ hello-ok:

```json
{
  "type": "res",
  "id": "c1",
  "ok": true,
  "payload": {
    "type": "hello-ok",
    "protocol": 3,
    "server": { "version": "dev", "connId": "ws-1" },
    "features": { "methods": ["health"], "events": ["tick"] },
    "snapshot": {
      "presence": [],
      "health": {},
      "stateVersion": { "presence": 0, "health": 0 },
      "uptimeMs": 0
    },
    "policy": { "maxPayload": 1048576, "maxBufferedBytes": 1048576, "tickIntervalMs": 30000 }
  }
}
```

Запрос и ответ:

```json
{ "type": "req", "id": "r1", "method": "health" }
```

```json
{ "type": "res", "id": "r1", "ok": true, "payload": { "ok": true } }
```

Событие:

```json
{ "type": "event", "event": "tick", "payload": { "ts": 1730000000 }, "seq": 12 }
```

## Минимальный клиент (Node.js)

Самый простой полезный поток: подключение + проверка работоспособности.

```ts
import { WebSocket } from "ws";

const ws = new WebSocket("ws://127.0.0.1:18789");

ws.on("open", () => {
  ws.send(
    JSON.stringify({
      type: "req",
      id: "c1",
      method: "connect",
      params: {
        minProtocol: 3,
        maxProtocol: 3,
        client: {
          id: "cli",
          displayName: "example",
          version: "dev",
          platform: "node",
          mode: "cli",
        },
      },
    }),
  );
});

ws.on("message", (data) => {
  const msg = JSON.parse(String(data));
  if (msg.type === "res" && msg.id === "c1" && msg.ok) {
    ws.send(JSON.stringify({ type: "req", id: "h1", method: "health" }));
  }
  if (msg.type === "res" && msg.id === "h1") {
    console.log("health:", msg.payload);
    ws.close();
  }
});
```

## Пример работы: добавление метода от начала до конца

Пример: добавить новый запрос `system.echo`, который возвращает `{ ok: true, text }`.

1. **Схема (источник истины)**

Добавить в `src/gateway/protocol/schema.ts`:

```ts
export const SystemEchoParamsSchema = Type.Object(
  { text: NonEmptyString },
  { additionalProperties: false },
);

export const SystemEchoResultSchema = Type.Object(
  { ok: Type.Boolean(), text: NonEmptyString },
  { additionalProperties: false },
);
```

Добавить оба в `ProtocolSchemas` и экспортировать типы:

```ts
  SystemEchoParams: SystemEchoParamsSchema,
  SystemEchoResult: SystemEchoResultSchema,
```

```ts
export type SystemEchoParams = Static<typeof SystemEchoParamsSchema>;
export type SystemEchoResult = Static<typeof SystemEchoResultSchema>;
```

2. **Валидация**

В `src/gateway