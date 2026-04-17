---
read_when:
    - 你想用一个 API 密钥访问多个 LLM
    - 你想在 OpenClaw 中通过 Kilo Gateway 运行模型
summary: 使用 Kilo Gateway 的统一 API 在 OpenClaw 中访问多种模型
title: Kilocode
x-i18n:
    generated_at: "2026-04-12T10:43:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32946f2187f3933115341cbe81006718b10583abc4deea7440b5e56366025f4a
    source_path: providers/kilocode.md
    workflow: 15
---

# Kilo Gateway

Kilo Gateway 提供一个**统一 API**，可将请求路由到单个端点和 API 密钥背后的多种模型。它兼容 OpenAI，因此大多数 OpenAI SDK 只需切换 base URL 即可使用。

| Property | Value |
| -------- | ----- |
| 提供商 | `kilocode` |
| 认证 | `KILOCODE_API_KEY` |
| API | 兼容 OpenAI |
| Base URL | `https://api.kilo.ai/api/gateway/` |

## 入门指南

<Steps>
  <Step title="创建账户">
    前往 [app.kilo.ai](https://app.kilo.ai)，登录或创建账户，然后导航到 API Keys 并生成一个新密钥。
  </Step>
  <Step title="运行新手引导">
    ```bash
    openclaw onboard --auth-choice kilocode-api-key
    ```

    或直接设置环境变量：

    ```bash
    export KILOCODE_API_KEY="<your-kilocode-api-key>" # pragma: allowlist secret
    ```

  </Step>
  <Step title="验证模型是否可用">
    ```bash
    openclaw models list --provider kilocode
    ```
  </Step>
</Steps>

## 默认模型

默认模型是 `kilocode/kilo/auto`，这是一个由 Kilo Gateway 管理、由提供商拥有的智能路由模型。

<Note>
OpenClaw 将 `kilocode/kilo/auto` 视为稳定的默认引用，但不会发布该路由从任务到上游模型映射的源码依据。`kilocode/kilo/auto` 背后的确切上游路由由 Kilo Gateway 决定，而不是在 OpenClaw 中硬编码。
</Note>

## 可用模型

OpenClaw 会在启动时从 Kilo Gateway 动态发现可用模型。使用
`/models kilocode` 可查看你的账户可用的完整模型列表。

Gateway 网关上任何可用模型都可以配合 `kilocode/` 前缀使用：

| 模型引用 | 说明 |
| -------- | ---- |
| `kilocode/kilo/auto` | 默认 —— 智能路由 |
| `kilocode/anthropic/claude-sonnet-4` | 通过 Kilo 使用 Anthropic |
| `kilocode/openai/gpt-5.4` | 通过 Kilo 使用 OpenAI |
| `kilocode/google/gemini-3-pro-preview` | 通过 Kilo 使用 Google |
| ...以及更多 | 使用 `/models kilocode` 列出全部 |

<Tip>
启动时，OpenClaw 会查询 `GET https://api.kilo.ai/api/gateway/models`，并将发现的模型合并到静态后备目录之前。内置后备目录始终包含 `kilocode/kilo/auto`（`Kilo Auto`），其参数为 `input: ["text", "image"]`、`reasoning: true`、`contextWindow: 1000000` 和 `maxTokens: 128000`。
</Tip>

## 配置示例

```json5
{
  env: { KILOCODE_API_KEY: "<your-kilocode-api-key>" }, // pragma: allowlist secret
  agents: {
    defaults: {
      model: { primary: "kilocode/kilo/auto" },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="传输与兼容性">
    源码中将 Kilo Gateway 记录为兼容 OpenRouter，因此它会保留在代理风格的 OpenAI 兼容路径上，而不是使用原生 OpenAI 请求整形。

    - 由 Gemini 支持的 Kilo 引用会保留在 proxy-Gemini 路径上，因此 OpenClaw 会继续在该路径执行 Gemini thought-signature 清理，而不会启用原生 Gemini 重放校验或 bootstrap 重写。
    - Kilo Gateway 在底层使用带有你的 API 密钥的 Bearer token。

  </Accordion>

  <Accordion title="流包装器与推理">
    Kilo 的共享流包装器会添加 provider app header，并为受支持的具体模型引用规范化代理推理负载。

    <Warning>
    `kilocode/kilo/auto` 和其他不支持代理推理的提示会跳过推理注入。如果你需要推理支持，请使用具体的模型引用，例如 `kilocode/anthropic/claude-sonnet-4`。
    </Warning>

  </Accordion>

  <Accordion title="故障排除">
    - 如果模型发现过程在启动时失败，OpenClaw 会回退到包含 `kilocode/kilo/auto` 的内置静态目录。
    - 确认你的 API 密钥有效，并且你的 Kilo 账户已启用所需模型。
    - 当 Gateway 网关以守护进程方式运行时，确保 `KILOCODE_API_KEY` 对该进程可用（例如放在 `~/.openclaw/.env` 中，或通过 `env.shellEnv` 提供）。
  </Accordion>
</AccordionGroup>

## 相关内容

<CardGroup cols={2}>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障转移行为。
  </Card>
  <Card title="配置参考" href="/zh-CN/gateway/configuration" icon="gear">
    完整的 OpenClaw 配置参考。
  </Card>
  <Card title="Kilo Gateway" href="https://app.kilo.ai" icon="arrow-up-right-from-square">
    Kilo Gateway 仪表板、API 密钥和账户管理。
  </Card>
</CardGroup>
