---
read_when:
    - ACP経由でコーディングハーネスを実行する場合
    - メッセージチャンネル上で会話にバインドされたACPセッションをセットアップする場合
    - メッセージチャンネルの会話を永続的なACPセッションにバインドする場合
    - ACPバックエンドとプラグイン配線をトラブルシュートする場合
    - チャットから`/acp`コマンドを運用する場合
summary: Codex、Claude Code、Cursor、Gemini CLI、OpenClaw ACP、その他のハーネスエージェントにACPランタイムセッションを使用する
title: ACPエージェント
x-i18n:
    generated_at: "2026-04-08T02:21:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 71c7c0cdae5247aefef17a0029360950a1c2987ddcee21a1bb7d78c67da52950
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACPエージェント

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/)セッションにより、OpenClawはACPバックエンドプラグインを通じて外部コーディングハーネス（たとえばPi、Claude Code、Codex、Cursor、Copilot、OpenClaw ACP、OpenCode、Gemini CLI、その他のサポートされるACPXハーネス）を実行できます。

OpenClawに平文で「これをCodexで実行して」や「スレッドでClaude Codeを開始して」と依頼した場合、OpenClawはそのリクエストをACPランタイムへルーティングする必要があります（ネイティブのsub-agentランタイムではありません）。各ACPセッションspawnは[background task](/ja-JP/automation/tasks)として追跡されます。

CodexやClaude Codeを、既存のOpenClawチャンネル会話へ外部MCPクライアントとして直接接続したい場合は、
ACPではなく[`openclaw mcp serve`](/cli/mcp)を使用してください。

## どのページを見るべきか

混同しやすい、近い3つのサーフェスがあります:

| したいこと... | 使用するもの | 補足 |
| ---------------------------------------------------------------------------------- | ------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| OpenClawを_通して_ Codex、Claude Code、Gemini CLI、または別の外部ハーネスを実行する | このページ: ACPエージェント | チャットにバインドされたセッション、`/acp spawn`、`sessions_spawn({ runtime: "acp" })`、background task、ランタイム制御 |
| エディターやクライアント向けに、OpenClaw GatewayセッションをACPサーバーとして公開する | [`openclaw acp`](/cli/acp) | ブリッジモード。IDE/クライアントがstdio/WebSocket経由でACPを使ってOpenClawと通信 |
| ローカルAI CLIをテキスト専用のフォールバックモデルとして再利用する | [CLI Backends](/ja-JP/gateway/cli-backends) | ACPではありません。OpenClawツールなし、ACP制御なし、ハーネスランタイムなし |

## これはそのままで動きますか

通常は、はい。

- 新規インストールでは現在、バンドル済み`acpx`ランタイムプラグインがデフォルトで有効です。
- バンドル済み`acpx`プラグインは、プラグインローカルに固定された`acpx`バイナリを優先します。
- 起動時に、OpenClawはそのバイナリをprobeし、必要なら自己修復します。
- 準備状況をすばやく確認したい場合は、まず`/acp doctor`から始めてください。

初回使用時にまだ起こりうること:

- 対象ハーネスアダプターが、そのハーネスを初めて使用するときに`npx`でオンデマンド取得される場合があります。
- そのハーネス用のベンダー認証は、依然としてホスト上に存在している必要があります。
- ホストにnpm/ネットワークアクセスがない場合、初回実行時のアダプター取得は、キャッシュが事前に温められるか、別の方法でアダプターがインストールされるまで失敗することがあります。

例:

- `/acp spawn codex`: OpenClawは`acpx`のブートストラップ準備ができているはずですが、Codex ACPアダプターは初回実行時の取得がまだ必要な場合があります。
- `/acp spawn claude`: Claude ACPアダプターでも同様で、加えてそのホスト上のClaude側認証も必要です。

## 高速なオペレーターフロー

実用的な`/acp`ランブックが欲しいときは、これを使ってください:

1. セッションをspawnします:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. バインドされた会話またはスレッド内で作業します（またはそのセッションキーを明示的に指定します）。
3. ランタイム状態を確認します:
   - `/acp status`
4. 必要に応じてランタイムオプションを調整します:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. コンテキストを置き換えずに、アクティブなセッションへ指示を追加します:
   - `/acp steer tighten logging and continue`
6. 作業を停止します:
   - `/acp cancel`（現在のターンを停止）、または
   - `/acp close`（セッションを閉じてバインディングを削除）

## 人間向けクイックスタート

自然な依頼の例:

- 「このDiscordチャンネルをCodexにバインドして。」
- 「ここでスレッド内に永続的なCodexセッションを開始して、集中させて。」
- 「これをワンショットのClaude Code ACPセッションとして実行して、結果を要約して。」
- 「このiMessageチャットをCodexにバインドして、追加入力も同じworkspaceで続けて。」
- 「このタスクにはGemini CLIをスレッドで使って、その後の追加入力も同じスレッドで続けて。」

OpenClawが行うべきこと:

1. `runtime: "acp"`を選択します。
2. 要求されたハーネスターゲット（`agentId`、たとえば`codex`）を解決します。
3. 現在の会話へのバインドが要求されており、アクティブなチャンネルがそれをサポートしている場合は、ACPセッションをその会話にバインドします。
4. それ以外で、スレッドバインドが要求されており、現在のチャンネルがそれをサポートしている場合は、ACPセッションをそのスレッドにバインドします。
5. フォーカス解除/クローズ/期限切れになるまで、その後のバインド済みメッセージを同じACPセッションへルーティングします。

## ACPとsub-agentの違い

外部ハーネスランタイムが必要な場合はACPを使用します。OpenClawネイティブの委譲実行が必要な場合はsub-agentを使用します。

| 項目 | ACPセッション | sub-agent実行 |
| ------------- | ------------------------------------- | ---------------------------------- |
| ランタイム | ACPバックエンドプラグイン（たとえばacpx） | OpenClawネイティブsub-agentランタイム |
| セッションキー | `agent:<agentId>:acp:<uuid>` | `agent:<agentId>:subagent:<uuid>` |
| 主なコマンド | `/acp ...` | `/subagents ...` |
| Spawnツール | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn`（デフォルトランタイム） |

関連: [Sub-agents](/ja-JP/tools/subagents)

## ACPがClaude Codeを実行する仕組み

ACP経由でClaude Codeを使う場合、スタックは次のとおりです:

1. OpenClaw ACPセッション制御プレーン
2. バンドル済み`acpx`ランタイムプラグイン
3. Claude ACPアダプター
4. Claude側ランタイム/セッション機構

重要な違い:

- ACP Claudeは、ACP制御、セッションresume、background-task追跡、および任意の会話/スレッドバインディングを備えたハーネスセッションです。
- CLIバックエンドは、別のテキスト専用ローカルフォールバックランタイムです。[CLI Backends](/ja-JP/gateway/cli-backends)を参照してください。

オペレーター向けの実用ルールは次のとおりです:

- `/acp spawn`、バインド可能なセッション、ランタイム制御、または永続的なハーネス作業が必要なら: ACPを使う
- raw CLIを通じたシンプルなローカルテキストフォールバックが必要なら: CLI backendsを使う

## バインド済みセッション

### 現在の会話へのバインド

子スレッドを作らずに、現在の会話を永続的なACP workspaceにしたい場合は`/acp spawn <harness> --bind here`を使用します。

動作:

- OpenClawは、チャンネルトランスポート、認証、安全性、配信の所有を維持します。
- 現在の会話は、spawnされたACPセッションキーに固定されます。
- その会話内の追加入力メッセージは、同じACPセッションへルーティングされます。
- `/new`と`/reset`は、同じバインド済みACPセッションをその場でリセットします。
- `/acp close`はセッションを閉じ、現在の会話バインディングを削除します。

実際に意味すること:

- `--bind here`は同じチャットサーフェスを維持します。Discordでは、現在のチャンネルはそのまま現在のチャンネルです。
- 新しい作業をspawnしている場合、`--bind here`でも新しいACPセッションを作成できます。バインドはそのセッションを現在の会話へ接続します。
- `--bind here`は、それ自体では子DiscordスレッドやTelegramトピックを作成しません。
- ACPランタイムは、それ自身の作業ディレクトリ（`cwd`）やバックエンド管理workspaceをディスク上に持つことができます。そのランタイムworkspaceはチャットサーフェスとは別であり、新しいメッセージスレッドを意味するものではありません。
- 別のACPエージェントへspawnし、`--cwd`を渡さない場合、OpenClawはデフォルトでリクエスターのものではなく**対象エージェントの**workspaceを継承します。
- その継承されたworkspaceパスが存在しない場合（`ENOENT`/`ENOTDIR`）、OpenClawは誤ったツリーを黙って再利用するのではなく、バックエンドのデフォルトcwdへフォールバックします。
- 継承されたworkspaceが存在していてもアクセスできない場合（たとえば`EACCES`）、spawnは`cwd`を落とすのではなく実際のアクセスエラーを返します。

メンタルモデル:

- チャットサーフェス: 人が会話を続ける場所（`Discord channel`, `Telegram topic`, `iMessage chat`）
- ACPセッション: OpenClawがルーティングする永続的なCodex/Claude/Geminiランタイム状態
- 子スレッド/トピック: `--thread ...`によってのみ作成される任意の追加メッセージサーフェス
- ランタイムworkspace: ハーネスが実行されるファイルシステム上の場所（`cwd`、リポジトリチェックアウト、バックエンドworkspace）

例:

- `/acp spawn codex --bind here`: このチャットを維持し、Codex ACPセッションをspawnまたは接続し、今後のメッセージをここからそこへルーティングします
- `/acp spawn codex --thread auto`: OpenClawは子スレッド/トピックを作成して、そこへACPセッションをバインドする場合があります
- `/acp spawn codex --bind here --cwd /workspace/repo`: 上と同じチャットバインディングですが、Codexは`/workspace/repo`で実行されます

現在の会話バインディングサポート:

- 現在の会話バインディングサポートを通知するチャット/メッセージチャンネルは、共有の会話バインディング経路を通じて`--bind here`を使用できます。
- 独自のスレッド/トピックセマンティクスを持つチャンネルも、同じ共有インターフェースの裏側でチャンネル固有の正規化を提供できます。
- `--bind here`は常に「現在の会話をその場でバインドする」ことを意味します。
- 汎用の現在会話バインドは、共有のOpenClawバインディングストアを使用し、通常のGateway再起動後も維持されます。

補足:

- `/acp spawn`では`--bind here`と`--thread ...`は相互排他です。
- Discordでは、`--bind here`は現在のチャンネルまたはスレッドをその場でバインドします。`spawnAcpSessions`が必要なのは、`--thread auto|here`のためにOpenClawが子スレッドを作成する必要がある場合だけです。
- アクティブなチャンネルが現在会話のACPバインディングを公開していない場合、OpenClawは明確な未対応メッセージを返します。
- `resume`と「新しいセッション」の質問は、チャンネルの質問ではなくACPセッションの質問です。現在のチャットサーフェスを変えずに、ランタイム状態を再利用または置き換えできます。

### スレッドにバインドされたセッション

チャンネルアダプターでスレッドバインディングが有効な場合、ACPセッションをスレッドへバインドできます:

- OpenClawはスレッドを対象ACPセッションへバインドします。
- そのスレッド内の追加入力メッセージは、バインドされたACPセッションへルーティングされます。
- ACP出力は同じスレッドへ返送されます。
- unfocus/close/archive/idle-timeoutまたはmax-age期限切れでバインディングは削除されます。

スレッドバインディングサポートはアダプター依存です。アクティブなチャンネルアダプターがスレッドバインディングをサポートしていない場合、OpenClawは明確な未対応/利用不可メッセージを返します。

スレッドバインドACPに必要な機能フラグ:

- `acp.enabled=true`
- `acp.dispatch.enabled`はデフォルトでオンです（ACPディスパッチを一時停止するには`false`に設定）
- チャンネルアダプターのACPスレッドspawnフラグを有効化（アダプター固有）
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### スレッド対応チャンネル

- セッション/スレッドバインディング機能を公開する任意のチャンネルアダプター。
- 現在の組み込みサポート:
  - Discordスレッド/チャンネル
  - Telegramトピック（グループ/スーパーグループのフォーラムトピック、およびDMトピック）
- プラグインチャンネルも同じバインディングインターフェースを通じてサポートを追加できます。

## チャンネル固有の設定

非エフェメラルなワークフローでは、最上位の`bindings[]`エントリで永続的なACPバインディングを設定します。

### バインディングモデル

- `bindings[].type="acp"`は永続的なACP会話バインディングを示します。
- `bindings[].match`は対象会話を識別します:
  - Discordチャンネルまたはスレッド: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegramフォーラムトピック: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/グループチャット: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループバインディングには`chat_id:*`または`chat_identifier:*`を推奨します。
  - iMessage DM/グループチャット: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループバインディングには`chat_id:*`を推奨します。
- `bindings[].agentId`は所有するOpenClawエージェントidです。
- 任意のACP上書きは`bindings[].acp`配下に置きます:
  - `mode`（`persistent`または`oneshot`）
  - `label`
  - `cwd`
  - `backend`

### エージェントごとのランタイムデフォルト

`agents.list[].runtime`を使って、エージェントごとに一度ACPデフォルトを定義します:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent`（ハーネスid、たとえば`codex`または`claude`）
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACPバインド済みセッションの上書き優先順位:

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

- OpenClawは、使用前に設定されたACPセッションが存在することを保証します。
- そのチャンネルまたはトピック内のメッセージは、設定されたACPセッションへルーティングされます。
- バインド済み会話では、`/new`と`/reset`は同じACPセッションキーをその場でリセットします。
- 一時的なランタイムバインディング（たとえばthread-focusフローで作成されたもの）は、存在する場合は引き続き適用されます。
- 明示的な`cwd`なしのクロスエージェントACP spawnでは、OpenClawはエージェント設定から対象エージェントworkspaceを継承します。
- 継承されたworkspaceパスが存在しない場合は、バックエンドのデフォルトcwdへフォールバックします。存在するがアクセス失敗する場合は、spawnエラーとして表面化します。

## ACPセッションを開始する（インターフェース）

### `sessions_spawn`から

エージェントターンまたはツール呼び出しからACPセッションを開始するには`runtime: "acp"`を使用します。

```json
{
  "task": "Open the repo and summarize failing tests",
  "runtime": "acp",
  "agentId": "codex",
  "thread": true,
  "mode": "session"
}
```

補足:

- `runtime`のデフォルトは`subagent`なので、ACPセッションでは明示的に`runtime: "acp"`を設定してください。
- `agentId`を省略した場合、設定されていればOpenClawは`acp.defaultAgent`を使用します。
- `mode: "session"`は、永続的なバインド会話を維持するために`thread: true`を必要とします。

インターフェース詳細:

- `task`（必須）: ACPセッションへ送られる初期プロンプト。
- `runtime`（ACPでは必須）: `"acp"`でなければなりません。
- `agentId`（任意）: ACP対象ハーネスid。設定されていれば`acp.defaultAgent`へフォールバックします。
- `thread`（任意、デフォルト`false`）: サポートされる場合にスレッドバインディングフローを要求します。
- `mode`（任意）: `run`（ワンショット）または`session`（永続）。
  - デフォルトは`run`
  - `thread: true`でmode省略時、OpenClawはランタイム経路ごとに永続動作をデフォルトにする場合があります
  - `mode: "session"`は`thread: true`を必要とします
- `cwd`（任意）: 要求するランタイム作業ディレクトリ（バックエンド/ランタイムポリシーによって検証されます）。省略時、ACP spawnは設定されていれば対象エージェントworkspaceを継承します。継承パスが存在しない場合はバックエンドデフォルトへフォールバックし、実際のアクセスエラーはそのまま返されます。
- `label`（任意）: セッション/バナーテキストで使用されるオペレーター向けラベル。
- `resumeSessionId`（任意）: 新しいACPセッションを作成する代わりに既存のACPセッションをresumeします。エージェントは`session/load`経由で会話履歴をreplayします。`runtime: "acp"`が必要です。
- `streamTo`（任意）: `"parent"`は初期ACP実行の進捗サマリーをシステムイベントとしてリクエスターセッションへストリーミングします。
  - 利用可能な場合、受理されたレスポンスには`streamLogPath`が含まれます。これはセッションスコープのJSONLログ（`<sessionId>.acp-stream.jsonl`）を指し、完全なリレー履歴をtailできます。

### 既存セッションをresumeする

新規開始ではなく、以前のACPセッションを継続するには`resumeSessionId`を使います。エージェントは`session/load`経由で会話履歴をreplayするため、以前の完全な文脈を引き継いで再開できます。

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

よくある用途:

- ノートPC上のCodexセッションをスマートフォンへ引き継ぐ — エージェントに中断した場所から再開するよう依頼する
- CLIで対話的に開始したコーディングセッションを、今度はエージェント経由でヘッドレスに継続する
- Gateway再起動やidle timeoutで中断した作業を再開する

補足:

- `resumeSessionId`は`runtime: "acp"`を必要とします — sub-agentランタイムで使用するとエラーを返します。
- `resumeSessionId`は上流ACPの会話履歴を復元します。`thread`と`mode`は、作成する新しいOpenClawセッションに対して通常どおり適用されるため、`mode: "session"`は依然として`thread: true`を必要とします。
- 対象エージェントは`session/load`をサポートしている必要があります（CodexとClaude Codeはサポートしています）。
- セッションIDが見つからない場合、spawnは明確なエラーで失敗します — 新しいセッションへの暗黙フォールバックはありません。

### オペレータースモークテスト

Gatewayデプロイ後に、unitテストが通るだけでなく、ACP spawn
が本当にエンドツーエンドで動作しているかをすばやくlive確認したい場合に使ってください。

推奨ゲート:

1. 対象ホスト上で、デプロイされたGatewayのバージョン/コミットを確認します。
2. デプロイされたソースに、`src/gateway/sessions-patch.ts`内のACP lineage acceptance
   （`subagent:* or acp:* sessions`）が含まれていることを確認します。
3. liveエージェント（たとえば
   `jpclawhq`上の`razor(main)`）への一時的なACPXブリッジセッションを開きます。
4. そのエージェントに、以下で`sessions_spawn`を呼ぶよう依頼します:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - task: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. エージェントが次を報告することを確認します:
   - `accepted=yes`
   - 実際の`childSessionKey`
   - validatorエラーなし
6. 一時的なACPXブリッジセッションをクリーンアップします。

liveエージェントへのプロンプト例:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

補足:

- このスモークテストでは、意図的にスレッドバインドされた永続ACPセッションを検証していない限り、`mode: "run"`を使ってください。
- 基本ゲートでは`streamTo: "parent"`を必須にしないでください。この経路は
  リクエスター/セッション機能に依存し、別のintegrationチェックです。
- スレッドバインドされた`mode: "session"`のテストは、実際のDiscordスレッドまたはTelegramトピックからの、より豊かな第2段階integration
  として扱ってください。

## Sandbox互換性

ACPセッションは現在、OpenClaw sandbox内ではなくホストランタイム上で実行されます。

現在の制限:

- リクエスターセッションがsandbox化されている場合、`sessions_spawn({ runtime: "acp" })`と`/acp spawn`の両方でACP spawnはブロックされます。
  - エラー: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"`を指定した`sessions_spawn`は`sandbox: "require"`をサポートしません。
  - エラー: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

sandboxで強制された実行が必要な場合は`runtime: "subagent"`を使用してください。

### `/acp`コマンドから

チャットから明示的なオペレーター制御が必要な場合は`/acp spawn`を使います。

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

## セッションターゲットの解決

ほとんどの`/acp`アクションは、任意のセッションターゲット（`session-key`、`session-id`、または`session-label`）を受け付けます。

解決順序:

1. 明示的なターゲット引数（または`/acp steer`の`--session`）
   - まずkeyを試す
   - 次にUUID形式のsession id
   - 次にlabel
2. 現在のスレッドバインディング（この会話/スレッドがACPセッションにバインドされている場合）
3. 現在のリクエスターセッションへのフォールバック

現在の会話バインディングとスレッドバインディングの両方が、手順2に参加します。

ターゲットが解決できない場合、OpenClawは明確なエラーを返します（`Unable to resolve session target: ...`）。

## Spawnバインドモード

`/acp spawn`は`--bind here|off`をサポートします。

| モード | 動作 |
| ------ | ---------------------------------------------------------------------- |
| `here` | 現在アクティブな会話をその場でバインドします。アクティブな会話がなければ失敗します。 |
| `off`  | 現在の会話バインディングを作成しません。 |

補足:

- `--bind here`は、「このチャンネルまたはチャットをCodex対応にする」ための最も単純なオペレーターパスです。
- `--bind here`は子スレッドを作成しません。
- `--bind here`は、現在の会話バインディングサポートを公開するチャンネルでのみ利用できます。
- 同じ`/acp spawn`呼び出しで`--bind`と`--thread`は併用できません。

## Spawnスレッドモード

`/acp spawn`は`--thread auto|here|off`をサポートします。

| モード | 動作 |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | アクティブなスレッド内では: そのスレッドをバインドします。スレッド外では: サポートされる場合に子スレッドを作成してバインドします。 |
| `here` | 現在アクティブなスレッドを必須とします。スレッド内でなければ失敗します。 |
| `off`  | バインディングなし。セッションは未バインドで開始されます。 |

補足:

- スレッドバインディングのないサーフェスでは、デフォルト動作は実質的に`off`です。
- スレッドバインドspawnにはチャンネルポリシーのサポートが必要です:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- 子スレッドを作らずに現在の会話を固定したい場合は`--bind here`を使ってください。

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

`/acp status`は有効なランタイムオプションを表示し、利用可能な場合はランタイムレベルとバックエンドレベルの両方のセッション識別子を表示します。

一部の制御はバックエンド機能に依存します。バックエンドが制御をサポートしていない場合、OpenClawは明確なunsupported-controlエラーを返します。

## ACPコマンドクックブック

| コマンド | 何をするか | 例 |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn`         | ACPセッションを作成。任意で現在バインドまたはスレッドバインド。 | `/acp spawn codex --bind here --cwd /repo`                    |
| `/acp cancel`        | 対象セッションの進行中ターンをキャンセル。 | `/acp cancel agent:codex:acp:<uuid>`                          |
| `/acp steer`         | 実行中セッションへsteer指示を送信。 | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | セッションを閉じてスレッドターゲットをunbind。 | `/acp close`                                                  |
| `/acp status`        | バックエンド、モード、状態、ランタイムオプション、機能を表示。 | `/acp status`                                                 |
| `/acp set-mode`      | 対象セッションのランタイムモードを設定。 | `/acp set-mode plan`                                          |
| `/acp set`           | 汎用のランタイム設定オプション書き込み。 | `/acp set model openai/gpt-5.4`                               |
| `/acp cwd`           | ランタイム作業ディレクトリ上書きを設定。 | `/acp cwd /Users/user/Projects/repo`                          |
| `/acp permissions`   | 承認ポリシープロファイルを設定。 | `/acp permissions strict`                                     |
| `/acp timeout`       | ランタイムタイムアウト（秒）を設定。 | `/acp timeout 120`                                            |
| `/acp model`         | ランタイムモデル上書きを設定。 | `/acp model anthropic/claude-opus-4-6`                        |
| `/acp reset-options` | セッションのランタイムオプション上書きを削除。 | `/acp reset-options`                                          |
| `/acp sessions`      | ストアから最近のACPセッションを一覧表示。 | `/acp sessions`                                               |
| `/acp doctor`        | バックエンド健全性、機能、実行可能な修正。 | `/acp doctor`                                                 |
| `/acp install`       | 決定的なインストールと有効化手順を表示。 | `/acp install`                                                |

`/acp sessions`は、現在バインドされているセッションまたはリクエスターセッションのストアを読み取ります。`session-key`、`session-id`、または`session-label`トークンを受け付けるコマンドは、エージェントごとのカスタム`session.store`ルートを含むGatewayセッション検出を通じてターゲットを解決します。

## ランタイムオプションのマッピング

`/acp`には便利コマンドと汎用setterがあります。

等価な操作:

- `/acp model <id>`はランタイム設定キー`model`にマップされます。
- `/acp permissions <profile>`はランタイム設定キー`approval_policy`にマップされます。
- `/acp timeout <seconds>`はランタイム設定キー`timeout`にマップされます。
- `/acp cwd <path>`はランタイムcwd上書きを直接更新します。
- `/acp set <key> <value>`は汎用経路です。
  - 特例: `key=cwd`はcwd上書き経路を使用します。
- `/acp reset-options`は対象セッションのすべてのランタイム上書きをクリアします。

## acpxハーネスサポート（現行）

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

OpenClawがacpxバックエンドを使う場合、acpx設定でカスタムagentエイリアスを定義していない限り、`agentId`にはこれらの値を優先して使用してください。
ローカルのCursorインストールがまだACPを`agent acp`として公開している場合は、組み込みデフォルトを変更するのではなく、acpx設定内で`cursor`エージェントコマンドを上書きしてください。

直接のacpx CLI使用では、`--agent <command>`で任意のアダプターも対象にできますが、このraw escape hatchはacpx CLIの機能であり（通常のOpenClaw `agentId`経路ではありません）。

## 必要な設定

コアACPベースライン:

```json5
{
  acp: {
    enabled: true,
    // 任意。デフォルトはtrue。/acp controlsを維持したままACP dispatchを一時停止するにはfalseに設定します。
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

スレッドバインディング設定はチャンネルアダプター固有です。Discordの例:

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

スレッドバインドACP spawnが動作しない場合は、まずアダプター機能フラグを確認してください:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

現在の会話バインドでは子スレッド作成は不要です。必要なのは、アクティブな会話コンテキストと、ACP会話バインディングを公開するチャンネルアダプターです。

[Configuration Reference](/ja-JP/gateway/configuration-reference)を参照してください。

## acpxバックエンド用プラグインセットアップ

新規インストールにはバンドル済み`acpx`ランタイムプラグインがデフォルトで含まれているため、ACPは通常、
手動でプラグインをインストールしなくても動作します。

まずは次から始めてください:

```text
/acp doctor
```

`acpx`を無効にしている、`plugins.allow` / `plugins.deny`で拒否している、または
ローカルの開発チェックアウトへ切り替えたい場合は、明示的なプラグイン経路を使用してください:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

開発中のローカルworkspaceインストール:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

その後、バックエンド健全性を確認します:

```text
/acp doctor
```

### acpxコマンドとバージョン設定

デフォルトでは、バンドル済みacpxバックエンドプラグイン（`acpx`）はプラグインローカルに固定されたバイナリを使用します:

1. コマンドは、ACPXプラグインパッケージ内のプラグインローカル`node_modules/.bin/acpx`がデフォルトです。
2. 期待バージョンは、拡張機能のpinがデフォルトです。
3. 起動時、ACPバックエンドは即座にnot-readyとして登録されます。
4. バックグラウンドのensureジョブが`acpx --version`を検証します。
5. プラグインローカルバイナリが存在しない、または不一致の場合、次を実行します:
   `npm install --omit=dev --no-save acpx@<pinned>`して再検証します。

プラグイン設定でcommand/versionを上書きできます:

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

補足:

- `command`は絶対パス、相対パス、またはコマンド名（`acpx`）を受け付けます。
- 相対パスはOpenClaw workspaceディレクトリから解決されます。
- `expectedVersion: "any"`は厳密なバージョン一致を無効化します。
- `command`がカスタムバイナリ/パスを指している場合、プラグインローカルの自動インストールは無効になります。
- バックエンド健全性チェック実行中も、OpenClaw起動は非ブロッキングのままです。

[Plugins](/ja-JP/tools/plugin)を参照してください。

### 自動依存関係インストール

`npm install -g openclaw`でOpenClawをグローバルインストールすると、acpx
ランタイム依存関係（プラットフォーム固有バイナリ）はpostinstallフックにより自動インストールされます。自動インストールに失敗しても、gatewayは通常どおり起動し、
不足している依存関係は`openclaw acp doctor`を通じて報告されます。

### プラグインツールMCPブリッジ

デフォルトでは、ACPXセッションはOpenClawに登録されたプラグインツールをACPハーネスへ**公開しません**。

CodexやClaude CodeのようなACPエージェントに、memory recall/storeのような
インストール済みOpenClawプラグインツールを呼ばせたい場合は、
専用ブリッジを有効にしてください:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

これが行うこと:

- `openclaw-plugin-tools`という名前の組み込みMCPサーバーをACPXセッション
  ブートストラップへ注入します。
- インストールされ、有効になっているOpenClaw
  プラグインによってすでに登録されているプラグインツールを公開します。
- この機能を明示的かつデフォルトオフのままに保ちます。

セキュリティと信頼に関する補足:

- これはACPハーネスのツールサーフェスを拡張します。
- ACPエージェントは、gatewayですでに有効なプラグインツールにのみアクセスできます。
- これは、それらのプラグインを
  OpenClaw自体で実行させるのと同じ信頼境界として扱ってください。
- 有効化する前に、インストール済みプラグインを確認してください。

カスタム`mcpServers`は従来どおり引き続き動作します。組み込みのplugin-toolsブリッジは
追加のオプトイン利便機能であり、汎用MCPサーバー設定の置き換えではありません。

### ランタイムタイムアウト設定

バンドル済み`acpx`プラグインは、埋め込みランタイムターンに対してデフォルトで120秒の
タイムアウトを使用します。これにより、Gemini CLIのような低速なハーネスでもACP起動と初期化を完了するのに十分な時間を確保できます。ホストで別の
ランタイム制限が必要な場合は上書きしてください:

```bash
openclaw config set plugins.entries.acpx.config.timeoutSeconds 180
```

この値を変更した後はgatewayを再起動してください。

## 権限設定

ACPセッションは非対話的に実行されます — ファイル書き込みやshell-exec権限プロンプトを承認または拒否するためのTTYはありません。acpxプラグインは、権限処理方法を制御する2つの設定キーを提供します:

これらのACPXハーネス権限は、OpenClaw exec承認とは別物であり、Claude CLI `--permission-mode bypassPermissions`のようなCLI-backendのベンダーバイパスフラグとも別物です。ACPXの`approve-all`は、ACPセッション用のハーネスレベルのブレークグラススイッチです。

### `permissionMode`

ハーネスエージェントが、プロンプトなしでどの操作を実行できるかを制御します。

| 値 | 動作 |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | すべてのファイル書き込みとshellコマンドを自動承認します。 |
| `approve-reads` | 読み取りのみ自動承認します。書き込みとexecはプロンプトが必要です。 |
| `deny-all`      | すべての権限プロンプトを拒否します。 |

### `nonInteractivePermissions`

権限プロンプトが表示されるべきだが、対話的TTYが利用できない場合（ACPセッションでは常にそうです）に何をするかを制御します。

| 値 | 動作 |
| ------ | ----------------------------------------------------------------- |
| `fail` | `AcpRuntimeError`でセッションを中断します。**（デフォルト）** |
| `deny` | 権限を黙って拒否して継続します（穏やかな劣化）。 |

### 設定

プラグイン設定経由で設定します:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

これらの値を変更した後はgatewayを再起動してください。

> **重要:** OpenClawは現在、デフォルトで`permissionMode=approve-reads`および`nonInteractivePermissions=fail`です。
>
> 非対話的ACPセッションでは、権限プロンプトを引き起こす書き込みまたはexecは、`AcpRuntimeError: Permission prompt unavailable in non-interactive mode`で失敗する場合があります。
>
> 権限を制限する必要がある場合は、セッションがクラッシュする代わりに穏やかに劣化するよう、`nonInteractivePermissions`を`deny`に設定してください。

## トラブルシューティング

| 症状 | 原因の可能性 | 修正 |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | バックエンドプラグインがないか無効です。 | バックエンドプラグインをインストールして有効にし、その後`/acp doctor`を実行してください。 |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACPがグローバルに無効です。 | `acp.enabled=true`を設定してください。 |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | 通常のスレッドメッセージからのdispatchが無効です。 | `acp.dispatch.enabled=true`を設定してください。 |
| `ACP agent "<id>" is not allowed by policy`                                 | エージェントがallowlistにありません。 | 許可された`agentId`を使うか、`acp.allowedAgents`を更新してください。 |
| `Unable to resolve session target: ...`                                     | key/id/labelトークンが不正です。 | `/acp sessions`を実行し、正確なkey/labelをコピーして再試行してください。 |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here`が、バインド可能なアクティブ会話なしで使用されました。 | 対象のチャット/チャンネルへ移動して再試行するか、未バインドspawnを使ってください。 |
| `Conversation bindings are unavailable for <channel>.`                      | アダプターに現在会話ACPバインディング機能がありません。 | サポートされる場合は`/acp spawn ... --thread ...`を使う、最上位の`bindings[]`を設定する、またはサポート対象チャンネルへ移動してください。 |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here`がスレッド文脈外で使われました。 | 対象スレッドへ移動するか、`--thread auto`/`off`を使ってください。 |
| `Only <user-id> can rebind this channel/conversation/thread.`               | 別ユーザーがアクティブなバインディングターゲットを所有しています。 | 所有者として再バインドするか、別の会話またはスレッドを使ってください。 |
| `Thread bindings are unavailable for <channel>.`                            | アダプターにスレッドバインディング機能がありません。 | `--thread off`を使うか、サポートされるアダプター/チャンネルへ移動してください。 |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACPランタイムはホスト側です。リクエスターセッションがsandbox化されています。 | sandbox化セッションでは`runtime="subagent"`を使うか、sandbox化されていないセッションからACP spawnを実行してください。 |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACPランタイムに対して`sandbox="require"`が要求されました。 | 必須sandbox化には`runtime="subagent"`を使うか、sandbox化されていないセッションから`sandbox="inherit"`付きACPを使ってください。 |
| Missing ACP metadata for bound session                                      | 古い/削除されたACPセッションメタデータ。 | `/acp spawn`で再作成し、その後スレッドを再バインド/再フォーカスしてください。 |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | `permissionMode`が非対話的ACPセッションで書き込み/execをブロックしています。 | `plugins.entries.acpx.config.permissionMode`を`approve-all`に設定し、gatewayを再起動してください。[権限設定](#permission-configuration)を参照してください。 |
| ACPセッションがほとんど出力なく早期に失敗する | 権限プロンプトが`permissionMode`/`nonInteractivePermissions`でブロックされています。 | `AcpRuntimeError`についてgatewayログを確認してください。完全な権限が必要なら`permissionMode=approve-all`を、穏やかな劣化が必要なら`nonInteractivePermissions=deny`を設定してください。 |
| ACPセッションが作業完了後も無期限に停止したままになる | ハーネスプロセスは終了したが、ACPセッションが完了を報告しませんでした。 | `ps aux \| grep acpx`で監視し、古いプロセスを手動でkillしてください。 |
