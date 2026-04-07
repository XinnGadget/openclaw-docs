---
read_when:
    - Запуск тестів локально або в CI
    - Додавання регресій для помилок моделей/провайдерів
    - Налагодження поведінки gateway та agent
summary: 'Набір для тестування: unit/e2e/live набори, Docker-раннери та що саме покриває кожен тест'
title: Тестування
x-i18n:
    generated_at: "2026-04-07T05:10:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 77c61126344d03c7b04ccf1f9aba0381cf8c7c73042d69b2d9f3f07a5eba70d3
    source_path: help/testing.md
    workflow: 15
---

# Тестування

OpenClaw має три набори Vitest (unit/integration, e2e, live) і невеликий набір Docker-раннерів.

Цей документ — посібник «як ми тестуємо»:

- Що покриває кожен набір (і що він навмисно _не_ покриває)
- Які команди запускати для типових сценаріїв (локально, перед push, налагодження)
- Як live-тести знаходять облікові дані та вибирають моделі/провайдерів
- Як додавати регресії для реальних проблем із моделями/провайдерами

## Швидкий старт

У більшості випадків:

- Повний gate (очікується перед push): `pnpm build && pnpm check && pnpm test`
- Швидший локальний запуск повного набору на потужній машині: `pnpm test:max`
- Прямий цикл спостереження Vitest: `pnpm test:watch`
- Пряме націлення на файли тепер також маршрутизує шляхи extension/channel: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- QA-сайт на основі Docker: `pnpm qa:lab:up`

Коли ви змінюєте тести або хочете більше впевненості:

- Gate покриття: `pnpm test:coverage`
- Набір E2E: `pnpm test:e2e`

Під час налагодження реальних провайдерів/моделей (потрібні реальні облікові дані):

- Live-набір (моделі + gateway tool/image probes): `pnpm test:live`
- Тихо націлитися на один live-файл: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Порада: якщо вам потрібен лише один збійний кейс, звужуйте live-тести через змінні середовища allowlist, описані нижче.

## Набори тестів (що і де запускається)

Сприймайте набори як «зростання реалістичності» (і зростання нестабільності/вартості):

### Unit / integration (типово)

- Команда: `pnpm test`
- Конфігурація: десять послідовних shard-запусків (`vitest.full-*.config.ts`) поверх наявних scoped Vitest projects
- Файли: core/unit inventory у `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` та дозволені node-тести `ui`, які покриває `vitest.unit.config.ts`
- Обсяг:
  - Чисті unit-тести
  - In-process integration-тести (gateway auth, routing, tooling, parsing, config)
  - Детерміновані регресії для відомих багів
- Очікування:
  - Запускається в CI
  - Реальні ключі не потрібні
  - Має бути швидким і стабільним
- Примітка щодо projects:
  - Ненацілений `pnpm test` тепер запускає десять менших shard-конфігів (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) замість одного великого native root-project процесу. Це зменшує піковий RSS на завантажених машинах і не дає роботі auto-reply/extension виснажувати не пов’язані набори.
  - `pnpm test --watch` і далі використовує native root `vitest.config.ts` project graph, тому що multi-shard цикл watch непрактичний.
  - `pnpm test`, `pnpm test:watch` і `pnpm test:perf:imports` спочатку маршрутизують явні file/directory targets через scoped lanes, тож `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` уникає повної вартості запуску root project.
  - `pnpm test:changed` розгортає змінені git-шляхи в ті самі scoped lanes, коли diff зачіпає лише маршрутизовані source/test-файли; зміни config/setup усе ще повертаються до ширшого повторного запуску root-project.
  - Вибрані тести `plugin-sdk` і `commands` також маршрутизуються через окремі легкі lanes, які пропускають `test/setup-openclaw-runtime.ts`; stateful/runtime-heavy файли лишаються на наявних lanes.
  - Вибрані helper source-файли `plugin-sdk` і `commands` також відображають запуски в режимі changed на явні sibling-тести в цих легких lanes, щоб зміни helper-файлів не перевантажували повний важкий набір для цього каталогу.
  - `auto-reply` тепер має три окремі bucket-и: top-level core helpers, top-level integration-тести `reply.*` і піддерево `src/auto-reply/reply/**`. Це прибирає найважчу роботу harness reply із дешевих тестів status/chunk/token.
- Примітка щодо embedded runner:
  - Коли ви змінюєте входи виявлення message-tool або runtime context ущільнення,
    зберігайте обидва рівні покриття.
  - Додавайте сфокусовані helper-регресії для чистих меж routing/normalization.
  - Також підтримуйте здоровими integration-набори embedded runner:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`, і
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Ці набори перевіряють, що scoped ids і поведінка ущільнення все ще проходять
    через реальні шляхи `run.ts` / `compact.ts`; лише helper-тести не є
    достатньою заміною для цих integration-шляхів.
- Примітка щодо pool:
  - Базовий конфіг Vitest тепер типово використовує `threads`.
  - Спільний конфіг Vitest також фіксує `isolate: false` і використовує неізольований runner у root projects, e2e та live конфигах.
  - Root UI lane зберігає свій `jsdom` setup та optimizer, але тепер теж працює на спільному неізольованому runner.
  - Кожен shard `pnpm test` успадковує ті самі типові значення `threads` + `isolate: false` зі спільного конфига Vitest.
  - Спільний launcher `scripts/run-vitest.mjs` тепер також типово додає `--no-maglev` для дочірніх Node-процесів Vitest, щоб зменшити churn компіляції V8 під час великих локальних запусків. Установіть `OPENCLAW_VITEST_ENABLE_MAGLEV=1`, якщо потрібно порівняти зі стандартною поведінкою V8.
- Примітка щодо швидкої локальної ітерації:
  - `pnpm test:changed` маршрутизується через scoped lanes, коли змінені шляхи чисто відображаються на менший набір.
  - `pnpm test:max` і `pnpm test:changed:max` зберігають ту саму поведінку маршрутизації, лише з вищим лімітом worker-ів.
  - Автомасштабування локальних worker-ів тепер навмисно консервативне й також знижує активність, коли середнє навантаження хоста вже високе, тож кілька одночасних запусків Vitest типово завдають менше шкоди.
  - Базовий конфіг Vitest позначає projects/config files як `forceRerunTriggers`, щоб повторні запуски в режимі changed залишалися коректними, коли змінюється тестова wiring.
  - Конфіг зберігає `OPENCLAW_VITEST_FS_MODULE_CACHE` увімкненим на підтримуваних хостах; установіть `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`, якщо хочете одну явну локацію кешу для прямого профілювання.
- Примітка щодо налагодження продуктивності:
  - `pnpm test:perf:imports` вмикає звітність Vitest про тривалість імпорту та вивід деталізації імпортів.
  - `pnpm test:perf:imports:changed` обмежує той самий погляд профілювання файлами, зміненими відносно `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` порівнює маршрутизований `test:changed` із native root-project шляхом для цього зафіксованого diff і виводить wall time та macOS max RSS.
- `pnpm test:perf:changed:bench -- --worktree` бенчмаркує поточне брудне дерево, маршрутизуючи список змінених файлів через `scripts/test-projects.mjs` і root Vitest config.
  - `pnpm test:perf:profile:main` записує main-thread CPU profile для startup Vitest/Vite і transform overhead.
  - `pnpm test:perf:profile:runner` записує runner CPU+heap profiles для unit-набору з вимкненим паралелізмом файлів.

### E2E (gateway smoke)

- Команда: `pnpm test:e2e`
- Конфігурація: `vitest.e2e.config.ts`
- Файли: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Типові параметри runtime:
  - Використовує Vitest `threads` з `isolate: false`, узгоджено з рештою репозиторію.
  - Використовує адаптивну кількість worker-ів (CI: до 2, локально: 1 типово).
  - Типово запускається в silent mode, щоб зменшити накладні витрати на console I/O.
- Корисні override-и:
  - `OPENCLAW_E2E_WORKERS=<n>` — примусово задати кількість worker-ів (обмежено 16).
  - `OPENCLAW_E2E_VERBOSE=1` — знову увімкнути докладний консольний вивід.
- Обсяг:
  - Наскрізна поведінка multi-instance gateway
  - Поверхні WebSocket/HTTP, pair-инг node та важче мережеве навантаження
- Очікування:
  - Запускається в CI (коли ввімкнено в pipeline)
  - Реальні ключі не потрібні
  - Більше рухомих частин, ніж у unit-тестах (може бути повільніше)

### E2E: OpenShell backend smoke

- Команда: `pnpm test:e2e:openshell`
- Файл: `test/openshell-sandbox.e2e.test.ts`
- Обсяг:
  - Запускає ізольований OpenShell gateway на хості через Docker
  - Створює sandbox із тимчасового локального Dockerfile
  - Тестує backend OpenShell в OpenClaw через реальні `sandbox ssh-config` + SSH exec
  - Перевіряє поведінку файлової системи remote-canonical через sandbox fs bridge
- Очікування:
  - Лише opt-in; не входить до типового запуску `pnpm test:e2e`
  - Потрібні локальний CLI `openshell` і робочий Docker daemon
  - Використовує ізольовані `HOME` / `XDG_CONFIG_HOME`, а потім знищує test gateway і sandbox
- Корисні override-и:
  - `OPENCLAW_E2E_OPENSHELL=1`, щоб увімкнути тест під час ручного запуску ширшого e2e-набору
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`, щоб указати нестандартний CLI binary або wrapper script

### Live (реальні провайдери + реальні моделі)

- Команда: `pnpm test:live`
- Конфігурація: `vitest.live.config.ts`
- Файли: `src/**/*.live.test.ts`
- Типово: **увімкнено** через `pnpm test:live` (встановлює `OPENCLAW_LIVE_TEST=1`)
- Обсяг:
  - «Чи справді цей провайдер/модель працює _сьогодні_ з реальними обліковими даними?»
  - Виявлення змін формату провайдера, особливостей tool calling, проблем auth і поведінки rate limit
- Очікування:
  - Навмисно не є CI-stable (реальні мережі, реальні політики провайдерів, квоти, збої)
  - Коштує грошей / використовує ліміти запитів
  - Краще запускати звужені піднабори замість «усе»
- Live-запуски читають `~/.profile`, щоб підхопити відсутні API-ключі.
- Типово live-запуски все ще ізолюють `HOME` і копіюють config/auth-матеріали в тимчасовий тестовий home, щоб unit-fixtures не могли змінити ваш реальний `~/.openclaw`.
- Установлюйте `OPENCLAW_LIVE_USE_REAL_HOME=1` лише тоді, коли вам навмисно потрібно, щоб live-тести використовували вашу реальну домашню директорію.
- `pnpm test:live` тепер типово працює в тихішому режимі: залишає вивід прогресу `[live] ...`, але приховує додаткове повідомлення про `~/.profile` і заглушує логи bootstrap gateway/Bonjour. Установіть `OPENCLAW_LIVE_TEST_QUIET=0`, якщо хочете повернути повні startup-логи.
- Ротація API-ключів (залежно від провайдера): задайте `*_API_KEYS` у форматі через кому/крапку з комою або `*_API_KEY_1`, `*_API_KEY_2` (наприклад, `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) або per-live override через `OPENCLAW_LIVE_*_KEY`; тести повторюють спробу у відповідь на rate limit.
- Вивід прогресу/heartbeat:
  - Live-набори тепер виводять рядки прогресу в stderr, щоб тривалі виклики провайдерів було видно навіть тоді, коли Vitest тихо перехоплює консоль.
  - `vitest.live.config.ts` вимикає перехоплення консолі Vitest, тож рядки прогресу провайдера/gateway одразу транслюються під час live-запусків.
  - Налаштовуйте heartbeat прямих моделей через `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Налаштовуйте heartbeat gateway/probe через `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Який набір мені запускати?

Скористайтеся цією таблицею рішень:

- Редагуєте логіку/тести: запускайте `pnpm test` (і `pnpm test:coverage`, якщо змінили багато)
- Торкаєтесь gateway networking / WS protocol / pairing: додайте `pnpm test:e2e`
- Налагоджуєте «мій бот не працює» / специфічні збої провайдера / tool calling: запускайте звужений `pnpm test:live`

## Live: перевірка можливостей Android node

- Тест: `src/gateway/android-node.capabilities.live.test.ts`
- Скрипт: `pnpm android:test:integration`
- Мета: викликати **кожну команду, яку наразі рекламує** підключений Android node, і перевірити поведінку контракту команд.
- Обсяг:
  - Попередньо підготовлений/ручний setup (набір не встановлює/не запускає/не pair-ить застосунок).
  - Перевірка `node.invoke` в gateway команда за командою для вибраного Android node.
- Обов’язкова попередня підготовка:
  - Android app уже підключений і спарений із gateway.
  - Застосунок утримується на передньому плані.
  - Надано дозволи/погодження на capture для можливостей, які ви очікуєте пройти.
- Необов’язкові override-и цілі:
  - `OPENCLAW_ANDROID_NODE_ID` або `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Повні деталі setup Android: [Android App](/uk/platforms/android)

## Live: model smoke (profile keys)

Live-тести поділені на два шари, щоб ми могли ізолювати збої:

- «Direct model» показує, чи провайдер/модель взагалі може відповісти з наданим ключем.
- «Gateway smoke» показує, чи працює повний pipeline gateway+agent для цієї моделі (sessions, history, tools, sandbox policy тощо).

### Шар 1: Пряме завершення моделі (без gateway)

- Тест: `src/agents/models.profiles.live.test.ts`
- Мета:
  - Перелічити знайдені моделі
  - Використати `getApiKeyForModel`, щоб вибрати моделі, для яких у вас є облікові дані
  - Виконати невелике completion для кожної моделі (і цільові регресії, де це потрібно)
- Як увімкнути:
  - `pnpm test:live` (або `OPENCLAW_LIVE_TEST=1`, якщо запускаєте Vitest напряму)
- Установіть `OPENCLAW_LIVE_MODELS=modern` (або `all`, псевдонім для modern), щоб реально запустити цей набір; інакше його буде пропущено, щоб `pnpm test:live` залишався зосередженим на gateway smoke
- Як вибирати моделі:
  - `OPENCLAW_LIVE_MODELS=modern`, щоб запустити modern allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` — псевдонім для modern allowlist
  - або `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist через кому)
- Як вибирати провайдерів:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist через кому)
- Звідки беруться ключі:
  - Типово: profile store і резервні env-значення
  - Установіть `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, щоб примусово використовувати **лише profile store**
- Навіщо це існує:
  - Відокремлює «API провайдера зламане / ключ невалідний» від «pipeline gateway agent зламаний»
  - Містить невеликі ізольовані регресії (наприклад, replay міркувань OpenAI Responses/Codex Responses + потоки tool-call)

### Шар 2: Gateway + dev agent smoke (що насправді робить "@openclaw")

- Тест: `src/gateway/gateway-models.profiles.live.test.ts`
- Мета:
  - Підняти in-process gateway
  - Створити/оновити session `agent:dev:*` (override моделі для кожного запуску)
  - Ітеруватися по моделях із ключами і перевіряти:
    - «змістовну» відповідь (без tools)
    - що працює реальний виклик tool (read probe)
    - необов’язкові додаткові tool probes (exec+read probe)
    - що регресійні шляхи OpenAI (лише tool-call → follow-up) продовжують працювати
- Деталі probe (щоб ви могли швидко пояснювати збої):
  - `read` probe: тест записує nonce-файл у workspace і просить agent `read`-нути його та повернути nonce.
  - `exec+read` probe: тест просить agent через `exec` записати nonce у тимчасовий файл, а потім `read`-нути його назад.
  - image probe: тест прикріплює згенерований PNG (cat + випадковий code) і очікує, що модель поверне `cat <CODE>`.
  - Посилання на реалізацію: `src/gateway/gateway-models.profiles.live.test.ts` і `src/gateway/live-image-probe.ts`.
- Як увімкнути:
  - `pnpm test:live` (або `OPENCLAW_LIVE_TEST=1`, якщо запускаєте Vitest напряму)
- Як вибирати моделі:
  - Типово: modern allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` — псевдонім для modern allowlist
  - Або встановіть `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (або список через кому), щоб звузити запуск
- Як вибирати провайдерів (уникнути «OpenRouter для всього»):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist через кому)
- Tool + image probes у цьому live-тесті завжди увімкнені:
  - `read` probe + `exec+read` probe (stress tool-ів)
  - image probe запускається, коли модель декларує підтримку image input
  - Потік (на високому рівні):
    - Тест генерує маленький PNG із «CAT» + випадковим code (`src/gateway/live-image-probe.ts`)
    - Надсилає його через `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Gateway розбирає attachments у `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Embedded agent передає multimodal user message моделі
    - Перевірка: відповідь містить `cat` + code (допуск OCR: незначні помилки дозволені)

Порада: щоб побачити, що ви можете тестувати на своїй машині (і точні id `provider/model`), виконайте:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke локального CLI backend (Codex CLI або інші локальні CLI)

- Тест: `src/gateway/gateway-cli-backend.live.test.ts`
- Мета: перевірити pipeline Gateway + agent із використанням локального CLI backend, не торкаючись вашої типової конфігурації.
- Увімкнення:
  - `pnpm test:live` (або `OPENCLAW_LIVE_TEST=1`, якщо запускаєте Vitest напряму)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Типові значення:
  - Модель: `codex-cli/gpt-5.4`
  - Команда: `codex`
  - Аргументи: `["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- Override-и (необов’язково):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`, щоб надіслати реальний image attachment (шляхи інжектуються в prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`, щоб передавати шляхи до image-файлів як CLI args замість інжекції в prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (або `"list"`), щоб контролювати спосіб передавання image args, коли задано `IMAGE_ARG`.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`, щоб надіслати другий turn і перевірити потік resume.
  
Приклад:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Docker-рецепт:

```bash
pnpm test:docker:live-cli-backend
```

Примітки:

- Docker-раннер розташовано в `scripts/test-live-cli-backend-docker.sh`.
- Він запускає live smoke CLI-backend усередині Docker-образу репозиторію від імені непривілейованого користувача `node`.
- Для `codex-cli` він встановлює Linux-пакет `@openai/codex` у кешований записуваний префікс за адресою `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (типово: `~/.cache/openclaw/docker-cli-tools`).

## Live: smoke ACP bind (`/acp spawn ... --bind here`)

- Тест: `src/gateway/gateway-acp-bind.live.test.ts`
- Мета: перевірити реальний потік прив’язки розмови ACP з live ACP agent:
  - надіслати `/acp spawn <agent> --bind here`
  - прив’язати synthetic message-channel conversation на місці
  - надіслати звичайний follow-up у тій самій conversation
  - перевірити, що follow-up потрапляє в transcript прив’язаної ACP session
- Увімкнення:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Типові значення:
  - ACP agents у Docker: `claude,codex`
  - ACP agent для прямого `pnpm test:live ...`: `claude`
  - Synthetic channel: контекст conversation у стилі Slack DM
  - ACP backend: `acpx`
- Override-и:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Примітки:
  - Ця lane використовує поверхню gateway `chat.send` з admin-only synthetic originating-route fields, щоб тести могли приєднати контекст message-channel, не вдаючи зовнішню доставку.
  - Коли `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` не задано, тест використовує вбудований реєстр agent-ів plugin-а `acpx` для вибраного ACP harness agent.

Приклад:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Docker-рецепт:

```bash
pnpm test:docker:live-acp-bind
```

Docker-рецепти для одного agent-а:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
```

Примітки щодо Docker:

- Docker-раннер розташовано в `scripts/test-live-acp-bind-docker.sh`.
- Типово він запускає smoke ACP bind послідовно для обох підтримуваних live CLI agent-ів: `claude`, потім `codex`.
- Використовуйте `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude` або `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex`, щоб звузити матрицю.
- Він читає `~/.profile`, переносить відповідні CLI auth-матеріали в контейнер, встановлює `acpx` у записуваний npm-префікс, а потім за потреби встановлює потрібний live CLI (`@anthropic-ai/claude-code` або `@openai/codex`).
- Усередині Docker раннер установлює `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`, щоб `acpx` зберігав provider env vars із прочитаного profile доступними для дочірнього harness CLI.

### Рекомендовані live-рецепти

Вузькі, явні allowlist-и — найшвидші й найменш нестабільні:

- Одна модель, напряму (без gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Одна модель, gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Tool calling через кількох провайдерів:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Фокус на Google (API key Gemini + Antigravity):
  - Gemini (API key): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Примітки:

- `google/...` використовує Gemini API (API key).
- `google-antigravity/...` використовує OAuth-міст Antigravity (agent endpoint у стилі Cloud Code Assist).
- `google-gemini-cli/...` використовує локальний CLI Gemini на вашій машині (окрема auth + особливості tooling).
- Gemini API проти Gemini CLI:
  - API: OpenClaw викликає хостований Gemini API від Google через HTTP (API key / profile auth); це те, що більшість користувачів мають на увазі під «Gemini».
  - CLI: OpenClaw виконує зовнішній виклик до локального binary `gemini`; він має власну auth і може поводитися інакше (streaming/tool support/version skew).

## Live: матриця моделей (що ми покриваємо)

Немає фіксованого «списку моделей CI» (live є opt-in), але це **рекомендовані** моделі, які варто регулярно покривати на dev-машині з ключами.

### Сучасний smoke-набір (tool calling + image)

Це запуск «поширених моделей», який ми очікуємо підтримувати працездатним:

- OpenAI (не-Codex): `openai/gpt-5.4` (необов’язково: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (або `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` і `google/gemini-3-flash-preview` (уникайте старіших моделей Gemini 2.x)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` і `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Запустити gateway smoke із tools + image:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Базовий рівень: tool calling (Read + необов’язковий Exec)

Виберіть щонайменше по одній моделі на сімейство провайдерів:

- OpenAI: `openai/gpt-5.4` (або `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (або `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (або `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Необов’язкове додаткове покриття (було б добре мати):

- xAI: `xai/grok-4` (або найновіша доступна)
- Mistral: `mistral/`… (виберіть одну модель із підтримкою tools, яка у вас увімкнена)
- Cerebras: `cerebras/`… (якщо у вас є доступ)
- LM Studio: `lmstudio/`… (локально; tool calling залежить від режиму API)

### Vision: надсилання image (attachment → multimodal message)

Додайте щонайменше одну модель із підтримкою image до `OPENCLAW_LIVE_GATEWAY_MODELS` (Claude/Gemini/OpenAI vision-capable variants тощо), щоб перевірити image probe.

### Агрегатори / альтернативні gateway

Якщо у вас увімкнені ключі, ми також підтримуємо тестування через:

- OpenRouter: `openrouter/...` (сотні моделей; використовуйте `openclaw models scan`, щоб знайти кандидатів із підтримкою tools+image)
- OpenCode: `opencode/...` для Zen і `opencode-go/...` для Go (auth через `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Більше провайдерів, які можна включити в live-матрицю (якщо у вас є облікові дані/config):

- Вбудовані: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Через `models.providers` (custom endpoints): `minimax` (cloud/API), а також будь-який OpenAI/Anthropic-сумісний proxy (LM Studio, vLLM, LiteLLM тощо)

Порада: не намагайтеся жорстко прописати в документації «усі моделі». Авторитетний список — це те, що повертає `discoverModels(...)` на вашій машині, плюс доступні ключі.

## Облікові дані (ніколи не комітьте)

Live-тести знаходять облікові дані так само, як це робить CLI. Практичні наслідки:

- Якщо CLI працює, live-тести мають знаходити ті самі ключі.
- Якщо live-тест каже «немає облікових даних», налагоджуйте це так само, як налагоджували б `openclaw models list` / вибір моделі.

- Auth-профілі для кожного agent-а: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (саме це live-тести мають на увазі під “profile keys”)
- Config: `~/.openclaw/openclaw.json` (або `OPENCLAW_CONFIG_PATH`)
- Застарілий state-dir: `~/.openclaw/credentials/` (копіюється в staged live home, якщо існує, але це не основне сховище profile keys)
- Локальні live-запуски типово копіюють активний config, per-agent файли `auth-profiles.json`, застарілий `credentials/` та підтримувані каталоги auth зовнішніх CLI в тимчасовий test home; override-и шляхів `agents.*.workspace` / `agentDir` видаляються в цьому staged config, щоб probes не торкалися вашого реального host workspace.

Якщо ви хочете покладатися на env-ключі (наприклад, експортовані у вашому `~/.profile`), запускайте локальні тести після `source ~/.profile`, або використовуйте Docker-раннери нижче (вони можуть монтувати `~/.profile` у контейнер).

## Live Deepgram (транскрибування аудіо)

- Тест: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Увімкнення: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live BytePlus coding plan

- Тест: `src/agents/byteplus.live.test.ts`
- Увімкнення: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Необов’язковий override моделі: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live ComfyUI workflow media

- Тест: `extensions/comfy/comfy.live.test.ts`
- Увімкнення: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Обсяг:
  - Тестує вбудовані шляхи comfy для image, video і `music_generate`
  - Пропускає кожну можливість, якщо `models.providers.comfy.<capability>` не налаштовано
  - Корисно після змін у поданні workflow comfy, polling, downloads або реєстрації plugin-ів

## Live image generation

- Тест: `src/image-generation/runtime.live.test.ts`
- Команда: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Обсяг:
  - Перелічує кожен зареєстрований plugin-провайдер генерації image
  - Довантажує відсутні provider env vars із вашої login shell (`~/.profile`) перед probe
  - Типово використовує live/env API keys раніше за збережені auth-профілі, тож застарілі тестові ключі в `auth-profiles.json` не маскують реальні shell credentials
  - Пропускає провайдерів без придатної auth/profile/model
  - Запускає стандартні варіанти image generation через спільну runtime-можливість:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Поточні вбудовані провайдери, які покриваються:
  - `openai`
  - `google`
- Необов’язкове звуження:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Необов’язкова поведінка auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, щоб примусово використовувати auth зі сховища профілів і ігнорувати env-only override-и

## Live music generation

- Тест: `extensions/music-generation-providers.live.test.ts`
- Увімкнення: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Обсяг:
  - Тестує спільний шлях вбудованих провайдерів генерації музики
  - Наразі покриває Google і MiniMax
  - Довантажує provider env vars із вашої login shell (`~/.profile`) перед probe
  - Типово використовує live/env API keys раніше за збережені auth-профілі, тож застарілі тестові ключі в `auth-profiles.json` не маскують реальні shell credentials
  - Пропускає провайдерів без придатної auth/profile/model
  - Запускає обидва заявлені runtime-режими, якщо вони доступні:
    - `generate` із входом лише prompt
    - `edit`, коли провайдер декларує `capabilities.edit.enabled`
  - Поточне покриття в shared lane:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: окремий live-файл Comfy, не цей shared sweep
- Необов’язкове звуження:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Необов’язкова поведінка auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, щоб примусово використовувати auth зі сховища профілів і ігнорувати env-only override-и

## Live video generation

- Тест: `extensions/video-generation-providers.live.test.ts`
- Увімкнення: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Обсяг:
  - Тестує спільний шлях вбудованих провайдерів генерації video
  - Довантажує provider env vars із вашої login shell (`~/.profile`) перед probe
  - Типово використовує live/env API keys раніше за збережені auth-профілі, тож застарілі тестові ключі в `auth-profiles.json` не маскують реальні shell credentials
  - Пропускає провайдерів без придатної auth/profile/model
  - Запускає обидва заявлені runtime-режими, якщо вони доступні:
    - `generate` із входом лише prompt
    - `imageToVideo`, коли провайдер декларує `capabilities.imageToVideo.enabled` і вибраний провайдер/модель приймає локальний image input на основі буфера у shared sweep
    - `videoToVideo`, коли провайдер декларує `capabilities.videoToVideo.enabled` і вибраний провайдер/модель приймає локальний video input на основі буфера у shared sweep
  - Поточні провайдери `imageToVideo`, які заявлені, але пропускаються в shared sweep:
    - `vydra`, бо вбудований `veo3` працює лише з текстом, а вбудований `kling` потребує віддаленого image URL
  - Специфічне для провайдера покриття Vydra:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - цей файл запускає `veo3` для text-to-video плюс lane `kling`, яка типово використовує fixture віддаленого image URL
  - Поточне live-покриття `videoToVideo`:
    - лише `runway`, коли вибрана модель — `runway/gen4_aleph`
  - Поточні провайдери `videoToVideo`, які заявлені, але пропускаються в shared sweep:
    - `alibaba`, `qwen`, `xai`, бо ці шляхи наразі потребують віддалених reference URL `http(s)` / MP4
    - `google`, бо поточна shared lane Gemini/Veo використовує локальний input на основі буфера, а цей шлях не приймається в shared sweep
    - `openai`, бо поточна shared lane не гарантує org-specific доступ до video inpaint/remix
- Необов’язкове звуження:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- Необов’язкова поведінка auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, щоб примусово використовувати auth зі сховища профілів і ігнорувати env-only override-и

## Media live harness

- Команда: `pnpm test:live:media`
- Призначення:
  - Запускає спільні live-набори image, music і video через один стандартний entrypoint репозиторію
  - Автоматично завантажує відсутні provider env vars із `~/.profile`
  - Типово автоматично звужує кожен набір до провайдерів, для яких наразі є придатна auth
  - Повторно використовує `scripts/test-live.mjs`, тож поведінка heartbeat і quiet mode залишається узгодженою
- Приклади:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Docker-раннери (необов’язкові перевірки «працює в Linux»)

Ці Docker-раннери поділяються на дві категорії:

- Live-model раннери: `test:docker:live-models` і `test:docker:live-gateway` запускають лише відповідний live-файл profile-key усередині Docker-образу репозиторію (`src/agents/models.profiles.live.test.ts` і `src/gateway/gateway-models.profiles.live.test.ts`), монтують ваш локальний config dir і workspace (і читають `~/.profile`, якщо він змонтований). Відповідні локальні entrypoint-и — `test:live:models-profiles` і `test:live:gateway-profiles`.
- Docker live-раннери типово мають меншу межу smoke, щоб повний Docker sweep залишався практичним:
  `test:docker:live-models` типово використовує `OPENCLAW_LIVE_MAX_MODELS=12`, а
  `test:docker:live-gateway` — `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`, і
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Перевизначте ці env vars, коли
  вам свідомо потрібне більше, вичерпне сканування.
- `test:docker:all` один раз збирає live Docker-образ через `test:docker:live-build`, а потім повторно використовує його для двох Docker-lane live.
- Container smoke-раннери: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` і `test:docker:plugins` запускають один або більше реальних контейнерів і перевіряють інтеграційні шляхи вищого рівня.

Live-model Docker-раннери також bind-mount-ять лише потрібні CLI auth homes (або всі підтримувані, якщо запуск не звужено), а потім копіюють їх у контейнерний home перед запуском, щоб OAuth зовнішніх CLI міг оновлювати токени, не змінюючи auth store хоста:

- Прямі моделі: `pnpm test:docker:live-models` (скрипт: `scripts/test-live-models-docker.sh`)
- Smoke ACP bind: `pnpm test:docker:live-acp-bind` (скрипт: `scripts/test-live-acp-bind-docker.sh`)
- Smoke CLI backend: `pnpm test:docker:live-cli-backend` (скрипт: `scripts/test-live-cli-backend-docker.sh`)
- Gateway + dev agent: `pnpm test:docker:live-gateway` (скрипт: `scripts/test-live-gateway-models-docker.sh`)
- Live smoke Open WebUI: `pnpm test:docker:openwebui` (скрипт: `scripts/e2e/openwebui-docker.sh`)
- Майстер onboarding (TTY, повне scaffolding): `pnpm test:docker:onboard` (скрипт: `scripts/e2e/onboard-docker.sh`)
- Мережа gateway (два контейнери, WS auth + health): `pnpm test:docker:gateway-network` (скрипт: `scripts/e2e/gateway-network-docker.sh`)
- MCP channel bridge (seeded Gateway + stdio bridge + raw Claude notification-frame smoke): `pnpm test:docker:mcp-channels` (скрипт: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (install smoke + alias `/plugin` + семантика перезапуску Claude-bundle): `pnpm test:docker:plugins` (скрипт: `scripts/e2e/plugins-docker.sh`)

Live-model Docker-раннери також монтують поточний checkout лише для читання і
переносять його до тимчасового workdir усередині контейнера. Це зберігає runtime
image компактним, але все одно дає змогу запускати Vitest точно на ваших
локальних source/config. Крок staging пропускає великі локальні кеші та build outputs
застосунків, як-от `.pnpm-store`, `.worktrees`, `__openclaw_vitest__`, а також
локальні каталоги `.build` чи Gradle output, щоб Docker live-запуски не витрачали
хвилини на копіювання артефактів, специфічних для машини.
Вони також встановлюють `OPENCLAW_SKIP_CHANNELS=1`, щоб probes gateway live не запускали
реальні worker-и каналів Telegram/Discord тощо всередині контейнера.
`test:docker:live-models` усе ще запускає `pnpm test:live`, тож також передавайте
`OPENCLAW_LIVE_GATEWAY_*`, коли потрібно звузити або виключити покриття gateway
live із цієї Docker-lane.
`test:docker:openwebui` — це smoke перевірка сумісності вищого рівня: вона запускає
контейнер gateway OpenClaw з увімкненими HTTP endpoint-ами, сумісними з OpenAI,
запускає pinned контейнер Open WebUI проти цього gateway, виконує вхід через
Open WebUI, перевіряє, що `/api/models` показує `openclaw/default`, а потім надсилає
реальний chat request через proxy Open WebUI `/api/chat/completions`.
Перший запуск може бути помітно повільнішим, тому що Docker може знадобитися завантажити
image Open WebUI, а самому Open WebUI — завершити власний cold-start setup.
Для цієї lane потрібен придатний ключ live-моделі, а основним способом надати його в
Dockerized-запусках є `OPENCLAW_PROFILE_FILE`
(типово `~/.profile`).
Успішні запуски виводять невеликий JSON payload на кшталт `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` є навмисно детермінованим і не потребує
реального облікового запису Telegram, Discord або iMessage. Він запускає seeded Gateway
container, стартує другий контейнер, який виконує `openclaw mcp serve`, а потім
перевіряє виявлення маршрутизованих conversation, читання transcript, metadata вкладень,
поведінку черги live events, маршрутизацію outbound send, а також channel +
permission notifications у стилі Claude через реальний stdio MCP bridge. Перевірка notification
безпосередньо аналізує raw stdio MCP frames, тож smoke перевіряє те, що
міст насправді випромінює, а не лише те, що випадково показує конкретний client SDK.

Ручний smoke plain-language thread ACP (не CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Зберігайте цей скрипт для регресійних сценаріїв і налагодження. Він може знову знадобитися для валідації маршрутизації ACP thread, тож не видаляйте його.

Корисні env vars:

- `OPENCLAW_CONFIG_DIR=...` (типово: `~/.openclaw`), монтується в `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (типово: `~/.openclaw/workspace`), монтується в `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (типово: `~/.profile`), монтується в `/home/node/.profile` і читається перед запуском тестів
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (типово: `~/.cache/openclaw/docker-cli-tools`), монтується в `/home/node/.npm-global` для кешованих встановлень CLI усередині Docker
- Зовнішні каталоги/файли CLI auth у `$HOME` монтуються лише для читання під `/host-auth...`, а потім копіюються в `/home/node/...` перед стартом тестів
  - Типові каталоги: `.minimax`
  - Типові файли: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Звужені запуски провайдерів монтують лише потрібні каталоги/файли, виведені з `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Можна перевизначити вручну через `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` або список через кому на кшталт `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`, щоб звузити запуск
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`, щоб відфільтрувати провайдерів у контейнері
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, щоб гарантувати, що облікові дані беруться зі сховища профілів, а не з env
- `OPENCLAW_OPENWEBUI_MODEL=...`, щоб вибрати модель, яку gateway показує для smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...`, щоб перевизначити prompt перевірки nonce, який використовує smoke Open WebUI
- `OPENWEBUI_IMAGE=...`, щоб перевизначити pinned image tag Open WebUI

## Перевірка документації

Запускайте перевірки документації після редагування docs: `pnpm check:docs`.
Запускайте повну перевірку anchor-ів Mintlify, коли вам також потрібні перевірки heading-ів у межах сторінки: `pnpm docs:check-links:anchors`.

## Офлайн-регресія (безпечна для CI)

Це регресії «реального pipeline» без реальних провайдерів:

- Tool calling gateway (mock OpenAI, реальний цикл gateway + agent): `src/gateway/gateway.test.ts` (кейс: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Майстер gateway (WS `wizard.start`/`wizard.next`, записує config + примусову auth): `src/gateway/gateway.test.ts` (кейс: "runs wizard over ws and writes auth token config")

## Agent reliability evals (Skills)

У нас уже є кілька безпечних для CI тестів, які поводяться як «оцінювання надійності agent-а»:

- Mock tool-calling через реальний цикл gateway + agent (`src/gateway/gateway.test.ts`).
- Наскрізні потоки майстра, які перевіряють wiring session і ефекти config (`src/gateway/gateway.test.ts`).

Що ще бракує для Skills (див. [Skills](/uk/tools/skills)):

- **Decisioning:** коли Skills перелічені в prompt, чи вибирає agent правильну skill (або уникає неактуальних)?
- **Compliance:** чи читає agent `SKILL.md` перед використанням і чи дотримується обов’язкових кроків/args?
- **Workflow contracts:** багатокрокові сценарії, які перевіряють порядок tool-ів, перенесення історії session та межі sandbox.

Майбутні eval-оцінювання спочатку мають залишатися детермінованими:

- Scenario runner з mock-провайдерами для перевірки викликів tool-ів + порядку, читання skill-файлів і wiring session.
- Невеликий набір skill-орієнтованих сценаріїв (використовувати чи уникати, gate-ування, prompt injection).
- Необов’язкові live eval-оцінювання (opt-in, під керуванням env) лише після того, як безпечний для CI набір буде готовий.

## Contract-тести (форма plugin-ів і channel-ів)

Contract-тести перевіряють, що кожен зареєстрований plugin і channel відповідає
своєму interface contract. Вони перебирають усі виявлені plugin-и й запускають набір
перевірок форми та поведінки. Типова unit-lane `pnpm test` навмисно
пропускає ці спільні seam- і smoke-файли; запускайте contract-команди явно,
коли торкаєтесь спільних поверхонь channel або provider.

### Команди

- Усі contracts: `pnpm test:contracts`
- Лише channel contracts: `pnpm test:contracts:channels`
- Лише provider contracts: `pnpm test:contracts:plugins`

### Channel contracts

Розташовані в `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Базова форма plugin-а (id, name, capabilities)
- **setup** - Контракт майстра setup
- **session-binding** - Поведінка прив’язки session
- **outbound-payload** - Структура message payload
- **inbound** - Обробка вхідних повідомлень
- **actions** - Обробники дій channel
- **threading** - Обробка ID thread
- **directory** - API directory/roster
- **group-policy** - Забезпечення group policy

### Contracts статусу провайдера

Розташовані в `src/plugins/contracts/*.contract.test.ts`.

- **status** - Probes статусу channel
- **registry** - Форма реєстру plugin-ів

### Provider contracts

Розташовані в `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Контракт потоку auth
- **auth-choice** - Вибір/підбір auth
- **catalog** - API каталогу моделей
- **discovery** - Виявлення plugin-ів
- **loader** - Завантаження plugin-ів
- **runtime** - Runtime провайдера
- **shape** - Форма/інтерфейс plugin-а
- **wizard** - Майстер setup

### Коли запускати

- Після зміни export-ів або subpath-ів plugin-sdk
- Після додавання або зміни channel чи provider plugin-а
- Після рефакторингу реєстрації plugin-ів або discovery

Contract-тести запускаються в CI і не потребують реальних API-ключів.

## Додавання регресій (рекомендації)

Коли ви виправляєте проблему провайдера/моделі, виявлену в live:

- Додайте безпечну для CI регресію, якщо це можливо (mock/stub провайдера або фіксація точної трансформації форми запиту)
- Якщо проблема за своєю природою лише live (rate limit, політики auth), зберігайте live-тест вузьким і opt-in через env vars
- Надавайте перевагу найменшому шару, який ловить баг:
  - баг перетворення/replay запиту провайдера → тест direct models
  - баг pipeline gateway session/history/tool → gateway live smoke або безпечний для CI mock-тест gateway
- Захисне правило обходу SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` виводить по одному вибраному target на клас SecretRef із metadata реєстру (`listSecretTargetRegistryEntries()`), а потім перевіряє, що traversal-segment exec id відхиляються.
  - Якщо ви додаєте нове сімейство target-ів SecretRef з `includeInPlan` у `src/secrets/target-registry-data.ts`, оновіть `classifyTargetClass` у цьому тесті. Тест навмисно падає на некласифікованих target id, щоб нові класи не можна було тихо пропустити.
