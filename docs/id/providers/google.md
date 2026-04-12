---
read_when:
    - Anda ingin menggunakan model Google Gemini dengan OpenClaw
    - Anda memerlukan alur auth API key atau OAuth
summary: Penyiapan Google Gemini (API key + OAuth, pembuatan gambar, pemahaman media, pencarian web)
title: Google (Gemini)
x-i18n:
    generated_at: "2026-04-12T23:30:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64b848add89061b208a5d6b19d206c433cace5216a0ca4b63d56496aecbde452
    source_path: providers/google.md
    workflow: 15
---

# Google (Gemini)

Plugin Google menyediakan akses ke model Gemini melalui Google AI Studio, serta
pembuatan gambar, pemahaman media (gambar/audio/video), dan pencarian web melalui
Gemini Grounding.

- Provider: `google`
- Auth: `GEMINI_API_KEY` atau `GOOGLE_API_KEY`
- API: Google Gemini API
- Provider alternatif: `google-gemini-cli` (OAuth)

## Memulai

Pilih metode auth yang Anda inginkan dan ikuti langkah penyiapannya.

<Tabs>
  <Tab title="API key">
    **Terbaik untuk:** akses API Gemini standar melalui Google AI Studio.

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice gemini-api-key
        ```

        Atau berikan key secara langsung:

        ```bash
        openclaw onboard --non-interactive \
          --mode local \
          --auth-choice gemini-api-key \
          --gemini-api-key "$GEMINI_API_KEY"
        ```
      </Step>
      <Step title="Setel model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "google/gemini-3.1-pro-preview" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi model tersedia">
        ```bash
        openclaw models list --provider google
        ```
      </Step>
    </Steps>

    <Tip>
    Variabel environment `GEMINI_API_KEY` dan `GOOGLE_API_KEY` sama-sama didukung. Gunakan salah satu yang sudah Anda konfigurasikan.
    </Tip>

  </Tab>

  <Tab title="Gemini CLI (OAuth)">
    **Terbaik untuk:** menggunakan kembali login Gemini CLI yang sudah ada melalui PKCE OAuth alih-alih API key terpisah.

    <Warning>
    Provider `google-gemini-cli` adalah integrasi tidak resmi. Beberapa pengguna
    melaporkan pembatasan akun saat menggunakan OAuth dengan cara ini. Gunakan dengan risiko Anda sendiri.
    </Warning>

    <Steps>
      <Step title="Instal Gemini CLI">
        Perintah `gemini` lokal harus tersedia di `PATH`.

        ```bash
        # Homebrew
        brew install gemini-cli

        # atau npm
        npm install -g @google/gemini-cli
        ```

        OpenClaw mendukung instalasi Homebrew maupun instalasi npm global, termasuk
        tata letak Windows/npm yang umum.
      </Step>
      <Step title="Masuk melalui OAuth">
        ```bash
        openclaw models auth login --provider google-gemini-cli --set-default
        ```
      </Step>
      <Step title="Verifikasi model tersedia">
        ```bash
        openclaw models list --provider google-gemini-cli
        ```
      </Step>
    </Steps>

    - Model default: `google-gemini-cli/gemini-3-flash-preview`
    - Alias: `gemini-cli`

    **Variabel environment:**

    - `OPENCLAW_GEMINI_OAUTH_CLIENT_ID`
    - `OPENCLAW_GEMINI_OAUTH_CLIENT_SECRET`

    (Atau varian `GEMINI_CLI_*`.)

    <Note>
    Jika permintaan OAuth Gemini CLI gagal setelah login, setel `GOOGLE_CLOUD_PROJECT` atau
    `GOOGLE_CLOUD_PROJECT_ID` pada host gateway lalu coba lagi.
    </Note>

    <Note>
    Jika login gagal sebelum alur browser dimulai, pastikan perintah `gemini` lokal
    terinstal dan ada di `PATH`.
    </Note>

    Provider `google-gemini-cli` yang khusus OAuth adalah
    surface inferensi teks yang terpisah. Pembuatan gambar, pemahaman media, dan Gemini Grounding tetap berada pada
    id provider `google`.

  </Tab>
</Tabs>

## Kemampuan

| Capability             | Supported         |
| ---------------------- | ----------------- |
| Chat completions       | Ya                |
| Pembuatan gambar       | Ya                |
| Pembuatan musik        | Ya                |
| Pemahaman gambar       | Ya                |
| Transkripsi audio      | Ya                |
| Pemahaman video        | Ya                |
| Pencarian web (Grounding) | Ya             |
| Thinking/reasoning     | Ya (Gemini 3.1+)  |
| Model Gemma 4          | Ya                |

<Tip>
Model Gemma 4 (misalnya `gemma-4-26b-a4b-it`) mendukung mode thinking. OpenClaw
menulis ulang `thinkingBudget` ke `thinkingLevel` Google yang didukung untuk Gemma 4.
Menyetel thinking ke `off` mempertahankan thinking nonaktif alih-alih memetakannya ke
`MINIMAL`.
</Tip>

## Pembuatan gambar

Provider pembuatan gambar `google` bawaan secara default menggunakan
`google/gemini-3.1-flash-image-preview`.

- Juga mendukung `google/gemini-3-pro-image-preview`
- Generate: hingga 4 gambar per permintaan
- Mode edit: aktif, hingga 5 gambar input
- Kontrol geometri: `size`, `aspectRatio`, dan `resolution`

Untuk menggunakan Google sebagai provider gambar default:

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

<Note>
Lihat [Image Generation](/id/tools/image-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

## Pembuatan video

Plugin `google` bawaan juga mendaftarkan pembuatan video melalui tool bersama
`video_generate`.

- Model video default: `google/veo-3.1-fast-generate-preview`
- Mode: text-to-video, image-to-video, dan alur referensi satu video
- Mendukung `aspectRatio`, `resolution`, dan `audio`
- Batas durasi saat ini: **4 hingga 8 detik**

Untuk menggunakan Google sebagai provider video default:

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

<Note>
Lihat [Video Generation](/id/tools/video-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

## Pembuatan musik

Plugin `google` bawaan juga mendaftarkan pembuatan musik melalui tool bersama
`music_generate`.

- Model musik default: `google/lyria-3-clip-preview`
- Juga mendukung `google/lyria-3-pro-preview`
- Kontrol prompt: `lyrics` dan `instrumental`
- Format output: `mp3` secara default, ditambah `wav` pada `google/lyria-3-pro-preview`
- Input referensi: hingga 10 gambar
- Eksekusi berbasis sesi dilepas melalui alur task/status bersama, termasuk `action: "status"`

Untuk menggunakan Google sebagai provider musik default:

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

<Note>
Lihat [Music Generation](/id/tools/music-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Reuse cache Gemini langsung">
    Untuk eksekusi API Gemini langsung (`api: "google-generative-ai"`), OpenClaw
    meneruskan handle `cachedContent` yang dikonfigurasi ke permintaan Gemini.

    - Konfigurasikan parameter per-model atau global dengan
      `cachedContent` atau `cached_content` lama
    - Jika keduanya ada, `cachedContent` yang diprioritaskan
    - Nilai contoh: `cachedContents/prebuilt-context`
    - Penggunaan cache-hit Gemini dinormalisasi ke `cacheRead` OpenClaw dari
      `cachedContentTokenCount` upstream

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

  </Accordion>

  <Accordion title="Catatan penggunaan JSON Gemini CLI">
    Saat menggunakan provider OAuth `google-gemini-cli`, OpenClaw menormalisasi
    output JSON CLI sebagai berikut:

    - Teks balasan berasal dari field JSON `response` milik CLI.
    - Penggunaan fallback ke `stats` saat CLI membiarkan `usage` kosong.
    - `stats.cached` dinormalisasi ke `cacheRead` OpenClaw.
    - Jika `stats.input` tidak ada, OpenClaw menurunkan token input dari
      `stats.input_tokens - stats.cached`.

  </Accordion>

  <Accordion title="Environment dan penyiapan daemon">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `GEMINI_API_KEY`
    tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pembuatan gambar" href="/id/tools/image-generation" icon="image">
    Parameter tool gambar bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan musik" href="/id/tools/music-generation" icon="music">
    Parameter tool musik bersama dan pemilihan provider.
  </Card>
</CardGroup>
