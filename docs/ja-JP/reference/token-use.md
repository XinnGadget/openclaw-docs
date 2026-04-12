---
read_when:
    - トークン使用量、コスト、またはコンテキストウィンドウの説明
    - コンテキストの増大や圧縮の挙動のデバッグ
summary: OpenClaw がプロンプトコンテキストを構築する方法と、トークン使用量 + コストを報告する方法
title: トークン使用量とコスト
x-i18n:
    generated_at: "2026-04-12T04:43:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: f8c856549cd28b8364a640e6fa9ec26aa736895c7a993e96cbe85838e7df2dfb
    source_path: reference/token-use.md
    workflow: 15
---

# トークン使用量とコスト

OpenClaw は文字数ではなく、**トークン**を追跡します。トークンはモデルごとに異なりますが、ほとんどの OpenAI スタイルのモデルでは、英語テキストは平均して 1 トークンあたり約 4 文字です。

## システムプロンプトの構築方法

OpenClaw は実行のたびに独自のシステムプロンプトを組み立てます。これには次が含まれます。

- ツール一覧 + 短い説明
- Skills 一覧（メタデータのみ。指示は必要時に `read` で読み込まれます）
- セルフアップデートの指示
- ワークスペース + ブートストラップファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、新規時の `BOOTSTRAP.md`、さらに存在する場合は `MEMORY.md`、または小文字の代替として `memory.md`）。大きなファイルは `agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で切り詰められ、ブートストラップ全体の注入量は `agents.defaults.bootstrapTotalMaxChars`（デフォルト: 150000）で上限設定されます。`memory/*.md` の日次ファイルは通常のブートストラッププロンプトには含まれません。通常のターンではメモリツール経由で必要時に利用されますが、素の `/new` と `/reset` では、最初のターンに限って最近の日次メモリを含むワンショットの起動コンテキストブロックが前置されることがあります。この起動プレリュードは `agents.defaults.startupContext` で制御されます。
- 時刻（UTC + ユーザーのタイムゾーン）
- 返信タグ + ハートビートの挙動
- ランタイムメタデータ（ホスト/OS/モデル/思考）

完全な内訳は [システムプロンプト](/ja-JP/concepts/system-prompt) を参照してください。

## コンテキストウィンドウに含まれるもの

モデルが受け取るものはすべて、コンテキスト上限に対してカウントされます。

- システムプロンプト（上記のすべてのセクション）
- 会話履歴（ユーザー + アシスタントメッセージ）
- ツール呼び出しとツール結果
- 添付ファイル/文字起こし（画像、音声、ファイル）
- 圧縮サマリーと枝刈りアーティファクト
- プロバイダーのラッパーや安全性ヘッダー（表示されませんが、やはりカウントされます）

画像については、OpenClaw はプロバイダー呼び出し前に文字起こし/ツールの画像ペイロードを縮小します。これを調整するには `agents.defaults.imageMaxDimensionPx`（デフォルト: `1200`）を使用します。

- 値を小さくすると、通常はビジョントークン使用量とペイロードサイズが減ります。
- 値を大きくすると、OCR や UI を多く含むスクリーンショットでより多くの視覚的詳細が保持されます。

実用的な内訳（注入された各ファイル、ツール、Skills、システムプロンプトサイズごと）を確認するには、`/context list` または `/context detail` を使ってください。[コンテキスト](/ja-JP/concepts/context) も参照してください。

## 現在のトークン使用量を確認する方法

チャットでは次を使用します。

- `/status` → セッションモデル、コンテキスト使用量、前回応答の入力/出力トークン、**推定コスト**（API キー時のみ）を表示する **絵文字豊富なステータスカード**。
- `/usage off|tokens|full` → すべての返信に **応答ごとの使用量フッター** を追加します。
  - セッション単位で永続化されます（`responseUsage` として保存）。
  - OAuth 認証では **コストは非表示** です（トークンのみ）。
- `/usage cost` → OpenClaw のセッションログからローカルのコスト概要を表示します。

その他の画面:

- **TUI/Web TUI:** `/status` と `/usage` がサポートされています。
- **CLI:** `openclaw status --usage` と `openclaw channels list` は、正規化されたプロバイダーのクォータウィンドウ（応答ごとのコストではなく `X% left`）を表示します。
  現在の使用量ウィンドウ対応プロバイダー: Anthropic、GitHub Copilot、Gemini CLI、OpenAI Codex、MiniMax、Xiaomi、z.ai。

使用量表示では、表示前に一般的なプロバイダーネイティブのフィールド別名を正規化します。OpenAI 系 Responses トラフィックでは、これに `input_tokens` / `output_tokens` と `prompt_tokens` / `completion_tokens` の両方が含まれるため、転送方式固有のフィールド名によって `/status`、`/usage`、またはセッション概要の表示が変わることはありません。
Gemini CLI の JSON 使用量も正規化されます。返信テキストは `response` から取得され、CLI が明示的な `stats.input` フィールドを省略した場合は、`stats.cached` が `cacheRead` に対応付けられ、`stats.input_tokens - stats.cached` が使われます。
ネイティブな OpenAI 系 Responses トラフィックでは、WebSocket/SSE の使用量別名も同様に正規化され、`total_tokens` が欠落しているか `0` の場合は、合計が正規化済みの input + output にフォールバックします。
現在のセッションスナップショットが疎な場合、`/status` と `session_status` は最新の transcript 使用量ログからトークン/キャッシュカウンターやアクティブなランタイムモデルラベルを復元することもできます。既存のゼロ以外のライブ値は引き続き transcript フォールバック値より優先され、保存済み合計が存在しないか小さい場合は、より大きなプロンプト指向の transcript 合計が優先されることがあります。
プロバイダーのクォータウィンドウ用の使用量認証は、利用可能な場合はプロバイダー固有のフックから取得されます。そうでない場合、OpenClaw は auth profile、env、または config から一致する OAuth/API キー資格情報にフォールバックします。

## コスト見積もり（表示される場合）

コストは、モデルの価格設定 config から見積もられます。

```
models.providers.<provider>.models[].cost
```

これらは `input`、`output`、`cacheRead`、`cacheWrite` に対する **100 万トークンあたりの USD** です。価格設定がない場合、OpenClaw はトークンのみを表示します。OAuth トークンではドル建てコストは表示されません。

## キャッシュ TTL と枝刈りの影響

プロバイダーのプロンプトキャッシュは、キャッシュ TTL ウィンドウ内でのみ適用されます。OpenClaw はオプションで **cache-ttl pruning** を実行できます。これは、キャッシュ TTL の期限切れ後にセッションを枝刈りし、その後キャッシュウィンドウをリセットして、以降のリクエストで履歴全体を再キャッシュする代わりに新たにキャッシュされたコンテキストを再利用できるようにするものです。これにより、セッションが TTL を超えてアイドル状態になった場合のキャッシュ書き込みコストを低く保てます。

これは [Gateway configuration](/ja-JP/gateway/configuration) で設定でき、挙動の詳細は [Session pruning](/ja-JP/concepts/session-pruning) を参照してください。

ハートビートは、アイドル期間をまたいでキャッシュを**ウォーム**な状態に保つことができます。モデルのキャッシュ TTL が `1h` の場合、ハートビート間隔をその少し手前（例: `55m`）に設定すると、完全なプロンプトの再キャッシュを避けられ、キャッシュ書き込みコストを減らせます。

マルチエージェント構成では、1 つの共有モデル config を維持しつつ、`agents.list[].params.cacheRetention` でエージェントごとにキャッシュ挙動を調整できます。

各設定項目の完全なガイドについては、[Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。

Anthropic API の価格設定では、キャッシュ読み取りは入力トークンよりかなり安価である一方、キャッシュ書き込みはより高い倍率で課金されます。最新の料金と TTL 倍率については、Anthropic の prompt caching pricing を参照してください:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 例: heartbeat で 1h キャッシュをウォームに保つ

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### 例: エージェントごとのキャッシュ戦略を使った混在トラフィック

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # ほとんどのエージェント向けのデフォルトのベースライン
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # 長時間セッション向けに長いキャッシュをウォームに保つ
    - id: "alerts"
      params:
        cacheRetention: "none" # バースト的な通知ではキャッシュ書き込みを避ける
```

`agents.list[].params` は、選択されたモデルの `params` の上にマージされるため、`cacheRetention` だけを上書きし、他のモデルデフォルトはそのまま継承できます。

### 例: Anthropic 1M context beta ヘッダーを有効化する

Anthropic の 1M コンテキストウィンドウは現在ベータ制限付きです。OpenClaw は、対応する Opus または Sonnet モデルで `context1m` を有効にすると、必要な `anthropic-beta` 値を注入できます。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

これは Anthropic の `context-1m-2025-08-07` beta ヘッダーに対応します。

これは、そのモデルエントリで `context1m: true` が設定されている場合にのみ適用されます。

要件: 資格情報が long-context 利用対象である必要があります。そうでない場合、Anthropic はそのリクエストに対してプロバイダー側のレート制限エラーを返します。

Anthropic を OAuth/サブスクリプショントークン（`sk-ant-oat-*`）で認証している場合、OpenClaw は `context-1m-*` beta ヘッダーをスキップします。これは Anthropic が現在その組み合わせを HTTP 401 で拒否するためです。

## トークン圧迫を減らすためのヒント

- `/compact` を使って長いセッションを要約する。
- ワークフロー内で大きなツール出力を削減する。
- スクリーンショットが多いセッションでは `agents.defaults.imageMaxDimensionPx` を下げる。
- Skill の説明は短く保つ（Skill 一覧はプロンプトに注入されるため）。
- 冗長で探索的な作業には小さいモデルを優先する。

正確な Skill 一覧のオーバーヘッド計算式は [Skills](/ja-JP/tools/skills) を参照してください。
