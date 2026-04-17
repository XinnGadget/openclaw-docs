---
read_when:
    - OpenClaw で Amazon Bedrock モデルを使いたい
    - モデル呼び出しには AWS の認証情報とリージョン設定が必要です
summary: OpenClaw で Amazon Bedrock（Converse API）モデルを使う
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-12T23:30:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88e7e24907ec26af098b648e2eeca32add090a9e381c818693169ab80aeccc47
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw は、pi-ai の **Bedrock Converse** ストリーミング provider を通じて **Amazon Bedrock** モデルを使用できます。Bedrock の認証では **AWS SDK デフォルト認証情報チェーン** を使用し、API キーは使いません。

| プロパティ | 値                                                          |
| -------- | ----------------------------------------------------------- |
| Provider | `amazon-bedrock`                                            |
| API      | `bedrock-converse-stream`                                   |
| Auth     | AWS 認証情報（環境変数、共有設定、またはインスタンスロール） |
| Region   | `AWS_REGION` または `AWS_DEFAULT_REGION`（デフォルト: `us-east-1`） |

## はじめに

好みの認証方法を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="アクセスキー / 環境変数">
    **最適な用途:** 開発マシン、CI、または AWS 認証情報を直接管理するホスト。

    <Steps>
      <Step title="Gateway ホストに AWS 認証情報を設定する">
        ```bash
        export AWS_ACCESS_KEY_ID="AKIA..."
        export AWS_SECRET_ACCESS_KEY="..."
        export AWS_REGION="us-east-1"
        # Optional:
        export AWS_SESSION_TOKEN="..."
        export AWS_PROFILE="your-profile"
        # Optional (Bedrock API key/bearer token):
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```
      </Step>
      <Step title="設定に Bedrock provider と model を追加する">
        `apiKey` は不要です。`auth: "aws-sdk"` で provider を設定します。

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
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Tip>
    env-marker auth（`AWS_ACCESS_KEY_ID`、`AWS_PROFILE`、または `AWS_BEARER_TOKEN_BEDROCK`）を使う場合、OpenClaw は追加設定なしで、モデル検出用の暗黙的な Bedrock provider を自動で有効にします。
    </Tip>

  </Tab>

  <Tab title="EC2 インスタンスロール（IMDS）">
    **最適な用途:** IAM ロールがアタッチされた EC2 インスタンスで、認証にインスタンスメタデータサービスを使う場合。

    <Steps>
      <Step title="検出を明示的に有効にする">
        IMDS を使用する場合、OpenClaw は環境変数マーカーだけでは AWS auth を検出できないため、明示的にオプトインする必要があります。

        ```bash
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1
        ```
      </Step>
      <Step title="必要に応じて自動モード用の env marker を追加する">
        env-marker の自動検出経路も動かしたい場合（たとえば `openclaw status` の画面向け）:

        ```bash
        export AWS_PROFILE=default
        export AWS_REGION=us-east-1
        ```

        ダミーの API キーは**不要**です。
      </Step>
      <Step title="モデルが検出されることを確認する">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Warning>
    EC2 インスタンスにアタッチされた IAM ロールには、次の権限が必要です。

    - `bedrock:InvokeModel`
    - `bedrock:InvokeModelWithResponseStream`
    - `bedrock:ListFoundationModels`（自動検出用）
    - `bedrock:ListInferenceProfiles`（推論プロファイル検出用）

    または、マネージドポリシー `AmazonBedrockFullAccess` をアタッチしてください。
    </Warning>

    <Note>
    `AWS_PROFILE=default` が必要なのは、自動モードや status 画面のために env marker が必要な場合だけです。実際の Bedrock 実行時 auth 経路は AWS SDK デフォルトチェーンを使うため、IMDS のインスタンスロール認証は env marker がなくても動作します。
    </Note>

  </Tab>
</Tabs>

## 自動モデル検出

OpenClaw は、**ストリーミング** と **テキスト出力** をサポートする Bedrock モデルを自動的に検出できます。検出には `bedrock:ListFoundationModels` と `bedrock:ListInferenceProfiles` を使用し、結果はキャッシュされます（デフォルト: 1 時間）。

暗黙的 provider が有効になる仕組み:

- `plugins.entries.amazon-bedrock.config.discovery.enabled` が `true` の場合、AWS env marker が存在しなくても OpenClaw は検出を試みます。
- `plugins.entries.amazon-bedrock.config.discovery.enabled` が未設定の場合、OpenClaw は次のいずれかの AWS auth marker を検出したときにのみ、暗黙的 Bedrock provider を自動追加します:
  `AWS_BEARER_TOKEN_BEDROCK`、`AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY`、または `AWS_PROFILE`。
- 実際の Bedrock 実行時 auth 経路は引き続き AWS SDK デフォルトチェーンを使うため、共有設定、SSO、IMDS インスタンスロール認証は、検出に `enabled: true` が必要だった場合でも動作します。

<Note>
明示的な `models.providers["amazon-bedrock"]` エントリーに対しても、OpenClaw は `AWS_BEARER_TOKEN_BEDROCK` などの AWS env marker から Bedrock env-marker auth を早期解決できますが、完全な実行時 auth ロードは強制しません。実際の model 呼び出し auth 経路は引き続き AWS SDK デフォルトチェーンを使います。
</Note>

<AccordionGroup>
  <Accordion title="検出設定オプション">
    設定オプションは `plugins.entries.amazon-bedrock.config.discovery` 配下にあります。

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

    | オプション | デフォルト | 説明 |
    | ------ | ------- | ----------- |
    | `enabled` | auto | 自動モードでは、OpenClaw はサポートされた AWS env marker を検出したときだけ暗黙的 Bedrock provider を有効にします。検出を強制するには `true` を設定します。 |
    | `region` | `AWS_REGION` / `AWS_DEFAULT_REGION` / `us-east-1` | 検出 API 呼び出しに使用する AWS リージョン。 |
    | `providerFilter` | (all) | Bedrock provider 名に一致します（例: `anthropic`, `amazon`）。 |
    | `refreshInterval` | `3600` | 秒単位のキャッシュ期間。キャッシュを無効にするには `0` を設定します。 |
    | `defaultContextWindow` | `32000` | 検出されたモデルに使用するコンテキストウィンドウ（モデル制限がわかっている場合は上書きしてください）。 |
    | `defaultMaxTokens` | `4096` | 検出されたモデルに使用する最大出力トークン数（モデル制限がわかっている場合は上書きしてください）。 |

  </Accordion>
</AccordionGroup>

## クイックセットアップ（AWS パス）

この手順では IAM ロールを作成し、Bedrock 権限をアタッチし、インスタンスプロファイルを関連付け、EC2 ホストで OpenClaw の検出を有効にします。

```bash
# 1. IAM ロールとインスタンスプロファイルを作成する
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

# 2. EC2 インスタンスにアタッチする
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. EC2 インスタンス上で、検出を明示的に有効にする
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. 任意: 明示的な有効化なしで自動モードを使いたい場合は env marker を追加する
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. モデルが検出されることを確認する
openclaw models list
```

## 高度な設定

<AccordionGroup>
  <Accordion title="推論プロファイル">
    OpenClaw は、foundation model と並んで **リージョナルおよびグローバル推論プロファイル** を検出します。プロファイルが既知の foundation model に対応している場合、そのプロファイルはそのモデルの機能（コンテキストウィンドウ、最大トークン数、reasoning、vision）を継承し、正しい Bedrock リクエストリージョンが自動的に注入されます。これにより、クロスリージョンの Claude プロファイルは手動の provider 上書きなしで動作します。

    推論プロファイル ID は `us.anthropic.claude-opus-4-6-v1:0`（リージョナル）や `anthropic.claude-opus-4-6-v1:0`（グローバル）のような形です。背後のモデルがすでに検出結果に含まれている場合、プロファイルはその完全な機能セットを継承し、そうでない場合は安全なデフォルトが適用されます。

    追加設定は不要です。検出が有効で、IAM principal に `bedrock:ListInferenceProfiles` があれば、プロファイルは `openclaw models list` で foundation model と並んで表示されます。

  </Accordion>

  <Accordion title="Guardrails">
    `amazon-bedrock` Plugin 設定に `guardrail` オブジェクトを追加することで、すべての Bedrock モデル呼び出しに [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) を適用できます。Guardrails により、コンテンツフィルタリング、トピック拒否、単語フィルター、機密情報フィルター、コンテキストに基づくグラウンディングチェックを強制できます。

    ```json5
    {
      plugins: {
        entries: {
          "amazon-bedrock": {
            config: {
              guardrail: {
                guardrailIdentifier: "abc123", // guardrail ID または完全な ARN
                guardrailVersion: "1", // バージョン番号、または "DRAFT"
                streamProcessingMode: "sync", // optional: "sync" または "async"
                trace: "enabled", // optional: "enabled"、"disabled"、または "enabled_full"
              },
            },
          },
        },
      },
    }
    ```

    | オプション | 必須 | 説明 |
    | ------ | -------- | ----------- |
    | `guardrailIdentifier` | はい | Guardrail ID（例: `abc123`）または完全な ARN（例: `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`）。 |
    | `guardrailVersion` | はい | 公開済みバージョン番号、または作業中ドラフトの `"DRAFT"`。 |
    | `streamProcessingMode` | いいえ | ストリーミング中の guardrail 評価に使う `"sync"` または `"async"`。省略時は Bedrock のデフォルトが使われます。 |
    | `trace` | いいえ | デバッグ用の `"enabled"` または `"enabled_full"`。本番では省略するか `"disabled"` を設定します。 |

    <Warning>
    Gateway が使用する IAM principal には、標準の invoke 権限に加えて `bedrock:ApplyGuardrail` 権限が必要です。
    </Warning>

  </Accordion>

  <Accordion title="memory search 用の埋め込み">
    Bedrock は [memory search](/ja-JP/concepts/memory-search) の埋め込み provider としても使用できます。これは推論 provider とは別に設定します。`agents.defaults.memorySearch.provider` を `"bedrock"` に設定してください。

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: {
            provider: "bedrock",
            model: "amazon.titan-embed-text-v2:0", // default
          },
        },
      },
    }
    ```

    Bedrock の埋め込みは、推論と同じ AWS SDK 認証情報チェーン（インスタンスロール、SSO、アクセスキー、共有設定、web identity）を使用します。API キーは不要です。`provider` が `"auto"` の場合、その認証情報チェーンが正常に解決されれば Bedrock は自動検出されます。

    サポートされる埋め込みモデルには、Amazon Titan Embed（v1、v2）、Amazon Nova
    Embed、Cohere Embed（v3、v4）、TwelveLabs Marengo が含まれます。完全なモデル一覧と次元オプションについては、
    [メモリ設定リファレンス -- Bedrock](/ja-JP/reference/memory-config#bedrock-embedding-config)
    を参照してください。

  </Accordion>

  <Accordion title="注意事項と制限">
    - Bedrock では、AWS アカウント/リージョンで **model access** を有効にする必要があります。
    - 自動検出には `bedrock:ListFoundationModels` と
      `bedrock:ListInferenceProfiles` の権限が必要です。
    - 自動モードに依存する場合は、サポートされている AWS auth env marker のいずれかを
      Gateway ホストに設定してください。env marker なしで IMDS/共有設定 auth を使いたい場合は、
      `plugins.entries.amazon-bedrock.config.discovery.enabled: true` を設定してください。
    - OpenClaw は認証情報ソースを次の順序で表示します: `AWS_BEARER_TOKEN_BEDROCK`、
      次に `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`、次に `AWS_PROFILE`、最後に
      デフォルトの AWS SDK チェーンです。
    - reasoning のサポートは model に依存します。現在の機能については Bedrock の model card を確認してください。
    - マネージドキーのフローを好む場合は、Bedrock の前段に OpenAI 互換の
      プロキシを置き、代わりに OpenAI provider として設定することもできます。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Memory Search" href="/ja-JP/concepts/memory-search" icon="magnifying-glass">
    memory search 用 Bedrock 埋め込みの設定。
  </Card>
  <Card title="メモリ設定リファレンス" href="/ja-JP/reference/memory-config#bedrock-embedding-config" icon="database">
    完全な Bedrock 埋め込みモデル一覧と次元オプション。
  </Card>
  <Card title="トラブルシューティング" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的なトラブルシューティングと FAQ。
  </Card>
</CardGroup>
