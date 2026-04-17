---
read_when:
    - 你想在 OpenClaw 中免费使用开放模型
    - 你需要设置 `NVIDIA_API_KEY`
summary: 在 OpenClaw 中使用 NVIDIA 的 OpenAI 兼容 API
title: NVIDIA
x-i18n:
    generated_at: "2026-04-12T10:38:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45048037365138141ee82cefa0c0daaf073a1c2ae3aa7b23815f6ca676fc0d3e
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA 在 `https://integrate.api.nvidia.com/v1` 提供 OpenAI 兼容 API，可免费用于开放模型。请使用来自 [build.nvidia.com](https://build.nvidia.com/settings/api-keys) 的 API 密钥进行身份验证。

## 入门指南

<Steps>
  <Step title="获取你的 API 密钥">
    在 [build.nvidia.com](https://build.nvidia.com/settings/api-keys) 创建 API 密钥。
  </Step>
  <Step title="导出密钥并运行新手引导">
    ```bash
    export NVIDIA_API_KEY="nvapi-..."
    openclaw onboard --auth-choice skip
    ```
  </Step>
  <Step title="设置一个 NVIDIA 模型">
    ```bash
    openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
    ```
  </Step>
</Steps>

<Warning>
如果你传递 `--token` 而不是使用环境变量，该值会进入 shell 历史记录和 `ps` 输出。在可能的情况下，优先使用 `NVIDIA_API_KEY` 环境变量。
</Warning>

## 配置示例

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

## 内置目录

| Model ref                                  | 名称                         | 上下文 | 最大输出 |
| ------------------------------------------ | ---------------------------- | ------ | -------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144 | 8,192      |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144 | 8,192      |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608 | 8,192      |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752 | 8,192      |

## 高级说明

<AccordionGroup>
  <Accordion title="自动启用行为">
    当设置了 `NVIDIA_API_KEY` 环境变量时，提供商会自动启用。除该密钥外，不需要任何显式的提供商配置。
  </Accordion>

  <Accordion title="目录和定价">
    内置目录是静态的。由于 NVIDIA 当前为所列模型提供免费 API 访问，因此源码中的费用默认值为 `0`。
  </Accordion>

  <Accordion title="OpenAI 兼容端点">
    NVIDIA 使用标准的 `/v1` completions 端点。任何 OpenAI 兼容工具都应该可以直接配合 NVIDIA base URL 开箱即用。
  </Accordion>
</AccordionGroup>

<Tip>
NVIDIA 模型当前可免费使用。请查看 [build.nvidia.com](https://build.nvidia.com/) 以获取最新的可用性和速率限制详情。
</Tip>

## 相关内容

<CardGroup cols={2}>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障切换行为。
  </Card>
  <Card title="配置参考" href="/zh-CN/gateway/configuration-reference" icon="gear">
    agents、models 和 providers 的完整配置参考。
  </Card>
</CardGroup>
