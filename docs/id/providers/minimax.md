---
read_when:
    - Anda ingin menggunakan model MiniMax di OpenClaw
    - Anda memerlukan panduan penyiapan MiniMax
summary: Gunakan model MiniMax di OpenClaw
title: MiniMax
x-i18n:
    generated_at: "2026-04-12T23:31:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: ee9c89faf57384feb66cda30934000e5746996f24b59122db309318f42c22389
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

Provider MiniMax di OpenClaw default-nya menggunakan **MiniMax M2.7**.

MiniMax juga menyediakan:

- Sintesis suara bawaan melalui T2A v2
- Pemahaman gambar bawaan melalui `MiniMax-VL-01`
- Pembuatan musik bawaan melalui `music-2.5+`
- `web_search` bawaan melalui API pencarian MiniMax Coding Plan

Pembagian provider:

| ID Provider      | Auth    | Kapabilitas                                                    |
| ---------------- | ------- | -------------------------------------------------------------- |
| `minimax`        | API key | Teks, pembuatan gambar, pemahaman gambar, suara, pencarian web |
| `minimax-portal` | OAuth   | Teks, pembuatan gambar, pemahaman gambar                       |

## Jajaran model

| Model                    | Tipe             | Deskripsi                                 |
| ------------------------ | ---------------- | ----------------------------------------- |
| `MiniMax-M2.7`           | Chat (reasoning) | Model reasoning hosted default            |
| `MiniMax-M2.7-highspeed` | Chat (reasoning) | Tier reasoning M2.7 yang lebih cepat      |
| `MiniMax-VL-01`          | Vision           | Model pemahaman gambar                    |
| `image-01`               | Pembuatan gambar | Teks-ke-gambar dan pengeditan gambar-ke-gambar |
| `music-2.5+`             | Pembuatan musik  | Model musik default                       |
| `music-2.5`              | Pembuatan musik  | Tier pembuatan musik sebelumnya           |
| `music-2.0`              | Pembuatan musik  | Tier pembuatan musik lama                 |
| `MiniMax-Hailuo-2.3`     | Pembuatan video  | Alur teks-ke-video dan referensi gambar   |

## Memulai

Pilih metode auth yang Anda sukai dan ikuti langkah penyiapannya.

<Tabs>
  <Tab title="OAuth (Coding Plan)">
    **Paling cocok untuk:** penyiapan cepat dengan MiniMax Coding Plan melalui OAuth, tanpa memerlukan API key.

    <Tabs>
      <Tab title="Internasional">
        <Steps>
          <Step title="Jalankan onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-oauth
            ```

            Ini melakukan autentikasi terhadap `api.minimax.io`.
          </Step>
          <Step title="Verifikasi bahwa model tersedia">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="Jalankan onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-oauth
            ```

            Ini melakukan autentikasi terhadap `api.minimaxi.com`.
          </Step>
          <Step title="Verifikasi bahwa model tersedia">
            ```bash
            openclaw models list --provider minimax-portal
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    <Note>
    Penyiapan OAuth menggunakan ID provider `minimax-portal`. Ref model mengikuti format `minimax-portal/MiniMax-M2.7`.
    </Note>

    <Tip>
    Tautan referral untuk MiniMax Coding Plan (diskon 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
    </Tip>

  </Tab>

  <Tab title="API key">
    **Paling cocok untuk:** MiniMax hosted dengan API yang kompatibel dengan Anthropic.

    <Tabs>
      <Tab title="Internasional">
        <Steps>
          <Step title="Jalankan onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-global-api
            ```

            Ini mengonfigurasi `api.minimax.io` sebagai base URL.
          </Step>
          <Step title="Verifikasi bahwa model tersedia">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
      <Tab title="China">
        <Steps>
          <Step title="Jalankan onboarding">
            ```bash
            openclaw onboard --auth-choice minimax-cn-api
            ```

            Ini mengonfigurasi `api.minimaxi.com` sebagai base URL.
          </Step>
          <Step title="Verifikasi bahwa model tersedia">
            ```bash
            openclaw models list --provider minimax
            ```
          </Step>
        </Steps>
      </Tab>
    </Tabs>

    ### Contoh config

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
      models: {
        mode: "merge",
        providers: {
          minimax: {
            baseUrl: "https://api.minimax.io/anthropic",
            apiKey: "${MINIMAX_API_KEY}",
            api: "anthropic-messages",
            models: [
              {
                id: "MiniMax-M2.7",
                name: "MiniMax M2.7",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
              {
                id: "MiniMax-M2.7-highspeed",
                name: "MiniMax M2.7 Highspeed",
                reasoning: true,
                input: ["text", "image"],
                cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
                contextWindow: 204800,
                maxTokens: 131072,
              },
            ],
          },
        },
      },
    }
    ```

    <Warning>
    Pada jalur streaming yang kompatibel dengan Anthropic, OpenClaw menonaktifkan thinking MiniMax secara default kecuali Anda secara eksplisit menetapkan `thinking` sendiri. Endpoint streaming MiniMax mengeluarkan `reasoning_content` dalam potongan delta bergaya OpenAI, bukan blok thinking Anthropic native, yang dapat membocorkan reasoning internal ke output yang terlihat jika dibiarkan aktif secara implisit.
    </Warning>

    <Note>
    Penyiapan API key menggunakan ID provider `minimax`. Ref model mengikuti format `minimax/MiniMax-M2.7`.
    </Note>

  </Tab>
</Tabs>

## Konfigurasi melalui `openclaw configure`

Gunakan wizard config interaktif untuk menyiapkan MiniMax tanpa mengedit JSON:

<Steps>
  <Step title="Luncurkan wizard">
    ```bash
    openclaw configure
    ```
  </Step>
  <Step title="Pilih Model/auth">
    Pilih **Model/auth** dari menu.
  </Step>
  <Step title="Pilih opsi auth MiniMax">
    Pilih salah satu opsi MiniMax yang tersedia:

    | Opsi auth | Deskripsi |
    | --- | --- |
    | `minimax-global-oauth` | OAuth internasional (Coding Plan) |
    | `minimax-cn-oauth` | OAuth China (Coding Plan) |
    | `minimax-global-api` | API key internasional |
    | `minimax-cn-api` | API key China |

  </Step>
  <Step title="Pilih model default Anda">
    Pilih model default Anda saat diminta.
  </Step>
</Steps>

## Kapabilitas

### Pembuatan gambar

Plugin MiniMax mendaftarkan model `image-01` untuk tool `image_generate`. Model ini mendukung:

- **Pembuatan teks-ke-gambar** dengan kontrol rasio aspek
- **Pengeditan gambar-ke-gambar** (referensi subjek) dengan kontrol rasio aspek
- Hingga **9 gambar output** per permintaan
- Hingga **1 gambar referensi** per permintaan edit
- Rasio aspek yang didukung: `1:1`, `16:9`, `4:3`, `3:2`, `2:3`, `3:4`, `9:16`, `21:9`

Untuk menggunakan MiniMax untuk pembuatan gambar, setel sebagai provider pembuatan gambar:

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

Plugin menggunakan `MINIMAX_API_KEY` atau auth OAuth yang sama seperti model teks. Tidak diperlukan konfigurasi tambahan jika MiniMax sudah disiapkan.

Baik `minimax` maupun `minimax-portal` mendaftarkan `image_generate` dengan model
`image-01` yang sama. Penyiapan API key menggunakan `MINIMAX_API_KEY`; penyiapan OAuth dapat menggunakan
jalur auth `minimax-portal` bawaan sebagai gantinya.

Saat onboarding atau penyiapan API key menulis entri `models.providers.minimax`
yang eksplisit, OpenClaw mewujudkan `MiniMax-M2.7` dan
`MiniMax-M2.7-highspeed` dengan `input: ["text", "image"]`.

Katalog teks MiniMax bawaan yang dibundel sendiri tetap berupa metadata khusus teks sampai
config provider eksplisit tersebut ada. Pemahaman gambar diekspos secara terpisah
melalui provider media `MiniMax-VL-01` milik Plugin.

<Note>
Lihat [Pembuatan Gambar](/id/tools/image-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

### Pembuatan musik

Plugin `minimax` bawaan juga mendaftarkan pembuatan musik melalui
tool bersama `music_generate`.

- Model musik default: `minimax/music-2.5+`
- Juga mendukung `minimax/music-2.5` dan `minimax/music-2.0`
- Kontrol prompt: `lyrics`, `instrumental`, `durationSeconds`
- Format output: `mp3`
- Proses yang didukung sesi dilepas melalui alur task/status bersama, termasuk `action: "status"`

Untuk menggunakan MiniMax sebagai provider musik default:

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "minimax/music-2.5+",
      },
    },
  },
}
```

<Note>
Lihat [Pembuatan Musik](/id/tools/music-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

### Pembuatan video

Plugin `minimax` bawaan juga mendaftarkan pembuatan video melalui
tool bersama `video_generate`.

- Model video default: `minimax/MiniMax-Hailuo-2.3`
- Mode: teks-ke-video dan alur referensi gambar tunggal
- Mendukung `aspectRatio` dan `resolution`

Untuk menggunakan MiniMax sebagai provider video default:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

<Note>
Lihat [Pembuatan Video](/id/tools/video-generation) untuk parameter tool bersama, pemilihan provider, dan perilaku failover.
</Note>

### Pemahaman gambar

Plugin MiniMax mendaftarkan pemahaman gambar secara terpisah dari
katalog teks:

| ID Provider      | Model gambar default |
| ---------------- | -------------------- |
| `minimax`        | `MiniMax-VL-01`      |
| `minimax-portal` | `MiniMax-VL-01`      |

Itulah sebabnya perutean media otomatis dapat menggunakan pemahaman gambar MiniMax bahkan
ketika katalog provider teks bawaan yang dibundel masih menampilkan ref chat M2.7 khusus teks.

### Pencarian web

Plugin MiniMax juga mendaftarkan `web_search` melalui API pencarian
MiniMax Coding Plan.

- ID provider: `minimax`
- Hasil terstruktur: judul, URL, snippet, kueri terkait
- Variabel env yang disarankan: `MINIMAX_CODE_PLAN_KEY`
- Alias env yang diterima: `MINIMAX_CODING_API_KEY`
- Fallback kompatibilitas: `MINIMAX_API_KEY` ketika sudah menunjuk ke token coding-plan
- Penggunaan ulang region: `plugins.entries.minimax.config.webSearch.region`, lalu `MINIMAX_API_HOST`, lalu base URL provider MiniMax
- Pencarian tetap berada pada ID provider `minimax`; penyiapan OAuth CN/global tetap dapat mengarahkan region secara tidak langsung melalui `models.providers.minimax-portal.baseUrl`

Config berada di bawah `plugins.entries.minimax.config.webSearch.*`.

<Note>
Lihat [MiniMax Search](/id/tools/minimax-search) untuk konfigurasi dan penggunaan pencarian web lengkap.
</Note>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Opsi konfigurasi">
    | Opsi | Deskripsi |
    | --- | --- |
    | `models.providers.minimax.baseUrl` | Pilih `https://api.minimax.io/anthropic` (kompatibel dengan Anthropic); `https://api.minimax.io/v1` opsional untuk payload yang kompatibel dengan OpenAI |
    | `models.providers.minimax.api` | Pilih `anthropic-messages`; `openai-completions` opsional untuk payload yang kompatibel dengan OpenAI |
    | `models.providers.minimax.apiKey` | API key MiniMax (`MINIMAX_API_KEY`) |
    | `models.providers.minimax.models` | Tentukan `id`, `name`, `reasoning`, `contextWindow`, `maxTokens`, `cost` |
    | `agents.defaults.models` | Alias model yang Anda inginkan dalam allowlist |
    | `models.mode` | Gunakan `merge` jika Anda ingin menambahkan MiniMax bersama bawaan |
  </Accordion>

  <Accordion title="Default thinking">
    Pada `api: "anthropic-messages"`, OpenClaw menyisipkan `thinking: { type: "disabled" }` kecuali thinking sudah disetel secara eksplisit dalam params/config.

    Ini mencegah endpoint streaming MiniMax mengeluarkan `reasoning_content` dalam potongan delta bergaya OpenAI, yang akan membocorkan reasoning internal ke output yang terlihat.

  </Accordion>

  <Accordion title="Mode cepat">
    `/fast on` atau `params.fastMode: true` menulis ulang `MiniMax-M2.7` menjadi `MiniMax-M2.7-highspeed` pada jalur stream yang kompatibel dengan Anthropic.
  </Accordion>

  <Accordion title="Contoh fallback">
    **Paling cocok untuk:** mempertahankan model generasi terbaru terkuat Anda sebagai primary, lalu fail over ke MiniMax M2.7. Contoh di bawah menggunakan Opus sebagai primary konkret; ganti dengan model primary generasi terbaru pilihan Anda.

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-..." },
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": { alias: "primary" },
            "minimax/MiniMax-M2.7": { alias: "minimax" },
          },
          model: {
            primary: "anthropic/claude-opus-4-6",
            fallbacks: ["minimax/MiniMax-M2.7"],
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Detail penggunaan Coding Plan">
    - API penggunaan Coding Plan: `https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains` (memerlukan coding plan key).
    - OpenClaw menormalkan penggunaan coding-plan MiniMax ke tampilan `% tersisa` yang sama seperti yang digunakan provider lain. Field mentah `usage_percent` / `usagePercent` MiniMax adalah kuota tersisa, bukan kuota yang sudah digunakan, jadi OpenClaw membalikkannya. Field berbasis hitungan diprioritaskan jika ada.
    - Saat API mengembalikan `model_remains`, OpenClaw memprioritaskan entri model chat, menurunkan label jendela dari `start_time` / `end_time` bila diperlukan, dan menyertakan nama model yang dipilih dalam label paket agar jendela coding-plan lebih mudah dibedakan.
    - Snapshot penggunaan memperlakukan `minimax`, `minimax-cn`, dan `minimax-portal` sebagai permukaan kuota MiniMax yang sama, dan memprioritaskan OAuth MiniMax yang tersimpan sebelum fallback ke env vars Coding Plan key.
  </Accordion>
</AccordionGroup>

## Catatan

- Ref model mengikuti jalur auth:
  - Penyiapan API key: `minimax/<model>`
  - Penyiapan OAuth: `minimax-portal/<model>`
- Model chat default: `MiniMax-M2.7`
- Model chat alternatif: `MiniMax-M2.7-highspeed`
- Onboarding dan penyiapan API key langsung menulis definisi model eksplisit dengan `input: ["text", "image"]` untuk kedua varian M2.7
- Katalog provider bawaan saat ini mengekspos ref chat sebagai metadata khusus teks sampai config provider MiniMax eksplisit ada
- Perbarui nilai harga di `models.json` jika Anda memerlukan pelacakan biaya yang akurat
- Gunakan `openclaw models list` untuk mengonfirmasi ID provider saat ini, lalu ganti dengan `openclaw models set minimax/MiniMax-M2.7` atau `openclaw models set minimax-portal/MiniMax-M2.7`

<Tip>
Tautan referral untuk MiniMax Coding Plan (diskon 10%): [MiniMax Coding Plan](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
</Tip>

<Note>
Lihat [Provider model](/id/concepts/model-providers) untuk aturan provider.
</Note>

## Pemecahan masalah

<AccordionGroup>
  <Accordion title='"Model tidak dikenal: minimax/MiniMax-M2.7"'>
    Ini biasanya berarti **provider MiniMax belum dikonfigurasi** (tidak ada entri provider yang cocok dan tidak ada profil auth/env key MiniMax yang ditemukan). Perbaikan untuk deteksi ini ada di **2026.1.12**. Perbaiki dengan:

    - Upgrade ke **2026.1.12** (atau jalankan dari source `main`), lalu restart gateway.
    - Jalankan `openclaw configure` dan pilih opsi auth **MiniMax**, atau
    - Tambahkan blok `models.providers.minimax` atau `models.providers.minimax-portal` yang cocok secara manual, atau
    - Setel `MINIMAX_API_KEY`, `MINIMAX_OAUTH_TOKEN`, atau profil auth MiniMax agar provider yang cocok dapat disisipkan.

    Pastikan ID model **peka huruf besar-kecil**:

    - Jalur API key: `minimax/MiniMax-M2.7` atau `minimax/MiniMax-M2.7-highspeed`
    - Jalur OAuth: `minimax-portal/MiniMax-M2.7` atau `minimax-portal/MiniMax-M2.7-highspeed`

    Lalu periksa ulang dengan:

    ```bash
    openclaw models list
    ```

  </Accordion>
</AccordionGroup>

<Note>
Bantuan lebih lanjut: [Pemecahan masalah](/id/help/troubleshooting) dan [FAQ](/id/help/faq).
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pembuatan gambar" href="/id/tools/image-generation" icon="image">
    Parameter tool gambar bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan musik" href="/id/tools/music-generation" icon="music">
    Parameter tool musik bersama dan pemilihan provider.
  </Card>
  <Card title="Pembuatan video" href="/id/tools/video-generation" icon="video">
    Parameter tool video bersama dan pemilihan provider.
  </Card>
  <Card title="MiniMax Search" href="/id/tools/minimax-search" icon="magnifying-glass">
    Konfigurasi pencarian web melalui MiniMax Coding Plan.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Pemecahan masalah umum dan FAQ.
  </Card>
</CardGroup>
