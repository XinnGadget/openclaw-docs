---
read_when:
    - Dodawanie lub modyfikowanie migracji doctor
    - Wprowadzanie niekompatybilnych zmian konfiguracji
summary: 'Polecenie Doctor: kontrole stanu, migracje konfiguracji i kroki naprawcze'
title: Doctor
x-i18n:
    generated_at: "2026-04-06T03:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6c0a15c522994552a1eef39206bed71fc5bf45746776372f24f31c101bfbd411
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` to narzędzie naprawy i migracji dla OpenClaw. Naprawia nieaktualny stan/konfigurację, sprawdza kondycję systemu i podaje konkretne kroki naprawcze.

## Szybki start

```bash
openclaw doctor
```

### Tryb bezobsługowy / automatyzacja

```bash
openclaw doctor --yes
```

Akceptuje wartości domyślne bez zadawania pytań (w tym kroki naprawy restartu/usługi/sandboxa, gdy ma to zastosowanie).

```bash
openclaw doctor --repair
```

Stosuje zalecane naprawy bez zadawania pytań (naprawy + restarty tam, gdzie jest to bezpieczne).

```bash
openclaw doctor --repair --force
```

Stosuje także agresywne naprawy (nadpisuje niestandardowe konfiguracje supervisora).

```bash
openclaw doctor --non-interactive
```

Uruchamia się bez pytań i stosuje tylko bezpieczne migracje (normalizacja konfiguracji + przenoszenie stanu na dysku). Pomija działania restartu/usługi/sandboxa wymagające potwierdzenia człowieka.
Migracje starszego stanu uruchamiają się automatycznie po wykryciu.

```bash
openclaw doctor --deep
```

Skanuje usługi systemowe pod kątem dodatkowych instalacji gatewaya (launchd/systemd/schtasks).

Jeśli chcesz przejrzeć zmiany przed zapisaniem, najpierw otwórz plik konfiguracji:

```bash
cat ~/.openclaw/openclaw.json
```

## Co robi (podsumowanie)

- Opcjonalna aktualizacja przed uruchomieniem dla instalacji git (tylko interaktywnie).
- Kontrola aktualności protokołu UI (przebudowuje Control UI, gdy schemat protokołu jest nowszy).
- Kontrola kondycji + monit o restart.
- Podsumowanie stanu Skills (gotowe/brakujące/zablokowane) i stan pluginów.
- Normalizacja konfiguracji dla starszych wartości.
- Migracja konfiguracji Talk ze starszych płaskich pól `talk.*` do `talk.provider` + `talk.providers.<provider>`.
- Kontrole migracji przeglądarki dla starszych konfiguracji rozszerzenia Chrome i gotowości Chrome MCP.
- Ostrzeżenia o nadpisaniu providera OpenCode (`models.providers.opencode` / `models.providers.opencode-go`).
- Kontrola wymagań wstępnych OAuth TLS dla profili OpenAI Codex OAuth.
- Migracja starszego stanu na dysku (sesje/katalog agenta/autoryzacja WhatsApp).
- Migracja starszych kluczy kontraktu manifestu pluginu (`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`).
- Migracja starszego magazynu cron (`jobId`, `schedule.cron`, pola delivery/payload na najwyższym poziomie, `provider` w payload, proste zadania zapasowe webhook z `notify: true`).
- Inspekcja plików blokady sesji i usuwanie nieaktualnych blokad.
- Kontrole integralności stanu i uprawnień (sesje, transkrypty, katalog stanu).
- Kontrole uprawnień pliku konfiguracji (chmod 600) przy uruchomieniu lokalnym.
- Kondycja uwierzytelniania modeli: sprawdza wygaśnięcie OAuth, może odświeżać wygasające tokeny i raportuje stany cooldown/disabled profilu auth.
- Wykrywanie dodatkowego katalogu workspace (`~/openclaw`).
- Naprawa obrazu sandboxa, gdy sandboxing jest włączony.
- Migracja starszej usługi i wykrywanie dodatkowych gatewayów.
- Migracja starszego stanu kanału Matrix (w trybie `--fix` / `--repair`).
- Kontrole środowiska uruchomieniowego gatewaya (usługa zainstalowana, ale nie działa; zapisany label launchd).
- Ostrzeżenia o stanie kanałów (sprawdzane z działającego gatewaya).
- Audyt konfiguracji supervisora (launchd/systemd/schtasks) z opcjonalną naprawą.
- Kontrole dobrych praktyk środowiska uruchomieniowego gatewaya (Node vs Bun, ścieżki menedżera wersji).
- Diagnostyka kolizji portu gatewaya (domyślnie `18789`).
- Ostrzeżenia bezpieczeństwa dla otwartych zasad wiadomości prywatnych.
- Kontrole uwierzytelniania gatewaya dla lokalnego trybu tokena (oferuje wygenerowanie tokena, gdy nie istnieje jego źródło; nie nadpisuje konfiguracji tokena SecretRef).
- Kontrola systemd linger w Linux.
- Kontrola rozmiaru plików bootstrapu workspace (ostrzeżenia o obcięciu / blisko limitu dla plików kontekstu).
- Kontrola stanu completion powłoki i automatyczna instalacja/aktualizacja.
- Kontrola gotowości providera embeddingów wyszukiwania pamięci (model lokalny, zdalny klucz API lub binarka QMD).
- Kontrole instalacji ze źródeł (niedopasowanie workspace pnpm, brak zasobów UI, brak binarki tsx).
- Zapisuje zaktualizowaną konfigurację i metadane kreatora.

## Szczegółowe zachowanie i uzasadnienie

### 0) Opcjonalna aktualizacja (instalacje git)

Jeśli to checkout git i doctor działa interaktywnie, proponuje
aktualizację (fetch/rebase/build) przed uruchomieniem doctor.

### 1) Normalizacja konfiguracji

Jeśli konfiguracja zawiera starsze kształty wartości (na przykład `messages.ackReaction`
bez nadpisania specyficznego dla kanału), doctor normalizuje je do bieżącego
schematu.

Dotyczy to także starszych płaskich pól Talk. Obecna publiczna konfiguracja Talk to
`talk.provider` + `talk.providers.<provider>`. Doctor przepisuje stare
kształty `talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` do mapy providerów.

### 2) Migracje starszych kluczy konfiguracji

Gdy konfiguracja zawiera przestarzałe klucze, inne polecenia odmawiają działania i proszą
o uruchomienie `openclaw doctor`.

Doctor:

- Wyjaśnia, które starsze klucze zostały znalezione.
- Pokazuje zastosowaną migrację.
- Przepisuje `~/.openclaw/openclaw.json` do zaktualizowanego schematu.

Gateway automatycznie uruchamia też migracje doctor przy starcie, gdy wykryje
starszy format konfiguracji, więc nieaktualne konfiguracje są naprawiane bez ręcznej interwencji.
Migracje magazynu zadań cron są obsługiwane przez `openclaw doctor --fix`.

Bieżące migracje:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → najwyższego poziomu `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- starsze `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- Dla kanałów z nazwanymi `accounts`, ale z pozostawionymi wartościami kanału najwyższego poziomu dla pojedynczego konta, przenieś te wartości o zakresie konta do promowanego konta wybranego dla tego kanału (`accounts.default` dla większości kanałów; Matrix może zachować istniejący pasujący cel nazwany/domyslny)
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- usuń `browser.relayBindHost` (starsze ustawienie relay rozszerzenia)

Ostrzeżenia doctor obejmują też wskazówki dotyczące domyślnego konta dla kanałów wielokontowych:

- Jeśli skonfigurowano co najmniej dwa wpisy `channels.<channel>.accounts` bez `channels.<channel>.defaultAccount` lub `accounts.default`, doctor ostrzega, że routing zapasowy może wybrać nieoczekiwane konto.
- Jeśli `channels.<channel>.defaultAccount` jest ustawione na nieznany identyfikator konta, doctor ostrzega i wyświetla skonfigurowane identyfikatory kont.

### 2b) Nadpisania providera OpenCode

Jeśli ręcznie dodano `models.providers.opencode`, `opencode-zen` lub `opencode-go`,
nadpisuje to wbudowany katalog OpenCode z `@mariozechner/pi-ai`.
Może to wymusić użycie niewłaściwego API przez modele albo wyzerować koszty. Doctor ostrzega, aby
usunąć nadpisanie i przywrócić routing API oraz koszty per model.

### 2c) Migracja przeglądarki i gotowość Chrome MCP

Jeśli konfiguracja przeglądarki nadal wskazuje usuniętą ścieżkę rozszerzenia Chrome, doctor
normalizuje ją do obecnego modelu podłączania host-local Chrome MCP:

- `browser.profiles.*.driver: "extension"` zmienia się na `"existing-session"`
- `browser.relayBindHost` jest usuwane

Doctor audytuje też ścieżkę host-local Chrome MCP, gdy używasz `defaultProfile:
"user"` lub skonfigurowanego profilu `existing-session`:

- sprawdza, czy Google Chrome jest zainstalowane na tym samym hoście dla domyślnych
  profili automatycznego połączenia
- sprawdza wykrytą wersję Chrome i ostrzega, gdy jest niższa niż Chrome 144
- przypomina o włączeniu zdalnego debugowania na stronie inspect przeglądarki (na
  przykład `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`
  lub `edge://inspect/#remote-debugging`)

Doctor nie może włączyć tego ustawienia po stronie Chrome za Ciebie. Host-local Chrome MCP
nadal wymaga:

- przeglądarki opartej na Chromium 144+ na hoście gatewaya/noda
- lokalnie uruchomionej przeglądarki
- włączonego zdalnego debugowania w tej przeglądarce
- zatwierdzenia pierwszego monitu o zgodę na podłączenie w przeglądarce

Gotowość tutaj dotyczy wyłącznie lokalnych wymagań wstępnych podłączenia. Existing-session zachowuje
obecne ograniczenia tras Chrome MCP; zaawansowane trasy takie jak `responsebody`, eksport PDF,
przechwytywanie pobierania i działania wsadowe nadal wymagają zarządzanej
przeglądarki lub surowego profilu CDP.

Ta kontrola **nie** dotyczy przepływów Docker, sandbox, remote-browser ani innych
przepływów headless. Nadal używają one surowego CDP.

### 2d) Wymagania wstępne OAuth TLS

Gdy skonfigurowano profil OpenAI Codex OAuth, doctor sonduje punkt autoryzacji OpenAI,
aby sprawdzić, czy lokalny stos TLS Node/OpenSSL może zweryfikować łańcuch certyfikatów.
Jeśli sonda zakończy się błędem certyfikatu (na przykład `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`, wygasły certyfikat lub certyfikat self-signed),
doctor wyświetla wskazówki naprawy zależne od platformy. Na macOS z Node z Homebrew
naprawą jest zwykle `brew postinstall ca-certificates`. Z `--deep` sonda uruchamia się
nawet wtedy, gdy gateway jest zdrowy.

### 3) Migracje starszego stanu (układ na dysku)

Doctor może migrować starsze układy na dysku do obecnej struktury:

- Magazyn sesji + transkrypty:
  - z `~/.openclaw/sessions/` do `~/.openclaw/agents/<agentId>/sessions/`
- Katalog agenta:
  - z `~/.openclaw/agent/` do `~/.openclaw/agents/<agentId>/agent/`
- Stan autoryzacji WhatsApp (Baileys):
  - ze starszego `~/.openclaw/credentials/*.json` (z wyjątkiem `oauth.json`)
  - do `~/.openclaw/credentials/whatsapp/<accountId>/...` (domyślny identyfikator konta: `default`)

Te migracje są wykonywane w trybie best-effort i są idempotentne; doctor wyświetli ostrzeżenia, gdy
pozostawi jakiekolwiek starsze foldery jako kopie zapasowe. Gateway/CLI także automatycznie migrują
starsze sesje + katalog agenta przy starcie, dzięki czemu historia/autoryzacja/modele trafiają do
ścieżki per agent bez ręcznego uruchamiania doctor. Autoryzacja WhatsApp jest celowo migrowana tylko
przez `openclaw doctor`. Normalizacja providera/mapy providerów Talk porównuje teraz
według równości strukturalnej, więc różnice wyłącznie w kolejności kluczy nie powodują już
powtarzalnych, pustych zmian `doctor --fix`.

### 3a) Migracje starszych manifestów pluginów

Doctor skanuje wszystkie zainstalowane manifesty pluginów pod kątem przestarzałych kluczy
możliwości na najwyższym poziomie (`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`). Po wykryciu proponuje przeniesienie ich do obiektu `contracts`
i przepisanie pliku manifestu na miejscu. Ta migracja jest idempotentna;
jeśli klucz `contracts` ma już te same wartości, starszy klucz jest usuwany
bez duplikowania danych.

### 3b) Migracje starszego magazynu cron

Doctor sprawdza też magazyn zadań cron (`~/.openclaw/cron/jobs.json` domyślnie,
lub `cron.store`, jeśli został nadpisany) pod kątem starych kształtów zadań, które scheduler nadal
akceptuje dla zgodności.

Bieżące porządki cron obejmują:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- pola payload najwyższego poziomu (`message`, `model`, `thinking`, ...) → `payload`
- pola delivery najwyższego poziomu (`deliver`, `channel`, `to`, `provider`, ...) → `delivery`
- aliasy delivery `provider` w payload → jawne `delivery.channel`
- proste starsze zadania zapasowe webhook z `notify: true` → jawne `delivery.mode="webhook"` z `delivery.to=cron.webhook`

Doctor automatycznie migruje zadania `notify: true` tylko wtedy, gdy może to zrobić
bez zmiany zachowania. Jeśli zadanie łączy starszy zapasowy webhook notify z istniejącym
trybem delivery innym niż webhook, doctor ostrzega i pozostawia takie zadanie do ręcznego przeglądu.

### 3c) Czyszczenie blokad sesji

Doctor skanuje katalog każdej sesji agenta pod kątem nieaktualnych plików write-lock — plików pozostawionych
po nienormalnym zakończeniu sesji. Dla każdego znalezionego pliku blokady raportuje:
ścieżkę, PID, czy PID nadal żyje, wiek blokady oraz czy jest
uznawana za nieaktualną (martwy PID lub starsza niż 30 minut). W trybie `--fix` / `--repair`
automatycznie usuwa nieaktualne pliki blokad; w przeciwnym razie wyświetla informację
i instruuje, aby uruchomić ponownie z `--fix`.

### 4) Kontrole integralności stanu (trwałość sesji, routing i bezpieczeństwo)

Katalog stanu to operacyjny rdzeń systemu. Jeśli zniknie, tracisz
sesje, poświadczenia, logi i konfigurację (chyba że masz kopie zapasowe gdzie indziej).

Doctor sprawdza:

- **Brak katalogu stanu**: ostrzega o katastrofalnej utracie stanu, proponuje odtworzenie
  katalogu i przypomina, że nie może odzyskać brakujących danych.
- **Uprawnienia katalogu stanu**: weryfikuje możliwość zapisu; oferuje naprawę uprawnień
  (i wyświetla wskazówkę `chown`, gdy wykryje niedopasowanie właściciela/grupy).
- **Katalog stanu zsynchronizowany z chmurą w macOS**: ostrzega, gdy stan znajduje się pod iCloud Drive
  (`~/Library/Mobile Documents/com~apple~CloudDocs/...`) lub
  `~/Library/CloudStorage/...`, ponieważ ścieżki oparte na synchronizacji mogą powodować wolniejsze I/O
  oraz wyścigi blokad/synchronizacji.
- **Katalog stanu na Linux na SD lub eMMC**: ostrzega, gdy stan znajduje się na źródle montowania `mmcblk*`,
  ponieważ losowe I/O na nośnikach SD lub eMMC może być wolniejsze i szybciej zużywać nośnik
  przy zapisach sesji i poświadczeń.
- **Brak katalogów sesji**: `sessions/` i katalog magazynu sesji są
  wymagane do zachowania historii i uniknięcia awarii `ENOENT`.
- **Niedopasowanie transkryptu**: ostrzega, gdy ostatnie wpisy sesji mają brakujące
  pliki transkryptu.
- **Główna sesja „1-line JSONL”**: oznacza sytuację, gdy główny transkrypt ma tylko jeden
  wiersz (historia się nie akumuluje).
- **Wiele katalogów stanu**: ostrzega, gdy istnieje wiele folderów `~/.openclaw` w różnych
  katalogach domowych lub gdy `OPENCLAW_STATE_DIR` wskazuje inne miejsce (historia może
  zostać podzielona między instalacje).
- **Przypomnienie o trybie zdalnym**: jeśli `gateway.mode=remote`, doctor przypomina, aby uruchomić
  go na hoście zdalnym (tam znajduje się stan).
- **Uprawnienia pliku konfiguracji**: ostrzega, jeśli `~/.openclaw/openclaw.json` ma
  odczyt dla grupy/wszystkich, i oferuje zaostrzenie do `600`.

### 5) Kondycja uwierzytelniania modeli (wygaśnięcie OAuth)

Doctor sprawdza profile OAuth w magazynie auth, ostrzega, gdy tokeny
wygasają/wygasły, i może je odświeżyć, gdy jest to bezpieczne. Jeśli profil
OAuth/token Anthropic jest nieaktualny, sugeruje klucz API Anthropic albo starszą
ścieżkę setup-token Anthropic.
Monity o odświeżenie pojawiają się tylko w trybie interaktywnym (TTY); `--non-interactive`
pomija próby odświeżenia.

Doctor wykrywa też nieaktualny usunięty stan Anthropic Claude CLI. Jeśli stare
bajty poświadczeń `anthropic:claude-cli` nadal istnieją w `auth-profiles.json`,
doctor konwertuje je z powrotem do profili token/OAuth Anthropic i przepisuje
nieaktualne odwołania do modeli `claude-cli/...`.
Jeśli bajty zniknęły, doctor usuwa nieaktualną konfigurację i wyświetla polecenia
odzyskiwania.

Doctor raportuje też profile auth, które są tymczasowo bezużyteczne z powodu:

- krótkich cooldownów (rate limits/timeouts/błędy auth)
- dłuższych wyłączeń (błędy rozliczeń/kredytu)

### 6) Walidacja modelu Hooks

Jeśli ustawiono `hooks.gmail.model`, doctor weryfikuje odwołanie do modelu względem
katalogu i allowlisty oraz ostrzega, gdy nie zostanie rozwiązane lub jest niedozwolone.

### 7) Naprawa obrazu sandboxa

Gdy sandboxing jest włączony, doctor sprawdza obrazy Docker i proponuje ich zbudowanie albo
przełączenie na starsze nazwy, jeśli obecny obraz nie istnieje.

### 7b) Zależności runtime pakietów pluginów

Doctor weryfikuje, czy zależności runtime pakietów wbudowanych pluginów (na przykład
pakiety runtime pluginu Discord) są obecne w katalogu głównym instalacji OpenClaw.
Jeśli którychkolwiek brakuje, doctor raportuje pakiety i instaluje je w trybie
`openclaw doctor --fix` / `openclaw doctor --repair`.

### 8) Migracje usług gatewaya i wskazówki czyszczenia

Doctor wykrywa starsze usługi gatewaya (launchd/systemd/schtasks) i
proponuje ich usunięcie oraz zainstalowanie usługi OpenClaw z użyciem bieżącego portu gatewaya.
Może też skanować dodatkowe usługi podobne do gatewaya i wyświetlać wskazówki czyszczenia.
Usługi gatewaya OpenClaw nazwane od profilu są traktowane jako pełnoprawne i nie są
oznaczane jako „dodatkowe”.

### 8b) Migracja Matrix przy starcie

Gdy konto kanału Matrix ma oczekującą lub wykonalną migrację starszego stanu,
doctor (w trybie `--fix` / `--repair`) tworzy migawkę przed migracją, a następnie
uruchamia kroki migracji best-effort: migrację starszego stanu Matrix oraz przygotowanie starszego
stanu zaszyfrowanego. Oba kroki nie są krytyczne; błędy są logowane i start trwa dalej.
W trybie tylko do odczytu (`openclaw doctor` bez `--fix`) ta kontrola
jest całkowicie pomijana.

### 9) Ostrzeżenia bezpieczeństwa

Doctor wyświetla ostrzeżenia, gdy provider jest otwarty na wiadomości prywatne bez
allowlisty albo gdy zasada jest skonfigurowana w niebezpieczny sposób.

### 10) systemd linger (Linux)

Jeśli działa jako usługa użytkownika systemd, doctor upewnia się, że lingering jest włączony,
aby gateway pozostawał aktywny po wylogowaniu.

### 11) Stan workspace (Skills, pluginy i starsze katalogi)

Doctor wyświetla podsumowanie stanu workspace dla domyślnego agenta:

- **Stan Skills**: liczba Skills gotowych, z brakującymi wymaganiami i zablokowanych przez allowlistę.
- **Starsze katalogi workspace**: ostrzega, gdy `~/openclaw` lub inne starsze katalogi workspace
  istnieją obok bieżącego workspace.
- **Stan pluginów**: liczba pluginów załadowanych/wyłączonych/z błędami; wypisuje identyfikatory pluginów dla
  błędów; raportuje możliwości pluginów w pakiecie.
- **Ostrzeżenia zgodności pluginów**: oznacza pluginy, które mają problemy zgodności z
  bieżącym runtime.
- **Diagnostyka pluginów**: pokazuje ostrzeżenia lub błędy zgłaszane przy ładowaniu przez
  rejestr pluginów.

### 11b) Rozmiar pliku bootstrap

Doctor sprawdza, czy pliki bootstrapu workspace (na przykład `AGENTS.md`,
`CLAUDE.md` lub inne wstrzykiwane pliki kontekstu) są blisko skonfigurowanego
limitu znaków lub go przekraczają. Raportuje dla każdego pliku liczbę znaków surowych vs. wstrzykniętych, procent
obcięcia, przyczynę obcięcia (`max/file` lub `max/total`) oraz łączną liczbę wstrzykniętych
znaków jako ułamek całkowitego limitu. Gdy pliki są obcięte lub blisko
limitu, doctor wyświetla wskazówki dotyczące dostrajania `agents.defaults.bootstrapMaxChars`
i `agents.defaults.bootstrapTotalMaxChars`.

### 11c) Completion powłoki

Doctor sprawdza, czy completion tabulatora jest zainstalowane dla bieżącej powłoki
(zsh, bash, fish lub PowerShell):

- Jeśli profil powłoki używa wolnego dynamicznego wzorca completion
  (`source <(openclaw completion ...)`), doctor aktualizuje go do szybszego
  wariantu z pliku cache.
- Jeśli completion jest skonfigurowane w profilu, ale brakuje pliku cache,
  doctor automatycznie odtwarza cache.
- Jeśli completion w ogóle nie jest skonfigurowane, doctor proponuje instalację
  (tylko tryb interaktywny; pomijane z `--non-interactive`).

Uruchom `openclaw completion --write-state`, aby ręcznie odtworzyć cache.

### 12) Kontrole uwierzytelniania gatewaya (token lokalny)

Doctor sprawdza gotowość uwierzytelniania tokenem lokalnego gatewaya.

- Jeśli tryb tokena wymaga tokena i nie istnieje jego źródło, doctor proponuje jego wygenerowanie.
- Jeśli `gateway.auth.token` jest zarządzany przez SecretRef, ale niedostępny, doctor ostrzega i nie nadpisuje go jawnym tekstem.
- `openclaw doctor --generate-gateway-token` wymusza wygenerowanie tylko wtedy, gdy nie skonfigurowano SecretRef tokena.

### 12b) Naprawy tylko do odczytu uwzględniające SecretRef

Niektóre przepływy napraw wymagają inspekcji skonfigurowanych poświadczeń bez osłabiania zachowania fail-fast w runtime.

- `openclaw doctor --fix` używa teraz tego samego modelu podsumowania SecretRef tylko do odczytu, co polecenia z rodziny status, dla ukierunkowanych napraw konfiguracji.
- Przykład: naprawa Telegram `allowFrom` / `groupAllowFrom` dla `@username` próbuje użyć skonfigurowanych poświadczeń bota, gdy są dostępne.
- Jeśli token bota Telegram jest skonfigurowany przez SecretRef, ale niedostępny w bieżącej ścieżce polecenia, doctor zgłasza, że poświadczenie jest skonfigurowane, ale niedostępne, i pomija automatyczne rozwiązywanie zamiast powodować awarię lub błędnie raportować brak tokena.

### 13) Kontrola kondycji gatewaya + restart

Doctor uruchamia kontrolę kondycji i proponuje restart gatewaya, gdy wygląda on
na niezdrowy.

### 13b) Gotowość wyszukiwania pamięci

Doctor sprawdza, czy skonfigurowany provider embeddingów wyszukiwania pamięci jest gotowy
dla domyślnego agenta. Zachowanie zależy od skonfigurowanego backendu i providera:

- **Backend QMD**: sonduje, czy binarka `qmd` jest dostępna i daje się uruchomić.
  Jeśli nie, wyświetla wskazówki naprawy, w tym pakiet npm i opcję ręcznej ścieżki do binarki.
- **Jawny provider lokalny**: sprawdza lokalny plik modelu albo rozpoznany
  zdalny/pobieralny URL modelu. Jeśli go brakuje, sugeruje przełączenie na providera zdalnego.
- **Jawny provider zdalny** (`openai`, `voyage` itd.): weryfikuje, czy klucz API
  jest obecny w środowisku lub magazynie auth. Jeśli go brakuje, wyświetla konkretne wskazówki naprawy.
- **Provider auto**: najpierw sprawdza dostępność modelu lokalnego, a potem próbuje każdego
  providera zdalnego w kolejności automatycznego wyboru.

Gdy dostępny jest wynik sondy gatewaya (gateway był zdrowy w czasie
kontroli), doctor porównuje go z konfiguracją widoczną dla CLI i odnotowuje
wszelkie rozbieżności.

Użyj `openclaw memory status --deep`, aby zweryfikować gotowość embeddingów w runtime.

### 14) Ostrzeżenia o stanie kanałów

Jeśli gateway jest zdrowy, doctor uruchamia sondę stanu kanałów i raportuje
ostrzeżenia z sugerowanymi naprawami.

### 15) Audyt konfiguracji supervisora + naprawa

Doctor sprawdza zainstalowaną konfigurację supervisora (launchd/systemd/schtasks) pod kątem
brakujących lub nieaktualnych wartości domyślnych (np. zależności systemd network-online i
opóźnienia restartu). Gdy znajdzie niedopasowanie, zaleca aktualizację i może
przepisać plik usługi/zadanie do bieżących wartości domyślnych.

Uwagi:

- `openclaw doctor` pyta przed przepisaniem konfiguracji supervisora.
- `openclaw doctor --yes` akceptuje domyślne monity naprawy.
- `openclaw doctor --repair` stosuje zalecane naprawy bez pytań.
- `openclaw doctor --repair --force` nadpisuje niestandardowe konfiguracje supervisora.
- Jeśli uwierzytelnianie tokenem wymaga tokena, a `gateway.auth.token` jest zarządzany przez SecretRef, instalacja/naprawa usługi przez doctor weryfikuje SecretRef, ale nie zapisuje rozwiązanych wartości tokena jawnym tekstem do metadanych środowiska usługi supervisora.
- Jeśli uwierzytelnianie tokenem wymaga tokena, a skonfigurowany SecretRef tokena nie jest rozwiązany, doctor blokuje ścieżkę instalacji/naprawy i podaje konkretne wskazówki.
- Jeśli skonfigurowane są zarówno `gateway.auth.token`, jak i `gateway.auth.password`, a `gateway.auth.mode` nie jest ustawione, doctor blokuje instalację/naprawę, dopóki tryb nie zostanie ustawiony jawnie.
- Dla jednostek Linux user-systemd kontrole dryfu tokena przez doctor obejmują teraz zarówno źródła `Environment=`, jak i `EnvironmentFile=` przy porównywaniu metadanych auth usługi.
- Zawsze możesz wymusić pełne przepisanie przez `openclaw gateway install --force`.

### 16) Diagnostyka runtime gatewaya + portu

Doctor analizuje runtime usługi (PID, ostatni status wyjścia) i ostrzega, gdy
usługa jest zainstalowana, ale faktycznie nie działa. Sprawdza też kolizje portów
na porcie gatewaya (domyślnie `18789`) i raportuje prawdopodobne przyczyny (gateway już
działa, tunel SSH).

### 17) Najlepsze praktyki runtime gatewaya

Doctor ostrzega, gdy usługa gatewaya działa na Bun albo na ścieżce Node zarządzanej przez menedżer wersji
(`nvm`, `fnm`, `volta`, `asdf` itd.). Kanały WhatsApp + Telegram wymagają Node,
a ścieżki menedżerów wersji mogą przestać działać po aktualizacjach, ponieważ usługa nie
ładuje inicjalizacji Twojej powłoki. Doctor proponuje migrację do systemowej instalacji Node, gdy
jest dostępna (Homebrew/apt/choco).

### 18) Zapis konfiguracji + metadane kreatora

Doctor zapisuje wszystkie zmiany konfiguracji i oznacza metadane kreatora, aby zarejestrować
uruchomienie doctor.

### 19) Wskazówki dotyczące workspace (kopie zapasowe + system pamięci)

Doctor sugeruje system pamięci workspace, jeśli go brakuje, i wyświetla wskazówkę dotyczącą kopii zapasowej,
jeśli workspace nie jest już pod kontrolą git.

Zobacz [/concepts/agent-workspace](/pl/concepts/agent-workspace), aby uzyskać pełny przewodnik po
strukturze workspace i kopii zapasowej git (zalecane prywatne GitHub lub GitLab).
