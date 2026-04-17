---
read_when:
    - Anda ingin menggunakan model OpenAI di OpenClaw
    - Anda ingin auth subscription Codex alih-alih API key
    - Anda memerlukan perilaku eksekusi agen GPT-5 yang lebih ketat
summary: Gunakan OpenAI melalui API key atau subscription Codex di OpenClaw
title: OpenAI
x-i18n:
    generated_at: "2026-04-12T23:31:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6aeb756618c5611fed56e4bf89015a2304ff2e21596104b470ec6e7cb459d1c9
    source_path: providers/openai.md
    workflow: 15
---

# OpenAI

OpenAI menyediakan API developer untuk model GPT. OpenClaw mendukung dua jalur auth:

- **API key** — akses langsung OpenAI Platform dengan penagihan berbasis penggunaan (model `openai/*`)
- **Subscription Codex** — sign-in ChatGPT/Codex dengan akses subscription (model `openai-codex/*`)

OpenAI secara eksplisit mendukung penggunaan OAuth subscription dalam alat eksternal dan alur kerja seperti OpenClaw.

## Memulai

Pilih metode auth yang Anda inginkan dan ikuti langkah penyiapannya.

<Tabs>
  <Tab title="API key (OpenAI Platform)">
    **Terbaik untuk:** akses API langsung dan penagihan berbasis penggunaan.

    <Steps>
      <Step title="Dapatkan API key Anda">
        Buat atau salin API key dari [dasbor OpenAI Platform](https://platform.openai.com/api-keys).
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice openai-api-key
        ```

        Atau teruskan key secara langsung:

        ```bash
        openclaw onboard --openai-api-key "$OPENAI_API_KEY"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider openai
        ```
      </Step>
    </Steps>

    ### Ringkasan rute

    | Ref model | Rute | Auth |
    |-----------|-------|------|
    | `openai/gpt-5.4` | API OpenAI Platform langsung | `OPENAI_API_KEY` |
    | `openai/gpt-5.4-pro` | API OpenAI Platform langsung | `OPENAI_API_KEY` |

    <Note>
    Sign-in ChatGPT/Codex dirutekan melalui `openai-codex/*`, bukan `openai/*`.
    </Note>

    ### Contoh config

    ```json5
    {
      env: { OPENAI_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
    }
    ```

    <Warning>
    OpenClaw **tidak** mengekspos `openai/gpt-5.3-codex-spark` pada jalur API langsung. Permintaan API OpenAI live menolak model tersebut. Spark hanya untuk Codex.
    </Warning>

  </Tab>

  <Tab title="Subscription Codex">
    **Terbaik untuk:** menggunakan subscription ChatGPT/Codex Anda alih-alih API key terpisah. Codex cloud memerlukan sign-in ChatGPT.

    <Steps>
      <Step title="Jalankan OAuth Codex">
        ```bash
        openclaw onboard --auth-choice openai-codex
        ```

        Atau jalankan OAuth secara langsung:

        ```bash
        openclaw models auth login --provider openai-codex
        ```
      </Step>
      <Step title="Setel model default">
        ```bash
        openclaw config set agents.defaults.model.primary openai-codex/gpt-5.4
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider openai-codex
        ```
      </Step>
    </Steps>

    ### Ringkasan rute

    | Ref model | Rute | Auth |
    |-----------|-------|------|
    | `openai-codex/gpt-5.4` | OAuth ChatGPT/Codex | Sign-in Codex |
    | `openai-codex/gpt-5.3-codex-spark` | OAuth ChatGPT/Codex | Sign-in Codex (bergantung pada entitlement) |

    <Note>
    Rute ini sengaja dipisahkan dari `openai/gpt-5.4`. Gunakan `openai/*` dengan API key untuk akses Platform langsung, dan `openai-codex/*` untuk akses subscription Codex.
    </Note>

    ### Contoh config

    ```json5
    {
      agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
    }
    ```

    <Tip>
    Jika onboarding menggunakan ulang login Codex CLI yang sudah ada, kredensial tersebut tetap dikelola oleh Codex CLI. Saat kedaluwarsa, OpenClaw terlebih dahulu membaca ulang sumber Codex eksternal lalu menulis kembali kredensial yang diperbarui ke penyimpanan Codex.
    </Tip>

    ### Batas jendela konteks

    OpenClaw memperlakukan metadata model dan batas konteks runtime sebagai nilai yang terpisah.

    Untuk `openai-codex/gpt-5.4`:

    - `contextWindow` native: `1050000`
    - Batas runtime `contextTokens` default: `272000`

    Batas default yang lebih kecil memiliki karakteristik latensi dan kualitas yang lebih baik dalam praktik. Timpa dengan `contextTokens`:

    ```json5
    {
      models: {
        providers: {
          "openai-codex": {
            models: [{ id: "gpt-5.4", contextTokens: 160000 }],
          },
        },
      },
    }
    ```

    <Note>
    Gunakan `contextWindow` untuk mendeklarasikan metadata model native. Gunakan `contextTokens` untuk membatasi anggaran konteks runtime.
    </Note>

  </Tab>
</Tabs>

## Pembuatan gambar

Plugin `openai` bawaan mendaftarkan pembuatan gambar melalui alat `image_generate`.

| Kapabilitas               | Nilai                              |
| ------------------------- | ---------------------------------- |
| Model default             | `openai/gpt-image-1`               |
| Maks gambar per permintaan| 4                                  |
| Mode edit                 | Diaktifkan (hingga 5 gambar referensi) |
| Override ukuran           | Didukung                           |
| Rasio aspek / resolusi    | Tidak diteruskan ke OpenAI Images API |

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "openai/gpt-image-1" },
    },
  },
}
```

<Note>
Lihat [Image Generation](/id/tools/image-generation) untuk parameter alat bersama, pemilihan provider, dan perilaku failover.
</Note>

## Pembuatan video

Plugin `openai` bawaan mendaftarkan pembuatan video melalui alat `video_generate`.

| Kapabilitas     | Nilai                                                                             |
| ---------------- | --------------------------------------------------------------------------------- |
| Model default    | `openai/sora-2`                                                                   |
| Mode            | Text-to-video, image-to-video, edit video tunggal                                  |
| Input referensi | 1 gambar atau 1 video                                                             |
| Override ukuran | Didukung                                                                         |
| Override lainnya  | `aspectRatio`, `resolution`, `audio`, `watermark` diabaikan dengan peringatan alat |

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "openai/sora-2" },
    },
  },
}
```

<Note>
Lihat [Video Generation](/id/tools/video-generation) untuk parameter alat bersama, pemilihan provider, dan perilaku failover.
</Note>

## Overlay kepribadian

OpenClaw menambahkan overlay prompt kecil khusus OpenAI untuk eksekusi `openai/*` dan `openai-codex/*`. Overlay ini menjaga assistant tetap hangat, kolaboratif, ringkas, dan sedikit lebih ekspresif secara emosional tanpa menggantikan system prompt dasar.

| Nilai                  | Efek                             |
| ---------------------- | ---------------------------------- |
| `"friendly"` (default) | Aktifkan overlay khusus OpenAI |
| `"on"`                 | Alias untuk `"friendly"`             |
| `"off"`                | Hanya gunakan prompt dasar OpenClaw      |

<Tabs>
  <Tab title="Config">
    ```json5
    {
      plugins: {
        entries: {
          openai: { config: { personality: "friendly" } },
        },
      },
    }
    ```
  </Tab>
  <Tab title="CLI">
    ```bash
    openclaw config set plugins.entries.openai.config.personality off
    ```
  </Tab>
</Tabs>

<Tip>
Nilai tidak peka huruf besar/kecil saat runtime, jadi `"Off"` dan `"off"` sama-sama menonaktifkan overlay.
</Tip>

## Voice dan speech

<AccordionGroup>
  <Accordion title="Sintesis ucapan (TTS)">
    Plugin `openai` bawaan mendaftarkan sintesis ucapan untuk surface `messages.tts`.

    | Pengaturan | Path config | Default |
    |---------|------------|---------|
    | Model | `messages.tts.providers.openai.model` | `gpt-4o-mini-tts` |
    | Suara | `messages.tts.providers.openai.voice` | `coral` |
    | Kecepatan | `messages.tts.providers.openai.speed` | (tidak disetel) |
    | Instruksi | `messages.tts.providers.openai.instructions` | (tidak disetel, hanya `gpt-4o-mini-tts`) |
    | Format | `messages.tts.providers.openai.responseFormat` | `opus` untuk catatan suara, `mp3` untuk berkas |
    | API key | `messages.tts.providers.openai.apiKey` | Fallback ke `OPENAI_API_KEY` |
    | Base URL | `messages.tts.providers.openai.baseUrl` | `https://api.openai.com/v1` |

    Model yang tersedia: `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`. Suara yang tersedia: `alloy`, `ash`, `ballad`, `cedar`, `coral`, `echo`, `fable`, `juniper`, `marin`, `onyx`, `nova`, `sage`, `shimmer`, `verse`.

    ```json5
    {
      messages: {
        tts: {
          providers: {
            openai: { model: "gpt-4o-mini-tts", voice: "coral" },
          },
        },
      },
    }
    ```

    <Note>
    Setel `OPENAI_TTS_BASE_URL` untuk menimpa base URL TTS tanpa memengaruhi endpoint API chat.
    </Note>

  </Accordion>

  <Accordion title="Transkripsi realtime">
    Plugin `openai` bawaan mendaftarkan transkripsi realtime untuk Plugin Voice Call.

    | Pengaturan | Path config | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.streaming.providers.openai.model` | `gpt-4o-transcribe` |
    | Durasi hening | `...openai.silenceDurationMs` | `800` |
    | Ambang VAD | `...openai.vadThreshold` | `0.5` |
    | API key | `...openai.apiKey` | Fallback ke `OPENAI_API_KEY` |

    <Note>
    Menggunakan koneksi WebSocket ke `wss://api.openai.com/v1/realtime` dengan audio G.711 u-law.
    </Note>

  </Accordion>

  <Accordion title="Voice realtime">
    Plugin `openai` bawaan mendaftarkan voice realtime untuk Plugin Voice Call.

    | Pengaturan | Path config | Default |
    |---------|------------|---------|
    | Model | `plugins.entries.voice-call.config.realtime.providers.openai.model` | `gpt-realtime` |
    | Suara | `...openai.voice` | `alloy` |
    | Temperature | `...openai.temperature` | `0.8` |
    | Ambang VAD | `...openai.vadThreshold` | `0.5` |
    | Durasi hening | `...openai.silenceDurationMs` | `500` |
    | API key | `...openai.apiKey` | Fallback ke `OPENAI_API_KEY` |

    <Note>
    Mendukung Azure OpenAI melalui key config `azureEndpoint` dan `azureDeployment`. Mendukung pemanggilan alat dua arah. Menggunakan format audio G.711 u-law.
    </Note>

  </Accordion>
</AccordionGroup>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Transport (WebSocket vs SSE)">
    OpenClaw menggunakan prioritas WebSocket dengan fallback SSE (`"auto"`) untuk `openai/*` dan `openai-codex/*`.

    Dalam mode `"auto"`, OpenClaw:
    - Mencoba ulang satu kegagalan WebSocket awal sebelum fallback ke SSE
    - Setelah kegagalan, menandai WebSocket sebagai terdegradasi selama ~60 detik dan menggunakan SSE selama masa cooldown
    - Melampirkan header identitas sesi dan giliran yang stabil untuk retry dan reconnect
    - Menormalkan penghitung penggunaan (`input_tokens` / `prompt_tokens`) di seluruh varian transport

    | Nilai | Perilaku |
    |-------|----------|
    | `"auto"` (default) | WebSocket terlebih dahulu, fallback SSE |
    | `"sse"` | Paksa hanya SSE |
    | `"websocket"` | Paksa hanya WebSocket |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai-codex/gpt-5.4": {
              params: { transport: "auto" },
            },
          },
        },
      },
    }
    ```

    Dokumen OpenAI terkait:
    - [Realtime API with WebSocket](https://platform.openai.com/docs/guides/realtime-websocket)
    - [Streaming API responses (SSE)](https://platform.openai.com/docs/guides/streaming-responses)

  </Accordion>

  <Accordion title="Warm-up WebSocket">
    OpenClaw mengaktifkan warm-up WebSocket secara default untuk `openai/*` guna mengurangi latensi giliran pertama.

    ```json5
    // Nonaktifkan warm-up
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: { openaiWsWarmup: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Mode cepat">
    OpenClaw mengekspos toggle mode cepat bersama untuk `openai/*` dan `openai-codex/*`:

    - **Chat/UI:** `/fast status|on|off`
    - **Config:** `agents.defaults.models["<provider>/<model>"].params.fastMode`

    Saat diaktifkan, OpenClaw memetakan mode cepat ke pemrosesan prioritas OpenAI (`service_tier = "priority"`). Nilai `service_tier` yang sudah ada dipertahankan, dan mode cepat tidak menulis ulang `reasoning` atau `text.verbosity`.

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { fastMode: true } },
            "openai-codex/gpt-5.4": { params: { fastMode: true } },
          },
        },
      },
    }
    ```

    <Note>
    Override sesi menang atas config. Menghapus override sesi di UI Sessions akan mengembalikan sesi ke default yang dikonfigurasi.
    </Note>

  </Accordion>

  <Accordion title="Pemrosesan prioritas (service_tier)">
    API OpenAI mengekspos pemrosesan prioritas melalui `service_tier`. Setel per model di OpenClaw:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": { params: { serviceTier: "priority" } },
            "openai-codex/gpt-5.4": { params: { serviceTier: "priority" } },
          },
        },
      },
    }
    ```

    Nilai yang didukung: `auto`, `default`, `flex`, `priority`.

    <Warning>
    `serviceTier` hanya diteruskan ke endpoint OpenAI native (`api.openai.com`) dan endpoint Codex native (`chatgpt.com/backend-api`). Jika Anda merutekan salah satu provider melalui proxy, OpenClaw membiarkan `service_tier` tetap tidak diubah.
    </Warning>

  </Accordion>

  <Accordion title="Compaction sisi server (Responses API)">
    Untuk model OpenAI Responses langsung (`openai/*` di `api.openai.com`), OpenClaw otomatis mengaktifkan Compaction sisi server:

    - Memaksa `store: true` (kecuali compat model menetapkan `supportsStore: false`)
    - Menyuntikkan `context_management: [{ type: "compaction", compact_threshold: ... }]`
    - Default `compact_threshold`: 70% dari `contextWindow` (atau `80000` bila tidak tersedia)

    <Tabs>
      <Tab title="Aktifkan secara eksplisit">
        Berguna untuk endpoint kompatibel seperti Azure OpenAI Responses:

        ```json5
        {
          agents: {
            defaults: {
              models: {
                "azure-openai-responses/gpt-5.4": {
                  params: { responsesServerCompaction: true },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Ambang kustom">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: {
                    responsesServerCompaction: true,
                    responsesCompactThreshold: 120000,
                  },
                },
              },
            },
          },
        }
        ```
      </Tab>
      <Tab title="Nonaktifkan">
        ```json5
        {
          agents: {
            defaults: {
              models: {
                "openai/gpt-5.4": {
                  params: { responsesServerCompaction: false },
                },
              },
            },
          },
        }
        ```
      </Tab>
    </Tabs>

    <Note>
    `responsesServerCompaction` hanya mengontrol penyuntikan `context_management`. Model OpenAI Responses langsung tetap memaksa `store: true` kecuali compat menetapkan `supportsStore: false`.
    </Note>

  </Accordion>

  <Accordion title="Mode GPT agentik ketat">
    Untuk eksekusi keluarga GPT-5 pada `openai/*` dan `openai-codex/*`, OpenClaw dapat menggunakan kontrak eksekusi tersemat yang lebih ketat:

    ```json5
    {
      agents: {
        defaults: {
          embeddedPi: { executionContract: "strict-agentic" },
        },
      },
    }
    ```

    Dengan `strict-agentic`, OpenClaw:
    - Tidak lagi memperlakukan giliran yang hanya berisi rencana sebagai progres yang berhasil saat tindakan alat tersedia
    - Mencoba ulang giliran dengan pengarahan bertindak-sekarang
    - Secara otomatis mengaktifkan `update_plan` untuk pekerjaan yang substansial
    - Menampilkan status terblokir yang eksplisit jika model terus membuat rencana tanpa bertindak

    <Note>
    Cakupannya hanya untuk eksekusi keluarga GPT-5 OpenAI dan Codex. Provider lain dan keluarga model yang lebih lama mempertahankan perilaku default.
    </Note>

  </Accordion>

  <Accordion title="Rute native vs yang kompatibel dengan OpenAI">
    OpenClaw memperlakukan endpoint OpenAI langsung, Codex, dan Azure OpenAI secara berbeda dari proxy `/v1` generik yang kompatibel dengan OpenAI:

    **Rute native** (`openai/*`, `openai-codex/*`, Azure OpenAI):
    - Mempertahankan `reasoning: { effort: "none" }` tetap utuh saat reasoning dinonaktifkan secara eksplisit
    - Menjadikan schema alat default ke mode strict
    - Melampirkan header atribusi tersembunyi hanya pada host native yang terverifikasi
    - Mempertahankan pembentukan permintaan khusus OpenAI (`service_tier`, `store`, reasoning-compat, petunjuk prompt-cache)

    **Rute proxy/kompatibel:**
    - Menggunakan perilaku compat yang lebih longgar
    - Tidak memaksa schema alat strict atau header khusus native

    Azure OpenAI menggunakan transport dan perilaku compat native, tetapi tidak menerima header atribusi tersembunyi.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pembuatan gambar" href="/id/tools/image-generation" icon="image">
    Parameter alat gambar bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter alat video bersama dan pemilihan provider.
  </Card>
  <Card title="OAuth dan auth" href="/id/gateway/authentication" icon="key">
    Detail auth dan aturan penggunaan ulang kredensial.
  </Card>
</CardGroup>
