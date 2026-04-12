---
read_when:
    - Anda ingin setup Moonshot K2 (Moonshot Open Platform) vs Kimi Coding
    - Anda perlu memahami endpoint, kunci, dan ref model yang terpisah
    - Anda menginginkan config siap salin-tempel untuk salah satu provider
summary: Konfigurasikan Moonshot K2 vs Kimi Coding (provider + kunci terpisah)
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-12T23:31:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f261f83a9b37e4fffb0cd0803e0c64f27eae8bae91b91d8a781a030663076f8
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI (Kimi)

Moonshot menyediakan API Kimi dengan endpoint yang kompatibel dengan OpenAI. Konfigurasikan
provider dan tetapkan model default ke `moonshot/kimi-k2.5`, atau gunakan
Kimi Coding dengan `kimi/kimi-code`.

<Warning>
Moonshot dan Kimi Coding adalah **provider yang terpisah**. Kunci tidak dapat dipertukarkan, endpoint berbeda, dan ref model juga berbeda (`moonshot/...` vs `kimi/...`).
</Warning>

## Katalog model bawaan

[//]: # "moonshot-kimi-k2-ids:start"

| Model ref                         | Nama                   | Reasoning | Input       | Konteks | Output maks |
| --------------------------------- | ---------------------- | --------- | ----------- | ------- | ----------- |
| `moonshot/kimi-k2.5`              | Kimi K2.5              | Tidak     | text, image | 262,144 | 262,144     |
| `moonshot/kimi-k2-thinking`       | Kimi K2 Thinking       | Ya        | text        | 262,144 | 262,144     |
| `moonshot/kimi-k2-thinking-turbo` | Kimi K2 Thinking Turbo | Ya        | text        | 262,144 | 262,144     |
| `moonshot/kimi-k2-turbo`          | Kimi K2 Turbo          | Tidak     | text        | 256,000 | 16,384      |

[//]: # "moonshot-kimi-k2-ids:end"

## Memulai

Pilih provider Anda dan ikuti langkah setup.

<Tabs>
  <Tab title="API Moonshot">
    **Paling cocok untuk:** model Kimi K2 melalui Moonshot Open Platform.

    <Steps>
      <Step title="Pilih region endpoint Anda">
        | Pilihan auth           | Endpoint                       | Region        |
        | ---------------------- | ------------------------------ | ------------- |
        | `moonshot-api-key`     | `https://api.moonshot.ai/v1`   | Internasional |
        | `moonshot-api-key-cn`  | `https://api.moonshot.cn/v1`   | Tiongkok      |
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice moonshot-api-key
        ```

        Atau untuk endpoint Tiongkok:

        ```bash
        openclaw onboard --auth-choice moonshot-api-key-cn
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "moonshot/kimi-k2.5" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider moonshot
        ```
      </Step>
    </Steps>

    ### Contoh config

    ```json5
    {
      env: { MOONSHOT_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "moonshot/kimi-k2.5" },
          models: {
            // moonshot-kimi-k2-aliases:start
            "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
            "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
            "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
            "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
            // moonshot-kimi-k2-aliases:end
          },
        },
      },
      models: {
        mode: "merge",
        providers: {
          moonshot: {
            baseUrl: "https://api.moonshot.ai/v1",
            apiKey: "${MOONSHOT_API_KEY}",
            api: "openai-completions",
            models: [
              // moonshot-kimi-k2-models:start
              {
                id: "kimi-k2.5",
                name: "Kimi K2.5",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking",
                name: "Kimi K2 Thinking",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking-turbo",
                name: "Kimi K2 Thinking Turbo",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-turbo",
                name: "Kimi K2 Turbo",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 16384,
              },
              // moonshot-kimi-k2-models:end
            ],
          },
        },
      },
    }
    ```

  </Tab>

  <Tab title="Kimi Coding">
    **Paling cocok untuk:** tugas yang berfokus pada kode melalui endpoint Kimi Coding.

    <Note>
    Kimi Coding menggunakan kunci API dan prefiks provider (`kimi/...`) yang berbeda dari Moonshot (`moonshot/...`). Ref model lama `kimi/k2p5` tetap diterima sebagai ID kompatibilitas.
    </Note>

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice kimi-code-api-key
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "kimi/kimi-code" },
            },
          },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider kimi
        ```
      </Step>
    </Steps>

    ### Contoh config

    ```json5
    {
      env: { KIMI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "kimi/kimi-code" },
          models: {
            "kimi/kimi-code": { alias: "Kimi" },
          },
        },
      },
    }
    ```

  </Tab>
</Tabs>

## Pencarian web Kimi

OpenClaw juga menyediakan **Kimi** sebagai provider `web_search`, yang didukung oleh pencarian web Moonshot.

<Steps>
  <Step title="Jalankan setup interaktif pencarian web">
    ```bash
    openclaw configure --section web
    ```

    Pilih **Kimi** di bagian web-search untuk menyimpan
    `plugins.entries.moonshot.config.webSearch.*`.

  </Step>
  <Step title="Konfigurasikan region dan model pencarian web">
    Setup interaktif akan meminta:

    | Pengaturan         | Opsi                                                                 |
    | ------------------ | -------------------------------------------------------------------- |
    | Region API         | `https://api.moonshot.ai/v1` (internasional) atau `https://api.moonshot.cn/v1` (Tiongkok) |
    | Model pencarian web | Default ke `kimi-k2.5`                                              |

  </Step>
</Steps>

Config berada di bawah `plugins.entries.moonshot.config.webSearch`:

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // atau gunakan KIMI_API_KEY / MOONSHOT_API_KEY
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## Lanjutan

<AccordionGroup>
  <Accordion title="Mode thinking native">
    Moonshot Kimi mendukung mode thinking native biner:

    - `thinking: { type: "enabled" }`
    - `thinking: { type: "disabled" }`

    Konfigurasikan per model melalui `agents.defaults.models.<provider/model>.params`:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "moonshot/kimi-k2.5": {
              params: {
                thinking: { type: "disabled" },
              },
            },
          },
        },
      },
    }
    ```

    OpenClaw juga memetakan level runtime `/think` untuk Moonshot:

    | Level `/think`      | Perilaku Moonshot         |
    | ------------------- | ------------------------- |
    | `/think off`        | `thinking.type=disabled`  |
    | Level apa pun selain off | `thinking.type=enabled` |

    <Warning>
    Saat thinking Moonshot diaktifkan, `tool_choice` harus `auto` atau `none`. OpenClaw menormalisasi nilai `tool_choice` yang tidak kompatibel menjadi `auto` demi kompatibilitas.
    </Warning>

  </Accordion>

  <Accordion title="Kompatibilitas penggunaan streaming">
    Endpoint Moonshot native (`https://api.moonshot.ai/v1` dan
    `https://api.moonshot.cn/v1`) mengiklankan kompatibilitas penggunaan streaming pada transport bersama `openai-completions`. OpenClaw menentukannya berdasarkan capability endpoint, sehingga ID provider kustom yang kompatibel yang menargetkan host Moonshot native yang sama mewarisi perilaku streaming-usage yang sama.
  </Accordion>

  <Accordion title="Referensi endpoint dan ref model">
    | Provider      | Prefiks ref model | Endpoint                     | Env var auth        |
    | ------------- | ----------------- | ---------------------------- | ------------------- |
    | Moonshot      | `moonshot/`       | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY`  |
    | Moonshot CN   | `moonshot/`       | `https://api.moonshot.cn/v1` | `MOONSHOT_API_KEY`  |
    | Kimi Coding   | `kimi/`           | endpoint Kimi Coding         | `KIMI_API_KEY`      |
    | Pencarian web | N/A               | Sama seperti region API Moonshot | `KIMI_API_KEY` atau `MOONSHOT_API_KEY` |

    - Pencarian web Kimi menggunakan `KIMI_API_KEY` atau `MOONSHOT_API_KEY`, dan default ke `https://api.moonshot.ai/v1` dengan model `kimi-k2.5`.
    - Override metadata pricing dan konteks di `models.providers` jika diperlukan.
    - Jika Moonshot menerbitkan batas konteks yang berbeda untuk suatu model, sesuaikan `contextWindow` sebagaimana mestinya.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Pencarian web" href="/tools/web-search" icon="magnifying-glass">
    Mengonfigurasi provider pencarian web termasuk Kimi.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Skema config lengkap untuk provider, model, dan Plugin.
  </Card>
  <Card title="Moonshot Open Platform" href="https://platform.moonshot.ai" icon="globe">
    Pengelolaan kunci API Moonshot dan dokumentasi.
  </Card>
</CardGroup>
