---
read_when:
    - Anda ingin menggunakan pembuatan video Runway di OpenClaw
    - Anda memerlukan penyiapan API key/env Runway
    - Anda ingin menjadikan Runway sebagai provider video default
summary: Penyiapan pembuatan video Runway di OpenClaw
title: Runway
x-i18n:
    generated_at: "2026-04-12T23:32:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb9a2d26687920544222b0769f314743af245629fd45b7f456c0161a47476176
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw menyertakan provider `runway` bawaan untuk pembuatan video hosted.

| Properti    | Nilai                                                             |
| ----------- | ----------------------------------------------------------------- |
| ID provider | `runway`                                                          |
| Auth        | `RUNWAYML_API_SECRET` (kanonis) atau `RUNWAY_API_KEY`             |
| API         | Pembuatan video berbasis task Runway (`GET /v1/tasks/{id}` polling) |

## Memulai

<Steps>
  <Step title="Setel API key">
    ```bash
    openclaw onboard --auth-choice runway-api-key
    ```
  </Step>
  <Step title="Setel Runway sebagai provider video default">
    ```bash
    openclaw config set agents.defaults.videoGenerationModel.primary "runway/gen4.5"
    ```
  </Step>
  <Step title="Buat video">
    Minta agen untuk membuat video. Runway akan digunakan secara otomatis.
  </Step>
</Steps>

## Mode yang didukung

| Mode           | Model              | Input referensi         |
| -------------- | ------------------ | ----------------------- |
| Teks-ke-video  | `gen4.5` (default) | Tidak ada               |
| Gambar-ke-video | `gen4.5`          | 1 gambar lokal atau jarak jauh |
| Video-ke-video | `gen4_aleph`       | 1 video lokal atau jarak jauh |

<Note>
Referensi gambar dan video lokal didukung melalui URI data. Proses khusus teks
saat ini mengekspos rasio aspek `16:9` dan `9:16`.
</Note>

<Warning>
Video-ke-video saat ini memerlukan `runway/gen4_aleph` secara spesifik.
</Warning>

## Konfigurasi

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Alias variabel environment">
    OpenClaw mengenali `RUNWAYML_API_SECRET` (kanonis) dan `RUNWAY_API_KEY`.
    Salah satu variabel dapat mengautentikasi provider Runway.
  </Accordion>

  <Accordion title="Polling task">
    Runway menggunakan API berbasis task. Setelah mengirim permintaan pembuatan, OpenClaw
    melakukan polling ke `GET /v1/tasks/{id}` sampai video siap. Tidak diperlukan
    konfigurasi tambahan untuk perilaku polling ini.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool bersama, pemilihan provider, dan perilaku async.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference#agent-defaults" icon="gear">
    Pengaturan default agen termasuk model pembuatan video.
  </Card>
</CardGroup>
