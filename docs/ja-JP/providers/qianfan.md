---
read_when:
    - 多くの LLM に対して 1 つの API キーを使いたい
    - Baidu Qianfan のセットアップ ガイダンスが必要です
summary: Qianfan の統合 API を使って OpenClaw で多くのモデルにアクセスする
title: Qianfan
x-i18n:
    generated_at: "2026-04-12T23:33:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1d0eeee9ec24b335c2fb8ac5e985a9edc35cfc5b2641c545cb295dd2de619f50
    source_path: providers/qianfan.md
    workflow: 15
---

# Qianfan

Qianfan は Baidu の MaaS プラットフォームで、単一の
エンドポイントと API キーの背後で、多数のモデルにリクエストをルーティングする**統合 API**を提供します。OpenAI 互換なので、ほとんどの OpenAI SDK は base URL を切り替えるだけで動作します。

| Property | Value |
| -------- | ----- |
| プロバイダー | `qianfan` |
| 認証 | `QIANFAN_API_KEY` |
| API | OpenAI 互換 |
| ベース URL | `https://qianfan.baidubce.com/v2` |

## はじめに

<Steps>
  <Step title="Baidu Cloud アカウントを作成する">
    [Qianfan Console](https://console.bce.baidu.com/qianfan/ais/console/apiKey) で登録またはログインし、Qianfan API アクセスが有効になっていることを確認してください。
  </Step>
  <Step title="API キーを生成する">
    新しいアプリケーションを作成するか既存のものを選択し、API キーを生成します。キー形式は `bce-v3/ALTAK-...` です。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice qianfan-api-key
    ```
  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider qianfan
    ```
  </Step>
</Steps>

## 利用可能なモデル

| Model ref | Input | Context | Max output | Reasoning | Notes |
| ------------------------------------ | ----------- | ------- | ---------- | --------- | ------------- |
| `qianfan/deepseek-v3.2` | text | 98,304 | 32,768 | Yes | デフォルト モデル |
| `qianfan/ernie-5.0-thinking-preview` | text, image | 119,000 | 64,000 | Yes | マルチモーダル |

<Tip>
デフォルトのバンドル済み model ref は `qianfan/deepseek-v3.2` です。カスタム base URL またはモデル メタデータが必要な場合にのみ `models.providers.qianfan` を上書きする必要があります。
</Tip>

## 設定例

```json5
{
  env: { QIANFAN_API_KEY: "bce-v3/ALTAK-..." },
  agents: {
    defaults: {
      model: { primary: "qianfan/deepseek-v3.2" },
      models: {
        "qianfan/deepseek-v3.2": { alias: "QIANFAN" },
      },
    },
  },
  models: {
    providers: {
      qianfan: {
        baseUrl: "https://qianfan.baidubce.com/v2",
        api: "openai-completions",
        models: [
          {
            id: "deepseek-v3.2",
            name: "DEEPSEEK V3.2",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 98304,
            maxTokens: 32768,
          },
          {
            id: "ernie-5.0-thinking-preview",
            name: "ERNIE-5.0-Thinking-Preview",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 119000,
            maxTokens: 64000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="トランスポートと互換性">
    Qianfan は、ネイティブ OpenAI のリクエスト整形ではなく、OpenAI 互換のトランスポート パスを通ります。これは標準の OpenAI SDK 機能は動作する一方で、プロバイダー固有のパラメーターは転送されない可能性があることを意味します。
  </Accordion>

  <Accordion title="カタログとオーバーライド">
    現在、バンドルされたカタログには `deepseek-v3.2` と `ernie-5.0-thinking-preview` が含まれています。カスタム base URL またはモデル メタデータが必要な場合にのみ `models.providers.qianfan` を追加または上書きしてください。

    <Note>
    Model ref では `qianfan/` プレフィックスを使用します（例: `qianfan/deepseek-v3.2`）。
    </Note>

  </Accordion>

  <Accordion title="トラブルシューティング">
    - API キーが `bce-v3/ALTAK-` で始まり、Baidu Cloud コンソールで Qianfan API アクセスが有効になっていることを確認してください。
    - モデルが一覧表示されない場合は、アカウントで Qianfan サービスが有効化されていることを確認してください。
    - デフォルトの base URL は `https://qianfan.baidubce.com/v2` です。カスタム エンドポイントまたはプロキシを使う場合にのみ変更してください。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration" icon="gear">
    OpenClaw の完全な設定リファレンス。
  </Card>
  <Card title="エージェント設定" href="/ja-JP/concepts/agent" icon="robot">
    エージェントのデフォルトとモデル割り当ての設定。
  </Card>
  <Card title="Qianfan API ドキュメント" href="https://cloud.baidu.com/doc/qianfan-api/s/3m7of64lb" icon="arrow-up-right-from-square">
    公式の Qianfan API ドキュメント。
  </Card>
</CardGroup>
