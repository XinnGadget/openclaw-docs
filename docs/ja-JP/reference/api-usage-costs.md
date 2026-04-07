---
read_when:
    - どの機能が有料APIを呼び出す可能性があるかを理解したい
    - キー、コスト、使用量の可視性を監査する必要がある
    - '`/status` または `/usage` のコスト報告を説明している'
summary: 何が費用を発生させうるか、どのキーが使われるか、使用量をどう確認するかを監査する
title: API使用量とコスト
x-i18n:
    generated_at: "2026-04-07T04:46:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab6eefcde9ac014df6cdda7aaa77ef48f16936ab12eaa883d9fe69425a31a2dd
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# API使用量とコスト

このドキュメントでは、**APIキーを使う可能性がある機能**と、そのコストがどこに表示されるかを一覧化します。対象は、
プロバイダー使用量や有料API呼び出しを発生させる可能性があるOpenClaw機能です。

## コストが表示される場所（チャット + CLI）

**セッションごとのコストスナップショット**

- `/status` は、現在のセッションモデル、コンテキスト使用量、最後の応答トークン数を表示します。
- モデルが**APIキー認証**を使っている場合、`/status` は最後の返信の**推定コスト**も表示します。
- ライブセッションメタデータが少ない場合、`/status` は最新の文字起こし使用量
  エントリからトークン/キャッシュ
  カウンターとアクティブなランタイムモデルラベルを復元できます。既存の非ゼロのライブ値は引き続き優先され、保存済み合計がないか小さい場合は、プロンプトサイズの文字起こし合計が優先されることがあります。

**メッセージごとのコストフッター**

- `/usage full` は、すべての返信に使用量フッターを追加し、**推定コスト**も含めます（APIキーのみ）。
- `/usage tokens` はトークンのみを表示します。サブスクリプション型のOAuth/トークンやCLIフローではドル建てコストは表示されません。
- Gemini CLIに関する注記: CLIがJSON出力を返す場合、OpenClawは
  `stats` から使用量を読み取り、`stats.cached` を `cacheRead` に正規化し、
  必要に応じて `stats.input_tokens - stats.cached` から入力トークン数を導出します。

Anthropicに関する注記: Anthropicの担当者は、OpenClaw方式のClaude CLI利用は
再び許可されていると案内したため、Anthropicが新しいポリシーを公開しない限り、
OpenClawはこの統合においてClaude CLIの再利用と `claude -p` の使用を
認可済みとして扱います。Anthropicは依然として、OpenClawが
`/usage full` に表示できるメッセージ単位のドル建て推定値を公開していません。

**CLI使用量ウィンドウ（プロバイダークォータ）**

- `openclaw status --usage` と `openclaw channels list` は、プロバイダーの**使用量ウィンドウ**
  を表示します
  （メッセージごとのコストではなく、クォータのスナップショット）。
- 人間向け出力は、プロバイダー間で `X% left` に正規化されます。
- 現在の使用量ウィンドウ対応プロバイダー: Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi、z.ai。
- MiniMaxに関する注記: 生の `usage_percent` / `usagePercent` フィールドは残り
  クォータを意味するため、OpenClawは表示前にそれらを反転します。件数ベースのフィールドが存在する場合は、そちらが依然として優先されます。プロバイダーが `model_remains` を返す場合、OpenClawは
  chat-modelエントリを優先し、必要に応じてタイムスタンプからウィンドウラベルを導出し、
  プランラベルにモデル名を含めます。
- これらのクォータウィンドウ向けの使用量認証は、利用可能な場合はプロバイダー固有フックから取得されます。それ以外の場合、OpenClawは認証プロファイル、env、またはconfigから一致するOAuth/APIキー
  認証情報へフォールバックします。

詳細と例は [Token use & costs](/ja-JP/reference/token-use) を参照してください。

## キーの検出方法

OpenClawは次の場所から認証情報を取得できます:

- **認証プロファイル**（エージェントごと、`auth-profiles.json` に保存）。
- **環境変数**（例: `OPENAI_API_KEY`、`BRAVE_API_KEY`、`FIRECRAWL_API_KEY`）。
- **Config**（`models.providers.*.apiKey`、`plugins.entries.*.config.webSearch.apiKey`、
  `plugins.entries.firecrawl.config.webFetch.apiKey`、`memorySearch.*`、
  `talk.providers.*.apiKey`）。
- **Skills**（`skills.entries.<name>.apiKey`）。skillプロセスのenvにキーをエクスポートする場合があります。

## キーを消費する可能性がある機能

### 1) Coreモデル応答（チャット + tools）

すべての返信またはtool呼び出しは、**現在のモデルプロバイダー**（OpenAI、Anthropicなど）を使用します。これが、
使用量とコストの主な発生源です。

これには、OpenClawのローカルUI外で引き続き課金されるサブスクリプション型ホストプロバイダーも含まれます。たとえば **OpenAI Codex**、**Alibaba Cloud Model Studio
Coding Plan**、**MiniMax Coding Plan**、**Z.AI / GLM Coding Plan**、および
**Extra Usage** が有効なAnthropicのOpenClaw Claude-login経路です。

価格設定については [Models](/ja-JP/providers/models)、表示については [Token use & costs](/ja-JP/reference/token-use) を参照してください。

### 2) メディア理解（音声/画像/動画）

受信メディアは、返信実行前に要約/文字起こしされることがあります。これはモデル/プロバイダーAPIを使用します。

- 音声: OpenAI / Groq / Deepgram / Google / Mistral。
- 画像: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI。
- 動画: Google / Qwen / Moonshot。

[Media understanding](/ja-JP/nodes/media-understanding) を参照してください。

### 3) 画像生成と動画生成

共有生成機能もプロバイダーキーを消費することがあります:

- 画像生成: OpenAI / Google / fal / MiniMax
- 動画生成: Qwen

画像生成は、`agents.defaults.imageGenerationModel` が未設定のとき、
認証済みプロバイダーのデフォルトを推論できます。動画生成は現在、
`qwen/wan2.6-t2v` のような明示的な `agents.defaults.videoGenerationModel` を必要とします。

[Image generation](/ja-JP/tools/image-generation)、[Qwen Cloud](/ja-JP/providers/qwen)、
[Models](/ja-JP/concepts/models) を参照してください。

### 4) メモリ埋め込み + セマンティック検索

セマンティックメモリ検索は、リモートプロバイダー向けに設定されている場合、**埋め込みAPI**を使用します:

- `memorySearch.provider = "openai"` → OpenAI embeddings
- `memorySearch.provider = "gemini"` → Gemini embeddings
- `memorySearch.provider = "voyage"` → Voyage embeddings
- `memorySearch.provider = "mistral"` → Mistral embeddings
- `memorySearch.provider = "ollama"` → Ollama embeddings（ローカル/self-hosted。通常はホスト型API課金なし）
- ローカルembeddingsが失敗した場合、任意でリモートプロバイダーへフォールバック

`memorySearch.provider = "local"` を使えばローカルのままにできます（API使用なし）。

[Memory](/ja-JP/concepts/memory) を参照してください。

### 5) Web search tool

`web_search` は、プロバイダーによっては使用料金が発生することがあります:

- **Brave Search API**: `BRAVE_API_KEY` または `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: `EXA_API_KEY` または `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: `FIRECRAWL_API_KEY` または `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: `GEMINI_API_KEY` または `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: `XAI_API_KEY` または `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: `KIMI_API_KEY`、`MOONSHOT_API_KEY`、または `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: `MINIMAX_CODE_PLAN_KEY`、`MINIMAX_CODING_API_KEY`、`MINIMAX_API_KEY`、または `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: デフォルトではキー不要ですが、到達可能なOllamaホストと `ollama signin` が必要です。ホストが必要とする場合は通常のOllama provider bearer authも再利用できます
- **Perplexity Search API**: `PERPLEXITY_API_KEY`、`OPENROUTER_API_KEY`、または `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` または `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: キー不要のフォールバック（API課金なし。ただし非公式でHTMLベース）
- **SearXNG**: `SEARXNG_BASE_URL` または `plugins.entries.searxng.config.webSearch.baseUrl`（キー不要/self-hosted。ホスト型API課金なし）

従来の `tools.web.search.*` provider pathは、一時的な互換shimを通じて引き続き読み込まれますが、推奨されるconfig surfaceではなくなっています。

**Brave Search無料クレジット:** 各Braveプランには、毎月更新される
\$5/月の無料クレジットが含まれます。Searchプランの費用は1,000リクエストあたり\$5のため、このクレジットで
月1,000リクエストまで無料でカバーされます。予期しない請求を避けるため、Braveダッシュボードで使用量上限を設定してください。

[Web tools](/ja-JP/tools/web) を参照してください。

### 5) Web fetch tool（Firecrawl）

APIキーが存在する場合、`web_fetch` は **Firecrawl** を呼び出すことがあります:

- `FIRECRAWL_API_KEY` または `plugins.entries.firecrawl.config.webFetch.apiKey`

Firecrawlが設定されていない場合、このtoolは直接fetch + readabilityへフォールバックします（有料APIなし）。

[Web tools](/ja-JP/tools/web) を参照してください。

### 6) プロバイダー使用量スナップショット（status/health）

一部のstatusコマンドは、クォータウィンドウや認証ヘルスを表示するために**プロバイダー使用量エンドポイント**を呼び出します。
通常は少量の呼び出しですが、それでもプロバイダーAPIにはアクセスします:

- `openclaw status --usage`
- `openclaw models status --json`

[Models CLI](/cli/models) を参照してください。

### 7) コンパクション保護の要約

コンパクション保護は、**現在のモデル**を使ってセッション履歴を要約することがあり、
実行時にはプロバイダーAPIを呼び出します。

[Session management + compaction](/ja-JP/reference/session-management-compaction) を参照してください。

### 8) モデルscan / probe

`openclaw models scan` はOpenRouterモデルをprobeでき、有効時には `OPENROUTER_API_KEY` を使用します
。

[Models CLI](/cli/models) を参照してください。

### 9) Talk（音声）

Talk modeは、設定されている場合 **ElevenLabs** を呼び出すことがあります:

- `ELEVENLABS_API_KEY` または `talk.providers.elevenlabs.apiKey`

[Talk mode](/ja-JP/nodes/talk) を参照してください。

### 10) Skills（サードパーティAPI）

Skillsは `skills.entries.<name>.apiKey` に `apiKey` を保存できます。skillがそのキーを外部
APIに使用する場合、そのskillのプロバイダーに応じてコストが発生することがあります。

[Skills](/ja-JP/tools/skills) を参照してください。
