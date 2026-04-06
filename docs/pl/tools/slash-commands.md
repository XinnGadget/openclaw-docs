---
read_when:
    - Używasz lub konfigurujesz polecenia czatu
    - Debugujesz routing poleceń lub uprawnienia
summary: 'Polecenia slash: tekstowe vs natywne, konfiguracja i obsługiwane polecenia'
title: Polecenia slash
x-i18n:
    generated_at: "2026-04-06T03:14:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 417e35b9ddd87f25f6c019111b55b741046ea11039dde89210948185ced5696d
    source_path: tools/slash-commands.md
    workflow: 15
---

# Polecenia slash

Polecenia są obsługiwane przez Gateway. Większość poleceń musi być wysłana jako **samodzielna** wiadomość zaczynająca się od `/`.
Dostępne tylko na hoście polecenie bash na czacie używa `! <cmd>` (z aliasem `/bash <cmd>`).

Istnieją dwa powiązane systemy:

- **Polecenia**: samodzielne wiadomości `/...`.
- **Dyrektywy**: `/think`, `/fast`, `/verbose`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Dyrektywy są usuwane z wiadomości, zanim zobaczy ją model.
  - W zwykłych wiadomościach czatu (nie tylko z samymi dyrektywami) są traktowane jako „wskazówki inline” i **nie** utrwalają ustawień sesji.
  - W wiadomościach zawierających tylko dyrektywy (wiadomość zawiera wyłącznie dyrektywy) są utrwalane w sesji i odpowiadają potwierdzeniem.
  - Dyrektywy są stosowane tylko dla **autoryzowanych nadawców**. Jeśli ustawiono `commands.allowFrom`, jest to jedyna
    allowlista używana dla dyrektyw; w przeciwnym razie autoryzacja pochodzi z allowlist/parowania kanałów oraz `commands.useAccessGroups`.
    Nieautoryzowani nadawcy widzą dyrektywy traktowane jak zwykły tekst.

Istnieje też kilka **skrótów inline** (tylko dla nadawców z allowlisty/autoryzowanych): `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Uruchamiają się natychmiast, są usuwane, zanim model zobaczy wiadomość, a pozostały tekst przechodzi dalej normalnym przepływem.

## Konfiguracja

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: false,
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (domyślnie `true`) włącza parsowanie `/...` w wiadomościach czatu.
  - Na powierzchniach bez natywnych poleceń (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams) polecenia tekstowe nadal działają, nawet jeśli ustawisz to na `false`.
- `commands.native` (domyślnie `"auto"`) rejestruje natywne polecenia.
  - Auto: włączone dla Discord/Telegram; wyłączone dla Slack (dopóki nie dodasz slash commands); ignorowane dla dostawców bez natywnej obsługi.
  - Ustaw `channels.discord.commands.native`, `channels.telegram.commands.native` lub `channels.slack.commands.native`, aby nadpisać per dostawca (bool albo `"auto"`).
  - `false` czyści wcześniej zarejestrowane polecenia na Discord/Telegram przy starcie. Polecenia Slack są zarządzane w aplikacji Slack i nie są usuwane automatycznie.
- `commands.nativeSkills` (domyślnie `"auto"`) rejestruje natywnie polecenia **Skills**, gdy jest to obsługiwane.
  - Auto: włączone dla Discord/Telegram; wyłączone dla Slack (Slack wymaga utworzenia jednego slash command na Skill).
  - Ustaw `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` lub `channels.slack.commands.nativeSkills`, aby nadpisać per dostawca (bool albo `"auto"`).
- `commands.bash` (domyślnie `false`) włącza `! <cmd>` do uruchamiania poleceń powłoki hosta (`/bash <cmd>` to alias; wymaga allowlist `tools.elevated`).
- `commands.bashForegroundMs` (domyślnie `2000`) kontroluje, jak długo bash czeka przed przełączeniem do trybu tła (`0` natychmiast przenosi do tła).
- `commands.config` (domyślnie `false`) włącza `/config` (odczyt/zapis `openclaw.json`).
- `commands.mcp` (domyślnie `false`) włącza `/mcp` (odczyt/zapis konfiguracji MCP zarządzanej przez OpenClaw pod `mcp.servers`).
- `commands.plugins` (domyślnie `false`) włącza `/plugins` (wykrywanie/status plugins oraz sterowanie install + enable/disable).
- `commands.debug` (domyślnie `false`) włącza `/debug` (nadpisania tylko w czasie działania).
- `commands.allowFrom` (opcjonalne) ustawia allowlistę per dostawca dla autoryzacji poleceń. Gdy jest skonfigurowana, jest
  jedynym źródłem autoryzacji dla poleceń i dyrektyw (`commands.useAccessGroups` oraz allowlisty/parowanie kanałów są ignorowane). Użyj `"*"` jako domyślnej wartości globalnej; klucze specyficzne dla dostawcy ją nadpisują.
- `commands.useAccessGroups` (domyślnie `true`) wymusza allowlisty/polityki dla poleceń, gdy `commands.allowFrom` nie jest ustawione.

## Lista poleceń

Tekstowe + natywne (gdy włączone):

- `/help`
- `/commands`
- `/tools [compact|verbose]` (pokaż, czego bieżący agent może używać teraz; `verbose` dodaje opisy)
- `/skill <name> [input]` (uruchom Skill po nazwie)
- `/status` (pokaż bieżący status; obejmuje użycie/limit dostawcy dla bieżącego dostawcy modelu, gdy jest dostępne)
- `/tasks` (wylistuj zadania w tle dla bieżącej sesji; pokazuje aktywne i ostatnie szczegóły zadań z lokalnymi dla agenta licznikami fallbacków)
- `/allowlist` (wylistuj/dodaj/usuń wpisy allowlisty)
- `/approve <id> <decision>` (rozstrzygnij prośby o zatwierdzenie exec; użyj oczekującej wiadomości zatwierdzenia, aby zobaczyć dostępne decyzje)
- `/context [list|detail|json]` (wyjaśnia „kontekst”; `detail` pokazuje rozmiar per plik + per narzędzie + per Skill + prompt systemowy)
- `/btw <question>` (zadaj efemeryczne pytanie poboczne o bieżącą sesję bez zmiany przyszłego kontekstu sesji; zobacz [/tools/btw](/pl/tools/btw))
- `/export-session [path]` (alias: `/export`) (eksportuj bieżącą sesję do HTML z pełnym promptem systemowym)
- `/whoami` (pokaż identyfikator nadawcy; alias: `/id`)
- `/session idle <duration|off>` (zarządzaj automatycznym unfocus przy bezczynności dla powiązań wątków z fokusem)
- `/session max-age <duration|off>` (zarządzaj automatycznym unfocus po twardym maksymalnym wieku dla powiązań wątków z fokusem)
- `/subagents list|kill|log|info|send|steer|spawn` (sprawdzaj, steruj albo uruchamiaj przebiegi sub-agent dla bieżącej sesji)
- `/acp spawn|cancel|steer|close|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|sessions` (sprawdzaj i steruj sesjami runtime ACP)
- `/agents` (wylistuj agentów powiązanych z wątkiem dla tej sesji)
- `/focus <target>` (Discord: powiąż ten wątek albo nowy wątek z celem sesji/subagenta)
- `/unfocus` (Discord: usuń bieżące powiązanie wątku)
- `/kill <id|#|all>` (natychmiast przerwij jednego albo wszystkie uruchomione sub-agents dla tej sesji; bez wiadomości potwierdzającej)
- `/steer <id|#> <message>` (natychmiast pokieruj działającym sub-agentem: w trakcie przebiegu, gdy to możliwe, w przeciwnym razie przerwij bieżącą pracę i uruchom ponownie z wiadomością steer)
- `/tell <id|#> <message>` (alias dla `/steer`)
- `/config show|get|set|unset` (utrwal konfigurację na dysku, tylko dla właściciela; wymaga `commands.config: true`)
- `/mcp show|get|set|unset` (zarządzaj konfiguracją serwera MCP OpenClaw, tylko dla właściciela; wymaga `commands.mcp: true`)
- `/plugins list|show|get|install|enable|disable` (sprawdzaj wykryte plugins, instaluj nowe i przełączaj ich włączenie; zapisy tylko dla właściciela; wymaga `commands.plugins: true`)
  - `/plugin` jest aliasem dla `/plugins`.
  - `/plugin install <spec>` przyjmuje te same specyfikacje pluginów co `openclaw plugins install`: lokalna ścieżka/archiwum, pakiet npm albo `clawhub:<pkg>`.
  - Odpowiedzi dla zapisów enable/disable nadal zawierają wskazówkę restartu. Na obserwowanym gateway działającym na pierwszym planie OpenClaw może wykonać ten restart automatycznie zaraz po zapisie.
- `/debug show|set|unset|reset` (nadpisania runtime, tylko dla właściciela; wymaga `commands.debug: true`)
- `/usage off|tokens|full|cost` (stopka użycia per odpowiedź albo lokalne podsumowanie kosztów)
- `/tts off|always|inbound|tagged|status|provider|limit|summary|audio` (sterowanie TTS; zobacz [/tts](/pl/tools/tts))
  - Discord: natywne polecenie to `/voice` (Discord rezerwuje `/tts`); tekstowe `/tts` nadal działa.
- `/stop`
- `/restart`
- `/dock-telegram` (alias: `/dock_telegram`) (przełącz odpowiedzi na Telegram)
- `/dock-discord` (alias: `/dock_discord`) (przełącz odpowiedzi na Discord)
- `/dock-slack` (alias: `/dock_slack`) (przełącz odpowiedzi na Slack)
- `/activation mention|always` (tylko grupy)
- `/send on|off|inherit` (tylko dla właściciela)
- `/reset` lub `/new [model]` (opcjonalna wskazówka modelu; pozostała część jest przekazywana dalej)
- `/think <off|minimal|low|medium|high|xhigh>` (dynamiczne wybory zależne od modelu/dostawcy; aliasy: `/thinking`, `/t`)
- `/fast status|on|off` (pominięcie argumentu pokazuje bieżący efektywny stan fast-mode)
- `/verbose on|full|off` (alias: `/v`)
- `/reasoning on|off|stream` (alias: `/reason`; gdy włączone, wysyła oddzielną wiadomość z prefiksem `Reasoning:`; `stream` = tylko szkic Telegram)
- `/elevated on|off|ask|full` (alias: `/elev`; `full` pomija zatwierdzenia exec)
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` (wyślij `/exec`, aby pokazać bieżący stan)
- `/model <name>` (alias: `/models`; albo `/<alias>` z `agents.defaults.models.*.alias`)
- `/queue <mode>` (plus opcje typu `debounce:2s cap:25 drop:summarize`; wyślij `/queue`, aby zobaczyć bieżące ustawienia)
- `/bash <command>` (tylko host; alias dla `! <command>`; wymaga `commands.bash: true` + allowlist `tools.elevated`)
- `/dreaming [on|off|status|help]` (przełącz globalne dreaming albo pokaż status; zobacz [Dreaming](/concepts/dreaming))

Tylko tekstowe:

- `/compact [instructions]` (zobacz [/concepts/compaction](/pl/concepts/compaction))
- `! <command>` (tylko host; po jednym na raz; używaj `!poll` + `!stop` przy długotrwałych zadaniach)
- `!poll` (sprawdź wyjście / status; akceptuje opcjonalne `sessionId`; `/bash poll` też działa)
- `!stop` (zatrzymaj uruchomione zadanie bash; akceptuje opcjonalne `sessionId`; `/bash stop` też działa)

Uwagi:

- Polecenia akceptują opcjonalne `:` między poleceniem a argumentami (np. `/think: high`, `/send: on`, `/help:`).
- `/new <model>` akceptuje alias modelu, `provider/model` albo nazwę dostawcy (dopasowanie przybliżone); jeśli nic nie pasuje, tekst jest traktowany jako treść wiadomości.
- Dla pełnego zestawienia użycia dostawcy użyj `openclaw status --usage`.
- `/allowlist add|remove` wymaga `commands.config=true` i respektuje kanałowe `configWrites`.
- W kanałach wielokontowych `/allowlist --account <id>` ukierunkowane na konfigurację oraz `/config set channels.<provider>.accounts.<id>...` również respektują `configWrites` konta docelowego.
- `/usage` steruje stopką użycia per odpowiedź; `/usage cost` wypisuje lokalne podsumowanie kosztów na podstawie logów sesji OpenClaw.
- `/restart` jest domyślnie włączone; ustaw `commands.restart: false`, aby je wyłączyć.
- Natywne polecenie tylko dla Discord: `/vc join|leave|status` steruje kanałami głosowymi (wymaga `channels.discord.voice` i natywnych poleceń; niedostępne jako tekst).
- Polecenia powiązań wątków Discord (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`) wymagają skutecznie włączonych powiązań wątków (`session.threadBindings.enabled` i/lub `channels.discord.threadBindings.enabled`).
- Referencja poleceń ACP i zachowanie runtime: [ACP Agents](/pl/tools/acp-agents).
- `/verbose` jest przeznaczone do debugowania i dodatkowej widoczności; w normalnym użyciu trzymaj je **wyłączone**.
- `/fast on|off` utrwala nadpisanie sesji. Użyj opcji `inherit` w Sessions UI, aby je wyczyścić i wrócić do wartości domyślnych z konfiguracji.
- `/fast` jest zależne od dostawcy: OpenAI/OpenAI Codex mapują je do `service_tier=priority` na natywnych endpointach Responses, podczas gdy bezpośrednie publiczne żądania Anthropic, w tym ruch uwierzytelniany przez OAuth wysyłany do `api.anthropic.com`, mapują je do `service_tier=auto` albo `standard_only`. Zobacz [OpenAI](/pl/providers/openai) i [Anthropic](/pl/providers/anthropic).
- Podsumowania awarii narzędzi są nadal pokazywane, gdy mają znaczenie, ale szczegółowy tekst błędu jest dołączany tylko wtedy, gdy `/verbose` ma wartość `on` albo `full`.
- `/reasoning` (i `/verbose`) są ryzykowne w ustawieniach grupowych: mogą ujawniać wewnętrzne rozumowanie albo wyjście narzędzi, których nie zamierzałeś ujawniać. Najlepiej pozostawić je wyłączone, szczególnie w czatach grupowych.
- `/model` natychmiast utrwala nowy model sesji.
- Jeśli agent jest bezczynny, następny przebieg użyje go od razu.
- Jeśli przebieg jest już aktywny, OpenClaw oznacza przełączenie na żywo jako oczekujące i restartuje do nowego modelu dopiero w czystym punkcie ponowienia.
- Jeśli aktywność narzędzi albo generowanie odpowiedzi już się rozpoczęły, oczekujące przełączenie może pozostać w kolejce do późniejszej okazji ponowienia albo do następnej tury użytkownika.
- **Szybka ścieżka:** wiadomości zawierające tylko polecenie od nadawców z allowlisty są obsługiwane natychmiast (z pominięciem kolejki i modelu).
- **Bramkowanie wzmianką w grupie:** wiadomości zawierające tylko polecenie od nadawców z allowlisty omijają wymagania wzmianki.
- **Skróty inline (tylko dla nadawców z allowlisty):** niektóre polecenia działają również po osadzeniu w zwykłej wiadomości i są usuwane, zanim model zobaczy pozostały tekst.
  - Przykład: `hej /status` uruchamia odpowiedź statusu, a pozostały tekst przechodzi dalej normalnym przepływem.
- Obecnie: `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- Nieautoryzowane wiadomości zawierające tylko polecenie są cicho ignorowane, a tokeny inline `/...` są traktowane jak zwykły tekst.
- **Polecenia Skills:** Skills typu `user-invocable` są wystawiane jako polecenia slash. Nazwy są sanitizowane do `a-z0-9_` (maks. 32 znaki); kolizje dostają sufiksy liczbowe (np. `_2`).
  - `/skill <name> [input]` uruchamia Skill po nazwie (przydatne, gdy limity natywnych poleceń uniemożliwiają polecenia per Skill).
  - Domyślnie polecenia Skills są przekazywane do modelu jako zwykłe żądanie.
  - Skills mogą opcjonalnie deklarować `command-dispatch: tool`, aby kierować polecenie bezpośrednio do narzędzia (deterministycznie, bez modelu).
  - Przykład: `/prose` (plugin OpenProse) — zobacz [OpenProse](/pl/prose).
- **Argumenty natywnych poleceń:** Discord używa autocomplete dla dynamicznych opcji (oraz menu przycisków, gdy pominiesz wymagane argumenty). Telegram i Slack pokazują menu przycisków, gdy polecenie obsługuje wybory i pominiesz argument.

## `/tools`

`/tools` odpowiada na pytanie runtime, a nie konfiguracyjne: **czego ten agent może używać teraz
w tej rozmowie**.

- Domyślne `/tools` jest zwięzłe i zoptymalizowane pod szybkie skanowanie.
- `/tools verbose` dodaje krótkie opisy.
- Powierzchnie z natywnymi poleceniami, które obsługują argumenty, udostępniają ten sam przełącznik trybu `compact|verbose`.
- Wyniki są ograniczone do sesji, więc zmiana agenta, kanału, wątku, autoryzacji nadawcy albo modelu może
  zmienić wynik.
- `/tools` obejmuje narzędzia, które są faktycznie osiągalne w runtime, w tym narzędzia core, podłączone
  narzędzia pluginów oraz narzędzia należące do kanału.

Do edycji profili i nadpisań używaj panelu Tools w Control UI albo powierzchni config/catalog zamiast
traktować `/tools` jak statyczny katalog.

## Powierzchnie użycia (co jest pokazywane gdzie)

- **Użycie/limit dostawcy** (przykład: „Claude 80% left”) pojawia się w `/status` dla bieżącego dostawcy modelu, gdy śledzenie użycia jest włączone. OpenClaw normalizuje okna dostawców do `% left`; dla MiniMax pola procentowe zawierające tylko pozostałą wartość są odwracane przed wyświetleniem, a odpowiedzi `model_remains` preferują wpis modelu czatu wraz z etykietą planu oznaczoną modelem.
- Wiersze **token/cache** w `/status` mogą przejść do fallbacku do najnowszego wpisu użycia z transkryptu, gdy aktywna migawka sesji jest uboga. Istniejące niezerowe wartości na żywo nadal wygrywają, a fallback z transkryptu może też odzyskać etykietę aktywnego modelu runtime oraz większą sumę zorientowaną na prompt, gdy zapisanych sum brakuje albo są mniejsze.
- **Tokeny/koszt per odpowiedź** są kontrolowane przez `/usage off|tokens|full` (dołączane do zwykłych odpowiedzi).
- `/model status` dotyczy **modeli/uwierzytelniania/endpointów**, a nie użycia.

## Wybór modelu (`/model`)

`/model` jest zaimplementowane jako dyrektywa.

Przykłady:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

Uwagi:

- `/model` i `/model list` pokazują zwięzły, numerowany selektor (rodzina modeli + dostępni dostawcy).
- Na Discord `/model` i `/models` otwierają interaktywny selektor z listami rozwijanymi dostawcy i modelu oraz krokiem Submit.
- `/model <#>` wybiera z tego selektora (i w miarę możliwości preferuje bieżącego dostawcę).
- `/model status` pokazuje widok szczegółowy, w tym skonfigurowany endpoint dostawcy (`baseUrl`) i tryb API (`api`), gdy są dostępne.

## Nadpisania debug

`/debug` pozwala ustawiać nadpisania konfiguracji **tylko w runtime** (w pamięci, nie na dysku). Tylko dla właściciela. Domyślnie wyłączone; włącz przez `commands.debug: true`.

Przykłady:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Uwagi:

- Nadpisania są stosowane natychmiast do nowych odczytów konfiguracji, ale **nie** zapisują się do `openclaw.json`.
- Użyj `/debug reset`, aby wyczyścić wszystkie nadpisania i wrócić do konfiguracji z dysku.

## Aktualizacje konfiguracji

`/config` zapisuje do konfiguracji na dysku (`openclaw.json`). Tylko dla właściciela. Domyślnie wyłączone; włącz przez `commands.config: true`.

Przykłady:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

Uwagi:

- Konfiguracja jest walidowana przed zapisem; nieprawidłowe zmiany są odrzucane.
- Aktualizacje `/config` utrzymują się po restartach.

## Aktualizacje MCP

`/mcp` zapisuje definicje serwerów MCP zarządzane przez OpenClaw pod `mcp.servers`. Tylko dla właściciela. Domyślnie wyłączone; włącz przez `commands.mcp: true`.

Przykłady:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Uwagi:

- `/mcp` zapisuje konfigurację w konfiguracji OpenClaw, a nie w ustawieniach projektu należących do Pi.
- Adaptery runtime decydują, które transporty są faktycznie wykonywalne.

## Aktualizacje pluginów

`/plugins` pozwala operatorom sprawdzać wykryte plugins i przełączać ich włączenie w konfiguracji. Przepływy tylko do odczytu mogą używać aliasu `/plugin`. Domyślnie wyłączone; włącz przez `commands.plugins: true`.

Przykłady:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Uwagi:

- `/plugins list` i `/plugins show` używają rzeczywistego wykrywania pluginów względem bieżącego workspace oraz konfiguracji na dysku.
- `/plugins enable|disable` aktualizuje tylko konfigurację pluginów; nie instaluje ani nie odinstalowuje pluginów.
- Po zmianach enable/disable zrestartuj gateway, aby je zastosować.

## Uwagi o powierzchniach

- **Polecenia tekstowe** działają w normalnej sesji czatu (DM współdzielą `main`, grupy mają własną sesję).
- **Polecenia natywne** używają sesji izolowanych:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>` (prefiks konfigurowany przez `channels.slack.slashCommand.sessionPrefix`)
  - Telegram: `telegram:slash:<userId>` (kieruje na sesję czatu przez `CommandTargetSessionKey`)
- **`/stop`** jest kierowane do aktywnej sesji czatu, aby mogło przerwać bieżący przebieg.
- **Slack:** `channels.slack.slashCommand` nadal jest obsługiwane dla pojedynczego polecenia w stylu `/openclaw`. Jeśli włączysz `commands.native`, musisz utworzyć jedno slash command Slack dla każdego wbudowanego polecenia (o tych samych nazwach co `/help`). Menu argumentów poleceń dla Slack są dostarczane jako efemeryczne przyciski Block Kit.
  - Wyjątek dla natywnych poleceń Slack: zarejestruj `/agentstatus` (nie `/status`), ponieważ Slack rezerwuje `/status`. Tekstowe `/status` nadal działa w wiadomościach Slack.

## Poboczne pytania BTW

`/btw` to szybkie **pytanie poboczne** o bieżącą sesję.

W przeciwieństwie do zwykłego czatu:

- używa bieżącej sesji jako kontekstu w tle,
- działa jako osobne, jednorazowe wywołanie **bez narzędzi**,
- nie zmienia przyszłego kontekstu sesji,
- nie jest zapisywane do historii transkryptu,
- jest dostarczane jako żywy wynik poboczny zamiast zwykłej wiadomości asystenta.

To sprawia, że `/btw` jest przydatne, gdy chcesz tymczasowego doprecyzowania, podczas gdy główne
zadanie nadal trwa.

Przykład:

```text
/btw co teraz robimy?
```

Pełny opis zachowania i szczegóły UX klienta znajdziesz w [BTW Side Questions](/pl/tools/btw).
