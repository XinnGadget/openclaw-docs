---
read_when:
    - 你想在 OpenClaw 中使用 Runway 视频生成
    - 你需要设置 Runway API 密钥/环境变量
    - 你想将 Runway 设为默认视频提供商
summary: OpenClaw 中的 Runway 视频生成设置
title: Runway
x-i18n:
    generated_at: "2026-04-06T00:19:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 87092da3f1a3cb137b0a3dffe1241a5a3d84eb29fa7c3a6b1df9c2871f1c80b6
    source_path: providers/runway.md
    workflow: 15
---

# Runway

OpenClaw 内置了一个 `runway` 提供商，用于托管视频生成。

- 提供商：`runway`
- 凭证：`RUNWAYML_API_SECRET`（规范名称；`RUNWAY_API_KEY` 也可用）
- API：Runway 基于任务的视频生成 API

## 快速开始

1. 设置 API 密钥：

```bash
openclaw onboard --auth-choice runway-api-key
```

2. 设置默认视频模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## 视频生成

内置的 `runway` 视频生成提供商默认使用 `runway/gen4.5`。

- 模式：文生视频、单图图生视频，以及单视频视频转视频
- 运行时：异步提交任务，并通过 `GET /v1/tasks/{id}` 轮询
- 智能体会话：`video_generate` 会启动一个后台任务，之后在同一会话中的调用现在会返回活动任务状态，而不是生成重复运行
- 状态查询：`video_generate action=status`
- 本地图像/视频引用：支持通过数据 URI
- 当前视频转视频注意事项：OpenClaw 目前对视频输入要求使用 `runway/gen4_aleph`
- 当前文生视频注意事项：OpenClaw 目前为纯文本运行公开 `16:9` 和 `9:16`

要将 Runway 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "runway/gen4.5",
      },
    },
  },
}
```

## 相关内容

- [视频生成](/zh-CN/tools/video-generation)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
