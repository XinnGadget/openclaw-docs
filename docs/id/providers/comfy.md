---
read_when:
    - Anda ingin menggunakan workflow ComfyUI lokal dengan OpenClaw
    - Anda ingin menggunakan Comfy Cloud dengan workflow gambar, video, atau musik
    - Anda memerlukan key config Plugin comfy bawaan
summary: Penyiapan generasi gambar, video, dan musik workflow ComfyUI di OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-12T23:30:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85db395b171f37f80b34b22f3e7707bffc1fd9138e7d10687eef13eaaa55cf24
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw menyediakan Plugin `comfy` bawaan untuk eksekusi ComfyUI berbasis workflow. Plugin ini sepenuhnya digerakkan oleh workflow, jadi OpenClaw tidak mencoba memetakan `size`, `aspectRatio`, `resolution`, `durationSeconds`, atau kontrol bergaya TTS generik ke graph Anda.

| Property          | Detail                                                                           |
| ----------------- | -------------------------------------------------------------------------------- |
| Provider          | `comfy`                                                                          |
| Model             | `comfy/workflow`                                                                 |
| Permukaan bersama | `image_generate`, `video_generate`, `music_generate`                             |
| Autentikasi       | Tidak ada untuk ComfyUI lokal; `COMFY_API_KEY` atau `COMFY_CLOUD_API_KEY` untuk Comfy Cloud |
| API               | ComfyUI `/prompt` / `/history` / `/view` dan Comfy Cloud `/api/*`                |

## Yang didukung

- Generasi gambar dari workflow JSON
- Pengeditan gambar dengan 1 gambar referensi yang diunggah
- Generasi video dari workflow JSON
- Generasi video dengan 1 gambar referensi yang diunggah
- Generasi musik atau audio melalui tool bersama `music_generate`
- Pengunduhan output dari node yang dikonfigurasi atau semua node output yang cocok

## Memulai

Pilih antara menjalankan ComfyUI di mesin Anda sendiri atau menggunakan Comfy Cloud.

<Tabs>
  <Tab title="Lokal">
    **Paling cocok untuk:** menjalankan instance ComfyUI Anda sendiri di mesin atau LAN Anda.

    <Steps>
      <Step title="Jalankan ComfyUI secara lokal">
        Pastikan instance ComfyUI lokal Anda sedang berjalan (default ke `http://127.0.0.1:8188`).
      </Step>
      <Step title="Siapkan workflow JSON Anda">
        Ekspor atau buat file workflow JSON ComfyUI. Catat ID node untuk node input prompt dan node output yang ingin dibaca oleh OpenClaw.
      </Step>
      <Step title="Konfigurasikan provider">
        Tetapkan `mode: "local"` dan arahkan ke file workflow Anda. Berikut contoh gambar minimal:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "local",
                baseUrl: "http://127.0.0.1:8188",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Tetapkan model default">
        Arahkan OpenClaw ke model `comfy/workflow` untuk kapabilitas yang Anda konfigurasi:

        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Comfy Cloud">
    **Paling cocok untuk:** menjalankan workflow di Comfy Cloud tanpa mengelola resource GPU lokal.

    <Steps>
      <Step title="Dapatkan kunci API">
        Daftar di [comfy.org](https://comfy.org) dan buat kunci API dari dashboard akun Anda.
      </Step>
      <Step title="Tetapkan kunci API">
        Berikan kunci Anda melalui salah satu metode ini:

        ```bash
        # Variabel lingkungan (disarankan)
        export COMFY_API_KEY="your-key"

        # Variabel lingkungan alternatif
        export COMFY_CLOUD_API_KEY="your-key"

        # Atau inline di config
        openclaw config set models.providers.comfy.apiKey "your-key"
        ```
      </Step>
      <Step title="Siapkan workflow JSON Anda">
        Ekspor atau buat file workflow JSON ComfyUI. Catat ID node untuk node input prompt dan node output.
      </Step>
      <Step title="Konfigurasikan provider">
        Tetapkan `mode: "cloud"` dan arahkan ke file workflow Anda:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "cloud",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```

        <Tip>
        Mode cloud menggunakan default `baseUrl` ke `https://cloud.comfy.org`. Anda hanya perlu menetapkan `baseUrl` jika menggunakan endpoint cloud kustom.
        </Tip>
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Konfigurasi

Comfy mendukung pengaturan koneksi tingkat atas bersama plus bagian workflow per kapabilitas (`image`, `video`, `music`):

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

### Key bersama

| Key                   | Tipe                   | Deskripsi                                                                                |
| --------------------- | ---------------------- | ---------------------------------------------------------------------------------------- |
| `mode`                | `"local"` atau `"cloud"` | Mode koneksi.                                                                          |
| `baseUrl`             | string                 | Default ke `http://127.0.0.1:8188` untuk lokal atau `https://cloud.comfy.org` untuk cloud. |
| `apiKey`              | string                 | Key inline opsional, alternatif dari env var `COMFY_API_KEY` / `COMFY_CLOUD_API_KEY`.   |
| `allowPrivateNetwork` | boolean                | Izinkan `baseUrl` private/LAN dalam mode cloud.                                          |

### Key per kapabilitas

Key ini berlaku di dalam bagian `image`, `video`, atau `music`:

| Key                          | Wajib | Default  | Deskripsi                                                                    |
| ---------------------------- | ----- | -------- | ---------------------------------------------------------------------------- |
| `workflow` atau `workflowPath` | Ya  | --       | Path ke file workflow JSON ComfyUI.                                          |
| `promptNodeId`               | Ya    | --       | ID node yang menerima prompt teks.                                           |
| `promptInputName`            | Tidak | `"text"` | Nama input pada node prompt.                                                 |
| `outputNodeId`               | Tidak | --       | ID node untuk membaca output. Jika dihilangkan, semua node output yang cocok digunakan. |
| `pollIntervalMs`             | Tidak | --       | Interval polling dalam milidetik untuk penyelesaian job.                     |
| `timeoutMs`                  | Tidak | --       | Timeout dalam milidetik untuk eksekusi workflow.                             |

Bagian `image` dan `video` juga mendukung:

| Key                   | Wajib                                 | Default   | Deskripsi                                           |
| --------------------- | ------------------------------------- | --------- | --------------------------------------------------- |
| `inputImageNodeId`    | Ya (saat memberikan gambar referensi) | --        | ID node yang menerima gambar referensi yang diunggah. |
| `inputImageInputName` | Tidak                                 | `"image"` | Nama input pada node gambar.                        |

## Detail workflow

<AccordionGroup>
  <Accordion title="Workflow gambar">
    Tetapkan model gambar default ke `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    **Contoh pengeditan gambar referensi:**

    Untuk mengaktifkan pengeditan gambar dengan gambar referensi yang diunggah, tambahkan `inputImageNodeId` ke config gambar Anda:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            image: {
              workflowPath: "./workflows/edit-api.json",
              promptNodeId: "6",
              inputImageNodeId: "7",
              inputImageInputName: "image",
              outputNodeId: "9",
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Workflow video">
    Tetapkan model video default ke `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    Workflow video Comfy mendukung teks-ke-video dan gambar-ke-video melalui graph yang dikonfigurasi.

    <Note>
    OpenClaw tidak meneruskan video input ke workflow Comfy. Hanya prompt teks dan satu gambar referensi yang didukung sebagai input.
    </Note>

  </Accordion>

  <Accordion title="Workflow musik">
    Plugin bawaan mendaftarkan provider generasi musik untuk output audio atau musik yang didefinisikan workflow, ditampilkan melalui tool bersama `music_generate`:

    ```text
    /tool music_generate prompt="Warm ambient synth loop with soft tape texture"
    ```

    Gunakan bagian config `music` untuk mengarahkan ke workflow JSON audio Anda dan node output.

  </Accordion>

  <Accordion title="Kompatibilitas mundur">
    Config gambar tingkat atas yang sudah ada (tanpa bagian `image` bertingkat) tetap berfungsi:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            workflowPath: "./workflows/flux-api.json",
            promptNodeId: "6",
            outputNodeId: "9",
          },
        },
      },
    }
    ```

    OpenClaw memperlakukan bentuk lama itu sebagai config workflow gambar. Anda tidak perlu segera bermigrasi, tetapi bagian bertingkat `image` / `video` / `music` direkomendasikan untuk penyiapan baru.

    <Tip>
    Jika Anda hanya menggunakan generasi gambar, config datar lama dan bagian `image` bertingkat yang baru secara fungsional setara.
    </Tip>

  </Accordion>

  <Accordion title="Live test">
    Cakupan live opt-in tersedia untuk Plugin bawaan:

    ```bash
    OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
    ```

    Live test akan melewati kasus gambar, video, atau musik individual kecuali bagian workflow Comfy yang sesuai sudah dikonfigurasi.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Generasi Gambar" href="/id/tools/image-generation" icon="image">
    Konfigurasi dan penggunaan tool generasi gambar.
  </Card>
  <Card title="Generasi Video" href="/id/tools/video-generation" icon="video">
    Konfigurasi dan penggunaan tool generasi video.
  </Card>
  <Card title="Generasi Musik" href="/id/tools/music-generation" icon="music">
    Penyiapan tool generasi musik dan audio.
  </Card>
  <Card title="Direktori Provider" href="/id/providers/index" icon="layers">
    Ikhtisar semua provider dan ref model.
  </Card>
  <Card title="Referensi Konfigurasi" href="/id/gateway/configuration-reference#agent-defaults" icon="gear">
    Referensi config lengkap termasuk default agent.
  </Card>
</CardGroup>
