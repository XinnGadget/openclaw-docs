---
read_when:
    - OpenClawにおける「コンテキスト」の意味を理解したい場合
    - モデルがなぜ何かを「知っている」のか（あるいは忘れたのか）をデバッグしている場合
    - コンテキストのオーバーヘッドを減らしたい場合（`/context`、`/status`、`/compact`）
summary: 'コンテキスト: モデルが何を見るか、どのように構築されるか、そしてそれをどのように調べるか'
title: コンテキスト
x-i18n:
    generated_at: "2026-04-12T23:27:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3620db1a8c1956d91a01328966df491388d3a32c4003dc4447197eb34316c77d
    source_path: concepts/context.md
    workflow: 15
---

# コンテキスト

「コンテキスト」とは、**OpenClawが実行時にモデルへ送信するすべてのもの**です。これはモデルの**コンテキストウィンドウ**（トークン上限）によって制限されます。

初心者向けのイメージ:

- **システムプロンプト**（OpenClawが構築）: ルール、ツール、Skills リスト、時刻/ランタイム、注入されたワークスペースファイル。
- **会話履歴**: このセッションにおけるあなたのメッセージ + アシスタントのメッセージ。
- **ツール呼び出し/結果 + 添付**: コマンド出力、ファイル読み取り、画像/音声など。

コンテキストは「メモリ」とは_同じではありません_。メモリはディスクに保存されて後で再読み込みできますが、コンテキストはモデルの現在のウィンドウ内に入っているものです。

## クイックスタート（コンテキストを調べる）

- `/status` → 「ウィンドウがどの程度埋まっているか」の簡易表示 + セッション設定。
- `/context list` → 注入されているもの + おおよそのサイズ（ファイルごと + 合計）。
- `/context detail` → より詳細な内訳: ファイルごと、ツールスキーマごとのサイズ、Skill エントリごとのサイズ、システムプロンプトサイズ。
- `/usage tokens` → 通常の返信に返信ごとの使用量フッターを追加。
- `/compact` → 古い履歴をコンパクトなエントリに要約して、ウィンドウの空きを増やす。

関連項目: [スラッシュコマンド](/ja-JP/tools/slash-commands)、[トークン使用量とコスト](/ja-JP/reference/token-use)、[Compaction](/ja-JP/concepts/compaction)。

## 出力例

値はモデル、プロバイダ、ツールポリシー、ワークスペース内の内容によって異なります。

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

モデルが受け取るものはすべてカウントされます。これには以下が含まれます:

- システムプロンプト（すべてのセクション）。
- 会話履歴。
- ツール呼び出し + ツール結果。
- 添付/文字起こし（画像/音声/ファイル）。
- Compaction の要約と pruning アーティファクト。
- プロバイダの「ラッパー」や隠しヘッダー（見えなくてもカウントされる）。

## OpenClawがシステムプロンプトをどのように構築するか

システムプロンプトは**OpenClawが所有**しており、実行ごとに再構築されます。これには以下が含まれます:

- ツール一覧 + 短い説明。
- Skills リスト（メタデータのみ。詳細は後述）。
- ワークスペースの場所。
- 時刻（UTC + 設定されていれば変換後のユーザー時刻）。
- ランタイムメタデータ（ホスト/OS/モデル/thinking）。
- **Project Context** 配下に注入されるワークスペースのブートストラップファイル。

完全な内訳: [System Prompt](/ja-JP/concepts/system-prompt)。

## 注入されるワークスペースファイル（Project Context）

デフォルトでは、OpenClawは固定のワークスペースファイル群を（存在すれば）注入します:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（初回実行時のみ）

大きなファイルは、`agents.defaults.bootstrapMaxChars`（デフォルト `20000` 文字）を使ってファイルごとに切り詰められます。OpenClawはさらに、ファイル全体をまたいだブートストラップ注入の合計上限 `agents.defaults.bootstrapTotalMaxChars`（デフォルト `150000` 文字）も適用します。`/context` では、**raw と injected** のサイズ、および切り詰めが発生したかどうかが表示されます。

切り詰めが発生すると、ランタイムは Project Context の下にプロンプト内警告ブロックを注入できます。これは `agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`。デフォルトは `once`）で設定します。

## Skills: 注入されるものと必要時に読み込まれるもの

システムプロンプトには、コンパクトな**Skills リスト**（名前 + 説明 + 場所）が含まれます。このリストには実際のオーバーヘッドがあります。

Skill の指示はデフォルトでは含まれません。モデルは必要なときにだけ、その Skill の `SKILL.md` を `read` することが想定されています。

## ツール: コストは2種類ある

ツールは2つの形でコンテキストに影響します:

1. システムプロンプト内の**ツール一覧テキスト**（「Tooling」として見えるもの）。
2. **ツールスキーマ**（JSON）。これらはモデルがツールを呼び出せるように送られます。プレーンテキストとして見えなくても、コンテキストにカウントされます。

`/context detail` では最大のツールスキーマを内訳表示するため、どこが支配的か確認できます。

## コマンド、ディレクティブ、「インラインショートカット」

スラッシュコマンドは Gateway によって処理されます。動作にはいくつかの種類があります:

- **スタンドアロンコマンド**: `/...` のみのメッセージはコマンドとして実行されます。
- **ディレクティブ**: `/think`、`/verbose`、`/trace`、`/reasoning`、`/elevated`、`/model`、`/queue` は、モデルがメッセージを見る前に取り除かれます。
  - ディレクティブのみのメッセージはセッション設定を保持します。
  - 通常メッセージ内のインラインディレクティブは、メッセージ単位のヒントとして機能します。
- **インラインショートカット**（許可リストにある送信者のみ）: 通常メッセージ内の特定の `/...` トークンは即座に実行されることがあり（例: 「hey /status」）、残りのテキストをモデルが見る前に取り除かれます。

詳細: [スラッシュコマンド](/ja-JP/tools/slash-commands)。

## セッション、Compaction、pruning（何が保持されるか）

メッセージをまたいで何が保持されるかは、その仕組みによって異なります:

- **通常の履歴**は、ポリシーによって compact/prune されるまでセッショントランスクリプトに保持されます。
- **Compaction** は要約をトランスクリプトに保持し、最近のメッセージはそのまま残します。
- **Pruning** は実行時の_インメモリ_プロンプトから古いツール結果を削除しますが、トランスクリプト自体は書き換えません。

ドキュメント: [Session](/ja-JP/concepts/session)、[Compaction](/ja-JP/concepts/compaction)、[Session pruning](/ja-JP/concepts/session-pruning)。

デフォルトでは、OpenClawは組み立てと
compaction に組み込みの `legacy` コンテキストエンジンを使用します。`kind: "context-engine"` を提供する Plugin をインストールし、
`plugins.slots.contextEngine` でそれを選択すると、OpenClawはコンテキストの組み立て、`/compact`、および関連するサブエージェントのコンテキストライフサイクルフックをそのエンジンに委譲します。`ownsCompaction: false` は `legacy`
エンジンへの自動フォールバックを意味しません。アクティブなエンジンは依然として `compact()` を正しく実装している必要があります。完全な
プラガブルインターフェース、ライフサイクルフック、設定については
[Context Engine](/ja-JP/concepts/context-engine) を参照してください。

## `/context` が実際に報告するもの

`/context` は、利用可能な場合は最新の**実行時構築済み**システムプロンプトレポートを優先します:

- `System prompt (run)` = 最後の埋め込み（ツール使用可能）実行から取得され、セッションストアに保持されたもの。
- `System prompt (estimate)` = 実行レポートが存在しない場合（またはそのレポートを生成しないCLIバックエンド経由で実行している場合）に、その場で計算されたもの。

いずれの場合も、サイズと主な要因を報告しますが、完全なシステムプロンプトやツールスキーマ自体は出力しません。

## 関連

- [Context Engine](/ja-JP/concepts/context-engine) — Plugin によるカスタムコンテキスト注入
- [Compaction](/ja-JP/concepts/compaction) — 長い会話の要約
- [System Prompt](/ja-JP/concepts/system-prompt) — システムプロンプトの構築方法
- [Agent Loop](/ja-JP/concepts/agent-loop) — エージェント実行サイクル全体
