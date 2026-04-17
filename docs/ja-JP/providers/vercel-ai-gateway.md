---
read_when:
    - OpenClaw で Vercel AI Gateway を使いたい場合
    - API キーの環境変数または CLI の認証選択肢が必要な場合
summary: Vercel AI Gateway のセットアップ（認証 + モデル選択）
title: Vercel AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:33:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 48c206a645d7a62e201a35ae94232323c8570fdae63129231c38d363ea78a60b
    source_path: providers/vercel-ai-gateway.md
    workflow: 15
---

# Vercel AI Gateway

[Vercel AI Gateway](https://vercel.com/ai-gateway) は、単一のエンドポイントを通じて数百のモデルにアクセスするための統一 API を提供します。

| 項目 | 値 |
| ------------- | -------------------------------- |
| Provider | `vercel-ai-gateway` |
| Auth | `AI_GATEWAY_API_KEY` |
| API | Anthropic Messages 互換 |
| モデルカタログ | `/v1/models` 経由で自動検出 |

<Tip>
OpenClaw は Gateway の `/v1/models` カタログを自動検出するため、
`/models vercel-ai-gateway` には
`vercel-ai-gateway/openai/gpt-5.4` のような現在のモデル参照が含まれます。
</Tip>

## はじめに

<Steps>
  <Step title="API キーを設定する">
    オンボーディングを実行し、AI Gateway の認証オプションを選択します。

    ```bash
    openclaw onboard --auth-choice ai-gateway-api-key
    ```

  </Step>
  <Step title="デフォルトモデルを設定する">
    モデルを OpenClaw 設定に追加します。

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "vercel-ai-gateway/anthropic/claude-opus-4.6" },
        },
      },
    }
    ```

  </Step>
  <Step title="モデルが利用可能であることを確認する">
    ```bash
    openclaw models list --provider vercel-ai-gateway
    ```
  </Step>
</Steps>

## 非対話の例

スクリプト化されたセットアップや CI セットアップでは、すべての値をコマンドラインで渡します。

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice ai-gateway-api-key \
  --ai-gateway-api-key "$AI_GATEWAY_API_KEY"
```

## モデル ID の短縮形

OpenClaw は Vercel Claude の短縮モデル参照を受け付け、ランタイム時に正規化します。

| 短縮入力 | 正規化されたモデル参照 |
| ----------------------------------- | --------------------------------------------- |
| `vercel-ai-gateway/claude-opus-4.6` | `vercel-ai-gateway/anthropic/claude-opus-4.6` |
| `vercel-ai-gateway/opus-4.6` | `vercel-ai-gateway/anthropic/claude-opus-4-6` |

<Tip>
設定では短縮形でも完全修飾のモデル参照でも使用できます。OpenClaw が自動的に正式な形式へ解決します。
</Tip>

## 高度な注意事項

<AccordionGroup>
  <Accordion title="デーモンプロセス用の環境変数">
    OpenClaw Gateway がデーモン（launchd/systemd）として実行される場合は、
    `AI_GATEWAY_API_KEY` がそのプロセスで利用可能であることを確認してください。

    <Warning>
    `~/.profile` にのみ設定されたキーは、その環境を明示的に取り込まない限り、
    launchd/systemd デーモンからは見えません。gateway プロセスが
    読み取れるように、キーは `~/.openclaw/.env` または `env.shellEnv` で設定してください。
    </Warning>

  </Accordion>

  <Accordion title="provider ルーティング">
    Vercel AI Gateway は、モデル参照プレフィックスに基づいてリクエストを上流 provider へルーティングします。たとえば、`vercel-ai-gateway/anthropic/claude-opus-4.6` は
    Anthropic 経由でルーティングされ、`vercel-ai-gateway/openai/gpt-5.4` は
    OpenAI 経由でルーティングされます。単一の `AI_GATEWAY_API_KEY` で、すべての
    上流 provider に対する認証を処理します。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、モデル参照、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Troubleshooting" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的なトラブルシューティングと FAQ。
  </Card>
</CardGroup>
