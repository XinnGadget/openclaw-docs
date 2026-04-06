---
read_when:
    - Odpowiadasz na typowe pytania wsparcia dotyczące konfiguracji, instalacji, onboardingu lub działania w czasie uruchomienia
    - Analizujesz zgłoszone przez użytkowników problemy przed głębszym debugowaniem
summary: Często zadawane pytania dotyczące konfiguracji, ustawień i używania OpenClaw
title: FAQ
x-i18n:
    generated_at: "2026-04-06T03:13:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4d6d09621c6033d580cbcf1ff46f81587d69404d6f64c8d8fd8c3f09185bb920
    source_path: help/faq.md
    workflow: 15
---

# FAQ

Szybkie odpowiedzi oraz głębsze wskazówki dotyczące rozwiązywania problemów dla rzeczywistych konfiguracji (lokalny development, VPS, multi-agent, OAuth/klucze API, failover modeli). Informacje o diagnostyce w czasie działania znajdziesz w [Rozwiązywanie problemów](/pl/gateway/troubleshooting). Pełną referencję konfiguracji znajdziesz w [Konfiguracja](/pl/gateway/configuration).

## Pierwsze 60 sekund, jeśli coś nie działa

1. **Szybki status (pierwsza kontrola)**

   ```bash
   openclaw status
   ```

   Szybkie lokalne podsumowanie: system operacyjny + aktualizacja, osiągalność gateway/service, agenci/sesje, konfiguracja dostawców + problemy w czasie działania (gdy gateway jest osiągalny).

2. **Raport do wklejenia (bezpieczny do udostępnienia)**

   ```bash
   openclaw status --all
   ```

   Diagnostyka tylko do odczytu z końcówką logu (tokeny ukryte).

3. **Stan demona + portu**

   ```bash
   openclaw gateway status
   ```

   Pokazuje środowisko wykonawcze nadzorcy względem osiągalności RPC, docelowy URL sondy oraz której konfiguracji usługa prawdopodobnie użyła.

4. **Głębokie sondy**

   ```bash
   openclaw status --deep
   ```

   Uruchamia aktywną sondę stanu gateway, w tym sondy kanałów, gdy są obsługiwane
   (wymaga osiągalnego gateway). Zobacz [Health](/pl/gateway/health).

5. **Podgląd najnowszego logu**

   ```bash
   openclaw logs --follow
   ```

   Jeśli RPC nie działa, przejdź do:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Logi plikowe są oddzielone od logów usługi; zobacz [Logowanie](/pl/logging) i [Rozwiązywanie problemów](/pl/gateway/troubleshooting).

6. **Uruchom doctora (naprawy)**

   ```bash
   openclaw doctor
   ```

   Naprawia/migruje konfigurację i stan + uruchamia kontrole kondycji. Zobacz [Doctor](/pl/gateway/doctor).

7. **Migawka gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # pokazuje docelowy URL + ścieżkę konfiguracji przy błędach
   ```

   Pobiera od działającego gateway pełną migawkę (tylko WS). Zobacz [Health](/pl/gateway/health).

## Szybki start i konfiguracja przy pierwszym uruchomieniu

<AccordionGroup>
  <Accordion title="Utknąłem, jaki jest najszybszy sposób, żeby ruszyć dalej">
    Użyj lokalnego agenta AI, który **widzi twój komputer**. To jest znacznie skuteczniejsze niż pytanie
    na Discord, ponieważ większość przypadków typu „utknąłem” to **lokalne problemy z konfiguracją lub środowiskiem**,
    których zdalni pomocnicy nie mogą sprawdzić.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Te narzędzia potrafią czytać repozytorium, uruchamiać polecenia, sprawdzać logi i pomagać naprawiać konfigurację
    na poziomie komputera (PATH, usługi, uprawnienia, pliki uwierzytelniania). Udostępnij im **pełne checkout źródeł**
    przez instalację hackable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    To instaluje OpenClaw **z checkout repozytorium git**, więc agent może czytać kod + dokumentację i
    analizować dokładnie tę wersję, której używasz. Zawsze możesz później wrócić do stable,
    ponownie uruchamiając instalator bez `--install-method git`.

    Wskazówka: poproś agenta, aby **zaplanował i nadzorował** naprawę (krok po kroku), a następnie wykonał tylko
    niezbędne polecenia. Dzięki temu zmiany są małe i łatwiejsze do audytu.

    Jeśli odkryjesz prawdziwy błąd albo poprawkę, zgłoś issue na GitHub albo wyślij PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Zacznij od tych poleceń (udostępniaj ich wyniki, gdy prosisz o pomoc):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Co robią:

    - `openclaw status`: szybka migawka kondycji gateway/agenta + podstawowa konfiguracja.
    - `openclaw models status`: sprawdza uwierzytelnianie dostawców + dostępność modeli.
    - `openclaw doctor`: weryfikuje i naprawia typowe problemy z konfiguracją/stanem.

    Inne przydatne kontrole CLI: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Szybka pętla debugowania: [Pierwsze 60 sekund, jeśli coś nie działa](#pierwsze-60-sekund-jesli-cos-nie-dziala).
    Dokumentacja instalacji: [Instalacja](/pl/install), [Flagi instalatora](/pl/install/installer), [Aktualizowanie](/pl/install/updating).

  </Accordion>

  <Accordion title="Heartbeat ciągle jest pomijany. Co oznaczają powody pominięcia?">
    Typowe powody pominięcia heartbeat:

    - `quiet-hours`: poza skonfigurowanym oknem active-hours
    - `empty-heartbeat-file`: `HEARTBEAT.md` istnieje, ale zawiera tylko pustą treść/szablon z samymi nagłówkami
    - `no-tasks-due`: tryb zadań `HEARTBEAT.md` jest aktywny, ale żaden interwał zadania jeszcze nie jest należny
    - `alerts-disabled`: cała widoczność heartbeat jest wyłączona (`showOk`, `showAlerts` i `useIndicator` są wyłączone)

    W trybie zadań znaczniki czasu należności są przesuwane dopiero po zakończeniu
    rzeczywistego przebiegu heartbeat. Pominięte uruchomienia nie oznaczają zadań jako ukończonych.

    Dokumentacja: [Heartbeat](/pl/gateway/heartbeat), [Automatyzacja i zadania](/pl/automation).

  </Accordion>

  <Accordion title="Zalecany sposób instalacji i konfiguracji OpenClaw">
    Repozytorium zaleca uruchamianie ze źródeł i użycie onboardingu:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Kreator może też automatycznie zbudować zasoby interfejsu. Po onboardingu zwykle uruchamiasz Gateway na porcie **18789**.

    Ze źródeł (współtwórcy/dev):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # przy pierwszym uruchomieniu automatycznie instaluje zależności UI
    openclaw onboard
    ```

    Jeśli nie masz jeszcze instalacji globalnej, uruchom to przez `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Jak otworzyć dashboard po onboardingu?">
    Kreator otwiera przeglądarkę z czystym adresem URL dashboardu (bez tokena) zaraz po onboardingu i wypisuje link w podsumowaniu. Zachowaj tę kartę otwartą; jeśli nie uruchomiła się automatycznie, skopiuj/wklej wypisany URL na tym samym komputerze.
  </Accordion>

  <Accordion title="Jak uwierzytelnić dashboard na localhost w porównaniu ze zdalnym hostem?">
    **Localhost (ten sam komputer):**

    - Otwórz `http://127.0.0.1:18789/`.
    - Jeśli poprosi o uwierzytelnianie shared-secret, wklej skonfigurowany token lub hasło w ustawieniach Control UI.
    - Źródło tokena: `gateway.auth.token` (lub `OPENCLAW_GATEWAY_TOKEN`).
    - Źródło hasła: `gateway.auth.password` (lub `OPENCLAW_GATEWAY_PASSWORD`).
    - Jeśli nie skonfigurowano jeszcze shared secret, wygeneruj token poleceniem `openclaw doctor --generate-gateway-token`.

    **Poza localhost:**

    - **Tailscale Serve** (zalecane): pozostaw bind loopback, uruchom `openclaw gateway --tailscale serve`, otwórz `https://<magicdns>/`. Jeśli `gateway.auth.allowTailscale` ma wartość `true`, nagłówki tożsamości spełniają uwierzytelnianie Control UI/WebSocket (bez wklejania shared secret, przy założeniu zaufanego hosta gateway); interfejsy HTTP API nadal wymagają uwierzytelniania shared-secret, chyba że celowo używasz private-ingress `none` albo HTTP auth trusted-proxy.
      Błędne równoległe próby uwierzytelnienia Serve od tego samego klienta są serializowane, zanim ogranicznik nieudanych uwierzytelnień je zarejestruje, więc druga błędna próba może już pokazać `retry later`.
    - **Tailnet bind**: uruchom `openclaw gateway --bind tailnet --token "<token>"` (albo skonfiguruj uwierzytelnianie hasłem), otwórz `http://<tailscale-ip>:18789/`, a następnie wklej odpowiadający shared secret w ustawieniach dashboardu.
    - **Identity-aware reverse proxy**: pozostaw Gateway za trusted proxy innym niż loopback, skonfiguruj `gateway.auth.mode: "trusted-proxy"`, a następnie otwórz URL proxy.
    - **Tunel SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host`, a następnie otwórz `http://127.0.0.1:18789/`. Uwierzytelnianie shared-secret nadal obowiązuje przez tunel; po wyświetleniu monitu wklej skonfigurowany token lub hasło.

    Szczegóły trybów bind i uwierzytelniania znajdziesz w [Dashboard](/web/dashboard) i [Powierzchnie webowe](/web).

  </Accordion>

  <Accordion title="Dlaczego istnieją dwie konfiguracje zatwierdzania exec dla zatwierdzeń na czacie?">
    Sterują różnymi warstwami:

    - `approvals.exec`: przekazuje prośby o zatwierdzenie do miejsc docelowych na czacie
    - `channels.<channel>.execApprovals`: sprawia, że dany kanał działa jako natywny klient zatwierdzania dla zatwierdzeń exec

    Polityka exec hosta nadal jest rzeczywistą bramką zatwierdzeń. Konfiguracja czatu kontroluje tylko,
    gdzie pojawiają się prośby o zatwierdzenie i jak ludzie mogą na nie odpowiadać.

    W większości konfiguracji **nie** potrzebujesz obu:

    - Jeśli czat już obsługuje polecenia i odpowiedzi, `/approve` w tym samym czacie działa przez współdzieloną ścieżkę.
    - Jeśli obsługiwany kanał natywny może bezpiecznie wywnioskować zatwierdzających, OpenClaw teraz automatycznie włącza natywne zatwierdzenia DM-first, gdy `channels.<channel>.execApprovals.enabled` jest nieustawione albo ma wartość `"auto"`.
    - Gdy dostępne są natywne karty/przyciski zatwierdzeń, ten natywny interfejs jest podstawową ścieżką; agent powinien dołączać ręczne polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi, że zatwierdzenia na czacie są niedostępne albo ręczne zatwierdzenie jest jedyną ścieżką.
    - Używaj `approvals.exec` tylko wtedy, gdy prośby muszą być też przekazywane do innych czatów albo jawnych pokoi operacyjnych.
    - Używaj `channels.<channel>.execApprovals.target: "channel"` albo `"both"` tylko wtedy, gdy chcesz, aby prośby o zatwierdzenie były publikowane z powrotem w pierwotnym pokoju/wątku.
    - Zatwierdzenia pluginów są znowu osobne: domyślnie używają `/approve` w tym samym czacie, opcjonalnego przekazywania `approvals.plugin`, a tylko niektóre kanały natywne dodatkowo utrzymują natywną obsługę zatwierdzania pluginów.

    Krótko: forwarding służy do routingu, a konfiguracja klienta natywnego do bogatszego UX specyficznego dla kanału.
    Zobacz [Zatwierdzenia exec](/pl/tools/exec-approvals).

  </Accordion>

  <Accordion title="Jakiego runtime potrzebuję?">
    Wymagany jest Node **>= 22**. Zalecany jest `pnpm`. Bun **nie jest zalecany** dla Gateway.
  </Accordion>

  <Accordion title="Czy działa na Raspberry Pi?">
    Tak. Gateway jest lekki — dokumentacja podaje **512 MB–1 GB RAM**, **1 rdzeń** i około **500 MB**
    miejsca na dysku jako wystarczające do użytku osobistego oraz zaznacza, że **Raspberry Pi 4 może go uruchomić**.

    Jeśli chcesz większy zapas (logi, media, inne usługi), **zalecane są 2 GB**, ale
    nie jest to twarde minimum.

    Wskazówka: mały Pi/VPS może hostować Gateway, a ty możesz sparować **nodes** na laptopie/telefonie do
    lokalnego ekranu/kamery/canvas lub wykonywania poleceń. Zobacz [Nodes](/pl/nodes).

  </Accordion>

  <Accordion title="Jakieś wskazówki dotyczące instalacji na Raspberry Pi?">
    Krótko: działa, ale spodziewaj się ostrych krawędzi.

    - Użyj systemu **64-bitowego** i utrzymuj Node >= 22.
    - Preferuj instalację **hackable (git)**, aby móc widzieć logi i szybko aktualizować.
    - Zacznij bez kanałów/Skills, a potem dodawaj je pojedynczo.
    - Jeśli trafisz na dziwne problemy binarne, zwykle jest to problem **zgodności ARM**.

    Dokumentacja: [Linux](/pl/platforms/linux), [Instalacja](/pl/install).

  </Accordion>

  <Accordion title="Zawiesza się na wake up my friend / onboarding nie chce się zakończyć. Co teraz?">
    Ten ekran zależy od tego, czy Gateway jest osiągalny i uwierzytelniony. TUI automatycznie wysyła też
    „Wake up, my friend!” przy pierwszym hatch. Jeśli widzisz ten wiersz **bez odpowiedzi**
    i liczba tokenów pozostaje 0, agent nigdy się nie uruchomił.

    1. Uruchom ponownie Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Sprawdź status + uwierzytelnianie:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Jeśli nadal się zawiesza, uruchom:

    ```bash
    openclaw doctor
    ```

    Jeśli Gateway jest zdalny, upewnij się, że tunel/połączenie Tailscale działa i że UI
    wskazuje właściwy Gateway. Zobacz [Dostęp zdalny](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Czy mogę przenieść swoją konfigurację na nowy komputer (Mac mini) bez ponownego onboardingu?">
    Tak. Skopiuj **katalog stanu** i **workspace**, a następnie uruchom Doctor raz. To
    zachowuje bota „dokładnie takim samym” (pamięć, historię sesji, uwierzytelnianie i
    stan kanałów), o ile skopiujesz **obie** lokalizacje:

    1. Zainstaluj OpenClaw na nowym komputerze.
    2. Skopiuj `$OPENCLAW_STATE_DIR` (domyślnie: `~/.openclaw`) ze starego komputera.
    3. Skopiuj swój workspace (domyślnie: `~/.openclaw/workspace`).
    4. Uruchom `openclaw doctor` i zrestartuj usługę Gateway.

    To zachowuje konfigurację, profile uwierzytelniania, poświadczenia WhatsApp, sesje i pamięć. Jeśli jesteś
    w trybie zdalnym, pamiętaj, że host gateway posiada magazyn sesji i workspace.

    **Ważne:** jeśli tylko commitujesz/pushujesz swój workspace do GitHub, wykonujesz
    kopię zapasową **pamięci + plików bootstrap**, ale **nie** historii sesji ani uwierzytelniania. One żyją
    w `~/.openclaw/` (na przykład `~/.openclaw/agents/<agentId>/sessions/`).

    Powiązane: [Migracja](/pl/install/migrating), [Gdzie rzeczy są przechowywane na dysku](#gdzie-rzeczy-sa-przechowywane-na-dysku),
    [Workspace agenta](/pl/concepts/agent-workspace), [Doctor](/pl/gateway/doctor),
    [Tryb zdalny](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Gdzie mogę zobaczyć, co jest nowe w najnowszej wersji?">
    Sprawdź changelog na GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Najnowsze wpisy są na górze. Jeśli górna sekcja jest oznaczona jako **Unreleased**, następna sekcja z datą
    to ostatnia wydana wersja. Wpisy są pogrupowane według **Highlights**, **Changes** i
    **Fixes** (oraz sekcji docs/innych, gdy to potrzebne).

  </Accordion>

  <Accordion title="Nie mogę otworzyć docs.openclaw.ai (błąd SSL)">
    Niektóre połączenia Comcast/Xfinity błędnie blokują `docs.openclaw.ai` przez Xfinity
    Advanced Security. Wyłącz tę funkcję albo dodaj `docs.openclaw.ai` do allowlisty, a potem spróbuj ponownie.
    Pomóż nam to odblokować, zgłaszając tutaj: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Jeśli nadal nie możesz otworzyć strony, dokumentacja jest mirrorowana na GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Różnica między stable a beta">
    **Stable** i **beta** to **npm dist-tags**, a nie osobne linie kodu:

    - `latest` = stable
    - `beta` = wczesna kompilacja do testów

    Zwykle wydanie stable trafia najpierw na **beta**, a następnie jawny
    krok promowania przenosi tę samą wersję do `latest`. Maintainerzy mogą też
    publikować bezpośrednio do `latest`, gdy jest to potrzebne. Dlatego beta i stable mogą
    wskazywać na **tę samą wersję** po promowaniu.

    Zobacz, co się zmieniło:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Instalacyjne one-linery i różnicę między beta i dev znajdziesz w akordeonie poniżej.

  </Accordion>

  <Accordion title="Jak zainstalować wersję beta i czym różni się beta od dev?">
    **Beta** to npm dist-tag `beta` (po promowaniu może odpowiadać `latest`).
    **Dev** to ruchoma głowa `main` (git); po publikacji używa npm dist-tag `dev`.

    One-linery (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Instalator Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Więcej szczegółów: [Kanały developmentu](/pl/install/development-channels) i [Flagi instalatora](/pl/install/installer).

  </Accordion>

  <Accordion title="Jak wypróbować najnowsze bity?">
    Dwie opcje:

    1. **Kanał dev (checkout git):**

    ```bash
    openclaw update --channel dev
    ```

    To przełącza na gałąź `main` i aktualizuje ze źródeł.

    2. **Instalacja hackable (ze strony instalatora):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    To daje lokalne repozytorium, które możesz edytować, a potem aktualizować przez git.

    Jeśli wolisz ręcznie wykonać czysty clone, użyj:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Dokumentacja: [Aktualizacja](/cli/update), [Kanały developmentu](/pl/install/development-channels),
    [Instalacja](/pl/install).

  </Accordion>

  <Accordion title="Jak długo zwykle trwa instalacja i onboarding?">
    Orientacyjnie:

    - **Instalacja:** 2–5 minut
    - **Onboarding:** 5–15 minut, zależnie od liczby konfigurowanych kanałów/modeli

    Jeśli się zawiesi, użyj [Zawieszony instalator](#szybki-start-i-konfiguracja-przy-pierwszym-uruchomieniu)
    oraz szybkiej pętli debugowania z [Utknąłem](#szybki-start-i-konfiguracja-przy-pierwszym-uruchomieniu).

  </Accordion>

  <Accordion title="Instalator się zawiesił? Jak uzyskać więcej informacji?">
    Uruchom ponownie instalator z **szczegółowym wyjściem**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Instalacja beta z verbose:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Dla instalacji hackable (git):

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

    Więcej opcji: [Flagi instalatora](/pl/install/installer).

  </Accordion>

  <Accordion title="Instalacja na Windows mówi git not found albo openclaw not recognized">
    Dwa typowe problemy w Windows:

    **1) błąd npm spawn git / git not found**

    - Zainstaluj **Git for Windows** i upewnij się, że `git` jest w PATH.
    - Zamknij i otwórz ponownie PowerShell, a potem uruchom instalator ponownie.

    **2) openclaw is not recognized po instalacji**

    - Twój globalny katalog bin npm nie jest w PATH.
    - Sprawdź ścieżkę:

      ```powershell
      npm config get prefix
      ```

    - Dodaj ten katalog do PATH użytkownika (w Windows nie potrzeba sufiksu `\bin`; na większości systemów jest to `%AppData%\npm`).
    - Zamknij i otwórz ponownie PowerShell po aktualizacji PATH.

    Jeśli chcesz możliwie najgładszej konfiguracji Windows, użyj **WSL2** zamiast natywnego Windows.
    Dokumentacja: [Windows](/pl/platforms/windows).

  </Accordion>

  <Accordion title="Wyjście exec w Windows pokazuje zniekształcony chiński tekst — co mam zrobić?">
    Zwykle jest to niedopasowanie strony kodowej konsoli w natywnych powłokach Windows.

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

    Następnie zrestartuj Gateway i ponów polecenie:

    ```powershell
    openclaw gateway restart
    ```

    Jeśli nadal odtwarzasz ten problem na najnowszym OpenClaw, śledź/zgłoś go tutaj:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Dokumentacja nie odpowiedziała na moje pytanie — jak uzyskać lepszą odpowiedź?">
    Użyj instalacji **hackable (git)**, aby mieć lokalnie pełne źródła i dokumentację, a potem zapytaj
    swojego bota (albo Claude/Codex) _z tego folderu_, aby mógł czytać repozytorium i odpowiadać precyzyjnie.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Więcej szczegółów: [Instalacja](/pl/install) i [Flagi instalatora](/pl/install/installer).

  </Accordion>

  <Accordion title="Jak zainstalować OpenClaw na Linux?">
    Krótka odpowiedź: postępuj według przewodnika dla Linux, a następnie uruchom onboarding.

    - Szybka ścieżka Linux + instalacja usługi: [Linux](/pl/platforms/linux).
    - Pełny przewodnik: [Pierwsze kroki](/pl/start/getting-started).
    - Instalator + aktualizacje: [Instalacja i aktualizacje](/pl/install/updating).

  </Accordion>

  <Accordion title="Jak zainstalować OpenClaw na VPS?">
    Każdy Linux VPS będzie działał. Zainstaluj na serwerze, a potem używaj SSH/Tailscale, aby dotrzeć do Gateway.

    Przewodniki: [exe.dev](/pl/install/exe-dev), [Hetzner](/pl/install/hetzner), [Fly.io](/pl/install/fly).
    Dostęp zdalny: [Gateway remote](/pl/gateway/remote).

  </Accordion>

  <Accordion title="Gdzie są przewodniki instalacji w chmurze / na VPS?">
    Utrzymujemy **hub hostingu** z typowymi dostawcami. Wybierz jednego i postępuj według przewodnika:

    - [Hosting VPS](/pl/vps) (wszyscy dostawcy w jednym miejscu)
    - [Fly.io](/pl/install/fly)
    - [Hetzner](/pl/install/hetzner)
    - [exe.dev](/pl/install/exe-dev)

    Jak to działa w chmurze: **Gateway działa na serwerze**, a ty uzyskujesz do niego dostęp
    z laptopa/telefonu przez Control UI (albo Tailscale/SSH). Twój stan + workspace
    żyją na serwerze, więc traktuj host jako źródło prawdy i twórz jego kopie zapasowe.

    Możesz sparować **nodes** (Mac/iOS/Android/headless) z tym chmurowym Gateway, aby uzyskać dostęp do
    lokalnego ekranu/kamery/canvas lub uruchamiać polecenia na laptopie przy jednoczesnym trzymaniu
    Gateway w chmurze.

    Hub: [Platformy](/pl/platforms). Dostęp zdalny: [Gateway remote](/pl/gateway/remote).
    Nodes: [Nodes](/pl/nodes), [CLI nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Czy mogę poprosić OpenClaw, żeby zaktualizował się sam?">
    Krótka odpowiedź: **możliwe, ale niezalecane**. Przepływ aktualizacji może zrestartować
    Gateway (co zrywa aktywną sesję), może wymagać czystego checkout git i
    może prosić o potwierdzenie. Bezpieczniej: uruchamiaj aktualizacje z powłoki jako operator.

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

    Dokumentacja: [Aktualizacja](/cli/update), [Aktualizowanie](/pl/install/updating).

  </Accordion>

  <Accordion title="Co właściwie robi onboarding?">
    `openclaw onboard` to zalecana ścieżka konfiguracji. W **trybie lokalnym** przeprowadza przez:

    - **Konfigurację modelu/uwierzytelniania** (OAuth dostawcy, klucze API, legacy setup-token Anthropic oraz opcje modeli lokalnych, takie jak LM Studio)
    - Lokalizację **workspace** + pliki bootstrap
    - **Ustawienia Gateway** (bind/port/auth/tailscale)
    - **Kanały** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage oraz bundled channel plugins, takie jak QQ Bot)
    - **Instalację demona** (LaunchAgent na macOS; jednostka użytkownika systemd na Linux/WSL2)
    - **Kontrole kondycji** i wybór **Skills**

    Ostrzega też, jeśli skonfigurowany model jest nieznany lub brakuje uwierzytelniania.

  </Accordion>

  <Accordion title="Czy potrzebuję subskrypcji Claude lub OpenAI, żeby tego używać?">
    Nie. Możesz uruchamiać OpenClaw z użyciem **kluczy API** (Anthropic/OpenAI/innych) albo z
    **całkowicie lokalnymi modelami**, aby dane pozostawały na twoim urządzeniu. Subskrypcje (Claude
    Pro/Max lub OpenAI Codex) to opcjonalne sposoby uwierzytelniania tych dostawców.

    W przypadku Anthropic w OpenClaw praktyczny podział wygląda tak:

    - **Klucz API Anthropic**: zwykłe rozliczanie API Anthropic
    - **Uwierzytelnianie subskrypcją Claude w OpenClaw**: Anthropic poinformował użytkowników OpenClaw
      **4 kwietnia 2026 o 12:00 PM PT / 8:00 PM BST**, że wymaga to
      **Extra Usage** rozliczanego osobno od subskrypcji

    Nasze lokalne reprodukcje pokazują też, że `claude -p --append-system-prompt ...` może
    trafić na tę samą blokadę Extra Usage, gdy dołączony prompt identyfikuje
    OpenClaw, podczas gdy ten sam ciąg promptu **nie** odtwarza tej blokady na
    ścieżce Anthropic SDK + klucz API. OpenAI Codex OAuth jest jawnie
    obsługiwany dla zewnętrznych narzędzi takich jak OpenClaw.

    OpenClaw obsługuje też inne hostowane opcje w stylu subskrypcyjnym, w tym
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan** oraz
    **Z.AI / GLM Coding Plan**.

    Dokumentacja: [Anthropic](/pl/providers/anthropic), [OpenAI](/pl/providers/openai),
    [Qwen Cloud](/pl/providers/qwen),
    [MiniMax](/pl/providers/minimax), [GLM Models](/pl/providers/glm),
    [Modele lokalne](/pl/gateway/local-models), [Modele](/pl/concepts/models).

  </Accordion>

  <Accordion title="Czy mogę używać subskrypcji Claude Max bez klucza API?">
    Tak, ale traktuj to jako **uwierzytelnianie subskrypcją Claude z Extra Usage**.

    Subskrypcje Claude Pro/Max nie zawierają klucza API. W OpenClaw oznacza to,
    że obowiązuje informacja Anthropic o rozliczaniu specyficznym dla OpenClaw: ruch
    subskrypcyjny wymaga **Extra Usage**. Jeśli chcesz używać ruchu Anthropic bez
    tej ścieżki Extra Usage, użyj zamiast tego klucza API Anthropic.

  </Accordion>

  <Accordion title="Czy obsługujecie uwierzytelnianie subskrypcją Claude (Claude Pro lub Max)?">
    Tak, ale obecnie obsługiwana interpretacja jest następująca:

    - Anthropic w OpenClaw z subskrypcją oznacza **Extra Usage**
    - Anthropic w OpenClaw bez tej ścieżki oznacza **klucz API**

    Anthropic setup-token nadal jest dostępny jako legacy/ręczna ścieżka OpenClaw,
    i nadal obowiązuje informacja Anthropic o rozliczaniu specyficznym dla OpenClaw. My
    odtworzyliśmy też lokalnie tę samą blokadę rozliczeniową przy bezpośrednim użyciu
    `claude -p --append-system-prompt ...`, gdy dołączony prompt
    identyfikuje OpenClaw, podczas gdy ten sam ciąg promptu **nie** odtwarzał jej na
    ścieżce Anthropic SDK + klucz API.

    W przypadku środowisk produkcyjnych lub wieloużytkownikowych uwierzytelnianie kluczem API Anthropic jest
    bezpieczniejszym, zalecanym wyborem. Jeśli chcesz innych hostowanych
    opcji w stylu subskrypcyjnym w OpenClaw, zobacz [OpenAI](/pl/providers/openai), [Qwen / Model
    Cloud](/pl/providers/qwen), [MiniMax](/pl/providers/minimax) oraz
    [GLM Models](/pl/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Dlaczego widzę HTTP 429 rate_limit_error od Anthropic?">
To oznacza, że twój **limit/rate limit Anthropic** został wyczerpany w bieżącym oknie. Jeśli
używasz **Claude CLI**, poczekaj na reset okna albo przejdź na wyższy plan. Jeśli
używasz **klucza API Anthropic**, sprawdź Anthropic Console
pod kątem użycia/rozliczeń i w razie potrzeby zwiększ limity.

    Jeśli komunikat brzmi dokładnie:
    `Extra usage is required for long context requests`, żądanie próbuje użyć
    bety 1M context Anthropic (`context1m: true`). To działa tylko wtedy, gdy twoje
    poświadczenie kwalifikuje się do rozliczania długiego kontekstu (rozliczanie kluczem API albo
    ścieżka logowania Claude w OpenClaw z włączonym Extra Usage).

    Wskazówka: ustaw **model fallback**, aby OpenClaw mógł nadal odpowiadać, gdy dostawca jest ograniczany przez rate limit.
    Zobacz [Modele](/cli/models), [OAuth](/pl/concepts/oauth) oraz
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/pl/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="Czy AWS Bedrock jest obsługiwany?">
    Tak. OpenClaw ma dołączonego dostawcę **Amazon Bedrock (Converse)**. Gdy obecne są znaczniki środowiska AWS, OpenClaw może automatycznie wykryć katalog Bedrock do streamingu/tekstu i scalić go jako niejawnego dostawcę `amazon-bedrock`; w przeciwnym razie możesz jawnie włączyć `plugins.entries.amazon-bedrock.config.discovery.enabled` albo dodać ręczny wpis dostawcy. Zobacz [Amazon Bedrock](/pl/providers/bedrock) i [Dostawcy modeli](/pl/providers/models). Jeśli wolisz zarządzany przepływ z kluczem, proxy zgodne z OpenAI przed Bedrockiem nadal jest poprawną opcją.
  </Accordion>

  <Accordion title="Jak działa uwierzytelnianie Codex?">
    OpenClaw obsługuje **OpenAI Code (Codex)** przez OAuth (logowanie ChatGPT). Onboarding może uruchomić przepływ OAuth i ustawi domyślny model na `openai-codex/gpt-5.4`, gdy to odpowiednie. Zobacz [Dostawcy modeli](/pl/concepts/model-providers) i [Onboarding (CLI)](/pl/start/wizard).
  </Accordion>

  <Accordion title="Czy obsługujecie uwierzytelnianie subskrypcją OpenAI (Codex OAuth)?">
    Tak. OpenClaw w pełni obsługuje **subskrypcyjny OAuth OpenAI Code (Codex)**.
    OpenAI jawnie zezwala na używanie subskrypcyjnego OAuth w zewnętrznych narzędziach/przepływach
    takich jak OpenClaw. Onboarding może uruchomić ten przepływ OAuth za ciebie.

    Zobacz [OAuth](/pl/concepts/oauth), [Dostawcy modeli](/pl/concepts/model-providers) i [Onboarding (CLI)](/pl/start/wizard).

  </Accordion>

  <Accordion title="Jak skonfigurować Gemini CLI OAuth?">
    Gemini CLI używa **przepływu uwierzytelniania pluginu**, a nie client id ani secret w `openclaw.json`.

    Użyj zamiast tego dostawcy Gemini API:

    1. Włącz plugin: `openclaw plugins enable google`
    2. Uruchom `openclaw onboard --auth-choice gemini-api-key`
    3. Ustaw model Google, na przykład `google/gemini-3.1-pro-preview`

  </Accordion>

  <Accordion title="Czy lokalny model nadaje się do luźnych rozmów?">
    Zwykle nie. OpenClaw potrzebuje dużego kontekstu + mocnego bezpieczeństwa; małe karty obcinają i przeciekają. Jeśli musisz, uruchom lokalnie **największą** kompilację modelu, jaką możesz (LM Studio), i zobacz [/gateway/local-models](/pl/gateway/local-models). Mniejsze/kwantyzowane modele zwiększają ryzyko prompt injection — zobacz [Bezpieczeństwo](/pl/gateway/security).
  </Accordion>

  <Accordion title="Jak utrzymać ruch do modeli hostowanych w określonym regionie?">
    Wybieraj endpointy przypięte do regionu. OpenRouter udostępnia opcje hostowane w USA dla MiniMax, Kimi i GLM; wybierz wariant hostowany w USA, aby utrzymać dane w regionie. Możesz nadal umieścić obok nich Anthropic/OpenAI, używając `models.mode: "merge"`, aby fallbacki pozostały dostępne przy jednoczesnym respektowaniu wybranego dostawcy regionalnego.
  </Accordion>

  <Accordion title="Czy muszę kupić Mac mini, żeby to zainstalować?">
    Nie. OpenClaw działa na macOS lub Linux (Windows przez WSL2). Mac mini jest opcjonalny — niektórzy
    kupują go jako zawsze włączonego hosta, ale mały VPS, domowy serwer albo urządzenie klasy Raspberry Pi też wystarczy.

    Maca potrzebujesz tylko do **narzędzi dostępnych wyłącznie na macOS**. Do iMessage użyj [BlueBubbles](/pl/channels/bluebubbles) (zalecane) — serwer BlueBubbles działa na dowolnym Macu, a Gateway może działać na Linux lub gdzie indziej. Jeśli chcesz innych narzędzi tylko dla macOS, uruchom Gateway na Macu albo sparuj node macOS.

    Dokumentacja: [BlueBubbles](/pl/channels/bluebubbles), [Nodes](/pl/nodes), [Zdalny tryb Mac](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Czy potrzebuję Mac mini do obsługi iMessage?">
    Potrzebujesz **jakiegoś urządzenia macOS** zalogowanego do Messages. To **nie** musi być Mac mini —
    dowolny Mac wystarczy. Do iMessage **użyj [BlueBubbles](/pl/channels/bluebubbles)** (zalecane) — serwer BlueBubbles działa na macOS, a Gateway może działać na Linux lub gdzie indziej.

    Typowe konfiguracje:

    - Uruchamiasz Gateway na Linux/VPS, a serwer BlueBubbles na dowolnym Macu zalogowanym do Messages.
    - Uruchamiasz wszystko na Macu, jeśli chcesz najprostszą konfigurację na jednym komputerze.

    Dokumentacja: [BlueBubbles](/pl/channels/bluebubbles), [Nodes](/pl/nodes),
    [Zdalny tryb Mac](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Jeśli kupię Mac mini do uruchamiania OpenClaw, czy mogę połączyć go z moim MacBook Pro?">
    Tak. **Mac mini może uruchamiać Gateway**, a twój MacBook Pro może łączyć się jako
    **node** (urządzenie towarzyszące). Nodes nie uruchamiają Gateway — zapewniają dodatkowe
    możliwości, takie jak screen/camera/canvas oraz `system.run` na tym urządzeniu.

    Typowy wzorzec:

    - Gateway na Mac mini (zawsze włączony).
    - MacBook Pro uruchamia aplikację macOS albo hosta node i paruje się z Gateway.
    - Użyj `openclaw nodes status` / `openclaw nodes list`, aby to zobaczyć.

    Dokumentacja: [Nodes](/pl/nodes), [CLI nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Czy mogę używać Bun?">
    Bun **nie jest zalecany**. Widzimy błędy czasu działania, zwłaszcza z WhatsApp i Telegram.
    Używaj **Node** dla stabilnych gateway.

    Jeśli mimo to chcesz eksperymentować z Bun, rób to na nieprodukcyjnym gateway
    bez WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: co wpisać w allowFrom?">
    `channels.telegram.allowFrom` to **Telegram user ID ludzkiego nadawcy** (liczbowe). To nie jest nazwa użytkownika bota.

    Onboarding przyjmuje dane wejściowe `@username` i rozwiązuje je do numerycznego ID, ale autoryzacja OpenClaw używa wyłącznie numerycznych ID.

    Bezpieczniej (bez bota zewnętrznego):

    - Wyślij DM do swojego bota, a następnie uruchom `openclaw logs --follow` i odczytaj `from.id`.

    Oficjalne Bot API:

    - Wyślij DM do swojego bota, a następnie wywołaj `https://api.telegram.org/bot<bot_token>/getUpdates` i odczytaj `message.from.id`.

    Zewnętrznie (mniej prywatnie):

    - Wyślij DM do `@userinfobot` albo `@getidsbot`.

    Zobacz [/channels/telegram](/pl/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Czy wiele osób może używać jednego numeru WhatsApp z różnymi instancjami OpenClaw?">
    Tak, przez **multi-agent routing**. Powiąż każdy WhatsApp **DM** nadawcy (peer `kind: "direct"`, nadawca E.164 jak `+15551234567`) z innym `agentId`, aby każda osoba miała własny workspace i magazyn sesji. Odpowiedzi nadal będą pochodzić z **tego samego konta WhatsApp**, a kontrola dostępu DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) jest globalna dla całego konta WhatsApp. Zobacz [Multi-Agent Routing](/pl/concepts/multi-agent) i [WhatsApp](/pl/channels/whatsapp).
  </Accordion>

  <Accordion title='Czy mogę mieć agenta „fast chat” i agenta „Opus do kodowania”?'>
    Tak. Użyj multi-agent routing: nadaj każdemu agentowi własny domyślny model, a następnie powiąż trasy przychodzące (konto dostawcy lub konkretni peery) z każdym agentem. Przykładowa konfiguracja znajduje się w [Multi-Agent Routing](/pl/concepts/multi-agent). Zobacz też [Modele](/pl/concepts/models) i [Konfiguracja](/pl/gateway/configuration).
  </Accordion>

  <Accordion title="Czy Homebrew działa na Linux?">
    Tak. Homebrew obsługuje Linux (Linuxbrew). Szybka konfiguracja:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Jeśli uruchamiasz OpenClaw przez systemd, upewnij się, że PATH usługi zawiera `/home/linuxbrew/.linuxbrew/bin` (lub twój prefiks brew), aby narzędzia instalowane przez `brew` były rozwiązywane w nieinteraktywnych powłokach.
    Ostatnie kompilacje dodają też na początku typowe katalogi bin użytkownika w usługach Linux systemd (na przykład `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) i honorują `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR` oraz `FNM_DIR`, gdy są ustawione.

  </Accordion>

  <Accordion title="Różnica między hackable git install a npm install">
    - **Hackable (git) install:** pełny checkout źródeł, edytowalny, najlepszy dla współtwórców.
      Budujesz lokalnie i możesz łatwo poprawiać kod/dokumentację.
    - **npm install:** globalna instalacja CLI, bez repozytorium, najlepsza do „po prostu uruchom”.
      Aktualizacje pochodzą z npm dist-tags.

    Dokumentacja: [Pierwsze kroki](/pl/start/getting-started), [Aktualizowanie](/pl/install/updating).

  </Accordion>

  <Accordion title="Czy mogę później przełączać się między instalacją npm i git?">
    Tak. Zainstaluj drugi wariant, a potem uruchom Doctor, aby usługa gateway wskazywała nowy entrypoint.
    To **nie usuwa twoich danych** — zmienia tylko instalację kodu OpenClaw. Twój stan
    (`~/.openclaw`) i workspace (`~/.openclaw/workspace`) pozostają nietknięte.

    Z npm do git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    Z git do npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor wykrywa niezgodność entrypointu usługi gateway i proponuje przepisanie konfiguracji usługi tak, aby odpowiadała bieżącej instalacji (w automatyzacji użyj `--repair`).

    Wskazówki dotyczące kopii zapasowych: zobacz [Strategia kopii zapasowych](#gdzie-rzeczy-sa-przechowywane-na-dysku).

  </Accordion>

  <Accordion title="Czy powinienem uruchamiać Gateway na laptopie czy na VPS?">
    Krótka odpowiedź: **jeśli chcesz niezawodności 24/7, użyj VPS**. Jeśli chcesz
    najmniejszego tarcia i akceptujesz uśpienia/restarty, uruchamiaj lokalnie.

    **Laptop (lokalny Gateway)**

    - **Zalety:** brak kosztu serwera, bezpośredni dostęp do lokalnych plików, widoczne okno przeglądarki.
    - **Wady:** uśpienie/zerwania sieci = rozłączenia, aktualizacje/restarty systemu przerywają pracę, komputer musi pozostać wybudzony.

    **VPS / chmura**

    - **Zalety:** zawsze włączony, stabilna sieć, brak problemów z usypianiem laptopa, łatwiej utrzymać działanie.
    - **Wady:** często działanie headless (używaj zrzutów ekranu), tylko zdalny dostęp do plików, do aktualizacji potrzebujesz SSH.

    **Uwaga specyficzna dla OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord działają dobrze z VPS. Jedyny realny kompromis to **przeglądarka headless** vs widoczne okno. Zobacz [Browser](/pl/tools/browser).

    **Zalecane domyślnie:** VPS, jeśli wcześniej miałeś rozłączenia gateway. Lokalnie świetnie działa, gdy aktywnie używasz Maca i chcesz lokalnego dostępu do plików albo automatyzacji UI z widoczną przeglądarką.

  </Accordion>

  <Accordion title="Jak ważne jest uruchamianie OpenClaw na dedykowanym komputerze?">
    Nie jest to wymagane, ale **zalecane ze względu na niezawodność i izolację**.

    - **Dedykowany host (VPS/Mac mini/Pi):** zawsze włączony, mniej przerw przez uśpienia/restarty, czystsze uprawnienia, łatwiej utrzymać działanie.
    - **Wspólny laptop/desktop:** całkowicie w porządku do testów i aktywnego używania, ale spodziewaj się przerw, gdy komputer się usypia lub aktualizuje.

    Jeśli chcesz połączyć oba światy, trzymaj Gateway na dedykowanym hoście i sparuj laptop jako **node** do lokalnych narzędzi screen/camera/exec. Zobacz [Nodes](/pl/nodes).
    Wskazówki bezpieczeństwa znajdziesz w [Bezpieczeństwo](/pl/gateway/security).

  </Accordion>

  <Accordion title="Jakie są minimalne wymagania VPS i zalecany system operacyjny?">
    OpenClaw jest lekki. Dla podstawowego Gateway + jednego kanału czatu:

    - **Absolutne minimum:** 1 vCPU, 1 GB RAM, około 500 MB dysku.
    - **Zalecane:** 1–2 vCPU, 2 GB RAM lub więcej zapasu (logi, media, wiele kanałów). Narzędzia Node i automatyzacja przeglądarki mogą być zasobożerne.

    System operacyjny: używaj **Ubuntu LTS** (lub dowolnego nowoczesnego Debian/Ubuntu). Ta ścieżka instalacji na Linux jest tam najlepiej przetestowana.

    Dokumentacja: [Linux](/pl/platforms/linux), [Hosting VPS](/pl/vps).

  </Accordion>

  <Accordion title="Czy mogę uruchomić OpenClaw w VM i jakie są wymagania?">
    Tak. Traktuj VM tak samo jak VPS: musi być zawsze włączona, osiągalna i mieć wystarczająco
    dużo RAM dla Gateway i wszystkich włączonych kanałów.

    Bazowe wskazówki:

    - **Absolutne minimum:** 1 vCPU, 1 GB RAM.
    - **Zalecane:** 2 GB RAM lub więcej, jeśli uruchamiasz wiele kanałów, automatyzację przeglądarki lub narzędzia multimedialne.
    - **System operacyjny:** Ubuntu LTS albo inny nowoczesny Debian/Ubuntu.

    Jeśli używasz Windows, **WSL2 to najłatwiejsza konfiguracja typu VM** i zapewnia najlepszą
    zgodność narzędzi. Zobacz [Windows](/pl/platforms/windows), [Hosting VPS](/pl/vps).
    Jeśli uruchamiasz macOS w VM, zobacz [macOS VM](/pl/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Czym jest OpenClaw?

<AccordionGroup>
  <Accordion title="Czym jest OpenClaw w jednym akapicie?">
    OpenClaw to osobisty asystent AI uruchamiany na własnych urządzeniach. Odpowiada na używanych już przez ciebie powierzchniach komunikacyjnych (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat oraz bundled channel plugins, takie jak QQ Bot) i może też oferować głos + żywy Canvas na obsługiwanych platformach. **Gateway** to zawsze włączona płaszczyzna sterowania; asystent jest produktem.
  </Accordion>

  <Accordion title="Propozycja wartości">
    OpenClaw nie jest „tylko wrapperem Claude”. To **lokalna, local-first płaszczyzna sterowania**, która pozwala uruchamiać
    zdolnego asystenta na **twoim własnym sprzęcie**, dostępnego z aplikacji czatu, których już używasz, z
    sesjami stanowymi, pamięcią i narzędziami — bez oddawania kontroli nad własnymi przepływami pracy
    hostowanemu SaaS.

    Najważniejsze cechy:

    - **Twoje urządzenia, twoje dane:** uruchamiaj Gateway gdzie chcesz (Mac, Linux, VPS) i trzymaj
      workspace + historię sesji lokalnie.
    - **Prawdziwe kanały, a nie webowy sandbox:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage itd.,
      plus głos mobilny i Canvas na obsługiwanych platformach.
    - **Niezależność od modelu:** używaj Anthropic, OpenAI, MiniMax, OpenRouter itd., z routingiem
      per agent i failoverem.
    - **Opcja tylko lokalna:** uruchamiaj lokalne modele, aby **wszystkie dane mogły pozostać na twoim urządzeniu**, jeśli chcesz.
    - **Multi-agent routing:** oddzielni agenci per kanał, konto lub zadanie, każdy z własnym
      workspace i domyślnymi ustawieniami.
    - **Open source i hackable:** sprawdzaj, rozszerzaj i self-hostuj bez vendor lock-in.

    Dokumentacja: [Gateway](/pl/gateway), [Kanały](/pl/channels), [Multi-agent](/pl/concepts/multi-agent),
    [Pamięć](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Właśnie to skonfigurowałem — co powinienem zrobić najpierw?">
    Dobre pierwsze projekty:

    - Zbudować stronę internetową (WordPress, Shopify albo prostą stronę statyczną).
    - Zrobić prototyp aplikacji mobilnej (zarys, ekrany, plan API).
    - Zorganizować pliki i foldery (sprzątanie, nazewnictwo, tagowanie).
    - Połączyć Gmail i zautomatyzować podsumowania albo follow-upy.

    Potrafi obsługiwać duże zadania, ale działa najlepiej, gdy dzielisz je na fazy i
    używasz sub-agents do pracy równoległej.

  </Accordion>

  <Accordion title="Jakie jest pięć najważniejszych codziennych zastosowań OpenClaw?">
    Codzienne korzyści zwykle wyglądają tak:

    - **Osobiste briefingi:** podsumowania skrzynki odbiorczej, kalendarza i ważnych dla ciebie wiadomości.
    - **Research i przygotowywanie treści:** szybki research, podsumowania i pierwsze wersje maili lub dokumentów.
    - **Przypomnienia i follow-upy:** ponaglenia i checklisty sterowane cron lub heartbeat.
    - **Automatyzacja przeglądarki:** wypełnianie formularzy, zbieranie danych i powtarzanie zadań webowych.
    - **Koordynacja między urządzeniami:** wyślij zadanie z telefonu, pozwól Gateway uruchomić je na serwerze i odbierz wynik na czacie.

  </Accordion>

  <Accordion title="Czy OpenClaw może pomóc w lead gen, outreach, reklamach i blogach dla SaaS?">
    Tak, jeśli chodzi o **research, kwalifikację i przygotowywanie treści**. Może skanować strony, budować shortlisty,
    podsumowywać potencjalnych klientów i pisać wersje robocze wiadomości outreach lub copy reklamowego.

    W przypadku **outreachu lub kampanii reklamowych** trzymaj człowieka w pętli. Unikaj spamu, przestrzegaj lokalnych przepisów i
    zasad platform, a wszystko przeglądaj przed wysłaniem. Najbezpieczniejszy wzorzec to:
    OpenClaw przygotowuje, a ty zatwierdzasz.

    Dokumentacja: [Bezpieczeństwo](/pl/gateway/security).

  </Accordion>

  <Accordion title="Jakie ma zalety względem Claude Code w web development?">
    OpenClaw to **osobisty asystent** i warstwa koordynacji, a nie zamiennik IDE. Używaj
    Claude Code lub Codex do najszybszej bezpośredniej pętli kodowania w repozytorium. Używaj OpenClaw, gdy
    chcesz trwałej pamięci, dostępu między urządzeniami i orkiestracji narzędzi.

    Zalety:

    - **Trwała pamięć + workspace** między sesjami
    - **Dostęp z wielu platform** (WhatsApp, Telegram, TUI, WebChat)
    - **Orkiestracja narzędzi** (przeglądarka, pliki, harmonogram, hooks)
    - **Zawsze włączony Gateway** (uruchamiasz na VPS, kontaktujesz się z dowolnego miejsca)
    - **Nodes** dla lokalnych browser/screen/camera/exec

    Prezentacja: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills i automatyzacja

<AccordionGroup>
  <Accordion title="Jak dostosować Skills bez brudzenia repozytorium?">
    Używaj zarządzanych nadpisań zamiast edytować kopię w repozytorium. Umieść zmiany w `~/.openclaw/skills/<name>/SKILL.md` (albo dodaj folder przez `skills.load.extraDirs` w `~/.openclaw/openclaw.json`). Priorytet to `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`, więc zarządzane nadpisania nadal wygrywają z dołączonymi Skills bez dotykania gita. Jeśli Skill ma być zainstalowany globalnie, ale widoczny tylko dla niektórych agentów, trzymaj współdzieloną kopię w `~/.openclaw/skills` i kontroluj widoczność przez `agents.defaults.skills` oraz `agents.list[].skills`. Tylko zmiany warte upstream powinny trafiać do repozytorium i wychodzić jako PR.
  </Accordion>

  <Accordion title="Czy mogę ładować Skills z niestandardowego folderu?">
    Tak. Dodaj dodatkowe katalogi przez `skills.load.extraDirs` w `~/.openclaw/openclaw.json` (najniższy priorytet). Domyślny priorytet to `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs`. `clawhub` domyślnie instaluje do `./skills`, co OpenClaw traktuje jako `<workspace>/skills` podczas następnej sesji. Jeśli Skill ma być widoczny tylko dla określonych agentów, połącz to z `agents.defaults.skills` albo `agents.list[].skills`.
  </Accordion>

  <Accordion title="Jak mogę używać różnych modeli do różnych zadań?">
    Obecnie obsługiwane wzorce to:

    - **Zadania cron**: izolowane zadania mogą ustawiać nadpisanie `model` dla każdego zadania.
    - **Sub-agents**: kieruj zadania do oddzielnych agentów z innymi modelami domyślnymi.
    - **Przełączanie na żądanie**: użyj `/model`, aby w dowolnym momencie przełączyć model bieżącej sesji.

    Zobacz [Zadania cron](/pl/automation/cron-jobs), [Multi-Agent Routing](/pl/concepts/multi-agent) i [Polecenia slash](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot zawiesza się podczas ciężkiej pracy. Jak to odciążyć?">
    Użyj **sub-agents** do długich lub równoległych zadań. Sub-agents działają we własnej sesji,
    zwracają podsumowanie i utrzymują responsywność głównego czatu.

    Poproś bota, aby „uruchomił sub-agenta dla tego zadania” albo użyj `/subagents`.
    Użyj `/status` na czacie, aby sprawdzić, co Gateway robi teraz (i czy jest zajęty).

    Wskazówka dotycząca tokenów: długie zadania i sub-agents zużywają tokeny. Jeśli koszt ma znaczenie, ustaw
    tańszy model dla sub-agents przez `agents.defaults.subagents.model`.

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Zadania w tle](/pl/automation/tasks).

  </Accordion>

  <Accordion title="Jak działają sesje subagentów związane z wątkiem na Discord?">
    Używaj powiązań wątków. Możesz powiązać wątek Discord z celem subagenta lub sesji, aby kolejne wiadomości w tym wątku pozostawały na powiązanej sesji.

    Podstawowy przepływ:

    - Uruchom przez `sessions_spawn` z `thread: true` (i opcjonalnie `mode: "session"` dla trwałych dalszych wiadomości).
    - Albo ręcznie powiąż przez `/focus <target>`.
    - Użyj `/agents`, aby sprawdzić stan powiązań.
    - Użyj `/session idle <duration|off>` i `/session max-age <duration|off>`, aby sterować automatycznym unfocus.
    - Użyj `/unfocus`, aby odłączyć wątek.

    Wymagana konfiguracja:

    - Ustawienia globalne: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Nadpisania Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Auto-bind przy uruchomieniu: ustaw `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Discord](/pl/channels/discord), [Referencja konfiguracji](/pl/gateway/configuration-reference), [Polecenia slash](/pl/tools/slash-commands).

  </Accordion>

  <Accordion title="Subagent zakończył pracę, ale aktualizacja o ukończeniu trafiła w złe miejsce albo w ogóle nie została opublikowana. Co sprawdzić?">
    Najpierw sprawdź rozstrzygniętą trasę żądającego:

    - Dostarczanie completion-mode subagent preferuje dowolny powiązany wątek lub trasę rozmowy, jeśli taka istnieje.
    - Jeśli źródło zakończenia niesie tylko kanał, OpenClaw wraca do zapisanej trasy sesji żądającego (`lastChannel` / `lastTo` / `lastAccountId`), aby bezpośrednie dostarczenie nadal mogło się udać.
    - Jeśli nie istnieje ani powiązana trasa, ani użyteczna zapisana trasa, bezpośrednie dostarczenie może się nie udać, a wynik przejdzie do dostarczenia przez kolejkę sesji zamiast natychmiastowej publikacji na czacie.
    - Nieprawidłowe lub przestarzałe cele nadal mogą wymusić fallback do kolejki albo końcowe niepowodzenie dostarczenia.
    - Jeśli ostatnia widoczna odpowiedź asystenta dziecka to dokładnie cichy token `NO_REPLY` / `no_reply` albo dokładnie `ANNOUNCE_SKIP`, OpenClaw celowo tłumi ogłoszenie zamiast publikować wcześniejszy, nieaktualny postęp.
    - Jeśli dziecko przekroczyło limit czasu po samych wywołaniach narzędzi, ogłoszenie może zwinąć to do krótkiego podsumowania częściowego postępu zamiast odtwarzać surowe wyjście narzędzi.

    Debugowanie:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Sub-agents](/pl/tools/subagents), [Zadania w tle](/pl/automation/tasks), [Narzędzia sesji](/pl/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron albo przypomnienia się nie uruchamiają. Co sprawdzić?">
    Cron działa wewnątrz procesu Gateway. Jeśli Gateway nie działa stale,
    zaplanowane zadania nie będą się uruchamiać.

    Lista kontrolna:

    - Potwierdź, że cron jest włączony (`cron.enabled`) i `OPENCLAW_SKIP_CRON` nie jest ustawione.
    - Sprawdź, czy Gateway działa 24/7 (bez uśpień/restartów).
    - Zweryfikuj ustawienia strefy czasowej zadania (`--tz` vs strefa czasowa hosta).

    Debugowanie:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Dokumentacja: [Zadania cron](/pl/automation/cron-jobs), [Automatyzacja i zadania](/pl/automation).

  </Accordion>

  <Accordion title="Cron się uruchomił, ale nic nie zostało wysłane do kanału. Dlaczego?">
    Najpierw sprawdź tryb dostarczania:

    - `--no-deliver` / `delivery.mode: "none"` oznacza, że nie należy oczekiwać wiadomości zewnętrznej.
    - Brak lub nieprawidłowy cel ogłoszenia (`channel` / `to`) oznacza, że runner pominął dostarczanie wychodzące.
    - Błędy uwierzytelniania kanału (`unauthorized`, `Forbidden`) oznaczają, że runner próbował dostarczyć, ale poświadczenia to zablokowały.
    - Cichy wynik izolowany (`NO_REPLY` / `no_reply` tylko) jest traktowany jako celowo nienadający się do dostarczenia, więc runner tłumi też fallback dostarczenia przez kolejkę.

    W przypadku izolowanych zadań cron runner odpowiada za końcowe dostarczenie. Od agenta
    oczekuje się zwrócenia zwykłego podsumowania tekstowego, które runner wyśle.
    `--no-deliver` utrzymuje ten wynik wewnętrznie; nie pozwala agentowi wysłać go bezpośrednio przez
    narzędzie wiadomości.

    Debugowanie:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Zadania cron](/pl/automation/cron-jobs), [Zadania w tle](/pl/automation/tasks).

  </Accordion>

  <Accordion title="Dlaczego izolowany przebieg cron przełączył modele albo ponowił próbę raz?">
    Zwykle jest to ścieżka przełączenia modelu na żywo, a nie duplikacja harmonogramu.

    Izolowany cron może utrwalić przekazanie modelu w czasie działania i ponowić próbę, gdy aktywny
    przebieg rzuci `LiveSessionModelSwitchError`. Ponowienie zachowuje przełączonego
    dostawcę/model, a jeśli przełączenie niosło nowe nadpisanie profilu uwierzytelniania, cron
    utrwala je również przed ponowieniem.

    Powiązane reguły wyboru:

    - Najpierw wygrywa nadpisanie modelu hooka Gmail, gdy ma zastosowanie.
    - Następnie `model` per zadanie.
    - Następnie dowolne zapisane nadpisanie modelu sesji cron.
    - Następnie zwykły wybór modelu agenta/domysłnego.

    Pętla ponawiania jest ograniczona. Po pierwszej próbie plus 2 ponowieniach po przełączeniu
    cron przerywa zamiast zapętlać się w nieskończoność.

    Debugowanie:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Dokumentacja: [Zadania cron](/pl/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Jak instalować Skills na Linux?">
    Używaj natywnych poleceń `openclaw skills` albo wrzucaj Skills do workspace. Interfejs Skills na macOS nie jest dostępny na Linux.
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
    w workspace. Oddzielne CLI `clawhub` instaluj tylko wtedy, gdy chcesz publikować albo
    synchronizować własne Skills. Dla współdzielonych instalacji między agentami umieść Skill w `~/.openclaw/skills` i użyj `agents.defaults.skills` lub
    `agents.list[].skills`, jeśli chcesz zawęzić listę agentów, które mogą go widzieć.

  </Accordion>

  <Accordion title="Czy OpenClaw może uruchamiać zadania według harmonogramu albo stale w tle?">
    Tak. Użyj harmonogramu Gateway:

    - **Zadania cron** dla zadań zaplanowanych lub cyklicznych (trwają po restartach).
    - **Heartbeat** dla okresowych kontroli „głównej sesji”.
    - **Zadania izolowane** dla autonomicznych agentów, które publikują podsumowania albo dostarczają je do czatów.

    Dokumentacja: [Zadania cron](/pl/automation/cron-jobs), [Automatyzacja i zadania](/pl/automation),
    [Heartbeat](/pl/gateway/heartbeat).

  </Accordion>

  <Accordion title="Czy mogę uruchamiać apple/macOS-only Skills z Linux?">
    Nie bezpośrednio. Skills macOS są bramkowane przez `metadata.openclaw.os` oraz wymagane binaria, a Skills pojawiają się w prompcie systemowym tylko wtedy, gdy kwalifikują się na **hoście Gateway**. Na Linux Skills tylko dla `darwin` (takie jak `apple-notes`, `apple-reminders`, `things-mac`) nie zostaną załadowane, chyba że nadpiszesz bramkowanie.

    Masz trzy obsługiwane wzorce:

    **Opcja A — uruchom Gateway na Macu (najprościej).**
    Uruchom Gateway tam, gdzie istnieją binaria macOS, a potem łącz się z Linux w [trybie zdalnym](#gateway-porty-juz-dzialaja-i-tryb-zdalny) albo przez Tailscale. Skills ładują się normalnie, bo host Gateway to macOS.

    **Opcja B — użyj node macOS (bez SSH).**
    Uruchom Gateway na Linux, sparuj node macOS (aplikacja w pasku menu) i ustaw **Node Run Commands** na „Always Ask” albo „Always Allow” na Macu. OpenClaw może traktować Skills tylko dla macOS jako kwalifikujące się, gdy wymagane binaria istnieją na node. Agent uruchamia te Skills przez narzędzie `nodes`. Jeśli wybierzesz „Always Ask”, zatwierdzenie „Always Allow” w monicie dodaje to polecenie do allowlisty.

    **Opcja C — proxy binariów macOS przez SSH (zaawansowane).**
    Pozostaw Gateway na Linux, ale spraw, aby wymagane binaria CLI były rozwiązywane do wrapperów SSH uruchamianych na Macu. Następnie nadpisz Skill tak, aby zezwalał na Linux i pozostawał kwalifikujący się.

    1. Utwórz wrapper SSH dla binarium (przykład: `memo` dla Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Umieść wrapper w `PATH` na hoście Linux (na przykład `~/bin/memo`).
    3. Nadpisz metadane Skill (workspace albo `~/.openclaw/skills`), aby zezwalać na Linux:

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Rozpocznij nową sesję, aby odświeżyć migawkę Skills.

  </Accordion>

  <Accordion title="Czy macie integrację z Notion albo HeyGen?">
    Na dziś nie wbudowaną.

    Opcje:

    - **Niestandardowy Skill / plugin:** najlepszy dla niezawodnego dostępu do API (Notion i HeyGen mają API).
    - **Automatyzacja przeglądarki:** działa bez kodu, ale jest wolniejsza i bardziej krucha.

    Jeśli chcesz utrzymywać kontekst per klient (przepływy agencji), prosty wzorzec to:

    - Jedna strona Notion na klienta (kontekst + preferencje + aktywna praca).
    - Poproś agenta, aby pobierał tę stronę na początku sesji.

    Jeśli chcesz natywnej integracji, otwórz prośbę o funkcję albo zbuduj Skill
    dla tych API.

    Instalacja Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Instalacje natywne trafiają do aktywnego katalogu `skills/` w workspace. W przypadku współdzielonych Skills między agentami umieszczaj je w `~/.openclaw/skills/<name>/SKILL.md`. Jeśli tylko niektórzy agenci powinni widzieć współdzieloną instalację, skonfiguruj `agents.defaults.skills` lub `agents.list[].skills`. Niektóre Skills oczekują binariów instalowanych przez Homebrew; na Linux oznacza to Linuxbrew (zobacz wpis FAQ o Homebrew na Linux powyżej). Zobacz [Skills](/pl/tools/skills), [Konfiguracja Skills](/pl/tools/skills-config) i [ClawHub](/pl/tools/clawhub).

  </Accordion>

  <Accordion title="Jak używać mojego już zalogowanego Chrome z OpenClaw?">
    Użyj wbudowanego profilu przeglądarki `user`, który łączy się przez Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Jeśli chcesz własnej nazwy, utwórz jawny profil MCP:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Ta ścieżka jest lokalna względem hosta. Jeśli Gateway działa gdzie indziej, uruchom hosta node na komputerze z przeglądarką albo użyj zdalnego CDP.

    Aktualne ograniczenia `existing-session` / `user`:

    - akcje są oparte na ref, nie na selektorach CSS
    - uploady wymagają `ref` / `inputRef` i obecnie obsługują po jednym pliku na raz
    - `responsebody`, eksport PDF, przechwytywanie pobrań i akcje wsadowe nadal wymagają zarządzanej przeglądarki albo surowego profilu CDP

  </Accordion>
</AccordionGroup>

## Sandbox i pamięć

<AccordionGroup>
  <Accordion title="Czy jest osobny dokument o sandboxingu?">
    Tak. Zobacz [Sandboxing](/pl/gateway/sandboxing). Konfigurację specyficzną dla Dockera (pełny gateway w Docker albo obrazy sandbox) znajdziesz w [Docker](/pl/install/docker).
  </Accordion>

  <Accordion title="Docker wydaje się ograniczony — jak włączyć pełne funkcje?">
    Domyślny obraz stawia na bezpieczeństwo i działa jako użytkownik `node`, więc nie
    zawiera pakietów systemowych, Homebrew ani dołączonych przeglądarek. Dla pełniejszej konfiguracji:

    - Utrwal `/home/node` przy użyciu `OPENCLAW_HOME_VOLUME`, aby cache przetrwały.
    - Dodaj zależności systemowe do obrazu przez `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Zainstaluj przeglądarki Playwright przez dołączone CLI:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Ustaw `PLAYWRIGHT_BROWSERS_PATH` i upewnij się, że ścieżka jest utrwalona.

    Dokumentacja: [Docker](/pl/install/docker), [Browser](/pl/tools/browser).

  </Accordion>

  <Accordion title="Czy mogę mieć prywatne DM, ale grupy publiczne/sandboxowane z jednym agentem?">
    Tak — jeśli prywatny ruch to **DM**, a publiczny ruch to **grupy**.

    Użyj `agents.defaults.sandbox.mode: "non-main"`, aby sesje grup/kanałów (klucze inne niż main) działały w Dockerze, podczas gdy główna sesja DM pozostaje na hoście. Następnie ogranicz dostępne narzędzia w sesjach sandboxowanych przez `tools.sandbox.tools`.

    Przewodnik konfiguracji + przykładowa konfiguracja: [Grupy: prywatne DM + publiczne grupy](/pl/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Kluczowa referencja konfiguracji: [Konfiguracja Gateway](/pl/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Jak podpiąć folder hosta do sandboxa?">
    Ustaw `agents.defaults.sandbox.docker.binds` na `["host:path:mode"]` (np. `"/home/user/src:/src:ro"`). Powiązania globalne + per agent są scalane; powiązania per agent są ignorowane, gdy `scope: "shared"`. Używaj `:ro` dla wszystkiego wrażliwego i pamiętaj, że bindy omijają granice systemu plików sandboxa.

    OpenClaw weryfikuje źródła bind zarówno względem ścieżki znormalizowanej, jak i kanonicznej ścieżki rozwiązanej przez najgłębszego istniejącego przodka. Oznacza to, że ucieczki przez rodzica-symlink nadal kończą się bezpiecznym zamknięciem nawet wtedy, gdy ostatni segment ścieżki jeszcze nie istnieje, a kontrole allowed-root nadal obowiązują po rozwiązaniu symlinków.

    Zobacz [Sandboxing](/pl/gateway/sandboxing#custom-bind-mounts) oraz [Sandbox vs Tool Policy vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check), aby zobaczyć przykłady i uwagi dotyczące bezpieczeństwa.

  </Accordion>

  <Accordion title="Jak działa pamięć?">
    Pamięć OpenClaw to po prostu pliki Markdown w workspace agenta:

    - Notatki dzienne w `memory/YYYY-MM-DD.md`
    - Kuratorowane notatki długoterminowe w `MEMORY.md` (tylko sesje main/prywatne)

    OpenClaw uruchamia też **cichy memory flush przed kompaktowaniem**, aby przypomnieć modelowi
    o zapisywaniu trwałych notatek przed automatycznym kompaktowaniem. Działa to tylko wtedy, gdy workspace
    jest zapisywalny (sandboxy tylko do odczytu to pomijają). Zobacz [Pamięć](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Pamięć ciągle zapomina różne rzeczy. Jak sprawić, żeby zostały?">
    Poproś bota, aby **zapisał fakt do pamięci**. Notatki długoterminowe powinny trafiać do `MEMORY.md`,
    a krótkoterminowy kontekst do `memory/YYYY-MM-DD.md`.

    To nadal obszar, który ulepszamy. Pomaga przypominanie modelowi o zapisywaniu wspomnień;
    model będzie wiedział, co zrobić. Jeśli nadal zapomina, sprawdź, czy Gateway używa
    tego samego workspace przy każdym uruchomieniu.

    Dokumentacja: [Pamięć](/pl/concepts/memory), [Workspace agenta](/pl/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Czy pamięć trwa wiecznie? Jakie są ograniczenia?">
    Pliki pamięci żyją na dysku i pozostają tam, dopóki ich nie usuniesz. Ograniczeniem jest
    pamięć masowa, a nie model. **Kontekst sesji** nadal jest ograniczony oknem kontekstu modelu,
    więc długie rozmowy mogą być kompaktowane albo obcinane. Dlatego istnieje
    wyszukiwanie pamięci — przywraca do kontekstu tylko istotne fragmenty.

    Dokumentacja: [Pamięć](/pl/concepts/memory), [Kontekst](/pl/concepts/context).

  </Accordion>

  <Accordion title="Czy semantyczne wyszukiwanie pamięci wymaga klucza API OpenAI?">
    Tylko jeśli używasz **embeddingów OpenAI**. Codex OAuth obejmuje chat/completions i
    **nie** daje dostępu do embeddingów, więc **logowanie przez Codex (OAuth lub
    logowanie Codex CLI)** nie pomaga w semantycznym wyszukiwaniu pamięci. Embeddingi OpenAI
    nadal wymagają prawdziwego klucza API (`OPENAI_API_KEY` lub `models.providers.openai.apiKey`).

    Jeśli nie ustawisz jawnie dostawcy, OpenClaw automatycznie wybiera dostawcę wtedy, gdy
    może rozwiązać klucz API (profile uwierzytelniania, `models.providers.*.apiKey` albo zmienne env).
    Preferuje OpenAI, jeśli może rozwiązać klucz OpenAI, w przeciwnym razie Gemini, jeśli może rozwiązać klucz Gemini,
    następnie Voyage, a potem Mistral. Jeśli nie ma dostępnego zdalnego klucza, wyszukiwanie pamięci
    pozostaje wyłączone, dopóki go nie skonfigurujesz. Jeśli masz skonfigurowaną i obecną ścieżkę modelu lokalnego, OpenClaw
    preferuje `local`. Ollama jest obsługiwana, gdy jawnie ustawisz
    `memorySearch.provider = "ollama"`.

    Jeśli wolisz pozostać lokalnie, ustaw `memorySearch.provider = "local"` (i opcjonalnie
    `memorySearch.fallback = "none"`). Jeśli chcesz embeddingów Gemini, ustaw
    `memorySearch.provider = "gemini"` i podaj `GEMINI_API_KEY` (lub
    `memorySearch.remote.apiKey`). Obsługujemy modele embeddingów **OpenAI, Gemini, Voyage, Mistral, Ollama lub local**
    — szczegóły konfiguracji znajdziesz w [Pamięć](/pl/concepts/memory).

  </Accordion>
</AccordionGroup>

## Gdzie rzeczy są przechowywane na dysku

<AccordionGroup>
  <Accordion title="Czy wszystkie dane używane z OpenClaw są zapisywane lokalnie?">
    Nie — **stan OpenClaw jest lokalny**, ale **zewnętrzne usługi nadal widzą to, co im wysyłasz**.

    - **Domyślnie lokalnie:** sesje, pliki pamięci, konfiguracja i workspace znajdują się na hoście Gateway
      (`~/.openclaw` + katalog twojego workspace).
    - **Zdalnie z konieczności:** wiadomości wysyłane do dostawców modeli (Anthropic/OpenAI itd.) trafiają do
      ich API, a platformy czatowe (WhatsApp/Telegram/Slack itd.) przechowują dane wiadomości na swoich
      serwerach.
    - **Ty kontrolujesz zakres:** używanie modeli lokalnych utrzymuje prompty na twoim komputerze, ale ruch kanałów
      nadal przechodzi przez serwery danego kanału.

    Powiązane: [Workspace agenta](/pl/concepts/agent-workspace), [Pamięć](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Gdzie OpenClaw przechowuje swoje dane?">
    Wszystko znajduje się pod `$OPENCLAW_STATE_DIR` (domyślnie: `~/.openclaw`):

    | Ścieżka                                                         | Przeznaczenie                                                      |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Główna konfiguracja (JSON5)                                        |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Legacy import OAuth (kopiowany do profili uwierzytelniania przy pierwszym użyciu) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Profile uwierzytelniania (OAuth, klucze API oraz opcjonalne `keyRef`/`tokenRef`) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Opcjonalny payload sekretu oparty na pliku dla dostawców SecretRef `file` |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Plik zgodności legacy (statyczne wpisy `api_key` są czyszczone)    |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Stan dostawców (np. `whatsapp/<accountId>/creds.json`)             |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | Stan per agent (agentDir + sesje)                                  |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Historia i stan rozmów (per agent)                                 |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Metadane sesji (per agent)                                         |

    Ścieżka legacy dla pojedynczego agenta: `~/.openclaw/agent/*` (migrowana przez `openclaw doctor`).

    Twój **workspace** (`AGENTS.md`, pliki pamięci, Skills itd.) jest oddzielny i konfigurowany przez `agents.defaults.workspace` (domyślnie: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Gdzie powinny znajdować się AGENTS.md / SOUL.md / USER.md / MEMORY.md?">
    Te pliki znajdują się w **workspace agenta**, a nie w `~/.openclaw`.

    - **Workspace (per agent)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (albo legacy fallback `memory.md`, gdy `MEMORY.md` nie istnieje),
      `memory/YYYY-MM-DD.md`, opcjonalnie `HEARTBEAT.md`.
    - **Katalog stanu (`~/.openclaw`)**: konfiguracja, stan kanałów/dostawców, profile uwierzytelniania, sesje, logi
      i współdzielone Skills (`~/.openclaw/skills`).

    Domyślny workspace to `~/.openclaw/workspace`, konfigurowany przez:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Jeśli bot „zapomina” po restarcie, upewnij się, że Gateway używa tego samego
    workspace przy każdym uruchomieniu (i pamiętaj: tryb zdalny używa workspace
    **hosta gateway**, a nie twojego lokalnego laptopa).

    Wskazówka: jeśli chcesz utrwalić zachowanie albo preferencję, poproś bota, aby **zapisał to do
    AGENTS.md albo MEMORY.md**, zamiast polegać na historii czatu.

    Zobacz [Workspace agenta](/pl/concepts/agent-workspace) i [Pamięć](/pl/concepts/memory).

  </Accordion>

  <Accordion title="Zalecana strategia kopii zapasowych">
    Umieść **workspace agenta** w **prywatnym** repozytorium git i wykonuj jego kopie zapasowe w miejscu
    prywatnym (na przykład GitHub private). To obejmuje pamięć + pliki AGENTS/SOUL/USER
    i pozwala później przywrócić „umysł” asystenta.

    **Nie** commituj niczego z `~/.openclaw` (poświadczeń, sesji, tokenów ani zaszyfrowanych payloadów sekretów).
    Jeśli potrzebujesz pełnego odtworzenia, wykonuj oddzielnie kopie zapasowe workspace i katalogu stanu
    (zobacz pytanie o migrację powyżej).

    Dokumentacja: [Workspace agenta](/pl/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Jak całkowicie odinstalować OpenClaw?">
    Zobacz osobny przewodnik: [Odinstalowanie](/pl/install/uninstall).
  </Accordion>

  <Accordion title="Czy agenci mogą pracować poza workspace?">
    Tak. Workspace to **domyślny cwd** i kotwica pamięci, a nie twardy sandbox.
    Ścieżki względne rozwiązują się wewnątrz workspace, ale ścieżki bezwzględne mogą uzyskiwać dostęp do innych
    lokalizacji hosta, jeśli sandboxing nie jest włączony. Jeśli potrzebujesz izolacji, użyj
    [`agents.defaults.sandbox`](/pl/gateway/sandboxing) albo ustawień sandbox per agent. Jeśli chcesz,
    aby repozytorium było domyślnym katalogiem roboczym, wskaż `workspace` tego agenta
    na katalog główny repozytorium. Repozytorium OpenClaw to tylko kod źródłowy; trzymaj
    workspace osobno, chyba że celowo chcesz, aby agent pracował wewnątrz niego.

    Przykład (repo jako domyślny cwd):

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
    Stan sesji należy do **hosta gateway**. Jeśli jesteś w trybie zdalnym, interesujący cię magazyn sesji znajduje się na zdalnym komputerze, a nie na lokalnym laptopie. Zobacz [Zarządzanie sesjami](/pl/concepts/session).
  </Accordion>
</AccordionGroup>

## Podstawy konfiguracji

<AccordionGroup>
  <Accordion title="Jaki jest format konfiguracji? Gdzie się znajduje?">
    OpenClaw odczytuje opcjonalną konfigurację **JSON5** z `$OPENCLAW_CONFIG_PATH` (domyślnie: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Jeśli pliku brakuje, używane są dość bezpieczne ustawienia domyślne (w tym domyślny workspace `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Ustawiłem gateway.bind: "lan" (albo "tailnet") i teraz nic nie nasłuchuje / UI mówi unauthorized'>
    Bindy inne niż loopback **wymagają prawidłowej ścieżki uwierzytelniania gateway**. W praktyce oznacza to:

    - uwierzytelnianie shared-secret: token albo hasło
    - `gateway.auth.mode: "trusted-proxy"` za poprawnie skonfigurowanym identity-aware reverse proxy innym niż loopback

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

    - `gateway.remote.token` / `.password` same z siebie **nie** włączają lokalnego uwierzytelniania gateway.
    - Lokalne ścieżki wywołań mogą używać `gateway.remote.*` jako fallback tylko wtedy, gdy `gateway.auth.*` nie jest ustawione.
    - W przypadku uwierzytelniania hasłem ustaw zamiast tego `gateway.auth.mode: "password"` oraz `gateway.auth.password` (albo `OPENCLAW_GATEWAY_PASSWORD`).
    - Jeśli `gateway.auth.token` / `gateway.auth.password` są jawnie skonfigurowane przez SecretRef i nierozwiązane, rozwiązanie kończy się bezpiecznym zamknięciem (brak maskującego fallbacku z remote).
    - Konfiguracje Control UI z shared-secret uwierzytelniają się przez `connect.params.auth.token` albo `connect.params.auth.password` (przechowywane w ustawieniach aplikacji/UI). Tryby oparte na tożsamości, takie jak Tailscale Serve lub `trusted-proxy`, używają zamiast tego nagłówków żądań. Unikaj umieszczania shared secret w URL.
    - Przy `gateway.auth.mode: "trusted-proxy"` reverse proxy na tym samym hoście, używające loopback, nadal **nie** spełnia uwierzytelniania trusted-proxy. Trusted proxy musi być skonfigurowanym źródłem innym niż loopback.

  </Accordion>

  <Accordion title="Dlaczego teraz potrzebuję tokena na localhost?">
    OpenClaw domyślnie wymusza uwierzytelnianie gateway, także dla loopback. W normalnej domyślnej ścieżce oznacza to uwierzytelnianie tokenem: jeśli nie skonfigurowano jawnej ścieżki uwierzytelniania, start gateway przełącza się na tryb tokena i automatycznie go generuje, zapisując w `gateway.auth.token`, więc **lokalni klienci WS muszą się uwierzytelniać**. To blokuje innym lokalnym procesom wywoływanie Gateway.

    Jeśli wolisz inną ścieżkę uwierzytelniania, możesz jawnie wybrać tryb hasła (albo dla reverse proxy z tożsamością, innych niż loopback, `trusted-proxy`). Jeśli **naprawdę** chcesz otwarty loopback, ustaw jawnie `gateway.auth.mode: "none"` w konfiguracji. Doctor może wygenerować token w dowolnym momencie: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Czy po zmianie konfiguracji muszę restartować?">
    Gateway obserwuje konfigurację i obsługuje hot-reload:

    - `gateway.reload.mode: "hybrid"` (domyślnie): bezpieczne zmiany stosowane na gorąco, krytyczne wymagają restartu
    - obsługiwane są także `hot`, `restart`, `off`

  </Accordion>

  <Accordion title="Jak wyłączyć śmieszne tagline w CLI?">
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

    - `off`: ukrywa tekst tagline, ale pozostawia tytuł banera i wiersz wersji.
    - `default`: zawsze używa `All your chats, one OpenClaw.`.
    - `random`: rotacyjne śmieszne/sezonowe tagline (domyślne zachowanie).
    - Jeśli nie chcesz żadnego banera, ustaw env `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Jak włączyć web search (i web fetch)?">
    `web_fetch` działa bez klucza API. `web_search` zależy od wybranego
    dostawcy:

    - Dostawcy oparci o API, tacy jak Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity i Tavily, wymagają standardowej konfiguracji klucza API.
    - Ollama Web Search nie wymaga klucza, ale używa skonfigurowanego hosta Ollama i wymaga `ollama signin`.
    - DuckDuckGo nie wymaga klucza, ale jest nieoficjalną integracją opartą na HTML.
    - SearXNG jest bezkluczowy/self-hosted; skonfiguruj `SEARXNG_BASE_URL` albo `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Zalecane:** uruchom `openclaw configure --section web` i wybierz dostawcę.
    Alternatywy oparte na zmiennych środowiskowych:

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
              provider: "firecrawl", // opcjonalne; pomiń dla auto-detect
            },
          },
        },
    }
    ```

    Konfiguracja web-search specyficzna dla dostawcy znajduje się teraz pod `plugins.entries.<plugin>.config.webSearch.*`.
    Ścieżki dostawców legacy `tools.web.search.*` są nadal tymczasowo ładowane dla zgodności, ale nie należy ich używać w nowych konfiguracjach.
    Konfiguracja fallbacku web-fetch dla Firecrawl znajduje się pod `plugins.entries.firecrawl.config.webFetch.*`.

    Uwagi:

    - Jeśli używasz allowlist, dodaj `web_search`/`web_fetch`/`x_search` albo `group:web`.
    - `web_fetch` jest domyślnie włączone (chyba że jawnie wyłączone).
    - Jeśli pominięto `tools.web.fetch.provider`, OpenClaw automatycznie wykrywa pierwszego gotowego dostawcę fallback dla fetch na podstawie dostępnych poświadczeń. Obecnie dołączonym dostawcą jest Firecrawl.
    - Demony odczytują zmienne env z `~/.openclaw/.env` (albo ze środowiska usługi).

    Dokumentacja: [Narzędzia webowe](/pl/tools/web).

  </Accordion>

  <Accordion title="config.apply wyczyścił moją konfigurację. Jak to naprawić i jak tego unikać?">
    `config.apply` zastępuje **całą konfigurację**. Jeśli wyślesz obiekt częściowy, wszystko
    pozostałe zostanie usunięte.

    Odzyskiwanie:

    - Przywróć z kopii zapasowej (git albo skopiowane `~/.openclaw/openclaw.json`).
    - Jeśli nie masz kopii, uruchom ponownie `openclaw doctor` i ponownie skonfiguruj kanały/modele.
    - Jeśli było to nieoczekiwane, zgłoś błąd i dołącz ostatnią znaną konfigurację albo dowolną kopię zapasową.
    - Lokalny agent kodujący często potrafi odtworzyć działającą konfigurację na podstawie logów albo historii.

    Jak unikać:

    - Używaj `openclaw config set` do małych zmian.
    - Używaj `openclaw configure` do interaktywnej edycji.
    - Używaj najpierw `config.schema.lookup`, gdy nie masz pewności co do dokładnej ścieżki albo kształtu pola; zwraca płytki węzeł schematu oraz podsumowania bezpośrednich dzieci do dalszej analizy.
    - Używaj `config.patch` do częściowych edycji RPC; zachowaj `config.apply` tylko do pełnej wymiany konfiguracji.
    - Jeśli używasz dostępnego tylko dla właściciela narzędzia `gateway` z uruchomienia agenta, nadal będzie ono odrzucało zapisy do `tools.exec.ask` / `tools.exec.security` (w tym aliasów legacy `tools.bash.*`, które normalizują się do tych samych chronionych ścieżek exec).

    Dokumentacja: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/pl/gateway/doctor).

  </Accordion>

  <Accordion title="Jak uruchomić centralny Gateway z wyspecjalizowanymi workerami na różnych urządzeniach?">
    Typowy wzorzec to **jeden Gateway** (np. Raspberry Pi) plus **nodes** i **agents**:

    - **Gateway (centralny):** posiada kanały (Signal/WhatsApp), routing i sesje.
    - **Nodes (urządzenia):** Mac/iOS/Android łączą się jako urządzenia peryferyjne i udostępniają lokalne narzędzia (`system.run`, `canvas`, `camera`).
    - **Agents (workery):** oddzielne „mózgi”/workspace do specjalnych ról (np. „Hetzner ops”, „Personal data”).
    - **Sub-agents:** uruchamiaj pracę w tle z głównego agenta, gdy potrzebujesz równoległości.
    - **TUI:** łącz się z Gateway i przełączaj agentów/sesje.

    Dokumentacja: [Nodes](/pl/nodes), [Dostęp zdalny](/pl/gateway/remote), [Multi-Agent Routing](/pl/concepts/multi-agent), [Sub-agents](/pl/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Czy przeglądarka OpenClaw może działać w trybie headless?">
    Tak. To opcja konfiguracyjna:

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

    Domyślnie jest `false` (headful). Tryb headless częściej wywołuje kontrole antybotowe na niektórych stronach. Zobacz [Browser](/pl/tools/browser).

    Headless używa **tego samego silnika Chromium** i działa dla większości automatyzacji (formularze, kliknięcia, scraping, logowanie). Główne różnice:

    - Brak widocznego okna przeglądarki (używaj zrzutów ekranu, jeśli potrzebujesz obrazu).
    - Niektóre strony są bardziej rygorystyczne wobec automatyzacji w trybie headless (CAPTCHA, antybot).
      Na przykład X/Twitter często blokuje sesje headless.

  </Accordion>

  <Accordion title="Jak używać Brave do sterowania przeglądarką?">
    Ustaw `browser.executablePath` na binarium Brave (albo dowolnej przeglądarki opartej na Chromium) i zrestartuj Gateway.
    Pełne przykłady konfiguracji znajdziesz w [Browser](/pl/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Zdalne gateway i nodes

<AccordionGroup>
  <Accordion title="Jak polecenia propagują się między Telegram, gateway i nodes?">
    Wiadomości Telegram są obsługiwane przez **gateway**. Gateway uruchamia agenta i
    dopiero wtedy wywołuje nodes przez **Gateway WebSocket**, gdy potrzebne jest narzędzie node:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Nodes nie widzą ruchu przychodzącego od dostawców; otrzymują tylko wywołania RPC node.

  </Accordion>

  <Accordion title="Jak mój agent może uzyskać dostęp do mojego komputera, jeśli Gateway jest hostowany zdalnie?">
    Krótka odpowiedź: **sparuj swój komputer jako node**. Gateway działa gdzie indziej, ale może
    wywoływać narzędzia `node.*` (screen, camera, system) na twoim lokalnym komputerze przez Gateway WebSocket.

    Typowa konfiguracja:

    1. Uruchom Gateway na zawsze włączonym hoście (VPS/domowy serwer).
    2. Umieść host Gateway i swój komputer w tym samym tailnet.
    3. Upewnij się, że WS Gateway jest osiągalny (tailnet bind albo tunel SSH).
    4. Otwórz lokalnie aplikację macOS i połącz się w trybie **Remote over SSH** (albo bezpośrednio przez tailnet),
       aby mogła zarejestrować się jako node.
    5. Zatwierdź node na Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Nie jest wymagany oddzielny most TCP; nodes łączą się przez Gateway WebSocket.

    Przypomnienie o bezpieczeństwie: sparowanie node macOS umożliwia `system.run` na tym komputerze. Paruj tylko
    urządzenia, którym ufasz, i zapoznaj się z [Bezpieczeństwo](/pl/gateway/security).

    Dokumentacja: [Nodes](/pl/nodes), [Gateway protocol](/pl/gateway/protocol), [zdalny tryb macOS](/pl/platforms/mac/remote), [Bezpieczeństwo](/pl/gateway/security).

  </Accordion>

  <Accordion title="Tailscale jest połączony, ale nie dostaję odpowiedzi. Co teraz?">
    Sprawdź podstawy:

    - Gateway działa: `openclaw gateway status`
    - Stan Gateway: `openclaw status`
    - Stan kanałów: `openclaw channels status`

    Następnie zweryfikuj uwierzytelnianie i routing:

    - Jeśli używasz Tailscale Serve, upewnij się, że `gateway.auth.allowTailscale` jest ustawione poprawnie.
    - Jeśli łączysz się przez tunel SSH, potwierdź, że lokalny tunel działa i wskazuje właściwy port.
    - Potwierdź, że allowlisty (DM albo grupa) zawierają twoje konto.

    Dokumentacja: [Tailscale](/pl/gateway/tailscale), [Dostęp zdalny](/pl/gateway/remote), [Kanały](/pl/channels).

  </Accordion>

  <Accordion title="Czy dwie instancje OpenClaw mogą rozmawiać ze sobą (lokalna + VPS)?">
    Tak. Nie ma wbudowanego mostu „bot-do-bota”, ale można to połączyć na kilka
    niezawodnych sposobów:

    **Najprościej:** użyj zwykłego kanału czatu, do którego oba boty mają dostęp (Telegram/Slack/WhatsApp).
    Niech Bot A wyśle wiadomość do Bota B, a Bot B odpowie w zwykły sposób.

    **Most CLI (ogólny):** uruchom skrypt, który wywoła drugi Gateway przez
    `openclaw agent --message ... --deliver`, kierując do czatu, którego tamten bot
    słucha. Jeśli jeden bot działa na zdalnym VPS, skieruj swoje CLI do tego zdalnego Gateway
    przez SSH/Tailscale (zobacz [Dostęp zdalny](/pl/gateway/remote)).

    Przykładowy wzorzec (uruchamiany z komputera, który może dotrzeć do docelowego Gateway):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Wskazówka: dodaj guardrail, aby oba boty nie zapętlały się bez końca (tylko wzmianki, allowlisty kanałów albo reguła „nie odpowiadaj na wiadomości botów”).

    Dokumentacja: [Dostęp zdalny](/pl/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/pl/tools/agent-send).

  </Accordion>

  <Accordion title="Czy potrzebuję oddzielnych VPS dla wielu agentów?">
    Nie. Jeden Gateway może hostować wielu agentów, każdy z własnym workspace, modelami domyślnymi
    i routingiem. To jest typowa konfiguracja i jest dużo tańsza oraz prostsza niż uruchamianie
    jednego VPS na agenta.

    Używaj oddzielnych VPS tylko wtedy, gdy potrzebujesz twardej izolacji (granice bezpieczeństwa) albo bardzo
    różnych konfiguracji, których nie chcesz współdzielić. W przeciwnym razie utrzymuj jeden Gateway i
    używaj wielu agentów albo sub-agents.

  </Accordion>

  <Accordion title="Czy jest korzyść z używania node na moim prywatnym laptopie zamiast SSH z VPS?">
    Tak — nodes są rozwiązaniem pierwszej klasy do docierania do laptopa ze zdalnego Gateway i
    dają więcej niż dostęp do powłoki. Gateway działa na macOS/Linux (Windows przez WSL2) i jest
    lekki (wystarczy mały VPS albo urządzenie klasy Raspberry Pi; 4 GB RAM to aż nadto), więc typowa
    konfiguracja to zawsze włączony host plus twój laptop jako node.

    - **Bez potrzeby przychodzącego SSH.** Nodes łączą się wychodząco do Gateway WebSocket i używają parowania urządzeń.
    - **Bezpieczniejsze sterowanie wykonaniem.** `system.run` jest bramkowane przez allowlisty/zatwierdzenia node na tym laptopie.
    - **Więcej narzędzi urządzenia.** Nodes udostępniają `canvas`, `camera` i `screen` oprócz `system.run`.
    - **Lokalna automatyzacja przeglądarki.** Trzymaj Gateway na VPS, ale uruchamiaj Chrome lokalnie przez hosta node na laptopie albo dołączaj do lokalnego Chrome na hoście przez Chrome MCP.

    SSH jest w porządku dla okazjonalnego dostępu do powłoki, ale nodes są prostsze dla ciągłych workflow agentów i
    automatyzacji urządzeń.

    Dokumentacja: [Nodes](/pl/nodes), [CLI nodes](/cli/nodes), [Browser](/pl/tools/browser).

  </Accordion>

  <Accordion title="Czy nodes uruchamiają usługę gateway?">
    Nie. Tylko **jeden gateway** powinien działać na hoście, chyba że celowo uruchamiasz profile izolowane (zobacz [Wiele gateway](/pl/gateway/multiple-gateways)). Nodes to urządzenia peryferyjne łączące się
    z gateway (nodes iOS/Android albo tryb „node mode” macOS w aplikacji w pasku menu). Dla bezgłowych
    hostów node i sterowania CLI zobacz [Node host CLI](/cli/node).

    Pełny restart jest wymagany dla zmian `gateway`, `discovery` i `canvasHost`.

  </Accordion>

  <Accordion title="Czy istnieje API / RPC do stosowania konfiguracji?">
    Tak.

    - `config.schema.lookup`: sprawdź jedno poddrzewo konfiguracji wraz z płytkim węzłem schematu, dopasowaną wskazówką UI i podsumowaniami bezpośrednich dzieci przed zapisem
    - `config.get`: pobierz bieżącą migawkę + hash
    - `config.patch`: bezpieczna częściowa aktualizacja (preferowana dla większości edycji RPC)
    - `config.apply`: zweryfikuj + zastąp pełną konfigurację, a następnie zrestartuj
    - Dostępne tylko dla właściciela narzędzie runtime `gateway` nadal odmawia przepisania `tools.exec.ask` / `tools.exec.security`; aliasy legacy `tools.bash.*` normalizują się do tych samych chronionych ścieżek exec

  </Accordion>

  <Accordion title="Minimalna sensowna konfiguracja dla pierwszej instalacji">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    To ustawia twój workspace i ogranicza, kto może wywołać bota.

  </Accordion>

  <Accordion title="Jak skonfigurować Tailscale na VPS i połączyć się z Maca?">
    Minimalne kroki:

    1. **Zainstaluj + zaloguj się na VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Zainstaluj + zaloguj się na Macu**
       - Użyj aplikacji Tailscale i zaloguj się do tego samego tailnet.
    3. **Włącz MagicDNS (zalecane)**
       - W konsoli administracyjnej Tailscale włącz MagicDNS, aby VPS miał stabilną nazwę.
    4. **Używaj nazwy hosta tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Jeśli chcesz Control UI bez SSH, użyj Tailscale Serve na VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    To utrzymuje gateway na bind loopback i wystawia HTTPS przez Tailscale. Zobacz [Tailscale](/pl/gateway/tailscale).

  </Accordion>

  <Accordion title="Jak połączyć node Mac z zdalnym Gateway (Tailscale Serve)?">
    Serve wystawia **Gateway Control UI + WS**. Nodes łączą się przez ten sam endpoint Gateway WS.

    Zalecana konfiguracja:

    1. **Upewnij się, że VPS i Mac są w tym samym tailnet**.
    2. **Użyj aplikacji macOS w trybie Remote** (celem SSH może być nazwa hosta tailnet).
       Aplikacja tuneluje port Gateway i połączy się jako node.
    3. **Zatwierdź node** na gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Dokumentacja: [Gateway protocol](/pl/gateway/protocol), [Discovery](/pl/gateway/discovery), [zdalny tryb macOS](/pl/platforms/mac/remote).

  </Accordion>

  <Accordion title="Czy powinienem zainstalować to na drugim laptopie, czy po prostu dodać node?">
    Jeśli potrzebujesz tylko **lokalnych narzędzi** (screen/camera/exec) na drugim laptopie, dodaj go jako
    **node**. Dzięki temu zachowasz pojedynczy Gateway i unikniesz duplikowania konfiguracji. Lokalne narzędzia node są
    obecnie dostępne tylko na macOS, ale planujemy rozszerzyć je na inne systemy operacyjne.

    Drugi Gateway instaluj tylko wtedy, gdy potrzebujesz **twardej izolacji** albo dwóch całkowicie osobnych botów.

    Dokumentacja: [Nodes](/pl/nodes), [CLI nodes](/cli/nodes), [Wiele gateway](/pl/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Zmienne env i ładowanie .env

<AccordionGroup>
  <Accordion title="Jak OpenClaw ładuje zmienne środowiskowe?">
    OpenClaw odczytuje zmienne env z procesu nadrzędnego (powłoka, launchd/systemd, CI itd.) i dodatkowo ładuje:

    - `.env` z bieżącego katalogu roboczego
    - globalny fallback `.env` z `~/.openclaw/.env` (czyli `$OPENCLAW_STATE_DIR/.env`)

    Żaden z plików `.env` nie nadpisuje istniejących zmiennych env.

    Możesz też definiować wbudowane zmienne env w konfiguracji (stosowane tylko, jeśli nie ma ich w env procesu):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Pełną kolejność priorytetów i źródła znajdziesz w [/environment](/pl/help/environment).

  </Accordion>

  <Accordion title="Uruchomiłem Gateway przez usługę i moje zmienne env zniknęły. Co teraz?">
    Dwie typowe poprawki:

    1. Umieść brakujące klucze w `~/.openclaw/.env`, aby były pobierane nawet wtedy, gdy usługa nie dziedziczy env z twojej powłoki.
    2. Włącz import powłoki (opcja convenience typu opt-in):

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

    To uruchamia twoją powłokę logowania i importuje tylko brakujące oczekiwane klucze (nigdy nie nadpisuje). Odpowiedniki w env:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Ustawiłem COPILOT_GITHUB_TOKEN, ale models status pokazuje "Shell env: off." Dlaczego?'>
    `openclaw models status` informuje, czy **import env z powłoki** jest włączony. „Shell env: off”
    **nie** oznacza, że twoich zmiennych env brakuje — oznacza tylko, że OpenClaw nie będzie automatycznie ładować
    twojej powłoki logowania.

    Jeśli Gateway działa jako usługa (launchd/systemd), nie odziedziczy środowiska twojej powłoki.
    Napraw to jednym z tych sposobów:

    1. Umieść token w `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Albo włącz import powłoki (`env.shellEnv.enabled: true`).
    3. Albo dodaj go do bloku `env` w konfiguracji (stosowany tylko wtedy, gdy go brakuje).

    Następnie zrestartuj gateway i sprawdź ponownie:

    ```bash
    openclaw models status
    ```

    Tokeny Copilot są odczytywane z `COPILOT_GITHUB_TOKEN` (również `GH_TOKEN` / `GITHUB_TOKEN`).
    Zobacz [/concepts/model-providers](/pl/concepts/model-providers) i [/environment](/pl/help/environment).

  </Accordion>
</AccordionGroup>

## Sesje i wiele czatów

<AccordionGroup>
  <Accordion title="Jak rozpocząć nową rozmowę?">
    Wyślij `/new` albo `/reset` jako osobną wiadomość. Zobacz [Zarządzanie sesjami](/pl/concepts/session).
  </Accordion>

  <Accordion title="Czy sesje resetują się automatycznie, jeśli nigdy nie wyślę /new?">
    Sesje mogą wygasać po `session.idleMinutes`, ale ta funkcja jest **domyślnie wyłączona** (domyślnie **0**).
    Ustaw wartość dodatnią, aby włączyć wygasanie bezczynności. Gdy jest włączone, **następna**
    wiadomość po okresie bezczynności rozpoczyna nowy identyfikator sesji dla tego klucza czatu.
    Nie usuwa to transkryptów — po prostu rozpoczyna nową sesję.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Czy jest sposób, aby zbudować zespół instancji OpenClaw (jeden CEO i wielu agentów)?">
    Tak, przez **multi-agent routing** i **sub-agents**. Możesz utworzyć jednego agenta koordynującego
    i kilku agentów roboczych z własnymi workspace i modelami.

    Mimo to najlepiej traktować to jako **ciekawy eksperyment**. Zużywa dużo tokenów i często
    jest mniej efektywne niż używanie jednego bota z oddzielnymi sesjami. Typowy model, który
    sobie wyobrażamy, to jeden bot, z którym rozmawiasz, z różnymi sesjami do pracy równoległej. Ten
    bot może też uruchamiać sub-agents w razie potrzeby.

    Dokumentacja: [Multi-agent routing](/pl/concepts/multi-agent), [Sub-agents](/pl/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Dlaczego kontekst został obcięty w środku zadania? Jak temu zapobiec?">
    Kontekst sesji jest ograniczony przez okno modelu. Długie czaty, duże wyjścia narzędzi lub wiele
    plików mogą wywołać kompaktowanie albo obcięcie.

    Co pomaga:

    - Poproś bota o podsumowanie bieżącego stanu i zapisanie go do pliku.
    - Używaj `/compact` przed długimi zadaniami i `/new` przy zmianie tematu.
    - Trzymaj ważny kontekst w workspace i poproś bota, aby go ponownie odczytał.
    - Używaj sub-agents do długiej lub równoległej pracy, aby główny czat był mniejszy.
    - Wybierz model z większym oknem kontekstu, jeśli zdarza się to często.

  </Accordion>

  <Accordion title="Jak całkowicie zresetować OpenClaw, ale zachować instalację?">
    Użyj polecenia reset:

    ```bash
    openclaw reset
    ```

    Pełny reset w trybie nieinteraktywnym:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Następnie uruchom konfigurację ponownie:

    ```bash
    openclaw onboard --install-daemon
    ```

    Uwagi:

    - Onboarding oferuje też **Reset**, jeśli wykryje istniejącą konfigurację. Zobacz [Onboarding (CLI)](/pl/start/wizard).
    - Jeśli używałeś profili (`--profile` / `OPENCLAW_PROFILE`), resetuj każdy katalog stanu (domyślnie `~/.openclaw-<profile>`).
    - Reset dev: `openclaw gateway --dev --reset` (tylko dev; czyści konfigurację dev + poświadczenia + sesje + workspace).

  </Accordion>

  <Accordion title='Dostaję błędy "context too large" — jak zresetować albo skompaktować?'>
    Użyj jednej z tych opcji:

    - **Kompaktowanie** (zachowuje rozmowę, ale podsumowuje starsze tury):

      ```
      /compact
      ```

      albo `/compact <instructions>`, aby ukierunkować podsumowanie.

    - **Reset** (nowy identyfikator sesji dla tego samego klucza czatu):

      ```
      /new
      /reset
      ```

    Jeśli to się powtarza:

    - Włącz albo dostrój **przycinanie sesji** (`agents.defaults.contextPruning`), aby obcinać stare wyjścia narzędzi.
    - Użyj modelu z większym oknem kontekstu.

    Dokumentacja: [Kompaktowanie](/pl/concepts/compaction), [Przycinanie sesji](/pl/concepts/session-pruning), [Zarządzanie sesjami](/pl/concepts/session).

  </Accordion>

  <Accordion title='Dlaczego widzę "LLM request rejected: messages.content.tool_use.input field required"?'>
    To błąd walidacji dostawcy: model wyemitował blok `tool_use` bez wymaganego
    `input`. Zwykle oznacza to, że historia sesji jest przestarzała albo uszkodzona (często po długich wątkach
    albo zmianie narzędzia/schematu).

    Naprawa: rozpocznij nową sesję poleceniem `/new` (osobna wiadomość).

  </Accordion>

  <Accordion title="Dlaczego dostaję wiadomości heartbeat co 30 minut?">
    Heartbeaty domyślnie uruchamiają się co **30m** (**1h** przy uwierzytelnianiu OAuth). Dostosuj albo wyłącz je:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // albo "0m", aby wyłączyć
          },
        },
      },
    }
    ```

    Jeśli `HEARTBEAT.md` istnieje, ale jest efektywnie pusty (tylko puste wiersze i nagłówki
    Markdown, takie jak `# Heading`), OpenClaw pomija przebieg heartbeat, aby oszczędzać wywołania API.
    Jeśli pliku nie ma, heartbeat nadal działa, a model sam decyduje, co zrobić.

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
    Opcja 1 (najszybciej): śledź logi i wyślij testową wiadomość w grupie:

    ```bash
    openclaw logs --follow --json
    ```

    Szukaj `chatId` (albo `from`) kończącego się na `@g.us`, np.:
    `1234567890-1234567890@g.us`.

    Opcja 2 (jeśli już skonfigurowane/na allowliście): wylistuj grupy z konfiguracji:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Dokumentacja: [WhatsApp](/pl/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Dlaczego OpenClaw nie odpowiada w grupie?">
    Dwie typowe przyczyny:

    - Bramka wzmianki jest włączona (domyślnie). Musisz @wspomnieć bota (albo dopasować `mentionPatterns`).
    - Skonfigurowałeś `channels.whatsapp.groups` bez `"*"` i grupa nie jest na allowliście.

    Zobacz [Grupy](/pl/channels/groups) i [Wiadomości grupowe](/pl/channels/group-messages).

  </Accordion>

  <Accordion title="Czy grupy/wątki współdzielą kontekst z DM?">
    Czaty bezpośrednie domyślnie zapadają się do głównej sesji. Grupy/kanały mają własne klucze sesji, a tematy Telegram / wątki Discord są oddzielnymi sesjami. Zobacz [Grupy](/pl/channels/groups) i [Wiadomości grupowe](/pl/channels/group-messages).
  </Accordion>

  <Accordion title="Ile workspace i agentów mogę utworzyć?">
    Brak twardych limitów. Dziesiątki (a nawet setki) są w porządku, ale zwracaj uwagę na:

    - **Przyrost dysku:** sesje + transkrypty żyją w `~/.openclaw/agents/<agentId>/sessions/`.
    - **Koszt tokenów:** więcej agentów oznacza więcej współbieżnego użycia modeli.
    - **Narzut operacyjny:** profile uwierzytelniania per agent, workspace i routing kanałów.

    Wskazówki:

    - Utrzymuj jeden **aktywny** workspace per agent (`agents.defaults.workspace`).
    - Przycinaj stare sesje (usuwaj JSONL albo wpisy magazynu), jeśli dysk rośnie.
    - Używaj `openclaw doctor`, aby wychwycić porzucone workspace i niezgodności profili.

  </Accordion>

  <Accordion title="Czy mogę uruchamiać wiele botów lub czatów jednocześnie (Slack) i jak to skonfigurować?">
    Tak. Użyj **Multi-Agent Routing**, aby uruchamiać wiele izolowanych agentów i routować wiadomości przychodzące według
    kanału/konta/peera. Slack jest obsługiwany jako kanał i można go powiązać z określonymi agentami.

    Dostęp do przeglądarki jest potężny, ale nie oznacza „zrób wszystko, co potrafi człowiek” — antyboty, CAPTCHA i MFA nadal
    mogą blokować automatyzację. Dla najbardziej niezawodnego sterowania przeglądarką używaj lokalnego Chrome MCP na hoście
    albo CDP na komputerze, który faktycznie uruchamia przeglądarkę.

    Konfiguracja zgodna z dobrymi praktykami:

    - Zawsze włączony host Gateway (VPS/Mac mini).
    - Jeden agent na rolę (powiązania).
    - Kanały Slack powiązane z tymi agentami.
    - Lokalna przeglądarka przez Chrome MCP albo node, gdy jest potrzebna.

    Dokumentacja: [Multi-Agent Routing](/pl/concepts/multi-agent), [Slack](/pl/channels/slack),
    [Browser](/pl/tools/browser), [Nodes](/pl/nodes).

  </Accordion>
</AccordionGroup>

## Modele: ustawienia domyślne, wybór, aliasy, przełączanie

<AccordionGroup>
  <Accordion title='Czym jest „model domyślny”?'>
    Domyślny model OpenClaw to to, co ustawisz jako:

    ```
    agents.defaults.model.primary
    ```

    Do modeli odwołuje się jako `provider/model` (przykład: `openai/gpt-5.4`). Jeśli pominiesz dostawcę, OpenClaw najpierw próbuje aliasu, potem unikalnego dopasowania skonfigurowanego dostawcy dla dokładnie tego identyfikatora modelu, a dopiero potem przechodzi do skonfigurowanego domyślnego dostawcy jako przestarzałej ścieżki zgodności. Jeśli ten dostawca nie udostępnia już skonfigurowanego modelu domyślnego, OpenClaw przechodzi do pierwszego skonfigurowanego dostawcy/modelu zamiast pokazywać nieaktualny domyślny model usuniętego dostawcy. Nadal powinieneś **jawnie** ustawiać `provider/model`.

  </Accordion>

  <Accordion title="Jaki model polecacie?">
    **Zalecane ustawienie domyślne:** używaj najmocniejszego modelu najnowszej generacji dostępnego w twoim zestawie dostawców.
    **Dla agentów z narzędziami lub niezaufanymi danymi wejściowymi:** priorytetem powinna być siła modelu ponad koszt.
    **Do rutynowego/mało istotnego czatu:** używaj tańszych modeli fallback i routingu według roli agenta.

    MiniMax ma własną dokumentację: [MiniMax](/pl/providers/minimax) i
    [Modele lokalne](/pl/gateway/local-models).

    Praktyczna zasada: używaj **najlepszego modelu, na jaki cię stać** do zadań wysokiej stawki, a tańszego
    modelu do rutynowego czatu albo podsumowań. Możesz routować modele per agent i używać sub-agents do
    równoleglenia długich zadań (każdy sub-agent zużywa tokeny). Zobacz [Modele](/pl/concepts/models) i
    [Sub-agents](/pl/tools/subagents).

    Mocne ostrzeżenie: słabsze/nadmiernie skwantyzowane modele są bardziej podatne na prompt
    injection i niebezpieczne zachowanie. Zobacz [Bezpieczeństwo](/pl/gateway/security).

    Więcej kontekstu: [Modele](/pl/concepts/models).

  </Accordion>

  <Accordion title="Jak przełączać modele bez wymazywania konfiguracji?">
    Używaj **poleceń modeli** albo edytuj tylko pola **modelu**. Unikaj pełnych zamian konfiguracji.

    Bezpieczne opcje:

    - `/model` na czacie (szybko, per sesja)
    - `openclaw models set ...` (aktualizuje tylko konfigurację modelu)
    - `openclaw configure --section model` (interaktywnie)
    - edytuj `agents.defaults.model` w `~/.openclaw/openclaw.json`

    Unikaj `config.apply` z obiektem częściowym, chyba że chcesz zastąpić całą konfigurację.
    W przypadku edycji RPC najpierw sprawdź przez `config.schema.lookup` i preferuj `config.patch`. Payload lookup daje znormalizowaną ścieżkę, płytką dokumentację/ograniczenia schematu oraz podsumowania bezpośrednich dzieci
    dla częściowych aktualizacji.
    Jeśli nadpisałeś konfigurację, przywróć ją z kopii zapasowej albo uruchom `openclaw doctor`, aby ją naprawić.

    Dokumentacja: [Modele](/pl/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/pl/gateway/doctor).

  </Accordion>

  <Accordion title="Czy mogę używać modeli self-hosted (llama.cpp, vLLM, Ollama)?">