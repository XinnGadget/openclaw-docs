---
read_when:
    - qa-lab または qa-channel を拡張する場合
    - リポジトリに基づくQAシナリオを追加する場合
    - Gateway ダッシュボードを中心に、より現実的なQA自動化を構築する場合
summary: qa-lab、qa-channel、シード済みシナリオ、プロトコルレポート向けのプライベートQA自動化の構成
title: QA E2E 自動化
x-i18n:
    generated_at: "2026-04-08T04:41:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 57da147dc06abf9620290104e01a83b42182db1806514114fd9e8467492cda99
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E 自動化

プライベートQAスタックは、単一のユニットテストよりも、
より現実的でチャネルの形に沿った方法でOpenClawを検証することを目的としています。

現在の構成要素:

- `extensions/qa-channel`: DM、channel、thread、
  reaction、edit、delete の各操作面を備えた合成メッセージチャネル。
- `extensions/qa-lab`: トランスクリプトを観察し、
  受信メッセージを注入し、Markdownレポートをエクスポートするための
  デバッガーUIとQAバス。
- `qa/`: キックオフタスクおよびベースラインQA
  シナリオ向けの、リポジトリに基づくシードアセット。

現在のQAオペレーターフローは2ペインのQAサイトです:

- 左: エージェント付きのGateway ダッシュボード（Control UI）。
- 右: Slack風のトランスクリプトとシナリオ計画を表示するQA Lab。

実行方法:

```bash
pnpm qa:lab:up
```

これによりQAサイトがビルドされ、Dockerベースのgatewayレーンが起動し、
オペレーターまたは自動化ループがエージェントにQAミッションを与え、
実際のチャネル動作を観察し、何が機能し、何が失敗し、あるいは
何がブロックされたままだったかを記録できるQA Labページが公開されます。

Dockerイメージを毎回再ビルドせずに、より高速にQA Lab UIを反復開発するには、
bind mountされたQA Labバンドルでスタックを起動します:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` は、Dockerサービスを事前ビルド済みイメージで維持しつつ、
`extensions/qa-lab/web/dist` を `qa-lab` コンテナにbind mountします。`qa:lab:watch`
は変更時にそのバンドルを再ビルドし、QA Labアセットのハッシュが変わると
ブラウザは自動的に再読み込みされます。

## リポジトリに基づくシード

シードアセットは `qa/` にあります:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

これらは意図的にgitに含められており、人間と
エージェントの両方がQA計画を確認できます。ベースライン一覧は、少なくとも次を
カバーできるよう十分に広く保つ必要があります:

- DM と channel のチャット
- thread の動作
- メッセージアクションのライフサイクル
- cron コールバック
- メモリの想起
- モデルの切り替え
- サブエージェントへの引き継ぎ
- リポジトリの読み取りとドキュメントの読み取り
- Lobster Invaders のような小規模なビルドタスク1件

## レポート

`qa-lab` は、観察されたバスタイムラインからMarkdownのプロトコルレポートをエクスポートします。
レポートでは次に答える必要があります:

- 何が機能したか
- 何が失敗したか
- 何がブロックされたままだったか
- どのフォローアップシナリオを追加する価値があるか

## 関連ドキュメント

- [テスト](/ja-JP/help/testing)
- [QAチャネル](/ja-JP/channels/qa-channel)
- [ダッシュボード](/web/dashboard)
