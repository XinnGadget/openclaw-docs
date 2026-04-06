---
read_when:
    - OpenClaw の OAuth の全体像を理解したい場合
    - トークン無効化やログアウトの問題が発生した場合
    - Claude CLI または OAuth 認証フローを使いたい場合
    - 複数アカウントまたはプロファイルルーティングを使いたい場合
summary: 'OpenClaw における OAuth: トークン交換、保存、複数アカウントのパターン'
title: OAuth
x-i18n:
    generated_at: "2026-04-06T03:07:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 402e20dfeb6ae87a90cba5824a56a7ba3b964f3716508ea5cc48a47e5affdd73
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw は、それを提供するプロバイダー向けに、OAuth による「subscription auth」をサポートしています
（特に **OpenAI Codex (ChatGPT OAuth)**）。Anthropic については、実用上の区分は現在次のとおりです。

- **Anthropic API key**: 通常の Anthropic API 課金
- **OpenClaw 内の Anthropic subscription auth**: Anthropic は OpenClaw
  ユーザーに対し、**2026 年 4 月 4 日 午後 12:00 PT / 午後 8:00 BST** に、これには現在
  **Extra Usage** が必要であると通知しました

OpenAI Codex OAuth は、OpenClaw のような外部ツールでの利用が明示的にサポートされています。このページでは次を説明します。

本番環境で Anthropic を使う場合、より安全で推奨される経路は API key 認証です。

- OAuth の **トークン交換** の仕組み（PKCE）
- トークンが **保存** される場所（およびその理由）
- **複数アカウント** の扱い方（プロファイル + セッションごとの上書き）

OpenClaw は、独自の OAuth または API‑key
フローを提供する **provider plugins** もサポートしています。実行方法:

```bash
openclaw models auth login --provider <id>
```

## トークンシンク（なぜ存在するのか）

OAuth プロバイダーは、ログイン/リフレッシュフロー中に **新しい refresh token** を発行することがよくあります。プロバイダーや OAuth クライアントによっては、同じユーザー/アプリに対して新しいものが発行されると、古い refresh token が無効化されることがあります。

実際の症状:

- OpenClaw でも、Claude Code / Codex CLI でもログインすると → 後でどちらかがランダムに「ログアウト」状態になる

これを軽減するために、OpenClaw は `auth-profiles.json` を **トークンシンク** として扱います。

- ランタイムは **1 か所** から認証情報を読み取ります
- 複数のプロファイルを保持して、決定的にルーティングできます
- Codex CLI のような外部 CLI から認証情報を再利用する場合、OpenClaw は
  それらを来歴付きでミラーし、
  refresh token 自体をローテーションする代わりに、その外部ソースを再読込します

## 保存場所（トークンはどこに保存されるか）

シークレットは **エージェントごと** に保存されます。

- Auth プロファイル（OAuth + API keys + オプションの値レベル参照）: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 旧互換ファイル: `~/.openclaw/agents/<agentId>/agent/auth.json`
  （静的な `api_key` エントリーは発見時に消去されます）

旧インポート専用ファイル（引き続きサポートされますが、メインの保存先ではありません）:

- `~/.openclaw/credentials/oauth.json`（初回使用時に `auth-profiles.json` へインポートされます）

上記はいずれも `$OPENCLAW_STATE_DIR`（状態ディレクトリ上書き）に従います。完全なリファレンス: [/gateway/configuration](/ja-JP/gateway/configuration-reference#auth-storage)

静的シークレット参照とランタイムのスナップショット有効化動作については、[Secrets Management](/ja-JP/gateway/secrets) を参照してください。

## Anthropic の旧トークン互換性

<Warning>
Anthropic の公開 Claude Code ドキュメントでは、Claude Code を直接使用する場合は
Claude subscription の制限内に収まるとされています。一方で、Anthropic は OpenClaw ユーザーに対し、
**2026 年 4 月 4 日 午後 12:00 PT / 午後 8:00 BST** に、**OpenClaw は
サードパーティのハーネスとして扱われる** と通知しました。既存の Anthropic トークンプロファイルは
技術的には OpenClaw で引き続き利用可能ですが、Anthropic によれば OpenClaw 経由では現在
そのトラフィックに **Extra Usage**（subscription とは別に従量課金）が必要です。

Anthropic の現在の Claude Code 直接利用向けプラン文書については、[Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
および [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)
を参照してください。

OpenClaw で他の subscription 形式の選択肢を使いたい場合は、[OpenAI
Codex](/ja-JP/providers/openai)、[Qwen Cloud Coding
Plan](/ja-JP/providers/qwen)、[MiniMax Coding Plan](/ja-JP/providers/minimax)、
[Z.AI / GLM Coding Plan](/ja-JP/providers/glm) を参照してください。
</Warning>

OpenClaw は現在、Anthropic setup-token を旧式/手動の経路として再び公開しています。
この経路にも Anthropic の OpenClaw 固有の課金通知が引き続き適用されるため、
OpenClaw 主導の Claude ログイントラフィックには Anthropic が **Extra Usage** を要求する
という前提で使用してください。

## Anthropic Claude CLI 移行

Anthropic には、OpenClaw におけるサポート対象のローカル Claude CLI 移行経路はもはやありません。
Anthropic トラフィックには Anthropic API keys を使用するか、すでに設定済みの場所に限って旧式の
トークンベース認証を維持してください。その場合も、Anthropic はその OpenClaw 経路を
**Extra Usage** として扱う前提になります。

## OAuth 交換（ログインの仕組み）

OpenClaw の対話型ログインフローは `@mariozechner/pi-ai` に実装されており、ウィザード/コマンドに組み込まれています。

### Anthropic setup-token

フローの形:

1. OpenClaw から Anthropic setup-token を開始する、またはトークンを貼り付ける
2. OpenClaw は結果の Anthropic 認証情報を auth プロファイルに保存する
3. モデル選択は `anthropic/...` のまま維持される
4. 既存の Anthropic auth プロファイルは、ロールバック/順序制御のために引き続き利用可能

### OpenAI Codex（ChatGPT OAuth）

OpenAI Codex OAuth は、Codex CLI の外部、OpenClaw ワークフローを含めて使用することが明示的にサポートされています。

フローの形（PKCE）:

1. PKCE verifier/challenge + ランダムな `state` を生成する
2. `https://auth.openai.com/oauth/authorize?...` を開く
3. `http://127.0.0.1:1455/auth/callback` でコールバックをキャプチャしようとする
4. コールバックをバインドできない場合（またはリモート/ヘッドレス環境の場合）、リダイレクト URL/コードを貼り付ける
5. `https://auth.openai.com/oauth/token` で交換する
6. アクセストークンから `accountId` を抽出し、`{ access, refresh, expires, accountId }` を保存する

ウィザード経路は `openclaw onboard` → auth 選択 `openai-codex` です。

## リフレッシュ + 有効期限

プロファイルには `expires` タイムスタンプが保存されます。

ランタイムでは:

- `expires` が未来なら → 保存済みの access token を使用する
- 期限切れなら → リフレッシュし（ファイルロック下）、保存済み認証情報を上書きする
- 例外: 再利用された外部 CLI 認証情報は外部管理のままです。OpenClaw は
  CLI の auth ストアを再読込し、コピーされた refresh token 自体は決して使用しません

リフレッシュフローは自動です。通常、トークンを手動で管理する必要はありません。

## 複数アカウント（プロファイル） + ルーティング

2 つのパターンがあります。

### 1) 推奨: エージェントを分ける

「個人」と「仕事」を決して相互作用させたくない場合は、分離されたエージェント（別セッション + 別認証情報 + 別ワークスペース）を使用します。

```bash
openclaw agents add work
openclaw agents add personal
```

その後、エージェントごとに auth を設定し（ウィザード）、チャットを適切なエージェントにルーティングします。

### 2) 上級者向け: 1 つのエージェントで複数プロファイル

`auth-profiles.json` は、同じプロバイダーに対して複数のプロファイル ID をサポートします。

どのプロファイルを使うかの指定方法:

- グローバルには設定順序（`auth.order`）で
- セッションごとには `/model ...@<profileId>` で

例（セッション上書き）:

- `/model Opus@anthropic:work`

存在するプロファイル ID の確認方法:

- `openclaw channels list --json`（`auth[]` を表示）

関連ドキュメント:

- [/concepts/model-failover](/ja-JP/concepts/model-failover)（ローテーション + クールダウンルール）
- [/tools/slash-commands](/ja-JP/tools/slash-commands)（コマンドサーフェス）

## 関連

- [Authentication](/ja-JP/gateway/authentication) — モデルプロバイダー認証の概要
- [Secrets](/ja-JP/gateway/secrets) — 認証情報の保存と SecretRef
- [Configuration Reference](/ja-JP/gateway/configuration-reference#auth-storage) — auth 設定キー
