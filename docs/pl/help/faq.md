---
read_when:
    - Odpowiedzi na typowe pytania dotyczące konfiguracji, instalacji, onboardingu lub obsługi środowiska uruchomieniowego
    - Wstępna analiza problemów zgłaszanych przez użytkowników przed głębszym debugowaniem
summary: Często zadawane pytania dotyczące konfiguracji, ustawień i korzystania z OpenClaw
title: FAQ
x-i18n:
    generated_at: "2026-04-12T23:28:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# FAQ

Szybkie odpowiedzi oraz dokładniejsze wskazówki diagnostyczne dla rzeczywistych konfiguracji (lokalny development, VPS, multi-agent, OAuth/klucze API, failover modeli). Informacje o diagnostyce środowiska uruchomieniowego znajdziesz w [Troubleshooting](/pl/gateway/troubleshooting). Pełne informacje o konfiguracji znajdziesz w [Configuration](/pl/gateway/configuration).

## Pierwsze 60 sekund, jeśli coś nie działa

1. **Szybki status (pierwsza kontrola)**

   ```bash
   openclaw status
   ```

   Szybkie lokalne podsumowanie: system operacyjny + aktualizacja, dostępność Gateway/usługi, agenci/sesje, konfiguracja dostawców + problemy środowiska uruchomieniowego (gdy Gateway jest osiągalny).

2. **Raport do wklejenia (bezpieczny do udostępnienia)**

   ```bash
   openclaw status --all
   ```

   Diagnoza tylko do odczytu z końcówką logów (tokeny zredagowane).

3. **Stan demona + portu**

   ```bash
   openclaw gateway status
   ```

   Pokazuje środowisko uruchomieniowe supervisora vs dostępność RPC, docelowy URL sondy oraz której konfiguracji usługa prawdopodobnie użyła.

4. **Głębokie sondy**

   ```bash
   openclaw status --deep
   ```

   Uruchamia aktywną sondę zdrowia Gateway, w tym sondy kanałów, gdy są obsługiwane
   (wymaga osiągalnego Gateway). Zobacz [Health](/pl/gateway/health).

5. **Podgląd najnowszego logu**

   ```bash
   openclaw logs --follow
   ```

   Jeśli RPC nie działa, użyj awaryjnie:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Logi plikowe są oddzielone od logów usługi; zobacz [Logging](/pl/logging) i [Troubleshooting](/pl/gateway/troubleshooting).

6. **Uruchom doctora (naprawy)**

   ```bash
   openclaw doctor
   ```

   Naprawia/migruje konfigurację i stan + uruchamia kontrole zdrowia. Zobacz [Doctor](/pl/gateway/doctor).

7. **Migawka Gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # pokazuje docelowy URL + ścieżkę konfiguracji przy błędach
   ```

   Pobiera pełną migawkę z uruchomionego Gateway (tylko WS). Zobacz [Health](/pl/gateway/health).

## Szybki start i konfiguracja przy pierwszym uruchomieniu

<AccordionGroup>
  <Accordion title="Utknąłem, jaki jest najszybszy sposób, żeby ruszyć dalej">
    Użyj lokalnego agenta AI, który potrafi **widzieć twój komputer**. To jest znacznie skuteczniejsze niż pytanie
    na Discord, ponieważ większość przypadków typu „utknąłem” to **lokalne problemy z konfiguracją lub środowiskiem**,
    których zdalne osoby pomagające nie mogą sprawdzić.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Te narzędzia potrafią czytać repozytorium, uruchamiać polecenia, sprawdzać logi i pomagać naprawić
    konfigurację na poziomie komputera (PATH, usługi, uprawnienia, pliki uwierzytelniania). Daj im **pełne checkout repozytorium**
    przez instalację hackowalną (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Instaluje to OpenClaw **z checkoutu git**, dzięki czemu agent może czytać kod i dokumentację oraz
    analizować dokładnie tę wersję, której używasz. Zawsze możesz później wrócić do wersji stabilnej,
    ponownie uruchamiając instalator bez `--install-method git`.

    Wskazówka: poproś agenta, aby **zaplanował i nadzorował** naprawę (krok po kroku), a następnie wykonał tylko
    niezbędne polecenia. Dzięki temu zmiany pozostają małe i łatwiejsze do sprawdzenia.

    Jeśli odkryjesz prawdziwy błąd lub poprawkę, zgłoś issue na GitHub albo wyślij PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Zacznij od tych poleceń (udostępnij ich wyniki, gdy prosisz o pomoc):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Co robią:

    - `openclaw status`: szybka migawka zdrowia Gateway/agenta + podstawowej konfiguracji.
    - `openclaw models status`: sprawdza uwierzytelnienie dostawcy + dostępność modeli.
    - `openclaw doctor`: sprawdza i naprawia typowe problemy z konfiguracją i stanem.

    Inne przydatne kontrole CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Szybka pętla debugowania: [First 60 seconds if something is broken](#first-60-seconds-if-something-is-broken).
    Dokumentacja instalacji: [Install](/pl/install), [Installer flags](/pl/install/installer), [Updating](/pl/install/updating).

  </Accordion>

  <Accordion title="Heartbeat jest stale pomijany. Co oznaczają powody pominięcia?">
    Typowe powody pominięcia Heartbeat:

    - `quiet-hours`: poza skonfigurowanym oknem aktywnych godzin
    - `empty-heartbeat-file`: `HEARTBEAT.md` istnieje, ale zawiera tylko pustą strukturę lub same nagłówki
    - `no-tasks-due`: tryb zadań `HEARTBEAT.md` jest aktywny, ale żaden z interwałów zadań nie jest jeszcze należny
    - `alerts-disabled`: cała widoczność Heartbeat jest wyłączona (`showOk`, `showAlerts` i `useIndicator` są wyłączone)

    W trybie zadań znaczniki czasu należności są przesuwane dopiero po zakończeniu
    rzeczywistego uruchomienia Heartbeat. Pominięte uruchomienia nie oznaczają zadań jako ukończonych.

    Dokumentacja: [Heartbeat](/pl/gateway/heartbeat), [Automation & Tasks](/pl/automation).

  </Accordion>

  <Accordion title="Zalecany sposób instalacji i konfiguracji OpenClaw">
    Repozytorium zaleca uruchamianie ze źródeł i korzystanie z onboardingu:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Kreator może również automatycznie zbudować zasoby UI. Po onboardingu zwykle uruchamiasz Gateway na porcie **18789**.

    Ze źródeł (współtwórcy/dev):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # automatycznie instaluje zależności UI przy pierwszym uruchomieniu
    openclaw onboard
    ```

    Jeśli nie masz jeszcze instalacji globalnej, uruchom to przez `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Jak otworzyć dashboard po onboardingu?">
    Kreator otwiera przeglądarkę z czystym adresem URL dashboardu (bez tokena) zaraz po onboardingu i wypisuje też link w podsumowaniu. Zachowaj tę kartę otwartą; jeśli nie uruchomiła się automatycznie, skopiuj i wklej wypisany URL na tej samej maszynie.
  </Accordion>

  <Accordion title="Jak uwierzytelnić dashboard na localhost w porównaniu ze środowiskiem zdalnym?">
    **Localhost (ta sama maszyna):**

    - Otwórz `http://127.0.0.1:18789/`.
    - Jeśli pojawi się żądanie uwierzytelnienia wspólnym sekretem, wklej skonfigurowany token lub hasło w ustawieniach Control UI.
    - Źródło tokena: `gateway.auth.token` (lub `OPENCLAW_GATEWAY_TOKEN`).
    - Źródło hasła: `gateway.auth.password` (lub `OPENCLAW_GATEWAY_PASSWORD`).
    - Jeśli wspólny sekret nie jest jeszcze skonfigurowany, wygeneruj token poleceniem `openclaw doctor --generate-gateway-token`.

    **Poza localhost:**

    - **Tailscale Serve** (zalecane): pozostaw bind loopback, uruchom `openclaw gateway --tailscale serve`, otwórz `https://<magicdns>/`. Jeśli `gateway.auth.allowTailscale` ma wartość `true`, nagłówki tożsamości spełniają wymagania uwierzytelnienia Control UI/WebSocket (bez wklejania wspólnego sekretu, przy założeniu zaufanego hosta Gateway); interfejsy HTTP API nadal wymagają uwierzytelnienia wspólnym sekretem, chyba że celowo używasz prywatnego wejścia `none` lub uwierzytelnienia HTTP zaufanego proxy.
      Błędne równoczesne próby uwierzytelnienia Serve od tego samego klienta są serializowane, zanim ogranicznik nieudanych uwierzytelnień zapisze zdarzenie, więc przy drugiej błędnej próbie może już pojawić się `retry later`.
    - **Powiązanie z tailnet**: uruchom `openclaw gateway --bind tailnet --token "<token>"` (lub skonfiguruj uwierzytelnianie hasłem), otwórz `http://<tailscale-ip>:18789/`, a następnie wklej pasujący wspólny sekret w ustawieniach dashboardu.
    - **Reverse proxy ze świadomością tożsamości**: pozostaw Gateway za zaufanym proxy niebędącym loopback, skonfiguruj `gateway.auth.mode: "trusted-proxy"`, a następnie otwórz URL proxy.
    - **Tunel SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host`, a następnie otwórz `http://127.0.0.1:18789/`. Uwierzytelnienie wspólnym sekretem nadal obowiązuje przez tunel; jeśli pojawi się monit, wklej skonfigurowany token lub hasło.

    Zobacz [Dashboard](/web/dashboard) i [Web surfaces](/web), aby poznać tryby bind i szczegóły uwierzytelniania.

  </Accordion>

  <Accordion title="Dlaczego są dwie konfiguracje zatwierdzania exec dla zatwierdzeń na czacie?">
    Sterują różnymi warstwami:

    - `approvals.exec`: przekazuje prompty zatwierdzania do miejsc docelowych na czacie
    - `channels.<channel>.execApprovals`: sprawia, że dany kanał działa jako natywny klient zatwierdzania dla zatwierdzeń exec

    Polityka exec hosta nadal jest rzeczywistą bramką zatwierdzania. Konfiguracja czatu steruje tylko tym,
    gdzie pojawiają się prompty zatwierdzania i jak ludzie mogą na nie odpowiadać.

    W większości konfiguracji **nie** potrzebujesz obu:

    - Jeśli czat już obsługuje polecenia i odpowiedzi, `/approve` w tym samym czacie działa przez wspólną ścieżkę.
    - Jeśli obsługiwany kanał natywny potrafi bezpiecznie ustalić osoby zatwierdzające, OpenClaw teraz automatycznie włącza natywne zatwierdzenia DM-first, gdy `channels.<channel>.execApprovals.enabled` jest nieustawione lub ma wartość `"auto"`.
    - Gdy dostępne są natywne karty/przyciski zatwierdzania, ta natywna warstwa UI jest ścieżką podstawową; agent powinien dołączyć ręczne polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi, że zatwierdzanie na czacie jest niedostępne albo ręczne zatwierdzenie jest jedyną ścieżką.
    - Używaj `approvals.exec` tylko wtedy, gdy prompty muszą być też przekazywane do innych czatów lub wyraźnie wskazanych pokoi operacyjnych.
    - Używaj `channels.<channel>.execApprovals.target: "channel"` lub `"both"` tylko wtedy, gdy wyraźnie chcesz publikować prompty zatwierdzania z powrotem w pokoju/temacie źródłowym.
    - Zatwierdzenia Plugin również są osobne: domyślnie używają `/approve` w tym samym czacie, opcjonalnego przekazywania `approvals.plugin`, a tylko niektóre kanały natywne utrzymują dodatkową natywną obsługę zatwierdzeń Plugin.

    Krótko: przekazywanie służy do routingu, konfiguracja klienta natywnego do bogatszego UX specyficznego dla kanału.
    Zobacz [Exec Approvals](/pl/tools/exec-approvals).

  </Accordion>

  <Accordion title="Jakiego środowiska uruchomieniowego potrzebuję?">
    Wymagany jest Node **>= 22**. Zalecane jest `pnpm`. Bun **nie jest zalecany** dla Gateway.
  </Accordion>

  <Accordion title="Czy to działa na Raspberry Pi?">
    Tak. Gateway jest lekki — dokumentacja podaje **512 MB–1 GB RAM**, **1 rdzeń** i około **500 MB**
    miejsca na dysku jako wystarczające do użytku osobistego oraz zaznacza, że **Raspberry Pi 4 może go uruchomić**.

    Jeśli chcesz większy zapas zasobów (logi, multimedia, inne usługi), **zalecane są 2 GB**, ale
    nie jest to twarde minimum.

    Wskazówka: mały Pi/VPS może hostować Gateway, a ty możesz sparować **nodes** na laptopie/telefonie do
    lokalnego ekranu/kamery/canvas lub wykonywania poleceń. Zobacz [Nodes](/pl/nodes).

  </Accordion>

  <Accordion title="Jakieś wskazówki dotyczące instalacji na Raspberry Pi?">
    Krótko: działa, ale spodziewaj się pewnych nierówności.

    - Używaj systemu **64-bitowego** i trzymaj Node >= 22.
    - Preferuj **instalację hackowalną (git)**, aby mieć wgląd w logi i szybko aktualizować.
    - Zacznij bez kanałów/Skills, a potem dodawaj je jeden po drugim.
    - Jeśli trafisz na dziwne problemy binarne, zwykle jest to problem **zgodności ARM**.

    Dokumentacja: [Linux](/pl/platforms/linux), [Install](/pl/install).

  </Accordion>

  <Accordion title="Utknęło na wake up my friend / onboarding nie chce się wykluć. Co teraz?">
    Ten ekran zależy od tego, czy Gateway jest osiągalny i uwierzytelniony. TUI wysyła też
    „Wake up, my friend!” automatycznie przy pierwszym wykluciu. Jeśli widzisz ten tekst i **brak odpowiedzi**,
    a liczba tokenów pozostaje na 0, agent nigdy się nie uruchomił.

    1. Zrestartuj Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Sprawdź status + uwierzytelnienie:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Jeśli nadal się zawiesza, uruchom:

    ```bash
    openclaw doctor
    ```

    Jeśli Gateway jest zdalny, upewnij się, że tunel/połączenie Tailscale działa oraz że UI
    wskazuje właściwy Gateway. Zobacz [Remote access](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Czy mogę przenieść konfigurację na nową maszynę (Mac mini) bez ponownego przechodzenia onboardingu?">
    Tak. Skopiuj **katalog stanu** i **workspace**, a następnie raz uruchom Doctor. Dzięki temu
    twój bot pozostanie „dokładnie taki sam” (pamięć, historia sesji, uwierzytelnienie i stan
    kanałów), o ile skopiujesz **obie** lokalizacje:

    1. Zainstaluj OpenClaw na nowej maszynie.
    2. Skopiuj `$OPENCLAW_STATE_DIR` (domyślnie: `~/.openclaw`) ze starej maszyny.
    3. Skopiuj swój workspace (domyślnie: `~/.openclaw/workspace`).
    4. Uruchom `openclaw doctor` i zrestartuj usługę Gateway.

    To zachowuje konfigurację, profile uwierzytelniania, dane logowania WhatsApp, sesje i pamięć. Jeśli działasz
    w trybie zdalnym, pamiętaj, że host Gateway jest właścicielem magazynu sesji i workspace.

    **Ważne:** jeśli tylko commitujesz/wypychasz swój workspace do GitHub, tworzysz kopię zapasową
    **pamięci + plików bootstrap**, ale **nie** historii sesji ani uwierzytelnienia. Te znajdują się
    w `~/.openclaw/` (na przykład `~/.openclaw/agents/<agentId>/sessions/`).

    Powiązane: [Migrating](/pl/install/migrating), [Where things live on disk](#where-things-live-on-disk),
    [Agent workspace](/pl/concepts/agent-workspace), [Doctor](/pl/gateway/doctor),
    [Remote mode](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Gdzie mogę zobaczyć, co nowego jest w najnowszej wersji?">
    Sprawdź changelog na GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Najnowsze wpisy są na górze. Jeśli górna sekcja jest oznaczona jako **Unreleased**, następna sekcja
    z datą to najnowsza wydana wersja. Wpisy są pogrupowane według **Highlights**, **Changes** i
    **Fixes** (plus sekcje dokumentacji/inne, gdy są potrzebne).

  </Accordion>

  <Accordion title="Nie można uzyskać dostępu do docs.openclaw.ai (błąd SSL)">
    Niektóre połączenia Comcast/Xfinity błędnie blokują `docs.openclaw.ai` przez Xfinity
    Advanced Security. Wyłącz tę funkcję albo dodaj `docs.openclaw.ai` do listy dozwolonych, a następnie spróbuj ponownie.
    Pomóż nam to odblokować, zgłaszając problem tutaj: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Jeśli nadal nie możesz uzyskać dostępu do strony, dokumentacja jest też dostępna na GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Różnica między stable a beta">
    **Stable** i **beta** to **tagi dystybucyjne npm**, a nie oddzielne linie kodu:

    - `latest` = stable
    - `beta` = wczesna kompilacja do testów

    Zwykle wydanie stable trafia najpierw na **beta**, a potem jawny
    krok promocji przenosi tę samą wersję do `latest`. Maintainerzy mogą też
    publikować bezpośrednio do `latest`, gdy jest to potrzebne. Dlatego beta i stable mogą
    wskazywać na **tę samą wersję** po promocji.

    Zobacz, co się zmieniło:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Informacje o jednolinijkowych poleceniach instalacji i różnicy między beta a dev znajdziesz w akordeonie poniżej.

  </Accordion>

  <Accordion title="Jak zainstalować wersję beta i jaka jest różnica między beta a dev?">
    **Beta** to tag dystrybucyjny npm `beta` (po promocji może odpowiadać `latest`).
    **Dev** to ruchomy HEAD gałęzi `main` (git); po publikacji używa tagu dystrybucyjnego npm `dev`.

    Jednolinijkowe polecenia (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Instalator Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Więcej szczegółów: [Development channels](/pl/install/development-channels) i [Installer flags](/pl/install/installer).

  </Accordion>

  <Accordion title="Jak wypróbować najnowsze elementy?">
    Masz dwie opcje:

    1. **Kanał dev (checkout git):**

    ```bash
    openclaw update --channel dev
    ```

    To przełącza na gałąź `main` i aktualizuje ze źródeł.

    2. **Instalacja hackowalna (ze strony instalatora):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Daje to lokalne repozytorium, które możesz edytować, a następnie aktualizować przez git.

    Jeśli wolisz ręcznie wykonać czysty klon, użyj:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Dokumentacja: [Update](/cli/update), [Development channels](/pl/install/development-channels),
    [Install](/pl/install).

  </Accordion>

  <Accordion title="Jak długo zwykle trwa instalacja i onboarding?">
    Orientacyjnie:

    - **Instalacja:** 2–5 minut
    - **Onboarding:** 5–15 minut w zależności od liczby skonfigurowanych kanałów/modeli

    Jeśli proces się zawiesza, skorzystaj z [Installer stuck](#quick-start-and-first-run-setup)
    i szybkiej pętli debugowania w [I am stuck](#quick-start-and-first-run-setup).

  </Accordion>

  <Accordion title="Instalator się zawiesza? Jak uzyskać więcej informacji zwrotnych?">
    Uruchom instalator ponownie z **szczegółowym wyjściem**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Instalacja beta z trybem verbose:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Dla instalacji hackowalnej (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Odpowiednik dla Windows (PowerShell):

    ```powershell
    # install.ps1 nie ma jeszcze dedykowanej flagi -Verbose.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Więcej opcji: [Installer flags](/pl/install/installer).

  </Accordion>

  <Accordion title="Instalacja w Windows zgłasza git not found lub openclaw not recognized">
    Dwa częste problemy w Windows:

    **1) błąd npm spawn git / git not found**

    - Zainstaluj **Git for Windows** i upewnij się, że `git` jest w PATH.
    - Zamknij i ponownie otwórz PowerShell, a następnie uruchom instalator ponownie.

    **2) openclaw is not recognized po instalacji**

    - Twój globalny folder bin npm nie znajduje się w PATH.
    - Sprawdź ścieżkę:

      ```powershell
      npm config get prefix
      ```

    - Dodaj ten katalog do użytkownikowego PATH (w Windows nie trzeba dopisywać sufiksu `\bin`; na większości systemów jest to `%AppData%\npm`).
    - Zamknij i ponownie otwórz PowerShell po zaktualizowaniu PATH.

    Jeśli chcesz uzyskać możliwie najpłynniejszą konfigurację w Windows, używaj **WSL2** zamiast natywnego Windows.
    Dokumentacja: [Windows](/pl/platforms/windows).

  </Accordion>

  <Accordion title="Wyjście exec w Windows pokazuje zniekształcony chiński tekst — co zrobić?">
    Zwykle jest to problem niedopasowania strony kodowej konsoli w natywnych powłokach Windows.

    Objawy:

    - Wyjście `system.run`/`exec` renderuje chiński tekst jako mojibake
    - To samo polecenie wygląda poprawnie w innym profilu terminala

    Szybkie obejście w PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Następnie zrestartuj Gateway i spróbuj ponownie wykonać polecenie:

    ```powershell
    openclaw gateway restart
    ```

    Jeśli nadal możesz odtworzyć ten problem w najnowszym OpenClaw, śledź/zgłoś go tutaj:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Dokumentacja nie odpowiedziała na moje pytanie — jak uzyskać lepszą odpowiedź?">
    Użyj **instalacji hackowalnej (git)**, aby mieć lokalnie pełne źródła i dokumentację, a potem zapytaj
    swojego bota (lub Claude/Codex) _z tego folderu_, aby mógł czytać repozytorium i odpowiedzieć precyzyjnie.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Więcej szczegółów: [Install](/pl/install) i [Installer flags](/pl/install/installer).

  </Accordion>

  <Accordion title="Jak zainstalować OpenClaw na Linux?">
    Krótka odpowiedź: postępuj zgodnie z przewodnikiem dla Linux, a następnie uruchom onboarding.

    - Szybka ścieżka dla Linux + instalacja usługi: [Linux](/pl/platforms/linux).
    - Pełny przewodnik: [Getting Started](/pl/start/getting-started).
    - Instalator + aktualizacje: [Install & updates](/pl/install/updating).

  </Accordion>

  <Accordion title="Jak zainstalować OpenClaw na VPS?">
    Dowolny VPS z Linux będzie odpowiedni. Zainstaluj na serwerze, a następnie użyj SSH/Tailscale, aby uzyskać dostęp do Gateway.

    Przewodniki: [exe.dev](/pl/install/exe-dev), [Hetzner](/pl/install/hetzner), [Fly.io](/pl/install/fly).
    Dostęp zdalny: [Gateway remote](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Gdzie są przewodniki instalacji w chmurze/VPS?">
    Mamy **hub hostingowy** z najczęstszymi dostawcami. Wybierz jednego i postępuj zgodnie z przewodnikiem:

    - [VPS hosting](/pl/vps) (wszyscy dostawcy w jednym miejscu)
    - [Fly.io](/pl/install/fly)
    - [Hetzner](/pl/install/hetzner)
    - [exe.dev](/pl/install/exe-dev)

    Jak to działa w chmurze: **Gateway działa na serwerze**, a ty uzyskujesz do niego dostęp
    z laptopa/telefonu przez Control UI (lub Tailscale/SSH). Twój stan + workspace
    znajdują się na serwerze, więc traktuj host jako źródło prawdy i twórz jego kopie zapasowe.

    Możesz sparować **nodes** (Mac/iOS/Android/headless) z tym chmurowym Gateway, aby uzyskać dostęp
    do lokalnego ekranu/kamery/canvas lub uruchamiać polecenia na laptopie, zachowując
    Gateway w chmurze.

    Hub: [Platforms](/pl/platforms). Dostęp zdalny: [Gateway remote](/pl/gateway/remote).
    Nodes: [Nodes](/pl/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Czy mogę poprosić OpenClaw, aby sam się zaktualizował?">
    Krótka odpowiedź: **to możliwe, ale niezalecane**. Proces aktualizacji może zrestartować
    Gateway (co przerywa aktywną sesję), może wymagać czystego checkoutu git i
    może poprosić o potwierdzenie. Bezpieczniej: uruchamiać aktualizacje z powłoki jako operator.

    Użyj CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Jeśli musisz zautomatyzować to z poziomu agenta:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Dokumentacja: [Update](/cli/update), [Updating](/pl/install/updating).

  </Accordion>

  <Accordion title="Co właściwie robi onboarding?">
    `openclaw onboard` to zalecana ścieżka konfiguracji. W **trybie lokalnym** prowadzi cię przez:

    - **Konfigurację modeli/uwierzytelniania** (OAuth dostawcy, klucze API, setup-token Anthropic oraz opcje modeli lokalnych, takie jak LM Studio)
    - Lokalizację **workspace** + pliki bootstrap
    - **Ustawienia Gateway** (bind/port/auth/tailscale)
    - **Kanały** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage oraz dołączone pluginy kanałów, takie jak QQ Bot)
    - **Instalację demona** (LaunchAgent w macOS; jednostka użytkownika systemd w Linux/WSL2)
    - **Kontrole zdrowia** i wybór **Skills**

    Ostrzega też, jeśli skonfigurowany model jest nieznany lub brakuje uwierzytelnienia.

  </Accordion>

  <Accordion title="Czy potrzebuję subskrypcji Claude lub OpenAI, aby to uruchomić?">
    Nie. Możesz uruchamiać OpenClaw za pomocą **kluczy API** (Anthropic/OpenAI/inne) albo
    **wyłącznie modeli lokalnych**, aby dane pozostawały na twoim urządzeniu. Subskrypcje (Claude
    Pro/Max lub OpenAI Codex) to opcjonalne sposoby uwierzytelniania tych dostawców.

    W przypadku Anthropic w OpenClaw praktyczny podział wygląda tak:

    - **Klucz API Anthropic**: zwykłe rozliczanie API Anthropic
    - **Claude CLI / uwierzytelnianie subskrypcją Claude w OpenClaw**: pracownicy Anthropic
      powiedzieli nam, że to użycie jest znowu dozwolone, a OpenClaw traktuje użycie `claude -p`
      jako autoryzowane dla tej integracji, chyba że Anthropic opublikuje nową
      politykę

    Dla hostów Gateway działających długoterminowo klucze API Anthropic nadal są bardziej
    przewidywalną konfiguracją. OpenAI Codex OAuth jest jawnie obsługiwane dla zewnętrznych
    narzędzi takich jak OpenClaw.

    OpenClaw obsługuje też inne hostowane opcje w stylu subskrypcyjnym, w tym
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** oraz
    **Z.AI / GLM Coding Plan**.

    Dokumentacja: [Anthropic](/pl/providers/anthropic), [OpenAI](/pl/providers/openai),
    [Qwen Cloud](/pl/providers/qwen),
    [MiniMax](/pl/providers/minimax), [GLM Models](/pl/providers/glm),
    [Local models](/pl/gateway/local-models), [Models](/pl/concepts/models).

  </Accordion>

  <Accordion title="Czy mogę używać subskrypcji Claude Max bez klucza API?">
    Tak.

    Pracownicy Anthropic powiedzieli nam, że użycie Claude CLI w stylu OpenClaw jest znowu dozwolone, więc
    OpenClaw traktuje uwierzytelnianie subskrypcją Claude i użycie `claude -p` jako autoryzowane
    dla tej integracji, chyba że Anthropic opublikuje nową politykę. Jeśli chcesz
    najbardziej przewidywalnej konfiguracji po stronie serwera, użyj zamiast tego klucza API Anthropic.

  </Accordion>

  <Accordion title="Czy obsługujecie uwierzytelnianie subskrypcją Claude (Claude Pro lub Max)?">
    Tak.

    Pracownicy Anthropic powiedzieli nam, że to użycie jest znowu dozwolone, więc OpenClaw traktuje
    ponowne użycie Claude CLI i użycie `claude -p` jako autoryzowane dla tej integracji,
    chyba że Anthropic opublikuje nową politykę.

    Setup-token Anthropic jest nadal dostępny jako obsługiwana ścieżka tokenu OpenClaw, ale OpenClaw teraz preferuje ponowne użycie Claude CLI i `claude -p`, gdy są dostępne.
    Dla środowisk produkcyjnych lub obciążeń wieloużytkownikowych uwierzytelnianie kluczem API Anthropic jest nadal
    bezpieczniejszym i bardziej przewidywalnym wyborem. Jeśli chcesz innych hostowanych
    opcji w stylu subskrypcyjnym w OpenClaw, zobacz [OpenAI](/pl/providers/openai), [Qwen / Model
    Cloud](/pl/providers/qwen), [MiniMax](/pl/providers/minimax) oraz [GLM
    Models](/pl/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Dlaczego widzę HTTP 429 rate_limit_error z Anthropic?">
To oznacza, że twój **limit/rate limit Anthropic** został wyczerpany w bieżącym oknie. Jeśli
używasz **Claude CLI**, poczekaj na reset okna albo przejdź na wyższy plan. Jeśli
używasz **klucza API Anthropic**, sprawdź Anthropic Console
pod kątem użycia/rozliczeń i w razie potrzeby zwiększ limity.

    Jeśli komunikat brzmi dokładnie:
    `Extra usage is required for long context requests`, żądanie próbuje użyć
    bety kontekstu 1M Anthropic (`context1m: true`). To działa tylko wtedy, gdy twoje
    poświadczenie kwalifikuje się do rozliczania długiego kontekstu (rozliczanie kluczem API lub
    ścieżka logowania Claude w OpenClaw z włączonym Extra Usage).

    Wskazówka: ustaw **model zapasowy**, aby OpenClaw mógł nadal odpowiadać, gdy dostawca jest ograniczany przez rate limit.
    Zobacz [Models](/cli/models), [OAuth](/pl/concepts/oauth) oraz
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/pl/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="Czy AWS Bedrock jest obsługiwany?">
    Tak. OpenClaw ma dołączonego dostawcę **Amazon Bedrock (Converse)**. Gdy obecne są znaczniki środowiska AWS, OpenClaw może automatycznie wykryć katalog Bedrock dla streamingu/tekstu i scalić go jako niejawnego dostawcę `amazon-bedrock`; w przeciwnym razie możesz jawnie włączyć `plugins.entries.amazon-bedrock.config.discovery.enabled` lub dodać ręczny wpis dostawcy. Zobacz [Amazon Bedrock](/pl/providers/bedrock) i [Model providers](/pl/providers/models). Jeśli wolisz zarządzany przepływ kluczy, proxy zgodne z OpenAI przed Bedrock nadal jest prawidłową opcją.
  </Accordion>

  <Accordion title="Jak działa uwierzytelnianie Codex?">
    OpenClaw obsługuje **OpenAI Code (Codex)** przez OAuth (logowanie ChatGPT). Onboarding może uruchomić przepływ OAuth i w odpowiednich przypadkach ustawi domyślny model na `openai-codex/gpt-5.4`. Zobacz [Model providers](/pl/concepts/model-providers) i [Onboarding (CLI)](/pl/start/wizard).
  </Accordion>

  <Accordion title="Dlaczego ChatGPT GPT-5.4 nie odblokowuje openai/gpt-5.4 w OpenClaw?">
    OpenClaw traktuje te dwie ścieżki oddzielnie:

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = bezpośrednie API OpenAI Platform

    W OpenClaw logowanie ChatGPT/Codex jest podłączone do ścieżki `openai-codex/*`,
    a nie do bezpośredniej ścieżki `openai/*`. Jeśli chcesz używać bezpośredniej ścieżki API w
    OpenClaw, ustaw `OPENAI_API_KEY` (lub równoważną konfigurację dostawcy OpenAI).
    Jeśli chcesz używać logowania ChatGPT/Codex w OpenClaw, użyj `openai-codex/*`.

  </Accordion>

  <Accordion title="Dlaczego limity OAuth Codex mogą różnić się od limitów w ChatGPT web?">
    `openai-codex/*` używa ścieżki OAuth Codex, a jego dostępne okna limitów są
    zarządzane przez OpenAI i zależą od planu. W praktyce limity te mogą różnić się od
    doświadczenia na stronie/aplikacji ChatGPT, nawet gdy oba są powiązane z tym samym kontem.

    OpenClaw może pokazać obecnie widoczne okna użycia/limitów dostawcy w
    `openclaw models status`, ale nie tworzy ani nie normalizuje uprawnień ChatGPT-web
    do bezpośredniego dostępu API. Jeśli chcesz używać bezpośredniej ścieżki rozliczeń/limitów OpenAI Platform,
    użyj `openai/*` z kluczem API.

  </Accordion>

  <Accordion title="Czy obsługujecie uwierzytelnianie subskrypcją OpenAI (Codex OAuth)?">
    Tak. OpenClaw w pełni obsługuje **subskrypcyjny OAuth OpenAI Code (Codex)**.
    OpenAI jednoznacznie zezwala na użycie subskrypcyjnego OAuth w zewnętrznych narzędziach/przepływach
    takich jak OpenClaw. Onboarding może uruchomić ten przepływ OAuth za ciebie.

    Zobacz [OAuth](/pl/concepts/oauth), [Model providers](/pl/concepts/model-providers) i [Onboarding (CLI)](/pl/start/wizard).

  </Accordion>

  <Accordion title="Jak skonfigurować Gemini CLI OAuth?">
    Gemini CLI używa **przepływu uwierzytelniania Plugin**, a nie client id ani secret w `openclaw.json`.

    Kroki:

    1. Zainstaluj lokalnie Gemini CLI, aby `gemini` było dostępne w `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Włącz Plugin: `openclaw plugins enable google`
    3. Zaloguj się: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Domyślny model po zalogowaniu: `google-gemini-cli/gemini-3-flash-preview`
    5. Jeśli żądania kończą się błędem, ustaw `GOOGLE_CLOUD_PROJECT` lub `GOOGLE_CLOUD_PROJECT_ID` na hoście Gateway

    To zapisuje tokeny OAuth w profilach uwierzytelniania na hoście Gateway. Szczegóły: [Model providers](/pl/concepts/model-providers).

  </Accordion>

  <Accordion title="Czy model lokalny nadaje się do swobodnych rozmów?">
    Zwykle nie. OpenClaw potrzebuje dużego kontekstu i silnych zabezpieczeń; małe karty obcinają kontekst i przeciekają. Jeśli musisz, uruchom lokalnie **największy** build modelu, jaki możesz (LM Studio), i zobacz [/gateway/local-models](/pl/gateway/local-models). Mniejsze/kwantyzowane modele zwiększają ryzyko prompt injection — zobacz [Security](/pl/gateway/security).
  </Accordion>

  <Accordion title="Jak utrzymać ruch do modeli hostowanych w określonym regionie?">
    Wybierz endpointy przypisane do regionu. OpenRouter udostępnia opcje hostowane w USA dla MiniMax, Kimi i GLM; wybierz wariant hostowany w USA, aby utrzymać dane w regionie. Nadal możesz wymieniać obok nich Anthropic/OpenAI, używając `models.mode: "merge"`, aby modele zapasowe pozostały dostępne przy jednoczesnym zachowaniu wybranego dostawcy regionalnego.
  </Accordion>

  <Accordion title="Czy muszę kupić Mac Mini, aby to zainstalować?">
    Nie. OpenClaw działa na macOS lub Linux (Windows przez WSL2). Mac mini jest opcjonalny — niektórzy
    kupują go jako host działający cały czas, ale mały VPS, serwer domowy lub urządzenie klasy Raspberry Pi też się nada.

    Potrzebujesz Mac **tylko do narzędzi dostępnych wyłącznie w macOS**. Dla iMessage użyj [BlueBubbles](/pl/channels/bluebubbles) (zalecane) — serwer BlueBubbles działa na dowolnym Mac, a Gateway może działać na Linux lub gdzie indziej. Jeśli chcesz korzystać z innych narzędzi tylko dla macOS, uruchom Gateway na Mac albo sparuj Node macOS.

    Dokumentacja: [BlueBubbles](/pl/channels/bluebubbles), [Nodes](/pl/nodes), [Mac remote mode](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Czy potrzebuję Mac mini do obsługi iMessage?">
    Potrzebujesz **jakiegoś urządzenia macOS** zalogowanego do Wiadomości. To **nie** musi być Mac mini —
    wystarczy dowolny Mac. Dla iMessage **użyj [BlueBubbles](/pl/channels/bluebubbles)** (zalecane) — serwer BlueBubbles działa na macOS, a Gateway może działać na Linux lub gdzie indziej.

    Typowe konfiguracje:

    - Uruchom Gateway na Linux/VPS, a serwer BlueBubbles na dowolnym Mac zalogowanym do Wiadomości.
    - Uruchom wszystko na Mac, jeśli chcesz najprostszą konfigurację na jednej maszynie.

    Dokumentacja: [BlueBubbles](/pl/channels/bluebubbles), [Nodes](/pl/nodes),
    [Mac remote mode](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Jeśli kupię Mac mini do uruchamiania OpenClaw, czy mogę połączyć go z moim MacBook Pro?">
    Tak. **Mac mini może uruchamiać Gateway**, a twój MacBook Pro może połączyć się jako
    **Node** (urządzenie towarzyszące). Nodes nie uruchamiają Gateway — zapewniają dodatkowe
    możliwości, takie jak ekran/kamera/canvas oraz `system.run` na tym urządzeniu.

    Typowy wzorzec:

    - Gateway na Mac mini (zawsze włączony).
    - MacBook Pro uruchamia aplikację macOS albo hosta Node i paruje się z Gateway.
    - Użyj `openclaw nodes status` / `openclaw nodes list`, aby to zobaczyć.

    Dokumentacja: [Nodes](/pl/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Czy mogę używać Bun?">
    Bun **nie jest zalecany**. Widzimy błędy środowiska uruchomieniowego, szczególnie z WhatsApp i Telegram.
    Używaj **Node** do stabilnych Gateway.

    Jeśli mimo to chcesz eksperymentować z Bun, rób to na nieprodukcyjnym Gateway
    bez WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: co wpisuje się w allowFrom?">
    `channels.telegram.allowFrom` to **Telegram user ID człowieka-nadawcy** (liczbowy). To nie jest nazwa użytkownika bota.

    Onboarding akceptuje dane wejściowe `@username` i rozwiązuje je do liczbowego ID, ale autoryzacja OpenClaw używa wyłącznie liczbowych ID.

    Bezpieczniej (bez bota zewnętrznego):

    - Wyślij DM do swojego bota, a następnie uruchom `openclaw logs --follow` i odczytaj `from.id`.

    Oficjalne Bot API:

    - Wyślij DM do swojego bota, a następnie wywołaj `https://api.telegram.org/bot<bot_token>/getUpdates` i odczytaj `message.from.id`.

    Zewnętrzne rozwiązanie (mniej prywatne):

    - Wyślij DM do `@userinfobot` lub `@getidsbot`.

    Zobacz [/channels/telegram](/pl/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Czy wiele osób może używać jednego numeru WhatsApp z różnymi instancjami OpenClaw?">
    Tak, przez **ruting multi-agent**. Przypisz DM WhatsApp każdego nadawcy **DM** (peer `kind: "direct"`, E.164 nadawcy, np. `+15551234567`) do innego `agentId`, aby każda osoba miała własny workspace i magazyn sesji. Odpowiedzi nadal będą pochodzić z **tego samego konta WhatsApp**, a kontrola dostępu do DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) jest globalna dla całego konta WhatsApp. Zobacz [Multi-Agent Routing](/pl/concepts/multi-agent) i [WhatsApp](/pl/channels/whatsapp).
  </Accordion>

  <Accordion title='Czy mogę uruchomić agenta „fast chat” i agenta „Opus for coding”?'>
    Tak. Użyj rutingu multi-agent: przypisz każdemu agentowi własny model domyślny, a następnie powiąż trasy przychodzące (konto dostawcy lub określonych peerów) z każdym agentem. Przykładowa konfiguracja znajduje się w [Multi-Agent Routing](/pl/concepts/multi-agent). Zobacz też [Models](/pl/concepts/models) i [Configuration](/pl/gateway/configuration).
  </Accordion>

  <Accordion title="Czy Homebrew działa na Linux?">
    Tak. Homebrew obsługuje Linux (Linuxbrew). Szybka konfiguracja:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Jeśli uruchamiasz OpenClaw przez systemd, upewnij się, że PATH usługi zawiera `/home/linuxbrew/.linuxbrew/bin` (lub twój prefiks brew), aby narzędzia zainstalowane przez `brew` były rozpoznawane w powłokach niebędących powłokami logowania.
    Nowsze buildy dodają też na początku typowe katalogi bin użytkownika w usługach Linux systemd (na przykład `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) i honorują `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` oraz `FNM_DIR`, gdy są ustawione.

  </Accordion>

  <Accordion title="Różnica między hackowalną instalacją git a npm install">
    - **Hackowalna instalacja (git):** pełny checkout źródeł, możliwość edycji, najlepsza dla współtwórców.
      Budujesz lokalnie i możesz poprawiać kod/dokumentację.
    - **npm install:** globalna instalacja CLI, bez repozytorium, najlepsza do „po prostu uruchom”.
      Aktualizacje pochodzą z tagów dystrybucyjnych npm.

    Dokumentacja: [Getting started](/pl/start/getting-started), [Updating](/pl/install/updating).

  </Accordion>

  <Accordion title="Czy mogę później przełączać się między instalacją npm a git?">
    Tak. Zainstaluj drugi wariant, a następnie uruchom Doctor, aby usługa Gateway wskazywała na nowy entrypoint.
    To **nie usuwa twoich danych** — zmienia tylko instalację kodu OpenClaw. Twój stan
    (`~/.openclaw`) i workspace (`~/.openclaw/workspace`) pozostają nienaruszone.

    Z npm na git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    Z git na npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor wykrywa niedopasowanie entrypointu usługi Gateway i proponuje przepisanie konfiguracji usługi tak, aby odpowiadała bieżącej instalacji (w automatyzacji użyj `--repair`).

    Wskazówki dotyczące kopii zapasowych: zobacz [Backup strategy](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="Czy powinienem uruchamiać Gateway na laptopie czy na VPS?">
    Krótka odpowiedź: **jeśli chcesz niezawodności 24/7, użyj VPS**. Jeśli chcesz
    najmniejszych utrudnień i nie przeszkadzają ci uśpienia/restarty, uruchamiaj lokalnie.

    **Laptop (lokalny Gateway)**

    - **Zalety:** brak kosztów serwera, bezpośredni dostęp do plików lokalnych, widoczne okno przeglądarki.
    - **Wady:** uśpienie/utrata sieci = rozłączenia, aktualizacje/restarty systemu operacyjnego przerywają pracę, komputer musi pozostać aktywny.

    **VPS / chmura**

    - **Zalety:** działa cały czas, stabilna sieć, brak problemów z uśpieniem laptopa, łatwiej utrzymać działanie.
    - **Wady:** często działa bez interfejsu (używaj zrzutów ekranu), tylko zdalny dostęp do plików, do aktualizacji trzeba używać SSH.

    **Uwaga specyficzna dla OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord działają dobrze na VPS. Jedyny realny kompromis to **przeglądarka bez interfejsu** vs widoczne okno. Zobacz [Browser](/pl/tools/browser).

    **Zalecane ustawienie domyślne:** VPS, jeśli wcześniej zdarzały ci się rozłączenia Gateway. Tryb lokalny jest świetny, gdy aktywnie używasz Mac i chcesz mieć dostęp do plików lokalnych lub automatyzację UI z widoczną przeglądarką.

  </Accordion>

  <Accordion title="Jak ważne jest uruchamianie OpenClaw na dedykowanej maszynie?">
    Nie jest to wymagane, ale **zalecane dla niezawodności i izolacji**.

    - **Dedykowany host (VPS/Mac mini/Pi):** działa cały czas, mniej przerw z powodu uśpienia/restartów, czystsze uprawnienia, łatwiej utrzymać działanie.
    - **Współdzielony laptop/desktop:** całkowicie wystarczający do testów i aktywnego używania, ale spodziewaj się przerw, gdy maszyna przechodzi w stan uśpienia lub się aktualizuje.

    Jeśli chcesz połączyć zalety obu podejść, utrzymuj Gateway na dedykowanym hoście i sparuj laptop jako **Node** dla lokalnych narzędzi ekranu/kamery/exec. Zobacz [Nodes](/pl/nodes).
    Wskazówki dotyczące bezpieczeństwa znajdziesz w [Security](/pl/gateway/security).

  </Accordion>

  <Accordion title="Jakie są minimalne wymagania VPS i zalecany system operacyjny?">
    OpenClaw jest lekki. Dla podstawowego Gateway + jednego kanału czatu:

    - **Absolutne minimum:** 1 vCPU, 1 GB RAM, około 500 MB dysku.
    - **Zalecane:** 1–2 vCPU, 2 GB RAM lub więcej dla zapasu (logi, multimedia, wiele kanałów). Narzędzia Node i automatyzacja przeglądarki mogą wymagać sporo zasobów.

    System operacyjny: używaj **Ubuntu LTS** (lub dowolnego nowoczesnego Debian/Ubuntu). Ścieżka instalacji Linux jest tam najlepiej przetestowana.

    Dokumentacja: [Linux](/pl/platforms/linux), [VPS hosting](/pl/vps).

  </Accordion>

  <Accordion title="Czy mogę uruchamiać OpenClaw w VM i jakie są wymagania?">
    Tak. Traktuj VM tak samo jak VPS: musi być zawsze włączona, osiągalna i mieć wystarczająco
    dużo RAM dla Gateway oraz wszystkich włączonych kanałów.

    Podstawowe wytyczne:

    - **Absolutne minimum:** 1 vCPU, 1 GB RAM.
    - **Zalecane:** 2 GB RAM lub więcej, jeśli uruchamiasz wiele kanałów, automatyzację przeglądarki lub narzędzia multimedialne.
    - **System operacyjny:** Ubuntu LTS lub inny nowoczesny Debian/Ubuntu.

    Jeśli używasz Windows, **WSL2 to najłatwiejsza konfiguracja w stylu VM** i oferuje najlepszą
    zgodność narzędzi. Zobacz [Windows](/pl/platforms/windows), [VPS hosting](/pl/vps).
    Jeśli uruchamiasz macOS w VM, zobacz [macOS VM](/pl/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Czym jest OpenClaw?

<AccordionGroup>
  <Accordion title="Czym jest OpenClaw w jednym akapicie?">
    OpenClaw to osobisty asystent AI, którego uruchamiasz na własnych urządzeniach. Odpowiada na używanych już przez ciebie powierzchniach komunikacyjnych (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat oraz dołączone pluginy kanałów, takie jak QQ Bot), a na obsługiwanych platformach może też oferować głos + aktywny Canvas. **Gateway** jest stale działającą płaszczyzną sterowania; asystent jest produktem.
  </Accordion>

  <Accordion title="Propozycja wartości">
    OpenClaw nie jest „tylko wrapperem do Claude”. To **lokalna w pierwszej kolejności płaszczyzna sterowania**, która pozwala uruchamiać
    wydajnego asystenta na **własnym sprzęcie**, dostępnego z aplikacji czatu, których już używasz,
    ze stanowymi sesjami, pamięcią i narzędziami — bez oddawania kontroli nad swoimi przepływami pracy hostowanemu
    SaaS.

    Najważniejsze elementy:

    - **Twoje urządzenia, twoje dane:** uruchamiaj Gateway tam, gdzie chcesz (Mac, Linux, VPS), i przechowuj
      workspace + historię sesji lokalnie.
    - **Prawdziwe kanały, a nie web sandbox:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage itp.,
      a do tego głos mobilny i Canvas na obsługiwanych platformach.
    - **Niezależność od modelu:** używaj Anthropic, OpenAI, MiniMax, OpenRouter itd. z rutingiem
      per agent i failover.
    - **Opcja wyłącznie lokalna:** uruchamiaj modele lokalne, aby **wszystkie dane mogły pozostać na twoim urządzeniu**, jeśli chcesz.
    - **Ruting multi-agent:** oddzielni agenci dla kanału, konta lub zadania, każdy z własnym
      workspace i ustawieniami domyślnymi.
    - **Open source i możliwość modyfikacji:** sprawdzaj, rozszerzaj i hostuj samodzielnie bez uzależnienia od dostawcy.

    Dokumentacja: [Gateway](/pl/gateway), [Channels](/pl/channels), [Multi-agent](/pl/concepts/multi-agent),
    [Memory](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Dopiero to skonfigurowałem — co powinienem zrobić najpierw?">
    Dobre pierwsze projekty:

    - Zbuduj stronę internetową (WordPress, Shopify albo prostą stronę statyczną).
    - Stwórz prototyp aplikacji mobilnej (zarys, ekrany, plan API).
    - Zorganizuj pliki i foldery (porządkowanie, nazewnictwo, tagowanie).
    - Połącz Gmail i zautomatyzuj podsumowania lub działania następcze.

    Potrafi obsługiwać duże zadania, ale działa najlepiej, gdy podzielisz je na etapy i
    użyjesz sub-agentów do pracy równoległej.

  </Accordion>

  <Accordion title="Jakie jest pięć najważniejszych codziennych zastosowań OpenClaw?">
    Codzienne korzyści zwykle wyglądają tak:

    - **Osobiste briefingi:** podsumowania skrzynki odbiorczej, kalendarza i interesujących cię wiadomości.
    - **Research i tworzenie szkiców:** szybki research, podsumowania i pierwsze wersje e-maili lub dokumentów.
    - **Przypomnienia i działania następcze:** bodźce i checklisty sterowane przez Cron lub Heartbeat.
    - **Automatyzacja przeglądarki:** wypełnianie formularzy, zbieranie danych i powtarzalne zadania webowe.
    - **Koordynacja między urządzeniami:** wyślij zadanie z telefonu, pozwól Gateway uruchomić je na serwerze i otrzymaj wynik z powrotem na czacie.

  </Accordion>

  <Accordion title="Czy OpenClaw może pomóc w lead gen, outreach, reklamach i blogach dla SaaS?">
    Tak, w zakresie **researchu, kwalifikacji i tworzenia szkiców**. Może skanować strony, budować shortlisty,
    podsumowywać potencjalnych klientów i pisać szkice wiadomości outreachowych lub tekstów reklam.

    W przypadku **outreachu lub uruchamiania reklam** pozostaw człowieka w pętli. Unikaj spamu, przestrzegaj lokalnego prawa i
    zasad platform oraz sprawdzaj wszystko przed wysłaniem. Najbezpieczniejszy wzorzec to taki, w którym
    OpenClaw przygotowuje szkic, a ty go zatwierdzasz.

    Dokumentacja: [Security](/pl/gateway/security).

  </Accordion>

  <Accordion title="Jakie są zalety względem Claude Code przy tworzeniu stron internetowych?">
    OpenClaw to **osobisty asystent** i warstwa koordynacji, a nie zamiennik IDE. Używaj
    Claude Code lub Codex dla najszybszej bezpośredniej pętli kodowania w repozytorium. Używaj OpenClaw, gdy
    chcesz trwałej pamięci, dostępu między urządzeniami i orkiestracji narzędzi.

    Zalety:

    - **Trwała pamięć + workspace** między sesjami
    - **Dostęp wieloplatformowy** (WhatsApp, Telegram, TUI, WebChat)
    - **Orkiestracja narzędzi** (przeglądarka, pliki, harmonogramowanie, hooki)
    - **Stale działający Gateway** (uruchom na VPS, korzystaj z dowolnego miejsca)
    - **Nodes** dla lokalnej przeglądarki/ekranu/kamery/exec

    Prezentacja: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills i automatyzacja

<AccordionGroup>
  <Accordion title="Jak dostosować Skills bez utrzymywania brudnego repozytorium?">
    Używaj zarządzanych nadpisań zamiast edytować kopię w repozytorium. Umieść zmiany w `~/.openclaw/skills/<name>/SKILL.md` (lub dodaj folder przez `skills.load.extraDirs` w `~/.openclaw/openclaw.json`). Priorytet to `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → dołączone → `skills.load.extraDirs`, więc zarządzane nadpisania nadal mają pierwszeństwo przed dołączonymi Skills bez dotykania gita. Jeśli Skill ma być zainstalowany globalnie, ale widoczny tylko dla niektórych agentów, trzymaj wspólną kopię w `~/.openclaw/skills` i kontroluj widoczność przez `agents.defaults.skills` oraz `agents.list[].skills`. Tylko zmiany warte upstreamu powinny trafiać do repozytorium i wychodzić jako PR.
  </Accordion>

  <Accordion title="Czy mogę ładować Skills z własnego folderu?">
    Tak. Dodaj dodatkowe katalogi przez `skills.load.extraDirs` w `~/.openclaw/openclaw.json` (najniższy priorytet). Domyślny priorytet to `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → dołączone → `skills.load.extraDirs`. `clawhub` instaluje domyślnie do `./skills`, co OpenClaw traktuje jako `<workspace>/skills` przy następnej sesji. Jeśli Skill ma być widoczny tylko dla określonych agentów, połącz to z `agents.defaults.skills` lub `agents.list[].skills`.
  </Accordion>

  <Accordion title="Jak mogę używać różnych modeli do różnych zadań?">
    Obecnie obsługiwane wzorce to:

    - **Zadania Cron**: odizolowane zadania mogą ustawiać nadpisanie `model` dla każdego zadania.
    - **Sub-agenci**: kieruj zadania do oddzielnych agentów z różnymi modelami domyślnymi.
    - **Przełączanie na żądanie**: użyj `/model`, aby w dowolnym momencie przełączyć model bieżącej sesji.

    Zobacz [Cron jobs](/pl/automation/cron-jobs), [Multi-Agent Routing](/pl/concepts/multi-agent) i [Slash commands](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot zawiesza się podczas ciężkiej pracy. Jak to odciążyć?">
    Używaj **sub-agentów** do długich lub równoległych zadań. Sub-agenci działają we własnej sesji,
    zwracają podsumowanie i utrzymują responsywność głównego czatu.

    Poproś bota, aby „uruchomił sub-agenta dla tego zadania”, albo użyj `/subagents`.
    Użyj `/status` na czacie, aby zobaczyć, co Gateway robi w tej chwili (i czy jest zajęty).

    Wskazówka dotycząca tokenów: długie zadania i sub-agenci oba zużywają tokeny. Jeśli koszt ma znaczenie, ustaw
    tańszy model dla sub-agentów przez `agents.defaults.subagents.model`.

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Background Tasks](/pl/automation/tasks).

  </Accordion>

  <Accordion title="Jak działają sesje sub-agentów powiązane z wątkiem na Discord?">
    Używaj powiązań wątków. Możesz powiązać wątek Discord z sub-agentem lub celem sesji, aby kolejne wiadomości w tym wątku pozostawały w tej powiązanej sesji.

    Podstawowy przepływ:

    - Uruchom przez `sessions_spawn` z `thread: true` (i opcjonalnie `mode: "session"` dla trwałych wiadomości następczych).
    - Albo ręcznie powiąż przez `/focus <target>`.
    - Użyj `/agents`, aby sprawdzić stan powiązania.
    - Użyj `/session idle <duration|off>` i `/session max-age <duration|off>`, aby sterować automatycznym odwiązaniem.
    - Użyj `/unfocus`, aby odłączyć wątek.

    Wymagana konfiguracja:

    - Globalne wartości domyślne: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Nadpisania Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Automatyczne wiązanie przy uruchamianiu: ustaw `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Discord](/pl/channels/discord), [Configuration Reference](/pl/gateway/configuration-reference), [Slash commands](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Sub-agent się zakończył, ale aktualizacja o ukończeniu trafiła w złe miejsce albo w ogóle nie została opublikowana. Co sprawdzić?">
    Najpierw sprawdź rozstrzygniętą trasę żądającego:

    - Dostarczanie ukończenia w trybie completion preferuje każdy powiązany wątek lub trasę rozmowy, jeśli taka istnieje.
    - Jeśli źródło ukończenia zawiera tylko kanał, OpenClaw wraca do zapisanej trasy sesji żądającego (`lastChannel` / `lastTo` / `lastAccountId`), dzięki czemu bezpośrednie dostarczenie nadal może się udać.
    - Jeśli nie istnieje ani powiązana trasa, ani użyteczna zapisana trasa, bezpośrednie dostarczenie może się nie powieść, a wynik wraca wtedy do kolejkowanego dostarczenia sesji zamiast zostać natychmiast opublikowany na czacie.
    - Nieprawidłowe lub nieaktualne cele nadal mogą wymusić powrót do kolejki albo końcową porażkę dostarczenia.
    - Jeśli ostatnia widoczna odpowiedź asystenta dziecka to dokładnie cichy token `NO_REPLY` / `no_reply` albo dokładnie `ANNOUNCE_SKIP`, OpenClaw celowo tłumi ogłoszenie zamiast publikować wcześniejszy, nieaktualny postęp.
    - Jeśli dziecko przekroczyło limit czasu po samych wywołaniach narzędzi, ogłoszenie może zwinąć to do krótkiego podsumowania częściowego postępu zamiast odtwarzać surowe wyjście narzędzi.

    Debugowanie:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Background Tasks](/pl/automation/tasks), [Session Tools](/pl/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron lub przypomnienia nie uruchamiają się. Co sprawdzić?">
    Cron działa wewnątrz procesu Gateway. Jeśli Gateway nie działa stale,
    zaplanowane zadania nie będą się uruchamiać.

    Lista kontrolna:

    - Potwierdź, że Cron jest włączony (`cron.enabled`) i że `OPENCLAW_SKIP_CRON` nie jest ustawione.
    - Sprawdź, czy Gateway działa 24/7 (bez uśpień/restartów).
    - Zweryfikuj ustawienia strefy czasowej dla zadania (`--tz` vs strefa czasowa hosta).

    Debugowanie:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Dokumentacja: [Cron jobs](/pl/automation/cron-jobs), [Automation & Tasks](/pl/automation).

  </Accordion>

  <Accordion title="Cron się uruchomił, ale nic nie zostało wysłane do kanału. Dlaczego?">
    Najpierw sprawdź tryb dostarczania:

    - `--no-deliver` / `delivery.mode: "none"` oznacza, że nie należy oczekiwać żadnej wiadomości zewnętrznej.
    - Brakujący lub nieprawidłowy cel ogłoszenia (`channel` / `to`) oznacza, że runner pominął dostarczenie wychodzące.
    - Błędy uwierzytelniania kanału (`unauthorized`, `Forbidden`) oznaczają, że runner próbował dostarczyć wiadomość, ale poświadczenia to zablokowały.
    - Cichy wynik izolowany (`NO_REPLY` / `no_reply` bez niczego więcej) jest traktowany jako celowo nienadający się do dostarczenia, więc runner tłumi też awaryjne dostarczenie przez kolejkę.

    W przypadku izolowanych zadań Cron runner odpowiada za końcowe dostarczenie. Agent powinien
    zwrócić zwykłe tekstowe podsumowanie, które runner wyśle. `--no-deliver` zachowuje
    ten wynik wewnętrznie; nie pozwala agentowi zamiast tego wysyłać bezpośrednio
    przez narzędzie wiadomości.

    Debugowanie:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Cron jobs](/pl/automation/cron-jobs), [Background Tasks](/pl/automation/tasks).

  </Accordion>

  <Accordion title="Dlaczego izolowane uruchomienie Cron przełączyło modele albo wykonało jedną ponowną próbę?">
    To zwykle ścieżka przełączania modelu na żywo, a nie zduplikowane harmonogramowanie.

    Izolowany Cron może utrwalić przekazanie modelu w czasie działania i wykonać ponowną próbę, gdy aktywne
    uruchomienie zgłosi `LiveSessionModelSwitchError`. Ponowna próba zachowuje przełączonego
    dostawcę/model, a jeśli przełączenie zawierało nowe nadpisanie profilu uwierzytelniania, Cron
    zapisuje je również przed ponowną próbą.

    Powiązane reguły wyboru:

    - Najpierw wygrywa nadpisanie modelu hooka Gmail, jeśli ma zastosowanie.
    - Następnie `model` dla danego zadania.
    - Następnie dowolne zapisane nadpisanie modelu sesji Cron.
    - Następnie zwykły wybór modelu agenta/dom yślnego modelu.

    Pętla ponownych prób jest ograniczona. Po początkowej próbie i 2 ponownych próbach przełączenia
    Cron przerywa działanie zamiast zapętlać się bez końca.

    Debugowanie:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Cron jobs](/pl/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Jak zainstalować Skills na Linux?">
    Użyj natywnych poleceń `openclaw skills` albo umieść Skills w swoim workspace. UI Skills dla macOS nie jest dostępne na Linux.
    Przeglądaj Skills na [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    Natywne `openclaw skills install` zapisuje do aktywnego katalogu `skills/`
    w workspace. Osobne CLI `clawhub` instaluj tylko wtedy, gdy chcesz publikować lub
    synchronizować własne Skills. W przypadku instalacji współdzielonych między agentami umieść Skill w
    `~/.openclaw/skills` i użyj `agents.defaults.skills` lub
    `agents.list[].skills`, jeśli chcesz zawęzić, którzy agenci mogą go widzieć.

  </Accordion>

  <Accordion title="Czy OpenClaw może uruchamiać zadania według harmonogramu lub stale w tle?">
    Tak. Użyj harmonogramu Gateway:

    - **Cron jobs** do zadań zaplanowanych lub cyklicznych (utrzymują się po restartach).
    - **Heartbeat** do okresowych kontroli „głównej sesji”.
    - **Zadania izolowane** dla autonomicznych agentów, które publikują podsumowania lub dostarczają je na czaty.

    Dokumentacja: [Cron jobs](/pl/automation/cron-jobs), [Automation & Tasks](/pl/automation),
    [Heartbeat](/pl/gateway/heartbeat).

  </Accordion>

  <Accordion title="Czy mogę uruchamiać Apple Skills tylko dla macOS z Linux?">
    Nie bezpośrednio. Skills macOS są ograniczane przez `metadata.openclaw.os` oraz wymagane binaria, a Skills pojawiają się w prompcie systemowym tylko wtedy, gdy kwalifikują się na **hoście Gateway**. W Linux Skills tylko dla `darwin` (takie jak `apple-notes`, `apple-reminders`, `things-mac`) nie zostaną załadowane, chyba że nadpiszesz te ograniczenia.

    Masz trzy obsługiwane wzorce:

    **Opcja A — uruchom Gateway na Mac (najprostsze).**
    Uruchom Gateway tam, gdzie istnieją binaria macOS, a następnie połącz się z Linux w [trybie zdalnym](#gateway-ports-already-running-and-remote-mode) lub przez Tailscale. Skills załadują się normalnie, ponieważ host Gateway działa na macOS.

    **Opcja B — użyj Node macOS (bez SSH).**
    Uruchom Gateway na Linux, sparuj Node macOS (aplikacja w pasku menu) i ustaw **Node Run Commands** na „Always Ask” lub „Always Allow” na Mac. OpenClaw może traktować Skills tylko dla macOS jako kwalifikujące się, gdy wymagane binaria istnieją na Node. Agent uruchamia te Skills przez narzędzie `nodes`. Jeśli wybierzesz „Always Ask”, zatwierdzenie „Always Allow” w prompcie doda to polecenie do allowlist.

    **Opcja C — proxowanie binariów macOS przez SSH (zaawansowane).**
    Pozostaw Gateway na Linux, ale spraw, by wymagane binaria CLI były rozwiązywane do wrapperów SSH uruchamianych na Mac. Następnie nadpisz Skill, aby zezwalał na Linux i pozostawał kwalifikowalny.

    1. Utwórz wrapper SSH dla binarium (przykład: `memo` dla Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Umieść wrapper w `PATH` na hoście Linux (na przykład `~/bin/memo`).
    3. Nadpisz metadane Skill (workspace lub `~/.openclaw/skills`), aby zezwalały na Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Rozpocznij nową sesję, aby odświeżyć migawkę Skills.

  </Accordion>

  <Accordion title="Czy macie integrację z Notion lub HeyGen?">
    Obecnie nie jest wbudowana.

    Opcje:

    - **Własny Skill / Plugin:** najlepszy dla niezawodnego dostępu do API (zarówno Notion, jak i HeyGen mają API).
    - **Automatyzacja przeglądarki:** działa bez kodu, ale jest wolniejsza i bardziej krucha.

    Jeśli chcesz utrzymywać kontekst dla każdego klienta (przepływy agencyjne), prosty wzorzec jest taki:

    - Jedna strona Notion na klienta (kontekst + preferencje + aktywna praca).
    - Poproś agenta, aby pobierał tę stronę na początku sesji.

    Jeśli chcesz natywną integrację, otwórz prośbę o funkcję albo zbuduj Skill
    korzystający z tych API.

    Instalacja Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Instalacje natywne trafiają do aktywnego katalogu `skills/` w workspace. W przypadku współdzielonych Skills między agentami umieść je w `~/.openclaw/skills/<name>/SKILL.md`. Jeśli tylko niektórzy agenci mają widzieć wspólną instalację, skonfiguruj `agents.defaults.skills` lub `agents.list[].skills`. Niektóre Skills oczekują binariów instalowanych przez Homebrew; na Linux oznacza to Linuxbrew (zobacz wpis FAQ o Homebrew na Linux powyżej). Zobacz [Skills](/pl/tools/skills), [Skills config](/pl/tools/skills-config) i [ClawHub](/pl/tools/clawhub).

  </Accordion>

  <Accordion title="Jak używać istniejącego zalogowanego Chrome z OpenClaw?">
    Użyj wbudowanego profilu przeglądarki `user`, który łączy się przez Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Jeśli chcesz niestandardowej nazwy, utwórz jawny profil MCP:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Ta ścieżka jest lokalna dla hosta. Jeśli Gateway działa gdzie indziej, uruchom hosta Node na maszynie przeglądarki albo użyj zdalnego CDP.

    Obecne ograniczenia `existing-session` / `user`:

    - działania są oparte na `ref`, a nie na selektorach CSS
    - przesyłanie plików wymaga `ref` / `inputRef` i obecnie obsługuje tylko jeden plik naraz
    - `responsebody`, eksport PDF, przechwytywanie pobrań i działania wsadowe nadal wymagają zarządzanej przeglądarki albo surowego profilu CDP

  </Accordion>
</AccordionGroup>

## Sandbox i pamięć

<AccordionGroup>
  <Accordion title="Czy istnieje osobny dokument o sandboxingu?">
    Tak. Zobacz [Sandboxing](/pl/gateway/sandboxing). Informacje o konfiguracji specyficznej dla Docker (pełny Gateway w Docker lub obrazy sandbox) znajdziesz w [Docker](/pl/install/docker).
  </Accordion>

  <Accordion title="Docker wydaje się ograniczony — jak włączyć pełne funkcje?">
    Domyślny obraz stawia bezpieczeństwo na pierwszym miejscu i działa jako użytkownik `node`, więc nie
    zawiera pakietów systemowych, Homebrew ani dołączonych przeglądarek. Aby uzyskać pełniejszą konfigurację:

    - Utrwal `/home/node` za pomocą `OPENCLAW_HOME_VOLUME`, aby cache przetrwał.
    - Wbuduj zależności systemowe do obrazu za pomocą `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Zainstaluj przeglądarki Playwright przez dołączone CLI:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Ustaw `PLAYWRIGHT_BROWSERS_PATH` i upewnij się, że ta ścieżka jest utrwalana.

    Dokumentacja: [Docker](/pl/install/docker), [Browser](/pl/tools/browser).

  </Accordion>

  <Accordion title="Czy mogę zachować prywatne DM, ale uczynić grupy publicznymi/sandboxowanymi przy użyciu jednego agenta?">
    Tak — jeśli twój ruch prywatny to **DM**, a ruch publiczny to **grupy**.

    Użyj `agents.defaults.sandbox.mode: "non-main"`, aby sesje grupowe/kanałowe (klucze inne niż główne) działały w Docker, podczas gdy główna sesja DM pozostaje na hoście. Następnie ogranicz, które narzędzia są dostępne w sesjach sandboxowanych, przez `tools.sandbox.tools`.

    Przewodnik konfiguracji + przykładowa konfiguracja: [Groups: personal DMs + public groups](/pl/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Odwołanie do kluczowej konfiguracji: [Gateway configuration](/pl/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Jak powiązać folder hosta z sandboxem?">
    Ustaw `agents.defaults.sandbox.docker.binds` na `["host:path:mode"]` (np. `"/home/user/src:/src:ro"`). Powiązania globalne i per agent są scalane; powiązania per agent są ignorowane, gdy `scope: "shared"`. Używaj `:ro` dla wszystkiego, co wrażliwe, i pamiętaj, że powiązania omijają granice systemu plików sandboxa.

    OpenClaw sprawdza źródła bind zarówno względem ścieżki znormalizowanej, jak i ścieżki kanonicznej rozwiązanej przez najgłębszego istniejącego przodka. Oznacza to, że ucieczki przez symlink w katalogu nadrzędnym nadal kończą się bezpiecznym odrzuceniem nawet wtedy, gdy ostatni segment ścieżki jeszcze nie istnieje, a kontrole dozwolonego katalogu głównego nadal obowiązują po rozwiązaniu symlinków.

    Zobacz [Sandboxing](/pl/gateway/sandboxing#custom-bind-mounts) i [Sandbox vs Tool Policy vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check), aby poznać przykłady i uwagi dotyczące bezpieczeństwa.

  </Accordion>

  <Accordion title="Jak działa pamięć?">
    Pamięć OpenClaw to po prostu pliki Markdown w workspace agenta:

    - Codzienne notatki w `memory/YYYY-MM-DD.md`
    - Kuratorowane notatki długoterminowe w `MEMORY.md` (tylko sesje główne/prywatne)

    OpenClaw uruchamia też **ciche opróżnianie pamięci przed Compaction**, aby przypomnieć modelowi
    o zapisaniu trwałych notatek przed automatycznym Compaction. Działa to tylko wtedy, gdy workspace
    jest zapisywalny (sandboxy tylko do odczytu to pomijają). Zobacz [Memory](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Pamięć ciągle zapomina różne rzeczy. Jak sprawić, żeby zostały?">
    Poproś bota, aby **zapisał dany fakt w pamięci**. Notatki długoterminowe powinny trafić do `MEMORY.md`,
    a kontekst krótkoterminowy do `memory/YYYY-MM-DD.md`.

    To nadal obszar, który ulepszamy. Pomaga przypominanie modelowi, aby zapisywał wspomnienia;
    będzie wiedział, co zrobić. Jeśli nadal zapomina, sprawdź, czy Gateway używa tego samego
    workspace przy każdym uruchomieniu.

    Dokumentacja: [Memory](/pl/concepts/memory), [Agent workspace](/pl/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Czy pamięć utrzymuje się na zawsze? Jakie są limity?">
    Pliki pamięci są przechowywane na dysku i pozostają tam, dopóki ich nie usuniesz. Ograniczeniem jest
    miejsce na dysku, a nie model. **Kontekst sesji** nadal jest jednak ograniczony przez okno kontekstu modelu,
    więc długie rozmowy mogą zostać skompaktowane lub obcięte. Dlatego istnieje
    wyszukiwanie w pamięci — przywraca ono do kontekstu tylko odpowiednie fragmenty.

    Dokumentacja: [Memory](/pl/concepts/memory), [Context](/pl/concepts/context).

  </Accordion>

  <Accordion title="Czy semantyczne wyszukiwanie w pamięci wymaga klucza API OpenAI?">
    Tylko jeśli używasz **embeddingów OpenAI**. OAuth Codex obejmuje chat/completions i
    **nie** przyznaje dostępu do embeddingów, więc **logowanie przez Codex (OAuth lub
    logowanie CLI Codex)** nie pomaga w semantycznym wyszukiwaniu pamięci. Embeddingi OpenAI
    nadal wymagają prawdziwego klucza API (`OPENAI_API_KEY` lub `models.providers.openai.apiKey`).

    Jeśli nie ustawisz jawnie dostawcy, OpenClaw automatycznie wybiera dostawcę, gdy
    może rozwiązać klucz API (profile uwierzytelniania, `models.providers.*.apiKey` lub zmienne środowiskowe).
    Preferuje OpenAI, jeśli rozwiąże klucz OpenAI, w przeciwnym razie Gemini, jeśli
    rozwiąże klucz Gemini, potem Voyage, a następnie Mistral. Jeśli nie ma dostępnego zdalnego klucza,
    wyszukiwanie pamięci pozostaje wyłączone, dopóki go nie skonfigurujesz. Jeśli masz skonfigurowaną i obecną
    ścieżkę modelu lokalnego, OpenClaw
    preferuje `local`. Ollama jest obsługiwane, gdy jawnie ustawisz
    `memorySearch.provider = "ollama"`.

    Jeśli wolisz pozostać lokalnie, ustaw `memorySearch.provider = "local"` (i opcjonalnie
    `memorySearch.fallback = "none"`). Jeśli chcesz embeddingów Gemini, ustaw
    `memorySearch.provider = "gemini"` i podaj `GEMINI_API_KEY` (lub
    `memorySearch.remote.apiKey`). Obsługujemy modele embeddingów **OpenAI, Gemini, Voyage, Mistral, Ollama lub local**
    — szczegóły konfiguracji znajdziesz w [Memory](/pl/concepts/memory).

  </Accordion>
</AccordionGroup>

## Gdzie rzeczy znajdują się na dysku

<AccordionGroup>
  <Accordion title="Czy wszystkie dane używane z OpenClaw są zapisywane lokalnie?">
    Nie — **stan OpenClaw jest lokalny**, ale **zewnętrzne usługi nadal widzą to, co im wysyłasz**.

    - **Domyślnie lokalne:** sesje, pliki pamięci, konfiguracja i workspace znajdują się na hoście Gateway
      (`~/.openclaw` + katalog twojego workspace).
    - **Zdalne z konieczności:** wiadomości wysyłane do dostawców modeli (Anthropic/OpenAI/itd.) trafiają do
      ich API, a platformy czatu (WhatsApp/Telegram/Slack/itd.) przechowują dane wiadomości na swoich
      serwerach.
    - **Ty kontrolujesz zakres:** używanie modeli lokalnych utrzymuje prompty na twojej maszynie, ale ruch kanałów
      nadal przechodzi przez serwery danego kanału.

    Powiązane: [Agent workspace](/pl/concepts/agent-workspace), [Memory](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Gdzie OpenClaw przechowuje swoje dane?">
    Wszystko znajduje się w `$OPENCLAW_STATE_DIR` (domyślnie: `~/.openclaw`):

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Główna konfiguracja (JSON5)                                        |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Starszy import OAuth (kopiowany do profili uwierzytelniania przy pierwszym użyciu) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Profile uwierzytelniania (OAuth, klucze API oraz opcjonalne `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Opcjonalny ładunek sekretów opartych na pliku dla dostawców SecretRef typu `file` |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Starszy plik zgodności (statyczne wpisy `api_key` są czyszczone)   |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Stan dostawców (np. `whatsapp/<accountId>/creds.json`)             |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Stan per agent (agentDir + sesje)                                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Historia rozmów i stan (per agent)                                 |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Metadane sesji (per agent)                                         |

    Starsza ścieżka dla pojedynczego agenta: `~/.openclaw/agent/*` (migrowana przez `openclaw doctor`).

    Twój **workspace** (`AGENTS.md`, pliki pamięci, Skills itd.) jest oddzielny i konfigurowany przez `agents.defaults.workspace` (domyślnie: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Gdzie powinny znajdować się AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Te pliki znajdują się w **workspace agenta**, a nie w `~/.openclaw`.

    - **Workspace (per agent)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (lub starszy fallback `memory.md`, gdy `MEMORY.md` nie istnieje),
      `memory/YYYY-MM-DD.md`, opcjonalnie `HEARTBEAT.md`.
    - **Katalog stanu (`~/.openclaw`)**: konfiguracja, stan kanałów/dostawców, profile uwierzytelniania, sesje, logi
      oraz współdzielone Skills (`~/.openclaw/skills`).

    Domyślny workspace to `~/.openclaw/workspace`, konfigurowany przez:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Jeśli bot „zapomina” po restarcie, sprawdź, czy Gateway używa tego samego
    workspace przy każdym uruchomieniu (i pamiętaj: tryb zdalny używa workspace **hosta Gateway**,
    a nie twojego lokalnego laptopa).

    Wskazówka: jeśli chcesz trwałego zachowania lub preferencji, poproś bota, aby **zapisał to w
    AGENTS.md lub MEMORY.md**, zamiast polegać na historii czatu.

    Zobacz [Agent workspace](/pl/concepts/agent-workspace) i [Memory](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Zalecana strategia kopii zapasowych">
    Umieść swój **workspace agenta** w **prywatnym** repozytorium git i twórz jego kopię zapasową gdzieś
    prywatnie (na przykład na prywatnym GitHub). To obejmuje pamięć + pliki AGENTS/SOUL/USER
    i pozwala później odtworzyć „umysł” asystenta.

    **Nie** commituj niczego z `~/.openclaw` (poświadczeń, sesji, tokenów ani zaszyfrowanych ładunków sekretów).
    Jeśli potrzebujesz pełnego odtworzenia, utwórz osobno kopię zapasową zarówno workspace, jak i katalogu stanu
    (zobacz pytanie o migrację powyżej).

    Dokumentacja: [Agent workspace](/pl/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Jak całkowicie odinstalować OpenClaw?">
    Zobacz osobny przewodnik: [Uninstall](/pl/install/uninstall).
  </Accordion>

  <Accordion title="Czy agenci mogą działać poza workspace?">
    Tak. Workspace to **domyślny cwd** i punkt odniesienia dla pamięci, a nie twardy sandbox.
    Ścieżki względne są rozwiązywane wewnątrz workspace, ale ścieżki bezwzględne mogą uzyskiwać dostęp do innych
    lokalizacji hosta, chyba że sandboxing jest włączony. Jeśli potrzebujesz izolacji, użyj
    [`agents.defaults.sandbox`](/pl/gateway/sandboxing) lub ustawień sandbox per agent. Jeśli
    chcesz, aby repozytorium było domyślnym katalogiem roboczym, wskaż `workspace`
    tego agenta na katalog główny repozytorium. Repozytorium OpenClaw to tylko kod źródłowy; trzymaj
    workspace osobno, chyba że celowo chcesz, aby agent pracował w nim.

    Przykład (repozytorium jako domyślny cwd):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Tryb zdalny: gdzie jest magazyn sesji?">
    Stan sesji należy do **hosta Gateway**. Jeśli działasz w trybie zdalnym, interesujący cię magazyn sesji znajduje się na zdalnej maszynie, a nie na twoim lokalnym laptopie. Zobacz [Session management](/pl/concepts/session).
  </Accordion>
</AccordionGroup>

## Podstawy konfiguracji

<AccordionGroup>
  <Accordion title="Jaki jest format konfiguracji? Gdzie ona się znajduje?">
    OpenClaw odczytuje opcjonalną konfigurację **JSON5** z `$OPENCLAW_CONFIG_PATH` (domyślnie: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Jeśli plik nie istnieje, używane są dość bezpieczne ustawienia domyślne (w tym domyślny workspace `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Ustawiłem `gateway.bind: "lan"` (lub `"tailnet"`) i teraz nic nie nasłuchuje / UI mówi unauthorized'>
    Powiązania inne niż loopback **wymagają prawidłowej ścieżki uwierzytelniania Gateway**. W praktyce oznacza to:

    - uwierzytelnianie wspólnym sekretem: token lub hasło
    - `gateway.auth.mode: "trusted-proxy"` za poprawnie skonfigurowanym, świadomym tożsamości reverse proxy innym niż loopback

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Uwagi:

    - `gateway.remote.token` / `.password` same w sobie **nie** włączają lokalnego uwierzytelniania Gateway.
    - Lokalne ścieżki wywołań mogą używać `gateway.remote.*` jako fallbacku tylko wtedy, gdy `gateway.auth.*` nie jest ustawione.
    - W przypadku uwierzytelniania hasłem ustaw `gateway.auth.mode: "password"` oraz `gateway.auth.password` (lub `OPENCLAW_GATEWAY_PASSWORD`).
    - Jeśli `gateway.auth.token` / `gateway.auth.password` jest jawnie skonfigurowane przez SecretRef i nierozwiązane, rozwiązywanie kończy się bezpiecznym odrzuceniem (brak maskującego fallbacku zdalnego).
    - Konfiguracje Control UI ze wspólnym sekretem uwierzytelniają się przez `connect.params.auth.token` lub `connect.params.auth.password` (przechowywane w ustawieniach aplikacji/UI). Tryby oparte na tożsamości, takie jak Tailscale Serve lub `trusted-proxy`, używają zamiast tego nagłówków żądania. Unikaj umieszczania wspólnych sekretów w URL.
    - Przy `gateway.auth.mode: "trusted-proxy"` reverse proxy loopback na tym samym hoście nadal **nie** spełniają wymagań uwierzytelniania trusted-proxy. Zaufane proxy musi być skonfigurowanym źródłem innym niż loopback.

  </Accordion>

  <Accordion title="Dlaczego teraz potrzebuję tokena na localhost?">
    OpenClaw domyślnie wymusza uwierzytelnianie Gateway, także dla loopback. W zwykłej ścieżce domyślnej oznacza to uwierzytelnianie tokenem: jeśli nie skonfigurowano jawnie ścieżki uwierzytelniania, uruchamianie Gateway przechodzi do trybu tokenu i automatycznie go generuje, zapisując w `gateway.auth.token`, więc **lokalni klienci WS muszą się uwierzytelniać**. To blokuje innym lokalnym procesom wywoływanie Gateway.

    Jeśli wolisz inną ścieżkę uwierzytelniania, możesz jawnie wybrać tryb hasła (lub, dla reverse proxy świadomych tożsamości innych niż loopback, `trusted-proxy`). Jeśli **naprawdę** chcesz otwarty loopback, ustaw jawnie `gateway.auth.mode: "none"` w konfiguracji. Doctor może wygenerować token w dowolnym momencie: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Czy po zmianie konfiguracji muszę wykonać restart?">
    Gateway obserwuje konfigurację i obsługuje hot-reload:

    - `gateway.reload.mode: "hybrid"` (domyślnie): bezpieczne zmiany stosuje na gorąco, krytyczne wymagają restartu
    - obsługiwane są też `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="Jak wyłączyć zabawne hasła CLI?">
    Ustaw `cli.banner.taglineMode` w konfiguracji:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: ukrywa tekst hasła, ale zachowuje linię tytułu/wersji banera.
    - `default`: zawsze używa `All your chats, one OpenClaw.`.
    - `random`: rotujące zabawne/sezonowe hasła (domyślne zachowanie).
    - Jeśli nie chcesz żadnego banera, ustaw zmienną środowiskową `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Jak włączyć wyszukiwanie w sieci (i pobieranie z sieci)?">
    `web_fetch` działa bez klucza API. `web_search` zależy od wybranego
    dostawcy:

    - Dostawcy oparci na API, tacy jak Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity i Tavily, wymagają standardowej konfiguracji klucza API.
    - Ollama Web Search nie wymaga klucza, ale używa skonfigurowanego hosta Ollama i wymaga `ollama signin`.
    - DuckDuckGo nie wymaga klucza, ale jest to nieoficjalna integracja oparta na HTML.
    - SearXNG nie wymaga klucza/jest self-hosted; skonfiguruj `SEARXNG_BASE_URL` lub `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Zalecane:** uruchom `openclaw configure --section web` i wybierz dostawcę.
    Alternatywy w zmiennych środowiskowych:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` lub `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY` lub `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` lub `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // opcjonalne; pomiń dla auto-detekcji
            },
          },
        },
    }
    ```

    Konfiguracja wyszukiwania w sieci specyficzna dla dostawcy znajduje się teraz pod `plugins.entries.<plugin>.config.webSearch.*`.
    Starsze ścieżki dostawców `tools.web.search.*` nadal są tymczasowo wczytywane dla zgodności, ale nie powinny być używane w nowych konfiguracjach.
    Konfiguracja fallbacku Firecrawl dla web-fetch znajduje się pod `plugins.entries.firecrawl.config.webFetch.*`.

    Uwagi:

    - Jeśli używasz allowlist, dodaj `web_search`/`web_fetch`/`x_search` lub `group:web`.
    - `web_fetch` jest domyślnie włączone (chyba że jawnie je wyłączysz).
    - Jeśli `tools.web.fetch.provider` zostanie pominięte, OpenClaw automatycznie wykrywa pierwszego gotowego dostawcę fallback dla fetch na podstawie dostępnych poświadczeń. Obecnie dołączonym dostawcą jest Firecrawl.
    - Demony odczytują zmienne środowiskowe z `~/.openclaw/.env` (lub ze środowiska usługi).

    Dokumentacja: [Web tools](/pl/tools/web).

  </Accordion>

  <Accordion title="config.apply wyczyścił moją konfigurację. Jak to odzyskać i jak tego uniknąć?">
    `config.apply` zastępuje **całą konfigurację**. Jeśli wyślesz obiekt częściowy, wszystko
    inne zostanie usunięte.

    Odzyskiwanie:

    - Przywróć z kopii zapasowej (git lub skopiowane `~/.openclaw/openclaw.json`).
    - Jeśli nie masz kopii zapasowej, uruchom ponownie `openclaw doctor` i skonfiguruj kanały/modele od nowa.
    - Jeśli było to nieoczekiwane, zgłoś błąd i dołącz ostatnią znaną konfigurację lub dowolną kopię zapasową.
    - Lokalny agent kodujący często potrafi odtworzyć działającą konfigurację na podstawie logów lub historii.

    Jak tego uniknąć:

    - Używaj `openclaw config set` do małych zmian.
    - Używaj `openclaw configure` do edycji interaktywnych.
    - Najpierw użyj `config.schema.lookup`, jeśli nie masz pewności co do dokładnej ścieżki lub kształtu pola; zwraca płytki węzeł schematu oraz podsumowania bezpośrednich dzieci do dalszego zagłębiania się.
    - Używaj `config.patch` do częściowych edycji RPC; zachowaj `config.apply` wyłącznie do pełnej zamiany konfiguracji.
    - Jeśli używasz narzędzia `gateway` tylko dla właściciela z uruchomienia agenta, nadal będzie ono odrzucać zapisy do `tools.exec.ask` / `tools.exec.security` (w tym starsze aliasy `tools.bash.*`, które normalizują się do tych samych chronionych ścieżek exec).

    Dokumentacja: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/pl/gateway/doctor).

  </Accordion>

  <Accordion title="Jak uruchomić centralny Gateway ze specjalizowanymi workerami na różnych urządzeniach?">
    Typowy wzorzec to **jeden Gateway** (np. Raspberry Pi) plus **Nodes** i **agenci**:

    - **Gateway (centralny):** zarządza kanałami (Signal/WhatsApp), rutingiem i sesjami.
    - **Nodes (urządzenia):** Mac/iOS/Android łączą się jako peryferia i udostępniają lokalne narzędzia (`system.run`, `canvas`, `camera`).
    - **Agenci (workery):** oddzielne „mózgi”/workspace dla specjalnych ról (np. „Hetzner ops”, „Dane osobiste”).
    - **Sub-agenci:** uruchamiają pracę w tle z głównego agenta, gdy chcesz równoległości.
    - **TUI:** łączy się z Gateway i przełącza agentów/sesje.

    Dokumentacja: [Nodes](/pl/nodes), [Remote access](/pl/gateway/remote), [Multi-Agent Routing](/pl/concepts/multi-agent), [Sub-agents](/pl/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Czy przeglądarka OpenClaw może działać bez interfejsu?">
    Tak. To opcja konfiguracji:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    Domyślnie jest `false` (z interfejsem). Tryb headless z większym prawdopodobieństwem uruchamia kontrole antybotowe na niektórych stronach. Zobacz [Browser](/pl/tools/browser).

    Tryb headless używa **tego samego silnika Chromium** i działa w większości przypadków automatyzacji (formularze, kliknięcia, scraping, logowanie). Główne różnice:

    - Brak widocznego okna przeglądarki (jeśli potrzebujesz obrazu, używaj zrzutów ekranu).
    - Niektóre strony są bardziej rygorystyczne wobec automatyzacji w trybie headless (CAPTCHA, antybot).
      Na przykład X/Twitter często blokuje sesje headless.

  </Accordion>

  <Accordion title="Jak używać Brave do sterowania przeglądarką?">
    Ustaw `browser.executablePath` na binarkę Brave (lub dowolnej przeglądarki opartej na Chromium) i zrestartuj Gateway.
    Pełne przykłady konfiguracji znajdziesz w [Browser](/pl/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Zdalne Gateway i Nodes

<AccordionGroup>
  <Accordion title="Jak polecenia propagują się między Telegram, Gateway i Nodes?">
    Wiadomości Telegram są obsługiwane przez **Gateway**. Gateway uruchamia agenta i
    dopiero wtedy wywołuje Nodes przez **Gateway WebSocket**, gdy potrzebne jest narzędzie Node:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes nie widzą przychodzącego ruchu od dostawców; otrzymują tylko wywołania RPC Node.

  </Accordion>

  <Accordion title="Jak mój agent może uzyskać dostęp do mojego komputera, jeśli Gateway jest hostowany zdalnie?">
    Krótka odpowiedź: **sparuj swój komputer jako Node**. Gateway działa gdzie indziej, ale może
    wywoływać narzędzia `node.*` (ekran, kamera, system) na twojej lokalnej maszynie przez Gateway WebSocket.

    Typowa konfiguracja:

    1. Uruchom Gateway na stale działającym hoście (VPS/serwer domowy).
    2. Umieść host Gateway i swój komputer w tym samym tailnet.
    3. Upewnij się, że Gateway WS jest osiągalny (bind tailnet lub tunel SSH).
    4. Otwórz lokalnie aplikację macOS i połącz się w trybie **Remote over SSH** (lub bezpośrednio przez tailnet),
       aby mogła zarejestrować się jako Node.
    5. Zatwierdź Node na Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Nie jest wymagany osobny most TCP; Nodes łączą się przez Gateway WebSocket.

    Przypomnienie dotyczące bezpieczeństwa: sparowanie Node macOS umożliwia `system.run` na tej maszynie. Paryj tylko zaufane urządzenia i zapoznaj się z [Security](/pl/gateway/security).

    Dokumentacja: [Nodes](/pl/nodes), [Gateway protocol](/pl/gateway/protocol), [macOS remote mode](/pl/platforms/mac/remote), [Security](/pl/gateway/security).

  </Accordion>

  <Accordion title="Tailscale jest połączony, ale nie otrzymuję odpowiedzi. Co teraz?">
    Sprawdź podstawy:

    - Gateway działa: `openclaw gateway status`
    - Zdrowie Gateway: `openclaw status`
    - Zdrowie kanałów: `openclaw channels status`

    Następnie zweryfikuj uwierzytelnianie i ruting:

    - Jeśli używasz Tailscale Serve, upewnij się, że `gateway.auth.allowTailscale` jest ustawione poprawnie.
    - Jeśli łączysz się przez tunel SSH, potwierdź, że lokalny tunel działa i wskazuje właściwy port.
    - Potwierdź, że allowlisty (DM lub grupowe) obejmują twoje konto.

    Dokumentacja: [Tailscale](/pl/gateway/tailscale), [Remote access](/pl/gateway/remote), [Channels](/pl/channels).

  </Accordion>

  <Accordion title="Czy dwie instancje OpenClaw mogą rozmawiać ze sobą (lokalna + VPS)?">
    Tak. Nie ma wbudowanego mostu „bot-do-bota”, ale możesz to połączyć na kilka
    niezawodnych sposobów:

    **Najprościej:** użyj zwykłego kanału czatu, do którego oba boty mają dostęp (Telegram/Slack/WhatsApp).
    Niech Bot A wyśle wiadomość do Bota B, a potem Bot B odpowie jak zwykle.

    **Most CLI (ogólny):** uruchom skrypt, który wywołuje drugi Gateway przez
    `openclaw agent --message ... --deliver`, kierując do czatu, na którym drugi bot
    nasłuchuje. Jeśli jeden bot działa na zdalnym VPS, skieruj CLI na ten zdalny Gateway
    przez SSH/Tailscale (zobacz [Remote access](/pl/gateway/remote)).

    Przykładowy wzorzec (uruchamiany z maszyny, która może osiągnąć docelowy Gateway):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Wskazówka: dodaj zabezpieczenie, aby oba boty nie zapętliły się bez końca (tylko wzmianki, allowlisty kanałów albo reguła „nie odpowiadaj na wiadomości botów”).

    Dokumentacja: [Remote access](/pl/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/pl/tools/agent-send).

  </Accordion>

  <Accordion title="Czy potrzebuję osobnych VPS-ów dla wielu agentów?">
    Nie. Jeden Gateway może hostować wielu agentów, z których każdy ma własny workspace, domyślne modele
    i ruting. To jest normalna konfiguracja i jest znacznie tańsza oraz prostsza niż uruchamianie
    jednego VPS na agenta.

    Używaj osobnych VPS-ów tylko wtedy, gdy potrzebujesz twardej izolacji (granic bezpieczeństwa) albo bardzo
    różnych konfiguracji, których nie chcesz współdzielić. W przeciwnym razie zachowaj jeden Gateway i
    używaj wielu agentów lub sub-agentów.

  </Accordion>

  <Accordion title="Czy korzystanie z Node na moim prywatnym laptopie zamiast SSH z VPS ma jakieś zalety?">
    Tak — Nodes to rozwiązanie pierwszej klasy do uzyskiwania dostępu do laptopa ze zdalnego Gateway i
    oferują więcej niż tylko dostęp do powłoki. Gateway działa na macOS/Linux (Windows przez WSL2) i jest
    lekki (wystarczy mały VPS lub urządzenie klasy Raspberry Pi; 4 GB RAM to aż nadto), więc częstą
    konfiguracją jest stale działający host plus twój laptop jako Node.

    - **Brak potrzeby przychodzącego SSH.** Nodes łączą się wychodząco z Gateway WebSocket i używają parowania urządzeń.
    - **Bezpieczniejsze kontrole wykonywania.** `system.run` jest ograniczone przez allowlisty/zatwierdzenia Node na tym laptopie.
    - **Więcej narzędzi urządzenia.** Nodes udostępniają `canvas`, `camera` i `screen` oprócz `system.run`.
    - **Lokalna automatyzacja przeglądarki.** Zachowaj Gateway na VPS, ale uruchamiaj Chrome lokalnie przez hosta Node na laptopie albo podłącz się do lokalnego Chrome na hoście przez Chrome MCP.

    SSH jest w porządku do doraźnego dostępu do powłoki, ale Nodes są prostsze dla ciągłych przepływów pracy agenta i
    automatyzacji urządzeń.

    Dokumentacja: [Nodes](/pl/nodes), [Nodes CLI](/cli/nodes), [Browser](/pl/tools/browser).

  </Accordion>

  <Accordion title="Czy Nodes uruchamiają usługę Gateway?">
    Nie. Na hoście powinien działać tylko **jeden Gateway**, chyba że celowo uruchamiasz izolowane profile (zobacz [Multiple gateways](/pl/gateway/multiple-gateways)). Nodes to urządzenia peryferyjne, które łączą się
    z Gateway (Nodes iOS/Android albo tryb „node mode” w aplikacji macOS w pasku menu). Informacje o bezgłowych
    hostach Node i sterowaniu przez CLI znajdziesz w [Node host CLI](/cli/node).

    Pełny restart jest wymagany dla zmian `gateway`, `discovery` i `canvasHost`.

  </Accordion>

  <Accordion title="Czy istnieje sposób API / RPC na zastosowanie konfiguracji?">
    Tak.

    - `config.schema.lookup`: sprawdza jedno poddrzewo konfiguracji wraz z jego płytkim węzłem schematu, dopasowaną wskazówką UI i podsumowaniami bezpośrednich dzieci przed zapisem
    - `config.get`: pobiera bieżącą migawkę + hash
    - `config.patch`: bezpieczna częściowa aktualizacja (zalecana dla większości edycji RPC); wykonuje hot-reload, gdy to możliwe, i restart, gdy jest wymagany
    - `config.apply`: waliduje i zastępuje pełną konfigurację; wykonuje hot-reload, gdy to możliwe, i restart, gdy jest wymagany
    - Narzędzie runtime `gateway` tylko dla właściciela nadal odmawia przepisywania `tools.exec.ask` / `tools.exec.security`; starsze aliasy `tools.bash.*` normalizują się do tych samych chronionych ścieżek exec

  </Accordion>

  <Accordion title="Minimalna sensowna konfiguracja dla pierwszej instalacji">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    To ustawia twój workspace i ogranicza, kto może uruchamiać bota.

  </Accordion>

  <Accordion title="Jak skonfigurować Tailscale na VPS i połączyć się z niego z mojego Mac?">
    Minimalne kroki:

    1. **Zainstaluj i zaloguj się na VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Zainstaluj i zaloguj się na swoim Mac**
       - Użyj aplikacji Tailscale i zaloguj się do tego samego tailnet.
    3. **Włącz MagicDNS (zalecane)**
       - W konsoli administracyjnej Tailscale włącz MagicDNS, aby VPS miał stabilną nazwę.
    4. **Użyj nazwy hosta tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Jeśli chcesz używać Control UI bez SSH, uruchom Tailscale Serve na VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    To pozostawia Gateway powiązany z loopback i udostępnia HTTPS przez Tailscale. Zobacz [Tailscale](/pl/gateway/tailscale).

  </Accordion>

  <Accordion title="Jak połączyć Node Mac ze zdalnym Gateway (Tailscale Serve)?">
    Serve udostępnia **Gateway Control UI + WS**. Nodes łączą się przez ten sam endpoint Gateway WS.

    Zalecana konfiguracja:

    1. **Upewnij się, że VPS i Mac są w tym samym tailnet**.
    2. **Użyj aplikacji macOS w trybie Remote** (celem SSH może być nazwa hosta tailnet).
       Aplikacja utworzy tunel dla portu Gateway i połączy się jako Node.
    3. **Zatwierdź Node** na Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Dokumentacja: [Gateway protocol](/pl/gateway/protocol), [Discovery](/pl/gateway/discovery), [macOS remote mode](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Czy powinienem zainstalować to na drugim laptopie, czy tylko dodać Node?">
    Jeśli potrzebujesz tylko **lokalnych narzędzi** (ekran/kamera/exec) na drugim laptopie, dodaj go jako
    **Node**. Dzięki temu zachowujesz jeden Gateway i unikasz duplikowania konfiguracji. Lokalne narzędzia Node są
    obecnie dostępne tylko na macOS, ale planujemy rozszerzyć je na inne systemy operacyjne.

    Drugi Gateway instaluj tylko wtedy, gdy potrzebujesz **twardej izolacji** lub dwóch całkowicie oddzielnych botów.

    Dokumentacja: [Nodes](/pl/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/pl/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Zmienne środowiskowe i ładowanie `.env`

<AccordionGroup>
  <Accordion title="Jak OpenClaw ładuje zmienne środowiskowe?">
    OpenClaw odczytuje zmienne środowiskowe z procesu nadrzędnego (powłoka, launchd/systemd, CI itd.) i dodatkowo ładuje:

    - `.env` z bieżącego katalogu roboczego
    - globalny zapasowy `.env` z `~/.openclaw/.env` (czyli `$OPENCLAW_STATE_DIR/.env`)

    Żaden z plików `.env` nie nadpisuje istniejących zmiennych środowiskowych.

    Możesz też zdefiniować wbudowane zmienne środowiskowe w konfiguracji (stosowane tylko wtedy, gdy brakuje ich w środowisku procesu):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Pełny opis priorytetów i źródeł znajdziesz w [/environment](/pl/help/environment).

  </Accordion>

  <Accordion title="Uruchomiłem Gateway przez usługę i moje zmienne środowiskowe zniknęły. Co teraz?">
    Dwie typowe poprawki:

    1. Umieść brakujące klucze w `~/.openclaw/.env`, aby były pobierane nawet wtedy, gdy usługa nie dziedziczy zmiennych środowiskowych z twojej powłoki.
    2. Włącz import z powłoki (opcjonalne ułatwienie):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    To uruchamia twoją powłokę logowania i importuje tylko brakujące oczekiwane klucze (nigdy nie nadpisuje). Odpowiedniki w zmiennych środowiskowych:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Ustawiłem `COPILOT_GITHUB_TOKEN`, ale models status pokazuje „Shell env: off.”. Dlaczego?'>
    `openclaw models status` raportuje, czy **import zmiennych środowiskowych z powłoki** jest włączony. „Shell env: off”
    **nie** oznacza, że twoje zmienne środowiskowe są nieobecne — oznacza tylko, że OpenClaw nie będzie
    automatycznie ładować twojej powłoki logowania.

    Jeśli Gateway działa jako usługa (launchd/systemd), nie odziedziczy środowiska
    twojej powłoki. Napraw to na jeden z poniższych sposobów:

    1. Umieść token w `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Albo włącz import z powłoki (`env.shellEnv.enabled: true`).
    3. Albo dodaj go do bloku `env` w konfiguracji (stosuje się tylko wtedy, gdy brakuje).

    Następnie zrestartuj Gateway i sprawdź ponownie:

    ```bash
    openclaw models status
    ```

    Tokeny Copilot są odczytywane z `COPILOT_GITHUB_TOKEN` (także `GH_TOKEN` / `GITHUB_TOKEN`).
    Zobacz [/concepts/model-providers](/pl/concepts/model-providers) i [/environment](/pl/help/environment).

  </Accordion>
</AccordionGroup>

## Sesje i wiele czatów

<AccordionGroup>
  <Accordion title="Jak rozpocząć nową rozmowę?">
    Wyślij `/new` lub `/reset` jako samodzielną wiadomość. Zobacz [Session management](/pl/concepts/session).
  </Accordion>

  <Accordion title="Czy sesje resetują się automatycznie, jeśli nigdy nie wyślę /new?">
    Sesje mogą wygasać po `session.idleMinutes`, ale domyślnie jest to **wyłączone** (domyślnie **0**).
    Ustaw wartość dodatnią, aby włączyć wygaszanie bezczynności. Gdy jest włączone, **następna**
    wiadomość po okresie bezczynności rozpoczyna nowy identyfikator sesji dla tego klucza czatu.
    Nie usuwa to transkrypcji — tylko rozpoczyna nową sesję.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Czy da się stworzyć zespół instancji OpenClaw (jeden CEO i wielu agentów)?">
    Tak, przez **routing multi-agent** i **sub-agentów**. Możesz utworzyć jednego agenta
    koordynującego i kilku agentów roboczych z własnymi workspace i modelami.

    Warto jednak traktować to raczej jako **zabawny eksperyment**. Zużywa dużo tokenów i często
    jest mniej wydajne niż używanie jednego bota z osobnymi sesjami. Typowy model, który
    mamy na myśli, to jeden bot, z którym rozmawiasz, z różnymi sesjami do pracy równoległej. Ten
    bot może też uruchamiać sub-agentów, gdy to potrzebne.

    Dokumentacja: [Multi-agent routing](/pl/concepts/multi-agent), [Sub-agents](/pl/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Dlaczego kontekst został obcięty w środku zadania? Jak temu zapobiec?">
    Kontekst sesji jest ograniczony oknem modelu. Długie czaty, duże wyjścia narzędzi lub wiele
    plików mogą wywołać Compaction albo obcięcie.

    Co pomaga:

    - Poproś bota o podsumowanie bieżącego stanu i zapisanie go do pliku.
    - Używaj `/compact` przed długimi zadaniami oraz `/new` przy zmianie tematu.
    - Trzymaj ważny kontekst w workspace i poproś bota, by odczytał go ponownie.
    - Używaj sub-agentów do długiej lub równoległej pracy, aby główny czat pozostawał mniejszy.
    - Wybierz model z większym oknem kontekstu, jeśli to zdarza się często.

  </Accordion>

  <Accordion title="Jak całkowicie zresetować OpenClaw, ale zachować instalację?">
    Użyj polecenia resetowania:

    ```bash
    openclaw reset
    ```

    Nieinteraktywny pełny reset:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Następnie ponownie uruchom konfigurację:

    ```bash
    openclaw onboard --install-daemon
    ```

    Uwagi:

    - Onboarding oferuje też opcję **Reset**, jeśli wykryje istniejącą konfigurację. Zobacz [Onboarding (CLI)](/pl/start/wizard).
    - Jeśli używałeś profili (`--profile` / `OPENCLAW_PROFILE`), zresetuj każdy katalog stanu (domyślnie są to `~/.openclaw-<profile>`).
    - Reset deweloperski: `openclaw gateway --dev --reset` (tylko dla dev; czyści konfigurację dev + poświadczenia + sesje + workspace).

  </Accordion>

  <Accordion title='Dostaję błędy „context too large” — jak zresetować lub skompaktować kontekst?'>
    Użyj jednej z tych opcji:

    - **Compaction** (zachowuje rozmowę, ale podsumowuje starsze tury):

      ```
      /compact
      ```

      albo `/compact <instructions>`, aby ukierunkować podsumowanie.

    - **Reset** (nowy identyfikator sesji dla tego samego klucza czatu):

      ```
      /new
      /reset
      ```

    Jeśli to wciąż się zdarza:

    - Włącz lub dostrój **session pruning** (`agents.defaults.contextPruning`), aby przycinać stare wyjścia narzędzi.
    - Używaj modelu z większym oknem kontekstu.

    Dokumentacja: [Compaction](/pl/concepts/compaction), [Session pruning](/pl/concepts/session-pruning), [Session management](/pl/concepts/session).

  </Accordion>

  <Accordion title='Dlaczego widzę „LLM request rejected: messages.content.tool_use.input field required”?'>
    To błąd walidacji dostawcy: model wygenerował blok `tool_use` bez wymaganego
    `input`. Zwykle oznacza to, że historia sesji jest nieaktualna lub uszkodzona (często po długich wątkach
    albo zmianie narzędzia/schematu).

    Naprawa: rozpocznij nową sesję przez `/new` (samodzielna wiadomość).

  </Accordion>

  <Accordion title="Dlaczego dostaję wiadomości Heartbeat co 30 minut?">
    Heartbeat działa domyślnie co **30m** (**1h** przy użyciu uwierzytelniania OAuth). Dostosuj lub wyłącz go:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // lub "0m", aby wyłączyć
          },
        },
      },
    }
    ```

    Jeśli `HEARTBEAT.md` istnieje, ale jest w praktyce pusty (tylko puste linie i nagłówki
    Markdown, takie jak `# Heading`), OpenClaw pomija uruchomienie Heartbeat, aby oszczędzać wywołania API.
    Jeśli pliku brakuje, Heartbeat nadal się uruchamia, a model decyduje, co zrobić.

    Nadpisania per agent używają `agents.list[].heartbeat`. Dokumentacja: [Heartbeat](/pl/gateway/heartbeat).

  </Accordion>

  <Accordion title='Czy muszę dodać „konto bota” do grupy WhatsApp?'>
    Nie. OpenClaw działa na **twoim własnym koncie**, więc jeśli jesteś w grupie, OpenClaw może ją widzieć.
    Domyślnie odpowiedzi grupowe są blokowane, dopóki nie zezwolisz nadawcom (`groupPolicy: "allowlist"`).

    Jeśli chcesz, aby tylko **ty** mógł wywoływać odpowiedzi grupowe:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Jak uzyskać JID grupy WhatsApp?">
    Opcja 1 (najszybsza): śledź logi i wyślij wiadomość testową do grupy:

    ```bash
    openclaw logs --follow --json
    ```

    Szukaj `chatId` (lub `from`) kończącego się na `@g.us`, na przykład:
    `1234567890-1234567890@g.us`.

    Opcja 2 (jeśli jest już skonfigurowane/dodane do allowlist): wyświetl grupy z konfiguracji:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Dokumentacja: [WhatsApp](/pl/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Dlaczego OpenClaw nie odpowiada w grupie?">
    Dwie częste przyczyny:

    - Filtrowanie po wzmiankach jest włączone (domyślnie). Musisz użyć @wzmianki o bocie (lub dopasować `mentionPatterns`).
    - Skonfigurowałeś `channels.whatsapp.groups` bez `"*"`, a grupa nie znajduje się na allowlist.

    Zobacz [Groups](/pl/channels/groups) i [Group messages](/pl/channels/group-messages).

  </Accordion>

  <Accordion title="Czy grupy/wątki współdzielą kontekst z DM?">
    Czaty bezpośrednie domyślnie zwijają się do głównej sesji. Grupy/kanały mają własne klucze sesji, a tematy Telegram / wątki Discord to oddzielne sesje. Zobacz [Groups](/pl/channels/groups) i [Group messages](/pl/channels/group-messages).
  </Accordion>

  <Accordion title="Ile workspace i agentów mogę utworzyć?">
    Nie ma sztywnych limitów. Dziesiątki (a nawet setki) są w porządku, ale zwracaj uwagę na:

    - **Przyrost zajętości dysku:** sesje + transkrypcje znajdują się w `~/.openclaw/agents/<agentId>/sessions/`.
    - **Koszt tokenów:** więcej agentów oznacza większe równoczesne użycie modeli.
    - **Narzut operacyjny:** profile uwierzytelniania per agent, workspace i routing kanałów.

    Wskazówki:

    - Utrzymuj jeden **aktywny** workspace na agenta (`agents.defaults.workspace`).
    - Przycinaj stare sesje (usuwaj wpisy JSONL lub wpisy w magazynie), jeśli zajętość dysku rośnie.
    - Używaj `openclaw doctor`, aby wykrywać osierocone workspace i niedopasowania profili.

  </Accordion>

  <Accordion title="Czy mogę uruchamiać wiele botów lub czatów jednocześnie (Slack) i jak to skonfigurować?">
    Tak. Użyj **Multi-Agent Routing**, aby uruchamiać wiele odizolowanych agentów i kierować wiadomości przychodzące według
    kanału/konta/peera. Slack jest obsługiwany jako kanał i może być przypisany do określonych agentów.

    Dostęp do przeglądarki jest potężny, ale nie oznacza „wszystkiego, co może człowiek” — antyboty, CAPTCHA i MFA nadal mogą
    blokować automatyzację. Aby uzyskać najbardziej niezawodne sterowanie przeglądarką, używaj lokalnego Chrome MCP na hoście
    albo CDP na maszynie, która faktycznie uruchamia przeglądarkę.

    Konfiguracja zgodna z najlepszymi praktykami:

    - Stale działający host Gateway (VPS/Mac mini).
    - Jeden agent na rolę (powiązania).
    - Kanał(y) Slack przypisane do tych agentów.
    - Lokalna przeglądarka przez Chrome MCP lub Node, gdy jest potrzebna.

    Dokumentacja: [Multi-Agent Routing](/pl/concepts/multi-agent), [Slack](/pl/channels/slack),
    [Browser](/pl/tools/browser), [Nodes](/pl/nodes).

  </Accordion>
</AccordionGroup>

## Modele: domyślne, wybór, aliasy, przełączanie

<AccordionGroup>
  <Accordion title='Co to jest „model domyślny”?'>
    Domyślny model OpenClaw to to, co ustawisz jako:

    ```
    agents.defaults.model.primary
    ```

    Do modeli odwołuje się jako `provider/model` (przykład: `openai/gpt-5.4`). Jeśli pominiesz dostawcę, OpenClaw najpierw próbuje aliasu, potem unikalnego dopasowania skonfigurowanego dostawcy dla dokładnie tego identyfikatora modelu, a dopiero potem wraca do skonfigurowanego domyślnego dostawcy jako przestarzałej ścieżki zgodności. Jeśli ten dostawca nie udostępnia już skonfigurowanego modelu domyślnego, OpenClaw przechodzi na pierwszy skonfigurowany dostawca/model zamiast ujawniać nieaktualny domyślny model usuniętego dostawcy. Nadal jednak powinieneś **jawnie** ustawiać `provider/model`.

  </Accordion>

  <Accordion title="Jaki model polecacie?">
    **Zalecany model domyślny:** używaj najmocniejszego modelu najnowszej generacji dostępnego w twoim stosie dostawców.
    **Dla agentów z włączonymi narzędziami lub obsługujących niezaufane dane wejściowe:** stawiaj siłę modelu ponad kosztem.
    **Dla rutynowego czatu / zadań o niskiej stawce:** używaj tańszych modeli zapasowych i kieruj według roli agenta.

    MiniMax ma własną dokumentację: [MiniMax](/pl/providers/minimax) i
    [Local models](/pl/gateway/local-models).

    Zasada praktyczna: używaj **najlepszego modelu, na jaki cię stać** do zadań o wysokiej stawce, a tańszego
    modelu do rutynowego czatu lub podsumowań. Możesz kierować modele per agent i używać sub-agentów do
    równoległego wykonywania długich zadań (każdy sub-agent zużywa tokeny). Zobacz [Models](/pl/concepts/models) i
    [Sub-agents](/pl/tools/subagents).

    Mocne ostrzeżenie: słabsze / zbyt mocno skwantyzowane modele są bardziej podatne na prompt
    injection i niebezpieczne zachowania. Zobacz [Security](/pl/gateway/security).

    Więcej kontekstu: [Models](/pl/concepts/models).

  </Accordion>

  <Accordion title="Jak przełączać modele bez czyszczenia konfiguracji?">
    Używaj **poleceń modelu** albo edytuj tylko pola **modelu**. Unikaj pełnej zamiany konfiguracji.

    Bezpieczne opcje:

    - `/model` na czacie (szybko, per sesja)
    - `openclaw models set ...` (aktualizuje tylko konfigurację modelu)
    - `openclaw configure --section model` (interaktywnie)
    - edytuj `agents.defaults.model` w `~/.openclaw/openclaw.json`

    Unikaj `config.apply` z obiektem częściowym, chyba że zamierzasz zastąpić całą konfigurację.
    Przy edycjach RPC najpierw sprawdź przez `config.schema.lookup` i preferuj `config.patch`. Ładunek lookup daje znormalizowaną ścieżkę, płytką dokumentację/ograniczenia schematu oraz podsumowania bezpośrednich dzieci
    dla częściowych aktualizacji.
    Jeśli nadpisałeś konfigurację, przywróć ją z kopii zapasowej albo uruchom ponownie `openclaw doctor`, aby ją naprawić.

    Dokumentacja: [Models](/pl/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/pl/gateway/doctor).

  </Accordion>

  <Accordion title="Czy mogę używać modeli self-hosted (llama.cpp, vLLM, Ollama)?">
    Tak. Ollama to najłatwiejsza ścieżka do modeli lokalnych.

    Najszybsza konfiguracja:

    1. Zainstaluj Ollama z `https://ollama.com/download`
    2. Pobierz model lokalny, na przykład `ollama pull gemma4`
    3. Jeśli chcesz też modele chmurowe, uruchom `ollama signin`
    4. Uruchom `openclaw onboard` i wybierz `Ollama`
    5. Wybierz `Local` albo `Cloud + Local`

    Uwagi:

    - `Cloud + Local` daje ci modele chmurowe plus twoje lokalne modele Ollama
    - modele chmurowe, takie jak `kimi-k2.5:cloud`, nie wymagają lokalnego pobierania
    - do ręcznego przełączania używaj `openclaw models list` i `openclaw models set ollama/<model>`

    Uwaga dotycząca bezpieczeństwa: mniejsze lub mocno skwantyzowane modele są bardziej podatne na prompt
    injection. Zdecydowanie zalecamy **duże modele** dla każdego bota, który może używać narzędzi.
    Jeśli mimo to chcesz małych modeli, włącz sandboxing i ścisłe allowlisty narzędzi.

    Dokumentacja: [Ollama](/pl/providers/ollama), [Local models](/pl/gateway/local-models),
    [Model providers](/pl/concepts/model-providers), [Security](/pl/gateway/security),
    [Sandboxing](/pl/gateway/sandboxing).

  </Accordion>

  <Accordion title="Jakich modeli używają OpenClaw, Flawd i Krill?">
    - Te wdrożenia mogą się różnić i zmieniać w czasie; nie ma stałej rekomendacji dotyczącej dostawcy.
    - Sprawdź bieżące ustawienie środowiska uruchomieniowego na każdym Gateway przez `openclaw models status`.
    - Dla agentów wrażliwych na bezpieczeństwo / z włączonymi narzędziami używaj najmocniejszego dostępnego modelu najnowszej generacji.
  </Accordion>

  <Accordion title="Jak przełączać modele w locie (bez restartu)?">
    Użyj polecenia `/model` jako samodzielnej wiadomości:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    To są wbudowane aliasy. Własne aliasy można dodać przez `agents.defaults.models`.

    Możesz wyświetlić dostępne modele przez `/model`, `/model list` lub `/model status`.

    `/model` (i `/model list`) pokazuje kompaktowy, numerowany wybór. Wybierz numerem:

    ```
    /model 3
    ```

    Możesz też wymusić określony profil uwierzytelniania dla dostawcy (per sesja):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Wskazówka: `/model status` pokazuje, który agent jest aktywny, który plik `auth-profiles.json` jest używany i który profil uwierzytelniania zostanie wypróbowany jako następny.
    Pokazuje też skonfigurowany endpoint dostawcy (`baseUrl`) i tryb API (`api`), gdy są dostępne.

    **Jak odpiąć profil ustawiony przez @profile?**

    Uruchom `/model` ponownie **bez** sufiksu `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Jeśli chcesz wrócić do domyślnego, wybierz go z `/model` (albo wyślij `/model <default provider/model>`).
    Użyj `/model status`, aby potwierdzić, który profil uwierzytelniania jest aktywny.

  </Accordion>

  <Accordion title="Czy mogę używać GPT 5.2 do codziennych zadań, a Codex 5.3 do kodowania?">
    Tak. Ustaw jeden jako domyślny i przełączaj w razie potrzeby:

    - **Szybkie przełączenie (per sesja):** `/model gpt-5.4` do codziennych zadań, `/model openai-codex/gpt-5.4` do kodowania z Codex OAuth.
    - **Domyślny + przełączanie:** ustaw `agents.defaults.model.primary` na `openai/gpt-5.4`, a potem przełączaj na `openai-codex/gpt-5.4` przy kodowaniu (albo odwrotnie).
    - **Sub-agenci:** kieruj zadania związane z kodowaniem do sub-agentów z innym modelem domyślnym.

    Zobacz [Models](/pl/concepts/models) i [Slash commands](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Jak skonfigurować fast mode dla GPT 5.4?">
    Użyj przełącznika sesji albo domyślnego ustawienia w konfiguracji:

    - **Per sesja:** wyślij `/fast on`, gdy sesja używa `openai/gpt-5.4` lub `openai-codex/gpt-5.4`.
    - **Domyślnie per model:** ustaw `agents.defaults.models["openai/gpt-5.4"].params.fastMode` na `true`.
    - **Także dla Codex OAuth:** jeśli używasz również `openai-codex/gpt-5.4`, ustaw tam tę samą flagę.

    Przykład:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    W przypadku OpenAI fast mode mapuje się na `service_tier = "priority"` w obsługiwanych natywnych żądaniach Responses. Sesyjne nadpisania `/fast` mają wyższy priorytet niż ustawienia domyślne w konfiguracji.

    Zobacz [Thinking and fast mode](/pl/tools/thinking) i [OpenAI fast mode](/pl/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Dlaczego widzę „Model ... is not allowed”, a potem brak odpowiedzi?'>
    Jeśli ustawione jest `agents.defaults.models`, staje się ono **allowlistą** dla `/model` i wszelkich
    nadpisań sesji. Wybranie modelu, którego nie ma na tej liście, zwraca:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Ten błąd jest zwracany **zamiast** zwykłej odpowiedzi. Naprawa: dodaj model do
    `agents.defaults.models`, usuń allowlistę albo wybierz model z `/model list`.

  </Accordion>

  <Accordion title='Dlaczego widzę „Unknown model: minimax/MiniMax-M2.7”?'>
    Oznacza to, że **dostawca nie jest skonfigurowany** (nie znaleziono konfiguracji dostawcy MiniMax ani
    profilu uwierzytelniania), więc model nie może zostać rozpoznany.

    Lista kontrolna naprawy:

    1. Zaktualizuj do bieżącego wydania OpenClaw (albo uruchamiaj ze źródłowego `main`), a następnie zrestartuj Gateway.
    2. Upewnij się, że MiniMax jest skonfigurowany (kreator lub JSON) albo że istnieje uwierzytelnianie MiniMax
       w env/profilach uwierzytelniania, aby pasujący dostawca mógł zostać wstrzyknięty
       (`MINIMAX_API_KEY` dla `minimax`, `MINIMAX_OAUTH_TOKEN` albo zapisane OAuth MiniMax
       dla `minimax-portal`).
    3. Użyj dokładnego identyfikatora modelu (uwzględniającego wielkość liter) dla swojej ścieżki uwierzytelniania:
       `minimax/MiniMax-M2.7` albo `minimax/MiniMax-M2.7-highspeed` dla konfiguracji
       z kluczem API, albo `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` dla konfiguracji OAuth.
    4. Uruchom:

       ```bash
       openclaw models list
       ```

       i wybierz z listy (albo `/model list` na czacie).

    Zobacz [MiniMax](/pl/providers/minimax) i [Models](/pl/concepts/models).

  </Accordion>

  <Accordion title="Czy mogę używać MiniMax jako domyślnego, a OpenAI do złożonych zadań?">
    Tak. Używaj **MiniMax jako domyślnego** i przełączaj modele **per sesja**, kiedy to potrzebne.
    Fallbacki są dla **błędów**, a nie dla „trudnych zadań”, więc użyj `/model` albo oddzielnego agenta.

    **Opcja A: przełączanie per sesja**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Następnie:

    ```
    /model gpt
    ```

    **Opcja B: oddzielni agenci**

    - Agent A domyślnie: MiniMax
    - Agent B domyślnie: OpenAI
    - Kieruj według agenta albo użyj `/agent`, aby się przełączyć

    Dokumentacja: [Models](/pl/concepts/models), [Multi-Agent Routing](/pl/concepts/multi-agent), [MiniMax](/pl/providers/minimax), [OpenAI](/pl/providers/openai).

  </Accordion>

  <Accordion title="Czy `opus` / `sonnet` / `gpt` to wbudowane skróty?">
    Tak. OpenClaw dostarcza kilka domyślnych skrótów (stosowanych tylko wtedy, gdy model istnieje w `agents.defaults.models`):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Jeśli ustawisz własny alias o tej samej nazwie, twoja wartość ma pierwszeństwo.

  </Accordion>

  <Accordion title="Jak zdefiniować / nadpisać skróty modeli (aliasy)?">
    Aliasy pochodzą z `agents.defaults.models.<modelId>.alias`. Przykład:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Wtedy `/model sonnet` (albo `/<alias>`, gdy jest obsługiwane) rozwiązuje się do tego identyfikatora modelu.

  </Accordion>

  <Accordion title="Jak dodać modele od innych dostawców, takich jak OpenRouter lub Z.AI?">
    OpenRouter (płatność za token; wiele modeli):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (modele GLM):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    Jeśli odwołasz się do `provider/model`, ale brakuje wymaganego klucza dostawcy, otrzymasz błąd uwierzytelniania w czasie działania (np. `No API key found for provider "zai"`).

    **Po dodaniu nowego agenta pojawia się „No API key found for provider”**

    Zwykle oznacza to, że **nowy agent** ma pusty magazyn uwierzytelniania. Uwierzytelnianie jest per agent i
    jest przechowywane w:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    Opcje naprawy:

    - Uruchom `openclaw agents add <id>` i skonfiguruj uwierzytelnianie w kreatorze.
    - Albo skopiuj `auth-profiles.json` z `agentDir` głównego agenta do `agentDir` nowego agenta.

    **Nie** używaj tego samego `agentDir` dla wielu agentów; powoduje to kolizje uwierzytelniania i sesji.

  </Accordion>
</AccordionGroup>

## Failover modeli i „All models failed”

<AccordionGroup>
  <Accordion title="Jak działa failover?">
    Failover działa w dwóch etapach:

    1. **Rotacja profili uwierzytelniania** w obrębie tego samego dostawcy.
    2. **Fallback modelu** do następnego modelu w `agents.defaults.model.fallbacks`.

    Do profili kończących się błędami stosowane są cooldowny (wykładniczy backoff), dzięki czemu OpenClaw może nadal odpowiadać nawet wtedy, gdy dostawca ma rate limit albo chwilowo zawodzi.

    Bucket rate limit obejmuje coś więcej niż zwykłe odpowiedzi `429`. OpenClaw
    traktuje też komunikaty takie jak `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted` oraz okresowe
    limity okna użycia (`weekly/monthly limit reached`) jako
    kwalifikujące się do failover rate limity.

    Niektóre odpowiedzi wyglądające na związane z rozliczeniami nie mają kodu `402`, a niektóre odpowiedzi HTTP `402`
    również pozostają w tym przejściowym bucketcie. Jeśli dostawca zwraca
    jawny tekst rozliczeniowy przy `401` lub `403`, OpenClaw nadal może zachować to
    w ścieżce rozliczeniowej, ale dopasowania tekstu specyficzne dla dostawcy pozostają ograniczone do
    dostawcy, który jest ich właścicielem (na przykład OpenRouter `Key limit exceeded`). Jeśli komunikat `402`
    wygląda raczej jak okno użycia możliwe do ponowienia próby albo
    limit wydatków organizacji/workspace (`daily limit reached, resets tomorrow`,
    `organization spending limit exceeded`), OpenClaw traktuje go jako
    `rate_limit`, a nie długotrwałe wyłączenie z powodów rozliczeniowych.

    Błędy przepełnienia kontekstu są inne: sygnatury takie jak
    `request_too_large`, `input exceeds the maximum number of tokens`,
    `input token count exceeds the maximum number of input tokens`,
    `input is too long for the model` albo `ollama error: context length
    exceeded` pozostają na ścieżce Compaction/ponownej próby zamiast przechodzić do fallbacku modelu.

    Generyczny tekst błędu serwera jest celowo węższy niż „wszystko z
    unknown/error w środku”. OpenClaw traktuje jako kwalifikujące się do failover
    sygnały timeout/przeciążenia zależne od kontekstu dostawcy, takie jak gołe
    `An unknown error occurred` w Anthropic, gołe `Provider returned error` w OpenRouter,
    błędy stop-reason takie jak `Unhandled stop reason:
    error`, ładunki JSON `api_error` z przejściowym tekstem błędu serwera
    (`internal server error`, `unknown error, 520`, `upstream error`, `backend
    error`) oraz błędy zajętości dostawcy, takie jak `ModelNotReadyException`, gdy kontekst
    dostawcy pasuje.
    Ogólny wewnętrzny tekst fallbacku, taki jak `LLM request failed with an unknown
    error.`, pozostaje konserwatywny i sam z siebie nie wywołuje fallbacku modelu.

  </Accordion>

  <Accordion title='Co oznacza „No credentials found for profile anthropic:default”?'>
    Oznacza to, że system próbował użyć identyfikatora profilu uwierzytelniania `anthropic:default`, ale nie mógł znaleźć poświadczeń dla niego w oczekiwanym magazynie uwierzytelniania.

    **Lista kontrolna naprawy:**

    - **Potwierdź, gdzie znajdują się profile uwierzytelniania** (nowe vs starsze ścieżki)
      - Bieżąca: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - Starsza: `~/.openclaw/agent/*` (migrowana przez `openclaw doctor`)
    - **Potwierdź, że twoja zmienna środowiskowa jest załadowana przez Gateway**
      - Jeśli ustawisz `ANTHROPIC_API_KEY` w swojej powłoce, ale uruchamiasz Gateway przez systemd/launchd, może jej nie dziedziczyć. Umieść ją w `~/.openclaw/.env` albo włącz `env.shellEnv`.
    - **Upewnij się, że edytujesz właściwego agenta**
      - Konfiguracje multi-agent oznaczają, że może istnieć wiele plików `auth-profiles.json`.
    - **Sprawdzenie podstawowe stanu modelu/uwierzytelniania**
      - Użyj `openclaw models status`, aby zobaczyć skonfigurowane modele i to, czy dostawcy są uwierzytelnieni.

    **Lista kontrolna naprawy dla „No credentials found for profile anthropic”**

    Oznacza to, że uruchomienie jest przypięte do profilu uwierzytelniania Anthropic, ale Gateway
    nie może go znaleźć w swoim magazynie uwierzytelniania.

    - **Użyj Claude CLI**
      - Uruchom `openclaw models auth login --provider anthropic --method cli --set-default` na hoście Gateway.
    - **Jeśli zamiast tego chcesz używać klucza API**
      - Umieść `ANTHROPIC_API_KEY` w `~/.openclaw/.env` na **hoście Gateway**.
      - Wyczyść wszelką przypiętą kolejność wymuszającą brakujący profil:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **Potwierdź, że uruchamiasz polecenia na hoście Gateway**
      - W trybie zdalnym profile uwierzytelniania znajdują się na maszynie Gateway, a nie na twoim laptopie.

  </Accordion>

  <Accordion title="Dlaczego próbował też Google Gemini i nie udało się?">
    Jeśli konfiguracja twojego modelu obejmuje Google Gemini jako fallback (albo przełączyłeś się na skrót Gemini), OpenClaw spróbuje go podczas fallbacku modelu. Jeśli nie skonfigurowałeś poświadczeń Google, zobaczysz `No API key found for provider "google"`.

    Naprawa: albo podaj uwierzytelnianie Google, albo usuń/unikaj modeli Google w `agents.defaults.model.fallbacks` / aliasach, aby fallback tam nie kierował.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    Przyczyna: historia sesji zawiera **bloki thinking bez podpisów** (często z
    przerwanego/niepełnego streamu). Google Antigravity wymaga podpisów dla bloków thinking.

    Naprawa: OpenClaw usuwa teraz niepodpisane bloki thinking dla Google Antigravity Claude. Jeśli nadal się pojawia, rozpocznij **nową sesję** albo ustaw `/thinking off` dla tego agenta.

  </Accordion>
</AccordionGroup>

## Profile uwierzytelniania: czym są i jak nimi zarządzać

Powiązane: [/concepts/oauth](/pl/concepts/oauth) (przepływy OAuth, przechowywanie tokenów, wzorce dla wielu kont)

<AccordionGroup>
  <Accordion title="Czym jest profil uwierzytelniania?">
    Profil uwierzytelniania to nazwany rekord poświadczeń (OAuth lub klucz API) powiązany z dostawcą. Profile znajdują się w:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="Jakie są typowe identyfikatory profili?">
    OpenClaw używa identyfikatorów z prefiksem dostawcy, takich jak:

    - `anthropic:default` (częste, gdy nie istnieje tożsamość e-mail)
    - `anthropic:<email>` dla tożsamości OAuth
    - własne identyfikatory, które wybierzesz (np. `anthropic:work`)

  </Accordion>

  <Accordion title="Czy mogę sterować, który profil uwierzytelniania jest próbowany jako pierwszy?">
    Tak. Konfiguracja obsługuje opcjonalne metadane profili i kolejność per dostawca (`auth.order.<provider>`). To **nie** przechowuje sekretów; mapuje identyfikatory na dostawcę/tryb i ustawia kolejność rotacji.

    OpenClaw może tymczasowo pominąć profil, jeśli jest w krótkim **cooldownie** (rate limity/timeouty/błędy uwierzytelniania) albo w dłuższym stanie **disabled** (rozliczenia/niewystarczające środki). Aby to sprawdzić, uruchom `openclaw models status --json` i sprawdź `auth.unusableProfiles`. Strojenie: `auth.cooldowns.billingBackoffHours*`.

    Cooldowny rate limit mogą być ograniczone do modelu. Profil, który jest w cooldownie
    dla jednego modelu, może nadal być używalny dla siostrzanego modelu u tego samego dostawcy,
    podczas gdy okna billing/disabled nadal blokują cały profil.

    Możesz też ustawić nadpisanie kolejności **per agent** (przechowywane w `auth-state.json` tego agenta) przez CLI:

    ```bash
    # Domyślnie używa skonfigurowanego agenta domyślnego (pomiń --agent)
    openclaw models auth order get --provider anthropic

    # Zablokuj rotację do jednego profilu (próbuj tylko tego jednego)
    openclaw models auth order set --provider anthropic anthropic:default

    # Albo ustaw jawną kolejność (fallback w obrębie dostawcy)
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # Wyczyść nadpisanie (powrót do config auth.order / round-robin)
    openclaw models auth order clear --provider anthropic
    ```

    Aby wskazać konkretnego agenta:

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    Aby sprawdzić, co faktycznie będzie próbowane, użyj:

    ```bash
    openclaw models status --probe
    ```

    Jeśli zapisany profil jest pominięty w jawnej kolejności, sonda zgłasza
    `excluded_by_auth_order` dla tego profilu zamiast próbować go po cichu.

  </Accordion>

  <Accordion title="OAuth vs klucz API — jaka jest różnica?">
    OpenClaw obsługuje oba podejścia:

    - **OAuth** często wykorzystuje dostęp subskrypcyjny (tam, gdzie ma to zastosowanie).
    - **Klucze API** używają rozliczania pay-per-token.

    Kreator jawnie obsługuje Anthropic Claude CLI, OpenAI Codex OAuth i klucze API.

  </Accordion>
</AccordionGroup>

## Gateway: porty, „already running” i tryb zdalny

<AccordionGroup>
  <Accordion title="Jakiego portu używa Gateway?">
    `gateway.port` kontroluje pojedynczy multipleksowany port dla WebSocket + HTTP (Control UI, hooki itd.).

    Priorytet:

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
    ```

  </Accordion>

  <Accordion title='Dlaczego `openclaw gateway status` pokazuje „Runtime: running”, ale „RPC probe: failed”?'>
    Ponieważ „running” to widok **supervisora** (launchd/systemd/schtasks). Sonda RPC oznacza, że CLI faktycznie łączy się z Gateway WebSocket i wywołuje `status`.

    Użyj `openclaw gateway status` i ufaj tym liniom:

    - `Probe target:` (URL, którego sonda faktycznie użyła)
    - `Listening:` (co faktycznie nasłuchuje na porcie)
    - `Last gateway error:` (częsta przyczyna źródłowa, gdy proces żyje, ale port nie nasłuchuje)

  </Accordion>

  <Accordion title='Dlaczego `openclaw gateway status` pokazuje różne wartości dla „Config (cli)” i „Config (service)”?'>
    Edytujesz jeden plik konfiguracyjny, podczas gdy usługa działa na innym (często jest to niedopasowanie `--profile` / `OPENCLAW_STATE_DIR`).

    Naprawa:

    ```bash
    openclaw gateway install --force
    ```

    Uruchom to z tego samego `--profile` / środowiska, którego ma używać usługa.

  </Accordion>

  <Accordion title='Co oznacza „another gateway instance is already listening”?'>
    OpenClaw wymusza blokadę środowiska uruchomieniowego przez natychmiastowe powiązanie nasłuchiwania WebSocket przy starcie (domyślnie `ws://127.0.0.1:18789`). Jeśli powiązanie nie powiedzie się z `EADDRINUSE`, zgłaszany jest `GatewayLockError`, wskazujący, że inna instancja już nasłuchuje.

    Naprawa: zatrzymaj drugą instancję, zwolnij port albo uruchom z `openclaw gateway --port <port>`.

  </Accordion>

  <Accordion title="Jak uruchomić OpenClaw w trybie zdalnym (klient łączy się z Gateway działającym gdzie indziej)?">
    Ustaw `gateway.mode: "remote"` i wskaż zdalny URL WebSocket, opcjonalnie z poświadczeniami zdalnymi opartymi na wspólnym sekrecie:

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    Uwagi:

    - `openclaw gateway` uruchamia się tylko wtedy, gdy `gateway.mode` ma wartość `local` (albo przekażesz flagę nadpisującą).
    - Aplikacja macOS obserwuje plik konfiguracji i przełącza tryby na żywo, gdy te wartości się zmieniają.
    - `gateway.remote.token` / `.password` to tylko poświadczenia zdalne po stronie klienta; same w sobie nie włączają lokalnego uwierzytelniania Gateway.

  </Accordion>

  <Accordion title='Control UI pokazuje „unauthorized” (albo stale się przełącza w reconnect). Co teraz?'>
    Ścieżka uwierzytelniania Gateway i metoda uwierzytelniania UI nie pasują do siebie.

    Fakty (z kodu):

    - Control UI przechowuje token w `sessionStorage` dla bieżącej sesji karty przeglądarki i wybranego URL Gateway, więc odświeżenia w tej samej karcie nadal działają bez przywracania długotrwałego przechowywania tokenu w localStorage.
    - Przy `AUTH_TOKEN_MISMATCH` zaufani klienci mogą wykonać jedną ograniczoną ponowną próbę z użyciem pamiętanego tokenu urządzenia, gdy Gateway zwróci wskazówki do ponowienia (`canRetryWithDeviceToken=true`, `recommendedNextStep=retry_with_device_token`).
    - Ta ponowna próba z tokenem z cache używa teraz ponownie zatwierdzonych zakresów zapisanych wraz z tokenem urządzenia. Wywołania z jawnym `deviceToken` / jawnymi `scopes` nadal zachowują żądany zestaw zakresów zamiast dziedziczyć zakresy z cache.
    - Poza tą ścieżką ponowienia priorytet uwierzytelniania połączenia wygląda następująco: najpierw jawny współdzielony token/hasło, potem jawny `deviceToken`, potem zapisany token urządzenia, a na końcu token bootstrap.
    - Kontrole zakresu tokenu bootstrap są prefiksowane rolą. Wbudowana allowlista operatora dla bootstrap spełnia tylko żądania operatora; Node lub inne role niebędące operatorem nadal potrzebują zakresów pod własnym prefiksem roli.

    Naprawa:

    - Najszybciej: `openclaw dashboard` (wypisuje i kopiuje URL dashboardu, próbuje otworzyć; przy trybie headless pokazuje wskazówkę SSH).
    - Jeśli nie masz jeszcze tokenu: `openclaw doctor --generate-gateway-token`.
    - Jeśli zdalnie, najpierw utwórz tunel: `ssh -N -L 18789:127.0.0.1:18789 user@host`, a następnie otwórz `http://127.0.0.1:18789/`.
    - Tryb wspólnego sekretu: ustaw `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` albo `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`, a następnie wklej pasujący sekret w ustawieniach Control UI.
    - Tryb Tailscale Serve: upewnij się, że `gateway.auth.allowTailscale` jest włączone i że otwierasz URL Serve, a nie surowy URL loopback/tailnet, który omija nagłówki tożsamości Tailscale.
    - Tryb trusted-proxy: upewnij się, że łączysz się przez skonfigurowane, świadome tożsamości proxy inne niż loopback, a nie przez proxy loopback na tym samym hoście ani surowy URL Gateway.
    - Jeśli niedopasowanie utrzymuje się po tej jednej próbie, obróć / ponownie zatwierdź sparowany token urządzenia:
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - Jeśli to wywołanie rotate mówi, że zostało odrzucone, sprawdź dwie rzeczy:
      - sesje sparowanego urządzenia mogą obracać tylko **własne** urządzenie, chyba że mają też `operator.admin`
      - jawne wartości `--scope` nie mogą przekraczać bieżących zakresów operatora wywołującego
    - Nadal utknąłeś? Uruchom `openclaw status --all` i postępuj zgodnie z [Troubleshooting](/pl/gateway/troubleshooting). Szczegóły uwierzytelniania znajdziesz w [Dashboard](/web/dashboard).

  </Accordion>

  <Accordion title="Ustawiłem `gateway.bind tailnet`, ale nie może się powiązać i nic nie nasłuchuje">
    Powiązanie `tailnet` wybiera adres IP Tailscale z interfejsów sieciowych (100.64.0.0/10). Jeśli maszyna nie jest w Tailscale (albo interfejs nie działa), nie ma do czego się powiązać.

    Naprawa:

    - Uruchom Tailscale na tym hoście (aby miał adres 100.x), albo
    - Przełącz na `gateway.bind: "loopback"` / `"lan"`.

    Uwaga: `tailnet` jest jawne. `auto` preferuje loopback; użyj `gateway.bind: "tailnet"`, gdy chcesz powiązania tylko z tailnet.

  </Accordion>

  <Accordion title="Czy mogę uruchamiać wiele Gateway na tym samym hoście?">
    Zwykle nie — jeden Gateway może obsługiwać wiele kanałów komunikacyjnych i agentów. Używaj wielu Gateway tylko wtedy, gdy potrzebujesz redundancji (np. rescue bot) albo twardej izolacji.

    Tak, ale musisz odizolować:

    - `OPENCLAW_CONFIG_PATH` (konfiguracja per instancja)
    - `OPENCLAW_STATE_DIR` (stan per instancja)
    - `agents.defaults.workspace` (izolacja workspace)
    - `gateway.port` (unikalne porty)

    Szybka konfiguracja (zalecana):

    - Używaj `openclaw --profile <name> ...` dla każdej instancji (automatycznie tworzy `~/.openclaw-<name>`).
    - Ustaw unikalny `gateway.port` w konfiguracji każdego profilu (albo przekaż `--port` dla uruchomień ręcznych).
    - Zainstaluj usługę per profil: `openclaw --profile <name> gateway install`.

    Profile dodają też sufiksy do nazw usług (`ai.openclaw.<profile>`; starsze `com.openclaw.*`, `openclaw-gateway-<profile>.service`, `OpenClaw Gateway (<profile>)`).
    Pełny przewodnik: [Multiple gateways](/pl/gateway/multiple-gateways).

  </Accordion>

  <Accordion title='Co oznacza „invalid handshake” / kod 1008?'>
    Gateway to **serwer WebSocket** i oczekuje, że pierwszą wiadomością
    będzie ramka `connect`. Jeśli otrzyma cokolwiek innego, zamyka połączenie
    kodem **1008** (naruszenie zasad).

    Typowe przyczyny:

    - Otworzyłeś adres **HTTP** w przeglądarce (`http://...`) zamiast klienta WS.
    - Użyłeś niewłaściwego portu lub ścieżki.
    - Proxy albo tunel usunęły nagłówki uwierzytelniania albo wysłały żądanie inne niż do Gateway.

    Szybkie naprawy:

    1. Użyj adresu WS: `ws://<host>:18789` (albo `wss://...`, jeśli HTTPS).
    2. Nie otwieraj portu WS w zwykłej karcie przeglądarki.
    3. Jeśli uwierzytelnianie jest włączone, dołącz token/hasło w ramce `connect`.

    Jeśli używasz CLI albo TUI, URL powinien wyglądać tak:

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    Szczegóły protokołu: [Gateway protocol](/pl/gateway/protocol).

  </Accordion>
</AccordionGroup>

## Logowanie i debugowanie

<AccordionGroup>
  <Accordion title="Gdzie są logi?">
    Logi plikowe (ustrukturyzowane):

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    Możesz ustawić stałą ścieżkę przez `logging.file`. Poziom logów plikowych jest kontrolowany przez `logging.level`. Szczegółowość konsoli jest kontrolowana przez `--verbose` i `logging.consoleLevel`.

    Najszybsze śledzenie logów:

    ```bash
    openclaw logs --follow
    ```

    Logi usługi/supervisora (gdy Gateway działa przez launchd/systemd):

    - macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` i `gateway.err.log` (domyślnie: `~/.openclaw/logs/...`; profile używają `~/.openclaw-<profile>/logs/...`)
    - Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    Więcej informacji znajdziesz w [Troubleshooting](/pl/gateway/troubleshooting).

  </Accordion>

  <Accordion title="Jak uruchomić / zatrzymać / zrestartować usługę Gateway?">
    Użyj pomocników gateway:

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    Jeśli uruchamiasz Gateway ręcznie, `openclaw gateway --force` może przejąć port. Zobacz [Gateway](/pl/gateway).

  </Accordion>

  <Accordion title="Zamknąłem terminal w Windows — jak zrestartować OpenClaw?">
    Istnieją **dwa tryby instalacji w Windows**:

    **1) WSL2 (zalecane):** Gateway działa wewnątrz Linux.

    Otwórz PowerShell, wejdź do WSL, a następnie wykonaj restart:

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    Jeśli nigdy nie zainstalowałeś usługi, uruchom go na pierwszym planie:

    ```bash
    openclaw gateway run
    ```

    **2) Natywny Windows (niezalecane):** Gateway działa bezpośrednio w Windows.

    Otwórz PowerShell i uruchom:

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    Jeśli uruchamiasz go ręcznie (bez usługi), użyj:

    ```powershell
    openclaw gateway run
    ```

    Dokumentacja: [Windows (WSL2)](/pl/platforms/windows), [Gateway service runbook](/pl/gateway).

  </Accordion>

  <Accordion title="Gateway działa, ale odpowiedzi nigdy nie docierają. Co sprawdzić?">
    Zacznij od szybkiego sprawdzenia kondycji:

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    Typowe przyczyny:

    - Uwierzytelnianie modelu nie zostało załadowane na **hoście Gateway** (sprawdź `models status`).
    - Parowanie kanału / allowlist blokują odpowiedzi (sprawdź konfigurację kanału + logi).
    - WebChat/Dashboard jest otwarty bez właściwego tokenu.

    Jeśli działasz zdalnie, potwierdź, że tunel / połączenie Tailscale działa i że
    Gateway WebSocket jest osiągalny.

    Dokumentacja: [Channels](/pl/channels), [Troubleshooting](/pl/gateway/troubleshooting), [Remote access](/pl/gateway/remote).

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason" — co teraz?'>
    Zwykle oznacza to, że UI utracił połączenie WebSocket. Sprawdź:

    1. Czy Gateway działa? `openclaw gateway status`
    2. Czy Gateway jest zdrowy? `openclaw status`
    3. Czy UI ma właściwy token? `openclaw dashboard`
    4. Jeśli zdalnie, czy tunel / połączenie Tailscale działa?

    Następnie śledź logi:

    ```bash
    openclaw logs --follow
    ```

    Dokumentacja: [Dashboard](/web/dashboard), [Remote access](/pl/gateway/remote), [Troubleshooting](/pl/gateway/troubleshooting).

  </Accordion>

  <Accordion title="`Telegram setMyCommands` kończy się błędem. Co sprawdzić?">
    Zacznij od logów i statusu kanału:

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    Następnie dopasuj błąd:

    - `BOT_COMMANDS_TOO_MUCH`: menu Telegram ma zbyt wiele wpisów. OpenClaw już przycina je do limitu Telegram i ponawia próbę z mniejszą liczbą poleceń, ale niektóre wpisy nadal trzeba usunąć. Ogranicz polecenia pluginów/Skills/własne albo wyłącz `channels.telegram.commands.native`, jeśli nie potrzebujesz menu.
    - `TypeError: fetch failed`, `Network request for 'setMyCommands' failed!` lub podobne błędy sieciowe: jeśli jesteś na VPS albo za proxy, potwierdź, że wychodzący HTTPS jest dozwolony i że DNS działa dla `api.telegram.org`.

    Jeśli Gateway jest zdalny, upewnij się, że patrzysz na logi na hoście Gateway.

    Dokumentacja: [Telegram](/pl/channels/telegram), [Channel troubleshooting](/pl/channels/troubleshooting).

  </Accordion>

  <Accordion title="TUI nie pokazuje żadnego wyjścia. Co sprawdzić?">
    Najpierw potwierdź, że Gateway jest osiągalny i agent może działać:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    W TUI użyj `/status`, aby zobaczyć bieżący stan. Jeśli oczekujesz odpowiedzi na czacie
    kanału, upewnij się, że dostarczanie jest włączone (`/deliver on`).

    Dokumentacja: [TUI](/web/tui), [Slash commands](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Jak całkowicie zatrzymać, a potem uruchomić Gateway?">
    Jeśli zainstalowałeś usługę:

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    To zatrzymuje / uruchamia **nadzorowaną usługę** (launchd w macOS, systemd w Linux).
    Używaj tego, gdy Gateway działa w tle jako demon.

    Jeśli uruchamiasz na pierwszym planie, zatrzymaj przez Ctrl-C, a następnie:

    ```bash
    openclaw gateway run
    ```

    Dokumentacja: [Gateway service runbook](/pl/gateway).

  </Accordion>

  <Accordion title="ELI5: `openclaw gateway restart` vs `openclaw gateway`">
    - `openclaw gateway restart`: restartuje **usługę działającą w tle** (launchd/systemd).
    - `openclaw gateway`: uruchamia Gateway **na pierwszym planie** dla tej sesji terminala.

    Jeśli zainstalowałeś usługę, używaj poleceń gateway. Używaj `openclaw gateway`, gdy
    chcesz jednorazowego uruchomienia na pierwszym planie.

  </Accordion>

  <Accordion title="Najszybszy sposób, aby uzyskać więcej szczegółów, gdy coś kończy się błędem">
    Uruchom Gateway z `--verbose`, aby uzyskać bardziej szczegółowe informacje w konsoli. Następnie sprawdź plik logu pod kątem uwierzytelniania kanału, rutingu modelu i błędów RPC.
  </Accordion>
</AccordionGroup>

## Multimedia i załączniki

<AccordionGroup>
  <Accordion title="Mój Skill wygenerował obraz/PDF, ale nic nie zostało wysłane">
    Wychodzące załączniki od agenta muszą zawierać wiersz `MEDIA:<path-or-url>` (w osobnym wierszu). Zobacz [OpenClaw assistant setup](/pl/start/openclaw) i [Agent send](/pl/tools/agent-send).

    Wysyłanie przez CLI:

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    Sprawdź też:

    - Czy docelowy kanał obsługuje media wychodzące i nie jest blokowany przez allowlisty.
    - Czy plik mieści się w limitach rozmiaru dostawcy (obrazy są zmniejszane do maks. 2048 px).
    - `tools.fs.workspaceOnly=true` ogranicza wysyłanie ścieżek lokalnych do workspace, temp/media-store i plików zwalidowanych przez sandbox.
    - `tools.fs.workspaceOnly=false` pozwala `MEDIA:` wysyłać lokalne pliki hosta, które agent już może odczytać, ale tylko dla multimediów oraz bezpiecznych typów dokumentów (obrazy, audio, wideo, PDF i dokumenty Office). Zwykły tekst i pliki przypominające sekrety są nadal blokowane.

    Zobacz [Images](/pl/nodes/images).

  </Accordion>
</AccordionGroup>

## Bezpieczeństwo i kontrola dostępu

<AccordionGroup>
  <Accordion title="Czy wystawienie OpenClaw na przychodzące DM jest bezpieczne?">
    Traktuj przychodzące DM jako niezaufane dane wejściowe. Ustawienia domyślne zostały zaprojektowane tak, aby zmniejszać ryzyko:

    - Domyślne zachowanie w kanałach obsługujących DM to **pairing**:
      - Nieznani nadawcy otrzymują kod parowania; bot nie przetwarza ich wiadomości.
      - Zatwierdź przez: `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - Oczekujące żądania są ograniczone do **3 na kanał**; sprawdź `openclaw pairing list --channel <channel> [--account <id>]`, jeśli kod nie dotarł.
    - Publiczne otwarcie DM wymaga jawnego opt-in (`dmPolicy: "open"` i allowlisty `"*"`).

    Uruchom `openclaw doctor`, aby wykryć ryzykowne polityki DM.

  </Accordion>

  <Accordion title="Czy prompt injection to problem tylko dla publicznych botów?">
    Nie. Prompt injection dotyczy **niezaufanej treści**, a nie tylko tego, kto może wysłać DM do bota.
    Jeśli twój asystent odczytuje zewnętrzną treść (wyszukiwanie/pobieranie z sieci, strony w przeglądarce, e-maile,
    dokumenty, załączniki, wklejone logi), ta treść może zawierać instrukcje próbujące
    przejąć kontrolę nad modelem. Może się to zdarzyć, nawet jeśli **ty jesteś jedynym nadawcą**.

    Największe ryzyko pojawia się, gdy włączone są narzędzia: model może zostać nakłoniony do
    wycieku kontekstu lub wywoływania narzędzi w twoim imieniu. Ogranicz promień rażenia przez:

    - używanie agenta „czytelnika” tylko do odczytu lub bez narzędzi do podsumowywania niezaufanej treści
    - utrzymywanie `web_search` / `web_fetch` / `browser` wyłączonych dla agentów z włączonymi narzędziami
    - traktowanie zdekodowanego tekstu plików/dokumentów również jako niezaufanego: OpenResponses
      `input_file` oraz ekstrakcja treści z załączników multimedialnych opakowują wyodrębniony tekst w
      jawne znaczniki granic treści zewnętrznej zamiast przekazywać surowy tekst pliku
    - sandboxing i ścisłe allowlisty narzędzi

    Szczegóły: [Security](/pl/gateway/security).

  </Accordion>

  <Accordion title="Czy mój bot powinien mieć własny e-mail, konto GitHub albo numer telefonu?">
    Tak, w większości konfiguracji. Izolowanie bota przy użyciu oddzielnych kont i numerów telefonów
    zmniejsza promień rażenia, jeśli coś pójdzie nie tak. Ułatwia to też rotację
    poświadczeń lub cofanie dostępu bez wpływu na twoje osobiste konta.

    Zacznij od małej skali. Daj dostęp tylko do narzędzi i kont, których rzeczywiście potrzebujesz, i rozszerzaj go
    później, jeśli będzie to wymagane.

    Dokumentacja: [Security](/pl/gateway/security), [Pairing](/pl/channels/pairing).

  </Accordion>

  <Accordion title="Czy mogę dać mu autonomię nad moimi wiadomościami tekstowymi i czy to bezpieczne?">
    **Nie** zalecamy pełnej autonomii nad twoimi prywatnymi wiadomościami. Najbezpieczniejszy wzorzec to:

    - Utrzymuj DM w trybie **pairing** albo z ciasną allowlistą.
    - Używaj **oddzielnego numeru lub konta**, jeśli chcesz, aby pisał wiadomości w twoim imieniu.
    - Pozwól mu tworzyć szkice, a potem **zatwierdzaj przed wysłaniem**.

    Jeśli chcesz eksperymentować, rób to na dedykowanym koncie i utrzymuj izolację. Zobacz
    [Security](/pl/gateway/security).

  </Accordion>

  <Accordion title="Czy mogę używać tańszych modeli do zadań osobistego asystenta?">
    Tak, **jeśli** agent obsługuje tylko czat, a dane wejściowe są zaufane. Mniejsze warianty są
    bardziej podatne na przejmowanie instrukcji, więc unikaj ich w przypadku agentów z włączonymi narzędziami
    lub przy odczytywaniu niezaufanej treści. Jeśli musisz używać mniejszego modelu, zablokuj
    narzędzia i uruchamiaj w sandboxie. Zobacz [Security](/pl/gateway/security).
  </Accordion>

  <Accordion title="Uruchomiłem `/start` w Telegram, ale nie dostałem kodu parowania">
    Kody parowania są wysyłane **tylko** wtedy, gdy nieznany nadawca napisze do bota i
    `dmPolicy: "pairing"` jest włączone. Samo `/start` nie generuje kodu.

    Sprawdź oczekujące żądania:

    ```bash
    openclaw pairing list telegram
    ```

    Jeśli chcesz natychmiastowego dostępu, dodaj identyfikator nadawcy do allowlisty albo ustaw `dmPolicy: "open"`
    dla tego konta.

  </Accordion>

  <Accordion title="WhatsApp: czy będzie pisał do moich kontaktów? Jak działa pairing?">
    Nie. Domyślna polityka DM WhatsApp to **pairing**. Nieznani nadawcy dostają tylko kod parowania, a ich wiadomość **nie jest przetwarzana**. OpenClaw odpowiada tylko na czaty, które otrzymuje, albo na jawne wysyłki, które sam wywołasz.

    Zatwierdź parowanie przez:

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    Wyświetl oczekujące żądania:

    ```bash
    openclaw pairing list whatsapp
    ```

    Prompt kreatora dotyczący numeru telefonu: służy do ustawienia twojej **allowlisty / właściciela**, aby twoje własne DM były dozwolone. Nie jest używany do automatycznego wysyłania. Jeśli działasz na swoim prywatnym numerze WhatsApp, użyj tego numeru i włącz `channels.whatsapp.selfChatMode`.

  </Accordion>
</AccordionGroup>

## Polecenia czatu, przerywanie zadań i „to nie chce się zatrzymać”

<AccordionGroup>
  <Accordion title="Jak zatrzymać wyświetlanie wewnętrznych komunikatów systemowych na czacie?">
    Większość wewnętrznych komunikatów lub komunikatów narzędzi pojawia się tylko wtedy, gdy dla tej sesji
    włączone są **verbose**, **trace** albo **reasoning**.

    Napraw to na czacie, na którym to widzisz:

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    Jeśli nadal jest zbyt głośno, sprawdź ustawienia sesji w Control UI i ustaw verbose
    na **inherit**. Potwierdź też, że nie używasz profilu bota z ustawieniem `verboseDefault`
    ustawionym w konfiguracji na `on`.

    Dokumentacja: [Thinking and verbose](/pl/tools/thinking), [Security](/pl/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="Jak zatrzymać / anulować uruchomione zadanie?">
    Wyślij dowolny z poniższych tekstów **jako samodzielną wiadomość** (bez ukośnika):

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    To są wyzwalacze przerwania (nie polecenia slash).

    W przypadku procesów działających w tle (z narzędzia exec) możesz poprosić agenta o uruchomienie:

    ```
    process action:kill sessionId:XXX
    ```

    Przegląd poleceń slash: zobacz [Slash commands](/pl/tools/slash-commands).

    Większość poleceń musi zostać wysłana jako **samodzielna** wiadomość zaczynająca się od `/`, ale kilka skrótów (takich jak `/status`) działa też inline dla nadawców z allowlisty.

  </Accordion>

  <Accordion title='Jak wysłać wiadomość Discord z Telegram? („Cross-context messaging denied”)'>
    OpenClaw domyślnie blokuje wiadomości **między różnymi dostawcami**. Jeśli wywołanie narzędzia jest powiązane
    z Telegram, nie wyśle do Discord, chyba że jawnie na to zezwolisz.

    Włącz komunikację między dostawcami dla agenta:

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    Po edycji konfiguracji zrestartuj Gateway.

  </Accordion>

  <Accordion title='Dlaczego wygląda to tak, jakby bot „ignorował” serię szybkich wiadomości?'>
    Tryb kolejki kontroluje, jak nowe wiadomości wchodzą w interakcję z trwającym uruchomieniem. Użyj `/queue`, aby zmienić tryb:

    - `steer` - nowe wiadomości przekierowują bieżące zadanie
    - `followup` - uruchamia wiadomości jedna po drugiej
    - `collect` - grupuje wiadomości i odpowiada raz (domyślnie)
    - `steer-backlog` - przekierowuje teraz, a potem przetwarza backlog
    - `interrupt` - przerywa bieżące uruchomienie i zaczyna od nowa

    Możesz dodać opcje takie jak `debounce:2s cap:25 drop:summarize` dla trybów followup.

  </Accordion>
</AccordionGroup>

## Różne

<AccordionGroup>
  <Accordion title='Jaki jest domyślny model dla Anthropic przy użyciu klucza API?'>
    W OpenClaw poświadczenia i wybór modelu są oddzielne. Ustawienie `ANTHROPIC_API_KEY` (albo zapisanie klucza API Anthropic w profilach uwierzytelniania) włącza uwierzytelnianie, ale faktyczny model domyślny to to, co skonfigurujesz w `agents.defaults.model.primary` (na przykład `anthropic/claude-sonnet-4-6` albo `anthropic/claude-opus-4-6`). Jeśli widzisz `No credentials found for profile "anthropic:default"`, oznacza to, że Gateway nie mógł znaleźć poświadczeń Anthropic w oczekiwanym `auth-profiles.json` dla uruchomionego agenta.
  </Accordion>
</AccordionGroup>

---

Nadal utknąłeś? Zapytaj na [Discord](https://discord.com/invite/clawd) albo otwórz [dyskusję na GitHub](https://github.com/openclaw/openclaw/discussions).
