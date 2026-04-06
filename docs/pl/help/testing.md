---
read_when:
    - Uruchamiasz testy lokalnie lub w CI
    - Dodajesz regresje dla błędów modeli/dostawców
    - Debugujesz zachowanie gateway + agenta
summary: 'Zestaw do testowania: pakiety unit/e2e/live, uruchamianie w Dockerze i zakres poszczególnych testów'
title: Testowanie
x-i18n:
    generated_at: "2026-04-06T03:10:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfa174e565df5fdf957234b7909beaf1304aa026e731cc2c433ca7d931681b56
    source_path: help/testing.md
    workflow: 15
---

# Testowanie

OpenClaw ma trzy pakiety Vitest (unit/integration, e2e, live) oraz niewielki zestaw runnerów Dockera.

Ten dokument to przewodnik „jak testujemy”:

- Co obejmuje każdy pakiet testów (i czego celowo _nie_ obejmuje)
- Jakie polecenia uruchamiać w typowych przepływach pracy (lokalnie, przed pushem, debugowanie)
- Jak testy live wykrywają poświadczenia oraz wybierają modele/dostawców
- Jak dodawać regresje dla rzeczywistych problemów modeli/dostawców

## Szybki start

Na co dzień:

- Pełna bramka (oczekiwana przed pushem): `pnpm build && pnpm check && pnpm test`
- Szybsze lokalne uruchomienie pełnego pakietu na wydajnej maszynie: `pnpm test:max`
- Bezpośrednia pętla watch Vitest (nowoczesna konfiguracja projects): `pnpm test:watch`
- Bezpośrednie wskazywanie plików obsługuje teraz także ścieżki extension/channel: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`

Gdy dotykasz testów lub chcesz mieć większą pewność:

- Bramka coverage: `pnpm test:coverage`
- Pakiet E2E: `pnpm test:e2e`

Podczas debugowania rzeczywistych dostawców/modeli (wymaga prawdziwych poświadczeń):

- Pakiet live (modele + testy gateway dla narzędzi/obrazów): `pnpm test:live`
- Ciche uruchomienie jednego pliku live: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Wskazówka: gdy potrzebujesz tylko jednego nieprzechodzącego przypadku, zawężaj testy live za pomocą zmiennych środowiskowych allowlist opisanych poniżej.

## Pakiety testów (co uruchamia się gdzie)

Myśl o tych pakietach jako o „rosnącym realizmie” (i rosnącej niestabilności/koszcie):

### Unit / integration (domyślne)

- Polecenie: `pnpm test`
- Konfiguracja: natywne Vitest `projects` przez `vitest.config.ts`
- Pliki: zasoby core/unit w `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` oraz dopuszczone testy node w `ui` objęte przez `vitest.unit.config.ts`
- Zakres:
  - Czyste testy jednostkowe
  - Testy integracyjne w procesie (gateway auth, routing, narzędzia, parsowanie, konfiguracja)
  - Deterministyczne regresje dla znanych błędów
- Oczekiwania:
  - Uruchamiane w CI
  - Nie wymagają prawdziwych kluczy
  - Powinny być szybkie i stabilne
- Uwaga o projects:
  - `pnpm test`, `pnpm test:watch` i `pnpm test:changed` używają teraz tej samej natywnej konfiguracji root `projects` Vitest.
  - Bezpośrednie filtry plików są natywnie prowadzone przez graf projektów root, więc `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` działa bez własnego wrappera.
- Uwaga o embedded runner:
  - Gdy zmieniasz dane wejściowe wykrywania message-tool lub kontekst runtime compaction,
    zachowaj oba poziomy pokrycia.
  - Dodawaj ukierunkowane regresje helperów dla czystych granic routingu/normalizacji.
  - Utrzymuj też w dobrym stanie zintegrowane pakiety embedded runner:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` oraz
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Te pakiety weryfikują, że zakresowe identyfikatory i zachowanie compaction nadal przepływają
    przez rzeczywiste ścieżki `run.ts` / `compact.ts`; testy samych helperów nie są
    wystarczającym zamiennikiem dla tych ścieżek integracyjnych.
- Uwaga o puli:
  - Bazowa konfiguracja Vitest domyślnie używa teraz `threads`.
  - Współdzielona konfiguracja Vitest ustawia też `isolate: false` i używa nieizolowanego runnera w projektach root, konfiguracjach e2e i live.
  - Główna ścieżka UI zachowuje konfigurację `jsdom` i optymalizator, ale teraz także działa na współdzielonym nieizolowanym runnerze.
  - `pnpm test` dziedziczy te same domyślne wartości `threads` + `isolate: false` z konfiguracji projects w root `vitest.config.ts`.
  - Współdzielony launcher `scripts/run-vitest.mjs` domyślnie dodaje teraz także `--no-maglev` dla podrzędnych procesów Node Vitest, aby ograniczyć obciążenie kompilacji V8 podczas dużych lokalnych uruchomień. Ustaw `OPENCLAW_VITEST_ENABLE_MAGLEV=1`, jeśli chcesz porównać zachowanie ze standardowym V8.
- Uwaga o szybkiej iteracji lokalnej:
  - `pnpm test:changed` uruchamia natywną konfigurację projects z `--changed origin/main`.
  - `pnpm test:max` i `pnpm test:changed:max` zachowują tę samą natywną konfigurację projects, tylko z wyższym limitem workerów.
  - Lokalne automatyczne skalowanie workerów jest teraz celowo bardziej zachowawcze i dodatkowo ogranicza się, gdy średnie obciążenie hosta jest już wysokie, dzięki czemu wiele równoczesnych uruchomień Vitest domyślnie mniej szkodzi.
  - Bazowa konfiguracja Vitest oznacza pliki projects/config jako `forceRerunTriggers`, aby ponowne uruchomienia w trybie changed pozostawały poprawne przy zmianach w okablowaniu testów.
  - Konfiguracja utrzymuje włączone `OPENCLAW_VITEST_FS_MODULE_CACHE` na obsługiwanych hostach; ustaw `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`, jeśli chcesz mieć jedną jawną lokalizację cache do bezpośredniego profilowania.
- Uwaga o debugowaniu wydajności:
  - `pnpm test:perf:imports` włącza raportowanie czasu importu Vitest oraz szczegółowy podział importów.
  - `pnpm test:perf:imports:changed` zawęża ten sam widok profilowania do plików zmienionych od `origin/main`.
  - `pnpm test:perf:profile:main` zapisuje profil CPU głównego wątku dla kosztów startu i transformacji Vitest/Vite.
  - `pnpm test:perf:profile:runner` zapisuje profile CPU+heap runnera dla pakietu unit przy wyłączonej równoległości plików.

### E2E (gateway smoke)

- Polecenie: `pnpm test:e2e`
- Konfiguracja: `vitest.e2e.config.ts`
- Pliki: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Domyślne ustawienia runtime:
  - Używa Vitest `threads` z `isolate: false`, zgodnie z resztą repozytorium.
  - Używa adaptacyjnej liczby workerów (CI: do 2, lokalnie: domyślnie 1).
  - Domyślnie działa w trybie cichym, aby ograniczyć narzut I/O konsoli.
- Przydatne nadpisania:
  - `OPENCLAW_E2E_WORKERS=<n>` aby wymusić liczbę workerów (limit 16).
  - `OPENCLAW_E2E_VERBOSE=1` aby ponownie włączyć szczegółowe logi konsoli.
- Zakres:
  - Zachowanie end-to-end gateway z wieloma instancjami
  - Powierzchnie WebSocket/HTTP, parowanie node i cięższe scenariusze sieciowe
- Oczekiwania:
  - Uruchamiane w CI (gdy są włączone w pipeline)
  - Nie wymagają prawdziwych kluczy
  - Więcej ruchomych części niż testy unit (mogą być wolniejsze)

### E2E: smoke backendu OpenShell

- Polecenie: `pnpm test:e2e:openshell`
- Plik: `test/openshell-sandbox.e2e.test.ts`
- Zakres:
  - Uruchamia izolowany gateway OpenShell na hoście przez Docker
  - Tworzy sandbox na podstawie tymczasowego lokalnego Dockerfile
  - Testuje backend OpenShell OpenClaw przez rzeczywiste `sandbox ssh-config` + wykonanie SSH
  - Weryfikuje zachowanie zdalnego kanonicznego systemu plików przez most fs sandboxa
- Oczekiwania:
  - Tylko opt-in; nie jest częścią domyślnego uruchomienia `pnpm test:e2e`
  - Wymaga lokalnego CLI `openshell` oraz działającego demona Docker
  - Używa izolowanych `HOME` / `XDG_CONFIG_HOME`, a następnie usuwa testowy gateway i sandbox
- Przydatne nadpisania:
  - `OPENCLAW_E2E_OPENSHELL=1`, aby włączyć test przy ręcznym uruchamianiu szerszego pakietu e2e
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`, aby wskazać niestandardowe binarium CLI lub skrypt wrappera

### Live (rzeczywiści dostawcy + rzeczywiste modele)

- Polecenie: `pnpm test:live`
- Konfiguracja: `vitest.live.config.ts`
- Pliki: `src/**/*.live.test.ts`
- Domyślnie: **włączone** przez `pnpm test:live` (ustawia `OPENCLAW_LIVE_TEST=1`)
- Zakres:
  - „Czy ten dostawca/model faktycznie działa _dzisiaj_ z prawdziwymi poświadczeniami?”
  - Wychwytywanie zmian formatów dostawców, niuansów wywołań narzędzi, problemów auth i zachowania limitów
- Oczekiwania:
  - Z założenia niestabilne w CI (prawdziwe sieci, rzeczywiste polityki dostawców, limity, awarie)
  - Kosztują pieniądze / zużywają limity
  - Lepiej uruchamiać zawężone podzbiory niż „wszystko”
- Uruchomienia live źródłują `~/.profile`, aby pobrać brakujące klucze API.
- Domyślnie uruchomienia live nadal izolują `HOME` i kopiują konfigurację/materiały auth do tymczasowego katalogu domowego testów, aby fixture unit nie mogły modyfikować Twojego prawdziwego `~/.openclaw`.
- Ustaw `OPENCLAW_LIVE_USE_REAL_HOME=1` tylko wtedy, gdy świadomie chcesz, aby testy live używały Twojego rzeczywistego katalogu domowego.
- `pnpm test:live` domyślnie działa teraz w cichszym trybie: zachowuje postęp `[live] ...`, ale ukrywa dodatkowy komunikat o `~/.profile` i wycisza logi startowe gateway / szum Bonjour. Ustaw `OPENCLAW_LIVE_TEST_QUIET=0`, jeśli chcesz przywrócić pełne logi startowe.
- Rotacja kluczy API (zależna od dostawcy): ustaw `*_API_KEYS` w formacie rozdzielanym przecinkami/średnikami albo `*_API_KEY_1`, `*_API_KEY_2` (na przykład `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) albo nadpisanie per-live przez `OPENCLAW_LIVE_*_KEY`; testy ponawiają próbę przy odpowiedziach z limitem.
- Wyjście postępu/heartbeat:
  - Pakiety live emitują teraz linie postępu na stderr, dzięki czemu długie wywołania dostawców są widocznie aktywne nawet wtedy, gdy przechwytywanie konsoli Vitest jest ciche.
  - `vitest.live.config.ts` wyłącza przechwytywanie konsoli Vitest, aby linie postępu dostawcy/gateway były natychmiast strumieniowane podczas uruchomień live.
  - Dostosuj heartbeat dla modeli bezpośrednich przez `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Dostosuj heartbeat dla gateway/testów probe przez `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Który pakiet powinienem uruchomić?

Użyj tej tabeli decyzyjnej:

- Edycja logiki/testów: uruchom `pnpm test` (oraz `pnpm test:coverage`, jeśli zmieniłeś dużo)
- Dotknięcie sieci gateway / protokołu WS / parowania: dodaj `pnpm test:e2e`
- Debugowanie „mój bot nie działa” / awarii zależnych od dostawcy / wywołań narzędzi: uruchom zawężone `pnpm test:live`

## Live: przegląd możliwości node Android

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Skrypt: `pnpm android:test:integration`
- Cel: wywołać **każde aktualnie ogłaszane polecenie** podłączonego node Android i potwierdzić zachowanie kontraktu poleceń.
- Zakres:
  - Ręczna konfiguracja wstępna / warunki wstępne (pakiet nie instaluje, nie uruchamia ani nie paruje aplikacji).
  - Walidacja `node.invoke` gateway polecenie po poleceniu dla wybranego node Android.
- Wymagana konfiguracja wstępna:
  - Aplikacja Android jest już podłączona i sparowana z gateway.
  - Aplikacja pozostaje na pierwszym planie.
  - Uprawnienia/zgoda na przechwytywanie są przyznane dla możliwości, które mają przechodzić test.
- Opcjonalne nadpisania celu:
  - `OPENCLAW_ANDROID_NODE_ID` lub `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Pełne informacje o konfiguracji Androida: [Aplikacja Android](/pl/platforms/android)

## Live: smoke modeli (klucze profili)

Testy live są podzielone na dwie warstwy, aby można było izolować awarie:

- „Direct model” mówi nam, czy dostawca/model w ogóle odpowiada przy użyciu danego klucza.
- „Gateway smoke” mówi nam, czy działa pełny pipeline gateway+agent dla tego modelu (sesje, historia, narzędzia, zasady sandboxa itd.).

### Warstwa 1: Bezpośrednie uzupełnianie modelu (bez gateway)

- Test: `src/agents/models.profiles.live.test.ts`
- Cel:
  - Wyliczyć wykryte modele
  - Użyć `getApiKeyForModel` do wyboru modeli, dla których masz poświadczenia
  - Uruchomić krótkie completion dla każdego modelu (oraz ukierunkowane regresje tam, gdzie trzeba)
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Ustaw `OPENCLAW_LIVE_MODELS=modern` (lub `all`, alias dla modern), aby faktycznie uruchomić ten pakiet; w przeciwnym razie zostanie pominięty, żeby `pnpm test:live` pozostawało skupione na smoke gateway
- Jak wybierać modele:
  - `OPENCLAW_LIVE_MODELS=modern`, aby uruchomić nowoczesną allowlistę (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` jest aliasem dla nowoczesnej allowlisty
  - albo `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlista rozdzielana przecinkami)
- Jak wybierać dostawców:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity"` (allowlista rozdzielana przecinkami)
- Skąd pochodzą klucze:
  - Domyślnie: magazyn profili i awaryjne odczyty z env
  - Ustaw `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić użycie **wyłącznie magazynu profili**
- Dlaczego to istnieje:
  - Oddziela „API dostawcy jest zepsute / klucz jest nieprawidłowy” od „pipeline agenta gateway jest zepsuty”
  - Zawiera małe, izolowane regresje (przykład: replay rozumowania OpenAI Responses/Codex Responses + przepływy wywołań narzędzi)

### Warstwa 2: Gateway + smoke agenta dev (co faktycznie robi „@openclaw”)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Cel:
  - Uruchomić gateway w procesie
  - Utworzyć/zmodyfikować sesję `agent:dev:*` (nadpisanie modelu dla danego uruchomienia)
  - Iterować po modelach z kluczami i potwierdzić:
    - „sensowną” odpowiedź (bez narzędzi)
    - działanie rzeczywistego wywołania narzędzia (read probe)
    - opcjonalne dodatkowe testy probe narzędzi (exec+read probe)
    - że ścieżki regresji OpenAI (samo wywołanie narzędzia → follow-up) nadal działają
- Szczegóły probe (aby łatwo wyjaśniać awarie):
  - probe `read`: test zapisuje plik nonce w workspace i prosi agenta o jego `read` oraz zwrócenie nonce.
  - probe `exec+read`: test prosi agenta o zapisanie nonce do pliku tymczasowego przez `exec`, a następnie o odczytanie go przez `read`.
  - probe obrazu: test dołącza wygenerowany PNG (kot + losowy kod) i oczekuje, że model zwróci `cat <CODE>`.
  - Referencja implementacyjna: `src/gateway/gateway-models.profiles.live.test.ts` oraz `src/gateway/live-image-probe.ts`.
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Jak wybierać modele:
  - Domyślnie: nowoczesna allowlista (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` jest aliasem dla nowoczesnej allowlisty
  - Albo ustaw `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (lub listę rozdzielaną przecinkami), aby zawęzić zakres
- Jak wybierać dostawców (unikając „wszystkiego z OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,openai,anthropic,zai,minimax"` (allowlista rozdzielana przecinkami)
- Probe narzędzi i obrazów są zawsze włączone w tym teście live:
  - probe `read` + `exec+read` probe (obciążenie narzędzi)
  - probe obrazu działa, gdy model deklaruje obsługę wejścia obrazowego
  - Przepływ (wysoki poziom):
    - Test generuje mały plik PNG z „CAT” + losowym kodem (`src/gateway/live-image-probe.ts`)
    - Wysyła go przez `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Gateway parsuje załączniki do `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Embedded agent przekazuje do modelu multimodalną wiadomość użytkownika
    - Asercja: odpowiedź zawiera `cat` + kod (tolerancja OCR: drobne błędy są dozwolone)

Wskazówka: aby zobaczyć, co możesz testować na swojej maszynie (i dokładne identyfikatory `provider/model`), uruchom:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke ACP bind (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Cel: zweryfikować rzeczywisty przepływ wiązania konwersacji ACP z aktywnym agentem ACP:
  - wyślij `/acp spawn <agent> --bind here`
  - przypnij syntetyczną konwersację kanału wiadomości w miejscu
  - wyślij normalny follow-up w tej samej konwersacji
  - sprawdź, czy follow-up trafia do transkryptu związanej sesji ACP
- Włączenie:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Domyślne ustawienia:
  - Agent ACP: `claude`
  - Syntetyczny kanał: kontekst rozmowy w stylu Slack DM
  - Backend ACP: `acpx`
- Nadpisania:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Uwagi:
  - Ta ścieżka używa powierzchni `chat.send` gateway z polami administracyjnymi tylko do testów dla syntetycznej trasy źródłowej, aby testy mogły dołączać kontekst kanału wiadomości bez udawania zewnętrznego dostarczenia.
  - Gdy `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` nie jest ustawione, test używa wbudowanego rejestru agentów pluginu `acpx` dla wybranego agenta harness ACP.

Przykład:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Recepta Docker:

```bash
pnpm test:docker:live-acp-bind
```

Uwagi dotyczące Dockera:

- Runner Dockera znajduje się w `scripts/test-live-acp-bind-docker.sh`.
- Źródłuje `~/.profile`, przygotowuje odpowiednie materiały auth CLI w kontenerze, instaluje `acpx` do zapisywalnego prefiksu npm, a następnie instaluje wymagane aktywne CLI (`@anthropic-ai/claude-code` lub `@openai/codex`), jeśli ich brakuje.
- Wewnątrz Dockera runner ustawia `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`, aby `acpx` zachowało zmienne env dostawcy z załadowanego profilu dostępne dla podrzędnego CLI harness.

### Zalecane recepty live

Wąskie, jawne allowlisty są najszybsze i najmniej podatne na niestabilność:

- Jeden model, bezpośrednio (bez gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Jeden model, smoke gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Wywoływanie narzędzi dla kilku dostawców:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Skupienie na Google (klucz API Gemini + Antigravity):
  - Gemini (klucz API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Uwagi:

- `google/...` używa API Gemini (klucz API).
- `google-antigravity/...` używa mostu OAuth Antigravity (punkt końcowy agenta w stylu Cloud Code Assist).

## Live: macierz modeli (co obejmujemy)

Nie ma stałej „listy modeli CI” (live jest opt-in), ale poniżej znajdują się **zalecane** modele do regularnego testowania na maszynie deweloperskiej z kluczami.

### Nowoczesny zestaw smoke (wywoływanie narzędzi + obraz)

To jest uruchomienie „typowych modeli”, które oczekujemy, że będzie działać:

- OpenAI (bez Codex): `openai/gpt-5.4` (opcjonalnie: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` i `google/gemini-3-flash-preview` (unikaj starszych modeli Gemini 2.x)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` i `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Uruchom smoke gateway z narzędziami + obrazem:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Bazowy zestaw: wywoływanie narzędzi (Read + opcjonalny Exec)

Wybierz co najmniej jeden model z każdej rodziny dostawców:

- OpenAI: `openai/gpt-5.4` (lub `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (lub `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Opcjonalne dodatkowe pokrycie (warto mieć):

- xAI: `xai/grok-4` (lub najnowszy dostępny)
- Mistral: `mistral/`… (wybierz model z włączoną obsługą narzędzi)
- Cerebras: `cerebras/`… (jeśli masz dostęp)
- LM Studio: `lmstudio/`… (lokalnie; wywoływanie narzędzi zależy od trybu API)

### Vision: wysyłanie obrazu (załącznik → wiadomość multimodalna)

Uwzględnij co najmniej jeden model obsługujący obrazy w `OPENCLAW_LIVE_GATEWAY_MODELS` (Claude/Gemini/warianty OpenAI z obsługą vision itd.), aby przetestować probe obrazu.

### Agregatory / alternatywne gateway

Jeśli masz włączone klucze, wspieramy też testowanie przez:

- OpenRouter: `openrouter/...` (setki modeli; użyj `openclaw models scan`, aby znaleźć kandydatów z obsługą narzędzi i obrazów)
- OpenCode: `opencode/...` dla Zen oraz `opencode-go/...` dla Go (auth przez `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Więcej dostawców, których możesz uwzględnić w macierzy live (jeśli masz poświadczenia/konfigurację):

- Wbudowani: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Przez `models.providers` (własne endpointy): `minimax` (cloud/API) oraz dowolny proxy zgodny z OpenAI/Anthropic (LM Studio, vLLM, LiteLLM itd.)

Wskazówka: nie próbuj na sztywno wpisywać w dokumentacji „wszystkich modeli”. Autorytatywna lista to to, co zwraca `discoverModels(...)` na Twojej maszynie + jakie klucze są dostępne.

## Poświadczenia (nigdy nie commituj)

Testy live wykrywają poświadczenia tak samo jak CLI. Praktyczne konsekwencje:

- Jeśli CLI działa, testy live powinny znaleźć te same klucze.
- Jeśli test live zgłasza „brak poświadczeń”, debuguj to tak samo, jak debugowałbyś `openclaw models list` / wybór modelu.

- Profile auth per-agent: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (to właśnie oznaczają „klucze profili” w testach live)
- Konfiguracja: `~/.openclaw/openclaw.json` (lub `OPENCLAW_CONFIG_PATH`)
- Starszy katalog stanu: `~/.openclaw/credentials/` (kopiowany do przygotowanego katalogu domowego live, jeśli istnieje, ale nie jest głównym magazynem kluczy profili)
- Lokalne uruchomienia live domyślnie kopiują aktywną konfigurację, pliki `auth-profiles.json` per-agent, starsze `credentials/` oraz obsługiwane katalogi auth zewnętrznych CLI do tymczasowego katalogu domowego testów; nadpisania ścieżek `agents.*.workspace` / `agentDir` są usuwane z tej przygotowanej konfiguracji, aby probe nie działały w Twoim rzeczywistym workspace hosta.

Jeśli chcesz polegać na kluczach z env (np. wyeksportowanych w `~/.profile`), uruchamiaj testy lokalne po `source ~/.profile` albo użyj runnerów Dockera opisanych poniżej (mogą montować `~/.profile` do kontenera).

## Live Deepgram (transkrypcja audio)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Włączenie: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live BytePlus coding plan

- Test: `src/agents/byteplus.live.test.ts`
- Włączenie: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Opcjonalne nadpisanie modelu: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live mediów dla workflow ComfyUI

- Test: `extensions/comfy/comfy.live.test.ts`
- Włączenie: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Zakres:
  - Testuje ścieżki wbudowanego comfy dla obrazu, wideo i `music_generate`
  - Pomija każdą zdolność, jeśli `models.providers.comfy.<capability>` nie jest skonfigurowane
  - Przydatne po zmianach w przesyłaniu workflow comfy, polling, pobieraniu lub rejestracji pluginu

## Live generowanie obrazów

- Test: `src/image-generation/runtime.live.test.ts`
- Polecenie: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Zakres:
  - Wylicza każdy zarejestrowany plugin dostawcy generowania obrazów
  - Ładuje brakujące zmienne env dostawców z powłoki logowania (`~/.profile`) przed testami probe
  - Domyślnie używa aktywnych kluczy live/env przed zapisanymi profilami auth, aby nieaktualne klucze testowe w `auth-profiles.json` nie maskowały rzeczywistych poświadczeń z powłoki
  - Pomija dostawców bez użytecznego auth/profilu/modelu
  - Uruchamia standardowe warianty generowania obrazów przez współdzieloną zdolność runtime:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Obecnie objęci wbudowani dostawcy:
  - `openai`
  - `google`
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Opcjonalne zachowanie auth:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić auth z magazynu profili i ignorować nadpisania tylko z env

## Live generowanie muzyki

- Test: `extensions/music-generation-providers.live.test.ts`
- Włączenie: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Zakres:
  - Testuje współdzieloną ścieżkę wbudowanych dostawców generowania muzyki
  - Obecnie obejmuje Google i MiniMax
  - Ładuje zmienne env dostawców z powłoki logowania (`~/.profile`) przed testami probe
  - Pomija dostawców bez użytecznego auth/profilu/modelu
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`

## Runnery Dockera (opcjonalne testy „działa w Linuksie”)

Te runnery Dockera dzielą się na dwie grupy:

- Runnery modeli live: `test:docker:live-models` i `test:docker:live-gateway` uruchamiają tylko odpowiadający im plik live z kluczami profili wewnątrz obrazu Dockera repozytorium (`src/agents/models.profiles.live.test.ts` i `src/gateway/gateway-models.profiles.live.test.ts`), montując lokalny katalog konfiguracji i workspace (oraz źródłując `~/.profile`, jeśli jest zamontowane). Odpowiadające lokalne entrypointy to `test:live:models-profiles` i `test:live:gateway-profiles`.
- Runnery live w Dockerze domyślnie mają mniejszy limit smoke, aby pełny przebieg w Dockerze pozostawał praktyczny:
  `test:docker:live-models` domyślnie ustawia `OPENCLAW_LIVE_MAX_MODELS=12`, a
  `test:docker:live-gateway` domyślnie ustawia `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` oraz
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Nadpisz te zmienne env, gdy
  świadomie chcesz wykonać większy, wyczerpujący skan.
- `test:docker:all` buduje obraz Dockera live jeden raz przez `test:docker:live-build`, a następnie ponownie używa go dla dwóch ścieżek live Docker.
- Runnery smoke dla kontenerów: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` i `test:docker:plugins` uruchamiają jeden lub więcej rzeczywistych kontenerów i weryfikują ścieżki integracyjne wyższego poziomu.

Runnery modeli live w Dockerze montują też tylko potrzebne katalogi domowe auth CLI (lub wszystkie obsługiwane, gdy uruchomienie nie jest zawężone), a następnie kopiują je do katalogu domowego kontenera przed uruchomieniem, aby zewnętrzne OAuth CLI mogło odświeżać tokeny bez modyfikowania magazynu auth hosta:

- Modele bezpośrednie: `pnpm test:docker:live-models` (skrypt: `scripts/test-live-models-docker.sh`)
- Smoke ACP bind: `pnpm test:docker:live-acp-bind` (skrypt: `scripts/test-live-acp-bind-docker.sh`)
- Gateway + agent dev: `pnpm test:docker:live-gateway` (skrypt: `scripts/test-live-gateway-models-docker.sh`)
- Open WebUI live smoke: `pnpm test:docker:openwebui` (skrypt: `scripts/e2e/openwebui-docker.sh`)
- Kreator onboardingu (TTY, pełne scaffoldowanie): `pnpm test:docker:onboard` (skrypt: `scripts/e2e/onboard-docker.sh`)
- Sieć gateway (dwa kontenery, auth WS + health): `pnpm test:docker:gateway-network` (skrypt: `scripts/e2e/gateway-network-docker.sh`)
- Most kanałów MCP (zasiany Gateway + most stdio + smoke surowych ramek powiadomień Claude): `pnpm test:docker:mcp-channels` (skrypt: `scripts/e2e/mcp-channels-docker.sh`)
- Pluginy (smoke instalacji + alias `/plugin` + semantyka restartu paczki Claude): `pnpm test:docker:plugins` (skrypt: `scripts/e2e/plugins-docker.sh`)

Runnery modeli live w Dockerze montują też bieżący checkout tylko do odczytu i
przygotowują go w tymczasowym katalogu roboczym wewnątrz kontenera. Dzięki temu obraz runtime
pozostaje lekki, a Vitest nadal działa na dokładnie Twoim lokalnym źródle/konfiguracji.
Etap przygotowania pomija duże lokalne cache i wyniki budowania aplikacji, takie jak
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` oraz lokalne katalogi `.build`
lub wyjścia Gradle, aby uruchomienia live w Dockerze nie traciły minut na kopiowanie
artefaktów specyficznych dla maszyny.
Ustawiają też `OPENCLAW_SKIP_CHANNELS=1`, aby testy live gateway nie uruchamiały
rzeczywistych workerów kanałów Telegram/Discord itd. wewnątrz kontenera.
`test:docker:live-models` nadal uruchamia `pnpm test:live`, więc przekazuj także
`OPENCLAW_LIVE_GATEWAY_*`, gdy chcesz zawęzić lub wykluczyć pokrycie gateway
w tej ścieżce Docker.
`test:docker:openwebui` to smoke zgodności wyższego poziomu: uruchamia
kontener gateway OpenClaw z włączonymi endpointami HTTP zgodnymi z OpenAI,
uruchamia przypięty kontener Open WebUI podłączony do tego gateway, loguje się przez
Open WebUI, sprawdza, że `/api/models` udostępnia `openclaw/default`, a następnie wysyła
rzeczywiste żądanie czatu przez proxy `/api/chat/completions` Open WebUI.
Pierwsze uruchomienie może być zauważalnie wolniejsze, ponieważ Docker może potrzebować pobrać
obraz Open WebUI, a samo Open WebUI może potrzebować ukończyć własną konfigurację zimnego startu.
Ta ścieżka oczekuje działającego klucza modelu live, a `OPENCLAW_PROFILE_FILE`
(domyslnie `~/.profile`) jest podstawowym sposobem dostarczenia go w uruchomieniach z Dockerem.
Udane przebiegi wypisują mały ładunek JSON, taki jak `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` jest celowo deterministyczny i nie wymaga
prawdziwego konta Telegram, Discord ani iMessage. Uruchamia zasiany kontener Gateway,
startuje drugi kontener, który uruchamia `openclaw mcp serve`, a następnie
weryfikuje wykrywanie routowanych konwersacji, odczyty transkryptów, metadane załączników,
zachowanie kolejki zdarzeń live, routing wysyłek wychodzących oraz powiadomienia kanału +
uprawnień w stylu Claude przez rzeczywisty most stdio MCP. Kontrola powiadomień
sprawdza bezpośrednio surowe ramki stdio MCP, tak aby smoke weryfikował to, co most
naprawdę emituje, a nie tylko to, co akurat udostępnia konkretne SDK klienta.

Ręczny smoke ACP plain-language thread (nie CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Zachowaj ten skrypt do przepływów regresji/debugowania. Może znów być potrzebny do walidacji routingu wątków ACP, więc go nie usuwaj.

Przydatne zmienne env:

- `OPENCLAW_CONFIG_DIR=...` (domyślnie: `~/.openclaw`) montowane do `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (domyślnie: `~/.openclaw/workspace`) montowane do `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (domyślnie: `~/.profile`) montowane do `/home/node/.profile` i źródłowane przed uruchomieniem testów
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (domyślnie: `~/.cache/openclaw/docker-cli-tools`) montowane do `/home/node/.npm-global` dla cache instalacji CLI w Dockerze
- Zewnętrzne katalogi/pliki auth CLI w `$HOME` są montowane tylko do odczytu pod `/host-auth...`, a następnie kopiowane do `/home/node/...` przed rozpoczęciem testów
  - Domyślne katalogi: `.minimax`
  - Domyślne pliki: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Zawężone uruchomienia dostawców montują tylko potrzebne katalogi/pliki wywnioskowane z `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Nadpisanie ręczne przez `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` lub listę rozdzielaną przecinkami, np. `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`, aby zawęzić uruchomienie
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`, aby filtrować dostawców wewnątrz kontenera
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby upewnić się, że poświadczenia pochodzą z magazynu profili (a nie z env)
- `OPENCLAW_OPENWEBUI_MODEL=...`, aby wybrać model udostępniany przez gateway dla smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...`, aby nadpisać prompt kontroli nonce używany przez smoke Open WebUI
- `OPENWEBUI_IMAGE=...`, aby nadpisać przypięty tag obrazu Open WebUI

## Kontrola dokumentacji

Uruchamiaj kontrole dokumentacji po edycjach dokumentów: `pnpm check:docs`.
Uruchamiaj pełną walidację anchorów Mintlify, gdy potrzebujesz także kontroli nagłówków w obrębie strony: `pnpm docs:check-links:anchors`.

## Regresje offline (bezpieczne dla CI)

To są regresje „rzeczywistego pipeline” bez prawdziwych dostawców:

- Wywoływanie narzędzi gateway (mock OpenAI, rzeczywista pętla gateway + agent): `src/gateway/gateway.test.ts` (przypadek: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Kreator gateway (WS `wizard.start`/`wizard.next`, wymuszone zapisy config + auth): `src/gateway/gateway.test.ts` (przypadek: "runs wizard over ws and writes auth token config")

## Evalue niezawodności agenta (Skills)

Mamy już kilka testów bezpiecznych dla CI, które zachowują się jak „ewaluacje niezawodności agenta”:

- Mockowane wywoływanie narzędzi przez rzeczywistą pętlę gateway + agent (`src/gateway/gateway.test.ts`).
- Przepływy kreatora end-to-end, które weryfikują okablowanie sesji i skutki konfiguracji (`src/gateway/gateway.test.ts`).

Czego nadal brakuje dla Skills (zobacz [Skills](/pl/tools/skills)):

- **Podejmowanie decyzji:** gdy Skills są wymienione w prompcie, czy agent wybiera właściwe Skill (lub unika nieistotnych)?
- **Zgodność:** czy agent czyta `SKILL.md` przed użyciem i stosuje wymagane kroki/argumenty?
- **Kontrakty przepływu pracy:** scenariusze wieloturowe, które potwierdzają kolejność narzędzi, przenoszenie historii sesji i granice sandboxa.

Przyszłe ewaluacje powinny przede wszystkim pozostać deterministyczne:

- Runner scenariuszy używający mockowanych dostawców do potwierdzania wywołań narzędzi + kolejności, odczytów plików Skill i okablowania sesji.
- Mały pakiet scenariuszy skoncentrowanych na Skills (użycie vs unikanie, bramkowanie, prompt injection).
- Opcjonalne ewaluacje live (opt-in, sterowane env) dopiero po wdrożeniu pakietu bezpiecznego dla CI.

## Testy kontraktowe (kształt pluginów i kanałów)

Testy kontraktowe weryfikują, że każdy zarejestrowany plugin i kanał jest zgodny ze swoim
kontraktem interfejsu. Iterują po wszystkich wykrytych pluginach i uruchamiają zestaw
asercji kształtu i zachowania. Domyślna ścieżka unit `pnpm test` celowo
pomija te współdzielone pliki seam i smoke; uruchamiaj polecenia kontraktowe jawnie,
gdy dotykasz współdzielonych powierzchni kanałów lub dostawców.

### Polecenia

- Wszystkie kontrakty: `pnpm test:contracts`
- Tylko kontrakty kanałów: `pnpm test:contracts:channels`
- Tylko kontrakty dostawców: `pnpm test:contracts:plugins`

### Kontrakty kanałów

Znajdują się w `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Podstawowy kształt pluginu (id, nazwa, capabilities)
- **setup** - Kontrakt kreatora konfiguracji
- **session-binding** - Zachowanie wiązania sesji
- **outbound-payload** - Struktura ładunku wiadomości
- **inbound** - Obsługa wiadomości przychodzących
- **actions** - Handlery akcji kanału
- **threading** - Obsługa identyfikatorów wątków
- **directory** - API katalogu/listy
- **group-policy** - Egzekwowanie zasad grup

### Kontrakty statusu dostawcy

Znajdują się w `src/plugins/contracts/*.contract.test.ts`.

- **status** - Testy probe statusu kanałów
- **registry** - Kształt rejestru pluginów

### Kontrakty dostawców

Znajdują się w `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Kontrakt przepływu auth
- **auth-choice** - Wybór/selekcja auth
- **catalog** - API katalogu modeli
- **discovery** - Wykrywanie pluginów
- **loader** - Ładowanie pluginów
- **runtime** - Runtime dostawcy
- **shape** - Kształt/interfejs pluginu
- **wizard** - Kreator konfiguracji

### Kiedy uruchamiać

- Po zmianie eksportów lub subścieżek plugin-sdk
- Po dodaniu lub modyfikacji kanału albo pluginu dostawcy
- Po refaktoryzacji rejestracji pluginów lub wykrywania

Testy kontraktowe działają w CI i nie wymagają prawdziwych kluczy API.

## Dodawanie regresji (wskazówki)

Gdy naprawiasz problem dostawcy/modelu wykryty w live:

- Dodaj regresję bezpieczną dla CI, jeśli to możliwe (mock/stub dostawcy albo przechwycenie dokładnej transformacji kształtu żądania)
- Jeśli z natury da się to przetestować tylko live (limity, zasady auth), utrzymuj test live wąski i opt-in przez zmienne env
- Celuj w najmniejszą warstwę, która wykrywa błąd:
  - błąd konwersji/replay żądania dostawcy → test modeli bezpośrednich
  - błąd pipeline sesji/historii/narzędzi gateway → smoke gateway live albo bezpieczny dla CI test mock gateway
- Poręcz przy przechodzeniu SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` wyprowadza jeden przykładowy cel na klasę SecretRef z metadanych rejestru (`listSecretTargetRegistryEntries()`), a następnie potwierdza, że identyfikatory `exec` dla segmentów przejścia są odrzucane.
  - Jeśli dodasz nową rodzinę celów SecretRef z `includeInPlan` w `src/secrets/target-registry-data.ts`, zaktualizuj `classifyTargetClass` w tym teście. Test celowo kończy się niepowodzeniem dla niesklasyfikowanych identyfikatorów celów, aby nowych klas nie dało się pominąć po cichu.
