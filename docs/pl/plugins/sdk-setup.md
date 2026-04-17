---
read_when:
    - Dodajesz kreator konfiguracji do Pluginu
    - Musisz zrozumieć `setup-entry.ts` w porównaniu z `index.ts`
    - Definiujesz schematy konfiguracji Pluginu lub metadane openclaw w `package.json`
sidebarTitle: Setup and Config
summary: Kreatory konfiguracji, `setup-entry.ts`, schematy konfiguracji i metadane `package.json`
title: Konfiguracja i ustawienia Pluginu
x-i18n:
    generated_at: "2026-04-15T19:41:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: ddf28e25e381a4a38ac478e531586f59612e1a278732597375f87c2eeefc521b
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Konfiguracja i ustawienia Pluginu

Dokumentacja referencyjna dotycząca pakietowania pluginów (metadane `package.json`), manifestów
(`openclaw.plugin.json`), wpisów konfiguracji oraz schematów konfiguracji.

<Tip>
  **Szukasz instrukcji krok po kroku?** Przewodniki how-to omawiają pakietowanie w kontekście:
  [Pluginy kanałów](/pl/plugins/sdk-channel-plugins#step-1-package-and-manifest) i
  [Pluginy dostawców](/pl/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## Metadane pakietu

Twój `package.json` musi zawierać pole `openclaw`, które informuje system pluginów, co
udostępnia Twój Plugin:

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
      "blurb": "Short description of the channel."
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

Jeśli publikujesz Plugin zewnętrznie w ClawHub, pola `compat` i `build`
są wymagane. Kanoniczne fragmenty do publikacji znajdują się w
`docs/snippets/plugin-publish/`.

### Pola `openclaw`

| Pole         | Typ        | Opis                                                                                                   |
| ------------ | ---------- | ------------------------------------------------------------------------------------------------------ |
| `extensions` | `string[]` | Pliki punktów wejścia (względem katalogu głównego pakietu)                                             |
| `setupEntry` | `string`   | Lekki wpis wyłącznie do konfiguracji (opcjonalny)                                                      |
| `channel`    | `object`   | Metadane katalogu kanału dla konfiguracji, selektora, szybkiego startu i powierzchni statusu          |
| `providers`  | `string[]` | Identyfikatory dostawców rejestrowane przez ten Plugin                                                 |
| `install`    | `object`   | Wskazówki instalacyjne: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | Flagi zachowania podczas uruchamiania                                                                  |

### `openclaw.channel`

`openclaw.channel` to tanie metadane pakietu dla wykrywania kanałów i powierzchni
konfiguracji, zanim środowisko uruchomieniowe zostanie załadowane.

| Pole                                   | Typ        | Znaczenie                                                                     |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id`                                   | `string`   | Kanoniczny identyfikator kanału.                                              |
| `label`                                | `string`   | Główna etykieta kanału.                                                       |
| `selectionLabel`                       | `string`   | Etykieta selektora/konfiguracji, gdy ma się różnić od `label`.                |
| `detailLabel`                          | `string`   | Dodatkowa etykieta szczegółów dla bogatszych katalogów kanałów i powierzchni statusu. |
| `docsPath`                             | `string`   | Ścieżka dokumentacji dla linków konfiguracji i wyboru.                        |
| `docsLabel`                            | `string`   | Etykieta zastępcza używana dla linków do dokumentacji, gdy ma się różnić od identyfikatora kanału. |
| `blurb`                                | `string`   | Krótki opis do onboardingu/katalogu.                                          |
| `order`                                | `number`   | Kolejność sortowania w katalogach kanałów.                                    |
| `aliases`                              | `string[]` | Dodatkowe aliasy wyszukiwania dla wyboru kanału.                              |
| `preferOver`                           | `string[]` | Identyfikatory pluginów/kanałów o niższym priorytecie, które ten kanał ma wyprzedzać. |
| `systemImage`                          | `string`   | Opcjonalna nazwa ikony/obrazu systemowego dla katalogów UI kanałów.           |
| `selectionDocsPrefix`                  | `string`   | Tekst prefiksu przed linkami do dokumentacji na powierzchniach wyboru.        |
| `selectionDocsOmitLabel`               | `boolean`  | Pokazuje bezpośrednio ścieżkę dokumentacji zamiast podpisanego linku na powierzchniach wyboru. |
| `selectionExtras`                      | `string[]` | Dodatkowe krótkie ciągi dołączane na powierzchniach wyboru.                   |
| `markdownCapable`                      | `boolean`  | Oznacza kanał jako obsługujący Markdown na potrzeby decyzji o formatowaniu wychodzącym. |
| `exposure`                             | `object`   | Kontrolki widoczności kanału dla konfiguracji, list skonfigurowanych kanałów i powierzchni dokumentacji. |
| `quickstartAllowFrom`                  | `boolean`  | Włącza ten kanał do standardowego przepływu konfiguracji `allowFrom` szybkiego startu. |
| `forceAccountBinding`                  | `boolean`  | Wymaga jawnego powiązania konta nawet wtedy, gdy istnieje tylko jedno konto.  |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | Preferuje wyszukiwanie sesji przy rozwiązywaniu celów ogłoszeń dla tego kanału. |

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
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
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

- `configured`: uwzględnia kanał na powierzchniach list skonfigurowanych kanałów/w stylu statusu
- `setup`: uwzględnia kanał w interaktywnych selektorach konfiguracji
- `docs`: oznacza kanał jako publicznie widoczny na powierzchniach dokumentacji/nawigacji

`showConfigured` i `showInSetup` nadal są obsługiwane jako starsze aliasy. Preferuj
`exposure`.

### `openclaw.install`

`openclaw.install` to metadane pakietu, a nie metadane manifestu.

| Pole                         | Typ                  | Znaczenie                                                                        |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | Kanoniczna specyfikacja npm dla przepływów instalacji/aktualizacji.             |
| `localPath`                  | `string`             | Lokalna ścieżka instalacji deweloperskiej lub wbudowanej.                       |
| `defaultChoice`              | `"npm"` \| `"local"` | Preferowane źródło instalacji, gdy oba są dostępne.                             |
| `minHostVersion`             | `string`             | Minimalna obsługiwana wersja OpenClaw w formacie `>=x.y.z`.                     |
| `allowInvalidConfigRecovery` | `boolean`            | Umożliwia przepływom ponownej instalacji wbudowanych pluginów odzyskiwanie po wybranych błędach nieaktualnej konfiguracji. |

Jeśli ustawiono `minHostVersion`, zarówno instalacja, jak i ładowanie z rejestru
manifestów będą je egzekwować. Starsze hosty pomijają Plugin; nieprawidłowe ciągi
wersji są odrzucane.

`allowInvalidConfigRecovery` nie jest ogólnym obejściem dla uszkodzonych konfiguracji. Jest
przeznaczone wyłącznie do wąskiego odzyskiwania dla wbudowanych pluginów, aby
ponowna instalacja/konfiguracja mogła naprawić znane pozostałości po aktualizacjach,
takie jak brakująca ścieżka wbudowanego pluginu lub nieaktualny wpis `channels.<id>`
dla tego samego Pluginu. Jeśli konfiguracja jest uszkodzona z innych powodów, instalacja
nadal kończy się bez obejścia i informuje operatora o konieczności uruchomienia `openclaw doctor --fix`.

### Odroczone pełne ładowanie

Pluginy kanałów mogą włączyć odroczone ładowanie za pomocą:

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

Gdy ta opcja jest włączona, OpenClaw ładuje tylko `setupEntry` w fazie uruchamiania
przed rozpoczęciem nasłuchiwania, nawet dla już skonfigurowanych kanałów. Pełny wpis
jest ładowany po tym, jak Gateway zacznie nasłuchiwać.

<Warning>
  Włączaj odroczone ładowanie tylko wtedy, gdy `setupEntry` rejestruje wszystko,
  czego Gateway potrzebuje przed rozpoczęciem nasłuchiwania (rejestracja kanału,
  trasy HTTP, metody Gateway). Jeśli pełny wpis posiada wymagane możliwości
  startowe, pozostaw domyślne zachowanie.
</Warning>

Jeśli Twój wpis konfiguracji/pełny wpis rejestruje metody RPC Gateway, zachowaj je pod
prefiksem specyficznym dla pluginu. Zastrzeżone przestrzenie nazw administracyjnych rdzenia (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) pozostają własnością rdzenia i zawsze są rozwiązywane
do `operator.admin`.

## Manifest Pluginu

Każdy natywny Plugin musi dostarczać plik `openclaw.plugin.json` w katalogu głównym pakietu.
OpenClaw używa go do walidacji konfiguracji bez wykonywania kodu pluginu.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
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

Pełny opis schematu znajdziesz w [Manifeście Pluginu](/pl/plugins/manifest).

## Publikowanie w ClawHub

Dla pakietów pluginów używaj polecenia ClawHub przeznaczonego dla pakietów:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Starszy alias publikacji tylko dla Skills jest przeznaczony dla Skills. Pakiety pluginów powinny
zawsze używać `clawhub package publish`.

## Wpis konfiguracji

Plik `setup-entry.ts` to lekka alternatywa dla `index.ts`, którą
OpenClaw ładuje wtedy, gdy potrzebuje tylko powierzchni konfiguracji (onboarding, naprawa konfiguracji,
inspekcja wyłączonych kanałów).

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

Pozwala to uniknąć ładowania ciężkiego kodu środowiska uruchomieniowego (bibliotek kryptograficznych, rejestracji CLI,
usług działających w tle) podczas przepływów konfiguracji.

Wbudowane kanały workspace, które przechowują eksporty bezpieczne dla konfiguracji w modułach pobocznych,
mogą używać `defineBundledChannelSetupEntry(...)` z
`openclaw/plugin-sdk/channel-entry-contract` zamiast
`defineSetupPluginEntry(...)`. Ten kontrakt dla wbudowanych pluginów obsługuje też opcjonalny eksport
`runtime`, dzięki czemu łączenie środowiska uruchomieniowego w czasie konfiguracji może pozostać lekkie i jawne.

**Kiedy OpenClaw używa `setupEntry` zamiast pełnego wpisu:**

- Kanał jest wyłączony, ale potrzebuje powierzchni konfiguracji/onboardingu
- Kanał jest włączony, ale nieskonfigurowany
- Włączono odroczone ładowanie (`deferConfiguredChannelFullLoadUntilAfterListen`)

**Co `setupEntry` musi zarejestrować:**

- Obiekt pluginu kanału (przez `defineSetupPluginEntry`)
- Wszelkie trasy HTTP wymagane przed rozpoczęciem nasłuchiwania przez Gateway
- Wszelkie metody Gateway potrzebne podczas uruchamiania

Te startowe metody Gateway nadal powinny unikać zastrzeżonych przestrzeni nazw administracyjnych rdzenia,
takich jak `config.*` czy `update.*`.

**Czego `setupEntry` NIE powinien zawierać:**

- Rejestracje CLI
- Usługi działające w tle
- Ciężkie importy środowiska uruchomieniowego (crypto, SDK)
- Metody Gateway potrzebne dopiero po uruchomieniu

### Wąskie importy pomocników konfiguracji

Dla gorących ścieżek wyłącznie konfiguracyjnych preferuj wąskie punkty dostępu pomocników konfiguracji zamiast szerszego
parasola `plugin-sdk/setup`, gdy potrzebujesz tylko części powierzchni konfiguracji:

| Ścieżka importu                     | Używaj do                                                                                | Kluczowe eksporty                                                                                                                                                                                                                                                                             |
| ----------------------------------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`          | pomocniki środowiska uruchomieniowego używane w czasie konfiguracji, dostępne w `setupEntry` / przy odroczonym uruchamianiu kanału | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime`  | adaptery konfiguracji kont świadome środowiska                                           | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                         |
| `plugin-sdk/setup-tools`            | pomocniki CLI/archiwów/dokumentacji dla konfiguracji i instalacji                        | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                               |

Użyj szerszego punktu dostępu `plugin-sdk/setup`, gdy potrzebujesz pełnego współdzielonego
zestawu narzędzi konfiguracji, w tym pomocników do łatania konfiguracji, takich jak
`moveSingleAccountChannelSectionToDefaultAccount(...)`.

Adaptery łatek konfiguracji pozostają bezpieczne dla gorącej ścieżki przy imporcie. Ich wbudowane
leniwe wyszukiwanie powierzchni kontraktu promocji pojedynczego konta sprawia, że import
`plugin-sdk/setup-runtime` nie powoduje natychmiastowego ładowania wykrywania powierzchni kontraktu
wbudowanych pluginów, zanim adapter faktycznie zostanie użyty.

### Promocja pojedynczego konta zarządzana przez kanał

Gdy kanał przechodzi z konfiguracji najwyższego poziomu dla pojedynczego konta do
`channels.<id>.accounts.*`, domyślne współdzielone zachowanie polega na przeniesieniu promowanych
wartości o zakresie konta do `accounts.default`.

Wbudowane kanały mogą zawężać lub nadpisywać tę promocję przez swoją powierzchnię kontraktu
konfiguracji:

- `singleAccountKeysToMove`: dodatkowe klucze najwyższego poziomu, które powinny zostać przeniesione do
  promowanego konta
- `namedAccountPromotionKeys`: gdy nazwane konta już istnieją, tylko te
  klucze są przenoszone do promowanego konta; współdzielone klucze polityki/dostarczania pozostają w katalogu głównym kanału
- `resolveSingleAccountPromotionTarget(...)`: wybiera, które istniejące konto
  otrzyma promowane wartości

Matrix jest obecnie przykładem wbudowanego kanału. Jeśli istnieje dokładnie jedno nazwane konto Matrix
albo jeśli `defaultAccount` wskazuje istniejący niekanoniczny klucz, taki jak
`Ops`, promocja zachowuje to konto zamiast tworzyć nowy wpis
`accounts.default`.

## Schemat konfiguracji

Konfiguracja pluginu jest walidowana względem JSON Schema w manifeście. Użytkownicy
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

Twój Plugin otrzymuje tę konfigurację jako `api.pluginConfig` podczas rejestracji.

W przypadku konfiguracji specyficznej dla kanału użyj zamiast tego sekcji konfiguracji kanału:

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

Użyj `buildChannelConfigSchema` z `openclaw/plugin-sdk/core`, aby przekonwertować
schemat Zod do opakowania `ChannelConfigSchema`, które OpenClaw waliduje:

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

Pluginy kanałów mogą udostępniać interaktywne kreatory konfiguracji dla `openclaw onboard`.
Kreator to obiekt `ChannelSetupWizard` w `ChannelPlugin`:

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
Pełne przykłady znajdziesz w pakietach wbudowanych pluginów (na przykład plugin Discord `src/channel.setup.ts`).

Dla promptów listy dozwolonych w DM, które wymagają tylko standardowego przepływu
`note -> prompt -> parse -> merge -> patch`, preferuj współdzielone pomocniki konfiguracji
z `openclaw/plugin-sdk/setup`: `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)` i
`createNestedChannelParsedAllowFromPrompt(...)`.

Dla bloków statusu konfiguracji kanału, które różnią się tylko etykietami, wynikami i opcjonalnymi
dodatkowymi liniami, preferuj `createStandardChannelSetupStatus(...)` z
`openclaw/plugin-sdk/setup` zamiast ręcznie tworzyć ten sam obiekt `status` w
każdym pluginie.

Dla opcjonalnych powierzchni konfiguracji, które powinny pojawiać się tylko w określonych kontekstach, użyj
`createOptionalChannelSetupSurface` z `openclaw/plugin-sdk/channel-setup`:

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Zwraca { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup` udostępnia także niższopoziomowe konstruktory
`createOptionalChannelSetupAdapter(...)` i
`createOptionalChannelSetupWizard(...)`, gdy potrzebujesz tylko jednej połowy
tej opcjonalnej powierzchni instalacji.

Wygenerowany opcjonalny adapter/kreator kończy działanie bez obejścia przy rzeczywistych zapisach konfiguracji. Ponownie
wykorzystują jeden komunikat o wymaganej instalacji w `validateInput`,
`applyAccountConfig` i `finalize`, a po ustawieniu `docsPath` dołączają link do dokumentacji.

Dla interfejsów konfiguracji opartych na plikach binarnych preferuj współdzielone pomocniki delegujące zamiast
kopiowania tego samego kodu pośredniego binariów/statusu do każdego kanału:

- `createDetectedBinaryStatus(...)` dla bloków statusu, które różnią się tylko etykietami,
  wskazówkami, wynikami i wykrywaniem binariów
- `createCliPathTextInput(...)` dla wejść tekstowych opartych na ścieżce
- `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)` i
  `createDelegatedResolveConfigured(...)`, gdy `setupEntry` musi leniwie przekazać obsługę
  do cięższego pełnego kreatora
- `createDelegatedTextInputShouldPrompt(...)`, gdy `setupEntry` musi jedynie
  delegować decyzję `textInputs[*].shouldPrompt`

## Publikowanie i instalacja

**Pluginy zewnętrzne:** opublikuj w [ClawHub](/pl/tools/clawhub) lub npm, a następnie zainstaluj:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw najpierw próbuje ClawHub, a potem automatycznie przechodzi do npm. Możesz też
jawnie wymusić ClawHub:

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # tylko ClawHub
```

Nie ma odpowiadającego nadpisania `npm:`. Użyj zwykłej specyfikacji pakietu npm, gdy
chcesz użyć ścieżki npm po awaryjnym przejściu z ClawHub:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**Pluginy w repozytorium:** umieść je w drzewie workspace wbudowanych pluginów, a zostaną automatycznie
wykryte podczas budowania.

**Użytkownicy mogą instalować:**

```bash
openclaw plugins install <package-name>
```

<Info>
  W przypadku instalacji pochodzących z npm `openclaw plugins install` uruchamia
  `npm install --ignore-scripts` (bez skryptów cyklu życia). Zachowaj drzewo zależności pluginu
  jako czyste JS/TS i unikaj pakietów, które wymagają kompilacji w `postinstall`.
</Info>

## Powiązane

- [Punkty wejścia SDK](/pl/plugins/sdk-entrypoints) -- `definePluginEntry` i `defineChannelPluginEntry`
- [Manifest Pluginu](/pl/plugins/manifest) -- pełna dokumentacja schematu manifestu
- [Tworzenie pluginów](/pl/plugins/building-plugins) -- przewodnik krok po kroku na start
