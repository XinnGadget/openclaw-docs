---
read_when:
    - Chcesz używać modeli OpenAI w OpenClaw
    - Chcesz uwierzytelniania subskrypcją Codex zamiast kluczy API
    - Potrzebujesz bardziej rygorystycznego zachowania wykonywania agenta GPT-5
summary: Używaj OpenAI przez klucze API lub subskrypcję Codex w OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T23:32:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aeb756618c5611fed56e4bf89015a2304ff2e21596104b470ec6e7cb459d1c9
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI udostępnia API deweloperskie dla modeli GPT. OpenClaw obsługuje dwie ścieżki uwierzytelniania:

- **Klucz API** — bezpośredni dostęp do OpenAI Platform z rozliczaniem usage-based (`openai/*` modeli)
- **Subskrypcja Codex** — logowanie ChatGPT/Codex z dostępem w ramach subskrypcji (`openai-codex/*` modeli)

OpenAI jawnie wspiera użycie OAuth subskrypcji w zewnętrznych narzędziach i przepływach pracy takich jak OpenClaw.

## Pierwsze kroki

Wybierz preferowaną metodę uwierzytelniania i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Klucz API (OpenAI Platform)">
    **Najlepsze dla:** bezpośredniego dostępu do API i rozliczania usage-based.

    <Steps>
      <Step title="Pobierz klucz API">
        Utwórz lub skopiuj klucz API z [panelu OpenAI Platform](https://platform.openai.com/api-keys).
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard --auth-choice openai-api-key
        ```

        Lub przekaż klucz bezpośrednio:

        ```bash
        openclaw onboard --openai-api-key "$OPENAI_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider openai
        ```
      </Step>
    </Steps>

    ### Podsumowanie ścieżki

    | Ref modelu | Ścieżka | Uwierzytelnianie |
    |-----------|-------|------|
    | `openai/gpt-5.4` | Bezpośrednie API OpenAI Platform | `OPENAI_API_KEY` |
    | `openai/gpt-5.4-pro` | Bezpośrednie API OpenAI Platform | `OPENAI_API_KEY` |

    <Note>
    Logowanie ChatGPT/Codex jest routowane przez `openai-codex/*`, a nie `openai/*`.
    </Note>

    ### Przykład konfiguracji

    ```json5
    {
      env: { OPENAI_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
    }
    ```

    <Warning>
    OpenClaw **nie** udostępnia `openai/gpt-5.3-codex-spark` na bezpośredniej ścieżce API. Żądania do live OpenAI API odrzucają ten model. Spark jest dostępny tylko w Codex.
    </Warning>

  </Tab>

  <Tab title="Subskrypcja Codex">
    **Najlepsze dla:** używania subskrypcji ChatGPT/Codex zamiast osobnego klucza API. Chmura Codex wymaga logowania ChatGPT.

    <Steps>
      <Step title="Uruchom OAuth Codex">
        ```bash
        openclaw onboard --auth-choice openai-codex
        ```

        Lub uruchom OAuth bezpośrednio:

        ```bash
        openclaw models auth login --provider openai-codex
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```bash
        openclaw config set agents.defaults.model.primary openai-codex/gpt-5.4
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider openai-codex
        ```
      </Step>
    </Steps>

    ### Podsumowanie ścieżki

    | Ref modelu | Ścieżka | Uwierzytelnianie |
    |-----------|-------|------|
    | `openai-codex/gpt-5.4` | OAuth ChatGPT/Codex | Logowanie Codex |
    | `openai-codex/gpt-5.3-codex-spark` | OAuth ChatGPT/Codex | Logowanie Codex (zależne od uprawnień) |

    <Note>
    Ta ścieżka jest celowo oddzielona od `openai/gpt-5.4`. Używaj `openai/*` z kluczem API do bezpośredniego dostępu do Platform, a `openai-codex/*` do dostępu w ramach subskrypcji Codex.
    </Note>

    ### Przykład konfiguracji

    ```json5
    {
      agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
    }
    ```

    <Tip>
    Jeśli onboarding ponownie wykorzystuje istniejące logowanie Codex CLI, te poświadczenia pozostają zarządzane przez Codex CLI. Po wygaśnięciu OpenClaw najpierw ponownie odczytuje zewnętrzne źródło Codex, a następnie zapisuje odświeżone poświadczenia z powrotem do magazynu Codex.
    </Tip>

    ### Limit okna kontekstu

    OpenClaw traktuje metadane modelu i limit kontekstu runtime jako oddzielne wartości.

    Dla `openai-codex/gpt-5.4`:

    - Natywne `contextWindow`: `1050000`
    - Domyślny limit runtime `contextTokens`: `272000`

    Mniejszy domyślny limit w praktyce daje lepszą latencję i jakość. Nadpisz go za pomocą `contextTokens`:

    ```json5
    {
      models: {
        providers: {
          "openai-codex": {
            models: [{ id: "gpt-5.4", contextTokens: 160000 }],
          },
        },
      },
    }
    ```

    <Note>
    Używaj `contextWindow`, aby deklarować natywne metadane modelu. Używaj `contextTokens`, aby ograniczać budżet kontekstu runtime.
    </Note>

  </Tab>
</Tabs>

## Generowanie obrazów

Dołączony Plugin `openai` rejestruje generowanie obrazów przez narzędzie `image_generate`.

| Możliwość                | Wartość                            |
| ------------------------ | ---------------------------------- |
| Model domyślny           | `openai/gpt-image-1`               |
| Maks. liczba obrazów na żądanie | 4                           |
| Tryb edycji              | Włączony (do 5 obrazów referencyjnych) |
| Nadpisania rozmiaru      | Obsługiwane                        |
| Proporcje obrazu / rozdzielczość | Nie są przekazywane do OpenAI Images API |

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "openai/gpt-image-1" },
    },
  },
}
```

<Note>
Zobacz [Image Generation](/pl/tools/image-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

## Generowanie wideo

Dołączony Plugin `openai` rejestruje generowanie wideo przez narzędzie `video_generate`.

| Możliwość       | Wartość                                                                           |
| --------------- | --------------------------------------------------------------------------------- |
| Model domyślny  | `openai/sora-2`                                                                   |
| Tryby           | Tekst-na-wideo, obraz-na-wideo, edycja pojedynczego wideo                         |
| Wejścia referencyjne | 1 obraz lub 1 wideo                                                          |
| Nadpisania rozmiaru | Obsługiwane                                                                   |
| Inne nadpisania | `aspectRatio`, `resolution`, `audio`, `watermark` są ignorowane z ostrzeżeniem narzędzia |

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "openai/sora-2" },
    },
  },
}
```

<Note>
Zobacz [Video Generation](/pl/tools/video-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

## Nakładka osobowości

OpenClaw dodaje małą nakładkę promptu specyficzną dla OpenAI dla uruchomień `openai/*` i `openai-codex/*`. Nakładka sprawia, że asystent pozostaje ciepły, współpracujący, zwięzły i trochę bardziej ekspresyjny emocjonalnie, bez zastępowania bazowego promptu systemowego.

| Wartość               | Efekt                                |
| --------------------- | ------------------------------------ |
| `"friendly"` (domyślnie) | Włącza nakładkę specyficzną dla OpenAI |
| `"on"`                | Alias dla `"friendly"`               |
| `"off"`               | Używa tylko bazowego promptu OpenClaw |

<Tabs>
  <Tab title="Konfiguracja">
    ```json5
    {
      plugins: {
        entries: {
          openai: { config: { personality: "friendly" } },
        },
      },
    }
    ```
  </Tab>
  <Tab title="CLI">
    ```bash
    openclaw config set plugins.entries.openai.config.personality off
    ```
  </Tab>
</Tabs>

<Tip>
Wartości są niewrażliwe na wielkość liter w runtime, więc zarówno `"Off"`, jak i `"off"` wyłączają nakładkę.
</Tip>

## Głos i mowa

<AccordionGroup>
  <Accordion title="Synteza mowy (TTS)">
    Dołączony Plugin `openai` rejestruje syntezę mowy dla powierzchni `messages.tts`.

    | Ustawienie | Ścieżka konfiguracji | Domyślnie |
    |---------|------------|---------|
    | Model | `messages.tts.providers.openai.model` | `gpt-4o-mini-tts` |
    | Głos | `messages.tts.providers.openai.voice` | `coral` |
    | Szybkość | `messages.tts.providers.openai.speed` | (nieustawione) |
    | Instrukcje | `messages.tts.providers.openai.instructions` | (nieustawione, tylko `gpt-4o-mini-tts`) |
    | Format | `messages.tts.providers.openai.responseFormat` | `opus` dla notatek głosowych, `mp3` dla plików |
    | Klucz API | `messages.tts.providers.openai.apiKey` | Fallback do `OPENAI_API_KEY` |
    | Bazowy URL | `messages.tts.providers.openai.baseUrl` | `https://api.openai.com/v1` |

    Dostępne modele: `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`. Dostępne głosy: `alloy`, `ash`, `ballad`, `cedar`, `coral`, `echo`, `fable`, `juniper`, `marin`, `onyx`, `nova`, `sage`, `shimmer`, `verse`.

    ```json5
    {
      messages: {
        tts: {
          providers: {
            openai: { model: "gpt-4o-mini-tts", voice: "coral" },
          },
        },
      },
    }
    ```

    <Note>
    Ustaw `OPENAI_TTS_BASE_URL`, aby nadpisać bazowy URL TTS bez wpływu na endpoint API czatu.
    </Note>

  </Accordion>

  <Accordion title="Transkrypcja realtime">
    Dołączony Plugin `openai` rejestruje transkrypcję realtime dla Pluginu Voice Call.

    | Ustawienie | Ścieżka konfiguracji | Domyślnie |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.streaming.providers.openai.model` | `gpt-4o-transcribe` |
    | Czas trwania ciszy | `...openai.silenceDurationMs` | `800` |
    | Próg VAD | `...openai.vadThreshold` | `0.5` |
    | Klucz API | `...openai.apiKey` | Fallback do `OPENAI_API_KEY` |

    <Note>
    Używa połączenia WebSocket z `wss://api.openai.com/v1/realtime` z dźwiękiem G.711 u-law.
    </Note>

  </Accordion>

  <Accordion title="Głos realtime">
    Dołączony Plugin `openai` rejestruje głos realtime dla Pluginu Voice Call.

    | Ustawienie | Ścieżka konfiguracji | Domyślnie |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.realtime.providers.openai.model` | `gpt-realtime` |
    | Głos | `...openai.voice` | `alloy` |
    | Temperatura | `...openai.temperature` | `0.8` |
    | Próg VAD | `...openai.vadThreshold` | `0.5` |
    | Czas trwania ciszy | `...openai.silenceDurationMs` | `500` |
    | Klucz API | `...openai.apiKey` | Fallback do `OPENAI_API_KEY` |

    <Note>
    Obsługuje Azure OpenAI przez klucze konfiguracyjne `azureEndpoint` i `azureDeployment`. Obsługuje dwukierunkowe wywoływanie narzędzi. Używa formatu audio G.711 u-law.
    </Note>

  </Accordion>
</AccordionGroup>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Transport (WebSocket vs SSE)">
    OpenClaw używa podejścia WebSocket-first z fallbackiem do SSE (`"auto"`) zarówno dla `openai/*`, jak i `openai-codex/*`.

    W trybie `"auto"` OpenClaw:
    - Ponawia jedną wczesną awarię WebSocket przed przejściem do SSE
    - Po awarii oznacza WebSocket jako zdegradowany na około 60 sekund i używa SSE podczas okresu schłodzenia
    - Dołącza stabilne nagłówki tożsamości sesji i tury do ponowień i ponownych połączeń
    - Normalizuje liczniki użycia (`input_tokens` / `prompt_tokens`) między wariantami transportu

    | Wartość | Zachowanie |
    |-------|----------|
    | `"auto"` (domyślnie) | Najpierw WebSocket, fallback do SSE |
    | `"sse"` | Wymuś tylko SSE |
    | `"websocket"` | Wymuś tylko WebSocket |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai-codex/gpt-5.4": {
              params: { transport: "auto" },
            },
          },
        },
      },
    }
    ```

    Powiązana dokumentacja OpenAI:
    - [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
    - [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

  </Accordion>

  <Accordion title="Rozgrzewanie WebSocket">
    OpenClaw domyślnie włącza rozgrzewanie WebSocket dla `openai/*`, aby zmniejszyć opóźnienie pierwszej tury.

    ```json5
    // Wyłącz rozgrzewanie
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: { openaiWsWarmup: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Tryb fast">
    OpenClaw udostępnia wspólny przełącznik trybu fast zarówno dla `openai/*`, jak i `openai-codex/*`:

    - **Czat/UI:** `/fast status|on|off`
    - **Konfiguracja:** `agents.defaults.models["<provider>/<model>"].params.fastMode`

    Po włączeniu OpenClaw mapuje tryb fast na przetwarzanie priorytetowe OpenAI (`service_tier = "priority"`). Istniejące wartości `service_tier` są zachowywane, a tryb fast nie nadpisuje `reasoning` ani `text.verbosity`.

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { fastMode: true } },
            "openai-codex/gpt-5.4": { params: { fastMode: true } },
          },
        },
      },
    }
    ```

    <Note>
    Nadpisania sesji mają pierwszeństwo przed konfiguracją. Wyczyszczenie nadpisania sesji w UI Sessions przywraca sesję do skonfigurowanej wartości domyślnej.
    </Note>

  </Accordion>

  <Accordion title="Przetwarzanie priorytetowe (`service_tier`)">
    API OpenAI udostępnia przetwarzanie priorytetowe przez `service_tier`. Ustaw je dla każdego modelu w OpenClaw:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { serviceTier: "priority" } },
            "openai-codex/gpt-5.4": { params: { serviceTier: "priority" } },
          },
        },
      },
    }
    ```

    Obsługiwane wartości: `auto`, `default`, `flex`, `priority`.

    <Warning>
    `serviceTier` jest przekazywane tylko do natywnych endpointów OpenAI (`api.openai.com`) i natywnych endpointów Codex (`chatgpt.com/backend-api`). Jeśli kierujesz któregoś z tych dostawców przez proxy, OpenClaw pozostawia `service_tier` bez zmian.
    </Warning>

  </Accordion>

  <Accordion title="Compaction po stronie serwera (Responses API)">
    Dla bezpośrednich modeli OpenAI Responses (`openai/*` na `api.openai.com`) OpenClaw automatycznie włącza Compaction po stronie serwera:

    - Wymusza `store: true` (chyba że zgodność modelu ustawia `supportsStore: false`)
    - Wstrzykuje `context_management: [{ type: "compaction", compact_threshold: ... }]`
    - Domyślny `compact_threshold`: 70% `contextWindow` (lub `80000`, gdy nie jest dostępne)

    <Tabs>
      <Tab title="Włącz jawnie">
        Przydatne dla zgodnych endpointów, takich jak Azure OpenAI Responses:

        ```json5
        {
          agents: {
            defaults: {
              models: {
                "azure-openai-responses/gpt-5.4": {
                  params: { responsesServerCompaction: true },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Niestandardowy próg">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: {
                    responsesServerCompaction: true,
                    responsesCompactThreshold: 120000,
                  },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Wyłącz">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: { responsesServerCompaction: false },
                },
              },
            },
          },
        }
        ```
      </Tab>
    </Tabs>

    <Note>
    `responsesServerCompaction` kontroluje tylko wstrzykiwanie `context_management`. Bezpośrednie modele OpenAI Responses nadal wymuszają `store: true`, chyba że zgodność ustawia `supportsStore: false`.
    </Note>

  </Accordion>

  <Accordion title="Rygorystyczny tryb agentowy GPT">
    Dla uruchomień rodziny GPT-5 na `openai/*` i `openai-codex/*` OpenClaw może używać bardziej rygorystycznego osadzonego kontraktu wykonania:

    ```json5
    {
      agents: {
        defaults: {
          embeddedPi: { executionContract: "strict-agentic" },
        },
      },
    }
    ```

    Przy `strict-agentic` OpenClaw:
    - Nie traktuje już tury zawierającej wyłącznie plan jako pomyślnego postępu, gdy dostępna jest akcja narzędzia
    - Ponawia turę ze wskazówką działania natychmiast
    - Automatycznie włącza `update_plan` dla istotnej pracy
    - Pokazuje jawny stan zablokowania, jeśli model nadal planuje bez działania

    <Note>
    Dotyczy wyłącznie uruchomień rodziny GPT-5 dla OpenAI i Codex. Inni dostawcy i starsze rodziny modeli zachowują domyślne zachowanie.
    </Note>

  </Accordion>

  <Accordion title="Ścieżki natywne a zgodne z OpenAI">
    OpenClaw traktuje bezpośrednie endpointy OpenAI, Codex i Azure OpenAI inaczej niż generyczne proxy `/v1` zgodne z OpenAI:

    **Ścieżki natywne** (`openai/*`, `openai-codex/*`, Azure OpenAI):
    - Zachowują `reasoning: { effort: "none" }`, gdy rozumowanie jest jawnie wyłączone
    - Domyślnie ustawiają schematy narzędzi w trybie ścisłym
    - Dołączają ukryte nagłówki atrybucji tylko na zweryfikowanych natywnych hostach
    - Zachowują kształtowanie żądań specyficzne dla OpenAI (`service_tier`, `store`, zgodność reasoning, wskazówki prompt-cache)

    **Ścieżki proxy/zgodne:**
    - Używają luźniejszego zachowania zgodności
    - Nie wymuszają ścisłych schematów narzędzi ani nagłówków wyłącznie natywnych

    Azure OpenAI używa natywnego transportu i zachowania zgodności, ale nie otrzymuje ukrytych nagłówków atrybucji.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Generowanie obrazów" href="/pl/tools/image-generation" icon="image">
    Wspólne parametry narzędzia obrazów i wybór dostawcy.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Wspólne parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="OAuth i uwierzytelnianie" href="/pl/gateway/authentication" icon="key">
    Szczegóły uwierzytelniania i zasady ponownego użycia poświadczeń.
  </Card>
</CardGroup>
