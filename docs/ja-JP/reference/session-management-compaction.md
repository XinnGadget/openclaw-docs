---
read_when:
    - session ids、transcript JSONL、またはsessions.jsonフィールドをデバッグする必要がある
    - auto-compactionの挙動を変更する、または「pre-compaction」housekeepingを追加する
    - memory flushやsilent system turnsを実装したい
summary: '詳細解説: セッションストアとtranscripts、ライフサイクル、（自動）compactionの内部動作'
title: セッション管理の詳細解説
x-i18n:
    generated_at: "2026-04-06T03:13:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0d8c2d30be773eac0424f7a4419ab055fdd50daac8bc654e7d250c891f2c3b8
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# セッション管理とCompaction（詳細解説）

このドキュメントでは、OpenClawがセッションをエンドツーエンドでどのように管理するかを説明します。

- **セッションルーティング**（受信メッセージがどのように`sessionKey`へ対応付けられるか）
- **セッションストア**（`sessions.json`）と、そこで追跡される内容
- **Transcriptの永続化**（`*.jsonl`）とその構造
- **Transcript hygiene**（実行前のプロバイダー固有修正）
- **コンテキスト制限**（コンテキストウィンドウと追跡トークン）
- **Compaction**（手動 + 自動compaction）と、pre-compaction作業をどこにフックするか
- **サイレントhousekeeping**（たとえば、ユーザーに見える出力を生成すべきでないmemory書き込み）

まずより高レベルの概要が必要な場合は、次から始めてください。

- [/concepts/session](/ja-JP/concepts/session)
- [/concepts/compaction](/ja-JP/concepts/compaction)
- [/concepts/memory](/ja-JP/concepts/memory)
- [/concepts/memory-search](/ja-JP/concepts/memory-search)
- [/concepts/session-pruning](/ja-JP/concepts/session-pruning)
- [/reference/transcript-hygiene](/ja-JP/reference/transcript-hygiene)

---

## 信頼できる唯一の情報源: Gateway

OpenClawは、セッション状態を所有する単一の**Gatewayプロセス**を中心に設計されています。

- UI（macOSアプリ、web Control UI、TUI）は、セッション一覧とトークン数をGatewayへ問い合わせるべきです。
- リモートモードでは、セッションファイルはリモートホスト上にあります。「ローカルMac上のファイルを確認する」だけでは、Gatewayが実際に使っている内容は反映されません。

---

## 2つの永続化レイヤー

OpenClawは、セッションを2つのレイヤーで永続化します。

1. **セッションストア（`sessions.json`）**
   - キー/値マップ: `sessionKey -> SessionEntry`
   - 小さく、可変で、編集（またはエントリ削除）が安全
   - セッションメタデータ（現在のsession id、最終アクティビティ、トグル、トークンカウンターなど）を追跡

2. **Transcript（`<sessionId>.jsonl`）**
   - ツリー構造を持つ追記専用Transcript（エントリには`id` + `parentId`がある）
   - 実際の会話 + tool calls + compaction summariesを保存
   - 将来のターンのためにモデルコンテキストを再構築するために使用

---

## ディスク上の場所

Gatewayホスト上で、agentごとに:

- ストア: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transcripts: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegramトピックセッション: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClawは`src/config/sessions.ts`経由でこれらを解決します。

---

## ストア保守とディスク制御

セッション永続化には、`sessions.json`とtranscript artifact向けの自動保守制御（`session.maintenance`）があります。

- `mode`: `warn`（デフォルト）または`enforce`
- `pruneAfter`: 古いエントリの期限切れカットオフ（デフォルト`30d`）
- `maxEntries`: `sessions.json`内のエントリ上限（デフォルト`500`）
- `rotateBytes`: `sessions.json`が大きすぎるときにローテート（デフォルト`10mb`）
- `resetArchiveRetention`: `*.reset.<timestamp>` transcript archivesの保持期間（デフォルト: `pruneAfter`と同じ。`false`でクリーンアップ無効化）
- `maxDiskBytes`: 任意のsessionsディレクトリ予算
- `highWaterBytes`: クリーンアップ後の任意の目標値（デフォルトは`maxDiskBytes`の`80%`）

ディスク予算クリーンアップ（`mode: "enforce"`）の適用順序:

1. 最初に、もっとも古いアーカイブ済みまたは孤立したtranscript artifactsを削除します。
2. それでも目標を超える場合は、もっとも古いセッションエントリとそれに対応するtranscript filesを退避削除します。
3. 使用量が`highWaterBytes`以下になるまで継続します。

`mode: "warn"`では、OpenClawは潜在的な退避削除を報告しますが、ストア/ファイルは変更しません。

必要に応じて保守を実行:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Cronセッションと実行ログ

分離されたcron実行もセッションエントリ/transcriptsを作成し、それらには専用の保持制御があります。

- `cron.sessionRetention`（デフォルト`24h`）は、古い分離cron実行セッションをセッションストアから削除します（`false`で無効化）。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`は`~/.openclaw/cron/runs/<jobId>.jsonl` filesを削減します（デフォルト: `2_000_000` bytesおよび`2000` lines）。

---

## セッションキー（`sessionKey`）

`sessionKey`は、どの_会話バケット_にいるかを識別します（ルーティング + 分離）。

一般的なパターン:

- メイン/ダイレクトチャット（agentごと）: `agent:<agentId>:<mainKey>`（デフォルト`main`）
- グループ: `agent:<agentId>:<channel>:group:<id>`
- ルーム/チャネル（Discord/Slack）: `agent:<agentId>:<channel>:channel:<id>`または`...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>`（上書きされない限り）

正式なルールは[/concepts/session](/ja-JP/concepts/session)に記載されています。

---

## セッションid（`sessionId`）

各`sessionKey`は現在の`sessionId`（会話を継続するtranscript file）を指します。

経験則:

- **リセット**（`/new`、`/reset`）は、その`sessionKey`に対して新しい`sessionId`を作成します。
- **日次リセット**（デフォルトではGatewayホストのローカル時刻で午前4:00）は、リセット境界を越えた後の次のメッセージで新しい`sessionId`を作成します。
- **アイドル期限切れ**（`session.reset.idleMinutes`またはレガシーな`session.idleMinutes`）は、アイドル期間経過後にメッセージが到着したとき、新しい`sessionId`を作成します。日次とアイドルの両方が設定されている場合、先に期限切れになった方が優先されます。
- **スレッド親forkガード**（`session.parentForkMaxTokens`、デフォルト`100000`）は、親セッションがすでに大きすぎる場合に親transcriptのforkをスキップします。新しいスレッドは新規開始になります。無効にするには`0`を設定してください。

実装の詳細: この判定は`src/auto-reply/reply/session.ts`の`initSessionState()`で行われます。

---

## セッションストアスキーマ（`sessions.json`）

ストアの値型は`src/config/sessions.ts`内の`SessionEntry`です。

主なフィールド（網羅ではありません）:

- `sessionId`: 現在のtranscript id（`sessionFile`が設定されていない限り、ファイル名はこれから導出される）
- `updatedAt`: 最終アクティビティのタイムスタンプ
- `sessionFile`: 任意の明示的transcript path override
- `chatType`: `direct | group | room`（UIと送信ポリシーの助けになる）
- `provider`, `subject`, `room`, `space`, `displayName`: グループ/チャネルラベリング用メタデータ
- トグル:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy`（セッション単位のoverride）
- モデル選択:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- トークンカウンター（ベストエフォート / プロバイダー依存）:
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: そのsession keyで自動compactionが何回完了したか
- `memoryFlushAt`: 最後のpre-compaction memory flushのタイムスタンプ
- `memoryFlushCompactionCount`: 最後のflushが実行されたときのcompaction count

ストアは安全に編集できますが、権威を持つのはGatewayです。セッション実行中にエントリを書き換えたり再生成したりすることがあります。

---

## Transcript構造（`*.jsonl`）

Transcriptsは`@mariozechner/pi-coding-agent`の`SessionManager`によって管理されます。

ファイルはJSONLです。

- 1行目: セッションヘッダー（`type: "session"`、`id`、`cwd`、`timestamp`、任意の`parentSession`を含む）
- その後: `id` + `parentId`を持つセッションエントリ（ツリー）

注目すべきエントリ型:

- `message`: user/assistant/toolResultメッセージ
- `custom_message`: 拡張によって注入されるメッセージで、モデルコンテキストには_入る_（UIから隠すことは可能）
- `custom`: モデルコンテキストには入らない拡張状態
- `compaction`: `firstKeptEntryId`と`tokensBefore`を持つ永続化されたcompaction summary
- `branch_summary`: ツリーブランチ移動時の永続化されたsummary

OpenClawは意図的にTranscriptを**修正しません**。Gatewayは、それらの読み書きに`SessionManager`を使います。

---

## コンテキストウィンドウと追跡トークン

重要なのは、2つの異なる概念です。

1. **モデルコンテキストウィンドウ**: モデルごとのハード上限（モデルに見えるトークン）
2. **セッションストアカウンター**: `sessions.json`に書き込まれるローリング統計（`/status`やダッシュボードで使用）

制限を調整する場合:

- コンテキストウィンドウはモデルカタログから取得されます（configでoverride可能です）。
- ストア内の`contextTokens`は実行時の推定/報告値です。厳密な保証として扱わないでください。

詳細は[/token-use](/ja-JP/reference/token-use)を参照してください。

---

## Compaction: それが何か

Compactionは、古い会話をtranscript内の永続化された`compaction`エントリへ要約し、最近のメッセージはそのまま保持します。

compaction後、将来のターンで見えるのは次の内容です。

- compaction summary
- `firstKeptEntryId`以降のメッセージ

Compactionは**永続的**です（session pruningとは異なります）。[/concepts/session-pruning](/ja-JP/concepts/session-pruning)を参照してください。

## Compactionチャンク境界とtoolペアリング

OpenClawが長いtranscriptをcompactionチャンクに分割するときは、
assistantのtool callsと対応する`toolResult`エントリのペアを維持します。

- トークン比率による分割位置がtool callとその結果の間に落ちた場合、OpenClawは
  ペアを分離する代わりに、境界をassistantのtool-call messageまで移動します。
- 末尾のtool-resultブロックによってチャンクが目標サイズを超える場合でも、
  OpenClawはその保留中toolブロックを保持し、未要約の末尾をそのまま維持します。
- 中断/エラーになったtool-callブロックは、保留中分割を維持しません。

---

## auto-compactionが発生するタイミング（Pi runtime）

組み込みPi agentでは、自動compactionは次の2つの場合にトリガーされます。

1. **オーバーフロー回復**: モデルがコンテキストオーバーフローエラーを返す
   （`request_too_large`、`context length exceeded`、`input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`input is too long for the model`、`ollama error: context length
exceeded`、および類似のプロバイダー形状バリアント）→ compact → retry。
2. **しきい値保守**: 成功したターンの後、次の条件を満たしたとき:

`contextTokens > contextWindow - reserveTokens`

ここで:

- `contextWindow`はモデルのコンテキストウィンドウ
- `reserveTokens`は、プロンプト + 次のモデル出力のために予約されたヘッドルーム

これらはPi runtimeの意味論です（OpenClawはイベントを消費しますが、compactするタイミングを決めるのはPiです）。

---

## Compaction設定（`reserveTokens`, `keepRecentTokens`）

Piのcompaction設定はPi settingsにあります。

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClawは、組み込み実行に対して安全下限も強制します。

- `compaction.reserveTokens < reserveTokensFloor`の場合、OpenClawはそれを引き上げます。
- デフォルト下限は`20000`トークンです。
- 下限を無効化するには、`agents.defaults.compaction.reserveTokensFloor: 0`を設定してください。
- すでにそれより高い場合、OpenClawはそのままにします。

理由: compactionが避けられなくなる前に、複数ターンの「housekeeping」（たとえばmemory書き込み）に十分なヘッドルームを残すためです。

実装: `src/agents/pi-settings.ts`の`ensurePiCompactionReserveTokens()`
（`src/agents/pi-embedded-runner.ts`から呼び出されます）。

---

## ユーザー向けの可視surface

compactionとセッション状態は次で確認できます。

- `/status`（任意のチャットセッション内）
- `openclaw status`（CLI）
- `openclaw sessions` / `sessions --json`
- 詳細モード: `🧹 Auto-compaction complete` + compaction count

---

## サイレントhousekeeping（`NO_REPLY`）

OpenClawは、ユーザーに中間出力を見せるべきでないバックグラウンドタスク向けに「サイレント」ターンをサポートします。

慣例:

- assistantは、`NO_REPLY` /
  `no_reply`という完全一致のサイレントトークンで出力を開始し、「ユーザーに返信を配信しない」ことを示します。
- OpenClawは配信レイヤーでこれを削除/抑制します。
- 完全一致のサイレントトークン抑制は大文字小文字を区別しないため、payload全体がそのサイレントトークンだけである場合、`NO_REPLY`と
  `no_reply`の両方が有効です。
- これは、本当にバックグラウンド/無配信のターン専用です。通常の実行可能なユーザー要求の近道ではありません。

`2026.1.10`以降、OpenClawはpartial chunkが`NO_REPLY`で始まる場合、
**draft/typing streaming**も抑制します。これにより、サイレント操作がターン途中で部分出力を漏らすことを防ぎます。

---

## pre-compaction「memory flush」（実装済み）

目的: auto-compactionが起きる前に、永続状態をディスクへ書き込む
サイレントなagentic turnを実行します（たとえばagent workspace内の`memory/YYYY-MM-DD.md`）。これにより、compactionによって重要なコンテキストが消えないようにします。

OpenClawは**pre-threshold flush**アプローチを使用します。

1. セッションのコンテキスト使用量を監視します。
2. それが「ソフトしきい値」（Piのcompactionしきい値より低い）を超えたら、サイレントな
   「今すぐmemoryを書き込む」指示をagentへ実行します。
3. ユーザーに何も見せないよう、完全一致のサイレントトークン`NO_REPLY` / `no_reply`を使用します。

設定（`agents.defaults.compaction.memoryFlush`）:

- `enabled`（デフォルト: `true`）
- `softThresholdTokens`（デフォルト: `4000`）
- `prompt`（flush turn用のuser message）
- `systemPrompt`（flush turn用に追加される追加system prompt）

注意:

- デフォルトのprompt/system promptには、配信を抑制するための`NO_REPLY`ヒントが含まれます。
- flushはcompactionサイクルごとに1回だけ実行されます（`sessions.json`で追跡）。
- flushは組み込みPiセッションでのみ実行されます。
- セッションworkspaceが読み取り専用（`workspaceAccess: "ro"`または`"none"`）の場合、flushはスキップされます。
- workspace file layoutと書き込みパターンについては、[Memory](/ja-JP/concepts/memory)を参照してください。

Piは拡張APIで`session_before_compact` hookも公開していますが、OpenClawの
flushロジックは現在Gateway側にあります。

---

## トラブルシューティングチェックリスト

- Session keyが間違っている? まず[/concepts/session](/ja-JP/concepts/session)から始めて、`/status`内の`sessionKey`を確認してください。
- ストアとtranscriptが一致しない? Gatewayホストと、`openclaw status`から取得したストアパスを確認してください。
- compactionが多すぎる? 次を確認してください:
  - モデルコンテキストウィンドウ（小さすぎる）
  - compaction設定（モデルウィンドウに対して`reserveTokens`が高すぎると、早すぎるcompactionの原因になることがあります）
  - tool-resultの肥大化: session pruningを有効化/調整する
- サイレントターンが漏れる? 返信が`NO_REPLY`で始まっていること（大文字小文字を区別しない完全一致トークン）と、streaming suppression fixを含むビルドであることを確認してください。
