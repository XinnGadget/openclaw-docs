---
read_when:
    - テストを実行または修正する場合
summary: ローカルでテストを実行する方法（vitest）と、force/coverageモードを使うタイミング
title: テスト
x-i18n:
    generated_at: "2026-04-07T04:46:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: a25236a707860307cc324f32752ad13a53e448bee9341d8df2e11655561e841c
    source_path: reference/test.md
    workflow: 15
---

# テスト

- 完全なテストキット（スイート、live、Docker）: [Testing](/ja-JP/help/testing)

- `pnpm test:force`: デフォルトの制御ポートを保持している残留Gatewayプロセスを強制終了してから、分離されたGatewayポートで完全なVitestスイートを実行し、サーバーテストが実行中インスタンスと衝突しないようにします。以前のGateway実行によってポート18789が使用中のままになった場合に使用してください。
- `pnpm test:coverage`: V8カバレッジ付きでユニットスイートを実行します（`vitest.unit.config.ts` 経由）。グローバル閾値は lines/branches/functions/statements すべて70%です。カバレッジからは、対象をユニットテスト可能なロジックに絞るため、統合負荷の高いentrypoint（CLI配線、gateway/telegramブリッジ、webchat静的サーバー）を除外しています。
- `pnpm test:coverage:changed`: `origin/main` 以降に変更されたファイルのみを対象にユニットカバレッジを実行します。
- `pnpm test:changed`: 差分がルーティング可能なソース/テストファイルのみを変更している場合、変更されたgitパスをスコープ付きVitestレーンへ展開します。設定/セットアップ変更は、配線変更時に広範囲の再実行が必要になるため、引き続きネイティブなルートプロジェクト実行にフォールバックします。
- `pnpm test`: 明示的なファイル/ディレクトリ対象をスコープ付きVitestレーン経由で実行します。対象指定なしの実行では、1つの巨大なルートプロジェクトプロセスの代わりに、10個の逐次シャード設定（`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`）を実行するようになりました。
- 一部の `plugin-sdk` および `commands` テストファイルは、`test/setup.ts` のみを保持する専用の軽量レーンを通るようになり、ランタイム負荷の高いケースは既存レーンに残ります。
- 一部の `plugin-sdk` および `commands` ヘルパーソースファイルも、`pnpm test:changed` をそれら軽量レーン内の明示的な兄弟テストへマッピングするため、小規模なヘルパー編集で重いランタイム依存スイートを再実行せずに済みます。
- `auto-reply` も3つの専用設定（`core`、`top-level`、`reply`）に分割され、replyハーネスが軽量なtop-levelのstatus/token/helperテストを支配しないようになりました。
- ベースのVitest設定は、現在 `pool: "threads"` と `isolate: false` をデフォルトとし、共有の非分離runnerがリポジトリ全体の設定で有効になっています。
- `pnpm test:channels` は `vitest.channels.config.ts` を実行します。
- `pnpm test:extensions` は `vitest.extensions.config.ts` を実行します。
- `pnpm test:extensions`: extension/pluginスイートを実行します。
- `pnpm test:perf:imports`: 明示的なファイル/ディレクトリ対象に対してスコープ付きレーンルーティングを維持したまま、Vitestのimport-duration + import-breakdownレポートを有効にします。
- `pnpm test:perf:imports:changed`: 同じimportプロファイリングですが、`origin/main` 以降に変更されたファイルのみを対象にします。
- `pnpm test:perf:changed:bench -- --ref <git-ref>` は、同じコミット済みgit差分に対して、ルーティングされたchangedモードのパスをネイティブなルートプロジェクト実行と比較してベンチマークします。
- `pnpm test:perf:changed:bench -- --worktree` は、先にコミットせずに現在のworktree変更セットをベンチマークします。
- `pnpm test:perf:profile:main`: VitestメインスレッドのCPUプロファイルを `.artifacts/vitest-main-profile` に書き出します。
- `pnpm test:perf:profile:runner`: unit runnerのCPU + heapプロファイルを `.artifacts/vitest-runner-profile` に書き出します。
- Gateway統合: `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` または `pnpm test:gateway` でオプトインします。
- `pnpm test:e2e`: Gatewayのエンドツーエンドスモークテスト（マルチインスタンスWS/HTTP/node pairing）を実行します。デフォルトでは `vitest.e2e.config.ts` で `threads` + `isolate: false` と適応的workerを使用します。`OPENCLAW_E2E_WORKERS=<n>` で調整し、詳細ログには `OPENCLAW_E2E_VERBOSE=1` を設定してください。
- `pnpm test:live`: プロバイダーliveテスト（minimax/zai）を実行します。APIキーと `LIVE=1`（またはプロバイダー固有の `*_LIVE_TEST=1`）が必要で、これがないとスキップ解除されません。
- `pnpm test:docker:openwebui`: Docker化されたOpenClaw + Open WebUIを起動し、Open WebUI経由でサインインし、`/api/models` を確認してから、`/api/chat/completions` を通る実際のプロキシチャットを実行します。使用可能なliveモデルキー（たとえば `~/.profile` のOpenAI）が必要で、外部のOpen WebUIイメージをpullし、通常のunit/e2eスイートのようにCI安定であることは想定していません。
- `pnpm test:docker:mcp-channels`: シード済みのGatewayコンテナーと、`openclaw mcp serve` を起動する2つ目のクライアントコンテナーを起動し、その後、ルーティングされた会話検出、transcript読み取り、添付メタデータ、liveイベントキュー動作、送信ルーティング、およびClaudeスタイルのチャネル + 権限通知を実際のstdioブリッジ経由で検証します。Claude通知アサーションは生のstdio MCPフレームを直接読み取るため、このスモークはブリッジが実際に出力する内容を反映します。

## ローカルPRゲート

ローカルのPR land/gateチェックでは、次を実行してください:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

`pnpm test` が負荷の高いホストで不安定な場合は、回帰と見なす前に1回再実行し、その後 `pnpm test <path/to/test>` で切り分けてください。メモリ制約のあるホストでは、次を使用してください:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## モデル遅延ベンチ（ローカルキー）

スクリプト: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

使用方法:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 任意の環境変数: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- デフォルトプロンプト: 「Reply with a single word: ok. No punctuation or extra text.」

前回実行（2025-12-31、20回）:

- minimax median 1279ms（min 1114、max 2431）
- opus median 2454ms（min 1224、max 3170）

## CLI起動ベンチ

スクリプト: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

使用方法:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist/entry.js --preset all`
- `pnpm tsx scripts/bench-cli-startup.ts --preset all --output .artifacts/cli-startup-bench-all.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case gatewayStatusJson --output .artifacts/cli-startup-bench-smoke.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --cpu-prof-dir .artifacts/cli-cpu`
- `pnpm tsx scripts/bench-cli-startup.ts --json`

プリセット:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: 両方のプリセット

出力には、各コマンドの `sampleCount`、avg、p50、p95、min/max、exit-code/signal分布、およびmax RSS概要が含まれます。任意の `--cpu-prof-dir` / `--heap-prof-dir` は、実行ごとのV8プロファイルを書き出すため、タイミング測定とプロファイル取得に同じハーネスを使えます。

保存済み出力の規約:

- `pnpm test:startup:bench:smoke` は、対象のスモークアーティファクトを `.artifacts/cli-startup-bench-smoke.json` に書き出します
- `pnpm test:startup:bench:save` は、完全スイートのアーティファクトを `runs=5` と `warmup=1` で `.artifacts/cli-startup-bench-all.json` に書き出します
- `pnpm test:startup:bench:update` は、チェックイン済みのベースラインfixtureを `runs=5` と `warmup=1` で `test/fixtures/cli-startup-bench.json` に更新します

チェックイン済みfixture:

- `test/fixtures/cli-startup-bench.json`
- `pnpm test:startup:bench:update` で更新
- 現在の結果をfixtureと比較するには `pnpm test:startup:bench:check`

## オンボーディングE2E（Docker）

Dockerは任意です。これはコンテナー化されたオンボーディングスモークテストにのみ必要です。

クリーンなLinuxコンテナーでの完全なコールドスタートフロー:

```bash
scripts/e2e/onboard-docker.sh
```

このスクリプトは擬似TTY経由で対話型ウィザードを操作し、config/workspace/sessionファイルを検証してから、Gatewayを起動して `openclaw health` を実行します。

## QRインポートスモーク（Docker）

サポートされるDocker Nodeランタイム（デフォルトのNode 24、互換のNode 22）で `qrcode-terminal` が読み込まれることを確認します:

```bash
pnpm test:docker:qr
```
