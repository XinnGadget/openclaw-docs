---
read_when:
    - Anda ingin menjalankan OpenClaw dengan model cloud atau lokal melalui Ollama
    - Anda memerlukan panduan penyiapan dan konfigurasi Ollama
summary: Jalankan OpenClaw dengan Ollama (model cloud dan lokal)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:40:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw terintegrasi dengan API native Ollama (`/api/chat`) untuk model cloud yang dihosting dan server Ollama lokal/self-hosted. Anda dapat menggunakan Ollama dalam tiga mode: `Cloud + Local` melalui host Ollama yang dapat dijangkau, `Cloud only` terhadap `https://ollama.com`, atau `Local only` terhadap host Ollama yang dapat dijangkau.

<Warning>
**Pengguna Ollama jarak jauh**: Jangan gunakan URL kompatibel OpenAI `/v1` (`http://host:11434/v1`) dengan OpenClaw. Ini merusak pemanggilan tool dan model dapat mengeluarkan JSON tool mentah sebagai teks biasa. Gunakan URL API native Ollama sebagai gantinya: `baseUrl: "http://host:11434"` (tanpa `/v1`).
</Warning>

## Memulai

Pilih metode dan mode penyiapan yang Anda inginkan.

<Tabs>
  <Tab title="Onboarding (direkomendasikan)">
    **Paling cocok untuk:** cara tercepat menuju penyiapan Ollama cloud atau lokal yang berfungsi.

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard
        ```

        Pilih **Ollama** dari daftar penyedia.
      </Step>
      <Step title="Pilih mode Anda">
        - **Cloud + Local** — host Ollama lokal ditambah model cloud yang dirutekan melalui host tersebut
        - **Cloud only** — model Ollama yang dihosting melalui `https://ollama.com`
        - **Local only** — hanya model lokal
      </Step>
      <Step title="Pilih model">
        `Cloud only` meminta `OLLAMA_API_KEY` dan menyarankan default cloud yang dihosting. `Cloud + Local` dan `Local only` meminta URL dasar Ollama, menemukan model yang tersedia, dan secara otomatis menarik model lokal yang dipilih jika belum tersedia. `Cloud + Local` juga memeriksa apakah host Ollama tersebut sudah masuk untuk akses cloud.
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Mode non-interaktif

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    Secara opsional tentukan URL dasar atau model kustom:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Penyiapan manual">
    **Paling cocok untuk:** kontrol penuh atas penyiapan cloud atau lokal.

    <Steps>
      <Step title="Pilih cloud atau lokal">
        - **Cloud + Local**: instal Ollama, masuk dengan `ollama signin`, dan rutekan permintaan cloud melalui host tersebut
        - **Cloud only**: gunakan `https://ollama.com` dengan `OLLAMA_API_KEY`
        - **Local only**: instal Ollama dari [ollama.com/download](https://ollama.com/download)
      </Step>
      <Step title="Tarik model lokal (hanya lokal)">
        ```bash
        ollama pull gemma4
        # atau
        ollama pull gpt-oss:20b
        # atau
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Aktifkan Ollama untuk OpenClaw">
        Untuk `Cloud only`, gunakan `OLLAMA_API_KEY` asli Anda. Untuk penyiapan berbasis host, nilai placeholder apa pun dapat digunakan:

        ```bash
        # Cloud
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Hanya lokal
        export OLLAMA_API_KEY="ollama-local"

        # Atau konfigurasi di file konfigurasi Anda
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Periksa dan atur model Anda">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Atau atur default di konfigurasi:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Model cloud

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` menggunakan host Ollama yang dapat dijangkau sebagai titik kontrol untuk model lokal dan cloud. Ini adalah alur hibrida yang direkomendasikan oleh Ollama.

    Gunakan **Cloud + Local** saat penyiapan. OpenClaw meminta URL dasar Ollama, menemukan model lokal dari host tersebut, dan memeriksa apakah host sudah masuk untuk akses cloud dengan `ollama signin`. Saat host sudah masuk, OpenClaw juga menyarankan default cloud yang dihosting seperti `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, dan `glm-5.1:cloud`.

    Jika host belum masuk, OpenClaw akan mempertahankan penyiapan hanya lokal sampai Anda menjalankan `ollama signin`.

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` berjalan terhadap API hosted Ollama di `https://ollama.com`.

    Gunakan **Cloud only** saat penyiapan. OpenClaw meminta `OLLAMA_API_KEY`, menetapkan `baseUrl: "https://ollama.com"`, dan mengisi daftar model cloud yang dihosting. Jalur ini **tidak** memerlukan server Ollama lokal atau `ollama signin`.

  </Tab>

  <Tab title="Local only">
    Dalam mode hanya lokal, OpenClaw menemukan model dari instance Ollama yang dikonfigurasi. Jalur ini ditujukan untuk server Ollama lokal atau self-hosted.

    OpenClaw saat ini menyarankan `gemma4` sebagai default lokal.

  </Tab>
</Tabs>

## Penemuan model (penyedia implisit)

Saat Anda menetapkan `OLLAMA_API_KEY` (atau profil autentikasi) dan **tidak** mendefinisikan `models.providers.ollama`, OpenClaw menemukan model dari instance Ollama lokal di `http://127.0.0.1:11434`.

| Perilaku             | Detail                                                                                                                                                               |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kueri katalog        | Mengueri `/api/tags`                                                                                                                                                 |
| Deteksi kapabilitas  | Menggunakan lookup `/api/show` best-effort untuk membaca `contextWindow` dan mendeteksi kapabilitas (termasuk vision)                                              |
| Model vision         | Model dengan kapabilitas `vision` yang dilaporkan oleh `/api/show` ditandai sebagai mampu menerima gambar (`input: ["text", "image"]`), sehingga OpenClaw secara otomatis menyisipkan gambar ke prompt |
| Deteksi penalaran    | Menandai `reasoning` dengan heuristik nama model (`r1`, `reasoning`, `think`)                                                                                       |
| Batas token          | Menetapkan `maxTokens` ke batas maksimum token Ollama default yang digunakan oleh OpenClaw                                                                          |
| Biaya                | Menetapkan semua biaya ke `0`                                                                                                                                       |

Ini menghindari entri model manual sambil menjaga katalog tetap selaras dengan instance Ollama lokal.

```bash
# Lihat model yang tersedia
ollama list
openclaw models list
```

Untuk menambahkan model baru, cukup tarik dengan Ollama:

```bash
ollama pull mistral
```

Model baru akan ditemukan secara otomatis dan tersedia untuk digunakan.

<Note>
Jika Anda menetapkan `models.providers.ollama` secara eksplisit, penemuan otomatis dilewati dan Anda harus mendefinisikan model secara manual. Lihat bagian konfigurasi eksplisit di bawah.
</Note>

## Konfigurasi

<Tabs>
  <Tab title="Dasar (penemuan implisit)">
    Jalur aktivasi hanya lokal yang paling sederhana adalah melalui variabel lingkungan:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    Jika `OLLAMA_API_KEY` ditetapkan, Anda dapat menghilangkan `apiKey` di entri penyedia dan OpenClaw akan mengisinya untuk pemeriksaan ketersediaan.
    </Tip>

  </Tab>

  <Tab title="Eksplisit (model manual)">
    Gunakan konfigurasi eksplisit saat Anda menginginkan penyiapan cloud yang dihosting, Ollama berjalan di host/port lain, Anda ingin memaksakan jendela konteks atau daftar model tertentu, atau Anda ingin definisi model sepenuhnya manual.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="URL dasar kustom">
    Jika Ollama berjalan di host atau port yang berbeda (konfigurasi eksplisit menonaktifkan penemuan otomatis, jadi definisikan model secara manual):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // Tanpa /v1 - gunakan URL API native Ollama
            api: "ollama", // Tetapkan secara eksplisit untuk menjamin perilaku pemanggilan tool native
          },
        },
      },
    }
    ```

    <Warning>
    Jangan tambahkan `/v1` ke URL. Jalur `/v1` menggunakan mode kompatibel OpenAI, tempat pemanggilan tool tidak andal. Gunakan URL dasar Ollama tanpa sufiks jalur.
    </Warning>

  </Tab>
</Tabs>

### Pemilihan model

Setelah dikonfigurasi, semua model Ollama Anda tersedia:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Pencarian Web Ollama

OpenClaw mendukung **Ollama Web Search** sebagai penyedia `web_search` bawaan.

| Properti    | Detail                                                                                                             |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| Host        | Menggunakan host Ollama yang dikonfigurasi (`models.providers.ollama.baseUrl` jika ditetapkan, jika tidak `http://127.0.0.1:11434`) |
| Auth        | Tidak memerlukan kunci                                                                                                |
| Persyaratan | Ollama harus berjalan dan sudah masuk dengan `ollama signin`                                                       |

Pilih **Ollama Web Search** saat `openclaw onboard` atau `openclaw configure --section web`, atau atur:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Untuk detail lengkap penyiapan dan perilaku, lihat [Ollama Web Search](/id/tools/ollama-search).
</Note>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Mode kompatibel OpenAI lama">
    <Warning>
    **Pemanggilan tool tidak andal dalam mode kompatibel OpenAI.** Gunakan mode ini hanya jika Anda memerlukan format OpenAI untuk proxy dan tidak bergantung pada perilaku pemanggilan tool native.
    </Warning>

    Jika Anda perlu menggunakan endpoint kompatibel OpenAI sebagai gantinya (misalnya, di balik proxy yang hanya mendukung format OpenAI), tetapkan `api: "openai-completions"` secara eksplisit:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // default: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Mode ini mungkin tidak mendukung streaming dan pemanggilan tool secara bersamaan. Anda mungkin perlu menonaktifkan streaming dengan `params: { streaming: false }` dalam konfigurasi model.

    Saat `api: "openai-completions"` digunakan dengan Ollama, OpenClaw secara default menyisipkan `options.num_ctx` agar Ollama tidak diam-diam kembali ke jendela konteks 4096. Jika proxy/upstream Anda menolak field `options` yang tidak dikenal, nonaktifkan perilaku ini:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Jendela konteks">
    Untuk model yang ditemukan secara otomatis, OpenClaw menggunakan jendela konteks yang dilaporkan oleh Ollama jika tersedia, jika tidak maka akan kembali ke jendela konteks Ollama default yang digunakan oleh OpenClaw.

    Anda dapat mengganti `contextWindow` dan `maxTokens` dalam konfigurasi penyedia eksplisit:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Model reasoning">
    OpenClaw memperlakukan model dengan nama seperti `deepseek-r1`, `reasoning`, atau `think` sebagai model yang mendukung reasoning secara default.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Tidak diperlukan konfigurasi tambahan -- OpenClaw menandainya secara otomatis.

  </Accordion>

  <Accordion title="Biaya model">
    Ollama gratis dan berjalan secara lokal, jadi semua biaya model ditetapkan ke $0. Ini berlaku untuk model yang ditemukan secara otomatis maupun yang didefinisikan secara manual.
  </Accordion>

  <Accordion title="Embedding memori">
    Plugin Ollama bawaan mendaftarkan penyedia embedding memori untuk
    [pencarian memori](/id/concepts/memory). Ini menggunakan URL dasar Ollama
    dan API key yang dikonfigurasi.

    | Properti      | Nilai               |
    | ------------- | ------------------- |
    | Model default | `nomic-embed-text`  |
    | Tarik otomatis     | Ya — model embedding ditarik secara otomatis jika belum ada secara lokal |

    Untuk memilih Ollama sebagai penyedia embedding pencarian memori:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Konfigurasi streaming">
    Integrasi Ollama OpenClaw menggunakan **API native Ollama** (`/api/chat`) secara default, yang sepenuhnya mendukung streaming dan pemanggilan tool secara bersamaan. Tidak diperlukan konfigurasi khusus.

    <Tip>
    Jika Anda perlu menggunakan endpoint yang kompatibel dengan OpenAI, lihat bagian "Mode kompatibel OpenAI lama" di atas. Streaming dan pemanggilan tool mungkin tidak berfungsi secara bersamaan dalam mode tersebut.
    </Tip>

  </Accordion>
</AccordionGroup>

## Pemecahan masalah

<AccordionGroup>
  <Accordion title="Ollama tidak terdeteksi">
    Pastikan Ollama sedang berjalan dan Anda telah menetapkan `OLLAMA_API_KEY` (atau profil autentikasi), dan Anda **tidak** mendefinisikan entri `models.providers.ollama` eksplisit:

    ```bash
    ollama serve
    ```

    Verifikasi bahwa API dapat diakses:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Tidak ada model yang tersedia">
    Jika model Anda tidak tercantum, tarik model tersebut secara lokal atau definisikan secara eksplisit di `models.providers.ollama`.

    ```bash
    ollama list  # Lihat yang terinstal
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Atau model lain
    ```

  </Accordion>

  <Accordion title="Koneksi ditolak">
    Periksa bahwa Ollama berjalan pada port yang benar:

    ```bash
    # Periksa apakah Ollama berjalan
    ps aux | grep ollama

    # Atau mulai ulang Ollama
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Bantuan lebih lanjut: [Pemecahan masalah](/id/help/troubleshooting) dan [FAQ](/id/help/faq).
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Penyedia model" href="/id/concepts/model-providers" icon="layers">
    Ikhtisar semua penyedia, ref model, dan perilaku failover.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/models" icon="brain">
    Cara memilih dan mengonfigurasi model.
  </Card>
  <Card title="Ollama Web Search" href="/id/tools/ollama-search" icon="magnifying-glass">
    Detail lengkap penyiapan dan perilaku untuk pencarian web bertenaga Ollama.
  </Card>
  <Card title="Konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi konfigurasi lengkap.
  </Card>
</CardGroup>
