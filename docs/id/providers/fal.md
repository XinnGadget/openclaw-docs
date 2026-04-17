---
read_when:
    - Anda ingin menggunakan pembuatan gambar fal di OpenClaw
    - Anda memerlukan alur auth `FAL_KEY`
    - Anda ingin default fal untuk `image_generate` atau `video_generate`
summary: setup pembuatan gambar dan video fal di OpenClaw
title: fal
x-i18n:
    generated_at: "2026-04-12T23:30:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: ff275233179b4808d625383efe04189ad9e92af09944ba39f1e953e77378e347
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw menyediakan provider `fal` bawaan untuk pembuatan gambar dan video terhosting.

| Properti | Nilai                                                         |
| -------- | ------------------------------------------------------------- |
| Provider | `fal`                                                         |
| Auth     | `FAL_KEY` (kanonis; `FAL_API_KEY` juga berfungsi sebagai fallback) |
| API      | endpoint model fal                                            |

## Memulai

<Steps>
  <Step title="Tetapkan kunci API">
    ```bash
    openclaw onboard --auth-choice fal-api-key
    ```
  </Step>
  <Step title="Tetapkan model gambar default">
    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "fal/fal-ai/flux/dev",
          },
        },
      },
    }
    ```
  </Step>
</Steps>

## Pembuatan gambar

Provider image-generation `fal` bawaan secara default menggunakan
`fal/fal-ai/flux/dev`.

| Capability     | Nilai                     |
| -------------- | ------------------------- |
| Max images     | 4 per permintaan          |
| Edit mode      | Diaktifkan, 1 gambar referensi |
| Size overrides | Didukung                  |
| Aspect ratio   | Didukung                  |
| Resolution     | Didukung                  |

<Warning>
Endpoint edit gambar fal **tidak** mendukung override `aspectRatio`.
</Warning>

Untuk menggunakan fal sebagai provider gambar default:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## Pembuatan video

Provider video-generation `fal` bawaan secara default menggunakan
`fal/fal-ai/minimax/video-01-live`.

| Capability | Nilai                                                        |
| ---------- | ------------------------------------------------------------ |
| Modes      | Teks-ke-video, referensi satu gambar                         |
| Runtime    | Alur submit/status/result berbasis antrean untuk job berdurasi panjang |

<AccordionGroup>
  <Accordion title="Model video yang tersedia">
    **Video-agent HeyGen:**

    - `fal/fal-ai/heygen/v2/video-agent`

    **Seedance 2.0:**

    - `fal/bytedance/seedance-2.0/fast/text-to-video`
    - `fal/bytedance/seedance-2.0/fast/image-to-video`
    - `fal/bytedance/seedance-2.0/text-to-video`
    - `fal/bytedance/seedance-2.0/image-to-video`

  </Accordion>

  <Accordion title="Contoh config Seedance 2.0">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Contoh config video-agent HeyGen">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "fal/fal-ai/heygen/v2/video-agent",
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

<Tip>
Gunakan `openclaw models list --provider fal` untuk melihat daftar lengkap model fal
yang tersedia, termasuk entri yang baru ditambahkan.
</Tip>

## Terkait

<CardGroup cols={2}>
  <Card title="Pembuatan gambar" href="/id/tools/image-generation" icon="image">
    Parameter tool gambar bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference#agent-defaults" icon="gear">
    Default agen termasuk pemilihan model gambar dan video.
  </Card>
</CardGroup>
