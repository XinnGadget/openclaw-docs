---
summary: "Использовать Z.AI (модели GLM) с OpenClaw"
read_when:
  - Вам нужны модели Z.AI / GLM в OpenClaw
  - Вам нужна простая настройка ZAI_API_KEY
title: "Z.AI"
---

# Z.AI

Z.AI — это платформа API для моделей **GLM**. Она предоставляет REST API для GLM и использует API-ключи для аутентификации. Создайте свой API-ключ в консоли Z.AI. OpenClaw использует провайдер `zai` с API-ключом Z.AI.

## Настройка через CLI

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

## Встроенный каталог GLM

В настоящее время OpenClaw включает в состав встроенного провайдера `zai` следующие модели:

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

- Модели GLM доступны как `zai/<модель>` (например, `zai/glm-5`).
- Модель по умолчанию во встроенном каталоге: `zai/glm-5.1`.
- Неизвестные идентификаторы `glm-5*` по-прежнему разрешаются во встроенном провайдере путём синтеза метаданных, принадлежащих провайдеру, на основе шаблона `glm-4.7`, если идентификатор соответствует текущей структуре семейства GLM-5.
- Функция `tool_stream` включена по умолчанию для потоковой передачи вызовов инструментов в Z.AI. Чтобы отключить её, установите значение `agents.defaults.models["zai/<модель>"].params.tool_stream` равным `false`.
- Обзор семейства моделей см. в разделе [/providers/glm](/providers/glm).
- В Z.AI используется аутентификация Bearer с вашим API-ключом.