---
read_when:
    - Musisz sprawdzić surowe dane wyjściowe modelu pod kątem wycieku rozumowania
    - Chcesz uruchomić Gateway w trybie watch podczas iteracji
    - Potrzebujesz powtarzalnego przepływu debugowania
summary: 'Narzędzia debugowania: tryb watch, surowe strumienie modelu i śledzenie wycieku rozumowania'
title: Debugowanie
x-i18n:
    generated_at: "2026-04-12T23:28:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# Debugowanie

Ta strona opisuje pomocnicze narzędzia do debugowania strumieniowego wyjścia, szczególnie gdy dostawca miesza rozumowanie ze zwykłym tekstem.

## Nadpisania debugowania w czasie działania

Użyj `/debug` na czacie, aby ustawić nadpisania konfiguracji **tylko na czas działania** (w pamięci, nie na dysku).
`/debug` jest domyślnie wyłączone; włącz je przez `commands.debug: true`.
To przydaje się, gdy trzeba przełączać rzadko używane ustawienia bez edytowania `openclaw.json`.

Przykłady:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` czyści wszystkie nadpisania i przywraca konfigurację z dysku.

## Wyjście śledzenia sesji

Użyj `/trace`, gdy chcesz zobaczyć linie śledzenia/debugowania należące do Plugin w jednej sesji bez włączania pełnego trybu verbose.

Przykłady:

```text
/trace
/trace on
/trace off
```

Używaj `/trace` do diagnostyki Plugin, takiej jak podsumowania debugowania Active Memory.
Nadal używaj `/verbose` do zwykłego szczegółowego wyjścia statusu/narzędzi, a `/debug` do nadpisań konfiguracji tylko na czas działania.

## Tryb watch Gateway

Aby szybko iterować, uruchom Gateway pod watcherem plików:

```bash
pnpm gateway:watch
```

To mapuje się na:

```bash
node scripts/watch-node.mjs gateway --force
```

Watcher restartuje proces po zmianach w plikach mających znaczenie dla kompilacji w `src/`, plikach źródłowych rozszerzeń, metadanych rozszerzeń `package.json` i `openclaw.plugin.json`, `tsconfig.json`, `package.json` oraz `tsdown.config.ts`. Zmiany metadanych rozszerzeń restartują Gateway bez wymuszania przebudowy `tsdown`; zmiany w źródłach i konfiguracji nadal najpierw przebudowują `dist`.

Dodaj dowolne flagi CLI Gateway po `gateway:watch`, a będą przekazywane przy każdym restarcie. Ponowne uruchomienie tego samego polecenia watch dla tego samego repozytorium/zestawu flag zastępuje teraz starszego watchera zamiast pozostawiać zduplikowane procesy nadrzędne watcherów.

## Profil deweloperski + deweloperski Gateway (`--dev`)

Użyj profilu deweloperskiego, aby odizolować stan i uruchomić bezpieczne, tymczasowe środowisko do debugowania. Istnieją **dwie** flagi `--dev`:

- **Globalne `--dev` (profil):** izoluje stan w `~/.openclaw-dev` i domyślnie ustawia port Gateway na `19001` (powiązane porty przesuwają się wraz z nim).
- **`gateway --dev`:** mówi Gateway, aby automatycznie utworzył domyślną konfigurację + workspace, jeśli ich brakuje (i pominął `BOOTSTRAP.md`).

Zalecany przepływ (profil deweloperski + bootstrap deweloperski):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

Jeśli nie masz jeszcze instalacji globalnej, uruchamiaj CLI przez `pnpm openclaw ...`.

Co to robi:

1. **Izolacja profilu** (globalne `--dev`)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (porty browser/canvas odpowiednio się przesuwają)

2. **Bootstrap deweloperski** (`gateway --dev`)
   - Zapisuje minimalną konfigurację, jeśli jej brakuje (`gateway.mode=local`, bind do loopback).
   - Ustawia `agent.workspace` na deweloperski workspace.
   - Ustawia `agent.skipBootstrap=true` (bez `BOOTSTRAP.md`).
   - Tworzy pliki workspace, jeśli ich brakuje:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - Domyślna tożsamość: **C3‑PO** (droid protokolarny).
   - Pomija dostawców kanałów w trybie deweloperskim (`OPENCLAW_SKIP_CHANNELS=1`).

Przepływ resetowania (świeży start):

```bash
pnpm gateway:dev:reset
```

Uwaga: `--dev` to **globalna** flaga profilu i bywa przechwytywana przez niektóre uruchamiacze.
Jeśli musisz zapisać ją jawnie, użyj formy z zmienną środowiskową:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` czyści konfigurację, poświadczenia, sesje i deweloperski workspace (używając `trash`, a nie `rm`), a następnie odtwarza domyślne środowisko deweloperskie.

Wskazówka: jeśli działa już Gateway poza trybem deweloperskim (launchd/systemd), najpierw go zatrzymaj:

```bash
openclaw gateway stop
```

## Logowanie surowego strumienia (OpenClaw)

OpenClaw może logować **surowy strumień asystenta** przed jakimkolwiek filtrowaniem/formatowaniem.
To najlepszy sposób, aby sprawdzić, czy rozumowanie przychodzi jako zwykłe delty tekstowe
(lub jako osobne bloki myślenia).

Włącz przez CLI:

```bash
pnpm gateway:watch --raw-stream
```

Opcjonalne nadpisanie ścieżki:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

Równoważne zmienne środowiskowe:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

Plik domyślny:

`~/.openclaw/logs/raw-stream.jsonl`

## Logowanie surowych chunków (pi-mono)

Aby przechwytywać **surowe chunki zgodne z OpenAI** przed przetworzeniem ich na bloki,
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

> Uwaga: jest to emitowane tylko przez procesy używające dostawcy
> `openai-completions` z pi-mono.

## Uwagi dotyczące bezpieczeństwa

- Logi surowego strumienia mogą zawierać pełne prompty, wyjście narzędzi i dane użytkownika.
- Przechowuj logi lokalnie i usuwaj je po debugowaniu.
- Jeśli udostępniasz logi, najpierw usuń z nich sekrety i dane osobowe.
