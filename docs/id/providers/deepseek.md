---
read_when:
    - Anda ingin menggunakan DeepSeek dengan OpenClaw
    - Anda memerlukan variabel env API key atau pilihan auth CLI
summary: Penyiapan DeepSeek (auth + pemilihan model)
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T23:30:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) menyediakan model AI canggih dengan API yang kompatibel dengan OpenAI.

| Property | Value                      |
| -------- | -------------------------- |
| Provider | `deepseek`                 |
| Auth     | `DEEPSEEK_API_KEY`         |
| API      | Kompatibel dengan OpenAI   |
| Base URL | `https://api.deepseek.com` |

## Memulai

<Steps>
  <Step title="Dapatkan API key Anda">
    Buat API key di [platform.deepseek.com](https://platform.deepseek.com/api_keys).
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    Ini akan meminta API key Anda dan menetapkan `deepseek/deepseek-chat` sebagai model default.

  </Step>
  <Step title="Verifikasi model tersedia">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="Penyiapan non-interaktif">
    Untuk instalasi terotomatisasi atau headless, berikan semua flag secara langsung:

    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice deepseek-api-key \
      --deepseek-api-key "$DEEPSEEK_API_KEY" \
      --skip-health \
      --accept-risk
    ```

  </Accordion>
</AccordionGroup>

<Warning>
Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `DEEPSEEK_API_KEY`
tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui
`env.shellEnv`).
</Warning>

## Katalog bawaan

| Model ref                    | Name              | Input | Context | Max output | Notes                                             |
| ---------------------------- | ----------------- | ----- | ------- | ---------- | ------------------------------------------------- |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | text  | 131,072 | 8,192      | Model default; surface DeepSeek V3.2 non-thinking |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text  | 131,072 | 65,536     | Surface V3.2 dengan reasoning                     |

<Tip>
Kedua model bawaan saat ini mengiklankan kompatibilitas penggunaan streaming di source.
</Tip>

## Contoh konfigurasi

```json5
{
  env: { DEEPSEEK_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "deepseek/deepseek-chat" },
    },
  },
}
```

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Referensi konfigurasi lengkap untuk agen, model, dan provider.
  </Card>
</CardGroup>
