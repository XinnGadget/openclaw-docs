---
read_when:
    - 通过智能体生成视频
    - 配置视频生成提供商和模型
    - 了解 `video_generate` 工具参数
summary: 使用已配置的提供商（如 Alibaba、OpenAI、Google、Qwen 和 MiniMax）生成视频
title: 视频生成
x-i18n:
    generated_at: "2026-04-05T22:08:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2e2c4e263bdcf96eab5067c93cee6719890b3e05396fc948854ff4926576ca3a
    source_path: tools/video-generation.md
    workflow: 15
---

# 视频生成

`video_generate` 工具可让智能体使用你已配置的提供商创建视频。生成的视频会作为媒体附件自动随智能体的回复一并发送。

<Note>
只有在至少有一个视频生成提供商可用时，此工具才会出现。如果你在智能体工具中看不到 `video_generate`，请配置 `agents.defaults.videoGenerationModel` 或设置提供商 API 密钥。
</Note>

## 快速开始

1. 为至少一个提供商设置 API 密钥（例如 `OPENAI_API_KEY`、`GEMINI_API_KEY`、`MODELSTUDIO_API_KEY` 或 `QWEN_API_KEY`）。
2. 可选：设置你偏好的模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: "qwen/wan2.6-t2v",
    },
  },
}
```

3. 向智能体提问：_“生成一段 5 秒钟的电影感视频，内容是一只友好的龙虾在日落时分冲浪。”_

智能体会自动调用 `video_generate`。无需将其加入工具允许列表——当提供商可用时，它默认启用。

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
| Together | `Wan-AI/Wan2.2-T2V-A14B`        | 1 张图片           | `TOGETHER_API_KEY`                                         |
| xAI    | `grok-imagine-video`            | 1 张图片或 1 个视频 | `XAI_API_KEY`                                              |

使用 `action: "list"` 可在运行时查看可用的提供商和模型：

```
/tool video_generate action=list
```

## 工具参数

| 参数              | 类型     | 描述                                                                                |
| ----------------- | -------- | ----------------------------------------------------------------------------------- |
| `prompt`          | string   | 视频生成提示词（`action: "generate"` 时必填）                                       |
| `action`          | string   | `"generate"`（默认）或 `"list"`，用于查看提供商                                     |
| `model`           | string   | 提供商/模型覆盖，例如 `qwen/wan2.6-t2v`                                             |
| `image`           | string   | 单个参考图片路径或 URL                                                              |
| `images`          | string[] | 多个参考图片（最多 5 张）                                                           |
| `video`           | string   | 单个参考视频路径或 URL                                                              |
| `videos`          | string[] | 多个参考视频（最多 4 个）                                                           |
| `size`            | string   | 当提供商支持时的尺寸提示                                                            |
| `aspectRatio`     | string   | 宽高比：`1:1`、`2:3`、`3:2`、`3:4`、`4:3`、`4:5`、`5:4`、`9:16`、`16:9`、`21:9` |
| `resolution`      | string   | 分辨率提示：`480P`、`720P` 或 `1080P`                                               |
| `durationSeconds` | number   | 目标时长（秒）                                                                      |
| `audio`           | boolean  | 当提供商支持时，启用生成音频                                                        |
| `watermark`       | boolean  | 当支持时，切换提供商水印                                                            |
| `filename`        | string   | 输出文件名提示                                                                      |

并非所有提供商都支持所有参数。该工具会在提交请求前验证提供商能力限制。

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
4. **自动检测** —— 仅使用有凭证支持的默认提供商：
   - 先使用当前默认提供商
   - 再按提供商 ID 顺序使用其余已注册的视频生成提供商

如果某个提供商失败，会自动尝试下一个候选项。如果全部失败，错误信息会包含每次尝试的详细信息。

## 提供商说明

- Alibaba 使用 DashScope / Model Studio 异步视频端点，目前要求参考资源使用远程 `http(s)` URL。
- Google 使用 Gemini/Veo，支持单个图片或视频参考输入。
- MiniMax、Together、BytePlus（国际版）和 fal 当前支持单个图片参考输入。
- OpenAI 使用原生视频端点，目前默认使用 `sora-2`。
- Qwen 支持图片/视频参考，但上游 DashScope 视频端点目前要求这些参考使用远程 `http(s)` URL。
- xAI 使用原生 xAI 视频 API，支持文生视频、图生视频，以及远程视频编辑/扩展流程。

## Qwen 参考输入

内置的 Qwen 提供商支持文生视频以及图片/视频参考模式，但上游 DashScope 视频端点目前要求参考输入必须为**远程 http(s) URL**。本地文件路径和上传的缓冲区会在前置检查时直接被拒绝，而不是被静默忽略。

## 相关内容

- [工具概览](/zh-CN/tools) — 所有可用的智能体工具
- [Qwen](/zh-CN/providers/qwen) — Qwen 专属设置与限制
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults) — `videoGenerationModel` 配置
- [模型](/zh-CN/concepts/models) — 模型配置与故障切换
