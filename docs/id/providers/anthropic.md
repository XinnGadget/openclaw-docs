---
read_when:
    - Anda ingin menggunakan model Anthropic di OpenClaw
summary: Gunakan Anthropic Claude melalui kunci API atau Claude CLI di OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-12T23:29:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5e3dda5f98ade9d4c3841888103bfb43d59e075d358a701ed0ae3ffb8d5694a7
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic membangun keluarga model **Claude**. OpenClaw mendukung dua jalur autentikasi:

- **Kunci API** — akses API Anthropic langsung dengan penagihan berbasis penggunaan (model `anthropic/*`)
- **Claude CLI** — gunakan kembali login Claude CLI yang sudah ada di host yang sama

<Warning>
Staf Anthropic memberi tahu kami bahwa penggunaan Claude CLI bergaya OpenClaw kembali diizinkan, jadi
OpenClaw memperlakukan penggunaan ulang Claude CLI dan penggunaan `claude -p` sebagai hal yang diizinkan kecuali
Anthropic menerbitkan kebijakan baru.

Untuk host gateway jangka panjang, kunci API Anthropic tetap menjadi jalur produksi yang paling jelas dan
paling dapat diprediksi.

Dokumentasi publik Anthropic saat ini:

- [Referensi Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Ikhtisar Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Menggunakan Claude Code dengan paket Pro atau Max Anda](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Menggunakan Claude Code dengan paket Team atau Enterprise Anda](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)
  </Warning>

## Memulai

<Tabs>
  <Tab title="Kunci API">
    **Paling cocok untuk:** akses API standar dan penagihan berbasis penggunaan.

    <Steps>
      <Step title="Dapatkan kunci API Anda">
        Buat kunci API di [Anthropic Console](https://console.anthropic.com/).
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard
        # pilih: Kunci API Anthropic
        ```

        Atau berikan kuncinya secara langsung:

        ```bash
        openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    ### Contoh config

    ```json5
    {
      env: { ANTHROPIC_API_KEY: "sk-ant-..." },
      agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
    }
    ```

  </Tab>

  <Tab title="Claude CLI">
    **Paling cocok untuk:** menggunakan kembali login Claude CLI yang sudah ada tanpa kunci API terpisah.

    <Steps>
      <Step title="Pastikan Claude CLI terinstal dan sudah login">
        Verifikasi dengan:

        ```bash
        claude --version
        ```
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard
        # pilih: Claude CLI
        ```

        OpenClaw mendeteksi dan menggunakan kembali kredensial Claude CLI yang sudah ada.
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    <Note>
    Detail penyiapan dan runtime untuk backend Claude CLI ada di [Backend CLI](/id/gateway/cli-backends).
    </Note>

    <Tip>
    Jika Anda menginginkan jalur penagihan yang paling jelas, gunakan kunci API Anthropic. OpenClaw juga mendukung opsi bergaya langganan dari [OpenAI Codex](/id/providers/openai), [Qwen Cloud](/id/providers/qwen), [MiniMax](/id/providers/minimax), dan [Z.AI / GLM](/id/providers/glm).
    </Tip>

  </Tab>
</Tabs>

## Default thinking (Claude 4.6)

Model Claude 4.6 secara default menggunakan thinking `adaptive` di OpenClaw saat tidak ada tingkat thinking eksplisit yang ditetapkan.

Override per pesan dengan `/think:<level>` atau di parameter model:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { thinking: "adaptive" },
        },
      },
    },
  },
}
```

<Note>
Dokumentasi Anthropic terkait:
- [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
</Note>

## Caching prompt

OpenClaw mendukung fitur caching prompt Anthropic untuk autentikasi kunci API.

| Value               | Durasi cache | Deskripsi                              |
| ------------------- | ------------ | -------------------------------------- |
| `"short"` (default) | 5 menit      | Diterapkan otomatis untuk autentikasi kunci API |
| `"long"`            | 1 jam        | Cache diperpanjang                     |
| `"none"`            | Tanpa cache  | Nonaktifkan caching prompt             |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Override cache per agent">
    Gunakan params tingkat model sebagai baseline, lalu override agent tertentu melalui `agents.list[].params`:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": {
              params: { cacheRetention: "long" },
            },
          },
        },
        list: [
          { id: "research", default: true },
          { id: "alerts", params: { cacheRetention: "none" } },
        ],
      },
    }
    ```

    Urutan penggabungan config:

    1. `agents.defaults.models["provider/model"].params`
    2. `agents.list[].params` (`id` yang cocok, override per key)

    Ini memungkinkan satu agent mempertahankan cache jangka panjang sementara agent lain pada model yang sama menonaktifkan caching untuk traffic yang bursty/berulang-rendah.

  </Accordion>

  <Accordion title="Catatan Claude Bedrock">
    - Model Anthropic Claude di Bedrock (`amazon-bedrock/*anthropic.claude*`) menerima pass-through `cacheRetention` saat dikonfigurasi.
    - Model Bedrock non-Anthropic dipaksa ke `cacheRetention: "none"` saat runtime.
    - Smart default kunci API juga mengisi `cacheRetention: "short"` untuk ref Claude-on-Bedrock saat tidak ada nilai eksplisit yang ditetapkan.
  </Accordion>
</AccordionGroup>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Mode cepat">
    Toggle `/fast` bersama milik OpenClaw mendukung traffic Anthropic langsung (kunci API dan OAuth ke `api.anthropic.com`).

    | Command | Dipetakan ke |
    |---------|--------------|
    | `/fast on` | `service_tier: "auto"` |
    | `/fast off` | `service_tier: "standard_only"` |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-sonnet-4-6": {
              params: { fastMode: true },
            },
          },
        },
      },
    }
    ```

    <Note>
    - Hanya disuntikkan untuk permintaan langsung `api.anthropic.com`. Rute proxy membiarkan `service_tier` tidak berubah.
    - Param `serviceTier` atau `service_tier` yang eksplisit mengoverride `/fast` saat keduanya ditetapkan.
    - Pada akun tanpa kapasitas Priority Tier, `service_tier: "auto"` dapat diselesaikan menjadi `standard`.
    </Note>

  </Accordion>

  <Accordion title="Pemahaman media (gambar dan PDF)">
    Plugin Anthropic bawaan mendaftarkan pemahaman gambar dan PDF. OpenClaw
    secara otomatis me-resolve kapabilitas media dari autentikasi Anthropic yang dikonfigurasi — tidak
    diperlukan config tambahan.

    | Property       | Value                |
    | -------------- | -------------------- |
    | Model default  | `claude-opus-4-6`    |
    | Input yang didukung | Gambar, dokumen PDF |

    Saat gambar atau PDF dilampirkan ke percakapan, OpenClaw secara otomatis
    merutekannya melalui provider pemahaman media Anthropic.

  </Accordion>

  <Accordion title="Jendela konteks 1M (beta)">
    Jendela konteks 1M Anthropic dibatasi beta. Aktifkan per model:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": {
              params: { context1m: true },
            },
          },
        },
      },
    }
    ```

    OpenClaw memetakan ini ke `anthropic-beta: context-1m-2025-08-07` pada permintaan.

    <Warning>
    Memerlukan akses konteks panjang pada kredensial Anthropic Anda. Autentikasi token lama (`sk-ant-oat-*`) ditolak untuk permintaan konteks 1M — OpenClaw mencatat peringatan dan kembali ke jendela konteks standar.
    </Warning>

  </Accordion>
</AccordionGroup>

## Pemecahan masalah

<AccordionGroup>
  <Accordion title="Error 401 / token tiba-tiba tidak valid">
    Autentikasi token Anthropic dapat kedaluwarsa atau dicabut. Untuk penyiapan baru, migrasikan ke kunci API Anthropic.
  </Accordion>

  <Accordion title='Tidak ada kunci API yang ditemukan untuk provider "anthropic"'>
    Autentikasi bersifat **per agent**. Agent baru tidak mewarisi kunci agent utama. Jalankan ulang onboarding untuk agent tersebut, atau konfigurasikan kunci API di host gateway, lalu verifikasi dengan `openclaw models status`.
  </Accordion>

  <Accordion title='Tidak ditemukan kredensial untuk profil "anthropic:default"'>
    Jalankan `openclaw models status` untuk melihat profil autentikasi mana yang aktif. Jalankan ulang onboarding, atau konfigurasikan kunci API untuk path profil tersebut.
  </Accordion>

  <Accordion title="Tidak ada profil autentikasi yang tersedia (semua dalam cooldown)">
    Periksa `openclaw models status --json` untuk `auth.unusableProfiles`. Cooldown rate limit Anthropic dapat bersifat model-scoped, jadi model Anthropic saudara mungkin masih dapat digunakan. Tambahkan profil Anthropic lain atau tunggu cooldown selesai.
  </Accordion>
</AccordionGroup>

<Note>
Bantuan lebih lanjut: [Pemecahan masalah](/id/help/troubleshooting) dan [FAQ](/id/help/faq).
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Backend CLI" href="/id/gateway/cli-backends" icon="terminal">
    Penyiapan backend Claude CLI dan detail runtime.
  </Card>
  <Card title="Caching prompt" href="/id/reference/prompt-caching" icon="database">
    Cara kerja caching prompt di berbagai provider.
  </Card>
  <Card title="OAuth dan autentikasi" href="/id/gateway/authentication" icon="key">
    Detail autentikasi dan aturan penggunaan ulang kredensial.
  </Card>
</CardGroup>
