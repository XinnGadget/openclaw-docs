---
read_when:
    - Instalowanie lub konfigurowanie pluginów
    - Zrozumienie reguł wykrywania i ładowania pluginów
    - Praca z bundle'ami pluginów zgodnymi z Codex/Claude
sidebarTitle: Install and Configure
summary: Instalowanie, konfigurowanie i zarządzanie pluginami OpenClaw
title: Pluginy
x-i18n:
    generated_at: "2026-04-06T03:14:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9e2472a3023f3c1c6ee05b0cdc228f6b713cc226a08695b327de8a3ad6973c83
    source_path: tools/plugin.md
    workflow: 15
---

# Pluginy

Pluginy rozszerzają OpenClaw o nowe capabilities: kanały, providery modeli,
narzędzia, Skills, mowę, transkrypcję realtime, głos realtime,
media-understanding, generowanie obrazów, generowanie wideo, web fetch, web
search i inne. Niektóre pluginy są **core** (dostarczane z OpenClaw), a inne
są **zewnętrzne** (publikowane na npm przez społeczność).

## Szybki start

<Steps>
  <Step title="Zobacz, co jest załadowane">
    ```bash
    openclaw plugins list
    ```
  </Step>

  <Step title="Zainstaluj plugin">
    ```bash
    # Z npm
    openclaw plugins install @openclaw/voice-call

    # Z lokalnego katalogu lub archiwum
    openclaw plugins install ./my-plugin
    openclaw plugins install ./my-plugin.tgz
    ```

  </Step>

  <Step title="Uruchom ponownie Gateway">
    ```bash
    openclaw gateway restart
    ```

    Następnie skonfiguruj plugin w `plugins.entries.\<id\>.config` w pliku konfiguracji.

  </Step>
</Steps>

Jeśli wolisz sterowanie natywne dla czatu, włącz `commands.plugins: true` i używaj:

```text
/plugin install clawhub:@openclaw/voice-call
/plugin show voice-call
/plugin enable voice-call
```

Ścieżka instalacji używa tego samego resolvera co CLI: lokalna ścieżka/archiwum, jawne
`clawhub:<pkg>` albo zwykła specyfikacja pakietu (najpierw ClawHub, potem fallback do npm).

Jeśli konfiguracja jest nieprawidłowa, instalacja zwykle kończy się bezpieczną odmową i kieruje do
`openclaw doctor --fix`. Jedynym wyjątkiem odzyskiwania jest wąska ścieżka
ponownej instalacji bundled pluginu dla pluginów, które aktywnie włączają
`openclaw.install.allowInvalidConfigRecovery`.

## Typy pluginów

OpenClaw rozpoznaje dwa formaty pluginów:

| Format     | Jak działa                                                       | Przykłady                                              |
| ---------- | ---------------------------------------------------------------- | ------------------------------------------------------ |
| **Native** | `openclaw.plugin.json` + moduł runtime; wykonywany w tym samym procesie | Oficjalne pluginy, pakiety społecznościowe npm         |
| **Bundle** | Układ zgodny z Codex/Claude/Cursor; mapowany na funkcje OpenClaw | `.codex-plugin/`, `.claude-plugin/`, `.cursor-plugin/` |

Oba pojawiają się w `openclaw plugins list`. Szczegóły dotyczące bundle'i znajdziesz w [Plugin Bundles](/pl/plugins/bundles).

Jeśli tworzysz plugin Native, zacznij od [Building Plugins](/pl/plugins/building-plugins)
i [Plugin SDK Overview](/pl/plugins/sdk-overview).

## Oficjalne pluginy

### Instalowalne (npm)

| Plugin          | Pakiet                | Dokumentacja                         |
| --------------- | --------------------- | ------------------------------------ |
| Matrix          | `@openclaw/matrix`    | [Matrix](/pl/channels/matrix)           |
| Microsoft Teams | `@openclaw/msteams`   | [Microsoft Teams](/pl/channels/msteams) |
| Nostr           | `@openclaw/nostr`     | [Nostr](/pl/channels/nostr)             |
| Voice Call      | `@openclaw/voice-call` | [Voice Call](/pl/plugins/voice-call)   |
| Zalo            | `@openclaw/zalo`      | [Zalo](/pl/channels/zalo)               |
| Zalo Personal   | `@openclaw/zalouser`  | [Zalo Personal](/pl/plugins/zalouser)   |

### Core (dostarczane z OpenClaw)

<AccordionGroup>
  <Accordion title="Providerzy modeli (włączone domyślnie)">
    `anthropic`, `byteplus`, `cloudflare-ai-gateway`, `github-copilot`, `google`,
    `huggingface`, `kilocode`, `kimi-coding`, `minimax`, `mistral`, `qwen`,
    `moonshot`, `nvidia`, `openai`, `opencode`, `opencode-go`, `openrouter`,
    `qianfan`, `synthetic`, `together`, `venice`,
    `vercel-ai-gateway`, `volcengine`, `xiaomi`, `zai`
  </Accordion>

  <Accordion title="Pluginy pamięci">
    - `memory-core` — bundled memory search (domyślnie przez `plugins.slots.memory`)
    - `memory-lancedb` — instalowana na żądanie pamięć długoterminowa z auto-recall/capture (ustaw `plugins.slots.memory = "memory-lancedb"`)
  </Accordion>

  <Accordion title="Providerzy mowy (włączone domyślnie)">
    `elevenlabs`, `microsoft`
  </Accordion>

  <Accordion title="Inne">
    - `browser` — bundled browser plugin dla narzędzia browser, CLI `openclaw browser`, metody gatewaya `browser.request`, runtime przeglądarki i domyślnej usługi sterowania przeglądarką (włączony domyślnie; wyłącz go przed zastąpieniem)
    - `copilot-proxy` — most VS Code Copilot Proxy (domyślnie wyłączony)
  </Accordion>
</AccordionGroup>

Szukasz pluginów firm trzecich? Zobacz [Community Plugins](/pl/plugins/community).

## Konfiguracja

```json5
{
  plugins: {
    enabled: true,
    allow: ["voice-call"],
    deny: ["untrusted-plugin"],
    load: { paths: ["~/Projects/oss/voice-call-extension"] },
    entries: {
      "voice-call": { enabled: true, config: { provider: "twilio" } },
    },
  },
}
```

| Pole             | Opis                                                      |
| ---------------- | --------------------------------------------------------- |
| `enabled`        | Główny przełącznik (domyślnie: `true`)                    |
| `allow`          | Allowlist pluginów (opcjonalnie)                          |
| `deny`           | Denylist pluginów (opcjonalnie; `deny` ma pierwszeństwo)  |
| `load.paths`     | Dodatkowe pliki/katalogi pluginów                         |
| `slots`          | Selektory wyłącznych slotów (np. `memory`, `contextEngine`) |
| `entries.\<id\>` | Przełączniki i konfiguracja dla poszczególnych pluginów   |

Zmiany konfiguracji **wymagają restartu gatewaya**. Jeśli Gateway działa z watcherem
konfiguracji i restartem in-process (domyślna ścieżka `openclaw gateway`), ten
restart zwykle jest wykonywany automatycznie chwilę po zapisaniu konfiguracji.

<Accordion title="Stany pluginów: disabled vs missing vs invalid">
  - **Disabled**: plugin istnieje, ale reguły włączania go wyłączyły. Konfiguracja jest zachowywana.
  - **Missing**: konfiguracja odwołuje się do identyfikatora pluginu, którego wykrywanie nie znalazło.
  - **Invalid**: plugin istnieje, ale jego konfiguracja nie pasuje do zadeklarowanego schematu.
</Accordion>

## Wykrywanie i pierwszeństwo

OpenClaw skanuje pluginy w tej kolejności (pierwsze dopasowanie wygrywa):

<Steps>
  <Step title="Ścieżki konfiguracji">
    `plugins.load.paths` — jawne ścieżki plików lub katalogów.
  </Step>

  <Step title="Rozszerzenia workspace">
    `\<workspace\>/.openclaw/<plugin-root>/*.ts` i `\<workspace\>/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Globalne rozszerzenia">
    `~/.openclaw/<plugin-root>/*.ts` i `~/.openclaw/<plugin-root>/*/index.ts`.
  </Step>

  <Step title="Bundled plugins">
    Dostarczane z OpenClaw. Wiele z nich jest włączonych domyślnie (providerzy modeli, mowa).
    Inne wymagają jawnego włączenia.
  </Step>
</Steps>

### Reguły włączania

- `plugins.enabled: false` wyłącza wszystkie pluginy
- `plugins.deny` zawsze ma pierwszeństwo przed `allow`
- `plugins.entries.\<id\>.enabled: false` wyłącza dany plugin
- Pluginy pochodzące z workspace są **domyślnie wyłączone** (muszą zostać jawnie włączone)
- Bundled plugins stosują wbudowany zestaw domyślnie włączony, chyba że zostanie nadpisany
- Wyłączne sloty mogą wymusić włączenie wybranego pluginu dla danego slotu

## Sloty pluginów (wyłączne kategorie)

Niektóre kategorie są wyłączne (tylko jedna aktywna naraz):

```json5
{
  plugins: {
    slots: {
      memory: "memory-core", // lub "none", aby wyłączyć
      contextEngine: "legacy", // lub id pluginu
    },
  },
}
```

| Slot            | Co kontroluje         | Domyślnie           |
| --------------- | --------------------- | ------------------- |
| `memory`        | Aktywny plugin pamięci | `memory-core`      |
| `contextEngine` | Aktywny silnik kontekstu | `legacy` (wbudowany) |

## Dokumentacja CLI

```bash
openclaw plugins list                       # zwięzły spis
openclaw plugins list --enabled            # tylko załadowane pluginy
openclaw plugins list --verbose            # szczegółowe linie dla każdego pluginu
openclaw plugins list --json               # spis czytelny maszynowo
openclaw plugins inspect <id>              # szczegółowe informacje
openclaw plugins inspect <id> --json       # format czytelny maszynowo
openclaw plugins inspect --all             # tabela dla całej floty
openclaw plugins info <id>                 # alias inspect
openclaw plugins doctor                    # diagnostyka

openclaw plugins install <package>         # instalacja (najpierw ClawHub, potem npm)
openclaw plugins install clawhub:<pkg>     # instalacja tylko z ClawHub
openclaw plugins install <spec> --force    # nadpisz istniejącą instalację
openclaw plugins install <path>            # instalacja z lokalnej ścieżki
openclaw plugins install -l <path>         # link (bez kopiowania) do dev
openclaw plugins install <plugin> --marketplace <source>
openclaw plugins install <plugin> --marketplace https://github.com/<owner>/<repo>
openclaw plugins install <spec> --pin      # zapisz dokładnie rozwiązaną specyfikację npm
openclaw plugins install <spec> --dangerously-force-unsafe-install
openclaw plugins update <id>             # zaktualizuj jeden plugin
openclaw plugins update <id> --dangerously-force-unsafe-install
openclaw plugins update --all            # zaktualizuj wszystkie
openclaw plugins uninstall <id>          # usuń rekordy konfiguracji/instalacji
openclaw plugins uninstall <id> --keep-files
openclaw plugins marketplace list <source>
openclaw plugins marketplace list <source> --json

openclaw plugins enable <id>
openclaw plugins disable <id>
```

Bundled plugins są dostarczane z OpenClaw. Wiele z nich jest włączonych domyślnie (na przykład
bundled providerzy modeli, bundled providerzy mowy i bundled browser
plugin). Inne bundled plugins nadal wymagają `openclaw plugins enable <id>`.

`--force` nadpisuje istniejący zainstalowany plugin lub pakiet hooków w miejscu.
Nie jest obsługiwane z `--link`, które ponownie używa ścieżki źródłowej zamiast
kopiowania do zarządzanego celu instalacji.

`--pin` działa tylko dla npm. Nie jest obsługiwane z `--marketplace`, ponieważ
instalacje marketplace zapisują metadane źródła marketplace zamiast specyfikacji npm.

`--dangerously-force-unsafe-install` to awaryjne nadpisanie dla fałszywych
pozytywów z wbudowanego skanera niebezpiecznego kodu. Pozwala kontynuować instalację
i aktualizację pluginów mimo wbudowanych ustaleń `critical`, ale nadal
nie omija blokad polityki pluginów `before_install` ani blokowania przy błędzie skanowania.

Ta flaga CLI dotyczy tylko przepływów instalacji/aktualizacji pluginów. Instalacje zależności Skills
wykonywane przez Gateway używają zamiast tego odpowiadającego nadpisania żądania `dangerouslyForceUnsafeInstall`, natomiast `openclaw skills install` pozostaje osobnym przepływem pobierania/instalacji Skills z ClawHub.

Zgodne bundle'e uczestniczą w tym samym przepływie list/inspect/enable/disable
co pluginy. Obecne wsparcie runtime obejmuje bundle Skills, Claude command-skills,
domyślne ustawienia Claude `settings.json`, domyślne ustawienia Claude `.lsp.json` oraz manifest-declared
`lspServers`, Cursor command-skills i zgodne katalogi hooków Codex.

`openclaw plugins inspect <id>` raportuje również wykryte capabilities bundle'a oraz
obsługiwane lub nieobsługiwane wpisy serwerów MCP i LSP dla pluginów opartych na bundle'ach.

Źródła marketplace mogą być nazwą znanego marketplace Claude z
`~/.claude/plugins/known_marketplaces.json`, lokalnym katalogiem marketplace albo
ścieżką `marketplace.json`, skrótem GitHub typu `owner/repo`, URL repozytorium GitHub
albo URL git. W przypadku zdalnych marketplace wpisy pluginów muszą pozostać wewnątrz
sklonowanego repozytorium marketplace i używać wyłącznie źródeł ze ścieżkami względnymi.

Pełne szczegóły znajdziesz w [dokumentacji CLI `openclaw plugins`](/cli/plugins).

## Przegląd API pluginów

Pluginy Native eksportują obiekt wejściowy udostępniający `register(api)`. Starsze
pluginy mogą nadal używać `activate(api)` jako starszego aliasu, ale nowe pluginy powinny
używać `register`.

```typescript
export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
    api.registerChannel({
      /* ... */
    });
  },
});
```

OpenClaw ładuje obiekt wejściowy i wywołuje `register(api)` podczas aktywacji
pluginu. Loader nadal wraca do `activate(api)` dla starszych pluginów,
ale bundled plugins i nowe pluginy zewnętrzne powinny traktować `register` jako
publiczny kontrakt.

Typowe metody rejestracji:

| Metoda                                  | Co rejestruje                |
| --------------------------------------- | ---------------------------- |
| `registerProvider`                      | Provider modeli (LLM)        |
| `registerChannel`                       | Kanał czatu                  |
| `registerTool`                          | Narzędzie agenta             |
| `registerHook` / `on(...)`              | Hooki cyklu życia            |
| `registerSpeechProvider`                | Text-to-speech / STT         |
| `registerRealtimeTranscriptionProvider` | Strumieniowe STT             |
| `registerRealtimeVoiceProvider`         | Dwukierunkowy głos realtime  |
| `registerMediaUnderstandingProvider`    | Analiza obrazu/audio         |
| `registerImageGenerationProvider`       | Generowanie obrazów          |
| `registerMusicGenerationProvider`       | Generowanie muzyki           |
| `registerVideoGenerationProvider`       | Generowanie wideo            |
| `registerWebFetchProvider`              | Provider web fetch / scrape  |
| `registerWebSearchProvider`             | Web search                   |
| `registerHttpRoute`                     | Endpoint HTTP                |
| `registerCommand` / `registerCli`       | Polecenia CLI                |
| `registerContextEngine`                 | Silnik kontekstu             |
| `registerService`                       | Usługa działająca w tle      |

Zachowanie ochronne hooków dla typowanych hooków cyklu życia:

- `before_tool_call`: `{ block: true }` jest rozstrzygające; handlery o niższym priorytecie są pomijane.
- `before_tool_call`: `{ block: false }` nic nie robi i nie usuwa wcześniejszej blokady.
- `before_install`: `{ block: true }` jest rozstrzygające; handlery o niższym priorytecie są pomijane.
- `before_install`: `{ block: false }` nic nie robi i nie usuwa wcześniejszej blokady.
- `message_sending`: `{ cancel: true }` jest rozstrzygające; handlery o niższym priorytecie są pomijane.
- `message_sending`: `{ cancel: false }` nic nie robi i nie usuwa wcześniejszego anulowania.

Pełne zachowanie typowanych hooków znajdziesz w [SDK Overview](/pl/plugins/sdk-overview#hook-decision-semantics).

## Powiązane

- [Building Plugins](/pl/plugins/building-plugins) — utwórz własny plugin
- [Plugin Bundles](/pl/plugins/bundles) — zgodność bundle'i Codex/Claude/Cursor
- [Plugin Manifest](/pl/plugins/manifest) — schemat manifestu
- [Registering Tools](/pl/plugins/building-plugins#registering-agent-tools) — dodawanie narzędzi agenta w pluginie
- [Plugin Internals](/pl/plugins/architecture) — model capabilities i pipeline ładowania
- [Community Plugins](/pl/plugins/community) — zestawienia pluginów firm trzecich
