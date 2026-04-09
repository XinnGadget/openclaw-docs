---
summary: "Протокол WebSocket шлюза: рукопожатие, фреймы, версионирование"
read_when:
  - Реализация или обновление клиентов шлюза WS
  - Отладка несоответствий протоколов или сбоев подключения
  - Перегенерация схемы/моделей протокола
title: "Протокол шлюза"
---

# Протокол шлюза (WebSocket)

Протокол Gateway WS — это **единая плоскость управления + транспорт для узлов** в OpenClaw. Все клиенты (CLI, веб-интерфейс, приложение для macOS, узлы для iOS/Android, безголовые узлы) подключаются через WebSocket и указывают свою **роль** + **область действия** во время рукопожатия.

## Транспорт

- WebSocket, текстовые фреймы с полезными нагрузками в формате JSON.
- Первый фрейм **должен** быть запросом `connect`.

## Рукопожатие (connect)

Шлюз → Клиент (задача перед подключением):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

Клиент → Шлюз:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Шлюз → Клиент:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

Когда выдаётся токен устройства, `hello-ok` также включает:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Во время доверенной передачи при начальной загрузке `hello-ok.auth` может также включать дополнительные записи ролей с ограниченной областью действия в `deviceTokens`:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Для встроенного потока начальной загрузки узла/оператора основной токен узла остаётся с `scopes: []`, а любой переданный токен оператора остаётся ограниченным списком разрешённых операторов (`operator.approvals`, `operator.read`, `operator.talk.secrets`, `operator.write`). Проверки области действия при начальной загрузке остаются с префиксом роли: записи оператора удовлетворяют только запросам оператора, а для ролей, не являющихся операторами, по-прежнему требуются области действия с их собственным префиксом роли.

### Пример для узла

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Формирование фреймов

- **Запрос**: `{type:"req", id, method, params}`
- **Ответ**: `{type:"res", id, ok, payload|error}`
- **Событие**: `{type:"event", event, payload, seq?, stateVersion?}`

Методы с побочными эффектами требуют **ключей идемпотентности** (см. схему).

## Роли и области действия

### Роли

- `operator` = клиент плоскости управления (CLI/интерфейс/автоматизация).
- `node` = хост возможностей (camera/screen/canvas/system.run).

### Области действия (оператор)

Общие области действия:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

Для `talk.config` с `includeSecrets: true` требуется `operator.talk.secrets` (или `operator.admin`).

Методы RPC шлюза, зарегистрированные плагинами, могут запрашивать собственную область действия оператора, но зарезервированные префиксы администратора ядра (`config.*`, `exec.approvals.*`, `wizard.*`, `update.*`) всегда разрешаются в `operator.admin`.

Область действия метода — это только первый уровень защиты. Некоторые команды с косой чертой, доступные через `chat.send`, применяют более строгие проверки на уровне команд. Например, постоянные команды `/config set` и `/config unset` требуют `operator.admin`.

Для `node.pair.approve` также предусмотрена дополнительная проверка области действия во время утверждения в дополнение к базовой области действия метода:

- запросы без команд: `operator.pairing`
- запросы с командами узла, не относящимися к exec: `operator.pairing` + `operator.write`
- запросы, включающие `system.run`, `system.run.prepare` или `system.which`: `operator.pairing` + `operator.admin`

### Возможности/команды/разрешения (узел)

Узлы объявляют свои возможности во время подключения:

- `caps`: категории возможностей высокого уровня.
- `commands`: список разрешённых команд для вызова.
- `permissions`: детальные переключатели (например, `screen.record`, `camera.capture`).

Шлюз рассматривает их как **заявления** и применяет списки разрешённых действий на стороне сервера.

## Присутствие

- `system-presence` возвращает записи, ключи которых соответствуют идентификатору устройства.
- Записи о присутствии включают `deviceId`, `roles` и `scopes`, поэтому интерфейсы могут отображать одну строку для каждого устройства, даже если оно подключается как **оператор** и **узел**.

## Основные семейства методов RPC

Эта страница не является автоматически сгенерированным полным списком, но публичный интерфейс WS шире, чем примеры рукопожатия/аутентификации, приведённые выше. Ниже перечислены основные семейства методов, которые предоставляет шлюз.

`hello-ok.features.methods` — это консервативный список для обнаружения, созданный на основе `src/gateway/server-methods-list.ts` плюс экспортированные методы плагинов/каналов. Рассматривайте его как средство обнаружения функций, а не как автоматически сгенерированный список всех вспомогательных функций, реализованных в `src/gateway/server-methods/*.ts`.

### Система и идентификация

- `health` возвращает кэшированный или свежеполученный снимок состояния шлюза.
- `status` возвращает сводку шлюза в стиле `/status`; конфиденциальные поля включаются только для клиентов оператора с областью действия администратора.
- `gateway.identity.get` возвращает идентификатор устройства шлюза, используемый в потоках ретрансляции и сопряжения.
- `system-presence` возвращает текущий снимок присутствия подключённых устройств оператора/узла.
- `system-event` добавляет системное событие и может обновлять/передавать контек