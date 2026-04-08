---
read_when:
    - ローカルまたはCIでテストを実行する場合
    - モデル/プロバイダーのバグに対するリグレッションを追加する場合
    - Gateway + エージェントの動作をデバッグする場合
summary: 'テストキット: unit/e2e/liveスイート、Dockerランナー、および各テストの対象範囲'
title: テスト
x-i18n:
    generated_at: "2026-04-08T02:18:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: ace2c19bfc350780475f4348264a4b55be2b4ccbb26f0d33b4a6af34510943b5
    source_path: help/testing.md
    workflow: 15
---

# テスト

OpenClawには3つのVitestスイート（unit/integration、e2e、live）と、少数のDockerランナーがあります。

このドキュメントは「どのようにテストするか」のガイドです:

- 各スイートが何をカバーするか（そして意図的に_カバーしない_ものは何か）
- よくあるワークフロー（ローカル、push前、デバッグ）でどのコマンドを実行するか
- liveテストが資格情報をどのように検出し、モデル/プロバイダーを選択するか
- 実際のモデル/プロバイダー問題に対するリグレッションの追加方法

## クイックスタート

普段は次のとおりです:

- フルゲート（push前に期待される）: `pnpm build && pnpm check && pnpm test`
- 余裕のあるマシンでの、より高速なローカル全スイート実行: `pnpm test:max`
- 直接Vitest watchループ: `pnpm test:watch`
- 直接のファイル指定は、拡張機能/チャンネルのパスもルーティングするようになりました: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- DockerベースのQAサイト: `pnpm qa:lab:up`

テストに触れた場合や、さらに確信がほしい場合:

- カバレッジゲート: `pnpm test:coverage`
- E2Eスイート: `pnpm test:e2e`

実際のプロバイダー/モデルをデバッグする場合（実際の資格情報が必要）:

- Liveスイート（モデル + Gatewayツール/画像probe）: `pnpm test:live`
- 1つのliveファイルを静かに対象指定: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

ヒント: 失敗しているケースが1つだけ必要な場合は、以下で説明するallowlist環境変数を使ってliveテストを絞り込む方が適しています。

## テストスイート（どこで何が実行されるか）

スイートは「現実性が増す順」（そして不安定さ/コストも増す順）と考えてください:

### Unit / integration（デフォルト）

- コマンド: `pnpm test`
- 設定: 既存のスコープ付きVitestプロジェクトに対する10個の逐次シャード実行（`vitest.full-*.config.ts`）
- ファイル: `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts`配下のcore/unitインベントリと、`vitest.unit.config.ts`でカバーされる許可済みの`ui` nodeテスト
- 範囲:
  - 純粋なunitテスト
  - インプロセスintegrationテスト（Gateway認証、ルーティング、ツール、パース、設定）
  - 既知のバグに対する決定的なリグレッション
- 期待値:
  - CIで実行される
  - 実際のキーは不要
  - 高速で安定しているべき
- プロジェクトに関する補足:
  - 対象を絞らない`pnpm test`は、1つの巨大なネイティブルートプロジェクトプロセスではなく、11個のより小さなシャード設定（`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`）を実行するようになりました。これにより、負荷の高いマシンでのピークRSSを削減し、auto-reply/extensionの処理が無関係なスイートを圧迫するのを避けられます。
  - `pnpm test --watch`は、マルチシャードのwatchループが実用的ではないため、引き続きネイティブルートの`vitest.config.ts`プロジェクトグラフを使用します。
  - `pnpm test`、`pnpm test:watch`、`pnpm test:perf:imports`は、明示的なファイル/ディレクトリ指定をまずスコープ付きレーン経由でルーティングするため、`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`ではルートプロジェクト全体の起動コストを払わずに済みます。
  - `pnpm test:changed`は、差分がルーティング可能なソース/テストファイルのみに触れている場合、変更されたgitパスを同じスコープ付きレーンに展開します。設定/セットアップ編集は、引き続き広範囲のルートプロジェクト再実行にフォールバックします。
  - 選択された`plugin-sdk`および`commands`テストも、`test/setup-openclaw-runtime.ts`をスキップする専用の軽量レーンを通るようになりました。状態保持型/ランタイム負荷の高いファイルは既存レーンのままです。
  - 選択された`plugin-sdk`および`commands`のヘルパーソースファイルも、changedモード実行をそれら軽量レーン内の明示的な兄弟テストにマップするため、ヘルパー編集でそのディレクトリの重いスイート全体を再実行する必要がありません。
  - `auto-reply`には現在3つの専用バケットがあります: 最上位coreヘルパー、最上位`reply.*` integrationテスト、そして`src/auto-reply/reply/**`サブツリーです。これにより、最も重いreplyハーネス処理を、軽量なstatus/chunk/tokenテストから切り離せます。
- Embedded runnerに関する補足:
  - メッセージツール検出入力や圧縮ランタイムコンテキストを変更する場合は、
    両方のレベルのカバレッジを維持してください。
  - 純粋なルーティング/正規化境界に対しては、焦点を絞ったヘルパーリグレッションを追加してください。
  - さらに、embedded runnerのintegrationスイートも健全に保ってください:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`, および
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - これらのスイートは、スコープ付きidと圧縮動作が実際の
    `run.ts` / `compact.ts`パスを通って流れ続けることを検証します。ヘルパー専用テストだけでは、
    これらのintegrationパスの十分な代替にはなりません。
- Poolに関する補足:
  - ベースのVitest設定は現在デフォルトで`threads`です。
  - 共有Vitest設定では、`isolate: false`も固定されており、ルートプロジェクト、e2e、live設定全体で非分離ランナーを使用します。
  - ルートUIレーンは`jsdom`セットアップとoptimizerを維持していますが、現在は共有の非分離ランナー上でも実行されます。
  - 各`pnpm test`シャードは、共有Vitest設定から同じ`threads` + `isolate: false`デフォルトを継承します。
  - 共有の`scripts/run-vitest.mjs`ランチャーは、Vitest子Nodeプロセスに対してデフォルトで`--no-maglev`も追加するようになり、大規模なローカル実行時のV8コンパイルの揺らぎを減らします。標準のV8動作と比較したい場合は`OPENCLAW_VITEST_ENABLE_MAGLEV=1`を設定してください。
- 高速なローカル反復に関する補足:
  - `pnpm test:changed`は、変更パスがより小さいスイートにきれいにマップされる場合、スコープ付きレーン経由でルーティングします。
  - `pnpm test:max`と`pnpm test:changed:max`も同じルーティング動作を維持しつつ、worker上限だけ高くしています。
  - ローカルworker自動スケーリングは現在意図的に保守的で、ホストの負荷平均がすでに高い場合にも抑制されるため、複数のVitest実行が同時に走っても既定では影響を抑えられます。
  - ベースのVitest設定は、テスト配線が変わったときでもchangedモード再実行の正しさを保つため、プロジェクト/設定ファイルを`forceRerunTriggers`としてマークしています。
  - 設定は、対応ホストでは`OPENCLAW_VITEST_FS_MODULE_CACHE`を有効のままにします。直接プロファイリング用に明示的なキャッシュ場所を1つ指定したい場合は、`OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path`を設定してください。
- Perfデバッグに関する補足:
  - `pnpm test:perf:imports`は、Vitestのimport所要時間レポートとimport内訳出力を有効にします。
  - `pnpm test:perf:imports:changed`は、`origin/main`以降に変更されたファイルに同じプロファイリング表示を絞り込みます。
- `pnpm test:perf:changed:bench -- --ref <git-ref>`は、そのコミット差分に対してルーティングされた`test:changed`とネイティブルートプロジェクト経路を比較し、wall timeとmacOS max RSSを出力します。
- `pnpm test:perf:changed:bench -- --worktree`は、変更ファイル一覧を`scripts/test-projects.mjs`とルートVitest設定に通すことで、現在のdirty treeをベンチマークします。
  - `pnpm test:perf:profile:main`は、Vitest/Viteの起動とtransformオーバーヘッドに対するメインスレッドCPUプロファイルを書き出します。
  - `pnpm test:perf:profile:runner`は、unitスイートでファイル並列実行を無効にした状態のrunner CPU+heapプロファイルを書き出します。

### E2E（Gatewayスモーク）

- コマンド: `pnpm test:e2e`
- 設定: `vitest.e2e.config.ts`
- ファイル: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- ランタイムデフォルト:
  - リポジトリ内の他と同様、Vitest `threads`と`isolate: false`を使用します。
  - 適応型workerを使用します（CI: 最大2、ローカル: デフォルト1）。
  - コンソールI/Oオーバーヘッドを減らすため、デフォルトでsilentモードで実行します。
- 便利な上書き:
  - worker数を強制するには`OPENCLAW_E2E_WORKERS=<n>`（上限16）。
  - 詳細なコンソール出力を再有効化するには`OPENCLAW_E2E_VERBOSE=1`。
- 範囲:
  - マルチインスタンスGatewayのエンドツーエンド動作
  - WebSocket/HTTPサーフェス、ノードペアリング、およびより重いネットワーク処理
- 期待値:
  - CIで実行される（パイプラインで有効な場合）
  - 実際のキーは不要
  - unitテストより可動部が多い（遅くなる場合がある）

### E2E: OpenShellバックエンドスモーク

- コマンド: `pnpm test:e2e:openshell`
- ファイル: `test/openshell-sandbox.e2e.test.ts`
- 範囲:
  - Docker経由でホスト上に分離されたOpenShell Gatewayを起動
  - 一時的なローカルDockerfileからsandboxを作成
  - 実際の`sandbox ssh-config` + SSH execを通じて、OpenClawのOpenShellバックエンドを実行
  - sandbox fs bridgeを通じて、remote-canonicalなファイルシステム動作を検証
- 期待値:
  - オプトインのみ。デフォルトの`pnpm test:e2e`実行には含まれない
  - ローカルの`openshell` CLIと動作するDockerデーモンが必要
  - 分離された`HOME` / `XDG_CONFIG_HOME`を使用し、その後テストGatewayとsandboxを破棄する
- 便利な上書き:
  - 広範なe2eスイートを手動実行する際にこのテストを有効化するには`OPENCLAW_E2E_OPENSHELL=1`
  - デフォルト以外のCLIバイナリやラッパースクリプトを指定するには`OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live（実プロバイダー + 実モデル）

- コマンド: `pnpm test:live`
- 設定: `vitest.live.config.ts`
- ファイル: `src/**/*.live.test.ts`
- デフォルト: `pnpm test:live`により**有効**（`OPENCLAW_LIVE_TEST=1`を設定）
- 範囲:
  - 「このプロバイダー/モデルは、実際の資格情報で_今日_本当に動くか？」
  - プロバイダー形式の変更、tool-callingの癖、認証問題、レート制限動作を検出
- 期待値:
  - 設計上CIで安定しない（実ネットワーク、実プロバイダーポリシー、クォータ、障害）
  - コストがかかる / レート制限を使う
  - 「全部」ではなく、絞り込んだ部分集合の実行を推奨
- Live実行は、不足しているAPIキーを取得するために`~/.profile`を読み込みます。
- デフォルトでは、live実行は依然として`HOME`を分離し、設定/認証素材を一時的なテストホームへコピーするため、unitフィクスチャが実際の`~/.openclaw`を変更できません。
- liveテストで意図的に実際のホームディレクトリを使いたい場合にのみ、`OPENCLAW_LIVE_USE_REAL_HOME=1`を設定してください。
- `pnpm test:live`は現在、より静かなモードがデフォルトです: `[live] ...`進行出力は維持しますが、追加の`~/.profile`通知を抑制し、Gatewayブートストラップログ/Bonjourの雑音をミュートします。完全な起動ログを戻したい場合は`OPENCLAW_LIVE_TEST_QUIET=0`を設定してください。
- APIキーのローテーション（プロバイダー別）: カンマ/セミコロン形式の`*_API_KEYS`または`*_API_KEY_1`, `*_API_KEY_2`（例: `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`）、またはlive専用上書きとして`OPENCLAW_LIVE_*_KEY`を設定してください。テストはレート制限応答時に再試行します。
- 進捗/heartbeat出力:
  - Liveスイートは現在、長いプロバイダー呼び出し中でも視覚的に動作していることが分かるよう、stderrへ進捗行を出力します。Vitestコンソールキャプチャが静かでも有効です。
  - `vitest.live.config.ts`はVitestのコンソール捕捉を無効化しているため、プロバイダー/Gatewayの進捗行がlive実行中に即座にストリーミングされます。
  - 直接モデルheartbeatは`OPENCLAW_LIVE_HEARTBEAT_MS`で調整します。
  - Gateway/probe heartbeatは`OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`で調整します。

## どのスイートを実行すべきか

次の判断表を使ってください:

- ロジック/テストを編集している: `pnpm test`を実行（大きく変更した場合は`pnpm test:coverage`も）
- Gatewayネットワーキング / WSプロトコル / ペアリングに触れた: `pnpm test:e2e`も追加
- 「ボットが落ちている」/ プロバイダー固有の失敗 / tool callingをデバッグしている: 絞り込んだ`pnpm test:live`を実行

## Live: Androidノード機能スイープ

- テスト: `src/gateway/android-node.capabilities.live.test.ts`
- スクリプト: `pnpm android:test:integration`
- 目的: 接続済みのAndroidノードが**現在通知しているすべてのコマンド**を呼び出し、コマンド契約の動作を検証すること。
- 範囲:
  - 前提条件付き/手動セットアップ（このスイートはアプリをインストール/起動/ペアリングしません）。
  - 選択されたAndroidノードに対する、コマンド単位のGateway `node.invoke`検証。
- 必要な事前セットアップ:
  - AndroidアプリがすでにGatewayへ接続済み + ペアリング済みであること。
  - アプリがフォアグラウンドに維持されていること。
  - 成功を期待する機能に対して、権限/キャプチャ同意が付与されていること。
- オプションの対象上書き:
  - `OPENCLAW_ANDROID_NODE_ID`または`OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- Androidの完全なセットアップ詳細: [Android App](/ja-JP/platforms/android)

## Live: モデルスモーク（プロファイルキー）

Liveテストは、失敗を切り分けられるよう2つの層に分かれています:

- 「Direct model」は、そのキーでプロバイダー/モデルが少なくとも応答できることを示します。
- 「Gateway smoke」は、そのモデルに対して完全なGateway+エージェントパイプライン（セッション、履歴、ツール、sandboxポリシーなど）が動作することを示します。

### レイヤー1: Direct model completion（Gatewayなし）

- テスト: `src/agents/models.profiles.live.test.ts`
- 目的:
  - 検出されたモデルを列挙する
  - `getApiKeyForModel`を使って、資格情報を持っているモデルを選択する
  - モデルごとに小さなcompletionを実行する（必要に応じて対象リグレッションも）
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接起動する場合は`OPENCLAW_LIVE_TEST=1`）
- このスイートを実際に実行するには`OPENCLAW_LIVE_MODELS=modern`（またはmodernの別名である`all`）を設定してください。そうしないと、`pnpm test:live`をGateway smokeに集中させるためにスキップされます
- モデルの選択方法:
  - modern allowlistを実行するには`OPENCLAW_LIVE_MODELS=modern`（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all`はmodern allowlistの別名です
  - または`OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（カンマ区切りallowlist）
- プロバイダーの選択方法:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（カンマ区切りallowlist）
- キーの取得元:
  - デフォルト: プロファイルストアと環境フォールバック
  - **プロファイルストアのみ**を強制するには`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`を設定
- この層の存在理由:
  - 「プロバイダーAPIが壊れている / キーが無効」と「Gatewayエージェントパイプラインが壊れている」を分離するため
  - 小さく分離されたリグレッションを収めるため（例: OpenAI Responses/Codex Responsesのreasoning replay + tool-callフロー）

### レイヤー2: Gateway + dev agent smoke（「@openclaw」が実際に行うこと）

- テスト: `src/gateway/gateway-models.profiles.live.test.ts`
- 目的:
  - インプロセスGatewayを起動
  - `agent:dev:*`セッションを作成/patchする（実行ごとのモデル上書き）
  - キー付きモデルを反復し、以下を検証:
    - 「意味のある」応答（ツールなし）
    - 実際のツール呼び出しが動作する（read probe）
    - オプションの追加ツールprobe（exec+read probe）
    - OpenAIのリグレッション経路（tool-call-only → follow-up）が動き続ける
- Probeの詳細（失敗をすばやく説明できるように）:
  - `read` probe: テストがworkspace内にnonceファイルを書き込み、エージェントにそれを`read`してnonceをそのまま返すよう求めます。
  - `exec+read` probe: テストがエージェントに、一時ファイルへnonceを書き込む`exec`を行い、その後それを`read`して返すよう求めます。
  - image probe: テストが生成したPNG（cat + ランダム化コード）を添付し、モデルが`cat <CODE>`を返すことを期待します。
  - 実装参照: `src/gateway/gateway-models.profiles.live.test.ts`および`src/gateway/live-image-probe.ts`。
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接起動する場合は`OPENCLAW_LIVE_TEST=1`）
- モデルの選択方法:
  - デフォルト: modern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all`はmodern allowlistの別名です
  - または`OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（またはカンマ区切りリスト）で絞り込み
- プロバイダーの選択方法（「OpenRouter全部」を避ける）:
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（カンマ区切りallowlist）
- このliveテストではツール + image probeが常に有効です:
  - `read` probe + `exec+read` probe（ツールストレス）
  - モデルが画像入力サポートを通知している場合、image probeが実行されます
  - フロー（高レベル）:
    - テストが「CAT」+ ランダムコード入りの小さなPNGを生成します（`src/gateway/live-image-probe.ts`）
    - `agent`の`attachments: [{ mimeType: "image/png", content: "<base64>" }]`経由で送信します
    - Gatewayが添付を`images[]`へパースします（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - Embedded agentがマルチモーダルなユーザーメッセージをモデルへ転送します
    - アサーション: 返信に`cat` + そのコードが含まれます（OCR耐性: 軽微な誤りは許容）

ヒント: 自分のマシンで何をテストできるか（および正確な`provider/model` id）を確認するには、次を実行してください:

```bash
openclaw models list
openclaw models list --json
```

## Live: CLIバックエンドスモーク（Claude、Codex、Gemini、またはその他のローカルCLI）

- テスト: `src/gateway/gateway-cli-backend.live.test.ts`
- 目的: デフォルト設定に触れずに、ローカルCLIバックエンドを使ってGateway + エージェントパイプラインを検証すること。
- バックエンド固有のスモークデフォルトは、所有する拡張機能の`cli-backend.ts`定義内にあります。
- 有効化:
  - `pnpm test:live`（またはVitestを直接起動する場合は`OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- デフォルト:
  - デフォルトのプロバイダー/モデル: `claude-cli/claude-sonnet-4-6`
  - コマンド/引数/画像動作は、所有するCLIバックエンドプラグインのメタデータから取得されます。
- 上書き（任意）:
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - 実際の画像添付を送るには`OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`（パスはプロンプトに注入されます）。
  - プロンプト注入ではなくCLI引数として画像ファイルパスを渡すには`OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`。
  - `IMAGE_ARG`が設定されている場合の画像引数の渡し方を制御するには`OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（または`"list"`）。
  - 第2ターンを送ってresumeフローを検証するには`OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`。
  - デフォルトのClaude Sonnet -> Opus同一セッション継続性probeを無効にするには`OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0`（選択モデルが切り替え先をサポートしている場合に強制的に有効化するには`1`）。

例:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Dockerレシピ:

```bash
pnpm test:docker:live-cli-backend
```

単一プロバイダーDockerレシピ:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

補足:

- Dockerランナーは`scripts/test-live-cli-backend-docker.sh`にあります。
- これはリポジトリDockerイメージ内で、非rootの`node`ユーザーとしてlive CLIバックエンドスモークを実行します。
- 所有する拡張機能からCLIスモークメタデータを解決し、その後、対応するLinux CLIパッケージ（`@anthropic-ai/claude-code`, `@openai/codex`, または`@google/gemini-cli`）を、`OPENCLAW_DOCKER_CLI_TOOLS_DIR`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）にあるキャッシュ可能な書き込み可能プレフィックスへインストールします。
- live CLIバックエンドスモークは現在、Claude、Codex、Geminiに対して同じエンドツーエンドフローを実行します: テキストターン、画像分類ターン、そしてGateway CLI経由で検証されるMCP `cron`ツール呼び出しです。
- Claudeのデフォルトスモークは、セッションをSonnetからOpusへpatchし、resumeされたセッションが以前のメモをまだ覚えていることも検証します。

## Live: ACP bindスモーク（`/acp spawn ... --bind here`）

- テスト: `src/gateway/gateway-acp-bind.live.test.ts`
- 目的: live ACPエージェントを使用した実際のACP conversation-bindフローを検証すること:
  - `/acp spawn <agent> --bind here`を送信する
  - syntheticなmessage-channel会話をその場でbindする
  - 同じ会話上で通常のfollow-upを送信する
  - そのfollow-upがbindされたACPセッショントランスクリプトに到達することを検証する
- 有効化:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- デフォルト:
  - Docker内のACPエージェント: `claude,codex,gemini`
  - 直接`pnpm test:live ...`用のACPエージェント: `claude`
  - syntheticチャンネル: Slack DM風の会話コンテキスト
  - ACPバックエンド: `acpx`
- 上書き:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 補足:
  - このレーンは、admin専用のsynthetic originating-routeフィールド付きのGateway `chat.send`サーフェスを使用するため、外部配信を装わずにmessage-channelコンテキストをテストへ付与できます。
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND`が未設定の場合、テストは、選択されたACPハーネスエージェントに対して埋め込み`acpx`プラグインの組み込みエージェントレジストリを使用します。

例:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Dockerレシピ:

```bash
pnpm test:docker:live-acp-bind
```

単一エージェントDockerレシピ:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Dockerに関する補足:

- Dockerランナーは`scripts/test-live-acp-bind-docker.sh`にあります。
- デフォルトでは、サポートされているすべてのlive CLIエージェントに対してACP bindスモークを順番に実行します: `claude`、`codex`、そして`gemini`です。
- マトリクスを絞るには`OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`、`OPENCLAW_LIVE_ACP_BIND_AGENTS=codex`、または`OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini`を使ってください。
- これは`~/.profile`を読み込み、対応するCLI認証素材をコンテナへ配置し、書き込み可能なnpmプレフィックスへ`acpx`をインストールしてから、要求されたlive CLI（`@anthropic-ai/claude-code`, `@openai/codex`, または`@google/gemini-cli`）が存在しない場合にインストールします。
- Docker内では、runnerは`OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx`を設定し、読み込まれたprofileで利用可能なプロバイダー環境変数をacpxが子ハーネスCLIへ引き継げるようにします。

### 推奨liveレシピ

狭く明示的なallowlistが最も高速で不安定さも少なくなります:

- 単一モデル、direct（Gatewayなし）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 単一モデル、Gatewayスモーク:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 複数プロバイダーにまたがるtool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google重視（Gemini APIキー + Antigravity）:
  - Gemini（APIキー）: `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）: `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

補足:

- `google/...`はGemini APIを使用します（APIキー）。
- `google-antigravity/...`はAntigravity OAuth bridge（Cloud Code Assist風のagent endpoint）を使用します。
- `google-gemini-cli/...`はマシン上のローカルGemini CLIを使用します（別の認証 + ツールの癖があります）。
- Gemini APIとGemini CLI:
  - API: OpenClawはGoogleのホストされたGemini APIをHTTP経由で呼び出します（APIキー / プロファイル認証）。これが、ほとんどのユーザーが「Gemini」と言うときの意味です。
  - CLI: OpenClawはローカルの`gemini`バイナリをshell outして使います。独自の認証があり、挙動も異なる場合があります（ストリーミング/ツール対応/バージョン差異）。

## Live: モデルマトリクス（何をカバーするか）

固定の「CIモデル一覧」はありません（liveはオプトイン）ですが、キー付きの開発マシンで定期的にカバーすることを**推奨**するモデルは次のとおりです。

### Modernスモークセット（tool calling + image）

これは、動作し続けることを期待する「一般的なモデル」実行です:

- OpenAI（非Codex）: `openai/gpt-5.4`（任意: `openai/gpt-5.4-mini`）
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6`（または`anthropic/claude-sonnet-4-6`）
- Google（Gemini API）: `google/gemini-3.1-pro-preview`および`google/gemini-3-flash-preview`（古いGemini 2.xモデルは避けてください）
- Google（Antigravity）: `google-antigravity/claude-opus-4-6-thinking`および`google-antigravity/gemini-3-flash`
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

ツール + image付きGatewayスモークの実行:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### ベースライン: tool calling（Read + 任意のExec）

少なくともプロバイダーファミリーごとに1つは選んでください:

- OpenAI: `openai/gpt-5.4`（または`openai/gpt-5.4-mini`）
- Anthropic: `anthropic/claude-opus-4-6`（または`anthropic/claude-sonnet-4-6`）
- Google: `google/gemini-3-flash-preview`（または`google/gemini-3.1-pro-preview`）
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

追加の任意カバレッジ（あると望ましい）:

- xAI: `xai/grok-4`（または利用可能な最新）
- Mistral: `mistral/`…（有効化されている「tools」対応モデルを1つ選択）
- Cerebras: `cerebras/`…（アクセス権がある場合）
- LM Studio: `lmstudio/`…（ローカル; tool callingはAPIモードに依存）

### Vision: image send（添付 → マルチモーダルメッセージ）

image probeを実行するために、少なくとも1つの画像対応モデル（Claude/Gemini/OpenAIのvision対応バリアントなど）を`OPENCLAW_LIVE_GATEWAY_MODELS`に含めてください。

### Aggregator / 代替Gateway

キーが有効であれば、次経由のテストもサポートします:

- OpenRouter: `openrouter/...`（何百ものモデル; `openclaw models scan`を使ってtools+image対応候補を見つけてください）
- OpenCode: Zen用の`opencode/...`およびGo用の`opencode-go/...`（認証は`OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`）

さらに、liveマトリクスへ含められるプロバイダー（資格情報/設定がある場合）:

- 組み込み: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- `models.providers`経由（カスタムendpoint）: `minimax`（cloud/API）、および任意のOpenAI/Anthropic互換proxy（LM Studio、vLLM、LiteLLMなど）

ヒント: ドキュメント内に「すべてのモデル」をハードコードしないでください。権威ある一覧は、あなたのマシンで`discoverModels(...)`が返すもの + 利用可能なキーです。

## 資格情報（絶対にコミットしない）

Liveテストは、CLIと同じ方法で資格情報を検出します。実務上の意味は次のとおりです:

- CLIが動作するなら、liveテストも同じキーを見つけられるはずです。
- liveテストが「資格情報なし」と言う場合は、`openclaw models list` / モデル選択をデバッグするときと同じように調べてください。

- エージェント単位の認証プロファイル: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（これがliveテストでいう「プロファイルキー」です）
- 設定: `~/.openclaw/openclaw.json`（または`OPENCLAW_CONFIG_PATH`）
- レガシーstateディレクトリ: `~/.openclaw/credentials/`（存在する場合はステージされたliveホームへコピーされますが、メインのプロファイルキーストアではありません）
- ローカルのlive実行は、アクティブな設定、エージェント単位の`auth-profiles.json`ファイル、レガシー`credentials/`、およびサポートされる外部CLI認証ディレクトリをデフォルトで一時テストホームへコピーします。ステージされたliveホームでは`workspace/`と`sandboxes/`をスキップし、`agents.*.workspace` / `agentDir`パス上書きも取り除かれるため、probeが実際のホストworkspaceに触れません。

環境キー（たとえば`~/.profile`でexportされたもの）に依存したい場合は、`source ~/.profile`後にローカルテストを実行するか、以下のDockerランナーを使用してください（`~/.profile`をコンテナへマウント可能です）。

## Deepgram live（音声文字起こし）

- テスト: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 有効化: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- テスト: `src/agents/byteplus.live.test.ts`
- 有効化: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 任意のモデル上書き: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUIワークフローメディアlive

- テスト: `extensions/comfy/comfy.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- 範囲:
  - バンドル済みcomfyの画像、動画、および`music_generate`パスを実行
  - `models.providers.comfy.<capability>`が設定されていない限り、各機能をスキップ
  - comfyワークフロー送信、ポーリング、ダウンロード、またはプラグイン登録を変更した後に有用

## 画像生成live

- テスト: `src/image-generation/runtime.live.test.ts`
- コマンド: `pnpm test:live src/image-generation/runtime.live.test.ts`
- ハーネス: `pnpm test:live:media image`
- 範囲:
  - 登録されたすべての画像生成プロバイダープラグインを列挙
  - probe前に、ログインシェル（`~/.profile`）から不足しているプロバイダー環境変数を読み込む
  - デフォルトでは、保存済み認証プロファイルより先にlive/env APIキーを使用するため、`auth-profiles.json`内の古いテストキーが実際のシェル資格情報を隠しません
  - 使用可能な認証/プロファイル/モデルがないプロバイダーはスキップ
  - 共有ランタイム機能を通じて標準の画像生成バリアントを実行:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 現在カバーされているバンドル済みプロバイダー:
  - `openai`
  - `google`
- 任意の絞り込み:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 任意の認証動作:
  - プロファイルストア認証を強制し、env専用上書きを無視するには`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## 音楽生成live

- テスト: `extensions/music-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- ハーネス: `pnpm test:live:media music`
- 範囲:
  - 共有のバンドル済み音楽生成プロバイダーパスを実行
  - 現在はGoogleとMiniMaxをカバー
  - probe前に、ログインシェル（`~/.profile`）からプロバイダー環境変数を読み込む
  - デフォルトでは、保存済み認証プロファイルより先にlive/env APIキーを使用するため、`auth-profiles.json`内の古いテストキーが実際のシェル資格情報を隠しません
  - 使用可能な認証/プロファイル/モデルがないプロバイダーはスキップ
  - 利用可能な場合、宣言された両方のランタイムモードを実行:
    - プロンプトのみ入力での`generate`
    - プロバイダーが`capabilities.edit.enabled`を宣言している場合の`edit`
  - 現在の共有レーンカバレッジ:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: 別のComfy liveファイルであり、この共有スイープではない
- 任意の絞り込み:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- 任意の認証動作:
  - プロファイルストア認証を強制し、env専用上書きを無視するには`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## 動画生成live

- テスト: `extensions/video-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- ハーネス: `pnpm test:live:media video`
- 範囲:
  - 共有のバンドル済み動画生成プロバイダーパスを実行
  - probe前に、ログインシェル（`~/.profile`）からプロバイダー環境変数を読み込む
  - デフォルトでは、保存済み認証プロファイルより先にlive/env APIキーを使用するため、`auth-profiles.json`内の古いテストキーが実際のシェル資格情報を隠しません
  - 使用可能な認証/プロファイル/モデルがないプロバイダーはスキップ
  - 利用可能な場合、宣言された両方のランタイムモードを実行:
    - プロンプトのみ入力での`generate`
    - プロバイダーが`capabilities.imageToVideo.enabled`を宣言しており、選択されたプロバイダー/モデルが共有スイープでbufferベースのローカル画像入力を受け付ける場合の`imageToVideo`
    - プロバイダーが`capabilities.videoToVideo.enabled`を宣言しており、選択されたプロバイダー/モデルが共有スイープでbufferベースのローカル動画入力を受け付ける場合の`videoToVideo`
  - 共有スイープで現在は宣言済みだがスキップされる`imageToVideo`プロバイダー:
    - `vydra`。バンドル済み`veo3`はテキスト専用で、バンドル済み`kling`はリモート画像URLを必要とするため
  - プロバイダー固有のVydraカバレッジ:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - このファイルは、デフォルトでリモート画像URLフィクスチャを使う`kling`レーンとともに、`veo3`のtext-to-videoを実行します
  - 現在の`videoToVideo` liveカバレッジ:
    - 選択されたモデルが`runway/gen4_aleph`の場合のみ`runway`
  - 共有スイープで現在は宣言済みだがスキップされる`videoToVideo`プロバイダー:
    - `alibaba`, `qwen`, `xai`。これらのパスは現在、リモートの`http(s)` / MP4参照URLを必要とするため
    - `google`。現在の共有Gemini/Veoレーンはローカルbufferベース入力を使用しており、そのパスは共有スイープで受け付けられないため
    - `openai`。現在の共有レーンには、組織固有のvideo inpaint/remixアクセス保証がないため
- 任意の絞り込み:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- 任意の認証動作:
  - プロファイルストア認証を強制し、env専用上書きを無視するには`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## メディアliveハーネス

- コマンド: `pnpm test:live:media`
- 目的:
  - 共有の画像、音楽、動画liveスイートを、リポジトリネイティブな1つのentrypointから実行
  - `~/.profile`から不足しているプロバイダー環境変数を自動読み込み
  - デフォルトで、現在使用可能な認証を持つプロバイダーへ各スイートを自動的に絞り込み
  - `scripts/test-live.mjs`を再利用するため、heartbeatとquietモードの動作が一貫する
- 例:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Dockerランナー（任意の「Linuxで動く」チェック）

これらのDockerランナーは2つのグループに分かれます:

- Live-modelランナー: `test:docker:live-models`と`test:docker:live-gateway`は、対応するプロファイルキーliveファイルのみをリポジトリDockerイメージ内で実行します（`src/agents/models.profiles.live.test.ts`および`src/gateway/gateway-models.profiles.live.test.ts`）。ローカル設定ディレクトリとworkspaceをマウントし（マウントされていれば`~/.profile`も読み込む）、対応するローカルentrypointは`test:live:models-profiles`と`test:live:gateway-profiles`です。
- Docker liveランナーは、フルDockerスイープを実用的に保つため、デフォルトでより小さなスモーク上限を持ちます:
  `test:docker:live-models`はデフォルトで`OPENCLAW_LIVE_MAX_MODELS=12`、
  `test:docker:live-gateway`はデフォルトで`OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`、および
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`です。より大きく網羅的なスキャンを明示的に望む場合は、
  これらの環境変数を上書きしてください。
- `test:docker:all`は、まず`test:docker:live-build`経由でlive Dockerイメージを一度ビルドし、その後2つのlive Dockerレーンで再利用します。
- コンテナスモークランナー: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels`, および`test:docker:plugins`は、1つ以上の実コンテナを起動し、より高レベルなintegrationパスを検証します。

live-model Dockerランナーは、必要なCLI認証ホームのみ（または実行が絞り込まれていない場合はサポートされるものすべて）をbind mountし、その後、外部CLI OAuthがホスト認証ストアを変更せずにトークン更新できるよう、実行前にそれらをコンテナホームへコピーします:

- Direct models: `pnpm test:docker:live-models`（スクリプト: `scripts/test-live-models-docker.sh`）
- ACP bindスモーク: `pnpm test:docker:live-acp-bind`（スクリプト: `scripts/test-live-acp-bind-docker.sh`）
- CLIバックエンドスモーク: `pnpm test:docker:live-cli-backend`（スクリプト: `scripts/test-live-cli-backend-docker.sh`）
- Gateway + dev agent: `pnpm test:docker:live-gateway`（スクリプト: `scripts/test-live-gateway-models-docker.sh`）
- Open WebUI liveスモーク: `pnpm test:docker:openwebui`（スクリプト: `scripts/e2e/openwebui-docker.sh`）
- オンボーディングウィザード（TTY、完全なscaffolding）: `pnpm test:docker:onboard`（スクリプト: `scripts/e2e/onboard-docker.sh`）
- Gatewayネットワーキング（2コンテナ、WS auth + health）: `pnpm test:docker:gateway-network`（スクリプト: `scripts/e2e/gateway-network-docker.sh`）
- MCPチャンネルbridge（seed済みGateway + stdio bridge + raw Claude notification-frameスモーク）: `pnpm test:docker:mcp-channels`（スクリプト: `scripts/e2e/mcp-channels-docker.sh`）
- Plugins（インストールスモーク + `/plugin`エイリアス + Claudeバンドル再起動セマンティクス）: `pnpm test:docker:plugins`（スクリプト: `scripts/e2e/plugins-docker.sh`）

live-model Dockerランナーはまた、現在のチェックアウトを読み取り専用でbind mountし、
コンテナ内の一時workdirへステージします。これにより、ランタイム
イメージを軽量に保ちつつ、正確にローカルのソース/設定に対してVitestを実行できます。
ステージング手順では、`.pnpm-store`, `.worktrees`, `__openclaw_vitest__`, および
アプリローカルの`.build`またはGradle出力ディレクトリのような、大きなローカル専用キャッシュやアプリビルド出力をスキップするため、
Docker live実行でマシン固有のアーティファクトをコピーするのに何分も費やすことがありません。
また、`OPENCLAW_SKIP_CHANNELS=1`も設定するため、Gateway live probeが
コンテナ内で実際のTelegram/Discordなどのチャンネルworkerを起動しません。
`test:docker:live-models`は依然として`pnpm test:live`を実行するため、
そのDockerレーンからGateway
liveカバレッジを絞り込んだり除外したりする必要がある場合は、`OPENCLAW_LIVE_GATEWAY_*`も渡してください。
`test:docker:openwebui`は、より高レベルな互換性スモークです: OpenAI互換HTTPエンドポイントを有効にした
OpenClaw Gatewayコンテナを起動し、そのGatewayに対して固定版Open WebUIコンテナを起動し、Open WebUI経由でサインインし、
`/api/models`が`openclaw/default`を公開していることを確認してから、
Open WebUIの`/api/chat/completions`プロキシ経由で実際のチャットリクエストを送信します。
初回実行は、Dockerが
Open WebUIイメージをpullする必要があったり、Open WebUI自体のコールドスタートセットアップ完了が必要だったりするため、目に見えて遅くなる場合があります。
このレーンは使用可能なliveモデルキーを前提としており、Docker化された実行でそれを提供する主な方法は
`OPENCLAW_PROFILE_FILE`
（デフォルトで`~/.profile`）です。
成功した実行では、`{ "ok": true, "model":
"openclaw/default", ... }`のような小さなJSONペイロードが出力されます。
`test:docker:mcp-channels`は意図的に決定的であり、実際の
Telegram、Discord、iMessageアカウントを必要としません。これはseed済みGateway
コンテナを起動し、`openclaw mcp serve`を起動する第2コンテナを開始してから、
ルーティングされた会話検出、transcript読み取り、添付メタデータ、
liveイベントキュー動作、送信ルーティング、およびClaude風チャンネル +
権限通知を、実際のstdio MCP bridge上で検証します。通知チェックは
raw stdio MCPフレームを直接検査するため、このスモークは
特定のクライアントSDKがたまたま表面化するものだけでなく、bridgeが実際に出力する内容を検証します。

手動ACP平易言語スレッドスモーク（CIではない）:

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- このスクリプトはリグレッション/デバッグワークフロー用に維持してください。ACPスレッドルーティング検証で再び必要になる可能性があるため、削除しないでください。

便利な環境変数:

- `OPENCLAW_CONFIG_DIR=...`（デフォルト: `~/.openclaw`）を`/home/node/.openclaw`へマウント
- `OPENCLAW_WORKSPACE_DIR=...`（デフォルト: `~/.openclaw/workspace`）を`/home/node/.openclaw/workspace`へマウント
- `OPENCLAW_PROFILE_FILE=...`（デフォルト: `~/.profile`）を`/home/node/.profile`へマウントし、テスト実行前にsourceする
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）を`/home/node/.npm-global`へマウントし、Docker内でCLIインストールをキャッシュする
- `$HOME`配下の外部CLI認証ディレクトリ/ファイルは、`/host-auth...`配下に読み取り専用でマウントされ、その後テスト開始前に`/home/node/...`へコピーされます
  - デフォルトディレクトリ: `.minimax`
  - デフォルトファイル: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - 絞り込まれたプロバイダー実行では、`OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`から推定された必要なディレクトリ/ファイルのみをマウントします
  - 手動で上書きするには`OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`、または`OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`のようなカンマ区切りリストを使用
- 実行を絞り込むには`OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- コンテナ内でプロバイダーをフィルタするには`OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- 資格情報がプロファイルストア由来であることを保証するには`OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`（envではない）
- Open WebUIスモーク向けにGatewayが公開するモデルを選ぶには`OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUIスモークで使うnonceチェックプロンプトを上書きするには`OPENCLAW_OPENWEBUI_PROMPT=...`
- 固定されたOpen WebUIイメージタグを上書きするには`OPENWEBUI_IMAGE=...`

## ドキュメント健全性

ドキュメント編集後にドキュメントチェックを実行: `pnpm check:docs`。
ページ内見出しチェックも必要な場合は、完全なMintlifyアンカー検証を実行: `pnpm docs:check-links:anchors`。

## オフラインリグレッション（CI安全）

これらは、実際のプロバイダーなしでの「実際のパイプライン」リグレッションです:

- Gateway tool calling（mock OpenAI、実際のGateway + エージェントループ）: `src/gateway/gateway.test.ts`（ケース: "runs a mock OpenAI tool call end-to-end via gateway agent loop"）
- Gatewayウィザード（WS `wizard.start`/`wizard.next`、設定書き込み + 認証強制）: `src/gateway/gateway.test.ts`（ケース: "runs wizard over ws and writes auth token config"）

## エージェント信頼性eval（Skills）

すでにいくつかのCI安全なテストがあり、「エージェント信頼性eval」のように機能します:

- 実際のGateway + エージェントループを通したmock tool-calling（`src/gateway/gateway.test.ts`）。
- セッション配線と設定効果を検証するエンドツーエンドのウィザードフロー（`src/gateway/gateway.test.ts`）。

Skills向けにまだ不足しているもの（[Skills](/ja-JP/tools/skills)を参照）:

- **Decisioning:** スキルがプロンプトに列挙されたとき、エージェントは正しいスキルを選ぶか（または無関係なものを避けるか）？
- **Compliance:** エージェントは使用前に`SKILL.md`を読み、必要な手順/引数に従うか？
- **Workflow contracts:** ツール順序、セッション履歴の持ち越し、sandbox境界を検証するマルチターンシナリオ。

今後のevalは、まず決定的であるべきです:

- mockプロバイダーを使って、ツール呼び出し + 順序、スキルファイル読み取り、セッション配線を検証するシナリオランナー。
- スキルに焦点を当てた小さなシナリオスイート（使う vs 避ける、ゲーティング、プロンプトインジェクション）。
- オプションのlive eval（オプトイン、envゲート）は、CI安全なスイートが整ってからにすること。

## 契約テスト（プラグインとチャンネルの形状）

契約テストは、登録されたすべてのプラグインとチャンネルがその
インターフェース契約に準拠していることを検証します。検出されたすべてのプラグインを反復し、
形状と動作に関する一連のアサーションを実行します。デフォルトの`pnpm test` unitレーンは、
これらの共有seamとスモークファイルを意図的にスキップします。共有チャンネルまたはプロバイダーサーフェスに触れた場合は、
契約コマンドを明示的に実行してください。

### コマンド

- すべての契約: `pnpm test:contracts`
- チャンネル契約のみ: `pnpm test:contracts:channels`
- プロバイダー契約のみ: `pnpm test:contracts:plugins`

### チャンネル契約

`src/channels/plugins/contracts/*.contract.test.ts`にあります:

- **plugin** - 基本的なプラグイン形状（id、name、capabilities）
- **setup** - セットアップウィザード契約
- **session-binding** - セッションbind動作
- **outbound-payload** - メッセージpayload構造
- **inbound** - 受信メッセージ処理
- **actions** - チャンネルアクションハンドラー
- **threading** - スレッドID処理
- **directory** - ディレクトリ/roster API
- **group-policy** - グループポリシー強制

### プロバイダーステータス契約

`src/plugins/contracts/*.contract.test.ts`にあります。

- **status** - チャンネルステータスprobe
- **registry** - プラグインレジストリ形状

### プロバイダー契約

`src/plugins/contracts/*.contract.test.ts`にあります:

- **auth** - 認証フロー契約
- **auth-choice** - 認証の選択/選定
- **catalog** - モデルカタログAPI
- **discovery** - プラグイン検出
- **loader** - プラグイン読み込み
- **runtime** - プロバイダーランタイム
- **shape** - プラグイン形状/インターフェース
- **wizard** - セットアップウィザード

### 実行するタイミング

- plugin-sdkのexportまたはsubpathを変更した後
- チャンネルまたはプロバイダープラグインを追加または変更した後
- プラグイン登録または検出をリファクタリングした後

契約テストはCIで実行され、実際のAPIキーは不要です。

## リグレッションの追加（ガイダンス）

liveで発見されたプロバイダー/モデル問題を修正したときは:

- 可能であればCI安全なリグレッションを追加してください（mock/stubプロバイダー、または正確なリクエスト形状変換をキャプチャ）
- 本質的にlive専用である場合（レート制限、認証ポリシー）は、liveテストを狭く保ち、env変数経由のオプトインにしてください
- バグを捕まえる最小のレイヤーを狙うようにしてください:
  - プロバイダーのリクエスト変換/replayバグ → direct modelsテスト
  - Gatewayセッション/履歴/ツールパイプラインのバグ → Gateway liveスモークまたはCI安全なGateway mockテスト
- SecretRef traversalガードレール:
  - `src/secrets/exec-secret-ref-id-parity.test.ts`は、レジストリメタデータ（`listSecretTargetRegistryEntries()`）からSecretRefクラスごとに1つのサンプル対象を導出し、その後traversal-segment exec idが拒否されることを検証します。
  - `src/secrets/target-registry-data.ts`に新しい`includeInPlan` SecretRef対象ファミリーを追加する場合は、そのテスト内の`classifyTargetClass`を更新してください。このテストは、分類されていない対象idがあると意図的に失敗するため、新しいクラスが黙ってスキップされることはありません。
