---
read_when:
    - Anda ingin mengonfigurasi provider pencarian memori atau model embedding
    - Anda ingin menyiapkan backend QMD
    - Anda ingin menyetel pencarian hibrida, MMR, atau temporal decay
    - Anda ingin mengaktifkan pengindeksan memori multimodal
summary: Semua knob konfigurasi untuk pencarian memori, provider embedding, QMD, pencarian hibrida, dan pengindeksan multimodal
title: Referensi konfigurasi memori
x-i18n:
    generated_at: "2026-04-12T23:33:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 299ca9b69eea292ea557a2841232c637f5c1daf2bc0f73c0a42f7c0d8d566ce2
    source_path: reference/memory-config.md
    workflow: 15
---

# Referensi konfigurasi memori

Halaman ini mencantumkan setiap knob konfigurasi untuk pencarian memori OpenClaw. Untuk
ikhtisar konseptual, lihat:

- [Ikhtisar Memori](/id/concepts/memory) -- cara kerja memori
- [Builtin Engine](/id/concepts/memory-builtin) -- backend SQLite default
- [QMD Engine](/id/concepts/memory-qmd) -- sidecar local-first
- [Pencarian Memori](/id/concepts/memory-search) -- pipeline pencarian dan penyetelan
- [Active Memory](/id/concepts/active-memory) -- mengaktifkan sub-agent memori untuk sesi interaktif

Semua pengaturan pencarian memori berada di bawah `agents.defaults.memorySearch` dalam
`openclaw.json` kecuali jika disebutkan lain.

Jika Anda mencari toggle fitur **Active Memory** dan config sub-agent,
itu berada di bawah `plugins.entries.active-memory`, bukan `memorySearch`.

Active Memory menggunakan model dua gerbang:

1. plugin harus diaktifkan dan menargetkan id agent saat ini
2. permintaan harus berupa sesi chat persisten interaktif yang memenuhi syarat

Lihat [Active Memory](/id/concepts/active-memory) untuk model aktivasi,
config milik plugin, persistensi transkrip, dan pola rollout yang aman.

---

## Pemilihan provider

| Key        | Tipe      | Default          | Deskripsi                                                                                 |
| ---------- | --------- | ---------------- | ----------------------------------------------------------------------------------------- |
| `provider` | `string`  | terdeteksi otomatis | ID adapter embedding: `openai`, `gemini`, `voyage`, `mistral`, `bedrock`, `ollama`, `local` |
| `model`    | `string`  | default provider | Nama model embedding                                                                      |
| `fallback` | `string`  | `"none"`         | ID adapter fallback saat yang utama gagal                                                 |
| `enabled`  | `boolean` | `true`           | Mengaktifkan atau menonaktifkan pencarian memori                                          |

### Urutan deteksi otomatis

Saat `provider` tidak ditetapkan, OpenClaw memilih yang pertama tersedia:

1. `local` -- jika `memorySearch.local.modelPath` dikonfigurasi dan file tersebut ada.
2. `openai` -- jika key OpenAI dapat di-resolve.
3. `gemini` -- jika key Gemini dapat di-resolve.
4. `voyage` -- jika key Voyage dapat di-resolve.
5. `mistral` -- jika key Mistral dapat di-resolve.
6. `bedrock` -- jika rantai kredensial AWS SDK dapat di-resolve (instance role, access key, profile, SSO, web identity, atau shared config).

`ollama` didukung tetapi tidak terdeteksi otomatis (tetapkan secara eksplisit).

### Resolusi kunci API

Embedding jarak jauh memerlukan kunci API. Bedrock menggunakan rantai kredensial default AWS SDK
sebagai gantinya (instance role, SSO, access key).

| Provider | Env var                        | Key config                         |
| -------- | ------------------------------ | ---------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`   |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`   |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`   |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey`  |
| Bedrock  | Rantai kredensial AWS          | Tidak memerlukan kunci API         |
| Ollama   | `OLLAMA_API_KEY` (placeholder) | --                                 |

Codex OAuth hanya mencakup chat/completions dan tidak memenuhi permintaan
embedding.

---

## Config endpoint jarak jauh

Untuk endpoint kustom yang kompatibel dengan OpenAI atau mengoverride default provider:

| Key              | Tipe     | Deskripsi                                        |
| ---------------- | -------- | ------------------------------------------------ |
| `remote.baseUrl` | `string` | Base URL API kustom                              |
| `remote.apiKey`  | `string` | Override kunci API                               |
| `remote.headers` | `object` | Header HTTP tambahan (digabung dengan default provider) |

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

## Config khusus Gemini

| Key                    | Tipe     | Default                | Deskripsi                                |
| ---------------------- | -------- | ---------------------- | ---------------------------------------- |
| `model`                | `string` | `gemini-embedding-001` | Juga mendukung `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Untuk Embedding 2: 768, 1536, atau 3072  |

<Warning>
Mengubah model atau `outputDimensionality` memicu reindex penuh otomatis.
</Warning>

---

## Config embedding Bedrock

Bedrock menggunakan rantai kredensial default AWS SDK -- tidak memerlukan kunci API.
Jika OpenClaw berjalan di EC2 dengan instance role yang mengaktifkan Bedrock, cukup tetapkan
provider dan model:

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

| Key                    | Tipe     | Default                        | Deskripsi                    |
| ---------------------- | -------- | ------------------------------ | ---------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | ID model embedding Bedrock apa pun |
| `outputDimensionality` | `number` | default model                  | Untuk Titan V2: 256, 512, atau 1024 |

### Model yang didukung

Model berikut didukung (dengan deteksi keluarga dan default dimensi):

| ID Model                                   | Provider   | Dims Default | Dims yang Dapat Dikonfigurasi |
| ------------------------------------------ | ---------- | ------------ | ----------------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024         | 256, 512, 1024               |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536         | --                           |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536         | --                           |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024         | --                           |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024         | 256, 384, 1024, 3072         |
| `cohere.embed-english-v3`                  | Cohere     | 1024         | --                           |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024         | --                           |
| `cohere.embed-v4:0`                        | Cohere     | 1536         | 256-1536                     |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512          | --                           |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024         | --                           |

Varian dengan sufiks throughput (misalnya, `amazon.titan-embed-text-v1:2:8k`) mewarisi
konfigurasi model dasarnya.

### Autentikasi

Autentikasi Bedrock menggunakan urutan resolusi kredensial AWS SDK standar:

1. Variabel lingkungan (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Cache token SSO
3. Kredensial token web identity
4. File shared credentials dan config
5. Kredensial metadata ECS atau EC2

Region di-resolve dari `AWS_REGION`, `AWS_DEFAULT_REGION`, `baseUrl` provider
`amazon-bedrock`, atau default ke `us-east-1`.

### Izin IAM

Role atau user IAM memerlukan:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Untuk least-privilege, batasi `InvokeModel` ke model tertentu:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Config embedding lokal

| Key                   | Tipe     | Default                | Deskripsi                    |
| --------------------- | -------- | ---------------------- | ---------------------------- |
| `local.modelPath`     | `string` | diunduh otomatis       | Path ke file model GGUF      |
| `local.modelCacheDir` | `string` | default node-llama-cpp | Direktori cache untuk model yang diunduh |

Model default: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, diunduh otomatis).
Memerlukan build native: `pnpm approve-builds` lalu `pnpm rebuild node-llama-cpp`.

---

## Config pencarian hibrida

Semua berada di bawah `memorySearch.query.hybrid`:

| Key                   | Tipe      | Default | Deskripsi                         |
| --------------------- | --------- | ------- | --------------------------------- |
| `enabled`             | `boolean` | `true`  | Aktifkan pencarian hibrida BM25 + vector |
| `vectorWeight`        | `number`  | `0.7`   | Bobot untuk skor vector (0-1)     |
| `textWeight`          | `number`  | `0.3`   | Bobot untuk skor BM25 (0-1)       |
| `candidateMultiplier` | `number`  | `4`     | Pengali ukuran kumpulan kandidat  |

### MMR (keragaman)

| Key           | Tipe      | Default | Deskripsi                            |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Aktifkan pemeringkatan ulang MMR     |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = keragaman maksimum, 1 = relevansi maksimum |

### Temporal decay (keterkinian)

| Key                          | Tipe      | Default | Deskripsi                    |
| ---------------------------- | --------- | ------- | ---------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Aktifkan peningkatan keterkinian |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | Skor menjadi setengah setiap N hari |

File evergreen (`MEMORY.md`, file tanpa tanggal di `memory/`) tidak pernah dikenai decay.

### Contoh lengkap

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

## Path memori tambahan

| Key          | Tipe       | Deskripsi                              |
| ------------ | ---------- | -------------------------------------- |
| `extraPaths` | `string[]` | Direktori atau file tambahan untuk diindeks |

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

Path dapat berupa absolut atau relatif terhadap workspace. Direktori dipindai
secara rekursif untuk file `.md`. Penanganan symlink bergantung pada backend aktif:
builtin engine mengabaikan symlink, sedangkan QMD mengikuti perilaku scanner QMD
yang mendasarinya.

Untuk pencarian transkrip lintas-agent yang dibatasi agent, gunakan
`agents.list[].memorySearch.qmd.extraCollections` alih-alih `memory.qmd.paths`.
Extra collection tersebut mengikuti bentuk `{ path, name, pattern? }` yang sama, tetapi
digabung per agent dan dapat mempertahankan nama bersama yang eksplisit saat path
menunjuk ke luar workspace saat ini.
Jika path hasil resolve yang sama muncul di `memory.qmd.paths` dan
`memorySearch.qmd.extraCollections`, QMD mempertahankan entri pertama dan melewati
duplikatnya.

---

## Memori multimodal (Gemini)

Indeks gambar dan audio bersama Markdown menggunakan Gemini Embedding 2:

| Key                       | Tipe       | Default    | Deskripsi                                |
| ------------------------- | ---------- | ---------- | ---------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Aktifkan pengindeksan multimodal         |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]`, atau `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Ukuran file maksimum untuk pengindeksan  |

Hanya berlaku untuk file di `extraPaths`. Root memori default tetap hanya Markdown.
Memerlukan `gemini-embedding-2-preview`. `fallback` harus `"none"`.

Format yang didukung: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(gambar); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (audio).

---

## Cache embedding

| Key                | Tipe      | Default | Deskripsi                           |
| ------------------ | --------- | ------- | ----------------------------------- |
| `cache.enabled`    | `boolean` | `false` | Cache embedding chunk di SQLite     |
| `cache.maxEntries` | `number`  | `50000` | Jumlah maksimum embedding yang di-cache |

Mencegah embedding ulang teks yang tidak berubah selama reindex atau pembaruan transkrip.

---

## Pengindeksan batch

| Key                           | Tipe      | Default | Deskripsi                     |
| ----------------------------- | --------- | ------- | ----------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | Aktifkan API embedding batch  |
| `remote.batch.concurrency`    | `number`  | `2`     | Job batch paralel             |
| `remote.batch.wait`           | `boolean` | `true`  | Tunggu batch selesai          |
| `remote.batch.pollIntervalMs` | `number`  | --      | Interval polling              |
| `remote.batch.timeoutMinutes` | `number`  | --      | Timeout batch                 |

Tersedia untuk `openai`, `gemini`, dan `voyage`. Batch OpenAI biasanya
paling cepat dan paling murah untuk backfill besar.

---

## Pencarian memori sesi (eksperimental)

Indeks transkrip sesi dan tampilkan melalui `memory_search`:

| Key                           | Tipe       | Default      | Deskripsi                                |
| ----------------------------- | ---------- | ------------ | ---------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | Aktifkan pengindeksan sesi               |
| `sources`                     | `string[]` | `["memory"]` | Tambahkan `"sessions"` untuk menyertakan transkrip |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | Ambang byte untuk reindex                |
| `sync.sessions.deltaMessages` | `number`   | `50`         | Ambang jumlah pesan untuk reindex        |

Pengindeksan sesi bersifat opt-in dan berjalan secara asinkron. Hasil dapat sedikit
stale. Log sesi berada di disk, jadi perlakukan akses filesystem sebagai batas
kepercayaan.

---

## Akselerasi vector SQLite (`sqlite-vec`)

| Key                          | Tipe      | Default | Deskripsi                          |
| ---------------------------- | --------- | ------- | ---------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | Gunakan `sqlite-vec` untuk query vector |
| `store.vector.extensionPath` | `string`  | bundled | Override path `sqlite-vec`         |

Saat `sqlite-vec` tidak tersedia, OpenClaw otomatis kembali ke cosine
similarity dalam proses.

---

## Penyimpanan indeks

| Key                   | Tipe     | Default                               | Deskripsi                                   |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Lokasi indeks (mendukung token `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                           | Tokenizer FTS5 (`unicode61` atau `trigram`) |

---

## Config backend QMD

Tetapkan `memory.backend = "qmd"` untuk mengaktifkan. Semua pengaturan QMD berada di bawah
`memory.qmd`:

| Key                      | Tipe      | Default  | Deskripsi                                   |
| ------------------------ | --------- | -------- | ------------------------------------------- |
| `command`                | `string`  | `qmd`    | Path executable QMD                         |
| `searchMode`             | `string`  | `search` | Perintah pencarian: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | Otomatis mengindeks `MEMORY.md` + `memory/**/*.md` |
| `paths[]`                | `array`   | --       | Path tambahan: `{ name, path, pattern? }`   |
| `sessions.enabled`       | `boolean` | `false`  | Indeks transkrip sesi                       |
| `sessions.retentionDays` | `number`  | --       | Retensi transkrip                           |
| `sessions.exportDir`     | `string`  | --       | Direktori ekspor                            |

OpenClaw lebih memilih bentuk collection dan query MCP QMD saat ini, tetapi tetap
membuat rilis QMD lama berfungsi dengan kembali ke flag collection `--mask` lama
dan nama tool MCP lama bila diperlukan.

Override model QMD tetap berada di sisi QMD, bukan config OpenClaw. Jika Anda perlu
mengoverride model QMD secara global, tetapkan variabel lingkungan seperti
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL`, dan `QMD_GENERATE_MODEL` di lingkungan runtime gateway.

### Jadwal pembaruan

| Key                       | Tipe      | Default | Deskripsi                              |
| ------------------------- | --------- | ------- | -------------------------------------- |
| `update.interval`         | `string`  | `5m`    | Interval refresh                       |
| `update.debounceMs`       | `number`  | `15000` | Debounce perubahan file                |
| `update.onBoot`           | `boolean` | `true`  | Refresh saat startup                   |
| `update.waitForBootSync`  | `boolean` | `false` | Blok startup sampai refresh selesai    |
| `update.embedInterval`    | `string`  | --      | Cadence embedding terpisah             |
| `update.commandTimeoutMs` | `number`  | --      | Timeout untuk perintah QMD             |
| `update.updateTimeoutMs`  | `number`  | --      | Timeout untuk operasi update QMD       |
| `update.embedTimeoutMs`   | `number`  | --      | Timeout untuk operasi embed QMD        |

### Batas

| Key                       | Tipe     | Default | Deskripsi                     |
| ------------------------- | -------- | ------- | ----------------------------- |
| `limits.maxResults`       | `number` | `6`     | Jumlah maksimum hasil pencarian |
| `limits.maxSnippetChars`  | `number` | --      | Batasi panjang snippet        |
| `limits.maxInjectedChars` | `number` | --      | Batasi total karakter yang diinjeksi |
| `limits.timeoutMs`        | `number` | `4000`  | Timeout pencarian             |

### Cakupan

Mengontrol sesi mana yang dapat menerima hasil pencarian QMD. Skemanya sama dengan
[`session.sendPolicy`](/id/gateway/configuration-reference#session):

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

Default bawaan mengizinkan sesi direct dan channel, sambil tetap menolak
grup.

Default-nya hanya DM. `match.keyPrefix` mencocokkan key sesi yang dinormalisasi;
`match.rawKeyPrefix` mencocokkan key mentah termasuk `agent:<id>:`.

### Sitasi

`memory.citations` berlaku untuk semua backend:

| Value            | Perilaku                                             |
| ---------------- | ---------------------------------------------------- |
| `auto` (default) | Sertakan footer `Source: <path#line>` di snippet     |
| `on`             | Selalu sertakan footer                               |
| `off`            | Hilangkan footer (path tetap diteruskan ke agent secara internal) |

### Contoh QMD lengkap

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

## Dreaming (eksperimental)

Dreaming dikonfigurasi di bawah `plugins.entries.memory-core.config.dreaming`,
bukan di bawah `agents.defaults.memorySearch`.

Dreaming berjalan sebagai satu sapuan terjadwal dan menggunakan fase internal light/deep/REM sebagai
detail implementasi.

Untuk perilaku konseptual dan slash command, lihat [Dreaming](/id/concepts/dreaming).

### Pengaturan pengguna

| Key         | Tipe      | Default     | Deskripsi                                        |
| ----------- | --------- | ----------- | ------------------------------------------------ |
| `enabled`   | `boolean` | `false`     | Aktifkan atau nonaktifkan Dreaming sepenuhnya    |
| `frequency` | `string`  | `0 3 * * *` | Cadence Cron opsional untuk sapuan Dreaming penuh |

### Contoh

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

Catatan:

- Dreaming menulis status mesin ke `memory/.dreams/`.
- Dreaming menulis output naratif yang dapat dibaca manusia ke `DREAMS.md` (atau `dreams.md` yang sudah ada).
- Kebijakan fase light/deep/REM dan ambangnya adalah perilaku internal, bukan config yang menghadap pengguna.
