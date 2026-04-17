---
read_when:
    - Anda menginginkan satu API key untuk banyak LLM
    - Anda ingin menjalankan model melalui Kilo Gateway di OpenClaw
summary: Gunakan API terpadu Kilo Gateway untuk mengakses banyak model di OpenClaw
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T23:31:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

Kilo Gateway menyediakan **API terpadu** yang merutekan permintaan ke banyak model di balik satu
endpoint dan API key. Ini kompatibel dengan OpenAI, sehingga sebagian besar SDK OpenAI dapat digunakan dengan mengganti base URL.

| Properti | Nilai                              |
| -------- | ---------------------------------- |
| Provider | `kilocode`                         |
| Auth     | `KILOCODE_API_KEY`                 |
| API      | Kompatibel dengan OpenAI           |
| Base URL | `https://api.kilo.ai/api/gateway/` |

## Memulai

<Steps>
  <Step title="Buat akun">
    Buka [app.kilo.ai](https://app.kilo.ai), masuk atau buat akun, lalu buka API Keys dan buat key baru.
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    Atau setel variabel environment secara langsung:

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## Model default

Model default adalah `kilocode/kilo/auto`, model smart-routing milik provider
yang dikelola oleh Kilo Gateway.

<Note>
OpenClaw memperlakukan `kilocode/kilo/auto` sebagai ref default yang stabil, tetapi tidak
mempublikasikan pemetaan tugas-ke-model-upstream berbasis sumber untuk rute tersebut. Rute upstream yang tepat
di balik `kilocode/kilo/auto` dimiliki oleh Kilo Gateway, bukan
di-hardcode di OpenClaw.
</Note>

## Model yang tersedia

OpenClaw secara dinamis menemukan model yang tersedia dari Kilo Gateway saat startup. Gunakan
`/models kilocode` untuk melihat daftar lengkap model yang tersedia untuk akun Anda.

Model apa pun yang tersedia di Gateway dapat digunakan dengan prefiks `kilocode/`:

| Ref model                              | Catatan                            |
| -------------------------------------- | ---------------------------------- |
| `kilocode/kilo/auto`                   | Default — smart routing            |
| `kilocode/anthropic/claude-sonnet-4`   | Anthropic melalui Kilo             |
| `kilocode/openai/gpt-5.4`              | OpenAI melalui Kilo                |
| `kilocode/google/gemini-3-pro-preview` | Google melalui Kilo                |
| ...dan masih banyak lagi               | Gunakan `/models kilocode` untuk melihat semuanya |

<Tip>
Saat startup, OpenClaw melakukan kueri `GET https://api.kilo.ai/api/gateway/models` dan menggabungkan
model yang ditemukan sebelum katalog fallback statis. Fallback bawaan selalu
mencakup `kilocode/kilo/auto` (`Kilo Auto`) dengan `input: ["text", "image"]`,
`reasoning: true`, `contextWindow: 1000000`, dan `maxTokens: 128000`.
</Tip>

## Contoh config

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport dan kompatibilitas">
    Kilo Gateway didokumentasikan dalam source sebagai kompatibel dengan OpenRouter, sehingga tetap berada di
    jalur kompatibel OpenAI bergaya proxy, bukan pembentukan permintaan OpenAI native.

    - Ref Kilo berbasis Gemini tetap berada di jalur proxy-Gemini, sehingga OpenClaw mempertahankan
      sanitasi thought-signature Gemini di sana tanpa mengaktifkan validasi replay Gemini native
      atau penulisan ulang bootstrap.
    - Kilo Gateway menggunakan token Bearer dengan API key Anda di balik layar.

  </Accordion>

  <Accordion title="Wrapper stream dan reasoning">
    Wrapper stream bersama Kilo menambahkan header aplikasi provider dan menormalkan
    payload reasoning proxy untuk ref model konkret yang didukung.

    <Warning>
    `kilocode/kilo/auto` dan petunjuk lain yang tidak mendukung proxy-reasoning melewati injeksi
    reasoning. Jika Anda memerlukan dukungan reasoning, gunakan ref model konkret seperti
    `kilocode/anthropic/claude-sonnet-4`.
    </Warning>

  </Accordion>

  <Accordion title="Pemecahan masalah">
    - Jika discovery model gagal saat startup, OpenClaw kembali ke katalog statis bawaan yang berisi `kilocode/kilo/auto`.
    - Pastikan API key Anda valid dan akun Kilo Anda mengaktifkan model yang diinginkan.
    - Saat Gateway berjalan sebagai daemon, pastikan `KILOCODE_API_KEY` tersedia untuk proses tersebut (misalnya di `~/.openclaw/.env` atau melalui `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi konfigurasi OpenClaw lengkap.
  </Card>
  <Card title="Kilo Gateway" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    Dashboard Kilo Gateway, API key, dan pengelolaan akun.
  </Card>
</CardGroup>
