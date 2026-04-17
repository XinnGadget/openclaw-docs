---
read_when:
    - OpenClaw で Z.AI / GLM モデルを使用したい場合
    - 簡単な `ZAI_API_KEY` セットアップが必要な場合
summary: OpenClaw で Z.AI（GLM モデル）を使用する
title: Z.AI
x-i18n:
    generated_at: "2026-04-12T23:34:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 972b467dab141c8c5126ac776b7cb6b21815c27da511b3f34e12bd9e9ac953b7
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI は **GLM** モデル向けの API プラットフォームです。GLM 用の REST API を提供し、
認証には API キーを使用します。API キーは Z.AI コンソールで作成してください。OpenClaw は
`zai` provider を Z.AI API キーとともに使用します。

- Provider: `zai`
- Auth: `ZAI_API_KEY`
- API: Z.AI Chat Completions（Bearer 認証）

## はじめに

<Tabs>
  <Tab title="Auto-detect endpoint">
    **最適な用途:** ほとんどのユーザー。OpenClaw はキーから一致する Z.AI エンドポイントを検出し、正しい base URL を自動で適用します。

    <Steps>
      <Step title="Run onboarding">
        ```bash
        openclaw onboard --auth-choice zai-api-key
        ```
      </Step>
      <Step title="Set a default model">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Explicit regional endpoint">
    **最適な用途:** 特定の Coding Plan または一般 API サーフェスを強制したいユーザー。

    <Steps>
      <Step title="Pick the right onboarding choice">
        ```bash
        # Coding Plan Global（Coding Plan ユーザー向け推奨）
        openclaw onboard --auth-choice zai-coding-global

        # Coding Plan CN（中国リージョン）
        openclaw onboard --auth-choice zai-coding-cn

        # General API
        openclaw onboard --auth-choice zai-global

        # General API CN（中国リージョン）
        openclaw onboard --auth-choice zai-cn
        ```
      </Step>
      <Step title="Set a default model">
        ```json5
        {
          env: { ZAI_API_KEY: "sk-..." },
          agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
        }
        ```
      </Step>
      <Step title="Verify the model is available">
        ```bash
        openclaw models list --provider zai
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## バンドル済み GLM カタログ

OpenClaw は現在、バンドルされた `zai` provider に次を初期登録しています:

| Model ref            | Notes         |
| -------------------- | ------------- |
| `zai/glm-5.1`        | デフォルトモデル |
| `zai/glm-5`          |               |
| `zai/glm-5-turbo`    |               |
| `zai/glm-5v-turbo`   |               |
| `zai/glm-4.7`        |               |
| `zai/glm-4.7-flash`  |               |
| `zai/glm-4.7-flashx` |               |
| `zai/glm-4.6`        |               |
| `zai/glm-4.6v`       |               |
| `zai/glm-4.5`        |               |
| `zai/glm-4.5-air`    |               |
| `zai/glm-4.5-flash`  |               |
| `zai/glm-4.5v`       |               |

<Tip>
GLM モデルは `zai/<model>` の形式で利用できます（例: `zai/glm-5`）。デフォルトのバンドル済み model ref は `zai/glm-5.1` です。
</Tip>

## 詳細設定

<AccordionGroup>
  <Accordion title="Forward-resolving unknown GLM-5 models">
    未知の `glm-5*` ID でも、現在の GLM-5 ファミリー形状に一致する場合は、
    `glm-4.7` テンプレートから provider 所有の metadata を合成することで、
    バンドル済み provider パス上で forward-resolve されます。
  </Accordion>

  <Accordion title="Tool-call streaming">
    Z.AI の tool-call streaming では、`tool_stream` がデフォルトで有効です。無効にするには:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "zai/<model>": {
              params: { tool_stream: false },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Image understanding">
    バンドルされた Z.AI Plugin は image understanding を登録します。

    | Property      | Value       |
    | ------------- | ----------- |
    | Model         | `glm-4.6v`  |

    image understanding は設定済みの Z.AI 認証から自動解決されるため、
    追加設定は不要です。

  </Accordion>

  <Accordion title="Auth details">
    - Z.AI は API キーによる Bearer 認証を使用します。
    - `zai-api-key` のオンボーディング選択では、キーのプレフィックスから一致する Z.AI エンドポイントを自動検出します。
    - 特定の API サーフェスを強制したい場合は、明示的なリージョン選択（`zai-coding-global`、`zai-coding-cn`、`zai-global`、`zai-cn`）を使用してください。
  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="GLM model family" href="/ja-JP/providers/glm" icon="microchip">
    GLM の model family 概要。
  </Card>
  <Card title="Model selection" href="/ja-JP/concepts/model-providers" icon="layers">
    provider、model ref、フェイルオーバー動作の選び方。
  </Card>
</CardGroup>
