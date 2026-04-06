---
read_when:
    - 通过智能体生成视频
    - 配置视频生成提供商和模型
    - 了解 `video_generate` 工具参数
summary: 使用已配置的提供商（如 Alibaba、OpenAI、Google、Qwen、MiniMax 和 Runway）生成视频
title: 视频生成
x-i18n:
    generated_at: "2026-04-06T00:19:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9917245069c39676a7e33afe4800d9c528300e8489a35a28aa6c0356d65b2282
    source_path: tools/video-generation.md
    workflow: 15
---

# 视频生成

`video_generate` 工具让智能体能够使用你配置的提供商来创建视频。在智能体会话中，OpenClaw 会将视频生成作为后台任务启动，在任务账本中跟踪它，然后在片段准备就绪后再次唤醒智能体，以便智能体将完成的视频发回原始渠道。

<Note>
只有在至少有一个视频生成提供商可用时，此工具才会出现。如果你在智能体工具中看不到 `video_generate`，请配置 `agents.defaults.videoGenerationModel` 或设置提供商 API 密钥。
</Note>

<Note>
在智能体会话中，`video_generate` 会立即返回一个任务 id/run id。实际的提供商作业会在后台继续运行。完成后，OpenClaw 会使用内部完成事件唤醒同一会话，以便智能体发送常规后续消息以及生成的视频附件。
</Note>

## 快速开始

1. 为至少一个提供商设置 API 密钥（例如 `OPENAI_API_KEY`、`GEMINI_API_KEY`、`MODELSTUDIO_API_KEY`、`QWEN_API_KEY` 或 `RUNWAYML_API_SECRET`）。
2. 可选：设置你偏好的模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "qwen/wan2.6-t2v",
      },
    },
  },
}
```

3. 向智能体发出请求：_“生成一段 5 秒的电影感视频，内容是一只友善的龙虾在日落时分冲浪。”_

智能体会自动调用 `video_generate`。无需工具白名单配置——当提供商可用时，它默认启用。

对于没有会话支持的智能体运行的直接同步上下文，该工具仍会回退为内联生成，并在工具结果中返回最终媒体路径。

## 支持的提供商

| 提供商 | 默认模型                        | 参考输入           | API 密钥                                                   |
| ------ | ------------------------------- | ------------------ | ---------------------------------------------------------- |
| Alibaba  | `wan2.6-t2v`                    | 是，远程 URL       | `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`, `QWEN_API_KEY` |
| BytePlus（国际版） | `seedance-1-0-lite-t2v-250428`  | 1 张图片           | `BYTEPLUS_API_KEY`                                         |
| fal    | `fal-ai/minimax/video-01-live`  | 1 张图片           | `FAL_KEY`                                                  |
| Google | `veo-3.1-fast-generate-preview` | 1 张图片或 1 个视频 | `GEMINI_API_KEY`, `GOOGLE_API_KEY`                         |
| MiniMax | `MiniMax-Hailuo-2.3`            | 1 张图片           | `MINIMAX_API_KEY`                                          |
| OpenAI | `sora-2`                        | 1 张图片或 1 个视频 | `OPENAI_API_KEY`                                           |
| Qwen   | `wan2.6-t2v`                    | 是，远程 URL       | `QWEN_API_KEY`, `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY` |
| Runway | `gen4.5`                        | 1 张图片或 1 个视频 | `RUNWAYML_API_SECRET`, `RUNWAY_API_KEY`                    |
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | 1 张图片           | `TOGETHER_API_KEY`                                         |
| xAI    | `grok-imagine-video`            | 1 张图片或 1 个视频 | `XAI_API_KEY`                                              |

使用 `action: "list"` 在运行时查看可用的提供商和模型：

```
/tool video_generate action=list
```

## 工具参数

| 参数              | 类型     | 描述                                                                                              |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------- |
| `prompt`          | string   | 视频生成提示词（`action: "generate"` 时必填）                                                     |
| `action`          | string   | `"generate"`（默认）、用于当前会话任务的 `"status"`，或用于查看提供商的 `"list"`                 |
| `model`           | string   | 提供商/模型覆盖，例如 `qwen/wan2.6-t2v`                                                           |
| `image`           | string   | 单个参考图片路径或 URL                                                                            |
| `images`          | string[] | 多个参考图片（最多 5 张）                                                                         |
| `video`           | string   | 单个参考视频路径或 URL                                                                            |
| `videos`          | string[] | 多个参考视频（最多 4 个）                                                                         |
| `size`            | string   | 当提供商支持时的尺寸提示                                                                          |
| `aspectRatio`     | string   | 宽高比：`1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9`                 |
| `resolution`      | string   | 分辨率提示：`480P`、`720P` 或 `1080P`                                                             |
| `durationSeconds` | number   | 目标时长（秒）。OpenClaw 可能会将其四舍五入到最近的提供商支持值                                  |
| `audio`           | boolean  | 当提供商支持时启用生成音频                                                                        |
| `watermark`       | boolean  | 在支持时切换提供商水印                                                                            |
| `filename`        | string   | 输出文件名提示                                                                                    |

并非所有提供商都支持所有参数。不受支持的可选覆盖项会在尽力而为的基础上被忽略，并在工具结果中作为警告返回。诸如参考输入过多之类的硬性能力限制，仍会在提交前直接失败。当提供商或模型仅支持离散的视频时长集合时，OpenClaw 会将 `durationSeconds` 四舍五入到最近的支持值，并在工具结果中报告规范化后的时长。

## 异步行为

- 有会话支持的智能体运行：`video_generate` 会创建一个后台任务，立即返回 started/task 响应，并在稍后的智能体后续消息中发送完成的视频。
- 重复预防：当该后台任务仍处于 `queued` 或 `running` 状态时，同一会话中后续的 `video_generate` 调用会返回任务状态，而不是启动另一次生成。
- 状态查询：使用 `action: "status"` 查看当前有会话支持的视频任务，而不启动新任务。
- 任务跟踪：使用 `openclaw tasks list` / `openclaw tasks show <taskId>` 查看生成任务的排队、运行中和终态状态。
- 完成唤醒：OpenClaw 会将内部完成事件注入回同一会话，以便模型自行编写面向用户的后续消息。
- 提示词提示：当视频任务已在进行中时，同一会话中的后续用户/手动轮次会收到一个小的运行时提示，这样模型就不会盲目再次调用 `video_generate`。
- 无会话回退：在没有真实智能体会话的直接/本地上下文中，仍会以内联方式运行，并在同一轮返回最终视频结果。

## 配置

### 模型选择

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

### 提供商选择顺序

生成视频时，OpenClaw 会按以下顺序尝试提供商：

1. 工具调用中的 **`model` 参数**（如果智能体指定了该参数）
2. 配置中的 **`videoGenerationModel.primary`**
3. 按顺序使用 **`videoGenerationModel.fallbacks`**
4. **自动检测** —— 仅使用基于凭证的提供商默认值：
   - 先尝试当前默认提供商
   - 然后按 provider-id 顺序尝试其余已注册的视频生成提供商

如果某个提供商失败，会自动尝试下一个候选项。如果全部失败，错误中将包含每次尝试的详细信息。

## 提供商说明

- Alibaba 使用 DashScope / Model Studio 异步视频端点，目前要求参考资源必须为远程 `http(s)` URL。
- Google 使用 Gemini/Veo，并支持单个图片或视频参考输入。
- MiniMax、Together、BytePlus（国际版）和 fal 目前支持单个图片参考输入。
- OpenAI 使用原生视频端点，目前默认使用 `sora-2`。
- Qwen 支持图片/视频参考，但上游 DashScope 视频端点当前要求这些参考必须为远程 `http(s)` URL。
- Runway 使用原生异步任务 API，并通过 `GET /v1/tasks/{id}` 轮询，目前默认使用 `gen4.5`。
- xAI 使用原生 xAI 视频 API，支持文生视频、图生视频以及远程视频编辑/扩展流程。
- fal 对于长时间运行的作业使用基于队列的 fal 视频流程，而不是单个阻塞式推理请求。

## Qwen 参考输入

内置的 Qwen 提供商支持文生视频以及图片/视频参考模式，但上游 DashScope 视频端点当前要求参考输入必须为 **远程 http(s) URL**。本地文件路径和上传的缓冲区会在前置检查时直接被拒绝，而不是被静默忽略。

## 相关内容

- [工具概览](/zh-CN/tools) — 所有可用的智能体工具
- [后台任务](/zh-CN/automation/tasks) — 分离式 `video_generate` 运行的任务跟踪
- [Alibaba Model Studio](/zh-CN/providers/alibaba) — 直接 Wan 提供商设置
- [Google（Gemini）](/zh-CN/providers/google) — Veo 提供商设置
- [MiniMax](/zh-CN/providers/minimax) — Hailuo 提供商设置
- [OpenAI](/zh-CN/providers/openai) — Sora 提供商设置
- [Qwen](/zh-CN/providers/qwen) — Qwen 专属设置和限制
- [Runway](/zh-CN/providers/runway) — Runway 设置以及当前模型/输入说明
- [Together AI](/zh-CN/providers/together) — Together Wan 提供商设置
- [xAI](/zh-CN/providers/xai) — Grok 视频提供商设置
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults) — `videoGenerationModel` 配置
- [模型](/zh-CN/concepts/models) — 模型配置和故障转移
