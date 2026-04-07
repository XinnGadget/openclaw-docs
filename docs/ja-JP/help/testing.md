---
read_when:
    - ローカルまたはCIでテストを実行するとき
    - model/providerの不具合に対するリグレッションを追加するとき
    - Gateway + agentの動作をデバッグするとき
summary: 'テストキット: unit/e2e/liveスイート、Dockerランナー、および各テストの対象範囲'
title: テスト
x-i18n:
    generated_at: "2026-04-07T04:44:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61b1856fff7d09dcfdbaacf1b5c8fbc3284750e360fc37d5e15852011b6a5bb5
    source_path: help/testing.md
    workflow: 15
---

# テスト

OpenClawには3つのVitestスイート（unit/integration、e2e、live）と、少数のDockerランナーがあります。

このドキュメントは「どのようにテストするか」のガイドです:

- 各スイートが何を対象にし、意図的に何を対象外としているか
- よくあるワークフロー（ローカル、push前、デバッグ）で実行するコマンド
- liveテストが認証情報をどのように見つけ、models/providersをどのように選ぶか
- 実際のmodel/providerの問題に対するリグレッションをどう追加するか

## クイックスタート

たいていの日は次で十分です:

- フルゲート（push前に期待されるもの）: `pnpm build && pnpm check && pnpm test`
- 余裕のあるマシンでのより高速なローカル全スイート実行: `pnpm test:max`
- Vitestの直接watchループ: `pnpm test:watch`
- 直接のファイル指定はextension/channelパスにも対応: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- DockerベースのQAサイト: `pnpm qa:lab:up`

テストを触ったときや、さらに確信を持ちたいとき:

- カバレッジゲート: `pnpm test:coverage`
- E2Eスイート: `pnpm test:e2e`

実際のproviders/modelsをデバッグするとき（実際の認証情報が必要）:

- Liveスイート（models + gateway tool/image probes）: `pnpm test:live`
- 1つのliveファイルだけを静かに対象化: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

ヒント: 失敗している1ケースだけが必要な場合は、下で説明するallowlist環境変数でliveテストを絞ることを優先してください。

## テストスイート（どこで何が動くか）

スイートは「現実性が増す順」（そして不安定さ/コストも増す順）と考えてください:

### Unit / integration（デフォルト）

- コマンド: `pnpm test`
- 設定: 既存のスコープ付きVitest projectを対象にした10個の逐次shard実行（`vitest.full-*.config.ts`）
- ファイル: `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` のcore/unitインベントリと、`vitest.unit.config.ts` で対象になっている許可済みの `ui` nodeテスト
- 対象範囲:
  - 純粋なunitテスト
  - プロセス内integrationテスト（gateway auth、routing、tooling、parsing、config）
  - 既知のバグに対する決定的なリグレッション
- 前提:
  - CIで実行される
  - 実際のキーは不要
  - 高速で安定しているべき
- Projectsに関する注記:
  - 対象を絞らない `pnpm test` は、1つの巨大なネイティブルートprojectプロセスの代わりに、10個の小さなshard設定（`core-unit-src`、`core-unit-security`、`core-unit-ui`、`core-unit-support`、`core-contracts`、`core-bundled`、`core-runtime`、`agentic`、`auto-reply`、`extensions`）を実行するようになりました。これにより、負荷の高いマシンでのピークRSSを抑え、auto-reply/extension作業が無関係なスイートを圧迫するのを防ぎます。
  - `pnpm test --watch` は、multi-shard watchループが現実的でないため、引き続きネイティブルートの `vitest.config.ts` project graphを使います。
  - `pnpm test`、`pnpm test:watch`、`pnpm test:perf:imports` は、明示的なファイル/ディレクトリ対象をまずスコープ付きlane経由でルーティングするので、`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` はフルルートproject起動のコストを払わずに済みます。
  - `pnpm test:changed` は、差分がルーティング可能なsource/testファイルだけに触れている場合、変更されたgitパスを同じスコープ付きlaneに展開します。config/setup編集は引き続き広いルートproject再実行にフォールバックします。
  - 一部の `plugin-sdk` および `commands` テストも、`test/setup-openclaw-runtime.ts` をスキップする専用の軽量lane経由でルーティングされます。stateful/runtime-heavyなファイルは既存laneに残ります。
  - 一部の `plugin-sdk` および `commands` のhelper sourceファイルも、changed-mode実行をそれらの軽量laneにある明示的な隣接テストへマップするようになったため、helper編集ではそのディレクトリ全体の重いスイートを再実行せずに済みます。
  - `auto-reply` には、トップレベルのcore helper、トップレベルの `reply.*` integrationテスト、`src/auto-reply/reply/**` サブツリーの3つの専用bucketがあります。これにより、最も重いreply harness作業が、軽量なstatus/chunk/tokenテストに乗らないようにしています。
- Embedded runnerに関する注記:
  - message-tool discovery入力またはcompaction runtime contextを変更するときは、両方のレベルのカバレッジを維持してください。
  - 純粋なrouting/normalization境界には、焦点を絞ったhelperリグレッションを追加してください。
  - さらに、embedded runner integrationスイートも健全に保ってください:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、`src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`、`src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - これらのスイートは、スコープ付きidとcompaction動作が実際の `run.ts` / `compact.ts` パスを通って流れ続けることを検証します。helperのみのテストは、これらのintegrationパスの十分な代替にはなりません。
- Poolに関する注記:
  - ベースのVitest configは、現在デフォルトで `threads` です。
  - 共有Vitest configでは `isolate: false` も固定され、root projects、e2e、live config全体で非isolate runnerを使用します。
  - ルートUI laneは `jsdom` セットアップとoptimizerを維持していますが、現在は共有の非isolate runner上で実行されます。
  - 各 `pnpm test` shardは、共有Vitest configから同じ `threads` + `isolate: false` のデフォルトを継承します。
  - 共有の `scripts/run-vitest.mjs` launcherは、大規模なローカル実行中のV8コンパイル負荷を減らすため、Vitestの子Nodeプロセスにデフォルトで `--no-maglev` も追加します。標準のV8動作と比較したい場合は `OPENCLAW_VITEST_ENABLE_MAGLEV=1` を設定してください。
- 高速なローカル反復に関する注記:
  - `pnpm test:changed` は、変更パスがより小さなスイートにきれいにマップされる場合、スコープ付きlane経由でルーティングします。
  - `pnpm test:max` と `pnpm test:changed:max` も同じルーティング動作を維持しつつ、worker上限だけを高くします。
  - ローカルworkerの自動スケーリングは現在意図的に保守的で、ホストのload averageがすでに高い場合にも抑制されるため、複数のVitest実行が同時に走ってもデフォルトで被害が少なくなります。
  - ベースVitest configは、projects/configファイルを `forceRerunTriggers` としてマークするので、テスト配線が変わったときもchanged-modeの再実行が正確に保たれます。
  - configは、対応ホストでは `OPENCLAW_VITEST_FS_MODULE_CACHE` を有効にしたままにします。直接profiling用に明示的なキャッシュ場所がほしい場合は `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` を設定してください。
- Perf-debugに関する注記:
  - `pnpm test:perf:imports` はVitestのimport-durationレポートとimport-breakdown出力を有効にします。
  - `pnpm test:perf:imports:changed` は、同じprofilingビューを `origin/main` 以降で変更されたファイルに限定します。
- `pnpm test:perf:changed:bench -- --ref <git-ref>` は、そのコミット済み差分に対して、ルーティングされた `test:changed` とネイティブルートproject経路を比較し、wall timeとmacOS max RSSを出力します。
- `pnpm test:perf:changed:bench -- --worktree` は、変更ファイル一覧を `scripts/test-projects.mjs` とルートVitest config経由でルーティングして、現在のdirty treeをベンチマークします。
  - `pnpm test:perf:profile:main` は、Vitest/Viteの起動とtransformオーバーヘッドに対するmain-thread CPU profileを書き出します。
  - `pnpm test:perf:profile:runner` は、unitスイートでファイル並列を無効にしたrunner CPU+heap profilesを書き出します。

### E2E（gateway smoke）

- コマンド: `pnpm test:e2e`
- 設定: `vitest.e2e.config.ts`
- ファイル: `src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- ランタイムのデフォルト:
  - 他のrepo部分に合わせて、Vitest `threads` と `isolate: false` を使用します。
  - 適応的workerを使用します（CI: 最大2、ローカル: デフォルトで1）。
  - コンソールI/Oオーバーヘッドを減らすため、デフォルトでsilent modeで実行します。
- 便利な上書き:
  - worker数を強制するには `OPENCLAW_E2E_WORKERS=<n>`（上限16）
  - 詳細なコンソール出力を再有効化するには `OPENCLAW_E2E_VERBOSE=1`
- 対象範囲:
  - マルチインスタンスgatewayのエンドツーエンド動作
  - WebSocket/HTTP surface、node pairing、より重いネットワーキング
- 前提:
  - CIで実行される（パイプラインで有効な場合）
  - 実際のキーは不要
  - unitテストより可動部分が多い（遅くなることがある）

### E2E: OpenShell backend smoke

- コマンド: `pnpm test:e2e:openshell`
- ファイル: `test/openshell-sandbox.e2e.test.ts`
- 対象範囲:
  - Docker経由でホスト上に隔離されたOpenShell gatewayを起動
  - 一時的なローカルDockerfileからsandboxを作成
  - 実際の `sandbox ssh-config` + SSH exec 上でOpenClawのOpenShell backendを実行
  - sandbox fs bridgeを通じてremote-canonical filesystem動作を検証
- 前提:
  - オプトイン専用。デフォルトの `pnpm test:e2e` 実行には含まれない
  - ローカルの `openshell` CLIと動作するDocker daemonが必要
  - 隔離された `HOME` / `XDG_CONFIG_HOME` を使い、その後テスト用gatewayとsandboxを破棄する
- 便利な上書き:
  - 広いe2eスイートを手動で実行するときにこのテストを有効にするには `OPENCLAW_E2E_OPENSHELL=1`
  - デフォルト以外のCLI binaryまたはwrapper scriptを指すには `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live（実際のproviders + 実際のmodels）

- コマンド: `pnpm test:live`
- 設定: `vitest.live.config.ts`
- ファイル: `src/**/*.live.test.ts`
- デフォルト: `pnpm test:live` により**有効**（`OPENCLAW_LIVE_TEST=1` を設定）
- 対象範囲:
  - 「このprovider/modelは、今日、実際の認証情報で本当に動くか？」
  - providerの形式変更、tool-callingの癖、authの問題、rate limit動作の検出
- 前提:
  - 設計上CIで安定しない（実ネットワーク、実providerポリシー、quota、outage）
  - コストがかかる / rate limitを消費する
  - 「全部」よりも、絞ったサブセット実行を優先する
- Live実行は、欠けているAPI keyを拾うために `~/.profile` を読み込みます。
- デフォルトでは、live実行でも `HOME` を隔離し、config/auth materialを一時テストhomeにコピーするため、unit fixtureが実際の `~/.openclaw` を変更することはありません。
- liveテストで意図的に実際のhome directoryを使いたい場合にのみ、`OPENCLAW_LIVE_USE_REAL_HOME=1` を設定してください。
- `pnpm test:live` は現在、より静かなモードがデフォルトです。[live] ...` 進捗出力は維持されますが、追加の `~/.profile` 通知は抑制され、gateway bootstrap logs/Bonjour chatterもミュートされます。完全な起動ログを戻したい場合は `OPENCLAW_LIVE_TEST_QUIET=0` を設定してください。
- API key rotation（provider別）: カンマ/セミコロン形式の `*_API_KEYS`、または `*_API_KEY_1`、`*_API_KEY_2`（例: `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`）、またはlive専用上書きの `OPENCLAW_LIVE_*_KEY` を設定します。テストはrate limit応答時に再試行します。
- 進捗/heartbeat出力:
  - Liveスイートは現在、長いprovider呼び出し中でも動作中であることが見えるよう、stderrに進捗行を出力します。Vitestのconsole captureが静かでも有効です。
  - `vitest.live.config.ts` はVitestのconsole interceptionを無効にしているため、provider/gatewayの進捗行はlive実行中に即時ストリームされます。
  - direct-modelのheartbeatは `OPENCLAW_LIVE_HEARTBEAT_MS` で調整します。
  - gateway/probeのheartbeatは `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` で調整します。

## どのスイートを実行すべきか？

この判断表を使ってください:

- ロジック/テストを編集した: `pnpm test` を実行（大きく変更したなら `pnpm test:coverage` も）
- gateway networking / WS protocol / pairing に触れた: `pnpm test:e2e` も追加
- 「botが落ちている」/ provider固有の失敗 / tool calling をデバッグしたい: 絞った `pnpm test:live` を実行

## Live: Android node capability sweep

- テスト: `src/gateway/android-node.capabilities.live.test.ts`
- スクリプト: `pnpm android:test:integration`
- 目的: 接続済みAndroid nodeが現在公開している**すべてのコマンド**を呼び出し、command contract動作を検証すること。
- 対象範囲:
  - 前提条件付き / 手動セットアップ（このスイートはアプリのインストール/実行/pairingは行いません）。
  - 選択したAndroid nodeに対する、コマンドごとのgateway `node.invoke` 検証。
- 必要な事前セットアップ:
  - Androidアプリがすでにgatewayに接続済みでpairing済みであること。
  - アプリをforegroundのままにしておくこと。
  - 通ることを期待するcapabilityに対して、権限/キャプチャ同意が付与されていること。
- 任意のターゲット上書き:
  - `OPENCLAW_ANDROID_NODE_ID` または `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- Androidの完全なセットアップ詳細: [Android App](/platforms/android)

## Live: model smoke（profile keys）

liveテストは、失敗を切り分けられるよう2つの層に分かれています:

- 「Direct model」は、与えられたキーでprovider/modelがそもそも応答できるかを教えてくれます。
- 「Gateway smoke」は、そのmodelに対して完全なgateway+agentパイプラインが動くか（sessions、history、tools、sandbox policyなど）を教えてくれます。

### Layer 1: Direct model completion（gatewayなし）

- テスト: `src/agents/models.profiles.live.test.ts`
- 目的:
  - 発見されたmodelを列挙する
  - `getApiKeyForModel` を使って、認証情報があるmodelを選ぶ
  - modelごとに小さなcompletionを実行する（必要に応じて対象を絞ったリグレッションも）
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼ぶ場合は `OPENCLAW_LIVE_TEST=1`）
- 実際にこのスイートを実行するには `OPENCLAW_LIVE_MODELS=modern`（または `all`、modernの別名）を設定してください。そうしないと、`pnpm test:live` をgateway smokeに集中させるためskipされます
- modelの選び方:
  - modern allowlistを実行するには `OPENCLAW_LIVE_MODELS=modern`（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` はmodern allowlistの別名
  - または `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（カンマ区切りallowlist）
- providerの選び方:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（カンマ区切りallowlist）
- キーの取得元:
  - デフォルト: profile storeと環境変数フォールバック
  - **profile storeのみ**を強制するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` を設定
- これが存在する理由:
  - 「provider APIが壊れている / keyが無効」と「gateway agent pipelineが壊れている」を分離するため
  - 小さく隔離されたリグレッションを収容するため（例: OpenAI Responses/Codex Responsesのreasoning replay + tool-call flow）

### Layer 2: Gateway + dev agent smoke（「@openclaw」が実際に行うこと）

- テスト: `src/gateway/gateway-models.profiles.live.test.ts`
- 目的:
  - プロセス内gatewayを立ち上げる
  - `agent:dev:*` sessionを作成/patchする（実行ごとにmodel override）
  - keys付きmodelsを反復し、次を検証する:
    - 「意味のある」応答（toolsなし）
    - 実際のtool invocationが動く（read probe）
    - 任意の追加tool probe（exec+read probe）
    - OpenAIリグレッション経路（tool-call-only → follow-up）が動き続ける
- Probeの詳細（失敗をすばやく説明できるように）:
  - `read` probe: テストがworkspaceにnonceファイルを書き込み、agentにそれを `read` してnonceを返すよう求めます。
  - `exec+read` probe: テストがagentに、temp fileへnonceを書き込む `exec` を実行させ、その後それを `read` で読み返させます。
  - image probe: テストが生成したPNG（cat + ランダム化コード）を添付し、modelが `cat <CODE>` を返すことを期待します。
  - 実装参照: `src/gateway/gateway-models.profiles.live.test.ts` と `src/gateway/live-image-probe.ts`。
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼ぶ場合は `OPENCLAW_LIVE_TEST=1`）
- modelの選び方:
  - デフォルト: modern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` はmodern allowlistの別名
  - または `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（またはカンマ区切り）で絞り込み
- providerの選び方（「OpenRouter全部」を避ける）:
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（カンマ区切りallowlist）
- Tool + image probesはこのliveテストでは常に有効:
  - `read` probe + `exec+read` probe（tool stress）
  - image probeは、modelがimage input supportを公開している場合に実行されます
  - Flow（高レベル）:
    - テストが「CAT」+ ランダムコードの小さなPNGを生成します（`src/gateway/live-image-probe.ts`）
    - `agent` に `attachments: [{ mimeType: "image/png", content: "<base64>" }]` で送信します
    - Gatewayがattachmentを `images[]` に解析します（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - Embedded agentがmultimodal user messageをmodelへ転送します
    - 検証: replyに `cat` + そのコードが含まれること（OCR耐性: 小さな誤りは許容）

ヒント: 自分のマシンで何をテストできるか（および正確な `provider/model` id）を確認するには、次を実行してください:
__OC_I18N_900000__
## Live: CLI backend smoke（Codex CLIまたはその他のローカルCLI）

- テスト: `src/gateway/gateway-cli-backend.live.test.ts`
- 目的: デフォルトconfigに触れず、ローカルCLI backendを使ってGateway + agent pipelineを検証すること。
- 有効化:
  - `pnpm test:live`（またはVitestを直接呼ぶ場合は `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- デフォルト:
  - Model: `codex-cli/gpt-5.4`
  - Command: `codex`
  - Args: `["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]`
- 上書き（任意）:
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - 実際のimage attachmentを送信するには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`（パスはpromptに注入されます）。
  - prompt注入の代わりにimage file pathをCLI引数として渡すには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`。
  - `IMAGE_ARG` が設定されているときにimage引数の渡し方を制御するには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（または `"list"`）。
  - 2ターン目を送ってresume flowを検証するには `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`。
  
例:
__OC_I18N_900001__
Dockerレシピ:
__OC_I18N_900002__
注意:

- Dockerランナーは `scripts/test-live-cli-backend-docker.sh` にあります。
- repo Docker image内で、非rootの `node` ユーザーとしてlive CLI-backend smokeを実行します。
- `codex-cli` については、Linux版 `@openai/codex` packageを、キャッシュ可能で書き込み可能なprefix `OPENCLAW_DOCKER_CLI_TOOLS_DIR`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）にインストールします。

## Live: ACP bind smoke（`/acp spawn ... --bind here`）

- テスト: `src/gateway/gateway-acp-bind.live.test.ts`
- 目的: live ACP agentを使って実際のACP conversation-bind flowを検証すること:
  - `/acp spawn <agent> --bind here` を送る
  - syntheticなmessage-channel conversationをその場でbindする
  - 同じconversationで通常のfollow-upを送る
  - そのfollow-upがbindされたACP session transcriptに入ることを確認する
- 有効化:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- デフォルト:
  - ACP agent: `claude`
  - Synthetic channel: Slack DM風のconversation context
  - ACP backend: `acpx`
- 上書き:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 注意:
  - このlaneは、admin専用のsynthetic originating-route field付きのgateway `chat.send` surfaceを使うため、外部配信を装わずにmessage-channel contextを付加できます。
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` が未設定の場合、テストは選択されたACP harness agentに対して、組み込み `acpx` pluginの内蔵agent registryを使用します。

例:
__OC_I18N_900003__
Dockerレシピ:
__OC_I18N_900004__
Dockerに関する注意:

- Dockerランナーは `scripts/test-live-acp-bind-docker.sh` にあります。
- `~/.profile` を読み込み、対応するCLI auth materialをcontainerへ展開し、書き込み可能なnpm prefixへ `acpx` をインストールし、不足していれば要求されたlive CLI（`@anthropic-ai/claude-code` または `@openai/codex`）をインストールします。
- Docker内では、runnerは `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` を設定するので、読み込まれたprofile由来のprovider環境変数を、子harness CLIでも `acpx` が利用できます。

### 推奨liveレシピ

狭く明示的なallowlistが最速で、最も不安定になりにくいです:

- 単一model、direct（gatewayなし）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 単一model、gateway smoke:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 複数providerにまたがるtool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google重視（Gemini API key + Antigravity）:
  - Gemini（API key）: `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）: `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注意:

- `google/...` はGemini API（API key）を使用します。
- `google-antigravity/...` はAntigravity OAuth bridge（Cloud Code Assist風agent endpoint）を使用します。
- `google-gemini-cli/...` はあなたのマシン上のローカルGemini CLIを使用します（認証もtoolingの癖も別です）。
- Gemini APIとGemini CLIの違い:
  - API: OpenClawはGoogleのホスト型Gemini APIをHTTP経由で呼び出します（API key / profile auth）。多くのユーザーが「Gemini」と言うとき、通常はこちらです。
  - CLI: OpenClawはローカルの `gemini` binaryをshell実行します。独自のauthを持ち、挙動も異なる場合があります（streaming/tool support/version skew）。

## Live: model matrix（何をカバーするか）

固定の「CI model list」はありません（liveはオプトインです）が、キーを持つ開発マシンで定期的にカバーすることを**推奨**するmodelsは次のとおりです。

### Modern smoke set（tool calling + image）

これは、動作し続けることを期待する「一般的なmodel」実行です:

- OpenAI（非Codex）: `openai/gpt-5.4`（任意: `openai/gpt-5.4-mini`）
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）: `google/gemini-3.1-pro-preview` と `google/gemini-3-flash-preview`（古いGemini 2.x modelは避ける）
- Google（Antigravity）: `google-antigravity/claude-opus-4-6-thinking` と `google-antigravity/gemini-3-flash`
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

tools + imageつきgateway smokeを実行:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Baseline: tool calling（Read + 任意のExec）

provider familyごとに少なくとも1つ選んでください:

- OpenAI: `openai/gpt-5.4`（または `openai/gpt-5.4-mini`）
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google: `google/gemini-3-flash-preview`（または `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

任意の追加カバレッジ（あるとよいもの）:

- xAI: `xai/grok-4`（または利用可能な最新）
- Mistral: `mistral/`…（有効化済みの「tools」対応modelを1つ選ぶ）
- Cerebras: `cerebras/`…（アクセスがある場合）
- LM Studio: `lmstudio/`…（ローカル。tool callingはAPI modeに依存）

### Vision: image send（attachment → multimodal message）

image probeを通すため、`OPENCLAW_LIVE_GATEWAY_MODELS` には少なくとも1つ、image対応model（Claude/Gemini/OpenAIのvision対応variantなど）を含めてください。

### Aggregators / alternate gateways

キーが有効なら、次経由のテストもサポートしています:

- OpenRouter: `openrouter/...`（数百のmodel。tool+image対応候補を探すには `openclaw models scan` を使ってください）
- OpenCode: Zen用の `opencode/...` と、Go用の `opencode-go/...`（authは `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`）

live matrixに含められる他のproviders（認証情報/configがある場合）:

- 組み込み: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers` 経由（custom endpoints）: `minimax`（cloud/API）、およびOpenAI/Anthropic互換proxy（LM Studio、vLLM、LiteLLMなど）

ヒント: ドキュメントに「全models」をハードコードしようとしないでください。権威ある一覧は、あなたのマシンで `discoverModels(...)` が返すものと、利用可能なキーに依存します。

## 認証情報（コミットしないこと）

liveテストは、CLIと同じ方法で認証情報を見つけます。実務上の意味は次のとおりです:

- CLIが動くなら、liveテストも同じキーを見つけられるはずです。
- liveテストが「認証情報なし」と言うなら、`openclaw models list` / model selectionをデバッグするときと同じように調べてください。

- agentごとのauth profile: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（liveテストでいう「profile keys」とはこれです）
- Config: `~/.openclaw/openclaw.json`（または `OPENCLAW_CONFIG_PATH`）
- 旧state dir: `~/.openclaw/credentials/`（存在する場合はstage済みlive homeへコピーされますが、メインのprofile-key storeではありません）
- デフォルトでは、liveのローカル実行は、使用中のconfig、agentごとの `auth-profiles.json` ファイル、旧 `credentials/`、および対応する外部CLI auth dirを一時テストhomeへコピーします。このstage済みconfigでは、`agents.*.workspace` / `agentDir` のパス上書きは取り除かれ、probeが実際のhost workspaceに触れないようにします。

環境変数のキー（例: `~/.profile` でexport済み）に頼りたい場合は、ローカルテストを `source ~/.profile` の後で実行するか、下記のDockerランナーを使ってください（container内に `~/.profile` をmountできます）。

## Deepgram live（音声文字起こし）

- テスト: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 有効化: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- テスト: `src/agents/byteplus.live.test.ts`
- 有効化: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 任意のmodel上書き: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- テスト: `extensions/comfy/comfy.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- 対象範囲:
  - バンドルされたcomfy image、video、`music_generate` パスを実行
  - `models.providers.comfy.<capability>` が設定されていなければ各capabilityをskip
  - comfy workflow submission、polling、downloads、plugin registrationを変更した後に有用

## Image generation live

- テスト: `src/image-generation/runtime.live.test.ts`
- コマンド: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- 対象範囲:
  - 登録されたすべてのimage-generation provider pluginを列挙
  - probe前にlogin shell（`~/.profile`）から不足しているprovider環境変数を読み込む
  - デフォルトでは保存済みauth profileよりlive/env API keysを優先するため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠すことがない
  - 使えるauth/profile/modelがないproviderはskip
  - 標準のimage-generation variantを共有runtime capability経由で実行:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 現在カバーされる組み込みprovider:
  - `openai`
  - `google`
- 任意の絞り込み:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 任意のauth動作:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Music generation live

- テスト: `extensions/music-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- 対象範囲:
  - 共有のバンドル済みmusic-generation provider pathを実行
  - 現在はGoogleとMiniMaxをカバー
  - probe前にlogin shell（`~/.profile`）からprovider環境変数を読み込む
  - デフォルトでは保存済みauth profileよりlive/env API keysを優先するため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠すことがない
  - 使えるauth/profile/modelがないproviderはskip
  - 利用可能な場合、宣言済みの両runtime modeを実行:
    - prompt-only入力の `generate`
    - providerが `capabilities.edit.enabled` を宣言している場合の `edit`
  - 現在の共有laneカバレッジ:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: 別のComfy liveファイルで扱い、この共有sweepでは扱わない
- 任意の絞り込み:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- 任意のauth動作:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Video generation live

- テスト: `extensions/video-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- 対象範囲:
  - 共有のバンドル済みvideo-generation provider pathを実行
  - probe前にlogin shell（`~/.profile`）からprovider環境変数を読み込む
  - デフォルトでは保存済みauth profileよりlive/env API keysを優先するため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠すことがない
  - 使えるauth/profile/modelがないproviderはskip
  - 利用可能な場合、宣言済みの両runtime modeを実行:
    - prompt-only入力の `generate`
    - providerが `capabilities.imageToVideo.enabled` を宣言しており、選択したprovider/modelが共有sweepでbuffer-backed local image inputを受け付ける場合の `imageToVideo`
    - providerが `capabilities.videoToVideo.enabled` を宣言しており、選択したprovider/modelが共有sweepでbuffer-backed local video inputを受け付ける場合の `videoToVideo`
  - 共有sweepで現在「宣言済みだがskip」される `imageToVideo` provider:
    - `vydra`。バンドルされた `veo3` はtext-onlyで、バンドルされた `kling` はremote image URLを必要とするため
  - provider固有のVydraカバレッジ:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - このファイルはデフォルトで、`veo3` のtext-to-videoと、remote image URL fixtureを使う `kling` laneを実行します
  - 現在の `videoToVideo` liveカバレッジ:
    - 選択したmodelが `runway/gen4_aleph` の場合のみ `runway`
  - 共有sweepで現在「宣言済みだがskip」される `videoToVideo` provider:
    - `alibaba`、`qwen`、`xai`。これらのパスは現在remote `http(s)` / MP4 reference URLを必要とするため
    - `google`。現在の共有Gemini/Veo laneはlocal buffer-backed inputを使っており、そのパスは共有sweepでは受け付けられないため
    - `openai`。現在の共有laneにはorg固有のvideo inpaint/remix access保証がないため
- 任意の絞り込み:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- 任意のauth動作:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Media live harness

- コマンド: `pnpm test:live:media`
- 目的:
  - 共有image、music、video liveスイートを1つのrepoネイティブentrypoint経由で実行
  - `~/.profile` から不足しているprovider環境変数を自動読み込み
  - デフォルトで、現在使えるauthを持つproviderへ各スイートを自動的に絞り込む
  - `scripts/test-live.mjs` を再利用するため、heartbeatとquiet-modeの動作が一貫する
- 例:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Dockerランナー（任意の「Linuxで動く」確認）

これらのDockerランナーは2つのグループに分かれます:

- Live-modelランナー: `test:docker:live-models` と `test:docker:live-gateway` は、それぞれ対応するprofile-key liveファイルのみをrepo Docker image内で実行します（`src/agents/models.profiles.live.test.ts` と `src/gateway/gateway-models.profiles.live.test.ts`）。ローカルのconfig dirとworkspaceをmountし（mountされていれば `~/.profile` も読み込む）、対応するローカルentrypointは `test:live:models-profiles` と `test:live:gateway-profiles` です。
- Docker liveランナーは、フルDocker sweepを現実的に保つため、デフォルトで小さめのsmoke capを使います:
  `test:docker:live-models` はデフォルトで `OPENCLAW_LIVE_MAX_MODELS=12`、`test:docker:live-gateway` はデフォルトで `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、`OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、`OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`、`OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` を使用します。より大きく網羅的なscanを明示的に望む場合は、これらの環境変数を上書きしてください。
- `test:docker:all` は `test:docker:live-build` でlive Docker imageを一度だけbuildし、その後2つのlive Docker laneで再利用します。
- Container smokeランナー: `test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels`、`test:docker:plugins` は、1つ以上の実containerを起動し、より高レベルのintegration pathを検証します。

live-model Dockerランナーは、必要なCLI auth homeだけをbind-mountし（実行が絞られていない場合は対応するものをすべて）、その後container homeへコピーしてから実行するため、外部CLI OAuthはホストauth storeを変更せずにtoken更新できます:

- Direct models: `pnpm test:docker:live-models`（script: `scripts/test-live-models-docker.sh`）
- ACP bind smoke: `pnpm test:docker:live-acp-bind`（script: `scripts/test-live-acp-bind-docker.sh`）
- CLI backend smoke: `pnpm test:docker:live-cli-backend`（script: `scripts/test-live-cli-backend-docker.sh`）
- Gateway + dev agent: `pnpm test:docker:live-gateway`（script: `scripts/test-live-gateway-models-docker.sh`）
- Open WebUI live smoke: `pnpm test:docker:openwebui`（script: `scripts/e2e/openwebui-docker.sh`）
- Onboardingウィザード（TTY、完全scaffolding）: `pnpm test:docker:onboard`（script: `scripts/e2e/onboard-docker.sh`）
- Gateway networking（2 containers、WS auth + health）: `pnpm test:docker:gateway-network`（script: `scripts/e2e/gateway-network-docker.sh`）
- MCP channel bridge（seed済みGateway + stdio bridge + 生のClaude notification-frame smoke）: `pnpm test:docker:mcp-channels`（script: `scripts/e2e/mcp-channels-docker.sh`）
- Plugins（install smoke + `/plugin` alias + Claude-bundle restart semantics）: `pnpm test:docker:plugins`（script: `scripts/e2e/plugins-docker.sh`）

live-model Dockerランナーは、現在のcheckoutも読み取り専用でbind-mountし、
container内の一時workdirへstageします。これによりruntime
imageをスリムに保ちつつ、あなたの正確なローカルsource/configに対してVitestを実行できます。
stage手順では、大きなローカル専用cacheやapp build出力、たとえば
`.pnpm-store`、`.worktrees`、`__openclaw_vitest__`、appローカルの `.build` または
Gradle出力ディレクトリをスキップするため、Docker live実行で
マシン固有のartifactをコピーするのに何分も費やすことがありません。
さらに、`OPENCLAW_SKIP_CHANNELS=1` も設定するため、gateway live probeは
container内で本物のTelegram/Discordなどのchannel workerを起動しません。
`test:docker:live-models` はそれでも `pnpm test:live` を実行するため、
そのDocker laneからgateway
live coverageを絞り込みまたは除外したい場合は `OPENCLAW_LIVE_GATEWAY_*` も渡してください。
`test:docker:openwebui` はより高レベルな互換性smokeです。これは
OpenAI互換HTTP endpointを有効にしたOpenClaw gateway containerを起動し、
そのgatewayに対してpinされたOpen WebUI containerを起動し、さらに
Open WebUI経由でサインインし、`/api/models` が `openclaw/default` を公開していることを確認し、その後
Open WebUIの `/api/chat/completions` proxy経由で
実際のchat requestを送信します。
最初の実行は体感的にかなり遅いことがあります。Dockerが
Open WebUI imageをpullする必要があり、Open WebUI自体も
cold-startセットアップを完了する必要があるためです。
このlaneは利用可能なlive model keyを前提としており、Dockerized実行で
それを提供する主な方法は `OPENCLAW_PROFILE_FILE`
（デフォルトは `~/.profile`）です。
成功した実行では `{ "ok": true, "model":
"openclaw/default", ... }` のような小さなJSON payloadが出力されます。
`test:docker:mcp-channels` は意図的に決定的であり、
実際のTelegram、Discord、iMessageアカウントは必要ありません。seed済みGateway
containerを起動し、次に `openclaw mcp serve` を起動する第2のcontainerを開始し、
その後、ルーティングされたconversation discovery、transcript reads、attachment metadata、
live event queue動作、outbound send routing、およびClaude風のchannel +
permission notificationを、実際のstdio MCP bridge上で検証します。notificationチェックは
生のstdio MCP frameを直接検査するため、このsmokeは、特定のclient SDKがたまたま表面化するものだけでなく、
bridgeが実際に出力する内容を検証します。

手動ACP平文thread smoke（CIではない）:

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- このscriptはリグレッション/デバッグ用ワークフローのために保持してください。ACP thread routing検証で再び必要になる可能性があるため、削除しないでください。

便利な環境変数:

- `OPENCLAW_CONFIG_DIR=...`（デフォルト: `~/.openclaw`）を `/home/node/.openclaw` にmount
- `OPENCLAW_WORKSPACE_DIR=...`（デフォルト: `~/.openclaw/workspace`）を `/home/node/.openclaw/workspace` にmount
- `OPENCLAW_PROFILE_FILE=...`（デフォルト: `~/.profile`）を `/home/node/.profile` にmountし、テスト実行前にsource
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）を、Docker内でCLI installをキャッシュするため `/home/node/.npm-global` にmount
- `$HOME` 配下の外部CLI auth dirs/filesは、`/host-auth...` 配下に読み取り専用でmountされ、その後テスト開始前に `/home/node/...` へコピーされる
  - デフォルトdir: `.minimax`
  - デフォルトfile: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - 絞り込まれたprovider実行では、`OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` から推定される必要なdirs/filesのみをmount
  - 手動上書きは `OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`、または `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` のようなカンマ区切りリストで可能
- 実行を絞るには `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- container内でproviderをフィルタするには `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- 認証情報がprofile storeから来ることを保証するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`（envは使わない）
- Open WebUI smokeでgatewayが公開するmodelを選ぶには `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUI smokeで使うnonce-check promptを上書きするには `OPENCLAW_OPENWEBUI_PROMPT=...`
- pinされたOpen WebUI image tagを上書きするには `OPENWEBUI_IMAGE=...`

## Docsの健全性確認

ドキュメント編集後はdocsチェックを実行: `pnpm check:docs`。
ページ内見出しチェックも必要な場合は、完全なMintlify anchor検証を実行: `pnpm docs:check-links:anchors`。

## Offline regression（CI安全）

これらは、実providerなしで「実パイプライン」を検証するリグレッションです:

- Gateway tool calling（mock OpenAI、実gateway + agent loop）: `src/gateway/gateway.test.ts`（ケース: "runs a mock OpenAI tool call end-to-end via gateway agent loop"）
- Gateway wizard（WS `wizard.start`/`wizard.next`、config + auth enforcedの書き込み）: `src/gateway/gateway.test.ts`（ケース: "runs wizard over ws and writes auth token config"）

## Agent reliability evals（Skills）

CI安全のテストとして、すでに「agent reliability evals」のように振る舞うものがいくつかあります:

- 実gateway + agent loopを通るmock tool-calling（`src/gateway/gateway.test.ts`）。
- session wiringとconfig effectを検証するend-to-end wizard flow（`src/gateway/gateway.test.ts`）。

Skillsについてまだ不足しているもの（[Skills](/tools/skills) 参照）:

- **Decisioning:** promptにskillsが列挙されたとき、agentは正しいskillを選ぶか（または無関係なものを避けるか）？
- **Compliance:** agentは使用前に `SKILL.md` を読み、必要な手順/引数に従うか？
- **Workflow contracts:** tool順序、session historyの引き継ぎ、sandbox boundaryを検証するmulti-turn scenario。

将来のevalsは、まず決定的であるべきです:

- mock providerを使ってtool call + 順序、skill file read、session wiringを検証するscenario runner。
- skillに焦点を当てた小規模なscenarioスイート（使うべき/避けるべき、gating、prompt injection）。
- CI安全スイートが整った後にのみ、任意のlive evals（オプトイン、env-gated）。

## Contract tests（pluginとchannelの形状）

Contract testsは、登録されたすべてのpluginとchannelが
そのinterface contractに準拠していることを検証します。発見されたすべてのpluginを反復し、
形状と動作に関する一連の検証を実行します。デフォルトの `pnpm test` unit laneは、
これらの共有seamおよびsmokeファイルを意図的に
スキップします。共有channelまたはprovider surfaceに触れた場合は、
contractコマンドを明示的に実行してください。

### コマンド

- すべてのcontracts: `pnpm test:contracts`
- Channel contractsのみ: `pnpm test:contracts:channels`
- Provider contractsのみ: `pnpm test:contracts:plugins`

### Channel contracts

`src/channels/plugins/contracts/*.contract.test.ts` にあります:

- **plugin** - 基本的なplugin形状（id、name、capabilities）
- **setup** - セットアップウィザードcontract
- **session-binding** - Session binding動作
- **outbound-payload** - メッセージpayload構造
- **inbound** - 受信メッセージ処理
- **actions** - Channel action handler
- **threading** - Thread ID処理
- **directory** - Directory/roster API
- **group-policy** - Group policyの強制

### Provider status contracts

`src/plugins/contracts/*.contract.test.ts` にあります。

- **status** - Channel status probe
- **registry** - Plugin registryの形状

### Provider contracts

`src/plugins/contracts/*.contract.test.ts` にあります:

- **auth** - Auth flow contract
- **auth-choice** - Auth choice/selection
- **catalog** - Model catalog API
- **discovery** - Plugin discovery
- **loader** - Plugin loading
- **runtime** - Provider runtime
- **shape** - Plugin shape/interface
- **wizard** - セットアップウィザード

### 実行すべきタイミング

- plugin-sdk exportまたはsubpathを変更した後
- channelまたはprovider pluginを追加または変更した後
- plugin registrationまたはdiscoveryをリファクタした後

Contract testsはCIで実行され、実際のAPI keysは必要ありません。

## リグレッション追加のガイダンス

liveで発見されたprovider/modelの問題を修正したとき:

- 可能ならCI安全なリグレッションを追加してください（mock/stub provider、または正確なrequest-shape transformationのキャプチャ）
- 本質的にlive専用の場合（rate limits、auth policies）は、liveテストを狭く保ち、環境変数でオプトインにしてください
- バグを捉えられる最小の層を狙うことを優先してください:
  - provider request conversion/replay bug → direct models test
  - gateway session/history/tool pipeline bug → gateway live smokeまたはCI安全なgateway mock test
- SecretRef traversal guardrail:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` は、registry metadata（`listSecretTargetRegistryEntries()`）からSecretRef classごとに1つのsampled targetを導出し、そのうえでtraversal-segment exec idが拒否されることを検証します。
  - `src/secrets/target-registry-data.ts` に新しい `includeInPlan` SecretRef target familyを追加した場合は、そのテスト内の `classifyTargetClass` を更新してください。このテストは、未分類のtarget idがあると意図的に失敗するため、新しいclassが黙ってスキップされることはありません。
