---
read_when:
    - model provider として Synthetic を使用したい場合
    - Synthetic API キーまたは base URL の設定が必要な場合
summary: OpenClaw で Synthetic の Anthropic 互換 API を使用する
title: Synthetic
x-i18n:
    generated_at: "2026-04-12T23:33:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1c4d2c6635482e09acaf603a75c8a85f0782e42a4a68ef6166f423a48d184ffa
    source_path: providers/synthetic.md
    workflow: 15
---

# Synthetic

[Synthetic](https://synthetic.new) は Anthropic 互換エンドポイントを提供します。
OpenClaw はこれを `synthetic` provider として登録し、Anthropic
Messages API を使用します。

| Property | Value                                 |
| -------- | ------------------------------------- |
| Provider | `synthetic`                           |
| Auth     | `SYNTHETIC_API_KEY`                   |
| API      | Anthropic Messages                    |
| Base URL | `https://api.synthetic.new/anthropic` |

## はじめに

<Steps>
  <Step title="Get an API key">
    Synthetic アカウントから `SYNTHETIC_API_KEY` を取得するか、
    オンボーディングウィザードで入力してください。
  </Step>
  <Step title="Run onboarding">
    ```bash
    openclaw onboard --auth-choice synthetic-api-key
    ```
  </Step>
  <Step title="Verify the default model">
    オンボーディング後、デフォルトモデルは次のように設定されます:
    ```
    synthetic/hf:MiniMaxAI/MiniMax-M2.5
    ```
  </Step>
</Steps>

<Warning>
OpenClaw の Anthropic client は base URL に自動で `/v1` を追加するため、
`https://api.synthetic.new/anthropic` を使用してください（`/anthropic/v1` ではありません）。Synthetic
が base URL を変更した場合は、`models.providers.synthetic.baseUrl` を上書きしてください。
</Warning>

## 設定例

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## モデルカタログ

すべての Synthetic モデルは cost `0`（input/output/cache）を使用します。

| Model ID                                               | Context window | Max tokens | Reasoning | Input        |
| ------------------------------------------------------ | -------------- | ---------- | --------- | ------------ |
| `hf:MiniMaxAI/MiniMax-M2.5`                            | 192,000        | 65,536     | no        | text         |
| `hf:moonshotai/Kimi-K2-Thinking`                       | 256,000        | 8,192      | yes       | text         |
| `hf:zai-org/GLM-4.7`                                   | 198,000        | 128,000    | no        | text         |
| `hf:deepseek-ai/DeepSeek-R1-0528`                      | 128,000        | 8,192      | no        | text         |
| `hf:deepseek-ai/DeepSeek-V3-0324`                      | 128,000        | 8,192      | no        | text         |
| `hf:deepseek-ai/DeepSeek-V3.1`                         | 128,000        | 8,192      | no        | text         |
| `hf:deepseek-ai/DeepSeek-V3.1-Terminus`                | 128,000        | 8,192      | no        | text         |
| `hf:deepseek-ai/DeepSeek-V3.2`                         | 159,000        | 8,192      | no        | text         |
| `hf:meta-llama/Llama-3.3-70B-Instruct`                 | 128,000        | 8,192      | no        | text         |
| `hf:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 524,000        | 8,192      | no        | text         |
| `hf:moonshotai/Kimi-K2-Instruct-0905`                  | 256,000        | 8,192      | no        | text         |
| `hf:moonshotai/Kimi-K2.5`                              | 256,000        | 8,192      | yes       | text + image |
| `hf:openai/gpt-oss-120b`                               | 128,000        | 8,192      | no        | text         |
| `hf:Qwen/Qwen3-235B-A22B-Instruct-2507`                | 256,000        | 8,192      | no        | text         |
| `hf:Qwen/Qwen3-Coder-480B-A35B-Instruct`               | 256,000        | 8,192      | no        | text         |
| `hf:Qwen/Qwen3-VL-235B-A22B-Instruct`                  | 250,000        | 8,192      | no        | text + image |
| `hf:zai-org/GLM-4.5`                                   | 128,000        | 128,000    | no        | text         |
| `hf:zai-org/GLM-4.6`                                   | 198,000        | 128,000    | no        | text         |
| `hf:zai-org/GLM-5`                                     | 256,000        | 128,000    | yes       | text + image |
| `hf:deepseek-ai/DeepSeek-V3`                           | 128,000        | 8,192      | no        | text         |
| `hf:Qwen/Qwen3-235B-A22B-Thinking-2507`                | 256,000        | 8,192      | yes       | text         |

<Tip>
model ref は `synthetic/<modelId>` の形式を使用します。アカウントで利用可能なすべてのモデルを確認するには、
`openclaw models list --provider synthetic` を使用してください。
</Tip>

<AccordionGroup>
  <Accordion title="Model allowlist">
    model allowlist（`agents.defaults.models`）を有効にする場合は、
    使用予定の Synthetic モデルをすべて追加してください。allowlist にないモデルは agent から見えなくなります。
  </Accordion>

  <Accordion title="Base URL override">
    Synthetic が API エンドポイントを変更した場合は、config で base URL を上書きしてください:

    ```json5
    {
      models: {
        providers: {
          synthetic: {
            baseUrl: "https://new-api.synthetic.new/anthropic",
          },
        },
      },
    }
    ```

    OpenClaw が自動で `/v1` を追加することを忘れないでください。

  </Accordion>
</AccordionGroup>

## 関連

<CardGroup cols={2}>
  <Card title="Model providers" href="/ja-JP/concepts/model-providers" icon="layers">
    provider ルール、model ref、フェイルオーバー動作。
  </Card>
  <Card title="Configuration reference" href="/ja-JP/gateway/configuration-reference" icon="gear">
    provider 設定を含む完全な config schema。
  </Card>
  <Card title="Synthetic" href="https://synthetic.new" icon="arrow-up-right-from-square">
    Synthetic ダッシュボードと API ドキュメント。
  </Card>
</CardGroup>
