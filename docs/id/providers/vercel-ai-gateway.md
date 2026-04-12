---
read_when:
    - Anda ingin menggunakan Vercel AI Gateway dengan OpenClaw
    - Anda memerlukan variabel env API key atau pilihan auth CLI
summary: Penyiapan Vercel AI Gateway (auth + pemilihan model)
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:33:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 48c206a645d7a62e201a35ae94232323c8570fdae63129231c38d363ea78a60b
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

[Vercel AI Gateway](https://vercel.com/ai-gateway) menyediakan API terpadu untuk
mengakses ratusan model melalui satu endpoint.

| Properti      | Nilai                            |
| ------------- | -------------------------------- |
| Provider      | `vercel-ai-gateway`              |
| Auth          | `AI_GATEWAY_API_KEY`             |
| API           | Kompatibel dengan Anthropic Messages |
| Katalog model | Ditemukan otomatis melalui `/v1/models` |

<Tip>
OpenClaw menemukan otomatis katalog Gateway `/v1/models`, sehingga
`/models vercel-ai-gateway` mencakup ref model saat ini seperti
`vercel-ai-gateway/openai/gpt-5.4`.
</Tip>

## Memulai

<Steps>
  <Step title="Setel API key">
    Jalankan onboarding dan pilih opsi auth AI Gateway:

    ```bash
    openclaw onboard --auth-choice ai-gateway-api-key
    ```

  </Step>
  <Step title="Setel model default">
    Tambahkan model ke config OpenClaw Anda:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
        },
      },
    }
    ```

  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider vercel-ai-gateway
    ```
  </Step>
</Steps>

## Contoh non-interaktif

Untuk penyiapan skrip atau CI, berikan semua nilai di baris perintah:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## Singkatan ID model

OpenClaw menerima ref model singkat Vercel Claude dan menormalkannya saat
runtime:

| Input singkat                      | Ref model yang dinormalisasi                 |
| ---------------------------------- | -------------------------------------------- |
| `vercel-ai-gateway/claude-opus-4.6` | `vercel-ai-gateway/anthropic/claude-opus-4.6` |
| `vercel-ai-gateway/opus-4.6`        | `vercel-ai-gateway/anthropic/claude-opus-4-6` |

<Tip>
Anda dapat menggunakan singkatan atau ref model lengkap di
konfigurasi Anda. OpenClaw menyelesaikan bentuk kanonis secara otomatis.
</Tip>

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Variabel environment untuk proses daemon">
    Jika Gateway OpenClaw berjalan sebagai daemon (launchd/systemd), pastikan
    `AI_GATEWAY_API_KEY` tersedia untuk proses tersebut.

    <Warning>
    Key yang hanya disetel di `~/.profile` tidak akan terlihat oleh daemon launchd/systemd
    kecuali environment tersebut diimpor secara eksplisit. Setel key di
    `~/.openclaw/.env` atau melalui `env.shellEnv` untuk memastikan proses gateway dapat
    membacanya.
    </Warning>

  </Accordion>

  <Accordion title="Perutean provider">
    Vercel AI Gateway merutekan permintaan ke provider upstream berdasarkan prefiks
    ref model. Misalnya, `vercel-ai-gateway/anthropic/claude-opus-4.6` dirutekan
    melalui Anthropic, sementara `vercel-ai-gateway/openai/gpt-5.4` dirutekan melalui
    OpenAI. Satu `AI_GATEWAY_API_KEY` Anda menangani autentikasi untuk semua
    provider upstream.
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
