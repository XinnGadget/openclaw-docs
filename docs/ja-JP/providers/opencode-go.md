---
read_when:
    - OpenCode Go カタログを使いたい
    - Go でホストされるモデルの実行時 model ref が必要です
summary: 共有の OpenCode セットアップで OpenCode Go カタログを使う
title: OpenCode Go
x-i18n:
    generated_at: "2026-04-12T23:32:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: d1f0f182de81729616ccc19125d93ba0445de2349daf7067b52e8c15b9d3539c
    source_path: providers/opencode-go.md
    workflow: 15
---

# OpenCode Go

OpenCode Go は [OpenCode](/ja-JP/providers/opencode) 内の Go カタログです。
Zen カタログと同じ `OPENCODE_API_KEY` を使いますが、上流のモデルごとのルーティングを正しく保つために、実行時の
プロバイダー ID は `opencode-go` のままです。

| Property | Value |
| ---------------- | ------------------------------- |
| 実行時プロバイダー | `opencode-go` |
| 認証 | `OPENCODE_API_KEY` |
| 親セットアップ | [OpenCode](/ja-JP/providers/opencode) |

## サポートされるモデル

| Model ref | Name |
| -------------------------- | ------------ |
| `opencode-go/kimi-k2.5` | Kimi K2.5 |
| `opencode-go/glm-5` | GLM 5 |
| `opencode-go/minimax-m2.5` | MiniMax M2.5 |

## はじめに

<Tabs>
  <Tab title="Interactive">
    <Steps>
      <Step title="オンボーディングを実行する">
        ```bash
        openclaw onboard --auth-choice opencode-go
        ```
      </Step>
      <Step title="Go モデルをデフォルトとして設定する">
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

  <Tab title="Non-interactive">
    <Steps>
      <Step title="キーを直接渡す">
        ```bash
        openclaw onboard --opencode-go-api-key "$OPENCODE_API_KEY"
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
  env: { OPENCODE_API_KEY: "YOUR_API_KEY_HERE" }, // pragma: allowlist secret
  agents: { defaults: { model: { primary: "opencode-go/kimi-k2.5" } } },
}
```

## 高度な注意事項

<AccordionGroup>
  <Accordion title="ルーティングの挙動">
    model ref に `opencode-go/...` を使用すると、OpenClaw はモデルごとのルーティングを自動的に処理します。
    追加のプロバイダー設定は不要です。
  </Accordion>

  <Accordion title="実行時 ref の規約">
    実行時 ref は明示的なままです: Zen は `opencode/...`、Go は `opencode-go/...` です。
    これにより、両カタログにまたがって上流のモデルごとのルーティングが正しく保たれます。
  </Accordion>

  <Accordion title="共有認証情報">
    Zen カタログと Go カタログの両方で、同じ `OPENCODE_API_KEY` を使用します。セットアップ中に
    キーを入力すると、両方の実行時プロバイダーの認証情報が保存されます。
  </Accordion>
</AccordionGroup>

<Tip>
共有オンボーディングの概要と Zen + Go カタログの完全な
リファレンスについては、[OpenCode](/ja-JP/providers/opencode) を参照してください。
</Tip>

## 関連

<CardGroup cols={2}>
  <Card title="OpenCode（親）" href="/ja-JP/providers/opencode" icon="server">
    共有オンボーディング、カタログ概要、高度な注意事項。
  </Card>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
</CardGroup>
