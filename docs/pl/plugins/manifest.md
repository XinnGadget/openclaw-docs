---
read_when:
    - Tworzysz plugin OpenClaw
    - Musisz dostarczyć schemat konfiguracji pluginu albo debugować błędy walidacji pluginu
summary: Manifest pluginu + wymagania schematu JSON (ścisła walidacja konfiguracji)
title: Manifest pluginu
x-i18n:
    generated_at: "2026-04-06T03:10:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: f6f915a761cdb5df77eba5d2ccd438c65445bd2ab41b0539d1200e63e8cf2c3a
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifest pluginu (openclaw.plugin.json)

Ta strona dotyczy wyłącznie **natywnego manifestu pluginu OpenClaw**.

Informacje o zgodnych układach bundli znajdziesz w [Plugin bundles](/pl/plugins/bundles).

Zgodne formaty bundli używają innych plików manifestu:

- Bundel Codex: `.codex-plugin/plugin.json`
- Bundel Claude: `.claude-plugin/plugin.json` albo domyślny układ komponentu Claude
  bez manifestu
- Bundel Cursor: `.cursor-plugin/plugin.json`

OpenClaw automatycznie wykrywa także te układy bundli, ale nie są one
walidowane względem schematu `openclaw.plugin.json` opisanego tutaj.

Dla zgodnych bundli OpenClaw obecnie odczytuje metadane bundla oraz zadeklarowane
katalogi główne umiejętności, katalogi główne poleceń Claude, domyślne wartości `settings.json` bundla Claude,
domyślne wartości LSP bundla Claude oraz obsługiwane paczki hooków, gdy układ odpowiada
oczekiwaniom środowiska uruchomieniowego OpenClaw.

Każdy natywny plugin OpenClaw **musi** dostarczać plik `openclaw.plugin.json` w
**katalogu głównym pluginu**. OpenClaw używa tego manifestu do walidacji konfiguracji
**bez wykonywania kodu pluginu**. Brakujące lub nieprawidłowe manifesty są traktowane jako
błędy pluginu i blokują walidację konfiguracji.

Zobacz pełny przewodnik po systemie pluginów: [Plugins](/pl/tools/plugin).
Informacje o natywnym modelu możliwości i aktualnych wytycznych zgodności zewnętrznej:
[Capability model](/pl/plugins/architecture#public-capability-model).

## Do czego służy ten plik

`openclaw.plugin.json` to metadane, które OpenClaw odczytuje, zanim załaduje
kod Twojego pluginu.

Używaj go do:

- tożsamości pluginu
- walidacji konfiguracji
- metadanych uwierzytelniania i onboardingu, które powinny być dostępne bez uruchamiania
  środowiska uruchomieniowego pluginu
- metadanych aliasów i automatycznego włączania, które powinny być rozstrzygane przed załadowaniem środowiska uruchomieniowego pluginu
- metadanych skrótowych własności rodzin modeli, które powinny automatycznie aktywować
  plugin przed załadowaniem środowiska uruchomieniowego
- statycznych migawek własności możliwości używanych do zgodności bundli i pokrycia kontraktów
- metadanych konfiguracji specyficznych dla kanału, które powinny być scalane z powierzchniami katalogu i walidacji
  bez ładowania środowiska uruchomieniowego
- wskazówek dla UI konfiguracji

Nie używaj go do:

- rejestrowania zachowania środowiska uruchomieniowego
- deklarowania punktów wejścia kodu
- metadanych instalacji npm

Te elementy należą do kodu pluginu i `package.json`.

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

## Rozszerzony przykład

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
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
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

## Dokumentacja pól najwyższego poziomu

| Pole                                | Wymagane | Typ                              | Co oznacza                                                                                                                                                                                                   |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Tak      | `string`                         | Kanoniczne ID pluginu. Jest to ID używane w `plugins.entries.<id>`.                                                                                                                                          |
| `configSchema`                      | Tak      | `object`                         | Wbudowany JSON Schema dla konfiguracji tego pluginu.                                                                                                                                                         |
| `enabledByDefault`                  | Nie      | `true`                           | Oznacza plugin bundlowany jako domyślnie włączony. Pomiń to pole albo ustaw dowolną wartość inną niż `true`, aby pozostawić plugin domyślnie wyłączony.                                                   |
| `legacyPluginIds`                   | Nie      | `string[]`                       | Starsze ID, które są normalizowane do tego kanonicznego ID pluginu.                                                                                                                                          |
| `autoEnableWhenConfiguredProviders` | Nie      | `string[]`                       | ID dostawców, które powinny automatycznie włączać ten plugin, gdy uwierzytelnianie, konfiguracja lub odwołania do modeli o nich wspominają.                                                                |
| `kind`                              | Nie      | `"memory"` \| `"context-engine"` | Deklaruje wyłączny typ pluginu używany przez `plugins.slots.*`.                                                                                                                                              |
| `channels`                          | Nie      | `string[]`                       | ID kanałów należących do tego pluginu. Używane do wykrywania i walidacji konfiguracji.                                                                                                                       |
| `providers`                         | Nie      | `string[]`                       | ID dostawców należących do tego pluginu.                                                                                                                                                                     |
| `modelSupport`                      | Nie      | `object`                         | Skrótowe metadane rodzin modeli należące do manifestu, używane do automatycznego ładowania pluginu przed środowiskiem uruchomieniowym.                                                                     |
| `providerAuthEnvVars`               | Nie      | `Record<string, string[]>`       | Lekkie metadane env do uwierzytelniania dostawców, które OpenClaw może sprawdzać bez ładowania kodu pluginu.                                                                                                |
| `providerAuthChoices`               | Nie      | `object[]`                       | Lekkie metadane wyboru uwierzytelniania dla selektorów onboardingu, rozstrzygania preferowanych dostawców i prostego powiązania flag CLI.                                                                  |
| `contracts`                         | Nie      | `object`                         | Statyczna migawka możliwości bundla dla speech, realtime transcription, realtime voice, media understanding, image generation, music generation, video generation, web fetch, web search i własności narzędzi. |
| `channelConfigs`                    | Nie      | `Record<string, object>`         | Metadane konfiguracji kanału należące do manifestu, scalane z powierzchniami wykrywania i walidacji przed załadowaniem środowiska uruchomieniowego.                                                        |
| `skills`                            | Nie      | `string[]`                       | Katalogi Skills do załadowania, względne względem katalogu głównego pluginu.                                                                                                                                 |
| `name`                              | Nie      | `string`                         | Czytelna dla człowieka nazwa pluginu.                                                                                                                                                                        |
| `description`                       | Nie      | `string`                         | Krótkie podsumowanie wyświetlane na powierzchniach pluginu.                                                                                                                                                  |
| `version`                           | Nie      | `string`                         | Informacyjna wersja pluginu.                                                                                                                                                                                 |
| `uiHints`                           | Nie      | `Record<string, object>`         | Etykiety UI, placeholdery i wskazówki o wrażliwości dla pól konfiguracji.                                                                                                                                     |

## Dokumentacja `providerAuthChoices`

Każdy wpis `providerAuthChoices` opisuje jedną opcję onboardingu lub uwierzytelniania.
OpenClaw odczytuje to, zanim załaduje się środowisko uruchomieniowe dostawcy.

| Pole                 | Wymagane | Typ                                             | Co oznacza                                                                                               |
| -------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`           | Tak      | `string`                                        | ID dostawcy, do którego należy ta opcja.                                                                 |
| `method`             | Tak      | `string`                                        | ID metody uwierzytelniania, do której należy przekierować.                                               |
| `choiceId`           | Tak      | `string`                                        | Stabilne ID opcji uwierzytelniania używane przez onboarding i przepływy CLI.                             |
| `choiceLabel`        | Nie      | `string`                                        | Etykieta widoczna dla użytkownika. Jeśli jest pominięta, OpenClaw używa `choiceId`.                     |
| `choiceHint`         | Nie      | `string`                                        | Krótki tekst pomocniczy dla selektora.                                                                   |
| `assistantPriority`  | Nie      | `number`                                        | Niższe wartości są sortowane wcześniej w interaktywnych selektorach sterowanych przez asystenta.        |
| `assistantVisibility`| Nie      | `"visible"` \| `"manual-only"`                  | Ukrywa opcję w selektorach asystenta, jednocześnie nadal pozwalając na ręczny wybór przez CLI.          |
| `deprecatedChoiceIds`| Nie      | `string[]`                                      | Starsze ID opcji, które powinny przekierowywać użytkowników do tej zastępczej opcji.                    |
| `groupId`            | Nie      | `string`                                        | Opcjonalne ID grupy do grupowania powiązanych opcji.                                                     |
| `groupLabel`         | Nie      | `string`                                        | Etykieta tej grupy widoczna dla użytkownika.                                                             |
| `groupHint`          | Nie      | `string`                                        | Krótki tekst pomocniczy dla grupy.                                                                       |
| `optionKey`          | Nie      | `string`                                        | Wewnętrzny klucz opcji dla prostych przepływów uwierzytelniania z jedną flagą.                          |
| `cliFlag`            | Nie      | `string`                                        | Nazwa flagi CLI, na przykład `--openrouter-api-key`.                                                     |
| `cliOption`          | Nie      | `string`                                        | Pełny kształt opcji CLI, na przykład `--openrouter-api-key <key>`.                                      |
| `cliDescription`     | Nie      | `string`                                        | Opis używany w pomocy CLI.                                                                               |
| `onboardingScopes`   | Nie      | `Array<"text-inference" \| "image-generation">` | Na których powierzchniach onboardingu ta opcja powinna się pojawić. Jeśli pominięte, domyślnie używane jest `["text-inference"]`. |

## Dokumentacja `uiHints`

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
| `sensitive`   | `boolean`  | Oznacza pole jako sekretne lub wrażliwe.|
| `placeholder` | `string`   | Tekst placeholdera dla pól formularza.  |

## Dokumentacja `contracts`

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

| Pole                             | Typ        | Co oznacza                                                    |
| -------------------------------- | ---------- | ------------------------------------------------------------- |
| `speechProviders`                | `string[]` | ID dostawców mowy należących do tego pluginu.                 |
| `realtimeTranscriptionProviders` | `string[]` | ID dostawców transkrypcji czasu rzeczywistego należących do tego pluginu. |
| `realtimeVoiceProviders`         | `string[]` | ID dostawców głosu czasu rzeczywistego należących do tego pluginu. |
| `mediaUnderstandingProviders`    | `string[]` | ID dostawców rozumienia mediów należących do tego pluginu.    |
| `imageGenerationProviders`       | `string[]` | ID dostawców generowania obrazów należących do tego pluginu.  |
| `videoGenerationProviders`       | `string[]` | ID dostawców generowania wideo należących do tego pluginu.    |
| `webFetchProviders`              | `string[]` | ID dostawców pobierania z sieci należących do tego pluginu.   |
| `webSearchProviders`             | `string[]` | ID dostawców wyszukiwania w sieci należących do tego pluginu. |
| `tools`                          | `string[]` | Nazwy narzędzi agenta należące do tego pluginu dla sprawdzeń kontraktów bundli. |

## Dokumentacja `channelConfigs`

Używaj `channelConfigs`, gdy plugin kanału potrzebuje lekkich metadanych konfiguracji przed
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
          "label": "URL homeservera",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Połączenie z homeserverem Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Każdy wpis kanału może zawierać:

| Pole          | Typ                      | Co oznacza                                                                                |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema dla `channels.<id>`. Wymagane dla każdego zadeklarowanego wpisu konfiguracji kanału. |
| `uiHints`     | `Record<string, object>` | Opcjonalne etykiety UI/placeholdery/wskazówki o wrażliwości dla tej sekcji konfiguracji kanału. |
| `label`       | `string`                 | Etykieta kanału scalana z powierzchniami selektora i inspekcji, gdy metadane runtime nie są gotowe. |
| `description` | `string`                 | Krótki opis kanału dla powierzchni inspekcji i katalogu.                                  |
| `preferOver`  | `string[]`               | Starsze lub niższego priorytetu ID pluginów, które ten kanał powinien wyprzedzać na powierzchniach wyboru. |

## Dokumentacja `modelSupport`

Używaj `modelSupport`, gdy OpenClaw powinien wywnioskować plugin dostawcy z
krótkich ID modeli, takich jak `gpt-5.4` albo `claude-sonnet-4.6`, zanim
załaduje się środowisko uruchomieniowe pluginu.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw stosuje następujący priorytet:

- jawne odwołania `provider/model` używają metadanych manifestu właściciela `providers`
- `modelPatterns` mają pierwszeństwo przed `modelPrefixes`
- jeśli dopasują się jednocześnie jeden plugin niebundlowany i jeden bundlowany,
  wygrywa plugin niebundlowany
- pozostała niejednoznaczność jest ignorowana, dopóki użytkownik lub konfiguracja nie wskaże dostawcy

Pola:

| Pole            | Typ        | Co oznacza                                                                         |
| --------------- | ---------- | ---------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefiksy dopasowywane przez `startsWith` do skróconych ID modeli.                  |
| `modelPatterns` | `string[]` | Źródła regex dopasowywane do skróconych ID modeli po usunięciu sufiksu profilu.    |

Starsze klucze możliwości najwyższego poziomu są przestarzałe. Użyj `openclaw doctor --fix`, aby
przenieść `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` i `webSearchProviders` do `contracts`; zwykłe
ładowanie manifestu nie traktuje już tych pól najwyższego poziomu jako
własności możliwości.

## Manifest a package.json

Te dwa pliki służą do różnych zadań:

| Plik                   | Używaj go do                                                                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Wykrywania, walidacji konfiguracji, metadanych wyboru uwierzytelniania i wskazówek UI, które muszą istnieć zanim uruchomi się kod pluginu |
| `package.json`         | Metadanych npm, instalacji zależności oraz bloku `openclaw` używanego do punktów wejścia, bramek instalacji, konfiguracji lub metadanych katalogu |

Jeśli nie masz pewności, gdzie powinien należeć dany fragment metadanych, użyj tej reguły:

- jeśli OpenClaw musi go znać przed załadowaniem kodu pluginu, umieść go w `openclaw.plugin.json`
- jeśli dotyczy pakowania, plików wejściowych lub zachowania instalacji npm, umieść go w `package.json`

### Pola package.json wpływające na wykrywanie

Niektóre metadane pluginu przed uruchomieniem celowo znajdują się w `package.json` w bloku
`openclaw`, a nie w `openclaw.plugin.json`.

Ważne przykłady:

| Pole                                                              | Co oznacza                                                                                                                                   |
| ----------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Deklaruje natywne punkty wejścia pluginu.                                                                                                     |
| `openclaw.setupEntry`                                             | Lekki punkt wejścia tylko do konfiguracji używany podczas onboardingu i odroczonego startu kanału.                                           |
| `openclaw.channel`                                                | Lekkie metadane katalogu kanału, takie jak etykiety, ścieżki dokumentacji, aliasy i tekst wyboru.                                           |
| `openclaw.channel.configuredState`                                | Lekkie metadane sprawdzania skonfigurowanego stanu, które mogą odpowiedzieć na pytanie „czy konfiguracja tylko z env już istnieje?” bez ładowania pełnego środowiska uruchomieniowego kanału. |
| `openclaw.channel.persistedAuthState`                             | Lekkie metadane sprawdzania utrwalonego stanu uwierzytelnienia, które mogą odpowiedzieć na pytanie „czy cokolwiek jest już zalogowane?” bez ładowania pełnego środowiska uruchomieniowego kanału. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Wskazówki instalacji/aktualizacji dla pluginów bundlowanych i publikowanych zewnętrznie.                                                      |
| `openclaw.install.defaultChoice`                                  | Preferowana ścieżka instalacji, gdy dostępnych jest wiele źródeł instalacji.                                                                 |
| `openclaw.install.minHostVersion`                                 | Minimalna obsługiwana wersja hosta OpenClaw, z użyciem dolnej granicy semver, takiej jak `>=2026.3.22`.                                     |
| `openclaw.install.allowInvalidConfigRecovery`                     | Pozwala na wąską ścieżkę odzyskiwania przez ponowną instalację pluginu bundlowanego, gdy konfiguracja jest nieprawidłowa.                   |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Pozwala na ładowanie powierzchni kanału tylko do konfiguracji przed pełnym pluginem kanału podczas uruchamiania.                            |

`openclaw.install.minHostVersion` jest wymuszane podczas instalacji i ładowania rejestru
manifestów. Nieprawidłowe wartości są odrzucane; nowsze, ale prawidłowe wartości pomijają
plugin na starszych hostach.

`openclaw.install.allowInvalidConfigRecovery` jest celowo wąskie. Nie
sprawia, że dowolne uszkodzone konfiguracje stają się instalowalne. Obecnie pozwala tylko
przepływom instalacji odzyskać działanie po określonych nieaktualnych błędach aktualizacji pluginów bundlowanych, takich jak
brakująca ścieżka pluginu bundlowanego albo nieaktualny wpis `channels.<id>` dla tego samego
pluginu bundlowanego. Niezwiązane błędy konfiguracji nadal blokują instalację i kierują operatorów
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

Używaj tego, gdy przepływy konfiguracji, doctor lub configured-state potrzebują lekkiego testu
uwierzytelnienia tak/nie przed załadowaniem pełnego pluginu kanału. Eksport docelowy powinien być małą
funkcją, która odczytuje tylko utrwalony stan; nie kieruj tego przez pełną belkę runtime kanału.

`openclaw.channel.configuredState` ma ten sam kształt dla lekkich sprawdzeń
skonfigurowanego stanu tylko z env:

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

Używaj tego, gdy kanał może odpowiedzieć o stanie konfiguracji na podstawie env lub innych małych
wejść nieruntime. Jeśli sprawdzenie wymaga pełnego rozstrzygania konfiguracji albo rzeczywistego
środowiska uruchomieniowego kanału, pozostaw tę logikę w hooku pluginu `config.hasConfiguredState`.

## Wymagania JSON Schema

- **Każdy plugin musi dostarczać JSON Schema**, nawet jeśli nie przyjmuje żadnej konfiguracji.
- Pusty schemat jest akceptowalny (na przykład `{ "type": "object", "additionalProperties": false }`).
- Schematy są walidowane w czasie odczytu/zapisu konfiguracji, a nie w runtime.

## Zachowanie walidacji

- Nieznane klucze `channels.*` są **błędami**, chyba że ID kanału jest zadeklarowane przez
  manifest pluginu.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` i `plugins.slots.*`
  muszą odwoływać się do **wykrywalnych** ID pluginów. Nieznane ID są **błędami**.
- Jeśli plugin jest zainstalowany, ale ma uszkodzony lub brakujący manifest albo schemat,
  walidacja kończy się niepowodzeniem, a Doctor raportuje błąd pluginu.
- Jeśli konfiguracja pluginu istnieje, ale plugin jest **wyłączony**, konfiguracja jest zachowywana, a
  w Doctor + logach pojawia się **ostrzeżenie**.

Zobacz [Configuration reference](/pl/gateway/configuration), aby poznać pełny schemat `plugins.*`.

## Uwagi

- Manifest jest **wymagany dla natywnych pluginów OpenClaw**, w tym dla ładowań z lokalnego systemu plików.
- Runtime nadal ładuje moduł pluginu osobno; manifest służy wyłącznie do
  wykrywania + walidacji.
- Natywne manifesty są parsowane przy użyciu JSON5, więc komentarze, końcowe przecinki i
  nieujęte w cudzysłów klucze są akceptowane, o ile końcowa wartość nadal jest obiektem.
- Loader manifestu odczytuje tylko udokumentowane pola manifestu. Unikaj dodawania
  własnych niestandardowych kluczy najwyższego poziomu.
- `providerAuthEnvVars` to lekka ścieżka metadanych dla testów uwierzytelniania, walidacji znaczników env
  i podobnych powierzchni uwierzytelniania dostawcy, które nie powinny uruchamiać środowiska uruchomieniowego pluginu
  tylko po to, aby sprawdzić nazwy env.
- `providerAuthChoices` to lekka ścieżka metadanych dla selektorów opcji uwierzytelniania,
  rozstrzygania `--auth-choice`, mapowania preferowanego dostawcy i prostej rejestracji
  flag CLI onboardingu przed załadowaniem środowiska uruchomieniowego dostawcy. Dla metadanych kreatora runtime,
  które wymagają kodu dostawcy, zobacz
  [Provider runtime hooks](/pl/plugins/architecture#provider-runtime-hooks).
- Wyłączne typy pluginów są wybierane przez `plugins.slots.*`.
  - `kind: "memory"` jest wybierane przez `plugins.slots.memory`.
  - `kind: "context-engine"` jest wybierane przez `plugins.slots.contextEngine`
    (domyślnie: wbudowane `legacy`).
- `channels`, `providers` i `skills` można pominąć, gdy
  plugin ich nie potrzebuje.
- Jeśli plugin zależy od modułów natywnych, udokumentuj kroki budowania i wszelkie
  wymagania listy dozwolonych menedżera pakietów (na przykład pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Powiązane

- [Building Plugins](/pl/plugins/building-plugins) — pierwsze kroki z pluginami
- [Plugin Architecture](/pl/plugins/architecture) — architektura wewnętrzna
- [SDK Overview](/pl/plugins/sdk-overview) — dokumentacja Plugin SDK
