---
read_when:
    - Chcesz używać modeli Z.AI / GLM w OpenClaw
    - Potrzebujesz prostej konfiguracji `ZAI_API_KEY`
summary: Używanie Z.AI (modele GLM) z OpenClaw
title: Z.AI
x-i18n:
    generated_at: "2026-04-12T23:33:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 972b467dab141c8c5126ac776b7cb6b21815c27da511b3f34e12bd9e9ac953b7
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI to platforma API dla modeli **GLM**. Udostępnia REST API dla GLM i używa kluczy API
do uwierzytelniania. Utwórz klucz API w konsoli Z.AI. OpenClaw używa dostawcy `zai`
z kluczem API Z.AI.

- Dostawca: `zai`
- Uwierzytelnianie: `ZAI_API_KEY`
- API: Z.AI Chat Completions (Bearer auth)

## Pierwsze kroki

<Tabs>
  <Tab title="Endpoint wykrywany automatycznie">
    **Najlepsze dla:** większości użytkowników. OpenClaw wykrywa pasujący endpoint Z.AI na podstawie klucza i automatycznie stosuje poprawny `base URL`.

    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice zai-api-key
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Jawny regionalny endpoint">
    **Najlepsze dla:** użytkowników, którzy chcą wymusić konkretny plan Coding Plan lub ogólną powierzchnię API.

    <Steps>
      <Step title="Wybierz właściwą opcję onboardingu">
        ```bash
        # Coding Plan Global (zalecane dla użytkowników Coding Plan)
        openclaw onboard --auth-choice zai-coding-global

        # Coding Plan CN (region Chiny)
        openclaw onboard --auth-choice zai-coding-cn

        # Ogólne API
        openclaw onboard --auth-choice zai-global

        # Ogólne API CN (region Chiny)
        openclaw onboard --auth-choice zai-cn
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Bundlowany katalog GLM

OpenClaw obecnie inicjalizuje bundlowanego dostawcę `zai` następującymi modelami:

| Odwołanie do modelu | Uwagi           |
| ------------------- | --------------- |
| `zai/glm-5.1`       | Model domyślny  |
| `zai/glm-5`         |                 |
| `zai/glm-5-turbo`   |                 |
| `zai/glm-5v-turbo`  |                 |
| `zai/glm-4.7`       |                 |
| `zai/glm-4.7-flash` |                 |
| `zai/glm-4.7-flashx`|                 |
| `zai/glm-4.6`       |                 |
| `zai/glm-4.6v`      |                 |
| `zai/glm-4.5`       |                 |
| `zai/glm-4.5-air`   |                 |
| `zai/glm-4.5-flash` |                 |
| `zai/glm-4.5v`      |                 |

<Tip>
Modele GLM są dostępne jako `zai/<model>` (przykład: `zai/glm-5`). Domyślne bundlowane odwołanie do modelu to `zai/glm-5.1`.
</Tip>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Rozwiązywanie w przód nieznanych modeli GLM-5">
    Nieznane identyfikatory `glm-5*` nadal są rozwiązywane w przód na ścieżce bundlowanego dostawcy przez
    syntetyzowanie metadanych należących do dostawcy na podstawie szablonu `glm-4.7`, gdy identyfikator
    pasuje do bieżącego kształtu rodziny GLM-5.
  </Accordion>

  <Accordion title="Strumieniowanie wywołań narzędzi">
    `tool_stream` jest domyślnie włączone dla strumieniowania wywołań narzędzi Z.AI. Aby je wyłączyć:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "zai/<model>": {
              params: { tool_stream: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Rozumienie obrazów">
    Bundlowany Plugin Z.AI rejestruje rozumienie obrazów.

    | Właściwość | Wartość    |
    | ---------- | ---------- |
    | Model      | `glm-4.6v` |

    Rozumienie obrazów jest automatycznie rozwiązywane na podstawie skonfigurowanego uwierzytelniania Z.AI — nie
    jest potrzebna dodatkowa konfiguracja.

  </Accordion>

  <Accordion title="Szczegóły uwierzytelniania">
    - Z.AI używa Bearer auth z Twoim kluczem API.
    - Opcja onboardingu `zai-api-key` automatycznie wykrywa pasujący endpoint Z.AI na podstawie prefiksu klucza.
    - Użyj jawnych opcji regionalnych (`zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn`), gdy chcesz wymusić konkretną powierzchnię API.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Rodzina modeli GLM" href="/pl/providers/glm" icon="microchip">
    Przegląd rodziny modeli GLM.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybieranie dostawców, odwołań do modeli i zachowania failover.
  </Card>
</CardGroup>
