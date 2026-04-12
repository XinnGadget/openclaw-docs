---
read_when:
    - システムプロンプトのテキスト、ツール一覧、または時刻 / ハートビートのセクションの編集
    - ワークスペースのブートストラップや Skills の注入動作の変更
summary: OpenClaw のシステムプロンプトに含まれる内容と、その組み立て方法
title: システムプロンプト
x-i18n:
    generated_at: "2026-04-12T04:43:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 057f01aac51f7737b5223f61f5d55e552d9011232aebb130426e269d8f6c257f
    source_path: concepts/system-prompt.md
    workflow: 15
---

# システムプロンプト

OpenClaw は、エージェントの実行ごとにカスタムのシステムプロンプトを構築します。このプロンプトは **OpenClaw が管理** しており、pi-coding-agent のデフォルトプロンプトは使用しません。

このプロンプトは OpenClaw によって組み立てられ、各エージェント実行に注入されます。

プロバイダープラグインは、OpenClaw 管理の完全なプロンプトを置き換えることなく、キャッシュ対応のプロンプトガイダンスを提供できます。プロバイダーランタイムでは、次のことが可能です。

- 少数の名前付きコアセクション（`interaction_style`、`tool_call_style`、`execution_bias`）を置き換える
- プロンプトキャッシュ境界の上に**安定したプレフィックス**を注入する
- プロンプトキャッシュ境界の下に**動的なサフィックス**を注入する

モデルファミリー固有のチューニングには、プロバイダー管理の追加を使用してください。従来の
`before_prompt_build` によるプロンプト変更は、互換性のため、または本当にグローバルなプロンプト変更にのみ使い、通常のプロバイダー挙動には使わないでください。

## 構造

このプロンプトは意図的にコンパクトで、固定セクションを使用します。

- **Tooling**: structured-tool の信頼できる情報源であることのリマインダーと、ランタイムのツール使用ガイダンス。
- **Safety**: 権力志向の挙動や監督の回避を避けるための短いガードレールのリマインダー。
- **Skills**（利用可能な場合）: 必要に応じて skill の指示を読み込む方法をモデルに伝えます。
- **OpenClaw Self-Update**: `config.schema.lookup` で安全に設定を調べる方法、`config.patch` で設定にパッチを当てる方法、`config.apply` で完全な設定を置き換える方法、および明示的なユーザー要求がある場合にのみ `update.run` を実行する方法。owner 限定の `gateway` ツールは、`tools.exec.ask` / `tools.exec.security` の書き換えも拒否します。これには、それらの保護された exec パスに正規化される旧来の `tools.bash.*` エイリアスも含まれます。
- **Workspace**: 作業ディレクトリ（`agents.defaults.workspace`）。
- **Documentation**: OpenClaw ドキュメントのローカルパス（リポジトリまたは npm パッケージ）と、それを読むべきタイミング。
- **Workspace Files (injected)**: ブートストラップファイルが以下に含まれていることを示します。
- **Sandbox**（有効な場合）: サンドボックス化されたランタイム、サンドボックスパス、および権限昇格付き exec が利用可能かどうかを示します。
- **Current Date & Time**: ユーザーのローカル時刻、タイムゾーン、時刻形式。
- **Reply Tags**: 対応プロバイダー向けのオプションの返信タグ構文。
- **Heartbeats**: デフォルトエージェントで heartbeat が有効な場合の、heartbeat プロンプトと ack の挙動。
- **Runtime**: ホスト、OS、node、モデル、リポジトリルート（検出された場合）、thinking level（1 行）。
- **Reasoning**: 現在の可視性レベルと `/reasoning` 切り替えのヒント。

Tooling セクションには、長時間実行される作業に対するランタイムガイダンスも含まれます。

- 将来のフォローアップ（`check back later`、リマインダー、定期作業）には `cron` を使用し、`exec` の sleep ループ、`yieldMs` の遅延トリック、繰り返しの `process` ポーリングは使わない
- 今すぐ開始してバックグラウンドで継続実行されるコマンドにのみ `exec` / `process` を使用する
- 自動完了 wake が有効な場合は、コマンドを一度だけ開始し、出力が出たときや失敗したときの push ベースの wake 経路に任せる
- 実行中コマンドのログ、状態、入力、介入を確認する必要がある場合は `process` を使用する
- タスクがより大きい場合は `sessions_spawn` を優先する。サブエージェントの完了は push ベースで、要求元に自動通知される
- 完了を待つためだけに `subagents list` / `sessions_list` をループでポーリングしない

実験的な `update_plan` ツールが有効な場合、Tooling では、これを自明でない複数ステップの作業にのみ使用し、`in_progress` のステップをちょうど 1 つに保ち、更新のたびに計画全体を繰り返さないようモデルに伝えます。

システムプロンプト内の Safety ガードレールは助言的なものです。これらはモデルの挙動を導きますが、ポリシーを強制するものではありません。強制にはツールポリシー、exec 承認、サンドボックス、チャンネル allowlist を使用してください。オペレーターは設計上これらを無効化できます。

ネイティブの承認カードやボタンがあるチャンネルでは、ランタイムプロンプトは、まずそのネイティブ承認 UI に依存するようエージェントに伝えます。手動の `/approve` コマンドを含めるのは、ツール結果がチャット承認を利用できないと示している場合、または手動承認が唯一の経路である場合だけです。

## プロンプトモード

OpenClaw は、サブエージェント向けにより小さいシステムプロンプトをレンダリングできます。ランタイムは各実行に `promptMode` を設定します（ユーザー向けの設定ではありません）。

- `full`（デフォルト）: 上記のすべてのセクションを含みます。
- `minimal`: サブエージェントに使用されます。**Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies**、**Heartbeats** を省略します。Tooling、**Safety**、Workspace、Sandbox、Current Date & Time（既知の場合）、Runtime、および注入されたコンテキストは引き続き利用可能です。
- `none`: ベースとなる識別行のみを返します。

`promptMode=minimal` の場合、追加で注入されるプロンプトは **Group Chat Context** ではなく **Subagent Context** とラベル付けされます。

## ワークスペースのブートストラップ注入

ブートストラップファイルは切り詰められたうえで **Project Context** の下に追加されるため、モデルは明示的に読まなくても識別情報とプロファイルコンテキストを把握できます。

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（新規ワークスペースでのみ）
- `MEMORY.md` がある場合はそれを、ない場合は小文字のフォールバックとして `memory.md`

これらのファイルはすべて、**ファイルごとのゲートが適用される場合を除き**、毎ターン **コンテキストウィンドウに注入** されます。`HEARTBEAT.md` は、通常の実行では、デフォルトエージェントで heartbeat が無効な場合、または
`agents.defaults.heartbeat.includeSystemPromptSection` が false の場合に省略されます。注入されるファイルは簡潔に保ってください。特に `MEMORY.md` は時間とともに大きくなり、予想外にコンテキスト使用量が増えたり、compaction がより頻繁に発生したりする可能性があります。

> **注:** `memory/*.md` の日次ファイルは、通常のブートストラップ Project Context の一部**ではありません**。通常のターンでは、これらは `memory_search` および `memory_get` ツールを通じて必要時にアクセスされるため、モデルが明示的に読むまでコンテキストウィンドウを消費しません。例外は素の `/new` および `/reset` ターンで、この最初のターンに限り、ランタイムが最近の日次メモリをワンショットの起動コンテキストブロックとして前置できる場合があります。

大きなファイルはマーカー付きで切り詰められます。ファイルごとの最大サイズは
`agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で制御されます。ファイル全体にまたがる注入済みブートストラップ内容の総量は
`agents.defaults.bootstrapTotalMaxChars`（デフォルト: 150000）で上限が設定されます。欠落しているファイルには短い欠落ファイルマーカーが注入されます。切り詰めが発生した場合、OpenClaw は Project Context に警告ブロックを注入できます。これは
`agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`；デフォルト: `once`）で制御します。

サブエージェントセッションでは `AGENTS.md` と `TOOLS.md` のみが注入されます（サブエージェントのコンテキストを小さく保つため、他のブートストラップファイルは除外されます）。

内部フックは `agent:bootstrap` を介してこのステップを横取りし、注入されるブートストラップファイルを変更または置き換えできます（たとえば `SOUL.md` を別のペルソナに差し替えるなど）。

エージェントの口調をより汎用的でなくしたい場合は、まず
[SOUL.md Personality Guide](/ja-JP/concepts/soul) から始めてください。

各注入ファイルがどれだけ寄与しているか（生データと注入後、切り詰め、さらにツールスキーマのオーバーヘッド）を確認するには、`/context list` または `/context detail` を使用してください。[Context](/ja-JP/concepts/context) を参照してください。

## 時刻の扱い

システムプロンプトには、ユーザーのタイムゾーンが既知の場合、専用の **Current Date & Time** セクションが含まれます。プロンプトキャッシュを安定させるため、ここには現在 **タイムゾーン** のみが含まれます（動的な時計や時刻形式は含みません）。

エージェントが現在時刻を必要とする場合は `session_status` を使用してください。ステータスカードにはタイムスタンプ行が含まれます。同じツールでは、セッションごとのモデル上書きも任意で設定できます（`model=default` でクリアされます）。

設定は次で行います。

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat`（`auto` | `12` | `24`）

完全な挙動の詳細は [Date & Time](/ja-JP/date-time) を参照してください。

## Skills

対象となる skill が存在する場合、OpenClaw は **available skills list** のコンパクト版（`formatSkillsForPrompt`）を注入し、各 skill の **ファイルパス** を含めます。プロンプトは、列挙された場所（ワークスペース、管理対象、または同梱）にある SKILL.md を読み込むために `read` を使うようモデルに指示します。対象 skill がない場合、Skills セクションは省略されます。

対象判定には、skill メタデータのゲート、ランタイム環境 / 設定チェック、および `agents.defaults.skills` または
`agents.list[].skills` が設定されている場合の有効なエージェント skill allowlist が含まれます。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

これにより、ベースプロンプトを小さく保ちながら、必要な skill だけを使えるようにしています。

## Documentation

利用可能な場合、システムプロンプトには **Documentation** セクションが含まれ、OpenClaw ドキュメントディレクトリのローカルパス（リポジトリ内の `docs/` または npm パッケージに同梱されたドキュメント）を示します。また、公開ミラー、ソースリポジトリ、コミュニティ Discord、および Skills を見つけるための ClawHub（[https://clawhub.ai](https://clawhub.ai)）にも触れます。プロンプトは、OpenClaw の挙動、コマンド、設定、またはアーキテクチャについては、まずローカルドキュメントを参照し、可能であれば自分で `openclaw status` を実行するようモデルに指示します（アクセス権がない場合にのみユーザーに尋ねます）。
