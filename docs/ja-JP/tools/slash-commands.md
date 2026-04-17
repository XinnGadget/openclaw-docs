---
read_when:
    - チャットコマンドを使用または設定している場合
    - コマンドのルーティングや権限をデバッグしている場合
summary: 'スラッシュコマンド: テキストとネイティブ、設定、サポートされるコマンド'
title: スラッシュコマンド
x-i18n:
    generated_at: "2026-04-12T23:34:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ef6f54500fa2ce3b873a8398d6179a0882b8bf6fba38f61146c64671055505e
    source_path: tools/slash-commands.md
    workflow: 15
---

# スラッシュコマンド

コマンドは Gateway によって処理されます。ほとんどのコマンドは、`/` で始まる**単独の**メッセージとして送信する必要があります。
ホスト専用の bash チャットコマンドは `! <cmd>` を使います（`/bash <cmd>` はエイリアスです）。

関連するシステムは2つあります:

- **コマンド**: 単独の `/...` メッセージ。
- **ディレクティブ**: `/think`、`/fast`、`/verbose`、`/trace`、`/reasoning`、`/elevated`、`/exec`、`/model`、`/queue`。
  - ディレクティブは、モデルがメッセージを見る前に取り除かれます。
  - 通常のチャットメッセージ内では（ディレクティブのみのメッセージではない場合）、それらは「インラインヒント」として扱われ、セッション設定には**保持されません**。
  - ディレクティブのみのメッセージでは（メッセージがディレクティブだけを含む場合）、それらはセッションに保持され、確認応答が返ります。
  - ディレクティブは**認可された送信者**にのみ適用されます。`commands.allowFrom` が設定されている場合、それが使われる唯一の
    allowlist です。そうでない場合、認可はチャネル allowlist/ペアリングと `commands.useAccessGroups` から来ます。
    認可されていない送信者には、ディレクティブはプレーンテキストとして扱われます。

さらに、いくつかの**インラインショートカット**もあります（allowlist 済み/認可済み送信者のみ）: `/help`、`/commands`、`/status`、`/whoami`（`/id`）。
これらは即座に実行され、モデルが見る前に取り除かれ、残りのテキストは通常のフローを続行します。

## 設定

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text`（デフォルト `true`）は、チャットメッセージ内での `/...` のパースを有効にします。
  - ネイティブコマンドのないサーフェス（WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams）では、これを `false` に設定してもテキストコマンドは引き続き動作します。
- `commands.native`（デフォルト `"auto"`）は、ネイティブコマンドを登録します。
  - auto: Discord/Telegram ではオン、Slack ではオフ（スラッシュコマンドを追加するまでは）。ネイティブ非対応プロバイダでは無視されます。
  - プロバイダごとに上書きするには、`channels.discord.commands.native`、`channels.telegram.commands.native`、`channels.slack.commands.native` を設定します（bool または `"auto"`）。
  - `false` にすると、起動時に Discord/Telegram で以前登録されたコマンドを削除します。Slack コマンドは Slack アプリ内で管理され、自動では削除されません。
- `commands.nativeSkills`（デフォルト `"auto"`）は、サポートされている場合に **skill** コマンドをネイティブ登録します。
  - auto: Discord/Telegram ではオン、Slack ではオフ（Slack では skill ごとにスラッシュコマンドを作成する必要があります）。
  - プロバイダごとに上書きするには、`channels.discord.commands.nativeSkills`、`channels.telegram.commands.nativeSkills`、`channels.slack.commands.nativeSkills` を設定します（bool または `"auto"`）。
- `commands.bash`（デフォルト `false`）は、ホストシェルコマンドを実行する `! <cmd>` を有効にします（`/bash <cmd>` はエイリアス。`tools.elevated` の allowlist が必要）。
- `commands.bashForegroundMs`（デフォルト `2000`）は、bash がバックグラウンドモードへ切り替わるまで待機する時間を制御します（`0` は即座にバックグラウンド化）。
- `commands.config`（デフォルト `false`）は `/config` を有効にします（`openclaw.json` の読み書き）。
- `commands.mcp`（デフォルト `false`）は `/mcp` を有効にします（`mcp.servers` 配下の OpenClaw 管理 MCP 設定の読み書き）。
- `commands.plugins`（デフォルト `false`）は `/plugins` を有効にします（Plugin のディスカバリ/ステータス、および install + enable/disable 制御）。
- `commands.debug`（デフォルト `false`）は `/debug` を有効にします（ランタイム専用オーバーライド）。
- `commands.restart`（デフォルト `true`）は `/restart` と gateway 再起動ツールアクションを有効にします。
- `commands.ownerAllowFrom`（任意）は、owner 専用コマンド/ツールサーフェス用の明示的な owner allowlist を設定します。これは `commands.allowFrom` とは別です。
- `commands.ownerDisplay` は、システムプロンプト内で owner id をどのように表示するかを制御します: `raw` または `hash`。
- `commands.ownerDisplaySecret` は、`commands.ownerDisplay="hash"` の場合に使う HMAC シークレットを任意で設定します。
- `commands.allowFrom`（任意）は、コマンド認可用のプロバイダ別 allowlist を設定します。設定されている場合、これはコマンドとディレクティブに使われる
  唯一の認可ソースであり（チャネル allowlist/ペアリングと `commands.useAccessGroups` は無視されます）。グローバルデフォルトには `"*"` を使い、プロバイダ別キーがそれを上書きします。
- `commands.useAccessGroups`（デフォルト `true`）は、`commands.allowFrom` が設定されていない場合に、コマンドに対して allowlist/ポリシーを強制します。

## コマンド一覧

現在の信頼できる情報源:

- コア組み込みコマンドは `src/auto-reply/commands-registry.shared.ts` から来ます
- 生成される dock コマンドは `src/auto-reply/commands-registry.data.ts` から来ます
- Plugin コマンドは Plugin の `registerCommand()` 呼び出しから来ます
- 実際にあなたの gateway で利用可能かどうかは、依然として設定フラグ、チャネルサーフェス、install/有効化された Plugin に依存します

### コア組み込みコマンド

現在利用可能な組み込みコマンド:

- `/new [model]` は新しいセッションを開始します。`/reset` はリセットのエイリアスです。
- `/compact [instructions]` はセッションコンテキストを Compaction します。参照: [/concepts/compaction](/ja-JP/concepts/compaction)。
- `/stop` は現在の実行を中断します。
- `/session idle <duration|off>` と `/session max-age <duration|off>` は、スレッドバインディングの有効期限を管理します。
- `/think <off|minimal|low|medium|high|xhigh>` は thinking レベルを設定します。エイリアス: `/thinking`、`/t`。
- `/verbose on|off|full` は詳細出力を切り替えます。エイリアス: `/v`。
- `/trace on|off` は現在のセッションの Plugin トレース出力を切り替えます。
- `/fast [status|on|off]` は fast mode を表示または設定します。
- `/reasoning [on|off|stream]` は reasoning の可視性を切り替えます。エイリアス: `/reason`。
- `/elevated [on|off|ask|full]` は elevated mode を切り替えます。エイリアス: `/elev`。
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` は exec のデフォルトを表示または設定します。
- `/model [name|#|status]` はモデルを表示または設定します。
- `/models [provider] [page] [limit=<n>|size=<n>|all]` はプロバイダまたは、あるプロバイダのモデルを一覧表示します。
- `/queue <mode>` はキュー動作を管理します（`steer`、`interrupt`、`followup`、`collect`、`steer-backlog`）および `debounce:2s cap:25 drop:summarize` のようなオプション。
- `/help` は短いヘルプ要約を表示します。
- `/commands` は生成されたコマンドカタログを表示します。
- `/tools [compact|verbose]` は、現在のエージェントが今使えるものを表示します。
- `/status` はランタイムステータスを表示し、利用可能な場合はプロバイダの使用量/クォータも含みます。
- `/tasks` は現在のセッションのアクティブ/最近のバックグラウンドタスクを一覧表示します。
- `/context [list|detail|json]` は、コンテキストがどのように組み立てられるかを説明します。
- `/export-session [path]` は現在のセッションを HTML にエクスポートします。エイリアス: `/export`。
- `/whoami` はあなたの sender id を表示します。エイリアス: `/id`。
- `/skill <name> [input]` は名前で skill を実行します。
- `/allowlist [list|add|remove] ...` は allowlist エントリを管理します。テキスト専用です。
- `/approve <id> <decision>` は exec 承認プロンプトを解決します。
- `/btw <question>` は、将来のセッションコンテキストを変更せずに横道の質問をします。参照: [/tools/btw](/ja-JP/tools/btw)。
- `/subagents list|kill|log|info|send|steer|spawn` は、現在のセッションのサブエージェント実行を管理します。
- `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` は ACP セッションとランタイムオプションを管理します。
- `/focus <target>` は、現在の Discord スレッドまたは Telegram トピック/会話をセッションターゲットにバインドします。
- `/unfocus` は現在のバインディングを削除します。
- `/agents` は現在のセッションにスレッドバインドされたエージェントを一覧表示します。
- `/kill <id|#|all>` は1つまたはすべての実行中サブエージェントを中断します。
- `/steer <id|#> <message>` は実行中のサブエージェントにステアリングを送ります。エイリアス: `/tell`。
- `/config show|get|set|unset` は `openclaw.json` を読み書きします。owner 専用。`commands.config: true` が必要です。
- `/mcp show|get|set|unset` は `mcp.servers` 配下の OpenClaw 管理 MCP サーバー設定を読み書きします。owner 専用。`commands.mcp: true` が必要です。
- `/plugins list|inspect|show|get|install|enable|disable` は Plugin 状態を調査または変更します。`/plugin` はエイリアスです。書き込みは owner 専用。`commands.plugins: true` が必要です。
- `/debug show|set|unset|reset` はランタイム専用設定オーバーライドを管理します。owner 専用。`commands.debug: true` が必要です。
- `/usage off|tokens|full|cost` は、応答ごとの使用量フッターを制御するか、ローカルなコスト要約を表示します。
- `/tts on|off|status|provider|limit|summary|audio|help` は TTS を制御します。参照: [/tools/tts](/ja-JP/tools/tts)。
- `/restart` は、有効な場合に OpenClaw を再起動します。デフォルト: 有効。無効にするには `commands.restart: false` を設定します。
- `/activation mention|always` はグループ activation mode を設定します。
- `/send on|off|inherit` は send policy を設定します。owner 専用。
- `/bash <command>` はホストシェルコマンドを実行します。テキスト専用。エイリアス: `! <command>`。`commands.bash: true` と `tools.elevated` の allowlist が必要です。
- `!poll [sessionId]` はバックグラウンド bash ジョブを確認します。
- `!stop [sessionId]` はバックグラウンド bash ジョブを停止します。

### 生成される dock コマンド

Dock コマンドは、ネイティブコマンド対応のチャネル Plugin から生成されます。現在のバンドルセット:

- `/dock-discord`（エイリアス: `/dock_discord`）
- `/dock-mattermost`（エイリアス: `/dock_mattermost`）
- `/dock-slack`（エイリアス: `/dock_slack`）
- `/dock-telegram`（エイリアス: `/dock_telegram`）

### バンドル Plugin コマンド

バンドル Plugin は、さらにスラッシュコマンドを追加できます。このリポジトリ内の現在のバンドルコマンド:

- `/dreaming [on|off|status|help]` は memory Dreaming を切り替えます。参照: [Dreaming](/ja-JP/concepts/dreaming)。
- `/pair [qr|status|pending|approve|cleanup|notify]` はデバイスのペアリング/setup フローを管理します。参照: [ペアリング](/ja-JP/channels/pairing)。
- `/phone status|arm <camera|screen|writes|all> [duration]|disarm` は、高リスクな phone Node コマンドを一時的に有効化します。
- `/voice status|list [limit]|set <voiceId|name>` は Talk voice 設定を管理します。Discord では、ネイティブコマンド名は `/talkvoice` です。
- `/card ...` は LINE rich card プリセットを送信します。参照: [LINE](/ja-JP/channels/line)。
- `/codex status|models|threads|resume|compact|review|account|mcp|skills` は、バンドルされた Codex app-server harness を調査および制御します。参照: [Codex Harness](/ja-JP/plugins/codex-harness)。
- QQBot 専用コマンド:
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### 動的 skill コマンド

ユーザーが呼び出せる Skills もスラッシュコマンドとして公開されます:

- `/skill <name> [input]` は常に汎用エントリポイントとして機能します。
- skill/plugin がそれらを登録している場合、`/prose` のような直接コマンドとして現れることもあります。
- ネイティブ skill-command 登録は、`commands.nativeSkills` と `channels.<provider>.commands.nativeSkills` によって制御されます。

注記:

- コマンドは、コマンドと引数の間に任意で `:` を受け付けます（例: `/think: high`、`/send: on`、`/help:`）。
- `/new <model>` はモデルエイリアス、`provider/model`、またはプロバイダ名（あいまい一致）を受け付けます。一致しない場合、そのテキストはメッセージ本文として扱われます。
- プロバイダ使用量の完全な内訳には、`openclaw status --usage` を使ってください。
- `/allowlist add|remove` には `commands.config=true` が必要で、チャネルの `configWrites` を尊重します。
- マルチアカウントチャネルでは、設定対象の `/allowlist --account <id>` と `/config set channels.<provider>.accounts.<id>...` も、対象アカウントの `configWrites` を尊重します。
- `/usage` は応答ごとの使用量フッターを制御します。`/usage cost` は OpenClaw セッションログからローカルなコスト要約を表示します。
- `/restart` はデフォルトで有効です。無効にするには `commands.restart: false` を設定します。
- `/plugins install <spec>` は `openclaw plugins install` と同じ Plugin 指定を受け付けます: ローカルパス/アーカイブ、npm package、または `clawhub:<pkg>`。
- `/plugins enable|disable` は Plugin 設定を更新し、再起動を促すことがあります。
- Discord 専用ネイティブコマンド: `/vc join|leave|status` は音声チャンネルを制御します（`channels.discord.voice` とネイティブコマンドが必要。テキストでは利用不可）。
- Discord のスレッドバインディングコマンド（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`）には、実効的なスレッドバインディングが有効である必要があります（`session.threadBindings.enabled` および/または `channels.discord.threadBindings.enabled`）。
- ACP コマンドリファレンスとランタイム動作: [ACP Agents](/ja-JP/tools/acp-agents)。
- `/verbose` はデバッグと追加の可視性のためのものです。通常利用では **off** のままにしてください。
- `/trace` は `/verbose` より狭いものです。Plugin 所有のトレース/デバッグ行のみを表示し、通常の詳細なツール chatter はオフのままにします。
- `/fast on|off` はセッションオーバーライドを保持します。Sessions UI の `inherit` オプションを使うと、それを消去して設定デフォルトにフォールバックできます。
- `/fast` はプロバイダ固有です。OpenAI/OpenAI Codex ではネイティブ Responses エンドポイント上の `service_tier=priority` にマップされ、直接の公開 Anthropic リクエストでは、`api.anthropic.com` に送られる OAuth 認証済みトラフィックを含め、`service_tier=auto` または `standard_only` にマップされます。参照: [OpenAI](/ja-JP/providers/openai) と [Anthropic](/ja-JP/providers/anthropic)。
- ツール失敗の要約は関連がある場合には引き続き表示されますが、詳細な失敗テキストは `/verbose` が `on` または `full` のときにのみ含まれます。
- `/reasoning`、`/verbose`、`/trace` はグループ設定ではリスクがあります。意図せず内部 reasoning、ツール出力、または Plugin 診断を露出する可能性があります。特にグループチャットでは、オフのままにしておくことを推奨します。
- `/model` は新しいセッションモデルを即座に保持します。
- エージェントがアイドルなら、次の実行でただちに使われます。
- すでに実行がアクティブな場合、OpenClaw はライブ切り替えを保留としてマークし、クリーンな再試行ポイントでのみ新しいモデルへ再起動します。
- すでにツール動作または返信出力が始まっている場合、その保留切り替えは、後の再試行機会または次のユーザーターンまでキューに残ることがあります。
- **Fast path:** allowlist 済み送信者からのコマンド専用メッセージは即座に処理されます（キュー + モデルをバイパス）。
- **グループ mention ゲーティング:** allowlist 済み送信者からのコマンド専用メッセージは mention 要件をバイパスします。
- **インラインショートカット（allowlist 済み送信者のみ）:** 特定のコマンドは通常メッセージ内に埋め込まれていても動作し、残りのテキストをモデルが見る前に取り除かれます。
  - 例: `hey /status` はステータス返信をトリガーし、残りのテキストは通常フローを続行します。
- 現在: `/help`、`/commands`、`/status`、`/whoami`（`/id`）。
- 認可されていないコマンド専用メッセージは黙って無視され、インライン `/...` トークンはプレーンテキストとして扱われます。
- **skill コマンド:** `user-invocable` Skills はスラッシュコマンドとして公開されます。名前は `a-z0-9_` にサニタイズされ（最大32文字）、衝突した場合は数値サフィックスが付きます（例: `_2`）。
  - `/skill <name> [input]` は名前で skill を実行します（ネイティブコマンドの制限により skill ごとのコマンドが使えない場合に便利です）。
  - デフォルトでは、skill コマンドは通常のリクエストとしてモデルに転送されます。
  - Skills は任意で `command-dispatch: tool` を宣言でき、コマンドを直接ツールへルーティングできます（決定的で、モデルなし）。
  - 例: `/prose`（OpenProse Plugin）— 参照: [OpenProse](/ja-JP/prose)。
- **ネイティブコマンド引数:** Discord では動的オプションにオートコンプリートを使います（必須引数を省略した場合はボタンメニューも表示）。Telegram と Slack では、コマンドが選択肢をサポートしていて引数を省略した場合、ボタンメニューを表示します。

## `/tools`

`/tools` が答えるのは設定上の問いではなく、ランタイム上の問いです: **この会話でこのエージェントが今使えるものは何か**。

- デフォルトの `/tools` はコンパクトで、素早く確認できるよう最適化されています。
- `/tools verbose` は短い説明を追加します。
- 引数をサポートするネイティブコマンドサーフェスでは、同じモード切り替え `compact|verbose` を公開します。
- 結果はセッションスコープなので、エージェント、チャネル、スレッド、送信者認可、またはモデルを変えると出力も変わることがあります。
- `/tools` には、コアツール、接続された Plugin ツール、チャネル所有ツールを含め、実際にランタイムで到達可能なツールが含まれます。

プロファイルやオーバーライドの編集には、`/tools` を静的カタログとして扱うのではなく、Control UI の Tools パネルまたは設定/カタログサーフェスを使ってください。

## 使用量サーフェス（どこに何が表示されるか）

- **プロバイダ使用量/クォータ**（例: 「Claude 80% left」）は、使用量トラッキングが有効な場合、現在のモデルプロバイダについて `/status` に表示されます。OpenClaw はプロバイダウィンドウを `% left` に正規化します。MiniMax では、remaining-only のパーセントフィールドは表示前に反転され、`model_remains` レスポンスでは、モデルタグ付きプランラベルに加えてチャットモデルエントリが優先されます。
- `/status` 内の **トークン/キャッシュ行** は、ライブセッションスナップショットが疎な場合、最新の transcript 使用量エントリへフォールバックできます。既存の非ゼロのライブ値が依然として優先され、保存済み合計が欠けているか小さすぎる場合、transcript フォールバックはアクティブなランタイムモデルラベルや、より大きいプロンプト指向の合計も復元できます。
- **応答ごとのトークン/コスト** は `/usage off|tokens|full` で制御されます（通常の返信に追記）。
- `/model status` は使用量ではなく、**モデル/認証/エンドポイント** に関するものです。

## モデル選択（`/model`）

`/model` はディレクティブとして実装されています。

例:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

注記:

- `/model` と `/model list` は、コンパクトで番号付きの picker（モデルファミリ + 利用可能なプロバイダ）を表示します。
- Discord では、`/model` と `/models` は、プロバイダとモデルのドロップダウンに Submit ステップを加えた対話型 picker を開きます。
- `/model <#>` はその picker から選択します（可能な場合は現在のプロバイダを優先します）。
- `/model status` は詳細ビューを表示し、利用可能な場合は設定済みプロバイダエンドポイント（`baseUrl`）と API mode（`api`）も含みます。

## デバッグオーバーライド

`/debug` を使うと、**ランタイム専用**の設定オーバーライド（ディスクではなくメモリ）を設定できます。owner 専用。デフォルトでは無効で、`commands.debug: true` で有効にします。

例:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

注記:

- オーバーライドは新しい設定読み取りに即座に適用されますが、`openclaw.json` には書き込みません。
- すべてのオーバーライドを消去してオンディスク設定へ戻るには `/debug reset` を使います。

## Plugin トレース出力

`/trace` を使うと、完全な verbose mode を有効にせずに、**セッションスコープの Plugin トレース/デバッグ行** を切り替えられます。

例:

```text
/trace
/trace on
/trace off
```

注記:

- 引数なしの `/trace` は、現在のセッショントレース状態を表示します。
- `/trace on` は、現在のセッションで Plugin トレース行を有効にします。
- `/trace off` はそれを再び無効にします。
- Plugin トレース行は `/status` に現れることがあり、通常のアシスタント返信後のフォローアップ診断メッセージとしても表示されることがあります。
- `/trace` は `/debug` の代わりではありません。`/debug` は引き続きランタイム専用設定オーバーライドを管理します。
- `/trace` は `/verbose` の代わりでもありません。通常の verbose なツール/ステータス出力は依然として `/verbose` に属します。

## 設定更新

`/config` は、オンディスク設定（`openclaw.json`）に書き込みます。owner 専用。デフォルトでは無効で、`commands.config: true` で有効にします。

例:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

注記:

- 書き込み前に設定は検証されます。不正な変更は拒否されます。
- `/config` の更新は再起動後も保持されます。

## MCP 更新

`/mcp` は、`mcp.servers` 配下の OpenClaw 管理 MCP サーバー定義を書き込みます。owner 専用。デフォルトでは無効で、`commands.mcp: true` で有効にします。

例:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

注記:

- `/mcp` は Pi 所有のプロジェクト設定ではなく、OpenClaw 設定に保存します。
- どのトランスポートが実際に実行可能かは、ランタイムアダプタが決定します。

## Plugin 更新

`/plugins` を使うと、オペレーターは発見済み Plugin を調査し、設定内で有効化を切り替えられます。読み取り専用フローでは `/plugin` をエイリアスとして使えます。デフォルトでは無効で、`commands.plugins: true` で有効にします。

例:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

注記:

- `/plugins list` と `/plugins show` は、現在のワークスペースとオンディスク設定に対する実際の Plugin ディスカバリを使います。
- `/plugins enable|disable` は Plugin 設定のみを更新し、Plugin を install または uninstall はしません。
- enable/disable の変更後は、適用のために gateway を再起動してください。

## サーフェスに関する注記

- **テキストコマンド** は通常のチャットセッション内で実行されます（DM は `main` を共有し、グループは独自のセッションを持ちます）。
- **ネイティブコマンド** は分離されたセッションを使います:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>`（接頭辞は `channels.slack.slashCommand.sessionPrefix` で設定可能）
  - Telegram: `telegram:slash:<userId>`（`CommandTargetSessionKey` を介してチャットセッションを対象にします）
- **`/stop`** はアクティブなチャットセッションを対象にし、現在の実行を中断できるようにします。
- **Slack:** `channels.slack.slashCommand` は、単一の `/openclaw` 形式コマンド用として引き続きサポートされています。`commands.native` を有効にする場合、組み込みコマンドごとに1つの Slack スラッシュコマンドを作成する必要があります（名前は `/help` と同じ）。Slack 向けのコマンド引数メニューは、一時的な Block Kit ボタンとして配信されます。
  - Slack ネイティブ例外: Slack は `/status` を予約しているため、`/status` ではなく `/agentstatus` を登録してください。テキストの `/status` は Slack メッセージ内で引き続き動作します。

## BTW 横道の質問

`/btw` は、現在のセッションについての素早い**横道の質問**です。

通常のチャットとは異なり、これは:

- 現在のセッションを背景コンテキストとして使い、
- 別個の**ツールなし** one-shot 呼び出しとして実行され、
- 将来のセッションコンテキストを変更せず、
- transcript 履歴には書き込まれず、
- 通常のアシスタントメッセージではなく、ライブの横道結果として配信されます。

これにより `/btw` は、メインの
タスクを進めたまま一時的な確認をしたいときに便利です。

例:

```text
/btw what are we doing right now?
```

完全な動作とクライアント UX の
詳細については [BTW 横道の質問](/ja-JP/tools/btw) を参照してください。
