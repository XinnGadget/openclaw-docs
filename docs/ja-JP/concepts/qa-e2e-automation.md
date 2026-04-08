---
read_when:
    - qa-labまたはqa-channelを拡張する場合
    - リポジトリに裏付けられたQAシナリオを追加する場合
    - Gatewayダッシュボード周辺で、より現実に近いQA自動化を構築する場合
summary: qa-lab、qa-channel、シード済みシナリオ、プロトコルレポート向けのプライベートQA自動化の構成
title: QA E2E自動化
x-i18n:
    generated_at: "2026-04-08T02:13:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b4aa5acc8e77303f4045d4f04372494cae21b89d2fdaba856dbb4855ced9d27
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E自動化

プライベートQAスタックは、単一のユニットテストよりも、より現実的で
チャネルに近い形でOpenClawを検証することを目的としています。

現在の構成要素:

- `extensions/qa-channel`: DM、channel、thread、
  reaction、edit、deleteの各操作面を備えた合成メッセージチャネル。
- `extensions/qa-lab`: トランスクリプトの観察、
  受信メッセージの注入、Markdownレポートのエクスポートを行うためのデバッガーUIとQAバス。
- `qa/`: キックオフタスクとベースラインQA
  シナリオ向けの、リポジトリに裏付けられたシードアセット。

現在のQAオペレーターのフローは、2ペインのQAサイトです:

- 左: エージェントを備えたGatewayダッシュボード（Control UI）。
- 右: Slack風のトランスクリプトとシナリオ計画を表示するQA Lab。

次のコマンドで実行します:

```bash
pnpm qa:lab:up
```

これによりQAサイトがビルドされ、DockerベースのGatewayレーンが起動し、
オペレーターまたは自動化ループがエージェントにQA
ミッションを与え、実際のチャネル動作を観察し、成功したこと、失敗したこと、
またはブロックされたままのことを記録できるQA Labページが公開されます。

Dockerイメージを毎回再ビルドせずにQA Lab UIをより高速に反復するには、
bind mountしたQA Labバンドルでスタックを起動します:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` は、事前ビルド済みイメージ上でDockerサービスを維持しつつ、
`extensions/qa-lab/web/dist` を `qa-lab` コンテナにbind mountします。`qa:lab:watch`
は変更時にそのバンドルを再ビルドし、QA Labアセットのハッシュが変わると
ブラウザは自動的にリロードされます。

## リポジトリに裏付けられたシード

シードアセットは `qa/` にあります:

- `qa/scenarios.md`

これらは、QA計画が人間と
エージェントの両方から見えるように、意図的にgitに置かれています。
ベースラインの一覧は、次をカバーできる程度に十分広く保つ必要があります:

- DMとchannelチャット
- threadの動作
- メッセージアクションのライフサイクル
- cronコールバック
- メモリの再呼び出し
- モデル切り替え
- サブエージェントへの引き継ぎ
- リポジトリ読み取りとドキュメント読み取り
- Lobster Invadersのような小さなビルドタスクを1つ

## レポート

`qa-lab` は、観測されたバスタイムラインからMarkdownのプロトコルレポートをエクスポートします。
レポートは次の問いに答える必要があります:

- 何がうまく動作したか
- 何が失敗したか
- 何がブロックされたままだったか
- どのフォローアップシナリオを追加する価値があるか

## 関連ドキュメント

- [Testing](/ja-JP/help/testing)
- [QA Channel](/ja-JP/channels/qa-channel)
- [Dashboard](/web/dashboard)
