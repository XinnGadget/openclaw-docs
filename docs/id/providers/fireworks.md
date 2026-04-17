---
read_when:
    - Anda ingin menggunakan Fireworks dengan OpenClaw
    - Anda memerlukan variabel env API key Fireworks atau ID model default
summary: Penyiapan Fireworks (auth + pemilihan model)
title: Fireworks
x-i18n:
    generated_at: "2026-04-12T23:30:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1a85d9507c19e275fdd846a303d844eda8045d008774d4dde1eae408e8716b6f
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

[Fireworks](https://fireworks.ai) menyediakan model open-weight dan model yang dirutekan melalui API yang kompatibel dengan OpenAI. OpenClaw menyertakan Plugin provider Fireworks bawaan.

| Property      | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Provider      | `fireworks`                                            |
| Auth          | `FIREWORKS_API_KEY`                                    |
| API           | Chat/completions yang kompatibel dengan OpenAI         |
| Base URL      | `https://api.fireworks.ai/inference/v1`                |
| Default model | `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` |

## Memulai

<Steps>
  <Step title="Siapkan auth Fireworks melalui onboarding">
    ```bash
    openclaw onboard --auth-choice fireworks-api-key
    ```

    Ini menyimpan key Fireworks Anda di konfigurasi OpenClaw dan menetapkan model awal Fire Pass sebagai default.

  </Step>
  <Step title="Verifikasi model tersedia">
    ```bash
    openclaw models list --provider fireworks
    ```
  </Step>
</Steps>

## Contoh non-interaktif

Untuk penyiapan terotomatisasi atau CI, berikan semua nilai di command line:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## Katalog bawaan

| Model ref                                              | Name                        | Input      | Context | Max output | Notes                                      |
| ------------------------------------------------------ | --------------------------- | ---------- | ------- | ---------- | ------------------------------------------ |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | text,image | 256,000 | 256,000    | Model awal bawaan default di Fireworks     |

<Tip>
Jika Fireworks menerbitkan model yang lebih baru seperti rilis Qwen atau Gemma terbaru, Anda dapat langsung beralih ke model tersebut dengan menggunakan ID model Fireworks-nya tanpa harus menunggu pembaruan katalog bawaan.
</Tip>

## ID model Fireworks kustom

OpenClaw juga menerima ID model Fireworks dinamis. Gunakan ID model atau router persis seperti yang ditampilkan oleh Fireworks dan beri prefiks `fireworks/`.

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Cara kerja prefiks ID model">
    Setiap ref model Fireworks di OpenClaw dimulai dengan `fireworks/` lalu diikuti oleh ID atau path router persis dari platform Fireworks. Contohnya:

    - Model router: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`
    - Model langsung: `fireworks/accounts/fireworks/models/<model-name>`

    OpenClaw menghapus prefiks `fireworks/` saat membangun permintaan API dan mengirim path sisanya ke endpoint Fireworks.

  </Accordion>

  <Accordion title="Catatan environment">
    Jika Gateway berjalan di luar shell interaktif Anda, pastikan `FIREWORKS_API_KEY` juga tersedia untuk proses tersebut.

    <Warning>
    Key yang hanya ada di `~/.profile` tidak akan membantu daemon launchd/systemd kecuali environment tersebut juga diimpor ke sana. Setel key di `~/.openclaw/.env` atau melalui `env.shellEnv` untuk memastikan proses gateway dapat membacanya.
    </Warning>

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Pemecahan masalah umum dan FAQ.
  </Card>
</CardGroup>
