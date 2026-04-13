---
read_when:
    - Uruchamianie testów lokalnie lub w CI
    - Dodawanie testów regresji dla błędów modeli/dostawców
    - Debugowanie zachowania Gateway i agenta
summary: 'Zestaw testowy: pakiety testów unit/e2e/live, uruchamiacze Docker i zakres pokrycia poszczególnych testów'
title: Testowanie
x-i18n:
    generated_at: "2026-04-13T08:50:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3db91b4bc36f626cd014958ec66b08b9cecd9faaa20a5746cd3a49ad4b0b1c38
    source_path: help/testing.md
    workflow: 15
---

# Testowanie

OpenClaw ma trzy pakiety Vitest (unit/integration, e2e, live) oraz niewielki zestaw uruchamiaczy Docker.

Ten dokument jest przewodnikiem „jak testujemy”:

- Co obejmuje każdy pakiet testów (i czego celowo _nie_ obejmuje)
- Jakie polecenia uruchamiać w typowych przepływach pracy (lokalnie, przed pushem, debugowanie)
- Jak testy live wykrywają poświadczenia oraz wybierają modele/dostawców
- Jak dodawać testy regresji dla rzeczywistych problemów modeli/dostawców

## Szybki start

W większości dni:

- Pełna bramka (oczekiwana przed pushem): `pnpm build && pnpm check && pnpm test`
- Szybsze lokalne uruchomienie całego pakietu na wydajnej maszynie: `pnpm test:max`
- Bezpośrednia pętla obserwacji Vitest: `pnpm test:watch`
- Bezpośrednie wskazanie pliku teraz obsługuje także ścieżki rozszerzeń/kanałów: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Gdy iterujesz nad pojedynczym błędem, najpierw preferuj uruchomienia ukierunkowane.
- Witryna QA oparta na Docker: `pnpm qa:lab:up`
- Linia QA oparta na Linux VM: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Gdy modyfikujesz testy lub chcesz uzyskać większą pewność:

- Bramka pokrycia: `pnpm test:coverage`
- Pakiet E2E: `pnpm test:e2e`

Podczas debugowania rzeczywistych dostawców/modeli (wymaga prawdziwych poświadczeń):

- Pakiet live (modele + sondy narzędzi/obrazów Gateway): `pnpm test:live`
- Ciche uruchomienie pojedynczego pliku live: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Wskazówka: gdy potrzebujesz tylko jednego nieudanego przypadku, zawężaj testy live za pomocą zmiennych środowiskowych allowlist opisanych poniżej.

## Uruchamiacze specyficzne dla QA

Te polecenia działają obok głównych pakietów testów, gdy potrzebujesz realizmu qa-lab:

- `pnpm openclaw qa suite`
  - Uruchamia scenariusze QA wspierane przez repozytorium bezpośrednio na hoście.
  - Domyślnie uruchamia równolegle wiele wybranych scenariuszy z izolowanymi workerami Gateway, maksymalnie do 64 workerów lub liczby wybranych scenariuszy. Użyj `--concurrency <count>`, aby dostroić liczbę workerów, albo `--concurrency 1` dla starszej linii sekwencyjnej.
- `pnpm openclaw qa suite --runner multipass`
  - Uruchamia ten sam pakiet QA wewnątrz jednorazowej maszyny wirtualnej Linux Multipass.
  - Zachowuje ten sam sposób wyboru scenariuszy co `qa suite` na hoście.
  - Używa tych samych flag wyboru dostawcy/modelu co `qa suite`.
  - Uruchomienia live przekazują do gościa obsługiwane wejścia uwierzytelniania QA, które są praktyczne dla środowiska gościa:
    klucze dostawców oparte na env, ścieżkę konfiguracji dostawcy QA live oraz `CODEX_HOME`, jeśli jest obecne.
  - Katalogi wyjściowe muszą pozostawać pod korzeniem repozytorium, aby gość mógł zapisywać dane z powrotem przez zamontowany obszar roboczy.
  - Zapisuje zwykły raport + podsumowanie QA oraz logi Multipass w `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - Uruchamia witrynę QA opartą na Docker do pracy QA w stylu operatorskim.
- `pnpm openclaw qa matrix`
  - Uruchamia linię live QA Matrix na jednorazowym homeserverze Tuwunel opartym na Docker.
  - Tworzy trzy tymczasowe konta użytkowników Matrix (`driver`, `sut`, `observer`) oraz jeden prywatny pokój, a następnie uruchamia podrzędny proces QA Gateway z rzeczywistym Plugin Matrix jako transportem SUT.
  - Domyślnie używa przypiętego stabilnego obrazu Tuwunel `ghcr.io/matrix-construct/tuwunel:v1.5.1`. Zastąp przez `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE`, gdy musisz przetestować inny obraz.
  - Matrix obecnie obsługuje tylko `--credential-source env`, ponieważ linia tworzy tymczasowych użytkowników lokalnie.
  - Zapisuje raport QA Matrix, podsumowanie oraz artefakt obserwowanych zdarzeń w `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - Uruchamia linię live QA Telegram na rzeczywistej prywatnej grupie przy użyciu tokenów botów driver i SUT z env.
  - Wymaga `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` oraz `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. Identyfikator grupy musi być numerycznym identyfikatorem czatu Telegram.
  - Obsługuje `--credential-source convex` dla współdzielonych poświadczeń z puli. Domyślnie używaj trybu env albo ustaw `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`, aby włączyć dzierżawy z puli.
  - Wymaga dwóch różnych botów w tej samej prywatnej grupie, przy czym bot SUT musi udostępniać nazwę użytkownika Telegram.
  - Aby zapewnić stabilną obserwację bot-bot, włącz Bot-to-Bot Communication Mode w `@BotFather` dla obu botów i upewnij się, że bot driver może obserwować ruch botów w grupie.
  - Zapisuje raport QA Telegram, podsumowanie oraz artefakt obserwowanych wiadomości w `.artifacts/qa-e2e/...`.

Linie live dla transportów współdzielą jeden standardowy kontrakt, aby nowe transporty nie dryfowały.

`qa-channel` pozostaje szerokim syntetycznym pakietem QA i nie jest częścią macierzy pokrycia live dla transportów.

| Linia    | Canary | Bramka wzmianek | Blokada allowlist | Odpowiedź najwyższego poziomu | Wznowienie po restarcie | Kontynuacja wątku | Izolacja wątku | Obserwacja reakcji | Polecenie pomocy |
| -------- | ------ | --------------- | ----------------- | ----------------------------- | ----------------------- | ----------------- | -------------- | ------------------ | ---------------- |
| Matrix   | x      | x               | x                 | x                             | x                       | x                 | x              | x                  |                  |
| Telegram | x      |                 |                   |                               |                         |                   |                |                    | x                |

### Współdzielone poświadczenia Telegram przez Convex (v1)

Gdy `--credential-source convex` (lub `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`) jest włączone dla
`openclaw qa telegram`, laboratorium QA pobiera wyłączną dzierżawę z puli opartej na Convex, wysyła Heartbeat
tej dzierżawy, gdy linia działa, i zwalnia dzierżawę przy zamykaniu.

Referencyjny szkielet projektu Convex:

- `qa/convex-credential-broker/`

Wymagane zmienne środowiskowe:

- `OPENCLAW_QA_CONVEX_SITE_URL` (na przykład `https://your-deployment.convex.site`)
- Jeden sekret dla wybranej roli:
  - `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` dla `maintainer`
  - `OPENCLAW_QA_CONVEX_SECRET_CI` dla `ci`
- Wybór roli poświadczeń:
  - CLI: `--credential-role maintainer|ci`
  - Domyślna wartość z env: `OPENCLAW_QA_CREDENTIAL_ROLE` (domyślnie `maintainer`)

Opcjonalne zmienne środowiskowe:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS` (domyślnie `1200000`)
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS` (domyślnie `30000`)
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS` (domyślnie `90000`)
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS` (domyślnie `15000`)
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX` (domyślnie `/qa-credentials/v1`)
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID` (opcjonalny identyfikator śledzenia)
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` pozwala na adresy URL Convex `http://` w local loopback wyłącznie do lokalnego developmentu.

`OPENCLAW_QA_CONVEX_SITE_URL` powinien używać `https://` w normalnej pracy.

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
  - Wyczerpanie/możliwość ponowienia: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
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

Kształt payload dla rodzaju Telegram:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` musi być ciągiem znaków będącym numerycznym identyfikatorem czatu Telegram.
- `admin/add` waliduje ten kształt dla `kind: "telegram"` i odrzuca nieprawidłowy payload.

### Dodawanie kanału do QA

Dodanie kanału do markdownowego systemu QA wymaga dokładnie dwóch rzeczy:

1. Adaptera transportu dla kanału.
2. Pakietu scenariuszy, który testuje kontrakt kanału.

Nie dodawaj uruchamiacza QA specyficznego dla kanału, jeśli wspólny uruchamiacz `qa-lab`
może obsłużyć ten przepływ.

`qa-lab` odpowiada za wspólną mechanikę:

- uruchamianie i zamykanie pakietu
- współbieżność workerów
- zapisywanie artefaktów
- generowanie raportów
- wykonywanie scenariuszy
- aliasy zgodności dla starszych scenariuszy `qa-channel`

Adapter kanału odpowiada za kontrakt transportu:

- jak Gateway jest konfigurowany dla tego transportu
- jak sprawdzana jest gotowość
- jak wstrzykiwane są zdarzenia przychodzące
- jak obserwowane są wiadomości wychodzące
- jak udostępniane są transkrypcje i znormalizowany stan transportu
- jak wykonywane są akcje oparte na transporcie
- jak obsługiwany jest reset lub czyszczenie specyficzne dla transportu

Minimalny próg wdrożenia dla nowego kanału to:

1. Zaimplementować adapter transportu na wspólnej granicy `qa-lab`.
2. Zarejestrować adapter w rejestrze transportów.
3. Zachować mechanikę specyficzną dla transportu wewnątrz adaptera lub harnessu kanału.
4. Napisać lub dostosować scenariusze markdown w `qa/scenarios/`.
5. Używać ogólnych helperów scenariuszy dla nowych scenariuszy.
6. Zachować działanie istniejących aliasów zgodności, chyba że repozytorium przeprowadza zamierzoną migrację.

Zasada decyzyjna jest ścisła:

- Jeśli zachowanie można wyrazić raz w `qa-lab`, umieść je w `qa-lab`.
- Jeśli zachowanie zależy od jednego transportu kanału, zachowaj je w tym adapterze lub harnessie Plugin.
- Jeśli scenariusz wymaga nowej możliwości, z której może skorzystać więcej niż jeden kanał, dodaj ogólny helper zamiast gałęzi specyficznej dla kanału w `suite.ts`.
- Jeśli zachowanie ma sens tylko dla jednego transportu, zachowaj scenariusz jako specyficzny dla tego transportu i zaznacz to wyraźnie w kontrakcie scenariusza.

Preferowane nazwy ogólnych helperów dla nowych scenariuszy to:

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

Aliasy zgodności pozostają dostępne dla istniejących scenariuszy, w tym:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

Nowa praca nad kanałami powinna używać ogólnych nazw helperów.
Aliasy zgodności istnieją po to, aby uniknąć migracji typu flag day, a nie jako model
tworzenia nowych scenariuszy.

## Pakiety testów (co uruchamia się gdzie)

O pakietach warto myśleć jako o „rosnącym realizmie” (oraz rosnącej podatności na błędy/niestabilność i koszcie):

### Unit / integration (domyślne)

- Polecenie: `pnpm test`
- Konfiguracja: dziesięć sekwencyjnych uruchomień shardów (`vitest.full-*.config.ts`) na istniejących zakresowanych projektach Vitest
- Pliki: inwentarze core/unit w `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts` oraz umieszczone na allowliście testy node w `ui`, objęte przez `vitest.unit.config.ts`
- Zakres:
  - Czyste testy unit
  - Testy integracyjne in-process (uwierzytelnianie Gateway, routing, narzędzia, parsowanie, konfiguracja)
  - Deterministyczne testy regresji dla znanych błędów
- Oczekiwania:
  - Uruchamia się w CI
  - Nie wymaga prawdziwych kluczy
  - Powinno być szybkie i stabilne
- Uwaga o projektach:
  - Niekierunkowane `pnpm test` uruchamia teraz jedenaście mniejszych konfiguracji shardów (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) zamiast jednego ogromnego natywnego procesu root-project. Zmniejsza to szczytowe RSS na obciążonych maszynach i zapobiega temu, by prace `auto-reply`/rozszerzeń zagłodziły niezwiązane pakiety.
  - `pnpm test --watch` nadal używa natywnego grafu projektów root `vitest.config.ts`, ponieważ wieloszardowa pętla watch nie jest praktyczna.
  - `pnpm test`, `pnpm test:watch` i `pnpm test:perf:imports` kierują jawne cele plików/katalogów najpierw przez zakresowane linie, dzięki czemu `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` nie płaci kosztu uruchomienia pełnego root project.
  - `pnpm test:changed` rozwija zmienione ścieżki git do tych samych zakresowanych linii, gdy diff dotyczy tylko routowalnych plików źródłowych/testowych; edycje konfiguracji/ustawień nadal przechodzą do szerokiego ponownego uruchomienia root project.
  - Lekkie importowo testy unit z agentów, poleceń, pluginów, helperów `auto-reply`, `plugin-sdk` i podobnych czystych obszarów narzędziowych są kierowane przez linię `unit-fast`, która pomija `test/setup-openclaw-runtime.ts`; pliki stanowe/ciężkie runtime pozostają na istniejących liniach.
  - Wybrane pliki źródłowe helperów `plugin-sdk` i `commands` również mapują uruchomienia trybu changed do jawnych sąsiednich testów w tych lekkich liniach, dzięki czemu edycje helperów nie wymuszają ponownego uruchamiania całego ciężkiego pakietu dla tego katalogu.
  - `auto-reply` ma teraz trzy dedykowane koszyki: helpery core najwyższego poziomu, testy integracyjne najwyższego poziomu `reply.*` oraz poddrzewo `src/auto-reply/reply/**`. Dzięki temu najcięższa praca harnessu odpowiedzi nie trafia do tanich testów status/chunk/token.
- Uwaga o osadzonym uruchamiaczu:
  - Gdy zmieniasz wejścia wykrywania message-tool lub kontekst runtime Compaction,
    utrzymuj oba poziomy pokrycia.
  - Dodawaj ukierunkowane testy regresji helperów dla czystych granic routingu/normalizacji.
  - Utrzymuj też w dobrej kondycji pakiety integracyjne osadzonego uruchamiacza:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts` oraz
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Te pakiety weryfikują, że zakresowane identyfikatory i zachowanie Compaction nadal przepływają
    przez rzeczywiste ścieżki `run.ts` / `compact.ts`; same testy helperów nie są
    wystarczającym zamiennikiem dla tych ścieżek integracyjnych.
- Uwaga o puli:
  - Bazowa konfiguracja Vitest domyślnie używa teraz `threads`.
  - Współdzielona konfiguracja Vitest ustawia również `isolate: false` i używa nieizolowanego uruchamiacza w projektach root, konfiguracjach e2e i live.
  - Główna linia UI zachowuje konfigurację `jsdom` i optimizer, ale teraz również działa na współdzielonym nieizolowanym uruchamiaczu.
  - Każdy shard `pnpm test` dziedziczy te same domyślne ustawienia `threads` + `isolate: false` ze współdzielonej konfiguracji Vitest.
  - Współdzielony launcher `scripts/run-vitest.mjs` domyślnie dodaje teraz także `--no-maglev` dla podrzędnych procesów Node Vitest, aby ograniczyć narzut kompilacji V8 podczas dużych lokalnych uruchomień. Ustaw `OPENCLAW_VITEST_ENABLE_MAGLEV=1`, jeśli chcesz porównać zachowanie z domyślnym V8.
- Uwaga o szybkiej iteracji lokalnej:
  - `pnpm test:changed` kieruje przez zakresowane linie, gdy zmienione ścieżki czysto mapują się na mniejszy pakiet.
  - `pnpm test:max` i `pnpm test:changed:max` zachowują to samo kierowanie, tylko z wyższym limitem workerów.
  - Automatyczne skalowanie lokalnych workerów jest teraz celowo konserwatywne i dodatkowo zwalnia, gdy średnie obciążenie hosta jest już wysokie, dzięki czemu wiele równoczesnych uruchomień Vitest domyślnie powoduje mniej szkód.
  - Bazowa konfiguracja Vitest oznacza projekty/pliki konfiguracyjne jako `forceRerunTriggers`, aby ponowne uruchomienia w trybie changed pozostawały poprawne, gdy zmienia się okablowanie testów.
  - Konfiguracja utrzymuje włączone `OPENCLAW_VITEST_FS_MODULE_CACHE` na obsługiwanych hostach; ustaw `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`, jeśli chcesz jeden jawny katalog cache do bezpośredniego profilowania.
- Uwaga o debugowaniu wydajności:
  - `pnpm test:perf:imports` włącza raportowanie czasu importu Vitest oraz wynik z podziałem importów.
  - `pnpm test:perf:imports:changed` zawęża ten sam widok profilowania do plików zmienionych od `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` porównuje kierowane `test:changed` z natywną ścieżką root-project dla tego zatwierdzonego diffu i wypisuje czas ścienny oraz maksymalne RSS na macOS.
- `pnpm test:perf:changed:bench -- --worktree` benchmarkuje bieżące brudne drzewo, kierując listę zmienionych plików przez `scripts/test-projects.mjs` oraz główną konfigurację Vitest.
  - `pnpm test:perf:profile:main` zapisuje profil CPU głównego wątku dla narzutu uruchamiania i transformacji Vitest/Vite.
  - `pnpm test:perf:profile:runner` zapisuje profile CPU+heap uruchamiacza dla pakietu unit z wyłączoną równoległością plików.

### E2E (smoke Gateway)

- Polecenie: `pnpm test:e2e`
- Konfiguracja: `vitest.e2e.config.ts`
- Pliki: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Domyślne ustawienia runtime:
  - Używa Vitest `threads` z `isolate: false`, zgodnie z resztą repozytorium.
  - Używa adaptacyjnej liczby workerów (CI: do 2, lokalnie: domyślnie 1).
  - Domyślnie działa w trybie cichym, aby ograniczyć narzut I/O konsoli.
- Przydatne nadpisania:
  - `OPENCLAW_E2E_WORKERS=<n>` aby wymusić liczbę workerów (maksymalnie 16).
  - `OPENCLAW_E2E_VERBOSE=1` aby ponownie włączyć szczegółowy wynik konsoli.
- Zakres:
  - Zachowanie end-to-end Gateway z wieloma instancjami
  - Powierzchnie WebSocket/HTTP, parowanie Node oraz cięższa komunikacja sieciowa
- Oczekiwania:
  - Uruchamia się w CI (gdy jest włączone w pipeline)
  - Nie wymaga prawdziwych kluczy
  - Ma więcej ruchomych części niż testy unit (może być wolniejsze)

### E2E: smoke backendu OpenShell

- Polecenie: `pnpm test:e2e:openshell`
- Plik: `test/openshell-sandbox.e2e.test.ts`
- Zakres:
  - Uruchamia na hoście izolowany Gateway OpenShell przez Docker
  - Tworzy sandbox z tymczasowego lokalnego Dockerfile
  - Testuje backend OpenShell w OpenClaw przez rzeczywiste `sandbox ssh-config` + wykonanie SSH
  - Weryfikuje zdalnie kanoniczne zachowanie systemu plików przez most fs sandboxa
- Oczekiwania:
  - Tylko opt-in; nie jest częścią domyślnego uruchomienia `pnpm test:e2e`
  - Wymaga lokalnego CLI `openshell` oraz działającego demona Docker
  - Używa izolowanych `HOME` / `XDG_CONFIG_HOME`, a następnie niszczy testowy Gateway i sandbox
- Przydatne nadpisania:
  - `OPENCLAW_E2E_OPENSHELL=1`, aby włączyć test przy ręcznym uruchamianiu szerszego pakietu e2e
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`, aby wskazać niestandardowy binarny plik CLI lub skrypt wrappera

### Live (rzeczywiści dostawcy + rzeczywiste modele)

- Polecenie: `pnpm test:live`
- Konfiguracja: `vitest.live.config.ts`
- Pliki: `src/**/*.live.test.ts`
- Domyślnie: **włączone** przez `pnpm test:live` (ustawia `OPENCLAW_LIVE_TEST=1`)
- Zakres:
  - „Czy ten dostawca/model naprawdę działa _dzisiaj_ z prawdziwymi poświadczeniami?”
  - Wychwytywanie zmian formatu dostawcy, niuansów wywołań narzędzi, problemów z uwierzytelnianiem oraz zachowania limitów szybkości
- Oczekiwania:
  - Z założenia niestabilne w CI (rzeczywiste sieci, rzeczywiste polityki dostawców, limity, awarie)
  - Kosztują pieniądze / zużywają limity szybkości
  - Lepiej uruchamiać zawężone podzbiory zamiast „wszystkiego”
- Uruchomienia live pobierają `~/.profile`, aby przejąć brakujące klucze API.
- Domyślnie uruchomienia live nadal izolują `HOME` i kopiują materiały konfiguracji/uwierzytelniania do tymczasowego katalogu testowego, aby fixture unit nie mogły modyfikować twojego rzeczywistego `~/.openclaw`.
- Ustaw `OPENCLAW_LIVE_USE_REAL_HOME=1` tylko wtedy, gdy celowo chcesz, by testy live używały twojego rzeczywistego katalogu domowego.
- `pnpm test:live` domyślnie działa teraz w cichszym trybie: zachowuje wynik postępu `[live] ...`, ale ukrywa dodatkowy komunikat o `~/.profile` i wycisza logi bootstrapu Gateway/hałas Bonjour. Ustaw `OPENCLAW_LIVE_TEST_QUIET=0`, jeśli chcesz z powrotem pełne logi startowe.
- Rotacja kluczy API (specyficzna dla dostawcy): ustaw `*_API_KEYS` w formacie rozdzielanym przecinkami/średnikami albo `*_API_KEY_1`, `*_API_KEY_2` (na przykład `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) lub nadpisanie per-live przez `OPENCLAW_LIVE_*_KEY`; testy ponawiają próby przy odpowiedziach z limitem szybkości.
- Wynik postępu/Heartbeat:
  - Pakiety live emitują teraz linie postępu do stderr, dzięki czemu długie wywołania dostawców są widocznie aktywne, nawet gdy przechwytywanie konsoli Vitest jest wyciszone.
  - `vitest.live.config.ts` wyłącza przechwytywanie konsoli przez Vitest, dzięki czemu linie postępu dostawcy/Gateway są strumieniowane natychmiast podczas uruchomień live.
  - Dostosuj Heartbeat dla bezpośrednich modeli przez `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Dostosuj Heartbeat dla Gateway/sond przez `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Który pakiet powinienem uruchomić?

Użyj tej tabeli decyzyjnej:

- Edycja logiki/testów: uruchom `pnpm test` (oraz `pnpm test:coverage`, jeśli zmieniłeś dużo)
- Zmiany w komunikacji sieciowej Gateway / protokole WS / parowaniu: dodaj `pnpm test:e2e`
- Debugowanie „mój bot nie działa” / błędów specyficznych dla dostawcy / wywołań narzędzi: uruchom zawężone `pnpm test:live`

## Live: przegląd możliwości Android Node

- Test: `src/gateway/android-node.capabilities.live.test.ts`
- Skrypt: `pnpm android:test:integration`
- Cel: wywołać **każde polecenie aktualnie ogłaszane** przez podłączony Android Node i sprawdzić zachowanie kontraktu poleceń.
- Zakres:
  - Wstępnie przygotowana/ręczna konfiguracja (pakiet nie instaluje, nie uruchamia ani nie paruje aplikacji).
  - Walidacja `node.invoke` Gateway polecenie po poleceniu dla wybranego Android Node.
- Wymagane przygotowanie:
  - Aplikacja Android jest już połączona i sparowana z Gateway.
  - Aplikacja pozostaje na pierwszym planie.
  - Uprawnienia/zgody na przechwytywanie zostały przyznane dla możliwości, które mają przechodzić.
- Opcjonalne nadpisania celu:
  - `OPENCLAW_ANDROID_NODE_ID` lub `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Pełne szczegóły konfiguracji Android: [Android App](/pl/platforms/android)

## Live: smoke modeli (klucze profili)

Testy live są podzielone na dwie warstwy, aby można było izolować błędy:

- „Direct model” mówi nam, czy dostawca/model w ogóle potrafi odpowiedzieć przy danym kluczu.
- „Gateway smoke” mówi nam, czy pełny pipeline gateway+agent działa dla tego modelu (sesje, historia, narzędzia, polityka sandbox itd.).

### Warstwa 1: bezpośrednie ukończenie modelu (bez Gateway)

- Test: `src/agents/models.profiles.live.test.ts`
- Cel:
  - Wyliczać wykryte modele
  - Używać `getApiKeyForModel` do wyboru modeli, dla których masz poświadczenia
  - Wykonywać małe ukończenie dla każdego modelu (oraz ukierunkowane testy regresji tam, gdzie to potrzebne)
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Ustaw `OPENCLAW_LIVE_MODELS=modern` (lub `all`, alias dla modern), aby faktycznie uruchomić ten pakiet; w przeciwnym razie zostanie pominięty, aby `pnpm test:live` było skupione na smoke Gateway
- Jak wybierać modele:
  - `OPENCLAW_LIVE_MODELS=modern`, aby uruchomić nowoczesną allowlistę (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` jest aliasem dla nowoczesnej allowlisty
  - albo `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlista rozdzielana przecinkami)
  - Przeglądy modern/all domyślnie używają kuratorowanego limitu o wysokim sygnale; ustaw `OPENCLAW_LIVE_MAX_MODELS=0` dla wyczerpującego przeglądu modern albo dodatnią liczbę dla mniejszego limitu.
- Jak wybierać dostawców:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlista rozdzielana przecinkami)
- Skąd pochodzą klucze:
  - Domyślnie: magazyn profili i fallbacki env
  - Ustaw `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić wyłącznie **magazyn profili**
- Po co to istnieje:
  - Oddziela „API dostawcy jest zepsute / klucz jest nieprawidłowy” od „pipeline agenta Gateway jest zepsuty”
  - Zawiera małe, izolowane testy regresji (przykład: replay rozumowania OpenAI Responses/Codex Responses + przepływy wywołań narzędzi)

### Warstwa 2: smoke Gateway + agenta developerskiego (to, co faktycznie robi „@openclaw”)

- Test: `src/gateway/gateway-models.profiles.live.test.ts`
- Cel:
  - Uruchomić in-process Gateway
  - Utworzyć/spatchować sesję `agent:dev:*` (nadpisanie modelu dla każdego uruchomienia)
  - Iterować po modelach-z-kluczami i sprawdzać:
    - „sensowną” odpowiedź (bez narzędzi)
    - że rzeczywiste wywołanie narzędzia działa (sonda odczytu)
    - opcjonalne dodatkowe sondy narzędzi (sonda exec+read)
    - że ścieżki regresji OpenAI (tylko tool-call → follow-up) nadal działają
- Szczegóły sond (aby można było szybko wyjaśniać błędy):
  - sonda `read`: test zapisuje plik nonce w obszarze roboczym i prosi agenta o jego `read` oraz odesłanie nonce.
  - sonda `exec+read`: test prosi agenta o zapisanie nonce do pliku tymczasowego przez `exec`, a następnie o jego odczytanie przez `read`.
  - sonda obrazu: test dołącza wygenerowany PNG (kot + losowy kod) i oczekuje, że model zwróci `cat <CODE>`.
  - Referencja implementacyjna: `src/gateway/gateway-models.profiles.live.test.ts` oraz `src/gateway/live-image-probe.ts`.
- Jak włączyć:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
- Jak wybierać modele:
  - Domyślnie: nowoczesna allowlista (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` jest aliasem dla nowoczesnej allowlisty
  - Albo ustaw `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (lub listę rozdzielaną przecinkami), aby zawęzić
  - Przeglądy gateway modern/all domyślnie używają kuratorowanego limitu o wysokim sygnale; ustaw `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` dla wyczerpującego przeglądu modern albo dodatnią liczbę dla mniejszego limitu.
- Jak wybierać dostawców (aby uniknąć „wszystkiego z OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlista rozdzielana przecinkami)
- Sondy narzędzi + obrazu są zawsze włączone w tym teście live:
  - sonda `read` + sonda `exec+read` (obciążenie narzędzi)
  - sonda obrazu działa, gdy model deklaruje obsługę wejścia obrazowego
  - Przepływ (na wysokim poziomie):
    - Test generuje mały PNG z napisem „CAT” + losowym kodem (`src/gateway/live-image-probe.ts`)
    - Wysyła go przez `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Gateway parsuje załączniki do `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Osadzony agent przekazuje do modelu multimodalną wiadomość użytkownika
    - Asercja: odpowiedź zawiera `cat` + kod (tolerancja OCR: drobne błędy są dozwolone)

Wskazówka: aby zobaczyć, co możesz testować na swojej maszynie (oraz dokładne identyfikatory `provider/model`), uruchom:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke backendu CLI (Claude, Codex, Gemini lub inne lokalne CLI)

- Test: `src/gateway/gateway-cli-backend.live.test.ts`
- Cel: zweryfikować pipeline Gateway + agent przy użyciu lokalnego backendu CLI, bez naruszania domyślnej konfiguracji.
- Domyślne ustawienia smoke specyficzne dla backendu znajdują się w definicji `cli-backend.ts` należącej do odpowiedniego rozszerzenia.
- Włączanie:
  - `pnpm test:live` (lub `OPENCLAW_LIVE_TEST=1`, jeśli wywołujesz Vitest bezpośrednio)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Domyślne ustawienia:
  - Domyślny dostawca/model: `claude-cli/claude-sonnet-4-6`
  - Zachowanie polecenia/argumentów/obrazu pochodzi z metadanych Plugin odpowiedzialnego za backend CLI.
- Nadpisania (opcjonalne):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`, aby wysłać rzeczywisty załącznik obrazu (ścieżki są wstrzykiwane do promptu).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`, aby przekazywać ścieżki plików obrazów jako argumenty CLI zamiast przez wstrzykiwanie do promptu.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (lub `"list"`), aby sterować sposobem przekazywania argumentów obrazów, gdy ustawiono `IMAGE_ARG`.
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

- Uruchamiacz Docker znajduje się w `scripts/test-live-cli-backend-docker.sh`.
- Uruchamia smoke live backendu CLI wewnątrz obrazu Docker repozytorium jako użytkownik nieuprzywilejowany `node`.
- Rozwiązuje metadane smoke CLI z odpowiedniego rozszerzenia, a następnie instaluje pasujący pakiet Linux CLI (`@anthropic-ai/claude-code`, `@openai/codex` lub `@google/gemini-cli`) do cache’owanego zapisywalnego prefiksu w `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (domyślnie: `~/.cache/openclaw/docker-cli-tools`).
- `pnpm test:docker:live-cli-backend:claude-subscription` wymaga przenośnego OAuth subskrypcji Claude Code przez `~/.claude/.credentials.json` z `claudeAiOauth.subscriptionType` lub `CLAUDE_CODE_OAUTH_TOKEN` z `claude setup-token`. Najpierw potwierdza bezpośrednie `claude -p` w Docker, a następnie uruchamia dwie tury backendu CLI Gateway bez zachowywania zmiennych env z kluczem API Anthropic. Ta linia subskrypcyjna domyślnie wyłącza sondy Claude MCP/tool i obrazu, ponieważ Claude obecnie rozlicza użycie aplikacji zewnętrznych przez billing extra-usage zamiast zwykłych limitów planu subskrypcji.
- Smoke live backendu CLI testuje teraz ten sam przepływ end-to-end dla Claude, Codex i Gemini: tura tekstowa, tura klasyfikacji obrazu, a następnie wywołanie narzędzia MCP `cron` zweryfikowane przez CLI Gateway.
- Domyślny smoke Claude dodatkowo patchuje sesję z Sonnet do Opus i sprawdza, czy wznowiona sesja nadal pamięta wcześniejszą notatkę.

## Live: smoke powiązania ACP (`/acp spawn ... --bind here`)

- Test: `src/gateway/gateway-acp-bind.live.test.ts`
- Cel: zweryfikować rzeczywisty przepływ powiązania rozmowy ACP z aktywnym agentem ACP:
  - wysłać `/acp spawn <agent> --bind here`
  - powiązać syntetyczną rozmowę kanału wiadomości w miejscu
  - wysłać zwykły follow-up w tej samej rozmowie
  - zweryfikować, że follow-up trafia do transkryptu powiązanej sesji ACP
- Włączanie:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Domyślne ustawienia:
  - Agenci ACP w Docker: `claude,codex,gemini`
  - Agent ACP dla bezpośredniego `pnpm test:live ...`: `claude`
  - Syntetyczny kanał: kontekst rozmowy w stylu Slack DM
  - Backend ACP: `acpx`
- Nadpisania:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Uwagi:
  - Ta linia używa powierzchni `chat.send` Gateway z polami synthetic originating-route dostępnymi tylko dla administratora, dzięki czemu testy mogą dołączać kontekst kanału wiadomości bez udawania zewnętrznego dostarczenia.
  - Gdy `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` nie jest ustawione, test używa wbudowanego rejestru agentów Plugin `acpx` dla wybranego agenta harnessu ACP.

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

Uwagi dotyczące Docker:

- Uruchamiacz Docker znajduje się w `scripts/test-live-acp-bind-docker.sh`.
- Domyślnie uruchamia smoke powiązania ACP kolejno dla wszystkich obsługiwanych aktywnych agentów CLI: `claude`, `codex`, a następnie `gemini`.
- Użyj `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex` lub `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini`, aby zawęzić macierz.
- Pobiera `~/.profile`, przygotowuje pasujące materiały uwierzytelniające CLI w kontenerze, instaluje `acpx` do zapisywalnego prefiksu npm, a następnie instaluje żądane aktywne CLI (`@anthropic-ai/claude-code`, `@openai/codex` lub `@google/gemini-cli`), jeśli go brakuje.
- Wewnątrz Docker uruchamiacz ustawia `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`, aby `acpx` zachował zmienne env dostawcy z pobranego profilu dostępne dla podrzędnego CLI harnessu.

## Live: smoke harnessu app-server Codex

- Cel: zweryfikować należący do Plugin harness Codex przez normalną
  metodę `agent` Gateway:
  - załadować bundlowany Plugin `codex`
  - wybrać `OPENCLAW_AGENT_RUNTIME=codex`
  - wysłać pierwszą turę agenta Gateway do `codex/gpt-5.4`
  - wysłać drugą turę do tej samej sesji OpenClaw i zweryfikować, że wątek
    app-server może zostać wznowiony
  - uruchomić `/codex status` oraz `/codex models` przez tę samą ścieżkę
    poleceń Gateway
- Test: `src/gateway/gateway-codex-harness.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- Domyślny model: `codex/gpt-5.4`
- Opcjonalna sonda obrazu: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- Opcjonalna sonda MCP/tool: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- Ten smoke ustawia `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, aby uszkodzony
  harness Codex nie mógł przejść przez cichy fallback do PI.
- Uwierzytelnianie: `OPENAI_API_KEY` z powłoki/profilu oraz opcjonalnie skopiowane
  `~/.codex/auth.json` i `~/.codex/config.toml`

Lokalna recepta:

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

Uwagi dotyczące Docker:

- Uruchamiacz Docker znajduje się w `scripts/test-live-codex-harness-docker.sh`.
- Pobiera zamontowane `~/.profile`, przekazuje `OPENAI_API_KEY`, kopiuje pliki
  uwierzytelniające CLI Codex, gdy są dostępne, instaluje `@openai/codex` do zapisywalnego zamontowanego prefiksu npm,
  przygotowuje drzewo źródłowe, a następnie uruchamia tylko test live harnessu Codex.
- Docker domyślnie włącza sondy obrazu oraz MCP/tool. Ustaw
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` lub
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0`, gdy potrzebujesz węższego uruchomienia debugowego.
- Docker eksportuje również `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, zgodnie z konfiguracją testu live, aby fallback `openai-codex/*` lub PI nie mógł ukryć regresji harnessu Codex.

### Zalecane recepty live

Wąskie, jawne allowlisty są najszybsze i najmniej podatne na niestabilność:

- Pojedynczy model, bezpośrednio (bez Gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Pojedynczy model, smoke Gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Wywoływanie narzędzi u kilku dostawców:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Skupienie na Google (klucz API Gemini + Antigravity):
  - Gemini (klucz API): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Uwagi:

- `google/...` używa Gemini API (klucz API).
- `google-antigravity/...` używa mostu OAuth Antigravity (endpoint agenta w stylu Cloud Code Assist).
- `google-gemini-cli/...` używa lokalnego Gemini CLI na twojej maszynie (osobne uwierzytelnianie + niuanse narzędzi).
- Gemini API vs Gemini CLI:
  - API: OpenClaw wywołuje hostowane Gemini API Google przez HTTP (uwierzytelnianie kluczem API / profilem); to właśnie większość użytkowników ma na myśli, mówiąc „Gemini”.
  - CLI: OpenClaw wywołuje lokalny binarny plik `gemini`; ma własne uwierzytelnianie i może zachowywać się inaczej (streaming/obsługa narzędzi/rozbieżność wersji).

## Live: macierz modeli (co obejmujemy)

Nie ma stałej „listy modeli CI” (live jest opt-in), ale to są **zalecane** modele do regularnego pokrywania na maszynie deweloperskiej z kluczami.

### Nowoczesny zestaw smoke (wywoływanie narzędzi + obraz)

To jest uruchomienie „typowych modeli”, które oczekujemy utrzymać w działaniu:

- OpenAI (bez Codex): `openai/gpt-5.4` (opcjonalnie: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google (Gemini API): `google/gemini-3.1-pro-preview` oraz `google/gemini-3-flash-preview` (unikaj starszych modeli Gemini 2.x)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` oraz `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Uruchom smoke Gateway z narzędziami + obrazem:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Linia bazowa: wywoływanie narzędzi (Read + opcjonalnie Exec)

Wybierz co najmniej jeden model z każdej rodziny dostawców:

- OpenAI: `openai/gpt-5.4` (lub `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (lub `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (lub `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Opcjonalne dodatkowe pokrycie (warto mieć):

- xAI: `xai/grok-4` (lub najnowszy dostępny)
- Mistral: `mistral/`… (wybierz jeden model z włączoną obsługą „tools”, do którego masz dostęp)
- Cerebras: `cerebras/`… (jeśli masz dostęp)
- LM Studio: `lmstudio/`… (lokalnie; wywoływanie narzędzi zależy od trybu API)

### Vision: wysyłanie obrazu (załącznik → wiadomość multimodalna)

Uwzględnij co najmniej jeden model z obsługą obrazu w `OPENCLAW_LIVE_GATEWAY_MODELS` (warianty Claude/Gemini/OpenAI z obsługą vision itd.), aby przetestować sondę obrazu.

### Agregatory / alternatywne Gateway

Jeśli masz włączone klucze, obsługujemy też testowanie przez:

- OpenRouter: `openrouter/...` (setki modeli; użyj `openclaw models scan`, aby znaleźć kandydatów z obsługą narzędzi+obrazu)
- OpenCode: `opencode/...` dla Zen i `opencode-go/...` dla Go (uwierzytelnianie przez `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Więcej dostawców, których możesz uwzględnić w macierzy live (jeśli masz poświadczenia/konfigurację):

- Wbudowani: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Przez `models.providers` (własne endpointy): `minimax` (cloud/API), plus dowolny proxy zgodny z OpenAI/Anthropic (LM Studio, vLLM, LiteLLM itd.)

Wskazówka: nie próbuj wpisywać na stałe „wszystkich modeli” w dokumentacji. Autorytatywna lista to to, co `discoverModels(...)` zwraca na twojej maszynie + jakie klucze są dostępne.

## Poświadczenia (nigdy nie commituj)

Testy live wykrywają poświadczenia w ten sam sposób, co CLI. Praktyczne konsekwencje:

- Jeśli działa CLI, testy live powinny znaleźć te same klucze.
- Jeśli test live mówi „brak poświadczeń”, debuguj to tak samo, jak debugowałbyś `openclaw models list` / wybór modelu.

- Profile uwierzytelniania per agent: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (to właśnie oznaczają „profile keys” w testach live)
- Konfiguracja: `~/.openclaw/openclaw.json` (lub `OPENCLAW_CONFIG_PATH`)
- Starszy katalog stanu: `~/.openclaw/credentials/` (kopiowany do przygotowanego katalogu domowego live, jeśli istnieje, ale nie jest głównym magazynem kluczy profili)
- Lokalne uruchomienia live domyślnie kopiują aktywną konfigurację, pliki `auth-profiles.json` per agent, starszy katalog `credentials/` oraz obsługiwane zewnętrzne katalogi uwierzytelniania CLI do tymczasowego katalogu domowego testu; przygotowane katalogi domowe live pomijają `workspace/` i `sandboxes/`, a nadpisania ścieżek `agents.*.workspace` / `agentDir` są usuwane, aby sondy nie działały w twoim rzeczywistym obszarze roboczym hosta.

Jeśli chcesz polegać na kluczach env (np. wyeksportowanych w `~/.profile`), uruchamiaj testy lokalne po `source ~/.profile` albo użyj poniższych uruchamiaczy Docker (mogą montować `~/.profile` do kontenera).

## Live: Deepgram (transkrypcja audio)

- Test: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Włączanie: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live: plan kodowania BytePlus

- Test: `src/agents/byteplus.live.test.ts`
- Włączanie: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Opcjonalne nadpisanie modelu: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live: media workflow ComfyUI

- Test: `extensions/comfy/comfy.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Zakres:
  - Testuje bundlowane ścieżki obrazu, wideo i `music_generate` comfy
  - Pomija każdą możliwość, jeśli `models.providers.comfy.<capability>` nie jest skonfigurowane
  - Przydatne po zmianach w wysyłaniu workflow comfy, odpytywaniu, pobieraniu lub rejestracji Plugin

## Live: generowanie obrazów

- Test: `src/image-generation/runtime.live.test.ts`
- Polecenie: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Zakres:
  - Wylicza każdy zarejestrowany Plugin dostawcy generowania obrazów
  - Ładuje brakujące zmienne env dostawców z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa aktywnych/env kluczy API przed zapisanymi profilami uwierzytelniania, aby nieaktualne klucze testowe w `auth-profiles.json` nie maskowały rzeczywistych poświadczeń powłoki
  - Pomija dostawców bez użytecznego uwierzytelniania/profilu/modelu
  - Uruchamia standardowe warianty generowania obrazów przez współdzieloną możliwość runtime:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Obecnie objęci bundlowani dostawcy:
  - `openai`
  - `google`
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie z magazynu profili i ignorować nadpisania tylko z env

## Live: generowanie muzyki

- Test: `extensions/music-generation-providers.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Zakres:
  - Testuje współdzieloną bundlowaną ścieżkę dostawcy generowania muzyki
  - Obecnie obejmuje Google i MiniMax
  - Ładuje zmienne env dostawców z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa aktywnych/env kluczy API przed zapisanymi profilami uwierzytelniania, aby nieaktualne klucze testowe w `auth-profiles.json` nie maskowały rzeczywistych poświadczeń powłoki
  - Pomija dostawców bez użytecznego uwierzytelniania/profilu/modelu
  - Uruchamia oba zadeklarowane tryby runtime, gdy są dostępne:
    - `generate` z wejściem opartym wyłącznie na prompcie
    - `edit`, gdy dostawca deklaruje `capabilities.edit.enabled`
  - Obecne pokrycie współdzielonej linii:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: osobny plik live Comfy, nie ten współdzielony przegląd
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie z magazynu profili i ignorować nadpisania tylko z env

## Live: generowanie wideo

- Test: `extensions/video-generation-providers.live.test.ts`
- Włączanie: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Zakres:
  - Testuje współdzieloną bundlowaną ścieżkę dostawcy generowania wideo
  - Ładuje zmienne env dostawców z twojej powłoki logowania (`~/.profile`) przed sondowaniem
  - Domyślnie używa aktywnych/env kluczy API przed zapisanymi profilami uwierzytelniania, aby nieaktualne klucze testowe w `auth-profiles.json` nie maskowały rzeczywistych poświadczeń powłoki
  - Pomija dostawców bez użytecznego uwierzytelniania/profilu/modelu
  - Uruchamia oba zadeklarowane tryby runtime, gdy są dostępne:
    - `generate` z wejściem opartym wyłącznie na prompcie
    - `imageToVideo`, gdy dostawca deklaruje `capabilities.imageToVideo.enabled` i wybrany dostawca/model akceptuje wejście lokalnego obrazu oparte na buforze we współdzielonym przeglądzie
    - `videoToVideo`, gdy dostawca deklaruje `capabilities.videoToVideo.enabled` i wybrany dostawca/model akceptuje wejście lokalnego wideo oparte na buforze we współdzielonym przeglądzie
  - Obecni zadeklarowani, ale pomijani dostawcy `imageToVideo` we współdzielonym przeglądzie:
    - `vydra`, ponieważ bundlowany `veo3` jest tylko tekstowy, a bundlowany `kling` wymaga zdalnego adresu URL obrazu
  - Pokrycie Vydra specyficzne dla dostawcy:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - ten plik uruchamia `veo3` text-to-video oraz linię `kling`, która domyślnie używa fixture zdalnego adresu URL obrazu
  - Obecne pokrycie live `videoToVideo`:
    - tylko `runway`, gdy wybrany model to `runway/gen4_aleph`
  - Obecni zadeklarowani, ale pomijani dostawcy `videoToVideo` we współdzielonym przeglądzie:
    - `alibaba`, `qwen`, `xai`, ponieważ te ścieżki obecnie wymagają zdalnych referencyjnych adresów URL `http(s)` / MP4
    - `google`, ponieważ obecna współdzielona linia Gemini/Veo używa lokalnego wejścia opartego na buforze i ta ścieżka nie jest akceptowana we współdzielonym przeglądzie
    - `openai`, ponieważ obecna współdzielona linia nie gwarantuje organizacyjnego dostępu do video inpaint/remix
- Opcjonalne zawężanie:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- Opcjonalne zachowanie uwierzytelniania:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby wymusić uwierzytelnianie z magazynu profili i ignorować nadpisania tylko z env

## Harness live dla mediów

- Polecenie: `pnpm test:live:media`
- Cel:
  - Uruchamia współdzielone pakiety live dla obrazów, muzyki i wideo przez jedno natywne wejście repozytorium
  - Automatycznie ładuje brakujące zmienne env dostawców z `~/.profile`
  - Domyślnie automatycznie zawęża każdy pakiet do dostawców, którzy aktualnie mają użyteczne uwierzytelnianie
  - Ponownie używa `scripts/test-live.mjs`, więc zachowanie Heartbeat i trybu cichego pozostaje spójne
- Przykłady:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Uruchamiacze Docker (opcjonalne testy „działa w Linux”) 

Te uruchamiacze Docker dzielą się na dwie kategorie:

- Uruchamiacze live-model: `test:docker:live-models` i `test:docker:live-gateway` uruchamiają tylko odpowiadający im plik live z kluczami profili wewnątrz obrazu Docker repozytorium (`src/agents/models.profiles.live.test.ts` i `src/gateway/gateway-models.profiles.live.test.ts`), montując lokalny katalog konfiguracji i obszar roboczy (oraz pobierając `~/.profile`, jeśli jest zamontowany). Odpowiadające im lokalne punkty wejścia to `test:live:models-profiles` i `test:live:gateway-profiles`.
- Uruchamiacze Docker live domyślnie używają mniejszego limitu smoke, aby pełny przegląd Docker pozostawał praktyczny:
  `test:docker:live-models` domyślnie ustawia `OPENCLAW_LIVE_MAX_MODELS=12`, a
  `test:docker:live-gateway` domyślnie ustawia `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000` oraz
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Nadpisz te zmienne env, gdy
  celowo chcesz większego, wyczerpującego przeglądu.
- `test:docker:all` buduje obraz Docker live raz przez `test:docker:live-build`, a następnie ponownie używa go dla dwóch linii Docker live.
- Uruchamiacze smoke kontenerów: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels` oraz `test:docker:plugins` uruchamiają jeden lub więcej rzeczywistych kontenerów i weryfikują ścieżki integracji wyższego poziomu.

Uruchamiacze Docker live-model montują też tylko potrzebne katalogi domowe uwierzytelniania CLI (albo wszystkie obsługiwane, gdy uruchomienie nie jest zawężone), a następnie kopiują je do katalogu domowego kontenera przed uruchomieniem, aby zewnętrzny OAuth CLI mógł odświeżać tokeny bez modyfikowania magazynu uwierzytelniania hosta:

- Bezpośrednie modele: `pnpm test:docker:live-models` (skrypt: `scripts/test-live-models-docker.sh`)
- Smoke powiązania ACP: `pnpm test:docker:live-acp-bind` (skrypt: `scripts/test-live-acp-bind-docker.sh`)
- Smoke backendu CLI: `pnpm test:docker:live-cli-backend` (skrypt: `scripts/test-live-cli-backend-docker.sh`)
- Smoke harnessu app-server Codex: `pnpm test:docker:live-codex-harness` (skrypt: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + agent developerski: `pnpm test:docker:live-gateway` (skrypt: `scripts/test-live-gateway-models-docker.sh`)
- Smoke live Open WebUI: `pnpm test:docker:openwebui` (skrypt: `scripts/e2e/openwebui-docker.sh`)
- Kreator onboardingu (TTY, pełne scaffoldowanie): `pnpm test:docker:onboard` (skrypt: `scripts/e2e/onboard-docker.sh`)
- Sieć Gateway (dwa kontenery, uwierzytelnianie WS + health): `pnpm test:docker:gateway-network` (skrypt: `scripts/e2e/gateway-network-docker.sh`)
- Most kanałów MCP (seedowany Gateway + most stdio + smoke surowej ramki powiadomień Claude): `pnpm test:docker:mcp-channels` (skrypt: `scripts/e2e/mcp-channels-docker.sh`)
- Pluginy (smoke instalacji + alias `/plugin` + semantyka restartu bundla Claude): `pnpm test:docker:plugins` (skrypt: `scripts/e2e/plugins-docker.sh`)

Uruchamiacze Docker live-model montują też bieżący checkout tylko do odczytu i
przygotowują go w tymczasowym katalogu roboczym wewnątrz kontenera. Dzięki temu obraz runtime
pozostaje lekki, a jednocześnie Vitest działa na dokładnie twojej lokalnej konfiguracji/źródłach.
Krok przygotowania pomija duże lokalne cache oraz wyniki buildów aplikacji, takie jak
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__` oraz lokalne dla aplikacji katalogi `.build` lub
wyjścia Gradle, dzięki czemu uruchomienia Docker live nie tracą minut na kopiowanie
artefaktów specyficznych dla maszyny.
Ustawiają też `OPENCLAW_SKIP_CHANNELS=1`, aby aktywne sondy Gateway nie uruchamiały
rzeczywistych workerów kanałów Telegram/Discord/itd. wewnątrz kontenera.
`test:docker:live-models` nadal uruchamia `pnpm test:live`, więc przekazuj także
`OPENCLAW_LIVE_GATEWAY_*`, gdy chcesz zawęzić lub wykluczyć pokrycie Gateway
live z tej linii Docker.
`test:docker:openwebui` jest smoke zgodności wyższego poziomu: uruchamia
kontener Gateway OpenClaw z włączonymi endpointami HTTP zgodnymi z OpenAI,
uruchamia przypięty kontener Open WebUI przeciwko temu Gateway, loguje się przez
Open WebUI, weryfikuje, że `/api/models` udostępnia `openclaw/default`, a następnie wysyła
rzeczywiste żądanie czatu przez proxy `/api/chat/completions` Open WebUI.
Pierwsze uruchomienie może być zauważalnie wolniejsze, ponieważ Docker może potrzebować pobrać
obraz Open WebUI, a samo Open WebUI może potrzebować dokończyć własną konfigurację cold-start.
Ta linia oczekuje użytecznego klucza modelu live, a `OPENCLAW_PROFILE_FILE`
(domyślnie `~/.profile`) jest podstawowym sposobem jego dostarczenia w uruchomieniach konteneryzowanych.
Udane uruchomienia wypisują mały payload JSON, taki jak `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` jest celowo deterministyczny i nie wymaga
rzeczywistego konta Telegram, Discord ani iMessage. Uruchamia seedowany kontener
Gateway, startuje drugi kontener uruchamiający `openclaw mcp serve`, a następnie
weryfikuje wykrywanie routowanych rozmów, odczyty transkryptów, metadane załączników,
zachowanie kolejki zdarzeń live, routing wysyłania wychodzącego oraz powiadomienia
w stylu Claude dla kanałów + uprawnień przez rzeczywisty most stdio MCP. Kontrola powiadomień
sprawdza bezpośrednio surowe ramki stdio MCP, dzięki czemu smoke weryfikuje to, co
most rzeczywiście emituje, a nie tylko to, co akurat ujawnia określony klient SDK.

Ręczny smoke wątku ACP w plain language (nie w CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Zachowaj ten skrypt do przepływów pracy regresji/debugowania. Może być znów potrzebny do walidacji routingu wątków ACP, więc go nie usuwaj.

Przydatne zmienne env:

- `OPENCLAW_CONFIG_DIR=...` (domyślnie: `~/.openclaw`) montowane do `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (domyślnie: `~/.openclaw/workspace`) montowane do `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (domyślnie: `~/.profile`) montowane do `/home/node/.profile` i pobierane przed uruchomieniem testów
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (domyślnie: `~/.cache/openclaw/docker-cli-tools`) montowane do `/home/node/.npm-global` dla cache’owanych instalacji CLI wewnątrz Docker
- Zewnętrzne katalogi/pliki uwierzytelniania CLI pod `$HOME` są montowane tylko do odczytu pod `/host-auth...`, a następnie kopiowane do `/home/node/...` przed rozpoczęciem testów
  - Domyślne katalogi: `.minimax`
  - Domyślne pliki: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Zawężone uruchomienia dostawców montują tylko potrzebne katalogi/pliki wywnioskowane z `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Ręczne nadpisanie: `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none` lub lista rozdzielana przecinkami, np. `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`, aby zawęzić uruchomienie
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`, aby filtrować dostawców wewnątrz kontenera
- `OPENCLAW_SKIP_DOCKER_BUILD=1`, aby ponownie użyć istniejącego obrazu `openclaw:local-live` przy ponownych uruchomieniach, które nie wymagają przebudowy
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`, aby upewnić się, że poświadczenia pochodzą z magazynu profili (a nie z env)
- `OPENCLAW_OPENWEBUI_MODEL=...`, aby wybrać model udostępniany przez Gateway dla smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...`, aby nadpisać prompt sprawdzania nonce używany przez smoke Open WebUI
- `OPENWEBUI_IMAGE=...`, aby nadpisać przypięty tag obrazu Open WebUI

## Kontrola poprawności dokumentacji

Po edycjach dokumentacji uruchom sprawdzenia dokumentacji: `pnpm check:docs`.
Uruchom pełną walidację anchorów Mintlify, gdy potrzebujesz także sprawdzania nagłówków w obrębie strony: `pnpm docs:check-links:anchors`.

## Regresje offline (bezpieczne dla CI)

To regresje „rzeczywistego pipeline” bez rzeczywistych dostawców:

- Wywoływanie narzędzi Gateway (mock OpenAI, rzeczywisty Gateway + pętla agenta): `src/gateway/gateway.test.ts` (przypadek: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Kreator Gateway (WS `wizard.start`/`wizard.next`, wymuszone zapisywanie konfiguracji + auth): `src/gateway/gateway.test.ts` (przypadek: "runs wizard over ws and writes auth token config")

## Ewaluacje niezawodności agenta (Skills)

Mamy już kilka testów bezpiecznych dla CI, które zachowują się jak „ewaluacje niezawodności agenta”:

- Mock wywoływania narzędzi przez rzeczywistą pętlę Gateway + agenta (`src/gateway/gateway.test.ts`).
- Przepływy kreatora end-to-end, które walidują okablowanie sesji i efekty konfiguracji (`src/gateway/gateway.test.ts`).

Czego nadal brakuje dla Skills (zobacz [Skills](/pl/tools/skills)):

- **Decisioning:** gdy Skills są wymienione w prompcie, czy agent wybiera właściwy Skill (albo unika nieistotnych)?
- **Compliance:** czy agent odczytuje `SKILL.md` przed użyciem i wykonuje wymagane kroki/argumenty?
- **Workflow contracts:** scenariusze wieloturowe, które sprawdzają kolejność narzędzi, przenoszenie historii sesji i granice sandboxa.

Przyszłe ewaluacje powinny najpierw pozostać deterministyczne:

- Uruchamiacz scenariuszy używający mock dostawców do sprawdzania wywołań narzędzi + kolejności, odczytów plików Skill i okablowania sesji.
- Niewielki pakiet scenariuszy skupionych na Skills (użycie vs unikanie, bramkowanie, prompt injection).
- Opcjonalne ewaluacje live (opt-in, bramkowane env) dopiero po wdrożeniu pakietu bezpiecznego dla CI.

## Testy kontraktowe (kształt Plugin i kanałów)

Testy kontraktowe weryfikują, że każdy zarejestrowany Plugin i kanał jest zgodny ze swoim
kontraktem interfejsu. Iterują po wszystkich wykrytych Plugin i uruchamiają pakiet
asercji kształtu i zachowania. Domyślna linia unit `pnpm test` celowo
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
- **outbound-payload** - Struktura payload wiadomości
- **inbound** - Obsługa wiadomości przychodzących
- **actions** - Handlery akcji kanału
- **threading** - Obsługa identyfikatorów wątków
- **directory** - API katalogu/listy
- **group-policy** - Egzekwowanie zasad grup

### Kontrakty statusu dostawców

Znajdują się w `src/plugins/contracts/*.contract.test.ts`.

- **status** - Sondy statusu kanałów
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

- Po zmianie eksportów lub subścieżek plugin-sdk
- Po dodaniu lub modyfikacji kanału albo Plugin dostawcy
- Po refaktoryzacji rejestracji lub wykrywania Plugin

Testy kontraktowe uruchamiają się w CI i nie wymagają prawdziwych kluczy API.

## Dodawanie regresji (wskazówki)

Gdy naprawiasz problem dostawcy/modelu wykryty w live:

- Jeśli to możliwe, dodaj regresję bezpieczną dla CI (mock/stub dostawcy albo przechwycenie dokładnej transformacji kształtu żądania)
- Jeśli z natury jest to problem tylko live (limity szybkości, polityki uwierzytelniania), utrzymaj test live wąski i opt-in przez zmienne env
- Preferuj celowanie w najmniejszą warstwę, która wychwytuje błąd:
  - błąd konwersji/replay żądania dostawcy → test bezpośrednich modeli
  - błąd pipeline sesji/historii/narzędzi Gateway → smoke Gateway live albo bezpieczny dla CI mock test Gateway
- Zabezpieczenie przechodzenia SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` wyprowadza jeden przykładowy cel na klasę SecretRef z metadanych rejestru (`listSecretTargetRegistryEntries()`), a następnie sprawdza, że identyfikatory exec segmentów przechodzenia są odrzucane.
  - Jeśli dodajesz nową rodzinę celów SecretRef `includeInPlan` w `src/secrets/target-registry-data.ts`, zaktualizuj `classifyTargetClass` w tym teście. Test celowo kończy się błędem przy niesklasyfikowanych identyfikatorach celów, aby nowe klasy nie mogły zostać pominięte po cichu.
