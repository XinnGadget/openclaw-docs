---
summary: "Обзор семейства моделей GLM + как использовать их в OpenClaw"
read_when:
  - Вам нужны модели GLM в OpenClaw
  - Вам требуется соглашение об именовании моделей и их настройка
title: "Модели GLM"
---

# Модели GLM

GLM — это **семейство моделей** (не компания), доступное через платформу Z.AI. В OpenClaw доступ к моделям GLM осуществляется через провайдера `zai` и идентификаторы моделей вроде `zai/glm-5`.

## Настройка CLI

```bash
# Общая настройка API-ключа с автоматическим определением эндпоинта
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global, рекомендуется для пользователей Coding Plan
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN (регион Китай), рекомендуется для пользователей Coding Plan
openclaw onboard --auth-choice zai-coding-cn

# Общий API
openclaw onboard --auth-choice zai-global

# Общий API CN (регион Китай)
openclaw onboard --auth-choice zai-cn
```

## Фрагмент конфигурации

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

`zai-api-key` позволяет OpenClaw определить соответствующий эндпоинт Z.AI по ключу и автоматически применить корректный базовый URL. Используйте явные региональные варианты, если хотите принудительно выбрать определённый Coding Plan или общий интерфейс API.

## Текущие встроенные модели GLM

В настоящее время OpenClaw предоставляет встроенному провайдеру `zai` следующие ссылки на модели GLM:

- `glm-5.1`
- `glm-5`
- `glm-5-turbo`
- `glm-5v-turbo`
- `glm-4.7`
- `glm-4.7-flash`
- `glm-4.7-flashx`
- `glm-4.6`
- `glm-4.6v`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`
- `glm-4.5v`

## Примечания

- Версии GLM и их доступность могут меняться; ознакомьтесь с актуальной документацией Z.AI.
- Ссылка на модель по умолчанию во встроенном пакете — `zai/glm-5.1`.
- Подробности о провайдере см. в разделе [/providers/zai](/providers/zai).