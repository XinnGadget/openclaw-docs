---
x-i18n:
    generated_at: "2026-04-08T04:40:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# Рефакторинг QA

Статус: базова міграція завершена.

## Мета

Перевести QA в OpenClaw з моделі з розділеними визначеннями до єдиного джерела істини:

- метадані сценаріїв
- підказки, що надсилаються моделі
- налаштування та завершення
- логіка harness
- перевірки та критерії успіху
- артефакти та підказки для звіту

Бажаний кінцевий стан — це універсальний QA harness, який завантажує потужні файли визначення сценаріїв замість того, щоб жорстко кодувати більшість поведінки в TypeScript.

## Поточний стан

Основне джерело істини тепер розташоване в `qa/scenarios/index.md` плюс по одному файлу для кожного
сценарію в `qa/scenarios/*.md`.

Реалізовано:

- `qa/scenarios/index.md`
  - канонічні метадані QA pack
  - ідентичність оператора
  - стартова місія
- `qa/scenarios/*.md`
  - один markdown-файл на сценарій
  - метадані сценарію
  - прив’язки handler
  - конфігурація виконання, специфічна для сценарію
- `extensions/qa-lab/src/scenario-catalog.ts`
  - markdown-парсер pack + валідація zod
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - рендеринг плану з markdown pack
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - створює compatibility-файли плюс `QA_SCENARIOS.md`
- `extensions/qa-lab/src/suite.ts`
  - вибирає виконувані сценарії через прив’язки handler, визначені в markdown
- QA bus protocol + UI
  - універсальні вбудовані вкладення для рендерингу image/video/audio/file

Поверхні, що залишаються розділеними:

- `extensions/qa-lab/src/suite.ts`
  - досі містить більшість виконуваної логіки кастомних handler
- `extensions/qa-lab/src/report.ts`
  - досі виводить структуру звіту з runtime-результатів

Тож розділення джерел істини вже виправлено, але виконання все ще переважно спирається на handler, а не є повністю декларативним.

## Як насправді виглядає поверхня сценаріїв

Читання поточного suite показує кілька окремих класів сценаріїв.

### Проста взаємодія

- базовий сценарій каналу
- базовий сценарій DM
- подальша взаємодія в треді
- перемикання моделі
- продовження після погодження
- реакція/редагування/видалення

### Зміна конфігурації та runtime

- вимкнення skill через patch конфігурації
- пробудження після перезапуску через застосування конфігурації
- перемикання можливостей після перезапуску конфігурації
- перевірка дрейфу inventory у runtime

### Перевірки файлової системи та репозиторію

- звіт про виявлення source/docs
- збірка Lobster Invaders
- пошук артефакта згенерованого зображення

### Оркестрація пам’яті

- відновлення з пам’яті
- memory tools у контексті каналу
- fallback при збої пам’яті
- ранжування пам’яті сесії
- ізоляція пам’яті тредів
- sweep мрій пам’яті

### Інтеграція tools і plugin

- виклик MCP plugin-tools
- видимість skill
- гаряче встановлення skill
- нативна генерація зображення
- цикл обробки зображення
- розуміння зображення з вкладення

### Багатокрокові та мультиакторні сценарії

- передача підзадачі субагенту
- fanout synthesis субагента
- потоки у стилі відновлення після перезапуску

Ці категорії важливі, бо вони визначають вимоги до DSL. Простого списку prompt + очікуваний текст недостатньо.

## Напрямок

### Єдине джерело істини

Використовувати `qa/scenarios/index.md` плюс `qa/scenarios/*.md` як авторське джерело
істини.

Pack має залишатися:

- читабельним для людини під час review
- придатним до машинного парсингу
- достатньо багатим, щоб керувати:
  - виконанням suite
  - bootstrap QA workspace
  - метаданими UI QA Lab
  - prompts для docs/discovery
  - генерацією звітів

### Бажаний формат авторства

Використовувати markdown як формат верхнього рівня зі структурованим YAML усередині.

Рекомендована форма:

- YAML frontmatter
  - id
  - title
  - surface
  - tags
  - docs refs
  - code refs
  - перевизначення model/provider
  - prerequisites
- прозові секції
  - objective
  - notes
  - debugging hints
- fenced YAML blocks
  - setup
  - steps
  - assertions
  - cleanup

Це дає:

- кращу читабельність PR, ніж гігантський JSON
- багатший контекст, ніж чистий YAML
- суворий парсинг і валідацію zod

Сирий JSON прийнятний лише як проміжна згенерована форма.

## Запропонована форма файлу сценарію

Приклад:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## Можливості runner, які має покривати DSL

З огляду на поточний suite, універсальному runner потрібне не лише виконання prompt.

### Дії середовища та налаштування

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### Дії під час ходу агента

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### Дії з конфігурацією та runtime

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### Дії з файлами та артефактами

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### Дії з пам’яттю та cron

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### Дії MCP

- `mcp.callTool`

### Перевірки

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## Змінні та посилання на артефакти

DSL має підтримувати збережені виходи та подальші посилання на них.

Приклади з поточного suite:

- створити тред, а потім повторно використати `threadId`
- створити сесію, а потім повторно використати `sessionKey`
- згенерувати зображення, а потім прикріпити файл на наступному ході
- згенерувати рядок wake marker, а потім перевірити, що він з’являється пізніше

Потрібні можливості:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- типізовані посилання для шляхів, ключів сесій, id тредів, marker, виходів tool

Без підтримки змінних harness і далі виноситиме логіку сценаріїв назад у TypeScript.

## Що має залишитися як escape hatch

Повністю чистий декларативний runner нереалістичний на фазі 1.

Деякі сценарії за своєю природою вимагають складної оркестрації:

- sweep мрій пам’яті
- пробудження після перезапуску через застосування конфігурації
- перемикання можливостей після перезапуску конфігурації
- визначення артефакта згенерованого зображення за timestamp/шляхом
- оцінювання discovery-report

Поки що для них слід використовувати явні custom handlers.

Рекомендоване правило:

- 85-90% декларативного
- явні кроки `customHandler` для складного залишку
- лише іменовані та задокументовані custom handlers
- жодного анонімного inline-коду у файлі сценарію

Це зберігає чистоту універсального engine і водночас дозволяє рухатися вперед.

## Архітектурна зміна

### Поточний стан

Markdown сценаріїв уже є джерелом істини для:

- виконання suite
- bootstrap-файлів workspace
- каталогу сценаріїв UI QA Lab
- метаданих звіту
- prompts для discovery

Згенерована сумісність:

- seeded workspace досі містить `QA_KICKOFF_TASK.md`
- seeded workspace досі містить `QA_SCENARIO_PLAN.md`
- seeded workspace тепер також містить `QA_SCENARIOS.md`

## План рефакторингу

### Фаза 1: loader і schema

Готово.

- додано `qa/scenarios/index.md`
- сценарії розділено на `qa/scenarios/*.md`
- додано парсер для іменованого markdown YAML-вмісту pack
- виконано валідацію через zod
- споживачів переключено на parsed pack
- видалено `qa/seed-scenarios.json` і `qa/QA_KICKOFF_TASK.md` на рівні репозиторію

### Фаза 2: універсальний engine

- розділити `extensions/qa-lab/src/suite.ts` на:
  - loader
  - engine
  - action registry
  - assertion registry
  - custom handlers
- зберегти наявні helper-функції як операції engine

Результат:

- engine виконує прості декларативні сценарії

Почати зі сценаріїв, які здебільшого складаються з prompt + wait + assert:

- подальша взаємодія в треді
- розуміння зображення з вкладення
- видимість і виклик skill
- базовий сценарій каналу

Результат:

- перші реальні сценарії, визначені в markdown, постачаються через універсальний engine

### Фаза 4: міграція сценаріїв середньої складності

- цикл обробки генерації зображення
- memory tools у контексті каналу
- ранжування пам’яті сесії
- передача підзадачі субагенту
- fanout synthesis субагента

Результат:

- підтверджено роботу змінних, артефактів, перевірок tool і request-log

### Фаза 5: залишити складні сценарії на custom handlers

- sweep мрій пам’яті
- пробудження після перезапуску через застосування конфігурації
- перемикання можливостей після перезапуску конфігурації
- дрейф inventory у runtime

Результат:

- той самий формат авторства, але з явними блоками custom-step там, де це потрібно

### Фаза 6: видалити hardcoded map сценаріїв

Коли покриття pack стане достатньо добрим:

- прибрати більшість специфічних для сценаріїв розгалужень TypeScript із `extensions/qa-lab/src/suite.ts`

## Підтримка Fake Slack / Rich Media

Поточний QA bus орієнтований насамперед на текст.

Відповідні файли:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Сьогодні QA bus підтримує:

- текст
- реакції
- треди

Він ще не моделює вбудовані медіавкладення.

### Потрібний транспортний контракт

Додати універсальну модель вкладень QA bus:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

Потім додати `attachments?: QaBusAttachment[]` до:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### Чому спочатку універсально

Не створюйте модель медіа лише для Slack.

Натомість:

- одна універсальна транспортна модель QA
- кілька renderer поверх неї
  - поточний чат QA Lab
  - майбутній fake Slack web
  - будь-які інші fake transport views

Це запобігає дублюванню логіки й дозволяє медіасценаріям залишатися незалежними від транспорту.

### Необхідна робота в UI

Оновити UI QA для рендерингу:

- вбудованого попереднього перегляду зображення
- вбудованого аудіоплеєра
- вбудованого відеоплеєра
- chip вкладеного файлу

Поточний UI вже може рендерити треди та реакції, тож рендеринг вкладень має нашаровуватися на ту саму модель картки повідомлення.

### Робота зі сценаріями, яку відкриває медіатранспорт

Коли вкладення проходитимуть через QA bus, ми зможемо додати багатші сценарії fake-chat:

- вбудована відповідь із зображенням у fake Slack
- розуміння аудіовкладення
- розуміння відеовкладення
- змішане впорядкування вкладень
- відповідь у треді зі збереженням медіа

## Рекомендація

Наступний блок реалізації має бути таким:

1. додати markdown loader сценаріїв + zod schema
2. згенерувати поточний каталог із markdown
3. спочатку мігрувати кілька простих сценаріїв
4. додати універсальну підтримку вкладень QA bus
5. реалізувати рендеринг вбудованого зображення в UI QA
6. потім розширити на audio та video

Це найменший шлях, який доводить обидві цілі:

- універсальний QA, визначений через markdown
- багатші fake messaging surfaces

## Відкриті питання

- чи мають файли сценаріїв дозволяти вбудовані markdown-шаблони prompt з інтерполяцією змінних
- чи мають setup/cleanup бути іменованими секціями, чи просто впорядкованими списками дій
- чи мають посилання на артефакти бути строго типізованими в schema, чи базуватися на рядках
- чи мають custom handlers жити в одному registry чи в registry для кожної surface
- чи має згенерований compatibility-файл залишатися закоміченим під час міграції
