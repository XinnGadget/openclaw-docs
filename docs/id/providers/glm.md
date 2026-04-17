---
read_when:
    - Anda ingin model GLM di OpenClaw
    - Anda memerlukan konvensi penamaan model dan penyiapannya
summary: Ikhtisar keluarga model GLM + cara menggunakannya di OpenClaw
title: GLM (Zhipu)
x-i18n:
    generated_at: "2026-04-12T23:30:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: b38f0896c900fae3cf3458ff99938d73fa46973a057d1dd373ae960cb7d2e9b5
    source_path: providers/glm.md
    workflow: 15
---

# Model GLM

GLM adalah **keluarga model** (bukan perusahaan) yang tersedia melalui platform Z.AI. Di OpenClaw, model
GLM diakses melalui provider `zai` dan ID model seperti `zai/glm-5`.

## Memulai

<Steps>
  <Step title="Pilih jalur autentikasi dan jalankan onboarding">
    Pilih opsi onboarding yang sesuai dengan paket dan region Z.AI Anda:

    | Auth choice | Paling cocok untuk |
    | ----------- | ------------------ |
    | `zai-api-key` | Penyiapan kunci API umum dengan deteksi endpoint otomatis |
    | `zai-coding-global` | Pengguna Coding Plan (global) |
    | `zai-coding-cn` | Pengguna Coding Plan (region China) |
    | `zai-global` | API umum (global) |
    | `zai-cn` | API umum (region China) |

    ```bash
    # Contoh: deteksi otomatis umum
    openclaw onboard --auth-choice zai-api-key

    # Contoh: Coding Plan global
    openclaw onboard --auth-choice zai-coding-global
    ```

  </Step>
  <Step title="Tetapkan GLM sebagai model default">
    ```bash
    openclaw config set agents.defaults.model.primary "zai/glm-5.1"
    ```
  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider zai
    ```
  </Step>
</Steps>

## Contoh config

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

<Tip>
`zai-api-key` memungkinkan OpenClaw mendeteksi endpoint Z.AI yang cocok dari key tersebut dan
menerapkan base URL yang benar secara otomatis. Gunakan pilihan regional eksplisit saat
Anda ingin memaksa permukaan Coding Plan atau API umum tertentu.
</Tip>

## Model GLM bawaan

OpenClaw saat ini mengisi provider `zai` bawaan dengan ref GLM berikut:

| Model           | Model            |
| --------------- | ---------------- |
| `glm-5.1`       | `glm-4.7`        |
| `glm-5`         | `glm-4.7-flash`  |
| `glm-5-turbo`   | `glm-4.7-flashx` |
| `glm-5v-turbo`  | `glm-4.6`        |
| `glm-4.5`       | `glm-4.6v`       |
| `glm-4.5-air`   |                  |
| `glm-4.5-flash` |                  |
| `glm-4.5v`      |                  |

<Note>
Ref model bawaan default adalah `zai/glm-5.1`. Versi dan ketersediaan GLM
dapat berubah; periksa dokumentasi Z.AI untuk yang terbaru.
</Note>

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Deteksi endpoint otomatis">
    Saat Anda menggunakan opsi autentikasi `zai-api-key`, OpenClaw memeriksa format key
    untuk menentukan base URL Z.AI yang benar. Pilihan regional eksplisit
    (`zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn`) mengoverride
    deteksi otomatis dan langsung menetapkan endpoint.
  </Accordion>

  <Accordion title="Detail provider">
    Model GLM disajikan oleh provider runtime `zai`. Untuk konfigurasi provider lengkap,
    endpoint regional, dan kapabilitas tambahan, lihat
    [dokumentasi provider Z.AI](/id/providers/zai).
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider Z.AI" href="/id/providers/zai" icon="server">
    Konfigurasi provider Z.AI lengkap dan endpoint regional.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
</CardGroup>
