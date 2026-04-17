---
read_when:
    - Używanie lub konfigurowanie poleceń czatu
    - Debugowanie routingu poleceń lub uprawnień
summary: 'Polecenia ukośnikowe: tekstowe vs natywne, konfiguracja i obsługiwane polecenia'
title: Polecenia ukośnikowe
x-i18n:
    generated_at: "2026-04-12T23:33:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ef6f54500fa2ce3b873a8398d6179a0882b8bf6fba38f61146c64671055505e
    source_path: tools/slash-commands.md
    workflow: 15
---

# Polecenia ukośnikowe

Polecenia są obsługiwane przez Gateway. Większość poleceń musi zostać wysłana jako **samodzielna** wiadomość zaczynająca się od `/`.
Polecenie czatu bash dostępne tylko na hoście używa `! <cmd>` (z aliasem `/bash <cmd>`).

Istnieją dwa powiązane systemy:

- **Polecenia**: samodzielne wiadomości `/...`.
- **Dyrektywy**: `/think`, `/fast`, `/verbose`, `/trace`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Dyrektywy są usuwane z wiadomości, zanim model ją zobaczy.
  - W zwykłych wiadomościach czatu (nie będących wyłącznie dyrektywami) są traktowane jako „wskazówki inline” i **nie** zachowują ustawień sesji.
  - W wiadomościach zawierających wyłącznie dyrektywy (wiadomość zawiera tylko dyrektywy) utrwalają się w sesji i odpowiadają potwierdzeniem.
  - Dyrektywy są stosowane tylko dla **autoryzowanych nadawców**. Jeśli ustawiono `commands.allowFrom`, jest to jedyna
    allowlista używana; w przeciwnym razie autoryzacja pochodzi z allowlist/parowania kanałów oraz `commands.useAccessGroups`.
    Nieautoryzowani nadawcy widzą dyrektywy traktowane jak zwykły tekst.

Są też dostępne niektóre **skróty inline** (tylko dla nadawców z allowlisty / autoryzowanych): `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Uruchamiają się natychmiast, są usuwane, zanim model zobaczy wiadomość, a pozostały tekst przechodzi dalej przez normalny przepływ.

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
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (domyślnie `true`) włącza parsowanie `/...` w wiadomościach czatu.
  - Na powierzchniach bez natywnych poleceń (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams) polecenia tekstowe nadal działają, nawet jeśli ustawisz tę opcję na `false`.
- `commands.native` (domyślnie `"auto"`) rejestruje polecenia natywne.
  - Auto: włączone dla Discord/Telegram; wyłączone dla Slack (dopóki nie dodasz poleceń ukośnikowych); ignorowane dla dostawców bez obsługi natywnej.
  - Ustaw `channels.discord.commands.native`, `channels.telegram.commands.native` lub `channels.slack.commands.native`, aby nadpisać to per dostawca (bool albo `"auto"`).
  - `false` czyści wcześniej zarejestrowane polecenia na Discord/Telegram przy starcie. Polecenia Slack są zarządzane w aplikacji Slack i nie są usuwane automatycznie.
- `commands.nativeSkills` (domyślnie `"auto"`) rejestruje natywnie polecenia **Skills**, gdy jest to obsługiwane.
  - Auto: włączone dla Discord/Telegram; wyłączone dla Slack (Slack wymaga utworzenia polecenia ukośnikowego dla każdej Skill).
  - Ustaw `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` lub `channels.slack.commands.nativeSkills`, aby nadpisać to per dostawca (bool albo `"auto"`).
- `commands.bash` (domyślnie `false`) włącza `! <cmd>` do uruchamiania poleceń powłoki hosta (`/bash <cmd>` to alias; wymaga allowlist `tools.elevated`).
- `commands.bashForegroundMs` (domyślnie `2000`) określa, jak długo bash czeka przed przełączeniem się do trybu tła (`0` natychmiast przenosi do tła).
- `commands.config` (domyślnie `false`) włącza `/config` (odczyt/zapis `openclaw.json`).
- `commands.mcp` (domyślnie `false`) włącza `/mcp` (odczyt/zapis konfiguracji MCP zarządzanej przez OpenClaw pod `mcp.servers`).
- `commands.plugins` (domyślnie `false`) włącza `/plugins` (wykrywanie/status Plugin oraz kontrolki instalacji + włączania/wyłączania).
- `commands.debug` (domyślnie `false`) włącza `/debug` (nadpisania tylko na czas działania).
- `commands.restart` (domyślnie `true`) włącza `/restart` oraz działania narzędzia restartu Gateway.
- `commands.ownerAllowFrom` (opcjonalnie) ustawia jawną allowlistę właściciela dla powierzchni poleceń/narzędzi dostępnych tylko właścicielowi. To jest oddzielne od `commands.allowFrom`.
- `commands.ownerDisplay` określa, jak identyfikatory właściciela pojawiają się w promcie systemowym: `raw` albo `hash`.
- `commands.ownerDisplaySecret` opcjonalnie ustawia sekret HMAC używany, gdy `commands.ownerDisplay="hash"`.
- `commands.allowFrom` (opcjonalnie) ustawia allowlistę per dostawca dla autoryzacji poleceń. Gdy jest skonfigurowana, jest to
  jedyne źródło autoryzacji dla poleceń i dyrektyw (allowlisty/parowanie kanałów i `commands.useAccessGroups`
  są ignorowane). Użyj `"*"` jako globalnej wartości domyślnej; klucze specyficzne dla dostawcy mają pierwszeństwo.
- `commands.useAccessGroups` (domyślnie `true`) wymusza allowlisty/polityki dla poleceń, gdy `commands.allowFrom` nie jest ustawione.

## Lista poleceń

Obecne źródło prawdy:

- wbudowane polecenia core pochodzą z `src/auto-reply/commands-registry.shared.ts`
- wygenerowane polecenia dock pochodzą z `src/auto-reply/commands-registry.data.ts`
- polecenia Plugin pochodzą z wywołań `registerCommand()` w Plugin
- rzeczywista dostępność na Twoim Gateway nadal zależy od flag konfiguracji, powierzchni kanału i zainstalowanych/włączonych Plugin

### Wbudowane polecenia core

Wbudowane polecenia dostępne obecnie:

- `/new [model]` rozpoczyna nową sesję; `/reset` to alias resetu.
- `/compact [instructions]` wykonuje Compaction kontekstu sesji. Zobacz [/concepts/compaction](/pl/concepts/compaction).
- `/stop` przerywa bieżące uruchomienie.
- `/session idle <duration|off>` i `/session max-age <duration|off>` zarządzają wygaśnięciem powiązania wątku.
- `/think <off|minimal|low|medium|high|xhigh>` ustawia poziom thinking. Aliasy: `/thinking`, `/t`.
- `/verbose on|off|full` przełącza szczegółowe wyjście. Alias: `/v`.
- `/trace on|off` przełącza wyjście śledzenia Plugin dla bieżącej sesji.
- `/fast [status|on|off]` pokazuje lub ustawia tryb fast.
- `/reasoning [on|off|stream]` przełącza widoczność reasoning. Alias: `/reason`.
- `/elevated [on|off|ask|full]` przełącza tryb elevated. Alias: `/elev`.
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` pokazuje lub ustawia domyślne wartości exec.
- `/model [name|#|status]` pokazuje lub ustawia model.
- `/models [provider] [page] [limit=<n>|size=<n>|all]` wyświetla listę dostawców lub modeli dla dostawcy.
- `/queue <mode>` zarządza zachowaniem kolejki (`steer`, `interrupt`, `followup`, `collect`, `steer-backlog`) oraz opcjami takimi jak `debounce:2s cap:25 drop:summarize`.
- `/help` pokazuje krótkie podsumowanie pomocy.
- `/commands` pokazuje wygenerowany katalog poleceń.
- `/tools [compact|verbose]` pokazuje, czego bieżący agent może teraz używać.
- `/status` pokazuje status środowiska wykonawczego, w tym użycie/limit dostawcy, gdy jest dostępny.
- `/tasks` wyświetla aktywne/niedawne taski w tle dla bieżącej sesji.
- `/context [list|detail|json]` wyjaśnia, jak składany jest kontekst.
- `/export-session [path]` eksportuje bieżącą sesję do HTML. Alias: `/export`.
- `/whoami` pokazuje Twój identyfikator nadawcy. Alias: `/id`.
- `/skill <name> [input]` uruchamia Skill po nazwie.
- `/allowlist [list|add|remove] ...` zarządza wpisami allowlisty. Tylko tekstowo.
- `/approve <id> <decision>` rozwiązuje prompty zatwierdzania exec.
- `/btw <question>` zadaje pytanie poboczne bez zmiany przyszłego kontekstu sesji. Zobacz [/tools/btw](/pl/tools/btw).
- `/subagents list|kill|log|info|send|steer|spawn` zarządza uruchomieniami podagentów dla bieżącej sesji.
- `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` zarządza sesjami ACP i opcjami środowiska wykonawczego.
- `/focus <target>` wiąże bieżący wątek Discord albo temat/rozmowę Telegram z celem sesji.
- `/unfocus` usuwa bieżące powiązanie.
- `/agents` wyświetla listę agentów powiązanych z wątkiem dla bieżącej sesji.
- `/kill <id|#|all>` przerywa jednego albo wszystkich uruchomionych podagentów.
- `/steer <id|#> <message>` wysyła sterowanie do działającego podagenta. Alias: `/tell`.
- `/config show|get|set|unset` odczytuje lub zapisuje `openclaw.json`. Tylko właściciel. Wymaga `commands.config: true`.
- `/mcp show|get|set|unset` odczytuje lub zapisuje konfigurację serwera MCP zarządzaną przez OpenClaw pod `mcp.servers`. Tylko właściciel. Wymaga `commands.mcp: true`.
- `/plugins list|inspect|show|get|install|enable|disable` sprawdza lub modyfikuje stan Plugin. `/plugin` to alias. Zapisy tylko dla właściciela. Wymaga `commands.plugins: true`.
- `/debug show|set|unset|reset` zarządza nadpisaniami konfiguracji tylko na czas działania. Tylko właściciel. Wymaga `commands.debug: true`.
- `/usage off|tokens|full|cost` kontroluje stopkę użycia przy każdej odpowiedzi albo wypisuje lokalne podsumowanie kosztów.
- `/tts on|off|status|provider|limit|summary|audio|help` steruje TTS. Zobacz [/tools/tts](/pl/tools/tts).
- `/restart` restartuje OpenClaw, gdy jest włączone. Domyślnie: włączone; ustaw `commands.restart: false`, aby je wyłączyć.
- `/activation mention|always` ustawia tryb aktywacji grupy.
- `/send on|off|inherit` ustawia politykę wysyłania. Tylko właściciel.
- `/bash <command>` uruchamia polecenie powłoki hosta. Tylko tekstowo. Alias: `! <command>`. Wymaga `commands.bash: true` oraz allowlist `tools.elevated`.
- `!poll [sessionId]` sprawdza zadanie bash w tle.
- `!stop [sessionId]` zatrzymuje zadanie bash w tle.

### Wygenerowane polecenia dock

Polecenia dock są generowane z Plugin kanałów z obsługą poleceń natywnych. Obecny dołączony zestaw:

- `/dock-discord` (alias: `/dock_discord`)
- `/dock-mattermost` (alias: `/dock_mattermost`)
- `/dock-slack` (alias: `/dock_slack`)
- `/dock-telegram` (alias: `/dock_telegram`)

### Polecenia dołączonych Plugin

Dołączone Plugin mogą dodawać więcej poleceń ukośnikowych. Obecne dołączone polecenia w tym repozytorium:

- `/dreaming [on|off|status|help]` przełącza Dreaming pamięci. Zobacz [Dreaming](/pl/concepts/dreaming).
- `/pair [qr|status|pending|approve|cleanup|notify]` zarządza przepływem parowania/konfiguracji urządzenia. Zobacz [Pairing](/pl/channels/pairing).
- `/phone status|arm <camera|screen|writes|all> [duration]|disarm` tymczasowo uzbraja polecenia Node telefonu o wysokim ryzyku.
- `/voice status|list [limit]|set <voiceId|name>` zarządza konfiguracją głosu Talk. Na Discordzie natywna nazwa polecenia to `/talkvoice`.
- `/card ...` wysyła presety bogatych kart LINE. Zobacz [LINE](/pl/channels/line).
- `/codex status|models|threads|resume|compact|review|account|mcp|skills` sprawdza i steruje dołączonym harness app-server Codex. Zobacz [Codex Harness](/pl/plugins/codex-harness).
- Polecenia tylko dla QQBot:
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### Dynamiczne polecenia Skills

Skills wywoływane przez użytkownika są także udostępniane jako polecenia ukośnikowe:

- `/skill <name> [input]` zawsze działa jako ogólny punkt wejścia.
- Skills mogą też pojawiać się jako bezpośrednie polecenia, takie jak `/prose`, gdy Skill/Plugin je rejestruje.
- rejestracja natywnych poleceń Skills jest kontrolowana przez `commands.nativeSkills` i `channels.<provider>.commands.nativeSkills`.

Uwagi:

- Polecenia akceptują opcjonalny znak `:` między poleceniem a argumentami (np. `/think: high`, `/send: on`, `/help:`).
- `/new <model>` akceptuje alias modelu, `provider/model` albo nazwę dostawcy (dopasowanie rozmyte); jeśli nic nie pasuje, tekst jest traktowany jako treść wiadomości.
- Aby zobaczyć pełne zestawienie użycia dostawców, użyj `openclaw status --usage`.
- `/allowlist add|remove` wymaga `commands.config=true` i respektuje kanałowe `configWrites`.
- W kanałach z wieloma kontami polecenia `/allowlist --account <id>` ukierunkowane na konfigurację oraz `/config set channels.<provider>.accounts.<id>...` również respektują `configWrites` konta docelowego.
- `/usage` kontroluje stopkę użycia dołączaną do każdej odpowiedzi; `/usage cost` wypisuje lokalne podsumowanie kosztów z logów sesji OpenClaw.
- `/restart` jest domyślnie włączone; ustaw `commands.restart: false`, aby je wyłączyć.
- `/plugins install <spec>` akceptuje te same specyfikacje Plugin co `openclaw plugins install`: lokalna ścieżka/archiwum, pakiet npm albo `clawhub:<pkg>`.
- `/plugins enable|disable` aktualizuje konfigurację Plugin i może poprosić o restart.
- Polecenie natywne tylko dla Discorda: `/vc join|leave|status` steruje kanałami głosowymi (wymaga `channels.discord.voice` i poleceń natywnych; niedostępne jako tekst).
- Polecenia powiązania wątku Discord (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`) wymagają skutecznie włączonych powiązań wątków (`session.threadBindings.enabled` i/lub `channels.discord.threadBindings.enabled`).
- Referencja poleceń ACP i zachowanie środowiska wykonawczego: [ACP Agents](/pl/tools/acp-agents).
- `/verbose` służy do debugowania i dodatkowej widoczności; w normalnym użyciu trzymaj je **wyłączone**.
- `/trace` jest węższe niż `/verbose`: ujawnia tylko linie śledzenia/debugowania należące do Plugin i nie pokazuje zwykłego szczegółowego szumu narzędzi.
- `/fast on|off` zapisuje nadpisanie sesji. Użyj opcji `inherit` w interfejsie Sessions, aby je wyczyścić i wrócić do domyślnych ustawień konfiguracji.
- `/fast` zależy od dostawcy: OpenAI/OpenAI Codex mapują je na `service_tier=priority` na natywnych endpointach Responses, podczas gdy bezpośrednie publiczne żądania Anthropic, w tym ruch uwierzytelniony OAuth wysyłany do `api.anthropic.com`, mapują je na `service_tier=auto` lub `standard_only`. Zobacz [OpenAI](/pl/providers/openai) i [Anthropic](/pl/providers/anthropic).
- Podsumowania awarii narzędzi są nadal pokazywane, gdy mają znaczenie, ale szczegółowy tekst awarii jest dołączany tylko wtedy, gdy `/verbose` ma wartość `on` albo `full`.
- `/reasoning`, `/verbose` i `/trace` są ryzykowne w ustawieniach grupowych: mogą ujawniać wewnętrzne reasoning, wyjście narzędzi albo diagnostykę Plugin, której nie zamierzałeś ujawniać. Lepiej zostawić je wyłączone, szczególnie w czatach grupowych.
- `/model` natychmiast zapisuje nowy model sesji.
- Jeśli agent jest bezczynny, następne uruchomienie od razu go użyje.
- Jeśli uruchomienie już trwa, OpenClaw oznacza przełączenie na żywo jako oczekujące i restartuje się do nowego modelu dopiero przy czystym punkcie ponowienia.
- Jeśli aktywność narzędzi albo wyjście odpowiedzi już się rozpoczęły, oczekujące przełączenie może pozostać w kolejce do późniejszej okazji ponowienia albo do następnej tury użytkownika.
- **Szybka ścieżka:** wiadomości zawierające tylko polecenie od nadawców z allowlisty są obsługiwane natychmiast (pomijają kolejkę + model).
- **Bramkowanie wzmianek grupowych:** wiadomości zawierające tylko polecenie od nadawców z allowlisty omijają wymagania dotyczące wzmianek.
- **Skróty inline (tylko dla nadawców z allowlisty):** niektóre polecenia działają również po osadzeniu w zwykłej wiadomości i są usuwane, zanim model zobaczy pozostały tekst.
  - Przykład: `hey /status` wywołuje odpowiedź statusu, a pozostały tekst przechodzi dalej przez normalny przepływ.
- Obecnie: `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- Nieautoryzowane wiadomości zawierające tylko polecenie są po cichu ignorowane, a tokeny inline `/...` są traktowane jak zwykły tekst.
- **Polecenia Skills:** Skills `user-invocable` są udostępniane jako polecenia ukośnikowe. Nazwy są sanityzowane do `a-z0-9_` (maks. 32 znaki); kolizje dostają sufiksy numeryczne (np. `_2`).
  - `/skill <name> [input]` uruchamia Skill po nazwie (przydatne, gdy ograniczenia natywnych poleceń uniemożliwiają polecenia per Skill).
  - Domyślnie polecenia Skills są przekazywane do modelu jako zwykłe żądanie.
  - Skills mogą opcjonalnie deklarować `command-dispatch: tool`, aby kierować polecenie bezpośrednio do narzędzia (deterministycznie, bez modelu).
  - Przykład: `/prose` (Plugin OpenProse) — zobacz [OpenProse](/pl/prose).
- **Argumenty poleceń natywnych:** Discord używa autouzupełniania dla opcji dynamicznych (oraz menu przycisków, gdy pominiesz wymagane argumenty). Telegram i Slack pokazują menu przycisków, gdy polecenie obsługuje wybory i pominiesz argument.

## `/tools`

`/tools` odpowiada na pytanie dotyczące środowiska wykonawczego, a nie konfiguracji: **czego ten agent może teraz używać
w tej rozmowie**.

- Domyślne `/tools` jest zwięzłe i zoptymalizowane pod szybkie skanowanie.
- `/tools verbose` dodaje krótkie opisy.
- Powierzchnie z poleceniami natywnymi, które obsługują argumenty, udostępniają ten sam przełącznik trybu `compact|verbose`.
- Wyniki są ograniczone do sesji, więc zmiana agenta, kanału, wątku, autoryzacji nadawcy albo modelu może
  zmienić wynik.
- `/tools` obejmuje narzędzia, które są faktycznie osiągalne w czasie działania, w tym narzędzia core, podłączone
  narzędzia Plugin i narzędzia należące do kanału.

Do edycji profili i nadpisań użyj panelu Tools w interfejsie Control UI albo powierzchni konfiguracji/katalogu, zamiast
traktować `/tools` jak statyczny katalog.

## Powierzchnie użycia (co jest pokazywane gdzie)

- **Użycie/limit dostawcy** (na przykład: „Claude 80% left”) pojawia się w `/status` dla bieżącego dostawcy modelu, gdy śledzenie użycia jest włączone. OpenClaw normalizuje okna dostawców do `% left`; dla MiniMax pola procentowe zawierające tylko wartość pozostałą są odwracane przed wyświetleniem, a odpowiedzi `model_remains` preferują wpis modelu czatu oraz etykietę planu oznaczoną modelem.
- **Linie tokenów/cache** w `/status` mogą wracać do najnowszego wpisu użycia z transkryptu, gdy migawka aktywnej sesji jest uboga. Istniejące niezerowe wartości z aktywnego środowiska nadal mają pierwszeństwo, a fallback do transkryptu może też odzyskać etykietę aktywnego modelu środowiska wykonawczego oraz większą sumę zorientowaną na prompt, gdy zapisanych sum brakuje albo są mniejsze.
- **Tokeny/koszt dla każdej odpowiedzi** są kontrolowane przez `/usage off|tokens|full` (dołączane do zwykłych odpowiedzi).
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
- Na Discordzie `/model` i `/models` otwierają interaktywny selektor z listami rozwijanymi dostawców i modeli oraz krokiem Submit.
- `/model <#>` wybiera z tego selektora (i w miarę możliwości preferuje bieżącego dostawcę).
- `/model status` pokazuje widok szczegółowy, w tym skonfigurowany endpoint dostawcy (`baseUrl`) i tryb API (`api`), gdy są dostępne.

## Nadpisania debugowania

`/debug` pozwala ustawiać **nadpisania konfiguracji tylko na czas działania** (w pamięci, nie na dysku). Tylko właściciel. Domyślnie wyłączone; włącz przez `commands.debug: true`.

Przykłady:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Uwagi:

- Nadpisania zaczynają działać natychmiast dla nowych odczytów konfiguracji, ale **nie** zapisują się do `openclaw.json`.
- Użyj `/debug reset`, aby wyczyścić wszystkie nadpisania i wrócić do konfiguracji z dysku.

## Wyjście śledzenia Plugin

`/trace` pozwala przełączać **linie śledzenia/debugowania Plugin o zakresie sesji** bez włączania pełnego trybu verbose.

Przykłady:

```text
/trace
/trace on
/trace off
```

Uwagi:

- `/trace` bez argumentu pokazuje bieżący stan śledzenia sesji.
- `/trace on` włącza linie śledzenia Plugin dla bieżącej sesji.
- `/trace off` ponownie je wyłącza.
- Linie śledzenia Plugin mogą pojawiać się w `/status` oraz jako dodatkowa wiadomość diagnostyczna po zwykłej odpowiedzi asystenta.
- `/trace` nie zastępuje `/debug`; `/debug` nadal zarządza nadpisaniami konfiguracji tylko na czas działania.
- `/trace` nie zastępuje `/verbose`; zwykłe szczegółowe wyjście narzędzi/statusu nadal należy do `/verbose`.

## Aktualizacje konfiguracji

`/config` zapisuje do Twojej konfiguracji na dysku (`openclaw.json`). Tylko właściciel. Domyślnie wyłączone; włącz przez `commands.config: true`.

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

`/mcp` zapisuje definicje serwerów MCP zarządzane przez OpenClaw pod `mcp.servers`. Tylko właściciel. Domyślnie wyłączone; włącz przez `commands.mcp: true`.

Przykłady:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Uwagi:

- `/mcp` zapisuje konfigurację w konfiguracji OpenClaw, a nie w ustawieniach projektu należących do Pi.
- Adapters środowiska wykonawczego decydują, które transporty są faktycznie wykonywalne.

## Aktualizacje Plugin

`/plugins` pozwala operatorom sprawdzać wykryte Plugin i przełączać ich włączenie w konfiguracji. Przepływy tylko do odczytu mogą używać aliasu `/plugin`. Domyślnie wyłączone; włącz przez `commands.plugins: true`.

Przykłady:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Uwagi:

- `/plugins list` i `/plugins show` używają rzeczywistego wykrywania Plugin względem bieżącego workspace i konfiguracji na dysku.
- `/plugins enable|disable` aktualizuje tylko konfigurację Plugin; nie instaluje ani nie odinstalowuje Plugin.
- Po zmianach `enable/disable` uruchom Gateway ponownie, aby je zastosować.

## Uwagi o powierzchniach

- **Polecenia tekstowe** działają w normalnej sesji czatu (DM współdzielą `main`, grupy mają własną sesję).
- **Polecenia natywne** używają izolowanych sesji:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>` (prefiks konfigurowalny przez `channels.slack.slashCommand.sessionPrefix`)
  - Telegram: `telegram:slash:<userId>` (celuje w sesję czatu przez `CommandTargetSessionKey`)
- **`/stop`** celuje w aktywną sesję czatu, aby móc przerwać bieżące uruchomienie.
- **Slack:** `channels.slack.slashCommand` nadal jest obsługiwane dla pojedynczego polecenia w stylu `/openclaw`. Jeśli włączysz `commands.native`, musisz utworzyć jedno polecenie ukośnikowe Slack dla każdego wbudowanego polecenia (te same nazwy co `/help`). Menu argumentów poleceń dla Slack są dostarczane jako efemeryczne przyciski Block Kit.
  - Wyjątek dla natywnych poleceń Slack: zarejestruj `/agentstatus` (nie `/status`), ponieważ Slack rezerwuje `/status`. Tekstowe `/status` nadal działa w wiadomościach Slack.

## Pytania poboczne BTW

`/btw` to szybkie **pytanie poboczne** dotyczące bieżącej sesji.

W odróżnieniu od zwykłego czatu:

- używa bieżącej sesji jako kontekstu tła,
- działa jako osobne jednorazowe wywołanie **bez narzędzi**,
- nie zmienia przyszłego kontekstu sesji,
- nie jest zapisywane w historii transkryptu,
- jest dostarczane jako wynik poboczny na żywo zamiast zwykłej wiadomości asystenta.

To sprawia, że `/btw` jest przydatne, gdy chcesz uzyskać tymczasowe doprecyzowanie, podczas gdy główne
zadanie nadal trwa.

Przykład:

```text
/btw co teraz właściwie robimy?
```

Zobacz [BTW Side Questions](/pl/tools/btw), aby poznać pełne zachowanie i szczegóły
UX klienta.
