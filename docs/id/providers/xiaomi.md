---
read_when:
    - Anda ingin menggunakan model Xiaomi MiMo di OpenClaw
    - Anda memerlukan penyiapan `XIAOMI_API_KEY`
summary: Gunakan model Xiaomi MiMo dengan OpenClaw
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-12T23:33:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd5a526764c796da7e1fff61301bc2ec618e1cf3857894ba2ef4b6dd9c4dc339
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo adalah platform API untuk model **MiMo**. OpenClaw menggunakan endpoint
Xiaomi yang kompatibel dengan OpenAI dengan autentikasi API key.

| Properti | Nilai                           |
| -------- | ------------------------------- |
| Provider | `xiaomi`                        |
| Auth     | `XIAOMI_API_KEY`                |
| API      | Kompatibel dengan OpenAI        |
| Base URL | `https://api.xiaomimimo.com/v1` |

## Memulai

<Steps>
  <Step title="Dapatkan API key">
    Buat API key di [konsol Xiaomi MiMo](https://platform.xiaomimimo.com/#/console/api-keys).
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice xiaomi-api-key
    ```

    Atau berikan key secara langsung:

    ```bash
    openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
    ```

  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider xiaomi
    ```
  </Step>
</Steps>

## Model yang tersedia

| Ref model              | Input       | Konteks   | Output maks | Reasoning | Catatan       |
| ---------------------- | ----------- | --------- | ----------- | --------- | ------------- |
| `xiaomi/mimo-v2-flash` | text        | 262,144   | 8,192       | Tidak     | Model default |
| `xiaomi/mimo-v2-pro`   | text        | 1,048,576 | 32,000      | Ya        | Konteks besar |
| `xiaomi/mimo-v2-omni`  | text, image | 262,144   | 32,000      | Ya        | Multimodal    |

<Tip>
Ref model default adalah `xiaomi/mimo-v2-flash`. Provider disisipkan secara otomatis saat `XIAOMI_API_KEY` disetel atau profil auth tersedia.
</Tip>

## Contoh config

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Perilaku penyisipan otomatis">
    Provider `xiaomi` disisipkan secara otomatis saat `XIAOMI_API_KEY` disetel di environment Anda atau profil auth tersedia. Anda tidak perlu mengonfigurasi provider secara manual kecuali ingin mengoverride metadata model atau base URL.
  </Accordion>

  <Accordion title="Detail model">
    - **mimo-v2-flash** — ringan dan cepat, ideal untuk tugas teks umum. Tidak mendukung reasoning.
    - **mimo-v2-pro** — mendukung reasoning dengan jendela konteks 1M token untuk beban kerja dokumen panjang.
    - **mimo-v2-omni** — model multimodal dengan reasoning yang menerima input teks dan gambar.

    <Note>
    Semua model menggunakan prefiks `xiaomi/` (misalnya `xiaomi/mimo-v2-pro`).
    </Note>

  </Accordion>

  <Accordion title="Pemecahan masalah">
    - Jika model tidak muncul, pastikan `XIAOMI_API_KEY` sudah disetel dan valid.
    - Saat Gateway berjalan sebagai daemon, pastikan key tersedia untuk proses tersebut (misalnya di `~/.openclaw/.env` atau melalui `env.shellEnv`).

    <Warning>
    Key yang hanya disetel di shell interaktif Anda tidak terlihat oleh proses gateway yang dikelola daemon. Gunakan config `~/.openclaw/.env` atau `env.shellEnv` agar tersedia secara persisten.
    </Warning>

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
  <Card title="Konsol Xiaomi MiMo" href="https://platform.xiaomimimo.com" icon="arrow-up-right-from-square">
    Dashboard Xiaomi MiMo dan pengelolaan API key.
  </Card>
</CardGroup>
