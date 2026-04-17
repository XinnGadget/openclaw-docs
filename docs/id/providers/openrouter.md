---
read_when:
    - Anda menginginkan satu kunci API untuk banyak LLM
    - Anda ingin menjalankan model melalui OpenRouter di OpenClaw
summary: Gunakan API terpadu OpenRouter untuk mengakses banyak model di OpenClaw
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T23:32:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter menyediakan **API terpadu** yang merutekan permintaan ke banyak model di balik satu
endpoint dan kunci API. OpenRouter kompatibel dengan OpenAI, sehingga sebagian besar SDK OpenAI dapat digunakan hanya dengan mengganti base URL.

## Memulai

<Steps>
  <Step title="Dapatkan kunci API Anda">
    Buat kunci API di [openrouter.ai/keys](https://openrouter.ai/keys).
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="(Opsional) Beralih ke model tertentu">
    Onboarding secara default menggunakan `openrouter/auto`. Pilih model konkret nanti:

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## Contoh config

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## Referensi model

<Note>
Ref model mengikuti pola `openrouter/<provider>/<model>`. Untuk daftar lengkap
provider dan model yang tersedia, lihat [/concepts/model-providers](/id/concepts/model-providers).
</Note>

## Auth dan header

OpenRouter menggunakan token Bearer dengan kunci API Anda di balik layar.

Pada permintaan OpenRouter nyata (`https://openrouter.ai/api/v1`), OpenClaw juga menambahkan
header atribusi aplikasi OpenRouter yang terdokumentasi:

| Header                    | Nilai                 |
| ------------------------- | --------------------- |
| `HTTP-Referer`            | `https://openclaw.ai` |
| `X-OpenRouter-Title`      | `OpenClaw`            |
| `X-OpenRouter-Categories` | `cli-agent`           |

<Warning>
Jika Anda mengarahkan ulang provider OpenRouter ke proxy atau base URL lain, OpenClaw
**tidak** menyisipkan header khusus OpenRouter tersebut atau penanda cache Anthropic.
</Warning>

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Penanda cache Anthropic">
    Pada rute OpenRouter yang terverifikasi, ref model Anthropic mempertahankan
    penanda `cache_control` Anthropic khusus OpenRouter yang digunakan OpenClaw untuk
    pemakaian ulang prompt-cache yang lebih baik pada blok prompt system/developer.
  </Accordion>

  <Accordion title="Penyisipan thinking / reasoning">
    Pada rute non-`auto` yang didukung, OpenClaw memetakan level thinking yang dipilih ke
    payload reasoning proxy OpenRouter. Petunjuk model yang tidak didukung dan
    `openrouter/auto` melewati penyisipan reasoning tersebut.
  </Accordion>

  <Accordion title="Pembentukan permintaan khusus OpenAI">
    OpenRouter tetap berjalan melalui jalur kompatibel OpenAI bergaya proxy, sehingga
    pembentukan permintaan khusus OpenAI native seperti `serviceTier`, `store` pada Responses,
    payload kompatibilitas reasoning OpenAI, dan petunjuk prompt-cache tidak diteruskan.
  </Accordion>

  <Accordion title="Rute berbasis Gemini">
    Ref OpenRouter berbasis Gemini tetap berada di jalur proxy-Gemini: OpenClaw mempertahankan
    sanitasi thought-signature Gemini di sana, tetapi tidak mengaktifkan validasi replay Gemini native atau penulisan ulang bootstrap.
  </Accordion>

  <Accordion title="Metadata perutean provider">
    Jika Anda meneruskan perutean provider OpenRouter di bawah parameter model, OpenClaw akan meneruskannya
    sebagai metadata perutean OpenRouter sebelum wrapper stream bersama dijalankan.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Referensi config lengkap untuk agen, model, dan provider.
  </Card>
</CardGroup>
