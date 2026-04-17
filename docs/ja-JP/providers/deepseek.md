---
read_when:
    - OpenClaw で DeepSeek を使いたい場合
    - API キーの環境変数または CLI の認証選択肢が必要な場合
summary: DeepSeek のセットアップ（認証 + モデル選択）
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T23:30:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) は、OpenAI 互換 API を備えた高性能な AI モデルを提供します。

| 項目 | 値 |
| -------- | -------------------------- |
| Provider | `deepseek` |
| Auth | `DEEPSEEK_API_KEY` |
| API | OpenAI 互換 |
| Base URL | `https://api.deepseek.com` |

## はじめに

<Steps>
  <Step title="API キーを取得する">
    [platform.deepseek.com](https://platform.deepseek.com/api_keys) で API キーを作成します。
  </Step>
  <Step title="オンボーディングを実行する">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    これにより API キーの入力が求められ、デフォルトモデルとして `deepseek/deepseek-chat` が設定されます。

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="非対話セットアップ">
    スクリプト化されたインストールやヘッドレスインストールでは、すべてのフラグを直接渡します。

    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice deepseek-api-key \
      --deepseek-api-key "$DEEPSEEK_API_KEY" \
      --skip-health \
      --accept-risk
    ```

  </Accordion>
</AccordionGroup>

<Warning>
Gateway がデーモン（launchd/systemd）として実行される場合は、`DEEPSEEK_API_KEY` がそのプロセスで利用可能であることを確認してください（たとえば `~/.openclaw/.env` または `env.shellEnv` 経由）。
</Warning>

## 組み込みカタログ

| モデル参照 | 名前 | 入力 | コンテキスト | 最大出力 | 注記 |
| ---------------------------- | ----------------- | ----- | ------- | ---------- | ------------------------------------------------- |
| `deepseek/deepseek-chat` | DeepSeek Chat | text | 131,072 | 8,192 | デフォルトモデル。DeepSeek V3.2 の非 thinking サーフェス |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text | 131,072 | 65,536 | 推論対応の V3.2 サーフェス |

<Tip>
現在、バンドルされている両モデルはソース上でストリーミング利用互換として公開されています。
</Tip>

## 設定例

```json5
{
  env: { DEEPSEEK_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "deepseek/deepseek-chat" },
    },
  },
}
```

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Configuration reference" href="/ja-JP/gateway/configuration-reference" icon="gear">
    エージェント、モデル、provider の完全な設定リファレンス。
  </Card>
</CardGroup>
