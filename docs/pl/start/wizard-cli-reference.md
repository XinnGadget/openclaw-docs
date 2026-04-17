---
read_when:
    - Potrzebujesz szczegółowego opisu działania `openclaw onboard`
    - Debugujesz wyniki onboardingu lub integrujesz klientów onboardingu
sidebarTitle: CLI reference
summary: Pełna dokumentacja referencyjna przepływu konfiguracji CLI, konfiguracji uwierzytelniania/modeli, danych wyjściowych i elementów wewnętrznych
title: Dokumentacja referencyjna konfiguracji CLI
x-i18n:
    generated_at: "2026-04-15T14:41:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# Dokumentacja referencyjna konfiguracji CLI

Ta strona zawiera pełną dokumentację referencyjną dla `openclaw onboard`.
Krótki przewodnik znajdziesz w [Onboarding (CLI)](/pl/start/wizard).

## Co robi kreator

Tryb lokalny (domyślny) przeprowadza Cię przez:

- Konfigurację modelu i uwierzytelniania (OAuth subskrypcji OpenAI Code, Anthropic Claude CLI lub klucz API, a także opcje MiniMax, GLM, Ollama, Moonshot, StepFun i AI Gateway)
- Lokalizację obszaru roboczego i pliki bootstrap
- Ustawienia Gateway (port, bind, uwierzytelnianie, tailscale)
- Kanały i dostawców (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles i inne dołączone Pluginy kanałów)
- Instalację demona (LaunchAgent, jednostka użytkownika systemd lub natywne zadanie Harmonogramu zadań Windows z awaryjnym użyciem folderu Autostart)
- Kontrolę stanu
- Konfigurację Skills

Tryb zdalny konfiguruje tę maszynę do łączenia się z Gateway uruchomionym gdzie indziej.
Nie instaluje ani nie modyfikuje niczego na zdalnym hoście.

## Szczegóły przepływu lokalnego

<Steps>
  <Step title="Wykrywanie istniejącej konfiguracji">
    - Jeśli istnieje `~/.openclaw/openclaw.json`, wybierz Zachowaj, Zmodyfikuj lub Zresetuj.
    - Ponowne uruchomienie kreatora niczego nie usuwa, chyba że jawnie wybierzesz Reset (lub przekażesz `--reset`).
    - CLI `--reset` domyślnie obejmuje `config+creds+sessions`; użyj `--reset-scope full`, aby usunąć także obszar roboczy.
    - Jeśli konfiguracja jest nieprawidłowa lub zawiera przestarzałe klucze, kreator zatrzymuje się i prosi o uruchomienie `openclaw doctor` przed kontynuowaniem.
    - Reset używa `trash` i oferuje zakresy:
      - Tylko konfiguracja
      - Konfiguracja + poświadczenia + sesje
      - Pełny reset (usuwa także obszar roboczy)
  </Step>
  <Step title="Model i uwierzytelnianie">
    - Pełna macierz opcji znajduje się w [Opcje uwierzytelniania i modeli](#auth-and-model-options).
  </Step>
  <Step title="Obszar roboczy">
    - Domyślnie `~/.openclaw/workspace` (konfigurowalne).
    - Tworzy pliki obszaru roboczego potrzebne do bootstrap ritual przy pierwszym uruchomieniu.
    - Układ obszaru roboczego: [Agent workspace](/pl/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Wyświetla pytania o port, bind, tryb uwierzytelniania i ekspozycję tailscale.
    - Zalecane: pozostaw włączone uwierzytelnianie tokenem nawet dla loopback, aby lokalni klienci WS musieli się uwierzytelniać.
    - W trybie tokena interaktywna konfiguracja oferuje:
      - **Wygeneruj/zapisz token w postaci jawnej** (domyślnie)
      - **Użyj SecretRef** (opcjonalnie)
    - W trybie hasła interaktywna konfiguracja również obsługuje przechowywanie jawne lub SecretRef.
    - Ścieżka nieinteraktywna dla tokena SecretRef: `--gateway-token-ref-env <ENV_VAR>`.
      - Wymaga niepustej zmiennej środowiskowej w środowisku procesu onboardingu.
      - Nie może być łączona z `--gateway-token`.
    - Wyłączaj uwierzytelnianie tylko wtedy, gdy w pełni ufasz każdemu lokalnemu procesowi.
    - Bindy inne niż loopback nadal wymagają uwierzytelniania.
  </Step>
  <Step title="Kanały">
    - [WhatsApp](/pl/channels/whatsapp): opcjonalne logowanie kodem QR
    - [Telegram](/pl/channels/telegram): token bota
    - [Discord](/pl/channels/discord): token bota
    - [Google Chat](/pl/channels/googlechat): JSON konta usługi + webhook audience
    - [Mattermost](/pl/channels/mattermost): token bota + bazowy URL
    - [Signal](/pl/channels/signal): opcjonalna instalacja `signal-cli` + konfiguracja konta
    - [BlueBubbles](/pl/channels/bluebubbles): zalecane dla iMessage; URL serwera + hasło + webhook
    - [iMessage](/pl/channels/imessage): starsza ścieżka do CLI `imsg` + dostęp do DB
    - Bezpieczeństwo DM: domyślnie używane jest parowanie. Pierwsza wiadomość DM wysyła kod; zatwierdź przez
      `openclaw pairing approve <channel> <code>` albo użyj list dozwolonych.
  </Step>
  <Step title="Instalacja demona">
    - macOS: LaunchAgent
      - Wymaga sesji zalogowanego użytkownika; dla środowiska bezgłowego użyj własnego LaunchDaemon (nie jest dostarczany).
    - Linux i Windows przez WSL2: jednostka użytkownika systemd
      - Kreator próbuje wykonać `loginctl enable-linger <user>`, aby Gateway działał po wylogowaniu.
      - Może poprosić o sudo (zapisuje do `/var/lib/systemd/linger`); najpierw próbuje bez sudo.
    - Natywny Windows: najpierw Harmonogram zadań
      - Jeśli utworzenie zadania zostanie odrzucone, OpenClaw przechodzi na element logowania per użytkownik w folderze Autostart i natychmiast uruchamia Gateway.
      - Harmonogram zadań pozostaje preferowany, ponieważ zapewnia lepszy status nadzorcy.
    - Wybór środowiska uruchomieniowego: Node (zalecane; wymagane dla WhatsApp i Telegram). Bun nie jest zalecany.
  </Step>
  <Step title="Kontrola stanu">
    - Uruchamia Gateway (jeśli potrzeba) i wykonuje `openclaw health`.
    - `openclaw status --deep` dodaje do danych wyjściowych statusu sondę kondycji działającego Gateway, w tym sondy kanałów, gdy są obsługiwane.
  </Step>
  <Step title="Skills">
    - Odczytuje dostępne Skills i sprawdza wymagania.
    - Pozwala wybrać menedżera Node: npm, pnpm lub bun.
    - Instaluje opcjonalne zależności (niektóre używają Homebrew na macOS).
  </Step>
  <Step title="Zakończenie">
    - Podsumowanie i kolejne kroki, w tym opcje aplikacji iOS, Android i macOS.
  </Step>
</Steps>

<Note>
Jeśli nie zostanie wykryty żaden interfejs GUI, kreator wypisze instrukcje przekierowania portów SSH dla Control UI zamiast otwierać przeglądarkę.
Jeśli brakuje zasobów Control UI, kreator spróbuje je zbudować; rozwiązaniem awaryjnym jest `pnpm ui:build` (automatycznie instaluje zależności UI).
</Note>

## Szczegóły trybu zdalnego

Tryb zdalny konfiguruje tę maszynę do łączenia się z Gateway uruchomionym gdzie indziej.

<Info>
Tryb zdalny nie instaluje ani nie modyfikuje niczego na zdalnym hoście.
</Info>

Co ustawiasz:

- URL zdalnego Gateway (`ws://...`)
- Token, jeśli zdalny Gateway wymaga uwierzytelniania (zalecane)

<Note>
- Jeśli Gateway jest dostępny tylko przez loopback, użyj tunelowania SSH lub tailnet.
- Wskazówki dotyczące wykrywania:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Opcje uwierzytelniania i modeli

<AccordionGroup>
  <Accordion title="Klucz API Anthropic">
    Używa `ANTHROPIC_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje go do użycia przez demona.
  </Accordion>
  <Accordion title="Subskrypcja OpenAI Code (ponowne użycie Codex CLI)">
    Jeśli istnieje `~/.codex/auth.json`, kreator może użyć go ponownie.
    Ponownie użyte poświadczenia Codex CLI pozostają zarządzane przez Codex CLI; po wygaśnięciu OpenClaw
    najpierw ponownie odczytuje to źródło, a gdy dostawca może je odświeżyć, zapisuje
    odświeżone poświadczenie z powrotem do magazynu Codex zamiast samodzielnie
    przejmować nad nim kontrolę.
  </Accordion>
  <Accordion title="Subskrypcja OpenAI Code (OAuth)">
    Przepływ w przeglądarce; wklej `code#state`.

    Ustawia `agents.defaults.model` na `openai-codex/gpt-5.4`, gdy model nie jest ustawiony lub ma postać `openai/*`.

  </Accordion>
  <Accordion title="Klucz API OpenAI">
    Używa `OPENAI_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje poświadczenie w profilach uwierzytelniania.

    Ustawia `agents.defaults.model` na `openai/gpt-5.4`, gdy model nie jest ustawiony, ma postać `openai/*` lub `openai-codex/*`.

  </Accordion>
  <Accordion title="Klucz API xAI (Grok)">
    Prosi o `XAI_API_KEY` i konfiguruje xAI jako dostawcę modeli.
  </Accordion>
  <Accordion title="OpenCode">
    Prosi o `OPENCODE_API_KEY` (lub `OPENCODE_ZEN_API_KEY`) i pozwala wybrać katalog Zen lub Go.
    URL konfiguracji: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="Klucz API (ogólny)">
    Zapisuje klucz za Ciebie.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Prosi o `AI_GATEWAY_API_KEY`.
    Więcej szczegółów: [Vercel AI Gateway](/pl/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Prosi o ID konta, ID Gateway i `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    Więcej szczegółów: [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Konfiguracja jest zapisywana automatycznie. Domyślny model hostowany to `MiniMax-M2.7`; konfiguracja z kluczem API używa
    `minimax/...`, a konfiguracja OAuth używa `minimax-portal/...`.
    Więcej szczegółów: [MiniMax](/pl/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Konfiguracja jest zapisywana automatycznie dla StepFun standard lub Step Plan na chińskich albo globalnych punktach końcowych.
    Standard obecnie obejmuje `step-3.5-flash`, a Step Plan obejmuje także `step-3.5-flash-2603`.
    Więcej szczegółów: [StepFun](/pl/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (zgodny z Anthropic)">
    Prosi o `SYNTHETIC_API_KEY`.
    Więcej szczegółów: [Synthetic](/pl/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud i lokalne modele otwarte)">
    Najpierw prosi o wybór `Cloud + Local`, `Cloud only` lub `Local only`.
    `Cloud only` używa `OLLAMA_API_KEY` z `https://ollama.com`.
    Tryby oparte na hoście proszą o bazowy URL (domyślnie `http://127.0.0.1:11434`), wykrywają dostępne modele i sugerują wartości domyślne.
    `Cloud + Local` sprawdza także, czy ten host Ollama jest zalogowany z dostępem do chmury.
    Więcej szczegółów: [Ollama](/pl/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot i Kimi Coding">
    Konfiguracje Moonshot (Kimi K2) i Kimi Coding są zapisywane automatycznie.
    Więcej szczegółów: [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot).
  </Accordion>
  <Accordion title="Dostawca niestandardowy">
    Działa z punktami końcowymi zgodnymi z OpenAI i zgodnymi z Anthropic.

    Interaktywny onboarding obsługuje te same opcje przechowywania kluczy API co inne przepływy kluczy API dostawców:
    - **Wklej klucz API teraz** (jawnie)
    - **Użyj odwołania do sekretu** (odwołanie do env lub skonfigurowanego dostawcy, z walidacją wstępną)

    Flagi nieinteraktywne:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (opcjonalne; awaryjnie używa `CUSTOM_API_KEY`)
    - `--custom-provider-id` (opcjonalne)
    - `--custom-compatibility <openai|anthropic>` (opcjonalne; domyślnie `openai`)

  </Accordion>
  <Accordion title="Pomiń">
    Pozostawia uwierzytelnianie nieskonfigurowane.
  </Accordion>
</AccordionGroup>

Zachowanie modeli:

- Wybierz model domyślny z wykrytych opcji albo ręcznie wprowadź dostawcę i model.
- Gdy onboarding rozpoczyna się od wyboru uwierzytelniania dostawcy, selektor modeli automatycznie preferuje
  tego dostawcę. W przypadku Volcengine i BytePlus ta sama preferencja
  obejmuje także ich warianty coding-plan (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Jeśli ten filtr preferowanego dostawcy byłby pusty, selektor wraca do
  pełnego katalogu zamiast pokazywać brak modeli.
- Kreator uruchamia sprawdzenie modelu i ostrzega, jeśli skonfigurowany model jest nieznany lub brakuje uwierzytelniania.

Ścieżki poświadczeń i profili:

- Profile uwierzytelniania (klucze API + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Import starszego OAuth: `~/.openclaw/credentials/oauth.json`

Tryb przechowywania poświadczeń:

- Domyślne zachowanie onboardingu zapisuje klucze API jako jawne wartości w profilach uwierzytelniania.
- `--secret-input-mode ref` włącza tryb odwołań zamiast jawnego przechowywania kluczy.
  W konfiguracji interaktywnej możesz wybrać jedno z poniższych:
  - odwołanie do zmiennej środowiskowej (na przykład `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - odwołanie do skonfigurowanego dostawcy (`file` lub `exec`) z aliasem dostawcy + ID
- Interaktywny tryb odwołań uruchamia szybką walidację wstępną przed zapisaniem.
  - Odwołania env: sprawdza nazwę zmiennej i niepustą wartość w bieżącym środowisku onboardingu.
  - Odwołania dostawcy: sprawdza konfigurację dostawcy i rozwiązuje żądane ID.
  - Jeśli walidacja wstępna się nie powiedzie, onboarding pokaże błąd i pozwoli spróbować ponownie.
- W trybie nieinteraktywnym `--secret-input-mode ref` jest obsługiwany tylko przez env.
  - Ustaw zmienną środowiskową dostawcy w środowisku procesu onboardingu.
  - Flagi kluczy inline (na przykład `--openai-api-key`) wymagają ustawienia tej zmiennej env; w przeciwnym razie onboarding zakończy się natychmiast błędem.
  - Dla dostawców niestandardowych nieinteraktywny tryb `ref` zapisuje `models.providers.<id>.apiKey` jako `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - W tym przypadku dostawcy niestandardowego `--custom-api-key` wymaga ustawienia `CUSTOM_API_KEY`; w przeciwnym razie onboarding zakończy się natychmiast błędem.
- Poświadczenia uwierzytelniania Gateway obsługują w konfiguracji interaktywnej wybór między jawnym zapisem i SecretRef:
  - Tryb tokena: **Wygeneruj/zapisz token w postaci jawnej** (domyślnie) albo **Użyj SecretRef**.
  - Tryb hasła: jawnie albo SecretRef.
- Ścieżka nieinteraktywna dla tokena SecretRef: `--gateway-token-ref-env <ENV_VAR>`.
- Istniejące konfiguracje z jawnym przechowywaniem nadal działają bez zmian.

<Note>
Wskazówka dla środowisk bezgłowych i serwerowych: ukończ OAuth na maszynie z przeglądarką, a następnie skopiuj
plik `auth-profiles.json` tego agenta (na przykład
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` lub odpowiadającą mu
ścieżkę `$OPENCLAW_STATE_DIR/...`) na host Gateway. `credentials/oauth.json`
jest tylko starszym źródłem importu.
</Note>

## Dane wyjściowe i elementy wewnętrzne

Typowe pola w `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (jeśli wybrano MiniMax)
- `tools.profile` (lokalny onboarding domyślnie ustawia `"coding"`, gdy wartość nie jest ustawiona; istniejące jawne wartości są zachowywane)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (lokalny onboarding domyślnie ustawia tu `per-channel-peer`, gdy wartość nie jest ustawiona; istniejące jawne wartości są zachowywane)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Listy dozwolonych kanałów (Slack, Discord, Matrix, Microsoft Teams), gdy włączysz tę opcję podczas pytań (nazwy są rozwiązywane do identyfikatorów, jeśli to możliwe)
- `skills.install.nodeManager`
  - Flaga `setup --node-manager` akceptuje `npm`, `pnpm` lub `bun`.
  - Ręczna konfiguracja nadal może później ustawić `skills.install.nodeManager: "yarn"`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` zapisuje `agents.list[]` oraz opcjonalne `bindings`.

Poświadczenia WhatsApp trafiają do `~/.openclaw/credentials/whatsapp/<accountId>/`.
Sesje są przechowywane w `~/.openclaw/agents/<agentId>/sessions/`.

<Note>
Niektóre kanały są dostarczane jako Pluginy. Po wybraniu podczas konfiguracji kreator
prosi o zainstalowanie Pluginu (npm lub ścieżka lokalna) przed konfiguracją kanału.
</Note>

RPC kreatora Gateway:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

Klienci (aplikacja macOS i Control UI) mogą renderować kroki bez ponownego implementowania logiki onboardingu.

Zachowanie konfiguracji Signal:

- Pobiera odpowiedni zasób wydania
- Zapisuje go w `~/.openclaw/tools/signal-cli/<version>/`
- Zapisuje `channels.signal.cliPath` w konfiguracji
- Kompilacje JVM wymagają Java 21
- Kompilacje natywne są używane, gdy są dostępne
- Windows używa WSL2 i stosuje linuksowy przepływ `signal-cli` wewnątrz WSL

## Powiązane dokumenty

- Centrum onboardingu: [Onboarding (CLI)](/pl/start/wizard)
- Automatyzacja i skrypty: [CLI Automation](/pl/start/wizard-cli-automation)
- Dokumentacja polecenia: [`openclaw onboard`](/cli/onboard)
