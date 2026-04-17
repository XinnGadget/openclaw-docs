---
read_when:
    - OpenClaw でオープンモデルを無料で使いたい
    - '`NVIDIA_API_KEY` のセットアップが必要です'
summary: OpenClaw で NVIDIA の OpenAI 互換 API を使う
title: NVIDIA
x-i18n:
    generated_at: "2026-04-12T23:32:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45048037365138141ee82cefa0c0daaf073a1c2ae3aa7b23815f6ca676fc0d3e
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA は `https://integrate.api.nvidia.com/v1` で OpenAI 互換 API を提供しており、
オープンモデルを無料で利用できます。認証には
[build.nvidia.com](https://build.nvidia.com/settings/api-keys) で取得した API キーを使用します。

## はじめに

<Steps>
  <Step title="API キーを取得する">
    API キーは [build.nvidia.com](https://build.nvidia.com/settings/api-keys) で作成します。
  </Step>
  <Step title="キーを export してオンボーディングを実行する">
    ```bash
    export NVIDIA_API_KEY="nvapi-..."
    openclaw onboard --auth-choice skip
    ```
  </Step>
  <Step title="NVIDIA モデルを設定する">
    ```bash
    openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
    ```
  </Step>
</Steps>

<Warning>
環境変数の代わりに `--token` を渡すと、その値がシェル履歴や
`ps` 出力に残ります。可能な限り `NVIDIA_API_KEY` 環境変数を使用してください。
</Warning>

## 設定例

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## 組み込みカタログ

| Model ref | Name | Context | Max output |
| ------------------------------------------ | ---------------------------- | ------- | ---------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192 |
| `nvidia/moonshotai/kimi-k2.5` | Kimi K2.5 | 262,144 | 8,192 |
| `nvidia/minimaxai/minimax-m2.5` | Minimax M2.5 | 196,608 | 8,192 |
| `nvidia/z-ai/glm5` | GLM 5 | 202,752 | 8,192 |

## 高度な注意事項

<AccordionGroup>
  <Accordion title="自動有効化の挙動">
    `NVIDIA_API_KEY` 環境変数が設定されると、このプロバイダーは自動的に有効になります。
    キー以外に明示的なプロバイダー設定は不要です。
  </Accordion>

  <Accordion title="カタログと価格">
    バンドルされたカタログは静的です。NVIDIA は
    現在、一覧のモデルに対して無料の API アクセスを提供しているため、ソース内ではコストのデフォルトは `0` です。
  </Accordion>

  <Accordion title="OpenAI 互換エンドポイント">
    NVIDIA は標準の `/v1` completions エンドポイントを使用します。OpenAI 互換の
    ツールであれば、NVIDIA の base URL を指定するだけでそのまま動作するはずです。
  </Accordion>
</AccordionGroup>

<Tip>
NVIDIA モデルは現在無料で利用できます。最新の提供状況と
レート制限の詳細については [build.nvidia.com](https://build.nvidia.com/) を確認してください。
</Tip>

## 関連

<CardGroup cols={2}>
  <Card title="モデル選択" href="/ja-JP/concepts/model-providers" icon="layers">
    プロバイダー、モデル ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="設定リファレンス" href="/ja-JP/gateway/configuration-reference" icon="gear">
    エージェント、モデル、プロバイダーの完全な設定リファレンス。
  </Card>
</CardGroup>
