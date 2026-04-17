---
read_when:
    - 你想了解哪些功能可能会调用付费 API】【。analysis to=functions.read  рацәcommentary ￣色json {"path":"/home/runner/work/docs/docs/source/AGENTS.md","offset":1,"limit":40}
    - 你需要审查密钥、费用和用量可见性
    - 你在说明 `/status` 或 `/usage` 的费用报告
summary: 审查哪些内容会花钱、使用了哪些密钥，以及如何查看用量
title: API 用量和费用
x-i18n:
    generated_at: "2026-04-13T07:24:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# API 用量与费用

本文档列出**可能调用 API 密钥的功能**以及其费用会显示在哪里。它重点介绍
OpenClaw 中可能产生提供商用量或付费 API 调用的功能。

## 费用显示位置（聊天 + CLI）

**按会话显示的费用快照**

- `/status` 会显示当前会话的模型、上下文用量以及上次回复的 token 数。
- 如果模型使用**API 密钥认证**，`/status` 还会显示上次回复的**预估费用**。
- 如果实时会话元数据较少，`/status` 可以从最新的转录用量条目中恢复 token/缓存
  计数器以及当前运行时模型标签。现有的非零实时数值仍然优先；当存储的总计缺失或更小时，
  基于提示词大小的转录总计可能会优先生效。

**按消息显示的费用页脚**

- `/usage full` 会在每条回复后附加一个用量页脚，包括**预估费用**（仅限 API 密钥）。
- `/usage tokens` 只显示 token；订阅式 OAuth/token 和 CLI 流程会隐藏美元费用。
- Gemini CLI 说明：当 CLI 返回 JSON 输出时，OpenClaw 会从
  `stats` 读取用量，将 `stats.cached` 规范化为 `cacheRead`，并在需要时根据
  `stats.input_tokens - stats.cached` 推导输入 token 数。

Anthropic 说明：Anthropic 工作人员告诉我们，OpenClaw 风格的 Claude CLI 用量
再次被允许，因此 OpenClaw 将 Claude CLI 复用和 `claude -p` 用量视为此集成的
受认可方式，除非 Anthropic 发布新的政策。
Anthropic 仍然不会提供 OpenClaw 能在 `/usage full` 中显示的按消息美元预估。

**CLI 用量窗口（提供商配额）**

- `openclaw status --usage` 和 `openclaw channels list` 会显示提供商的**用量窗口**
  （配额快照，而不是按消息计费）。
- 面向用户的输出会在各提供商之间统一为 `X% left`。
- 当前支持用量窗口的提供商：Anthropic、GitHub Copilot、Gemini CLI、
  OpenAI Codex、MiniMax、Xiaomi 和 z.ai。
- MiniMax 说明：其原始 `usage_percent` / `usagePercent` 字段表示的是剩余
  配额，因此 OpenClaw 会在显示前对其取反。如果存在按次数计数字段，则这些字段仍优先。
  如果提供商返回 `model_remains`，OpenClaw 会优先选择聊天模型条目，
  在需要时根据时间戳推导窗口标签，并在计划标签中包含模型名称。
- 这些配额窗口的用量认证在可用时来自提供商特定的钩子；否则 OpenClaw 会回退为匹配
  来自认证配置文件、环境变量或配置中的 OAuth/API 密钥凭证。

详见[Token 用量与费用](/zh-CN/reference/token-use)中的详细说明和示例。

## 如何发现密钥

OpenClaw 可以从以下位置获取凭证：

- **认证配置文件**（按智能体区分，存储在 `auth-profiles.json` 中）。
- **环境变量**（例如 `OPENAI_API_KEY`、`BRAVE_API_KEY`、`FIRECRAWL_API_KEY`）。
- **配置**（`models.providers.*.apiKey`、`plugins.entries.*.config.webSearch.apiKey`、
  `plugins.entries.firecrawl.config.webFetch.apiKey`、`memorySearch.*`、
  `talk.providers.*.apiKey`）。
- **Skills**（`skills.entries.<name>.apiKey`），它们可能会将密钥导出到 Skill 进程环境中。

## 可能会消耗密钥的功能

### 1) 核心模型响应（聊天 + 工具）

每次回复或工具调用都会使用**当前模型提供商**（OpenAI、Anthropic 等）。这是
用量和费用的主要来源。

这也包括订阅式托管提供商，它们仍会在 OpenClaw 本地 UI 之外计费，例如
**OpenAI Codex**、**Alibaba Cloud Model Studio
Coding Plan**、**MiniMax Coding Plan**、**Z.AI / GLM Coding Plan**，以及
Anthropic 的启用了 **Extra Usage** 的 OpenClaw Claude 登录路径。

有关定价配置，请参见[模型](/zh-CN/providers/models)；有关显示方式，请参见[Token 用量与费用](/zh-CN/reference/token-use)。

### 2) 媒体理解（音频/图像/视频）

在回复开始前，传入媒体可能会先被总结/转录。这会使用模型/提供商 API。

- 音频：OpenAI / Groq / Deepgram / Google / Mistral。
- 图像：OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI。
- 视频：Google / Qwen / Moonshot。

参见[媒体理解](/zh-CN/nodes/media-understanding)。

### 3) 图像和视频生成

共享生成能力也可能消耗提供商密钥：

- 图像生成：OpenAI / Google / fal / MiniMax
- 视频生成：Qwen

当 `agents.defaults.imageGenerationModel` 未设置时，图像生成可以推断
一个基于认证的提供商默认值。视频生成目前仍需要显式设置
`agents.defaults.videoGenerationModel`，例如
`qwen/wan2.6-t2v`。

参见[图像生成](/zh-CN/tools/image-generation)、[Qwen Cloud](/zh-CN/providers/qwen)
和[模型](/zh-CN/concepts/models)。

### 4) Memory 嵌入 + 语义搜索

语义 Memory 搜索在配置为远程提供商时会使用**嵌入 API**：

- `memorySearch.provider = "openai"` → OpenAI embeddings
- `memorySearch.provider = "gemini"` → Gemini embeddings
- `memorySearch.provider = "voyage"` → Voyage embeddings
- `memorySearch.provider = "mistral"` → Mistral embeddings
- `memorySearch.provider = "lmstudio"` → LM Studio embeddings（本地/自托管）
- `memorySearch.provider = "ollama"` → Ollama embeddings（本地/自托管；通常不会产生托管 API 计费）
- 如果本地 embeddings 失败，可选择回退到远程提供商

你可以通过设置 `memorySearch.provider = "local"` 保持完全本地运行（无 API 用量）。

参见[Memory](/zh-CN/concepts/memory)。

### 5) Web 搜索工具

`web_search` 可能会根据你的提供商产生用量费用：

- **Brave Search API**：`BRAVE_API_KEY` 或 `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**：`EXA_API_KEY` 或 `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**：`FIRECRAWL_API_KEY` 或 `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini（Google Search）**：`GEMINI_API_KEY` 或 `plugins.entries.google.config.webSearch.apiKey`
- **Grok（xAI）**：`XAI_API_KEY` 或 `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi（Moonshot）**：`KIMI_API_KEY`、`MOONSHOT_API_KEY` 或 `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**：`MINIMAX_CODE_PLAN_KEY`、`MINIMAX_CODING_API_KEY`、`MINIMAX_API_KEY` 或 `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web 搜索**：默认不需要密钥，但需要可访问的 Ollama 主机以及 `ollama signin`；当主机要求认证时，也可以复用普通的 Ollama 提供商 bearer 认证
- **Perplexity Search API**：`PERPLEXITY_API_KEY`、`OPENROUTER_API_KEY` 或 `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**：`TAVILY_API_KEY` 或 `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**：无密钥回退方案（无 API 计费，但为非官方且基于 HTML）
- **SearXNG**：`SEARXNG_BASE_URL` 或 `plugins.entries.searxng.config.webSearch.baseUrl`（无密钥/自托管；无托管 API 计费）

旧版 `tools.web.search.*` 提供商路径仍会通过临时兼容层加载，但它们已不再是推荐的配置入口。

**Brave Search 免费额度：** 每个 Brave 套餐都包含每月 \$5 的可续期免费额度。
Search 套餐的价格为每 1,000 次请求 \$5，因此该额度可覆盖每月
1,000 次免费请求。请在 Brave 控制台中设置用量上限，以避免意外收费。

参见[Web 工具](/zh-CN/tools/web)。

### 5) Web 抓取工具（Firecrawl）

当存在 API 密钥时，`web_fetch` 可以调用 **Firecrawl**：

- `FIRECRAWL_API_KEY` 或 `plugins.entries.firecrawl.config.webFetch.apiKey`

如果未配置 Firecrawl，该工具会回退为直接抓取 + readability（不使用付费 API）。

参见[Web 工具](/zh-CN/tools/web)。

### 6) 提供商用量快照（状态/健康）

某些状态命令会调用**提供商用量端点**来显示配额窗口或认证健康状态。
这些通常是低频调用，但仍会访问提供商 API：

- `openclaw status --usage`
- `openclaw models status --json`

参见[模型 CLI](/cli/models)。

### 7) 压缩保护摘要

压缩保护功能可以使用**当前模型**来总结会话历史，这会在运行时
调用提供商 API。

参见[会话管理 + 压缩](/zh-CN/reference/session-management-compaction)。

### 8) 模型扫描 / 探测

`openclaw models scan` 可以探测 OpenRouter 模型，并会在
启用探测时使用 `OPENROUTER_API_KEY`。

参见[模型 CLI](/cli/models)。

### 9) Talk（语音）

Talk 模式在配置后可以调用 **ElevenLabs**：

- `ELEVENLABS_API_KEY` 或 `talk.providers.elevenlabs.apiKey`

参见[Talk 模式](/zh-CN/nodes/talk)。

### 10) Skills（第三方 API）

Skills 可以在 `skills.entries.<name>.apiKey` 中存储 `apiKey`。如果某个 Skill 使用该密钥访问外部
API，就可能根据该 Skill 的提供商产生费用。

参见[Skills](/zh-CN/tools/skills)。
