---
read_when:
    - 你想在 OpenClaw 中使用 DeepSeek
    - 你需要 API 密钥环境变量或 CLI 认证选项
summary: DeepSeek 设置（认证 + 模型选择）
x-i18n:
    generated_at: "2026-04-12T10:38:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8b439c4b4cf5445db891b81d03e99f6aef5be64623e79e818763de43a2823d6d
    source_path: providers/deepseek.md
    workflow: 15
---

# DeepSeek

[DeepSeek](https://www.deepseek.com) 通过兼容 OpenAI 的 API 提供强大的 AI 模型。

| Property | Value                      |
| -------- | -------------------------- |
| 提供商 | `deepseek`                 |
| 认证     | `DEEPSEEK_API_KEY`         |
| API      | 兼容 OpenAI          |
| Base URL | `https://api.deepseek.com` |

## 入门指南

<Steps>
  <Step title="获取你的 API 密钥">
    在 [platform.deepseek.com](https://platform.deepseek.com/api_keys) 创建 API 密钥。
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
    对于脚本化或无头安装，直接传入所有标志：

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
如果 Gateway 网关 以守护进程方式运行（launchd/systemd），请确保 `DEEPSEEK_API_KEY`
对该进程可用（例如，在 `~/.openclaw/.env` 中或通过
`env.shellEnv`）。
</Warning>

## 内置目录

| Model ref                    | Name              | Input | Context | Max output | Notes                                             |
| ---------------------------- | ----------------- | ----- | ------- | ---------- | ------------------------------------------------- |
| `deepseek/deepseek-chat`     | DeepSeek Chat     | 文本  | 131,072 | 8,192      | 默认模型；DeepSeek V3.2 非思考表层 |
| `deepseek/deepseek-reasoner` | DeepSeek Reasoner | 文本  | 131,072 | 65,536     | 启用推理的 V3.2 表层                    |

<Tip>
源码中，这两个内置模型目前都声明支持流式传输用法兼容性。
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
