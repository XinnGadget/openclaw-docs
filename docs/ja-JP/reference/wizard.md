---
read_when:
    - 特定のオンボーディング手順やフラグを調べている
    - 非対話モードでオンボーディングを自動化している
    - オンボーディングの動作をデバッグしている
sidebarTitle: Onboarding Reference
summary: 'CLIオンボーディングの完全リファレンス: すべての手順、フラグ、設定フィールド'
title: オンボーディングリファレンス
x-i18n:
    generated_at: "2026-04-06T03:13:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: e02a4da4a39ba335199095723f5d3b423671eb12efc2d9e4f9e48c1e8ee18419
    source_path: reference/wizard.md
    workflow: 15
---

# オンボーディングリファレンス

これは `openclaw onboard` の完全リファレンスです。
概要については、[Onboarding (CLI)](/ja-JP/start/wizard) を参照してください。

## フロー詳細（ローカルモード）

<Steps>
  <Step title="既存設定の検出">
    - `~/.openclaw/openclaw.json` が存在する場合、**Keep / Modify / Reset** を選択します。
    - オンボーディングを再実行しても、明示的に **Reset** を選ばない限り
      （または `--reset` を渡さない限り）、何も消去されません。
    - CLI の `--reset` はデフォルトで `config+creds+sessions` です。ワークスペースも
      削除するには `--reset-scope full` を使用します。
    - 設定が無効であるか、旧式キーを含んでいる場合、ウィザードは停止し、
      続行前に `openclaw doctor` を実行するよう求めます。
    - リセットには `trash` を使用し（`rm` は決して使いません）、次のスコープがあります:
      - 設定のみ
      - 設定 + 認証情報 + セッション
      - フルリセット（ワークスペースも削除）
  </Step>
  <Step title="モデル/認証">
    - **Anthropic APIキー**: 存在する場合は `ANTHROPIC_API_KEY` を使用し、なければキーの入力を求め、その後デーモン用に保存します。
    - **Anthropic APIキー**: オンボーディング/設定で推奨される Anthropic アシスタント選択肢です。
    - **Anthropic setup-token（旧式/手動）**: オンボーディング/設定で再び利用可能ですが、Anthropic は OpenClaw ユーザーに対し、OpenClaw の Claude-login 経路はサードパーティハーネス利用に当たり、Claude アカウントで **Extra Usage** が必要だと伝えています。
    - **OpenAI Code (Codex) subscription (Codex CLI)**: `~/.codex/auth.json` が存在する場合、オンボーディングはそれを再利用できます。再利用された Codex CLI 認証情報は引き続き Codex CLI によって管理されます。有効期限切れ時には OpenClaw はまずそのソースを再読み込みし、プロバイダーが更新可能であれば、認証情報を自ら所有するのではなく、更新された認証情報を Codex ストレージへ書き戻します。
    - **OpenAI Code (Codex) subscription (OAuth)**: ブラウザーフロー。`code#state` を貼り付けます。
      - モデルが未設定、または `openai/*` の場合、`agents.defaults.model` を `openai-codex/gpt-5.4` に設定します。
    - **OpenAI APIキー**: 存在する場合は `OPENAI_API_KEY` を使用し、なければキーの入力を求め、その後認証プロファイルに保存します。
      - モデルが未設定、`openai/*`、または `openai-codex/*` の場合、`agents.defaults.model` を `openai/gpt-5.4` に設定します。
    - **xAI (Grok) APIキー**: `XAI_API_KEY` の入力を求め、xAI をモデルプロバイダーとして設定します。
    - **OpenCode**: `OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`、取得先: https://opencode.ai/auth）の入力を求め、Zen または Go カタログを選択できます。
    - **Ollama**: Ollama の base URL の入力を求め、**Cloud + Local** または **Local** モードを提示し、利用可能なモデルを検出し、必要に応じて選択したローカルモデルを自動 pull します。
    - 詳細: [Ollama](/ja-JP/providers/ollama)
    - **APIキー**: キーを保存します。
    - **Vercel AI Gateway（複数モデルプロキシ）**: `AI_GATEWAY_API_KEY` の入力を求めます。
    - 詳細: [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID、Gateway ID、`CLOUDFLARE_AI_GATEWAY_API_KEY` の入力を求めます。
    - 詳細: [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
    - **MiniMax**: 設定は自動書き込みされます。ホスト型デフォルトは `MiniMax-M2.7` です。
      APIキー セットアップは `minimax/...` を使用し、OAuth セットアップは
      `minimax-portal/...` を使用します。
    - 詳細: [MiniMax](/ja-JP/providers/minimax)
    - **StepFun**: 中国またはグローバルエンドポイント上の StepFun standard または Step Plan 用に設定が自動書き込みされます。
    - Standard には現在 `step-3.5-flash` が含まれ、Step Plan には `step-3.5-flash-2603` も含まれます。
    - 詳細: [StepFun](/ja-JP/providers/stepfun)
    - **Synthetic（Anthropic互換）**: `SYNTHETIC_API_KEY` の入力を求めます。
    - 詳細: [Synthetic](/ja-JP/providers/synthetic)
    - **Moonshot (Kimi K2)**: 設定は自動書き込みされます。
    - **Kimi Coding**: 設定は自動書き込みされます。
    - 詳細: [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
    - **Skip**: まだ認証は設定しません。
    - 検出された選択肢からデフォルトモデルを選択します（または provider/model を手動入力します）。最良の品質と、より低いプロンプトインジェクションリスクのため、利用可能なプロバイダースタックの中で最も強力な最新世代モデルを選んでください。
    - オンボーディングはモデルチェックを実行し、設定されたモデルが不明または認証不足である場合に警告します。
    - APIキー の保存モードは、デフォルトで平文の認証プロファイル値です。代わりに env ベースの参照を保存するには `--secret-input-mode ref` を使います（例: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）。
    - 認証プロファイルは `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` にあります（APIキー + OAuth）。`~/.openclaw/credentials/oauth.json` は旧式のインポート専用です。
    - 詳細: [/concepts/oauth](/ja-JP/concepts/oauth)
    <Note>
    ヘッドレス/サーバー向けのヒント: ブラウザーがあるマシンで OAuth を完了し、その後
    そのエージェントの `auth-profiles.json`（例:
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`、または対応する
    `$OPENCLAW_STATE_DIR/...` パス）を gateway host にコピーしてください。`credentials/oauth.json`
    は旧式のインポート元にすぎません。
    </Note>
  </Step>
  <Step title="ワークスペース">
    - デフォルトは `~/.openclaw/workspace`（変更可能）。
    - エージェントの bootstrap ritual に必要なワークスペースファイルをシードします。
    - 完全なワークスペース構成とバックアップガイド: [Agent workspace](/ja-JP/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - ポート、bind、認証モード、Tailscale 公開。
    - 推奨認証: loopback であっても **Token** を維持し、ローカル WS クライアントにも認証を必須にしてください。
    - token モードでは、対話セットアップで次が提示されます:
      - **Generate/store plaintext token**（デフォルト）
      - **Use SecretRef**（オプトイン）
      - Quickstart は `env`、`file`、`exec` プロバイダー全体で既存の `gateway.auth.token` SecretRef を再利用して、オンボーディングのプローブ/ダッシュボード bootstrap を行います。
      - その SecretRef が設定されているのに解決できない場合、オンボーディングはランタイム認証を黙って劣化させるのではなく、明確な修正メッセージとともに早期失敗します。
    - password モードでも、対話セットアップは平文または SecretRef 保存をサポートします。
    - 非対話 token SecretRef 経路: `--gateway-token-ref-env <ENV_VAR>`。
      - オンボーディングプロセス環境内に空でない env var が必要です。
      - `--gateway-token` とは併用できません。
    - 認証は、すべてのローカルプロセスを完全に信頼している場合にのみ無効にしてください。
    - 非 loopback bind では、引き続き認証が必要です。
  </Step>
  <Step title="チャネル">
    - [WhatsApp](/ja-JP/channels/whatsapp): 任意のQRログイン。
    - [Telegram](/ja-JP/channels/telegram): bot token。
    - [Discord](/ja-JP/channels/discord): bot token。
    - [Google Chat](/ja-JP/channels/googlechat): service account JSON + webhook audience。
    - [Mattermost](/ja-JP/channels/mattermost)（plugin）: bot token + base URL。
    - [Signal](/ja-JP/channels/signal): 任意の `signal-cli` インストール + アカウント設定。
    - [BlueBubbles](/ja-JP/channels/bluebubbles): **iMessage には推奨**。server URL + password + webhook。
    - [iMessage](/ja-JP/channels/imessage): 旧式の `imsg` CLI 経路 + DB アクセス。
    - DM セキュリティ: デフォルトはペアリングです。最初の DM はコードを送信します。`openclaw pairing approve <channel> <code>` で承認するか、allowlist を使用します。
  </Step>
  <Step title="Web search">
    - Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Ollama Web Search、Perplexity、SearXNG、Tavily などのサポート済みプロバイダーを選択します（またはスキップ）。
    - API ベースのプロバイダーは、すばやいセットアップのために env vars または既存設定を使用できます。キーレスのプロバイダーは、そのプロバイダー固有の前提条件を使います。
    - `--skip-search` でスキップします。
    - 後で設定する場合: `openclaw configure --section web`。
  </Step>
  <Step title="デーモンインストール">
    - macOS: LaunchAgent
      - ログイン済みユーザーセッションが必要です。ヘッドレス用途では、カスタム LaunchDaemon を使用してください（同梱されていません）。
    - Linux（および WSL2 経由の Windows）: systemd user unit
      - オンボーディングは、ログアウト後も Gateway が起動し続けるように `loginctl enable-linger <user>` の有効化を試みます。
      - sudo を求める場合があります（`/var/lib/systemd/linger` に書き込み）。まず sudo なしで試行します。
    - **ランタイム選択:** Node（推奨。WhatsApp/Telegram に必須）。Bun は**推奨されません**。
    - token 認証に token が必要で、`gateway.auth.token` が SecretRef 管理の場合、デーモンインストールはそれを検証しますが、解決された平文 token 値を supervisor サービス環境メタデータへ永続化しません。
    - token 認証に token が必要で、設定済み token SecretRef が未解決の場合、デーモンインストールは実行可能なガイダンス付きでブロックされます。
    - `gateway.auth.token` と `gateway.auth.password` の両方が設定されており、`gateway.auth.mode` が未設定の場合、モードが明示設定されるまでデーモンインストールはブロックされます。
  </Step>
  <Step title="ヘルスチェック">
    - 必要に応じて Gateway を起動し、`openclaw health` を実行します。
    - ヒント: `openclaw status --deep` は、サポートされている場合はチャネルプローブも含めて、ライブ gateway health probe をステータス出力に追加します（到達可能な gateway が必要です）。
  </Step>
  <Step title="Skills（推奨）">
    - 利用可能な Skills を読み取り、要件を確認します。
    - node manager を選択できます: **npm / pnpm**（bun は推奨されません）。
    - 任意の依存関係をインストールします（一部は macOS で Homebrew を使用します）。
  </Step>
  <Step title="完了">
    - 追加機能向けの iOS/Android/macOS アプリを含む、要約と次の手順を表示します。
  </Step>
</Steps>

<Note>
GUI が検出されない場合、オンボーディングはブラウザーを開く代わりに、Control UI 用の SSH ポートフォワード手順を表示します。
Control UI アセットが見つからない場合、オンボーディングはそれらのビルドを試みます。フォールバックは `pnpm ui:build` です（UI 依存関係を自動インストールします）。
</Note>

## 非対話モード

オンボーディングを自動化またはスクリプト化するには `--non-interactive` を使用します。

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

機械可読な要約には `--json` を追加します。

非対話モードでの Gateway token SecretRef:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` と `--gateway-token-ref-env` は相互排他です。

<Note>
`--json` は**非対話モードを意味しません**。スクリプトでは `--non-interactive`（および `--workspace`）を使用してください。
</Note>

プロバイダー固有のコマンド例は [CLI Automation](/ja-JP/start/wizard-cli-automation#provider-specific-examples) にあります。
このリファレンスページは、フラグの意味と手順順序のために使用してください。

### エージェントを追加（非対話）

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway ウィザード RPC

Gateway は RPC 経由でオンボーディングフローを公開します（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）。
クライアント（macOS アプリ、Control UI）は、オンボーディングロジックを再実装せずに手順を描画できます。

## Signal セットアップ（signal-cli）

オンボーディングは GitHub releases から `signal-cli` をインストールできます。

- 適切な release asset をダウンロードします。
- それを `~/.openclaw/tools/signal-cli/<version>/` に保存します。
- `channels.signal.cliPath` を設定に書き込みます。

注記:

- JVM ビルドには **Java 21** が必要です。
- 利用可能な場合はネイティブビルドが使われます。
- Windows は WSL2 を使用し、signal-cli インストールは WSL 内で Linux フローに従います。

## ウィザードが書き込むもの

`~/.openclaw/openclaw.json` に書き込まれる典型的なフィールド:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（Minimax が選択された場合）
- `tools.profile`（ローカルオンボーディングでは、未設定時のデフォルトは `"coding"`。既存の明示値は保持されます）
- `gateway.*`（mode、bind、auth、tailscale）
- `session.dmScope`（挙動の詳細: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference#outputs-and-internals)）
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- プロンプト中にオプトインした場合のチャネル allowlist（Slack/Discord/Matrix/Microsoft Teams）。可能であれば名前は ID に解決されます。
- `skills.install.nodeManager`
  - `setup --node-manager` は `npm`、`pnpm`、または `bun` を受け付けます。
  - 手動設定では、`skills.install.nodeManager` を直接設定することで引き続き `yarn` を使用できます。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` は `agents.list[]` と任意の `bindings` を書き込みます。

WhatsApp の認証情報は `~/.openclaw/credentials/whatsapp/<accountId>/` 配下に置かれます。
セッションは `~/.openclaw/agents/<agentId>/sessions/` 配下に保存されます。

一部のチャネルは plugin として提供されます。セットアップ中にそれらを選択すると、オンボーディングは設定前にそれらのインストール（npm またはローカルパス）を求めます。

## 関連ドキュメント

- オンボーディング概要: [Onboarding (CLI)](/ja-JP/start/wizard)
- macOS アプリのオンボーディング: [Onboarding](/ja-JP/start/onboarding)
- 設定リファレンス: [Gateway configuration](/ja-JP/gateway/configuration)
- プロバイダー: [WhatsApp](/ja-JP/channels/whatsapp), [Telegram](/ja-JP/channels/telegram), [Discord](/ja-JP/channels/discord), [Google Chat](/ja-JP/channels/googlechat), [Signal](/ja-JP/channels/signal), [BlueBubbles](/ja-JP/channels/bluebubbles) (iMessage), [iMessage](/ja-JP/channels/imessage) (legacy)
- Skills: [Skills](/ja-JP/tools/skills), [Skills config](/ja-JP/tools/skills-config)
