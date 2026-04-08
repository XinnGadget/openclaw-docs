---
read_when:
    - ローカルのinferrsサーバーに対してOpenClawを実行したい場合
    - inferrs経由でGemmaまたは別のモデルを提供している場合
    - inferrs向けの正確なOpenClaw互換フラグが必要な場合
summary: inferrs（OpenAI互換ローカルサーバー）経由でOpenClawを実行する
title: inferrs
x-i18n:
    generated_at: "2026-04-08T02:18:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: d84f660d49a682d0c0878707eebe1bc1e83dd115850687076ea3938b9f9c86c6
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) は、
OpenAI互換の `/v1` API の背後でローカルモデルを提供できます。OpenClawは、汎用の
`openai-completions` 経路を通じて `inferrs` と連携します。

現在のところ、`inferrs` は専用のOpenClawプロバイダープラグインではなく、
カスタムのセルフホスト型OpenAI互換バックエンドとして扱うのが最適です。

## クイックスタート

1. モデルを指定して `inferrs` を起動します。

例:

```bash
inferrs serve gg-hf-gg/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. サーバーに到達できることを確認します。

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. 明示的なOpenClawプロバイダーエントリを追加し、デフォルトモデルがそれを指すようにします。

## 完全な設定例

この例では、ローカルの `inferrs` サーバー上でGemma 4を使用します。

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/gg-hf-gg/gemma-4-E2B-it" },
      models: {
        "inferrs/gg-hf-gg/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "gg-hf-gg/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## `requiresStringContent` が重要な理由

一部の `inferrs` Chat Completions 経路は、構造化されたcontent-part配列ではなく、
文字列の `messages[].content` のみを受け付けます。

OpenClawの実行が次のようなエラーで失敗する場合:

```text
messages[1].content: invalid type: sequence, expected a string
```

次を設定してください:

```json5
compat: {
  requiresStringContent: true
}
```

OpenClawは、リクエスト送信前に純粋なテキストcontent partをプレーンな文字列へ
フラット化します。

## Gemmaとツールスキーマに関する注意点

現在の一部の `inferrs` + Gemma の組み合わせでは、小さな直接
`/v1/chat/completions` リクエストは受け付けても、完全なOpenClaw agent-runtime
ターンでは失敗することがあります。

その場合は、まず次を試してください:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

これにより、そのモデル向けのOpenClawツールスキーマサーフェスが無効になり、
より厳格なローカルバックエンドに対するプロンプト負荷を下げられる場合があります。

小さな直接リクエストは依然として通るのに、通常のOpenClaw agentターンが
`inferrs` 内で引き続きクラッシュする場合、残っている問題は通常、
OpenClawの転送レイヤーではなく上流のモデル/サーバー動作です。

## 手動スモークテスト

設定後は、両方のレイヤーをテストしてください:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"gg-hf-gg/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/gg-hf-gg/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

最初のコマンドは動作するのに2つ目が失敗する場合は、以下の
トラブルシューティングメモを使ってください。

## トラブルシューティング

- `curl /v1/models` が失敗する: `inferrs` が起動していない、到達できない、または
  想定したホスト/ポートにバインドされていません。
- `messages[].content ... expected a string`: `compat.requiresStringContent: true`
  を設定してください。
- 直接の小さな `/v1/chat/completions` 呼び出しは成功するが、`openclaw infer model run`
  が失敗する: `compat.supportsTools: false` を試してください。
- OpenClawでスキーマエラーは出なくなったが、より大きなagentターンで `inferrs` が引き続きクラッシュする:
  上流の `inferrs` またはモデルの制限として扱い、プロンプト負荷を下げるか、
  ローカルバックエンド/モデルを切り替えてください。

## プロキシ型の動作

`inferrs` は、ネイティブなOpenAIエンドポイントではなく、
プロキシ型のOpenAI互換 `/v1` バックエンドとして扱われます。

- ここではネイティブOpenAI専用のリクエスト整形は適用されません
- `service_tier`、Responses の `store`、プロンプトキャッシュヒント、
  OpenAI reasoning互換ペイロード整形はありません
- 非公開のOpenClaw attribution ヘッダー（`originator`、`version`、`User-Agent`）は、
  カスタム `inferrs` base URL には注入されません

## 関連ドキュメント

- [Local models](/ja-JP/gateway/local-models)
- [Gateway troubleshooting](/ja-JP/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Model providers](/ja-JP/concepts/model-providers)
