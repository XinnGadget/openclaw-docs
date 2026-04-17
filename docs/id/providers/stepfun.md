---
read_when:
    - Anda ingin model StepFun di OpenClaw
    - Anda memerlukan panduan setup StepFun
summary: Gunakan model StepFun dengan OpenClaw
title: StepFun
x-i18n:
    generated_at: "2026-04-12T23:32:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: a463bed0951d33802dcdb3a7784406272ee206b731e9864ea020323e67b4d159
    source_path: providers/stepfun.md
    workflow: 15
---

# StepFun

OpenClaw menyertakan Plugin provider StepFun bawaan dengan dua id provider:

- `stepfun` untuk endpoint standar
- `stepfun-plan` untuk endpoint Step Plan

<Warning>
Standard dan Step Plan adalah **provider yang terpisah** dengan endpoint dan prefiks model ref yang berbeda (`stepfun/...` vs `stepfun-plan/...`). Gunakan key China dengan endpoint `.com` dan key global dengan endpoint `.ai`.
</Warning>

## Ringkasan region dan endpoint

| Endpoint  | China (`.com`)                         | Global (`.ai`)                        |
| --------- | -------------------------------------- | ------------------------------------- |
| Standard  | `https://api.stepfun.com/v1`           | `https://api.stepfun.ai/v1`           |
| Step Plan | `https://api.stepfun.com/step_plan/v1` | `https://api.stepfun.ai/step_plan/v1` |

Auth env var: `STEPFUN_API_KEY`

## Katalog bawaan

Standard (`stepfun`):

| Model ref                | Konteks | Output maks | Catatan                |
| ------------------------ | ------- | ----------- | ---------------------- |
| `stepfun/step-3.5-flash` | 262,144 | 65,536      | Model standar default  |

Step Plan (`stepfun-plan`):

| Model ref                          | Konteks | Output maks | Catatan                     |
| ---------------------------------- | ------- | ----------- | --------------------------- |
| `stepfun-plan/step-3.5-flash`      | 262,144 | 65,536      | Model Step Plan default     |
| `stepfun-plan/step-3.5-flash-2603` | 262,144 | 65,536      | Model Step Plan tambahan    |

## Memulai

Pilih surface provider Anda dan ikuti langkah setup.

<Tabs>
  <Tab title="Standard">
    **Paling cocok untuk:** penggunaan umum melalui endpoint StepFun standar.

    <Steps>
      <Step title="Pilih region endpoint Anda">
        | Pilihan auth                    | Endpoint                        | Region        |
        | -------------------------------- | -------------------------------- | ------------- |
        | `stepfun-standard-api-key-intl`  | `https://api.stepfun.ai/v1`     | Internasional |
        | `stepfun-standard-api-key-cn`    | `https://api.stepfun.com/v1`    | China         |
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl
        ```

        Atau untuk endpoint China:

        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-cn
        ```
      </Step>
      <Step title="Alternatif non-interaktif">
        ```bash
        openclaw onboard --auth-choice stepfun-standard-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider stepfun
        ```
      </Step>
    </Steps>

    ### Model ref

    - Model default: `stepfun/step-3.5-flash`

  </Tab>

  <Tab title="Step Plan">
    **Paling cocok untuk:** endpoint penalaran Step Plan.

    <Steps>
      <Step title="Pilih region endpoint Anda">
        | Pilihan auth                  | Endpoint                               | Region        |
        | ----------------------------- | -------------------------------------- | ------------- |
        | `stepfun-plan-api-key-intl`   | `https://api.stepfun.ai/step_plan/v1`  | Internasional |
        | `stepfun-plan-api-key-cn`     | `https://api.stepfun.com/step_plan/v1` | China         |
      </Step>
      <Step title="Jalankan onboarding">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl
        ```

        Atau untuk endpoint China:

        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-cn
        ```
      </Step>
      <Step title="Alternatif non-interaktif">
        ```bash
        openclaw onboard --auth-choice stepfun-plan-api-key-intl \
          --stepfun-api-key "$STEPFUN_API_KEY"
        ```
      </Step>
      <Step title="Verifikasi bahwa model tersedia">
        ```bash
        openclaw models list --provider stepfun-plan
        ```
      </Step>
    </Steps>

    ### Model ref

    - Model default: `stepfun-plan/step-3.5-flash`
    - Model alternatif: `stepfun-plan/step-3.5-flash-2603`

  </Tab>
</Tabs>

## Lanjutan

<AccordionGroup>
  <Accordion title="Config lengkap: provider Standard">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          stepfun: {
            baseUrl: "https://api.stepfun.ai/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Config lengkap: provider Step Plan">
    ```json5
    {
      env: { STEPFUN_API_KEY: "your-key" },
      agents: { defaults: { model: { primary: "stepfun-plan/step-3.5-flash" } } },
      models: {
        mode: "merge",
        providers: {
          "stepfun-plan": {
            baseUrl: "https://api.stepfun.ai/step_plan/v1",
            api: "openai-completions",
            apiKey: "${STEPFUN_API_KEY}",
            models: [
              {
                id: "step-3.5-flash",
                name: "Step 3.5 Flash",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
              {
                id: "step-3.5-flash-2603",
                name: "Step 3.5 Flash 2603",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 65536,
              },
            ],
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="Catatan">
    - Provider ini dibundel dengan OpenClaw, jadi tidak ada langkah instalasi Plugin terpisah.
    - `step-3.5-flash-2603` saat ini hanya diekspos pada `stepfun-plan`.
    - Satu flow auth menulis profil yang cocok dengan region untuk `stepfun` dan `stepfun-plan`, sehingga kedua surface dapat ditemukan bersama.
    - Gunakan `openclaw models list` dan `openclaw models set <provider/model>` untuk memeriksa atau mengganti model.
  </Accordion>
</AccordionGroup>

<Note>
Untuk ikhtisar provider yang lebih luas, lihat [Provider model](/id/concepts/model-providers).
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Ikhtisar semua provider, model ref, dan perilaku failover.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Schema config lengkap untuk provider, model, dan Plugin.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/models" icon="brain">
    Cara memilih dan mengonfigurasi model.
  </Card>
  <Card title="Platform StepFun" href="https://platform.stepfun.com" icon="globe">
    Pengelolaan API key dan dokumentasi StepFun.
  </Card>
</CardGroup>
