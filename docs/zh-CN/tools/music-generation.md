---
read_when:
    - 通过智能体生成音乐或音频
    - 配置音乐生成提供商和模型
    - 了解 `music_generate` 工具参数
summary: 使用共享提供商生成音乐，包括基于工作流的插件
title: 音乐生成
x-i18n:
    generated_at: "2026-04-06T01:07:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7e5dc234b14aee2f5ef766985479b0ba262cceb4510596f6b1cc343a3732838c
    source_path: tools/music-generation.md
    workflow: 15
---

# 音乐生成

`music_generate` 工具让智能体能够通过共享音乐生成能力，结合已配置的提供商（例如 Google、MiniMax 和基于工作流配置的 ComfyUI）创建音乐或音频。

对于由共享提供商支持的智能体会话，OpenClaw 会将音乐生成作为后台任务启动，在任务账本中跟踪它，然后在音轨准备就绪时再次唤醒智能体，以便智能体将完成的音频发布回原始渠道。

<Note>
只有在至少有一个音乐生成提供商可用时，内置共享工具才会显示。如果你在智能体工具中看不到 `music_generate`，请配置 `agents.defaults.musicGenerationModel` 或设置提供商 API 密钥。
</Note>

## 快速开始

### 由共享提供商支持的生成

1. 为至少一个提供商设置 API 密钥，例如 `GEMINI_API_KEY` 或 `MINIMAX_API_KEY`。
2. 可选：设置你偏好的模型：

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
      },
    },
  },
}
```

3. 向智能体发出请求：_“生成一段欢快的 synthpop 音轨，主题是在霓虹都市中夜间驾车。”_

智能体会自动调用 `music_generate`。不需要工具允许列表。

对于没有会话支持的智能体运行的直接同步上下文，内置工具仍会回退为内联生成，并在工具结果中返回最终媒体路径。

示例提示词：

```text
Generate a cinematic piano track with soft strings and no vocals.
```

```text
Generate an energetic chiptune loop about launching a rocket at sunrise.
```

### 由工作流驱动的 Comfy 生成

内置的 `comfy` 插件通过音乐生成提供商注册表接入共享 `music_generate` 工具。

1. 为 `models.providers.comfy.music` 配置工作流 JSON 以及提示词/输出节点。
2. 如果你使用 Comfy Cloud，请设置 `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY`。
3. 请求智能体生成音乐，或直接调用该工具。

示例：

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

## 共享内置提供商支持

| 提供商 | 默认模型               | 参考输入       | 支持的控制项                                              | API 密钥                               |
| ------ | ---------------------- | -------------- | --------------------------------------------------------- | -------------------------------------- |
| ComfyUI  | `workflow`           | 最多 1 张图片  | 由工作流定义的音乐或音频                                  | `COMFY_API_KEY`, `COMFY_CLOUD_API_KEY` |
| Google | `lyria-3-clip-preview` | 最多 10 张图片 | `lyrics`、`instrumental`、`format`                        | `GEMINI_API_KEY`, `GOOGLE_API_KEY`     |
| MiniMax | `music-2.5+`         | 无             | `lyrics`、`instrumental`、`durationSeconds`、`format=mp3` | `MINIMAX_API_KEY`                      |

使用 `action: "list"` 可在运行时查看可用的共享提供商和模型：

```text
/tool music_generate action=list
```

使用 `action: "status"` 可检查当前由会话支持的活动音乐任务：

```text
/tool music_generate action=status
```

直接生成示例：

```text
/tool music_generate prompt="Dreamy lo-fi hip hop with vinyl texture and gentle rain" instrumental=true
```

## 内置工具参数

| 参数              | 类型     | 描述                                                                                              |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------- |
| `prompt`          | string   | 音乐生成提示词（`action: "generate"` 时必填）                                                     |
| `action`          | string   | `"generate"`（默认）、用于当前会话任务的 `"status"`，或用于查看提供商的 `"list"`                  |
| `model`           | string   | 提供商/模型覆盖，例如 `google/lyria-3-pro-preview` 或 `comfy/workflow`                            |
| `lyrics`          | string   | 当提供商支持显式歌词输入时可选填写歌词                                                            |
| `instrumental`    | boolean  | 当提供商支持时，请求仅器乐输出                                                                    |
| `image`           | string   | 单个参考图片路径或 URL                                                                            |
| `images`          | string[] | 多个参考图片（最多 10 张）                                                                        |
| `durationSeconds` | number   | 当提供商支持时长提示时，以秒为单位的目标时长                                                      |
| `format`          | string   | 当提供商支持时的输出格式提示（`mp3` 或 `wav`）                                                    |
| `filename`        | string   | 输出文件名提示                                                                                    |

并非所有提供商都支持所有参数。共享工具会在提交请求前验证提供商能力限制。

## 共享提供商支持路径的异步行为

- 由会话支持的智能体运行：`music_generate` 会创建后台任务，立即返回 started/task 响应，并在稍后的智能体跟进消息中发布完成的音轨。
- 防止重复：当该后台任务仍处于 `queued` 或 `running` 状态时，同一会话中后续的 `music_generate` 调用会返回任务状态，而不是再次启动生成。
- 状态查询：使用 `action: "status"` 可检查当前由会话支持的活动音乐任务，而不会启动新任务。
- 任务跟踪：使用 `openclaw tasks list` 或 `openclaw tasks show <taskId>` 可检查生成任务的排队、运行中和终态状态。
- 完成唤醒：OpenClaw 会将内部完成事件注入回同一会话，以便模型自行编写面向用户的后续消息。
- 提示词提示：当音乐任务已在处理中时，同一会话中后续的用户/手动轮次会收到一个小型运行时提示，这样模型就不会盲目再次调用 `music_generate`。
- 无会话回退：在没有真实智能体会话的直接/本地上下文中，仍会以内联方式运行，并在同一轮中返回最终音频结果。

## 配置

### 模型选择

```json5
{
  agents: {
    defaults: {
      musicGenerationModel: {
        primary: "google/lyria-3-clip-preview",
        fallbacks: ["minimax/music-2.5+"],
      },
    },
  },
}
```

### 提供商选择顺序

生成音乐时，OpenClaw 会按以下顺序尝试提供商：

1. 工具调用中的 `model` 参数（如果智能体指定了）
2. 配置中的 `musicGenerationModel.primary`
3. 按顺序尝试 `musicGenerationModel.fallbacks`
4. 仅使用基于凭证的提供商默认值进行自动检测：
   - 先尝试当前默认提供商
   - 再按 provider-id 顺序尝试其余已注册的音乐生成提供商

如果某个提供商失败，会自动尝试下一个候选项。如果全部失败，错误信息会包含每次尝试的详细信息。

## 提供商说明

- Google 使用 Lyria 3 批量生成。当前内置流程支持提示词、可选歌词文本和可选参考图片。
- MiniMax 使用批量 `music_generation` 端点。当前内置流程支持提示词、可选歌词、器乐模式、时长控制以及 mp3 输出。
- ComfyUI 支持由工作流驱动，具体取决于已配置的图形以及提示词/输出字段的节点映射。

## 选择合适的路径

- 如果你希望使用模型选择、提供商故障切换和内置的异步任务/状态流程，请使用由共享提供商支持的路径。
- 如果你需要自定义工作流图，或需要使用不属于共享内置音乐能力的提供商，请使用插件路径，例如 ComfyUI。
- 如果你正在调试 ComfyUI 特定行为，请参见 [ComfyUI](/zh-CN/providers/comfy)。如果你正在调试共享提供商行为，请先查看 [Google (Gemini)](/zh-CN/providers/google) 或 [MiniMax](/zh-CN/providers/minimax)。

## 实时测试

共享内置提供商的选择加入式实时覆盖：

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

内置 ComfyUI 音乐路径的选择加入式实时覆盖：

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

当这些部分已配置时，Comfy 实时文件也涵盖 comfy 图片和视频工作流。

## 相关内容

- [后台任务](/zh-CN/automation/tasks) - 用于分离式 `music_generate` 运行的任务跟踪
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` 配置
- [ComfyUI](/zh-CN/providers/comfy)
- [Google (Gemini)](/zh-CN/providers/google)
- [MiniMax](/zh-CN/providers/minimax)
- [模型](/zh-CN/concepts/models) - 模型配置和故障切换
- [工具概览](/zh-CN/tools)
