---
read_when:
    - 自分のGPUマシンからモデルを提供したい場合
    - LM StudioまたはOpenAI互換プロキシを設定している場合
    - 最も安全なローカルモデルのガイダンスが必要な場合
summary: ローカルLLM（LM Studio、vLLM、LiteLLM、カスタムOpenAIエンドポイント）でOpenClawを実行する
title: ローカルモデル
x-i18n:
    generated_at: "2026-04-15T14:40:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7a506ff83e4c2870d3878339f646c906584454a156ecd618c360f592cf3b0011
    source_path: gateway/local-models.md
    workflow: 15
---

# ローカルモデル

ローカル運用は可能ですが、OpenClawは大きなコンテキストと、プロンプトインジェクションに対する強力な防御を前提としています。小規模なGPUではコンテキストが切り詰められ、安全性も低下します。目標は高く設定してください: **最大構成のMac Studio 2台以上、または同等のGPUリグ（約3万ドル以上）**。単一の**24 GB** GPUでも、より軽いプロンプトで高いレイテンシを許容するなら動作します。実行可能な範囲で**最大級 / フルサイズのモデルバリアント**を使ってください。強く量子化されたチェックポイントや「small」なチェックポイントは、プロンプトインジェクションのリスクを高めます（[Security](/ja-JP/gateway/security)を参照）。

最も手間の少ないローカル構成を望むなら、[LM Studio](/ja-JP/providers/lmstudio)または[Ollama](/ja-JP/providers/ollama)と`openclaw onboard`から始めてください。このページは、より高性能なローカルスタックやカスタムのOpenAI互換ローカルサーバー向けの、方針を明確にしたガイドです。

## 推奨: LM Studio + 大規模ローカルモデル（Responses API）

現時点で最良のローカルスタックです。LM Studioで大規模モデル（たとえばフルサイズのQwen、DeepSeek、Llamaビルド）を読み込み、ローカルサーバー（デフォルトは`http://127.0.0.1:1234`）を有効化し、Responses APIを使って推論を最終テキストから分離してください。

```json5
{
  agents: {
    defaults: {
      model: { primary: “lmstudio/my-local-model” },
      models: {
        “anthropic/claude-opus-4-6”: { alias: “Opus” },
        “lmstudio/my-local-model”: { alias: “Local” },
      },
    },
  },
  models: {
    mode: “merge”,
    providers: {
      lmstudio: {
        baseUrl: “http://127.0.0.1:1234/v1”,
        apiKey: “lmstudio”,
        api: “openai-responses”,
        models: [
          {
            id: “my-local-model”,
            name: “Local Model”,
            reasoning: false,
            input: [“text”],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

**セットアップチェックリスト**

- LM Studioをインストール: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studioで、利用可能な**最大のモデルビルド**をダウンロードし（「small」や強い量子化バリアントは避けてください）、サーバーを起動して、`http://127.0.0.1:1234/v1/models`にそのモデルが一覧表示されることを確認します。
- `my-local-model`を、LM Studioに表示される実際のモデルIDに置き換えます。
- モデルは読み込んだままにしてください。コールドロードは起動レイテンシを追加します。
- LM Studioのビルドに応じて`contextWindow`/`maxTokens`を調整します。
- WhatsAppでは、最終テキストだけが送信されるよう、Responses APIを使ってください。

ローカル実行時でもホスト型モデルは設定したままにしてください。`models.mode: "merge"`を使うことで、フォールバックを利用可能なまま維持できます。

### ハイブリッド構成: ホスト型をプライマリ、ローカルをフォールバック

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-6",
        fallbacks: ["lmstudio/my-local-model", "anthropic/claude-opus-4-6"],
      },
      models: {
        "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
        "lmstudio/my-local-model": { alias: "Local" },
        "anthropic/claude-opus-4-6": { alias: "Opus" },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      lmstudio: {
        baseUrl: "http://127.0.0.1:1234/v1",
        apiKey: "lmstudio",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 196608,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

### ローカル優先、ホスト型をセーフティネットに

プライマリとフォールバックの順序を入れ替えてください。プロバイダーブロックと`models.mode: "merge"`はそのままにし、ローカルマシンが停止したときにSonnetやOpusへフォールバックできるようにします。

### リージョン別ホスティング / データルーティング

- ホスト型のMiniMax/Kimi/GLMバリアントは、リージョン固定エンドポイント（たとえばUSホスト）付きでOpenRouter上にも存在します。そこではリージョンバリアントを選ぶことで、`models.mode: "merge"`を使ったAnthropic/OpenAIフォールバックを維持しつつ、トラフィックを選択した管轄内に留められます。
- ローカル専用が最も強力なプライバシー経路です。ホスト型のリージョナルルーティングは、プロバイダー機能が必要だがデータフローの制御もしたい場合の中間的な選択肢です。

## その他のOpenAI互換ローカルプロキシ

vLLM、LiteLLM、OAI-proxy、またはカスタムGatewayは、OpenAIスタイルの`/v1`エンドポイントを公開していれば利用できます。上記のプロバイダーブロックを、あなたのエンドポイントとモデルIDに置き換えてください。

```json5
{
  models: {
    mode: "merge",
    providers: {
      local: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "sk-local",
        api: "openai-responses",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 120000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

ホスト型モデルをフォールバックとして使い続けられるよう、`models.mode: "merge"`を維持してください。

ローカル / プロキシ化された`/v1`バックエンドの動作に関する注意:

- OpenClawはこれらをネイティブな
  OpenAIエンドポイントではなく、プロキシ形式のOpenAI互換ルートとして扱います
- ここではOpenAIネイティブ専用のリクエスト整形は適用されません:
  `service_tier`、Responsesの`store`、OpenAIのreasoning互換ペイロード整形、
  プロンプトキャッシュヒントは使われません
- 非公開のOpenClawアトリビューションヘッダー（`originator`、`version`、`User-Agent`）
  は、これらのカスタムプロキシURLには注入されません

より厳格なOpenAI互換バックエンド向けの互換性メモ:

- 一部のサーバーは、Chat Completionsで構造化されたcontent-part配列ではなく、
  文字列の`messages[].content`のみを受け付けます。そのようなエンドポイントでは、
  `models.providers.<provider>.models[].compat.requiresStringContent: true`を
  設定してください。
- 一部の小規模またはより厳格なローカルバックエンドは、OpenClawの完全な
  agent-runtimeプロンプト形式、特にtool schemaが含まれる場合に不安定です。
  バックエンドが小さな直接の`/v1/chat/completions`呼び出しでは動作するのに、
  通常のOpenClaw agentターンでは失敗する場合、まず
  `agents.defaults.experimental.localModelLean: true`を試して、
  `browser`、`cron`、`message`のような重量級のデフォルトtoolを落としてください。
  これは実験的なフラグであり、安定したデフォルトモード設定ではありません。
  [Experimental Features](/ja-JP/concepts/experimental-features)を参照してください。
  それでも失敗する場合は、
  `models.providers.<provider>.models[].compat.supportsTools: false`を試してください。
- それでもOpenClawの大きめの実行時にだけバックエンドが失敗する場合、
  残っている問題は通常、OpenClawのトランスポート層ではなく、
  上流のモデル / サーバー容量またはバックエンドのバグです。

## トラブルシューティング

- Gatewayはプロキシに到達できますか？ `curl http://127.0.0.1:1234/v1/models`
- LM Studioのモデルがアンロードされていますか？ 再読み込みしてください。コールドスタートは「ハングしている」ように見える一般的な原因です。
- 検出されたコンテキストウィンドウが**32k**未満の場合、OpenClawは警告を出し、**16k**未満ではブロックします。その事前チェックに引っかかった場合は、サーバー / モデルのコンテキスト上限を引き上げるか、より大きなモデルを選んでください。
- コンテキストエラーですか？ `contextWindow`を下げるか、サーバーの上限を引き上げてください。
- OpenAI互換サーバーが`messages[].content ... expected a string`を返しますか？
  そのモデルエントリに`compat.requiresStringContent: true`を追加してください。
- 小さな直接の`/v1/chat/completions`呼び出しは動作するのに、
  `openclaw infer model run`がGemmaや他のローカルモデルで失敗しますか？
  まず`compat.supportsTools: false`でtool schemaを無効にしてから再テストしてください。
  それでもOpenClawのより大きなプロンプトでのみサーバーがクラッシュするなら、
  上流のサーバー / モデルの制限として扱ってください。
- 安全性: ローカルモデルはプロバイダー側フィルターをスキップするため、プロンプトインジェクションの影響範囲を抑えるために、agentは狭く保ち、Compactionを有効にしておいてください。
