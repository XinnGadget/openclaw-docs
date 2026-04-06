---
read_when:
    - 通过智能体生成视频
    - 配置视频生成 provider 和模型
    - 了解 `video_generate` 工具参数
summary: 使用 12 个 provider 后端根据文本、图像或现有视频生成视频
title: 视频生成
x-i18n:
    generated_at: "2026-04-06T15:32:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7d995d91f86f863f5a69c6945043dc430eb186830348a09eeaaad94620767f7d
    source_path: tools/video-generation.md
    workflow: 15
---

# 视频生成

OpenClaw 智能体可以根据文本提示词、参考图像或现有视频生成视频。支持 12 个 provider 后端，每个后端都有不同的模型选项、输入模式和功能集。智能体会根据你的配置和可用的 API 密钥自动选择合适的 provider。

<Note>
只有在至少有一个视频生成 provider 可用时，`video_generate` 工具才会出现。如果你没有在智能体工具中看到它，请设置 provider API 密钥或配置 `agents.defaults.videoGenerationModel`。
</Note>

OpenClaw 将视频生成视为三种运行时模式：

- `generate`：用于没有参考媒体的 text-to-video 请求
- `imageToVideo`：当请求包含一个或多个参考图像时使用
- `videoToVideo`：当请求包含一个或多个参考视频时使用

Providers 可以支持这些模式中的任意子集。工具会在提交前验证当前
模式，并在 `action=list` 中报告支持的模式。

## 快速开始

1. 为任意受支持的 provider 设置 API 密钥：

```bash
export GEMINI_API_KEY="your-key"
```

2. 可选地固定一个默认模型：

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "google/veo-3.1-fast-generate-preview"
```

3. 向智能体发出请求：

> 生成一个 5 秒钟的电影感视频：一只友好的龙虾在日落时冲浪。

智能体会自动调用 `video_generate`。不需要工具 allowlist。

## 生成视频时会发生什么

视频生成是异步的。当智能体在会话中调用 `video_generate` 时：

1. OpenClaw 将请求提交给 provider，并立即返回一个任务 ID。
2. Provider 在后台处理该任务（通常需要 30 秒到 5 分钟，取决于 provider 和分辨率）。
3. 当视频准备就绪后，OpenClaw 会通过内部完成事件唤醒同一个会话。
4. 智能体会将生成完成的视频发布回原始对话中。

当同一会话中已有任务正在进行时，重复调用 `video_generate` 不会启动新的生成，而是返回当前任务状态。使用 `openclaw tasks list` 或 `openclaw tasks show <taskId>` 可以在 CLI 中检查进度。

在没有会话支持的智能体运行之外（例如直接工具调用），该工具会回退为内联生成，并在同一轮中返回最终媒体路径。

### 任务生命周期

每个 `video_generate` 请求都会经历四种状态：

1. **queued** -- 任务已创建，等待 provider 接受。
2. **running** -- provider 正在处理（通常需要 30 秒到 5 分钟，取决于 provider 和分辨率）。
3. **succeeded** -- 视频已准备好；智能体会被唤醒并将其发布到对话中。
4. **failed** -- provider 错误或超时；智能体会带着错误详情被唤醒。

从 CLI 检查状态：

```bash
openclaw tasks list
openclaw tasks show <taskId>
openclaw tasks cancel <taskId>
```

防止重复：如果当前会话已有视频任务处于 `queued` 或 `running` 状态，`video_generate` 会返回现有任务状态，而不是启动新任务。使用 `action: "status"` 可以显式检查状态，而不触发新的生成。

## 支持的 providers

| Provider | 默认模型 | 文本 | 图像参考 | 视频参考 | API 密钥 |
| -------- | ------------------------------- | ---- | ----------------- | ---------------- | ---------------------------------------- |
| Alibaba  | `wan2.6-t2v`                    | Yes  | Yes（远程 URL） | Yes（远程 URL） | `MODELSTUDIO_API_KEY`                    |
| BytePlus（国际版） | `seedance-1-0-lite-t2v-250428`  | Yes  | 1 张图像 | No               | `BYTEPLUS_API_KEY`                       |
| ComfyUI  | `workflow`                      | Yes  | 1 张图像 | No               | `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY` |
| fal      | `fal-ai/minimax/video-01-live`  | Yes  | 1 张图像 | No               | `FAL_KEY`                                |
| Google   | `veo-3.1-fast-generate-preview` | Yes  | 1 张图像 | 1 个视频 | `GEMINI_API_KEY`                         |
| MiniMax  | `MiniMax-Hailuo-2.3`            | Yes  | 1 张图像 | No               | `MINIMAX_API_KEY`                        |
| OpenAI   | `sora-2`                        | Yes  | 1 张图像 | 1 个视频 | `OPENAI_API_KEY`                         |
| Qwen     | `wan2.6-t2v`                    | Yes  | Yes（远程 URL） | Yes（远程 URL） | `QWEN_API_KEY`                           |
| Runway   | `gen4.5`                        | Yes  | 1 张图像 | 1 个视频 | `RUNWAYML_API_SECRET`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | Yes  | 1 张图像 | No               | `TOGETHER_API_KEY`                       |
| Vydra    | `veo3`                          | Yes  | 1 张图像（`kling`） | No               | `VYDRA_API_KEY`                          |
| xAI      | `grok-imagine-video`            | Yes  | 1 张图像 | 1 个视频 | `XAI_API_KEY`                            |

某些 provider 接受额外的或替代的 API 密钥环境变量。详情请参见各个[provider 页面](#related)。

运行 `video_generate action=list` 可在运行时检查可用的 provider、模型和
运行时模式。

### 声明的能力矩阵

这是 `video_generate`、合约测试和共享 live sweep 所使用的显式模式合约。

| Provider | `generate` | `imageToVideo` | `videoToVideo` | 当前共享 live lanes |
| -------- | ---------- | -------------- | -------------- | ---------------------------------------------------------------------------------------------------------- |
| Alibaba  | Yes        | Yes            | Yes            | `generate`、`imageToVideo`；跳过 `videoToVideo`，因为此 provider 需要远程 `http(s)` 视频 URL |
| BytePlus（国际版） | Yes        | Yes            | No             | `generate`、`imageToVideo` |
| ComfyUI  | Yes        | Yes            | No             | 不在共享 sweep 中；特定 workflow 的覆盖由 Comfy 测试负责 |
| fal      | Yes        | Yes            | No             | `generate`、`imageToVideo` |
| Google   | Yes        | Yes            | Yes            | `generate`、`imageToVideo`、`videoToVideo` |
| MiniMax  | Yes        | Yes            | No             | `generate`、`imageToVideo` |
| OpenAI   | Yes        | Yes            | Yes            | `generate`、`imageToVideo`、`videoToVideo` |
| Qwen     | Yes        | Yes            | Yes            | `generate`、`imageToVideo`；跳过 `videoToVideo`，因为此 provider 需要远程 `http(s)` 视频 URL |
| Runway   | Yes        | Yes            | Yes            | `generate`、`imageToVideo`；仅当所选模型为 `runway/gen4_aleph` 时运行 `videoToVideo` |
| Together | Yes        | Yes            | No             | `generate`、`imageToVideo` |
| Vydra    | Yes        | Yes            | No             | `generate`、`imageToVideo` |
| xAI      | Yes        | Yes            | Yes            | `generate`、`imageToVideo`；跳过 `videoToVideo`，因为此 provider 当前需要远程 MP4 URL |

## 工具参数

### 必填

| 参数 | 类型 | 描述 |
| --------- | ------ | ----------------------------------------------------------------------------- |
| `prompt`  | string | 要生成的视频文本描述（`action: "generate"` 时必填） |

### 内容输入

| 参数 | 类型 | 描述 |
| --------- | -------- | ------------------------------------ |
| `image`   | string   | 单个参考图像（路径或 URL） |
| `images`  | string[] | 多个参考图像（最多 5 个） |
| `video`   | string   | 单个参考视频（路径或 URL） |
| `videos`  | string[] | 多个参考视频（最多 4 个） |

### 风格控制

| 参数 | 类型 | 描述 |
| ----------------- | ------- | ------------------------------------------------------------------------ |
| `aspectRatio`     | string  | `1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9` |
| `resolution`      | string  | `480P`、`720P` 或 `1080P` |
| `durationSeconds` | number  | 目标时长（秒，会四舍五入到 provider 支持的最近值） |
| `size`            | string  | 当 provider 支持时使用的尺寸提示 |
| `audio`           | boolean | 在支持时启用生成音频 |
| `watermark`       | boolean | 在支持时切换 provider 水印 |

### 高级

| 参数 | 类型 | 描述 |
| ---------- | ------ | ----------------------------------------------- |
| `action`   | string | `"generate"`（默认）、`"status"` 或 `"list"` |
| `model`    | string | provider/model 覆盖（例如 `runway/gen4.5`） |
| `filename` | string | 输出文件名提示 |

并非所有 provider 都支持所有参数。不支持的覆盖会尽力忽略，并在工具结果中报告为警告。硬性能力限制（例如参考输入过多）会在提交前直接失败。

参考输入还会决定运行时模式：

- 无参考媒体：`generate`
- 任意图像参考：`imageToVideo`
- 任意视频参考：`videoToVideo`

混合图像与视频参考不是稳定的共享能力表面。
每个请求优先只使用一种参考类型。

## 操作

- **generate**（默认）-- 根据给定提示词和可选参考输入创建视频。
- **status** -- 检查当前会话中正在进行的视频任务状态，而不启动新的生成。
- **list** -- 显示可用的 provider、模型及其能力。

## 模型选择

生成视频时，OpenClaw 按以下顺序解析模型：

1. **`model` 工具参数** -- 如果智能体在调用中指定了它。
2. **`videoGenerationModel.primary`** -- 来自配置。
3. **`videoGenerationModel.fallbacks`** -- 按顺序尝试。
4. **自动检测** -- 使用具有有效身份验证的 providers，先从当前默认 provider 开始，然后按字母顺序尝试其余 providers。

如果某个 provider 失败，会自动尝试下一个候选项。如果所有候选项都失败，错误中会包含每次尝试的详情。

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
        fallbacks: ["runway/gen4.5", "qwen/wan2.6-t2v"],
      },
    },
  },
}
```

## Provider 说明

| Provider | 说明 |
| -------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Alibaba  | 使用 DashScope/Model Studio 异步端点。参考图像和视频必须是远程 `http(s)` URL。 |
| BytePlus（国际版） | 仅支持单张参考图像。 |
| ComfyUI  | 由 workflow 驱动的本地或云端执行。通过已配置图支持 text-to-video 和 image-to-video。 |
| fal      | 对长时间运行任务使用基于队列的流程。仅支持单张参考图像。 |
| Google   | 使用 Gemini/Veo。支持一张参考图像或一个参考视频。 |
| MiniMax  | 仅支持单张参考图像。 |
| OpenAI   | 只会转发 `size` 覆盖。其他风格覆盖（`aspectRatio`、`resolution`、`audio`、`watermark`）会被忽略并附带警告。 |
| Qwen     | 与 Alibaba 使用相同的 DashScope 后端。参考输入必须是远程 `http(s)` URL；本地文件会在一开始就被拒绝。 |
| Runway   | 通过 data URI 支持本地文件。video-to-video 需要 `runway/gen4_aleph`。纯文本运行暴露 `16:9` 和 `9:16` 宽高比。 |
| Together | 仅支持单张参考图像。 |
| Vydra    | 直接使用 `https://www.vydra.ai/api/v1` 以避免丢失身份验证的重定向。`veo3` 内置为仅 text-to-video；`kling` 需要远程图像 URL。 |
| xAI      | 支持 text-to-video、image-to-video，以及远程视频编辑/扩展流程。 |

## Provider 能力模式

共享视频生成合约现在允许 providers 声明特定模式的
能力，而不是只声明扁平的聚合限制。新的 provider
实现应优先使用显式模式块：

```typescript
capabilities: {
  generate: {
    maxVideos: 1,
    maxDurationSeconds: 10,
    supportsResolution: true,
  },
  imageToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputImages: 1,
    maxDurationSeconds: 5,
  },
  videoToVideo: {
    enabled: true,
    maxVideos: 1,
    maxInputVideos: 1,
    maxDurationSeconds: 5,
  },
}
```

像 `maxInputImages` 和 `maxInputVideos` 这样的扁平聚合字段，不足以表达变换模式支持。Providers 应显式声明
`generate`、`imageToVideo` 和 `videoToVideo`，这样 live tests、
合约测试和共享 `video_generate` 工具才能以确定性的方式验证模式支持。

## Live tests

针对共享内置 providers 的选择接入 live 覆盖：

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts
```

该 live 文件会从 `~/.profile` 加载缺失的 provider 环境变量，默认优先使用
live/env API 密钥而不是已存储的 auth profiles，并运行它能够用本地媒体安全执行的已声明模式：

- 对 sweep 中每个 provider 执行 `generate`
- 当 `capabilities.imageToVideo.enabled` 时执行 `imageToVideo`
- 当 `capabilities.videoToVideo.enabled` 且 provider/model
  在共享 sweep 中接受基于缓冲区的本地视频输入时执行 `videoToVideo`

目前共享 `videoToVideo` live lane 覆盖：

- `google`
- `openai`
- `runway`，仅当你选择 `runway/gen4_aleph`

## 配置

在你的 OpenClaw 配置中设置默认视频生成模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
        fallbacks: ["qwen/wan2.6-r2v-flash"],
      },
    },
  },
}
```

或者通过 CLI：

```bash
openclaw config set agents.defaults.videoGenerationModel.primary "qwen/wan2.6-t2v"
```

## 相关内容

- [工具概览](/zh-CN/tools)
- [后台任务](/zh-CN/automation/tasks) -- 异步视频生成的任务跟踪
- [Alibaba Model Studio](/zh-CN/providers/alibaba)
- [BytePlus（国际版）](/zh-CN/concepts/model-providers#byteplus-international)
- [ComfyUI](/zh-CN/providers/comfy)
- [fal](/zh-CN/providers/fal)
- [Google（Gemini）](/zh-CN/providers/google)
- [MiniMax](/zh-CN/providers/minimax)
- [OpenAI](/zh-CN/providers/openai)
- [Qwen](/zh-CN/providers/qwen)
- [Runway](/zh-CN/providers/runway)
- [Together AI](/zh-CN/providers/together)
- [Vydra](/zh-CN/providers/vydra)
- [xAI](/zh-CN/providers/xai)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
- [模型](/zh-CN/concepts/models)
