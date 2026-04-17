---
read_when:
    - システムプロンプトのテキスト、ツール一覧、または時刻／Heartbeat セクションの編集
    - ワークスペースのブートストラップや Skills の注入動作の変更
summary: OpenClawのシステムプロンプトに何が含まれているか、およびそれがどのように組み立てられるか
title: システムプロンプト
x-i18n:
    generated_at: "2026-04-15T19:41:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: c740e4646bc4980567338237bfb55126af0df72499ca00a48e4848d9a3608ab4
    source_path: concepts/system-prompt.md
    workflow: 15
---

# システムプロンプト

OpenClaw は、エージェントの各実行ごとにカスタムのシステムプロンプトを構築します。このプロンプトは **OpenClaw が所有** しており、pi-coding-agent のデフォルトプロンプトは使用しません。

このプロンプトは OpenClaw によって組み立てられ、各エージェント実行に注入されます。

プロバイダ Plugin は、完全な OpenClaw 所有のプロンプトを置き換えることなく、キャッシュを意識したプロンプトガイダンスを提供できます。プロバイダランタイムでは次のことが可能です。

- 少数の名前付きコアセクション（`interaction_style`、`tool_call_style`、`execution_bias`）を置き換える
- プロンプトキャッシュ境界の上に **stable prefix** を注入する
- プロンプトキャッシュ境界の下に **dynamic suffix** を注入する

モデルファミリー固有のチューニングには、プロバイダ所有の寄与を使ってください。従来の
`before_prompt_build` によるプロンプト変更は、互換性維持や本当にグローバルなプロンプト変更のために残し、通常のプロバイダ動作には使わないでください。

## 構造

このプロンプトは意図的にコンパクトで、固定セクションを使用します。

- **Tooling**: 構造化ツールの source-of-truth リマインダーと、ランタイムのツール使用ガイダンス。
- **Safety**: 権力追求的な振る舞いや監督の回避を避けるための短いガードレールリマインダー。
- **Skills**（利用可能な場合）: 必要に応じてスキル指示を読み込む方法をモデルに伝えます。
- **OpenClaw Self-Update**: `config.schema.lookup` を使った安全な設定確認方法、`config.patch` による設定パッチ、`config.apply` による完全設定置換、そして明示的なユーザー要求時にのみ `update.run` を実行する方法。owner-only の `gateway` ツールは、保護された exec パスに正規化される従来の `tools.bash.*` エイリアスを含め、`tools.exec.ask` / `tools.exec.security` の書き換えも拒否します。
- **Workspace**: 作業ディレクトリ（`agents.defaults.workspace`）。
- **Documentation**: OpenClaw ドキュメントへのローカルパス（リポジトリまたは npm パッケージ）と、それを読むべきタイミング。
- **Workspace Files (injected)**: ブートストラップファイルが以下に含まれることを示します。
- **Sandbox**（有効な場合）: サンドボックス化されたランタイム、サンドボックスのパス、昇格 exec が利用可能かどうかを示します。
- **Current Date & Time**: ユーザーローカル時刻、タイムゾーン、時刻形式。
- **Reply Tags**: 対応プロバイダ向けの任意の返信タグ構文。
- **Heartbeats**: デフォルトエージェントで Heartbeat が有効な場合の Heartbeat プロンプトと ack 動作。
- **Runtime**: ホスト、OS、node、モデル、repo ルート（検出された場合）、thinking レベル（1 行）。
- **Reasoning**: 現在の可視性レベルと `/reasoning` 切り替えヒント。

Tooling セクションには、長時間実行される作業向けのランタイムガイダンスも含まれます。

- `exec` の sleep ループ、`yieldMs` の遅延トリック、`process` の繰り返しポーリングではなく、将来のフォローアップ（`check back later`、リマインダー、定期作業）には cron を使う
- `exec` / `process` は、今すぐ開始してバックグラウンドで継続実行されるコマンドにのみ使う
- 自動完了ウェイクが有効な場合は、コマンドを一度だけ開始し、出力または失敗時の push ベースのウェイク経路に依存する
- 実行中コマンドを確認する必要があるときのログ、状態、入力、介入には `process` を使う
- タスクがより大きい場合は、`sessions_spawn` を優先する。サブエージェントの完了は push ベースで、依頼元へ自動通知される
- 完了待ちのためだけに `subagents list` / `sessions_list` をループでポーリングしない

実験的な `update_plan` ツールが有効な場合、Tooling では、それを自明でない複数ステップ作業にのみ使い、`in_progress` ステップをちょうど 1 つ維持し、各更新後に計画全体を繰り返さないようモデルに伝えます。

システムプロンプト内の Safety ガードレールは助言的なものです。モデルの動作を導きますが、ポリシーを強制するものではありません。強制には、ツールポリシー、exec 承認、サンドボックス化、チャネル許可リストを使ってください。運用者は設計上これらを無効化できます。

ネイティブの承認カード／ボタンがあるチャネルでは、ランタイムプロンプトはエージェントに対して、まずそのネイティブ承認 UI に依存するよう伝えます。手動の
`/approve` コマンドを含めるのは、ツール結果がチャット承認を利用不可と示した場合、または手動承認のみが唯一の経路である場合だけです。

## プロンプトモード

OpenClaw はサブエージェント向けにより小さいシステムプロンプトをレンダリングできます。ランタイムは各実行に `promptMode` を設定します（ユーザー向け設定ではありません）。

- `full`（デフォルト）: 上記の全セクションを含みます。
- `minimal`: サブエージェントで使われ、**Skills**、**Memory Recall**、**OpenClaw Self-Update**、**Model Aliases**、**User Identity**、**Reply Tags**、**Messaging**、**Silent Replies**、**Heartbeats** を省略します。Tooling、**Safety**、Workspace、Sandbox、Current Date & Time（既知の場合）、Runtime、および注入コンテキストは引き続き利用可能です。
- `none`: ベースの識別 1 行のみを返します。

`promptMode=minimal` の場合、追加で注入されるプロンプトは **Group Chat Context** ではなく **Subagent Context** とラベル付けされます。

## ワークスペースのブートストラップ注入

ブートストラップファイルはトリミングされ、**Project Context** の下に追加されます。これにより、モデルは明示的に読み取らなくても識別情報やプロファイルコンテキストを把握できます。

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`（新規ワークスペースのみ）
- `MEMORY.md` が存在する場合はそれを、存在しない場合は小文字のフォールバックとして `memory.md`

これらのファイルはすべて、**ファイル固有のゲートが適用されない限り**、各ターンで **コンテキストウィンドウに注入** されます。`HEARTBEAT.md` は、通常実行では、デフォルトエージェントで Heartbeat が無効な場合、または
`agents.defaults.heartbeat.includeSystemPromptSection` が false の場合に省略されます。注入ファイルは簡潔に保ってください。特に `MEMORY.md` は時間とともに大きくなりやすく、予想外にコンテキスト使用量が増えたり、Compaction がより頻繁に発生したりする原因になります。

> **注:** `memory/*.md` の日次ファイルは、通常のブートストラップ Project Context の一部では **ありません**。通常ターンでは、これらは
> `memory_search` と `memory_get` ツールを通じて必要時にアクセスされるため、モデルが明示的にそれらを読まない限りコンテキストウィンドウを消費しません。例外は素の `/new` および `/reset` ターンです。この最初のターンでは、ランタイムが最近の日次メモリを 1 回限りの起動コンテキストブロックとして先頭に追加することがあります。

大きなファイルはマーカー付きで切り詰められます。ファイルごとの最大サイズは
`agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で制御されます。ファイル横断で注入されるブートストラップコンテンツ総量は
`agents.defaults.bootstrapTotalMaxChars`（デフォルト: 150000）で上限が設けられています。見つからないファイルは短い missing-file マーカーを注入します。切り詰めが発生した場合、OpenClaw は Project Context に警告ブロックを注入できます。これは
`agents.defaults.bootstrapPromptTruncationWarning`（`off`、`once`、`always`；
デフォルト: `once`）で制御します。

サブエージェントセッションでは `AGENTS.md` と `TOOLS.md` のみが注入されます（サブエージェントコンテキストを小さく保つため、他のブートストラップファイルは除外されます）。

内部フックは `agent:bootstrap` を通じてこのステップを横取りし、注入されるブートストラップファイルを変更または置換できます（たとえば `SOUL.md` を別のペルソナに差し替えるなど）。

エージェントの話し方をより generic でなくしたい場合は、まず
[SOUL.md Personality Guide](/ja-JP/concepts/soul) から始めてください。

各注入ファイルの寄与量（raw と injected、切り詰め、さらにツールスキーマのオーバーヘッド）を確認するには、`/context list` または `/context detail` を使ってください。[Context](/ja-JP/concepts/context) を参照してください。

## 時刻処理

ユーザーのタイムゾーンがわかっている場合、システムプロンプトには専用の **Current Date & Time** セクションが含まれます。プロンプトキャッシュを安定させるため、現在は **タイムゾーン** のみを含みます（動的な時計や時刻形式は含みません）。

エージェントが現在時刻を必要とする場合は `session_status` を使ってください。ステータスカードにはタイムスタンプ行が含まれます。同じツールは、セッションごとのモデル上書きも任意で設定できます（`model=default` でクリアされます）。

設定項目:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat`（`auto` | `12` | `24`）

完全な動作の詳細は [Date & Time](/ja-JP/date-time) を参照してください。

## Skills

条件を満たすスキルが存在する場合、OpenClaw は **利用可能なスキル一覧** をコンパクトに注入します（`formatSkillsForPrompt`）。これには各スキルの **ファイルパス** が含まれます。プロンプトは、列挙された場所（ワークスペース、managed、または bundled）にある SKILL.md を `read` で読み込むようモデルに指示します。条件を満たすスキルがない場合、Skills セクションは省略されます。

適格性には、スキルメタデータのゲート、ランタイム環境／設定チェック、そして `agents.defaults.skills` または
`agents.list[].skills` が設定されている場合の有効なエージェントスキル許可リストが含まれます。

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

これにより、ベースプロンプトを小さく保ちながら、対象を絞ったスキル利用を可能にします。

スキル一覧の予算はスキルサブシステムが管理します。

- グローバルデフォルト: `skills.limits.maxSkillsPromptChars`
- エージェントごとの上書き: `agents.list[].skillsLimits.maxSkillsPromptChars`

一般的な境界付きランタイム抜粋は別のサーフェスを使います。

- `agents.defaults.contextLimits.*`
- `agents.list[].contextLimits.*`

この分離により、スキルのサイズ設定を、`memory_get`、ライブツール結果、Compaction 後の AGENTS.md リフレッシュなどのランタイム読み取り／注入サイズから分けて扱えます。

## Documentation

利用可能な場合、システムプロンプトには **Documentation** セクションが含まれ、ローカルの OpenClaw ドキュメントディレクトリ（リポジトリワークスペース内の `docs/` またはバンドルされた npm パッケージのドキュメント）を指し示します。さらに、公開ミラー、ソースリポジトリ、コミュニティ Discord、そしてスキル発見用の ClawHub（[https://clawhub.ai](https://clawhub.ai)）も記載されます。プロンプトは、OpenClaw の動作、コマンド、設定、またはアーキテクチャについては、まずローカルドキュメントを参照し、可能な場合は `openclaw status` を自分で実行するようモデルに指示します（アクセスできない場合にのみユーザーに尋ねます）。
