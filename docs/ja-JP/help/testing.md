---
read_when:
    - ローカルまたはCIでテストを実行する
    - モデル/プロバイダーのバグに対するリグレッションテストを追加する
    - Gateway + エージェントの動作をデバッグする
summary: 'テストキット: unit/e2e/liveスイート、Dockerランナー、および各テストがカバーする内容'
title: テスト中
x-i18n:
    generated_at: "2026-04-16T21:51:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: af2bc0e9b5e08ca3119806d355b517290f6078fda430109e7a0b153586215e34
    source_path: help/testing.md
    workflow: 15
---

# テスト

OpenClawには3つのVitestスイート（unit/integration、e2e、live）と、少数のDockerランナーがあります。

このドキュメントは「どのようにテストするか」のガイドです。

- 各スイートが何をカバーするか（そして意図的に何を _カバーしない_ か）
- 一般的なワークフロー（ローカル、push前、デバッグ）で実行するコマンド
- liveテストがどのように認証情報を検出し、モデル/プロバイダーを選択するか
- 実運用のモデル/プロバイダー問題に対するリグレッションを追加する方法

## クイックスタート

普段は次のとおりです。

- フルゲート（push前に想定）: `pnpm build && pnpm check && pnpm test`
- 余裕のあるマシンでの、より高速なローカル全スイート実行: `pnpm test:max`
- 直接のVitest watchループ: `pnpm test:watch`
- 直接のファイル指定は、extension/channelのパスにも対応するようになりました: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- 単一の失敗を反復修正しているときは、まず対象を絞った実行を優先してください。
- DockerバックのQAサイト: `pnpm qa:lab:up`
- Linux VMバックのQAレーン: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

テストに触れたとき、または追加の確信が欲しいとき:

- カバレッジゲート: `pnpm test:coverage`
- E2Eスイート: `pnpm test:e2e`

実際のプロバイダー/モデルをデバッグするとき（実際の認証情報が必要）:

- liveスイート（モデル + Gatewayのツール/画像プローブ）: `pnpm test:live`
- 1つのliveファイルだけを静かに対象化: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

ヒント: 必要なのが1つの失敗ケースだけなら、以下で説明するallowlist環境変数を使ってliveテストを絞り込むことを優先してください。

## QA専用ランナー

これらのコマンドは、QA-lab相当の現実性が必要なときに、メインのテストスイートと並んで使います。

- `pnpm openclaw qa suite`
  - リポジトリバックのQAシナリオをホスト上で直接実行します。
  - デフォルトでは、隔離されたGatewayワーカーを使って複数の選択シナリオを並列実行します。最大64ワーカーまたは選択シナリオ数までです。ワーカー数の調整には `--concurrency <count>` を使用し、従来の直列レーンにしたい場合は `--concurrency 1` を使用します。
- `pnpm openclaw qa suite --runner multipass`
  - 同じQAスイートを一時的なMultipass Linux VM内で実行します。
  - ホスト上の `qa suite` と同じシナリオ選択の挙動を維持します。
  - `qa suite` と同じプロバイダー/モデル選択フラグを再利用します。
  - live実行では、ゲスト向けに現実的な範囲で、サポート対象のQA認証入力を転送します:
    envベースのプロバイダーキー、QA liveプロバイダー設定パス、存在する場合は `CODEX_HOME`。
  - 出力ディレクトリは、ゲストがマウントされたワークスペース経由で書き戻せるよう、リポジトリルート配下に置く必要があります。
  - 通常のQAレポート + サマリーに加え、Multipassログを `.artifacts/qa-e2e/...` 配下に書き込みます。
- `pnpm qa:lab:up`
  - オペレーター型のQA作業向けに、DockerバックのQAサイトを起動します。
- `pnpm openclaw qa matrix`
  - 使い捨てのDockerバックTuwunel homeserverに対して、Matrix live QAレーンを実行します。
  - このQAホストは現時点ではrepo/dev専用です。パッケージ化されたOpenClawインストールには `qa-lab` が含まれないため、`openclaw qa` は公開されません。
  - リポジトリチェックアウトでは、バンドル済みランナーを直接読み込みます。別途Pluginのインストール手順は不要です。
  - 一時的なMatrixユーザー3人（`driver`、`sut`、`observer`）と1つのプライベートルームを用意し、実際のMatrix PluginをSUTトランスポートとして使うQA Gateway子プロセスを起動します。
  - デフォルトでは、固定された安定版Tuwunelイメージ `ghcr.io/matrix-construct/tuwunel:v1.5.1` を使用します。別のイメージをテストしたい場合は `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` で上書きします。
  - Matrixはローカルで使い捨てユーザーを生成するため、共有のcredential-sourceフラグは公開しません。
  - Matrix QAレポート、サマリー、observed-eventsアーティファクト、結合されたstdout/stderr出力ログを `.artifacts/qa-e2e/...` 配下に書き込みます。
- `pnpm openclaw qa telegram`
  - envのdriverおよびSUTボットトークンを使用し、実際のプライベートグループに対してTelegram live QAレーンを実行します。
  - `OPENCLAW_QA_TELEGRAM_GROUP_ID`、`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`、`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` が必要です。group idは数値のTelegram chat idである必要があります。
  - 共有プール認証情報には `--credential-source convex` をサポートします。通常はenvモードを使用し、プールされたリースを使う場合は `OPENCLAW_QA_CREDENTIAL_SOURCE=convex` を設定してください。
  - 同じプライベートグループ内に2つの異なるボットが必要で、SUTボットはTelegram usernameを公開している必要があります。
  - 安定したボット間観測のため、両方のボットで `@BotFather` の Bot-to-Bot Communication Mode を有効にし、driverボットがグループ内のボット通信を観測できるようにしてください。
  - Telegram QAレポート、サマリー、observed-messagesアーティファクトを `.artifacts/qa-e2e/...` 配下に書き込みます。

liveトランスポートレーンは、新しいトランスポートが逸脱しないよう、1つの標準契約を共有します。

`qa-channel` は引き続き広範な合成QAスイートであり、liveトランスポートのカバレッジマトリクスには含まれません。

| レーン | Canary | メンションゲーティング | Allowlist block | トップレベル返信 | 再起動後の再開 | スレッド追従 | スレッド分離 | リアクション観測 | ヘルプコマンド |
| ------ | ------ | ---------------------- | --------------- | ---------------- | -------------- | ------------ | ------------ | ---------------- | -------------- |
| Matrix   | x      | x                      | x               | x                | x              | x            | x            | x                |                |
| Telegram | x      |                        |                 |                  |                |              |              |                  | x              |

### Convex経由の共有Telegram認証情報（v1）

`openclaw qa telegram` で `--credential-source convex`（または `OPENCLAW_QA_CREDENTIAL_SOURCE=convex`）が有効な場合、QA labはConvexバックのプールから排他的なリースを取得し、レーンの実行中はそのリースにHeartbeatを送り、終了時にリースを解放します。

参考用のConvexプロジェクト雛形:

- `qa/convex-credential-broker/`

必須の環境変数:

- `OPENCLAW_QA_CONVEX_SITE_URL`（例: `https://your-deployment.convex.site`）
- 選択したロール用のシークレット1つ:
  - `maintainer` 用の `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER`
  - `ci` 用の `OPENCLAW_QA_CONVEX_SECRET_CI`
- 認証ロールの選択:
  - CLI: `--credential-role maintainer|ci`
  - 環境変数のデフォルト: `OPENCLAW_QA_CREDENTIAL_ROLE`（デフォルトは `maintainer`）

任意の環境変数:

- `OPENCLAW_QA_CREDENTIAL_LEASE_TTL_MS`（デフォルト `1200000`）
- `OPENCLAW_QA_CREDENTIAL_HEARTBEAT_INTERVAL_MS`（デフォルト `30000`）
- `OPENCLAW_QA_CREDENTIAL_ACQUIRE_TIMEOUT_MS`（デフォルト `90000`）
- `OPENCLAW_QA_CREDENTIAL_HTTP_TIMEOUT_MS`（デフォルト `15000`）
- `OPENCLAW_QA_CONVEX_ENDPOINT_PREFIX`（デフォルト `/qa-credentials/v1`）
- `OPENCLAW_QA_CREDENTIAL_OWNER_ID`（任意のトレースid）
- `OPENCLAW_QA_ALLOW_INSECURE_HTTP=1` を設定すると、ローカル専用開発向けに loopback の `http://` Convex URL を許可します。

通常運用では、`OPENCLAW_QA_CONVEX_SITE_URL` は `https://` を使用してください。

メンテナー向け管理コマンド（プールの追加/削除/一覧）には、特に `OPENCLAW_QA_CONVEX_SECRET_MAINTAINER` が必要です。

メンテナー向けCLIヘルパー:

```bash
pnpm openclaw qa credentials add --kind telegram --payload-file qa/telegram-credential.json
pnpm openclaw qa credentials list --kind telegram
pnpm openclaw qa credentials remove --credential-id <credential-id>
```

スクリプトやCIユーティリティで機械可読な出力が必要な場合は `--json` を使ってください。

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
- `POST /admin/add`（maintainer secret専用）
  - リクエスト: `{ kind, actorId, payload, note?, status? }`
  - 成功: `{ status: "ok", credential }`
- `POST /admin/remove`（maintainer secret専用）
  - リクエスト: `{ credentialId, actorId }`
  - 成功: `{ status: "ok", changed, credential }`
  - アクティブリースのガード: `{ status: "error", code: "LEASE_ACTIVE", ... }`
- `POST /admin/list`（maintainer secret専用）
  - リクエスト: `{ kind?, status?, includePayload?, limit? }`
  - 成功: `{ status: "ok", credentials, count }`

Telegram種別のペイロード形状:

- `{ groupId: string, driverToken: string, sutToken: string }`
- `groupId` は数値のTelegram chat id文字列である必要があります。
- `admin/add` は `kind: "telegram"` に対してこの形状を検証し、不正なペイロードを拒否します。

### QAにチャネルを追加する

Markdown QAシステムにチャネルを追加するには、必要なのは正確に2つだけです。

1. そのチャネル用のトランスポートアダプター
2. そのチャネル契約を検証するシナリオパック

共有の `qa-lab` ホストでフローを管理できる場合は、新しいトップレベルQAコマンドルートを追加しないでください。

`qa-lab` は共有ホスト機構を管理します:

- `openclaw qa` コマンドルート
- スイートの起動と終了
- ワーカー並列度
- アーティファクト書き込み
- レポート生成
- シナリオ実行
- 旧 `qa-channel` シナリオ向けの互換エイリアス

ランナーPluginはトランスポート契約を管理します:

- `openclaw qa <runner>` を共有 `qa` ルート配下にどのようにマウントするか
- そのトランスポート向けにGatewayをどう設定するか
- 準備完了をどう確認するか
- 受信イベントをどう注入するか
- 送信メッセージをどう観測するか
- transcript と正規化済みトランスポート状態をどう公開するか
- トランスポートバックのアクションをどう実行するか
- トランスポート固有のリセットやクリーンアップをどう扱うか

新しいチャネルに求められる最小採用要件は次のとおりです。

1. 共有 `qa` ルートの管理者は `qa-lab` のままにする。
2. 共有 `qa-lab` ホスト境界でトランスポートランナーを実装する。
3. トランスポート固有の仕組みはランナーPluginまたはチャネルハーネス内に閉じ込める。
4. 競合するルートコマンドを登録するのではなく、ランナーを `openclaw qa <runner>` としてマウントする。  
   ランナーPluginは `openclaw.plugin.json` に `qaRunners` を宣言し、`runtime-api.ts` から対応する `qaRunnerCliRegistrations` 配列をエクスポートする必要があります。  
   `runtime-api.ts` は軽量に保ってください。遅延CLIおよびランナー実行は、別のエントリーポイントの背後に置く必要があります。
5. `qa/scenarios/` 配下にMarkdownシナリオを作成または適応する。
6. 新しいシナリオには汎用シナリオヘルパーを使う。
7. リポジトリが意図的な移行中でない限り、既存の互換エイリアスを維持する。

判断ルールは厳格です。

- 振る舞いを `qa-lab` で一度だけ表現できるなら、`qa-lab` に置く。
- 振る舞いが1つのチャネルトランスポートに依存するなら、そのランナーPluginまたはPluginハーネスに置く。
- あるシナリオが複数チャネルで使える新しい機能を必要とするなら、`suite.ts` にチャネル固有の分岐を追加するのではなく、汎用ヘルパーを追加する。
- 振る舞いが1つのトランスポートにしか意味を持たないなら、そのシナリオはトランスポート固有のままにし、そのことをシナリオ契約で明示する。

新しいシナリオで推奨される汎用ヘルパー名は次のとおりです。

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

既存シナリオ向けに、互換エイリアスも引き続き利用できます。

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

新しいチャネル作業では、汎用ヘルパー名を使うべきです。  
互換エイリアスは、一斉移行を避けるために存在しているのであって、新しいシナリオ作成のモデルではありません。

## テストスイート（どこで何が実行されるか）

スイートは「現実性が増していくもの」（同時に不安定さ/コストも増える）として考えてください。

### Unit / integration（デフォルト）

- コマンド: `pnpm test`
- 設定: 既存のスコープ付きVitestプロジェクトに対する、10回の逐次シャード実行（`vitest.full-*.config.ts`）
- ファイル: `src/**/*.test.ts`、`packages/**/*.test.ts`、`test/**/*.test.ts` 配下のcore/unitインベントリ、および `vitest.unit.config.ts` でカバーされる許可済みの `ui` Nodeテスト
- スコープ:
  - 純粋なunitテスト
  - プロセス内integrationテスト（Gateway認証、ルーティング、ツール、パース、設定）
  - 既知のバグに対する決定論的なリグレッション
- 期待事項:
  - CIで実行される
  - 実際のキーは不要
  - 高速かつ安定しているべき
- プロジェクトに関する注記:
  - 対象を絞らない `pnpm test` は、1つの巨大なネイティブルートプロジェクトプロセスの代わりに、11個の小さなシャード設定（`core-unit-src`、`core-unit-security`、`core-unit-ui`、`core-unit-support`、`core-support-boundary`、`core-contracts`、`core-bundled`、`core-runtime`、`agentic`、`auto-reply`、`extensions`）を実行するようになりました。これにより、負荷の高いマシンでのピークRSSが削減され、auto-reply/extensionの処理が無関係なスイートを圧迫することを避けられます。
  - `pnpm test --watch` は依然としてネイティブルートの `vitest.config.ts` プロジェクトグラフを使用します。これは、マルチシャードのwatchループが現実的ではないためです。
  - `pnpm test`、`pnpm test:watch`、`pnpm test:perf:imports` は、明示的なファイル/ディレクトリ指定をまずスコープ付きレーンにルーティングするため、`pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` はフルルートプロジェクト起動のコストを払わずに済みます。
  - `pnpm test:changed` は、差分がルーティング可能なソース/テストファイルのみを対象にしている場合、変更されたgitパスを同じスコープ付きレーンへ展開します。設定/セットアップの編集は、引き続き広範なルートプロジェクト再実行にフォールバックします。
  - agents、commands、plugins、auto-replyヘルパー、`plugin-sdk` などの純粋なユーティリティ領域にあるimport負荷の軽いunitテストは、`test/setup-openclaw-runtime.ts` をスキップする `unit-fast` レーンにルーティングされます。stateful/runtime-heavyなファイルは既存レーンのままです。
  - 選択された `plugin-sdk` および `commands` のヘルパーソースファイルも、changedモードの実行をこれらの軽量レーン内の明示的な隣接テストへマップするため、ヘルパー編集時にそのディレクトリ全体の重いスイートを再実行せずに済みます。
  - `auto-reply` には現在、3つの専用バケットがあります: トップレベルのコアヘルパー、トップレベルの `reply.*` integrationテスト、そして `src/auto-reply/reply/**` サブツリーです。これにより、最も重いreplyハーネスの処理が、軽量なstatus/chunk/tokenテストに影響しないようにしています。
- 埋め込みランナーに関する注記:
  - メッセージツール検出入力またはCompactionランタイムコンテキストを変更するときは、両方のレベルのカバレッジを維持してください。
  - 純粋なルーティング/正規化境界には、焦点を絞ったヘルパーリグレッションを追加してください。
  - 同時に、埋め込みランナーのintegrationスイートも健全に保ってください:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`、
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`、および
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`。
  - これらのスイートは、スコープ付きidとCompactionの挙動が実際の `run.ts` / `compact.ts` 経路を通じて流れ続けることを検証します。ヘルパー専用テストだけでは、これらのintegration経路の十分な代替にはなりません。
- Poolに関する注記:
  - ベースVitest設定は現在、デフォルトで `threads` を使用します。
  - 共有Vitest設定は `isolate: false` も固定し、ルートプロジェクト、e2e、live設定全体で非分離ランナーを使用します。
  - ルートUIレーンは `jsdom` セットアップとoptimizerを維持していますが、現在は共有の非分離ランナー上でも動作します。
  - 各 `pnpm test` シャードは、共有Vitest設定から同じ `threads` + `isolate: false` のデフォルトを継承します。
  - 共有の `scripts/run-vitest.mjs` ランチャーは、大規模なローカル実行時のV8コンパイル負荷を減らすため、Vitest子Nodeプロセスにデフォルトで `--no-maglev` も追加するようになりました。標準のV8挙動と比較したい場合は `OPENCLAW_VITEST_ENABLE_MAGLEV=1` を設定してください。
- 高速ローカル反復に関する注記:
  - `pnpm test:changed` は、変更パスがより小さなスイートにきれいにマップされる場合、スコープ付きレーンを経由します。
  - `pnpm test:max` と `pnpm test:changed:max` も同じルーティング挙動を維持しつつ、より高いワーカー上限を使います。
  - ローカルのワーカー自動スケーリングは現在意図的に保守的で、ホストの負荷平均がすでに高いときにも抑制されるため、複数のVitest実行を同時に走らせた際の影響をデフォルトで減らします。
  - ベースVitest設定は、changedモードの再実行がテスト配線の変更時にも正しくなるよう、プロジェクト/設定ファイルを `forceRerunTriggers` としてマークします。
  - 設定は、サポートされるホスト上で `OPENCLAW_VITEST_FS_MODULE_CACHE` を有効にしたままにします。直接プロファイリング用に明示的なキャッシュ場所を1つ指定したい場合は `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` を設定してください。
- パフォーマンスデバッグに関する注記:
  - `pnpm test:perf:imports` は、Vitestのimport時間レポートとimport内訳出力を有効にします。
  - `pnpm test:perf:imports:changed` は、同じプロファイリング表示を `origin/main` 以降で変更されたファイルに絞り込みます。
- `pnpm test:perf:changed:bench -- --ref <git-ref>` は、そのコミット済み差分について、ルーティングされた `test:changed` とネイティブルートプロジェクト経路を比較し、wall timeとmacOSの最大RSSを表示します。
- `pnpm test:perf:changed:bench -- --worktree` は、変更されたファイル一覧を `scripts/test-projects.mjs` とルートVitest設定に通すことで、現在の未コミットツリーをベンチマークします。
  - `pnpm test:perf:profile:main` は、Vitest/Viteの起動およびtransformオーバーヘッドに対するメインスレッドCPUプロファイルを書き出します。
  - `pnpm test:perf:profile:runner` は、ファイル並列実行を無効にしたunitスイート向けに、ランナーのCPU+heapプロファイルを書き出します。

### E2E（Gatewayスモーク）

- コマンド: `pnpm test:e2e`
- 設定: `vitest.e2e.config.ts`
- ファイル: `src/**/*.e2e.test.ts`、`test/**/*.e2e.test.ts`
- ランタイムのデフォルト:
  - リポジトリの他の部分に合わせて、Vitest `threads` と `isolate: false` を使用します。
  - 適応型ワーカーを使用します（CI: 最大2、ローカル: デフォルト1）。
  - コンソールI/Oのオーバーヘッドを減らすため、デフォルトでsilentモードで実行します。
- 便利な上書き:
  - ワーカー数を強制するには `OPENCLAW_E2E_WORKERS=<n>`（上限16）。
  - 詳細なコンソール出力を再有効化するには `OPENCLAW_E2E_VERBOSE=1`。
- スコープ:
  - 複数インスタンスのGatewayエンドツーエンド挙動
  - WebSocket/HTTPサーフェス、Nodeペアリング、およびより重いネットワーキング
- 期待事項:
  - CIで実行される（パイプラインで有効化されている場合）
  - 実際のキーは不要
  - unitテストより可動部分が多い（遅くなる可能性がある）

### E2E: OpenShellバックエンドスモーク

- コマンド: `pnpm test:e2e:openshell`
- ファイル: `test/openshell-sandbox.e2e.test.ts`
- スコープ:
  - Docker経由でホスト上に隔離されたOpenShell Gatewayを起動する
  - 一時的なローカルDockerfileからsandboxを作成する
  - 実際の `sandbox ssh-config` + SSH実行を通じて、OpenClawのOpenShellバックエンドを検証する
  - sandbox fsブリッジを通じて、リモート正準ファイルシステム挙動を検証する
- 期待事項:
  - 明示的に有効化した場合のみ。デフォルトの `pnpm test:e2e` 実行には含まれない
  - ローカルの `openshell` CLI と動作するDockerデーモンが必要
  - 隔離された `HOME` / `XDG_CONFIG_HOME` を使用し、その後テスト用Gatewayとsandboxを破棄する
- 便利な上書き:
  - より広いe2eスイートを手動実行するときにこのテストを有効化するには `OPENCLAW_E2E_OPENSHELL=1`
  - デフォルト以外のCLIバイナリまたはラッパースクリプトを指定するには `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell`

### Live（実際のプロバイダー + 実際のモデル）

- コマンド: `pnpm test:live`
- 設定: `vitest.live.config.ts`
- ファイル: `src/**/*.live.test.ts`
- デフォルト: `pnpm test:live` により **有効**（`OPENCLAW_LIVE_TEST=1` を設定）
- スコープ:
  - 「このプロバイダー/モデルは、今日、実際の認証情報で本当に動くか？」
  - プロバイダーのフォーマット変更、ツール呼び出しの癖、認証問題、レート制限挙動を捕捉する
- 期待事項:
  - 設計上、CI安定ではない（実ネットワーク、実際のプロバイダーポリシー、クォータ、障害）
  - コストがかかる / レート制限を消費する
  - 「すべて」を実行するより、対象を絞ったサブセット実行を推奨
- live実行は、不足しているAPIキーを拾うために `~/.profile` を読み込みます。
- デフォルトでは、live実行は依然として `HOME` を隔離し、設定/認証情報を一時的なテスト用homeにコピーするため、unitフィクスチャが実際の `~/.openclaw` を変更することはありません。
- liveテストで意図的に実際のhomeディレクトリを使いたい場合にのみ、`OPENCLAW_LIVE_USE_REAL_HOME=1` を設定してください。
- `pnpm test:live` は現在、より静かなモードがデフォルトです。`[live] ...` の進行出力は維持しますが、追加の `~/.profile` 通知を抑制し、Gatewayブートストラップログ/Bonjourの雑音をミュートします。完全な起動ログを再表示したい場合は `OPENCLAW_LIVE_TEST_QUIET=0` を設定してください。
- APIキーのローテーション（プロバイダー別）: カンマ/セミコロン形式の `*_API_KEYS`、または `*_API_KEY_1`、`*_API_KEY_2`（例: `OPENAI_API_KEYS`、`ANTHROPIC_API_KEYS`、`GEMINI_API_KEYS`）を設定するか、live専用の上書きとして `OPENCLAW_LIVE_*_KEY` を使用します。テストはレート制限応答時にリトライします。
- 進行/Heartbeat出力:
  - liveスイートは現在、長時間のプロバイダー呼び出しが、Vitestのコンソールキャプチャが静かな場合でも動作中だと分かるよう、進行行をstderrに出力します。
  - `vitest.live.config.ts` はVitestのコンソール横取りを無効化しているため、プロバイダー/Gatewayの進行行はlive実行中に即座にストリーミングされます。
  - 直接モデルのHeartbeat調整には `OPENCLAW_LIVE_HEARTBEAT_MS` を使用します。
  - Gateway/プローブのHeartbeat調整には `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS` を使用します。

## どのスイートを実行すべきか？

この判断表を使ってください。

- ロジック/テストを編集した: `pnpm test` を実行（大きく変更したなら `pnpm test:coverage` も）
- Gatewayのネットワーキング / WSプロトコル / ペアリングに触れた: `pnpm test:e2e` を追加
- 「自分のボットが落ちている」/ プロバイダー固有の失敗 / ツール呼び出しをデバッグしている: 絞り込んだ `pnpm test:live` を実行

## Live: Android Node機能スイープ

- テスト: `src/gateway/android-node.capabilities.live.test.ts`
- スクリプト: `pnpm android:test:integration`
- 目的: 接続されたAndroid Nodeが**現在広告しているすべてのコマンド**を呼び出し、コマンド契約の挙動を検証すること。
- スコープ:
  - 前提条件付き/手動セットアップ（このスイートはアプリのインストール/起動/ペアリングを行いません）。
  - 選択されたAndroid Nodeに対する、コマンドごとのGateway `node.invoke` 検証。
- 必須の事前セットアップ:
  - AndroidアプリがすでにGatewayに接続され、ペアリングされていること。
  - アプリがフォアグラウンドに保たれていること。
  - 成功を期待する機能に対して、権限/キャプチャ同意が付与されていること。
- 任意のターゲット上書き:
  - `OPENCLAW_ANDROID_NODE_ID` または `OPENCLAW_ANDROID_NODE_NAME`
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`
- Androidの完全なセットアップ詳細: [Android App](/ja-JP/platforms/android)

## Live: モデルスモーク（プロファイルキー）

liveテストは、失敗を切り分けられるよう2層に分かれています。

- 「直接モデル」は、与えられたキーでそのプロバイダー/モデルがそもそも応答できるかを示します。
- 「Gatewayスモーク」は、そのモデルに対してGateway+エージェントの完全なパイプライン（セッション、履歴、ツール、sandboxポリシーなど）が機能することを示します。

### レイヤー1: 直接モデル完了（Gatewayなし）

- テスト: `src/agents/models.profiles.live.test.ts`
- 目的:
  - 発見されたモデルを列挙する
  - `getApiKeyForModel` を使用して、認証情報を持っているモデルを選択する
  - モデルごとに小さな完了処理を実行する（必要に応じて対象を絞ったリグレッションも）
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
- このスイートを実際に実行するには `OPENCLAW_LIVE_MODELS=modern`（または `all`、これはmodernの別名）を設定します。そうでない場合、`pnpm test:live` をGatewayスモークに集中させるためにスキップされます。
- モデルの選択方法:
  - modern allowlistを実行するには `OPENCLAW_LIVE_MODELS=modern`（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_MODELS=all` はmodern allowlistの別名です
  - または `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."`（カンマ区切りallowlist）
  - modern/allスイープは、デフォルトで厳選された高信号の上限を使用します。網羅的なmodernスイープには `OPENCLAW_LIVE_MAX_MODELS=0`、より小さい上限には正の数を設定します。
- プロバイダーの選択方法:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"`（カンマ区切りallowlist）
- キーの取得元:
  - デフォルト: プロファイルストアとenvフォールバック
  - **プロファイルストアのみ** を強制するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` を設定
- これが存在する理由:
  - 「プロバイダーAPIが壊れている / キーが無効」と「Gatewayエージェントパイプラインが壊れている」を切り分ける
  - 小さく隔離されたリグレッションを収容する（例: OpenAI Responses/Codex Responsesのreasoning replay + tool-callフロー）

### レイヤー2: Gateway + devエージェントスモーク（`@openclaw` が実際に行うこと）

- テスト: `src/gateway/gateway-models.profiles.live.test.ts`
- 目的:
  - プロセス内Gatewayを起動する
  - `agent:dev:*` セッションを作成/patchする（実行ごとにモデル上書き）
  - キー付きモデルを反復し、次を検証する:
    - 「意味のある」応答（ツールなし）
    - 実際のツール呼び出しが機能すること（readプローブ）
    - 任意の追加ツールプローブ（exec+readプローブ）
    - OpenAIのリグレッション経路（tool-call-only → follow-up）が引き続き機能すること
- プローブの詳細（失敗をすばやく説明できるように）:
  - `read` プローブ: テストがワークスペースにnonceファイルを書き込み、エージェントにそれを `read` してnonceをそのまま返すよう求めます。
  - `exec+read` プローブ: テストがエージェントに対して `exec` で一時ファイルにnonceを書き込み、その後それを `read` で読み戻すよう求めます。
  - imageプローブ: テストが生成したPNG（cat + ランダム化コード）を添付し、モデルが `cat <CODE>` を返すことを期待します。
  - 実装参照: `src/gateway/gateway-models.profiles.live.test.ts` および `src/gateway/live-image-probe.ts`
- 有効化方法:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
- モデルの選択方法:
  - デフォルト: modern allowlist（Opus/Sonnet 4.6+、GPT-5.x + Codex、Gemini 3、GLM 4.7、MiniMax M2.7、Grok 4）
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` はmodern allowlistの別名です
  - または `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"`（またはカンマ区切りリスト）を設定して絞り込む
  - modern/allのGatewayスイープは、デフォルトで厳選された高信号の上限を使用します。網羅的なmodernスイープには `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0`、より小さい上限には正の数を設定します。
- プロバイダーの選択方法（「OpenRouterを全部」は避ける）:
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"`（カンマ区切りallowlist）
- このliveテストではツール + imageプローブは常時有効です:
  - `read` プローブ + `exec+read` プローブ（ツール負荷テスト）
  - imageプローブは、モデルがimage入力サポートを公開している場合に実行されます
  - フロー（概要）:
    - テストが「CAT」+ ランダムコードの小さなPNGを生成します（`src/gateway/live-image-probe.ts`）
    - これを `agent` の `attachments: [{ mimeType: "image/png", content: "<base64>" }]` 経由で送信します
    - Gatewayが添付を `images[]` にパースします（`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`）
    - 埋め込みエージェントがマルチモーダルなユーザーメッセージをモデルへ転送します
    - 検証: 返信に `cat` + そのコードが含まれること（OCR許容: 軽微な誤りは許容）

ヒント: 自分のマシンで何をテストできるか（および正確な `provider/model` id）を確認するには、次を実行してください。

```bash
openclaw models list
openclaw models list --json
```

## Live: CLIバックエンドスモーク（Claude、Codex、Gemini、またはその他のローカルCLI）

- テスト: `src/gateway/gateway-cli-backend.live.test.ts`
- 目的: デフォルト設定に触れずに、ローカルCLIバックエンドを使ってGateway + エージェントのパイプラインを検証する。
- バックエンド固有のスモークデフォルトは、所有するextensionの `cli-backend.ts` 定義とともに置かれます。
- 有効化:
  - `pnpm test:live`（またはVitestを直接呼び出す場合は `OPENCLAW_LIVE_TEST=1`）
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- デフォルト:
  - デフォルトのプロバイダー/モデル: `claude-cli/claude-sonnet-4-6`
  - コマンド/引数/image挙動は、所有するCLIバックエンドPluginメタデータから取得されます。
- 上書き（任意）:
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - 実際のimage添付を送信するには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1`（パスはプロンプトへ注入されます）
  - プロンプト注入の代わりにimageファイルパスをCLI引数として渡すには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"`
  - `IMAGE_ARG` が設定されている場合のimage引数の渡し方を制御するには `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"`（または `"list"`）
  - 2ターン目を送ってresumeフローを検証するには `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1`
  - デフォルトのClaude Sonnet -> Opus同一セッション継続プローブを無効にするには `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0`（選択したモデルが切り替え先をサポートしている場合に強制有効化するには `1` を設定）

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
- これはリポジトリのDockerイメージ内で、非rootの `node` ユーザーとしてlive CLIバックエンドスモークを実行します。
- 所有するextensionからCLIスモークメタデータを解決し、一致するLinux CLIパッケージ（`@anthropic-ai/claude-code`、`@openai/codex`、または `@google/gemini-cli`）を、キャッシュ可能で書き込み可能なprefix `OPENCLAW_DOCKER_CLI_TOOLS_DIR`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）にインストールします。
- `pnpm test:docker:live-cli-backend:claude-subscription` には、`~/.claude/.credentials.json` と `claudeAiOauth.subscriptionType`、または `claude setup-token` の `CLAUDE_CODE_OAUTH_TOKEN` によるポータブルなClaude CodeサブスクリプションOAuthが必要です。まずDocker内で直接 `claude -p` を検証し、その後Anthropic APIキー環境変数を保持せずに2回のGateway CLIバックエンドターンを実行します。このsubscriptionレーンでは、Claudeが現在サードパーティアプリ利用を通常のsubscriptionプラン上限ではなく追加利用課金経由で処理するため、Claude MCP/ツールおよびimageプローブはデフォルトで無効になります。
- live CLIバックエンドスモークは現在、Claude、Codex、Geminiに対して同じエンドツーエンドフローを検証します: テキストターン、image分類ターン、その後Gateway CLI経由で検証されるMCP `cron` ツール呼び出しです。
- Claudeのデフォルトスモークでは、セッションをSonnetからOpusへpatchし、resumeしたセッションが以前のメモを引き続き覚えていることも検証します。

## Live: ACP bindスモーク（`/acp spawn ... --bind here`）

- テスト: `src/gateway/gateway-acp-bind.live.test.ts`
- 目的: live ACPエージェントを使って、実際のACP会話bindフローを検証すること:
  - `/acp spawn <agent> --bind here` を送信
  - 合成のメッセージチャネル会話をその場でbind
  - 同じ会話上で通常のfollow-upを送信
  - そのfollow-upがbind済みACPセッショントランスクリプトに入ることを確認
- 有効化:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- デフォルト:
  - Docker内のACPエージェント: `claude,codex,gemini`
  - 直接の `pnpm test:live ...` 用ACPエージェント: `claude`
  - 合成チャネル: Slack DM風の会話コンテキスト
  - ACPバックエンド: `acpx`
- 上書き:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- 注記:
  - このレーンは、テストが外部配信を装わずにメッセージチャネルコンテキストを付与できるよう、管理者専用の合成originating-routeフィールド付きのGateway `chat.send` サーフェスを使います。
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` が未設定の場合、テストは埋め込みの `acpx` Plugin内蔵エージェントレジストリを、選択されたACPハーネスエージェント向けに使用します。

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
- デフォルトでは、サポートされるすべてのlive CLIエージェントに対してACP bindスモークを順番に実行します: `claude`、`codex`、`gemini`。
- マトリクスを絞り込むには `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`、`OPENCLAW_LIVE_ACP_BIND_AGENTS=codex`、または `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` を使用します。
- これは `~/.profile` を読み込み、一致するCLI認証情報をコンテナへステージし、`acpx` を書き込み可能なnpm prefixにインストールし、不足している場合は要求されたlive CLI（`@anthropic-ai/claude-code`、`@openai/codex`、または `@google/gemini-cli`）をインストールします。
- Docker内では、ランナーは `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` を設定し、ソース済みprofileからのプロバイダーenv変数をacpxが子ハーネスCLIでも利用できるようにします。

## Live: Codex app-serverハーネススモーク

- 目的: Pluginが所有するCodexハーネスを、通常のGateway
  `agent` メソッド経由で検証すること:
  - バンドル済みの `codex` Pluginを読み込む
  - `OPENCLAW_AGENT_RUNTIME=codex` を選択する
  - `codex/gpt-5.4` に最初のGateway agentターンを送る
  - 同じOpenClawセッションに2ターン目を送り、app-server
    スレッドがresumeできることを確認する
  - 同じGatewayコマンド
    経路を通じて `/codex status` と `/codex models` を実行する
- テスト: `src/gateway/gateway-codex-harness.live.test.ts`
- 有効化: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- デフォルトモデル: `codex/gpt-5.4`
- 任意のimageプローブ: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- 任意のMCP/ツールプローブ: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- このスモークは `OPENCLAW_AGENT_HARNESS_FALLBACK=none` を設定するため、壊れたCodex
  ハーネスがPIへのサイレントフォールバックによって通過することはありません。
- 認証: シェル/profileからの `OPENAI_API_KEY`、および任意でコピーされる
  `~/.codex/auth.json` と `~/.codex/config.toml`

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
- これはマウントされた `~/.profile` を読み込み、`OPENAI_API_KEY` を渡し、Codex CLI認証ファイルが存在する場合はそれをコピーし、`@openai/codex` を書き込み可能なマウント済みnpm prefixにインストールし、ソースツリーをステージしたうえで、Codexハーネスliveテストのみを実行します。
- DockerではimageおよびMCP/ツールプローブがデフォルトで有効です。より狭いデバッグ実行が必要な場合は
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` または
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` を設定してください。
- Dockerでも `OPENCLAW_AGENT_HARNESS_FALLBACK=none` をエクスポートし、live
  テスト設定と一致させます。これにより `openai-codex/*` やPIフォールバックがCodexハーネスの
  リグレッションを隠すことはできません。

### 推奨されるliveレシピ

狭く明示的なallowlistが最も高速で、最も不安定さが少なくなります。

- 単一モデル、直接（Gatewayなし）:
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- 単一モデル、Gatewayスモーク:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- 複数プロバイダーにまたがるツール呼び出し:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Google重視（Gemini APIキー + Antigravity）:
  - Gemini（APIキー）: `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity（OAuth）: `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

注記:

- `google/...` はGemini APIを使用します（APIキー）。
- `google-antigravity/...` はAntigravity OAuthブリッジを使用します（Cloud Code Assist風のエージェントエンドポイント）。
- `google-gemini-cli/...` はあなたのマシン上のローカルGemini CLIを使用します（別個の認証 + ツール面での癖があります）。
- Gemini APIとGemini CLIの違い:
  - API: OpenClawがGoogleのホスト型Gemini APIをHTTP経由で呼び出します（APIキー / プロファイル認証）。ほとんどのユーザーが「Gemini」と言うとき、これを指します。
  - CLI: OpenClawがローカルの `gemini` バイナリをshell実行します。独自の認証があり、挙動も異なることがあります（ストリーミング/ツールサポート/バージョン差異）。

## Live: モデルマトリクス（何をカバーするか）

固定の「CIモデル一覧」はありません（liveはオプトイン）が、開発マシン上でキー付きで定期的にカバーすることを**推奨**するモデルは次のとおりです。

### Modernスモークセット（ツール呼び出し + image）

これは、動作し続けることを期待する「一般的なモデル」実行です。

- OpenAI（非Codex）: `openai/gpt-5.4`（任意: `openai/gpt-5.4-mini`）
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google（Gemini API）: `google/gemini-3.1-pro-preview` および `google/gemini-3-flash-preview`（古いGemini 2.xモデルは避ける）
- Google（Antigravity）: `google-antigravity/claude-opus-4-6-thinking` および `google-antigravity/gemini-3-flash`
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

ツール + image付きでGatewayスモークを実行:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### ベースライン: ツール呼び出し（Read + 任意のExec）

プロバイダーファミリーごとに少なくとも1つは選んでください。

- OpenAI: `openai/gpt-5.4`（または `openai/gpt-5.4-mini`）
- Anthropic: `anthropic/claude-opus-4-6`（または `anthropic/claude-sonnet-4-6`）
- Google: `google/gemini-3-flash-preview`（または `google/gemini-3.1-pro-preview`）
- Z.AI（GLM）: `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

任意の追加カバレッジ（あるとよいもの）:

- xAI: `xai/grok-4`（または利用可能な最新）
- Mistral: `mistral/`…（有効化されている「tools」対応モデルを1つ選ぶ）
- Cerebras: `cerebras/`…（アクセス権がある場合）
- LM Studio: `lmstudio/`…（ローカル。ツール呼び出しはAPIモードに依存）

### Vision: image送信（添付 → マルチモーダルメッセージ）

imageプローブを検証するため、`OPENCLAW_LIVE_GATEWAY_MODELS` には少なくとも1つのimage対応モデル（Claude/Gemini/OpenAIのvision対応バリアントなど）を含めてください。

### アグリゲーター / 代替Gateway

キーが有効なら、次経由のテストもサポートしています。

- OpenRouter: `openrouter/...`（数百のモデル。ツール+image対応候補を探すには `openclaw models scan` を使用）
- OpenCode: Zen向けの `opencode/...` およびGo向けの `opencode-go/...`（認証は `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`）

liveマトリクスに含められるその他のプロバイダー（認証情報/設定がある場合）:

- 組み込み: `openai`、`openai-codex`、`anthropic`、`google`、`google-vertex`、`google-antigravity`、`google-gemini-cli`、`zai`、`openrouter`、`opencode`、`opencode-go`、`xai`、`groq`、`cerebras`、`mistral`、`github-copilot`
- `models.providers` 経由（カスタムエンドポイント）: `minimax`（cloud/API）、および任意のOpenAI/Anthropic互換プロキシ（LM Studio、vLLM、LiteLLMなど）

ヒント: ドキュメント内で「すべてのモデル」をハードコードしようとしないでください。権威ある一覧は、あなたのマシンで `discoverModels(...)` が返すものと、利用可能なキー次第です。

## 認証情報（絶対にコミットしない）

liveテストは、CLIと同じ方法で認証情報を検出します。実際上の意味は次のとおりです。

- CLIが動くなら、liveテストも同じキーを見つけられるはずです。
- liveテストが「認証情報なし」と言うなら、`openclaw models list` / モデル選択をデバッグするときと同じように調べてください。

- エージェントごとの認証プロファイル: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（liveテストで「profile keys」と言っているのはこれです）
- 設定: `~/.openclaw/openclaw.json`（または `OPENCLAW_CONFIG_PATH`）
- 旧stateディレクトリ: `~/.openclaw/credentials/`（存在する場合はステージされたlive homeにコピーされますが、メインのprofile-keyストアではありません）
- ローカルのlive実行では、デフォルトでアクティブ設定、エージェントごとの `auth-profiles.json`、旧 `credentials/`、およびサポートされる外部CLI認証ディレクトリを一時テストhomeへコピーします。ステージされたlive homeでは `workspace/` と `sandboxes/` はスキップされ、`agents.*.workspace` / `agentDir` パス上書きは削除されるため、プローブが実際のホストワークスペースに影響しません。

envキーに依存したい場合（たとえば `~/.profile` でexportしている場合）は、`source ~/.profile` の後でローカルテストを実行するか、以下のDockerランナーを使ってください（これらは `~/.profile` をコンテナへマウントできます）。

## Deepgram live（音声文字起こし）

- テスト: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- 有効化: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## BytePlus coding plan live

- テスト: `src/agents/byteplus.live.test.ts`
- 有効化: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- 任意のモデル上書き: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## ComfyUI workflow media live

- テスト: `extensions/comfy/comfy.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- スコープ:
  - バンドル済みcomfyのimage、video、および `music_generate` 経路を検証する
  - `models.providers.comfy.<capability>` が設定されていない場合は各機能をスキップする
  - comfyのworkflow送信、ポーリング、ダウンロード、またはPlugin登録を変更した後に有用

## Image generation live

- テスト: `src/image-generation/runtime.live.test.ts`
- コマンド: `pnpm test:live src/image-generation/runtime.live.test.ts`
- ハーネス: `pnpm test:live:media image`
- スコープ:
  - 登録されているすべてのimage-generation provider Pluginを列挙する
  - プローブ前に、足りないprovider env変数をログインシェル（`~/.profile`）から読み込む
  - デフォルトでは、保存済み認証プロファイルよりもlive/env APIキーを優先するため、`auth-profiles.json` 内の古いテストキーが実際のシェル認証情報を隠しません
  - 利用可能な認証/プロファイル/モデルがないプロバイダーはスキップする
  - 共有ランタイム機能を通じて標準のimage-generationバリアントを実行する:
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
- 任意の認証挙動:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` でプロファイルストア認証を強制し、envのみの上書きを無視する

## Music generation live

- テスト: `extensions/music-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- ハーネス: `pnpm test:live:media music`
- スコープ:
  - 共有のバンドル済みmusic-generation provider経路を検証する
  - 現在はGoogleとMiniMaxをカバーする
  - プローブ前に、ログインシェル（`~/.profile`）からprovider env変数を読み込む
  - デフォルトでは、保存済み認証プロファイルよりもlive/env APIキーを優先するため、`auth-profiles.json` 内の古いテストキーが実際のシェル認証情報を隠しません
  - 利用可能な認証/プロファイル/モデルがないプロバイダーはスキップする
  - 利用可能な場合、宣言された両方のランタイムモードを実行する:
    - プロンプトのみ入力の `generate`
    - プロバイダーが `capabilities.edit.enabled` を宣言している場合の `edit`
  - 現在の共有レーンカバレッジ:
    - `google`: `generate`、`edit`
    - `minimax`: `generate`
    - `comfy`: 別のComfy liveファイルであり、この共有スイープではない
- 任意の絞り込み:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- 任意の認証挙動:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` でプロファイルストア認証を強制し、envのみの上書きを無視する

## Video generation live

- テスト: `extensions/video-generation-providers.live.test.ts`
- 有効化: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- ハーネス: `pnpm test:live:media video`
- スコープ:
  - 共有のバンドル済みvideo-generation provider経路を検証する
  - デフォルトでは、リリース安全なスモーク経路を使用する: FAL以外のプロバイダー、プロバイダーごとに1件のtext-to-videoリクエスト、1秒のlobsterプロンプト、そして `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS`（デフォルト `180000`）から取得されるプロバイダーごとの操作上限
  - FALは、プロバイダー側のキュー遅延がリリース時間を支配しうるため、デフォルトでスキップされます。明示的に実行するには `--video-providers fal` または `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="fal"` を渡してください
  - プローブ前に、ログインシェル（`~/.profile`）からprovider env変数を読み込む
  - デフォルトでは、保存済み認証プロファイルよりもlive/env APIキーを優先するため、`auth-profiles.json` 内の古いテストキーが実際のシェル認証情報を隠しません
  - 利用可能な認証/プロファイル/モデルがないプロバイダーはスキップする
  - デフォルトでは `generate` のみを実行する
  - 利用可能な場合に宣言されたtransformモードも実行するには `OPENCLAW_LIVE_VIDEO_GENERATION_FULL_MODES=1` を設定する:
    - プロバイダーが `capabilities.imageToVideo.enabled` を宣言しており、選択されたプロバイダー/モデルが共有スイープでバッファバックのローカルimage入力を受け付ける場合の `imageToVideo`
    - プロバイダーが `capabilities.videoToVideo.enabled` を宣言しており、選択されたプロバイダー/モデルが共有スイープでバッファバックのローカルvideo入力を受け付ける場合の `videoToVideo`
  - 現在、共有スイープで宣言はされているがスキップされる `imageToVideo` プロバイダー:
    - バンドル済み `veo3` はtext専用で、バンドル済み `kling` はリモートimage URLを必要とするため、`vydra`
  - プロバイダー固有のVydraカバレッジ:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - このファイルは `veo3` のtext-to-videoに加え、デフォルトでリモートimage URLフィクスチャを使う `kling` レーンを実行します
  - 現在の `videoToVideo` liveカバレッジ:
    - 選択モデルが `runway/gen4_aleph` の場合のみ `runway`
  - 現在、共有スイープで宣言はされているがスキップされる `videoToVideo` プロバイダー:
    - これらの経路は現在リモートの `http(s)` / MP4参照URLを必要とするため、`alibaba`、`qwen`、`xai`
    - 現在の共有Gemini/Veoレーンがローカルのバッファバック入力を使っており、その経路は共有スイープでは受け付けられないため、`google`
    - 現在の共有レーンには組織固有のvideo inpaint/remixアクセス保証がないため、`openai`
- 任意の絞り込み:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_SKIP_PROVIDERS=""` で、FALを含むデフォルトスイープ内のすべてのプロバイダーを含める
  - `OPENCLAW_LIVE_VIDEO_GENERATION_TIMEOUT_MS=60000` で、積極的なスモーク実行向けに各プロバイダーの操作上限を短縮する
- 任意の認証挙動:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` でプロファイルストア認証を強制し、envのみの上書きを無視する

## メディアliveハーネス

- コマンド: `pnpm test:live:media`
- 目的:
  - 共有のimage、music、videoのliveスイートを、リポジトリネイティブな1つのエントリーポイントから実行する
  - `~/.profile` から不足しているprovider env変数を自動読み込みする
  - デフォルトで、現在利用可能な認証を持つプロバイダーに各スイートを自動的に絞り込む
  - `scripts/test-live.mjs` を再利用するため、Heartbeatとquietモードの挙動が一貫する
- 例:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Dockerランナー（任意の「Linuxで動く」確認）

これらのDockerランナーは、2つのカテゴリに分かれます。

- liveモデルランナー: `test:docker:live-models` と `test:docker:live-gateway` は、それぞれ対応するprofile-key liveファイルのみをリポジトリDockerイメージ内で実行します（`src/agents/models.profiles.live.test.ts` と `src/gateway/gateway-models.profiles.live.test.ts`）。ローカルのconfigディレクトリとworkspaceをマウントし（マウントされていれば `~/.profile` も読み込みます）。対応するローカルエントリーポイントは `test:live:models-profiles` と `test:live:gateway-profiles` です。
- Docker liveランナーは、完全なDockerスイープを現実的な時間で保つために、デフォルトでより小さいスモーク上限を使用します:
  `test:docker:live-models` のデフォルトは `OPENCLAW_LIVE_MAX_MODELS=12`、そして
  `test:docker:live-gateway` のデフォルトは `OPENCLAW_LIVE_GATEWAY_SMOKE=1`、
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`、
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`、および
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000` です。より大きな網羅的スキャンを明示的に行いたい場合は、これらのenv変数を上書きしてください。
- `test:docker:all` は、まず `test:docker:live-build` でlive Dockerイメージを1回ビルドし、その後2つのlive Dockerレーンで再利用します。
- コンテナスモークランナー: `test:docker:openwebui`、`test:docker:onboard`、`test:docker:gateway-network`、`test:docker:mcp-channels`、`test:docker:plugins` は、1つ以上の実コンテナを起動し、より高レベルなintegration経路を検証します。

liveモデルDockerランナーは、必要なCLI認証homeのみ（または実行が絞り込まれていない場合はサポートされるすべて）をbind-mountし、その後、外部CLI OAuthがホストの認証ストアを変更せずにトークンを更新できるよう、実行前にそれらをコンテナhomeへコピーします。

- 直接モデル: `pnpm test:docker:live-models`（スクリプト: `scripts/test-live-models-docker.sh`）
- ACP bindスモーク: `pnpm test:docker:live-acp-bind`（スクリプト: `scripts/test-live-acp-bind-docker.sh`）
- CLIバックエンドスモーク: `pnpm test:docker:live-cli-backend`（スクリプト: `scripts/test-live-cli-backend-docker.sh`）
- Codex app-serverハーネススモーク: `pnpm test:docker:live-codex-harness`（スクリプト: `scripts/test-live-codex-harness-docker.sh`）
- Gateway + devエージェント: `pnpm test:docker:live-gateway`（スクリプト: `scripts/test-live-gateway-models-docker.sh`）
- Open WebUI liveスモーク: `pnpm test:docker:openwebui`（スクリプト: `scripts/e2e/openwebui-docker.sh`）
- オンボーディングウィザード（TTY、完全なscaffolding）: `pnpm test:docker:onboard`（スクリプト: `scripts/e2e/onboard-docker.sh`）
- Gatewayネットワーキング（2コンテナ、WS認証 + health）: `pnpm test:docker:gateway-network`（スクリプト: `scripts/e2e/gateway-network-docker.sh`）
- MCPチャネルブリッジ（seed済みGateway + stdioブリッジ + 生のClaude通知フレームスモーク）: `pnpm test:docker:mcp-channels`（スクリプト: `scripts/e2e/mcp-channels-docker.sh`）
- Plugins（インストールスモーク + `/plugin` エイリアス + Claudeバンドル再起動セマンティクス）: `pnpm test:docker:plugins`（スクリプト: `scripts/e2e/plugins-docker.sh`）

liveモデルDockerランナーは、現在のcheckoutも読み取り専用でbind-mountし、コンテナ内の一時workdirへステージします。これにより、ランタイムイメージをスリムに保ちながら、正確にあなたのローカルソース/設定に対してVitestを実行できます。
このステージング手順では、`.pnpm-store`、`.worktrees`、`__openclaw_vitest__`、およびアプリローカルの `.build` やGradle出力ディレクトリのような、大きなローカル専用キャッシュやアプリビルド出力をスキップするため、Docker live実行でマシン固有のアーティファクトのコピーに何分も費やすことがありません。
また、コンテナ内で実際のTelegram/DiscordなどのチャネルワーカーをGateway liveプローブが起動しないように、`OPENCLAW_SKIP_CHANNELS=1` も設定します。
`test:docker:live-models` は依然として `pnpm test:live` を実行するため、そのDockerレーンからGateway liveカバレッジを絞り込んだり除外したりしたい場合は、`OPENCLAW_LIVE_GATEWAY_*` も渡してください。
`test:docker:openwebui` は、より高レベルな互換性スモークです。OpenAI互換HTTPエンドポイントを有効にしたOpenClaw Gatewayコンテナを起動し、そのGatewayに向けた固定版のOpen WebUIコンテナを起動し、Open WebUI経由でサインインし、`/api/models` が `openclaw/default` を公開していることを確認したうえで、Open WebUIの `/api/chat/completions` プロキシ経由で実際のチャットリクエストを送信します。
初回実行は、DockerがOpen WebUIイメージをpullする必要があったり、Open WebUI自身のコールドスタートセットアップを完了する必要があるため、目に見えて遅くなることがあります。
このレーンは使用可能なliveモデルキーを前提としており、Docker化された実行でそれを提供する主な方法は `OPENCLAW_PROFILE_FILE`
（デフォルトは `~/.profile`）です。
成功した実行では、`{ "ok": true, "model":
"openclaw/default", ... }` のような小さなJSONペイロードが出力されます。
`test:docker:mcp-channels` は意図的に決定論的であり、実際のTelegram、Discord、またはiMessageアカウントは必要ありません。seed済みGateway
コンテナを起動し、`openclaw mcp serve` を起動する2つ目のコンテナを開始し、その後、実際のstdio MCPブリッジ上で、ルーティングされた会話検出、トランスクリプト読み取り、添付メタデータ、liveイベントキュー挙動、送信ルーティング、そしてClaude風のチャネル +
権限通知を検証します。通知チェックでは、生のstdio MCPフレームを直接検査するため、このスモークは、特定のクライアントSDKがたまたま表面化するものではなく、ブリッジが実際に出力するものを検証します。

手動ACP平文スレッドスモーク（CIではない）:

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- このスクリプトはリグレッション/デバッグワークフロー用に維持してください。ACPスレッドルーティング検証で再び必要になる可能性があるため、削除しないでください。

便利なenv変数:

- `OPENCLAW_CONFIG_DIR=...`（デフォルト: `~/.openclaw`）を `/home/node/.openclaw` にマウント
- `OPENCLAW_WORKSPACE_DIR=...`（デフォルト: `~/.openclaw/workspace`）を `/home/node/.openclaw/workspace` にマウント
- `OPENCLAW_PROFILE_FILE=...`（デフォルト: `~/.profile`）を `/home/node/.profile` にマウントし、テスト実行前に読み込む
- `OPENCLAW_DOCKER_PROFILE_ENV_ONLY=1` で、`OPENCLAW_PROFILE_FILE` から読み込まれたenv変数のみを検証し、一時的なconfig/workspaceディレクトリを使い、外部CLI認証マウントは使わない
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...`（デフォルト: `~/.cache/openclaw/docker-cli-tools`）を `/home/node/.npm-global` にマウントし、Docker内のCLIインストールキャッシュとして使う
- `$HOME` 配下の外部CLI認証ディレクトリ/ファイルは、`/host-auth...` 配下に読み取り専用でマウントされ、テスト開始前に `/home/node/...` へコピーされます
  - デフォルトディレクトリ: `.minimax`
  - デフォルトファイル: `~/.codex/auth.json`、`~/.codex/config.toml`、`.claude.json`、`~/.claude/.credentials.json`、`~/.claude/settings.json`、`~/.claude/settings.local.json`
  - 絞り込まれたプロバイダー実行では、`OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS` から推測された必要なディレクトリ/ファイルのみをマウントします
  - 手動で上書きするには `OPENCLAW_DOCKER_AUTH_DIRS=all`、`OPENCLAW_DOCKER_AUTH_DIRS=none`、または `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex` のようなカンマ区切りリストを使用します
- 実行を絞り込むには `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...`
- コンテナ内でプロバイダーを絞り込むには `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...`
- リビルド不要の再実行で既存の `openclaw:local-live` イメージを再利用するには `OPENCLAW_SKIP_DOCKER_BUILD=1`
- 認証情報がenvではなくプロファイルストアから来ることを保証するには `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1`
- Open WebUIスモークでGatewayが公開するモデルを選ぶには `OPENCLAW_OPENWEBUI_MODEL=...`
- Open WebUIスモークで使うnonce確認プロンプトを上書きするには `OPENCLAW_OPENWEBUI_PROMPT=...`
- 固定されたOpen WebUIイメージタグを上書きするには `OPENWEBUI_IMAGE=...`

## ドキュメント健全性チェック

ドキュメントを編集した後は、ドキュメントチェックを実行してください: `pnpm check:docs`。
ページ内見出しチェックも必要な場合は、完全なMintlifyアンカー検証を実行してください: `pnpm docs:check-links:anchors`。

## オフラインリグレッション（CI安全）

これらは、実際のプロバイダーを使わない「実パイプライン」リグレッションです。

- Gatewayツール呼び出し（OpenAIをモック、実際のGateway + エージェントループ）: `src/gateway/gateway.test.ts`（ケース: 「モックOpenAIツール呼び出しをGatewayエージェントループ経由でエンドツーエンド実行する」）
- Gatewayウィザード（WS `wizard.start`/`wizard.next`、設定 + 認証の強制書き込み）: `src/gateway/gateway.test.ts`（ケース: 「WS経由でウィザードを実行し、auth token設定を書き込む」）

## エージェント信頼性評価（Skills）

すでにいくつかのCI安全なテストがあり、「エージェント信頼性評価」のように振る舞います。

- 実際のGateway + エージェントループを通したモックツール呼び出し（`src/gateway/gateway.test.ts`）。
- セッション配線と設定効果を検証するエンドツーエンドのウィザードフロー（`src/gateway/gateway.test.ts`）。

Skillsに関してまだ不足しているもの（[Skills](/ja-JP/tools/skills) を参照）:

- **判断**: Skillsがプロンプトに列挙されたとき、エージェントは正しいSkillを選ぶか（または無関係なものを避けるか）？
- **準拠**: エージェントは使用前に `SKILL.md` を読み、必要な手順/引数に従うか？
- **ワークフロー契約**: ツール順序、セッション履歴の持ち越し、sandbox境界を検証するマルチターンシナリオ。

将来の評価は、まず決定論的であるべきです。

- ツール呼び出し + 順序、Skillファイル読み取り、セッション配線を検証するために、モックプロバイダーを使うシナリオランナー。
- Skillに焦点を当てた小さなシナリオスイート（使う vs 使わない、ゲーティング、プロンプトインジェクション）。
- オプトインかつenvでゲートされた任意のlive評価は、CI安全スイートが整ってからにする。

## 契約テスト（Pluginおよびチャネル形状）

契約テストは、登録されたすべてのPluginとチャネルがその
インターフェース契約に準拠していることを検証します。見つかったすべてのPluginを反復し、
形状と挙動に関する一連の検証を実行します。デフォルトの `pnpm test` unitレーンは意図的に
これらの共有境界およびスモークファイルをスキップするため、共有チャネルまたはproviderサーフェスに触れた場合は、
契約コマンドを明示的に実行してください。

### コマンド

- すべての契約: `pnpm test:contracts`
- チャネル契約のみ: `pnpm test:contracts:channels`
- provider契約のみ: `pnpm test:contracts:plugins`

### チャネル契約

`src/channels/plugins/contracts/*.contract.test.ts` にあります:

- **plugin** - 基本的なPlugin形状（id、name、capabilities）
- **setup** - セットアップウィザード契約
- **session-binding** - セッションbind挙動
- **outbound-payload** - メッセージペイロード構造
- **inbound** - 受信メッセージ処理
- **actions** - チャネルアクションハンドラー
- **threading** - スレッドID処理
- **directory** - ディレクトリ/ロスターAPI
- **group-policy** - グループポリシーの強制

### provider status契約

`src/plugins/contracts/*.contract.test.ts` にあります。

- **status** - チャネルstatusプローブ
- **registry** - Pluginレジストリ形状

### provider契約

`src/plugins/contracts/*.contract.test.ts` にあります:

- **auth** - 認証フロー契約
- **auth-choice** - 認証選択/選定
- **catalog** - モデルcatalog API
- **discovery** - Plugin検出
- **loader** - Plugin読み込み
- **runtime** - providerランタイム
- **shape** - Plugin形状/インターフェース
- **wizard** - セットアップウィザード

### 実行するタイミング

- plugin-sdkのエクスポートまたはsubpathを変更した後
- チャネルまたはprovider Pluginを追加または変更した後
- Plugin登録または検出をリファクタリングした後

契約テストはCIで実行され、実際のAPIキーは必要ありません。

## リグレッションの追加（ガイダンス）

liveで見つかったprovider/modelの問題を修正したときは:

- 可能ならCI安全なリグレッションを追加する（providerをモック/スタブするか、正確なリクエスト形状変換をキャプチャする）
- 本質的にlive専用である場合（レート制限、認証ポリシーなど）は、liveテストを狭く保ち、env変数経由のオプトインにする
- バグを捕捉する最小のレイヤーを狙う:
  - providerのリクエスト変換/replayバグ → 直接モデルテスト
  - Gatewayセッション/履歴/ツールパイプラインのバグ → Gateway liveスモークまたはCI安全なGatewayモックテスト
- SecretRef走査ガードレール:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` は、レジストリメタデータ（`listSecretTargetRegistryEntries()`）からSecretRefクラスごとに1つのサンプル対象を導出し、その後、走査セグメントのexec idが拒否されることを検証します。
  - `src/secrets/target-registry-data.ts` に新しい `includeInPlan` SecretRef対象ファミリーを追加した場合は、そのテスト内の `classifyTargetClass` を更新してください。このテストは、未分類のtarget idに対して意図的に失敗するため、新しいクラスが黙ってスキップされることはありません。
