---
read_when:
    - Anda ingin menggunakan Chutes dengan OpenClaw
    - Anda memerlukan jalur penyiapan OAuth atau API key
    - Anda ingin model default, alias, atau perilaku penemuan model
summary: Penyiapan Chutes (OAuth atau API key, penemuan model, alias)
title: Chutes
x-i18n:
    generated_at: "2026-04-12T23:29:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 07c52b1d1d2792412e6daabc92df5310434b3520116d9e0fd2ad26bfa5297e1c
    source_path: providers/chutes.md
    workflow: 15
---

# Chutes

[Chutes](https://chutes.ai) menyediakan katalog model open-source melalui
API yang kompatibel dengan OpenAI. OpenClaw mendukung auth OAuth berbasis browser dan
auth API key langsung untuk provider `chutes` bawaan.

| Property | Value                        |
| -------- | ---------------------------- |
| Provider | `chutes`                     |
| API      | Kompatibel dengan OpenAI     |
| Base URL | `https://llm.chutes.ai/v1`   |
| Auth     | OAuth atau API key (lihat di bawah) |

## Memulai

<Tabs>
  <Tab title="OAuth">
    <Steps>
      <Step title="Jalankan alur onboarding OAuth">
        ```bash
        openclaw onboard --auth-choice chutes
        ```
        OpenClaw meluncurkan alur browser secara lokal, atau menampilkan alur URL + tempel-pengalihan
        pada host jarak jauh/headless. Token OAuth diperbarui otomatis melalui profil auth OpenClaw.
      </Step>
      <Step title="Verifikasi model default">
        Setelah onboarding, model default disetel ke
        `chutes/zai-org/GLM-4.7-TEE` dan katalog Chutes bawaan
        didaftarkan.
      </Step>
    </Steps>
  </Tab>
  <Tab title="API key">
    <Steps>
      <Step title="Dapatkan API key">
        Buat key di
        [chutes.ai/settings/api-keys](https://chutes.ai/settings/api-keys).
      </Step>
      <Step title="Jalankan alur onboarding API key">
        ```bash
        openclaw onboard --auth-choice chutes-api-key
        ```
      </Step>
      <Step title="Verifikasi model default">
        Setelah onboarding, model default disetel ke
        `chutes/zai-org/GLM-4.7-TEE` dan katalog Chutes bawaan
        didaftarkan.
      </Step>
    </Steps>
  </Tab>
</Tabs>

<Note>
Kedua jalur auth mendaftarkan katalog Chutes bawaan dan menyetel model default ke
`chutes/zai-org/GLM-4.7-TEE`. Variabel environment runtime: `CHUTES_API_KEY`,
`CHUTES_OAUTH_TOKEN`.
</Note>

## Perilaku penemuan

Saat auth Chutes tersedia, OpenClaw mengueri katalog Chutes dengan
kredensial tersebut dan menggunakan model yang ditemukan. Jika penemuan gagal, OpenClaw
kembali menggunakan katalog statis bawaan agar onboarding dan startup tetap berfungsi.

## Alias default

OpenClaw mendaftarkan tiga alias praktis untuk katalog Chutes bawaan:

| Alias           | Model target                                          |
| --------------- | ----------------------------------------------------- |
| `chutes-fast`   | `chutes/zai-org/GLM-4.7-FP8`                          |
| `chutes-pro`    | `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes-vision` | `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |

## Katalog pemula bawaan

Katalog fallback bawaan mencakup ref Chutes saat ini:

| Model ref                                             |
| ----------------------------------------------------- |
| `chutes/zai-org/GLM-4.7-TEE`                          |
| `chutes/zai-org/GLM-5-TEE`                            |
| `chutes/deepseek-ai/DeepSeek-V3.2-TEE`                |
| `chutes/deepseek-ai/DeepSeek-R1-0528-TEE`             |
| `chutes/moonshotai/Kimi-K2.5-TEE`                     |
| `chutes/chutesai/Mistral-Small-3.2-24B-Instruct-2506` |
| `chutes/Qwen/Qwen3-Coder-Next-TEE`                    |
| `chutes/openai/gpt-oss-120b-TEE`                      |

## Contoh konfigurasi

```json5
{
  agents: {
    defaults: {
      model: { primary: "chutes/zai-org/GLM-4.7-TEE" },
      models: {
        "chutes/zai-org/GLM-4.7-TEE": { alias: "Chutes GLM 4.7" },
        "chutes/deepseek-ai/DeepSeek-V3.2-TEE": { alias: "Chutes DeepSeek V3.2" },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Override OAuth">
    Anda dapat menyesuaikan alur OAuth dengan variabel environment opsional:

    | Variable | Purpose |
    | -------- | ------- |
    | `CHUTES_CLIENT_ID` | ID klien OAuth kustom |
    | `CHUTES_CLIENT_SECRET` | Secret klien OAuth kustom |
    | `CHUTES_OAUTH_REDIRECT_URI` | URI pengalihan kustom |
    | `CHUTES_OAUTH_SCOPES` | Scope OAuth kustom |

    Lihat [dokumentasi OAuth Chutes](https://chutes.ai/docs/sign-in-with-chutes/overview)
    untuk persyaratan aplikasi pengalihan dan bantuan.

  </Accordion>

  <Accordion title="Catatan">
    - Penemuan berbasis API key dan OAuth sama-sama menggunakan id provider `chutes`.
    - Model Chutes didaftarkan sebagai `chutes/<model-id>`.
    - Jika penemuan gagal saat startup, katalog statis bawaan digunakan secara otomatis.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Aturan provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Skema konfigurasi lengkap termasuk pengaturan provider.
  </Card>
  <Card title="Chutes" href="https://chutes.ai" icon="arrow-up-right-from-square">
    Dashboard Chutes dan dokumentasi API.
  </Card>
  <Card title="API key Chutes" href="https://chutes.ai/settings/api-keys" icon="key">
    Buat dan kelola API key Chutes.
  </Card>
</CardGroup>
