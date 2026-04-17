---
read_when:
    - OpenClaw で GLM モデルを使いたい
    - モデル命名規則とセットアップが必要です
summary: GLM モデルファミリーの概要と OpenClaw での使い方
title: GLM (Zhipu)
x-i18n:
    generated_at: "2026-04-12T23:31:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: b38f0896c900fae3cf3458ff99938d73fa46973a057d1dd373ae960cb7d2e9b5
    source_path: providers/glm.md
    workflow: 15
---

# GLM モデル

GLM は **モデルファミリー**（企業ではありません）であり、Z.AI プラットフォームを通じて利用できます。OpenClaw では、GLM
モデルは `zai` provider と `zai/glm-5` のような model ID を通じてアクセスします。

## はじめに

<Steps>
  <Step title="認証ルートを選んでオンボーディングを実行する">
    Z.AI のプランとリージョンに一致するオンボーディング選択を選んでください。

    | Auth choice | 最適な用途 |
    | ----------- | -------- |
    | `zai-api-key` | エンドポイント自動検出付きの汎用 API キー設定 |
    | `zai-coding-global` | Coding Plan ユーザー（グローバル） |
    | `zai-coding-cn` | Coding Plan ユーザー（中国リージョン） |
    | `zai-global` | 一般 API（グローバル） |
    | `zai-cn` | 一般 API（中国リージョン） |

    ```bash
    # 例: 汎用自動検出
    openclaw onboard --auth-choice zai-api-key

    # 例: Coding Plan グローバル
    openclaw onboard --auth-choice zai-coding-global
    ```

  </Step>
  <Step title="GLM をデフォルトモデルとして設定する">
    ```bash
    openclaw config set agents.defaults.model.primary "zai/glm-5.1"
    ```
  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider zai
    ```
  </Step>
</Steps>

## 設定例

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

<Tip>
`zai-api-key` を使うと、OpenClaw はキーから一致する Z.AI エンドポイントを検出し、正しい base URL を自動的に適用します。特定の Coding Plan または一般 API サーフェスを強制したい場合は、明示的なリージョン選択を使用してください。
</Tip>

## バンドル済み GLM モデル

OpenClaw は現在、バンドル済み `zai` provider に次の GLM ref を初期登録しています。

| モデル           | モデル            |
| --------------- | ---------------- |
| `glm-5.1`       | `glm-4.7`        |
| `glm-5`         | `glm-4.7-flash`  |
| `glm-5-turbo`   | `glm-4.7-flashx` |
| `glm-5v-turbo`  | `glm-4.6`        |
| `glm-4.5`       | `glm-4.6v`       |
| `glm-4.5-air`   |                  |
| `glm-4.5-flash` |                  |
| `glm-4.5v`      |                  |

<Note>
デフォルトのバンドル済み model ref は `zai/glm-5.1` です。GLM のバージョンと提供状況は変わる可能性があるため、最新情報は Z.AI のドキュメントを確認してください。
</Note>

## 高度な注意事項

<AccordionGroup>
  <Accordion title="エンドポイント自動検出">
    `zai-api-key` の auth choice を使用すると、OpenClaw はキー形式を調べて正しい Z.AI base URL を判断します。明示的なリージョン選択
    （`zai-coding-global`、`zai-coding-cn`、`zai-global`、`zai-cn`）は自動検出を上書きし、エンドポイントを直接固定します。
  </Accordion>

  <Accordion title="provider の詳細">
    GLM モデルは `zai` 実行時 provider により提供されます。完全な provider
    設定、リージョンエンドポイント、追加機能については、
    [Z.AI provider ドキュメント](/ja-JP/providers/zai) を参照してください。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Z.AI provider" href="/ja-JP/providers/zai" icon="server">
    完全な Z.AI provider 設定とリージョンエンドポイント。
  </Card>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
</CardGroup>
