---
read_when:
    - 你想在 OpenClaw 中使用 NVIDIA 模型
    - 你需要设置 `NVIDIA_API_KEY`
summary: 在 OpenClaw 中使用 NVIDIA 的 OpenAI 兼容 API
title: NVIDIA
x-i18n:
    generated_at: "2026-04-05T08:42:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: a24c5e46c0cf0fbc63bf09c772b486dd7f8f4b52e687d3b835bb54a1176b28da
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA 在 `https://integrate.api.nvidia.com/v1` 提供适用于 Nemotron 和 NeMo 模型的 OpenAI 兼容 API。请使用来自 [NVIDIA NGC](https://catalog.ngc.nvidia.com/) 的 API 密钥进行身份验证。

## CLI 设置

先导出密钥，然后运行新手引导并设置一个 NVIDIA 模型：

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/llama-3.1-nemotron-70b-instruct
```

如果你仍然传入 `--token`，请记住它会出现在 shell 历史记录和 `ps` 输出中；如果可以，优先使用环境变量。

## 配置片段

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
      model: { primary: "nvidia/nvidia/llama-3.1-nemotron-70b-instruct" },
    },
  },
}
```

## 模型 ID

| 模型引用 | 名称 | 上下文 | 最大输出 |
| ---------------------------------------------------- | ---------------------------------------- | ------- | ---------- |
| `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`      | NVIDIA Llama 3.1 Nemotron 70B Instruct   | 131,072 | 4,096      |
| `nvidia/meta/llama-3.3-70b-instruct`                 | Meta Llama 3.3 70B Instruct              | 131,072 | 4,096      |
| `nvidia/nvidia/mistral-nemo-minitron-8b-8k-instruct` | NVIDIA Mistral NeMo Minitron 8B Instruct | 8,192   | 2,048      |

## 说明

- 使用 OpenAI 兼容的 `/v1` 端点；请使用来自 NVIDIA NGC 的 API 密钥。
- 设置 `NVIDIA_API_KEY` 后，提供商会自动启用。
- 内置目录是静态的；源码中的成本默认值为 `0`。
