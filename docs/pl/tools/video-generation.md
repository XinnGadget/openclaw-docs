---
read_when:
    - Generowanie wideo przez agenta
    - Konfigurowanie dostawców i modeli generowania wideo
    - Zrozumienie parametrów narzędzia video_generate
summary: Generowanie wideo z tekstu, obrazów lub istniejących filmów przy użyciu 12 backendów dostawców
title: Generowanie wideo
x-i18n:
    generated_at: "2026-04-06T03:14:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4afec87368232221db1aa5a3980254093d6a961b17271b2dcbf724e6bd455b16
    source_path: tools/video-generation.md
    workflow: 15
---

# Generowanie wideo

Agenci OpenClaw mogą generować wideo z promptów tekstowych, obrazów referencyjnych lub istniejących filmów. Obsługiwanych jest dwanaście backendów dostawców, z których każdy ma różne opcje modeli, tryby wejścia i zestawy funkcji. Agent automatycznie wybiera właściwego dostawcę na podstawie twojej konfiguracji i dostępnych kluczy API.

<Note>
Narzędzie `video_generate` pojawia się tylko wtedy, gdy dostępny jest co najmniej jeden dostawca generowania wideo. Jeśli nie widzisz go w narzędziach agenta, ustaw klucz API dostawcy albo skonfiguruj `agents.defaults.videoGenerationModel`.
</Note>

## Szybki start

1. Ustaw klucz API dla dowolnego obsługiwanego dostawcy:

```bash
export GEMINI_API_KEY="your-key"
```

2. Opcjonalnie przypnij model domyślny:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Poproś agenta:

> Wygeneruj 5-sekundowe kinowe wideo przedstawiające przyjaznego homara surfującego o zachodzie słońca.

Agent automatycznie wywoła `video_generate`. Nie jest wymagane dodawanie narzędzia do allowlisty.

## Co dzieje się podczas generowania wideo

Generowanie wideo jest asynchroniczne. Gdy agent wywołuje `video_generate` w sesji:

1. OpenClaw wysyła żądanie do dostawcy i natychmiast zwraca identyfikator zadania.
2. Dostawca przetwarza zadanie w tle (zwykle od 30 sekund do 5 minut w zależności od dostawcy i rozdzielczości).
3. Gdy wideo jest gotowe, OpenClaw wybudza tę samą sesję przez wewnętrzne zdarzenie ukończenia.
4. Agent publikuje gotowe wideo z powrotem w oryginalnej konwersacji.

Gdy zadanie jest w toku, zduplikowane wywołania `video_generate` w tej samej sesji zwracają bieżący stan zadania zamiast rozpoczynać kolejne generowanie. Użyj `openclaw tasks list` albo `openclaw tasks show <taskId>`, aby sprawdzić postęp przez CLI.

Poza uruchomieniami agenta opartymi na sesji (na przykład przy bezpośrednich wywołaniach narzędzia) narzędzie wraca do generowania inline i zwraca końcową ścieżkę multimediów w tej samej turze.

## Obsługiwani dostawcy

| Dostawca | Model domyślny                 | Tekst | Obraz ref.       | Wideo ref.       | Klucz API                                 |
| -------- | ------------------------------ | ----- | ---------------- | ---------------- | ----------------------------------------- |
| Alibaba  | `wan2.6-t2v`                   | Tak   | Tak (zdalny URL) | Tak (zdalny URL) | `MODELSTUDIO_API_KEY`                     |
| BytePlus | `seedance-1-0-lite-t2v-250428` | Tak   | 1 obraz          | Nie              | `BYTEPLUS_API_KEY`                        |
| ComfyUI  | `workflow`                     | Tak   | 1 obraz          | Nie              | `COMFY_API_KEY` lub `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live` | Tak   | 1 obraz          | Nie              | `FAL_KEY`                                 |
| Google   | `veo-3.1-fast-generate-preview` | Tak  | 1 obraz          | 1 wideo          | `GEMINI_API_KEY`                          |
| MiniMax  | `MiniMax-Hailuo-2.3`           | Tak   | 1 obraz          | Nie              | `MINIMAX_API_KEY`                         |
| OpenAI   | `sora-2`                       | Tak   | 1 obraz          | 1 wideo          | `OPENAI_API_KEY`                          |
| Qwen     | `wan2.6-t2v`                   | Tak   | Tak (zdalny URL) | Tak (zdalny URL) | `QWEN_API_KEY`                            |
| Runway   | `gen4.5`                       | Tak   | 1 obraz          | 1 wideo          | `RUNWAYML_API_SECRET`                     |
| Together | `Wan-AI/Wan2.2-T2V-A14B`       | Tak   | 1 obraz          | Nie              | `TOGETHER_API_KEY`                        |
| Vydra    | `veo3`                         | Tak   | 1 obraz (`kling`) | Nie             | `VYDRA_API_KEY`                           |
| xAI      | `grok-imagine-video`           | Tak   | 1 obraz          | 1 wideo          | `XAI_API_KEY`                             |

Niektórzy dostawcy akceptują dodatkowe lub alternatywne zmienne środowiskowe kluczy API. Szczegóły znajdziesz na poszczególnych [stronach dostawców](#related).

Uruchom `video_generate action=list`, aby sprawdzić dostępnych dostawców i modele w czasie działania.

## Parametry narzędzia

### Wymagane

| Parametr | Typ    | Opis                                                                     |
| -------- | ------ | ------------------------------------------------------------------------ |
| `prompt` | string | Tekstowy opis wideo do wygenerowania (wymagany dla `action: "generate"`) |

### Wejścia treści

| Parametr | Typ      | Opis                                 |
| -------- | -------- | ------------------------------------ |
| `image`  | string   | Pojedynczy obraz referencyjny (ścieżka lub URL) |
| `images` | string[] | Wiele obrazów referencyjnych (maks. 5) |
| `video`  | string   | Pojedyncze wideo referencyjne (ścieżka lub URL) |
| `videos` | string[] | Wiele filmów referencyjnych (maks. 4) |

### Sterowanie stylem

| Parametr         | Typ     | Opis                                                                     |
| ---------------- | ------- | ------------------------------------------------------------------------ |
| `aspectRatio`    | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` |
| `resolution`     | string  | `480P`, `720P` lub `1080P`                                               |
| `durationSeconds`| number  | Docelowy czas trwania w sekundach (zaokrąglany do najbliższej wartości obsługiwanej przez dostawcę) |
| `size`           | string  | Wskazówka rozmiaru, gdy dostawca ją obsługuje                            |
| `audio`          | boolean | Włącza generowany dźwięk, gdy jest obsługiwany                           |
| `watermark`      | boolean | Przełącza watermark dostawcy, gdy jest obsługiwany                       |

### Zaawansowane

| Parametr  | Typ    | Opis                                             |
| --------- | ------ | ------------------------------------------------ |
| `action`  | string | `"generate"` (domyślnie), `"status"` albo `"list"` |
| `model`   | string | Nadpisanie dostawcy/modelu (np. `runway/gen4.5`) |
| `filename`| string | Wskazówka nazwy pliku wyjściowego                |

Nie wszyscy dostawcy obsługują wszystkie parametry. Nieobsługiwane nadpisania są ignorowane w trybie best-effort i zgłaszane jako ostrzeżenia w wyniku narzędzia. Twarde ograniczenia capability (na przykład zbyt wiele wejść referencyjnych) powodują błąd przed wysłaniem.

## Działania

- **generate** (domyślnie) -- utwórz wideo z podanego promptu i opcjonalnych wejść referencyjnych.
- **status** -- sprawdź stan zadania generowania wideo będącego w toku dla bieżącej sesji bez uruchamiania kolejnego generowania.
- **list** -- pokaż dostępnych dostawców, modele i ich capabilities.

## Wybór modelu

Podczas generowania wideo OpenClaw rozpoznaje model w tej kolejności:

1. **parametr narzędzia `model`** -- jeśli agent poda go w wywołaniu.
2. **`videoGenerationModel.primary`** -- z konfiguracji.
3. **`videoGenerationModel.fallbacks`** -- próbowane po kolei.
4. **Automatyczne wykrywanie** -- używa dostawców z poprawnym auth, zaczynając od bieżącego domyślnego dostawcy, a następnie pozostałych dostawców w kolejności alfabetycznej.

Jeśli jeden dostawca zawiedzie, automatycznie próbowany jest kolejny kandydat. Jeśli zawiodą wszyscy kandydaci, błąd zawiera szczegóły każdej próby.

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Uwagi o dostawcach

| Dostawca | Uwagi |
| -------- | ----- |
| Alibaba  | Używa asynchronicznego endpointu DashScope/Model Studio. Obrazy i filmy referencyjne muszą być zdalnymi URL-ami `http(s)`. |
| BytePlus | Tylko jeden obraz referencyjny. |
| ComfyUI  | Lokalne lub chmurowe wykonanie sterowane workflow. Obsługuje text-to-video i image-to-video przez skonfigurowany graf. |
| fal      | Używa przepływu opartego na kolejce dla długich zadań. Tylko jeden obraz referencyjny. |
| Google   | Używa Gemini/Veo. Obsługuje jeden obraz albo jedno wideo referencyjne. |
| MiniMax  | Tylko jeden obraz referencyjny. |
| OpenAI   | Przekazywane jest tylko nadpisanie `size`. Inne nadpisania stylu (`aspectRatio`, `resolution`, `audio`, `watermark`) są ignorowane z ostrzeżeniem. |
| Qwen     | Ten sam backend DashScope co Alibaba. Wejścia referencyjne muszą być zdalnymi URL-ami `http(s)`; pliki lokalne są odrzucane z góry. |
| Runway   | Obsługuje pliki lokalne przez data URI. Video-to-video wymaga `runway/gen4_aleph`. Uruchomienia tylko tekstowe udostępniają proporcje `16:9` i `9:16`. |
| Together | Tylko jeden obraz referencyjny. |
| Vydra    | Używa bezpośrednio `https://www.vydra.ai/api/v1`, aby uniknąć przekierowań gubiących auth. `veo3` jest dołączony tylko jako text-to-video; `kling` wymaga zdalnego URL obrazu. |
| xAI      | Obsługuje text-to-video, image-to-video oraz zdalne przepływy edycji/rozszerzania wideo. |

## Konfiguracja

Ustaw domyślny model generowania wideo w konfiguracji OpenClaw:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

Lub przez CLI:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## Powiązane

- [Przegląd narzędzi](/pl/tools)
- [Zadania w tle](/pl/automation/tasks) -- śledzenie zadań dla asynchronicznego generowania wideo
- [Alibaba Model Studio](/providers/alibaba)
- [BytePlus](/providers/byteplus)
- [ComfyUI](/providers/comfy)
- [fal](/providers/fal)
- [Google (Gemini)](/pl/providers/google)
- [MiniMax](/pl/providers/minimax)
- [OpenAI](/pl/providers/openai)
- [Qwen](/pl/providers/qwen)
- [Runway](/providers/runway)
- [Together AI](/pl/providers/together)
- [Vydra](/providers/vydra)
- [xAI](/pl/providers/xai)
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
- [Modele](/pl/concepts/models)
