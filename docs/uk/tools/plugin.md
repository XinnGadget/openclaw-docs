---
read_when:
    - Установлення або налаштування плагінів
    - Розуміння правил виявлення та завантаження плагінів
    - Робота з пакетами плагінів, сумісними з Codex/Claude
sidebarTitle: Install and Configure
summary: Установлення, налаштування та керування плагінами OpenClaw
title: Плагіни
x-i18n:
    generated_at: "2026-04-06T00:53:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2472a3023f3c1c6ee05b0cdc228f6b713cc226a08695b327de8a3ad6973c83
    source_path: tools/plugin.md
    workflow: 15
---

# Плагіни

Плагіни розширюють OpenClaw новими можливостями: канали, провайдери моделей,
інструменти, Skills, мовлення, транскрибування в реальному часі, голос у реальному часі,
розуміння медіа, генерація зображень, генерація відео, отримання даних із вебу, вебпошук
тощо. Деякі плагіни є **core** (постачаються з OpenClaw), інші —
**external** (публікуються спільнотою на npm).

## Швидкий старт

<Steps>
  <Step title="Перегляньте, що завантажено">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="Установіть плагін">
    ```bash
    # З npm
    openclaw plugins install @openclaw/voice-call

    # З локального каталогу або архіву
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Перезапустіть Gateway">
    ```bash
    openclaw gateway restart
    ```

    Потім налаштуйте в `plugins.entries.\<id\>.config` у вашому файлі конфігурації.

  </Step>
</Steps>

Якщо ви надаєте перевагу керуванню безпосередньо в чаті, увімкніть `commands.plugins: true` і використовуйте:

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

Шлях установлення використовує той самий механізм розв’язання, що й CLI: локальний
шлях/архів, явний `clawhub:<pkg>` або специфікація пакета без префікса
(спочатку ClawHub, потім запасний варіант npm).

Якщо конфігурація недійсна, установлення зазвичай безпечно завершується помилкою і вказує на
`openclaw doctor --fix`. Єдиний виняток для відновлення — вузький шлях
перевстановлення вбудованого плагіна для плагінів, які підтримують
`openclaw.install.allowInvalidConfigRecovery`.

## Типи плагінів

OpenClaw розпізнає два формати плагінів:

| Формат     | Як це працює                                                     | Приклади                                               |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------------ |
| **Native** | `openclaw.plugin.json` + runtime-модуль; виконується в процесі   | Офіційні плагіни, пакети npm від спільноти             |
| **Bundle** | Макет, сумісний із Codex/Claude/Cursor; відображається на можливості OpenClaw | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

Обидва відображаються в `openclaw plugins list`. Докладніше про пакети див. в [Пакети плагінів](/uk/plugins/bundles).

Якщо ви пишете native-плагін, почніть із [Створення плагінів](/uk/plugins/building-plugins)
та [Огляду Plugin SDK](/uk/plugins/sdk-overview).

## Офіційні плагіни

### Доступні для встановлення (npm)

| Плагін          | Пакет                 | Документація                        |
| --------------- | --------------------- | ----------------------------------- |
| Matrix          | `@openclaw/matrix`    | [Matrix](/uk/channels/matrix)          |
| Microsoft Teams | `@openclaw/msteams`   | [Microsoft Teams](/uk/channels/msteams) |
| Nostr           | `@openclaw/nostr`     | [Nostr](/uk/channels/nostr)            |
| Voice Call      | `@openclaw/voice-call` | [Voice Call](/uk/plugins/voice-call)   |
| Zalo            | `@openclaw/zalo`      | [Zalo](/uk/channels/zalo)              |
| Zalo Personal   | `@openclaw/zalouser`  | [Zalo Personal](/uk/plugins/zalouser)  |

### Core (постачаються з OpenClaw)

<AccordionGroup>
  <Accordion title="Провайдери моделей (увімкнені за замовчуванням)">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="Плагіни пам’яті">
    - `memory-core` — вбудований пошук у пам’яті (за замовчуванням через `plugins.slots.memory`)
    - `memory-lancedb` — довготривала пам’ять з автоматичним пригадуванням/збереженням, що встановлюється за потреби (установіть `plugins.slots.memory = "memory-lancedb"`)
  </Accordion>

  <Accordion title="Провайдери мовлення (увімкнені за замовчуванням)">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="Інше">
    - `browser` — вбудований плагін браузера для інструмента браузера, CLI `openclaw browser`, методу gateway `browser.request`, runtime браузера та стандартного сервісу керування браузером (увімкнений за замовчуванням; вимкніть його перед заміною)
    - `copilot-proxy` — міст VS Code Copilot Proxy (вимкнений за замовчуванням)
  </Accordion>
</AccordionGroup>

Шукаєте сторонні плагіни? Див. [Плагіни спільноти](/uk/plugins/community).

## Конфігурація

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| Поле             | Опис                                                      |
| ---------------- | --------------------------------------------------------- |
| `enabled`        | Головний перемикач (за замовчуванням: `true`)             |
| `allow`          | Allowlist плагінів (необов’язково)                        |
| `deny`           | Denylist плагінів (необов’язково; deny має пріоритет)     |
| `load.paths`     | Додаткові файли/каталоги плагінів                         |
| `slots`          | Вибір ексклюзивних слотів (наприклад, `memory`, `contextEngine`) |
| `entries.\<id\>` | Перемикачі та конфігурація для окремих плагінів           |

Зміни конфігурації **потребують перезапуску gateway**. Якщо Gateway запущено з
відстеженням конфігурації та внутрішньопроцесним перезапуском (типовий шлях `openclaw gateway`),
цей перезапуск зазвичай виконується автоматично невдовзі після запису конфігурації.

<Accordion title="Стани плагінів: вимкнений, відсутній, недійсний">
  - **Вимкнений**: плагін існує, але правила ввімкнення його вимкнули. Конфігурація зберігається.
  - **Відсутній**: конфігурація посилається на ідентифікатор плагіна, який не знайдено під час виявлення.
  - **Недійсний**: плагін існує, але його конфігурація не відповідає оголошеній схемі.
</Accordion>

## Виявлення та пріоритет

OpenClaw сканує плагіни в такому порядку (перше збігання перемагає):

<Steps>
  <Step title="Шляхи з конфігурації">
    `plugins.load.paths` — явні шляхи до файлів або каталогів.
  </Step>

  <Step title="Розширення робочого простору">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` і `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Глобальні розширення">
    `~/.openclaw/<plugin-root>/*.ts` і `~/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Вбудовані плагіни">
    Постачаються з OpenClaw. Багато з них увімкнені за замовчуванням (провайдери моделей, мовлення).
    Інші потрібно вмикати явно.
  </Step>
</Steps>

### Правила ввімкнення

- `plugins.enabled: false` вимикає всі плагіни
- `plugins.deny` завжди має пріоритет над allow
- `plugins.entries.\<id\>.enabled: false` вимикає цей плагін
- Плагіни з робочого простору **вимкнені за замовчуванням** (їх потрібно явно ввімкнути)
- Вбудовані плагіни дотримуються вбудованого набору, увімкненого за замовчуванням, якщо це не перевизначено
- Ексклюзивні слоти можуть примусово ввімкнути вибраний плагін для цього слота

## Слоти плагінів (ексклюзивні категорії)

Деякі категорії є ексклюзивними (одночасно активний лише один варіант):

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // або "none", щоб вимкнути
      contextEngine: "legacy", // або ідентифікатор плагіна
    },
  },
}
```

| Слот            | Що він контролює        | За замовчуванням     |
| --------------- | ----------------------- | -------------------- |
| `memory`        | Активний плагін пам’яті | `memory-core`        |
| `contextEngine` | Активний рушій контексту | `legacy` (вбудований) |

## Довідка CLI

```bash
openclaw plugins list                       # компактний перелік
openclaw plugins list --enabled            # лише завантажені плагіни
openclaw plugins list --verbose            # деталі по кожному плагіну
openclaw plugins list --json               # машиночитний перелік
openclaw plugins inspect <id>              # розгорнута інформація
openclaw plugins inspect <id> --json       # машиночитний формат
openclaw plugins inspect --all             # таблиця для всього набору
openclaw plugins info <id>                 # псевдонім inspect
openclaw plugins doctor                    # діагностика

openclaw plugins install <package>         # установлення (спочатку ClawHub, потім npm)
openclaw plugins install clawhub:<pkg>     # установлення лише з ClawHub
openclaw plugins install <spec> --force    # перезаписати наявне встановлення
openclaw plugins install <path>            # установлення з локального шляху
openclaw plugins install -l <path>         # прив’язати (без копіювання) для розробки
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # записати точну розв’язану npm-специфікацію
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # оновити один плагін
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # оновити всі
openclaw plugins uninstall <id>          # видалити записи конфігурації/встановлення
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

Вбудовані плагіни постачаються разом з OpenClaw. Багато з них увімкнені за замовчуванням (наприклад,
вбудовані провайдери моделей, вбудовані провайдери мовлення та вбудований плагін
браузера). Інші вбудовані плагіни все ще потребують `openclaw plugins enable <id>`.

`--force` перезаписує наявний встановлений плагін або набір хуків на місці.
Його не підтримано разом з `--link`, який повторно використовує вихідний шлях
замість копіювання в керовану ціль установлення.

`--pin` працює лише для npm. Його не підтримано з `--marketplace`, оскільки
установлення з marketplace зберігає метадані джерела marketplace замість npm-специфікації.

`--dangerously-force-unsafe-install` — це аварійне перевизначення для хибно
позитивних спрацювань вбудованого сканера небезпечного коду. Воно дозволяє
продовжувати встановлення та оновлення плагінів попри вбудовані результати рівня `critical`, але
все одно не обходить блокування політики плагіна `before_install` або блокування через помилки сканування.

Цей прапорець CLI застосовується лише до потоків встановлення/оновлення плагінів. Установлення залежностей Skills через gateway
замість цього використовує відповідне перевизначення запиту `dangerouslyForceUnsafeInstall`, тоді як `openclaw skills install`
залишається окремим потоком завантаження/встановлення Skills із ClawHub.

Сумісні пакети беруть участь у тому самому потоці list/inspect/enable/disable
для плагінів. Поточна підтримка runtime включає bundle Skills, command-skills Claude,
значення за замовчуванням у Claude `settings.json`, значення за замовчуванням для Claude `.lsp.json` та оголошених у маніфесті
`lspServers`, command-skills Cursor і сумісні каталоги хуків Codex.

`openclaw plugins inspect <id>` також показує виявлені можливості bundle, а також
підтримувані чи непідтримувані записи серверів MCP і LSP для плагінів на основі bundle.

Джерелами marketplace можуть бути відома назва marketplace Claude з
`~/.claude/plugins/known_marketplaces.json`, локальний корінь marketplace або шлях
`marketplace.json`, скорочений запис GitHub на кшталт `owner/repo`, URL репозиторію GitHub
або git URL. Для віддалених marketplace записи плагінів мають залишатися в межах
клонованого репозиторію marketplace і використовувати лише відносні шляхи джерел.

Детальніше див. в [`openclaw plugins` довідці CLI](/cli/plugins).

## Огляд API плагінів

Native-плагіни експортують об’єкт entry, який надає `register(api)`. Старіші
плагіни все ще можуть використовувати `activate(api)` як застарілий псевдонім, але нові плагіни повинні
використовувати `register`.

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClaw завантажує об’єкт entry і викликає `register(api)` під час
активації плагіна. Завантажувач усе ще повертається до `activate(api)` для старіших плагінів,
але вбудовані плагіни й нові зовнішні плагіни мають розглядати `register` як
публічний контракт.

Поширені методи реєстрації:

| Метод                                  | Що він реєструє               |
| -------------------------------------- | ----------------------------- |
| `registerProvider`                     | Провайдер моделей (LLM)       |
| `registerChannel`                      | Канал чату                    |
| `registerTool`                         | Інструмент агента             |
| `registerHook` / `on(...)`             | Хуки життєвого циклу          |
| `registerSpeechProvider`               | Text-to-speech / STT          |
| `registerRealtimeTranscriptionProvider` | Streaming STT                |
| `registerRealtimeVoiceProvider`        | Двобічний голос у реальному часі |
| `registerMediaUnderstandingProvider`   | Аналіз зображень/аудіо        |
| `registerImageGenerationProvider`      | Генерація зображень           |
| `registerMusicGenerationProvider`      | Генерація музики              |
| `registerVideoGenerationProvider`      | Генерація відео               |
| `registerWebFetchProvider`             | Провайдер отримання/скрейпінгу вебданих |
| `registerWebSearchProvider`            | Вебпошук                      |
| `registerHttpRoute`                    | HTTP-ендпойнт                 |
| `registerCommand` / `registerCli`      | Команди CLI                   |
| `registerContextEngine`                | Рушій контексту               |
| `registerService`                      | Фоновий сервіс                |

Поведінка guard для типізованих хуків життєвого циклу:

- `before_tool_call`: `{ block: true }` є термінальним; обробники з нижчим пріоритетом пропускаються.
- `before_tool_call`: `{ block: false }` нічого не робить і не скасовує раніше встановлений блок.
- `before_install`: `{ block: true }` є термінальним; обробники з нижчим пріоритетом пропускаються.
- `before_install`: `{ block: false }` нічого не робить і не скасовує раніше встановлений блок.
- `message_sending`: `{ cancel: true }` є термінальним; обробники з нижчим пріоритетом пропускаються.
- `message_sending`: `{ cancel: false }` нічого не робить і не скасовує раніше встановлене скасування.

Повну поведінку типізованих хуків див. в [Огляді SDK](/uk/plugins/sdk-overview#hook-decision-semantics).

## Пов’язане

- [Створення плагінів](/uk/plugins/building-plugins) — створіть власний плагін
- [Пакети плагінів](/uk/plugins/bundles) — сумісність пакетів Codex/Claude/Cursor
- [Маніфест плагіна](/uk/plugins/manifest) — схема маніфесту
- [Реєстрація інструментів](/uk/plugins/building-plugins#registering-agent-tools) — додавання інструментів агента в плагін
- [Внутрішня будова плагінів](/uk/plugins/architecture) — модель можливостей і конвеєр завантаження
- [Плагіни спільноти](/uk/plugins/community) — сторонні переліки
