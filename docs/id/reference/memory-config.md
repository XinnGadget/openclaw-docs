---
read_when:
    - Anda ingin mengonfigurasi penyedia pencarian memori atau model embedding
    - Anda ingin menyiapkan backend QMD
    - Anda ingin menyesuaikan pencarian hibrida, MMR, atau peluruhan temporal
    - Anda ingin mengaktifkan pengindeksan memori multimodal
summary: Semua opsi konfigurasi untuk pencarian memori, penyedia embedding, QMD, pencarian hibrida, dan pengindeksan multimodal
title: Referensi konfigurasi memori
x-i18n:
    generated_at: "2026-04-15T14:41:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 334c3c4dac08e864487047d3822c75f96e9e7a97c38be4b4e0cd9e63c4489a53
    source_path: reference/memory-config.md
    workflow: 15
---

# Referensi konfigurasi memori

Halaman ini mencantumkan setiap opsi konfigurasi untuk pencarian memori OpenClaw. Untuk gambaran konseptual, lihat:

- [Ikhtisar Memori](/id/concepts/memory) -- cara kerja memori
- [Mesin Bawaan](/id/concepts/memory-builtin) -- backend SQLite default
- [Mesin QMD](/id/concepts/memory-qmd) -- sidecar yang mengutamakan lokal
- [Pencarian Memori](/id/concepts/memory-search) -- pipeline pencarian dan penyesuaian
- [Active Memory](/id/concepts/active-memory) -- mengaktifkan sub-agen memori untuk sesi interaktif

Semua pengaturan pencarian memori berada di bawah `agents.defaults.memorySearch` di
`openclaw.json` kecuali jika dinyatakan lain.

Jika Anda mencari tombol fitur **active memory** dan config sub-agen,
itu berada di bawah `plugins.entries.active-memory`, bukan `memorySearch`.

Active memory menggunakan model dua gerbang:

1. plugin harus diaktifkan dan menargetkan id agen saat ini
2. permintaan harus berupa sesi chat persisten interaktif yang memenuhi syarat

Lihat [Active Memory](/id/concepts/active-memory) untuk model aktivasi,
config milik plugin, persistensi transkrip, dan pola peluncuran yang aman.

---

## Pemilihan penyedia

| Key        | Type      | Default          | Description                                                                                                   |
| ---------- | --------- | ---------------- | ------------------------------------------------------------------------------------------------------------- |
| `provider` | `string`  | terdeteksi otomatis    | ID adaptor embedding: `bedrock`, `gemini`, `github-copilot`, `local`, `mistral`, `ollama`, `openai`, `voyage` |
| `model`    | `string`  | default penyedia | Nama model embedding                                                                                          |
| `fallback` | `string`  | `"none"`         | ID adaptor fallback saat yang utama gagal                                                                     |
| `enabled`  | `boolean` | `true`           | Mengaktifkan atau menonaktifkan pencarian memori                                                              |

### Urutan deteksi otomatis

Saat `provider` tidak ditetapkan, OpenClaw memilih yang pertama tersedia:

1. `local` -- jika `memorySearch.local.modelPath` dikonfigurasi dan file tersebut ada.
2. `github-copilot` -- jika token GitHub Copilot dapat di-resolve (variabel lingkungan atau profil auth).
3. `openai` -- jika kunci OpenAI dapat di-resolve.
4. `gemini` -- jika kunci Gemini dapat di-resolve.
5. `voyage` -- jika kunci Voyage dapat di-resolve.
6. `mistral` -- jika kunci Mistral dapat di-resolve.
7. `bedrock` -- jika rantai kredensial AWS SDK berhasil di-resolve (peran instance, access key, profil, SSO, identitas web, atau config bersama).

`ollama` didukung tetapi tidak dideteksi otomatis (tetapkan secara eksplisit).

### Resolusi kunci API

Embedding jarak jauh memerlukan kunci API. Bedrock menggunakan rantai kredensial default AWS SDK
sebagai gantinya (peran instance, SSO, access key).

| Provider       | Env var                                            | Config key                        |
| -------------- | -------------------------------------------------- | --------------------------------- |
| Bedrock        | rantai kredensial AWS                              | Tidak memerlukan kunci API        |
| Gemini         | `GEMINI_API_KEY`                                   | `models.providers.google.apiKey`  |
| GitHub Copilot | `COPILOT_GITHUB_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN` | Profil auth melalui login perangkat     |
| Mistral        | `MISTRAL_API_KEY`                                  | `models.providers.mistral.apiKey` |
| Ollama         | `OLLAMA_API_KEY` (placeholder)                     | --                                |
| OpenAI         | `OPENAI_API_KEY`                                   | `models.providers.openai.apiKey`  |
| Voyage         | `VOYAGE_API_KEY`                                   | `models.providers.voyage.apiKey`  |

OAuth Codex hanya mencakup chat/completions dan tidak memenuhi permintaan
embedding.

---

## Config endpoint jarak jauh

Untuk endpoint kompatibel OpenAI kustom atau menimpa default penyedia:

| Key              | Type     | Description                                        |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | URL dasar API kustom                               |
| `remote.apiKey`  | `string` | Timpa kunci API                                    |
| `remote.headers` | `object` | Header HTTP tambahan (digabungkan dengan default penyedia) |

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

| Key                    | Type     | Default                | Description                                |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | Juga mendukung `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | Untuk Embedding 2: 768, 1536, atau 3072        |

<Warning>
Mengubah model atau `outputDimensionality` memicu pengindeksan ulang penuh secara otomatis.
</Warning>

---

## Config embedding Bedrock

Bedrock menggunakan rantai kredensial default AWS SDK -- tidak memerlukan kunci API.
Jika OpenClaw berjalan di EC2 dengan peran instance yang mendukung Bedrock, cukup tetapkan
penyedia dan model:

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

| Key                    | Type     | Default                        | Description                     |
| ---------------------- | -------- | ------------------------------ | ------------------------------- |
| `model`                | `string` | `amazon.titan-embed-text-v2:0` | ID model embedding Bedrock apa pun  |
| `outputDimensionality` | `number` | default model                  | Untuk Titan V2: 256, 512, atau 1024 |

### Model yang didukung

Model berikut didukung (dengan deteksi keluarga dan default dimensi):

| Model ID                                   | Provider   | Default Dims | Configurable Dims    |
| ------------------------------------------ | ---------- | ------------ | -------------------- |
| `amazon.titan-embed-text-v2:0`             | Amazon     | 1024         | 256, 512, 1024       |
| `amazon.titan-embed-text-v1`               | Amazon     | 1536         | --                   |
| `amazon.titan-embed-g1-text-02`            | Amazon     | 1536         | --                   |
| `amazon.titan-embed-image-v1`              | Amazon     | 1024         | --                   |
| `amazon.nova-2-multimodal-embeddings-v1:0` | Amazon     | 1024         | 256, 384, 1024, 3072 |
| `cohere.embed-english-v3`                  | Cohere     | 1024         | --                   |
| `cohere.embed-multilingual-v3`             | Cohere     | 1024         | --                   |
| `cohere.embed-v4:0`                        | Cohere     | 1536         | 256-1536             |
| `twelvelabs.marengo-embed-3-0-v1:0`        | TwelveLabs | 512          | --                   |
| `twelvelabs.marengo-embed-2-7-v1:0`        | TwelveLabs | 1024         | --                   |

Varian dengan sufiks throughput (misalnya, `amazon.titan-embed-text-v1:2:8k`) mewarisi
config model dasarnya.

### Autentikasi

Auth Bedrock menggunakan urutan resolusi kredensial AWS SDK standar:

1. Variabel lingkungan (`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`)
2. Cache token SSO
3. Kredensial token identitas web
4. File kredensial dan config bersama
5. Kredensial metadata ECS atau EC2

Region di-resolve dari `AWS_REGION`, `AWS_DEFAULT_REGION`, `baseUrl` penyedia
`amazon-bedrock`, atau default ke `us-east-1`.

### Izin IAM

Peran atau pengguna IAM memerlukan:

```json
{
  "Effect": "Allow",
  "Action": "bedrock:InvokeModel",
  "Resource": "*"
}
```

Untuk hak istimewa minimum, batasi `InvokeModel` ke model tertentu:

```
arn:aws:bedrock:*::foundation-model/amazon.titan-embed-text-v2:0
```

---

## Config embedding lokal

| Key                   | Type     | Default                | Description                     |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | diunduh otomatis        | Path ke file model GGUF         |
| `local.modelCacheDir` | `string` | default node-llama-cpp | Direktori cache untuk model yang diunduh |

Model default: `embeddinggemma-300m-qat-Q8_0.gguf` (~0.6 GB, diunduh otomatis).
Memerlukan build native: `pnpm approve-builds` lalu `pnpm rebuild node-llama-cpp`.

---

## Config pencarian hibrida

Semua di bawah `memorySearch.query.hybrid`:

| Key                   | Type      | Default | Description                        |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | Aktifkan pencarian hibrida BM25 + vektor |
| `vectorWeight`        | `number`  | `0.7`   | Bobot untuk skor vektor (0-1)     |
| `textWeight`          | `number`  | `0.3`   | Bobot untuk skor BM25 (0-1)       |
| `candidateMultiplier` | `number`  | `4`     | Pengali ukuran kumpulan kandidat     |

### MMR (keberagaman)

| Key           | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | Aktifkan pemeringkatan ulang MMR                |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = keberagaman maksimum, 1 = relevansi maksimum |

### Peluruhan temporal (keterkinian)

| Key                          | Type      | Default | Description               |
| ---------------------------- | --------- | ------- | ------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | Aktifkan peningkatan skor keterkinian      |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | Skor berkurang setengah setiap N hari |

File evergreen (`MEMORY.md`, file tanpa tanggal di `memory/`) tidak pernah dikenai peluruhan.

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

| Key          | Type       | Description                              |
| ------------ | ---------- | ---------------------------------------- |
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
mesin bawaan mengabaikan symlink, sedangkan QMD mengikuti perilaku pemindai QMD
yang mendasarinya.

Untuk pencarian transkrip lintas agen dengan cakupan agen, gunakan
`agents.list[].memorySearch.qmd.extraCollections` alih-alih `memory.qmd.paths`.
Koleksi tambahan tersebut mengikuti bentuk `{ path, name, pattern? }` yang sama, tetapi
digabungkan per agen dan dapat mempertahankan nama bersama yang eksplisit saat path
mengarah ke luar workspace saat ini.
Jika path hasil resolve yang sama muncul baik di `memory.qmd.paths` maupun
`memorySearch.qmd.extraCollections`, QMD mempertahankan entri pertama dan melewati
duplikat tersebut.

---

## Memori multimodal (Gemini)

Indeks gambar dan audio bersama Markdown menggunakan Gemini Embedding 2:

| Key                       | Type       | Default    | Description                            |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | Aktifkan pengindeksan multimodal       |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]`, atau `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | Ukuran file maksimum untuk pengindeksan |

Hanya berlaku untuk file di `extraPaths`. Root memori default tetap khusus Markdown.
Memerlukan `gemini-embedding-2-preview`. `fallback` harus `"none"`.

Format yang didukung: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(gambar); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (audio).

---

## Cache embedding

| Key                | Type      | Default | Description                      |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | Cache embedding chunk di SQLite  |
| `cache.maxEntries` | `number`  | `50000` | Embedding yang di-cache maksimum |

Mencegah embedding ulang pada teks yang tidak berubah selama pengindeksan ulang atau pembaruan transkrip.

---

## Pengindeksan batch

| Key                           | Type      | Default | Description                |
| ----------------------------- | --------- | ------- | -------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | Aktifkan API embedding batch |
| `remote.batch.concurrency`    | `number`  | `2`     | Job batch paralel          |
| `remote.batch.wait`           | `boolean` | `true`  | Tunggu penyelesaian batch  |
| `remote.batch.pollIntervalMs` | `number`  | --      | Interval polling           |
| `remote.batch.timeoutMinutes` | `number`  | --      | Batas waktu batch          |

Tersedia untuk `openai`, `gemini`, dan `voyage`. Batch OpenAI biasanya
paling cepat dan paling murah untuk backfill besar.

---

## Pencarian memori sesi (eksperimental)

Indeks transkrip sesi dan tampilkan melalui `memory_search`:

| Key                           | Type       | Default      | Description                             |
| ----------------------------- | ---------- | ------------ | --------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | Aktifkan pengindeksan sesi              |
| `sources`                     | `string[]` | `["memory"]` | Tambahkan `"sessions"` untuk menyertakan transkrip |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | Ambang byte untuk pengindeksan ulang    |
| `sync.sessions.deltaMessages` | `number`   | `50`         | Ambang pesan untuk pengindeksan ulang   |

Pengindeksan sesi bersifat opt-in dan berjalan secara asinkron. Hasilnya bisa sedikit
tidak mutakhir. Log sesi berada di disk, jadi perlakukan akses filesystem sebagai batas
kepercayaan.

---

## Akselerasi vektor SQLite (sqlite-vec)

| Key                          | Type      | Default | Description                       |
| ---------------------------- | --------- | ------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | Gunakan sqlite-vec untuk kueri vektor |
| `store.vector.extensionPath` | `string`  | bundled | Timpa path sqlite-vec             |

Saat sqlite-vec tidak tersedia, OpenClaw secara otomatis beralih ke
similaritas cosine dalam proses.

---

## Penyimpanan indeks

| Key                   | Type     | Default                               | Description                                 |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | Lokasi indeks (mendukung token `{agentId}`) |
| `store.fts.tokenizer` | `string` | `unicode61`                           | Tokenizer FTS5 (`unicode61` atau `trigram`) |

---

## Config backend QMD

Tetapkan `memory.backend = "qmd"` untuk mengaktifkannya. Semua pengaturan QMD berada di bawah
`memory.qmd`:

| Key                      | Type      | Default  | Description                                  |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | Path executable QMD                          |
| `searchMode`             | `string`  | `search` | Perintah pencarian: `search`, `vsearch`, `query` |
| `includeDefaultMemory`   | `boolean` | `true`   | Indeks otomatis `MEMORY.md` + `memory/**/*.md`    |
| `paths[]`                | `array`   | --       | Path tambahan: `{ name, path, pattern? }`      |
| `sessions.enabled`       | `boolean` | `false`  | Indeks transkrip sesi                    |
| `sessions.retentionDays` | `number`  | --       | Retensi transkrip                         |
| `sessions.exportDir`     | `string`  | --       | Direktori ekspor                             |

OpenClaw mengutamakan koleksi QMD saat ini dan bentuk kueri MCP, tetapi tetap
membuat rilis QMD yang lebih lama tetap berfungsi dengan beralih ke flag koleksi
`--mask` lama dan nama tool MCP yang lebih lama bila diperlukan.

Penggantian model QMD tetap berada di sisi QMD, bukan config OpenClaw. Jika Anda perlu
menimpa model QMD secara global, tetapkan variabel lingkungan seperti
`QMD_EMBED_MODEL`, `QMD_RERANK_MODEL`, dan `QMD_GENERATE_MODEL` di lingkungan runtime
Gateway.

### Jadwal pembaruan

| Key                       | Type      | Default | Description                           |
| ------------------------- | --------- | ------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`    | Interval penyegaran                   |
| `update.debounceMs`       | `number`  | `15000` | Debounce perubahan file               |
| `update.onBoot`           | `boolean` | `true`  | Segarkan saat startup                 |
| `update.waitForBootSync`  | `boolean` | `false` | Blokir startup sampai penyegaran selesai |
| `update.embedInterval`    | `string`  | --      | Irama embedding terpisah              |
| `update.commandTimeoutMs` | `number`  | --      | Batas waktu untuk perintah QMD        |
| `update.updateTimeoutMs`  | `number`  | --      | Batas waktu untuk operasi pembaruan QMD     |
| `update.embedTimeoutMs`   | `number`  | --      | Batas waktu untuk operasi embedding QMD      |

### Batas

| Key                       | Type     | Default | Description                |
| ------------------------- | -------- | ------- | -------------------------- |
| `limits.maxResults`       | `number` | `6`     | Hasil pencarian maksimum   |
| `limits.maxSnippetChars`  | `number` | --      | Batasi panjang cuplikan    |
| `limits.maxInjectedChars` | `number` | --      | Batasi total karakter yang disuntikkan |
| `limits.timeoutMs`        | `number` | `4000`  | Batas waktu pencarian      |

### Cakupan

Mengontrol sesi mana yang dapat menerima hasil pencarian QMD. Skema yang sama seperti
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

Default adalah khusus DM. `match.keyPrefix` cocok dengan kunci sesi yang dinormalisasi;
`match.rawKeyPrefix` cocok dengan kunci mentah termasuk `agent:<id>:`.

### Sitasi

`memory.citations` berlaku untuk semua backend:

| Value            | Behavior                                            |
| ---------------- | --------------------------------------------------- |
| `auto` (default) | Sertakan footer `Source: <path#line>` dalam cuplikan    |
| `on`             | Selalu sertakan footer                               |
| `off`            | Hilangkan footer (path tetap diteruskan ke agen secara internal) |

### Contoh lengkap QMD

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

Dreaming dikonfigurasi di bawah `plugins.entries.memory-core.config.dreaming`,
bukan di bawah `agents.defaults.memorySearch`.

Dreaming berjalan sebagai satu sapuan terjadwal dan menggunakan fase internal light/deep/REM sebagai
detail implementasi.

Untuk perilaku konseptual dan slash command, lihat [Dreaming](/id/concepts/dreaming).

### Pengaturan pengguna

| Key         | Type      | Default     | Description                                       |
| ----------- | --------- | ----------- | ------------------------------------------------- |
| `enabled`   | `boolean` | `false`     | Aktifkan atau nonaktifkan Dreaming sepenuhnya     |
| `frequency` | `string`  | `0 3 * * *` | Irama Cron opsional untuk keseluruhan sapuan Dreaming |

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
- Kebijakan dan ambang fase light/deep/REM adalah perilaku internal, bukan config yang ditujukan untuk pengguna.
