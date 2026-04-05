---
read_when:
    - 你想在 OpenClaw 中使用 Google Gemini 模型
    - 你需要 API 密钥认证流程
summary: Google Gemini 设置（API 密钥、图像生成、媒体理解、Web 搜索）
title: Google（Gemini）
x-i18n:
    generated_at: "2026-04-05T18:14:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0df5bcbd98e2c1dafea3e9919e9793533ba785120b24f1db12e8e35b1ad23083
    source_path: providers/google.md
    workflow: 15
---

# Google（Gemini）

Google 插件通过 Google AI Studio 提供对 Gemini 模型的访问，以及通过 Gemini Grounding 提供图像生成、媒体理解（图像/音频/视频）和 Web 搜索功能。

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
| 图像理解 | 是 |
| 音频转录 | 是 |
| 视频理解 | 是 |
| Web 搜索（Grounding） | 是 |
| Thinking/推理 | 是（Gemini 3.1+） |

## 直接复用 Gemini 缓存

对于直接 Gemini API 运行（`api: "google-generative-ai"`），OpenClaw 现在会将已配置的 `cachedContent` 句柄透传到 Gemini 请求中。

- 使用 `cachedContent` 或旧版 `cached_content` 为每个模型或全局参数进行配置
- 如果两者都存在，则 `cachedContent` 优先
- 示例值：`cachedContents/prebuilt-context`
- Gemini 缓存命中的用量会从上游 `cachedContentTokenCount` 规范化为 OpenClaw `cacheRead`

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

图像生成、媒体理解和 Gemini Grounding 都保持使用 `google` 提供商 ID。

## 环境说明

如果 Gateway 网关以守护进程（launchd/systemd）方式运行，请确保 `GEMINI_API_KEY` 对该进程可用（例如，在 `~/.openclaw/.env` 中，或通过 `env.shellEnv`）。
