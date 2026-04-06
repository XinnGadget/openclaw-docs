---
read_when:
    - OpenClawでAmazon Bedrockモデルを使いたいとき
    - モデル呼び出しのためにAWS資格情報/リージョン設定が必要なとき
summary: OpenClawでAmazon Bedrock（Converse API）モデルを使う
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-06T03:11:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 70bb29fe9199084b1179ced60935b5908318f5b80ced490bf44a45e0467c4929
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClawは、pi‑aiの **Bedrock Converse** ストリーミングprovider経由で **Amazon Bedrock** モデルを使用できます。Bedrockの認証には **AWS SDK default credential chain** を使用し、APIキーは使いません。

## pi-aiがサポートする内容

- Provider: `amazon-bedrock`
- API: `bedrock-converse-stream`
- Auth: AWS資格情報（env vars、共有config、またはインスタンスロール）
- Region: `AWS_REGION` または `AWS_DEFAULT_REGION`（デフォルト: `us-east-1`）

## 自動モデル検出

OpenClawは、**streaming** と **text output** をサポートするBedrockモデルを自動検出できます。検出には `bedrock:ListFoundationModels` と `bedrock:ListInferenceProfiles` を使用し、結果はキャッシュされます（デフォルト: 1時間）。

暗黙のproviderが有効になる仕組み:

- `plugins.entries.amazon-bedrock.config.discovery.enabled` が `true` の場合、AWS env marker が存在しなくてもOpenClawは検出を試みます。
- `plugins.entries.amazon-bedrock.config.discovery.enabled` が未設定の場合、OpenClawは次のいずれかのAWS認証マーカーを検出したときにのみ、暗黙のBedrock provider を自動追加します: `AWS_BEARER_TOKEN_BEDROCK`、`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`、または `AWS_PROFILE`。
- 実際のBedrockランタイム認証パスは引き続きAWS SDK default chainを使用するため、shared config、SSO、IMDSインスタンスロール認証は、検出でオプトインのために `enabled: true` が必要だった場合でも機能します。

Configオプションは `plugins.entries.amazon-bedrock.config.discovery` 配下にあります。

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          discovery: {
            enabled: true,
            region: "us-east-1",
            providerFilter: ["anthropic", "amazon"],
            refreshInterval: 3600,
            defaultContextWindow: 32000,
            defaultMaxTokens: 4096,
          },
        },
      },
    },
  },
}
```

メモ:

- `enabled` のデフォルトはauto modeです。auto modeでは、OpenClawはサポートされているAWS env marker を検出した場合にのみ、暗黙のBedrock provider を有効化します。
- `region` のデフォルトは `AWS_REGION` または `AWS_DEFAULT_REGION`、その次に `us-east-1` です。
- `providerFilter` はBedrock provider 名（たとえば `anthropic`）に一致します。
- `refreshInterval` は秒単位です。キャッシュを無効にするには `0` を設定します。
- `defaultContextWindow`（デフォルト: `32000`）と `defaultMaxTokens`（デフォルト: `4096`）は検出されたモデルに使われます（モデル上限が分かっている場合は上書きしてください）。
- 明示的な `models.providers["amazon-bedrock"]` エントリについても、OpenClawは `AWS_BEARER_TOKEN_BEDROCK` のようなAWS env marker からBedrock env-marker auth を早期解決できますが、完全なランタイムauth読み込みを強制しません。実際のモデル呼び出し認証パスは引き続きAWS SDK default chainを使用します。

## オンボーディング

1. **gateway host** でAWS資格情報が利用可能であることを確認します。

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# 任意:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# 任意（Bedrock API key/bearer token）:
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. ConfigにBedrock provider とモデルを追加します（`apiKey` は不要です）。

```json5
{
  models: {
    providers: {
      "amazon-bedrock": {
        baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
        api: "bedrock-converse-stream",
        auth: "aws-sdk",
        models: [
          {
            id: "us.anthropic.claude-opus-4-6-v1:0",
            name: "Claude Opus 4.6 (Bedrock)",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
    },
  },
}
```

## EC2インスタンスロール

IAMロールが関連付けられたEC2インスタンス上でOpenClawを実行する場合、AWS SDKは認証にインスタンスメタデータサービス（IMDS）を使用できます。Bedrockモデル検出については、OpenClawは明示的に `plugins.entries.amazon-bedrock.config.discovery.enabled: true` を設定しない限り、AWS env marker からのみ暗黙のproviderを自動有効化します。

IMDSを使うホスト向けの推奨セットアップ:

- `plugins.entries.amazon-bedrock.config.discovery.enabled` を `true` に設定する。
- `plugins.entries.amazon-bedrock.config.discovery.region` を設定する（または `AWS_REGION` をexportする）。
- ダミーのAPIキーは不要です。
- auto mode またはstatusサーフェスのためにenv marker が欲しい場合にのみ `AWS_PROFILE=default` が必要です。

```bash
# 推奨: 明示的にdiscoveryを有効化し、regionを設定
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 任意: 明示的な有効化なしでauto modeを使いたい場合はenv markerを追加
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

EC2インスタンスロールに必要なIAM権限:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels`（自動検出用）
- `bedrock:ListInferenceProfiles`（推論プロファイル検出用）

または、マネージドポリシー `AmazonBedrockFullAccess` をアタッチしてください。

## クイックセットアップ（AWSパス）

```bash
# 1. IAMロールとインスタンスプロファイルを作成
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. EC2インスタンスにアタッチ
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. EC2インスタンス上で、discoveryを明示的に有効化
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. 任意: 明示的な有効化なしでauto modeを使いたい場合はenv markerを追加
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. モデルが検出されることを確認
openclaw models list
```

## 推論プロファイル

OpenClawは、foundation model と並んで **regional and global inference profiles** を検出します。あるプロファイルが既知のfoundation model に対応付けられる場合、そのプロファイルはそのモデルの機能（context window、max tokens、reasoning、vision）を継承し、正しいBedrockリクエストregionが自動的に注入されます。つまり、クロスリージョンのClaudeプロファイルは手動のprovider上書きなしで動作します。

推論プロファイルIDは `us.anthropic.claude-opus-4-6-v1:0`（regional）
または `anthropic.claude-opus-4-6-v1:0`（global）のような形式です。バックエンドのモデルがすでに検出結果に含まれていれば、そのプロファイルは完全な機能セットを継承し、そうでなければ安全なデフォルトが適用されます。

追加の設定は不要です。discoveryが有効で、IAM
principalが `bedrock:ListInferenceProfiles` を持っていれば、プロファイルは `openclaw models list` でfoundation model と並んで表示されます。

## メモ

- Bedrockでは、AWSアカウント/regionで **model access** が有効になっている必要があります。
- 自動検出には `bedrock:ListFoundationModels` と
  `bedrock:ListInferenceProfiles` 権限が必要です。
- auto modeに依存する場合は、サポートされているAWS auth env marker のいずれかを gateway host に設定してください。env markerなしでIMDS/shared-config auth を使いたい場合は、`plugins.entries.amazon-bedrock.config.discovery.enabled: true` を設定してください。
- OpenClawは資格情報ソースを次の順で表示します: `AWS_BEARER_TOKEN_BEDROCK`、
  次に `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`、次に `AWS_PROFILE`、最後に default AWS SDK chain。
- reasoning サポートはモデルによって異なります。現在の機能はBedrock model card で確認してください。
- 管理されたキーのフローを使いたい場合は、Bedrockの前段にOpenAI互換
  proxyを置いて、それをOpenAI provider として設定することもできます。

## ガードレール

`amazon-bedrock` プラグインconfigに `guardrail` オブジェクトを追加することで、すべてのBedrockモデル呼び出しに [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) を適用できます。Guardrailsを使うと、コンテンツフィルタリング、トピック拒否、単語フィルター、機密情報フィルター、コンテキストグラウンディングチェックを強制できます。

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          guardrail: {
            guardrailIdentifier: "abc123", // guardrail ID または完全な ARN
            guardrailVersion: "1", // バージョン番号または "DRAFT"
            streamProcessingMode: "sync", // 任意: "sync" または "async"
            trace: "enabled", // 任意: "enabled", "disabled", または "enabled_full"
          },
        },
      },
    },
  },
}
```

- `guardrailIdentifier`（必須）は、guardrail ID（例: `abc123`）または完全なARN（例: `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`）を受け付けます。
- `guardrailVersion`（必須）は、使用する公開済みバージョン、または作業ドラフト用の `"DRAFT"` を指定します。
- `streamProcessingMode`（任意）は、ストリーミング中のguardrail評価を同期的（`"sync"`）に実行するか、非同期的（`"async"`）に実行するかを制御します。省略した場合、Bedrockはデフォルト動作を使用します。
- `trace`（任意）は、APIレスポンスでguardrail trace出力を有効にします。デバッグには `"enabled"` または `"enabled_full"` を設定し、本番環境では省略するか `"disabled"` を設定してください。

gatewayが使用するIAM principal には、標準のinvoke権限に加えて `bedrock:ApplyGuardrail` 権限も必要です。

## memory search 用の埋め込み

Bedrockは [memory search](/ja-JP/concepts/memory-search) の埋め込みprovider としても使用できます。これは推論provider とは別に設定します。`agents.defaults.memorySearch.provider` を `"bedrock"` に設定してください。

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0", // デフォルト
      },
    },
  },
}
```

Bedrock embeddings は、推論と同じAWS SDK credential chain（インスタンスロール、SSO、access keys、shared config、web identity）を使用します。APIキーは不要です。`provider` が `"auto"` の場合、そのcredential chain が正常に解決されるとBedrockは自動検出されます。

サポートされるembedding model には、Amazon Titan Embed（v1、v2）、Amazon Nova
Embed、Cohere Embed（v3、v4）、TwelveLabs Marengo が含まれます。完全なモデル一覧と次元オプションについては、[Memory configuration reference — Bedrock](/ja-JP/reference/memory-config#bedrock-embedding-config) を参照してください。
