---
read_when: You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox.
status: active
summary: 'Jak działa piaskownica OpenClaw: tryby, zakresy, dostęp do obszaru roboczego i obrazy'
title: Piaskownica
x-i18n:
    generated_at: "2026-04-14T02:08:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2573d0d7462f63a68eb1750e5432211522ff5b42989a17379d3e188468bbce52
    source_path: gateway/sandboxing.md
    workflow: 15
---

# Piaskownica

OpenClaw może uruchamiać **narzędzia wewnątrz backendów piaskownicy**, aby zmniejszyć promień rażenia.
Jest to **opcjonalne** i kontrolowane przez konfigurację (`agents.defaults.sandbox` lub
`agents.list[].sandbox`). Jeśli piaskownica jest wyłączona, narzędzia działają na hoście.
Gateway pozostaje na hoście; wykonywanie narzędzi działa w odizolowanej piaskownicy,
gdy jest włączone.

Nie jest to idealna granica bezpieczeństwa, ale znacząco ogranicza dostęp do systemu plików
i procesów, gdy model zrobi coś głupiego.

## Co jest objęte piaskownicą

- Wykonywanie narzędzi (`exec`, `read`, `write`, `edit`, `apply_patch`, `process` itd.).
- Opcjonalna piaskownica przeglądarki (`agents.defaults.sandbox.browser`).
  - Domyślnie przeglądarka w piaskownicy uruchamia się automatycznie (zapewnia, że CDP jest osiągalne), gdy narzędzie przeglądarki tego potrzebuje.
    Konfiguracja przez `agents.defaults.sandbox.browser.autoStart` i `agents.defaults.sandbox.browser.autoStartTimeoutMs`.
  - Domyślnie kontenery przeglądarki w piaskownicy używają dedykowanej sieci Docker (`openclaw-sandbox-browser`) zamiast globalnej sieci `bridge`.
    Konfiguracja przez `agents.defaults.sandbox.browser.network`.
  - Opcjonalne `agents.defaults.sandbox.browser.cdpSourceRange` ogranicza ruch przychodzący CDP na brzegu kontenera za pomocą listy dozwolonych CIDR (na przykład `172.21.0.1/32`).
  - Dostęp obserwatora noVNC jest domyślnie chroniony hasłem; OpenClaw emituje krótkotrwały URL z tokenem, który udostępnia lokalną stronę bootstrap i otwiera noVNC z hasłem we fragmencie URL (nie w logach zapytań/nagłówków).
  - `agents.defaults.sandbox.browser.allowHostControl` pozwala sesjom w piaskownicy jawnie wskazywać przeglądarkę hosta jako cel.
  - Opcjonalne listy dozwolonych elementów ograniczają `target: "custom"`: `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`.

Nie są objęte piaskownicą:

- Sam proces Gateway.
- Każde narzędzie jawnie dopuszczone do uruchamiania poza piaskownicą (np. `tools.elevated`).
  - **Elevated exec omija piaskownicę i używa skonfigurowanej ścieżki wyjścia (`gateway` domyślnie albo `node`, gdy celem exec jest `node`).**
  - Jeśli piaskownica jest wyłączona, `tools.elevated` nie zmienia sposobu wykonania (i tak odbywa się ono na hoście). Zobacz [Tryb Elevated](/pl/tools/elevated).

## Tryby

`agents.defaults.sandbox.mode` określa, **kiedy** używana jest piaskownica:

- `"off"`: bez piaskownicy.
- `"non-main"`: piaskownica tylko dla sesji **niegłównych** (domyślnie, jeśli chcesz zwykłe czaty na hoście).
- `"all"`: każda sesja działa w piaskownicy.
  Uwaga: `"non-main"` opiera się na `session.mainKey` (domyślnie `"main"`), a nie na identyfikatorze agenta.
  Sesje grupowe/kanałowe używają własnych kluczy, więc są traktowane jako niegłówne i będą objęte piaskownicą.

## Zakres

`agents.defaults.sandbox.scope` określa, **ile kontenerów** jest tworzonych:

- `"agent"` (domyślnie): jeden kontener na agenta.
- `"session"`: jeden kontener na sesję.
- `"shared"`: jeden kontener współdzielony przez wszystkie sesje objęte piaskownicą.

## Backend

`agents.defaults.sandbox.backend` określa, **które środowisko uruchomieniowe** dostarcza piaskownicę:

- `"docker"` (domyślnie): lokalne środowisko piaskownicy oparte na Dockerze.
- `"ssh"`: ogólne zdalne środowisko piaskownicy oparte na SSH.
- `"openshell"`: środowisko piaskownicy oparte na OpenShell.

Konfiguracja specyficzna dla SSH znajduje się w `agents.defaults.sandbox.ssh`.
Konfiguracja specyficzna dla OpenShell znajduje się w `plugins.entries.openshell.config`.

### Wybór backendu

|                     | Docker                           | SSH                            | OpenShell                                                  |
| ------------------- | -------------------------------- | ------------------------------ | ---------------------------------------------------------- |
| **Gdzie działa**    | Lokalny kontener                 | Dowolny host dostępny przez SSH | Piaskownica zarządzana przez OpenShell                     |
| **Konfiguracja**    | `scripts/sandbox-setup.sh`       | Klucz SSH + host docelowy      | Włączony Plugin OpenShell                                  |
| **Model obszaru roboczego** | Bind-mount lub kopia              | Zdalny jako kanoniczny (jednorazowe zasianie) | `mirror` lub `remote`                              |
| **Kontrola sieci**  | `docker.network` (domyślnie: brak) | Zależy od zdalnego hosta       | Zależy od OpenShell                                        |
| **Piaskownica przeglądarki** | Obsługiwana                     | Nieobsługiwana                 | Jeszcze nieobsługiwana                                     |
| **Bind mounty**     | `docker.binds`                   | N/D                            | N/D                                                        |
| **Najlepsze dla**   | Lokalny development, pełna izolacja | Odciążenie na zdalnej maszynie | Zarządzane zdalne piaskownice z opcjonalną dwukierunkową synchronizacją |

### Backend Docker

Backend Docker jest domyślnym środowiskiem uruchomieniowym, wykonującym narzędzia i przeglądarki w piaskownicy lokalnie przez gniazdo demona Docker (`/var/run/docker.sock`). Izolacja kontenera piaskownicy jest określana przez przestrzenie nazw Dockera.

**Ograniczenia Docker-out-of-Docker (DooD)**:
Jeśli wdrażasz sam Gateway OpenClaw jako kontener Docker, orkiestruje on sąsiednie kontenery piaskownicy przy użyciu gniazda Dockera hosta (DooD). Wprowadza to konkretne ograniczenie mapowania ścieżek:

- **Konfiguracja wymaga ścieżek hosta**: konfiguracja `workspace` w `openclaw.json` MUSI zawierać **bezwzględną ścieżkę hosta** (np. `/home/user/.openclaw/workspaces`), a nie wewnętrzną ścieżkę kontenera Gateway. Gdy OpenClaw prosi demona Docker o uruchomienie piaskownicy, demon interpretuje ścieżki względem przestrzeni nazw systemu operacyjnego hosta, a nie przestrzeni nazw Gateway.
- **Parzystość mostka FS (identyczne mapowanie wolumenów)**: natywny proces Gateway OpenClaw również zapisuje pliki heartbeat i bridge do katalogu `workspace`. Ponieważ Gateway interpretuje dokładnie ten sam ciąg znaków (ścieżkę hosta) wewnątrz własnego środowiska kontenerowego, wdrożenie Gateway MUSI zawierać identyczne mapowanie wolumenów, które natywnie łączy przestrzeń nazw hosta (`-v /home/user/.openclaw:/home/user/.openclaw`).

Jeśli zmapujesz ścieżki wewnętrznie bez pełnej zgodności bezwzględnych ścieżek hosta, OpenClaw natywnie zgłosi błąd uprawnień `EACCES` podczas próby zapisania swojego heartbeat wewnątrz środowiska kontenera, ponieważ w pełni kwalifikowany ciąg ścieżki nie istnieje natywnie.

### Backend SSH

Użyj `backend: "ssh"`, gdy chcesz, aby OpenClaw umieszczał `exec`, narzędzia plikowe i odczyty multimediów w piaskownicy
na dowolnej maszynie dostępnej przez SSH.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // Lub użyj SecretRefs / zawartości inline zamiast lokalnych plików:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

Jak to działa:

- OpenClaw tworzy zdalny katalog główny dla danego zakresu pod `sandbox.ssh.workspaceRoot`.
- Przy pierwszym użyciu po utworzeniu lub odtworzeniu OpenClaw jednorazowo zasiewa ten zdalny obszar roboczy z lokalnego obszaru roboczego.
- Następnie `exec`, `read`, `write`, `edit`, `apply_patch`, odczyty mediów w promptach oraz przygotowanie mediów przychodzących działają bezpośrednio na zdalnym obszarze roboczym przez SSH.
- OpenClaw nie synchronizuje automatycznie zdalnych zmian z powrotem do lokalnego obszaru roboczego.

Materiał uwierzytelniający:

- `identityFile`, `certificateFile`, `knownHostsFile`: używają istniejących lokalnych plików i przekazują je przez konfigurację OpenSSH.
- `identityData`, `certificateData`, `knownHostsData`: używają ciągów inline lub SecretRefs. OpenClaw rozwiązuje je przez zwykły snapshot środowiska secrets, zapisuje do plików tymczasowych z uprawnieniami `0600` i usuwa po zakończeniu sesji SSH.
- Jeśli dla tego samego elementu ustawiono zarówno `*File`, jak i `*Data`, to w tej sesji SSH pierwszeństwo ma `*Data`.

To model **zdalny jako kanoniczny**. Zdalny obszar roboczy SSH staje się rzeczywistym stanem piaskownicy po początkowym zasianiu.

Ważne konsekwencje:

- Lokalne edycje na hoście wykonane poza OpenClaw po kroku zasiania nie są widoczne zdalnie, dopóki nie odtworzysz piaskownicy.
- `openclaw sandbox recreate` usuwa zdalny katalog główny dla danego zakresu i przy następnym użyciu ponownie zasiewa go z lokalnego obszaru roboczego.
- Piaskownica przeglądarki nie jest obsługiwana w backendzie SSH.
- Ustawienia `sandbox.docker.*` nie mają zastosowania do backendu SSH.

### Backend OpenShell

Użyj `backend: "openshell"`, gdy chcesz, aby OpenClaw umieszczał narzędzia w piaskownicy
w zdalnym środowisku zarządzanym przez OpenShell. Pełny przewodnik konfiguracji, dokumentację
referencyjną i porównanie trybów obszaru roboczego znajdziesz na dedykowanej
[stronie OpenShell](/pl/gateway/openshell).

OpenShell ponownie wykorzystuje ten sam podstawowy transport SSH i most zdalnego systemu plików co
ogólny backend SSH oraz dodaje cykl życia specyficzny dla OpenShell
(`sandbox create/get/delete`, `sandbox ssh-config`) wraz z opcjonalnym trybem obszaru roboczego `mirror`.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote", // mirror | remote
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
        },
      },
    },
  },
}
```

Tryby OpenShell:

- `mirror` (domyślnie): lokalny obszar roboczy pozostaje kanoniczny. OpenClaw synchronizuje lokalne pliki do OpenShell przed exec i synchronizuje zdalny obszar roboczy z powrotem po exec.
- `remote`: obszar roboczy OpenShell staje się kanoniczny po utworzeniu piaskownicy. OpenClaw jednorazowo zasiewa zdalny obszar roboczy z lokalnego obszaru roboczego, a następnie narzędzia plikowe i exec działają bezpośrednio na zdalnej piaskownicy bez synchronizacji zmian z powrotem.

Szczegóły zdalnego transportu:

- OpenClaw prosi OpenShell o konfigurację SSH specyficzną dla piaskownicy przez `openshell sandbox ssh-config <name>`.
- Core zapisuje tę konfigurację SSH do pliku tymczasowego, otwiera sesję SSH i ponownie używa tego samego mostu zdalnego systemu plików, który jest używany przez `backend: "ssh"`.
- Tylko w trybie `mirror` cykl życia jest inny: synchronizacja lokalne→zdalne przed exec, a następnie synchronizacja z powrotem po exec.

Obecne ograniczenia OpenShell:

- piaskownica przeglądarki nie jest jeszcze obsługiwana
- `sandbox.docker.binds` nie jest obsługiwane w backendzie OpenShell
- specyficzne dla Dockera parametry środowiska uruchomieniowego w `sandbox.docker.*` nadal mają zastosowanie tylko do backendu Docker

#### Tryby obszaru roboczego

OpenShell ma dwa modele obszaru roboczego. To część, która ma największe znaczenie w praktyce.

##### `mirror`

Użyj `plugins.entries.openshell.config.mode: "mirror"`, gdy chcesz, aby **lokalny obszar roboczy pozostał kanoniczny**.

Zachowanie:

- Przed `exec` OpenClaw synchronizuje lokalny obszar roboczy do piaskownicy OpenShell.
- Po `exec` OpenClaw synchronizuje zdalny obszar roboczy z powrotem do lokalnego obszaru roboczego.
- Narzędzia plikowe nadal działają przez most piaskownicy, ale lokalny obszar roboczy pozostaje źródłem prawdy między turami.

Użyj tego, gdy:

- edytujesz pliki lokalnie poza OpenClaw i chcesz, aby te zmiany automatycznie pojawiały się w piaskownicy
- chcesz, aby piaskownica OpenShell zachowywała się możliwie najbardziej jak backend Docker
- chcesz, aby obszar roboczy hosta odzwierciedlał zapisy piaskownicy po każdej turze exec

Kompromis:

- dodatkowy koszt synchronizacji przed i po exec

##### `remote`

Użyj `plugins.entries.openshell.config.mode: "remote"`, gdy chcesz, aby **obszar roboczy OpenShell stał się kanoniczny**.

Zachowanie:

- Gdy piaskownica jest tworzona po raz pierwszy, OpenClaw jednorazowo zasiewa zdalny obszar roboczy z lokalnego obszaru roboczego.
- Następnie `exec`, `read`, `write`, `edit` i `apply_patch` działają bezpośrednio na zdalnym obszarze roboczym OpenShell.
- OpenClaw **nie** synchronizuje zdalnych zmian z powrotem do lokalnego obszaru roboczego po exec.
- Odczyty mediów podczas budowania promptu nadal działają, ponieważ narzędzia plikowe i multimedialne odczytują przez most piaskownicy zamiast zakładać lokalną ścieżkę hosta.
- Transport odbywa się przez SSH do piaskownicy OpenShell zwróconej przez `openshell sandbox ssh-config`.

Ważne konsekwencje:

- Jeśli edytujesz pliki na hoście poza OpenClaw po kroku zasiania, zdalna piaskownica **nie** zobaczy tych zmian automatycznie.
- Jeśli piaskownica zostanie odtworzona, zdalny obszar roboczy zostanie ponownie zasiany z lokalnego obszaru roboczego.
- Przy `scope: "agent"` lub `scope: "shared"` ten zdalny obszar roboczy jest współdzielony w tym samym zakresie.

Użyj tego, gdy:

- piaskownica ma działać głównie po zdalnej stronie OpenShell
- chcesz mniejszego narzutu synchronizacji w każdej turze
- nie chcesz, aby lokalne edycje na hoście po cichu nadpisywały stan zdalnej piaskownicy

Wybierz `mirror`, jeśli traktujesz piaskownicę jako tymczasowe środowisko wykonawcze.
Wybierz `remote`, jeśli traktujesz piaskownicę jako rzeczywisty obszar roboczy.

#### Cykl życia OpenShell

Piaskownice OpenShell są nadal zarządzane przez zwykły cykl życia piaskownicy:

- `openclaw sandbox list` pokazuje środowiska uruchomieniowe OpenShell, a także środowiska uruchomieniowe Docker
- `openclaw sandbox recreate` usuwa bieżące środowisko uruchomieniowe i pozwala OpenClaw odtworzyć je przy następnym użyciu
- logika czyszczenia jest również świadoma backendu

Dla trybu `remote` odtworzenie jest szczególnie ważne:

- odtworzenie usuwa kanoniczny zdalny obszar roboczy dla tego zakresu
- przy następnym użyciu zasiewany jest nowy zdalny obszar roboczy z lokalnego obszaru roboczego

Dla trybu `mirror` odtworzenie głównie resetuje zdalne środowisko wykonawcze,
ponieważ lokalny obszar roboczy i tak pozostaje kanoniczny.

## Dostęp do obszaru roboczego

`agents.defaults.sandbox.workspaceAccess` określa, **co piaskownica może widzieć**:

- `"none"` (domyślnie): narzędzia widzą obszar roboczy piaskownicy w `~/.openclaw/sandboxes`.
- `"ro"`: montuje obszar roboczy agenta tylko do odczytu pod `/agent` (wyłącza `write`/`edit`/`apply_patch`).
- `"rw"`: montuje obszar roboczy agenta do odczytu i zapisu pod `/workspace`.

W backendzie OpenShell:

- tryb `mirror` nadal używa lokalnego obszaru roboczego jako kanonicznego źródła między turami exec
- tryb `remote` używa zdalnego obszaru roboczego OpenShell jako kanonicznego źródła po początkowym zasianiu
- `workspaceAccess: "ro"` i `"none"` nadal ograniczają możliwość zapisu w ten sam sposób

Media przychodzące są kopiowane do aktywnego obszaru roboczego piaskownicy (`media/inbound/*`).
Uwaga dotycząca Skills: narzędzie `read` jest zakorzenione w piaskownicy. Przy `workspaceAccess: "none"`
OpenClaw odzwierciedla kwalifikujące się Skills w obszarze roboczym piaskownicy (`.../skills`), aby
mogły być odczytywane. Przy `"rw"` Skills obszaru roboczego są dostępne do odczytu z
`/workspace/skills`.

## Niestandardowe bind mounty

`agents.defaults.sandbox.docker.binds` montuje dodatkowe katalogi hosta do kontenera.
Format: `host:container:mode` (np. `"/home/user/source:/source:rw"`).

Globalne bindy i bindy per agent są **scalane** (a nie zastępowane). Przy `scope: "shared"` bindy per agent są ignorowane.

`agents.defaults.sandbox.browser.binds` montuje dodatkowe katalogi hosta tylko do kontenera **przeglądarki w piaskownicy**.

- Gdy jest ustawione (w tym `[]`), zastępuje `agents.defaults.sandbox.docker.binds` dla kontenera przeglądarki.
- Gdy jest pominięte, kontener przeglądarki wraca do `agents.defaults.sandbox.docker.binds` (zgodność wsteczna).

Przykład (źródło tylko do odczytu + dodatkowy katalog danych):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

Uwagi dotyczące bezpieczeństwa:

- Biny omijają system plików piaskownicy: udostępniają ścieżki hosta z ustawionym przez Ciebie trybem (`:ro` lub `:rw`).
- OpenClaw blokuje niebezpieczne źródła bindów (na przykład: `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev` oraz nadrzędne mounty, które by je ujawniały).
- OpenClaw blokuje także typowe katalogi główne z poświadczeniami w katalogu domowym, takie jak `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm` i `~/.ssh`.
- Walidacja bindów nie polega wyłącznie na dopasowaniu ciągów znaków. OpenClaw normalizuje ścieżkę źródłową, a następnie ponownie ją rozwiązuje przez najgłębszego istniejącego przodka przed ponownym sprawdzeniem zablokowanych ścieżek i dozwolonych katalogów głównych.
- Oznacza to, że ucieczki przez nadrzędny symlink nadal kończą się bezpiecznym odrzuceniem, nawet gdy końcowy liść jeszcze nie istnieje. Przykład: `/workspace/run-link/new-file` nadal rozwiązuje się jako `/var/run/...`, jeśli `run-link` wskazuje tam.
- Dozwolone katalogi źródłowe są kanonikalizowane w ten sam sposób, więc ścieżka, która wygląda na mieszczącą się na liście dozwolonych przed rozwiązaniem symlinków, nadal zostanie odrzucona jako `outside allowed roots`.
- Wrażliwe mounty (secrets, klucze SSH, poświadczenia usług) powinny mieć tryb `:ro`, chyba że jest to absolutnie konieczne.
- Połącz to z `workspaceAccess: "ro"`, jeśli potrzebujesz tylko dostępu do odczytu obszaru roboczego; tryby bindów pozostają niezależne.
- Zobacz [Piaskownica vs zasady narzędzi vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated), aby zrozumieć, jak bindy współdziałają z zasadami narzędzi i elevated exec.

## Obrazy + konfiguracja

Domyślny obraz Docker: `openclaw-sandbox:bookworm-slim`

Zbuduj go raz:

```bash
scripts/sandbox-setup.sh
```

Uwaga: domyślny obraz **nie** zawiera Node. Jeśli Skill wymaga Node (lub
innych środowisk uruchomieniowych), albo przygotuj własny obraz, albo zainstaluj je przez
`sandbox.docker.setupCommand` (wymaga wychodzącego ruchu sieciowego + zapisywalnego katalogu głównego +
użytkownika root).

Jeśli chcesz bardziej funkcjonalny obraz piaskownicy z popularnymi narzędziami (na przykład
`curl`, `jq`, `nodejs`, `python3`, `git`), zbuduj:

```bash
scripts/sandbox-common-setup.sh
```

Następnie ustaw `agents.defaults.sandbox.docker.image` na
`openclaw-sandbox-common:bookworm-slim`.

Obraz przeglądarki w piaskownicy:

```bash
scripts/sandbox-browser-setup.sh
```

Domyślnie kontenery piaskownicy Docker działają **bez sieci**.
Możesz to zmienić przez `agents.defaults.sandbox.docker.network`.

Dołączony obraz przeglądarki w piaskownicy stosuje również konserwatywne domyślne ustawienia uruchamiania Chromium
dla obciążeń uruchamianych w kontenerach. Obecne domyślne ustawienia kontenera obejmują:

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` i `--disable-setuid-sandbox`, gdy włączone jest `noSandbox`.
- Trzy flagi utwardzania grafiki (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) są opcjonalne i przydają się,
  gdy kontenery nie mają obsługi GPU. Ustaw `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`,
  jeśli Twoje obciążenie wymaga WebGL lub innych funkcji 3D/przeglądarki.
- `--disable-extensions` jest domyślnie włączone i można je wyłączyć przez
  `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` dla przepływów zależnych od rozszerzeń.
- `--renderer-process-limit=2` jest kontrolowane przez
  `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>`, gdzie `0` zachowuje domyślne ustawienie Chromium.

Jeśli potrzebujesz innego profilu środowiska uruchomieniowego, użyj niestandardowego obrazu przeglądarki i podaj
własny entrypoint. W przypadku lokalnych profili Chromium (poza kontenerem) użyj
`browser.extraArgs`, aby dodać dodatkowe flagi uruchomieniowe.

Domyślne ustawienia bezpieczeństwa:

- `network: "host"` jest zablokowane.
- `network: "container:<id>"` jest domyślnie zablokowane (ryzyko ominięcia przez dołączenie do przestrzeni nazw).
- Awaryjne obejście: `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`.

Instalacje Docker i konteneryzowany Gateway znajdują się tutaj:
[Docker](/pl/install/docker)

W przypadku wdrożeń Gateway na Dockerze `scripts/docker/setup.sh` może przygotować konfigurację piaskownicy.
Ustaw `OPENCLAW_SANDBOX=1` (lub `true`/`yes`/`on`), aby włączyć tę ścieżkę. Możesz
nadpisać lokalizację gniazda przez `OPENCLAW_DOCKER_SOCKET`. Pełna konfiguracja i dokumentacja
zmiennych środowiskowych: [Docker](/pl/install/docker#agent-sandbox).

## setupCommand (jednorazowa konfiguracja kontenera)

`setupCommand` uruchamia się **raz** po utworzeniu kontenera piaskownicy (nie przy każdym uruchomieniu).
Wykonuje się wewnątrz kontenera przez `sh -lc`.

Ścieżki:

- Globalnie: `agents.defaults.sandbox.docker.setupCommand`
- Per agent: `agents.list[].sandbox.docker.setupCommand`

Typowe pułapki:

- Domyślne `docker.network` to `"none"` (brak ruchu wychodzącego), więc instalacje pakietów zakończą się błędem.
- `docker.network: "container:<id>"` wymaga `dangerouslyAllowContainerNamespaceJoin: true` i powinno być używane wyłącznie awaryjnie.
- `readOnlyRoot: true` blokuje zapisy; ustaw `readOnlyRoot: false` lub przygotuj własny obraz.
- `user` musi być rootem dla instalacji pakietów (pomiń `user` lub ustaw `user: "0:0"`).
- Exec w piaskownicy **nie** dziedziczy hostowego `process.env`. Użyj
  `agents.defaults.sandbox.docker.env` (lub własnego obrazu) dla kluczy API używanych przez Skills.

## Zasady narzędzi + ścieżki obejścia

Zasady allow/deny dla narzędzi nadal są stosowane przed regułami piaskownicy. Jeśli narzędzie jest zablokowane
globalnie lub per agent, piaskownica go nie przywróci.

`tools.elevated` to jawna ścieżka obejścia, która uruchamia `exec` poza piaskownicą (`gateway` domyślnie albo `node`, gdy celem exec jest `node`).
Dyrektywy `/exec` mają zastosowanie tylko do autoryzowanych nadawców i są utrwalane per sesja; aby całkowicie wyłączyć
`exec`, użyj reguły deny w zasadach narzędzi (zobacz [Piaskownica vs zasady narzędzi vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated)).

Debugowanie:

- Użyj `openclaw sandbox explain`, aby sprawdzić efektywny tryb piaskownicy, zasady narzędzi i klucze konfiguracji naprawczej.
- Zobacz [Piaskownica vs zasady narzędzi vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated), aby zrozumieć model myślowy „dlaczego to jest zablokowane?”.
  Zachowaj ścisłe ograniczenia.

## Nadpisania dla wielu agentów

Każdy agent może nadpisywać ustawienia piaskownicy i narzędzi:
`agents.list[].sandbox` oraz `agents.list[].tools` (plus `agents.list[].tools.sandbox.tools` dla zasad narzędzi w piaskownicy).
Zobacz [Piaskownica i narzędzia dla wielu agentów](/pl/tools/multi-agent-sandbox-tools), aby poznać reguły pierwszeństwa.

## Minimalny przykład włączenia

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Powiązana dokumentacja

- [OpenShell](/pl/gateway/openshell) -- konfiguracja zarządzanego backendu piaskownicy, tryby obszaru roboczego i dokumentacja referencyjna konfiguracji
- [Konfiguracja piaskownicy](/pl/gateway/configuration-reference#agentsdefaultssandbox)
- [Piaskownica vs zasady narzędzi vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated) -- debugowanie „dlaczego to jest zablokowane?”
- [Piaskownica i narzędzia dla wielu agentów](/pl/tools/multi-agent-sandbox-tools) -- nadpisania per agent i reguły pierwszeństwa
- [Bezpieczeństwo](/pl/gateway/security)
