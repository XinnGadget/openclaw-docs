---
read_when:
    - OpenClaw で Arcee AI を使用したい場合
    - API キーの env var または CLI の認証方法を選ぶ必要がある場合
summary: Arcee AI のセットアップ（認証 + モデル選択）
title: Arcee AI
x-i18n:
    generated_at: "2026-04-12T23:29:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68c5fddbe272c69611257ceff319c4de7ad21134aaf64582d60720a6f3b853cc
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) は、OpenAI 互換 API を通じて、mixture-of-experts モデルの Trinity ファミリーへのアクセスを提供します。すべての Trinity モデルは Apache 2.0 ライセンスです。

Arcee AI モデルには、Arcee プラットフォーム経由で直接アクセスすることも、[OpenRouter](/ja-JP/providers/openrouter) 経由でアクセスすることもできます。

| Property | Value                                                                                 |
| -------- | ------------------------------------------------------------------------------------- |
| Provider | `arcee`                                                                               |
| Auth     | `ARCEEAI_API_KEY`（直接）または `OPENROUTER_API_KEY`（OpenRouter 経由）               |
| API      | OpenAI 互換                                                                          |
| Base URL | `https://api.arcee.ai/api/v1`（直接）または `https://openrouter.ai/api/v1`（OpenRouter） |

## はじめに

<Tabs>
  <Tab title="Direct (Arcee platform)">
    <Steps>
      <Step title="Get an API key">
        [Arcee AI](https://chat.arcee.ai/) で API キーを作成します。
      </Step>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-api-key
        ```
      </Step>
      <Step title="Set a default model">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```
      </Step>
    </Steps>
  </Tab>

  <Tab title="Via OpenRouter">
    <Steps>
      <Step title="Get an API key">
        [OpenRouter](https://openrouter.ai/keys) で API キーを作成します。
      </Step>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice arceeai-openrouter
        ```
      </Step>
      <Step title="Set a default model">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "arcee/trinity-large-thinking" },
            },
          },
        }
        ```

        同じ model ref を、直接セットアップと OpenRouter セットアップの両方で使用できます（例: `arcee/trinity-large-thinking`）。
      </Step>
    </Steps>

  </Tab>
</Tabs>

## 非対話セットアップ

<Tabs>
  <Tab title="Direct (Arcee platform)">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-api-key \
      --arceeai-api-key "$ARCEEAI_API_KEY"
    ```
  </Tab>

  <Tab title="Via OpenRouter">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice arceeai-openrouter \
      --openrouter-api-key "$OPENROUTER_API_KEY"
    ```
  </Tab>
</Tabs>

## 組み込みカタログ

OpenClaw には現在、このバンドルされた Arcee カタログが含まれています:

| Model ref                      | Name                   | Input | Context | Cost (in/out per 1M) | Notes                                     |
| ------------------------------ | ---------------------- | ----- | ------- | -------------------- | ----------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K    | $0.25 / $0.90        | デフォルトモデル; reasoning 有効          |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K    | $0.25 / $1.00        | 汎用; 400B params, 13B active             |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K    | $0.045 / $0.15       | 高速かつコスト効率が高い; function calling |

<Tip>
オンボーディングプリセットでは、デフォルトモデルとして `arcee/trinity-large-thinking` が設定されます。
</Tip>

## サポートされている機能

| Feature                                       | Supported                    |
| --------------------------------------------- | ---------------------------- |
| Streaming                                     | はい                         |
| Tool use / function calling                   | はい                         |
| Structured output (JSON mode and JSON schema) | はい                         |
| Extended thinking                             | はい（Trinity Large Thinking） |

<AccordionGroup>
  <Accordion title="Environment note">
    Gateway が daemon（launchd/systemd）として実行される場合は、`ARCEEAI_API_KEY`
    （または `OPENROUTER_API_KEY`）がそのプロセスから利用可能であることを確認してください（たとえば
    `~/.openclaw/.env` または `env.shellEnv` 内）。
  </Accordion>

  <Accordion title="OpenRouter routing">
    OpenRouter 経由で Arcee モデルを使用する場合でも、同じ `arcee/*` model ref が適用されます。
    OpenClaw は、認証方法に基づいて透過的にルーティングを処理します。OpenRouter 固有の
    設定の詳細については、
    [OpenRouter provider docs](/ja-JP/providers/openrouter) を参照してください。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="OpenRouter" href="/ja-JP/providers/openrouter" icon="shuffle">
    1 つの API キーで Arcee モデルやその他多数のモデルにアクセスできます。
  </Card>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
</CardGroup>
