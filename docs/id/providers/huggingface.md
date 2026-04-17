---
read_when:
    - Anda ingin menggunakan Hugging Face Inference dengan OpenClaw
    - Anda memerlukan env var token HF atau pilihan auth CLI
summary: Setup Hugging Face Inference (auth + pemilihan model)
title: Hugging Face (Inference)
x-i18n:
    generated_at: "2026-04-12T23:31:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face (Inference)

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) menawarkan chat completion yang kompatibel dengan OpenAI melalui satu API router. Anda mendapatkan akses ke banyak model (DeepSeek, Llama, dan lainnya) dengan satu token. OpenClaw menggunakan **endpoint yang kompatibel dengan OpenAI** (hanya chat completion); untuk text-to-image, embeddings, atau speech gunakan [klien inference HF](https://huggingface.co/docs/api-inference/quicktour) secara langsung.

- Provider: `huggingface`
- Auth: `HUGGINGFACE_HUB_TOKEN` atau `HF_TOKEN` (token fine-grained dengan izin **Make calls to Inference Providers**)
- API: kompatibel dengan OpenAI (`https://router.huggingface.co/v1`)
- Billing: Satu token HF; [pricing](https://huggingface.co/docs/inference-providers/pricing) mengikuti tarif provider dengan tier gratis.

## Memulai

<Steps>
  <Step title="Buat token fine-grained">
    Buka [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained) dan buat token fine-grained baru.

    <Warning>
    Token tersebut harus mengaktifkan izin **Make calls to Inference Providers** atau permintaan API akan ditolak.
    </Warning>

  </Step>
  <Step title="Jalankan onboarding">
    Pilih **Hugging Face** di dropdown provider, lalu masukkan kunci API Anda saat diminta:

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="Pilih model default">
    Di dropdown **Default Hugging Face model**, pilih model yang Anda inginkan. Daftar ini dimuat dari Inference API saat Anda memiliki token yang valid; jika tidak, daftar bawaan akan ditampilkan. Pilihan Anda disimpan sebagai model default.

    Anda juga dapat menetapkan atau mengubah model default nanti di config:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### Setup non-interaktif

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

Ini akan menetapkan `huggingface/deepseek-ai/DeepSeek-R1` sebagai model default.

## ID model

Ref model menggunakan format `huggingface/<org>/<model>` (ID bergaya Hub). Daftar di bawah ini berasal dari **GET** `https://router.huggingface.co/v1/models`; katalog Anda mungkin mencakup lebih banyak.

| Model                  | Ref (awali dengan `huggingface/`)   |
| ---------------------- | ----------------------------------- |
| DeepSeek R1            | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2          | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B               | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct    | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B              | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct  | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B           | `openai/gpt-oss-120b`               |
| GLM 4.7                | `zai-org/GLM-4.7`                   |
| Kimi K2.5              | `moonshotai/Kimi-K2.5`              |

<Tip>
Anda dapat menambahkan `:fastest` atau `:cheapest` ke ID model mana pun. Tetapkan urutan default Anda di [Inference Provider settings](https://hf.co/settings/inference-providers); lihat [Inference Providers](https://huggingface.co/docs/inference-providers) dan **GET** `https://router.huggingface.co/v1/models` untuk daftar lengkap.
</Tip>

## Detail lanjutan

<AccordionGroup>
  <Accordion title="Discovery model dan dropdown onboarding">
    OpenClaw menemukan model dengan memanggil **endpoint Inference secara langsung**:

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    (Opsional: kirim `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` atau `$HF_TOKEN` untuk daftar lengkap; beberapa endpoint mengembalikan subset tanpa auth.) Responsnya bergaya OpenAI `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`.

    Saat Anda mengonfigurasi kunci API Hugging Face (melalui onboarding, `HUGGINGFACE_HUB_TOKEN`, atau `HF_TOKEN`), OpenClaw menggunakan GET ini untuk menemukan model chat-completion yang tersedia. Selama **setup interaktif**, setelah Anda memasukkan token, Anda akan melihat dropdown **Default Hugging Face model** yang diisi dari daftar tersebut (atau katalog bawaan jika permintaan gagal). Saat runtime (misalnya startup Gateway), ketika kunci tersedia, OpenClaw kembali memanggil **GET** `https://router.huggingface.co/v1/models` untuk menyegarkan katalog. Daftar tersebut digabungkan dengan katalog bawaan (untuk metadata seperti context window dan biaya). Jika permintaan gagal atau tidak ada kunci yang ditetapkan, hanya katalog bawaan yang digunakan.

  </Accordion>

  <Accordion title="Nama model, alias, dan sufiks kebijakan">
    - **Nama dari API:** Nama tampilan model **diisi dari GET /v1/models** saat API mengembalikan `name`, `title`, atau `display_name`; jika tidak, nama tersebut diturunkan dari ID model (misalnya `deepseek-ai/DeepSeek-R1` menjadi "DeepSeek R1").
    - **Override nama tampilan:** Anda dapat menetapkan label kustom per model di config agar tampil sesuai yang Anda inginkan di CLI dan UI:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (cepat)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (murah)" },
          },
        },
      },
    }
    ```

    - **Sufiks kebijakan:** Dokumen dan helper Hugging Face bawaan OpenClaw saat ini memperlakukan dua sufiks ini sebagai varian kebijakan bawaan:
      - **`:fastest`** — throughput tertinggi.
      - **`:cheapest`** — biaya terendah per token output.

      Anda dapat menambahkannya sebagai entri terpisah di `models.providers.huggingface.models` atau menetapkan `model.primary` dengan sufiks tersebut. Anda juga dapat menetapkan urutan provider default Anda di [Inference Provider settings](https://hf.co/settings/inference-providers) (tanpa sufiks = gunakan urutan tersebut).

    - **Penggabungan config:** Entri yang sudah ada di `models.providers.huggingface.models` (misalnya di `models.json`) tetap dipertahankan saat config digabungkan. Jadi setiap `name`, `alias`, atau opsi model kustom yang Anda tetapkan di sana akan dipertahankan.

  </Accordion>

  <Accordion title="Environment dan setup daemon">
    Jika Gateway berjalan sebagai daemon (launchd/systemd), pastikan `HUGGINGFACE_HUB_TOKEN` atau `HF_TOKEN` tersedia untuk proses tersebut (misalnya, di `~/.openclaw/.env` atau melalui `env.shellEnv`).

    <Note>
    OpenClaw menerima `HUGGINGFACE_HUB_TOKEN` dan `HF_TOKEN` sebagai alias env var. Keduanya dapat digunakan; jika keduanya ditetapkan, `HUGGINGFACE_HUB_TOKEN` diprioritaskan.
    </Note>

  </Accordion>

  <Accordion title="Config: DeepSeek R1 dengan fallback Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: Qwen dengan varian cheapest dan fastest">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (termurah)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (tercepat)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: DeepSeek + Llama + GPT-OSS dengan alias">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config: Beberapa Qwen dan DeepSeek dengan sufiks kebijakan">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (murah)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (cepat)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Gambaran umum semua provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/models" icon="brain">
    Cara memilih dan mengonfigurasi model.
  </Card>
  <Card title="Dokumen Inference Providers" href="https://huggingface.co/docs/inference-providers" icon="book">
    Dokumentasi resmi Hugging Face Inference Providers.
  </Card>
  <Card title="Konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi config lengkap.
  </Card>
</CardGroup>
