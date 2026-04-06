---
read_when:
    - Chcesz używać modeli OpenAI w OpenClaw
    - Chcesz używać uwierzytelniania subskrypcją Codex zamiast kluczy API
summary: Używanie OpenAI przez klucze API lub subskrypcję Codex w OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-06T03:12:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e04db5787f6ed7b1eda04d965c10febae10809fc82ae4d9769e7163234471f5
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI udostępnia API dla deweloperów do modeli GPT. Codex obsługuje **logowanie ChatGPT** w celu uzyskania dostępu
w ramach subskrypcji albo **logowanie kluczem API** w celu dostępu rozliczanego za użycie. Codex cloud wymaga logowania do ChatGPT.
OpenAI jawnie wspiera użycie subskrypcyjnego OAuth w zewnętrznych narzędziach/workflow, takich jak OpenClaw.

## Domyślny styl interakcji

OpenClaw może dodać małą nakładkę promptu specyficzną dla OpenAI zarówno dla uruchomień `openai/*`, jak i
`openai-codex/*`. Domyślnie nakładka utrzymuje asystenta jako ciepłego,
współpracującego, zwięzłego, bezpośredniego i nieco bardziej ekspresyjnego emocjonalnie,
bez zastępowania bazowego system promptu OpenClaw. Przyjazna nakładka także
dopuszcza okazjonalne emoji, gdy pasuje to naturalnie, przy jednoczesnym zachowaniu ogólnej zwięzłości
wypowiedzi.

Klucz konfiguracji:

`plugins.entries.openai.config.personality`

Dozwolone wartości:

- `"friendly"`: domyślnie; włącza nakładkę specyficzną dla OpenAI.
- `"off"`: wyłącza nakładkę i używa tylko bazowego promptu OpenClaw.

Zakres:

- Dotyczy modeli `openai/*`.
- Dotyczy modeli `openai-codex/*`.
- Nie wpływa na innych providerów.

To zachowanie jest domyślnie włączone. Zachowaj jawnie `"friendly"`, jeśli chcesz,
aby przetrwało to przyszłe lokalne zmiany konfiguracji:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "friendly",
        },
      },
    },
  },
}
```

### Wyłączanie nakładki promptu OpenAI

Jeśli chcesz używać niezmodyfikowanego bazowego promptu OpenClaw, ustaw nakładkę na `"off"`:

```json5
{
  plugins: {
    entries: {
      openai: {
        config: {
          personality: "off",
        },
      },
    },
  },
}
```

Możesz też ustawić to bezpośrednio przez CLI konfiguracji:

```bash
openclaw config set plugins.entries.openai.config.personality off
```

## Opcja A: klucz API OpenAI (OpenAI Platform)

**Najlepsze dla:** bezpośredniego dostępu do API i rozliczania za użycie.
Pobierz klucz API z panelu OpenAI.

### Konfiguracja CLI

```bash
openclaw onboard --auth-choice openai-api-key
# albo bez interakcji
openclaw onboard --openai-api-key "$OPENAI_API_KEY"
```

### Fragment konfiguracji

```json5
{
  env: { OPENAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

Aktualna dokumentacja modeli API OpenAI wymienia `gpt-5.4` i `gpt-5.4-pro` dla bezpośredniego
użycia API OpenAI. OpenClaw przekazuje oba przez ścieżkę `openai/*` Responses.
OpenClaw celowo ukrywa przestarzały wiersz `openai/gpt-5.3-codex-spark`,
ponieważ bezpośrednie wywołania API OpenAI odrzucają go w ruchu produkcyjnym.

OpenClaw **nie** udostępnia `openai/gpt-5.3-codex-spark` w bezpośredniej ścieżce
API OpenAI. `pi-ai` nadal dostarcza wbudowany wiersz dla tego modelu, ale aktywne żądania do API OpenAI
są obecnie odrzucane. W OpenClaw Spark jest traktowany wyłącznie jako model Codex.

## Generowanie obrazów

Bundled plugin `openai` rejestruje również generowanie obrazów przez współdzielone
narzędzie `image_generate`.

- Domyślny model obrazów: `openai/gpt-image-1`
- Generowanie: do 4 obrazów na żądanie
- Tryb edycji: włączony, do 5 obrazów referencyjnych
- Obsługuje `size`
- Obecne zastrzeżenie specyficzne dla OpenAI: OpenClaw nie przekazuje dziś nadpisań `aspectRatio` ani
  `resolution` do OpenAI Images API

Aby używać OpenAI jako domyślnego providera obrazów:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "openai/gpt-image-1",
      },
    },
  },
}
```

Zobacz [Image Generation](/pl/tools/image-generation), aby poznać współdzielone
parametry narzędzia, wybór providera i zachowanie failover.

## Generowanie wideo

Bundled plugin `openai` rejestruje również generowanie wideo przez współdzielone
narzędzie `video_generate`.

- Domyślny model wideo: `openai/sora-2`
- Tryby: text-to-video, image-to-video oraz przepływy z pojedynczym wideo referencyjnym/edycją
- Obecne limity: 1 obraz lub 1 wejście referencyjne wideo
- Obecne zastrzeżenie specyficzne dla OpenAI: OpenClaw obecnie przekazuje tylko nadpisania `size`
  dla natywnego generowania wideo OpenAI. Nieobsługiwane opcjonalne nadpisania,
  takie jak `aspectRatio`, `resolution`, `audio` i `watermark`, są ignorowane
  i zgłaszane z powrotem jako ostrzeżenie narzędzia.

Aby używać OpenAI jako domyślnego providera wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "openai/sora-2",
      },
    },
  },
}
```

Zobacz [Video Generation](/tools/video-generation), aby poznać współdzielone
parametry narzędzia, wybór providera i zachowanie failover.

## Opcja B: subskrypcja OpenAI Code (Codex)

**Najlepsze dla:** używania dostępu subskrypcyjnego ChatGPT/Codex zamiast klucza API.
Codex cloud wymaga logowania ChatGPT, podczas gdy Codex CLI obsługuje logowanie ChatGPT albo kluczem API.

### Konfiguracja CLI (OAuth Codex)

```bash
# Uruchom OAuth Codex w kreatorze
openclaw onboard --auth-choice openai-codex

# Albo uruchom OAuth bezpośrednio
openclaw models auth login --provider openai-codex
```

### Fragment konfiguracji (subskrypcja Codex)

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

Aktualna dokumentacja Codex OpenAI wymienia `gpt-5.4` jako bieżący model Codex. OpenClaw
mapuje go na `openai-codex/gpt-5.4` dla użycia z OAuth ChatGPT/Codex.

Jeśli onboarding użyje istniejącego logowania Codex CLI, te poświadczenia pozostaną
zarządzane przez Codex CLI. Po wygaśnięciu OpenClaw najpierw ponownie odczytuje zewnętrzne źródło Codex
i, gdy provider może je odświeżyć, zapisuje odświeżone poświadczenie z powrotem do pamięci Codex zamiast przejmować je do osobnej
kopii tylko dla OpenClaw.

Jeśli Twoje konto Codex ma uprawnienia do Codex Spark, OpenClaw obsługuje również:

- `openai-codex/gpt-5.3-codex-spark`

OpenClaw traktuje Codex Spark jako model tylko dla Codex. Nie udostępnia bezpośredniej
ścieżki klucza API `openai/gpt-5.3-codex-spark`.

OpenClaw zachowuje również `openai-codex/gpt-5.3-codex-spark`, gdy `pi-ai`
go wykryje. Traktuj go jako zależny od uprawnień i eksperymentalny: Codex Spark jest
oddzielny od GPT-5.4 `/fast`, a dostępność zależy od zalogowanego konta Codex /
ChatGPT.

### Limit okna kontekstu Codex

OpenClaw traktuje metadane modelu Codex i limit kontekstu w runtime jako osobne
wartości.

Dla `openai-codex/gpt-5.4`:

- natywne `contextWindow`: `1050000`
- domyślny limit `contextTokens` w runtime: `272000`

Pozwala to zachować zgodność metadanych modelu z prawdą, przy jednoczesnym utrzymaniu mniejszego domyślnego okna runtime,
które w praktyce ma lepsze właściwości opóźnienia i jakości.

Jeśli chcesz użyć innego efektywnego limitu, ustaw `models.providers.<provider>.models[].contextTokens`:

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [
          {
            id: "gpt-5.4",
            contextTokens: 160000,
          },
        ],
      },
    },
  },
}
```

Używaj `contextWindow` tylko wtedy, gdy deklarujesz lub nadpisujesz natywne metadane
modelu. Używaj `contextTokens`, gdy chcesz ograniczyć budżet kontekstu w runtime.

### Domyślny transport

OpenClaw używa `pi-ai` do strumieniowania modeli. Dla `openai/*` i
`openai-codex/*` domyślnym transportem jest `"auto"` (najpierw WebSocket, potem fallback do SSE).

W trybie `"auto"` OpenClaw ponawia też jedno wczesne, możliwe do ponowienia niepowodzenie WebSocket,
zanim przełączy się na SSE. Wymuszony tryb `"websocket"` nadal bezpośrednio pokazuje błędy transportu
zamiast ukrywać je za fallbackiem.

Po błędzie WebSocket podczas połączenia lub wczesnej tury w trybie `"auto"` OpenClaw oznacza
ścieżkę WebSocket tej sesji jako zdegradowaną na około 60 sekund i wysyła
kolejne tury przez SSE podczas czasu odnowienia zamiast bez końca przełączać się między
transportami.

Dla natywnych endpointów rodziny OpenAI (`openai/*`, `openai-codex/*` i Azure
OpenAI Responses) OpenClaw dołącza też do żądań stabilny stan tożsamości sesji i tury,
aby ponowienia, ponowne połączenia i fallback do SSE były zgodne z tą samą
tożsamością rozmowy. W natywnych trasach rodziny OpenAI obejmuje to stabilne nagłówki tożsamości żądania sesji/tury oraz pasujące metadane transportu.

OpenClaw normalizuje też liczniki użycia OpenAI między wariantami transportu, zanim
trafią one do powierzchni sesji/statusu. Natywny ruch OpenAI/Codex Responses może
raportować użycie jako `input_tokens` / `output_tokens` albo
`prompt_tokens` / `completion_tokens`; OpenClaw traktuje je jako te same liczniki wejścia
i wyjścia dla `/status`, `/usage` i logów sesji. Gdy natywny ruch WebSocket pomija `total_tokens`
(lub raportuje `0`), OpenClaw używa znormalizowanej sumy wejścia + wyjścia, aby wyświetlenia sesji/statusu nadal były wypełnione.

Możesz ustawić `agents.defaults.models.<provider/model>.params.transport`:

- `"sse"`: wymuś SSE
- `"websocket"`: wymuś WebSocket
- `"auto"`: spróbuj WebSocket, potem fallback do SSE

Dla `openai/*` (Responses API) OpenClaw domyślnie włącza także rozgrzewanie WebSocket
(`openaiWsWarmup: true`) przy użyciu transportu WebSocket.

Powiązana dokumentacja OpenAI:

- [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
- [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

```json5
{
  agents: {
    defaults: {
      model: { primary: "openai-codex/gpt-5.4" },
      models: {
        "openai-codex/gpt-5.4": {
          params: {
            transport: "auto",
          },
        },
      },
    },
  },
}
```

### Rozgrzewanie WebSocket OpenAI

Dokumentacja OpenAI opisuje rozgrzewanie jako opcjonalne. OpenClaw włącza je domyślnie dla
`openai/*`, aby zmniejszyć opóźnienie pierwszej tury przy użyciu transportu WebSocket.

### Wyłączanie rozgrzewania

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: false,
          },
        },
      },
    },
  },
}
```

### Jawne włączanie rozgrzewania

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            openaiWsWarmup: true,
          },
        },
      },
    },
  },
}
```

### Priorytetowe przetwarzanie OpenAI i Codex

API OpenAI udostępnia priorytetowe przetwarzanie przez `service_tier=priority`. W
OpenClaw ustaw `agents.defaults.models["<provider>/<model>"].params.serviceTier`,
aby przekazać to pole do natywnych endpointów OpenAI/Codex Responses.

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Obsługiwane wartości to `auto`, `default`, `flex` i `priority`.

OpenClaw przekazuje `params.serviceTier` zarówno do bezpośrednich żądań `openai/*` Responses,
jak i do żądań `openai-codex/*` Codex Responses, gdy te modele wskazują
na natywne endpointy OpenAI/Codex.

Ważne zachowanie:

- bezpośrednie `openai/*` musi wskazywać `api.openai.com`
- `openai-codex/*` musi wskazywać `chatgpt.com/backend-api`
- jeśli kierujesz którykolwiek provider przez inny base URL lub proxy, OpenClaw pozostawia `service_tier` bez zmian

### Tryb szybki OpenAI

OpenClaw udostępnia współdzielony przełącznik trybu szybkiego dla sesji `openai/*` i
`openai-codex/*`:

- Czat/UI: `/fast status|on|off`
- Konfiguracja: `agents.defaults.models["<provider>/<model>"].params.fastMode`

Gdy tryb szybki jest włączony, OpenClaw mapuje go na priorytetowe przetwarzanie OpenAI:

- bezpośrednie wywołania `openai/*` Responses do `api.openai.com` wysyłają `service_tier = "priority"`
- wywołania `openai-codex/*` Responses do `chatgpt.com/backend-api` również wysyłają `service_tier = "priority"`
- istniejące wartości payloadu `service_tier` są zachowywane
- tryb szybki nie nadpisuje `reasoning` ani `text.verbosity`

Dla GPT 5.4 najczęstsza konfiguracja wygląda tak:

- wyślij `/fast on` w sesji używającej `openai/gpt-5.4` lub `openai-codex/gpt-5.4`
- albo ustaw `agents.defaults.models["openai/gpt-5.4"].params.fastMode = true`
- jeśli używasz też OAuth Codex, ustaw również `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = true`

Przykład:

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
        "openai-codex/gpt-5.4": {
          params: {
            fastMode: true,
          },
        },
      },
    },
  },
}
```

Nadpisania sesji mają pierwszeństwo przed konfiguracją. Wyczyszczenie nadpisania sesji w interfejsie Sessions UI
przywraca sesji skonfigurowaną wartość domyślną.

### Natywne trasy OpenAI a trasy zgodne z OpenAI

OpenClaw traktuje bezpośrednie endpointy OpenAI, Codex i Azure OpenAI inaczej
niż generyczne proxy `/v1` zgodne z OpenAI:

- natywne trasy `openai/*`, `openai-codex/*` i Azure OpenAI zachowują
  `reasoning: { effort: "none" }`, gdy jawnie wyłączysz reasoning
- natywne trasy rodziny OpenAI domyślnie ustawiają ścisły tryb schematów narzędzi
- ukryte nagłówki atrybucji OpenClaw (`originator`, `version` i
  `User-Agent`) są dołączane tylko do zweryfikowanych natywnych hostów OpenAI
  (`api.openai.com`) i natywnych hostów Codex (`chatgpt.com/backend-api`)
- natywne trasy OpenAI/Codex zachowują kształtowanie żądań specyficzne dla OpenAI, takie jak
  `service_tier`, Responses `store`, payloady zgodności z reasoning OpenAI oraz
  wskazówki prompt-cache
- trasy proxy zgodne z OpenAI zachowują luźniejsze zachowanie zgodności i nie
  wymuszają ścisłych schematów narzędzi, natywnego kształtowania żądań ani ukrytych
  nagłówków atrybucji OpenAI/Codex

Azure OpenAI pozostaje w grupie natywnego routingu dla zachowania transportu i zgodności,
ale nie otrzymuje ukrytych nagłówków atrybucji OpenAI/Codex.

Pozwala to zachować obecne natywne zachowanie OpenAI Responses bez wymuszania starszych
nakładek zgodnych z OpenAI na backendach `/v1` firm trzecich.

### Kompaktowanie po stronie serwera OpenAI Responses

Dla bezpośrednich modeli OpenAI Responses (`openai/*` używających `api: "openai-responses"` z
`baseUrl` ustawionym na `api.openai.com`) OpenClaw teraz automatycznie włącza
wskazówki payloadu do kompaktowania po stronie serwera OpenAI:

- Wymusza `store: true` (chyba że zgodność modelu ustawia `supportsStore: false`)
- Wstrzykuje `context_management: [{ type: "compaction", compact_threshold: ... }]`

Domyślnie `compact_threshold` wynosi `70%` modelowego `contextWindow` (lub `80000`,
gdy wartość jest niedostępna).

### Jawne włączanie kompaktowania po stronie serwera

Użyj tego, jeśli chcesz wymusić wstrzykiwanie `context_management` w zgodnych
modelach Responses (na przykład Azure OpenAI Responses):

```json5
{
  agents: {
    defaults: {
      models: {
        "azure-openai-responses/gpt-5.4": {
          params: {
            responsesServerCompaction: true,
          },
        },
      },
    },
  },
}
```

### Włączanie z niestandardowym progiem

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

### Wyłączanie kompaktowania po stronie serwera

```json5
{
  agents: {
    defaults: {
      models: {
        "openai/gpt-5.4": {
          params: {
            responsesServerCompaction: false,
          },
        },
      },
    },
  },
}
```

`responsesServerCompaction` kontroluje tylko wstrzykiwanie `context_management`.
Bezpośrednie modele OpenAI Responses nadal wymuszają `store: true`, chyba że zgodność ustawi
`supportsStore: false`.

## Uwagi

- Referencje modeli zawsze używają formatu `provider/model` (zobacz [/concepts/models](/pl/concepts/models)).
- Szczegóły auth + reguły ponownego użycia znajdują się w [/concepts/oauth](/pl/concepts/oauth).
