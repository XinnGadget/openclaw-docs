---
read_when:
    - OpenClawでAnthropicモデルを使いたい場合
summary: OpenClawでAPIキーまたはClaude CLI経由でAnthropic Claudeを使う
title: Anthropic
x-i18n:
    generated_at: "2026-04-07T04:45:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 423928fd36c66729985208d4d3f53aff1f94f63b908df85072988bdc41d5cf46
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropicは**Claude**モデルファミリーを開発しており、APIと
Claude CLIを通じて利用できます。OpenClawでは、Anthropic APIキーとClaude CLIの再利用の両方が
サポートされています。既存のレガシーAnthropicトークンプロファイルも、すでに設定済みであれば
引き続きランタイムで尊重されます。

<Warning>
Anthropicのスタッフから、OpenClawスタイルのClaude CLI利用は再び許可されていると伝えられたため、
Anthropicが新しいポリシーを公開しない限り、OpenClawはこの統合においてClaude CLIの再利用と`claude -p`の利用を許可済みとして扱います。

長期間稼働するGatewayホストでは、Anthropic APIキーが依然として最も明確で
予測しやすい本番運用パスです。ホスト上ですでにClaude CLIを使っている場合、
OpenClawはそのログインを直接再利用できます。

Anthropicの現在の公開ドキュメント:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

最も明確な課金パスを望む場合は、代わりにAnthropic APIキーを使ってください。
OpenClawは、[OpenAI
Codex](/ja-JP/providers/openai)、[Qwen Cloud Coding Plan](/ja-JP/providers/qwen)、
[MiniMax Coding Plan](/ja-JP/providers/minimax)、および [Z.AI / GLM Coding
Plan](/ja-JP/providers/glm) を含む、他のサブスクリプション型オプションもサポートしています。
</Warning>

## オプションA: Anthropic APIキー

**最適な用途:** 標準的なAPIアクセスと従量課金。
APIキーはAnthropic Consoleで作成してください。

### CLIセットアップ

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Anthropic設定スニペット

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Thinkingのデフォルト（Claude 4.6）

- Anthropic Claude 4.6モデルは、明示的なthinkingレベルが設定されていない場合、OpenClawではデフォルトで`adaptive` thinkingになります。
- メッセージごと（`/think:<level>`）またはモデルパラメータ
  `agents.defaults.models["anthropic/<model>"].params.thinking`
  でオーバーライドできます。
- 関連するAnthropicドキュメント:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Fast mode（Anthropic API）

OpenClawの共通`/fast`トグルは、APIキーおよびOAuth認証済みで`api.anthropic.com`へ送信されるリクエストを含む、公開Anthropicへの直接トラフィックもサポートしています。

- `/fast on` は `service_tier: "auto"` に対応
- `/fast off` は `service_tier: "standard_only"` に対応
- 設定デフォルト:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

重要な制限:

- OpenClawがAnthropic service tiersを注入するのは、直接の`api.anthropic.com`リクエストに対してのみです。`anthropic/*`をプロキシまたはGateway経由でルーティングする場合、`/fast`は`service_tier`を変更しません。
- 明示的なAnthropicの`serviceTier`または`service_tier`モデルパラメータが設定されている場合、両方があるときはそれらが`/fast`のデフォルトを上書きします。
- Anthropicは有効なtierをレスポンスの`usage.service_tier`で報告します。Priority Tier容量のないアカウントでは、`service_tier: "auto"`でも`standard`に解決される場合があります。

## Prompt caching（Anthropic API）

OpenClawはAnthropicのprompt caching機能をサポートしています。これは**API専用**です。レガシーAnthropicトークン認証ではキャッシュ設定は尊重されません。

### 設定

モデル設定で`cacheRetention`パラメータを使います。

| Value   | Cache Duration | Description              |
| ------- | -------------- | ------------------------ |
| `none`  | キャッシュなし | prompt cachingを無効化 |
| `short` | 5分 | API Key認証のデフォルト |
| `long`  | 1時間 | 拡張キャッシュ |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### デフォルト

Anthropic API Key認証を使用している場合、OpenClawはすべてのAnthropicモデルに対して自動的に`cacheRetention: "short"`（5分キャッシュ）を適用します。設定で`cacheRetention`を明示的に指定すれば、これをオーバーライドできます。

### エージェントごとのcacheRetentionオーバーライド

モデルレベルのparamsをベースラインとして使い、その後`agents.list[].params`で特定のagentをオーバーライドします。

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // ほとんどのagent向けのベースライン
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // このagentだけのオーバーライド
    ],
  },
}
```

キャッシュ関連パラメータの設定マージ順序:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params`（一致する`id`、キーごとに上書き）

これにより、同じモデル上のあるagentは長時間のキャッシュを維持しつつ、別のagentはキャッシュを無効化して、突発的で再利用の少ないトラフィックにおける書き込みコストを避けられます。

### Bedrock Claudeに関する注意

- Bedrock上のAnthropic Claudeモデル（`amazon-bedrock/*anthropic.claude*`）は、設定されていれば`cacheRetention`のパススルーを受け付けます。
- Anthropic以外のBedrockモデルは、ランタイムで強制的に`cacheRetention: "none"`になります。
- Anthropic APIキーのスマートデフォルトは、明示的な値が設定されていない場合、Claude-on-Bedrockのmodel refに対しても`cacheRetention: "short"`を初期値として設定します。

## 1Mコンテキストウィンドウ（Anthropic beta）

Anthropicの1Mコンテキストウィンドウはbeta制です。OpenClawでは、対応するOpus/Sonnetモデルごとに
`params.context1m: true`で有効にします。

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClawはこれをAnthropic
リクエスト上の`anthropic-beta: context-1m-2025-08-07`にマッピングします。

これは、そのモデルに対して`params.context1m`が明示的に`true`に設定されている場合にのみ有効化されます。

要件: Anthropicがその認証情報で長コンテキスト利用を許可している必要があります。

注: Anthropicは現在、レガシーAnthropicトークン認証（`sk-ant-oat-*`）を使用している場合、
`context-1m-*` betaリクエストを拒否します。このレガシー認証モードで
`context1m: true`を設定した場合、OpenClawは警告をログに出し、
必要なOAuth betaは維持したまま、context1m beta
ヘッダーをスキップして標準のコンテキストウィンドウへフォールバックします。

## Claude CLIバックエンド

バンドル済みのAnthropic `claude-cli`バックエンドはOpenClawでサポートされています。

- Anthropicのスタッフから、この利用は再び許可されていると伝えられました。
- そのためOpenClawは、Anthropicが新しいポリシーを公開しない限り、この統合においてClaude CLIの再利用と`claude -p`の利用を許可済みとして扱います。
- Anthropic APIキーは、常時稼働するGateway
  ホストと明示的なサーバー側課金制御において、依然として最も明確な本番運用パスです。
- セットアップとランタイムの詳細は[/gateway/cli-backends](/ja-JP/gateway/cli-backends)にあります。

## 注意事項

- Anthropicの公開Claude Codeドキュメントは、依然として
  `claude -p`のような直接CLI利用を記載しており、AnthropicのスタッフからもOpenClawスタイルのClaude CLI利用は
  再び許可されていると伝えられています。Anthropicが
  新しいポリシー変更を公開しない限り、私たちはこのガイダンスを確定したものとして扱っています。
- Anthropic setup-tokenは、サポートされるtoken-authパスとしてOpenClawで引き続き利用可能ですが、OpenClawは現在、利用可能な場合はClaude CLIの再利用と`claude -p`を優先します。
- 認証の詳細と再利用ルールは[/concepts/oauth](/ja-JP/concepts/oauth)にあります。

## トラブルシューティング

**401エラー / トークンが突然無効になった**

- Anthropicのトークン認証は期限切れまたは失効することがあります。
- 新規セットアップでは、Anthropic APIキーへ移行してください。

**provider "anthropic" のAPIキーが見つかりません**

- 認証は**agentごと**です。新しいagentはメインagentのキーを引き継ぎません。
- そのagentに対してオンボーディングを再実行するか、Gateway
  ホストにAPIキーを設定してから、`openclaw models status`で確認してください。

**プロファイル`anthropic:default`の認証情報が見つかりません**

- どの認証プロファイルがアクティブかを確認するには`openclaw models status`を実行してください。
- オンボーディングを再実行するか、そのプロファイルパスにAPIキーを設定してください。

**利用可能な認証プロファイルがありません（すべてクールダウン中/利用不可）**

- `auth.unusableProfiles`を確認するには`openclaw models status --json`を使ってください。
- Anthropicのレート制限クールダウンはモデルスコープの場合があるため、現在のモデルがクールダウン中でも、兄弟のAnthropic
  モデルはまだ利用できる可能性があります。
- 別のAnthropicプロファイルを追加するか、クールダウンが終わるまで待ってください。

詳細: [/gateway/troubleshooting](/ja-JP/gateway/troubleshooting) と [/help/faq](/ja-JP/help/faq)。
