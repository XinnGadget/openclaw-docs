---
read_when:
    - ローカルの inferrs サーバーに対して OpenClaw を実行したい
    - inferrs 経由で Gemma または別のモデルを提供している
    - inferrs 用の正確な OpenClaw 互換フラグが必要です
summary: OpenClaw を inferrs（OpenAI 互換のローカルサーバー）経由で実行する
title: inferrs
x-i18n:
    generated_at: "2026-04-12T23:31:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) は、OpenAI 互換の `/v1` API の背後でローカルモデルを提供できます。OpenClaw は、汎用の
`openai-completions` パスを通じて `inferrs` と連携します。

現在のところ、`inferrs` は専用の OpenClaw provider Plugin ではなく、カスタムのセルフホスト型 OpenAI 互換
バックエンドとして扱うのが最適です。

## はじめに

<Steps>
  <Step title="モデル付きで inferrs を起動する">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="サーバーに到達可能であることを確認する">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="OpenClaw の provider エントリーを追加する">
    明示的な provider エントリーを追加し、デフォルトモデルをそこに向けます。以下の完全な設定例を参照してください。
  </Step>
</Steps>

## 完全な設定例

この例では、ローカルの `inferrs` サーバー上の Gemma 4 を使用します。

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
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
            id: "google/gemma-4-E2B-it",
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

## 高度な設定

<AccordionGroup>
  <Accordion title="requiresStringContent が重要な理由">
    一部の `inferrs` Chat Completions ルートは、構造化された content-part 配列ではなく、文字列の
    `messages[].content` のみを受け付けます。

    <Warning>
    OpenClaw の実行が次のようなエラーで失敗する場合:

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    model エントリーで `compat.requiresStringContent: true` を設定してください。
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw は、リクエスト送信前に純粋なテキスト content part をプレーンな文字列へフラット化します。

  </Accordion>

  <Accordion title="Gemma とツールスキーマの注意点">
    現在の一部の `inferrs` + Gemma の組み合わせは、小さな直接
    `/v1/chat/completions` リクエストは受け付けても、完全な OpenClaw エージェント実行時の
    ターンでは失敗することがあります。

    その場合は、まずこれを試してください。

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    これにより、そのモデルに対する OpenClaw のツールスキーマサーフェスが無効になり、より厳格なローカルバックエンドでのプロンプト負荷を下げられる場合があります。

    それでも小さな直接リクエストは動作する一方で、通常の OpenClaw エージェントターンが引き続き `inferrs` 内でクラッシュする場合、残っている問題は通常、OpenClaw のトランスポート層ではなく上流の model/server の動作です。

  </Accordion>

  <Accordion title="手動スモークテスト">
    設定後は、両方のレイヤーをテストしてください。

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    最初のコマンドが動作し、2 つ目が失敗する場合は、以下のトラブルシューティングセクションを確認してください。

  </Accordion>

  <Accordion title="プロキシ型の動作">
    `inferrs` はネイティブな OpenAI エンドポイントではなく、プロキシ型の OpenAI 互換 `/v1` バックエンドとして扱われます。

    - ここではネイティブ OpenAI 専用のリクエスト整形は適用されません
    - `service_tier`、Responses の `store`、プロンプトキャッシュヒント、OpenAI reasoning 互換ペイロード整形はありません
    - カスタム `inferrs` base URL には、隠し OpenClaw attribution ヘッダー（`originator`、`version`、`User-Agent`）は注入されません

  </Accordion>
</AccordionGroup>

## トラブルシューティング

<AccordionGroup>
  <Accordion title="curl /v1/models が失敗する">
    `inferrs` が実行されていない、到達できない、または期待した
    host/port にバインドされていません。サーバーが起動していて、設定したアドレスで待ち受けていることを確認してください。
  </Accordion>

  <Accordion title="messages[].content に文字列が必要">
    model エントリーで `compat.requiresStringContent: true` を設定してください。詳細は上記の
    `requiresStringContent` セクションを参照してください。
  </Accordion>

  <Accordion title="直接の /v1/chat/completions 呼び出しは通るが openclaw infer model run が失敗する">
    ツールスキーマサーフェスを無効にするため、`compat.supportsTools: false` を設定してみてください。
    詳細は上記の Gemma のツールスキーマ注意点を参照してください。
  </Accordion>

  <Accordion title="大きなエージェントターンで inferrs がまだクラッシュする">
    OpenClaw でスキーマエラーが出なくなっても、大きな
    エージェントターンで `inferrs` が引き続きクラッシュする場合は、上流の `inferrs` または model の制限として扱ってください。プロンプト負荷を減らすか、別のローカルバックエンドまたは model に切り替えてください。
  </Accordion>
</AccordionGroup>

<Tip>
一般的なヘルプについては、[トラブルシューティング](/ja-JP/help/troubleshooting) と [FAQ](/ja-JP/help/faq) を参照してください。
</Tip>

## 関連項目

<CardGroup cols={2}>
  <Card title="ローカルモデル" href="/ja-JP/gateway/local-models" icon="server">
    ローカルモデルサーバーに対して OpenClaw を実行する方法。
  </Card>
  <Card title="Gateway のトラブルシューティング" href="/ja-JP/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    直接プローブは通るがエージェント実行に失敗するローカル OpenAI 互換バックエンドのデバッグ。
  </Card>
  <Card title="モデル provider" href="/ja-JP/concepts/model-providers" icon="layers">
    すべての provider、model ref、フェイルオーバー動作の概要。
  </Card>
</CardGroup>
