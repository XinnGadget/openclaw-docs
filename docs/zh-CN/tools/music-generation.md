---
read_when:
    - 通过智能体生成音乐或音频
    - 配置音乐生成提供商和模型
    - 了解 `music_generate` 工具参数
summary: 通过共享提供商或插件提供的工作流生成音乐
title: 音乐生成
x-i18n:
    generated_at: "2026-04-06T01:00:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 10a310920a34a6d2aa90b82703b00dbd9944ec349ada948c3fdb12e9d45246a0
    source_path: tools/music-generation.md
    workflow: 15
---

# 音乐生成

`music_generate` 工具让智能体通过以下任一方式创建音乐或音频：

- 使用共享音乐生成功能，并配合已配置的提供商，例如 Google 和 MiniMax
- 使用由插件提供的工具接口，例如通过工作流配置的 ComfyUI 图表

对于由共享提供商支持的智能体会话，OpenClaw 会将音乐生成作为后台任务启动，在任务账本中跟踪它，然后在曲目准备好后再次唤醒智能体，以便智能体将完成的音频回发到原始渠道中。

<Note>
只有在至少有一个音乐生成提供商可用时，内置共享工具才会显示。如果你在智能体的工具中看不到 `music_generate`，请配置 `agents.defaults.musicGenerationModel` 或设置提供商 API 密钥。
</Note>

<Note>
由插件提供的 `music_generate` 实现可能会暴露不同的参数或运行时行为。下面的异步任务/状态流程适用于内置的、由共享提供商支持的路径。
</Note>

## 快速开始

### 共享提供商支持的生成

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

3. 向智能体发出请求：_“生成一首关于夜晚穿行霓虹城市驾驶的欢快 synthpop 曲目。”_

智能体会自动调用 `music_generate`。无需配置工具允许列表。

对于没有会话支持的智能体运行的直接同步上下文，内置工具仍会回退到内联生成，并在工具结果中返回最终媒体路径。

示例提示词：

```text
Generate a cinematic piano track with soft strings and no vocals.
```

```text
Generate an energetic chiptune loop about launching a rocket at sunrise.
```

### 工作流驱动的插件生成

内置的 `comfy` 插件也可以使用通过工作流配置的 ComfyUI 图表提供 `music_generate`。

1. 使用工作流 JSON 以及提示词/输出节点配置 `models.providers.comfy.music`。
2. 如果你使用 Comfy Cloud，请设置 `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY`。
3. 请求智能体生成音乐，或直接调用该工具。

示例：

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

## 共享内置提供商支持

| 提供商 | 默认模型               | 参考输入         | 支持的控制项                                              | API 密钥                           |
| ------ | ---------------------- | ---------------- | --------------------------------------------------------- | ---------------------------------- |
| Google | `lyria-3-clip-preview` | 最多 10 张图片   | `lyrics`、`instrumental`、`format`                        | `GEMINI_API_KEY`, `GOOGLE_API_KEY` |
| MiniMax  | `music-2.5+`           | 无               | `lyrics`、`instrumental`、`durationSeconds`、`format=mp3` | `MINIMAX_API_KEY`                  |

## 插件提供的支持

| 提供商   | 模型       | 说明                     |
| -------- | ---------- | ------------------------ |
| ComfyUI  | `workflow` | 由工作流定义的音乐或音频 |

使用 `action: "list"` 可在运行时检查可用的共享提供商和模型：

```text
/tool music_generate action=list
```

使用 `action: "status"` 可检查当前由会话支持的音乐任务：

```text
/tool music_generate action=status
```

直接生成示例：

```text
/tool music_generate prompt="Dreamy lo-fi hip hop with vinyl texture and gentle rain" instrumental=true
```

## 内置工具参数

| 参数              | 类型     | 说明                                                                                             |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------ |
| `prompt`          | string   | 音乐生成提示词（`action: "generate"` 时必填）                                                    |
| `action`          | string   | `"generate"`（默认）、用于当前会话任务的 `"status"`，或用于检查提供商的 `"list"`                 |
| `model`           | string   | 提供商/模型覆盖，例如 `google/lyria-3-pro-preview` 或 `comfy/workflow`                           |
| `lyrics`          | string   | 当提供商支持显式歌词输入时可选填写歌词                                                           |
| `instrumental`    | boolean  | 当提供商支持时，请求仅器乐输出                                                                   |
| `image`           | string   | 单个参考图片路径或 URL                                                                           |
| `images`          | string[] | 多个参考图片（最多 10 张）                                                                       |
| `durationSeconds` | number   | 当提供商支持时，以秒为单位指定目标时长提示                                                       |
| `format`          | string   | 当提供商支持时，输出格式提示（`mp3` 或 `wav`）                                                   |
| `filename`        | string   | 输出文件名提示                                                                                   |

并非所有提供商或插件都支持所有参数。共享内置工具会在提交请求前验证提供商能力限制。

## 共享提供商支持路径的异步行为

- 由会话支持的智能体运行：`music_generate` 会创建后台任务，立即返回 started/task 响应，并稍后在后续智能体消息中发布完成的曲目。
- 防止重复：当该后台任务仍处于 `queued` 或 `running` 状态时，同一会话中的后续 `music_generate` 调用会返回任务状态，而不是启动另一次生成。
- 状态查询：使用 `action: "status"` 可检查当前由会话支持的音乐任务，而不会启动新任务。
- 任务跟踪：使用 `openclaw tasks list` 或 `openclaw tasks show <taskId>` 检查该生成任务的排队、运行和终态状态。
- 完成唤醒：OpenClaw 会将内部完成事件重新注入到同一会话中，以便模型自行编写面向用户的后续回复。
- 提示词提示：当音乐任务已在进行中时，同一会话中的后续用户/手动轮次会收到一条简短的运行时提示，以便模型不会再次盲目调用 `music_generate`。
- 无会话回退：没有真实智能体会话的直接/本地上下文仍会以内联方式运行，并在同一轮中返回最终音频结果。

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

1. 工具调用中的 `model` 参数（如果智能体指定了它）
2. 配置中的 `musicGenerationModel.primary`
3. 按顺序使用 `musicGenerationModel.fallbacks`
4. 仅使用基于认证支持的提供商默认值进行自动检测：
   - 先尝试当前默认提供商
   - 再按提供商 ID 顺序尝试其余已注册的音乐生成提供商

如果某个提供商失败，会自动尝试下一个候选项。如果全部失败，错误中将包含每次尝试的详细信息。

## 提供商说明

- Google 使用 Lyria 3 批量生成。当前内置流程支持提示词、可选歌词文本以及可选参考图片。
- MiniMax 使用批量 `music_generation` 端点。当前内置流程支持提示词、可选歌词、器乐模式、时长控制以及 mp3 输出。
- ComfyUI 支持由工作流驱动，并取决于配置的图表以及提示词/输出字段的节点映射。

## 选择合适的路径

- 当你需要模型选择、提供商故障切换以及内置异步任务/状态流时，请使用共享提供商支持路径。
- 当你需要自定义工作流图表，或使用不属于共享内置音乐能力的提供商时，请使用插件路径，例如 ComfyUI。
- 如果你正在调试 ComfyUI 特定行为，请参阅 [ComfyUI](/zh-CN/providers/comfy)。如果你正在调试共享提供商行为，请先查看 [Google (Gemini)](/zh-CN/providers/google) 或 [MiniMax](/zh-CN/providers/minimax)。

## 实时测试

共享内置提供商的选择性实时覆盖：

```bash
OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts
```

内置 ComfyUI 音乐路径的选择性实时覆盖：

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

如果配置了相关部分，Comfy 实时文件还会覆盖 comfy 图片和视频工作流。

## 相关内容

- [后台任务](/zh-CN/automation/tasks) - 用于分离式 `music_generate` 运行的任务跟踪
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults) - `musicGenerationModel` 配置
- [ComfyUI](/zh-CN/providers/comfy)
- [Google (Gemini)](/zh-CN/providers/google)
- [MiniMax](/zh-CN/providers/minimax)
- [模型](/zh-CN/concepts/models) - 模型配置与故障切换
- [工具概览](/zh-CN/tools)
