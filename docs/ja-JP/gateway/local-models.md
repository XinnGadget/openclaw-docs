---
read_when:
    - 自分の GPU マシンからモデルを提供したい
    - LM Studio または OpenAI 互換プロキシを接続している
    - 最も安全なローカルモデルのガイダンスが必要
summary: ローカル LLM（LM Studio、vLLM、LiteLLM、カスタム OpenAI エンドポイント）で OpenClaw を実行する
title: ローカルモデル
x-i18n:
    generated_at: "2026-04-08T02:15:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: d619d72b0e06914ebacb7e9f38b746caf1b9ce8908c9c6638c3acdddbaa025e8
    source_path: gateway/local-models.md
    workflow: 15
---

# ローカルモデル

ローカル運用は可能ですが、OpenClaw は大きなコンテキストと、プロンプトインジェクションに対する強力な防御を前提としています。小さなカードではコンテキストが切り詰められ、安全性も低下します。高い構成を目指してください: **最大構成の Mac Studio 2 台以上、または同等の GPU リグ（約 $30k+）**。単一の **24 GB** GPU は、レイテンシが高くなる軽めのプロンプトでのみ実用的です。実行可能な中で **最大 / フルサイズのモデルバリアント** を使ってください。強い量子化が施された、または「small」なチェックポイントは、プロンプトインジェクションのリスクを高めます（[セキュリティ](/ja-JP/gateway/security) を参照）。

最も手間の少ないローカルセットアップを望む場合は、[Ollama](/ja-JP/providers/ollama) と `openclaw onboard` から始めてください。このページは、より高性能なローカルスタックと、カスタムの OpenAI 互換ローカルサーバー向けの方針重視ガイドです。

## 推奨: LM Studio + 大規模ローカルモデル（Responses API）

現時点で最良のローカルスタックです。LM Studio に大規模モデル（たとえば、フルサイズの Qwen、DeepSeek、または Llama ビルド）を読み込み、ローカルサーバー（デフォルトは `http://127.0.0.1:1234`）を有効にし、推論を最終テキストと分離するために Responses API を使用します。

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

- LM Studio をインストールします: [https://lmstudio.ai](https://lmstudio.ai)
- LM Studio で、**利用可能な中で最大のモデルビルド** をダウンロードし（「small」/強い量子化版は避けてください）、サーバーを起動し、`http://127.0.0.1:1234/v1/models` に一覧表示されることを確認します。
- `my-local-model` を、LM Studio に表示される実際のモデル ID に置き換えます。
- モデルをロードしたままにします。コールドロードは起動レイテンシを追加します。
- LM Studio のビルドが異なる場合は、`contextWindow` / `maxTokens` を調整します。
- WhatsApp では、最終テキストだけが送信されるように Responses API を使ってください。

ローカル実行時でもホスト型モデルは設定したままにしてください。`models.mode: "merge"` を使うと、フォールバックを利用可能なままにできます。

### ハイブリッド設定: ホスト型をプライマリ、ローカルをフォールバック

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

### ローカル優先、ホスト型を安全網として使用

プライマリとフォールバックの順序を入れ替え、同じ providers ブロックと `models.mode: "merge"` を維持してください。これにより、ローカルマシンが停止しているときに Sonnet や Opus にフォールバックできます。

### リージョナルホスティング / データルーティング

- ホスト型の MiniMax / Kimi / GLM バリアントは、リージョン固定エンドポイント（例: US ホスト）を持つ OpenRouter 上にも存在します。そこでリージョナルバリアントを選択すると、`models.mode: "merge"` を使った Anthropic/OpenAI フォールバックを維持しつつ、トラフィックを選択した法域内に留められます。
- ローカル専用は依然として最も強力なプライバシー経路です。ホスト型リージョナルルーティングは、プロバイダー機能が必要だがデータフローも制御したい場合の中間案です。

## その他の OpenAI 互換ローカルプロキシ

vLLM、LiteLLM、OAI-proxy、またはカスタム Gateway は、OpenAI 形式の `/v1` エンドポイントを公開していれば動作します。上記の provider ブロックを、自分のエンドポイントとモデル ID に置き換えてください。

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

ホスト型モデルをフォールバックとして利用可能なままにするため、`models.mode: "merge"` を維持してください。

ローカル / プロキシ経由の `/v1` バックエンドに関する動作メモ:

- OpenClaw はこれらをネイティブな
  OpenAI エンドポイントではなく、プロキシ形式の OpenAI 互換ルートとして扱います
- ここでは OpenAI 専用のネイティブなリクエスト整形は適用されません:
  `service_tier`、Responses の `store`、OpenAI の reasoning 互換ペイロード
  整形、プロンプトキャッシュヒントはありません
- 非表示の OpenClaw 属性ヘッダー（`originator`、`version`、`User-Agent`）は、
  これらのカスタムプロキシ URL には挿入されません

より厳格な OpenAI 互換バックエンド向けの互換性メモ:

- 一部のサーバーは Chat Completions で、構造化された content-part 配列ではなく、
  文字列の `messages[].content` だけを受け付けます。そのようなエンドポイントでは、
  `models.providers.<provider>.models[].compat.requiresStringContent: true` を
  設定してください。
- より小規模または厳格なローカルバックエンドの中には、OpenClaw の完全な
  エージェントランタイム用プロンプト形状、特にツールスキーマが含まれる場合に不安定になるものがあります。その
  バックエンドが小さな直接 `/v1/chat/completions` 呼び出しでは動作しても、通常の
  OpenClaw エージェントターンでは失敗する場合は、まず
  `models.providers.<provider>.models[].compat.supportsTools: false` を試してください。
- それでもバックエンドが大きめの OpenClaw 実行時にだけ失敗する場合、残る問題は通常
  OpenClaw のトランスポート層ではなく、上流のモデル / サーバー容量、またはバックエンドの不具合です。

## トラブルシューティング

- Gateway はプロキシに到達できますか？ `curl http://127.0.0.1:1234/v1/models`
- LM Studio のモデルがアンロードされていますか？ 再ロードしてください。コールドスタートは「ハングしている」ように見える一般的な原因です。
- コンテキストエラーですか？ `contextWindow` を下げるか、サーバー側の上限を上げてください。
- OpenAI 互換サーバーが `messages[].content ... expected a string` を返しますか？
  そのモデルエントリーに `compat.requiresStringContent: true` を追加してください。
- 小さな直接 `/v1/chat/completions` 呼び出しは動作するのに、`openclaw infer model run`
  が Gemma や他のローカルモデルで失敗しますか？ まず
  `compat.supportsTools: false` でツールスキーマを無効にし、その後再テストしてください。それでもサーバーが
  より大きな OpenClaw プロンプトでのみクラッシュする場合は、上流サーバー / モデルの制限として扱ってください。
- 安全性: ローカルモデルはプロバイダー側フィルターを通りません。プロンプトインジェクションの影響範囲を抑えるため、エージェントは限定的にし、圧縮は有効のままにしてください。
