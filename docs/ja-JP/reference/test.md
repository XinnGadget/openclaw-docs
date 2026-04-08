---
read_when:
    - テストを実行または修正する場合
summary: ローカルでのテスト実行方法（vitest）と force / coverage モードを使うタイミング
title: テスト
x-i18n:
    generated_at: "2026-04-08T02:19:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: f7c19390f7577b3a29796c67514c96fe4c86c9fa0c7686cd4e377c6e31dcd085
    source_path: reference/test.md
    workflow: 15
---

# テスト

- 完全なテストキット（スイート、live、Docker）: [Testing](/ja-JP/help/testing)

- `pnpm test:force`: デフォルトの control ポートを保持している残存 Gateway プロセスを強制終了し、その後、分離された Gateway ポートで完全な Vitest スイートを実行します。これにより、サーバーテストが実行中インスタンスと衝突しないようにします。以前の Gateway 実行でポート 18789 が使用されたままになっている場合に使ってください。
- `pnpm test:coverage`: V8 coverage 付きで unit スイートを実行します（`vitest.unit.config.ts` 経由）。グローバルしきい値は lines / branches / functions / statements で 70% です。coverage からは、統合の重いエントリポイント（CLI 配線、Gateway / Telegram ブリッジ、webchat 静的サーバー）を除外し、unit-test 可能なロジックに対象を絞っています。
- `pnpm test:coverage:changed`: `origin/main` 以降に変更されたファイルだけを対象に unit coverage を実行します。
- `pnpm test:changed`: 変更差分がルーティング可能な source / test ファイルだけに触れている場合、変更された git パスをスコープ付き Vitest レーンに展開します。config / setup の変更は、必要に応じて配線変更を広く再実行できるよう、引き続きネイティブな root projects 実行にフォールバックします。
- `pnpm test`: 明示的な file / directory ターゲットをスコープ付き Vitest レーンにルーティングします。ターゲット未指定の実行では、1 つの巨大な root-project プロセスの代わりに、11 個の連続 shard config（`vitest.full-core-unit-src.config.ts`、`vitest.full-core-unit-security.config.ts`、`vitest.full-core-unit-ui.config.ts`、`vitest.full-core-unit-support.config.ts`、`vitest.full-core-support-boundary.config.ts`、`vitest.full-core-contracts.config.ts`、`vitest.full-core-bundled.config.ts`、`vitest.full-core-runtime.config.ts`、`vitest.full-agentic.config.ts`、`vitest.full-auto-reply.config.ts`、`vitest.full-extensions.config.ts`）を実行するようになりました。
- 一部の `plugin-sdk` と `commands` のテストファイルは、`test/setup.ts` だけを残す専用の軽量レーンにルーティングされるようになり、ランタイムの重いケースは従来のレーンに残ります。
- 一部の `plugin-sdk` と `commands` のヘルパーソースファイルも、`pnpm test:changed` でそれらの軽量レーン内の明示的な sibling テストにマップされるため、小さなヘルパー修正で重いランタイム依存スイート全体を再実行せずに済みます。
- `auto-reply` も 3 つの専用 config（`core`、`top-level`、`reply`）に分割され、reply ハーネスが軽量な top-level の status / token / helper テストを支配しないようになりました。
- ベースの Vitest config は、repo 全体の config で共有の非分離 runner を有効にした上で、デフォルトで `pool: "threads"` と `isolate: false` を使用します。
- `pnpm test:channels` は `vitest.channels.config.ts` を実行します。
- `pnpm test:extensions` は `vitest.extensions.config.ts` を実行します。
- `pnpm test:extensions`: 拡張機能 / プラグインのスイートを実行します。
- `pnpm test:perf:imports`: Vitest の import-duration + import-breakdown レポートを有効にしつつ、明示的な file / directory ターゲットには引き続きスコープ付きレーンルーティングを使用します。
- `pnpm test:perf:imports:changed`: 同じ import プロファイリングを、`origin/main` 以降に変更されたファイルに対してのみ実行します。
- `pnpm test:perf:changed:bench -- --ref <git-ref>`: 同じコミット済み git diff に対して、ルーティングされた changed-mode 経路をネイティブな root-project 実行とベンチマーク比較します。
- `pnpm test:perf:changed:bench -- --worktree`: 事前にコミットせず、現在の worktree の変更セットをベンチマークします。
- `pnpm test:perf:profile:main`: Vitest メインスレッドの CPU プロファイルを書き出します（`.artifacts/vitest-main-profile`）。
- `pnpm test:perf:profile:runner`: unit runner の CPU + heap プロファイルを書き出します（`.artifacts/vitest-runner-profile`）。
- Gateway integration: `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` または `pnpm test:gateway` で opt-in します。
- `pnpm test:e2e`: Gateway の end-to-end スモークテスト（マルチインスタンス WS / HTTP / node pairing）を実行します。デフォルトでは `vitest.e2e.config.ts` で適応型 worker を使った `threads` + `isolate: false` になっており、`OPENCLAW_E2E_WORKERS=<n>` で調整でき、詳細ログが必要なら `OPENCLAW_E2E_VERBOSE=1` を設定します。
- `pnpm test:live`: プロバイダーの live テスト（minimax / zai）を実行します。スキップ解除には API キーと `LIVE=1`（またはプロバイダー固有の `*_LIVE_TEST=1`）が必要です。
- `pnpm test:docker:openwebui`: Docker 化された OpenClaw + Open WebUI を起動し、Open WebUI 経由でサインインし、`/api/models` を確認した後、`/api/chat/completions` を通した実際のプロキシチャットを実行します。利用可能な live モデルキー（たとえば `~/.profile` の OpenAI）が必要で、外部の Open WebUI イメージを pull し、通常の unit / e2e スイートのように CI 安定であることは想定されていません。
- `pnpm test:docker:mcp-channels`: シード済み Gateway コンテナと、`openclaw mcp serve` を起動する 2 つ目のクライアントコンテナを起動し、その後、ルーティングされた会話検出、transcript 読み取り、添付ファイル metadata、live event queue 動作、outbound send routing、そして実際の stdio ブリッジ上での Claude 形式の channel + permission 通知を検証します。Claude 通知アサーションは生の stdio MCP フレームを直接読み取るため、このスモークはブリッジが実際に出力する内容を反映します。

## ローカル PR ゲート

ローカルでの PR land / gate チェックでは、次を実行してください。

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

`pnpm test` が高負荷のホストでフレークした場合は、回帰と判断する前に 1 回再実行し、その後 `pnpm test <path/to/test>` で切り分けてください。メモリ制約のあるホストでは、次を使用してください。

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## モデル遅延ベンチ（ローカルキー）

スクリプト: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

使い方:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- 任意の env: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- デフォルトプロンプト: 「Reply with a single word: ok. No punctuation or extra text.」

前回の実行結果（2025-12-31、20 回）:

- minimax の中央値 1279ms（最小 1114、最大 2431）
- opus の中央値 2454ms（最小 1224、最大 3170）

## CLI 起動ベンチ

スクリプト: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

使い方:

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

出力には、各コマンドごとの `sampleCount`、avg、p50、p95、min / max、exit-code / signal 分布、および max RSS サマリーが含まれます。任意の `--cpu-prof-dir` / `--heap-prof-dir` を指定すると、実行ごとの V8 プロファイルが書き出されるため、計測とプロファイル取得に同じハーネスを使えます。

保存済み出力の規約:

- `pnpm test:startup:bench:smoke` は対象のスモークアーティファクトを `.artifacts/cli-startup-bench-smoke.json` に書き出します
- `pnpm test:startup:bench:save` は `runs=5` と `warmup=1` を使って、完全スイートのアーティファクトを `.artifacts/cli-startup-bench-all.json` に書き出します
- `pnpm test:startup:bench:update` は `runs=5` と `warmup=1` を使って、チェックイン済みベースライン fixture を `test/fixtures/cli-startup-bench.json` に更新します

チェックイン済み fixture:

- `test/fixtures/cli-startup-bench.json`
- 更新: `pnpm test:startup:bench:update`
- 現在の結果を fixture と比較: `pnpm test:startup:bench:check`

## オンボーディング E2E（Docker）

Docker は任意です。これはコンテナ化されたオンボーディングスモークテストでのみ必要です。

クリーンな Linux コンテナでの完全なコールドスタートフロー:

```bash
scripts/e2e/onboard-docker.sh
```

このスクリプトは擬似 tty 経由で対話型ウィザードを実行し、config / workspace / session ファイルを検証した後、Gateway を起動して `openclaw health` を実行します。

## QR import スモーク（Docker）

サポートされる Docker Node ランタイム（デフォルトの Node 24、互換の Node 22）で `qrcode-terminal` が読み込まれることを確認します。

```bash
pnpm test:docker:qr
```
