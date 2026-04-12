---
read_when:
    - 你想将 QMD 设置为你的记忆后端
    - 你想要高级记忆功能，例如重排序或额外的索引路径
summary: 本地优先的搜索 sidecar，支持 BM25、向量、重排序和查询扩展
title: QMD Memory Engine
x-i18n:
    generated_at: "2026-04-12T17:53:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27afc996b959d71caed964a3cae437e0e29721728b30ebe7f014db124c88da04
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# QMD Memory Engine

[QMD](https://github.com/tobi/qmd) 是一个与 OpenClaw 一起运行的本地优先搜索 sidecar。它将 BM25、向量搜索和重排序整合到一个二进制文件中，并且可以为你的工作区记忆文件之外的内容建立索引。

## 相比内置功能增加了什么

- **重排序和查询扩展**，以获得更好的召回效果。
- **为额外目录建立索引** —— 项目文档、团队笔记、磁盘上的任何内容。
- **为会话转录建立索引** —— 回忆更早的对话。
- **完全本地运行** —— 通过 Bun + node-llama-cpp 运行，自动下载 GGUF 模型。
- **自动回退** —— 如果 QMD 不可用，OpenClaw 会无缝回退到内置引擎。

## 入门指南

### 前提条件

- 安装 QMD：`npm install -g @tobilu/qmd` 或 `bun install -g @tobilu/qmd`
- 允许扩展的 SQLite 构建版本（在 macOS 上使用 `brew install sqlite`）。
- QMD 必须位于 Gateway 网关的 `PATH` 上。
- macOS 和 Linux 开箱即用。Windows 通过 WSL2 的支持最佳。

### 启用

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw 会在 `~/.openclaw/agents/<agentId>/qmd/` 下创建一个自包含的 QMD 主目录，并自动管理 sidecar 生命周期 —— 集合、更新和嵌入运行都会为你处理。它会优先使用当前的 QMD 集合和 MCP 查询格式，但在需要时仍会回退到旧版 `--mask` 集合标志和较旧的 MCP 工具名称。

## sidecar 的工作方式

- OpenClaw 会根据你的工作区记忆文件以及任何已配置的 `memory.qmd.paths` 创建集合，然后在启动时和定期执行 `qmd update` + `qmd embed`（默认每 5 分钟一次）。
- 默认工作区集合会跟踪 `MEMORY.md` 以及 `memory/` 目录树。小写的 `memory.md` 仍然只是启动引导回退项，而不是单独的 QMD 集合。
- 启动刷新会在后台运行，因此不会阻塞聊天启动。
- 搜索会使用配置的 `searchMode`（默认：`search`；也支持 `vsearch` 和 `query`）。如果某种模式失败，OpenClaw 会使用 `qmd query` 重试。
- 如果 QMD 完全失败，OpenClaw 会回退到内置 SQLite 引擎。

<Info>
首次搜索可能会比较慢 —— QMD 会在第一次运行 `qmd query` 时自动下载用于重排序和查询扩展的 GGUF 模型（约 2 GB）。
</Info>

## 模型覆盖

QMD 模型环境变量会从 Gateway 网关进程原样透传，因此你可以全局调整 QMD，而无需新增 OpenClaw 配置：

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

更改嵌入模型后，请重新运行嵌入，以确保索引与新的向量空间匹配。

## 为额外路径建立索引

将 QMD 指向附加目录，使其可被搜索：

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

来自额外路径的片段会在搜索结果中显示为 `qmd/<collection>/<relative-path>`。`memory_get` 能识别此前缀，并从正确的集合根目录读取。

## 为会话转录建立索引

启用会话索引以回忆更早的对话：

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

转录会以经过净化的用户/助手轮次形式导出到专用的 QMD 集合中，位置为 `~/.openclaw/agents/<id>/qmd/sessions/`。

## 搜索范围

默认情况下，QMD 搜索结果会显示在私信和渠道会话中（不包括群组）。可通过配置 `memory.qmd.scope` 来更改：

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

当范围阻止搜索时，OpenClaw 会记录一条警告日志，其中包含推导出的渠道和聊天类型，以便更容易调试空结果。

## 引用

当 `memory.citations` 为 `auto` 或 `on` 时，搜索片段会包含 `Source: <path#line>` 页脚。将 `memory.citations = "off"` 可省略该页脚，同时仍会在内部将路径传递给智能体。

## 何时使用

当你需要以下能力时，请选择 QMD：

- 通过重排序获得更高质量的结果。
- 搜索工作区之外的项目文档或笔记。
- 回忆过去的会话对话。
- 完全本地的搜索，无需 API 密钥。

对于更简单的设置，[内置引擎](/zh-CN/concepts/memory-builtin) 在无需额外依赖的情况下也能很好地工作。

## 故障排除

**找不到 QMD？** 请确保该二进制文件位于 Gateway 网关的 `PATH` 上。如果 OpenClaw 作为服务运行，请创建符号链接：
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`。

**首次搜索非常慢？** QMD 会在首次使用时下载 GGUF 模型。可使用与 OpenClaw 相同的 XDG 目录运行 `qmd query "test"` 进行预热。

**搜索超时？** 增加 `memory.qmd.limits.timeoutMs`（默认：4000ms）。对于较慢的硬件，可设置为 `120000`。

**群聊中结果为空？** 检查 `memory.qmd.scope` —— 默认仅允许私信和渠道会话。

**工作区可见的临时仓库导致 `ENAMETOOLONG` 或索引损坏？**
QMD 当前的遍历遵循底层 QMD 扫描器的行为，而不是 OpenClaw 内置的符号链接规则。在 QMD 提供循环安全遍历或显式排除控制之前，请将临时 monorepo 检出保存在 `.tmp/` 等隐藏目录下，或放在已建立索引的 QMD 根目录之外。

## 配置

有关完整配置范围（`memory.qmd.*`）、搜索模式、更新间隔、范围规则以及所有其他可调项，请参阅[记忆配置参考](/zh-CN/reference/memory-config)。
