---
read_when:
    - Chcesz skonfigurować dostawców wyszukiwania w pamięci lub modele osadzeń
    - Chcesz skonfigurować backend QMD
    - Chcesz dostroić wyszukiwanie hybrydowe, MMR lub rozpad czasowy
    - Chcesz włączyć multimodalne indeksowanie pamięci
summary: Wszystkie ustawienia konfiguracyjne dotyczące wyszukiwania w pamięci, dostawców osadzeń, QMD, wyszukiwania hybrydowego i indeksowania multimodalnego
title: Dokumentacja konfiguracji pamięci
x-i18n:
    generated_at: "2026-04-15T14:40:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# Dokumentacja konfiguracji pamięci

Ta strona zawiera wszystkie ustawienia konfiguracyjne wyszukiwania w pamięci w OpenClaw. Aby zapoznać się z omówieniami koncepcyjnymi, zobacz:

- [Przegląd pamięci](/pl/concepts/memory) -- jak działa pamięć
- [Wbudowany silnik](/pl/concepts/memory-builtin) -- domyślny backend SQLite
- [Silnik QMD](/pl/concepts/memory-qmd) -- lokalny sidecar
- [Wyszukiwanie w pamięci](/pl/concepts/memory-search) -- potok wyszukiwania i strojenie
- [Active Memory](/pl/concepts/active-memory) -- włączanie subagenta pamięci dla sesji interaktywnych

Wszystkie ustawienia wyszukiwania w pamięci znajdują się w `agents.defaults.memorySearch` w
`openclaw.json`, o ile nie zaznaczono inaczej.

Jeśli szukasz przełącznika funkcji **active memory** i konfiguracji subagenta,
znajdują się one w `plugins.entries.active-memory`, a nie w `memorySearch`.

Active memory korzysta z modelu dwóch bramek:

1. Plugin musi być włączony i kierować na bieżący identyfikator agenta
2. Żądanie musi być kwalifikującą się interaktywną trwałą sesją czatu

Model aktywacji, konfigurację należącą do Plugin, trwałość transkryptu i bezpieczny wzorzec wdrażania opisano w [Active Memory](/pl/concepts/active-memory).

---

## Wybór dostawcy

| Klucz      | Typ       | Domyślnie       | Opis                                                                                                          |
| ---------- | --------- | --------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | wykrywany automatycznie | Identyfikator adaptera osadzeń: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | domyślny dostawcy | Nazwa modelu osadzeń                                                                                          |
| `fallback` | `string`  | `"none"`        | Identyfikator zapasowego adaptera, gdy główny zawiedzie                                                       |
| `enabled`  | `boolean` | `true`          | Włącza lub wyłącza wyszukiwanie w pamięci                                                                     |

### Kolejność automatycznego wykrywania

Gdy `provider` nie jest ustawiony, OpenClaw wybiera pierwszy dostępny:

1. `local` -- jeśli skonfigurowano `memorySearch.local.modelPath` i plik istnieje.
2. `github-copilot` -- jeśli można rozpoznać token GitHub Copilot (zmienna środowiskowa lub profil uwierzytelniania).
3. `openai` -- jeśli można rozpoznać klucz OpenAI.
4. `gemini` -- jeśli można rozpoznać klucz Gemini.
5. `voyage` -- jeśli można rozpoznać klucz Voyage.
6. `mistral` -- jeśli można rozpoznać klucz Mistral.
7. `bedrock` -- jeśli łańcuch poświadczeń AWS SDK zostanie rozpoznany (rola instancji, klucze dostępu, profil, SSO, tożsamość webowa lub współdzielona konfiguracja).

`ollama` jest obsługiwany, ale nie jest wykrywany automatycznie (ustaw go jawnie).

### Rozpoznawanie kluczy API

Zdalne osadzenia wymagają klucza API. Bedrock zamiast tego używa domyślnego
łańcucha poświadczeń AWS SDK (role instancji, SSO, klucze dostępu).

| Dostawca       | Zmienna środowiskowa                              | Klucz konfiguracji                |
| -------------- | ------------------------------------------------- | --------------------------------- |
| Bedrock        | łańcuch poświadczeń AWS                           | Klucz API nie jest wymagany       |
| Gemini         | `GEMINI_API_KEY`                                  | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Profil uwierzytelniania przez logowanie urządzenia |
| Mistral        | `MISTRAL_API_KEY`                                 | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (placeholder)                    | --                                |
| OpenAI         | `OPENAI_API_KEY`                                  | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                  | `models.providers.voyage.apiKey`  |

OAuth Codex obejmuje tylko chat/completions i nie spełnia wymagań żądań
osadzeń.

---

## Konfiguracja zdalnego punktu końcowego

Dla niestandardowych punktów końcowych zgodnych z OpenAI lub nadpisania ustawień domyślnych dostawcy:

| Klucz            | Typ      | Opis                                             |
| ---------------- | -------- | ------------------------------------------------ |
| `remote.baseUrl` | `string` | Niestandardowy bazowy URL API                    |
| `remote.apiKey`  | `string` | Nadpisanie klucza API                            |
| `remote.headers` | `object` | Dodatkowe nagłówki HTTP (łączone z domyślnymi ustawieniami dostawcy) |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Konfiguracja specyficzna dla Gemini

| Klucz                  | Typ      | Domyślnie             | Opis                                         |
| ---------------------- | -------- | --------------------- | -------------------------------------------- |
| `model`                | `string` | `gemini-embedding-001` | Obsługuje także `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                | Dla Embedding 2: 768, 1536 lub 3072          |

<Warning>
Zmiana modelu lub `outputDimensionality` uruchamia automatyczne pełne ponowne indeksowanie.
</Warning>

---

## Konfiguracja osadzeń Bedrock

Bedrock używa domyślnego łańcucha poświadczeń AWS SDK -- klucze API nie są potrzebne.
Jeśli OpenClaw działa na EC2 z rolą instancji z włączonym Bedrock, wystarczy ustawić
dostawcę i model:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0",
      },
    },
  },
}
```

| Klucz                  | Typ      | Domyślnie                     | Opis                            |
| ---------------------- | -------- | ----------------------------- | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Dowolny identyfikator modelu osadzeń Bedrock |
| `outputDimensionality` | `number` | domyślna wartość modelu       | Dla Titan V2: 256, 512 lub 1024 |

### Obsługiwane modele

Obsługiwane są następujące modele (z wykrywaniem rodziny i domyślnymi
wymiarami):

| Model ID                                   | Dostawca   | Domyślne wymiary | Konfigurowalne wymiary |
| ------------------------------------------ | ---------- | ---------------- | ---------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024             | 256, 512, 1024         |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536             | --                     |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536             | --                     |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024             | --                     |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024             | 256, 384, 1024, 3072   |
| `cohere.embed-english-v3`                  | Cohere     | 1024             | --                     |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024             | --                     |
| `cohere.embed-v4:0`                        | Cohere     | 1536             | 256-1536               |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512              | --                     |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024             | --                     |

Warianty z sufiksem przepustowości (na przykład `amazon.titan-embed-text-v1:2:8k`) dziedziczą
konfigurację modelu bazowego.

### Uwierzytelnianie

Uwierzytelnianie Bedrock używa standardowej kolejności rozpoznawania poświadczeń AWS SDK:

1. Zmienne środowiskowe (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Pamięć podręczna tokenów SSO
3. Poświadczenia tokena tożsamości webowej
4. Współdzielone pliki poświadczeń i konfiguracji
5. Poświadczenia metadanych ECS lub EC2

Region jest rozpoznawany na podstawie `AWS_REGION`, `AWS_DEFAULT_REGION`,
`baseUrl` dostawcy `amazon-bedrock` albo domyślnie przyjmuje wartość `us-east-1`.

### Uprawnienia IAM

Rola lub użytkownik IAM potrzebuje:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Aby zachować zasadę najmniejszych uprawnień, ogranicz `InvokeModel` do konkretnego modelu:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Konfiguracja lokalnych osadzeń

| Klucz                 | Typ      | Domyślnie             | Opis                              |
| --------------------- | -------- | --------------------- | --------------------------------- |
| `local.modelPath`     | `string` | pobierany automatycznie | Ścieżka do pliku modelu GGUF      |
| `local.modelCacheDir` | `string` | domyślna wartość node-llama-cpp | Katalog pamięci podręcznej dla pobranych modeli |

Domyślny model: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, pobierany automatycznie).
Wymaga natywnego buildu: `pnpm approve-builds`, a następnie `pnpm rebuild node-llama-cpp`.

---

## Konfiguracja wyszukiwania hybrydowego

Wszystko w `memorySearch.query.hybrid`:

| Klucz                 | Typ       | Domyślnie | Opis                               |
| --------------------- | --------- | --------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`    | Włącza hybrydowe wyszukiwanie BM25 + wektorowe |
| `vectorWeight`        | `number`  | `0.7`     | Waga dla wyników wektorowych (0-1) |
| `textWeight`          | `number`  | `0.3`     | Waga dla wyników BM25 (0-1)        |
| `candidateMultiplier` | `number`  | `4`       | Mnożnik rozmiaru puli kandydatów   |

### MMR (różnorodność)

| Klucz         | Typ       | Domyślnie | Opis                                       |
| ------------- | --------- | --------- | ------------------------------------------ |
| `mmr.enabled` | `boolean` | `false`   | Włącza ponowne rangowanie MMR              |
| `mmr.lambda`  | `number`  | `0.7`     | 0 = maksymalna różnorodność, 1 = maksymalna trafność |

### Rozpad czasowy (świeżość)

| Klucz                        | Typ       | Domyślnie | Opis                          |
| ---------------------------- | --------- | --------- | ----------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false`   | Włącza premiowanie świeżości  |
| `temporalDecay.halfLifeDays` | `number`  | `30`      | Wynik spada o połowę co N dni |

Pliki evergreen (`MEMORY.md`, pliki bez daty w `memory/`) nigdy nie podlegają rozpadowi.

### Pełny przykład

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## Dodatkowe ścieżki pamięci

| Klucz       | Typ        | Opis                                      |
| ----------- | ---------- | ----------------------------------------- |
| `extraPaths` | `string[]` | Dodatkowe katalogi lub pliki do indeksowania |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

Ścieżki mogą być bezwzględne lub względne względem workspace. Katalogi są skanowane
rekurencyjnie pod kątem plików `.md`. Obsługa dowiązań symbolicznych zależy od aktywnego backendu:
wbudowany silnik ignoruje dowiązania symboliczne, natomiast QMD stosuje zachowanie
bazowego skanera QMD.

Do wyszukiwania transkryptów między agentami w zakresie agenta użyj
`agents.list[].memorySearch.qmd.extraCollections` zamiast `memory.qmd.paths`.
Te dodatkowe kolekcje mają ten sam kształt `{ path, name, pattern? }`, ale
są scalane per agent i mogą zachowywać jawne współdzielone nazwy, gdy ścieżka
wskazuje poza bieżący workspace.
Jeśli ta sama rozpoznana ścieżka pojawi się zarówno w `memory.qmd.paths`, jak i
`memorySearch.qmd.extraCollections`, QMD zachowuje pierwszy wpis i pomija
duplikat.

---

## Pamięć multimodalna (Gemini)

Indeksuj obrazy i audio wraz z Markdown przy użyciu Gemini Embedding 2:

| Klucz                     | Typ        | Domyślnie  | Opis                                   |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Włącza indeksowanie multimodalne       |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` lub `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Maksymalny rozmiar pliku do indeksowania |

Dotyczy tylko plików w `extraPaths`. Domyślne katalogi główne pamięci pozostają tylko dla Markdown.
Wymaga `gemini-embedding-2-preview`. `fallback` musi mieć wartość `"none"`.

Obsługiwane formaty: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(obrazy); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (audio).

---

## Pamięć podręczna osadzeń

| Klucz             | Typ       | Domyślnie | Opis                                  |
| ----------------- | --------- | --------- | ------------------------------------- |
| `cache.enabled`   | `boolean` | `false`   | Buforuje osadzenia fragmentów w SQLite |
| `cache.maxEntries` | `number` | `50000`   | Maksymalna liczba buforowanych osadzeń |

Zapobiega ponownemu tworzeniu osadzeń dla niezmienionego tekstu podczas ponownego indeksowania lub aktualizacji transkryptów.

---

## Indeksowanie wsadowe

| Klucz                         | Typ       | Domyślnie | Opis                         |
| ----------------------------- | --------- | --------- | ---------------------------- |
| `remote.batch.enabled`        | `boolean` | `false`   | Włącza interfejs API osadzeń wsadowych |
| `remote.batch.concurrency`    | `number`  | `2`       | Równoległe zadania wsadowe   |
| `remote.batch.wait`           | `boolean` | `true`    | Czeka na ukończenie wsadu    |
| `remote.batch.pollIntervalMs` | `number`  | --        | Interwał odpytywania         |
| `remote.batch.timeoutMinutes` | `number`  | --        | Limit czasu wsadu            |

Dostępne dla `openai`, `gemini` i `voyage`. Wsad OpenAI jest zwykle
najszybszy i najtańszy przy dużych uzupełnieniach wstecznych.

---

## Wyszukiwanie pamięci sesji (eksperymentalne)

Indeksuje transkrypty sesji i udostępnia je przez `memory_search`:

| Klucz                        | Typ        | Domyślnie   | Opis                                      |
| ---------------------------- | ---------- | ----------- | ----------------------------------------- |
| `experimental.sessionMemory` | `boolean`  | `false`     | Włącza indeksowanie sesji                 |
| `sources`                    | `string[]` | `["memory"]` | Dodaj `"sessions"`, aby uwzględnić transkrypty |
| `sync.sessions.deltaBytes`   | `number`   | `100000`    | Próg bajtów dla ponownego indeksowania    |
| `sync.sessions.deltaMessages` | `number`  | `50`        | Próg liczby wiadomości dla ponownego indeksowania |

Indeksowanie sesji jest opcjonalne i działa asynchronicznie. Wyniki mogą być
nieco nieaktualne. Logi sesji są przechowywane na dysku, więc granicą zaufania
jest dostęp do systemu plików.

---

## Przyspieszenie wektorowe SQLite (sqlite-vec)

| Klucz                      | Typ       | Domyślnie | Opis                                  |
| -------------------------- | --------- | --------- | ------------------------------------- |
| `store.vector.enabled`     | `boolean` | `true`    | Używa sqlite-vec do zapytań wektorowych |
| `store.vector.extensionPath` | `string` | bundled   | Nadpisuje ścieżkę sqlite-vec          |

Gdy sqlite-vec jest niedostępne, OpenClaw automatycznie przechodzi na
obliczanie podobieństwa cosinusowego w procesie.

---

## Magazyn indeksu

| Klucz                 | Typ      | Domyślnie                            | Opis                                        |
| --------------------- | -------- | ------------------------------------ | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Lokalizacja indeksu (obsługuje token `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                          | Tokenizer FTS5 (`unicode61` lub `trigram`)  |

---

## Konfiguracja backendu QMD

Aby włączyć, ustaw `memory.backend = "qmd"`. Wszystkie ustawienia QMD znajdują się w
`memory.qmd`:

| Klucz                    | Typ       | Domyślnie | Opis                                         |
| ------------------------ | --------- | --------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`     | Ścieżka do pliku wykonywalnego QMD           |
| `searchMode`             | `string`  | `search`  | Polecenie wyszukiwania: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`    | Automatycznie indeksuje `MEMORY.md` + `memory/**/*.md` |
| `paths[]`                | `array`   | --        | Dodatkowe ścieżki: `{ name, path, pattern? }` |
| `sessions.enabled`       | `boolean` | `false`   | Indeksuje transkrypty sesji                  |
| `sessions.retentionDays` | `number`  | --        | Czas przechowywania transkryptów             |
| `sessions.exportDir`     | `string`  | --        | Katalog eksportu                             |

OpenClaw preferuje bieżące kształty kolekcji QMD i zapytań MCP, ale zachowuje
zgodność ze starszymi wydaniami QMD, przechodząc w razie potrzeby na starsze flagi kolekcji `--mask`
i starsze nazwy narzędzi MCP.

Nadpisania modeli QMD pozostają po stronie QMD, a nie w konfiguracji OpenClaw. Jeśli chcesz
globalnie nadpisać modele QMD, ustaw zmienne środowiskowe takie jak
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` i `QMD_GENERATE_MODEL` w środowisku
uruchomieniowym Gateway.

### Harmonogram aktualizacji

| Klucz                     | Typ       | Domyślnie | Opis                                  |
| ------------------------- | --------- | --------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`      | Interwał odświeżania                  |
| `update.debounceMs`       | `number`  | `15000`   | Debounce zmian plików                 |
| `update.onBoot`           | `boolean` | `true`    | Odświeżanie przy uruchomieniu         |
| `update.waitForBootSync`  | `boolean` | `false`   | Blokuje uruchamianie do ukończenia odświeżania |
| `update.embedInterval`    | `string`  | --        | Osobna kadencja osadzania             |
| `update.commandTimeoutMs` | `number`  | --        | Limit czasu dla poleceń QMD           |
| `update.updateTimeoutMs`  | `number`  | --        | Limit czasu dla operacji aktualizacji QMD |
| `update.embedTimeoutMs`   | `number`  | --        | Limit czasu dla operacji osadzania QMD |

### Limity

| Klucz                     | Typ      | Domyślnie | Opis                              |
| ------------------------- | -------- | --------- | --------------------------------- |
| `limits.maxResults`       | `number` | `6`       | Maksymalna liczba wyników wyszukiwania |
| `limits.maxSnippetChars`  | `number` | --        | Ogranicza długość fragmentu       |
| `limits.maxInjectedChars` | `number` | --        | Ogranicza łączną liczbę wstrzykniętych znaków |
| `limits.timeoutMs`        | `number` | `4000`    | Limit czasu wyszukiwania          |

### Zakres

Kontroluje, które sesje mogą otrzymywać wyniki wyszukiwania QMD. Ten sam schemat co
[`session.sendPolicy`](/pl/gateway/configuration-reference#session):

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Dostarczana domyślna konfiguracja zezwala na sesje bezpośrednie i kanałowe, nadal odrzucając
grupy.

Domyślnie tylko DM. `match.keyPrefix` dopasowuje znormalizowany klucz sesji;
`match.rawKeyPrefix` dopasowuje surowy klucz wraz z `agent:<id>:`.

### Cytowania

`memory.citations` dotyczy wszystkich backendów:

| Wartość          | Zachowanie                                           |
| ---------------- | ---------------------------------------------------- |
| `auto` (domyślnie) | Dodaje stopkę `Source: <path#line>` we fragmentach |
| `on`             | Zawsze dodaje stopkę                                 |
| `off`            | Pomija stopkę (ścieżka nadal jest przekazywana wewnętrznie do agenta) |

### Pełny przykład QMD

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming

Dreaming jest konfigurowane w `plugins.entries.memory-core.config.dreaming`,
a nie w `agents.defaults.memorySearch`.

Dreaming działa jako jeden zaplanowany przebieg i wykorzystuje wewnętrzne fazy light/deep/REM jako
szczegół implementacyjny.

Aby zapoznać się z zachowaniem koncepcyjnym i poleceniami slash, zobacz [Dreaming](/pl/concepts/dreaming).

### Ustawienia użytkownika

| Klucz       | Typ       | Domyślnie   | Opis                                              |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`     | Włącza lub wyłącza Dreaming całkowicie            |
| `frequency` | `string`  | `0 3 * * *` | Opcjonalna kadencja Cron dla pełnego przebiegu Dreaming |

### Przykład

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            frequency: "0 3 * * *",
          },
        },
      },
    },
  },
}
```

Uwagi:

- Dreaming zapisuje stan maszyny w `memory/.dreams/`.
- Dreaming zapisuje czytelne dla człowieka dane wyjściowe narracji do `DREAMS.md` (lub istniejącego `dreams.md`).
- Zasady faz light/deep/REM i progi są zachowaniem wewnętrznym, a nie konfiguracją dostępną dla użytkownika.
