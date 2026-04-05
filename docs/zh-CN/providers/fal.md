---
read_when:
    - 你想在 OpenClaw 中使用 fal 图像生成
    - 你需要 FAL_KEY 认证流程
    - 你想为 image_generate 或 video_generate 使用 fal 默认值
summary: 在 OpenClaw 中设置 fal 图像和视频生成
title: fal
x-i18n:
    generated_at: "2026-04-05T22:22:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: f136abdc36826812c9f1930483df308247de07be2dacab4d4c6c1b32d951602c
    source_path: providers/fal.md
    workflow: 15
---

# fal

OpenClaw 内置了一个 `fal` 提供商，用于托管式图像和视频生成。

- 提供商：`fal`
- 认证：`FAL_KEY`
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

- 生成：每个请求最多 4 张图像
- 编辑模式：已启用，支持 1 张参考图像
- 支持 `size`、`aspectRatio` 和 `resolution`
- 当前编辑限制：fal 图像编辑端点**不**支持
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

要将 fal 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "fal/fal-ai/minimax/video-01-live",
      },
    },
  },
}
```

## 相关内容

- [图像生成](/zh-CN/tools/image-generation)
- [视频生成](/zh-CN/tools/video-generation)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
