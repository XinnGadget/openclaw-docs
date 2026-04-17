---
read_when:
    - Ви хочете використовувати вбудований каркас app-server Codex
    - Вам потрібні посилання на моделі Codex і приклади конфігурації
    - Ви хочете вимкнути резервний перехід на Pi для розгортань лише з Codex
summary: Запускайте вбудовані ходи агента OpenClaw через вбудований каркас app-server Codex
title: Каркас Codex
x-i18n:
    generated_at: "2026-04-10T23:15:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e1dcf4f1a00c63c3ef31d72feac44bce255421c032c58fa4fd67295b3daf23
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Каркас Codex

Вбудований плагін `codex` дає OpenClaw змогу запускати вбудовані ходи агента через
app-server Codex замість вбудованого каркаса PI.

Використовуйте це, коли хочете, щоб Codex керував низькорівневою сесією агента: виявленням
моделей, нативним відновленням потоку, нативною компакцією та виконанням через app-server.
OpenClaw і надалі керує каналами чату, файлами сесій, вибором моделі, інструментами,
погодженнями, доставкою медіа та видимим дзеркалом стенограми.

Цей каркас вимкнений за замовчуванням. Його буде вибрано лише тоді, коли плагін `codex`
увімкнений і розв’язана модель є моделлю `codex/*`, або коли ви явно примусово задаєте
`embeddedHarness.runtime: "codex"` чи `OPENCLAW_AGENT_RUNTIME=codex`.
Якщо ви ніколи не налаштовуєте `codex/*`, наявні запуски PI, OpenAI, Anthropic, Gemini, local
і custom-provider зберігають свою поточну поведінку.

## Виберіть правильний префікс моделі

OpenClaw має окремі маршрути для доступу у стилі OpenAI і Codex:

| Посилання на модель | Шлях середовища виконання                   | Використовуйте, коли                                                        |
| ------------------- | ------------------------------------------- | --------------------------------------------------------------------------- |
| `openai/gpt-5.4`    | Провайдер OpenAI через конвеєр OpenClaw/PI  | Вам потрібен прямий доступ до API OpenAI Platform з `OPENAI_API_KEY`.       |
| `openai-codex/gpt-5.4` | Провайдер OpenAI Codex OAuth через PI    | Вам потрібен ChatGPT/Codex OAuth без каркаса app-server Codex.              |
| `codex/gpt-5.4`     | Вбудований провайдер Codex плюс каркас Codex | Вам потрібне нативне виконання через app-server Codex для вбудованого ходу агента. |

Каркас Codex обробляє лише посилання на моделі `codex/*`. Наявні посилання `openai/*`,
`openai-codex/*`, Anthropic, Gemini, xAI, local і custom provider зберігають
свої звичайні шляхи.

## Вимоги

- OpenClaw із доступним вбудованим плагіном `codex`.
- app-server Codex версії `0.118.0` або новішої.
- Доступна автентифікація Codex для процесу app-server.

Плагін блокує старіші або неверсіоновані узгодження app-server. Це утримує
OpenClaw на поверхні протоколу, з якою його було протестовано.

Для живих і Docker smoke-тестів автентифікація зазвичай надходить із `OPENAI_API_KEY`, а також
з необов’язкових файлів Codex CLI, таких як `~/.codex/auth.json` і
`~/.codex/config.toml`. Використовуйте ті самі автентифікаційні матеріали, які використовує
ваш локальний app-server Codex.

## Мінімальна конфігурація

Використовуйте `codex/gpt-5.4`, увімкніть вбудований плагін і примусово задайте каркас `codex`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Якщо ваша конфігурація використовує `plugins.allow`, додайте туди також `codex`:

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Установлення `agents.defaults.model` або моделі агента в `codex/<model>` також
автоматично вмикає вбудований плагін `codex`. Явний запис плагіна все одно
корисний у спільних конфігураціях, оскільки робить намір розгортання очевидним.

## Додайте Codex без заміни інших моделей

Залиште `runtime: "auto"`, якщо хочете використовувати Codex для моделей `codex/*`, а PI для
всього іншого:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

Із такою структурою:

- `/model codex` або `/model codex/gpt-5.4` використовує каркас app-server Codex.
- `/model gpt` або `/model openai/gpt-5.4` використовує шлях провайдера OpenAI.
- `/model opus` використовує шлях провайдера Anthropic.
- Якщо вибрано не-Codex модель, PI залишається каркасом сумісності.

## Розгортання лише з Codex

Вимкніть резервний перехід на PI, якщо вам потрібно підтвердити, що кожен вбудований хід агента використовує
каркас Codex:

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Перевизначення через середовище:

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Якщо резервний перехід вимкнено, OpenClaw завершується з помилкою на ранньому етапі, якщо плагін Codex вимкнено,
потрібна модель не є посиланням `codex/*`, app-server надто старий або
app-server не може запуститися.

## Codex для окремого агента

Ви можете зробити одного агента лише для Codex, тоді як агент за замовчуванням зберігатиме звичайний
автовибір:

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

Використовуйте звичайні команди сесії, щоб перемикати агентів і моделі. `/new` створює нову
сесію OpenClaw, а каркас Codex за потреби створює або відновлює свій побічний потік app-server.
`/reset` очищає прив’язку сесії OpenClaw для цього потоку.

## Виявлення моделей

За замовчуванням плагін Codex запитує app-server про доступні моделі. Якщо
виявлення завершується помилкою або перевищує час очікування, використовується вбудований резервний каталог:

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

Ви можете налаштувати виявлення в `plugins.entries.codex.config.discovery`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

Вимкніть виявлення, якщо хочете, щоб під час запуску не виконувалася перевірка Codex і використовувався
резервний каталог:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## Підключення до app-server і політика

За замовчуванням плагін локально запускає Codex так:

```bash
codex app-server --listen stdio://
```

Ви можете залишити це значення за замовчуванням і налаштувати лише нативну політику Codex:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            sandbox: "workspace-write",
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Для вже запущеного app-server використовуйте транспорт WebSocket:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://127.0.0.1:39175",
            authToken: "${CODEX_APP_SERVER_TOKEN}",
            requestTimeoutMs: 60000,
          },
        },
      },
    },
  },
}
```

Підтримувані поля `appServer`:

| Поле                | За замовчуванням                         | Значення                                                                  |
| ------------------- | ---------------------------------------- | ------------------------------------------------------------------------- |
| `transport`         | `"stdio"`                                | `"stdio"` запускає Codex; `"websocket"` підключається до `url`.           |
| `command`           | `"codex"`                                | Виконуваний файл для транспорту stdio.                                    |
| `args`              | `["app-server", "--listen", "stdio://"]` | Аргументи для транспорту stdio.                                           |
| `url`               | unset                                    | URL WebSocket app-server.                                                 |
| `authToken`         | unset                                    | Bearer-токен для транспорту WebSocket.                                    |
| `headers`           | `{}`                                     | Додаткові заголовки WebSocket.                                            |
| `requestTimeoutMs`  | `60000`                                  | Час очікування для викликів площини керування app-server.                 |
| `approvalPolicy`    | `"never"`                                | Нативна політика погодження Codex, що надсилається до start/resume/turn потоку. |
| `sandbox`           | `"workspace-write"`                      | Нативний режим sandbox Codex, що надсилається до start/resume потоку.     |
| `approvalsReviewer` | `"user"`                                 | Використовуйте `"guardian_subagent"`, щоб нативні погодження переглядав guardian Codex. |
| `serviceTier`       | unset                                    | Необов’язковий рівень сервісу Codex, наприклад `"priority"`.              |

Старі змінні середовища все ще працюють як резервні значення для локального тестування, коли
відповідне поле конфігурації не задане:

- `OPENCLAW_CODEX_APP_SERVER_BIN`
- `OPENCLAW_CODEX_APP_SERVER_ARGS`
- `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY`
- `OPENCLAW_CODEX_APP_SERVER_SANDBOX`
- `OPENCLAW_CODEX_APP_SERVER_GUARDIAN=1`

Для відтворюваних розгортань перевага надається конфігурації.

## Поширені рецепти

Локальний Codex із типовим транспортом stdio:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Перевірка каркаса лише Codex, із вимкненим резервним переходом на PI:

```json5
{
  embeddedHarness: {
    fallback: "none",
  },
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Погодження Codex із переглядом guardian:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            approvalsReviewer: "guardian_subagent",
            sandbox: "workspace-write",
          },
        },
      },
    },
  },
}
```

Віддалений app-server із явними заголовками:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://gateway-host:39175",
            headers: {
              "X-OpenClaw-Agent": "main",
            },
          },
        },
      },
    },
  },
}
```

Перемикання моделей і далі контролює OpenClaw. Коли сесію OpenClaw прив’язано
до наявного потоку Codex, наступний хід знову надсилає до
app-server поточні вибрані `codex/*` модель, провайдера, політику погодження, sandbox і service tier.
Перемикання з `codex/gpt-5.4` на `codex/gpt-5.2` зберігає прив’язку
до потоку, але просить Codex продовжити з нововибраною моделлю.

## Команда Codex

Вбудований плагін реєструє `/codex` як авторизовану slash-команду. Вона є
загальною і працює в будь-якому каналі, який підтримує текстові команди OpenClaw.

Поширені форми:

- `/codex status` показує живе підключення до app-server, моделі, обліковий запис, ліміти швидкості, сервери MCP і Skills.
- `/codex models` перелічує живі моделі app-server Codex.
- `/codex threads [filter]` перелічує нещодавні потоки Codex.
- `/codex resume <thread-id>` прив’язує поточну сесію OpenClaw до наявного потоку Codex.
- `/codex compact` просить app-server Codex виконати компакцію прив’язаного потоку.
- `/codex review` запускає нативну перевірку Codex для прив’язаного потоку.
- `/codex account` показує стан облікового запису та лімітів швидкості.
- `/codex mcp` перелічує стан серверів MCP app-server Codex.
- `/codex skills` перелічує Skills app-server Codex.

`/codex resume` записує той самий файл побічної прив’язки, який каркас використовує для
звичайних ходів. У наступному повідомленні OpenClaw відновлює цей потік Codex, передає поточну
вибрану в OpenClaw модель `codex/*` до app-server і зберігає ввімкнену
розширену історію.

Поверхня команд вимагає app-server Codex версії `0.118.0` або новішої. Для окремих
методів керування буде показано `unsupported by this Codex app-server`, якщо
майбутній або кастомний app-server не надає цей метод JSON-RPC.

## Інструменти, медіа та компакція

Каркас Codex змінює лише низькорівневий виконавець вбудованого агента.

OpenClaw, як і раніше, формує список інструментів і отримує динамічні результати інструментів від
каркаса. Текст, зображення, відео, музика, TTS, погодження та вивід інструментів обміну повідомленнями
і далі проходять через звичайний шлях доставки OpenClaw.

Коли вибрана модель використовує каркас Codex, нативна компакція потоку делегується app-server Codex.
OpenClaw зберігає дзеркало стенограми для історії каналу, пошуку, `/new`, `/reset` і майбутнього
перемикання моделі або каркаса. Дзеркало включає запит користувача, фінальний текст помічника та
полегшені записи міркувань або плану Codex, коли app-server їх надсилає.

Генерація медіа не потребує PI. Генерація зображень, відео, музики, PDF, TTS і
аналіз медіа й надалі використовують відповідні налаштування провайдера/моделі, такі як
`agents.defaults.imageGenerationModel`, `videoGenerationModel`, `pdfModel` і
`messages.tts`.

## Усунення несправностей

**Codex не з’являється в `/model`:** увімкніть `plugins.entries.codex.enabled`,
задайте посилання на модель `codex/*` або перевірте, чи не виключає `plugins.allow` `codex`.

**OpenClaw переходить на PI:** установіть `embeddedHarness.fallback: "none"` або
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` під час тестування.

**app-server відхиляється:** оновіть Codex, щоб узгодження app-server
повідомляло версію `0.118.0` або новішу.

**Виявлення моделей повільне:** зменште `plugins.entries.codex.config.discovery.timeoutMs`
або вимкніть виявлення.

**Транспорт WebSocket одразу завершується з помилкою:** перевірте `appServer.url`, `authToken`
і що віддалений app-server використовує ту саму версію протоколу app-server Codex.

**Не-Codex модель використовує PI:** це очікувана поведінка. Каркас Codex обробляє лише
посилання на моделі `codex/*`.

## Пов’язане

- [Плагіни каркаса агента](/uk/plugins/sdk-agent-harness)
- [Провайдери моделей](/uk/concepts/model-providers)
- [Довідник із конфігурації](/uk/gateway/configuration-reference)
- [Тестування](/uk/help/testing#live-codex-app-server-harness-smoke)
