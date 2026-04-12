---
read_when:
    - Tworzysz Plugin OpenClaw
    - Musisz dostarczyć schemat konfiguracji pluginu lub debugować błędy walidacji pluginu
summary: Wymagania dotyczące manifestu Plugin + schematu JSON (ścisła walidacja konfiguracji)
title: Manifest Plugin
x-i18n:
    generated_at: "2026-04-12T09:33:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4074b3639bf24606d6087597f28e29afc85f4ea628a713e9d984b441a16f1c13
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifest Plugin (`openclaw.plugin.json`)

Ta strona dotyczy wyłącznie **natywnego manifestu Plugin OpenClaw**.

Informacje o zgodnych układach pakietów znajdziesz tutaj: [Pakiety Plugin](/pl/plugins/bundles).

Zgodne formaty pakietów używają innych plików manifestu:

- Pakiet Codex: `.codex-plugin/plugin.json`
- Pakiet Claude: `.claude-plugin/plugin.json` lub domyślny układ komponentu Claude
  bez manifestu
- Pakiet Cursor: `.cursor-plugin/plugin.json`

OpenClaw automatycznie wykrywa także te układy pakietów, ale nie są one walidowane
względem opisanego tutaj schematu `openclaw.plugin.json`.

W przypadku zgodnych pakietów OpenClaw obecnie odczytuje metadane pakietu oraz zadeklarowane
korzenie Skills, korzenie poleceń Claude, domyślne ustawienia `settings.json` pakietu Claude,
domyślne ustawienia LSP pakietu Claude oraz obsługiwane zestawy hooków, gdy układ odpowiada
oczekiwaniom środowiska uruchomieniowego OpenClaw.

Każdy natywny Plugin OpenClaw **musi** zawierać plik `openclaw.plugin.json` w
**katalogu głównym pluginu**. OpenClaw używa tego manifestu do walidacji konfiguracji
**bez wykonywania kodu pluginu**. Brakujące lub nieprawidłowe manifesty są traktowane jako
błędy pluginu i blokują walidację konfiguracji.

Zobacz pełny przewodnik po systemie pluginów: [Plugins](/pl/tools/plugin).
Informacje o natywnym modelu możliwości i aktualnych wytycznych zgodności zewnętrznej:
[Model możliwości](/pl/plugins/architecture#public-capability-model).

## Do czego służy ten plik

`openclaw.plugin.json` to metadane, które OpenClaw odczytuje przed załadowaniem
kodu twojego pluginu.

Używaj go do:

- tożsamości pluginu
- walidacji konfiguracji
- metadanych uwierzytelniania i onboardingu, które powinny być dostępne bez uruchamiania
  środowiska uruchomieniowego pluginu
- tanich wskazówek aktywacji, które powierzchnie płaszczyzny sterowania mogą sprawdzać przed załadowaniem środowiska uruchomieniowego
- tanich deskryptorów konfiguracji, które powierzchnie konfiguracji/onboardingu mogą sprawdzać przed załadowaniem
  środowiska uruchomieniowego
- metadanych aliasów i automatycznego włączania, które powinny być rozstrzygane przed załadowaniem środowiska uruchomieniowego pluginu
- skróconych metadanych własności rodziny modeli, które powinny automatycznie aktywować
  plugin przed załadowaniem środowiska uruchomieniowego
- statycznych migawek własności możliwości używanych do zgodnego okablowania pakietów i pokrycia kontraktów
- metadanych konfiguracji specyficznych dla kanału, które powinny być scalane z katalogiem i powierzchniami walidacji
  bez ładowania środowiska uruchomieniowego
- wskazówek UI konfiguracji

Nie używaj go do:

- rejestrowania zachowania środowiska uruchomieniowego
- deklarowania punktów wejścia kodu
- metadanych instalacji npm

To należy do kodu twojego pluginu i `package.json`.

## Minimalny przykład

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Rozbudowany przykład

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin dostawcy OpenRouter",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "Klucz API OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Klucz API OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Klucz API",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Odwołanie do pól najwyższego poziomu

| Pole                                | Wymagane | Typ                              | Co oznacza                                                                                                                                                                                                    |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | Tak      | `string`                         | Kanoniczny identyfikator pluginu. Jest to identyfikator używany w `plugins.entries.<id>`.                                                                                                                    |
| `configSchema`                      | Tak      | `object`                         | Wbudowany schemat JSON dla konfiguracji tego pluginu.                                                                                                                                                         |
| `enabledByDefault`                  | Nie      | `true`                           | Oznacza plugin pakietowy jako domyślnie włączony. Pomiń to pole lub ustaw dowolną wartość inną niż `true`, aby plugin pozostał domyślnie wyłączony.                                                        |
| `legacyPluginIds`                   | Nie      | `string[]`                       | Starsze identyfikatory, które są normalizowane do tego kanonicznego identyfikatora pluginu.                                                                                                                  |
| `autoEnableWhenConfiguredProviders` | Nie      | `string[]`                       | Identyfikatory dostawców, które powinny automatycznie włączać ten plugin, gdy uwierzytelnianie, konfiguracja lub odwołania do modeli o nich wspominają.                                                    |
| `kind`                              | Nie      | `"memory"` \| `"context-engine"` | Deklaruje wyłączny rodzaj pluginu używany przez `plugins.slots.*`.                                                                                                                                            |
| `channels`                          | Nie      | `string[]`                       | Identyfikatory kanałów należących do tego pluginu. Używane do wykrywania i walidacji konfiguracji.                                                                                                           |
| `providers`                         | Nie      | `string[]`                       | Identyfikatory dostawców należących do tego pluginu.                                                                                                                                                          |
| `modelSupport`                      | Nie      | `object`                         | Skrócone metadane rodziny modeli należące do manifestu, używane do automatycznego ładowania pluginu przed środowiskiem uruchomieniowym.                                                                    |
| `cliBackends`                       | Nie      | `string[]`                       | Identyfikatory backendów inferencji CLI należących do tego pluginu. Używane do automatycznej aktywacji przy uruchomieniu na podstawie jawnych odwołań w konfiguracji.                                      |
| `commandAliases`                    | Nie      | `object[]`                       | Nazwy poleceń należące do tego pluginu, które powinny generować świadome pluginu diagnostyki konfiguracji i CLI przed załadowaniem środowiska uruchomieniowego.                                            |
| `providerAuthEnvVars`               | Nie      | `Record<string, string[]>`       | Lekkie metadane env uwierzytelniania dostawcy, które OpenClaw może sprawdzić bez ładowania kodu pluginu.                                                                                                     |
| `providerAuthAliases`               | Nie      | `Record<string, string>`         | Identyfikatory dostawców, które powinny używać ponownie innego identyfikatora dostawcy do wyszukiwania uwierzytelniania, na przykład dostawca programistyczny współdzielący bazowy klucz API i profile uwierzytelniania dostawcy. |
| `channelEnvVars`                    | Nie      | `Record<string, string[]>`       | Lekkie metadane env kanału, które OpenClaw może sprawdzić bez ładowania kodu pluginu. Użyj tego dla konfiguracji kanału sterowanej przez env lub powierzchni uwierzytelniania, które ogólne pomocniki uruchamiania/konfiguracji powinny widzieć. |
| `providerAuthChoices`               | Nie      | `object[]`                       | Lekkie metadane wyboru uwierzytelniania dla selektorów onboardingu, rozstrzygania preferowanego dostawcy i prostego mapowania flag CLI.                                                                     |
| `activation`                        | Nie      | `object`                         | Lekkie wskazówki aktywacji dla ładowania wyzwalanego przez dostawcę, polecenie, kanał, trasę i możliwości. Tylko metadane; rzeczywiste zachowanie nadal należy do środowiska uruchomieniowego pluginu.   |
| `setup`                             | Nie      | `object`                         | Lekkie deskryptory konfiguracji/onboardingu, które powierzchnie wykrywania i konfiguracji mogą sprawdzać bez ładowania środowiska uruchomieniowego pluginu.                                                |
| `contracts`                         | Nie      | `object`                         | Statyczna migawka możliwości pakietowych dla własności mowy, transkrypcji w czasie rzeczywistym, głosu w czasie rzeczywistym, rozumienia mediów, generowania obrazów, generowania muzyki, generowania wideo, pobierania z sieci, wyszukiwania w sieci i narzędzi. |
| `channelConfigs`                    | Nie      | `Record<string, object>`         | Metadane konfiguracji kanału należące do manifestu, scalane z powierzchniami wykrywania i walidacji przed załadowaniem środowiska uruchomieniowego.                                                        |
| `skills`                            | Nie      | `string[]`                       | Katalogi Skills do załadowania, względnie do katalogu głównego pluginu.                                                                                                                                      |
| `name`                              | Nie      | `string`                         | Czytelna dla człowieka nazwa pluginu.                                                                                                                                                                         |
| `description`                       | Nie      | `string`                         | Krótkie podsumowanie wyświetlane na powierzchniach pluginu.                                                                                                                                                   |
| `version`                           | Nie      | `string`                         | Informacyjna wersja pluginu.                                                                                                                                                                                  |
| `uiHints`                           | Nie      | `Record<string, object>`         | Etykiety UI, placeholdery i wskazówki dotyczące wrażliwości dla pól konfiguracji.                                                                                                                             |

## Odwołanie do `providerAuthChoices`

Każdy wpis `providerAuthChoices` opisuje jeden wybór onboardingu lub uwierzytelniania.
OpenClaw odczytuje to przed załadowaniem środowiska uruchomieniowego dostawcy.

| Pole                  | Wymagane | Typ                                             | Co oznacza                                                                                               |
| --------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Tak      | `string`                                        | Identyfikator dostawcy, do którego należy ten wybór.                                                     |
| `method`              | Tak      | `string`                                        | Identyfikator metody uwierzytelniania, do której należy przekazać żądanie.                               |
| `choiceId`            | Tak      | `string`                                        | Stabilny identyfikator wyboru uwierzytelniania używany przez onboarding i przepływy CLI.                |
| `choiceLabel`         | Nie      | `string`                                        | Etykieta widoczna dla użytkownika. Jeśli zostanie pominięta, OpenClaw użyje wartości `choiceId`.        |
| `choiceHint`          | Nie      | `string`                                        | Krótki tekst pomocniczy dla selektora.                                                                   |
| `assistantPriority`   | Nie      | `number`                                        | Niższe wartości są sortowane wcześniej w interaktywnych selektorach sterowanych przez asystenta.        |
| `assistantVisibility` | Nie      | `"visible"` \| `"manual-only"`                  | Ukrywa wybór w selektorach asystenta, ale nadal pozwala na ręczny wybór w CLI.                          |
| `deprecatedChoiceIds` | Nie      | `string[]`                                      | Starsze identyfikatory wyboru, które powinny przekierowywać użytkowników do tego zamiennego wyboru.     |
| `groupId`             | Nie      | `string`                                        | Opcjonalny identyfikator grupy do grupowania powiązanych wyborów.                                        |
| `groupLabel`          | Nie      | `string`                                        | Etykieta widoczna dla użytkownika dla tej grupy.                                                         |
| `groupHint`           | Nie      | `string`                                        | Krótki tekst pomocniczy dla grupy.                                                                       |
| `optionKey`           | Nie      | `string`                                        | Wewnętrzny klucz opcji dla prostych przepływów uwierzytelniania z jedną flagą.                          |
| `cliFlag`             | Nie      | `string`                                        | Nazwa flagi CLI, na przykład `--openrouter-api-key`.                                                     |
| `cliOption`           | Nie      | `string`                                        | Pełna postać opcji CLI, na przykład `--openrouter-api-key <key>`.                                        |
| `cliDescription`      | Nie      | `string`                                        | Opis używany w pomocy CLI.                                                                               |
| `onboardingScopes`    | Nie      | `Array<"text-inference" \| "image-generation">` | Na których powierzchniach onboardingu ten wybór powinien się pojawiać. Jeśli zostanie pominięte, domyślnie używane jest `["text-inference"]`. |

## Odwołanie do `commandAliases`

Użyj `commandAliases`, gdy plugin jest właścicielem nazwy polecenia środowiska uruchomieniowego, którą użytkownicy mogą
omyłkowo umieścić w `plugins.allow` lub próbować uruchomić jako główne polecenie CLI. OpenClaw
używa tych metadanych do diagnostyki bez importowania kodu środowiska uruchomieniowego pluginu.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Pole         | Wymagane | Typ               | Co oznacza                                                                  |
| ------------ | -------- | ----------------- | --------------------------------------------------------------------------- |
| `name`       | Tak      | `string`          | Nazwa polecenia należąca do tego pluginu.                                   |
| `kind`       | Nie      | `"runtime-slash"` | Oznacza alias jako polecenie slash czatu, a nie główne polecenie CLI.       |
| `cliCommand` | Nie      | `string`          | Powiązane główne polecenie CLI, które należy zasugerować dla operacji CLI, jeśli istnieje. |

## Odwołanie do `activation`

Użyj `activation`, gdy plugin może w prosty sposób zadeklarować, które zdarzenia płaszczyzny sterowania
powinny aktywować go później.

Ten blok zawiera tylko metadane. Nie rejestruje zachowania środowiska uruchomieniowego i nie
zastępuje `register(...)`, `setupEntry` ani innych punktów wejścia środowiska uruchomieniowego/pluginu.
Obecni konsumenci używają go jako wskazówki zawężającej przed szerszym ładowaniem pluginu, więc
brak metadanych aktywacji wpływa tylko na wydajność; nie powinien zmieniać
poprawności.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Pole             | Wymagane | Typ                                                  | Co oznacza                                                            |
| ---------------- | -------- | ---------------------------------------------------- | --------------------------------------------------------------------- |
| `onProviders`    | Nie      | `string[]`                                           | Identyfikatory dostawców, które powinny aktywować ten plugin po żądaniu. |
| `onCommands`     | Nie      | `string[]`                                           | Identyfikatory poleceń, które powinny aktywować ten plugin.           |
| `onChannels`     | Nie      | `string[]`                                           | Identyfikatory kanałów, które powinny aktywować ten plugin.           |
| `onRoutes`       | Nie      | `string[]`                                           | Rodzaje tras, które powinny aktywować ten plugin.                     |
| `onCapabilities` | Nie      | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Ogólne wskazówki dotyczące możliwości używane przy planowaniu aktywacji płaszczyzny sterowania. |

W przypadku planowania wyzwalanego poleceniem OpenClaw nadal korzysta z awaryjnego mechanizmu
opartego na starszych `commandAliases[].cliCommand` lub `commandAliases[].name`, gdy plugin
nie dodał jeszcze jawnych metadanych `activation.onCommands`.

## Odwołanie do `setup`

Użyj `setup`, gdy powierzchnie konfiguracji i onboardingu potrzebują prostych metadanych należących do pluginu
przed załadowaniem środowiska uruchomieniowego.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

Pole najwyższego poziomu `cliBackends` pozostaje prawidłowe i nadal opisuje backendy inferencji CLI.
`setup.cliBackends` to powierzchnia deskryptorów specyficzna dla konfiguracji dla
przepływów płaszczyzny sterowania/konfiguracji, które powinny pozostać wyłącznie metadanymi.

Gdy są obecne, `setup.providers` i `setup.cliBackends` są preferowaną
powierzchnią wyszukiwania opartą najpierw na deskryptorach dla wykrywania konfiguracji. Jeśli deskryptor
jedynie zawęża kandydujący plugin, a konfiguracja nadal potrzebuje bogatszych hooków czasu konfiguracji,
ustaw `requiresRuntime: true` i pozostaw `setup-api` jako
awaryjną ścieżkę wykonania.

Ponieważ wyszukiwanie konfiguracji może wykonywać kod `setup-api` należący do pluginu,
znormalizowane wartości `setup.providers[].id` i `setup.cliBackends[]` muszą pozostać unikalne globalnie
wśród wykrytych pluginów. Niejednoznaczna własność kończy się bezpieczną odmową zamiast wybierania
zwycięzcy na podstawie kolejności wykrywania.

### Odwołanie do `setup.providers`

| Pole          | Wymagane | Typ        | Co oznacza                                                                              |
| ------------- | -------- | ---------- | --------------------------------------------------------------------------------------- |
| `id`          | Tak      | `string`   | Identyfikator dostawcy udostępniany podczas konfiguracji lub onboardingu. Zachowaj globalną unikalność znormalizowanych identyfikatorów. |
| `authMethods` | Nie      | `string[]` | Identyfikatory metod konfiguracji/uwierzytelniania obsługiwanych przez tego dostawcę bez ładowania pełnego środowiska uruchomieniowego. |
| `envVars`     | Nie      | `string[]` | Zmienne env, które ogólne powierzchnie konfiguracji/statusu mogą sprawdzać przed załadowaniem środowiska uruchomieniowego pluginu.      |

### Pola `setup`

| Pole               | Wymagane | Typ        | Co oznacza                                                                                          |
| ------------------ | -------- | ---------- | --------------------------------------------------------------------------------------------------- |
| `providers`        | Nie      | `object[]` | Deskryptory konfiguracji dostawców udostępniane podczas konfiguracji i onboardingu.                |
| `cliBackends`      | Nie      | `string[]` | Identyfikatory backendów czasu konfiguracji używane do wyszukiwania konfiguracji opartego najpierw na deskryptorach. Zachowaj globalną unikalność znormalizowanych identyfikatorów. |
| `configMigrations` | Nie      | `string[]` | Identyfikatory migracji konfiguracji należące do powierzchni konfiguracji tego pluginu.            |
| `requiresRuntime`  | Nie      | `boolean`  | Czy konfiguracja nadal wymaga wykonania `setup-api` po wyszukaniu deskryptora.                     |

## Odwołanie do `uiHints`

`uiHints` to mapa od nazw pól konfiguracji do małych wskazówek renderowania.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Klucz API",
      "help": "Używany do żądań OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Każda wskazówka pola może zawierać:

| Pole          | Typ        | Co oznacza                              |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Etykieta pola widoczna dla użytkownika. |
| `help`        | `string`   | Krótki tekst pomocniczy.                |
| `tags`        | `string[]` | Opcjonalne tagi UI.                     |
| `advanced`    | `boolean`  | Oznacza pole jako zaawansowane.         |
| `sensitive`   | `boolean`  | Oznacza pole jako tajne lub wrażliwe.   |
| `placeholder` | `string`   | Tekst placeholdera dla pól formularza.  |

## Odwołanie do `contracts`

Używaj `contracts` tylko dla statycznych metadanych własności możliwości, które OpenClaw może
odczytać bez importowania środowiska uruchomieniowego pluginu.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Każda lista jest opcjonalna:

| Pole                             | Typ        | Co oznacza                                                      |
| -------------------------------- | ---------- | --------------------------------------------------------------- |
| `speechProviders`                | `string[]` | Identyfikatory dostawców mowy należących do tego pluginu.       |
| `realtimeTranscriptionProviders` | `string[]` | Identyfikatory dostawców transkrypcji w czasie rzeczywistym należących do tego pluginu. |
| `realtimeVoiceProviders`         | `string[]` | Identyfikatory dostawców głosu w czasie rzeczywistym należących do tego pluginu. |
| `mediaUnderstandingProviders`    | `string[]` | Identyfikatory dostawców rozumienia mediów należących do tego pluginu. |
| `imageGenerationProviders`       | `string[]` | Identyfikatory dostawców generowania obrazów należących do tego pluginu. |
| `videoGenerationProviders`       | `string[]` | Identyfikatory dostawców generowania wideo należących do tego pluginu. |
| `webFetchProviders`              | `string[]` | Identyfikatory dostawców pobierania z sieci należących do tego pluginu. |
| `webSearchProviders`             | `string[]` | Identyfikatory dostawców wyszukiwania w sieci należących do tego pluginu. |
| `tools`                          | `string[]` | Nazwy narzędzi agenta należących do tego pluginu na potrzeby kontroli kontraktów pakietowych. |

## Odwołanie do `channelConfigs`

Użyj `channelConfigs`, gdy plugin kanału potrzebuje prostych metadanych konfiguracji przed
załadowaniem środowiska uruchomieniowego.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "URL homeserwera",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Połączenie z homeserwerem Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Każdy wpis kanału może zawierać:

| Pole          | Typ                      | Co oznacza                                                                                 |
| ------------- | ------------------------ | ------------------------------------------------------------------------------------------ |
| `schema`      | `object`                 | Schemat JSON dla `channels.<id>`. Wymagany dla każdego zadeklarowanego wpisu konfiguracji kanału. |
| `uiHints`     | `Record<string, object>` | Opcjonalne etykiety UI/placeholdery/wskazówki dotyczące wrażliwości dla tej sekcji konfiguracji kanału. |
| `label`       | `string`                 | Etykieta kanału scalana z powierzchniami selektora i inspekcji, gdy metadane środowiska uruchomieniowego nie są gotowe. |
| `description` | `string`                 | Krótki opis kanału dla powierzchni inspekcji i katalogu.                                   |
| `preferOver`  | `string[]`               | Starsze lub niżej priorytetowe identyfikatory pluginów, które ten kanał powinien wyprzedzać na powierzchniach wyboru. |

## Odwołanie do `modelSupport`

Użyj `modelSupport`, gdy OpenClaw ma wnioskować o pluginie dostawcy na podstawie
skrótowych identyfikatorów modeli, takich jak `gpt-5.4` lub `claude-sonnet-4.6`, zanim środowisko uruchomieniowe pluginu
zostanie załadowane.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw stosuje następujący priorytet:

- jawne odwołania `provider/model` używają metadanych manifestu `providers` właściciela
- `modelPatterns` mają pierwszeństwo przed `modelPrefixes`
- jeśli jeden plugin zewnętrzny i jeden plugin pakietowy pasują jednocześnie, wygrywa plugin zewnętrzny
- pozostała niejednoznaczność jest ignorowana, dopóki użytkownik lub konfiguracja nie określi dostawcy

Pola:

| Pole            | Typ        | Co oznacza                                                                    |
| --------------- | ---------- | ----------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefiksy dopasowywane za pomocą `startsWith` do skrótowych identyfikatorów modeli. |
| `modelPatterns` | `string[]` | Źródła regex dopasowywane do skrótowych identyfikatorów modeli po usunięciu sufiksu profilu. |

Starsze klucze możliwości najwyższego poziomu są przestarzałe. Użyj `openclaw doctor --fix`, aby
przenieść `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` i `webSearchProviders` do `contracts`; zwykłe
ładowanie manifestu nie traktuje już tych pól najwyższego poziomu jako
własności możliwości.

## Manifest a package.json

Te dwa pliki pełnią różne role:

| Plik                   | Używaj go do                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.plugin.json` | Wykrywania, walidacji konfiguracji, metadanych wyboru uwierzytelniania i wskazówek UI, które muszą istnieć przed uruchomieniem kodu pluginu |
| `package.json`         | Metadanych npm, instalacji zależności oraz bloku `openclaw` używanego do punktów wejścia, kontroli instalacji, konfiguracji lub metadanych katalogu |

Jeśli nie masz pewności, gdzie powinien znaleźć się dany fragment metadanych, użyj tej zasady:

- jeśli OpenClaw musi o tym wiedzieć przed załadowaniem kodu pluginu, umieść to w `openclaw.plugin.json`
- jeśli dotyczy to pakowania, plików wejściowych lub zachowania instalacji npm, umieść to w `package.json`

### Pola `package.json`, które wpływają na wykrywanie

Niektóre metadane pluginów sprzed uruchomienia celowo znajdują się w `package.json` w bloku
`openclaw`, a nie w `openclaw.plugin.json`.

Ważne przykłady:

| Pole                                                              | Co oznacza                                                                                                                                   |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Deklaruje natywne punkty wejścia Plugin.                                                                                                     |
| `openclaw.setupEntry`                                             | Lekki punkt wejścia tylko do konfiguracji używany podczas onboardingu i odroczonego uruchamiania kanału.                                    |
| `openclaw.channel`                                                | Lekkie metadane katalogu kanałów, takie jak etykiety, ścieżki dokumentacji, aliasy i teksty wyboru.                                        |
| `openclaw.channel.configuredState`                                | Lekkie metadane modułu sprawdzania stanu konfiguracji, które mogą odpowiedzieć na pytanie „czy konfiguracja oparta wyłącznie na env już istnieje?” bez ładowania pełnego środowiska uruchomieniowego kanału. |
| `openclaw.channel.persistedAuthState`                             | Lekkie metadane modułu sprawdzania utrwalonego stanu uwierzytelniania, które mogą odpowiedzieć na pytanie „czy cokolwiek jest już zalogowane?” bez ładowania pełnego środowiska uruchomieniowego kanału. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Wskazówki instalacji/aktualizacji dla pluginów pakietowych i publikowanych zewnętrznie.                                                     |
| `openclaw.install.defaultChoice`                                  | Preferowana ścieżka instalacji, gdy dostępnych jest wiele źródeł instalacji.                                                                |
| `openclaw.install.minHostVersion`                                 | Minimalna obsługiwana wersja hosta OpenClaw z użyciem dolnego ograniczenia semver, na przykład `>=2026.3.22`.                               |
| `openclaw.install.allowInvalidConfigRecovery`                     | Umożliwia wąską ścieżkę odzyskiwania przez ponowną instalację pluginu pakietowego, gdy konfiguracja jest nieprawidłowa.                    |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Pozwala powierzchniom kanału tylko do konfiguracji ładować się przed pełnym pluginem kanału podczas uruchamiania.                          |

`openclaw.install.minHostVersion` jest egzekwowane podczas instalacji i
ładowania rejestru manifestów. Nieprawidłowe wartości są odrzucane; nowsze, ale poprawne wartości powodują pominięcie
pluginu na starszych hostach.

`openclaw.install.allowInvalidConfigRecovery` jest celowo wąskie. Nie
sprawia, że dowolne uszkodzone konfiguracje stają się możliwe do zainstalowania. Obecnie pozwala tylko przepływom instalacji
odzyskiwać po konkretnych nieaktualnych awariach aktualizacji pluginów pakietowych, takich jak
brakująca ścieżka pluginu pakietowego lub nieaktualny wpis `channels.<id>` dla tego samego
pluginu pakietowego. Niezwiązane błędy konfiguracji nadal blokują instalację i kierują operatorów
do `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` to metadane pakietu dla małego modułu sprawdzającego:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Użyj tego, gdy przepływy konfiguracji, doctor lub stanu konfiguracji potrzebują prostego sprawdzenia
uwierzytelniania typu tak/nie przed załadowaniem pełnego pluginu kanału. Docelowy eksport powinien być małą
funkcją, która odczytuje tylko utrwalony stan; nie prowadź go przez pełną beczkę środowiska uruchomieniowego kanału.

`openclaw.channel.configuredState` ma ten sam kształt dla prostych kontroli
stanu konfiguracji opartych wyłącznie na env:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Użyj tego, gdy kanał może odpowiedzieć o stanie konfiguracji na podstawie env lub innych małych
wejść niebędących częścią środowiska uruchomieniowego. Jeśli sprawdzenie wymaga pełnego rozstrzygania konfiguracji lub rzeczywistego
środowiska uruchomieniowego kanału, pozostaw tę logikę w hooku pluginu `config.hasConfiguredState`.

## Wymagania schematu JSON

- **Każdy plugin musi dostarczać schemat JSON**, nawet jeśli nie przyjmuje żadnej konfiguracji.
- Pusty schemat jest akceptowalny (na przykład `{ "type": "object", "additionalProperties": false }`).
- Schematy są walidowane podczas odczytu/zapisu konfiguracji, a nie w czasie działania.

## Zachowanie walidacji

- Nieznane klucze `channels.*` są **błędami**, chyba że identyfikator kanału jest zadeklarowany przez
  manifest pluginu.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` i `plugins.slots.*`
  muszą odwoływać się do **wykrywalnych** identyfikatorów pluginów. Nieznane identyfikatory są **błędami**.
- Jeśli plugin jest zainstalowany, ale ma uszkodzony lub brakujący manifest albo schemat,
  walidacja kończy się niepowodzeniem, a Doctor zgłasza błąd pluginu.
- Jeśli konfiguracja pluginu istnieje, ale plugin jest **wyłączony**, konfiguracja jest zachowywana i
  pojawia się **ostrzeżenie** w Doctor + logach.

Pełny schemat `plugins.*` znajdziesz w [Odwołaniu do konfiguracji](/pl/gateway/configuration).

## Uwagi

- Manifest jest **wymagany dla natywnych Plugin OpenClaw**, w tym dla ładowań z lokalnego systemu plików.
- Środowisko uruchomieniowe nadal ładuje moduł pluginu osobno; manifest służy tylko do
  wykrywania + walidacji.
- Natywne manifesty są parsowane przy użyciu JSON5, więc komentarze, końcowe przecinki i
  klucze bez cudzysłowów są akceptowane, o ile końcowa wartość nadal jest obiektem.
- Ładowarka manifestu odczytuje tylko udokumentowane pola manifestu. Unikaj dodawania
  tutaj niestandardowych kluczy najwyższego poziomu.
- `providerAuthEnvVars` to lekka ścieżka metadanych dla sond uwierzytelniania, walidacji znaczników env
  i podobnych powierzchni uwierzytelniania dostawcy, które nie powinny uruchamiać środowiska uruchomieniowego pluginu
  tylko po to, aby sprawdzić nazwy env.
- `providerAuthAliases` pozwala wariantom dostawcy ponownie używać zmiennych env uwierzytelniania innego dostawcy,
  profili uwierzytelniania, uwierzytelniania opartego na konfiguracji oraz wyboru onboardingu klucza API
  bez kodowania tej relacji na sztywno w rdzeniu.
- `channelEnvVars` to lekka ścieżka metadanych dla awaryjnego użycia shell env, promptów konfiguracji
  i podobnych powierzchni kanału, które nie powinny uruchamiać środowiska uruchomieniowego pluginu
  tylko po to, aby sprawdzić nazwy env.
- `providerAuthChoices` to lekka ścieżka metadanych dla selektorów wyboru uwierzytelniania,
  rozstrzygania `--auth-choice`, mapowania preferowanego dostawcy i prostej rejestracji flag CLI
  dla onboardingu przed załadowaniem środowiska uruchomieniowego dostawcy. W przypadku metadanych kreatora środowiska uruchomieniowego,
  które wymagają kodu dostawcy, zobacz
  [Hooki środowiska uruchomieniowego dostawcy](/pl/plugins/architecture#provider-runtime-hooks).
- Wyłączne rodzaje pluginów są wybierane przez `plugins.slots.*`.
  - `kind: "memory"` jest wybierany przez `plugins.slots.memory`.
  - `kind: "context-engine"` jest wybierany przez `plugins.slots.contextEngine`
    (domyślnie: wbudowany `legacy`).
- `channels`, `providers`, `cliBackends` i `skills` można pominąć, gdy
  plugin ich nie potrzebuje.
- Jeśli twój plugin zależy od modułów natywnych, udokumentuj kroki budowania oraz wszelkie
  wymagania listy dozwolonych elementów menedżera pakietów (na przykład pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Powiązane

- [Tworzenie Plugin](/pl/plugins/building-plugins) — wprowadzenie do pluginów
- [Architektura Plugin](/pl/plugins/architecture) — architektura wewnętrzna
- [Przegląd SDK](/pl/plugins/sdk-overview) — dokumentacja SDK Plugin
