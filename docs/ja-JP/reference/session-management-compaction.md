---
read_when:
    - session id、トランスクリプトJSONL、またはsessions.jsonのフィールドをデバッグする必要がある場合
    - 自動compactionの動作を変更したり、「pre-compaction」のハウスキーピングを追加したりする場合
    - メモリフラッシュやサイレントなシステムターンを実装したい場合
summary: '詳細解説: セッションストアとトランスクリプト、ライフサイクル、および（自動）compactionの内部構造'
title: セッション管理の詳細解説
x-i18n:
    generated_at: "2026-04-07T04:46:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: e379d624dd7808d3af25ed011079268ce6a9da64bb3f301598884ad4c46ab091
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# セッション管理とcompaction（詳細解説）

このドキュメントでは、OpenClawがセッションをエンドツーエンドでどのように管理するかを説明します。

- **セッションルーティング**（受信メッセージがどのように`sessionKey`へマップされるか）
- **セッションストア**（`sessions.json`）と、そこで追跡される内容
- **トランスクリプトの永続化**（`*.jsonl`）とその構造
- **トランスクリプト衛生**（実行前のプロバイダー固有の修正）
- **コンテキスト制限**（コンテキストウィンドウと追跡トークンの違い）
- **Compaction**（手動 + 自動compaction）と、pre-compaction処理をフックする場所
- **サイレントなハウスキーピング**（例: ユーザーに見える出力を生成すべきでないメモリ書き込み）

まず高レベルの概要を見たい場合は、次から始めてください。

- [/concepts/session](/ja-JP/concepts/session)
- [/concepts/compaction](/ja-JP/concepts/compaction)
- [/concepts/memory](/ja-JP/concepts/memory)
- [/concepts/memory-search](/ja-JP/concepts/memory-search)
- [/concepts/session-pruning](/ja-JP/concepts/session-pruning)
- [/reference/transcript-hygiene](/ja-JP/reference/transcript-hygiene)

---

## ソースオブトゥルース: Gateway

OpenClawは、セッション状態を所有する単一の**Gatewayプロセス**を中心に設計されています。

- UI（macOS app、web Control UI、TUI）は、セッション一覧とトークン数をGatewayに問い合わせるべきです。
- リモートモードでは、セッションファイルはリモートホスト上にあります。「ローカルMac上のファイルを確認しても」、Gatewayが使っている内容は反映されません。

---

## 2つの永続化レイヤー

OpenClawは、セッションを2つのレイヤーで永続化します。

1. **セッションストア（`sessions.json`）**
   - キー/値マップ: `sessionKey -> SessionEntry`
   - 小さく、可変で、編集しやすい（またはエントリを削除しやすい）
   - セッションメタデータ（現在のsession id、最終アクティビティ、トグル、トークンカウンターなど）を追跡する

2. **トランスクリプト（`<sessionId>.jsonl`）**
   - ツリー構造を持つ追記専用トランスクリプト（各エントリは`id` + `parentId`を持つ）
   - 実際の会話 + ツールコール + compactionサマリーを保存する
   - 将来のターンのためにモデルコンテキストを再構築するために使われる

---

## ディスク上の場所

Gatewayホスト上で、agentごとに:

- ストア: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- トランスクリプト: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegramトピックセッション: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClawはこれらを`src/config/sessions.ts`経由で解決します。

---

## ストア保守とディスク制御

セッション永続化には、`sessions.json`とトランスクリプト成果物に対する自動保守制御（`session.maintenance`）があります。

- `mode`: `warn`（デフォルト）または`enforce`
- `pruneAfter`: 古いエントリの経過時間によるカットオフ（デフォルト`30d`）
- `maxEntries`: `sessions.json`内のエントリ上限（デフォルト`500`）
- `rotateBytes`: サイズ超過時に`sessions.json`をローテーションする閾値（デフォルト`10mb`）
- `resetArchiveRetention`: `*.reset.<timestamp>`トランスクリプトアーカイブの保持期間（デフォルト: `pruneAfter`と同じ。`false`でクリーンアップ無効）
- `maxDiskBytes`: オプションのsessionsディレクトリ予算
- `highWaterBytes`: クリーンアップ後の目標値（オプション。デフォルトは`maxDiskBytes`の`80%`）

ディスク予算クリーンアップ（`mode: "enforce"`）の強制順序:

1. 最初に、最も古いアーカイブ済みまたは孤立したトランスクリプト成果物を削除する。
2. それでも目標を超える場合、最も古いセッションエントリとそのトランスクリプトファイルを退避する。
3. 使用量が`highWaterBytes`以下になるまで継続する。

`mode: "warn"`では、OpenClawは想定される退避を報告しますが、ストア/ファイルは変更しません。

必要に応じて保守を実行:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## cronセッションと実行ログ

分離されたcron実行もセッションエントリ/トランスクリプトを作成し、専用の保持制御があります。

- `cron.sessionRetention`（デフォルト`24h`）は、古い分離cron実行セッションをセッションストアから削除します（`false`で無効）。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines`は、`~/.openclaw/cron/runs/<jobId>.jsonl`ファイルを削減します（デフォルト: `2_000_000`バイトと`2000`行）。

---

## セッションキー（`sessionKey`）

`sessionKey`は、どの会話バケットにいるかを識別します（ルーティング + 分離）。

一般的なパターン:

- メイン/ダイレクトチャット（agentごと）: `agent:<agentId>:<mainKey>`（デフォルト`main`）
- グループ: `agent:<agentId>:<channel>:group:<id>`
- ルーム/channel（Discord/Slack）: `agent:<agentId>:<channel>:channel:<id>`または`...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>`（オーバーライドされない限り）

正規ルールは[/concepts/session](/ja-JP/concepts/session)に文書化されています。

---

## セッションid（`sessionId`）

各`sessionKey`は現在の`sessionId`を指します（会話を継続するトランスクリプトファイル）。

経験則:

- **リセット**（`/new`、`/reset`）は、その`sessionKey`に対して新しい`sessionId`を作成します。
- **日次リセット**（デフォルトではGatewayホストのローカル時刻で午前4:00）は、リセット境界を越えた後の次のメッセージで新しい`sessionId`を作成します。
- **アイドル期限切れ**（`session.reset.idleMinutes`またはレガシーな`session.idleMinutes`）は、アイドルウィンドウ後にメッセージが届いたとき、新しい`sessionId`を作成します。日次 + アイドルの両方が設定されている場合、先に期限切れになる方が優先されます。
- **スレッド親forkガード**（`session.parentForkMaxTokens`、デフォルト`100000`）は、親セッションがすでに大きすぎる場合、親トランスクリプトのforkをスキップします。新しいスレッドは新規に開始されます。無効化するには`0`を設定します。

実装詳細: 判定は`src/auto-reply/reply/session.ts`の`initSessionState()`で行われます。

---

## セッションストアスキーマ（`sessions.json`）

ストアの値型は、`src/config/sessions.ts`内の`SessionEntry`です。

主なフィールド（網羅ではありません）:

- `sessionId`: 現在のトランスクリプトid（`sessionFile`が設定されていない限り、ファイル名はこれから導出される）
- `updatedAt`: 最終アクティビティのタイムスタンプ
- `sessionFile`: オプションの明示的トランスクリプトパスオーバーライド
- `chatType`: `direct | group | room`（UIと送信ポリシーに役立つ）
- `provider`, `subject`, `room`, `space`, `displayName`: グループ/channelラベル用メタデータ
- トグル:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy`（セッション単位のオーバーライド）
- モデル選択:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- トークンカウンター（ベストエフォート / プロバイダー依存）:
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: このセッションキーで自動compactionが何回完了したか
- `memoryFlushAt`: 最後のpre-compaction memory flushのタイムスタンプ
- `memoryFlushCompactionCount`: 最後のflushが実行されたときのcompaction count

ストアは安全に編集できますが、権威はGatewayにあります。セッション実行中に、エントリが再書き込みまたは再hydrationされることがあります。

---

## トランスクリプト構造（`*.jsonl`）

トランスクリプトは、`@mariozechner/pi-coding-agent`の`SessionManager`によって管理されます。

ファイルはJSONLです。

- 1行目: セッションヘッダー（`type: "session"`、`id`、`cwd`、`timestamp`、オプションの`parentSession`を含む）
- 以降: `id` + `parentId`を持つセッションエントリ（ツリー）

主なエントリ型:

- `message`: user/assistant/toolResultメッセージ
- `custom_message`: モデルコンテキストに_入る_拡張注入メッセージ（UIから隠せる）
- `custom`: モデルコンテキストに_入らない_拡張状態
- `compaction`: `firstKeptEntryId`と`tokensBefore`を持つ永続化されたcompactionサマリー
- `branch_summary`: ツリーブランチ移動時の永続化サマリー

OpenClawは意図的にトランスクリプトを「修正」しません。Gatewayは、それらの読み書きに`SessionManager`を使います。

---

## コンテキストウィンドウと追跡トークンの違い

重要なのは2つの異なる概念です。

1. **モデルコンテキストウィンドウ**: モデルごとのハード上限（モデルに見えるトークン数）
2. **セッションストアカウンター**: `sessions.json`に書き込まれるローリング統計（`/status`やダッシュボードで使用）

制限を調整する場合:

- コンテキストウィンドウはモデルカタログから取得されます（設定でオーバーライド可能）。
- ストア内の`contextTokens`はランタイムの推定値/報告値です。厳密な保証として扱わないでください。

詳細は[/token-use](/ja-JP/reference/token-use)を参照してください。

---

## Compactionとは何か

Compactionは、古い会話をトランスクリプト内の永続化された`compaction`エントリに要約し、最近のメッセージはそのまま保持します。

compaction後、将来のターンで見えるのは次のものです。

- compactionサマリー
- `firstKeptEntryId`以降のメッセージ

Compactionは**永続的**です（session pruningとは異なります）。[/concepts/session-pruning](/ja-JP/concepts/session-pruning)を参照してください。

## Compactionチャンク境界とツールペアリング

OpenClawが長いトランスクリプトをcompactionチャンクに分割する際、assistantのツールコールと対応する`toolResult`エントリのペアを維持します。

- トークン比率による分割位置がツールコールとその結果の間に来る場合、OpenClawはペアを分離する代わりに、境界をassistantのツールコールメッセージ側へ移動します。
- 末尾のtool-resultブロックがそのままだとチャンクが目標サイズを超える場合、OpenClawはその保留中のツールブロックを維持し、未要約の末尾をそのまま残します。
- 中断/エラーになったツールコールブロックは、保留中の分割を維持しません。

---

## 自動compactionが発生するタイミング（Pi runtime）

埋め込みPi agentでは、自動compactionは次の2つの場合に発火します。

1. **オーバーフロー回復**: モデルがコンテキストオーバーフローエラーを返したとき
   （`request_too_large`、`context length exceeded`、`input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`input is too long for the model`、`ollama error: context length
exceeded`、および同様のプロバイダー依存バリエーション）→ compact → retry。
2. **しきい値保守**: 成功したターンの後、次の条件を満たしたとき:

`contextTokens > contextWindow - reserveTokens`

ここで:

- `contextWindow`はモデルのコンテキストウィンドウ
- `reserveTokens`は、プロンプト + 次のモデル出力のために確保されるヘッドルーム

これらはPi runtimeのセマンティクスです（OpenClawはイベントを消費しますが、いつcompactするかはPiが決めます）。

---

## Compaction設定（`reserveTokens`, `keepRecentTokens`）

Piのcompaction設定は、Pi settingsにあります。

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClawは埋め込み実行に対して安全下限も強制します。

- `compaction.reserveTokens < reserveTokensFloor`なら、OpenClawはそれを引き上げます。
- デフォルトの下限は`20000`トークンです。
- 下限を無効にするには`agents.defaults.compaction.reserveTokensFloor: 0`を設定します。
- すでにそれより高い場合、OpenClawは変更しません。

理由: compactionが避けられなくなる前に、複数ターンにわたる「ハウスキーピング」（メモリ書き込みなど）のための十分なヘッドルームを残すためです。

実装: `src/agents/pi-settings.ts`の`ensurePiCompactionReserveTokens()`
（`src/agents/pi-embedded-runner.ts`から呼び出されます）。

---

## ユーザーに見えるサーフェス

compactionとセッション状態は、次の方法で観察できます。

- `/status`（任意のチャットセッションで）
- `openclaw status`（CLI）
- `openclaw sessions` / `sessions --json`
- verbose mode: `🧹 Auto-compaction complete` + compaction count

---

## サイレントなハウスキーピング（`NO_REPLY`）

OpenClawは、ユーザーに中間出力を見せるべきでないバックグラウンドタスク向けに、「サイレント」ターンをサポートしています。

慣例:

- assistantは、正確なサイレントトークン`NO_REPLY` /
  `no_reply`で出力を開始し、「ユーザーに返信を配信しない」ことを示します。
- OpenClawは、配信レイヤーでこれを除去/抑制します。
- 正確なサイレントトークンの抑制は大文字小文字を区別しないため、ペイロード全体がそのサイレントトークンだけである場合、`NO_REPLY`と
  `no_reply`の両方が対象になります。
- これは真のバックグラウンド/無配信ターン専用であり、
  通常の実行可能なユーザー要求の近道ではありません。

`2026.1.10`以降、OpenClawは部分チャンクが`NO_REPLY`で始まる場合、**draft/typing streaming**も抑制するため、サイレント操作がターン途中で部分出力を漏らしません。

---

## Pre-compaction「memory flush」（実装済み）

目的: 自動compactionが起こる前に、永続状態をディスクへ書き込むサイレントな
agentic turnを実行すること（例: agent workspace内の`memory/YYYY-MM-DD.md`）。これにより、
compactionで重要なコンテキストが失われないようにします。

OpenClawは**pre-threshold flush**アプローチを使います。

1. セッションのコンテキスト使用量を監視する。
2. それが「ソフトしきい値」（Piのcompactionしきい値より低い）を超えたら、サイレントな
   「今すぐメモリを書き込む」指示をagentへ実行する。
3. ユーザーに何も見せないために、正確なサイレントトークン`NO_REPLY` / `no_reply`を使う。

設定（`agents.defaults.compaction.memoryFlush`）:

- `enabled`（デフォルト: `true`）
- `softThresholdTokens`（デフォルト: `4000`）
- `prompt`（flushターン用のユーザーメッセージ）
- `systemPrompt`（flushターン用に追加される追加システムプロンプト）

注意:

- デフォルトのprompt/system promptには、配信を抑制するための
  `NO_REPLY`ヒントが含まれます。
- flushは、compactionサイクルごとに1回実行されます（`sessions.json`で追跡）。
- flushは埋め込みPiセッションでのみ実行されます（CLIバックエンドではスキップ）。
- セッションworkspaceが読み取り専用（`workspaceAccess: "ro"`または`"none"`）の場合、flushはスキップされます。
- workspaceのファイルレイアウトと書き込みパターンについては、[Memory](/ja-JP/concepts/memory)を参照してください。

Piはextension APIで`session_before_compact`フックも公開していますが、OpenClawの
flushロジックは現在Gateway側にあります。

---

## トラブルシューティングチェックリスト

- session keyが違う? [/concepts/session](/ja-JP/concepts/session)から始めて、`/status`内の`sessionKey`を確認してください。
- ストアとトランスクリプトが一致しない? `openclaw status`からGatewayホストとストアパスを確認してください。
- compactionが多すぎる? 次を確認してください:
  - モデルのコンテキストウィンドウ（小さすぎないか）
  - compaction設定（モデルウィンドウに対して`reserveTokens`が高すぎると、早期compactionの原因になります）
  - tool-resultの肥大化: session pruningを有効化/調整する
- サイレントターンが漏れる? 返信が`NO_REPLY`（大文字小文字を区別しない正確なトークン）で始まっていることと、streaming suppression修正を含むビルドであることを確認してください。
