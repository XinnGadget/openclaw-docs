---
read_when:
    - Ви хочете використовувати генерацію відео Runway в OpenClaw
    - Вам потрібне налаштування API-ключа/змінної середовища Runway
    - Ви хочете зробити Runway типовим провайдером відео
summary: Налаштування генерації відео Runway в OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-12T10:36:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw постачається з вбудованим провайдером `runway` для хостованої генерації відео.

| Властивість | Значення                                                           |
| ----------- | ------------------------------------------------------------------ |
| ID провайдера | `runway`                                                         |
| Автентифікація | `RUNWAYML_API_SECRET` (канонічна) або `RUNWAY_API_KEY`          |
| API         | Генерація відео Runway на основі задач (`GET /v1/tasks/{id}` polling) |

## Початок роботи

<Steps>
  <Step title="Встановіть API-ключ">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="Зробіть Runway типовим провайдером відео">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="Згенеруйте відео">
    Попросіть агента згенерувати відео. Runway буде використано автоматично.
  </Step>
</Steps>

## Підтримувані режими

| Режим         | Модель             | Вхідні референсні дані   |
| ------------- | ------------------ | ------------------------ |
| Текст у відео | `gen4.5` (типово)  | Немає                    |
| Зображення у відео | `gen4.5`      | 1 локальне або віддалене зображення |
| Відео у відео | `gen4_aleph`       | 1 локальне або віддалене відео |

<Note>
Локальні посилання на зображення та відео підтримуються через URI даних. Для
запусків лише з текстом наразі доступні співвідношення сторін `16:9` і `9:16`.
</Note>

<Warning>
Режим відео у відео наразі вимагає саме `runway/gen4_aleph`.
</Warning>

## Конфігурація

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## Додаткові примітки

<AccordionGroup>
  <Accordion title="Псевдоніми змінних середовища">
    OpenClaw розпізнає і `RUNWAYML_API_SECRET` (канонічна), і `RUNWAY_API_KEY`.
    Будь-яка зі змінних забезпечить автентифікацію провайдера Runway.
  </Accordion>

  <Accordion title="Опитування задач">
    Runway використовує API на основі задач. Після надсилання запиту на генерацію OpenClaw
    опитує `GET /v1/tasks/{id}`, доки відео не буде готове. Додаткова
    конфігурація для такої поведінки опитування не потрібна.
  </Accordion>
</AccordionGroup>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Генерація відео" href="/uk/tools/video-generation" icon="video">
    Спільні параметри інструмента, вибір провайдера та асинхронна поведінка.
  </Card>
  <Card title="Довідник із конфігурації" href="/uk/gateway/configuration-reference#agent-defaults" icon="gear">
    Типові налаштування агента, зокрема модель генерації відео.
  </Card>
</CardGroup>
