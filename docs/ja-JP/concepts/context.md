---
read_when:
    - OpenClawで「コンテキスト」が何を意味するのか理解したい
    - モデルがなぜ何かを「知っている」のか（または忘れたのか）をデバッグしている
    - コンテキストのオーバーヘッドを減らしたい（`/context`、`/status`、`/compact`）
summary: 'コンテキスト: モデルが何を見ているか、どのように構築されるか、そしてそれを調べる方法'
title: コンテキスト
x-i18n:
    generated_at: "2026-04-07T04:41:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: a75b4cd65bf6385d46265b9ce1643310bc99d220e35ec4b4924096bed3ca4aa0
    source_path: concepts/context.md
    workflow: 15
---

# コンテキスト

「コンテキスト」とは、**OpenClawが1回の実行のためにモデルへ送信するすべてのもの**です。これはモデルの**コンテキストウィンドウ**（トークン上限）によって制限されます。

初心者向けのイメージ:

- **システムプロンプト**（OpenClawが構築）: ルール、ツール、Skillsリスト、時刻/ランタイム、注入されたワークスペースファイル。
- **会話履歴**: このセッションにおけるあなたのメッセージとアシスタントのメッセージ。
- **ツール呼び出し/結果 + 添付ファイル**: コマンド出力、ファイル読み取り、画像/音声など。

コンテキストは「メモリ」とは _同じものではありません_。メモリはディスクに保存して後で再読み込みできますが、コンテキストはモデルの現在のウィンドウ内にあるものです。

## クイックスタート（コンテキストを調べる）

- `/status` → 「自分のウィンドウがどれくらい埋まっているか？」をすばやく確認 + セッション設定。
- `/context list` → 何が注入されているか + おおよそのサイズ（ファイルごと + 合計）。
- `/context detail` → より詳細な内訳: ファイルごと、ツールスキーマごとのサイズ、skillエントリごとのサイズ、システムプロンプトのサイズ。
- `/usage tokens` → 通常の返信に、返信ごとの使用量フッターを追加。
- `/compact` → 古い履歴をコンパクトなエントリに要約して、ウィンドウの空き容量を増やす。

関連項目: [スラッシュコマンド](/ja-JP/tools/slash-commands)、[トークン使用量とコスト](/ja-JP/reference/token-use)、[コンパクション](/ja-JP/concepts/compaction)。

## 出力例

値は、モデル、プロバイダー、ツールポリシー、ワークスペース内の内容によって異なります。

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

モデルが受け取るものはすべてカウントされます。たとえば次のものが含まれます。

- システムプロンプト（すべてのセクション）。
- 会話履歴。
- ツール呼び出し + ツール結果。
- 添付ファイル/文字起こし（画像/音声/ファイル）。
- コンパクションの要約と剪定アーティファクト。
- プロバイダーの「ラッパー」や隠しヘッダー（見えなくてもカウントされる）。

## OpenClawがシステムプロンプトを構築する方法

システムプロンプトは**OpenClawが管理**しており、実行ごとに再構築されます。これには次が含まれます。

- ツール一覧 + 短い説明。
- Skillsリスト（メタデータのみ。詳細は後述）。
- ワークスペースの場所。
- 時刻（UTC + 設定されていれば変換後のユーザー時刻）。
- ランタイムメタデータ（ホスト/OS/モデル/thinking）。
- **Project Context**配下に注入されたワークスペースのブートストラップファイル。

完全な内訳: [System Prompt](/ja-JP/concepts/system-prompt)。

## 注入されるワークスペースファイル（Project Context）

デフォルトでは、OpenClawは固定のワークスペースファイル群を注入します（存在する場合）。

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（初回実行時のみ）

大きなファイルは、`agents.defaults.bootstrapMaxChars`（デフォルト `20000` 文字）によって、ファイルごとに切り詰められます。OpenClawはさらに、`agents.defaults.bootstrapTotalMaxChars`（デフォルト `150000` 文字）によって、ファイル全体にまたがるブートストラップ注入の合計上限も適用します。`/context` は**rawとinjected**のサイズ、および切り詰めが発生したかどうかを表示します。

切り詰めが発生すると、ランタイムはProject Contextの下にプロンプト内警告ブロックを注入できます。これは `agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`。デフォルトは `once`）で設定します。

## Skills: 注入されるものと必要時に読み込まれるもの

システムプロンプトには、コンパクトな**skills list**（名前 + 説明 + 場所）が含まれます。このリストには実際のオーバーヘッドがあります。

skillの指示はデフォルトでは含まれません。モデルは必要なときにのみ、そのskillの `SKILL.md` を `read` することが想定されています。

## Tools: コストは2種類ある

ツールは、コンテキストに対して2つの形で影響します。

1. システムプロンプト内の**ツール一覧テキスト**（「Tooling」として見えるもの）。
2. **ツールスキーマ**（JSON）。モデルがツールを呼び出せるように送信されます。プレーンテキストとして見えなくても、コンテキストにカウントされます。

`/context detail` では、最も大きいツールスキーマの内訳が表示され、何が支配的かを確認できます。

## コマンド、ディレクティブ、そして「インラインショートカット」

スラッシュコマンドはGatewayによって処理されます。挙動にはいくつかの違いがあります。

- **スタンドアロンコマンド**: `/...` だけのメッセージはコマンドとして実行されます。
- **ディレクティブ**: `/think`、`/verbose`、`/reasoning`、`/elevated`、`/model`、`/queue` は、モデルがメッセージを見る前に取り除かれます。
  - ディレクティブだけのメッセージは、セッション設定を保持します。
  - 通常メッセージ内のインラインディレクティブは、メッセージ単位のヒントとして機能します。
- **インラインショートカット**（許可リストに載っている送信者のみ）: 通常メッセージ内の特定の `/...` トークンは即座に実行されることがあります（例: 「hey /status」）。残りのテキストはモデルが見る前に取り除かれます。

詳細: [スラッシュコマンド](/ja-JP/tools/slash-commands)。

## セッション、コンパクション、剪定（何が保持されるか）

メッセージをまたいで何が保持されるかは、仕組みによって異なります。

- **通常の履歴** は、ポリシーによってコンパクト化または剪定されるまで、セッション文字起こしに保持されます。
- **コンパクション** は、要約を文字起こしに保持しつつ、最近のメッセージはそのまま残します。
- **剪定** は、実行時の _インメモリ_ プロンプトから古いツール結果を削除しますが、文字起こしは書き換えません。

ドキュメント: [Session](/ja-JP/concepts/session)、[Compaction](/ja-JP/concepts/compaction)、[Session pruning](/ja-JP/concepts/session-pruning)。

デフォルトでは、OpenClawは組み立てと
コンパクションに組み込みの `legacy` context engine を使用します。`kind: "context-engine"` を提供するプラグインをインストールし、
`plugins.slots.contextEngine` で選択すると、OpenClawはコンテキストの
組み立て、`/compact`、および関連するsubagentコンテキストのライフサイクルフックをその
engineに委譲します。`ownsCompaction: false` であっても、自動的にlegacy
engineへフォールバックはしません。アクティブなengineは依然として `compact()` を正しく実装する必要があります。完全な
プラグ可能インターフェース、ライフサイクルフック、設定については
[Context Engine](/ja-JP/concepts/context-engine) を参照してください。

## `/context` が実際に報告するもの

`/context` は、利用可能であれば最新の**実行時に構築された**システムプロンプトレポートを優先します。

- `System prompt (run)` = 直近の埋め込み（ツール使用可能）実行から取得され、セッションストアに保持されたもの。
- `System prompt (estimate)` = 実行レポートが存在しない場合（またはレポートを生成しないCLIバックエンド経由で実行している場合）に、その場で計算されるもの。

どちらの場合も、サイズと主要な寄与要素を報告しますが、完全なシステムプロンプトやツールスキーマ自体は出力しません。

## 関連

- [Context Engine](/ja-JP/concepts/context-engine) — プラグインによるカスタムコンテキスト注入
- [Compaction](/ja-JP/concepts/compaction) — 長い会話の要約
- [System Prompt](/ja-JP/concepts/system-prompt) — システムプロンプトの構築方法
- [Agent Loop](/ja-JP/concepts/agent-loop) — エージェント実行サイクル全体
