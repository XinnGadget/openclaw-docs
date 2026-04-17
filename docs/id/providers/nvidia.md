---
read_when:
    - Anda ingin menggunakan model terbuka di OpenClaw secara gratis
    - Anda perlu menyiapkan `NVIDIA_API_KEY`
summary: Gunakan API yang kompatibel dengan OpenAI milik NVIDIA di OpenClaw
title: NVIDIA
x-i18n:
    generated_at: "2026-04-12T23:31:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45048037365138141ee82cefa0c0daaf073a1c2ae3aa7b23815f6ca676fc0d3e
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA menyediakan API yang kompatibel dengan OpenAI di `https://integrate.api.nvidia.com/v1` untuk
model terbuka secara gratis. Lakukan autentikasi dengan API key dari
[build.nvidia.com](https://build.nvidia.com/settings/api-keys).

## Memulai

<Steps>
  <Step title="Dapatkan API key Anda">
    Buat API key di [build.nvidia.com](https://build.nvidia.com/settings/api-keys).
  </Step>
  <Step title="Ekspor key dan jalankan onboarding">
    ```bash
    export NVIDIA_API_KEY="nvapi-..."
    openclaw onboard --auth-choice skip
    ```
  </Step>
  <Step title="Setel model NVIDIA">
    ```bash
    openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
    ```
  </Step>
</Steps>

<Warning>
Jika Anda meneruskan `--token` alih-alih env var, nilainya akan masuk ke riwayat shell dan
output `ps`. Jika memungkinkan, utamakan env var `NVIDIA_API_KEY`.
</Warning>

## Contoh config

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## Katalog bawaan

| Ref model                                  | Nama                         | Konteks | Output maks |
| ------------------------------------------ | ---------------------------- | ------- | ----------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192       |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144 | 8,192       |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608 | 8,192       |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752 | 8,192       |

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Perilaku aktif otomatis">
    Provider aktif secara otomatis saat env var `NVIDIA_API_KEY` disetel.
    Tidak diperlukan config provider eksplisit selain key tersebut.
  </Accordion>

  <Accordion title="Katalog dan harga">
    Katalog bawaan bersifat statis. Biaya default ke `0` dalam source karena NVIDIA
    saat ini menawarkan akses API gratis untuk model yang tercantum.
  </Accordion>

  <Accordion title="Endpoint yang kompatibel dengan OpenAI">
    NVIDIA menggunakan endpoint completions standar `/v1`. Tooling apa pun yang kompatibel dengan OpenAI
    seharusnya langsung berfungsi dengan base URL NVIDIA.
  </Accordion>
</AccordionGroup>

<Tip>
Model NVIDIA saat ini gratis untuk digunakan. Periksa
[build.nvidia.com](https://build.nvidia.com/) untuk ketersediaan terbaru dan
detail rate limit.
</Tip>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Referensi config lengkap untuk agen, model, dan provider.
  </Card>
</CardGroup>
