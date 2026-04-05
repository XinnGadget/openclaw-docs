---
read_when:
    - 你想在 OpenClaw 中使用 Grok 模型
    - 你正在配置 xAI 身份验证或模型 ID
summary: 在 OpenClaw 中使用 xAI Grok 模型
title: xAI
x-i18n:
    generated_at: "2026-04-05T22:23:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 64bc899655427cc10bdc759171c7d1ec25ad9f1e4f9d803f1553d3d586c6d71d
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw 内置了一个用于 Grok 模型的 `xai` 提供商插件。

## 设置

1. 在 xAI 控制台中创建一个 API 密钥。
2. 设置 `XAI_API_KEY`，或运行：

```bash
openclaw onboard --auth-choice xai-api-key
```

3. 选择一个模型，例如：

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

OpenClaw 现在使用 xAI Responses API 作为内置 xAI 传输层。同一个
`XAI_API_KEY` 也可用于由 Grok 驱动的 `web_search`、原生的 `x_search`，
以及远程 `code_execution`。
如果你将 xAI 密钥存储在 `plugins.entries.xai.config.webSearch.apiKey` 下，
内置的 xAI 模型提供商现在也会将该密钥作为回退复用。
`code_execution` 调优配置位于 `plugins.entries.xai.config.codeExecution` 下。

## 当前内置模型目录

OpenClaw 现在开箱即用地包含以下 xAI 模型系列：

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

当较新的 `grok-4*` 和 `grok-code-fast*` ID 遵循相同的 API 形态时，
该插件也会转发解析这些 ID。

快速模型说明：

- `grok-4-fast`、`grok-4-1-fast` 以及 `grok-4.20-beta-*` 变体，是当前内置目录中支持图像能力的 Grok 引用。
- `/fast on` 或 `agents.defaults.models["xai/<model>"].params.fastMode: true`
  会将原生 xAI 请求按如下方式重写：
  - `grok-3` -> `grok-3-fast`
  - `grok-3-mini` -> `grok-3-mini-fast`
  - `grok-4` -> `grok-4-fast`
  - `grok-4-0709` -> `grok-4-fast`

旧版兼容别名仍会规范化为内置的规范 ID。例如：

- `grok-4-fast-reasoning` -> `grok-4-fast`
- `grok-4-1-fast-reasoning` -> `grok-4-1-fast`
- `grok-4.20-reasoning` -> `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` -> `grok-4.20-beta-latest-non-reasoning`

## 网页搜索

内置的 `grok` 网页搜索提供商也使用 `XAI_API_KEY`：

```bash
openclaw config set tools.web.search.provider grok
```

## 视频生成

内置的 `xai` 插件还通过共享的
`video_generate` 工具注册了视频生成功能。

- 默认视频模型：`xai/grok-imagine-video`
- 模式：文生视频、图生视频，以及远程视频编辑/延长流程
- 支持 `aspectRatio` 和 `resolution`
- 当前限制：不接受本地视频缓冲区；视频参考/编辑输入请使用远程 `http(s)`
  URL

要将 xAI 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "xai/grok-imagine-video",
      },
    },
  },
}
```

有关共享工具参数、提供商选择和故障切换行为，请参见 [视频生成](/zh-CN/tools/video-generation)。

## 已知限制

- 目前身份验证仅支持 API 密钥。OpenClaw 还不支持 xAI OAuth/设备代码流程。
- `grok-4.20-multi-agent-experimental-beta-0304` 在常规 xAI 提供商路径上不受支持，因为它所需的上游 API 接口与标准 OpenClaw xAI 传输层不同。

## 说明

- OpenClaw 会在共享运行器路径上自动应用 xAI 专用的工具模式和工具调用兼容性修复。
- 原生 xAI 请求默认使用 `tool_stream: true`。将
  `agents.defaults.models["xai/<model>"].params.tool_stream` 设置为 `false`
  可禁用它。
- 内置的 xAI 包装器会在发送原生 xAI 请求前，移除不受支持的严格工具模式标志和推理负载键。
- `web_search`、`x_search` 和 `code_execution` 会作为 OpenClaw 工具暴露。OpenClaw 会在每次工具请求中启用所需的特定 xAI 内置功能，而不是在每次聊天轮次中附加所有原生工具。
- `x_search` 和 `code_execution` 由内置 xAI 插件负责，而不是硬编码在核心模型运行时中。
- `code_execution` 是远程 xAI 沙箱执行，不是本地的 [`exec`](/zh-CN/tools/exec)。
- 关于更广泛的提供商概览，请参见 [模型提供商](/zh-CN/providers/index)。
