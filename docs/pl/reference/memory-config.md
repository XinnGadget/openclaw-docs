---
read_when:
    - Chcesz skonfigurować dostawców wyszukiwania pamięci lub modele embeddingów
    - Chcesz skonfigurować backend QMD
    - Chcesz dostroić wyszukiwanie hybrydowe, MMR lub zanik czasowy
    - Chcesz włączyć multimodalne indeksowanie pamięci
summary: Wszystkie ustawienia konfiguracji dla wyszukiwania pamięci, dostawców embeddingów, QMD, wyszukiwania hybrydowego i indeksowania multimodalnego
title: Dokumentacja konfiguracji pamięci
x-i18n:
    generated_at: "2026-04-06T03:13:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0de0b85125443584f4e575cf673ca8d9bd12ecd849d73c537f4a17545afa93fd
    source_path: reference/memory-config.md
    workflow: 15
---

# Dokumentacja konfiguracji pamięci

Ta strona zawiera wszystkie ustawienia konfiguracji wyszukiwania pamięci w OpenClaw. Aby zapoznać się z
omówieniem koncepcyjnym, zobacz:

- [Przegląd pamięci](/pl/concepts/memory) -- jak działa pamięć
- [Wbudowany silnik](/pl/concepts/memory-builtin) -- domyślny backend SQLite
- [Silnik QMD](/pl/concepts/memory-qmd) -- lokalny sidecar
- [Wyszukiwanie pamięci](/pl/concepts/memory-search) -- pipeline wyszukiwania i strojenie

Wszystkie ustawienia wyszukiwania pamięci znajdują się w `agents.defaults.memorySearch` w
`openclaw.json`, chyba że zaznaczono inaczej.

---

## Wybór dostawcy

| Key        | Type      | Default          | Opis                                                                                       |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------ |
| `provider` | `string`  | wykrywany automatycznie | Identyfikator adaptera embeddingów: `openai`, `gemini`, `voyage`, `mistral`, `bedrock`, `ollama`, `local` |
| `model`    | `string`  | domyślny dostawcy | Nazwa modelu embeddingów                                                                   |
| `fallback` | `string`  | `"none"`         | Identyfikator adaptera fallback, gdy podstawowy zawiedzie                                  |
| `enabled`  | `boolean` | `true`           | Włącza lub wyłącza wyszukiwanie pamięci                                                    |

### Kolejność automatycznego wykrywania

Gdy `provider` nie jest ustawiony, OpenClaw wybiera pierwszy dostępny:

1. `local` -- jeśli `memorySearch.local.modelPath` jest skonfigurowane i plik istnieje.
2. `openai` -- jeśli można rozpoznać klucz OpenAI.
3. `gemini` -- jeśli można rozpoznać klucz Gemini.
4. `voyage` -- jeśli można rozpoznać klucz Voyage.
5. `mistral` -- jeśli można rozpoznać klucz Mistral.
6. `bedrock` -- jeśli łańcuch poświadczeń AWS SDK zostanie rozpoznany (rola instancji, klucze dostępu, profil, SSO, tożsamość webowa lub współdzielona konfiguracja).

`ollama` jest obsługiwane, ale nie jest wykrywane automatycznie (ustaw je jawnie).

### Rozpoznawanie klucza API

Zdalne embeddingi wymagają klucza API. Bedrock zamiast tego używa domyślnego
łańcucha poświadczeń AWS SDK (role instancji, SSO, klucze dostępu).

| Provider | Zmienna env                    | Klucz config                      |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Bedrock  | łańcuch poświadczeń AWS        | Klucz API nie jest potrzebny      |
| Ollama   | `OLLAMA_API_KEY` (placeholder) | --                                |

OAuth Codex obejmuje tylko czat/uzupełnienia i nie spełnia wymagań żądań embeddingów.

---

## Konfiguracja zdalnego endpointu

Dla niestandardowych endpointów zgodnych z OpenAI lub nadpisywania domyślnych wartości dostawcy:

| Key              | Type     | Opis                                               |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | Niestandardowy bazowy URL API                      |
| `remote.apiKey`  | `string` | Nadpisanie klucza API                              |
| `remote.headers` | `object` | Dodatkowe nagłówki HTTP (scalane z domyślnymi dostawcy) |

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

| Key                    | Type     | Default                | Opis                                       |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | Obsługuje też `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Dla Embedding 2: 768, 1536 lub 3072        |

<Warning>
Zmiana modelu lub `outputDimensionality` uruchamia automatyczne pełne ponowne indeksowanie.
</Warning>

---

## Konfiguracja embeddingów Bedrock

Bedrock używa domyślnego łańcucha poświadczeń AWS SDK -- klucze API nie są potrzebne.
Jeśli OpenClaw działa na EC2 z rolą instancji z włączonym Bedrock, po prostu ustaw
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

| Key                    | Type     | Default                        | Opis                          |
| ---------------------- | -------- | ------------------------------ | ----------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | Dowolny identyfikator modelu embeddingów Bedrock |
| `outputDimensionality` | `number` | domyślna wartość modelu        | Dla Titan V2: 256, 512 lub 1024 |

### Obsługiwane modele

Obsługiwane są następujące modele (z wykrywaniem rodziny i domyślnymi
wymiarami):

| Model ID                                   | Provider   | Domyślne wymiary | Konfigurowalne wymiary |
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
2. Cache tokenów SSO
3. Poświadczenia tokena tożsamości webowej
4. Współdzielone pliki poświadczeń i konfiguracji
5. Poświadczenia metadanych ECS lub EC2

Region jest rozpoznawany z `AWS_REGION`, `AWS_DEFAULT_REGION`, `baseUrl`
dostawcy `amazon-bedrock` lub domyślnie ustawiany na `us-east-1`.

### Uprawnienia IAM

Rola IAM lub użytkownik potrzebują:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Dla zasady najmniejszych uprawnień ogranicz `InvokeModel` do konkretnego modelu:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Konfiguracja lokalnych embeddingów

| Key                   | Type     | Default                | Opis                            |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | pobierane automatycznie | Ścieżka do pliku modelu GGUF    |
| `local.modelCacheDir` | `string` | domyślna wartość node-llama-cpp | Katalog cache dla pobranych modeli |

Domyślny model: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, pobierany automatycznie).
Wymaga natywnej kompilacji: `pnpm approve-builds`, a następnie `pnpm rebuild node-llama-cpp`.

---

## Konfiguracja wyszukiwania hybrydowego

Wszystko pod `memorySearch.query.hybrid`:

| Key                   | Type      | Default | Opis                             |
| --------------------- | --------- | ------- | -------------------------------- |
| `enabled`             | `boolean` | `true`  | Włącza hybrydowe wyszukiwanie BM25 + wektorowe |
| `vectorWeight`        | `number`  | `0.7`   | Waga dla wyników wektorowych (0-1) |
| `textWeight`          | `number`  | `0.3`   | Waga dla wyników BM25 (0-1)      |
| `candidateMultiplier` | `number`  | `4`     | Mnożnik rozmiaru puli kandydatów |

### MMR (różnorodność)

| Key           | Type      | Default | Opis                                 |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Włącza ponowne rangowanie MMR        |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = maksymalna różnorodność, 1 = maksymalna trafność |

### Zanik czasowy (świeżość)

| Key                          | Type      | Default | Opis                          |
| ---------------------------- | --------- | ------- | ----------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Włącza premiowanie świeżości  |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | Wynik spada o połowę co N dni |

Pliki evergreen (`MEMORY.md`, pliki bez dat w `memory/`) nigdy nie podlegają zanikowi.

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

| Key          | Type       | Opis                                         |
| ------------ | ---------- | -------------------------------------------- |
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

Ścieżki mogą być bezwzględne lub względne względem obszaru roboczego. Katalogi są skanowane
rekurencyjnie w poszukiwaniu plików `.md`. Obsługa symlinków zależy od aktywnego backendu:
wbudowany silnik ignoruje symlinki, podczas gdy QMD korzysta z zachowania
bazowego skanera QMD.

Dla wyszukiwania transkryptów między agentami w zakresie agenta użyj
`agents.list[].memorySearch.qmd.extraCollections` zamiast `memory.qmd.paths`.
Te dodatkowe kolekcje używają tego samego kształtu `{ path, name, pattern? }`, ale
są scalane dla każdego agenta i mogą zachować jawne współdzielone nazwy, gdy ścieżka
wskazuje poza bieżący obszar roboczy.
Jeśli ta sama rozpoznana ścieżka pojawi się zarówno w `memory.qmd.paths`, jak i
`memorySearch.qmd.extraCollections`, QMD zachowuje pierwszy wpis i pomija
duplikat.

---

## Pamięć multimodalna (Gemini)

Indeksuj obrazy i audio razem z Markdown przy użyciu Gemini Embedding 2:

| Key                       | Type       | Default    | Opis                                        |
| ------------------------- | ---------- | ---------- | ------------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Włącza indeksowanie multimodalne            |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` lub `["all"]`      |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Maksymalny rozmiar pliku do indeksowania    |

Dotyczy tylko plików w `extraPaths`. Domyślne korzenie pamięci pozostają tylko dla Markdown.
Wymaga `gemini-embedding-2-preview`. `fallback` musi mieć wartość `"none"`.

Obsługiwane formaty: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(obrazy); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (audio).

---

## Cache embeddingów

| Key                | Type      | Default | Opis                             |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | Buforuje embeddingi fragmentów w SQLite |
| `cache.maxEntries` | `number`  | `50000` | Maksymalna liczba buforowanych embeddingów |

Zapobiega ponownemu osadzaniu niezmienionego tekstu podczas reindeksowania lub aktualizacji transkryptów.

---

## Indeksowanie wsadowe

| Key                           | Type      | Default | Opis                         |
| ----------------------------- | --------- | ------- | ---------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | Włącza API embeddingów wsadowych |
| `remote.batch.concurrency`    | `number`  | `2`     | Równoległe zadania wsadowe   |
| `remote.batch.wait`           | `boolean` | `true`  | Czeka na zakończenie wsadu   |
| `remote.batch.pollIntervalMs` | `number`  | --      | Interwał odpytywania         |
| `remote.batch.timeoutMinutes` | `number`  | --      | Limit czasu wsadu            |

Dostępne dla `openai`, `gemini` i `voyage`. Wsady OpenAI są zwykle
najszybsze i najtańsze przy dużych uzupełnieniach zaległości.

---

## Wyszukiwanie pamięci sesji (eksperymentalne)

Indeksuj transkrypty sesji i udostępniaj je przez `memory_search`:

| Key                           | Type       | Default      | Opis                                        |
| ----------------------------- | ---------- | ------------ | ------------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | Włącza indeksowanie sesji                   |
| `sources`                     | `string[]` | `["memory"]` | Dodaj `"sessions"`, aby uwzględnić transkrypty |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | Próg bajtów dla reindeksowania              |
| `sync.sessions.deltaMessages` | `number`   | `50`         | Próg wiadomości dla reindeksowania          |

Indeksowanie sesji jest opt-in i działa asynchronicznie. Wyniki mogą być nieco
nieaktualne. Logi sesji są przechowywane na dysku, więc dostęp do systemu plików należy traktować jako
granicę zaufania.

---

## Przyspieszenie wektorowe SQLite (sqlite-vec)

| Key                          | Type      | Default | Opis                               |
| ---------------------------- | --------- | ------- | ---------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | Używa sqlite-vec dla zapytań wektorowych |
| `store.vector.extensionPath` | `string`  | dołączone | Nadpisuje ścieżkę sqlite-vec       |

Gdy sqlite-vec jest niedostępne, OpenClaw automatycznie przechodzi awaryjnie do
podobieństwa cosinusowego w procesie.

---

## Przechowywanie indeksu

| Key                   | Type     | Default                               | Opis                                         |
| --------------------- | -------- | ------------------------------------- | -------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Lokalizacja indeksu (obsługuje token `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                           | Tokenizer FTS5 (`unicode61` lub `trigram`)   |

---

## Konfiguracja backendu QMD

Ustaw `memory.backend = "qmd"`, aby włączyć. Wszystkie ustawienia QMD znajdują się w
`memory.qmd`:

| Key                      | Type      | Default  | Opis                                         |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | Ścieżka do pliku wykonywalnego QMD           |
| `searchMode`             | `string`  | `search` | Polecenie wyszukiwania: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | Automatycznie indeksuje `MEMORY.md` + `memory/**/*.md` |
| `paths[]`                | `array`   | --       | Dodatkowe ścieżki: `{ name, path, pattern? }` |
| `sessions.enabled`       | `boolean` | `false`  | Indeksuje transkrypty sesji                  |
| `sessions.retentionDays` | `number`  | --       | Retencja transkryptów                        |
| `sessions.exportDir`     | `string`  | --       | Katalog eksportu                             |

OpenClaw preferuje bieżące kształty kolekcji QMD i zapytań MCP, ale zachowuje
zgodność ze starszymi wydaniami QMD, przechodząc awaryjnie do starszych flag kolekcji `--mask`
i starszych nazw narzędzi MCP, gdy jest to potrzebne.

Nadpisania modeli QMD pozostają po stronie QMD, a nie w config OpenClaw. Jeśli musisz
globalnie nadpisać modele QMD, ustaw zmienne środowiskowe, takie jak
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` i `QMD_GENERATE_MODEL`, w środowisku runtime
gateway.

### Harmonogram aktualizacji

| Key                       | Type      | Default | Opis                                   |
| ------------------------- | --------- | ------- | -------------------------------------- |
| `update.interval`         | `string`  | `5m`    | Interwał odświeżania                   |
| `update.debounceMs`       | `number`  | `15000` | Opóźnienie zmian plików                |
| `update.onBoot`           | `boolean` | `true`  | Odświeżanie przy uruchomieniu          |
| `update.waitForBootSync`  | `boolean` | `false` | Blokuje uruchomienie do zakończenia odświeżania |
| `update.embedInterval`    | `string`  | --      | Oddzielna kadencja embeddingów         |
| `update.commandTimeoutMs` | `number`  | --      | Limit czasu dla poleceń QMD            |
| `update.updateTimeoutMs`  | `number`  | --      | Limit czasu dla operacji aktualizacji QMD |
| `update.embedTimeoutMs`   | `number`  | --      | Limit czasu dla operacji embeddingów QMD |

### Limity

| Key                       | Type     | Default | Opis                           |
| ------------------------- | -------- | ------- | ------------------------------ |
| `limits.maxResults`       | `number` | `6`     | Maksymalna liczba wyników wyszukiwania |
| `limits.maxSnippetChars`  | `number` | --      | Ogranicza długość fragmentu    |
| `limits.maxInjectedChars` | `number` | --      | Ogranicza łączną liczbę wstrzykniętych znaków |
| `limits.timeoutMs`        | `number` | `4000`  | Limit czasu wyszukiwania       |

### Zakres

Steruje tym, które sesje mogą otrzymywać wyniki wyszukiwania QMD. Ten sam schemat co
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

Domyślnie tylko DM. `match.keyPrefix` dopasowuje znormalizowany klucz sesji;
`match.rawKeyPrefix` dopasowuje surowy klucz, w tym `agent:<id>:`.

### Cytowania

`memory.citations` dotyczy wszystkich backendów:

| Value            | Zachowanie                                           |
| ---------------- | ---------------------------------------------------- |
| `auto` (domyślne) | Uwzględnia stopkę `Source: <path#line>` we fragmentach |
| `on`             | Zawsze uwzględnia stopkę                             |
| `off`            | Pomija stopkę (ścieżka nadal jest przekazywana agentowi wewnętrznie) |

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

## Dreaming (eksperymentalne)

Dreaming jest konfigurowane pod `plugins.entries.memory-core.config.dreaming`,
a nie pod `agents.defaults.memorySearch`.

Dreaming działa jako jedno zaplanowane przejście i wykorzystuje wewnętrzne fazy light/deep/REM jako
szczegół implementacyjny.

Aby poznać zachowanie koncepcyjne i polecenia ukośnikowe, zobacz [Dreaming](/concepts/dreaming).

### Ustawienia użytkownika

| Key         | Type      | Default     | Opis                                              |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`     | Włącza lub wyłącza dreaming całkowicie            |
| `frequency` | `string`  | `0 3 * * *` | Opcjonalna kadencja cron dla pełnego przejścia dreaming |

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

- Dreaming zapisuje stan maszyny do `memory/.dreams/`.
- Dreaming zapisuje czytelne dla człowieka dane narracyjne do `DREAMS.md` (lub istniejącego `dreams.md`).
- Polityka faz light/deep/REM i progi są zachowaniem wewnętrznym, a nie config dostępnym dla użytkownika.
