---
read_when:
    - Anda ingin menjalankan OpenClaw terhadap server vLLM lokal
    - Anda ingin endpoint `/v1` yang kompatibel dengan OpenAI dengan model Anda sendiri
summary: Jalankan OpenClaw dengan vLLM (server lokal yang kompatibel dengan OpenAI)
title: vLLM
x-i18n:
    generated_at: "2026-04-12T23:33:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: a43be9ae879158fcd69d50fb3a47616fd560e3c6fe4ecb3a109bdda6a63a6a80
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

vLLM dapat menyajikan model open-source (dan beberapa model kustom) melalui API HTTP **yang kompatibel dengan OpenAI**. OpenClaw terhubung ke vLLM menggunakan API `openai-completions`.

OpenClaw juga dapat **menemukan otomatis** model yang tersedia dari vLLM saat Anda melakukan opt-in dengan `VLLM_API_KEY` (nilai apa pun berfungsi jika server Anda tidak menerapkan auth) dan Anda tidak mendefinisikan entri `models.providers.vllm` secara eksplisit.

| Property         | Value                                    |
| ---------------- | ---------------------------------------- |
| ID Provider      | `vllm`                                   |
| API              | `openai-completions` (kompatibel dengan OpenAI) |
| Auth             | Variabel environment `VLLM_API_KEY`      |
| Base URL default | `http://127.0.0.1:8000/v1`               |

## Memulai

<Steps>
  <Step title="Mulai vLLM dengan server yang kompatibel dengan OpenAI">
    Base URL Anda harus mengekspos endpoint `/v1` (mis. `/v1/models`, `/v1/chat/completions`). vLLM umumnya berjalan di:

    ```
    http://127.0.0.1:8000/v1
    ```

  </Step>
  <Step title="Setel variabel environment API key">
    Nilai apa pun berfungsi jika server Anda tidak menerapkan auth:

    ```bash
    export VLLM_API_KEY="vllm-local"
    ```

  </Step>
  <Step title="Pilih model">
    Ganti dengan salah satu ID model vLLM Anda:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vllm/your-model-id" },
        },
      },
    }
    ```

  </Step>
  <Step title="Verifikasi model tersedia">
    ```bash
    openclaw models list --provider vllm
    ```
  </Step>
</Steps>

## Penemuan model (provider implisit)

Saat `VLLM_API_KEY` disetel (atau profil auth ada) dan Anda **tidak** mendefinisikan `models.providers.vllm`, OpenClaw mengueri:

```
GET http://127.0.0.1:8000/v1/models
```

dan mengubah ID yang dikembalikan menjadi entri model.

<Note>
Jika Anda menyetel `models.providers.vllm` secara eksplisit, penemuan otomatis dilewati dan Anda harus mendefinisikan model secara manual.
</Note>

## Konfigurasi eksplisit (model manual)

Gunakan konfigurasi eksplisit ketika:

- vLLM berjalan di host atau port yang berbeda
- Anda ingin mem-pin nilai `contextWindow` atau `maxTokens`
- Server Anda memerlukan API key sungguhan (atau Anda ingin mengontrol header)

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Model vLLM Lokal",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Perilaku bergaya proxy">
    vLLM diperlakukan sebagai backend `/v1` bergaya proxy yang kompatibel dengan OpenAI, bukan endpoint OpenAI native. Ini berarti:

    | Behavior | Applied? |
    |----------|----------|
    | Pembentukan permintaan OpenAI native | Tidak |
    | `service_tier` | Tidak dikirim |
    | Responses `store` | Tidak dikirim |
    | Petunjuk prompt-cache | Tidak dikirim |
    | Pembentukan payload kompatibilitas reasoning OpenAI | Tidak diterapkan |
    | Header atribusi OpenClaw tersembunyi | Tidak disuntikkan pada base URL kustom |

  </Accordion>

  <Accordion title="Base URL kustom">
    Jika server vLLM Anda berjalan di host atau port non-default, setel `baseUrl` dalam konfigurasi provider eksplisit:

    ```json5
    {
      models: {
        providers: {
          vllm: {
            baseUrl: "http://192.168.1.50:9000/v1",
            apiKey: "${VLLM_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "my-custom-model",
                name: "Model vLLM Remote",
                reasoning: false,
                input: ["text"],
                contextWindow: 64000,
                maxTokens: 4096,
              },
            ],
          },
        },
      },
    }
    ```

  </Accordion>
</AccordionGroup>

## Pemecahan masalah

<AccordionGroup>
  <Accordion title="Server tidak dapat dijangkau">
    Periksa bahwa server vLLM berjalan dan dapat diakses:

    ```bash
    curl http://127.0.0.1:8000/v1/models
    ```

    Jika Anda melihat error koneksi, verifikasi host, port, dan bahwa vLLM dimulai dengan mode server yang kompatibel dengan OpenAI.

  </Accordion>

  <Accordion title="Error auth pada permintaan">
    Jika permintaan gagal dengan error auth, setel `VLLM_API_KEY` sungguhan yang sesuai dengan konfigurasi server Anda, atau konfigurasikan provider secara eksplisit di bawah `models.providers.vllm`.

    <Tip>
    Jika server vLLM Anda tidak menerapkan auth, nilai apa pun yang tidak kosong untuk `VLLM_API_KEY` berfungsi sebagai sinyal opt-in untuk OpenClaw.
    </Tip>

  </Accordion>

  <Accordion title="Tidak ada model yang ditemukan">
    Penemuan otomatis memerlukan `VLLM_API_KEY` disetel **dan** tidak ada entri konfigurasi `models.providers.vllm` yang eksplisit. Jika Anda telah mendefinisikan provider secara manual, OpenClaw melewati penemuan dan hanya menggunakan model yang Anda deklarasikan.
  </Accordion>
</AccordionGroup>

<Warning>
Bantuan lebih lanjut: [Pemecahan masalah](/id/help/troubleshooting) dan [FAQ](/id/help/faq).
</Warning>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="OpenAI" href="/id/providers/openai" icon="bolt">
    Provider OpenAI native dan perilaku rute yang kompatibel dengan OpenAI.
  </Card>
  <Card title="OAuth dan auth" href="/id/gateway/authentication" icon="key">
    Detail auth dan aturan penggunaan ulang kredensial.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Masalah umum dan cara mengatasinya.
  </Card>
</CardGroup>
