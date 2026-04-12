---
read_when:
    - Anda menginginkan model Z.AI / GLM di OpenClaw
    - Anda memerlukan setup `ZAI_API_KEY` yang sederhana
summary: Gunakan Z.AI (model GLM) dengan OpenClaw
title: Z.AI
x-i18n:
    generated_at: "2026-04-12T23:33:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: 972b467dab141c8c5126ac776b7cb6b21815c27da511b3f34e12bd9e9ac953b7
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI adalah platform API untuk model **GLM**. Platform ini menyediakan REST API untuk GLM dan menggunakan kunci API
untuk auth. Buat kunci API Anda di konsol Z.AI. OpenClaw menggunakan provider `zai`
dengan kunci API Z.AI.

- Provider: `zai`
- Auth: `ZAI_API_KEY`
- API: Z.AI Chat Completions (auth Bearer)

## Memulai

<Tabs>
  <Tab title="Deteksi otomatis endpoint">
    **Paling cocok untuk:** sebagian besar pengguna. OpenClaw mendeteksi endpoint Z.AI yang cocok dari kunci dan otomatis menerapkan base URL yang benar.

    <Steps>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice zai-api-key
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Endpoint regional eksplisit">
    **Paling cocok untuk:** pengguna yang ingin memaksa permukaan API Coding Plan atau API umum tertentu.

    <Steps>
      <Step title="Pilih pilihan onboarding yang tepat">
        ```bash
        # Coding Plan Global (disarankan untuk pengguna Coding Plan)
        openclaw onboard --auth-choice zai-coding-global

        # Coding Plan CN (region Tiongkok)
        openclaw onboard --auth-choice zai-coding-cn

        # API umum
        openclaw onboard --auth-choice zai-global

        # API umum CN (region Tiongkok)
        openclaw onboard --auth-choice zai-cn
        ```
      </Step>
      <Step title="Tetapkan model default">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Katalog GLM bawaan

OpenClaw saat ini mengisi provider `zai` bawaan dengan:

| Model ref            | Catatan       |
| -------------------- | ------------- |
| `zai/glm-5.1`        | Model default |
| `zai/glm-5`          |               |
| `zai/glm-5-turbo`    |               |
| `zai/glm-5v-turbo`   |               |
| `zai/glm-4.7`        |               |
| `zai/glm-4.7-flash`  |               |
| `zai/glm-4.7-flashx` |               |
| `zai/glm-4.6`        |               |
| `zai/glm-4.6v`       |               |
| `zai/glm-4.5`        |               |
| `zai/glm-4.5-air`    |               |
| `zai/glm-4.5-flash`  |               |
| `zai/glm-4.5v`       |               |

<Tip>
Model GLM tersedia sebagai `zai/<model>` (contoh: `zai/glm-5`). Ref model bawaan default adalah `zai/glm-5.1`.
</Tip>

## Konfigurasi lanjutan

<AccordionGroup>
  <Accordion title="Forward-resolving model GLM-5 yang tidak dikenal">
    ID `glm-5*` yang tidak dikenal tetap di-forward-resolve pada jalur provider bawaan dengan
    mensintesis metadata milik provider dari template `glm-4.7` ketika ID tersebut
    cocok dengan bentuk keluarga GLM-5 saat ini.
  </Accordion>

  <Accordion title="Streaming pemanggilan tool">
    `tool_stream` diaktifkan secara default untuk streaming pemanggilan tool Z.AI. Untuk menonaktifkannya:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "zai/<model>": {
              params: { tool_stream: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Pemahaman gambar">
    Plugin Z.AI bawaan mendaftarkan pemahaman gambar.

    | Properti      | Nilai       |
    | ------------- | ----------- |
    | Model         | `glm-4.6v`  |

    Pemahaman gambar otomatis diselesaikan dari auth Z.AI yang dikonfigurasi — tidak
    diperlukan config tambahan.

  </Accordion>

  <Accordion title="Detail auth">
    - Z.AI menggunakan auth Bearer dengan kunci API Anda.
    - Pilihan onboarding `zai-api-key` mendeteksi otomatis endpoint Z.AI yang cocok dari prefiks kunci.
    - Gunakan pilihan regional eksplisit (`zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn`) ketika Anda ingin memaksa permukaan API tertentu.
  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Keluarga model GLM" href="/id/providers/glm" icon="microchip">
    Gambaran umum keluarga model untuk GLM.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
</CardGroup>
