---
read_when:
    - OpenClaw が提供するツールを理解したい
    - ツールを設定、許可、または拒否する必要がある
    - 組み込みツール、Skills、plugin のどれを使うべきか判断している
summary: 'OpenClaw のツールと plugin の概要: エージェントができることと拡張方法'
title: ツールとプラグイン
x-i18n:
    generated_at: "2026-04-06T03:13:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: b2371239316997b0fe389bfa2ec38404e1d3e177755ad81ff8035ac583d9adeb
    source_path: tools/index.md
    workflow: 15
---

# ツールとプラグイン

エージェントがテキスト生成以外のことを行うときは、すべて **tools** を通じて行われます。
tools は、エージェントがファイルを読み、コマンドを実行し、Web を閲覧し、メッセージを送り、
デバイスと対話する方法です。

## tools、skills、plugin

OpenClaw には、連携して動作する3つのレイヤーがあります。

<Steps>
  <Step title="tools はエージェントが呼び出すもの">
    tool は、エージェントが呼び出せる型付き関数です（例: `exec`、`browser`、
    `web_search`、`message`）。OpenClaw には一連の**組み込み tools** が含まれており、
    plugin は追加のものを登録できます。

    エージェントは、tools をモデル API に送られる構造化関数定義として認識します。

  </Step>

  <Step title="Skills はいつどのように使うかを教える">
    skill は、システムプロンプトに注入される markdown ファイル（`SKILL.md`）です。
    Skills は、tools を効果的に使うためのコンテキスト、制約、段階的なガイダンスを
    エージェントに与えます。Skills はワークスペース、共有フォルダー、
    または plugin 内に配置されます。

    [Skills reference](/ja-JP/tools/skills) | [Creating skills](/ja-JP/tools/creating-skills)

  </Step>

  <Step title="plugin はすべてをまとめてパッケージ化する">
    plugin は、さまざまな機能の組み合わせを登録できるパッケージです:
    チャネル、モデルプロバイダー、tools、skills、音声、リアルタイム文字起こし、
    リアルタイム音声、メディア理解、画像生成、動画生成、
    Web fetch、Web search などです。一部の plugin は **core**（
    OpenClaw に同梱）であり、他は **external**（コミュニティが npm で公開）
    です。

    [Install and configure plugins](/ja-JP/tools/plugin) | [Build your own](/ja-JP/plugins/building-plugins)

  </Step>
</Steps>

## 組み込みツール

これらのツールは OpenClaw に同梱されており、plugin をインストールしなくても利用できます。

| Tool                                       | 内容                                                                  | ページ                                       |
| ------------------------------------------ | --------------------------------------------------------------------- | -------------------------------------------- |
| `exec` / `process`                         | シェルコマンドを実行し、バックグラウンドプロセスを管理する            | [Exec](/ja-JP/tools/exec)                          |
| `code_execution`                           | サンドボックス化されたリモート Python 分析を実行する                  | [Code Execution](/ja-JP/tools/code-execution)      |
| `browser`                                  | Chromium ブラウザーを操作する（ナビゲート、クリック、スクリーンショット） | [Browser](/ja-JP/tools/browser)                |
| `web_search` / `x_search` / `web_fetch`    | Web を検索し、X 投稿を検索し、ページ内容を取得する                    | [Web](/ja-JP/tools/web)                            |
| `read` / `write` / `edit`                  | ワークスペース内でファイル I/O を行う                                 |                                              |
| `apply_patch`                              | 複数 hunk のファイルパッチ                                            | [Apply Patch](/ja-JP/tools/apply-patch)            |
| `message`                                  | すべてのチャネルへメッセージを送信する                                | [Agent Send](/ja-JP/tools/agent-send)              |
| `canvas`                                   | ノード Canvas を操作する（present、eval、snapshot）                   |                                              |
| `nodes`                                    | ペアリング済みデバイスを検出して対象指定する                          |                                              |
| `cron` / `gateway`                         | スケジュール済みジョブを管理し、gateway を調査、patch、再起動、更新する |                                              |
| `image` / `image_generate`                 | 画像を解析または生成する                                              | [Image Generation](/ja-JP/tools/image-generation)  |
| `music_generate`                           | 音楽トラックを生成する                                                | [Music Generation](/tools/music-generation)  |
| `video_generate`                           | 動画を生成する                                                        | [Video Generation](/tools/video-generation)  |
| `tts`                                      | 単発の text-to-speech 変換                                            | [TTS](/ja-JP/tools/tts)                            |
| `sessions_*` / `subagents` / `agents_list` | セッション管理、ステータス、サブエージェントのオーケストレーション    | [Sub-agents](/ja-JP/tools/subagents)               |
| `session_status`                           | 軽量な `/status` 風の読み戻しとセッション単位のモデル上書き           | [Session Tools](/ja-JP/concepts/session-tool)      |

画像関連では、解析には `image` を、生成または編集には `image_generate` を使用します。`openai/*`、`google/*`、`fal/*`、または他の非デフォルト画像プロバイダーを対象にする場合は、まずそのプロバイダーの認証/API キーを設定してください。

音楽関連では、`music_generate` を使用します。`google/*`、`minimax/*`、または他の非デフォルト音楽プロバイダーを対象にする場合は、まずそのプロバイダーの認証/API キーを設定してください。

動画関連では、`video_generate` を使用します。`qwen/*` または他の非デフォルト動画プロバイダーを対象にする場合は、まずそのプロバイダーの認証/API キーを設定してください。

ワークフロー駆動の音声生成では、ComfyUI のような plugin が
それを登録している場合は `music_generate` を使用します。これは `tts` とは別物で、
`tts` は text-to-speech です。

`session_status` は sessions グループにある軽量なステータス/読み戻しツールです。
これは現在のセッションに関する `/status` 風の質問に答え、
任意でセッション単位のモデル上書きを設定できます。`model=default` はその
上書きをクリアします。`/status` と同様に、最新の transcript usage エントリから、
不足している token/cache カウンターとアクティブなランタイムモデルラベルを
補完できます。

`gateway` は、gateway 操作用の owner-only ランタイムツールです。

- 編集前に、1つの path スコープ付き設定サブツリーを確認する `config.schema.lookup`
- 現在の設定スナップショット + ハッシュを取得する `config.get`
- 再起動付きの部分設定更新を行う `config.patch`
- 完全設定の置換時にのみ使う `config.apply`
- 明示的な self-update + 再起動を行う `update.run`

部分変更では、`config.schema.lookup` の後に `config.patch` を使うことを推奨します。
設定全体を意図的に置き換える場合にのみ `config.apply` を使用してください。
また、このツールは `tools.exec.ask` または `tools.exec.security` の変更を拒否します。
旧式の `tools.bash.*` エイリアスは、同じ保護された exec パスへ正規化されます。

### plugin 提供ツール

plugin は追加のツールを登録できます。例:

- [Lobster](/ja-JP/tools/lobster) — 再開可能な承認を持つ型付きワークフローランタイム
- [LLM Task](/ja-JP/tools/llm-task) — 構造化出力向けの JSON 専用 LLM ステップ
- [Music Generation](/tools/music-generation) — ワークフロー駆動プロバイダーを持つ共有 `music_generate` ツール
- [Diffs](/ja-JP/tools/diffs) — diff ビューアーとレンダラー
- [OpenProse](/ja-JP/prose) — markdown-first のワークフローオーケストレーション

## ツール設定

### 許可リストと拒否リスト

設定内の `tools.allow` / `tools.deny` で、エージェントが呼び出せるツールを制御します。
拒否は常に許可より優先されます。

```json5
{
  tools: {
    allow: ["group:fs", "browser", "web_search"],
    deny: ["exec"],
  },
}
```

### ツールプロファイル

`tools.profile` は、`allow`/`deny` が適用される前のベース許可リストを設定します。
エージェント単位の上書き: `agents.list[].tools.profile`。

| Profile     | 含まれるもの                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| `full`      | 制限なし（未設定と同じ）                                                                                                                          |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `music_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                                         |
| `minimal`   | `session_status` のみ                                                                                                                             |

### ツールグループ

allow/deny リストでは `group:*` の短縮表記を使います。

| Group              | Tools                                                                                                     |
| ------------------ | --------------------------------------------------------------------------------------------------------- |
| `group:runtime`    | exec, process, code_execution（`bash` は `exec` のエイリアスとして受け付けられます）                     |
| `group:fs`         | read, write, edit, apply_patch                                                                            |
| `group:sessions`   | sessions_list, sessions_history, sessions_send, sessions_spawn, sessions_yield, subagents, session_status |
| `group:memory`     | memory_search, memory_get                                                                                 |
| `group:web`        | web_search, x_search, web_fetch                                                                           |
| `group:ui`         | browser, canvas                                                                                           |
| `group:automation` | cron, gateway                                                                                             |
| `group:messaging`  | message                                                                                                   |
| `group:nodes`      | nodes                                                                                                     |
| `group:agents`     | agents_list                                                                                               |
| `group:media`      | image, image_generate, music_generate, video_generate, tts                                                |
| `group:openclaw`   | すべての組み込み OpenClaw tools（plugin tools は除外）                                                    |

`sessions_history` は、境界付きで安全性フィルター済みのリコールビューを返します。これは
thinking タグ、`<relevant-memories>` の足場、
平文の tool-call XML ペイロード（`<tool_call>...</tool_call>`、
`<function_call>...</function_call>`、`<tool_calls>...</tool_calls>`、
`<function_calls>...</function_calls>`、および切り詰められた tool-call ブロックを含む）、
格下げされた tool-call 足場、漏れた ASCII/全角のモデル制御
トークン、壊れた MiniMax tool-call XML を assistant テキストから除去し、その後
リダクション/切り詰めと、必要に応じて oversized-row プレースホルダーを適用するため、
生の transcript ダンプとしては動作しません。

### プロバイダー固有の制限

グローバルデフォルトを変えずに、特定のプロバイダー用にツールを制限するには `tools.byProvider` を使用します。

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```
