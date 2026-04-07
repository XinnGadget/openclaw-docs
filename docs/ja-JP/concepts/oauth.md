---
read_when:
    - OpenClawのOAuthをエンドツーエンドで理解したい
    - トークン無効化 / ログアウトの問題に遭遇した
    - Claude CLIまたはOAuthの認証フローを使いたい
    - 複数アカウントまたはプロファイルルーティングを使いたい
summary: 'OpenClawにおけるOAuth: トークン交換、保存、複数アカウントのパターン'
title: OAuth
x-i18n:
    generated_at: "2026-04-07T04:41:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4117fee70e3e64fd3a762403454ac2b78de695d2b85a7146750c6de615921e02
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClawは、それを提供するプロバイダー向けに、OAuthによる「サブスクリプション認証」をサポートしています
（特に **OpenAI Codex (ChatGPT OAuth)**）。Anthropicについては、実質的な区分は現在次のとおりです:

- **Anthropic API key**: 通常のAnthropic API課金
- **Anthropic Claude CLI / OpenClaw内のサブスクリプション認証**: Anthropicスタッフから、この利用は再び許可されていると案内されています

OpenAI Codex OAuthは、OpenClawのような外部ツールでの利用が明示的にサポートされています。このページでは次の内容を説明します:

本番環境でAnthropicを使う場合は、API key認証のほうがより安全で推奨される経路です。

- OAuthの**トークン交換**の仕組み（PKCE）
- トークンが**どこに保存されるか**（およびその理由）
- **複数アカウント**の扱い方（プロファイル + セッションごとの上書き）

OpenClawは、独自のOAuthまたはAPI‑keyフローを同梱する**プロバイダープラグイン**もサポートしています。次のコマンドで実行します:

```bash
openclaw models auth login --provider <id>
```

## トークンシンク（なぜ存在するのか）

OAuthプロバイダーは、ログインやリフレッシュのフロー中に**新しいrefresh token**を発行することが一般的です。一部のプロバイダー（またはOAuthクライアント）は、同じユーザー/アプリに対して新しいものが発行されると、古いrefresh tokenを無効化することがあります。

実際の症状:

- OpenClaw _と_ Claude Code / Codex CLI の両方でログインすると、あとでどちらかがランダムに「ログアウト」される

これを減らすため、OpenClawは `auth-profiles.json` を**トークンシンク**として扱います:

- ランタイムは**1か所**から認証情報を読み取ります
- 複数のプロファイルを保持し、それらを決定論的にルーティングできます
- 認証情報がCodex CLIのような外部CLIから再利用される場合、OpenClawはそれらを来歴付きでミラーし、自身でrefresh tokenをローテーションする代わりに、その外部ソースを再読込します

## 保存先（トークンはどこに保存されるか）

シークレットは**エージェントごと**に保存されます:

- 認証プロファイル（OAuth + API keys + 任意の値レベルref）: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 互換性維持用のレガシーファイル: `~/.openclaw/agents/<agentId>/agent/auth.json`
  （静的な `api_key` エントリーは見つかると除去されます）

レガシーのインポート専用ファイル（引き続きサポートされますが、メインの保存先ではありません）:

- `~/.openclaw/credentials/oauth.json` （初回使用時に `auth-profiles.json` にインポートされます）

上記のすべてで `$OPENCLAW_STATE_DIR`（state dir override）も尊重されます。完全なリファレンス: [/gateway/configuration](/ja-JP/gateway/configuration-reference#auth-storage)

静的SecretRefとランタイムスナップショットの有効化動作については、[Secrets Management](/ja-JP/gateway/secrets) を参照してください。

## Anthropicのレガシートークン互換性

<Warning>
Anthropicの公開されたClaude Codeドキュメントでは、Claude Codeの直接利用はClaudeサブスクリプションの上限内にとどまるとされており、Anthropicスタッフからも、OpenClawスタイルのClaude CLI利用は再び許可されていると案内されています。そのためOpenClawは、Anthropicが新しいポリシーを公開しない限り、この連携においてClaude CLIの再利用と `claude -p` の使用を認められたものとして扱います。

Anthropicの現在のdirect-Claude-Codeプランのドキュメントについては、[Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
および [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/) を参照してください。

OpenClawで他のサブスクリプション形式の選択肢を使いたい場合は、[OpenAI
Codex](/ja-JP/providers/openai)、[Qwen Cloud Coding
Plan](/ja-JP/providers/qwen)、[MiniMax Coding Plan](/ja-JP/providers/minimax)、
および [Z.AI / GLM Coding Plan](/ja-JP/providers/glm) を参照してください。
</Warning>

OpenClawは、Anthropic setup-tokenもサポートされるトークン認証経路として公開していますが、現在は利用可能な場合にClaude CLIの再利用と `claude -p` を優先します。

## Anthropic Claude CLI移行

OpenClawは再びAnthropic Claude CLIの再利用をサポートしています。ホスト上ですでにClaudeにローカルログインしている場合、オンボーディング/設定でそれを直接再利用できます。

## OAuth交換（ログインの仕組み）

OpenClawの対話型ログインフローは `@mariozechner/pi-ai` に実装され、ウィザード/コマンドに接続されています。

### Anthropic setup-token

フローの形:

1. OpenClawからAnthropic setup-tokenまたはpaste-tokenを開始する
2. OpenClawは結果として得られたAnthropic認証情報を認証プロファイルに保存する
3. モデル選択は `anthropic/...` のまま維持される
4. 既存のAnthropic認証プロファイルは、ロールバック/順序制御のため引き続き利用可能なままになる

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuthは、Codex CLIの外部を含むOpenClawワークフローでの利用が明示的にサポートされています。

フローの形（PKCE）:

1. PKCE verifier/challenge + ランダムな `state` を生成する
2. `https://auth.openai.com/oauth/authorize?...` を開く
3. `http://127.0.0.1:1455/auth/callback` でコールバックを受け取ろうとする
4. コールバックをbindできない場合（またはリモート/ヘッドレス環境の場合）は、リダイレクトURL/codeを貼り付ける
5. `https://auth.openai.com/oauth/token` で交換する
6. access tokenから `accountId` を抽出し、`{ access, refresh, expires, accountId }` を保存する

ウィザードの経路は `openclaw onboard` → 認証の選択肢 `openai-codex` です。

## リフレッシュ + 有効期限

プロファイルには `expires` タイムスタンプが保存されます。

ランタイムでは:

- `expires` が未来なら → 保存済みのaccess tokenを使う
- 期限切れなら → （ファイルロック下で）リフレッシュし、保存済み認証情報を上書きする
- 例外: 再利用される外部CLI認証情報は外部で管理されたままです。OpenClawはCLI認証ストアを再読込し、コピーされたrefresh token自体を消費しません

リフレッシュフローは自動です。通常、トークンを手動で管理する必要はありません。

## 複数アカウント（プロファイル）+ ルーティング

2つのパターンがあります:

### 1) 推奨: エージェントを分ける

「個人用」と「仕事用」を決して相互作用させたくない場合は、分離されたエージェント（別々のセッション + 認証情報 + ワークスペース）を使います:

```bash
openclaw agents add work
openclaw agents add personal
```

次に、エージェントごとに認証を設定し（ウィザード）、正しいエージェントにチャットをルーティングします。

### 2) 上級者向け: 1つのエージェントで複数プロファイル

`auth-profiles.json` は、同じプロバイダーに対して複数のプロファイルIDをサポートします。

どのプロファイルを使うかの指定方法:

- グローバルには設定順序（`auth.order`）経由
- セッションごとには `/model ...@<profileId>` 経由

例（セッション上書き）:

- `/model Opus@anthropic:work`

どのプロファイルIDが存在するかを確認する方法:

- `openclaw channels list --json` （`auth[]` を表示します）

関連ドキュメント:

- [/concepts/model-failover](/ja-JP/concepts/model-failover) （ローテーション + クールダウンルール）
- [/tools/slash-commands](/ja-JP/tools/slash-commands) （コマンドサーフェス）

## 関連

- [Authentication](/ja-JP/gateway/authentication) — モデルプロバイダー認証の概要
- [Secrets](/ja-JP/gateway/secrets) — 認証情報の保存とSecretRef
- [Configuration Reference](/ja-JP/gateway/configuration-reference#auth-storage) — 認証設定キー
