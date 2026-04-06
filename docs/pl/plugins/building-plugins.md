---
read_when:
    - Chcesz utworzyć nowy plugin OpenClaw
    - Potrzebujesz szybkiego startu w tworzeniu pluginów
    - Dodajesz nowy kanał, providera, narzędzie lub inną możliwość do OpenClaw
sidebarTitle: Getting Started
summary: Utwórz swój pierwszy plugin OpenClaw w kilka minut
title: Tworzenie pluginów
x-i18n:
    generated_at: "2026-04-06T03:09:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9be344cb300ecbcba08e593a95bcc93ab16c14b28a0ff0c29b26b79d8249146c
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Tworzenie pluginów

Pluginy rozszerzają OpenClaw o nowe możliwości: kanały, providery modeli,
speech, realtime transcription, realtime voice, media understanding, image
generation, video generation, web fetch, web search, narzędzia agentów lub
dowolne połączenie tych elementów.

Nie musisz dodawać swojego pluginu do repozytorium OpenClaw. Opublikuj go w
[ClawHub](/pl/tools/clawhub) lub npm, a użytkownicy zainstalują go za pomocą
`openclaw plugins install <package-name>`. OpenClaw najpierw próbuje użyć ClawHub, a potem automatycznie przechodzi do npm.

## Wymagania wstępne

- Node >= 22 i menedżer pakietów (npm lub pnpm)
- Znajomość TypeScript (ESM)
- Dla pluginów w repozytorium: sklonowane repozytorium i wykonane `pnpm install`

## Jaki rodzaj pluginu?

<CardGroup cols={3}>
  <Card title="Plugin kanału" icon="messages-square" href="/pl/plugins/sdk-channel-plugins">
    Połącz OpenClaw z platformą komunikacyjną (Discord, IRC itp.)
  </Card>
  <Card title="Plugin providera" icon="cpu" href="/pl/plugins/sdk-provider-plugins">
    Dodaj providera modeli (LLM, proxy lub niestandardowy endpoint)
  </Card>
  <Card title="Plugin narzędzia / hooka" icon="wrench">
    Rejestruj narzędzia agenta, hooki zdarzeń lub usługi — przejdź dalej poniżej
  </Card>
</CardGroup>

Jeśli plugin kanału jest opcjonalny i może nie być zainstalowany podczas działania onboardingu/konfiguracji,
użyj `createOptionalChannelSetupSurface(...)` z
`openclaw/plugin-sdk/channel-setup`. Tworzy on adapter konfiguracji i parę kreatora,
która informuje o wymaganiu instalacji i blokuje rzeczywiste zapisy konfiguracji
do czasu zainstalowania pluginu.

## Szybki start: plugin narzędzia

Ten przewodnik tworzy minimalny plugin, który rejestruje narzędzie agenta. Pluginy kanałów
i providerów mają osobne przewodniki podlinkowane powyżej.

<Steps>
  <Step title="Utwórz pakiet i manifest">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-my-plugin",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Każdy plugin potrzebuje manifestu, nawet jeśli nie ma konfiguracji. Zobacz
    [Manifest](/pl/plugins/manifest), aby poznać pełny schemat. Kanoniczne fragmenty publikacji ClawHub
    znajdują się w `docs/snippets/plugin-publish/`.

  </Step>

  <Step title="Napisz punkt wejścia">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry` jest przeznaczone dla pluginów niebędących pluginami kanałów. Dla kanałów użyj
    `defineChannelPluginEntry` — zobacz [Pluginy kanałów](/pl/plugins/sdk-channel-plugins).
    Pełne opcje punktu wejścia znajdziesz w [Punktach wejścia](/pl/plugins/sdk-entrypoints).

  </Step>

  <Step title="Przetestuj i opublikuj">

    **Pluginy zewnętrzne:** zweryfikuj i opublikuj za pomocą ClawHub, a następnie zainstaluj:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw sprawdza również ClawHub przed npm dla prostych specyfikacji pakietu, takich jak
    `@myorg/openclaw-my-plugin`.

    **Pluginy w repozytorium:** umieść je w drzewie workspace wbudowanych pluginów — zostaną wykryte automatycznie.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Możliwości pluginów

Jeden plugin może rejestrować dowolną liczbę możliwości przez obiekt `api`:

| Capability             | Registration method                              | Detailed guide                                                                  |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| Text inference (LLM)   | `api.registerProvider(...)`                      | [Provider Plugins](/pl/plugins/sdk-provider-plugins)                               |
| Channel / messaging    | `api.registerChannel(...)`                       | [Channel Plugins](/pl/plugins/sdk-channel-plugins)                                 |
| Speech (TTS/STT)       | `api.registerSpeechProvider(...)`                | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime transcription | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Realtime voice         | `api.registerRealtimeVoiceProvider(...)`         | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Media understanding    | `api.registerMediaUnderstandingProvider(...)`    | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Image generation       | `api.registerImageGenerationProvider(...)`       | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Music generation       | `api.registerMusicGenerationProvider(...)`       | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Video generation       | `api.registerVideoGenerationProvider(...)`       | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web fetch              | `api.registerWebFetchProvider(...)`              | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Web search             | `api.registerWebSearchProvider(...)`             | [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Agent tools            | `api.registerTool(...)`                          | Poniżej                                                                         |
| Custom commands        | `api.registerCommand(...)`                       | [Entry Points](/pl/plugins/sdk-entrypoints)                                        |
| Event hooks            | `api.registerHook(...)`                          | [Entry Points](/pl/plugins/sdk-entrypoints)                                        |
| HTTP routes            | `api.registerHttpRoute(...)`                     | [Internals](/pl/plugins/architecture#gateway-http-routes)                          |
| CLI subcommands        | `api.registerCli(...)`                           | [Entry Points](/pl/plugins/sdk-entrypoints)                                        |

Pełne API rejestracji znajdziesz w [Przeglądzie SDK](/pl/plugins/sdk-overview#registration-api).

Jeśli Twój plugin rejestruje niestandardowe metody gateway RPC, trzymaj je pod
prefiksem specyficznym dla pluginu. Przestrzenie nazw administracyjnych core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) pozostają zarezerwowane i zawsze są rozwiązywane do
`operator.admin`, nawet jeśli plugin prosi o węższy zakres.

Semantyka strażników hooków, o której warto pamiętać:

- `before_tool_call`: `{ block: true }` jest terminalne i zatrzymuje handlery o niższym priorytecie.
- `before_tool_call`: `{ block: false }` jest traktowane jako brak decyzji.
- `before_tool_call`: `{ requireApproval: true }` wstrzymuje wykonanie agenta i prosi użytkownika o zatwierdzenie przez nakładkę zatwierdzeń exec, przyciski Telegram, interakcje Discord lub polecenie `/approve` na dowolnym kanale.
- `before_install`: `{ block: true }` jest terminalne i zatrzymuje handlery o niższym priorytecie.
- `before_install`: `{ block: false }` jest traktowane jako brak decyzji.
- `message_sending`: `{ cancel: true }` jest terminalne i zatrzymuje handlery o niższym priorytecie.
- `message_sending`: `{ cancel: false }` jest traktowane jako brak decyzji.

Polecenie `/approve` obsługuje zarówno zatwierdzenia exec, jak i pluginów z ograniczonym fallbackiem: gdy nie znajdzie identyfikatora zatwierdzenia exec, OpenClaw ponawia próbę z tym samym identyfikatorem przez zatwierdzenia pluginów. Przekazywanie zatwierdzeń pluginów można konfigurować niezależnie przez `approvals.plugin` w konfiguracji.

Jeśli niestandardowa logika zatwierdzeń musi wykryć ten sam przypadek ograniczonego fallbacku,
preferuj `isApprovalNotFoundError` z `openclaw/plugin-sdk/error-runtime`
zamiast ręcznego dopasowywania ciągów wygaśnięcia zatwierdzeń.

Szczegóły znajdziesz w [semantyce decyzji hooków w Przeglądzie SDK](/pl/plugins/sdk-overview#hook-decision-semantics).

## Rejestrowanie narzędzi agenta

Narzędzia to typowane funkcje, które może wywoływać LLM. Mogą być wymagane (zawsze
dostępne) lub opcjonalne (włączane przez użytkownika):

```typescript
register(api) {
  // Required tool — always available
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // Optional tool — user must add to allowlist
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

Użytkownicy włączają opcjonalne narzędzia w konfiguracji:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- Nazwy narzędzi nie mogą kolidować z narzędziami core (konflikty są pomijane)
- Używaj `optional: true` dla narzędzi z efektami ubocznymi lub dodatkowymi wymaganiami binarnymi
- Użytkownicy mogą włączyć wszystkie narzędzia z pluginu, dodając identyfikator pluginu do `tools.allow`

## Konwencje importu

Zawsze importuj z ukierunkowanych ścieżek `openclaw/plugin-sdk/<subpath>`:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// Wrong: monolithic root (deprecated, will be removed)
import { ... } from "openclaw/plugin-sdk";
```

Pełne odwołanie do subpath znajdziesz w [Przeglądzie SDK](/pl/plugins/sdk-overview).

W obrębie swojego pluginu używaj lokalnych plików barrel (`api.ts`, `runtime-api.ts`) do
wewnętrznych importów — nigdy nie importuj własnego pluginu przez jego ścieżkę SDK.

W przypadku pluginów providerów trzymaj pomocniki specyficzne dla providera w tych plikach barrel
w katalogu głównym pakietu, chyba że dany punkt styku jest rzeczywiście ogólny. Bieżące przykłady wbudowane:

- Anthropic: wrappery strumieni Claude oraz helpery `service_tier` / beta
- OpenAI: konstruktory providerów, helpery modeli domyślnych, providery realtime
- OpenRouter: konstruktor providera oraz helpery onboardingu/konfiguracji

Jeśli helper jest użyteczny tylko wewnątrz jednego wbudowanego pakietu providera, pozostaw go na tej
powierzchni w katalogu głównym pakietu zamiast promować go do `openclaw/plugin-sdk/*`.

Niektóre generowane powierzchnie helperów `openclaw/plugin-sdk/<bundled-id>` nadal istnieją dla
utrzymania wbudowanych pluginów i zgodności, na przykład
`plugin-sdk/feishu-setup` lub `plugin-sdk/zalo-setup`. Traktuj je jako powierzchnie
zarezerwowane, a nie jako domyślny wzorzec dla nowych pluginów zewnętrznych.

## Lista kontrolna przed wysłaniem

<Check>**package.json** ma poprawne metadane `openclaw`</Check>
<Check>Manifest **openclaw.plugin.json** jest obecny i poprawny</Check>
<Check>Punkt wejścia używa `defineChannelPluginEntry` lub `definePluginEntry`</Check>
<Check>Wszystkie importy używają ukierunkowanych ścieżek `plugin-sdk/<subpath>`</Check>
<Check>Importy wewnętrzne używają lokalnych modułów, a nie własnych importów SDK</Check>
<Check>Testy przechodzą (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` przechodzi (pluginy w repozytorium)</Check>

## Testowanie wydań beta

1. Obserwuj tagi wydań GitHub w [openclaw/openclaw](https://github.com/openclaw/openclaw/releases) i zasubskrybuj przez `Watch` > `Releases`. Tagi beta mają postać `v2026.3.N-beta.1`. Możesz też włączyć powiadomienia dla oficjalnego konta OpenClaw na X [@openclaw](https://x.com/openclaw), aby otrzymywać ogłoszenia o wydaniach.
2. Przetestuj swój plugin z tagiem beta natychmiast po jego pojawieniu się. Okno przed wydaniem stabilnym zwykle trwa tylko kilka godzin.
3. Po testach napisz w wątku swojego pluginu na kanale Discord `plugin-forum`, używając `all good` albo opisując, co się zepsuło. Jeśli nie masz jeszcze wątku, utwórz go.
4. Jeśli coś się zepsuje, otwórz lub zaktualizuj issue zatytułowane `Beta blocker: <plugin-name> - <summary>` i dodaj etykietę `beta-blocker`. Umieść link do issue w swoim wątku.
5. Otwórz PR do `main` zatytułowany `fix(<plugin-id>): beta blocker - <summary>` i dodaj link do issue zarówno w PR, jak i w swoim wątku na Discord. Współtwórcy nie mogą nadawać etykiet PR, więc tytuł jest sygnałem po stronie PR dla maintainerów i automatyzacji. Blokery z PR są scalane; blokery bez PR mogą mimo to trafić do wydania. Maintainerzy obserwują te wątki podczas testów beta.
6. Brak wiadomości oznacza zielone światło. Jeśli przegapisz okno, poprawka prawdopodobnie trafi do następnego cyklu.

## Następne kroki

<CardGroup cols={2}>
  <Card title="Pluginy kanałów" icon="messages-square" href="/pl/plugins/sdk-channel-plugins">
    Zbuduj plugin kanału komunikacyjnego
  </Card>
  <Card title="Pluginy providerów" icon="cpu" href="/pl/plugins/sdk-provider-plugins">
    Zbuduj plugin providera modeli
  </Card>
  <Card title="Przegląd SDK" icon="book-open" href="/pl/plugins/sdk-overview">
    Mapa importów i dokumentacja API rejestracji
  </Card>
  <Card title="Pomocniki runtime" icon="settings" href="/pl/plugins/sdk-runtime">
    TTS, wyszukiwanie, subagent przez api.runtime
  </Card>
  <Card title="Testowanie" icon="test-tubes" href="/pl/plugins/sdk-testing">
    Narzędzia testowe i wzorce
  </Card>
  <Card title="Manifest pluginu" icon="file-json" href="/pl/plugins/manifest">
    Pełna dokumentacja schematu manifestu
  </Card>
</CardGroup>

## Powiązane

- [Architektura pluginów](/pl/plugins/architecture) — szczegółowe omówienie architektury wewnętrznej
- [Przegląd SDK](/pl/plugins/sdk-overview) — dokumentacja Plugin SDK
- [Manifest](/pl/plugins/manifest) — format manifestu pluginu
- [Pluginy kanałów](/pl/plugins/sdk-channel-plugins) — tworzenie pluginów kanałów
- [Pluginy providerów](/pl/plugins/sdk-provider-plugins) — tworzenie pluginów providerów
