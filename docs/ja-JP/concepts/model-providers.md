---
read_when:
    - プロバイダーごとのモデル設定リファレンスが必要な場合
    - モデルプロバイダー向けの設定例や CLI オンボーディングコマンドを確認したい場合
summary: 設定例と CLI フローを含むモデルプロバイダーの概要
title: モデルプロバイダー
x-i18n:
    generated_at: "2026-04-08T04:43:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 558ac9e34b67fcc3dd6791a01bebc17e1c34152fa6c5611593d681e8cfa532d9
    source_path: concepts/model-providers.md
    workflow: 15
---

# モデルプロバイダー

このページでは、**LLM/モデルプロバイダー**（WhatsApp/Telegram のようなチャットチャネルではありません）を扱います。
モデル選択ルールについては、[/concepts/models](/ja-JP/concepts/models) を参照してください。

## クイックルール

- モデル参照は `provider/model` を使用します（例: `opencode/claude-opus-4-6`）。
- `agents.defaults.models` を設定すると、それが許可リストになります。
- CLI ヘルパー: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`
- フォールバックのランタイムルール、クールダウンプローブ、セッション上書きの永続化は、[/concepts/model-failover](/ja-JP/concepts/model-failover) に
  記載されています。
- `models.providers.*.models[].contextWindow` はネイティブなモデルメタデータです。
  `models.providers.*.models[].contextTokens` は実効ランタイム上限です。
- プロバイダープラグインは `registerProvider({ catalog })` を通じて
  モデルカタログを注入できます。
  OpenClaw はその出力を `models.providers` にマージしてから
  `models.json` を書き込みます。
- プロバイダーマニフェストでは `providerAuthEnvVars` を宣言できるため、
  汎用の env ベース認証プローブでプラグインランタイムを読み込む必要がありません。残るコアの env var
  マップは、非プラグイン/コアプロバイダーと、Anthropic の API キー優先オンボーディングのような一部の汎用優先順位ケースのみを対象としています。
- プロバイダープラグインは、以下を通じてプロバイダーのランタイム動作も所有できます。
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
- 注: プロバイダーランタイムの `capabilities` は共有ランナーのメタデータです（プロバイダーファミリー、文字起こし/ツール関連の癖、トランスポート/キャッシュのヒント）。これは、プラグインが登録する内容（テキスト推論、音声など）を説明する
  [公開 capability model](/ja-JP/plugins/architecture#public-capability-model)
  とは同じではありません。

## プラグイン所有のプロバイダー動作

OpenClaw が汎用推論ループを維持しつつ、プロバイダープラグインが
プロバイダー固有ロジックの大半を所有できるようになりました。

典型的な分担:

- `auth[].run` / `auth[].runNonInteractive`: プロバイダーが `openclaw onboard`、`openclaw models auth`、ヘッドレスセットアップ向けのオンボーディング/ログイン
  フローを所有します
- `wizard.setup` / `wizard.modelPicker`: プロバイダーが認証選択ラベル、
  レガシーエイリアス、オンボーディングの許可リストヒント、およびオンボーディング/モデルピッカー内の設定項目を所有します
- `catalog`: プロバイダーが `models.providers` に表示されます
- `normalizeModelId`: プロバイダーが、検索または正規化の前に
  レガシー/プレビューのモデル id を正規化します
- `normalizeTransport`: プロバイダーが汎用モデル組み立て前に
  トランスポートファミリーの `api` / `baseUrl` を正規化します。OpenClaw はまず一致したプロバイダーを確認し、
  次に、実際にトランスポートを変更するものが現れるまで、他のフック対応プロバイダープラグインを確認します
- `normalizeConfig`: プロバイダーがランタイムで使用する前に
  `models.providers.<id>` の設定を正規化します。OpenClaw はまず一致したプロバイダーを確認し、
  次に、実際に設定を変更するものが現れるまで、他のフック対応プロバイダープラグインを確認します。プロバイダーフックが設定を書き換えない場合でも、
  バンドルされた Google ファミリーのヘルパーが引き続きサポート対象の Google プロバイダーエントリを
  正規化します。
- `applyNativeStreamingUsageCompat`: プロバイダーが設定プロバイダー向けに、エンドポイント駆動のネイティブ streaming-usage 互換書き換えを適用します
- `resolveConfigApiKey`: プロバイダーが、完全なランタイム認証ロードを強制せずに、
  設定プロバイダー向けの env-marker 認証を解決します。`amazon-bedrock` にもここに
  組み込みの AWS env-marker リゾルバーがありますが、Bedrock のランタイム認証は
  AWS SDK のデフォルトチェーンを使用します。
- `resolveSyntheticAuth`: プロバイダーは、平文シークレットを永続化せずに
  ローカル/セルフホスト型やその他の設定ベース認証の利用可否を公開できます
- `shouldDeferSyntheticProfileAuth`: プロバイダーは、保存された synthetic profile
  プレースホルダーを env/config ベース認証より低い優先順位として扱うよう指定できます
- `resolveDynamicModel`: プロバイダーは、ローカルの
  静的カタログにまだ存在しないモデル id を受け入れます
- `prepareDynamicModel`: プロバイダーが動的解決を再試行する前に
  メタデータ更新を必要とします
- `normalizeResolvedModel`: プロバイダーがトランスポートまたは base URL の書き換えを必要とします
- `contributeResolvedModelCompat`: プロバイダーは、そのベンダーモデルが別の互換トランスポート経由で到着した場合でも、
  互換フラグを提供します
- `capabilities`: プロバイダーが文字起こし/ツール/プロバイダーファミリーの癖を公開します
- `normalizeToolSchemas`: プロバイダーが、埋め込みランナーが参照する前に
  ツールスキーマをクリーンアップします
- `inspectToolSchemas`: プロバイダーが、正規化後に
  トランスポート固有のスキーマ警告を提示します
- `resolveReasoningOutputMode`: プロバイダーがネイティブとタグ付きの
  reasoning-output 契約を選択します
- `prepareExtraParams`: プロバイダーがモデルごとのリクエストパラメータを
  デフォルト化または正規化します
- `createStreamFn`: プロバイダーが通常のストリームパスを
  完全にカスタムなトランスポートに置き換えます
- `wrapStreamFn`: プロバイダーがリクエストヘッダー/ボディ/モデル互換のラッパーを適用します
- `resolveTransportTurnState`: プロバイダーがターンごとのネイティブトランスポート
  ヘッダーまたはメタデータを提供します
- `resolveWebSocketSessionPolicy`: プロバイダーがネイティブ WebSocket セッション
  ヘッダーまたはセッションクールダウンポリシーを提供します
- `createEmbeddingProvider`: プロバイダーが、コアの埋め込みスイッチボードではなく
  プロバイダープラグイン側に属するメモリ埋め込み動作を所有します
- `formatApiKey`: プロバイダーが、保存された認証プロファイルを
  トランスポートが期待するランタイム `apiKey` 文字列へ整形します
- `refreshOAuth`: 共有の `pi-ai`
  リフレッシャーでは不十分な場合、プロバイダーが OAuth 更新を所有します
- `buildAuthDoctorHint`: OAuth 更新が
  失敗した際に、プロバイダーが修復ガイダンスを追加します
- `matchesContextOverflowError`: プロバイダーが、汎用ヒューリスティックでは見逃す
  プロバイダー固有のコンテキストウィンドウ超過エラーを認識します
- `classifyFailoverReason`: プロバイダーが、プロバイダー固有の生のトランスポート/API
  エラーを、レート制限や過負荷などのフェイルオーバー理由にマッピングします
- `isCacheTtlEligible`: プロバイダーが、どの上流モデル id が prompt-cache TTL をサポートするかを判断します
- `buildMissingAuthMessage`: プロバイダーが、汎用認証ストアエラーを
  プロバイダー固有の復旧ヒントに置き換えます
- `suppressBuiltInModel`: プロバイダーが古くなった上流行を非表示にし、
  直接解決の失敗に対してベンダー所有のエラーを返せます
- `augmentModelCatalog`: プロバイダーが、発見と設定マージ後に
  synthetic/最終カタログ行を追加します
- `isBinaryThinking`: プロバイダーが二値の on/off thinking UX を所有します
- `supportsXHighThinking`: プロバイダーが、選択したモデルに `xhigh` を有効化します
- `resolveDefaultThinkingLevel`: プロバイダーがモデルファミリー向けの
  デフォルト `/think` ポリシーを所有します
- `applyConfigDefaults`: プロバイダーが、認証モード、env、またはモデルファミリーに基づいて
  設定具体化時にプロバイダー固有のグローバルデフォルトを適用します
- `isModernModelRef`: プロバイダーが live/smoke の優先モデル照合を所有します
- `prepareRuntimeAuth`: プロバイダーが、設定済み認証情報を
  短命なランタイムトークンに変換します
- `resolveUsageAuth`: プロバイダーが、`/usage`
  および関連するステータス/レポート画面向けの使用量/クォータ認証情報を解決します
- `fetchUsageSnapshot`: プロバイダーが使用量エンドポイントの取得/解析を所有し、
  コアはサマリーの枠組みと整形を引き続き所有します
- `onModelSelected`: プロバイダーが、
  テレメトリーやプロバイダー所有のセッション管理など、選択後の副作用を実行します

現在のバンドル例:

- `anthropic`: Claude 4.6 の前方互換フォールバック、認証修復ヒント、使用量
  エンドポイント取得、cache-TTL/プロバイダーファミリーメタデータ、および認証対応のグローバル
  設定デフォルト
- `amazon-bedrock`: Bedrock 固有のスロットル/未準備エラーに対する、プロバイダー所有のコンテキスト超過判定と
  フェイルオーバー理由分類、さらに Anthropic トラフィックに対する Claude 専用 replay-policy
  ガード用の共有 `anthropic-by-model` リプレイファミリー
- `anthropic-vertex`: Anthropic-message
  トラフィックに対する Claude 専用 replay-policy ガード
- `openrouter`: 透過的なモデル id、リクエストラッパー、プロバイダー capability
  ヒント、プロキシ Gemini トラフィック上の Gemini thought-signature のサニタイズ、
  `openrouter-thinking` ストリームファミリー経由のプロキシ推論注入、ルーティング
  メタデータの転送、および cache-TTL ポリシー
- `github-copilot`: オンボーディング/デバイスログイン、前方互換モデルフォールバック、
  Claude-thinking 文字起こしヒント、ランタイムトークン交換、使用量エンドポイント
  取得
- `openai`: GPT-5.4 の前方互換フォールバック、直接 OpenAI トランスポート
  正規化、Codex 対応の認証不足ヒント、Spark の抑制、synthetic な
  OpenAI/Codex カタログ行、thinking/live-model ポリシー、使用量トークン別名
  正規化（`input` / `output` および `prompt` / `completion` ファミリー）、ネイティブ OpenAI/Codex
  ラッパー用の共有 `openai-responses-defaults` ストリームファミリー、
  プロバイダーファミリーメタデータ、`gpt-image-1` 向けバンドル済み画像生成プロバイダー
  登録、および `sora-2` 向けバンドル済み動画生成プロバイダー
  登録
- `google` および `google-gemini-cli`: Gemini 3.1 の前方互換フォールバック、
  ネイティブ Gemini リプレイ検証、ブートストラップリプレイのサニタイズ、タグ付き
  reasoning-output モード、modern-model 照合、Gemini image-preview モデル向け
  バンドル済み画像生成プロバイダー登録、および
  Veo モデル向けバンドル済み動画生成プロバイダー登録。Gemini CLI OAuth も
  使用量画面向けの認証プロファイルトークン整形、使用量トークン解析、およびクォータエンドポイント
  取得を所有します
- `moonshot`: 共有トランスポート、プラグイン所有の thinking ペイロード正規化
- `kilocode`: 共有トランスポート、プラグイン所有のリクエストヘッダー、reasoning ペイロード
  正規化、プロキシ Gemini thought-signature のサニタイズ、および cache-TTL
  ポリシー
- `zai`: GLM-5 の前方互換フォールバック、`tool_stream` のデフォルト、cache-TTL
  ポリシー、二値 thinking/live-model ポリシー、および使用量認証 + クォータ取得。
  不明な `glm-5*` id は、バンドル済みの `glm-4.7` テンプレートから生成されます
- `xai`: ネイティブ Responses トランスポート正規化、Grok fast バリアント向け
  `/fast` エイリアス書き換え、デフォルト `tool_stream`、xAI 固有のツールスキーマ /
  reasoning ペイロードのクリーンアップ、およびバンドル済み動画生成プロバイダー
  `grok-imagine-video` 向け登録
- `mistral`: プラグイン所有の capability メタデータ
- `opencode` および `opencode-go`: プラグイン所有の capability メタデータに加え、
  プロキシ Gemini thought-signature のサニタイズ
- `alibaba`: `alibaba/wan2.6-t2v` のような直接 Wan モデル参照向け、
  プラグイン所有の動画生成カタログ
- `byteplus`: プラグイン所有のカタログに加え、Seedance の text-to-video/image-to-video モデル向け
  バンドル済み動画生成プロバイダー
  登録
- `fal`: ホスト型サードパーティ向けのバンドル済み動画生成プロバイダー登録、
  FLUX 画像モデル向けの画像生成プロバイダー登録に加え、ホスト型サードパーティ動画モデル向けの
  バンドル済み動画生成プロバイダー登録
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway`, および `volcengine`:
  プラグイン所有のカタログのみ
- `qwen`: テキストモデル向けのプラグイン所有カタログに加え、
  そのマルチモーダル画面向けの共有
  media-understanding および動画生成プロバイダー登録。Qwen の動画生成は、
  `wan2.6-t2v` や `wan2.7-r2v` のようなバンドル済み Wan モデルを用いた、
  標準 DashScope 動画エンドポイントを使用します
- `runway`: `gen4.5` のようなネイティブ
  Runway タスクベースモデル向けのプラグイン所有動画生成プロバイダー登録
- `minimax`: プラグイン所有のカタログ、Hailuo 動画モデル向けのバンドル済み動画生成プロバイダー
  登録、`image-01` 向けのバンドル済み画像生成プロバイダー
  登録、ハイブリッドな Anthropic/OpenAI replay-policy
  選択、および使用量認証/スナップショットロジック
- `together`: プラグイン所有のカタログに加え、Wan 動画モデル向けのバンドル済み動画生成プロバイダー
  登録
- `xiaomi`: プラグイン所有のカタログに加え、使用量認証/スナップショットロジック

バンドル済みの `openai` プラグインは現在、`openai` と
`openai-codex` の両方のプロバイダー id を所有しています。

これで、OpenClaw の通常トランスポートにまだ収まるプロバイダーは網羅されます。完全にカスタムなリクエスト実行器が必要なプロバイダーは、
別の、より深い拡張サーフェスになります。

## API キーのローテーション

- 選択したプロバイダーに対する汎用プロバイダーローテーションをサポートします。
- 複数キーの設定方法:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（単一の live 上書き、最優先）
  - `<PROVIDER>_API_KEYS`（カンマまたはセミコロン区切りのリスト）
  - `<PROVIDER>_API_KEY`（プライマリキー）
  - `<PROVIDER>_API_KEY_*`（番号付きリスト。例: `<PROVIDER>_API_KEY_1`）
- Google プロバイダーでは、フォールバックとして `GOOGLE_API_KEY` も含まれます。
- キー選択順序は優先順位を維持し、値は重複排除されます。
- リクエストは、レート制限レスポンスの場合にのみ次のキーで再試行されます（例:
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded`、または定期的な usage-limit メッセージ）。
- レート制限以外の失敗は即座に失敗し、キーのローテーションは試行されません。
- すべての候補キーが失敗した場合、最後の試行からの最終エラーが返されます。

## 組み込みプロバイダー（pi-ai カタログ）

OpenClaw には pi‑ai カタログが同梱されています。これらのプロバイダーでは
`models.providers` の設定は**不要**です。認証を設定してモデルを選ぶだけです。

### OpenAI

- プロバイダー: `openai`
- 認証: `OPENAI_API_KEY`
- 任意のローテーション: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2`, および `OPENCLAW_LIVE_OPENAI_KEY`（単一上書き）
- モデル例: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- デフォルトのトランスポートは `auto` です（WebSocket 優先、SSE フォールバック）
- モデルごとの上書きは `agents.defaults.models["openai/<model>"].params.transport` で行います（`"sse"`, `"websocket"`, または `"auto"`）
- OpenAI Responses WebSocket ウォームアップは、`params.openaiWsWarmup`（`true`/`false`）によりデフォルトで有効です
- OpenAI priority processing は `agents.defaults.models["openai/<model>"].params.serviceTier` で有効化できます
- `/fast` と `params.fastMode` は、直接の `openai/*` Responses リクエストを `api.openai.com` 上の `service_tier=priority` にマップします
- 共有の `/fast` トグルではなく明示的な tier を使いたい場合は、`params.serviceTier` を使用してください
- 非表示の OpenClaw 属性ヘッダー（`originator`, `version`,
  `User-Agent`）は、ネイティブ OpenAI トラフィックの `api.openai.com` にのみ適用され、
  汎用の OpenAI 互換プロキシには適用されません
- ネイティブ OpenAI ルートでは、Responses の `store`、prompt-cache ヒント、および
  OpenAI reasoning 互換のペイロード整形も維持されます。プロキシルートでは維持されません
- `openai/gpt-5.3-codex-spark` は、live OpenAI API がこれを拒否するため、OpenClaw では意図的に抑制されています。Spark は Codex 専用として扱われます

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
- 直接の公開 Anthropic リクエストでは、共有の `/fast` トグルと `params.fastMode` もサポートされます。これには `api.anthropic.com` に送信される API キー認証および OAuth 認証トラフィックが含まれます。OpenClaw はこれを Anthropic の `service_tier`（`auto` と `standard_only`）にマップします
- Anthropic 注記: Anthropic のスタッフから、OpenClaw スタイルの Claude CLI 利用は再び許可されていると伝えられたため、Anthropic が新しいポリシーを公開しない限り、OpenClaw は Claude CLI の再利用と `claude -p` の利用をこの統合において認可済みとして扱います。
- Anthropic setup-token も引き続きサポートされる OpenClaw のトークン経路として利用可能ですが、OpenClaw は現在、利用可能であれば Claude CLI の再利用と `claude -p` を優先します。

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
- デフォルトのトランスポートは `auto` です（WebSocket 優先、SSE フォールバック）
- モデルごとの上書きは `agents.defaults.models["openai-codex/<model>"].params.transport` で行います（`"sse"`, `"websocket"`, または `"auto"`）
- `params.serviceTier` も、ネイティブ Codex Responses リクエスト（`chatgpt.com/backend-api`）で転送されます
- 非表示の OpenClaw 属性ヘッダー（`originator`, `version`,
  `User-Agent`）は、`chatgpt.com/backend-api` へのネイティブ Codex トラフィックにのみ付与され、
  汎用の OpenAI 互換プロキシには付与されません
- 直接の `openai/*` と同じ `/fast` トグルおよび `params.fastMode` 設定を共有し、OpenClaw はこれを `service_tier=priority` にマップします
- `openai-codex/gpt-5.3-codex-spark` は、Codex OAuth カタログが公開している場合は引き続き利用可能です。権限依存です
- `openai-codex/gpt-5.4` はネイティブの `contextWindow = 1050000` と、デフォルトのランタイム `contextTokens = 272000` を維持します。ランタイム上限は `models.providers.openai-codex.models[].contextTokens` で上書きできます
- ポリシー注記: OpenAI Codex OAuth は、OpenClaw のような外部ツール/ワークフロー向けに明示的にサポートされています。

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

- [Qwen Cloud](/ja-JP/providers/qwen): Qwen Cloud のプロバイダーサーフェスに加え、Alibaba DashScope と Coding Plan エンドポイントのマッピング
- [MiniMax](/ja-JP/providers/minimax): MiniMax Coding Plan OAuth または API キーアクセス
- [GLM Models](/ja-JP/providers/glm): Z.AI Coding Plan または一般 API エンドポイント

### OpenCode

- 認証: `OPENCODE_API_KEY`（または `OPENCODE_ZEN_API_KEY`）
- Zen ランタイムプロバイダー: `opencode`
- Go ランタイムプロバイダー: `opencode-go`
- モデル例: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` または `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini（API キー）

- プロバイダー: `google`
- 認証: `GEMINI_API_KEY`
- 任意のローテーション: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` フォールバック、および `OPENCLAW_LIVE_GEMINI_KEY`（単一上書き）
- モデル例: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- 互換性: `google/gemini-3.1-flash-preview` を使用するレガシーな OpenClaw 設定は、`google/gemini-3-flash-preview` に正規化されます
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- 直接の Gemini 実行では、`agents.defaults.models["google/<model>"].params.cachedContent`
  （またはレガシーな `cached_content`）も受け付け、
  プロバイダーネイティブの `cachedContents/...` ハンドルを転送します。
  Gemini のキャッシュヒットは OpenClaw の `cacheRead` として表示されます

### Google Vertex と Gemini CLI

- プロバイダー: `google-vertex`, `google-gemini-cli`
- 認証: Vertex は gcloud ADC を使用し、Gemini CLI は自身の OAuth フローを使用します
- 注意: OpenClaw における Gemini CLI OAuth は非公式な統合です。サードパーティクライアント利用後に Google アカウントの制限が発生したという報告もあります。利用する場合は Google の規約を確認し、重要でないアカウントを使用してください。
- Gemini CLI OAuth は、バンドル済みの `google` プラグインの一部として提供されます。
  - まず Gemini CLI をインストールします:
    - `brew install gemini-cli`
    - または `npm install -g @google/gemini-cli`
  - 有効化: `openclaw plugins enable google`
  - ログイン: `openclaw models auth login --provider google-gemini-cli --set-default`
  - デフォルトモデル: `google-gemini-cli/gemini-3-flash-preview`
  - 注: `openclaw.json` に client id や secret を貼り付ける必要は**ありません**。CLI のログインフローは
    トークンを Gateway ホスト上の認証プロファイルに保存します。
  - ログイン後にリクエストが失敗する場合は、Gateway ホストで `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定してください。
  - Gemini CLI の JSON 応答は `response` から解析され、使用量は
    `stats` にフォールバックされます。`stats.cached` は OpenClaw の `cacheRead` に正規化されます。

### Z.AI（GLM）

- プロバイダー: `zai`
- 認証: `ZAI_API_KEY`
- モデル例: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - エイリアス: `z.ai/*` と `z-ai/*` は `zai/*` に正規化されます
  - `zai-api-key` は一致する Z.AI エンドポイントを自動検出します。`zai-coding-global`, `zai-coding-cn`, `zai-global`, `zai-cn` は特定のサーフェスを強制します

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
- ベース URL: `https://api.kilo.ai/api/gateway/`
- 静的フォールバックカタログには `kilocode/kilo/auto` が同梱されており、
  live の `https://api.kilo.ai/api/gateway/models` 検出によって
  ランタイムカタログがさらに拡張される場合があります。
- `kilocode/kilo/auto` の背後にある正確な上流ルーティングは Kilo Gateway が所有しており、
  OpenClaw にはハードコードされていません。

セットアップの詳細は [/providers/kilocode](/ja-JP/providers/kilocode) を参照してください。

### その他のバンドル済みプロバイダープラグイン

- OpenRouter: `openrouter`（`OPENROUTER_API_KEY`）
- モデル例: `openrouter/auto`
- OpenClaw は、リクエストの実際の送信先が `openrouter.ai` の場合にのみ、
  OpenRouter の文書化されたアプリ属性ヘッダーを適用します
- OpenRouter 固有の Anthropic `cache_control` マーカーも同様に、
  任意のプロキシ URL ではなく検証済みの OpenRouter ルートに対してのみ有効です
- OpenRouter は引き続きプロキシ型の OpenAI 互換パス上にあるため、ネイティブ OpenAI 専用のリクエスト整形（`serviceTier`、Responses の `store`、
  prompt-cache ヒント、OpenAI reasoning 互換ペイロード）は転送されません
- Gemini ベースの OpenRouter 参照では、プロキシ Gemini thought-signature のサニタイズのみが維持されます。
  ネイティブ Gemini のリプレイ検証とブートストラップ書き換えは無効のままです
- Kilo Gateway: `kilocode`（`KILOCODE_API_KEY`）
- モデル例: `kilocode/kilo/auto`
- Gemini ベースの Kilo 参照でも、同じプロキシ Gemini thought-signature
  サニタイズパスが維持されます。`kilocode/kilo/auto` やその他のプロキシ推論非対応
  ヒントでは、プロキシ推論注入はスキップされます
- MiniMax: `minimax`（API キー）および `minimax-portal`（OAuth）
- 認証: `minimax` には `MINIMAX_API_KEY`、`minimax-portal` には `MINIMAX_OAUTH_TOKEN` または `MINIMAX_API_KEY`
- モデル例: `minimax/MiniMax-M2.7` または `minimax-portal/MiniMax-M2.7`
- MiniMax のオンボーディング/API キー設定では、
  `input: ["text", "image"]` を持つ明示的な M2.7 モデル定義が書き込まれます。バンドル済みプロバイダーカタログでは、
  そのプロバイダー設定が具体化されるまで、チャット参照は
  テキスト専用のままです
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
  - ネイティブのバンドル済み xAI リクエストでは、xAI Responses パスを使用します
  - `/fast` または `params.fastMode: true` は、`grok-3`, `grok-3-mini`,
    `grok-4`, および `grok-4-0709` をそれぞれの `*-fast` バリアントに
    書き換えます
  - `tool_stream` はデフォルトで有効です。無効にするには、
    `agents.defaults.models["xai/<model>"].params.tool_stream` を `false` に設定してください
- Mistral: `mistral`（`MISTRAL_API_KEY`）
- モデル例: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq`（`GROQ_API_KEY`）
- Cerebras: `cerebras`（`CEREBRAS_API_KEY`）
  - Cerebras 上の GLM モデルは `zai-glm-4.7` および `zai-glm-4.6` という id を使用します。
  - OpenAI 互換の base URL: `https://api.cerebras.ai/v1`
- GitHub Copilot: `github-copilot`（`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`）
- Hugging Face Inference のモデル例: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`。 [Hugging Face (Inference)](/ja-JP/providers/huggingface) を参照してください。

## `models.providers` 経由のプロバイダー（カスタム/base URL）

`models.providers`（または `models.json`）を使うと、**カスタム**プロバイダーや
OpenAI/Anthropic 互換プロキシを追加できます。

以下のバンドル済みプロバイダープラグインの多くは、すでにデフォルトカタログを公開しています。
デフォルトの base URL、ヘッダー、またはモデル一覧を上書きしたい場合にのみ、
明示的な `models.providers.<id>` エントリを使用してください。

### Moonshot AI（Kimi）

Moonshot はバンドル済みプロバイダープラグインとして提供されています。デフォルトでは組み込みプロバイダーを使用し、
base URL またはモデルメタデータを上書きしたい場合にのみ、明示的な `models.providers.moonshot` エントリを追加してください。

- プロバイダー: `moonshot`
- 認証: `MOONSHOT_API_KEY`
- モデル例: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` または `openclaw onboard --auth-choice moonshot-api-key-cn`

Kimi K2 モデル ID:

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

Kimi Coding は Moonshot AI の Anthropic 互換エンドポイントを使用します。

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

レガシーな `kimi/k2p5` も互換モデル id として引き続き受け付けられます。

### Volcano Engine（Doubao）

Volcano Engine（火山引擎）は、中国国内で Doubao などのモデルへのアクセスを提供します。

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

オンボーディングでは coding サーフェスがデフォルトですが、一般的な `volcengine/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、Volcengine の認証選択は
`volcengine/*` と `volcengine-plan/*` の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、
OpenClaw は空のプロバイダー限定ピッカーを表示する代わりに、
フィルタなしカタログへフォールバックします。

利用可能なモデル:

- `volcengine/doubao-seed-1-8-251228`（Doubao Seed 1.8）
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127`（Kimi K2.5）
- `volcengine/glm-4-7-251222`（GLM 4.7）
- `volcengine/deepseek-v3-2-251201`（DeepSeek V3.2 128K）

Coding モデル（`volcengine-plan`）:

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus（International）

BytePlus ARK は、国際ユーザー向けに Volcano Engine と同じモデルへのアクセスを提供します。

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

オンボーディングでは coding サーフェスがデフォルトですが、一般的な `byteplus/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、BytePlus の認証選択は
`byteplus/*` と `byteplus-plan/*` の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、
OpenClaw は空のプロバイダー限定ピッカーを表示する代わりに、
フィルタなしカタログへフォールバックします。

利用可能なモデル:

- `byteplus/seed-1-8-251228`（Seed 1.8）
- `byteplus/kimi-k2-5-260127`（Kimi K2.5）
- `byteplus/glm-4-7-251222`（GLM 4.7）

Coding モデル（`byteplus-plan`）:

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic は `synthetic` プロバイダーの背後で Anthropic 互換モデルを提供します。

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

MiniMax はカスタムエンドポイントを使用するため、`models.providers` で設定されます。

- MiniMax OAuth（Global）: `--auth-choice minimax-global-oauth`
- MiniMax OAuth（CN）: `--auth-choice minimax-cn-oauth`
- MiniMax API キー（Global）: `--auth-choice minimax-global-api`
- MiniMax API キー（CN）: `--auth-choice minimax-cn-api`
- 認証: `minimax` には `MINIMAX_API_KEY`、`minimax-portal` には
  `MINIMAX_OAUTH_TOKEN` または `MINIMAX_API_KEY`

セットアップの詳細、モデルオプション、設定スニペットについては [/providers/minimax](/ja-JP/providers/minimax) を参照してください。

MiniMax の Anthropic 互換ストリーミングパスでは、OpenClaw は
明示的に設定しない限り thinking をデフォルトで無効化し、`/fast on` は
`MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。

プラグイン所有の capability 分担:

- テキスト/チャットのデフォルトは `minimax/MiniMax-M2.7` のままです
- 画像生成は `minimax/image-01` または `minimax-portal/image-01` です
- 画像理解は、両方の MiniMax 認証パスでプラグイン所有の `MiniMax-VL-01` です
- Web 検索はプロバイダー id `minimax` のままです

### Ollama

Ollama はバンドル済みプロバイダープラグインとして提供され、Ollama のネイティブ API を使用します。

- プロバイダー: `ollama`
- 認証: 不要（ローカルサーバー）
- モデル例: `ollama/llama3.3`
- インストール: [https://ollama.com/download](https://ollama.com/download)

```bash
# Ollama をインストールしてから、モデルを pull します:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama は、`OLLAMA_API_KEY` でオプトインしたときに
`http://127.0.0.1:11434` でローカル検出され、バンドル済みプロバイダープラグインは Ollama を直接
`openclaw onboard` とモデルピッカーに追加します。オンボーディング、クラウド/ローカルモード、カスタム設定については [/providers/ollama](/ja-JP/providers/ollama)
を参照してください。

### vLLM

vLLM は、ローカル/セルフホスト型の OpenAI 互換
サーバー向けバンドル済みプロバイダープラグインとして提供されています。

- プロバイダー: `vllm`
- 認証: 任意（サーバー構成による）
- デフォルトの base URL: `http://127.0.0.1:8000/v1`

ローカルで自動検出を有効化するには（サーバーが認証を強制しない場合は任意の値で動作します）:

```bash
export VLLM_API_KEY="vllm-local"
```

次にモデルを設定します（`/v1/models` が返す ID のいずれかに置き換えてください）:

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

詳細は [/providers/vllm](/ja-JP/providers/vllm) を参照してください。

### SGLang

SGLang は、高速なセルフホスト型
OpenAI 互換サーバー向けバンドル済みプロバイダープラグインとして提供されています。

- プロバイダー: `sglang`
- 認証: 任意（サーバー構成による）
- デフォルトの base URL: `http://127.0.0.1:30000/v1`

ローカルで自動検出を有効化するには（サーバーが
認証を強制しない場合は任意の値で動作します）:

```bash
export SGLANG_API_KEY="sglang-local"
```

次にモデルを設定します（`/v1/models` が返す ID のいずれかに置き換えてください）:

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

詳細は [/providers/sglang](/ja-JP/providers/sglang) を参照してください。

### ローカルプロキシ（LM Studio、vLLM、LiteLLM など）

例（OpenAI 互換）:

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

注:

- カスタムプロバイダーでは、`reasoning`, `input`, `cost`, `contextWindow`, `maxTokens` は任意です。
  省略した場合、OpenClaw のデフォルトは次のとおりです:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 推奨: プロキシ/モデルの制限に一致する明示的な値を設定してください。
- ネイティブでないエンドポイント上の `api: "openai-completions"`（`api.openai.com` ではないホストを持つ、空でない `baseUrl`）では、OpenClaw は
  サポートされない `developer` ロールによるプロバイダー 400 エラーを避けるため、
  `compat.supportsDeveloperRole: false` を強制します。
- プロキシ型の OpenAI 互換ルートでは、ネイティブ OpenAI 専用のリクエスト
  整形もスキップされます。`service_tier` なし、Responses の `store` なし、prompt-cache ヒントなし、
  OpenAI reasoning 互換ペイロード整形なし、非表示の OpenClaw 属性
  ヘッダーなしです。
- `baseUrl` が空または省略されている場合、OpenClaw はデフォルトの OpenAI 動作（`api.openai.com` に解決される）を維持します。
- 安全のため、ネイティブでない `openai-completions` エンドポイントでは、明示的な `compat.supportsDeveloperRole: true` も引き続き上書きされます。

## CLI 例

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

あわせて参照: 完全な設定例は [/gateway/configuration](/ja-JP/gateway/configuration) を参照してください。

## 関連

- [Models](/ja-JP/concepts/models) — モデル設定とエイリアス
- [Model Failover](/ja-JP/concepts/model-failover) — フォールバックチェーンと再試行動作
- [Configuration Reference](/ja-JP/gateway/configuration-reference#agent-defaults) — モデル設定キー
- [Providers](/ja-JP/providers) — プロバイダーごとのセットアップガイド
