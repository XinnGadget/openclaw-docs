---
read_when:
    - Anda ingin menggunakan model Google Gemini dengan OpenClaw
    - Anda memerlukan alur autentikasi kunci API atau OAuth
summary: Penyiapan Google Gemini (kunci API + OAuth, pembuatan gambar, pemahaman media, pencarian web)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-08T09:12:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: fad2ff68987301bd86145fa6e10de8c7b38d5bd5dbcd13db9c883f7f5b9a4e01
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

plugin Google menyediakan akses ke model Gemini melalui Google AI Studio, serta
pembuatan gambar, pemahaman media (gambar/audio/video), dan pencarian web melalui
Gemini Grounding.

- Penyedia: `google`
- Autentikasi: `GEMINI_API_KEY` atau `GOOGLE_API_KEY`
- API: Google Gemini API
- Penyedia alternatif: `google-gemini-cli` (OAuth)

## Mulai cepat

1. Atur kunci API:

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. Atur model default:

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## Contoh non-interaktif

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## OAuth (Gemini CLI)

Penyedia alternatif `google-gemini-cli` menggunakan PKCE OAuth alih-alih kunci API.
Ini adalah integrasi tidak resmi; beberapa pengguna melaporkan adanya
pembatasan akun. Gunakan dengan risiko Anda sendiri.

- Model default: `google-gemini-cli/gemini-3-flash-preview`
- Alias: `gemini-cli`
- Prasyarat instalasi: Gemini CLI lokal tersedia sebagai `gemini`
  - Homebrew: `brew install gemini-cli`
  - npm: `npm install -g @google/gemini-cli`
- Login:

```bash
openclaw models auth login --provider google-gemini-cli --set-default
```

Variabel lingkungan:

- `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
- `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

(Atau varian `GEMINI_CLI_*`.)

Jika permintaan OAuth Gemini CLI gagal setelah login, atur
`GOOGLE_CLOUD_PROJECT` atau `GOOGLE_CLOUD_PROJECT_ID` pada host gateway lalu
coba lagi.

Jika login gagal sebelum alur browser dimulai, pastikan perintah `gemini` lokal
sudah terinstal dan tersedia di `PATH`. OpenClaw mendukung instalasi Homebrew
dan instalasi npm global, termasuk tata letak umum Windows/npm.

Catatan penggunaan JSON Gemini CLI:

- Teks balasan berasal dari kolom JSON `response` milik CLI.
- Penggunaan akan fallback ke `stats` saat CLI membiarkan `usage` kosong.
- `stats.cached` dinormalisasi menjadi OpenClaw `cacheRead`.
- Jika `stats.input` tidak ada, OpenClaw menurunkan token input dari
  `stats.input_tokens - stats.cached`.

## Kemampuan

| Kemampuan              | Didukung          |
| ---------------------- | ----------------- |
| Penyelesaian chat      | Ya                |
| Pembuatan gambar       | Ya                |
| Pembuatan musik        | Ya                |
| Pemahaman gambar       | Ya                |
| Transkripsi audio      | Ya                |
| Pemahaman video        | Ya                |
| Pencarian web (Grounding) | Ya             |
| Thinking/reasoning     | Ya (Gemini 3.1+)  |
| Model Gemma 4          | Ya                |

Model Gemma 4 (misalnya `gemma-4-26b-a4b-it`) mendukung mode thinking. OpenClaw menulis ulang `thinkingBudget` menjadi `thinkingLevel` Google yang didukung untuk Gemma 4. Menyetel thinking ke `off` akan mempertahankan thinking tetap dinonaktifkan alih-alih memetakannya ke `MINIMAL`.

## Penggunaan ulang cache Gemini langsung

Untuk eksekusi API Gemini langsung (`api: "google-generative-ai"`), OpenClaw kini
meneruskan handle `cachedContent` yang dikonfigurasi ke permintaan Gemini.

- Konfigurasikan parameter per model atau global dengan
  `cachedContent` atau `cached_content` lama
- Jika keduanya ada, `cachedContent` yang diprioritaskan
- Contoh nilai: `cachedContents/prebuilt-context`
- Penggunaan cache-hit Gemini dinormalisasi menjadi OpenClaw `cacheRead` dari
  `cachedContentTokenCount` upstream

Contoh:

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## Pembuatan gambar

Penyedia pembuatan gambar `google` bawaan default ke
`google/gemini-3.1-flash-image-preview`.

- Juga mendukung `google/gemini-3-pro-image-preview`
- Generate: hingga 4 gambar per permintaan
- Mode edit: diaktifkan, hingga 5 gambar input
- Kontrol geometri: `size`, `aspectRatio`, dan `resolution`

Penyedia `google-gemini-cli` yang hanya mendukung OAuth adalah surface inferensi
teks yang terpisah. Pembuatan gambar, pemahaman media, dan Gemini Grounding tetap
berada pada id penyedia `google`.

Untuk menggunakan Google sebagai penyedia gambar default:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

Lihat [Image Generation](/id/tools/image-generation) untuk parameter tool bersama,
pemilihan penyedia, dan perilaku failover.

## Pembuatan video

plugin `google` bawaan juga mendaftarkan pembuatan video melalui tool bersama
`video_generate`.

- Model video default: `google/veo-3.1-fast-generate-preview`
- Mode: text-to-video, image-to-video, dan alur referensi satu video
- Mendukung `aspectRatio`, `resolution`, dan `audio`
- Batas durasi saat ini: **4 hingga 8 detik**

Untuk menggunakan Google sebagai penyedia video default:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

Lihat [Video Generation](/id/tools/video-generation) untuk parameter tool bersama,
pemilihan penyedia, dan perilaku failover.

## Pembuatan musik

plugin `google` bawaan juga mendaftarkan pembuatan musik melalui tool bersama
`music_generate`.

- Model musik default: `google/lyria-3-clip-preview`
- Juga mendukung `google/lyria-3-pro-preview`
- Kontrol prompt: `lyrics` dan `instrumental`
- Format keluaran: `mp3` secara default, serta `wav` pada `google/lyria-3-pro-preview`
- Input referensi: hingga 10 gambar
- Eksekusi berbasis sesi dilepas melalui alur tugas/status bersama, termasuk `action: "status"`

Untuk menggunakan Google sebagai penyedia musik default:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

Lihat [Music Generation](/id/tools/music-generation) untuk parameter tool bersama,
pemilihan penyedia, dan perilaku failover.

## Catatan lingkungan

Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `GEMINI_API_KEY`
tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui
`env.shellEnv`).
