---
read_when:
    - Bedrock MantleでホストされるOSSモデルをOpenClawで使いたいとき
    - GPT-OSS、Qwen、Kimi、またはGLM向けのMantle OpenAI互換エンドポイントが必要なとき
summary: OpenClawでAmazon Bedrock Mantle（OpenAI互換）モデルを使用する
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-06T03:10:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e5b33ede4067fb7de02a046f3e375cbd2af4bf68e7751c8dd687447f1a78c86
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClawには、MantleのOpenAI互換エンドポイントに接続する、バンドル済みの **Amazon Bedrock Mantle** provider が含まれています。Mantleは、Bedrockインフラストラクチャを基盤とする標準的な `/v1/chat/completions` サーフェスを通じて、オープンソースおよびサードパーティモデル（GPT-OSS、Qwen、Kimi、GLM など）をホストします。

## OpenClawがサポートする内容

- Provider: `amazon-bedrock-mantle`
- API: `openai-completions`（OpenAI互換）
- 認証: 明示的な `AWS_BEARER_TOKEN_BEDROCK`、またはIAM資格情報チェーンによるベアラートークン生成
- リージョン: `AWS_REGION` または `AWS_DEFAULT_REGION`（デフォルト: `us-east-1`）

## 自動モデル検出

`AWS_BEARER_TOKEN_BEDROCK` が設定されている場合、OpenClawはそれを直接使用します。それ以外の場合、OpenClawは、共有credentials/configプロファイル、SSO、web identity、インスタンスロールまたはタスクロールを含むAWSデフォルト資格情報チェーンからMantleベアラートークンの生成を試みます。次に、そのリージョンの `/v1/models` エンドポイントを問い合わせて利用可能なMantleモデルを検出します。検出結果は1時間キャッシュされ、IAM由来のベアラートークンは1時間ごとに更新されます。

サポートされるリージョン: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## オンボーディング

1. **gateway host** で、次の認証パスのいずれか1つを選びます。

明示的なベアラートークン:

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# 任意（デフォルトは us-east-1）:
export AWS_REGION="us-west-2"
```

IAM資格情報:

```bash
# ここでは、任意のAWS SDK互換認証ソースが使えます。例:
export AWS_PROFILE="default"
export AWS_REGION="us-west-2"
```

2. モデルが検出されることを確認します。

```bash
openclaw models list
```

検出されたモデルは `amazon-bedrock-mantle` provider の下に表示されます。デフォルトを上書きしたい場合を除き、追加の設定は不要です。

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

## メモ

- `AWS_BEARER_TOKEN_BEDROCK` が設定されていない場合、OpenClawはAWS SDK互換のIAM資格情報からMantleベアラートークンを自動生成できます。
- このベアラートークンは、標準の [Amazon Bedrock](/ja-JP/providers/bedrock) provider で使われるものと同じ `AWS_BEARER_TOKEN_BEDROCK` です。
- reasoning サポートは、`thinking`、`reasoner`、`gpt-oss-120b` のようなパターンを含むモデルIDから推定されます。
- Mantleエンドポイントが利用できない場合、またはモデルを返さない場合、そのproviderは黙ってスキップされます。
