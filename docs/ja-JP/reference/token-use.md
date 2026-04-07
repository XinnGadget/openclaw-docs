---
read_when:
    - トークン使用量、コスト、またはコンテキストウィンドウを説明する場合
    - コンテキストの増大やcompactionの動作をデバッグする場合
summary: OpenClawがプロンプトコンテキストをどのように構築し、トークン使用量とコストをどのように報告するか
title: トークン使用量とコスト
x-i18n:
    generated_at: "2026-04-07T04:46:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0683693d6c6fcde7d5fba236064ba97dd4b317ae6bea3069db969fcd178119d9
    source_path: reference/token-use.md
    workflow: 15
---

# トークン使用量とコスト

OpenClawは**文字数**ではなく**トークン**を追跡します。トークンはモデル固有ですが、ほとんどの
OpenAIスタイルのモデルでは、英語テキストで平均すると1トークンあたり約4文字です。

## system promptの構築方法

OpenClawは、実行のたびに独自のsystem promptを組み立てます。これには次が含まれます:

- Tool一覧 + 短い説明
- Skills一覧（メタデータのみ。指示は必要時に`read`で読み込まれます）
- self-update instructions
- Workspace + bootstrap files（`AGENTS.md`、`SOUL.md`、`TOOLS.md`、`IDENTITY.md`、`USER.md`、`HEARTBEAT.md`、新規の場合は`BOOTSTRAP.md`、さらに存在する場合は`MEMORY.md`、または小文字フォールバックとして`memory.md`）。大きなファイルは`agents.defaults.bootstrapMaxChars`（デフォルト: 20000）で切り詰められ、bootstrap注入全体は`agents.defaults.bootstrapTotalMaxChars`（デフォルト: 150000）で上限設定されます。`memory/*.md`ファイルはmemory tools経由のオンデマンドであり、自動注入されません。
- 時刻（UTC + ユーザーのタイムゾーン）
- 返信タグ + heartbeat behavior
- runtime metadata（host/OS/model/thinking）

完全な内訳は[System Prompt](/ja-JP/concepts/system-prompt)を参照してください。

## context windowに含まれるもの

モデルが受け取るものは、すべてcontext limitに含まれます:

- System prompt（上記のすべてのセクション）
- 会話履歴（user + assistant messages）
- Tool callsとtool results
- 添付ファイル/transcripts（画像、音声、ファイル）
- compaction summariesとpruning artifacts
- provider wrappersまたはsafety headers（見えませんが、それでもカウントされます）

画像については、OpenClawはprovider呼び出し前にtranscript/tool画像payloadsを縮小します。
これを調整するには`agents.defaults.imageMaxDimensionPx`（デフォルト: `1200`）を使用します:

- 値を低くすると、通常はvision-token使用量とpayloadサイズが減ります。
- 値を高くすると、OCR/UIが多いスクリーンショットでより多くの視覚的詳細を保持できます。

実用的な内訳（注入されたファイルごと、tools、Skills、およびsystem promptサイズごと）を確認するには、`/context list`または`/context detail`を使用してください。[Context](/ja-JP/concepts/context)を参照してください。

## 現在のトークン使用量を見る方法

チャットでは次を使用します:

- `/status` → セッションモデル、context使用量、
  直近の応答の入力/出力トークン、および**推定コスト**（APIキーのみ）を含む**絵文字付きのステータスカード**。
- `/usage off|tokens|full` → すべての返信に**応答ごとの使用量フッター**を追加します。
  - セッションごとに保持されます（`responseUsage`として保存）。
  - OAuth authでは**コストは非表示**になります（トークンのみ）。
- `/usage cost` → OpenClawのセッションログからローカルのコスト概要を表示します。

その他の表面:

- **TUI/Web TUI:** `/status`と`/usage`がサポートされています。
- **CLI:** `openclaw status --usage`と`openclaw channels list`は
  正規化されたprovider quota windows（応答ごとのコストではなく`X% left`）を表示します。
  現在のusage-window対応provider: Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi、z.ai。

使用量の表示面では、表示前に共通のproviderネイティブfield aliasesを正規化します。
OpenAI系Responsesトラフィックでは、`input_tokens` /
`output_tokens`と`prompt_tokens` / `completion_tokens`の両方が含まれるため、transport固有の
field namesによって`/status`、`/usage`、またはセッション概要の表示が変わることはありません。
Gemini CLI JSON usageも正規化されます: reply textは`response`から取得され、
CLIが明示的な`stats.input` fieldを省略した場合は、`stats.cached`が`cacheRead`に対応付けられ、`stats.input_tokens - stats.cached`
が使用されます。
ネイティブOpenAI系Responsesトラフィックでは、WebSocket/SSE usage aliasesも
同じ方法で正規化され、`total_tokens`が存在しない、または`0`の場合は、合計値は正規化済みのinput + outputへフォールバックします。
現在のセッションスナップショットが疎な場合、`/status`と`session_status`は
最新のtranscript usage logからトークン/cache countersおよびアクティブなruntime model labelも復元できます。既存のゼロ以外のlive値は引き続きtranscript fallback値より優先され、保存済み合計が存在しないか小さい場合は、より大きいprompt指向の
transcript totalsが優先されることがあります。
provider quota windows用のusage authは、利用可能な場合はprovider固有のhooksから取得されます。そうでない場合、OpenClawはauth profiles、env、またはconfigから一致するOAuth/API-key credentialsへフォールバックします。

## コスト見積もり（表示される場合）

コストは、モデル価格設定configから見積もられます:

```
models.providers.<provider>.models[].cost
```

これらは`input`、`output`、`cacheRead`、`cacheWrite`に対する**100万トークンあたりのUSD**です。
価格設定がない場合、OpenClawはトークンのみを表示します。OAuth tokensでは
ドルコストは表示されません。

## Cache TTLとpruningの影響

provider prompt cachingは、cache TTL window内でのみ適用されます。OpenClawは
必要に応じて**cache-ttl pruning**を実行できます: cache TTLが期限切れになるとセッションをpruneし、
次のリクエストで履歴全体を再キャッシュするのではなく、新しくキャッシュされたコンテキストを再利用できるよう
cache windowをリセットします。これにより、セッションがTTLを超えてアイドル状態になったときのcache
writeコストを低く保てます。

これは[Gateway configuration](/ja-JP/gateway/configuration)で設定し、
動作の詳細は[Session pruning](/ja-JP/concepts/session-pruning)を参照してください。

Heartbeatは、アイドル間隔をまたいでcacheを**warm**に保つことができます。モデルのcache TTL
が`1h`なら、heartbeat intervalをそれより少し短く設定する（例: `55m`）ことで、
プロンプト全体の再キャッシュを避け、cache writeコストを減らせます。

マルチエージェント構成では、1つの共有モデルconfigを維持したまま、
`agents.list[].params.cacheRetention`でエージェントごとにcache動作を調整できます。

各設定項目を順に確認する完全ガイドについては、[Prompt Caching](/ja-JP/reference/prompt-caching)を参照してください。

Anthropic APIの価格設定では、cache readはinput
tokensより大幅に安価である一方、cache writeはより高い倍率で課金されます。最新の料金とTTL倍率については、Anthropicの
prompt caching価格設定を参照してください:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 例: heartbeatで1時間のcacheをwarmに保つ

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

### 例: エージェントごとのcache戦略を持つ混在トラフィック

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # most agents向けのデフォルトベースライン
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # 深いセッション向けにlong cacheをwarmに保つ
    - id: "alerts"
      params:
        cacheRetention: "none" # bursty notifications向けにcache writesを避ける
```

`agents.list[].params`は選択されたモデルの`params`の上にマージされるため、
`cacheRetention`だけを上書きし、その他のモデルデフォルトはそのまま継承できます。

### 例: Anthropic 1M context beta headerを有効にする

Anthropicの1M context windowは現在beta-gatedです。OpenClawは、サポートされるOpus
またはSonnetモデルで`context1m`を有効にすると、必要な
`anthropic-beta`値を注入できます。

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

これはAnthropicの`context-1m-2025-08-07` beta headerに対応します。

これは、そのモデルエントリで`context1m: true`が設定されている場合にのみ適用されます。

要件: credentialがlong-context usageの対象である必要があります。対象でない場合、
Anthropicはそのリクエストに対してprovider-side rate limit errorを返します。

AnthropicをOAuth/subscription tokens（`sk-ant-oat-*`）で認証している場合、
Anthropicは現在その組み合わせをHTTP 401で拒否するため、OpenClawは`context-1m-*`
beta headerをスキップします。

## トークン圧力を減らすためのヒント

- 長いセッションの要約には`/compact`を使用してください。
- ワークフロー内の大きなtool outputsを切り詰めてください。
- スクリーンショットが多いセッションでは`agents.defaults.imageMaxDimensionPx`を下げてください。
- skill descriptionsは短く保ってください（skill listはプロンプトに注入されます）。
- 冗長で探索的な作業には、より小さなモデルを選んでください。

skill listの正確なオーバーヘッド計算式については、[Skills](/ja-JP/tools/skills)を参照してください。
