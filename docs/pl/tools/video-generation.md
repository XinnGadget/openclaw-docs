---
read_when:
    - Generowanie filmów za pomocą agenta
    - Konfigurowanie dostawców i modeli do generowania filmów
    - Omówienie parametrów narzędzia `video_generate`
summary: Generuj filmy z tekstu, obrazów lub istniejących filmów za pomocą 14 backendów dostawców
title: Generowanie filmów
x-i18n:
    generated_at: "2026-04-11T09:30:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0ec159a0bbb6b8a030e68828c0a8bcaf40c8538ecf98bc8ff609dab9d0068263
    source_path: tools/video-generation.md
    workflow: 15
---

# Generowanie filmów

Agenci OpenClaw mogą generować filmy na podstawie promptów tekstowych, obrazów referencyjnych lub istniejących filmów. Obsługiwanych jest czternaście backendów dostawców, z których każdy oferuje różne opcje modeli, tryby wejściowe i zestawy funkcji. Agent automatycznie wybiera właściwego dostawcę na podstawie Twojej konfiguracji i dostępnych kluczy API.

<Note>
Narzędzie `video_generate` pojawia się tylko wtedy, gdy dostępny jest co najmniej jeden dostawca generowania filmów. Jeśli go nie widzisz w narzędziach agenta, ustaw klucz API dostawcy lub skonfiguruj `agents.defaults.videoGenerationModel`.
</Note>

OpenClaw traktuje generowanie filmów jako trzy tryby działania w czasie wykonywania:

- `generate` dla żądań tekst-na-film bez mediów referencyjnych
- `imageToVideo` gdy żądanie zawiera jeden lub więcej obrazów referencyjnych
- `videoToVideo` gdy żądanie zawiera jeden lub więcej filmów referencyjnych

Dostawcy mogą obsługiwać dowolny podzbiór tych trybów. Narzędzie sprawdza aktywny
tryb przed wysłaniem i raportuje obsługiwane tryby w `action=list`.

## Szybki start

1. Ustaw klucz API dla dowolnego obsługiwanego dostawcy:

```bash
export GEMINI_API_KEY="your-key"
```

2. Opcjonalnie przypnij domyślny model:

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. Poproś agenta:

> Wygeneruj 5-sekundowy kinowy film przedstawiający przyjaznego homara surfującego o zachodzie słońca.

Agent automatycznie wywoła `video_generate`. Lista dozwolonych narzędzi nie jest wymagana.

## Co dzieje się podczas generowania filmu

Generowanie filmów jest asynchroniczne. Gdy agent wywoła `video_generate` w sesji:

1. OpenClaw wysyła żądanie do dostawcy i natychmiast zwraca identyfikator zadania.
2. Dostawca przetwarza zadanie w tle (zwykle od 30 sekund do 5 minut, w zależności od dostawcy i rozdzielczości).
3. Gdy film jest gotowy, OpenClaw wybudza tę samą sesję wewnętrznym zdarzeniem ukończenia.
4. Agent publikuje gotowy film z powrotem w oryginalnej rozmowie.

Gdy zadanie jest w toku, zduplikowane wywołania `video_generate` w tej samej sesji zwracają bieżący stan zadania zamiast rozpoczynać kolejne generowanie. Użyj `openclaw tasks list` lub `openclaw tasks show <taskId>`, aby sprawdzić postęp z poziomu CLI.

Poza uruchomieniami agenta opartymi na sesji (na przykład przy bezpośrednich wywołaniach narzędzia), narzędzie przechodzi do generowania inline i zwraca końcową ścieżkę do multimediów w tej samej turze.

### Cykl życia zadania

Każde żądanie `video_generate` przechodzi przez cztery stany:

1. **queued** -- zadanie utworzone, oczekuje na zaakceptowanie przez dostawcę.
2. **running** -- dostawca przetwarza zadanie (zwykle od 30 sekund do 5 minut, w zależności od dostawcy i rozdzielczości).
3. **succeeded** -- film gotowy; agent wybudza się i publikuje go w rozmowie.
4. **failed** -- błąd dostawcy lub przekroczenie limitu czasu; agent wybudza się ze szczegółami błędu.

Sprawdź stan z poziomu CLI:

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

Zapobieganie duplikatom: jeśli zadanie wideo ma już stan `queued` lub `running` dla bieżącej sesji, `video_generate` zwraca stan istniejącego zadania zamiast uruchamiać nowe. Użyj `action: "status"`, aby sprawdzić to jawnie bez uruchamiania nowego generowania.

## Obsługiwani dostawcy

| Dostawca             | Model domyślny                 | Tekst | Obraz ref.                                          | Film ref.       | Klucz API                                 |
| -------------------- | ------------------------------ | ----- | --------------------------------------------------- | --------------- | ----------------------------------------- |
| Alibaba              | `wan2.6-t2v`                   | Tak   | Tak (zdalny URL)                                    | Tak (zdalny URL) | `MODELSTUDIO_API_KEY`                    |
| BytePlus (1.0)       | `seedance-1-0-pro-250528`      | Tak   | Do 2 obrazów (tylko modele I2V; pierwsza + ostatnia klatka) | Nie       | `BYTEPLUS_API_KEY`                        |
| BytePlus Seedance 1.5 | `seedance-1-5-pro-251215`     | Tak   | Do 2 obrazów (pierwsza + ostatnia klatka przez rolę) | Nie             | `BYTEPLUS_API_KEY`                        |
| BytePlus Seedance 2.0 | `dreamina-seedance-2-0-260128` | Tak  | Do 9 obrazów referencyjnych                         | Do 3 filmów     | `BYTEPLUS_API_KEY`                        |
| ComfyUI              | `workflow`                     | Tak   | 1 obraz                                             | Nie             | `COMFY_API_KEY` lub `COMFY_CLOUD_API_KEY` |
| fal                  | `fal-ai/minimax/video-01-live` | Tak   | 1 obraz                                             | Nie             | `FAL_KEY`                                 |
| Google               | `veo-3.1-fast-generate-preview` | Tak  | 1 obraz                                             | 1 film          | `GEMINI_API_KEY`                          |
| MiniMax              | `MiniMax-Hailuo-2.3`           | Tak   | 1 obraz                                             | Nie             | `MINIMAX_API_KEY`                         |
| OpenAI               | `sora-2`                       | Tak   | 1 obraz                                             | 1 film          | `OPENAI_API_KEY`                          |
| Qwen                 | `wan2.6-t2v`                   | Tak   | Tak (zdalny URL)                                    | Tak (zdalny URL) | `QWEN_API_KEY`                           |
| Runway               | `gen4.5`                       | Tak   | 1 obraz                                             | 1 film          | `RUNWAYML_API_SECRET`                     |
| Together             | `Wan-AI/Wan2.2-T2V-A14B`       | Tak   | 1 obraz                                             | Nie             | `TOGETHER_API_KEY`                        |
| Vydra                | `veo3`                         | Tak   | 1 obraz (`kling`)                                   | Nie             | `VYDRA_API_KEY`                           |
| xAI                  | `grok-imagine-video`           | Tak   | 1 obraz                                             | 1 film          | `XAI_API_KEY`                             |

Niektórzy dostawcy akceptują dodatkowe lub alternatywne zmienne środowiskowe kluczy API. Szczegóły znajdziesz na poszczególnych [stronach dostawców](#related).

Uruchom `video_generate action=list`, aby sprawdzić dostępnych dostawców, modele i
tryby działania w czasie wykonywania.

### Zadeklarowana macierz możliwości

Jest to jawny kontrakt trybów używany przez `video_generate`, testy kontraktowe
oraz wspólny zestaw testów live.

| Dostawca | `generate` | `imageToVideo` | `videoToVideo` | Wspólne ścieżki live obecnie                                                                                                             |
| -------- | ---------- | -------------- | -------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; `videoToVideo` pomijane, ponieważ ten dostawca wymaga zdalnych adresów URL filmów `http(s)`                |
| BytePlus | Tak        | Tak            | Nie            | `generate`, `imageToVideo`                                                                                                               |
| ComfyUI  | Tak        | Tak            | Nie            | Nie wchodzi w skład wspólnego zestawu; pokrycie specyficzne dla workflow znajduje się w testach Comfy                                  |
| fal      | Tak        | Tak            | Nie            | `generate`, `imageToVideo`                                                                                                               |
| Google   | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; wspólne `videoToVideo` pomijane, ponieważ obecny zestaw Gemini/Veo oparty na buforach nie akceptuje tego wejścia |
| MiniMax  | Tak        | Tak            | Nie            | `generate`, `imageToVideo`                                                                                                               |
| OpenAI   | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; wspólne `videoToVideo` pomijane, ponieważ ta ścieżka organizacji/wejścia obecnie wymaga dostępu do inpaint/remix po stronie dostawcy |
| Qwen     | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; `videoToVideo` pomijane, ponieważ ten dostawca wymaga zdalnych adresów URL filmów `http(s)`               |
| Runway   | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; `videoToVideo` działa tylko wtedy, gdy wybrany model to `runway/gen4_aleph`                                |
| Together | Tak        | Tak            | Nie            | `generate`, `imageToVideo`                                                                                                               |
| Vydra    | Tak        | Tak            | Nie            | `generate`; wspólne `imageToVideo` pomijane, ponieważ dołączony `veo3` obsługuje tylko tekst, a dołączony `kling` wymaga zdalnego URL obrazu |
| xAI      | Tak        | Tak            | Tak            | `generate`, `imageToVideo`; `videoToVideo` pomijane, ponieważ ten dostawca obecnie wymaga zdalnego URL MP4                             |

## Parametry narzędzia

### Wymagane

| Parametr | Typ    | Opis                                                                                  |
| -------- | ------ | ------------------------------------------------------------------------------------- |
| `prompt` | string | Tekstowy opis filmu do wygenerowania (wymagany dla `action: "generate"`)             |

### Wejścia treści

| Parametr    | Typ      | Opis                                                                                                                                   |
| ----------- | -------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `image`     | string   | Pojedynczy obraz referencyjny (ścieżka lub URL)                                                                                        |
| `images`    | string[] | Wiele obrazów referencyjnych (do 9)                                                                                                    |
| `imageRoles` | string[] | Opcjonalne wskazówki ról dla każdej pozycji, równoległe do połączonej listy obrazów. Kanoniczne wartości: `first_frame`, `last_frame`, `reference_image` |
| `video`     | string   | Pojedynczy film referencyjny (ścieżka lub URL)                                                                                         |
| `videos`    | string[] | Wiele filmów referencyjnych (do 4)                                                                                                     |
| `videoRoles` | string[] | Opcjonalne wskazówki ról dla każdej pozycji, równoległe do połączonej listy filmów. Kanoniczna wartość: `reference_video`           |
| `audioRef`  | string   | Pojedyncze audio referencyjne (ścieżka lub URL). Używane np. jako muzyka w tle lub referencja głosu, gdy dostawca obsługuje wejścia audio |
| `audioRefs` | string[] | Wiele plików audio referencyjnych (do 3)                                                                                               |
| `audioRoles` | string[] | Opcjonalne wskazówki ról dla każdej pozycji, równoległe do połączonej listy audio. Kanoniczna wartość: `reference_audio`            |

Wskazówki ról są przekazywane do dostawcy w niezmienionej postaci. Kanoniczne wartości pochodzą z
unii `VideoGenerationAssetRole`, ale dostawcy mogą akceptować dodatkowe
ciągi ról. Tablice `*Roles` nie mogą mieć więcej wpisów niż
odpowiadająca im lista referencji; błędy typu off-by-one kończą się czytelnym komunikatem.
Użyj pustego ciągu, aby pozostawić pozycję nieustawioną.

### Kontrolki stylu

| Parametr          | Typ     | Opis                                                                                   |
| ----------------- | ------- | -------------------------------------------------------------------------------------- |
| `aspectRatio`     | string  | `1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9` lub `adaptive` |
| `resolution`      | string  | `480P`, `720P`, `768P` lub `1080P`                                                     |
| `durationSeconds` | number  | Docelowy czas trwania w sekundach (zaokrąglany do najbliższej wartości obsługiwanej przez dostawcę) |
| `size`            | string  | Wskazówka rozmiaru, gdy dostawca ją obsługuje                                          |
| `audio`           | boolean | Włącza wygenerowane audio w wyjściu, gdy jest obsługiwane. Odrębne od `audioRef*` (wejść) |
| `watermark`       | boolean | Przełącza znak wodny dostawcy, gdy jest obsługiwany                                    |

`adaptive` to specyficzna dla dostawcy wartość specjalna: jest przekazywana bez zmian do
dostawców, którzy deklarują `adaptive` w swoich możliwościach (np. BytePlus
Seedance używa jej do automatycznego wykrywania proporcji na podstawie
wymiarów obrazu wejściowego). Dostawcy, którzy jej nie deklarują, pokazują tę wartość w
`details.ignoredOverrides` w wyniku narzędzia, dzięki czemu pominięcie jest widoczne.

### Zaawansowane

| Parametr          | Typ    | Opis                                                                                                                                                                                                                                                                                                                                            |
| ----------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `action`          | string | `"generate"` (domyślnie), `"status"` lub `"list"`                                                                                                                                                                                                                                                                                               |
| `model`           | string | Zastąpienie dostawcy/modelu (np. `runway/gen4.5`)                                                                                                                                                                                                                                                                                               |
| `filename`        | string | Wskazówka nazwy pliku wyjściowego                                                                                                                                                                                                                                                                                                               |
| `providerOptions` | object | Opcje specyficzne dla dostawcy jako obiekt JSON (np. `{"seed": 42, "draft": true}`). Dostawcy, którzy deklarują schemat typowany, walidują klucze i typy; nieznane klucze lub niedopasowania powodują pominięcie kandydata podczas fallbacku. Dostawcy bez zadeklarowanego schematu otrzymują opcje bez zmian. Uruchom `video_generate action=list`, aby zobaczyć, co akceptuje każdy dostawca |

Nie wszyscy dostawcy obsługują wszystkie parametry. OpenClaw już normalizuje czas trwania do najbliższej wartości obsługiwanej przez dostawcę, a także mapuje przetłumaczone wskazówki geometrii, takie jak rozmiar na proporcje obrazu, gdy zapasowy dostawca udostępnia inny interfejs sterowania. Rzeczywiście nieobsługiwane zastąpienia są ignorowane na zasadzie best-effort i zgłaszane jako ostrzeżenia w wyniku narzędzia. Twarde limity możliwości (takie jak zbyt wiele wejść referencyjnych) powodują błąd przed wysłaniem.

Wyniki narzędzia raportują zastosowane ustawienia. Gdy OpenClaw przemapowuje czas trwania lub geometrię podczas fallbacku dostawcy, zwrócone wartości `durationSeconds`, `size`, `aspectRatio` i `resolution` odzwierciedlają to, co zostało wysłane, a `details.normalization` zawiera mapowanie z wartości żądanych na zastosowane.

Wejścia referencyjne również wybierają tryb działania:

- Brak mediów referencyjnych: `generate`
- Dowolny obraz referencyjny: `imageToVideo`
- Dowolny film referencyjny: `videoToVideo`
- Referencyjne wejścia audio nie zmieniają rozstrzygniętego trybu; są stosowane dodatkowo do trybu wybranego przez referencje obrazu/filmu i działają tylko z dostawcami, którzy deklarują `maxInputAudios`

Mieszane referencje obrazów i filmów nie stanowią stabilnej wspólnej powierzchni możliwości.
Preferuj jeden typ referencji na żądanie.

#### Fallback i opcje typowane

Niektóre kontrole możliwości są stosowane w warstwie fallbacku, a nie na granicy
narzędzia, aby żądanie przekraczające limity głównego dostawcy
mogło nadal zostać uruchomione przez odpowiedni fallback:

- Jeśli aktywny kandydat nie deklaruje `maxInputAudios` (lub deklaruje
  `0`), jest pomijany, gdy żądanie zawiera referencje audio, i
  sprawdzany jest kolejny kandydat.
- Jeśli `maxDurationSeconds` aktywnego kandydata jest niższe niż żądane
  `durationSeconds`, a kandydat nie deklaruje listy
  `supportedDurationSeconds`,
  jest pomijany.
- Jeśli żądanie zawiera `providerOptions`, a aktywny kandydat
  jawnie deklaruje typowany schemat `providerOptions`, kandydat jest
  pomijany, gdy podane klucze nie występują w schemacie lub typy wartości
  nie pasują. Dostawcy, którzy jeszcze nie zadeklarowali schematu, otrzymują
  opcje bez zmian (zgodny wstecznie pass-through). Dostawca może
  jawnie zrezygnować ze wszystkich opcji dostawcy, deklarując pusty schemat
  (`capabilities.providerOptions: {}`), co powoduje takie samo pominięcie jak
  niedopasowanie typu.

Pierwszy powód pominięcia w żądaniu jest logowany na poziomie `warn`, aby operatorzy widzieli,
kiedy główny dostawca został pominięty; kolejne pominięcia są logowane na poziomie
`debug`, aby długie łańcuchy fallbacku pozostawały ciche. Jeśli każdy kandydat zostanie pominięty,
zbiorczy błąd zawiera powód pominięcia dla każdego z nich.

## Akcje

- **generate** (domyślnie) -- utwórz film na podstawie podanego promptu i opcjonalnych wejść referencyjnych.
- **status** -- sprawdź stan zadania generowania filmu będącego w toku dla bieżącej sesji bez uruchamiania kolejnego generowania.
- **list** -- pokaż dostępnych dostawców, modele i ich możliwości.

## Wybór modelu

Podczas generowania filmu OpenClaw rozstrzyga model w tej kolejności:

1. **Parametr narzędzia `model`** -- jeśli agent określi go w wywołaniu.
2. **`videoGenerationModel.primary`** -- z konfiguracji.
3. **`videoGenerationModel.fallbacks`** -- próbowane po kolei.
4. **Automatyczne wykrywanie** -- używa dostawców z prawidłowym uwierzytelnianiem, zaczynając od bieżącego domyślnego dostawcy, a następnie pozostałych dostawców w kolejności alfabetycznej.

Jeśli dostawca zawiedzie, automatycznie sprawdzany jest kolejny kandydat. Jeśli wszyscy kandydaci zawiodą, błąd zawiera szczegóły z każdej próby.

Ustaw `agents.defaults.mediaGenerationAutoProviderFallback: false`, jeśli chcesz,
aby generowanie filmów używało tylko jawnych wpisów `model`, `primary` i `fallbacks`.

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

| Dostawca             | Uwagi                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba              | Używa asynchronicznego endpointu DashScope/Model Studio. Obrazy i filmy referencyjne muszą być zdalnymi adresami URL `http(s)`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| BytePlus (1.0)       | Id dostawcy `byteplus`. Modele: `seedance-1-0-pro-250528` (domyślny), `seedance-1-0-pro-t2v-250528`, `seedance-1-0-pro-fast-251015`, `seedance-1-0-lite-t2v-250428`, `seedance-1-0-lite-i2v-250428`. Modele T2V (`*-t2v-*`) nie akceptują wejść obrazów; modele I2V i ogólne modele `*-pro-*` obsługują pojedynczy obraz referencyjny (pierwsza klatka). Przekaż obraz pozycyjnie lub ustaw `role: "first_frame"`. Identyfikatory modeli T2V są automatycznie przełączane na odpowiadający wariant I2V, gdy podany jest obraz. Obsługiwane klucze `providerOptions`: `seed` (number), `draft` (boolean, wymusza 480p), `camera_fixed` (boolean). |
| BytePlus Seedance 1.5 | Wymaga pluginu [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark). Id dostawcy `byteplus-seedance15`. Model: `seedance-1-5-pro-251215`. Używa zunifikowanego API `content[]`. Obsługuje maksymalnie 2 obrazy wejściowe (first_frame + last_frame). Wszystkie wejścia muszą być zdalnymi adresami URL `https://`. Ustaw `role: "first_frame"` / `"last_frame"` dla każdego obrazu lub przekaż obrazy pozycyjnie. `aspectRatio: "adaptive"` automatycznie wykrywa proporcje z obrazu wejściowego. `audio: true` jest mapowane na `generate_audio`. `providerOptions.seed` (number) jest przekazywane dalej.                                                                                                  |
| BytePlus Seedance 2.0 | Wymaga pluginu [`@openclaw/byteplus-modelark`](https://www.npmjs.com/package/@openclaw/byteplus-modelark). Id dostawcy `byteplus-seedance2`. Modele: `dreamina-seedance-2-0-260128`, `dreamina-seedance-2-0-fast-260128`. Używa zunifikowanego API `content[]`. Obsługuje do 9 obrazów referencyjnych, 3 filmów referencyjnych i 3 plików audio referencyjnych. Wszystkie wejścia muszą być zdalnymi adresami URL `https://`. Ustaw `role` dla każdego zasobu — obsługiwane wartości: `"first_frame"`, `"last_frame"`, `"reference_image"`, `"reference_video"`, `"reference_audio"`. `aspectRatio: "adaptive"` automatycznie wykrywa proporcje z obrazu wejściowego. `audio: true` jest mapowane na `generate_audio`. `providerOptions.seed` (number) jest przekazywane dalej. |
| ComfyUI              | Wykonywanie lokalne lub chmurowe sterowane przez workflow. Obsługuje tekst-na-film i obraz-na-film przez skonfigurowany graf.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| fal                  | Używa przepływu opartego na kolejce dla długotrwałych zadań. Tylko pojedynczy obraz referencyjny.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| Google               | Używa Gemini/Veo. Obsługuje jeden obraz lub jeden film referencyjny.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| MiniMax              | Tylko pojedynczy obraz referencyjny.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| OpenAI               | Przekazywane jest tylko zastąpienie `size`. Pozostałe zastąpienia stylu (`aspectRatio`, `resolution`, `audio`, `watermark`) są ignorowane z ostrzeżeniem.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Qwen                 | Ten sam backend DashScope co Alibaba. Wejścia referencyjne muszą być zdalnymi adresami URL `http(s)`; pliki lokalne są odrzucane z góry.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| Runway               | Obsługuje pliki lokalne przez URI `data`. Film-na-film wymaga `runway/gen4_aleph`. Uruchomienia tylko tekstowe udostępniają proporcje `16:9` i `9:16`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Together             | Tylko pojedynczy obraz referencyjny.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| Vydra                | Używa bezpośrednio `https://www.vydra.ai/api/v1`, aby uniknąć przekierowań usuwających uwierzytelnianie. `veo3` jest dołączony wyłącznie jako tekst-na-film; `kling` wymaga zdalnego URL obrazu.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| xAI                  | Obsługuje tekst-na-film, obraz-na-film oraz zdalne przepływy edycji/rozszerzania filmów.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |

## Tryby możliwości dostawców

Wspólny kontrakt generowania filmów pozwala teraz dostawcom deklarować możliwości
specyficzne dla trybu zamiast tylko płaskich limitów zbiorczych. Nowe implementacje
dostawców powinny preferować jawne bloki trybów:

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

Płaskie pola zbiorcze, takie jak `maxInputImages` i `maxInputVideos`, nie
wystarczają do reklamowania obsługi trybów transformacji. Dostawcy powinni jawnie deklarować
`generate`, `imageToVideo` i `videoToVideo`, aby testy live,
testy kontraktowe oraz wspólne narzędzie `video_generate` mogły deterministycznie
walidować obsługę trybów.

## Testy live

Zakres testów live typu opt-in dla wspólnych dołączonych dostawców:

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

Wrapper repozytorium:

```bash
pnpm test:live:media video
```

Ten plik live ładuje brakujące zmienne środowiskowe dostawców z `~/.profile`, domyślnie preferuje
klucze API z live/env przed zapisanymi profilami uwierzytelniania i uruchamia
zadeklarowane tryby, które może bezpiecznie przetestować z lokalnymi mediami:

- `generate` dla każdego dostawcy w zestawie
- `imageToVideo`, gdy `capabilities.imageToVideo.enabled`
- `videoToVideo`, gdy `capabilities.videoToVideo.enabled` i dostawca/model
  akceptuje lokalne wejście wideo oparte na buforze we wspólnym zestawie

Obecnie wspólna ścieżka live `videoToVideo` obejmuje:

- `runway` tylko wtedy, gdy wybierzesz `runway/gen4_aleph`

## Konfiguracja

Ustaw domyślny model generowania filmów w konfiguracji OpenClaw:

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
- [Zadania w tle](/pl/automation/tasks) -- śledzenie zadań dla asynchronicznego generowania filmów
- [Alibaba Model Studio](/pl/providers/alibaba)
- [BytePlus](/pl/concepts/model-providers#byteplus-international)
- [ComfyUI](/pl/providers/comfy)
- [fal](/pl/providers/fal)
- [Google (Gemini)](/pl/providers/google)
- [MiniMax](/pl/providers/minimax)
- [OpenAI](/pl/providers/openai)
- [Qwen](/pl/providers/qwen)
- [Runway](/pl/providers/runway)
- [Together AI](/pl/providers/together)
- [Vydra](/pl/providers/vydra)
- [xAI](/pl/providers/xai)
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
- [Modele](/pl/concepts/models)
