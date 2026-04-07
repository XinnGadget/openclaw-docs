---
read_when:
    - Ви хочете безкоштовно використовувати відкриті моделі в OpenClaw
    - Вам потрібно налаштувати NVIDIA_API_KEY
summary: Використовуйте сумісний з OpenAI API від NVIDIA в OpenClaw
title: NVIDIA
x-i18n:
    generated_at: "2026-04-07T14:49:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: b00f8cedaf223a33ba9f6a6dd8cf066d88cebeea52d391b871e435026182228a
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA надає сумісний з OpenAI API за адресою `https://integrate.api.nvidia.com/v1` для безкоштовного використання відкритих моделей. Автентифікуйтеся за допомогою API-ключа з [build.nvidia.com](https://build.nvidia.com/settings/api-keys).

## Налаштування CLI

Експортуйте ключ один раз, потім виконайте онбординг і встановіть модель NVIDIA:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

Якщо ви все ще передаєте `--token`, пам’ятайте, що він потрапляє в історію оболонки та вивід `ps`; за можливості надавайте перевагу змінній середовища.

## Фрагмент конфігурації

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## Ідентифікатори моделей

| Посилання на модель                         | Назва                        | Контекст | Макс. вивід |
| ------------------------------------------ | ---------------------------- | -------- | ----------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144  | 8,192       |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144  | 8,192       |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608  | 8,192       |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752  | 8,192       |

## Примітки

- Сумісна з OpenAI кінцева точка `/v1`; використовуйте API-ключ із [build.nvidia.com](https://build.nvidia.com/).
- Провайдер автоматично вмикається, коли встановлено `NVIDIA_API_KEY`.
- Вбудований каталог є статичним; у вихідному коді вартість за замовчуванням дорівнює `0`.
