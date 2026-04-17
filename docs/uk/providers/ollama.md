---
read_when:
    - Ви хочете запустити OpenClaw із хмарними або локальними моделями через Ollama
    - Вам потрібні вказівки щодо налаштування та конфігурації Ollama
summary: Запустіть OpenClaw з Ollama (хмарні та локальні моделі)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:08:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw інтегрується з нативним API Ollama (`/api/chat`) для розміщених хмарних моделей і локальних/самостійно розміщених серверів Ollama. Ви можете використовувати Ollama у трьох режимах: `Cloud + Local` через доступний хост Ollama, `Cloud only` через `https://ollama.com` або `Local only` через доступний хост Ollama.

<Warning>
**Користувачі віддаленого Ollama**: Не використовуйте OpenAI-сумісний URL `/v1` (`http://host:11434/v1`) з OpenClaw. Це порушує виклик інструментів, і моделі можуть виводити сирий JSON інструментів як звичайний текст. Натомість використовуйте URL нативного API Ollama: `baseUrl: "http://host:11434"` (без `/v1`).
</Warning>

## Початок роботи

Виберіть бажаний спосіб налаштування та режим.

<Tabs>
  <Tab title="Онбординг (рекомендовано)">
    **Найкраще для:** найшвидшого способу налаштувати робочу хмарну або локальну конфігурацію Ollama.

    <Steps>
      <Step title="Запустіть онбординг">
        ```bash
        openclaw onboard
        ```

        Виберіть **Ollama** зі списку провайдерів.
      </Step>
      <Step title="Виберіть режим">
        - **Cloud + Local** — локальний хост Ollama плюс хмарні моделі, що маршрутизуються через цей хост
        - **Cloud only** — розміщені моделі Ollama через `https://ollama.com`
        - **Local only** — лише локальні моделі
      </Step>
      <Step title="Виберіть модель">
        `Cloud only` запитує `OLLAMA_API_KEY` і пропонує типові хмарні значення за замовчуванням. `Cloud + Local` і `Local only` запитують базовий URL Ollama, виявляють доступні моделі та автоматично завантажують вибрану локальну модель, якщо вона ще недоступна. `Cloud + Local` також перевіряє, чи виконано вхід на цьому хості Ollama для доступу до хмари.
      </Step>
      <Step title="Переконайтеся, що модель доступна">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Неінтерактивний режим

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    За потреби вкажіть власний базовий URL або модель:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Ручне налаштування">
    **Найкраще для:** повного контролю над хмарною або локальною конфігурацією.

    <Steps>
      <Step title="Виберіть хмарний або локальний режим">
        - **Cloud + Local**: встановіть Ollama, виконайте вхід через `ollama signin` і маршрутизуйте хмарні запити через цей хост
        - **Cloud only**: використовуйте `https://ollama.com` з `OLLAMA_API_KEY`
        - **Local only**: встановіть Ollama з [ollama.com/download](https://ollama.com/download)
      </Step>
      <Step title="Завантажте локальну модель (лише Local only)">
        ```bash
        ollama pull gemma4
        # або
        ollama pull gpt-oss:20b
        # або
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Увімкніть Ollama для OpenClaw">
        Для `Cloud only` використовуйте ваш справжній `OLLAMA_API_KEY`. Для конфігурацій на основі хоста підійде будь-яке значення-заповнювач:

        ```bash
        # Cloud
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Local-only
        export OLLAMA_API_KEY="ollama-local"

        # Або налаштуйте у своєму конфігураційному файлі
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Перегляньте та встановіть свою модель">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Або встановіть значення за замовчуванням у конфігурації:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Хмарні моделі

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` використовує доступний хост Ollama як точку керування і для локальних, і для хмарних моделей. Це рекомендований Ollama гібридний сценарій.

    Використовуйте **Cloud + Local** під час налаштування. OpenClaw запитує базовий URL Ollama, виявляє локальні моделі з цього хоста та перевіряє, чи виконано вхід на хості для доступу до хмари через `ollama signin`. Якщо на хості виконано вхід, OpenClaw також пропонує типові розміщені хмарні моделі, такі як `kimi-k2.5:cloud`, `minimax-m2.7:cloud` і `glm-5.1:cloud`.

    Якщо на хості ще не виконано вхід, OpenClaw залишає налаштування лише локальним, доки ви не виконаєте `ollama signin`.

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` працює через розміщений API Ollama за адресою `https://ollama.com`.

    Використовуйте **Cloud only** під час налаштування. OpenClaw запитує `OLLAMA_API_KEY`, встановлює `baseUrl: "https://ollama.com"` і заповнює список розміщених хмарних моделей. Цей шлях **не** потребує локального сервера Ollama або `ollama signin`.

  </Tab>

  <Tab title="Local only">
    У режимі лише локального використання OpenClaw виявляє моделі з налаштованого екземпляра Ollama. Цей шлях призначений для локальних або самостійно розміщених серверів Ollama.

    Наразі OpenClaw пропонує `gemma4` як локальну модель за замовчуванням.

  </Tab>
</Tabs>

## Виявлення моделей (неявний провайдер)

Коли ви встановлюєте `OLLAMA_API_KEY` (або профіль автентифікації) і **не** визначаєте `models.providers.ollama`, OpenClaw виявляє моделі з локального екземпляра Ollama за адресою `http://127.0.0.1:11434`.

| Поведінка            | Докладно                                                                                                                                                            |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Запит каталогу       | Виконує запити до `/api/tags`                                                                                                                                       |
| Визначення можливостей | Використовує найкращі зусилля для запитів `/api/show`, щоб зчитати `contextWindow` і визначити можливості (зокрема vision)                                         |
| Vision-моделі        | Моделі з можливістю `vision`, про яку повідомляє `/api/show`, позначаються як такі, що підтримують зображення (`input: ["text", "image"]`), тому OpenClaw автоматично додає зображення до запиту |
| Визначення reasoning | Позначає `reasoning` за евристикою назви моделі (`r1`, `reasoning`, `think`)                                                                                        |
| Ліміти токенів       | Встановлює `maxTokens` на типовий максимальний ліміт токенів Ollama, який використовує OpenClaw                                                                    |
| Вартість             | Встановлює всі вартості в `0`                                                                                                                                        |

Це дає змогу уникнути ручного додавання моделей, водночас зберігаючи каталог узгодженим із локальним екземпляром Ollama.

```bash
# Перегляньте, які моделі доступні
ollama list
openclaw models list
```

Щоб додати нову модель, просто завантажте її через Ollama:

```bash
ollama pull mistral
```

Нова модель буде автоматично виявлена та стане доступною для використання.

<Note>
Якщо ви явно задаєте `models.providers.ollama`, автоматичне виявлення пропускається, і ви маєте визначити моделі вручну. Дивіться розділ явної конфігурації нижче.
</Note>

## Конфігурація

<Tabs>
  <Tab title="Базова (неявне виявлення)">
    Найпростіший спосіб увімкнути режим лише локального використання — через змінну середовища:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    Якщо `OLLAMA_API_KEY` встановлено, ви можете не вказувати `apiKey` у записі провайдера, і OpenClaw підставить його для перевірок доступності.
    </Tip>

  </Tab>

  <Tab title="Явна (ручні моделі)">
    Використовуйте явну конфігурацію, якщо вам потрібне розміщене хмарне налаштування, Ollama працює на іншому хості або порту, ви хочете примусово задати конкретні контекстні вікна чи списки моделей, або вам потрібні повністю ручні визначення моделей.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="Власний базовий URL">
    Якщо Ollama працює на іншому хості або порту (явна конфігурація вимикає автоматичне виявлення, тому моделі потрібно визначати вручну):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // Без /v1 - використовуйте URL нативного API Ollama
            api: "ollama", // Вкажіть явно, щоб гарантувати нативну поведінку виклику інструментів
          },
        },
      },
    }
    ```

    <Warning>
    Не додавайте `/v1` до URL. Шлях `/v1` використовує OpenAI-сумісний режим, у якому виклик інструментів ненадійний. Використовуйте базовий URL Ollama без суфікса шляху.
    </Warning>

  </Tab>
</Tabs>

### Вибір моделі

Після налаштування всі ваші моделі Ollama будуть доступні:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Вебпошук Ollama

OpenClaw підтримує **Вебпошук Ollama** як вбудований провайдер `web_search`.

| Властивість | Докладно                                                                                                          |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| Хост        | Використовує налаштований хост Ollama (`models.providers.ollama.baseUrl`, якщо задано, інакше `http://127.0.0.1:11434`) |
| Автентифікація | Без ключа                                                                                                      |
| Вимога      | Ollama має працювати, і в ньому має бути виконано вхід через `ollama signin`                                     |

Виберіть **Ollama Web Search** під час `openclaw onboard` або `openclaw configure --section web`, або встановіть:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Повні відомості про налаштування та поведінку дивіться в [Ollama Web Search](/uk/tools/ollama-search).
</Note>

## Розширена конфігурація

<AccordionGroup>
  <Accordion title="Застарілий OpenAI-сумісний режим">
    <Warning>
    **Виклик інструментів ненадійний в OpenAI-сумісному режимі.** Використовуйте цей режим лише якщо вам потрібен формат OpenAI для проксі й ви не залежите від нативної поведінки виклику інструментів.
    </Warning>

    Якщо вам потрібно використовувати OpenAI-сумісну кінцеву точку замість цього (наприклад, за проксі, який підтримує лише формат OpenAI), явно встановіть `api: "openai-completions"`:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // за замовчуванням: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Цей режим може не підтримувати одночасно потокову передачу та виклик інструментів. Можливо, вам доведеться вимкнути потокову передачу за допомогою `params: { streaming: false }` у конфігурації моделі.

    Коли `api: "openai-completions"` використовується з Ollama, OpenClaw за замовчуванням додає `options.num_ctx`, щоб Ollama не переходив непомітно до контекстного вікна 4096. Якщо ваш проксі або upstream відхиляє невідомі поля `options`, вимкніть цю поведінку:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Контекстні вікна">
    Для автоматично виявлених моделей OpenClaw використовує контекстне вікно, про яке повідомляє Ollama, якщо воно доступне; інакше використовується типове контекстне вікно Ollama, яке застосовує OpenClaw.

    Ви можете перевизначити `contextWindow` і `maxTokens` у явній конфігурації провайдера:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Моделі reasoning">
    OpenClaw за замовчуванням вважає моделі з назвами на кшталт `deepseek-r1`, `reasoning` або `think` такими, що підтримують reasoning.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Жодна додаткова конфігурація не потрібна — OpenClaw позначає їх автоматично.

  </Accordion>

  <Accordion title="Вартість моделей">
    Ollama є безкоштовним і працює локально, тому для всіх моделей вартість встановлено в $0. Це стосується як автоматично виявлених, так і вручну визначених моделей.
  </Accordion>

  <Accordion title="Ембедінги пам’яті">
    Вбудований Plugin Ollama реєструє провайдера ембедінгів пам’яті для
    [пошуку в пам’яті](/uk/concepts/memory). Він використовує налаштований базовий URL Ollama
    та API-ключ.

    | Властивість   | Значення            |
    | ------------- | ------------------- |
    | Типова модель | `nomic-embed-text`  |
    | Автозавантаження | Так — модель ембедінгів автоматично завантажується, якщо її немає локально |

    Щоб вибрати Ollama як провайдера ембедінгів для пошуку в пам’яті:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Конфігурація потокової передачі">
    Інтеграція Ollama в OpenClaw за замовчуванням використовує **нативний API Ollama** (`/api/chat`), який повністю підтримує одночасно потокову передачу та виклик інструментів. Жодна спеціальна конфігурація не потрібна.

    <Tip>
    Якщо вам потрібно використовувати OpenAI-сумісну кінцеву точку, дивіться розділ "Застарілий OpenAI-сумісний режим" вище. У цьому режимі потокова передача та виклик інструментів можуть не працювати одночасно.
    </Tip>

  </Accordion>
</AccordionGroup>

## Усунення несправностей

<AccordionGroup>
  <Accordion title="Ollama не виявлено">
    Переконайтеся, що Ollama запущено, що ви встановили `OLLAMA_API_KEY` (або профіль автентифікації), і що ви **не** визначили явний запис `models.providers.ollama`:

    ```bash
    ollama serve
    ```

    Переконайтеся, що API доступний:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Немає доступних моделей">
    Якщо вашу модель не вказано у списку, або завантажте її локально, або явно визначте її в `models.providers.ollama`.

    ```bash
    ollama list  # Переглянути, що встановлено
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Або іншу модель
    ```

  </Accordion>

  <Accordion title="У з’єднанні відмовлено">
    Перевірте, що Ollama запущено на правильному порту:

    ```bash
    # Перевірити, чи запущено Ollama
    ps aux | grep ollama

    # Або перезапустити Ollama
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Більше допомоги: [Усунення несправностей](/uk/help/troubleshooting) і [FAQ](/uk/help/faq).
</Note>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Провайдери моделей" href="/uk/concepts/model-providers" icon="layers">
    Огляд усіх провайдерів, посилань на моделі та поведінки перемикання при відмові.
  </Card>
  <Card title="Вибір моделі" href="/uk/concepts/models" icon="brain">
    Як вибирати та налаштовувати моделі.
  </Card>
  <Card title="Ollama Web Search" href="/uk/tools/ollama-search" icon="magnifying-glass">
    Повні відомості про налаштування та поведінку вебпошуку на основі Ollama.
  </Card>
  <Card title="Конфігурація" href="/uk/gateway/configuration" icon="gear">
    Повний довідник із конфігурації.
  </Card>
</CardGroup>
