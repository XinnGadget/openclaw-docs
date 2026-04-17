---
read_when:
    - Вам потрібен надійний резервний варіант, коли API-провайдери не працюють.
    - Ви використовуєте Codex CLI або інші локальні AI CLI і хочете використовувати їх повторно.
    - Ви хочете зрозуміти міст MCP local loopback для доступу інструментів до бекенду CLI.
summary: 'Бекенди CLI: локальний резервний CLI для AI з необов’язковим мостом інструментів MCP'
title: Бекенди CLI
x-i18n:
    generated_at: "2026-04-16T16:34:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 381273532a8622bc4628000a6fb999712b12af08faade2b5f2b7ac4cc7d23efe
    source_path: gateway/cli-backends.md
    workflow: 15
---

# Бекенди CLI (резервне середовище виконання)

OpenClaw може запускати **локальні AI CLI** як **резервний варіант лише для тексту**, коли API-провайдери недоступні,
обмежені за частотою запитів або тимчасово працюють некоректно. Це навмисно консервативний режим:

- **Інструменти OpenClaw не інжектуються напряму**, але бекенди з `bundleMcp: true`
  можуть отримувати інструменти gateway через міст MCP local loopback.
- **Потокова передача JSONL** для CLI, які її підтримують.
- **Сесії підтримуються** (тож наступні ходи залишаються узгодженими).
- **Зображення можна передавати далі**, якщо CLI приймає шляхи до зображень.

Це задумано як **страхувальний механізм**, а не як основний шлях. Використовуйте це, коли вам
потрібні текстові відповіді у стилі «завжди працює» без залежності від зовнішніх API.

Якщо вам потрібне повноцінне середовище виконання harness із керуванням сесіями ACP, фоновими завданнями,
прив’язкою до потоку/розмови та постійними зовнішніми coding sessions, використовуйте
[ACP Agents](/uk/tools/acp-agents). Бекенди CLI — це не ACP.

## Швидкий старт для початківців

Ви можете використовувати Codex CLI **без жодної конфігурації** (вбудований плагін OpenAI
реєструє стандартний бекенд):

```bash
openclaw agent --message "hi" --model codex-cli/gpt-5.4
```

Якщо ваш gateway працює під launchd/systemd і `PATH` мінімальний, додайте лише
шлях до команди:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
      },
    },
  },
}
```

І все. Жодних ключів, жодної додаткової конфігурації автентифікації, окрім самої CLI.

Якщо ви використовуєте вбудований бекенд CLI як **основного провайдера повідомлень** на
хості gateway, OpenClaw тепер автоматично завантажує відповідний вбудований Plugin, коли ваша конфігурація
явно посилається на цей бекенд у посиланні на модель або в
`agents.defaults.cliBackends`.

## Використання як резервного варіанту

Додайте бекенд CLI до списку резервних, щоб він запускався лише тоді, коли основні моделі не працюють:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["codex-cli/gpt-5.4"],
      },
      models: {
        "anthropic/claude-opus-4-6": { alias: "Opus" },
        "codex-cli/gpt-5.4": {},
      },
    },
  },
}
```

Примітки:

- Якщо ви використовуєте `agents.defaults.models` (allowlist), ви також маєте включити туди моделі вашого бекенду CLI.
- Якщо основний провайдер не працює (автентифікація, обмеження частоти запитів, тайм-аути), OpenClaw
  спробує використати бекенд CLI далі.

## Огляд конфігурації

Усі бекенди CLI знаходяться в:

```
agents.defaults.cliBackends
```

Кожен запис має ключ у вигляді **ідентифікатора провайдера** (наприклад, `codex-cli`, `my-cli`).
Ідентифікатор провайдера стає лівою частиною посилання на модель:

```
<provider>/<model>
```

### Приклад конфігурації

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "codex-cli": {
          command: "/opt/homebrew/bin/codex",
        },
        "my-cli": {
          command: "my-cli",
          args: ["--json"],
          output: "json",
          input: "arg",
          modelArg: "--model",
          modelAliases: {
            "claude-opus-4-6": "opus",
            "claude-sonnet-4-6": "sonnet",
          },
          sessionArg: "--session",
          sessionMode: "existing",
          sessionIdFields: ["session_id", "conversation_id"],
          systemPromptArg: "--system",
          // CLI у стилі Codex можуть натомість вказувати на файл prompt:
          // systemPromptFileConfigArg: "-c",
          // systemPromptFileConfigKey: "model_instructions_file",
          systemPromptWhen: "first",
          imageArg: "--image",
          imageMode: "repeat",
          serialize: true,
        },
      },
    },
  },
}
```

## Як це працює

1. **Вибирає бекенд** на основі префікса провайдера (`codex-cli/...`).
2. **Формує system prompt** з використанням того самого prompt OpenClaw і контексту workspace.
3. **Виконує CLI** з ідентифікатором сесії (якщо підтримується), щоб історія залишалася узгодженою.
4. **Розбирає вивід** (JSON або звичайний текст) і повертає фінальний текст.
5. **Зберігає ідентифікатори сесій** для кожного бекенду, щоб наступні запити повторно використовували ту саму CLI-сесію.

<Note>
Вбудований бекенд Anthropic `claude-cli` знову підтримується. Співробітники Anthropic
повідомили нам, що використання Claude CLI у стилі OpenClaw знову дозволене, тому OpenClaw розглядає
використання `claude -p` як санкціоноване для цієї інтеграції, якщо Anthropic не опублікує
нову політику.
</Note>

Вбудований бекенд OpenAI `codex-cli` передає system prompt OpenClaw через
перевизначення конфігурації `model_instructions_file` у Codex (`-c
model_instructions_file="..."`). Codex не надає прапора у стилі Claude
`--append-system-prompt`, тому OpenClaw записує зібраний prompt у
тимчасовий файл для кожної нової сесії Codex CLI.

Вбудований бекенд Anthropic `claude-cli` отримує знімок Skills OpenClaw
двома способами: компактний каталог Skills OpenClaw у доданому system prompt і
тимчасовий плагін Claude Code, переданий через `--plugin-dir`. Плагін містить
лише ті Skills, які дозволені для цього агента/сесії, тому вбудований
механізм визначення skill у Claude Code бачить той самий відфільтрований набір, який OpenClaw інакше рекламував би в prompt.
Перевизначення skill env/API key, як і раніше, застосовуються OpenClaw до середовища дочірнього процесу під час запуску.

## Сесії

- Якщо CLI підтримує сесії, задайте `sessionArg` (наприклад, `--session-id`) або
  `sessionArgs` (з плейсхолдером `{sessionId}`), коли ID потрібно вставити
  в кілька прапорів.
- Якщо CLI використовує **підкоманду resume** з іншими прапорами, задайте
  `resumeArgs` (замінює `args` під час відновлення) і за потреби `resumeOutput`
  (для відновлення без JSON).
- `sessionMode`:
  - `always`: завжди надсилати ідентифікатор сесії (новий UUID, якщо нічого не збережено).
  - `existing`: надсилати ідентифікатор сесії лише якщо його вже було збережено.
  - `none`: ніколи не надсилати ідентифікатор сесії.

Примітки щодо серіалізації:

- `serialize: true` зберігає впорядкованість запусків на одній смузі.
- Більшість CLI серіалізуються в межах однієї смуги провайдера.
- OpenClaw скидає повторне використання збереженої CLI-сесії, коли змінюється стан автентифікації бекенду, зокрема під час повторного входу, ротації токена або зміни облікових даних профілю автентифікації.

## Зображення (pass-through)

Якщо ваша CLI приймає шляхи до зображень, задайте `imageArg`:

```json5
imageArg: "--image",
imageMode: "repeat"
```

OpenClaw записуватиме base64-зображення у тимчасові файли. Якщо `imageArg` задано, ці
шляхи передаються як аргументи CLI. Якщо `imageArg` відсутній, OpenClaw додає
шляхи до файлів у prompt (інжекція шляху), чого достатньо для CLI, які автоматично
завантажують локальні файли зі звичайних шляхів.

## Входи / виходи

- `output: "json"` (типово) намагається розібрати JSON і витягти текст + ідентифікатор сесії.
- Для JSON-виводу Gemini CLI OpenClaw читає текст відповіді з `response`, а
  usage — з `stats`, коли `usage` відсутній або порожній.
- `output: "jsonl"` розбирає потоки JSONL (наприклад, Codex CLI `--json`) і витягує фінальне повідомлення агента та ідентифікатори сесії,
  якщо вони присутні.
- `output: "text"` обробляє stdout як фінальну відповідь.

Режими введення:

- `input: "arg"` (типово) передає prompt як останній аргумент CLI.
- `input: "stdin"` надсилає prompt через stdin.
- Якщо prompt дуже довгий і задано `maxPromptArgChars`, використовується stdin.

## Типові значення (належать Plugin)

Вбудований Plugin OpenAI також реєструє типові значення для `codex-cli`:

- `command: "codex"`
- `args: ["exec","--json","--color","never","--sandbox","workspace-write","--skip-git-repo-check"]`
- `resumeArgs: ["exec","resume","{sessionId}","-c","sandbox_mode=\"workspace-write\"","--skip-git-repo-check"]`
- `output: "jsonl"`
- `resumeOutput: "text"`
- `modelArg: "--model"`
- `imageArg: "--image"`
- `sessionMode: "existing"`

Вбудований Plugin Google також реєструє типові значення для `google-gemini-cli`:

- `command: "gemini"`
- `args: ["--output-format", "json", "--prompt", "{prompt}"]`
- `resumeArgs: ["--resume", "{sessionId}", "--output-format", "json", "--prompt", "{prompt}"]`
- `imageArg: "@"`
- `imagePathScope: "workspace"`
- `modelArg: "--model"`
- `sessionMode: "existing"`
- `sessionIdFields: ["session_id", "sessionId"]`

Передумова: локальна Gemini CLI має бути встановлена й доступна як
`gemini` у `PATH` (`brew install gemini-cli` або
`npm install -g @google/gemini-cli`).

Примітки щодо JSON Gemini CLI:

- Текст відповіді читається з поля JSON `response`.
- Usage береться з `stats`, якщо `usage` відсутній або порожній.
- `stats.cached` нормалізується в OpenClaw `cacheRead`.
- Якщо `stats.input` відсутній, OpenClaw обчислює вхідні токени з
  `stats.input_tokens - stats.cached`.

Перевизначайте лише за потреби (типовий випадок: абсолютний шлях `command`).

## Типові значення, що належать Plugin

Типові значення бекенду CLI тепер є частиною поверхні Plugin:

- Plugins реєструють їх через `api.registerCliBackend(...)`.
- `id` бекенду стає префіксом провайдера в посиланнях на модель.
- Конфігурація користувача в `agents.defaults.cliBackends.<id>` як і раніше перевизначає типове значення Plugin.
- Очищення конфігурації, специфічне для бекенду, залишається відповідальністю Plugin через необов’язковий
  хук `normalizeConfig`.

Plugins, яким потрібні невеликі compatibility shims для prompt/повідомлень, можуть оголошувати
двонапрямні текстові перетворення без заміни провайдера або бекенду CLI:

```typescript
api.registerTextTransforms({
  input: [
    { from: /red basket/g, to: "blue basket" },
    { from: /paper ticket/g, to: "digital ticket" },
    { from: /left shelf/g, to: "right shelf" },
  ],
  output: [
    { from: /blue basket/g, to: "red basket" },
    { from: /digital ticket/g, to: "paper ticket" },
    { from: /right shelf/g, to: "left shelf" },
  ],
});
```

`input` переписує system prompt і prompt користувача, що передаються до CLI. `output`
переписує потокові дельти помічника і розібраний фінальний текст до того, як OpenClaw обробить
власні службові маркери та доставку в канал.

Для CLI, які видають JSONL, сумісний із Claude Code stream-json, задайте
`jsonlDialect: "claude-stream-json"` у конфігурації цього бекенду.

## Bundle MCP overlays

Бекенди CLI **не** отримують виклики інструментів OpenClaw напряму, але бекенд може
увімкнути згенерований MCP config overlay через `bundleMcp: true`.

Поточна вбудована поведінка:

- `claude-cli`: згенерований строгий файл конфігурації MCP
- `codex-cli`: вбудовані перевизначення конфігурації для `mcp_servers`
- `google-gemini-cli`: згенерований файл системних налаштувань Gemini

Коли bundle MCP увімкнено, OpenClaw:

- запускає loopback HTTP MCP-сервер, який надає інструменти gateway процесу CLI
- автентифікує міст за допомогою токена на сесію (`OPENCLAW_MCP_TOKEN`)
- обмежує доступ до інструментів поточною сесією, обліковим записом і контекстом каналу
- завантажує увімкнені bundle-MCP сервери для поточного workspace
- об’єднує їх з будь-якою наявною формою MCP-конфігурації/налаштувань бекенду
- переписує конфігурацію запуску, використовуючи режим інтеграції, що належить бекенду, з відповідного extension

Якщо жодного MCP-сервера не увімкнено, OpenClaw усе одно інжектує строгу конфігурацію, коли
бекенд увімкнув bundle MCP, щоб фонові запуски залишалися ізольованими.

## Обмеження

- **Немає прямих викликів інструментів OpenClaw.** OpenClaw не інжектує виклики інструментів у
  протокол бекенду CLI. Бекенди бачать інструменти gateway лише коли вони увімкнули
  `bundleMcp: true`.
- **Потокова передача залежить від бекенду.** Деякі бекенди передають JSONL потоково, інші буферизують
  до завершення.
- **Структуровані виходи** залежать від JSON-формату CLI.
- **Сесії Codex CLI** відновлюються через текстовий вивід (без JSONL), що менш
  структуровано, ніж початковий запуск `--json`. Сесії OpenClaw при цьому все одно працюють
  нормально.

## Усунення неполадок

- **CLI не знайдено**: задайте `command` як повний шлях.
- **Неправильна назва моделі**: використовуйте `modelAliases`, щоб зіставити `provider/model` → модель CLI.
- **Немає безперервності сесії**: переконайтеся, що задано `sessionArg` і `sessionMode` не дорівнює
  `none` (Codex CLI наразі не може відновлюватися з JSON-виводом).
- **Зображення ігноруються**: задайте `imageArg` (і переконайтеся, що CLI підтримує шляхи до файлів).
