---
read_when:
    - チャットコマンドを使う、または設定する場合
    - コマンドルーティングや権限をデバッグしている場合
summary: 'Slash command: テキストとネイティブ、設定、対応コマンド'
title: Slash Commands
x-i18n:
    generated_at: "2026-04-06T03:14:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 417e35b9ddd87f25f6c019111b55b741046ea11039dde89210948185ced5696d
    source_path: tools/slash-commands.md
    workflow: 15
---

# Slash Commands

コマンドは Gateway によって処理されます。ほとんどのコマンドは、`/` で始まる**単独の**メッセージとして送信する必要があります。
ホスト専用の bash チャットコマンドは `! <cmd>` を使用します（`/bash <cmd>` は alias）。

関連する 2 つのシステムがあります。

- **Commands**: 単独の `/...` メッセージ。
- **Directives**: `/think`、`/fast`、`/verbose`、`/reasoning`、`/elevated`、`/exec`、`/model`、`/queue`。
  - Directives は、モデルがメッセージを見る前に取り除かれます。
  - 通常のチャットメッセージ内（directive のみではない場合）では、「inline hint」として扱われ、session 設定は永続化されません。
  - Directive のみのメッセージ（メッセージに directive しか含まれない場合）では、session に永続化され、acknowledgement で応答します。
  - Directives は**認可された送信者**に対してのみ適用されます。`commands.allowFrom` が設定されている場合、それが唯一の allowlist として使われます。そうでない場合、認可はチャネル allowlist/pairing と `commands.useAccessGroups` から決まります。認可されていない送信者には、directives は通常のテキストとして扱われます。

さらに、いくつかの **inline shortcut**（allowlist 済み/認可済み送信者のみ）もあります: `/help`、`/commands`、`/status`、`/whoami`（`/id`）。
これらは即座に実行され、モデルがメッセージを見る前に取り除かれ、残りのテキストは通常フローに進みます。

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
    restart: false,
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text`（デフォルト `true`）は、チャットメッセージ内での `/...` の解析を有効にします。
  - ネイティブコマンドがないサーフェス（WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams）では、これを `false` に設定しても text command は引き続き動作します。
- `commands.native`（デフォルト `"auto"`）は、ネイティブコマンドを登録します。
  - Auto: Discord/Telegram ではオン、Slack ではオフ（slash command を追加するまで）、ネイティブサポートのないプロバイダーでは無視。
  - プロバイダーごとに上書きするには、`channels.discord.commands.native`、`channels.telegram.commands.native`、または `channels.slack.commands.native` を設定します（bool または `"auto"`）。
  - `false` は、起動時に Discord/Telegram で以前登録されたコマンドを削除します。Slack command は Slack app 側で管理されるため、自動では削除されません。
- `commands.nativeSkills`（デフォルト `"auto"`）は、サポートされる場合に **skill** command をネイティブ登録します。
  - Auto: Discord/Telegram ではオン、Slack ではオフ（Slack は skill ごとに 1 つの slash command 作成が必要）。
  - プロバイダーごとに上書きするには、`channels.discord.commands.nativeSkills`、`channels.telegram.commands.nativeSkills`、または `channels.slack.commands.nativeSkills` を設定します（bool または `"auto"`）。
- `commands.bash`（デフォルト `false`）は、ホスト shell command を実行する `! <cmd>` を有効にします（`/bash <cmd>` は alias。`tools.elevated` allowlist が必要）。
- `commands.bashForegroundMs`（デフォルト `2000`）は、bash が background mode に切り替わるまで待つ時間を制御します（`0` は即座に background 化）。
- `commands.config`（デフォルト `false`）は `/config` を有効にします（`openclaw.json` を読み書き）。
- `commands.mcp`（デフォルト `false`）は `/mcp` を有効にします（`mcp.servers` 配下の OpenClaw 管理 MCP 設定を読み書き）。
- `commands.plugins`（デフォルト `false`）は `/plugins` を有効にします（plugin discovery/status、および install + enable/disable 操作）。
- `commands.debug`（デフォルト `false`）は `/debug` を有効にします（ランタイム専用上書き）。
- `commands.allowFrom`（オプション）は、command 認可用のプロバイダーごとの allowlist を設定します。設定されている場合、それが command と directive の**唯一の**認可ソースになります（チャネル allowlist/pairing と `commands.useAccessGroups` は無視されます）。グローバルデフォルトには `"*"` を使用し、プロバイダー固有キーがそれを上書きします。
- `commands.useAccessGroups`（デフォルト `true`）は、`commands.allowFrom` が設定されていない場合に command に allowlist/policy を適用します。

## コマンド一覧

Text + native（有効な場合）:

- `/help`
- `/commands`
- `/tools [compact|verbose]`（現在の agent が今この場で何を使えるかを表示。`verbose` は説明を追加）
- `/skill <name> [input]`（名前で skill を実行）
- `/status`（現在の status を表示。利用可能な場合は、現在の model provider の provider usage/quota も含む）
- `/tasks`（現在の session の background task を一覧表示。agent ローカル fallback count を含む、active と最近の task 詳細を表示）
- `/allowlist`（allowlist entry の一覧/追加/削除）
- `/approve <id> <decision>`（exec approval prompt を解決。利用可能な decision は保留中の approval メッセージを使用）
- `/context [list|detail|json]`（「context」を説明。`detail` は file ごと + tool ごと + skill ごと + system prompt サイズを表示）
- `/btw <question>`（将来の session context を変更せずに、現在の session について一時的な side question を尋ねる。[/tools/btw](/ja-JP/tools/btw) を参照）
- `/export-session [path]`（alias: `/export`）（完全な system prompt 付きで現在の session を HTML に export）
- `/whoami`（自分の sender id を表示。alias: `/id`）
- `/session idle <duration|off>`（focused thread binding 向けの inactivity auto-unfocus を管理）
- `/session max-age <duration|off>`（focused thread binding 向けの hard max-age auto-unfocus を管理）
- `/subagents list|kill|log|info|send|steer|spawn`（現在の session の sub-agent 実行を調査、制御、または spawn）
- `/acp spawn|cancel|steer|close|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|sessions`（ACP runtime session を調査および制御）
- `/agents`（この session の thread-bound agent を一覧表示）
- `/focus <target>`（Discord: このスレッド、または新しいスレッドを、session/subagent target にバインド）
- `/unfocus`（Discord: 現在の thread binding を削除）
- `/kill <id|#|all>`（現在の session で実行中の 1 つまたはすべての sub-agent を即時中止。確認メッセージなし）
- `/steer <id|#> <message>`（実行中の sub-agent を即時 steer: 可能なら実行中に、そうでなければ現在の作業を中止して steer message で再開）
- `/tell <id|#> <message>`（`/steer` の alias）
- `/config show|get|set|unset`（設定をディスクへ永続化。owner-only。`commands.config: true` が必要）
- `/mcp show|get|set|unset`（OpenClaw MCP server 設定を管理。owner-only。`commands.mcp: true` が必要）
- `/plugins list|show|get|install|enable|disable`（discovery 済み plugin の確認、新しい plugin の install、有効/無効の切り替え。書き込みは owner-only。`commands.plugins: true` が必要）
  - `/plugin` は `/plugins` の alias。
  - `/plugin install <spec>` は `openclaw plugins install` と同じ plugin spec を受け付けます: ローカル path/archive、npm package、または `clawhub:<pkg>`。
  - Enable/disable の書き込みは、引き続き restart hint を返します。監視付き foreground gateway では、OpenClaw は書き込み直後にその restart を自動で実行することがあります。
- `/debug show|set|unset|reset`（runtime override。owner-only。`commands.debug: true` が必要）
- `/usage off|tokens|full|cost`（応答ごとの usage footer またはローカル cost summary）
- `/tts off|always|inbound|tagged|status|provider|limit|summary|audio`（TTS を制御。[/tts](/ja-JP/tools/tts) を参照）
  - Discord: ネイティブ command は `/voice`（Discord は `/tts` を予約済み）。text の `/tts` は引き続き動作。
- `/stop`
- `/restart`
- `/dock-telegram`（alias: `/dock_telegram`）（返信先を Telegram に切り替え）
- `/dock-discord`（alias: `/dock_discord`）（返信先を Discord に切り替え）
- `/dock-slack`（alias: `/dock_slack`）（返信先を Slack に切り替え）
- `/activation mention|always`（グループのみ）
- `/send on|off|inherit`（owner-only）
- `/reset` または `/new [model]`（オプションの model hint。残りはそのまま渡される）
- `/think <off|minimal|low|medium|high|xhigh>`（model/provider に応じた動的 choice。alias: `/thinking`、`/t`）
- `/fast status|on|off`（引数を省略すると現在有効な fast-mode 状態を表示）
- `/verbose on|full|off`（alias: `/v`）
- `/reasoning on|off|stream`（alias: `/reason`。on の場合、`Reasoning:` で始まる別メッセージを送信。`stream` = Telegram draft only）
- `/elevated on|off|ask|full`（alias: `/elev`。`full` は exec approval をスキップ）
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>`（現在値を表示するには `/exec` を送信）
- `/model <name>`（alias: `/models`。または `agents.defaults.models.*.alias` 由来の `/<alias>`）
- `/queue <mode>`（`debounce:2s cap:25 drop:summarize` などのオプション付き。現在設定を表示するには `/queue` を送信）
- `/bash <command>`（ホスト専用。`! <command>` の alias。`commands.bash: true` + `tools.elevated` allowlist が必要）
- `/dreaming [on|off|status|help]`（グローバル dreaming の切り替えまたは status 表示。[Dreaming](/concepts/dreaming) を参照）

Text-only:

- `/compact [instructions]`（[/concepts/compaction](/ja-JP/concepts/compaction) を参照）
- `! <command>`（ホスト専用。一度に 1 つ。長時間ジョブには `!poll` + `!stop` を使用）
- `!poll`（出力 / status を確認。オプションで `sessionId` を指定可。`/bash poll` でも動作）
- `!stop`（実行中の bash job を停止。オプションで `sessionId` を指定可。`/bash stop` でも動作）

注記:

- コマンドは、コマンドと引数の間にオプションで `:` を受け付けます（例: `/think: high`、`/send: on`、`/help:`）。
- `/new <model>` は model alias、`provider/model`、または provider 名（fuzzy match）を受け付けます。一致しない場合、そのテキストは message body として扱われます。
- 完全な provider usage breakdown には `openclaw status --usage` を使用してください。
- `/allowlist add|remove` には `commands.config=true` が必要で、チャネルの `configWrites` を尊重します。
- 複数アカウントチャネルでは、config を対象にした `/allowlist --account <id>` と `/config set channels.<provider>.accounts.<id>...` も、対象アカウントの `configWrites` を尊重します。
- `/usage` は応答ごとの usage footer を制御します。`/usage cost` は OpenClaw session log からローカル cost summary を表示します。
- `/restart` はデフォルトで有効です。無効にするには `commands.restart: false` を設定してください。
- Discord 専用のネイティブ command: `/vc join|leave|status` は voice channel を制御します（`channels.discord.voice` と native commands が必要。text としては利用不可）。
- Discord の thread-binding command（`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age`）は、thread binding が有効である必要があります（`session.threadBindings.enabled` および/または `channels.discord.threadBindings.enabled`）。
- ACP command のリファレンスと runtime の動作: [ACP Agents](/ja-JP/tools/acp-agents)。
- `/verbose` はデバッグや追加可視化向けです。通常使用では **off** のままにしてください。
- `/fast on|off` は session override を永続化します。これをクリアして config のデフォルトに戻すには、Sessions UI の `inherit` オプションを使用してください。
- `/fast` は provider 固有です: OpenAI/OpenAI Codex ではネイティブ Responses endpoint 上で `service_tier=priority` にマップされます。一方、`api.anthropic.com` へ送信される OAuth 認証トラフィックを含む direct public Anthropic request では、`service_tier=auto` または `standard_only` にマップされます。[OpenAI](/ja-JP/providers/openai) と [Anthropic](/ja-JP/providers/anthropic) を参照してください。
- Tool failure summary は必要に応じて引き続き表示されますが、詳細な failure text は `/verbose` が `on` または `full` のときにのみ含まれます。
- `/reasoning`（および `/verbose`）はグループ設定では危険です: 意図せず公開したくない内部 reasoning や tool output を露出する可能性があります。特に group chat では off のままにすることを推奨します。
- `/model` は新しい session model を即座に永続化します。
- agent が idle の場合、次回の run ですぐに使われます。
- すでに run が active の場合、OpenClaw は live switch を pending として記録し、クリーンな retry point でのみ新しい model へ再起動します。
- tool activity または reply output がすでに始まっている場合、その pending switch は後の retry opportunity または次の user turn までキューされたままになることがあります。
- **Fast path:** allowlist 済み送信者からの command-only message は即時処理されます（queue + model をバイパス）。
- **Group mention gating:** allowlist 済み送信者からの command-only message は mention requirement をバイパスします。
- **Inline shortcut（allowlist 済み送信者のみ）:** 一部の command は通常メッセージ内に埋め込まれていても動作し、残りのテキストがモデルに渡る前に取り除かれます。
  - 例: `hey /status` は status reply をトリガーし、残りのテキストは通常フローに進みます。
- 現在対象: `/help`、`/commands`、`/status`、`/whoami`（`/id`）。
- 認可されていない command-only message は黙って無視され、inline `/...` token は通常テキストとして扱われます。
- **Skill command:** `user-invocable` な skill は slash command として公開されます。名前は `a-z0-9_` に sanitize され（最大 32 文字）、衝突時は数値 suffix が付与されます（例: `_2`）。
  - `/skill <name> [input]` は名前で skill を実行します（ネイティブ command 制限により skill ごとの command が使えない場合に便利）。
  - デフォルトでは、skill command は通常の request としてモデルへ転送されます。
  - Skill はオプションで `command-dispatch: tool` を宣言でき、その場合 command は tool へ直接ルーティングされます（決定的で、モデルなし）。
  - 例: `/prose`（OpenProse plugin）— [OpenProse](/ja-JP/prose) を参照。
- **Native command 引数:** Discord は動的オプションに autocomplete を使用します（必要な引数を省略した場合は button menu も使用）。Telegram と Slack は、command が choice をサポートし、引数を省略した場合に button menu を表示します。

## `/tools`

`/tools` は config に関する質問ではなく、ランタイムの質問に答えます: **この会話で、この agent が今使えるものは何か**。

- デフォルトの `/tools` は compact で、素早く確認できるよう最適化されています。
- `/tools verbose` は短い説明を追加します。
- 引数をサポートする native-command サーフェスでは、同じ mode 切り替えとして `compact|verbose` が公開されます。
- 結果は session スコープなので、agent、channel、thread、sender authorization、または model を変えると出力も変わることがあります。
- `/tools` には、実際に runtime で到達可能な tool が含まれます。core tool、接続済み plugin tool、channel 所有 tool を含みます。

profile や override の編集には、`/tools` を静的 catalog とみなすのではなく、Control UI の Tools panel または config/catalog サーフェスを使用してください。

## Usage サーフェス（どこに何が表示されるか）

- **Provider usage/quota**（例: 「Claude 80% left」）は、usage tracking が有効な場合、現在の model provider に対して `/status` に表示されます。OpenClaw は provider の window を `% left` に正規化します。MiniMax では remaining-only percent field を表示前に反転し、`model_remains` response では model-tagged plan label とともに chat-model entry を優先します。
- `/status` 内の **token/cache 行** は、live session snapshot が疎な場合、最新 transcript usage entry にフォールバックできます。既存の非ゼロ live 値は引き続き優先され、transcript fallback は、保存済み total が欠落しているか小さい場合に、active runtime model label と、より大きい prompt 指向 total の回復にも使えます。
- **応答ごとの token/cost** は `/usage off|tokens|full` によって制御されます（通常の reply に追記されます）。
- `/model status` は **models/auth/endpoints** に関するものであり、usage ではありません。

## Model 選択（`/model`）

`/model` は directive として実装されています。

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

- `/model` と `/model list` は compact で番号付きの picker（model family + 利用可能 provider）を表示します。
- Discord では、`/model` と `/models` は provider と model の dropdown に Submit ステップを加えた対話型 picker を開きます。
- `/model <#>` はその picker から選択します（可能な場合は current provider を優先）。
- `/model status` は詳細ビューを表示し、利用可能な場合は設定済み provider endpoint（`baseUrl`）と API mode（`api`）も含みます。

## Debug override

`/debug` では **runtime-only** の config override（メモリ上、ディスクではない）を設定できます。owner-only。デフォルトでは無効で、`commands.debug: true` で有効化します。

例:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

注記:

- Override は新しい config read に即時適用されますが、`openclaw.json` には書き込みません。
- すべての override を消去し、ディスク上の config に戻すには `/debug reset` を使用してください。

## Config 更新

`/config` はディスク上の config（`openclaw.json`）に書き込みます。owner-only。デフォルトでは無効で、`commands.config: true` で有効化します。

例:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

注記:

- Config は書き込み前に検証され、不正な変更は拒否されます。
- `/config` の更新は restart 後も保持されます。

## MCP 更新

`/mcp` は `mcp.servers` 配下の OpenClaw 管理 MCP server 定義を書き込みます。owner-only。デフォルトでは無効で、`commands.mcp: true` で有効化します。

例:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

注記:

- `/mcp` は Pi 所有の project setting ではなく、OpenClaw config に保存されます。
- 実際にどの transport が実行可能かは runtime adapter が決定します。

## Plugin 更新

`/plugins` は operator が discovery 済み plugin を確認し、config 内で有効/無効を切り替えられるようにします。読み取り専用フローでは `/plugin` を alias として使用できます。デフォルトでは無効で、`commands.plugins: true` で有効化します。

例:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

注記:

- `/plugins list` と `/plugins show` は、現在の workspace とディスク上の config に対して実際の plugin discovery を使用します。
- `/plugins enable|disable` は plugin config のみを更新し、plugin の install や uninstall は行いません。
- enable/disable 変更後、それらを適用するには gateway を restart してください。

## サーフェスごとの注記

- **Text command** は通常のチャット session で実行されます（DM は `main` を共有し、group は独自の session を持ちます）。
- **Native command** は分離された session を使用します:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>`（prefix は `channels.slack.slashCommand.sessionPrefix` で設定可能）
  - Telegram: `telegram:slash:<userId>`（`CommandTargetSessionKey` によって chat session を対象にする）
- **`/stop`** は active な chat session を対象にし、現在の run を中止できます。
- **Slack:** `channels.slack.slashCommand` は、単一の `/openclaw` 形式 command 用として引き続きサポートされています。`commands.native` を有効にする場合は、組み込み command ごとに 1 つずつ Slack slash command を作成する必要があります（名前は `/help` などと同じ）。Slack の command argument menu は ephemeral Block Kit button として配信されます。
  - Slack のネイティブ例外: Slack は `/status` を予約しているため、`/status` ではなく `/agentstatus` を登録してください。text の `/status` は Slack message 内で引き続き動作します。

## BTW side question

`/btw` は、現在の session についての素早い **side question** です。

通常のチャットと異なり:

- 現在の session を背景 context として使用し、
- separate な **tool-less** one-shot call として実行され、
- 将来の session context を変更せず、
- transcript history には書き込まれず、
- 通常の assistant message ではなく live side result として配信されます。

これにより、`/btw` はメインタスクを進めたまま、一時的な確認をしたい場合に便利です。

例:

```text
/btw what are we doing right now?
```

完全な動作と client UX の詳細は [BTW Side Questions](/ja-JP/tools/btw) を参照してください。
