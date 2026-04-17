---
read_when:
    - Пошук конкретного кроку онбордингу або прапорця
    - Автоматизація онбордингу в неінтерактивному режимі
    - Налагодження поведінки онбордингу
sidebarTitle: Onboarding Reference
summary: 'Повний довідник з CLI-онбордингу: кожен крок, прапорець і поле конфігурації'
title: Довідник з онбордингу
x-i18n:
    generated_at: "2026-04-15T14:08:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# Довідник з онбордингу

Це повний довідник для `openclaw onboard`.
Огляд високого рівня див. у [Онбординг (CLI)](/uk/start/wizard).

## Деталі процесу (локальний режим)

<Steps>
  <Step title="Виявлення наявної конфігурації">
    - Якщо `~/.openclaw/openclaw.json` існує, виберіть **Зберегти / Змінити / Скинути**.
    - Повторний запуск онбордингу **не** стирає нічого, якщо ви явно не виберете **Скинути**
      (або не передасте `--reset`).
    - CLI `--reset` за замовчуванням використовує `config+creds+sessions`; використовуйте `--reset-scope full`,
      щоб також видалити workspace.
    - Якщо конфігурація невалідна або містить застарілі ключі, майстер зупиняється і просить
      вас запустити `openclaw doctor` перед продовженням.
    - Скидання використовує `trash` (ніколи не `rm`) і пропонує області:
      - Лише конфігурація
      - Конфігурація + облікові дані + сесії
      - Повне скидання (також видаляє workspace)
  </Step>
  <Step title="Модель/автентифікація">
    - **Ключ API Anthropic**: використовує `ANTHROPIC_API_KEY`, якщо він наявний, або запитує ключ, а потім зберігає його для використання демоном.
    - **Ключ API Anthropic**: бажаний вибір помічника Anthropic в онбордингу/налаштуванні.
    - **Anthropic setup-token**: усе ще доступний в онбордингу/налаштуванні, хоча OpenClaw тепер надає перевагу повторному використанню Claude CLI, коли це можливо.
    - **Підписка OpenAI Code (Codex) (Codex CLI)**: якщо `~/.codex/auth.json` існує, онбординг може повторно використати її. Повторно використані облікові дані Codex CLI і далі керуються Codex CLI; після завершення строку дії OpenClaw спочатку знову читає це джерело і, коли провайдер може їх оновити, записує оновлені облікові дані назад у сховище Codex замість того, щоб самостійно брати їх під своє керування.
    - **Підписка OpenAI Code (Codex) (OAuth)**: потік через браузер; вставте `code#state`.
      - Встановлює `agents.defaults.model` у `openai-codex/gpt-5.4`, якщо модель не задана або має вигляд `openai/*`.
    - **Ключ API OpenAI**: використовує `OPENAI_API_KEY`, якщо він наявний, або запитує ключ, а потім зберігає його в профілях автентифікації.
      - Встановлює `agents.defaults.model` у `openai/gpt-5.4`, якщо модель не задана, має вигляд `openai/*` або `openai-codex/*`.
    - **Ключ API xAI (Grok)**: запитує `XAI_API_KEY` і налаштовує xAI як провайдера моделей.
    - **OpenCode**: запитує `OPENCODE_API_KEY` (або `OPENCODE_ZEN_API_KEY`, отримайте його на https://opencode.ai/auth) і дає змогу вибрати каталог Zen або Go.
    - **Ollama**: спочатку пропонує **Cloud + Local**, **Лише Cloud** або **Лише Local**. `Cloud only` запитує `OLLAMA_API_KEY` і використовує `https://ollama.com`; режими з підтримкою хоста запитують базовий URL Ollama, виявляють доступні моделі та автоматично завантажують вибрану локальну модель за потреби; `Cloud + Local` також перевіряє, чи цей хост Ollama увійшов у cloud-доступ.
    - Докладніше: [Ollama](/uk/providers/ollama)
    - **Ключ API**: зберігає ключ за вас.
    - **Vercel AI Gateway (багатомодельний проксі)**: запитує `AI_GATEWAY_API_KEY`.
    - Докладніше: [Vercel AI Gateway](/uk/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: запитує Account ID, Gateway ID і `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - Докладніше: [Cloudflare AI Gateway](/uk/providers/cloudflare-ai-gateway)
    - **MiniMax**: конфігурація записується автоматично; hosted-значення за замовчуванням — `MiniMax-M2.7`.
      Налаштування через ключ API використовує `minimax/...`, а налаштування через OAuth —
      `minimax-portal/...`.
    - Докладніше: [MiniMax](/uk/providers/minimax)
    - **StepFun**: конфігурація записується автоматично для стандартного StepFun або Step Plan на китайських чи глобальних ендпойнтах.
    - Наразі стандартний набір містить `step-3.5-flash`, а Step Plan також містить `step-3.5-flash-2603`.
    - Докладніше: [StepFun](/uk/providers/stepfun)
    - **Synthetic (сумісний з Anthropic)**: запитує `SYNTHETIC_API_KEY`.
    - Докладніше: [Synthetic](/uk/providers/synthetic)
    - **Moonshot (Kimi K2)**: конфігурація записується автоматично.
    - **Kimi Coding**: конфігурація записується автоматично.
    - Докладніше: [Moonshot AI (Kimi + Kimi Coding)](/uk/providers/moonshot)
    - **Пропустити**: автентифікацію ще не налаштовано.
    - Виберіть модель за замовчуванням із виявлених варіантів (або введіть provider/model вручну). Для найкращої якості та нижчого ризику prompt injection вибирайте найсильнішу модель останнього покоління, доступну у вашому стеку провайдерів.
    - Онбординг запускає перевірку моделі та попереджає, якщо налаштована модель невідома або бракує автентифікації.
    - Режим зберігання ключів API за замовчуванням — це значення профілю автентифікації у відкритому тексті. Використовуйте `--secret-input-mode ref`, щоб натомість зберігати посилання на env (наприклад, `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Профілі автентифікації зберігаються в `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (ключі API + OAuth). `~/.openclaw/credentials/oauth.json` — це застаріле джерело лише для імпорту.
    - Докладніше: [/concepts/oauth](/uk/concepts/oauth)
    <Note>
    Порада для headless/server: завершіть OAuth на машині з браузером, а потім скопіюйте
    `auth-profiles.json` цього агента (наприклад,
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` або відповідний
    шлях `$OPENCLAW_STATE_DIR/...`) на хост Gateway. `credentials/oauth.json`
    є лише застарілим джерелом імпорту.
    </Note>
  </Step>
  <Step title="Workspace">
    - За замовчуванням `~/.openclaw/workspace` (можна налаштувати).
    - Створює у workspace файли, потрібні для ритуалу початкового запуску агента.
    - Повна структура workspace + довідник із резервного копіювання: [Робочий простір агента](/uk/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Порт, bind, режим автентифікації, експонування через Tailscale.
    - Рекомендація щодо автентифікації: залишайте **Token** навіть для loopback, щоб локальні WS-клієнти мали проходити автентифікацію.
    - У режимі token інтерактивне налаштування пропонує:
      - **Згенерувати/зберегти token у відкритому тексті** (типово)
      - **Використати SecretRef** (опційно)
      - Quickstart повторно використовує наявні SecretRef `gateway.auth.token` у провайдерах `env`, `file` і `exec` для probe/dashboard bootstrap під час онбордингу.
      - Якщо цей SecretRef налаштовано, але його неможливо розв’язати, онбординг завершується помилкою на ранньому етапі з чітким повідомленням про виправлення замість тихого погіршення автентифікації під час виконання.
    - У режимі password інтерактивне налаштування також підтримує зберігання у відкритому тексті або через SecretRef.
    - Шлях SecretRef для token у неінтерактивному режимі: `--gateway-token-ref-env <ENV_VAR>`.
      - Вимагає непорожню змінну середовища в середовищі процесу онбордингу.
      - Не можна поєднувати з `--gateway-token`.
    - Вимикайте автентифікацію лише якщо ви повністю довіряєте кожному локальному процесу.
    - Bind не до loopback усе одно вимагає автентифікації.
  </Step>
  <Step title="Канали">
    - [WhatsApp](/uk/channels/whatsapp): необов’язковий вхід через QR.
    - [Telegram](/uk/channels/telegram): token бота.
    - [Discord](/uk/channels/discord): token бота.
    - [Google Chat](/uk/channels/googlechat): JSON service account + webhook audience.
    - [Mattermost](/uk/channels/mattermost) (Plugin): token бота + базовий URL.
    - [Signal](/uk/channels/signal): необов’язкове встановлення `signal-cli` + конфігурація облікового запису.
    - [BlueBubbles](/uk/channels/bluebubbles): **рекомендовано для iMessage**; URL сервера + пароль + webhook.
    - [iMessage](/uk/channels/imessage): застарілий шлях до `imsg` CLI + доступ до БД.
    - Безпека приватних повідомлень: за замовчуванням використовується pairing. Перше приватне повідомлення надсилає код; схваліть його через `openclaw pairing approve <channel> <code>` або використовуйте allowlist.
  </Step>
  <Step title="Вебпошук">
    - Виберіть підтримуваного провайдера, наприклад Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG або Tavily (або пропустіть).
    - Провайдери з API можуть використовувати змінні середовища або наявну конфігурацію для швидкого налаштування; провайдери без ключів використовують натомість власні передумови.
    - Пропустити: `--skip-search`.
    - Налаштувати пізніше: `openclaw configure --section web`.
  </Step>
  <Step title="Встановлення демона">
    - macOS: LaunchAgent
      - Потрібна сесія користувача, що увійшов у систему; для headless використовуйте власний LaunchDaemon (не постачається).
    - Linux (і Windows через WSL2): systemd user unit
      - Онбординг намагається ввімкнути lingering через `loginctl enable-linger <user>`, щоб Gateway залишався активним після виходу із системи.
      - Може запросити sudo (записує в `/var/lib/systemd/linger`); спочатку пробує без sudo.
    - **Вибір runtime:** Node (рекомендовано; потрібен для WhatsApp/Telegram). Bun **не рекомендовано**.
    - Якщо автентифікація token вимагає token, а `gateway.auth.token` керується через SecretRef, встановлення демона перевіряє його, але не зберігає розв’язані значення token у відкритому тексті в метаданих середовища служби супервізора.
    - Якщо автентифікація token вимагає token, а налаштований token SecretRef не розв’язується, встановлення демона блокується з практичними вказівками.
    - Якщо налаштовано і `gateway.auth.token`, і `gateway.auth.password`, а `gateway.auth.mode` не задано, встановлення демона блокується, доки режим не буде задано явно.
  </Step>
  <Step title="Перевірка стану">
    - Запускає Gateway (за потреби) і виконує `openclaw health`.
    - Порада: `openclaw status --deep` додає live-probe стану Gateway до виводу статусу, зокрема probe каналів, коли це підтримується (потрібен доступний Gateway).
  </Step>
  <Step title="Skills (рекомендовано)">
    - Зчитує доступні Skills і перевіряє вимоги.
    - Дає змогу вибрати менеджер Node: **npm / pnpm** (bun не рекомендовано).
    - Встановлює необов’язкові залежності (деякі використовують Homebrew на macOS).
  </Step>
  <Step title="Завершення">
    - Підсумок + наступні кроки, зокрема застосунки iOS/Android/macOS для додаткових можливостей.
  </Step>
</Steps>

<Note>
Якщо GUI не виявлено, онбординг виводить інструкції з SSH port-forward для Control UI замість відкриття браузера.
Якщо ресурси Control UI відсутні, онбординг намагається їх зібрати; резервний варіант — `pnpm ui:build` (автоматично встановлює залежності UI).
</Note>

## Неінтерактивний режим

Використовуйте `--non-interactive`, щоб автоматизувати або скриптувати онбординг:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Додайте `--json` для машинозчитуваного підсумку.

Gateway token SecretRef у неінтерактивному режимі:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` і `--gateway-token-ref-env` взаємовиключні.

<Note>
`--json` **не** означає неінтерактивний режим. Для скриптів використовуйте `--non-interactive` (і `--workspace`).
</Note>

Командні приклади для конкретних провайдерів наведено в [Автоматизація CLI](/uk/start/wizard-cli-automation#provider-specific-examples).
Використовуйте цю довідкову сторінку для семантики прапорців і порядку кроків.

### Додати агента (неінтерактивно)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## RPC майстра Gateway

Gateway надає процес онбордингу через RPC (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
Клієнти (застосунок macOS, Control UI) можуть відображати кроки без повторної реалізації логіки онбордингу.

## Налаштування Signal (signal-cli)

Онбординг може встановити `signal-cli` з GitHub releases:

- Завантажує відповідний release asset.
- Зберігає його в `~/.openclaw/tools/signal-cli/<version>/`.
- Записує `channels.signal.cliPath` у вашу конфігурацію.

Примітки:

- Збірки JVM вимагають **Java 21**.
- Нативні збірки використовуються, коли вони доступні.
- Windows використовує WSL2; встановлення signal-cli виконується за Linux-сценарієм усередині WSL.

## Що записує майстер

Типові поля в `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (якщо вибрано Minimax)
- `tools.profile` (локальний онбординг за замовчуванням встановлює `"coding"`, якщо значення не задано; наявні явно вказані значення зберігаються)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (деталі поведінки: [Довідник із налаштування CLI](/uk/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Списки дозволених каналів (Slack/Discord/Matrix/Microsoft Teams), якщо ви погоджуєтеся на це під час підказок (імена за можливості зіставляються з ID).
- `skills.install.nodeManager`
  - `setup --node-manager` приймає `npm`, `pnpm` або `bun`.
  - У ручній конфігурації все ще можна використовувати `yarn`, безпосередньо встановивши `skills.install.nodeManager`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` записує `agents.list[]` і необов’язкові `bindings`.

Облікові дані WhatsApp зберігаються в `~/.openclaw/credentials/whatsapp/<accountId>/`.
Сесії зберігаються в `~/.openclaw/agents/<agentId>/sessions/`.

Деякі канали постачаються як Plugin. Коли ви вибираєте один із них під час налаштування, онбординг
запропонує встановити його (npm або локальний шлях), перш ніж його можна буде налаштувати.

## Пов’язана документація

- Огляд онбордингу: [Онбординг (CLI)](/uk/start/wizard)
- Онбординг застосунку macOS: [Онбординг](/uk/start/onboarding)
- Довідник із конфігурації: [Конфігурація Gateway](/uk/gateway/configuration)
- Провайдери: [WhatsApp](/uk/channels/whatsapp), [Telegram](/uk/channels/telegram), [Discord](/uk/channels/discord), [Google Chat](/uk/channels/googlechat), [Signal](/uk/channels/signal), [BlueBubbles](/uk/channels/bluebubbles) (iMessage), [iMessage](/uk/channels/imessage) (застаріле)
- Skills: [Skills](/uk/tools/skills), [Конфігурація Skills](/uk/tools/skills-config)
