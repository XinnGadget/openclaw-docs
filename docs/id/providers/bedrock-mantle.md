---
read_when:
    - Anda ingin menggunakan model OSS yang dihosting Bedrock Mantle dengan OpenClaw
    - Anda memerlukan endpoint kompatibel OpenAI Mantle untuk GPT-OSS, Qwen, Kimi, atau GLM
summary: Gunakan model Amazon Bedrock Mantle (kompatibel OpenAI) dengan OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-12T23:29:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27e602b6f6a3ae92427de135cb9df6356e0daaea6b6fe54723a7542dd0d5d21e
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw menyertakan provider **Amazon Bedrock Mantle** bawaan yang terhubung ke
endpoint Mantle yang kompatibel dengan OpenAI. Mantle menghosting model open-source dan
pihak ketiga (GPT-OSS, Qwen, Kimi, GLM, dan sejenisnya) melalui permukaan standar
`/v1/chat/completions` yang didukung oleh infrastruktur Bedrock.

| Property       | Value                                                                               |
| -------------- | ----------------------------------------------------------------------------------- |
| ID Provider    | `amazon-bedrock-mantle`                                                             |
| API            | `openai-completions` (kompatibel OpenAI)                                            |
| Autentikasi    | `AWS_BEARER_TOKEN_BEDROCK` eksplisit atau pembuatan bearer token rantai kredensial IAM |
| Region default | `us-east-1` (override dengan `AWS_REGION` atau `AWS_DEFAULT_REGION`)                |

## Memulai

Pilih metode autentikasi yang Anda inginkan dan ikuti langkah penyiapannya.

<Tabs>
  <Tab title="Bearer token eksplisit">
    **Paling cocok untuk:** lingkungan tempat Anda sudah memiliki bearer token Mantle.

    <Steps>
      <Step title="Tetapkan bearer token di host gateway">
        ```bash
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```

        Secara opsional tetapkan region (default-nya `us-east-1`):

        ```bash
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verifikasi model ditemukan">
        ```bash
        openclaw models list
        ```

        Model yang ditemukan akan muncul di bawah provider `amazon-bedrock-mantle`. Tidak
        diperlukan config tambahan kecuali Anda ingin mengoverride default.
      </Step>
    </Steps>

  </Tab>

  <Tab title="Kredensial IAM">
    **Paling cocok untuk:** menggunakan kredensial yang kompatibel dengan AWS SDK (shared config, SSO, web identity, instance role, atau task role).

    <Steps>
      <Step title="Konfigurasikan kredensial AWS di host gateway">
        Sumber autentikasi apa pun yang kompatibel dengan AWS SDK dapat digunakan:

        ```bash
        export AWS_PROFILE="default"
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verifikasi model ditemukan">
        ```bash
        openclaw models list
        ```

        OpenClaw menghasilkan bearer token Mantle dari rantai kredensial secara otomatis.
      </Step>
    </Steps>

    <Tip>
    Saat `AWS_BEARER_TOKEN_BEDROCK` tidak diatur, OpenClaw membuat bearer token untuk Anda dari rantai kredensial default AWS, termasuk shared credentials/config profile, SSO, web identity, serta instance role atau task role.
    </Tip>

  </Tab>
</Tabs>

## Penemuan model otomatis

Saat `AWS_BEARER_TOKEN_BEDROCK` diatur, OpenClaw menggunakannya secara langsung. Jika tidak,
OpenClaw mencoba menghasilkan bearer token Mantle dari rantai kredensial default AWS.
Setelah itu, OpenClaw menemukan model Mantle yang tersedia dengan melakukan query ke
endpoint `/v1/models` milik region tersebut.

| Perilaku            | Detail                    |
| ------------------- | ------------------------- |
| Cache penemuan      | Hasil di-cache selama 1 jam |
| Refresh token IAM   | Per jam                   |

<Note>
Bearer token ini sama dengan `AWS_BEARER_TOKEN_BEDROCK` yang digunakan oleh provider [Amazon Bedrock](/id/providers/bedrock) standar.
</Note>

### Region yang didukung

`us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## Konfigurasi manual

Jika Anda lebih memilih config eksplisit daripada penemuan otomatis:

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Dukungan reasoning">
    Dukungan reasoning disimpulkan dari ID model yang mengandung pola seperti
    `thinking`, `reasoner`, atau `gpt-oss-120b`. OpenClaw menetapkan `reasoning: true`
    secara otomatis untuk model yang cocok selama penemuan.
  </Accordion>

  <Accordion title="Endpoint tidak tersedia">
    Jika endpoint Mantle tidak tersedia atau tidak mengembalikan model, provider ini
    akan dilewati secara senyap. OpenClaw tidak menghasilkan error; provider lain yang dikonfigurasi
    tetap berfungsi normal.
  </Accordion>

  <Accordion title="Hubungan dengan provider Amazon Bedrock">
    Bedrock Mantle adalah provider terpisah dari provider
    [Amazon Bedrock](/id/providers/bedrock) standar. Mantle menggunakan permukaan
    `/v1` yang kompatibel dengan OpenAI, sedangkan provider Bedrock standar menggunakan
    API Bedrock native.

    Kedua provider berbagi kredensial `AWS_BEARER_TOKEN_BEDROCK` yang sama jika
    tersedia.

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" href="/id/providers/bedrock" icon="cloud">
    Provider Bedrock native untuk Anthropic Claude, Titan, dan model lainnya.
  </Card>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="OAuth dan autentikasi" href="/id/gateway/authentication" icon="key">
    Detail autentikasi dan aturan penggunaan ulang kredensial.
  </Card>
  <Card title="Pemecahan masalah" href="/id/help/troubleshooting" icon="wrench">
    Masalah umum dan cara menyelesaikannya.
  </Card>
</CardGroup>
