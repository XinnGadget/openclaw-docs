---
read_when:
    - Anda ingin menggunakan model Mistral di OpenClaw
    - Anda memerlukan onboarding kunci API Mistral dan ref model
summary: Gunakan model Mistral dan transkripsi Voxtral dengan OpenClaw
title: Mistral
x-i18n:
    generated_at: "2026-04-12T23:31:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0474f55587909ce9bbdd47b881262edbeb1b07eb3ed52de1090a8ec4d260c97b
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw mendukung Mistral untuk routing model teks/gambar (`mistral/...`) dan
transkripsi audio melalui Voxtral dalam pemahaman media.
Mistral juga dapat digunakan untuk embedding memori (`memorySearch.provider = "mistral"`).

- Provider: `mistral`
- Autentikasi: `MISTRAL_API_KEY`
- API: Mistral Chat Completions (`https://api.mistral.ai/v1`)

## Memulai

<Steps>
  <Step title="Dapatkan kunci API Anda">
    Buat kunci API di [Mistral Console](https://console.mistral.ai/).
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice mistral-api-key
    ```

    Atau berikan kuncinya secara langsung:

    ```bash
    openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
    ```

  </Step>
  <Step title="Tetapkan model default">
    ```json5
    {
      env: { MISTRAL_API_KEY: "sk-..." },
      agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
    }
    ```
  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider mistral
    ```
  </Step>
</Steps>

## Katalog LLM bawaan

OpenClaw saat ini menyediakan katalog Mistral bawaan berikut:

| Ref model                        | Input       | Konteks | Output maks | Catatan                                                         |
| -------------------------------- | ----------- | ------- | ----------- | ---------------------------------------------------------------- |
| `mistral/mistral-large-latest`   | teks, gambar | 262,144 | 16,384      | Model default                                                    |
| `mistral/mistral-medium-2508`    | teks, gambar | 262,144 | 8,192       | Mistral Medium 3.1                                               |
| `mistral/mistral-small-latest`   | teks, gambar | 128,000 | 16,384      | Mistral Small 4; reasoning yang dapat disesuaikan melalui API `reasoning_effort` |
| `mistral/pixtral-large-latest`   | teks, gambar | 128,000 | 32,768      | Pixtral                                                          |
| `mistral/codestral-latest`       | teks        | 256,000 | 4,096       | Coding                                                           |
| `mistral/devstral-medium-latest` | teks        | 262,144 | 32,768      | Devstral 2                                                       |
| `mistral/magistral-small`        | teks        | 128,000 | 40,000      | reasoning diaktifkan                                             |

## Transkripsi audio (Voxtral)

Gunakan Voxtral untuk transkripsi audio melalui pipeline pemahaman media.

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

<Tip>
Jalur transkripsi media menggunakan `/v1/audio/transcriptions`. Model audio default untuk Mistral adalah `voxtral-mini-latest`.
</Tip>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Reasoning yang dapat disesuaikan (mistral-small-latest)">
    `mistral/mistral-small-latest` dipetakan ke Mistral Small 4 dan mendukung [reasoning yang dapat disesuaikan](https://docs.mistral.ai/capabilities/reasoning/adjustable) pada API Chat Completions melalui `reasoning_effort` (`none` meminimalkan thinking tambahan dalam output; `high` menampilkan jejak thinking penuh sebelum jawaban akhir).

    OpenClaw memetakan level **thinking** sesi ke API Mistral:

    | Level thinking OpenClaw                          | `reasoning_effort` Mistral |
    | ------------------------------------------------ | -------------------------- |
    | **off** / **minimal**                            | `none`                     |
    | **low** / **medium** / **high** / **xhigh** / **adaptive** | `high`             |

    <Note>
    Model katalog Mistral bawaan lainnya tidak menggunakan parameter ini. Tetap gunakan model `magistral-*` saat Anda menginginkan perilaku native Mistral yang mengutamakan reasoning.
    </Note>

  </Accordion>

  <Accordion title="Embedding memori">
    Mistral dapat melayani embedding memori melalui `/v1/embeddings` (model default: `mistral-embed`).

    ```json5
    {
      memorySearch: { provider: "mistral" },
    }
    ```

  </Accordion>

  <Accordion title="Autentikasi dan base URL">
    - Autentikasi Mistral menggunakan `MISTRAL_API_KEY`.
    - Base URL provider secara default adalah `https://api.mistral.ai/v1`.
    - Model default onboarding adalah `mistral/mistral-large-latest`.
    - Z.AI menggunakan autentikasi Bearer dengan kunci API Anda.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pemahaman media" href="/tools/media-understanding" icon="microphone">
    Penyiapan transkripsi audio dan pemilihan provider.
  </Card>
</CardGroup>
