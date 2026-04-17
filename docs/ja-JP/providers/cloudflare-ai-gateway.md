---
read_when:
    - OpenClaw で Cloudflare AI Gateway を使用したい場合
    - アカウント ID、Gateway ID、または API キーの env var が必要な場合
summary: Cloudflare AI Gateway のセットアップ（認証 + モデル選択）
title: Cloudflare AI Gateway
x-i18n:
    generated_at: "2026-04-12T23:30:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 12e9589fe74e6a6335370b9cf2361a464876a392a33f8317d7fd30c3f163b2e5
    source_path: providers/cloudflare-ai-gateway.md
    workflow: 15
---

# Cloudflare AI Gateway

Cloudflare AI Gateway は provider API の前段に配置され、分析、キャッシュ、制御を追加できます。Anthropic については、OpenClaw は Gateway エンドポイントを通じて Anthropic Messages API を使用します。

| Property      | Value                                                                                    |
| ------------- | ---------------------------------------------------------------------------------------- |
| Provider      | `cloudflare-ai-gateway`                                                                  |
| Base URL      | `https://gateway.ai.cloudflare.com/v1/<account_id>/<gateway_id>/anthropic`              |
| Default model | `cloudflare-ai-gateway/claude-sonnet-4-5`                                                |
| API key       | `CLOUDFLARE_AI_GATEWAY_API_KEY`（Gateway 経由のリクエストに使う provider API キー）     |

<Note>
Cloudflare AI Gateway 経由でルーティングされる Anthropic モデルでは、provider キーとして **Anthropic API キー** を使用してください。
</Note>

## はじめに

<Steps>
  <Step title="Set the provider API key and Gateway details">
    オンボーディングを実行し、Cloudflare AI Gateway の認証オプションを選択します:

    ```bash
    openclaw onboard --auth-choice cloudflare-ai-gateway-api-key
    ```

    これにより、アカウント ID、gateway ID、API キーの入力を求められます。

  </Step>
  <Step title="Set a default model">
    OpenClaw の設定にモデルを追加します:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "cloudflare-ai-gateway/claude-sonnet-4-5" },
        },
      },
    }
    ```

  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider cloudflare-ai-gateway
    ```
  </Step>
</Steps>

## 非対話の例

スクリプト化されたセットアップや CI セットアップでは、すべての値をコマンドラインで渡します:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice cloudflare-ai-gateway-api-key \
  --cloudflare-ai-gateway-account-id "your-account-id" \
  --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
  --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY"
```

## 詳細設定

<AccordionGroup>
  <Accordion title="Authenticated gateways">
    Cloudflare で Gateway 認証を有効にしている場合は、`cf-aig-authorization` ヘッダーを追加してください。これは provider API キーに**加えて**必要です。

    ```json5
    {
      models: {
        providers: {
          "cloudflare-ai-gateway": {
            headers: {
              "cf-aig-authorization": "Bearer <cloudflare-ai-gateway-token>",
            },
          },
        },
      },
    }
    ```

    <Tip>
    `cf-aig-authorization` ヘッダーは Cloudflare Gateway 自体を認証し、provider API キー（たとえば Anthropic キー）は上流 provider を認証します。
    </Tip>

  </Accordion>

  <Accordion title="Environment note">
    Gateway が daemon（launchd/systemd）として実行される場合は、`CLOUDFLARE_AI_GATEWAY_API_KEY` がそのプロセスから利用可能であることを確認してください。

    <Warning>
    `~/.profile` にだけ置かれたキーは、その環境がそこにも取り込まれていない限り、launchd/systemd daemon には役立ちません。gateway プロセスが読み取れるように、キーを `~/.openclaw/.env` または `env.shellEnv` で設定してください。
    </Warning>

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
  <Card title="Troubleshooting" href="/ja-JP/help/troubleshooting" icon="wrench">
    一般的なトラブルシューティングと FAQ。
  </Card>
</CardGroup>
