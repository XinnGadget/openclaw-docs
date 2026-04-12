---
read_when:
    - Tworzenie lub debugowanie natywnych pluginów OpenClaw
    - Zrozumienie modelu możliwości pluginów lub granic własności
    - Praca nad potokiem ładowania pluginów lub rejestrem
    - Implementowanie hooków środowiska uruchomieniowego dostawcy lub pluginów kanałów
sidebarTitle: Internals
summary: 'Wewnętrzne elementy Plugin: model możliwości, własność, kontrakty, potok ładowania i pomocniki środowiska uruchomieniowego'
title: Wewnętrzne elementy Plugin
x-i18n:
    generated_at: "2026-04-12T09:33:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6f4f8e6bcb14358b3aaa698d03faf456bbeebc04a6d70d1ae6451b02ab17cf09
    source_path: plugins/architecture.md
    workflow: 15
---

# Wewnętrzne elementy Plugin

<Info>
  To jest **szczegółowe odniesienie architektoniczne**. Praktyczne przewodniki znajdziesz tutaj:
  - [Instalowanie i używanie pluginów](/pl/tools/plugin) — przewodnik użytkownika
  - [Pierwsze kroki](/pl/plugins/building-plugins) — pierwszy samouczek dotyczący pluginów
  - [Pluginy kanałów](/pl/plugins/sdk-channel-plugins) — tworzenie kanału komunikacyjnego
  - [Pluginy dostawców](/pl/plugins/sdk-provider-plugins) — tworzenie dostawcy modeli
  - [Przegląd SDK](/pl/plugins/sdk-overview) — mapa importów i API rejestracji
</Info>

Ta strona opisuje wewnętrzną architekturę systemu pluginów OpenClaw.

## Publiczny model możliwości

Możliwości to publiczny model **natywnych pluginów** w OpenClaw. Każdy
natywny plugin OpenClaw rejestruje się względem co najmniej jednego typu możliwości:

| Możliwość             | Metoda rejestracji                              | Przykładowe pluginy                  |
| --------------------- | ----------------------------------------------- | ------------------------------------ |
| Wnioskowanie tekstowe | `api.registerProvider(...)`                     | `openai`, `anthropic`                |
| Backend wnioskowania CLI | `api.registerCliBackend(...)`                | `openai`, `anthropic`                |
| Mowa                  | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`            |
| Transkrypcja w czasie rzeczywistym | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                  |
| Głos w czasie rzeczywistym | `api.registerRealtimeVoiceProvider(...)`   | `openai`                             |
| Rozumienie multimediów | `api.registerMediaUnderstandingProvider(...)`  | `openai`, `google`                   |
| Generowanie obrazów   | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Generowanie muzyki    | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                  |
| Generowanie wideo     | `api.registerVideoGenerationProvider(...)`      | `qwen`                               |
| Pobieranie z sieci    | `api.registerWebFetchProvider(...)`             | `firecrawl`                          |
| Wyszukiwanie w sieci  | `api.registerWebSearchProvider(...)`            | `google`                             |
| Kanał / komunikacja   | `api.registerChannel(...)`                      | `msteams`, `matrix`                  |

Plugin, który rejestruje zero możliwości, ale udostępnia hooki, narzędzia lub
usługi, to plugin **legacy typu wyłącznie hooki**. Ten wzorzec nadal jest w pełni wspierany.

### Podejście do zgodności zewnętrznej

Model możliwości został wdrożony w rdzeniu i jest już dziś używany przez
bundlowane/natywne pluginy, ale zgodność zewnętrznych pluginów nadal wymaga
bardziej rygorystycznego podejścia niż „jest eksportowane, więc jest zamrożone”.

Aktualne wskazówki:

- **istniejące pluginy zewnętrzne:** utrzymuj działanie integracji opartych na hookach; traktuj
  to jako bazowy poziom zgodności
- **nowe bundlowane/natywne pluginy:** preferuj jawną rejestrację możliwości zamiast
  zależności specyficznych dla dostawcy lub nowych projektów typu wyłącznie hooki
- **zewnętrzne pluginy przyjmujące rejestrację możliwości:** dozwolone, ale traktuj
  powierzchnie pomocnicze specyficzne dla możliwości jako rozwijające się, chyba że dokumentacja
  wyraźnie oznacza dany kontrakt jako stabilny

Praktyczna zasada:

- API rejestracji możliwości jest zamierzonym kierunkiem
- legacy hooki pozostają najbezpieczniejszą ścieżką bez ryzyka naruszenia zgodności dla pluginów zewnętrznych w czasie przejścia
- eksportowane podścieżki pomocnicze nie są równoważne; preferuj wąski, udokumentowany
  kontrakt, a nie przypadkowe eksporty pomocnicze

### Kształty pluginów

OpenClaw klasyfikuje każdy załadowany plugin do jednego z kształtów na podstawie jego
rzeczywistego zachowania rejestracyjnego (a nie tylko statycznych metadanych):

- **plain-capability** -- rejestruje dokładnie jeden typ możliwości (na przykład
  plugin tylko dostawcy, taki jak `mistral`)
- **hybrid-capability** -- rejestruje wiele typów możliwości (na przykład
  `openai` obsługuje wnioskowanie tekstowe, mowę, rozumienie multimediów i
  generowanie obrazów)
- **hook-only** -- rejestruje wyłącznie hooki (typowane lub własne), bez możliwości,
  narzędzi, poleceń ani usług
- **non-capability** -- rejestruje narzędzia, polecenia, usługi lub trasy, ale bez
  możliwości

Użyj `openclaw plugins inspect <id>`, aby zobaczyć kształt pluginu i rozbicie możliwości.
Szczegóły znajdziesz w [odniesieniu do CLI](/cli/plugins#inspect).

### Legacy hooki

Hook `before_agent_start` pozostaje wspierany jako ścieżka zgodności dla
pluginów typu wyłącznie hooki. Nadal zależą od niego legacy pluginy używane w praktyce.

Kierunek:

- utrzymywać jego działanie
- dokumentować go jako legacy
- preferować `before_model_resolve` do pracy związanej z nadpisywaniem modelu/dostawcy
- preferować `before_prompt_build` do pracy związanej z modyfikacją promptu
- usuwać dopiero wtedy, gdy rzeczywiste użycie spadnie, a pokrycie testami fixture potwierdzi bezpieczeństwo migracji

### Sygnały zgodności

Gdy uruchamiasz `openclaw doctor` lub `openclaw plugins inspect <id>`, możesz zobaczyć
jedną z tych etykiet:

| Sygnał                     | Znaczenie                                                    |
| -------------------------- | ------------------------------------------------------------ |
| **config valid**           | Konfiguracja parsuje się poprawnie i pluginy są rozwiązywane |
| **compatibility advisory** | Plugin używa wspieranego, ale starszego wzorca (np. `hook-only`) |
| **legacy warning**         | Plugin używa `before_agent_start`, które jest przestarzałe   |
| **hard error**             | Konfiguracja jest nieprawidłowa lub plugin nie załadował się |

Ani `hook-only`, ani `before_agent_start` nie zepsują dziś Twojego pluginu --
`hook-only` ma charakter doradczy, a `before_agent_start` wywołuje jedynie ostrzeżenie. Te
sygnały pojawiają się także w `openclaw status --all` oraz `openclaw plugins doctor`.

## Przegląd architektury

System pluginów OpenClaw ma cztery warstwy:

1. **Manifest + wykrywanie**
   OpenClaw znajduje kandydackie pluginy w skonfigurowanych ścieżkach, katalogach głównych workspace,
   globalnych katalogach rozszerzeń i wbudowanych rozszerzeniach. Wykrywanie najpierw odczytuje natywne
   manifesty `openclaw.plugin.json` oraz wspierane manifesty bundle.
2. **Włączanie + walidacja**
   Rdzeń decyduje, czy wykryty plugin jest włączony, wyłączony, zablokowany czy
   wybrany do ekskluzywnego slotu, takiego jak pamięć.
3. **Ładowanie środowiska uruchomieniowego**
   Natywne pluginy OpenClaw są ładowane w procesie przez jiti i rejestrują
   możliwości w centralnym rejestrze. Zgodne bundle są normalizowane do rekordów
   rejestru bez importowania kodu środowiska uruchomieniowego.
4. **Konsumpcja powierzchni**
   Pozostałe części OpenClaw odczytują rejestr, aby udostępniać narzędzia, kanały, konfigurację
   dostawców, hooki, trasy HTTP, polecenia CLI i usługi.

Dla CLI pluginów w szczególności, wykrywanie poleceń głównych jest podzielone na dwa etapy:

- metadane czasu parsowania pochodzą z `registerCli(..., { descriptors: [...] })`
- właściwy moduł CLI pluginu może pozostać leniwy i zarejestrować się przy pierwszym wywołaniu

Dzięki temu kod CLI należący do pluginu pozostaje w pluginie, a OpenClaw nadal może
zarezerwować nazwy poleceń głównych przed parsowaniem.

Ważna granica projektowa:

- wykrywanie i walidacja konfiguracji powinny działać na podstawie **metadanych manifestu/schematu**
  bez wykonywania kodu pluginu
- natywne zachowanie środowiska uruchomieniowego pochodzi ze ścieżki `register(api)` modułu pluginu

Ten podział pozwala OpenClaw walidować konfigurację, wyjaśniać brakujące/wyłączone pluginy i
budować wskazówki dla UI/schematu zanim pełne środowisko uruchomieniowe zostanie aktywowane.

### Pluginy kanałów i wspólne narzędzie message

Pluginy kanałów nie muszą rejestrować osobnego narzędzia do wysyłania/edycji/reakcji dla
zwykłych działań czatu. OpenClaw utrzymuje jedno wspólne narzędzie `message` w rdzeniu,
a pluginy kanałów odpowiadają za właściwe dla kanału wykrywanie i wykonywanie za nim stojące.

Obecna granica wygląda tak:

- rdzeń odpowiada za hosta wspólnego narzędzia `message`, powiązanie z promptem, prowadzenie
  ewidencji sesji/wątków i dyspozycję wykonania
- pluginy kanałów odpowiadają za wykrywanie działań objętych zakresem, wykrywanie możliwości oraz wszelkie
  fragmenty schematu specyficzne dla kanału
- pluginy kanałów odpowiadają za gramatykę konwersacji sesji specyficzną dla dostawcy, na przykład
  za sposób, w jaki identyfikatory konwersacji kodują identyfikatory wątków lub dziedziczą je po
  konwersacjach nadrzędnych
- pluginy kanałów wykonują końcowe działanie przez swój adapter działań

Dla pluginów kanałów powierzchnią SDK jest
`ChannelMessageActionAdapter.describeMessageTool(...)`. To ujednolicone wywołanie wykrywania
pozwala pluginowi zwrócić widoczne działania, możliwości i wkłady do schematu razem, tak
aby te elementy nie rozjeżdżały się względem siebie.

Rdzeń przekazuje zakres środowiska uruchomieniowego do tego kroku wykrywania. Ważne pola obejmują:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- zaufane przychodzące `requesterSenderId`

Ma to znaczenie dla pluginów zależnych od kontekstu. Kanał może ukrywać lub udostępniać
działania wiadomości na podstawie aktywnego konta, bieżącego pokoju/wątku/wiadomości lub
zaufanej tożsamości żądającego bez twardego kodowania gałęzi specyficznych dla kanału
we wspólnym narzędziu `message` rdzenia.

Dlatego właśnie zmiany routingu embedded-runner nadal należą do pracy nad pluginami: runner
odpowiada za przekazanie bieżącej tożsamości czatu/sesji do granicy wykrywania pluginu, tak
aby wspólne narzędzie `message` udostępniało właściwą, należącą do kanału powierzchnię dla
bieżącej tury.

W przypadku pomocników wykonania należących do kanału, bundlowane pluginy powinny utrzymywać
środowisko uruchomieniowe wykonania we własnych modułach rozszerzeń. Rdzeń nie odpowiada już za
środowiska uruchomieniowe działań wiadomości Discord, Slack, Telegram czy WhatsApp
w `src/agents/tools`. Nie publikujemy osobnych podścieżek `plugin-sdk/*-action-runtime`, a bundlowane
pluginy powinny importować swój lokalny kod środowiska uruchomieniowego bezpośrednio z
własnych modułów rozszerzenia.

Ta sama granica dotyczy ogólnie nazwanych po dostawcach szwów SDK: rdzeń nie powinien
importować wygodnych barrelów specyficznych dla kanałów takich jak Slack, Discord, Signal,
WhatsApp czy podobnych rozszerzeń. Jeśli rdzeń potrzebuje jakiegoś zachowania, powinien albo
skorzystać z własnego barrela `api.ts` / `runtime-api.ts` bundlowanego pluginu, albo wynieść tę
potrzebę do wąskiej, ogólnej możliwości we wspólnym SDK.

W przypadku ankiet istnieją konkretnie dwie ścieżki wykonania:

- `outbound.sendPoll` to wspólna baza dla kanałów pasujących do wspólnego modelu ankiet
- `actions.handleAction("poll")` to preferowana ścieżka dla semantyki ankiet specyficznej dla kanału
  lub dodatkowych parametrów ankiety

Rdzeń odracza teraz wspólne parsowanie ankiet do momentu, aż dyspozycja ankiety pluginu odrzuci
działanie, dzięki czemu obsługujące ankiety handlery należące do pluginów mogą przyjmować pola
ankiet specyficzne dla kanału bez wcześniejszego zablokowania przez ogólny parser ankiet.

Pełną sekwencję uruchamiania znajdziesz w sekcji [Potok ładowania](#load-pipeline).

## Model własności możliwości

OpenClaw traktuje natywny plugin jako granicę własności dla **firmy** lub
**funkcji**, a nie jako zbiór niepowiązanych integracji.

Oznacza to, że:

- plugin firmy powinien zwykle obsługiwać wszystkie powierzchnie OpenClaw skierowane do tej firmy
- plugin funkcji powinien zwykle obsługiwać pełną powierzchnię funkcji, którą wprowadza
- kanały powinny korzystać ze wspólnych możliwości rdzenia zamiast doraźnie ponownie implementować
  zachowanie dostawcy

Przykłady:

- bundlowany plugin `openai` obsługuje zachowanie dostawcy modeli OpenAI oraz zachowanie OpenAI dla
  mowy + głosu w czasie rzeczywistym + rozumienia multimediów + generowania obrazów
- bundlowany plugin `elevenlabs` obsługuje zachowanie mowy ElevenLabs
- bundlowany plugin `microsoft` obsługuje zachowanie mowy Microsoft
- bundlowany plugin `google` obsługuje zachowanie dostawcy modeli Google oraz zachowanie Google dla
  rozumienia multimediów + generowania obrazów + wyszukiwania w sieci
- bundlowany plugin `firecrawl` obsługuje zachowanie Firecrawl dla pobierania z sieci
- bundlowane pluginy `minimax`, `mistral`, `moonshot` i `zai` obsługują swoje backendy
  rozumienia multimediów
- bundlowany plugin `qwen` obsługuje zachowanie dostawcy tekstu Qwen oraz
  rozumienie multimediów i generowanie wideo
- plugin `voice-call` jest pluginem funkcji: obsługuje transport połączeń, narzędzia,
  CLI, trasy i mostkowanie strumienia multimediów Twilio, ale korzysta ze wspólnych możliwości
  mowy oraz transkrypcji i głosu w czasie rzeczywistym zamiast importować pluginy dostawców bezpośrednio

Docelowy stan to:

- OpenAI znajduje się w jednym pluginie, nawet jeśli obejmuje modele tekstowe, mowę, obrazy i
  przyszłe wideo
- inny dostawca może zrobić to samo dla własnego obszaru funkcjonalnego
- kanały nie muszą wiedzieć, który plugin dostawcy obsługuje danego providera; korzystają ze
  wspólnego kontraktu możliwości udostępnianego przez rdzeń

To jest kluczowe rozróżnienie:

- **plugin** = granica własności
- **capability** = kontrakt rdzenia, który wiele pluginów może implementować lub wykorzystywać

Jeśli więc OpenClaw doda nową domenę, taką jak wideo, pierwsze pytanie nie brzmi
„który provider powinien na sztywno obsługiwać wideo?”. Pierwsze pytanie brzmi:
„jaki jest kontrakt możliwości wideo w rdzeniu?”. Gdy taki kontrakt już istnieje,
pluginy dostawców mogą się względem niego rejestrować, a pluginy kanałów/funkcji mogą z niego korzystać.

Jeśli możliwość jeszcze nie istnieje, właściwym krokiem jest zwykle:

1. zdefiniowanie brakującej możliwości w rdzeniu
2. udostępnienie jej przez API/runtime pluginów w sposób typowany
3. podłączenie kanałów/funkcji do tej możliwości
4. pozwolenie pluginom dostawców na rejestrowanie implementacji

Pozwala to zachować jawną własność i jednocześnie unikać zachowań rdzenia, które zależą od
jednego dostawcy albo od jednorazowej, specyficznej dla pluginu ścieżki kodu.

### Warstwowanie możliwości

Używaj tego modelu mentalnego, gdy decydujesz, gdzie powinien znajdować się kod:

- **warstwa możliwości rdzenia**: wspólna orkiestracja, polityki, fallbacki, zasady
  scalania konfiguracji, semantyka dostarczania i typowane kontrakty
- **warstwa pluginów dostawców**: API specyficzne dla dostawcy, uwierzytelnianie, katalogi modeli, synteza mowy,
  generowanie obrazów, przyszłe backendy wideo, endpointy użycia
- **warstwa pluginów kanałów/funkcji**: integracja Slack/Discord/voice-call/itp.,
  która korzysta z możliwości rdzenia i udostępnia je na konkretnej powierzchni

Na przykład TTS ma następujący kształt:

- rdzeń odpowiada za politykę TTS w czasie odpowiedzi, kolejność fallbacków, preferencje i dostarczanie do kanału
- `openai`, `elevenlabs` i `microsoft` odpowiadają za implementacje syntezy
- `voice-call` korzysta z pomocnika środowiska uruchomieniowego TTS dla telefonii

Ten sam wzorzec należy preferować dla przyszłych możliwości.

### Przykład pluginu firmy z wieloma możliwościami

Plugin firmy powinien z zewnątrz sprawiać wrażenie spójnego. Jeśli OpenClaw ma wspólne
kontrakty dla modeli, mowy, transkrypcji w czasie rzeczywistym, głosu w czasie rzeczywistym, rozumienia multimediów,
generowania obrazów, generowania wideo, pobierania z sieci i wyszukiwania w sieci,
dostawca może obsługiwać wszystkie swoje powierzchnie w jednym miejscu:

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

Istotne nie są dokładne nazwy helperów. Istotny jest kształt:

- jeden plugin obsługuje powierzchnię dostawcy
- rdzeń nadal odpowiada za kontrakty możliwości
- pluginy kanałów i funkcji korzystają z helperów `api.runtime.*`, a nie z kodu dostawcy
- testy kontraktowe mogą sprawdzać, że plugin zarejestrował możliwości, które
  deklaruje jako należące do niego

### Przykład możliwości: rozumienie wideo

OpenClaw już traktuje rozumienie obrazów/dźwięku/wideo jako jedną wspólną
możliwość. Obowiązuje tu ten sam model własności:

1. rdzeń definiuje kontrakt rozumienia multimediów
2. pluginy dostawców rejestrują odpowiednio `describeImage`, `transcribeAudio` i
   `describeVideo`
3. pluginy kanałów i funkcji korzystają ze wspólnego zachowania rdzenia zamiast
   łączyć się bezpośrednio z kodem dostawcy

Pozwala to uniknąć wbudowania założeń jednego dostawcy dotyczących wideo do rdzenia. Plugin odpowiada
za powierzchnię dostawcy; rdzeń odpowiada za kontrakt możliwości i zachowanie fallback.

Generowanie wideo korzysta już z tej samej sekwencji: rdzeń odpowiada za typowany
kontrakt możliwości i helper środowiska uruchomieniowego, a pluginy dostawców rejestrują
implementacje `api.registerVideoGenerationProvider(...)` względem niego.

Potrzebujesz konkretnej listy wdrożeniowej? Zobacz
[Capability Cookbook](/pl/plugins/architecture).

## Kontrakty i egzekwowanie

Powierzchnia API pluginów jest celowo typowana i scentralizowana w
`OpenClawPluginApi`. Ten kontrakt definiuje wspierane punkty rejestracji oraz
helpery środowiska uruchomieniowego, na których plugin może polegać.

Dlaczego ma to znaczenie:

- autorzy pluginów otrzymują jeden stabilny standard wewnętrzny
- rdzeń może odrzucać zduplikowaną własność, na przykład gdy dwa pluginy rejestrują ten sam
  identyfikator providera
- podczas uruchamiania można wyświetlić użyteczne diagnostyki dla nieprawidłowych rejestracji
- testy kontraktowe mogą egzekwować własność bundlowanych pluginów i zapobiegać cichemu dryfowi

Istnieją dwie warstwy egzekwowania:

1. **egzekwowanie rejestracji w środowisku uruchomieniowym**
   Rejestr pluginów waliduje rejestracje podczas ładowania pluginów. Przykłady:
   zduplikowane identyfikatory providerów, zduplikowane identyfikatory providerów mowy oraz nieprawidłowe
   rejestracje powodują diagnostyki pluginów zamiast niezdefiniowanego zachowania.
2. **testy kontraktowe**
   Bundlowane pluginy są przechwytywane w rejestrach kontraktowych podczas uruchomień testów, aby
   OpenClaw mógł jawnie sprawdzać własność. Dziś dotyczy to modeli
   providerów, providerów mowy, providerów wyszukiwania w sieci oraz własności rejestracji bundlowanych pluginów.

Praktyczny efekt jest taki, że OpenClaw z góry wie, który plugin obsługuje którą
powierzchnię. Dzięki temu rdzeń i kanały mogą komponować się bezproblemowo, ponieważ własność jest
zadeklarowana, typowana i testowalna, a nie ukryta.

### Co należy do kontraktu

Dobre kontrakty pluginów są:

- typowane
- małe
- specyficzne dla możliwości
- należące do rdzenia
- wielokrotnego użytku przez wiele pluginów
- używalne przez kanały/funkcje bez wiedzy o dostawcy

Złe kontrakty pluginów to:

- polityki specyficzne dla dostawcy ukryte w rdzeniu
- jednorazowe furtki dla pluginów omijające rejestr
- kod kanału sięgający bezpośrednio do implementacji dostawcy
- ad hoc obiekty środowiska uruchomieniowego, które nie są częścią `OpenClawPluginApi` ani
  `api.runtime`

W razie wątpliwości podnieś poziom abstrakcji: najpierw zdefiniuj możliwość, a potem
pozwól pluginom się do niej podłączać.

## Model wykonania

Natywne pluginy OpenClaw działają **w procesie** razem z Gateway. Nie są
sandboxowane. Załadowany natywny plugin ma tę samą granicę zaufania na poziomie procesu co
kod rdzenia.

Konsekwencje:

- natywny plugin może rejestrować narzędzia, handlery sieciowe, hooki i usługi
- błąd natywnego pluginu może spowodować awarię lub destabilizację gateway
- złośliwy natywny plugin jest równoważny dowolnemu wykonaniu kodu wewnątrz
  procesu OpenClaw

Zgodne bundle są domyślnie bezpieczniejsze, ponieważ OpenClaw obecnie traktuje je
jako pakiety metadanych/treści. W bieżących wydaniach oznacza to głównie bundlowane
Skills.

W przypadku pluginów niebundlowanych używaj list dozwolonych i jawnych ścieżek instalacji/ładowania. Traktuj
pluginy workspace jako kod czasu programowania, a nie domyślne rozwiązanie produkcyjne.

Dla nazw pakietów bundlowanych workspace, utrzymuj identyfikator pluginu zakotwiczony w nazwie npm:
domyślnie `@openclaw/<id>` albo zatwierdzony typowany sufiks, taki jak
`-provider`, `-plugin`, `-speech`, `-sandbox` lub `-media-understanding`, gdy
pakiet celowo udostępnia węższą rolę pluginu.

Ważna uwaga dotycząca zaufania:

- `plugins.allow` ufa **identyfikatorom pluginów**, a nie pochodzeniu źródła.
- Plugin workspace z tym samym identyfikatorem co bundlowany plugin celowo przesłania
  bundlowaną kopię, gdy taki plugin workspace jest włączony/na liście dozwolonych.
- Jest to normalne i przydatne przy lokalnym programowaniu, testowaniu poprawek i hotfixach.

## Granica eksportu

OpenClaw eksportuje możliwości, a nie wygodne szczegóły implementacyjne.

Zachowaj publiczną rejestrację możliwości. Ogranicz eksport helperów niebędących kontraktem:

- podścieżki helperów specyficznych dla bundlowanych pluginów
- podścieżki infrastruktury środowiska uruchomieniowego, które nie są przeznaczone jako publiczne API
- wygodne helpery specyficzne dla dostawców
- helpery konfiguracji/onboardingu, które są szczegółami implementacji

Niektóre podścieżki helperów bundlowanych pluginów nadal pozostają w wygenerowanej mapie eksportu SDK
ze względu na zgodność i utrzymanie bundlowanych pluginów. Obecne przykłady obejmują
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` oraz kilka szwów `plugin-sdk/matrix*`. Traktuj je jako
zastrzeżone eksporty szczegółów implementacyjnych, a nie jako zalecany wzorzec SDK dla
nowych pluginów firm trzecich.

## Potok ładowania

Podczas uruchamiania OpenClaw wykonuje z grubsza następujące kroki:

1. wykrywa kandydackie katalogi główne pluginów
2. odczytuje natywne lub zgodne manifesty bundle i metadane pakietów
3. odrzuca niebezpiecznych kandydatów
4. normalizuje konfigurację pluginów (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decyduje o włączeniu dla każdego kandydata
6. ładuje włączone natywne moduły przez jiti
7. wywołuje natywne hooki `register(api)` (lub `activate(api)` — legacy alias) i zbiera rejestracje do rejestru pluginów
8. udostępnia rejestr powierzchniom poleceń/środowiska uruchomieniowego

<Note>
`activate` to legacy alias dla `register` — loader rozwiązuje to, które z nich jest obecne (`def.register ?? def.activate`) i wywołuje je w tym samym miejscu. Wszystkie bundlowane pluginy używają `register`; dla nowych pluginów preferuj `register`.
</Note>

Bramki bezpieczeństwa działają **przed** wykonaniem w środowisku uruchomieniowym. Kandydaci są blokowani,
gdy entry wychodzi poza katalog główny pluginu, ścieżka ma uprawnienia do zapisu dla wszystkich albo
własność ścieżki wygląda podejrzanie w przypadku pluginów niebundlowanych.

### Zachowanie manifest-first

Manifest jest źródłem prawdy warstwy control plane. OpenClaw używa go do:

- identyfikacji pluginu
- wykrywania zadeklarowanych kanałów/Skills/schematu konfiguracji lub możliwości bundle
- walidacji `plugins.entries.<id>.config`
- rozszerzania etykiet/placeholderów Control UI
- wyświetlania metadanych instalacji/katalogu
- zachowania tanich deskryptorów aktywacji i konfiguracji bez ładowania środowiska uruchomieniowego pluginu

Dla natywnych pluginów moduł środowiska uruchomieniowego jest częścią data plane. Rejestruje
rzeczywiste zachowania, takie jak hooki, narzędzia, polecenia czy przepływy providerów.

Opcjonalne bloki manifestu `activation` i `setup` pozostają w control plane.
Są to deskryptory wyłącznie metadanych do planowania aktywacji i wykrywania konfiguracji;
nie zastępują rejestracji środowiska uruchomieniowego, `register(...)` ani `setupEntry`.
Pierwszy konsument aktywacji używa teraz wskazówek poleceń z manifestu do zawężania ładowania pluginów CLI,
gdy znane jest polecenie podstawowe, zamiast zawsze ładować z góry każdy plugin zdolny do CLI.

Wykrywanie konfiguracji preferuje teraz identyfikatory należące do deskryptorów, takie jak `setup.providers` i
`setup.cliBackends`, aby zawęzić pluginy kandydackie, zanim przejdzie do `setup-api`
dla pluginów, które nadal potrzebują hooków środowiska uruchomieniowego na etapie konfiguracji. Jeśli więcej niż
jeden wykryty plugin deklaruje ten sam znormalizowany identyfikator providera konfiguracji lub backendu CLI,
wyszukiwanie konfiguracji odmawia wyboru niejednoznacznego właściciela zamiast polegać na kolejności wykrywania.

### Co loader przechowuje w pamięci podręcznej

OpenClaw utrzymuje krótkotrwałe pamięci podręczne w procesie dla:

- wyników wykrywania
- danych rejestru manifestów
- załadowanych rejestrów pluginów

Te pamięci podręczne zmniejszają skokowe obciążenie przy uruchamianiu oraz narzut powtarzanych poleceń. Można o nich
bezpiecznie myśleć jako o krótkotrwałych pamięciach podręcznych wydajności, a nie o trwałości.

Uwaga dotycząca wydajności:

- Ustaw `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` lub
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, aby wyłączyć te pamięci podręczne.
- Dostosuj okna cache za pomocą `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` i
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Model rejestru

Załadowane pluginy nie modyfikują bezpośrednio losowych globalnych elementów rdzenia. Rejestrują się w
centralnym rejestrze pluginów.

Rejestr śledzi:

- rekordy pluginów (tożsamość, źródło, pochodzenie, status, diagnostyka)
- narzędzia
- legacy hooki i hooki typowane
- kanały
- providery
- handlery Gateway RPC
- trasy HTTP
- rejestratory CLI
- usługi działające w tle
- polecenia należące do pluginów

Funkcje rdzenia odczytują następnie dane z tego rejestru zamiast komunikować się bezpośrednio z modułami pluginów.
Dzięki temu ładowanie pozostaje jednokierunkowe:

- moduł pluginu -> rejestracja w rejestrze
- środowisko uruchomieniowe rdzenia -> korzystanie z rejestru

To rozdzielenie ma znaczenie dla łatwości utrzymania. Oznacza, że większość powierzchni rdzenia potrzebuje
tylko jednego punktu integracji: „odczytaj rejestr”, a nie „dodaj osobny wyjątek dla każdego modułu pluginu”.

## Callbacki wiązania konwersacji

Pluginy, które wiążą konwersację, mogą reagować, gdy zatwierdzenie zostanie rozstrzygnięte.

Użyj `api.onConversationBindingResolved(...)`, aby otrzymać callback po zatwierdzeniu lub odrzuceniu
żądania wiązania:

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

Pola payloadu callbacku:

- `status`: `"approved"` lub `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` lub `"deny"`
- `binding`: rozstrzygnięte wiązanie dla zatwierdzonych żądań
- `request`: podsumowanie oryginalnego żądania, wskazówka odłączenia, identyfikator nadawcy oraz
  metadane konwersacji

Ten callback służy wyłącznie do powiadamiania. Nie zmienia tego, kto może wiązać
konwersację, i uruchamia się po zakończeniu obsługi zatwierdzenia przez rdzeń.

## Hooki środowiska uruchomieniowego dostawcy

Pluginy dostawców mają teraz dwie warstwy:

- metadane manifestu: `providerAuthEnvVars` do taniego wyszukiwania env-auth providera
  przed załadowaniem środowiska uruchomieniowego, `providerAuthAliases` dla wariantów providera, które współdzielą
  uwierzytelnianie, `channelEnvVars` do taniego wyszukiwania env/setup kanału przed załadowaniem środowiska uruchomieniowego,
  oraz `providerAuthChoices` do tanich etykiet onboardingu/wyboru uwierzytelniania i
  metadanych flag CLI przed załadowaniem środowiska uruchomieniowego
- hooki czasu konfiguracji: `catalog` / legacy `discovery` oraz `applyConfigDefaults`
- hooki środowiska uruchomieniowego: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
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
politykę narzędzi. Te hooki stanowią powierzchnię rozszerzeń dla zachowań specyficznych dla dostawców bez
potrzeby tworzenia całkowicie własnego transportu wnioskowania.

Używaj manifestu `providerAuthEnvVars`, gdy provider ma poświadczenia oparte na zmiennych środowiskowych,
które ogólne ścieżki auth/status/model-picker powinny widzieć bez ładowania środowiska uruchomieniowego pluginu.
Używaj manifestu `providerAuthAliases`, gdy jeden identyfikator providera powinien ponownie używać
zmiennych środowiskowych, profili auth, auth opartego na konfiguracji i opcji onboardingu klucza API
innego identyfikatora providera. Używaj manifestu `providerAuthChoices`, gdy powierzchnie CLI
onboardingu/wyboru auth powinny znać identyfikator opcji providera, etykiety grup i proste
powiązanie auth z jedną flagą bez ładowania środowiska uruchomieniowego providera. Zachowaj `envVars`
środowiska uruchomieniowego providera dla wskazówek skierowanych do operatora, takich jak etykiety onboardingu lub
zmienne konfiguracji OAuth `client-id`/`client-secret`.

Używaj manifestu `channelEnvVars`, gdy kanał ma auth lub konfigurację opartą na zmiennych środowiskowych, które
ogólny fallback shell-env, sprawdzenia config/status lub prompty konfiguracji powinny widzieć
bez ładowania środowiska uruchomieniowego kanału.

### Kolejność hooków i sposób użycia

Dla pluginów modelu/providera OpenClaw wywołuje hooki mniej więcej w tej kolejności.
Kolumna „Kiedy używać” to szybki przewodnik decyzyjny.

| #   | Hook                              | Co robi                                                                                                        | Kiedy używać                                                                                                                               |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | Publikuje konfigurację providera do `models.providers` podczas generowania `models.json`                      | Provider posiada katalog lub domyślne wartości `baseUrl`                                                                                   |
| 2   | `applyConfigDefaults`             | Stosuje globalne domyślne wartości konfiguracji należące do providera podczas materializacji konfiguracji     | Wartości domyślne zależą od trybu auth, env lub semantyki rodziny modeli providera                                                        |
| --  | _(wbudowane wyszukiwanie modeli)_ | OpenClaw najpierw próbuje zwykłej ścieżki rejestru/katalogu                                                    | _(to nie jest hook pluginu)_                                                                                                               |
| 3   | `normalizeModelId`                | Normalizuje legacy aliasy identyfikatorów modeli lub aliasy wersji preview przed wyszukaniem                  | Provider odpowiada za czyszczenie aliasów przed rozstrzygnięciem kanonicznego modelu                                                      |
| 4   | `normalizeTransport`              | Normalizuje `api` / `baseUrl` rodziny providerów przed ogólnym złożeniem modelu                               | Provider odpowiada za czyszczenie transportu dla własnych identyfikatorów providera w tej samej rodzinie transportu                       |
| 5   | `normalizeConfig`                 | Normalizuje `models.providers.<id>` przed rozstrzygnięciem środowiska uruchomieniowego/providera             | Provider potrzebuje czyszczenia konfiguracji, które powinno znajdować się razem z pluginem; bundlowane helpery rodziny Google dodatkowo wspierają obsługiwane wpisy konfiguracji Google |
| 6   | `applyNativeStreamingUsageCompat` | Stosuje poprawki zgodności natywnego usage dla streamingu do providerów konfiguracji                           | Provider potrzebuje poprawek metadanych natywnego usage dla streamingu zależnych od endpointu                                             |
| 7   | `resolveConfigApiKey`             | Rozstrzyga auth oparty na znacznikach env dla providerów konfiguracji przed załadowaniem auth środowiska uruchomieniowego | Provider ma własne rozstrzyganie klucza API przez znaczniki env; `amazon-bedrock` ma tu także wbudowany resolver znaczników env AWS      |
| 8   | `resolveSyntheticAuth`            | Udostępnia lokalne/self-hosted lub oparte na konfiguracji auth bez utrwalania jawnego tekstu                  | Provider może działać z syntetycznym/lokalnym znacznikiem poświadczeń                                                                      |
| 9   | `resolveExternalAuthProfiles`     | Nakłada należące do providera zewnętrzne profile auth; domyślne `persistence` to `runtime-only` dla poświadczeń należących do CLI/aplikacji | Provider ponownie wykorzystuje zewnętrzne poświadczenia auth bez utrwalania skopiowanych tokenów odświeżania                              |
| 10  | `shouldDeferSyntheticProfileAuth` | Obniża priorytet zapisanych syntetycznych placeholderów profili względem auth opartego na env/konfiguracji    | Provider przechowuje syntetyczne placeholdery profili, które nie powinny mieć pierwszeństwa                                               |
| 11  | `resolveDynamicModel`             | Synchroniczny fallback dla należących do providera identyfikatorów modeli, których nie ma jeszcze w lokalnym rejestrze | Provider akceptuje dowolne identyfikatory modeli z upstreamu                                                                               |
| 12  | `prepareDynamicModel`             | Asynchroniczne rozgrzanie, po którym `resolveDynamicModel` uruchamia się ponownie                             | Provider potrzebuje metadanych sieciowych przed rozstrzygnięciem nieznanych identyfikatorów                                               |
| 13  | `normalizeResolvedModel`          | Końcowe przepisanie przed użyciem rozstrzygniętego modelu przez embedded runner                               | Provider potrzebuje przepisania transportu, ale nadal używa transportu rdzenia                                                            |
| 14  | `contributeResolvedModelCompat`   | Dodaje flagi zgodności dla modeli dostawcy działających za innym kompatybilnym transportem                    | Provider rozpoznaje własne modele na transportach proxy bez przejmowania providera                                                        |
| 15  | `capabilities`                    | Metadane transkryptu/narzędzi należące do providera używane przez współdzieloną logikę rdzenia               | Provider potrzebuje specyficznych niuansów transkryptu/rodziny providerów                                                                  |
| 16  | `normalizeToolSchemas`            | Normalizuje schematy narzędzi, zanim zobaczy je embedded runner                                               | Provider potrzebuje czyszczenia schematów dla rodziny transportu                                                                           |
| 17  | `inspectToolSchemas`              | Udostępnia diagnostyki schematów należące do providera po normalizacji                                        | Provider chce ostrzeżenia dotyczące słów kluczowych bez uczenia rdzenia zasad specyficznych dla providera                                 |
| 18  | `resolveReasoningOutputMode`      | Wybiera kontrakt wyjścia rozumowania natywny lub tagowany                                                     | Provider potrzebuje tagowanego rozumowania/końcowego wyjścia zamiast natywnych pól                                                        |
| 19  | `prepareExtraParams`              | Normalizacja parametrów żądania przed ogólnymi wrapperami opcji streamu                                       | Provider potrzebuje domyślnych parametrów żądania lub czyszczenia parametrów per provider                                                 |
| 20  | `createStreamFn`                  | Całkowicie zastępuje zwykłą ścieżkę streamu własnym transportem                                               | Provider potrzebuje własnego protokołu połączenia, a nie tylko wrappera                                                                   |
| 21  | `wrapStreamFn`                    | Wrapper strumienia po zastosowaniu ogólnych wrapperów                                                         | Provider potrzebuje wrapperów zgodności dla nagłówków/treści żądania/modelu bez własnego transportu                                       |
| 22  | `resolveTransportTurnState`       | Dołącza natywne nagłówki lub metadane transportu per turn                                                     | Provider chce, aby ogólne transporty wysyłały natywną dla providera tożsamość tury                                                        |
| 23  | `resolveWebSocketSessionPolicy`   | Dołącza natywne nagłówki WebSocket lub politykę cool-down sesji                                               | Provider chce, aby ogólne transporty WS dostrajały nagłówki sesji lub politykę fallback                                                   |
| 24  | `formatApiKey`                    | Formater profilu auth: zapisany profil staje się ciągiem `apiKey` dla środowiska uruchomieniowego            | Provider przechowuje dodatkowe metadane auth i potrzebuje własnego kształtu tokenu środowiska uruchomieniowego                            |
| 25  | `refreshOAuth`                    | Nadpisanie odświeżania OAuth dla własnych endpointów odświeżania lub polityki błędów odświeżania             | Provider nie pasuje do współdzielonych mechanizmów odświeżania `pi-ai`                                                                     |
| 26  | `buildAuthDoctorHint`             | Wskazówka naprawy dołączana, gdy odświeżanie OAuth się nie powiedzie                                          | Provider potrzebuje własnych wskazówek naprawy auth po nieudanym odświeżeniu                                                              |
| 27  | `matchesContextOverflowError`     | Matcher przepełnienia okna kontekstu należący do providera                                                    | Provider ma surowe błędy przepełnienia, których ogólna heurystyka by nie wykryła                                                          |
| 28  | `classifyFailoverReason`          | Klasyfikacja przyczyny failover należąca do providera                                                         | Provider potrafi mapować surowe błędy API/transportu na rate-limit/przeciążenie/itp.                                                      |
| 29  | `isCacheTtlEligible`              | Polityka cache promptów dla providerów proxy/backhaul                                                         | Provider potrzebuje bramkowania TTL cache specyficznego dla proxy                                                                          |
| 30  | `buildMissingAuthMessage`         | Zamiennik dla ogólnego komunikatu odzyskiwania po braku auth                                                  | Provider potrzebuje własnej wskazówki odzyskiwania po braku auth                                                                           |
| 31  | `suppressBuiltInModel`            | Ukrywanie nieaktualnych modeli upstream z opcjonalną wskazówką błędu dla użytkownika                         | Provider musi ukrywać nieaktualne wiersze upstream lub zastępować je wskazówką dostawcy                                                   |
| 32  | `augmentModelCatalog`             | Syntetyczne/końcowe wiersze katalogu dodawane po wykryciu                                                    | Provider potrzebuje syntetycznych wierszy forward-compat w `models list` i selektorach                                                    |
| 33  | `isBinaryThinking`                | Przełącznik rozumowania włącz/wyłącz dla providerów z binarnym thinkingiem                                    | Provider udostępnia wyłącznie binarne myślenie włącz/wyłącz                                                                                |
| 34  | `supportsXHighThinking`           | Obsługa rozumowania `xhigh` dla wybranych modeli                                                              | Provider chce `xhigh` tylko dla podzbioru modeli                                                                                           |
| 35  | `resolveDefaultThinkingLevel`     | Domyślny poziom `/think` dla konkretnej rodziny modeli                                                        | Provider odpowiada za domyślną politykę `/think` dla rodziny modeli                                                                        |
| 36  | `isModernModelRef`                | Matcher nowoczesnych modeli dla filtrów live profile i wyboru smoke                                           | Provider odpowiada za dopasowywanie preferowanych modeli live/smoke                                                                        |
| 37  | `prepareRuntimeAuth`              | Wymienia skonfigurowane poświadczenie na rzeczywisty token/klucz środowiska uruchomieniowego tuż przed wnioskowaniem | Provider potrzebuje wymiany tokenu lub krótkotrwałego poświadczenia żądania                                                               |
| 38  | `resolveUsageAuth`                | Rozstrzyga poświadczenia usage/billing dla `/usage` i powiązanych powierzchni statusu                         | Provider potrzebuje własnego parsowania tokenu usage/quota albo innych poświadczeń usage                                                   |
| 39  | `fetchUsageSnapshot`              | Pobiera i normalizuje snapshoty usage/quota specyficzne dla providera po rozstrzygnięciu auth                | Provider potrzebuje własnego endpointu usage albo parsera payloadu                                                                          |
| 40  | `createEmbeddingProvider`         | Buduje należący do providera adapter embeddingów dla pamięci/wyszukiwania                                     | Zachowanie embeddingów pamięci powinno należeć do pluginu providera                                                                         |
| 41  | `buildReplayPolicy`               | Zwraca politykę replay sterującą obsługą transkryptu dla providera                                            | Provider potrzebuje własnej polityki transkryptu (na przykład usuwania bloków myślenia)                                                    |
| 42  | `sanitizeReplayHistory`           | Przepisuje historię replay po ogólnym czyszczeniu transkryptu                                                 | Provider potrzebuje własnych przepisów replay wykraczających poza współdzielone helpery Compaction                                         |
| 43  | `validateReplayTurns`             | Końcowa walidacja lub przekształcanie tur replay przed embedded runnerem                                      | Transport providera potrzebuje bardziej rygorystycznej walidacji tur po ogólnym sanityzowaniu                                              |
| 44  | `onModelSelected`                 | Uruchamia skutki uboczne po wyborze modelu należące do providera                                              | Provider potrzebuje telemetrii lub własnego stanu providera, gdy model staje się aktywny                                                   |

`normalizeModelId`, `normalizeTransport` i `normalizeConfig` najpierw sprawdzają
dopasowany plugin providera, a następnie przechodzą do innych pluginów providerów obsługujących hooki,
dopóki któryś faktycznie nie zmieni identyfikatora modelu albo transportu/konfiguracji. Dzięki temu
shimy aliasów/providerów zgodności działają bez wymagania, by wywołujący wiedział, który
bundlowany plugin odpowiada za dane przepisanie. Jeśli żaden hook providera nie przepisze obsługiwanego
wpisu konfiguracji z rodziny Google, bundlowany normalizator konfiguracji Google nadal zastosuje to
czyszczenie zgodności.

Jeśli provider potrzebuje w pełni własnego protokołu połączenia lub własnego wykonawcy żądań,
to jest inna klasa rozszerzenia. Te hooki służą do zachowań providera, które nadal działają
w zwykłej pętli wnioskowania OpenClaw.

### Przykład providera

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
  oraz `wrapStreamFn`, ponieważ odpowiada za zgodność wprzód Claude 4.6,
  wskazówki dotyczące rodziny providerów, wskazówki naprawy auth,
  integrację z endpointem usage, kwalifikację do cache promptów, domyślne wartości konfiguracji zależne od auth,
  domyślną/adaptacyjną politykę myślenia Claude
  oraz specyficzne dla Anthropic kształtowanie streamu dla
  nagłówków beta, `/fast` / `serviceTier` i `context1m`.
- Specyficzne dla Claude helpery strumienia Anthropic pozostają na razie we
  własnym publicznym szwie `api.ts` / `contract-api.ts` bundlowanego pluginu. Ta powierzchnia pakietu
  eksportuje `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` oraz bardziej niskopoziomowe
  buildery wrapperów Anthropic zamiast rozszerzać ogólne SDK wokół reguł nagłówków beta
  jednego providera.
- OpenAI używa `resolveDynamicModel`, `normalizeResolvedModel` i
  `capabilities`, a także `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` i `isModernModelRef`,
  ponieważ odpowiada za zgodność wprzód GPT-5.4, bezpośrednią normalizację OpenAI
  `openai-completions` -> `openai-responses`, wskazówki auth uwzględniające Codex,
  ukrywanie Spark, syntetyczne wiersze listy OpenAI oraz politykę myślenia/modeli live GPT-5; rodzina strumieni `openai-responses-defaults`
  odpowiada za współdzielone natywne wrappery OpenAI Responses dla
  nagłówków atrybucji, `/fast`/`serviceTier`, szczegółowości tekstu, natywnego wyszukiwania w sieci Codex,
  kształtowania payloadu zgodności rozumowania oraz zarządzania kontekstem Responses.
- OpenRouter używa `catalog` oraz `resolveDynamicModel` i
  `prepareDynamicModel`, ponieważ provider działa jako pass-through i może ujawniać nowe
  identyfikatory modeli, zanim statyczny katalog OpenClaw zostanie zaktualizowany; używa też
  `capabilities`, `wrapStreamFn` i `isCacheTtlEligible`, aby utrzymać
  nagłówki żądań specyficzne dla providera, metadane routingu, poprawki rozumowania oraz
  politykę cache promptów poza rdzeniem. Jego polityka replay pochodzi z rodziny
  `passthrough-gemini`, podczas gdy rodzina strumieni `openrouter-thinking`
  odpowiada za wstrzykiwanie rozumowania proxy oraz pomijanie nieobsługiwanych modeli i `auto`.
- GitHub Copilot używa `catalog`, `auth`, `resolveDynamicModel` i
  `capabilities`, a także `prepareRuntimeAuth` i `fetchUsageSnapshot`, ponieważ
  potrzebuje należącego do providera logowania urządzenia, zachowania fallback modelu, niuansów
  transkryptu Claude, wymiany tokenu GitHub -> token Copilot oraz
  należącego do providera endpointu usage.
- OpenAI Codex używa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` i `augmentModelCatalog`, a także
  `prepareExtraParams`, `resolveUsageAuth` i `fetchUsageSnapshot`, ponieważ
  nadal działa na transportach rdzenia OpenAI, ale odpowiada za własną normalizację transportu/`baseUrl`,
  politykę fallback odświeżania OAuth, domyślny wybór transportu,
  syntetyczne wiersze katalogu Codex oraz integrację z endpointem usage ChatGPT; współdzieli tę samą rodzinę strumieni `openai-responses-defaults` co bezpośredni OpenAI.
- Google AI Studio i Gemini CLI OAuth używają `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` i `isModernModelRef`, ponieważ
  rodzina replay `google-gemini` odpowiada za fallback zgodności wprzód Gemini 3.1,
  natywną walidację replay Gemini, sanityzację replay bootstrap,
  tagowany tryb wyjścia rozumowania oraz dopasowywanie nowoczesnych modeli, podczas gdy
  rodzina strumieni `google-thinking` odpowiada za normalizację payloadu myślenia Gemini;
  Gemini CLI OAuth używa także `formatApiKey`, `resolveUsageAuth` i
  `fetchUsageSnapshot` do formatowania tokenu, parsowania tokenu i
  podłączenia endpointu quota.
- Anthropic Vertex używa `buildReplayPolicy` przez rodzinę replay
  `anthropic-by-model`, dzięki czemu czyszczenie replay specyficzne dla Claude pozostaje
  ograniczone do identyfikatorów Claude zamiast do każdego transportu `anthropic-messages`.
- Amazon Bedrock używa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` i `resolveDefaultThinkingLevel`, ponieważ odpowiada za
  klasyfikację błędów specyficznych dla Bedrock dotyczących throttlingu/braku gotowości/przepełnienia kontekstu
  dla ruchu Anthropic-on-Bedrock; jego polityka replay nadal współdzieli tę samą
  ochronę tylko dla Claude `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode i Opencode Go używają `buildReplayPolicy`
  przez rodzinę replay `passthrough-gemini`, ponieważ pośredniczą dla modeli Gemini
  przez transporty zgodne z OpenAI i potrzebują sanityzacji
  thought-signature Gemini bez natywnej walidacji replay Gemini ani
  przepisów bootstrap.
- MiniMax używa `buildReplayPolicy` przez rodzinę replay
  `hybrid-anthropic-openai`, ponieważ jeden provider obsługuje zarówno
  semantykę komunikatów Anthropic, jak i semantykę zgodną z OpenAI; zachowuje
  usuwanie bloków myślenia tylko dla Claude po stronie Anthropic, jednocześnie nadpisując tryb wyjścia
  rozumowania z powrotem na natywny, a rodzina strumieni `minimax-fast-mode` odpowiada za
  przepisywanie modeli fast-mode na współdzielonej ścieżce strumienia.
- Moonshot używa `catalog` oraz `wrapStreamFn`, ponieważ nadal korzysta ze współdzielonego
  transportu OpenAI, ale potrzebuje należącej do providera normalizacji payloadu myślenia; rodzina strumieni
  `moonshot-thinking` mapuje konfigurację oraz stan `/think` na swój
  natywny payload binarnego myślenia.
- Kilocode używa `catalog`, `capabilities`, `wrapStreamFn` oraz
  `isCacheTtlEligible`, ponieważ potrzebuje należących do providera nagłówków żądań,
  normalizacji payloadu rozumowania, wskazówek transkryptu Gemini oraz
  bramkowania cache-TTL Anthropic; rodzina strumieni `kilocode-thinking` utrzymuje wstrzykiwanie myślenia Kilo
  na współdzielonej ścieżce strumienia proxy, pomijając `kilo/auto` i
  inne identyfikatory modeli proxy, które nie obsługują jawnych payloadów rozumowania.
- Z.AI używa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` i `fetchUsageSnapshot`, ponieważ odpowiada za fallback GLM-5,
  domyślne `tool_stream`, UX binarnego myślenia, dopasowywanie nowoczesnych modeli oraz
  zarówno auth usage, jak i pobieranie quota; rodzina strumieni `tool-stream-default-on` utrzymuje
  wrapper `tool_stream` domyślnie włączony poza ręcznie pisanym klejem per provider.
- xAI używa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` i `isModernModelRef`,
  ponieważ odpowiada za natywną normalizację transportu xAI Responses, przepisywanie aliasów Grok fast-mode,
  domyślne `tool_stream`, czyszczenie strict-tool / payloadu rozumowania,
  ponowne użycie fallback auth dla narzędzi należących do pluginu, zgodne wprzód rozstrzyganie modeli Grok
  oraz poprawki zgodności należące do providera, takie jak profil schematu narzędzi xAI,
  nieobsługiwane słowa kluczowe schematu, natywne `web_search` i dekodowanie
  argumentów wywołań narzędzi z encji HTML.
- Mistral, OpenCode Zen i OpenCode Go używają wyłącznie `capabilities`, aby utrzymać
  niuanse transkryptu/narzędzi poza rdzeniem.
- Bundlowani providerzy tylko z katalogiem, tacy jak `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` i `volcengine`, używają
  wyłącznie `catalog`.
- Qwen używa `catalog` dla swojego providera tekstowego oraz współdzielonych rejestracji rozumienia multimediów
  i generowania wideo dla swoich powierzchni multimodalnych.
- MiniMax i Xiaomi używają `catalog` oraz hooków usage, ponieważ ich zachowanie `/usage`
  należy do pluginu, mimo że wnioskowanie nadal przebiega przez współdzielone transporty.

## Helpery środowiska uruchomieniowego

Pluginy mogą uzyskiwać dostęp do wybranych helperów rdzenia przez `api.runtime`. Dla TTS:

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
- Używa konfiguracji rdzenia `messages.tts` i wyboru providera.
- Zwraca bufor audio PCM + częstotliwość próbkowania. Pluginy muszą wykonać resampling/kodowanie dla providerów.
- `listVoices` jest opcjonalne dla każdego providera. Używaj go do selektorów głosów lub przepływów konfiguracji należących do dostawcy.
- Listy głosów mogą zawierać bogatsze metadane, takie jak locale, płeć i tagi osobowości dla selektorów świadomych providera.
- OpenAI i ElevenLabs obsługują dziś telefonię. Microsoft nie.

Pluginy mogą także rejestrować providery mowy przez `api.registerSpeechProvider(...)`.

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
- Używaj providerów mowy do zachowań syntezy należących do dostawców.
- Legacy wejście Microsoft `edge` jest normalizowane do identyfikatora providera `microsoft`.
- Preferowany model własności jest zorientowany na firmy: jeden plugin dostawcy może obsługiwać
  tekst, mowę, obraz i przyszłych providerów mediów, gdy OpenClaw dodaje te
  kontrakty możliwości.

Dla rozumienia obrazów/dźwięku/wideo pluginy rejestrują jednego typowanego
providera rozumienia multimediów zamiast ogólnego worka klucz/wartość:

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

- Zachowaj orkiestrację, fallbacki, konfigurację i powiązanie z kanałami w rdzeniu.
- Zachowaj zachowanie dostawcy w pluginie providera.
- Rozszerzanie addytywne powinno pozostać typowane: nowe opcjonalne metody, nowe opcjonalne
  pola wyników, nowe opcjonalne możliwości.
- Generowanie wideo już podąża za tym samym wzorcem:
  - rdzeń odpowiada za kontrakt możliwości i helper środowiska uruchomieniowego
  - pluginy dostawców rejestrują `api.registerVideoGenerationProvider(...)`
  - pluginy funkcji/kanałów korzystają z `api.runtime.videoGeneration.*`

Dla helperów środowiska uruchomieniowego media-understanding pluginy mogą wywoływać:

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

Do transkrypcji audio pluginy mogą używać albo środowiska uruchomieniowego media-understanding,
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
  rozumienia obrazów/dźwięku/wideo.
- Używa konfiguracji audio media-understanding rdzenia (`tools.media.audio`) oraz kolejności fallback providerów.
- Zwraca `{ text: undefined }`, gdy nie zostanie wygenerowana transkrypcja (na przykład dla pominiętego/nieobsługiwanego wejścia).
- `api.runtime.stt.transcribeAudioFile(...)` pozostaje aliasem zgodności.

Pluginy mogą również uruchamiać w tle przebiegi subagentów przez `api.runtime.subagent`:

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

- `provider` i `model` to opcjonalne nadpisania dla pojedynczego uruchomienia, a nie trwałe zmiany sesji.
- OpenClaw uwzględnia te pola nadpisania tylko dla zaufanych wywołujących.
- Dla przebiegów fallback należących do pluginu operatorzy muszą jawnie wyrazić zgodę przez `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Użyj `plugins.entries.<id>.subagent.allowedModels`, aby ograniczyć zaufane pluginy do konkretnych kanonicznych celów `provider/model`, albo `"*"`, aby jawnie dopuścić dowolny cel.
- Uruchomienia subagentów przez niezaufane pluginy nadal działają, ale żądania nadpisania są odrzucane zamiast po cichu przechodzić do fallback.

W przypadku wyszukiwania w sieci pluginy mogą korzystać ze współdzielonego helpera środowiska uruchomieniowego zamiast
sięgać do powiązań narzędzia agenta:

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

Pluginy mogą także rejestrować providery wyszukiwania w sieci przez
`api.registerWebSearchProvider(...)`.

Uwagi:

- Zachowaj wybór providera, rozstrzyganie poświadczeń i współdzieloną semantykę żądań w rdzeniu.
- Używaj providerów wyszukiwania w sieci dla transportów wyszukiwania specyficznych dla dostawcy.
- `api.runtime.webSearch.*` to preferowana współdzielona powierzchnia dla pluginów funkcji/kanałów, które potrzebują zachowania wyszukiwania bez zależności od wrappera narzędzia agenta.

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

- `generate(...)`: generuje obraz przy użyciu skonfigurowanego łańcucha providerów generowania obrazów.
- `listProviders(...)`: wyświetla dostępnych providerów generowania obrazów i ich możliwości.

## Trasy HTTP Gateway

Pluginy mogą udostępniać endpointy HTTP przez `api.registerHttpRoute(...)`.

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
- `auth`: wymagane. Użyj `"gateway"`, aby wymagać normalnego auth gateway, albo `"plugin"` dla auth zarządzanego przez plugin / weryfikacji Webhook.
- `match`: opcjonalne. `"exact"` (domyślnie) albo `"prefix"`.
- `replaceExisting`: opcjonalne. Pozwala temu samemu pluginowi zastąpić własną istniejącą rejestrację trasy.
- `handler`: zwróć `true`, gdy trasa obsłużyła żądanie.

Uwagi:

- `api.registerHttpHandler(...)` zostało usunięte i spowoduje błąd ładowania pluginu. Zamiast tego używaj `api.registerHttpRoute(...)`.
- Trasy pluginów muszą jawnie deklarować `auth`.
- Konflikty dokładnego `path + match` są odrzucane, chyba że ustawiono `replaceExisting: true`, i jeden plugin nie może zastąpić trasy innego pluginu.
- Nakładające się trasy z różnymi poziomami `auth` są odrzucane. Zachowuj łańcuchy przechodzenia `exact`/`prefix` tylko w obrębie tego samego poziomu auth.
- Trasy `auth: "plugin"` **nie** otrzymują automatycznie zakresów środowiska uruchomieniowego operatora. Służą do webhooków zarządzanych przez plugin / weryfikacji podpisów, a nie do uprzywilejowanych wywołań pomocników Gateway.
- Trasy `auth: "gateway"` działają w zakresie środowiska uruchomieniowego żądania Gateway, ale ten zakres jest celowo zachowawczy:
  - auth bearer ze wspólnym sekretem (`gateway.auth.mode = "token"` / `"password"`) utrzymuje zakresy środowiska uruchomieniowego tras pluginów przypięte do `operator.write`, nawet jeśli wywołujący wysyła `x-openclaw-scopes`
  - zaufane tryby HTTP przenoszące tożsamość (na przykład `trusted-proxy` lub `gateway.auth.mode = "none"` na prywatnym ingressie) honorują `x-openclaw-scopes` tylko wtedy, gdy nagłówek jest jawnie obecny
  - jeśli `x-openclaw-scopes` jest nieobecne w takich żądaniach tras pluginów przenoszących tożsamość, zakres środowiska uruchomieniowego wraca do `operator.write`
- Praktyczna zasada: nie zakładaj, że trasa pluginu z auth gateway jest domyślnie powierzchnią administracyjną. Jeśli Twoja trasa wymaga zachowania tylko dla administratora, wymagaj trybu auth przenoszącego tożsamość i udokumentuj jawny kontrakt nagłówka `x-openclaw-scopes`.

## Ścieżki importu Plugin SDK

Przy tworzeniu pluginów używaj podścieżek SDK zamiast monolitycznego importu `openclaw/plugin-sdk`:

- `openclaw/plugin-sdk/plugin-entry` dla prymitywów rejestracji pluginów.
- `openclaw/plugin-sdk/core` dla ogólnego współdzielonego kontraktu skierowanego do pluginów.
- `openclaw/plugin-sdk/config-schema` dla eksportu głównego schematu Zod `openclaw.json`
  (`OpenClawSchema`).
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
  `openclaw/plugin-sdk/secret-input` oraz
  `openclaw/plugin-sdk/webhook-ingress` do współdzielonego powiązania konfiguracji/auth/odpowiedzi/webhooków.
  `channel-inbound` to współdzielony dom dla debounce, dopasowywania wzmianek,
  helperów zasad przychodzących wzmianek, formatowania envelope oraz helperów
  kontekstu inbound envelope.
  `channel-setup` to wąski szew konfiguracji opcjonalnej instalacji.
  `setup-runtime` to bezpieczna dla runtime powierzchnia konfiguracji używana przez `setupEntry` /
  odroczone uruchamianie, w tym adaptery poprawek konfiguracji bezpieczne dla importu.
  `setup-adapter-runtime` to świadomy env szew adaptera konfiguracji konta.
  `setup-tools` to mały szew pomocników CLI/archiwów/dokumentacji (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Podścieżki domenowe, takie jak `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` oraz
  `openclaw/plugin-sdk/directory-runtime` dla współdzielonych helperów środowiska uruchomieniowego/konfiguracji.
  `telegram-command-config` to wąski publiczny szew dla normalizacji/walidacji niestandardowych
  poleceń Telegram i pozostaje dostępny nawet wtedy, gdy powierzchnia kontraktu bundlowanego
  Telegram jest chwilowo niedostępna.
  `text-runtime` to współdzielony szew tekstu/Markdown/logowania, obejmujący
  usuwanie tekstu widocznego dla asystenta, helpery renderowania/dzielenia Markdown, helpery redakcji,
  helpery tagów dyrektyw i narzędzia safe-text.
- Szwy kanałów specyficzne dla zatwierdzeń powinny preferować jeden kontrakt `approvalCapability`
  na pluginie. Rdzeń odczytuje wtedy auth zatwierdzeń, dostarczanie, renderowanie,
  natywny routing i zachowanie leniwego natywnego handlera przez tę jedną możliwość
  zamiast mieszać zachowanie zatwierdzeń z niepowiązanymi polami pluginu.
- `openclaw/plugin-sdk/channel-runtime` jest przestarzałe i pozostaje jedynie jako
  shim zgodności dla starszych pluginów. Nowy kod powinien importować zamiast tego węższe
  ogólne prymitywy, a kod repo nie powinien dodawać nowych importów tego shimu.
- Wewnętrzne elementy bundlowanych rozszerzeń pozostają prywatne. Zewnętrzne pluginy powinny używać tylko
  podścieżek `openclaw/plugin-sdk/*`. Kod rdzenia/testów OpenClaw może używać publicznych
  punktów wejścia repo pod katalogiem głównym pakietu pluginu, takich jak `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` i wąsko określone pliki, takie jak
  `login-qr-api.js`. Nigdy nie importuj `src/*` pakietu pluginu z rdzenia ani z
  innego rozszerzenia.
- Podział punktów wejścia repo:
  `<plugin-package-root>/api.js` to barrel helperów/typów,
  `<plugin-package-root>/runtime-api.js` to barrel tylko dla runtime,
  `<plugin-package-root>/index.js` to punkt wejścia bundlowanego pluginu,
  a `<plugin-package-root>/setup-entry.js` to punkt wejścia pluginu konfiguracji.
- Obecne przykłady bundlowanych providerów:
  - Anthropic używa `api.js` / `contract-api.js` dla helperów strumienia Claude, takich
    jak `wrapAnthropicProviderStream`, helpery nagłówków beta i parsowanie `service_tier`.
  - OpenAI używa `api.js` dla builderów providerów, helperów modeli domyślnych i
    builderów providerów realtime.
  - OpenRouter używa `api.js` dla swojego buildera providera oraz helperów onboardingu/konfiguracji,
    podczas gdy `register.runtime.js` nadal może reeksportować ogólne
    helpery `plugin-sdk/provider-stream` do użytku lokalnego w repo.
- Publiczne punkty wejścia ładowane przez fasadę preferują aktywny snapshot konfiguracji runtime,
  gdy taki istnieje, a następnie wracają do rozstrzygniętego pliku konfiguracji na dysku, gdy
  OpenClaw nie udostępnia jeszcze snapshotu runtime.
- Ogólne współdzielone prymitywy pozostają preferowanym publicznym kontraktem SDK. Nadal istnieje
  mały, zastrzeżony zestaw szwów helperów oznaczonych markami bundlowanych kanałów dla zgodności.
  Traktuj je jako szwy utrzymaniowe/zgodności dla bundli, a nie jako nowe cele importu dla firm trzecich;
  nowe kontrakty międzykanałowe nadal powinny trafiać do ogólnych podścieżek `plugin-sdk/*` albo do lokalnych barrelów pluginu `api.js` /
  `runtime-api.js`.

Uwaga dotycząca zgodności:

- Unikaj głównego barrela `openclaw/plugin-sdk` w nowym kodzie.
- Najpierw preferuj wąskie stabilne prymitywy. Nowsze podścieżki setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool są zamierzonym kontraktem dla nowych
  bundlowanych i zewnętrznych pluginów.
  Parsowanie/dopasowywanie celów należy umieszczać w `openclaw/plugin-sdk/channel-targets`.
  Bramki działań wiadomości i helpery identyfikatorów wiadomości reakcji należą do
  `openclaw/plugin-sdk/channel-actions`.
- Barlle helperów specyficznych dla bundlowanych rozszerzeń nie są domyślnie stabilne. Jeśli
  helper jest potrzebny tylko bundlowanemu rozszerzeniu, trzymaj go za lokalnym
  szwem `api.js` lub `runtime-api.js` tego rozszerzenia zamiast promować go do
  `openclaw/plugin-sdk/<extension>`.
- Nowe współdzielone szwy helperów powinny być ogólne, a nie oznaczone marką kanału. Wspólne parsowanie
  celów należy umieszczać w `openclaw/plugin-sdk/channel-targets`; wewnętrzne elementy specyficzne dla kanału
  pozostają za lokalnym szwem `api.js` lub `runtime-api.js` należącego do danego pluginu.
- Podścieżki specyficzne dla możliwości, takie jak `image-generation`,
  `media-understanding` i `speech`, istnieją, ponieważ bundlowane/natywne pluginy używają
  ich już dziś. Ich obecność sama w sobie nie oznacza, że każdy eksportowany helper jest
  długoterminowym zamrożonym kontraktem zewnętrznym.

## Schematy narzędzia message

Pluginy powinny obsługiwać wkłady do schematu `describeMessageTool(...)` specyficzne dla kanału.
Pola specyficzne dla dostawcy powinny pozostać w pluginie, a nie we współdzielonym rdzeniu.

Dla współdzielonych przenośnych fragmentów schematu używaj ponownie ogólnych helperów eksportowanych przez
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` dla payloadów w stylu siatki przycisków
- `createMessageToolCardSchema()` dla strukturalnych payloadów kart

Jeśli dany kształt schematu ma sens tylko dla jednego dostawcy, zdefiniuj go we
własnym źródle tego pluginu zamiast promować go do współdzielonego SDK.

## Rozstrzyganie celów kanału

Pluginy kanałów powinny obsługiwać semantykę celów specyficzną dla kanału. Zachowaj
wspólny host outbound jako ogólny i używaj powierzchni adaptera komunikacyjnego dla reguł dostawcy:

- `messaging.inferTargetChatType({ to })` decyduje, czy znormalizowany cel
  powinien być traktowany jako `direct`, `group` czy `channel` przed wyszukaniem w katalogu.
- `messaging.targetResolver.looksLikeId(raw, normalized)` informuje rdzeń, czy
  dane wejście powinno pominąć wyszukiwanie w katalogu i przejść od razu do rozstrzygania podobnego do identyfikatora.
- `messaging.targetResolver.resolveTarget(...)` to fallback pluginu, gdy
  rdzeń potrzebuje końcowego rozstrzygnięcia należącego do dostawcy po normalizacji albo po
  braku trafienia w katalogu.
- `messaging.resolveOutboundSessionRoute(...)` odpowiada za specyficzne dla dostawcy
  konstruowanie trasy sesji po rozstrzygnięciu celu.

Zalecany podział:

- Używaj `inferTargetChatType` do decyzji kategorycznych, które powinny zapaść przed
  wyszukiwaniem peerów/grup.
- Używaj `looksLikeId` do sprawdzania typu „traktuj to jako jawny/natywny identyfikator celu”.
- Używaj `resolveTarget` do fallbacku normalizacji specyficznej dla dostawcy, a nie do
  szerokiego wyszukiwania w katalogu.
- Natywne identyfikatory dostawcy, takie jak identyfikatory czatów, identyfikatory wątków, JID-y, handlery i identyfikatory pokoi,
  trzymaj wewnątrz wartości `target` albo parametrów specyficznych dla dostawcy, a nie w ogólnych polach SDK.

## Katalogi oparte na konfiguracji

Pluginy, które wyprowadzają wpisy katalogu z konfiguracji, powinny utrzymywać tę logikę w
pluginie i ponownie używać współdzielonych helperów z
`openclaw/plugin-sdk/directory-runtime`.

Używaj tego, gdy kanał potrzebuje peerów/grup opartych na konfiguracji, takich jak:

- peery DM sterowane przez allowlist
- skonfigurowane mapy kanałów/grup
- statyczne fallbacki katalogu z zakresem konta

Współdzielone helpery w `directory-runtime` obsługują tylko operacje ogólne:

- filtrowanie zapytań
- stosowanie limitów
- helpery deduplikacji/normalizacji
- budowanie `ChannelDirectoryEntry[]`

Inspekcja konta i normalizacja identyfikatorów specyficzne dla kanału powinny pozostać w
implementacji pluginu.

## Katalogi providerów

Pluginy dostawców mogą definiować katalogi modeli dla wnioskowania przez
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` zwraca ten sam kształt, który OpenClaw zapisuje do
`models.providers`:

- `{ provider }` dla jednego wpisu providera
- `{ providers }` dla wielu wpisów providerów

Używaj `catalog`, gdy plugin odpowiada za identyfikatory modeli specyficzne dla providera, wartości domyślne `baseUrl`
albo metadane modeli zależne od auth.

`catalog.order` kontroluje, kiedy katalog pluginu scala się względem wbudowanych
niejawnych providerów OpenClaw:

- `simple`: providerzy z prostym kluczem API lub sterowani env
- `profile`: providerzy pojawiający się, gdy istnieją profile auth
- `paired`: providerzy syntetyzujący wiele powiązanych wpisów providerów
- `late`: ostatnie przejście, po innych niejawnych providerach

Późniejsi providerzy wygrywają przy kolizji kluczy, więc pluginy mogą celowo nadpisywać
wbudowany wpis providera o tym samym identyfikatorze providera.

Zgodność:

- `discovery` nadal działa jako legacy alias
- jeśli zarejestrowane są jednocześnie `catalog` i `discovery`, OpenClaw używa `catalog`

## Inspekcja kanałów tylko do odczytu

Jeśli Twój plugin rejestruje kanał, preferuj implementację
`plugin.config.inspectAccount(cfg, accountId)` obok `resolveAccount(...)`.

Dlaczego:

- `resolveAccount(...)` to ścieżka środowiska uruchomieniowego. Może zakładać, że poświadczenia
  są w pełni zmaterializowane, i może szybko zakończyć się błędem, gdy brakuje wymaganych sekretów.
- Ścieżki poleceń tylko do odczytu, takie jak `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` oraz przepływy doctor/naprawy
  konfiguracji nie powinny wymagać materializacji poświadczeń środowiska uruchomieniowego tylko po to, aby
  opisać konfigurację.

Zalecane zachowanie `inspectAccount(...)`:

- Zwracaj wyłącznie opisowy stan konta.
- Zachowuj `enabled` i `configured`.
- Dołączaj pola źródła/statusu poświadczeń, gdy ma to znaczenie, takie jak:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Nie musisz zwracać surowych wartości tokenów tylko po to, by raportować dostępność
  tylko do odczytu. Do poleceń typu status wystarczy zwrócić `tokenStatus: "available"` (oraz odpowiadające mu pole źródła).
- Używaj `configured_unavailable`, gdy poświadczenie jest skonfigurowane przez SecretRef, ale
  niedostępne w bieżącej ścieżce polecenia.

Dzięki temu polecenia tylko do odczytu mogą raportować „skonfigurowano, ale niedostępne w tej ścieżce polecenia”
zamiast kończyć się awarią lub błędnie raportować konto jako nieskonfigurowane.

## Pakiety zbiorcze

Katalog pluginu może zawierać `package.json` z `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Każdy wpis staje się pluginem. Jeśli pakiet zbiorczy zawiera wiele rozszerzeń, identyfikator pluginu
przyjmuje postać `name/<fileBase>`.

Jeśli Twój plugin importuje zależności npm, zainstaluj je w tym katalogu, aby
`node_modules` było dostępne (`npm install` / `pnpm install`).

Bariera bezpieczeństwa: każdy wpis `openclaw.extensions` musi pozostać wewnątrz katalogu pluginu
po rozstrzygnięciu symlinków. Wpisy wychodzące poza katalog pakietu są
odrzucane.

Uwaga dotycząca bezpieczeństwa: `openclaw plugins install` instaluje zależności pluginu przez
`npm install --omit=dev --ignore-scripts` (bez skryptów cyklu życia, bez zależności deweloperskich w runtime). Utrzymuj drzewa zależności pluginów jako „czyste JS/TS” i unikaj pakietów wymagających kompilacji w `postinstall`.

Opcjonalnie: `openclaw.setupEntry` może wskazywać lekki moduł tylko do konfiguracji.
Gdy OpenClaw potrzebuje powierzchni konfiguracji dla wyłączonego pluginu kanału albo
gdy plugin kanału jest włączony, ale nadal nieskonfigurowany, ładuje `setupEntry`
zamiast pełnego punktu wejścia pluginu. Dzięki temu uruchamianie i konfiguracja pozostają lżejsze,
gdy główny punkt wejścia pluginu podłącza także narzędzia, hooki lub inny kod wyłącznie runtime.

Opcjonalnie: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
może włączyć plugin kanału do korzystania z tej samej ścieżki `setupEntry` podczas fazy
uruchamiania gateway przed `listen`, nawet gdy kanał jest już skonfigurowany.

Używaj tego tylko wtedy, gdy `setupEntry` w pełni pokrywa powierzchnię uruchamiania, która musi istnieć
zanim gateway zacznie nasłuchiwać. W praktyce oznacza to, że punkt wejścia konfiguracji
musi rejestrować każdą możliwość należącą do kanału, od której zależy uruchamianie, taką jak:

- sama rejestracja kanału
- wszelkie trasy HTTP, które muszą być dostępne przed rozpoczęciem nasłuchiwania przez gateway
- wszelkie metody gateway, narzędzia lub usługi, które muszą istnieć w tym samym oknie czasowym

Jeśli Twój pełny punkt wejścia nadal obsługuje jakąkolwiek wymaganą możliwość uruchamiania, nie włączaj
tej flagi. Pozostaw plugin przy domyślnym zachowaniu i pozwól OpenClaw załadować
pełny punkt wejścia podczas uruchamiania.

Bundlowane kanały mogą również publikować helpery powierzchni kontraktu tylko do konfiguracji, z których rdzeń
może korzystać przed załadowaniem pełnego środowiska uruchomieniowego kanału. Obecna powierzchnia
promowania konfiguracji to:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Rdzeń używa tej powierzchni, gdy musi awansować legacy konfigurację kanału z jednym kontem
do `channels.<id>.accounts.*` bez ładowania pełnego punktu wejścia pluginu.
Obecnym bundlowanym przykładem jest Matrix: przenosi tylko klucze auth/bootstrap do
nazwanego awansowanego konta, gdy nazwane konta już istnieją, i potrafi zachować
skonfigurowany niekanoniczny klucz konta domyślnego zamiast zawsze tworzyć
`accounts.default`.

Te adaptery poprawek konfiguracji utrzymują leniwe wykrywanie powierzchni kontraktu bundli. Czas
importu pozostaje niski; powierzchnia promowania jest ładowana dopiero przy pierwszym użyciu, zamiast
ponownie wchodzić w uruchamianie bundlowanego kanału podczas importu modułu.

Gdy te powierzchnie uruchamiania obejmują metody Gateway RPC, utrzymuj je pod
prefiksem specyficznym dla pluginu. Przestrzenie nazw administratora rdzenia (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) pozostają zastrzeżone i zawsze są rozstrzygane
do `operator.admin`, nawet jeśli plugin żąda węższego zakresu.

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

Pluginy kanałów mogą reklamować metadane konfiguracji/wykrywania przez `openclaw.channel` oraz
wskazówki instalacyjne przez `openclaw.install`. Dzięki temu dane katalogowe rdzenia pozostają wolne od danych statycznych.

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
      "blurb": "Samohostowany czat przez boty webhook Nextcloud Talk.",
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
- `docsLabel`: nadpisanie tekstu linku do dokumentacji
- `preferOver`: identyfikatory pluginów/kanałów o niższym priorytecie, które ten wpis katalogu powinien wyprzedzać
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: kontrolki tekstu powierzchni wyboru
- `markdownCapable`: oznacza kanał jako zdolny do Markdown dla decyzji o formatowaniu outbound
- `exposure.configured`: ukrywa kanał z powierzchni listy skonfigurowanych kanałów, gdy ustawione na `false`
- `exposure.setup`: ukrywa kanał z interaktywnych selektorów konfiguracji/ustawień, gdy ustawione na `false`
- `exposure.docs`: oznacza kanał jako wewnętrzny/prywatny dla powierzchni nawigacji dokumentacji
- `showConfigured` / `showInSetup`: legacy aliasy nadal akceptowane dla zgodności; preferuj `exposure`
- `quickstartAllowFrom`: włącza kanał do standardowego przepływu szybkiego startu `allowFrom`
- `forceAccountBinding`: wymaga jawnego powiązania konta nawet wtedy, gdy istnieje tylko jedno konto
- `preferSessionLookupForAnnounceTarget`: preferuje wyszukiwanie sesji przy rozstrzyganiu celów ogłoszeń

OpenClaw może również scalać **zewnętrzne katalogi kanałów** (na przykład eksport
rejestru MPM). Umieść plik JSON w jednej z lokalizacji:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Albo wskaż `OPENCLAW_PLUGIN_CATALOG_PATHS` (lub `OPENCLAW_MPM_CATALOG_PATHS`) na
jeden lub więcej plików JSON (rozdzielanych przecinkami/średnikami/w stylu `PATH`). Każdy plik powinien
zawierać `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Parser akceptuje także `"packages"` lub `"plugins"` jako legacy aliasy klucza `"entries"`.

## Pluginy silnika kontekstu

Pluginy silnika kontekstu odpowiadają za orkiestrację kontekstu sesji dla ingestu, składania
i Compaction. Rejestruj je ze swojego pluginu przez
`api.registerContextEngine(id, factory)`, a następnie wybieraj aktywny silnik przez
`plugins.slots.contextEngine`.

Używaj tego, gdy Twój plugin musi zastąpić lub rozszerzyć domyślny potok kontekstu,
a nie tylko dodać wyszukiwanie pamięci lub hooki.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Jeśli Twój silnik **nie** obsługuje algorytmu Compaction, pozostaw zaimplementowane `compact()`
i jawnie deleguj je dalej:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

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
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Dodawanie nowej możliwości

Gdy plugin potrzebuje zachowania, które nie pasuje do obecnego API, nie obchodź
systemu pluginów przez prywatne sięganie do wnętrza. Dodaj brakującą możliwość.

Zalecana sekwencja:

1. zdefiniuj kontrakt rdzenia
   Zdecyduj, jakie współdzielone zachowanie powinien obsługiwać rdzeń: politykę, fallback, scalanie konfiguracji,
   cykl życia, semantykę skierowaną do kanałów i kształt helpera środowiska uruchomieniowego.
2. dodaj typowane powierzchnie rejestracji/runtime pluginów
   Rozszerz `OpenClawPluginApi` i/lub `api.runtime` o najmniejszą użyteczną
   typowaną powierzchnię możliwości.
3. podłącz konsumentów rdzenia oraz pluginy kanałów/funkcji
   Pluginy kanałów i funkcji powinny korzystać z nowej możliwości przez rdzeń,
   a nie przez bezpośredni import implementacji dostawcy.
4. zarejestruj implementacje dostawców
   Pluginy dostawców następnie rejestrują swoje backendy względem tej możliwości.
5. dodaj pokrycie kontraktowe
   Dodaj testy, aby własność i kształt rejestracji pozostawały z czasem jawne.

W ten sposób OpenClaw zachowuje zdecydowane podejście bez stawania się rozwiązaniem zakodowanym na sztywno
pod światopogląd jednego dostawcy. Zobacz [Capability Cookbook](/pl/plugins/architecture),
aby przejrzeć konkretną listę plików i gotowy przykład.

### Lista kontrolna możliwości

Gdy dodajesz nową możliwość, implementacja zwykle powinna obejmować razem te
powierzchnie:

- typy kontraktu rdzenia w `src/<capability>/types.ts`
- runner/helper środowiska uruchomieniowego rdzenia w `src/<capability>/runtime.ts`
- powierzchnię rejestracji API pluginów w `src/plugins/types.ts`
- powiązanie rejestru pluginów w `src/plugins/registry.ts`
- udostępnienie środowiska uruchomieniowego pluginów w `src/plugins/runtime/*`, gdy pluginy funkcji/kanałów
  muszą z niego korzystać
- helpery przechwytywania/testów w `src/test-utils/plugin-registration.ts`
- asercje własności/kontraktu w `src/plugins/contracts/registry.ts`
- dokumentację operatora/pluginów w `docs/`

Jeśli którejś z tych powierzchni brakuje, zwykle jest to znak, że możliwość nie została jeszcze
w pełni zintegrowana.

### Szablon możliwości

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

Dzięki temu zasada pozostaje prosta:

- rdzeń odpowiada za kontrakt możliwości i orkiestrację
- pluginy dostawców odpowiadają za implementacje dostawców
- pluginy funkcji/kanałów korzystają z helperów środowiska uruchomieniowego
- testy kontraktowe utrzymują jawną własność
