---
read_when:
    - Tworzenie lub debugowanie natywnych wtyczek OpenClaw
    - Zrozumienie modelu capabilities wtyczek lub granic własności
    - Praca nad pipeline ładowania wtyczek lub rejestrem
    - Implementowanie hooków środowiska wykonawczego dostawcy lub wtyczek kanałów
sidebarTitle: Internals
summary: 'Wnętrze wtyczek: model capabilities, własność, kontrakty, pipeline ładowania i pomocniki środowiska wykonawczego'
title: Wnętrze wtyczek
x-i18n:
    generated_at: "2026-04-06T03:13:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: d39158455701dedfb75f6c20b8c69fd36ed9841f1d92bed1915f448df57fd47b
    source_path: plugins/architecture.md
    workflow: 15
---

# Wnętrze wtyczek

<Info>
  To jest **szczegółowa dokumentacja architektury**. Praktyczne przewodniki znajdziesz tutaj:
  - [Instalowanie i używanie wtyczek](/pl/tools/plugin) — przewodnik użytkownika
  - [Pierwsze kroki](/pl/plugins/building-plugins) — pierwszy samouczek tworzenia wtyczki
  - [Wtyczki kanałów](/pl/plugins/sdk-channel-plugins) — tworzenie kanału wiadomości
  - [Wtyczki dostawców](/pl/plugins/sdk-provider-plugins) — tworzenie dostawcy modeli
  - [Przegląd SDK](/pl/plugins/sdk-overview) — mapa importów i API rejestracji
</Info>

Ta strona opisuje wewnętrzną architekturę systemu wtyczek OpenClaw.

## Publiczny model capabilities

Capabilities to publiczny model **natywnych wtyczek** wewnątrz OpenClaw. Każda
natywna wtyczka OpenClaw rejestruje się względem jednego lub większej liczby typów capability:

| Capability             | Metoda rejestracji                              | Przykładowe wtyczki                  |
| ---------------------- | ----------------------------------------------- | ------------------------------------ |
| Wnioskowanie tekstowe  | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| Mowa                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| Transkrypcja realtime  | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Głos realtime          | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| Rozumienie multimediów | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Generowanie obrazów    | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Generowanie muzyki     | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| Generowanie wideo      | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Pobieranie z sieci     | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Wyszukiwanie w sieci   | `api.registerWebSearchProvider(...)`             | `google`                             |
| Kanał / wiadomości     | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Wtyczka, która rejestruje zero capabilities, ale dostarcza hooki, narzędzia lub
usługi, jest wtyczką **legacy hook-only**. Ten wzorzec jest nadal w pełni obsługiwany.

### Stanowisko wobec zgodności zewnętrznej

Model capability jest już wdrożony w rdzeniu i używany dziś przez dołączone/natywne wtyczki,
ale zgodność zewnętrznych wtyczek nadal wymaga wyższego progu niż „jest
eksportowane, więc jest zamrożone”.

Obecne wskazówki:

- **istniejące wtyczki zewnętrzne:** utrzymuj integracje oparte na hookach; traktuj
  to jako bazowy poziom zgodności
- **nowe dołączone/natywne wtyczki:** preferuj jawną rejestrację capabilities zamiast
  sięgania do elementów zależnych od dostawcy lub nowych projektów typu hook-only
- **zewnętrzne wtyczki przyjmujące rejestrację capabilities:** dozwolone, ale traktuj
  powierzchnie pomocnicze specyficzne dla capability jako rozwijające się, chyba że dokumentacja
  wyraźnie oznacza dany kontrakt jako stabilny

Praktyczna zasada:

- API rejestracji capabilities to zamierzony kierunek
- legacy hooks pozostają najbezpieczniejszą ścieżką bez ryzyka naruszenia zgodności dla zewnętrznych wtyczek w czasie
  przejścia
- eksportowane podścieżki pomocnicze nie są sobie równe; preferuj wąski udokumentowany
  kontrakt, a nie przypadkowe eksporty pomocnicze

### Kształty wtyczek

OpenClaw klasyfikuje każdą załadowaną wtyczkę do określonego kształtu na podstawie jej rzeczywistego
zachowania rejestracyjnego (a nie tylko statycznych metadanych):

- **plain-capability** -- rejestruje dokładnie jeden typ capability (na przykład
  wtyczka tylko dostawcy, taka jak `mistral`)
- **hybrid-capability** -- rejestruje wiele typów capability (na przykład
  `openai` obsługuje wnioskowanie tekstowe, mowę, rozumienie multimediów i generowanie
  obrazów)
- **hook-only** -- rejestruje wyłącznie hooki (typowane lub niestandardowe), bez capabilities,
  narzędzi, poleceń ani usług
- **non-capability** -- rejestruje narzędzia, polecenia, usługi lub trasy, ale bez
  capabilities

Użyj `openclaw plugins inspect <id>`, aby zobaczyć kształt wtyczki i rozkład
capabilities. Szczegóły znajdziesz w [Dokumentacja CLI](/cli/plugins#inspect).

### Legacy hooks

Hook `before_agent_start` pozostaje obsługiwany jako ścieżka zgodności dla
wtyczek hook-only. Rzeczywiste starsze wtyczki nadal od niego zależą.

Kierunek:

- utrzymywać działanie
- dokumentować jako legacy
- preferować `before_model_resolve` przy pracy nad nadpisywaniem modelu/dostawcy
- preferować `before_prompt_build` przy mutowaniu promptów
- usuwać dopiero wtedy, gdy rzeczywiste użycie spadnie, a pokrycie fixture’ów potwierdzi bezpieczeństwo migracji

### Sygnały zgodności

Gdy uruchamiasz `openclaw doctor` albo `openclaw plugins inspect <id>`, możesz zobaczyć
jedną z tych etykiet:

| Sygnał                     | Znaczenie                                                   |
| -------------------------- | ----------------------------------------------------------- |
| **config valid**           | Konfiguracja poprawnie się parsuje i wtyczki są rozpoznawane |
| **compatibility advisory** | Wtyczka używa obsługiwanego, ale starszego wzorca (np. `hook-only`) |
| **legacy warning**         | Wtyczka używa `before_agent_start`, które jest przestarzałe |
| **hard error**             | Konfiguracja jest nieprawidłowa albo wtyczki nie udało się załadować |

Ani `hook-only`, ani `before_agent_start` nie zepsują dziś twojej wtyczki --
`hook-only` ma charakter informacyjny, a `before_agent_start` powoduje tylko ostrzeżenie. Te
sygnały pojawiają się również w `openclaw status --all` i `openclaw plugins doctor`.

## Przegląd architektury

System wtyczek OpenClaw ma cztery warstwy:

1. **Manifest + wykrywanie**
   OpenClaw znajduje kandydatów na wtyczki w skonfigurowanych ścieżkach, katalogach głównych workspace,
   globalnych katalogach rozszerzeń i dołączonych rozszerzeniach. Wykrywanie najpierw odczytuje natywne
   manifesty `openclaw.plugin.json` oraz obsługiwane manifesty bundle.
2. **Włączanie + walidacja**
   Rdzeń decyduje, czy wykryta wtyczka jest włączona, wyłączona, zablokowana, czy
   wybrana do wyłącznego slotu, takiego jak pamięć.
3. **Ładowanie w czasie działania**
   Natywne wtyczki OpenClaw są ładowane w tym samym procesie przez jiti i rejestrują
   capabilities w centralnym rejestrze. Zgodne bundle są normalizowane do
   rekordów rejestru bez importowania kodu środowiska wykonawczego.
4. **Konsumpcja powierzchni**
   Pozostała część OpenClaw odczytuje rejestr, aby udostępnić narzędzia, kanały, konfigurację
   dostawców, hooki, trasy HTTP, polecenia CLI i usługi.

W szczególności dla CLI wtyczek, wykrywanie poleceń głównych jest podzielone na dwie fazy:

- metadane czasu parsowania pochodzą z `registerCli(..., { descriptors: [...] })`
- rzeczywisty moduł CLI wtyczki może pozostać leniwy i zarejestrować się przy pierwszym wywołaniu

Dzięki temu kod CLI należący do wtyczki pozostaje wewnątrz wtyczki, a OpenClaw nadal może
zarezerwować nazwy poleceń głównych przed parsowaniem.

Ważna granica projektowa:

- wykrywanie + walidacja konfiguracji powinny działać na podstawie **manifestu/metadanych schematu**
  bez wykonywania kodu wtyczki
- natywne zachowanie w czasie działania pochodzi ze ścieżki `register(api)` modułu wtyczki

Ten podział pozwala OpenClaw walidować konfigurację, wyjaśniać brakujące/wyłączone wtyczki i
budować podpowiedzi UI/schematu, zanim pełne środowisko wykonawcze stanie się aktywne.

### Wtyczki kanałów i współdzielone narzędzie wiadomości

Wtyczki kanałów nie muszą rejestrować osobnego narzędzia send/edit/react dla
zwykłych akcji czatu. OpenClaw utrzymuje jedno współdzielone narzędzie `message` w rdzeniu, a
wtyczki kanałów odpowiadają za specyficzne dla kanału wykrywanie i wykonywanie za nim.

Obecna granica wygląda tak:

- rdzeń odpowiada za host współdzielonego narzędzia `message`, połączenie z promptami, księgowanie sesji/wątków
  oraz dyspozycję wykonania
- wtyczki kanałów odpowiadają za wykrywanie działań w zakresie, wykrywanie capabilities i
  wszelkie fragmenty schematu specyficzne dla kanału
- wtyczki kanałów odpowiadają za gramatykę konwersacji sesji specyficzną dla dostawcy, taką jak
  sposób kodowania identyfikatorów konwersacji przez identyfikatory wątków lub dziedziczenia z konwersacji nadrzędnych
- wtyczki kanałów wykonują końcową akcję przez swój adapter akcji

Dla wtyczek kanałów powierzchnią SDK jest
`ChannelMessageActionAdapter.describeMessageTool(...)`. To ujednolicone wywołanie wykrywania
pozwala wtyczce zwrócić razem widoczne akcje, capabilities i wkład do schematu,
aby te elementy nie rozjeżdżały się z czasem.

Rdzeń przekazuje zakres środowiska wykonawczego do tego kroku wykrywania. Ważne pola obejmują:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- zaufany przychodzący `requesterSenderId`

To ma znaczenie dla wtyczek zależnych od kontekstu. Kanał może ukrywać lub ujawniać
akcje wiadomości na podstawie aktywnego konta, bieżącego pokoju/wątku/wiadomości albo
zaufanej tożsamości żądającego nadawcy bez zakodowanych na sztywno gałęzi specyficznych dla kanału w
narzędziu rdzenia `message`.

Dlatego zmiany routingu embedded-runner nadal należą do pracy nad wtyczką: runner
odpowiada za przekazanie bieżącej tożsamości czatu/sesji do granicy wykrywania wtyczki, tak aby
współdzielone narzędzie `message` ujawniało właściwą powierzchnię należącą do kanału
dla bieżącej tury.

Jeśli chodzi o pomocniki wykonania należące do kanału, dołączone wtyczki powinny utrzymywać środowisko wykonawcze
we własnych modułach rozszerzeń. Rdzeń nie odpowiada już za środowiska wykonawcze akcji wiadomości
Discord, Slack, Telegram ani WhatsApp w `src/agents/tools`.
Nie publikujemy osobnych podścieżek `plugin-sdk/*-action-runtime`, a dołączone
wtyczki powinny importować swój własny lokalny kod środowiska wykonawczego bezpośrednio z
modułów należących do rozszerzenia.

Ta sama granica dotyczy ogólnie nazwanych przez dostawcę szczelin SDK: rdzeń nie powinien
importować wygodnych barrelów specyficznych dla kanałów dla Slack, Discord, Signal,
WhatsApp ani podobnych rozszerzeń. Jeśli rdzeń potrzebuje jakiegoś zachowania, powinien albo użyć
własnego barrela `api.ts` / `runtime-api.ts` dołączonej wtyczki, albo przenieść tę potrzebę
do wąskiej ogólnej capability we współdzielonym SDK.

W szczególności dla ankiet istnieją dwie ścieżki wykonania:

- `outbound.sendPoll` to współdzielona baza dla kanałów pasujących do wspólnego
  modelu ankiet
- `actions.handleAction("poll")` to preferowana ścieżka dla semantyki ankiet specyficznej dla kanału
  lub dodatkowych parametrów ankiet

Rdzeń odkłada teraz współdzielone parsowanie ankiet do momentu, gdy dyspozycja ankiety przez wtyczkę
odrzuci akcję, dzięki czemu procedury obsługi ankiet należące do wtyczki mogą akceptować pola ankiet
specyficzne dla kanału bez wcześniejszego blokowania przez ogólny parser ankiet.

Pełną sekwencję uruchamiania znajdziesz w sekcji [Pipeline ładowania](#load-pipeline).

## Model własności capabilities

OpenClaw traktuje natywną wtyczkę jako granicę własności dla **firmy** lub
**funkcji**, a nie jako worek niepowiązanych integracji.

To oznacza, że:

- wtyczka firmy powinna zwykle posiadać wszystkie powierzchnie OpenClaw-facing tej firmy
- wtyczka funkcji powinna zwykle posiadać pełną powierzchnię funkcji, którą wprowadza
- kanały powinny wykorzystywać współdzielone capabilities rdzenia zamiast ad hoc
  ponownie implementować zachowanie dostawców

Przykłady:

- dołączona wtyczka `openai` odpowiada za zachowanie dostawcy modeli OpenAI oraz
  zachowanie OpenAI dla mowy + realtime-voice + media-understanding + image-generation
- dołączona wtyczka `elevenlabs` odpowiada za zachowanie mowy ElevenLabs
- dołączona wtyczka `microsoft` odpowiada za zachowanie mowy Microsoft
- dołączona wtyczka `google` odpowiada za zachowanie dostawcy modeli Google oraz Google
  media-understanding + image-generation + web-search
- dołączona wtyczka `firecrawl` odpowiada za zachowanie web-fetch Firecrawl
- dołączone wtyczki `minimax`, `mistral`, `moonshot` i `zai` odpowiadają za swoje
  backendy media-understanding
- wtyczka `voice-call` jest wtyczką funkcji: odpowiada za transport połączeń, narzędzia,
  CLI, trasy i mostkowanie strumieni mediów Twilio, ale korzysta ze współdzielonych capabilities
  mowy oraz realtime-transcription i realtime-voice zamiast bezpośrednio importować wtyczki dostawców

Zamierzony stan docelowy to:

- OpenAI żyje w jednej wtyczce nawet wtedy, gdy obejmuje modele tekstowe, mowę, obrazy i
  przyszłe wideo
- inny dostawca może zrobić to samo dla własnego obszaru
- kanały nie interesują się tym, która wtyczka dostawcy posiada danego dostawcę; korzystają z
  kontraktu współdzielonej capability udostępnionego przez rdzeń

To kluczowe rozróżnienie:

- **wtyczka** = granica własności
- **capability** = kontrakt rdzenia, który wiele wtyczek może implementować lub wykorzystywać

Dlatego jeśli OpenClaw doda nową domenę, taką jak wideo, pierwsze pytanie nie brzmi
„który dostawca powinien na sztywno zakodować obsługę wideo?”. Pierwsze pytanie brzmi „jaki jest
kontrakt capability wideo w rdzeniu?”. Gdy taki kontrakt istnieje, wtyczki dostawców
mogą się wobec niego rejestrować, a wtyczki kanałów/funkcji mogą z niego korzystać.

Jeśli capability jeszcze nie istnieje, właściwy ruch to zwykle:

1. zdefiniować brakującą capability w rdzeniu
2. udostępnić ją przez API/runtime wtyczek w sposób typowany
3. podłączyć kanały/funkcje do tej capability
4. pozwolić wtyczkom dostawców zarejestrować implementacje

To utrzymuje jawną własność, jednocześnie unikając zachowania rdzenia zależnego od
jednego dostawcy albo jednorazowej ścieżki kodu specyficznej dla wtyczki.

### Warstwowanie capabilities

Używaj tego modelu myślowego przy decydowaniu, gdzie powinien znajdować się kod:

- **warstwa capabilities rdzenia**: współdzielona orkiestracja, polityka, fallback, reguły scalania konfiguracji,
  semantyka dostarczania i typowane kontrakty
- **warstwa wtyczki dostawcy**: API specyficzne dla dostawcy, auth, katalogi modeli, synteza mowy,
  generowanie obrazów, przyszłe backendy wideo, endpointy zużycia
- **warstwa wtyczki kanału/funkcji**: integracja Slack/Discord/voice-call/etc.,
  która korzysta z capabilities rdzenia i prezentuje je na danej powierzchni

Na przykład TTS ma następujący kształt:

- rdzeń odpowiada za politykę TTS w czasie odpowiedzi, kolejność fallbacków, preferencje i dostarczanie kanałowe
- `openai`, `elevenlabs` i `microsoft` odpowiadają za implementacje syntezy
- `voice-call` korzysta z pomocnika runtime TTS dla telefonii

Ten sam wzorzec należy preferować dla przyszłych capabilities.

### Przykład firmowej wtyczki z wieloma capabilities

Firmowa wtyczka powinna z zewnątrz sprawiać wrażenie spójnej. Jeśli OpenClaw ma współdzielone
kontrakty dla modeli, mowy, transkrypcji realtime, głosu realtime, rozumienia multimediów,
generowania obrazów, generowania wideo, web fetch i web search,
dostawca może posiadać wszystkie swoje powierzchnie w jednym miejscu:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Znaczenie ma nie tyle dokładna nazwa pomocników. Znaczenie ma kształt:

- jedna wtyczka odpowiada za powierzchnię dostawcy
- rdzeń nadal odpowiada za kontrakty capabilities
- kanały i wtyczki funkcji korzystają z pomocników `api.runtime.*`, a nie z kodu dostawcy
- testy kontraktowe mogą sprawdzać, czy wtyczka zarejestrowała capabilities, za które
  twierdzi, że odpowiada

### Przykład capability: rozumienie wideo

OpenClaw już traktuje rozumienie obrazu/audio/wideo jako jedną współdzieloną
capability. Ten sam model własności obowiązuje także tutaj:

1. rdzeń definiuje kontrakt media-understanding
2. wtyczki dostawców rejestrują `describeImage`, `transcribeAudio` i
   `describeVideo`, jeśli ma to zastosowanie
3. kanały i wtyczki funkcji korzystają ze współdzielonego zachowania rdzenia zamiast
   łączyć się bezpośrednio z kodem dostawcy

To zapobiega wbudowywaniu założeń jednego dostawcy dotyczących wideo w rdzeń. Wtyczka posiada
powierzchnię dostawcy; rdzeń posiada kontrakt capability i zachowanie fallback.

Generowanie wideo już używa tej samej sekwencji: rdzeń posiada typowany
kontrakt capability i pomocnik runtime, a wtyczki dostawców rejestrują
implementacje `api.registerVideoGenerationProvider(...)`.

Potrzebujesz konkretnej listy wdrożeniowej? Zobacz
[Capability Cookbook](/pl/plugins/architecture).

## Kontrakty i egzekwowanie

Powierzchnia API wtyczek jest celowo typowana i scentralizowana w
`OpenClawPluginApi`. Ten kontrakt definiuje obsługiwane punkty rejestracji i
pomocniki runtime, na których może polegać wtyczka.

Dlaczego to ważne:

- autorzy wtyczek dostają jeden stabilny wewnętrzny standard
- rdzeń może odrzucać duplikaty własności, takie jak dwie wtyczki rejestrujące ten sam
  identyfikator dostawcy
- przy uruchamianiu można wyświetlić przydatną diagnostykę dla nieprawidłowej rejestracji
- testy kontraktowe mogą egzekwować własność dołączonych wtyczek i zapobiegać cichemu dryfowi

Istnieją dwie warstwy egzekwowania:

1. **egzekwowanie rejestracji w czasie działania**
   Rejestr wtyczek waliduje rejestracje podczas ładowania wtyczek. Przykłady:
   zduplikowane identyfikatory dostawców, zduplikowane identyfikatory dostawców mowy oraz nieprawidłowe
   rejestracje powodują diagnostykę wtyczek zamiast niezdefiniowanego zachowania.
2. **testy kontraktowe**
   Dołączone wtyczki są przechwytywane w rejestrach kontraktów podczas uruchamiania testów, dzięki czemu
   OpenClaw może jawnie sprawdzać własność. Dziś jest to używane dla dostawców modeli,
   dostawców mowy, dostawców web search i własności rejestracji dołączonych wtyczek.

Praktyczny efekt jest taki, że OpenClaw z góry wie, która wtyczka odpowiada za którą
powierzchnię. Dzięki temu rdzeń i kanały mogą płynnie się składać, ponieważ własność jest
zadeklarowana, typowana i testowalna, a nie domyślna.

### Co należy do kontraktu

Dobre kontrakty wtyczek są:

- typowane
- małe
- specyficzne dla capability
- należące do rdzenia
- wielokrotnego użytku przez wiele wtyczek
- konsumowalne przez kanały/funkcje bez wiedzy o dostawcy

Złe kontrakty wtyczek to:

- polityka specyficzna dla dostawcy ukryta w rdzeniu
- jednorazowe furtki dla wtyczek omijające rejestr
- kod kanału sięgający bezpośrednio do implementacji dostawcy
- doraźne obiekty runtime, które nie są częścią `OpenClawPluginApi` ani
  `api.runtime`

W razie wątpliwości podnieś poziom abstrakcji: najpierw zdefiniuj capability, a potem
pozwól wtyczkom się do niej podłączać.

## Model wykonania

Natywne wtyczki OpenClaw działają **w tym samym procesie** co Gateway. Nie są
sandboxowane. Załadowana natywna wtyczka ma tę samą granicę zaufania na poziomie procesu co
kod rdzenia.

Konsekwencje:

- natywna wtyczka może rejestrować narzędzia, handlery sieciowe, hooki i usługi
- błąd natywnej wtyczki może zawiesić lub zdestabilizować gateway
- złośliwa natywna wtyczka jest równoważna dowolnemu wykonaniu kodu wewnątrz
  procesu OpenClaw

Zgodne bundle są domyślnie bezpieczniejsze, ponieważ OpenClaw obecnie traktuje je
jako pakiety metadanych/treści. W bieżących wydaniach oznacza to głównie dołączone
Skills.

Dla niedołączonych wtyczek używaj allowlist i jawnych ścieżek instalacji/ładowania. Traktuj
wtyczki workspace jako kod czasu rozwoju, a nie produkcyjne ustawienia domyślne.

Dla nazw pakietów dołączonych wtyczek workspace utrzymuj identyfikator wtyczki zakotwiczony w nazwie npm:
domyślnie `@openclaw/<id>` albo zatwierdzony typowany sufiks, taki jak
`-provider`, `-plugin`, `-speech`, `-sandbox` lub `-media-understanding`, gdy
pakiet celowo udostępnia węższą rolę wtyczki.

Ważna uwaga dotycząca zaufania:

- `plugins.allow` ufa **identyfikatorom wtyczek**, a nie pochodzeniu źródła.
- Wtyczka workspace z tym samym identyfikatorem co wtyczka dołączona celowo przesłania
  dołączoną kopię, gdy ta wtyczka workspace jest włączona/na allowliście.
- To normalne i przydatne przy lokalnym rozwoju, testowaniu poprawek i hotfixach.

## Granica eksportu

OpenClaw eksportuje capabilities, a nie wygodne szczegóły implementacji.

Utrzymuj publiczną rejestrację capabilities. Ogranicz eksporty pomocnicze, które nie są kontraktami:

- podścieżki pomocnicze specyficzne dla dołączonych wtyczek
- podścieżki mechaniki runtime, które nie są przeznaczone jako publiczne API
- wygodne pomocniki specyficzne dla dostawców
- pomocniki konfiguracji/onboardingu będące szczegółami implementacji

Niektóre podścieżki pomocnicze dołączonych wtyczek nadal pozostają w wygenerowanej mapie eksportów SDK
ze względu na zgodność i utrzymanie dołączonych wtyczek. Obecne przykłady to
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` oraz kilka szczelin `plugin-sdk/matrix*`. Traktuj je jako
zastrzeżone eksporty będące szczegółami implementacji, a nie jako zalecany wzorzec SDK dla
nowych wtyczek zewnętrznych.

## Pipeline ładowania

Przy uruchamianiu OpenClaw robi w przybliżeniu to:

1. wykrywa katalogi główne kandydatów na wtyczki
2. odczytuje natywne lub zgodne manifesty bundle oraz metadane pakietów
3. odrzuca niebezpiecznych kandydatów
4. normalizuje konfigurację wtyczek (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decyduje o włączeniu dla każdego kandydata
6. ładuje włączone natywne moduły przez jiti
7. wywołuje natywne hooki `register(api)` (lub `activate(api)` — starszy alias) i zbiera rejestracje do rejestru wtyczek
8. udostępnia rejestr powierzchniom poleceń/runtime

<Note>
`activate` jest starszym aliasem dla `register` — loader rozpoznaje, który z nich jest obecny (`def.register ?? def.activate`) i wywołuje go w tym samym punkcie. Wszystkie dołączone wtyczki używają `register`; dla nowych wtyczek preferuj `register`.
</Note>

Bramki bezpieczeństwa działają **przed** wykonaniem runtime. Kandydaci są blokowani,
gdy entry wychodzi poza katalog główny wtyczki, ścieżka ma uprawnienia world-writable albo
własność ścieżki wygląda podejrzanie w przypadku wtyczek niedołączonych.

### Zachowanie manifest-first

Manifest jest źródłem prawdy control-plane. OpenClaw używa go, aby:

- zidentyfikować wtyczkę
- wykryć zadeklarowane kanały/Skills/schemat konfiguracji lub capabilities bundle
- zwalidować `plugins.entries.<id>.config`
- rozszerzyć etykiety/placeholders Control UI
- wyświetlić metadane instalacji/katalogu

Dla natywnych wtyczek moduł runtime jest częścią data-plane. Rejestruje
rzeczywiste zachowanie, takie jak hooki, narzędzia, polecenia albo przepływy dostawców.

### Co loader buforuje

OpenClaw utrzymuje krótkie bufory w procesie dla:

- wyników wykrywania
- danych rejestru manifestów
- załadowanych rejestrów wtyczek

Te bufory ograniczają skokowe obciążenie przy uruchamianiu i koszt powtarzanych poleceń. Można o nich bezpiecznie myśleć
jako o krótkotrwałych buforach wydajnościowych, a nie o trwałości.

Uwaga dotycząca wydajności:

- Ustaw `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` lub
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, aby wyłączyć te bufory.
- Dostosuj okna cache przy użyciu `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` i
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Model rejestru

Załadowane wtyczki nie mutują bezpośrednio losowych globalnych zmiennych rdzenia. Rejestrują się w
centralnym rejestrze wtyczek.

Rejestr śledzi:

- rekordy wtyczek (tożsamość, źródło, pochodzenie, status, diagnostyka)
- narzędzia
- legacy hooks i typowane hooki
- kanały
- dostawców
- handlery Gateway RPC
- trasy HTTP
- rejestratory CLI
- usługi działające w tle
- polecenia należące do wtyczek

Funkcje rdzenia odczytują następnie z tego rejestru zamiast rozmawiać bezpośrednio z modułami
wtyczek. Dzięki temu ładowanie pozostaje jednokierunkowe:

- moduł wtyczki -> rejestracja w rejestrze
- runtime rdzenia -> konsumpcja rejestru

To rozdzielenie ma znaczenie dla utrzymywalności. Oznacza, że większość powierzchni rdzenia potrzebuje tylko
jednego punktu integracji: „odczytaj rejestr”, a nie „obsłuż specjalnie każdy moduł
wtyczki”.

## Callbacki powiązania konwersacji

Wtyczki, które wiążą konwersację, mogą reagować po rozstrzygnięciu zatwierdzenia.

Użyj `api.onConversationBindingResolved(...)`, aby otrzymać callback po zatwierdzeniu
lub odrzuceniu żądania powiązania:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Pola ładunku callbacka:

- `status`: `"approved"` albo `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` albo `"deny"`
- `binding`: rozstrzygnięte powiązanie dla zatwierdzonych żądań
- `request`: podsumowanie oryginalnego żądania, podpowiedź odłączenia, identyfikator nadawcy i
  metadane konwersacji

Ten callback ma wyłącznie charakter powiadomienia. Nie zmienia tego, kto może powiązać
konwersację, i uruchamia się po zakończeniu obsługi zatwierdzenia przez rdzeń.

## Hooki runtime dostawców

Wtyczki dostawców mają teraz dwie warstwy:

- metadane manifestu: `providerAuthEnvVars` do taniego wyszukiwania uwierzytelniania z env przed
  załadowaniem runtime oraz `providerAuthChoices` do tanich etykiet onboardingu/wyboru auth
  i metadanych flag CLI przed załadowaniem runtime
- hooki czasu konfiguracji: `catalog` / starsze `discovery` oraz `applyConfigDefaults`
- hooki runtime: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw nadal odpowiada za ogólną pętlę agenta, failover, obsługę transkryptów i
politykę narzędzi. Te hooki są powierzchnią rozszerzeń dla zachowania specyficznego dla dostawcy, bez
potrzeby tworzenia całkowicie niestandardowego transportu inferencji.

Używaj manifestu `providerAuthEnvVars`, gdy dostawca ma poświadczenia oparte na env,
które ogólne ścieżki auth/status/model-picker powinny widzieć bez ładowania runtime wtyczki.
Używaj manifestu `providerAuthChoices`, gdy powierzchnie CLI onboardingu/wyboru auth
powinny znać identyfikator wyboru dostawcy, etykiety grup i prosty mechanizm auth
jedną flagą bez ładowania runtime dostawcy. Zachowaj runtime dostawcy
`envVars` dla wskazówek skierowanych do operatora, takich jak etykiety onboardingu albo zmienne
konfiguracji client-id/client-secret OAuth.

### Kolejność hooków i użycie

Dla wtyczek modeli/dostawców OpenClaw wywołuje hooki mniej więcej w tej kolejności.
Kolumna „Kiedy używać” to szybki przewodnik decyzyjny.

| #   | Hook                              | Co robi                                                                                  | Kiedy używać                                                                                                                               |
| --- | --------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | Publikuje konfigurację dostawcy do `models.providers` podczas generowania `models.json`  | Dostawca posiada katalog albo domyślne `baseUrl`                                                                                           |
| 2   | `applyConfigDefaults`             | Stosuje należące do dostawcy globalne ustawienia domyślne podczas materializacji konfiguracji | Ustawienia domyślne zależą od trybu auth, env albo semantyki rodziny modeli dostawcy                                                     |
| --  | _(built-in model lookup)_         | OpenClaw najpierw próbuje normalnej ścieżki rejestru/katalogu                             | _(to nie jest hook wtyczki)_                                                                                                               |
| 3   | `normalizeModelId`                | Normalizuje starsze aliasy model-id albo aliasy preview przed wyszukiwaniem               | Dostawca odpowiada za porządkowanie aliasów przed kanonicznym rozpoznaniem modelu                                                        |
| 4   | `normalizeTransport`              | Normalizuje rodzinę dostawcy `api` / `baseUrl` przed ogólnym składaniem modelu            | Dostawca odpowiada za porządkowanie transportu dla niestandardowych identyfikatorów dostawcy w tej samej rodzinie transportów            |
| 5   | `normalizeConfig`                 | Normalizuje `models.providers.<id>` przed rozpoznaniem runtime/dostawcy                   | Dostawca potrzebuje porządkowania konfiguracji, które powinno żyć z wtyczką; dołączone pomocniki rodziny Google dodatkowo stabilizują obsługiwane wpisy konfiguracji Google |
| 6   | `applyNativeStreamingUsageCompat` | Stosuje zgodnościowe przepisania native streaming-usage do dostawców konfiguracji         | Dostawca potrzebuje poprawek metadanych native streaming usage zależnych od endpointu                                                     |
| 7   | `resolveConfigApiKey`             | Rozpoznaje auth markerów env dla dostawców konfiguracji przed załadowaniem runtime auth   | Dostawca ma własne rozpoznawanie klucza API z markerów env; `amazon-bedrock` ma tu także wbudowany resolver markerów AWS                 |
| 8   | `resolveSyntheticAuth`            | Ujawnia auth lokalne/self-hosted lub oparte na konfiguracji bez utrwalania plaintext      | Dostawca może działać z syntetycznym/lokalnym markerem poświadczeń                                                                        |
| 9   | `shouldDeferSyntheticProfileAuth` | Obniża priorytet zapisanych syntetycznych placeholderów profilu względem auth z env/konfiguracji | Dostawca przechowuje syntetyczne placeholdery profilu, które nie powinny mieć pierwszeństwa                                         |
| 10  | `resolveDynamicModel`             | Synchroniczny fallback dla identyfikatorów modeli należących do dostawcy, których nie ma jeszcze w lokalnym rejestrze | Dostawca akceptuje dowolne identyfikatory modeli z upstreamu                                                     |
| 11  | `prepareDynamicModel`             | Asynchroniczne przygotowanie, a następnie `resolveDynamicModel` działa ponownie            | Dostawca potrzebuje metadanych sieciowych przed rozpoznaniem nieznanych identyfikatorów modeli                                           |
| 12  | `normalizeResolvedModel`          | Ostateczne przepisanie zanim embedded runner użyje rozpoznanego modelu                    | Dostawca potrzebuje przepisań transportu, ale nadal używa transportu rdzenia                                                             |
| 13  | `contributeResolvedModelCompat`   | Wnosi flagi zgodności dla modeli dostawcy za innym zgodnym transportem                    | Dostawca rozpoznaje własne modele na transportach proxy bez przejmowania dostawcy                                                         |
| 14  | `capabilities`                    | Metadane transkryptu/narzędzi należące do dostawcy używane przez współdzieloną logikę rdzenia | Dostawca potrzebuje niuansów dotyczących transkryptu/rodziny dostawcy                                                                  |
| 15  | `normalizeToolSchemas`            | Normalizuje schematy narzędzi, zanim zobaczy je embedded runner                           | Dostawca potrzebuje porządkowania schematu dla rodziny transportów                                                                        |
| 16  | `inspectToolSchemas`              | Ujawnia diagnostykę schematu należącą do dostawcy po normalizacji                         | Dostawca chce ostrzeżeń o słowach kluczowych bez uczenia rdzenia reguł specyficznych dla dostawcy                                       |
| 17  | `resolveReasoningOutputMode`      | Wybiera kontrakt wyniku reasoning: native vs tagged                                       | Dostawca potrzebuje tagged reasoning/final output zamiast pól native                                                                      |
| 18  | `prepareExtraParams`              | Normalizacja parametrów żądania przed ogólnymi wrapperami opcji stream                    | Dostawca potrzebuje domyślnych parametrów żądania albo porządkowania parametrów per dostawca                                             |
| 19  | `createStreamFn`                  | Całkowicie zastępuje normalną ścieżkę stream własnym transportem                          | Dostawca potrzebuje własnego protokołu wire, a nie tylko wrappera                                                                         |
| 20  | `wrapStreamFn`                    | Wrapper stream po zastosowaniu wrapperów ogólnych                                         | Dostawca potrzebuje wrapperów nagłówków/ciała/modelu bez własnego transportu                                                              |
| 21  | `resolveTransportTurnState`       | Dołącza natywne nagłówki lub metadane transportu per turn                                 | Dostawca chce, aby ogólne transporty wysyłały natywną tożsamość tury dla dostawcy                                                        |
| 22  | `resolveWebSocketSessionPolicy`   | Dołącza natywne nagłówki WebSocket lub politykę cooldown sesji                            | Dostawca chce, by ogólne transporty WS dostrajały nagłówki sesji lub politykę fallback                                                   |
| 23  | `formatApiKey`                    | Formatter profilu auth: zapisany profil staje się runtime stringiem `apiKey`              | Dostawca przechowuje dodatkowe metadane auth i potrzebuje własnego kształtu tokenu runtime                                               |
| 24  | `refreshOAuth`                    | Nadpisanie odświeżania OAuth dla niestandardowych endpointów odświeżania albo polityki błędów odświeżania | Dostawca nie pasuje do współdzielonych odświeżaczy `pi-ai`                                                                    |
| 25  | `buildAuthDoctorHint`             | Wskazówka naprawy dołączana po nieudanym odświeżeniu OAuth                                | Dostawca potrzebuje własnych wskazówek naprawy auth po błędzie odświeżania                                                                |
| 26  | `matchesContextOverflowError`     | Dopasowanie błędu przepełnienia okna kontekstu należące do dostawcy                       | Dostawca ma surowe błędy przepełnienia, których ogólne heurystyki nie wychwytują                                                         |
| 27  | `classifyFailoverReason`          | Klasyfikacja przyczyny failover należąca do dostawcy                                      | Dostawca potrafi mapować surowe błędy API/transportu na rate-limit/przeciążenie itd.                                                     |
| 28  | `isCacheTtlEligible`              | Polityka prompt-cache dla dostawców proxy/backhaul                                        | Dostawca potrzebuje bramkowania TTL cache specyficznego dla proxy                                                                         |
| 29  | `buildMissingAuthMessage`         | Zamiennik ogólnego komunikatu odzyskiwania przy braku auth                                | Dostawca potrzebuje własnej wskazówki odzyskiwania przy braku auth                                                                        |
| 30  | `suppressBuiltInModel`            | Tłumienie nieaktualnych modeli upstream plus opcjonalna wskazówka błędu dla użytkownika   | Dostawca musi ukryć nieaktualne wiersze upstream albo zastąpić je wskazówką dostawcy                                                     |
| 31  | `augmentModelCatalog`             | Syntetyczne/końcowe wiersze katalogu dodawane po wykryciu                                 | Dostawca potrzebuje syntetycznych wierszy zgodności przyszłościowej w `models list` i pickerach                                          |
| 32  | `isBinaryThinking`                | Przełącznik thinking włącz/wyłącz dla dostawców binary-thinking                           | Dostawca udostępnia wyłącznie binarne włącz/wyłącz thinking                                                                               |
| 33  | `supportsXHighThinking`           | Obsługa `xhigh` reasoning dla wybranych modeli                                            | Dostawca chce `xhigh` tylko dla podzbioru modeli                                                                                          |
| 34  | `resolveDefaultThinkingLevel`     | Domyślny poziom `/think` dla konkretnej rodziny modeli                                    | Dostawca odpowiada za domyślną politykę `/think` dla rodziny modeli                                                                       |
| 35  | `isModernModelRef`                | Dopasowywanie nowoczesnych modeli dla filtrów live profile i wyboru smoke                 | Dostawca odpowiada za dopasowywanie preferowanych modeli live/smoke                                                                       |
| 36  | `prepareRuntimeAuth`              | Wymienia skonfigurowane poświadczenie na rzeczywisty token/klucz runtime tuż przed inferencją | Dostawca potrzebuje wymiany tokenu albo krótkotrwałego poświadczenia żądania                                                           |
| 37  | `resolveUsageAuth`                | Rozpoznaje poświadczenia usage/billing dla `/usage` i powiązanych powierzchni statusu     | Dostawca potrzebuje własnego parsowania tokenu usage/quota lub innego poświadczenia usage                                                |
| 38  | `fetchUsageSnapshot`              | Pobiera i normalizuje migawki usage/quota specyficzne dla dostawcy po rozpoznaniu auth    | Dostawca potrzebuje własnego endpointu usage albo parsera payloadu                                                                        |
| 39  | `createEmbeddingProvider`         | Buduje adapter embedding należący do dostawcy dla memory/search                           | Zachowanie embedding pamięci powinno należeć do wtyczki dostawcy                                                                          |
| 40  | `buildReplayPolicy`               | Zwraca politykę replay sterującą obsługą transkryptu dla dostawcy                         | Dostawca potrzebuje własnej polityki transkryptu (np. usuwania bloków thinking)                                                          |
| 41  | `sanitizeReplayHistory`           | Przepisuje historię replay po ogólnym porządkowaniu transkryptu                           | Dostawca potrzebuje własnych przepisań replay poza współdzielonymi helperami kompaktowania                                               |
| 42  | `validateReplayTurns`             | Ostateczna walidacja albo przekształcenie tur replay przed embedded runnerem              | Transport dostawcy wymaga bardziej rygorystycznej walidacji tur po ogólnej sanitacji                                                     |
| 43  | `onModelSelected`                 | Uruchamia skutki uboczne po wyborze modelu należące do dostawcy                           | Dostawca potrzebuje telemetrii albo stanu należącego do dostawcy, gdy model staje się aktywny                                            |

`normalizeModelId`, `normalizeTransport` i `normalizeConfig` najpierw sprawdzają
dopasowaną wtyczkę dostawcy, a następnie przechodzą przez inne wtyczki dostawców obsługujące hooki,
aż któraś rzeczywiście zmieni model id albo transport/konfigurację. Dzięki temu
shimy aliasów/zgodności dostawców działają bez wymagania od wywołującego wiedzy, która
dołączona wtyczka odpowiada za przepisanie. Jeśli żaden hook dostawcy nie przepisze
obsługiwanego wpisu konfiguracji rodziny Google, dołączony normalizator konfiguracji Google
nadal zastosuje to porządkowanie zgodności.

Jeśli dostawca potrzebuje całkowicie własnego protokołu wire albo własnego wykonawcy żądań,
to jest to inna klasa rozszerzenia. Te hooki są przeznaczone dla zachowania dostawcy,
które nadal działa na normalnej pętli inferencji OpenClaw.

### Przykład dostawcy

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Wbudowane przykłady

- Anthropic używa `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  i `wrapStreamFn`, ponieważ odpowiada za zgodność przyszłościową Claude 4.6,
  wskazówki dotyczące rodziny dostawcy, wskazówki naprawy auth, integrację
  endpointu usage, kwalifikowalność prompt-cache, domyślne ustawienia konfiguracji świadome auth,
  domyślną/adaptacyjną politykę thinking Claude oraz kształtowanie stream specyficzne dla Anthropic dla
  nagłówków beta, `/fast` / `serviceTier` i `context1m`.
- Pomocniki stream specyficzne dla Claude w Anthropic pozostają na razie we
  własnej publicznej szczelinie `api.ts` / `contract-api.ts` dołączonej wtyczki. Ta
  powierzchnia pakietu eksportuje `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` oraz niższego poziomu
  buildery wrapperów Anthropic zamiast poszerzać ogólne SDK wokół reguł nagłówków beta
  jednego dostawcy.
- OpenAI używa `resolveDynamicModel`, `normalizeResolvedModel` i
  `capabilities` oraz `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` i `isModernModelRef`,
  ponieważ odpowiada za zgodność przyszłościową GPT-5.4, bezpośrednią normalizację OpenAI
  `openai-completions` -> `openai-responses`, wskazówki auth świadome Codex,
  tłumienie Spark, syntetyczne wiersze listy OpenAI oraz politykę thinking /
  modeli live GPT-5; rodzina stream `openai-responses-defaults` odpowiada za
  współdzielone natywne wrappery OpenAI Responses dla nagłówków atrybucji,
  `/fast`/`serviceTier`, szczegółowości tekstu, natywnego web search Codex,
  kształtowania payloadów reasoning-compat i zarządzania kontekstem Responses.
- OpenRouter używa `catalog` oraz `resolveDynamicModel` i
  `prepareDynamicModel`, ponieważ dostawca jest pass-through i może ujawniać nowe
  identyfikatory modeli, zanim statyczny katalog OpenClaw zostanie zaktualizowany; używa także
  `capabilities`, `wrapStreamFn` i `isCacheTtlEligible`, aby zachować
  nagłówki żądań specyficzne dla dostawcy, metadane routingu, poprawki reasoning i
  politykę prompt-cache poza rdzeniem. Jego polityka replay pochodzi z rodziny
  `passthrough-gemini`, podczas gdy rodzina stream `openrouter-thinking`
  odpowiada za wstrzykiwanie reasoning proxy oraz pomijanie modeli nieobsługiwanych / `auto`.
- GitHub Copilot używa `catalog`, `auth`, `resolveDynamicModel` i
  `capabilities` oraz `prepareRuntimeAuth` i `fetchUsageSnapshot`, ponieważ
  potrzebuje należącego do dostawcy logowania urządzenia, zachowania fallback modeli,
  niuansów transkryptu Claude, wymiany tokenu GitHub -> token Copilot i
  należącego do dostawcy endpointu usage.
- OpenAI Codex używa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` i `augmentModelCatalog` oraz
  `prepareExtraParams`, `resolveUsageAuth` i `fetchUsageSnapshot`, ponieważ
  nadal działa na transportach OpenAI rdzenia, ale odpowiada za normalizację
  transportu/base URL, politykę fallback odświeżania OAuth, domyślny wybór transportu,
  syntetyczne wiersze katalogu Codex i integrację endpointu usage ChatGPT; współdzieli tę samą rodzinę
  stream `openai-responses-defaults` co bezpośrednie OpenAI.
- Google AI Studio oraz Gemini CLI OAuth używają `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` i `isModernModelRef`, ponieważ rodzina replay
  `google-gemini` odpowiada za fallback zgodności przyszłościowej Gemini 3.1,
  natywną walidację replay Gemini, sanitację replay bootstrap, tryb tagged
  reasoning-output i dopasowywanie nowoczesnych modeli, podczas gdy rodzina stream
  `google-thinking` odpowiada za normalizację payloadów thinking Gemini;
  Gemini CLI OAuth używa również `formatApiKey`, `resolveUsageAuth` i
  `fetchUsageSnapshot` do formatowania tokenów, parsowania tokenów i
  podłączenia endpointu quota.
- Anthropic Vertex używa `buildReplayPolicy` przez rodzinę replay
  `anthropic-by-model`, dzięki czemu porządkowanie replay specyficzne dla Claude pozostaje
  ograniczone do identyfikatorów Claude zamiast wszystkich transportów `anthropic-messages`.
- Amazon Bedrock używa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` i `resolveDefaultThinkingLevel`, ponieważ odpowiada za
  klasyfikację błędów throttle/not-ready/context-overflow specyficznych dla Bedrock
  dla ruchu Anthropic-on-Bedrock; jego polityka replay nadal współdzieli tę samą
  osłonę `anthropic-by-model` przeznaczoną wyłącznie dla Claude.
- OpenRouter, Kilocode, Opencode i Opencode Go używają `buildReplayPolicy`
  przez rodzinę replay `passthrough-gemini`, ponieważ przekazują modele Gemini
  przez transporty zgodne z OpenAI i potrzebują sanitacji thought-signature
  Gemini bez natywnej walidacji replay Gemini ani przepisań bootstrap.
- MiniMax używa `buildReplayPolicy` przez rodzinę replay
  `hybrid-anthropic-openai`, ponieważ jeden dostawca posiada zarówno semantykę
  wiadomości Anthropic, jak i zgodną z OpenAI; zachowuje
  usuwanie bloków thinking tylko dla Claude po stronie Anthropic, jednocześnie przywracając tryb
  wyniku reasoning do native, a rodzina stream `minimax-fast-mode` odpowiada za
  przepisania modeli fast-mode na współdzielonej ścieżce stream.
- Moonshot używa `catalog` oraz `wrapStreamFn`, ponieważ nadal używa współdzielonego
  transportu OpenAI, ale potrzebuje normalizacji payloadu thinking należącej do dostawcy; rodzina stream
  `moonshot-thinking` mapuje konfigurację oraz stan `/think` na swój
  natywny binarny payload thinking.
- Kilocode używa `catalog`, `capabilities`, `wrapStreamFn` i
  `isCacheTtlEligible`, ponieważ potrzebuje nagłówków żądań należących do dostawcy,
  normalizacji payloadu reasoning, wskazówek transkryptu Gemini oraz bramkowania
  Anthropic cache-TTL; rodzina stream `kilocode-thinking` utrzymuje wstrzykiwanie Kilo thinking
  na współdzielonej ścieżce stream proxy, jednocześnie pomijając `kilo/auto` i
  inne identyfikatory modeli proxy, które nie obsługują jawnych payloadów reasoning.
- Z.AI używa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` i `fetchUsageSnapshot`, ponieważ odpowiada za fallback GLM-5,
  domyślne `tool_stream`, UX binary thinking, dopasowywanie nowoczesnych modeli
  oraz zarówno auth usage, jak i pobieranie quota; rodzina stream `tool-stream-default-on`
  utrzymuje wrapper `tool_stream` włączony domyślnie poza ręcznie pisanym glue per dostawca.
- xAI używa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` i `isModernModelRef`,
  ponieważ odpowiada za normalizację natywnego transportu xAI Responses, przepisania aliasów
  Grok fast-mode, domyślne `tool_stream`, porządkowanie strict-tool / reasoning-payload,
  ponowne użycie fallback auth dla narzędzi należących do wtyczki, rozpoznawanie modeli Grok
  zgodne z przyszłością oraz poprawki zgodności należące do dostawcy, takie jak profil schematu narzędzi xAI,
  nieobsługiwane słowa kluczowe schematu, natywne `web_search` i
  dekodowanie argumentów wywołań narzędzi z encji HTML.
- Mistral, OpenCode Zen i OpenCode Go używają tylko `capabilities`, aby
  utrzymać niuanse transkryptu/narzędzi poza rdzeniem.
- Dołączeni dostawcy tylko-katalogowi, tacy jak `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` i `volcengine`, używają
  tylko `catalog`.
- Qwen używa `catalog` dla swojego dostawcy tekstowego oraz współdzielonych rejestracji
  media-understanding i video-generation dla swoich powierzchni multimodalnych.
- MiniMax i Xiaomi używają `catalog` oraz hooków usage, ponieważ ich zachowanie `/usage`
  należy do wtyczki, mimo że inferencja nadal działa przez współdzielone transporty.

## Pomocniki runtime

Wtyczki mogą uzyskiwać dostęp do wybranych pomocników rdzenia przez `api.runtime`. Dla TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Uwagi:

- `textToSpeech` zwraca normalny payload wyjściowy TTS rdzenia dla powierzchni plików/notatek głosowych.
- Używa konfiguracji rdzenia `messages.tts` i wyboru dostawcy.
- Zwraca bufor audio PCM + częstotliwość próbkowania. Wtyczki muszą samodzielnie resamplować/kodować dla dostawców.
- `listVoices` jest opcjonalne dla każdego dostawcy. Używaj tego dla pickerów głosów albo przepływów konfiguracji należących do dostawcy.
- Listy głosów mogą zawierać bogatsze metadane, takie jak locale, płeć i tagi osobowości dla pickerów świadomych dostawcy.
- OpenAI i ElevenLabs obsługują dziś telefonię. Microsoft nie.

Wtyczki mogą też rejestrować dostawców mowy przez `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Uwagi:

- Zachowaj politykę TTS, fallback i dostarczanie odpowiedzi w rdzeniu.
- Używaj dostawców mowy dla zachowania syntezy należącego do dostawcy.
- Starsze wejście Microsoft `edge` jest normalizowane do identyfikatora dostawcy `microsoft`.
- Preferowany model własności jest zorientowany na firmę: jedna wtyczka dostawcy może posiadać
  dostawców tekstu, mowy, obrazów i przyszłych mediów, gdy OpenClaw dodaje takie
  kontrakty capability.

Dla rozumienia obrazów/audio/wideo wtyczki rejestrują jednego typowanego
dostawcę media-understanding zamiast ogólnego worka klucz/wartość:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Uwagi:

- Zachowaj orkiestrację, fallback, konfigurację i połączenie kanałów w rdzeniu.
- Zachowanie dostawcy utrzymuj we wtyczce dostawcy.
- Rozszerzanie addytywne powinno pozostać typowane: nowe opcjonalne metody, nowe opcjonalne
  pola wyniku, nowe opcjonalne capabilities.
- Generowanie wideo już podąża tym samym wzorcem:
  - rdzeń posiada kontrakt capability i pomocnik runtime
  - wtyczki dostawców rejestrują `api.registerVideoGenerationProvider(...)`
  - wtyczki funkcji/kanałów korzystają z `api.runtime.videoGeneration.*`

Dla pomocników runtime media-understanding wtyczki mogą wywoływać:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Do transkrypcji audio wtyczki mogą używać albo runtime media-understanding,
albo starszego aliasu STT:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Uwagi:

- `api.runtime.mediaUnderstanding.*` to preferowana współdzielona powierzchnia dla
  rozumienia obrazów/audio/wideo.
- Używa konfiguracji audio media-understanding rdzenia (`tools.media.audio`) oraz kolejności fallbacków dostawców.
- Zwraca `{ text: undefined }`, gdy nie powstanie wynik transkrypcji (na przykład przy pominiętym/nieobsługiwanym wejściu).
- `api.runtime.stt.transcribeAudioFile(...)` pozostaje aliasem zgodności.

Wtyczki mogą też uruchamiać podagentów w tle przez `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Uwagi:

- `provider` i `model` to opcjonalne nadpisania per uruchomienie, a nie trwałe zmiany sesji.
- OpenClaw honoruje te pola nadpisania tylko dla zaufanych wywołujących.
- Dla fallbackowych uruchomień należących do wtyczki operatorzy muszą jawnie wyrazić zgodę przez `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Użyj `plugins.entries.<id>.subagent.allowedModels`, aby ograniczyć zaufane wtyczki do określonych kanonicznych celów `provider/model`, albo `"*"` dla jawnego dopuszczenia dowolnego celu.
- Uruchomienia podagentów z niezaufanych wtyczek nadal działają, ale żądania nadpisania są odrzucane zamiast po cichu wracać do fallbacku.

W przypadku web search wtyczki mogą korzystać ze współdzielonego pomocnika runtime zamiast
sięgać do mechaniki narzędzia agenta:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Wtyczki mogą też rejestrować dostawców web-search przez
`api.registerWebSearchProvider(...)`.

Uwagi:

- Zachowaj wybór dostawcy, rozpoznawanie poświadczeń i współdzieloną semantykę żądań w rdzeniu.
- Używaj dostawców web-search dla transportów wyszukiwania specyficznych dla dostawcy.
- `api.runtime.webSearch.*` to preferowana współdzielona powierzchnia dla wtyczek funkcji/kanałów, które potrzebują zachowania wyszukiwania bez zależności od wrappera narzędzia agenta.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: wygeneruj obraz przy użyciu skonfigurowanego łańcucha dostawców generowania obrazów.
- `listProviders(...)`: wyświetl dostępnych dostawców generowania obrazów i ich capabilities.

## Trasy HTTP Gateway

Wtyczki mogą wystawiać endpointy HTTP przez `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Pola trasy:

- `path`: ścieżka trasy pod serwerem HTTP gateway.
- `auth`: wymagane. Użyj `"gateway"`, aby wymagać normalnego auth gateway, albo `"plugin"` dla auth/weryfikacji webhooków zarządzanych przez wtyczkę.
- `match`: opcjonalne. `"exact"` (domyślnie) albo `"prefix"`.
- `replaceExisting`: opcjonalne. Pozwala tej samej wtyczce zastąpić własną istniejącą rejestrację trasy.
- `handler`: zwróć `true`, gdy trasa obsłużyła żądanie.

Uwagi:

- `api.registerHttpHandler(...)` zostało usunięte i spowoduje błąd ładowania wtyczki. Użyj zamiast tego `api.registerHttpRoute(...)`.
- Trasy wtyczek muszą jawnie deklarować `auth`.
- Konflikty identycznych `path + match` są odrzucane, chyba że ustawiono `replaceExisting: true`, i jedna wtyczka nie może zastąpić trasy innej wtyczki.
- Nakładające się trasy z różnymi poziomami `auth` są odrzucane. Zachowuj łańcuchy fallthrough `exact`/`prefix` tylko w obrębie tego samego poziomu auth.
- Trasy `auth: "plugin"` **nie** otrzymują automatycznie operatorskich zakresów runtime. Służą do webhooków/weryfikacji podpisów zarządzanych przez wtyczkę, a nie do uprzywilejowanych wywołań pomocników Gateway.
- Trasy `auth: "gateway"` działają wewnątrz zakresu runtime żądania Gateway, ale ten zakres jest celowo konserwatywny:
  - bearer auth oparty na współdzielonym sekrecie (`gateway.auth.mode = "token"` / `"password"`) utrzymuje zakresy runtime trasy wtyczki przypięte do `operator.write`, nawet jeśli wywołujący wysyła `x-openclaw-scopes`
  - zaufane tryby HTTP niosące tożsamość (na przykład `trusted-proxy` albo `gateway.auth.mode = "none"` na prywatnym ingressie) honorują `x-openclaw-scopes` tylko wtedy, gdy nagłówek jest jawnie obecny
  - jeśli `x-openclaw-scopes` nie występuje w tych żądaniach trasy wtyczki niosących tożsamość, zakres runtime wraca do `operator.write`
- Praktyczna zasada: nie zakładaj, że trasa wtyczki z auth gateway jest niejawną powierzchnią administratora. Jeśli twoja trasa wymaga zachowania dostępnego tylko dla admina, wymagaj trybu auth niosącego tożsamość i opisz jawny kontrakt nagłówka `x-openclaw-scopes`.

## Ścieżki importu Plugin SDK

Przy tworzeniu wtyczek używaj podścieżek SDK zamiast monolitycznego importu
`openclaw/plugin-sdk`:

- `openclaw/plugin-sdk/plugin-entry` dla prymitywów rejestracji wtyczek.
- `openclaw/plugin-sdk/core` dla ogólnego współdzielonego kontraktu skierowanego do wtyczek.
- `openclaw/plugin-sdk/config-schema` dla eksportu głównego schematu Zod
  `openclaw.json` (`OpenClawSchema`).
- Stabilne prymitywy kanałów, takie jak `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` i
  `openclaw/plugin-sdk/webhook-ingress` dla współdzielonego połączenia konfiguracji/auth/odpowiedzi/webhooków.
  `channel-inbound` to współdzielony dom dla debounce, dopasowywania wzmianek,
  formatowania kopert i pomocników kontekstu kopert przychodzących.
  `channel-setup` to wąska szczelina konfiguracji opcjonalnej instalacji.
  `setup-runtime` to bezpieczna runtime powierzchnia konfiguracji używana przez `setupEntry` /
  opóźniony startup, łącznie z adapterami łatek konfiguracji bezpiecznymi przy imporcie.
  `setup-adapter-runtime` to świadoma env szczelina adaptera konfiguracji kont.
  `setup-tools` to mała szczelina pomocnicza CLI/archive/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Podścieżki domenowe, takie jak `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` i
  `openclaw/plugin-sdk/directory-runtime` dla współdzielonych helperów runtime/konfiguracji.
  `telegram-command-config` to wąska publiczna szczelina dla normalizacji/walidacji
  niestandardowych poleceń Telegram i pozostaje dostępna nawet wtedy, gdy dołączona
  powierzchnia kontraktu Telegram jest chwilowo niedostępna.
  `text-runtime` to współdzielona szczelina tekst/Markdown/logowanie, obejmująca
  usuwanie tekstu widocznego dla asystenta, helpery renderowania/dzielenia Markdown, helpery redakcji,
  helpery tagów dyrektyw i narzędzia bezpiecznego tekstu.
- Szczeliny kanałów specyficzne dla zatwierdzeń powinny preferować jeden kontrakt
  `approvalCapability` na wtyczce. Rdzeń odczytuje wtedy auth zatwierdzeń, dostarczanie, renderowanie i
  natywne zachowanie routingu przez tę jedną capability zamiast mieszać
  zachowanie zatwierdzeń z niepowiązanymi polami wtyczki.
- `openclaw/plugin-sdk/channel-runtime` jest przestarzałe i pozostaje tylko jako
  shim zgodności dla starszych wtyczek. Nowy kod powinien importować węższe
  ogólne prymitywy, a kod repozytorium nie powinien dodawać nowych importów tego shimu.
- Wewnętrzne elementy dołączonych rozszerzeń pozostają prywatne. Zewnętrzne wtyczki powinny używać tylko
  podścieżek `openclaw/plugin-sdk/*`. Kod/testy rdzenia OpenClaw mogą używać publicznych punktów wejścia
  repozytorium pod katalogiem głównym pakietu wtyczki, takich jak `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` oraz wąsko określonych plików, takich jak
  `login-qr-api.js`. Nigdy nie importuj `src/*` pakietu wtyczki z rdzenia ani z
  innego rozszerzenia.
- Podział punktów wejścia repozytorium:
  `<plugin-package-root>/api.js` to barrel helperów/typów,
  `<plugin-package-root>/runtime-api.js` to barrel tylko runtime,
  `<plugin-package-root>/index.js` to punkt wejścia dołączonej wtyczki,
  a `<plugin-package-root>/setup-entry.js` to punkt wejścia wtyczki konfiguracji.
- Obecne przykłady dołączonych dostawców:
  - Anthropic używa `api.js` / `contract-api.js` dla helperów stream Claude, takich
    jak `wrapAnthropicProviderStream`, helpery nagłówków beta i parsowanie `service_tier`.
  - OpenAI używa `api.js` dla builderów dostawców, helperów modeli domyślnych i builderów dostawców realtime.
  - OpenRouter używa `api.js` dla buildera dostawcy oraz helperów onboardingu/konfiguracji,
    podczas gdy `register.runtime.js` może nadal re-eksportować ogólne helpery
    `plugin-sdk/provider-stream` do użytku lokalnego w repozytorium.
- Publiczne punkty wejścia ładowane przez fasadę preferują aktywną migawkę konfiguracji runtime,
  gdy taka istnieje, a następnie wracają do rozpoznanego pliku konfiguracji na dysku, gdy
  OpenClaw nie udostępnia jeszcze migawki runtime.
- Ogólne współdzielone prymitywy pozostają preferowanym publicznym kontraktem SDK. Mały
  zastrzeżony zestaw zgodności pomocniczych szczelin oznaczonych marką dołączonych kanałów nadal istnieje.
  Traktuj je jako szczeliny utrzymaniowe/zgodnościowe dla dołączonych wtyczek, a nie jako nowe cele importu dla stron trzecich;
  nowe kontrakty międzykanałowe powinny nadal trafiać do ogólnych podścieżek `plugin-sdk/*` lub do lokalnych barrelów `api.js` /
  `runtime-api.js` danej wtyczki.

Uwaga dotycząca zgodności:

- Unikaj głównego barrela `openclaw/plugin-sdk` w nowym kodzie.
- W pierwszej kolejności preferuj wąskie stabilne prymitywy. Nowsze podścieżki setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool to zamierzony kontrakt dla nowych
  dołączonych i zewnętrznych wtyczek.
  Parsowanie/dopasowywanie celów należy do `openclaw/plugin-sdk/channel-targets`.
  Bramy akcji wiadomości i helpery message-id reakcji należą do
  `openclaw/plugin-sdk/channel-actions`.
- Barrele pomocnicze specyficzne dla dołączonych rozszerzeń nie są domyślnie stabilne. Jeśli
  helper jest potrzebny tylko dołączonemu rozszerzeniu, utrzymuj go za lokalną szczeliną `api.js` lub `runtime-api.js`
  tego rozszerzenia zamiast promować go do `openclaw/plugin-sdk/<extension>`.
- Nowe współdzielone szczeliny pomocnicze powinny być ogólne, a nie oznaczone marką kanału. Wspólne parsowanie celów
  należy do `openclaw/plugin-sdk/channel-targets`; wewnętrzne elementy specyficzne dla kanału
  pozostają za lokalną szczeliną `api.js` lub `runtime-api.js` należącej do wtyczki.
- Podścieżki specyficzne dla capability, takie jak `image-generation`,
  `media-understanding` i `speech`, istnieją, ponieważ dołączone/natywne wtyczki używają ich dziś.
  Ich obecność sama w sobie nie oznacza jeszcze, że każdy eksportowany helper jest
  długoterminowym zamrożonym kontraktem zewnętrznym.

## Schematy narzędzia wiadomości

Wtyczki powinny posiadać wkład do schematu `describeMessageTool(...)` specyficzny dla kanału.
Zachowuj pola specyficzne dla dostawcy we wtyczce, a nie we współdzielonym rdzeniu.

Dla współdzielonych przenośnych fragmentów schematu używaj ogólnych helperów eksportowanych przez
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` dla payloadów w stylu siatki przycisków
- `createMessageToolCardSchema()` dla ustrukturyzowanych payloadów kart

Jeśli dany kształt schematu ma sens tylko dla jednego dostawcy, zdefiniuj go w
kodzie źródłowym tej wtyczki zamiast promować go do współdzielonego SDK.

## Rozpoznawanie celów kanału

Wtyczki kanałów powinny posiadać semantykę celów specyficzną dla kanału. Zachowuj współdzielony
host wychodzący jako ogólny i używaj powierzchni adaptera wiadomości dla reguł dostawcy:

- `messaging.inferTargetChatType({ to })` decyduje, czy znormalizowany cel
  należy traktować jako `direct`, `group` albo `channel` przed wyszukiwaniem w katalogu.
- `messaging.targetResolver.looksLikeId(raw, normalized)` mówi rdzeniowi, czy dane wejście
  powinno od razu przejść do rozpoznawania podobnego do identyfikatora zamiast do wyszukiwania w katalogu.
- `messaging.targetResolver.resolveTarget(...)` to fallback wtyczki, gdy
  rdzeń potrzebuje ostatecznego rozpoznania należącego do dostawcy po normalizacji lub po
  niepowodzeniu wyszukiwania w katalogu.
- `messaging.resolveOutboundSessionRoute(...)` odpowiada za specyficzną dla dostawcy konstrukcję trasy sesji
  wychodzącej po rozpoznaniu celu.

Zalecany podział:

- Używaj `inferTargetChatType` do decyzji kategoryzacyjnych, które powinny zapadać przed
  przeszukiwaniem rozmówców/grup.
- Używaj `looksLikeId` do sprawdzania typu „traktuj to jako jawny/natywny identyfikator celu”.
- Używaj `resolveTarget` do fallbackowej normalizacji specyficznej dla dostawcy, a nie do
  szerokiego wyszukiwania w katalogu.
- Utrzymuj natywne identyfikatory dostawcy, takie jak chat ids, thread ids, JID-y, uchwyty i room ids
  wewnątrz wartości `target` albo parametrów specyficznych dla dostawcy, a nie w ogólnych polach SDK.

## Katalogi oparte na konfiguracji

Wtyczki, które wyprowadzają wpisy katalogu z konfiguracji, powinny utrzymywać tę logikę we
wtyczce i używać współdzielonych helperów z
`openclaw/plugin-sdk/directory-runtime`.

Używaj tego, gdy kanał potrzebuje rozmówców/grup opartych na konfiguracji, takich jak:

- partnerzy DM sterowani allowlistą
- skonfigurowane mapy kanałów/grup
- statyczne fallbacki katalogu w zakresie konta

Współdzielone helpery w `directory-runtime` obsługują tylko operacje ogólne:

- filtrowanie zapytań
- stosowanie limitów
- deduplikację/helpery normalizacji
- budowanie `ChannelDirectoryEntry[]`

Inspekcja kont specyficzna dla kanału i normalizacja identyfikatorów powinny pozostać w
implementacji wtyczki.

## Katalogi dostawców

Wtyczki dostawców mogą definiować katalogi modeli dla inferencji za pomocą
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` zwraca ten sam kształt, który OpenClaw zapisuje do
`models.providers`:

- `{ provider }` dla jednego wpisu dostawcy
- `{ providers }` dla wielu wpisów dostawców

Używaj `catalog`, gdy wtyczka posiada identyfikatory modeli specyficzne dla dostawcy, domyślne wartości `baseUrl` albo
metadane modeli zależne od auth.

`catalog.order` kontroluje, kiedy katalog wtyczki scala się względem wbudowanych
niejawnych dostawców OpenClaw:

- `simple`: dostawcy z prostym kluczem API albo sterowani env
- `profile`: dostawcy pojawiający się, gdy istnieją profile auth
- `paired`: dostawcy syntetyzujący wiele powiązanych wpisów dostawców
- `late`: ostatnie przejście, po innych niejawnych dostawcach

Późniejsi dostawcy wygrywają przy kolizji kluczy, więc wtyczki mogą celowo zastąpić
wbudowany wpis dostawcy tym samym identyfikatorem dostawcy.

Zgodność:

- `discovery` nadal działa jako starszy alias
- jeśli zarejestrowane są zarówno `catalog`, jak i `discovery`, OpenClaw używa `catalog`

## Inspekcja kanałów tylko do odczytu

Jeśli twoja wtyczka rejestruje kanał, preferuj implementację
`plugin.config.inspectAccount(cfg, accountId)` obok `resolveAccount(...)`.

Dlaczego:

- `resolveAccount(...)` to ścieżka runtime. Może zakładać, że poświadczenia
  są w pełni zmaterializowane, i szybko kończyć się błędem, gdy brakuje wymaganych sekretów.
- Ścieżki poleceń tylko do odczytu, takie jak `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` oraz przepływy doctor/config
  repair, nie powinny wymagać materializacji poświadczeń runtime tylko po to, by opisać konfigurację.

Zalecane zachowanie `inspectAccount(...)`:

- Zwracaj tylko opisowy stan konta.
- Zachowuj `enabled` i `configured`.
- Uwzględniaj pola źródła/statusu poświadczeń, gdy mają znaczenie, na przykład:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Nie musisz zwracać surowych wartości tokenów tylko po to, by raportować dostępność w trybie tylko do odczytu. Wystarczy
  zwrócić `tokenStatus: "available"` (oraz odpowiadające pole źródła).
- Używaj `configured_unavailable`, gdy poświadczenie jest skonfigurowane przez SecretRef, ale
  niedostępne w bieżącej ścieżce polecenia.

Dzięki temu polecenia tylko do odczytu mogą raportować „skonfigurowane, ale niedostępne w tej ścieżce polecenia”
zamiast kończyć się błędem albo błędnie zgłaszać konto jako nieskonfigurowane.

## Package packs

Katalog wtyczki może zawierać `package.json` z `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Każdy wpis staje się wtyczką. Jeśli pakiet wymienia wiele rozszerzeń, identyfikator wtyczki
staje się `name/<fileBase>`.

Jeśli twoja wtyczka importuje zależności npm, zainstaluj je w tym katalogu, aby
`node_modules` było dostępne (`npm install` / `pnpm install`).

Zabezpieczenie: każdy wpis `openclaw.extensions` musi pozostać wewnątrz katalogu wtyczki
po rozpoznaniu symlinków. Wpisy wychodzące poza katalog pakietu są
odrzucane.

Uwaga dotycząca bezpieczeństwa: `openclaw plugins install` instaluje zależności wtyczki przez
`npm install --omit=dev --ignore-scripts` (bez skryptów lifecycle i bez zależności dev w runtime). Utrzymuj drzewa zależności wtyczek jako „czyste JS/TS” i unikaj pakietów wymagających buildów `postinstall`.

Opcjonalnie: `openclaw.setupEntry` może wskazywać lekki moduł tylko do konfiguracji.
Gdy OpenClaw potrzebuje powierzchni konfiguracji dla wyłączonej wtyczki kanału, albo
gdy wtyczka kanału jest włączona, ale nadal nieskonfigurowana, ładuje `setupEntry`
zamiast pełnego entry wtyczki. Dzięki temu uruchamianie i konfiguracja są lżejsze,
gdy główne entry wtyczki podłącza też narzędzia, hooki lub inny kod tylko runtime.

Opcjonalnie: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
może włączyć dla wtyczki kanału tę samą ścieżkę `setupEntry` podczas fazy uruchamiania gateway
przed listen, nawet gdy kanał jest już skonfigurowany.

Używaj tego tylko wtedy, gdy `setupEntry` w pełni pokrywa powierzchnię startupu, która musi istnieć
zanim gateway zacznie nasłuchiwać. W praktyce oznacza to, że entry konfiguracji
musi zarejestrować każdą capability należącą do kanału, od której zależy startup, taką jak:

- sama rejestracja kanału
- wszelkie trasy HTTP, które muszą być dostępne zanim gateway zacznie nasłuchiwać
- wszelkie metody gateway, narzędzia lub usługi, które muszą istnieć w tym samym oknie

Jeśli twoje pełne entry nadal posiada jakąkolwiek wymaganą capability startupową, nie włączaj
tej flagi. Zachowaj domyślne zachowanie wtyczki i pozwól OpenClaw załadować
pełne entry podczas startupu.

Dołączone kanały mogą też publikować pomocniki powierzchni kontraktu tylko do konfiguracji, z których
rdzeń może korzystać przed załadowaniem pełnego runtime kanału. Obecna powierzchnia promocji konfiguracji to:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Rdzeń używa tej powierzchni, gdy musi promować starszą konfigurację kanału z jednym kontem do
`channels.<id>.accounts.*` bez ładowania pełnego entry wtyczki.
Matrix jest obecnym przykładem dołączonym: przenosi tylko klucze auth/bootstrap do
nazwanego promowanego konta, gdy nazwane konta już istnieją, i może zachować
skonfigurowany niekanoniczny klucz konta domyślnego zamiast zawsze tworzyć
`accounts.default`.

Te adaptery łatek konfiguracji utrzymują leniwe wykrywanie powierzchni kontraktu dołączonych kanałów. Czas importu
pozostaje lekki; powierzchnia promocji jest ładowana dopiero przy pierwszym użyciu, zamiast
ponownie wchodzić w startup dołączonego kanału przy imporcie modułu.

Gdy te powierzchnie startupu obejmują metody Gateway RPC, utrzymuj je pod
prefiksem specyficznym dla wtyczki. Przestrzenie nazw administratora rdzenia (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) pozostają zastrzeżone i zawsze są rozpoznawane
do `operator.admin`, nawet jeśli wtyczka żąda węższego zakresu.

Przykład:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadane katalogu kanałów

Wtyczki kanałów mogą reklamować metadane konfiguracji/wykrywania przez `openclaw.channel` oraz
wskazówki instalacji przez `openclaw.install`. Dzięki temu dane katalogowe rdzenia pozostają puste.

Przykład:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Przydatne pola `openclaw.channel` poza minimalnym przykładem:

- `detailLabel`: etykieta pomocnicza dla bogatszych powierzchni katalogu/statusu
- `docsLabel`: nadpisuje tekst linku do dokumentacji
- `preferOver`: identyfikatory wtyczek/kanałów o niższym priorytecie, które ten wpis katalogu powinien wyprzedzać
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: kontrola tekstu na powierzchni wyboru
- `markdownCapable`: oznacza kanał jako obsługujący Markdown przy decyzjach dotyczących formatowania wychodzącego
- `exposure.configured`: ukrywa kanał z powierzchni listowania skonfigurowanych kanałów po ustawieniu na `false`
- `exposure.setup`: ukrywa kanał z interaktywnych pickerów konfiguracji po ustawieniu na `false`
- `exposure.docs`: oznacza kanał jako wewnętrzny/prywatny dla powierzchni nawigacji dokumentacji
- `showConfigured` / `showInSetup`: starsze aliasy nadal akceptowane dla zgodności; preferuj `exposure`
- `quickstartAllowFrom`: włącza kanał do standardowego przepływu quickstart `allowFrom`
- `forceAccountBinding`: wymaga jawnego powiązania konta nawet wtedy, gdy istnieje tylko jedno konto
- `preferSessionLookupForAnnounceTarget`: preferuje lookup sesji przy rozpoznawaniu celów announce

OpenClaw może także scalać **zewnętrzne katalogi kanałów** (na przykład eksport
rejestru MPM). Umieść plik JSON w jednej z lokalizacji:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Albo wskaż `OPENCLAW_PLUGIN_CATALOG_PATHS` (lub `OPENCLAW_MPM_CATALOG_PATHS`) na
jeden lub wiele plików JSON (rozdzielanych przecinkiem/średnikiem/`PATH`). Każdy plik powinien
zawierać `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Parser akceptuje też `"packages"` albo `"plugins"` jako starsze aliasy klucza `"entries"`.

## Wtyczki silnika kontekstu

Wtyczki silnika kontekstu odpowiadają za orkiestrację kontekstu sesji dla ingest, składania
i kompaktowania. Zarejestruj je ze swojej wtyczki przez
`api.registerContextEngine(id, factory)`, a następnie wybierz aktywny silnik przez
`plugins.slots.contextEngine`.

Używaj tego, gdy twoja wtyczka musi zastąpić lub rozszerzyć domyślny
pipeline kontekstu zamiast tylko dodawać wyszukiwanie pamięci albo hooki.

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Jeśli twój silnik **nie** posiada algorytmu kompaktowania, pozostaw zaimplementowane `compact()`
i jawnie deleguj je dalej:

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Dodawanie nowej capability

Gdy wtyczka potrzebuje zachowania, które nie pasuje do obecnego API, nie omijaj
systemu wtyczek przez prywatne sięgnięcie do wnętrza. Dodaj brakującą capability.

Zalecana sekwencja:

1. zdefiniuj kontrakt rdzenia
   Zdecyduj, jakie współdzielone zachowanie powinien posiadać rdzeń: politykę, fallback, scalanie konfiguracji,
   cykl życia, semantykę skierowaną do kanałów i kształt pomocnika runtime.
2. dodaj typowane powierzchnie rejestracji/runtime wtyczek
   Rozszerz `OpenClawPluginApi` i/lub `api.runtime` o najmniejszą użyteczną
   typowaną powierzchnię capability.
3. podłącz konsumentów w rdzeniu oraz wtyczkach kanałów/funkcji
   Kanały i wtyczki funkcji powinny korzystać z nowej capability przez rdzeń,
   a nie przez bezpośredni import implementacji dostawcy.
4. zarejestruj implementacje dostawców
   Wtyczki dostawców rejestrują wtedy swoje backendy względem capability.
5. dodaj pokrycie kontraktowe
   Dodaj testy, aby kształt własności i rejestracji pozostawał z czasem jawny.

W ten sposób OpenClaw pozostaje systemem z jasno określonymi opiniami, nie stając się systemem zakodowanym pod
światopogląd jednego dostawcy. Zobacz [Capability Cookbook](/pl/plugins/architecture),
aby znaleźć konkretną listę plików i gotowy przykład.

### Lista kontrolna capability

Gdy dodajesz nową capability, implementacja zwykle powinna dotykać tych
powierzchni razem:

- typy kontraktu rdzenia w `src/<capability>/types.ts`
- runner/pomocnik runtime rdzenia w `src/<capability>/runtime.ts`
- powierzchnia rejestracji API wtyczek w `src/plugins/types.ts`
- połączenie rejestru wtyczek w `src/plugins/registry.ts`
- udostępnienie runtime wtyczek w `src/plugins/runtime/*`, gdy wtyczki funkcji/kanałów
  muszą z tego korzystać
- helpery przechwytywania/testów w `src/test-utils/plugin-registration.ts`
- asercje własności/kontraktów w `src/plugins/contracts/registry.ts`
- dokumentacja dla operatorów/wtyczek w `docs/`

Jeśli którejś z tych powierzchni brakuje, zwykle oznacza to, że capability
nie jest jeszcze w pełni zintegrowana.

### Szablon capability

Minimalny wzorzec:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Wzorzec testu kontraktowego:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

To utrzymuje prostą zasadę:

- rdzeń posiada kontrakt capability + orkiestrację
- wtyczki dostawców posiadają implementacje dostawców
- wtyczki funkcji/kanałów korzystają z helperów runtime
- testy kontraktowe utrzymują jawną własność
