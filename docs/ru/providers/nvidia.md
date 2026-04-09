---
summary: "Использовать совместимый с OpenAI API от NVIDIA в OpenClaw"
read_when:
  - Вы хотите бесплатно использовать открытые модели в OpenClaw
  - Вам нужно настроить NVIDIA_API_KEY
title: "NVIDIA"
---

# NVIDIA

NVIDIA предоставляет совместимый с OpenAI API по адресу `https://integrate.api.nvidia.com/v1` для открытых моделей — бесплатно. Для аутентификации используйте API-ключ с сайта [build.nvidia.com](https://build.nvidia.com/settings/api-keys).

## Настройка через CLI

Экспортируйте ключ один раз, затем запустите процедуру подключения и выберите модель NVIDIA:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

Если вы всё же используете параметр `--token`, помните, что он попадает в историю оболочки и вывод команды `ps`; по возможности предпочитайте переменную окружения.

## Фрагмент конфигурации

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

## Идентификаторы моделей

| Ссылка на модель | Название | Контекст | Максимальный объём вывода |
| --- | --- | --- | --- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262 144 | 8 192 |
| `nvidia/moonshotai/kimi-k2.5` | Kimi K2.5 | 262 144 | 8 192 |
| `nvidia/minimaxai/minimax-m2.5` | Minimax M2.5 | 196 608 | 8 192 |
| `nvidia/z-ai/glm5` | GLM 5 | 202 752 | 8 192 |

## Примечания

- Конечная точка `/v1`, совместимая с OpenAI; используйте API-ключ с [build.nvidia.com](https://build.nvidia.com/).
- Поставщик автоматически активируется при установке переменной `NVIDIA_API_KEY`.
- Входящий в комплект каталог статичен; стоимость по умолчанию в исходном коде равна `0`.