---
read_when:
    - トークン使用量、コスト、またはコンテキストウィンドウの説明
    - コンテキストの増大やCompactionの挙動をデバッグすること
summary: OpenClawがどのようにプロンプトコンテキストを構築し、トークン使用量とコストを報告するか
title: トークン使用量とコスト
x-i18n:
    generated_at: "2026-04-15T19:42:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9a706d3df8b2ea1136b3535d216c6b358e43aee2a31a4759824385e1345e6fe5
    source_path: reference/token-use.md
    workflow: 15
---

# トークン使用量とコスト

OpenClawは**文字数**ではなく**トークン**を追跡します。トークンはモデル固有ですが、ほとんどのOpenAI系モデルでは英語テキストで平均して1トークンあたり約4文字です。

## システムプロンプトの構築方法

OpenClawは実行のたびに独自のシステムプロンプトを組み立てます。これには次が含まれます:

- ツール一覧 + 短い説明
- Skills一覧（メタデータのみ。指示は必要時に `read` で読み込まれます）。
  コンパクトなSkillsブロックは `skills.limits.maxSkillsPromptChars` によって制限され、
  エージェントごとのオーバーライドとして
  `agents.list[].skillsLimits.maxSkillsPromptChars` を設定することもできます。
- 自己更新の指示
- ワークスペース + ブートストラップファイル（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、新規時の `BOOTSTRAP.md`、および存在する場合の `MEMORY.md` または小文字フォールバックの `memory.md`）。大きなファイルは `agents.defaults.bootstrapMaxChars`（デフォルト: 12000）で切り詰められ、ブートストラップ注入全体は `agents.defaults.bootstrapTotalMaxChars`（デフォルト: 60000）で上限が設定されます。`memory/*.md` の日次ファイルは通常のブートストラッププロンプトには含まれません。通常のターンではメモリツール経由のオンデマンドのままですが、素の `/new` と `/reset` では、最初のターンに限り最近の日次メモリを含むワンショットの起動コンテキストブロックを先頭に追加できます。この起動プレリュードは `agents.defaults.startupContext` で制御されます。
- 時刻（UTC + ユーザーのタイムゾーン）
- 返信タグ + Heartbeatの挙動
- ランタイムメタデータ（ホスト/OS/モデル/thinking）

完全な内訳は [System Prompt](/ja-JP/concepts/system-prompt) を参照してください。

## コンテキストウィンドウに含まれるもの

モデルが受け取るものはすべてコンテキスト上限に含まれます:

- システムプロンプト（上記の全セクション）
- 会話履歴（ユーザー + アシスタントメッセージ）
- ツール呼び出しとツール結果
- 添付ファイル/文字起こし（画像、音声、ファイル）
- Compactionの要約とpruning成果物
- Providerラッパーや安全性ヘッダー（表示はされませんが、カウント対象です）

ランタイム負荷の高い一部のサーフェスには、独自の明示的な上限があります:

- `agents.defaults.contextLimits.memoryGetMaxChars`
- `agents.defaults.contextLimits.memoryGetDefaultLines`
- `agents.defaults.contextLimits.toolResultMaxChars`
- `agents.defaults.contextLimits.postCompactionMaxChars`

エージェントごとのオーバーライドは `agents.list[].contextLimits` の下にあります。これらのノブは、
上限付きのランタイム抜粋と、ランタイム所有の注入ブロックに対するものです。これらは
ブートストラップ上限、起動コンテキスト上限、Skillsプロンプト上限とは別です。

画像については、OpenClawはProvider呼び出し前に文字起こし/ツール画像ペイロードを縮小します。
これを調整するには `agents.defaults.imageMaxDimensionPx`（デフォルト: `1200`）を使用します:

- 値を低くすると、通常はvisionトークン使用量とペイロードサイズが減少します。
- 値を高くすると、OCRやUI中心のスクリーンショットでより多くの視覚的詳細を保持できます。

実用的な内訳（注入された各ファイル、ツール、Skills、システムプロンプトサイズごと）を確認するには、`/context list` または `/context detail` を使用してください。[Context](/ja-JP/concepts/context) を参照してください。

## 現在のトークン使用量を確認する方法

チャットでは次を使用します:

- `/status` → セッションモデル、コンテキスト使用量、
  直近の応答の入力/出力トークン、および**推定コスト**（APIキーのみ）を表示する
  **絵文字豊富なステータスカード**。
- `/usage off|tokens|full` → すべての返信に**応答ごとの使用量フッター**を追加します。
  - セッションごとに保持されます（`responseUsage` として保存）。
  - OAuth認証では**コストは非表示**です（トークンのみ）。
- `/usage cost` → OpenClawのセッションログからローカルのコスト概要を表示します。

その他のサーフェス:

- **TUI/Web TUI:** `/status` + `/usage` がサポートされています。
- **CLI:** `openclaw status --usage` と `openclaw channels list` は
  正規化されたProviderクォータウィンドウ（`X% left`。応答ごとのコストではありません）を表示します。
  現在の使用量ウィンドウ対応Provider: Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi、z.ai。

使用量サーフェスは、表示前に一般的なProviderネイティブのフィールド別名を正規化します。
OpenAI系のResponsesトラフィックでは、これに `input_tokens` /
`output_tokens` と `prompt_tokens` / `completion_tokens` の両方が含まれるため、トランスポート固有の
フィールド名によって `/status`、`/usage`、またはセッション要約が変わることはありません。
Gemini CLIのJSON使用量も正規化されます: 返信テキストは `response` から取得され、
CLIが明示的な `stats.input` フィールドを省略した場合は、`stats.cached` は `cacheRead` にマップされ、
`stats.input_tokens - stats.cached` が使用されます。
ネイティブなOpenAI系Responsesトラフィックでは、WebSocket/SSEの使用量別名も同様に正規化され、
`total_tokens` が欠けているか `0` の場合は、正規化された入力 + 出力から合計が補完されます。
現在のセッションスナップショットが疎な場合、`/status` と `session_status` は
直近の文字起こし使用量ログからトークン/キャッシュカウンターとアクティブなランタイムモデルラベルを復元することもできます。
既存のゼロ以外のライブ値は、引き続き文字起こしのフォールバック値より優先され、
保存済み合計が欠けているか小さい場合には、より大きいプロンプト指向の文字起こし合計が優先されることがあります。
Providerクォータウィンドウの使用量認証は、利用可能な場合はProvider固有のフックから取得されます。
それ以外の場合、OpenClawは認証プロファイル、環境変数、または設定から一致するOAuth/APIキー資格情報へフォールバックします。

## コスト見積もり（表示される場合）

コストはモデルの価格設定から見積もられます:

```
models.providers.<provider>.models[].cost
```

これらは `input`、`output`、`cacheRead`、`cacheWrite` に対する**100万トークンあたりのUSD**です。
価格設定がない場合、OpenClawはトークンのみを表示します。OAuthトークンでは
ドルコストは表示されません。

## キャッシュTTLとpruningの影響

Providerのプロンプトキャッシュは、キャッシュTTLウィンドウ内でのみ適用されます。OpenClawは
オプションで**cache-ttl pruning**を実行できます: キャッシュTTLの有効期限が切れたらセッションをpruneし、
その後キャッシュウィンドウをリセットして、後続のリクエストが履歴全体を再キャッシュする代わりに
新たにキャッシュされたコンテキストを再利用できるようにします。これにより、セッションがTTLを超えて
アイドル状態になった場合のキャッシュ書き込みコストを低く保てます。

これを設定するには [Gateway configuration](/ja-JP/gateway/configuration) を参照し、
挙動の詳細は [Session pruning](/ja-JP/concepts/session-pruning) を参照してください。

Heartbeatは、アイドルギャップをまたいでキャッシュを**温かい**状態に保つことができます。モデルのキャッシュTTLが
`1h` の場合、Heartbeat間隔をそれより少し短く（例: `55m`）設定すると、
完全なプロンプトの再キャッシュを避けられ、キャッシュ書き込みコストを削減できます。

マルチエージェント構成では、共有のモデル設定を1つ保ちつつ、
`agents.list[].params.cacheRetention` でエージェントごとにキャッシュ挙動を調整できます。

各ノブの完全ガイドは [Prompt Caching](/ja-JP/reference/prompt-caching) を参照してください。

Anthropic APIの価格設定では、cache readはinputトークンより大幅に安価である一方、
cache writeはより高い倍率で課金されます。最新の料金とTTL倍率については、
Anthropicのプロンプトキャッシュ料金を参照してください:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 例: Heartbeatで1時間キャッシュを温かい状態に保つ

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

### 例: エージェントごとのキャッシュ戦略を使った混合トラフィック

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # default baseline for most agents
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # keep long cache warm for deep sessions
    - id: "alerts"
      params:
        cacheRetention: "none" # avoid cache writes for bursty notifications
```

`agents.list[].params` は選択されたモデルの `params` の上にマージされるため、
`cacheRetention` のみをオーバーライドし、他のモデルデフォルトはそのまま継承できます。

### 例: Anthropicの1Mコンテキストベータヘッダーを有効にする

Anthropicの1Mコンテキストウィンドウは現在ベータ制限付きです。OpenClawでは、
サポートされているOpusまたはSonnetモデルで `context1m` を有効にすると、
必要な `anthropic-beta` 値を注入できます。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

これはAnthropicの `context-1m-2025-08-07` ベータヘッダーにマップされます。

これは、そのモデルエントリで `context1m: true` が設定されている場合にのみ適用されます。

要件: 資格情報がロングコンテキスト利用の対象である必要があります。そうでない場合、
Anthropicはそのリクエストに対してProvider側のレート制限エラーを返します。

AnthropicをOAuth/サブスクリプショントークン（`sk-ant-oat-*`）で認証している場合、
Anthropicは現在その組み合わせをHTTP 401で拒否するため、OpenClawは
`context-1m-*` ベータヘッダーをスキップします。

## トークン負荷を減らすためのヒント

- 長いセッションは `/compact` を使って要約します。
- ワークフロー内で大きなツール出力を切り詰めます。
- スクリーンショット中心のセッションでは `agents.defaults.imageMaxDimensionPx` を下げます。
- Skillの説明は短く保ちます（Skill一覧はプロンプトに注入されます）。
- 冗長で探索的な作業には、より小さいモデルを優先します。

正確なSkill一覧のオーバーヘッド計算式については [Skills](/ja-JP/tools/skills) を参照してください。
