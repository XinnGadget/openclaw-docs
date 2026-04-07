---
read_when:
    - 特定のオンボーディングステップやフラグを調べている
    - 非対話モードでオンボーディングを自動化している
    - オンボーディングの動作をデバッグしている
sidebarTitle: Onboarding Reference
summary: 'CLIオンボーディングの完全リファレンス: すべてのステップ、フラグ、config field'
title: オンボーディングリファレンス
x-i18n:
    generated_at: "2026-04-07T04:46:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: a142b9ec4323fabb9982d05b64375d2b4a4007dffc910acbee3a38ff871a7236
    source_path: reference/wizard.md
    workflow: 15
---

# オンボーディングリファレンス

これは `openclaw onboard` の完全なリファレンスです。
概要については、[オンボーディング（CLI）](/ja-JP/start/wizard) を参照してください。

## フロー詳細（local mode）

<Steps>
  <Step title="既存configの検出">
    - `~/.openclaw/openclaw.json` が存在する場合は、**Keep / Modify / Reset** を選択します。
    - オンボーディングを再実行しても、明示的に **Reset** を選ばない限り
      （または `--reset` を渡さない限り）、何も消去されません。
    - CLIの `--reset` はデフォルトで `config+creds+sessions` を対象にします。workspaceも削除するには
      `--reset-scope full` を使用します。
    - configが無効、またはlegacy keyを含んでいる場合、ウィザードは停止し、
      続行前に `openclaw doctor` を実行するよう求めます。
    - Resetは `trash` を使用し（`rm` は決して使いません）、次のスコープを提供します:
      - Configのみ
      - Config + 認証情報 + セッション
      - 完全リセット（workspaceも削除）
  </Step>
  <Step title="Model/Auth">
    - **Anthropic API key**: 存在すれば `ANTHROPIC_API_KEY` を使用し、なければキーの入力を求め、その後デーモン利用のために保存します。
    - **Anthropic API key**: オンボーディング/設定における推奨Anthropic assistant選択肢です。
    - **Anthropic setup-token**: オンボーディング/設定で引き続き利用可能ですが、OpenClawは現在、利用可能ならClaude CLIの再利用を優先します。
    - **OpenAI Code (Codex) subscription (Codex CLI)**: `~/.codex/auth.json` が存在する場合、オンボーディングでそれを再利用できます。再利用されたCodex CLI認証情報は引き続きCodex CLIによって管理されます。期限切れ時には、OpenClawはまずそのソースを再読み込みし、プロバイダーが更新可能な場合は、自身で所有権を持つのではなく、更新済み認証情報をCodexストレージに書き戻します。
    - **OpenAI Code (Codex) subscription (OAuth)**: ブラウザーフローです。`code#state` を貼り付けます。
      - modelが未設定、または `openai/*` の場合、`agents.defaults.model` を `openai-codex/gpt-5.4` に設定します。
    - **OpenAI API key**: 存在すれば `OPENAI_API_KEY` を使用し、なければキーの入力を求め、その後auth profileに保存します。
      - modelが未設定、`openai/*`、または `openai-codex/*` の場合、`agents.defaults.model` を `openai/gpt-5.4` に設定します。
    - **xAI (Grok) API key**: `XAI_API_KEY` の入力を求め、xAIをモデルプロバイダーとして設定します。
    - **OpenCode**: `OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`、取得先は https://opencode.ai/auth）の入力を求め、ZenまたはGoカタログを選べます。
    - **Ollama**: Ollama base URLの入力を求め、**Cloud + Local** または **Local** モードを提示し、利用可能なmodelを検出し、必要に応じて選択したlocal modelを自動でpullします。
    - 詳細: [Ollama](/ja-JP/providers/ollama)
    - **API key**: キーを保存します。
    - **Vercel AI Gateway (multi-model proxy)**: `AI_GATEWAY_API_KEY` の入力を求めます。
    - 詳細: [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID、Gateway ID、`CLOUDFLARE_AI_GATEWAY_API_KEY` の入力を求めます。
    - 詳細: [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
    - **MiniMax**: configは自動書き込みされます。ホスト側のデフォルトは `MiniMax-M2.7` です。
      APIキー設定では `minimax/...` を使用し、OAuth設定では
      `minimax-portal/...` を使用します。
    - 詳細: [MiniMax](/ja-JP/providers/minimax)
    - **StepFun**: Chinaまたはglobal endpoint上のStepFun standardまたはStep Plan向けに、configが自動書き込みされます。
    - 現在、Standardには `step-3.5-flash` が含まれ、Step Planには `step-3.5-flash-2603` も含まれます。
    - 詳細: [StepFun](/ja-JP/providers/stepfun)
    - **Synthetic (Anthropic-compatible)**: `SYNTHETIC_API_KEY` の入力を求めます。
    - 詳細: [Synthetic](/ja-JP/providers/synthetic)
    - **Moonshot (Kimi K2)**: configは自動書き込みされます。
    - **Kimi Coding**: configは自動書き込みされます。
    - 詳細: [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
    - **Skip**: まだauthは設定しません。
    - 検出された候補からデフォルトmodelを選択します（または provider/model を手入力します）。品質を最大化し、prompt injectionリスクを下げるには、利用可能なprovider stackの中で最も強力な最新世代modelを選んでください。
    - オンボーディングはmodelチェックを実行し、設定されたmodelが不明、またはauthが欠けている場合は警告します。
    - APIキーの保存モードは、デフォルトで平文のauth-profile値です。代わりにenvベースのrefを保存するには `--secret-input-mode ref` を使用します（例: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）。
    - auth profileは `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` にあります（API keys + OAuth）。`~/.openclaw/credentials/oauth.json` はlegacyのimport専用です。
    - 詳細: [/concepts/oauth](/ja-JP/concepts/oauth)
    <Note>
    ヘッドレス/サーバー向けのヒント: ブラウザーのあるマシンでOAuthを完了し、その
    エージェントの `auth-profiles.json` を（たとえば
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`、または対応する
    `$OPENCLAW_STATE_DIR/...` のパスから）gateway hostにコピーしてください。`credentials/oauth.json`
    はlegacyのimport元にすぎません。
    </Note>
  </Step>
  <Step title="Workspace">
    - デフォルトは `~/.openclaw/workspace`（変更可能）。
    - agent bootstrap ritualに必要なworkspace fileを作成します。
    - 完全なworkspaceレイアウトとバックアップガイド: [Agent workspace](/ja-JP/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - ポート、bind、auth mode、Tailscale公開を設定します。
    - 推奨auth: loopbackであっても **Token** を維持し、local WS clientにも認証を要求してください。
    - token modeでは、対話セットアップは次を提供します:
      - **平文トークンを生成/保存**（デフォルト）
      - **SecretRefを使う**（オプトイン）
      - クイックスタートでは、オンボーディングのprobe/dashboard bootstrap向けに、既存の `gateway.auth.token` SecretRef を `env`、`file`、`exec` provider間で再利用します。
      - そのSecretRefが設定されているのに解決できない場合、オンボーディングはランタイムauthを黙って劣化させるのではなく、明確な修正メッセージとともに早期失敗します。
    - password modeでも、対話セットアップは平文またはSecretRef保存をサポートします。
    - 非対話のtoken SecretRef経路: `--gateway-token-ref-env <ENV_VAR>`。
      - オンボーディングプロセス環境内に、空でないenv varが必要です。
      - `--gateway-token` とは併用できません。
    - すべてのlocal processを完全に信頼している場合にのみ、authを無効にしてください。
    - 非loopback bindでは引き続きauthが必要です。
  </Step>
  <Step title="Channels">
    - [WhatsApp](/ja-JP/channels/whatsapp): 任意のQRログイン。
    - [Telegram](/ja-JP/channels/telegram): bot token。
    - [Discord](/ja-JP/channels/discord): bot token。
    - [Google Chat](/ja-JP/channels/googlechat): service account JSON + webhook audience。
    - [Mattermost](/ja-JP/channels/mattermost)（plugin）: bot token + base URL。
    - [Signal](/ja-JP/channels/signal): 任意の `signal-cli` インストール + account config。
    - [BlueBubbles](/ja-JP/channels/bluebubbles): **iMessageには推奨**。server URL + password + webhook。
    - [iMessage](/ja-JP/channels/imessage): legacy `imsg` CLI path + DB access。
    - DMセキュリティ: デフォルトはpairingです。最初のDMでコードが送られます。`openclaw pairing approve <channel> <code>` で承認するか、allowlistを使用します。
  </Step>
  <Step title="Web search">
    - Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Ollama Web Search、Perplexity、SearXNG、Tavily などのサポート済みproviderを選択します（またはskip）。
    - APIベースproviderでは、クイックセットアップのためにenv varsまたは既存configを使用できます。キー不要providerでは、それぞれのprovider固有の前提条件を使用します。
    - `--skip-search` でスキップします。
    - 後で設定するには: `openclaw configure --section web`。
  </Step>
  <Step title="Daemon install">
    - macOS: LaunchAgent
      - ログイン済みユーザーセッションが必要です。ヘッドレス用には、カスタムLaunchDaemonを使用してください（同梱されていません）。
    - Linux（およびWSL2経由のWindows）: systemd user unit
      - オンボーディングは、logout後もGatewayが動作し続けるように `loginctl enable-linger <user>` によるlingering有効化を試みます。
      - sudoを求める場合があります（`/var/lib/systemd/linger` に書き込み）。最初はsudoなしで試します。
    - **ランタイム選択:** Node（推奨。WhatsApp/Telegramに必須）。Bunは**推奨されません**。
    - token authでトークンが必要かつ `gateway.auth.token` がSecretRef管理されている場合、daemon installはそれを検証しますが、解決済み平文トークン値をsupervisor service環境メタデータへ永続化しません。
    - token authでトークンが必要なのに、設定されたtoken SecretRefが未解決の場合、daemon installは実行可能な案内付きでブロックされます。
    - `gateway.auth.token` と `gateway.auth.password` の両方が設定され、`gateway.auth.mode` が未設定の場合、modeが明示的に設定されるまでdaemon installはブロックされます。
  </Step>
  <Step title="Health check">
    - 必要に応じてGatewayを起動し、`openclaw health` を実行します。
    - ヒント: `openclaw status --deep` を使うと、ライブgateway health probeがstatus出力に追加され、サポートされている場合はchannel probeも含まれます（到達可能なgatewayが必要）。
  </Step>
  <Step title="Skills（推奨）">
    - 利用可能なSkillsを読み取り、要件を確認します。
    - node managerを選択できます: **npm / pnpm**（bunは推奨されません）。
    - 任意の依存関係をインストールします（一部はmacOSでHomebrewを使用します）。
  </Step>
  <Step title="完了">
    - サマリーと次のステップ。追加機能向けのiOS/Android/macOSアプリも含みます。
  </Step>
</Steps>

<Note>
GUIが検出されない場合、オンボーディングはブラウザーを開く代わりに、Control UI用のSSHポートフォワード手順を表示します。
Control UIアセットが欠けている場合、オンボーディングはそれらのビルドを試みます。フォールバックは `pnpm ui:build` です（UI依存関係を自動インストールします）。
</Note>

## 非対話モード

オンボーディングを自動化またはスクリプト化するには `--non-interactive` を使用します:

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

機械可読なサマリーには `--json` を追加します。

非対話モードでのGateway token SecretRef:

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

provider固有のコマンド例は [CLI Automation](/ja-JP/start/wizard-cli-automation#provider-specific-examples) にあります。
フラグの意味とステップ順序については、このリファレンスページを使用してください。

### Add agent（非対話）

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## GatewayウィザードRPC

Gatewayは、RPC経由でオンボーディングフローを公開しています（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）。
client（macOSアプリ、Control UI）は、オンボーディングロジックを再実装せずにステップを描画できます。

## Signalセットアップ（signal-cli）

オンボーディングでは、GitHub releasesから `signal-cli` をインストールできます:

- 適切なrelease assetをダウンロードします。
- `~/.openclaw/tools/signal-cli/<version>/` 配下に保存します。
- configに `channels.signal.cliPath` を書き込みます。

注記:

- JVM buildには **Java 21** が必要です。
- 利用可能な場合はnative buildが使われます。
- WindowsではWSL2を使用します。signal-cliのインストールはWSL内でLinuxフローに従います。

## ウィザードが書き込む内容

`~/.openclaw/openclaw.json` に書き込まれる代表的なfield:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（MiniMaxを選択した場合）
- `tools.profile`（localオンボーディングでは未設定時にデフォルトで `"coding"` になります。既存の明示値は保持されます）
- `gateway.*`（mode、bind、auth、tailscale）
- `session.dmScope`（動作詳細: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference#outputs-and-internals)）
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- prompt中にオプトインした場合のchannel allowlist（Slack/Discord/Matrix/Microsoft Teams）。可能な場合は名前がIDに解決されます。
- `skills.install.nodeManager`
  - `setup --node-manager` は `npm`、`pnpm`、`bun` を受け付けます。
  - 手動configでは、`skills.install.nodeManager` を直接設定することで引き続き `yarn` を使えます。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` は `agents.list[]` と任意の `bindings` を書き込みます。

WhatsApp認証情報は `~/.openclaw/credentials/whatsapp/<accountId>/` 配下に保存されます。
セッションは `~/.openclaw/agents/<agentId>/sessions/` 配下に保存されます。

一部のchannelはpluginとして提供されます。セットアップ中にそれらを選ぶと、オンボーディングは
設定前にそれをインストールするよう求めます（npmまたはlocal path）。

## 関連ドキュメント

- オンボーディング概要: [オンボーディング（CLI）](/ja-JP/start/wizard)
- macOSアプリのオンボーディング: [オンボーディング](/ja-JP/start/onboarding)
- Configリファレンス: [Gateway configuration](/ja-JP/gateway/configuration)
- Providers: [WhatsApp](/ja-JP/channels/whatsapp), [Telegram](/ja-JP/channels/telegram), [Discord](/ja-JP/channels/discord), [Google Chat](/ja-JP/channels/googlechat), [Signal](/ja-JP/channels/signal), [BlueBubbles](/ja-JP/channels/bluebubbles)（iMessage）, [iMessage](/ja-JP/channels/imessage)（legacy）
- Skills: [Skills](/ja-JP/tools/skills), [Skills config](/ja-JP/tools/skills-config)
