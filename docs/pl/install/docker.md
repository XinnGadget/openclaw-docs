---
read_when:
    - Chcesz używać gatewaya w kontenerze zamiast lokalnych instalacji
    - Weryfikujesz przepływ Dockera
summary: Opcjonalna konfiguracja i onboarding OpenClaw oparty na Dockerze
title: Docker
x-i18n:
    generated_at: "2026-04-06T03:08:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: d6aa0453340d7683b4954316274ba6dd1aa7c0ce2483e9bd8ae137ff4efd4c3c
    source_path: install/docker.md
    workflow: 15
---

# Docker (opcjonalnie)

Docker jest **opcjonalny**. Używaj go tylko wtedy, gdy chcesz mieć gateway w kontenerze albo zweryfikować przepływ Dockera.

## Czy Docker jest dla mnie odpowiedni?

- **Tak**: chcesz mieć odizolowane, tymczasowe środowisko gatewaya albo uruchamiać OpenClaw na hoście bez lokalnych instalacji.
- **Nie**: uruchamiasz system na własnej maszynie i chcesz po prostu najszybszej pętli deweloperskiej. Zamiast tego użyj standardowego przepływu instalacji.
- **Uwaga o sandboxingu**: sandboxing agenta również używa Dockera, ale **nie** wymaga uruchamiania całego gatewaya w Dockerze. Zobacz [Sandboxing](/pl/gateway/sandboxing).

## Wymagania wstępne

- Docker Desktop (lub Docker Engine) + Docker Compose v2
- Co najmniej 2 GB RAM do budowania obrazu (`pnpm install` może zostać zakończone przez OOM na hostach z 1 GB z kodem wyjścia 137)
- Wystarczająca ilość miejsca na dysku na obrazy i logi
- Jeśli uruchamiasz na VPS/publicznym hoście, zapoznaj się z
  [utwardzaniem zabezpieczeń przy ekspozycji sieciowej](/pl/gateway/security),
  zwłaszcza z polityką zapory `DOCKER-USER` w Dockerze.

## Gateway w kontenerze

<Steps>
  <Step title="Zbuduj obraz">
    W katalogu głównym repozytorium uruchom skrypt konfiguracji:

    ```bash
    ./scripts/docker/setup.sh
    ```

    Spowoduje to lokalne zbudowanie obrazu gatewaya. Aby zamiast tego użyć gotowego obrazu:

    ```bash
    export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
    ./scripts/docker/setup.sh
    ```

    Gotowe obrazy są publikowane w
    [GitHub Container Registry](https://github.com/openclaw/openclaw/pkgs/container/openclaw).
    Typowe tagi: `main`, `latest`, `<version>` (np. `2026.2.26`).

  </Step>

  <Step title="Ukończ onboarding">
    Skrypt konfiguracji uruchamia onboarding automatycznie. W jego ramach:

    - pojawi się prośba o klucze API providera
    - zostanie wygenerowany token gatewaya i zapisany do `.env`
    - gateway zostanie uruchomiony przez Docker Compose

    Podczas konfiguracji onboarding przed startem i zapisy konfiguracji wykonywane przed uruchomieniem przechodzą przez
    `openclaw-gateway` bezpośrednio. `openclaw-cli` służy do poleceń uruchamianych po
    tym, jak kontener gatewaya już istnieje.

  </Step>

  <Step title="Otwórz Control UI">
    Otwórz `http://127.0.0.1:18789/` w przeglądarce i wklej skonfigurowany
    wspólny sekret w Settings. Skrypt konfiguracji domyślnie zapisuje token do `.env`; jeśli przełączysz konfigurację kontenera na uwierzytelnianie hasłem, użyj zamiast tego
    tego hasła.

    Potrzebujesz ponownie URL?

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    ```

  </Step>

  <Step title="Skonfiguruj kanały (opcjonalnie)">
    Użyj kontenera CLI, aby dodać kanały komunikatorów:

    ```bash
    # WhatsApp (QR)
    docker compose run --rm openclaw-cli channels login

    # Telegram
    docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

    # Discord
    docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
    ```

    Dokumentacja: [WhatsApp](/pl/channels/whatsapp), [Telegram](/pl/channels/telegram), [Discord](/pl/channels/discord)

  </Step>
</Steps>

### Przepływ ręczny

Jeśli wolisz uruchamiać każdy krok samodzielnie zamiast używać skryptu konfiguracji:

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"},{"path":"gateway.controlUi.allowedOrigins","value":["http://localhost:18789","http://127.0.0.1:18789"]}]'
docker compose up -d openclaw-gateway
```

<Note>
Uruchamiaj `docker compose` z katalogu głównego repozytorium. Jeśli włączyłeś `OPENCLAW_EXTRA_MOUNTS`
lub `OPENCLAW_HOME_VOLUME`, skrypt konfiguracji zapisuje `docker-compose.extra.yml`;
dołącz go za pomocą `-f docker-compose.yml -f docker-compose.extra.yml`.
</Note>

<Note>
Ponieważ `openclaw-cli` współdzieli przestrzeń nazw sieci `openclaw-gateway`, jest to
narzędzie używane po starcie. Przed `docker compose up -d openclaw-gateway` uruchamiaj onboarding
i zapisy konfiguracji w czasie konfiguracji przez `openclaw-gateway` z
`--no-deps --entrypoint node`.
</Note>

### Zmienne środowiskowe

Skrypt konfiguracji akceptuje następujące opcjonalne zmienne środowiskowe:

| Zmienna                       | Cel                                                              |
| ----------------------------- | ---------------------------------------------------------------- |
| `OPENCLAW_IMAGE`              | Użyj zdalnego obrazu zamiast budować lokalnie                    |
| `OPENCLAW_DOCKER_APT_PACKAGES` | Zainstaluj dodatkowe pakiety apt podczas builda (nazwy rozdzielone spacjami) |
| `OPENCLAW_EXTENSIONS`         | Wstępnie zainstaluj zależności rozszerzeń podczas builda (nazwy rozdzielone spacjami) |
| `OPENCLAW_EXTRA_MOUNTS`       | Dodatkowe bind mounty hosta (rozdzielone przecinkami `source:target[:opts]`) |
| `OPENCLAW_HOME_VOLUME`        | Utrwal `/home/node` w nazwanym wolumenie Docker                  |
| `OPENCLAW_SANDBOX`            | Włącz bootstrap sandboxa (`1`, `true`, `yes`, `on`)              |
| `OPENCLAW_DOCKER_SOCKET`      | Nadpisz ścieżkę do gniazda Docker                                |

### Kontrole stanu

Endpointy probe kontenera (bez wymaganego auth):

```bash
curl -fsS http://127.0.0.1:18789/healthz   # żywotność
curl -fsS http://127.0.0.1:18789/readyz     # gotowość
```

Obraz Docker zawiera wbudowany `HEALTHCHECK`, który wysyła ping do `/healthz`.
Jeśli kontrole stale się nie powiodą, Docker oznaczy kontener jako `unhealthy`, a
systemy orkiestracji będą mogły go zrestartować lub wymienić.

Uwierzytelniony szczegółowy snapshot stanu zdrowia:

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### LAN vs loopback

`scripts/docker/setup.sh` domyślnie ustawia `OPENCLAW_GATEWAY_BIND=lan`, aby dostęp hosta do
`http://127.0.0.1:18789` działał z publikowaniem portów Dockera.

- `lan` (domyślnie): przeglądarka hosta i CLI hosta mogą osiągnąć opublikowany port gatewaya.
- `loopback`: tylko procesy wewnątrz przestrzeni nazw sieci kontenera mogą osiągnąć
  gateway bezpośrednio.

<Note>
Używaj wartości trybu bind w `gateway.bind` (`lan` / `loopback` / `custom` /
`tailnet` / `auto`), a nie aliasów hosta takich jak `0.0.0.0` lub `127.0.0.1`.
</Note>

### Przechowywanie i trwałość

Docker Compose podmontowuje `OPENCLAW_CONFIG_DIR` do `/home/node/.openclaw` oraz
`OPENCLAW_WORKSPACE_DIR` do `/home/node/.openclaw/workspace`, więc te ścieżki
przetrwają wymianę kontenera.

To podmontowane katalog konfiguracji to miejsce, w którym OpenClaw przechowuje:

- `openclaw.json` dla konfiguracji zachowania
- `agents/<agentId>/agent/auth-profiles.json` dla zapisanego uwierzytelniania OAuth/kluczem API providera
- `.env` dla sekretów runtime opartych na env, takich jak `OPENCLAW_GATEWAY_TOKEN`

Pełne szczegóły dotyczące trwałości w wdrożeniach VM znajdziesz w
[Docker VM Runtime - What persists where](/pl/install/docker-vm-runtime#what-persists-where).

**Miejsca szybkiego wzrostu użycia dysku:** obserwuj `media/`, pliki JSONL sesji, `cron/runs/*.jsonl`
oraz rotujące logi plikowe w `/tmp/openclaw/`.

### Pomocniki shella (opcjonalnie)

Aby ułatwić codzienne zarządzanie Dockerem, zainstaluj `ClawDock`:

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/clawdock/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

Jeśli zainstalowałeś ClawDock ze starszej surowej ścieżki `scripts/shell-helpers/clawdock-helpers.sh`, uruchom ponownie powyższe polecenie instalacji, aby lokalny plik pomocniczy śledził nową lokalizację.

Następnie używaj `clawdock-start`, `clawdock-stop`, `clawdock-dashboard` itd. Uruchom
`clawdock-help`, aby zobaczyć wszystkie polecenia.
Pełny przewodnik pomocników znajdziesz w [ClawDock](/pl/install/clawdock).

<AccordionGroup>
  <Accordion title="Włącz sandbox agenta dla gatewaya Docker">
    ```bash
    export OPENCLAW_SANDBOX=1
    ./scripts/docker/setup.sh
    ```

    Niestandardowa ścieżka do gniazda (np. rootless Docker):

    ```bash
    export OPENCLAW_SANDBOX=1
    export OPENCLAW_DOCKER_SOCKET=/run/user/1000/docker.sock
    ./scripts/docker/setup.sh
    ```

    Skrypt montuje `docker.sock` dopiero po przejściu wymagań wstępnych sandboxa. Jeśli
    konfiguracja sandboxa nie może zostać ukończona, skrypt resetuje `agents.defaults.sandbox.mode`
    do `off`.

  </Accordion>

  <Accordion title="Automatyzacja / CI (bez interakcji)">
    Wyłącz przydział pseudo-TTY Compose za pomocą `-T`:

    ```bash
    docker compose run -T --rm openclaw-cli gateway probe
    docker compose run -T --rm openclaw-cli devices list --json
    ```

  </Accordion>

  <Accordion title="Uwaga o bezpieczeństwie współdzielonej sieci">
    `openclaw-cli` używa `network_mode: "service:openclaw-gateway"`, więc polecenia CLI
    mogą osiągnąć gateway przez `127.0.0.1`. Traktuj to jako współdzieloną
    granicę zaufania. Konfiguracja compose usuwa `NET_RAW`/`NET_ADMIN` i włącza
    `no-new-privileges` w `openclaw-cli`.
  </Accordion>

  <Accordion title="Uprawnienia i EACCES">
    Obraz działa jako `node` (uid 1000). Jeśli widzisz błędy uprawnień na
    `/home/node/.openclaw`, upewnij się, że bind mounty hosta są własnością uid 1000:

    ```bash
    sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
    ```

  </Accordion>

  <Accordion title="Szybsze przebudowy">
    Ułóż Dockerfile tak, aby warstwy zależności były cache'owane. Pozwala to uniknąć ponownego uruchamiania
    `pnpm install`, chyba że zmienią się lockfile:

    ```dockerfile
    FROM node:24-bookworm
    RUN curl -fsSL https://bun.sh/install | bash
    ENV PATH="/root/.bun/bin:${PATH}"
    RUN corepack enable
    WORKDIR /app
    COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
    COPY ui/package.json ./ui/package.json
    COPY scripts ./scripts
    RUN pnpm install --frozen-lockfile
    COPY . .
    RUN pnpm build
    RUN pnpm ui:install
    RUN pnpm ui:build
    ENV NODE_ENV=production
    CMD ["node","dist/index.js"]
    ```

  </Accordion>

  <Accordion title="Zaawansowane opcje kontenera">
    Domyślny obraz jest nastawiony przede wszystkim na bezpieczeństwo i działa jako nieuprzywilejowany `node`. Aby uzyskać bardziej
    rozbudowany kontener:

    1. **Utrwal `/home/node`**: `export OPENCLAW_HOME_VOLUME="openclaw_home"`
    2. **Dodaj zależności systemowe do obrazu**: `export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"`
    3. **Zainstaluj przeglądarki Playwright**:
       ```bash
       docker compose run --rm openclaw-cli \
         node /app/node_modules/playwright-core/cli.js install chromium
       ```
    4. **Utrwal pobrane przeglądarki**: ustaw
       `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright` i użyj
       `OPENCLAW_HOME_VOLUME` lub `OPENCLAW_EXTRA_MOUNTS`.

  </Accordion>

  <Accordion title="OAuth OpenAI Codex (Docker bezgłowy)">
    Jeśli wybierzesz w kreatorze OAuth OpenAI Codex, otworzy się URL w przeglądarce. W
    Dockerze lub konfiguracjach bezgłowych skopiuj pełny URL przekierowania, na który trafisz, i wklej
    go z powrotem do kreatora, aby zakończyć auth.
  </Accordion>

  <Accordion title="Metadane obrazu bazowego">
    Główny obraz Docker używa `node:24-bookworm` i publikuje adnotacje obrazu bazowego OCI,
    w tym `org.opencontainers.image.base.name`,
    `org.opencontainers.image.source` i inne. Zobacz
    [adnotacje obrazu OCI](https://github.com/opencontainers/image-spec/blob/main/annotations.md).
  </Accordion>
</AccordionGroup>

### Uruchamianie na VPS?

Zobacz [Hetzner (Docker VPS)](/pl/install/hetzner) i
[Docker VM Runtime](/pl/install/docker-vm-runtime), aby poznać kroki wspólnego wdrażania na VM,
w tym wypiekanie binariów, trwałość i aktualizacje.

## Sandbox agenta

Gdy `agents.defaults.sandbox` jest włączone, gateway uruchamia wykonywanie narzędzi agenta
(shell, odczyt/zapis plików itd.) wewnątrz izolowanych kontenerów Dockera, podczas gdy
sam gateway pozostaje na hoście. Daje to twardą granicę wokół nieufnych lub
wielodzierżawnych sesji agentów bez konteneryzowania całego gatewaya.

Zakres sandboxa może być per agent (domyślnie), per sesja albo współdzielony. Każdy zakres
ma własny workspace montowany pod `/workspace`. Możesz również konfigurować
polityki zezwalania/zabraniania narzędzi, izolację sieci, limity zasobów oraz kontenery przeglądarki.

Pełną konfigurację, obrazy, uwagi dotyczące bezpieczeństwa i profile wieloagentowe znajdziesz w:

- [Sandboxing](/pl/gateway/sandboxing) -- pełne informacje o sandboxie
- [OpenShell](/pl/gateway/openshell) -- interaktywny dostęp do powłoki w kontenerach sandboxa
- [Multi-Agent Sandbox and Tools](/pl/tools/multi-agent-sandbox-tools) -- nadpisania per agent

### Szybkie włączenie

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared
      },
    },
  },
}
```

Zbuduj domyślny obraz sandboxa:

```bash
scripts/sandbox-setup.sh
```

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Brak obrazu lub kontener sandboxa się nie uruchamia">
    Zbuduj obraz sandboxa za pomocą
    [`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh)
    albo ustaw `agents.defaults.sandbox.docker.image` na własny obraz.
    Kontenery są tworzone automatycznie per sesja na żądanie.
  </Accordion>

  <Accordion title="Błędy uprawnień w sandboxie">
    Ustaw `docker.user` na UID:GID zgodne z własnością zamontowanego workspace'u,
    albo wykonaj chown katalogu workspace.
  </Accordion>

  <Accordion title="Niestandardowe narzędzia nie są znajdowane w sandboxie">
    OpenClaw uruchamia polecenia za pomocą `sh -lc` (login shell), co wczytuje
    `/etc/profile` i może resetować PATH. Ustaw `docker.env.PATH`, aby poprzedzić nim
    ścieżki do własnych narzędzi, albo dodaj skrypt w `/etc/profile.d/` w swoim Dockerfile.
  </Accordion>

  <Accordion title="Zakończone przez OOM podczas builda obrazu (wyjście 137)">
    VM potrzebuje co najmniej 2 GB RAM. Użyj większej klasy maszyny i spróbuj ponownie.
  </Accordion>

  <Accordion title="Unauthorized lub wymagane parowanie w Control UI">
    Pobierz świeży link do panelu i zatwierdź urządzenie przeglądarki:

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    docker compose run --rm openclaw-cli devices list
    docker compose run --rm openclaw-cli devices approve <requestId>
    ```

    Więcej szczegółów: [Dashboard](/web/dashboard), [Devices](/cli/devices).

  </Accordion>

  <Accordion title="Cel gatewaya pokazuje ws://172.x.x.x lub błędy parowania z Docker CLI">
    Zresetuj tryb i bind gatewaya:

    ```bash
    docker compose run --rm openclaw-cli config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"}]'
    docker compose run --rm openclaw-cli devices list --url ws://127.0.0.1:18789
    ```

  </Accordion>
</AccordionGroup>

## Powiązane

- [Przegląd instalacji](/pl/install) — wszystkie metody instalacji
- [Podman](/pl/install/podman) — alternatywa Podman dla Dockera
- [ClawDock](/pl/install/clawdock) — społecznościowa konfiguracja Docker Compose
- [Aktualizacja](/pl/install/updating) — utrzymywanie OpenClaw w aktualnym stanie
- [Configuration](/pl/gateway/configuration) — konfiguracja gatewaya po instalacji
