---
read_when:
    - '`openclaw onboard` の詳細な動作が必要です。'
    - オンボーディング結果をデバッグしている、またはオンボーディングクライアントを統合している。
sidebarTitle: CLI reference
summary: CLI のセットアップフロー、認証/モデル設定、出力、内部動作の完全リファレンス
title: CLI セットアップリファレンス
x-i18n:
    generated_at: "2026-04-15T14:41:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI セットアップリファレンス

このページは `openclaw onboard` の完全リファレンスです。
短いガイドについては、[オンボーディング (CLI)](/ja-JP/start/wizard) を参照してください。

## ウィザードの動作

ローカルモード（デフォルト）では、次の内容を順に設定します。

- モデルと認証のセットアップ（OpenAI Code subscription OAuth、Anthropic Claude CLI または API キー、さらに MiniMax、GLM、Ollama、Moonshot、StepFun、AI Gateway の各オプション）
- ワークスペースの場所とブートストラップファイル
- Gateway の設定（ポート、bind、auth、tailscale）
- チャンネルとプロバイダー（Telegram、WhatsApp、Discord、Google Chat、Mattermost、Signal、BlueBubbles、およびその他のバンドルされたチャンネル Plugin）
- デーモンのインストール（LaunchAgent、systemd ユーザーユニット、またはネイティブ Windows Scheduled Task。Startup フォルダへのフォールバックあり）
- ヘルスチェック
- Skills のセットアップ

リモートモードでは、このマシンが別の場所にある Gateway に接続するよう設定します。
リモートホストには何もインストールせず、変更も加えません。

## ローカルフローの詳細

<Steps>
  <Step title="既存設定の検出">
    - `~/.openclaw/openclaw.json` が存在する場合は、Keep、Modify、Reset を選択します。
    - ウィザードを再実行しても、明示的に Reset を選ばない限り（または `--reset` を渡さない限り）、何も消去されません。
    - CLI の `--reset` のデフォルトは `config+creds+sessions` です。ワークスペースも削除するには `--reset-scope full` を使います。
    - 設定が無効、またはレガシーキーを含んでいる場合、ウィザードは停止し、続行前に `openclaw doctor` を実行するよう求めます。
    - Reset では `trash` を使用し、次のスコープを選べます。
      - 設定のみ
      - 設定 + 認証情報 + セッション
      - 完全リセット（ワークスペースも削除）
  </Step>
  <Step title="モデルと認証">
    - 完全な選択肢マトリクスは [認証とモデルのオプション](#auth-and-model-options) にあります。
  </Step>
  <Step title="ワークスペース">
    - デフォルトは `~/.openclaw/workspace`（変更可能）。
    - 初回実行のブートストラップ手順に必要なワークスペースファイルを生成します。
    - ワークスペース構成: [Agent workspace](/ja-JP/concepts/agent-workspace)。
  </Step>
  <Step title="Gateway">
    - ポート、bind、auth モード、tailscale 公開について対話的に尋ねます。
    - 推奨: loopback のみでもトークン認証を有効にして、ローカル WS クライアントに認証を必須にします。
    - トークンモードでは、対話型セットアップで次を選べます。
      - **平文トークンを生成して保存**（デフォルト）
      - **SecretRef を使用**（オプトイン）
    - パスワードモードでも、対話型セットアップは平文または SecretRef 保存をサポートします。
    - 非対話型のトークン SecretRef パス: `--gateway-token-ref-env <ENV_VAR>`。
      - オンボーディング処理環境内に空でない環境変数が必要です。
      - `--gateway-token` と併用できません。
    - auth を無効にするのは、すべてのローカルプロセスを完全に信頼している場合だけにしてください。
    - loopback 以外への bind でも auth は必須です。
  </Step>
  <Step title="チャンネル">
    - [WhatsApp](/ja-JP/channels/whatsapp): 任意の QR ログイン
    - [Telegram](/ja-JP/channels/telegram): bot token
    - [Discord](/ja-JP/channels/discord): bot token
    - [Google Chat](/ja-JP/channels/googlechat): サービスアカウント JSON + webhook audience
    - [Mattermost](/ja-JP/channels/mattermost): bot token + base URL
    - [Signal](/ja-JP/channels/signal): 任意の `signal-cli` インストール + アカウント設定
    - [BlueBubbles](/ja-JP/channels/bluebubbles): iMessage に推奨。server URL + password + webhook
    - [iMessage](/ja-JP/channels/imessage): レガシー `imsg` CLI パス + DB アクセス
    - DM セキュリティ: デフォルトはペアリングです。最初の DM でコードが送られます。`openclaw pairing approve <channel> <code>` で承認するか、許可リストを使用します。
  </Step>
  <Step title="デーモンのインストール">
    - macOS: LaunchAgent
      - ログイン済みユーザーセッションが必要です。ヘッドレス環境ではカスタム LaunchDaemon を使用してください（同梱されていません）。
    - Linux と WSL2 経由の Windows: systemd ユーザーユニット
      - ウィザードは、ログアウト後も gateway が動作し続けるよう `loginctl enable-linger <user>` を試みます。
      - sudo を求められる場合があります（`/var/lib/systemd/linger` に書き込みます）。まず sudo なしで試行します。
    - ネイティブ Windows: まず Scheduled Task
      - タスク作成が拒否された場合、OpenClaw はユーザーごとの Startup フォルダのログイン項目にフォールバックし、すぐに gateway を起動します。
      - Scheduled Task のほうが supervisor 状態をより適切に提供できるため、引き続き推奨されます。
    - ランタイム選択: Node（推奨。WhatsApp と Telegram には必須）。Bun は推奨されません。
  </Step>
  <Step title="ヘルスチェック">
    - 必要に応じて gateway を起動し、`openclaw health` を実行します。
    - `openclaw status --deep` は、サポートされている場合にチャンネル probe を含むライブ gateway ヘルス probe をステータス出力に追加します。
  </Step>
  <Step title="Skills">
    - 利用可能な Skills を読み取り、要件を確認します。
    - Node マネージャーとして npm、pnpm、bun を選べます。
    - 任意の依存関係をインストールします（一部は macOS で Homebrew を使用します）。
  </Step>
  <Step title="完了">
    - iOS、Android、macOS アプリのオプションを含む要約と次の手順を表示します。
  </Step>
</Steps>

<Note>
GUI が検出されない場合、ウィザードはブラウザを開く代わりに、Control UI 用の SSH ポートフォワード手順を表示します。
Control UI アセットが不足している場合、ウィザードはそれらのビルドを試みます。フォールバックは `pnpm ui:build` です（UI 依存関係を自動インストールします）。
</Note>

## リモートモードの詳細

リモートモードでは、このマシンが別の場所にある Gateway に接続するよう設定します。

<Info>
リモートモードはリモートホストに何もインストールせず、変更も加えません。
</Info>

設定するもの:

- リモート Gateway URL（`ws://...`）
- リモート Gateway の auth が必要な場合のトークン（推奨）

<Note>
- gateway が loopback のみの場合は、SSH トンネルまたは tailnet を使用してください。
- 検出のヒント:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## 認証とモデルのオプション

<AccordionGroup>
  <Accordion title="Anthropic API キー">
    `ANTHROPIC_API_KEY` が存在すればそれを使用し、なければキーの入力を求め、その後デーモンで使えるよう保存します。
  </Accordion>
  <Accordion title="OpenAI Code subscription（Codex CLI の再利用）">
    `~/.codex/auth.json` が存在する場合、ウィザードはそれを再利用できます。
    再利用された Codex CLI 認証情報は引き続き Codex CLI によって管理されます。期限切れ時には、OpenClaw はまずその保存元を再読み込みし、プロバイダー側で更新できる場合は、その更新後の認証情報を自分で管理するのではなく Codex ストレージへ書き戻します。
  </Accordion>
  <Accordion title="OpenAI Code subscription（OAuth）">
    ブラウザフローです。`code#state` を貼り付けます。

    モデルが未設定、または `openai/*` の場合、`agents.defaults.model` を `openai-codex/gpt-5.4` に設定します。

  </Accordion>
  <Accordion title="OpenAI API キー">
    `OPENAI_API_KEY` が存在すればそれを使用し、なければキーの入力を求め、その後認証プロファイルに認証情報を保存します。

    モデルが未設定、`openai/*`、または `openai-codex/*` の場合、`agents.defaults.model` を `openai/gpt-5.4` に設定します。

  </Accordion>
  <Accordion title="xAI（Grok）API キー">
    `XAI_API_KEY` の入力を求め、xAI をモデルプロバイダーとして設定します。
  </Accordion>
  <Accordion title="OpenCode">
    `OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）の入力を求め、Zen または Go カタログを選択できます。
    セットアップ URL: [opencode.ai/auth](https://opencode.ai/auth)。
  </Accordion>
  <Accordion title="API キー（汎用）">
    キーを保存します。
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    `AI_GATEWAY_API_KEY` の入力を求めます。
    詳細: [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)。
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    account ID、gateway ID、`CLOUDFLARE_AI_GATEWAY_API_KEY` の入力を求めます。
    詳細: [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)。
  </Accordion>
  <Accordion title="MiniMax">
    設定は自動で書き込まれます。ホスト版のデフォルトは `MiniMax-M2.7` です。API キーのセットアップでは `minimax/...` を使用し、OAuth のセットアップでは `minimax-portal/...` を使用します。
    詳細: [MiniMax](/ja-JP/providers/minimax)。
  </Accordion>
  <Accordion title="StepFun">
    China または global エンドポイント上の StepFun standard または Step Plan 用に、設定が自動で書き込まれます。
    現在、Standard には `step-3.5-flash` が含まれ、Step Plan には `step-3.5-flash-2603` も含まれます。
    詳細: [StepFun](/ja-JP/providers/stepfun)。
  </Accordion>
  <Accordion title="Synthetic（Anthropic 互換）">
    `SYNTHETIC_API_KEY` の入力を求めます。
    詳細: [Synthetic](/ja-JP/providers/synthetic)。
  </Accordion>
  <Accordion title="Ollama（Cloud とローカルのオープンモデル）">
    まず `Cloud + Local`、`Cloud only`、`Local only` を尋ねます。
    `Cloud only` は `OLLAMA_API_KEY` と `https://ollama.com` を使用します。
    ホスト連携モードでは、base URL（デフォルトは `http://127.0.0.1:11434`）の入力を求め、利用可能なモデルを検出し、デフォルト候補を提案します。
    `Cloud + Local` では、その Ollama ホストが cloud アクセス用にサインイン済みかどうかも確認します。
    詳細: [Ollama](/ja-JP/providers/ollama)。
  </Accordion>
  <Accordion title="Moonshot と Kimi Coding">
    Moonshot（Kimi K2）および Kimi Coding の設定は自動で書き込まれます。
    詳細: [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)。
  </Accordion>
  <Accordion title="カスタムプロバイダー">
    OpenAI 互換および Anthropic 互換エンドポイントで動作します。

    対話型オンボーディングは、他のプロバイダー API キーフローと同じ API キー保存オプションをサポートします。
    - **今すぐ API キーを貼り付ける**（平文）
    - **シークレット参照を使用**（env ref または設定済み provider ref。事前検証あり）

    非対話型フラグ:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key`（任意。未指定時は `CUSTOM_API_KEY` を使用）
    - `--custom-provider-id`（任意）
    - `--custom-compatibility <openai|anthropic>`（任意。デフォルトは `openai`）

  </Accordion>
  <Accordion title="スキップ">
    auth を未設定のままにします。
  </Accordion>
</AccordionGroup>

モデルの動作:

- 検出された選択肢からデフォルトモデルを選ぶか、プロバイダーとモデルを手動で入力します。
- オンボーディングがプロバイダー認証の選択から始まる場合、モデルピッカーはそのプロバイダーを自動的に優先します。Volcengine と BytePlus では、この優先設定はそれぞれの coding-plan バリアント（`volcengine-plan/*`、`byteplus-plan/*`）にも一致します。
- その優先プロバイダーフィルターが空になる場合、モデルが何も表示されないのを避けるため、ピッカーは完全なカタログにフォールバックします。
- ウィザードはモデルチェックを実行し、設定されたモデルが未知であるか、auth が不足している場合に警告します。

認証情報とプロファイルのパス:

- 認証プロファイル（API キー + OAuth）: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- レガシー OAuth のインポート: `~/.openclaw/credentials/oauth.json`

認証情報の保存モード:

- デフォルトのオンボーディング動作では、API キーは平文値として認証プロファイルに保存されます。
- `--secret-input-mode ref` を指定すると、平文キー保存の代わりに参照モードが有効になります。
  対話型セットアップでは、次のいずれかを選べます。
  - 環境変数 ref（例: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）
  - 設定済み provider ref（`file` または `exec`）と provider alias + id
- 対話型の参照モードでは、保存前に高速な事前検証を実行します。
  - Env ref: 変数名と、現在のオンボーディング環境での空でない値を検証します。
  - Provider ref: provider 設定を検証し、要求された id を解決します。
  - 事前検証に失敗した場合、オンボーディングはエラーを表示し、再試行できます。
- 非対話型モードでは、`--secret-input-mode ref` は env ベースのみです。
  - オンボーディング処理環境で provider の環境変数を設定してください。
  - インラインのキーフラグ（例: `--openai-api-key`）では、その環境変数が設定されていないとオンボーディングは即座に失敗します。
  - カスタムプロバイダーでは、非対話型 `ref` モードは `models.providers.<id>.apiKey` を `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` として保存します。
  - そのカスタムプロバイダーのケースでは、`--custom-api-key` を使うには `CUSTOM_API_KEY` が設定されている必要があり、そうでない場合はオンボーディングは即座に失敗します。
- Gateway auth 認証情報は、対話型セットアップで平文と SecretRef の両方をサポートします。
  - トークンモード: **平文トークンを生成して保存**（デフォルト）または **SecretRef を使用**
  - パスワードモード: 平文または SecretRef
- 非対話型のトークン SecretRef パス: `--gateway-token-ref-env <ENV_VAR>`。
- 既存の平文セットアップは、そのまま引き続き動作します。

<Note>
ヘッドレス環境およびサーバー向けのヒント: ブラウザのあるマシンで OAuth を完了し、その agent の `auth-profiles.json`（たとえば `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`、または対応する `$OPENCLAW_STATE_DIR/...` パス）を gateway ホストへコピーしてください。`credentials/oauth.json` はレガシーなインポート元にすぎません。
</Note>

## 出力と内部動作

`~/.openclaw/openclaw.json` に含まれる典型的なフィールド:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（MiniMax を選択した場合）
- `tools.profile`（ローカルオンボーディングでは、未設定時のデフォルトとして `"coding"` を使用します。既存の明示的な値は保持されます）
- `gateway.*`（mode、bind、auth、tailscale）
- `session.dmScope`（ローカルオンボーディングでは、未設定時のデフォルトとして `per-channel-peer` を使用します。既存の明示的な値は保持されます）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.matrix.*`、`channels.signal.*`、`channels.imessage.*`
- プロンプト中にオプトインした場合のチャンネル許可リスト（Slack、Discord、Matrix、Microsoft Teams）（可能な場合は名前が ID に解決されます）
- `skills.install.nodeManager`
  - `setup --node-manager` フラグは `npm`、`pnpm`、`bun` を受け付けます。
  - 手動設定では、後から `skills.install.nodeManager: "yarn"` を設定することもできます。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` は `agents.list[]` と、必要に応じて `bindings` を書き込みます。

WhatsApp の認証情報は `~/.openclaw/credentials/whatsapp/<accountId>/` 配下に保存されます。
セッションは `~/.openclaw/agents/<agentId>/sessions/` 配下に保存されます。

<Note>
一部のチャンネルは Plugin として提供されます。セットアップ中にそれらを選択すると、ウィザードはチャンネル設定の前に Plugin のインストール（npm またはローカルパス）を促します。
</Note>

Gateway ウィザード RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

クライアント（macOS アプリおよび Control UI）は、オンボーディングロジックを再実装せずにステップを描画できます。

Signal のセットアップ動作:

- 適切なリリースアセットをダウンロードします
- それを `~/.openclaw/tools/signal-cli/<version>/` 配下に保存します
- 設定に `channels.signal.cliPath` を書き込みます
- JVM ビルドには Java 21 が必要です
- 利用可能な場合はネイティブビルドが使われます
- Windows は WSL2 を使用し、WSL 内で Linux の signal-cli フローに従います

## 関連ドキュメント

- オンボーディングハブ: [オンボーディング (CLI)](/ja-JP/start/wizard)
- 自動化とスクリプト: [CLI 自動化](/ja-JP/start/wizard-cli-automation)
- コマンドリファレンス: [`openclaw onboard`](/cli/onboard)
