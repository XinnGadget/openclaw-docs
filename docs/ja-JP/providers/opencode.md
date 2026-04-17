---
read_when:
    - OpenCode がホストするモデルアクセスを使いたい場合
    - Zen カタログと Go カタログのどちらを使うか選びたい場合
summary: OpenCode Zen と Go カタログを OpenClaw で使う
title: OpenCode
x-i18n:
    generated_at: "2026-04-12T23:32:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: a68444d8c403c3caba4a18ea47f078c7a4c163f874560e1fad0e818afb6e0e60
    source_path: providers/opencode.md
    workflow: 15
---

# OpenCode

OpenCode は OpenClaw で 2 つのホスト型カタログを公開します。

| カタログ | プレフィックス | ランタイム provider |
| ------- | ----------------- | ---------------- |
| **Zen** | `opencode/...` | `opencode` |
| **Go** | `opencode-go/...` | `opencode-go` |

どちらのカタログも同じ OpenCode API キーを使用します。OpenClaw は、上流のモデルごとのルーティングを正しく保つためにランタイム provider ID を分けたままにしていますが、オンボーディングとドキュメントでは 1 つの OpenCode セットアップとして扱います。

## はじめに

<Tabs>
  <Tab title="Zen カタログ">
    **最適な用途:** 厳選された OpenCode マルチモデルプロキシ（Claude、GPT、Gemini）。

    <Steps>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard --auth-choice opencode-zen
        ```

        またはキーを直接渡します。

        ```bash
        openclaw onboard --opencode-zen-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Zen モデルをデフォルトに設定する">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode/claude-opus-4-6"
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider opencode
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Go カタログ">
    **最適な用途:** OpenCode がホストする Kimi、GLM、MiniMax のラインアップ。

    <Steps>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```

        またはキーを直接渡します。

        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
        ```
      </Step>
      <Step title="Go モデルをデフォルトに設定する">
        ```bash
        openclaw config set agents.defaults.model.primary "opencode-go/kimi-k2.5"
        ```
      </Step>
      <Step title="モデルが利用可能であることを確認する">
        ```bash
        openclaw models list --provider opencode-go
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 設定例

```json5
{
  env: { OPENCODE_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

## カタログ

### Zen

| 項目 | 値 |
| ---------------- | ----------------------------------------------------------------------- |
| ランタイム provider | `opencode` |
| モデル例 | `opencode/claude-opus-4-6`, `opencode/gpt-5.4`, `opencode/gemini-3-pro` |

### Go

| 項目 | 値 |
| ---------------- | ------------------------------------------------------------------------ |
| ランタイム provider | `opencode-go` |
| モデル例 | `opencode-go/kimi-k2.5`, `opencode-go/glm-5`, `opencode-go/minimax-m2.5` |

## 高度な注意事項

<AccordionGroup>
  <Accordion title="API キーのエイリアス">
    `OPENCODE_ZEN_API_KEY` も `OPENCODE_API_KEY` のエイリアスとしてサポートされています。
  </Accordion>

  <Accordion title="共有資格情報">
    セットアップ中に 1 つの OpenCode キーを入力すると、両方のランタイム
    provider の資格情報が保存されます。各カタログを個別にオンボーディングする必要はありません。
  </Accordion>

  <Accordion title="課金とダッシュボード">
    OpenCode にサインインし、課金情報を追加して、API キーをコピーします。課金
    とカタログの利用可否は OpenCode ダッシュボードから管理されます。
  </Accordion>

  <Accordion title="Gemini のリプレイ動作">
    Gemini をバックエンドとする OpenCode 参照はプロキシ Gemini 経路のままなので、OpenClaw
    はネイティブ Gemini のリプレイ検証やブートストラップ書き換えを有効にせずに、
    そこで Gemini の thought-signature サニタイズを維持します。
  </Accordion>

  <Accordion title="非 Gemini のリプレイ動作">
    非 Gemini の OpenCode 参照は、最小限の OpenAI 互換リプレイポリシーを維持します。
  </Accordion>
</AccordionGroup>

<Tip>
セットアップ中に 1 つの OpenCode キーを入力すると、Zen と
Go の両方のランタイム provider に資格情報が保存されるため、オンボーディングは 1 回だけで済みます。
</Tip>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Configuration reference" href="/ja-JP/gateway/configuration-reference" icon="gear">
    エージェント、モデル、provider の完全な設定リファレンス。
  </Card>
</CardGroup>
