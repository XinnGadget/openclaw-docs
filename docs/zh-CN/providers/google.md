---
read_when:
    - 你想将 Google Gemini 模型与 OpenClaw 一起使用
    - 你需要 API 密钥认证流程
summary: Google Gemini 设置（API 密钥、图像生成、媒体理解、Web 搜索）
title: Google（Gemini）
x-i18n:
    generated_at: "2026-04-05T22:22:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: c0dc6413ca67e0fe274c7fc1182cf220252aae31266a72e0b251a319d4dd286e
    source_path: providers/google.md
    workflow: 15
---

# Google（Gemini）

Google 插件通过 Google AI Studio 提供对 Gemini 模型的访问，以及通过 Gemini Grounding 提供图像生成、媒体理解（图像/音频/视频）和 Web 搜索。

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

| 能力 | 支持情况 |
| ---------------------- | ----------------- |
| 聊天补全 | 是 |
| 图像生成 | 是 |
| 图像理解 | 是 |
| 音频转录 | 是 |
| 视频理解 | 是 |
| Web 搜索（Grounding） | 是 |
| 思考/推理 | 是（Gemini 3.1+） |

## 直接复用 Gemini 缓存

对于直接调用 Gemini API 的运行（`api: "google-generative-ai"`），OpenClaw 现在会将已配置的 `cachedContent` 句柄透传给 Gemini 请求。

- 可使用 `cachedContent` 或旧版 `cached_content` 为每个模型或全局配置参数
- 如果两者同时存在，则以 `cachedContent` 为准
- 示例值：`cachedContents/prebuilt-context`
- Gemini 的缓存命中用量会从上游的 `cachedContentTokenCount` 规范化为 OpenClaw 的 `cacheRead`

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

内置的 `google` 图像生成提供商默认使用 `google/gemini-3.1-flash-image-preview`。

- 也支持 `google/gemini-3-pro-image-preview`
- 生成：每次请求最多 4 张图像
- 编辑模式：已启用，最多支持 5 张输入图像
- 几何控制：`size`、`aspectRatio` 和 `resolution`

图像生成、媒体理解和 Gemini Grounding 都保持使用 `google` 提供商 id。

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

有关共享工具参数、提供商选择和故障转移行为，请参阅 [Image Generation](/zh-CN/tools/image-generation)。

## 视频生成

内置的 `google` 插件还会通过共享的 `video_generate` 工具注册视频生成功能。

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

有关共享工具参数、提供商选择和故障转移行为，请参阅 [Video Generation](/zh-CN/tools/video-generation)。

## 环境说明

如果 Gateway 网关 作为守护进程运行（launchd/systemd），请确保该进程可以访问 `GEMINI_API_KEY`（例如，在 `~/.openclaw/.env` 中设置，或通过 `env.shellEnv` 提供）。
