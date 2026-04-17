---
read_when:
    - Anda ingin menggunakan model Volcano Engine atau Doubao dengan OpenClaw
    - Anda memerlukan penyiapan kunci API Volcengine
summary: Penyiapan Volcano Engine (model Doubao, endpoint umum + coding)
title: Volcengine (Doubao)
x-i18n:
    generated_at: "2026-04-12T23:33:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: a21f390da719f79c88c6d55a7d952d35c2ce5ff26d910c9f10020132cd7d2f4c
    source_path: providers/volcengine.md
    workflow: 15
---

# Volcengine (Doubao)

Provider Volcengine memberikan akses ke model Doubao dan model pihak ketiga
yang dihosting di Volcano Engine, dengan endpoint terpisah untuk beban kerja
umum dan coding.

| Detail    | Value                                               |
| --------- | --------------------------------------------------- |
| Provider  | `volcengine` (umum) + `volcengine-plan` (coding)    |
| Autentikasi | `VOLCANO_ENGINE_API_KEY`                          |
| API       | Kompatibel OpenAI                                   |

## Memulai

<Steps>
  <Step title="Tetapkan kunci API">
    Jalankan onboarding interaktif:

    ```bash
    openclaw onboard --auth-choice volcengine-api-key
    ```

    Ini mendaftarkan provider umum (`volcengine`) dan coding (`volcengine-plan`) dari satu kunci API.

  </Step>
  <Step title="Tetapkan model default">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "volcengine-plan/ark-code-latest" },
        },
      },
    }
    ```
  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider volcengine
    openclaw models list --provider volcengine-plan
    ```
  </Step>
</Steps>

<Tip>
Untuk penyiapan non-interaktif (CI, scripting), berikan key secara langsung:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice volcengine-api-key \
  --volcengine-api-key "$VOLCANO_ENGINE_API_KEY"
```

</Tip>

## Provider dan endpoint

| Provider          | Endpoint                                  | Kasus penggunaan |
| ----------------- | ----------------------------------------- | ---------------- |
| `volcengine`      | `ark.cn-beijing.volces.com/api/v3`        | Model umum       |
| `volcengine-plan` | `ark.cn-beijing.volces.com/api/coding/v3` | Model coding     |

<Note>
Kedua provider dikonfigurasi dari satu kunci API. Penyiapan mendaftarkan keduanya secara otomatis.
</Note>

## Model yang tersedia

<Tabs>
  <Tab title="Umum (volcengine)">
    | Ref model                                    | Nama                            | Input       | Konteks |
    | -------------------------------------------- | ------------------------------- | ----------- | ------- |
    | `volcengine/doubao-seed-1-8-251228`          | Doubao Seed 1.8                 | teks, gambar | 256,000 |
    | `volcengine/doubao-seed-code-preview-251028` | doubao-seed-code-preview-251028 | teks, gambar | 256,000 |
    | `volcengine/kimi-k2-5-260127`                | Kimi K2.5                       | teks, gambar | 256,000 |
    | `volcengine/glm-4-7-251222`                  | GLM 4.7                         | teks, gambar | 200,000 |
    | `volcengine/deepseek-v3-2-251201`            | DeepSeek V3.2                   | teks, gambar | 128,000 |
  </Tab>
  <Tab title="Coding (volcengine-plan)">
    | Ref model                                         | Nama                     | Input | Konteks |
    | ------------------------------------------------- | ------------------------ | ----- | ------- |
    | `volcengine-plan/ark-code-latest`                 | Ark Coding Plan          | teks  | 256,000 |
    | `volcengine-plan/doubao-seed-code`                | Doubao Seed Code         | teks  | 256,000 |
    | `volcengine-plan/glm-4.7`                         | GLM 4.7 Coding           | teks  | 200,000 |
    | `volcengine-plan/kimi-k2-thinking`                | Kimi K2 Thinking         | teks  | 256,000 |
    | `volcengine-plan/kimi-k2.5`                       | Kimi K2.5 Coding         | teks  | 256,000 |
    | `volcengine-plan/doubao-seed-code-preview-251028` | Doubao Seed Code Preview | teks  | 256,000 |
  </Tab>
</Tabs>

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Model default setelah onboarding">
    `openclaw onboard --auth-choice volcengine-api-key` saat ini menetapkan
    `volcengine-plan/ark-code-latest` sebagai model default sambil juga mendaftarkan
    katalog `volcengine` umum.
  </Accordion>

  <Accordion title="Perilaku fallback pemilih model">
    Selama pemilihan model onboarding/configure, opsi autentikasi Volcengine memprioritaskan
    baris `volcengine/*` dan `volcengine-plan/*`. Jika model tersebut belum
    dimuat, OpenClaw akan kembali ke katalog tanpa filter alih-alih menampilkan
    pemilih yang scoped ke provider namun kosong.
  </Accordion>

  <Accordion title="Variabel lingkungan untuk proses daemon">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan
    `VOLCANO_ENGINE_API_KEY` tersedia untuk proses tersebut (misalnya, di
    `~/.openclaw/.env` atau melalui `env.shellEnv`).
  </Accordion>
</AccordionGroup>

<Warning>
Saat menjalankan OpenClaw sebagai layanan latar belakang, variabel lingkungan yang ditetapkan di shell
interaktif Anda tidak diwariskan secara otomatis. Lihat catatan daemon di atas.
</Warning>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi config lengkap untuk agent, model, dan provider.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Masalah umum dan langkah debugging.
  </Card>
  <Card title="FAQ" href="/id/help/faq" icon="circle-question">
    Pertanyaan yang sering diajukan tentang penyiapan OpenClaw.
  </Card>
</CardGroup>
