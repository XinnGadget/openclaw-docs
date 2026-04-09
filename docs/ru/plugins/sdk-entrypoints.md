---
title: "Точки входа плагинов"
sidebarTitle: "Точки входа"
summary: "Справочник по definePluginEntry, defineChannelPluginEntry и defineSetupPluginEntry"
read_when:
  - Вам нужна точная сигнатура типа definePluginEntry или defineChannelPluginEntry
  - Вы хотите разобраться в режимах регистрации (полный режим, режим настройки, метаданные CLI)
  - Вы ищете варианты настроек точек входа
---

# Точки входа плагинов

Каждый плагин экспортирует объект точки входа по умолчанию. SDK предоставляет три вспомогательных функции для их создания.

<Tip>
  **Ищете пошаговое руководство?** Ознакомьтесь с разделами [Плагины каналов](/plugins/sdk-channel-plugins) или [Плагины провайдеров](/plugins/sdk-provider-plugins).
</Tip>

## `definePluginEntry`

**Импорт:** `openclaw/plugin-sdk/plugin-entry`

Для плагинов провайдеров, инструментов, хуков и всего, что **не является** каналом обмена сообщениями.

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Short summary",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
  },
});
```

| Поле | Тип | Обязательно | Значение по умолчанию |
| -------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id` | `string` | Да | — |
| `name` | `string` | Да | — |
| `description` | `string` | Да | — |
| `kind` | `string` | Нет | — |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Нет | Пустая схема объекта |
| `register` | `(api: OpenClawPluginApi) => void` | Да | — |

- `id` должен соответствовать манифесту `openclaw.plugin.json`.
- `kind` используется для эксклюзивных слотов: `"memory"` или `"context-engine"`.
- `configSchema` может быть функцией для отложенного вычисления.
- OpenClaw разрешает и кэширует эту схему при первом обращении, поэтому ресурсоёмкие построители схем выполняются только один раз.

## `defineChannelPluginEntry`

**Импорт:** `openclaw/plugin-sdk/channel-core`

Обёртывает `definePluginEntry` с настройкой, специфичной для каналов. Автоматически вызывает `api.registerChannel({ plugin })`, предоставляет необязательный раздел метаданных CLI для корневой справки и управляет `registerFull` в зависимости от режима регистрации.

```typescript
import { defineChannelPluginEntry from "openclaw/plugin-sdk/channel-core";

export default defineChannelPluginEntry({
  id: "my-channel",
  name: "My Channel",
  description: "Short summary",
  plugin: myChannelPlugin,
  setRuntime: setMyRuntime,
  registerCliMetadata(api) {
    api.registerCli(/* ... */);
  },
  registerFull(api) {
    api.registerGatewayMethod(/* ... */);
  },
});
```

| Поле | Тип | Обязательно | Значение по умолчанию |
| --------------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id` | `string` | Да | — |
| `name` | `string` | Да | — |
| `description` | `string` | Да | — |
| `plugin` | `ChannelPlugin` | Да | — |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Нет | Пустая схема объекта |
| `setRuntime` | `(runtime: PluginRuntime) => void` | Нет | — |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void` | Нет | — |
| `registerFull` | `(api: OpenClawPluginApi) => void` | Нет | — |

- `setRuntime` вызывается во время регистрации, чтобы вы могли сохранить ссылку на среду выполнения (обычно через `createPluginRuntimeStore`). При сборе метаданных CLI этот вызов пропускается.
- `registerCliMetadata` выполняется как при `api.registrationMode === "cli-metadata"`, так и при `api.registrationMode === "full"`. Используйте его как основное место для дескрипторов CLI, принадлежащих каналу, чтобы корневая справка оставалась неактивной, а регистрация обычных команд CLI оставалась совместимой с полной загрузкой плагина.
- `registerFull` выполняется только при `api.registrationMode === "full"`. При загрузке только в режиме настройки этот вызов пропускается.
- Как и в случае с `definePluginEntry`, `configSchema` может быть отложенной фабрикой, и OpenClaw кэширует разрешённую схему при первом обращении.
- Для корневых команд CLI, принадлежащих плагину, предпочтительно использовать `api.registerCli(..., { descriptors: [...] })` — так команда будет загружаться отложенно, не исчезая из дерева разбора корневого CLI. Для плагинов каналов предпочтительно регистрировать эти дескрипторы из `registerCliMetadata(...)`, а `registerFull(...)` использовать для работы, связанной только со средой выполнения.
- Если `registerFull(...)` также регистрирует методы RPC шлюза, размещайте их с префиксом, специфичным для плагина. Зарезервированные основные административные пространства имён (`config.*`, `exec.approvals.*`, `wizard.*`, `update.*`) всегда преобразуются в `operator.admin`.

## `defineSetupPluginEntry`

**Импорт:** `openclaw/plugin-sdk/channel-core`

Для облегчённого файла `setup-entry.ts`. Возвращает только `{ plugin }` без настройки среды выполнения или CLI.

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

OpenClaw загружает этот файл вместо полной точки входа, когда канал отключён, не настроен или включена отложенная загрузка. См. раздел [Настройка и конфигурация](/plugins/sdk-setup#setup-entry), чтобы узнать, в каких случаях это имеет значение.

На практике используйте `defineSetupPluginEntry(...)` вместе с узкими семействами вспомогательных функций для настройки:

- `openclaw/plugin-sdk/setup-runtime` — вспомогательные функции для безопасной настройки среды выполнения, такие как адаптеры патчей настройки с безопасной загрузкой, вывод заметок поиска, `promptResolvedAllowFrom`, `splitSetupEntries` и делегированные прокси настройки;
- `openclaw/plugin-sdk/channel-setup` — поверхности настройки для необязательной установки;
- `openclaw/plugin-sdk/setup-tools` — вспомогательные функции для настройки/установки CLI/архива/документации.

Размещайте тяжёлые SDK, регистрацию CLI и длительные службы среды выполнения в полной точке входа.

## Режим регистрации

`api.registrationMode` сообщает плагину, как он был загружен:

| Режим | Когда | Что регистрировать |
| ----------------- | --------------------------------- | ----------------------------------------------------------------------------------------- |
| `"full"` | Обычный запуск шлюза | Всё |
| `"setup-only"` | Отключённый/ненастроенный канал | Только регистрацию канала |
| `"setup-runtime"` | Процесс настройки с доступной средой выполнения | Регистрация канала плюс только облегчённая среда выполнения, необходимая до загрузки полной точки входа |
| `"cli-metadata"` | Сбор корневой справки / метаданных CLI | Только дескрипторы CLI |

`defineChannelPluginEntry` обрабатывает это разделение автоматически. Если вы используете `definePluginEntry` напрямую для канала, проверьте режим самостоятельно:

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // Тяжёлая регистрация, связанная только со средой выполнения
  api.registerService(/* ... */);
}
```

Рассматривайте `"setup-runtime"` как окно, в котором поверхности запуска только для настройки должны существовать без повторного входа в полную среду выполнения канала. Подходят: регистрация канала, HTTP-маршруты, безопасные для настройки, методы шлюза, безопасные для настройки, и делегированные вспомогательные функции настройки. Тяжёлые фоновые службы, регистраторы CLI и начальная загрузка SDK провайдера/клиента по-прежнему относятся к режиму `"full"`.

Для регистраторов CLI в частности:

- используйте `descriptors`, когда регистратор владеет одной или несколькими корневыми командами и вы хотите, чтобы OpenClaw загружал реальный модуль CLI отложенно при первом вызове;
- убедитесь, что эти дескрипторы охватывают каждую корневую команду верхнего уровня, предоставляемую регистратором;
- используйте только `commands` только для путей с немедленной совместимостью.

## Формы плагинов
