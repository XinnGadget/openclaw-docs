---
read_when:
    - モデル認証やOAuthの期限切れをデバッグしている
    - 認証や認証情報ストレージをドキュメント化している
summary: 'モデル認証: OAuth、APIキー、Claude CLIの再利用、Anthropic setup-token'
title: 認証
x-i18n:
    generated_at: "2026-04-07T04:41:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9db0ad9eccd7e3e3ca328adaad260bc4288a8ccdbe2dc0c24d9fd049b7ab9231
    source_path: gateway/authentication.md
    workflow: 15
---

# 認証（モデルプロバイダー）

<Note>
このページでは**モデルプロバイダー**の認証（APIキー、OAuth、Claude CLIの再利用、Anthropic setup-token）を扱います。**Gateway接続**の認証（トークン、パスワード、trusted-proxy）については、[Configuration](/ja-JP/gateway/configuration) と [Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth) を参照してください。
</Note>

OpenClawはモデルプロバイダー向けにOAuthとAPIキーをサポートしています。常時稼働のGateway
ホストでは、通常はAPIキーが最も予測しやすい選択肢です。サブスクリプション/OAuth
フローも、プロバイダーのアカウントモデルに合う場合はサポートされています。

完全なOAuthフローとストレージ
レイアウトについては [/concepts/oauth](/ja-JP/concepts/oauth) を参照してください。
SecretRefベースの認証（`env`/`file`/`exec` プロバイダー）については、[Secrets Management](/ja-JP/gateway/secrets) を参照してください。
`models status --probe` で使用される認証情報の適格性/理由コードのルールについては、
[Auth Credential Semantics](/ja-JP/auth-credential-semantics) を参照してください。

## 推奨セットアップ（APIキー、任意のプロバイダー）

長時間稼働するGatewayを動かしている場合は、選択した
プロバイダーのAPIキーから始めてください。
Anthropicについては特に、APIキー認証が依然として最も予測しやすいサーバー向け
セットアップですが、OpenClawはローカルのClaude CLIログインの再利用もサポートしています。

1. プロバイダーのコンソールでAPIキーを作成します。
2. それを**Gatewayホスト**（`openclaw gateway` を実行しているマシン）に配置します。

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Gatewayがsystemd/launchdの下で動作している場合は、デーモンが読み取れるように
   `~/.openclaw/.env` にキーを置くことを推奨します。

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

その後、デーモンを再起動する（またはGatewayプロセスを再起動する）か、再確認します。

```bash
openclaw models status
openclaw doctor
```

環境変数を自分で管理したくない場合は、オンボーディングで
デーモン用のAPIキーを保存できます: `openclaw onboard`。

`env.shellEnv`、`~/.openclaw/.env`、systemd/launchd における環境継承の詳細は [Help](/ja-JP/help) を参照してください。

## Anthropic: Claude CLIとトークン互換性

Anthropic setup-token認証は、OpenClawで引き続きサポートされているトークン
経路として利用できます。その後、Anthropicの担当者から、OpenClaw方式のClaude CLI利用は
再び許可されていると案内されたため、Anthropicが新しいポリシーを公開しない限り、
OpenClawはこの統合においてClaude CLIの再利用と `claude -p` の使用を認可済みとして扱います。ホスト上で
Claude CLIの再利用が利用できる場合、現在はこちらが推奨される経路です。

長時間稼働するGatewayホストでは、Anthropic APIキーが依然として最も予測しやすい
セットアップです。同じホスト上の既存のClaudeログインを再利用したい場合は、オンボーディング/設定で
Anthropic Claude CLI経路を使用してください。

手動トークン入力（任意のプロバイダー; `auth-profiles.json` に書き込み + 設定を更新）:

```bash
openclaw models auth paste-token --provider openrouter
```

静的認証情報では認証プロファイル参照もサポートされています。

- `api_key` 認証情報は `keyRef: { source, provider, id }` を使用できます
- `token` 認証情報は `tokenRef: { source, provider, id }` を使用できます
- OAuthモードのプロファイルはSecretRef認証情報をサポートしません。`auth.profiles.<id>.mode` が `"oauth"` に設定されている場合、そのプロファイルへのSecretRefベースの `keyRef`/`tokenRef` 入力は拒否されます。

自動化向けチェック（期限切れ/未設定で終了コード `1`、期限切れ間近で `2`）:

```bash
openclaw models status --check
```

ライブ認証プローブ:

```bash
openclaw models status --probe
```

注記:

- プローブ行は、認証プロファイル、環境認証情報、または `models.json` から来ることがあります。
- 明示的な `auth.order.<provider>` で保存済みプロファイルが省かれている場合、プローブは
  そのプロファイルを試す代わりに `excluded_by_auth_order` を報告します。
- 認証が存在していても、そのプロバイダー向けにプローブ可能なモデル候補をOpenClawが解決できない場合、
  プローブは `status: no_model` を報告します。
- レート制限のクールダウンはモデル単位である場合があります。ある
  モデルでクールダウン中のプロファイルでも、同じプロバイダー上の別のモデルでは使用可能なことがあります。

任意の運用スクリプト（systemd/Termux）については、ここで説明しています:
[Auth monitoring scripts](/ja-JP/help/scripts#auth-monitoring-scripts)

## Anthropicに関する注記

Anthropicの `claude-cli` バックエンドは再びサポートされています。

- Anthropicの担当者は、このOpenClaw統合経路は再び許可されていると案内しました。
- そのためOpenClawは、Anthropicが新しいポリシーを公開しない限り、
  Anthropicベースの実行におけるClaude CLIの再利用と `claude -p` の使用を認可済みとして扱います。
- Anthropic APIキーは、長時間稼働するGateway
  ホストと、明示的なサーバー側課金制御において、依然として最も予測しやすい選択肢です。

## モデル認証ステータスの確認

```bash
openclaw models status
openclaw doctor
```

## APIキーのローテーション動作（Gateway）

一部のプロバイダーは、API呼び出しがプロバイダーのレート制限に達した場合に、
別のキーでリクエストを再試行することをサポートしています。

- 優先順位:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（単一のオーバーライド）
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Googleプロバイダーでは、追加のフォールバックとして `GOOGLE_API_KEY` も含まれます。
- 同じキー一覧は使用前に重複排除されます。
- OpenClawは、レート制限エラーの場合にのみ次のキーで再試行します（たとえば
  `429`、`rate_limit`、`quota`、`resource exhausted`、`Too many concurrent
requests`、`ThrottlingException`、`concurrency limit reached`、または
  `workers_ai ... quota limit exceeded`）。
- レート制限以外のエラーでは、代替キーで再試行しません。
- すべてのキーが失敗した場合は、最後の試行での最終エラーが返されます。

## 使用する認証情報の制御

### セッションごと（チャットコマンド）

現在のセッションで特定のプロバイダー認証情報を固定するには、`/model <alias-or-id>@<profileId>` を使用します（プロファイルIDの例: `anthropic:default`、`anthropic:work`）。

簡易ピッカーには `/model`（または `/model list`）を、完全表示には `/model status` を使用します（候補 + 次の認証プロファイル。設定されている場合はプロバイダーのエンドポイント詳細も表示）。

### エージェントごと（CLIオーバーライド）

エージェントに対する明示的な認証プロファイル順序のオーバーライドを設定します（そのエージェントの `auth-state.json` に保存されます）。

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

特定のエージェントを対象にするには `--agent <id>` を使用します。省略すると、設定されたデフォルトエージェントが使用されます。
順序の問題をデバッグするときは、`openclaw models status --probe` により、省かれた
保存済みプロファイルは黙ってスキップされるのではなく `excluded_by_auth_order` として表示されます。
クールダウンの問題をデバッグするときは、レート制限のクールダウンが
プロバイダープロファイル全体ではなく1つのモデルIDに結びついている可能性があることを覚えておいてください。

## トラブルシューティング

### 「認証情報が見つかりません」

Anthropicプロファイルがない場合は、
**Gatewayホスト**にAnthropic APIキーを設定するか、Anthropic setup-token経路を設定してから、再確認してください。

```bash
openclaw models status
```

### トークンの有効期限切れ/期限切れ間近

どのプロファイルの期限が近いかを確認するには `openclaw models status` を実行します。Anthropicの
トークンプロファイルが存在しない、または期限切れの場合は、
setup-tokenでその設定を更新するか、Anthropic APIキーへ移行してください。
