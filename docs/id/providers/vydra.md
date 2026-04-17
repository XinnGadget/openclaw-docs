---
read_when:
    - Anda ingin pembuatan media Vydra di OpenClaw
    - Anda memerlukan panduan setup API key Vydra
summary: Gunakan gambar, video, dan ucapan Vydra di OpenClaw
title: Vydra
x-i18n:
    generated_at: "2026-04-12T23:33:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab623d14b656ce0b68d648a6393fcee3bb880077d6583e0d5c1012e91757f20e
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

Plugin Vydra bawaan menambahkan:

- Pembuatan gambar melalui `vydra/grok-imagine`
- Pembuatan video melalui `vydra/veo3` dan `vydra/kling`
- Sintesis ucapan melalui route TTS Vydra yang didukung ElevenLabs

OpenClaw menggunakan `VYDRA_API_KEY` yang sama untuk ketiga kapabilitas tersebut.

<Warning>
Gunakan `https://www.vydra.ai/api/v1` sebagai base URL.

Host apex Vydra (`https://vydra.ai/api/v1`) saat ini mengalihkan ke `www`. Beberapa klien HTTP menghapus `Authorization` pada pengalihan lintas host itu, yang membuat API key yang valid tampak seperti kegagalan auth yang menyesatkan. Plugin bawaan menggunakan base URL `www` secara langsung untuk menghindarinya.
</Warning>

## Setup

<Steps>
  <Step title="Jalankan onboarding interaktif">
    ```bash
    openclaw onboard --auth-choice vydra-api-key
    ```

    Atau atur env var secara langsung:

    ```bash
    export VYDRA_API_KEY="vydra_live_..."
    ```

  </Step>
  <Step title="Pilih kapabilitas default">
    Pilih satu atau lebih kapabilitas di bawah ini (gambar, video, atau ucapan) dan terapkan konfigurasi yang sesuai.
  </Step>
</Steps>

## Kapabilitas

<AccordionGroup>
  <Accordion title="Pembuatan gambar">
    Model gambar default:

    - `vydra/grok-imagine`

    Atur sebagai provider gambar default:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "vydra/grok-imagine",
          },
        },
      },
    }
    ```

    Dukungan bawaan saat ini hanya untuk text-to-image. Route edit yang di-host Vydra mengharapkan URL gambar jarak jauh, dan OpenClaw belum menambahkan bridge upload khusus Vydra di plugin bawaan.

    <Note>
    Lihat [Pembuatan Gambar](/id/tools/image-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
    </Note>

  </Accordion>

  <Accordion title="Pembuatan video">
    Model video yang terdaftar:

    - `vydra/veo3` untuk text-to-video
    - `vydra/kling` untuk image-to-video

    Atur Vydra sebagai provider video default:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "vydra/veo3",
          },
        },
      },
    }
    ```

    Catatan:

    - `vydra/veo3` dibundel hanya sebagai text-to-video.
    - `vydra/kling` saat ini memerlukan referensi URL gambar jarak jauh. Upload file lokal ditolak sejak awal.
    - Route HTTP `kling` Vydra saat ini tidak konsisten mengenai apakah membutuhkan `image_url` atau `video_url`; provider bawaan memetakan URL gambar jarak jauh yang sama ke kedua field.
    - Plugin bawaan bersikap konservatif dan tidak meneruskan knob style yang tidak terdokumentasi seperti rasio aspek, resolusi, watermark, atau audio yang dihasilkan.

    <Note>
    Lihat [Pembuatan Video](/id/tools/video-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
    </Note>

  </Accordion>

  <Accordion title="Test live video">
    Cakupan live khusus provider:

    ```bash
    OPENCLAW_LIVE_TEST=1 \
    OPENCLAW_LIVE_VYDRA_VIDEO=1 \
    pnpm test:live -- extensions/vydra/vydra.live.test.ts
    ```

    File live Vydra bawaan kini mencakup:

    - `vydra/veo3` text-to-video
    - `vydra/kling` image-to-video menggunakan URL gambar jarak jauh

    Override fixture gambar jarak jauh bila diperlukan:

    ```bash
    export OPENCLAW_LIVE_VYDRA_KLING_IMAGE_URL="https://example.com/reference.png"
    ```

  </Accordion>

  <Accordion title="Sintesis ucapan">
    Atur Vydra sebagai provider ucapan:

    ```json5
    {
      messages: {
        tts: {
          provider: "vydra",
          providers: {
            vydra: {
              apiKey: "${VYDRA_API_KEY}",
              voiceId: "21m00Tcm4TlvDq8ikWAM",
            },
          },
        },
      },
    }
    ```

    Default:

    - Model: `elevenlabs/tts`
    - Id suara: `21m00Tcm4TlvDq8ikWAM`

    Plugin bawaan saat ini mengekspos satu suara default yang sudah teruji baik dan mengembalikan file audio MP3.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Direktori provider" href="/id/providers/index" icon="list">
    Jelajahi semua provider yang tersedia.
  </Card>
  <Card title="Pembuatan gambar" href="/id/tools/image-generation" icon="image">
    Parameter tool gambar bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference#agent-defaults" icon="gear">
    Default agen dan konfigurasi model.
  </Card>
</CardGroup>
