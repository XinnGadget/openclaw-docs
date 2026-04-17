---
read_when:
    - Chcesz używać modeli Mistral w OpenClaw
    - Potrzebujesz onboardingu z kluczem API Mistral i referencji modeli
summary: Używaj modeli Mistral i transkrypcji Voxtral z OpenClaw
title: Mistral
x-i18n:
    generated_at: "2026-04-12T23:31:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0474f55587909ce9bbdd47b881262edbeb1b07eb3ed52de1090a8ec4d260c97b
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw obsługuje Mistral zarówno do routingu modeli tekstowych/obrazowych (`mistral/...`), jak i
transkrypcji audio przez Voxtral w media understanding.
Mistral może być także używany do embeddings pamięci (`memorySearch.provider = "mistral"`).

- Dostawca: `mistral`
- Uwierzytelnianie: `MISTRAL_API_KEY`
- API: Mistral Chat Completions (`https://api.mistral.ai/v1`)

## Pierwsze kroki

<Steps>
  <Step title="Pobierz klucz API">
    Utwórz klucz API w [Mistral Console](https://console.mistral.ai/).
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice mistral-api-key
    ```

    Lub przekaż klucz bezpośrednio:

    ```bash
    openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
    ```

  </Step>
  <Step title="Ustaw model domyślny">
    ```json5
    {
      env: { MISTRAL_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
    }
    ```
  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider mistral
    ```
  </Step>
</Steps>

## Wbudowany katalog LLM

OpenClaw obecnie dostarcza ten dołączony katalog Mistral:

| Ref modelu                       | Wejście     | Kontekst | Maks. wyjście | Uwagi                                                            |
| -------------------------------- | ----------- | -------- | ------------- | ---------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | text, image | 262,144  | 16,384        | Model domyślny                                                   |
| `mistral/mistral-medium-2508`    | text, image | 262,144  | 8,192         | Mistral Medium 3.1                                               |
| `mistral/mistral-small-latest`   | text, image | 128,000  | 16,384        | Mistral Small 4; regulowane rozumowanie przez API `reasoning_effort` |
| `mistral/pixtral-large-latest`   | text, image | 128,000  | 32,768        | Pixtral                                                          |
| `mistral/codestral-latest`       | text        | 256,000  | 4,096         | Kodowanie                                                        |
| `mistral/devstral-medium-latest` | text        | 262,144  | 32,768        | Devstral 2                                                       |
| `mistral/magistral-small`        | text        | 128,000  | 40,000        | Rozumowanie włączone                                             |

## Transkrypcja audio (Voxtral)

Używaj Voxtral do transkrypcji audio przez pipeline media understanding.

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

<Tip>
Ścieżka transkrypcji mediów używa `/v1/audio/transcriptions`. Domyślny model audio dla Mistral to `voxtral-mini-latest`.
</Tip>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Regulowane rozumowanie (`mistral-small-latest`)">
    `mistral/mistral-small-latest` mapuje do Mistral Small 4 i obsługuje [regulowane rozumowanie](https://docs.mistral.ai/capabilities/reasoning/adjustable) w Chat Completions API przez `reasoning_effort` (`none` minimalizuje dodatkowe myślenie w odpowiedzi; `high` pokazuje pełne ślady myślenia przed odpowiedzią końcową).

    OpenClaw mapuje poziom **thinking** sesji na API Mistral:

    | Poziom thinking w OpenClaw                      | Mistral `reasoning_effort` |
    | ----------------------------------------------- | -------------------------- |
    | **off** / **minimal**                           | `none`                     |
    | **low** / **medium** / **high** / **xhigh** / **adaptive** | `high`         |

    <Note>
    Pozostałe modele z dołączonego katalogu Mistral nie używają tego parametru. Nadal używaj modeli `magistral-*`, gdy chcesz korzystać z natywnego dla Mistral zachowania nastawionego na rozumowanie.
    </Note>

  </Accordion>

  <Accordion title="Embeddings pamięci">
    Mistral może udostępniać embeddings pamięci przez `/v1/embeddings` (model domyślny: `mistral-embed`).

    ```json5
    {
      memorySearch: { provider: "mistral" },
    }
    ```

  </Accordion>

  <Accordion title="Uwierzytelnianie i bazowy URL">
    - Uwierzytelnianie Mistral używa `MISTRAL_API_KEY`.
    - Bazowy URL dostawcy domyślnie to `https://api.mistral.ai/v1`.
    - Domyślnym modelem w onboardingu jest `mistral/mistral-large-latest`.
    - Z.AI używa uwierzytelniania Bearer z Twoim kluczem API.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Media understanding" href="/tools/media-understanding" icon="microphone">
    Konfiguracja transkrypcji audio i wybór dostawcy.
  </Card>
</CardGroup>
