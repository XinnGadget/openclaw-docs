---
read_when:
    - qa-labまたはqa-channelを拡張している
    - リポジトリに裏付けられたQAシナリオを追加している
    - Gatewayダッシュボードを中心に、より現実的なQA自動化を構築している
summary: qa-lab、qa-channel、シードシナリオ、プロトコルレポートのための非公開QA自動化の構成
title: QA E2E自動化
x-i18n:
    generated_at: "2026-04-07T04:41:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 113e89d8d3ee8ef3058d95b9aea9a1c2335b07794446be2d231c0faeb044b23b
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E自動化

非公開QAスタックは、単一のユニットテストよりも現実のチャネルに近い形でOpenClawを検証することを目的としています。

現在の構成要素:

- `extensions/qa-channel`: DM、チャネル、スレッド、リアクション、編集、削除の各インターフェースを備えた合成メッセージチャネル。
- `extensions/qa-lab`: 文字起こしの観測、受信メッセージの注入、Markdownレポートのエクスポートを行うためのデバッガーUIとQAバス。
- `qa/`: キックオフタスクとベースラインQAシナリオのための、リポジトリに裏付けられたシードアセット。

現在のQAオペレーターのフローは、2ペインのQAサイトです。

- 左: エージェントを備えたGatewayダッシュボード（Control UI）。
- 右: Slack風の文字起こしとシナリオ計画を表示するQA Lab。

実行方法:

```bash
pnpm qa:lab:up
```

これによりQAサイトがビルドされ、DockerベースのGatewayレーンが起動し、
QA Labページが公開されます。そこでオペレーターまたは自動化ループがエージェントにQA
ミッションを与え、実際のチャネル動作を観察し、何が機能したか、何が失敗したか、
何がブロックされたままだったかを記録できます。

## リポジトリに裏付けられたシード

シードアセットは `qa/` にあります。

- `qa/QA_KICKOFF_TASK.md`
- `qa/seed-scenarios.json`

これらは、QA計画が人間とエージェントの両方から見えるよう、意図的にgitに含められています。ベースラインの一覧は、次をカバーできるよう十分に広いままにしておくべきです。

- DMとチャネルチャット
- スレッド動作
- メッセージアクションのライフサイクル
- cronコールバック
- メモリの想起
- モデル切り替え
- subagentハンドオフ
- リポジトリ読み取りとドキュメント読み取り
- Lobster Invadersのような小さなビルドタスク1件

## レポート

`qa-lab` は、観測されたバスタイムラインからMarkdown形式のプロトコルレポートをエクスポートします。
レポートは次の点に答える必要があります。

- 何が機能したか
- 何が失敗したか
- 何がブロックされたままだったか
- 追加する価値のあるフォローアップシナリオは何か

## 関連ドキュメント

- [Testing](/ja-JP/help/testing)
- [QA Channel](/ja-JP/channels/qa-channel)
- [Dashboard](/web/dashboard)
