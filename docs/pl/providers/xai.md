---
read_when:
    - Chcesz używać modeli Grok w OpenClaw
    - Konfigurujesz uwierzytelnianie xAI lub identyfikatory modeli
summary: Używanie modeli Grok od xAI w OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-06T03:12:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64bc899655427cc10bdc759171c7d1ec25ad9f1e4f9d803f1553d3d586c6d71d
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw dostarcza wbudowany plugin dostawcy `xai` dla modeli Grok.

## Konfiguracja

1. Utwórz klucz API w konsoli xAI.
2. Ustaw `XAI_API_KEY` albo uruchom:

```bash
openclaw onboard --auth-choice xai-api-key
```

3. Wybierz model, na przykład:

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

OpenClaw używa teraz API Responses xAI jako wbudowanego transportu xAI. Ten sam
`XAI_API_KEY` może również obsługiwać `web_search` oparte na Grok, natywne `x_search`
oraz zdalne `code_execution`.
Jeśli zapiszesz klucz xAI pod `plugins.entries.xai.config.webSearch.apiKey`,
wbudowany dostawca modeli xAI również użyje tego klucza jako rozwiązania awaryjnego.
Dostrajanie `code_execution` znajduje się pod `plugins.entries.xai.config.codeExecution`.

## Aktualny wbudowany katalog modeli

OpenClaw zawiera teraz domyślnie następujące rodziny modeli xAI:

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

Plugin przekazuje też dalej rozwiązywanie nowszych identyfikatorów `grok-4*` i `grok-code-fast*`, gdy
stosują ten sam kształt API.

Uwagi dotyczące modeli fast:

- `grok-4-fast`, `grok-4-1-fast` oraz warianty `grok-4.20-beta-*` to
  aktualne referencje Grok z obsługą obrazów we wbudowanym katalogu.
- `/fast on` lub `agents.defaults.models["xai/<model>"].params.fastMode: true`
  przepisuje natywne żądania xAI w następujący sposób:
  - `grok-3` -> `grok-3-fast`
  - `grok-3-mini` -> `grok-3-mini-fast`
  - `grok-4` -> `grok-4-fast`
  - `grok-4-0709` -> `grok-4-fast`

Starsze aliasy zgodności są nadal normalizowane do kanonicznych wbudowanych identyfikatorów. Na
przykład:

- `grok-4-fast-reasoning` -> `grok-4-fast`
- `grok-4-1-fast-reasoning` -> `grok-4-1-fast`
- `grok-4.20-reasoning` -> `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` -> `grok-4.20-beta-latest-non-reasoning`

## Wyszukiwanie w sieci

Wbudowany dostawca wyszukiwania w sieci `grok` także używa `XAI_API_KEY`:

```bash
openclaw config set tools.web.search.provider grok
```

## Generowanie wideo

Wbudowany plugin `xai` rejestruje także generowanie wideo przez współdzielone
narzędzie `video_generate`.

- Domyślny model wideo: `xai/grok-imagine-video`
- Tryby: text-to-video, image-to-video oraz zdalne przepływy edycji/rozszerzania wideo
- Obsługuje `aspectRatio` i `resolution`
- Aktualne ograniczenie: lokalne bufory wideo nie są akceptowane; używaj zdalnych adresów URL `http(s)`
  dla wejść referencyjnych/edycji wideo

Aby używać xAI jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "xai/grok-imagine-video",
      },
    },
  },
}
```

Zobacz [Generowanie wideo](/tools/video-generation), aby poznać współdzielone
parametry narzędzia, wybór dostawcy i zachowanie failover.

## Znane ograniczenia

- Uwierzytelnianie obecnie obsługuje tylko klucz API. W OpenClaw nie ma jeszcze przepływu OAuth/device-code dla xAI.
- `grok-4.20-multi-agent-experimental-beta-0304` nie jest obsługiwany na zwykłej ścieżce dostawcy xAI, ponieważ wymaga innej powierzchni upstream API niż standardowy transport xAI w OpenClaw.

## Uwagi

- OpenClaw automatycznie stosuje poprawki zgodności specyficzne dla xAI dotyczące schematu narzędzi i wywołań narzędzi na współdzielonej ścieżce runnera.
- Natywne żądania xAI domyślnie ustawiają `tool_stream: true`. Ustaw
  `agents.defaults.models["xai/<model>"].params.tool_stream` na `false`, aby
  to wyłączyć.
- Wbudowany wrapper xAI usuwa nieobsługiwane flagi ścisłego schematu narzędzi i
  klucze payloadu reasoning przed wysłaniem natywnych żądań xAI.
- `web_search`, `x_search` i `code_execution` są udostępniane jako narzędzia OpenClaw. OpenClaw włącza konkretne wbudowane mechanizmy xAI, których potrzebuje w każdym żądaniu narzędzia, zamiast dołączać wszystkie natywne narzędzia do każdej tury czatu.
- `x_search` i `code_execution` należą do wbudowanego pluginu xAI, a nie są zakodowane na sztywno w podstawowym runtime modeli.
- `code_execution` oznacza zdalne wykonywanie w sandboxie xAI, a nie lokalne [`exec`](/pl/tools/exec).
- Szerszy przegląd dostawców znajdziesz w [Dostawcy modeli](/pl/providers/index).
