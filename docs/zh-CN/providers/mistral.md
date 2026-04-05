---
read_when:
    - 你想在 OpenClaw 中使用 Mistral 模型
    - 你需要 Mistral API 密钥新手引导和模型引用
summary: 在 OpenClaw 中使用 Mistral 模型和 Voxtral 转录
title: Mistral
x-i18n:
    generated_at: "2026-04-05T08:42:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8f61b9e0656dd7e0243861ddf14b1b41a07c38bff27cef9ad0815d14c8e34408
    source_path: providers/mistral.md
    workflow: 15
---

# Mistral

OpenClaw 支持将 Mistral 用于文本/图像模型路由（`mistral/...`）以及通过媒体理解中的 Voxtral 进行音频转录。
Mistral 也可用于记忆嵌入（`memorySearch.provider = "mistral"`）。

## CLI 设置

```bash
openclaw onboard --auth-choice mistral-api-key
# 或非交互式
openclaw onboard --mistral-api-key "$MISTRAL_API_KEY"
```

## 配置片段（LLM 提供商）

```json5
{
  env: { MISTRAL_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "mistral/mistral-large-latest" } } },
}
```

## 内置 LLM 目录

OpenClaw 当前内置了以下 Mistral 目录：

| 模型引用 | 输入 | 上下文 | 最大输出 | 说明 |
| -------------------------------- | ----------- | ------- | ---------- | ------------------------ |
| `mistral/mistral-large-latest`   | text, image | 262,144 | 16,384     | 默认模型 |
| `mistral/mistral-medium-2508`    | text, image | 262,144 | 8,192      | Mistral Medium 3.1 |
| `mistral/mistral-small-latest`   | text, image | 128,000 | 16,384     | 更小的多模态模型 |
| `mistral/pixtral-large-latest`   | text, image | 128,000 | 32,768     | Pixtral |
| `mistral/codestral-latest`       | text        | 256,000 | 4,096      | 编码 |
| `mistral/devstral-medium-latest` | text        | 262,144 | 32,768     | Devstral 2 |
| `mistral/magistral-small`        | text        | 128,000 | 40,000     | 支持推理 |

## 配置片段（使用 Voxtral 进行音频转录）

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [{ provider: "mistral", model: "voxtral-mini-latest" }],
      },
    },
  },
}
```

## 说明

- Mistral 身份验证使用 `MISTRAL_API_KEY`。
- 提供商基础 URL 默认为 `https://api.mistral.ai/v1`。
- 新手引导默认模型为 `mistral/mistral-large-latest`。
- Mistral 的媒体理解默认音频模型为 `voxtral-mini-latest`。
- 媒体转录路径使用 `/v1/audio/transcriptions`。
- 记忆嵌入路径使用 `/v1/embeddings`（默认模型：`mistral-embed`）。
