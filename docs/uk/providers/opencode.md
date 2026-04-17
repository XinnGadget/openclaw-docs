---
read_when:
    - Вам потрібен доступ до моделей, розміщених у OpenCode
    - Ви хочете вибрати між каталогами Zen і Go
summary: Використовуйте каталоги OpenCode Zen і Go з OpenClaw
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T10:36:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode надає два розміщені каталоги в OpenClaw:

| Каталог | Префікс          | Провайдер runtime |
| ------- | ---------------- | ----------------- |
| **Zen** | `opencode/...`    | `opencode`       |
| **Go**  | `opencode-go/...` | `opencode-go`    |

Обидва каталоги використовують той самий ключ API OpenCode. OpenClaw зберігає ідентифікатори провайдерів runtime
розділеними, щоб маршрутизація для кожної моделі у вищерозташованому сервісі залишалася коректною, але онбординг і документація розглядають їх
як єдине налаштування OpenCode.

## Початок роботи

<Tabs>
  <Tab title="Zen catalog">
    **Найкраще підходить для:** курованого багатомодельного проксі OpenCode (Claude, GPT, Gemini).

    <Steps>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        Або передайте ключ напряму:

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Set a Zen model as the default">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="Verify models are available">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Go catalog">
    **Найкраще підходить для:** лінійки Kimi, GLM і MiniMax, розміщеної в OpenCode.

    <Steps>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        Або передайте ключ напряму:

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Set a Go model as the default">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="Verify models are available">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Приклад конфігурації

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## Каталоги

### Zen

| Властивість      | Значення                                                                |
| ---------------- | ----------------------------------------------------------------------- |
| Провайдер runtime | `opencode`                                                             |
| Приклади моделей | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| Властивість      | Значення                                                                 |
| ---------------- | ------------------------------------------------------------------------ |
| Провайдер runtime | `opencode-go`                                                           |
| Приклади моделей | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## Додаткові примітки

<AccordionGroup>
  <Accordion title="API key aliases">
    `OPENCODE_ZEN_API_KEY` також підтримується як псевдонім для `OPENCODE_API_KEY`.
  </Accordion>

  <Accordion title="Shared credentials">
    Введення одного ключа OpenCode під час налаштування зберігає облікові дані для обох провайдерів runtime.
    Вам не потрібно проходити онбординг для кожного каталогу окремо.
  </Accordion>

  <Accordion title="Billing and dashboard">
    Ви входите в OpenCode, додаєте платіжні дані та копіюєте свій ключ API. Керування білінгом
    і доступністю каталогів здійснюється з панелі керування OpenCode.
  </Accordion>

  <Accordion title="Gemini replay behavior">
    Посилання OpenCode на базі Gemini залишаються на шляху proxy-Gemini, тому OpenClaw зберігає
    там санітизацію thought-signature Gemini без увімкнення нативної
    перевірки повторного відтворення Gemini або переписування bootstrap.
  </Accordion>

  <Accordion title="Non-Gemini replay behavior">
    Посилання OpenCode не на базі Gemini зберігають мінімальну політику повторного відтворення, сумісну з OpenAI.
  </Accordion>
</AccordionGroup>

<Tip>
Введення одного ключа OpenCode під час налаштування зберігає облікові дані для обох провайдерів runtime Zen і
Go, тож вам потрібно пройти онбординг лише один раз.
</Tip>

## Пов’язане

<CardGroup cols={2}>
  <Card title="Model selection" href="/uk/concepts/model-providers" icon="layers">
    Вибір провайдерів, посилань моделей і поведінки резервного перемикання.
  </Card>
  <Card title="Configuration reference" href="/uk/gateway/configuration-reference" icon="gear">
    Повний довідник конфігурації для агентів, моделей і провайдерів.
  </Card>
</CardGroup>
