---
read_when:
    - 你想在 OpenClaw 中使用 MiniMax 模型
    - 你需要 MiniMax 设置指南
summary: 在 OpenClaw 中使用 MiniMax 模型
title: MiniMax
x-i18n:
    generated_at: "2026-04-05T22:23:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 32e737d8eb9b9728ec3925f626599bb4be6d0904b6357b29c6f33a315600fef4
    source_path: providers/minimax.md
    workflow: 15
---

# MiniMax

OpenClaw 的 MiniMax 提供商默认使用 **MiniMax M2.7**。

MiniMax 还提供：

- 通过 T2A v2 内置语音合成
- 通过 `MiniMax-VL-01` 内置图像理解
- 通过 MiniMax Coding Plan 搜索 API 内置 `web_search`

提供商划分：

- `minimax`：基于 API 密钥的文本提供商，另含内置图像生成、图像理解、语音和 Web 搜索
- `minimax-portal`：基于 OAuth 的文本提供商，另含内置图像生成和图像理解

## 模型阵容

- `MiniMax-M2.7`：默认托管推理模型。
- `MiniMax-M2.7-highspeed`：更快的 M2.7 推理层级。
- `image-01`：图像生成模型（生成和图生图编辑）。

## 图像生成

MiniMax 插件为 `image_generate` 工具注册了 `image-01` 模型。它支持：

- 可控制宽高比的**文生图生成**。
- 可控制宽高比的**图生图编辑**（主体参考）。
- 每次请求最多 **9 张输出图像**。
- 每次编辑请求最多 **1 张参考图像**。
- 支持的宽高比：`1:1`、`16:9`、`4:3`、`3:2`、`2:3`、`3:4`、`9:16`、`21:9`。

要将 MiniMax 用于图像生成，请将其设置为图像生成提供商：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: { primary: "minimax/image-01" },
    },
  },
}
```

该插件对文本模型使用相同的 `MINIMAX_API_KEY` 或 OAuth 认证。如果 MiniMax 已经设置完成，则无需额外配置。

`minimax` 和 `minimax-portal` 都使用相同的 `image-01` 模型注册了 `image_generate`。
基于 API 密钥的设置使用 `MINIMAX_API_KEY`；基于 OAuth 的设置则可以改用
内置的 `minimax-portal` 认证路径。

当新手引导或 API 密钥设置写入显式的 `models.providers.minimax`
条目时，OpenClaw 会具体生成 `MiniMax-M2.7` 和
`MiniMax-M2.7-highspeed`，并带有 `input: ["text", "image"]`。

内置的 MiniMax 文本目录本身仍然保持为仅文本元数据，
直到该显式提供商配置存在为止。图像理解则通过插件自有的
`MiniMax-VL-01` 媒体提供商单独公开。

有关共享工具参数、提供商选择和故障切换行为，请参见
[图像生成](/zh-CN/tools/image-generation)。

## 视频生成

内置的 `minimax` 插件还通过共享的
`video_generate` 工具注册了视频生成功能。

- 默认视频模型：`minimax/MiniMax-Hailuo-2.3`
- 模式：文生视频和单图参考流程
- 支持 `aspectRatio` 和 `resolution`

要将 MiniMax 用作默认视频提供商：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "minimax/MiniMax-Hailuo-2.3",
      },
    },
  },
}
```

有关共享工具参数、提供商选择和故障切换行为，请参见
[视频生成](/zh-CN/tools/video-generation)。

## 图像理解

MiniMax 插件将图像理解与文本目录分开注册：

- `minimax`：默认图像模型 `MiniMax-VL-01`
- `minimax-portal`：默认图像模型 `MiniMax-VL-01`

这就是为什么自动媒体路由即使在内置文本提供商目录仍显示为
仅文本的 M2.7 聊天引用时，也可以使用 MiniMax 图像理解。

## Web 搜索

MiniMax 插件还通过 MiniMax Coding Plan
搜索 API 注册了 `web_search`。

- 提供商 ID：`minimax`
- 结构化结果：标题、URL、摘要、相关查询
- 首选环境变量：`MINIMAX_CODE_PLAN_KEY`
- 可接受的环境变量别名：`MINIMAX_CODING_API_KEY`
- 兼容性回退：当 `MINIMAX_API_KEY` 已指向 coding-plan 令牌时使用它
- 区域复用：`plugins.entries.minimax.config.webSearch.region`，然后是 `MINIMAX_API_HOST`，再然后是 MiniMax 提供商基础 URL
- 搜索始终保留在提供商 ID `minimax` 上；OAuth 中国区 / 全球设置仍可通过 `models.providers.minimax-portal.baseUrl` 间接引导区域

配置位于 `plugins.entries.minimax.config.webSearch.*` 下。
请参见 [MiniMax 搜索](/zh-CN/tools/minimax-search)。

## 选择一种设置方式

### MiniMax OAuth（Coding Plan）- 推荐

**最适合：** 通过 OAuth 快速设置 MiniMax Coding Plan，无需 API 密钥。

使用显式的区域 OAuth 选项进行认证：

```bash
openclaw onboard --auth-choice minimax-global-oauth
# 或
openclaw onboard --auth-choice minimax-cn-oauth
```

选项映射：

- `minimax-global-oauth`：国际用户（`api.minimax.io`）
- `minimax-cn-oauth`：中国用户（`api.minimaxi.com`）

详情请参见 OpenClaw 仓库中的 MiniMax 插件包 README。

### MiniMax M2.7（API 密钥）

**最适合：** 使用带有 Anthropic 兼容 API 的托管 MiniMax。

通过 CLI 配置：

- 交互式新手引导：

```bash
openclaw onboard --auth-choice minimax-global-api
# 或
openclaw onboard --auth-choice minimax-cn-api
```

- `minimax-global-api`：国际用户（`api.minimax.io`）
- `minimax-cn-api`：中国用户（`api.minimaxi.com`）

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "minimax/MiniMax-M2.7" } } },
  models: {
    mode: "merge",
    providers: {
      minimax: {
        baseUrl: "https://api.minimax.io/anthropic",
        apiKey: "${MINIMAX_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "MiniMax-M2.7",
            name: "MiniMax M2.7",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.3, output: 1.2, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
          {
            id: "MiniMax-M2.7-highspeed",
            name: "MiniMax M2.7 Highspeed",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0.6, output: 2.4, cacheRead: 0.06, cacheWrite: 0.375 },
            contextWindow: 204800,
            maxTokens: 131072,
          },
        ],
      },
    },
  },
}
```

在 Anthropic 兼容的流式传输路径上，OpenClaw 现在默认禁用 MiniMax
的 thinking，除非你自己明确设置了 `thinking`。MiniMax 的
流式端点会以 OpenAI 风格的 delta 分块发出 `reasoning_content`，
而不是原生的 Anthropic thinking 块，如果默认隐式启用，
可能会把内部推理泄露到可见输出中。

### 将 MiniMax M2.7 用作回退模型（示例）

**最适合：** 将你最强的最新一代模型保留为主模型，并在失败时回退到 MiniMax M2.7。
下面的示例使用 Opus 作为具体主模型；请替换为你偏好的最新一代主模型。

```json5
{
  env: { MINIMAX_API_KEY: "sk-..." },
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": { alias: "primary" },
        "minimax/MiniMax-M2.7": { alias: "minimax" },
      },
      model: {
        primary: "anthropic/claude-opus-4-6",
        fallbacks: ["minimax/MiniMax-M2.7"],
      },
    },
  },
}
```

## 通过 `openclaw configure` 配置

使用交互式配置向导，无需编辑 JSON 即可设置 MiniMax：

1. 运行 `openclaw configure`。
2. 选择 **Model/auth**。
3. 选择一个 **MiniMax** 认证选项。
4. 在提示时选择你的默认模型。

向导 / CLI 中当前可用的 MiniMax 认证选项：

- `minimax-global-oauth`
- `minimax-cn-oauth`
- `minimax-global-api`
- `minimax-cn-api`

## 配置选项

- `models.providers.minimax.baseUrl`：优先使用 `https://api.minimax.io/anthropic`（Anthropic 兼容）；`https://api.minimax.io/v1` 可选，用于 OpenAI 兼容载荷。
- `models.providers.minimax.api`：优先使用 `anthropic-messages`；`openai-completions` 可选，用于 OpenAI 兼容载荷。
- `models.providers.minimax.apiKey`：MiniMax API 密钥（`MINIMAX_API_KEY`）。
- `models.providers.minimax.models`：定义 `id`、`name`、`reasoning`、`contextWindow`、`maxTokens`、`cost`。
- `agents.defaults.models`：为你想加入 allowlist 的模型设置别名。
- `models.mode`：如果你想在内置模型旁添加 MiniMax，请保持为 `merge`。

## 说明

- 模型引用遵循认证路径：
  - API 密钥设置：`minimax/<model>`
  - OAuth 设置：`minimax-portal/<model>`
- 默认聊天模型：`MiniMax-M2.7`
- 备用聊天模型：`MiniMax-M2.7-highspeed`
- 在 `api: "anthropic-messages"` 下，OpenClaw 会注入
  `thinking: { type: "disabled" }`，除非 thinking 已在
  params / config 中被显式设置。
- `/fast on` 或 `params.fastMode: true` 会在 Anthropic 兼容流式路径上
  将 `MiniMax-M2.7` 重写为 `MiniMax-M2.7-highspeed`。
- 新手引导和直接 API 密钥设置会为两个 M2.7 变体写入显式模型定义，
  并带有 `input: ["text", "image"]`
- 在显式 MiniMax 提供商配置存在之前，
  内置提供商目录当前会将聊天引用公开为仅文本元数据
- Coding Plan 用量 API：`https://api.minimaxi.com/v1/api/openplatform/coding_plan/remains`（需要 coding plan 密钥）。
- OpenClaw 会将 MiniMax coding-plan 用量标准化为与其他提供商相同的
  “% left” 显示。MiniMax 原始的 `usage_percent` / `usagePercent`
  字段表示的是剩余额度，而不是已消耗额度，因此 OpenClaw 会对其取反。
  如果存在按次数统计的字段，则优先使用这些字段。当 API 返回 `model_remains` 时，
  OpenClaw 会优先选择聊天模型条目，并在需要时从
  `start_time` / `end_time` 推导窗口标签，同时在计划标签中包含所选模型名称，
  以便更容易区分 coding-plan 窗口。
- 用量快照会将 `minimax`、`minimax-cn` 和 `minimax-portal` 视为
  同一个 MiniMax 配额面，并优先使用已存储的 MiniMax OAuth，
  然后才回退到 Coding Plan 密钥环境变量。
- 如果你需要精确的成本跟踪，请更新 `models.json` 中的定价值。
- MiniMax Coding Plan 推荐链接（9 折优惠）：[https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link](https://platform.minimax.io/subscribe/coding-plan?code=DbXJTRClnb&source=link)
- 有关提供商规则，请参见 [/concepts/model-providers](/zh-CN/concepts/model-providers)。
- 使用 `openclaw models list` 确认当前提供商 ID，然后通过
  `openclaw models set minimax/MiniMax-M2.7` 或
  `openclaw models set minimax-portal/MiniMax-M2.7` 切换。

## 故障排除

### “Unknown model: minimax/MiniMax-M2.7”

这通常意味着**MiniMax 提供商未配置**（没有匹配的
provider 条目，也没有找到 MiniMax 认证配置文件 / 环境变量密钥）。
针对这一检测问题的修复已包含在 **2026.1.12** 中。可通过以下方式修复：

- 升级到 **2026.1.12**（或从源码 `main` 运行），然后重启 Gateway 网关。
- 运行 `openclaw configure` 并选择一个 **MiniMax** 认证选项，或
- 手动添加匹配的 `models.providers.minimax` 或
  `models.providers.minimax-portal` 配置块，或
- 设置 `MINIMAX_API_KEY`、`MINIMAX_OAUTH_TOKEN` 或 MiniMax 认证配置文件，
  以便注入匹配的提供商。

请确保模型 ID **区分大小写**：

- API 密钥路径：`minimax/MiniMax-M2.7` 或 `minimax/MiniMax-M2.7-highspeed`
- OAuth 路径：`minimax-portal/MiniMax-M2.7` 或
  `minimax-portal/MiniMax-M2.7-highspeed`

然后使用以下命令再次检查：

```bash
openclaw models list
```
