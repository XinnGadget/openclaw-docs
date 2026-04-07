---
read_when:
    - CLIオンボーディングを実行または設定する場合
    - 新しいマシンをセットアップする場合
sidebarTitle: 'Onboarding: CLI'
summary: 'CLIオンボーディング: Gateway、workspace、channels、Skillsのガイド付きセットアップ'
title: オンボーディング（CLI）
x-i18n:
    generated_at: "2026-04-07T04:46:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6773b07afa8babf1b5ac94d857063d08094a962ee21ec96ca966e99ad57d107d
    source_path: start/wizard.md
    workflow: 15
---

# オンボーディング（CLI）

CLIオンボーディングは、macOS、
Linux、またはWindows（WSL2経由。強く推奨）でOpenClawをセットアップする**推奨**方法です。
ローカルGatewayまたはリモートGateway接続に加えて、channels、Skills、
workspaceのデフォルトを、1つのガイド付きフローで設定します。

```bash
openclaw onboard
```

<Info>
最速で最初のチャットを始めるには、Control UIを開いてください（channelのセットアップは不要です）。`openclaw dashboard`を実行し、
ブラウザーでチャットします。ドキュメント: [Dashboard](/web/dashboard)。
</Info>

後で再設定するには:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json`はnon-interactiveモードを意味しません。スクリプトでは`--non-interactive`を使用してください。
</Note>

<Tip>
CLIオンボーディングにはweb searchのステップがあり、Brave、DuckDuckGo、Exa、Firecrawl、Gemini、Grok、Kimi、MiniMax Search、
Ollama Web Search、Perplexity、SearXNG、Tavilyなどのproviderを選択できます。一部のproviderでは
API keyが必要ですが、キー不要のものもあります。これは後から`openclaw configure --section web`で設定することもできます。ドキュメント: [Web tools](/ja-JP/tools/web)。
</Tip>

## クイックスタートとAdvanced

オンボーディングは**クイックスタート**（デフォルト）と**Advanced**（完全制御）から始まります。

<Tabs>
  <Tab title="クイックスタート（デフォルト）">
    - ローカルGateway（local loopback）
    - workspaceデフォルト（または既存workspace）
    - Gatewayポート **18789**
    - Gateway認証 **Token**（loopback上でも自動生成）
    - 新しいローカルセットアップのtoolポリシーデフォルト: `tools.profile: "coding"`（既存の明示的なprofileは保持されます）
    - DM分離のデフォルト: ローカルオンボーディングは、未設定の場合に`session.dmScope: "per-channel-peer"`を書き込みます。詳細: [CLI Setup Reference](/ja-JP/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale公開 **Off**
    - Telegram + WhatsApp DMのデフォルトは**allowlist**（電話番号の入力を求められます）
  </Tab>
  <Tab title="Advanced（完全制御）">
    - すべてのステップ（mode、workspace、gateway、channels、daemon、Skills）を公開します。
  </Tab>
</Tabs>

## オンボーディングで設定される内容

**ローカルモード（デフォルト）**では、次のステップを案内します:

1. **モデル/認証** — サポートされている任意のprovider/認証フロー（API key、OAuth、またはprovider固有の手動認証）を選択します。これにはCustom Provider
   （OpenAI互換、Anthropic互換、またはUnknown auto-detect）も含まれます。デフォルトモデルを選びます。
   セキュリティに関する注意: このagentがtoolsを実行したり、webhook/hooks内容を処理したりする場合は、利用可能な中で最も強力な最新世代モデルを選び、tool policyを厳格に保ってください。弱い/古い層はprompt injectionを受けやすくなります。
   non-interactive実行では、`--secret-input-mode ref`は平文のAPI key値ではなく、envベースのrefsをauth profilesに保存します。
   non-interactiveの`ref`モードでは、provider env varが設定されている必要があります。そのenv varなしでインラインのkeyフラグを渡すと即座に失敗します。
   interactive実行では、secret reference modeを選ぶと、環境変数または設定済みprovider ref（`file`または`exec`）のいずれかを指定でき、保存前に高速な事前検証が行われます。
   Anthropicでは、interactiveなオンボーディング/設定で、優先されるローカルパスとして**Anthropic Claude CLI**が、推奨される本番パスとして**Anthropic API key**が提示されます。Anthropic setup-tokenも、サポートされるtoken-authパスとして引き続き利用できます。
2. **Workspace** — agentファイルの配置場所です（デフォルトは`~/.openclaw/workspace`）。bootstrap filesを作成します。
3. **Gateway** — ポート、bind address、auth mode、Tailscale公開。
   interactiveなtoken modeでは、デフォルトの平文token保存を選ぶか、SecretRefへのオプトインを選べます。
   non-interactiveなtoken SecretRefパス: `--gateway-token-ref-env <ENV_VAR>`。
4. **Channels** — BlueBubbles、Discord、Feishu、Google Chat、Mattermost、Microsoft Teams、QQ Bot、Signal、Slack、Telegram、WhatsAppなどの組み込みおよびバンドル済みchat channels。
5. **Daemon** — LaunchAgent（macOS）、systemd user unit（Linux/WSL2）、またはネイティブWindows Scheduled Taskを、ユーザーごとのStartup-folderフォールバック付きでインストールします。
   token authでtokenが必要かつ`gateway.auth.token`がSecretRef管理されている場合、daemon installはそれを検証しますが、解決済みtokenをsupervisor service environment metadataには永続化しません。
   token authでtokenが必要かつ設定されたtoken SecretRefが未解決の場合、daemon installは実行可能なガイダンス付きでブロックされます。
   `gateway.auth.token`と`gateway.auth.password`の両方が設定され、かつ`gateway.auth.mode`が未設定の場合、modeが明示的に設定されるまでdaemon installはブロックされます。
6. **ヘルスチェック** — Gatewayを起動し、実行中であることを確認します。
7. **Skills** — 推奨Skillsと任意の依存関係をインストールします。

<Note>
オンボーディングを再実行しても、明示的に**Reset**を選ぶ（または`--reset`を渡す）までは何も消去されません。
CLIの`--reset`はデフォルトでconfig、credentials、sessionsを対象とします。workspaceも含めるには`--reset-scope full`を使用してください。
configが無効またはlegacy keysを含んでいる場合、オンボーディングは先に`openclaw doctor`を実行するよう求めます。
</Note>

**リモートモード**では、別の場所にあるGatewayへ接続するためのローカルクライアントだけを設定します。
リモートホスト上には何もインストールも変更もしません。

## 別のagentを追加する

`openclaw agents add <name>`を使用して、独自のworkspace、
sessions、auth profilesを持つ別のagentを作成します。`--workspace`なしで実行するとオンボーディングが起動します。

設定される内容:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

注意:

- デフォルトworkspaceは`~/.openclaw/workspace-<agentId>`に従います。
- 受信メッセージをルーティングするには`bindings`を追加します（オンボーディングでも実行できます）。
- non-interactiveフラグ: `--model`、`--agent-dir`、`--bind`、`--non-interactive`。

## 完全なリファレンス

詳細なステップごとの内訳とconfig出力については、
[CLI Setup Reference](/ja-JP/start/wizard-cli-reference)を参照してください。
non-interactiveの例については、[CLI Automation](/ja-JP/start/wizard-cli-automation)を参照してください。
RPCの詳細を含む、より技術的なリファレンスについては、
[Onboarding Reference](/ja-JP/reference/wizard)を参照してください。

## 関連ドキュメント

- CLIコマンドリファレンス: [`openclaw onboard`](/cli/onboard)
- オンボーディング概要: [Onboarding Overview](/ja-JP/start/onboarding-overview)
- macOSアプリのオンボーディング: [Onboarding](/ja-JP/start/onboarding)
- agent初回実行の儀式: [Agent Bootstrapping](/ja-JP/start/bootstrapping)
