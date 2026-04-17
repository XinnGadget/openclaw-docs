---
read_when:
    - Ви хочете налаштувати постачальників пошуку в пам’яті або моделі ембедингів
    - Ви хочете налаштувати бекенд QMD
    - Ви хочете налаштувати гібридний пошук, MMR або часове згасання
    - Ви хочете ввімкнути мультимодальне індексування пам’яті
summary: Усі параметри конфігурації для пошуку в пам’яті, постачальників ембедингів, QMD, гібридного пошуку та мультимодальної індексації
title: Довідник із конфігурації пам’яті
x-i18n:
    generated_at: "2026-04-15T10:48:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# Довідник із конфігурації пам’яті

На цій сторінці перелічено всі параметри конфігурації для пошуку в пам’яті OpenClaw. Для концептуальних оглядів див.:

- [Огляд пам’яті](/uk/concepts/memory) -- як працює пам’ять
- [Вбудований рушій](/uk/concepts/memory-builtin) -- типовий бекенд SQLite
- [Рушій QMD](/uk/concepts/memory-qmd) -- локальний sidecar
- [Пошук у пам’яті](/uk/concepts/memory-search) -- конвеєр пошуку та налаштування
- [Active Memory](/uk/concepts/active-memory) -- увімкнення субагента пам’яті для інтерактивних сесій

Усі налаштування пошуку в пам’яті розміщені в `agents.defaults.memorySearch` у
`openclaw.json`, якщо не зазначено інше.

Якщо ви шукаєте перемикач функції **active memory** і конфігурацію субагента,
вони розміщені в `plugins.entries.active-memory`, а не в `memorySearch`.

Active memory використовує модель із двома умовами:

1. Plugin має бути ввімкнений і націлений на поточний id агента
2. запит має бути придатною інтерактивною сесією постійного чату

Див. [Active Memory](/uk/concepts/active-memory), щоб дізнатися про модель активації,
конфігурацію, якою володіє plugin, збереження транскриптів і безпечний шаблон розгортання.

---

## Вибір постачальника

| Key        | Type      | Default          | Description                                                                                                   |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | auto-detected    | ID адаптера ембедингів: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | provider default | Назва моделі ембедингів                                                                                       |
| `fallback` | `string`  | `"none"`         | ID резервного адаптера, якщо основний завершується помилкою                                                   |
| `enabled`  | `boolean` | `true`           | Увімкнути або вимкнути пошук у пам’яті                                                                        |

### Порядок автовизначення

Коли `provider` не задано, OpenClaw вибирає перший доступний:

1. `local` -- якщо налаштовано `memorySearch.local.modelPath` і файл існує.
2. `github-copilot` -- якщо можна визначити токен GitHub Copilot (змінна середовища або профіль автентифікації).
3. `openai` -- якщо можна визначити ключ OpenAI.
4. `gemini` -- якщо можна визначити ключ Gemini.
5. `voyage` -- якщо можна визначити ключ Voyage.
6. `mistral` -- якщо можна визначити ключ Mistral.
7. `bedrock` -- якщо ланцюжок облікових даних AWS SDK успішно визначається (роль екземпляра, ключі доступу, профіль, SSO, web identity або спільна конфігурація).

`ollama` підтримується, але не визначається автоматично (задайте його явно).

### Визначення API-ключа

Віддалені ембединги потребують API-ключ. Натомість Bedrock використовує типовий
ланцюжок облікових даних AWS SDK (ролі екземпляра, SSO, ключі доступу).

| Provider       | Env var                                            | Config key                        |
| -------------- | -------------------------------------------------- | --------------------------------- |
| Bedrock        | Ланцюжок облікових даних AWS                       | API-ключ не потрібен              |
| Gemini         | `GEMINI_API_KEY`                                   | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Профіль автентифікації через вхід із пристрою |
| Mistral        | `MISTRAL_API_KEY`                                  | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (заповнювач)                      | --                                |
| OpenAI         | `OPENAI_API_KEY`                                   | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                   | `models.providers.voyage.apiKey`  |

Codex OAuth покриває лише chat/completions і не задовольняє запити
ембедингів.

---

## Конфігурація віддаленої кінцевої точки

Для власних OpenAI-сумісних кінцевих точок або перевизначення типових значень постачальника:

| Key              | Type     | Description                                        |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | Власний базовий URL API                            |
| `remote.apiKey`  | `string` | Перевизначити API-ключ                             |
| `remote.headers` | `object` | Додаткові HTTP-заголовки (об’єднуються з типовими значеннями постачальника) |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Конфігурація, специфічна для Gemini

| Key                    | Type     | Default                | Description                                |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | Також підтримує `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Для Embedding 2: 768, 1536 або 3072        |

<Warning>
Зміна `model` або `outputDimensionality` запускає автоматичне повне переіндексування.
</Warning>

---

## Конфігурація ембедингів Bedrock

Bedrock використовує типовий ланцюжок облікових даних AWS SDK -- API-ключі не потрібні.
Якщо OpenClaw працює на EC2 з роллю екземпляра, у якої ввімкнено Bedrock, просто задайте
postачальника і модель:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| Key                    | Type     | Default                        | Description                     |
| ---------------------- | -------- | ------------------------------ | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Будь-який ID моделі ембедингів Bedrock |
| `outputDimensionality` | `number` | model default                  | Для Titan V2: 256, 512 або 1024 |

### Підтримувані моделі

Підтримуються такі моделі (із визначенням сімейства та типовими
розмірностями):

| Model ID                                   | Provider   | Default Dims | Configurable Dims    |
| ------------------------------------------ | ---------- | ------------ | -------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024         | 256, 512, 1024       |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536         | --                   |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536         | --                   |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024         | --                   |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024         | 256, 384, 1024, 3072 |
| `cohere.embed-english-v3`                  | Cohere     | 1024         | --                   |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024         | --                   |
| `cohere.embed-v4:0`                        | Cohere     | 1536         | 256-1536             |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512          | --                   |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024         | --                   |

Варіанти із суфіксом пропускної здатності (наприклад, `amazon.titan-embed-text-v1:2:8k`) успадковують
конфігурацію базової моделі.

### Автентифікація

Автентифікація Bedrock використовує стандартний порядок визначення облікових даних AWS SDK:

1. Змінні середовища (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Кеш токенів SSO
3. Облікові дані токена web identity
4. Спільні файли облікових даних і конфігурації
5. Облікові дані метаданих ECS або EC2

Регіон визначається з `AWS_REGION`, `AWS_DEFAULT_REGION`, `baseUrl` постачальника
`amazon-bedrock` або за замовчуванням використовується `us-east-1`.

### Дозволи IAM

Роль або користувач IAM потребує:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Для принципу найменших привілеїв обмежте `InvokeModel` конкретною моделлю:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Локальна конфігурація ембедингів

| Key                   | Type     | Default                | Description                     |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | auto-downloaded        | Шлях до файлу моделі GGUF       |
| `local.modelCacheDir` | `string` | node-llama-cpp default | Каталог кешу для завантажених моделей |

Типова модель: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, завантажується автоматично).
Потребує нативного збирання: `pnpm approve-builds`, потім `pnpm rebuild node-llama-cpp`.

---

## Конфігурація гібридного пошуку

Усе розміщується в `memorySearch.query.hybrid`:

| Key                   | Type      | Default | Description                        |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | Увімкнути гібридний пошук BM25 + vector |
| `vectorWeight`        | `number`  | `0.7`   | Вага для векторних оцінок (0-1)    |
| `textWeight`          | `number`  | `0.3`   | Вага для оцінок BM25 (0-1)         |
| `candidateMultiplier` | `number`  | `4`     | Множник розміру пулу кандидатів    |

### MMR (різноманітність)

| Key           | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Увімкнути повторне ранжування MMR    |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = максимальна різноманітність, 1 = максимальна релевантність |

### Часове згасання (свіжість)

| Key                          | Type      | Default | Description               |
| ---------------------------- | --------- | ------- | ------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Увімкнути підсилення свіжості |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | Оцінка зменшується вдвічі кожні N днів |

Для evergreen-файлів (`MEMORY.md`, файли без дати в `memory/`) згасання ніколи не застосовується.

### Повний приклад

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## Додаткові шляхи пам’яті

| Key          | Type       | Description                              |
| ------------ | ---------- | ---------------------------------------- |
| `extraPaths` | `string[]` | Додаткові каталоги або файли для індексації |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

Шляхи можуть бути абсолютними або відносними до робочого простору. Каталоги скануються
рекурсивно на наявність файлів `.md`. Обробка символьних посилань залежить від активного бекенда:
вбудований рушій ігнорує символьні посилання, тоді як QMD дотримується поведінки базового
сканера QMD.

Для пошуку транскриптів між агентами в межах агента використовуйте
`agents.list[].memorySearch.qmd.extraCollections` замість `memory.qmd.paths`.
Ці додаткові колекції мають ту саму форму `{ path, name, pattern? }`, але
об’єднуються для кожного агента і можуть зберігати явні спільні назви, коли шлях
вказує за межі поточного робочого простору.
Якщо той самий визначений шлях з’являється і в `memory.qmd.paths`, і в
`memorySearch.qmd.extraCollections`, QMD зберігає перший запис і пропускає
дублікат.

---

## Мультимодальна пам’ять (Gemini)

Індексуйте зображення та аудіо разом із Markdown за допомогою Gemini Embedding 2:

| Key                       | Type       | Default    | Description                            |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Увімкнути мультимодальне індексування   |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` або `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Максимальний розмір файлу для індексації |

Застосовується лише до файлів у `extraPaths`. Типові корені пам’яті залишаються лише для Markdown.
Потрібен `gemini-embedding-2-preview`. `fallback` має бути `"none"`.

Підтримувані формати: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(зображення); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (аудіо).

---

## Кеш ембедингів

| Key                | Type      | Default | Description                      |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | Кешувати ембединги фрагментів у SQLite |
| `cache.maxEntries` | `number`  | `50000` | Максимальна кількість кешованих ембедингів |

Запобігає повторному створенню ембедингів для незміненого тексту під час переіндексації або оновлення транскриптів.

---

## Пакетна індексація

| Key                           | Type      | Default | Description                |
| ----------------------------- | --------- | ------- | -------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | Увімкнути API пакетних ембедингів |
| `remote.batch.concurrency`    | `number`  | `2`     | Паралельні пакетні завдання |
| `remote.batch.wait`           | `boolean` | `true`  | Очікувати завершення пакета |
| `remote.batch.pollIntervalMs` | `number`  | --      | Інтервал опитування         |
| `remote.batch.timeoutMinutes` | `number`  | --      | Тайм-аут пакета             |

Доступно для `openai`, `gemini` і `voyage`. Пакетний режим OpenAI зазвичай
найшвидший і найдешевший для великих зворотних заповнень.

---

## Пошук у пам’яті сесій (експериментально)

Індексує транскрипти сесій і показує їх через `memory_search`:

| Key                           | Type       | Default      | Description                             |
| ----------------------------- | ---------- | ------------ | --------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | Увімкнути індексацію сесій              |
| `sources`                     | `string[]` | `["memory"]` | Додайте `"sessions"`, щоб включити транскрипти |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | Поріг байтів для переіндексації         |
| `sync.sessions.deltaMessages` | `number`   | `50`         | Поріг повідомлень для переіндексації    |

Індексація сесій вмикається за бажанням і виконується асинхронно. Результати можуть бути дещо
застарілими. Журнали сесій зберігаються на диску, тому вважайте доступ до файлової системи
межею довіри.

---

## Прискорення векторів SQLite (sqlite-vec)

| Key                          | Type      | Default | Description                       |
| ---------------------------- | --------- | ------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | Використовувати sqlite-vec для векторних запитів |
| `store.vector.extensionPath` | `string`  | bundled | Перевизначити шлях до sqlite-vec  |

Коли sqlite-vec недоступний, OpenClaw автоматично повертається до in-process
cosine similarity.

---

## Сховище індексу

| Key                   | Type     | Default                               | Description                                 |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Розташування індексу (підтримує токен `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                           | Токенізатор FTS5 (`unicode61` або `trigram`) |

---

## Конфігурація бекенда QMD

Щоб увімкнути, задайте `memory.backend = "qmd"`. Усі налаштування QMD розміщені в
`memory.qmd`:

| Key                      | Type      | Default  | Description                                  |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | Шлях до виконуваного файлу QMD               |
| `searchMode`             | `string`  | `search` | Команда пошуку: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | Автоматично індексувати `MEMORY.md` + `memory/**/*.md` |
| `paths[]`                | `array`   | --       | Додаткові шляхи: `{ name, path, pattern? }`  |
| `sessions.enabled`       | `boolean` | `false`  | Індексувати транскрипти сесій                |
| `sessions.retentionDays` | `number`  | --       | Зберігання транскриптів                      |
| `sessions.exportDir`     | `string`  | --       | Каталог експорту                             |

OpenClaw віддає перевагу поточним формам колекцій QMD і запитів MCP, але зберігає
працездатність старіших випусків QMD, за потреби повертаючись до застарілих прапорців
колекцій `--mask` і старіших назв інструментів MCP.

Перевизначення моделей QMD залишаються на боці QMD, а не в конфігурації OpenClaw. Якщо вам потрібно
глобально перевизначити моделі QMD, задайте змінні середовища, наприклад
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` і `QMD_GENERATE_MODEL`, у середовищі виконання
Gateway.

### Розклад оновлень

| Key                       | Type      | Default | Description                           |
| ------------------------- | --------- | ------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`    | Інтервал оновлення                    |
| `update.debounceMs`       | `number`  | `15000` | Дебаунс змін файлів                   |
| `update.onBoot`           | `boolean` | `true`  | Оновлювати під час запуску            |
| `update.waitForBootSync`  | `boolean` | `false` | Блокувати запуск до завершення оновлення |
| `update.embedInterval`    | `string`  | --      | Окремий інтервал для ембедингів       |
| `update.commandTimeoutMs` | `number`  | --      | Тайм-аут для команд QMD               |
| `update.updateTimeoutMs`  | `number`  | --      | Тайм-аут для операцій оновлення QMD   |
| `update.embedTimeoutMs`   | `number`  | --      | Тайм-аут для операцій ембедингів QMD  |

### Обмеження

| Key                       | Type     | Default | Description                |
| ------------------------- | -------- | ------- | -------------------------- |
| `limits.maxResults`       | `number` | `6`     | Максимум результатів пошуку |
| `limits.maxSnippetChars`  | `number` | --      | Обмежити довжину фрагмента  |
| `limits.maxInjectedChars` | `number` | --      | Обмежити загальну кількість вставлених символів |
| `limits.timeoutMs`        | `number` | `4000`  | Тайм-аут пошуку             |

### Область дії

Керує тим, які сесії можуть отримувати результати пошуку QMD. Та сама схема, що й у
[`session.sendPolicy`](/uk/gateway/configuration-reference#session):

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Типова конфігурація в постачанні дозволяє прямі сесії та сесії каналів, водночас
усе ще забороняючи групи.

Типове значення — лише DM. `match.keyPrefix` зіставляється з нормалізованим ключем сесії;
`match.rawKeyPrefix` зіставляється з сирим ключем, включно з `agent:<id>:`.

### Цитати

`memory.citations` застосовується до всіх бекендів:

| Value            | Behavior                                            |
| ---------------- | --------------------------------------------------- |
| `auto` (default) | Додавати нижній колонтитул `Source: <path#line>` до фрагментів |
| `on`             | Завжди додавати нижній колонтитул                   |
| `off`            | Не додавати нижній колонтитул (шлях усе одно передається агенту внутрішньо) |

### Повний приклад QMD

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming

Dreaming налаштовується в `plugins.entries.memory-core.config.dreaming`,
а не в `agents.defaults.memorySearch`.

Dreaming запускається як один запланований цикл і використовує внутрішні фази light/deep/REM як
деталь реалізації.

Щоб дізнатися про концептуальну поведінку та slash-команди, див. [Dreaming](/uk/concepts/dreaming).

### Налаштування користувача

| Key         | Type      | Default     | Description                                       |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`     | Повністю ввімкнути або вимкнути Dreaming          |
| `frequency` | `string`  | `0 3 * * *` | Необов’язкова частота Cron для повного циклу Dreaming |

### Приклад

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

Примітки:

- Dreaming записує машинний стан у `memory/.dreams/`.
- Dreaming записує зрозумілий людині наративний вивід у `DREAMS.md` (або наявний `dreams.md`).
- Політика фаз light/deep/REM і пороги є внутрішньою поведінкою, а не користувацькою конфігурацією.
