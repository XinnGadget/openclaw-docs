---
read_when:
    - 你想在 OpenClaw 中使用 Google Gemini 模型
    - 你需要 API 密钥认证流程
summary: Google Gemini 设置（API 密钥、图像生成、媒体理解、网页搜索）
title: Google（Gemini）
x-i18n:
    generated_at: "2026-04-06T00:51:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 358d33a68275b01ebd916a3621dd651619cb9a1d062e2fb6196a7f3c501c015a
    source_path: providers/google.md
    workflow: 15
---

# Google（Gemini）

Google 插件通过 Google AI Studio 提供对 Gemini 模型的访问，并通过
Gemini Grounding 提供图像生成、媒体理解（图像/音频/视频）和网页搜索功能。

- 提供商：`google`
- 认证：`GEMINI_API_KEY` 或 `GOOGLE_API_KEY`
- API：Google Gemini API

## 快速开始

1. 设置 API 密钥：

```bash
openclaw onboard --auth-choice gemini-api-key
```

2. 设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "google/gemini-3.1-pro-preview" },
    },
  },
}
```

## 非交互式示例

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice gemini-api-key \
  --gemini-api-key "$GEMINI_API_KEY"
```

## 功能

| 功能 | 支持情况 |
| ---------------------- | ----------------- |
| 聊天补全 | 是 |
| 图像生成 | 是 |
| 音乐生成 | 是 |
| 图像理解 | 是 |
| 音频转写 | 是 |
| 视频理解 | 是 |
| 网页搜索（Grounding） | 是 |
| 思考/推理 | 是（Gemini 3.1+） |

## 直接复用 Gemini 缓存

对于直接使用 Gemini API 的运行（`api: "google-generative-ai"`），OpenClaw 现在会
将已配置的 `cachedContent` 句柄传递给 Gemini 请求。

- 可通过 `cachedContent` 或旧版的 `cached_content`
  为每个模型或全局参数进行配置
- 如果两者同时存在，则 `cachedContent` 优先
- 示例值：`cachedContents/prebuilt-context`
- Gemini 的缓存命中用量会从上游的 `cachedContentTokenCount`
  统一归一化到 OpenClaw 的 `cacheRead`

示例：

```json5
{
  agents: {
    defaults: {
      models: {
        "google/gemini-2.5-pro": {
          params: {
            cachedContent: "cachedContents/prebuilt-context",
          },
        },
      },
    },
  },
}
```

## 图像生成

内置的 `google` 图像生成提供商默认使用
`google/gemini-3.1-flash-image-preview`。

- 也支持 `google/gemini-3-pro-image-preview`
- 生成：每次请求最多 4 张图像
- 编辑模式：已启用，最多支持 5 张输入图像
- 几何控制：`size`、`aspectRatio` 和 `resolution`

图像生成、媒体理解和 Gemini Grounding 都继续使用
`google` 提供商 id。

要将 Google 用作默认图像提供商：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "google/gemini-3.1-flash-image-preview",
      },
    },
  },
}
```

参见 [图像生成](/zh-CN/tools/image-generation)，了解共享工具参数、
提供商选择和故障切换行为。

## 视频生成

内置的 `google` 插件还通过共享的
`video_generate` 工具注册了视频生成功能。

- 默认视频模型：`google/veo-3.1-fast-generate-preview`
- 模式：文生视频、图生视频，以及单视频参考流程
- 支持 `aspectRatio`、`resolution` 和 `audio`
- 当前时长限制：**4 到 8 秒**

要将 Google 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "google/veo-3.1-fast-generate-preview",
      },
    },
  },
}
```

参见 [视频生成](/zh-CN/tools/video-generation)，了解共享工具参数、
提供商选择和故障切换行为。

## 音乐生成

内置的 `google` 插件还通过共享的
`music_generate` 工具注册了音乐生成功能。

- 默认音乐模型：`google/lyria-3-clip-preview`
- 也支持 `google/lyria-3-pro-preview`
- 提示词控制：`lyrics` 和 `instrumental`
- 输出格式：默认 `mp3`，此外 `google/lyria-3-pro-preview` 还支持 `wav`
- 参考输入：最多 10 张图像
- 基于会话的运行会通过共享的任务/状态流程分离执行，包括 `action: "status"`

要将 Google 用作默认音乐提供商：

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

参见 [音乐生成](/zh-CN/tools/music-generation)，了解共享工具参数、
提供商选择和故障切换行为。

## 环境说明

如果 Gateway 网关 以守护进程方式运行（launchd/systemd），请确保 `GEMINI_API_KEY`
对该进程可用（例如放在 `~/.openclaw/.env` 中，或通过
`env.shellEnv` 提供）。
