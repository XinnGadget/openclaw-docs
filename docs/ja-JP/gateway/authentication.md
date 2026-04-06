---
read_when:
    - モデル認証またはOAuthの期限切れをデバッグしている
    - 認証または認証情報ストレージを文書化している
summary: 'モデル認証: OAuth、APIキー、旧式のAnthropic setup-token'
title: 認証
x-i18n:
    generated_at: "2026-04-06T03:07:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: f59ede3fcd7e692ad4132287782a850526acf35474b5bfcea29e0e23610636c2
    source_path: gateway/authentication.md
    workflow: 15
---

# 認証（モデルプロバイダー）

<Note>
このページでは**モデルプロバイダー**認証（APIキー、OAuth、旧式のAnthropic setup-token）を扱います。**Gateway接続**認証（token、password、trusted-proxy）については、[Configuration](/ja-JP/gateway/configuration) と [Trusted Proxy Auth](/ja-JP/gateway/trusted-proxy-auth) を参照してください。
</Note>

OpenClaw は、モデルプロバイダー向けにOAuthとAPIキーをサポートしています。常時稼働するGatewayホストでは、通常、APIキーが最も予測しやすい選択肢です。サブスクリプション/OAuthフローも、プロバイダーのアカウントモデルに合っていればサポートされます。

完全なOAuthフローとストレージ構成については [/concepts/oauth](/ja-JP/concepts/oauth) を参照してください。
SecretRefベースの認証（`env`/`file`/`exec` プロバイダー）については、[Secrets Management](/ja-JP/gateway/secrets) を参照してください。
`models status --probe` で使われる認証情報の適格性/理由コードのルールについては、
[Auth Credential Semantics](/ja-JP/auth-credential-semantics) を参照してください。

## 推奨セットアップ（APIキー、任意のプロバイダー）

長期間稼働するGatewayを実行している場合は、選択したプロバイダーのAPIキーから始めてください。
Anthropicについては特に、APIキー認証が安全な経路です。OpenClaw内でのAnthropicのサブスクリプション型認証は旧式のsetup-token経路であり、プラン上限の経路ではなく、**Extra Usage** 経路として扱う必要があります。

1. プロバイダーのコンソールでAPIキーを作成します。
2. それを**Gatewayホスト**（`openclaw gateway` を実行しているマシン）に配置します。

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Gatewayがsystemd/launchd配下で動作している場合は、デーモンが読み取れるよう、キーを `~/.openclaw/.env` に置くことを推奨します。

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

その後、デーモンを再起動するか（またはGatewayプロセスを再起動し）、再確認します。

```bash
openclaw models status
openclaw doctor
```

環境変数を自分で管理したくない場合は、オンボーディングで
デーモン利用向けのAPIキーを保存できます: `openclaw onboard`。

環境の継承（`env.shellEnv`、`~/.openclaw/.env`、systemd/launchd）の詳細は [Help](/ja-JP/help) を参照してください。

## Anthropic: 旧式トークン互換性

Anthropic setup-token認証は、OpenClaw では依然として
旧式/手動の経路として利用可能です。Anthropic の公開Claude Codeドキュメントでは、Claudeプラン配下でのClaude Codeターミナルの直接利用が引き続き説明されていますが、Anthropic は別途 OpenClaw ユーザーに対し、**OpenClaw** のClaudeログイン経路はサードパーティハーネス利用として扱われ、サブスクリプションとは別料金の **Extra Usage** が必要だと伝えています。

最も明確なセットアップ経路としては、Anthropic APIキーを使用してください。どうしても OpenClaw でサブスクリプション型のAnthropic経路を維持する必要がある場合は、Anthropic がそれを **Extra Usage** として扱う前提で、旧式のsetup-token経路を使用してください。

手動トークン入力（任意のプロバイダー。`auth-profiles.json` に書き込み、設定を更新）:

```bash
openclaw models auth paste-token --provider openrouter
```

静的認証情報では認証プロファイル参照もサポートされます。

- `api_key` 認証情報は `keyRef: { source, provider, id }` を使用できます
- `token` 認証情報は `tokenRef: { source, provider, id }` を使用できます
- OAuthモードのプロファイルは SecretRef 認証情報をサポートしません。`auth.profiles.<id>.mode` が `"oauth"` に設定されている場合、そのプロファイルに対する SecretRef ベースの `keyRef`/`tokenRef` 入力は拒否されます。

自動化向けチェック（期限切れ/未設定で終了コード `1`、期限が近い場合は `2`）:

```bash
openclaw models status --check
```

ライブ認証プローブ:

```bash
openclaw models status --probe
```

注意:

- プローブ行は、認証プロファイル、環境認証情報、または `models.json` のいずれかから来ることがあります。
- 明示的な `auth.order.<provider>` に保存済みプロファイルが含まれていない場合、
  プローブはそのプロファイルを試すのではなく
  `excluded_by_auth_order` として報告します。
- 認証が存在しても、OpenClaw がそのプロバイダー用のプローブ可能なモデル候補を解決できない場合、
  プローブは `status: no_model` を報告します。
- レート制限クールダウンはモデル単位になることがあります。あるモデルでクールダウン中の
  プロファイルでも、同じプロバイダー上の別の兄弟モデルでは利用可能な場合があります。

オプションの運用スクリプト（systemd/Termux）については、こちらに記載されています:
[Auth monitoring scripts](/ja-JP/help/scripts#auth-monitoring-scripts)

## Anthropic に関する注意

Anthropic の `claude-cli` バックエンドは削除されました。

- OpenClaw でのAnthropicトラフィックにはAnthropic APIキーを使用してください。
- Anthropic setup-token は旧式/手動の経路として残っていますが、
  Anthropic が OpenClaw ユーザーに伝えた Extra Usage 課金の前提で使用する必要があります。
- `openclaw doctor` は、古くなって削除されたAnthropic Claude CLI状態を検出するようになりました。
  保存された認証情報バイト列がまだ存在する場合、doctor はそれらを
  Anthropic token/OAuthプロファイルに変換して戻します。存在しない場合は、doctor は古いClaude CLI
  設定を削除し、APIキーまたはsetup-tokenによる復旧を案内します。

## モデル認証ステータスの確認

```bash
openclaw models status
openclaw doctor
```

## APIキーのローテーション動作（Gateway）

一部のプロバイダーは、API呼び出しがプロバイダーのレート制限に
達したときに、別のキーでリクエストを再試行することをサポートしています。

- 優先順序:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（単一オーバーライド）
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Googleプロバイダーでは、追加のフォールバックとして `GOOGLE_API_KEY` も含まれます。
- 同じキー一覧は使用前に重複排除されます。
- OpenClaw は、レート制限エラーの場合にのみ次のキーで再試行します（たとえば
  `429`、`rate_limit`、`quota`、`resource exhausted`、`Too many concurrent
requests`、`ThrottlingException`、`concurrency limit reached`、または
  `workers_ai ... quota limit exceeded`）。
- レート制限以外のエラーでは、代替キーで再試行しません。
- すべてのキーが失敗した場合、最後の試行で発生した最終エラーが返されます。

## 使用する認証情報の制御

### セッション単位（チャットコマンド）

現在のセッションで特定のプロバイダー認証情報を固定するには、`/model <alias-or-id>@<profileId>` を使用します（プロファイルIDの例: `anthropic:default`、`anthropic:work`）。

コンパクトなピッカーには `/model`（または `/model list`）を、完全表示には `/model status` を使用します（候補 + 次の認証プロファイル、設定されている場合はプロバイダーのエンドポイント詳細も表示）。

### エージェント単位（CLIオーバーライド）

エージェントの明示的な認証プロファイル順序オーバーライドを設定します（そのエージェントの `auth-profiles.json` に保存されます）。

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

特定のエージェントを対象にするには `--agent <id>` を使用し、設定済みのデフォルトエージェントを使う場合は省略します。
順序の問題をデバッグするときは、`openclaw models status --probe` が省略された
保存済みプロファイルを黙ってスキップするのではなく `excluded_by_auth_order` として表示します。
クールダウンの問題をデバッグするときは、レート制限クールダウンが
プロバイダープロファイル全体ではなく、1つのモデルIDに結び付くことがある点を覚えておいてください。

## トラブルシューティング

### 「認証情報が見つかりません」

Anthropicプロファイルがない場合は、
**Gatewayホスト** 上でAnthropic APIキーを設定するか、旧式のAnthropic setup-token経路を設定してから、再確認してください。

```bash
openclaw models status
```

### トークンの期限切れが近い/期限切れ

どのプロファイルの期限が近いかを確認するには `openclaw models status` を実行します。旧式の
Anthropicトークンプロファイルがない、または期限切れの場合は、
setup-token でその設定を更新するか、Anthropic APIキーへ移行してください。

マシンに、古いビルドからの削除済みAnthropic Claude CLI状態がまだ残っている場合は、次を実行します。

```bash
openclaw doctor --yes
```

保存された認証情報バイト列がまだ存在する場合、Doctor は `anthropic:claude-cli` を Anthropic token/OAuth に戻して変換します。
存在しない場合は、古いClaude CLIプロファイル/設定/モデル参照を削除し、次の手順の案内を残します。
