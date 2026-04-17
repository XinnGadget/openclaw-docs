---
read_when:
    - Anda ingin menggunakan Qwen dengan OpenClaw
    - Anda sebelumnya menggunakan OAuth Qwen
summary: Gunakan Qwen Cloud melalui provider qwen bawaan OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-12T23:32:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**OAuth Qwen telah dihapus.** Integrasi OAuth tier gratis
(`qwen-portal`) yang menggunakan endpoint `portal.qwen.ai` tidak lagi tersedia.
Lihat [Issue #49557](https://github.com/openclaw/openclaw/issues/49557) untuk
latar belakang.

</Warning>

OpenClaw sekarang memperlakukan Qwen sebagai provider bawaan kelas satu dengan ID kanonis
`qwen`. Provider bawaan ini menargetkan endpoint Qwen Cloud / Alibaba DashScope dan
Coding Plan serta tetap membuat ID lama `modelstudio` berfungsi sebagai
alias kompatibilitas.

- Provider: `qwen`
- Env var yang disarankan: `QWEN_API_KEY`
- Juga diterima untuk kompatibilitas: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Gaya API: kompatibel dengan OpenAI

<Tip>
Jika Anda menginginkan `qwen3.6-plus`, gunakan endpoint **Standard (pay-as-you-go)**.
Dukungan Coding Plan dapat tertinggal dari katalog publik.
</Tip>

## Memulai

Pilih jenis paket Anda dan ikuti langkah setup.

<Tabs>
  <Tab title="Coding Plan (langganan)">
    **Paling cocok untuk:** akses berbasis langganan melalui Qwen Coding Plan.

    <Steps>
      <Step title="Dapatkan kunci API Anda">
        Buat atau salin kunci API dari [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Jalankan onboarding">
        Untuk endpoint **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        Untuk endpoint **China**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    ID `auth-choice` lama `modelstudio-*` dan ref model `modelstudio/...` tetap
    berfungsi sebagai alias kompatibilitas, tetapi alur setup baru sebaiknya menggunakan
    ID `auth-choice` `qwen-*` kanonis dan ref model `qwen/...`.
    </Note>

  </Tab>

  <Tab title="Standard (pay-as-you-go)">
    **Paling cocok untuk:** akses pay-as-you-go melalui endpoint Standard Model Studio, termasuk model seperti `qwen3.6-plus` yang mungkin tidak tersedia di Coding Plan.

    <Steps>
      <Step title="Dapatkan kunci API Anda">
        Buat atau salin kunci API dari [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Jalankan onboarding">
        Untuk endpoint **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        Untuk endpoint **China**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    ID `auth-choice` lama `modelstudio-*` dan ref model `modelstudio/...` tetap
    berfungsi sebagai alias kompatibilitas, tetapi alur setup baru sebaiknya menggunakan
    ID `auth-choice` `qwen-*` kanonis dan ref model `qwen/...`.
    </Note>

  </Tab>
</Tabs>

## Jenis paket dan endpoint

| Paket                      | Region | Pilihan auth               | Endpoint                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | China  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (langganan)    | China  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (langganan)    | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Provider otomatis memilih endpoint berdasarkan pilihan auth Anda. Pilihan kanonis
menggunakan keluarga `qwen-*`; `modelstudio-*` tetap hanya untuk kompatibilitas.
Anda dapat melakukan override dengan `baseUrl` kustom di config.

<Tip>
**Kelola kunci:** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**Dokumen:** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## Katalog bawaan

OpenClaw saat ini menyediakan katalog Qwen bawaan berikut. Katalog yang dikonfigurasi
sadar endpoint: config Coding Plan menghilangkan model yang hanya diketahui berfungsi pada
endpoint Standard.

| Model ref                   | Input       | Konteks   | Catatan                                            |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | text, image | 1,000,000 | Model default                                      |
| `qwen/qwen3.6-plus`         | text, image | 1,000,000 | Utamakan endpoint Standard saat Anda membutuhkan model ini |
| `qwen/qwen3-max-2026-01-23` | text        | 262,144   | Lini Qwen Max                                      |
| `qwen/qwen3-coder-next`     | text        | 262,144   | Coding                                             |
| `qwen/qwen3-coder-plus`     | text        | 1,000,000 | Coding                                             |
| `qwen/MiniMax-M2.5`         | text        | 1,000,000 | Reasoning diaktifkan                               |
| `qwen/glm-5`                | text        | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | text        | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | text, image | 262,144   | Moonshot AI melalui Alibaba                        |

<Note>
Ketersediaan tetap dapat bervariasi menurut endpoint dan paket billing meskipun model
tersebut ada di katalog bawaan.
</Note>

## Add-on multimodal

Ekstensi `qwen` juga mengekspos capability multimodal pada endpoint DashScope **Standard**
(bukan endpoint Coding Plan):

- **Pemahaman video** melalui `qwen-vl-max-latest`
- **Pembuatan video Wan** melalui `wan2.6-t2v` (default), `wan2.6-i2v`, `wan2.6-r2v`, `wan2.6-r2v-flash`, `wan2.7-r2v`

Untuk menggunakan Qwen sebagai provider video default:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
Lihat [Video Generation](/id/tools/video-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

## Lanjutan

<AccordionGroup>
  <Accordion title="Pemahaman gambar dan video">
    Plugin Qwen bawaan mendaftarkan media-understanding untuk gambar dan video
    pada endpoint DashScope **Standard** (bukan endpoint Coding Plan).

    | Properti        | Nilai                |
    | --------------- | -------------------- |
    | Model           | `qwen-vl-max-latest` |
    | Input yang didukung | Gambar, video     |

    Media-understanding diselesaikan otomatis dari auth Qwen yang dikonfigurasi — tidak
    diperlukan config tambahan. Pastikan Anda menggunakan endpoint Standard (pay-as-you-go)
    untuk dukungan media-understanding.

  </Accordion>

  <Accordion title="Ketersediaan Qwen 3.6 Plus">
    `qwen3.6-plus` tersedia pada endpoint Model Studio Standard (pay-as-you-go):

    - China: `dashscope.aliyuncs.com/compatible-mode/v1`
    - Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    Jika endpoint Coding Plan mengembalikan error "unsupported model" untuk
    `qwen3.6-plus`, beralihlah ke Standard (pay-as-you-go), bukan pasangan
    endpoint/kunci Coding Plan.

  </Accordion>

  <Accordion title="Rencana capability">
    Ekstensi `qwen` sedang diposisikan sebagai rumah vendor untuk seluruh permukaan Qwen
    Cloud, bukan hanya model coding/text.

    - **Model text/chat:** sudah dibundel
    - **Pemanggilan tool, output terstruktur, thinking:** diwarisi dari transport yang kompatibel dengan OpenAI
    - **Pembuatan gambar:** direncanakan pada lapisan provider-plugin
    - **Pemahaman gambar/video:** sudah dibundel pada endpoint Standard
    - **Speech/audio:** direncanakan pada lapisan provider-plugin
    - **Memory embeddings/reranking:** direncanakan melalui permukaan adaptor embedding
    - **Pembuatan video:** sudah dibundel melalui capability video-generation bersama

  </Accordion>

  <Accordion title="Detail pembuatan video">
    Untuk pembuatan video, OpenClaw memetakan region Qwen yang dikonfigurasi ke host
    DashScope AIGC yang cocok sebelum mengirim job:

    - Global/Intl: `https://dashscope-intl.aliyuncs.com`
    - China: `https://dashscope.aliyuncs.com`

    Artinya `models.providers.qwen.baseUrl` normal yang mengarah ke salah satu host
    Qwen Coding Plan atau Standard tetap menjaga pembuatan video pada endpoint video
    DashScope regional yang benar.

    Batas pembuatan video Qwen bawaan saat ini:

    - Hingga **1** video output per permintaan
    - Hingga **1** gambar input
    - Hingga **4** video input
    - Hingga durasi **10 detik**
    - Mendukung `size`, `aspectRatio`, `resolution`, `audio`, dan `watermark`
    - Mode gambar/video referensi saat ini memerlukan **URL `http(s)` jarak jauh**. Path file lokal ditolak sejak awal karena endpoint video DashScope tidak menerima buffer lokal yang diunggah untuk referensi tersebut.

  </Accordion>

  <Accordion title="Kompatibilitas penggunaan streaming">
    Endpoint native Model Studio mengiklankan kompatibilitas penggunaan streaming pada
    transport bersama `openai-completions`. OpenClaw kini menentukannya berdasarkan
    capability endpoint, sehingga ID provider kustom yang kompatibel dengan DashScope dan menargetkan host native yang sama mewarisi perilaku streaming-usage yang sama alih-alih
    mensyaratkan ID provider `qwen` bawaan secara khusus.

    Kompatibilitas penggunaan native-streaming berlaku untuk host Coding Plan dan
    host Standard yang kompatibel dengan DashScope:

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Region endpoint multimodal">
    Permukaan multimodal (pemahaman video dan pembuatan video Wan) menggunakan
    endpoint DashScope **Standard**, bukan endpoint Coding Plan:

    - Base URL Standard Global/Intl: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - Base URL Standard China: `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Environment dan setup daemon">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `QWEN_API_KEY` tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/id/providers/alibaba" icon="cloud">
    Provider ModelStudio lama dan catatan migrasi.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Pemecahan masalah umum dan FAQ.
  </Card>
</CardGroup>
