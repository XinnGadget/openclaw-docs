---
read_when:
    - Ви хочете зрозуміти, які функції можуть викликати платні API
    - Вам потрібно перевірити ключі, витрати та видимість використання
    - Ви пояснюєте звітування про витрати у `/status` або `/usage`
summary: Перевірте, що може витрачати кошти, які ключі використовуються та як переглядати використання
title: Використання API та витрати
x-i18n:
    generated_at: "2026-04-13T07:24:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# Використання API та витрати

У цьому документі перелічено **функції, які можуть використовувати API-ключі**, і де відображаються їхні витрати. Він зосереджений на
функціях OpenClaw, які можуть генерувати використання провайдера або платні виклики API.

## Де відображаються витрати (чат + CLI)

**Знімок витрат за сесію**

- `/status` показує поточну модель сесії, використання контексту та токени останньої відповіді.
- Якщо модель використовує **автентифікацію через API-ключ**, `/status` також показує **орієнтовну вартість** останньої відповіді.
- Якщо метадані активної сесії обмежені, `/status` може відновити
  лічильники токенів/кешу та мітку активної моделі середовища виконання з
  останнього запису про використання в транскрипті. Наявні ненульові значення
  активної сесії все одно мають пріоритет, а загальні значення з транскрипту
  розміру підказки можуть мати перевагу, якщо збережені підсумки відсутні або
  менші.

**Нижній колонтитул витрат за повідомлення**

- `/usage full` додає нижній колонтитул використання до кожної відповіді, зокрема **орієнтовну вартість** (лише для API-ключів).
- `/usage tokens` показує лише токени; потоки OAuth/токенів у стилі підписки та CLI приховують вартість у доларах.
- Примітка щодо Gemini CLI: коли CLI повертає JSON-вивід, OpenClaw зчитує використання з
  `stats`, нормалізує `stats.cached` у `cacheRead` і виводить вхідні токени
  з `stats.input_tokens - stats.cached`, коли це потрібно.

Примітка щодо Anthropic: співробітники Anthropic повідомили нам, що використання Claude CLI у стилі OpenClaw
знову дозволене, тому OpenClaw вважає повторне використання Claude CLI і використання `claude -p`
санкціонованими для цієї інтеграції, якщо Anthropic не опублікує нову політику.
Anthropic усе ще не надає оцінки вартості в доларах за повідомлення, яку OpenClaw міг би
показувати в `/usage full`.

**Вікна використання CLI (квоти провайдерів)**

- `openclaw status --usage` і `openclaw channels list` показують **вікна використання** провайдера
  (знімки квот, а не витрати за повідомлення).
- Людинозрозумілий вивід нормалізовано до `X% left` для всіх провайдерів.
- Поточні провайдери вікон використання: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi і z.ai.
- Примітка щодо MiniMax: його сирі поля `usage_percent` / `usagePercent` означають
  залишок квоти, тому OpenClaw інвертує їх перед показом. Поля на основі підрахунку
  все одно мають перевагу, якщо присутні. Якщо провайдер повертає `model_remains`,
  OpenClaw надає перевагу запису моделі чату, за потреби виводить мітку вікна з часових позначок
  і включає назву моделі до мітки плану.
- Автентифікація використання для цих вікон квот надходить із хуків, специфічних для провайдера, коли вони доступні;
  інакше OpenClaw повертається до зіставлення облікових даних OAuth/API-ключа
  з профілів автентифікації, змінних середовища або конфігурації.

Докладніше й приклади див. у [Використання токенів і витрати](/uk/reference/token-use).

## Як виявляються ключі

OpenClaw може отримувати облікові дані з:

- **Профілів автентифікації** (для кожного агента, зберігаються в `auth-profiles.json`).
- **Змінних середовища** (наприклад, `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Конфігурації** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`), які можуть експортувати ключі до середовища процесу Skill.

## Функції, які можуть витрачати кошти через ключі

### 1) Відповіді основної моделі (чат + інструменти)

Кожна відповідь або виклик інструмента використовує **поточного провайдера моделі** (OpenAI, Anthropic тощо). Це
основне джерело використання та витрат.

Сюди також входять хостингові провайдери у стилі підписки, які все одно тарифікуються поза
локальним інтерфейсом OpenClaw, наприклад **OpenAI Codex**, **Alibaba Cloud Model Studio
Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan** та
шлях входу Anthropic Claude в OpenClaw з увімкненим **Extra Usage**.

Див. [Моделі](/uk/providers/models) для конфігурації цін і [Використання токенів і витрати](/uk/reference/token-use) для відображення.

### 2) Розуміння медіа (аудіо/зображення/відео)

Вхідні медіафайли можуть бути підсумовані/транскрибовані до запуску відповіді. Для цього використовуються API моделей/провайдерів.

- Аудіо: OpenAI / Groq / Deepgram / Google / Mistral.
- Зображення: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- Відео: Google / Qwen / Moonshot.

Див. [Розуміння медіа](/uk/nodes/media-understanding).

### 3) Генерація зображень і відео

Спільні можливості генерації також можуть витрачати ключі провайдерів:

- Генерація зображень: OpenAI / Google / fal / MiniMax
- Генерація відео: Qwen

Генерація зображень може вивести типовий провайдер з автентифікацією, якщо
`agents.defaults.imageGenerationModel` не встановлено. Генерація відео наразі
вимагає явного `agents.defaults.videoGenerationModel`, наприклад
`qwen/wan2.6-t2v`.

Див. [Генерація зображень](/uk/tools/image-generation), [Qwen Cloud](/uk/providers/qwen)
та [Моделі](/uk/concepts/models).

### 4) Ембеддинги пам’яті + семантичний пошук

Семантичний пошук у пам’яті використовує **API ембеддингів**, якщо налаштовано віддалених провайдерів:

- `memorySearch.provider = "openai"` → ембеддинги OpenAI
- `memorySearch.provider = "gemini"` → ембеддинги Gemini
- `memorySearch.provider = "voyage"` → ембеддинги Voyage
- `memorySearch.provider = "mistral"` → ембеддинги Mistral
- `memorySearch.provider = "lmstudio"` → ембеддинги LM Studio (локально/самостійний хостинг)
- `memorySearch.provider = "ollama"` → ембеддинги Ollama (локально/самостійний хостинг; зазвичай без тарифікації хостингового API)
- Необов’язковий резервний перехід на віддаленого провайдера, якщо локальні ембеддинги не спрацьовують

Ви можете залишити все локально за допомогою `memorySearch.provider = "local"` (без використання API).

Див. [Пам’ять](/uk/concepts/memory).

### 5) Інструмент вебпошуку

`web_search` може спричиняти витрати на використання залежно від вашого провайдера:

- **Brave Search API**: `BRAVE_API_KEY` або `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: `EXA_API_KEY` або `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: `FIRECRAWL_API_KEY` або `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: `GEMINI_API_KEY` або `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: `XAI_API_KEY` або `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: `KIMI_API_KEY`, `MOONSHOT_API_KEY` або `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY` або `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: без ключа за замовчуванням, але потребує доступного хоста Ollama плюс `ollama signin`; також може повторно використовувати звичайну bearer-автентифікацію провайдера Ollama, якщо хост її вимагає
- **Perplexity Search API**: `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY` або `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` або `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: резервний варіант без ключа (без тарифікації API, але неофіційний і на основі HTML)
- **SearXNG**: `SEARXNG_BASE_URL` або `plugins.entries.searxng.config.webSearch.baseUrl` (без ключа/самостійний хостинг; без тарифікації хостингового API)

Застарілі шляхи провайдера `tools.web.search.*` усе ще завантажуються через тимчасовий шар сумісності, але вони більше не є рекомендованою поверхнею конфігурації.

**Безкоштовний кредит Brave Search:** Кожен план Brave включає відновлюваний
безкоштовний кредит \$5/місяць. План Search коштує \$5 за 1 000 запитів, тож цей кредит покриває
1 000 запитів/місяць без оплати. Установіть ліміт використання в панелі керування Brave,
щоб уникнути неочікуваних витрат.

Див. [Вебінструменти](/uk/tools/web).

### 5) Інструмент веботримання (Firecrawl)

`web_fetch` може викликати **Firecrawl**, якщо присутній API-ключ:

- `FIRECRAWL_API_KEY` або `plugins.entries.firecrawl.config.webFetch.apiKey`

Якщо Firecrawl не налаштовано, інструмент переходить на пряме отримання + readability (без платного API).

Див. [Вебінструменти](/uk/tools/web).

### 6) Знімки використання провайдера (status/health)

Деякі команди status викликають **кінцеві точки використання провайдера**, щоб відобразити вікна квот або стан автентифікації.
Зазвичай це виклики з малим обсягом, але вони все одно звертаються до API провайдера:

- `openclaw status --usage`
- `openclaw models status --json`

Див. [CLI моделей](/cli/models).

### 7) Підсумовування захисту Compaction

Захист Compaction може підсумовувати історію сесії за допомогою **поточної моделі**,
що викликає API провайдера під час виконання.

Див. [Керування сесією + Compaction](/uk/reference/session-management-compaction).

### 8) Сканування / перевірка моделі

`openclaw models scan` може перевіряти моделі OpenRouter і використовує `OPENROUTER_API_KEY`, коли
перевірку ввімкнено.

Див. [CLI моделей](/cli/models).

### 9) Talk (мовлення)

Режим Talk може викликати **ElevenLabs**, якщо його налаштовано:

- `ELEVENLABS_API_KEY` або `talk.providers.elevenlabs.apiKey`

Див. [Режим Talk](/uk/nodes/talk).

### 10) Skills (сторонні API)

Skills можуть зберігати `apiKey` у `skills.entries.<name>.apiKey`. Якщо Skill використовує цей ключ для зовнішніх
API, це може спричиняти витрати відповідно до провайдера цього Skill.

Див. [Skills](/uk/tools/skills).
