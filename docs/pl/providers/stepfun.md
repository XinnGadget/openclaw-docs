---
read_when:
    - Chcesz używać modeli StepFun w OpenClaw
    - Potrzebujesz wskazówek konfiguracji StepFun
summary: Używaj modeli StepFun z OpenClaw
title: StepFun
x-i18n:
    generated_at: "2026-04-12T23:33:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: a463bed0951d33802dcdb3a7784406272ee206b731e9864ea020323e67b4d159
    source_path: providers/stepfun.md
    workflow: 15
---

# StepFun

OpenClaw zawiera dołączony Plugin dostawcy StepFun z dwoma identyfikatorami dostawców:

- `stepfun` dla standardowego endpointu
- `stepfun-plan` dla endpointu Step Plan

<Warning>
Standard i Step Plan to **oddzielni dostawcy** z różnymi endpointami i prefiksami referencji modeli (`stepfun/...` vs `stepfun-plan/...`). Używaj klucza China z endpointami `.com`, a klucza globalnego z endpointami `.ai`.
</Warning>

## Przegląd regionów i endpointów

| Endpoint  | Chiny (`.com`)                        | Globalny (`.ai`)                      |
| --------- | ------------------------------------- | ------------------------------------- |
| Standard  | `https://api.stepfun.com/v1`          | `https://api.stepfun.ai/v1`           |
| Step Plan | `https://api.stepfun.com/step_plan/v1` | `https://api.stepfun.ai/step_plan/v1` |

Zmienna środowiskowa uwierzytelniania: `STEPFUN_API_KEY`

## Wbudowane katalogi

Standard (`stepfun`):

| Ref modelu               | Kontekst | Maks. wyjście | Uwagi                    |
| ------------------------ | -------- | ------------- | ------------------------ |
| `stepfun/step-3.5-flash` | 262,144  | 65,536        | Domyślny model standardowy |

Step Plan (`stepfun-plan`):

| Ref modelu                         | Kontekst | Maks. wyjście | Uwagi                        |
| ---------------------------------- | -------- | ------------- | ---------------------------- |
| `stepfun-plan/step-3.5-flash`      | 262,144  | 65,536        | Domyślny model Step Plan     |
| `stepfun-plan/step-3.5-flash-2603` | 262,144  | 65,536        | Dodatkowy model Step Plan    |

## Pierwsze kroki

Wybierz powierzchnię dostawcy i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Standard">
    **Najlepsze dla:** ogólnego użycia przez standardowy endpoint StepFun.

    <Steps>
      <Step title="Wybierz region endpointu">
        | Opcja uwierzytelniania          | Endpoint                       | Region         |
        | -------------------------------- | ------------------------------ | -------------- |
        | `stepfun-standard-api-key-intl`  | `https://api.stepfun.ai/v1`    | Międzynarodowy |
        | `stepfun-standard-api-key-cn`    | `https://api.stepfun.com/v1`   | Chiny          |
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl
        ```

        Lub dla endpointu China:

        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-cn
        ```
      </Step>
      <Step title="Alternatywa nieinteraktywna">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider stepfun
        ```
      </Step>
    </Steps>

    ### Referencje modeli

    - Model domyślny: `stepfun/step-3.5-flash`

  </Tab>

  <Tab title="Step Plan">
    **Najlepsze dla:** endpointu rozumowania Step Plan.

    <Steps>
      <Step title="Wybierz region endpointu">
        | Opcja uwierzytelniania        | Endpoint                               | Region         |
        | ----------------------------- | -------------------------------------- | -------------- |
        | `stepfun-plan-api-key-intl`   | `https://api.stepfun.ai/step_plan/v1`  | Międzynarodowy |
        | `stepfun-plan-api-key-cn`     | `https://api.stepfun.com/step_plan/v1` | Chiny          |
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl
        ```

        Lub dla endpointu China:

        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-cn
        ```
      </Step>
      <Step title="Alternatywa nieinteraktywna">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider stepfun-plan
        ```
      </Step>
    </Steps>

    ### Referencje modeli

    - Model domyślny: `stepfun-plan/step-3.5-flash`
    - Model alternatywny: `stepfun-plan/step-3.5-flash-2603`

  </Tab>
</Tabs>

## Zaawansowane

<AccordionGroup>
  <Accordion title="Pełna konfiguracja: dostawca Standard">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          stepfun: {
            baseUrl: "https://api.stepfun.ai/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Pełna konfiguracja: dostawca Step Plan">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun-plan/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          "stepfun-plan": {
            baseUrl: "https://api.stepfun.ai/step_plan/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
              {
                id: "step-3.5-flash-2603",
                name: "Step 3.5 Flash 2603",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Uwagi">
    - Dostawca jest dołączony do OpenClaw, więc nie ma osobnego kroku instalacji Pluginu.
    - `step-3.5-flash-2603` jest obecnie udostępniany tylko przez `stepfun-plan`.
    - Jeden przepływ uwierzytelniania zapisuje profile dopasowane do regionu zarówno dla `stepfun`, jak i `stepfun-plan`, dzięki czemu obie powierzchnie mogą być wykrywane razem.
    - Użyj `openclaw models list` oraz `openclaw models set <provider/model>`, aby sprawdzać lub przełączać modele.
  </Accordion>
</AccordionGroup>

<Note>
Szerszy przegląd dostawców znajdziesz w [Model providers](/pl/concepts/model-providers).
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Model providers" href="/pl/concepts/model-providers" icon="layers">
    Przegląd wszystkich dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Configuration reference" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji dostawców, modeli i Pluginów.
  </Card>
  <Card title="Model selection" href="/pl/concepts/models" icon="brain">
    Jak wybierać i konfigurować modele.
  </Card>
  <Card title="StepFun Platform" href="https://platform.stepfun.com" icon="globe">
    Zarządzanie kluczami API StepFun i dokumentacja.
  </Card>
</CardGroup>
