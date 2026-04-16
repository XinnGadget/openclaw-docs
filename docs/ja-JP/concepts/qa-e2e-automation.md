---
read_when:
    - qa-labまたはqa-channelの拡張
    - リポジトリ連携のQAシナリオの追加
    - Gatewayダッシュボードを中心とした、より高い現実性を備えたQA自動化の構築
summary: qa-lab、qa-channel、シード済みシナリオ、およびプロトコルレポートのための非公開QA自動化の構成
title: QA E2E自動化
x-i18n:
    generated_at: "2026-04-16T21:51:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7deefda1c90a0d2e21e2155ffd8b585fb999e7416bdbaf0ff57eb33ccc063afc
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E自動化

非公開QAスタックは、単一のユニットテストよりも現実的で、
チャネルの形に近い方法でOpenClawを検証することを目的としています。

現在の構成要素:

- `extensions/qa-channel`: DM、チャネル、スレッド、
  リアクション、編集、削除の各面を備えた合成メッセージチャネル。
- `extensions/qa-lab`: トランスクリプトの観察、
  受信メッセージの注入、Markdownレポートのエクスポートのための
  デバッガUIとQAバス。
- `qa/`: キックオフタスクとベースラインQA
  シナリオのための、リポジトリ連携のシードアセット。

現在のQAオペレーターフローは、2ペインのQAサイトです:

- 左: エージェントを表示するGatewayダッシュボード（Control UI）。
- 右: Slack風のトランスクリプトとシナリオプランを表示するQA Lab。

実行するには:

```bash
pnpm qa:lab:up
```

これによりQAサイトがビルドされ、Dockerベースのgatewayレーンが起動し、
QA Labページが公開されます。そこでは、オペレーターまたは自動化ループが
エージェントにQAミッションを与え、実際のチャネル動作を観察し、
何が機能したか、失敗したか、あるいはブロックされたままだったかを
記録できます。

Dockerイメージを毎回再ビルドせずに、より高速にQA Lab UIを反復開発するには、
バインドマウントされたQA Labバンドルでスタックを起動します:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` は、Dockerサービスを事前ビルド済みイメージ上で維持し、
`extensions/qa-lab/web/dist` を `qa-lab` コンテナにバインドマウントします。
`qa:lab:watch` は変更時にそのバンドルを再ビルドし、QA Labの
アセットハッシュが変わるとブラウザが自動リロードされます。

実際のトランスポートを使うMatrixスモークレーンを実行するには、次を実行します:

```bash
pnpm openclaw qa matrix
```

このレーンは、Docker内に使い捨てのTuwunel homeserverを用意し、
一時的なドライバー、SUT、オブザーバーのユーザーを登録し、
1つのプライベートルームを作成した後、QA gateway child内で
実際のMatrix Pluginを実行します。ライブトランスポートレーンは、
対象トランスポートに限定されたchild configを維持するため、
child config内で `qa-channel` なしにMatrixが実行されます。
構造化されたレポートアーティファクトと、結合されたstdout/stderrログを、
選択したMatrix QA出力ディレクトリに書き込みます。
外側の `scripts/run-node.mjs` のビルド/ランチャー出力も記録するには、
`OPENCLAW_RUN_NODE_OUTPUT_LOG=<path>` をリポジトリローカルのログファイルに設定します。

実際のトランスポートを使うTelegramスモークレーンを実行するには、次を実行します:

```bash
pnpm openclaw qa telegram
```

このレーンは、使い捨てサーバーを用意する代わりに、
1つの実在するプライベートTelegramグループを対象にします。
これには `OPENCLAW_QA_TELEGRAM_GROUP_ID`、
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`、
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN` が必要であり、
さらに同じプライベートグループ内に2つの異なるボットが必要です。
SUTボットにはTelegramユーザー名が必要であり、
ボット間観測は、両方のボットで `@BotFather` の
Bot-to-Bot Communication Mode が有効になっていると最適に機能します。

ライブトランスポートレーンは現在、各レーンが独自のシナリオリスト形状を
作るのではなく、より小さな1つの共通契約を共有します:

`qa-channel` は、引き続き幅広い合成プロダクト動作スイートであり、
ライブトランスポートのカバレッジマトリクスには含まれません。

| レーン | Canary | メンションゲーティング | 許可リストブロック | トップレベル返信 | 再起動後の復帰 | スレッド追従 | スレッド分離 | リアクション観測 | helpコマンド |
| -------- | ------ | -------------- | --------------- | --------------- | -------------- | ---------------- | ---------------- | -------------------- | ------------ |
| Matrix   | x      | x              | x               | x               | x              | x                | x                | x                    |              |
| Telegram | x      |                |                 |                 |                |                  |                  |                      | x            |

これにより、`qa-channel` は引き続き幅広いプロダクト動作スイートとして維持され、
一方でMatrix、Telegram、および今後のライブトランスポートは、
明示的な1つのトランスポート契約チェックリストを共有します。

DockerをQAパスに持ち込まずに、使い捨てLinux VMレーンを実行するには、
次を実行します:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

これにより、新しいMultipassゲストが起動し、依存関係をインストールし、
ゲスト内でOpenClawをビルドし、`qa suite` を実行した後、
通常のQAレポートとサマリーをホスト上の `.artifacts/qa-e2e/...` に
コピーし戻します。
シナリオ選択動作は、ホスト上の `qa suite` と同じものを再利用します。
ホストとMultipassのsuite実行はどちらも、
デフォルトで分離されたgateway workerを使って、
選択された複数のシナリオを並列実行します。上限は64 workerまたは
選択シナリオ数です。worker数を調整するには `--concurrency <count>` を使い、
直列実行するには `--concurrency 1` を使います。
ライブ実行では、ゲストにとって実用的なサポート済みQA認証入力が転送されます:
envベースのプロバイダーキー、QA live provider config path、
および存在する場合の `CODEX_HOME` です。ゲストが
マウントされたworkspace経由で書き戻せるよう、
`--output-dir` はリポジトリルート配下に維持してください。

## リポジトリ連携シード

シードアセットは `qa/` にあります:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

これらは意図的にgitに置かれており、QAプランが人間にも
エージェントにも見えるようになっています。

`qa-lab` は汎用的なmarkdownランナーとして維持するべきです。
各シナリオMarkdownファイルは、1回のテスト実行における
信頼できる唯一の情報源であり、次を定義する必要があります:

- シナリオメタデータ
- docsおよびコード参照
- 任意のPlugin要件
- 任意のgateway config patch
- 実行可能な `qa-flow`

`qa-flow` を支える再利用可能なランタイム面は、
汎用かつ横断的なままで構いません。たとえば、Markdownシナリオは、
特別扱いのランナーを追加することなく、
トランスポート側ヘルパーと、Gatewayの `browser.request` seam を通じて
埋め込みControl UIを操作するブラウザ側ヘルパーを組み合わせられます。

ベースラインリストは、次をカバーできる程度に十分広く維持するべきです:

- DMおよびチャネルチャット
- スレッド動作
- メッセージアクションのライフサイクル
- Cronコールバック
- メモリ想起
- モデル切り替え
- サブエージェントのハンドオフ
- リポジトリ読み取りとdocs読み取り
- Lobster Invadersのような小さなビルドタスクを1つ

## トランスポートアダプター

`qa-lab` はMarkdown QAシナリオ向けの汎用トランスポートseamを持ちます。
`qa-channel` はそのseam上の最初のアダプターですが、
設計上の目標はより広いものです:
今後の実在または合成チャネルは、
トランスポート固有のQAランナーを追加するのではなく、
同じsuiteランナーに接続されるべきです。

アーキテクチャレベルでの分割は次のとおりです:

- `qa-lab` は、汎用シナリオ実行、worker並列性、アーティファクト書き込み、レポート作成を担当します。
- トランスポートアダプターは、gateway config、準備完了、受信および送信の観測、トランスポートアクション、正規化されたトランスポート状態を担当します。
- `qa/scenarios/` 配下のMarkdownシナリオファイルがテスト実行を定義し、それを実行する再利用可能なランタイム面は `qa-lab` が提供します。

新しいチャネルアダプター向けのメンテナー向け導入ガイダンスは、
[Testing](/ja-JP/help/testing#adding-a-channel-to-qa) にあります。

## レポート

`qa-lab` は、観測されたバスタイムラインからMarkdownの
プロトコルレポートをエクスポートします。
レポートは次に答えるべきです:

- 何が機能したか
- 何が失敗したか
- 何がブロックされたままだったか
- どのフォローアップシナリオを追加する価値があるか

キャラクターおよびスタイルのチェックには、同じシナリオを複数の
ライブモデル参照で実行し、評価済みMarkdownレポートを書き出します:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

このコマンドはDockerではなく、ローカルのQA gateway child processを実行します。
character evalシナリオでは、`SOUL.md` を通じてペルソナを設定し、
その後、チャット、workspaceヘルプ、小さなファイルタスクのような
通常のユーザーターンを実行するべきです。
候補モデルには、それが評価されていることを伝えないでください。
このコマンドは各完全トランスクリプトを保持し、基本的な実行統計を記録し、
その後judge modelに対して、`xhigh` 推論付きのfast modeで、
自然さ、雰囲気、ユーモアに基づいて実行結果を順位付けするよう求めます。
プロバイダーを比較する場合は `--blind-judge-models` を使ってください:
judge promptには引き続きすべてのトランスクリプトと実行状態が渡されますが、
候補参照は `candidate-01` のような中立的ラベルに置き換えられます。
レポートは、解析後に順位を実際の参照へマッピングし直します。
候補実行のデフォルトは `high` thinking であり、
それをサポートするOpenAIモデルでは `xhigh` になります。
特定の候補を個別に上書きするには、
`--model provider/model,thinking=<level>` を使います。
`--thinking <level>` は引き続きグローバルなフォールバックを設定し、
従来の `--model-thinking <provider/model=level>` 形式も
互換性のため維持されています。
OpenAIの候補参照はデフォルトでfast modeとなり、
プロバイダーが対応している場合は優先処理が使われます。
単一の候補またはjudgeに対して上書きが必要な場合は、
`,fast`、`,no-fast`、または `,fast=false` をインラインで追加してください。
すべての候補モデルに対してfast modeを強制したい場合にのみ、
`--fast` を渡してください。候補とjudgeの所要時間は、
ベンチマーク分析のためレポートに記録されますが、
judge promptでは速度で順位付けしないよう明示されます。
候補モデル実行とjudge model実行はどちらもデフォルトで並列数16です。
プロバイダー制限やローカルgateway負荷によって実行が
ノイジーになりすぎる場合は、`--concurrency` または
`--judge-concurrency` を下げてください。
候補の `--model` が渡されない場合、character evalのデフォルトは
`openai/gpt-5.4`、`openai/gpt-5.2`、`openai/gpt-5`、`anthropic/claude-opus-4-6`、
`anthropic/claude-sonnet-4-6`、`zai/glm-5.1`、
`moonshot/kimi-k2.5`、
`google/gemini-3.1-pro-preview` です。
judgeの `--judge-model` が渡されない場合、judgeのデフォルトは
`openai/gpt-5.4,thinking=xhigh,fast` と
`anthropic/claude-opus-4-6,thinking=high` です。

## 関連docs

- [Testing](/ja-JP/help/testing)
- [QA Channel](/ja-JP/channels/qa-channel)
- [Dashboard](/web/dashboard)
