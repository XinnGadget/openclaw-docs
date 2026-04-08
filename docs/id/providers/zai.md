---
read_when:
    - Anda ingin menggunakan Z.AI / model GLM di OpenClaw
    - Anda memerlukan penyiapan `ZAI_API_KEY` yang sederhana
summary: Gunakan Z.AI (model GLM) dengan OpenClaw
title: Z.AI
x-i18n:
    generated_at: "2026-04-08T06:01:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66cbd9813ee28d202dcae34debab1b0cf9927793acb00743c1c62b48d9e381f9
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI adalah platform API untuk model **GLM**. Platform ini menyediakan REST API untuk GLM dan menggunakan kunci API
untuk autentikasi. Buat kunci API Anda di konsol Z.AI. OpenClaw menggunakan provider `zai`
dengan kunci API Z.AI.

## Penyiapan CLI

```bash
# Penyiapan kunci API generik dengan deteksi otomatis endpoint
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global, direkomendasikan untuk pengguna Coding Plan
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN (wilayah Tiongkok), direkomendasikan untuk pengguna Coding Plan
openclaw onboard --auth-choice zai-coding-cn

# API umum
openclaw onboard --auth-choice zai-global

# API umum CN (wilayah Tiongkok)
openclaw onboard --auth-choice zai-cn
```

## Cuplikan konfigurasi

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

`zai-api-key` memungkinkan OpenClaw mendeteksi endpoint Z.AI yang cocok dari kunci tersebut dan
menerapkan URL dasar yang benar secara otomatis. Gunakan pilihan regional yang eksplisit saat
Anda ingin memaksakan permukaan Coding Plan atau API umum tertentu.

## Katalog GLM bawaan

Saat ini OpenClaw mengisi provider `zai` bawaan dengan:

- `glm-5.1`
- `glm-5`
- `glm-5-turbo`
- `glm-5v-turbo`
- `glm-4.7`
- `glm-4.7-flash`
- `glm-4.7-flashx`
- `glm-4.6`
- `glm-4.6v`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`
- `glm-4.5v`

## Catatan

- Model GLM tersedia sebagai `zai/<model>` (contoh: `zai/glm-5`).
- Referensi model bawaan default: `zai/glm-5.1`
- ID `glm-5*` yang tidak dikenal tetap di-resolve secara forward pada jalur provider bawaan dengan
  menyintesis metadata milik provider dari template `glm-4.7` saat ID tersebut
  cocok dengan bentuk keluarga GLM-5 saat ini.
- `tool_stream` diaktifkan secara default untuk streaming pemanggilan alat Z.AI. Setel
  `agents.defaults.models["zai/<model>"].params.tool_stream` ke `false` untuk menonaktifkannya.
- Lihat [/providers/glm](/id/providers/glm) untuk ikhtisar keluarga model.
- Z.AI menggunakan autentikasi Bearer dengan kunci API Anda.
