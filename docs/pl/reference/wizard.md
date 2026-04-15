---
read_when:
    - Wyszukiwanie konkretnego kroku lub flagi onboardingu
    - Automatyzacja onboardingu za pomocą trybu nieinteraktywnego
    - Debugowanie zachowania onboardingu
sidebarTitle: Onboarding Reference
summary: 'Pełna dokumentacja referencyjna onboardingu CLI: każdy krok, flaga i pole konfiguracji'
title: Dokumentacja referencyjna onboardingu
x-i18n:
    generated_at: "2026-04-15T14:40:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# Dokumentacja referencyjna onboardingu

To pełna dokumentacja referencyjna dla `openclaw onboard`.
Aby zobaczyć omówienie na wysokim poziomie, przejdź do [Onboarding (CLI)](/pl/start/wizard).

## Szczegóły przebiegu (tryb lokalny)

<Steps>
  <Step title="Wykrywanie istniejącej konfiguracji">
    - Jeśli istnieje `~/.openclaw/openclaw.json`, wybierz **Zachowaj / Zmodyfikuj / Zresetuj**.
    - Ponowne uruchomienie onboardingu **nie** usuwa niczego, chyba że jawnie wybierzesz **Zresetuj**
      (lub przekażesz `--reset`).
    - CLI `--reset` domyślnie ustawia `config+creds+sessions`; użyj `--reset-scope full`,
      aby usunąć także workspace.
    - Jeśli konfiguracja jest nieprawidłowa lub zawiera starsze klucze, kreator zatrzyma się i poprosi
      o uruchomienie `openclaw doctor` przed kontynuacją.
    - Reset używa `trash` (nigdy `rm`) i oferuje zakresy:
      - Tylko konfiguracja
      - Konfiguracja + poświadczenia + sesje
      - Pełny reset (usuwa także workspace)
  </Step>
  <Step title="Model/Uwierzytelnianie">
    - **Klucz API Anthropic**: używa `ANTHROPIC_API_KEY`, jeśli jest obecny, lub prosi o klucz, a następnie zapisuje go do użycia przez demon.
    - **Klucz API Anthropic**: preferowany wybór asystenta Anthropic w onboardingu/konfiguracji.
    - **Token konfiguracji Anthropic**: nadal dostępny w onboardingu/konfiguracji, chociaż OpenClaw preferuje teraz ponowne użycie Claude CLI, gdy jest dostępne.
    - **Subskrypcja OpenAI Code (Codex) (Codex CLI)**: jeśli istnieje `~/.codex/auth.json`, onboarding może go ponownie użyć. Ponownie użyte poświadczenia Codex CLI pozostają zarządzane przez Codex CLI; po wygaśnięciu OpenClaw najpierw ponownie odczytuje to źródło i, gdy dostawca może je odświeżyć, zapisuje odświeżone poświadczenie z powrotem do magazynu Codex zamiast samodzielnie przejmować nad nim kontrolę.
    - **Subskrypcja OpenAI Code (Codex) (OAuth)**: przepływ w przeglądarce; wklej `code#state`.
      - Ustawia `agents.defaults.model` na `openai-codex/gpt-5.4`, gdy model nie jest ustawiony lub ma postać `openai/*`.
    - **Klucz API OpenAI**: używa `OPENAI_API_KEY`, jeśli jest obecny, lub prosi o klucz, a następnie zapisuje go w profilach uwierzytelniania.
      - Ustawia `agents.defaults.model` na `openai/gpt-5.4`, gdy model nie jest ustawiony, ma postać `openai/*` lub `openai-codex/*`.
    - **Klucz API xAI (Grok)**: prosi o `XAI_API_KEY` i konfiguruje xAI jako dostawcę modelu.
    - **OpenCode**: prosi o `OPENCODE_API_KEY` (lub `OPENCODE_ZEN_API_KEY`, uzyskaj go na https://opencode.ai/auth) i pozwala wybrać katalog Zen lub Go.
    - **Ollama**: najpierw oferuje **Cloud + Local**, **Cloud only** lub **Local only**. `Cloud only` prosi o `OLLAMA_API_KEY` i używa `https://ollama.com`; tryby oparte na hoście proszą o bazowy URL Ollama, wykrywają dostępne modele i automatycznie pobierają wybrany model lokalny, jeśli to konieczne; `Cloud + Local` sprawdza również, czy ten host Ollama jest zalogowany do dostępu do chmury.
    - Więcej szczegółów: [Ollama](/pl/providers/ollama)
    - **Klucz API**: zapisuje klucz za Ciebie.
    - **Vercel AI Gateway (wielomodelowy serwer proxy)**: prosi o `AI_GATEWAY_API_KEY`.
    - Więcej szczegółów: [Vercel AI Gateway](/pl/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: prosi o Account ID, Gateway ID i `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - Więcej szczegółów: [Cloudflare AI Gateway](/pl/providers/cloudflare-ai-gateway)
    - **MiniMax**: konfiguracja jest zapisywana automatycznie; domyślny model hostowany to `MiniMax-M2.7`.
      Konfiguracja z kluczem API używa `minimax/...`, a konfiguracja OAuth używa
      `minimax-portal/...`.
    - Więcej szczegółów: [MiniMax](/pl/providers/minimax)
    - **StepFun**: konfiguracja jest zapisywana automatycznie dla StepFun standard lub Step Plan na endpointach chińskich albo globalnych.
    - Wersja standardowa obejmuje obecnie `step-3.5-flash`, a Step Plan obejmuje również `step-3.5-flash-2603`.
    - Więcej szczegółów: [StepFun](/pl/providers/stepfun)
    - **Synthetic (zgodny z Anthropic)**: prosi o `SYNTHETIC_API_KEY`.
    - Więcej szczegółów: [Synthetic](/pl/providers/synthetic)
    - **Moonshot (Kimi K2)**: konfiguracja jest zapisywana automatycznie.
    - **Kimi Coding**: konfiguracja jest zapisywana automatycznie.
    - Więcej szczegółów: [Moonshot AI (Kimi + Kimi Coding)](/pl/providers/moonshot)
    - **Pomiń**: uwierzytelnianie nie jest jeszcze skonfigurowane.
    - Wybierz domyślny model spośród wykrytych opcji (lub wpisz ręcznie dostawcę/model). Aby uzyskać najlepszą jakość i mniejsze ryzyko prompt injection, wybierz najmocniejszy model najnowszej generacji dostępny w stosie Twoich dostawców.
    - Onboarding uruchamia sprawdzenie modelu i ostrzega, jeśli skonfigurowany model jest nieznany lub brakuje uwierzytelniania.
    - Tryb przechowywania klucza API domyślnie używa jawnych wartości w profilu uwierzytelniania. Użyj `--secret-input-mode ref`, aby zamiast tego zapisać odwołania oparte na zmiennych środowiskowych (na przykład `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Profile uwierzytelniania znajdują się w `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (klucze API + OAuth). `~/.openclaw/credentials/oauth.json` jest starszym źródłem tylko do importu.
    - Więcej szczegółów: [/concepts/oauth](/pl/concepts/oauth)
    <Note>
    Wskazówka dla środowisk bez GUI/serwerowych: ukończ OAuth na maszynie z przeglądarką, a następnie skopiuj
    `auth-profiles.json` tego agenta (na przykład
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` lub odpowiadającą mu
    ścieżkę `$OPENCLAW_STATE_DIR/...`) na host Gateway. `credentials/oauth.json`
    jest tylko starszym źródłem importu.
    </Note>
  </Step>
  <Step title="Workspace">
    - Domyślnie `~/.openclaw/workspace` (konfigurowalne).
    - Tworzy pliki workspace potrzebne do rytuału bootstrap agenta.
    - Pełny układ workspace + przewodnik po kopiach zapasowych: [Workspace agenta](/pl/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, tryb uwierzytelniania, ekspozycja Tailscale.
    - Zalecenie dotyczące uwierzytelniania: zachowaj **Token** nawet dla loopback, aby lokalni klienci WS musieli się uwierzytelnić.
    - W trybie tokena interaktywna konfiguracja oferuje:
      - **Wygeneruj/zapisz jawny token** (domyślnie)
      - **Użyj SecretRef** (opcjonalnie)
      - Quickstart ponownie używa istniejących SecretRef `gateway.auth.token` w dostawcach `env`, `file` i `exec` do bootstrapu sondy onboardingu/panelu.
      - Jeśli ten SecretRef jest skonfigurowany, ale nie można go rozwiązać, onboarding kończy się wcześniej z jasnym komunikatem o sposobie naprawy zamiast po cichu obniżać poziom uwierzytelniania środowiska uruchomieniowego.
    - W trybie hasła interaktywna konfiguracja także obsługuje przechowywanie jawne lub SecretRef.
    - Ścieżka SecretRef tokena w trybie nieinteraktywnym: `--gateway-token-ref-env <ENV_VAR>`.
      - Wymaga niepustej zmiennej środowiskowej w środowisku procesu onboardingu.
      - Nie można łączyć z `--gateway-token`.
    - Wyłączaj uwierzytelnianie tylko wtedy, gdy w pełni ufasz każdemu lokalnemu procesowi.
    - Powiązania inne niż loopback nadal wymagają uwierzytelniania.
  </Step>
  <Step title="Kanały">
    - [WhatsApp](/pl/channels/whatsapp): opcjonalne logowanie kodem QR.
    - [Telegram](/pl/channels/telegram): token bota.
    - [Discord](/pl/channels/discord): token bota.
    - [Google Chat](/pl/channels/googlechat): JSON konta usługi + odbiorca webhooka.
    - [Mattermost](/pl/channels/mattermost) (Plugin): token bota + bazowy URL.
    - [Signal](/pl/channels/signal): opcjonalna instalacja `signal-cli` + konfiguracja konta.
    - [BlueBubbles](/pl/channels/bluebubbles): **zalecane dla iMessage**; URL serwera + hasło + Webhook.
    - [iMessage](/pl/channels/imessage): starsza ścieżka CLI `imsg` + dostęp do bazy danych.
    - Zabezpieczenia DM: domyślnie używane jest parowanie. Pierwsza wiadomość DM wysyła kod; zatwierdź przez `openclaw pairing approve <channel> <code>` lub użyj list dozwolonych.
  </Step>
  <Step title="Wyszukiwanie w sieci">
    - Wybierz obsługiwanego dostawcę, takiego jak Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG lub Tavily (albo pomiń).
    - Dostawcy opierający się na API mogą używać zmiennych środowiskowych lub istniejącej konfiguracji do szybkiej konfiguracji; dostawcy bez kluczy używają zamiast tego własnych wymagań wstępnych.
    - Pomiń za pomocą `--skip-search`.
    - Skonfiguruj później: `openclaw configure --section web`.
  </Step>
  <Step title="Instalacja demona">
    - macOS: LaunchAgent
      - Wymaga zalogowanej sesji użytkownika; w środowiskach bezobsługowych użyj niestandardowego LaunchDaemon (nie jest dostarczany).
    - Linux (oraz Windows przez WSL2): jednostka użytkownika systemd
      - Onboarding próbuje włączyć lingering przez `loginctl enable-linger <user>`, aby Gateway działał po wylogowaniu.
      - Może poprosić o sudo (zapisuje do `/var/lib/systemd/linger`); najpierw próbuje bez sudo.
    - **Wybór środowiska uruchomieniowego:** Node (zalecane; wymagane dla WhatsApp/Telegram). Bun **nie jest zalecany**.
    - Jeśli uwierzytelnianie tokenem wymaga tokena, a `gateway.auth.token` jest zarządzane przez SecretRef, instalacja demona weryfikuje go, ale nie zapisuje rozwiązanych jawnych wartości tokena w metadanych środowiska usługi nadzorcy.
    - Jeśli uwierzytelnianie tokenem wymaga tokena, a skonfigurowany SecretRef tokena nie jest rozwiązany, instalacja demona zostaje zablokowana z praktycznymi wskazówkami.
    - Jeśli skonfigurowane są jednocześnie `gateway.auth.token` i `gateway.auth.password`, a `gateway.auth.mode` nie jest ustawione, instalacja demona zostaje zablokowana do czasu jawnego ustawienia trybu.
  </Step>
  <Step title="Kontrola stanu">
    - Uruchamia Gateway (jeśli to potrzebne) i wykonuje `openclaw health`.
    - Wskazówka: `openclaw status --deep` dodaje sondę stanu działającego Gateway do danych wyjściowych statusu, w tym sondy kanałów tam, gdzie są obsługiwane (wymaga osiągalnego Gateway).
  </Step>
  <Step title="Skills (zalecane)">
    - Odczytuje dostępne Skills i sprawdza wymagania.
    - Pozwala wybrać menedżera Node: **npm / pnpm** (bun nie jest zalecany).
    - Instaluje opcjonalne zależności (niektóre używają Homebrew na macOS).
  </Step>
  <Step title="Zakończenie">
    - Podsumowanie + kolejne kroki, w tym aplikacje iOS/Android/macOS dla dodatkowych funkcji.
  </Step>
</Steps>

<Note>
Jeśli nie wykryto GUI, onboarding wyświetla instrukcje przekierowania portów SSH dla interfejsu Control UI zamiast otwierać przeglądarkę.
Jeśli brakuje zasobów interfejsu Control UI, onboarding próbuje je zbudować; ścieżką awaryjną jest `pnpm ui:build` (automatycznie instaluje zależności UI).
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
`--json` **nie** oznacza trybu nieinteraktywnego. W skryptach używaj `--non-interactive` (oraz `--workspace`).
</Note>

Przykłady poleceń specyficzne dla dostawców znajdują się w [Automatyzacja CLI](/pl/start/wizard-cli-automation#provider-specific-examples).
Używaj tej strony referencyjnej do sprawdzania semantyki flag i kolejności kroków.

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
Klienci (aplikacja macOS, Control UI) mogą renderować kroki bez ponownej implementacji logiki onboardingu.

## Konfiguracja Signal (signal-cli)

Onboarding może zainstalować `signal-cli` z wydań GitHub:

- Pobiera odpowiedni zasób wydania.
- Zapisuje go w `~/.openclaw/tools/signal-cli/<version>/`.
- Zapisuje `channels.signal.cliPath` do Twojej konfiguracji.

Uwagi:

- Wersje JVM wymagają **Java 21**.
- Wersje natywne są używane, gdy są dostępne.
- Windows używa WSL2; instalacja signal-cli przebiega zgodnie z przepływem Linux wewnątrz WSL.

## Co zapisuje kreator

Typowe pola w `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (jeśli wybrano MiniMax)
- `tools.profile` (lokalny onboarding domyślnie ustawia `"coding"`, gdy wartość nie jest ustawiona; istniejące jawne wartości są zachowywane)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (szczegóły zachowania: [Dokumentacja referencyjna konfiguracji CLI](/pl/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Listy dozwolonych kanałów (Slack/Discord/Matrix/Microsoft Teams), jeśli włączysz tę opcję podczas promptów (nazwy są rozwiązywane do identyfikatorów, gdy to możliwe).
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

Niektóre kanały są dostarczane jako Pluginy. Gdy wybierzesz taki kanał podczas konfiguracji, onboarding
poprosi o jego zainstalowanie (npm lub ścieżka lokalna), zanim będzie można go skonfigurować.

## Powiązana dokumentacja

- Omówienie onboardingu: [Onboarding (CLI)](/pl/start/wizard)
- Onboarding aplikacji macOS: [Onboarding](/pl/start/onboarding)
- Dokumentacja referencyjna konfiguracji: [Konfiguracja Gateway](/pl/gateway/configuration)
- Dostawcy: [WhatsApp](/pl/channels/whatsapp), [Telegram](/pl/channels/telegram), [Discord](/pl/channels/discord), [Google Chat](/pl/channels/googlechat), [Signal](/pl/channels/signal), [BlueBubbles](/pl/channels/bluebubbles) (iMessage), [iMessage](/pl/channels/imessage) (starsze)
- Skills: [Skills](/pl/tools/skills), [Konfiguracja Skills](/pl/tools/skills-config)
