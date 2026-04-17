---
read_when:
    - Вам потрібен точний сигнатурний тип `definePluginEntry` або `defineChannelPluginEntry`
    - Ви хочете зрозуміти режим реєстрації (`full` проти `setup` проти метаданих CLI)
    - Ви шукаєте параметри точки входу
sidebarTitle: Entry Points
summary: Довідник для definePluginEntry, defineChannelPluginEntry та defineSetupPluginEntry
title: Точки входу Plugin
x-i18n:
    generated_at: "2026-04-15T16:36:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: aabca25bc9b8ff1b5bb4852bafe83640ffeba006ea6b6a8eff4e2c37a10f1fe4
    source_path: plugins/sdk-entrypoints.md
    workflow: 15
---

# Точки входу Plugin

Кожен plugin експортує типовий об’єкт точки входу. SDK надає три хелпери для
їх створення.

<Tip>
  **Шукаєте покрокове пояснення?** Дивіться [Channel Plugins](/uk/plugins/sdk-channel-plugins)
  або [Provider Plugins](/uk/plugins/sdk-provider-plugins) для покрокових інструкцій.
</Tip>

## `definePluginEntry`

**Імпорт:** `openclaw/plugin-sdk/plugin-entry`

Для provider plugins, tool plugins, hook plugins і всього, що **не** є
каналом обміну повідомленнями.

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

| Поле           | Тип                                                              | Обов’язково | Типово              |
| -------------- | ---------------------------------------------------------------- | ----------- | ------------------- |
| `id`           | `string`                                                         | Так         | —                   |
| `name`         | `string`                                                         | Так         | —                   |
| `description`  | `string`                                                         | Так         | —                   |
| `kind`         | `string`                                                         | Ні          | —                   |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Ні          | Порожня схема об’єкта |
| `register`     | `(api: OpenClawPluginApi) => void`                               | Так         | —                   |

- `id` має збігатися з вашим маніфестом `openclaw.plugin.json`.
- `kind` призначений для ексклюзивних слотів: `"memory"` або `"context-engine"`.
- `configSchema` може бути функцією для лінивого обчислення.
- OpenClaw розв’язує та мемоїзує цю схему під час першого доступу, тож затратні
  побудовники схем запускаються лише один раз.

## `defineChannelPluginEntry`

**Імпорт:** `openclaw/plugin-sdk/channel-core`

Обгортає `definePluginEntry` логікою, специфічною для каналу. Автоматично викликає
`api.registerChannel({ plugin })`, відкриває необов’язковий шов метаданих CLI
для кореневої довідки та керує `registerFull` залежно від режиму реєстрації.

```typescript
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";

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

| Поле                  | Тип                                                              | Обов’язково | Типово              |
| --------------------- | ---------------------------------------------------------------- | ----------- | ------------------- |
| `id`                  | `string`                                                         | Так         | —                   |
| `name`                | `string`                                                         | Так         | —                   |
| `description`         | `string`                                                         | Так         | —                   |
| `plugin`              | `ChannelPlugin`                                                  | Так         | —                   |
| `configSchema`        | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Ні          | Порожня схема об’єкта |
| `setRuntime`          | `(runtime: PluginRuntime) => void`                               | Ні          | —                   |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void`                               | Ні          | —                   |
| `registerFull`        | `(api: OpenClawPluginApi) => void`                               | Ні          | —                   |

- `setRuntime` викликається під час реєстрації, щоб ви могли зберегти посилання
  на runtime (зазвичай через `createPluginRuntimeStore`). Воно пропускається під час
  захоплення метаданих CLI.
- `registerCliMetadata` виконується і під час `api.registrationMode === "cli-metadata"`,
  і під час `api.registrationMode === "full"`.
  Використовуйте його як канонічне місце для дескрипторів CLI, що належать каналу,
  щоб коренева довідка не активувала plugin, а звичайна реєстрація команд CLI
  залишалася сумісною з повним завантаженням plugin.
- `registerFull` виконується лише коли `api.registrationMode === "full"`. Воно пропускається
  під час завантаження лише для налаштування.
- Як і в `definePluginEntry`, `configSchema` може бути лінивою фабрикою, а OpenClaw
  мемоїзує розв’язану схему під час першого доступу.
- Для кореневих команд CLI, що належать plugin, віддавайте перевагу `api.registerCli(..., { descriptors: [...] })`,
  коли хочете, щоб команда лишалася ліниво завантажуваною, але не зникала з
  дерева розбору кореневого CLI. Для channel plugins краще реєструвати ці дескриптори
  з `registerCliMetadata(...)`, а `registerFull(...)` залишати для суто runtime-роботи.
- Якщо `registerFull(...)` також реєструє методи Gateway RPC, тримайте їх у
  префіксі, специфічному для plugin. Зарезервовані простори назв адміністрування ядра (`config.*`,
  `exec.approvals.*`, `wizard.*`, `update.*`) завжди примусово переводяться до
  `operator.admin`.

## `defineSetupPluginEntry`

**Імпорт:** `openclaw/plugin-sdk/channel-core`

Для полегшеного файла `setup-entry.ts`. Повертає лише `{ plugin }` без
runtime або логіки CLI.

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

OpenClaw завантажує це замість повної точки входу, коли канал вимкнений,
не налаштований або коли ввімкнене відкладене завантаження. Дивіться
[Налаштування та конфігурація](/uk/plugins/sdk-setup#setup-entry), щоб зрозуміти,
коли це має значення.

На практиці поєднуйте `defineSetupPluginEntry(...)` із вузькими сімействами
хелперів для налаштування:

- `openclaw/plugin-sdk/setup-runtime` для безпечних для runtime хелперів налаштування, таких як
  безпечні для імпорту адаптери setup patch, виведення приміток пошуку,
  `promptResolvedAllowFrom`, `splitSetupEntries` і делеговані проксі налаштування
- `openclaw/plugin-sdk/channel-setup` для поверхонь налаштування з необов’язковим встановленням
- `openclaw/plugin-sdk/setup-tools` для хелперів CLI/архіву/документації для налаштування/встановлення

Тримайте важкі SDK, реєстрацію CLI та довгоживучі runtime-сервіси в повній
точці входу.

Вбудовані workspace channels, які розділяють поверхні налаштування та runtime,
можуть натомість використовувати `defineBundledChannelSetupEntry(...)` з
`openclaw/plugin-sdk/channel-entry-contract`. Цей контракт дозволяє точці входу
налаштування зберігати безпечні для setup експорти plugin/secrets і водночас
відкривати setter для runtime:

```typescript
import { defineBundledChannelSetupEntry } from "openclaw/plugin-sdk/channel-entry-contract";

export default defineBundledChannelSetupEntry({
  importMetaUrl: import.meta.url,
  plugin: {
    specifier: "./channel-plugin-api.js",
    exportName: "myChannelPlugin",
  },
  runtime: {
    specifier: "./runtime-api.js",
    exportName: "setMyChannelRuntime",
  },
});
```

Використовуйте цей вбудований контракт лише тоді, коли потокам налаштування
справді потрібен полегшений setter runtime до завантаження повної точки входу каналу.

## Режим реєстрації

`api.registrationMode` повідомляє вашому plugin, як саме його було завантажено:

| Режим             | Коли                              | Що реєструвати                                                                          |
| ----------------- | --------------------------------- | --------------------------------------------------------------------------------------- |
| `"full"`          | Звичайний запуск Gateway          | Усе                                                                                     |
| `"setup-only"`    | Вимкнений/неналаштований канал    | Лише реєстрацію каналу                                                                  |
| `"setup-runtime"` | Потік налаштування з доступним runtime | Реєстрацію каналу плюс лише полегшений runtime, потрібний до завантаження повної точки входу |
| `"cli-metadata"`  | Коренева довідка / захоплення метаданих CLI | Лише дескриптори CLI                                                                    |

`defineChannelPluginEntry` обробляє цей поділ автоматично. Якщо ви використовуєте
`definePluginEntry` напряму для каналу, перевіряйте режим самостійно:

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // Важкі реєстрації лише для runtime
  api.registerService(/* ... */);
}
```

Сприймайте `"setup-runtime"` як вікно, у якому поверхні запуску лише для налаштування
мають існувати без повторного входу в повний runtime вбудованого каналу. Добре
підходять реєстрація каналу, безпечні для setup HTTP-маршрути, безпечні для setup
методи Gateway і делеговані хелпери налаштування. Важкі фонові сервіси, реєстратори CLI
та ініціалізація provider/client SDK усе ще мають належати до `"full"`.

Зокрема для реєстраторів CLI:

- використовуйте `descriptors`, коли реєстратор володіє однією або кількома кореневими командами і ви
  хочете, щоб OpenClaw ліниво завантажував справжній модуль CLI під час першого виклику
- переконайтеся, що ці дескриптори охоплюють кожен корінь команди верхнього рівня, який відкриває
  реєстратор
- використовуйте лише `commands` тільки для eager-шляхів сумісності

## Форми plugin

OpenClaw класифікує завантажені plugins за їхньою поведінкою під час реєстрації:

| Форма                 | Опис                                               |
| --------------------- | -------------------------------------------------- |
| **plain-capability**  | Один тип capability (наприклад, лише provider)     |
| **hybrid-capability** | Кілька типів capability (наприклад, provider + speech) |
| **hook-only**         | Лише hooks, без capability                         |
| **non-capability**    | Tools/commands/services, але без capability        |

Використовуйте `openclaw plugins inspect <id>`, щоб побачити форму plugin.

## Пов’язані матеріали

- [Огляд SDK](/uk/plugins/sdk-overview) — API реєстрації та довідник за subpath
- [Хелпери runtime](/uk/plugins/sdk-runtime) — `api.runtime` і `createPluginRuntimeStore`
- [Налаштування та конфігурація](/uk/plugins/sdk-setup) — маніфест, точка входу налаштування, відкладене завантаження
- [Channel Plugins](/uk/plugins/sdk-channel-plugins) — побудова об’єкта `ChannelPlugin`
- [Provider Plugins](/uk/plugins/sdk-provider-plugins) — реєстрація provider та hooks
