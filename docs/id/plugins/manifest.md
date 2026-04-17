---
read_when:
    - Anda sedang membangun plugin OpenClaw
    - Anda perlu mengirimkan skema konfigurasi plugin atau men-debug kesalahan validasi plugin
summary: Persyaratan manifest Plugin + skema JSON (validasi konfigurasi ketat)
title: Manifest Plugin
x-i18n:
    generated_at: "2026-04-15T09:14:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: ba2183bfa8802871e4ef33a0ebea290606e8351e9e83e25ee72456addb768730
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifest Plugin (`openclaw.plugin.json`)

Halaman ini hanya untuk **manifest plugin OpenClaw native**.

Untuk tata letak bundle yang kompatibel, lihat [Bundle Plugin](/id/plugins/bundles).

Format bundle yang kompatibel menggunakan file manifest yang berbeda:

- Bundle Codex: `.codex-plugin/plugin.json`
- Bundle Claude: `.claude-plugin/plugin.json` atau tata letak komponen Claude
  default tanpa manifest
- Bundle Cursor: `.cursor-plugin/plugin.json`

OpenClaw juga mendeteksi otomatis tata letak bundle tersebut, tetapi tata letak itu tidak divalidasi
terhadap skema `openclaw.plugin.json` yang dijelaskan di sini.

Untuk bundle yang kompatibel, OpenClaw saat ini membaca metadata bundle ditambah root
skill yang dideklarasikan, root perintah Claude, default `settings.json` bundle Claude,
default LSP bundle Claude, dan paket hook yang didukung saat tata letaknya sesuai
dengan ekspektasi runtime OpenClaw.

Setiap plugin OpenClaw native **harus** menyertakan file `openclaw.plugin.json` di
**root plugin**. OpenClaw menggunakan manifest ini untuk memvalidasi konfigurasi
**tanpa mengeksekusi kode plugin**. Manifest yang hilang atau tidak valid diperlakukan sebagai
kesalahan plugin dan memblokir validasi konfigurasi.

Lihat panduan lengkap sistem plugin: [Plugin](/id/tools/plugin).
Untuk model kapabilitas native dan panduan kompatibilitas eksternal saat ini:
[Model kapabilitas](/id/plugins/architecture#public-capability-model).

## Fungsi file ini

`openclaw.plugin.json` adalah metadata yang dibaca OpenClaw sebelum memuat
kode plugin Anda.

Gunakan untuk:

- identitas plugin
- validasi konfigurasi
- metadata auth dan onboarding yang harus tersedia tanpa mem-boot runtime
  plugin
- petunjuk aktivasi ringan yang dapat diperiksa oleh permukaan control-plane sebelum runtime
  dimuat
- deskriptor penyiapan ringan yang dapat diperiksa oleh permukaan setup/onboarding sebelum
  runtime dimuat
- metadata alias dan auto-enable yang harus diselesaikan sebelum runtime plugin dimuat
- metadata kepemilikan keluarga model shorthand yang harus mengaktifkan otomatis
  plugin sebelum runtime dimuat
- snapshot kepemilikan kapabilitas statis yang digunakan untuk wiring kompatibilitas bundle dan
  cakupan kontrak
- metadata runner QA ringan yang dapat diperiksa oleh host bersama `openclaw qa`
  sebelum runtime plugin dimuat
- metadata konfigurasi khusus channel yang harus digabungkan ke dalam katalog dan permukaan validasi
  tanpa memuat runtime
- petunjuk UI konfigurasi

Jangan gunakan untuk:

- mendaftarkan perilaku runtime
- mendeklarasikan entrypoint kode
- metadata instalasi npm

Hal-hal tersebut termasuk dalam kode plugin Anda dan `package.json`.

## Contoh minimal

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

## Contoh lengkap

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin provider OpenRouter",
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
      "choiceLabel": "Kunci API OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Kunci API OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Kunci API",
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

## Referensi field tingkat atas

| Field                               | Wajib    | Tipe                             | Artinya                                                                                                                                                                                                      |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Ya       | `string`                         | Id plugin kanonis. Ini adalah id yang digunakan di `plugins.entries.<id>`.                                                                                                                                  |
| `configSchema`                      | Ya       | `object`                         | JSON Schema inline untuk konfigurasi plugin ini.                                                                                                                                                             |
| `enabledByDefault`                  | Tidak    | `true`                           | Menandai plugin bundle sebagai aktif secara default. Hilangkan field ini, atau setel ke nilai apa pun selain `true`, agar plugin tetap nonaktif secara default.                                            |
| `legacyPluginIds`                   | Tidak    | `string[]`                       | Id lawas yang dinormalisasi ke id plugin kanonis ini.                                                                                                                                                        |
| `autoEnableWhenConfiguredProviders` | Tidak    | `string[]`                       | Id provider yang harus mengaktifkan plugin ini secara otomatis saat auth, konfigurasi, atau referensi model menyebutkannya.                                                                                 |
| `kind`                              | Tidak    | `"memory"` \| `"context-engine"` | Mendeklarasikan jenis plugin eksklusif yang digunakan oleh `plugins.slots.*`.                                                                                                                                |
| `channels`                          | Tidak    | `string[]`                       | Id channel yang dimiliki plugin ini. Digunakan untuk discovery dan validasi konfigurasi.                                                                                                                     |
| `providers`                         | Tidak    | `string[]`                       | Id provider yang dimiliki plugin ini.                                                                                                                                                                        |
| `modelSupport`                      | Tidak    | `object`                         | Metadata keluarga model shorthand milik manifest yang digunakan untuk memuat otomatis plugin sebelum runtime.                                                                                                |
| `cliBackends`                       | Tidak    | `string[]`                       | Id backend inferensi CLI yang dimiliki plugin ini. Digunakan untuk auto-aktivasi saat startup dari referensi konfigurasi eksplisit.                                                                         |
| `commandAliases`                    | Tidak    | `object[]`                       | Nama perintah yang dimiliki plugin ini yang harus menghasilkan diagnostik konfigurasi dan CLI yang sadar-plugin sebelum runtime dimuat.                                                                     |
| `providerAuthEnvVars`               | Tidak    | `Record<string, string[]>`       | Metadata env auth provider ringan yang dapat diperiksa OpenClaw tanpa memuat kode plugin.                                                                                                                    |
| `providerAuthAliases`               | Tidak    | `Record<string, string>`         | Id provider yang harus memakai ulang id provider lain untuk pencarian auth, misalnya provider coding yang berbagi kunci API provider dasar dan profil auth.                                                  |
| `channelEnvVars`                    | Tidak    | `Record<string, string[]>`       | Metadata env channel ringan yang dapat diperiksa OpenClaw tanpa memuat kode plugin. Gunakan ini untuk penyiapan channel berbasis env atau permukaan auth yang perlu dilihat helper startup/konfigurasi umum. |
| `providerAuthChoices`               | Tidak    | `object[]`                       | Metadata pilihan auth ringan untuk pemilih onboarding, resolusi provider yang diprioritaskan, dan wiring flag CLI sederhana.                                                                                |
| `activation`                        | Tidak    | `object`                         | Petunjuk aktivasi ringan untuk pemuatan yang dipicu provider, perintah, channel, rute, dan kapabilitas. Hanya metadata; runtime plugin tetap memiliki perilaku sebenarnya.                                  |
| `setup`                             | Tidak    | `object`                         | Deskriptor setup/onboarding ringan yang dapat diperiksa oleh permukaan discovery dan setup tanpa memuat runtime plugin.                                                                                     |
| `qaRunners`                         | Tidak    | `object[]`                       | Deskriptor runner QA ringan yang digunakan oleh host bersama `openclaw qa` sebelum runtime plugin dimuat.                                                                                                   |
| `contracts`                         | Tidak    | `object`                         | Snapshot kapabilitas bundle statis untuk kepemilikan speech, transkripsi realtime, suara realtime, media-understanding, image-generation, music-generation, video-generation, web-fetch, web search, dan tool. |
| `channelConfigs`                    | Tidak    | `Record<string, object>`         | Metadata konfigurasi channel milik manifest yang digabungkan ke dalam permukaan discovery dan validasi sebelum runtime dimuat.                                                                              |
| `skills`                            | Tidak    | `string[]`                       | Direktori Skills yang akan dimuat, relatif terhadap root plugin.                                                                                                                                             |
| `name`                              | Tidak    | `string`                         | Nama plugin yang dapat dibaca manusia.                                                                                                                                                                       |
| `description`                       | Tidak    | `string`                         | Ringkasan singkat yang ditampilkan di permukaan plugin.                                                                                                                                                      |
| `version`                           | Tidak    | `string`                         | Versi plugin untuk keperluan informasional.                                                                                                                                                                  |
| `uiHints`                           | Tidak    | `Record<string, object>`         | Label UI, placeholder, dan petunjuk sensitivitas untuk field konfigurasi.                                                                                                                                    |

## Referensi `providerAuthChoices`

Setiap entri `providerAuthChoices` mendeskripsikan satu pilihan onboarding atau auth.
OpenClaw membaca ini sebelum runtime provider dimuat.

| Field                 | Wajib    | Tipe                                            | Artinya                                                                                                        |
| --------------------- | -------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `provider`            | Ya       | `string`                                        | Id provider tempat pilihan ini berada.                                                                         |
| `method`              | Ya       | `string`                                        | Id metode auth yang akan digunakan untuk dispatch.                                                             |
| `choiceId`            | Ya       | `string`                                        | Id pilihan auth stabil yang digunakan oleh alur onboarding dan CLI.                                            |
| `choiceLabel`         | Tidak    | `string`                                        | Label yang ditampilkan ke pengguna. Jika dihilangkan, OpenClaw akan menggunakan `choiceId` sebagai fallback.  |
| `choiceHint`          | Tidak    | `string`                                        | Teks bantuan singkat untuk pemilih.                                                                            |
| `assistantPriority`   | Tidak    | `number`                                        | Nilai yang lebih rendah diurutkan lebih awal dalam pemilih interaktif yang digerakkan asisten.                |
| `assistantVisibility` | Tidak    | `"visible"` \| `"manual-only"`                  | Menyembunyikan pilihan dari pemilih asisten sambil tetap mengizinkan pemilihan CLI manual.                    |
| `deprecatedChoiceIds` | Tidak    | `string[]`                                      | Id pilihan lawas yang harus mengarahkan pengguna ke pilihan pengganti ini.                                     |
| `groupId`             | Tidak    | `string`                                        | Id grup opsional untuk mengelompokkan pilihan yang terkait.                                                    |
| `groupLabel`          | Tidak    | `string`                                        | Label yang ditampilkan ke pengguna untuk grup tersebut.                                                        |
| `groupHint`           | Tidak    | `string`                                        | Teks bantuan singkat untuk grup.                                                                               |
| `optionKey`           | Tidak    | `string`                                        | Kunci opsi internal untuk alur auth sederhana dengan satu flag.                                                |
| `cliFlag`             | Tidak    | `string`                                        | Nama flag CLI, seperti `--openrouter-api-key`.                                                                 |
| `cliOption`           | Tidak    | `string`                                        | Bentuk opsi CLI lengkap, seperti `--openrouter-api-key <key>`.                                                 |
| `cliDescription`      | Tidak    | `string`                                        | Deskripsi yang digunakan dalam bantuan CLI.                                                                    |
| `onboardingScopes`    | Tidak    | `Array<"text-inference" \| "image-generation">` | Permukaan onboarding tempat pilihan ini harus muncul. Jika dihilangkan, default-nya adalah `["text-inference"]`. |

## Referensi `commandAliases`

Gunakan `commandAliases` saat sebuah plugin memiliki nama perintah runtime yang mungkin
secara keliru dimasukkan pengguna ke dalam `plugins.allow` atau dicoba dijalankan sebagai
perintah CLI root. OpenClaw menggunakan metadata ini untuk diagnostik tanpa mengimpor kode runtime plugin.

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

| Field        | Wajib    | Tipe              | Artinya                                                                  |
| ------------ | -------- | ----------------- | ------------------------------------------------------------------------ |
| `name`       | Ya       | `string`          | Nama perintah yang dimiliki oleh plugin ini.                             |
| `kind`       | Tidak    | `"runtime-slash"` | Menandai alias sebagai perintah slash chat, bukan perintah CLI root.     |
| `cliCommand` | Tidak    | `string`          | Perintah CLI root terkait yang disarankan untuk operasi CLI, jika ada.   |

## Referensi `activation`

Gunakan `activation` saat plugin dapat secara ringan mendeklarasikan event control-plane mana
yang seharusnya mengaktifkannya nanti.

## Referensi `qaRunners`

Gunakan `qaRunners` saat sebuah plugin menyumbangkan satu atau lebih runner transport di bawah
root bersama `openclaw qa`. Pertahankan metadata ini tetap ringan dan statis; runtime plugin
tetap memiliki registrasi CLI yang sebenarnya melalui permukaan `runtime-api.ts`
ringan yang mengekspor `qaRunnerCliRegistrations`.

```json
{
  "qaRunners": [
    {
      "commandName": "matrix",
      "description": "Jalankan lane QA live Matrix berbasis Docker terhadap homeserver sementara"
    }
  ]
}
```

| Field         | Wajib    | Tipe     | Artinya                                                            |
| ------------- | -------- | -------- | ------------------------------------------------------------------ |
| `commandName` | Ya       | `string` | Subperintah yang dipasang di bawah `openclaw qa`, misalnya `matrix`. |
| `description` | Tidak    | `string` | Teks bantuan fallback yang digunakan saat host bersama memerlukan perintah stub. |

Blok ini hanya metadata. Blok ini tidak mendaftarkan perilaku runtime, dan juga
tidak menggantikan `register(...)`, `setupEntry`, atau entrypoint runtime/plugin lainnya.
Konsumen saat ini menggunakannya sebagai petunjuk penyempitan sebelum pemuatan plugin yang lebih luas, jadi
metadata activation yang hilang biasanya hanya berdampak pada performa; hal itu seharusnya tidak
mengubah kebenaran selama fallback kepemilikan manifest lawas masih ada.

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

| Field            | Wajib    | Tipe                                                 | Artinya                                                            |
| ---------------- | -------- | ---------------------------------------------------- | ------------------------------------------------------------------ |
| `onProviders`    | Tidak    | `string[]`                                           | Id provider yang harus mengaktifkan plugin ini saat diminta.       |
| `onCommands`     | Tidak    | `string[]`                                           | Id perintah yang harus mengaktifkan plugin ini.                    |
| `onChannels`     | Tidak    | `string[]`                                           | Id channel yang harus mengaktifkan plugin ini.                     |
| `onRoutes`       | Tidak    | `string[]`                                           | Jenis rute yang harus mengaktifkan plugin ini.                     |
| `onCapabilities` | Tidak    | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Petunjuk kapabilitas luas yang digunakan oleh perencanaan aktivasi control-plane. |

Konsumen live saat ini:

- perencanaan CLI yang dipicu perintah menggunakan fallback ke
  `commandAliases[].cliCommand` atau `commandAliases[].name` lawas
- perencanaan setup/channel yang dipicu channel menggunakan fallback ke kepemilikan
  `channels[]` lawas saat metadata aktivasi channel eksplisit tidak ada
- perencanaan setup/runtime yang dipicu provider menggunakan fallback ke
  kepemilikan `providers[]` dan `cliBackends[]` tingkat atas lawas saat metadata aktivasi provider eksplisit
  tidak ada

## Referensi `setup`

Gunakan `setup` saat permukaan setup dan onboarding memerlukan metadata milik plugin yang ringan
sebelum runtime dimuat.

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

`cliBackends` tingkat atas tetap valid dan terus mendeskripsikan backend inferensi
CLI. `setup.cliBackends` adalah permukaan deskriptor khusus setup untuk
alur control-plane/setup yang harus tetap hanya berupa metadata.

Jika ada, `setup.providers` dan `setup.cliBackends` adalah permukaan pencarian
utama berbasis deskriptor untuk discovery setup. Jika deskriptor hanya
mempersempit kandidat plugin dan setup masih memerlukan hook runtime saat setup
yang lebih kaya, setel `requiresRuntime: true` dan tetap pertahankan `setup-api`
sebagai jalur eksekusi fallback.

Karena pencarian setup dapat mengeksekusi kode `setup-api` milik plugin, nilai
`setup.providers[].id` dan `setup.cliBackends[]` yang telah dinormalisasi harus tetap unik di seluruh
plugin yang ditemukan. Kepemilikan yang ambigu akan gagal secara tertutup alih-alih memilih
pemenang berdasarkan urutan discovery.

### Referensi `setup.providers`

| Field         | Wajib    | Tipe       | Artinya                                                                              |
| ------------- | -------- | ---------- | ------------------------------------------------------------------------------------ |
| `id`          | Ya       | `string`   | Id provider yang diekspos saat setup atau onboarding. Pertahankan id yang dinormalisasi tetap unik secara global. |
| `authMethods` | Tidak    | `string[]` | Id metode setup/auth yang didukung provider ini tanpa memuat runtime penuh.          |
| `envVars`     | Tidak    | `string[]` | Env vars yang dapat diperiksa oleh permukaan setup/status umum sebelum runtime plugin dimuat. |

### Field `setup`

| Field              | Wajib    | Tipe       | Artinya                                                                                         |
| ------------------ | -------- | ---------- | ------------------------------------------------------------------------------------------------ |
| `providers`        | Tidak    | `object[]` | Deskriptor setup provider yang diekspos selama setup dan onboarding.                             |
| `cliBackends`      | Tidak    | `string[]` | Id backend saat setup yang digunakan untuk pencarian setup berbasis deskriptor. Pertahankan id yang dinormalisasi tetap unik secara global. |
| `configMigrations` | Tidak    | `string[]` | Id migrasi konfigurasi yang dimiliki oleh permukaan setup plugin ini.                            |
| `requiresRuntime`  | Tidak    | `boolean`  | Apakah setup masih memerlukan eksekusi `setup-api` setelah pencarian deskriptor.                |

## Referensi `uiHints`

`uiHints` adalah peta dari nama field konfigurasi ke petunjuk rendering kecil.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Kunci API",
      "help": "Digunakan untuk permintaan OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Setiap petunjuk field dapat mencakup:

| Field         | Tipe       | Artinya                                 |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Label field yang ditampilkan ke pengguna. |
| `help`        | `string`   | Teks bantuan singkat.                   |
| `tags`        | `string[]` | Tag UI opsional.                        |
| `advanced`    | `boolean`  | Menandai field sebagai lanjutan.        |
| `sensitive`   | `boolean`  | Menandai field sebagai rahasia atau sensitif. |
| `placeholder` | `string`   | Teks placeholder untuk input formulir.  |

## Referensi `contracts`

Gunakan `contracts` hanya untuk metadata kepemilikan kapabilitas statis yang dapat
dibaca OpenClaw tanpa mengimpor runtime plugin.

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

Setiap daftar bersifat opsional:

| Field                            | Tipe       | Artinya                                                          |
| -------------------------------- | ---------- | ---------------------------------------------------------------- |
| `speechProviders`                | `string[]` | Id provider speech yang dimiliki plugin ini.                     |
| `realtimeTranscriptionProviders` | `string[]` | Id provider transkripsi realtime yang dimiliki plugin ini.       |
| `realtimeVoiceProviders`         | `string[]` | Id provider suara realtime yang dimiliki plugin ini.             |
| `mediaUnderstandingProviders`    | `string[]` | Id provider media-understanding yang dimiliki plugin ini.        |
| `imageGenerationProviders`       | `string[]` | Id provider image-generation yang dimiliki plugin ini.           |
| `videoGenerationProviders`       | `string[]` | Id provider video-generation yang dimiliki plugin ini.           |
| `webFetchProviders`              | `string[]` | Id provider web-fetch yang dimiliki plugin ini.                  |
| `webSearchProviders`             | `string[]` | Id provider web search yang dimiliki plugin ini.                 |
| `tools`                          | `string[]` | Nama tool agen yang dimiliki plugin ini untuk pemeriksaan kontrak bundle. |

## Referensi `channelConfigs`

Gunakan `channelConfigs` saat plugin channel memerlukan metadata konfigurasi ringan sebelum
runtime dimuat.

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
          "label": "URL homeserver",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Koneksi homeserver Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Setiap entri channel dapat mencakup:

| Field         | Tipe                     | Artinya                                                                                  |
| ------------- | ------------------------ | ----------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema untuk `channels.<id>`. Wajib untuk setiap entri konfigurasi channel yang dideklarasikan. |
| `uiHints`     | `Record<string, object>` | Label UI/placeholder/petunjuk sensitif opsional untuk bagian konfigurasi channel tersebut. |
| `label`       | `string`                 | Label channel yang digabungkan ke dalam permukaan pemilih dan inspeksi saat metadata runtime belum siap. |
| `description` | `string`                 | Deskripsi channel singkat untuk permukaan inspeksi dan katalog.                          |
| `preferOver`  | `string[]`               | Id plugin lawas atau berprioritas lebih rendah yang harus dikalahkan channel ini dalam permukaan pemilihan. |

## Referensi `modelSupport`

Gunakan `modelSupport` saat OpenClaw harus menyimpulkan plugin provider Anda dari
id model shorthand seperti `gpt-5.4` atau `claude-sonnet-4.6` sebelum runtime plugin
dimuat.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw menerapkan prioritas berikut:

- referensi `provider/model` yang eksplisit menggunakan metadata manifest `providers`
  milik plugin pemilik
- `modelPatterns` mengalahkan `modelPrefixes`
- jika satu plugin non-bundled dan satu plugin bundled sama-sama cocok, plugin non-bundled
  yang menang
- ambiguitas yang tersisa diabaikan sampai pengguna atau konfigurasi menentukan provider

Field:

| Field           | Tipe       | Artinya                                                                        |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | Prefiks yang dicocokkan dengan `startsWith` terhadap id model shorthand.       |
| `modelPatterns` | `string[]` | Sumber regex yang dicocokkan terhadap id model shorthand setelah sufiks profil dihapus. |

Kunci kapabilitas tingkat atas lawas sudah usang. Gunakan `openclaw doctor --fix` untuk
memindahkan `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders`, dan `webSearchProviders` ke bawah `contracts`; pemuatan
manifest normal tidak lagi memperlakukan field tingkat atas tersebut sebagai
kepemilikan kapabilitas.

## Manifest versus package.json

Kedua file ini melayani fungsi yang berbeda:

| File                   | Gunakan untuk                                                                                                                       |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Discovery, validasi konfigurasi, metadata pilihan auth, dan petunjuk UI yang harus ada sebelum kode plugin berjalan                |
| `package.json`         | Metadata npm, instalasi dependensi, dan blok `openclaw` yang digunakan untuk entrypoint, pengendalian instalasi, setup, atau metadata katalog |

Jika Anda tidak yakin metadata tertentu harus ditempatkan di mana, gunakan aturan ini:

- jika OpenClaw harus mengetahuinya sebelum memuat kode plugin, letakkan di `openclaw.plugin.json`
- jika itu berkaitan dengan packaging, file entry, atau perilaku instalasi npm, letakkan di `package.json`

### Field `package.json` yang memengaruhi discovery

Beberapa metadata plugin pra-runtime sengaja ditempatkan di `package.json` di bawah
blok `openclaw`, bukan di `openclaw.plugin.json`.

Contoh penting:

| Field                                                             | Artinya                                                                                                                                      |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Mendeklarasikan entrypoint plugin native.                                                                                                    |
| `openclaw.setupEntry`                                             | Entrypoint ringan khusus setup yang digunakan selama onboarding dan startup channel yang ditunda.                                            |
| `openclaw.channel`                                                | Metadata katalog channel ringan seperti label, path docs, alias, dan copy pemilihan.                                                        |
| `openclaw.channel.configuredState`                                | Metadata pemeriksa configured-state ringan yang dapat menjawab "apakah setup hanya-env sudah ada?" tanpa memuat runtime channel penuh.      |
| `openclaw.channel.persistedAuthState`                             | Metadata pemeriksa auth tersimpan ringan yang dapat menjawab "apakah sudah ada yang login?" tanpa memuat runtime channel penuh.             |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Petunjuk instalasi/pembaruan untuk plugin bundle dan plugin yang dipublikasikan secara eksternal.                                           |
| `openclaw.install.defaultChoice`                                  | Jalur instalasi yang diprioritaskan saat tersedia beberapa sumber instalasi.                                                                |
| `openclaw.install.minHostVersion`                                 | Versi minimum host OpenClaw yang didukung, menggunakan batas bawah semver seperti `>=2026.3.22`.                                           |
| `openclaw.install.allowInvalidConfigRecovery`                     | Mengizinkan jalur pemulihan reinstalasi plugin bundle yang sempit saat konfigurasi tidak valid.                                             |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Memungkinkan permukaan channel khusus setup dimuat sebelum plugin channel penuh saat startup.                                                |

`openclaw.install.minHostVersion` diterapkan selama instalasi dan pemuatan registry
manifest. Nilai yang tidak valid ditolak; nilai yang valid tetapi lebih baru akan melewati
plugin pada host yang lebih lama.

`openclaw.install.allowInvalidConfigRecovery` sengaja dibuat sempit. Nilai ini
tidak membuat konfigurasi rusak apa pun dapat diinstal. Saat ini nilai ini hanya memungkinkan
alur instalasi memulihkan kegagalan upgrade plugin bundle lama tertentu, seperti
path plugin bundle yang hilang atau entri `channels.<id>` lama untuk plugin bundle yang sama.
Kesalahan konfigurasi yang tidak terkait tetap memblokir instalasi dan mengarahkan operator
ke `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` adalah metadata package untuk modul pemeriksa
kecil:

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

Gunakan ini saat alur setup, doctor, atau configured-state memerlukan probe auth ya/tidak
yang ringan sebelum plugin channel penuh dimuat. Export target harus berupa fungsi kecil
yang hanya membaca state yang tersimpan; jangan arahkan melalui barrel runtime
channel penuh.

`openclaw.channel.configuredState` mengikuti bentuk yang sama untuk pemeriksaan configured-state
hanya-env yang ringan:

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

Gunakan ini saat sebuah channel dapat menjawab configured-state dari env atau input kecil
non-runtime lainnya. Jika pemeriksaan memerlukan resolusi konfigurasi penuh atau runtime
channel yang sebenarnya, pertahankan logika itu di hook plugin `config.hasConfiguredState`.

## Persyaratan JSON Schema

- **Setiap plugin harus menyertakan JSON Schema**, bahkan jika tidak menerima konfigurasi apa pun.
- Skema kosong dapat diterima (misalnya, `{ "type": "object", "additionalProperties": false }`).
- Skema divalidasi pada saat baca/tulis konfigurasi, bukan saat runtime.

## Perilaku validasi

- Kunci `channels.*` yang tidak dikenal adalah **kesalahan**, kecuali id channel tersebut dideklarasikan oleh
  manifest plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, dan `plugins.slots.*`
  harus merujuk ke id plugin yang **dapat ditemukan**. Id yang tidak dikenal adalah **kesalahan**.
- Jika sebuah plugin terinstal tetapi memiliki manifest atau skema yang rusak atau hilang,
  validasi gagal dan Doctor melaporkan kesalahan plugin.
- Jika konfigurasi plugin ada tetapi plugin tersebut **nonaktif**, konfigurasi tetap disimpan dan
  **peringatan** ditampilkan di Doctor + log.

Lihat [Referensi konfigurasi](/id/gateway/configuration) untuk skema `plugins.*` lengkap.

## Catatan

- Manifest **wajib untuk plugin OpenClaw native**, termasuk pemuatan dari filesystem lokal.
- Runtime tetap memuat modul plugin secara terpisah; manifest hanya untuk
  discovery + validasi.
- Manifest native di-parse dengan JSON5, sehingga komentar, koma di akhir, dan
  kunci tanpa tanda kutip diterima selama nilai akhirnya tetap berupa objek.
- Hanya field manifest yang terdokumentasi yang dibaca oleh loader manifest. Hindari menambahkan
  kunci tingkat atas kustom di sini.
- `providerAuthEnvVars` adalah jalur metadata ringan untuk probe auth, validasi
  penanda env, dan permukaan auth provider serupa yang tidak seharusnya mem-boot runtime
  plugin hanya untuk memeriksa nama env.
- `providerAuthAliases` memungkinkan varian provider menggunakan kembali env vars
  auth, profil auth, auth berbasis konfigurasi, dan pilihan onboarding kunci API milik provider lain
  tanpa meng-hardcode hubungan tersebut di core.
- `channelEnvVars` adalah jalur metadata ringan untuk fallback shell-env, prompt
  setup, dan permukaan channel serupa yang tidak seharusnya mem-boot runtime plugin
  hanya untuk memeriksa nama env.
- `providerAuthChoices` adalah jalur metadata ringan untuk pemilih pilihan auth,
  resolusi `--auth-choice`, pemetaan provider yang diprioritaskan, dan registrasi flag CLI onboarding
  sederhana sebelum runtime provider dimuat. Untuk metadata wizard runtime
  yang memerlukan kode provider, lihat
  [Hook runtime provider](/id/plugins/architecture#provider-runtime-hooks).
- Jenis plugin eksklusif dipilih melalui `plugins.slots.*`.
  - `kind: "memory"` dipilih oleh `plugins.slots.memory`.
  - `kind: "context-engine"` dipilih oleh `plugins.slots.contextEngine`
    (default: `legacy` bawaan).
- `channels`, `providers`, `cliBackends`, dan `skills` dapat dihilangkan saat sebuah
  plugin tidak memerlukannya.
- Jika plugin Anda bergantung pada modul native, dokumentasikan langkah build dan
  persyaratan allowlist package-manager apa pun (misalnya, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Terkait

- [Membangun Plugin](/id/plugins/building-plugins) — memulai dengan plugin
- [Arsitektur Plugin](/id/plugins/architecture) — arsitektur internal
- [Ikhtisar SDK](/id/plugins/sdk-overview) — referensi SDK Plugin
