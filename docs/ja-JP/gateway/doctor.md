---
read_when:
    - doctor移行を追加または変更する場合
    - 破壊的な設定変更を導入する場合
summary: 'Doctorコマンド: ヘルスチェック、設定移行、修復手順'
title: Doctor
x-i18n:
    generated_at: "2026-04-07T04:43:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: a834dc7aec79c20d17bc23d37fb5f5e99e628d964d55bd8cf24525a7ee57130c
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor` は、OpenClawの修復 + 移行ツールです。古い設定/状態を修正し、健全性を確認し、実行可能な修復手順を提供します。

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

積極的な修復も適用します（カスタムのsupervisor設定を上書きします）。

```bash
openclaw doctor --non-interactive
```

プロンプトなしで実行し、安全な移行のみを適用します（設定の正規化 + ディスク上の状態移動）。人の確認が必要な再起動/サービス/サンドボックス操作はスキップします。
レガシー状態の移行は、検出されると自動的に実行されます。

```bash
openclaw doctor --deep
```

追加のGatewayインストールをシステムサービスからスキャンします（launchd/systemd/schtasks）。

書き込む前に変更を確認したい場合は、最初に設定ファイルを開いてください:

```bash
cat ~/.openclaw/openclaw.json
```

## 何をするか（概要）

- gitインストール向けの任意の事前更新（対話モードのみ）。
- UIプロトコルの新しさチェック（プロトコルスキーマが新しい場合はControl UIを再ビルド）。
- ヘルスチェック + 再起動プロンプト。
- Skillsステータス概要（対象/不足/ブロック済み）とプラグインステータス。
- レガシー値に対する設定の正規化。
- レガシーなフラット `talk.*` フィールドから `talk.provider` + `talk.providers.<provider>` へのTalk設定移行。
- レガシーChrome拡張設定およびChrome MCP準備状況のブラウザ移行チェック。
- OpenCodeプロバイダー上書き警告（`models.providers.opencode` / `models.providers.opencode-go`）。
- OpenAI Codex OAuthプロファイル向けのOAuth TLS前提条件チェック。
- レガシーなディスク上の状態移行（sessions/agent dir/WhatsApp auth）。
- レガシーなプラグインmanifest契約キー移行（`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`）。
- レガシーcronストア移行（`jobId`, `schedule.cron`, トップレベルのdelivery/payloadフィールド、payload `provider`, 単純な `notify: true` webhookフォールバックジョブ）。
- セッションlockファイルの検査と古いlockのクリーンアップ。
- 状態整合性および権限チェック（sessions、transcripts、state dir）。
- ローカル実行時の設定ファイル権限チェック（chmod 600）。
- モデル認証の健全性: OAuth有効期限を確認し、期限切れ間近のトークンを更新し、認証プロファイルのcooldown/無効化状態を報告します。
- 追加のworkspaceディレクトリ検出（`~/openclaw`）。
- サンドボックス有効時のsandbox image修復。
- レガシーサービス移行と追加Gateway検出。
- Matrixチャネルのレガシー状態移行（`--fix` / `--repair` モード）。
- Gatewayランタイムチェック（サービスがインストール済みだが実行されていない; キャッシュされたlaunchdラベル）。
- チャネルステータス警告（実行中のGatewayからプローブ）。
- Supervisor設定監査（launchd/systemd/schtasks）と任意の修復。
- Gatewayランタイムのベストプラクティスチェック（Node vs Bun、バージョンマネージャーパス）。
- Gatewayポート競合診断（デフォルト `18789`）。
- オープンなDMポリシーに対するセキュリティ警告。
- ローカルトークンモード向けのGateway authチェック（トークンソースが存在しない場合はトークン生成を提案; token SecretRef設定は上書きしません）。
- Linuxでのsystemd lingerチェック。
- Workspace bootstrapファイルサイズチェック（コンテキストファイルの切り捨て/上限近接警告）。
- Shell completionステータスチェックと自動インストール/アップグレード。
- メモリ検索embeddingプロバイダーの準備状況チェック（ローカルモデル、リモートAPIキー、またはQMDバイナリ）。
- ソースインストールチェック（pnpm workspace不一致、欠落したUIアセット、欠落したtsxバイナリ）。
- 更新された設定 + wizardメタデータを書き込みます。

## 詳細な動作と理由

### 0) 任意の更新（gitインストール）

これがgit checkoutで、doctorが対話モードで実行されている場合、doctorを実行する前に更新（fetch/rebase/build）するかどうかを提案します。

### 1) 設定の正規化

設定にレガシーな値の形状（たとえばチャネル固有の上書きがない `messages.ackReaction`）が含まれている場合、doctorはそれらを現在のスキーマに正規化します。

これにはレガシーなTalkフラットフィールドも含まれます。現在の公開Talk設定は `talk.provider` + `talk.providers.<provider>` です。doctorは古い `talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` / `talk.apiKey` の形状をプロバイダーマップに書き換えます。

### 2) レガシー設定キー移行

設定に非推奨キーが含まれている場合、ほかのコマンドは実行を拒否し、`openclaw doctor` を実行するよう求めます。

Doctorは次を行います:

- 見つかったレガシーキーを説明します。
- 適用した移行を表示します。
- 更新されたスキーマで `~/.openclaw/openclaw.json` を書き換えます。

Gatewayも、レガシー設定形式を検出すると起動時にdoctor移行を自動実行するため、古い設定は手動介入なしで修復されます。
Cronジョブストアの移行は `openclaw doctor --fix` で処理されます。

現在の移行:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → トップレベル `bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- レガシー `talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
- `routing.agentToAgent` → `tools.agentToAgent`
- `routing.transcribeAudio` → `tools.media.audio.models`
- `messages.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `messages.tts.providers.<provider>`
- `channels.discord.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.voice.tts.providers.<provider>`
- `channels.discord.accounts.<id>.voice.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `channels.discord.accounts.<id>.voice.tts.providers.<provider>`
- `plugins.entries.voice-call.config.tts.<provider>` (`openai`/`elevenlabs`/`microsoft`/`edge`) → `plugins.entries.voice-call.config.tts.providers.<provider>`
- `plugins.entries.voice-call.config.provider: "log"` → `"mock"`
- `plugins.entries.voice-call.config.twilio.from` → `plugins.entries.voice-call.config.fromNumber`
- `plugins.entries.voice-call.config.streaming.sttProvider` → `plugins.entries.voice-call.config.streaming.provider`
- `plugins.entries.voice-call.config.streaming.openaiApiKey|sttModel|silenceDurationMs|vadThreshold`
  → `plugins.entries.voice-call.config.streaming.providers.openai.*`
- `bindings[].match.accountID` → `bindings[].match.accountId`
- 名前付き `accounts` を持つチャネルで、単一アカウント用のトップレベルチャネル値が残っている場合、そのアカウントスコープ値を、そのチャネル用に選ばれた昇格先アカウントへ移動します（大半のチャネルでは `accounts.default`; Matrixは一致する既存の名前付き/デフォルトの対象を保持できます）
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*`（tools/elevated/exec/sandbox/subagents）
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost` を削除（レガシー拡張relay設定）

Doctorの警告には、マルチアカウントチャネル向けのアカウントデフォルトガイダンスも含まれます:

- `channels.<channel>.accounts` に2つ以上のエントリが設定されているのに `channels.<channel>.defaultAccount` または `accounts.default` がない場合、doctorはフォールバックルーティングによって想定外のアカウントが選ばれる可能性があると警告します。
- `channels.<channel>.defaultAccount` が未知のアカウントIDに設定されている場合、doctorは警告し、設定済みのアカウントIDを一覧表示します。

### 2b) OpenCodeプロバイダー上書き

`models.providers.opencode`, `opencode-zen`, または `opencode-go` を手動で追加している場合、それは `@mariozechner/pi-ai` の組み込みOpenCodeカタログを上書きします。
その結果、モデルが誤ったAPIに強制されたり、コストがゼロになったりする可能性があります。doctorは、その上書きを削除してモデルごとのAPIルーティング + コストを復元できるよう警告します。

### 2c) ブラウザ移行とChrome MCP準備状況

ブラウザ設定がまだ削除済みのChrome拡張パスを指している場合、doctorはそれを現在のホストローカルChrome MCPアタッチモデルに正規化します:

- `browser.profiles.*.driver: "extension"` は `"existing-session"` になります
- `browser.relayBindHost` は削除されます

Doctorは、`defaultProfile: "user"` または設定済みの `existing-session` プロファイルを使用している場合に、ホストローカルChrome MCPパスも監査します:

- デフォルトの自動接続プロファイル向けに、同じホストにGoogle Chromeがインストールされているかを確認します
- 検出されたChromeバージョンを確認し、Chrome 144未満の場合は警告します
- ブラウザのinspectページでリモートデバッグを有効化するよう注意を促します（例: `chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`, `edge://inspect/#remote-debugging`）

DoctorはChrome側の設定を代わりに有効化することはできません。ホストローカルChrome MCPには、引き続き次が必要です:

- Gateway/nodeホスト上のChromium系ブラウザ 144+
- ローカルで実行中のブラウザ
- そのブラウザで有効化されたリモートデバッグ
- ブラウザで最初のアタッチ同意プロンプトを承認すること

ここでの準備状況はローカルアタッチの前提条件のみを対象としています。Existing-sessionは現在のChrome MCPルート制限を維持します。`responsebody`、PDFエクスポート、ダウンロード傍受、バッチアクションなどの高度なルートには、引き続き管理対象ブラウザまたは生のCDPプロファイルが必要です。

このチェックは Docker、sandbox、remote-browser、その他のヘッドレスフローには**適用されません**。それらは引き続き生のCDPを使用します。

### 2d) OAuth TLS前提条件

OpenAI Codex OAuthプロファイルが設定されている場合、doctorはOpenAI認可エンドポイントをプローブして、ローカルのNode/OpenSSL TLSスタックが証明書チェーンを検証できることを確認します。プローブが証明書エラー（たとえば `UNABLE_TO_GET_ISSUER_CERT_LOCALLY`、期限切れ証明書、または自己署名証明書）で失敗した場合、doctorはプラットフォーム固有の修正ガイダンスを表示します。HomebrewのNodeを使うmacOSでは、通常の修正は `brew postinstall ca-certificates` です。`--deep` を指定すると、Gatewayが健全であってもこのプローブが実行されます。

### 3) レガシー状態移行（ディスクレイアウト）

Doctorは、古いディスク上のレイアウトを現在の構造に移行できます:

- Sessionsストア + transcripts:
  - `~/.openclaw/sessions/` から `~/.openclaw/agents/<agentId>/sessions/` へ
- Agent dir:
  - `~/.openclaw/agent/` から `~/.openclaw/agents/<agentId>/agent/` へ
- WhatsApp auth state（Baileys）:
  - レガシーな `~/.openclaw/credentials/*.json`（`oauth.json` を除く）から
  - `~/.openclaw/credentials/whatsapp/<accountId>/...` へ（デフォルトのアカウントID: `default`）

これらの移行はベストエフォートかつ冪等です。バックアップとしてレガシーフォルダーが残された場合、doctorは警告を出します。Gateway/CLIも、起動時にレガシーsessions + agent dirを自動移行するため、履歴/auth/models は手動でdoctorを実行しなくてもエージェント別パスに配置されます。WhatsApp authは意図的に `openclaw doctor` 経由でのみ移行されます。Talk provider/provider-mapの正規化は現在、構造的同値性で比較するため、キー順だけの差分では no-op な `doctor --fix` 変更が繰り返し発生しなくなりました。

### 3a) レガシープラグインmanifest移行

Doctorは、インストール済みのすべてのプラグインmanifestをスキャンし、非推奨のトップレベル機能キー（`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders`）を検出します。見つかった場合、それらを `contracts` オブジェクトへ移動し、manifestファイルをその場で書き換えることを提案します。この移行は冪等です。`contracts` キーにすでに同じ値がある場合、データを重複させることなくレガシーキーが削除されます。

### 3b) レガシーcronストア移行

Doctorはcronジョブストア（デフォルトでは `~/.openclaw/cron/jobs.json`、または上書きされている場合は `cron.store`）もチェックし、スケジューラーが互換性のためにまだ受け入れている古いジョブ形状を確認します。

現在のcronクリーンアップには次が含まれます:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- トップレベルのpayloadフィールド（`message`, `model`, `thinking`, ...）→ `payload`
- トップレベルのdeliveryフィールド（`deliver`, `channel`, `to`, `provider`, ...）→ `delivery`
- payload `provider` deliveryエイリアス → 明示的な `delivery.channel`
- 単純なレガシー `notify: true` webhookフォールバックジョブ → 明示的な `delivery.mode="webhook"` と `delivery.to=cron.webhook`

Doctorは、動作を変更せずに実行できる場合にのみ `notify: true` ジョブを自動移行します。ジョブがレガシーnotifyフォールバックと既存の非webhook配信モードを組み合わせている場合、doctorは警告を出し、そのジョブは手動確認用に残します。

### 3c) セッションlockクリーンアップ

Doctorは、異常終了したセッションが残した書き込みlockファイル、つまり各エージェントのセッションディレクトリに残されたファイルをスキャンします。見つかった各lockファイルについて、次を報告します:
パス、PID、そのPIDがまだ生きているか、lockの経過時間、古いと見なされるかどうか（PIDが死んでいる、または30分より古い）。`--fix` / `--repair` モードでは、古いlockファイルを自動的に削除します。それ以外では、メモを表示し、`--fix` を付けて再実行するよう案内します。

### 4) 状態整合性チェック（セッション永続化、ルーティング、安全性）

状態ディレクトリは運用上の中枢です。これが消えると、sessions、credentials、logs、config を失います（別の場所にバックアップがない限り）。

Doctorは次を確認します:

- **状態ディレクトリがない**: 壊滅的な状態損失について警告し、ディレクトリの再作成を提案し、不足データは復旧できないことを注意喚起します。
- **状態ディレクトリ権限**: 書き込み可能か確認します。権限修復を提案し、所有者/グループ不一致が検出された場合は `chown` のヒントを出します。
- **macOSのクラウド同期状態ディレクトリ**: 状態が iCloud Drive（`~/Library/Mobile Documents/com~apple~CloudDocs/...`）または `~/Library/CloudStorage/...` の下に解決される場合に警告します。同期ベースのパスはI/O低下やlock/同期競合を引き起こす可能性があるためです。
- **LinuxのSDまたはeMMC状態ディレクトリ**: 状態が `mmcblk*` マウントソースに解決される場合に警告します。SDまたはeMMCベースのランダムI/Oは、セッションや認証情報の書き込み時に遅くなり、摩耗も速くなる可能性があるためです。
- **Sessionディレクトリがない**: `sessions/` とセッションストアディレクトリは、履歴の永続化と `ENOENT` クラッシュ回避に必要です。
- **Transcript不一致**: 最近のセッションエントリに欠落したtranscriptファイルがある場合に警告します。
- **メインセッションの「1行JSONL」**: メインtranscriptが1行しかない場合を検出します（履歴が蓄積されていない）。
- **複数の状態ディレクトリ**: 複数の `~/.openclaw` フォルダーがホームディレクトリ間に存在する場合、または `OPENCLAW_STATE_DIR` が別の場所を指している場合に警告します（履歴がインストール間で分散する可能性があります）。
- **リモートモードの注意**: `gateway.mode=remote` の場合、doctorはリモートホストで実行するよう注意します（状態はそこにあります）。
- **設定ファイル権限**: `~/.openclaw/openclaw.json` がグループ/全員に読み取り可能な場合に警告し、`600` へ厳格化することを提案します。

### 5) モデル認証の健全性（OAuth有効期限）

Doctorはauthストア内のOAuthプロファイルを検査し、トークンが期限切れ間近/期限切れの場合に警告し、安全な場合は更新できます。Anthropic OAuth/tokenプロファイルが古い場合は、Anthropic APIキーまたはAnthropic setup-tokenパスを提案します。
更新プロンプトは対話モード（TTY）で実行している場合にのみ表示されます。`--non-interactive` は更新試行をスキップします。

Doctorはまた、次の理由で一時的に使用不能なauthプロファイルも報告します:

- 短時間のcooldown（レート制限/タイムアウト/auth失敗）
- 長めの無効化（請求/クレジット失敗）

### 6) Hooksモデル検証

`hooks.gmail.model` が設定されている場合、doctorはそのモデル参照をカタログおよびallowlistに照らして検証し、解決できない場合や許可されていない場合に警告します。

### 7) Sandbox image修復

サンドボックスが有効な場合、doctorはDockerイメージをチェックし、現在のイメージがない場合はビルドまたはレガシー名への切り替えを提案します。

### 7b) バンドル済みプラグインのランタイム依存関係

Doctorは、バンドル済みプラグインのランタイム依存関係（たとえばDiscordプラグインのランタイムパッケージ）がOpenClawインストールルートに存在することを確認します。
不足しているものがあれば、doctorはそのパッケージを報告し、`openclaw doctor --fix` / `openclaw doctor --repair` モードでインストールします。

### 8) Gatewayサービス移行とクリーンアップのヒント

DoctorはレガシーGatewayサービス（launchd/systemd/schtasks）を検出し、それらを削除して現在のGatewayポートを使うOpenClawサービスをインストールすることを提案します。また、追加のGateway風サービスをスキャンし、クリーンアップのヒントを表示することもできます。
プロファイル名付きのOpenClaw Gatewayサービスは第一級のものとして扱われ、「追加」とは見なされません。

### 8b) 起動時のMatrix移行

Matrixチャネルアカウントに保留中または対処可能なレガシー状態移行がある場合、doctor（`--fix` / `--repair` モード）は移行前スナップショットを作成し、その後ベストエフォートの移行手順を実行します: レガシーMatrix状態移行とレガシー暗号化状態準備。どちらの手順も致命的ではなく、エラーはログに記録され、起動は継続します。読み取り専用モード（`--fix` なしの `openclaw doctor`）では、このチェックは完全にスキップされます。

### 9) セキュリティ警告

Doctorは、プロバイダーがallowlistなしでDMに開かれている場合や、ポリシーが危険な方法で設定されている場合に警告を出します。

### 10) systemd linger（Linux）

systemdユーザーサービスとして実行している場合、doctorはログアウト後もGatewayが動作し続けるよう lingering が有効であることを確認します。

### 11) Workspaceステータス（Skills、プラグイン、レガシーディレクトリ）

Doctorは、デフォルトエージェントのworkspace状態の概要を表示します:

- **Skillsステータス**: 対象、必要条件不足、allowlistブロック済みのSkills数をカウントします。
- **レガシーworkspaceディレクトリ**: `~/openclaw` または他のレガシーworkspaceディレクトリが現在のworkspaceと並存している場合に警告します。
- **プラグインステータス**: 読み込み済み/無効/エラーのプラグイン数をカウントします。エラーがあるプラグインIDを列挙し、bundle plugin capabilities を報告します。
- **プラグイン互換性警告**: 現在のランタイムとの互換性問題があるプラグインを検出します。
- **プラグイン診断**: プラグインレジストリが出力した読み込み時警告やエラーを表示します。

### 11b) Bootstrapファイルサイズ

Doctorは、workspace bootstrapファイル（たとえば `AGENTS.md`、`CLAUDE.md`、または他の注入されるコンテキストファイル）が、設定された文字数予算に近いか超えているかを確認します。ファイルごとの生文字数と注入後文字数、切り捨て率、切り捨て理由（`max/file` または `max/total`）、および総予算に対する総注入文字数の割合を報告します。ファイルが切り捨てられているか上限に近い場合、doctorは `agents.defaults.bootstrapMaxChars` と `agents.defaults.bootstrapTotalMaxChars` を調整するためのヒントを表示します。

### 11c) Shell completion

Doctorは、現在のシェル（zsh、bash、fish、またはPowerShell）に対してタブ補完がインストールされているかを確認します:

- シェルプロファイルが遅い動的補完パターン（`source <(openclaw completion ...)`）を使用している場合、doctorはそれをより高速なキャッシュファイル方式にアップグレードします。
- 補完がプロファイル内で設定されているのにキャッシュファイルが存在しない場合、doctorはキャッシュを自動再生成します。
- 補完がまったく設定されていない場合、doctorはインストールを提案します（対話モードのみ; `--non-interactive` ではスキップ）。

キャッシュを手動で再生成するには `openclaw completion --write-state` を実行してください。

### 12) Gateway authチェック（ローカルトークン）

DoctorはローカルGatewayトークンauthの準備状況を確認します。

- トークンモードでトークンが必要なのにトークンソースが存在しない場合、doctorはトークン生成を提案します。
- `gateway.auth.token` がSecretRef管理だが利用不可の場合、doctorは警告し、平文で上書きしません。
- `openclaw doctor --generate-gateway-token` は、token SecretRef が設定されていない場合にのみ生成を強制します。

### 12b) 読み取り専用のSecretRef対応修復

一部の修復フローでは、ランタイムのfail-fast動作を弱めずに設定済み認証情報を検査する必要があります。

- `openclaw doctor --fix` は現在、対象設定修復のために status系コマンドと同じ読み取り専用SecretRef概要モデルを使用します。
- 例: Telegramの `allowFrom` / `groupAllowFrom` の `@username` 修復は、利用可能な場合に設定済みボット認証情報の使用を試みます。
- TelegramボットトークンがSecretRef経由で設定されているが現在のコマンドパスでは利用できない場合、doctorはその認証情報が「設定済みだが利用不可」であることを報告し、クラッシュしたりトークンを欠落と誤報したりせずに自動解決をスキップします。

### 13) Gatewayヘルスチェック + 再起動

Doctorはヘルスチェックを実行し、不健全に見える場合はGatewayの再起動を提案します。

### 13b) メモリ検索の準備状況

Doctorは、デフォルトエージェント向けに設定されたメモリ検索embeddingプロバイダーの準備状況を確認します。動作は、設定されたバックエンドとプロバイダーに応じて異なります:

- **QMDバックエンド**: `qmd` バイナリが利用可能で起動可能かをプローブします。
  そうでない場合は、npmパッケージと手動バイナリパス指定オプションを含む修正ガイダンスを表示します。
- **明示的なローカルプロバイダー**: ローカルモデルファイルまたは認識可能なリモート/ダウンロード可能モデルURLを確認します。存在しない場合は、リモートプロバイダーへの切り替えを提案します。
- **明示的なリモートプロバイダー**（`openai`, `voyage` など）: 環境またはauthストアにAPIキーが存在することを確認します。存在しない場合は、実行可能な修正ヒントを表示します。
- **自動プロバイダー**: まずローカルモデルの利用可能性を確認し、その後、自動選択順に各リモートプロバイダーを試します。

Gatewayプローブ結果が利用可能な場合（チェック時点でGatewayが健全だった場合）、doctorはその結果をCLIから見える設定と照合し、不一致があれば通知します。

実行時にembedding準備状況を確認するには `openclaw memory status --deep` を使用してください。

### 14) チャネルステータス警告

Gatewayが健全な場合、doctorはチャネルステータスプローブを実行し、修正案付きで警告を報告します。

### 15) Supervisor設定監査 + 修復

Doctorは、インストール済みのsupervisor設定（launchd/systemd/schtasks）に不足または古いデフォルト（たとえばsystemdのnetwork-online依存関係や再起動遅延）がないか確認します。不一致が見つかった場合は更新を推奨し、サービスファイル/タスクを現在のデフォルトに書き換えることができます。

注記:

- `openclaw doctor` はsupervisor設定を書き換える前に確認します。
- `openclaw doctor --yes` はデフォルトの修復プロンプトを受け入れます。
- `openclaw doctor --repair` はプロンプトなしで推奨修復を適用します。
- `openclaw doctor --repair --force` はカスタムのsupervisor設定を上書きします。
- token auth にトークンが必要で、`gateway.auth.token` がSecretRef管理されている場合、doctorのサービスインストール/修復はSecretRefを検証しますが、解決済みの平文トークン値をsupervisorサービス環境メタデータへ永続化しません。
- token auth にトークンが必要で、設定されたtoken SecretRef が未解決の場合、doctorは実行可能なガイダンス付きでインストール/修復パスをブロックします。
- `gateway.auth.token` と `gateway.auth.password` の両方が設定され、`gateway.auth.mode` が未設定の場合、doctorはモードが明示的に設定されるまでインストール/修復をブロックします。
- Linux user-systemdユニットでは、doctorのトークンドリフトチェックに、サービスauthメタデータ比較時の `Environment=` と `EnvironmentFile=` の両方のソースが含まれるようになりました。
- 完全な再書き換えはいつでも `openclaw gateway install --force` で強制できます。

### 16) Gatewayランタイム + ポート診断

Doctorはサービスランタイム（PID、前回終了ステータス）を検査し、サービスがインストール済みだが実際には実行されていない場合に警告します。また、Gatewayポート（デフォルト `18789`）のポート競合も確認し、考えられる原因（Gatewayがすでに実行中、SSHトンネル）を報告します。

### 17) Gatewayランタイムのベストプラクティス

Doctorは、GatewayサービスがBunまたはバージョンマネージャー管理のNodeパス（`nvm`, `fnm`, `volta`, `asdf` など）で実行されている場合に警告します。WhatsApp + TelegramチャネルにはNodeが必要であり、バージョンマネージャーのパスは、サービスがシェル初期化を読み込まないため、アップグレード後に壊れる可能性があります。利用可能な場合、doctorはシステムNodeインストール（Homebrew/apt/choco）への移行を提案します。

### 18) 設定書き込み + wizardメタデータ

Doctorは設定変更を永続化し、doctor実行を記録するためにwizardメタデータを付与します。

### 19) Workspaceのヒント（バックアップ + メモリシステム）

Doctorは、不足している場合はworkspaceメモリシステムを提案し、workspaceがまだgit管理下にない場合はバックアップのヒントを表示します。

workspace構造とgitバックアップ（推奨: 非公開のGitHubまたはGitLab）の完全なガイドについては [/concepts/agent-workspace](/ja-JP/concepts/agent-workspace) を参照してください。
