---
read_when:
    - Anda menginginkan satu kunci API untuk banyak LLM
    - Anda memerlukan panduan penyiapan Baidu Qianfan
summary: Gunakan API terpadu Qianfan untuk mengakses banyak model di OpenClaw
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T23:32:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan adalah platform MaaS milik Baidu yang menyediakan **API terpadu** yang merutekan permintaan ke banyak model di balik satu
endpoint dan kunci API. API ini kompatibel dengan OpenAI, sehingga sebagian besar SDK OpenAI dapat digunakan hanya dengan mengganti base URL.

| Property | Value                             |
| -------- | --------------------------------- |
| Provider | `qianfan`                         |
| Autentikasi | `QIANFAN_API_KEY`              |
| API      | Kompatibel OpenAI                 |
| Base URL | `https://qianfan.baidubce.com/v2` |

## Memulai

<Steps>
  <Step title="Buat akun Baidu Cloud">
    Daftar atau masuk di [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey) dan pastikan akses API Qianfan sudah diaktifkan.
  </Step>
  <Step title="Buat kunci API">
    Buat aplikasi baru atau pilih yang sudah ada, lalu buat kunci API. Format key adalah `bce-v3/ALTAK-...`.
  </Step>
  <Step title="Jalankan onboarding">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="Verifikasi bahwa model tersedia">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## Model yang tersedia

| Ref model                            | Input       | Konteks | Output maks | Reasoning | Catatan       |
| ------------------------------------ | ----------- | ------- | ----------- | --------- | ------------- |
| `qianfan/deepseek-v3.2`              | teks        | 98,304  | 32,768      | Ya        | Model default |
| `qianfan/ernie-5.0-thinking-preview` | teks, gambar | 119,000 | 64,000     | Ya        | Multimodal    |

<Tip>
Ref model bawaan default adalah `qianfan/deepseek-v3.2`. Anda hanya perlu mengoverride `models.providers.qianfan` jika memerlukan base URL atau metadata model kustom.
</Tip>

## Contoh config

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Transport dan kompatibilitas">
    Qianfan berjalan melalui jalur transport yang kompatibel dengan OpenAI, bukan pembentukan permintaan OpenAI native. Ini berarti fitur SDK OpenAI standar tetap berfungsi, tetapi parameter khusus provider mungkin tidak diteruskan.
  </Accordion>

  <Accordion title="Katalog dan override">
    Katalog bawaan saat ini mencakup `deepseek-v3.2` dan `ernie-5.0-thinking-preview`. Tambahkan atau override `models.providers.qianfan` hanya jika Anda memerlukan base URL atau metadata model kustom.

    <Note>
    Ref model menggunakan prefiks `qianfan/` (misalnya `qianfan/deepseek-v3.2`).
    </Note>

  </Accordion>

  <Accordion title="Pemecahan masalah">
    - Pastikan kunci API Anda diawali dengan `bce-v3/ALTAK-` dan akses API Qianfan sudah diaktifkan di konsol Baidu Cloud.
    - Jika model tidak tercantum, pastikan akun Anda telah mengaktifkan layanan Qianfan.
    - Base URL default adalah `https://qianfan.baidubce.com/v2`. Ubah hanya jika Anda menggunakan endpoint atau proxy kustom.
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
  <Card title="Penyiapan agent" href="/id/concepts/agent" icon="robot">
    Mengonfigurasi default agent dan penetapan model.
  </Card>
  <Card title="Dokumentasi API Qianfan" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    Dokumentasi API Qianfan resmi.
  </Card>
</CardGroup>
