---
read_when:
    - Mengaktifkan text-to-speech untuk balasan
    - Mengonfigurasi penyedia atau batas TTS
    - Menggunakan perintah /tts
summary: Text-to-speech (TTS) untuk balasan keluar
title: Text-to-Speech
x-i18n:
    generated_at: "2026-04-08T06:01:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e0fbcaf61282733c134f682e05a71f94d2169c03a85131ce9ad233c71a1e533
    source_path: tools/tts.md
    workflow: 15
---

# Text-to-speech (TTS)

OpenClaw dapat mengubah balasan keluar menjadi audio menggunakan ElevenLabs, Microsoft, MiniMax, atau OpenAI.
Ini berfungsi di mana pun OpenClaw dapat mengirim audio.

## Layanan yang didukung

- **ElevenLabs** (penyedia utama atau fallback)
- **Microsoft** (penyedia utama atau fallback; implementasi bawaan saat ini menggunakan `node-edge-tts`)
- **MiniMax** (penyedia utama atau fallback; menggunakan API T2A v2)
- **OpenAI** (penyedia utama atau fallback; juga digunakan untuk ringkasan)

### Catatan speech Microsoft

Penyedia speech Microsoft bawaan saat ini menggunakan layanan
TTS neural online Microsoft Edge melalui library `node-edge-tts`. Ini adalah layanan yang dihosting (bukan
lokal), menggunakan endpoint Microsoft, dan tidak memerlukan kunci API.
`node-edge-tts` mengekspos opsi konfigurasi speech dan format output, tetapi
tidak semua opsi didukung oleh layanan. Konfigurasi lama dan input directive
yang menggunakan `edge` masih berfungsi dan dinormalisasi menjadi `microsoft`.

Karena jalur ini adalah layanan web publik tanpa SLA atau kuota yang dipublikasikan,
anggap ini sebagai upaya terbaik. Jika Anda membutuhkan batas dan dukungan yang terjamin, gunakan OpenAI
atau ElevenLabs.

## Kunci opsional

Jika Anda ingin menggunakan OpenAI, ElevenLabs, atau MiniMax:

- `ELEVENLABS_API_KEY` (atau `XI_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Speech Microsoft **tidak** memerlukan kunci API.

Jika beberapa penyedia dikonfigurasi, penyedia yang dipilih digunakan terlebih dahulu dan yang lain menjadi opsi fallback.
Auto-summary menggunakan `summaryModel` yang dikonfigurasi (atau `agents.defaults.model.primary`),
jadi penyedia tersebut juga harus diautentikasi jika Anda mengaktifkan ringkasan.

## Tautan layanan

- [Panduan OpenAI Text-to-Speech](https://platform.openai.com/docs/guides/text-to-speech)
- [Referensi API Audio OpenAI](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [Autentikasi ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [API MiniMax T2A v2](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Format output Microsoft Speech](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Apakah ini diaktifkan secara default?

Tidak. Auto‑TTS **nonaktif** secara default. Aktifkan di konfigurasi dengan
`messages.tts.auto` atau secara lokal dengan `/tts on`.

Ketika `messages.tts.provider` tidak disetel, OpenClaw memilih penyedia
speech pertama yang dikonfigurasi dalam urutan auto-select registri.

## Konfigurasi

Konfigurasi TTS berada di bawah `messages.tts` dalam `openclaw.json`.
Skema lengkap ada di [Konfigurasi gateway](/id/gateway/configuration).

### Konfigurasi minimal (aktifkan + penyedia)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI sebagai utama dengan fallback ElevenLabs

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft sebagai utama (tanpa kunci API)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax sebagai utama

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### Nonaktifkan speech Microsoft

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### Batas khusus + path preferensi

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### Hanya balas dengan audio setelah pesan suara masuk

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Nonaktifkan auto-summary untuk balasan panjang

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Lalu jalankan:

```
/tts summary off
```

### Catatan tentang field

- `auto`: mode auto‑TTS (`off`, `always`, `inbound`, `tagged`).
  - `inbound` hanya mengirim audio setelah pesan suara masuk.
  - `tagged` hanya mengirim audio ketika balasan menyertakan tag `[[tts]]`.
- `enabled`: toggle lama (doctor memigrasikan ini ke `auto`).
- `mode`: `"final"` (default) atau `"all"` (termasuk balasan tool/block).
- `provider`: id penyedia speech seperti `"elevenlabs"`, `"microsoft"`, `"minimax"`, atau `"openai"` (fallback berjalan otomatis).
- Jika `provider` **tidak disetel**, OpenClaw menggunakan penyedia speech pertama yang dikonfigurasi dalam urutan auto-select registri.
- `provider: "edge"` lama masih berfungsi dan dinormalisasi menjadi `microsoft`.
- `summaryModel`: model murah opsional untuk auto-summary; default ke `agents.defaults.model.primary`.
  - Menerima `provider/model` atau alias model yang dikonfigurasi.
- `modelOverrides`: mengizinkan model mengeluarkan directive TTS (aktif secara default).
  - `allowProvider` default ke `false` (peralihan penyedia bersifat opt-in).
- `providers.<id>`: pengaturan milik penyedia yang dikunci dengan id penyedia speech.
- Blok penyedia langsung lama (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) dimigrasikan otomatis ke `messages.tts.providers.<id>` saat dimuat.
- `maxTextLength`: batas keras untuk input TTS (karakter). `/tts audio` gagal jika terlampaui.
- `timeoutMs`: batas waktu permintaan (ms).
- `prefsPath`: menimpa path JSON preferensi lokal (penyedia/batas/ringkasan).
- Nilai `apiKey` fallback ke env vars (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: timpa URL dasar API ElevenLabs.
- `providers.openai.baseUrl`: timpa endpoint TTS OpenAI.
  - Urutan resolusi: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Nilai non-default diperlakukan sebagai endpoint TTS yang kompatibel dengan OpenAI, sehingga nama model dan suara kustom diterima.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = normal)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: ISO 639-1 2 huruf (misalnya `en`, `de`)
- `providers.elevenlabs.seed`: bilangan bulat `0..4294967295` (determinisme upaya terbaik)
- `providers.minimax.baseUrl`: timpa URL dasar API MiniMax (default `https://api.minimax.io`, env: `MINIMAX_API_HOST`).
- `providers.minimax.model`: model TTS (default `speech-2.8-hd`, env: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: pengenal suara (default `English_expressive_narrator`, env: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: kecepatan pemutaran `0.5..2.0` (default 1.0).
- `providers.minimax.vol`: volume `(0, 10]` (default 1.0; harus lebih besar dari 0).
- `providers.minimax.pitch`: pergeseran pitch `-12..12` (default 0).
- `providers.microsoft.enabled`: izinkan penggunaan speech Microsoft (default `true`; tanpa kunci API).
- `providers.microsoft.voice`: nama suara neural Microsoft (misalnya `en-US-MichelleNeural`).
- `providers.microsoft.lang`: kode bahasa (misalnya `en-US`).
- `providers.microsoft.outputFormat`: format output Microsoft (misalnya `audio-24khz-48kbitrate-mono-mp3`).
  - Lihat format output Microsoft Speech untuk nilai yang valid; tidak semua format didukung oleh transport bawaan berbasis Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: string persen (misalnya `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: tulis subtitle JSON di samping file audio.
- `providers.microsoft.proxy`: URL proxy untuk permintaan speech Microsoft.
- `providers.microsoft.timeoutMs`: timpa batas waktu permintaan (ms).
- `edge.*`: alias lama untuk pengaturan Microsoft yang sama.

## Override berbasis model (aktif secara default)

Secara default, model **dapat** mengeluarkan directive TTS untuk satu balasan.
Ketika `messages.tts.auto` adalah `tagged`, directive ini wajib untuk memicu audio.

Saat diaktifkan, model dapat mengeluarkan directive `[[tts:...]]` untuk menimpa suara
untuk satu balasan, ditambah blok `[[tts:text]]...[[/tts:text]]` opsional untuk
memberikan tag ekspresif (tawa, petunjuk bernyanyi, dan sebagainya) yang seharusnya hanya muncul di
audio.

Directive `provider=...` diabaikan kecuali `modelOverrides.allowProvider: true`.

Contoh payload balasan:

```
Ini dia.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](tertawa) Bacakan lagunya sekali lagi.[[/tts:text]]
```

Kunci directive yang tersedia (saat diaktifkan):

- `provider` (id penyedia speech terdaftar, misalnya `openai`, `elevenlabs`, `minimax`, atau `microsoft`; memerlukan `allowProvider: true`)
- `voice` (suara OpenAI) atau `voiceId` (ElevenLabs / MiniMax)
- `model` (model TTS OpenAI, id model ElevenLabs, atau model MiniMax)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (volume MiniMax, 0-10)
- `pitch` (pitch MiniMax, -12 hingga 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Nonaktifkan semua override model:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

Allowlist opsional (aktifkan peralihan penyedia sambil tetap menjaga knob lain dapat dikonfigurasi):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## Preferensi per pengguna

Perintah slash menulis override lokal ke `prefsPath` (default:
`~/.openclaw/settings/tts.json`, timpa dengan `OPENCLAW_TTS_PREFS` atau
`messages.tts.prefsPath`).

Field yang disimpan:

- `enabled`
- `provider`
- `maxLength` (ambang ringkasan; default 1500 karakter)
- `summarize` (default `true`)

Ini menimpa `messages.tts.*` untuk host tersebut.

## Format output (tetap)

- **Feishu / Matrix / Telegram / WhatsApp**: pesan suara Opus (`opus_48000_64` dari ElevenLabs, `opus` dari OpenAI).
  - 48kHz / 64kbps adalah kompromi yang baik untuk pesan suara.
- **Kanal lain**: MP3 (`mp3_44100_128` dari ElevenLabs, `mp3` dari OpenAI).
  - 44.1kHz / 128kbps adalah keseimbangan default untuk kejernihan ucapan.
- **MiniMax**: MP3 (model `speech-2.8-hd`, sample rate 32kHz). Format voice note tidak didukung secara native; gunakan OpenAI atau ElevenLabs untuk pesan suara Opus yang terjamin.
- **Microsoft**: menggunakan `microsoft.outputFormat` (default `audio-24khz-48kbitrate-mono-mp3`).
  - Transport bawaan menerima `outputFormat`, tetapi tidak semua format tersedia dari layanan.
  - Nilai format output mengikuti format output Microsoft Speech (termasuk Ogg/WebM Opus).
  - Telegram `sendVoice` menerima OGG/MP3/M4A; gunakan OpenAI/ElevenLabs jika Anda membutuhkan
    pesan suara Opus yang terjamin.
  - Jika format output Microsoft yang dikonfigurasi gagal, OpenClaw mencoba lagi dengan MP3.

Format output OpenAI/ElevenLabs ditetapkan per kanal (lihat di atas).

## Perilaku Auto-TTS

Saat diaktifkan, OpenClaw:

- melewati TTS jika balasan sudah berisi media atau directive `MEDIA:`.
- melewati balasan yang sangat pendek (< 10 karakter).
- meringkas balasan panjang saat diaktifkan menggunakan `agents.defaults.model.primary` (atau `summaryModel`).
- melampirkan audio yang dihasilkan ke balasan.

Jika balasan melebihi `maxLength` dan ringkasan nonaktif (atau tidak ada kunci API untuk
model ringkasan), audio
dilewati dan balasan teks normal dikirim.

## Diagram alur

```
Balasan -> TTS diaktifkan?
  tidak -> kirim teks
  ya    -> ada media / MEDIA: / pendek?
            ya    -> kirim teks
            tidak -> panjang > batas?
                      tidak -> TTS -> lampirkan audio
                      ya    -> ringkasan diaktifkan?
                                tidak -> kirim teks
                                ya    -> ringkas (summaryModel atau agents.defaults.model.primary)
                                          -> TTS -> lampirkan audio
```

## Penggunaan perintah slash

Ada satu perintah: `/tts`.
Lihat [Perintah slash](/id/tools/slash-commands) untuk detail pengaktifannya.

Catatan Discord: `/tts` adalah perintah bawaan Discord, jadi OpenClaw mendaftarkan
`/voice` sebagai perintah native di sana. Teks `/tts ...` tetap berfungsi.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

Catatan:

- Perintah memerlukan pengirim yang diotorisasi (aturan allowlist/owner tetap berlaku).
- `commands.text` atau pendaftaran perintah native harus diaktifkan.
- Konfigurasi `messages.tts.auto` menerima `off|always|inbound|tagged`.
- `/tts on` menulis preferensi TTS lokal menjadi `always`; `/tts off` menulisnya menjadi `off`.
- Gunakan konfigurasi jika Anda ingin default `inbound` atau `tagged`.
- `limit` dan `summary` disimpan dalam preferensi lokal, bukan konfigurasi utama.
- `/tts audio` menghasilkan balasan audio satu kali (tidak mengaktifkan TTS).
- `/tts status` mencakup visibilitas fallback untuk percobaan terbaru:
  - fallback berhasil: `Fallback: <primary> -> <used>` ditambah `Attempts: ...`
  - gagal: `Error: ...` ditambah `Attempts: ...`
  - diagnostik terperinci: `Attempt details: provider:outcome(reasonCode) latency`
- Kegagalan API OpenAI dan ElevenLabs kini mencakup detail error penyedia yang telah di-parse dan request id (saat dikembalikan oleh penyedia), yang ditampilkan dalam error/log TTS.

## Tool agen

Tool `tts` mengubah teks menjadi speech dan mengembalikan lampiran audio untuk
pengiriman balasan. Ketika kanalnya adalah Feishu, Matrix, Telegram, atau WhatsApp,
audio dikirim sebagai pesan suara, bukan sebagai lampiran file.

## Gateway RPC

Metode gateway:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
