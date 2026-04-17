---
read_when:
    - 你想在 OpenClaw 中使用 DeepSeek
    - 你需要 API 密钥环境变量或 CLI 身份验证选项
summary: DeepSeek 设置（身份验证 + 模型选择）
title: DeepSeek
x-i18n:
    generated_at: "2026-04-12T10:43:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad06880bd1ab89f72f9e31f4927e2c099dcf6b4e0ff2b3fcc91a24468fbc089d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) 通过与 OpenAI 兼容的 API 提供强大的 AI 模型。

| 属性 | 值 |
| -------- | -------------------------- |
| 提供商 | `deepseek` |
| 身份验证 | `DEEPSEEK_API_KEY` |
| API | 与 OpenAI 兼容 |
| Base URL | `https://api.deepseek.com` |

## 入门指南

<Steps>
  <Step title="获取你的 API 密钥">
    在 [platform.deepseek.com](https://platform.deepseek.com/api_keys) 创建一个 API 密钥。
  </Step>
  <Step title="运行新手引导">
    ```bash
    openclaw onboard --auth-choice deepseek-api-key
    ```

    这会提示你输入 API 密钥，并将 `deepseek/deepseek-chat` 设为默认模型。

  </Step>
  <Step title="验证模型可用">
    ```bash
    openclaw models list --provider deepseek
    ```
  </Step>
</Steps>

<AccordionGroup>
  <Accordion title="非交互式设置">
    对于脚本化或无头安装，请直接传递所有标志：

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
如果 Gateway 网关 以守护进程（launchd/systemd）方式运行，请确保 `DEEPSEEK_API_KEY`
可供该进程使用（例如，在 `~/.openclaw/.env` 中，或通过
`env.shellEnv`）。
</Warning>

## 内置目录

| 模型引用 | 名称 | 输入 | 上下文 | 最大输出 | 说明 |
| ---------------------------- | ----------------- | ----- | ------- | ---------- | ------------------------------------------------- |
| `deepseek/deepseek-chat` | DeepSeek Chat | text | 131,072 | 8,192 | 默认模型；DeepSeek V3.2 非思考表面 |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | text | 131,072 | 65,536 | 启用推理的 V3.2 表面 |

<Tip>
源码中当前将这两个内置模型都声明为兼容流式传输用法。
</Tip>

## 配置示例

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

## 相关内容

<CardGroup cols={2}>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障转移行为。
  </Card>
  <Card title="配置参考" href="/zh-CN/gateway/configuration-reference" icon="gear">
    agents、模型和提供商的完整配置参考。
  </Card>
</CardGroup>
