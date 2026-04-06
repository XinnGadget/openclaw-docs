---
read_when:
    - 你想在 OpenClaw 中使用 Arcee AI
    - 你需要 API 密钥环境变量或 CLI 认证选择
summary: Arcee AI 设置（认证 + 模型选择）
title: Arcee AI
x-i18n:
    generated_at: "2026-04-06T18:54:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: fb04909a708fec08dd2c8c863501b178f098bc4818eaebad38aea264157969d8
    source_path: providers/arcee.md
    workflow: 15
---

# Arcee AI

[Arcee AI](https://arcee.ai) 通过兼容 OpenAI 的 API 提供 Trinity 系列混合专家模型的访问。所有 Trinity 模型均采用 Apache 2.0 许可证。

Arcee AI 模型可以通过 Arcee 平台直接访问，也可以通过 [OpenRouter](/zh-CN/providers/openrouter) 访问。

- 提供商：`arcee`
- 认证：`ARCEEAI_API_KEY`（直连）或 `OPENROUTER_API_KEY`（通过 OpenRouter）
- API：兼容 OpenAI
- Base URL：`https://api.arcee.ai/api/v1`（直连）或 `https://openrouter.ai/api/v1`（OpenRouter）

## 快速开始

1. 从 [Arcee AI](https://chat.arcee.ai/) 或 [OpenRouter](https://openrouter.ai/keys) 获取一个 API 密钥。

2. 设置 API 密钥（推荐：将其存储给 Gateway 网关使用）：

```bash
# Direct (Arcee platform)
openclaw onboard --auth-choice arceeai-api-key

# Via OpenRouter
openclaw onboard --auth-choice arceeai-openrouter
```

3. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "arcee/trinity-large-thinking" },
    },
  },
}
```

## 非交互式示例

```bash
# Direct (Arcee platform)
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-api-key \
  --arceeai-api-key "$ARCEEAI_API_KEY"

# Via OpenRouter
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice arceeai-openrouter \
  --openrouter-api-key "$OPENROUTER_API_KEY"
```

## 环境说明

如果 Gateway 网关以守护进程形式运行（launchd/systemd），请确保 `ARCEEAI_API_KEY`
（或 `OPENROUTER_API_KEY`）可供该进程使用（例如在
`~/.openclaw/.env` 中，或通过 `env.shellEnv`）。

## 内置目录

OpenClaw 当前内置了以下 Arcee 目录：

| Model ref                      | Name                   | Input | Context | Cost (in/out per 1M) | Notes                                  |
| ------------------------------ | ---------------------- | ----- | ------- | -------------------- | -------------------------------------- |
| `arcee/trinity-large-thinking` | Trinity Large Thinking | text  | 256K    | $0.25 / $0.90        | 默认模型；已启用推理                   |
| `arcee/trinity-large-preview`  | Trinity Large Preview  | text  | 128K    | $0.25 / $1.00        | 通用模型；400B 参数，13B 活跃参数      |
| `arcee/trinity-mini`           | Trinity Mini 26B       | text  | 128K    | $0.045 / $0.15       | 快速且具成本效益；支持 function calling |

相同的模型引用可同时用于直连和 OpenRouter 设置（例如 `arcee/trinity-large-thinking`）。

新手引导预设会将 `arcee/trinity-large-thinking` 设置为默认模型。

## 支持的功能

- 流式传输
- 工具使用 / function calling
- 结构化输出（JSON 模式和 JSON schema）
- 扩展思考（Trinity Large Thinking）
