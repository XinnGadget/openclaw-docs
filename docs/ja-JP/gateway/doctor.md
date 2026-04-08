---
read_when:
    - doctor移行を追加または変更する場合
    - 破壊的な設定変更を導入する場合
summary: 'Doctorコマンド: ヘルスチェック、設定移行、修復手順'
title: Doctor
x-i18n:
    generated_at: "2026-04-08T02:15:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3761a222d9db7088f78215575fa84e5896794ad701aa716e8bf9039a4424dca6
    source_path: gateway/doctor.md
    workflow: 15
---

# Doctor

`openclaw doctor`は、OpenClawの修復 + 移行ツールです。古い
設定/状態を修復し、ヘルスチェックを行い、実行可能な修復手順を提供します。

## クイックスタート

```bash
openclaw doctor
```

### ヘッドレス / 自動化

```bash
openclaw doctor --yes
```

プロンプトを出さずにデフォルトを受け入れます（該当する場合、再起動/サービス/サンドボックス修復手順を含む）。

```bash
openclaw doctor --repair
```

推奨される修復をプロンプトなしで適用します（安全な範囲での修復 + 再起動）。

```bash
openclaw doctor --repair --force
```

積極的な修復も適用します（カスタムsupervisor設定を上書きします）。

```bash
openclaw doctor --non-interactive
```

プロンプトなしで実行し、安全な移行のみを適用します（設定の正規化 + ディスク上の状態の移動）。人による確認が必要な再起動/サービス/サンドボックス操作はスキップします。
検出されたレガシー状態の移行は自動的に実行されます。

```bash
openclaw doctor --deep
```

追加のGatewayインストールについてシステムサービスをスキャンします（launchd/systemd/schtasks）。

書き込む前に変更内容を確認したい場合は、最初に設定ファイルを開いてください:

```bash
cat ~/.openclaw/openclaw.json
```

## 実行内容（概要）

- gitインストール向けのオプションの事前更新（対話モードのみ）。
- UIプロトコルの新しさチェック（プロトコルスキーマが新しい場合はControl UIを再ビルド）。
- ヘルスチェック + 再起動プロンプト。
- Skillsステータス概要（対象/不足/ブロック）とプラグインステータス。
- レガシー値の設定正規化。
- レガシーフラット`talk.*`フィールドから`talk.provider` + `talk.providers.<provider>`へのTalk設定移行。
- レガシーChrome拡張設定とChrome MCPの準備状況に対するブラウザー移行チェック。
- OpenCodeプロバイダー上書き警告（`models.providers.opencode` / `models.providers.opencode-go`）。
- Codex OAuthのシャドーイング警告（`models.providers.openai-codex`）。
- OpenAI Codex OAuthプロファイル向けのOAuth TLS前提条件チェック。
- レガシーなディスク上の状態移行（sessions/agentディレクトリ/WhatsApp認証）。
- レガシープラグインマニフェスト契約キー移行（`speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`, `webSearchProviders` → `contracts`）。
- レガシーcronストア移行（`jobId`, `schedule.cron`, 最上位delivery/payloadフィールド, payload `provider`, 単純な`notify: true` webhookフォールバックジョブ）。
- セッションロックファイルの検査と古いロックのクリーンアップ。
- 状態の整合性と権限チェック（sessions, transcripts, stateディレクトリ）。
- ローカル実行時の設定ファイル権限チェック（chmod 600）。
- モデル認証の健全性: OAuthの有効期限を確認し、期限切れが近いトークンを更新でき、認証プロファイルのクールダウン/無効状態を報告します。
- 追加のワークスペースディレクトリ検出（`~/openclaw`）。
- サンドボックス有効時のサンドボックスイメージ修復。
- レガシーサービス移行と追加Gateway検出。
- Matrixチャンネルのレガシー状態移行（`--fix` / `--repair`モード）。
- Gatewayランタイムチェック（サービスはインストール済みだが未実行; キャッシュされたlaunchdラベル）。
- チャンネルステータス警告（実行中のGatewayからprobe）。
- Supervisor設定の監査（launchd/systemd/schtasks）とオプションの修復。
- Gatewayランタイムのベストプラクティスチェック（Node vs Bun、バージョンマネージャーパス）。
- Gatewayポート競合診断（デフォルト`18789`）。
- オープンなDMポリシーに対するセキュリティ警告。
- ローカルトークンモード向けのGateway認証チェック（トークンソースが存在しない場合はトークン生成を提案; トークンSecretRef設定は上書きしません）。
- Linuxでのsystemd lingerチェック。
- ワークスペースbootstrapファイルサイズチェック（コンテキストファイルの切り詰め/上限近接警告）。
- シェル補完ステータスチェックと自動インストール/アップグレード。
- メモリー検索embeddingプロバイダーの準備状況チェック（ローカルモデル、リモートAPIキー、またはQMDバイナリ）。
- ソースインストールチェック（pnpmワークスペース不一致、不足しているUIアセット、不足しているtsxバイナリ）。
- 更新された設定 + ウィザードメタデータを書き込みます。

## 詳細な動作と理由

### 0) オプションの更新（gitインストール）

gitチェックアウトでdoctorが対話モードで実行されている場合、
doctorを実行する前に更新（fetch/rebase/build）するかを提案します。

### 1) 設定の正規化

設定にレガシーな値の形状が含まれている場合（たとえば`messages.ackReaction`
にチャンネル固有の上書きがない場合）、doctorはそれらを現在の
スキーマに正規化します。

これにはレガシーなTalkのフラットフィールドも含まれます。現在の公開Talk設定は
`talk.provider` + `talk.providers.<provider>`です。doctorは古い
`talk.voiceId` / `talk.voiceAliases` / `talk.modelId` / `talk.outputFormat` /
`talk.apiKey`の形状をプロバイダーマップへ書き換えます。

### 2) レガシー設定キー移行

設定に非推奨キーが含まれている場合、他のコマンドは実行を拒否し、
`openclaw doctor`を実行するよう求めます。

Doctorは次を行います:

- 見つかったレガシーキーを説明します。
- 適用した移行内容を表示します。
- 更新されたスキーマで`~/.openclaw/openclaw.json`を書き換えます。

Gatewayも、レガシー設定形式を検出すると起動時に
doctor移行を自動実行するため、古い設定は手動介入なしで修復されます。
Cronジョブストアの移行は`openclaw doctor --fix`で処理されます。

現在の移行:

- `routing.allowFrom` → `channels.whatsapp.allowFrom`
- `routing.groupChat.requireMention` → `channels.whatsapp/telegram/imessage.groups."*".requireMention`
- `routing.groupChat.historyLimit` → `messages.groupChat.historyLimit`
- `routing.groupChat.mentionPatterns` → `messages.groupChat.mentionPatterns`
- `routing.queue` → `messages.queue`
- `routing.bindings` → 最上位の`bindings`
- `routing.agents`/`routing.defaultAgentId` → `agents.list` + `agents.list[].default`
- レガシーな`talk.voiceId`/`talk.voiceAliases`/`talk.modelId`/`talk.outputFormat`/`talk.apiKey` → `talk.provider` + `talk.providers.<provider>`
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
- 名前付き`accounts`があるチャンネルで、単一アカウント用の最上位チャンネル値が残っている場合、それらのアカウントスコープ値をそのチャンネル用に選ばれた昇格済みアカウントへ移動します（ほとんどのチャンネルでは`accounts.default`; Matrixは既存の一致する名前付き/デフォルト対象を保持できます）
- `identity` → `agents.list[].identity`
- `agent.*` → `agents.defaults` + `tools.*` (tools/elevated/exec/sandbox/subagents)
- `agent.model`/`allowedModels`/`modelAliases`/`modelFallbacks`/`imageModelFallbacks`
  → `agents.defaults.models` + `agents.defaults.model.primary/fallbacks` + `agents.defaults.imageModel.primary/fallbacks`
- `browser.ssrfPolicy.allowPrivateNetwork` → `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `browser.profiles.*.driver: "extension"` → `"existing-session"`
- `browser.relayBindHost`を削除（レガシー拡張relay設定）

Doctorの警告には、マルチアカウントチャンネル向けのアカウントデフォルトに関するガイダンスも含まれます:

- `channels.<channel>.defaultAccount`または`accounts.default`なしで、2つ以上の`channels.<channel>.accounts`エントリが設定されている場合、doctorはフォールバックルーティングが予期しないアカウントを選ぶ可能性があると警告します。
- `channels.<channel>.defaultAccount`が未知のアカウントIDに設定されている場合、doctorは警告し、設定済みアカウントIDを一覧表示します。

### 2b) OpenCodeプロバイダー上書き

`models.providers.opencode`, `opencode-zen`, または`opencode-go`を
手動で追加している場合、それは`@mariozechner/pi-ai`の組み込みOpenCodeカタログを上書きします。
その結果、モデルが誤ったAPIへ強制されたり、コストがゼロになったりすることがあります。doctorはこの点を警告し、
上書きを削除して、モデルごとのAPIルーティング + コストを復元できるようにします。

### 2c) ブラウザー移行とChrome MCPの準備状況

ブラウザー設定がまだ削除済みChrome拡張パスを指している場合、doctorは
それを現在のホストローカルChrome MCP接続モデルに正規化します:

- `browser.profiles.*.driver: "extension"`は`"existing-session"`になります
- `browser.relayBindHost`は削除されます

doctorはまた、`defaultProfile:
"user"`または設定済みの`existing-session`プロファイルを使用している場合、
ホストローカルChrome MCPパスを監査します:

- デフォルトの
  自動接続プロファイル向けに、同じホストにGoogle Chromeがインストールされているかを確認します
- 検出されたChromeバージョンを確認し、Chrome 144未満の場合は警告します
- ブラウザーinspectページでリモートデバッグを有効にするよう促します（
  たとえば`chrome://inspect/#remote-debugging`, `brave://inspect/#remote-debugging`,
  または`edge://inspect/#remote-debugging`）

doctorはChrome側の設定をあなたの代わりに有効化することはできません。ホストローカルChrome MCPには引き続き以下が必要です:

- gateway/nodeホスト上の144+のChromium系ブラウザー
- ローカルで実行中のブラウザー
- そのブラウザーで有効化されたリモートデバッグ
- ブラウザーで最初の接続同意プロンプトを承認すること

ここでの準備状況は、ローカル接続の前提条件に限られます。existing-sessionは
現在のChrome MCPルート制限を維持します。`responsebody`、PDF
エクスポート、ダウンロードインターセプト、バッチ操作のような高度なルートは、引き続き管理対象
ブラウザーまたはraw CDPプロファイルが必要です。

このチェックはDocker、sandbox、remote-browser、その他の
ヘッドレスフローには**適用されません**。それらは引き続きraw CDPを使用します。

### 2d) OAuth TLS前提条件

OpenAI Codex OAuthプロファイルが設定されている場合、doctorはOpenAI
認可エンドポイントをprobeして、ローカルのNode/OpenSSL TLSスタックが
証明書チェーンを検証できることを確認します。probeが証明書エラーで失敗した場合（
たとえば`UNABLE_TO_GET_ISSUER_CERT_LOCALLY`、期限切れ証明書、または自己署名証明書）、
doctorはプラットフォーム固有の修正ガイダンスを表示します。Homebrew版Nodeを使用しているmacOSでは、
通常、修正は`brew postinstall ca-certificates`です。`--deep`では、
Gatewayが健全であってもprobeが実行されます。

### 2c) Codex OAuthプロバイダー上書き

以前にレガシーなOpenAIトランスポート設定を
`models.providers.openai-codex`の下に追加していた場合、それらは新しいリリースで自動的に使用される
組み込みCodex OAuthプロバイダーパスをシャドーイングする可能性があります。doctorは、Codex OAuthと並んで
それらの古いトランスポート設定を検出すると警告し、古いトランスポート上書きを削除または書き換えて、
組み込みのルーティング/フォールバック動作を
取り戻せるようにします。カスタムプロキシやヘッダーのみの上書きは引き続きサポートされ、この警告は発生しません。

### 3) レガシー状態移行（ディスクレイアウト）

Doctorは古いディスク上レイアウトを現在の構造へ移行できます:

- セッションストア + transcripts:
  - `~/.openclaw/sessions/`から`~/.openclaw/agents/<agentId>/sessions/`へ
- agentディレクトリ:
  - `~/.openclaw/agent/`から`~/.openclaw/agents/<agentId>/agent/`へ
- WhatsApp認証状態（Baileys）:
  - レガシーな`~/.openclaw/credentials/*.json`（`oauth.json`を除く）
  - から`~/.openclaw/credentials/whatsapp/<accountId>/...`へ（デフォルトのアカウントID: `default`）

これらの移行はベストエフォートかつ冪等です。doctorは、
バックアップとして残したレガシーフォルダーがある場合に警告を出します。Gateway/CLIも、起動時に
レガシーsessions + agentディレクトリを自動移行するため、履歴/認証/モデルは
手動でdoctorを実行しなくてもエージェント単位のパスに配置されます。WhatsApp認証は意図的に
`openclaw doctor`経由でのみ移行されます。Talk provider/provider-mapの正規化は現在
構造的等価性で比較されるため、キー順のみの差分では
無操作の`doctor --fix`変更が繰り返し発生しなくなりました。

### 3a) レガシープラグインマニフェスト移行

Doctorは、非推奨の最上位ケイパビリティ
キー（`speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders`,
`webSearchProviders`）がないか、インストール済みプラグインマニフェストをすべてスキャンします。見つかった場合、
それらを`contracts`オブジェクトへ移動し、マニフェストファイルをその場で書き換えることを提案します。この移行は冪等です。
`contracts`キーにすでに同じ値がある場合は、データを重複させずに
レガシーキーのみを削除します。

### 3b) レガシーcronストア移行

Doctorはまた、cronジョブストア（デフォルトでは`~/.openclaw/cron/jobs.json`、
または上書き時は`cron.store`）に対して、スケジューラーが互換性のために
まだ受け入れている古いジョブ形式がないか確認します。

現在のcronクリーンアップには次が含まれます:

- `jobId` → `id`
- `schedule.cron` → `schedule.expr`
- 最上位payloadフィールド（`message`, `model`, `thinking`, ...）→ `payload`
- 最上位deliveryフィールド（`deliver`, `channel`, `to`, `provider`, ...）→ `delivery`
- payload `provider` deliveryエイリアス → 明示的な`delivery.channel`
- 単純なレガシー`notify: true` webhookフォールバックジョブ → 明示的な`delivery.mode="webhook"`と`delivery.to=cron.webhook`

Doctorは、動作を変えずに実行できる場合にのみ`notify: true`ジョブを
自動移行します。ジョブがレガシーnotifyフォールバックと既存の
非webhook配信モードを組み合わせている場合、doctorは警告を出し、そのジョブは手動確認用に残します。

### 3c) セッションロックのクリーンアップ

Doctorは、古い書き込みロックファイルを探して、各エージェントセッションディレクトリをスキャンします —
セッションが異常終了した際に残されたファイルです。見つかった各ロックファイルについて、次を報告します:
パス、PID、そのPIDがまだ生きているか、ロックの経過時間、および
古いと見なされるかどうか（PIDが死んでいる、または30分より古い）。`--fix` / `--repair`
モードでは古いロックファイルを自動的に削除します。それ以外ではメモを表示し、
`--fix`で再実行するよう案内します。

### 4) 状態整合性チェック（セッション永続化、ルーティング、安全性）

stateディレクトリは運用上の中枢です。これが消えると、
セッション、資格情報、ログ、設定を失います（他にバックアップがない限り）。

Doctorは以下を確認します:

- **Stateディレクトリがない**: 壊滅的な状態損失について警告し、ディレクトリ再作成を促し、
  失われたデータは復旧できないことを思い出させます。
- **Stateディレクトリ権限**: 書き込み可能か検証します。権限修復を提案し、
  所有者/グループ不一致が検出された場合は`chown`のヒントを出します。
- **macOSのクラウド同期stateディレクトリ**: stateがiCloud Drive
  （`~/Library/Mobile Documents/com~apple~CloudDocs/...`）または
  `~/Library/CloudStorage/...`配下に解決される場合に警告します。同期ベースのパスはI/O低下
  やロック/同期競合の原因になるためです。
- **LinuxのSDまたはeMMC stateディレクトリ**: stateが`mmcblk*`
  マウントソースに解決される場合に警告します。SDまたはeMMCベースのランダムI/Oは
  セッションや資格情報の書き込みで遅く、摩耗も早くなるためです。
- **セッションディレクトリがない**: `sessions/`とセッションストアディレクトリは
  履歴を永続化し、`ENOENT`クラッシュを避けるために必要です。
- **transcript不一致**: 最近のセッションエントリに欠落した
  transcriptファイルがある場合に警告します。
- **メインセッションの「1行JSONL」**: メインtranscriptが1行しかない場合に検出します（履歴が蓄積していません）。
- **複数のstateディレクトリ**: 複数の`~/.openclaw`フォルダーがホーム
  ディレクトリ間に存在する場合、または`OPENCLAW_STATE_DIR`が別の場所を指す場合に警告します（履歴がインストール間で分割される可能性があります）。
- **リモートモードのリマインダー**: `gateway.mode=remote`の場合、doctorは
  リモートホストで実行するよう促します（stateはそこにあります）。
- **設定ファイル権限**: `~/.openclaw/openclaw.json`が
  グループ/全員に読み取り可能な場合に警告し、`600`へ厳格化することを提案します。

### 5) モデル認証の健全性（OAuth有効期限）

Doctorは認証ストア内のOAuthプロファイルを検査し、トークンの
期限切れが近い/期限切れである場合に警告し、安全な場合は更新できます。Anthropic
OAuth/トークンプロファイルが古い場合は、Anthropic APIキーまたは
Anthropic setup-tokenパスを提案します。
更新プロンプトは対話モード（TTY）で実行している場合にのみ表示されます。`--non-interactive`
では更新試行をスキップします。

Doctorはまた、次の理由により一時的に使用できない認証プロファイルも報告します:

- 短いクールダウン（レート制限/タイムアウト/認証失敗）
- 長い無効化（課金/クレジット失敗）

### 6) Hooksモデル検証

`hooks.gmail.model`が設定されている場合、doctorはそのモデル参照を
カタログと許可リストに照らして検証し、解決できない場合や許可されていない場合に警告します。

### 7) サンドボックスイメージ修復

サンドボックスが有効な場合、doctorはDockerイメージを確認し、
現在のイメージが存在しない場合はビルドまたはレガシー名への切り替えを提案します。

### 7b) バンドル済みプラグインのランタイム依存関係

Doctorは、バンドル済みプラグインのランタイム依存関係（たとえば
Discordプラグインのランタイムパッケージ）がOpenClawインストールルートに存在することを確認します。
不足しているものがある場合、doctorはそのパッケージを報告し、
`openclaw doctor --fix` / `openclaw doctor --repair`モードでインストールします。

### 8) Gatewayサービス移行とクリーンアップヒント

DoctorはレガシーGatewayサービス（launchd/systemd/schtasks）を検出し、
それらを削除して、現在のGateway
ポートを使ってOpenClawサービスをインストールすることを提案します。また、追加のGateway類似サービスをスキャンし、クリーンアップのヒントを表示することもできます。
プロファイル名付きのOpenClaw Gatewayサービスは正式なものとして扱われ、「追加」とは見なされません。

### 8b) 起動時Matrix移行

Matrixチャンネルアカウントに保留中または対応可能なレガシー状態移行がある場合、
doctor（`--fix` / `--repair`モード）は移行前スナップショットを作成してから、
ベストエフォートの移行手順を実行します: レガシーMatrix状態移行とレガシー暗号化状態準備です。どちらの手順も致命的ではなく、エラーはログに記録され、起動は継続します。読み取り専用モード（`--fix`なしの`openclaw doctor`）では、このチェックは
完全にスキップされます。

### 9) セキュリティ警告

Doctorは、プロバイダーが許可リストなしでDMに開かれている場合や、
ポリシーが危険な方法で設定されている場合に警告を出します。

### 10) systemd linger（Linux）

systemdユーザーサービスとして実行している場合、doctorは
ログアウト後もgatewayが動作し続けるようlingerが有効であることを確認します。

### 11) ワークスペースステータス（Skills、プラグイン、レガシーディレクトリ）

Doctorはデフォルトエージェント向けのワークスペース状態の概要を表示します:

- **Skillsステータス**: 対象、要件不足、許可リストでブロックされたSkillsの数。
- **レガシーワークスペースディレクトリ**: `~/openclaw`やその他のレガシーワークスペースディレクトリが
  現在のワークスペースと並存する場合に警告します。
- **プラグインステータス**: 読み込み済み/無効/エラーのプラグイン数、エラーがある場合のプラグインID一覧、
  バンドルプラグインのケイパビリティを報告します。
- **プラグイン互換性警告**: 現在のランタイムとの互換性に問題があるプラグインを検出します。
- **プラグイン診断**: プラグインレジストリが
  読み込み時に出した警告やエラーを表示します。

### 11b) Bootstrapファイルサイズ

Doctorは、ワークスペースbootstrapファイル（たとえば`AGENTS.md`,
`CLAUDE.md`、またはその他の注入されるコンテキストファイル）が、設定された
文字数予算に近いか超えているかを確認します。ファイルごとの生文字数と注入後文字数、切り詰め率、
切り詰め原因（`max/file`または`max/total`）、および
総予算に対する注入総文字数の割合を報告します。ファイルが切り詰められているか上限に近い場合、
doctorは`agents.defaults.bootstrapMaxChars`
と`agents.defaults.bootstrapTotalMaxChars`の調整に関するヒントを表示します。

### 11c) シェル補完

Doctorは、現在のシェル
（zsh、bash、fish、またはPowerShell）にタブ補完がインストールされているか確認します:

- シェルプロファイルが遅い動的補完パターン
  （`source <(openclaw completion ...)`）を使用している場合、doctorはそれをより高速な
  キャッシュファイル方式へアップグレードします。
- プロファイルに補完が設定されているがキャッシュファイルが存在しない場合、
  doctorは自動的にキャッシュを再生成します。
- 補完がまったく設定されていない場合、doctorはインストールするか確認します
  （対話モードのみ; `--non-interactive`ではスキップされます）。

キャッシュを手動で再生成するには`openclaw completion --write-state`を実行してください。

### 12) Gateway認証チェック（ローカルトークン）

DoctorはローカルGatewayのトークン認証準備状況を確認します。

- トークンモードでトークンが必要だがトークンソースが存在しない場合、doctorは生成を提案します。
- `gateway.auth.token`がSecretRef管理だが利用できない場合、doctorは警告し、平文で上書きしません。
- `openclaw doctor --generate-gateway-token`は、トークンSecretRefが設定されていない場合にのみ生成を強制します。

### 12b) 読み取り専用のSecretRef対応修復

一部の修復フローでは、実行時fail-fast動作を弱めずに
設定済み資格情報を検査する必要があります。

- `openclaw doctor --fix`は現在、対象を絞った設定修復において、status系コマンドと同じ読み取り専用SecretRef要約モデルを使用します。
- 例: Telegramの`allowFrom` / `groupAllowFrom` `@username`修復は、利用可能な場合に設定済みボット資格情報の使用を試みます。
- TelegramボットトークンがSecretRef経由で設定されているが、現在のコマンド経路では利用できない場合、doctorはその資格情報が「設定済みだが利用不可」であることを報告し、自動解決をスキップします。クラッシュしたり、トークンが存在しないと誤報したりはしません。

### 13) Gatewayヘルスチェック + 再起動

Doctorはヘルスチェックを実行し、
不健全に見える場合はgatewayの再起動を提案します。

### 13b) メモリー検索の準備状況

Doctorは、デフォルトエージェント向けに設定されたメモリー検索embeddingプロバイダーが
準備できているか確認します。動作は、設定されたバックエンドとプロバイダーに依存します:

- **QMDバックエンド**: `qmd`バイナリが利用可能で起動可能かをprobeします。
  利用できない場合は、npmパッケージや手動バイナリパスオプションを含む修正ガイダンスを表示します。
- **明示的なローカルプロバイダー**: ローカルモデルファイルまたは認識可能な
  リモート/ダウンロード可能モデルURLがあるか確認します。ない場合は、リモートプロバイダーへの切り替えを提案します。
- **明示的なリモートプロバイダー**（`openai`, `voyage`など）: APIキーが
  環境または認証ストアに存在するか検証します。ない場合は実行可能な修正ヒントを表示します。
- **自動プロバイダー**: まずローカルモデルの可用性を確認し、その後、自動選択順に各リモート
  プロバイダーを試します。

Gatewayのprobe結果が利用可能な場合（チェック時点でGatewayが健全だった場合）、
doctorはその結果をCLIから見える設定と突き合わせ、
不一致があれば指摘します。

実行時のembedding準備状況を確認するには`openclaw memory status --deep`を使用してください。

### 14) チャンネルステータス警告

Gatewayが健全であれば、doctorはチャンネルステータスprobeを実行し、
修正案とともに警告を報告します。

### 15) Supervisor設定の監査 + 修復

Doctorはインストール済みsupervisor設定（launchd/systemd/schtasks）に対して、
デフォルトの欠落または古い項目（たとえばsystemdのnetwork-online依存関係や
再起動遅延）を確認します。不一致が見つかった場合は
更新を推奨し、現在のデフォルトに合わせてサービスファイル/タスクを
書き換えることができます。

補足:

- `openclaw doctor`はsupervisor設定を書き換える前に確認します。
- `openclaw doctor --yes`はデフォルトの修復プロンプトを受け入れます。
- `openclaw doctor --repair`は推奨修復をプロンプトなしで適用します。
- `openclaw doctor --repair --force`はカスタムsupervisor設定を上書きします。
- トークン認証でトークンが必要で、`gateway.auth.token`がSecretRef管理されている場合、doctorのサービスインストール/修復はSecretRefを検証しますが、解決済みの平文トークン値をsupervisorサービス環境メタデータへ永続化しません。
- トークン認証でトークンが必要で、設定されたトークンSecretRefが未解決の場合、doctorはインストール/修復経路をブロックし、実行可能なガイダンスを表示します。
- `gateway.auth.token`と`gateway.auth.password`の両方が設定されていて`gateway.auth.mode`が未設定の場合、doctorはmodeが明示的に設定されるまでインストール/修復をブロックします。
- Linux user-systemdユニットでは、doctorのトークンドリフトチェックにおいて、サービス認証メタデータ比較時に`Environment=`と`EnvironmentFile=`の両方のソースを含めるようになりました。
- `openclaw gateway install --force`でいつでも完全な書き換えを強制できます。

### 16) Gatewayランタイム + ポート診断

Doctorはサービスランタイム（PID、最後の終了ステータス）を検査し、
サービスがインストール済みなのに実際には実行されていない場合に警告します。また、Gatewayポート
（デフォルト`18789`）でポート競合を確認し、考えられる原因（Gatewayがすでに
実行中、SSHトンネル）を報告します。

### 17) Gatewayランタイムのベストプラクティス

Doctorは、GatewayサービスがBun上で実行されている場合や、バージョンマネージャー付きのNodeパス
（`nvm`, `fnm`, `volta`, `asdf`など）で動作している場合に警告します。WhatsApp + TelegramチャンネルにはNodeが必要であり、
バージョンマネージャーパスは、サービスがシェル初期化を
読み込まないため、アップグレード後に壊れる可能性があります。doctorは、利用可能な場合に
システムNodeインストール（Homebrew/apt/choco）への移行を提案します。

### 18) 設定書き込み + ウィザードメタデータ

Doctorは設定変更を永続化し、doctor実行を記録するために
ウィザードメタデータを記録します。

### 19) ワークスペースのヒント（バックアップ + メモリーシステム）

Doctorは、存在しない場合はワークスペースのメモリーシステムを提案し、
ワークスペースがまだgit管理下にない場合はバックアップのヒントを表示します。

ワークスペース構造とgitバックアップ（推奨: 非公開GitHubまたはGitLab）の完全なガイドは
[/concepts/agent-workspace](/ja-JP/concepts/agent-workspace)を参照してください。
