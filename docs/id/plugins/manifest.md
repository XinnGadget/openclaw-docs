---
read_when:
    - Anda sedang membangun Plugin OpenClaw
    - Anda perlu mengirimkan skema config Plugin atau men-debug error validasi Plugin
summary: Persyaratan manifest Plugin + skema JSON (validasi config ketat)
title: Manifest Plugin
x-i18n:
    generated_at: "2026-04-12T23:28:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 93b57c7373e4ccd521b10945346db67991543bd2bed4cc8b6641e1f215b48579
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifest Plugin (`openclaw.plugin.json`)

Halaman ini hanya untuk **manifest Plugin OpenClaw native**.

Untuk tata letak bundle yang kompatibel, lihat [Plugin bundles](/id/plugins/bundles).

Format bundle yang kompatibel menggunakan file manifest yang berbeda:

- Bundle Codex: `.codex-plugin/plugin.json`
- Bundle Claude: `.claude-plugin/plugin.json` atau tata letak komponen Claude default
  tanpa manifest
- Bundle Cursor: `.cursor-plugin/plugin.json`

OpenClaw juga mendeteksi tata letak bundle tersebut secara otomatis, tetapi tidak divalidasi
terhadap skema `openclaw.plugin.json` yang dijelaskan di sini.

Untuk bundle yang kompatibel, OpenClaw saat ini membaca metadata bundle beserta root
skill yang dideklarasikan, root perintah Claude, default `settings.json` bundle Claude,
default LSP bundle Claude, dan hook pack yang didukung ketika tata letaknya cocok
dengan ekspektasi runtime OpenClaw.

Setiap Plugin OpenClaw native **harus** menyertakan file `openclaw.plugin.json` di
**root Plugin**. OpenClaw menggunakan manifest ini untuk memvalidasi konfigurasi
**tanpa mengeksekusi kode Plugin**. Manifest yang hilang atau tidak valid dianggap
sebagai error Plugin dan memblokir validasi config.

Lihat panduan sistem Plugin lengkap: [Plugins](/id/tools/plugin).
Untuk model capability native dan panduan kompatibilitas eksternal saat ini:
[Capability model](/id/plugins/architecture#public-capability-model).

## Fungsi file ini

`openclaw.plugin.json` adalah metadata yang dibaca OpenClaw sebelum memuat kode
Plugin Anda.

Gunakan untuk:

- identitas Plugin
- validasi config
- metadata auth dan onboarding yang harus tersedia tanpa mem-boot runtime Plugin
- petunjuk aktivasi ringan yang dapat diperiksa permukaan control-plane sebelum runtime dimuat
- deskriptor setup ringan yang dapat diperiksa permukaan setup/onboarding sebelum
  runtime dimuat
- metadata alias dan auto-enable yang harus diselesaikan sebelum runtime Plugin dimuat
- metadata kepemilikan keluarga model bentuk singkat yang harus mengaktifkan Plugin
  secara otomatis sebelum runtime dimuat
- snapshot kepemilikan capability statis yang digunakan untuk wiring compat bundle dan
  cakupan kontrak
- metadata config khusus channel yang harus digabungkan ke permukaan katalog dan validasi
  tanpa memuat runtime
- petunjuk UI config

Jangan gunakan untuk:

- mendaftarkan perilaku runtime
- mendeklarasikan entrypoint kode
- metadata instalasi npm

Hal-hal tersebut termasuk ke dalam kode Plugin Anda dan `package.json`.

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

| Field                               | Wajib | Tipe                             | Artinya                                                                                                                                                                                                      |
| ----------------------------------- | ----- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Ya    | `string`                         | ID Plugin kanonis. Ini adalah ID yang digunakan dalam `plugins.entries.<id>`.                                                                                                                               |
| `configSchema`                      | Ya    | `object`                         | JSON Schema inline untuk config Plugin ini.                                                                                                                                                                  |
| `enabledByDefault`                  | Tidak | `true`                           | Menandai Plugin bundle sebagai aktif secara default. Hilangkan, atau tetapkan nilai apa pun selain `true`, agar Plugin tetap nonaktif secara default.                                                       |
| `legacyPluginIds`                   | Tidak | `string[]`                       | ID lama yang dinormalisasi ke ID Plugin kanonis ini.                                                                                                                                                         |
| `autoEnableWhenConfiguredProviders` | Tidak | `string[]`                       | ID provider yang harus mengaktifkan Plugin ini secara otomatis ketika auth, config, atau ref model menyebutkannya.                                                                                          |
| `kind`                              | Tidak | `"memory"` \| `"context-engine"` | Mendeklarasikan jenis Plugin eksklusif yang digunakan oleh `plugins.slots.*`.                                                                                                                                |
| `channels`                          | Tidak | `string[]`                       | ID channel yang dimiliki oleh Plugin ini. Digunakan untuk discovery dan validasi config.                                                                                                                     |
| `providers`                         | Tidak | `string[]`                       | ID provider yang dimiliki oleh Plugin ini.                                                                                                                                                                   |
| `modelSupport`                      | Tidak | `object`                         | Metadata keluarga model bentuk singkat milik manifest yang digunakan untuk memuat Plugin secara otomatis sebelum runtime.                                                                                    |
| `cliBackends`                       | Tidak | `string[]`                       | ID backend inferensi CLI yang dimiliki oleh Plugin ini. Digunakan untuk auto-aktivasi saat startup dari ref config eksplisit.                                                                               |
| `commandAliases`                    | Tidak | `object[]`                       | Nama perintah yang dimiliki oleh Plugin ini yang harus menghasilkan diagnostik config dan CLI yang sadar-Plugin sebelum runtime dimuat.                                                                     |
| `providerAuthEnvVars`               | Tidak | `Record<string, string[]>`       | Metadata env auth provider ringan yang dapat diperiksa OpenClaw tanpa memuat kode Plugin.                                                                                                                    |
| `providerAuthAliases`               | Tidak | `Record<string, string>`         | ID provider yang harus menggunakan kembali ID provider lain untuk lookup auth, misalnya provider coding yang berbagi kunci API provider dasar dan profil auth.                                               |
| `channelEnvVars`                    | Tidak | `Record<string, string[]>`       | Metadata env channel ringan yang dapat diperiksa OpenClaw tanpa memuat kode Plugin. Gunakan ini untuk permukaan setup atau auth channel berbasis env yang harus terlihat oleh helper startup/config generik. |
| `providerAuthChoices`               | Tidak | `object[]`                       | Metadata pilihan auth ringan untuk pemilih onboarding, resolusi provider pilihan, dan wiring flag CLI sederhana.                                                                                            |
| `activation`                        | Tidak | `object`                         | Petunjuk aktivasi ringan untuk pemuatan yang dipicu oleh provider, perintah, channel, rute, dan capability. Hanya metadata; runtime Plugin tetap memiliki perilaku sebenarnya.                             |
| `setup`                             | Tidak | `object`                         | Deskriptor setup/onboarding ringan yang dapat diperiksa permukaan discovery dan setup tanpa memuat runtime Plugin.                                                                                          |
| `contracts`                         | Tidak | `object`                         | Snapshot capability bundle statis untuk speech, transkripsi realtime, suara realtime, media-understanding, image-generation, music-generation, video-generation, web-fetch, pencarian web, dan kepemilikan tool. |
| `channelConfigs`                    | Tidak | `Record<string, object>`         | Metadata config channel milik manifest yang digabungkan ke permukaan discovery dan validasi sebelum runtime dimuat.                                                                                          |
| `skills`                            | Tidak | `string[]`                       | Direktori Skills yang akan dimuat, relatif terhadap root Plugin.                                                                                                                                             |
| `name`                              | Tidak | `string`                         | Nama Plugin yang dapat dibaca manusia.                                                                                                                                                                       |
| `description`                       | Tidak | `string`                         | Ringkasan singkat yang ditampilkan di permukaan Plugin.                                                                                                                                                      |
| `version`                           | Tidak | `string`                         | Versi Plugin informasional.                                                                                                                                                                                  |
| `uiHints`                           | Tidak | `Record<string, object>`         | Label UI, placeholder, dan petunjuk sensitivitas untuk field config.                                                                                                                                         |

## Referensi `providerAuthChoices`

Setiap entri `providerAuthChoices` menjelaskan satu pilihan onboarding atau auth.
OpenClaw membacanya sebelum runtime provider dimuat.

| Field                 | Wajib | Tipe                                            | Artinya                                                                                             |
| --------------------- | ----- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `provider`            | Ya    | `string`                                        | ID provider tempat pilihan ini berada.                                                              |
| `method`              | Ya    | `string`                                        | ID metode auth yang akan dituju.                                                                    |
| `choiceId`            | Ya    | `string`                                        | ID pilihan auth stabil yang digunakan oleh alur onboarding dan CLI.                                 |
| `choiceLabel`         | Tidak | `string`                                        | Label yang ditampilkan ke pengguna. Jika dihilangkan, OpenClaw menggunakan `choiceId` sebagai fallback. |
| `choiceHint`          | Tidak | `string`                                        | Teks bantuan singkat untuk pemilih.                                                                 |
| `assistantPriority`   | Tidak | `number`                                        | Nilai yang lebih rendah diurutkan lebih awal dalam pemilih interaktif yang digerakkan asisten.     |
| `assistantVisibility` | Tidak | `"visible"` \| `"manual-only"`                  | Sembunyikan pilihan ini dari pemilih asisten sambil tetap mengizinkan pemilihan CLI manual.        |
| `deprecatedChoiceIds` | Tidak | `string[]`                                      | ID pilihan lama yang harus mengarahkan pengguna ke pilihan pengganti ini.                           |
| `groupId`             | Tidak | `string`                                        | ID grup opsional untuk mengelompokkan pilihan terkait.                                              |
| `groupLabel`          | Tidak | `string`                                        | Label untuk grup tersebut yang ditampilkan ke pengguna.                                             |
| `groupHint`           | Tidak | `string`                                        | Teks bantuan singkat untuk grup.                                                                    |
| `optionKey`           | Tidak | `string`                                        | Kunci opsi internal untuk alur auth sederhana dengan satu flag.                                     |
| `cliFlag`             | Tidak | `string`                                        | Nama flag CLI, seperti `--openrouter-api-key`.                                                      |
| `cliOption`           | Tidak | `string`                                        | Bentuk opsi CLI lengkap, seperti `--openrouter-api-key <key>`.                                      |
| `cliDescription`      | Tidak | `string`                                        | Deskripsi yang digunakan di bantuan CLI.                                                            |
| `onboardingScopes`    | Tidak | `Array<"text-inference" \| "image-generation">` | Permukaan onboarding tempat pilihan ini harus muncul. Jika dihilangkan, default-nya `["text-inference"]`. |

## Referensi `commandAliases`

Gunakan `commandAliases` ketika sebuah Plugin memiliki nama perintah runtime yang mungkin
keliru dimasukkan pengguna ke dalam `plugins.allow` atau dicoba dijalankan sebagai perintah CLI root. OpenClaw
menggunakan metadata ini untuk diagnostik tanpa mengimpor kode runtime Plugin.

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

| Field        | Wajib | Tipe              | Artinya                                                                      |
| ------------ | ----- | ----------------- | ---------------------------------------------------------------------------- |
| `name`       | Ya    | `string`          | Nama perintah yang dimiliki oleh Plugin ini.                                 |
| `kind`       | Tidak | `"runtime-slash"` | Menandai alias sebagai slash command chat, bukan perintah CLI root.          |
| `cliCommand` | Tidak | `string`          | Perintah CLI root terkait yang disarankan untuk operasi CLI, jika ada.       |

## Referensi `activation`

Gunakan `activation` ketika Plugin dapat mendeklarasikan secara ringan event control-plane mana
yang harus mengaktifkannya nanti.

Blok ini hanya metadata. Blok ini tidak mendaftarkan perilaku runtime, dan tidak
menggantikan `register(...)`, `setupEntry`, atau entrypoint runtime/Plugin lainnya.
Consumer saat ini menggunakannya sebagai petunjuk penyempitan sebelum pemuatan Plugin yang lebih luas, sehingga
metadata aktivasi yang hilang biasanya hanya berdampak pada performa; seharusnya tidak
mengubah kebenaran selama fallback kepemilikan manifest lama masih ada.

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

| Field            | Wajib | Tipe                                                 | Artinya                                                          |
| ---------------- | ----- | ---------------------------------------------------- | ---------------------------------------------------------------- |
| `onProviders`    | Tidak | `string[]`                                           | ID provider yang harus mengaktifkan Plugin ini saat diminta.     |
| `onCommands`     | Tidak | `string[]`                                           | ID perintah yang harus mengaktifkan Plugin ini.                  |
| `onChannels`     | Tidak | `string[]`                                           | ID channel yang harus mengaktifkan Plugin ini.                   |
| `onRoutes`       | Tidak | `string[]`                                           | Jenis route yang harus mengaktifkan Plugin ini.                  |
| `onCapabilities` | Tidak | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Petunjuk capability luas yang digunakan oleh perencanaan aktivasi control-plane. |

Consumer langsung saat ini:

- perencanaan CLI yang dipicu perintah menggunakan fallback ke
  `commandAliases[].cliCommand` atau `commandAliases[].name` lama
- perencanaan setup/channel yang dipicu channel menggunakan fallback ke kepemilikan
  `channels[]` lama ketika metadata aktivasi channel eksplisit tidak ada
- perencanaan setup/runtime yang dipicu provider menggunakan fallback ke kepemilikan
  `providers[]` dan `cliBackends[]` tingkat atas lama ketika metadata aktivasi provider eksplisit tidak ada

## Referensi `setup`

Gunakan `setup` ketika permukaan setup dan onboarding memerlukan metadata milik Plugin yang ringan
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

`cliBackends` tingkat atas tetap valid dan terus mendeskripsikan backend inferensi CLI. `setup.cliBackends` adalah permukaan deskriptor khusus setup untuk
alur control-plane/setup yang harus tetap hanya berupa metadata.

Jika ada, `setup.providers` dan `setup.cliBackends` adalah permukaan lookup yang diutamakan
berbasis deskriptor untuk discovery setup. Jika deskriptor hanya mempersempit kandidat Plugin dan setup masih membutuhkan hook runtime saat setup yang lebih kaya, tetapkan `requiresRuntime: true` dan pertahankan `setup-api` sebagai jalur eksekusi fallback.

Karena lookup setup dapat mengeksekusi kode `setup-api` milik Plugin, nilai `setup.providers[].id` dan `setup.cliBackends[]` yang telah dinormalisasi harus tetap unik di seluruh Plugin yang ditemukan. Kepemilikan yang ambigu gagal secara tertutup alih-alih memilih pemenang berdasarkan urutan discovery.

### Referensi `setup.providers`

| Field         | Wajib | Tipe       | Artinya                                                                               |
| ------------- | ----- | ---------- | ------------------------------------------------------------------------------------- |
| `id`          | Ya    | `string`   | ID provider yang diekspos selama setup atau onboarding. Pertahankan ID yang dinormalisasi tetap unik secara global. |
| `authMethods` | Tidak | `string[]` | ID metode setup/auth yang didukung provider ini tanpa memuat runtime penuh.           |
| `envVars`     | Tidak | `string[]` | Env vars yang dapat diperiksa permukaan setup/status generik sebelum runtime Plugin dimuat. |

### Field `setup`

| Field              | Wajib | Tipe       | Artinya                                                                                              |
| ------------------ | ----- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `providers`        | Tidak | `object[]` | Deskriptor setup provider yang diekspos selama setup dan onboarding.                                 |
| `cliBackends`      | Tidak | `string[]` | ID backend saat setup yang digunakan untuk lookup setup berbasis deskriptor. Pertahankan ID yang dinormalisasi tetap unik secara global. |
| `configMigrations` | Tidak | `string[]` | ID migrasi config yang dimiliki oleh permukaan setup Plugin ini.                                     |
| `requiresRuntime`  | Tidak | `boolean`  | Apakah setup masih memerlukan eksekusi `setup-api` setelah lookup deskriptor.                       |

## Referensi `uiHints`

`uiHints` adalah peta dari nama field config ke petunjuk rendering kecil.

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

| Field         | Tipe       | Artinya                                  |
| ------------- | ---------- | ---------------------------------------- |
| `label`       | `string`   | Label field yang ditampilkan ke pengguna. |
| `help`        | `string`   | Teks bantuan singkat.                    |
| `tags`        | `string[]` | Tag UI opsional.                         |
| `advanced`    | `boolean`  | Menandai field sebagai lanjutan.         |
| `sensitive`   | `boolean`  | Menandai field sebagai rahasia atau sensitif. |
| `placeholder` | `string`   | Teks placeholder untuk input formulir.   |

## Referensi `contracts`

Gunakan `contracts` hanya untuk metadata kepemilikan capability statis yang dapat dibaca OpenClaw
tanpa mengimpor runtime Plugin.

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

| Field                            | Tipe      | Artinya                                                     |
| -------------------------------- | --------- | ----------------------------------------------------------- |
| `speechProviders`                | `string[]` | ID provider speech yang dimiliki oleh Plugin ini.           |
| `realtimeTranscriptionProviders` | `string[]` | ID provider transkripsi realtime yang dimiliki oleh Plugin ini. |
| `realtimeVoiceProviders`         | `string[]` | ID provider suara realtime yang dimiliki oleh Plugin ini.   |
| `mediaUnderstandingProviders`    | `string[]` | ID provider media-understanding yang dimiliki oleh Plugin ini. |
| `imageGenerationProviders`       | `string[]` | ID provider image-generation yang dimiliki oleh Plugin ini. |
| `videoGenerationProviders`       | `string[]` | ID provider video-generation yang dimiliki oleh Plugin ini. |
| `webFetchProviders`              | `string[]` | ID provider web-fetch yang dimiliki oleh Plugin ini.        |
| `webSearchProviders`             | `string[]` | ID provider pencarian web yang dimiliki oleh Plugin ini.    |
| `tools`                          | `string[]` | Nama tool agen yang dimiliki oleh Plugin ini untuk pemeriksaan kontrak bundle. |

## Referensi `channelConfigs`

Gunakan `channelConfigs` ketika Plugin channel memerlukan metadata config ringan sebelum
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
          "label": "URL Homeserver",
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
| ------------- | ------------------------ | ---------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | JSON Schema untuk `channels.<id>`. Wajib untuk setiap entri config channel yang dideklarasikan. |
| `uiHints`     | `Record<string, object>` | Label UI, placeholder, dan petunjuk sensitif opsional untuk bagian config channel tersebut. |
| `label`       | `string`                 | Label channel yang digabungkan ke permukaan picker dan inspect ketika metadata runtime belum siap. |
| `description` | `string`                 | Deskripsi channel singkat untuk permukaan inspect dan katalog.                           |
| `preferOver`  | `string[]`               | ID Plugin lama atau berprioritas lebih rendah yang harus dikalahkan channel ini di permukaan pemilihan. |

## Referensi `modelSupport`

Gunakan `modelSupport` ketika OpenClaw harus menyimpulkan Plugin provider Anda dari
ID model bentuk singkat seperti `gpt-5.4` atau `claude-sonnet-4.6` sebelum runtime Plugin
dimuat.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw menerapkan urutan prioritas ini:

- ref `provider/model` eksplisit menggunakan metadata manifest `providers` yang memilikinya
- `modelPatterns` mengalahkan `modelPrefixes`
- jika satu Plugin non-bundle dan satu Plugin bundle sama-sama cocok, Plugin non-bundle
  yang menang
- ambiguitas yang tersisa diabaikan sampai pengguna atau config menentukan provider

Field:

| Field           | Tipe      | Artinya                                                                         |
| --------------- | --------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefiks yang dicocokkan dengan `startsWith` terhadap ID model bentuk singkat.   |
| `modelPatterns` | `string[]` | Sumber regex yang dicocokkan terhadap ID model bentuk singkat setelah sufiks profil dihapus. |

Kunci capability tingkat atas lama sudah deprecated. Gunakan `openclaw doctor --fix` untuk
memindahkan `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders`, dan `webSearchProviders` ke bawah `contracts`; pemuatan
manifest normal tidak lagi memperlakukan field tingkat atas tersebut sebagai
kepemilikan capability.

## Manifest versus `package.json`

Kedua file tersebut memiliki fungsi yang berbeda:

| File                   | Gunakan untuk                                                                                                                      |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Discovery, validasi config, metadata pilihan auth, dan petunjuk UI yang harus ada sebelum kode Plugin dijalankan                  |
| `package.json`         | Metadata npm, instalasi dependensi, dan blok `openclaw` yang digunakan untuk entrypoint, gating instalasi, setup, atau metadata katalog |

Jika Anda tidak yakin metadata tertentu harus diletakkan di mana, gunakan aturan ini:

- jika OpenClaw harus mengetahuinya sebelum memuat kode Plugin, letakkan di `openclaw.plugin.json`
- jika itu terkait packaging, file entry, atau perilaku instalasi npm, letakkan di `package.json`

### Field `package.json` yang memengaruhi discovery

Beberapa metadata Plugin pra-runtime memang sengaja ditempatkan di `package.json` di bawah blok
`openclaw` alih-alih `openclaw.plugin.json`.

Contoh penting:

| Field                                                             | Artinya                                                                                                                                      |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Mendeklarasikan entrypoint Plugin native.                                                                                                    |
| `openclaw.setupEntry`                                             | Entrypoint ringan khusus setup yang digunakan saat onboarding dan startup channel yang ditunda.                                              |
| `openclaw.channel`                                                | Metadata katalog channel ringan seperti label, path dokumen, alias, dan copy pemilihan.                                                     |
| `openclaw.channel.configuredState`                                | Metadata pemeriksa configured-state ringan yang dapat menjawab "apakah setup hanya-env sudah ada?" tanpa memuat runtime channel penuh.      |
| `openclaw.channel.persistedAuthState`                             | Metadata pemeriksa auth tersimpan ringan yang dapat menjawab "apakah sudah ada yang login?" tanpa memuat runtime channel penuh.             |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Petunjuk instalasi/pembaruan untuk Plugin bundle dan Plugin yang dipublikasikan secara eksternal.                                            |
| `openclaw.install.defaultChoice`                                  | Jalur instalasi pilihan ketika tersedia beberapa sumber instalasi.                                                                           |
| `openclaw.install.minHostVersion`                                 | Versi host OpenClaw minimum yang didukung, menggunakan batas bawah semver seperti `>=2026.3.22`.                                            |
| `openclaw.install.allowInvalidConfigRecovery`                     | Mengizinkan jalur pemulihan reinstalasi Plugin bundle yang sempit ketika config tidak valid.                                                 |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Memungkinkan permukaan channel khusus setup dimuat sebelum Plugin channel penuh saat startup.                                                |

`openclaw.install.minHostVersion` diterapkan selama instalasi dan pemuatan registry
manifest. Nilai yang tidak valid akan ditolak; nilai yang valid tetapi lebih baru akan melewati
Plugin tersebut pada host yang lebih lama.

`openclaw.install.allowInvalidConfigRecovery` memang sengaja dibuat sempit. Field ini
tidak membuat config rusak apa pun menjadi dapat diinstal. Saat ini field ini hanya mengizinkan
alur instalasi untuk pulih dari kegagalan upgrade Plugin bundle basi tertentu, seperti
path Plugin bundle yang hilang atau entri `channels.<id>` basi untuk Plugin bundle yang sama.
Error config yang tidak terkait tetap memblokir instalasi dan mengarahkan operator
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

Gunakan ini ketika alur setup, doctor, atau configured-state memerlukan probe auth ya/tidak yang ringan
sebelum Plugin channel penuh dimuat. Ekspor target harus berupa fungsi kecil yang hanya membaca state tersimpan; jangan mengarahkannya melalui barrel runtime channel penuh.

`openclaw.channel.configuredState` mengikuti bentuk yang sama untuk pemeriksaan configured
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

Gunakan ini ketika sebuah channel dapat menjawab configured-state dari env atau input kecil non-runtime lainnya. Jika pemeriksaan membutuhkan resolusi config penuh atau runtime channel nyata, pertahankan logika tersebut di hook Plugin `config.hasConfiguredState`.

## Persyaratan JSON Schema

- **Setiap Plugin harus menyertakan JSON Schema**, bahkan jika tidak menerima config.
- Skema kosong dapat diterima (misalnya, `{ "type": "object", "additionalProperties": false }`).
- Skema divalidasi saat pembacaan/penulisan config, bukan saat runtime.

## Perilaku validasi

- Kunci `channels.*` yang tidak dikenal adalah **error**, kecuali ID channel tersebut dideklarasikan oleh
  manifest Plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny`, dan `plugins.slots.*`
  harus mereferensikan ID Plugin yang **dapat ditemukan**. ID yang tidak dikenal adalah **error**.
- Jika sebuah Plugin diinstal tetapi memiliki manifest atau skema yang rusak atau hilang,
  validasi gagal dan Doctor melaporkan error Plugin tersebut.
- Jika config Plugin ada tetapi Plugin tersebut **dinonaktifkan**, config tetap disimpan dan
  **peringatan** ditampilkan di Doctor + log.

Lihat [Configuration reference](/id/gateway/configuration) untuk skema `plugins.*` lengkap.

## Catatan

- Manifest **wajib untuk Plugin OpenClaw native**, termasuk pemuatan dari filesystem lokal.
- Runtime tetap memuat modul Plugin secara terpisah; manifest hanya digunakan untuk
  discovery + validasi.
- Manifest native diparse dengan JSON5, sehingga komentar, trailing comma, dan
  key tanpa tanda kutip diterima selama nilai akhirnya tetap berupa object.
- Hanya field manifest yang terdokumentasi yang dibaca oleh pemuat manifest. Hindari menambahkan
  key tingkat atas kustom di sini.
- `providerAuthEnvVars` adalah jalur metadata ringan untuk probe auth, validasi
  penanda env, dan permukaan auth provider serupa yang tidak seharusnya mem-boot runtime Plugin
  hanya untuk memeriksa nama env.
- `providerAuthAliases` memungkinkan varian provider menggunakan kembali env var auth,
  profil auth, auth berbasis config, dan pilihan onboarding kunci API milik provider lain
  tanpa meng-hardcode hubungan tersebut di core.
- `channelEnvVars` adalah jalur metadata ringan untuk fallback shell-env, prompt setup,
  dan permukaan channel serupa yang tidak seharusnya mem-boot runtime Plugin
  hanya untuk memeriksa nama env.
- `providerAuthChoices` adalah jalur metadata ringan untuk pemilih pilihan auth,
  resolusi `--auth-choice`, pemetaan provider pilihan, dan registrasi flag CLI
  onboarding sederhana sebelum runtime provider dimuat. Untuk metadata wizard runtime
  yang memerlukan kode provider, lihat
  [Provider runtime hooks](/id/plugins/architecture#provider-runtime-hooks).
- Jenis Plugin eksklusif dipilih melalui `plugins.slots.*`.
  - `kind: "memory"` dipilih oleh `plugins.slots.memory`.
  - `kind: "context-engine"` dipilih oleh `plugins.slots.contextEngine`
    (default: `legacy` bawaan).
- `channels`, `providers`, `cliBackends`, dan `skills` dapat dihilangkan ketika sebuah
  Plugin tidak membutuhkannya.
- Jika Plugin Anda bergantung pada modul native, dokumentasikan langkah build dan
  persyaratan allowlist package-manager apa pun (misalnya, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Terkait

- [Building Plugins](/id/plugins/building-plugins) — memulai dengan Plugin
- [Plugin Architecture](/id/plugins/architecture) — arsitektur internal
- [SDK Overview](/id/plugins/sdk-overview) — referensi SDK Plugin
