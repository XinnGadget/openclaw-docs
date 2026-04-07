---
read_when:
    - Ви хочете запускати OpenClaw із хмарними або локальними моделями через Ollama
    - Вам потрібні вказівки щодо налаштування та конфігурації Ollama
summary: Запуск OpenClaw з Ollama (хмарні та локальні моделі)
title: Ollama
x-i18n:
    generated_at: "2026-04-07T18:55:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 222ec68f7d4bb29cc7796559ddef1d5059f5159e7a51e2baa3a271ddb3abb716
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama — це локальне середовище виконання LLM, яке спрощує запуск моделей з відкритим кодом на вашому комп’ютері. OpenClaw інтегрується з нативним API Ollama (`/api/chat`), підтримує потокову передачу та виклик інструментів, а також може автоматично виявляти локальні моделі Ollama, якщо ви ввімкнете це за допомогою `OLLAMA_API_KEY` (або профілю автентифікації) і не визначите явний запис `models.providers.ollama`.

<Warning>
**Користувачі віддаленої Ollama**: не використовуйте OpenAI-сумісну URL-адресу `/v1` (`http://host:11434/v1`) з OpenClaw. Це порушує виклик інструментів, і моделі можуть виводити необроблений JSON інструментів як звичайний текст. Натомість використовуйте нативну URL-адресу API Ollama: `baseUrl: "http://host:11434"` (без `/v1`).
</Warning>

## Швидкий старт

### Онбординг (рекомендовано)

Найшвидший спосіб налаштувати Ollama — через онбординг:

```bash
openclaw onboard
```

Виберіть **Ollama** зі списку провайдерів. Онбординг:

1. Запитає базову URL-адресу Ollama, за якою доступний ваш інстанс (типово `http://127.0.0.1:11434`).
2. Дозволить вибрати **Cloud + Local** (хмарні й локальні моделі) або **Local** (лише локальні моделі).
3. Відкриє потік входу через браузер, якщо ви виберете **Cloud + Local** і не ввійшли в ollama.com.
4. Виявить доступні моделі та запропонує типові значення.
5. Автоматично виконає завантаження вибраної моделі, якщо вона недоступна локально.

Також підтримується неінтерактивний режим:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --accept-risk
```

За потреби вкажіть власну базову URL-адресу або модель:

```bash
openclaw onboard --non-interactive \
  --auth-choice ollama \
  --custom-base-url "http://ollama-host:11434" \
  --custom-model-id "qwen3.5:27b" \
  --accept-risk
```

### Ручне налаштування

1. Установіть Ollama: [https://ollama.com/download](https://ollama.com/download)

2. Завантажте локальну модель, якщо хочете локальний інференс:

```bash
ollama pull gemma4
# або
ollama pull gpt-oss:20b
# або
ollama pull llama3.3
```

3. Якщо вам також потрібні хмарні моделі, увійдіть:

```bash
ollama signin
```

4. Запустіть онбординг і виберіть `Ollama`:

```bash
openclaw onboard
```

- `Local`: лише локальні моделі
- `Cloud + Local`: локальні моделі плюс хмарні моделі
- Хмарні моделі, як-от `kimi-k2.5:cloud`, `minimax-m2.7:cloud` і `glm-5.1:cloud`, **не** потребують локального `ollama pull`

Наразі OpenClaw пропонує:

- локальне типове значення: `gemma4`
- хмарні типові значення: `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud`

5. Якщо ви віддаєте перевагу ручному налаштуванню, увімкніть Ollama для OpenClaw напряму (підійде будь-яке значення; Ollama не потребує справжнього ключа):

```bash
# Set environment variable
export OLLAMA_API_KEY="ollama-local"

# Or configure in your config file
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. Перегляньте або змініть моделі:

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. Або встановіть типову модель у конфігурації:

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## Виявлення моделей (неявний провайдер)

Коли ви задаєте `OLLAMA_API_KEY` (або профіль автентифікації) і **не** визначаєте `models.providers.ollama`, OpenClaw виявляє моделі з локального інстансу Ollama за адресою `http://127.0.0.1:11434`:

- Виконує запити до `/api/tags`
- Використовує best-effort-запити до `/api/show`, щоб читати `contextWindow`, якщо він доступний
- Позначає `reasoning` за допомогою евристики назви моделі (`r1`, `reasoning`, `think`)
- Установлює `maxTokens` на типове максимальне обмеження токенів Ollama, яке використовує OpenClaw
- Установлює всі вартості в `0`

Це дозволяє уникнути ручного додавання моделей і водночас зберігати каталог узгодженим із локальним інстансом Ollama.

Щоб побачити, які моделі доступні:

```bash
ollama list
openclaw models list
```

Щоб додати нову модель, просто завантажте її через Ollama:

```bash
ollama pull mistral
```

Нова модель буде автоматично виявлена та стане доступною для використання.

Якщо ви явно задасте `models.providers.ollama`, автоматичне виявлення буде пропущено, і вам доведеться визначати моделі вручну (див. нижче).

## Конфігурація

### Базове налаштування (неявне виявлення)

Найпростіший спосіб увімкнути Ollama — через змінну середовища:

```bash
export OLLAMA_API_KEY="ollama-local"
```

### Явне налаштування (ручне визначення моделей)

Використовуйте явну конфігурацію, якщо:

- Ollama працює на іншому хості або порту.
- Ви хочете примусово задати конкретні вікна контексту або списки моделей.
- Ви хочете повністю вручну визначати моделі.

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

Якщо задано `OLLAMA_API_KEY`, ви можете не вказувати `apiKey` у записі провайдера, і OpenClaw підставить його для перевірок доступності.

### Власна базова URL-адреса (явна конфігурація)

Якщо Ollama працює на іншому хості або порту (явна конфігурація вимикає автоматичне виявлення, тому моделі потрібно визначати вручну):

```json5
{
  models: {
    providers: {
      ollama: {
        apiKey: "ollama-local",
        baseUrl: "http://ollama-host:11434", // Без /v1 - використовуйте нативну URL-адресу API Ollama
        api: "ollama", // Задайте явно, щоб гарантувати нативну поведінку виклику інструментів
      },
    },
  },
}
```

<Warning>
Не додавайте `/v1` до URL-адреси. Шлях `/v1` використовує OpenAI-сумісний режим, у якому виклик інструментів ненадійний. Використовуйте базову URL-адресу Ollama без суфікса шляху.
</Warning>

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

## Хмарні моделі

Хмарні моделі дають змогу використовувати розміщені в хмарі моделі (наприклад, `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud`) разом із вашими локальними моделями.

Щоб використовувати хмарні моделі, виберіть режим **Cloud + Local** під час налаштування. Майстер перевіряє, чи ви ввійшли в систему, і за потреби відкриває потік входу через браузер. Якщо автентифікацію не вдається перевірити, майстер повертається до типових локальних моделей.

Ви також можете ввійти безпосередньо на [ollama.com/signin](https://ollama.com/signin).

## Ollama Web Search

OpenClaw також підтримує **Ollama Web Search** як вбудований провайдер `web_search`.

- Він використовує налаштований вами хост Ollama (`models.providers.ollama.baseUrl`, якщо задано, інакше `http://127.0.0.1:11434`).
- Він не потребує ключа.
- Для нього потрібно, щоб Ollama працювала і ви були авторизовані через `ollama signin`.

Виберіть **Ollama Web Search** під час `openclaw onboard` або `openclaw configure --section web`, або задайте:

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

Повні відомості про налаштування та поведінку див. у [Ollama Web Search](/uk/tools/ollama-search).

## Додатково

### Моделі міркування

OpenClaw типово вважає моделі з назвами на кшталт `deepseek-r1`, `reasoning` або `think` такими, що підтримують міркування:

```bash
ollama pull deepseek-r1:32b
```

### Вартість моделей

Ollama є безкоштовною і працює локально, тому вартість усіх моделей встановлена на рівні $0.

### Конфігурація потокової передачі

Інтеграція OpenClaw з Ollama типово використовує **нативний API Ollama** (`/api/chat`), який повністю підтримує одночасно потокову передачу та виклик інструментів. Жодного спеціального налаштування не потрібно.

#### Застарілий OpenAI-сумісний режим

<Warning>
**Виклик інструментів у OpenAI-сумісному режимі ненадійний.** Використовуйте цей режим лише якщо вам потрібен формат OpenAI для проксі й ви не залежите від нативної поведінки виклику інструментів.
</Warning>

Якщо вам потрібно використовувати натомість OpenAI-сумісну кінцеву точку (наприклад, за проксі, який підтримує лише формат OpenAI), явно задайте `api: "openai-completions"`:

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434/v1",
        api: "openai-completions",
        injectNumCtxForOpenAICompat: true, // типово: true
        apiKey: "ollama-local",
        models: [...]
      }
    }
  }
}
```

Цей режим може не підтримувати одночасно потокову передачу й виклик інструментів. Може знадобитися вимкнути потокову передачу за допомогою `params: { streaming: false }` у конфігурації моделі.

Коли з Ollama використовується `api: "openai-completions"`, OpenClaw типово додає `options.num_ctx`, щоб Ollama не переходила непомітно на вікно контексту 4096. Якщо ваш проксі або upstream відхиляє невідомі поля `options`, вимкніть цю поведінку:

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

### Вікна контексту

Для автоматично виявлених моделей OpenClaw використовує вікно контексту, яке повідомляє Ollama, якщо воно доступне; інакше використовується типове вікно контексту Ollama, яке застосовує OpenClaw. Ви можете перевизначити `contextWindow` і `maxTokens` у явній конфігурації провайдера.

## Усунення несправностей

### Ollama не виявлено

Переконайтеся, що Ollama запущена, що ви задали `OLLAMA_API_KEY` (або профіль автентифікації), і що ви **не** визначили явний запис `models.providers.ollama`:

```bash
ollama serve
```

І що API доступний:

```bash
curl http://localhost:11434/api/tags
```

### Немає доступних моделей

Якщо вашої моделі немає у списку, виконайте одну з дій:

- Завантажте модель локально, або
- Явно визначте модель у `models.providers.ollama`.

Щоб додати моделі:

```bash
ollama list  # Переглянути, що встановлено
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # Або іншу модель
```

### У з’єднанні відмовлено

Переконайтеся, що Ollama працює на правильному порту:

```bash
# Перевірити, чи запущена Ollama
ps aux | grep ollama

# Або перезапустити Ollama
ollama serve
```

## Див. також

- [Провайдери моделей](/uk/concepts/model-providers) - Огляд усіх провайдерів
- [Вибір моделі](/uk/concepts/models) - Як вибирати моделі
- [Конфігурація](/uk/gateway/configuration) - Повний довідник з конфігурації
