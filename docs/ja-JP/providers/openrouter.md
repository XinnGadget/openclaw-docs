---
read_when:
    - 多くの LLM に対して 1 つの API キーを使いたい
    - OpenClaw で OpenRouter 経由でモデルを実行したい
summary: OpenRouter の統合 API を使って OpenClaw で多くのモデルにアクセスする
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T23:32:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter は、単一の
エンドポイントと API キーの背後で、多数のモデルにリクエストをルーティングする**統合 API**を提供します。OpenAI 互換なので、ほとんどの OpenAI SDK は base URL を切り替えるだけで動作します。

## はじめに

<Steps>
  <Step title="API キーを取得する">
    API キーは [openrouter.ai/keys](https://openrouter.ai/keys) で作成します。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="（オプション）特定のモデルに切り替える">
    オンボーディングではデフォルトで `openrouter/auto` が設定されます。後から具体的なモデルを選択できます:

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## 設定例

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## Model ref

<Note>
Model ref は `openrouter/<provider>/<model>` というパターンに従います。利用可能な
プロバイダーとモデルの完全な一覧については、[/concepts/model-providers](/ja-JP/concepts/model-providers) を参照してください。
</Note>

## 認証とヘッダー

OpenRouter は内部的に、API キー付きの Bearer トークンを使用します。

実際の OpenRouter リクエスト（`https://openrouter.ai/api/v1`）では、OpenClaw は
OpenRouter が文書化しているアプリ帰属ヘッダーも追加します:

| Header | Value |
| ------------------------- | --------------------- |
| `HTTP-Referer` | `https://openclaw.ai` |
| `X-OpenRouter-Title` | `OpenClaw` |
| `X-OpenRouter-Categories` | `cli-agent` |

<Warning>
OpenRouter プロバイダーを別のプロキシや base URL に向け直した場合、OpenClaw
はそれらの OpenRouter 固有ヘッダーや Anthropic キャッシュ マーカーを**注入しません**。
</Warning>

## 高度な注意事項

<AccordionGroup>
  <Accordion title="Anthropic キャッシュ マーカー">
    検証済みの OpenRouter ルートでは、Anthropic model ref は
    システム/開発者プロンプト ブロックでより良いプロンプト キャッシュ再利用のために OpenClaw が使用する、
    OpenRouter 固有の Anthropic `cache_control` マーカーを維持します。
  </Accordion>

  <Accordion title="Thinking / reasoning 注入">
    サポートされる非 `auto` ルートでは、OpenClaw は選択した thinking レベルを
    OpenRouter プロキシ reasoning ペイロードにマッピングします。非対応のモデル ヒントおよび
    `openrouter/auto` では、その reasoning 注入をスキップします。
  </Accordion>

  <Accordion title="OpenAI 専用のリクエスト整形">
    OpenRouter は引き続きプロキシ スタイルの OpenAI 互換パスを通るため、
    `serviceTier`、Responses の `store`、
    OpenAI reasoning 互換ペイロード、プロンプト キャッシュ ヒントなどのネイティブ OpenAI 専用リクエスト整形は転送されません。
  </Accordion>

  <Accordion title="Gemini ベースのルート">
    Gemini ベースの OpenRouter ref はプロキシ Gemini パスに留まります: OpenClaw は
    そこで Gemini の thought-signature サニタイズを維持しますが、ネイティブ Gemini の
    リプレイ検証やブートストラップ リライトは有効にしません。
  </Accordion>

  <Accordion title="プロバイダー ルーティング メタデータ">
    model params の下で OpenRouter のプロバイダー ルーティングを渡すと、OpenClaw は
    共有ストリーム ラッパーが実行される前に、それを OpenRouter のルーティング メタデータとして転送します。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    エージェント、モデル、プロバイダーの完全な設定リファレンス。
  </Card>
</CardGroup>
