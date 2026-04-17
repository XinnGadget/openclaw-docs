---
read_when:
    - Вам потрібен довідник із налаштування моделей для кожного постачальника окремо
    - Вам потрібні приклади конфігурацій або команд онбордингу CLI для постачальників моделей
summary: Огляд постачальника моделей із прикладами конфігурацій і потоками CLI
title: Постачальники моделей
x-i18n:
    generated_at: "2026-04-13T07:24:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66ba688c4b4366eec07667571e835d4cfeee684896e2ffae11d601b5fa0a4b98
    source_path: concepts/model-providers.md
    workflow: 15
---

# Постачальники моделей

Ця сторінка охоплює **постачальників LLM/моделей** (а не канали чату, як-от WhatsApp/Telegram).
Правила вибору моделей дивіться в [/concepts/models](/uk/concepts/models).

## Швидкі правила

- Посилання на моделі використовують `provider/model` (приклад: `opencode/claude-opus-4-6`).
- Якщо ви задасте `agents.defaults.models`, це стане allowlist.
- Допоміжні CLI-команди: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Резервні правила середовища виконання, cooldown-проби та збереження перевизначень сесії
  задокументовані в [/concepts/model-failover](/uk/concepts/model-failover).
- `models.providers.*.models[].contextWindow` — це рідні метадані моделі;
  `models.providers.*.models[].contextTokens` — це фактичне обмеження середовища виконання.
- Plugin-и постачальників можуть впроваджувати каталоги моделей через `registerProvider({ catalog })`;
  OpenClaw об’єднує цей результат у `models.providers` перед записом
  `models.json`.
- Маніфести постачальників можуть оголошувати `providerAuthEnvVars` і
  `providerAuthAliases`, щоб загальним перевіркам автентифікації на основі env і варіантам постачальників
  не потрібно було завантажувати середовище виконання Plugin-а. Залишкова мапа env-змінних у ядрі тепер
  використовується лише для неплагінових/вбудованих постачальників і кількох випадків загального пріоритету,
  таких як онбординг Anthropic із пріоритетом API-ключа.
- Plugin-и постачальників також можуть володіти поведінкою середовища виконання постачальника через
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, і
  `onModelSelected`.
- Примітка: `capabilities` середовища виконання постачальника — це спільні метадані раннера (сімейство постачальника,
  особливості транскриптів/інструментів, підказки щодо транспорту/кешу). Це не те саме, що
  [публічна модель можливостей](/uk/plugins/architecture#public-capability-model),
  яка описує, що реєструє Plugin (текстовий inference, мовлення тощо).
- Вбудований постачальник `codex` поєднаний із вбудованим агентним harness Codex.
  Використовуйте `codex/gpt-*`, коли вам потрібні логін під керуванням Codex, виявлення моделей, нативне
  відновлення thread-ів і виконання app-server. Звичайні посилання `openai/gpt-*` і надалі
  використовують постачальника OpenAI та звичайний транспорт постачальника OpenClaw.
  Розгортання лише з Codex можуть вимкнути автоматичний резервний перехід на PI через
  `agents.defaults.embeddedHarness.fallback: "none"`; див.
  [Codex Harness](/uk/plugins/codex-harness).

## Поведінка постачальника, якою володіє Plugin

Тепер Plugin-и постачальників можуть володіти більшістю логіки, специфічної для постачальника, тоді як OpenClaw зберігає
загальний цикл inference.

Типовий поділ:

- `auth[].run` / `auth[].runNonInteractive`: постачальник володіє потоками онбордингу/логіну
  для `openclaw onboard`, `openclaw models auth` і headless-налаштування
- `wizard.setup` / `wizard.modelPicker`: постачальник володіє мітками вибору автентифікації,
  застарілими псевдонімами, підказками allowlist для онбордингу та записами налаштування в засобах вибору онбордингу/моделей
- `catalog`: постачальник з’являється в `models.providers`
- `normalizeModelId`: постачальник нормалізує застарілі/preview-ідентифікатори моделей перед
  пошуком або канонізацією
- `normalizeTransport`: постачальник нормалізує `api` / `baseUrl` сімейства транспорту
  перед загальним збиранням моделі; OpenClaw спочатку перевіряє відповідного постачальника,
  потім інші Plugin-и постачальників, що підтримують hooks, доки один із них справді не змінить
  транспорт
- `normalizeConfig`: постачальник нормалізує конфігурацію `models.providers.<id>` перед
  використанням у середовищі виконання; OpenClaw спочатку перевіряє відповідного постачальника, потім інші
  Plugin-и постачальників, що підтримують hooks, доки один із них справді не змінить конфігурацію. Якщо жоден
  hook постачальника не переписує конфігурацію, вбудовані допоміжні засоби сімейства Google все одно
  нормалізують підтримувані записи постачальників Google.
- `applyNativeStreamingUsageCompat`: постачальник застосовує переписування сумісності native streaming-usage на основі endpoint-ів для конфігурованих постачальників
- `resolveConfigApiKey`: постачальник розв’язує автентифікацію через env-маркер для конфігурованих постачальників
  без примусового повного завантаження runtime-auth. `amazon-bedrock` тут також має
  вбудований розв’язувач env-маркерів AWS, хоча runtime-auth Bedrock використовує
  типовий ланцюжок AWS SDK.
- `resolveSyntheticAuth`: постачальник може надавати доступність локальної/self-hosted або іншої
  автентифікації на основі конфігурації без збереження plaintext-секретів
- `shouldDeferSyntheticProfileAuth`: постачальник може позначати збережені заповнювачі синтетичного профілю
  як нижчі за пріоритетом, ніж автентифікація на основі env/конфігурації
- `resolveDynamicModel`: постачальник приймає ідентифікатори моделей, яких ще немає в локальному
  статичному каталозі
- `prepareDynamicModel`: постачальнику потрібно оновити метадані перед повторною спробою
  динамічного розв’язання
- `normalizeResolvedModel`: постачальнику потрібні переписування транспорту або base URL
- `contributeResolvedModelCompat`: постачальник додає прапори сумісності для своїх
  моделей постачальника, навіть коли вони надходять через інший сумісний транспорт
- `capabilities`: постачальник публікує особливості транскриптів/інструментів/сімейства постачальника
- `normalizeToolSchemas`: постачальник очищає схеми інструментів перед тим, як їх побачить вбудований
  раннер
- `inspectToolSchemas`: постачальник показує попередження про схеми, специфічні для транспорту,
  після нормалізації
- `resolveReasoningOutputMode`: постачальник обирає нативні чи теговані
  контракти виводу reasoning
- `prepareExtraParams`: постачальник задає типові значення або нормалізує параметри запиту для кожної моделі
- `createStreamFn`: постачальник замінює звичайний шлях stream повністю
  користувацьким транспортом
- `wrapStreamFn`: постачальник застосовує обгортки сумісності заголовків/тіла запиту/моделі
- `resolveTransportTurnState`: постачальник надає нативні заголовки або метадані
  транспорту для кожного ходу
- `resolveWebSocketSessionPolicy`: постачальник надає нативні заголовки сесії WebSocket
  або політику cooldown сесії
- `createEmbeddingProvider`: постачальник володіє поведінкою memory embedding, коли вона
  має належати Plugin-у постачальника, а не вбудованому switchboard embedding-ів
- `formatApiKey`: постачальник форматує збережені профілі автентифікації у runtime-рядок
  `apiKey`, який очікує транспорт
- `refreshOAuth`: постачальник володіє оновленням OAuth, коли спільних засобів оновлення `pi-ai`
  недостатньо
- `buildAuthDoctorHint`: постачальник додає рекомендації з виправлення, коли оновлення OAuth
  завершується невдачею
- `matchesContextOverflowError`: постачальник розпізнає специфічні для постачальника
  помилки переповнення context window, які загальні евристики пропустили б
- `classifyFailoverReason`: постачальник зіставляє сирі помилки транспорту/API, специфічні для постачальника,
  із причинами failover, такими як rate limit або overload
- `isCacheTtlEligible`: постачальник визначає, які upstream-ідентифікатори моделей підтримують TTL кешу підказок
- `buildMissingAuthMessage`: постачальник замінює загальну помилку auth-store
  на підказку відновлення, специфічну для постачальника
- `suppressBuiltInModel`: постачальник приховує застарілі upstream-рядки та може повертати
  помилку від постачальника для прямих збоїв розв’язання
- `augmentModelCatalog`: постачальник додає синтетичні/підсумкові рядки каталогу після
  виявлення та об’єднання конфігурації
- `isBinaryThinking`: постачальник володіє UX двійкового thinking увімкнено/вимкнено
- `supportsXHighThinking`: постачальник вмикає `xhigh` для вибраних моделей
- `resolveDefaultThinkingLevel`: постачальник володіє типовою політикою `/think` для
  сімейства моделей
- `applyConfigDefaults`: постачальник застосовує глобальні типові значення, специфічні для постачальника,
  під час матеріалізації конфігурації на основі режиму автентифікації, env або сімейства моделей
- `isModernModelRef`: постачальник володіє зіставленням бажаних моделей для live/smoke
- `prepareRuntimeAuth`: постачальник перетворює налаштовані облікові дані на короткоживучий
  runtime-токен
- `resolveUsageAuth`: постачальник розв’язує облікові дані використання/квот для `/usage`
  та пов’язаних поверхонь статусу/звітності
- `fetchUsageSnapshot`: постачальник володіє отриманням/розбором endpoint-а використання, тоді як
  ядро й далі володіє оболонкою підсумку та форматуванням
- `onModelSelected`: постачальник виконує побічні ефекти після вибору моделі, такі як
  телеметрія або bookkeeping сесії, що належить постачальнику

Поточні вбудовані приклади:

- `anthropic`: forward-compat резервний перехід для Claude 4.6, підказки з відновлення автентифікації, отримання
  endpoint-ів використання, метадані cache-TTL/сімейства постачальника та глобальні
  типові значення конфігурації з урахуванням автентифікації
- `amazon-bedrock`: зіставлення переповнення context window, яким володіє постачальник, і класифікація
  причин failover для специфічних помилок Bedrock на кшталт throttle/not-ready, а також
  спільне сімейство відтворення `anthropic-by-model` для захистів політики відтворення лише для Claude на трафіку Anthropic
- `anthropic-vertex`: захисти політики відтворення лише для Claude на трафіку повідомлень Anthropic
- `openrouter`: наскрізні ідентифікатори моделей, обгортки запитів, підказки щодо можливостей постачальника,
  санація підпису thought Gemini на проксійованому трафіку Gemini, ін’єкція reasoning проксі
  через сімейство stream `openrouter-thinking`, пересилання метаданих маршрутизації та політика cache-TTL
- `github-copilot`: онбординг/логін пристрою, forward-compat резервний перехід для моделей,
  підказки транскрипту Claude-thinking, обмін runtime-токенів та отримання endpoint-ів використання
- `openai`: forward-compat резервний перехід для GPT-5.4, пряма нормалізація транспорту OpenAI,
  підказки щодо відсутньої автентифікації з урахуванням Codex, придушення Spark, синтетичні
  рядки каталогу OpenAI/Codex, політика thinking/live-model, нормалізація псевдонімів токенів використання
  (`input` / `output` і сімейства `prompt` / `completion`), спільне
  сімейство stream `openai-responses-defaults` для нативних обгорток OpenAI/Codex,
  метадані сімейства постачальника, реєстрація вбудованого постачальника генерації зображень
  для `gpt-image-1` і реєстрація вбудованого постачальника генерації відео
  для `sora-2`
- `google` і `google-gemini-cli`: forward-compat резервний перехід для Gemini 3.1,
  нативна перевірка відтворення Gemini, bootstrap-санація відтворення, тегований
  режим виводу reasoning, зіставлення сучасних моделей, реєстрація вбудованого постачальника генерації зображень
  для моделей Gemini image-preview і реєстрація вбудованого
  постачальника генерації відео для моделей Veo; Gemini CLI OAuth також
  володіє форматуванням токенів профілю автентифікації, розбором токенів використання та отриманням endpoint-ів квот
  для поверхонь використання
- `moonshot`: спільний транспорт, нормалізація payload thinking, якою володіє Plugin
- `kilocode`: спільний транспорт, заголовки запитів, якими володіє Plugin, нормалізація payload reasoning,
  санація підпису thought Gemini у проксі Gemini та політика cache-TTL
- `zai`: forward-compat резервний перехід для GLM-5, типові значення `tool_stream`, політика cache-TTL,
  політика binary-thinking/live-model і автентифікація використання + отримання квот;
  невідомі ідентифікатори `glm-5*` синтезуються з вбудованого шаблону `glm-4.7`
- `xai`: нативна нормалізація транспорту Responses, переписування псевдонімів `/fast` для
  швидких варіантів Grok, типовий `tool_stream`, очищення схеми інструментів /
  payload reasoning, специфічне для xAI, і реєстрація вбудованого постачальника генерації відео
  для `grok-imagine-video`
- `mistral`: метадані можливостей, якими володіє Plugin
- `opencode` і `opencode-go`: метадані можливостей, якими володіє Plugin, плюс
  санація підпису thought Gemini у проксі Gemini
- `alibaba`: каталог генерації відео, яким володіє Plugin, для прямих посилань на моделі Wan,
  таких як `alibaba/wan2.6-t2v`
- `byteplus`: каталоги, якими володіє Plugin, плюс реєстрація вбудованого постачальника генерації відео
  для моделей Seedance text-to-video/image-to-video
- `fal`: реєстрація вбудованого постачальника генерації відео для розміщених сторонніх
  постачальників генерації зображень для моделей FLUX image, а також реєстрація вбудованого
  постачальника генерації відео для розміщених сторонніх відеомоделей
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` і `volcengine`:
  лише каталоги, якими володіє Plugin
- `qwen`: каталоги текстових моделей, якими володіє Plugin, плюс спільні
  реєстрації постачальників media-understanding і генерації відео для його
  мультимодальних поверхонь; генерація відео Qwen використовує стандартні відеоendpoint-и DashScope
  зі вбудованими моделями Wan, такими як `wan2.6-t2v` і `wan2.7-r2v`
- `runway`: реєстрація постачальника генерації відео, якою володіє Plugin, для нативних
  task-based моделей Runway, таких як `gen4.5`
- `minimax`: каталоги, якими володіє Plugin, реєстрація вбудованого постачальника генерації відео
  для відеомоделей Hailuo, реєстрація вбудованого постачальника генерації зображень
  для `image-01`, гібридний вибір політики відтворення Anthropic/OpenAI
  та логіка автентифікації/знімків використання
- `together`: каталоги, якими володіє Plugin, плюс реєстрація вбудованого постачальника генерації відео
  для відеомоделей Wan
- `xiaomi`: каталоги, якими володіє Plugin, плюс логіка автентифікації/знімків використання

Тепер вбудований Plugin `openai` володіє обома ідентифікаторами постачальника: `openai` і
`openai-codex`.

Це охоплює постачальників, які все ще вписуються у звичайні транспорти OpenClaw. Постачальник,
якому потрібен повністю користувацький виконавець запитів, — це окрема, глибша поверхня розширення.

## Ротація API-ключів

- Підтримує загальну ротацію постачальників для вибраних постачальників.
- Налаштуйте кілька ключів через:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (одне live-перевизначення, найвищий пріоритет)
  - `<PROVIDER>_API_KEYS` (список через кому або крапку з комою)
  - `<PROVIDER>_API_KEY` (основний ключ)
  - `<PROVIDER>_API_KEY_*` (нумерований список, наприклад `<PROVIDER>_API_KEY_1`)
- Для постачальників Google як резерв також включається `GOOGLE_API_KEY`.
- Порядок вибору ключів зберігає пріоритет і прибирає дублікати значень.
- Запити повторюються з наступним ключем лише у відповідях із rate limit (наприклад
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` або періодичних повідомленнях про ліміт використання).
- Збої, не пов’язані з rate limit, завершуються одразу; ротація ключів не виконується.
- Коли всі можливі ключі не спрацьовують, повертається остання помилка з останньої спроби.

## Вбудовані постачальники (каталог pi-ai)

OpenClaw постачається з каталогом pi‑ai. Ці постачальники **не**
потребують конфігурації `models.providers`; достатньо налаштувати автентифікацію й вибрати модель.

### OpenAI

- Постачальник: `openai`
- Автентифікація: `OPENAI_API_KEY`
- Необов’язкова ротація: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, а також `OPENCLAW_LIVE_OPENAI_KEY` (одне перевизначення)
- Приклади моделей: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Типовий транспорт — `auto` (спочатку WebSocket, потім резервний SSE)
- Перевизначення для окремої моделі через `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` або `"auto"`)
- Розігрів OpenAI Responses WebSocket типово ввімкнено через `params.openaiWsWarmup` (`true`/`false`)
- Пріоритетну обробку OpenAI можна ввімкнути через `agents.defaults.models["openai/<model>"].params.serviceTier`
- `/fast` і `params.fastMode` зіставляють прямі запити Responses `openai/*` із `service_tier=priority` на `api.openai.com`
- Використовуйте `params.serviceTier`, якщо вам потрібен явний рівень замість спільного перемикача `/fast`
- Приховані заголовки атрибуції OpenClaw (`originator`, `version`,
  `User-Agent`) застосовуються лише до нативного трафіку OpenAI на `api.openai.com`, а не
  до загальних проксі, сумісних з OpenAI
- Нативні маршрути OpenAI також зберігають `store` Responses, підказки кешу підказок і
  формування payload сумісності reasoning OpenAI; проксі-маршрути цього не роблять
- `openai/gpt-5.3-codex-spark` навмисно придушено в OpenClaw, оскільки live API OpenAI його відхиляє; Spark розглядається як лише Codex

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Постачальник: `anthropic`
- Автентифікація: `ANTHROPIC_API_KEY`
- Необов’язкова ротація: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, а також `OPENCLAW_LIVE_ANTHROPIC_KEY` (одне перевизначення)
- Приклад моделі: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Прямі публічні запити Anthropic також підтримують спільний перемикач `/fast` і `params.fastMode`, зокрема трафік з автентифікацією API-ключем і OAuth, надісланий на `api.anthropic.com`; OpenClaw зіставляє це з Anthropic `service_tier` (`auto` проти `standard_only`)
- Примітка щодо Anthropic: співробітники Anthropic повідомили нам, що використання Claude CLI у стилі OpenClaw знову дозволене, тому OpenClaw розглядає повторне використання Claude CLI і використання `claude -p` як санкціоновані для цієї інтеграції, якщо Anthropic не опублікує нову політику.
- Setup-token Anthropic залишається доступним як підтримуваний шлях токена OpenClaw, але тепер OpenClaw надає перевагу повторному використанню Claude CLI і `claude -p`, коли вони доступні.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Постачальник: `openai-codex`
- Автентифікація: OAuth (ChatGPT)
- Приклад моделі: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` або `openclaw models auth login --provider openai-codex`
- Типовий транспорт — `auto` (спочатку WebSocket, потім резервний SSE)
- Перевизначення для окремої моделі через `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` або `"auto"`)
- `params.serviceTier` також пересилається в нативних запитах Codex Responses (`chatgpt.com/backend-api`)
- Приховані заголовки атрибуції OpenClaw (`originator`, `version`,
  `User-Agent`) додаються лише до нативного трафіку Codex на
  `chatgpt.com/backend-api`, а не до загальних проксі, сумісних з OpenAI
- Має спільний із прямим `openai/*` перемикач `/fast` і конфігурацію `params.fastMode`; OpenClaw зіставляє це з `service_tier=priority`
- `openai-codex/gpt-5.3-codex-spark` залишається доступною, коли каталог OAuth Codex її надає; залежить від entitlement
- `openai-codex/gpt-5.4` зберігає нативні `contextWindow = 1050000` і типові runtime `contextTokens = 272000`; перевизначте runtime-обмеження через `models.providers.openai-codex.models[].contextTokens`
- Примітка щодо політики: OAuth OpenAI Codex явно підтримується для зовнішніх інструментів/робочих процесів, таких як OpenClaw.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Інші розміщені варіанти в стилі підписки

- [Qwen Cloud](/uk/providers/qwen): поверхня постачальника Qwen Cloud, а також зіставлення endpoint-ів Alibaba DashScope і Coding Plan
- [MiniMax](/uk/providers/minimax): доступ MiniMax Coding Plan через OAuth або API-ключ
- [GLM Models](/uk/providers/glm): Z.AI Coding Plan або загальні API endpoint-и

### OpenCode

- Автентифікація: `OPENCODE_API_KEY` (або `OPENCODE_ZEN_API_KEY`)
- Постачальник середовища виконання Zen: `opencode`
- Постачальник середовища виконання Go: `opencode-go`
- Приклади моделей: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` або `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (API-ключ)

- Постачальник: `google`
- Автентифікація: `GEMINI_API_KEY`
- Необов’язкова ротація: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, резервний `GOOGLE_API_KEY` і `OPENCLAW_LIVE_GEMINI_KEY` (одне перевизначення)
- Приклади моделей: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Сумісність: застаріла конфігурація OpenClaw з `google/gemini-3.1-flash-preview` нормалізується до `google/gemini-3-flash-preview`
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Прямі запуски Gemini також приймають `agents.defaults.models["google/<model>"].params.cachedContent`
  (або застарілий `cached_content`) для пересилання нативного для постачальника
  дескриптора `cachedContents/...`; cache hit-и Gemini відображаються як `cacheRead` OpenClaw

### Google Vertex і Gemini CLI

- Постачальники: `google-vertex`, `google-gemini-cli`
- Автентифікація: Vertex використовує gcloud ADC; Gemini CLI використовує власний потік OAuth
- Застереження: Gemini CLI OAuth в OpenClaw — це неофіційна інтеграція. Деякі користувачі повідомляли про обмеження облікового запису Google після використання сторонніх клієнтів. Ознайомтеся з умовами Google і використовуйте некритичний обліковий запис, якщо вирішите продовжити.
- Gemini CLI OAuth постачається як частина вбудованого Plugin-а `google`.
  - Спочатку встановіть Gemini CLI:
    - `brew install gemini-cli`
    - або `npm install -g @google/gemini-cli`
  - Увімкнення: `openclaw plugins enable google`
  - Вхід: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Типова модель: `google-gemini-cli/gemini-3-flash-preview`
  - Примітка: вам **не потрібно** вставляти client id або secret у `openclaw.json`. Потік входу CLI зберігає
    токени в профілях автентифікації на хості Gateway.
  - Якщо після входу запити не виконуються, задайте `GOOGLE_CLOUD_PROJECT` або `GOOGLE_CLOUD_PROJECT_ID` на хості Gateway.
  - JSON-відповіді Gemini CLI розбираються з `response`; використання резервно береться з
    `stats`, а `stats.cached` нормалізується в `cacheRead` OpenClaw.

### Z.AI (GLM)

- Постачальник: `zai`
- Автентифікація: `ZAI_API_KEY`
- Приклад моделі: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Псевдоніми: `z.ai/*` і `z-ai/*` нормалізуються до `zai/*`
  - `zai-api-key` автоматично визначає відповідний endpoint Z.AI; `zai-coding-global`, `zai-coding-cn`, `zai-global` і `zai-cn` примусово задають конкретну поверхню

### Vercel AI Gateway

- Постачальник: `vercel-ai-gateway`
- Автентифікація: `AI_GATEWAY_API_KEY`
- Приклад моделі: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Постачальник: `kilocode`
- Автентифікація: `KILOCODE_API_KEY`
- Приклад моделі: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Base URL: `https://api.kilo.ai/api/gateway/`
- Статичний резервний каталог постачається з `kilocode/kilo/auto`; live-виявлення
  `https://api.kilo.ai/api/gateway/models` може додатково розширити runtime-каталог.
- Точна upstream-маршрутизація за `kilocode/kilo/auto` належить Kilo Gateway,
  а не жорстко закодована в OpenClaw.

Деталі налаштування дивіться в [/providers/kilocode](/uk/providers/kilocode).

### Інші вбудовані Plugin-и постачальників

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Приклад моделі: `openrouter/auto`
- OpenClaw застосовує задокументовані заголовки атрибуції застосунку OpenRouter лише тоді, коли
  запит справді спрямовано на `openrouter.ai`
- Специфічні для OpenRouter маркери Anthropic `cache_control` так само обмежуються
  перевіреними маршрутами OpenRouter, а не довільними URL проксі
- OpenRouter залишається на шляху в стилі проксі, сумісному з OpenAI, тому
  нативне формування запитів лише для OpenAI (`serviceTier`, `store` Responses,
  підказки кешу підказок, payload-и сумісності reasoning OpenAI) не пересилається
- Посилання OpenRouter на основі Gemini зберігають лише санацію підпису thought проксі Gemini;
  нативна перевірка відтворення Gemini та bootstrap-переписування залишаються вимкненими
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Приклад моделі: `kilocode/kilo/auto`
- Посилання Kilo на основі Gemini зберігають той самий шлях санації підпису thought
  проксі Gemini; `kilocode/kilo/auto` та інші підказки, що не підтримують проксі-reasoning,
  пропускають ін’єкцію proxy reasoning
- MiniMax: `minimax` (API-ключ) і `minimax-portal` (OAuth)
- Автентифікація: `MINIMAX_API_KEY` для `minimax`; `MINIMAX_OAUTH_TOKEN` або `MINIMAX_API_KEY` для `minimax-portal`
- Приклад моделі: `minimax/MiniMax-M2.7` або `minimax-portal/MiniMax-M2.7`
- Онбординг MiniMax/налаштування API-ключа записує явні визначення моделей M2.7 з
  `input: ["text", "image"]`; вбудований каталог постачальника зберігає chat-посилання
  лише текстовими, доки конфігурацію цього постачальника не буде матеріалізовано
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- Приклад моделі: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` або `KIMICODE_API_KEY`)
- Приклад моделі: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- Приклад моделі: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY` або `DASHSCOPE_API_KEY`)
- Приклад моделі: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- Приклад моделі: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Приклад моделі: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- Приклад моделі: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- Приклад моделі: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` або `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Приклад моделі: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- Приклад моделі: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - Нативні вбудовані запити xAI використовують шлях xAI Responses
  - `/fast` або `params.fastMode: true` переписує `grok-3`, `grok-3-mini`,
    `grok-4` і `grok-4-0709` на їхні варіанти `*-fast`
  - `tool_stream` типово ввімкнено; задайте
    `agents.defaults.models["xai/<model>"].params.tool_stream` у `false`, щоб
    вимкнути його
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Приклад моделі: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Моделі GLM на Cerebras використовують ідентифікатори `zai-glm-4.7` і `zai-glm-4.6`.
  - Base URL, сумісний з OpenAI: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Приклад моделі Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Див. [Hugging Face (Inference)](/uk/providers/huggingface).

## Постачальники через `models.providers` (custom/base URL)

Використовуйте `models.providers` (або `models.json`), щоб додати **власні** постачальники або
проксі, сумісні з OpenAI/Anthropic.

Багато з наведених нижче вбудованих Plugin-ів постачальників уже публікують типовий каталог.
Використовуйте явні записи `models.providers.<id>` лише тоді, коли хочете перевизначити
типовий base URL, заголовки або список моделей.

### Moonshot AI (Kimi)

Moonshot постачається як вбудований Plugin постачальника. Типово використовуйте вбудованого постачальника,
і додавайте явний запис `models.providers.moonshot` лише тоді, коли вам
потрібно перевизначити base URL або метадані моделі:

- Постачальник: `moonshot`
- Автентифікація: `MOONSHOT_API_KEY`
- Приклад моделі: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` або `openclaw onboard --auth-choice moonshot-api-key-cn`

Ідентифікатори моделей Kimi K2:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding використовує Anthropic-сумісний endpoint Moonshot AI:

- Постачальник: `kimi`
- Автентифікація: `KIMI_API_KEY`
- Приклад моделі: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Застарілий `kimi/k2p5` і надалі приймається як сумісний ідентифікатор моделі.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) надає доступ до Doubao та інших моделей у Китаї.

- Постачальник: `volcengine` (coding: `volcengine-plan`)
- Автентифікація: `VOLCANO_ENGINE_API_KEY`
- Приклад моделі: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Онбординг типово використовує coding-поверхню, але загальний каталог `volcengine/*`
реєструється одночасно.

У засобах вибору онбордингу/налаштування моделей варіант автентифікації Volcengine надає перевагу рядкам
`volcengine/*` і `volcengine-plan/*`. Якщо ці моделі ще не завантажені,
OpenClaw повертається до нефільтрованого каталогу замість показу порожнього
засобу вибору в межах постачальника.

Доступні моделі:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Coding-моделі (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (міжнародний)

BytePlus ARK надає міжнародним користувачам доступ до тих самих моделей, що й Volcano Engine.

- Постачальник: `byteplus` (coding: `byteplus-plan`)
- Автентифікація: `BYTEPLUS_API_KEY`
- Приклад моделі: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Онбординг типово використовує coding-поверхню, але загальний каталог `byteplus/*`
реєструється одночасно.

У засобах вибору онбордингу/налаштування моделей варіант автентифікації BytePlus надає перевагу рядкам
`byteplus/*` і `byteplus-plan/*`. Якщо ці моделі ще не завантажені,
OpenClaw повертається до нефільтрованого каталогу замість показу порожнього
засобу вибору в межах постачальника.

Доступні моделі:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Coding-моделі (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic надає Anthropic-сумісні моделі через постачальника `synthetic`:

- Постачальник: `synthetic`
- Автентифікація: `SYNTHETIC_API_KEY`
- Приклад моделі: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax налаштовується через `models.providers`, оскільки використовує власні endpoint-и:

- MiniMax OAuth (Global): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- MiniMax API-ключ (Global): `--auth-choice minimax-global-api`
- MiniMax API-ключ (CN): `--auth-choice minimax-cn-api`
- Автентифікація: `MINIMAX_API_KEY` для `minimax`; `MINIMAX_OAUTH_TOKEN` або
  `MINIMAX_API_KEY` для `minimax-portal`

Деталі налаштування, варіанти моделей і фрагменти конфігурації дивіться в [/providers/minimax](/uk/providers/minimax).

На Anthropic-сумісному streaming-шляху MiniMax OpenClaw вимикає thinking
типово, якщо ви явно його не задасте, а `/fast on` переписує
`MiniMax-M2.7` на `MiniMax-M2.7-highspeed`.

Поділ можливостей, якими володіє Plugin:

- Типові значення text/chat залишаються на `minimax/MiniMax-M2.7`
- Генерація зображень — це `minimax/image-01` або `minimax-portal/image-01`
- Розуміння зображень — це `MiniMax-VL-01`, яким володіє Plugin, на обох шляхах автентифікації MiniMax
- Вебпошук залишається на ідентифікаторі постачальника `minimax`

### LM Studio

LM Studio постачається як вбудований Plugin постачальника, який використовує нативний API:

- Постачальник: `lmstudio`
- Автентифікація: `LM_API_TOKEN`
- Типовий base URL inference: `http://localhost:1234/v1`

Потім задайте модель (замініть на один з ідентифікаторів, повернених `http://localhost:1234/api/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "lmstudio/openai/gpt-oss-20b" } },
  },
}
```

OpenClaw використовує нативні `/api/v1/models` і `/api/v1/models/load` LM Studio
для виявлення й автозавантаження, а `/v1/chat/completions` типово — для inference.
Див. [/providers/lmstudio](/uk/providers/lmstudio) для налаштування та усунення несправностей.

### Ollama

Ollama постачається як вбудований Plugin постачальника і використовує нативний API Ollama:

- Постачальник: `ollama`
- Автентифікація: не потрібна (локальний сервер)
- Приклад моделі: `ollama/llama3.3`
- Встановлення: [https://ollama.com/download](https://ollama.com/download)

```bash
# Встановіть Ollama, потім завантажте модель:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama локально виявляється за адресою `http://127.0.0.1:11434`, якщо ви явно вмикаєте це через
`OLLAMA_API_KEY`, а вбудований Plugin постачальника додає Ollama безпосередньо до
`openclaw onboard` і засобу вибору моделі. Див. [/providers/ollama](/uk/providers/ollama)
щодо онбордингу, хмарного/локального режиму та власної конфігурації.

### vLLM

vLLM постачається як вбудований Plugin постачальника для локальних/self-hosted OpenAI-сумісних
серверів:

- Постачальник: `vllm`
- Автентифікація: необов’язкова (залежить від вашого сервера)
- Типовий base URL: `http://127.0.0.1:8000/v1`

Щоб увімкнути локальне автовиявлення (підійде будь-яке значення, якщо ваш сервер не вимагає автентифікації):

```bash
export VLLM_API_KEY="vllm-local"
```

Потім задайте модель (замініть на один з ідентифікаторів, повернених `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Деталі дивіться в [/providers/vllm](/uk/providers/vllm).

### SGLang

SGLang постачається як вбудований Plugin постачальника для швидких self-hosted
OpenAI-сумісних серверів:

- Постачальник: `sglang`
- Автентифікація: необов’язкова (залежить від вашого сервера)
- Типовий base URL: `http://127.0.0.1:30000/v1`

Щоб увімкнути локальне автовиявлення (підійде будь-яке значення, якщо ваш сервер не
вимагає автентифікації):

```bash
export SGLANG_API_KEY="sglang-local"
```

Потім задайте модель (замініть на один з ідентифікаторів, повернених `/v1/models`):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Деталі дивіться в [/providers/sglang](/uk/providers/sglang).

### Локальні проксі (LM Studio, vLLM, LiteLLM тощо)

Приклад (сумісний з OpenAI):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "${LM_API_TOKEN}",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Примітки:

- Для власних постачальників `reasoning`, `input`, `cost`, `contextWindow` і `maxTokens` необов’язкові.
  Якщо їх не вказати, OpenClaw типово використовує:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Рекомендовано: задавайте явні значення, що відповідають обмеженням вашого проксі/моделі.
- Для `api: "openai-completions"` на ненативних endpoint-ах (будь-який непорожній `baseUrl`, чий host не є `api.openai.com`) OpenClaw примусово задає `compat.supportsDeveloperRole: false`, щоб уникати помилок 400 від постачальника для непідтримуваних ролей `developer`.
- Маршрути OpenAI-сумісного типу в стилі проксі також пропускають нативне формування запитів лише для OpenAI:
  без `service_tier`, без `store` Responses, без підказок кешу підказок, без
  формування payload сумісності reasoning OpenAI і без прихованих заголовків
  атрибуції OpenClaw.
- Якщо `baseUrl` порожній/не вказаний, OpenClaw зберігає типову поведінку OpenAI (яка вказує на `api.openai.com`).
- Для безпеки явне `compat.supportsDeveloperRole: true` усе одно перевизначається на ненативних endpoint-ах `openai-completions`.

## Приклади CLI

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Дивіться також: [/gateway/configuration](/uk/gateway/configuration) для повних прикладів конфігурації.

## Пов’язані сторінки

- [Models](/uk/concepts/models) — конфігурація моделей і псевдоніми
- [Model Failover](/uk/concepts/model-failover) — ланцюжки резервного переходу та поведінка повторних спроб
- [Configuration Reference](/uk/gateway/configuration-reference#agent-defaults) — ключі конфігурації моделей
- [Providers](/uk/providers) — посібники з налаштування для кожного постачальника
