---
read_when:
    - Anda ingin menggunakan Cloudflare AI Gateway dengan OpenClaw
    - Anda memerlukan ID akun, ID gateway, atau variabel env API key
summary: Penyiapan Cloudflare AI Gateway (auth + pemilihan model)
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:30:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12e9589fe74e6a6335370b9cf2361a464876a392a33f8317d7fd30c3f163b2e5
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

Cloudflare AI Gateway berada di depan API provider dan memungkinkan Anda menambahkan analitik, caching, dan kontrol. Untuk Anthropic, OpenClaw menggunakan Anthropic Messages API melalui endpoint Gateway Anda.

| Property      | Value                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------- |
| Provider      | `cloudflare-ai-gateway`                                                                  |
| Base URL      | `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`               |
| Default model | `cloudflare-ai-gateway/claude-sonnet-4-5`                                                |
| API key       | `CLOUDFLARE_AI_GATEWAY_API_KEY` (API key provider Anda untuk permintaan melalui Gateway) |

<Note>
Untuk model Anthropic yang dirutekan melalui Cloudflare AI Gateway, gunakan **Anthropic API key** Anda sebagai key provider.
</Note>

## Memulai

<Steps>
  <Step title="Setel API key provider dan detail Gateway">
    Jalankan onboarding dan pilih opsi auth Cloudflare AI Gateway:

    ```bash
    openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
    ```

    Ini akan meminta ID akun, ID gateway, dan API key Anda.

  </Step>
  <Step title="Setel model default">
    Tambahkan model ke konfigurasi OpenClaw Anda:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
        },
      },
    }
    ```

  </Step>
  <Step title="Verifikasi model tersedia">
    ```bash
    openclaw models list --provider cloudflare-ai-gateway
    ```
  </Step>
</Steps>

## Contoh non-interaktif

Untuk penyiapan terotomatisasi atau CI, berikan semua nilai di command line:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Gateway terautentikasi">
    Jika Anda mengaktifkan autentikasi Gateway di Cloudflare, tambahkan header `cf-aig-authorization`. Ini **selain** API key provider Anda.

    ```json5
    {
      models: {
        providers: {
          "cloudflare-ai-gateway": {
            headers: {
              "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
            },
          },
        },
      },
    }
    ```

    <Tip>
    Header `cf-aig-authorization` mengautentikasi ke Cloudflare Gateway itu sendiri, sedangkan API key provider (misalnya, key Anthropic Anda) mengautentikasi ke provider upstream.
    </Tip>

  </Accordion>

  <Accordion title="Catatan environment">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `CLOUDFLARE_AI_GATEWAY_API_KEY` tersedia untuk proses tersebut.

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
