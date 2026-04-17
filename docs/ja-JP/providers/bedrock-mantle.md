---
read_when:
    - OpenClaw で Bedrock Mantle がホストする OSS モデルを使用したい場合
    - GPT-OSS、Qwen、Kimi、または GLM 向けの Mantle OpenAI 互換エンドポイントが必要な場合
summary: OpenClaw で Amazon Bedrock Mantle（OpenAI 互換）モデルを使用する
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-12T23:30:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27e602b6f6a3ae92427de135cb9df6356e0daaea6b6fe54723a7542dd0d5d21e
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw には、Mantle の OpenAI 互換エンドポイントに接続する、バンドルされた **Amazon Bedrock Mantle** provider が含まれています。Mantle は、Bedrock インフラを基盤とする標準的な `/v1/chat/completions` サーフェスを通じて、オープンソースおよびサードパーティのモデル（GPT-OSS、Qwen、Kimi、GLM など）をホストします。

| Property       | Value                                                                               |
| -------------- | ----------------------------------------------------------------------------------- |
| Provider ID    | `amazon-bedrock-mantle`                                                             |
| API            | `openai-completions`（OpenAI 互換）                                                 |
| Auth           | 明示的な `AWS_BEARER_TOKEN_BEDROCK` または IAM credential-chain による bearer token 生成 |
| Default region | `us-east-1`（`AWS_REGION` または `AWS_DEFAULT_REGION` で上書き可能）                |

## はじめに

希望する認証方法を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="Explicit bearer token">
    **最適な用途:** すでに Mantle bearer token を持っている環境。

    <Steps>
      <Step title="Set the bearer token on the gateway host">
        ```bash
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```

        必要に応じてリージョンを設定します（デフォルトは `us-east-1`）:

        ```bash
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verify models are discovered">
        ```bash
        openclaw models list
        ```

        検出されたモデルは `amazon-bedrock-mantle` provider 配下に表示されます。デフォルトを上書きしたい場合を除き、追加の設定は不要です。
      </Step>
    </Steps>

  </Tab>

  <Tab title="IAM credentials">
    **最適な用途:** AWS SDK 互換資格情報（共有設定、SSO、web identity、instance または task role）を使用する場合。

    <Steps>
      <Step title="Configure AWS credentials on the gateway host">
        AWS SDK 互換の認証ソースであればどれでも使えます:

        ```bash
        export AWS_PROFILE="default"
        export AWS_REGION="us-west-2"
        ```
      </Step>
      <Step title="Verify models are discovered">
        ```bash
        openclaw models list
        ```

        OpenClaw は、credential chain から Mantle bearer token を自動生成します。
      </Step>
    </Steps>

    <Tip>
    `AWS_BEARER_TOKEN_BEDROCK` が設定されていない場合、OpenClaw は共有 credentials/config profile、SSO、web identity、instance または task role を含む AWS デフォルト credential chain から bearer token を自動発行します。
    </Tip>

  </Tab>
</Tabs>

## 自動モデル検出

`AWS_BEARER_TOKEN_BEDROCK` が設定されている場合、OpenClaw はそれを直接使用します。そうでない場合、OpenClaw は AWS デフォルト credential chain から Mantle bearer token の生成を試みます。その後、リージョンの `/v1/models` エンドポイントに問い合わせて、利用可能な Mantle モデルを検出します。

| Behavior          | Detail                    |
| ----------------- | ------------------------- |
| Discovery cache   | 結果は 1 時間キャッシュされます |
| IAM token refresh | 毎時                      |

<Note>
この bearer token は、標準の [Amazon Bedrock](/ja-JP/providers/bedrock) provider でも使用される同じ `AWS_BEARER_TOKEN_BEDROCK` です。
</Note>

### サポートされるリージョン

`us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## 手動設定

自動検出ではなく明示的な設定を使いたい場合:

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

## 補足事項

<AccordionGroup>
  <Accordion title="Reasoning support">
    Reasoning サポートは、`thinking`、`reasoner`、`gpt-oss-120b` のようなパターンを含む model ID から推測されます。OpenClaw は、検出時に一致するモデルに対して自動的に `reasoning: true` を設定します。
  </Accordion>

  <Accordion title="Endpoint unavailability">
    Mantle エンドポイントが利用できない、またはモデルを返さない場合、この provider は静かにスキップされます。OpenClaw はエラーにはせず、他の設定済み provider は通常どおり動作し続けます。
  </Accordion>

  <Accordion title="Relationship to Amazon Bedrock provider">
    Bedrock Mantle は、標準の [Amazon Bedrock](/ja-JP/providers/bedrock) provider とは別の provider です。Mantle は OpenAI 互換の `/v1` サーフェスを使用し、標準 Bedrock provider はネイティブ Bedrock API を使用します。

    両方の provider は、存在する場合は同じ `AWS_BEARER_TOKEN_BEDROCK` credential を共有します。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Amazon Bedrock" href="/ja-JP/providers/bedrock" icon="cloud">
    Anthropic Claude、Titan、その他のモデル向けのネイティブ Bedrock provider。
  </Card>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="OAuth and auth" href="/ja-JP/gateway/authentication" icon="key">
    認証の詳細と資格情報の再利用ルール。
  </Card>
  <Card title="Troubleshooting" href="/ja-JP/help/troubleshooting" icon="wrench">
    よくある問題とその解決方法。
  </Card>
</CardGroup>
