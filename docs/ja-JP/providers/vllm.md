---
read_when:
    - ローカルの vLLM サーバーに対して OpenClaw を実行したい
    - 自分のモデルで OpenAI 互換の `/v1` エンドポイントを使いたい
summary: OpenClaw を vLLM（OpenAI 互換のローカルサーバー）で実行する
title: vLLM
x-i18n:
    generated_at: "2026-04-12T23:33:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: a43be9ae879158fcd69d50fb3a47616fd560e3c6fe4ecb3a109bdda6a63a6a80
    source_path: providers/vllm.md
    workflow: 15
---

# vLLM

vLLM は、**OpenAI 互換** HTTP API を通じてオープンソースモデル（および一部のカスタムモデル）を提供できます。OpenClaw は `openai-completions` API を使用して vLLM に接続します。

OpenClaw は、`VLLM_API_KEY` でオプトインし（サーバーが auth を強制しない場合は任意の値で動作します）、明示的な `models.providers.vllm` エントリーを定義していないときに、vLLM から利用可能なモデルを**自動検出**することもできます。

| プロパティ         | 値                                       |
| ---------------- | ---------------------------------------- |
| Provider ID      | `vllm`                                   |
| API              | `openai-completions`（OpenAI 互換）      |
| Auth             | `VLLM_API_KEY` 環境変数                  |
| デフォルト base URL | `http://127.0.0.1:8000/v1`             |

## はじめに

<Steps>
  <Step title="OpenAI 互換サーバーとして vLLM を起動する">
    base URL は `/v1` エンドポイント（例: `/v1/models`、`/v1/chat/completions`）を公開している必要があります。vLLM は一般に次で動作します。

    ```
    http://127.0.0.1:8000/v1
    ```

  </Step>
  <Step title="API キー環境変数を設定する">
    サーバーが auth を強制しない場合は任意の値で動作します。

    ```bash
    export VLLM_API_KEY="vllm-local"
    ```

  </Step>
  <Step title="モデルを選択する">
    自分の vLLM model ID のいずれかに置き換えてください。

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vllm/your-model-id" },
        },
      },
    }
    ```

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider vllm
    ```
  </Step>
</Steps>

## モデル検出（暗黙的 provider）

`VLLM_API_KEY` が設定されている（または auth profile が存在する）状態で、**`models.providers.vllm` を定義していない**場合、OpenClaw は次を問い合わせます。

```
GET http://127.0.0.1:8000/v1/models
```

そして返された ID を model エントリーに変換します。

<Note>
`models.providers.vllm` を明示的に設定した場合、自動検出はスキップされ、model を手動で定義する必要があります。
</Note>

## 明示的設定（手動 model）

次のような場合は明示的設定を使用します。

- vLLM が別の host または port で動作している
- `contextWindow` や `maxTokens` の値を固定したい
- サーバーが実際の API キーを必要とする（またはヘッダーを制御したい）

```json5
{
  models: {
    providers: {
      vllm: {
        baseUrl: "http://127.0.0.1:8000/v1",
        apiKey: "${VLLM_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "Local vLLM Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 128000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

## 高度な注意事項

<AccordionGroup>
  <Accordion title="プロキシ型の動作">
    vLLM は、ネイティブな OpenAI エンドポイントではなく、プロキシ型の OpenAI 互換 `/v1` バックエンドとして扱われます。これは次を意味します。

    | 動作 | 適用されるか |
    |----------|----------|
    | ネイティブ OpenAI のリクエスト整形 | いいえ |
    | `service_tier` | 送信されない |
    | Responses `store` | 送信されない |
    | プロンプトキャッシュヒント | 送信されない |
    | OpenAI reasoning 互換ペイロード整形 | 適用されない |
    | 隠し OpenClaw attribution ヘッダー | カスタム base URL には注入されない |

  </Accordion>

  <Accordion title="カスタム base URL">
    vLLM サーバーがデフォルト以外の host または port で動作している場合は、明示的 provider 設定で `baseUrl` を設定します。

    ```json5
    {
      models: {
        providers: {
          vllm: {
            baseUrl: "http://192.168.1.50:9000/v1",
            apiKey: "${VLLM_API_KEY}",
            api: "openai-completions",
            models: [
              {
                id: "my-custom-model",
                name: "Remote vLLM Model",
                reasoning: false,
                input: ["text"],
                contextWindow: 64000,
                maxTokens: 4096,
              },
            ],
          },
        },
      },
    }
    ```

  </Accordion>
</AccordionGroup>

## トラブルシューティング

<AccordionGroup>
  <Accordion title="サーバーに到達できない">
    vLLM サーバーが起動していてアクセス可能であることを確認してください。

    ```bash
    curl http://127.0.0.1:8000/v1/models
    ```

    接続エラーが出る場合は、host、port、および vLLM が OpenAI 互換サーバーモードで起動していることを確認してください。

  </Accordion>

  <Accordion title="リクエストで auth エラーが出る">
    リクエストが auth エラーで失敗する場合は、サーバー設定に一致する実際の `VLLM_API_KEY` を設定するか、`models.providers.vllm` 配下で provider を明示的に設定してください。

    <Tip>
    vLLM サーバーが auth を強制しない場合、空でない任意の `VLLM_API_KEY` 値が OpenClaw のオプトインシグナルとして機能します。
    </Tip>

  </Accordion>

  <Accordion title="モデルが検出されない">
    自動検出には、`VLLM_API_KEY` が設定されていること**かつ**明示的な `models.providers.vllm` 設定エントリーがないことが必要です。provider を手動で定義している場合、OpenClaw は検出をスキップし、宣言した model のみを使用します。
  </Accordion>
</AccordionGroup>

<Warning>
詳細: [トラブルシューティング](/ja-JP/help/troubleshooting) と [FAQ](/ja-JP/help/faq)。
</Warning>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="OpenAI" href="/ja-JP/providers/openai" icon="bolt">
    ネイティブ OpenAI provider と OpenAI 互換ルートの動作。
  </Card>
  <Card title="OAuth と auth" href="/ja-JP/gateway/authentication" icon="key">
    auth の詳細と認証情報再利用ルール。
  </Card>
  <Card title="トラブルシューティング" href="/ja-JP/help/troubleshooting" icon="wrench">
    よくある問題とその解決方法。
  </Card>
</CardGroup>
