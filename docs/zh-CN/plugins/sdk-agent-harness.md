---
read_when:
    - 你正在更改嵌入式智能体运行时或 harness 注册表
    - 你正在从内置或受信任的插件注册一个智能体 harness
    - 你需要了解 Codex 插件与模型提供商之间的关系
sidebarTitle: Agent Harness
summary: 用于替换底层嵌入式智能体执行器的实验性插件 SDK 接口
title: 智能体 Harness 插件
x-i18n:
    generated_at: "2026-04-10T20:28:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3afa7d81ca5a34f40da63e01bb9b42aa10ff8d6f92c2f78bf2588f1a71b5bc0e
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# 智能体 Harness 插件

**智能体 harness** 是一个已准备好的 OpenClaw 智能体单次轮次的底层执行器。它不是模型提供商，不是渠道，也不是工具注册表。

仅将此接口用于内置或受信任的原生插件。该契约仍处于实验阶段，因为其参数类型有意与当前的嵌入式运行器保持一致。

## 何时使用 harness

当某个模型家族拥有自己的原生会话运行时，而常规的 OpenClaw 提供商传输层并不是合适抽象时，请注册一个智能体 harness。

示例：

- 拥有线程和压缩能力的原生编码智能体服务器
- 必须流式传输原生计划 / 推理 / 工具事件的本地 CLI 或守护进程
- 除 OpenClaw 会话转录之外，还需要自身 resume id 的模型运行时

不要仅仅为了添加一个新的 LLM API 而注册 harness。对于常规的 HTTP 或 WebSocket 模型 API，请构建一个[提供商插件](/zh-CN/plugins/sdk-provider-plugins)。

## 核心仍负责的内容

在选择 harness 之前，OpenClaw 已经解析了：

- 提供商和模型
- 运行时认证状态
- thinking level 和上下文预算
- OpenClaw transcript / session 文件
- 工作区、沙箱和工具策略
- 渠道回复回调和流式回调
- 模型回退和实时模型切换策略

这种划分是有意设计的。harness 负责运行一个已准备好的尝试；它不负责选择提供商，不替代渠道投递，也不会静默切换模型。

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

OpenClaw 会在提供商 / 模型解析之后选择一个 harness：

1. `OPENCLAW_AGENT_RUNTIME=<id>` 会强制使用具有该 id 的已注册 harness。
2. `OPENCLAW_AGENT_RUNTIME=pi` 会强制使用内置的 PI harness。
3. `OPENCLAW_AGENT_RUNTIME=auto` 会让已注册的 harness 询问自己是否支持已解析的提供商 / 模型。
4. 如果没有匹配的已注册 harness，OpenClaw 会使用 PI，除非已禁用 PI 回退。

强制使用插件 harness 时的失败会作为运行失败暴露出来。在 `auto` 模式下，如果所选插件 harness 在某一轮产生副作用之前失败，OpenClaw 可能会回退到 PI。将 `OPENCLAW_AGENT_HARNESS_FALLBACK=none` 或 `embeddedHarness.fallback: "none"` 设置为禁用回退，即可让该回退变成硬失败。

内置 Codex 插件将 `codex` 注册为其 harness id。为保持兼容性，当你手动设置 `OPENCLAW_AGENT_RUNTIME` 时，`codex-app-server` 和 `app-server` 也会解析到同一个 harness。

## 提供商与 harness 配对

大多数 harness 也应注册一个提供商。该提供商会将模型引用、认证状态、模型元数据和 `/model` 选择暴露给 OpenClaw 的其余部分。随后，harness 会在 `supports(...)` 中声明该提供商。

内置 Codex 插件遵循这一模式：

- provider id：`codex`
- 用户模型引用：`codex/gpt-5.4`、`codex/gpt-5.2`，或 Codex app server 返回的其他模型
- harness id：`codex`
- 认证：合成提供商可用性，因为 Codex harness 负责原生 Codex 登录 / 会话
- app-server 请求：OpenClaw 会将裸模型 id 发送给 Codex，并让 harness 与原生 app-server 协议通信

Codex 插件是增量式的。普通的 `openai/gpt-*` 引用仍然是 OpenAI 提供商引用，并继续使用常规的 OpenClaw 提供商路径。当你需要 Codex 管理的认证、Codex 模型发现、原生线程和 Codex app-server 执行时，请选择 `codex/gpt-*`。`/model` 可以在 Codex app server 返回的 Codex 模型之间切换，而无需 OpenAI 提供商凭证。

OpenClaw 要求 Codex app-server 版本为 `0.118.0` 或更高。Codex 插件会检查 app-server initialize 握手，并阻止较旧或未标明版本的服务器，以确保 OpenClaw 仅针对其已测试的协议接口运行。

## 禁用 PI 回退

默认情况下，OpenClaw 运行嵌入式智能体时，`agents.defaults.embeddedHarness` 设置为 `{ runtime: "auto", fallback: "pi" }`。在 `auto` 模式下，已注册的插件 harness 可以声明某个提供商 / 模型对。如果没有任何匹配项，或者自动选择的插件 harness 在产生输出之前失败，OpenClaw 会回退到 PI。

当你需要证明插件 harness 是唯一正在运行的运行时时，请设置 `fallback: "none"`。这会禁用自动 PI 回退；但不会阻止显式的 `runtime: "pi"` 或 `OPENCLAW_AGENT_RUNTIME=pi`。

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

如果你希望任何已注册的插件 harness 都能声明匹配的模型，但又不希望 OpenClaw 静默回退到 PI，请保持 `runtime: "auto"` 并禁用回退：

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

`OPENCLAW_AGENT_RUNTIME` 仍会覆盖已配置的运行时。使用 `OPENCLAW_AGENT_HARNESS_FALLBACK=none` 可以从环境中禁用 PI 回退。

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

禁用回退后，如果所请求的 harness 未注册、不支持已解析的提供商 / 模型，或在产生该轮副作用之前失败，则会话会提前失败。这对于仅使用 Codex 的部署，以及必须证明 Codex app-server 路径确实在使用中的实时测试来说，是有意设计的行为。

此设置仅控制嵌入式智能体 harness。它不会禁用图像、视频、音乐、TTS、PDF 或其他提供商特定的模型路由。

## 原生会话与转录镜像

harness 可以保留原生 session id、thread id 或守护进程侧的 resume token。请将该绑定明确与 OpenClaw 会话关联，并持续将用户可见的 assistant / tool 输出镜像到 OpenClaw transcript 中。

OpenClaw transcript 仍然是以下场景的兼容层：

- 渠道可见的会话历史
- transcript 搜索与索引
- 在后续轮次切换回内置 PI harness
- 通用的 `/new`、`/reset` 和会话删除行为

如果你的 harness 存储了一个 sidecar 绑定，请实现 `reset(...)`，以便 OpenClaw 在所属的 OpenClaw 会话被重置时清除它。

## 工具和媒体结果

核心会构建 OpenClaw 工具列表，并将其传入已准备好的尝试。当 harness 执行一个动态工具调用时，请通过 harness 结果结构返回工具结果，而不是自行发送渠道媒体。

这样可以让文本、图像、视频、音乐、TTS、审批和消息工具输出与 PI 支持的运行保持在同一投递路径上。

## 当前限制

- 公共导入路径是通用的，但某些 attempt / result 类型别名仍带有 `Pi` 命名，以保持兼容性。
- 第三方 harness 安装仍处于实验阶段。在你确实需要原生会话运行时之前，请优先使用提供商插件。
- 支持跨轮次切换 harness。不要在一轮中途、当原生工具、审批、assistant 文本或消息发送已经开始后切换 harness。

## 相关内容

- [SDK 概览](/zh-CN/plugins/sdk-overview)
- [运行时辅助函数](/zh-CN/plugins/sdk-runtime)
- [提供商插件](/zh-CN/plugins/sdk-provider-plugins)
- [模型提供商](/zh-CN/concepts/model-providers)
