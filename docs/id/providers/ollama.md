---
read_when:
    - Anda ingin menjalankan OpenClaw dengan model cloud atau lokal melalui Ollama
    - Anda memerlukan panduan penyiapan dan konfigurasi Ollama
summary: Jalankan OpenClaw dengan Ollama (model cloud dan lokal)
title: Ollama
x-i18n:
    generated_at: "2026-04-08T09:12:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: d3295a7c879d3636a2ffdec05aea6e670e54a990ef52bd9b0cae253bc24aa3f7
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

Ollama adalah runtime LLM lokal yang memudahkan Anda menjalankan model open-source di mesin Anda. OpenClaw terintegrasi dengan API native Ollama (`/api/chat`), mendukung streaming dan pemanggilan tool, serta dapat menemukan model Ollama lokal secara otomatis saat Anda ikut serta dengan `OLLAMA_API_KEY` (atau profil autentikasi) dan tidak mendefinisikan entri `models.providers.ollama` secara eksplisit.

<Warning>
**Pengguna Ollama jarak jauh**: Jangan gunakan URL kompatibel OpenAI `/v1` (`http://host:11434/v1`) dengan OpenClaw. Ini merusak pemanggilan tool dan model dapat mengeluarkan JSON tool mentah sebagai teks biasa. Gunakan URL API native Ollama sebagai gantinya: `baseUrl: "http://host:11434"` (tanpa `/v1`).
</Warning>

## Mulai cepat

### Onboarding (disarankan)

Cara tercepat untuk menyiapkan Ollama adalah melalui onboarding:

```bash
openclaw onboard
```

Pilih **Ollama** dari daftar provider. Onboarding akan:

1. Menanyakan URL dasar Ollama tempat instance Anda dapat dijangkau (default `http://127.0.0.1:11434`).
2. Memungkinkan Anda memilih **Cloud + Local** (model cloud dan model lokal) atau **Local** (hanya model lokal).
3. Membuka alur masuk browser jika Anda memilih **Cloud + Local** dan belum masuk ke ollama.com.
4. Menemukan model yang tersedia dan menyarankan default.
5. Melakukan auto-pull pada model yang dipilih jika model tersebut belum tersedia secara lokal.

Mode non-interaktif juga didukung:

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

### Penyiapan manual

1. Instal Ollama: [https://ollama.com/download](https://ollama.com/download)

2. Pull model lokal jika Anda ingin inferensi lokal:

```bash
ollama pull gemma4
# atau
ollama pull gpt-oss:20b
# atau
ollama pull llama3.3
```

3. Jika Anda juga menginginkan model cloud, masuklah:

```bash
ollama signin
```

4. Jalankan onboarding dan pilih `Ollama`:

```bash
openclaw onboard
```

- `Local`: hanya model lokal
- `Cloud + Local`: model lokal plus model cloud
- Model cloud seperti `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, dan `glm-5.1:cloud` **tidak** memerlukan `ollama pull` lokal

OpenClaw saat ini menyarankan:

- default lokal: `gemma4`
- default cloud: `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud`

5. Jika Anda lebih memilih penyiapan manual, aktifkan Ollama untuk OpenClaw secara langsung (nilai apa pun dapat digunakan; Ollama tidak memerlukan kunci asli):

```bash
# Tetapkan variabel lingkungan
export OLLAMA_API_KEY="ollama-local"

# Atau konfigurasi di file config Anda
openclaw config set models.providers.ollama.apiKey "ollama-local"
```

6. Periksa atau ganti model:

```bash
openclaw models list
openclaw models set ollama/gemma4
```

7. Atau tetapkan default di config:

```json5
{
  agents: {
    defaults: {
      model: { primary: "ollama/gemma4" },
    },
  },
}
```

## Penemuan model (provider implisit)

Saat Anda menetapkan `OLLAMA_API_KEY` (atau profil autentikasi) dan **tidak** mendefinisikan `models.providers.ollama`, OpenClaw menemukan model dari instance Ollama lokal di `http://127.0.0.1:11434`:

- Mengueri `/api/tags`
- Menggunakan lookup `/api/show` best-effort untuk membaca `contextWindow` dan mendeteksi kapabilitas (termasuk vision) jika tersedia
- Model dengan kapabilitas `vision` yang dilaporkan oleh `/api/show` ditandai sebagai mampu-gambar (`input: ["text", "image"]`), sehingga OpenClaw secara otomatis menyisipkan gambar ke prompt untuk model tersebut
- Menandai `reasoning` dengan heuristik nama model (`r1`, `reasoning`, `think`)
- Menetapkan `maxTokens` ke batas max-token default Ollama yang digunakan oleh OpenClaw
- Menetapkan semua biaya ke `0`

Ini menghindari entri model manual sambil menjaga katalog tetap selaras dengan instance Ollama lokal.

Untuk melihat model apa saja yang tersedia:

```bash
ollama list
openclaw models list
```

Untuk menambahkan model baru, cukup pull model tersebut dengan Ollama:

```bash
ollama pull mistral
```

Model baru akan ditemukan secara otomatis dan tersedia untuk digunakan.

Jika Anda menetapkan `models.providers.ollama` secara eksplisit, penemuan otomatis dilewati dan Anda harus mendefinisikan model secara manual (lihat di bawah).

## Konfigurasi

### Penyiapan dasar (penemuan implisit)

Cara paling sederhana untuk mengaktifkan Ollama adalah melalui variabel lingkungan:

```bash
export OLLAMA_API_KEY="ollama-local"
```

### Penyiapan eksplisit (model manual)

Gunakan config eksplisit ketika:

- Ollama berjalan di host/port lain.
- Anda ingin memaksa window konteks atau daftar model tertentu.
- Anda ingin definisi model sepenuhnya manual.

```json5
{
  models: {
    providers: {
      ollama: {
        baseUrl: "http://ollama-host:11434",
        apiKey: "ollama-local",
        api: "ollama",
        models: [
          {
            id: "gpt-oss:20b",
            name: "GPT-OSS 20B",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 8192,
            maxTokens: 8192 * 10
          }
        ]
      }
    }
  }
}
```

Jika `OLLAMA_API_KEY` ditetapkan, Anda dapat menghilangkan `apiKey` di entri provider dan OpenClaw akan mengisinya untuk pemeriksaan ketersediaan.

### URL dasar kustom (config eksplisit)

Jika Ollama berjalan di host atau port yang berbeda (config eksplisit menonaktifkan penemuan otomatis, jadi definisikan model secara manual):

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
Jangan tambahkan `/v1` ke URL. Jalur `/v1` menggunakan mode kompatibel OpenAI, di mana pemanggilan tool tidak andal. Gunakan URL dasar Ollama tanpa sufiks path.
</Warning>

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

## Model cloud

Model cloud memungkinkan Anda menjalankan model yang di-host di cloud (misalnya `kimi-k2.5:cloud`, `minimax-m2.7:cloud`, `glm-5.1:cloud`) bersama model lokal Anda.

Untuk menggunakan model cloud, pilih mode **Cloud + Local** selama penyiapan. Wizard memeriksa apakah Anda sudah masuk dan membuka alur masuk browser bila diperlukan. Jika autentikasi tidak dapat diverifikasi, wizard akan kembali ke default model lokal.

Anda juga dapat masuk langsung di [ollama.com/signin](https://ollama.com/signin).

## Ollama Web Search

OpenClaw juga mendukung **Ollama Web Search** sebagai provider `web_search`
bawaan.

- Ini menggunakan host Ollama yang Anda konfigurasi (`models.providers.ollama.baseUrl` saat
  ditetapkan, atau `http://127.0.0.1:11434` jika tidak).
- Ini tidak memerlukan key.
- Ini mengharuskan Ollama berjalan dan sudah masuk dengan `ollama signin`.

Pilih **Ollama Web Search** selama `openclaw onboard` atau
`openclaw configure --section web`, atau tetapkan:

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

Untuk detail penyiapan dan perilaku lengkap, lihat [Ollama Web Search](/id/tools/ollama-search).

## Lanjutan

### Model reasoning

OpenClaw memperlakukan model dengan nama seperti `deepseek-r1`, `reasoning`, atau `think` sebagai mampu-reasoning secara default:

```bash
ollama pull deepseek-r1:32b
```

### Biaya Model

Ollama gratis dan berjalan secara lokal, jadi semua biaya model ditetapkan ke $0.

### Konfigurasi Streaming

Integrasi Ollama OpenClaw menggunakan **API native Ollama** (`/api/chat`) secara default, yang sepenuhnya mendukung streaming dan pemanggilan tool secara bersamaan. Tidak diperlukan konfigurasi khusus.

#### Mode Kompatibel OpenAI Lama

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

Mode ini mungkin tidak mendukung streaming + pemanggilan tool secara bersamaan. Anda mungkin perlu menonaktifkan streaming dengan `params: { streaming: false }` di config model.

Saat `api: "openai-completions"` digunakan dengan Ollama, OpenClaw menyisipkan `options.num_ctx` secara default agar Ollama tidak diam-diam kembali ke window konteks 4096. Jika proxy/upstream Anda menolak field `options` yang tidak dikenal, nonaktifkan perilaku ini:

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

### Window konteks

Untuk model yang ditemukan otomatis, OpenClaw menggunakan window konteks yang dilaporkan oleh Ollama jika tersedia, jika tidak maka akan kembali ke window konteks default Ollama yang digunakan oleh OpenClaw. Anda dapat mengganti `contextWindow` dan `maxTokens` di config provider eksplisit.

## Pemecahan masalah

### Ollama tidak terdeteksi

Pastikan Ollama sedang berjalan dan Anda telah menetapkan `OLLAMA_API_KEY` (atau profil autentikasi), serta Anda **tidak** mendefinisikan entri `models.providers.ollama` secara eksplisit:

```bash
ollama serve
```

Dan pastikan API dapat diakses:

```bash
curl http://localhost:11434/api/tags
```

### Tidak ada model yang tersedia

Jika model Anda tidak terdaftar, lakukan salah satu dari berikut:

- Pull model secara lokal, atau
- Definisikan model secara eksplisit di `models.providers.ollama`.

Untuk menambahkan model:

```bash
ollama list  # Lihat apa yang terinstal
ollama pull gemma4
ollama pull gpt-oss:20b
ollama pull llama3.3     # Atau model lain
```

### Koneksi ditolak

Periksa bahwa Ollama berjalan pada port yang benar:

```bash
# Periksa apakah Ollama sedang berjalan
ps aux | grep ollama

# Atau mulai ulang Ollama
ollama serve
```

## Lihat juga

- [Provider Model](/id/concepts/model-providers) - Ikhtisar semua provider
- [Pemilihan Model](/id/concepts/models) - Cara memilih model
- [Konfigurasi](/id/gateway/configuration) - Referensi config lengkap
