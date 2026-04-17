---
read_when:
    - 你想用一个 API 密钥访问多个 LLM】【。
    - 你想在 OpenClaw 中通过 OpenRouter 运行模型】【。
summary: 使用 OpenRouter 的统一 API 在 OpenClaw 中访问多种模型
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T10:38:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter 提供了一个**统一 API**，可通过单个端点和 API 密钥将请求路由到多种模型。它兼容 OpenAI，因此大多数 OpenAI SDK 只需切换基础 URL 即可使用。

## 入门指南

<Steps>
  <Step title="获取你的 API 密钥">
    在 [openrouter.ai/keys](https://openrouter.ai/keys) 创建一个 API 密钥。
  </Step>
  <Step title="运行新手引导">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="（可选）切换到特定模型">
    新手引导默认使用 `openrouter/auto`。你稍后可以选择一个具体模型：

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## 配置示例

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## 模型引用

<Note>
模型引用遵循 `openrouter/<provider>/<model>` 模式。完整的可用提供商和模型列表，请参阅 [/concepts/model-providers](/zh-CN/concepts/model-providers)。
</Note>

## 身份验证和请求头

OpenRouter 在底层使用你的 API 密钥作为 Bearer token。

对于真实的 OpenRouter 请求（`https://openrouter.ai/api/v1`），OpenClaw 还会添加 OpenRouter 文档中说明的应用归因请求头：

| Header                    | Value                 |
| ------------------------- | --------------------- |
| `HTTP-Referer`            | `https://openclaw.ai` |
| `X-OpenRouter-Title`      | `OpenClaw`            |
| `X-OpenRouter-Categories` | `cli-agent`           |

<Warning>
如果你将 OpenRouter 提供商重新指向其他代理或基础 URL，OpenClaw **不会**注入这些 OpenRouter 特有的请求头或 Anthropic 缓存标记。
</Warning>

## 高级说明

<AccordionGroup>
  <Accordion title="Anthropic 缓存标记">
    在经过验证的 OpenRouter 路由上，Anthropic 模型引用会保留 OpenClaw 使用的 OpenRouter 特有 Anthropic `cache_control` 标记，以更好地复用系统 / 开发者提示块的提示缓存。
  </Accordion>

  <Accordion title="Thinking / 推理注入">
    在受支持的非 `auto` 路由上，OpenClaw 会将所选的 thinking 级别映射为 OpenRouter 代理推理负载。不受支持的模型提示和 `openrouter/auto` 会跳过该推理注入。
  </Accordion>

  <Accordion title="仅限 OpenAI 的请求塑形">
    OpenRouter 仍然通过代理式的 OpenAI 兼容路径运行，因此原生仅限 OpenAI 的请求塑形（如 `serviceTier`、Responses `store`、OpenAI 推理兼容负载和提示缓存提示）不会被转发。
  </Accordion>

  <Accordion title="Gemini 支持的路由">
    由 Gemini 支持的 OpenRouter 引用会保留在代理 Gemini 路径上：OpenClaw 会继续在那里进行 Gemini thought-signature 清理，但不会启用原生 Gemini 重放验证或引导重写。
  </Accordion>

  <Accordion title="提供商路由元数据">
    如果你在模型参数下传递 OpenRouter 提供商路由，OpenClaw 会在共享流包装器运行之前，将其作为 OpenRouter 路由元数据进行转发。
  </Accordion>
</AccordionGroup>

## 相关内容

<CardGroup cols={2}>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障转移行为。
  </Card>
  <Card title="配置参考" href="/zh-CN/gateway/configuration-reference" icon="gear">
    agents、模型和提供商的完整配置参考。
  </Card>
</CardGroup>
