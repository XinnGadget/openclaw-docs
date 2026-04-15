---
read_when:
    - Chcesz uruchomić OpenClaw z modelami chmurowymi lub lokalnymi przez Ollama
    - Potrzebujesz wskazówek dotyczących konfiguracji i ustawienia Ollama
summary: Uruchom OpenClaw z Ollama (modele chmurowe i lokalne)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw integruje się z natywnym API Ollama (`/api/chat`) dla hostowanych modeli chmurowych oraz lokalnych/samodzielnie hostowanych serwerów Ollama. Możesz używać Ollama w trzech trybach: `Cloud + Local` przez dostępny host Ollama, `Cloud only` względem `https://ollama.com` albo `Local only` względem dostępnego hosta Ollama.

<Warning>
**Użytkownicy zdalnego Ollama**: Nie używaj adresu URL `/v1` zgodnego z OpenAI (`http://host:11434/v1`) z OpenClaw. To psuje wywoływanie narzędzi i modele mogą zwracać surowy JSON narzędzi jako zwykły tekst. Zamiast tego użyj natywnego adresu URL API Ollama: `baseUrl: "http://host:11434"` (bez `/v1`).
</Warning>

## Pierwsze kroki

Wybierz preferowaną metodę konfiguracji i tryb.

<Tabs>
  <Tab title="Onboarding (zalecane)">
    **Najlepsze dla:** najszybszej drogi do działającej konfiguracji Ollama w chmurze lub lokalnie.

    <Steps>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard
        ```

        Wybierz **Ollama** z listy dostawców.
      </Step>
      <Step title="Wybierz tryb">
        - **Cloud + Local** — lokalny host Ollama plus modele chmurowe kierowane przez tego hosta
        - **Cloud only** — hostowane modele Ollama przez `https://ollama.com`
        - **Local only** — tylko modele lokalne
      </Step>
      <Step title="Wybierz model">
        `Cloud only` prosi o `OLLAMA_API_KEY` i sugeruje domyślne modele chmurowe hostowane. `Cloud + Local` oraz `Local only` proszą o bazowy URL Ollama, wykrywają dostępne modele i automatycznie pobierają wybrany model lokalny, jeśli nie jest jeszcze dostępny. `Cloud + Local` sprawdza też, czy ten host Ollama jest zalogowany do dostępu chmurowego.
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Tryb nieinteraktywny

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    Opcjonalnie podaj niestandardowy bazowy URL lub model:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Konfiguracja ręczna">
    **Najlepsze dla:** pełnej kontroli nad konfiguracją chmurową lub lokalną.

    <Steps>
      <Step title="Wybierz chmurę lub tryb lokalny">
        - **Cloud + Local**: zainstaluj Ollama, zaloguj się przez `ollama signin` i kieruj żądania chmurowe przez tego hosta
        - **Cloud only**: użyj `https://ollama.com` z `OLLAMA_API_KEY`
        - **Local only**: zainstaluj Ollama z [ollama.com/download](https://ollama.com/download)
      </Step>
      <Step title="Pobierz model lokalny (tylko local only)">
        ```bash
        ollama pull gemma4
        # lub
        ollama pull gpt-oss:20b
        # lub
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Włącz Ollama dla OpenClaw">
        Dla `Cloud only` użyj prawdziwego `OLLAMA_API_KEY`. Dla konfiguracji opartych na hoście zadziała dowolna wartość zastępcza:

        ```bash
        # Chmura
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Tylko lokalnie
        export OLLAMA_API_KEY="ollama-local"

        # Lub skonfiguruj w pliku konfiguracyjnym
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź i ustaw model">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Lub ustaw domyślny model w konfiguracji:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Modele chmurowe

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` używa dostępnego hosta Ollama jako punktu sterowania zarówno dla modeli lokalnych, jak i chmurowych. To preferowany przez Ollama hybrydowy przepływ pracy.

    Podczas konfiguracji użyj **Cloud + Local**. OpenClaw poprosi o bazowy URL Ollama, wykryje modele lokalne z tego hosta i sprawdzi, czy host jest zalogowany do dostępu chmurowego przez `ollama signin`. Gdy host jest zalogowany, OpenClaw sugeruje też domyślne hostowane modele chmurowe, takie jak `kimi-k2.5:cloud`, `minimax-m2.7:cloud` i `glm-5.1:cloud`.

    Jeśli host nie jest jeszcze zalogowany, OpenClaw utrzyma konfigurację tylko lokalną, dopóki nie uruchomisz `ollama signin`.

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` działa względem hostowanego API Ollama pod adresem `https://ollama.com`.

    Podczas konfiguracji użyj **Cloud only**. OpenClaw poprosi o `OLLAMA_API_KEY`, ustawi `baseUrl: "https://ollama.com"` i zainicjuje listę hostowanych modeli chmurowych. Ta ścieżka **nie** wymaga lokalnego serwera Ollama ani `ollama signin`.

  </Tab>

  <Tab title="Local only">
    W trybie tylko lokalnym OpenClaw wykrywa modele z skonfigurowanej instancji Ollama. Ta ścieżka jest przeznaczona dla lokalnych lub samodzielnie hostowanych serwerów Ollama.

    OpenClaw obecnie sugeruje `gemma4` jako lokalny model domyślny.

  </Tab>
</Tabs>

## Wykrywanie modeli (provider niejawny)

Gdy ustawisz `OLLAMA_API_KEY` (lub profil auth) i **nie** zdefiniujesz `models.providers.ollama`, OpenClaw wykryje modele z lokalnej instancji Ollama pod adresem `http://127.0.0.1:11434`.

| Zachowanie           | Szczegóły                                                                                                                                                            |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Zapytanie katalogu   | Odpytuje `/api/tags`                                                                                                                                                 |
| Wykrywanie możliwości | Używa wyszukiwań `/api/show` typu best-effort do odczytu `contextWindow` i wykrywania możliwości (w tym vision)                                                    |
| Modele vision        | Modele z możliwością `vision` zgłaszaną przez `/api/show` są oznaczane jako obsługujące obrazy (`input: ["text", "image"]`), więc OpenClaw automatycznie wstrzykuje obrazy do promptu |
| Wykrywanie reasoning | Oznacza `reasoning` za pomocą heurystyki nazwy modelu (`r1`, `reasoning`, `think`)                                                                                  |
| Limity tokenów       | Ustawia `maxTokens` na domyślny limit maksymalnej liczby tokenów Ollama używany przez OpenClaw                                                                     |
| Koszty               | Ustawia wszystkie koszty na `0`                                                                                                                                      |

Pozwala to uniknąć ręcznego definiowania modeli, a jednocześnie utrzymać katalog zgodny z lokalną instancją Ollama.

```bash
# Zobacz, jakie modele są dostępne
ollama list
openclaw models list
```

Aby dodać nowy model, po prostu pobierz go przez Ollama:

```bash
ollama pull mistral
```

Nowy model zostanie automatycznie wykryty i będzie gotowy do użycia.

<Note>
Jeśli jawnie ustawisz `models.providers.ollama`, automatyczne wykrywanie zostanie pominięte i modele trzeba będzie zdefiniować ręcznie. Zobacz sekcję jawnej konfiguracji poniżej.
</Note>

## Konfiguracja

<Tabs>
  <Tab title="Podstawowa (niejawne wykrywanie)">
    Najprostsza ścieżka włączenia trybu tylko lokalnego to zmienna środowiskowa:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    Jeśli `OLLAMA_API_KEY` jest ustawione, możesz pominąć `apiKey` we wpisie providera, a OpenClaw uzupełni je na potrzeby sprawdzania dostępności.
    </Tip>

  </Tab>

  <Tab title="Jawna (modele ręczne)">
    Użyj jawnej konfiguracji, gdy chcesz mieć hostowaną konfigurację chmurową, Ollama działa na innym hoście lub porcie, chcesz wymusić określone okna kontekstu lub listy modeli albo chcesz całkowicie ręcznie definiować modele.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="Niestandardowy bazowy URL">
    Jeśli Ollama działa na innym hoście lub porcie (jawna konfiguracja wyłącza automatyczne wykrywanie, więc zdefiniuj modele ręcznie):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // Bez /v1 - użyj natywnego URL API Ollama
            api: "ollama", // Ustaw jawnie, aby zagwarantować natywne zachowanie wywoływania narzędzi
          },
        },
      },
    }
    ```

    <Warning>
    Nie dodawaj `/v1` do URL-a. Ścieżka `/v1` używa trybu zgodnego z OpenAI, w którym wywoływanie narzędzi nie jest niezawodne. Użyj bazowego URL-a Ollama bez sufiksu ścieżki.
    </Warning>

  </Tab>
</Tabs>

### Wybór modelu

Po skonfigurowaniu wszystkie modele Ollama są dostępne:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Ollama Web Search

OpenClaw obsługuje **Ollama Web Search** jako wbudowanego providera `web_search`.

| Właściwość | Szczegóły                                                                                                            |
| ---------- | -------------------------------------------------------------------------------------------------------------------- |
| Host       | Używa skonfigurowanego hosta Ollama (`models.providers.ollama.baseUrl`, jeśli ustawione, w przeciwnym razie `http://127.0.0.1:11434`) |
| Auth       | Bez klucza                                                                                                           |
| Wymaganie  | Ollama musi działać i być zalogowane przez `ollama signin`                                                           |

Wybierz **Ollama Web Search** podczas `openclaw onboard` lub `openclaw configure --section web`, albo ustaw:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Pełne informacje o konfiguracji i szczegółach działania znajdziesz w [Ollama Web Search](/pl/tools/ollama-search).
</Note>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Starszy tryb zgodny z OpenAI">
    <Warning>
    **Wywoływanie narzędzi nie jest niezawodne w trybie zgodnym z OpenAI.** Używaj tego trybu tylko wtedy, gdy potrzebujesz formatu OpenAI dla proxy i nie polegasz na natywnym zachowaniu wywoływania narzędzi.
    </Warning>

    Jeśli zamiast tego musisz użyć punktu końcowego zgodnego z OpenAI (na przykład za proxy, które obsługuje wyłącznie format OpenAI), ustaw jawnie `api: "openai-completions"`:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // domyślnie: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Ten tryb może nie obsługiwać jednocześnie streamingu i wywoływania narzędzi. Może być konieczne wyłączenie streamingu przez `params: { streaming: false }` w konfiguracji modelu.

    Gdy `api: "openai-completions"` jest używane z Ollama, OpenClaw domyślnie wstrzykuje `options.num_ctx`, aby Ollama nie wracało po cichu do okna kontekstu 4096. Jeśli twoje proxy/upstream odrzuca nieznane pola `options`, wyłącz to zachowanie:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Okna kontekstu">
    Dla modeli wykrywanych automatycznie OpenClaw używa okna kontekstu zgłaszanego przez Ollama, a gdy nie jest ono dostępne, wraca do domyślnego okna kontekstu Ollama używanego przez OpenClaw.

    Możesz nadpisać `contextWindow` i `maxTokens` w jawnej konfiguracji providera:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Modele reasoning">
    OpenClaw domyślnie traktuje modele o nazwach takich jak `deepseek-r1`, `reasoning` lub `think` jako obsługujące reasoning.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Nie jest potrzebna żadna dodatkowa konfiguracja — OpenClaw oznacza je automatycznie.

  </Accordion>

  <Accordion title="Koszty modeli">
    Ollama jest darmowe i działa lokalnie, więc wszystkie koszty modeli są ustawione na $0. Dotyczy to zarówno modeli wykrywanych automatycznie, jak i definiowanych ręcznie.
  </Accordion>

  <Accordion title="Osadzania pamięci">
    Wbudowany Plugin Ollama rejestruje providera osadzań pamięci dla
    [wyszukiwania w pamięci](/pl/concepts/memory). Używa on skonfigurowanego bazowego URL-a Ollama
    i klucza API.

    | Właściwość     | Wartość              |
    | -------------- | -------------------- |
    | Model domyślny | `nomic-embed-text`   |
    | Auto-pull      | Tak — model osadzań jest pobierany automatycznie, jeśli nie jest dostępny lokalnie |

    Aby wybrać Ollama jako providera osadzań dla wyszukiwania w pamięci:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Konfiguracja streamingu">
    Integracja Ollama w OpenClaw domyślnie używa **natywnego API Ollama** (`/api/chat`), które w pełni obsługuje jednocześnie streaming i wywoływanie narzędzi. Nie jest wymagana żadna specjalna konfiguracja.

    <Tip>
    Jeśli musisz użyć punktu końcowego zgodnego z OpenAI, zobacz sekcję „Starszy tryb zgodny z OpenAI” powyżej. W tym trybie streaming i wywoływanie narzędzi mogą nie działać jednocześnie.
    </Tip>

  </Accordion>
</AccordionGroup>

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Nie wykryto Ollama">
    Upewnij się, że Ollama działa, że ustawiono `OLLAMA_API_KEY` (lub profil auth) oraz że **nie** zdefiniowano jawnego wpisu `models.providers.ollama`:

    ```bash
    ollama serve
    ```

    Sprawdź, czy API jest dostępne:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Brak dostępnych modeli">
    Jeśli Twojego modelu nie ma na liście, pobierz go lokalnie albo zdefiniuj jawnie w `models.providers.ollama`.

    ```bash
    ollama list  # Zobacz, co jest zainstalowane
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Lub inny model
    ```

  </Accordion>

  <Accordion title="Odmowa połączenia">
    Sprawdź, czy Ollama działa na poprawnym porcie:

    ```bash
    # Sprawdź, czy Ollama działa
    ps aux | grep ollama

    # Lub uruchom Ollama ponownie
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Więcej pomocy: [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Providerzy modeli" href="/pl/concepts/model-providers" icon="layers">
    Przegląd wszystkich providerów, odwołań do modeli i mechanizmu failover.
  </Card>
  <Card title="Wybór modelu" href="/pl/concepts/models" icon="brain">
    Jak wybierać i konfigurować modele.
  </Card>
  <Card title="Ollama Web Search" href="/pl/tools/ollama-search" icon="magnifying-glass">
    Pełne informacje o konfiguracji i działaniu wyszukiwania w sieci opartego na Ollama.
  </Card>
  <Card title="Konfiguracja" href="/pl/gateway/configuration" icon="gear">
    Pełna referencja konfiguracji.
  </Card>
</CardGroup>
