---
read_when:
    - ACP経由でコーディングハーネスを実行する場合
    - メッセージングチャネル上で会話に紐づくACPセッションをセットアップする場合
    - メッセージチャネルの会話を永続的なACPセッションへバインドする場合
    - ACPバックエンドとplugin配線をトラブルシュートする場合
    - チャットから`/acp`コマンドを運用する場合
summary: Codex、Claude Code、Cursor、Gemini CLI、OpenClaw ACP、その他のハーネスagent向けにACPランタイムセッションを使う
title: ACP Agents
x-i18n:
    generated_at: "2026-04-07T04:48:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb651ab39b05e537398623ee06cb952a5a07730fc75d3f7e0de20dd3128e72c6
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP agents

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/)セッションにより、OpenClawはACPバックエンドpluginを通じて外部のコーディングハーネス（たとえばPi、Claude Code、Codex、Cursor、Copilot、OpenClaw ACP、OpenCode、Gemini CLI、その他の対応ACPXハーネス）を実行できます。

平文で「これをCodexで実行して」や「このスレッドでClaude Codeを開始して」とOpenClawに依頼した場合、OpenClawはその要求をACPランタイムへルーティングすべきです（ネイティブのsub-agentランタイムではありません）。各ACPセッション起動は、[background task](/ja-JP/automation/tasks)として追跡されます。

既存のOpenClawチャネル会話に対して、CodexやClaude Codeを外部MCPクライアントとして直接接続したい場合は、ACPの代わりに[`openclaw mcp serve`](/cli/mcp)を使ってください。

## どのページを見ればよいですか？

混同しやすい近接したサーフェスが3つあります。

| やりたいこと | 使うもの | 補足 |
| ---------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| Codex、Claude Code、Gemini CLI、または他の外部ハーネスをOpenClaw _経由で_ 実行する | このページ: ACP agents | チャットに紐づくセッション、`/acp spawn`、`sessions_spawn({ runtime: "acp" })`、background task、ランタイム制御 |
| OpenClaw Gatewayセッションをエディターやクライアント向けのACPサーバー _として_ 公開する | [`openclaw acp`](/cli/acp) | ブリッジモード。IDE/クライアントがstdio/WebSocket経由でOpenClawにACPで接続する |
| ローカルAI CLIをテキスト専用のフォールバックモデルとして再利用する | [CLI Backends](/ja-JP/gateway/cli-backends) | ACPではありません。OpenClaw toolsなし、ACP制御なし、ハーネスランタイムなし |

## これはそのままで動きますか？

通常は、はい。

- 新規インストールでは、バンドル済みの`acpx`ランタイムpluginがデフォルトで有効になっています。
- バンドル済みの`acpx`pluginは、pluginローカルに固定された`acpx`バイナリを優先します。
- 起動時に、OpenClawはそのバイナリをプローブし、必要であれば自己修復します。
- 準備状況を素早く確認したい場合は、まず`/acp doctor`から始めてください。

初回使用時にまだ起こりうること:

- 対象ハーネスadapterが、そのハーネスを最初に使うときに`npx`でオンデマンド取得される場合があります。
- そのハーネス向けのベンダー認証は、依然としてホスト上に存在している必要があります。
- ホストにnpm/ネットワークアクセスがない場合、キャッシュを事前に温めるか別の方法でadapterをインストールするまで、初回実行時のadapter取得は失敗することがあります。

例:

- `/acp spawn codex`: OpenClawは`acpx`のブートストラップ準備ができているはずですが、Codex ACP adapterには依然として初回取得が必要な場合があります。
- `/acp spawn claude`: Claude ACP adapterでも同様で、加えてそのホスト上のClaude側認証も必要です。

## すばやい運用フロー

実用的な`/acp`ランブックが欲しい場合はこれを使ってください。

1. セッションを起動する:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. バインドされた会話またはスレッドで作業する（またはそのsession keyを明示的に対象指定する）。
3. ランタイム状態を確認する:
   - `/acp status`
4. 必要に応じてランタイムオプションを調整する:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. コンテキストを置き換えずに、アクティブなセッションへ指示を追加する:
   - `/acp steer tighten logging and continue`
6. 作業を止める:
   - `/acp cancel`（現在のターンを停止）、または
   - `/acp close`（セッションを閉じてバインディングを削除）

## 人向けクイックスタート

自然な依頼の例:

- 「このDiscordチャネルをCodexにバインドして。」
- 「ここでスレッドに永続的なCodexセッションを開始して、集中した状態を維持して。」
- 「これをワンショットのClaude Code ACPセッションとして実行して、結果を要約して。」
- 「このiMessageチャットをCodexにバインドして、追加入力も同じworkspaceで継続して。」
- 「このタスクではGemini CLIをスレッドで使って、その後の追加入力も同じスレッドで継続して。」

OpenClawが行うべきこと:

1. `runtime: "acp"`を選ぶ。
2. 要求されたハーネス対象（`agentId`、たとえば`codex`）を解決する。
3. 現在の会話へのバインドが要求され、かつアクティブチャネルがそれをサポートしている場合、ACPセッションをその会話へバインドする。
4. そうでなければ、スレッドバインドが要求され、かつ現在のチャネルがそれをサポートしている場合、ACPセッションをそのスレッドへバインドする。
5. フォーカス解除/クローズ/期限切れになるまで、その後のバインド済みメッセージを同じACPセッションへルーティングする。

## ACPとsub-agentsの違い

外部ハーネスランタイムを使いたいときはACPを使ってください。OpenClawネイティブの委譲実行を使いたいときはsub-agentsを使ってください。

| 項目 | ACPセッション | sub-agent実行 |
| ------------- | ------------------------------------- | ---------------------------------- |
| ランタイム | ACPバックエンドplugin（たとえばacpx） | OpenClawネイティブsub-agentランタイム |
| Session key | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| 主なコマンド | `/acp ...` | `/subagents ...` |
| 起動tool | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn`（デフォルトランタイム） |

[Sub-agents](/ja-JP/tools/subagents)も参照してください。

## ACPがClaude Codeを実行する仕組み

ACP経由のClaude Codeでは、スタックは次のとおりです。

1. OpenClaw ACPセッション制御プレーン
2. バンドル済みの`acpx`ランタイムplugin
3. Claude ACP adapter
4. Claude側ランタイム/セッション機構

重要な違い:

- ACP Claudeは、ACP制御、セッション再開、background-task追跡、および任意の会話/スレッドバインドを備えたハーネスセッションです。
- CLI backendsは、別個のテキスト専用ローカルフォールバックランタイムです。[CLI Backends](/ja-JP/gateway/cli-backends)を参照してください。

運用上の実用ルール:

- `/acp spawn`、バインド可能なセッション、ランタイム制御、または永続的なハーネス作業が必要: ACPを使う
- 生のCLIを通じた単純なローカルテキストフォールバックが必要: CLI backendsを使う

## バインド済みセッション

### 現在の会話へのバインド

現在の会話を、子スレッドを作らずに永続的なACP workspaceにしたい場合は、`/acp spawn <harness> --bind here`を使います。

動作:

- OpenClawは引き続きチャネルtransport、認証、安全性、配信を所有します。
- 現在の会話は、起動されたACP session keyに固定されます。
- その会話内の後続メッセージは、同じACPセッションへルーティングされます。
- `/new`と`/reset`は、同じバインド済みACPセッションをその場でリセットします。
- `/acp close`はセッションを閉じて、現在の会話バインディングを削除します。

実際の意味:

- `--bind here`は同じチャットサーフェスを維持します。Discordでは、現在のチャネルはそのまま現在のチャネルです。
- `--bind here`は、新しい作業を起動している場合には新しいACPセッションを作成することもあります。バインドは、そのセッションを現在の会話に接続します。
- `--bind here`自体は、子のDiscordスレッドやTelegramトピックを作成しません。
- ACPランタイムは独自の作業ディレクトリ（`cwd`）や、バックエンド管理のディスク上workspaceを持つことがあります。そのランタイムworkspaceはチャットサーフェスとは別物であり、新しいメッセージスレッドを意味しません。
- 別のACP agentへ起動し、かつ`--cwd`を渡さない場合、OpenClawはリクエスターのworkspaceではなく、デフォルトで**対象agentの**workspaceを継承します。
- その継承workspaceパスが存在しない場合（`ENOENT`/`ENOTDIR`）、OpenClawは誤ったツリーを黙って再利用する代わりに、バックエンドのデフォルトcwdへフォールバックします。
- 継承workspaceが存在していてもアクセスできない場合（たとえば`EACCES`）、起動は`cwd`を捨てるのではなく、実際のアクセスエラーを返します。

考え方:

- チャットサーフェス: 人が会話を続ける場所（`Discord channel`、`Telegram topic`、`iMessage chat`）
- ACPセッション: OpenClawがルーティングする永続的なCodex/Claude/Geminiランタイム状態
- 子スレッド/トピック: `--thread ...`でのみ作成される任意の追加メッセージサーフェス
- ランタイムworkspace: ハーネスが実行されるファイルシステム上の場所（`cwd`、repo checkout、バックエンドworkspace）

例:

- `/acp spawn codex --bind here`: このチャットを維持し、Codex ACPセッションを起動または接続し、今後のメッセージをここからそれへルーティングする
- `/acp spawn codex --thread auto`: OpenClawは子スレッド/トピックを作成し、そこへACPセッションをバインドする場合がある
- `/acp spawn codex --bind here --cwd /workspace/repo`: 上と同じチャットバインドだが、Codexは`/workspace/repo`で動作する

現在の会話バインドのサポート:

- 現在の会話バインド対応を公開しているチャット/メッセージチャネルでは、共有の会話バインド経路を通じて`--bind here`を使えます。
- 独自のスレッド/トピックセマンティクスを持つチャネルでも、同じ共有インターフェースの背後でチャネル固有の正規化を提供できます。
- `--bind here`は常に「現在の会話をその場でバインドする」ことを意味します。
- 汎用的な現在の会話バインドは、共有のOpenClaw binding storeを使い、通常のGateway再起動後も保持されます。

注意:

- `/acp spawn`では`--bind here`と`--thread ...`は相互排他的です。
- Discordでは、`--bind here`は現在のチャネルまたはスレッドをその場でバインドします。`spawnAcpSessions`が必要なのは、`--thread auto|here`のためにOpenClawが子スレッドを作成する必要がある場合だけです。
- アクティブなチャネルが現在の会話へのACPバインドを公開していない場合、OpenClawは明確な未対応メッセージを返します。
- `resume`や「新しいセッションにするか」の問題は、チャネルの問題ではなくACPセッションの問題です。現在のチャットサーフェスを変えずに、ランタイム状態を再利用または置き換えることができます。

### スレッドにバインドされたセッション

チャネルadapterでスレッドバインドが有効な場合、ACPセッションはスレッドにバインドできます。

- OpenClawは、スレッドを対象ACPセッションへバインドします。
- そのスレッド内の後続メッセージは、バインド済みACPセッションへルーティングされます。
- ACPの出力は同じスレッドに返送されます。
- フォーカス解除/クローズ/アーカイブ/アイドルタイムアウトまたは最大経過時間の期限切れで、バインディングは削除されます。

スレッドバインドのサポートはadapter固有です。アクティブなチャネルadapterがスレッドバインドをサポートしていない場合、OpenClawは明確な未対応/利用不可メッセージを返します。

スレッドバインドACPに必要なfeature flag:

- `acp.enabled=true`
- `acp.dispatch.enabled`はデフォルトでオンです（ACP dispatchを一時停止するには`false`を設定）
- チャネルadapterのACPスレッド起動フラグが有効（adapter固有）
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### スレッド対応チャネル

- セッション/スレッドバインド機能を公開する任意のチャネルadapter。
- 現在の組み込みサポート:
  - Discordのスレッド/チャネル
  - Telegramトピック（groups/supergroupsのforum topicsとDM topics）
- Pluginチャネルも、同じbindingインターフェースを通じてサポートを追加できます。

## チャネル固有設定

非一時的なワークフローでは、トップレベルの`bindings[]`エントリで永続的なACPバインディングを設定します。

### バインディングモデル

- `bindings[].type="acp"`は、永続的なACP会話バインディングを示します。
- `bindings[].match`は対象会話を識別します:
  - Discordチャネルまたはスレッド: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum topic: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/group chat: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループバインディングには`chat_id:*`または`chat_identifier:*`を推奨します。
  - iMessage DM/group chat: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループバインディングには`chat_id:*`を推奨します。
- `bindings[].agentId`は、所有するOpenClaw agent idです。
- 任意のACPオーバーライドは`bindings[].acp`配下に置きます:
  - `mode`（`persistent`または`oneshot`）
  - `label`
  - `cwd`
  - `backend`

### agentごとのランタイムデフォルト

`agents.list[].runtime`を使って、agentごとにACPデフォルトを一度だけ定義します。

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent`（ハーネスid。たとえば`codex`または`claude`）
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACPバインド済みセッションのオーバーライド優先順位:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. グローバルACPデフォルト（たとえば`acp.backend`）

例:

```json5
{
  agents: {
    list: [
      {
        id: "codex",
        runtime: {
          type: "acp",
          acp: {
            agent: "codex",
            backend: "acpx",
            mode: "persistent",
            cwd: "/workspace/openclaw",
          },
        },
      },
      {
        id: "claude",
        runtime: {
          type: "acp",
          acp: { agent: "claude", backend: "acpx", mode: "persistent" },
        },
      },
    ],
  },
  bindings: [
    {
      type: "acp",
      agentId: "codex",
      match: {
        channel: "discord",
        accountId: "default",
        peer: { kind: "channel", id: "222222222222222222" },
      },
      acp: { label: "codex-main" },
    },
    {
      type: "acp",
      agentId: "claude",
      match: {
        channel: "telegram",
        accountId: "default",
        peer: { kind: "group", id: "-1001234567890:topic:42" },
      },
      acp: { cwd: "/workspace/repo-b" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "discord", accountId: "default" },
    },
    {
      type: "route",
      agentId: "main",
      match: { channel: "telegram", accountId: "default" },
    },
  ],
  channels: {
    discord: {
      guilds: {
        "111111111111111111": {
          channels: {
            "222222222222222222": { requireMention: false },
          },
        },
      },
    },
    telegram: {
      groups: {
        "-1001234567890": {
          topics: { "42": { requireMention: false } },
        },
      },
    },
  },
}
```

動作:

- OpenClawは、設定済みACPセッションが使用前に存在することを保証します。
- そのチャネルまたはトピック内のメッセージは、設定済みACPセッションへルーティングされます。
- バインド済み会話では、`/new`と`/reset`は同じACP session keyをその場でリセットします。
- 一時的なランタイムバインディング（たとえばthread-focusフローで作成されたもの）が存在する場合は、引き続き適用されます。
- 明示的な`cwd`なしのcross-agent ACP起動では、OpenClawはagent設定から対象agent workspaceを継承します。
- 継承workspaceパスが存在しない場合はバックエンドのデフォルトcwdへフォールバックし、実際のアクセス失敗は起動エラーとして表面化します。

## ACPセッションを開始する（インターフェース）

### `sessions_spawn`から

agentターンまたはtool callからACPセッションを開始するには、`runtime: "acp"`を使います。

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

注意:

- `runtime`のデフォルトは`subagent`なので、ACPセッションでは明示的に`runtime: "acp"`を設定してください。
- `agentId`が省略された場合、設定されていればOpenClawは`acp.defaultAgent`を使います。
- `mode: "session"`には、永続的なバインド済み会話を維持するため`thread: true`が必要です。

インターフェース詳細:

- `task`（必須）: ACPセッションへ送られる初期プロンプト。
- `runtime`（ACPでは必須）: `"acp"`でなければなりません。
- `agentId`（任意）: ACP対象ハーネスid。設定されていれば`acp.defaultAgent`へフォールバックします。
- `thread`（任意、デフォルト`false`）: サポートされる場合にスレッドバインドフローを要求します。
- `mode`（任意）: `run`（ワンショット）または`session`（永続）。
  - デフォルトは`run`
  - `thread: true`で`mode`が省略された場合、OpenClawはランタイム経路ごとに永続動作をデフォルトにする場合があります
  - `mode: "session"`には`thread: true`が必要です
- `cwd`（任意）: 要求するランタイム作業ディレクトリ（バックエンド/ランタイムポリシーにより検証される）。省略時は、設定されていればACP起動は対象agent workspaceを継承します。継承パスが存在しない場合はバックエンドデフォルトへフォールバックし、実際のアクセスエラーは返されます。
- `label`（任意）: セッション/バナー文で使われる運用者向けラベル。
- `resumeSessionId`（任意）: 新規作成の代わりに既存ACPセッションを再開します。agentは`session/load`経由で会話履歴を再生します。`runtime: "acp"`が必要です。
- `streamTo`（任意）: `"parent"`を指定すると、初期ACP実行の進行サマリーをシステムイベントとしてリクエスターセッションへストリームします。
  - 利用可能な場合、acceptedレスポンスには完全なリレー履歴をtailできるセッション単位JSONLログ（`<sessionId>.acp-stream.jsonl`）を指す`streamLogPath`が含まれます。

### 既存セッションを再開する

新規開始ではなく以前のACPセッションを継続するには、`resumeSessionId`を使います。agentは`session/load`経由で会話履歴を再生するため、以前までの完全なコンテキストを持って再開できます。

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

一般的な用途:

- CodexセッションをノートPCからスマートフォンへ引き継ぐ — 以前の続きを行うようagentに伝える
- CLIで対話的に始めたコーディングセッションを、今度はagent経由でヘッドレスに継続する
- Gateway再起動やアイドルタイムアウトで中断された作業を再開する

注意:

- `resumeSessionId`には`runtime: "acp"`が必要です。sub-agentランタイムで使うとエラーになります。
- `resumeSessionId`は上流ACP会話履歴を復元しますが、`thread`と`mode`は作成中の新しいOpenClawセッションにも通常どおり適用されるため、`mode: "session"`には引き続き`thread: true`が必要です。
- 対象agentは`session/load`をサポートしている必要があります（CodexとClaude Codeはサポートします）。
- session IDが見つからない場合、起動は明確なエラーで失敗します。新しいセッションへ黙ってフォールバックすることはありません。

### 運用スモークテスト

Gatewayデプロイ後に、単にユニットテストが通るだけでなく、ACP起動が本当にエンドツーエンドで動いているかを素早くライブ確認したい場合に使ってください。

推奨ゲート:

1. 対象ホスト上のデプロイ済みGatewayバージョン/コミットを確認する。
2. デプロイ済みソースに、`src/gateway/sessions-patch.ts`内のACP lineage受け入れ（`subagent:* or acp:* sessions`）が含まれていることを確認する。
3. ライブagent（たとえば`jpclawhq`上の`razor(main)`）に対して、一時的なACPX bridgeセッションを開く。
4. そのagentに、次を指定して`sessions_spawn`を呼ぶよう依頼する:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - task: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. agentが次を報告することを確認する:
   - `accepted=yes`
   - 実在する`childSessionKey`
   - validator errorなし
6. 一時的なACPX bridgeセッションをクリーンアップする。

ライブagentへのプロンプト例:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

注意:

- このスモークテストは、意図的にスレッドバインドされた永続ACPセッションを検証するのでない限り、`mode: "run"`のままにしてください。
- 基本ゲートでは`streamTo: "parent"`を必須にしないでください。この経路はリクエスター/セッション能力に依存し、別の統合チェックです。
- スレッドバインドされた`mode: "session"`の検証は、実際のDiscordスレッドまたはTelegramトピックからの、より豊かな第2段階の統合パスとして扱ってください。

## サンドボックス互換性

ACPセッションは現在、OpenClawサンドボックス内ではなくホストランタイム上で動作します。

現在の制限:

- リクエスターセッションがサンドボックス化されている場合、ACP起動は`sessions_spawn({ runtime: "acp" })`と`/acp spawn`の両方でブロックされます。
  - エラー: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"`を指定した`sessions_spawn`は`sandbox: "require"`をサポートしません。
  - エラー: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

サンドボックス強制実行が必要な場合は、`runtime: "subagent"`を使ってください。

### `/acp`コマンドから

チャットから明示的な運用制御が必要な場合は、`/acp spawn`を使います。

```text
/acp spawn codex --mode persistent --thread auto
/acp spawn codex --mode oneshot --thread off
/acp spawn codex --bind here
/acp spawn codex --thread here
```

主なフラグ:

- `--mode persistent|oneshot`
- `--bind here|off`
- `--thread auto|here|off`
- `--cwd <absolute-path>`
- `--label <name>`

[Slash Commands](/ja-JP/tools/slash-commands)を参照してください。

## セッション対象解決

ほとんどの`/acp`アクションは、任意のセッション対象（`session-key`、`session-id`、または`session-label`）を受け付けます。

解決順序:

1. 明示的な対象引数（または`/acp steer`の`--session`）
   - まずkeyを試す
   - 次にUUID形式のsession id
   - その後label
2. 現在のスレッドバインディング（この会話/スレッドがACPセッションにバインドされている場合）
3. 現在のリクエスターセッションへのフォールバック

現在の会話バインディングとスレッドバインディングは、どちらも手順2に参加します。

対象が解決できない場合、OpenClawは明確なエラーを返します（`Unable to resolve session target: ...`）。

## 起動バインドモード

`/acp spawn`は`--bind here|off`をサポートします。

| Mode | 挙動 |
| ------ | ---------------------------------------------------------------------- |
| `here` | 現在アクティブな会話をその場でバインドする。アクティブな会話がなければ失敗。 |
| `off`  | 現在の会話バインディングを作成しない。 |

注意:

- `--bind here`は、「このチャネルやチャットをCodex対応にする」ための最も簡単な運用経路です。
- `--bind here`は子スレッドを作成しません。
- `--bind here`は、現在の会話バインド対応を公開しているチャネルでのみ使用できます。
- 同じ`/acp spawn`呼び出しで`--bind`と`--thread`は併用できません。

## 起動スレッドモード

`/acp spawn`は`--thread auto|here|off`をサポートします。

| Mode | 挙動 |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | アクティブなスレッド内ではそのスレッドをバインドする。スレッド外では、サポートされる場合に子スレッドを作成/バインドする。 |
| `here` | 現在アクティブなスレッドを必須とする。スレッド内でなければ失敗。 |
| `off`  | バインドしない。セッションは未バインドで開始される。 |

注意:

- スレッドバインドのないサーフェスでは、デフォルト動作は実質的に`off`です。
- スレッドバインド起動にはチャネルポリシーのサポートが必要です:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- 子スレッドを作らずに現在の会話を固定したい場合は、`--bind here`を使ってください。

## ACP制御

利用可能なコマンドファミリー:

- `/acp spawn`
- `/acp cancel`
- `/acp steer`
- `/acp close`
- `/acp status`
- `/acp set-mode`
- `/acp set`
- `/acp cwd`
- `/acp permissions`
- `/acp timeout`
- `/acp model`
- `/acp reset-options`
- `/acp sessions`
- `/acp doctor`
- `/acp install`

`/acp status`は有効なランタイムオプションを表示し、利用可能な場合はランタイムレベルとバックエンドレベルの両方のsession identifierを表示します。

一部の制御はバックエンド能力に依存します。バックエンドがその制御をサポートしない場合、OpenClawは明確なunsupported-controlエラーを返します。

## ACPコマンド クックブック

| Command | 何をするか | 例 |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn` | ACPセッションを作成する。任意で現在の会話バインドまたはスレッドバインド。 | `/acp spawn codex --bind here --cwd /repo` |
| `/acp cancel` | 対象セッションの進行中ターンをキャンセルする。 | `/acp cancel agent:codex:acp:<uuid>` |
| `/acp steer` | 実行中セッションに追加指示を送る。 | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close` | セッションを閉じてスレッド対象のバインドを解除する。 | `/acp close` |
| `/acp status` | バックエンド、モード、状態、ランタイムオプション、能力を表示する。 | `/acp status` |
| `/acp set-mode` | 対象セッションのランタイムモードを設定する。 | `/acp set-mode plan` |
| `/acp set` | 汎用ランタイム設定オプションを書き込む。 | `/acp set model openai/gpt-5.4` |
| `/acp cwd` | ランタイム作業ディレクトリオーバーライドを設定する。 | `/acp cwd /Users/user/Projects/repo` |
| `/acp permissions` | 承認ポリシープロファイルを設定する。 | `/acp permissions strict` |
| `/acp timeout` | ランタイムタイムアウト（秒）を設定する。 | `/acp timeout 120` |
| `/acp model` | ランタイムモデルオーバーライドを設定する。 | `/acp model anthropic/claude-opus-4-6` |
| `/acp reset-options` | セッションのランタイムオプションオーバーライドを削除する。 | `/acp reset-options` |
| `/acp sessions` | ストアから最近のACPセッションを一覧表示する。 | `/acp sessions` |
| `/acp doctor` | バックエンド健全性、能力、実行可能な修正を表示する。 | `/acp doctor` |
| `/acp install` | 決定的なインストール手順と有効化手順を表示する。 | `/acp install` |

`/acp sessions`は、現在バインドされたセッションまたはリクエスターセッションのストアを読み取ります。`session-key`、`session-id`、または`session-label`トークンを受け付けるコマンドは、agentごとのカスタム`session.store`ルートを含むGatewayセッション探索を通じて対象を解決します。

## ランタイムオプションの対応関係

`/acp`には便利コマンドと汎用setterがあります。

等価な操作:

- `/acp model <id>`はランタイム設定キー`model`に対応します。
- `/acp permissions <profile>`はランタイム設定キー`approval_policy`に対応します。
- `/acp timeout <seconds>`はランタイム設定キー`timeout`に対応します。
- `/acp cwd <path>`はランタイムcwdオーバーライドを直接更新します。
- `/acp set <key> <value>`は汎用経路です。
  - 特別扱い: `key=cwd`はcwdオーバーライド経路を使います。
- `/acp reset-options`は対象セッションのすべてのランタイムオーバーライドをクリアします。

## acpxハーネスサポート（現在）

現在のacpx組み込みハーネスエイリアス:

- `claude`
- `codex`
- `copilot`
- `cursor`（Cursor CLI: `cursor-agent acp`）
- `droid`
- `gemini`
- `iflow`
- `kilocode`
- `kimi`
- `kiro`
- `openclaw`
- `opencode`
- `pi`
- `qwen`

OpenClawがacpxバックエンドを使う場合、acpx設定でカスタムagentエイリアスを定義していない限り、`agentId`にはこれらの値を優先して使ってください。
ローカルのCursorインストールがまだ`agent acp`としてACPを公開している場合は、組み込みデフォルトを変更するのではなく、acpx設定で`cursor` agentコマンドをオーバーライドしてください。

直接のacpx CLI使用では、`--agent <command>`経由で任意adapterも対象にできますが、その生のescape hatchはacpx CLIの機能であり、通常のOpenClaw `agentId`経路ではありません。

## 必要な設定

コアACPベースライン:

```json5
{
  acp: {
    enabled: true,
    // Optional. Default is true; set false to pause ACP dispatch while keeping /acp controls.
    dispatch: { enabled: true },
    backend: "acpx",
    defaultAgent: "codex",
    allowedAgents: [
      "claude",
      "codex",
      "copilot",
      "cursor",
      "droid",
      "gemini",
      "iflow",
      "kilocode",
      "kimi",
      "kiro",
      "openclaw",
      "opencode",
      "pi",
      "qwen",
    ],
    maxConcurrentSessions: 8,
    stream: {
      coalesceIdleMs: 300,
      maxChunkChars: 1200,
    },
    runtime: {
      ttlMinutes: 120,
    },
  },
}
```

スレッドバインド設定はチャネルadapter固有です。Discordの例:

```json5
{
  session: {
    threadBindings: {
      enabled: true,
      idleHours: 24,
      maxAgeHours: 0,
    },
  },
  channels: {
    discord: {
      threadBindings: {
        enabled: true,
        spawnAcpSessions: true,
      },
    },
  },
}
```

スレッドバインドACP起動が動かない場合は、まずadapter feature flagを確認してください。

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

現在の会話バインドでは、子スレッド作成は不要です。必要なのは、アクティブな会話コンテキストと、ACP会話バインドを公開するチャネルadapterです。

[Configuration Reference](/ja-JP/gateway/configuration-reference)を参照してください。

## acpxバックエンド向けpluginセットアップ

新規インストールでは、バンドル済みの`acpx`ランタイムpluginがデフォルトで有効になっているため、通常ACPは手動pluginインストールなしで動作します。

まずは次から始めてください。

```text
/acp doctor
```

`acpx`を無効化した場合、`plugins.allow` / `plugins.deny`で拒否した場合、またはローカル開発checkoutへ切り替えたい場合は、明示的なplugin経路を使ってください。

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

開発中のローカルworkspaceインストール:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

その後、バックエンド健全性を確認します。

```text
/acp doctor
```

### acpxコマンドとバージョン設定

デフォルトでは、バンドル済みacpxバックエンドplugin（`acpx`）はpluginローカルに固定されたバイナリを使います。

1. コマンドは、ACPX pluginパッケージ内のpluginローカル`node_modules/.bin/acpx`がデフォルトです。
2. 期待バージョンは、デフォルトでextension pinに従います。
3. 起動時に、ACPバックエンドは即座にnot-readyとして登録されます。
4. バックグラウンドのensureジョブが`acpx --version`を検証します。
5. pluginローカルバイナリが欠落または不一致の場合、次を実行して再検証します:
   `npm install --omit=dev --no-save acpx@<pinned>`

plugin設定でコマンド/バージョンをオーバーライドできます。

```json
{
  "plugins": {
    "entries": {
      "acpx": {
        "enabled": true,
        "config": {
          "command": "../acpx/dist/cli.js",
          "expectedVersion": "any"
        }
      }
    }
  }
}
```

注意:

- `command`は絶対パス、相対パス、またはコマンド名（`acpx`）を受け付けます。
- 相対パスはOpenClaw workspaceディレクトリから解決されます。
- `expectedVersion: "any"`は厳密なバージョン一致を無効にします。
- `command`がカスタムバイナリ/パスを指す場合、pluginローカルの自動インストールは無効になります。
- バックエンド健全性チェック実行中も、OpenClaw起動は非ブロッキングのままです。

[Plugins](/ja-JP/tools/plugin)を参照してください。

### 依存関係の自動インストール

`npm install -g openclaw`でOpenClawをグローバルインストールすると、acpxランタイム依存関係（プラットフォーム固有バイナリ）はpostinstallフック経由で自動インストールされます。自動インストールに失敗しても、gatewayは通常どおり起動し、不足依存関係は`openclaw acp doctor`を通じて報告されます。

### Plugin tools MCPブリッジ

デフォルトでは、ACPXセッションはOpenClawのplugin登録済みtoolsをACPハーネスへ**公開しません**。

CodexやClaude CodeのようなACP agentsに、memory recall/storeなどのインストール済みOpenClaw plugin toolsを呼ばせたい場合は、専用ブリッジを有効にしてください。

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

これにより行われること:

- `openclaw-plugin-tools`という名前の組み込みMCPサーバーをACPXセッションブートストラップへ注入します。
- インストール済みかつ有効なOpenClaw pluginsによってすでに登録されているplugin toolsを公開します。
- この機能を明示的かつデフォルトオフのまま維持します。

セキュリティと信頼性に関する注意:

- これはACPハーネスのtoolサーフェスを拡張します。
- ACP agentsは、gateway内で既に有効なplugin toolsにのみアクセスできます。
- これは、それらのpluginsがOpenClaw自体で実行されることを許可するのと同じ信頼境界として扱ってください。
- 有効化前にインストール済みpluginsを確認してください。

カスタム`mcpServers`は従来どおり動作します。組み込みplugin-toolsブリッジは、汎用MCPサーバー設定の置き換えではなく、追加のオプトイン利便機能です。

## 権限設定

ACPセッションは非対話的に実行されます。ファイル書き込みやshell実行の権限プロンプトを承認または拒否するためのTTYはありません。acpx pluginは、権限の扱いを制御する2つの設定キーを提供します。

これらのACPXハーネス権限は、OpenClawのexec approvalsとも、Claude CLIの`--permission-mode bypassPermissions`のようなCLI-backendベンダー回避フラグとも別物です。ACPX `approve-all`は、ACPセッションのためのハーネスレベルのbreak-glassスイッチです。

### `permissionMode`

ハーネスagentがプロンプトなしで実行できる操作を制御します。

| Value | 挙動 |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | すべてのファイル書き込みとshell commandを自動承認する。 |
| `approve-reads` | 読み取りのみを自動承認する。書き込みとexecはプロンプトが必要。 |
| `deny-all`      | すべての権限プロンプトを拒否する。 |

### `nonInteractivePermissions`

権限プロンプトを表示すべきだが、対話的TTYが利用できない場合（ACPセッションでは常にそうです）に何が起こるかを制御します。

| Value | 挙動 |
| ------ | ----------------------------------------------------------------- |
| `fail` | `AcpRuntimeError`でセッションを中断する。**（デフォルト）** |
| `deny` | 権限を黙って拒否して続行する（穏やかな劣化）。 |

### 設定

plugin設定経由で設定します。

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

これらの値を変更したらgatewayを再起動してください。

> **重要:** OpenClawは現在、`permissionMode=approve-reads`および`nonInteractivePermissions=fail`をデフォルトとしています。非対話的ACPセッションでは、権限プロンプトを発生させる書き込みまたはexecは、`AcpRuntimeError: Permission prompt unavailable in non-interactive mode`で失敗することがあります。
>
> 権限を制限する必要がある場合は、セッションがクラッシュする代わりに穏やかに劣化するよう、`nonInteractivePermissions`を`deny`に設定してください。

## トラブルシューティング

| Symptom | Likely cause | Fix |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured` | バックエンドpluginが欠落または無効。 | バックエンドpluginをインストールして有効化し、その後`/acp doctor`を実行してください。 |
| `ACP is disabled by policy (acp.enabled=false)` | ACPがグローバルに無効。 | `acp.enabled=true`を設定してください。 |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)` | 通常のスレッドメッセージからのdispatchが無効。 | `acp.dispatch.enabled=true`を設定してください。 |
| `ACP agent "<id>" is not allowed by policy` | agentがallowlistに入っていない。 | 許可された`agentId`を使うか、`acp.allowedAgents`を更新してください。 |
| `Unable to resolve session target: ...` | key/id/labelトークンが不正。 | `/acp sessions`を実行し、正確なkey/labelをコピーして再試行してください。 |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`が、アクティブなバインド可能会話なしで使われた。 | 対象チャット/チャネルへ移動して再試行するか、未バインド起動を使ってください。 |
| `Conversation bindings are unavailable for <channel>.` | adapterに現在の会話へのACPバインド機能がない。 | サポートされる場合は`/acp spawn ... --thread ...`を使うか、トップレベル`bindings[]`を設定するか、サポートされたチャネルへ移動してください。 |
| `--thread here requires running /acp spawn inside an active ... thread` | `--thread here`がスレッド文脈外で使われた。 | 対象スレッドへ移動するか、`--thread auto`/`off`を使ってください。 |
| `Only <user-id> can rebind this channel/conversation/thread.` | 別のユーザーがアクティブなバインド対象を所有している。 | 所有者として再バインドするか、別の会話またはスレッドを使ってください。 |
| `Thread bindings are unavailable for <channel>.` | adapterにスレッドバインド機能がない。 | `--thread off`を使うか、対応adapter/チャネルへ移動してください。 |
| `Sandboxed sessions cannot spawn ACP sessions ...` | ACPランタイムはホスト側であり、リクエスターセッションはサンドボックス化されている。 | サンドボックス化セッションからは`runtime="subagent"`を使うか、非サンドボックスセッションからACP起動を行ってください。 |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...` | ACPランタイムに対して`sandbox="require"`が要求された。 | 必須サンドボックス化には`runtime="subagent"`を使うか、非サンドボックスセッションからACPを`sandbox="inherit"`で使ってください。 |
| バインド済みセッションのACPメタデータが欠落 | 古い/削除済みのACPセッションメタデータ。 | `/acp spawn`で再作成し、その後スレッドを再バインド/フォーカスしてください。 |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` | `permissionMode`が、非対話的ACPセッションで書き込み/execをブロックしている。 | `plugins.entries.acpx.config.permissionMode`を`approve-all`に設定し、gatewayを再起動してください。[権限設定](#permission-configuration)を参照してください。 |
| ACPセッションが少ない出力のまま早期失敗する | 権限プロンプトが`permissionMode`/`nonInteractivePermissions`によりブロックされている。 | gatewayログで`AcpRuntimeError`を確認してください。完全な権限が必要なら`permissionMode=approve-all`、穏やかな劣化には`nonInteractivePermissions=deny`を設定してください。 |
| ACPセッションが作業完了後も無期限に停止したままになる | ハーネスプロセスは終了したが、ACPセッションが完了を報告しなかった。 | `ps aux \| grep acpx`で監視し、古いプロセスを手動でkillしてください。 |
