---
read_when:
    - Sie möchten Anbieter für die Speicher-Suche oder Einbettungsmodelle konfigurieren
    - Sie möchten das QMD-Backend einrichten
    - Sie möchten die hybride Suche, MMR oder den zeitlichen Zerfall optimieren
    - Sie möchten die multimodale Speicherindizierung aktivieren
summary: Alle Konfigurationsoptionen für Speicher-Suche, Einbettungsanbieter, QMD, hybride Suche und multimodale Indizierung
title: Referenz zur Speicherkonfiguration
x-i18n:
    generated_at: "2026-04-15T14:41:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# Referenz zur Speicherkonfiguration

Diese Seite listet alle Konfigurationsoptionen für die OpenClaw-Speicher-Suche auf. Für
konzeptionelle Übersichten siehe:

- [Speicherübersicht](/de/concepts/memory) -- wie Speicher funktioniert
- [Integrierte Engine](/de/concepts/memory-builtin) -- Standard-SQLite-Backend
- [QMD-Engine](/de/concepts/memory-qmd) -- lokaler Sidecar mit Local-First-Ansatz
- [Speicher-Suche](/de/concepts/memory-search) -- Suchpipeline und Optimierung
- [Active Memory](/de/concepts/active-memory) -- Aktivieren des Speicher-Sub-Agenten für interaktive Sitzungen

Alle Einstellungen für die Speicher-Suche befinden sich unter `agents.defaults.memorySearch` in
`openclaw.json`, sofern nicht anders angegeben.

Wenn Sie nach dem **Active Memory**-Funktionsschalter und der Sub-Agent-Konfiguration suchen,
befinden sich diese unter `plugins.entries.active-memory` statt unter `memorySearch`.

Active Memory verwendet ein Modell mit zwei Voraussetzungen:

1. das Plugin muss aktiviert sein und auf die aktuelle Agent-ID zielen
2. die Anfrage muss eine geeignete interaktive persistente Chat-Sitzung sein

Siehe [Active Memory](/de/concepts/active-memory) für das Aktivierungsmodell,
die Plugin-eigene Konfiguration, die Transkriptpersistenz und ein sicheres Einführungsmodell.

---

## Anbieterauswahl

| Schlüssel  | Typ       | Standard         | Beschreibung                                                                                                  |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | automatisch erkannt | Einbettungsadapter-ID: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | Anbieterstandard | Name des Einbettungsmodells                                                                                   |
| `fallback` | `string`  | `"none"`         | Fallback-Adapter-ID, wenn der primäre Adapter fehlschlägt                                                     |
| `enabled`  | `boolean` | `true`           | Aktiviert oder deaktiviert die Speicher-Suche                                                                 |

### Reihenfolge der automatischen Erkennung

Wenn `provider` nicht gesetzt ist, wählt OpenClaw den ersten verfügbaren Anbieter:

1. `local` -- wenn `memorySearch.local.modelPath` konfiguriert ist und die Datei existiert.
2. `github-copilot` -- wenn ein GitHub-Copilot-Token aufgelöst werden kann (Umgebungsvariable oder Auth-Profil).
3. `openai` -- wenn ein OpenAI-Schlüssel aufgelöst werden kann.
4. `gemini` -- wenn ein Gemini-Schlüssel aufgelöst werden kann.
5. `voyage` -- wenn ein Voyage-Schlüssel aufgelöst werden kann.
6. `mistral` -- wenn ein Mistral-Schlüssel aufgelöst werden kann.
7. `bedrock` -- wenn die AWS-SDK-Anmeldedatenkette aufgelöst wird (Instanzrolle, Zugriffsschlüssel, Profil, SSO, Web-Identität oder freigegebene Konfiguration).

`ollama` wird unterstützt, aber nicht automatisch erkannt (setzen Sie es explizit).

### Auflösung von API-Schlüsseln

Remote-Einbettungen erfordern einen API-Schlüssel. Bedrock verwendet stattdessen die
Standard-Anmeldedatenkette des AWS SDK (Instanzrollen, SSO, Zugriffsschlüssel).

| Anbieter       | Umgebungsvariable                                 | Konfigurationsschlüssel           |
| -------------- | ------------------------------------------------- | --------------------------------- |
| Bedrock        | AWS-Anmeldedatenkette                             | Kein API-Schlüssel erforderlich   |
| Gemini         | `GEMINI_API_KEY`                                  | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Auth-Profil über Geräteanmeldung  |
| Mistral        | `MISTRAL_API_KEY`                                 | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (Platzhalter)                    | --                                |
| OpenAI         | `OPENAI_API_KEY`                                  | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                  | `models.providers.voyage.apiKey`  |

Codex OAuth deckt nur Chat/Completions ab und erfüllt keine Einbettungs-
anfragen.

---

## Remote-Endpunktkonfiguration

Für benutzerdefinierte OpenAI-kompatible Endpunkte oder zum Überschreiben von Anbieterstandards:

| Schlüssel         | Typ      | Beschreibung                                      |
| ----------------- | -------- | ------------------------------------------------- |
| `remote.baseUrl`  | `string` | Benutzerdefinierte API-Basis-URL                  |
| `remote.apiKey`   | `string` | API-Schlüssel überschreiben                       |
| `remote.headers`  | `object` | Zusätzliche HTTP-Header (mit Anbieterstandards zusammengeführt) |

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

## Gemini-spezifische Konfiguration

| Schlüssel               | Typ      | Standard               | Beschreibung                                |
| ----------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                 | `string` | `gemini-embedding-001` | Unterstützt auch `gemini-embedding-2-preview` |
| `outputDimensionality`  | `number` | `3072`                 | Für Embedding 2: 768, 1536 oder 3072       |

<Warning>
Das Ändern von Modell oder `outputDimensionality` löst automatisch eine vollständige Neuindizierung aus.
</Warning>

---

## Bedrock-Einbettungskonfiguration

Bedrock verwendet die Standard-Anmeldedatenkette des AWS SDK -- keine API-Schlüssel erforderlich.
Wenn OpenClaw auf EC2 mit einer Bedrock-aktivierten Instanzrolle ausgeführt wird, setzen Sie einfach
Anbieter und Modell:

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

| Schlüssel               | Typ      | Standard                       | Beschreibung                    |
| ----------------------- | -------- | ------------------------------ | ------------------------------- |
| `model`                 | `string` | `amazon.titan-embed-text-v2:0` | Beliebige Bedrock-Einbettungsmodell-ID |
| `outputDimensionality`  | `number` | Modellstandard                 | Für Titan V2: 256, 512 oder 1024 |

### Unterstützte Modelle

Die folgenden Modelle werden unterstützt (mit Familienerkennung und Standarddimensionen):

| Modell-ID                                  | Anbieter   | Standard-Dims | Konfigurierbare Dims |
| ------------------------------------------ | ---------- | ------------- | -------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024          | 256, 512, 1024       |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536          | --                   |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536          | --                   |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024          | --                   |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024          | 256, 384, 1024, 3072 |
| `cohere.embed-english-v3`                  | Cohere     | 1024          | --                   |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024          | --                   |
| `cohere.embed-v4:0`                        | Cohere     | 1536          | 256-1536             |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512           | --                   |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024          | --                   |

Varianten mit Durchsatzsuffix (z. B. `amazon.titan-embed-text-v1:2:8k`) übernehmen
die Konfiguration des Basismodells.

### Authentifizierung

Die Bedrock-Authentifizierung verwendet die Standardreihenfolge zur Auflösung von AWS-SDK-Anmeldedaten:

1. Umgebungsvariablen (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. SSO-Token-Cache
3. Anmeldedaten für Web-Identitätstoken
4. Freigegebene Anmeldedaten- und Konfigurationsdateien
5. ECS- oder EC2-Metadaten-Anmeldedaten

Die Region wird aus `AWS_REGION`, `AWS_DEFAULT_REGION`, der `baseUrl` des
Anbieters `amazon-bedrock` aufgelöst oder standardmäßig auf `us-east-1` gesetzt.

### IAM-Berechtigungen

Die IAM-Rolle oder der IAM-Benutzer benötigt:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Für Least-Privilege beschränken Sie `InvokeModel` auf das jeweilige Modell:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Lokale Einbettungskonfiguration

| Schlüssel              | Typ      | Standard               | Beschreibung                    |
| ---------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`      | `string` | automatisch heruntergeladen | Pfad zur GGUF-Modelldatei   |
| `local.modelCacheDir`  | `string` | node-llama-cpp-Standard | Cache-Verzeichnis für heruntergeladene Modelle |

Standardmodell: `embeddinggemma-300m-qat-Q8_0.gguf` (~0,6 GB, wird automatisch heruntergeladen).
Erfordert nativen Build: `pnpm approve-builds` und dann `pnpm rebuild node-llama-cpp`.

---

## Konfiguration der hybriden Suche

Alles unter `memorySearch.query.hybrid`:

| Schlüssel              | Typ       | Standard | Beschreibung                       |
| ---------------------- | --------- | -------- | ---------------------------------- |
| `enabled`              | `boolean` | `true`   | Hybride BM25- und Vektorsuche aktivieren |
| `vectorWeight`         | `number`  | `0.7`    | Gewichtung für Vektorscores (0-1)  |
| `textWeight`           | `number`  | `0.3`    | Gewichtung für BM25-Scores (0-1)   |
| `candidateMultiplier`  | `number`  | `4`      | Multiplikator für die Größe des Kandidatenpools |

### MMR (Diversität)

| Schlüssel      | Typ       | Standard | Beschreibung                            |
| -------------- | --------- | -------- | --------------------------------------- |
| `mmr.enabled`  | `boolean` | `false`  | MMR-Neu-Ranking aktivieren              |
| `mmr.lambda`   | `number`  | `0.7`    | 0 = maximale Diversität, 1 = maximale Relevanz |

### Zeitlicher Zerfall (Aktualität)

| Schlüssel                     | Typ       | Standard | Beschreibung                    |
| ----------------------------- | --------- | -------- | ------------------------------- |
| `temporalDecay.enabled`       | `boolean` | `false`  | Aktualitäts-Boost aktivieren    |
| `temporalDecay.halfLifeDays`  | `number`  | `30`     | Score halbiert sich alle N Tage |

Evergreen-Dateien (`MEMORY.md`, nicht datierte Dateien in `memory/`) unterliegen nie einem Zerfall.

### Vollständiges Beispiel

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

## Zusätzliche Speicherpfade

| Schlüssel   | Typ        | Beschreibung                              |
| ----------- | ---------- | ----------------------------------------- |
| `extraPaths`| `string[]` | Zusätzliche Verzeichnisse oder Dateien zur Indizierung |

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

Pfade können absolut oder relativ zum Workspace sein. Verzeichnisse werden
rekursiv nach `.md`-Dateien durchsucht. Die Behandlung symbolischer Links hängt
vom aktiven Backend ab: Die integrierte Engine ignoriert symbolische Links, während QMD
dem Verhalten des zugrunde liegenden QMD-Scanners folgt.

Für agentenbezogene agentenübergreifende Transkriptsuche verwenden Sie
`agents.list[].memorySearch.qmd.extraCollections` statt `memory.qmd.paths`.
Diese zusätzlichen Collections verwenden dieselbe Form `{ path, name, pattern? }`, werden jedoch
pro Agent zusammengeführt und können explizite gemeinsame Namen beibehalten, wenn der Pfad
außerhalb des aktuellen Workspace liegt.
Wenn derselbe aufgelöste Pfad sowohl in `memory.qmd.paths` als auch in
`memorySearch.qmd.extraCollections` erscheint, behält QMD den ersten Eintrag bei und überspringt
das Duplikat.

---

## Multimodaler Speicher (Gemini)

Indizieren Sie Bilder und Audio zusammen mit Markdown mit Gemini Embedding 2:

| Schlüssel                  | Typ        | Standard   | Beschreibung                          |
| -------------------------- | ---------- | ---------- | ------------------------------------- |
| `multimodal.enabled`       | `boolean`  | `false`    | Multimodale Indizierung aktivieren    |
| `multimodal.modalities`    | `string[]` | --         | `["image"]`, `["audio"]` oder `["all"]` |
| `multimodal.maxFileBytes`  | `number`   | `10000000` | Maximale Dateigröße für die Indizierung |

Gilt nur für Dateien in `extraPaths`. Standard-Speicherwurzeln bleiben auf Markdown beschränkt.
Erfordert `gemini-embedding-2-preview`. `fallback` muss `"none"` sein.

Unterstützte Formate: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(Bilder); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (Audio).

---

## Einbettungs-Cache

| Schlüssel           | Typ       | Standard | Beschreibung                         |
| ------------------- | --------- | -------- | ------------------------------------ |
| `cache.enabled`     | `boolean` | `false`  | Chunk-Einbettungen in SQLite cachen  |
| `cache.maxEntries`  | `number`  | `50000`  | Maximale Anzahl zwischengespeicherter Einbettungen |

Verhindert die erneute Einbettung unveränderten Texts bei Neuindizierung oder Transkriptaktualisierungen.

---

## Batch-Indizierung

| Schlüssel                      | Typ       | Standard | Beschreibung                |
| ------------------------------ | --------- | -------- | --------------------------- |
| `remote.batch.enabled`         | `boolean` | `false`  | Batch-Einbettungs-API aktivieren |
| `remote.batch.concurrency`     | `number`  | `2`      | Parallele Batch-Jobs        |
| `remote.batch.wait`            | `boolean` | `true`   | Auf Batch-Abschluss warten  |
| `remote.batch.pollIntervalMs`  | `number`  | --       | Abfrageintervall            |
| `remote.batch.timeoutMinutes`  | `number`  | --       | Batch-Timeout               |

Verfügbar für `openai`, `gemini` und `voyage`. OpenAI-Batches sind für große Backfills in der Regel
am schnellsten und kostengünstigsten.

---

## Sitzungs-Speicher-Suche (experimentell)

Indiziert Sitzungsprotokolle und stellt sie über `memory_search` bereit:

| Schlüssel                    | Typ        | Standard     | Beschreibung                              |
| ---------------------------- | ---------- | ------------ | ----------------------------------------- |
| `experimental.sessionMemory` | `boolean`  | `false`      | Sitzungsindizierung aktivieren            |
| `sources`                    | `string[]` | `["memory"]` | `"sessions"` hinzufügen, um Transkripte einzuschließen |
| `sync.sessions.deltaBytes`   | `number`   | `100000`     | Byte-Schwellenwert für Neuindizierung     |
| `sync.sessions.deltaMessages`| `number`   | `50`         | Nachrichten-Schwellenwert für Neuindizierung |

Die Sitzungsindizierung ist optional und läuft asynchron. Ergebnisse können leicht
veraltet sein. Sitzungsprotokolle werden auf der Festplatte gespeichert, daher sollte der Dateisystemzugriff als Vertrauensgrenze
behandelt werden.

---

## SQLite-Vektorbeschleunigung (sqlite-vec)

| Schlüssel                     | Typ       | Standard | Beschreibung                        |
| ----------------------------- | --------- | -------- | ----------------------------------- |
| `store.vector.enabled`        | `boolean` | `true`   | sqlite-vec für Vektorabfragen verwenden |
| `store.vector.extensionPath`  | `string`  | gebündelt | sqlite-vec-Pfad überschreiben      |

Wenn sqlite-vec nicht verfügbar ist, fällt OpenClaw automatisch auf Cosinus-
ähnlichkeit im Prozess zurück.

---

## Indexspeicher

| Schlüssel            | Typ      | Standard                              | Beschreibung                                  |
| -------------------- | -------- | ------------------------------------- | --------------------------------------------- |
| `store.path`         | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Speicherort des Indexes (unterstützt Token `{agentId}`) |
| `store.fts.tokenizer`| `string` | `unicode61`                           | FTS5-Tokenizer (`unicode61` oder `trigram`)   |

---

## Konfiguration des QMD-Backends

Setzen Sie `memory.backend = "qmd"`, um es zu aktivieren. Alle QMD-Einstellungen befinden sich unter
`memory.qmd`:

| Schlüssel               | Typ       | Standard | Beschreibung                                 |
| ----------------------- | --------- | -------- | -------------------------------------------- |
| `command`               | `string`  | `qmd`    | Pfad zur QMD-Executable                      |
| `searchMode`            | `string`  | `search` | Suchbefehl: `search`, `vsearch`, `query`     |
| `includeDefaultMemory`  | `boolean` | `true`   | `MEMORY.md` + `memory/**/*.md` automatisch indizieren |
| `paths[]`               | `array`   | --       | Zusätzliche Pfade: `{ name, path, pattern? }` |
| `sessions.enabled`      | `boolean` | `false`  | Sitzungsprotokolle indizieren                |
| `sessions.retentionDays`| `number`  | --       | Aufbewahrung von Transkripten                |
| `sessions.exportDir`    | `string`  | --       | Exportverzeichnis                            |

OpenClaw bevorzugt die aktuellen Formen für QMD-Collections und MCP-Abfragen, hält jedoch
ältere QMD-Versionen funktionsfähig, indem bei Bedarf auf Legacy-Collection-Flags `--mask`
und ältere MCP-Toolnamen zurückgegriffen wird.

QMD-Modellüberschreibungen bleiben auf der QMD-Seite, nicht in der OpenClaw-Konfiguration. Wenn Sie
QMD-Modelle global überschreiben müssen, setzen Sie Umgebungsvariablen wie
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL` und `QMD_GENERATE_MODEL` in der Gateway-
Laufzeitumgebung.

### Aktualisierungsplan

| Schlüssel                  | Typ       | Standard | Beschreibung                               |
| -------------------------- | --------- | -------- | ------------------------------------------ |
| `update.interval`          | `string`  | `5m`     | Aktualisierungsintervall                   |
| `update.debounceMs`        | `number`  | `15000`  | Entprellung für Dateiänderungen            |
| `update.onBoot`            | `boolean` | `true`   | Beim Start aktualisieren                   |
| `update.waitForBootSync`   | `boolean` | `false`  | Start blockieren, bis Aktualisierung abgeschlossen ist |
| `update.embedInterval`     | `string`  | --       | Separater Einbettungstakt                  |
| `update.commandTimeoutMs`  | `number`  | --       | Timeout für QMD-Befehle                    |
| `update.updateTimeoutMs`   | `number`  | --       | Timeout für QMD-Aktualisierungsvorgänge    |
| `update.embedTimeoutMs`    | `number`  | --       | Timeout für QMD-Einbettungsvorgänge        |

### Grenzen

| Schlüssel                  | Typ      | Standard | Beschreibung                      |
| -------------------------- | -------- | -------- | --------------------------------- |
| `limits.maxResults`        | `number` | `6`      | Maximale Suchergebnisse           |
| `limits.maxSnippetChars`   | `number` | --       | Snippet-Länge begrenzen           |
| `limits.maxInjectedChars`  | `number` | --       | Gesamte eingefügte Zeichen begrenzen |
| `limits.timeoutMs`         | `number` | `4000`   | Such-Timeout                      |

### Geltungsbereich

Steuert, welche Sitzungen QMD-Suchergebnisse empfangen können. Gleiches Schema wie
[`session.sendPolicy`](/de/gateway/configuration-reference#session):

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

Der mitgelieferte Standard erlaubt Direkt- und Kanalsitzungen, verweigert aber weiterhin
Gruppen.

Standard ist nur DM. `match.keyPrefix` gleicht den normalisierten Sitzungsschlüssel ab;
`match.rawKeyPrefix` gleicht den rohen Schlüssel einschließlich `agent:<id>:` ab.

### Quellenangaben

`memory.citations` gilt für alle Backends:

| Wert             | Verhalten                                           |
| ---------------- | --------------------------------------------------- |
| `auto` (Standard)| Fußzeile `Source: <path#line>` in Snippets einfügen |
| `on`             | Fußzeile immer einfügen                             |
| `off`            | Fußzeile weglassen (Pfad wird intern weiterhin an den Agenten übergeben) |

### Vollständiges QMD-Beispiel

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

Dreaming wird unter `plugins.entries.memory-core.config.dreaming` konfiguriert,
nicht unter `agents.defaults.memorySearch`.

Dreaming läuft als ein geplanter Durchlauf und verwendet interne Light-/Deep-/REM-Phasen als
Implementierungsdetail.

Zum konzeptionellen Verhalten und zu Slash-Befehlen siehe [Dreaming](/de/concepts/dreaming).

### Benutzereinstellungen

| Schlüssel    | Typ       | Standard    | Beschreibung                                      |
| ------------ | --------- | ----------- | ------------------------------------------------- |
| `enabled`    | `boolean` | `false`     | Dreaming vollständig aktivieren oder deaktivieren |
| `frequency`  | `string`  | `0 3 * * *` | Optionaler Cron-Takt für den vollständigen Dreaming-Durchlauf |

### Beispiel

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

Hinweise:

- Dreaming schreibt Maschinenzustand nach `memory/.dreams/`.
- Dreaming schreibt menschenlesbare narrative Ausgabe nach `DREAMS.md` (oder in vorhandene `dreams.md`).
- Die Richtlinie und Schwellenwerte für Light-/Deep-/REM-Phasen sind internes Verhalten, keine benutzerseitige Konfiguration.
