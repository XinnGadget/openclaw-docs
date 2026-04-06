---
read_when:
    - Chcesz używać modeli MiniMax w OpenClaw
    - Potrzebujesz wskazówek dotyczących konfiguracji MiniMax
summary: Używanie modeli MiniMax w OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-06T03:12:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ca35c43cdde53f6f09d9e12d48ce09e4c099cf8cbe1407ac6dbb45b1422507e
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Dostawca MiniMax w OpenClaw domyślnie używa **MiniMax M2.7**.

MiniMax udostępnia także:

- wbudowaną syntezę mowy przez T2A v2
- wbudowane rozumienie obrazów przez `MiniMax-VL-01`
- wbudowane generowanie muzyki przez `music-2.5+`
- wbudowane `web_search` przez API wyszukiwania MiniMax Coding Plan

Podział dostawców:

- `minimax`: dostawca tekstu z kluczem API oraz wbudowane generowanie obrazów, rozumienie obrazów, mowa i wyszukiwanie w sieci
- `minimax-portal`: dostawca tekstu OAuth oraz wbudowane generowanie obrazów i rozumienie obrazów

## Zestaw modeli

- `MiniMax-M2.7`: domyślny hostowany model rozumowania.
- `MiniMax-M2.7-highspeed`: szybszy poziom rozumowania M2.7.
- `image-01`: model generowania obrazów (generowanie oraz edycja obraz-do-obrazu).

## Generowanie obrazów

Plugin MiniMax rejestruje model `image-01` dla narzędzia `image_generate`. Obsługuje on:

- **Generowanie tekst-do-obrazu** z kontrolą proporcji.
- **Edycję obraz-do-obrazu** (odniesienie do obiektu) z kontrolą proporcji.
- Do **9 obrazów wyjściowych** na żądanie.
- Do **1 obrazu referencyjnego** na żądanie edycji.
- Obsługiwane proporcje: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`.

Aby używać MiniMax do generowania obrazów, ustaw go jako dostawcę generowania obrazów:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Plugin używa tego samego `MINIMAX_API_KEY` albo uwierzytelniania OAuth co modele tekstowe. Jeśli MiniMax jest już skonfigurowany, nie jest wymagana żadna dodatkowa konfiguracja.

Zarówno `minimax`, jak i `minimax-portal` rejestrują `image_generate` z tym samym
modelem `image-01`. Konfiguracje z kluczem API używają `MINIMAX_API_KEY`; konfiguracje OAuth mogą używać
zamiast tego wbudowanej ścieżki uwierzytelniania `minimax-portal`.

Gdy onboarding albo konfiguracja z kluczem API zapisuje jawne wpisy
`models.providers.minimax`, OpenClaw materializuje `MiniMax-M2.7` i
`MiniMax-M2.7-highspeed` z `input: ["text", "image"]`.

Sam wbudowany katalog tekstowy MiniMax pozostaje metadanymi tylko tekstowymi, dopóki
nie istnieje jawna konfiguracja tego dostawcy. Rozumienie obrazów jest udostępniane osobno
przez należącego do pluginu dostawcę mediów `MiniMax-VL-01`.

Zobacz [Image Generation](/pl/tools/image-generation), aby poznać współdzielone parametry
narzędzia, wybór dostawcy i zachowanie failover.

## Generowanie muzyki

Wbudowany plugin `minimax` rejestruje także generowanie muzyki przez współdzielone
narzędzie `music_generate`.

- Domyślny model muzyczny: `minimax/music-2.5+`
- Obsługuje także `minimax/music-2.5` i `minimax/music-2.0`
- Kontrolki promptu: `lyrics`, `instrumental`, `durationSeconds`
- Format wyjściowy: `mp3`
- Uruchomienia powiązane z sesją są odłączane przez współdzielony przepływ zadanie/status, w tym `action: "status"`

Aby używać MiniMax jako domyślnego dostawcy muzyki:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

Zobacz [Music Generation](/tools/music-generation), aby poznać współdzielone parametry
narzędzia, wybór dostawcy i zachowanie failover.

## Generowanie wideo

Wbudowany plugin `minimax` rejestruje także generowanie wideo przez współdzielone
narzędzie `video_generate`.

- Domyślny model wideo: `minimax/MiniMax-Hailuo-2.3`
- Tryby: tekst-do-wideo i przepływy z pojedynczym obrazem referencyjnym
- Obsługuje `aspectRatio` i `resolution`

Aby używać MiniMax jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

Zobacz [Video Generation](/tools/video-generation), aby poznać współdzielone parametry
narzędzia, wybór dostawcy i zachowanie failover.

## Rozumienie obrazów

Plugin MiniMax rejestruje rozumienie obrazów oddzielnie od katalogu
tekstowego:

- `minimax`: domyślny model obrazów `MiniMax-VL-01`
- `minimax-portal`: domyślny model obrazów `MiniMax-VL-01`

Dlatego automatyczny routing mediów może używać rozumienia obrazów MiniMax nawet
wtedy, gdy wbudowany katalog dostawcy tekstu nadal pokazuje odwołania do czatu M2.7
jako metadane tylko tekstowe.

## Wyszukiwanie w sieci

Plugin MiniMax rejestruje także `web_search` przez API wyszukiwania
MiniMax Coding Plan.

- ID dostawcy: `minimax`
- Wyniki strukturalne: tytuły, URL-e, snippety, powiązane zapytania
- Preferowana zmienna env: `MINIMAX_CODE_PLAN_KEY`
- Akceptowany alias env: `MINIMAX_CODING_API_KEY`
- Fallback zgodności: `MINIMAX_API_KEY`, gdy już wskazuje na token coding-plan
- Ponowne użycie regionu: `plugins.entries.minimax.config.webSearch.region`, potem `MINIMAX_API_HOST`, potem bazowe URL-e dostawców MiniMax
- Wyszukiwanie pozostaje przy ID dostawcy `minimax`; konfiguracja OAuth CN/global może nadal pośrednio sterować regionem przez `models.providers.minimax-portal.baseUrl`

Konfiguracja znajduje się pod `plugins.entries.minimax.config.webSearch.*`.
Zobacz [MiniMax Search](/pl/tools/minimax-search).

## Wybierz konfigurację

### MiniMax OAuth (Coding Plan) - zalecane

**Najlepsze dla:** szybkiej konfiguracji MiniMax Coding Plan przez OAuth, bez wymaganego klucza API.

Uwierzytelnij się za pomocą jawnego regionalnego wyboru OAuth:

```bash
openclaw onboard --auth-choice minimax-global-oauth
# or
openclaw onboard --auth-choice minimax-cn-oauth
```

Mapowanie opcji:

- `minimax-global-oauth`: użytkownicy międzynarodowi (`api.minimax.io`)
- `minimax-cn-oauth`: użytkownicy w Chinach (`api.minimaxi.com`)

Szczegóły znajdziesz w README pakietu pluginu MiniMax w repozytorium OpenClaw.

### MiniMax M2.7 (klucz API)

**Najlepsze dla:** hostowanego MiniMax z API zgodnym z Anthropic.

Skonfiguruj przez CLI:

- Interaktywny onboarding:

```bash
openclaw onboard --auth-choice minimax-global-api
# or
openclaw onboard --auth-choice minimax-cn-api
```

- `minimax-global-api`: użytkownicy międzynarodowi (`api.minimax.io`)
- `minimax-cn-api`: użytkownicy w Chinach (`api.minimaxi.com`)

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
          {
            id: "MiniMax-M2.7-highspeed",
            name: "MiniMax M2.7 Highspeed",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

W ścieżce strumieniowania zgodnej z Anthropic OpenClaw teraz domyślnie wyłącza
thinking dla MiniMax, chyba że jawnie ustawisz `thinking` samodzielnie. Punkt końcowy
strumieniowania MiniMax emituje `reasoning_content` w fragmentach delta w stylu OpenAI
zamiast natywnych bloków thinking Anthropic, co może ujawniać wewnętrzne rozumowanie
w widocznym wyjściu, jeśli pozostanie to niejawnie włączone.

### MiniMax M2.7 jako fallback (przykład)

**Najlepsze dla:** zachowania najmocniejszego modelu najnowszej generacji jako głównego i przełączania awaryjnego na MiniMax M2.7.
Poniższy przykład używa Opus jako konkretnego modelu głównego; zamień go na preferowany model główny najnowszej generacji.

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
    },
  },
}
```

## Konfiguracja przez `openclaw configure`

Użyj interaktywnego kreatora konfiguracji, aby ustawić MiniMax bez edytowania JSON:

1. Uruchom `openclaw configure`.
2. Wybierz **Model/auth**.
3. Wybierz opcję uwierzytelniania **MiniMax**.
4. Po wyświetleniu monitu wybierz swój domyślny model.

Aktualne opcje uwierzytelniania MiniMax w kreatorze/CLI:

- `minimax-global-oauth`
- `minimax-cn-oauth`
- `minimax-global-api`
- `minimax-cn-api`

## Opcje konfiguracji

- `models.providers.minimax.baseUrl`: preferowane `https://api.minimax.io/anthropic` (zgodne z Anthropic); `https://api.minimax.io/v1` jest opcjonalne dla ładunków zgodnych z OpenAI.
- `models.providers.minimax.api`: preferowane `anthropic-messages`; `openai-completions` jest opcjonalne dla ładunków zgodnych z OpenAI.
- `models.providers.minimax.apiKey`: klucz API MiniMax (`MINIMAX_API_KEY`).
- `models.providers.minimax.models`: zdefiniuj `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost`.
- `agents.defaults.models`: aliasuj modele, które chcesz mieć na liście dozwolonych.
- `models.mode`: pozostaw `merge`, jeśli chcesz dodać MiniMax obok wbudowanych dostawców.

## Uwagi

- Odwołania do modeli podążają za ścieżką uwierzytelniania:
  - konfiguracja z kluczem API: `minimax/<model>`
  - konfiguracja OAuth: `minimax-portal/<model>`
- Domyślny model czatu: `MiniMax-M2.7`
- Alternatywny model czatu: `MiniMax-M2.7-highspeed`
- Przy `api: "anthropic-messages"` OpenClaw wstrzykuje
  `thinking: { type: "disabled" }`, chyba że thinking jest już jawnie ustawione w
  params/config.
- `/fast on` lub `params.fastMode: true` przepisuje `MiniMax-M2.7` na
  `MiniMax-M2.7-highspeed` w ścieżce strumienia zgodnej z Anthropic.
- Onboarding i bezpośrednia konfiguracja z kluczem API zapisują jawne definicje modeli z
  `input: ["text", "image"]` dla obu wariantów M2.7
- Wbudowany katalog dostawców obecnie udostępnia odwołania czatu jako
  metadane tylko tekstowe, dopóki nie istnieje jawna konfiguracja dostawcy MiniMax
- API użycia Coding Plan: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (wymaga klucza coding plan).
- OpenClaw normalizuje użycie MiniMax coding-plan do tego samego wyświetlania `% left`,
  którego używają inni dostawcy. Surowe pola `usage_percent` / `usagePercent` MiniMax
  oznaczają pozostały limit, a nie zużyty limit, więc OpenClaw je odwraca.
  Jeśli są obecne, pierwszeństwo mają pola liczbowe. Gdy API zwraca `model_remains`,
  OpenClaw preferuje wpis modelu czatu, w razie potrzeby wyprowadza etykietę okna z
  `start_time` / `end_time` i dołącza wybraną nazwę modelu
  do etykiety planu, aby okna coding-plan były łatwiejsze do odróżnienia.
- Migawki użycia traktują `minimax`, `minimax-cn` i `minimax-portal` jako
  tę samą powierzchnię limitu MiniMax i preferują zapisany OAuth MiniMax przed
  fallbackiem do zmiennych env klucza Coding Plan.
- Zaktualizuj wartości cen w `models.json`, jeśli potrzebujesz dokładnego śledzenia kosztów.
- Link polecający do MiniMax Coding Plan (10% zniżki): [https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- Zobacz [/concepts/model-providers](/pl/concepts/model-providers), aby poznać zasady dostawców.
- Użyj `openclaw models list`, aby potwierdzić bieżące ID dostawcy, a następnie przełącz za pomocą
  `openclaw models set minimax/MiniMax-M2.7` lub
  `openclaw models set minimax-portal/MiniMax-M2.7`.

## Rozwiązywanie problemów

### "Unknown model: minimax/MiniMax-M2.7"

To zwykle oznacza, że **dostawca MiniMax nie jest skonfigurowany** (brak pasującego
wpisu dostawcy i brak profilu uwierzytelniania/env key MiniMax). Poprawka tego
wykrywania znajduje się w wersji **2026.1.12**. Napraw to przez:

- aktualizację do **2026.1.12** (albo uruchomienie ze źródła `main`), a następnie ponowne uruchomienie bramy.
- uruchomienie `openclaw configure` i wybranie opcji uwierzytelniania **MiniMax**, albo
- ręczne dodanie pasującego bloku `models.providers.minimax` lub
  `models.providers.minimax-portal`, albo
- ustawienie `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` albo profilu uwierzytelniania MiniMax,
  aby odpowiedni dostawca mógł zostać wstrzyknięty.

Upewnij się, że ID modelu jest **wrażliwe na wielkość liter**:

- ścieżka klucza API: `minimax/MiniMax-M2.7` lub `minimax/MiniMax-M2.7-highspeed`
- ścieżka OAuth: `minimax-portal/MiniMax-M2.7` lub
  `minimax-portal/MiniMax-M2.7-highspeed`

Następnie sprawdź ponownie za pomocą:

```bash
openclaw models list
```
