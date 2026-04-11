---
read_when:
    - 你想在 OpenClaw 中使用 fal 图像生成
    - 你需要 `FAL_KEY` 认证流程
    - 你想为 `image_generate` 或 `video_generate` 使用 fal 默认设置
summary: fal 图像和视频生成在 OpenClaw 中的设置
title: fal
x-i18n:
    generated_at: "2026-04-11T01:59:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9bfe4f69124e922a79a516a1bd78f0c00f7a45f3c6f68b6d39e0d196fa01beb3
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw 内置了一个 `fal` 提供商，用于托管式图像和视频生成。

- 提供商：`fal`
- 认证：`FAL_KEY`（规范用法；`FAL_API_KEY` 也可作为回退）
- API：fal 模型端点

## 快速开始

1. 设置 API 密钥：

```bash
openclaw onboard --auth-choice fal-api-key
```

2. 设置默认图像模型：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## 图像生成

内置的 `fal` 图像生成提供商默认使用
`fal/fal-ai/flux/dev`。

- 生成：每次请求最多 4 张图像
- 编辑模式：已启用，支持 1 张参考图像
- 支持 `size`、`aspectRatio` 和 `resolution`
- 当前编辑注意事项：fal 图像编辑端点**不**支持
  `aspectRatio` 覆盖

要将 fal 用作默认图像提供商：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "fal/fal-ai/flux/dev",
      },
    },
  },
}
```

## 视频生成

内置的 `fal` 视频生成提供商默认使用
`fal/fal-ai/minimax/video-01-live`。

- 模式：文生视频和单图参考流程
- 运行时：基于队列的提交 / 状态 / 结果流程，用于长时间运行的任务
- HeyGen 视频智能体模型引用：
  - `fal/fal-ai/heygen/v2/video-agent`
- Seedance 2.0 模型引用：
  - `fal/bytedance/seedance-2.0/fast/text-to-video`
  - `fal/bytedance/seedance-2.0/fast/image-to-video`
  - `fal/bytedance/seedance-2.0/text-to-video`
  - `fal/bytedance/seedance-2.0/image-to-video`

要将 Seedance 2.0 用作默认视频模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/bytedance/seedance-2.0/fast/text-to-video",
      },
    },
  },
}
```

要将 HeyGen 视频智能体用作默认视频模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/heygen/v2/video-agent",
      },
    },
  },
}
```

## 相关内容

- [图像生成](/zh-CN/tools/image-generation)
- [视频生成](/zh-CN/tools/video-generation)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
