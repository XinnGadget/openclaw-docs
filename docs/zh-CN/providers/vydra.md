---
read_when:
    - 你想在 OpenClaw 中使用 Vydra 媒体生成功能
    - 你需要 Vydra API 密钥设置指南
summary: 在 OpenClaw 中使用 Vydra 图像、视频和语音
title: Vydra
x-i18n:
    generated_at: "2026-04-06T01:23:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0fe999e8a5414b8a31a6d7d127bc6bcfc3b4492b8f438ab17dfa9680c5b079b7
    source_path: providers/vydra.md
    workflow: 15
---

# Vydra

内置的 Vydra 插件新增了：

- 通过 `vydra/grok-imagine` 进行图像生成
- 通过 `vydra/veo3` 和 `vydra/kling` 进行视频生成
- 通过 Vydra 基于 ElevenLabs 的 TTS 路由进行语音合成

OpenClaw 对这三项能力都使用同一个 `VYDRA_API_KEY`。

## 重要的基础 URL

请使用 `https://www.vydra.ai/api/v1`。

Vydra 的顶级主机（`https://vydra.ai/api/v1`）当前会重定向到 `www`。某些 HTTP 客户端会在这种跨主机重定向中丢弃 `Authorization`，从而让原本有效的 API 密钥表现为具有误导性的身份验证失败。内置插件会直接使用 `www` 基础 URL 以避免这个问题。

## 设置

交互式新手引导：

```bash
openclaw onboard --auth-choice vydra-api-key
```

或者直接设置环境变量：

```bash
export VYDRA_API_KEY="vydra_live_..."
```

## 图像生成

默认图像模型：

- `vydra/grok-imagine`

将其设为默认图像提供商：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "vydra/grok-imagine",
      },
    },
  },
}
```

当前内置支持仅限文生图。Vydra 托管的编辑路由需要远程图像 URL，而 OpenClaw 在内置插件中尚未添加 Vydra 专用的上传桥接。

有关共享工具行为，请参阅 [图像生成](/zh-CN/tools/image-generation)。

## 视频生成

已注册的视频模型：

- `vydra/veo3` 用于文生视频
- `vydra/kling` 用于图生视频

将 Vydra 设为默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "vydra/veo3",
      },
    },
  },
}
```

注意事项：

- `vydra/veo3` 内置时仅作为文生视频使用。
- `vydra/kling` 当前需要远程图像 URL 引用。本地文件上传会在前端直接被拒绝。
- 内置插件保持保守，不会转发未文档化的风格控制参数，例如宽高比、分辨率、水印或生成音频。

有关共享工具行为，请参阅 [视频生成](/zh-CN/tools/video-generation)。

## 语音合成

将 Vydra 设为语音提供商：

```json5
{
  messages: {
    tts: {
      provider: "vydra",
      providers: {
        vydra: {
          apiKey: "${VYDRA_API_KEY}",
          voiceId: "21m00Tcm4TlvDq8ikWAM",
        },
      },
    },
  },
}
```

默认值：

- model: `elevenlabs/tts`
- voice id: `21m00Tcm4TlvDq8ikWAM`

内置插件当前提供一个已知可用的默认语音，并返回 MP3 音频文件。

## 相关内容

- [提供商目录](/zh-CN/providers/index)
- [图像生成](/zh-CN/tools/image-generation)
- [视频生成](/zh-CN/tools/video-generation)
