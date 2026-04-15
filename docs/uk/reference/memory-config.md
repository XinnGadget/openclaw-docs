---
read_when:
    - Ви хочете налаштувати провайдерів пошуку в пам’яті або моделі ембедингів
    - Ви хочете налаштувати бекенд QMD
    - Ви хочете налаштувати гібридний пошук, MMR або часове згасання
    - Ви хочете ввімкнути мультимодальне індексування пам’яті
summary: Усі параметри конфігурації для пошуку в пам’яті, провайдерів ембедингів, QMD, гібридного пошуку та мультимодального індексування
title: Довідник із конфігурації пам’яті
x-i18n:
    generated_at: "2026-04-15T09:41:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: a13f6e982ee47401cc9a71bf2ee6a5305d06158b806a04703bcdcd92e340e4d5
    source_path: reference/memory-config.md
    workflow: 15
---

# Довідник із конфігурації пам’яті

На цій сторінці перелічено всі параметри конфігурації для пошуку в пам’яті OpenClaw. Для концептуальних оглядів дивіться:

- [Огляд пам’яті](/uk/concepts/memory) -- як працює пам’ять
- [Вбудований рушій](/uk/concepts/memory-builtin) -- типовий бекенд SQLite
- [Рушій QMD](/uk/concepts/memory-qmd) -- локально-орієнтований сайдкар
- [Пошук у пам’яті](/uk/concepts/memory-search) -- конвеєр пошуку та налаштування
- [Active Memory](/uk/concepts/active-memory) -- увімкнення субагента пам’яті для інтерактивних сесій

Усі налаштування пошуку в пам’яті розміщені в `agents.defaults.memorySearch` у
`openclaw.json`, якщо не вказано інше.

Якщо ви шукаєте перемикач функції **active memory** і конфігурацію субагента,
вони розміщені в `plugins.entries.active-memory`, а не в `memorySearch`.

Active memory використовує двоетапну модель:

1. plugin має бути ввімкнений і націлений на поточний ідентифікатор агента
2. запит має бути придатною інтерактивною сесією постійного чату

Дивіться [Active Memory](/uk/concepts/active-memory) щодо моделі активації,
конфігурації, якою володіє plugin, збереження транскриптів і безпечного шаблону розгортання.

---

## Вибір провайдера

| Key        | Type      | Default          | Description                                                                                                   |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | автовизначення   | Ідентифікатор адаптера ембедингів: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | типовий для провайдера | Назва моделі ембедингів                                                                                 |
| `fallback` | `string`  | `"none"`         | Ідентифікатор резервного адаптера, якщо основний не спрацює                                                   |
| `enabled`  | `boolean` | `true`           | Увімкнути або вимкнути пошук у пам’яті                                                                        |

### Порядок автовизначення

Коли `provider` не задано, OpenClaw вибирає перший доступний:

1. `local` -- якщо налаштовано `memorySearch.local.modelPath` і файл існує.
2. `github-copilot` -- якщо токен GitHub Copilot можна визначити (змінна середовища або профіль автентифікації).
3. `openai` -- якщо можна визначити ключ OpenAI.
4. `gemini` -- якщо можна визначити ключ Gemini.
5. `voyage` -- якщо можна визначити ключ Voyage.
6. `mistral` -- якщо можна визначити ключ Mistral.
7. `bedrock` -- якщо ланцюжок облікових даних AWS SDK успішно визначається (роль інстанса, ключі доступу, профіль, SSO, веб-ідентичність або спільна конфігурація).

`ollama` підтримується, але не визначається автоматично (задайте його явно).

### Визначення API-ключа

Віддалені ембединги потребують API-ключа. Натомість Bedrock використовує типовий
ланцюжок облікових даних AWS SDK (ролі інстансів, SSO, ключі доступу).

| Provider       | Env var                                            | Config key                        |
| -------------- | -------------------------------------------------- | --------------------------------- |
| Bedrock        | ланцюжок облікових даних AWS                       | API-ключ не потрібен              |
| Gemini         | `GEMINI_API_KEY`                                   | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Профіль автентифікації через вхід із пристрою |
| Mistral        | `MISTRAL_API_KEY`                                  | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (заповнювач)                      | --                                |
| OpenAI         | `OPENAI_API_KEY`                                   | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                   | `models.providers.voyage.apiKey`  |

OAuth Codex охоплює лише chat/completions і не задовольняє запити
ембедингів.

---

## Конфігурація віддаленої кінцевої точки

Для користувацьких OpenAI-сумісних кінцевих точок або перевизначення типових значень провайдера:

| Key              | Type     | Description                                        |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | Користувацька базова URL-адреса API                |
| `remote.apiKey`  | `string` | Перевизначення API-ключа                           |
| `remote.headers` | `object` | Додаткові HTTP-заголовки (об’єднуються з типовими значеннями провайдера) |

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

## Конфігурація для Gemini

| Key                    | Type     | Default                | Description                                |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | Також підтримує `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Для Embedding 2: 768, 1536 або 3072        |

<Warning>
Зміна моделі або `outputDimensionality` запускає автоматичну повну переіндексацію.
</Warning>

---

## Конфігурація ембедингів Bedrock

Bedrock використовує типовий ланцюжок облікових даних AWS SDK -- API-ключі не потрібні.
Якщо OpenClaw працює на EC2 із роллю інстанса, у якій увімкнено Bedrock, просто задайте
провайдера та модель:

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
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Будь-який ідентифікатор моделі ембедингів Bedrock |
| `outputDimensionality` | `number` | типове значення моделі         | Для Titan V2: 256, 512 або 1024 |

### Підтримувані моделі

Підтримуються такі моделі (з визначенням сімейства та типовими значеннями
розмірності):

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

Варіанти з суфіксами пропускної здатності (наприклад, `amazon.titan-embed-text-v1:2:8k`) успадковують
конфігурацію базової моделі.

### Автентифікація

Автентифікація Bedrock використовує стандартний порядок визначення облікових даних AWS SDK:

1. Змінні середовища (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Кеш токенів SSO
3. Облікові дані токена веб-ідентичності
4. Спільні файли облікових даних і конфігурації
5. Облікові дані метаданих ECS або EC2

Регіон визначається з `AWS_REGION`, `AWS_DEFAULT_REGION`, `baseUrl` провайдера
`amazon-bedrock` або типово встановлюється як `us-east-1`.

### Дозволи IAM

Роль або користувач IAM потребують:

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

## Конфігурація локальних ембедингів

| Key                   | Type     | Default                | Description                     |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | автоматично завантажується | Шлях до файлу моделі GGUF    |
| `local.modelCacheDir` | `string` | типове значення node-llama-cpp | Каталог кешу для завантажених моделей |

Типова модель: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, завантажується автоматично).
Потребує нативного збирання: `pnpm approve-builds`, потім `pnpm rebuild node-llama-cpp`.

---

## Конфігурація гібридного пошуку

Усе в `memorySearch.query.hybrid`:

| Key                   | Type      | Default | Description                        |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | Увімкнути гібридний пошук BM25 + векторний пошук |
| `vectorWeight`        | `number`  | `0.7`   | Вага для векторних оцінок (0-1)    |
| `textWeight`          | `number`  | `0.3`   | Вага для оцінок BM25 (0-1)         |
| `candidateMultiplier` | `number`  | `4`     | Множник розміру пулу кандидатів    |

### MMR (різноманітність)

| Key           | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Увімкнути повторне ранжування MMR    |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = максимальна різноманітність, 1 = максимальна релевантність |

### Часове згасання (актуальність)

| Key                          | Type      | Default | Description               |
| ---------------------------- | --------- | ------- | ------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Увімкнути підсилення за актуальністю |
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

## Додаткові шляхи до пам’яті

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

Шляхи можуть бути абсолютними або відносними до робочої області. Каталоги скануються
рекурсивно на наявність файлів `.md`. Обробка символьних посилань залежить від активного бекенда:
вбудований рушій ігнорує символьні посилання, тоді як QMD наслідує поведінку
базового сканера QMD.

Для пошуку транскриптів між агентами в межах агента використовуйте
`agents.list[].memorySearch.qmd.extraCollections` замість `memory.qmd.paths`.
Ці додаткові колекції мають ту саму форму `{ path, name, pattern? }`, але
об’єднуються для кожного агента й можуть зберігати явні спільні назви, коли шлях
вказує за межі поточної робочої області.
Якщо той самий визначений шлях з’являється і в `memory.qmd.paths`, і в
`memorySearch.qmd.extraCollections`, QMD зберігає перший запис і пропускає
дублікат.

---

## Мультимодальна пам’ять (Gemini)

Індексуйте зображення й аудіо разом із Markdown за допомогою Gemini Embedding 2:

| Key                       | Type       | Default    | Description                            |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Увімкнути мультимодальне індексування   |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` або `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Максимальний розмір файлу для індексації |

Застосовується лише до файлів у `extraPaths`. Типові корені пам’яті залишаються лише для Markdown.
Потребує `gemini-embedding-2-preview`. `fallback` має бути `"none"`.

Підтримувані формати: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(зображення); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (аудіо).

---

## Кеш ембедингів

| Key                | Type      | Default | Description                      |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | Кешувати ембединги фрагментів у SQLite |
| `cache.maxEntries` | `number`  | `50000` | Максимальна кількість кешованих ембедингів |

Запобігає повторному створенню ембедингів для незмінного тексту під час переіндексації або оновлення транскриптів.

---

## Пакетне індексування

| Key                           | Type      | Default | Description                |
| ----------------------------- | --------- | ------- | -------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | Увімкнути API пакетних ембедингів |
| `remote.batch.concurrency`    | `number`  | `2`     | Паралельні пакетні завдання |
| `remote.batch.wait`           | `boolean` | `true`  | Очікувати завершення пакета |
| `remote.batch.pollIntervalMs` | `number`  | --      | Інтервал опитування        |
| `remote.batch.timeoutMinutes` | `number`  | --      | Тайм-аут пакета            |

Доступно для `openai`, `gemini` і `voyage`. Пакетний режим OpenAI зазвичай
найшвидший і найдешевший для великих дозаповнень.

---

## Пошук у пам’яті сесій (експериментально)

Індексує транскрипти сесій і показує їх через `memory_search`:

| Key                           | Type       | Default      | Description                             |
| ----------------------------- | ---------- | ------------ | --------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | Увімкнути індексування сесій            |
| `sources`                     | `string[]` | `["memory"]` | Додайте `"sessions"`, щоб включити транскрипти |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | Поріг байтів для переіндексації         |
| `sync.sessions.deltaMessages` | `number`   | `50`         | Поріг повідомлень для переіндексації    |

Індексація сесій вмикається за бажанням і виконується асинхронно. Результати можуть бути трохи
застарілими. Журнали сесій зберігаються на диску, тому розглядайте доступ до файлової системи як межу довіри.

---

## Прискорення векторів SQLite (sqlite-vec)

| Key                          | Type      | Default | Description                       |
| ---------------------------- | --------- | ------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | Використовувати sqlite-vec для векторних запитів |
| `store.vector.extensionPath` | `string`  | вбудований | Перевизначити шлях до sqlite-vec |

Коли sqlite-vec недоступний, OpenClaw автоматично повертається до внутрішньопроцесної
косинусної подібності.

---

## Зберігання індексу

| Key                   | Type     | Default                               | Description                                 |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Розташування індексу (підтримує токен `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                           | Токенізатор FTS5 (`unicode61` або `trigram`) |

---

## Конфігурація бекенда QMD

Задайте `memory.backend = "qmd"` для ввімкнення. Усі налаштування QMD розміщені в
`memory.qmd`:

| Key                      | Type      | Default  | Description                                  |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | Шлях до виконуваного файла QMD               |
| `searchMode`             | `string`  | `search` | Команда пошуку: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | Автоматично індексувати `MEMORY.md` + `memory/**/*.md` |
| `paths[]`                | `array`   | --       | Додаткові шляхи: `{ name, path, pattern? }`  |
| `sessions.enabled`       | `boolean` | `false`  | Індексувати транскрипти сесій                |
| `sessions.retentionDays` | `number`  | --       | Термін зберігання транскриптів               |
| `sessions.exportDir`     | `string`  | --       | Каталог експорту                             |

OpenClaw надає перевагу поточним формам колекцій QMD і запитів MCP, але зберігає
сумісність зі старішими випусками QMD, за потреби повертаючись до застарілих прапорців колекцій `--mask`
і старіших назв інструментів MCP.

Перевизначення моделей QMD залишаються на боці QMD, а не в конфігурації OpenClaw. Якщо вам потрібно
глобально перевизначити моделі QMD, задайте змінні середовища, такі як
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` і `QMD_GENERATE_MODEL`, у середовищі виконання Gateway.

### Розклад оновлення

| Key                       | Type      | Default | Description                           |
| ------------------------- | --------- | ------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`    | Інтервал оновлення                    |
| `update.debounceMs`       | `number`  | `15000` | Усунення дрібезгу змін файлів         |
| `update.onBoot`           | `boolean` | `true`  | Оновлювати під час запуску            |
| `update.waitForBootSync`  | `boolean` | `false` | Блокувати запуск до завершення оновлення |
| `update.embedInterval`    | `string`  | --      | Окрема частота створення ембедингів   |
| `update.commandTimeoutMs` | `number`  | --      | Тайм-аут для команд QMD               |
| `update.updateTimeoutMs`  | `number`  | --      | Тайм-аут для операцій оновлення QMD   |
| `update.embedTimeoutMs`   | `number`  | --      | Тайм-аут для операцій ембедингів QMD  |

### Обмеження

| Key                       | Type     | Default | Description                |
| ------------------------- | -------- | ------- | -------------------------- |
| `limits.maxResults`       | `number` | `6`     | Максимальна кількість результатів пошуку |
| `limits.maxSnippetChars`  | `number` | --      | Обмеження довжини фрагмента |
| `limits.maxInjectedChars` | `number` | --      | Обмеження загальної кількості вставлених символів |
| `limits.timeoutMs`        | `number` | `4000`  | Тайм-аут пошуку            |

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

Типова конфігурація в постачанні дозволяє прямі сесії та сесії каналів, водночас і далі забороняючи
групи.

Типове значення — лише DM. `match.keyPrefix` відповідає нормалізованому ключу сесії;
`match.rawKeyPrefix` відповідає сирому ключу, включно з `agent:<id>:`.

### Цитування

`memory.citations` застосовується до всіх бекендів:

| Value            | Behavior                                            |
| ---------------- | --------------------------------------------------- |
| `auto` (типово)  | Додавати нижній колонтитул `Source: <path#line>` у фрагменти |
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

## Dreaming (експериментально)

Dreaming налаштовується в `plugins.entries.memory-core.config.dreaming`,
а не в `agents.defaults.memorySearch`.

Dreaming виконується як один запланований прохід і використовує внутрішні фази light/deep/REM як
деталь реалізації.

Для опису концептуальної поведінки та slash-команд дивіться [Dreaming](/uk/concepts/dreaming).

### Користувацькі налаштування

| Key         | Type      | Default     | Description                                       |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`     | Повністю ввімкнути або вимкнути Dreaming          |
| `frequency` | `string`  | `0 3 * * *` | Необов’язкова частота Cron для повного проходу Dreaming |

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
