---
read_when:
    - OpenClaw で Xiaomi MiMo モデルを使いたい場合
    - '`XIAOMI_API_KEY` の設定が必要な場合'
summary: OpenClaw で Xiaomi MiMo モデルを使う
title: Xiaomi MiMo
x-i18n:
    generated_at: "2026-04-12T23:34:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: cd5a526764c796da7e1fff61301bc2ec618e1cf3857894ba2ef4b6dd9c4dc339
    source_path: providers/xiaomi.md
    workflow: 15
---

# Xiaomi MiMo

Xiaomi MiMo は **MiMo** モデル向けの API プラットフォームです。OpenClaw は、API キー認証付きの Xiaomi の OpenAI 互換エンドポイントを使用します。

| 項目 | 値 |
| -------- | ------------------------------- |
| Provider | `xiaomi` |
| Auth | `XIAOMI_API_KEY` |
| API | OpenAI 互換 |
| Base URL | `https://api.xiaomimimo.com/v1` |

## はじめに

<Steps>
  <Step title="API キーを取得する">
    [Xiaomi MiMo console](https://platform.xiaomimimo.com/#/console/api-keys) で API キーを作成します。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice xiaomi-api-key
    ```

    またはキーを直接渡します。

    ```bash
    openclaw onboard --auth-choice xiaomi-api-key --xiaomi-api-key "$XIAOMI_API_KEY"
    ```

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider xiaomi
    ```
  </Step>
</Steps>

## 利用可能なモデル

| モデル参照 | 入力 | コンテキスト | 最大出力 | 推論 | 注記 |
| ---------------------- | ----------- | --------- | ---------- | --------- | ------------- |
| `xiaomi/mimo-v2-flash` | text | 262,144 | 8,192 | いいえ | デフォルトモデル |
| `xiaomi/mimo-v2-pro` | text | 1,048,576 | 32,000 | はい | 大きなコンテキスト |
| `xiaomi/mimo-v2-omni` | text, image | 262,144 | 32,000 | はい | マルチモーダル |

<Tip>
デフォルトのモデル参照は `xiaomi/mimo-v2-flash` です。`XIAOMI_API_KEY` が設定されているか auth プロファイルが存在する場合、provider は自動的に注入されます。
</Tip>

## 設定例

```json5
{
  env: { XIAOMI_API_KEY: "your-key" },
  agents: { defaults: { model: { primary: "xiaomi/mimo-v2-flash" } } },
  models: {
    mode: "merge",
    providers: {
      xiaomi: {
        baseUrl: "https://api.xiaomimimo.com/v1",
        api: "openai-completions",
        apiKey: "XIAOMI_API_KEY",
        models: [
          {
            id: "mimo-v2-flash",
            name: "Xiaomi MiMo V2 Flash",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 8192,
          },
          {
            id: "mimo-v2-pro",
            name: "Xiaomi MiMo V2 Pro",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 1048576,
            maxTokens: 32000,
          },
          {
            id: "mimo-v2-omni",
            name: "Xiaomi MiMo V2 Omni",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 32000,
          },
        ],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="自動注入の動作">
    `XIAOMI_API_KEY` が環境変数に設定されているか、auth プロファイルが存在する場合、`xiaomi` provider は自動的に注入されます。モデルメタデータや base URL を上書きしたい場合を除き、手動で provider を設定する必要はありません。
  </Accordion>

  <Accordion title="モデル詳細">
    - **mimo-v2-flash** — 軽量で高速。一般的なテキストタスクに最適です。推論サポートはありません。
    - **mimo-v2-pro** — 推論をサポートし、長文ドキュメント向けに 1M トークンのコンテキストウィンドウを備えます。
    - **mimo-v2-omni** — テキスト入力と画像入力の両方を受け付ける、推論対応のマルチモーダルモデルです。

    <Note>
    すべてのモデルは `xiaomi/` プレフィックスを使用します（例: `xiaomi/mimo-v2-pro`）。
    </Note>

  </Accordion>

  <Accordion title="トラブルシューティング">
    - モデルが表示されない場合は、`XIAOMI_API_KEY` が設定されていて有効であることを確認してください。
    - Gateway がデーモンとして実行される場合は、そのプロセスでキーが利用可能であることを確認してください（たとえば `~/.openclaw/.env` または `env.shellEnv`）。

    <Warning>
    対話シェルにのみ設定されたキーは、デーモン管理された gateway プロセスからは見えません。継続的に利用できるようにするには、`~/.openclaw/.env` または `env.shellEnv` 設定を使用してください。
    </Warning>

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Configuration reference" href="/ja-JP/gateway/configuration" icon="gear">
    OpenClaw の完全な設定リファレンス。
  </Card>
  <Card title="Xiaomi MiMo console" href="https://platform.xiaomimimo.com" icon="arrow-up-right-from-square">
    Xiaomi MiMo ダッシュボードと API キー管理。
  </Card>
</CardGroup>
