---
read_when:
    - プロバイダーごとのモデル設定リファレンスが必要な場合
    - モデルプロバイダー向けの設定例や CLI のオンボーディングコマンドを確認したい場合
summary: 設定例と CLI フローを含むモデルプロバイダーの概要
title: モデルプロバイダー
x-i18n:
    generated_at: "2026-04-08T02:16:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 26b36a2bc19a28a7ef39aa8e81a0050fea1d452ac4969122e5cdf8755e690258
    source_path: concepts/model-providers.md
    workflow: 15
---

# モデルプロバイダー

このページでは、**LLM/モデルプロバイダー**（WhatsApp/Telegram のようなチャットチャネルではなく）を扱います。
モデル選択ルールについては、[/concepts/models](/ja-JP/concepts/models) を参照してください。

## クイックルール

- モデル参照は `provider/model` を使用します（例: `opencode/claude-opus-4-6`）。
- `agents.defaults.models` を設定すると、それが許可リストになります。
- CLI ヘルパー: `openclaw onboard`、`openclaw models list`、`openclaw models set <provider/model>`
- フォールバックのランタイムルール、クールダウンプローブ、セッション上書きの永続化は
  [/concepts/model-failover](/ja-JP/concepts/model-failover) に記載されています。
- `models.providers.*.models[].contextWindow` はネイティブなモデルメタデータです。
  `models.providers.*.models[].contextTokens` は実効ランタイム上限です。
- プロバイダープラグインは `registerProvider({ catalog })` によってモデルカタログを注入できます。
  OpenClaw はその出力を `models.providers` にマージしてから
  `models.json` を書き込みます。
- プロバイダーマニフェストは `providerAuthEnvVars` を宣言できるため、
  汎用の環境変数ベース認証プローブでプラグインのランタイムを読み込む必要がありません。残るコアの環境変数マップは、非プラグイン/コアプロバイダーと、Anthropic の API キー優先オンボーディングのような一部の汎用優先順位ケース向けだけになりました。
- プロバイダープラグインは、以下を通じてプロバイダーのランタイム動作も所有できます:
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
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot`, and
  `onModelSelected`。
- 注: プロバイダーランタイムの `capabilities` は共有ランナーメタデータ（プロバイダーファミリー、トランスクリプト/ツールの癖、トランスポート/キャッシュのヒント）です。これは、プラグインが何を登録するか（テキスト推論、音声など）を説明する [public capability model](/ja-JP/plugins/architecture#public-capability-model) とは異なります。

## プラグイン所有のプロバイダー動作

プロバイダープラグインは、OpenClaw が汎用推論ループを維持しつつ、
ほとんどのプロバイダー固有ロジックを所有できるようになりました。

一般的な分担:

- `auth[].run` / `auth[].runNonInteractive`: プロバイダーが `openclaw onboard`、`openclaw models auth`、ヘッドレスセットアップ向けのオンボーディング/ログインフローを所有
- `wizard.setup` / `wizard.modelPicker`: プロバイダーが認証選択ラベル、レガシーエイリアス、オンボーディング許可リストのヒント、オンボーディング/モデルピッカー内のセットアップ項目を所有
- `catalog`: プロバイダーが `models.providers` に表示される
- `normalizeModelId`: プロバイダーがレガシー/プレビューのモデル ID を検索または正規化前に正規化
- `normalizeTransport`: プロバイダーが汎用モデル組み立て前にトランスポートファミリーの `api` / `baseUrl` を正規化し、OpenClaw はまず一致したプロバイダーを確認し、その後、実際にトランスポートを変更するまで他のフック対応プロバイダープラグインを確認します
- `normalizeConfig`: プロバイダーがランタイムで使用する前に `models.providers.<id>` 設定を正規化します。OpenClaw はまず一致したプロバイダーを確認し、その後、実際に設定を変更するまで他のフック対応プロバイダープラグインを確認します。どのプロバイダーフックも設定を書き換えない場合、バンドルされた Google ファミリーヘルパーが引き続き対応する Google プロバイダーエントリーを正規化します。
- `applyNativeStreamingUsageCompat`: プロバイダーが、設定プロバイダー向けにエンドポイント駆動のネイティブ streaming-usage 互換リライトを適用
- `resolveConfigApiKey`: プロバイダーが、設定プロバイダー向けに完全なランタイム認証読み込みを強制せず環境変数マーカー認証を解決します。`amazon-bedrock` には、Bedrock ランタイム認証が AWS SDK のデフォルトチェーンを使うにもかかわらず、ここに組み込みの AWS 環境変数マーカーリゾルバーもあります。
- `resolveSyntheticAuth`: プロバイダーが、平文シークレットを永続化せずに local/self-hosted やその他の設定ベース認証可用性を公開可能
- `shouldDeferSyntheticProfileAuth`: プロバイダーが、保存済みの synthetic profile プレースホルダーを env/config ベース認証より低い優先度として扱うよう指定可能
- `resolveDynamicModel`: プロバイダーが、まだローカル静的カタログに存在しないモデル ID を受け入れ
- `prepareDynamicModel`: プロバイダーが、動的解決の再試行前にメタデータ更新を必要とする
- `normalizeResolvedModel`: プロバイダーが、トランスポートまたはベース URL のリライトを必要とする
- `contributeResolvedModelCompat`: プロバイダーが、別の互換トランスポート経由で届いた場合でも自社ベンダーモデル向けの互換フラグを提供
- `capabilities`: プロバイダーがトランスクリプト/ツーリング/プロバイダーファミリーの癖を公開
- `normalizeToolSchemas`: プロバイダーが埋め込みランナーが見る前にツールスキーマをクリーンアップ
- `inspectToolSchemas`: プロバイダーが正規化後にトランスポート固有のスキーマ警告を公開
- `resolveReasoningOutputMode`: プロバイダーがネイティブかタグ付きかの reasoning-output 契約を選択
- `prepareExtraParams`: プロバイダーがモデルごとのリクエストパラメーターをデフォルト化または正規化
- `createStreamFn`: プロバイダーが通常のストリームパスを完全カスタムのトランスポートに置き換え
- `wrapStreamFn`: プロバイダーがリクエストヘッダー/ボディ/モデル互換ラッパーを適用
- `resolveTransportTurnState`: プロバイダーがターンごとのネイティブトランスポートヘッダーまたはメタデータを供給
- `resolveWebSocketSessionPolicy`: プロバイダーがネイティブ WebSocket セッションヘッダーまたはセッションクールダウンポリシーを供給
- `createEmbeddingProvider`: プロバイダーが、コアの embedding スイッチボードではなくプロバイダープラグイン側に属するメモリ embedding 動作を所有
- `formatApiKey`: プロバイダーが保存済み認証プロファイルを、トランスポートが期待するランタイム `apiKey` 文字列へ整形
- `refreshOAuth`: 共有の `pi-ai` リフレッシャーで十分でない場合に、プロバイダーが OAuth 更新を所有
- `buildAuthDoctorHint`: OAuth 更新失敗時に、プロバイダーが修復ガイダンスを追記
- `matchesContextOverflowError`: プロバイダーが、汎用ヒューリスティクスでは見逃すプロバイダー固有のコンテキストウィンドウ超過エラーを認識
- `classifyFailoverReason`: プロバイダーが、プロバイダー固有の生のトランスポート/API エラーを、レート制限や過負荷などのフェイルオーバー理由へマッピング
- `isCacheTtlEligible`: プロバイダーが、どの上流モデル ID がプロンプトキャッシュ TTL をサポートするかを判定
- `buildMissingAuthMessage`: プロバイダーが、汎用 auth-store エラーをプロバイダー固有の回復ヒントに置き換え
- `suppressBuiltInModel`: プロバイダーが古い上流行を非表示にし、直接解決失敗時にベンダー所有のエラーを返せる
- `augmentModelCatalog`: プロバイダーが、検出と設定マージの後に synthetic/final カタログ行を追加
- `isBinaryThinking`: プロバイダーがバイナリのオン/オフ thinking UX を所有
- `supportsXHighThinking`: プロバイダーが選択モデルを `xhigh` に対応させる
- `resolveDefaultThinkingLevel`: プロバイダーがモデルファミリー向けのデフォルト `/think` ポリシーを所有
- `applyConfigDefaults`: プロバイダーが認証モード、環境変数、またはモデルファミリーに基づき、設定マテリアライズ時にプロバイダー固有のグローバルデフォルトを適用
- `isModernModelRef`: プロバイダーが live/smoke の優先モデル一致を所有
- `prepareRuntimeAuth`: プロバイダーが設定済み資格情報を短命なランタイムトークンへ変換
- `resolveUsageAuth`: プロバイダーが `/usage` および関連するステータス/レポート画面向けの使用量/クォータ資格情報を解決
- `fetchUsageSnapshot`: プロバイダーが使用量エンドポイントの取得/解析を所有し、コアは引き続きサマリーの外枠と整形を所有
- `onModelSelected`: プロバイダーが、テレメトリーやプロバイダー所有のセッション記録管理のような選択後副作用を実行

現在のバンドル例:

- `anthropic`: Claude 4.6 の前方互換フォールバック、認証修復ヒント、使用量エンドポイント取得、cache-TTL/プロバイダーファミリーメタデータ、認証対応のグローバル設定デフォルト
- `amazon-bedrock`: Bedrock 固有のスロットリング/未準備エラーに対するプロバイダー所有のコンテキスト超過一致とフェイルオーバー理由分類、および Anthropic トラフィック上の Claude 専用 replay-policy ガード向け共有 `anthropic-by-model` リプレイファミリー
- `anthropic-vertex`: Anthropic-message トラフィック上の Claude 専用 replay-policy ガード
- `openrouter`: パススルーモデル ID、リクエストラッパー、プロバイダー capability ヒント、プロキシ Gemini トラフィック上の Gemini thought-signature サニタイズ、`openrouter-thinking` ストリームファミリー経由のプロキシ reasoning 注入、ルーティングメタデータ転送、cache-TTL ポリシー
- `github-copilot`: オンボーディング/デバイスログイン、前方互換モデルフォールバック、Claude-thinking のトランスクリプトヒント、ランタイムトークン交換、使用量エンドポイント取得
- `openai`: GPT-5.4 の前方互換フォールバック、直接 OpenAI トランスポート正規化、Codex 対応の認証不足ヒント、Spark 抑制、synthetic OpenAI/Codex カタログ行、thinking/live-model ポリシー、使用量トークン別名の正規化（`input` / `output` および `prompt` / `completion` ファミリー）、ネイティブ OpenAI/Codex ラッパー向け共有 `openai-responses-defaults` ストリームファミリー、プロバイダーファミリーメタデータ、`gpt-image-1` 向けバンドル画像生成プロバイダー登録、`sora-2` 向けバンドル動画生成プロバイダー登録
- `google` と `google-gemini-cli`: Gemini 3.1 の前方互換フォールバック、ネイティブ Gemini リプレイ検証、ブートストラップリプレイのサニタイズ、タグ付き reasoning-output モード、modern-model 一致、Gemini image-preview モデル向けバンドル画像生成プロバイダー登録、Veo モデル向けバンドル動画生成プロバイダー登録。Gemini CLI OAuth はさらに、認証プロファイルのトークン整形、使用量トークン解析、使用量画面向けクォータエンドポイント取得も所有
- `moonshot`: 共有トランスポート、プラグイン所有の thinking ペイロード正規化
- `kilocode`: 共有トランスポート、プラグイン所有のリクエストヘッダー、reasoning ペイロード正規化、プロキシ Gemini thought-signature サニタイズ、cache-TTL ポリシー
- `zai`: GLM-5 の前方互換フォールバック、`tool_stream` デフォルト、cache-TTL ポリシー、バイナリ thinking/live-model ポリシー、使用量認証 + クォータ取得。未知の `glm-5*` ID はバンドルされた `glm-4.7` テンプレートから合成されます
- `xai`: ネイティブ Responses トランスポート正規化、Grok 高速バリアント向け `/fast` エイリアス書き換え、デフォルト `tool_stream`、xAI 固有のツールスキーマ / reasoning ペイロードのクリーンアップ、`grok-imagine-video` 向けバンドル動画生成プロバイダー登録
- `mistral`: プラグイン所有の capability メタデータ
- `opencode` と `opencode-go`: プラグイン所有の capability メタデータに加え、プロキシ Gemini thought-signature サニタイズ
- `alibaba`: `alibaba/wan2.6-t2v` のような直接 Wan モデル参照向けのプラグイン所有動画生成カタログ
- `byteplus`: プラグイン所有カタログに加え、Seedance テキスト動画/画像動画モデル向けバンドル動画生成プロバイダー登録
- `fal`: ホスト型サードパーティー画像モデル向けバンドル画像生成プロバイダー登録に加え、ホスト型サードパーティー動画モデル向けバンドル動画生成プロバイダー登録
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway`, および `volcengine`:
  プラグイン所有カタログのみ
- `qwen`: テキストモデル向けプラグイン所有カタログに加え、マルチモーダル画面向けの共有 media-understanding と動画生成プロバイダー登録。Qwen の動画生成は、`wan2.6-t2v` や `wan2.7-r2v` のようなバンドル Wan モデルを用いる Standard DashScope 動画エンドポイントを使用します
- `runway`: `gen4.5` のようなネイティブ Runway タスクベースモデル向けプラグイン所有動画生成プロバイダー登録
- `minimax`: プラグイン所有カタログ、Hailuo 動画モデル向けバンドル動画生成プロバイダー登録、`image-01` 向けバンドル画像生成プロバイダー登録、ハイブリッド Anthropic/OpenAI replay-policy 選択、使用量認証/スナップショットロジック
- `together`: プラグイン所有カタログに加え、Wan 動画モデル向けバンドル動画生成プロバイダー登録
- `xiaomi`: プラグイン所有カタログに加え、使用量認証/スナップショットロジック

バンドルされた `openai` プラグインは現在、両方のプロバイダー ID を所有しています:
`openai` と `openai-codex`。

ここまでが、OpenClaw の通常トランスポートにまだ収まるプロバイダーです。完全にカスタムなリクエスト実行器を必要とするプロバイダーは、別のより深い拡張サーフェスになります。

## API キーローテーション

- 選択されたプロバイダー向けの汎用プロバイダーローテーションをサポートします。
- 複数キーの設定方法:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY`（単一の live 上書き、最優先）
  - `<PROVIDER>_API_KEYS`（カンマまたはセミコロン区切りリスト）
  - `<PROVIDER>_API_KEY`（プライマリキー）
  - `<PROVIDER>_API_KEY_*`（番号付きリスト、例: `<PROVIDER>_API_KEY_1`）
- Google プロバイダーでは、フォールバックとして `GOOGLE_API_KEY` も含まれます。
- キーの選択順序は優先順位を維持し、値の重複を除去します。
- リクエストは、レート制限応答の場合にのみ次のキーで再試行されます（例: `429`、`rate_limit`、`quota`、`resource exhausted`、`Too many
concurrent requests`、`ThrottlingException`、`concurrency limit reached`、
  `workers_ai ... quota limit exceeded`、または定期的な usage-limit メッセージ）。
- レート制限以外の失敗は即座に失敗し、キーローテーションは試行されません。
- すべての候補キーが失敗した場合、最後の試行での最終エラーが返されます。

## 組み込みプロバイダー（pi-ai カタログ）

OpenClaw には pi‑ai カタログが同梱されています。これらのプロバイダーでは
`models.providers` 設定は**不要**です。認証を設定してモデルを選ぶだけです。

### OpenAI

- プロバイダー: `openai`
- 認証: `OPENAI_API_KEY`
- オプションのローテーション: `OPENAI_API_KEYS`、`OPENAI_API_KEY_1`、`OPENAI_API_KEY_2`、および `OPENCLAW_LIVE_OPENAI_KEY`（単一上書き）
- モデル例: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- デフォルトのトランスポートは `auto`（WebSocket 優先、SSE フォールバック）
- モデルごとの上書きは `agents.defaults.models["openai/<model>"].params.transport` で行います（`"sse"`、`"websocket"`、または `"auto"`）
- OpenAI Responses WebSocket ウォームアップは、`params.openaiWsWarmup`（`true`/`false`）によりデフォルトで有効です
- OpenAI priority processing は `agents.defaults.models["openai/<model>"].params.serviceTier` で有効化できます
- `/fast` と `params.fastMode` は、直接 `openai/*` Responses リクエストを `api.openai.com` 上の `service_tier=priority` にマッピングします
- 共有 `/fast` トグルの代わりに明示的な tier を指定したい場合は `params.serviceTier` を使用します
- 非表示の OpenClaw 帰属ヘッダー（`originator`, `version`,
  `User-Agent`）は、`api.openai.com` へのネイティブ OpenAI トラフィックにのみ適用され、
  汎用の OpenAI 互換プロキシには適用されません
- ネイティブ OpenAI ルートでは、Responses の `store`、プロンプトキャッシュのヒント、
  OpenAI reasoning 互換ペイロード整形も維持されます。プロキシルートでは維持されません
- `openai/gpt-5.3-codex-spark` は、live OpenAI API がこれを拒否するため、OpenClaw では意図的に抑制されています。Spark は Codex 専用として扱われます

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- プロバイダー: `anthropic`
- 認証: `ANTHROPIC_API_KEY`
- オプションのローテーション: `ANTHROPIC_API_KEYS`、`ANTHROPIC_API_KEY_1`、`ANTHROPIC_API_KEY_2`、および `OPENCLAW_LIVE_ANTHROPIC_KEY`（単一上書き）
- モデル例: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- 直接の公開 Anthropic リクエストでは、共有 `/fast` トグルと `params.fastMode` もサポートされます。これには `api.anthropic.com` に送信される API キー認証および OAuth 認証トラフィックも含まれ、OpenClaw はこれを Anthropic の `service_tier`（`auto` 対 `standard_only`）にマッピングします
- Anthropic に関する注記: Anthropic スタッフから、OpenClaw スタイルの Claude CLI 利用は再び許可されていると伝えられたため、Anthropic が新しいポリシーを公開しない限り、OpenClaw はこの統合において Claude CLI の再利用と `claude -p` の利用を認可済みとして扱います。
- Anthropic setup-token は引き続きサポートされる OpenClaw トークン経路として利用可能ですが、OpenClaw は現在、利用可能な場合は Claude CLI の再利用と `claude -p` を優先します。

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
- デフォルトのトランスポートは `auto`（WebSocket 優先、SSE フォールバック）
- モデルごとの上書きは `agents.defaults.models["openai-codex/<model>"].params.transport` で行います（`"sse"`、`"websocket"`、または `"auto"`）
- `params.serviceTier` もネイティブ Codex Responses リクエスト（`chatgpt.com/backend-api`）で転送されます
- 非表示の OpenClaw 帰属ヘッダー（`originator`, `version`,
  `User-Agent`）は、`chatgpt.com/backend-api` へのネイティブ Codex トラフィックにのみ付与され、
  汎用の OpenAI 互換プロキシには付与されません
- 直接 `openai/*` と同じ `/fast` トグルおよび `params.fastMode` 設定を共有し、OpenClaw はこれを `service_tier=priority` にマッピングします
- `openai-codex/gpt-5.3-codex-spark` は、Codex OAuth カタログが公開している場合は引き続き利用可能です。権限依存です
- `openai-codex/gpt-5.4` はネイティブの `contextWindow = 1050000` とデフォルトのランタイム `contextTokens = 272000` を維持します。ランタイム上限は `models.providers.openai-codex.models[].contextTokens` で上書きできます
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

- [Qwen Cloud](/ja-JP/providers/qwen): Qwen Cloud プロバイダーサーフェスに加え、Alibaba DashScope および Coding Plan エンドポイントのマッピング
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
- オプションのローテーション: `GEMINI_API_KEYS`、`GEMINI_API_KEY_1`、`GEMINI_API_KEY_2`、`GOOGLE_API_KEY` フォールバック、および `OPENCLAW_LIVE_GEMINI_KEY`（単一上書き）
- モデル例: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- 互換性: `google/gemini-3.1-flash-preview` を使う従来の OpenClaw 設定は `google/gemini-3-flash-preview` に正規化されます
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- 直接 Gemini 実行では `agents.defaults.models["google/<model>"].params.cachedContent`
  （または従来の `cached_content`）も受け付け、
  プロバイダーネイティブの `cachedContents/...` ハンドルを転送します。Gemini のキャッシュヒットは OpenClaw の `cacheRead` として表示されます

### Google Vertex と Gemini CLI

- プロバイダー: `google-vertex`, `google-gemini-cli`
- 認証: Vertex は gcloud ADC を使用、Gemini CLI は独自の OAuth フローを使用
- 注意: OpenClaw における Gemini CLI OAuth は非公式統合です。サードパーティークライアントの使用後に Google アカウントの制限が報告された例があります。利用する場合は Google の利用規約を確認し、重要でないアカウントを使ってください。
- Gemini CLI OAuth は、バンドルされた `google` プラグインの一部として提供されます。
  - まず Gemini CLI をインストールします:
    - `brew install gemini-cli`
    - または `npm install -g @google/gemini-cli`
  - 有効化: `openclaw plugins enable google`
  - ログイン: `openclaw models auth login --provider google-gemini-cli --set-default`
  - デフォルトモデル: `google-gemini-cli/gemini-3-flash-preview`
  - 注: `openclaw.json` に client id や secret を貼り付ける必要は**ありません**。CLI ログインフローは
    トークンを Gateway ホスト上の認証プロファイルに保存します。
  - ログイン後にリクエストが失敗する場合は、Gateway ホストで `GOOGLE_CLOUD_PROJECT` または `GOOGLE_CLOUD_PROJECT_ID` を設定してください。
  - Gemini CLI の JSON 応答は `response` から解析され、使用量は
    `stats` にフォールバックします。`stats.cached` は OpenClaw の `cacheRead` に正規化されます。

### Z.AI（GLM）

- プロバイダー: `zai`
- 認証: `ZAI_API_KEY`
- モデル例: `zai/glm-5`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - エイリアス: `z.ai/*` と `z-ai/*` は `zai/*` に正規化されます
  - `zai-api-key` は一致する Z.AI エンドポイントを自動検出します。`zai-coding-global`、`zai-coding-cn`、`zai-global`、`zai-cn` は特定のサーフェスを強制します

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
  live の `https://api.kilo.ai/api/gateway/models` 検出によりランタイム
  カタログをさらに拡張できます。
- `kilocode/kilo/auto` の背後にある正確な上流ルーティングは Kilo Gateway が所有しており、
  OpenClaw にハードコードされていません。

セットアップの詳細は [/providers/kilocode](/ja-JP/providers/kilocode) を参照してください。

### その他のバンドル済みプロバイダープラグイン

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- モデル例: `openrouter/auto`
- OpenClaw は、リクエストが実際に `openrouter.ai` を対象としている場合にのみ、
  OpenRouter の文書化されたアプリ帰属ヘッダーを適用します
- OpenRouter 固有の Anthropic `cache_control` マーカーも同様に、
  任意のプロキシ URL ではなく、検証済み OpenRouter ルートにのみ適用されます
- OpenRouter は引き続きプロキシ型の OpenAI 互換パス上にあるため、
  ネイティブ OpenAI 専用のリクエスト整形（`serviceTier`、Responses `store`、
  プロンプトキャッシュヒント、OpenAI reasoning 互換ペイロード）は転送されません
- Gemini ベースの OpenRouter 参照では、プロキシ Gemini thought-signature サニタイズのみ維持されます。ネイティブ Gemini リプレイ検証とブートストラップ書き換えは無効のままです
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- モデル例: `kilocode/kilo/auto`
- Gemini ベースの Kilo 参照では同じプロキシ Gemini thought-signature
  サニタイズ経路が維持されます。`kilocode/kilo/auto` やその他の proxy-reasoning 非対応ヒントでは、プロキシ reasoning 注入をスキップします
- MiniMax: `minimax`（API キー）および `minimax-portal`（OAuth）
- 認証: `minimax` には `MINIMAX_API_KEY`、`minimax-portal` には `MINIMAX_OAUTH_TOKEN` または `MINIMAX_API_KEY`
- モデル例: `minimax/MiniMax-M2.7` または `minimax-portal/MiniMax-M2.7`
- MiniMax のオンボーディング/API キー設定では、`input: ["text", "image"]` を持つ明示的な M2.7 モデル定義を書き込みます。バンドルされたプロバイダーカタログでは、そのプロバイダー設定がマテリアライズされるまではチャット参照を text-only のままにします
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- モデル例: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` または `KIMICODE_API_KEY`)
- モデル例: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- モデル例: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY`, または `DASHSCOPE_API_KEY`)
- モデル例: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- モデル例: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- モデル例: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- モデル例: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- モデル例: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` または `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- モデル例: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- モデル例: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - ネイティブにバンドルされた xAI リクエストは xAI Responses パスを使用します
  - `/fast` または `params.fastMode: true` は `grok-3`, `grok-3-mini`,
    `grok-4`, `grok-4-0709` をそれぞれの `*-fast` バリアントに書き換えます
  - `tool_stream` はデフォルトで有効です。
    `agents.defaults.models["xai/<model>"].params.tool_stream` を `false` に設定して
    無効化できます
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- モデル例: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - Cerebras 上の GLM モデルは `zai-glm-4.7` および `zai-glm-4.6` の ID を使用します。
  - OpenAI 互換ベース URL: `https://api.cerebras.ai/v1`。
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Hugging Face Inference のモデル例: `huggingface/deepseek-ai/DeepSeek-R1`。CLI: `openclaw onboard --auth-choice huggingface-api-key`。詳細は [Hugging Face (Inference)](/ja-JP/providers/huggingface) を参照してください。

## `models.providers` 経由のプロバイダー（カスタム/ベース URL）

`models.providers`（または `models.json`）を使用して、**カスタム**プロバイダーまたは
OpenAI/Anthropic 互換プロキシを追加します。

以下のバンドル済みプロバイダープラグインの多くは、すでにデフォルトカタログを公開しています。
デフォルトのベース URL、ヘッダー、モデル一覧を上書きしたい場合にのみ、明示的な `models.providers.<id>` エントリーを使用してください。

### Moonshot AI（Kimi）

Moonshot はバンドル済みプロバイダープラグインとして提供されます。
通常は組み込みプロバイダーを使い、ベース URL やモデルメタデータを上書きする必要がある場合にのみ、明示的な `models.providers.moonshot` エントリーを追加してください。

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

従来の `kimi/k2p5` も互換モデル ID として引き続き受け付けられます。

### Volcano Engine（Doubao）

Volcano Engine（火山引擎）は、中国で Doubao やその他のモデルへのアクセスを提供します。

- プロバイダー: `volcengine`（コーディング: `volcengine-plan`）
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

オンボーディングはデフォルトでコーディングサーフェスを使用しますが、一般的な `volcengine/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、Volcengine の認証選択は
`volcengine/*` と `volcengine-plan/*` の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、
OpenClaw は空のプロバイダースコープピッカーを表示する代わりに、フィルターなしカタログへフォールバックします。

利用可能なモデル:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

コーディングモデル（`volcengine-plan`）:

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus（国際版）

BytePlus ARK は、国際ユーザー向けに Volcano Engine と同じモデルへのアクセスを提供します。

- プロバイダー: `byteplus`（コーディング: `byteplus-plan`）
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

オンボーディングはデフォルトでコーディングサーフェスを使用しますが、一般的な `byteplus/*`
カタログも同時に登録されます。

オンボーディング/モデル設定ピッカーでは、BytePlus の認証選択は
`byteplus/*` と `byteplus-plan/*` の両方の行を優先します。これらのモデルがまだ読み込まれていない場合、
OpenClaw は空のプロバイダースコープピッカーを表示する代わりに、フィルターなしカタログへフォールバックします。

利用可能なモデル:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

コーディングモデル（`byteplus-plan`）:

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic は、`synthetic` プロバイダーの背後で Anthropic 互換モデルを提供します。

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

MiniMax はカスタムエンドポイントを使用するため、`models.providers` 経由で設定します。

- MiniMax OAuth（Global）: `--auth-choice minimax-global-oauth`
- MiniMax OAuth（CN）: `--auth-choice minimax-cn-oauth`
- MiniMax API キー（Global）: `--auth-choice minimax-global-api`
- MiniMax API キー（CN）: `--auth-choice minimax-cn-api`
- 認証: `minimax` には `MINIMAX_API_KEY`、`minimax-portal` には
  `MINIMAX_OAUTH_TOKEN` または `MINIMAX_API_KEY`

セットアップの詳細、モデルオプション、設定スニペットについては [/providers/minimax](/ja-JP/providers/minimax) を参照してください。

MiniMax の Anthropic 互換ストリーミングパスでは、明示的に設定しない限り OpenClaw は thinking を
デフォルトで無効にし、`/fast on` は
`MiniMax-M2.7` を `MiniMax-M2.7-highspeed` に書き換えます。

プラグイン所有の capability 分担:

- テキスト/チャットのデフォルトは `minimax/MiniMax-M2.7` のまま
- 画像生成は `minimax/image-01` または `minimax-portal/image-01`
- 画像理解は、両方の MiniMax 認証パスでプラグイン所有の `MiniMax-VL-01`
- Web 検索は引き続きプロバイダー ID `minimax`

### Ollama

Ollama はバンドル済みプロバイダープラグインとして提供され、Ollama のネイティブ API を使用します。

- プロバイダー: `ollama`
- 認証: 不要（ローカルサーバー）
- モデル例: `ollama/llama3.3`
- インストール: [https://ollama.com/download](https://ollama.com/download)

```bash
# Ollama をインストールし、その後モデルを pull します:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama は `OLLAMA_API_KEY` でオプトインするとローカルの `http://127.0.0.1:11434` で検出され、
バンドルされたプロバイダープラグインが Ollama を直接
`openclaw onboard` とモデルピッカーに追加します。オンボーディング、cloud/local モード、カスタム設定については [/providers/ollama](/ja-JP/providers/ollama)
を参照してください。

### vLLM

vLLM は、local/self-hosted な OpenAI 互換
サーバー向けのバンドル済みプロバイダープラグインとして提供されます。

- プロバイダー: `vllm`
- 認証: オプション（サーバー依存）
- デフォルトベース URL: `http://127.0.0.1:8000/v1`

ローカルで自動検出にオプトインするには（サーバーが認証を強制しない場合、任意の値で動作します）:

```bash
export VLLM_API_KEY="vllm-local"
```

その後、モデルを設定します（`/v1/models` が返す ID のいずれかに置き換えてください）:

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

詳細は [/providers/vllm](/ja-JP/providers/vllm) を参照してください。

### SGLang

SGLang は、高速な self-hosted
OpenAI 互換サーバー向けのバンドル済みプロバイダープラグインとして提供されます。

- プロバイダー: `sglang`
- 認証: オプション（サーバー依存）
- デフォルトベース URL: `http://127.0.0.1:30000/v1`

ローカルで自動検出にオプトインするには（サーバーが
認証を強制しない場合、任意の値で動作します）:

```bash
export SGLANG_API_KEY="sglang-local"
```

その後、モデルを設定します（`/v1/models` が返す ID のいずれかに置き換えてください）:

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

- カスタムプロバイダーでは、`reasoning`、`input`、`cost`、`contextWindow`、`maxTokens` は省略可能です。
  省略した場合、OpenClaw のデフォルトは次のとおりです:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- 推奨: プロキシ/モデルの制限に一致する明示的な値を設定してください。
- ネイティブでないエンドポイントに対する `api: "openai-completions"` では（ホストが `api.openai.com` ではない任意の非空 `baseUrl`）、OpenClaw は、未対応の `developer` ロールによるプロバイダー 400 エラーを回避するため、`compat.supportsDeveloperRole: false` を強制します。
- プロキシ型の OpenAI 互換ルートでも、ネイティブ OpenAI 専用のリクエスト整形はスキップされます:
  `service_tier` なし、Responses `store` なし、プロンプトキャッシュヒントなし、
  OpenAI reasoning 互換ペイロード整形なし、非表示の OpenClaw 帰属
  ヘッダーなし。
- `baseUrl` が空または省略されている場合、OpenClaw はデフォルトの OpenAI 動作（`api.openai.com` に解決される）を維持します。
- 安全のため、ネイティブでない `openai-completions` エンドポイントでは、明示的な `compat.supportsDeveloperRole: true` も引き続き上書きされます。

## CLI の例

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
