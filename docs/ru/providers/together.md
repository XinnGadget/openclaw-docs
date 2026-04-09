---
title: "Together AI"
summary: "Настройка Together AI (аутентификация + выбор модели)"
read_when:
  - Вы хотите использовать Together AI с OpenClaw
  - Вам нужна переменная окружения с API-ключом или выбор аутентификации через CLI
---

# Together AI

[Together AI](https://together.ai) предоставляет доступ к ведущим моделям с открытым исходным кодом, включая Llama, DeepSeek, Kimi и другие, через унифицированный API.

- Поставщик: `together`
- Аутентификация: `TOGETHER_API_KEY`
- API: совместим с OpenAI
- Базовый URL: `https://api.together.xyz/v1`

## Быстрый старт

1. Задайте API-ключ (рекомендуется сохранить его для Gateway):

```bash
openclaw onboard --auth-choice together-api-key
```

2. Задайте модель по умолчанию:

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## Пример без интерактивного режима

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

Это установит `together/moonshotai/Kimi-K2.5` в качестве модели по умолчанию.

## Примечание об окружении

Если Gateway работает как демон (launchd/systemd), убедитесь, что `TOGETHER_API_KEY` доступен для этого процесса (например, в `~/.openclaw/.env` или через `env.shellEnv`).

## Встроенный каталог

В настоящее время OpenClaw поставляется со следующим встроенным каталогом Together:

| Ссылка на модель | Название | Входные данные | Контекст | Примечания |
| --- | --- | --- | --- | --- |
| `together/moonshotai/Kimi-K2.5` | Kimi K2.5 | текст, изображение | 262 144 | Модель по умолчанию; включено рассуждение |
| `together/zai-org/GLM-4.7` | GLM 4.7 Fp8 | текст | 202 752 | Универсальная текстовая модель |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo` | Llama 3.3 70B Instruct Turbo | текст | 131 072 | Быстрая модель для инструкций |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct` | Llama 4 Scout 17B 16E Instruct | текст, изображение | 10 000 000 | Мультимодальная модель |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | текст, изображение | 20 000 000 | Мультимодальная модель |
| `together/deepseek-ai/DeepSeek-V3.1` | DeepSeek V3.1 | текст | 131 072 | Общая текстовая модель |
| `together/deepseek-ai/DeepSeek-R1` | DeepSeek R1 | текст | 131 072 | Модель для рассуждений |
| `together/moonshotai/Kimi-K2-Instruct-0905` | Kimi K2-Instruct 0905 | текст | 262 144 | Вторая текстовая модель Kimi |

Пресет для подключения устанавливает `together/moonshotai/Kimi-K2.5` в качестве модели по умолчанию.

## Генерация видео

Встроенный плагин `together` также регистрирует генерацию видео через общий инструмент `video_generate`.

- Модель для видео по умолчанию: `together/Wan-AI/Wan2.2-T2V-A14B`
- Режимы: преобразование текста в видео и потоки с использованием одного изображения в качестве референса
- Поддерживает параметры `aspectRatio` и `resolution`

Чтобы использовать Together в качестве поставщика видео по умолчанию:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

См. [Генерация видео](/tools/video-generation) для ознакомления с параметрами общего инструмента, выбором поставщика и поведением при отказоустойчивости.