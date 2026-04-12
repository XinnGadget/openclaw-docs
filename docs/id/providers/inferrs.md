---
read_when:
    - Anda ingin menjalankan OpenClaw terhadap server inferrs lokal
    - Anda menyajikan Gemma atau model lain melalui inferrs
    - Anda memerlukan flag kompatibilitas OpenClaw yang tepat untuk inferrs
summary: Jalankan OpenClaw melalui inferrs (server lokal yang kompatibel dengan OpenAI)
title: inferrs
x-i18n:
    generated_at: "2026-04-12T23:31:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) dapat menyajikan model lokal di balik
API `/v1` yang kompatibel dengan OpenAI. OpenClaw bekerja dengan `inferrs` melalui jalur
`openai-completions` generik.

Saat ini, `inferrs` paling baik diperlakukan sebagai backend kustom yang di-host sendiri dan kompatibel dengan OpenAI,
bukan sebagai Plugin provider OpenClaw khusus.

## Memulai

<Steps>
  <Step title="Jalankan inferrs dengan model">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="Verifikasi bahwa server dapat dijangkau">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="Tambahkan entri provider OpenClaw">
    Tambahkan entri provider eksplisit dan arahkan model default Anda ke sana. Lihat contoh config lengkap di bawah.
  </Step>
</Steps>

## Contoh config lengkap

Contoh ini menggunakan Gemma 4 pada server `inferrs` lokal.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## Lanjutan

<AccordionGroup>
  <Accordion title="Mengapa requiresStringContent penting">
    Beberapa rute Chat Completions `inferrs` hanya menerima
    `messages[].content` berbentuk string, bukan array content-part terstruktur.

    <Warning>
    Jika eksekusi OpenClaw gagal dengan error seperti:

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    tetapkan `compat.requiresStringContent: true` di entri model Anda.
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw akan meratakan pure text content parts menjadi string biasa sebelum mengirim
    permintaan.

  </Accordion>

  <Accordion title="Gemma dan catatan tool-schema">
    Beberapa kombinasi `inferrs` + Gemma saat ini menerima permintaan
    `/v1/chat/completions` langsung yang kecil tetapi tetap gagal pada giliran runtime agent OpenClaw penuh.

    Jika itu terjadi, coba ini terlebih dahulu:

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    Itu menonaktifkan permukaan tool schema OpenClaw untuk model tersebut dan dapat mengurangi tekanan prompt
    pada backend lokal yang lebih ketat.

    Jika permintaan langsung kecil masih berfungsi tetapi giliran agent OpenClaw normal tetap
    crash di dalam `inferrs`, masalah yang tersisa biasanya merupakan perilaku model/server hulu
    daripada lapisan transport OpenClaw.

  </Accordion>

  <Accordion title="Smoke test manual">
    Setelah dikonfigurasi, uji kedua lapisan:

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    Jika perintah pertama berfungsi tetapi yang kedua gagal, periksa bagian pemecahan masalah di bawah.

  </Accordion>

  <Accordion title="Perilaku gaya proxy">
    `inferrs` diperlakukan sebagai backend `/v1` yang kompatibel dengan OpenAI bergaya proxy, bukan
    endpoint OpenAI native.

    - Pembentukan permintaan native khusus OpenAI tidak berlaku di sini
    - Tidak ada `service_tier`, tidak ada Responses `store`, tidak ada petunjuk prompt-cache, dan tidak ada
      pembentukan payload kompatibilitas reasoning OpenAI
    - Header atribusi OpenClaw tersembunyi (`originator`, `version`, `User-Agent`)
      tidak disuntikkan pada `baseUrl` `inferrs` kustom

  </Accordion>
</AccordionGroup>

## Pemecahan masalah

<AccordionGroup>
  <Accordion title="curl /v1/models gagal">
    `inferrs` tidak berjalan, tidak dapat dijangkau, atau tidak terikat ke
    host/port yang diharapkan. Pastikan server sudah dimulai dan mendengarkan di alamat yang
    Anda konfigurasi.
  </Accordion>

  <Accordion title="messages[].content mengharapkan string">
    Tetapkan `compat.requiresStringContent: true` di entri model. Lihat bagian
    `requiresStringContent` di atas untuk detail.
  </Accordion>

  <Accordion title="Panggilan langsung /v1/chat/completions berhasil tetapi openclaw infer model run gagal">
    Coba tetapkan `compat.supportsTools: false` untuk menonaktifkan permukaan tool schema.
    Lihat catatan tool-schema Gemma di atas.
  </Accordion>

  <Accordion title="inferrs tetap crash pada giliran agent yang lebih besar">
    Jika OpenClaw tidak lagi mendapat error schema tetapi `inferrs` masih crash pada giliran
    agent yang lebih besar, anggap ini sebagai keterbatasan `inferrs` atau model di hulu. Kurangi
    tekanan prompt atau beralih ke backend atau model lokal yang berbeda.
  </Accordion>
</AccordionGroup>

<Tip>
Untuk bantuan umum, lihat [Pemecahan masalah](/id/help/troubleshooting) dan [FAQ](/id/help/faq).
</Tip>

## Lihat juga

<CardGroup cols={2}>
  <Card title="Model lokal" href="/id/gateway/local-models" icon="server">
    Menjalankan OpenClaw terhadap server model lokal.
  </Card>
  <Card title="Pemecahan masalah Gateway" href="/id/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    Debugging backend lokal yang kompatibel dengan OpenAI yang lolos probe langsung tetapi gagal pada eksekusi agent.
  </Card>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Ikhtisar semua provider, ref model, dan perilaku failover.
  </Card>
</CardGroup>
