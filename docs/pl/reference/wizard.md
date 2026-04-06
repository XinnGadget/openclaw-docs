---
read_when:
    - Szukasz konkretnego kroku lub flagi onboardingu
    - Automatyzujesz onboarding w trybie nieinteraktywnym
    - Debugujesz zachowanie onboardingu
sidebarTitle: Onboarding Reference
summary: 'Pełna dokumentacja referencyjna onboardingu w CLI: każdy krok, flaga i pole konfiguracji'
title: Dokumentacja referencyjna onboardingu
x-i18n:
    generated_at: "2026-04-06T03:13:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: e02a4da4a39ba335199095723f5d3b423671eb12efc2d9e4f9e48c1e8ee18419
    source_path: reference/wizard.md
    workflow: 15
---

# Dokumentacja referencyjna onboardingu

To jest pełna dokumentacja referencyjna dla `openclaw onboard`.
Aby zapoznać się z omówieniem na wysokim poziomie, zobacz [Onboarding (CLI)](/pl/start/wizard).

## Szczegóły przepływu (tryb lokalny)

<Steps>
  <Step title="Wykrywanie istniejącej konfiguracji">
    - Jeśli istnieje `~/.openclaw/openclaw.json`, wybierz **Keep / Modify / Reset**.
    - Ponowne uruchomienie onboardingu **nie** usuwa niczego, chyba że jawnie wybierzesz **Reset**
      (albo przekażesz `--reset`).
    - CLI `--reset` domyślnie używa `config+creds+sessions`; użyj `--reset-scope full`,
      aby usunąć także przestrzeń roboczą.
    - Jeśli konfiguracja jest nieprawidłowa albo zawiera starsze klucze, kreator zatrzymuje się i prosi
      o uruchomienie `openclaw doctor` przed kontynuowaniem.
    - Reset używa `trash` (nigdy `rm`) i oferuje zakresy:
      - Tylko konfiguracja
      - Konfiguracja + poświadczenia + sesje
      - Pełny reset (usuwa także przestrzeń roboczą)
  </Step>
  <Step title="Model/Auth">
    - **Klucz API Anthropic**: używa `ANTHROPIC_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje go do użycia przez demona.
    - **Klucz API Anthropic**: preferowany wybór asystenta Anthropic w onboardingu/configure.
    - **Anthropic setup-token (legacy/manual)**: ponownie dostępny w onboarding/configure, ale Anthropic poinformował użytkowników OpenClaw, że ścieżka logowania Claude w OpenClaw liczy się jako użycie zewnętrznego harnessu i wymaga **Extra Usage** na koncie Claude.
    - **Subskrypcja OpenAI Code (Codex) (Codex CLI)**: jeśli istnieje `~/.codex/auth.json`, onboarding może go ponownie użyć. Ponownie użyte poświadczenia Codex CLI pozostają zarządzane przez Codex CLI; po wygaśnięciu OpenClaw najpierw ponownie odczytuje to źródło i, gdy dostawca może je odświeżyć, zapisuje odświeżone poświadczenie z powrotem do magazynu Codex zamiast samodzielnie przejmować nad nim kontrolę.
    - **Subskrypcja OpenAI Code (Codex) (OAuth)**: przepływ w przeglądarce; wklej `code#state`.
      - Ustawia `agents.defaults.model` na `openai-codex/gpt-5.4`, gdy model nie jest ustawiony albo ma postać `openai/*`.
    - **Klucz API OpenAI**: używa `OPENAI_API_KEY`, jeśli jest obecny, albo prosi o klucz, a następnie zapisuje go w profilach uwierzytelniania.
      - Ustawia `agents.defaults.model` na `openai/gpt-5.4`, gdy model nie jest ustawiony, ma postać `openai/*` albo `openai-codex/*`.
    - **Klucz API xAI (Grok)**: prosi o `XAI_API_KEY` i konfiguruje xAI jako dostawcę modeli.
    - **OpenCode**: prosi o `OPENCODE_API_KEY` (albo `OPENCODE_ZEN_API_KEY`, uzyskaj go na https://opencode.ai/auth) i pozwala wybrać katalog Zen albo Go.
    - **Ollama**: prosi o bazowy URL Ollama, oferuje tryb **Cloud + Local** albo **Local**, wykrywa dostępne modele i automatycznie pobiera wybrany model lokalny, gdy jest to potrzebne.
    - Więcej szczegółów: [Ollama](/pl/providers/ollama)
    - **Klucz API**: zapisuje klucz za Ciebie.
    - **Vercel AI Gateway (wielomodelowe proxy)**: prosi o `AI_GATEWAY_API_KEY`.
    - Więcej szczegółów: [Vercel AI Gateway](/pl/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: prosi o Account ID, Gateway ID i `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - Więcej szczegółów: [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway)
    - **MiniMax**: konfiguracja jest zapisywana automatycznie; domyślny model hostowany to `MiniMax-M2.7`.
      Konfiguracja z kluczem API używa `minimax/...`, a konfiguracja OAuth używa
      `minimax-portal/...`.
    - Więcej szczegółów: [MiniMax](/pl/providers/minimax)
    - **StepFun**: konfiguracja jest zapisywana automatycznie dla StepFun standard albo Step Plan na endpointach chińskich lub globalnych.
    - Standard obecnie obejmuje `step-3.5-flash`, a Step Plan obejmuje także `step-3.5-flash-2603`.
    - Więcej szczegółów: [StepFun](/pl/providers/stepfun)
    - **Synthetic (zgodny z Anthropic)**: prosi o `SYNTHETIC_API_KEY`.
    - Więcej szczegółów: [Synthetic](/pl/providers/synthetic)
    - **Moonshot (Kimi K2)**: konfiguracja jest zapisywana automatycznie.
    - **Kimi Coding**: konfiguracja jest zapisywana automatycznie.
    - Więcej szczegółów: [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot)
    - **Skip**: uwierzytelnianie nie jest jeszcze skonfigurowane.
    - Wybierz model domyślny spośród wykrytych opcji (albo wpisz ręcznie `provider/model`). Aby uzyskać najlepszą jakość i mniejsze ryzyko prompt injection, wybierz najsilniejszy model najnowszej generacji dostępny w Twoim stosie dostawców.
    - Onboarding uruchamia sprawdzenie modelu i ostrzega, jeśli skonfigurowany model jest nieznany albo brakuje dla niego uwierzytelniania.
    - Tryb przechowywania kluczy API domyślnie używa jawnych wartości w profilach uwierzytelniania. Użyj `--secret-input-mode ref`, aby zamiast tego przechowywać odwołania oparte na env (na przykład `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Profile uwierzytelniania znajdują się w `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (klucze API + OAuth). `~/.openclaw/credentials/oauth.json` jest starszym źródłem tylko do importu.
    - Więcej szczegółów: [/concepts/oauth](/pl/concepts/oauth)
    <Note>
    Wskazówka dla środowisk headless/serwerowych: ukończ OAuth na maszynie z przeglądarką, a następnie skopiuj
    `auth-profiles.json` tego agenta (na przykład
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` albo odpowiadającą
    ścieżkę `$OPENCLAW_STATE_DIR/...`) na host bramy. `credentials/oauth.json`
    jest tylko starszym źródłem importu.
    </Note>
  </Step>
  <Step title="Przestrzeń robocza">
    - Domyślnie `~/.openclaw/workspace` (konfigurowalne).
    - Inicjalizuje pliki przestrzeni roboczej potrzebne do rytuału bootstrapu agenta.
    - Pełny układ przestrzeni roboczej + przewodnik po kopiach zapasowych: [Agent workspace](/pl/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, tryb uwierzytelniania, ekspozycja Tailscale.
    - Zalecenie dotyczące uwierzytelniania: pozostaw **Token** nawet dla loopback, aby lokalni klienci WS musieli się uwierzytelnić.
    - W trybie tokena konfiguracja interaktywna oferuje:
      - **Generate/store plaintext token** (domyślnie)
      - **Use SecretRef** (opcjonalnie)
      - Quickstart ponownie używa istniejących SecretRef `gateway.auth.token` w dostawcach `env`, `file` i `exec` do bootstrapu testu onboardingu/panelu.
      - Jeśli ten SecretRef jest skonfigurowany, ale nie można go rozstrzygnąć, onboarding kończy się wcześnie z jasnym komunikatem naprawczym zamiast po cichu osłabiać uwierzytelnianie runtime.
    - W trybie hasła konfiguracja interaktywna obsługuje również przechowywanie jawne albo SecretRef.
    - Ścieżka SecretRef tokena w trybie nieinteraktywnym: `--gateway-token-ref-env <ENV_VAR>`.
      - Wymaga niepustej zmiennej env w środowisku procesu onboardingu.
      - Nie można łączyć z `--gateway-token`.
    - Wyłączaj uwierzytelnianie tylko wtedy, gdy w pełni ufasz każdemu lokalnemu procesowi.
    - Powiązania inne niż loopback nadal wymagają uwierzytelniania.
  </Step>
  <Step title="Kanały">
    - [WhatsApp](/pl/channels/whatsapp): opcjonalne logowanie przez kod QR.
    - [Telegram](/pl/channels/telegram): token bota.
    - [Discord](/pl/channels/discord): token bota.
    - [Google Chat](/pl/channels/googlechat): JSON konta usługi + webhook audience.
    - [Mattermost](/pl/channels/mattermost) (plugin): token bota + bazowy URL.
    - [Signal](/pl/channels/signal): opcjonalna instalacja `signal-cli` + konfiguracja konta.
    - [BlueBubbles](/pl/channels/bluebubbles): **zalecane dla iMessage**; URL serwera + hasło + webhook.
    - [iMessage](/pl/channels/imessage): starsza ścieżka CLI `imsg` + dostęp do DB.
    - Bezpieczeństwo DM: domyślnie używane jest parowanie. Pierwszy DM wysyła kod; zatwierdź przez `openclaw pairing approve <channel> <code>` albo użyj list dozwolonych.
  </Step>
  <Step title="Wyszukiwanie w sieci">
    - Wybierz obsługiwanego dostawcę, takiego jak Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG lub Tavily (albo pomiń).
    - Dostawcy oparty na API mogą używać zmiennych env albo istniejącej konfiguracji do szybkiej konfiguracji; dostawcy bez kluczy używają zamiast tego własnych wymagań wstępnych.
    - Pomiń przez `--skip-search`.
    - Skonfiguruj później: `openclaw configure --section web`.
  </Step>
  <Step title="Instalacja demona">
    - macOS: LaunchAgent
      - Wymaga zalogowanej sesji użytkownika; dla środowisk headless użyj własnego LaunchDaemon (nie jest dostarczany).
    - Linux (oraz Windows przez WSL2): jednostka systemd użytkownika
      - Onboarding próbuje włączyć lingering przez `loginctl enable-linger <user>`, aby Gateway działał dalej po wylogowaniu.
      - Może poprosić o sudo (zapisuje do `/var/lib/systemd/linger`); najpierw próbuje bez sudo.
    - **Wybór runtime:** Node (zalecany; wymagany dla WhatsApp/Telegram). Bun jest **niezalecany**.
    - Jeśli uwierzytelnianie tokenem wymaga tokena, a `gateway.auth.token` jest zarządzany przez SecretRef, instalacja demona go weryfikuje, ale nie zapisuje rozstrzygniętych jawnych wartości tokena w metadanych środowiska usługi nadzorcy.
    - Jeśli uwierzytelnianie tokenem wymaga tokena, a skonfigurowany SecretRef tokena jest nierozstrzygnięty, instalacja demona jest blokowana z instrukcjami możliwymi do wykonania.
    - Jeśli skonfigurowano jednocześnie `gateway.auth.token` i `gateway.auth.password`, a `gateway.auth.mode` nie jest ustawione, instalacja demona jest blokowana, dopóki tryb nie zostanie ustawiony jawnie.
  </Step>
  <Step title="Kontrola kondycji">
    - Uruchamia Gateway (jeśli to potrzebne) i wykonuje `openclaw health`.
    - Wskazówka: `openclaw status --deep` dodaje do wyniku statusu test kondycji działającej bramy, w tym testy kanałów, gdy są obsługiwane (wymaga osiągalnej bramy).
  </Step>
  <Step title="Skills (zalecane)">
    - Odczytuje dostępne Skills i sprawdza wymagania.
    - Pozwala wybrać menedżer Node: **npm / pnpm** (bun nie jest zalecany).
    - Instaluje opcjonalne zależności (niektóre używają Homebrew na macOS).
  </Step>
  <Step title="Zakończenie">
    - Podsumowanie + kolejne kroki, w tym aplikacje iOS/Android/macOS dla dodatkowych funkcji.
  </Step>
</Steps>

<Note>
Jeśli nie wykryto GUI, onboarding wypisuje instrukcje przekierowania portów SSH dla Control UI zamiast otwierać przeglądarkę.
Jeśli brakuje zasobów Control UI, onboarding próbuje je zbudować; fallback to `pnpm ui:build` (automatycznie instaluje zależności UI).
</Note>

## Tryb nieinteraktywny

Użyj `--non-interactive`, aby zautomatyzować onboarding lub uruchamiać go w skryptach:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Dodaj `--json`, aby uzyskać podsumowanie w formacie czytelnym maszynowo.

SecretRef tokena Gateway w trybie nieinteraktywnym:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` i `--gateway-token-ref-env` wzajemnie się wykluczają.

<Note>
`--json` **nie** implikuje trybu nieinteraktywnego. Użyj `--non-interactive` (oraz `--workspace`) w skryptach.
</Note>

Przykłady poleceń specyficznych dla dostawców znajdują się w [CLI Automation](/pl/start/wizard-cli-automation#provider-specific-examples).
Używaj tej strony referencyjnej do semantyki flag i kolejności kroków.

### Dodawanie agenta (tryb nieinteraktywny)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## RPC kreatora Gateway

Gateway udostępnia przepływ onboardingu przez RPC (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
Klienci (aplikacja macOS, Control UI) mogą renderować kroki bez ponownego implementowania logiki onboardingu.

## Konfiguracja Signal (signal-cli)

Onboarding może zainstalować `signal-cli` z wydań GitHub:

- Pobiera odpowiedni zasób wydania.
- Zapisuje go w `~/.openclaw/tools/signal-cli/<version>/`.
- Zapisuje `channels.signal.cliPath` do Twojej konfiguracji.

Uwagi:

- Buildy JVM wymagają **Java 21**.
- Gdy to możliwe, używane są buildy natywne.
- Windows używa WSL2; instalacja signal-cli przebiega zgodnie z przepływem Linux wewnątrz WSL.

## Co zapisuje kreator

Typowe pola w `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (jeśli wybrano Minimax)
- `tools.profile` (lokalny onboarding domyślnie używa `"coding"`, gdy wartość nie jest ustawiona; istniejące jawne wartości są zachowywane)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (szczegóły zachowania: [CLI Setup Reference](/pl/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Listy dozwolonych kanałów (Slack/Discord/Matrix/Microsoft Teams), gdy wyrazisz na to zgodę podczas promptów (nazwy są rozstrzygane do ID, gdy to możliwe).
- `skills.install.nodeManager`
  - `setup --node-manager` akceptuje `npm`, `pnpm` lub `bun`.
  - Konfiguracja ręczna nadal może używać `yarn`, ustawiając bezpośrednio `skills.install.nodeManager`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` zapisuje `agents.list[]` oraz opcjonalne `bindings`.

Poświadczenia WhatsApp trafiają do `~/.openclaw/credentials/whatsapp/<accountId>/`.
Sesje są przechowywane w `~/.openclaw/agents/<agentId>/sessions/`.

Niektóre kanały są dostarczane jako pluginy. Gdy wybierzesz taki kanał podczas konfiguracji, onboarding
zaproponuje jego instalację (npm albo lokalna ścieżka), zanim będzie można go skonfigurować.

## Powiązane dokumenty

- Omówienie onboardingu: [Onboarding (CLI)](/pl/start/wizard)
- Onboarding w aplikacji macOS: [Onboarding](/pl/start/onboarding)
- Dokumentacja referencyjna konfiguracji: [Gateway configuration](/pl/gateway/configuration)
- Dostawcy: [WhatsApp](/pl/channels/whatsapp), [Telegram](/pl/channels/telegram), [Discord](/pl/channels/discord), [Google Chat](/pl/channels/googlechat), [Signal](/pl/channels/signal), [BlueBubbles](/pl/channels/bluebubbles) (iMessage), [iMessage](/pl/channels/imessage) (legacy)
- Skills: [Skills](/pl/tools/skills), [Skills config](/pl/tools/skills-config)
