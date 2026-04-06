---
read_when:
    - プロバイダーごとのモデル設定リファレンスが必要である
    - モデルプロバイダー向けの設定例やCLIオンボーディングコマンドが必要である
summary: モデルプロバイダーの概要と設定例 + CLIフロー
title: モデルプロバイダー
x-i18n:
    generated_at: "2026-04-06T03:08:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 15e4b82e07221018a723279d309e245bb4023bc06e64b3c910ef2cae3dfa2599
    source_path: concepts/model-providers.md
    workflow: 15
---

# モデルプロバイダー

このページでは**LLM/モデルプロバイダー**を扱います（WhatsApp/Telegramのようなチャットチャネルではありません）。
モデル選択ルールについては[/concepts/models](/ja-JP/concepts/models)を参照してください。

## クイックルール

- モデル参照は`provider/model`を使用します（例: `opencode/claude-opus-4-6`）。
- `agents.defaults.models`を設定すると、それが許可リストになります。
- CLIヘルパー: `openclaw onboard`、`openclaw models list`、`openclaw models set <provider/model>`
- フォールバックのランタイムルール、クールダウンプローブ、セッションオーバーライドの永続化については[/concepts/model-failover](/ja-JP/concepts/model-failover)に記載されています。
- `models.providers.*.models[].contextWindow`はネイティブなモデルメタデータです。
  `models.providers.*.models[].contextTokens`は実効ランタイム上限です。
- プロバイダープラグインは`registerProvider({ catalog })`を通じてモデルカタログを注入できます。
  OpenClawはその出力を`models.providers`にマージしてから
  `models.json`を書き込みます。
- プロバイダーマニフェストは`providerAuthEnvVars`を宣言できるため、汎用の環境変数ベース認証プローブでプラグインランタイムをロードする必要がありません。残るコアの環境変数マップは、非プラグイン/コアプロバイダーと、AnthropicのAPIキー優先オンボーディングのような一部の汎用優先順位ケース向けのみになっています。
- プロバイダープラグインは以下を通じてプロバイダーランタイム動作も所有できます:
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, および
  `onModelSelected`。
- 注: プロバイダーランタイムの`capabilities`は共有ランナーメタデータ（プロバイダーファミリー、トランスクリプト/ツールの癖、トランスポート/キャッシュのヒント）です。これは、プラグインが何を登録するか（テキスト推論、音声など）を記述する[公開 capability model](/ja-JP/plugins/architecture#public-capability-model)とは異なります。

## プラグイン所有のプロバイダー動作

OpenClawが汎用推論ループを維持しつつ、プロバイダープラグインが大半のプロバイダー固有ロジックを所有できるようになりました。

典型的な分担:

- `auth[].run` / `auth[].runNonInteractive`: プロバイダーが`openclaw onboard`、`openclaw models auth`、およびヘッドレスセットアップ向けのオンボーディング/ログインフローを所有
- `wizard.setup` / `wizard.modelPicker`: プロバイダーが認証選択ラベル、レガシーエイリアス、オンボーディング許可リストのヒント、およびオンボーディング/モデルピッカー内のセットアップ項目を所有
- `catalog`: プロバイダーが`models.providers`に表示される
- `normalizeModelId`: プロバイダーが、検索または正規化の前にレガシー/プレビューモデルIDを正規化
- `normalizeTransport`: プロバイダーが、汎用モデル組み立ての前にトランスポート系の`api` / `baseUrl`を正規化します。OpenClawはまず一致したプロバイダーを確認し、その後、いずれかが実際にトランスポートを変更するまで他のフック対応プロバイダープラグインを確認します
- `normalizeConfig`: プロバイダーが、ランタイムが使用する前に`models.providers.<id>`設定を正規化します。OpenClawはまず一致したプロバイダーを確認し、その後、いずれかが実際に設定を変更するまで他のフック対応プロバイダープラグインを確認します。どのプロバイダーフックも設定を書き換えない場合、バンドルされたGoogle系ヘルパーが引き続きサポート対象Googleプロバイダー設定を正規化します
- `applyNativeStreamingUsageCompat`: プロバイダーが、設定プロバイダー向けにエンドポイント駆動のネイティブストリーミング使用量互換リライトを適用
- `resolveConfigApiKey`: プロバイダーが、設定プロバイダー向けに完全なランタイム認証ロードを強制せずに環境変数マーカー認証を解決します。`amazon-bedrock`は、Bedrockランタイム認証がAWS SDKデフォルトチェーンを使うにもかかわらず、ここでもAWS環境変数マーカーリゾルバーを内蔵しています
- `resolveSyntheticAuth`: プロバイダーが、平文シークレットを永続化せずにローカル/セルフホストまたはその他の設定ベース認証の利用可否を公開可能
- `shouldDeferSyntheticProfileAuth`: プロバイダーが、保存済みの合成プロファイルプレースホルダーを環境変数/設定ベース認証より低優先と見なすよう指定可能
- `resolveDynamicModel`: プロバイダーが、ローカル静的カタログにまだ存在しないモデルIDを受け入れる
- `prepareDynamicModel`: プロバイダーが、動的解決を再試行する前にメタデータ更新を必要とする
- `normalizeResolvedModel`: プロバイダーが、トランスポートまたはbase URLのリライトを必要とする
- `contributeResolvedModelCompat`: プロバイダーが、他の互換トランスポート経由で到着した場合でもそのベンダーモデル用の互換フラグを提供
- `capabilities`: プロバイダーがトランスクリプト/ツーリング/プロバイダーファミリーの癖を公開
- `normalizeToolSchemas`: プロバイダーが、埋め込みランナーが見る前にツールスキーマをクリーンアップ
- `inspectToolSchemas`: プロバイダーが、正規化後にトランスポート固有のスキーマ警告を表示
- `resolveReasoningOutputMode`: プロバイダーが、ネイティブまたはタグ付きのreasoning-output契約を選択
- `prepareExtraParams`: プロバイダーが、モデルごとのリクエストパラメータを既定化または正規化
- `createStreamFn`: プロバイダーが、通常のストリーム経路を完全にカスタムなトランスポートで置き換える
- `wrapStreamFn`: プロバイダーが、リクエストヘッダー/ボディ/モデル互換ラッパーを適用
- `resolveTransportTurnState`: プロバイダーが、ターンごとのネイティブトランスポートヘッダーまたはメタデータを提供
- `resolveWebSocketSessionPolicy`: プロバイダーが、ネイティブWebSocketセッションヘッダーまたはセッションクールダウンポリシーを提供
- `createEmbeddingProvider`: プロバイダーが、コアの埋め込みスイッチボードではなくプロバイダープラグイン側に属するメモリ埋め込み動作を所有
- `formatApiKey`: プロバイダーが、保存済み認証プロファイルをトランスポートが期待するランタイム`apiKey`文字列へ整形
- `refreshOAuth`: 共有の`pi-ai`リフレッシャーでは不十分な場合、プロバイダーがOAuth更新を所有
- `buildAuthDoctorHint`: OAuth更新が失敗した場合、プロバイダーが修復ガイダンスを追記
- `matchesContextOverflowError`: プロバイダーが、汎用ヒューリスティクスでは見逃すプロバイダー固有のコンテキストウィンドウ超過エラーを認識
- `classifyFailoverReason`: プロバイダーが、プロバイダー固有の生のトランスポート/APIエラーを、レート制限や過負荷などのフェイルオーバー理由にマッピング
- `isCacheTtlEligible`: プロバイダーが、どの上流モデルIDがプロンプトキャッシュTTLをサポートするかを判定
- `buildMissingAuthMessage`: プロバイダーが、汎用認証ストアエラーをプロバイダー固有の復旧ヒントに置き換える
- `suppressBuiltInModel`: プロバイダーが、古い上流行を非表示にし、直接解決失敗時にベンダー所有のエラーを返せる
- `augmentModelCatalog`: プロバイダーが、検出と設定マージの後に合成/最終カタログ行を追記
- `isBinaryThinking`: プロバイダーが、バイナリのオン/オフthinking UXを所有
- `supportsXHighThinking`: プロバイダーが、選択モデルを`xhigh`対応にする
- `resolveDefaultThinkingLevel`: プロバイダーが、モデルファミリーのデフォルト`/think`ポリシーを所有
- `applyConfigDefaults`: プロバイダーが、認証モード、環境変数、またはモデルファミリーに基づき、設定具現化中にプロバイダー固有のグローバル既定値を適用
- `isModernModelRef`: プロバイダーが、ライブ/スモーク向け優先モデルの一致を所有
- `prepareRuntimeAuth`: プロバイダーが、設定済み認証情報を短命のランタイムトークンへ変換
- `resolveUsageAuth`: プロバイダーが、`/usage`および関連するステータス/レポート画面向けの使用量/クォータ認証情報を解決
- `fetchUsageSnapshot`: プロバイダーが、使用量エンドポイントの取得/解析を所有しつつ、コアは要約シェルと整形を所有
- `onModelSelected`: プロバイダーが、テレメトリやプロバイダー所有のセッション台帳管理など、選択後の副作用を実行

現在のバンドル例:

- `anthropic`: Claude 4.6前方互換フォールバック、認証修復ヒント、使用量エンドポイント取得、cache-TTL/プロバイダーファミリーメタデータ、および認証対応のグローバル設定既定値
- `amazon-bedrock`: Bedrock固有のスロットル/未準備エラー向けに、プロバイダー所有のコンテキスト超過一致とフェイルオーバー理由分類を提供し、さらにAnthropicトラフィック上のClaude専用リプレイポリシーガード用に共有`anthropic-by-model`リプレイファミリーを提供
- `anthropic-vertex`: Anthropicメッセージトラフィック上のClaude専用リプレイポリシーガード
- `openrouter`: モデルIDのパススルー、リクエストラッパー、プロバイダーcapabilityヒント、プロキシGeminiトラフィック上のGemini thought-signatureサニタイズ、`openrouter-thinking`ストリームファミリー経由のプロキシreasoning注入、ルーティングメタデータ転送、およびcache-TTLポリシー
- `github-copilot`: オンボーディング/デバイスログイン、前方互換モデルフォールバック、Claude-thinkingトランスクリプトヒント、ランタイムトークン交換、および使用量エンドポイント取得
- `openai`: GPT-5.4前方互換フォールバック、直接OpenAIトランスポート正規化、Codex対応の認証不足ヒント、Spark抑制、合成OpenAI/Codexカタログ行、thinking/live-modelポリシー、使用量トークン別名正規化（`input` / `output`および`prompt` / `completion`系）、ネイティブOpenAI/Codexラッパー向け共有`openai-responses-defaults`ストリームファミリー、プロバイダーファミリーメタデータ、`gpt-image-1`向けバンドル画像生成プロバイダー登録、および`sora-2`向けバンドル動画生成プロバイダー登録
- `google`: Gemini 3.1前方互換フォールバック、ネイティブGeminiリプレイ検証、ブートストラップリプレイサニタイズ、タグ付きreasoning-outputモード、モダンモデル一致、Gemini image-previewモデル向けバンドル画像生成プロバイダー登録、およびVeoモデル向けバンドル動画生成プロバイダー登録
- `moonshot`: 共有トランスポート、プラグイン所有のthinkingペイロード正規化
- `kilocode`: 共有トランスポート、プラグイン所有のリクエストヘッダー、reasoningペイロード正規化、プロキシGemini thought-signatureサニタイズ、およびcache-TTLポリシー
- `zai`: GLM-5前方互換フォールバック、`tool_stream`既定値、cache-TTLポリシー、binary-thinking/live-modelポリシー、および使用量認証 + クォータ取得。未知の`glm-5*`IDはバンドルされた`glm-4.7`テンプレートから合成されます
- `xai`: ネイティブResponsesトランスポート正規化、Grok高速バリアント向けの`/fast`別名リライト、既定の`tool_stream`、xAI固有のツールスキーマ / reasoningペイロードクリーンアップ、および`grok-imagine-video`向けバンドル動画生成プロバイダー登録
- `mistral`: プラグイン所有のcapabilityメタデータ
- `opencode`および`opencode-go`: プラグイン所有のcapabilityメタデータに加え、プロキシGemini thought-signatureサニタイズ
- `alibaba`: `alibaba/wan2.6-t2v`のような直接Wanモデル参照向けの、プラグイン所有動画生成カタログ
- `byteplus`: プラグイン所有カタログに加え、Seedanceのテキスト動画/画像動画モデル向けバンドル動画生成プロバイダー登録
- `fal`: ホスト型サードパーティー動画モデル向けバンドル動画生成プロバイダー登録、FLUX画像モデル向けホスト型サードパーティー画像生成プロバイダー登録、およびホスト型サードパーティー動画モデル向けバンドル動画生成プロバイダー登録
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway`, および `volcengine`:
  プラグイン所有カタログのみ
- `qwen`: テキストモデル向けプラグイン所有カタログに加え、そのマルチモーダル画面向けの共有media-understandingおよび動画生成プロバイダー登録。Qwen動画生成は、`wan2.6-t2v`や`wan2.7-r2v`のようなバンドルWanモデルとともに、標準DashScope動画エンドポイントを使用します
- `runway`: `gen4.5`のようなネイティブRunwayタスクベースモデル向けのプラグイン所有動画生成プロバイダー登録
- `minimax`: プラグイン所有カタログ、Hailuo動画モデル向けバンドル動画生成プロバイダー登録、`image-01`向けバンドル画像生成プロバイダー登録、ハイブリッドAnthropic/OpenAIリプレイポリシー選択、および使用量認証/スナップショットロジック
- `together`: プラグイン所有カタログに加え、Wan動画モデル向けバンドル動画生成プロバイダー登録
- `xiaomi`: プラグイン所有カタログに加え、使用量認証/スナップショットロジック

バンドルされた`openai`プラグインは現在、両方のプロバイダーID `openai` と
`openai-codex` を所有しています。

これは、依然としてOpenClawの通常トランスポートに収まるプロバイダーを対象としています。完全にカスタムなリクエスト実行器を必要とするプロバイダーは、別の、より深い拡張サーフェスになります。

## APIキーのローテーション

- 選択されたプロバイダーに対する汎用プロバイダーローテーションをサポートします。
- 複数キーは次で設定します:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（単一のライブ上書き、最優先）
  - `<PROVIDER>_API_KEYS`（カンマまたはセミコロン区切りリスト）
  - `<PROVIDER>_API_KEY`（プライマリキー）
  - `<PROVIDER>_API_KEY_*`（番号付きリスト。例: `<PROVIDER>_API_KEY_1`）
- Googleプロバイダーでは、`GOOGLE_API_KEY`もフォールバックとして含まれます。
- キー選択順は優先度を維持しつつ値を重複排除します。
- リクエストは、レート制限応答の場合にのみ次のキーで再試行されます（例:
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded`, または定期的な使用量上限メッセージ）。
- レート制限以外の失敗は即時失敗となり、キーローテーションは試行されません。
- すべての候補キーが失敗した場合、最後の試行の最終エラーが返されます。

## 組み込みプロバイダー（pi-aiカタログ）

OpenClawにはpi‑aiカタログが同梱されています。これらのプロバイダーでは
`models.providers`設定は**不要**です。認証を設定してモデルを選ぶだけです。

### OpenAI

- プロバイダー: `openai`
- 認証: `OPENAI_API_KEY`
- 任意のローテーション: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, および `OPENCLAW_LIVE_OPENAI_KEY`（単一上書き）
- モデル例: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- デフォルトのトランスポートは`auto`です（WebSocket優先、SSEフォールバック）
- モデルごとの上書きは`agents.defaults.models["openai/<model>"].params.transport`で行います（`"sse"`、`"websocket"`、または`"auto"`）
- OpenAI Responses WebSocketウォームアップは、`params.openaiWsWarmup`（`true`/`false`）によりデフォルトで有効です
- OpenAI priority processingは`agents.defaults.models["openai/<model>"].params.serviceTier`で有効化できます
- `/fast`および`params.fastMode`は、直接`openai/*` Responsesリクエストを`api.openai.com`上の`service_tier=priority`へマッピングします
- 共有の`/fast`トグルではなく明示的なtierが必要な場合は`params.serviceTier`を使用してください
- 非公開のOpenClaw属性ヘッダー（`originator`, `version`,
  `User-Agent`）は、`api.openai.com`へのネイティブOpenAIトラフィックにのみ適用され、汎用OpenAI互換プロキシには適用されません
- ネイティブOpenAIルートでは、Responsesの`store`、プロンプトキャッシュヒント、およびOpenAI reasoning互換ペイロード整形も維持されます。プロキシルートでは維持されません
- `openai/gpt-5.3-codex-spark`は、ライブOpenAI APIが拒否するため、OpenClawでは意図的に抑制されています。SparkはCodex専用として扱われます

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- プロバイダー: `anthropic`
- 認証: `ANTHROPIC_API_KEY`
- 任意のローテーション: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2`, および `OPENCLAW_LIVE_ANTHROPIC_KEY`（単一上書き）
- モデル例: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- 直接の公開Anthropicリクエストは、共有の`/fast`トグルと`params.fastMode`もサポートします。これには、`api.anthropic.com`へ送られるAPIキー認証およびOAuth認証トラフィックが含まれます。OpenClawはそれをAnthropicの`service_tier`（`auto`対`standard_only`）にマッピングします
- 課金メモ: OpenClaw上のAnthropicでは、実際の区分は**APIキー**または**Extra Usage付きClaudeサブスクリプション**です。Anthropicは**2026年4月4日 午後12:00 PT / 午後8:00 BST**にOpenClawユーザーへ、**OpenClaw**のClaudeログイン経路はサードパーティーハーネス利用として扱われ、サブスクリプションとは別請求の**Extra Usage**が必要だと通知しました。私たちのローカル再現でも、OpenClaw識別用プロンプト文字列はAnthropic SDK + APIキーパスでは再現しないことが確認されています。
- Anthropic setup-tokenは、レガシー/手動のOpenClaw経路として再び利用可能です。この経路では**Extra Usage**が必要だとAnthropicがOpenClawユーザーに伝えている点を前提に利用してください。

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code（Codex）

- プロバイダー: `openai-codex`
- 認証: OAuth（ChatGPT）
- モデル例: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` または `openclaw models auth login --provider openai-codex`
- デフォルトのトランスポートは`auto`です（WebSocket優先、SSEフォールバック）
- モデルごとの上書きは`agents.defaults.models["openai-codex/<model>"].params.transport`で行います（`"sse"`、`"websocket"`、または`"auto"`）
- `params.serviceTier`もネイティブCodex Responsesリクエスト（`chatgpt.com/backend-api`）で転送されます
- 非公開のOpenClaw属性ヘッダー（`originator`, `version`,
  `User-Agent`）は、`chatgpt.com/backend-api`へのネイティブCodexトラフィックにのみ付与され、汎用OpenAI互換プロキシには付与されません
- 直接`openai/*`と同じ`/fast`トグルおよび`params.fastMode`設定を共有し、OpenClawはこれを`service_tier=priority`へマッピングします
- `openai-codex/gpt-5.3-codex-spark`は、Codex OAuthカタログが公開している場合は引き続き利用可能です。利用権に依存します
- `openai-codex/gpt-5.4`はネイティブな`contextWindow = 1050000`と、デフォルトのランタイム`contextTokens = 272000`を維持します。ランタイム上限は`models.providers.openai-codex.models[].contextTokens`で上書きしてください
- ポリシーメモ: OpenAI Codex OAuthは、OpenClawのような外部ツール/ワークフロー向けに明示的にサポートされています

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### その他のサブスクリプション型ホストオプション

- [Qwen Cloud](/ja-JP/providers/qwen): Qwen Cloudプロバイダーサーフェスに加え、Alibaba DashScopeおよびCoding Planエンドポイントマッピング
- [MiniMax](/ja-JP/providers/minimax): MiniMax Coding Plan OAuthまたはAPIキーアクセス
- [GLM Models](/ja-JP/providers/glm): Z.AI Coding Planまたは汎用APIエンドポイント

### OpenCode

- 認証: `OPENCODE_API_KEY`（または`OPENCODE_ZEN_API_KEY`）
- Zenランタイムプロバイダー: `opencode`
- Goランタイムプロバイダー: `opencode-go`
- モデル例: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini（APIキー）

- プロバイダー: `google`
- 認証: `GEMINI_API_KEY`
- 任意のローテーション: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY`フォールバック、および`OPENCLAW_LIVE_GEMINI_KEY`（単一上書き）
- モデル例: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- 互換性: `google/gemini-3.1-flash-preview`を使うレガシーなOpenClaw設定は`google/gemini-3-flash-preview`へ正規化されます
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- 直接のGemini実行は、`agents.defaults.models["google/<model>"].params.cachedContent`（またはレガシーな`cached_content`）も受け付け、プロバイダーネイティブな`cachedContents/...`ハンドルを転送します。GeminiのキャッシュヒットはOpenClawの`cacheRead`として表面化します

### Google Vertex

- プロバイダー: `google-vertex`
- 認証: gcloud ADC
  - Gemini CLIのJSON応答は`response`から解析されます。使用量は`stats`へフォールバックし、`stats.cached`はOpenClawの`cacheRead`へ正規化されます。

### Z.AI（GLM）

- プロバイダー: `zai`
- 認証: `ZAI_API_KEY`
- モデル例: `zai/glm-5`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - エイリアス: `z.ai/*`および`z-ai/*`は`zai/*`へ正規化されます
  - `zai-api-key`は一致するZ.AIエンドポイントを自動検出します。`zai-coding-global`, `zai-coding-cn`, `zai-global`, および `zai-cn`は特定のサーフェスを強制します

### Vercel AI Gateway

- プロバイダー: `vercel-ai-gateway`
- 認証: `AI_GATEWAY_API_KEY`
- モデル例: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- プロバイダー: `kilocode`
- 認証: `KILOCODE_API_KEY`
- モデル例: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- ベースURL: `https://api.kilo.ai/api/gateway/`
- 静的フォールバックカタログには`kilocode/kilo/auto`が同梱されており、ライブの
  `https://api.kilo.ai/api/gateway/models`検出によりランタイムカタログをさらに拡張できます。
- `kilocode/kilo/auto`の背後にある正確な上流ルーティングはKilo Gatewayが所有しており、
  OpenClawにハードコードされていません。

設定の詳細は[/providers/kilocode](/ja-JP/providers/kilocode)を参照してください。

### その他のバンドルされたプロバイダープラグイン

- OpenRouter: `openrouter`（`OPENROUTER_API_KEY`）
- モデル例: `openrouter/auto`
- OpenClawは、リクエストが実際に`openrouter.ai`を対象としている場合にのみ、OpenRouterの文書化されたアプリ属性ヘッダーを適用します
- OpenRouter固有のAnthropic `cache_control`マーカーも同様に、
  任意のプロキシURLではなく、検証済みのOpenRouterルートに対してのみ有効です
- OpenRouterは引き続きプロキシ型のOpenAI互換経路上にあるため、ネイティブOpenAI専用のリクエスト整形（`serviceTier`、Responses `store`、
  プロンプトキャッシュヒント、OpenAI reasoning互換ペイロード）は転送されません
- GeminiベースのOpenRouter参照では、プロキシGemini thought-signatureサニタイズのみ維持されます。ネイティブGeminiのリプレイ検証およびブートストラップリライトは無効のままです
- Kilo Gateway: `kilocode`（`KILOCODE_API_KEY`）
- モデル例: `kilocode/kilo/auto`
- GeminiベースのKilo参照でも同じプロキシGemini thought-signatureサニタイズ経路が維持されます。`kilocode/kilo/auto`および他のプロキシreasoning非対応ヒントでは、プロキシreasoning注入はスキップされます
- MiniMax: `minimax`（APIキー）および`minimax-portal`（OAuth）
- 認証: `MINIMAX_API_KEY`（`minimax`用）。`MINIMAX_OAUTH_TOKEN`または`MINIMAX_API_KEY`（`minimax-portal`用）
- モデル例: `minimax/MiniMax-M2.7` または `minimax-portal/MiniMax-M2.7`
- MiniMaxのオンボーディング/APIキー設定では、`input: ["text", "image"]`を持つ明示的なM2.7モデル定義が書き込まれます。バンドルされたプロバイダーカタログでは、そのプロバイダー設定が具現化されるまではチャット参照はテキスト専用のままです
- Moonshot: `moonshot`（`MOONSHOT_API_KEY`）
- モデル例: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi`（`KIMI_API_KEY` または `KIMICODE_API_KEY`）
- モデル例: `kimi/kimi-code`
- Qianfan: `qianfan`（`QIANFAN_API_KEY`）
- モデル例: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen`（`QWEN_API_KEY`, `MODELSTUDIO_API_KEY`, または `DASHSCOPE_API_KEY`）
- モデル例: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia`（`NVIDIA_API_KEY`）
- モデル例: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan`（`STEPFUN_API_KEY`）
- モデル例: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together`（`TOGETHER_API_KEY`）
- モデル例: `together/moonshotai/Kimi-K2.5`
- Venice: `venice`（`VENICE_API_KEY`）
- Xiaomi: `xiaomi`（`XIAOMI_API_KEY`）
- モデル例: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway`（`AI_GATEWAY_API_KEY`）
- Hugging Face Inference: `huggingface`（`HUGGINGFACE_HUB_TOKEN` または `HF_TOKEN`）
- Cloudflare AI Gateway: `cloudflare-ai-gateway`（`CLOUDFLARE_AI_GATEWAY_API_KEY`）
- Volcengine: `volcengine`（`VOLCANO_ENGINE_API_KEY`）
- モデル例: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus`（`BYTEPLUS_API_KEY`）
- モデル例: `byteplus-plan/ark-code-latest`
- xAI: `xai`（`XAI_API_KEY`）
  - ネイティブなバンドルxAIリクエストはxAI Responses経路を使用します
  - `/fast`または`params.fastMode: true`は`grok-3`, `grok-3-mini`,
    `grok-4`, および `grok-4-0709`をそれぞれの`*-fast`バリアントへ書き換えます
  - `tool_stream`はデフォルトでオンです。
    無効にするには`agents.defaults.models["xai/<model>"].params.tool_stream`を`false`に設定してください
- Mistral: `mistral`（`MISTRAL_API_KEY`）
- モデル例: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq`（`GROQ_API_KEY`）
- Cerebras: `cerebras`（`CEREBRAS_API_KEY`）
  - Cerebras上のGLMモデルは`zai-glm-4.7`および`zai-glm-4.6`のIDを使用します。
  - OpenAI互換ベースURL: `https://api.cerebras.ai/v1`。
- GitHub Copilot: `github-copilot`（`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`）
- Hugging Face Inferenceのモデル例: `huggingface/deepseek-ai/DeepSeek-R1`。CLI: `openclaw onboard --auth-choice huggingface-api-key`。詳細は[Hugging Face (Inference)](/ja-JP/providers/huggingface)を参照してください。

## `models.providers`経由のプロバイダー（カスタム/base URL）

`models.providers`（または`models.json`）を使うと、**カスタム**プロバイダーまたは
OpenAI/Anthropic互換プロキシを追加できます。

以下のバンドルされたプロバイダープラグインの多くは、すでにデフォルトカタログを公開しています。
デフォルトのbase URL、ヘッダー、またはモデル一覧を上書きしたい場合にのみ、明示的な`models.providers.<id>`エントリーを使用してください。

### Moonshot AI（Kimi）

Moonshotはバンドルされたプロバイダープラグインとして提供されます。通常は組み込みプロバイダーを使い、base URLまたはモデルメタデータを上書きする必要がある場合にのみ、明示的な`models.providers.moonshot`エントリーを追加してください。

- プロバイダー: `moonshot`
- 認証: `MOONSHOT_API_KEY`
- モデル例: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` または `openclaw onboard --auth-choice moonshot-api-key-cn`

Kimi K2モデルID:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi CodingはMoonshot AIのAnthropic互換エンドポイントを使用します。

- プロバイダー: `kimi`
- 認証: `KIMI_API_KEY`
- モデル例: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

レガシーな`kimi/k2p5`も互換モデルIDとして引き続き受け付けられます。

### Volcano Engine（Doubao）

Volcano Engine（火山引擎）は、中国でDoubaoやその他のモデルへのアクセスを提供します。

- プロバイダー: `volcengine`（coding: `volcengine-plan`）
- 認証: `VOLCANO_ENGINE_API_KEY`
- モデル例: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

オンボーディングはデフォルトでcodingサーフェスを使用しますが、一般の`volcengine/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、Volcengine認証選択は
`volcengine/*`と`volcengine-plan/*`の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、OpenClawは空のプロバイダースコープ付きピッカーを表示する代わりに、フィルターなしカタログへフォールバックします。

利用可能なモデル:

- `volcengine/doubao-seed-1-8-251228`（Doubao Seed 1.8）
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127`（Kimi K2.5）
- `volcengine/glm-4-7-251222`（GLM 4.7）
- `volcengine/deepseek-v3-2-251201`（DeepSeek V3.2 128K）

Codingモデル（`volcengine-plan`）:

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus（International）

BytePlus ARKは、国際ユーザー向けにVolcano Engineと同じモデルへのアクセスを提供します。

- プロバイダー: `byteplus`（coding: `byteplus-plan`）
- 認証: `BYTEPLUS_API_KEY`
- モデル例: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

オンボーディングはデフォルトでcodingサーフェスを使用しますが、一般の`byteplus/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、BytePlus認証選択は
`byteplus/*`と`byteplus-plan/*`の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、OpenClawは空のプロバイダースコープ付きピッカーを表示する代わりに、フィルターなしカタログへフォールバックします。

利用可能なモデル:

- `byteplus/seed-1-8-251228`（Seed 1.8）
- `byteplus/kimi-k2-5-260127`（Kimi K2.5）
- `byteplus/glm-4-7-251222`（GLM 4.7）

Codingモデル（`byteplus-plan`）:

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Syntheticは、`synthetic`プロバイダーの背後でAnthropic互換モデルを提供します。

- プロバイダー: `synthetic`
- 認証: `SYNTHETIC_API_KEY`
- モデル例: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMaxはカスタムエンドポイントを使用するため、`models.providers`経由で設定します。

- MiniMax OAuth（Global）: `--auth-choice minimax-global-oauth`
- MiniMax OAuth（CN）: `--auth-choice minimax-cn-oauth`
- MiniMax APIキー（Global）: `--auth-choice minimax-global-api`
- MiniMax APIキー（CN）: `--auth-choice minimax-cn-api`
- 認証: `MINIMAX_API_KEY`（`minimax`用）。`MINIMAX_OAUTH_TOKEN`または
  `MINIMAX_API_KEY`（`minimax-portal`用）

設定の詳細、モデルオプション、設定スニペットについては[/providers/minimax](/ja-JP/providers/minimax)を参照してください。

MiniMaxのAnthropic互換ストリーミング経路では、明示的に設定しない限りthinkingはデフォルトで無効であり、`/fast on`は
`MiniMax-M2.7`を`MiniMax-M2.7-highspeed`へ書き換えます。

プラグイン所有のcapability分割:

- テキスト/チャットのデフォルトは`minimax/MiniMax-M2.7`のまま
- 画像生成は`minimax/image-01`または`minimax-portal/image-01`
- 画像理解は、両方のMiniMax認証経路でプラグイン所有の`MiniMax-VL-01`
- Web検索は引き続きプロバイダーID `minimax`

### Ollama

Ollamaはバンドルされたプロバイダープラグインとして提供され、OllamaのネイティブAPIを使用します。

- プロバイダー: `ollama`
- 認証: 不要（ローカルサーバー）
- モデル例: `ollama/llama3.3`
- インストール: [https://ollama.com/download](https://ollama.com/download)

```bash
# Ollamaをインストールしてからモデルを取得:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollamaは、`OLLAMA_API_KEY`でオプトインするとローカルの`http://127.0.0.1:11434`で検出され、バンドルされたプロバイダープラグインがOllamaを
`openclaw onboard`とモデルピッカーへ直接追加します。オンボーディング、クラウド/ローカルモード、カスタム設定については[/providers/ollama](/ja-JP/providers/ollama)を参照してください。

### vLLM

vLLMは、ローカル/セルフホストのOpenAI互換サーバー向けバンドルプロバイダープラグインとして提供されます。

- プロバイダー: `vllm`
- 認証: 任意（サーバーによる）
- デフォルトbase URL: `http://127.0.0.1:8000/v1`

ローカル自動検出にオプトインするには（サーバーが認証を強制しない場合は任意の値で動作します）:

```bash
export VLLM_API_KEY="vllm-local"
```

次にモデルを設定します（`/v1/models`が返すIDの1つに置き換えてください）:

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

詳細は[/providers/vllm](/ja-JP/providers/vllm)を参照してください。

### SGLang

SGLangは、高速なセルフホスト
OpenAI互換サーバー向けのバンドルプロバイダープラグインとして提供されます。

- プロバイダー: `sglang`
- 認証: 任意（サーバーによる）
- デフォルトbase URL: `http://127.0.0.1:30000/v1`

ローカル自動検出にオプトインするには（サーバーが認証を強制しない場合は任意の値で動作します）:

```bash
export SGLANG_API_KEY="sglang-local"
```

次にモデルを設定します（`/v1/models`が返すIDの1つに置き換えてください）:

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

詳細は[/providers/sglang](/ja-JP/providers/sglang)を参照してください。

### ローカルプロキシ（LM Studio、vLLM、LiteLLMなど）

例（OpenAI互換）:

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

メモ:

- カスタムプロバイダーでは、`reasoning`、`input`、`cost`、`contextWindow`、および`maxTokens`は任意です。
  省略時、OpenClawのデフォルトは次のとおりです:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 推奨: プロキシ/モデルの上限に一致する明示的な値を設定してください。
- 非ネイティブエンドポイント上の`api: "openai-completions"`（`api.openai.com`ではないホストを持つ空でない`baseUrl`）では、OpenClawは、未対応の`developer`ロールによるプロバイダー400エラーを避けるため、`compat.supportsDeveloperRole: false`を強制します。
- プロキシ型OpenAI互換ルートでは、ネイティブOpenAI専用のリクエスト整形もスキップされます:
  `service_tier`なし、Responses `store`なし、プロンプトキャッシュヒントなし、
  OpenAI reasoning互換ペイロード整形なし、非公開のOpenClaw属性ヘッダーなし。
- `baseUrl`が空または省略されている場合、OpenClawはデフォルトのOpenAI動作（`api.openai.com`へ解決）を維持します。
- 安全性のため、明示的な`compat.supportsDeveloperRole: true`であっても、非ネイティブ`openai-completions`エンドポイントでは引き続き上書きされます。

## CLIの例

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

あわせて参照: 完全な設定例については[/gateway/configuration](/ja-JP/gateway/configuration)を参照してください。

## 関連

- [Models](/ja-JP/concepts/models) — モデル設定とエイリアス
- [Model Failover](/ja-JP/concepts/model-failover) — フォールバックチェーンと再試行動作
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) — モデル設定キー
- [Providers](/ja-JP/providers) — プロバイダーごとのセットアップガイド
