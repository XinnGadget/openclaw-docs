---
read_when:
    - OpenClaw で Fireworks を使用したい場合
    - Fireworks API キーの env var またはデフォルト model ID が必要な場合
summary: Fireworks のセットアップ（認証 + モデル選択）
title: Fireworks
x-i18n:
    generated_at: "2026-04-12T23:31:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1a85d9507c19e275fdd846a303d844eda8045d008774d4dde1eae408e8716b6f
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

[Fireworks](https://fireworks.ai) は、OpenAI 互換 API を通じて open-weight モデルおよびルーティングされたモデルを提供します。OpenClaw には、バンドルされた Fireworks provider Plugin が含まれています。

| Property      | Value                                                  |
| ------------- | ------------------------------------------------------ |
| Provider      | `fireworks`                                            |
| Auth          | `FIREWORKS_API_KEY`                                    |
| API           | OpenAI 互換 chat/completions                           |
| Base URL      | `https://api.fireworks.ai/inference/v1`                |
| Default model | `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` |

## はじめに

<Steps>
  <Step title="Set up Fireworks auth through onboarding">
    ```bash
    openclaw onboard --auth-choice fireworks-api-key
    ```

    これにより Fireworks キーが OpenClaw 設定に保存され、Fire Pass の starter model がデフォルトとして設定されます。

  </Step>
  <Step title="Verify the model is available">
    ```bash
    openclaw models list --provider fireworks
    ```
  </Step>
</Steps>

## 非対話の例

スクリプト化されたセットアップや CI セットアップでは、すべての値をコマンドラインで渡します:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## 組み込みカタログ

| Model ref                                              | Name                        | Input      | Context | Max output | Notes                                        |
| ------------------------------------------------------ | --------------------------- | ---------- | ------- | ---------- | -------------------------------------------- |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | text,image | 256,000 | 256,000    | Fireworks 上のデフォルトのバンドル済み starter model |

<Tip>
Fireworks が新しい Qwen や Gemma のリリースのような新しいモデルを公開した場合は、バンドル済みカタログの更新を待たずに、その Fireworks model ID を使って直接切り替えられます。
</Tip>

## カスタム Fireworks model ID

OpenClaw は動的な Fireworks model ID も受け付けます。Fireworks に表示される正確な model ID または router ID を使い、先頭に `fireworks/` を付けてください。

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="How model id prefixing works">
    OpenClaw のすべての Fireworks model ref は、`fireworks/` に続けて Fireworks プラットフォーム上の正確な ID または router path を付けた形になります。例:

    - Router model: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`
    - Direct model: `fireworks/accounts/fireworks/models/<model-name>`

    OpenClaw は API リクエストの構築時に `fireworks/` プレフィックスを取り除き、残りの path を Fireworks エンドポイントに送信します。

  </Accordion>

  <Accordion title="Environment note">
    Gateway が対話シェルの外で実行される場合は、`FIREWORKS_API_KEY` がそのプロセスでも利用可能であることを確認してください。

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
