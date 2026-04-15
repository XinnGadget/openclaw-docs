---
read_when:
    - Potrzebujesz dokładnej sygnatury typu `definePluginEntry` lub `defineChannelPluginEntry`
    - Chcesz zrozumieć tryb rejestracji (pełny vs konfiguracja vs metadane CLI)
    - Szukasz opcji punktu wejścia
sidebarTitle: Entry Points
summary: Odniesienie do `definePluginEntry`, `defineChannelPluginEntry` i `defineSetupPluginEntry`
title: Punkty wejścia Pluginu
x-i18n:
    generated_at: "2026-04-15T19:41:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: aabca25bc9b8ff1b5bb4852bafe83640ffeba006ea6b6a8eff4e2c37a10f1fe4
    source_path: plugins/sdk-entrypoints.md
    workflow: 15
---

# Punkty wejścia Pluginu

Każdy Plugin eksportuje domyślny obiekt punktu wejścia. SDK udostępnia trzy pomocnicze funkcje do ich tworzenia.

<Tip>
  **Szukasz przewodnika krok po kroku?** Zobacz [Pluginy kanałów](/pl/plugins/sdk-channel-plugins)
  lub [Pluginy dostawców](/pl/plugins/sdk-provider-plugins), aby skorzystać z instrukcji krok po kroku.
</Tip>

## `definePluginEntry`

**Import:** `openclaw/plugin-sdk/plugin-entry`

Dla Pluginów dostawców, Pluginów narzędzi, Pluginów hooków i wszystkiego, co **nie** jest kanałem wiadomości.

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Short summary",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
  },
});
```

| Pole           | Typ                                                              | Wymagane | Domyślnie           |
| -------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id`           | `string`                                                         | Tak      | —                   |
| `name`         | `string`                                                         | Tak      | —                   |
| `description`  | `string`                                                         | Tak      | —                   |
| `kind`         | `string`                                                         | Nie      | —                   |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Nie      | Schemat pustego obiektu |
| `register`     | `(api: OpenClawPluginApi) => void`                               | Tak      | —                   |

- `id` musi odpowiadać manifestowi `openclaw.plugin.json`.
- `kind` służy do wyłącznych slotów: `"memory"` lub `"context-engine"`.
- `configSchema` może być funkcją do leniwej ewaluacji.
- OpenClaw rozwiązuje i zapamiętuje ten schemat przy pierwszym dostępie, więc kosztowne konstruktory schematów uruchamiają się tylko raz.

## `defineChannelPluginEntry`

**Import:** `openclaw/plugin-sdk/channel-core`

Opakowuje `definePluginEntry` logiką specyficzną dla kanałów. Automatycznie wywołuje
`api.registerChannel({ plugin })`, udostępnia opcjonalny punkt integracji metadanych CLI dla pomocy głównej i uzależnia `registerFull` od trybu rejestracji.

```typescript
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineChannelPluginEntry({
  id: "my-channel",
  name: "My Channel",
  description: "Short summary",
  plugin: myChannelPlugin,
  setRuntime: setMyRuntime,
  registerCliMetadata(api) {
    api.registerCli(/* ... */);
  },
  registerFull(api) {
    api.registerGatewayMethod(/* ... */);
  },
});
```

| Pole                  | Typ                                                              | Wymagane | Domyślnie           |
| --------------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id`                  | `string`                                                         | Tak      | —                   |
| `name`                | `string`                                                         | Tak      | —                   |
| `description`         | `string`                                                         | Tak      | —                   |
| `plugin`              | `ChannelPlugin`                                                  | Tak      | —                   |
| `configSchema`        | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Nie      | Schemat pustego obiektu |
| `setRuntime`          | `(runtime: PluginRuntime) => void`                               | Nie      | —                   |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void`                               | Nie      | —                   |
| `registerFull`        | `(api: OpenClawPluginApi) => void`                               | Nie      | —                   |

- `setRuntime` jest wywoływane podczas rejestracji, aby można było przechować referencję do runtime
  (zwykle za pomocą `createPluginRuntimeStore`). Jest pomijane podczas
  przechwytywania metadanych CLI.
- `registerCliMetadata` działa zarówno przy `api.registrationMode === "cli-metadata"`,
  jak i `api.registrationMode === "full"`.
  Używaj go jako kanonicznego miejsca dla deskryptorów CLI należących do kanału, aby pomoc główna
  nie aktywowała ładowania, a jednocześnie zwykła rejestracja poleceń CLI pozostała zgodna
  z pełnym ładowaniem Pluginu.
- `registerFull` działa tylko wtedy, gdy `api.registrationMode === "full"`. Jest pomijane
  podczas ładowania tylko do konfiguracji.
- Podobnie jak `definePluginEntry`, `configSchema` może być leniwą fabryką, a OpenClaw
  zapamiętuje rozwiązany schemat przy pierwszym dostępie.
- Dla głównych poleceń CLI należących do Pluginu preferuj `api.registerCli(..., { descriptors: [...] })`,
  gdy chcesz, aby polecenie pozostało ładowane leniwie bez znikania z
  drzewa parsowania głównego CLI. W przypadku Pluginów kanałów preferuj rejestrowanie takich deskryptorów
  z poziomu `registerCliMetadata(...)`, a `registerFull(...)` pozostaw do pracy wyłącznie związanej z runtime.
- Jeśli `registerFull(...)` rejestruje także metody Gateway RPC, utrzymuj je pod
  prefiksem specyficznym dla Pluginu. Zastrzeżone przestrzenie nazw administracyjnych rdzenia (`config.*`,
  `exec.approvals.*`, `wizard.*`, `update.*`) są zawsze wymuszane do
  `operator.admin`.

## `defineSetupPluginEntry`

**Import:** `openclaw/plugin-sdk/channel-core`

Dla lekkiego pliku `setup-entry.ts`. Zwraca tylko `{ plugin }` bez
logiki runtime ani CLI.

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

OpenClaw ładuje to zamiast pełnego punktu wejścia, gdy kanał jest wyłączony,
nieskonfigurowany lub gdy włączone jest ładowanie odroczone. Zobacz
[Konfiguracja i ustawienia](/pl/plugins/sdk-setup#setup-entry), aby dowiedzieć się, kiedy ma to znaczenie.

W praktyce łącz `defineSetupPluginEntry(...)` z wąskimi rodzinami pomocników konfiguracji:

- `openclaw/plugin-sdk/setup-runtime` dla bezpiecznych względem runtime pomocników konfiguracji, takich jak
  adaptery łatek konfiguracji bezpieczne przy imporcie, dane wyjściowe `lookup-note`,
  `promptResolvedAllowFrom`, `splitSetupEntries` i delegowane proxy konfiguracji
- `openclaw/plugin-sdk/channel-setup` dla powierzchni konfiguracji opcjonalnej instalacji
- `openclaw/plugin-sdk/setup-tools` dla pomocników CLI/archiwum/dokumentacji konfiguracji i instalacji

Ciężkie SDK, rejestrację CLI i długowieczne usługi runtime pozostaw w pełnym
punkcie wejścia.

Kanały workspace dołączone do repozytorium, które rozdzielają powierzchnie konfiguracji i runtime, mogą zamiast tego używać
`defineBundledChannelSetupEntry(...)` z
`openclaw/plugin-sdk/channel-entry-contract`. Ten kontrakt pozwala zachować w punkcie wejścia konfiguracji
eksporty plugin/secrets bezpieczne dla konfiguracji, a jednocześnie nadal udostępnia setter runtime:

```typescript
import { defineBundledChannelSetupEntry } from "openclaw/plugin-sdk/channel-entry-contract";

export default defineBundledChannelSetupEntry({
  importMetaUrl: import.meta.url,
  plugin: {
    specifier: "./channel-plugin-api.js",
    exportName: "myChannelPlugin",
  },
  runtime: {
    specifier: "./runtime-api.js",
    exportName: "setMyChannelRuntime",
  },
});
```

Używaj tego dołączonego kontraktu tylko wtedy, gdy przepływy konfiguracji rzeczywiście wymagają lekkiego
settera runtime przed załadowaniem pełnego punktu wejścia kanału.

## Tryb rejestracji

`api.registrationMode` informuje Plugin, w jaki sposób został załadowany:

| Tryb              | Kiedy                             | Co rejestrować                                                                            |
| ----------------- | --------------------------------- | ----------------------------------------------------------------------------------------- |
| `"full"`          | Normalne uruchomienie Gateway     | Wszystko                                                                                  |
| `"setup-only"`    | Wyłączony/nieskonfigurowany kanał | Tylko rejestrację kanału                                                                  |
| `"setup-runtime"` | Przepływ konfiguracji z dostępnym runtime | Rejestrację kanału oraz tylko lekki runtime potrzebny przed załadowaniem pełnego punktu wejścia |
| `"cli-metadata"`  | Pomoc główna / przechwytywanie metadanych CLI | Tylko deskryptory CLI                                                                     |

`defineChannelPluginEntry` automatycznie obsługuje ten podział. Jeśli używasz
bezpośrednio `definePluginEntry` dla kanału, samodzielnie sprawdzaj tryb:

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // Heavy runtime-only registrations
  api.registerService(/* ... */);
}
```

Traktuj `"setup-runtime"` jako okno, w którym powierzchnie uruchomieniowe tylko do konfiguracji muszą
istnieć bez ponownego wchodzenia do pełnego runtime dołączonego kanału. Dobrze pasują tu:
rejestracja kanału, bezpieczne dla konfiguracji trasy HTTP, bezpieczne dla konfiguracji metody Gateway oraz
delegowane pomocniki konfiguracji. Ciężkie usługi działające w tle, rejestratory CLI oraz bootstrapy SDK dostawców/klientów nadal należą do `"full"`.

Konkretnie dla rejestratorów CLI:

- używaj `descriptors`, gdy rejestrator zarządza co najmniej jednym głównym poleceniem i
  chcesz, aby OpenClaw leniwie załadował rzeczywisty moduł CLI przy pierwszym wywołaniu
- upewnij się, że te deskryptory obejmują każdy główny korzeń poleceń udostępniany przez
  rejestrator
- używaj samego `commands` tylko dla ścieżek zgodności eager

## Kształty Pluginów

OpenClaw klasyfikuje załadowane Pluginy według ich zachowania podczas rejestracji:

| Kształt               | Opis                                               |
| --------------------- | -------------------------------------------------- |
| **plain-capability**  | Jeden typ capability (np. tylko dostawca)          |
| **hybrid-capability** | Wiele typów capability (np. dostawca + mowa)       |
| **hook-only**         | Tylko hooki, bez capability                        |
| **non-capability**    | Narzędzia/polecenia/usługi, ale bez capability     |

Użyj `openclaw plugins inspect <id>`, aby zobaczyć kształt Pluginu.

## Powiązane

- [Przegląd SDK](/pl/plugins/sdk-overview) — API rejestracji i opis subpathów
- [Pomocniki runtime](/pl/plugins/sdk-runtime) — `api.runtime` i `createPluginRuntimeStore`
- [Konfiguracja i ustawienia](/pl/plugins/sdk-setup) — manifest, punkt wejścia konfiguracji, ładowanie odroczone
- [Pluginy kanałów](/pl/plugins/sdk-channel-plugins) — budowanie obiektu `ChannelPlugin`
- [Pluginy dostawców](/pl/plugins/sdk-provider-plugins) — rejestracja dostawcy i hooki
