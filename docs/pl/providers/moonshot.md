---
read_when:
    - Chcesz skonfigurować Moonshot K2 (Moonshot Open Platform) oraz Kimi Coding
    - Musisz zrozumieć oddzielne endpointy, klucze i odwołania do modeli
    - Chcesz konfigurację do skopiowania i wklejenia dla dowolnego z dostawców
summary: Skonfiguruj Moonshot K2 i Kimi Coding (oddzielni dostawcy + klucze)
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-12T23:32:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f261f83a9b37e4fffb0cd0803e0c64f27eae8bae91b91d8a781a030663076f8
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI (Kimi)

Moonshot udostępnia API Kimi z endpointami zgodnymi z OpenAI. Skonfiguruj
dostawcę i ustaw domyślny model na `moonshot/kimi-k2.5`, albo użyj
Kimi Coding z `kimi/kimi-code`.

<Warning>
Moonshot i Kimi Coding to **oddzielni dostawcy**. Klucze nie są zamienne, endpointy są różne, a odwołania do modeli też się różnią (`moonshot/...` vs `kimi/...`).
</Warning>

## Wbudowany katalog modeli

[//]: # "moonshot-kimi-k2-ids:start"

| Odwołanie modelu                 | Nazwa                  | Reasoning | Wejście     | Kontekst | Maks. wyjście |
| -------------------------------- | ---------------------- | --------- | ----------- | -------- | ------------- |
| `moonshot/kimi-k2.5`             | Kimi K2.5              | Nie       | text, image | 262,144  | 262,144       |
| `moonshot/kimi-k2-thinking`      | Kimi K2 Thinking       | Tak       | text        | 262,144  | 262,144       |
| `moonshot/kimi-k2-thinking-turbo`| Kimi K2 Thinking Turbo | Tak       | text        | 262,144  | 262,144       |
| `moonshot/kimi-k2-turbo`         | Kimi K2 Turbo          | Nie       | text        | 256,000  | 16,384        |

[//]: # "moonshot-kimi-k2-ids:end"

## Pierwsze kroki

Wybierz dostawcę i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Moonshot API">
    **Najlepsze do:** modeli Kimi K2 przez Moonshot Open Platform.

    <Steps>
      <Step title="Wybierz region endpointu">
        | Wybór uwierzytelniania   | Endpoint                     | Region         |
        | ------------------------ | ---------------------------- | -------------- |
        | `moonshot-api-key`       | `https://api.moonshot.ai/v1` | Międzynarodowy |
        | `moonshot-api-key-cn`    | `https://api.moonshot.cn/v1` | Chiny          |
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice moonshot-api-key
        ```

        Albo dla endpointu w Chinach:

        ```bash
        openclaw onboard --auth-choice moonshot-api-key-cn
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "moonshot/kimi-k2.5" },
            },
          },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy modele są dostępne">
        ```bash
        openclaw models list --provider moonshot
        ```
      </Step>
    </Steps>

    ### Przykład konfiguracji

    ```json5
    {
      env: { MOONSHOT_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "moonshot/kimi-k2.5" },
          models: {
            // moonshot-kimi-k2-aliases:start
            "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
            "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
            "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
            "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
            // moonshot-kimi-k2-aliases:end
          },
        },
      },
      models: {
        mode: "merge",
        providers: {
          moonshot: {
            baseUrl: "https://api.moonshot.ai/v1",
            apiKey: "${MOONSHOT_API_KEY}",
            api: "openai-completions",
            models: [
              // moonshot-kimi-k2-models:start
              {
                id: "kimi-k2.5",
                name: "Kimi K2.5",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking",
                name: "Kimi K2 Thinking",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking-turbo",
                name: "Kimi K2 Thinking Turbo",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-turbo",
                name: "Kimi K2 Turbo",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 16384,
              },
              // moonshot-kimi-k2-models:end
            ],
          },
        },
      },
    }
    ```

  </Tab>

  <Tab title="Kimi Coding">
    **Najlepsze do:** zadań skoncentrowanych na kodzie przez endpoint Kimi Coding.

    <Note>
    Kimi Coding używa innego klucza API i prefiksu dostawcy (`kimi/...`) niż Moonshot (`moonshot/...`). Starsze odwołanie do modelu `kimi/k2p5` pozostaje akceptowane jako identyfikator zgodności.
    </Note>

    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice kimi-code-api-key
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "kimi/kimi-code" },
            },
          },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider kimi
        ```
      </Step>
    </Steps>

    ### Przykład konfiguracji

    ```json5
    {
      env: { KIMI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "kimi/kimi-code" },
          models: {
            "kimi/kimi-code": { alias: "Kimi" },
          },
        },
      },
    }
    ```

  </Tab>
</Tabs>

## Wyszukiwanie w sieci Kimi

OpenClaw zawiera też **Kimi** jako dostawcę `web_search`, oparty na wyszukiwaniu w sieci Moonshot.

<Steps>
  <Step title="Uruchom interaktywną konfigurację wyszukiwania w sieci">
    ```bash
    openclaw configure --section web
    ```

    W sekcji wyszukiwania w sieci wybierz **Kimi**, aby zapisać
    `plugins.entries.moonshot.config.webSearch.*`.

  </Step>
  <Step title="Skonfiguruj region wyszukiwania w sieci i model">
    Interaktywna konfiguracja pyta o:

    | Ustawienie          | Opcje                                                               |
    | ------------------- | ------------------------------------------------------------------- |
    | Region API          | `https://api.moonshot.ai/v1` (międzynarodowy) lub `https://api.moonshot.cn/v1` (Chiny) |
    | Model wyszukiwania w sieci | Domyślnie `kimi-k2.5`                                       |

  </Step>
</Steps>

Konfiguracja znajduje się pod `plugins.entries.moonshot.config.webSearch`:

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // lub użyj KIMI_API_KEY / MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## Zaawansowane

<AccordionGroup>
  <Accordion title="Natywny tryb thinking">
    Moonshot Kimi obsługuje binarny natywny tryb thinking:

    - `thinking: { type: "enabled" }`
    - `thinking: { type: "disabled" }`

    Skonfiguruj go per model przez `agents.defaults.models.<provider/model>.params`:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "moonshot/kimi-k2.5": {
              params: {
                thinking: { type: "disabled" },
              },
            },
          },
        },
      },
    }
    ```

    OpenClaw mapuje też poziomy `/think` w czasie działania dla Moonshot:

    | Poziom `/think`      | Zachowanie Moonshot        |
    | -------------------- | -------------------------- |
    | `/think off`         | `thinking.type=disabled`   |
    | Dowolny poziom inny niż off | `thinking.type=enabled` |

    <Warning>
    Gdy thinking Moonshot jest włączone, `tool_choice` musi mieć wartość `auto` albo `none`. OpenClaw normalizuje niezgodne wartości `tool_choice` do `auto` dla zgodności.
    </Warning>

  </Accordion>

  <Accordion title="Zgodność użycia streamingu">
    Natywne endpointy Moonshot (`https://api.moonshot.ai/v1` i
    `https://api.moonshot.cn/v1`) deklarują zgodność użycia streamingu na
    współdzielonym transporcie `openai-completions`. OpenClaw opiera się na możliwościach endpointu,
    więc zgodne niestandardowe identyfikatory dostawców kierujące na te same natywne
    hosty Moonshot dziedziczą to samo zachowanie użycia streamingu.
  </Accordion>

  <Accordion title="Referencja endpointów i odwołań do modeli">
    | Dostawca     | Prefiks odwołania modelu | Endpoint                     | Zmienna środowiskowa uwierzytelniania |
    | ------------ | ------------------------ | ---------------------------- | ------------------------------------- |
    | Moonshot     | `moonshot/`              | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY`                    |
    | Moonshot CN  | `moonshot/`              | `https://api.moonshot.cn/v1` | `MOONSHOT_API_KEY`                    |
    | Kimi Coding  | `kimi/`                  | endpoint Kimi Coding         | `KIMI_API_KEY`                        |
    | Wyszukiwanie w sieci | N/A            | Taki sam jak region API Moonshot | `KIMI_API_KEY` lub `MOONSHOT_API_KEY` |

    - Wyszukiwanie w sieci Kimi używa `KIMI_API_KEY` lub `MOONSHOT_API_KEY`, a domyślnie korzysta z `https://api.moonshot.ai/v1` z modelem `kimi-k2.5`.
    - W razie potrzeby nadpisz ceny i metadane kontekstowe w `models.providers`.
    - Jeśli Moonshot opublikuje inne limity kontekstu dla modelu, odpowiednio dostosuj `contextWindow`.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Wyszukiwanie w sieci" href="/tools/web-search" icon="magnifying-glass">
    Konfigurowanie dostawców wyszukiwania w sieci, w tym Kimi.
  </Card>
  <Card title="Referencja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji dostawców, modeli i Plugin.
  </Card>
  <Card title="Moonshot Open Platform" href="https://platform.moonshot.ai" icon="globe">
    Zarządzanie kluczami API Moonshot i dokumentacja.
  </Card>
</CardGroup>
