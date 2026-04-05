---
read_when:
    - 你想将 Together AI 与 OpenClaw 搭配使用
    - 你需要 API 密钥环境变量或 CLI 凭证选项
summary: Together AI 设置（凭证 + 模型选择）
title: Together AI
x-i18n:
    generated_at: "2026-04-05T22:23:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: b68fdc15bfcac8d59e3e0c06a39162abd48d9d41a9a64a0ac622cd8e3f80a595
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) 通过统一的 API 提供对 Llama、DeepSeek、Kimi 等领先开源模型的访问。

- 提供商：`together`
- 凭证：`TOGETHER_API_KEY`
- API：与 OpenAI 兼容
- 基础 URL：`https://api.together.xyz/v1`

## 快速开始

1. 设置 API 密钥（推荐：为 Gateway 网关 存储它）：

```bash
openclaw onboard --auth-choice together-api-key
```

2. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## 非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

这会将 `together/moonshotai/Kimi-K2.5` 设置为默认模型。

## 环境说明

如果 Gateway 网关 以守护进程（launchd/systemd）方式运行，请确保 `TOGETHER_API_KEY`
对该进程可用（例如，在 `~/.openclaw/.env` 中或通过
`env.shellEnv`）。

## 内置目录

OpenClaw 当前内置了以下 Together 模型目录：

| Model ref                                                    | Name                                   | Input       | Context    | Notes                            |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | 文本、图像  | 262,144    | 默认模型；已启用推理             |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | 文本        | 202,752    | 通用文本模型                     |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | 文本        | 131,072    | 快速指令模型                     |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | 文本、图像  | 10,000,000 | 多模态                           |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | 文本、图像  | 20,000,000 | 多模态                           |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | 文本        | 131,072    | 通用文本模型                     |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | 文本        | 131,072    | 推理模型                         |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | 文本        | 262,144    | 次要 Kimi 文本模型               |

新手引导预设会将 `together/moonshotai/Kimi-K2.5` 设置为默认模型。

## 视频生成

内置的 `together` 插件还通过共享的 `video_generate` 工具注册了视频生成功能。

- 默认视频模型：`together/Wan-AI/Wan2.2-T2V-A14B`
- 模式：文生视频和单图参考流程
- 支持 `aspectRatio` 和 `resolution`

要将 Together 设为默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

有关共享工具参数、提供商选择和故障转移行为，请参阅[视频生成](/zh-CN/tools/video-generation)。
