---
read_when:
    - CIジョブが実行された理由、または実行されなかった理由を理解する必要がある
    - 失敗しているGitHub Actionsチェックをデバッグしている
summary: CIジョブグラフ、スコープゲート、およびローカルコマンドの対応関係
title: CIパイプライン
x-i18n:
    generated_at: "2026-04-09T04:41:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: d104f2510fadd674d7952aa08ad73e10f685afebea8d7f19adc1d428e2bdc908
    source_path: ci.md
    workflow: 15
---

# CIパイプライン

CIは`main`へのすべてのpushとすべてのpull requestで実行されます。スマートなスコープ判定を使って、変更が無関係な領域のみに及ぶ場合は高コストなジョブをスキップします。

## ジョブ概要

| ジョブ                     | 目的                                                                                     | 実行されるタイミング                     |
| ------------------------ | -------------------------------------------------------------------------------------- | -------------------------------------- |
| `preflight`              | ドキュメントのみの変更、変更されたスコープ、変更された拡張機能を検出し、CIマニフェストをビルドする | draftではないpushとPRで常に実行          |
| `security-fast`          | 秘密鍵の検出、`zizmor`によるワークフロー監査、本番依存関係の監査                            | draftではないpushとPRで常に実行          |
| `build-artifacts`        | `dist/`とControl UIを一度ビルドし、下流ジョブ向けに再利用可能なアーティファクトをアップロードする | Node関連の変更                          |
| `checks-fast-core`       | バンドル済み/plugin-contract/protocolチェックなどの高速なLinux正当性レーン                 | Node関連の変更                          |
| `checks-fast-extensions` | `checks-fast-extensions-shard`の完了後に拡張機能シャードレーンを集約する                     | Node関連の変更                          |
| `extension-fast`         | 変更されたバンドル済みプラグインのみを対象にした集中テスト                                  | 拡張機能の変更が検出された場合            |
| `check`                  | CIにおけるメインのローカルゲート: `pnpm check` と `pnpm build:strict-smoke`               | Node関連の変更                          |
| `check-additional`       | アーキテクチャ、境界、import-cycleガードに加えて、Gateway watch regression harness         | Node関連の変更                          |
| `build-smoke`            | ビルド済みCLIのスモークテストと起動メモリのスモーク                                         | Node関連の変更                          |
| `checks`                 | より重いLinux Nodeレーン: 完全なテスト、チャネルテスト、push時のみのNode 22互換性            | Node関連の変更                          |
| `check-docs`             | ドキュメントのフォーマット、lint、リンク切れチェック                                        | ドキュメントが変更された場合              |
| `skills-python`          | PythonベースのSkillsに対するRuff + pytest                                              | Python Skills関連の変更                 |
| `checks-windows`         | Windows固有のテストレーン                                                               | Windows関連の変更                       |
| `macos-node`             | 共有のビルド済みアーティファクトを使用するmacOS TypeScriptテストレーン                      | macOS関連の変更                         |
| `macos-swift`            | macOSアプリ向けのSwift lint、ビルド、テスト                                              | macOS関連の変更                         |
| `android`                | Androidのビルドおよびテストマトリクス                                                    | Android関連の変更                       |

## フェイルファスト順序

ジョブは、高コストなものが実行される前に低コストなチェックが失敗するように順序付けされています。

1. `preflight`が、そもそもどのレーンを存在させるかを決定します。`docs-scope`と`changed-scope`のロジックは、このジョブ内のステップであり、独立したジョブではありません。
2. `security-fast`、`check`、`check-additional`、`check-docs`、`skills-python`は、より重いアーティファクトジョブやプラットフォームマトリクスジョブを待たずにすばやく失敗します。
3. `build-artifacts`は高速なLinuxレーンと並行して実行され、共有ビルドの準備ができしだい下流コンシューマーが開始できるようにします。
4. その後、より重いプラットフォームおよびランタイムレーンが分岐します: `checks-fast-core`、`checks-fast-extensions`、`extension-fast`、`checks`、`checks-windows`、`macos-node`、`macos-swift`、`android`。

スコープ判定ロジックは`scripts/ci-changed-scope.mjs`にあり、`src/scripts/ci-changed-scope.test.ts`のユニットテストでカバーされています。
別の`install-smoke`ワークフローは、独自の`preflight`ジョブを通じて同じスコープスクリプトを再利用します。これは、より狭いchanged-smokeシグナルから`run_install_smoke`を計算するため、Docker/install smokeはインストール、パッケージング、コンテナ関連の変更に対してのみ実行されます。

pushでは、`checks`マトリクスにpush時のみの`compat-node22`レーンが追加されます。pull requestでは、このレーンはスキップされ、マトリクスは通常のテスト/チャネルレーンに集中したままになります。

## ランナー

| ランナー                           | ジョブ                                                                                                 |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`、`security-fast`、`build-artifacts`、Linuxチェック、ドキュメントチェック、Python Skills、`android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                     |
| `macos-latest`                   | `macos-node`、`macos-swift`                                                                          |

## ローカルでの対応コマンド

```bash
pnpm check          # 型チェック + lint + フォーマット
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # vitestテスト
pnpm test:channels
pnpm check:docs     # ドキュメントのフォーマット + lint + リンク切れ
pnpm build          # CIのartifact/build-smokeレーンが関係する場合にdistをビルド
```
