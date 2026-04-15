---
read_when:
    - Uruchamianie testów lokalnie lub w CI
    - Dodawanie testów regresji dla błędów modeli/dostawców
    - Debugowanie zachowania Gateway i agenta
summary: 'Zestaw testowy: pakiety testów unit/e2e/live, uruchamianie w Dockerze i to, co obejmuje każdy test'
title: Testowanie
x-i18n:
    generated_at: "2026-04-15T14:40:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: ec3632cafa1f38b27510372391b84af744266df96c58f7fac98aa03763465db8
    source_path: help/testing.md
    workflow: 15
---

# Testowanie

OpenClaw ma trzy pakiety testów Vitest (unit/integration, e2e, live) oraz niewielki zestaw uruchomień w Dockerze.

Ten dokument to przewodnik „jak testujemy”:

- Co obejmuje każdy pakiet testów (i czego celowo _nie_ obejmuje)
- Jakie polecenia uruchamiać w typowych przepływach pracy (lokalnie, przed push, debugowanie)
- Jak testy live wykrywają poświadczenia oraz wybierają modele/dostawców
- Jak dodawać testy regresji dla rzeczywistych problemów z modelami/dostawcami

## Szybki start

W większości dni:

- Pełna bramka (oczekiwana przed push): `pnpm build && pnpm check && pnpm test`
- Szybsze lokalne uruchomienie pełnego pakietu na wydajnej maszynie: `pnpm test:max`
- Bezpośrednia pętla obserwacji Vitest: `pnpm test:watch`
- Bezpośrednie wskazywanie pliku obsługuje teraz także ścieżki rozszerzeń/kanałów: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Gdy iterujesz nad pojedynczym błędem, najpierw wybieraj uruchomienia ukierunkowane.
- Witryna QA oparta na Dockerze: `pnpm qa:lab:up`
- Ścieżka QA oparta na Linux VM: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Gdy modyfikujesz testy lub chcesz mieć większą pewność:

- Bramka pokrycia: `pnpm test:coverage`
- Pakiet E2E: `pnpm test:e2e`

Podczas debugowania rzeczywistych dostawców/modeli (wymaga prawdziwych poświadczeń):

- Pakiet live (modele + sondy narzędzi/obrazów Gateway): `pnpm test:live`
- Ciche uruchomienie pojedynczego pliku live: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Wskazówka: jeśli potrzebujesz tylko jednego nieudanego przypadku, zawężaj testy live za pomocą zmiennych środowiskowych allowlist opisanych poniżej.

## Uruchomienia specyficzne dla QA

Te polecenia działają obok głównych pakietów testów, gdy potrzebujesz realizmu qa-lab:

- `pnpm openclaw qa suite`
  - Uruchamia scenariusze QA oparte na repozytorium bezpośrednio na hoście.
  - Domyślnie uruchamia równolegle wiele wybranych scenariuszy z izolowanymi workerami Gateway, do 64 workerów lub liczby wybranych scenariuszy. Użyj `--concurrency <count>`, aby dostroić liczbę workerów, albo `--concurrency 1` dla starszej ścieżki sekwencyjnej.
- `pnpm openclaw qa suite --runner multipass`
  - Uruchamia ten sam pakiet QA wewnątrz tymczasowej maszyny wirtualnej Multipass Linux.
  - Zachowuje ten sam sposób wyboru scenariuszy co `qa suite` na hoście.
  - Używa tych samych flag wyboru dostawcy/modelu co `qa suite`.
  - Uruchomienia live przekazują do gościa obsługiwane wejścia uwierzytelniania QA, które są praktyczne: klucze dostawców oparte na env, ścieżkę konfiguracji dostawcy QA live oraz `CODEX_HOME`, jeśli jest obecne.
  - Katalogi wyjściowe muszą pozostawać pod katalogiem głównym repozytorium, aby gość mógł zapisywać wyniki przez zamontowany workspace.
  - Zapisuje standardowy raport i podsumowanie QA oraz logi Multipass w `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - Uruchamia witrynę QA opartą na Dockerze do pracy QA w stylu operatorskim.
- `pnpm openclaw qa matrix`
  - Uruchamia ścieżkę live QA dla Matrix względem tymczasowego homeservera Tuwunel opartego na Dockerze.
  - Ten host QA jest obecnie przeznaczony tylko do repo/dev. Spakowane instalacje OpenClaw nie zawierają `qa-lab`, więc nie udostępniają `openclaw qa`.
  - Kopie robocze repozytorium ładują dołączony runner bezpośrednio; nie jest potrzebny osobny krok instalacji Plugin.
  - Tworzy trzech tymczasowych użytkowników Matrix (`driver`, `sut`, `observer`) oraz jeden prywatny pokój, a następnie uruchamia podrzędny proces Gateway QA z rzeczywistym Plugin Matrix jako transportem SUT.
  - Domyślnie używa przypiętego stabilnego obrazu Tuwunel `ghcr.io/matrix-construct/tuwunel:v1.5.1`. Nadpisz przez `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE`, gdy chcesz przetestować inny obraz.
  - Matrix nie udostępnia współdzielonych flag źródła poświadczeń, ponieważ ta ścieżka tworzy tymczasowych użytkowników lokalnie.
  - Zapisuje raport QA Matrix, podsumowanie i artefakt observed-events w `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - Uruchamia ścieżkę live QA dla Telegram względem rzeczywistej prywatnej grupy, używając tokenów bota driver i SUT z env.
  - Wymaga `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` oraz `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. Identyfikator grupy musi być numerycznym identyfikatorem czatu Telegram.
  - Obsługuje `--credential-source convex` dla współdzielonych poświadczeń z puli. Domyślnie używaj trybu env albo ustaw `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`, aby włączyć dzierżawy z puli.
  - Wymaga dwóch różnych botów w tej samej prywatnej grupie, przy czym bot SUT musi udostępniać nazwę użytkownika Telegram.
  - Aby zapewnić stabilną obserwację ruchu bot-do-bota, włącz Bot-to-Bot Communication Mode w `@BotFather` dla obu botów i upewnij się, że bot driver może obserwować ruch botów w grupie.
  - Zapisuje raport QA Telegram, podsumowanie i artefakt observed-messages w `.artifacts/qa-e2e/...`.

Ścieżki live transportów współdzielą jeden standardowy kontrakt, aby nowe transporty nie ulegały rozbieżnościom:

`qa-channel` pozostaje szerokim syntetycznym pakietem QA i nie jest częścią macierzy pokrycia live transportów.

| Ścieżka  | Canary | Bramka mention | Blokada allowlist | Odpowiedź najwyższego poziomu | Wznowienie po restarcie | Kontynuacja wątku | Izolacja wątku | Obserwacja reakcji | Polecenie help |
| -------- | ------ | --------------- | ----------------- | ----------------------------- | ----------------------- | ----------------- | -------------- | ------------------ | -------------- |
| Matrix   | x      | x               | x                 | x                             | x                       | x                 | x              | x                  |                |
| Telegram | x      |                 |                   |                               |                         |                   |                |                    | x              |

### Współdzielone poświadczenia Telegram przez Convex (v1)

Gdy `--credential-source convex` (lub `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`) jest włączone dla
`openclaw qa telegram`, QA lab pobiera wyłączną dzierżawę z puli opartej na Convex, wysyła Heartbeat
tej dzierżawy podczas działania ścieżki i zwalnia dzierżawę przy zamknięciu.

Referencyjny szkielet projektu Convex:

- `qa/convex-credential-broker/`

Wymagane zmienne środowiskowe:

- `OPENCLAW_QA_CONVEX_SITE_URL` (na przykład `https://your-deployment.convex.site`)
- Jeden sekret dla wybranej roli:
  - `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` dla `maintainer`
  - `OPENCLAW_QA_CONVEX_SECRET_CI` dla `ci`
- Wybór roli poświadczeń:
  - CLI: `--credential-role maintainer|ci`
  - Domyślna wartość env: `OPENCLAW_QA_CREDENTIAL_ROLE` (domyślnie `maintainer`)

Opcjonalne zmienne środowiskowe:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS` (domyślnie `1200000`)
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS` (domyślnie `30000`)
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS` (domyślnie `90000`)
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS` (domyślnie `15000`)
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX` (domyślnie `/qa-credentials/v1`)
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID` (opcjonalny identyfikator śledzenia)
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` pozwala na adresy URL Convex `http://` w local loopback tylko do lokalnego rozwoju.

`OPENCLAW_QA_CONVEX_SITE_URL` powinien używać `https://` w normalnym działaniu.

Polecenia administracyjne maintainera (dodawanie/usuwanie/listowanie puli) wymagają
konkretnie `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER`.

Pomocnicze polecenia CLI dla maintainerów:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

Użyj `--json`, aby uzyskać wynik czytelny maszynowo w skryptach i narzędziach CI.

Domyślny kontrakt endpointu (`OPENCLAW_QA_CONVEX_SITE_URL` + `/qa-credentials/v1`):

- `POST /acquire`
  - Żądanie: `{ kind, ownerId, actorRole, leaseTtlMs, heartbeatIntervalMs }`
  - Sukces: `{ status: "ok", credentialId, leaseToken, payload, leaseTtlMs?, heartbeatIntervalMs? }`
  - Wyczerpana pula / możliwość ponowienia: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
- `POST /heartbeat`
  - Żądanie: `{ kind, ownerId, actorRole, credentialId, leaseToken, leaseTtlMs }`
  - Sukces: `{ status: "ok" }` (lub puste `2xx`)
- `POST /release`
  - Żądanie: `{ kind, ownerId, actorRole, credentialId, leaseToken }`
  - Sukces: `{ status: "ok" }` (lub puste `2xx`)
- `POST /admin/add` (tylko sekret maintainera)
  - Żądanie: `{ kind, actorId, payload, note?, status? }`
  - Sukces: `{ status: "ok", credential }`
- `POST /admin/remove` (tylko sekret maintainera)
  - Żądanie: `{ credentialId, actorId }`
  - Sukces: `{ status: "ok", changed, credential }`
  - Ochrona aktywnej dzierżawy: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list` (tylko sekret maintainera)
  - Żądanie: `{ kind?, status?, includePayload?, limit? }`
  - Sukces: `{ status: "ok", credentials, count }`

Kształt ładunku dla rodzaju Telegram:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` musi być numerycznym ciągiem identyfikatora czatu Telegram.
- `admin/add` waliduje ten kształt dla `kind: "telegram"` i odrzuca nieprawidłowy ładunek.

### Dodawanie kanału do QA

Dodanie kanału do systemu QA opartego na Markdown wymaga dokładnie dwóch rzeczy:

1. Adaptera transportu dla kanału.
2. Zestawu scenariuszy sprawdzających kontrakt kanału.

Nie dodawaj nowego głównego korzenia poleceń QA, gdy współdzielony host `qa-lab` może
obsłużyć ten przepływ.

`qa-lab` zarządza współdzieloną mechaniką hosta:

- korzeniem poleceń `openclaw qa`
- uruchamianiem i zamykaniem pakietu
- współbieżnością workerów
- zapisem artefaktów
- generowaniem raportów
- wykonywaniem scenariuszy
- aliasami zgodności dla starszych scenariuszy `qa-channel`

Pluginy runnerów zarządzają kontraktem transportu:

- jak `openclaw qa <runner>` jest montowane pod współdzielonym korzeniem `qa`
- jak Gateway jest konfigurowany dla tego transportu
- jak sprawdzana jest gotowość
- jak wstrzykiwane są zdarzenia przychodzące
- jak obserwowane są wiadomości wychodzące
- jak udostępniane są transkrypty i znormalizowany stan transportu
- jak wykonywane są działania oparte na transporcie
- jak obsługiwany jest reset lub czyszczenie specyficzne dla transportu

Minimalny próg wdrożenia dla nowego kanału to:

1. Zachowaj `qa-lab` jako właściciela współdzielonego korzenia `qa`.
2. Zaimplementuj runner transportu na współdzielonym interfejsie hosta `qa-lab`.
3. Zachowaj mechanikę specyficzną dla transportu w runnerze Plugin lub harnessie Plugin.
4. Montuj runner jako `openclaw qa <runner>`, zamiast rejestrować konkurencyjny korzeń poleceń.
   Pluginy runnerów powinny deklarować `qaRunners` w `openclaw.plugin.json` i eksportować pasującą tablicę `qaRunnerCliRegistrations` z `runtime-api.ts`.
   Zachowaj `runtime-api.ts` w lekkiej formie; leniwe wykonywanie CLI i runnera powinno pozostawać za osobnymi punktami wejścia.
5. Twórz lub dostosowuj scenariusze Markdown w `qa/scenarios/`.
6. Dla nowych scenariuszy używaj ogólnych helperów scenariuszy.
7. Zachowaj działanie istniejących aliasów zgodności, chyba że repozytorium przeprowadza celową migrację.

Reguła decyzyjna jest ścisła:

- Jeśli zachowanie można wyrazić raz w `qa-lab`, umieść je w `qa-lab`.
- Jeśli zachowanie zależy od jednego transportu kanału, zachowaj je w runnerze Plugin lub harnessie tego Plugin.
- Jeśli scenariusz potrzebuje nowej możliwości, z której może skorzystać więcej niż jeden kanał, dodaj ogólny helper zamiast gałęzi specyficznej dla kanału w `suite.ts`.
- Jeśli zachowanie ma znaczenie tylko dla jednego transportu, zachowaj scenariusz jako specyficzny dla transportu i wyraź to jasno w kontrakcie scenariusza.

Preferowane nazwy ogólnych helperów dla nowych scenariuszy:

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

Aliasów zgodności nadal można używać w istniejących scenariuszach, w tym:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

Nowe prace nad kanałami powinny używać ogólnych nazw helperów.
Aliasy zgodności istnieją po to, aby uniknąć migracji typu flag day, a nie jako wzorzec
dla tworzenia nowych scenariuszy.

## Pakiety testów (co jest uruchamiane gdzie)

Traktuj pakiety testów jako „rosnący realizm” (i rosnącą niestabilność/koszt):

### Unit / integration (domyślne)

- Polecenie: `pnpm test`
- Konfiguracja: dziesięć sekwencyjnych shardów (`vitest.full-*.config.ts`) uruchamianych na istniejących zakresowanych projektach Vitest
- Pliki: inwentarze core/unit w `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` oraz dozwolone testy `ui` dla Node objęte przez `vitest.unit.config.ts`
- Zakres:
  - Czyste testy unit
  - Testy integracyjne w procesie (uwierzytelnianie Gateway, routing, narzędzia, parsowanie, konfiguracja)
  - Deterministyczne testy regresji dla znanych błędów
- Oczekiwania:
  - Uruchamiane w CI
  - Nie wymagają prawdziwych kluczy
  - Powinny być szybkie i stabilne
- Uwaga o projektach:
  - Niezakresowane `pnpm test` uruchamia teraz jedenaście mniejszych konfiguracji shardów (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) zamiast jednego ogromnego natywnego procesu projektu root. Zmniejsza to szczytowe RSS na obciążonych maszynach i zapobiega temu, by prace `auto-reply`/rozszerzeń zagłodziły niezwiązane pakiety.
  - `pnpm test --watch` nadal używa natywnego grafu projektów root `vitest.config.ts`, ponieważ pętla watch z wieloma shardami nie jest praktyczna.
  - `pnpm test`, `pnpm test:watch` i `pnpm test:perf:imports` kierują jawne cele plików/katalogów najpierw przez zakresowane ścieżki, więc `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` unika kosztu uruchamiania pełnego projektu root.
  - `pnpm test:changed` rozwija zmienione ścieżki git do tych samych zakresowanych ścieżek, gdy diff dotyka tylko routowalnych plików źródłowych/testowych; edycje konfiguracji/setup nadal wracają do szerokiego ponownego uruchomienia projektu root.
  - Lekkie importowo testy unit z agents, commands, plugins, helperów `auto-reply`, `plugin-sdk` i podobnych czysto użytkowych obszarów są kierowane przez ścieżkę `unit-fast`, która pomija `test/setup-openclaw-runtime.ts`; pliki stanowe/ciężkie runtime pozostają na istniejących ścieżkach.
  - Wybrane pliki źródłowe helperów `plugin-sdk` i `commands` mapują także uruchomienia w trybie changed na jawne testy sąsiednie w tych lekkich ścieżkach, dzięki czemu edycje helperów nie wymagają ponownego uruchamiania pełnego ciężkiego pakietu dla tego katalogu.
  - `auto-reply` ma teraz trzy dedykowane koszyki: helpery core najwyższego poziomu, testy integracyjne `reply.*` najwyższego poziomu oraz poddrzewo `src/auto-reply/reply/**`. Dzięki temu najcięższa praca harnessu reply nie trafia do tanich testów status/chunk/token.
- Uwaga o embedded runner:
  - Gdy zmieniasz wejścia wykrywania message-tool lub kontekst runtime Compaction,
    zachowaj oba poziomy pokrycia.
  - Dodaj ukierunkowane testy regresji helperów dla czystych granic routingu/normalizacji.
  - Utrzymuj też w dobrej kondycji pakiety integracyjne embedded runner:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` oraz
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Te pakiety weryfikują, że zakresowane identyfikatory i zachowanie Compaction nadal przepływają
    przez rzeczywiste ścieżki `run.ts` / `compact.ts`; same testy helperów nie są
    wystarczającym zamiennikiem dla tych ścieżek integracyjnych.
- Uwaga o puli:
  - Bazowa konfiguracja Vitest domyślnie używa teraz `threads`.
  - Współdzielona konfiguracja Vitest ustawia też na stałe `isolate: false` i używa nieizolowanego runnera w projektach root, konfiguracjach e2e i live.
  - Ścieżka UI root zachowuje konfigurację `jsdom` i optimizer, ale teraz działa również na współdzielonym nieizolowanym runnerze.
  - Każdy shard `pnpm test` dziedziczy te same domyślne wartości `threads` + `isolate: false` ze współdzielonej konfiguracji Vitest.
  - Współdzielony launcher `scripts/run-vitest.mjs` dodaje teraz domyślnie także `--no-maglev` dla podrzędnych procesów Node Vitest, aby ograniczyć churn kompilacji V8 podczas dużych lokalnych uruchomień. Ustaw `OPENCLAW_VITEST_ENABLE_MAGLEV=1`, jeśli chcesz porównać zachowanie ze standardowym V8.
- Uwaga o szybkiej lokalnej iteracji:
  - `pnpm test:changed` kieruje przez zakresowane ścieżki, gdy zmienione ścieżki da się czysto odwzorować na mniejszy pakiet.
  - `pnpm test:max` i `pnpm test:changed:max` zachowują ten sam sposób routingu, tylko z wyższym limitem workerów.
  - Lokalne automatyczne skalowanie workerów jest teraz celowo konserwatywne i wycofuje się także wtedy, gdy średnie obciążenie hosta jest już wysokie, więc wiele równoczesnych uruchomień Vitest domyślnie wyrządza mniej szkód.
  - Bazowa konfiguracja Vitest oznacza pliki projektów/konfiguracji jako `forceRerunTriggers`, aby ponowne uruchomienia w trybie changed pozostały poprawne, gdy zmienia się okablowanie testów.
  - Konfiguracja utrzymuje `OPENCLAW_VITEST_FS_MODULE_CACHE` włączone na obsługiwanych hostach; ustaw `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`, jeśli chcesz jedną jawną lokalizację cache do bezpośredniego profilowania.
- Uwaga o debugowaniu wydajności:
  - `pnpm test:perf:imports` włącza raportowanie czasu importu Vitest oraz wyjście z rozbiciem importów.
  - `pnpm test:perf:imports:changed` ogranicza ten sam widok profilowania do plików zmienionych od `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` porównuje routowane `test:changed` z natywną ścieżką projektu root dla tego zatwierdzonego diffu i wypisuje czas ścienny oraz maksymalne RSS na macOS.
- `pnpm test:perf:changed:bench -- --worktree` wykonuje benchmark bieżącego brudnego drzewa, kierując listę zmienionych plików przez `scripts/test-projects.mjs` i konfigurację root Vitest.
  - `pnpm test:perf:profile:main` zapisuje profil CPU głównego wątku dla narzutu uruchamiania i transformacji Vitest/Vite.
  - `pnpm test:perf:profile:runner` zapisuje profile CPU+heap runnera dla pakietu unit przy wyłączonej równoległości plików.

### E2E (testy smoke Gateway)

- Polecenie: `pnpm test:e2e`
- Konfiguracja: `vitest.e2e.config.ts`
- Pliki: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Domyślne ustawienia runtime:
  - Używa Vitest `threads` z `isolate: false`, zgodnie z resztą repozytorium.
  - Używa adaptacyjnej liczby workerów (CI: do 2, lokalnie: domyślnie 1).
  - Domyślnie działa w trybie cichym, aby zmniejszyć narzut I/O konsoli.
- Przydatne nadpisania:
  - `OPENCLAW_E2E_WORKERS=<n>`, aby wymusić liczbę workerów (limit 16).
  - `OPENCLAW_E2E_VERBOSE=1`, aby ponownie włączyć szczegółowe wyjście konsoli.
- Zakres:
  - Zachowanie end-to-end Gateway z wieloma instancjami
  - Powierzchnie WebSocket/HTTP, parowanie węzłów i cięższa komunikacja sieciowa
- Oczekiwania:
  - Uruchamiane w CI (gdy są włączone w pipeline)
  - Nie wymagają prawdziwych kluczy
  - Mają więcej ruchomych części niż testy unit (mogą być wolniejsze)

### E2E: test smoke backendu OpenShell

- Polecenie: `pnpm test:e2e:openshell`
- Plik: `test/openshell-sandbox.e2e.test.ts`
- Zakres:
  - Uruchamia izolowany Gateway OpenShell na hoście przez Docker
  - Tworzy sandbox z tymczasowego lokalnego Dockerfile
  - Testuje backend OpenShell w OpenClaw przez rzeczywiste `sandbox ssh-config` + wykonanie SSH
  - Weryfikuje zachowanie systemu plików remote-canonical przez most fs sandboxa
- Oczekiwania:
  - Tylko opt-in; nie jest częścią domyślnego uruchomienia `pnpm test:e2e`
  - Wymaga lokalnego CLI `openshell` oraz działającego demona Docker
  - Używa izolowanych `HOME` / `XDG_CONFIG_HOME`, a następnie niszczy testowy Gateway i sandbox
- Przydatne nadpisania:
  - `OPENCLAW_E2E_OPENSHELL=1`, aby włączyć test przy ręcznym uruchamianiu szerszego pakietu e2e
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`, aby wskazać niestandardowy plik binarny CLI lub skrypt wrappera

### Live (rzeczywiści dostawcy + rzeczywiste modele)

- Polecenie: `pnpm test:live`
- Konfiguracja: `vitest.live.config.ts`
- Pliki: `src/**/*.live.test.ts`
- Domyślnie: **włączone** przez `pnpm test:live` (ustawia `OPENCLAW_LIVE_TEST=1`)
- Zakres:
  - „Czy ten dostawca/model rzeczywiście działa _dzisiaj_ przy prawdziwych poświadczeniach?”
  - Wychwytuje zmiany formatu dostawcy, osobliwości wywoływania narzędzi, problemy z uwierzytelnianiem i zachowanie limitów szybkości
- Oczekiwania:
  - Celowo niestabilne w CI (rzeczywiste sieci, rzeczywiste polityki dostawców, limity, awarie)
  - Kosztują pieniądze / zużywają limity szybkości
  - Lepiej uruchamiać zawężone podzbiory niż „wszystko”
- Uruchomienia live pobierają `~/.profile`, aby znaleźć brakujące klucze API.
- Domyślnie uruchomienia live nadal izolują `HOME` i kopiują materiał konfiguracyjny/uwierzytelniający do tymczasowego katalogu domowego testów, tak aby fixture'y unit nie mogły zmieniać twojego prawdziwego `~/.openclaw`.
- Ustaw `OPENCLAW_LIVE_USE_REAL_HOME=1` tylko wtedy, gdy celowo chcesz, aby testy live używały twojego prawdziwego katalogu domowego.
- `pnpm test:live` domyślnie używa teraz cichszego trybu: zachowuje wyjście postępu `[live] ...`, ale ukrywa dodatkową informację o `~/.profile` i wycisza logi bootstrap Gateway / szum Bonjour. Ustaw `OPENCLAW_LIVE_TEST_QUIET=0`, jeśli chcesz przywrócić pełne logi startowe.
- Rotacja kluczy API (specyficzna dla dostawcy): ustaw `*_API_KEYS` w formacie rozdzielanym przecinkami/średnikami lub `*_API_KEY_1`, `*_API_KEY_2` (na przykład `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) albo nadpisanie per-live przez `OPENCLAW_LIVE_*_KEY`; testy ponawiają próbę przy odpowiedziach z limitem szybkości.
- Wyjście postępu/Heartbeat:
  - Pakiety live emitują teraz linie postępu do stderr, dzięki czemu długie wywołania dostawców są widocznie aktywne nawet wtedy, gdy przechwytywanie konsoli Vitest jest ciche.
  - `vitest.live.config.ts` wyłącza przechwytywanie konsoli Vitest, więc linie postępu dostawcy/Gateway są przesyłane natychmiast podczas uruchomień live.
  - Dostosuj Heartbeat bezpośrednich modeli przez `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Dostosuj Heartbeat Gateway/sond przez `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Który pakiet testów powinienem uruchomić?

Użyj tej tabeli decyzyjnej:

- Edytowanie logiki/testów: uruchom `pnpm test` (oraz `pnpm test:coverage`, jeśli zmieniłeś dużo)
- Modyfikacja komunikacji sieciowej Gateway / protokołu WS / parowania: dodaj `pnpm test:e2e`
- Debugowanie „mój bot nie działa” / awarii specyficznych dla dostawcy / wywoływania narzędzi: uruchom zawężone `pnpm test:live`

## Live: przegląd możliwości węzła Android

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Skrypt: `pnpm android:test:integration`
- Cel: wywołać **każde polecenie aktualnie ogłaszane** przez podłączony węzeł Android i potwierdzić zachowanie kontraktu polecenia.
- Zakres:
  - Wstępnie przygotowana/ręczna konfiguracja (pakiet nie instaluje, nie uruchamia ani nie paruje aplikacji).
  - Walidacja `node.invoke` Gateway polecenie po poleceniu dla wybranego węzła Android.
- Wymagana wstępna konfiguracja:
  - Aplikacja Android jest już podłączona i sparowana z Gateway.
  - Aplikacja pozostaje na pierwszym planie.
  - Uprawnienia/zgody na przechwytywanie są udzielone dla możliwości, które mają przechodzić.
- Opcjonalne nadpisania celu:
  - `OPENCLAW_ANDROID_NODE_ID` lub `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Pełne szczegóły konfiguracji Androida: [Android App](/pl/platforms/android)

## Live: test smoke modeli (klucze profili)

Testy live są podzielone na dwie warstwy, aby można było izolować awarie:

- „Direct model” mówi nam, czy dostawca/model w ogóle odpowiada przy danym kluczu.
- „Gateway smoke” mówi nam, czy pełny pipeline gateway+agent działa dla tego modelu (sesje, historia, narzędzia, polityka sandboxa itd.).

### Warstwa 1: bezpośrednie ukończenie modelu (bez Gateway)

- Test: `src/agents/models.profiles.live.test.ts`
- Cel:
  - Wyliczyć wykryte modele
  - Użyć `getApiKeyForModel` do wyboru modeli, dla których masz poświadczenia
  - Uruchomić małe completion dla każdego modelu (oraz ukierunkowane testy regresji tam, gdzie to potrzebne)
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Ustaw `OPENCLAW_LIVE_MODELS=modern` (lub `all`, alias dla modern), aby rzeczywiście uruchomić ten pakiet; w przeciwnym razie jest pomijany, aby `pnpm test:live` pozostało skupione na testach smoke Gateway
- Jak wybierać modele:
  - `OPENCLAW_LIVE_MODELS=modern`, aby uruchomić nowoczesną allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` jest aliasem dla nowoczesnej allowlist
  - lub `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist rozdzielana przecinkami)
  - Przeglądy modern/all domyślnie używają kuratorowanego limitu o wysokim sygnale; ustaw `OPENCLAW_LIVE_MAX_MODELS=0` dla wyczerpującego przeglądu modern albo dodatnią liczbę dla mniejszego limitu.
- Jak wybierać dostawców:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist rozdzielana przecinkami)
- Skąd pochodzą klucze:
  - Domyślnie: store profili i fallbacki env
  - Ustaw `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić **wyłącznie store profili**
- Dlaczego to istnieje:
  - Oddziela „API dostawcy jest zepsute / klucz jest nieprawidłowy” od „pipeline agenta Gateway jest zepsuty”
  - Zawiera małe, izolowane testy regresji (przykład: OpenAI Responses/Codex Responses reasoning replay + przepływy wywołań narzędzi)

### Warstwa 2: Gateway + test smoke agenta dev (to, co faktycznie robi „@openclaw”)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Cel:
  - Uruchomić Gateway w procesie
  - Utworzyć/zmodyfikować sesję `agent:dev:*` (nadpisanie modelu dla każdego uruchomienia)
  - Iterować po modelach-z-kluczami i potwierdzić:
    - „znaczącą” odpowiedź (bez narzędzi)
    - że działa rzeczywiste wywołanie narzędzia (sonda read)
    - opcjonalne dodatkowe sondy narzędzi (sonda exec+read)
    - że ścieżki regresji OpenAI (tylko tool-call → follow-up) nadal działają
- Szczegóły sond (aby można było szybko wyjaśniać awarie):
  - sonda `read`: test zapisuje plik nonce w workspace i prosi agenta o `read` tego pliku oraz zwrócenie nonce.
  - sonda `exec+read`: test prosi agenta o zapisanie nonce do pliku tymczasowego przez `exec`, a następnie o odczytanie go przez `read`.
  - sonda obrazu: test dołącza wygenerowany PNG (kot + losowy kod) i oczekuje, że model zwróci `cat <CODE>`.
  - Odniesienie implementacyjne: `src/gateway/gateway-models.profiles.live.test.ts` oraz `src/gateway/live-image-probe.ts`.
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Jak wybierać modele:
  - Domyślnie: nowoczesna allowlist (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` jest aliasem dla nowoczesnej allowlist
  - Albo ustaw `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (lub listę rozdzielaną przecinkami), aby zawęzić
  - Przeglądy Gateway modern/all domyślnie używają kuratorowanego limitu o wysokim sygnale; ustaw `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` dla wyczerpującego przeglądu modern albo dodatnią liczbę dla mniejszego limitu.
- Jak wybierać dostawców (unikaj „wszystkiego z OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist rozdzielana przecinkami)
- Sondy narzędzi i obrazów są zawsze włączone w tym teście live:
  - sonda `read` + sonda `exec+read` (obciążenie narzędzi)
  - sonda obrazu uruchamia się, gdy model deklaruje obsługę wejścia obrazowego
  - Przepływ (na wysokim poziomie):
    - Test generuje mały PNG z napisem „CAT” + losowy kod (`src/gateway/live-image-probe.ts`)
    - Wysyła go przez `agent` jako `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Gateway parsuje załączniki do `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Embedded agent przekazuje multimodalną wiadomość użytkownika do modelu
    - Potwierdzenie: odpowiedź zawiera `cat` + kod (tolerancja OCR: drobne pomyłki są dopuszczalne)

Wskazówka: aby zobaczyć, co możesz testować na swojej maszynie (oraz dokładne identyfikatory `provider/model`), uruchom:

```bash
openclaw models list
openclaw models list --json
```

## Live: test smoke backendu CLI (Claude, Codex, Gemini lub inne lokalne CLI)

- Test: `src/gateway/gateway-cli-backend.live.test.ts`
- Cel: zweryfikować pipeline Gateway + agent przy użyciu lokalnego backendu CLI, bez naruszania domyślnej konfiguracji.
- Domyślne ustawienia smoke specyficzne dla backendu znajdują się w definicji `cli-backend.ts` należącej do odpowiedniego rozszerzenia.
- Włączanie:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Domyślne wartości:
  - Domyślny dostawca/model: `claude-cli/claude-sonnet-4-6`
  - Zachowanie polecenia/argumentów/obrazów pochodzi z metadanych Plugin właściciela backendu CLI.
- Nadpisania (opcjonalne):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`, aby wysłać rzeczywisty załącznik obrazu (ścieżki są wstrzykiwane do promptu).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`, aby przekazywać ścieżki plików obrazów jako argumenty CLI zamiast przez wstrzykiwanie do promptu.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (lub `"list"`), aby sterować sposobem przekazywania argumentów obrazu, gdy ustawiono `IMAGE_ARG`.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`, aby wysłać drugą turę i zweryfikować przepływ wznowienia.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0`, aby wyłączyć domyślną sondę ciągłości tej samej sesji Claude Sonnet -> Opus (ustaw `1`, aby wymusić jej włączenie, gdy wybrany model obsługuje cel przełączenia).

Przykład:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Recepta Docker:

```bash
pnpm test:docker:live-cli-backend
```

Recepty Docker dla pojedynczego dostawcy:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Uwagi:

- Runner Docker znajduje się w `scripts/test-live-cli-backend-docker.sh`.
- Uruchamia test smoke live CLI-backend wewnątrz obrazu Docker repozytorium jako użytkownik `node` bez uprawnień roota.
- Rozwiązuje metadane smoke CLI z rozszerzenia właściciela, a następnie instaluje pasujący pakiet CLI dla Linux (`@anthropic-ai/claude-code`, `@openai/codex` lub `@google/gemini-cli`) do cache’owanego zapisywalnego prefiksu w `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (domyślnie: `~/.cache/openclaw/docker-cli-tools`).
- `pnpm test:docker:live-cli-backend:claude-subscription` wymaga przenośnego OAuth subskrypcji Claude Code przez `~/.claude/.credentials.json` z `claudeAiOauth.subscriptionType` albo `CLAUDE_CODE_OAUTH_TOKEN` z `claude setup-token`. Najpierw potwierdza bezpośrednie `claude -p` w Dockerze, a następnie uruchamia dwie tury Gateway CLI-backend bez zachowywania zmiennych env z kluczami API Anthropic. Ta ścieżka subskrypcyjna domyślnie wyłącza sondy Claude MCP/narzędzi i obrazów, ponieważ Claude obecnie kieruje użycie aplikacji innych firm przez rozliczanie dodatkowego użycia zamiast zwykłych limitów planu subskrypcji.
- Test smoke live CLI-backend sprawdza teraz ten sam pełny przepływ end-to-end dla Claude, Codex i Gemini: tura tekstowa, tura klasyfikacji obrazu, a następnie wywołanie narzędzia MCP `cron` weryfikowane przez Gateway CLI.
- Domyślny test smoke Claude także modyfikuje sesję z Sonnet do Opus i sprawdza, czy wznowiona sesja nadal pamięta wcześniejszą notatkę.

## Live: test smoke wiązania ACP (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Cel: zweryfikować rzeczywisty przepływ conversation-bind ACP z live agentem ACP:
  - wysłać `/acp spawn <agent> --bind here`
  - powiązać syntetyczną konwersację kanału wiadomości w miejscu
  - wysłać zwykły follow-up w tej samej konwersacji
  - sprawdzić, że follow-up trafia do transkryptu powiązanej sesji ACP
- Włączanie:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Domyślne wartości:
  - Agenci ACP w Dockerze: `claude,codex,gemini`
  - Agent ACP dla bezpośredniego `pnpm test:live ...`: `claude`
  - Kanał syntetyczny: kontekst rozmowy w stylu Slack DM
  - Backend ACP: `acpx`
- Nadpisania:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Uwagi:
  - Ta ścieżka używa powierzchni Gateway `chat.send` z polami synthetic originating-route tylko dla administratora, dzięki czemu testy mogą dołączyć kontekst kanału wiadomości bez udawania zewnętrznego dostarczenia.
  - Gdy `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` nie jest ustawione, test używa wbudowanego rejestru agentów Plugin `acpx` dla wybranego agenta harness ACP.

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

Recepty Docker dla pojedynczego agenta:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Uwagi dotyczące Dockera:

- Runner Docker znajduje się w `scripts/test-live-acp-bind-docker.sh`.
- Domyślnie uruchamia test smoke wiązania ACP kolejno dla wszystkich obsługiwanych live agentów CLI: `claude`, `codex`, a następnie `gemini`.
- Użyj `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` lub `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini`, aby zawęzić macierz.
- Pobiera `~/.profile`, przenosi odpowiedni materiał uwierzytelniający CLI do kontenera, instaluje `acpx` do zapisywalnego prefiksu npm, a następnie instaluje żądane live CLI (`@anthropic-ai/claude-code`, `@openai/codex` lub `@google/gemini-cli`), jeśli go brakuje.
- Wewnątrz Dockera runner ustawia `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`, aby acpx zachowywał zmienne env dostawcy z pobranego profilu dostępne dla podrzędnego CLI harnessu.

## Live: test smoke harnessu serwera aplikacji Codex

- Cel: zweryfikować należący do Plugin harness Codex przez zwykłą metodę Gateway
  `agent`:
  - załadować dołączony Plugin `codex`
  - wybrać `OPENCLAW_AGENT_RUNTIME=codex`
  - wysłać pierwszą turę agenta Gateway do `codex/gpt-5.4`
  - wysłać drugą turę do tej samej sesji OpenClaw i sprawdzić, że wątek
    serwera aplikacji może zostać wznowiony
  - uruchomić `/codex status` i `/codex models` tą samą ścieżką
    poleceń Gateway
- Test: `src/gateway/gateway-codex-harness.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- Domyślny model: `codex/gpt-5.4`
- Opcjonalna sonda obrazu: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- Opcjonalna sonda MCP/narzędzi: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- Test smoke ustawia `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, więc uszkodzony harness Codex
  nie może przejść testu przez ciche przełączenie awaryjne na PI.
- Uwierzytelnianie: `OPENAI_API_KEY` z powłoki/profilu oraz opcjonalnie skopiowane
  `~/.codex/auth.json` i `~/.codex/config.toml`

Recepta lokalna:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Recepta Docker:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Uwagi dotyczące Dockera:

- Runner Docker znajduje się w `scripts/test-live-codex-harness-docker.sh`.
- Pobiera zamontowane `~/.profile`, przekazuje `OPENAI_API_KEY`, kopiuje pliki
  uwierzytelniające CLI Codex, jeśli są obecne, instaluje `@openai/codex` do zapisywalnego zamontowanego prefiksu npm,
  przygotowuje drzewo źródłowe, a następnie uruchamia tylko test live harnessu Codex.
- Docker domyślnie włącza sondy obrazu oraz MCP/narzędzi. Ustaw
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` lub
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0`, gdy potrzebujesz węższego uruchomienia debugującego.
- Docker eksportuje też `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, zgodnie z konfiguracją
  testu live, tak aby fallback `openai-codex/*` lub PI nie mógł ukryć regresji
  harnessu Codex.

### Zalecane recepty live

Wąskie, jawne allowlist są najszybsze i najmniej podatne na niestabilność:

- Pojedynczy model, bezpośrednio (bez Gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Pojedynczy model, test smoke Gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Wywoływanie narzędzi u kilku dostawców:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Skupienie na Google (klucz API Gemini + Antigravity):
  - Gemini (klucz API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Uwagi:

- `google/...` używa interfejsu Gemini API (klucz API).
- `google-antigravity/...` używa mostu OAuth Antigravity (endpoint agenta w stylu Cloud Code Assist).
- `google-gemini-cli/...` używa lokalnego CLI Gemini na twojej maszynie (osobne uwierzytelnianie + specyficzne zachowania narzędzi).
- Gemini API vs Gemini CLI:
  - API: OpenClaw wywołuje hostowane Gemini API Google przez HTTP (uwierzytelnianie kluczem API / profilem); to właśnie większość użytkowników ma na myśli, mówiąc „Gemini”.
  - CLI: OpenClaw uruchamia lokalny binarny `gemini`; ma on własne uwierzytelnianie i może zachowywać się inaczej (streaming/obsługa narzędzi/rozbieżności wersji).

## Live: macierz modeli (co obejmujemy)

Nie ma stałej „listy modeli CI” (live jest opt-in), ale to są **zalecane** modele do regularnego obejmowania na maszynie deweloperskiej z kluczami.

### Nowoczesny zestaw smoke (wywoływanie narzędzi + obraz)

To jest uruchomienie „typowych modeli”, które oczekujemy utrzymywać w działaniu:

- OpenAI (bez Codex): `openai/gpt-5.4` (opcjonalnie: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` i `google/gemini-3-flash-preview` (unikaj starszych modeli Gemini 2.x)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` i `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Uruchom smoke Gateway z narzędziami + obrazem:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Bazowy zestaw: wywoływanie narzędzi (Read + opcjonalnie Exec)

Wybierz co najmniej jeden model z każdej rodziny dostawców:

- OpenAI: `openai/gpt-5.4` (lub `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (lub `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Opcjonalne dodatkowe pokrycie (warto mieć):

- xAI: `xai/grok-4` (lub najnowszy dostępny)
- Mistral: `mistral/`… (wybierz jeden model obsługujący „tools”, który masz włączony)
- Cerebras: `cerebras/`… (jeśli masz dostęp)
- LM Studio: `lmstudio/`… (lokalnie; wywoływanie narzędzi zależy od trybu API)

### Vision: wysyłanie obrazu (załącznik → wiadomość multimodalna)

Uwzględnij co najmniej jeden model obsługujący obrazy w `OPENCLAW_LIVE_GATEWAY_MODELS` (Claude/Gemini/warianty OpenAI obsługujące vision itd.), aby sprawdzić sondę obrazu.

### Agregatory / alternatywne Gateway

Jeśli masz włączone klucze, obsługujemy też testowanie przez:

- OpenRouter: `openrouter/...` (setki modeli; użyj `openclaw models scan`, aby znaleźć kandydatów obsługujących tools+image)
- OpenCode: `opencode/...` dla Zen oraz `opencode-go/...` dla Go (uwierzytelnianie przez `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Więcej dostawców, których możesz użyć w macierzy live (jeśli masz poświadczenia/konfigurację):

- Wbudowani: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Przez `models.providers` (własne endpointy): `minimax` (cloud/API) oraz dowolny proxy zgodny z OpenAI/Anthropic (LM Studio, vLLM, LiteLLM itd.)

Wskazówka: nie próbuj wpisywać na sztywno „wszystkich modeli” w dokumentacji. Autorytatywną listą jest to, co `discoverModels(...)` zwraca na twojej maszynie + jakie klucze są dostępne.

## Poświadczenia (nigdy nie commituj)

Testy live wykrywają poświadczenia tak samo jak CLI. Praktyczne konsekwencje:

- Jeśli działa CLI, testy live powinny znaleźć te same klucze.
- Jeśli test live zgłasza „no creds”, debuguj to tak samo jak `openclaw models list` / wybór modelu.

- Profile uwierzytelniania per agent: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (to właśnie oznaczają „profile keys” w testach live)
- Konfiguracja: `~/.openclaw/openclaw.json` (lub `OPENCLAW_CONFIG_PATH`)
- Starszy katalog stanu: `~/.openclaw/credentials/` (kopiowany do przygotowanego katalogu domowego live, jeśli jest obecny, ale nie jest to główny store kluczy profili)
- Lokalne uruchomienia live domyślnie kopiują aktywną konfigurację, pliki `auth-profiles.json` per agent, starszy katalog `credentials/` oraz obsługiwane zewnętrzne katalogi uwierzytelniania CLI do tymczasowego katalogu domowego testów; przygotowane katalogi domowe live pomijają `workspace/` i `sandboxes/`, a nadpisania ścieżek `agents.*.workspace` / `agentDir` są usuwane, aby sondy nie działały na twoim rzeczywistym workspace hosta.

Jeśli chcesz polegać na kluczach env (np. eksportowanych w twoim `~/.profile`), uruchamiaj testy lokalne po `source ~/.profile` albo użyj runnerów Docker poniżej (mogą zamontować `~/.profile` do kontenera).

## Live Deepgram (transkrypcja audio)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Włączanie: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live BytePlus coding plan

- Test: `src/agents/byteplus.live.test.ts`
- Włączanie: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Opcjonalne nadpisanie modelu: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live mediów workflow ComfyUI

- Test: `extensions/comfy/comfy.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Zakres:
  - Sprawdza dołączone ścieżki obrazów, wideo i `music_generate` Comfy
  - Pomija każdą możliwość, jeśli `models.providers.comfy.<capability>` nie jest skonfigurowane
  - Przydatne po zmianach w przesyłaniu workflow Comfy, odpytywaniu, pobieraniu lub rejestracji Plugin

## Live generowanie obrazów

- Test: `src/image-generation/runtime.live.test.ts`
- Polecenie: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Zakres:
  - Wylicza każdy zarejestrowany Plugin dostawcy generowania obrazów
  - Ładuje brakujące zmienne env dostawcy z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa kluczy API live/env przed zapisanymi profilami uwierzytelniania, dzięki czemu nieaktualne klucze testowe w `auth-profiles.json` nie maskują rzeczywistych poświadczeń z powłoki
  - Pomija dostawców bez używalnego uwierzytelniania/profilu/modelu
  - Uruchamia standardowe warianty generowania obrazów przez współdzieloną możliwość runtime:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Obecnie objęci dołączeni dostawcy:
  - `openai`
  - `google`
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie wyłącznie ze store profili i ignorować nadpisania tylko z env

## Live generowanie muzyki

- Test: `extensions/music-generation-providers.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Zakres:
  - Sprawdza współdzieloną dołączoną ścieżkę dostawców generowania muzyki
  - Obecnie obejmuje Google i MiniMax
  - Ładuje zmienne env dostawców z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa kluczy API live/env przed zapisanymi profilami uwierzytelniania, dzięki czemu nieaktualne klucze testowe w `auth-profiles.json` nie maskują rzeczywistych poświadczeń z powłoki
  - Pomija dostawców bez używalnego uwierzytelniania/profilu/modelu
  - Uruchamia oba zadeklarowane tryby runtime, gdy są dostępne:
    - `generate` z wejściem opartym wyłącznie na prompt
    - `edit`, gdy dostawca deklaruje `capabilities.edit.enabled`
  - Obecne pokrycie współdzielonej ścieżki:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: osobny plik live Comfy, nie ten współdzielony przegląd
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie wyłącznie ze store profili i ignorować nadpisania tylko z env

## Live generowanie wideo

- Test: `extensions/video-generation-providers.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Zakres:
  - Sprawdza współdzieloną dołączoną ścieżkę dostawców generowania wideo
  - Domyślnie używa bezpiecznej dla wydania ścieżki smoke: dostawcy inni niż FAL, jedno żądanie text-to-video na dostawcę, jednosekundowy prompt lobster oraz limit czasu operacji per dostawca z `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS` (domyślnie `180000`)
  - Domyślnie pomija FAL, ponieważ opóźnienie kolejki po stronie dostawcy może zdominować czas wydania; przekaż `--video-providers fal` lub `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="fal"`, aby uruchomić go jawnie
  - Ładuje zmienne env dostawców z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa kluczy API live/env przed zapisanymi profilami uwierzytelniania, dzięki czemu nieaktualne klucze testowe w `auth-profiles.json` nie maskują rzeczywistych poświadczeń z powłoki
  - Pomija dostawców bez używalnego uwierzytelniania/profilu/modelu
  - Domyślnie uruchamia tylko `generate`
  - Ustaw `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1`, aby uruchamiać także zadeklarowane tryby transformacji, gdy są dostępne:
    - `imageToVideo`, gdy dostawca deklaruje `capabilities.imageToVideo.enabled` i wybrany dostawca/model akceptuje lokalne wejście obrazu oparte na buforze we współdzielonym przeglądzie
    - `videoToVideo`, gdy dostawca deklaruje `capabilities.videoToVideo.enabled` i wybrany dostawca/model akceptuje lokalne wejście wideo oparte na buforze we współdzielonym przeglądzie
  - Obecni dostawcy `imageToVideo` zadeklarowani, ale pomijani we współdzielonym przeglądzie:
    - `vydra`, ponieważ dołączony `veo3` jest tylko tekstowy, a dołączony `kling` wymaga zdalnego URL obrazu
  - Pokrycie specyficzne dla dostawcy Vydra:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - ten plik uruchamia `veo3` text-to-video oraz ścieżkę `kling`, która domyślnie używa fixture zdalnego URL obrazu
  - Obecne pokrycie live `videoToVideo`:
    - tylko `runway`, gdy wybranym modelem jest `runway/gen4_aleph`
  - Obecni dostawcy `videoToVideo` zadeklarowani, ale pomijani we współdzielonym przeglądzie:
    - `alibaba`, `qwen`, `xai`, ponieważ te ścieżki obecnie wymagają zdalnych referencyjnych URL `http(s)` / MP4
    - `google`, ponieważ obecna współdzielona ścieżka Gemini/Veo używa lokalnego wejścia opartego na buforze i ta ścieżka nie jest akceptowana we współdzielonym przeglądzie
    - `openai`, ponieważ obecnej współdzielonej ścieżce brakuje gwarancji dostępu do specyficznych dla organizacji funkcji inpaint/remix wideo
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_SKIP_PROVIDERS=""`, aby uwzględnić każdego dostawcę w domyślnym przeglądzie, w tym FAL
  - `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS=60000`, aby zmniejszyć limit czasu operacji każdego dostawcy przy agresywnym uruchomieniu smoke
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie wyłącznie ze store profili i ignorować nadpisania tylko z env

## Harness live mediów

- Polecenie: `pnpm test:live:media`
- Cel:
  - Uruchamia współdzielone pakiety live obrazu, muzyki i wideo przez jeden natywny dla repozytorium punkt wejścia
  - Automatycznie ładuje brakujące zmienne env dostawców z `~/.profile`
  - Domyślnie automatycznie zawęża każdy pakiet do dostawców, którzy mają obecnie używalne uwierzytelnianie
  - Ponownie używa `scripts/test-live.mjs`, dzięki czemu zachowanie Heartbeat i trybu cichego pozostaje spójne
- Przykłady:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Runnery Docker (opcjonalne kontrole „działa w Linuksie”)

Te runnery Docker dzielą się na dwa koszyki:

- Runnery live-model: `test:docker:live-models` i `test:docker:live-gateway` uruchamiają tylko odpowiadający im plik live z kluczami profili wewnątrz obrazu Docker repozytorium (`src/agents/models.profiles.live.test.ts` oraz `src/gateway/gateway-models.profiles.live.test.ts`), montując lokalny katalog konfiguracji i workspace (oraz pobierając `~/.profile`, jeśli jest zamontowany). Odpowiadające im lokalne punkty wejścia to `test:live:models-profiles` i `test:live:gateway-profiles`.
- Runnery live Docker domyślnie używają mniejszego limitu smoke, aby pełny przegląd w Dockerze pozostawał praktyczny:
  `test:docker:live-models` domyślnie ustawia `OPENCLAW_LIVE_MAX_MODELS=12`, a
  `test:docker:live-gateway` domyślnie ustawia `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` oraz
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Nadpisz te zmienne env, gdy
  jawnie chcesz uruchomić większy wyczerpujący przegląd.
- `test:docker:all` buduje obraz live Docker raz przez `test:docker:live-build`, a następnie ponownie używa go dla dwóch ścieżek live Docker.
- Runnery smoke kontenerów: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` oraz `test:docker:plugins` uruchamiają jeden lub więcej rzeczywistych kontenerów i weryfikują ścieżki integracji wyższego poziomu.

Runnery Docker live-model montują też tylko potrzebne katalogi uwierzytelniania CLI (albo wszystkie obsługiwane, gdy uruchomienie nie jest zawężone), a następnie kopiują je do katalogu domowego kontenera przed uruchomieniem, tak aby zewnętrzny OAuth CLI mógł odświeżać tokeny bez modyfikowania store uwierzytelniania hosta:

- Direct models: `pnpm test:docker:live-models` (skrypt: `scripts/test-live-models-docker.sh`)
- Test smoke wiązania ACP: `pnpm test:docker:live-acp-bind` (skrypt: `scripts/test-live-acp-bind-docker.sh`)
- Test smoke backendu CLI: `pnpm test:docker:live-cli-backend` (skrypt: `scripts/test-live-cli-backend-docker.sh`)
- Test smoke harnessu serwera aplikacji Codex: `pnpm test:docker:live-codex-harness` (skrypt: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + agent dev: `pnpm test:docker:live-gateway` (skrypt: `scripts/test-live-gateway-models-docker.sh`)
- Test smoke live Open WebUI: `pnpm test:docker:openwebui` (skrypt: `scripts/e2e/openwebui-docker.sh`)
- Kreator onboardingu (TTY, pełne scaffoldowanie): `pnpm test:docker:onboard` (skrypt: `scripts/e2e/onboard-docker.sh`)
- Sieć Gateway (dwa kontenery, uwierzytelnianie WS + health): `pnpm test:docker:gateway-network` (skrypt: `scripts/e2e/gateway-network-docker.sh`)
- Most kanałów MCP (seedowany Gateway + most stdio + surowy test smoke ramek powiadomień Claude): `pnpm test:docker:mcp-channels` (skrypt: `scripts/e2e/mcp-channels-docker.sh`)
- Pluginy (test smoke instalacji + alias `/plugin` + semantyka restartu bundla Claude): `pnpm test:docker:plugins` (skrypt: `scripts/e2e/plugins-docker.sh`)

Runnery Docker live-model montują też bieżącą kopię roboczą tylko do odczytu i
przygotowują ją w tymczasowym katalogu roboczym wewnątrz kontenera. Dzięki temu obraz runtime
pozostaje lekki, a jednocześnie Vitest działa na dokładnie lokalnym kodzie źródłowym/konfiguracji.
Krok przygotowania pomija duże lokalne cache i artefakty budowania aplikacji, takie jak
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` oraz lokalne dla aplikacji katalogi `.build` lub
wyjścia Gradle, dzięki czemu uruchomienia live w Dockerze nie tracą minut na kopiowanie
artefaktów zależnych od maszyny.
Ustawiają też `OPENCLAW_SKIP_CHANNELS=1`, aby sondy live Gateway nie uruchamiały
rzeczywistych workerów kanałów Telegram/Discord/itd. wewnątrz kontenera.
`test:docker:live-models` nadal uruchamia `pnpm test:live`, więc przekaż także
`OPENCLAW_LIVE_GATEWAY_*`, gdy chcesz zawęzić lub wykluczyć pokrycie live Gateway z tej ścieżki Docker.
`test:docker:openwebui` to test smoke zgodności wyższego poziomu: uruchamia
kontener Gateway OpenClaw z włączonymi endpointami HTTP zgodnymi z OpenAI,
uruchamia przypięty kontener Open WebUI względem tego Gateway, loguje się przez
Open WebUI, weryfikuje, że `/api/models` udostępnia `openclaw/default`, a następnie wysyła
rzeczywiste żądanie czatu przez proxy `/api/chat/completions` Open WebUI.
Pierwsze uruchomienie może być zauważalnie wolniejsze, ponieważ Docker może potrzebować pobrać
obraz Open WebUI, a samo Open WebUI może potrzebować zakończyć własny cold-start.
Ta ścieżka wymaga działającego klucza modelu live, a `OPENCLAW_PROFILE_FILE`
(domyślnie `~/.profile`) jest podstawowym sposobem jego dostarczenia w uruchomieniach dockerowych.
Udane uruchomienia wypisują mały ładunek JSON, taki jak `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` jest celowo deterministyczny i nie wymaga
rzeczywistego konta Telegram, Discord ani iMessage. Uruchamia seedowany kontener
Gateway, startuje drugi kontener, który uruchamia `openclaw mcp serve`, a następnie
weryfikuje routowane wykrywanie konwersacji, odczyty transkryptów, metadane załączników,
zachowanie kolejki zdarzeń live, routing wysyłania wiadomości wychodzących oraz powiadomienia
kanału + uprawnień w stylu Claude przez rzeczywisty most stdio MCP. Kontrola powiadomień
sprawdza bezpośrednio surowe ramki stdio MCP, dzięki czemu test smoke weryfikuje to, co
most faktycznie emituje, a nie tylko to, co akurat ujawnia konkretny SDK klienta.

Ręczny test smoke zwykłego języka dla wątku ACP (nie CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Zachowaj ten skrypt do przepływów pracy regresji/debugowania. Może być ponownie potrzebny do walidacji routingu wątków ACP, więc go nie usuwaj.

Przydatne zmienne env:

- `OPENCLAW_CONFIG_DIR=...` (domyślnie: `~/.openclaw`) montowane do `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (domyślnie: `~/.openclaw/workspace`) montowane do `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (domyślnie: `~/.profile`) montowane do `/home/node/.profile` i pobierane przed uruchomieniem testów
- `OPENCLAW_DOCKER_PROFILE_ENV_ONLY=1`, aby weryfikować wyłącznie zmienne env pobrane z `OPENCLAW_PROFILE_FILE`, z użyciem tymczasowych katalogów config/workspace i bez montowania zewnętrznego uwierzytelniania CLI
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (domyślnie: `~/.cache/openclaw/docker-cli-tools`) montowane do `/home/node/.npm-global` dla cache’owanych instalacji CLI wewnątrz Dockera
- Zewnętrzne katalogi/pliki uwierzytelniania CLI pod `$HOME` są montowane tylko do odczytu pod `/host-auth...`, a następnie kopiowane do `/home/node/...` przed startem testów
  - Domyślne katalogi: `.minimax`
  - Domyślne pliki: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Zawężone uruchomienia dla dostawców montują tylko potrzebne katalogi/pliki wywnioskowane z `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Nadpisanie ręczne: `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` lub lista rozdzielana przecinkami, jak `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`, aby zawęzić uruchomienie
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`, aby filtrować dostawców w kontenerze
- `OPENCLAW_SKIP_DOCKER_BUILD=1`, aby ponownie użyć istniejącego obrazu `openclaw:local-live` przy ponownych uruchomieniach, które nie wymagają przebudowy
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby upewnić się, że poświadczenia pochodzą ze store profili (a nie z env)
- `OPENCLAW_OPENWEBUI_MODEL=...`, aby wybrać model udostępniany przez Gateway dla testu smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...`, aby nadpisać prompt kontroli nonce używany przez test smoke Open WebUI
- `OPENWEBUI_IMAGE=...`, aby nadpisać przypięty tag obrazu Open WebUI

## Kontrola spójności dokumentacji

Po edycji dokumentacji uruchom kontrole docs: `pnpm check:docs`.
Uruchom pełną walidację kotwic Mintlify, gdy potrzebujesz także sprawdzenia nagłówków w obrębie strony: `pnpm docs:check-links:anchors`.

## Regresja offline (bezpieczna dla CI)

To testy regresji „rzeczywistego pipeline” bez prawdziwych dostawców:

- Wywoływanie narzędzi Gateway (mock OpenAI, rzeczywista pętla Gateway + agent): `src/gateway/gateway.test.ts` (przypadek: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Kreator Gateway (WS `wizard.start`/`wizard.next`, wymuszone zapisywanie config + auth): `src/gateway/gateway.test.ts` (przypadek: "runs wizard over ws and writes auth token config")

## Ewaluacje niezawodności agentów (Skills)

Mamy już kilka testów bezpiecznych dla CI, które zachowują się jak „ewaluacje niezawodności agentów”:

- Mock wywoływania narzędzi przez rzeczywistą pętlę Gateway + agent (`src/gateway/gateway.test.ts`).
- Przepływy kreatora end-to-end, które walidują okablowanie sesji i efekty konfiguracji (`src/gateway/gateway.test.ts`).

Czego nadal brakuje dla Skills (zobacz [Skills](/pl/tools/skills)):

- **Decisioning:** gdy Skills są wymienione w promptcie, czy agent wybiera właściwy Skill (lub unika nieistotnych)?
- **Compliance:** czy agent czyta `SKILL.md` przed użyciem i wykonuje wymagane kroki/argumenty?
- **Workflow contracts:** scenariusze wieloturowe, które potwierdzają kolejność narzędzi, przenoszenie historii sesji i granice sandboxa.

Przyszłe ewaluacje powinny najpierw pozostać deterministyczne:

- Runner scenariuszy używający mock dostawców do potwierdzania wywołań narzędzi + ich kolejności, odczytów plików Skill i okablowania sesji.
- Mały pakiet scenariuszy skupionych na Skill (użycie vs unikanie, bramkowanie, prompt injection).
- Opcjonalne ewaluacje live (opt-in, bramkowane przez env) dopiero po wdrożeniu pakietu bezpiecznego dla CI.

## Testy kontraktowe (kształt Plugin i kanałów)

Testy kontraktowe weryfikują, że każdy zarejestrowany Plugin i kanał jest zgodny ze swoim
kontraktem interfejsu. Iterują po wszystkich wykrytych Plugin i uruchamiają pakiet
potwierdzeń kształtu i zachowania. Domyślna ścieżka unit `pnpm test` celowo
pomija te współdzielone pliki seam i smoke; uruchamiaj polecenia kontraktowe jawnie,
gdy modyfikujesz współdzielone powierzchnie kanałów lub dostawców.

### Polecenia

- Wszystkie kontrakty: `pnpm test:contracts`
- Tylko kontrakty kanałów: `pnpm test:contracts:channels`
- Tylko kontrakty dostawców: `pnpm test:contracts:plugins`

### Kontrakty kanałów

Znajdują się w `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Podstawowy kształt Plugin (id, nazwa, capabilities)
- **setup** - Kontrakt kreatora konfiguracji
- **session-binding** - Zachowanie wiązania sesji
- **outbound-payload** - Struktura ładunku wiadomości
- **inbound** - Obsługa wiadomości przychodzących
- **actions** - Handlery akcji kanału
- **threading** - Obsługa identyfikatorów wątków
- **directory** - API katalogu/listy
- **group-policy** - Wymuszanie zasad grupy

### Kontrakty statusu dostawców

Znajdują się w `src/plugins/contracts/*.contract.test.ts`.

- **status** - Sondy statusu kanału
- **registry** - Kształt rejestru Plugin

### Kontrakty dostawców

Znajdują się w `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Kontrakt przepływu uwierzytelniania
- **auth-choice** - Wybór/selekcja uwierzytelniania
- **catalog** - API katalogu modeli
- **discovery** - Wykrywanie Plugin
- **loader** - Ładowanie Plugin
- **runtime** - Runtime dostawcy
- **shape** - Kształt/interfejs Plugin
- **wizard** - Kreator konfiguracji

### Kiedy uruchamiać

- Po zmianie eksportów lub subpaths `plugin-sdk`
- Po dodaniu lub modyfikacji kanału albo Plugin dostawcy
- Po refaktoryzacji rejestracji lub wykrywania Plugin

Testy kontraktowe działają w CI i nie wymagają prawdziwych kluczy API.

## Dodawanie testów regresji (wskazówki)

Gdy naprawiasz problem dostawcy/modelu wykryty w live:

- Jeśli to możliwe, dodaj test regresji bezpieczny dla CI (mock/stub dostawcy albo uchwycenie dokładnej transformacji kształtu żądania)
- Jeśli problem z natury występuje tylko w live (limity szybkości, polityki uwierzytelniania), zachowaj test live jako wąski i opt-in przez zmienne env
- Preferuj kierowanie testu na najmniejszą warstwę, która wychwytuje błąd:
  - błąd konwersji/odtworzenia żądania dostawcy → test direct models
  - błąd pipeline Gateway sesji/historii/narzędzi → live smoke Gateway albo bezpieczny dla CI test mock Gateway
- Guardrail przechodzenia SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` wyprowadza jeden próbny cel dla każdej klasy SecretRef z metadanych rejestru (`listSecretTargetRegistryEntries()`), a następnie potwierdza, że identyfikatory exec segmentów przejścia są odrzucane.
  - Jeśli dodasz nową rodzinę docelową SecretRef `includeInPlan` w `src/secrets/target-registry-data.ts`, zaktualizuj `classifyTargetClass` w tym teście. Test celowo kończy się niepowodzeniem dla niesklasyfikowanych identyfikatorów docelowych, aby nie dało się po cichu pominąć nowych klas.
