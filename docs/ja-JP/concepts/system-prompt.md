---
read_when:
    - システムプロンプトのテキスト、ツール一覧、または時刻 / ハートビートのセクションを編集する場合
    - ワークスペースのブートストラップや Skills の注入動作を変更する場合
summary: OpenClaw のシステムプロンプトに含まれる内容と、その組み立て方法
title: システムプロンプト
x-i18n:
    generated_at: "2026-04-08T02:14:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: e55fc886bc8ec47584d07c9e60dfacd964dc69c7db976ea373877dc4fe09a79a
    source_path: concepts/system-prompt.md
    workflow: 15
---

# システムプロンプト

OpenClaw は、各エージェント実行ごとにカスタムのシステムプロンプトを構築します。このプロンプトは **OpenClaw が管理する** ものであり、pi-coding-agent のデフォルトプロンプトは使用しません。

プロンプトは OpenClaw によって組み立てられ、各エージェント実行に注入されます。

プロバイダープラグインは、OpenClaw が管理するプロンプト全体を置き換えることなく、キャッシュを意識したプロンプトガイダンスを追加できます。プロバイダーランタイムでは、次のことが可能です。

- 少数の名前付きコアセクション（`interaction_style`、
  `tool_call_style`, `execution_bias`）を置き換える
- プロンプトキャッシュ境界の上に **stable prefix** を注入する
- プロンプトキャッシュ境界の下に **dynamic suffix** を注入する

モデルファミリー固有のチューニングには、プロバイダー管理の追加内容を使用してください。従来の
`before_prompt_build` によるプロンプト変更は、互換性維持や本当にグローバルなプロンプト変更のために残し、通常のプロバイダー動作には使わないでください。

## 構成

このプロンプトは意図的にコンパクトで、固定セクションを使用します。

- **Tooling**: structured-tool の信頼できる情報源であることのリマインダーと、ランタイムでのツール使用ガイダンス。
- **Safety**: 権力追求的な行動や監督の回避を避けるための短いガードレールのリマインダー。
- **Skills**（利用可能な場合）: 必要に応じてスキル指示を読み込む方法をモデルに伝えます。
- **OpenClaw Self-Update**: `config.schema.lookup` で安全に設定を確認する方法、`config.patch` で設定をパッチする方法、`config.apply` で完全な設定を置き換える方法、および明示的なユーザー要求がある場合にのみ `update.run` を実行する方法。owner 専用の `gateway` ツールも、保護された exec パスに正規化される従来の `tools.bash.*` エイリアスを含め、`tools.exec.ask` / `tools.exec.security` の書き換えを拒否します。
- **Workspace**: 作業ディレクトリ（`agents.defaults.workspace`）。
- **Documentation**: OpenClaw ドキュメントへのローカルパス（リポジトリまたは npm パッケージ）と、それを読むべきタイミング。
- **Workspace Files (injected)**: ブートストラップファイルが以下に含まれていることを示します。
- **Sandbox**（有効な場合）: サンドボックス化されたランタイム、サンドボックスのパス、および昇格された exec が利用可能かどうかを示します。
- **Current Date & Time**: ユーザーのローカル時刻、タイムゾーン、時刻形式。
- **Reply Tags**: サポートされているプロバイダー向けの任意の返信タグ構文。
- **Heartbeats**: デフォルトエージェントでハートビートが有効な場合の、ハートビートプロンプトと ack 動作。
- **Runtime**: ホスト、OS、node、モデル、リポジトリルート（検出時）、thinking level（1 行）。
- **Reasoning**: 現在の可視性レベルと /reasoning 切り替えのヒント。

Tooling セクションには、長時間実行される作業のためのランタイムガイダンスも含まれます。

- 将来のフォローアップ（`check back later`、リマインダー、定期作業）には cron を使い、`exec` の sleep ループ、`yieldMs` の遅延トリック、繰り返しの `process` ポーリングは使わない
- 今すぐ開始してバックグラウンドで実行し続けるコマンドにのみ `exec` / `process` を使う
- 自動完了 wake が有効な場合、コマンドは一度だけ開始し、出力または失敗時のプッシュベースの wake 経路に任せる
- 実行中コマンドの確認が必要な場合は、ログ、状態、入力、介入のために `process` を使う
- タスクが大きい場合は、`sessions_spawn` を優先する。サブエージェントの完了はプッシュベースで、依頼元に自動通知される
- 完了を待つためだけに `subagents list` / `sessions_list` をループでポーリングしない

実験的な `update_plan` ツールが有効な場合、Tooling はモデルに対して、これを自明でない複数ステップの作業にのみ使い、`in_progress` のステップを必ず 1 つだけ保ち、更新のたびにプラン全体を繰り返さないようにも指示します。

システムプロンプト内の Safety ガードレールは助言的なものです。これはモデルの動作を導きますが、ポリシーを強制するものではありません。厳格な強制には、ツールポリシー、exec 承認、サンドボックス化、チャネル allowlist を使用してください。オペレーターは設計上これらを無効にできます。

ネイティブの承認カード / ボタンがあるチャネルでは、ランタイムプロンプトはエージェントに対して、まずそのネイティブ承認 UI を使うよう指示します。手動の
`/approve` コマンドを含めるのは、ツール結果がチャット承認を利用できないと示した場合、または手動承認が唯一の手段である場合に限られます。

## プロンプトモード

OpenClaw は、サブエージェント用により小さいシステムプロンプトをレンダリングできます。ランタイムは各実行に対して
`promptMode` を設定します（ユーザー向けの設定ではありません）。

- `full`（デフォルト）: 上記のすべてのセクションを含みます。
- `minimal`: サブエージェントで使用されます。**Skills**、**Memory Recall**、**OpenClaw
  Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、
  **Messaging**、**Silent Replies**、**Heartbeats** を省略します。Tooling、**Safety**、
  Workspace、Sandbox、Current Date & Time（既知の場合）、Runtime、および注入された
  コンテキストは引き続き利用できます。
- `none`: ベースの識別行のみを返します。

`promptMode=minimal` の場合、追加で注入されるプロンプトには **Group Chat Context** ではなく **Subagent
Context** というラベルが付きます。

## ワークスペースブートストラップの注入

ブートストラップファイルはトリミングされ、**Project Context** の下に追加されます。これにより、モデルは明示的に読み込まなくても識別情報やプロファイル文脈を把握できます。

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（新規ワークスペースのみ）
- `MEMORY.md` が存在する場合はそれを、存在しない場合は小文字の代替として `memory.md`

これらのファイルはすべて、**ファイル固有のゲートが適用されない限り** 毎ターン **コンテキストウィンドウに注入されます**。通常実行時の `HEARTBEAT.md` は、デフォルトエージェントでハートビートが無効な場合、または
`agents.defaults.heartbeat.includeSystemPromptSection` が false の場合は省略されます。注入されるファイルは簡潔に保ってください。特に `MEMORY.md` は時間とともに肥大化しやすく、想定外に高いコンテキスト使用量やより頻繁な compaction の原因になります。

> **注:** `memory/*.md` の日次ファイルは **自動では注入されません**。これらは
> `memory_search` および `memory_get` ツールを通じて必要に応じてアクセスされるため、
> モデルが明示的に読み込まない限りコンテキストウィンドウを消費しません。

大きなファイルはマーカー付きで切り詰められます。1 ファイルあたりの最大サイズは
`agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で制御されます。ファイル全体で注入されるブートストラップ内容の合計は `agents.defaults.bootstrapTotalMaxChars`
（デフォルト: 150000）で上限が設定されます。ファイルが存在しない場合は、短い missing-file マーカーが注入されます。切り詰めが発生した場合、OpenClaw は Project Context に警告ブロックを注入できます。これは
`agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`；
デフォルト: `once`）で制御します。

サブエージェントセッションでは `AGENTS.md` と `TOOLS.md` のみを注入します（サブエージェントのコンテキストを小さく保つため、他のブートストラップファイルは除外されます）。

内部フックは `agent:bootstrap` を通じてこのステップを横取りし、注入されるブートストラップファイルを変更または置き換えることができます（たとえば、`SOUL.md` を別のペルソナに差し替えるなど）。

エージェントの話し方をもっと汎用的でなくしたい場合は、まず
[SOUL.md Personality Guide](/ja-JP/concepts/soul) から始めてください。

各注入ファイルがどれだけ寄与しているか（raw と injected、切り詰め、さらにツールスキーマのオーバーヘッド）を確認するには、`/context list` または `/context detail` を使用してください。詳しくは [Context](/ja-JP/concepts/context) を参照してください。

## 時刻の扱い

ユーザーのタイムゾーンが分かっている場合、システムプロンプトには専用の **Current Date & Time** セクションが含まれます。プロンプトキャッシュを安定させるため、現在は **time zone** のみを含みます（動的な時計や時刻形式は含みません）。

エージェントが現在時刻を必要とする場合は `session_status` を使用してください。ステータスカードにはタイムスタンプ行が含まれます。同じツールで、セッションごとのモデル上書きも任意で設定できます（`model=default` でクリアされます）。

設定項目:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

動作の詳細は [Date & Time](/ja-JP/date-time) を参照してください。

## Skills

適格な Skills が存在する場合、OpenClaw は各スキルの **file path** を含むコンパクトな **available skills list**
（`formatSkillsForPrompt`）を注入します。プロンプトは、一覧にある場所（workspace、managed、または bundled）から `read` を使って SKILL.md を読み込むようモデルに指示します。適格な Skills がない場合、Skills セクションは省略されます。

適格性には、スキルメタデータのゲート、ランタイム環境 / 設定チェック、および `agents.defaults.skills` または
`agents.list[].skills` が設定されている場合の実効エージェントスキル allowlist が含まれます。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

これにより、ベースプロンプトを小さく保ちながら、必要なスキルを対象を絞って利用できます。

## Documentation

利用可能な場合、システムプロンプトには **Documentation** セクションが含まれ、ローカルの OpenClaw ドキュメントディレクトリ（リポジトリ内の `docs/` またはバンドルされた npm パッケージのドキュメント）を示します。さらに、公開ミラー、ソースリポジトリ、コミュニティ Discord、および Skills を見つけるための ClawHub（[https://clawhub.ai](https://clawhub.ai)）についても記載されます。プロンプトは、OpenClaw の動作、コマンド、設定、またはアーキテクチャについては、まずローカルドキュメントを参照し、可能な場合は自分で `openclaw status` を実行するようモデルに指示します（アクセスできない場合にのみユーザーへ尋ねます）。
