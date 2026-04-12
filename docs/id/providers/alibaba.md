---
read_when:
    - Anda ingin menggunakan generasi video Wan Alibaba di OpenClaw
    - Anda memerlukan penyiapan kunci API Model Studio atau DashScope untuk generasi video
summary: Generasi video Wan Alibaba Model Studio di OpenClaw
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-12T23:28:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: a6e97d929952cdba7740f5ab3f6d85c18286b05596a4137bf80bbc8b54f32662
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw menyediakan provider generasi video `alibaba` bawaan untuk model Wan di
Alibaba Model Studio / DashScope.

- Provider: `alibaba`
- Autentikasi yang disarankan: `MODELSTUDIO_API_KEY`
- Juga diterima: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: generasi video asinkron DashScope / Model Studio

## Memulai

<Steps>
  <Step title="Tetapkan kunci API">
    ```bash
    openclaw onboard --auth-choice qwen-standard-api-key
    ```
  </Step>
  <Step title="Tetapkan model video default">
    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "alibaba/wan2.6-t2v",
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Verifikasi bahwa provider tersedia">
    ```bash
    openclaw models list --provider alibaba
    ```
  </Step>
</Steps>

<Note>
Kunci autentikasi apa pun yang diterima (`MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`, `QWEN_API_KEY`) akan berfungsi. Pilihan onboarding `qwen-standard-api-key` mengonfigurasi kredensial DashScope bersama.
</Note>

## Model Wan bawaan

Provider `alibaba` bawaan saat ini mendaftarkan:

| Model ref                  | Mode                           |
| -------------------------- | ------------------------------ |
| `alibaba/wan2.6-t2v`       | Teks-ke-video                  |
| `alibaba/wan2.6-i2v`       | Gambar-ke-video                |
| `alibaba/wan2.6-r2v`       | Referensi-ke-video             |
| `alibaba/wan2.6-r2v-flash` | Referensi-ke-video (cepat)     |
| `alibaba/wan2.7-r2v`       | Referensi-ke-video             |

## Batasan saat ini

| Parameter             | Batas                                                     |
| --------------------- | --------------------------------------------------------- |
| Video output          | Hingga **1** per permintaan                               |
| Gambar input          | Hingga **1**                                              |
| Video input           | Hingga **4**                                              |
| Durasi                | Hingga **10 detik**                                       |
| Kontrol yang didukung | `size`, `aspectRatio`, `resolution`, `audio`, `watermark` |
| Gambar/video referensi | Hanya URL `http(s)` jarak jauh                           |

<Warning>
Mode gambar/video referensi saat ini memerlukan **URL http(s) jarak jauh**. Path file lokal tidak didukung untuk input referensi.
</Warning>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Hubungan dengan Qwen">
    Provider `qwen` bawaan juga menggunakan endpoint DashScope yang dihosting Alibaba untuk
    generasi video Wan. Gunakan:

    - `qwen/...` saat Anda menginginkan permukaan provider Qwen kanonis
    - `alibaba/...` saat Anda menginginkan permukaan video Wan langsung milik vendor

    Lihat [dokumentasi provider Qwen](/id/providers/qwen) untuk detail lebih lanjut.

  </Accordion>

  <Accordion title="Prioritas kunci autentikasi">
    OpenClaw memeriksa kunci autentikasi dalam urutan ini:

    1. `MODELSTUDIO_API_KEY` (disarankan)
    2. `DASHSCOPE_API_KEY`
    3. `QWEN_API_KEY`

    Salah satu dari ini akan mengautentikasi provider `alibaba`.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Generasi video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="Qwen" href="/id/providers/qwen" icon="microchip">
    Penyiapan provider Qwen dan integrasi DashScope.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference#agent-defaults" icon="gear">
    Default agent dan konfigurasi model.
  </Card>
</CardGroup>
