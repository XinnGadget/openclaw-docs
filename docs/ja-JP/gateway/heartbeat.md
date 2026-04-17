---
read_when:
    - ハートビートの頻度またはメッセージングの調整
    - スケジュールされたタスクにハートビートと cron のどちらを使うかの判断
summary: ハートビートポーリングメッセージと通知ルール
title: ハートビート
x-i18n:
    generated_at: "2026-04-11T02:44:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: e4485072148753076d909867a623696829bf4a82dcd0479b95d5d0cae43100b0
    source_path: gateway/heartbeat.md
    workflow: 15
---

# ハートビート（Gateway）

> **Heartbeat と Cron のどちらを使うべきですか？** 使い分けの指針については [Automation & Tasks](/ja-JP/automation) を参照してください。

Heartbeat は、**定期的なエージェントターン** をメインセッションで実行し、
必要な注意事項をモデルが表に出せるようにしつつ、過剰な通知を防ぎます。

Heartbeat は、スケジュールされたメインセッションのターンです — [background task](/ja-JP/automation/tasks) レコードは作成しません。
タスクレコードは、切り離された作業（ACP 実行、subagent、分離された cron ジョブ）用です。

トラブルシューティング: [Scheduled Tasks](/ja-JP/automation/cron-jobs#troubleshooting)

## クイックスタート（初心者向け）

1. Heartbeat を有効のままにする（デフォルトは `30m`、Anthropic OAuth/token auth の場合は `1h`。Claude CLI reuse を含む）か、独自の頻度を設定します。
2. エージェントワークスペースに小さな `HEARTBEAT.md` チェックリストまたは `tasks:` ブロックを作成します（任意ですが推奨）。
3. Heartbeat メッセージの送信先を決めます（デフォルトは `target: "none"` です。最後の連絡先に送るには `target: "last"` を設定します）。
4. 任意で、透明性のために heartbeat reasoning 配信を有効にします。
5. 任意で、heartbeat 実行で `HEARTBEAT.md` だけが必要な場合は軽量な bootstrap コンテキストを使用します。
6. 任意で、heartbeat ごとに会話履歴全体を送らないように分離セッションを有効にします。
7. 任意で、heartbeat をアクティブ時間帯（ローカル時刻）に制限します。

設定例:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先への明示的な配信（デフォルトは "none"）
        directPolicy: "allow", // デフォルト: 直接/DM 宛先を許可。抑制するには "block" を設定
        lightContext: true, // 任意: bootstrap ファイルから HEARTBEAT.md のみを注入
        isolatedSession: true, // 任意: 毎回新しいセッションで実行（会話履歴なし）
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // 任意: 別の `Reasoning:` メッセージも送信
      },
    },
  },
}
```

## デフォルト

- 間隔: `30m`（または、Anthropic OAuth/token auth が検出された auth mode の場合は `1h`。Claude CLI reuse を含む）。`agents.defaults.heartbeat.every` またはエージェントごとの `agents.list[].heartbeat.every` を設定します。無効にするには `0m` を使用します。
- プロンプト本文（`agents.defaults.heartbeat.prompt` で設定可能）:
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- heartbeat プロンプトは、ユーザーメッセージとして**そのまま**送信されます。システム
  プロンプトには、デフォルトエージェントで heartbeat が有効かつ
  実行が内部的にフラグ付けされている場合にのみ「Heartbeat」セクションが含まれます。
- Heartbeat を `0m` で無効にすると、通常実行でも bootstrap コンテキストから
  `HEARTBEAT.md` が除外されるため、モデルは heartbeat 専用の指示を見ません。
- アクティブ時間帯（`heartbeat.activeHours`）は、設定されたタイムゾーンで判定されます。
  時間帯外では、heartbeat は次に時間帯内に入る tick までスキップされます。

## heartbeat プロンプトの目的

デフォルトのプロンプトは、意図的に広い内容になっています:

- **バックグラウンドタスク**: 「未処理タスクを検討する」は、エージェントに
  フォローアップ（受信箱、カレンダー、リマインダー、キュー済み作業）を確認させ、
  緊急なものを表に出すよう促します。
- **人へのチェックイン**: 「日中にときどき人間の様子を確認する」は、
  軽い「何か必要ですか？」メッセージを時々送るよう促しますが、
  設定されたローカルタイムゾーンを使うことで夜間の通知過多を避けます（[/concepts/timezone](/ja-JP/concepts/timezone) を参照）。

Heartbeat は完了した [background tasks](/ja-JP/automation/tasks) に反応できますが、heartbeat 実行自体はタスクレコードを作成しません。

heartbeat に非常に具体的なこと（たとえば「Gmail PubSub
stats を確認する」や「Gateway の健全性を検証する」）をさせたい場合は、`agents.defaults.heartbeat.prompt`（または
`agents.list[].heartbeat.prompt`）にカスタム本文（そのまま送信される）を設定してください。

## レスポンス契約

- 注意が必要なことが何もなければ、**`HEARTBEAT_OK`** で返信します。
- heartbeat 実行中、OpenClaw は返信の**先頭または末尾**に `HEARTBEAT_OK` が現れた場合、
  それを ack として扱います。このトークンは削除され、残りの内容が
  **`ackMaxChars` 以下**（デフォルト: 300）であれば、その返信は破棄されます。
- `HEARTBEAT_OK` が返信の**途中**に現れた場合は、
  特別扱いされません。
- アラートの場合は、**`HEARTBEAT_OK` を含めないでください**。アラート文だけを返します。

heartbeat 以外では、メッセージの先頭/末尾に紛れ込んだ `HEARTBEAT_OK` は削除されて
ログに記録されます。メッセージが `HEARTBEAT_OK` だけの場合は破棄されます。

## 設定

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // デフォルト: 30m（0m で無効化）
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // デフォルト: false（利用可能な場合は別の Reasoning: メッセージを配信）
        lightContext: false, // デフォルト: false。true の場合、ワークスペース bootstrap ファイルから HEARTBEAT.md のみを保持
        isolatedSession: false, // デフォルト: false。true の場合、各 heartbeat を新しいセッションで実行（会話履歴なし）
        target: "last", // デフォルト: none | オプション: last | none | <channel id>（コアまたは plugin。例: "bluebubbles"）
        to: "+15551234567", // 任意のチャネル固有オーバーライド
        accountId: "ops-bot", // 任意のマルチアカウントチャネル id
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // HEARTBEAT_OK の後に許容される最大文字数
      },
    },
  },
}
```

### スコープと優先順位

- `agents.defaults.heartbeat` はグローバルな heartbeat 動作を設定します。
- `agents.list[].heartbeat` はその上にマージされます。いずれかのエージェントに `heartbeat` ブロックがある場合、heartbeat を実行するのは**それらのエージェントだけ**です。
- `channels.defaults.heartbeat` は全チャネルの可視性デフォルトを設定します。
- `channels.<channel>.heartbeat` はチャネルデフォルトを上書きします。
- `channels.<channel>.accounts.<id>.heartbeat`（マルチアカウントチャネル）はチャネルごとの設定を上書きします。

### エージェントごとの heartbeat

いずれかの `agents.list[]` エントリに `heartbeat` ブロックが含まれている場合、heartbeat を実行するのは**それらのエージェントだけ**です。  
エージェントごとのブロックは `agents.defaults.heartbeat` の上にマージされます
（共有デフォルトを一度設定し、エージェントごとに上書きできます）。

例: 2つのエージェントがあり、heartbeat を実行するのは2番目のエージェントだけです。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先への明示的な配信（デフォルトは "none"）
      },
    },
    list: [
      { id: "main", default: true },
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "whatsapp",
          to: "+15551234567",
          timeoutSeconds: 45,
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### アクティブ時間帯の例

特定のタイムゾーンの業務時間に heartbeat を制限します:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先への明示的な配信（デフォルトは "none"）
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // 任意。userTimezone が設定されていればそれを使い、なければホストのタイムゾーン
        },
      },
    },
  },
}
```

この時間帯の外側（東部時間で午前9時前または午後10時以降）では、heartbeat はスキップされます。次に時間帯内に入る予定 tick で通常どおり実行されます。

### 24時間365日の設定

heartbeat を終日実行したい場合は、次のいずれかのパターンを使用します:

- `activeHours` を完全に省略する（時間帯制限なし。これがデフォルト動作です）。
- 終日ウィンドウを設定する: `activeHours: { start: "00:00", end: "24:00" }`。

同じ `start` と `end` の時刻（たとえば `08:00` から `08:00`）は設定しないでください。
これは幅ゼロのウィンドウとして扱われるため、heartbeat は常にスキップされます。

### マルチアカウントの例

Telegram のようなマルチアカウントチャネルで特定のアカウントを対象にするには `accountId` を使います:

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // 任意: 特定の topic/thread にルーティング
          accountId: "ops-bot",
        },
      },
    ],
  },
  channels: {
    telegram: {
      accounts: {
        "ops-bot": { botToken: "YOUR_TELEGRAM_BOT_TOKEN" },
      },
    },
  },
}
```

### フィールドメモ

- `every`: heartbeat 間隔（duration string。デフォルト単位 = 分）。
- `model`: heartbeat 実行用の任意のモデル上書き（`provider/model`）。
- `includeReasoning`: 有効な場合、利用可能なときに別の `Reasoning:` メッセージも配信します（`/reasoning on` と同じ形式）。
- `lightContext`: true の場合、heartbeat 実行では軽量な bootstrap コンテキストを使い、ワークスペース bootstrap ファイルから `HEARTBEAT.md` のみを保持します。
- `isolatedSession`: true の場合、各 heartbeat は以前の会話履歴を持たない新しいセッションで実行されます。cron の `sessionTarget: "isolated"` と同じ分離パターンを使用します。heartbeat ごとのトークンコストを大幅に削減します。最大限節約するには `lightContext: true` と組み合わせてください。配信ルーティングは引き続きメインセッションのコンテキストを使います。
- `session`: heartbeat 実行用の任意のセッションキー。
  - `main`（デフォルト）: エージェントのメインセッション。
  - 明示的なセッションキー（`openclaw sessions --json` または [sessions CLI](/cli/sessions) からコピー）。
  - セッションキー形式: [Sessions](/ja-JP/concepts/session) および [Groups](/ja-JP/channels/groups) を参照してください。
- `target`:
  - `last`: 最後に使用された外部チャネルに配信します。
  - 明示的なチャネル: 任意の設定済みチャネルまたは plugin id。たとえば `discord`、`matrix`、`telegram`、`whatsapp`。
  - `none`（デフォルト）: heartbeat は実行しますが、外部には**配信しません**。
- `directPolicy`: 直接/DM 配信の動作を制御します:
  - `allow`（デフォルト）: 直接/DM への heartbeat 配信を許可します。
  - `block`: 直接/DM 配信を抑制します（`reason=dm-blocked`）。
- `to`: 任意の受信者上書き（チャネル固有 id。たとえば WhatsApp の E.164 や Telegram の chat id）。Telegram の topic/thread には `<chatId>:topic:<messageThreadId>` を使用します。
- `accountId`: マルチアカウントチャネル用の任意のアカウント id。`target: "last"` の場合、そのアカウント id は、最後に解決されたチャネルがアカウントをサポートしていれば適用され、そうでなければ無視されます。アカウント id が解決されたチャネルの設定済みアカウントに一致しない場合、配信はスキップされます。
- `prompt`: デフォルトのプロンプト本文を上書きします（マージされません）。
- `ackMaxChars`: `HEARTBEAT_OK` の後に許容される最大文字数。
- `suppressToolErrorWarnings`: true の場合、heartbeat 実行中のツールエラー警告ペイロードを抑制します。
- `activeHours`: heartbeat 実行を時間帯に制限します。`start`（HH:MM、含む。日の始まりには `00:00` を使用）、`end`（HH:MM、含まない。日末には `24:00` が使用可能）、および任意の `timezone` を持つオブジェクトです。
  - 省略または `"user"`: `agents.defaults.userTimezone` が設定されていればそれを使い、そうでなければホストシステムのタイムゾーンにフォールバックします。
  - `"local"`: 常にホストシステムのタイムゾーンを使います。
  - 任意の IANA 識別子（例: `America/New_York`）: 直接使用されます。無効な場合は、上記の `"user"` 動作にフォールバックします。
  - アクティブウィンドウとして扱うには `start` と `end` は等しくしてはいけません。等しい値は幅ゼロ（常に時間帯外）として扱われます。
  - アクティブ時間帯の外では、heartbeat は次に時間帯内に入る tick までスキップされます。

## 配信動作

- Heartbeat はデフォルトでエージェントのメインセッション（`agent:<id>:<mainKey>`）で実行され、
  `session.scope = "global"` の場合は `global` で実行されます。特定のチャネルセッション（Discord/WhatsApp など）に上書きするには
  `session` を設定します。
- `session` は実行コンテキストにのみ影響します。配信は `target` と `to` によって制御されます。
- 特定のチャネル/受信者に配信するには、`target` + `to` を設定します。
  `target: "last"` の場合、配信にはそのセッションの最後の外部チャネルが使われます。
- Heartbeat 配信は、デフォルトで直接/DM 宛先を許可します。heartbeat ターン自体は実行したまま直接宛先への送信を抑制するには、`directPolicy: "block"` を設定します。
- メインキューがビジーな場合、heartbeat はスキップされ、後で再試行されます。
- `target` が外部宛先に解決されない場合でも、実行自体は行われますが、
  外向きメッセージは送信されません。
- `showOk`、`showAlerts`、`useIndicator` がすべて無効の場合、実行は事前に `reason=alerts-disabled` としてスキップされます。
- アラート配信のみが無効な場合、OpenClaw は引き続き heartbeat を実行し、期限付きタスクのタイムスタンプを更新し、セッションのアイドルタイムスタンプを復元し、外向きのアラートペイロードを抑制できます。
- Heartbeat 専用の返信はセッションをアクティブ状態に保ちません。`updatedAt`
  は復元されるため、アイドル期限切れは通常どおり動作します。
- 切り離された [background tasks](/ja-JP/automation/tasks) はシステムイベントをキューに入れ、メインセッションが何かにすばやく気づくべきときに heartbeat を起こすことができます。この wake によって heartbeat 実行が background task になるわけではありません。

## 可視性の制御

デフォルトでは、`HEARTBEAT_OK` の確認応答は抑制され、アラート内容は
配信されます。これはチャネルごと、またはアカウントごとに調整できます:

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # HEARTBEAT_OK を非表示（デフォルト）
      showAlerts: true # アラートメッセージを表示（デフォルト）
      useIndicator: true # indicator イベントを発行（デフォルト）
  telegram:
    heartbeat:
      showOk: true # Telegram では OK 確認応答を表示
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # このアカウントではアラート配信を抑制
```

優先順位: アカウントごと → チャネルごと → チャネルデフォルト → 組み込みデフォルト。

### 各フラグの意味

- `showOk`: モデルが OK のみの返信を返したときに `HEARTBEAT_OK` 確認応答を送信します。
- `showAlerts`: モデルが非 OK の返信を返したときにアラート内容を送信します。
- `useIndicator`: UI のステータス表示向けに indicator イベントを発行します。

**3つすべて** が false の場合、OpenClaw は heartbeat 実行全体をスキップします（モデル呼び出しなし）。

### チャネルごととアカウントごとの例

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false
      showAlerts: true
      useIndicator: true
  slack:
    heartbeat:
      showOk: true # すべての Slack アカウント
    accounts:
      ops:
        heartbeat:
          showAlerts: false # ops アカウントのみアラートを抑制
  telegram:
    heartbeat:
      showOk: true
```

### よくあるパターン

| 目的 | 設定 |
| --- | --- |
| デフォルト動作（OK は無言、アラートは有効） | _(設定不要)_ |
| 完全に無音（メッセージなし、indicator なし） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| indicator のみ（メッセージなし） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }` |
| 1つのチャネルでのみ OK を表示 | `channels.telegram.heartbeat: { showOk: true }` |

## HEARTBEAT.md（任意）

ワークスペースに `HEARTBEAT.md` ファイルがある場合、デフォルトプロンプトは
エージェントにそれを読むよう指示します。これは「heartbeat チェックリスト」と考えてください: 小さく、安定していて、
30分ごとに含めても安全なものです。

通常実行では、`HEARTBEAT.md` は
デフォルトエージェントで heartbeat ガイダンスが有効な場合にのみ注入されます。
頻度を `0m` にして heartbeat cadence を無効にするか、
`includeSystemPromptSection: false` を設定すると、通常の bootstrap
コンテキストから除外されます。

`HEARTBEAT.md` が存在していても、実質的に空（空行と
`# Heading` のような Markdown 見出しだけ）の場合、OpenClaw は API 呼び出しを節約するため heartbeat 実行をスキップします。
このスキップは `reason=empty-heartbeat-file` として報告されます。
ファイルが存在しない場合でも、heartbeat は実行され、モデルが何をするかを判断します。

プロンプト膨張を避けるため、小さく保ってください（短いチェックリストまたはリマインダー）。

`HEARTBEAT.md` の例:

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### `tasks:` ブロック

`HEARTBEAT.md` は、heartbeat 自体の中で間隔ベースの
チェックを行うための小さな構造化 `tasks:` ブロックもサポートしています。

例:

```md
tasks:

- name: inbox-triage
  interval: 30m
  prompt: "Check for urgent unread emails and flag anything time sensitive."
- name: calendar-scan
  interval: 2h
  prompt: "Check for upcoming meetings that need prep or follow-up."

# Additional instructions

- Keep alerts short.
- If nothing needs attention after all due tasks, reply HEARTBEAT_OK.
```

動作:

- OpenClaw は `tasks:` ブロックを解析し、各タスクをそれぞれの `interval` に対して確認します。
- その tick で**期限が来ている**タスクだけが heartbeat プロンプトに含まれます。
- 期限が来ているタスクがない場合、無駄なモデル呼び出しを避けるため、heartbeat は完全にスキップされます（`reason=no-tasks-due`）。
- `HEARTBEAT.md` 内のタスク以外の内容は保持され、期限到来タスクリストの後に追加コンテキストとして付加されます。
- タスクの最終実行タイムスタンプはセッション状態（`heartbeatTaskState`）に保存されるため、通常の再起動後も間隔が維持されます。
- タスクのタイムスタンプが進むのは、heartbeat 実行が通常の返信パスを完了した後だけです。`empty-heartbeat-file` / `no-tasks-due` でスキップされた実行は、タスク完了として記録されません。

タスクモードは、1つの heartbeat ファイルに複数の定期チェックを持たせつつ、毎 tick それらすべてのコストを払いたくない場合に便利です。

### エージェントは HEARTBEAT.md を更新できますか？

はい — そうするように指示すれば可能です。

`HEARTBEAT.md` はエージェントワークスペース内の通常のファイルなので、
通常のチャットで、たとえば次のようにエージェントに指示できます:

- 「毎日のカレンダーチェックを追加するように `HEARTBEAT.md` を更新して」
- 「`HEARTBEAT.md` を、もっと短くして受信箱のフォローアップに集中する内容に書き直して」

これを積極的に行わせたい場合は、heartbeat プロンプトに
「チェックリストが古くなったら、より良いものに `HEARTBEAT.md`
を更新すること」のような明示的な一文を含めることもできます。

安全上の注意: `HEARTBEAT.md` にシークレット（API キー、電話番号、秘密トークン）を入れないでください —
これはプロンプトコンテキストの一部になります。

## 手動 wake（オンデマンド）

システムイベントをキューに入れ、すぐに heartbeat をトリガーするには次を実行します:

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

複数のエージェントに `heartbeat` が設定されている場合、
手動 wake はそれらの各エージェント heartbeat を即座に実行します。

次の予定 tick を待つには `--mode next-heartbeat` を使用します。

## reasoning 配信（任意）

デフォルトでは、heartbeat は最終的な「回答」ペイロードのみを配信します。

透明性が必要な場合は、次を有効にします:

- `agents.defaults.heartbeat.includeReasoning: true`

有効にすると、heartbeat は `Reasoning:` で始まる別メッセージも配信します
（`/reasoning on` と同じ形式）。これは、エージェントが複数のセッション/codex を管理していて、
なぜあなたに通知すると判断したのかを見たい場合に便利です —
ただし、望まない内部詳細まで漏れる可能性もあります。グループチャットでは通常、無効のままにしておくことをおすすめします。

## コスト意識

Heartbeat は完全なエージェントターンを実行します。間隔を短くするほどトークン消費は増えます。コストを下げるには:

- 完全な会話履歴を送らないように `isolatedSession: true` を使用する（実行あたりおよそ 100K トークンから 2-5K に削減）。
- bootstrap ファイルを `HEARTBEAT.md` のみに制限するため `lightContext: true` を使用する。
- より安価な `model` を設定する（例: `ollama/llama3.2:1b`）。
- `HEARTBEAT.md` を小さく保つ。
- 内部状態更新だけが必要なら `target: "none"` を使用する。

## 関連

- [Automation & Tasks](/ja-JP/automation) — すべての自動化メカニズムの概要
- [Background Tasks](/ja-JP/automation/tasks) — 切り離された作業がどのように追跡されるか
- [Timezone](/ja-JP/concepts/timezone) — タイムゾーンが heartbeat スケジューリングにどう影響するか
- [Troubleshooting](/ja-JP/automation/cron-jobs#troubleshooting) — 自動化の問題をデバッグする方法
