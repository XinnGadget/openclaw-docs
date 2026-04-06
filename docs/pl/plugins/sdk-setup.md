---
read_when:
    - Dodajesz kreator konfiguracji do pluginu OpenClaw
    - Musisz zrozumieć różnicę między setup-entry.ts a index.ts
    - Definiujesz schematy konfiguracji pluginu albo metadane openclaw w package.json
sidebarTitle: Setup and Config
summary: Kreatory konfiguracji, setup-entry.ts, schematy konfiguracji i metadane openclaw w package.json
title: Konfiguracja i setup pluginu
x-i18n:
    generated_at: "2026-04-06T03:11:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: eac2586516d27bcd94cc4c259fe6274c792b3f9938c7ddd6dbf04a6dbb988dc9
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Konfiguracja i setup pluginu

Dokumentacja referencyjna dla pakowania pluginów (metadane `package.json`), manifestów
(`openclaw.plugin.json`), wpisów setup, oraz schematów konfiguracji.

<Tip>
  **Szukasz przewodnika krok po kroku?** Przewodniki how-to omawiają pakowanie w odpowiednim kontekście:
  [Channel Plugins](/pl/plugins/sdk-channel-plugins#step-1-package-and-manifest) i
  [Provider Plugins](/pl/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## Metadane pakietu

Twój `package.json` potrzebuje pola `openclaw`, które mówi systemowi pluginów, co
udostępnia Twój plugin:

**Plugin kanału:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Krótki opis kanału."
    }
  }
}
```

**Plugin dostawcy / bazowy wariant publikacji ClawHub:**

```json openclaw-clawhub-package.json
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

Jeśli publikujesz plugin zewnętrznie w ClawHub, te pola `compat` i `build`
są wymagane. Kanoniczne fragmenty publikacji znajdują się w
`docs/snippets/plugin-publish/`.

### Pola `openclaw`

| Pole         | Typ        | Opis                                                                                                 |
| ------------ | ---------- | ---------------------------------------------------------------------------------------------------- |
| `extensions` | `string[]` | Pliki punktów wejścia (względnie do katalogu głównego pakietu)                                       |
| `setupEntry` | `string`   | Lekki wpis tylko do setupu (opcjonalny)                                                              |
| `channel`    | `object`   | Metadane katalogu kanału dla powierzchni setupu, selektora, szybkiego startu i statusu              |
| `providers`  | `string[]` | ID dostawców rejestrowanych przez ten plugin                                                         |
| `install`    | `object`   | Wskazówki instalacji: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | Flagi zachowania przy uruchamianiu                                                                   |

### `openclaw.channel`

`openclaw.channel` to lekkie metadane pakietu dla wykrywania kanału i powierzchni setupu
przed załadowaniem runtime.

| Pole                                   | Typ        | Co oznacza                                                                    |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id`                                   | `string`   | Kanoniczne ID kanału.                                                         |
| `label`                                | `string`   | Główna etykieta kanału.                                                       |
| `selectionLabel`                       | `string`   | Etykieta w selektorze/setupie, gdy powinna różnić się od `label`.             |
| `detailLabel`                          | `string`   | Dodatkowa etykieta szczegółowa dla bogatszych katalogów kanałów i powierzchni statusu. |
| `docsPath`                             | `string`   | Ścieżka dokumentacji dla linków setupu i wyboru.                              |
| `docsLabel`                            | `string`   | Nadpisana etykieta używana dla linków do dokumentacji, gdy powinna różnić się od ID kanału. |
| `blurb`                                | `string`   | Krótki opis do onboardingu/katalogu.                                          |
| `order`                                | `number`   | Kolejność sortowania w katalogach kanałów.                                    |
| `aliases`                              | `string[]` | Dodatkowe aliasy wyszukiwania dla wyboru kanału.                              |
| `preferOver`                           | `string[]` | ID pluginów/kanałów o niższym priorytecie, które ten kanał powinien wyprzedzać. |
| `systemImage`                          | `string`   | Opcjonalna nazwa ikony/system image dla katalogów UI kanału.                  |
| `selectionDocsPrefix`                  | `string`   | Tekst prefiksu przed linkami do dokumentacji na powierzchniach wyboru.        |
| `selectionDocsOmitLabel`               | `boolean`  | Pokaż ścieżkę dokumentacji bezpośrednio zamiast opisanego linku do dokumentacji w tekście wyboru. |
| `selectionExtras`                      | `string[]` | Dodatkowe krótkie ciągi dołączane do tekstu wyboru.                           |
| `markdownCapable`                      | `boolean`  | Oznacza kanał jako obsługujący Markdown dla decyzji o formatowaniu wychodzącym. |
| `exposure`                             | `object`   | Kontrola widoczności kanału dla powierzchni setupu, list skonfigurowanych i dokumentacji. |
| `quickstartAllowFrom`                  | `boolean`  | Włącza ten kanał do standardowego przepływu szybkiego startu `allowFrom`.     |
| `forceAccountBinding`                  | `boolean`  | Wymaga jawnego powiązania konta, nawet gdy istnieje tylko jedno konto.        |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | Preferuje wyszukiwanie sesji przy rozstrzyganiu celów ogłoszeń dla tego kanału. |

Przykład:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Samohostowana integracja czatu oparta na webhookach.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Przewodnik:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "exposure": {
        "configured": true,
        "setup": true,
        "docs": true
      },
      "quickstartAllowFrom": true
    }
  }
}
```

`exposure` obsługuje:

- `configured`: uwzględnij kanał na powierzchniach list skonfigurowanych / podobnych do statusu
- `setup`: uwzględnij kanał w interaktywnych selektorach setupu/konfiguracji
- `docs`: oznacz kanał jako publicznie widoczny na powierzchniach dokumentacji/nawigacji

`showConfigured` i `showInSetup` nadal są obsługiwane jako starsze aliasy. Preferowane jest
`exposure`.

### `openclaw.install`

`openclaw.install` to metadane pakietu, a nie metadane manifestu.

| Pole                         | Typ                  | Co oznacza                                                                      |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | Kanoniczna specyfikacja npm dla przepływów instalacji/aktualizacji.             |
| `localPath`                  | `string`             | Lokalna ścieżka instalacji deweloperskiej lub bundlowanej.                      |
| `defaultChoice`              | `"npm"` \| `"local"` | Preferowane źródło instalacji, gdy oba są dostępne.                             |
| `minHostVersion`             | `string`             | Minimalna obsługiwana wersja OpenClaw w formacie `>=x.y.z`.                     |
| `allowInvalidConfigRecovery` | `boolean`            | Pozwala przepływom ponownej instalacji bundlowanych pluginów odzyskać działanie po określonych błędach nieaktualnej konfiguracji. |

Jeśli ustawiono `minHostVersion`, zarówno instalacja, jak i ładowanie rejestru manifestów
wymuszają to ograniczenie. Starsze hosty pomijają plugin; nieprawidłowe ciągi wersji są odrzucane.

`allowInvalidConfigRecovery` nie jest ogólnym obejściem dla uszkodzonych konfiguracji. Służy
wyłącznie do wąskiego odzyskiwania bundlowanych pluginów, tak aby ponowna instalacja/setup mogły naprawić znane
pozostałości po aktualizacji, takie jak brakująca ścieżka bundlowanego pluginu albo nieaktualny wpis `channels.<id>`
dla tego samego pluginu. Jeśli konfiguracja jest uszkodzona z niezwiązanych powodów, instalacja
nadal kończy się fail-closed i informuje operatora, aby uruchomił `openclaw doctor --fix`.

### Odroczone pełne ładowanie

Pluginy kanałów mogą włączyć odroczone ładowanie przez:

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

Gdy to jest włączone, OpenClaw ładuje tylko `setupEntry` podczas fazy uruchamiania
przed nasłuchiwaniem, nawet dla już skonfigurowanych kanałów. Pełny wpis ładuje się po
rozpoczęciu nasłuchiwania przez bramę.

<Warning>
  Włączaj odroczone ładowanie tylko wtedy, gdy `setupEntry` rejestruje wszystko, czego
  brama potrzebuje przed rozpoczęciem nasłuchiwania (rejestrację kanału, trasy HTTP,
  metody gateway). Jeśli pełny wpis posiada wymagane możliwości startowe, zachowaj
  domyślne zachowanie.
</Warning>

Jeśli Twój wpis setupu/pełny wpis rejestruje metody RPC gateway, utrzymuj je w
prefiksie specyficznym dla pluginu. Zastrzeżone przestrzenie nazw administracji rdzenia (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) pozostają własnością rdzenia i zawsze są rozstrzygane
do `operator.admin`.

## Manifest pluginu

Każdy natywny plugin musi dostarczać `openclaw.plugin.json` w katalogu głównym pakietu.
OpenClaw używa tego do walidacji konfiguracji bez wykonywania kodu pluginu.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Dodaje możliwości My Plugin do OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Sekret weryfikacji webhooka"
      }
    }
  }
}
```

Dla pluginów kanałów dodaj `kind` i `channels`:

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

Nawet pluginy bez konfiguracji muszą dostarczać schemat. Pusty schemat jest prawidłowy:

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

Zobacz [Plugin Manifest](/pl/plugins/manifest), aby poznać pełną dokumentację schematu.

## Publikowanie w ClawHub

Dla pakietów pluginów używaj polecenia ClawHub specyficznego dla pakietu:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Starszy alias publikacji tylko dla Skills dotyczy Skills. Pakiety pluginów
zawsze powinny używać `clawhub package publish`.

## Wpis setup

Plik `setup-entry.ts` jest lekką alternatywą dla `index.ts`, którą
OpenClaw ładuje, gdy potrzebuje tylko powierzchni setupu (onboarding, naprawa konfiguracji,
inspekcja wyłączonego kanału).

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

Pozwala to uniknąć ładowania ciężkiego kodu runtime (bibliotek kryptograficznych, rejestracji CLI,
usług działających w tle) podczas przepływów setupu.

**Kiedy OpenClaw używa `setupEntry` zamiast pełnego wpisu:**

- Kanał jest wyłączony, ale potrzebuje powierzchni setupu/onboardingu
- Kanał jest włączony, ale nieskonfigurowany
- Włączono odroczone ładowanie (`deferConfiguredChannelFullLoadUntilAfterListen`)

**Co musi rejestrować `setupEntry`:**

- Obiekt pluginu kanału (przez `defineSetupPluginEntry`)
- Wszelkie trasy HTTP wymagane przed rozpoczęciem nasłuchiwania przez bramę
- Wszelkie metody gateway potrzebne podczas uruchamiania

Te startowe metody gateway nadal powinny unikać zastrzeżonych przestrzeni nazw administracji rdzenia,
takich jak `config.*` czy `update.*`.

**Czego `setupEntry` NIE powinien zawierać:**

- Rejestracji CLI
- Usług działających w tle
- Ciężkich importów runtime (crypto, SDK)
- Metod gateway potrzebnych dopiero po uruchomieniu

### Wąskie importy helperów setupu

Dla gorących ścieżek tylko do setupu preferuj wąskie warstwy helperów setupu zamiast szerszego
parasola `plugin-sdk/setup`, jeśli potrzebujesz tylko części powierzchni setupu:

| Ścieżka importu                    | Użycie                                                                                  | Kluczowe eksporty                                                                                                                                                                                                                                                                           |
| ---------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`         | helpery runtime na czas setupu, które pozostają dostępne w `setupEntry` / odroczonym starcie kanału | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | adaptery setupu kont uwzględniające środowisko                                          | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                       |
| `plugin-sdk/setup-tools`           | helpery setupu/instalacji CLI/archiwów/dokumentacji                                     | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                             |

Użyj szerszej warstwy `plugin-sdk/setup`, gdy potrzebujesz pełnego współdzielonego
zestawu narzędzi setupu, w tym helperów do patchowania konfiguracji, takich jak
`moveSingleAccountChannelSectionToDefaultAccount(...)`.

Adaptery patchowania setupu pozostają bezpieczne dla gorącej ścieżki przy imporcie. Ich bundlowane
wyszukiwanie powierzchni kontraktów promocji pojedynczego konta jest leniwe, więc import
`plugin-sdk/setup-runtime` nie ładuje eagerly wykrywania bundlowanych powierzchni kontraktów, dopóki adapter nie zostanie faktycznie użyty.

### Promocja pojedynczego konta należąca do kanału

Gdy kanał przechodzi z konfiguracji najwyższego poziomu dla pojedynczego konta do
`channels.<id>.accounts.*`, domyślne współdzielone zachowanie polega na przeniesieniu wartości
o zakresie konta do `accounts.default`.

Bundlowane kanały mogą zawężać lub nadpisywać tę promocję przez swoją powierzchnię kontraktu setupu:

- `singleAccountKeysToMove`: dodatkowe klucze najwyższego poziomu, które powinny zostać przeniesione do
  promowanego konta
- `namedAccountPromotionKeys`: gdy nazwane konta już istnieją, tylko te
  klucze są przenoszone do promowanego konta; współdzielone klucze zasad/dostarczania pozostają w katalogu głównym
  kanału
- `resolveSingleAccountPromotionTarget(...)`: wybiera, które istniejące konto
  otrzyma promowane wartości

Matrix jest obecnym bundlowanym przykładem. Jeśli istnieje dokładnie jedno nazwane konto Matrix
albo jeśli `defaultAccount` wskazuje na istniejący niekanoniczny klucz, taki jak `Ops`,
promocja zachowuje to konto zamiast tworzyć nowy wpis `accounts.default`.

## Schemat konfiguracji

Konfiguracja pluginu jest walidowana względem JSON Schema w Twoim manifeście. Użytkownicy
konfigurują pluginy przez:

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

Twój plugin otrzymuje tę konfigurację jako `api.pluginConfig` podczas rejestracji.

Dla konfiguracji specyficznej dla kanału użyj zamiast tego sekcji konfiguracji kanału:

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### Budowanie schematów konfiguracji kanału

Użyj `buildChannelConfigSchema` z `openclaw/plugin-sdk/core`, aby przekształcić
schemat Zod w opakowanie `ChannelConfigSchema`, które OpenClaw waliduje:

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## Kreatory konfiguracji

Pluginy kanałów mogą dostarczać interaktywne kreatory konfiguracji dla `openclaw onboard`.
Kreator jest obiektem `ChannelSetupWizard` w `ChannelPlugin`:

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

Typ `ChannelSetupWizard` obsługuje `credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize` i inne.
Pełne przykłady znajdziesz w bundlowanych pakietach pluginów (na przykład plugin Discord `src/channel.setup.ts`).

Dla promptów listy dozwolonych DM, które potrzebują tylko standardowego przepływu
`note -> prompt -> parse -> merge -> patch`, preferuj współdzielone helpery setupu
z `openclaw/plugin-sdk/setup`: `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)` i
`createNestedChannelParsedAllowFromPrompt(...)`.

Dla bloków statusu konfiguracji kanału, które różnią się tylko etykietami, wynikami i opcjonalnymi
dodatkowymi liniami, preferuj `createStandardChannelSetupStatus(...)` z
`openclaw/plugin-sdk/setup` zamiast ręcznego tworzenia tego samego obiektu `status` w
każdym pluginie.

Dla opcjonalnych powierzchni setupu, które powinny pojawiać się tylko w określonych kontekstach, użyj
`createOptionalChannelSetupSurface` z `openclaw/plugin-sdk/channel-setup`:

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Returns { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup` udostępnia także niższego poziomu konstruktory
`createOptionalChannelSetupAdapter(...)` i
`createOptionalChannelSetupWizard(...)`, gdy potrzebujesz tylko jednej połowy
tej opcjonalnej powierzchni instalacji.

Wygenerowany opcjonalny adapter/kreator działa fail-closed przy rzeczywistych zapisach konfiguracji. Ponownie
wykorzystuje jeden komunikat o wymaganej instalacji w `validateInput`,
`applyAccountConfig` i `finalize`, a gdy ustawiono `docsPath`, dołącza link do dokumentacji.

Dla interfejsów setupu opartych na binariach preferuj współdzielone delegowane helpery zamiast
kopiowania tej samej logiki binariów/statusu do każdego kanału:

- `createDetectedBinaryStatus(...)` dla bloków statusu, które różnią się tylko etykietami,
  wskazówkami, wynikami i wykrywaniem binariów
- `createCliPathTextInput(...)` dla wejść tekstowych opartych na ścieżce
- `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)` i
  `createDelegatedResolveConfigured(...)`, gdy `setupEntry` musi leniwie przekazać dalej cięższy pełny kreator
- `createDelegatedTextInputShouldPrompt(...)`, gdy `setupEntry` musi tylko
  delegować decyzję `textInputs[*].shouldPrompt`

## Publikowanie i instalacja

**Pluginy zewnętrzne:** opublikuj do [ClawHub](/pl/tools/clawhub) albo npm, a następnie zainstaluj:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw najpierw próbuje ClawHub i automatycznie przechodzi do npm jako fallback. Możesz też
jawnie wymusić ClawHub:

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # tylko ClawHub
```

Nie ma odpowiadającego nadpisania `npm:`. Użyj zwykłej specyfikacji pakietu npm, jeśli
chcesz ścieżki npm po fallbacku z ClawHub:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**Pluginy w repo:** umieść je w drzewie workspace bundlowanych pluginów, a będą automatycznie
wykrywane podczas builda.

**Użytkownicy mogą instalować:**

```bash
openclaw plugins install <package-name>
```

<Info>
  Dla instalacji pochodzących z npm `openclaw plugins install` uruchamia
  `npm install --ignore-scripts` (bez skryptów lifecycle). Utrzymuj drzewo zależności pluginu
  jako czyste JS/TS i unikaj pakietów wymagających buildów `postinstall`.
</Info>

## Powiązane

- [SDK Entry Points](/pl/plugins/sdk-entrypoints) -- `definePluginEntry` i `defineChannelPluginEntry`
- [Plugin Manifest](/pl/plugins/manifest) -- pełna dokumentacja schematu manifestu
- [Building Plugins](/pl/plugins/building-plugins) -- przewodnik krok po kroku dla początkujących
