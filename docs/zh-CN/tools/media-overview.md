---
read_when:
    - 正在查找媒体能力概览
    - 正在决定应配置哪个媒体 provider
    - 想了解异步媒体生成是如何工作的
summary: 媒体生成、理解和语音能力的统一落地页
title: 媒体概览
x-i18n:
    generated_at: "2026-04-06T15:31:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfee08eb91ec3e827724c8fa99bff7465356f6f1ac1b146562f35651798e3fd6
    source_path: tools/media-overview.md
    workflow: 15
---

# 媒体生成与理解

OpenClaw 可以生成图像、视频和音乐，理解传入媒体（图像、音频、视频），并通过文本转语音将回复朗读出来。所有媒体能力都由工具驱动：智能体会根据对话决定何时使用它们，并且只有在至少配置了一个对应 provider 时，相应工具才会出现。

## 能力一览

| 能力 | 工具 | Providers | 功能说明 |
| -------------------- | ---------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------- |
| 图像生成 | `image_generate` | ComfyUI、fal、Google、MiniMax、OpenAI、Vydra | 根据文本提示词或参考内容创建或编辑图像 |
| 视频生成 | `video_generate` | Alibaba、BytePlus（国际版）、ComfyUI、fal、Google、MiniMax、OpenAI、Qwen、Runway、Together、Vydra、xAI | 根据文本、图像或现有视频创建视频 |
| 音乐生成 | `music_generate` | ComfyUI、Google、MiniMax | 根据文本提示词创建音乐或音轨 |
| 文本转语音（TTS） | `tts` | ElevenLabs、Microsoft、MiniMax、OpenAI | 将输出回复转换为语音音频 |
| 媒体理解 | （自动） | 任何具备视觉/音频能力的模型 provider，以及 CLI 回退 | 总结传入的图像、音频和视频 |

## Provider 能力矩阵

此表展示了各 provider 在整个平台上支持哪些媒体能力。

| Provider | 图像 | 视频 | 音乐 | TTS | STT / 转录 | 媒体理解 |
| ---------- | ----- | ----- | ----- | --- | ------------------- | ------------------- |
| Alibaba    |       | Yes   |       |     |                     |                     |
| BytePlus   |       | Yes   |       |     |                     |                     |
| ComfyUI    | Yes   | Yes   | Yes   |     |                     |                     |
| Deepgram   |       |       |       |     | Yes                 |                     |
| ElevenLabs |       |       |       | Yes |                     |                     |
| fal        | Yes   | Yes   |       |     |                     |                     |
| Google     | Yes   | Yes   | Yes   |     |                     | Yes                 |
| Microsoft  |       |       |       | Yes |                     |                     |
| MiniMax    | Yes   | Yes   | Yes   | Yes |                     |                     |
| OpenAI     | Yes   | Yes   |       | Yes | Yes                 | Yes                 |
| Qwen       |       | Yes   |       |     |                     |                     |
| Runway     |       | Yes   |       |     |                     |                     |
| Together   |       | Yes   |       |     |                     |                     |
| Vydra      | Yes   | Yes   |       |     |                     |                     |
| xAI        |       | Yes   |       |     |                     |                     |

<Note>
媒体理解会使用你在 provider 配置中注册的任何具备视觉能力或音频能力的模型。上表重点标出了具备专用媒体理解支持的 provider；大多数带有多模态模型的 LLM provider（Anthropic、Google、OpenAI 等）在被配置为当前活动回复模型时，也能够理解传入媒体。
</Note>

## 异步生成如何工作

视频和音乐生成会作为后台任务运行，因为 provider 处理通常需要 30 秒到数分钟。当智能体调用 `video_generate` 或 `music_generate` 时，OpenClaw 会将请求提交给 provider，立即返回任务 ID，并在任务账本中跟踪该作业。作业运行期间，智能体会继续响应其他消息。当 provider 完成后，OpenClaw 会唤醒智能体，使其能够将完成的媒体发布回原始渠道。图像生成和 TTS 是同步的，会在回复过程中内联完成。

## 快速链接

- [图像生成](/zh-CN/tools/image-generation) -- 生成和编辑图像
- [视频生成](/zh-CN/tools/video-generation) -- text-to-video、image-to-video 和 video-to-video
- [音乐生成](/zh-CN/tools/music-generation) -- 创建音乐和音轨
- [文本转语音](/zh-CN/tools/tts) -- 将回复转换为语音音频
- [媒体理解](/zh-CN/nodes/media-understanding) -- 理解传入的图像、音频和视频
