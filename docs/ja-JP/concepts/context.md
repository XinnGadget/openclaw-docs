---
read_when:
    - OpenClaw における「コンテキスト」の意味を理解したい
    - モデルが何かを「知っている」理由（または忘れた理由）をデバッグしている
    - コンテキストのオーバーヘッドを減らしたい（`/context`、`/status`、`/compact`）
summary: 'コンテキスト: モデルが何を見るのか、どのように構築されるのか、どう調べるのか'
title: コンテキスト
x-i18n:
    generated_at: "2026-04-06T03:06:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe7dfe52cb1a64df229c8622feed1804df6c483a6243e0d2f309f6ff5c9fe521
    source_path: concepts/context.md
    workflow: 15
---

# コンテキスト

「コンテキスト」とは、**OpenClaw が 1 回の実行のためにモデルへ送るすべてのもの**です。これはモデルの**コンテキストウィンドウ**（トークン上限）によって制限されます。

初心者向けのイメージ:

- **システムプロンプト**（OpenClaw が構築）: ルール、ツール、Skills の一覧、時刻/ランタイム、注入されたワークスペースファイル。
- **会話履歴**: このセッションにおけるあなたのメッセージ + アシスタントのメッセージ。
- **ツール呼び出し/結果 + 添付ファイル**: コマンド出力、ファイル読み取り、画像/音声 など。

コンテキストは「メモリ」とは _同じものではありません_。メモリはディスクに保存して後で再読み込みできますが、コンテキストはモデルの現在のウィンドウ内に入っているものです。

## クイックスタート（コンテキストを確認する）

- `/status` → 「ウィンドウがどれくらい埋まっているか」をすばやく確認 + セッション設定。
- `/context list` → 何が注入されているか + おおよそのサイズ（ファイルごと + 合計）。
- `/context detail` → より詳細な内訳: ファイルごと、ツールスキーマごと、スキルエントリごと、システムプロンプトサイズ。
- `/usage tokens` → 通常の返信に、返信ごとの使用量フッターを追加。
- `/compact` → 古い履歴をコンパクトなエントリに要約し、ウィンドウの空きを増やす。

関連項目: [スラッシュコマンド](/ja-JP/tools/slash-commands)、[トークン使用量とコスト](/ja-JP/reference/token-use)、[コンパクション](/ja-JP/concepts/compaction)。

## 出力例

値は、モデル、プロバイダー、ツールポリシー、ワークスペースの内容によって変わります。

### `/context list`

```
🧠 Context breakdown
Workspace: <workspaceDir>
Bootstrap max/file: 20,000 chars
Sandbox: mode=non-main sandboxed=false
System prompt (run): 38,412 chars (~9,603 tok) (Project Context 23,901 chars (~5,976 tok))

Injected workspace files:
- AGENTS.md: OK | raw 1,742 chars (~436 tok) | injected 1,742 chars (~436 tok)
- SOUL.md: OK | raw 912 chars (~228 tok) | injected 912 chars (~228 tok)
- TOOLS.md: TRUNCATED | raw 54,210 chars (~13,553 tok) | injected 20,962 chars (~5,241 tok)
- IDENTITY.md: OK | raw 211 chars (~53 tok) | injected 211 chars (~53 tok)
- USER.md: OK | raw 388 chars (~97 tok) | injected 388 chars (~97 tok)
- HEARTBEAT.md: MISSING | raw 0 | injected 0
- BOOTSTRAP.md: OK | raw 0 chars (~0 tok) | injected 0 chars (~0 tok)

Skills list (system prompt text): 2,184 chars (~546 tok) (12 skills)
Tools: read, edit, write, exec, process, browser, message, sessions_send, …
Tool list (system prompt text): 1,032 chars (~258 tok)
Tool schemas (JSON): 31,988 chars (~7,997 tok) (counts toward context; not shown as text)
Tools: (same as above)

Session tokens (cached): 14,250 total / ctx=32,000
```

### `/context detail`

```
🧠 Context breakdown (detailed)
…
Top skills (prompt entry size):
- frontend-design: 412 chars (~103 tok)
- oracle: 401 chars (~101 tok)
… (+10 more skills)

Top tools (schema size):
- browser: 9,812 chars (~2,453 tok)
- exec: 6,240 chars (~1,560 tok)
… (+N more tools)
```

## コンテキストウィンドウに含まれるもの

モデルが受け取るものはすべて含まれます。たとえば:

- システムプロンプト（すべてのセクション）。
- 会話履歴。
- ツール呼び出し + ツール結果。
- 添付ファイル/文字起こし（画像/音声/ファイル）。
- コンパクションの要約とプルーニングの成果物。
- プロバイダーの「ラッパー」や隠しヘッダー（見えなくてもカウントされる）。

## OpenClaw がシステムプロンプトを構築する方法

システムプロンプトは **OpenClaw が管理**しており、実行ごとに再構築されます。含まれるもの:

- ツール一覧 + 短い説明。
- Skills 一覧（メタデータのみ。後述）。
- ワークスペースの場所。
- 時刻（UTC + 設定されていれば変換後のユーザー時刻）。
- ランタイムメタデータ（ホスト/OS/モデル/thinking）。
- **Project Context** 配下に注入されたワークスペースのブートストラップファイル。

詳細な内訳: [System Prompt](/ja-JP/concepts/system-prompt)。

## 注入されるワークスペースファイル（Project Context）

デフォルトでは、OpenClaw は固定のワークスペースファイル群を注入します（存在する場合）:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（初回実行時のみ）

大きなファイルは `agents.defaults.bootstrapMaxChars`（デフォルト `20000` 文字）に従って、ファイルごとに切り詰められます。OpenClaw は、ファイル全体にまたがるブートストラップ注入の合計上限 `agents.defaults.bootstrapTotalMaxChars`（デフォルト `150000` 文字）も適用します。`/context` では、**raw と injected** のサイズ、および切り詰めが発生したかどうかを表示します。

切り詰めが発生すると、ランタイムは Project Context の下に警告ブロックをプロンプト内へ注入できます。これは `agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`、デフォルトは `once`）で設定します。

## Skills: 注入されるものと必要時に読み込まれるもの

システムプロンプトには、コンパクトな **Skills 一覧**（名前 + 説明 + 場所）が含まれます。この一覧には実際のオーバーヘッドがあります。

スキルの指示内容自体は、デフォルトでは含まれません。モデルは必要なときにだけ、そのスキルの `SKILL.md` を `read` することが期待されています。

## ツール: コストは 2 種類ある

ツールは 2 つの形でコンテキストに影響します。

1. システムプロンプト内の**ツール一覧テキスト**（「Tooling」として見えるもの）。
2. **ツールスキーマ**（JSON）。これはモデルがツールを呼び出せるように送られます。プレーンテキストとしては見えなくても、コンテキストに含まれます。

`/context detail` では最大のツールスキーマを内訳表示するので、どれが支配的かを確認できます。

## コマンド、ディレクティブ、「インラインショートカット」

スラッシュコマンドは Gateway が処理します。いくつか異なる動作があります。

- **スタンドアロンコマンド**: `/...` だけのメッセージはコマンドとして実行されます。
- **ディレクティブ**: `/think`、`/verbose`、`/reasoning`、`/elevated`、`/model`、`/queue` は、モデルがメッセージを見る前に取り除かれます。
  - ディレクティブだけのメッセージは、セッション設定を永続化します。
  - 通常メッセージ内のインラインディレクティブは、メッセージ単位のヒントとして動作します。
- **インラインショートカット**（許可リストにある送信者のみ）: 通常メッセージ内の特定の `/...` トークンは即座に実行されることがあります（例: 「hey /status」）。その後、残りのテキストがモデルに見える前に取り除かれます。

詳細: [スラッシュコマンド](/ja-JP/tools/slash-commands)。

## セッション、コンパクション、プルーニング（何が保持されるか）

メッセージをまたいで何が保持されるかは、その仕組みによって異なります。

- **通常の履歴** は、ポリシーにより compacted/pruned されるまでセッショントランスクリプトに保持されます。
- **コンパクション** は、要約をトランスクリプトへ保持し、最近のメッセージはそのまま残します。
- **プルーニング** は、ある実行のための _インメモリ_ プロンプトから古いツール結果を削除しますが、トランスクリプト自体は書き換えません。

ドキュメント: [Session](/ja-JP/concepts/session)、[Compaction](/ja-JP/concepts/compaction)、[Session pruning](/ja-JP/concepts/session-pruning)。

デフォルトでは、OpenClaw は組み立てと
コンパクションに組み込みの `legacy` context engine を使用します。
`kind: "context-engine"` を提供するプラグインをインストールし、
`plugins.slots.contextEngine` で選択すると、OpenClaw はコンテキストの
組み立て、`/compact`、および関連するサブエージェントのコンテキスト
ライフサイクルフックをその engine に委譲します。`ownsCompaction: false`
であっても `legacy` engine へ自動フォールバックはされません。アクティブな
engine は依然として `compact()` を正しく実装している必要があります。完全な
プラガブルインターフェース、ライフサイクルフック、設定については
[Context Engine](/ja-JP/concepts/context-engine) を参照してください。

## `/context` が実際に報告するもの

`/context` は、利用可能であれば最新の**実行時構築済み**システムプロンプトレポートを優先します。

- `System prompt (run)` = 最後の埋め込み済み（ツール利用可能）実行から取得され、セッションストアに保存されたもの。
- `System prompt (estimate)` = まだ実行レポートが存在しない場合に、その場で計算されたもの。

いずれの場合も、サイズと主要な要因を報告しますが、システムプロンプト全体やツールスキーマそのものは出力しません。

## 関連

- [Context Engine](/ja-JP/concepts/context-engine) — プラグインによるカスタムコンテキスト注入
- [Compaction](/ja-JP/concepts/compaction) — 長い会話の要約
- [System Prompt](/ja-JP/concepts/system-prompt) — システムプロンプトの構築方法
- [Agent Loop](/ja-JP/concepts/agent-loop) — エージェント実行サイクル全体
