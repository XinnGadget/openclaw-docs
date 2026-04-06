---
read_when:
    - doctor の移行を追加または変更する場合
    - 互換性を破る設定変更を導入する場合
summary: 'Doctor コマンド: ヘルスチェック、設定移行、修復手順'
title: Doctor
x-i18n:
    generated_at: "2026-04-06T03:08:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6c0a15c522994552a1eef39206bed71fc5bf45746776372f24f31c101bfbd411
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` は OpenClaw の修復 + 移行ツールです。古い設定/状態を修正し、健全性を確認し、実行可能な修復手順を提供します。

## クイックスタート

```bash
openclaw doctor
```

### ヘッドレス / 自動化

```bash
openclaw doctor --yes
```

プロンプトなしでデフォルトを受け入れます（該当する場合、再起動/サービス/サンドボックス修復手順を含む）。

```bash
openclaw doctor --repair
```

推奨される修復をプロンプトなしで適用します（安全な範囲で修復 + 再起動）。

```bash
openclaw doctor --repair --force
```

積極的な修復も適用します（カスタム supervisor 設定を上書きします）。

```bash
openclaw doctor --non-interactive
```

プロンプトなしで実行し、安全な移行のみを適用します（設定の正規化 + ディスク上の状態移動）。人による確認が必要な再起動/サービス/サンドボックス操作はスキップします。
検出されたレガシー状態の移行は自動的に実行されます。

```bash
openclaw doctor --deep
```

追加の Gateway インストールがないかシステムサービスをスキャンします（launchd/systemd/schtasks）。

書き込む前に変更内容を確認したい場合は、最初に設定ファイルを開いてください:

```bash
cat ~/.openclaw/openclaw.json
```

## 実行内容（概要）

- git インストール向けの任意の事前更新（対話モードのみ）。
- UI プロトコルの新しさ確認（プロトコルスキーマの方が新しい場合は Control UI を再ビルド）。
- ヘルスチェック + 再起動プロンプト。
- Skills ステータスの要約（利用可能/不足/ブロック）と plugin ステータス。
- レガシー値の設定正規化。
- レガシーなフラット `talk.*` フィールドから `talk.provider` + `talk.providers.<provider>` への Talk 設定移行。
- レガシーな Chrome 拡張設定と Chrome MCP 準備状況に対するブラウザー移行チェック。
- OpenCode プロバイダー上書き警告（`models.providers.opencode` / `models.providers.opencode-go`）。
- OpenAI Codex OAuth プロファイル向けの OAuth TLS 前提条件チェック。
- レガシーなディスク上状態の移行（sessions/agent dir/WhatsApp auth）。
- レガシーな plugin manifest 契約キー移行（`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`）。
- レガシーな cron ストア移行（`jobId`, `schedule.cron`, トップレベルの delivery/payload フィールド、payload の `provider`, 単純な `notify: true` webhook フォールバックジョブ）。
- セッションロックファイルの検査と古いロックのクリーンアップ。
- 状態の整合性と権限チェック（sessions, transcripts, state dir）。
- ローカル実行時の設定ファイル権限チェック（chmod 600）。
- モデル認証の健全性: OAuth 有効期限を確認し、期限切れが近いトークンを更新でき、auth-profile のクールダウン/無効状態を報告します。
- 追加ワークスペースディレクトリの検出（`~/openclaw`）。
- サンドボックス有効時のサンドボックスイメージ修復。
- レガシーサービス移行と追加 Gateway 検出。
- Matrix チャンネルのレガシー状態移行（`--fix` / `--repair` モード）。
- Gateway 実行時チェック（サービスはインストール済みだが未実行、キャッシュされた launchd ラベル）。
- チャンネルステータス警告（実行中 Gateway からプローブ）。
- supervisor 設定監査（launchd/systemd/schtasks）と任意の修復。
- Gateway 実行時のベストプラクティスチェック（Node vs Bun、バージョンマネージャーパス）。
- Gateway ポート競合診断（デフォルト `18789`）。
- 開放的な DM ポリシーに対するセキュリティ警告。
- ローカルトークンモード向け Gateway 認証チェック（トークンソースがない場合はトークン生成を提案し、token SecretRef 設定は上書きしません）。
- Linux での systemd linger チェック。
- ワークスペース bootstrap ファイルのサイズチェック（コンテキストファイルの切り詰め/制限接近警告）。
- シェル補完のステータス確認と自動インストール/アップグレード。
- メモリ検索埋め込みプロバイダーの準備状況チェック（ローカルモデル、リモート API キー、または QMD バイナリ）。
- ソースインストールチェック（pnpm workspace の不一致、欠落した UI アセット、欠落した tsx バイナリ）。
- 更新済み設定 + wizard メタデータを書き込み。

## 詳細な動作と理由

### 0) 任意の更新（git インストール）

git チェックアウトで doctor が対話モードで実行されている場合、doctor 実行前に更新（fetch/rebase/build）するかを提案します。

### 1) 設定の正規化

設定にレガシーな値の形が含まれている場合（たとえばチャンネル固有の上書きがない `messages.ackReaction` など）、doctor はそれらを現在のスキーマに正規化します。

これにはレガシーな Talk フラットフィールドも含まれます。現在の公開 Talk 設定は `talk.provider` + `talk.providers.<provider>` です。doctor は古い
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey` 形式をプロバイダーマップへ書き換えます。

### 2) レガシー設定キーの移行

設定に非推奨キーが含まれている場合、他のコマンドは実行を拒否し、`openclaw doctor` を実行するよう求めます。

Doctor は次を行います:

- 見つかったレガシーキーを説明します。
- 適用した移行を表示します。
- 更新済みスキーマで `~/.openclaw/openclaw.json` を書き換えます。

また Gateway は起動時にレガシーな設定形式を検出すると doctor の移行を自動実行するため、手動介入なしで古い設定が修復されます。
Cron ジョブストアの移行は `openclaw doctor --fix` で処理されます。

現在の移行:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → トップレベル `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- レガシーな `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>`（`openai`/`elevenlabs`/`microsoft`/`edge`）→ `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>`（`openai`/`elevenlabs`/`microsoft`/`edge`）→ `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>`（`openai`/`elevenlabs`/`microsoft`/`edge`）→ `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>`（`openai`/`elevenlabs`/`microsoft`/`edge`）→ `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- 名前付き `accounts` を持つチャンネルで、単一アカウント用トップレベルチャンネル値が残っている場合、そのチャンネルで選ばれた昇格先アカウントへそのアカウントスコープ値を移動します（ほとんどのチャンネルでは `accounts.default`。Matrix は既存の一致する named/default ターゲットを保持できます）
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*`（tools/elevated/exec/sandbox/subagents）
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` を削除（レガシーな拡張 relay 設定）

Doctor の警告には、マルチアカウントチャンネル向けの account-default ガイダンスも含まれます:

- 2 つ以上の `channels.<channel>.accounts` エントリが設定されているのに `channels.<channel>.defaultAccount` または `accounts.default` がない場合、doctor はフォールバックルーティングで予期しないアカウントが選ばれる可能性を警告します。
- `channels.<channel>.defaultAccount` が未知のアカウント ID に設定されている場合、doctor は警告し、設定済みアカウント ID を一覧表示します。

### 2b) OpenCode プロバイダー上書き

`models.providers.opencode`、`opencode-zen`、または `opencode-go` を手動で追加している場合、それは `@mariozechner/pi-ai` 由来の組み込み OpenCode カタログを上書きします。
その結果、モデルが誤った API に強制されたり、コストが 0 になったりすることがあります。doctor は、上書きを削除してモデルごとの API ルーティング + コストを復元できるよう警告します。

### 2c) ブラウザー移行と Chrome MCP の準備状況

ブラウザー設定がまだ削除済み Chrome 拡張パスを指している場合、doctor はそれを現在の host-local Chrome MCP attach モデルに正規化します:

- `browser.profiles.*.driver: "extension"` は `"existing-session"` になります
- `browser.relayBindHost` は削除されます

また doctor は、`defaultProfile:
"user"` または設定済み `existing-session` プロファイルを使っている場合、host-local Chrome MCP パスを監査します:

- デフォルト自動接続プロファイル向けに、同じホストに Google Chrome がインストールされているかを確認します
- 検出した Chrome バージョンを確認し、Chrome 144 未満の場合は警告します
- ブラウザーの inspect ページで remote debugging を有効にするよう通知します（例:
  `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  または `edge://inspect/#remote-debugging`）

doctor が Chrome 側の設定を有効にすることはできません。host-local Chrome MCP には引き続き次が必要です:

- Gateway/node ホスト上の Chromium ベースのブラウザー 144+
- ローカルで実行中のブラウザー
- そのブラウザーで有効化された remote debugging
- ブラウザーで最初の attach 同意プロンプトを承認すること

ここでの準備状況はローカル attach の前提条件だけを対象としています。existing-session は現在の Chrome MCP ルート制限を維持します。`responsebody`、PDF export、download interception、batch actions のような高度なルートには、引き続き managed browser または raw CDP profile が必要です。

このチェックは Docker、sandbox、remote-browser、その他の headless フローには **適用されません**。それらは引き続き raw CDP を使用します。

### 2d) OAuth TLS 前提条件

OpenAI Codex OAuth プロファイルが設定されている場合、doctor は OpenAI 認可エンドポイントをプローブし、ローカル Node/OpenSSL TLS スタックが証明書チェーンを検証できることを確認します。プローブが証明書エラー（たとえば `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`、期限切れ証明書、自己署名証明書）で失敗した場合、doctor はプラットフォーム別の修正ガイダンスを表示します。macOS で Homebrew Node を使っている場合、修正は通常 `brew postinstall ca-certificates` です。`--deep` を付けると、Gateway が健全な場合でもプローブを実行します。

### 3) レガシー状態の移行（ディスクレイアウト）

Doctor は、古いディスク上レイアウトを現在の構造へ移行できます:

- Sessions ストア + transcripts:
  - `~/.openclaw/sessions/` から `~/.openclaw/agents/<agentId>/sessions/` へ
- Agent dir:
  - `~/.openclaw/agent/` から `~/.openclaw/agents/<agentId>/agent/` へ
- WhatsApp auth state（Baileys）:
  - レガシーな `~/.openclaw/credentials/*.json`（`oauth.json` を除く）から
  - `~/.openclaw/credentials/whatsapp/<accountId>/...` へ（デフォルトアカウント id: `default`）

これらの移行はベストエフォートかつ冪等です。バックアップとして残したレガシーフォルダーがある場合、doctor は警告を出します。Gateway/CLI も起動時にレガシーな sessions + agent dir を自動移行するため、履歴/auth/models は手動の doctor 実行なしでエージェント別パスに収まります。WhatsApp auth は意図的に `openclaw doctor` 経由でのみ移行されます。Talk provider/provider-map の正規化は現在、構造的同値性で比較するため、キー順だけの差分では no-op な `doctor --fix` 変更が繰り返し発生しなくなりました。

### 3a) レガシー plugin manifest の移行

Doctor は、インストール済みのすべての plugin manifest をスキャンして、非推奨のトップレベル capability キー（`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`）を検出します。見つかった場合、それらを `contracts`
オブジェクトへ移動し、manifest ファイルをその場で書き換えることを提案します。この移行は冪等です。`contracts` キーにすでに同じ値がある場合、データを重複させずにレガシーキーが削除されます。

### 3b) レガシー cron ストアの移行

Doctor は、cron ジョブストア（デフォルトでは `~/.openclaw/cron/jobs.json`、または上書き時は `cron.store`）についても、スケジューラーが互換性のためにまだ受け付けている古いジョブ形式を確認します。

現在の cron クリーンアップには次が含まれます:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- トップレベル payload フィールド（`message`, `model`, `thinking`, ...）→ `payload`
- トップレベル delivery フィールド（`deliver`, `channel`, `to`, `provider`, ...）→ `delivery`
- payload `provider` delivery エイリアス → 明示的な `delivery.channel`
- 単純なレガシー `notify: true` webhook フォールバックジョブ → 明示的な `delivery.mode="webhook"` と `delivery.to=cron.webhook`

Doctor は、動作を変えずに移行できる場合にのみ `notify: true` ジョブを自動移行します。ジョブがレガシー notify フォールバックと既存の非 webhook 配信モードを組み合わせている場合、doctor は警告を出し、そのジョブは手動確認用に残します。

### 3c) セッションロックのクリーンアップ

Doctor はすべてのエージェントセッションディレクトリをスキャンし、古い write-lock ファイル、つまりセッションが異常終了した際に残されたファイルを探します。見つかった各ロックファイルについて、次を報告します:
パス、PID、その PID がまだ生存しているか、ロックの経過時間、古いと見なされるかどうか（PID が死んでいる、または 30 分超）。`--fix` / `--repair`
モードでは古いロックファイルを自動削除します。それ以外では注記を表示し、`--fix` 付きで再実行するよう案内します。

### 4) 状態の整合性チェック（セッション永続化、ルーティング、安全性）

state ディレクトリは運用上の中枢です。これが消えると、sessions、credentials、logs、config（別にバックアップがない限り）を失います。

Doctor は次を確認します:

- **state dir が存在しない**: 壊滅的な状態損失について警告し、ディレクトリの再作成を促し、失われたデータは復元できないことを通知します。
- **state dir の権限**: 書き込み可能かを確認し、権限修復を提案します（所有者/グループ不一致が検出された場合は `chown` ヒントも出します）。
- **macOS のクラウド同期 state dir**: state が iCloud Drive
  （`~/Library/Mobile Documents/com~apple~CloudDocs/...`）または
  `~/Library/CloudStorage/...` 配下に解決される場合に警告します。同期ベースのパスは I/O 遅延やロック/同期競合の原因になり得るためです。
- **Linux の SD または eMMC state dir**: state が `mmcblk*`
  マウントソースに解決される場合に警告します。SD または eMMC ベースのランダム I/O は、session や credential 書き込みで遅くなりやすく、摩耗も早いためです。
- **Session dir が存在しない**: `sessions/` と session store ディレクトリは、履歴を永続化し `ENOENT` クラッシュを避けるために必要です。
- **Transcript 不一致**: 最近のセッションエントリに transcript ファイル欠落がある場合に警告します。
- **メインセッション「1 行 JSONL」**: メイン transcript が 1 行しかない場合を検出します（履歴が蓄積されていません）。
- **複数の state dir**: 複数の `~/.openclaw` フォルダーがホームディレクトリ間に存在する場合、または `OPENCLAW_STATE_DIR` が別の場所を指している場合に警告します（履歴がインストール間で分散する可能性があります）。
- **remote モードのリマインダー**: `gateway.mode=remote` の場合、doctor はリモートホストで実行するよう通知します（state はそこにあります）。
- **設定ファイル権限**: `~/.openclaw/openclaw.json` が group/world readable の場合に警告し、`600` への引き締めを提案します。

### 5) モデル認証の健全性（OAuth 有効期限）

Doctor は auth ストア内の OAuth プロファイルを検査し、トークンの期限切れが近い/すでに期限切れの場合に警告し、安全な場合は更新できます。Anthropic
OAuth/token プロファイルが古い場合は、Anthropic API キーまたはレガシーな
Anthropic setup-token パスを提案します。
更新プロンプトは対話モード（TTY）で実行中にのみ表示され、`--non-interactive`
では更新試行をスキップします。

Doctor は、削除済み Anthropic Claude CLI 状態が古く残っていることも検出します。古い
`anthropic:claude-cli` credential バイト列がまだ `auth-profiles.json`
内に存在する場合、doctor はそれらを Anthropic token/OAuth プロファイルへ戻し、
古い `claude-cli/...` モデル参照を書き換えます。
バイト列が失われている場合、doctor は古い設定を削除し、復旧コマンドを表示します。

Doctor はさらに、一時的に利用不可になっている auth プロファイルも報告します。原因には次が含まれます:

- 短いクールダウン（レート制限/タイムアウト/認証失敗）
- 長めの無効化（請求/クレジット失敗）

### 6) Hooks モデル検証

`hooks.gmail.model` が設定されている場合、doctor はそのモデル参照をカタログと allowlist に照らして検証し、解決できない、または許可されていない場合に警告します。

### 7) サンドボックスイメージ修復

サンドボックスが有効な場合、doctor は Docker イメージを確認し、現在のイメージが欠落しているときはビルドまたはレガシー名への切り替えを提案します。

### 7b) バンドル plugin のランタイム依存関係

Doctor は、バンドル plugin のランタイム依存関係（たとえば
Discord plugin ランタイムパッケージ）が OpenClaw インストールルートに存在することを確認します。
不足しているものがある場合、doctor はそのパッケージを報告し、
`openclaw doctor --fix` / `openclaw doctor --repair` モードでインストールします。

### 8) Gateway サービス移行とクリーンアップのヒント

Doctor はレガシーな Gateway サービス（launchd/systemd/schtasks）を検出し、
それらを削除して現在の Gateway ポートを使う OpenClaw サービスをインストールすることを提案します。また、追加の Gateway 類似サービスをスキャンしてクリーンアップのヒントを表示することもできます。
プロファイル名付き OpenClaw Gateway サービスは第一級として扱われ、「追加」としては扱われません。

### 8b) 起動時 Matrix 移行

Matrix チャンネルアカウントに保留中または実行可能なレガシー状態移行がある場合、
doctor（`--fix` / `--repair` モード）は移行前スナップショットを作成してから、ベストエフォートな移行手順を実行します: レガシー Matrix 状態移行と、レガシー暗号化状態の準備です。どちらの手順も致命的ではなく、エラーはログ記録され、起動は続行されます。読み取り専用モード（`--fix` なしの `openclaw doctor`）ではこのチェックは完全にスキップされます。

### 9) セキュリティ警告

Doctor は、プロバイダーが allowlist なしで DM に開放されている場合、またはポリシーが危険な形で設定されている場合に警告を出します。

### 10) systemd linger（Linux）

systemd ユーザーサービスとして実行している場合、doctor はログアウト後も Gateway が生き続けるよう lingering が有効になっていることを確認します。

### 11) ワークスペース状態（Skills、plugins、レガシーディレクトリ）

Doctor はデフォルトエージェントのワークスペース状態の要約を表示します:

- **Skills ステータス**: 利用可能、要件不足、allowlist によるブロック済み Skills の数。
- **レガシーワークスペースディレクトリ**: `~/openclaw` やその他のレガシーワークスペースディレクトリが現在のワークスペースと並存している場合に警告します。
- **Plugin ステータス**: 読み込み済み/無効/エラーの plugin 数、エラーがある plugin ID の一覧、バンドル plugin capabilities の報告。
- **Plugin 互換性警告**: 現在の実行時と互換性問題がある plugins を検出します。
- **Plugin 診断**: plugin registry が出した読み込み時警告やエラーを表示します。

### 11b) Bootstrap ファイルサイズ

Doctor は、ワークスペース bootstrap ファイル（たとえば `AGENTS.md`,
`CLAUDE.md`、またはその他の注入コンテキストファイル）が設定済み文字数予算に近いか、超えていないかを確認します。ファイルごとの生文字数と注入後文字数、切り詰め率、切り詰め原因（`max/file` または `max/total`）、および総予算に対する注入文字数合計を報告します。ファイルが切り詰められている、または制限に近い場合、doctor は `agents.defaults.bootstrapMaxChars`
および `agents.defaults.bootstrapTotalMaxChars` の調整ヒントを表示します。

### 11c) シェル補完

Doctor は、現在のシェル
（zsh、bash、fish、または PowerShell）でタブ補完がインストールされているか確認します:

- シェルプロファイルが低速な動的補完パターン
  （`source <(openclaw completion ...)`）を使っている場合、doctor はそれを高速なキャッシュファイル方式にアップグレードします。
- 補完がプロファイルで設定されているのにキャッシュファイルが欠けている場合、doctor はキャッシュを自動再生成します。
- 補完がまったく設定されていない場合、doctor はインストールを提案します
  （対話モードのみ。`--non-interactive` ではスキップ）。

キャッシュを手動で再生成するには `openclaw completion --write-state` を実行してください。

### 12) Gateway 認証チェック（ローカルトークン）

Doctor はローカル Gateway トークン認証の準備状況を確認します。

- トークンモードでトークンが必要なのにトークンソースがない場合、doctor は生成を提案します。
- `gateway.auth.token` が SecretRef 管理だが利用不可の場合、doctor は警告し、平文で上書きしません。
- `openclaw doctor --generate-gateway-token` は token SecretRef が設定されていない場合にのみ強制生成します。

### 12b) 読み取り専用 SecretRef 対応修復

一部の修復フローでは、実行時 fail-fast の挙動を弱めずに設定済み認証情報を検査する必要があります。

- `openclaw doctor --fix` は現在、状態系コマンドと同じ読み取り専用 SecretRef サマリーモデルを使って、対象を絞った設定修復を行います。
- 例: Telegram `allowFrom` / `groupAllowFrom` の `@username` 修復では、利用可能であれば設定済み bot 認証情報の使用を試みます。
- Telegram bot token が SecretRef 経由で設定されているものの現在のコマンドパスでは利用できない場合、doctor はその認証情報が「configured-but-unavailable」であることを報告し、トークンを欠落と誤報したりクラッシュしたりせずに自動解決をスキップします。

### 13) Gateway ヘルスチェック + 再起動

Doctor はヘルスチェックを実行し、Gateway が不健全に見える場合は再起動を提案します。

### 13b) メモリ検索の準備状況

Doctor は、デフォルトエージェント向けに設定されたメモリ検索埋め込みプロバイダーの準備状況を確認します。動作は設定されたバックエンドとプロバイダーによって異なります:

- **QMD バックエンド**: `qmd` バイナリが利用可能で起動可能かをプローブします。
  利用不可の場合、npm パッケージや手動バイナリパス指定を含む修正ガイダンスを表示します。
- **明示的なローカルプロバイダー**: ローカルモデルファイル、または認識可能な
  リモート/ダウンロード可能モデル URL があるか確認します。欠落している場合はリモートプロバイダーへの切り替えを提案します。
- **明示的なリモートプロバイダー**（`openai`, `voyage` など）: 環境変数または auth ストアに API キーがあることを確認します。欠けている場合は実行可能な修正ヒントを表示します。
- **auto プロバイダー**: まずローカルモデルの可用性を確認し、その後 auto-selection 順で各リモートプロバイダーを試します。

Gateway プローブ結果が利用可能な場合（チェック時点で Gateway が健全だった場合）、doctor はその結果を CLI から見える設定と突き合わせ、差異があれば通知します。

実行時の埋め込み準備状況を確認するには `openclaw memory status --deep` を使ってください。

### 14) チャンネルステータス警告

Gateway が健全な場合、doctor はチャンネルステータスプローブを実行し、推奨修正付きの警告を報告します。

### 15) Supervisor 設定監査 + 修復

Doctor は、インストール済みの supervisor 設定（launchd/systemd/schtasks）に
欠落または古いデフォルト
（たとえば systemd の network-online 依存関係や restart delay）がないか確認します。不一致を見つけた場合、更新を推奨し、現在のデフォルトにサービスファイル/タスクを書き換えることができます。

注意:

- `openclaw doctor` は supervisor 設定を書き換える前に確認します。
- `openclaw doctor --yes` はデフォルトの修復プロンプトを受け入れます。
- `openclaw doctor --repair` はプロンプトなしで推奨修復を適用します。
- `openclaw doctor --repair --force` はカスタム supervisor 設定を上書きします。
- token auth でトークンが必要かつ `gateway.auth.token` が SecretRef 管理の場合、doctor のサービスインストール/修復では SecretRef を検証しますが、解決済み平文トークン値を supervisor サービスの環境メタデータに永続化しません。
- token auth でトークンが必要なのに設定済みトークン SecretRef が未解決の場合、doctor はインストール/修復パスをブロックし、実行可能なガイダンスを表示します。
- `gateway.auth.token` と `gateway.auth.password` の両方が設定されていて `gateway.auth.mode` が未設定の場合、doctor は mode が明示設定されるまで install/repair をブロックします。
- Linux user-systemd unit では、doctor のトークンドリフトチェックは現在、サービス auth メタデータ比較時に `Environment=` と `EnvironmentFile=` の両方を含みます。
- `openclaw gateway install --force` でいつでも完全な書き換えを強制できます。

### 16) Gateway 実行時 + ポート診断

Doctor はサービス実行時
（PID、前回の終了ステータス）を検査し、サービスがインストール済みなのに実際には実行されていない場合に警告します。また Gateway ポート（デフォルト `18789`）の競合も確認し、考えられる原因
（Gateway がすでに実行中、SSH トンネル）を報告します。

### 17) Gateway 実行時のベストプラクティス

Doctor は、Gateway サービスが Bun またはバージョンマネージャー管理の Node パス
（`nvm`, `fnm`, `volta`, `asdf` など）で動作している場合に警告します。WhatsApp + Telegram チャンネルには Node が必要であり、バージョンマネージャーパスはサービスがシェル初期化を読み込まないため、アップグレード後に壊れることがあります。doctor は、利用可能であればシステム Node インストール（Homebrew/apt/choco）への移行を提案します。

### 18) 設定書き込み + wizard メタデータ

Doctor は設定変更を永続化し、doctor 実行を記録するために wizard メタデータを付与します。

### 19) ワークスペースのヒント（バックアップ + メモリシステム）

Doctor は、ワークスペースメモリシステムがない場合にそれを提案し、ワークスペースがまだ git 配下にない場合はバックアップのヒントを表示します。

ワークスペース構造と git バックアップ（推奨: プライベート GitHub または GitLab）の完全ガイドは [/concepts/agent-workspace](/ja-JP/concepts/agent-workspace) を参照してください。
