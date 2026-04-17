---
read_when:
    - Moonshot K2（Moonshot Open Platform）と Kimi Coding のセットアップを比較したい場合
    - 別々のエンドポイント、キー、モデル参照を理解する必要がある場合
    - どちらの provider に対してもそのまま使える設定例が欲しい場合
summary: Moonshot K2 と Kimi Coding を設定する（別々の provider とキー）
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-12T23:32:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f261f83a9b37e4fffb0cd0803e0c64f27eae8bae91b91d8a781a030663076f8
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI（Kimi）

Moonshot は OpenAI 互換エンドポイントを備えた Kimi API を提供します。provider を設定し、デフォルトモデルを `moonshot/kimi-k2.5` に設定するか、`kimi/kimi-code` を使って Kimi Coding を使用します。

<Warning>
Moonshot と Kimi Coding は**別々の provider**です。キーに互換性はなく、エンドポイントも異なり、モデル参照も異なります（`moonshot/...` と `kimi/...`）。
</Warning>

## 組み込みモデルカタログ

[//]: # "moonshot-kimi-k2-ids:start"

| モデル参照 | 名前 | 推論 | 入力 | コンテキスト | 最大出力 |
| --------------------------------- | ---------------------- | --------- | ----------- | ------- | ---------- |
| `moonshot/kimi-k2.5` | Kimi K2.5 | いいえ | text, image | 262,144 | 262,144 |
| `moonshot/kimi-k2-thinking` | Kimi K2 Thinking | はい | text | 262,144 | 262,144 |
| `moonshot/kimi-k2-thinking-turbo` | Kimi K2 Thinking Turbo | はい | text | 262,144 | 262,144 |
| `moonshot/kimi-k2-turbo` | Kimi K2 Turbo | いいえ | text | 256,000 | 16,384 |

[//]: # "moonshot-kimi-k2-ids:end"

## はじめに

使用する provider を選び、セットアップ手順に従ってください。

<Tabs>
  <Tab title="Moonshot API">
    **最適な用途:** Moonshot Open Platform 経由で Kimi K2 モデルを使う場合。

    <Steps>
      <Step title="エンドポイントのリージョンを選ぶ">
        | 認証選択肢 | エンドポイント | リージョン |
        | ---------------------- | ------------------------------ | ------------- |
        | `moonshot-api-key` | `https://api.moonshot.ai/v1` | International |
        | `moonshot-api-key-cn` | `https://api.moonshot.cn/v1` | China |
      </Step>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard --auth-choice moonshot-api-key
        ```

        または China エンドポイントの場合:

        ```bash
        openclaw onboard --auth-choice moonshot-api-key-cn
        ```
      </Step>
      <Step title="デフォルトモデルを設定する">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "moonshot/kimi-k2.5" },
            },
          },
        }
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider moonshot
        ```
      </Step>
    </Steps>

    ### 設定例

    ```json5
    {
      env: { MOONSHOT_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "moonshot/kimi-k2.5" },
          models: {
            // moonshot-kimi-k2-aliases:start
            "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
            "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
            "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
            "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
            // moonshot-kimi-k2-aliases:end
          },
        },
      },
      models: {
        mode: "merge",
        providers: {
          moonshot: {
            baseUrl: "https://api.moonshot.ai/v1",
            apiKey: "${MOONSHOT_API_KEY}",
            api: "openai-completions",
            models: [
              // moonshot-kimi-k2-models:start
              {
                id: "kimi-k2.5",
                name: "Kimi K2.5",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking",
                name: "Kimi K2 Thinking",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-thinking-turbo",
                name: "Kimi K2 Thinking Turbo",
                reasoning: true,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 262144,
                maxTokens: 262144,
              },
              {
                id: "kimi-k2-turbo",
                name: "Kimi K2 Turbo",
                reasoning: false,
                input: ["text"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 256000,
                maxTokens: 16384,
              },
              // moonshot-kimi-k2-models:end
            ],
          },
        },
      },
    }
    ```

  </Tab>

  <Tab title="Kimi Coding">
    **最適な用途:** Kimi Coding エンドポイント経由でコード中心のタスクを行う場合。

    <Note>
    Kimi Coding は、Moonshot（`moonshot/...`）とは異なる API キーと provider プレフィックス（`kimi/...`）を使用します。レガシーなモデル参照 `kimi/k2p5` も互換 ID として引き続き受け付けられます。
    </Note>

    <Steps>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard --auth-choice kimi-code-api-key
        ```
      </Step>
      <Step title="デフォルトモデルを設定する">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "kimi/kimi-code" },
            },
          },
        }
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider kimi
        ```
      </Step>
    </Steps>

    ### 設定例

    ```json5
    {
      env: { KIMI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "kimi/kimi-code" },
          models: {
            "kimi/kimi-code": { alias: "Kimi" },
          },
        },
      },
    }
    ```

  </Tab>
</Tabs>

## Kimi web search

OpenClaw には **Kimi** が `web_search` provider としても同梱されており、Moonshot web
search をバックエンドとして使用します。

<Steps>
  <Step title="対話型 web search セットアップを実行する">
    ```bash
    openclaw configure --section web
    ```

    web-search セクションで **Kimi** を選ぶと、
    `plugins.entries.moonshot.config.webSearch.*` が保存されます。

  </Step>
  <Step title="web search のリージョンとモデルを設定する">
    対話セットアップでは次が表示されます。

    | 設定 | 選択肢 |
    | ------------------- | -------------------------------------------------------------------- |
    | API リージョン | `https://api.moonshot.ai/v1`（international）または `https://api.moonshot.cn/v1`（China） |
    | Web search モデル | デフォルトは `kimi-k2.5` |

  </Step>
</Steps>

設定は `plugins.entries.moonshot.config.webSearch` 配下に保存されます。

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // または KIMI_API_KEY / MOONSHOT_API_KEY を使用
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## 高度な内容

<AccordionGroup>
  <Accordion title="ネイティブ thinking モード">
    Moonshot Kimi はバイナリのネイティブ thinking をサポートします。

    - `thinking: { type: "enabled" }`
    - `thinking: { type: "disabled" }`

    `agents.defaults.models.<provider/model>.params` でモデルごとに設定します。

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "moonshot/kimi-k2.5": {
              params: {
                thinking: { type: "disabled" },
              },
            },
          },
        },
      },
    }
    ```

    OpenClaw は Moonshot に対してランタイムの `/think` レベルもマッピングします。

    | `/think` レベル | Moonshot の動作 |
    | -------------------- | -------------------------- |
    | `/think off` | `thinking.type=disabled` |
    | off 以外の任意のレベル | `thinking.type=enabled` |

    <Warning>
    Moonshot thinking が有効な場合、`tool_choice` は `auto` または `none` である必要があります。OpenClaw は互換性のために、互換性のない `tool_choice` 値を `auto` に正規化します。
    </Warning>

  </Accordion>

  <Accordion title="ストリーミング usage 互換性">
    ネイティブ Moonshot エンドポイント（`https://api.moonshot.ai/v1` と
    `https://api.moonshot.cn/v1`）は、共有の
    `openai-completions` トランスポートでストリーミング usage 互換性を公開しています。OpenClaw
    はそれをエンドポイント capability に基づいて判断するため、同じネイティブ
    Moonshot ホストを対象とする互換カスタム provider ID は、同じ streaming-usage
    動作を引き継ぎます。
  </Accordion>

  <Accordion title="エンドポイントとモデル参照のリファレンス">
    | Provider | モデル参照プレフィックス | エンドポイント | Auth 環境変数 |
    | ---------- | ---------------- | ----------------------------- | ------------------- |
    | Moonshot | `moonshot/` | `https://api.moonshot.ai/v1` | `MOONSHOT_API_KEY` |
    | Moonshot CN| `moonshot/` | `https://api.moonshot.cn/v1` | `MOONSHOT_API_KEY` |
    | Kimi Coding| `kimi/` | Kimi Coding endpoint | `KIMI_API_KEY` |
    | Web search | N/A | Moonshot API リージョンと同じ | `KIMI_API_KEY` または `MOONSHOT_API_KEY` |

    - Kimi web search は `KIMI_API_KEY` または `MOONSHOT_API_KEY` を使用し、デフォルトは `https://api.moonshot.ai/v1`、モデルは `kimi-k2.5` です。
    - 必要に応じて `models.providers` で料金やコンテキストのメタデータを上書きしてください。
    - Moonshot があるモデルについて異なるコンテキスト制限を公開した場合は、それに応じて `contextWindow` を調整してください。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Web search" href="/tools/web-search" icon="magnifying-glass">
    Kimi を含む web search provider の設定方法。
  </Card>
  <Card title="Configuration reference" href="/ja-JP/gateway/configuration-reference" icon="gear">
    provider、モデル、Plugin の完全な設定スキーマ。
  </Card>
  <Card title="Moonshot Open Platform" href="https://platform.moonshot.ai" icon="globe">
    Moonshot API キー管理とドキュメント。
  </Card>
</CardGroup>
