---
read_when:
    - CI ジョブが実行された、または実行されなかった理由を理解する必要があります
    - 失敗している GitHub Actions チェックをデバッグしています
summary: CI ジョブグラフ、スコープゲート、および対応するローカルコマンド
title: CI パイプライン
x-i18n:
    generated_at: "2026-04-11T02:44:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca7e355b7f73bfe8ea8c6971e78164b8b2e68cbb27966964955e267fed89fce6
    source_path: ci.md
    workflow: 15
---

# CI パイプライン

CI は `main` へのすべての push とすべての pull request で実行されます。スマートなスコープ判定を使用して、変更が無関係な領域のみに限定される場合は高コストなジョブをスキップします。

## ジョブ概要

| ジョブ                     | 目的                                                                                   | 実行されるタイミング                    |
| ------------------------ | ------------------------------------------------------------------------------------ | ----------------------------- |
| `preflight`              | docs のみの変更、変更されたスコープ、変更された拡張機能を検出し、CI マニフェストを構築する | draft ではない push と PR で常に実行 |
| `security-fast`          | 秘密鍵の検出、`zizmor` によるワークフロー監査、本番依存関係の監査                        | draft ではない push と PR で常に実行 |
| `build-artifacts`        | `dist/` と Control UI を一度だけビルドし、下流ジョブ向けに再利用可能な成果物をアップロードする | Node 関連の変更                    |
| `checks-fast-core`       | bundled/plugin-contract/protocol チェックなどの高速な Linux 正当性レーン            | Node 関連の変更                    |
| `checks-node-extensions` | 拡張機能スイート全体にわたる bundled-plugin テストの完全なシャード                      | Node 関連の変更                    |
| `checks-node-core-test`  | channel、bundled、contract、extension レーンを除く、Core Node テストのシャード          | Node 関連の変更                    |
| `extension-fast`         | 変更された bundled plugins のみに対する集中テスト                                      | extension の変更が検出された場合     |
| `check`                  | CI におけるメインのローカルゲート: `pnpm check` と `pnpm build:strict-smoke`           | Node 関連の変更                    |
| `check-additional`       | アーキテクチャ、境界、import-cycle ガードに加え、Gateway watch regression ハーネス         | Node 関連の変更                    |
| `build-smoke`            | ビルド済み CLI のスモークテストと起動時メモリのスモーク                                  | Node 関連の変更                    |
| `checks`                 | 残りの Linux Node レーン: channel テストと、push のみの Node 22 互換性                  | Node 関連の変更                    |
| `check-docs`             | docs のフォーマット、lint、リンク切れチェック                                           | docs に変更がある場合              |
| `skills-python`          | Python ベースの Skills 向け Ruff + pytest                                              | Python Skills 関連の変更           |
| `checks-windows`         | Windows 固有のテストレーン                                                                  | Windows 関連の変更                 |
| `macos-node`             | 共有ビルド成果物を使用する macOS TypeScript テストレーン                                  | macOS 関連の変更                   |
| `macos-swift`            | macOS アプリ向けの Swift lint、build、tests                                             | macOS 関連の変更                   |
| `android`                | Android の build および test マトリクス                                                 | Android 関連の変更                |

## フェイルファスト順序

ジョブは、コストの低いチェックが高コストなジョブより先に失敗するように順序付けられています。

1. `preflight` が、どのレーンをそもそも存在させるかを決定します。`docs-scope` と `changed-scope` のロジックは独立したジョブではなく、このジョブ内のステップです。
2. `security-fast`、`check`、`check-additional`、`check-docs`、`skills-python` は、より重い artifact や platform matrix ジョブを待たずに素早く失敗します。
3. `build-artifacts` は高速な Linux レーンと並行して動作するため、共有ビルドの準備ができ次第、下流の利用側が開始できます。
4. その後、より重い platform および runtime レーンがファンアウトします: `checks-fast-core`、`checks-node-extensions`、`checks-node-core-test`、`extension-fast`、`checks`、`checks-windows`、`macos-node`、`macos-swift`、`android`。

スコープロジックは `scripts/ci-changed-scope.mjs` にあり、`src/scripts/ci-changed-scope.test.ts` のユニットテストでカバーされています。
別個の `install-smoke` ワークフローは、独自の `preflight` ジョブを通じて同じスコープスクリプトを再利用します。これは、より狭い changed-smoke シグナルから `run_install_smoke` を算出するため、Docker/install smoke は install、packaging、container 関連の変更に対してのみ実行されます。

push では、`checks` マトリクスに push 専用の `compat-node22` レーンが追加されます。pull request では、そのレーンはスキップされ、マトリクスは通常の test/channel レーンに集中したままになります。

## ランナー

| ランナー                           | ジョブ                                                                                                   |
| -------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`、`security-fast`、`build-artifacts`、Linux checks、docs checks、Python skills、`android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                       |
| `macos-latest`                   | `macos-node`、`macos-swift`                                                                            |

## 対応するローカルコマンド

```bash
pnpm check          # 型チェック + lint + format
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # vitest テスト
pnpm test:channels
pnpm check:docs     # docs の format + lint + broken links
pnpm build          # CI の artifact/build-smoke レーンが関係する場合に dist をビルド
```
