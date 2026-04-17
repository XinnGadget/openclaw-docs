---
read_when:
    - Ви хочете використовувати Hugging Face Inference з OpenClaw
    - Вам потрібна змінна середовища токена HF або варіант автентифікації CLI
summary: Налаштування Hugging Face Inference (автентифікація + вибір моделі)
title: Hugging Face (Inference)
x-i18n:
    generated_at: "2026-04-12T10:12:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face (Inference)

[Провайдери Hugging Face Inference](https://huggingface.co/docs/inference-providers) пропонують OpenAI-сумісні chat completions через єдиний router API. Ви отримуєте доступ до багатьох моделей (DeepSeek, Llama та інших) з одним токеном. OpenClaw використовує **OpenAI-сумісний endpoint** (лише chat completions); для text-to-image, embeddings або speech використовуйте [HF inference clients](https://huggingface.co/docs/api-inference/quicktour) напряму.

- Провайдер: `huggingface`
- Автентифікація: `HUGGINGFACE_HUB_TOKEN` або `HF_TOKEN` (fine-grained token з дозволом **Make calls to Inference Providers**)
- API: OpenAI-сумісний (`https://router.huggingface.co/v1`)
- Оплата: один токен HF; [тарифи](https://huggingface.co/docs/inference-providers/pricing) відповідають ставкам провайдерів і мають безкоштовний рівень.

## Початок роботи

<Steps>
  <Step title="Створіть fine-grained token">
    Перейдіть до [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) і створіть новий fine-grained token.

    <Warning>
    Для токена має бути ввімкнено дозвіл **Make calls to Inference Providers**, інакше API-запити буде відхилено.
    </Warning>

  </Step>
  <Step title="Запустіть онбординг">
    Виберіть **Hugging Face** у випадаючому списку провайдера, а потім введіть свій API-ключ, коли з’явиться запит:

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="Виберіть модель за замовчуванням">
    У випадаючому списку **Default Hugging Face model** виберіть потрібну модель. Список завантажується з Inference API, якщо у вас є дійсний токен; інакше показується вбудований список. Ваш вибір зберігається як модель за замовчуванням.

    Ви також можете встановити або змінити модель за замовчуванням пізніше в config:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="Перевірте, що модель доступна">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### Неінтерактивне налаштування

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

Це встановить `huggingface/deepseek-ai/DeepSeek-R1` як модель за замовчуванням.

## ID моделей

Посилання на моделі використовують формат `huggingface/<org>/<model>` (Hub-style ID). Список нижче взято з **GET** `https://router.huggingface.co/v1/models`; ваш каталог може містити більше.

| Модель                 | Ref (додайте префікс `huggingface/`) |
| ---------------------- | ------------------------------------ |
| DeepSeek R1            | `deepseek-ai/DeepSeek-R1`            |
| DeepSeek V3.2          | `deepseek-ai/DeepSeek-V3.2`          |
| Qwen3 8B               | `Qwen/Qwen3-8B`                      |
| Qwen2.5 7B Instruct    | `Qwen/Qwen2.5-7B-Instruct`           |
| Qwen3 32B              | `Qwen/Qwen3-32B`                     |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct`  |
| Llama 3.1 8B Instruct  | `meta-llama/Llama-3.1-8B-Instruct`   |
| GPT-OSS 120B           | `openai/gpt-oss-120b`                |
| GLM 4.7                | `zai-org/GLM-4.7`                    |
| Kimi K2.5              | `moonshotai/Kimi-K2.5`               |

<Tip>
Ви можете додати `:fastest` або `:cheapest` до будь-якого ID моделі. Установіть порядок за замовчуванням у [налаштуваннях Inference Provider](https://hf.co/settings/inference-providers); див. [Inference Providers](https://huggingface.co/docs/inference-providers) і **GET** `https://router.huggingface.co/v1/models` для повного списку.
</Tip>

## Додаткові подробиці

<AccordionGroup>
  <Accordion title="Виявлення моделей і випадаючий список в онбордингу">
    OpenClaw виявляє моделі, викликаючи **endpoint Inference напряму**:

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    (Необов’язково: надсилайте `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` або `$HF_TOKEN` для повного списку; деякі endpoint без автентифікації повертають лише підмножину.) Відповідь має формат OpenAI `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`.

    Коли ви налаштовуєте API-ключ Hugging Face (через онбординг, `HUGGINGFACE_HUB_TOKEN` або `HF_TOKEN`), OpenClaw використовує цей GET для виявлення доступних моделей chat-completion. Під час **інтерактивного налаштування**, після введення токена, ви побачите випадаючий список **Default Hugging Face model**, заповнений із цього списку (або з вбудованого каталогу, якщо запит не вдасться). Під час виконання (наприклад, під час запуску Gateway), якщо ключ наявний, OpenClaw знову викликає **GET** `https://router.huggingface.co/v1/models`, щоб оновити каталог. Список об’єднується з вбудованим каталогом (для метаданих, як-от context window і вартість). Якщо запит не вдається або ключ не задано, використовується лише вбудований каталог.

  </Accordion>

  <Accordion title="Назви моделей, псевдоніми та суфікси політик">
    - **Назва з API:** Відображувана назва моделі **заповнюється з GET /v1/models**, коли API повертає `name`, `title` або `display_name`; інакше вона виводиться з ID моделі (наприклад, `deepseek-ai/DeepSeek-R1` стає "DeepSeek R1").
    - **Перевизначення відображуваної назви:** Ви можете задати власну мітку для кожної моделі в config, щоб вона відображалася в CLI та UI так, як вам потрібно:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
          },
        },
      },
    }
    ```

    - **Суфікси політик:** У вбудованій документації та helper-утилітах Hugging Face в OpenClaw ці два суфікси наразі розглядаються як вбудовані варіанти політик:
      - **`:fastest`** — найвища пропускна здатність.
      - **`:cheapest`** — найнижча вартість за вихідний токен.

      Ви можете додати їх як окремі записи в `models.providers.huggingface.models` або встановити `model.primary` із суфіксом. Ви також можете задати порядок провайдерів за замовчуванням у [налаштуваннях Inference Provider](https://hf.co/settings/inference-providers) (без суфікса = використовувати цей порядок).

    - **Об’єднання config:** Наявні записи в `models.providers.huggingface.models` (наприклад, у `models.json`) зберігаються під час об’єднання config. Тож будь-які власні `name`, `alias` або параметри моделі, які ви там задали, буде збережено.

  </Accordion>

  <Accordion title="Налаштування середовища та демона">
    Якщо Gateway працює як демон (launchd/systemd), переконайтеся, що `HUGGINGFACE_HUB_TOKEN` або `HF_TOKEN` доступні цьому процесу (наприклад, у `~/.openclaw/.env` або через `env.shellEnv`).

    <Note>
    OpenClaw приймає і `HUGGINGFACE_HUB_TOKEN`, і `HF_TOKEN` як псевдоніми змінних середовища. Працює будь-яка з них; якщо задано обидві, пріоритет має `HUGGINGFACE_HUB_TOKEN`.
    </Note>

  </Accordion>

  <Accordion title="Config: DeepSeek R1 із резервною моделлю Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: Qwen із найдешевшим і найшвидшим варіантами">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: DeepSeek + Llama + GPT-OSS із псевдонімами">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: Кілька моделей Qwen і DeepSeek із суфіксами політик">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Провайдери моделей" href="/uk/concepts/model-providers" icon="layers">
    Огляд усіх провайдерів, посилань на моделі та поведінки резервного перемикання.
  </Card>
  <Card title="Вибір моделі" href="/uk/concepts/models" icon="brain">
    Як вибирати й налаштовувати моделі.
  </Card>
  <Card title="Документація Inference Providers" href="https://huggingface.co/docs/inference-providers" icon="book">
    Офіційна документація Hugging Face Inference Providers.
  </Card>
  <Card title="Конфігурація" href="/uk/gateway/configuration" icon="gear">
    Повний довідник із config.
  </Card>
</CardGroup>
