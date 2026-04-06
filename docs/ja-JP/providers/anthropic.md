---
read_when:
    - OpenClaw で Anthropic モデルを使いたい
summary: OpenClaw で APIキー経由で Anthropic Claude を使用する
title: Anthropic
x-i18n:
    generated_at: "2026-04-06T03:11:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: bbc6c4938674aedf20ff944bc04e742c9a7e77a5ff10ae4f95b5718504c57c2d
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic は **Claude** モデルファミリーを開発しており、API経由で利用できます。
OpenClaw では、新しい Anthropic セットアップには APIキー を使うべきです。既存の旧式の
Anthropic token プロファイルは、すでに設定されていればランタイムで引き続き尊重されます。

<Warning>
OpenClaw における Anthropic の課金区分は次のとおりです。

- **Anthropic APIキー**: 通常の Anthropic API 課金。
- **OpenClaw 内の Claude サブスクリプション認証**: Anthropic は OpenClaw ユーザーに対し、
  **2026年4月4日 午後12:00 PT / 午後8:00 BST** に、これは
  サードパーティハーネス利用と見なされ、**Extra Usage**（従量課金、
  サブスクリプションとは別請求）が必要であると伝えました。

私たちのローカル再現もこの区分と一致しています。

- 直接の `claude -p` は引き続き動作する場合があります
- `claude -p --append-system-prompt ...` は、
  プロンプトが OpenClaw を識別すると Extra Usage ガードに引っかかることがあります
- 同じ OpenClaw 風のシステムプロンプトでも、
  Anthropic SDK + `ANTHROPIC_API_KEY` 経路ではこのブロックは再現しません

したがって実用上のルールは、**Anthropic APIキー、または
Extra Usage 付きの Claude サブスクリプション** です。最も明確な本番経路が必要なら、Anthropic API
キーを使用してください。

Anthropic の現在の公開ドキュメント:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

最も明確な課金経路が必要なら、代わりに Anthropic APIキー を使用してください。
OpenClaw は、[OpenAI
Codex](/ja-JP/providers/openai)、[Qwen Cloud Coding Plan](/ja-JP/providers/qwen)、
[MiniMax Coding Plan](/ja-JP/providers/minimax)、[Z.AI / GLM Coding
Plan](/ja-JP/providers/glm) など、他のサブスクリプション型オプションもサポートしています。
</Warning>

## Option A: Anthropic APIキー

**最適な用途:** 標準的なAPIアクセスと従量課金。
Anthropic Console で APIキー を作成してください。

### CLIセットアップ

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Anthropic 設定スニペット

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Thinking のデフォルト（Claude 4.6）

- Anthropic Claude 4.6 モデルは、明示的な thinking レベルが設定されていない場合、OpenClaw ではデフォルトで `adaptive` thinking を使用します。
- メッセージ単位（`/think:<level>`）またはモデル params の
  `agents.defaults.models["anthropic/<model>"].params.thinking` で上書きできます。
- 関連する Anthropic ドキュメント:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Fast mode（Anthropic API）

OpenClaw の共有 `/fast` トグルは、`api.anthropic.com` に送られる APIキー 認証および OAuth 認証のリクエストを含む、公開の Anthropic 直接通信もサポートします。

- `/fast on` は `service_tier: "auto"` に対応します
- `/fast off` は `service_tier: "standard_only"` に対応します
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

- OpenClaw が Anthropic service tier を注入するのは、直接 `api.anthropic.com` へ送るリクエストだけです。`anthropic/*` をプロキシまたは gateway 経由でルーティングしている場合、`/fast` は `service_tier` を変更しません。
- 明示的な Anthropic `serviceTier` または `service_tier` モデル params が設定されている場合、両方があると `/fast` のデフォルトよりそちらが優先されます。
- Anthropic は有効な tier をレスポンスの `usage.service_tier` で報告します。Priority Tier 容量のないアカウントでは、`service_tier: "auto"` でも `standard` に解決される場合があります。

## Prompt caching（Anthropic API）

OpenClaw は Anthropic の prompt caching 機能をサポートしています。これは**API専用**です。旧式の Anthropic token 認証では cache 設定は尊重されません。

### 設定

モデル設定で `cacheRetention` パラメーターを使用します。

| Value   | Cache Duration | 説明                     |
| ------- | -------------- | ------------------------ |
| `none`  | キャッシュなし | prompt caching を無効化  |
| `short` | 5分            | API Key 認証のデフォルト |
| `long`  | 1時間          | 拡張キャッシュ           |

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

Anthropic API Key 認証を使用する場合、OpenClaw はすべての Anthropic モデルに対して自動的に `cacheRetention: "short"`（5分キャッシュ）を適用します。設定で `cacheRetention` を明示的に指定すれば、これを上書きできます。

### エージェント単位の cacheRetention 上書き

ベースラインとしてモデルレベルの params を使い、特定のエージェントは `agents.list[].params` で上書きします。

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // ほとんどのエージェント向けのベースライン
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // このエージェント専用の上書き
    ],
  },
}
```

キャッシュ関連 params の設定マージ順序:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params`（一致する `id`、キー単位で上書き）

これにより、同じモデルを使っていても、あるエージェントは長寿命キャッシュを維持し、別のエージェントは書き込みコストを避けるためにバースト的/再利用の少ないトラフィックでキャッシュを無効化できます。

### Bedrock Claude に関する注記

- Bedrock 上の Anthropic Claude モデル（`amazon-bedrock/*anthropic.claude*`）は、設定されていれば `cacheRetention` のパススルーを受け付けます。
- Anthropic 以外の Bedrock モデルは、ランタイムで `cacheRetention: "none"` に強制されます。
- Anthropic APIキー のスマートデフォルトは、明示的な値が設定されていない場合、Claude-on-Bedrock モデル参照にも `cacheRetention: "short"` を適用します。

## 1M context window（Anthropic beta）

Anthropic の 1M context window は beta 制限付きです。OpenClaw では、対応する Opus/Sonnet モデルごとに `params.context1m: true` で有効化します。

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

OpenClaw はこれを Anthropic リクエスト上の `anthropic-beta: context-1m-2025-08-07` にマッピングします。

これは、そのモデルに対して `params.context1m` が明示的に `true` に設定されている場合にのみ有効になります。

要件: Anthropic がその認証情報で長いコンテキストの使用を許可している必要があります
（通常は APIキー 課金、または OpenClaw の Claude-login 経路 / Extra Usage が有効な旧式 token 認証）。
そうでない場合、Anthropic は次を返します:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

注意: Anthropic は現在、旧式の Anthropic token 認証（`sk-ant-oat-*`）使用時には
`context-1m-*` beta リクエストを拒否します。旧式認証モードで
`context1m: true` を設定した場合、OpenClaw は警告を記録し、
必要な OAuth beta は維持したまま context1m beta ヘッダーをスキップして
標準の context window にフォールバックします。

## 削除済み: Claude CLI バックエンド

バンドルされていた Anthropic `claude-cli` バックエンドは削除されました。

- Anthropic の 2026年4月4日の通知では、OpenClaw 主導の Claude-login トラフィックは
  サードパーティハーネス利用であり、**Extra Usage** が必要だとされています。
- 私たちのローカル再現でも、
  直接の `claude -p --append-system-prompt ...` が、追加された
  プロンプトが OpenClaw を識別する場合に同じガードに当たることが示されています。
- 同じ OpenClaw 風のシステムプロンプトは、
  Anthropic SDK + `ANTHROPIC_API_KEY` 経路ではそのガードに当たりません。
- OpenClaw における Anthropic トラフィックには Anthropic APIキー を使用してください。

## 注記

- Anthropic の公開 Claude Code ドキュメントでは、`claude -p` のような直接CLI利用が引き続き説明されていますが、Anthropic が OpenClaw ユーザーへ別途出した通知では、**OpenClaw** の Claude-login 経路はサードパーティハーネス利用であり、**Extra Usage**（サブスクリプションとは別の従量課金）が必要とされています。
  私たちのローカル再現でも、
  直接の `claude -p --append-system-prompt ...` が、追加された
  プロンプトが OpenClaw を識別する場合に同じガードへ当たることが示されている一方、同じプロンプト形状は
  Anthropic SDK + `ANTHROPIC_API_KEY` 経路では再現しません。本番用途では、
  代わりに Anthropic APIキー を推奨します。
- Anthropic setup-token は、OpenClaw で旧式/手動の経路として再び利用可能です。Anthropic の OpenClaw 固有の課金通知は引き続き適用されるため、この経路には Anthropic が **Extra Usage** を要求する前提で使用してください。
- 認証の詳細と再利用ルールは [/concepts/oauth](/ja-JP/concepts/oauth) にあります。

## トラブルシューティング

**401エラー / token が突然無効になった**

- 旧式の Anthropic token 認証は期限切れまたは失効することがあります。
- 新しいセットアップでは、Anthropic APIキー へ移行してください。

**provider "anthropic" の APIキー が見つかりません**

- 認証は**エージェント単位**です。新しいエージェントはメインエージェントのキーを引き継ぎません。
- そのエージェント向けにオンボーディングを再実行するか、gateway
  host で APIキー を設定し、その後 `openclaw models status` で確認してください。

**profile `anthropic:default` の認証情報が見つかりません**

- アクティブな認証プロファイルを確認するには `openclaw models status` を実行してください。
- オンボーディングを再実行するか、そのプロファイル経路向けに APIキー を設定してください。

**利用可能な認証プロファイルがない（すべてクールダウン中/利用不可）**

- `openclaw models status --json` で `auth.unusableProfiles` を確認してください。
- Anthropic のレート制限クールダウンはモデル単位になることがあるため、現在のモデルがクールダウン中でも、兄弟の Anthropic モデルはまだ利用可能な場合があります。
- 別の Anthropic プロファイルを追加するか、クールダウンを待ってください。

詳細: [/gateway/troubleshooting](/ja-JP/gateway/troubleshooting) と [/help/faq](/ja-JP/help/faq)。
