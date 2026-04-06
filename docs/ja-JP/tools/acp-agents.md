---
read_when:
    - ACP を通じて coding harness を実行する場合
    - メッセージ channel 上で会話にバインドされた ACP session をセットアップする場合
    - メッセージ channel の会話を永続的な ACP session にバインドする場合
    - ACP backend と plugin 配線のトラブルシューティングを行う場合
    - チャットから /acp コマンドを操作する場合
summary: Codex、Claude Code、Cursor、Gemini CLI、OpenClaw ACP、その他の harness agent 向けに ACP runtime session を使う
title: ACP Agents
x-i18n:
    generated_at: "2026-04-06T03:14:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 302f3fe25b1ffe0576592b6e0ad9e8a5781fa5702b31d508d9ba8908f7df33bd
    source_path: tools/acp-agents.md
    workflow: 15
---

# ACP agents

[Agent Client Protocol (ACP)](https://agentclientprotocol.com/) session を使うと、OpenClaw は ACP backend plugin を通じて外部 coding harness（たとえば Pi、Claude Code、Codex、Cursor、Copilot、OpenClaw ACP、OpenCode、Gemini CLI、その他の対応 ACPX harness）を実行できます。

平文で OpenClaw に「これを Codex で実行して」や「このスレッドで Claude Code を開始して」と依頼した場合、OpenClaw はそのリクエストを ACP runtime にルーティングするべきです（ネイティブ sub-agent runtime ではありません）。各 ACP session の起動は [background task](/ja-JP/automation/tasks) として追跡されます。

Codex や Claude Code を、既存の OpenClaw channel 会話に対して外部 MCP client として直接接続したい場合は、ACP ではなく
[`openclaw mcp serve`](/cli/mcp) を使用してください。

## どのページを見ればよいですか？

混同しやすい近接した surface が 3 つあります:

| したいこと | 使用するもの | 補足 |
| ---------------------------------------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------------------------------------------- |
| OpenClaw を通して Codex、Claude Code、Gemini CLI、または別の外部 harness を実行する | このページ: ACP agents      | チャットにバインドされた session、`/acp spawn`、`sessions_spawn({ runtime: "acp" })`、background task、runtime controls |
| エディターや client 向けに OpenClaw Gateway session を ACP server として公開する      | [`openclaw acp`](/cli/acp) | ブリッジモード。IDE/client は stdio/WebSocket 経由で OpenClaw に ACP で接続します                                          |

## これはそのままですぐ動きますか？

通常は、はい。

- 新規インストールでは、バンドルされた `acpx` runtime plugin がデフォルトで有効です。
- バンドル `acpx` plugin は、plugin ローカルで固定された `acpx` バイナリを優先します。
- 起動時に OpenClaw はそのバイナリをプローブし、必要なら自己修復します。
- 準備状況をすばやく確認したいなら、まず `/acp doctor` を使ってください。

初回利用時に起こり得ること:

- 対象 harness adapter は、その harness を初めて使うときに `npx` でオンデマンド取得されることがあります。
- その harness 用の vendor 認証は、引き続きホスト上に存在している必要があります。
- ホストに npm/ネットワークアクセスがない場合、初回の adapter 取得は、キャッシュを事前に温めるか別の方法で adapter をインストールするまで失敗することがあります。

例:

- `/acp spawn codex`: OpenClaw は `acpx` のブートストラップ準備ができているはずですが、Codex ACP adapter は初回取得が必要なことがあります。
- `/acp spawn claude`: Claude ACP adapter でも同様で、さらにそのホスト側で Claude 認証が必要です。

## 実用的なオペレーターフロー

実践的な `/acp` ランブックが欲しい場合はこれを使ってください:

1. session を起動します:
   - `/acp spawn codex --bind here`
   - `/acp spawn codex --mode persistent --thread auto`
2. バインドされた会話またはスレッドで作業します（またはその session key を明示的に対象にします）。
3. runtime 状態を確認します:
   - `/acp status`
4. 必要に応じて runtime オプションを調整します:
   - `/acp model <provider/model>`
   - `/acp permissions <profile>`
   - `/acp timeout <seconds>`
5. コンテキストを置き換えずにアクティブな session を微調整します:
   - `/acp steer tighten logging and continue`
6. 作業を停止します:
   - `/acp cancel`（現在のターンを停止）、または
   - `/acp close`（session を閉じて binding を削除）

## 人向けクイックスタート

自然な依頼の例:

- 「この Discord channel を Codex にバインドして。」
- 「ここでスレッドに永続的な Codex session を開始して、集中状態を保って。」
- 「これをワンショットの Claude Code ACP session として実行して、結果を要約して。」
- 「この iMessage チャットを Codex にバインドして、後続も同じ workspace で続けて。」
- 「このタスクは Gemini CLI を使ってこのスレッドで実行し、その後のやり取りも同じスレッドで続けて。」

OpenClaw が行うべきこと:

1. `runtime: "acp"` を選びます。
2. 要求された harness target（`agentId`、たとえば `codex`）を解決します。
3. 現在の会話への binding が要求されていて、アクティブな channel がそれをサポートしている場合は、その会話に ACP session をバインドします。
4. そうでなければ、スレッド binding が要求されていて、現在の channel がそれをサポートしている場合は、そのスレッドに ACP session をバインドします。
5. フォーカス解除/クローズ/期限切れになるまで、その後のバインド済みメッセージを同じ ACP session にルーティングします。

## ACP と sub-agents の違い

外部 harness runtime が欲しい場合は ACP を使ってください。OpenClaw ネイティブの委譲実行が欲しい場合は sub-agents を使ってください。

| 項目          | ACP session                           | sub-agent 実行                     |
| ------------- | ------------------------------------- | ---------------------------------- |
| Runtime       | ACP backend plugin（例: acpx）        | OpenClaw ネイティブ sub-agent runtime  |
| Session key   | `agent:<agentId>:acp:<uuid>`          | `agent:<agentId>:subagent:<uuid>`  |
| 主なコマンド | `/acp ...`                            | `/subagents ...`                   |
| 起動 tool     | `sessions_spawn` with `runtime:"acp"` | `sessions_spawn`（デフォルト runtime） |

あわせて [Sub-agents](/ja-JP/tools/subagents) も参照してください。

## ACP が Claude Code を実行する仕組み

ACP 経由で Claude Code を実行する場合、スタックは次のとおりです:

1. OpenClaw ACP session control plane
2. バンドル `acpx` runtime plugin
3. Claude ACP adapter
4. Claude 側の runtime/session 機構

重要な違い:

- ACP Claude は、ACP controls、session resume、background-task tracking、そして任意の会話/スレッド binding を備えた harness session です。
  オペレーターにとっての実践的なルールは次のとおりです:

- `/acp spawn`、バインド可能な session、runtime controls、または永続的な harness 作業が欲しいなら、ACP を使ってください

## バインドされた session

### 現在の会話への binding

現在の会話を子スレッドを作らずに永続的な ACP workspace にしたい場合は、`/acp spawn <harness> --bind here` を使ってください。

動作:

- OpenClaw は引き続き channel transport、認証、安全性、配信を所有します。
- 現在の会話は、起動した ACP session key に固定されます。
- その会話内の後続メッセージは、同じ ACP session にルーティングされます。
- `/new` と `/reset` は同じバインド済み ACP session をその場でリセットします。
- `/acp close` は session を閉じ、現在の会話の binding を削除します。

実際の意味:

- `--bind here` は同じチャット surface を維持します。Discord では、現在の channel はそのまま現在の channel です。
- `--bind here` は、新しい作業を開始している場合には新しい ACP session を作成することがあります。その binding が、その session を現在の会話に接続します。
- `--bind here` 自体は、子 Discord thread や Telegram topic を作成しません。
- ACP runtime 自体は、独自の working directory（`cwd`）や backend 管理 workspace をディスク上に持つことができます。その runtime workspace はチャット surface とは別物であり、新しい messaging thread を意味しません。
- 別の ACP agent へ起動し、`--cwd` を渡さない場合、OpenClaw はデフォルトで要求元ではなく **対象 agent** の workspace を継承します。
- 継承した workspace path が存在しない場合（`ENOENT`/`ENOTDIR`）、OpenClaw は誤った tree を黙って再利用する代わりに backend デフォルトの cwd にフォールバックします。
- 継承した workspace が存在するがアクセスできない場合（たとえば `EACCES`）、起動は `cwd` を捨てずに実際のアクセスエラーを返します。

考え方:

- chat surface: 人が会話を続ける場所（`Discord channel`、`Telegram topic`、`iMessage chat`）
- ACP session: OpenClaw がルーティングする、永続的な Codex/Claude/Gemini runtime 状態
- child thread/topic: `--thread ...` によってのみ作られる任意の追加 messaging surface
- runtime workspace: harness が実行されるファイルシステム上の場所（`cwd`、repo checkout、backend workspace）

例:

- `/acp spawn codex --bind here`: このチャットを維持し、Codex ACP session を起動または接続し、今後のメッセージをここからそこへルーティングします
- `/acp spawn codex --thread auto`: OpenClaw は子 thread/topic を作成し、そこに ACP session をバインドすることがあります
- `/acp spawn codex --bind here --cwd /workspace/repo`: 上と同じチャット binding ですが、Codex は `/workspace/repo` で実行されます

現在の会話 binding のサポート:

- 現在の会話 binding 対応を表明している chat/message channel は、共有 conversation-binding パスを通じて `--bind here` を使えます。
- 独自の thread/topic 意味論を持つ channels でも、同じ共有インターフェースの背後で channel 固有の正規化を提供できます。
- `--bind here` は常に「現在の会話をその場でバインドする」ことを意味します。
- 汎用的な現在会話 binding は、共有 OpenClaw binding store を使い、通常の Gateway 再起動後も維持されます。

注意:

- `/acp spawn` では `--bind here` と `--thread ...` は相互排他的です。
- Discord では、`--bind here` は現在の channel または thread をその場でバインドします。`spawnAcpSessions` が必要なのは、OpenClaw が `--thread auto|here` 用に子 thread を作る必要がある場合だけです。
- アクティブな channel が現在会話 ACP binding を公開していない場合、OpenClaw は明確な unsupported メッセージを返します。
- `resume` や「new session」に関する質問は ACP session に関するものであり、channel に関するものではありません。現在のチャット surface を変えずに runtime 状態を再利用または置き換えられます。

### スレッドにバインドされた session

channel adapter で thread bindings が有効な場合、ACP session はスレッドにバインドできます:

- OpenClaw はスレッドを対象 ACP session にバインドします。
- そのスレッドの後続メッセージは、バインドされた ACP session にルーティングされます。
- ACP 出力は同じスレッドに返送されます。
- unfocus/close/archive/idle-timeout または max-age 期限切れにより binding は削除されます。

thread binding のサポートは adapter ごとです。アクティブな channel adapter が thread binding をサポートしていない場合、OpenClaw は明確な unsupported/unavailable メッセージを返します。

thread-bound ACP に必要な feature flag:

- `acp.enabled=true`
- `acp.dispatch.enabled` はデフォルトで有効です（ACP dispatch を一時停止するには `false` を設定）
- channel-adapter 側の ACP thread-spawn flag を有効化（adapter ごと）
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`

### スレッド対応 channel

- session/thread binding capability を公開している任意の channel adapter
- 現在の組み込みサポート:
  - Discord の threads/channels
  - Telegram の topics（groups/supergroups の forum topics と DM topics）
- plugin channels も同じ binding インターフェースを通じてサポートを追加できます。

## Channel 固有設定

非 ephemeral なワークフローでは、トップレベル `bindings[]` エントリで永続的な ACP binding を設定します。

### Binding モデル

- `bindings[].type="acp"` は永続的な ACP 会話 binding を示します。
- `bindings[].match` は対象会話を識別します:
  - Discord channel または thread: `match.channel="discord"` + `match.peer.id="<channelOrThreadId>"`
  - Telegram forum topic: `match.channel="telegram"` + `match.peer.id="<chatId>:topic:<topicId>"`
  - BlueBubbles DM/group chat: `match.channel="bluebubbles"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループ binding には `chat_id:*` または `chat_identifier:*` を推奨します。
  - iMessage DM/group chat: `match.channel="imessage"` + `match.peer.id="<handle|chat_id:*|chat_guid:*|chat_identifier:*>"`
    安定したグループ binding には `chat_id:*` を推奨します。
- `bindings[].agentId` は所有する OpenClaw agent id です。
- 任意の ACP 上書きは `bindings[].acp` 配下に置きます:
  - `mode`（`persistent` または `oneshot`）
  - `label`
  - `cwd`
  - `backend`

### Agent ごとの runtime デフォルト

agent ごとに一度だけ ACP デフォルトを定義するには `agents.list[].runtime` を使います:

- `agents.list[].runtime.type="acp"`
- `agents.list[].runtime.acp.agent`（harness id、たとえば `codex` または `claude`）
- `agents.list[].runtime.acp.backend`
- `agents.list[].runtime.acp.mode`
- `agents.list[].runtime.acp.cwd`

ACP バインド session の上書き優先順位:

1. `bindings[].acp.*`
2. `agents.list[].runtime.acp.*`
3. グローバル ACP デフォルト（たとえば `acp.backend`）

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

- OpenClaw は、設定された ACP session が利用前に存在することを保証します。
- その channel または topic のメッセージは、設定された ACP session にルーティングされます。
- バインドされた会話では、`/new` と `/reset` は同じ ACP session key をその場でリセットします。
- 一時的な runtime binding（たとえば thread-focus フローで作成されたもの）は、存在する場合には引き続き適用されます。
- 明示的な `cwd` がない cross-agent ACP 起動では、OpenClaw は agent 設定から対象 agent の workspace を継承します。
- 継承した workspace path が存在しない場合は backend デフォルトの cwd にフォールバックし、実際のアクセス失敗は起動エラーとして返します。

## ACP session を開始する（インターフェース）

### `sessions_spawn` から

agent ターンまたは tool 呼び出しから ACP session を開始するには、`runtime: "acp"` を使います。

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

- `runtime` のデフォルトは `subagent` なので、ACP session では明示的に `runtime: "acp"` を設定してください。
- `agentId` を省略した場合、設定されていれば OpenClaw は `acp.defaultAgent` を使います。
- `mode: "session"` は、永続的なバインド会話を維持するために `thread: true` が必要です。

インターフェース詳細:

- `task`（必須）: ACP session に送られる初期プロンプト。
- `runtime`（ACP では必須）: `"acp"` でなければなりません。
- `agentId`（任意）: ACP の対象 harness id。設定されていれば `acp.defaultAgent` にフォールバックします。
- `thread`（任意、デフォルト `false`）: サポートされている場合に thread binding フローを要求します。
- `mode`（任意）: `run`（ワンショット）または `session`（永続）。
  - デフォルトは `run`
  - `thread: true` で mode を省略した場合、runtime パスによっては OpenClaw が永続動作をデフォルトにすることがあります
  - `mode: "session"` には `thread: true` が必要です
- `cwd`（任意）: 要求する runtime working directory（backend/runtime policy により検証されます）。省略時は、設定されていれば ACP 起動は対象 agent workspace を継承します。継承した path が存在しない場合は backend デフォルトへフォールバックし、実際のアクセスエラーは返されます。
- `label`（任意）: session/banner テキストで使われる operator 向けラベル。
- `resumeSessionId`（任意）: 新規作成の代わりに既存 ACP session を再開します。agent は `session/load` を通じて会話履歴を再生します。`runtime: "acp"` が必要です。
- `streamTo`（任意）: `"parent"` を指定すると、初期 ACP 実行の進行要約が system event として要求元 session にストリームされます。
  - 利用可能な場合、受理レスポンスには `streamLogPath` が含まれ、session スコープの JSONL ログ（`<sessionId>.acp-stream.jsonl`）を指します。完全な中継履歴を追尾できます。

### 既存 session の再開

新しく始める代わりに以前の ACP session を継続するには `resumeSessionId` を使います。agent は `session/load` を通じて会話履歴を再生するため、それまでの完全な文脈を引き継いで再開できます。

```json
{
  "task": "Continue where we left off — fix the remaining test failures",
  "runtime": "acp",
  "agentId": "codex",
  "resumeSessionId": "<previous-session-id>"
}
```

一般的な利用例:

- Codex session をノート PC から携帯へ引き継ぐ — 途中までの作業を agent に続けさせる
- CLI で対話的に始めた coding session を、今度は agent 経由で headless に続行する
- Gateway 再起動や idle timeout で中断された作業を再開する

注意:

- `resumeSessionId` には `runtime: "acp"` が必要です。sub-agent runtime で使うとエラーになります。
- `resumeSessionId` は上流 ACP 会話履歴を復元します。一方 `thread` と `mode` は、作成中の新しい OpenClaw session に対して通常どおり適用されるため、`mode: "session"` には引き続き `thread: true` が必要です。
- 対象 agent は `session/load` をサポートしている必要があります（Codex と Claude Code は対応）。
- その session ID が見つからない場合、起動は明確なエラーで失敗します。新しい session への暗黙フォールバックはありません。

### オペレーター向けスモークテスト

Gateway デプロイ後に、ACP 起動が unit test を通るだけでなく
本当に end-to-end で動いているかを手早く live 確認したい場合に使います。

推奨ゲート:

1. 対象ホスト上のデプロイ済み Gateway version/commit を確認します。
2. デプロイ済みソースに、`src/gateway/sessions-patch.ts` 内の ACP lineage acceptance
   （`subagent:* or acp:* sessions`）が含まれていることを確認します。
3. live agent（たとえば `jpclawhq` 上の
   `razor(main)`）への一時的な ACPX bridge session を開きます。
4. その agent に、次の内容で `sessions_spawn` を呼ぶよう依頼します:
   - `runtime: "acp"`
   - `agentId: "codex"`
   - `mode: "run"`
   - task: `Reply with exactly LIVE-ACP-SPAWN-OK`
5. agent が次を報告することを確認します:
   - `accepted=yes`
   - 実在する `childSessionKey`
   - validator error がない
6. 一時的な ACPX bridge session をクリーンアップします。

live agent へのプロンプト例:

```text
Use the sessions_spawn tool now with runtime: "acp", agentId: "codex", and mode: "run".
Set the task to: "Reply with exactly LIVE-ACP-SPAWN-OK".
Then report only: accepted=<yes/no>; childSessionKey=<value or none>; error=<exact text or none>.
```

注意:

- このスモークテストは、意図的に thread-bound 永続 ACP session を
  テストしている場合を除き、`mode: "run"` に保ってください。
- 基本ゲートでは `streamTo: "parent"` を必須にしないでください。このパスは
  requester/session の capability に依存しており、別の統合チェックです。
- thread-bound `mode: "session"` のテストは、実際の Discord thread や Telegram topic からの第 2 段階の、より充実した統合パスとして扱ってください。

## Sandbox 互換性

ACP session は現在、OpenClaw sandbox 内ではなくホスト runtime 上で動作します。

現在の制限:

- 要求元 session が sandboxed の場合、`sessions_spawn({ runtime: "acp" })` と `/acp spawn` の両方で ACP 起動はブロックされます。
  - エラー: `Sandboxed sessions cannot spawn ACP sessions because runtime="acp" runs on the host. Use runtime="subagent" from sandboxed sessions.`
- `runtime: "acp"` を使う `sessions_spawn` は `sandbox: "require"` をサポートしません。
  - エラー: `sessions_spawn sandbox="require" is unsupported for runtime="acp" because ACP sessions run outside the sandbox. Use runtime="subagent" or sandbox="inherit".`

sandbox により強制された実行が必要な場合は `runtime: "subagent"` を使ってください。

### `/acp` コマンドから

チャットから明示的に operator 制御を行いたい場合は `/acp spawn` を使います。

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

[Slash Commands](/ja-JP/tools/slash-commands) を参照してください。

## Session target の解決

多くの `/acp` アクションは任意の session target（`session-key`、`session-id`、または `session-label`）を受け付けます。

解決順序:

1. 明示的な target 引数（または `/acp steer` の `--session`）
   - まず key を試す
   - 次に UUID 形式の session id
   - 次に label
2. 現在の thread binding（この会話/スレッドが ACP session にバインドされている場合）
3. 現在の requester session へのフォールバック

現在の会話 binding と thread binding の両方が、手順 2 に参加します。

target を解決できない場合、OpenClaw は明確なエラー（`Unable to resolve session target: ...`）を返します。

## Spawn の bind モード

`/acp spawn` は `--bind here|off` をサポートします。

| Mode   | 動作 |
| ------ | ---------------------------------------------------------------------- |
| `here` | 現在アクティブな会話をその場でバインドします。アクティブな会話がなければ失敗します。 |
| `off`  | 現在の会話 binding を作成しません。                          |

注意:

- `--bind here` は「この channel または chat を Codex バックにする」ための最も簡単な operator パスです。
- `--bind here` は子スレッドを作成しません。
- `--bind here` は、現在の会話 binding サポートを公開している channel でのみ利用できます。
- `--bind` と `--thread` は同じ `/acp spawn` 呼び出しでは併用できません。

## Spawn の thread モード

`/acp spawn` は `--thread auto|here|off` をサポートします。

| Mode   | 動作 |
| ------ | --------------------------------------------------------------------------------------------------- |
| `auto` | アクティブなスレッド内ではそのスレッドをバインドします。スレッド外では、サポートされていれば子スレッドを作成してバインドします。 |
| `here` | 現在アクティブなスレッドを必須にします。スレッド内でなければ失敗します。                                                  |
| `off`  | binding なし。session は unbound で開始されます。                                                                 |

注意:

- thread binding がない surface では、デフォルト動作は実質的に `off` です。
- thread-bound 起動には channel policy サポートが必要です:
  - Discord: `channels.discord.threadBindings.spawnAcpSessions=true`
  - Telegram: `channels.telegram.threadBindings.spawnAcpSessions=true`
- 子スレッドを作らず現在の会話を固定したい場合は `--bind here` を使ってください。

## ACP controls

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

`/acp status` は有効な runtime オプションを表示し、利用可能な場合は runtime レベルと backend レベルの両方の session 識別子を表示します。

一部の control は backend capability に依存します。backend が control をサポートしていない場合、OpenClaw は明確な unsupported-control エラーを返します。

## ACP コマンド cookbook

| Command              | 動作 | 例 |
| -------------------- | --------------------------------------------------------- | ------------------------------------------------------------- |
| `/acp spawn`         | ACP session を作成します。現在会話への binding または thread binding は任意です。 | `/acp spawn codex --bind here --cwd /repo`                    |
| `/acp cancel`        | 対象 session の進行中ターンをキャンセルします。                 | `/acp cancel agent:codex:acp:<uuid>`                          |
| `/acp steer`         | 実行中 session に steer 指示を送ります。                | `/acp steer --session support inbox prioritize failing tests` |
| `/acp close`         | session を閉じ、thread target との binding を解除します。                  | `/acp close`                                                  |
| `/acp status`        | backend、mode、state、runtime options、capabilities を表示します。 | `/acp status`                                                 |
| `/acp set-mode`      | 対象 session の runtime mode を設定します。                      | `/acp set-mode plan`                                          |
| `/acp set`           | 汎用 runtime config オプションを書き込みます。                      | `/acp set model openai/gpt-5.4`                               |
| `/acp cwd`           | runtime working directory 上書きを設定します。                   | `/acp cwd /Users/user/Projects/repo`                          |
| `/acp permissions`   | approval policy profile を設定します。                              | `/acp permissions strict`                                     |
| `/acp timeout`       | runtime timeout（秒）を設定します。                            | `/acp timeout 120`                                            |
| `/acp model`         | runtime model 上書きを設定します。                               | `/acp model anthropic/claude-opus-4-6`                        |
| `/acp reset-options` | session の runtime option 上書きを削除します。                  | `/acp reset-options`                                          |
| `/acp sessions`      | store から最近の ACP session を一覧表示します。                      | `/acp sessions`                                               |
| `/acp doctor`        | backend の健全性、capabilities、実行可能な修正を表示します。           | `/acp doctor`                                                 |
| `/acp install`       | 決定的な install と有効化手順を表示します。             | `/acp install`                                                |

`/acp sessions` は、現在バインドされている session または requester session の store を読み取ります。`session-key`、`session-id`、または `session-label` を受け付けるコマンドは、agent ごとのカスタム `session.store` ルートを含む gateway session discovery を通じて target を解決します。

## Runtime オプションの対応関係

`/acp` には便利コマンドと汎用 setter があります。

等価な操作:

- `/acp model <id>` は runtime config key `model` に対応します。
- `/acp permissions <profile>` は runtime config key `approval_policy` に対応します。
- `/acp timeout <seconds>` は runtime config key `timeout` に対応します。
- `/acp cwd <path>` は runtime cwd 上書きを直接更新します。
- `/acp set <key> <value>` は汎用パスです。
  - 特別扱い: `key=cwd` は cwd 上書きパスを使います。
- `/acp reset-options` は対象 session のすべての runtime 上書きをクリアします。

## acpx の harness サポート（現在）

現在の acpx 組み込み harness alias:

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

OpenClaw が acpx backend を使う場合、ローカル acpx config にカスタム agent alias が定義されていない限り、`agentId` にはこれらの値を優先して使ってください。
ローカルの Cursor インストールがまだ ACP を `agent acp` として公開している場合は、組み込みデフォルトを変えるのではなく、acpx config 内の `cursor` agent command を上書きしてください。

直接の acpx CLI 利用では `--agent <command>` により任意の adapter も指定できますが、この生の escape hatch は acpx CLI 機能であり、通常の OpenClaw `agentId` パスではありません。

## 必要な設定

コア ACP ベースライン:

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

thread binding 設定は channel adapter ごとです。Discord の例:

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

thread-bound ACP 起動が動かない場合は、まず adapter feature flag を確認してください:

- Discord: `channels.discord.threadBindings.spawnAcpSessions=true`

現在の会話 binding は子スレッド作成を必要としません。必要なのは、アクティブな会話コンテキストと ACP conversation binding を公開する channel adapter です。

[Configuration Reference](/ja-JP/gateway/configuration-reference) を参照してください。

## acpx backend の plugin セットアップ

新規インストールではバンドル `acpx` runtime plugin がデフォルトで有効なため、ACP
は通常、手動で plugin をインストールしなくても動作します。

まず次を実行してください:

```text
/acp doctor
```

`acpx` を無効化している、`plugins.allow` / `plugins.deny` で拒否している、または
ローカル開発 checkout に切り替えたい場合は、明示的な plugin パスを使ってください:

```bash
openclaw plugins install acpx
openclaw config set plugins.entries.acpx.enabled true
```

開発時のローカル workspace install:

```bash
openclaw plugins install ./path/to/local/acpx-plugin
```

その後、backend の健全性を確認します:

```text
/acp doctor
```

### acpx command とバージョン設定

デフォルトでは、バンドル acpx backend plugin（`acpx`）は plugin ローカルで固定されたバイナリを使います:

1. command は ACPX plugin package 内の plugin ローカル `node_modules/.bin/acpx` がデフォルトです。
2. expected version は extension pin がデフォルトです。
3. 起動時に ACP backend は not-ready として即座に登録されます。
4. バックグラウンドの ensure job が `acpx --version` を検証します。
5. plugin ローカルのバイナリがないか不一致の場合、次を実行して再検証します:
   `npm install --omit=dev --no-save acpx@<pinned>`

plugin config で command/version を上書きできます:

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

- `command` には絶対 path、相対 path、または command 名（`acpx`）を指定できます。
- 相対 path は OpenClaw workspace directory から解決されます。
- `expectedVersion: "any"` は厳格なバージョン一致を無効にします。
- `command` がカスタムバイナリ/path を指している場合、plugin ローカルの自動インストールは無効になります。
- backend の健全性チェック実行中も、OpenClaw 起動は非ブロッキングのままです。

[Plugins](/ja-JP/tools/plugin) を参照してください。

### 自動依存関係インストール

`npm install -g openclaw` で OpenClaw をグローバルインストールすると、acpx
runtime 依存関係（プラットフォーム固有バイナリ）は postinstall hook により自動インストールされます。自動インストールに失敗しても、gateway は通常どおり起動し、欠落依存関係は `openclaw acp doctor` を通じて報告されます。

### Plugin tools MCP bridge

デフォルトでは、ACPX session は OpenClaw の plugin 登録 tools を ACP harness に **公開しません**。

Codex や Claude Code のような ACP agent から、memory recall/store のようなインストール済み
OpenClaw plugin tools を呼び出したい場合は、専用 bridge を有効化してください:

```bash
openclaw config set plugins.entries.acpx.config.pluginToolsMcpBridge true
```

これにより行われること:

- `openclaw-plugin-tools` という名前の組み込み MCP server を ACPX session
  bootstrap に注入します。
- インストール済みかつ有効な OpenClaw plugins によってすでに登録されている plugin tools を公開します。
- この機能を明示的なデフォルト off のままに保ちます。

セキュリティと信頼に関する注意:

- これにより ACP harness の tool surface が拡張されます。
- ACP agents がアクセスできるのは、gateway ですでに有効な plugin tools のみです。
- これは、それらの plugins を OpenClaw 自体で実行させるのと同じ信頼境界として扱ってください。
- 有効化する前に、インストール済み plugins を確認してください。

カスタム `mcpServers` は従来どおり動作します。組み込み plugin-tools bridge は、
汎用 MCP server 設定の置き換えではなく、追加の opt-in 便利機能です。

## 権限設定

ACP session は非対話で動作します — ファイル書き込みや shell 実行の権限プロンプトを承認/拒否するための TTY はありません。acpx plugin は、権限の扱いを制御する 2 つの設定キーを提供します:

これらの ACPX harness 権限は、OpenClaw exec approvals とは別物であり、Claude CLI の `--permission-mode bypassPermissions` のような CLI-backend vendor bypass flag とも別物です。ACPX の `approve-all` は、ACP session 用の harness レベルの緊急スイッチです。

### `permissionMode`

harness agent がプロンプトなしで実行できる操作を制御します。

| Value           | 動作 |
| --------------- | --------------------------------------------------------- |
| `approve-all`   | すべてのファイル書き込みと shell command を自動承認します。          |
| `approve-reads` | 読み取りのみ自動承認します。書き込みと exec はプロンプトが必要です。 |
| `deny-all`      | すべての権限プロンプトを拒否します。                              |

### `nonInteractivePermissions`

権限プロンプトを表示すべきだが対話 TTY が利用できない場合（ACP session では常にそうです）にどうするかを制御します。

| Value  | 動作 |
| ------ | ----------------------------------------------------------------- |
| `fail` | `AcpRuntimeError` で session を中断します。**（デフォルト）**           |
| `deny` | 権限を黙って拒否して続行します（段階的劣化）。 |

### 設定

plugin config 経由で設定します:

```bash
openclaw config set plugins.entries.acpx.config.permissionMode approve-all
openclaw config set plugins.entries.acpx.config.nonInteractivePermissions fail
```

これらの値を変更した後は gateway を再起動してください。

> **重要:** OpenClaw は現在、デフォルトで `permissionMode=approve-reads` と `nonInteractivePermissions=fail` を使います。非対話 ACP session では、権限プロンプトを発生させる書き込みまたは exec は `AcpRuntimeError: Permission prompt unavailable in non-interactive mode` で失敗することがあります。
>
> 権限を制限する必要がある場合は、session がクラッシュする代わりに段階的劣化するよう `nonInteractivePermissions` を `deny` に設定してください。

## トラブルシューティング

| Symptom                                                                     | Likely cause                                                                    | Fix                                                                                                                                                               |
| --------------------------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ACP runtime backend is not configured`                                     | backend plugin が欠落しているか無効です。                                             | backend plugin をインストールして有効化し、その後 `/acp doctor` を実行してください。                                                                                                        |
| `ACP is disabled by policy (acp.enabled=false)`                             | ACP がグローバルに無効です。                                                          | `acp.enabled=true` を設定してください。                                                                                                                                           |
| `ACP dispatch is disabled by policy (acp.dispatch.enabled=false)`           | 通常の thread message からの dispatch が無効です。                                  | `acp.dispatch.enabled=true` を設定してください。                                                                                                                                  |
| `ACP agent "<id>" is not allowed by policy`                                 | agent が allowlist に含まれていません。                                                         | 許可された `agentId` を使うか、`acp.allowedAgents` を更新してください。                                                                                                              |
| `Unable to resolve session target: ...`                                     | key/id/label token が不正です。                                                         | `/acp sessions` を実行し、正確な key/label をコピーして再試行してください。                                                                                                                 |
| `--bind here requires running /acp spawn inside an active ... conversation` | `--bind here` が、バインド可能なアクティブ会話なしで使われました。                     | 対象の chat/channel に移動して再試行するか、unbound 起動を使用してください。                                                                                                  |
| `Conversation bindings are unavailable for <channel>.`                      | adapter に現在会話 ACP binding capability がありません。                      | サポートされていれば `/acp spawn ... --thread ...` を使うか、トップレベル `bindings[]` を設定するか、対応 channel へ移動してください。                                              |
| `--thread here requires running /acp spawn inside an active ... thread`     | `--thread here` が thread コンテキスト外で使われました。                                  | 対象 thread に移動するか、`--thread auto`/`off` を使ってください。                                                                                                               |
| `Only <user-id> can rebind this channel/conversation/thread.`               | 別のユーザーが現在の binding target を所有しています。                                    | 所有者として再バインドするか、別の会話または thread を使ってください。                                                                                                        |
| `Thread bindings are unavailable for <channel>.`                            | adapter に thread binding capability がありません。                                        | `--thread off` を使うか、対応 adapter/channel に移動してください。                                                                                                          |
| `Sandboxed sessions cannot spawn ACP sessions ...`                          | ACP runtime はホスト側であり、要求元 session は sandboxed です。                       | sandboxed session からは `runtime="subagent"` を使うか、非 sandboxed session から ACP 起動を実行してください。                                                                  |
| `sessions_spawn sandbox="require" is unsupported for runtime="acp" ...`     | ACP runtime に対して `sandbox="require"` が要求されました。                                  | 必須 sandbox 化には `runtime="subagent"` を使うか、非 sandboxed session から `sandbox="inherit"` で ACP を使ってください。                                               |
| バインドされた session に対する ACP metadata が欠落している                                      | ACP session metadata が古いか削除されています。                                             | `/acp spawn` で再作成し、その後 thread を再バインド/再フォーカスしてください。                                                                                                             |
| `AcpRuntimeError: Permission prompt unavailable in non-interactive mode`    | 非対話 ACP session で `permissionMode` が書き込み/exec をブロックしています。             | `plugins.entries.acpx.config.permissionMode` を `approve-all` に設定し、gateway を再起動してください。[権限設定](#permission-configuration) を参照してください。                 |
| ACP session がほとんど出力しないまま早期に失敗する                                  | 権限プロンプトが `permissionMode`/`nonInteractivePermissions` によりブロックされています。 | gateway logs で `AcpRuntimeError` を確認してください。完全権限が必要なら `permissionMode=approve-all` を、段階的劣化には `nonInteractivePermissions=deny` を設定してください。 |
| 作業完了後も ACP session が無期限に停止したままになる                       | harness process は終了したが、ACP session が完了を報告しませんでした。             | `ps aux \| grep acpx` で監視し、古い process は手動で kill してください。                                                                                                |
