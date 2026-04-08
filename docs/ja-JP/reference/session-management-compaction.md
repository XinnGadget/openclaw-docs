---
read_when:
    - session id、transcript JSONL、または sessions.json フィールドをデバッグする必要がある場合
    - 自動 compaction の動作を変更する場合、または「pre-compaction」のハウスキーピングを追加する場合
    - メモリ flush や silent system turn を実装したい場合
summary: セッションストア + transcript、ライフサイクル、（自動）compaction 内部実装の詳細解説
title: Session Management Deep Dive
x-i18n:
    generated_at: "2026-04-08T02:19:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: cb1a4048646486693db8943a9e9c6c5bcb205f0ed532b34842de3d0346077454
    source_path: reference/session-management-compaction.md
    workflow: 15
---

# Session Management & Compaction（詳細解説）

このドキュメントでは、OpenClaw がセッションをエンドツーエンドでどのように管理するかを説明します。

- **セッションルーティング**（受信メッセージがどのように `sessionKey` に対応付けられるか）
- **セッションストア**（`sessions.json`）と、そこで追跡される内容
- **Transcript の永続化**（`*.jsonl`）とその構造
- **Transcript hygiene**（実行前の provider 固有 fixup）
- **コンテキスト制限**（コンテキストウィンドウと追跡トークンの違い）
- **Compaction**（手動 + 自動 compaction）と、pre-compaction 処理をフックする場所
- **サイレントなハウスキーピング**（例: ユーザーに見える出力を生成すべきでないメモリ書き込み）

まず高レベルの概要を確認したい場合は、次から始めてください。

- [/concepts/session](/ja-JP/concepts/session)
- [/concepts/compaction](/ja-JP/concepts/compaction)
- [/concepts/memory](/ja-JP/concepts/memory)
- [/concepts/memory-search](/ja-JP/concepts/memory-search)
- [/concepts/session-pruning](/ja-JP/concepts/session-pruning)
- [/reference/transcript-hygiene](/ja-JP/reference/transcript-hygiene)

---

## 信頼できる唯一の情報源: Gateway

OpenClaw は、セッション状態を所有する単一の **Gateway プロセス** を中心に設計されています。

- UI（macOS app、web Control UI、TUI）は、セッション一覧とトークン数を Gateway に問い合わせるべきです。
- リモートモードでは、セッションファイルはリモートホスト上にあります。「ローカル Mac 上のファイルを確認する」だけでは、Gateway が実際に使っている内容は反映されません。

---

## 2 つの永続化レイヤー

OpenClaw はセッションを 2 層で永続化します。

1. **Session store（`sessions.json`）**
   - キー/値マップ: `sessionKey -> SessionEntry`
   - 小さく、可変で、編集も安全（エントリの削除も可能）
   - セッションメタデータ（現在の session id、最終アクティビティ、トグル、トークンカウンターなど）を追跡します

2. **Transcript（`<sessionId>.jsonl`）**
   - ツリー構造を持つ追記専用 transcript（エントリは `id` + `parentId` を持つ）
   - 実際の会話 + tool call + compaction summary を保存します
   - 将来のターンでモデルコンテキストを再構築するために使われます

---

## ディスク上の場所

Gateway ホスト上の agent ごとに:

- Store: `~/.openclaw/agents/<agentId>/sessions/sessions.json`
- Transcript: `~/.openclaw/agents/<agentId>/sessions/<sessionId>.jsonl`
  - Telegram topic セッション: `.../<sessionId>-topic-<threadId>.jsonl`

OpenClaw はこれらを `src/config/sessions.ts` を通じて解決します。

---

## Store メンテナンスとディスク制御

セッション永続化には、`sessions.json` と transcript アーティファクト向けの自動メンテナンス制御（`session.maintenance`）があります。

- `mode`: `warn`（デフォルト）または `enforce`
- `pruneAfter`: 古いエントリの期限切れしきい値（デフォルト `30d`）
- `maxEntries`: `sessions.json` 内のエントリ数上限（デフォルト `500`）
- `rotateBytes`: サイズ超過時に `sessions.json` をローテーションするしきい値（デフォルト `10mb`）
- `resetArchiveRetention`: `*.reset.<timestamp>` transcript archive の保持期間（デフォルト: `pruneAfter` と同じ。`false` でクリーンアップ無効）
- `maxDiskBytes`: 任意の sessions ディレクトリ予算
- `highWaterBytes`: クリーンアップ後の任意ターゲット（デフォルトは `maxDiskBytes` の `80%`）

ディスク予算クリーンアップ（`mode: "enforce"`）の適用順序:

1. まず、最も古い archive 済みまたは orphan の transcript アーティファクトを削除します。
2. まだターゲットを超えている場合は、最も古いセッションエントリとそれに対応する transcript ファイルを削除します。
3. 使用量が `highWaterBytes` 以下になるまで続けます。

`mode: "warn"` では、OpenClaw は削除候補を報告しますが、store/files は変更しません。

必要に応じてメンテナンスを実行するには:

```bash
openclaw sessions cleanup --dry-run
openclaw sessions cleanup --enforce
```

---

## Cron セッションと実行ログ

分離された cron 実行でもセッションエントリ/transcript が作成され、専用の保持制御があります。

- `cron.sessionRetention`（デフォルト `24h`）は、session store から古い分離 cron 実行セッションを削除します（`false` で無効）。
- `cron.runLog.maxBytes` + `cron.runLog.keepLines` は `~/.openclaw/cron/runs/<jobId>.jsonl` ファイルを剪定します（デフォルト: `2_000_000` bytes と `2000` lines）。

---

## Session key（`sessionKey`）

`sessionKey` は、どの会話バケットにいるかを識別します（ルーティング + 分離）。

一般的なパターン:

- Main/direct chat（agent ごと）: `agent:<agentId>:<mainKey>`（デフォルト `main`）
- Group: `agent:<agentId>:<channel>:group:<id>`
- Room/channel（Discord/Slack）: `agent:<agentId>:<channel>:channel:<id>` または `...:room:<id>`
- Cron: `cron:<job.id>`
- Webhook: `hook:<uuid>`（上書きされない限り）

正規のルールは [/concepts/session](/ja-JP/concepts/session) に記載されています。

---

## Session id（`sessionId`）

各 `sessionKey` は現在の `sessionId` を指します（会話を継続する transcript ファイル）。

覚えておくべきルール:

- **Reset**（`/new`、`/reset`）は、その `sessionKey` 用に新しい `sessionId` を作成します。
- **日次リセット**（デフォルトでは Gateway ホストのローカル時刻で午前 4:00）は、リセット境界を越えた後の次のメッセージで新しい `sessionId` を作成します。
- **Idle expiry**（`session.reset.idleMinutes` またはレガシーの `session.idleMinutes`）は、アイドル期間後にメッセージが到着すると新しい `sessionId` を作成します。日次と idle の両方が設定されている場合は、先に期限切れになる方が優先されます。
- **Thread parent fork guard**（`session.parentForkMaxTokens`、デフォルト `100000`）は、親セッションがすでに大きすぎる場合に親 transcript の fork をスキップします。新しいスレッドは新規開始されます。無効にするには `0` を設定します。

実装の詳細: この判定は `src/auto-reply/reply/session.ts` の `initSessionState()` で行われます。

---

## Session store schema（`sessions.json`）

store の値型は `src/config/sessions.ts` の `SessionEntry` です。

主要フィールド（網羅的ではありません）:

- `sessionId`: 現在の transcript id（`sessionFile` が設定されていない限りファイル名はこれから導出される）
- `updatedAt`: 最終アクティビティのタイムスタンプ
- `sessionFile`: 任意の明示的 transcript パス override
- `chatType`: `direct | group | room`（UI や送信 policy の補助）
- `provider`, `subject`, `room`, `space`, `displayName`: group/channel ラベル用メタデータ
- トグル:
  - `thinkingLevel`, `verboseLevel`, `reasoningLevel`, `elevatedLevel`
  - `sendPolicy`（セッションごとの override）
- モデル選択:
  - `providerOverride`, `modelOverride`, `authProfileOverride`
- トークンカウンター（ベストエフォート / provider 依存）:
  - `inputTokens`, `outputTokens`, `totalTokens`, `contextTokens`
- `compactionCount`: この session key で自動 compaction が完了した回数
- `memoryFlushAt`: 最後の pre-compaction memory flush のタイムスタンプ
- `memoryFlushCompactionCount`: 最後の flush 実行時点の compaction count

store は安全に編集できますが、権限を持つのは Gateway です。セッション実行中にエントリが再書き込みまたは再構成されることがあります。

---

## Transcript 構造（`*.jsonl`）

Transcript は `@mariozechner/pi-coding-agent` の `SessionManager` によって管理されます。

ファイルは JSONL です。

- 1 行目: セッションヘッダー（`type: "session"`、`id`、`cwd`、`timestamp`、任意で `parentSession` を含む）
- 以降: `id` + `parentId` を持つセッションエントリ（ツリー）

主なエントリ型:

- `message`: user/assistant/toolResult メッセージ
- `custom_message`: 拡張機能が注入するメッセージで、モデルコンテキストには**入る**もの（UI では非表示にもできる）
- `custom`: モデルコンテキストには**入らない**拡張状態
- `compaction`: `firstKeptEntryId` と `tokensBefore` を含む永続化された compaction summary
- `branch_summary`: ツリー分岐を移動するときの永続化 summary

OpenClaw は意図的に transcript を「fix up」しません。Gateway は `SessionManager` を使ってそれらを読み書きします。

---

## コンテキストウィンドウと追跡トークンの違い

重要なのは 2 つの異なる概念です。

1. **モデルコンテキストウィンドウ**: モデルごとのハード上限（モデルに見えるトークン数）
2. **Session store カウンター**: `sessions.json` に書き込まれるローリング統計（`/status` やダッシュボードで使用）

制限を調整する場合:

- コンテキストウィンドウはモデルカタログから取得されます（config で override も可能）。
- store の `contextTokens` はランタイムの推定/報告値であり、厳密な保証として扱わないでください。

詳細は [/token-use](/ja-JP/reference/token-use) を参照してください。

---

## Compaction とは何か

Compaction は、古い会話を transcript 内の永続化された `compaction` エントリに要約し、最近のメッセージはそのまま保持します。

compaction 後、将来のターンで見えるものは次のとおりです。

- compaction summary
- `firstKeptEntryId` 以降のメッセージ

Compaction は **永続的** です（session pruning とは異なります）。[/concepts/session-pruning](/ja-JP/concepts/session-pruning) を参照してください。

## Compaction のチャンク境界と tool のペアリング

OpenClaw が長い transcript を compaction チャンクに分割するとき、assistant の tool call と対応する `toolResult` エントリをペアのまま保持します。

- トークン比率による分割が tool call とその結果の間に来る場合、OpenClaw はペアを分離する代わりに境界を assistant の tool-call message 側へずらします。
- 末尾の tool-result ブロックのせいでチャンクがターゲットを超えてしまう場合、OpenClaw はその保留中 tool ブロックを保持し、未要約の tail をそのまま残します。
- 中断/エラーになった tool-call ブロックは、保留中の分割を維持しません。

---

## 自動 compaction が発生するタイミング（Pi runtime）

組み込み Pi agent では、自動 compaction は次の 2 つの場合に発動します。

1. **オーバーフロー回復**: モデルがコンテキストオーバーフローエラーを返した場合
   （`request_too_large`、`context length exceeded`、`input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`input is too long for the model`、`ollama error: context length
exceeded`、およびそれに類する provider 固有のバリエーション）→ compact → retry。
2. **しきい値メンテナンス**: 成功したターンの後で、次を満たす場合:

`contextTokens > contextWindow - reserveTokens`

ここで:

- `contextWindow` はモデルのコンテキストウィンドウ
- `reserveTokens` はプロンプト + 次のモデル出力のために確保される余裕領域

これらは Pi runtime の意味論です（OpenClaw はイベントを消費しますが、compact するタイミングを決めるのは Pi です）。

---

## Compaction 設定（`reserveTokens`, `keepRecentTokens`）

Pi の compaction 設定は Pi settings にあります。

```json5
{
  compaction: {
    enabled: true,
    reserveTokens: 16384,
    keepRecentTokens: 20000,
  },
}
```

OpenClaw は組み込み実行に対して安全下限も適用します。

- `compaction.reserveTokens < reserveTokensFloor` の場合、OpenClaw はそれを引き上げます。
- デフォルトの下限は `20000` トークンです。
- 下限を無効にするには `agents.defaults.compaction.reserveTokensFloor: 0` を設定します。
- すでにそれより高い場合、OpenClaw は変更しません。

理由: compaction が避けられなくなる前に、複数ターンにわたる「ハウスキーピング」（メモリ書き込みなど）のための十分な余裕を残すためです。

実装: `src/agents/pi-settings.ts` の `ensurePiCompactionReserveTokens()`
（`src/agents/pi-embedded-runner.ts` から呼び出されます）。

---

## プラガブルな compaction provider

plugin は plugin API の `registerCompactionProvider()` を通じて compaction provider を登録できます。`agents.defaults.compaction.provider` に登録済み provider id が設定されている場合、safeguard extension は組み込みの `summarizeInStages` パイプラインではなく、その provider に要約を委譲します。

- `provider`: 登録済み compaction provider plugin の id。デフォルトの LLM 要約を使う場合は未設定のままにします。
- `provider` を設定すると `mode: "safeguard"` が強制されます。
- provider には、組み込み経路と同じ compaction 指示と ID 保持ポリシーが渡されます。
- safeguard は provider 出力後も recent-turn と split-turn の suffix コンテキストを保持します。
- provider が失敗したり空結果を返した場合、OpenClaw は自動的に組み込み LLM 要約へフォールバックします。
- Abort/timeout シグナルは呼び出し元のキャンセルを尊重するため再スローされます（握りつぶされません）。

ソース: `src/plugins/compaction-provider.ts`, `src/agents/pi-hooks/compaction-safeguard.ts`。

---

## ユーザーに見える surface

compaction とセッション状態は次で確認できます。

- `/status`（任意のチャットセッション内）
- `openclaw status`（CLI）
- `openclaw sessions` / `sessions --json`
- 詳細モード: `🧹 Auto-compaction complete` + compaction count

---

## サイレントなハウスキーピング（`NO_REPLY`）

OpenClaw は、バックグラウンドタスク向けの「サイレント」ターンをサポートしています。これは、ユーザーに中間出力を見せたくない場合に使います。

慣例:

- assistant は、ユーザーに返信を配信しないことを示すために、出力を正確な silent token `NO_REPLY` /
  `no_reply` で開始します。
- OpenClaw は配信レイヤーでこれを取り除く/抑制します。
- 正確な silent-token 抑制は大文字小文字を区別しないため、ペイロード全体が silent token だけである場合、`NO_REPLY` と
  `no_reply` の両方が有効です。
- これは本当にバックグラウンド/未配信のターン専用であり、通常の実行可能なユーザー要求の近道ではありません。

`2026.1.10` 時点で、OpenClaw は
部分チャンクが `NO_REPLY` で始まる場合、**draft/typing streaming** も抑制するため、サイレント操作がターン途中の部分出力を漏らすことはありません。

---

## Pre-compaction の「memory flush」（実装済み）

目的: 自動 compaction が起こる前に、ディスク上の永続状態（例: agent workspace 内の `memory/YYYY-MM-DD.md`）を書き込むサイレントな
agentic turn を実行し、critical なコンテキストが compaction で失われないようにすることです。

OpenClaw は **pre-threshold flush** アプローチを使用します。

1. セッションのコンテキスト使用量を監視する。
2. それが「ソフトしきい値」（Pi の compaction しきい値より低い）を超えたら、agent にサイレントな
   「今すぐ memory を書き込む」指示を実行する。
3. ユーザーに何も見せないため、正確な silent token `NO_REPLY` / `no_reply` を使用する。

設定（`agents.defaults.compaction.memoryFlush`）:

- `enabled`（デフォルト: `true`）
- `softThresholdTokens`（デフォルト: `4000`）
- `prompt`（flush turn 用 user message）
- `systemPrompt`（flush turn に追加される追加 system prompt）

注意:

- デフォルトの prompt/system prompt には、配信を抑制するための `NO_REPLY` ヒントが含まれます。
- flush は compaction サイクルごとに 1 回だけ実行されます（`sessions.json` で追跡）。
- flush は組み込み Pi セッションでのみ実行されます（CLI バックエンドではスキップ）。
- セッション workspace が読み取り専用（`workspaceAccess: "ro"` または `"none"`）の場合、flush はスキップされます。
- workspace ファイルレイアウトと書き込みパターンについては [Memory](/ja-JP/concepts/memory) を参照してください。

Pi も extension API に `session_before_compact` hook を公開していますが、OpenClaw の
flush ロジックは現在 Gateway 側にあります。

---

## トラブルシューティングチェックリスト

- Session key がおかしいですか？ まず [/concepts/session](/ja-JP/concepts/session) を確認し、`/status` の `sessionKey` を確認してください。
- Store と transcript が一致しませんか？ Gateway ホストと `openclaw status` から取得した store path を確認してください。
- Compaction が多すぎますか？ 次を確認してください:
  - モデルコンテキストウィンドウ（小さすぎないか）
  - compaction 設定（モデルウィンドウに対して `reserveTokens` が高すぎると、より早い compaction の原因になります）
  - tool-result の肥大化: session pruning を有効化/調整する
- Silent turn が漏れていますか？ 返信が `NO_REPLY`（大文字小文字を区別しない正確なトークン）で始まっていること、および streaming suppression 修正を含むビルドであることを確認してください。
