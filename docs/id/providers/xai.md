---
read_when:
    - Anda ingin menggunakan model Grok di OpenClaw
    - Anda sedang mengonfigurasi auth xAI atau ID model
summary: Gunakan model xAI Grok di OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-12T23:33:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw menyertakan Plugin provider `xai` bawaan untuk model Grok.

## Memulai

<Steps>
  <Step title="Buat API key">
    Buat API key di [konsol xAI](https://console.x.ai/).
  </Step>
  <Step title="Setel API key Anda">
    Setel `XAI_API_KEY`, atau jalankan:

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="Pilih model">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
OpenClaw menggunakan xAI Responses API sebagai transport xAI bawaan. `XAI_API_KEY`
yang sama juga dapat mendukung `web_search` berbasis Grok, `x_search` kelas satu,
dan `code_execution` jarak jauh.
Jika Anda menyimpan key xAI di bawah `plugins.entries.xai.config.webSearch.apiKey`,
provider model xAI bawaan juga menggunakan ulang key tersebut sebagai fallback.
Penyetelan `code_execution` berada di bawah `plugins.entries.xai.config.codeExecution`.
</Note>

## Katalog model bawaan

OpenClaw menyertakan keluarga model xAI berikut secara bawaan:

| Keluarga        | ID model                                                                 |
| --------------- | ------------------------------------------------------------------------ |
| Grok 3          | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`               |
| Grok 4          | `grok-4`, `grok-4-0709`                                                  |
| Grok 4 Fast     | `grok-4-fast`, `grok-4-fast-non-reasoning`                               |
| Grok 4.1 Fast   | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                           |
| Grok 4.20 Beta  | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code       | `grok-code-fast-1`                                                       |

Plugin ini juga melakukan forward-resolve untuk id `grok-4*` dan `grok-code-fast*` yang lebih baru saat
mengikuti bentuk API yang sama.

<Tip>
`grok-4-fast`, `grok-4-1-fast`, dan varian `grok-4.20-beta-*` adalah
ref Grok berkemampuan gambar saat ini dalam katalog bawaan.
</Tip>

### Pemetaan mode cepat

`/fast on` atau `agents.defaults.models["xai/<model>"].params.fastMode: true`
menulis ulang permintaan xAI native sebagai berikut:

| Model sumber   | Target mode cepat  |
| -------------- | ------------------ |
| `grok-3`       | `grok-3-fast`      |
| `grok-3-mini`  | `grok-3-mini-fast` |
| `grok-4`       | `grok-4-fast`      |
| `grok-4-0709`  | `grok-4-fast`      |

### Alias kompatibilitas lama

Alias lama tetap dinormalisasi ke id bawaan kanonis:

| Alias lama                | ID kanonis                            |
| ------------------------- | ------------------------------------- |
| `grok-4-fast-reasoning`   | `grok-4-fast`                         |
| `grok-4-1-fast-reasoning` | `grok-4-1-fast`                       |
| `grok-4.20-reasoning`     | `grok-4.20-beta-latest-reasoning`     |
| `grok-4.20-non-reasoning` | `grok-4.20-beta-latest-non-reasoning` |

## Fitur

<AccordionGroup>
  <Accordion title="Pencarian web">
    Provider pencarian web `grok` bawaan juga menggunakan `XAI_API_KEY`:

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="Pembuatan video">
    Plugin `xai` bawaan mendaftarkan pembuatan video melalui alat bersama
    `video_generate`.

    - Model video default: `xai/grok-imagine-video`
    - Mode: text-to-video, image-to-video, dan alur edit/extend video jarak jauh
    - Mendukung `aspectRatio` dan `resolution`

    <Warning>
    Buffer video lokal tidak diterima. Gunakan URL `http(s)` jarak jauh untuk
    input referensi video dan edit.
    </Warning>

    Untuk menggunakan xAI sebagai provider video default:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    Lihat [Video Generation](/id/tools/video-generation) untuk parameter alat bersama,
    pemilihan provider, dan perilaku failover.
    </Note>

  </Accordion>

  <Accordion title="Konfigurasi x_search">
    Plugin xAI bawaan mengekspos `x_search` sebagai alat OpenClaw untuk mencari
    konten X (sebelumnya Twitter) melalui Grok.

    Path config: `plugins.entries.xai.config.xSearch`

    | Key                | Tipe    | Default            | Deskripsi                          |
    | ------------------ | ------- | ------------------ | ------------------------------------ |
    | `enabled`          | boolean | —                  | Aktifkan atau nonaktifkan x_search           |
    | `model`            | string  | `grok-4-1-fast`    | Model yang digunakan untuk permintaan x_search     |
    | `inlineCitations`  | boolean | —                  | Sertakan sitasi inline dalam hasil  |
    | `maxTurns`         | number  | —                  | Maksimum giliran percakapan           |
    | `timeoutSeconds`   | number  | —                  | Timeout permintaan dalam detik           |
    | `cacheTtlMinutes`  | number  | —                  | Time-to-live cache dalam menit        |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Konfigurasi code execution">
    Plugin xAI bawaan mengekspos `code_execution` sebagai alat OpenClaw untuk
    eksekusi kode jarak jauh di lingkungan sandbox xAI.

    Path config: `plugins.entries.xai.config.codeExecution`

    | Key               | Tipe    | Default                     | Deskripsi                              |
    | ----------------- | ------- | --------------------------- | ---------------------------------------- |
    | `enabled`         | boolean | `true` (jika key tersedia) | Aktifkan atau nonaktifkan code execution  |
    | `model`           | string  | `grok-4-1-fast`            | Model yang digunakan untuk permintaan code execution   |
    | `maxTurns`        | number  | —                           | Maksimum giliran percakapan               |
    | `timeoutSeconds`  | number  | —                           | Timeout permintaan dalam detik               |

    <Note>
    Ini adalah eksekusi sandbox xAI jarak jauh, bukan [`exec`](/id/tools/exec) lokal.
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Batasan yang diketahui">
    - Auth saat ini hanya menggunakan API key. Belum ada alur OAuth atau device-code xAI di
      OpenClaw.
    - `grok-4.20-multi-agent-experimental-beta-0304` tidak didukung pada
      jalur provider xAI normal karena memerlukan surface API upstream
      yang berbeda dari transport xAI standar OpenClaw.
  </Accordion>

  <Accordion title="Catatan lanjutan">
    - OpenClaw secara otomatis menerapkan perbaikan kompatibilitas schema alat dan pemanggilan alat khusus xAI
      pada jalur runner bersama.
    - Permintaan xAI native secara default menggunakan `tool_stream: true`. Setel
      `agents.defaults.models["xai/<model>"].params.tool_stream` ke `false` untuk
      menonaktifkannya.
    - Wrapper xAI bawaan menghapus flag schema alat strict yang tidak didukung dan
      key payload reasoning sebelum mengirim permintaan xAI native.
    - `web_search`, `x_search`, dan `code_execution` diekspos sebagai alat OpenClaw.
      OpenClaw mengaktifkan built-in xAI spesifik yang dibutuhkan di dalam setiap permintaan alat
      alih-alih melampirkan semua alat native ke setiap giliran chat.
    - `x_search` dan `code_execution` dimiliki oleh Plugin xAI bawaan alih-alih
      di-hardcode ke runtime model inti.
    - `code_execution` adalah eksekusi sandbox xAI jarak jauh, bukan
      [`exec`](/id/tools/exec) lokal.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter alat video bersama dan pemilihan provider.
  </Card>
  <Card title="Semua provider" href="/id/providers/index" icon="grid-2">
    Ikhtisar provider yang lebih luas.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Masalah umum dan perbaikannya.
  </Card>
</CardGroup>
