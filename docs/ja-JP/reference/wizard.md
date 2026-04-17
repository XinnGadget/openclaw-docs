---
read_when:
    - 特定のオンボーディング手順やフラグを調べる場合
    - 非対話モードでオンボーディングを自動化する場合
    - オンボーディングの動作をデバッグする場合
sidebarTitle: Onboarding Reference
summary: 'CLIオンボーディングの完全リファレンス: すべての手順、フラグ、設定フィールド'
title: オンボーディングのリファレンス
x-i18n:
    generated_at: "2026-04-15T14:41:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# オンボーディングのリファレンス

これは`openclaw onboard`の完全リファレンスです。
概要については、[Onboarding (CLI)](/ja-JP/start/wizard)を参照してください。

## フローの詳細（ローカルモード）

<Steps>
  <Step title="既存設定の検出">
    - `~/.openclaw/openclaw.json`が存在する場合、**Keep / Modify / Reset**を選択します。
    - オンボーディングを再実行しても、明示的に**Reset**を選ばない限り
      （または`--reset`を渡さない限り）、何も消去されません。
    - CLIの`--reset`のデフォルトは`config+creds+sessions`です。ワークスペースも削除するには`--reset-scope full`
      を使用します。
    - 設定が無効であるか、レガシーキーを含んでいる場合、ウィザードは停止し、
      続行する前に`openclaw doctor`を実行するよう求めます。
    - Resetは`trash`を使用します（`rm`は決して使いません）。選べるスコープは次のとおりです:
      - 設定のみ
      - 設定 + 認証情報 + セッション
      - 完全リセット（ワークスペースも削除）
  </Step>
  <Step title="モデル/認証">
    - **Anthropic API key**: `ANTHROPIC_API_KEY`が存在すればそれを使用し、なければキーの入力を求め、その後デーモン用に保存します。
    - **Anthropic API key**: オンボーディング/設定で推奨されるAnthropicアシスタントの選択肢です。
    - **Anthropic setup-token**: オンボーディング/設定で引き続き利用可能ですが、OpenClawは利用可能な場合にClaude CLIの再利用を優先するようになりました。
    - **OpenAI Code (Codex) subscription (Codex CLI)**: `~/.codex/auth.json`が存在する場合、オンボーディングで再利用できます。再利用されたCodex CLI認証情報は引き続きCodex CLIによって管理されます。有効期限が切れると、OpenClawはまずそのソースを再読み込みし、プロバイダーが更新可能な場合は、認証情報の所有権を引き取るのではなく、更新後の認証情報をCodexストレージに書き戻します。
    - **OpenAI Code (Codex) subscription (OAuth)**: ブラウザーフローです。`code#state`を貼り付けます。
      - モデルが未設定または`openai/*`の場合、`agents.defaults.model`を`openai-codex/gpt-5.4`に設定します。
    - **OpenAI API key**: `OPENAI_API_KEY`が存在すればそれを使用し、なければキーの入力を求め、その後認証プロファイルに保存します。
      - モデルが未設定、`openai/*`、または`openai-codex/*`の場合、`agents.defaults.model`を`openai/gpt-5.4`に設定します。
    - **xAI (Grok) API key**: `XAI_API_KEY`の入力を求め、モデルプロバイダーとしてxAIを設定します。
    - **OpenCode**: `OPENCODE_API_KEY`（または`OPENCODE_ZEN_API_KEY`、取得先はhttps://opencode.ai/auth）の入力を求め、ZenまたはGoカタログを選べるようにします。
    - **Ollama**: 最初に**Cloud + Local**、**Cloud only**、または**Local only**を提示します。`Cloud only`では`OLLAMA_API_KEY`の入力を求め、`https://ollama.com`を使用します。ホスト利用モードではOllamaのベースURLの入力を求め、利用可能なモデルを検出し、必要に応じて選択したローカルモデルを自動的にpullします。`Cloud + Local`では、そのOllamaホストがcloud access用にサインイン済みかどうかも確認します。
    - 詳細: [Ollama](/ja-JP/providers/ollama)
    - **API key**: キーを保存します。
    - **Vercel AI Gateway (multi-model proxy)**: `AI_GATEWAY_API_KEY`の入力を求めます。
    - 詳細: [Vercel AI Gateway](/ja-JP/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID、Gateway ID、`CLOUDFLARE_AI_GATEWAY_API_KEY`の入力を求めます。
    - 詳細: [Cloudflare AI Gateway](/ja-JP/providers/cloudflare-ai-gateway)
    - **MiniMax**: 設定は自動で書き込まれます。ホスト版のデフォルトは`MiniMax-M2.7`です。
      APIキー設定では`minimax/...`を使用し、OAuth設定では
      `minimax-portal/...`を使用します。
    - 詳細: [MiniMax](/ja-JP/providers/minimax)
    - **StepFun**: 設定は、中国またはグローバルエンドポイント上のStepFun standardまたはStep Plan向けに自動で書き込まれます。
    - Standardには現在`step-3.5-flash`が含まれ、Step Planには`step-3.5-flash-2603`も含まれます。
    - 詳細: [StepFun](/ja-JP/providers/stepfun)
    - **Synthetic (Anthropic-compatible)**: `SYNTHETIC_API_KEY`の入力を求めます。
    - 詳細: [Synthetic](/ja-JP/providers/synthetic)
    - **Moonshot (Kimi K2)**: 設定は自動で書き込まれます。
    - **Kimi Coding**: 設定は自動で書き込まれます。
    - 詳細: [Moonshot AI (Kimi + Kimi Coding)](/ja-JP/providers/moonshot)
    - **Skip**: まだ認証は設定されません。
    - 検出された選択肢からデフォルトモデルを選ぶか、provider/modelを手入力します。最高品質でプロンプトインジェクションのリスクを下げるには、利用中のプロバイダースタックで利用可能な、最新世代の最も強力なモデルを選んでください。
    - オンボーディングはモデルチェックを実行し、設定されたモデルが不明または認証が不足している場合に警告します。
    - API keyの保存モードのデフォルトは、平文のauth-profile値です。代わりにenvベースのrefを保存するには`--secret-input-mode ref`を使用します（例: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`）。
    - Auth profileは`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`に保存されます（APIキー + OAuth）。`~/.openclaw/credentials/oauth.json`はレガシーのインポート専用です。
    - 詳細: [/concepts/oauth](/ja-JP/concepts/oauth)
    <Note>
    ヘッドレス/サーバー向けのヒント: ブラウザーのあるマシンでOAuthを完了してから、
    そのエージェントの`auth-profiles.json`（たとえば
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`、または対応する
    `$OPENCLAW_STATE_DIR/...`のパス）をGatewayホストにコピーしてください。`credentials/oauth.json`
    はレガシーなインポート元にすぎません。
    </Note>
  </Step>
  <Step title="ワークスペース">
    - デフォルトは`~/.openclaw/workspace`です（設定可能）。
    - エージェントのブートストラップ儀式に必要なワークスペースファイルをシードします。
    - 完全なワークスペースレイアウトとバックアップガイド: [Agent workspace](/ja-JP/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - ポート、bind、認証モード、Tailscale公開。
    - 認証の推奨: loopbackであっても**Token**のままにして、ローカルWSクライアントに認証を必須にしてください。
    - tokenモードでは、対話型セットアップで次を提供します:
      - **Generate/store plaintext token**（デフォルト）
      - **Use SecretRef**（オプトイン）
      - クイックスタートでは、オンボーディングのprobe/dashboardブートストラップ用に、`env`、`file`、`exec`プロバイダーにまたがる既存の`gateway.auth.token` SecretRefを再利用します。
      - そのSecretRefが設定されていても解決できない場合、オンボーディングはランタイム認証を黙って劣化させる代わりに、明確な修正メッセージを出して早期に失敗します。
    - passwordモードでは、対話型セットアップでも平文またはSecretRefによる保存をサポートします。
    - 非対話型のtoken SecretRefパス: `--gateway-token-ref-env <ENV_VAR>`。
      - オンボーディングプロセス環境内に空でない環境変数が必要です。
      - `--gateway-token`とは併用できません。
    - すべてのローカルプロセスを完全に信頼している場合にのみ認証を無効化してください。
    - 非`loopback`のbindでは、引き続き認証が必要です。
  </Step>
  <Step title="チャンネル">
    - [WhatsApp](/ja-JP/channels/whatsapp): 任意のQRログイン。
    - [Telegram](/ja-JP/channels/telegram): ボットトークン。
    - [Discord](/ja-JP/channels/discord): ボットトークン。
    - [Google Chat](/ja-JP/channels/googlechat): サービスアカウントJSON + Webhook audience。
    - [Mattermost](/ja-JP/channels/mattermost) (Plugin): ボットトークン + ベースURL。
    - [Signal](/ja-JP/channels/signal): 任意の`signal-cli`インストール + アカウント設定。
    - [BlueBubbles](/ja-JP/channels/bluebubbles): **iMessageには推奨**。サーバーURL + パスワード + Webhook。
    - [iMessage](/ja-JP/channels/imessage): レガシーな`imsg` CLIパス + DBアクセス。
    - DMセキュリティ: デフォルトはペアリングです。最初のDMでコードが送信されます。`openclaw pairing approve <channel> <code>`で承認するか、許可リストを使用してください。
  </Step>
  <Step title="Web検索">
    - Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、Ollama Web Search、Perplexity、SearXNG、Tavilyなどのサポート対象プロバイダーを選びます（またはスキップ）。
    - APIベースのプロバイダーは、env varまたは既存設定を使ってすばやくセットアップできます。キー不要のプロバイダーは、代わりにそのプロバイダー固有の前提条件を使用します。
    - `--skip-search`でスキップします。
    - 後で設定する場合: `openclaw configure --section web`。
  </Step>
  <Step title="デーモンのインストール">
    - macOS: LaunchAgent
      - ログイン済みユーザーセッションが必要です。ヘッドレス用途では、カスタムLaunchDaemonを使用してください（同梱されていません）。
    - Linux（およびWindowsのWSL2経由）: systemd user unit
      - オンボーディングでは、ログアウト後もGatewayが起動したままになるよう、`loginctl enable-linger <user>`によるlingeringの有効化を試みます。
      - sudoを求められる場合があります（`/var/lib/systemd/linger`に書き込みます）。まずsudoなしで試行します。
    - **ランタイム選択:** Node（推奨。WhatsApp/Telegramには必須）。Bunは**推奨されません**。
    - token認証でtokenが必要かつ`gateway.auth.token`がSecretRef管理の場合、デーモンのインストールではその検証を行いますが、解決済みの平文token値をsupervisorサービスの環境メタデータには保存しません。
    - token認証でtokenが必要かつ設定されたtoken SecretRefが未解決の場合、デーモンのインストールは実行可能なガイダンス付きでブロックされます。
    - `gateway.auth.token`と`gateway.auth.password`の両方が設定されていて、`gateway.auth.mode`が未設定の場合、モードが明示的に設定されるまでデーモンのインストールはブロックされます。
  </Step>
  <Step title="ヘルスチェック">
    - 必要に応じてGatewayを起動し、`openclaw health`を実行します。
    - ヒント: `openclaw status --deep`は、サポートされる場合にチャンネルprobeを含むライブGatewayヘルスprobeをステータス出力に追加します（到達可能なGatewayが必要です）。
  </Step>
  <Step title="Skills（推奨）">
    - 利用可能なSkillsを読み取り、要件を確認します。
    - ノードマネージャーを選択できます: **npm / pnpm**（bunは推奨されません）。
    - 任意の依存関係をインストールします（一部はmacOSでHomebrewを使用します）。
  </Step>
  <Step title="完了">
    - 追加機能向けのiOS/Android/macOSアプリを含む、要約と次のステップが表示されます。
  </Step>
</Steps>

<Note>
GUIが検出されない場合、オンボーディングはブラウザーを開く代わりにControl UI用のSSHポートフォワード手順を表示します。
Control UIアセットが不足している場合、オンボーディングはそれらのビルドを試みます。フォールバックは`pnpm ui:build`です（UI依存関係を自動インストールします）。
</Note>

## 非対話モード

オンボーディングを自動化またはスクリプト化するには`--non-interactive`を使用します。

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

マシン可読な要約を得るには`--json`を追加します。

非対話モードでのGateway token SecretRef:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token`と`--gateway-token-ref-env`は相互排他的です。

<Note>
`--json`は非対話モードを意味しません。スクリプトでは`--non-interactive`（および`--workspace`）を使用してください。
</Note>

プロバイダー固有のコマンド例は[CLI Automation](/ja-JP/start/wizard-cli-automation#provider-specific-examples)にあります。
このリファレンスページは、フラグの意味とステップの順序を確認するために使用してください。

### エージェントを追加（非対話）

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

GatewayはRPC（`wizard.start`、`wizard.next`、`wizard.cancel`、`wizard.status`）を通じてオンボーディングフローを公開しています。
クライアント（macOSアプリ、Control UI）は、オンボーディングロジックを再実装することなくステップを描画できます。

## Signalセットアップ（signal-cli）

オンボーディングはGitHub releasesから`signal-cli`をインストールできます。

- 適切なrelease assetをダウンロードします。
- `~/.openclaw/tools/signal-cli/<version>/`配下に保存します。
- 設定に`channels.signal.cliPath`を書き込みます。

注意:

- JVMビルドには**Java 21**が必要です。
- 利用可能な場合はネイティブビルドを使用します。
- WindowsではWSL2を使用します。signal-cliのインストールはWSL内でLinuxフローに従います。

## ウィザードが書き込む内容

`~/.openclaw/openclaw.json`内の一般的なフィールド:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers`（MiniMaxを選択した場合）
- `tools.profile`（ローカルオンボーディングでは未設定時のデフォルトが`"coding"`になります。既存の明示的な値は保持されます）
- `gateway.*`（mode、bind、auth、tailscale）
- `session.dmScope`（動作の詳細: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference#outputs-and-internals)）
- `channels.telegram.botToken`、`channels.discord.token`、`channels.matrix.*`、`channels.signal.*`、`channels.imessage.*`
- プロンプト中にオプトインした場合のチャンネル許可リスト（Slack/Discord/Matrix/Microsoft Teams）。可能な場合は名前がIDに解決されます。
- `skills.install.nodeManager`
  - `setup --node-manager`は`npm`、`pnpm`、または`bun`を受け付けます。
  - 手動設定では、`skills.install.nodeManager`を直接設定することで引き続き`yarn`を使用できます。
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`は`agents.list[]`と任意の`bindings`を書き込みます。

WhatsAppの認証情報は`~/.openclaw/credentials/whatsapp/<accountId>/`配下に保存されます。
セッションは`~/.openclaw/agents/<agentId>/sessions/`配下に保存されます。

一部のチャンネルはPluginとして提供されます。セットアップ中にそれらを選択すると、オンボーディングは設定前にそのインストール（npmまたはローカルパス）を求めます。

## 関連ドキュメント

- オンボーディング概要: [Onboarding (CLI)](/ja-JP/start/wizard)
- macOSアプリのオンボーディング: [Onboarding](/ja-JP/start/onboarding)
- 設定リファレンス: [Gateway configuration](/ja-JP/gateway/configuration)
- プロバイダー: [WhatsApp](/ja-JP/channels/whatsapp)、[Telegram](/ja-JP/channels/telegram)、[Discord](/ja-JP/channels/discord)、[Google Chat](/ja-JP/channels/googlechat)、[Signal](/ja-JP/channels/signal)、[BlueBubbles](/ja-JP/channels/bluebubbles)（iMessage）、[iMessage](/ja-JP/channels/imessage)（レガシー）
- Skills: [Skills](/ja-JP/tools/skills)、[Skills config](/ja-JP/tools/skills-config)
