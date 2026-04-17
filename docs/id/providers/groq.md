---
read_when:
    - Anda ingin menggunakan Groq dengan OpenClaw
    - Anda memerlukan env var kunci API atau opsi autentikasi CLI
summary: Penyiapan Groq (autentikasi + pemilihan model)
title: Groq
x-i18n:
    generated_at: "2026-04-12T23:30:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 613289efc36fedd002e1ebf9366e0e7119ea1f9e14a1dae773b90ea57100baee
    source_path: providers/groq.md
    workflow: 15
---

# Groq

[Groq](https://groq.com) menyediakan inferensi super cepat pada model open-source
(Llama, Gemma, Mistral, dan lainnya) menggunakan hardware LPU kustom. OpenClaw terhubung
ke Groq melalui API-nya yang kompatibel dengan OpenAI.

| Property | Value             |
| -------- | ----------------- |
| Provider | `groq`            |
| Autentikasi | `GROQ_API_KEY` |
| API      | Kompatibel OpenAI |

## Memulai

<Steps>
  <Step title="Dapatkan kunci API">
    Buat kunci API di [console.groq.com/keys](https://console.groq.com/keys).
  </Step>
  <Step title="Tetapkan kunci API">
    ```bash
    export GROQ_API_KEY="gsk_..."
    ```
  </Step>
  <Step title="Tetapkan model default">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "groq/llama-3.3-70b-versatile" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Contoh file config

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## Model yang tersedia

Katalog model Groq sering berubah. Jalankan `openclaw models list | grep groq`
untuk melihat model yang saat ini tersedia, atau periksa
[console.groq.com/docs/models](https://console.groq.com/docs/models).

| Model                       | Catatan                            |
| --------------------------- | ---------------------------------- |
| **Llama 3.3 70B Versatile** | Tujuan umum, konteks besar         |
| **Llama 3.1 8B Instant**    | Cepat, ringan                      |
| **Gemma 2 9B**              | Ringkas, efisien                   |
| **Mixtral 8x7B**            | Arsitektur MoE, reasoning kuat     |

<Tip>
Gunakan `openclaw models list --provider groq` untuk daftar model yang paling mutakhir
yang tersedia di akun Anda.
</Tip>

## Transkripsi audio

Groq juga menyediakan transkripsi audio cepat berbasis Whisper. Saat dikonfigurasi sebagai
provider pemahaman media, OpenClaw menggunakan model `whisper-large-v3-turbo` milik Groq
untuk mentranskripsikan pesan suara melalui permukaan bersama `tools.media.audio`.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Detail transkripsi audio">
    | Property | Value |
    |----------|-------|
    | Path config bersama | `tools.media.audio` |
    | Base URL default    | `https://api.groq.com/openai/v1` |
    | Model default       | `whisper-large-v3-turbo` |
    | Endpoint API        | `/audio/transcriptions` kompatibel OpenAI |
  </Accordion>

  <Accordion title="Catatan lingkungan">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `GROQ_API_KEY`
    tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui
    `env.shellEnv`).

    <Warning>
    Key yang hanya ditetapkan di shell interaktif Anda tidak terlihat oleh proses
    gateway yang dikelola daemon. Gunakan `~/.openclaw/.env` atau config `env.shellEnv`
    untuk ketersediaan yang persisten.
    </Warning>

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Skema config lengkap termasuk pengaturan provider dan audio.
  </Card>
  <Card title="Groq Console" href="https://console.groq.com" icon="arrow-up-right-from-square">
    Dashboard Groq, dokumentasi API, dan harga.
  </Card>
  <Card title="Daftar model Groq" href="https://console.groq.com/docs/models" icon="list">
    Katalog model Groq resmi.
  </Card>
</CardGroup>
