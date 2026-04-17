---
read_when:
    - ローカルまたはCIでテストを実行する
    - モデル/プロバイダーのバグに対するリグレッションを追加する
    - Gateway + エージェントの動作をデバッグする
summary: テストキット：unit/e2e/liveスイート、Dockerランナー、および各テストがカバーする内容
title: テスト
x-i18n:
    generated_at: "2026-04-17T04:44:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 55483bc68d3b24daca3189fba3af1e896f39b8e83068d102fed06eac05b36102
    source_path: help/testing.md
    workflow: 15
---

# テスト

OpenClawには3つのVitestスイート（unit/integration、e2e、live）と、少数のDockerランナーがあります。

このドキュメントは「どのようにテストするか」のガイドです。

- 各スイートが何をカバーするか（および意図的に何をカバーしないか）
- 一般的なワークフロー（ローカル、push前、デバッグ）でどのコマンドを実行するか
- liveテストがどのように認証情報を見つけ、モデル/プロバイダーを選択するか
- 実際のモデル/プロバイダーの問題に対するリグレッションをどのように追加するか

## クイックスタート

ほとんどの日は以下です。

- フルゲート（push前に期待されるもの）: `pnpm build && pnpm check && pnpm test`
- 余裕のあるマシンでの、より高速なローカル全スイート実行: `pnpm test:max`
- 直接のVitest watchループ: `pnpm test:watch`
- 直接のファイル指定は、extension/channelパスもルーティングされるようになりました: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- 単一の失敗を反復修正しているときは、まず対象を絞った実行を優先してください。
- DockerベースのQAサイト: `pnpm qa:lab:up`
- Linux VMベースのQAレーン: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

テストに触れたとき、または追加の確信がほしいとき:

- カバレッジゲート: `pnpm test:coverage`
- E2Eスイート: `pnpm test:e2e`

実際のプロバイダー/モデルをデバッグするとき（実際の認証情報が必要）:

- liveスイート（models + Gateway tool/image probes）: `pnpm test:live`
- 1つのliveファイルを静かに対象指定: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

ヒント: 必要なのが1つの失敗ケースだけなら、以下で説明するallowlist環境変数を使ってliveテストを絞り込むことを優先してください。

## QA固有のランナー

これらのコマンドは、QA-lab相当の現実性が必要なときに、メインのテストスイートと並んで使います。

- `pnpm openclaw qa suite`
  - リポジトリベースのQAシナリオをホスト上で直接実行します。
  - デフォルトで、分離されたGatewayワーカーを使って複数の選択シナリオを並列実行します。最大64ワーカー、または選択したシナリオ数までです。`--concurrency <count>`でワーカー数を調整するか、従来の直列レーンには`--concurrency 1`を使ってください。
  - プロバイダーモード `live-frontier`、`mock-openai`、`aimock` をサポートします。`aimock` は、シナリオ認識型の `mock-openai` レーンを置き換えることなく、実験的なfixtureおよびプロトコルモックのカバレッジ向けに、ローカルのAIMockベースのプロバイダーサーバーを起動します。
- `pnpm openclaw qa suite --runner multipass`
  - 同じQAスイートを、使い捨てのMultipass Linux VM内で実行します。
  - ホスト上の `qa suite` と同じシナリオ選択動作を維持します。
  - `qa suite` と同じプロバイダー/モデル選択フラグを再利用します。
  - live実行では、ゲストで実用的なサポート済みQA認証入力を転送します: 環境変数ベースのプロバイダーキー、QA liveプロバイダー設定パス、存在する場合は `CODEX_HOME`。
  - 出力ディレクトリは、ゲストがマウントされたワークスペース経由で書き戻せるよう、リポジトリルート配下に維持する必要があります。
  - 通常のQAレポートとサマリーに加え、Multipassログを `.artifacts/qa-e2e/...` 配下に書き込みます。
- `pnpm qa:lab:up`
  - オペレーター型のQA作業向けに、DockerベースのQAサイトを起動します。
- `pnpm openclaw qa aimock`
  - 直接のプロトコルスモークテスト用に、ローカルのAIMockプロバイダーサーバーのみを起動します。
- `pnpm openclaw qa matrix`
  - 使い捨てのDockerベースTuwunelホームサーバーに対して、Matrix live QAレーンを実行します。
  - このQAホストは現時点ではrepo/dev専用です。パッケージ化されたOpenClawインストールには `qa-lab` は含まれないため、`openclaw qa` は公開されません。
  - リポジトリチェックアウトはバンドルされたランナーを直接読み込みます。別途Pluginインストール手順は不要です。
  - 3つの一時的なMatrixユーザー（`driver`、`sut`、`observer`）と1つのプライベートルームをプロビジョニングし、その後、実際のMatrix PluginをSUTトランスポートとして使うQA Gateway子プロセスを起動します。
  - デフォルトでは、固定された安定版Tuwunelイメージ `ghcr.io/matrix-construct/tuwunel:v1.5.1` を使います。別のイメージをテストする必要がある場合は `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` で上書きしてください。
  - Matrixは共有認証情報ソースフラグを公開しません。これは、このレーンが使い捨てユーザーをローカルでプロビジョニングするためです。
  - Matrix QAレポート、サマリー、observed-events artifact、結合されたstdout/stderr出力ログを `.artifacts/qa-e2e/...` 配下に書き込みます。
- `pnpm openclaw qa telegram`
  - 環境変数から取得したdriverおよびSUT botトークンを使って、実際のプライベートグループに対してTelegram live QAレーンを実行します。
  - `OPENCLAW_QA_TELEGRAM_GROUP_ID`、`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`、`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` が必要です。グループIDは数値のTelegram chat idでなければなりません。
  - 共有プール認証情報用に `--credential-source convex` をサポートします。デフォルトではenvモードを使い、プールされたリースを使うには `OPENCLAW_QA_CREDENTIAL_SOURCE=convex` を設定してください。
  - 同じプライベートグループ内に2つの異なるbotが必要で、SUT botはTelegram usernameを公開している必要があります。
  - 安定したbot間観測のために、`@BotFather` で両方のbotのBot-to-Bot Communication Modeを有効にし、driver botがグループ内のbotトラフィックを観測できることを確認してください。
  - Telegram QAレポート、サマリー、およびobserved-messages artifactを `.artifacts/qa-e2e/...` 配下に書き込みます。

live transportレーンは、新しいtransportがずれないよう、1つの標準契約を共有します。

`qa-channel` は依然として広範な合成QAスイートであり、live transportカバレッジマトリクスには含まれません。

| レーン | Canary | Mention gating | Allowlist block | Top-level reply | Restart resume | Thread follow-up | Thread isolation | Reaction observation | Help command |
| -------- | ------ | -------------- | --------------- | --------------- | -------------- | ---------------- | ---------------- | -------------------- | ------------ |
| Matrix   | x      | x              | x               | x               | x              | x                | x                | x                    |              |
| Telegram | x      |                |                 |                 |                |                  |                  |                      | x            |

### Convex経由の共有Telegram認証情報（v1）

`openclaw qa telegram` で `--credential-source convex`（または `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`）を有効にすると、QA labはConvexベースのプールから排他的リースを取得し、レーンの実行中はそのリースにHeartbeatを送り続け、シャットダウン時にリースを解放します。

参考用Convexプロジェクトスキャフォールド:

- `qa/convex-credential-broker/`

必要な環境変数:

- `OPENCLAW_QA_CONVEX_SITE_URL`（例: `https://your-deployment.convex.site`）
- 選択したロール用のシークレット1つ:
  - `maintainer` 用の `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER`
  - `ci` 用の `OPENCLAW_QA_CONVEX_SECRET_CI`
- 認証情報ロール選択:
  - CLI: `--credential-role maintainer|ci`
  - 環境変数デフォルト: `OPENCLAW_QA_CREDENTIAL_ROLE`（デフォルトは `maintainer`）

任意の環境変数:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS`（デフォルト `1200000`）
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS`（デフォルト `30000`）
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS`（デフォルト `90000`）
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS`（デフォルト `15000`）
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX`（デフォルト `/qa-credentials/v1`）
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID`（任意のトレースID）
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` は、ローカル専用開発向けにloopbackの `http://` Convex URLを許可します。

通常運用では `OPENCLAW_QA_CONVEX_SITE_URL` は `https://` を使う必要があります。

maintainer管理コマンド（プールの追加/削除/一覧表示）には、特に `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` が必要です。

maintainer向けCLIヘルパー:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

スクリプトおよびCIユーティリティで機械可読な出力が必要な場合は `--json` を使ってください。

デフォルトのエンドポイント契約（`OPENCLAW_QA_CONVEX_SITE_URL` + `/qa-credentials/v1`）:

- `POST /acquire`
  - リクエスト: `{ kind, ownerId, actorRole, leaseTtlMs, heartbeatIntervalMs }`
  - 成功: `{ status: "ok", credentialId, leaseToken, payload, leaseTtlMs?, heartbeatIntervalMs? }`
  - 枯渇/再試行可能: `{ status: "error", code: "POOL_EXHAUSTED" | "NO_CREDENTIAL_AVAILABLE", ... }`
- `POST /heartbeat`
  - リクエスト: `{ kind, ownerId, actorRole, credentialId, leaseToken, leaseTtlMs }`
  - 成功: `{ status: "ok" }`（または空の `2xx`）
- `POST /release`
  - リクエスト: `{ kind, ownerId, actorRole, credentialId, leaseToken }`
  - 成功: `{ status: "ok" }`（または空の `2xx`）
- `POST /admin/add`（maintainerシークレット専用）
  - リクエスト: `{ kind, actorId, payload, note?, status? }`
  - 成功: `{ status: "ok", credential }`
- `POST /admin/remove`（maintainerシークレット専用）
  - リクエスト: `{ credentialId, actorId }`
  - 成功: `{ status: "ok", changed, credential }`
  - アクティブリースガード: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list`（maintainerシークレット専用）
  - リクエスト: `{ kind?, status?, includePayload?, limit? }`
  - 成功: `{ status: "ok", credentials, count }`

Telegram種別のpayload形状:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` は数値のTelegram chat id文字列でなければなりません。
- `admin/add` は `kind: "telegram"` に対してこの形状を検証し、不正なpayloadを拒否します。

### QAにチャネルを追加する

markdown QAシステムにチャネルを追加するには、正確に2つのものが必要です。

1. そのチャネル用のtransport adapter
2. チャネル契約を実行するscenario pack

共有の `qa-lab` ホストがフローを所有できる場合、新しいトップレベルQAコマンドルートを追加しないでください。

`qa-lab` は共有ホストメカニクスを所有します。

- `openclaw qa` コマンドルート
- スイートの起動と終了処理
- ワーカー並行性
- artifactの書き込み
- レポート生成
- シナリオ実行
- 古い `qa-channel` シナリオ向けの互換エイリアス

Runner Pluginはtransport契約を所有します。

- `openclaw qa <runner>` が共有の `qa` ルート配下にどのようにマウントされるか
- そのtransport向けにGatewayがどのように設定されるか
- 準備完了をどのように確認するか
- inboundイベントをどのように注入するか
- outboundメッセージをどのように観測するか
- transcriptおよび正規化されたtransport状態をどのように公開するか
- transportベースのアクションをどのように実行するか
- transport固有のリセットまたはクリーンアップをどのように処理するか

新しいチャネルの最低採用基準は以下です。

1. 共有 `qa` ルートの所有者は `qa-lab` のままにする。
2. 共有 `qa-lab` ホストシーム上にtransport runnerを実装する。
3. transport固有のメカニクスはrunner Pluginまたはチャネルharness内に保持する。
4. 競合するルートコマンドを登録するのではなく、runnerを `openclaw qa <runner>` としてマウントする。  
   Runner Pluginは `openclaw.plugin.json` に `qaRunners` を宣言し、`runtime-api.ts` から一致する `qaRunnerCliRegistrations` 配列をエクスポートする必要があります。  
   `runtime-api.ts` は軽量に保ってください。遅延CLIおよびrunner実行は、別のentrypointの背後に置く必要があります。
5. `qa/scenarios/` 配下にmarkdownシナリオを作成または調整する。
6. 新しいシナリオには汎用シナリオヘルパーを使う。
7. リポジトリが意図的な移行を行っているのでない限り、既存の互換エイリアスを動作させ続ける。

判断ルールは厳格です。

- 振る舞いを `qa-lab` で一度だけ表現できるなら、`qa-lab` に置く。
- 振る舞いが1つのチャネルtransportに依存するなら、そのrunner PluginまたはPlugin harnessに保持する。
- シナリオが複数のチャネルで使える新しい機能を必要とするなら、`suite.ts` にチャネル固有の分岐を追加するのではなく、汎用ヘルパーを追加する。
- 振る舞いが1つのtransportにのみ意味を持つなら、そのシナリオはtransport固有のままにし、シナリオ契約内でそれを明示する。

新しいシナリオ向けの推奨汎用ヘルパー名は以下です。

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

既存シナリオ向けには、以下を含む互換エイリアスが引き続き利用できます。

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

新しいチャネル作業では、汎用ヘルパー名を使う必要があります。  
互換エイリアスは、一斉移行を避けるために存在するのであって、新しいシナリオ作成のモデルではありません。

## テストスイート（どこで何が動くか）

スイートは「現実性が増す順」（そして不安定さ/コストも増す順）と考えてください:

### Unit / integration（デフォルト）

- コマンド: `pnpm test`
- 設定: 既存のスコープ付きVitest projectに対する10個の逐次shard実行（`vitest.full-*.config.ts`）
- ファイル: `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 配下のcore/unitインベントリ、および `vitest.unit.config.ts` でカバーされる許可済みの `ui` nodeテスト
- スコープ:
  - 純粋なunitテスト
  - プロセス内integrationテスト（Gateway auth、routing、tooling、parsing、config）
  - 既知のバグに対する決定論的なリグレッション
- 想定:
  - CIで実行される
  - 実際のキーは不要
  - 高速で安定しているべき
- projectに関する注記:
  - 対象指定なしの `pnpm test` は、1つの巨大なネイティブルートprojectプロセスの代わりに、11個のより小さなshard設定（`core-unit-src`、`core-unit-security`、`core-unit-ui`、`core-unit-support`、`core-support-boundary`、`core-contracts`、`core-bundled`、`core-runtime`、`agentic`、`auto-reply`、`extensions`）を実行するようになりました。これにより、負荷の高いマシンでのピークRSSを削減し、auto-reply/extension作業が無関係なスイートを圧迫するのを防ぎます。
  - `pnpm test --watch` は引き続きネイティブルートの `vitest.config.ts` project graphを使います。複数shardのwatchループは現実的でないためです。
  - `pnpm test`、`pnpm test:watch`、`pnpm test:perf:imports` は、明示的なファイル/ディレクトリ指定をまずスコープ付きレーン経由でルーティングするため、`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` はフルルートproject起動のコストを回避できます。
  - `pnpm test:changed` は、変更差分がルーティング可能なsource/testファイルだけに触れている場合、変更されたgitパスを同じスコープ付きレーンに展開します。config/setup編集は引き続き広範なルートproject再実行にフォールバックします。
  - agents、commands、plugins、auto-reply helper、`plugin-sdk`、および同様の純粋なutility領域のimport軽量なunitテストは、`test/setup-openclaw-runtime.ts` をスキップする `unit-fast` レーンを経由します。stateful/runtime-heavyなファイルは既存レーンに残ります。
  - 選択された `plugin-sdk` および `commands` helper sourceファイルも、changed-mode実行をそれらの軽量レーン内の明示的な隣接テストにマッピングするため、helper編集でそのディレクトリのフルheavyスイートを再実行せずに済みます。
  - `auto-reply` には現在、3つの専用バケットがあります: トップレベルのcore helper、トップレベルの `reply.*` integrationテスト、および `src/auto-reply/reply/**` サブツリーです。これにより、最も重いreply harness作業が、軽量なstatus/chunk/tokenテストに乗らないようにします。
- embedded runnerに関する注記:
  - メッセージtool discovery入力またはCompaction runtime contextを変更するときは、両方のレベルのカバレッジを維持してください。
  - 純粋なrouting/normalization境界に対する、焦点を絞ったhelperリグレッションを追加してください。
  - さらに、embedded runner integrationスイートも健全に保ってください:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`、および
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - これらのスイートは、スコープ付きidとCompactionの挙動が依然として実際の `run.ts` / `compact.ts` パスを通って流れることを検証します。helperのみのテストは、これらのintegrationパスの十分な代替にはなりません。
- poolに関する注記:
  - ベースのVitest設定は現在デフォルトで `threads` です。
  - 共有Vitest設定では、`isolate: false` も固定され、root projects、e2e、live設定全体で非分離runnerを使います。
  - ルートUIレーンはその `jsdom` setupとoptimizerを維持していますが、現在は共有の非分離runnerでも実行されます。
  - 各 `pnpm test` shardは、共有Vitest設定から同じ `threads` + `isolate: false` のデフォルトを継承します。
  - 共有の `scripts/run-vitest.mjs` launcherは現在、Vitestの子Nodeプロセスに対してデフォルトで `--no-maglev` も追加し、大規模なローカル実行中のV8 compile churnを減らします。標準のV8挙動と比較したい場合は `OPENCLAW_VITEST_ENABLE_MAGLEV=1` を設定してください。
- 高速なローカル反復に関する注記:
  - `pnpm test:changed` は、変更パスがより小さなスイートにきれいにマップされるとき、スコープ付きレーン経由でルーティングします。
  - `pnpm test:max` と `pnpm test:changed:max` は同じルーティング挙動を維持しつつ、worker上限だけを高くします。
  - ローカルworkerの自動スケーリングは現在意図的に保守的で、ホストのload averageがすでに高い場合にもバックオフするため、複数の同時Vitest実行がデフォルトで与える悪影響を減らします。
  - ベースのVitest設定は、テスト配線が変わったときにchanged-mode再実行の正しさを保つため、projects/configファイルを `forceRerunTriggers` としてマークします。
  - この設定は、サポート対象ホストで `OPENCLAW_VITEST_FS_MODULE_CACHE` を有効に保ちます。直接プロファイリング用に明示的なキャッシュ場所を1つ使いたい場合は `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` を設定してください。
- perf-debugに関する注記:
  - `pnpm test:perf:imports` はVitestのimport-durationレポートとimport-breakdown出力を有効にします。
  - `pnpm test:perf:imports:changed` は、同じプロファイリング表示を `origin/main` 以降に変更されたファイルに限定します。
- `pnpm test:perf:changed:bench -- --ref <git-ref>` は、そのコミット済み差分に対するルーティング済み `test:changed` とネイティブルートprojectパスを比較し、wall timeとmacOS max RSSを表示します。
- `pnpm test:perf:changed:bench -- --worktree` は、変更済みファイル一覧を `scripts/test-projects.mjs` とルートVitest設定経由でルーティングすることで、現在のdirty treeをベンチマークします。
  - `pnpm test:perf:profile:main` は、Vitest/Viteの起動とtransform overhead向けのmain-thread CPU profileを書き出します。
  - `pnpm test:perf:profile:runner` は、ファイル並列性を無効にしたunitスイート向けのrunner CPU+heap profileを書き出します。

### E2E（Gatewayスモーク）

- コマンド: `pnpm test:e2e`
- 設定: `vitest.e2e.config.ts`
- ファイル: `src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- ランタイムデフォルト:
  - リポジトリの他の部分に合わせて、Vitest `threads` と `isolate: false` を使います。
  - 適応型workerを使います（CI: 最大2、ローカル: デフォルトで1）。
  - コンソールI/O overheadを減らすため、デフォルトでsilent modeで実行します。
- 便利な上書き:
  - worker数を強制する `OPENCLAW_E2E_WORKERS=<n>`（上限16）
  - 詳細なコンソール出力を再度有効にする `OPENCLAW_E2E_VERBOSE=1`
- スコープ:
  - 複数インスタンスのGateway end-to-end挙動
  - WebSocket/HTTP surface、Node pairing、およびより重いネットワーキング
- 想定:
  - CIで実行される（パイプラインで有効な場合）
  - 実際のキーは不要
  - unitテストより可動部分が多い（遅くなることがある）

### E2E: OpenShell backendスモーク

- コマンド: `pnpm test:e2e:openshell`
- ファイル: `test/openshell-sandbox.e2e.test.ts`
- スコープ:
  - Docker経由でホスト上に分離されたOpenShell Gatewayを起動する
  - 一時的なローカルDockerfileからsandboxを作成する
  - 実際の `sandbox ssh-config` + SSH execを介してOpenClawのOpenShell backendを実行する
  - sandbox fs bridgeを通じてremote-canonical filesystem挙動を検証する
- 想定:
  - オプトイン専用。デフォルトの `pnpm test:e2e` 実行には含まれない
  - ローカルの `openshell` CLIと動作するDocker daemonが必要
  - 分離された `HOME` / `XDG_CONFIG_HOME` を使い、その後テストGatewayとsandboxを破棄する
- 便利な上書き:
  - より広いe2eスイートを手動実行するときにテストを有効化する `OPENCLAW_E2E_OPENSHELL=1`
  - デフォルト以外のCLI binaryまたはwrapper scriptを指す `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live（実際のプロバイダー + 実際のモデル）

- コマンド: `pnpm test:live`
- 設定: `vitest.live.config.ts`
- ファイル: `src/**/*.live.test.ts`
- デフォルト: `pnpm test:live` により **有効**（`OPENCLAW_LIVE_TEST=1` を設定）
- スコープ:
  - 「このプロバイダー/モデルは、実際の認証情報で _今日_ 本当に動くか？」
  - プロバイダーのフォーマット変更、tool-callingの癖、authの問題、rate limit挙動を検出する
- 想定:
  - 設計上CIで安定しない（実ネットワーク、実プロバイダーポリシー、quota、障害）
  - コストがかかる / rate limitを消費する
  - 「全部」よりも、絞り込んだサブセットを実行するのを優先する
- live実行は、欠けているAPIキーを取得するために `~/.profile` をsourceします。
- デフォルトでは、live実行は依然として `HOME` を分離し、config/auth materialを一時テストホームにコピーします。これにより、unit fixtureが実際の `~/.openclaw` を変更できないようにします。
- liveテストで実際のhomeディレクトリを意図的に使う必要がある場合にのみ、`OPENCLAW_LIVE_USE_REAL_HOME=1` を設定してください。
- `pnpm test:live` は現在、より静かなモードがデフォルトです。`[live] ...` の進捗出力は維持しますが、追加の `~/.profile` 通知を抑制し、Gateway bootstrapログ/Bonjour chatterをミュートします。完全な起動ログを再び見たい場合は `OPENCLAW_LIVE_TEST_QUIET=0` を設定してください。
- APIキーのローテーション（プロバイダー固有）: カンマ/セミコロン形式の `*_API_KEYS` または `*_API_KEY_1`、`*_API_KEY_2`（例: `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`）を設定するか、live専用上書きとして `OPENCLAW_LIVE_*_KEY` を使ってください。テストはrate limit応答時に再試行します。
- 進捗/Heartbeat出力:
  - liveスイートは現在、長いプロバイダー呼び出しがVitestのコンソールキャプチャが静かなときでも活動中であることが見えるよう、進捗行をstderrに出力します。
  - `vitest.live.config.ts` はVitestのコンソールインターセプトを無効にしているため、プロバイダー/Gatewayの進捗行はlive実行中に即時ストリームされます。
  - 直接モデルのHeartbeatは `OPENCLAW_LIVE_HEARTBEAT_MS` で調整します。
  - Gateway/probeのHeartbeatは `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` で調整します。

## どのスイートを実行すべきか？

この判断表を使ってください。

- ロジック/テストを編集している: `pnpm test` を実行する（大きく変更した場合は `pnpm test:coverage` も）
- Gatewayネットワーキング / WS protocol / pairingに触れる: `pnpm test:e2e` を追加する
- 「botが落ちている」問題 / プロバイダー固有の失敗 / tool callingをデバッグしている: 絞り込んだ `pnpm test:live` を実行する

## Live: Android Node capability sweep

- テスト: `src/gateway/android-node.capabilities.live.test.ts`
- スクリプト: `pnpm android:test:integration`
- 目標: 接続されたAndroid Nodeが現在公開している **すべてのコマンド** を呼び出し、コマンド契約の挙動を検証する。
- スコープ:
  - 前提条件付き/手動セットアップ（このスイートはアプリのインストール/実行/pairingは行いません）。
  - 選択されたAndroid Nodeに対する、コマンドごとのGateway `node.invoke` 検証。
- 必要な事前セットアップ:
  - AndroidアプリがすでにGatewayに接続済みで、pairing済みであること。
  - アプリが前面に維持されていること。
  - 成功を期待するcapabilityに対して、権限/キャプチャ同意が付与されていること。
- 任意のターゲット上書き:
  - `OPENCLAW_ANDROID_NODE_ID` または `OPENCLAW_ANDROID_NODE_NAME`。
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`。
- Androidの完全なセットアップ詳細: [Android App](/ja-JP/platforms/android)

## Live: modelスモーク（profileキー）

liveテストは、失敗を切り分けられるよう2つのレイヤーに分かれています。

- 「Direct model」は、与えられたキーでそのプロバイダー/モデルが少なくとも応答できるかを示します。
- 「Gateway smoke」は、そのモデルに対して完全なGateway+エージェントパイプラインが動作するか（sessions、history、tools、sandbox policyなど）を示します。

### レイヤー1: Direct model completion（Gatewayなし）

- テスト: `src/agents/models.profiles.live.test.ts`
- 目標:
  - 発見されたモデルを列挙する
  - `getApiKeyForModel` を使って、認証情報を持つモデルを選択する
  - モデルごとに小さなcompletionを実行する（必要に応じて対象を絞ったリグレッションも）
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
- このスイートを実際に実行するには `OPENCLAW_LIVE_MODELS=modern`（または `all`、`modern` のエイリアス）を設定してください。そうしないと、`pnpm test:live` をGatewayスモークに集中させるためスキップされます
- モデルの選択方法:
  - `OPENCLAW_LIVE_MODELS=modern` でmodern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）を実行
  - `OPENCLAW_LIVE_MODELS=all` はmodern allowlistのエイリアス
  - または `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（カンマ区切りallowlist）
  - modern/all sweepはデフォルトで厳選された高シグナル上限を使います。網羅的なmodern sweepには `OPENCLAW_LIVE_MAX_MODELS=0`、より小さい上限には正の数を設定してください。
- プロバイダーの選択方法:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（カンマ区切りallowlist）
- キーの取得元:
  - デフォルト: profile storeおよびenv fallback
  - **profile store** のみを強制するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` を設定
- これが存在する理由:
  - 「プロバイダーAPIが壊れている / キーが無効」であることと、「Gatewayエージェントパイプラインが壊れている」ことを分離する
  - 小さく分離されたリグレッションを含める（例: OpenAI Responses/Codex Responsesのreasoning replay + tool-callフロー）

### レイヤー2: Gateway + devエージェントスモーク（`@openclaw` が実際に行うこと）

- テスト: `src/gateway/gateway-models.profiles.live.test.ts`
- 目標:
  - プロセス内Gatewayを起動する
  - `agent:dev:*` sessionを作成/patchする（実行ごとのmodel override）
  - キーを持つモデル群を反復し、以下を検証する:
    - 「意味のある」応答（toolなし）
    - 実際のtool呼び出しが動作すること（read probe）
    - 任意の追加tool probe（exec+read probe）
    - OpenAIのリグレッション経路（tool-call-only → follow-up）が引き続き動作すること
- probeの詳細（失敗をすばやく説明できるように）:
  - `read` probe: テストはworkspaceにnonceファイルを書き込み、エージェントにそれを `read` してnonceを返答でそのまま返すよう求めます。
  - `exec+read` probe: テストはエージェントに `exec` でtempファイルへnonceを書かせ、その後それを `read` で読み戻させます。
  - image probe: テストは生成したPNG（猫 + ランダムコード）を添付し、モデルが `cat <CODE>` を返すことを期待します。
  - 実装参照: `src/gateway/gateway-models.profiles.live.test.ts` と `src/gateway/live-image-probe.ts`。
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
- モデルの選択方法:
  - デフォルト: modern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` はmodern allowlistのエイリアス
  - または `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（またはカンマ区切りリスト）で絞り込む
  - modern/allのGateway sweepはデフォルトで厳選された高シグナル上限を使います。網羅的なmodern sweepには `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0`、より小さな上限には正の数を設定してください。
- プロバイダーの選択方法（「OpenRouterを全部」は避ける）:
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（カンマ区切りallowlist）
- このliveテストではtool + image probeは常に有効です:
  - `read` probe + `exec+read` probe（tool stress）
  - image probeは、モデルがimage input supportを公開している場合に実行されます
  - フロー（高レベル）:
    - テストは「CAT」+ ランダムコードを含む小さなPNGを生成する（`src/gateway/live-image-probe.ts`）
    - それを `agent` の `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 経由で送信する
    - Gatewayは添付を `images[]` に解析する（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - embeddedエージェントはmultimodal user messageをモデルへ転送する
    - 検証: 返答に `cat` + そのコードが含まれること（OCR許容: 軽微な誤りは許容）

ヒント: 自分のマシンで何をテストできるか（および正確な `provider/model` id）を確認するには、以下を実行してください。

```bash
openclaw models list
openclaw models list --json
```

## Live: CLI backendスモーク（Claude、Codex、Gemini、またはその他のローカルCLI）

- テスト: `src/gateway/gateway-cli-backend.live.test.ts`
- 目標: デフォルトconfigに触れずに、ローカルCLI backendを使ってGateway + エージェントパイプラインを検証する。
- backend固有のスモークデフォルトは、所有extensionの `cli-backend.ts` 定義にあります。
- 有効化:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- デフォルト:
  - デフォルトのprovider/model: `claude-cli/claude-sonnet-4-6`
  - command/args/imageの挙動は、所有CLI backend Plugin metadataから取得されます。
- 上書き（任意）:
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - 実際のimage attachmentを送るには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`（パスはpromptに注入されます）。
  - prompt注入の代わりにimage file pathをCLI argsとして渡すには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`。
  - `IMAGE_ARG` が設定されているときにimage argsの渡し方を制御するには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（または `"list"`）。
  - 2回目のターンを送ってresumeフローを検証するには `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`。
  - デフォルトのClaude Sonnet -> Opus同一session継続probeを無効にするには `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0`（選択したmodelがswitch targetをサポートしているときに強制的に有効化するには `1` を設定）。

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

単一プロバイダーのDockerレシピ:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

注記:

- Dockerランナーは `scripts/test-live-cli-backend-docker.sh` にあります。
- これはリポジトリのDocker image内で、非rootの `node` userとしてlive CLI-backendスモークを実行します。
- 所有extensionからCLI smoke metadataを解決し、その後、一致するLinux CLI package（`@anthropic-ai/claude-code`、`@openai/codex`、または `@google/gemini-cli`）を、キャッシュ可能で書き込み可能なprefix `OPENCLAW_DOCKER_CLI_TOOLS_DIR`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）にインストールします。
- `pnpm test:docker:live-cli-backend:claude-subscription` は、`~/.claude/.credentials.json` 内の `claudeAiOauth.subscriptionType`、または `claude setup-token` の `CLAUDE_CODE_OAUTH_TOKEN` を使ったポータブルなClaude Code subscription OAuthを必要とします。これはまずDocker内で直接 `claude -p` を検証し、その後Anthropic APIキー環境変数を保持せずに、2回のGateway CLI-backendターンを実行します。このsubscriptionレーンでは、Claudeが現在サードパーティapp利用を通常のsubscriptionプラン上限ではなく追加利用課金経由で扱うため、ClaudeのMCP/toolおよびimage probeはデフォルトで無効です。
- live CLI-backendスモークは現在、Claude、Codex、Geminiに対して同じend-to-endフローを実行します: text turn、image classification turn、その後Gateway CLI経由で検証されるMCP `cron` tool call。
- Claudeのデフォルトスモークは、sessionをSonnetからOpusへpatchし、再開したsessionが以前のメモをまだ覚えていることも検証します。

## Live: ACP bindスモーク（`/acp spawn ... --bind here`）

- テスト: `src/gateway/gateway-acp-bind.live.test.ts`
- 目標: live ACPエージェントで実際のACP conversation-bindフローを検証する:
  - `/acp spawn <agent> --bind here` を送る
  - syntheticなmessage-channel conversationをその場でbindする
  - 同じconversationで通常のfollow-upを送る
  - そのfollow-upがbind済みACP session transcriptに到達することを検証する
- 有効化:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- デフォルト:
  - Docker内のACPエージェント: `claude,codex,gemini`
  - 直接 `pnpm test:live ...` 用のACPエージェント: `claude`
  - synthetic channel: Slack DM風conversation context
  - ACP backend: `acpx`
- 上書き:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 注記:
  - このレーンはGatewayの `chat.send` surfaceを使い、admin専用のsyntheticなoriginating-route fieldで、外部配信を装わずにmessage-channel contextを付与できるようにしています。
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` が未設定の場合、テストは選択したACP harness agentに対して、embedded `acpx` Pluginの組み込みagent registryを使います。

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

単一エージェントのDockerレシピ:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Dockerに関する注記:

- Dockerランナーは `scripts/test-live-acp-bind-docker.sh` にあります。
- デフォルトでは、サポートされているすべてのlive CLIエージェント `claude`、`codex`、`gemini` に対して順にACP bindスモークを実行します。
- マトリクスを絞り込むには、`OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`、`OPENCLAW_LIVE_ACP_BIND_AGENTS=codex`、または `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` を使ってください。
- これは `~/.profile` をsourceし、一致するCLI auth materialをcontainerへステージし、`acpx` を書き込み可能なnpm prefixにインストールし、その後、必要なら要求されたlive CLI（`@anthropic-ai/claude-code`、`@openai/codex`、または `@google/gemini-cli`）をインストールします。
- Docker内では、runnerは `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` を設定し、sourceしたprofile由来のprovider env varsが子harness CLIからも利用できるようにします。

## Live: Codex app-server harnessスモーク

- 目標: 通常のGateway
  `agent` methodを通じて、Plugin所有のCodex harnessを検証する:
  - バンドルされた `codex` Pluginを読み込む
  - `OPENCLAW_AGENT_RUNTIME=codex` を選択する
  - `codex/gpt-5.4` に対して最初のGateway agent turnを送る
  - 同じOpenClaw sessionに2回目のturnを送り、app-server threadがresumeできることを検証する
  - 同じGateway command
    path経由で `/codex status` と `/codex models` を実行する
- テスト: `src/gateway/gateway-codex-harness.live.test.ts`
- 有効化: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- デフォルトmodel: `codex/gpt-5.4`
- 任意のimage probe: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- 任意のMCP/tool probe: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- このスモークは `OPENCLAW_AGENT_HARNESS_FALLBACK=none` を設定するため、壊れたCodex
  harnessがPIへのサイレントfallbackで通過することはありません。
- auth: shell/profileの `OPENAI_API_KEY` と、必要に応じてコピーされる
  `~/.codex/auth.json` および `~/.codex/config.toml`

ローカルレシピ:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Dockerレシピ:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Dockerに関する注記:

- Dockerランナーは `scripts/test-live-codex-harness-docker.sh` にあります。
- これはマウントされた `~/.profile` をsourceし、`OPENAI_API_KEY` を渡し、Codex CLI
  authファイルが存在する場合はそれをコピーし、`@openai/codex` を書き込み可能なマウント済みnpm
  prefixにインストールし、source treeをステージした後、Codex-harness liveテストのみを実行します。
- DockerではimageおよびMCP/tool probeがデフォルトで有効です。より狭いデバッグ実行が必要な場合は、
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` または
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` を設定してください。
- Dockerも `OPENCLAW_AGENT_HARNESS_FALLBACK=none` をエクスポートし、live
  test設定と一致させるため、`openai-codex/*` やPI fallbackがCodex harness
  regressionを隠すことはできません。

### 推奨liveレシピ

狭く明示的なallowlistが最も高速で不安定さも最小です。

- 単一model、direct（Gatewayなし）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 単一model、Gatewayスモーク:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 複数プロバイダーにまたがるtool calling:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google重視（Gemini API key + Antigravity）:
  - Gemini（API key）: `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）: `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注記:

- `google/...` はGemini API（APIキー）を使います。
- `google-antigravity/...` はAntigravity OAuth bridge（Cloud Code Assist風エージェントエンドポイント）を使います。
- `google-gemini-cli/...` はあなたのマシン上のローカルGemini CLIを使います（別個のauth + toolingの癖があります）。
- Gemini APIとGemini CLIの違い:
  - API: OpenClawはGoogleのホストされたGemini APIをHTTP経由で呼び出します（APIキー / profile auth）。これは、ほとんどのユーザーが「Gemini」と言うときに意味しているものです。
  - CLI: OpenClawはローカルの `gemini` binaryをshell outして使います。独自のauthを持ち、挙動も異なることがあります（streaming/tool support/version skew）。

## Live: model matrix（何をカバーするか）

固定の「CI model list」はありません（liveはオプトインです）が、キーを持つdevマシンで定期的にカバーすることを**推奨**するモデルは以下です。

### Modernスモークセット（tool calling + image）

これは、動作し続けることを期待する「一般的なモデル」実行です。

- OpenAI（非Codex）: `openai/gpt-5.4`（任意: `openai/gpt-5.4-mini`）
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）: `google/gemini-3.1-pro-preview` および `google/gemini-3-flash-preview`（古いGemini 2.xモデルは避ける）
- Google（Antigravity）: `google-antigravity/claude-opus-4-6-thinking` および `google-antigravity/gemini-3-flash`
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

tools + image付きでGatewayスモークを実行:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### ベースライン: tool calling（Read + 任意のExec）

少なくとも各プロバイダーファミリーから1つ選んでください。

- OpenAI: `openai/gpt-5.4`（または `openai/gpt-5.4-mini`）
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google: `google/gemini-3-flash-preview`（または `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

任意の追加カバレッジ（あると望ましい）:

- xAI: `xai/grok-4`（または利用可能な最新）
- Mistral: `mistral/`…（有効化されている「tools」対応モデルを1つ選ぶ）
- Cerebras: `cerebras/`…（アクセスできる場合）
- LM Studio: `lmstudio/`…（ローカル。tool callingはAPI modeに依存）

### Vision: image送信（attachment → multimodal message）

image probeを実行するために、少なくとも1つのimage対応モデル（Claude/Gemini/OpenAIのvision対応バリアントなど）を `OPENCLAW_LIVE_GATEWAY_MODELS` に含めてください。

### Aggregator / 代替Gateway

キーが有効なら、以下経由でのテストもサポートしています。

- OpenRouter: `openrouter/...`（数百のモデル。tool+image対応候補を見つけるには `openclaw models scan` を使用）
- OpenCode: Zen向けの `opencode/...` と、Go向けの `opencode-go/...`（authは `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`）

live matrixに含められるその他のプロバイダー（認証情報/configがある場合）:

- 組み込み: `openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`google-gemini-cli`、`zai`、`openrouter`、`opencode`、`opencode-go`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`
- `models.providers` 経由（カスタムエンドポイント）: `minimax`（cloud/API）、およびOpenAI/Anthropic互換の任意のproxy（LM Studio、vLLM、LiteLLMなど）

ヒント: ドキュメントに「すべてのモデル」をハードコードしようとしないでください。権威ある一覧は、あなたのマシン上で `discoverModels(...)` が返すものと、利用可能なキーによって決まります。

## 認証情報（絶対にコミットしない）

liveテストは、CLIと同じ方法で認証情報を見つけます。実務上の意味は以下です。

- CLIが動くなら、liveテストも同じキーを見つけられるはずです。
- liveテストが「認証情報なし」と言うなら、`openclaw models list` / model選択をデバッグするときと同じ方法でデバッグしてください。

- エージェントごとのauth profile: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（liveテストで「profile keys」が意味するのはこれです）
- Config: `~/.openclaw/openclaw.json`（または `OPENCLAW_CONFIG_PATH`）
- レガシーstateディレクトリ: `~/.openclaw/credentials/`（存在する場合はステージされたlive homeにコピーされますが、メインのprofile-key storeではありません）
- ローカルのlive実行は、デフォルトでアクティブなconfig、エージェントごとの `auth-profiles.json` ファイル、レガシー `credentials/`、およびサポートされる外部CLI authディレクトリを一時的なテストhomeへコピーします。ステージされたlive homeでは `workspace/` と `sandboxes/` をスキップし、`agents.*.workspace` / `agentDir` のパス上書きも削除されるため、probeが実際のホストworkspaceに触れないようになっています。

envキー（たとえば `~/.profile` でexportしたもの）に依存したい場合は、`source ~/.profile` の後にローカルテストを実行するか、以下のDockerランナーを使ってください（これらは `~/.profile` をcontainer内にマウントできます）。

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
- スコープ:
  - バンドルされたcomfyのimage、video、および `music_generate` パスを実行する
  - `models.providers.comfy.<capability>` が設定されていない限り、各capabilityをスキップする
  - comfy workflow submission、polling、downloads、またはPlugin registrationを変更した後に有用

## Image generation live

- テスト: `src/image-generation/runtime.live.test.ts`
- コマンド: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- スコープ:
  - 登録されているすべてのimage-generation provider Pluginを列挙する
  - probe前にログインshell（`~/.profile`）から不足しているprovider env varsを読み込む
  - デフォルトでは、保存済みauth profileよりlive/env APIキーを優先して使うため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠さない
  - 使用可能なauth/profile/modelがないproviderはスキップする
  - 共有runtime capabilityを通じて標準のimage-generationバリアントを実行する:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- 現在カバーされているバンドルprovider:
  - `openai`
  - `google`
- 任意の絞り込み:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- 任意のauth挙動:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Music generation live

- テスト: `extensions/music-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- スコープ:
  - 共有のバンドルされたmusic-generation providerパスを実行する
  - 現在はGoogleとMiniMaxをカバーする
  - probe前にログインshell（`~/.profile`）からprovider env varsを読み込む
  - デフォルトでは、保存済みauth profileよりlive/env APIキーを優先して使うため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠さない
  - 使用可能なauth/profile/modelがないproviderはスキップする
  - 利用可能な場合は、宣言された両方のruntime modeを実行する:
    - promptのみ入力の `generate`
    - providerが `capabilities.edit.enabled` を宣言している場合の `edit`
  - 現在の共有レーンカバレッジ:
    - `google`: `generate`、`edit`
    - `minimax`: `generate`
    - `comfy`: この共有sweepではなく、別のComfy liveファイル
- 任意の絞り込み:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- 任意のauth挙動:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Video generation live

- テスト: `extensions/video-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- スコープ:
  - 共有のバンドルされたvideo-generation providerパスを実行する
  - デフォルトでは、リリース安全なスモークパスを使います: FAL以外のprovider、providerごとに1回のtext-to-videoリクエスト、1秒のlobster prompt、そして `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS`（デフォルト `180000`）によるproviderごとのoperation上限
  - provider側のqueue latencyがリリース時間を支配することがあるため、FALはデフォルトでスキップされます。明示的に実行するには `--video-providers fal` または `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="fal"` を渡してください
  - probe前にログインshell（`~/.profile`）からprovider env varsを読み込む
  - デフォルトでは、保存済みauth profileよりlive/env APIキーを優先して使うため、`auth-profiles.json` 内の古いテストキーが実際のshell認証情報を隠さない
  - 使用可能なauth/profile/modelがないproviderはスキップする
  - デフォルトでは `generate` のみを実行する
  - 利用可能な場合に宣言されたtransform modeも実行するには `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1` を設定:
    - providerが `capabilities.imageToVideo.enabled` を宣言し、選択されたprovider/modelが共有sweep内でbuffer-backedなローカルimage入力を受け付ける場合の `imageToVideo`
    - providerが `capabilities.videoToVideo.enabled` を宣言し、選択されたprovider/modelが共有sweep内でbuffer-backedなローカルvideo入力を受け付ける場合の `videoToVideo`
  - 現在、共有sweepで宣言されているがスキップされる `imageToVideo` provider:
    - `vydra`。バンドルされた `veo3` はtext-onlyで、バンドルされた `kling` はリモートimage URLを必要とするため
  - provider固有のVydraカバレッジ:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - このファイルは、`veo3` のtext-to-videoと、デフォルトでリモートimage URL fixtureを使う `kling` レーンを実行します
  - 現在の `videoToVideo` liveカバレッジ:
    - 選択されたmodelが `runway/gen4_aleph` の場合の `runway` のみ
  - 現在、共有sweepで宣言されているがスキップされる `videoToVideo` provider:
    - `alibaba`、`qwen`、`xai`。これらのパスは現在、リモートの `http(s)` / MP4 reference URLを必要とするため
    - `google`。現在の共有Gemini/Veoレーンはローカルのbuffer-backed入力を使っており、そのパスは共有sweepでは受け付けられないため
    - `openai`。現在の共有レーンではorg固有のvideo inpaint/remixアクセス保証がないため
- 任意の絞り込み:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
  - デフォルトsweep内のFALを含むすべてのproviderを含めるには `OPENCLAW_LIVE_VIDEO_GENERATION_SKIP_PROVIDERS=""`
  - 積極的なスモーク実行向けに各providerのoperation上限を下げるには `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS=60000`
- 任意のauth挙動:
  - profile-store authを強制し、env-only上書きを無視するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`

## Media live harness

- コマンド: `pnpm test:live:media`
- 目的:
  - 共有のimage、music、videoのliveスイートを、リポジトリネイティブな1つのentrypoint経由で実行する
  - `~/.profile` から不足しているprovider env varsを自動で読み込む
  - デフォルトでは、現在使用可能なauthを持つproviderに各スイートを自動で絞り込む
  - `scripts/test-live.mjs` を再利用するため、Heartbeatおよびquiet-modeの挙動が一貫する
- 例:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Dockerランナー（任意の「Linuxで動く」チェック）

これらのDockerランナーは、2つのバケットに分かれています:

- live-modelランナー: `test:docker:live-models` と `test:docker:live-gateway` は、それぞれ対応するprofile-key liveファイルのみをリポジトリDocker image内で実行します（`src/agents/models.profiles.live.test.ts` と `src/gateway/gateway-models.profiles.live.test.ts`）。ローカルのconfigディレクトリとworkspaceをマウントし（マウントされていれば `~/.profile` もsourceします）。対応するローカルentrypointは `test:live:models-profiles` と `test:live:gateway-profiles` です。
- Docker liveランナーは、完全なDocker sweepを現実的に保つため、デフォルトでより小さなスモーク上限を使います:
  `test:docker:live-models` はデフォルトで `OPENCLAW_LIVE_MAX_MODELS=12`、
  `test:docker:live-gateway` はデフォルトで `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`、および
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` を使います。より大きな網羅的スキャンを明示的に望む場合は、これらのenv varを上書きしてください。
- `test:docker:all` は、まず `test:docker:live-build` 経由でlive Docker imageを1回だけbuildし、その後2つのlive Dockerレーンで再利用します。
- containerスモークランナー: `test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels`、`test:docker:plugins` は、1つ以上の実コンテナを起動し、より高レベルなintegration pathを検証します。

live-model Dockerランナーは、必要なCLI auth homeのみ（または実行が絞り込まれていない場合はサポートされるものすべて）をbind-mountし、その後実行前にcontainer homeへコピーします。これにより、外部CLI OAuthがホストのauth storeを変更せずにトークンを更新できます。

- Direct models: `pnpm test:docker:live-models`（スクリプト: `scripts/test-live-models-docker.sh`）
- ACP bindスモーク: `pnpm test:docker:live-acp-bind`（スクリプト: `scripts/test-live-acp-bind-docker.sh`）
- CLI backendスモーク: `pnpm test:docker:live-cli-backend`（スクリプト: `scripts/test-live-cli-backend-docker.sh`）
- Codex app-server harnessスモーク: `pnpm test:docker:live-codex-harness`（スクリプト: `scripts/test-live-codex-harness-docker.sh`）
- Gateway + devエージェント: `pnpm test:docker:live-gateway`（スクリプト: `scripts/test-live-gateway-models-docker.sh`）
- Open WebUI liveスモーク: `pnpm test:docker:openwebui`（スクリプト: `scripts/e2e/openwebui-docker.sh`）
- オンボーディング ウィザード（TTY、完全なscaffolding）: `pnpm test:docker:onboard`（スクリプト: `scripts/e2e/onboard-docker.sh`）
- Gatewayネットワーキング（2つのcontainer、WS auth + health）: `pnpm test:docker:gateway-network`（スクリプト: `scripts/e2e/gateway-network-docker.sh`）
- MCP channel bridge（seed済みGateway + stdio bridge + 生のClaude notification-frameスモーク）: `pnpm test:docker:mcp-channels`（スクリプト: `scripts/e2e/mcp-channels-docker.sh`）
- Plugins（installスモーク + `/plugin` エイリアス + Claude-bundle restart semantics）: `pnpm test:docker:plugins`（スクリプト: `scripts/e2e/plugins-docker.sh`）

live-model Dockerランナーは、現在のcheckoutも読み取り専用でbind-mountし、container内の一時workdirへステージします。これにより、runtime
imageをスリムに保ちながら、正確にあなたのローカルsource/configに対してVitestを実行できます。
ステージング手順では、大きなローカル専用キャッシュやアプリbuild出力、たとえば
`.pnpm-store`、`.worktrees`、`__openclaw_vitest__`、およびアプリローカルの `.build` や
Gradle出力ディレクトリをスキップするため、Docker live実行がマシン固有artifactのコピーに何分も費やすことはありません。
また、container内で実際のTelegram/Discordなどのchannel workerを起動しないよう、
`OPENCLAW_SKIP_CHANNELS=1` も設定します。
`test:docker:live-models` は依然として `pnpm test:live` を実行するため、
そのDockerレーンからGateway liveカバレッジを絞り込んだり除外したりする必要がある場合は、
`OPENCLAW_LIVE_GATEWAY_*` も渡してください。
`test:docker:openwebui` は、より高レベルな互換性スモークです。これは
OpenAI互換HTTPエンドポイントを有効にしたOpenClaw Gateway containerを起動し、
そのGatewayに対して固定版のOpen WebUI containerを起動し、Open WebUI経由でサインインし、
`/api/models` が `openclaw/default` を公開していることを検証し、その後
Open WebUIの `/api/chat/completions` proxy経由で実際のchatリクエストを送信します。
初回実行は、Dockerが
Open WebUI imageをpullする必要があったり、Open WebUI自身のcold-start setupを完了する必要があったりするため、目立って遅いことがあります。
このレーンは使用可能なlive model keyを必要とし、Docker化された実行でそれを提供する主な方法は
`OPENCLAW_PROFILE_FILE`（デフォルトは `~/.profile`）です。
成功した実行では、`{ "ok": true, "model":
"openclaw/default", ... }` のような小さなJSON payloadが出力されます。
`test:docker:mcp-channels` は意図的に決定論的であり、
実際のTelegram、Discord、またはiMessageアカウントを必要としません。これはseed済みGateway
containerを起動し、`openclaw mcp serve` を起動する2つ目のcontainerを立ち上げ、その後
ルーティングされたconversation discovery、transcript読み取り、attachment metadata、
live event queue挙動、outbound送信ルーティング、およびClaude風のchannel +
permission通知を、実際のstdio MCP bridge上で検証します。通知チェックは
生のstdio MCP frameを直接検査するため、このスモークは特定のclient SDKがたまたまsurfaceするものではなく、
bridgeが実際に発行するものを検証します。

手動ACP平文threadスモーク（CIではない）:

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- このスクリプトはリグレッション/デバッグワークフロー用に維持してください。ACP thread routing検証のために再び必要になる可能性があるので、削除しないでください。

便利なenv var:

- `OPENCLAW_CONFIG_DIR=...`（デフォルト: `~/.openclaw`）を `/home/node/.openclaw` にマウント
- `OPENCLAW_WORKSPACE_DIR=...`（デフォルト: `~/.openclaw/workspace`）を `/home/node/.openclaw/workspace` にマウント
- `OPENCLAW_PROFILE_FILE=...`（デフォルト: `~/.profile`）を `/home/node/.profile` にマウントし、テスト実行前にsource
- `OPENCLAW_DOCKER_PROFILE_ENV_ONLY=1` で、`OPENCLAW_PROFILE_FILE` からsourceしたenv varのみを検証し、一時的なconfig/workspaceディレクトリを使い、外部CLI authマウントは行わない
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）を `/home/node/.npm-global` にマウントし、Docker内のCLI installをキャッシュ
- `$HOME` 配下の外部CLI authディレクトリ/ファイルは、読み取り専用で `/host-auth...` 配下にマウントされ、その後テスト開始前に `/home/node/...` へコピーされる
  - デフォルトディレクトリ: `.minimax`
  - デフォルトファイル: `~/.codex/auth.json`、`~/.codex/config.toml`、`.claude.json`、`~/.claude/.credentials.json`、`~/.claude/settings.json`、`~/.claude/settings.local.json`
  - 絞り込まれたprovider実行では、`OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` から推定された必要なディレクトリ/ファイルのみをマウントする
  - 手動上書きは `OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`、または `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` のようなカンマ区切りリスト
- 実行を絞り込む `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- container内でproviderをフィルタする `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- build不要の再実行で既存の `openclaw:local-live` imageを再利用する `OPENCLAW_SKIP_DOCKER_BUILD=1`
- 認証情報がprofile store由来であることを保証する `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`（envではない）
- Open WebUIスモークでGatewayが公開するmodelを選ぶ `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUIスモークで使うnonceチェックpromptを上書きする `OPENCLAW_OPENWEBUI_PROMPT=...`
- 固定されたOpen WebUI image tagを上書きする `OPENWEBUI_IMAGE=...`

## Docsの健全性確認

ドキュメント編集後はdocsチェックを実行してください: `pnpm check:docs`。  
ページ内見出しチェックも必要な場合は、完全なMintlify anchor検証を実行してください: `pnpm docs:check-links:anchors`。

## Offlineリグレッション（CI-safe）

これらは、実プロバイダーなしでの「実際のパイプライン」リグレッションです。

- Gateway tool calling（mock OpenAI、実際のGateway + エージェントループ）: `src/gateway/gateway.test.ts`（ケース: 「runs a mock OpenAI tool call end-to-end via gateway agent loop」）
- Gatewayウィザード（WS `wizard.start`/`wizard.next`、config + auth enforcedを書き込む）: `src/gateway/gateway.test.ts`（ケース: 「runs wizard over ws and writes auth token config」）

## エージェント信頼性eval（Skills）

すでに、いくつかのCI-safeな、いわば「エージェント信頼性eval」のようなテストがあります。

- 実際のGateway + エージェントループを通じたmock tool-calling（`src/gateway/gateway.test.ts`）。
- session配線とconfig効果を検証するend-to-endのウィザードフロー（`src/gateway/gateway.test.ts`）。

Skillsについてまだ不足しているもの（[Skills](/ja-JP/tools/skills) を参照）:

- **意思決定:** prompt内にSkillsが列挙されているとき、エージェントは正しいskillを選ぶか（または無関係なものを避けるか）？
- **準拠:** エージェントは使用前に `SKILL.md` を読み、必須の手順/引数に従うか？
- **ワークフロー契約:** tool順序、session historyの引き継ぎ、sandbox boundaryを検証する複数ターンのシナリオ。

今後のevalは、まず決定論的であるべきです。

- mock providerを使ってtool call + 順序、skillファイル読み取り、session配線を検証するscenario runner。
- skillに焦点を当てた小規模なシナリオスイート（使う/使わない、ゲーティング、prompt injection）。
- CI-safeスイートが整ってからの、任意のlive eval（オプトイン、env gate付き）のみ。

## Contractテスト（Pluginおよびchannel shape）

Contractテストは、登録されているすべてのPluginとchannelが
そのinterface contractに準拠していることを検証します。検出されたすべてのPluginを反復し、
shapeと挙動の検証スイートを実行します。デフォルトの `pnpm test` unitレーンは意図的に
これらの共有seamおよびスモークファイルをスキップするため、共有channelまたはprovider surfaceに触れたときは
Contractコマンドを明示的に実行してください。

### コマンド

- すべてのcontract: `pnpm test:contracts`
- channel contractのみ: `pnpm test:contracts:channels`
- provider contractのみ: `pnpm test:contracts:plugins`

### channel contract

`src/channels/plugins/contracts/*.contract.test.ts` にあります:

- **plugin** - 基本的なPlugin shape（id、name、capabilities）
- **setup** - セットアップ ウィザード契約
- **session-binding** - Session bindingの挙動
- **outbound-payload** - メッセージpayload構造
- **inbound** - inboundメッセージ処理
- **actions** - channel action handler
- **threading** - thread ID処理
- **directory** - directory/roster API
- **group-policy** - グループポリシーの適用

### provider status contract

`src/plugins/contracts/*.contract.test.ts` にあります。

- **status** - channel status probe
- **registry** - Plugin registry shape

### provider contract

`src/plugins/contracts/*.contract.test.ts` にあります:

- **auth** - authフロー契約
- **auth-choice** - authの選択/選定
- **catalog** - model catalog API
- **discovery** - Plugin discovery
- **loader** - Plugin loading
- **runtime** - provider runtime
- **shape** - Plugin shape/interface
- **wizard** - セットアップ ウィザード

### 実行するタイミング

- plugin-sdkのexportまたはsubpathを変更した後
- channelまたはprovider Pluginを追加または変更した後
- Plugin registrationまたはdiscoveryをリファクタリングした後

ContractテストはCIで実行され、実際のAPIキーは不要です。

## リグレッションを追加する（ガイダンス）

liveで見つかったprovider/modelの問題を修正するとき:

- 可能であればCI-safeなリグレッションを追加してください（providerのmock/stub、または正確なrequest-shape変換のキャプチャ）
- 本質的にlive-onlyな場合（rate limit、authポリシー）は、liveテストを狭く保ち、env var経由のオプトインにしてください
- バグを捕捉できる最小のレイヤーを狙うことを優先してください:
  - provider request conversion/replayバグ → direct modelsテスト
  - Gateway session/history/tool pipelineバグ → Gateway liveスモークまたはCI-safeなGateway mockテスト
- SecretRef traversal guardrail:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` は、registry metadata（`listSecretTargetRegistryEntries()`）からSecretRef classごとに1つのサンプルtargetを導出し、その後、traversal-segment exec idが拒否されることを検証します。
  - `src/secrets/target-registry-data.ts` に新しい `includeInPlan` SecretRef target familyを追加する場合は、そのテスト内の `classifyTargetClass` を更新してください。このテストは、未分類のtarget idに対して意図的に失敗するため、新しいclassが黙ってスキップされることはありません。
