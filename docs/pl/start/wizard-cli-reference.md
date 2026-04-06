---
read_when:
    - Potrzebujesz szczegółowego opisu działania `openclaw onboard`
    - Debugujesz wyniki onboardingu lub integrujesz klientów onboardingu
sidebarTitle: CLI reference
summary: Pełna dokumentacja przepływu konfiguracji CLI, konfiguracji auth/modelu, danych wyjściowych i elementów wewnętrznych
title: Dokumentacja konfiguracji CLI
x-i18n:
    generated_at: "2026-04-06T03:13:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 92f379b34a2b48c68335dae4f759117c770f018ec51b275f4f40421c6b3abb23
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# Dokumentacja konfiguracji CLI

Ta strona zawiera pełną dokumentację `openclaw onboard`.
Krótki przewodnik znajdziesz w [Onboarding (CLI)](/pl/start/wizard).

## Co robi kreator

Tryb lokalny (domyślny) prowadzi przez:

- konfigurację modelu i auth (subskrypcja OpenAI Code OAuth, Anthropic Claude CLI lub klucz API, a także opcje MiniMax, GLM, Ollama, Moonshot, StepFun i AI Gateway)
- lokalizację workspace i pliki bootstrap
- ustawienia Gateway (`port`, `bind`, `auth`, Tailscale)
- kanały i providery (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles i inne bundled channel plugins)
- instalację demona (LaunchAgent, jednostka użytkownika systemd lub natywne zadanie Windows Scheduled Task z fallbackiem do folderu Startup)
- kontrolę stanu
- konfigurację Skills

Tryb zdalny konfiguruje tę maszynę do łączenia się z gatewayem uruchomionym gdzie indziej.
Nie instaluje ani nie modyfikuje niczego na zdalnym hoście.

## Szczegóły przepływu lokalnego

<Steps>
  <Step title="Wykrywanie istniejącej konfiguracji">
    - Jeśli istnieje `~/.openclaw/openclaw.json`, wybierz Zachowaj, Zmień lub Resetuj.
    - Ponowne uruchomienie kreatora niczego nie usuwa, chyba że jawnie wybierzesz Resetuj (albo przekażesz `--reset`).
    - CLI `--reset` domyślnie obejmuje `config+creds+sessions`; użyj `--reset-scope full`, aby usunąć także workspace.
    - Jeśli konfiguracja jest nieprawidłowa lub zawiera starsze klucze, kreator zatrzymuje się i prosi o uruchomienie `openclaw doctor` przed kontynuacją.
    - Reset używa `trash` i oferuje zakresy:
      - Tylko konfiguracja
      - Konfiguracja + poświadczenia + sesje
      - Pełny reset (usuwa także workspace)
  </Step>
  <Step title="Model i auth">
    - Pełna macierz opcji znajduje się w [Opcje auth i modeli](#auth-and-model-options).
  </Step>
  <Step title="Workspace">
    - Domyślnie `~/.openclaw/workspace` (można zmienić).
    - Seeduje pliki workspace potrzebne do bootstrapu przy pierwszym uruchomieniu.
    - Układ workspace: [Workspace agenta](/pl/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Pyta o port, bind, tryb auth i ekspozycję przez tailscale.
    - Zalecenie: pozostaw włączone auth tokenem nawet dla loopback, aby lokalni klienci WS musieli się uwierzytelniać.
    - W trybie tokenu konfiguracja interaktywna oferuje:
      - **Wygeneruj/zapisz token jawny** (domyślnie)
      - **Użyj SecretRef** (opcjonalnie)
    - W trybie hasła konfiguracja interaktywna także obsługuje przechowywanie jawne lub przez SecretRef.
    - Nieinteraktywna ścieżka SecretRef dla tokenu: `--gateway-token-ref-env <ENV_VAR>`.
      - Wymaga niepustej zmiennej env w środowisku procesu onboardingu.
      - Nie można łączyć z `--gateway-token`.
    - Wyłączaj auth tylko wtedy, gdy w pełni ufasz każdemu lokalnemu procesowi.
    - Bindowania inne niż loopback nadal wymagają auth.
  </Step>
  <Step title="Kanały">
    - [WhatsApp](/pl/channels/whatsapp): opcjonalne logowanie QR
    - [Telegram](/pl/channels/telegram): token bota
    - [Discord](/pl/channels/discord): token bota
    - [Google Chat](/pl/channels/googlechat): JSON konta usługi + webhook audience
    - [Mattermost](/pl/channels/mattermost): token bota + podstawowy URL
    - [Signal](/pl/channels/signal): opcjonalna instalacja `signal-cli` + konfiguracja konta
    - [BlueBubbles](/pl/channels/bluebubbles): zalecane dla iMessage; URL serwera + hasło + webhook
    - [iMessage](/pl/channels/imessage): starsza ścieżka CLI `imsg` + dostęp do DB
    - Bezpieczeństwo DM: domyślnie pairing. Pierwszy DM wysyła kod; zatwierdź przez
      `openclaw pairing approve <channel> <code>` albo użyj list dozwolonych.
  </Step>
  <Step title="Instalacja demona">
    - macOS: LaunchAgent
      - Wymaga zalogowanej sesji użytkownika; dla trybu bezgłowego użyj niestandardowego LaunchDaemon (nie jest dostarczany).
    - Linux i Windows przez WSL2: jednostka użytkownika systemd
      - Kreator próbuje wykonać `loginctl enable-linger <user>`, aby gateway działał po wylogowaniu.
      - Może poprosić o sudo (zapisuje do `/var/lib/systemd/linger`); najpierw próbuje bez sudo.
    - Natywny Windows: najpierw Scheduled Task
      - Jeśli utworzenie zadania zostanie odrzucone, OpenClaw przełącza się na element logowania per użytkownik w folderze Startup i natychmiast uruchamia gateway.
      - Scheduled Tasks pozostają preferowane, ponieważ zapewniają lepszy status nadzorcy.
    - Wybór runtime: Node (zalecane; wymagane dla WhatsApp i Telegram). Bun nie jest zalecany.
  </Step>
  <Step title="Kontrola stanu">
    - Uruchamia gateway (jeśli potrzeba) i wykonuje `openclaw health`.
    - `openclaw status --deep` dodaje aktywną sondę stanu gatewaya do wyjścia statusu, w tym sondy kanałów, gdy są obsługiwane.
  </Step>
  <Step title="Skills">
    - Odczytuje dostępne Skills i sprawdza wymagania.
    - Pozwala wybrać menedżer Node: npm, pnpm lub bun.
    - Instaluje opcjonalne zależności (niektóre używają Homebrew na macOS).
  </Step>
  <Step title="Zakończenie">
    - Podsumowanie i kolejne kroki, w tym opcje aplikacji na iOS, Androida i macOS.
  </Step>
</Steps>

<Note>
Jeśli nie zostanie wykryty interfejs GUI, kreator wypisze instrukcje przekierowania portów SSH dla Control UI zamiast otwierać przeglądarkę.
Jeśli brakuje zasobów Control UI, kreator próbuje je zbudować; fallback to `pnpm ui:build` (automatycznie instaluje zależności UI).
</Note>

## Szczegóły trybu zdalnego

Tryb zdalny konfiguruje tę maszynę do łączenia się z gatewayem uruchomionym gdzie indziej.

<Info>
Tryb zdalny nie instaluje ani nie modyfikuje niczego na zdalnym hoście.
</Info>

Co ustawiasz:

- URL zdalnego gatewaya (`ws://...`)
- Token, jeśli zdalny gateway wymaga auth (zalecane)

<Note>
- Jeśli gateway jest dostępny tylko przez loopback, użyj tunelowania SSH albo tailnet.
- Wskazówki wykrywania:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Opcje auth i modeli

<AccordionGroup>
  <Accordion title="Klucz API Anthropic">
    Używa `ANTHROPIC_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje go do użycia przez demona.
  </Accordion>
  <Accordion title="Subskrypcja OpenAI Code (ponowne użycie Codex CLI)">
    Jeśli istnieje `~/.codex/auth.json`, kreator może go ponownie użyć.
    Ponownie użyte poświadczenia Codex CLI pozostają zarządzane przez Codex CLI; po wygaśnięciu OpenClaw
    najpierw ponownie odczytuje to źródło i, gdy provider może je odświeżyć, zapisuje
    odświeżone poświadczenie z powrotem do pamięci Codex zamiast samodzielnie przejmować
    nad nim kontrolę.
  </Accordion>
  <Accordion title="Subskrypcja OpenAI Code (OAuth)">
    Przepływ w przeglądarce; wklej `code#state`.

    Ustawia `agents.defaults.model` na `openai-codex/gpt-5.4`, gdy model nie jest ustawiony albo ma postać `openai/*`.

  </Accordion>
  <Accordion title="Klucz API OpenAI">
    Używa `OPENAI_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje poświadczenie w profilach auth.

    Ustawia `agents.defaults.model` na `openai/gpt-5.4`, gdy model nie jest ustawiony, ma postać `openai/*` albo `openai-codex/*`.

  </Accordion>
  <Accordion title="Klucz API xAI (Grok)">
    Prosi o `XAI_API_KEY` i konfiguruje xAI jako providera modeli.
  </Accordion>
  <Accordion title="OpenCode">
    Prosi o `OPENCODE_API_KEY` (albo `OPENCODE_ZEN_API_KEY`) i pozwala wybrać katalog Zen lub Go.
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
    Prosi o identyfikator konta, identyfikator gatewaya i `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    Więcej szczegółów: [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Konfiguracja jest zapisywana automatycznie. Domyślny model hostowany to `MiniMax-M2.7`; konfiguracja z kluczem API używa
    `minimax/...`, a konfiguracja OAuth używa `minimax-portal/...`.
    Więcej szczegółów: [MiniMax](/pl/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Konfiguracja jest zapisywana automatycznie dla StepFun standard lub Step Plan na endpointach chińskich albo globalnych.
    Standard obejmuje obecnie `step-3.5-flash`, a Step Plan obejmuje również `step-3.5-flash-2603`.
    Więcej szczegółów: [StepFun](/pl/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (zgodny z Anthropic)">
    Prosi o `SYNTHETIC_API_KEY`.
    Więcej szczegółów: [Synthetic](/pl/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud i lokalne otwarte modele)">
    Prosi o podstawowy URL (domyślnie `http://127.0.0.1:11434`), a następnie oferuje tryb Cloud + Local albo Local.
    Wykrywa dostępne modele i sugeruje wartości domyślne.
    Więcej szczegółów: [Ollama](/pl/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot i Kimi Coding">
    Konfiguracje Moonshot (Kimi K2) i Kimi Coding są zapisywane automatycznie.
    Więcej szczegółów: [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot).
  </Accordion>
  <Accordion title="Niestandardowy provider">
    Działa z endpointami zgodnymi z OpenAI i zgodnymi z Anthropic.

    Interaktywny onboarding obsługuje te same opcje przechowywania klucza API, co inne przepływy klucza API providera:
    - **Wklej teraz klucz API** (jawnie)
    - **Użyj odwołania do sekretu** (odwołanie env lub skonfigurowane odwołanie providera, z walidacją preflight)

    Flagi nieinteraktywne:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (opcjonalne; fallback do `CUSTOM_API_KEY`)
    - `--custom-provider-id` (opcjonalne)
    - `--custom-compatibility <openai|anthropic>` (opcjonalne; domyślnie `openai`)

  </Accordion>
  <Accordion title="Pomiń">
    Pozostawia auth bez konfiguracji.
  </Accordion>
</AccordionGroup>

Zachowanie modeli:

- Wybierz model domyślny z wykrytych opcji albo wpisz providera i model ręcznie.
- Gdy onboarding startuje od wyboru auth providera, selektor modeli automatycznie preferuje
  tego providera. W przypadku Volcengine i BytePlus ta sama preferencja
  dopasowuje również ich warianty planów coding (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Jeśli taki filtr preferowanego providera byłby pusty, selektor wraca do pełnego katalogu zamiast pokazywać brak modeli.
- Kreator wykonuje kontrolę modelu i ostrzega, jeśli skonfigurowany model jest nieznany albo brakuje auth.

Ścieżki poświadczeń i profili:

- Profile auth (klucze API + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Starszy import OAuth: `~/.openclaw/credentials/oauth.json`

Tryb przechowywania poświadczeń:

- Domyślne zachowanie onboardingu zapisuje klucze API jako wartości jawne w profilach auth.
- `--secret-input-mode ref` włącza tryb odwołań zamiast jawnego przechowywania kluczy.
  W konfiguracji interaktywnej możesz wybrać:
  - odwołanie do zmiennej środowiskowej (na przykład `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - skonfigurowane odwołanie providera (`file` lub `exec`) z aliasem providera + id
- Interaktywny tryb odwołań wykonuje szybką walidację preflight przed zapisaniem.
  - Odwołania env: sprawdza nazwę zmiennej i niepustą wartość w bieżącym środowisku onboardingu.
  - Odwołania providera: sprawdza konfigurację providera i rozwiązuje żądane id.
  - Jeśli preflight się nie powiedzie, onboarding pokazuje błąd i pozwala spróbować ponownie.
- W trybie nieinteraktywnym `--secret-input-mode ref` działa tylko z env.
  - Ustaw zmienną env providera w środowisku procesu onboardingu.
  - Flagi kluczy inline (na przykład `--openai-api-key`) wymagają ustawienia tej zmiennej env; w przeciwnym razie onboarding kończy się natychmiast błędem.
  - Dla niestandardowych providerów nieinteraktywny tryb `ref` zapisuje `models.providers.<id>.apiKey` jako `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - W tym przypadku niestandardowego providera `--custom-api-key` wymaga ustawienia `CUSTOM_API_KEY`; w przeciwnym razie onboarding kończy się natychmiast błędem.
- Poświadczenia auth gatewaya obsługują w konfiguracji interaktywnej wybór jawnego zapisu i SecretRef:
  - Tryb tokenu: **Wygeneruj/zapisz token jawny** (domyślnie) albo **Użyj SecretRef**.
  - Tryb hasła: zapis jawny albo SecretRef.
- Nieinteraktywna ścieżka SecretRef dla tokenu: `--gateway-token-ref-env <ENV_VAR>`.
- Istniejące konfiguracje jawne nadal działają bez zmian.

<Note>
Wskazówka dla środowisk bezgłowych i serwerowych: zakończ OAuth na maszynie z przeglądarką, a następnie skopiuj
`auth-profiles.json` tego agenta (na przykład
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` albo odpowiadającą
ścieżkę `$OPENCLAW_STATE_DIR/...`) na host gatewaya. `credentials/oauth.json`
jest wyłącznie starszym źródłem importu.
</Note>

## Dane wyjściowe i elementy wewnętrzne

Typowe pola w `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (jeśli wybrano Minimax)
- `tools.profile` (lokalny onboarding domyślnie ustawia `"coding"`, gdy brak wartości; istniejące jawne wartości są zachowywane)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (lokalny onboarding domyślnie ustawia `per-channel-peer`, gdy brak wartości; istniejące jawne wartości są zachowywane)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Listy dozwolonych kanałów (Slack, Discord, Matrix, Microsoft Teams), gdy włączysz je podczas promptów (nazwy są rozwiązywane do identyfikatorów, gdy to możliwe)
- `skills.install.nodeManager`
  - Flaga `setup --node-manager` akceptuje `npm`, `pnpm` lub `bun`.
  - Konfiguracja ręczna nadal może później ustawić `skills.install.nodeManager: "yarn"`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` zapisuje `agents.list[]` i opcjonalne `bindings`.

Poświadczenia WhatsApp trafiają do `~/.openclaw/credentials/whatsapp/<accountId>/`.
Sesje są przechowywane w `~/.openclaw/agents/<agentId>/sessions/`.

<Note>
Niektóre kanały są dostarczane jako pluginy. Gdy zostaną wybrane podczas konfiguracji, kreator
prosi o zainstalowanie pluginu (npm lub lokalna ścieżka) przed konfiguracją kanału.
</Note>

RPC kreatora gatewaya:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

Klienci (aplikacja macOS i Control UI) mogą renderować kroki bez ponownej implementacji logiki onboardingu.

Zachowanie konfiguracji Signal:

- Pobiera odpowiedni zasób wydania
- Przechowuje go w `~/.openclaw/tools/signal-cli/<version>/`
- Zapisuje `channels.signal.cliPath` w konfiguracji
- Buildy JVM wymagają Java 21
- Jeśli są dostępne, używane są buildy natywne
- Windows używa WSL2 i stosuje przepływ Linux `signal-cli` wewnątrz WSL

## Powiązana dokumentacja

- Centrum onboardingu: [Onboarding (CLI)](/pl/start/wizard)
- Automatyzacja i skrypty: [Automatyzacja CLI](/pl/start/wizard-cli-automation)
- Dokumentacja poleceń: [`openclaw onboard`](/cli/onboard)
