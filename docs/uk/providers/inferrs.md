---
read_when:
    - Ви хочете запустити OpenClaw через локальний сервер inferrs
    - Ви надаєте Gemma або іншу модель через inferrs
    - Вам потрібні точні прапорці сумісності OpenClaw для inferrs
summary: Запустіть OpenClaw через inferrs (локальний сервер, сумісний з OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-12T10:12:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) може обслуговувати локальні моделі через
OpenAI-сумісний API `/v1`. OpenClaw працює з `inferrs` через загальний шлях
`openai-completions`.

Наразі `inferrs` найкраще розглядати як користувацький саморозміщений
OpenAI-сумісний бекенд, а не як окремий Plugin провайдера OpenClaw.

## Початок роботи

<Steps>
  <Step title="Запустіть inferrs із моделлю">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="Переконайтеся, що сервер доступний">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="Додайте запис провайдера OpenClaw">
    Додайте явний запис провайдера та вкажіть на нього вашу модель за замовчуванням. Дивіться повний приклад конфігурації нижче.
  </Step>
</Steps>

## Повний приклад конфігурації

У цьому прикладі використовується Gemma 4 на локальному сервері `inferrs`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Додатково

<AccordionGroup>
  <Accordion title="Чому важливий requiresStringContent">
    Деякі маршрути Chat Completions в `inferrs` приймають лише рядковий
    `messages[].content`, а не структуровані масиви частин вмісту.

    <Warning>
    Якщо запуски OpenClaw завершуються помилкою на кшталт:

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    встановіть `compat.requiresStringContent: true` у записі моделі.
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw згорне частини вмісту, що складаються лише з тексту, у звичайні рядки перед надсиланням запиту.

  </Accordion>

  <Accordion title="Застереження щодо Gemma і схеми інструментів">
    Деякі поточні комбінації `inferrs` + Gemma приймають невеликі прямі
    запити до `/v1/chat/completions`, але все одно завершуються помилкою на повних
    ходах runtime агента OpenClaw.

    Якщо таке трапляється, спершу спробуйте це:

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    Це вимикає поверхню схеми інструментів OpenClaw для моделі й може зменшити навантаження на підказку для суворіших локальних бекендів.

    Якщо малі прямі запити й далі працюють, але звичайні ходи агента OpenClaw все ще
    аварійно завершуються всередині `inferrs`, то решта проблеми зазвичай пов’язана з
    поведінкою моделі/сервера вище за течією, а не з транспортним шаром OpenClaw.

  </Accordion>

  <Accordion title="Ручна smoke-перевірка">
    Після налаштування перевірте обидва шари:

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    Якщо перша команда працює, а друга — ні, перегляньте розділ усунення несправностей нижче.

  </Accordion>

  <Accordion title="Поведінка у стилі проксі">
    `inferrs` розглядається як OpenAI-сумісний бекенд `/v1` у стилі проксі, а не як
    нативна кінцева точка OpenAI.

    - Формування запитів, притаманне лише нативному OpenAI, тут не застосовується
    - Немає `service_tier`, немає Responses `store`, немає підказок кешу промптів і немає формування payload сумісності reasoning для OpenAI
    - Приховані заголовки атрибуції OpenClaw (`originator`, `version`, `User-Agent`)
      не додаються для користувацьких базових URL `inferrs`

  </Accordion>
</AccordionGroup>

## Усунення несправностей

<AccordionGroup>
  <Accordion title="curl /v1/models завершується помилкою">
    `inferrs` не запущено, він недоступний або не прив’язаний до очікуваного
    хоста/порту. Переконайтеся, що сервер запущений і слухає на адресі, яку ви
    налаштували.
  </Accordion>

  <Accordion title="messages[].content очікує рядок">
    Установіть `compat.requiresStringContent: true` у записі моделі. Дивіться
    розділ `requiresStringContent` вище для подробиць.
  </Accordion>

  <Accordion title="Прямі виклики /v1/chat/completions проходять, але openclaw infer model run завершується помилкою">
    Спробуйте встановити `compat.supportsTools: false`, щоб вимкнути поверхню схеми інструментів.
    Дивіться застереження щодо схеми інструментів для Gemma вище.
  </Accordion>

  <Accordion title="inferrs усе ще аварійно завершується на більших ходах агента">
    Якщо OpenClaw більше не отримує помилок схеми, але `inferrs` усе ще аварійно завершується на більших
    ходах агента, вважайте це обмеженням `inferrs` або моделі вище за течією. Зменште
    навантаження на промпт або перейдіть на інший локальний бекенд чи модель.
  </Accordion>
</AccordionGroup>

<Tip>
Для загальної довідки дивіться [Усунення несправностей](/uk/help/troubleshooting) і [FAQ](/uk/help/faq).
</Tip>

## Дивіться також

<CardGroup cols={2}>
  <Card title="Локальні моделі" href="/uk/gateway/local-models" icon="server">
    Запуск OpenClaw із локальними серверами моделей.
  </Card>
  <Card title="Усунення несправностей Gateway" href="/uk/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    Налагодження локальних OpenAI-сумісних бекендів, які проходять прямі перевірки, але не проходять запуски агента.
  </Card>
  <Card title="Провайдери моделей" href="/uk/concepts/model-providers" icon="layers">
    Огляд усіх провайдерів, посилань на моделі та поведінки перемикання при відмові.
  </Card>
</CardGroup>
