---
read_when:
    - Вам потрібна детальна поведінка для `openclaw onboard`
    - Ви налагоджуєте результати онбордингу або інтегруєте клієнти онбордингу
sidebarTitle: CLI reference
summary: Повний довідник щодо потоку налаштування CLI, налаштування автентифікації/моделі, вихідних даних і внутрішньої реалізації
title: Довідник із налаштування CLI
x-i18n:
    generated_at: "2026-04-15T14:08:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# Довідник із налаштування CLI

Ця сторінка є повним довідником для `openclaw onboard`.
Короткий посібник дивіться в [Онбординг (CLI)](/uk/start/wizard).

## Що робить майстер

Локальний режим (типовий) проводить вас через:

- Налаштування моделі та автентифікації (OAuth підписки OpenAI Code, Anthropic Claude CLI або API-ключ, а також варіанти MiniMax, GLM, Ollama, Moonshot, StepFun і AI Gateway)
- Розташування робочого простору та bootstrap-файли
- Налаштування Gateway (порт, bind, автентифікація, Tailscale)
- Канали та провайдери (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles та інші вбудовані channel plugins)
- Встановлення демона (LaunchAgent, systemd user unit або нативне Windows Scheduled Task із резервним варіантом через папку Startup)
- Перевірка справності
- Налаштування Skills

Віддалений режим налаштовує цю машину на підключення до Gateway в іншому місці.
Він не встановлює та не змінює нічого на віддаленому хості.

## Подробиці локального потоку

<Steps>
  <Step title="Виявлення наявної конфігурації">
    - Якщо існує `~/.openclaw/openclaw.json`, виберіть Зберегти, Змінити або Скинути.
    - Повторний запуск майстра нічого не стирає, якщо ви явно не виберете Скинути (або не передасте `--reset`).
    - CLI `--reset` типово використовує `config+creds+sessions`; щоб також видалити робочий простір, використовуйте `--reset-scope full`.
    - Якщо конфігурація недійсна або містить застарілі ключі, майстер зупиняється й просить вас запустити `openclaw doctor` перед продовженням.
    - Скидання використовує `trash` і пропонує області:
      - Лише конфігурація
      - Конфігурація + облікові дані + сесії
      - Повне скидання (також видаляє робочий простір)
  </Step>
  <Step title="Модель і автентифікація">
    - Повна матриця варіантів наведена в [Параметри автентифікації та моделі](#auth-and-model-options).
  </Step>
  <Step title="Робочий простір">
    - Типово `~/.openclaw/workspace` (можна налаштувати).
    - Створює файли робочого простору, потрібні для bootstrap-ритуалу першого запуску.
    - Структура робочого простору: [Робочий простір агента](/uk/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Запитує порт, bind, режим автентифікації та доступність через Tailscale.
    - Рекомендовано: залишати автентифікацію за токеном увімкненою навіть для loopback, щоб локальні WS-клієнти мусили автентифікуватися.
    - У режимі токена інтерактивне налаштування пропонує:
      - **Згенерувати/зберегти відкритий токен** (типово)
      - **Використати SecretRef** (необов’язково)
    - У режимі пароля інтерактивне налаштування також підтримує збереження у відкритому вигляді або через SecretRef.
    - Шлях SecretRef для неінтерактивного режиму токена: `--gateway-token-ref-env <ENV_VAR>`.
      - Потребує непорожньої змінної середовища в середовищі процесу онбордингу.
      - Не можна поєднувати з `--gateway-token`.
    - Вимикайте автентифікацію лише якщо повністю довіряєте кожному локальному процесу.
    - Bind не лише на loopback однаково вимагає автентифікації.
  </Step>
  <Step title="Канали">
    - [WhatsApp](/uk/channels/whatsapp): необов’язковий вхід через QR
    - [Telegram](/uk/channels/telegram): токен бота
    - [Discord](/uk/channels/discord): токен бота
    - [Google Chat](/uk/channels/googlechat): JSON сервісного облікового запису + аудиторія Webhook
    - [Mattermost](/uk/channels/mattermost): токен бота + базовий URL
    - [Signal](/uk/channels/signal): необов’язкове встановлення `signal-cli` + конфігурація облікового запису
    - [BlueBubbles](/uk/channels/bluebubbles): рекомендовано для iMessage; URL сервера + пароль + Webhook
    - [iMessage](/uk/channels/imessage): застарілий шлях CLI `imsg` + доступ до БД
    - Безпека DM: типово використовується прив’язка. Перше DM надсилає код; схваліть його через
      `openclaw pairing approve <channel> <code>` або використовуйте allowlist.
  </Step>
  <Step title="Встановлення демона">
    - macOS: LaunchAgent
      - Потребує сесії користувача з входом; для headless використовуйте власний LaunchDaemon (не постачається).
    - Linux і Windows через WSL2: systemd user unit
      - Майстер намагається виконати `loginctl enable-linger <user>`, щоб Gateway залишався активним після виходу з системи.
      - Може запросити sudo (записує в `/var/lib/systemd/linger`); спочатку пробує без sudo.
    - Нативний Windows: спочатку Scheduled Task
      - Якщо створення завдання заборонено, OpenClaw переходить на резервний варіант із per-user елементом входу в папці Startup і відразу запускає Gateway.
      - Scheduled Tasks залишаються кращим варіантом, бо забезпечують кращий статус супервізора.
    - Вибір середовища виконання: Node (рекомендовано; обов’язково для WhatsApp і Telegram). Bun не рекомендується.
  </Step>
  <Step title="Перевірка справності">
    - Запускає Gateway (за потреби) і виконує `openclaw health`.
    - `openclaw status --deep` додає до виводу статусу перевірку справності живого Gateway, включно з перевірками каналів, коли це підтримується.
  </Step>
  <Step title="Skills">
    - Зчитує доступні Skills і перевіряє вимоги.
    - Дозволяє вибрати менеджер Node: npm, pnpm або bun.
    - Встановлює необов’язкові залежності (деякі використовують Homebrew на macOS).
  </Step>
  <Step title="Завершення">
    - Підсумок і наступні кроки, включно з варіантами для застосунків iOS, Android і macOS.
  </Step>
</Steps>

<Note>
Якщо GUI не виявлено, майстер виводить інструкції з SSH-переадресації порту для Control UI замість відкриття браузера.
Якщо ресурси Control UI відсутні, майстер намагається їх зібрати; резервний варіант — `pnpm ui:build` (автоматично встановлює залежності UI).
</Note>

## Подробиці віддаленого режиму

Віддалений режим налаштовує цю машину на підключення до Gateway в іншому місці.

<Info>
Віддалений режим не встановлює та не змінює нічого на віддаленому хості.
</Info>

Що ви налаштовуєте:

- URL віддаленого Gateway (`ws://...`)
- Токен, якщо віддалений Gateway вимагає автентифікації (рекомендовано)

<Note>
- Якщо Gateway доступний лише через loopback, використовуйте SSH-тунелювання або tailnet.
- Підказки для виявлення:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Параметри автентифікації та моделі

<AccordionGroup>
  <Accordion title="API-ключ Anthropic">
    Використовує `ANTHROPIC_API_KEY`, якщо він наявний, або запитує ключ, а потім зберігає його для використання демоном.
  </Accordion>
  <Accordion title="Підписка OpenAI Code (повторне використання Codex CLI)">
    Якщо існує `~/.codex/auth.json`, майстер може повторно використати його.
    Повторно використані облікові дані Codex CLI і далі керуються Codex CLI; після завершення строку дії OpenClaw
    спочатку знову читає це джерело і, коли провайдер може його оновити, записує
    оновлені облікові дані назад у сховище Codex замість того, щоб брати керування
    ними на себе.
  </Accordion>
  <Accordion title="Підписка OpenAI Code (OAuth)">
    Потік через браузер; вставте `code#state`.

    Встановлює `agents.defaults.model` у `openai-codex/gpt-5.4`, коли модель не задана або має вигляд `openai/*`.

  </Accordion>
  <Accordion title="API-ключ OpenAI">
    Використовує `OPENAI_API_KEY`, якщо він наявний, або запитує ключ, а потім зберігає облікові дані в профілях автентифікації.

    Встановлює `agents.defaults.model` у `openai/gpt-5.4`, коли модель не задана, має вигляд `openai/*` або `openai-codex/*`.

  </Accordion>
  <Accordion title="API-ключ xAI (Grok)">
    Запитує `XAI_API_KEY` і налаштовує xAI як провайдера моделі.
  </Accordion>
  <Accordion title="OpenCode">
    Запитує `OPENCODE_API_KEY` (або `OPENCODE_ZEN_API_KEY`) і дозволяє вибрати каталог Zen або Go.
    URL налаштування: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API-ключ (загальний)">
    Зберігає ключ для вас.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Запитує `AI_GATEWAY_API_KEY`.
    Докладніше: [Vercel AI Gateway](/uk/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Запитує ID облікового запису, ID Gateway і `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    Докладніше: [Cloudflare AI Gateway](/uk/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Конфігурація записується автоматично. Розміщений типово варіант — `MiniMax-M2.7`; налаштування через API-ключ використовує
    `minimax/...`, а налаштування через OAuth — `minimax-portal/...`.
    Докладніше: [MiniMax](/uk/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Конфігурація записується автоматично для стандартного StepFun або Step Plan на китайських чи глобальних endpoints.
    Стандартний варіант наразі включає `step-3.5-flash`, а Step Plan також включає `step-3.5-flash-2603`.
    Докладніше: [StepFun](/uk/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (сумісний з Anthropic)">
    Запитує `SYNTHETIC_API_KEY`.
    Докладніше: [Synthetic](/uk/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud і локальні відкриті моделі)">
    Спочатку запитує `Cloud + Local`, `Cloud only` або `Local only`.
    `Cloud only` використовує `OLLAMA_API_KEY` з `https://ollama.com`.
    Режими з опорою на хост запитують базовий URL (типово `http://127.0.0.1:11434`), виявляють доступні моделі та пропонують типові варіанти.
    `Cloud + Local` також перевіряє, чи цей хост Ollama увійшов у систему для доступу до cloud.
    Докладніше: [Ollama](/uk/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot і Kimi Coding">
    Конфігурації Moonshot (Kimi K2) і Kimi Coding записуються автоматично.
    Докладніше: [Moonshot AI (Kimi + Kimi Coding)](/uk/providers/moonshot).
  </Accordion>
  <Accordion title="Власний провайдер">
    Працює з endpoint, сумісними з OpenAI і Anthropic.

    Інтерактивний онбординг підтримує ті самі варіанти збереження API-ключа, що й інші потоки API-ключів провайдерів:
    - **Вставити API-ключ зараз** (у відкритому вигляді)
    - **Використати secret reference** (посилання на env або налаштованого провайдера, з попередньою перевіркою)

    Прапорці неінтерактивного режиму:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (необов’язково; резервний варіант — `CUSTOM_API_KEY`)
    - `--custom-provider-id` (необов’язково)
    - `--custom-compatibility <openai|anthropic>` (необов’язково; типово `openai`)

  </Accordion>
  <Accordion title="Пропустити">
    Залишає автентифікацію неналаштованою.
  </Accordion>
</AccordionGroup>

Поведінка моделі:

- Виберіть типову модель із виявлених варіантів або введіть провайдера й модель вручну.
- Коли онбординг починається з вибору автентифікації провайдера, засіб вибору моделі автоматично надає перевагу
  цьому провайдеру. Для Volcengine і BytePlus та сама перевага
  також поширюється на їхні варіанти coding-plan (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Якщо цей фільтр за пріоритетним провайдером буде порожнім, засіб вибору повертається
  до повного каталогу замість того, щоб не показувати жодних моделей.
- Майстер запускає перевірку моделі та попереджає, якщо налаштована модель невідома або для неї відсутня автентифікація.

Шляхи до облікових даних і профілів:

- Профілі автентифікації (API-ключі + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Імпорт застарілого OAuth: `~/.openclaw/credentials/oauth.json`

Режим зберігання облікових даних:

- Типова поведінка онбордингу зберігає API-ключі як відкриті значення в профілях автентифікації.
- `--secret-input-mode ref` вмикає режим посилань замість зберігання ключів у відкритому вигляді.
  В інтерактивному налаштуванні можна вибрати один із варіантів:
  - посилання на змінну середовища (наприклад, `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - посилання на налаштованого провайдера (`file` або `exec`) з псевдонімом провайдера та id
- Інтерактивний режим посилань виконує швидку попередню перевірку перед збереженням.
  - Env-посилання: перевіряє назву змінної та непорожнє значення в поточному середовищі онбордингу.
  - Посилання на провайдера: перевіряє конфігурацію провайдера та розв’язує запитаний id.
  - Якщо попередня перевірка не вдається, онбординг показує помилку й дозволяє повторити спробу.
- У неінтерактивному режимі `--secret-input-mode ref` підтримує лише варіант через env.
  - Установіть змінну середовища провайдера в середовищі процесу онбордингу.
  - Вбудовані прапорці ключів (наприклад, `--openai-api-key`) вимагають, щоб цю змінну середовища було задано; інакше онбординг завершується з помилкою одразу.
  - Для власних провайдерів неінтерактивний режим `ref` зберігає `models.providers.<id>.apiKey` як `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - У випадку з таким власним провайдером `--custom-api-key` вимагає, щоб `CUSTOM_API_KEY` було задано; інакше онбординг завершується з помилкою одразу.
- Облікові дані автентифікації Gateway підтримують вибір між відкритим зберіганням і SecretRef в інтерактивному налаштуванні:
  - Режим токена: **Згенерувати/зберегти відкритий токен** (типово) або **Використати SecretRef**.
  - Режим пароля: відкритий вигляд або SecretRef.
- Шлях SecretRef для неінтерактивного режиму токена: `--gateway-token-ref-env <ENV_VAR>`.
- Наявні налаштування з відкритим зберіганням і далі працюють без змін.

<Note>
Порада для headless і серверів: завершіть OAuth на машині з браузером, а потім скопіюйте
`auth-profiles.json` цього агента (наприклад,
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` або відповідний шлях
`$OPENCLAW_STATE_DIR/...`) на хост Gateway. `credentials/oauth.json`
є лише застарілим джерелом імпорту.
</Note>

## Вихідні дані та внутрішня реалізація

Типові поля в `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (якщо вибрано Minimax)
- `tools.profile` (локальний онбординг типово встановлює `"coding"`, якщо значення не задано; наявні явні значення зберігаються)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (локальний онбординг типово встановлює `per-channel-peer`, якщо значення не задано; наявні явні значення зберігаються)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Allowlist каналів (Slack, Discord, Matrix, Microsoft Teams), якщо ви погоджуєтеся під час запитів (імена за можливості зіставляються з ID)
- `skills.install.nodeManager`
  - Прапорець `setup --node-manager` приймає `npm`, `pnpm` або `bun`.
  - Ручна конфігурація все одно може пізніше встановити `skills.install.nodeManager: "yarn"`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` записує `agents.list[]` і необов’язкові `bindings`.

Облікові дані WhatsApp зберігаються в `~/.openclaw/credentials/whatsapp/<accountId>/`.
Сесії зберігаються в `~/.openclaw/agents/<agentId>/sessions/`.

<Note>
Деякі канали постачаються як plugins. Якщо їх вибрано під час налаштування, майстер
пропонує встановити plugin (npm або локальний шлях) перед конфігурацією каналу.
</Note>

RPC майстра Gateway:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

Клієнти (застосунок macOS і Control UI) можуть відображати кроки без повторної реалізації логіки онбордингу.

Поведінка налаштування Signal:

- Завантажує відповідний ресурс релізу
- Зберігає його в `~/.openclaw/tools/signal-cli/<version>/`
- Записує `channels.signal.cliPath` у конфігурацію
- Збірки JVM потребують Java 21
- Нативні збірки використовуються, коли вони доступні
- Windows використовує WSL2 і дотримується Linux-потоку `signal-cli` всередині WSL

## Пов’язані документи

- Центр онбордингу: [Онбординг (CLI)](/uk/start/wizard)
- Автоматизація та скрипти: [Автоматизація CLI](/uk/start/wizard-cli-automation)
- Довідник команд: [`openclaw onboard`](/cli/onboard)
