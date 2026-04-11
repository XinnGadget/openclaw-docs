---
read_when:
    - 你正在更改嵌入式智能体运行时或 Harness 注册表
    - 你正在从内置或受信任的插件注册一个智能体 Harness
    - 你需要了解 Codex 插件与模型提供商之间的关系
sidebarTitle: Agent Harness
summary: 供替换底层嵌入式智能体执行器的插件使用的实验性 SDK 接口层
title: 智能体 Harness 插件
x-i18n:
    generated_at: "2026-04-11T16:15:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# 智能体 Harness 插件

**agent harness** 是为一个已准备好的 OpenClaw 智能体轮次提供底层执行的执行器。它不是模型提供商，不是渠道，也不是工具注册表。

仅将此接口层用于内置或受信任的原生插件。该契约仍然是实验性的，因为参数类型有意映射当前的嵌入式运行器。

## 何时使用 harness

当某个模型家族拥有自己的原生会话运行时，而常规的 OpenClaw 提供商传输层并不是合适抽象时，请注册一个智能体 harness。

示例：

- 拥有线程和上下文压缩能力的原生代码智能体服务器
- 必须流式传输原生计划 / 推理 / 工具事件的本地 CLI 或守护进程
- 除了 OpenClaw 会话 transcript 之外，还需要自身 resume id 的模型运行时

不要仅为了添加一个新的 LLM API 而注册 harness。对于普通的 HTTP 或 WebSocket 模型 API，请构建一个[提供商插件](/zh-CN/plugins/sdk-provider-plugins)。

## core 仍然负责的内容

在选择 harness 之前，OpenClaw 已经解析完成：

- 提供商和模型
- 运行时凭证状态
- 思考级别和上下文预算
- OpenClaw transcript / 会话文件
- workspace、沙箱和工具策略
- 渠道回复回调和流式传输回调
- 模型回退和在线模型切换策略

这种拆分是有意设计的。harness 负责运行一个已准备好的尝试；它不会选择提供商、替代渠道投递，也不会静默切换模型。

## 注册 harness

**导入：** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## 选择策略

OpenClaw 会在提供商 / 模型解析完成后选择一个 harness：

1. `OPENCLAW_AGENT_RUNTIME=<id>` 会强制使用具有该 id 的已注册 harness。
2. `OPENCLAW_AGENT_RUNTIME=pi` 会强制使用内置的 PI harness。
3. `OPENCLAW_AGENT_RUNTIME=auto` 会让已注册的 harness 询问自己是否支持已解析的提供商 / 模型。
4. 如果没有匹配的已注册 harness，OpenClaw 会使用 PI，除非已禁用 PI 回退。

强制使用插件 harness 但失败时，会表现为运行失败。在 `auto` 模式下，如果所选插件 harness 在某个轮次产生副作用之前失败，OpenClaw 可能会回退到 PI。设置 `OPENCLAW_AGENT_HARNESS_FALLBACK=none` 或 `embeddedHarness.fallback: "none"`，可以将该回退改为硬失败。

内置的 Codex 插件将 `codex` 注册为其 harness id。core 将其视为普通的插件 harness id；Codex 特有的别名应属于插件或操作员配置，而不应放在共享运行时选择器中。

## 提供商与 harness 配对

大多数 harness 也应该注册一个提供商。提供商会让模型引用、凭证状态、模型元数据以及 `/model` 选择功能对 OpenClaw 的其他部分可见。随后，harness 会在 `supports(...)` 中声明该提供商。

内置的 Codex 插件遵循此模式：

- provider id：`codex`
- 用户模型引用：`codex/gpt-5.4`、`codex/gpt-5.2`，或 Codex app server 返回的其他模型
- harness id：`codex`
- 凭证：合成的 provider 可用性，因为 Codex harness 拥有原生 Codex 登录 / 会话
- app server 请求：OpenClaw 会将裸模型 id 发送给 Codex，并让 harness 与原生 app-server 协议通信

Codex 插件是增量式的。普通的 `openai/gpt-*` 引用仍然是 OpenAI provider 引用，并继续使用常规的 OpenClaw provider 路径。当你需要 Codex 管理的凭证、Codex 模型发现、原生线程以及 Codex app-server 执行时，请选择 `codex/gpt-*`。`/model` 可以在 Codex app server 返回的 Codex 模型之间切换，而无需 OpenAI provider 凭证。

有关操作员设置、模型前缀示例和仅限 Codex 的配置，请参阅[Codex Harness](/zh-CN/plugins/codex-harness)。

OpenClaw 要求 Codex app-server 版本为 `0.118.0` 或更高。Codex 插件会检查 app-server 初始化握手，并阻止较旧或未带版本信息的服务器，以确保 OpenClaw 仅在其已测试过的协议接口层上运行。

### 原生 Codex harness 模式

内置的 `codex` harness 是嵌入式 OpenClaw 智能体轮次的原生 Codex 模式。请先启用内置 `codex` 插件；如果你的配置使用了限制性 allowlist，还需要将 `codex` 加入 `plugins.allow`。它与 `openai-codex/*` 不同：

- `openai-codex/*` 通过常规 OpenClaw provider 路径使用 ChatGPT / Codex OAuth。
- `codex/*` 使用内置的 Codex provider，并通过 Codex app-server 路由该轮次。

在此模式运行时，Codex 负责原生线程 id、resume 行为、上下文压缩和 app-server 执行。OpenClaw 仍然负责聊天渠道、可见 transcript 镜像、工具策略、审批、媒体投递和会话选择。当你需要证明使用的是 Codex app-server 路径，并且 PI 回退没有掩盖损坏的原生 harness 时，请使用 `embeddedHarness.runtime: "codex"` 并设置 `embeddedHarness.fallback: "none"`。

## 禁用 PI 回退

默认情况下，OpenClaw 使用 `agents.defaults.embeddedHarness` 设置为 `{ runtime: "auto", fallback: "pi" }` 来运行嵌入式智能体。在 `auto` 模式下，已注册的插件 harness 可以声明某个 provider / model 配对。如果没有匹配项，或者自动选择的插件 harness 在产生输出之前失败，OpenClaw 会回退到 PI。

当你需要证明某个插件 harness 是唯一被执行的运行时，请设置 `fallback: "none"`。这会禁用自动 PI 回退；但不会阻止显式的 `runtime: "pi"` 或 `OPENCLAW_AGENT_RUNTIME=pi`。

对于仅使用 Codex 的嵌入式运行：

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

如果你希望任何已注册的插件 harness 都可以声明匹配的模型，但永远不希望 OpenClaw 静默回退到 PI，请保持 `runtime: "auto"` 并禁用回退：

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

按智能体覆盖使用相同的结构：

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` 仍然会覆盖已配置的运行时。使用 `OPENCLAW_AGENT_HARNESS_FALLBACK=none` 可以通过环境变量禁用 PI 回退。

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

禁用回退后，当所请求的 harness 未注册、不支持已解析的 provider / model，或在产生轮次副作用之前失败时，会话会提前失败。对于仅使用 Codex 的部署，以及必须证明 Codex app-server 路径确实正在使用的在线测试，这是有意为之。

此设置仅控制嵌入式智能体 harness。它不会禁用图像、视频、音乐、TTS、PDF 或其他特定提供商的模型路由。

## 原生会话与 transcript 镜像

harness 可以保留原生 session id、thread id 或守护进程侧的 resume token。请将该绑定明确地与 OpenClaw 会话关联起来，并持续将用户可见的助手 / 工具输出镜像到 OpenClaw transcript 中。

OpenClaw transcript 仍然是以下场景的兼容层：

- 渠道可见的会话历史
- transcript 搜索与索引
- 在后续轮次切换回内置 PI harness
- 通用的 `/new`、`/reset` 和会话删除行为

如果你的 harness 存储了 sidecar 绑定，请实现 `reset(...)`，以便 OpenClaw 在所属 OpenClaw 会话被重置时清除它。

## 工具与媒体结果

core 会构造 OpenClaw 工具列表，并将其传入已准备好的尝试。当 harness 执行动态工具调用时，请通过 harness 结果结构返回工具结果，而不是自行发送渠道媒体。

这样可以让文本、图像、视频、音乐、TTS、审批以及消息工具输出，与 PI 支持的运行走同一条投递路径。

## 当前限制

- 公共导入路径是通用的，但某些 attempt / result 类型别名仍然保留 `Pi` 名称以保持兼容。
- 第三方 harness 安装仍属实验性。在你确实需要原生会话运行时之前，优先使用提供商插件。
- 支持跨轮次切换 harness。不要在某个轮次中途，在原生工具、审批、助手文本或消息发送已经开始后切换 harness。

## 相关内容

- [SDK 概览](/zh-CN/plugins/sdk-overview)
- [运行时辅助工具](/zh-CN/plugins/sdk-runtime)
- [提供商插件](/zh-CN/plugins/sdk-provider-plugins)
- [Codex Harness](/zh-CN/plugins/codex-harness)
- [模型提供商](/zh-CN/concepts/model-providers)
