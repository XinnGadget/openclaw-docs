---
read_when:
    - qa-labまたはqa-channelの拡張
    - リポジトリ連動のQAシナリオを追加する
    - Gatewayダッシュボードを中心に、より高い現実性のQA自動化を構築する
summary: qa-lab、qa-channel、シード済みシナリオ、プロトコルレポート向けの非公開QA自動化の構成
title: QA E2E自動化
x-i18n:
    generated_at: "2026-04-17T04:43:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 51f97293c184d7c04c95d9858305668fbc0f93273f587ec7e54896ad5d603ab0
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E自動化

非公開のQAスタックは、単一のユニットテストよりも現実的で、
チャネルに近い形でOpenClawを検証することを目的としています。

現在の構成要素:

- `extensions/qa-channel`: DM、チャネル、スレッド、
  リアクション、編集、削除の操作面を備えた合成メッセージチャネル。
- `extensions/qa-lab`: トランスクリプトの観察、
  受信メッセージの注入、Markdownレポートのエクスポートを行うための
  デバッガUIとQAバス。
- `qa/`: キックオフタスクとベースラインQA
  シナリオのための、リポジトリ連動のシードアセット。

現在のQAオペレーターフローは、2ペインのQAサイトです:

- 左: エージェントを表示するGatewayダッシュボード（Control UI）。
- 右: Slack風のトランスクリプトとシナリオ計画を表示するQA Lab。

実行方法:

```bash
pnpm qa:lab:up
```

これによりQAサイトがビルドされ、Dockerベースのgatewayレーンが起動し、
オペレーターまたは自動化ループがエージェントにQAミッションを与え、
実際のチャネル動作を観察し、何が機能し、何が失敗し、
何がブロックされたままだったかを記録できるQA Labページが公開されます。

Dockerイメージを毎回再ビルドせずにQA Lab UIをより高速に反復するには、
QA Labバンドルをバインドマウントしてスタックを起動します:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` は、Dockerサービスを事前ビルド済みイメージ上で維持しつつ、
`extensions/qa-lab/web/dist` を `qa-lab` コンテナにバインドマウントします。
`qa:lab:watch` は変更時にそのバンドルを再ビルドし、
QA Labアセットのハッシュが変わるとブラウザは自動リロードされます。

実際のトランスポートを使うMatrixスモークレーンを実行するには、次を使用します:

```bash
pnpm openclaw qa matrix
```

このレーンは、Docker内に使い捨てのTuwunelホームサーバーを用意し、
一時的なdriver、SUT、observerユーザーを登録し、1つのプライベートルームを作成してから、
QA gateway child内で実際のMatrix Pluginを実行します。ライブトランスポートレーンは、
child configをテスト対象のトランスポートに限定した状態に保つため、
Matrixはchild config内で`qa-channel`なしで動作します。
構造化レポートアーティファクトと、stdout/stderrを結合したログは、
選択したMatrix QA出力ディレクトリに書き込まれます。
外側の `scripts/run-node.mjs` のビルド/ランチャー出力も取得するには、
`OPENCLAW_RUN_NODE_OUTPUT_LOG=<path>` をリポジトリ内のログファイルに設定してください。

実際のトランスポートを使うTelegramスモークレーンを実行するには、次を使用します:

```bash
pnpm openclaw qa telegram
```

このレーンは、使い捨てサーバーを用意する代わりに、
1つの実在するプライベートTelegramグループを対象にします。
必要なのは `OPENCLAW_QA_TELEGRAM_GROUP_ID`、
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`、
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`、
および同じプライベートグループ内にある2つの異なるボットです。
SUTボットにはTelegramユーザー名が必要で、
ボット間観察は、両方のボットで `@BotFather` の
Bot-to-Bot Communication Mode を有効にしていると最も良好に動作します。

ライブトランスポートレーンは現在、それぞれが独自のシナリオリスト形状を考案するのではなく、
より小さな1つの共通契約を共有します:

`qa-channel` は引き続き幅広い合成プロダクト動作スイートであり、
ライブトランスポートのカバレッジマトリクスには含まれません。

| レーン | Canary | メンションゲーティング | Allowlistブロック | トップレベル返信 | 再起動後の再開 | スレッド継続返信 | スレッド分離 | リアクション観察 | ヘルプコマンド |
| -------- | ------ | -------------- | --------------- | --------------- | -------------- | ---------------- | ---------------- | -------------------- | ------------ |
| Matrix   | x      | x              | x               | x               | x              | x                | x                | x                    |              |
| Telegram | x      |                |                 |                 |                |                  |                  |                      | x            |

これにより、`qa-channel` は幅広いプロダクト動作スイートとして維持される一方で、
Matrix、Telegram、将来のライブトランスポートは、
明示的なトランスポート契約チェックリストを共有できます。

DockerをQAパスに持ち込まずに、
使い捨てLinux VMレーンを実行するには、次を使用します:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

これにより新しいMultipassゲストが起動し、依存関係をインストールし、
ゲスト内でOpenClawをビルドし、`qa suite` を実行したうえで、
通常のQAレポートとサマリーをホスト上の `.artifacts/qa-e2e/...` にコピーして戻します。
シナリオ選択の挙動は、ホスト上の `qa suite` と同じものを再利用します。
ホスト実行とMultipassスイート実行はどちらも、
デフォルトで分離されたgateway workerを使って複数の選択シナリオを並列実行し、
最大64 workerまたは選択シナリオ数のいずれか小さい方まで使用します。
worker数を調整するには `--concurrency <count>` を使い、
直列実行には `--concurrency 1` を使ってください。
ライブ実行では、ゲストにとって実用的なサポート対象のQA認証入力が転送されます:
envベースのプロバイダーキー、QAライブプロバイダー設定パス、
および存在する場合の `CODEX_HOME` です。
ゲストがマウントされたワークスペースを通じて書き戻せるよう、
`--output-dir` はリポジトリルート配下に置いてください。

## リポジトリ連動のシード

シードアセットは `qa/` にあります:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

これらは意図的にgitに置かれており、
QA計画が人間とエージェントの両方から見えるようになっています。

`qa-lab` は汎用的なMarkdownランナーのままであるべきです。
各シナリオMarkdownファイルは1回のテスト実行の信頼できる唯一の情報源であり、
次を定義する必要があります:

- シナリオメタデータ
- docsおよびコード参照
- 任意のPlugin要件
- 任意のgateway configパッチ
- 実行可能な `qa-flow`

`qa-flow` を支える再利用可能なランタイム面は、
汎用的かつ横断的なままでかまいません。たとえば、
Markdownシナリオは、埋め込みControl UIをGatewayの
`browser.request` シーム経由で操作するブラウザ側ヘルパーと、
トランスポート側ヘルパーを組み合わせてもよく、
そのために特別扱いのランナーを追加する必要はありません。

ベースライン一覧は、少なくとも次をカバーできるだけの広さを保つべきです:

- DMとチャネルチャット
- スレッド動作
- メッセージアクションのライフサイクル
- Cronコールバック
- メモリーの再呼び出し
- モデル切り替え
- サブエージェントへのハンドオフ
- リポジトリ読解とdocs読解
- Lobster Invadersのような小さなビルドタスク1件

## プロバイダーモックレーン

`qa suite` には2つのローカルプロバイダーモックレーンがあります:

- `mock-openai` は、シナリオ認識型のOpenClawモックです。
  これは、リポジトリ連動QAと同等性ゲート向けの、
  既定の決定論的モックレーンのままです。
- `aimock` は、実験的なプロトコル、
  フィクスチャ、record/replay、chaosカバレッジのために
  AIMockベースのプロバイダーサーバーを起動します。
  これは追加的なものであり、`mock-openai` の
  シナリオディスパッチャーを置き換えるものではありません。

プロバイダーレーンの実装は `extensions/qa-lab/src/providers/` 配下にあります。
各プロバイダーは、自身のデフォルト値、ローカルサーバー起動、
gateway model config、auth-profileのステージング要件、
およびlive/mockの機能フラグを持ちます。
共有スイートとgatewayコードは、プロバイダー名で分岐するのではなく、
プロバイダーレジストリを経由してルーティングするべきです。

## トランスポートアダプター

`qa-lab` はMarkdown QAシナリオ向けの汎用トランスポートシームを所有します。
`qa-channel` はそのシーム上の最初のアダプターですが、
設計目標はより広いものです:
将来の実チャネルまたは合成チャネルも、
トランスポート固有のQAランナーを追加するのではなく、
同じスイートランナーに接続できるようにするべきです。

アーキテクチャレベルでは、分担は次のとおりです:

- `qa-lab` は、汎用シナリオ実行、worker並列性、アーティファクト書き込み、レポート作成を所有する。
- トランスポートアダプターは、gateway config、準備完了、受信および送信の観察、トランスポートアクション、正規化されたトランスポート状態を所有する。
- `qa/scenarios/` 配下のMarkdownシナリオファイルがテスト実行を定義し、`qa-lab` がそれを実行する再利用可能なランタイム面を提供する。

新しいチャネルアダプター向けのメンテナー向け採用ガイダンスは、
[Testing](/ja-JP/help/testing#adding-a-channel-to-qa) にあります。

## レポート

`qa-lab` は、観察されたバスタイムラインからMarkdownのプロトコルレポートをエクスポートします。
このレポートは次に答えるべきです:

- 何がうまくいったか
- 何が失敗したか
- 何がブロックされたままだったか
- どのフォローアップシナリオを追加する価値があるか

キャラクター性とスタイルのチェックについては、
同じシナリオを複数のライブモデル参照で実行し、
評価済みMarkdownレポートを書き出します:

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
character evalシナリオは `SOUL.md` を通じてペルソナを設定し、
その後、チャット、ワークスペースヘルプ、
小さなファイルタスクのような通常のユーザーターンを実行するべきです。
候補モデルには、評価中であることを知らせてはいけません。
このコマンドは各完全トランスクリプトを保持し、
基本的な実行統計を記録したうえで、
judge modelに対して、fast modeかつ `xhigh` 推論で、
自然さ、雰囲気、ユーモアによって実行結果を順位付けさせます。
プロバイダーを比較するときは `--blind-judge-models` を使用してください:
judge promptは引き続きすべてのトランスクリプトと実行状態を受け取りますが、
候補参照は `candidate-01` のような中立ラベルに置き換えられます。
レポートはパース後に順位を実際の参照へマッピングし直します。
候補実行はデフォルトで `high` thinking を使用し、
それをサポートするOpenAIモデルでは `xhigh` を使用します。
特定の候補を上書きするには、
`--model provider/model,thinking=<level>` をインラインで指定してください。
`--thinking <level>` は引き続きグローバルなフォールバックを設定し、
古い `--model-thinking <provider/model=level>` 形式も
互換性のため維持されています。
OpenAI候補参照はデフォルトでfast modeになっており、
プロバイダーがサポートしている場合は優先処理が使われます。
単一の候補またはjudgeで上書きが必要な場合は、
`,fast`、`,no-fast`、または `,fast=false` をインラインで追加してください。
すべての候補モデルでfast modeを強制的に有効にしたい場合にのみ、
`--fast` を渡してください。
候補とjudgeの実行時間はベンチマーク分析のためレポートに記録されますが、
judge promptでは速度で順位付けしないよう明示されています。
候補とjudgeのモデル実行は、どちらもデフォルトで並列数16です。
プロバイダー制限またはローカルgatewayの負荷により実行のノイズが大きすぎる場合は、
`--concurrency` または `--judge-concurrency` を下げてください。
候補の `--model` が指定されていない場合、
character evalのデフォルトは
`openai/gpt-5.4`、`openai/gpt-5.2`、`openai/gpt-5`、
`anthropic/claude-opus-4-6`、`anthropic/claude-sonnet-4-6`、
`zai/glm-5.1`、
`moonshot/kimi-k2.5`、
`google/gemini-3.1-pro-preview` です。
judgeの `--judge-model` が指定されていない場合、
judgeのデフォルトは
`openai/gpt-5.4,thinking=xhigh,fast` と
`anthropic/claude-opus-4-6,thinking=high` です。

## 関連ドキュメント

- [Testing](/ja-JP/help/testing)
- [QA Channel](/ja-JP/channels/qa-channel)
- [Dashboard](/web/dashboard)
