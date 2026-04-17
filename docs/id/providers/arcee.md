---
read_when:
    - Anda ingin menggunakan Arcee AI dengan OpenClaw
    - Anda memerlukan variabel env API key atau pilihan auth CLI
summary: Penyiapan Arcee AI (auth + pemilihan model)
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T23:29:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) menyediakan akses ke keluarga model mixture-of-experts Trinity melalui API yang kompatibel dengan OpenAI. Semua model Trinity dilisensikan dengan Apache 2.0.

Model Arcee AI dapat diakses langsung melalui platform Arcee atau melalui [OpenRouter](/id/providers/openrouter).

| Property | Value                                                                                 |
| -------- | ------------------------------------------------------------------------------------- |
| Provider | `arcee`                                                                               |
| Auth     | `ARCEEAI_API_KEY` (langsung) atau `OPENROUTER_API_KEY` (melalui OpenRouter)           |
| API      | Kompatibel dengan OpenAI                                                              |
| Base URL | `https://api.arcee.ai/api/v1` (langsung) atau `https://openrouter.ai/api/v1` (OpenRouter) |

## Memulai

<Tabs>
  <Tab title="Langsung (platform Arcee)">
    <Steps>
      <Step title="Dapatkan API key">
        Buat API key di [Arcee AI](https://chat.arcee.ai/).
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="Setel model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Melalui OpenRouter">
    <Steps>
      <Step title="Dapatkan API key">
        Buat API key di [OpenRouter](https://openrouter.ai/keys).
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="Setel model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        Ref model yang sama berfungsi untuk penyiapan langsung maupun OpenRouter (misalnya `arcee/trinity-large-thinking`).
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Penyiapan non-interaktif

<Tabs>
  <Tab title="Langsung (platform Arcee)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="Melalui OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## Katalog bawaan

OpenClaw saat ini menyertakan katalog Arcee bawaan berikut:

| Model ref                      | Name                   | Input | Context | Cost (in/out per 1M) | Notes                                     |
| ------------------------------ | ---------------------- | ----- | ------- | -------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K    | $0.25 / $0.90        | Model default; reasoning diaktifkan       |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K    | $0.25 / $1.00        | Serbaguna; 400B parameter, 13B aktif      |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K    | $0.045 / $0.15       | Cepat dan hemat biaya; function calling   |

<Tip>
Preset onboarding menetapkan `arcee/trinity-large-thinking` sebagai model default.
</Tip>

## Fitur yang didukung

| Feature                                       | Supported                    |
| --------------------------------------------- | ---------------------------- |
| Streaming                                     | Ya                           |
| Penggunaan tool / function calling            | Ya                           |
| Output terstruktur (mode JSON dan JSON schema) | Ya                          |
| Thinking yang diperluas                        | Ya (Trinity Large Thinking)  |

<AccordionGroup>
  <Accordion title="Catatan environment">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `ARCEEAI_API_KEY`
    (atau `OPENROUTER_API_KEY`) tersedia untuk proses tersebut (misalnya, di
    `~/.openclaw/.env` atau melalui `env.shellEnv`).
  </Accordion>

  <Accordion title="Routing OpenRouter">
    Saat menggunakan model Arcee melalui OpenRouter, ref model `arcee/*` yang sama tetap berlaku.
    OpenClaw menangani routing secara transparan berdasarkan pilihan auth Anda. Lihat
    [dokumentasi provider OpenRouter](/id/providers/openrouter) untuk detail konfigurasi
    khusus OpenRouter.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/id/providers/openrouter" icon="shuffle">
    Akses model Arcee dan banyak model lainnya melalui satu API key.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
</CardGroup>
