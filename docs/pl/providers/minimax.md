---
read_when:
    - Chcesz używać modeli MiniMax w OpenClaw
    - Potrzebujesz wskazówek dotyczących konfiguracji MiniMax
summary: Używaj modeli MiniMax w OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T23:31:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Dostawca MiniMax w OpenClaw domyślnie używa **MiniMax M2.7**.

MiniMax zapewnia także:

- Bundlową syntezę mowy przez T2A v2
- Bundlowe rozumienie obrazów przez `MiniMax-VL-01`
- Bundlowe generowanie muzyki przez `music-2.5+`
- Bundlowe `web_search` przez API wyszukiwania MiniMax Coding Plan

Podział dostawców:

| ID dostawcy      | Auth     | Capabilities                                                   |
| ---------------- | -------- | -------------------------------------------------------------- |
| `minimax`        | Klucz API | Tekst, generowanie obrazów, rozumienie obrazów, mowa, web search |
| `minimax-portal` | OAuth    | Tekst, generowanie obrazów, rozumienie obrazów                |

## Zestaw modeli

| Model                    | Typ               | Opis                                      |
| ------------------------ | ----------------- | ----------------------------------------- |
| `MiniMax-M2.7`           | Czat (rozumowanie) | Domyślny hostowany model rozumowania      |
| `MiniMax-M2.7-highspeed` | Czat (rozumowanie) | Szybszy poziom rozumowania M2.7           |
| `MiniMax-VL-01`          | Vision            | Model rozumienia obrazów                  |
| `image-01`               | Generowanie obrazów | Text-to-image i edycja image-to-image   |
| `music-2.5+`             | Generowanie muzyki | Domyślny model muzyczny                  |
| `music-2.5`              | Generowanie muzyki | Poprzedni poziom generowania muzyki      |
| `music-2.0`              | Generowanie muzyki | Starszy poziom generowania muzyki        |
| `MiniMax-Hailuo-2.3`     | Generowanie wideo | Przepływy text-to-video i z obrazem referencyjnym |

## Pierwsze kroki

Wybierz preferowaną metodę auth i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **Najlepsze do:** szybkiej konfiguracji z MiniMax Coding Plan przez OAuth, bez wymaganego klucza API.

    <Tabs>
      <Tab title="Międzynarodowy">
        <Steps>
          <Step title="Uruchom onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            To uwierzytelnia względem `api.minimax.io`.
          </Step>
          <Step title="Sprawdź, czy model jest dostępny">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="Chiny">
        <Steps>
          <Step title="Uruchom onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            To uwierzytelnia względem `api.minimaxi.com`.
          </Step>
          <Step title="Sprawdź, czy model jest dostępny">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    Konfiguracje OAuth używają identyfikatora dostawcy `minimax-portal`. Odwołania do modeli mają postać `minimax-portal/MiniMax-M2.7`.
    </Note>

    <Tip>
    Link polecający do MiniMax Coding Plan (10% zniżki): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="Klucz API">
    **Najlepsze do:** hostowanego MiniMax z API zgodnym z Anthropic.

    <Tabs>
      <Tab title="Międzynarodowy">
        <Steps>
          <Step title="Uruchom onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            To konfiguruje `api.minimax.io` jako bazowy URL.
          </Step>
          <Step title="Sprawdź, czy model jest dostępny">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="Chiny">
        <Steps>
          <Step title="Uruchom onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            To konfiguruje `api.minimaxi.com` jako bazowy URL.
          </Step>
          <Step title="Sprawdź, czy model jest dostępny">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### Przykład konfiguracji

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

    <Warning>
    Na ścieżce strumieniowania zgodnej z Anthropic OpenClaw domyślnie wyłącza thinking MiniMax, chyba że jawnie ustawisz `thinking` samodzielnie. Endpoint strumieniowania MiniMax emituje `reasoning_content` w fragmentach delta w stylu OpenAI zamiast natywnych bloków thinking Anthropic, co może ujawniać wewnętrzne rozumowanie w widocznym wyjściu, jeśli pozostanie domyślnie włączone.
    </Warning>

    <Note>
    Konfiguracje z kluczem API używają identyfikatora dostawcy `minimax`. Odwołania do modeli mają postać `minimax/MiniMax-M2.7`.
    </Note>

  </Tab>
</Tabs>

## Konfiguracja przez `openclaw configure`

Użyj interaktywnego kreatora konfiguracji, aby ustawić MiniMax bez edytowania JSON:

<Steps>
  <Step title="Uruchom kreator">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="Wybierz Model/auth">
    Wybierz w menu **Model/auth**.
  </Step>
  <Step title="Wybierz opcję auth MiniMax">
    Wybierz jedną z dostępnych opcji MiniMax:

    | Wybór auth | Opis |
    | --- | --- |
    | `minimax-global-oauth` | Międzynarodowy OAuth (Coding Plan) |
    | `minimax-cn-oauth` | OAuth dla Chin (Coding Plan) |
    | `minimax-global-api` | Międzynarodowy klucz API |
    | `minimax-cn-api` | Klucz API dla Chin |

  </Step>
  <Step title="Wybierz model domyślny">
    Po wyświetleniu monitu wybierz model domyślny.
  </Step>
</Steps>

## Capabilities

### Generowanie obrazów

Plugin MiniMax rejestruje model `image-01` dla narzędzia `image_generate`. Obsługuje:

- **Generowanie text-to-image** z kontrolą proporcji
- **Edycja image-to-image** (odwołanie do obiektu) z kontrolą proporcji
- Do **9 obrazów wyjściowych** na żądanie
- Do **1 obrazu referencyjnego** na żądanie edycji
- Obsługiwane proporcje: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`

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

Plugin używa tego samego auth `MINIMAX_API_KEY` lub OAuth co modele tekstowe. Jeśli MiniMax jest już skonfigurowany, nie jest wymagana dodatkowa konfiguracja.

Zarówno `minimax`, jak i `minimax-portal` rejestrują `image_generate` z tym samym
modelem `image-01`. Konfiguracje z kluczem API używają `MINIMAX_API_KEY`; konfiguracje OAuth mogą używać
zamiast tego bundlowej ścieżki auth `minimax-portal`.

Gdy onboarding albo konfiguracja z kluczem API zapisuje jawne wpisy `models.providers.minimax`,
OpenClaw materializuje `MiniMax-M2.7` i
`MiniMax-M2.7-highspeed` z `input: ["text", "image"]`.

Sam wbudowany bundlowy katalog tekstowy MiniMax pozostaje metadanymi tylko dla tekstu, dopóki
nie pojawi się jawna konfiguracja dostawcy. Rozumienie obrazów jest udostępniane osobno
przez należącego do Pluginu dostawcę mediów `MiniMax-VL-01`.

<Note>
Zobacz [Generowanie obrazów](/pl/tools/image-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

### Generowanie muzyki

Bundlowy Plugin `minimax` rejestruje także generowanie muzyki przez wspólne
narzędzie `music_generate`.

- Domyślny model muzyczny: `minimax/music-2.5+`
- Obsługuje także `minimax/music-2.5` i `minimax/music-2.0`
- Kontrolki promptu: `lyrics`, `instrumental`, `durationSeconds`
- Format wyjściowy: `mp3`
- Przebiegi oparte na sesji są odłączane przez wspólny przepływ zadania/statusu, w tym `action: "status"`

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

<Note>
Zobacz [Generowanie muzyki](/pl/tools/music-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

### Generowanie wideo

Bundlowy Plugin `minimax` rejestruje także generowanie wideo przez wspólne
narzędzie `video_generate`.

- Domyślny model wideo: `minimax/MiniMax-Hailuo-2.3`
- Tryby: text-to-video i przepływy z pojedynczym obrazem referencyjnym
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

<Note>
Zobacz [Generowanie wideo](/pl/tools/video-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

### Rozumienie obrazów

Plugin MiniMax rejestruje rozumienie obrazów osobno od katalogu
tekstowego:

| ID dostawcy      | Domyślny model obrazu |
| ---------------- | --------------------- |
| `minimax`        | `MiniMax-VL-01`       |
| `minimax-portal` | `MiniMax-VL-01`       |

Dlatego automatyczne routowanie mediów może używać rozumienia obrazów MiniMax nawet
wtedy, gdy bundlowy katalog dostawcy tekstu nadal pokazuje wyłącznie tekstowe odwołania czatu M2.7.

### Web search

Plugin MiniMax rejestruje także `web_search` przez API wyszukiwania MiniMax Coding Plan.

- Identyfikator dostawcy: `minimax`
- Wyniki strukturalne: tytuły, URL-e, fragmenty, powiązane zapytania
- Preferowana zmienna env: `MINIMAX_CODE_PLAN_KEY`
- Akceptowany alias env: `MINIMAX_CODING_API_KEY`
- Fallback zgodności: `MINIMAX_API_KEY`, gdy już wskazuje na token coding-plan
- Ponowne użycie regionu: `plugins.entries.minimax.config.webSearch.region`, następnie `MINIMAX_API_HOST`, a potem bazowe URL-e dostawcy MiniMax
- Wyszukiwanie pozostaje przy identyfikatorze dostawcy `minimax`; konfiguracja OAuth CN/global nadal może pośrednio sterować regionem przez `models.providers.minimax-portal.baseUrl`

Konfiguracja znajduje się pod `plugins.entries.minimax.config.webSearch.*`.

<Note>
Zobacz [Wyszukiwanie MiniMax](/pl/tools/minimax-search), aby poznać pełną konfigurację i użycie web search.
</Note>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Opcje konfiguracji">
    | Opcja | Opis |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | Preferuj `https://api.minimax.io/anthropic` (zgodne z Anthropic); `https://api.minimax.io/v1` jest opcjonalne dla payloadów zgodnych z OpenAI |
    | `models.providers.minimax.api` | Preferuj `anthropic-messages`; `openai-completions` jest opcjonalne dla payloadów zgodnych z OpenAI |
    | `models.providers.minimax.apiKey` | Klucz API MiniMax (`MINIMAX_API_KEY`) |
    | `models.providers.minimax.models` | Zdefiniuj `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost` |
    | `agents.defaults.models` | Modele aliasów, które chcesz umieścić na allowlist |
    | `models.mode` | Zachowaj `merge`, jeśli chcesz dodać MiniMax obok wbudowanych |
  </Accordion>

  <Accordion title="Domyślne ustawienia thinking">
    Przy `api: "anthropic-messages"` OpenClaw wstrzykuje `thinking: { type: "disabled" }`, chyba że thinking jest już jawnie ustawione w parametrach/konfiguracji.

    Zapobiega to emitowaniu przez endpoint strumieniowania MiniMax `reasoning_content` w fragmentach delta w stylu OpenAI, co ujawniałoby wewnętrzne rozumowanie w widocznym wyjściu.

  </Accordion>

  <Accordion title="Tryb szybki">
    `/fast on` albo `params.fastMode: true` przepisuje `MiniMax-M2.7` na `MiniMax-M2.7-highspeed` na ścieżce strumieniowania zgodnej z Anthropic.
  </Accordion>

  <Accordion title="Przykład fallback">
    **Najlepsze do:** zachowania najmocniejszego modelu najnowszej generacji jako podstawowego i przejścia awaryjnego na MiniMax M2.7. Poniższy przykład używa Opus jako konkretnego modelu podstawowego; zamień go na preferowany model podstawowy najnowszej generacji.

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

  </Accordion>

  <Accordion title="Szczegóły użycia Coding Plan">
    - API użycia Coding Plan: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (wymaga klucza coding plan).
    - OpenClaw normalizuje użycie MiniMax coding plan do tego samego formatu wyświetlania `% pozostało`, co u innych dostawców. Surowe pola MiniMax `usage_percent` / `usagePercent` oznaczają pozostały limit, a nie wykorzystany limit, więc OpenClaw je odwraca. Pola oparte na liczbie mają pierwszeństwo, jeśli są obecne.
    - Gdy API zwraca `model_remains`, OpenClaw preferuje wpis modelu czatu, w razie potrzeby wyprowadza etykietę okna z `start_time` / `end_time` i uwzględnia wybraną nazwę modelu w etykiecie planu, aby łatwiej odróżniać okna coding plan.
    - Snapshoty użycia traktują `minimax`, `minimax-cn` i `minimax-portal` jako tę samą powierzchnię limitu MiniMax oraz preferują zapisany OAuth MiniMax, zanim przejdą do fallbacku do zmiennych env klucza Coding Plan.
  </Accordion>
</AccordionGroup>

## Uwagi

- Odwołania do modeli zależą od ścieżki auth:
  - konfiguracja z kluczem API: `minimax/<model>`
  - konfiguracja OAuth: `minimax-portal/<model>`
- Domyślny model czatu: `MiniMax-M2.7`
- Alternatywny model czatu: `MiniMax-M2.7-highspeed`
- Onboarding i bezpośrednia konfiguracja klucza API zapisują jawne definicje modeli z `input: ["text", "image"]` dla obu wariantów M2.7
- Bundlowy katalog dostawcy obecnie udostępnia odwołania czatu jako metadane wyłącznie tekstowe, dopóki nie pojawi się jawna konfiguracja dostawcy MiniMax
- Zaktualizuj wartości cen w `models.json`, jeśli potrzebujesz dokładnego śledzenia kosztów
- Użyj `openclaw models list`, aby potwierdzić bieżący identyfikator dostawcy, a następnie przełącz się przez `openclaw models set minimax/MiniMax-M2.7` albo `openclaw models set minimax-portal/MiniMax-M2.7`

<Tip>
Link polecający do MiniMax Coding Plan (10% zniżki): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
Zobacz [Dostawcy modeli](/pl/concepts/model-providers), aby poznać zasady dotyczące dostawców.
</Note>

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title='"Nieznany model: minimax/MiniMax-M2.7"'>
    Zwykle oznacza to, że **dostawca MiniMax nie jest skonfigurowany** (brak pasującego wpisu dostawcy i brak klucza env/profilu auth MiniMax). Poprawka dla tego wykrywania znajduje się w wersji **2026.1.12**. Napraw to przez:

    - aktualizację do wersji **2026.1.12** (albo uruchomienie ze źródła z `main`), a następnie ponowne uruchomienie gateway;
    - uruchomienie `openclaw configure` i wybranie opcji auth **MiniMax**, albo
    - ręczne dodanie pasującego bloku `models.providers.minimax` albo `models.providers.minimax-portal`, albo
    - ustawienie `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN` albo profilu auth MiniMax, aby można było wstrzyknąć pasującego dostawcę.

    Upewnij się, że identyfikator modelu jest **rozróżniający wielkość liter**:

    - ścieżka z kluczem API: `minimax/MiniMax-M2.7` albo `minimax/MiniMax-M2.7-highspeed`
    - ścieżka OAuth: `minimax-portal/MiniMax-M2.7` albo `minimax-portal/MiniMax-M2.7-highspeed`

    Następnie sprawdź ponownie przez:

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
Więcej pomocy: [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Generowanie obrazów" href="/pl/tools/image-generation" icon="image">
    Wspólne parametry narzędzia obrazu i wybór dostawcy.
  </Card>
  <Card title="Generowanie muzyki" href="/pl/tools/music-generation" icon="music">
    Wspólne parametry narzędzia muzyki i wybór dostawcy.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Wspólne parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="Wyszukiwanie MiniMax" href="/pl/tools/minimax-search" icon="magnifying-glass">
    Konfiguracja web search przez MiniMax Coding Plan.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Ogólne rozwiązywanie problemów i FAQ.
  </Card>
</CardGroup>
