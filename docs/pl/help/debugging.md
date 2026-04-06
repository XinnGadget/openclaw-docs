---
read_when:
    - Musisz sprawdzić surowe dane wyjściowe modelu pod kątem wycieku rozumowania
    - Chcesz uruchomić Gateway w trybie watch podczas iteracji
    - Potrzebujesz powtarzalnego workflow debugowania
summary: 'Narzędzia do debugowania: tryb watch, surowe strumienie modelu i śledzenie wycieku rozumowania'
title: Debugowanie
x-i18n:
    generated_at: "2026-04-06T03:07:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4bc72e8d6cad3a1acaad066f381c82309583fabf304c589e63885f2685dc704e
    source_path: help/debugging.md
    workflow: 15
---

# Debugowanie

Ta strona opisuje pomocniki debugowania dla wyjścia strumieniowego, szczególnie gdy
provider miesza rozumowanie ze zwykłym tekstem.

## Nadpisania debugowania runtime

Użyj `/debug` na czacie, aby ustawić nadpisania konfiguracji **tylko dla runtime** (pamięć, nie dysk).
`/debug` jest domyślnie wyłączone; włącz je za pomocą `commands.debug: true`.
To przydatne, gdy musisz przełączyć rzadko używane ustawienia bez edytowania `openclaw.json`.

Przykłady:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` czyści wszystkie nadpisania i przywraca konfigurację zapisaną na dysku.

## Tryb watch Gateway

Aby szybko iterować, uruchom gateway pod watcherem plików:

```bash
pnpm gateway:watch
```

Mapuje się to na:

```bash
node scripts/watch-node.mjs gateway --force
```

Watcher restartuje się po zmianach w plikach istotnych dla builda w `src/`, plikach źródłowych rozszerzeń,
metadanych `package.json` i `openclaw.plugin.json` rozszerzeń, `tsconfig.json`,
`package.json` oraz `tsdown.config.ts`. Zmiany metadanych rozszerzeń restartują
gateway bez wymuszania przebudowy `tsdown`; zmiany źródeł i konfiguracji nadal
najpierw przebudowują `dist`.

Dodaj dowolne flagi CLI gatewaya po `gateway:watch`, a będą przekazywane przy
każdym restarcie. Ponowne uruchomienie tego samego polecenia watch dla tego samego
repozytorium/zestawu flag zastępuje teraz starszy watcher zamiast pozostawiać
zduplikowane procesy nadrzędne watcherów.

## Profil dev + gateway dev (`--dev`)

Użyj profilu dev, aby odizolować stan i uruchomić bezpieczną, tymczasową konfigurację do
debugowania. Istnieją **dwie** flagi `--dev`:

- **Globalne `--dev` (profil):** izoluje stan w `~/.openclaw-dev` i
  domyślnie ustawia port gatewaya na `19001` (powiązane porty odpowiednio się przesuwają).
- **`gateway --dev`:** nakazuje Gateway automatycznie utworzyć domyślną konfigurację +
  workspace, jeśli ich brakuje (i pominąć BOOTSTRAP.md).

Zalecany przepływ (profil dev + bootstrap dev):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

Jeśli nie masz jeszcze globalnej instalacji, uruchom CLI przez `pnpm openclaw ...`.

Co to robi:

1. **Izolacja profilu** (globalne `--dev`)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (przeglądarka/canvas odpowiednio się przesuwają)

2. **Bootstrap dev** (`gateway --dev`)
   - Zapisuje minimalną konfigurację, jeśli jej brakuje (`gateway.mode=local`, bind loopback).
   - Ustawia `agent.workspace` na workspace dev.
   - Ustawia `agent.skipBootstrap=true` (bez BOOTSTRAP.md).
   - Seeduje pliki workspace, jeśli ich brakuje:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - Domyślna tożsamość: **C3‑PO** (droid protokolarny).
   - Pomija providery kanałów w trybie dev (`OPENCLAW_SKIP_CHANNELS=1`).

Przepływ resetu (świeży start):

```bash
pnpm gateway:dev:reset
```

Uwaga: `--dev` to **globalna** flaga profilu i jest przechwytywana przez niektóre runnery.
Jeśli musisz ją zapisać jawnie, użyj formy z env var:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` czyści konfigurację, poświadczenia, sesje i workspace dev (przy użyciu
`trash`, a nie `rm`), a następnie odtwarza domyślną konfigurację dev.

Wskazówka: jeśli działa już gateway inny niż dev (launchd/systemd), najpierw go zatrzymaj:

```bash
openclaw gateway stop
```

## Logowanie surowego strumienia (OpenClaw)

OpenClaw może logować **surowy strumień asystenta** przed jakimkolwiek filtrowaniem/formatowaniem.
To najlepszy sposób, aby sprawdzić, czy rozumowanie dociera jako zwykłe delty tekstowe
(lub jako osobne bloki thinking).

Włącz przez CLI:

```bash
pnpm gateway:watch --raw-stream
```

Opcjonalne nadpisanie ścieżki:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

Równoważne zmienne env:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

Plik domyślny:

`~/.openclaw/logs/raw-stream.jsonl`

## Logowanie surowych chunków (pi-mono)

Aby przechwycić **surowe chunki zgodne z OpenAI** przed ich sparsowaniem do bloków,
pi-mono udostępnia osobny logger:

```bash
PI_RAW_STREAM=1
```

Opcjonalna ścieżka:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

Plik domyślny:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> Uwaga: jest to emitowane tylko przez procesy używające providera
> `openai-completions` z pi-mono.

## Uwagi dotyczące bezpieczeństwa

- Logi surowego strumienia mogą zawierać pełne prompty, wyjście narzędzi i dane użytkownika.
- Przechowuj logi lokalnie i usuwaj je po zakończeniu debugowania.
- Jeśli udostępniasz logi, najpierw usuń z nich sekrety i dane osobowe.
