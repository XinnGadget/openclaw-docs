---
read_when:
    - Heartbeat の間隔やメッセージ内容を調整する場合
    - スケジュールされたタスクで heartbeat と cron のどちらを使うか判断する場合
summary: Heartbeat のポーリングメッセージと通知ルール
title: Heartbeat
x-i18n:
    generated_at: "2026-04-08T02:15:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8021d747637060eacb91ec5f75904368a08790c19f4fca32acda8c8c0a25e41
    source_path: gateway/heartbeat.md
    workflow: 15
---

# Heartbeat (Gateway)

> **Heartbeat と Cron の違いは？** 使い分けの指針については [Automation & Tasks](/ja-JP/automation) を参照してください。

Heartbeat は、メインセッションで **定期的なエージェントターン** を実行し、必要な注意事項をあなたにスパムせずに通知できるようにします。

Heartbeat はスケジュールされたメインセッションのターンであり、[background task](/ja-JP/automation/tasks) レコードは作成しません。
タスクレコードは、切り離された作業（ACP 実行、サブエージェント、分離された cron ジョブ）のためのものです。

トラブルシューティング: [Scheduled Tasks](/ja-JP/automation/cron-jobs#troubleshooting)

## クイックスタート（初心者向け）

1. Heartbeat を有効のままにしておくか（デフォルトは `30m`、Anthropic OAuth / token 認証時は `1h`。Claude CLI の再利用を含む）、独自の間隔を設定します。
2. エージェントのワークスペースに、小さな `HEARTBEAT.md` チェックリストまたは `tasks:` ブロックを作成します（任意ですが推奨）。
3. Heartbeat メッセージの送信先を決めます（デフォルトは `target: "none"` です。最後の連絡先へ送るには `target: "last"` を設定します）。
4. 任意: 透明性のために heartbeat reasoning 配信を有効にします。
5. 任意: Heartbeat 実行で `HEARTBEAT.md` だけが必要な場合は、軽量なブートストラップコンテキストを使用します。
6. 任意: 各 heartbeat で会話履歴全体を送信しないよう、分離セッションを有効にします。
7. 任意: Heartbeat をアクティブな時間帯（ローカル時刻）に制限します。

設定例:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先へ明示的に配信（デフォルトは "none"）
        directPolicy: "allow", // デフォルト: 直接 / DM 宛先を許可。抑止するには "block" を設定
        lightContext: true, // 任意: ブートストラップファイルから HEARTBEAT.md のみを注入
        isolatedSession: true, // 任意: 実行ごとに新しいセッションを使用（会話履歴なし）
        // activeHours: { start: "08:00", end: "24:00" },
        // includeReasoning: true, // 任意: 別の `Reasoning:` メッセージも送信
      },
    },
  },
}
```

## デフォルト

- 間隔: `30m`（Anthropic OAuth / token 認証が検出された認証モードの場合は `1h`。Claude CLI の再利用を含む）。`agents.defaults.heartbeat.every` またはエージェント単位の `agents.list[].heartbeat.every` を設定してください。無効化するには `0m` を使用します。
- プロンプト本文（`agents.defaults.heartbeat.prompt` で設定可能）:
  `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`
- Heartbeat プロンプトはユーザーメッセージとして **そのまま** 送信されます。システム
  プロンプトには、デフォルトエージェントで heartbeat が有効であり、
  かつ実行に内部フラグが付いている場合にのみ「Heartbeat」セクションが含まれます。
- `0m` で heartbeat を無効にすると、通常実行でもブートストラップコンテキストから `HEARTBEAT.md`
  が除外され、モデルは heartbeat 専用の指示を見なくなります。
- アクティブ時間帯（`heartbeat.activeHours`）は、設定されたタイムゾーンで判定されます。
  時間帯の外では、次回その時間帯内に入る tick まで heartbeat はスキップされます。

## heartbeat プロンプトの目的

デフォルトのプロンプトは意図的に広い内容になっています。

- **バックグラウンドタスク**: 「未処理のタスクを検討する」という指示により、エージェントは
  フォローアップ（受信箱、カレンダー、リマインダー、キューに入った作業）を見直し、
  緊急性のあるものを通知しやすくなります。
- **人への確認**: 「日中にときどき人間の様子を確認する」という指示により、
  時折「何か必要ですか？」という軽い確認メッセージを促しますが、設定されたローカルタイムゾーンを使うことで
  夜間のスパムは避けます（[/concepts/timezone](/ja-JP/concepts/timezone) を参照）。

Heartbeat は完了した [background tasks](/ja-JP/automation/tasks) に反応できますが、heartbeat 実行自体ではタスクレコードは作成されません。

Heartbeat に非常に具体的なこと（たとえば「Gmail PubSub
統計を確認する」や「gateway の健全性を確認する」）をさせたい場合は、`agents.defaults.heartbeat.prompt`（または
`agents.list[].heartbeat.prompt`）をカスタム本文に設定してください（そのまま送信されます）。

## 応答契約

- 注意すべきことが何もなければ、**`HEARTBEAT_OK`** で応答します。
- Heartbeat 実行中、OpenClaw は応答の **先頭または末尾** に `HEARTBEAT_OK` が
  ある場合、それを ack として扱います。このトークンは取り除かれ、残りの内容が
  **≤ `ackMaxChars`**（デフォルト: 300）であれば応答は破棄されます。
- `HEARTBEAT_OK` が応答の **途中** に現れた場合は、特別扱いされません。
- アラートでは、**`HEARTBEAT_OK` を含めないでください**。アラート本文のみを返します。

Heartbeat 以外では、メッセージの先頭または末尾にある余分な `HEARTBEAT_OK` は除去されてログ記録されます。
メッセージが `HEARTBEAT_OK` のみの場合は破棄されます。

## 設定

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m", // デフォルト: 30m（0m で無効化）
        model: "anthropic/claude-opus-4-6",
        includeReasoning: false, // デフォルト: false（利用可能な場合は別の Reasoning: メッセージを配信）
        lightContext: false, // デフォルト: false。true でワークスペースのブートストラップファイルから HEARTBEAT.md のみ保持
        isolatedSession: false, // デフォルト: false。true で各 heartbeat を新しいセッションで実行（会話履歴なし）
        target: "last", // デフォルト: none | 選択肢: last | none | <channel id>（コアまたはプラグイン、例: "bluebubbles"）
        to: "+15551234567", // 任意のチャネル固有オーバーライド
        accountId: "ops-bot", // 任意のマルチアカウントチャネル ID
        prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        ackMaxChars: 300, // HEARTBEAT_OK の後に許容される最大文字数
      },
    },
  },
}
```

### スコープと優先順位

- `agents.defaults.heartbeat` はグローバルな heartbeat 動作を設定します。
- `agents.list[].heartbeat` はその上にマージされます。いずれかのエージェントに `heartbeat` ブロックがある場合、**そのエージェントだけ** が heartbeat を実行します。
- `channels.defaults.heartbeat` はすべてのチャネルの可視性デフォルトを設定します。
- `channels.<channel>.heartbeat` はチャネルデフォルトを上書きします。
- `channels.<channel>.accounts.<id>.heartbeat`（マルチアカウントチャネル）はチャネル単位設定を上書きします。

### エージェントごとの Heartbeat

いずれかの `agents.list[]` エントリに `heartbeat` ブロックが含まれている場合、**そのエージェントだけ**
が heartbeat を実行します。エージェント単位のブロックは `agents.defaults.heartbeat`
の上にマージされます（そのため、共有デフォルトを 1 回設定して、エージェントごとに上書きできます）。

例: 2 つのエージェントがあり、2 番目のエージェントだけが heartbeat を実行します。

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先へ明示的に配信（デフォルトは "none"）
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
          prompt: "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.",
        },
      },
    ],
  },
}
```

### アクティブ時間帯の例

特定のタイムゾーンの営業時間内に heartbeat を制限する場合:

```json5
{
  agents: {
    defaults: {
      heartbeat: {
        every: "30m",
        target: "last", // 最後の連絡先へ明示的に配信（デフォルトは "none"）
        activeHours: {
          start: "09:00",
          end: "22:00",
          timezone: "America/New_York", // 任意。設定されていれば userTimezone を使い、なければホストのタイムゾーン
        },
      },
    },
  },
}
```

この時間帯（東部時間の午前 9 時前または午後 10 時以降）の外では、heartbeat はスキップされます。次に予定されている、その時間帯内の tick で通常どおり実行されます。

### 24 時間 365 日の設定

Heartbeat を終日実行したい場合は、次のいずれかのパターンを使用してください。

- `activeHours` を完全に省略する（時間帯の制限なし。これがデフォルトの動作です）。
- 終日ウィンドウを設定する: `activeHours: { start: "00:00", end: "24:00" }`。

`start` と `end` に同じ時刻（たとえば `08:00` から `08:00`）を設定しないでください。
これは幅ゼロのウィンドウとして扱われるため、heartbeat は常にスキップされます。

### マルチアカウントの例

Telegram のようなマルチアカウントチャネルで特定アカウントを対象にするには `accountId` を使います。

```json5
{
  agents: {
    list: [
      {
        id: "ops",
        heartbeat: {
          every: "1h",
          target: "telegram",
          to: "12345678:topic:42", // 任意: 特定の topic / thread にルーティング
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

- `every`: heartbeat の間隔（duration 文字列。デフォルト単位 = 分）。
- `model`: heartbeat 実行用の任意のモデル上書き（`provider/model`）。
- `includeReasoning`: 有効時、利用可能であれば別の `Reasoning:` メッセージも配信します（`/reasoning on` と同じ形式）。
- `lightContext`: true の場合、heartbeat 実行では軽量ブートストラップコンテキストを使用し、ワークスペースのブートストラップファイルから `HEARTBEAT.md` のみ保持します。
- `isolatedSession`: true の場合、各 heartbeat は以前の会話履歴なしの新しいセッションで実行されます。cron の `sessionTarget: "isolated"` と同じ分離パターンを使います。heartbeat ごとのトークンコストを大幅に削減します。最大限節約したい場合は `lightContext: true` と組み合わせてください。配信ルーティングは引き続きメインセッションのコンテキストを使います。
- `session`: heartbeat 実行用の任意のセッションキー。
  - `main`（デフォルト）: エージェントのメインセッション。
  - 明示的なセッションキー（`openclaw sessions --json` または [sessions CLI](/cli/sessions) からコピー）。
  - セッションキー形式については [Sessions](/ja-JP/concepts/session) と [Groups](/ja-JP/channels/groups) を参照してください。
- `target`:
  - `last`: 最後に使われた外部チャネルへ配信します。
  - 明示的なチャネル: 任意の設定済みチャネルまたはプラグイン ID。たとえば `discord`、`matrix`、`telegram`、`whatsapp`。
  - `none`（デフォルト）: heartbeat は実行しますが、外部には **配信しません**。
- `directPolicy`: 直接 / DM 配信の動作を制御します。
  - `allow`（デフォルト）: 直接 / DM への heartbeat 配信を許可します。
  - `block`: 直接 / DM 配信を抑止します（`reason=dm-blocked`）。
- `to`: 任意の受信者上書き（チャネル固有 ID。例: WhatsApp の E.164 や Telegram の chat id）。Telegram の topic / thread には `<chatId>:topic:<messageThreadId>` を使用します。
- `accountId`: マルチアカウントチャネル向けの任意のアカウント ID。`target: "last"` の場合、解決された最後のチャネルがアカウントをサポートしていればそのアカウント ID が適用され、そうでなければ無視されます。アカウント ID が解決されたチャネルの設定済みアカウントと一致しない場合、配信はスキップされます。
- `prompt`: デフォルトのプロンプト本文を上書きします（マージはされません）。
- `ackMaxChars`: 配信前に `HEARTBEAT_OK` の後ろに許容される最大文字数。
- `suppressToolErrorWarnings`: true の場合、heartbeat 実行中のツールエラー警告ペイロードを抑止します。
- `activeHours`: heartbeat 実行を時間帯に制限します。`start`（HH:MM、含む。日の開始には `00:00` を使用）、`end`（HH:MM、含まない。日の終わりには `24:00` が利用可）、および任意の `timezone` を持つオブジェクトです。
  - 省略または `"user"`: `agents.defaults.userTimezone` が設定されていればそれを使い、そうでなければホストシステムのタイムゾーンにフォールバックします。
  - `"local"`: 常にホストシステムのタイムゾーンを使います。
  - 任意の IANA 識別子（例: `America/New_York`）: それを直接使用します。無効な場合は上記の `"user"` 動作にフォールバックします。
  - `start` と `end` はアクティブウィンドウでは同じ値にしてはいけません。同じ値は幅ゼロ（常にウィンドウ外）として扱われます。
  - アクティブウィンドウ外では、次回そのウィンドウ内に入る tick まで heartbeat はスキップされます。

## 配信動作

- Heartbeat はデフォルトでエージェントのメインセッション（`agent:<id>:<mainKey>`）で実行され、
  `session.scope = "global"` の場合は `global` で実行されます。特定の
  チャネルセッション（Discord / WhatsApp など）に上書きするには `session` を設定します。
- `session` は実行コンテキストにのみ影響します。配信は `target` と `to` によって制御されます。
- 特定のチャネル / 受信者に配信するには、`target` + `to` を設定します。
  `target: "last"` の場合、配信はそのセッションの最後の外部チャネルを使います。
- Heartbeat 配信はデフォルトで直接 / DM 宛先を許可します。直接宛先への送信を抑止しつつ heartbeat ターンは実行したい場合は、`directPolicy: "block"` を設定してください。
- メインキューがビジーの場合、heartbeat はスキップされ、後で再試行されます。
- `target` が外部宛先に解決されない場合でも、実行自体は行われますが、
  外向きメッセージは送信されません。
- `showOk`、`showAlerts`、`useIndicator` がすべて無効な場合、実行は `reason=alerts-disabled` として事前にスキップされます。
- アラート配信だけが無効な場合でも、OpenClaw は heartbeat を実行し、期限タスクのタイムスタンプを更新し、セッションの idle タイムスタンプを復元し、外向きアラートペイロードを抑止できます。
- heartbeat 専用の応答はセッションをアクティブのままにしません。最後の `updatedAt`
  は復元されるため、アイドル期限切れは通常どおり動作します。
- 切り離された [background tasks](/ja-JP/automation/tasks) は、メインセッションが何かにすばやく気付くべきときにシステムイベントをキューに積み、heartbeat を起こすことができます。この wake によって heartbeat 実行が background task になることはありません。

## 可視性の制御

デフォルトでは、`HEARTBEAT_OK` の確認応答は抑止され、アラート内容のみが
配信されます。これをチャネルごと、またはアカウントごとに調整できます。

```yaml
channels:
  defaults:
    heartbeat:
      showOk: false # HEARTBEAT_OK を隠す（デフォルト）
      showAlerts: true # アラートメッセージを表示（デフォルト）
      useIndicator: true # indicator イベントを送出（デフォルト）
  telegram:
    heartbeat:
      showOk: true # Telegram では OK 確認応答を表示
  whatsapp:
    accounts:
      work:
        heartbeat:
          showAlerts: false # このアカウントではアラート配信を抑止
```

優先順位: アカウント単位 → チャネル単位 → チャネルデフォルト → 組み込みデフォルト。

### 各フラグの役割

- `showOk`: モデルが OK のみの応答を返したときに `HEARTBEAT_OK` 確認応答を送信します。
- `showAlerts`: モデルが OK 以外の応答を返したときにアラート内容を送信します。
- `useIndicator`: UI のステータス表示用に indicator イベントを送出します。

**3 つすべて** が false の場合、OpenClaw は heartbeat 実行自体をスキップします（モデル呼び出しなし）。

### チャネル単位とアカウント単位の例

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
          showAlerts: false # ops アカウントに対してのみアラートを抑止
  telegram:
    heartbeat:
      showOk: true
```

### よくあるパターン

| 目的 | 設定 |
| ---------------------------------------- | ---------------------------------------------------------------------------------------- |
| デフォルト動作（OK は無言、アラートは送信） | _(設定不要)_ |
| 完全に無言（メッセージなし、indicator なし） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: false }` |
| indicator のみ（メッセージなし） | `channels.defaults.heartbeat: { showOk: false, showAlerts: false, useIndicator: true }` |
| 1 つのチャネルでのみ OK を表示 | `channels.telegram.heartbeat: { showOk: true }` |

## HEARTBEAT.md（任意）

ワークスペースに `HEARTBEAT.md` ファイルが存在する場合、デフォルトプロンプトは
エージェントにそれを読むよう指示します。これは「heartbeat チェックリスト」と考えてください。小さく、安定していて、
30 分ごとに含めても安全なものが理想です。

通常実行では、`HEARTBEAT.md` はデフォルトエージェントで heartbeat ガイダンスが
有効な場合にのみ注入されます。
間隔を `0m` にして heartbeat を無効にするか、
`includeSystemPromptSection: false` を設定すると、通常のブートストラップ
コンテキストからは除外されます。

`HEARTBEAT.md` が存在しても実質的に空（空行と `# Heading` のような markdown
見出しだけ）の場合、OpenClaw は API 呼び出しを節約するため heartbeat 実行をスキップします。
このスキップは `reason=empty-heartbeat-file` として報告されます。
ファイルが存在しない場合でも heartbeat は実行され、何をするかはモデルが判断します。

プロンプト肥大化を避けるため、小さく保ってください（短いチェックリストやリマインダー）。

`HEARTBEAT.md` の例:

```md
# Heartbeat checklist

- Quick scan: anything urgent in inboxes?
- If it’s daytime, do a lightweight check-in if nothing else is pending.
- If a task is blocked, write down _what is missing_ and ask Peter next time.
```

### `tasks:` ブロック

`HEARTBEAT.md` は、heartbeat 自体の中で間隔ベースの確認を行うための、
小さな構造化 `tasks:` ブロックもサポートしています。

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
- その tick で **期限到来** しているタスクだけが heartbeat プロンプトに含まれます。
- 期限到来タスクがない場合、無駄なモデル呼び出しを避けるため heartbeat は完全にスキップされます（`reason=no-tasks-due`）。
- `HEARTBEAT.md` のタスク以外の内容は保持され、期限到来タスクリストの後に追加コンテキストとして付加されます。
- タスクの前回実行タイムスタンプはセッション状態（`heartbeatTaskState`）に保存されるため、通常の再起動をまたいでも間隔は維持されます。
- タスクタイムスタンプが進むのは、heartbeat 実行が通常の応答経路を完了した後だけです。`empty-heartbeat-file` / `no-tasks-due` によるスキップ実行では、タスクは完了済みとして記録されません。

タスクモードは、1 つの heartbeat ファイルに複数の定期チェックを持たせつつ、毎 tick ですべてのコストを払いたくない場合に便利です。

### エージェントは HEARTBEAT.md を更新できますか？

はい。そうするように指示すれば可能です。

`HEARTBEAT.md` はエージェントのワークスペース内の通常のファイルなので、
通常のチャットで次のように指示できます。

- 「毎日のカレンダー確認を追加するように `HEARTBEAT.md` を更新して。」
- 「もっと短くして受信箱のフォローアップに集中するよう `HEARTBEAT.md` を書き直して。」

これを能動的に行いたい場合は、heartbeat プロンプトに次のような明示的な一文を
入れることもできます。「チェックリストが古くなったら、よりよいものに `HEARTBEAT.md`
を更新すること。」

安全上の注意: 秘密情報（API キー、電話番号、プライベートトークン）は
`HEARTBEAT.md` に入れないでください。これはプロンプトコンテキストの一部になります。

## 手動 wake（オンデマンド）

次のコマンドでシステムイベントをキューに積み、即時 heartbeat を発火できます。

```bash
openclaw system event --text "Check for urgent follow-ups" --mode now
```

複数のエージェントに `heartbeat` が設定されている場合、手動 wake はそれらの
エージェント heartbeat をすべて即時実行します。

次回予定 tick まで待つには `--mode next-heartbeat` を使用してください。

## Reasoning 配信（任意）

デフォルトでは、heartbeat は最終的な「answer」ペイロードだけを配信します。

透明性が必要な場合は、次を有効にしてください。

- `agents.defaults.heartbeat.includeReasoning: true`

有効にすると、heartbeat は `Reasoning:` で始まる別メッセージも配信します
（`/reasoning on` と同じ形式）。これは、エージェントが複数のセッション / codex を管理していて、
なぜあなたに ping することにしたのか見たい場合に便利です。
ただし、望まない内部詳細がより多く漏れる可能性もあります。グループチャットでは
無効のままにしておくことを推奨します。

## コスト意識

Heartbeat は完全なエージェントターンを実行します。間隔を短くするほどトークン消費は増えます。コストを下げるには:

- `isolatedSession: true` を使って会話履歴全体の送信を避ける（約 100K トークンから 1 回あたり約 2〜5K に削減）。
- `lightContext: true` を使ってブートストラップファイルを `HEARTBEAT.md` だけに制限する。
- より安価な `model` を設定する（例: `ollama/llama3.2:1b`）。
- `HEARTBEAT.md` を小さく保つ。
- 内部状態更新だけが目的なら `target: "none"` を使う。

## 関連

- [Automation & Tasks](/ja-JP/automation) — 自動化の仕組み全体の概要
- [Background Tasks](/ja-JP/automation/tasks) — 切り離された作業の追跡方法
- [Timezone](/ja-JP/concepts/timezone) — タイムゾーンが heartbeat スケジューリングに与える影響
- [Troubleshooting](/ja-JP/automation/cron-jobs#troubleshooting) — 自動化の問題をデバッグする方法
