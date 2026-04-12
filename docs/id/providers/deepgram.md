---
read_when:
    - Anda menginginkan speech-to-text Deepgram untuk lampiran audio
    - Anda memerlukan contoh config Deepgram singkat
summary: Transkripsi Deepgram untuk catatan suara masuk
title: Deepgram
x-i18n:
    generated_at: "2026-04-12T23:30:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 091523d6669e3d258f07c035ec756bd587299b6c7025520659232b1b2c1e21a5
    source_path: providers/deepgram.md
    workflow: 15
---

# Deepgram (Transkripsi Audio)

Deepgram adalah API speech-to-text. Di OpenClaw, ini digunakan untuk **transkripsi audio/catatan suara masuk**
melalui `tools.media.audio`.

Saat diaktifkan, OpenClaw mengunggah file audio ke Deepgram dan menyisipkan transkrip
ke pipeline balasan (`{{Transcript}}` + blok `[Audio]`). Ini **bukan streaming**;
ini menggunakan endpoint transkripsi rekaman siap pakai.

| Detail        | Nilai                                                      |
| ------------- | ---------------------------------------------------------- |
| Situs web     | [deepgram.com](https://deepgram.com)                       |
| Dokumen       | [developers.deepgram.com](https://developers.deepgram.com) |
| Auth          | `DEEPGRAM_API_KEY`                                         |
| Model default | `nova-3`                                                   |

## Memulai

<Steps>
  <Step title="Setel API key Anda">
    Tambahkan API key Deepgram Anda ke environment:

    ```
    DEEPGRAM_API_KEY=dg_...
    ```

  </Step>
  <Step title="Aktifkan provider audio">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Step>
  <Step title="Kirim catatan suara">
    Kirim pesan audio melalui channel terhubung apa pun. OpenClaw akan mentranskripsikannya
    melalui Deepgram dan menyisipkan transkrip ke pipeline balasan.
  </Step>
</Steps>

## Opsi konfigurasi

| Opsi              | Path                                                         | Deskripsi                               |
| ----------------- | ------------------------------------------------------------ | --------------------------------------- |
| `model`           | `tools.media.audio.models[].model`                           | ID model Deepgram (default: `nova-3`)   |
| `language`        | `tools.media.audio.models[].language`                        | Petunjuk bahasa (opsional)              |
| `detect_language` | `tools.media.audio.providerOptions.deepgram.detect_language` | Aktifkan deteksi bahasa (opsional)      |
| `punctuate`       | `tools.media.audio.providerOptions.deepgram.punctuate`       | Aktifkan tanda baca (opsional)          |
| `smart_format`    | `tools.media.audio.providerOptions.deepgram.smart_format`    | Aktifkan pemformatan cerdas (opsional)  |

<Tabs>
  <Tab title="Dengan petunjuk bahasa">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            models: [{ provider: "deepgram", model: "nova-3", language: "en" }],
          },
        },
      },
    }
    ```
  </Tab>
  <Tab title="Dengan opsi Deepgram">
    ```json5
    {
      tools: {
        media: {
          audio: {
            enabled: true,
            providerOptions: {
              deepgram: {
                detect_language: true,
                punctuate: true,
                smart_format: true,
              },
            },
            models: [{ provider: "deepgram", model: "nova-3" }],
          },
        },
      },
    }
    ```
  </Tab>
</Tabs>

## Catatan

<AccordionGroup>
  <Accordion title="Autentikasi">
    Autentikasi mengikuti urutan auth provider standar. `DEEPGRAM_API_KEY` adalah
    jalur yang paling sederhana.
  </Accordion>
  <Accordion title="Proxy dan endpoint kustom">
    Override endpoint atau header dengan `tools.media.audio.baseUrl` dan
    `tools.media.audio.headers` saat menggunakan proxy.
  </Accordion>
  <Accordion title="Perilaku output">
    Output mengikuti aturan audio yang sama seperti provider lain (batas ukuran, timeout,
    penyisipan transkrip).
  </Accordion>
</AccordionGroup>

<Note>
Transkripsi Deepgram bersifat **khusus rekaman siap pakai** (bukan streaming real-time). OpenClaw
mengunggah file audio lengkap dan menunggu transkrip penuh sebelum menyisipkannya
ke dalam percakapan.
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Tool media" href="/tools/media" icon="photo-film">
    Ikhtisar pipeline pemrosesan audio, gambar, dan video.
  </Card>
  <Card title="Konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi config lengkap termasuk pengaturan tool media.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Masalah umum dan langkah debugging.
  </Card>
  <Card title="FAQ" href="/id/help/faq" icon="circle-question">
    Pertanyaan yang sering diajukan tentang penyiapan OpenClaw.
  </Card>
</CardGroup>
