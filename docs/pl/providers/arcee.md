---
read_when:
    - Chcesz używać Arcee AI z OpenClaw
    - Potrzebujesz zmiennej środowiskowej klucza API lub opcji uwierzytelniania w CLI
summary: Konfiguracja Arcee AI (uwierzytelnianie + wybór modelu)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T23:29:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) zapewnia dostęp do rodziny modeli typu mixture-of-experts Trinity przez API zgodne z OpenAI. Wszystkie modele Trinity są licencjonowane na Apache 2.0.

Do modeli Arcee AI można uzyskać dostęp bezpośrednio przez platformę Arcee lub przez [OpenRouter](/pl/providers/openrouter).

| Właściwość | Wartość                                                                              |
| ---------- | ------------------------------------------------------------------------------------ |
| Dostawca   | `arcee`                                                                              |
| Uwierzytelnianie | `ARCEEAI_API_KEY` (bezpośrednio) lub `OPENROUTER_API_KEY` (przez OpenRouter) |
| API        | zgodne z OpenAI                                                                      |
| Bazowy URL | `https://api.arcee.ai/api/v1` (bezpośrednio) lub `https://openrouter.ai/api/v1` (OpenRouter) |

## Pierwsze kroki

<Tabs>
  <Tab title="Bezpośrednio (platforma Arcee)">
    <Steps>
      <Step title="Pobierz klucz API">
        Utwórz klucz API w [Arcee AI](https://chat.arcee.ai/).
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Przez OpenRouter">
    <Steps>
      <Step title="Pobierz klucz API">
        Utwórz klucz API w [OpenRouter](https://openrouter.ai/keys).
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        Te same referencje modeli działają zarówno dla konfiguracji bezpośredniej, jak i przez OpenRouter (na przykład `arcee/trinity-large-thinking`).
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Konfiguracja nieinteraktywna

<Tabs>
  <Tab title="Bezpośrednio (platforma Arcee)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="Przez OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## Wbudowany katalog

OpenClaw obecnie dostarcza ten dołączony katalog Arcee:

| Ref modelu                     | Nazwa                  | Wejście | Kontekst | Koszt (wej./wyj. na 1 mln) | Uwagi                                     |
| ------------------------------ | ---------------------- | ------- | -------- | -------------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text    | 256K     | $0.25 / $0.90              | Model domyślny; rozumowanie włączone      |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text    | 128K     | $0.25 / $1.00              | Ogólnego przeznaczenia; 400B parametrów, 13B aktywnych |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text    | 128K     | $0.045 / $0.15             | Szybki i opłacalny; function calling      |

<Tip>
Preset onboarding ustawia `arcee/trinity-large-thinking` jako model domyślny.
</Tip>

## Obsługiwane funkcje

| Funkcja                                      | Obsługiwane                  |
| -------------------------------------------- | ---------------------------- |
| Streaming                                    | Tak                          |
| Użycie narzędzi / function calling           | Tak                          |
| Dane wyjściowe strukturalne (tryb JSON i schemat JSON) | Tak               |
| Rozszerzone myślenie                         | Tak (Trinity Large Thinking) |

<AccordionGroup>
  <Accordion title="Uwaga dotycząca środowiska">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `ARCEEAI_API_KEY`
    (lub `OPENROUTER_API_KEY`) jest dostępny dla tego procesu (na przykład w
    `~/.openclaw/.env` lub przez `env.shellEnv`).
  </Accordion>

  <Accordion title="Routing OpenRouter">
    Podczas używania modeli Arcee przez OpenRouter obowiązują te same referencje modeli `arcee/*`.
    OpenClaw obsługuje routing transparentnie na podstawie wybranego sposobu uwierzytelniania. Zobacz
    [dokumentację dostawcy OpenRouter](/pl/providers/openrouter), aby poznać szczegóły konfiguracji
    specyficzne dla OpenRouter.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/pl/providers/openrouter" icon="shuffle">
    Uzyskaj dostęp do modeli Arcee i wielu innych przez jeden klucz API.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
</CardGroup>
