---
read_when:
    - 构建或调试原生 OpenClaw 插件
    - 理解插件能力模型或归属边界
    - 处理插件加载流水线或注册表
    - 实现提供商运行时钩子或渠道插件
sidebarTitle: Internals
summary: 插件内部机制：能力模型、归属、契约、加载流水线和运行时辅助函数
title: 插件内部机制
x-i18n:
    generated_at: "2026-04-06T00:55:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: d39158455701dedfb75f6c20b8c69fd36ed9841f1d92bed1915f448df57fd47b
    source_path: plugins/architecture.md
    workflow: 15
---

# 插件内部机制

<Info>
  这是**深度架构参考**。如需实用指南，请参阅：
  - [安装和使用插件](/zh-CN/tools/plugin) — 用户指南
  - [入门指南](/zh-CN/plugins/building-plugins) — 第一个插件教程
  - [渠道插件](/zh-CN/plugins/sdk-channel-plugins) — 构建一个消息渠道
  - [提供商插件](/zh-CN/plugins/sdk-provider-plugins) — 构建一个模型提供商
  - [SDK 概览](/zh-CN/plugins/sdk-overview) — 导入映射和注册 API
</Info>

本页介绍 OpenClaw 插件系统的内部架构。

## 公共能力模型

能力是 OpenClaw 内部公共的**原生插件**模型。每个
原生 OpenClaw 插件都会针对一种或多种能力类型进行注册：

| 能力                 | 注册方法                                         | 示例插件                             |
| -------------------- | ------------------------------------------------ | ------------------------------------ |
| 文本推理             | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| 语音                 | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| 实时转录             | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| 实时语音             | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| 媒体理解             | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| 图像生成             | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| 音乐生成             | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| 视频生成             | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| 网页抓取             | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| 网页搜索             | `api.registerWebSearchProvider(...)`             | `google`                             |
| 渠道 / 消息          | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

如果一个插件注册了零个能力，但提供了 hooks、工具或
服务，那么它就是一个**仅 hooks 的遗留**插件。该模式仍然受到完全支持。

### 外部兼容性立场

能力模型已经在 core 中落地，并且如今已被内置 / 原生插件使用，
但外部插件的兼容性仍需要比“它已导出，因此它已冻结”
更严格的标准。

当前指导原则：

- **现有外部插件：** 保持基于 hooks 的集成正常工作；将其视为
  兼容性基线
- **新的内置 / 原生插件：** 优先使用显式能力注册，而不是
  面向特定厂商的内部耦合，或新的仅 hooks 设计
- **采用能力注册的外部插件：** 允许这样做，但除非文档明确将某个
  契约标记为稳定，否则应将特定于能力的辅助接口视为仍在演进

实践规则：

- 能力注册 API 是目标方向
- 在过渡期间，对于外部插件来说，遗留 hooks 仍然是最安全、最不容易破坏兼容性的路径
- 并非所有导出的辅助子路径都同等稳定；优先使用有文档说明的狭窄
  契约，而不是偶然暴露出来的辅助导出

### 插件形态

OpenClaw 会根据每个已加载插件的实际注册行为来将其归类为一种形态
（而不只是依据静态元数据）：

- **plain-capability** -- 恰好注册一种能力类型（例如仅提供商
  插件 `mistral`）
- **hybrid-capability** -- 注册多种能力类型（例如
  `openai` 同时拥有文本推理、语音、媒体理解和图像
  生成）
- **hook-only** -- 只注册 hooks（类型化或自定义），不注册能力、
  工具、命令或服务
- **non-capability** -- 注册工具、命令、服务或路由，但不注册
  能力

使用 `openclaw plugins inspect <id>` 查看插件的形态及其能力
明细。详见 [CLI 参考](/cli/plugins#inspect)。

### 遗留 hooks

`before_agent_start` hook 仍作为仅 hooks 插件的兼容路径受到支持。
现实中仍有遗留插件依赖它。

方向如下：

- 保持其正常工作
- 在文档中将其标记为遗留
- 对于模型 / 提供商覆写工作，优先使用 `before_model_resolve`
- 对于提示词变更工作，优先使用 `before_prompt_build`
- 仅在真实使用量下降，且夹具覆盖证明迁移安全后才移除

### 兼容性信号

当你运行 `openclaw doctor` 或 `openclaw plugins inspect <id>` 时，你可能会看到
以下标签之一：

| 信号                     | 含义                                                      |
| ------------------------ | --------------------------------------------------------- |
| **config valid**         | 配置解析正常，插件可正常解析                              |
| **compatibility advisory** | 插件使用了受支持但较旧的模式（例如 `hook-only`）       |
| **legacy warning**       | 插件使用了已弃用的 `before_agent_start`                  |
| **hard error**           | 配置无效或插件加载失败                                    |

如今，`hook-only` 和 `before_agent_start` 都不会破坏你的插件 --
`hook-only` 只是提示，而 `before_agent_start` 只会触发警告。这些
信号也会出现在 `openclaw status --all` 和 `openclaw plugins doctor` 中。

## 架构概览

OpenClaw 的插件系统有四层：

1. **清单 + 发现**
   OpenClaw 会从已配置路径、工作区根目录、
   全局扩展根目录和内置扩展中查找候选插件。
   发现阶段会优先读取原生 `openclaw.plugin.json` 清单以及受支持的 bundle 清单。
2. **启用 + 验证**
   Core 决定一个已发现的插件是启用、禁用、阻止，还是
   被选入某个独占槽位（例如 memory）。
3. **运行时加载**
   原生 OpenClaw 插件通过 jiti 在进程内加载，并将
   能力注册到一个中央注册表中。兼容 bundle 会在不导入运行时代码的情况下，
   被标准化为注册表记录。
4. **接口消费**
   OpenClaw 的其余部分读取该注册表，以暴露工具、渠道、提供商
   设置、hooks、HTTP 路由、CLI 命令和服务。

对于插件 CLI 而言，根命令发现专门分为两个阶段：

- 解析时元数据来自 `registerCli(..., { descriptors: [...] })`
- 真正的插件 CLI 模块可以保持懒加载，并在首次调用时再注册

这样既能把插件自有的 CLI 代码保留在插件内部，又能让 OpenClaw
在解析前预留根命令名称。

重要设计边界如下：

- 发现 + 配置验证应基于**清单 / schema 元数据**
  完成，而无需执行插件代码
- 原生运行时行为来自插件模块的 `register(api)` 路径

这种拆分让 OpenClaw 能在完整运行时尚未激活前，就完成配置验证、
解释缺失 / 已禁用插件，并构建 UI / schema 提示。

### 渠道插件和共享 `message` 工具

对于常规聊天动作，渠道插件不需要单独注册 send / edit / react 工具。
OpenClaw 在 core 中保留一个共享的 `message` 工具，而
渠道插件负责其背后与渠道相关的发现和执行逻辑。

当前边界如下：

- core 负责共享 `message` 工具宿主、提示词接线、会话 / 线程
  记账，以及执行分发
- 渠道插件负责作用域化动作发现、能力发现，以及任何
  渠道特有的 schema 片段
- 渠道插件负责提供商特定的会话对话语法，例如
  会话 id 如何编码线程 id，或如何从父级对话继承
- 渠道插件通过其动作适配器执行最终动作

对于渠道插件，SDK 接口是
`ChannelMessageActionAdapter.describeMessageTool(...)`。这个统一的发现
调用允许插件将可见动作、能力和 schema
扩展一起返回，从而避免这些部分彼此漂移。

Core 会将运行时作用域传入该发现步骤。重要字段包括：

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 受信任的入站 `requesterSenderId`

这对上下文敏感型插件很重要。渠道可以根据活动账户、
当前房间 / 线程 / 消息或受信任的请求者身份，
决定隐藏或暴露消息动作，而无需在 core 的 `message` 工具中硬编码
特定于渠道的分支。

这也是为什么嵌入式 runner 路由变更仍然属于插件工作：runner
负责将当前聊天 / 会话身份转发到插件发现边界，
从而让共享的 `message` 工具在当前轮次暴露出正确的、由渠道拥有的
接口。

对于渠道自有的执行辅助函数，内置插件应将执行运行时保留在
各自的扩展模块中。Core 不再拥有位于 `src/agents/tools` 下的 Discord、
Slack、Telegram 或 WhatsApp 消息动作运行时。
我们不会发布单独的 `plugin-sdk/*-action-runtime` 子路径，而内置
插件应直接从各自扩展拥有的模块中导入本地运行时代码。

同样的边界也适用于一般意义上的提供商命名 SDK 接缝：core
不应导入面向 Slack、Discord、Signal、
WhatsApp 或类似扩展的渠道特定便捷 barrel。如果 core 需要某种行为，
要么消费内置插件自有的 `api.ts` / `runtime-api.ts` barrel，
要么将该需求提升为共享 SDK 中一个狭窄、通用的能力。

对于投票，具体有两条执行路径：

- `outbound.sendPoll` 是适用于符合通用投票模型渠道的共享基线
- `actions.handleAction("poll")` 是更推荐的路径，适用于
  渠道特定的投票语义或额外投票参数

现在，core 会先尝试插件投票分发，只有在插件拒绝该动作后，才会延迟执行共享投票解析，
这样插件自有的投票处理器就能接收特定渠道的投票字段，
而不会先被通用投票解析器阻挡。

完整启动顺序请参阅 [加载流水线](#load-pipeline)。

## 能力归属模型

OpenClaw 将一个原生插件视为一个**公司**或一个
**功能**的归属边界，而不是一堆互不相关集成的集合。

这意味着：

- 一个公司插件通常应该拥有该公司所有面向 OpenClaw 的
  接口
- 一个功能插件通常应该拥有其引入的完整功能接口
- 渠道应消费共享的 core 能力，而不是临时重复实现
  提供商行为

示例：

- 内置的 `openai` 插件拥有 OpenAI 模型提供商行为，以及 OpenAI
  的语音 + 实时语音 + 媒体理解 + 图像生成行为
- 内置的 `elevenlabs` 插件拥有 ElevenLabs 语音行为
- 内置的 `microsoft` 插件拥有 Microsoft 语音行为
- 内置的 `google` 插件拥有 Google 模型提供商行为，以及 Google
  的媒体理解 + 图像生成 + 网页搜索行为
- 内置的 `firecrawl` 插件拥有 Firecrawl 网页抓取行为
- 内置的 `minimax`、`mistral`、`moonshot` 和 `zai` 插件拥有它们各自的
  媒体理解后端
- `voice-call` 插件是一个功能插件：它拥有通话传输、工具、
  CLI、路由和 Twilio 媒体流桥接，但它消费共享的语音
  以及实时转录和实时语音能力，而不是直接导入厂商插件

目标终态是：

- OpenAI 即使横跨文本模型、语音、图像以及未来的视频，
  也只存在于一个插件中
- 其他厂商也可以对自己的能力范围采用同样方式
- 渠道不关心哪个厂商插件拥有该提供商；它们只消费 core 暴露的
  共享能力契约

这是关键区别：

- **plugin** = 归属边界
- **capability** = 可由多个插件实现或消费的 core 契约

因此，如果 OpenClaw 新增一个如视频这样的领域，第一个问题不应是
“哪个提供商应该硬编码视频处理？”第一个问题应是“什么才是
core 的视频能力契约？”一旦该契约存在，厂商插件
就可以针对它注册，而渠道 / 功能插件也可以消费它。

如果该能力尚不存在，正确做法通常是：

1. 在 core 中定义缺失的能力
2. 以类型化方式通过插件 API / 运行时将其暴露出来
3. 让渠道 / 功能接入该能力
4. 允许厂商插件注册实现

这样能让归属关系保持清晰，同时避免 core 的行为依赖于
单一厂商或一次性的插件特定代码路径。

### 能力分层

在决定代码应放在哪里时，可使用以下思维模型：

- **core 能力层**：共享编排、策略、回退、配置
  合并规则、交付语义和类型化契约
- **厂商插件层**：厂商特定 API、认证、模型目录、语音
  合成、图像生成、未来视频后端、使用量端点
- **渠道 / 功能插件层**：Slack / Discord / voice-call 等集成，
  它们消费 core 能力并将其呈现在某个接口上

例如，TTS 遵循以下形态：

- core 负责回复时的 TTS 策略、回退顺序、偏好和渠道交付
- `openai`、`elevenlabs` 和 `microsoft` 负责合成实现
- `voice-call` 消费电话 TTS 运行时辅助函数

未来能力也应优先遵循同样模式。

### 多能力公司插件示例

一个公司插件从外部看应当是连贯的。如果 OpenClaw 对模型、
语音、实时转录、实时语音、媒体理解、图像生成、视频生成、
网页抓取和网页搜索都提供了共享契约，那么一个厂商就可以在一个地方
拥有其所有接口：

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // 认证 / 模型目录 / 运行时 hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // 厂商语音配置 —— 直接实现 SpeechProviderPlugin 接口
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // 凭证 + 获取逻辑
      }),
    );
  },
};

export default plugin;
```

关键不在于具体的辅助函数名称。重要的是结构：

- 一个插件拥有该厂商接口
- core 仍然拥有能力契约
- 渠道和功能插件消费 `api.runtime.*` 辅助函数，而不是厂商代码
- 契约测试可以断言插件已注册其所宣称拥有的能力

### 能力示例：视频理解

OpenClaw 已经将图像 / 音频 / 视频理解视为一种共享
能力。相同的归属模型也适用于此：

1. core 定义媒体理解契约
2. 厂商插件按适用情况注册 `describeImage`、`transcribeAudio` 和
   `describeVideo`
3. 渠道和功能插件消费共享的 core 行为，而不是
   直接接入厂商代码

这样就避免了把某个提供商的视频假设固化进 core。插件拥有
厂商接口；core 拥有能力契约和回退行为。

视频生成已经使用了同样的顺序：core 拥有类型化
能力契约和运行时辅助函数，而厂商插件通过
`api.registerVideoGenerationProvider(...)` 注册实现。

需要一份具体的发布清单吗？请参阅
[能力扩展手册](/zh-CN/plugins/architecture)。

## 契约与强制执行

插件 API 接口是有意采用类型化并集中在
`OpenClawPluginApi` 中的。该契约定义了受支持的注册点，以及
插件可依赖的运行时辅助函数。

其重要性在于：

- 插件作者获得一种稳定的内部标准
- core 可以拒绝重复归属，例如两个插件注册相同的
  provider id
- 启动时可以为格式错误的注册提供可操作诊断
- 契约测试可以强制内置插件的归属关系，并防止静默漂移

这里有两层强制执行机制：

1. **运行时注册强制**
   插件加载时，插件注册表会验证注册内容。示例：
   重复的 provider id、重复的语音 provider id，以及格式错误的
   注册，都会生成插件诊断，而不是产生未定义行为。
2. **契约测试**
   在测试运行中，内置插件会被捕获到契约注册表中，从而让
   OpenClaw 能显式断言归属关系。目前这用于模型
   提供商、语音提供商、网页搜索提供商以及内置注册
   归属。

其实际效果是，OpenClaw 能够预先知道哪个插件拥有哪个
接口。这让 core 和渠道可以无缝组合，因为归属关系是
声明式、类型化且可测试的，而不是隐式的。

### 什么应该属于契约

好的插件契约应当是：

- 类型化的
- 小而精的
- 特定于能力的
- 由 core 拥有
- 可被多个插件复用
- 可被渠道 / 功能消费，而无需了解厂商细节

糟糕的插件契约包括：

- 隐藏在 core 中的厂商特定策略
- 绕过注册表的一次性插件逃生口
- 渠道代码直接深入厂商实现
- 不属于 `OpenClawPluginApi` 或
  `api.runtime` 的临时运行时对象

如果拿不准，提升抽象层级：先定义能力，再让插件接入。

## 执行模型

原生 OpenClaw 插件会与 Gateway 网关**在同一进程内**运行。它们不会被
沙箱隔离。已加载的原生插件与 core 代码具有相同的进程级信任边界。

其影响包括：

- 原生插件可以注册工具、网络处理器、hooks 和服务
- 原生插件中的 bug 可能导致网关崩溃或不稳定
- 恶意原生插件等同于在 OpenClaw 进程内部执行任意代码

兼容 bundle 默认更安全，因为 OpenClaw 当前会将它们视为
元数据 / 内容包。在当前版本中，这主要意味着内置
Skills。

对于非内置插件，请使用 allowlist 和显式的安装 / 加载路径。
应将工作区插件视为开发期代码，而不是生产默认项。

对于内置工作区包名，请保持插件 id 与 npm
名称一致：默认使用 `@openclaw/<id>`，或使用经批准的类型化后缀，例如
`-provider`、`-plugin`、`-speech`、`-sandbox` 或
`-media-understanding`，当该包有意暴露更窄的插件角色时可使用这些后缀。

重要信任说明：

- `plugins.allow` 信任的是**插件 id**，而不是来源。
- 如果一个工作区插件与某个内置插件具有相同 id，那么当该工作区插件被启用 / 加入 allowlist 时，
  它会有意遮蔽内置副本。
- 这是正常且有用的行为，适用于本地开发、补丁测试和热修复。

## 导出边界

OpenClaw 导出的是能力，而不是实现层面的便捷接口。

应保持能力注册为公开接口。精简非契约辅助导出：

- 内置插件特定的辅助子路径
- 不打算作为公共 API 的运行时接线子路径
- 厂商特定的便捷辅助函数
- 作为实现细节的设置 / 新手引导辅助函数

出于兼容性和内置插件维护的需要，一些内置插件辅助子路径
仍然保留在生成的 SDK 导出映射中。当前示例包括
`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup` 以及若干 `plugin-sdk/matrix*` 接缝。应将这些视为
保留的实现细节导出，而不是推荐给新第三方插件使用的 SDK 模式。

## 加载流水线

启动时，OpenClaw 大致会执行以下步骤：

1. 发现候选插件根目录
2. 读取原生或兼容 bundle 清单以及包元数据
3. 拒绝不安全的候选项
4. 标准化插件配置（`plugins.enabled`、`allow`、`deny`、`entries`、
   `slots`、`load.paths`）
5. 决定每个候选项的启用状态
6. 通过 jiti 加载已启用的原生模块
7. 调用原生 `register(api)`（或 `activate(api)` —— 一个遗留别名）hooks，并将注册内容收集到插件注册表中
8. 将注册表暴露给命令 / 运行时接口

<Note>
`activate` 是 `register` 的遗留别名 —— 加载器会解析两者中存在的那个（`def.register ?? def.activate`），并在同一时机调用。所有内置插件都使用 `register`；新插件请优先使用 `register`。
</Note>

安全门会在**运行时执行之前**生效。如果入口路径逃出插件根目录、
路径对所有人可写，或对于非内置插件而言路径归属看起来可疑，
候选项就会被阻止。

### 清单优先行为

清单是控制平面的事实来源。OpenClaw 使用它来：

- 标识插件
- 发现声明的渠道 / Skills / 配置 schema 或 bundle 能力
- 验证 `plugins.entries.<id>.config`
- 增强 Control UI 标签 / 占位文本
- 显示安装 / 目录元数据

对于原生插件，运行时模块是数据平面部分。它会注册
hooks、工具、命令或提供商流程等真实行为。

### 加载器会缓存什么

OpenClaw 会保留一些短生命周期的进程内缓存，用于：

- 发现结果
- 清单注册表数据
- 已加载的插件注册表

这些缓存可以减少突发启动和重复命令的开销。你可以放心地将它们视为
短生命周期的性能缓存，而非持久化。

性能说明：

- 设置 `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` 或
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` 可禁用这些缓存。
- 使用 `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` 和
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` 调整缓存窗口。

## 注册表模型

已加载的插件不会直接改动随意的 core 全局状态。它们会注册到一个
中央插件注册表中。

注册表会跟踪：

- 插件记录（身份、来源、origin、状态、诊断）
- 工具
- 遗留 hooks 和类型化 hooks
- 渠道
- 提供商
- Gateway 网关 RPC 处理器
- HTTP 路由
- CLI 注册器
- 后台服务
- 插件自有命令

然后，core 功能会从该注册表读取内容，而不是直接与插件模块
交互。这使加载保持单向：

- 插件模块 -> 注册表注册
- core 运行时 -> 注册表消费

这种分离对可维护性很重要。它意味着大多数 core 接口只
需要一个集成点：“读取注册表”，而不是“对每个插件
模块做特殊处理”。

## 对话绑定回调

绑定对话的插件可以在审批完成时做出响应。

使用 `api.onConversationBindingResolved(...)`，在绑定
请求被批准或拒绝后接收回调：

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // 现在已存在此插件 + 对话的绑定。
        console.log(event.binding?.conversationId);
        return;
      }

      // 请求被拒绝；清除任何本地待处理状态。
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

回调负载字段：

- `status`：`"approved"` 或 `"denied"`
- `decision`：`"allow-once"`、`"allow-always"` 或 `"deny"`
- `binding`：针对已批准请求的已解析绑定
- `request`：原始请求摘要、detach 提示、sender id 和
  对话元数据

此回调仅用于通知。它不会改变谁有权绑定某个
对话，并且会在 core 的审批处理完成后运行。

## 提供商运行时 hooks

提供商插件现在有两层：

- 清单元数据：`providerAuthEnvVars` 用于在运行时加载前进行廉价的
  env 认证查找，`providerAuthChoices` 用于在运行时加载前提供廉价的
  新手引导 / 认证选项标签和 CLI flag 元数据
- 配置时 hooks：`catalog` / 遗留 `discovery` 以及 `applyConfigDefaults`
- 运行时 hooks：`normalizeModelId`、`normalizeTransport`、
  `normalizeConfig`、
  `applyNativeStreamingUsageCompat`、`resolveConfigApiKey`、
  `resolveSyntheticAuth`、`shouldDeferSyntheticProfileAuth`、
  `resolveDynamicModel`、`prepareDynamicModel`、`normalizeResolvedModel`、
  `contributeResolvedModelCompat`、`capabilities`、
  `normalizeToolSchemas`、`inspectToolSchemas`、
  `resolveReasoningOutputMode`、`prepareExtraParams`、`createStreamFn`、
  `wrapStreamFn`、`resolveTransportTurnState`、
  `resolveWebSocketSessionPolicy`、`formatApiKey`、`refreshOAuth`、
  `buildAuthDoctorHint`、`matchesContextOverflowError`、
  `classifyFailoverReason`、`isCacheTtlEligible`、
  `buildMissingAuthMessage`、`suppressBuiltInModel`、`augmentModelCatalog`、
  `isBinaryThinking`、`supportsXHighThinking`、
  `resolveDefaultThinkingLevel`、`isModernModelRef`、`prepareRuntimeAuth`、
  `resolveUsageAuth`、`fetchUsageSnapshot`、`createEmbeddingProvider`、
  `buildReplayPolicy`、
  `sanitizeReplayHistory`、`validateReplayTurns`、`onModelSelected`

OpenClaw 仍然拥有通用智能体循环、故障切换、转录处理和
工具策略。这些 hooks 是提供商特定行为的扩展接口，使其无需
实现一整套自定义推理传输。

当提供商具有基于 env 的凭证，且通用认证 / 状态 / 模型选择器路径
需要在不加载插件运行时的情况下看到它们时，请使用清单中的 `providerAuthEnvVars`。
当新手引导 / 认证选择 CLI 接口需要在不加载提供商运行时的情况下
了解该提供商的 choice id、分组标签和简单的单 flag 认证接线时，
请使用清单中的 `providerAuthChoices`。提供商运行时中的
`envVars` 应保留给面向运维人员的提示，例如新手引导标签或 OAuth
client-id / client-secret 设置变量。

### Hook 顺序与用法

对于模型 / 提供商插件，OpenClaw 大致按如下顺序调用 hooks。
“何时使用”列是快速决策指南。

| #   | Hook                              | 作用                                                                                     | 何时使用                                                                                                                                   |
| --- | --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| 1   | `catalog`                         | 在生成 `models.json` 时将提供商配置发布到 `models.providers`                             | 提供商拥有目录或 base URL 默认值                                                                                                           |
| 2   | `applyConfigDefaults`             | 在配置具体化期间应用提供商自有的全局配置默认值                                           | 默认值依赖认证模式、env 或提供商模型家族语义                                                                                              |
| --  | _(内置模型查找)_                  | OpenClaw 首先尝试常规注册表 / 目录路径                                                   | _(不是插件 hook)_                                                                                                                          |
| 3   | `normalizeModelId`                | 在查找前标准化遗留或预览版模型 id 别名                                                   | 提供商拥有规范模型解析前的别名清理逻辑                                                                                                     |
| 4   | `normalizeTransport`              | 在通用模型组装前标准化提供商家族中的 `api` / `baseUrl`                                   | 提供商拥有同一传输家族中自定义 provider id 的传输清理逻辑                                                                                  |
| 5   | `normalizeConfig`                 | 在运行时 / 提供商解析前标准化 `models.providers.<id>`                                    | 提供商需要将配置清理逻辑与插件放在一起；内置 Google 家族辅助函数也会对受支持的 Google 配置项提供兜底兼容清理                            |
| 6   | `applyNativeStreamingUsageCompat` | 对配置提供商应用原生流式使用量兼容改写                                                   | 提供商需要基于端点驱动的原生流式使用量元数据修复                                                                                           |
| 7   | `resolveConfigApiKey`             | 在加载运行时认证前，为配置提供商解析 env-marker 认证                                     | 提供商拥有自有的 env-marker API key 解析逻辑；`amazon-bedrock` 在这里也有内置的 AWS env-marker 解析器                                    |
| 8   | `resolveSyntheticAuth`            | 在不持久化明文的前提下暴露本地 / 自托管或基于配置的认证                                  | 提供商可以使用 synthetic / 本地凭证标记运行                                                                                                |
| 9   | `shouldDeferSyntheticProfileAuth` | 降低已存储 synthetic 配置文件占位符在 env / 配置支持认证后的优先级                       | 提供商存储了 synthetic 占位 profile，而这些 profile 不应优先                                                                               |
| 10  | `resolveDynamicModel`             | 为本地注册表中尚不存在的提供商自有模型 id 提供同步回退                                   | 提供商接受任意上游模型 id                                                                                                                  |
| 11  | `prepareDynamicModel`             | 异步预热，然后再次运行 `resolveDynamicModel`                                              | 提供商在解析未知 id 前需要网络元数据                                                                                                       |
| 12  | `normalizeResolvedModel`          | 在嵌入式 runner 使用已解析模型前进行最终改写                                             | 提供商需要传输改写，但仍使用 core 传输                                                                                                     |
| 13  | `contributeResolvedModelCompat`   | 为位于其他兼容传输后的厂商模型提供兼容标记                                               | 提供商可以在不接管整个提供商的情况下识别代理传输上的自有模型                                                                               |
| 14  | `capabilities`                    | 供共享 core 逻辑使用的、提供商自有的转录 / 工具元数据                                    | 提供商需要转录 / 提供商家族特有的兼容处理                                                                                                  |
| 15  | `normalizeToolSchemas`            | 在嵌入式 runner 看到工具 schema 之前进行标准化                                           | 提供商需要传输家族级的 schema 清理                                                                                                         |
| 16  | `inspectToolSchemas`              | 在标准化后暴露提供商自有的 schema 诊断                                                   | 提供商希望给出关键字警告，而不是让 core 学会提供商特定规则                                                                                 |
| 17  | `resolveReasoningOutputMode`      | 选择原生还是带标签的推理输出契约                                                         | 提供商需要带标签的推理 / 最终输出，而不是原生字段                                                                                          |
| 18  | `prepareExtraParams`              | 在通用流式选项包装器之前做请求参数标准化                                                 | 提供商需要默认请求参数或按提供商清理参数                                                                                                   |
| 19  | `createStreamFn`                  | 用自定义传输完全替换常规流路径                                                           | 提供商需要自定义线路协议，而不只是包装器                                                                                                   |
| 20  | `wrapStreamFn`                    | 在应用通用包装器后再包装流函数                                                           | 提供商需要请求头 / 请求体 / 模型兼容包装器，而无需自定义传输                                                                               |
| 21  | `resolveTransportTurnState`       | 附加原生的逐轮传输头或元数据                                                             | 提供商希望通用传输发送提供商原生的轮次身份                                                                                                 |
| 22  | `resolveWebSocketSessionPolicy`   | 附加原生 WebSocket 头或会话冷却策略                                                      | 提供商希望通用 WS 传输调优会话头或回退策略                                                                                                 |
| 23  | `formatApiKey`                    | 认证 profile 格式化器：已存储 profile 会变成运行时 `apiKey` 字符串                       | 提供商存储了额外认证元数据，且需要自定义运行时 token 形态                                                                                  |
| 24  | `refreshOAuth`                    | 针对自定义刷新端点或刷新失败策略的 OAuth 刷新覆写                                        | 提供商不适合共享的 `pi-ai` 刷新器                                                                                                          |
| 25  | `buildAuthDoctorHint`             | 当 OAuth 刷新失败时附加修复提示                                                          | 提供商在刷新失败后需要提供商自有的认证修复指导                                                                                             |
| 26  | `matchesContextOverflowError`     | 提供商自有的上下文窗口溢出匹配器                                                         | 提供商存在通用启发式无法识别的原始溢出错误                                                                                                 |
| 27  | `classifyFailoverReason`          | 提供商自有的故障切换原因分类                                                             | 提供商可以将原始 API / 传输错误映射为限速 / 过载等                                                                                         |
| 28  | `isCacheTtlEligible`              | 代理 / 回程提供商的提示词缓存策略                                                        | 提供商需要代理特定的缓存 TTL 门控                                                                                                          |
| 29  | `buildMissingAuthMessage`         | 替代通用缺失认证恢复消息                                                                 | 提供商需要提供商特定的缺失认证恢复提示                                                                                                     |
| 30  | `suppressBuiltInModel`            | 过期上游模型抑制以及可选的面向用户错误提示                                               | 提供商需要隐藏过期上游条目或用厂商提示替换它们                                                                                             |
| 31  | `augmentModelCatalog`             | 在发现后追加 synthetic / 最终目录条目                                                    | 提供商需要在 `models list` 和选择器中加入 synthetic 前向兼容条目                                                                           |
| 32  | `isBinaryThinking`                | 二元思考型提供商的开 / 关推理切换                                                        | 提供商只暴露二元的思考开 / 关                                                                                                              |
| 33  | `supportsXHighThinking`           | 为选定模型提供 `xhigh` 推理支持                                                          | 提供商只希望部分模型支持 `xhigh`                                                                                                           |
| 34  | `resolveDefaultThinkingLevel`     | 为特定模型家族提供默认 `/think` 级别                                                     | 提供商拥有某个模型家族的默认 `/think` 策略                                                                                                 |
| 35  | `isModernModelRef`                | 用于实时 profile 过滤和 smoke 选择的现代模型匹配器                                       | 提供商拥有 live / smoke 首选模型匹配逻辑                                                                                                   |
| 36  | `prepareRuntimeAuth`              | 在推理前将已配置凭证交换成真实运行时 token / key                                         | 提供商需要 token 交换或短期请求凭证                                                                                                        |
| 37  | `resolveUsageAuth`                | 为 `/usage` 及相关状态接口解析使用量 / 计费凭证                                          | 提供商需要自定义使用量 / 配额 token 解析，或使用不同的使用量凭证                                                                           |
| 38  | `fetchUsageSnapshot`              | 在认证解析后获取并标准化提供商特定的使用量 / 配额快照                                    | 提供商需要提供商特定的使用量端点或负载解析器                                                                                               |
| 39  | `createEmbeddingProvider`         | 为 memory / search 构建提供商自有的 embedding 适配器                                     | memory embedding 行为应归属于提供商插件                                                                                                    |
| 40  | `buildReplayPolicy`               | 返回控制提供商转录处理的 replay 策略                                                     | 提供商需要自定义转录策略（例如剥离 thinking block）                                                                                        |
| 41  | `sanitizeReplayHistory`           | 在通用转录清理后改写 replay 历史                                                         | 提供商需要超出共享压缩辅助函数之外的提供商特定 replay 改写                                                                                 |
| 42  | `validateReplayTurns`             | 在嵌入式 runner 之前进行最终 replay 轮次验证或重塑                                       | 提供商传输在通用清理之后需要更严格的轮次验证                                                                                               |
| 43  | `onModelSelected`                 | 运行提供商自有的模型选定后副作用                                                         | 提供商需要在模型激活时记录遥测或维护提供商自有状态                                                                                         |

`normalizeModelId`、`normalizeTransport` 和 `normalizeConfig` 会先检查
匹配到的提供商插件，然后依次回退到其他具备 hook 能力的提供商插件，
直到其中某个插件实际更改了 model id 或 transport / config 为止。这让
别名 / 兼容性提供商 shim 可以继续工作，而无需要求调用方知道哪个
内置插件拥有该改写逻辑。如果没有提供商 hook 改写受支持的
Google 家族配置项，内置 Google 配置标准化器仍会应用
该兼容性清理。

如果提供商需要完全自定义的线路协议或自定义请求执行器，
那属于另一类扩展。这些 hooks 适用于仍运行在
OpenClaw 常规推理循环上的提供商行为。

### 提供商示例

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### 内置示例

- Anthropic 使用 `resolveDynamicModel`、`capabilities`、`buildAuthDoctorHint`、
  `resolveUsageAuth`、`fetchUsageSnapshot`、`isCacheTtlEligible`、
  `resolveDefaultThinkingLevel`、`applyConfigDefaults`、`isModernModelRef`、
  和 `wrapStreamFn`，因为它拥有 Claude 4.6 的前向兼容、
  提供商家族提示、认证修复指导、使用量端点集成、
  提示词缓存资格、具备认证感知的配置默认值、Claude
  默认 / 自适应 thinking 策略，以及面向 beta
  headers、`/fast` / `serviceTier` 和 `context1m` 的 Anthropic 特定流整形。
- Anthropic 的 Claude 特定流辅助函数目前保留在该内置插件自己的
  公共 `api.ts` / `contract-api.ts` 接缝中。该包接口
  导出 `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
  `resolveAnthropicFastMode`、`resolveAnthropicServiceTier` 以及更底层的
  Anthropic 包装器构建函数，而不是围绕某一提供商的 beta header 规则
  扩大通用 SDK。
- OpenAI 使用 `resolveDynamicModel`、`normalizeResolvedModel` 和
  `capabilities`，以及 `buildMissingAuthMessage`、`suppressBuiltInModel`、
  `augmentModelCatalog`、`supportsXHighThinking` 和 `isModernModelRef`，
  因为它拥有 GPT-5.4 的前向兼容、直接的 OpenAI
  `openai-completions` -> `openai-responses` 标准化、Codex 感知的认证
  提示、Spark 抑制、synthetic OpenAI 列表行，以及 GPT-5 thinking /
  实时模型策略；`openai-responses-defaults` 流家族拥有共享的原生 OpenAI Responses 包装器，
  用于 attribution headers、
  `/fast`/`serviceTier`、文本冗长度、原生 Codex 网页搜索、
  reasoning 兼容负载整形，以及 Responses 上下文管理。
- OpenRouter 使用 `catalog` 以及 `resolveDynamicModel` 和
  `prepareDynamicModel`，因为该提供商是透传型的，可能在 OpenClaw
  静态目录更新前就暴露出新的模型 id；它还使用
  `capabilities`、`wrapStreamFn` 和 `isCacheTtlEligible`，以将
  提供商特定的请求头、路由元数据、reasoning 修补和
  提示词缓存策略留在 core 之外。其 replay 策略来自
  `passthrough-gemini` 家族，而 `openrouter-thinking` 流家族
  拥有代理 reasoning 注入以及不受支持模型 / `auto` 的跳过逻辑。
- GitHub Copilot 使用 `catalog`、`auth`、`resolveDynamicModel` 和
  `capabilities`，以及 `prepareRuntimeAuth` 和 `fetchUsageSnapshot`，因为它
  需要提供商自有的设备登录、模型回退行为、Claude 转录兼容性、
  GitHub token -> Copilot token 交换，以及提供商自有的使用量端点。
- OpenAI Codex 使用 `catalog`、`resolveDynamicModel`、
  `normalizeResolvedModel`、`refreshOAuth` 和 `augmentModelCatalog`，以及
  `prepareExtraParams`、`resolveUsageAuth` 和 `fetchUsageSnapshot`，因为它
  仍运行在 core OpenAI 传输之上，但拥有自己的 transport / base URL
  标准化、OAuth 刷新回退策略、默认传输选择、
  synthetic Codex 目录条目，以及 ChatGPT 使用量端点集成；它
  与直接 OpenAI 共享同一个 `openai-responses-defaults` 流家族。
- Google AI Studio 和 Gemini CLI OAuth 使用 `resolveDynamicModel`、
  `buildReplayPolicy`、`sanitizeReplayHistory`、
  `resolveReasoningOutputMode`、`wrapStreamFn` 和 `isModernModelRef`，因为
  `google-gemini` replay 家族拥有 Gemini 3.1 前向兼容回退、
  原生 Gemini replay 验证、bootstrap replay 清理、
  带标签的 reasoning 输出模式，以及现代模型匹配，而
  `google-thinking` 流家族拥有 Gemini thinking 负载标准化；
  Gemini CLI OAuth 还使用 `formatApiKey`、`resolveUsageAuth` 和
  `fetchUsageSnapshot` 来处理 token 格式化、token 解析以及配额端点
  接线。
- Anthropic Vertex 通过
  `anthropic-by-model` replay 家族使用 `buildReplayPolicy`，从而让 Claude 特定的 replay 清理
  只作用于 Claude id，而不是每个 `anthropic-messages` 传输。
- Amazon Bedrock 使用 `buildReplayPolicy`、`matchesContextOverflowError`、
  `classifyFailoverReason` 和 `resolveDefaultThinkingLevel`，因为它拥有
  Bedrock 特定的限流 / 未就绪 / 上下文溢出错误分类，
  用于 Anthropic-on-Bedrock 流量；其 replay 策略仍共享相同的
  仅限 Claude 的 `anthropic-by-model` 防护。
- OpenRouter、Kilocode、Opencode 和 Opencode Go 通过
  `passthrough-gemini` replay 家族使用 `buildReplayPolicy`，因为它们通过 OpenAI 兼容传输
  代理 Gemini 模型，并且需要进行 Gemini
  thought-signature 清理，而无需原生 Gemini replay 验证或
  bootstrap 改写。
- MiniMax 通过
  `hybrid-anthropic-openai` replay 家族使用 `buildReplayPolicy`，因为一个提供商同时拥有
  Anthropic-message 和 OpenAI 兼容语义；它会在 Anthropic 侧保持仅限 Claude 的
  thinking block 丢弃，同时将 reasoning
  输出模式改回原生，而 `minimax-fast-mode` 流家族则拥有
  共享流路径上的 fast-mode 模型改写。
- Moonshot 使用 `catalog` 和 `wrapStreamFn`，因为它仍使用共享的
  OpenAI 传输，但需要提供商自有的 thinking 负载标准化；
  `moonshot-thinking` 流家族将配置和 `/think` 状态映射到其
  原生二元 thinking 负载。
- Kilocode 使用 `catalog`、`capabilities`、`wrapStreamFn` 和
  `isCacheTtlEligible`，因为它需要提供商自有的请求头、
  reasoning 负载标准化、Gemini 转录提示，以及 Anthropic
  cache-TTL 门控；`kilocode-thinking` 流家族负责在共享代理流路径上注入 Kilo thinking，
  同时跳过 `kilo/auto` 以及其他不支持显式 reasoning 负载的
  代理模型 id。
- Z.AI 使用 `resolveDynamicModel`、`prepareExtraParams`、`wrapStreamFn`、
  `isCacheTtlEligible`、`isBinaryThinking`、`isModernModelRef`、
  `resolveUsageAuth` 和 `fetchUsageSnapshot`，因为它拥有 GLM-5 回退、
  `tool_stream` 默认值、二元 thinking UX、现代模型匹配，以及
  使用量认证 + 配额获取；`tool-stream-default-on` 流家族将
  默认开启的 `tool_stream` 包装器从每个提供商手写粘合逻辑中抽离出来。
- xAI 使用 `normalizeResolvedModel`、`normalizeTransport`、
  `contributeResolvedModelCompat`、`prepareExtraParams`、`wrapStreamFn`、
  `resolveSyntheticAuth`、`resolveDynamicModel` 和 `isModernModelRef`，
  因为它拥有原生 xAI Responses 传输标准化、Grok fast-mode
  别名改写、默认 `tool_stream`、strict-tool / reasoning-payload
  清理、用于插件自有工具的回退认证复用、前向兼容的 Grok
  模型解析，以及提供商自有的兼容修补，例如 xAI 工具 schema
  配置、受支持范围外的 schema 关键字、原生 `web_search`，以及 HTML 实体
  工具调用参数解码。
- Mistral、OpenCode Zen 和 OpenCode Go 仅使用 `capabilities`，
  以将转录 / 工具兼容性留在 core 之外。
- 仅目录型内置提供商，例如 `byteplus`、`cloudflare-ai-gateway`、
  `huggingface`、`kimi-coding`、`nvidia`、`qianfan`、
  `synthetic`、`together`、`venice`、`vercel-ai-gateway` 和 `volcengine`，
  仅使用 `catalog`。
- Qwen 使用 `catalog` 处理其文本提供商，同时为其多模态接口
  注册共享的媒体理解和视频生成。
- MiniMax 和 Xiaomi 使用 `catalog` 加上使用量 hooks，因为它们的 `/usage`
  行为归插件所有，尽管推理仍通过共享传输运行。

## 运行时辅助函数

插件可以通过 `api.runtime` 访问部分选定的 core 辅助函数。对于 TTS：

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

说明：

- `textToSpeech` 返回面向文件 / 语音便笺接口的常规 core TTS 输出负载。
- 使用 core 的 `messages.tts` 配置和提供商选择。
- 返回 PCM 音频缓冲区 + 采样率。插件必须为提供商重新采样 / 编码。
- `listVoices` 对每个提供商而言是可选的。将其用于厂商自有的语音选择器或设置流程。
- 语音列表可以包含更丰富的元数据，例如区域设置、性别和 personality 标签，以供感知提供商的选择器使用。
- 目前 OpenAI 和 ElevenLabs 支持电话场景。Microsoft 不支持。

插件也可以通过 `api.registerSpeechProvider(...)` 注册语音提供商。

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

说明：

- 将 TTS 策略、回退和回复交付保留在 core 中。
- 使用语音提供商承载厂商自有的合成行为。
- 遗留 Microsoft `edge` 输入会被标准化为 `microsoft` provider id。
- 推荐的归属模型是面向公司的：随着 OpenClaw 增加这些
  能力契约，一个厂商插件可以拥有文本、语音、图像以及未来的媒体提供商。

对于图像 / 音频 / 视频理解，插件应注册一个类型化的
媒体理解提供商，而不是一个通用的 key / value 包：

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

说明：

- 将编排、回退、配置和渠道接线保留在 core 中。
- 将厂商行为保留在提供商插件中。
- 增量扩展应保持类型化：新增可选方法、新增可选
  结果字段、新增可选能力。
- 视频生成已经遵循同样模式：
  - core 拥有能力契约和运行时辅助函数
  - 厂商插件注册 `api.registerVideoGenerationProvider(...)`
  - 功能 / 渠道插件消费 `api.runtime.videoGeneration.*`

对于媒体理解运行时辅助函数，插件可以调用：

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

对于音频转录，插件既可以使用媒体理解运行时，
也可以使用旧的 STT 别名：

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // 当 MIME 无法可靠推断时可选：
  mime: "audio/ogg",
});
```

说明：

- `api.runtime.mediaUnderstanding.*` 是图像 / 音频 / 视频理解
  的首选共享接口。
- 使用 core 的媒体理解音频配置（`tools.media.audio`）和提供商回退顺序。
- 当未产生转录输出时（例如输入被跳过 / 不受支持），返回 `{ text: undefined }`。
- `api.runtime.stt.transcribeAudioFile(...)` 仍保留为兼容别名。

插件还可以通过 `api.runtime.subagent` 启动后台子智能体运行：

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

说明：

- `provider` 和 `model` 是每次运行的可选覆写，而不是持久会话变更。
- OpenClaw 只会为受信任调用方接受这些覆写字段。
- 对于插件自有的回退运行，运维人员必须通过 `plugins.entries.<id>.subagent.allowModelOverride: true` 显式启用。
- 使用 `plugins.entries.<id>.subagent.allowedModels` 将受信任插件限制为特定的规范 `provider/model` 目标，或设置为 `"*"` 以显式允许任意目标。
- 不受信任的插件子智能体运行仍可执行，但覆写请求会被拒绝，而不是静默回退。

对于网页搜索，插件可以消费共享运行时辅助函数，而不是
深入智能体工具接线：

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

插件也可以通过
`api.registerWebSearchProvider(...)` 注册网页搜索提供商。

说明：

- 将提供商选择、凭证解析和共享请求语义保留在 core 中。
- 对于厂商特定的搜索传输，使用网页搜索提供商。
- `api.runtime.webSearch.*` 是功能 / 渠道插件在需要搜索能力但又不依赖
  智能体工具包装器时的首选共享接口。

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`：使用已配置的图像生成提供商链生成图像。
- `listProviders(...)`：列出可用的图像生成提供商及其能力。

## Gateway 网关 HTTP 路由

插件可以通过 `api.registerHttpRoute(...)` 暴露 HTTP 端点。

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

路由字段：

- `path`：Gateway 网关 HTTP 服务器下的路由路径。
- `auth`：必填。使用 `"gateway"` 以要求常规 Gateway 网关认证，或使用 `"plugin"` 以进行插件管理的认证 / webhook 验证。
- `match`：可选。`"exact"`（默认）或 `"prefix"`。
- `replaceExisting`：可选。允许同一插件替换自己现有的路由注册。
- `handler`：当路由处理了请求时返回 `true`。

说明：

- `api.registerHttpHandler(...)` 已移除，并会导致插件加载错误。请改用 `api.registerHttpRoute(...)`。
- 插件路由必须显式声明 `auth`。
- 除非设置 `replaceExisting: true`，否则精确的 `path + match` 冲突会被拒绝，且一个插件不能替换另一个插件的路由。
- 不同 `auth` 级别的重叠路由会被拒绝。`exact` / `prefix` 的顺序回退链只能保留在同一 auth 级别内。
- `auth: "plugin"` 路由**不会**自动接收运维人员运行时作用域。它们用于插件管理的 webhook / 签名验证，而不是带特权的 Gateway 网关辅助调用。
- `auth: "gateway"` 路由会在 Gateway 网关请求运行时作用域内运行，但该作用域有意保持保守：
  - 共享密钥 bearer 认证（`gateway.auth.mode = "token"` / `"password"`）会将插件路由运行时作用域固定在 `operator.write`，即使调用方发送了 `x-openclaw-scopes`
  - 受信任的携带身份 HTTP 模式（例如 `trusted-proxy` 或私有入口上的 `gateway.auth.mode = "none"`）只有在显式提供该 header 时，才会遵守 `x-openclaw-scopes`
  - 如果这些携带身份的插件路由请求中没有 `x-openclaw-scopes`，运行时作用域会回退到 `operator.write`
- 实践规则：不要假设一个经过 gateway 认证的插件路由天然就是管理接口。如果你的路由需要仅管理员行为，请要求使用携带身份的认证模式，并记录显式的 `x-openclaw-scopes` header 契约。

## 插件 SDK 导入路径

在编写插件时，请使用 SDK 子路径，而不是单体式 `openclaw/plugin-sdk` 导入：

- 使用 `openclaw/plugin-sdk/plugin-entry` 进行插件注册基础能力导入。
- 使用 `openclaw/plugin-sdk/core` 进行通用共享的插件侧契约导入。
- 使用 `openclaw/plugin-sdk/config-schema` 导入根 `openclaw.json` Zod schema
  导出（`OpenClawSchema`）。
- 稳定的渠道基础接口，例如 `openclaw/plugin-sdk/channel-setup`、
  `openclaw/plugin-sdk/setup-runtime`、
  `openclaw/plugin-sdk/setup-adapter-runtime`、
  `openclaw/plugin-sdk/setup-tools`、
  `openclaw/plugin-sdk/channel-pairing`、
  `openclaw/plugin-sdk/channel-contract`、
  `openclaw/plugin-sdk/channel-feedback`、
  `openclaw/plugin-sdk/channel-inbound`、
  `openclaw/plugin-sdk/channel-lifecycle`、
  `openclaw/plugin-sdk/channel-reply-pipeline`、
  `openclaw/plugin-sdk/command-auth`、
  `openclaw/plugin-sdk/secret-input` 和
  `openclaw/plugin-sdk/webhook-ingress`，用于共享设置 / 认证 / 回复 / webhook
  接线。`channel-inbound` 是 debounce、mention 匹配、
  envelope 格式化和入站 envelope 上下文辅助函数的共享位置。
  `channel-setup` 是可选安装设置的狭窄接缝。
  `setup-runtime` 是 `setupEntry` /
  延迟启动所使用的运行时安全设置接口，包括可安全导入的设置补丁适配器。
  `setup-adapter-runtime` 是感知 env 的账户设置适配器接缝。
  `setup-tools` 是小型 CLI / 归档 / 文档辅助接缝（`formatCliCommand`、
  `detectBinary`、`extractArchive`、`resolveBrewExecutable`、`formatDocsLink`、
  `CONFIG_DIR`）。
- 领域子路径，例如 `openclaw/plugin-sdk/channel-config-helpers`、
  `openclaw/plugin-sdk/allow-from`、
  `openclaw/plugin-sdk/channel-config-schema`、
  `openclaw/plugin-sdk/telegram-command-config`、
  `openclaw/plugin-sdk/channel-policy`、
  `openclaw/plugin-sdk/approval-runtime`、
  `openclaw/plugin-sdk/config-runtime`、
  `openclaw/plugin-sdk/infra-runtime`、
  `openclaw/plugin-sdk/agent-runtime`、
  `openclaw/plugin-sdk/lazy-runtime`、
  `openclaw/plugin-sdk/reply-history`、
  `openclaw/plugin-sdk/routing`、
  `openclaw/plugin-sdk/status-helpers`、
  `openclaw/plugin-sdk/text-runtime`、
  `openclaw/plugin-sdk/runtime-store` 和
  `openclaw/plugin-sdk/directory-runtime`，用于共享运行时 / 配置辅助函数。
  `telegram-command-config` 是 Telegram 自定义
  命令标准化 / 验证的狭窄公共接缝，即便内置
  Telegram 契约接口暂时不可用，它也仍然可用。
  `text-runtime` 是共享的文本 / markdown / 日志接缝，包括
  助手可见文本剥离、markdown 渲染 / 分块辅助函数、脱敏
  辅助函数、directive-tag 辅助函数和安全文本工具。
- 针对审批的渠道接缝应优先使用插件上的单一 `approvalCapability`
  契约。然后 core 会通过这一个能力读取审批认证、交付、渲染和
  原生路由行为，而不是把审批行为混入无关的插件字段中。
- `openclaw/plugin-sdk/channel-runtime` 已弃用，目前仅作为
  旧插件的兼容 shim 保留。新代码应改用更狭窄的通用基础接口导入，
  仓库代码也不应再新增对该 shim 的导入。
- 内置扩展内部实现仍然是私有的。外部插件应只使用
  `openclaw/plugin-sdk/*` 子路径。OpenClaw core / 测试代码可以使用插件包根目录下的
  仓库公共入口点，例如 `index.js`、`api.js`、
  `runtime-api.js`、`setup-entry.js`，以及作用域较窄的文件，例如
  `login-qr-api.js`。绝不要从 core 或另一个扩展中导入某个插件包的 `src/*`。
- 仓库入口点拆分：
  `<plugin-package-root>/api.js` 是辅助函数 / 类型 barrel，
  `<plugin-package-root>/runtime-api.js` 是仅运行时 barrel，
  `<plugin-package-root>/index.js` 是内置插件入口，
  `<plugin-package-root>/setup-entry.js` 是设置插件入口。
- 当前内置提供商示例：
  - Anthropic 使用 `api.js` / `contract-api.js` 提供 Claude 流辅助函数，例如
    `wrapAnthropicProviderStream`、beta-header 辅助函数和 `service_tier`
    解析。
  - OpenAI 使用 `api.js` 提供提供商构建器、默认模型辅助函数，以及
    实时提供商构建器。
  - OpenRouter 使用 `api.js` 提供其提供商构建器以及新手引导 / 配置
    辅助函数，而 `register.runtime.js` 仍然可以为仓库本地用途重新导出通用
    `plugin-sdk/provider-stream` 辅助函数。
- 通过 facade 加载的公共入口点会优先使用活动中的运行时配置快照；
  如果 OpenClaw 尚未提供运行时快照，则回退到磁盘上的已解析配置文件。
- 通用共享基础接口仍然是首选的公共 SDK 契约。仍然存在一小组保留的、
  兼容性用途的内置渠道品牌化辅助接缝。应将这些视为内置维护 /
  兼容性接缝，而不是新的第三方导入目标；新的跨渠道契约仍应落在
  通用 `plugin-sdk/*` 子路径或插件本地 `api.js` /
  `runtime-api.js` barrel 上。

兼容性说明：

- 新代码应避免使用根级 `openclaw/plugin-sdk` barrel。
- 优先使用狭窄、稳定的基础接口。更新的 setup / pairing / reply /
  feedback / contract / inbound / threading / command / secret-input / webhook / infra /
  allowlist / status / message-tool 子路径，是新的
  内置和外部插件工作的目标契约。
  目标解析 / 匹配应放在 `openclaw/plugin-sdk/channel-targets`。
  消息动作门控和 reaction message-id 辅助函数应放在
  `openclaw/plugin-sdk/channel-actions`。
- 默认情况下，内置扩展特定辅助 barrel 并不稳定。如果
  某个辅助函数只被某个内置扩展需要，应将其保留在该扩展的
  本地 `api.js` 或 `runtime-api.js` 接缝后，而不是提升到
  `openclaw/plugin-sdk/<extension>` 中。
- 新的共享辅助接缝应是通用的，而不是带渠道品牌的。共享目标
  解析应放在 `openclaw/plugin-sdk/channel-targets`；渠道特定
  内部实现应保留在所属插件的本地 `api.js` 或 `runtime-api.js`
  接缝后。
- `image-generation`、
  `media-understanding` 和 `speech` 之类的能力特定子路径之所以存在，
  是因为内置 / 原生插件如今在使用它们。这并不自动意味着每个导出的辅助函数
  都是长期冻结的外部契约。

## 消息工具 schema

插件应拥有渠道特定的 `describeMessageTool(...)` schema
扩展。将提供商特定字段保留在插件中，而不是放入共享 core。

对于共享的可移植 schema 片段，请复用
`openclaw/plugin-sdk/channel-actions` 导出的通用辅助函数：

- `createMessageToolButtonsSchema()` 用于按钮网格样式负载
- `createMessageToolCardSchema()` 用于结构化卡片负载

如果某个 schema 形态只适用于一个提供商，请在该插件自己的
源代码中定义，而不要将其提升到共享 SDK 中。

## 渠道目标解析

渠道插件应拥有渠道特定的目标语义。请保持共享
outbound 宿主的通用性，并通过消息适配器接口处理提供商规则：

- `messaging.inferTargetChatType({ to })` 用于决定一个标准化目标
  在目录查找前应被视为 `direct`、`group` 还是 `channel`。
- `messaging.targetResolver.looksLikeId(raw, normalized)` 用于告诉 core
  某个输入是否应跳过目录搜索，直接进入类似 id 的解析。
- `messaging.targetResolver.resolveTarget(...)` 是在标准化之后或目录未命中后，
  core 需要最终提供商自有解析时的插件回退接口。
- `messaging.resolveOutboundSessionRoute(...)` 拥有提供商特定的会话
  路由构建逻辑，在目标解析完成后执行。

推荐拆分：

- 使用 `inferTargetChatType` 处理那些应在搜索 peers / groups 之前完成的分类决策。
- 使用 `looksLikeId` 进行“将此视为显式 / 原生目标 id”的检查。
- 使用 `resolveTarget` 进行提供商特定的标准化回退，而不是进行广泛的目录搜索。
- 将聊天 id、线程 id、JID、handle 和房间 id 等提供商原生 id
  保留在 `target` 值或提供商特定参数中，而不是放入通用 SDK 字段。

## 基于配置的目录

从配置派生目录项的插件应将该逻辑保留在
插件内部，并复用
`openclaw/plugin-sdk/directory-runtime` 中的共享辅助函数。

当某个渠道需要基于配置的 peers / groups 时，应使用此模式，例如：

- 基于 allowlist 的私信 peers
- 已配置的渠道 / 群组映射
- 按账户作用域划分的静态目录回退

`directory-runtime` 中的共享辅助函数只处理通用操作：

- 查询过滤
- 应用限制
- 去重 / 标准化辅助函数
- 构建 `ChannelDirectoryEntry[]`

渠道特定的账户检查和 id 标准化应保留在
插件实现中。

## 提供商目录

提供商插件可以通过
`registerProvider({ catalog: { run(...) { ... } } })` 为推理定义模型目录。

`catalog.run(...)` 返回的形态与 OpenClaw 写入
`models.providers` 的内容相同：

- `{ provider }` 表示一个 provider 条目
- `{ providers }` 表示多个 provider 条目

当插件拥有提供商特定的模型 id、base URL 默认值，
或受认证保护的模型元数据时，请使用 `catalog`。

`catalog.order` 控制插件目录相对于 OpenClaw 内置隐式提供商
合并的时机：

- `simple`：纯 API key 或 env 驱动的提供商
- `profile`：当存在 auth profiles 时出现的提供商
- `paired`：合成多个相关 provider 条目的提供商
- `late`：最后一轮，在其他隐式提供商之后

后出现的提供商会在键冲突时获胜，因此插件可以有意用相同的
provider id 覆盖内置 provider 条目。

兼容性：

- `discovery` 仍可用，作为遗留别名
- 如果同时注册了 `catalog` 和 `discovery`，OpenClaw 会使用 `catalog`

## 只读渠道检查

如果你的插件注册了一个渠道，建议在
`resolveAccount(...)` 之外同时实现 `plugin.config.inspectAccount(cfg, accountId)`。

原因如下：

- `resolveAccount(...)` 是运行时路径。它可以假定凭证
  已完全具体化，并且在所需 secret 缺失时快速失败。
- `openclaw status`、`openclaw status --all`、
  `openclaw channels status`、`openclaw channels resolve` 以及 Doctor / 配置
  修复流等只读命令路径，不应为了描述配置而去具体化运行时凭证。

推荐的 `inspectAccount(...)` 行为：

- 只返回描述性的账户状态。
- 保留 `enabled` 和 `configured`。
- 在相关时包含凭证来源 / 状态字段，例如：
  - `tokenSource`、`tokenStatus`
  - `botTokenSource`、`botTokenStatus`
  - `appTokenSource`、`appTokenStatus`
  - `signingSecretSource`、`signingSecretStatus`
- 你不需要返回原始 token 值来报告只读
  可用性。返回 `tokenStatus: "available"`（以及匹配的 source 字段）就足以满足状态类命令。
- 当某个凭证通过 SecretRef 配置，但在当前命令路径中不可用时，
  使用 `configured_unavailable`。

这样，只读命令就能报告“已配置，但在此命令路径中不可用”，
而不是崩溃或错误地将该账户报告为未配置。

## 包集合

一个插件目录可以包含带有 `openclaw.extensions` 的 `package.json`：

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

每个条目都会成为一个插件。如果该包列出多个扩展，插件 id
就会变成 `name/<fileBase>`。

如果你的插件导入了 npm 依赖，请在该目录中安装它们，
以确保 `node_modules` 可用（`npm install` / `pnpm install`）。

安全护栏：每个 `openclaw.extensions` 条目在解析 symlink 后都必须
保留在插件目录内。逃出包目录的条目
会被拒绝。

安全说明：`openclaw plugins install` 会通过
`npm install --omit=dev --ignore-scripts` 安装插件依赖（运行时不执行生命周期脚本，也不安装 dev dependencies）。请保持插件依赖树为“纯 JS / TS”，并避免依赖需要
`postinstall` 构建的包。

可选：`openclaw.setupEntry` 可以指向一个轻量级、仅用于设置的模块。
当 OpenClaw 需要为已禁用渠道插件提供设置接口，或
当某个渠道插件已启用但尚未配置时，它会加载 `setupEntry`
而不是完整插件入口。这样可以在主插件入口还会接入工具、
hooks 或其他仅运行时代码时，让启动和设置过程更轻量。

可选：`openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
可以让渠道插件在 Gateway 网关预监听启动阶段也走同样的 `setupEntry` 路径，
即使该渠道已经完成配置也是如此。

仅当 `setupEntry` 完全覆盖了网关开始监听前
必须存在的启动接口时，才使用此选项。实践中，这意味着设置入口
必须注册启动阶段所依赖的每个渠道自有能力，例如：

- 渠道注册本身
- 任何必须在 Gateway 网关开始监听前就可用的 HTTP 路由
- 任何在同一窗口期必须存在的 gateway 方法、工具或服务

如果你的完整入口仍拥有任何必需的启动能力，请不要启用
该标志。保持插件使用默认行为，让 OpenClaw 在启动期间加载
完整入口。

内置渠道还可以发布仅设置用途的契约接口辅助函数，供 core
在完整渠道运行时尚未加载前进行查询。当前的设置提升接口是：

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

当 core 需要在不加载完整插件入口的情况下，将遗留的单账户渠道
配置提升到 `channels.<id>.accounts.*` 时，就会使用该接口。
Matrix 是当前的内置示例：当命名账户已存在时，它只会将 auth / bootstrap 键
迁移到一个命名提升账户中，并且可以保留一个已配置的非规范默认账户键，
而不总是创建 `accounts.default`。

这些设置补丁适配器让内置契约接口发现保持懒加载。
导入时开销保持很轻；提升接口只会在首次使用时加载，
而不会在模块导入时重新进入内置渠道启动流程。

当这些启动接口包含 gateway RPC 方法时，请将它们保留在
插件特定前缀下。Core 管理命名空间（`config.*`、
`exec.approvals.*`、`wizard.*`、`update.*`）始终是保留的，并且总会解析为
`operator.admin`，即使某个插件请求了更窄的作用域也是如此。

示例：

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### 渠道目录元数据

渠道插件可以通过 `openclaw.channel` 声明设置 / 发现元数据，并通过
`openclaw.install` 声明安装提示。这样可以让 core 目录保持无数据状态。

示例：

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

除最小示例之外，一些有用的 `openclaw.channel` 字段还包括：

- `detailLabel`：更丰富目录 / 状态接口中的次级标签
- `docsLabel`：覆盖文档链接文本
- `preferOver`：该目录项应优先于的低优先级插件 / 渠道 id
- `selectionDocsPrefix`、`selectionDocsOmitLabel`、`selectionExtras`：选择界面的文案控制
- `markdownCapable`：将该渠道标记为支持 markdown，以便做 outbound 格式决策
- `exposure.configured`：设为 `false` 时，在已配置渠道列表接口中隐藏该渠道
- `exposure.setup`：设为 `false` 时，在交互式设置 / 配置选择器中隐藏该渠道
- `exposure.docs`：在文档导航接口中将该渠道标记为内部 / 私有
- `showConfigured` / `showInSetup`：遗留别名，出于兼容性仍接受；推荐使用 `exposure`
- `quickstartAllowFrom`：让该渠道加入标准快速开始 `allowFrom` 流程
- `forceAccountBinding`：即使只存在一个账户，也要求显式账户绑定
- `preferSessionLookupForAnnounceTarget`：在解析 announce 目标时优先使用会话查找

OpenClaw 还可以合并**外部渠道目录**（例如某个 MPM
注册表导出）。将一个 JSON 文件放到以下任一路径：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者将 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）指向
一个或多个 JSON 文件（使用逗号 / 分号 / `PATH` 分隔）。每个文件应
包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。解析器也接受 `"packages"` 或 `"plugins"` 作为 `"entries"` 键的遗留别名。

## 上下文引擎插件

上下文引擎插件拥有会话上下文的编排逻辑，包括摄取、组装
和压缩。你可以在插件中通过
`api.registerContextEngine(id, factory)` 注册它们，然后通过
`plugins.slots.contextEngine` 选择活动引擎。

当你的插件需要替换或扩展默认上下文
流水线，而不只是添加 memory 搜索或 hooks 时，请使用此方式。

```ts
export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

如果你的引擎**不**拥有压缩算法，请保持 `compact()`
实现存在，并显式委托：

```ts
import { delegateCompactionToRuntime } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages }) {
      return { messages, estimatedTokens: 0 };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## 添加新能力

当某个插件需要当前 API 无法容纳的行为时，不要通过私有内部访问
绕过插件系统。应添加缺失的能力。

推荐顺序：

1. 定义 core 契约
   明确 core 应拥有哪些共享行为：策略、回退、配置合并、
   生命周期、面向渠道的语义，以及运行时辅助函数形态。
2. 添加类型化的插件注册 / 运行时接口
   使用最小但有用的
   类型化能力接口扩展 `OpenClawPluginApi` 和 / 或 `api.runtime`。
3. 接入 core + 渠道 / 功能消费者
   渠道和功能插件应通过 core 消费新能力，
   而不是直接导入某个厂商实现。
4. 注册厂商实现
   然后由厂商插件将其后端注册到该能力上。
5. 添加契约覆盖
   添加测试，使归属关系和注册形态始终保持明确。

这就是 OpenClaw 在保持鲜明主张的同时，不会被某个
提供商的世界观硬编码束缚的方式。请参阅 [能力扩展手册](/zh-CN/plugins/architecture)
了解具体文件清单和完整示例。

### 能力清单

当你添加一个新能力时，实现通常应同时涉及以下
接口：

- `src/<capability>/types.ts` 中的 core 契约类型
- `src/<capability>/runtime.ts` 中的 core runner / 运行时辅助函数
- `src/plugins/types.ts` 中的插件 API 注册接口
- `src/plugins/registry.ts` 中的插件注册表接线
- 当功能 / 渠道插件需要消费该能力时，位于 `src/plugins/runtime/*` 中的插件运行时暴露接口
- `src/test-utils/plugin-registration.ts` 中的捕获 / 测试辅助函数
- `src/plugins/contracts/registry.ts` 中的归属 / 契约断言
- `docs/` 中面向运维人员 / 插件作者的文档

如果其中某个接口缺失，这通常意味着该能力
尚未被完整集成。

### 能力模板

最小模式：

```ts
// core 契约
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// 插件 API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// 面向功能 / 渠道插件的共享运行时辅助函数
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

契约测试模式：

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

这样规则就很简单：

- core 拥有能力契约 + 编排
- 厂商插件拥有厂商实现
- 功能 / 渠道插件消费运行时辅助函数
- 契约测试使归属关系保持明确
