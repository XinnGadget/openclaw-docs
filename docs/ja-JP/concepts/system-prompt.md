---
read_when:
    - システムプロンプトのテキスト、ツール一覧、または時刻/heartbeat セクションを編集している
    - ワークスペースのブートストラップや Skills 注入の動作を変更している
summary: OpenClaw のシステムプロンプトに何が含まれ、どのように組み立てられるか
title: システムプロンプト
x-i18n:
    generated_at: "2026-04-06T03:07:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: f14ba7f16dda81ac973d72be05931fa246bdfa0e1068df1a84d040ebd551c236
    source_path: concepts/system-prompt.md
    workflow: 15
---

# システムプロンプト

OpenClaw は、エージェントの実行ごとにカスタムのシステムプロンプトを構築します。このプロンプトは **OpenClaw が管理**しており、pi-coding-agent のデフォルトプロンプトは使用しません。

このプロンプトは OpenClaw によって組み立てられ、各エージェント実行に注入されます。

プロバイダープラグインは、OpenClaw が管理するプロンプト全体を置き換えることなく、キャッシュを意識したプロンプトガイダンスを提供できます。プロバイダーランタイムができること:

- 名前付きの少数のコアセクション（`interaction_style`、`tool_call_style`、`execution_bias`）を置き換える
- プロンプトキャッシュ境界の上に**安定したプレフィックス**を注入する
- プロンプトキャッシュ境界の下に**動的なサフィックス**を注入する

モデルファミリー固有の調整には、プロバイダー側の提供機能を使ってください。従来の `before_prompt_build` によるプロンプト変更は、互換性維持や本当にグローバルなプロンプト変更のために残し、通常のプロバイダー動作には使わないでください。

## 構成

このプロンプトは意図的にコンパクトに保たれており、固定のセクションを使用します。

- **Tooling**: 構造化ツールの信頼できる唯一の情報源であることの注意と、ランタイムでのツール使用ガイダンス。
- **Safety**: 権力追求的な行動や監督回避を避けるための短いガードレールの注意。
- **Skills**（利用可能な場合）: 必要に応じてスキル指示を読み込む方法をモデルに伝えます。
- **OpenClaw Self-Update**: `config.schema.lookup` で安全に設定を確認し、`config.patch` で設定にパッチを当て、`config.apply` で設定全体を置き換え、明示的なユーザー要求がある場合にのみ `update.run` を実行する方法。owner 専用の `gateway` ツールも、従来の `tools.bash.*` エイリアスを含めて `tools.exec.ask` / `tools.exec.security` の書き換えを拒否し、これらは保護された exec パスへ正規化されます。
- **Workspace**: 作業ディレクトリ（`agents.defaults.workspace`）。
- **Documentation**: OpenClaw ドキュメントのローカルパス（リポジトリまたは npm パッケージ）と、読むべきタイミング。
- **Workspace Files (injected)**: ブートストラップファイルが下に含まれていることを示します。
- **Sandbox**（有効な場合）: サンドボックス化されたランタイム、サンドボックスパス、昇格付き exec が利用可能かどうかを示します。
- **Current Date & Time**: ユーザーのローカル時刻、タイムゾーン、時刻形式。
- **Reply Tags**: サポートされているプロバイダー向けの任意の返信タグ構文。
- **Heartbeats**: heartbeat プロンプトと ack の動作。
- **Runtime**: ホスト、OS、node、モデル、リポジトリルート（検出された場合）、thinking レベル（1 行）。
- **Reasoning**: 現在の可視性レベル + `/reasoning` 切り替えのヒント。

Tooling セクションには、長時間実行される作業のためのランタイムガイダンスも含まれます。

- 将来のフォローアップ（`check back later`、リマインダー、定期作業）には cron を使い、`exec` の sleep ループ、`yieldMs` の遅延トリック、繰り返しの `process` ポーリングは使わない
- `exec` / `process` は、今すぐ開始してバックグラウンドで実行し続けるコマンドにのみ使う
- 自動完了 wake が有効な場合は、コマンドを 1 回だけ開始し、出力または失敗時に push ベースの wake パスへ任せる
- 実行中コマンドのログ、状態、入力、介入を確認する必要がある場合は `process` を使う
- タスクが大きい場合は `sessions_spawn` を優先する。サブエージェントの完了は push ベースで、依頼元へ自動通知される
- 完了を待つためだけに `subagents list` / `sessions_list` をループでポーリングしない

実験的な `update_plan` ツールが有効な場合、Tooling は、これを自明でない複数ステップの作業にのみ使い、`in_progress` ステップを常に 1 つだけ保ち、更新のたびに計画全体を繰り返さないようモデルへ指示します。

システムプロンプト内の Safety ガードレールは助言的なものです。これはモデルの振る舞いを導きますが、ポリシーを強制するものではありません。厳格な強制には、ツールポリシー、exec 承認、サンドボックス化、チャネル allowlist を使ってください。オペレーターは設計上、これらを無効化できます。

ネイティブの承認カード/ボタンを持つチャネルでは、ランタイムプロンプトは、まずそのネイティブ承認 UI に頼るようエージェントへ指示します。ツール結果がチャット承認を利用できない、または手動承認しか経路がないと示している場合にのみ、手動の `/approve` コマンドを含めるべきです。

## プロンプトモード

OpenClaw はサブエージェント向けに、より小さなシステムプロンプトを描画できます。ランタイムは各実行に `promptMode` を設定します（ユーザー向け設定ではありません）。

- `full`（デフォルト）: 上記のすべてのセクションを含みます。
- `minimal`: サブエージェントに使用されます。**Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies**、**Heartbeats** を省略します。Tooling、**Safety**、Workspace、Sandbox、Current Date & Time（わかっている場合）、Runtime、および注入されたコンテキストは利用可能なままです。
- `none`: ベースの identity 行だけを返します。

`promptMode=minimal` の場合、追加で注入されるプロンプトには **Group Chat Context** ではなく **Subagent Context** というラベルが付きます。

## ワークスペースのブートストラップ注入

ブートストラップファイルはトリミングされ、**Project Context** 配下に追加されます。これにより、モデルは明示的に読む必要なく、identity と profile の文脈を把握できます。

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（新規ワークスペースのみ）
- `MEMORY.md` が存在する場合はそれを、存在しない場合は小文字のフォールバックとして `memory.md`

これらのファイルはすべて、毎ターン **コンテキストウィンドウに注入されます**。つまり、トークンを消費します。簡潔に保ってください。特に `MEMORY.md` は時間とともに大きくなりやすく、予想外にコンテキスト使用量が高くなり、compaction がより頻繁に発生する原因になります。

> **注:** `memory/*.md` の日次ファイルは自動では注入されません。これらは必要時に `memory_search` と `memory_get` ツール経由でアクセスされるため、モデルが明示的に読まない限りコンテキストウィンドウには含まれません。

大きなファイルはマーカー付きで切り詰められます。ファイルごとの最大サイズは `agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で制御されます。ファイル全体にまたがる注入済みブートストラップ内容の合計は `agents.defaults.bootstrapTotalMaxChars`（デフォルト: 150000）で制限されます。欠落しているファイルには短い missing-file マーカーが注入されます。切り詰めが発生すると、OpenClaw は Project Context に警告ブロックを注入できます。これは `agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`、デフォルト: `once`）で制御します。

サブエージェントセッションでは `AGENTS.md` と `TOOLS.md` だけが注入されます（他のブートストラップファイルは、サブエージェントのコンテキストを小さく保つため除外されます）。

内部フックは `agent:bootstrap` を通じてこの段階を横取りし、注入されるブートストラップファイルを変更または置き換えることができます（たとえば `SOUL.md` を別の persona に差し替えるなど）。

エージェントの話し方をより無個性でないものにしたい場合は、まず [SOUL.md Personality Guide](/ja-JP/concepts/soul) から始めてください。

注入された各ファイルがどれだけ寄与しているか（raw と injected、切り詰め、およびツールスキーマのオーバーヘッドを含む）を確認するには、`/context list` または `/context detail` を使ってください。[Context](/ja-JP/concepts/context) を参照してください。

## 時刻の扱い

ユーザーのタイムゾーンがわかっている場合、システムプロンプトには専用の **Current Date & Time** セクションが含まれます。プロンプトキャッシュを安定させるため、現在は **タイムゾーン** のみが含まれます（動的な時計や時刻形式は含まれません）。

エージェントが現在時刻を必要とする場合は `session_status` を使ってください。ステータスカードにはタイムスタンプ行が含まれます。同じツールは、セッションごとのモデル上書きも任意で設定できます（`model=default` でクリア）。

設定項目:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat`（`auto` | `12` | `24`）

動作の詳細は [Date & Time](/ja-JP/date-time) を参照してください。

## Skills

利用条件を満たすスキルが存在する場合、OpenClaw は各スキルの**ファイルパス**を含むコンパクトな **available skills list**（`formatSkillsForPrompt`）を注入します。プロンプトは、一覧にある場所（ワークスペース、managed、または bundled）にある `SKILL.md` を `read` で読み込むようモデルへ指示します。利用条件を満たすスキルがない場合、Skills セクションは省略されます。

利用条件には、スキルメタデータのゲート、ランタイム環境/設定チェック、および `agents.defaults.skills` または `agents.list[].skills` が設定されている場合の実効エージェントスキル allowlist が含まれます。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

これにより、ベースプロンプトを小さく保ちながら、必要なスキルだけを狙って利用できます。

## Documentation

利用可能な場合、システムプロンプトには **Documentation** セクションが含まれ、OpenClaw ドキュメントのローカルディレクトリ（リポジトリワークスペース内の `docs/` または同梱 npm パッケージの docs）を指し示します。また、公開ミラー、ソースリポジトリ、コミュニティ Discord、Skills 発見のための ClawHub（[https://clawhub.ai](https://clawhub.ai)）にも触れます。プロンプトは、OpenClaw の動作、コマンド、設定、アーキテクチャについてはまずローカルドキュメントを参照し、可能であれば自分で `openclaw status` を実行するようモデルへ指示します（アクセスできない場合のみユーザーに尋ねます）。
