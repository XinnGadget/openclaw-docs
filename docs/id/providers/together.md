---
read_when:
    - Anda ingin menggunakan Together AI dengan OpenClaw
    - Anda memerlukan env var kunci API atau opsi autentikasi CLI
summary: Penyiapan Together AI (autentikasi + pemilihan model)
title: Together AI
x-i18n:
    generated_at: "2026-04-12T23:32:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 33531a1646443ac2e46ee1fbfbb60ec71093611b022618106e8e5435641680ac
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) menyediakan akses ke model open-source terdepan
termasuk Llama, DeepSeek, Kimi, dan lainnya melalui API terpadu.

| Property | Value                         |
| -------- | ----------------------------- |
| Provider | `together`                    |
| Autentikasi | `TOGETHER_API_KEY`         |
| API      | Kompatibel OpenAI             |
| Base URL | `https://api.together.xyz/v1` |

## Memulai

<Steps>
  <Step title="Dapatkan kunci API">
    Buat kunci API di
    [api.together.ai/settings/api-keys](https://api.together.ai/settings/api-keys).
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice together-api-key
    ```
  </Step>
  <Step title="Tetapkan model default">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "together/moonshotai/Kimi-K2.5" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Contoh non-interaktif

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

<Note>
Preset onboarding menetapkan `together/moonshotai/Kimi-K2.5` sebagai model
default.
</Note>

## Katalog bawaan

OpenClaw menyediakan katalog Together bawaan berikut:

| Ref model                                                    | Nama                                   | Input       | Konteks    | Catatan                         |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | teks, gambar | 262,144   | Model default; reasoning diaktifkan |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | teks        | 202,752    | Model teks tujuan umum          |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | teks        | 131,072    | Model instruksi cepat           |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | teks, gambar | 10,000,000 | Multimodal                    |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | teks, gambar | 20,000,000 | Multimodal                    |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | teks        | 131,072    | Model teks umum                |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | teks        | 131,072    | Model reasoning                |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | teks        | 262,144    | Model teks Kimi sekunder       |

## Generasi video

Plugin `together` bawaan juga mendaftarkan generasi video melalui
tool bersama `video_generate`.

| Property             | Value                                 |
| -------------------- | ------------------------------------- |
| Model video default  | `together/Wan-AI/Wan2.2-T2V-A14B`     |
| Mode                 | teks-ke-video, referensi satu gambar  |
| Parameter yang didukung | `aspectRatio`, `resolution`        |

Untuk menggunakan Together sebagai provider video default:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

<Tip>
Lihat [Generasi Video](/id/tools/video-generation) untuk parameter tool bersama,
pemilihan provider, dan perilaku failover.
</Tip>

<AccordionGroup>
  <Accordion title="Catatan lingkungan">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan
    `TOGETHER_API_KEY` tersedia untuk proses tersebut (misalnya, di
    `~/.openclaw/.env` atau melalui `env.shellEnv`).

    <Warning>
    Key yang hanya ditetapkan di shell interaktif Anda tidak terlihat oleh proses
    gateway yang dikelola daemon. Gunakan `~/.openclaw/.env` atau config `env.shellEnv`
    untuk ketersediaan yang persisten.
    </Warning>

  </Accordion>

  <Accordion title="Pemecahan masalah">
    - Verifikasi bahwa key Anda berfungsi: `openclaw models list --provider together`
    - Jika model tidak muncul, pastikan kunci API ditetapkan di lingkungan yang benar
      untuk proses Gateway Anda.
    - Ref model menggunakan bentuk `together/<model-id>`.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Aturan provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Generasi video" href="/id/tools/video-generation" icon="video">
    Parameter tool generasi video bersama dan pemilihan provider.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Skema config lengkap termasuk pengaturan provider.
  </Card>
  <Card title="Together AI" href="https://together.ai" icon="arrow-up-right-from-square">
    Dashboard Together AI, dokumentasi API, dan harga.
  </Card>
</CardGroup>
