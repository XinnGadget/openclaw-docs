---
summary: "Настройка инференса Hugging Face (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать инференс Hugging Face с OpenClaw
  - Вам нужна переменная окружения с токеном HF или выбор аутентификации через CLI
title: "Hugging Face (инференс)"
---

# Hugging Face (инференс)

[Поставщики инференса Hugging Face](https://huggingface.co/docs/inference-providers) предоставляют совместимые с OpenAI завершения чата через единый API-маршрутизатор. Вы получаете доступ ко множеству моделей (DeepSeek, Llama и др.) с одним токеном. OpenClaw использует **совместимую с OpenAI конечную точку** (только завершения чата); для задач "текст-в-изображение", эмбеддингов или обработки речи используйте напрямую [клиенты инференса HF](https://huggingface.co/docs/api-inference/quicktour).

- Поставщик: `huggingface`
- Аутентификация: `HUGGINGFACE_HUB_TOKEN` или `HF_TOKEN` (детальный токен с правом **Make calls to Inference Providers**)
- API: совместимый с OpenAI (`https://router.huggingface.co/v1`)
- Оплата: единый токен HF; [цены](https://huggingface.co/docs/inference-providers/pricing) соответствуют тарифам поставщика, есть бесплатный уровень.

## Быстрый старт

1. Создайте детальный токен на [Hugging Face → Настройки → Токены](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) с правом **Make calls to Inference Providers**.
2. Запустите процесс настройки и выберите **Hugging Face** в выпадающем списке поставщиков, затем введите свой API-ключ, когда будет запрошено:

```bash
openclaw onboard --auth-choice huggingface-api-key
```

3. В выпадающем списке **Модель Hugging Face по умолчанию** выберите нужную модель (список загружается из API инференса, если у вас есть действительный токен; в противном случае отображается встроенный список). Ваш выбор сохраняется как модель по умолчанию.
4. Вы также можете задать или изменить модель по умолчанию позже в конфигурации:

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
    },
  },
}
```

## Пример без интерактивного взаимодействия

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

Это установит `huggingface/deepseek-ai/DeepSeek-R1` в качестве модели по умолчанию.

## Примечание об окружении

Если Gateway работает как демон (launchd/systemd), убедитесь, что `HUGGINGFACE_HUB_TOKEN` или `HF_TOKEN` доступны для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Обнаружение моделей и выпадающее меню настройки

OpenClaw обнаруживает модели, обращаясь напрямую к **конечной точке инференса**:

```bash
GET https://router.huggingface.co/v1/models
```

(Опционально: отправьте `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` или `$HF_TOKEN`, чтобы получить полный список; некоторые конечные точки возвращают подмножество без аутентификации.) Ответ имеет формат, совместимый с OpenAI: `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`.

Когда вы настраиваете API-ключ Hugging Face (через процесс настройки, `HUGGINGFACE_HUB_TOKEN` или `HF_TOKEN`), OpenClaw использует этот GET-запрос для обнаружения доступных моделей для завершения чата. Во время **интерактивной настройки** после ввода токена вы увидите выпадающее меню **Модель Hugging Face по умолчанию**, заполненное на основе этого списка (или встроенного каталога, если запрос не удался). Во время выполнения (например, при запуске Gateway), если ключ присутствует, OpenClaw снова выполняет GET-запрос `https://router.huggingface.co/v1/models`, чтобы обновить каталог. Список объединяется со встроенным каталогом (для метаданных, таких как окно контекста и стоимость). Если запрос не удался или ключ не задан, используется только встроенный каталог.

## Имена моделей и настраиваемые параметры

- **Имя из API:** отображаемое имя модели заполняется из GET-запроса `/v1/models`, когда API возвращает `name`, `title` или `display_name`; в противном случае оно формируется на основе идентификатора модели (например, `deepseek-ai/DeepSeek-R1` → "DeepSeek R1").
- **Переопределение отображаемого имени:** вы можете задать пользовательскую метку для каждой модели в конфигурации, чтобы она отображалась так, как вам нужно, в CLI и UI:

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

- **Суффиксы политик:** встроенные документы и помощники Hugging Face в OpenClaw в настоящее время рассматривают следующие два суффикса как встроенные варианты политик:
  - **`:fastest`** — максимальная пропускная способность.
  - **`:cheapest`** — минимальная стоимость за выходной токен.

  Вы можете добавить их как отдельные записи в `models.providers.huggingface.models` или задать `model.primary` с суффиксом. Вы также можете задать порядок поставщиков по умолчанию в [настройках поставщика инференса](https://hf.co/settings/inference-providers) (без суффикса — использовать этот порядок).

- **Слияние конфигурации:** существующие записи в `models.providers.huggingface.models` (например, в `models.json`) сохраняются при слиянии конфигурации. Таким образом, любые заданные вами пользовательские `name`, `alias` или параметры модели сохраняются.

## Идентификаторы моделей и примеры конфигурации

Ссылки на модели используют формат `huggingface/<org>/<model>` (ID в стиле Hub). Список ниже получен с помощью GET-запроса `https://router.huggingface.co/v1/models`; ваш каталог может содержать больше моделей.

**Примеры идентификаторов (из конечной точки инференса):**

| Модель | Ссылка (добавляйте префикс `huggingface/`) |
| --- | --- |
| DeepSeek R1 | `deepseek-ai/DeepSeek-R1` |
| DeepSeek V3.2 | `deepseek-ai/DeepSeek-V3.2` |
| Qwen3 8B | `Qwen/Qwen3-8B` |
| Qwen2.5 7B Instruct | `Qwen/Qwen2.5-7B-Instruct` |
| Qwen3 32B | `Qwen/Qwen3-32B` |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct | `meta-llama/Llama-3.1-8B-Instruct` |
| GPT-OSS 120B | `openai/gpt-oss-120b` |
| GLM 4.7 | `zai-org/GLM-4.7` |
| Kimi K2.5 | `moonshotai/Kimi-K2.5` |

Вы можете добавить к идентификатору модели суффиксы `:fastest` или `:cheapest`. Задайте порядок по умолчанию в [настройках поставщика инференса](https://hf.co/settings/inference-providers); полный список см. в разделе [Поставщики инференса](https://huggingface.co/docs/inference-providers) и по GET-запросу `https://router.huggingface.co/v1/models`.

### Полные примеры конфигурации

**Основная модель DeepSeek R1 с резервной моделью Qwen:**

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
      