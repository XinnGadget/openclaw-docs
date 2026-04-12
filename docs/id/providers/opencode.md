---
read_when:
    - Anda menginginkan akses model yang dihosting OpenCode
    - Anda ingin memilih antara katalog Zen dan Go
summary: Gunakan katalog OpenCode Zen dan Go dengan OpenClaw
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T23:32:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode mengekspos dua katalog hosted di OpenClaw:

| Catalog | Prefix            | Provider runtime |
| ------- | ----------------- | ---------------- |
| **Zen** | `opencode/...`    | `opencode`       |
| **Go**  | `opencode-go/...` | `opencode-go`    |

Kedua katalog menggunakan kunci API OpenCode yang sama. OpenClaw menjaga id provider runtime
tetap terpisah agar routing per model di hulu tetap benar, tetapi onboarding dan dokumentasi memperlakukannya
sebagai satu penyiapan OpenCode.

## Memulai

<Tabs>
  <Tab title="Katalog Zen">
    **Paling cocok untuk:** proxy multi-model OpenCode yang dikurasi (Claude, GPT, Gemini).

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        Atau berikan key secara langsung:

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Tetapkan model Zen sebagai default">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Katalog Go">
    **Paling cocok untuk:** jajaran Kimi, GLM, dan MiniMax yang dihosting OpenCode.

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        Atau berikan key secara langsung:

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Tetapkan model Go sebagai default">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Contoh config

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## Katalog

### Zen

| Property         | Value                                                                   |
| ---------------- | ----------------------------------------------------------------------- |
| Provider runtime | `opencode`                                                              |
| Contoh model     | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| Property         | Value                                                                    |
| ---------------- | ------------------------------------------------------------------------ |
| Provider runtime | `opencode-go`                                                            |
| Contoh model     | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Alias kunci API">
    `OPENCODE_ZEN_API_KEY` juga didukung sebagai alias untuk `OPENCODE_API_KEY`.
  </Accordion>

  <Accordion title="Kredensial bersama">
    Memasukkan satu key OpenCode saat penyiapan menyimpan kredensial untuk kedua provider
    runtime. Anda tidak perlu melakukan onboarding untuk setiap katalog secara terpisah.
  </Accordion>

  <Accordion title="Penagihan dan dashboard">
    Anda masuk ke OpenCode, menambahkan detail penagihan, dan menyalin kunci API Anda. Penagihan
    dan ketersediaan katalog dikelola dari dashboard OpenCode.
  </Accordion>

  <Accordion title="Perilaku replay Gemini">
    Ref OpenCode yang didukung Gemini tetap berada di jalur proxy-Gemini, sehingga OpenClaw tetap
    mempertahankan sanitasi thought-signature Gemini di sana tanpa mengaktifkan validasi replay Gemini native atau penulisan ulang bootstrap.
  </Accordion>

  <Accordion title="Perilaku replay non-Gemini">
    Ref OpenCode non-Gemini mempertahankan kebijakan replay kompatibel OpenAI yang minimal.
  </Accordion>
</AccordionGroup>

<Tip>
Memasukkan satu key OpenCode saat penyiapan menyimpan kredensial untuk provider runtime Zen dan
Go, jadi Anda hanya perlu melakukan onboarding sekali.
</Tip>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Referensi config lengkap untuk agent, model, dan provider.
  </Card>
</CardGroup>
