---
read_when:
    - ローカルの SGLang サーバーに対して OpenClaw を実行したい
    - 自分のモデルで OpenAI 互換の `/v1` エンドポイントを使いたい
summary: OpenClaw を SGLang（OpenAI 互換のセルフホスト サーバー）で実行する
title: SGLang
x-i18n:
    generated_at: "2026-04-12T23:33:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: e0a2e50a499c3d25dcdc3af425fb023c6e3f19ed88f533ecf0eb8a2cb7ec8b0d
    source_path: providers/sglang.md
    workflow: 15
---

# SGLang

SGLang は、**OpenAI 互換** HTTP API を通じてオープンソース モデルを提供できます。
OpenClaw は `openai-completions` API を使って SGLang に接続できます。

また、`SGLANG_API_KEY` でオプトインし、
明示的な `models.providers.sglang` エントリを定義していない場合、OpenClaw は SGLang から利用可能なモデルを**自動検出**することもできます
（サーバーで認証を強制していない場合は任意の値で構いません）。

## はじめに

<Steps>
  <Step title="SGLang を起動する">
    OpenAI 互換サーバーで SGLang を起動します。base URL は
    `/v1` エンドポイント（たとえば `/v1/models`、`/v1/chat/completions`）を公開している必要があります。SGLang は一般に次で動作します:

    - `http://127.0.0.1:30000/v1`

  </Step>
  <Step title="API キーを設定する">
    サーバーで認証が設定されていない場合は、どんな値でも構いません:

    ```bash
    export SGLANG_API_KEY="sglang-local"
    ```

  </Step>
  <Step title="オンボーディングを実行する、またはモデルを直接設定する">
    ```bash
    openclaw onboard
    ```

    または、モデルを手動で設定します:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "sglang/your-model-id" },
        },
      },
    }
    ```

  </Step>
</Steps>

## モデル検出（暗黙のプロバイダー）

`SGLANG_API_KEY` が設定されている（または認証プロファイルが存在する）状態で、
`models.providers.sglang` を**定義していない**場合、OpenClaw は次を問い合わせます:

- `GET http://127.0.0.1:30000/v1/models`

そして、返された ID を model エントリに変換します。

<Note>
`models.providers.sglang` を明示的に設定した場合、自動検出はスキップされ、
モデルは手動で定義する必要があります。
</Note>

## 明示的な設定（手動モデル）

次の場合は明示的な設定を使用します:

- SGLang が別のホスト/ポートで動作している。
- `contextWindow` / `maxTokens` の値を固定したい。
- サーバーが実際の API キーを必要とする（またはヘッダーを制御したい）。

```json5
{
  models: {
    providers: {
      sglang: {
        baseUrl: "http://127.0.0.1:30000/v1",
        apiKey: "${SGLANG_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "your-model-id",
            name: "ローカル SGLang モデル",
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

## 高度な設定

<AccordionGroup>
  <Accordion title="プロキシ スタイルの挙動">
    SGLang は、ネイティブ OpenAI エンドポイントではなく、プロキシ スタイルの OpenAI 互換 `/v1` バックエンドとして扱われます。

    | Behavior | SGLang |
    |----------|--------|
    | OpenAI 専用のリクエスト整形 | 適用されない |
    | `service_tier`、Responses の `store`、プロンプト キャッシュ ヒント | 送信されない |
    | reasoning 互換ペイロード整形 | 適用されない |
    | 隠し帰属ヘッダー（`originator`, `version`, `User-Agent`） | カスタム SGLang base URL には注入されない |

  </Accordion>

  <Accordion title="トラブルシューティング">
    **サーバーに到達できない**

    サーバーが起動して応答していることを確認してください:

    ```bash
    curl http://127.0.0.1:30000/v1/models
    ```

    **認証エラー**

    リクエストが認証エラーで失敗する場合は、サーバー設定に一致する実際の `SGLANG_API_KEY` を設定するか、
    `models.providers.sglang` の下でプロバイダーを明示的に設定してください。

    <Tip>
    認証なしで SGLang を実行している場合、モデル検出にオプトインするには
    `SGLANG_API_KEY` に空でない任意の値を設定すれば十分です。
    </Tip>

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    プロバイダー エントリを含む完全な設定スキーマ。
  </Card>
</CardGroup>
