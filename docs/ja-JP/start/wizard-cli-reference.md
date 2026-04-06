---
read_when:
    - openclaw onboard の詳細な動作が必要な場合
    - オンボーディング結果をデバッグしている、またはオンボーディングクライアントを統合している場合
sidebarTitle: CLI reference
summary: CLI セットアップフロー、auth/model 設定、出力、内部動作の完全リファレンス
title: CLI セットアップリファレンス
x-i18n:
    generated_at: "2026-04-06T03:13:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 92f379b34a2b48c68335dae4f759117c770f018ec51b275f4f40421c6b3abb23
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI セットアップリファレンス

このページは `openclaw onboard` の完全なリファレンスです。
短いガイドについては、[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

## ウィザードが行うこと

ローカルモード（デフォルト）では、次の内容を順に設定します。

- Model と auth のセットアップ（OpenAI Code subscription OAuth、Anthropic Claude CLI または API key、さらに MiniMax、GLM、Ollama、Moonshot、StepFun、AI Gateway オプション）
- workspace の場所と bootstrap ファイル
- Gateway 設定（port、bind、auth、Tailscale）
- チャネルと provider（Telegram、WhatsApp、Discord、Google Chat、Mattermost、Signal、BlueBubbles、その他の bundled channel plugins）
- daemon インストール（LaunchAgent、systemd user unit、または native Windows Scheduled Task。Startup-folder fallback あり）
- ヘルスチェック
- Skills のセットアップ

リモートモードでは、このマシンを別の場所にある gateway に接続するよう設定します。
リモートホストには何もインストールせず、変更も加えません。

## ローカルフローの詳細

<Steps>
  <Step title="既存設定の検出">
    - `~/.openclaw/openclaw.json` が存在する場合、Keep、Modify、Reset を選択します。
    - ウィザードを再実行しても、明示的に Reset を選ばない限り（または `--reset` を渡さない限り）何も消去されません。
    - CLI の `--reset` はデフォルトで `config+creds+sessions` を対象にします。workspace も削除するには `--reset-scope full` を使用してください。
    - 設定が無効、または legacy key を含む場合、ウィザードは停止し、続行前に `openclaw doctor` を実行するよう求めます。
    - Reset は `trash` を使用し、次のスコープを提示します:
      - 設定のみ
      - 設定 + 認証情報 + sessions
      - フルリセット（workspace も削除）
  </Step>
  <Step title="Model と auth">
    - 完全なオプション一覧は [Auth and model options](#auth-and-model-options) にあります。
  </Step>
  <Step title="Workspace">
    - デフォルトは `~/.openclaw/workspace`（変更可能）。
    - 初回実行の bootstrap ritual に必要な workspace ファイルを seed します。
    - workspace レイアウト: [Agent workspace](/ja-JP/concepts/agent-workspace)。
  </Step>
  <Step title="Gateway">
    - port、bind、auth mode、Tailscale 公開について質問します。
    - 推奨: loopback だけでも token auth を有効のままにして、ローカル WS クライアントにも認証を必須にしてください。
    - token mode では、対話型セットアップで次を提供します:
      - **平文 token を生成して保存**（デフォルト）
      - **SecretRef を使用**（オプトイン）
    - password mode でも、対話型セットアップは平文または SecretRef 保存をサポートします。
    - 非対話型の token SecretRef パス: `--gateway-token-ref-env <ENV_VAR>`。
      - オンボーディングを実行するプロセス環境内に、空でない env var が必要です。
      - `--gateway-token` とは併用できません。
    - すべてのローカルプロセスを完全に信頼している場合にのみ auth を無効にしてください。
    - 非 loopback bind では引き続き auth が必要です。
  </Step>
  <Step title="チャネル">
    - [WhatsApp](/ja-JP/channels/whatsapp): オプションの QR ログイン
    - [Telegram](/ja-JP/channels/telegram): bot token
    - [Discord](/ja-JP/channels/discord): bot token
    - [Google Chat](/ja-JP/channels/googlechat): service account JSON + webhook audience
    - [Mattermost](/ja-JP/channels/mattermost): bot token + base URL
    - [Signal](/ja-JP/channels/signal): オプションの `signal-cli` インストール + account 設定
    - [BlueBubbles](/ja-JP/channels/bluebubbles): iMessage 向け推奨。server URL + password + webhook
    - [iMessage](/ja-JP/channels/imessage): legacy `imsg` CLI path + DB access
    - DM セキュリティ: デフォルトは pairing です。最初の DM はコードを送信します。`openclaw pairing approve <channel> <code>` で承認するか、allowlist を使用してください。
  </Step>
  <Step title="Daemon インストール">
    - macOS: LaunchAgent
      - ログイン済みユーザーセッションが必要です。headless の場合はカスタム LaunchDaemon を使用してください（同梱されていません）。
    - Linux と Windows（WSL2 経由）: systemd user unit
      - gateway がログアウト後も動作し続けるよう、ウィザードは `loginctl enable-linger <user>` を試みます。
      - sudo を要求する場合があります（`/var/lib/systemd/linger` に書き込み）。まず sudo なしで試行します。
    - ネイティブ Windows: まず Scheduled Task
      - タスク作成が拒否された場合、OpenClaw はユーザーごとの Startup-folder ログイン項目にフォールバックし、gateway を即座に開始します。
      - より良い supervisor status を提供するため、Scheduled Task が引き続き推奨されます。
    - Runtime 選択: Node（推奨。WhatsApp と Telegram に必要）。Bun は推奨されません。
  </Step>
  <Step title="ヘルスチェック">
    - 必要に応じて gateway を起動し、`openclaw health` を実行します。
    - `openclaw status --deep` は status 出力に live gateway health probe を追加し、サポートされている場合は channel probe も含みます。
  </Step>
  <Step title="Skills">
    - 利用可能な Skills を読み取り、要件を確認します。
    - node manager として npm、pnpm、bun から選択できます。
    - オプション依存関係をインストールします（macOS では Homebrew を使うものもあります）。
  </Step>
  <Step title="完了">
    - iOS、Android、macOS アプリのオプションを含むサマリーと次の手順を表示します。
  </Step>
</Steps>

<Note>
GUI が検出されない場合、ウィザードはブラウザーを開く代わりに、Control UI 用の SSH port-forward 手順を表示します。
Control UI アセットが存在しない場合、ウィザードはそれらのビルドを試みます。フォールバックは `pnpm ui:build` です（UI 依存関係を自動インストールします）。
</Note>

## リモートモードの詳細

リモートモードでは、このマシンを別の場所にある gateway に接続するよう設定します。

<Info>
リモートモードは、リモートホストに何もインストールせず、変更も加えません。
</Info>

設定する内容:

- リモート gateway URL（`ws://...`）
- リモート gateway auth が必要な場合の token（推奨）

<Note>
- gateway が loopback-only の場合は、SSH トンネルまたは tailnet を使用してください。
- Discovery のヒント:
  - macOS: Bonjour（`dns-sd`）
  - Linux: Avahi（`avahi-browse`）
</Note>

## Auth と model のオプション

<AccordionGroup>
  <Accordion title="Anthropic API key">
    `ANTHROPIC_API_KEY` が存在すればそれを使用し、なければ key の入力を求め、daemon 用に保存します。
  </Accordion>
  <Accordion title="OpenAI Code subscription（Codex CLI 再利用）">
    `~/.codex/auth.json` が存在する場合、ウィザードはそれを再利用できます。
    再利用された Codex CLI 認証情報は引き続き Codex CLI によって管理されます。期限切れ時には OpenClaw はまずそのソースを再読込し、provider 側で refresh 可能な場合は、自身で所有権を持つ代わりに更新済み認証情報を Codex ストレージへ書き戻します。
  </Accordion>
  <Accordion title="OpenAI Code subscription（OAuth）">
    ブラウザーフローです。`code#state` を貼り付けます。

    model が未設定、または `openai/*` の場合、`agents.defaults.model` を `openai-codex/gpt-5.4` に設定します。

  </Accordion>
  <Accordion title="OpenAI API key">
    `OPENAI_API_KEY` が存在すればそれを使用し、なければ key の入力を求め、認証情報を auth profile に保存します。

    model が未設定、`openai/*`、または `openai-codex/*` の場合、`agents.defaults.model` を `openai/gpt-5.4` に設定します。

  </Accordion>
  <Accordion title="xAI（Grok）API key">
    `XAI_API_KEY` の入力を求め、xAI を model provider として設定します。
  </Accordion>
  <Accordion title="OpenCode">
    `OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）の入力を求め、Zen catalog と Go catalog を選択できます。
    セットアップ URL: [opencode.ai/auth](https://opencode.ai/auth)。
  </Accordion>
  <Accordion title="API key（汎用）">
    key を保存します。
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
    設定は自動で書き込まれます。hosted default は `MiniMax-M2.7` です。API-key セットアップでは `minimax/...`、OAuth セットアップでは `minimax-portal/...` を使用します。
    詳細: [MiniMax](/ja-JP/providers/minimax)。
  </Accordion>
  <Accordion title="StepFun">
    China または global endpoint 上の StepFun standard または Step Plan 用の設定が自動で書き込まれます。
    Standard には現在 `step-3.5-flash` が含まれ、Step Plan には `step-3.5-flash-2603` も含まれます。
    詳細: [StepFun](/ja-JP/providers/stepfun)。
  </Accordion>
  <Accordion title="Synthetic（Anthropic-compatible）">
    `SYNTHETIC_API_KEY` の入力を求めます。
    詳細: [Synthetic](/ja-JP/providers/synthetic)。
  </Accordion>
  <Accordion title="Ollama（Cloud とローカルの open model）">
    base URL（デフォルト `http://127.0.0.1:11434`）の入力を求め、その後 Cloud + Local または Local mode を選択できます。
    利用可能な model を discovery し、デフォルト候補を提示します。
    詳細: [Ollama](/ja-JP/providers/ollama)。
  </Accordion>
  <Accordion title="Moonshot と Kimi Coding">
    Moonshot（Kimi K2）と Kimi Coding の設定は自動で書き込まれます。
    詳細: [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)。
  </Accordion>
  <Accordion title="カスタム provider">
    OpenAI-compatible および Anthropic-compatible endpoint で動作します。

    対話型オンボーディングは、他の provider API key フローと同じ API key 保存オプションをサポートします:
    - **今すぐ API key を貼り付ける**（平文）
    - **secret reference を使う**（env ref または設定済み provider ref。事前検証あり）

    非対話型フラグ:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key`（オプション。`CUSTOM_API_KEY` にフォールバック）
    - `--custom-provider-id`（オプション）
    - `--custom-compatibility <openai|anthropic>`（オプション。デフォルトは `openai`）

  </Accordion>
  <Accordion title="スキップ">
    auth を未設定のままにします。
  </Accordion>
</AccordionGroup>

Model の動作:

- 検出されたオプションからデフォルト model を選ぶか、provider と model を手動入力します。
- オンボーディングが provider auth 選択から始まる場合、model picker はその provider を自動的に優先します。Volcengine と BytePlus では、この優先設定はそれぞれの coding-plan variant（`volcengine-plan/*`、`byteplus-plan/*`）にも一致します。
- その preferred-provider filter が空になる場合、model picker は model が表示されない状態にする代わりに、完全な catalog にフォールバックします。
- ウィザードは model check を実行し、設定された model が不明、または auth が不足している場合は警告します。

認証情報と profile のパス:

- Auth profile（API keys + OAuth）: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 旧 OAuth import: `~/.openclaw/credentials/oauth.json`

認証情報の保存モード:

- デフォルトのオンボーディング動作では、API key は auth profile 内に平文値として保存されます。
- `--secret-input-mode ref` は、平文 key 保存の代わりに reference mode を有効にします。
  対話型セットアップでは、次のいずれかを選べます:
  - 環境変数 ref（例: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）
  - 設定済み provider ref（`file` または `exec`）で、provider alias + id を使用
- 対話型 reference mode は、保存前に高速な事前検証を実行します。
  - Env ref: 変数名と、現在のオンボーディング環境内での空でない値を検証します。
  - Provider ref: provider 設定を検証し、要求された id を解決します。
  - 事前検証に失敗した場合、オンボーディングはエラーを表示し、再試行できます。
- 非対話型 mode では、`--secret-input-mode ref` は env ベースのみです。
  - provider env var をオンボーディングプロセス環境に設定してください。
  - インライン key フラグ（例: `--openai-api-key`）は、その env var が設定されていることを要求します。そうでない場合、オンボーディングは即座に失敗します。
  - カスタム provider では、非対話型 `ref` mode は `models.providers.<id>.apiKey` を `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` として保存します。
  - そのカスタム provider の場合、`--custom-api-key` では `CUSTOM_API_KEY` の設定が必要です。そうでない場合、オンボーディングは即座に失敗します。
- Gateway auth 認証情報は、対話型セットアップで平文と SecretRef の両方をサポートします:
  - Token mode: **平文 token を生成して保存**（デフォルト）または **SecretRef を使用**。
  - Password mode: 平文または SecretRef。
- 非対話型の token SecretRef パス: `--gateway-token-ref-env <ENV_VAR>`。
- 既存の平文セットアップは、そのまま変更なしで動作し続けます。

<Note>
headless および server のヒント: ブラウザーのあるマシンで OAuth を完了し、その agent の `auth-profiles.json`（たとえば `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`、または対応する `$OPENCLAW_STATE_DIR/...` パス）を gateway host にコピーしてください。`credentials/oauth.json` は legacy import source にすぎません。
</Note>

## 出力と内部動作

`~/.openclaw/openclaw.json` によく書き込まれるフィールド:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（Minimax を選んだ場合）
- `tools.profile`（ローカルオンボーディングでは、未設定時のデフォルトとして `"coding"` を設定します。既存の明示値は保持されます）
- `gateway.*`（mode、bind、auth、Tailscale）
- `session.dmScope`（ローカルオンボーディングでは、未設定時のデフォルトとして `per-channel-peer` を設定します。既存の明示値は保持されます）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.matrix.*`、`channels.signal.*`、`channels.imessage.*`
- プロンプト中にオプトインした場合の channel allowlist（Slack、Discord、Matrix、Microsoft Teams）（可能な場合は名前を ID に解決）
- `skills.install.nodeManager`
  - `setup --node-manager` フラグは `npm`、`pnpm`、`bun` を受け付けます。
  - 後で手動設定により `skills.install.nodeManager: "yarn"` を設定することも可能です。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` は `agents.list[]` とオプションの `bindings` を書き込みます。

WhatsApp 認証情報は `~/.openclaw/credentials/whatsapp/<accountId>/` に保存されます。
Sessions は `~/.openclaw/agents/<agentId>/sessions/` に保存されます。

<Note>
一部のチャネルは plugin として提供されます。セットアップ中に選択すると、ウィザードはチャネル設定の前に plugin のインストール（npm またはローカルパス）を求めます。
</Note>

Gateway ウィザード RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

クライアント（macOS アプリと Control UI）は、オンボーディングロジックを再実装せずにステップを描画できます。

Signal セットアップの動作:

- 適切な release asset をダウンロードする
- `~/.openclaw/tools/signal-cli/<version>/` に保存する
- config に `channels.signal.cliPath` を書き込む
- JVM ビルドには Java 21 が必要
- 利用可能な場合は native ビルドを使用
- Windows は WSL2 を使用し、WSL 内で Linux の signal-cli フローに従う

## 関連ドキュメント

- オンボーディングハブ: [Onboarding (CLI)](/ja-JP/start/wizard)
- 自動化とスクリプト: [CLI Automation](/ja-JP/start/wizard-cli-automation)
- コマンドリファレンス: [`openclaw onboard`](/cli/onboard)
