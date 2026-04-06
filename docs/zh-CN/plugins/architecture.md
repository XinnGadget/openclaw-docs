---
read_when:
    - 构建或调试原生 OpenClaw 插件
    - 理解插件能力模型或归属边界
    - 处理插件加载流水线或注册表
    - 实现提供商运行时 hook 或渠道插件
sidebarTitle: Internals
summary: 插件内部机制：能力模型、归属、契约、加载流水线和运行时辅助工具
title: 插件内部机制
x-i18n:
    generated_at: "2026-04-06T15:32:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8780d364f6784e4d44b4160f5c6b24fe34aaf31dec1b6ac5b06a90d54ac0403c
    source_path: plugins/architecture.md
    workflow: 15
---

# 插件内部机制

<Info>
  这是**深度架构参考**。如需实用指南，请参阅：
  - [Install and use plugins](/zh-CN/tools/plugin) —— 用户指南
  - [入门指南](/zh-CN/plugins/building-plugins) —— 第一个插件教程
  - [Channel Plugins](/zh-CN/plugins/sdk-channel-plugins) —— 构建一个消息渠道
  - [Provider Plugins](/zh-CN/plugins/sdk-provider-plugins) —— 构建一个模型提供商
  - [SDK 概览](/zh-CN/plugins/sdk-overview) —— 导入映射和注册 API
</Info>

本页介绍 OpenClaw 插件系统的内部架构。

## 公共能力模型

能力是 OpenClaw 内部公开的**原生插件**模型。每个
原生 OpenClaw 插件都会针对一种或多种能力类型进行注册：

| Capability             | Registration method                              | Example plugins                      |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| 文本推理               | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| CLI 推理后端           | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| 语音                   | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| 实时转录               | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| 实时语音               | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| 媒体理解               | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| 图像生成               | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| 音乐生成               | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| 视频生成               | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web 抓取               | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Web 搜索               | `api.registerWebSearchProvider(...)`             | `google`                             |
| 渠道 / 消息            | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

一个注册了零个能力、但提供 hooks、工具或服务的插件，属于**旧版仅 hook** 插件。这种模式仍然完全受支持。

### 外部兼容性立场

能力模型已经在 core 中落地，并且当前已被内置 / 原生插件使用，
但外部插件兼容性仍然需要比“它已导出，因此就是冻结的”更严格的标准。

当前指导如下：

- **现有外部插件：** 保持基于 hook 的集成继续工作；将其视为
  兼容性基线
- **新的内置 / 原生插件：** 优先选择显式能力注册，而不是
  提供商特定的深度调用或新的仅 hook 设计
- **采用能力注册的外部插件：** 允许这样做，但除非文档明确将某个契约标记为稳定，否则应将能力专用辅助工具 surface 视为持续演进中

实用规则：

- 能力注册 API 是预期的发展方向
- 在过渡期间，旧版 hooks 仍然是对外部插件最安全、最不易破坏的路径
- 已导出的辅助工具子路径并不完全等价；优先使用文档化的狭窄契约，
  而不是偶然导出的辅助工具

### 插件形态

OpenClaw 会根据每个已加载插件的实际注册行为来将其归类为某种形态
（而不只是依据静态元数据）：

- **plain-capability** —— 恰好注册一种能力类型（例如仅提供商的
  插件，如 `mistral`）
- **hybrid-capability** —— 注册多种能力类型（例如
  `openai` 拥有文本推理、语音、媒体理解和图像生成）
- **hook-only** —— 只注册 hooks（类型化或自定义），没有能力、
  工具、命令或服务
- **non-capability** —— 注册工具、命令、服务或路由，但没有能力

使用 `openclaw plugins inspect <id>` 可查看插件的形态和能力细分。
详情请参阅 [CLI reference](/cli/plugins#inspect)。

### 旧版 hooks

`before_agent_start` hook 仍作为仅 hook 插件的兼容路径而受支持。
现实中的旧版插件仍依赖它。

方向如下：

- 保持其继续工作
- 在文档中将其标记为旧版
- 对于模型 / 提供商覆盖工作，优先使用 `before_model_resolve`
- 对于提示词变更工作，优先使用 `before_prompt_build`
- 只有在真实使用量下降，并且 fixture 覆盖证明迁移安全后才移除

### 兼容性信号

当你运行 `openclaw doctor` 或 `openclaw plugins inspect <id>` 时，
你可能会看到以下标签之一：

| Signal                     | Meaning                                                      |
| -------------------------- | ------------------------------------------------------------ |
| **配置有效**               | 配置可正常解析，插件也能解析                                 |
| **兼容性提示**             | 插件使用受支持但较旧的模式（例如 `hook-only`）               |
| **旧版警告**               | 插件使用 `before_agent_start`，该功能已弃用                  |
| **硬错误**                 | 配置无效或插件加载失败                                       |

`hook-only` 和 `before_agent_start` 目前都不会破坏你的插件 —— `hook-only`
只是提示，而 `before_agent_start` 只会触发警告。这些信号也会出现在
`openclaw status --all` 和 `openclaw plugins doctor` 中。

## 架构概览

OpenClaw 的插件系统由四层组成：

1. **清单 + 发现**
   OpenClaw 会从已配置路径、工作区根目录、
   全局扩展根目录以及内置扩展中查找候选插件。
   发现过程会优先读取原生 `openclaw.plugin.json` 清单以及受支持的 bundle 清单。
2. **启用 + 校验**
   Core 决定某个已发现插件是启用、禁用、阻止，还是
   被选入某个独占槽位（如 memory）。
3. **运行时加载**
   原生 OpenClaw 插件通过 jiti 在进程内加载，并将能力注册到中央注册表中。兼容 bundle 会被规范化为注册表记录，而不导入运行时代码。
4. **Surface 消费**
   OpenClaw 的其余部分读取注册表，以暴露工具、渠道、提供商
   设置、hooks、HTTP 路由、CLI 命令和服务。

对于插件 CLI，本身的根命令发现分为两个阶段：

- 解析时元数据来自 `registerCli(..., { descriptors: [...] })`
- 真正的插件 CLI 模块可以保持懒加载，并在首次调用时注册

这样既能让插件拥有自己的 CLI 代码，又能让 OpenClaw 在解析之前保留根命令名称。

重要的设计边界是：

- 发现 + 配置校验应当能够基于**清单 / schema 元数据**
  在不执行插件代码的前提下工作
- 原生运行时行为来自插件模块的 `register(api)` 路径

这种拆分使 OpenClaw 能够在完整运行时尚未激活前，校验配置、
解释缺失 / 已禁用插件，并构建 UI / schema 提示。

### 渠道插件和共享 message 工具

对于普通聊天操作，渠道插件不需要单独注册发送 / 编辑 / 反应工具。
OpenClaw 在 core 中保留一个共享的 `message` 工具，而
渠道插件拥有其背后的渠道专用发现和执行逻辑。

当前边界如下：

- core 拥有共享 `message` 工具宿主、提示词接线、session / thread
  记录和执行分发
- 渠道插件拥有作用域动作发现、能力发现，以及任何
  渠道专用 schema 片段
- 渠道插件拥有提供商专用的 session 会话语法，例如
  会话 id 如何编码 thread id，或如何从父会话继承
- 渠道插件通过其动作适配器执行最终动作

对于渠道插件，SDK surface 是
`ChannelMessageActionAdapter.describeMessageTool(...)`。这个统一的发现调用可让插件一起返回其可见动作、能力和 schema
贡献，从而避免这些部分彼此漂移。

Core 会将运行时作用域传入该发现步骤。重要字段包括：

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 可信入站 `requesterSenderId`

这对于上下文敏感插件非常重要。渠道可以根据当前活跃账户、
当前房间 / 线程 / 消息，或可信请求者身份来隐藏或暴露
消息动作，而无需在 core 的 `message` 工具中硬编码渠道专用分支。

这也是为什么嵌入式 runner 路由变更仍然是插件工作：runner
负责将当前聊天 / 会话身份转发到插件发现边界，以便共享的
`message` 工具能够为当前轮次暴露正确的渠道自有 surface。

对于渠道自有的执行辅助工具，内置插件应将执行运行时保留在
自己的扩展模块中。Core 不再在 `src/agents/tools` 下拥有
Discord、Slack、Telegram 或 WhatsApp 的消息动作运行时。
我们不会单独发布 `plugin-sdk/*-action-runtime` 子路径，内置
插件应直接从其自有扩展模块中导入本地运行时代码。

同样的边界也适用于一般性的提供商命名 SDK 接缝：core
不应导入 Slack、Discord、Signal、WhatsApp 或类似扩展的
渠道专用便捷 barrel。如果 core 需要某种行为，
要么消费内置插件自己的 `api.ts` / `runtime-api.ts` barrel，
要么将该需求提升为共享 SDK 中狭窄的通用能力。

对于投票，具体有两条执行路径：

- `outbound.sendPoll` 是适用于符合通用投票模型渠道的共享基线
- `actions.handleAction("poll")` 是渠道专用投票语义或额外投票参数的首选路径

Core 现在会等到插件投票分发拒绝该动作后，才延迟执行共享投票解析，
因此插件自有的投票处理器可以接受渠道专用投票字段，而不会先被
通用投票解析器阻塞。

完整启动顺序请参阅 [Load pipeline](#load-pipeline)。

## 能力归属模型

OpenClaw 将原生插件视为某个**公司**或某项**功能**的归属边界，
而不是一堆无关集成的杂糅包。

这意味着：

- 一个公司插件通常应拥有该公司的所有 OpenClaw 对外 surface
- 一个功能插件通常应拥有它引入的完整功能 surface
- 渠道应消费共享 core 能力，而不是临时重新实现
  提供商行为

示例：

- 内置的 `openai` 插件拥有 OpenAI 模型提供商行为，以及 OpenAI
  语音 + 实时语音 + 媒体理解 + 图像生成行为
- 内置的 `elevenlabs` 插件拥有 ElevenLabs 语音行为
- 内置的 `microsoft` 插件拥有 Microsoft 语音行为
- 内置的 `google` 插件拥有 Google 模型提供商行为，以及 Google
  媒体理解 + 图像生成 + Web 搜索行为
- 内置的 `firecrawl` 插件拥有 Firecrawl Web 抓取行为
- 内置的 `minimax`、`mistral`、`moonshot` 和 `zai` 插件拥有各自的
  媒体理解后端
- `qwen` 内置插件拥有 Qwen 文本提供商行为，以及
  媒体理解和视频生成行为
- `voice-call` 插件是一个功能插件：它拥有通话传输、工具、
  CLI、路由和 Twilio 媒体流桥接，但它消费共享的语音
  以及实时转录和实时语音能力，而不是直接导入提供商插件

期望中的最终状态是：

- OpenAI 即使跨越文本模型、语音、图像和未来视频，也仍驻留在同一个插件中
- 其他提供商也可以用同样方式拥有自己的完整 surface area
- 渠道不关心哪个提供商插件拥有该提供商；它们消费的是
  core 暴露的共享能力契约

这就是关键区别：

- **plugin** = 归属边界
- **capability** = 多个插件都可以实现或消费的 core 契约

因此，如果 OpenClaw 添加一个新领域，例如视频，首要问题不是
“哪个提供商应该硬编码视频处理？” 首要问题是“core 的视频能力契约是什么？”
一旦该契约存在，提供商插件就可以注册到它上面，
而渠道 / 功能插件也可以消费它。

如果该能力尚不存在，通常正确的做法是：

1. 在 core 中定义缺失的能力
2. 通过插件 API / 运行时以类型化方式暴露它
3. 让渠道 / 功能接入该能力
4. 让提供商插件注册实现

这样既能保持归属明确，又能避免 core 行为依赖单一提供商
或某个一次性的插件专用代码路径。

### 能力分层

在决定代码归属时，可使用以下思维模型：

- **core 能力层**：共享编排、策略、回退、配置
  合并规则、传递语义和类型化契约
- **提供商插件层**：提供商专用 API、认证、模型目录、语音
  合成、图像生成、未来的视频后端、用量端点
- **渠道 / 功能插件层**：Slack / Discord / voice-call 等集成，
  它们消费 core 能力并在某个 surface 上呈现出来

例如，TTS 遵循如下形态：

- core 拥有回复时 TTS 策略、回退顺序、偏好和渠道传递
- `openai`、`elevenlabs` 和 `microsoft` 拥有合成实现
- `voice-call` 消费电话 TTS 运行时辅助工具

未来能力也应优先遵循同样模式。

### 多能力公司插件示例

从外部看，一个公司插件应该具备内聚感。如果 OpenClaw 拥有用于
模型、语音、实时转录、实时语音、媒体理解、图像生成、视频生成、
Web 抓取和 Web 搜索的共享契约，那么一个提供商可以在同一处拥有其所有 surface：

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
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
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
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

重要的不是确切的辅助工具名称，而是整体形态：

- 一个插件拥有该提供商 surface
- core 仍然拥有能力契约
- 渠道和功能插件消费 `api.runtime.*` 辅助工具，而不是提供商代码
- 契约测试可以断言插件注册了它声称拥有的能力

### 能力示例：视频理解

OpenClaw 已经将图像 / 音频 / 视频理解视为一种共享能力。
同样的归属模型也适用于这里：

1. core 定义媒体理解契约
2. 提供商插件按需注册 `describeImage`、`transcribeAudio` 和
   `describeVideo`
3. 渠道和功能插件消费共享的 core 行为，而不是直接接线到提供商代码

这样就能避免将某个提供商的视频假设固化进 core。插件拥有
提供商 surface；core 拥有能力契约和回退行为。

视频生成也已经遵循同样顺序：core 拥有类型化能力契约和
运行时辅助工具，而提供商插件注册
`api.registerVideoGenerationProvider(...)` 实现。

需要具体的发布检查清单吗？请参阅
[能力扩展手册](/zh-CN/plugins/architecture)。

## 契约和约束执行

插件 API surface 被有意类型化并集中定义在
`OpenClawPluginApi` 中。该契约定义了受支持的注册点以及
插件可以依赖的运行时辅助工具。

其重要性在于：

- 插件作者拥有统一且稳定的内部标准
- core 可以拒绝重复归属，例如两个插件注册相同的
  provider id
- 启动阶段可以为格式错误的注册暴露可执行诊断信息
- 契约测试可以强制内置插件归属，防止无声漂移

约束执行有两层：

1. **运行时注册约束**
   插件在加载时，插件注册表会校验其注册。例如：
   重复 provider id、重复 speech provider id 和格式错误的
   注册会产生插件诊断信息，而不是未定义行为。
2. **契约测试**
   在测试运行期间，内置插件会被捕获到契约注册表中，以便
   OpenClaw 能明确断言归属。如今这用于模型
   提供商、语音提供商、Web 搜索提供商以及内置注册归属。

其实际效果是，OpenClaw 可以预先知道哪个插件拥有哪个
surface。这使 core 和渠道能够无缝组合，因为归属是声明式、
类型化且可测试的，而不是隐式的。

### 什么应属于契约

好的插件契约应当是：

- 类型化
- 小而精
- 能力专用
- 由 core 拥有
- 可被多个插件复用
- 可被渠道 / 功能消费，而无需了解提供商细节

不好的插件契约包括：

- 隐藏在 core 中的提供商专用策略
- 绕过注册表的一次性插件逃逸口
- 直接深入某个提供商实现的渠道代码
- 不属于 `OpenClawPluginApi` 或
  `api.runtime` 的临时运行时对象

如果拿不准，就提升抽象层级：先定义能力，再让插件接入它。

## 执行模型

原生 OpenClaw 插件与 Gateway 网关**运行在同一进程内**。
它们没有沙箱隔离。已加载的原生插件与 core 代码处于相同的进程级信任边界。

含义如下：

- 原生插件可以注册工具、网络处理器、hooks 和服务
- 原生插件中的 bug 可能导致 gateway 崩溃或不稳定
- 恶意原生插件等同于在 OpenClaw 进程内执行任意代码

兼容 bundle 默认更安全，因为 OpenClaw 当前将其视为
元数据 / 内容包。当前版本里，这主要指内置
Skills。

对于非内置插件，请使用 allowlist 和显式安装 / 加载路径。将
工作区插件视为开发期代码，而不是生产默认项。

对于内置工作区包名，请保持插件 id 锚定在 npm
包名中：默认使用 `@openclaw/<id>`，或者使用批准的类型后缀，如
`-provider`、`-plugin`、`-speech`、`-sandbox` 或
`-media-understanding`，前提是该包有意暴露更狭窄的插件角色。

重要信任说明：

- `plugins.allow` 信任的是**插件 id**，而不是来源出处。
- 与内置插件拥有相同 id 的工作区插件，在启用 / 加入 allowlist 后，会有意遮蔽内置副本。
- 这是一种正常且有用的机制，适用于本地开发、补丁测试和热修复。

## 导出边界

OpenClaw 导出的是能力，而不是实现便捷性。

保持能力注册为公共内容。削减非契约辅助工具导出：

- 内置插件专用辅助工具子路径
- 不打算作为公共 API 的运行时接线子路径
- 提供商专用便捷辅助工具
- 属于实现细节的 setup / onboarding 辅助工具

出于兼容性和内置插件维护需要，某些内置插件辅助工具子路径
仍保留在生成的 SDK 导出映射中。当前示例包括
`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup`，以及若干 `plugin-sdk/matrix*` 接缝。请将这些视为保留的实现细节导出，而不是新第三方插件推荐使用的 SDK 模式。

## 加载流水线

启动时，OpenClaw 大致会执行以下步骤：

1. 发现候选插件根目录
2. 读取原生或兼容 bundle 的清单和包元数据
3. 拒绝不安全的候选项
4. 规范化插件配置（`plugins.enabled`、`allow`、`deny`、`entries`、
   `slots`、`load.paths`）
5. 为每个候选项决定启用状态
6. 通过 jiti 加载已启用的原生模块
7. 调用原生 `register(api)`（或 `activate(api)` —— 旧版别名）hook，并将注册项收集到插件注册表中
8. 将注册表暴露给命令 / 运行时 surface

<Note>
`activate` 是 `register` 的旧版别名 —— 加载器会解析两者中存在的那个（`def.register ?? def.activate`），并在同一时机调用它。所有内置插件都使用 `register`；新插件请优先使用 `register`。
</Note>

安全门槛发生在**运行时执行之前**。当入口逃离插件根目录、
路径对全世界可写，或对于非内置插件而言路径归属看起来可疑时，
候选项会被阻止。

### 清单优先行为

清单是控制平面的真实来源。OpenClaw 用它来：

- 识别插件
- 发现声明的渠道 / Skills / 配置 schema 或 bundle 能力
- 校验 `plugins.entries.<id>.config`
- 增强 Control UI 标签 / 占位符
- 显示安装 / 目录元数据

对于原生插件，运行时模块是数据平面部分。它注册诸如
hooks、工具、命令或提供商流程等实际行为。

### 加载器会缓存什么

OpenClaw 会保留短期的进程内缓存，用于：

- 发现结果
- 清单注册表数据
- 已加载的插件注册表

这些缓存可减少突发式启动和重复命令开销。可以放心地将它们视为
短生命周期性能缓存，而不是持久化。

性能说明：

- 设置 `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` 或
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` 可禁用这些缓存。
- 使用 `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` 和
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` 调整缓存窗口。

## 注册表模型

已加载插件不会直接变更各种 core 全局状态。它们会注册到一个
中央插件注册表中。

该注册表会跟踪：

- 插件记录（身份、来源、出处、状态、诊断信息）
- 工具
- 旧版 hooks 和类型化 hooks
- 渠道
- 提供商
- Gateway 网关 RPC 处理器
- HTTP 路由
- CLI 注册器
- 后台服务
- 插件自有命令

随后，core 功能会从该注册表中读取，而不是直接与插件模块交互。
这让加载保持单向：

- 插件模块 -> 注册表注册
- core 运行时 -> 注册表消费

这种分离对于可维护性非常重要。它意味着多数 core surface
只需要一个集成点：“读取注册表”，而不是“为每个插件模块写特殊分支”。

## 会话绑定回调

绑定会话的插件可以在审批结果解析后作出响应。

使用 `api.onConversationBindingResolved(...)` 可在绑定请求被批准或拒绝后接收回调：

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

回调负载字段：

- `status`：`"approved"` 或 `"denied"`
- `decision`：`"allow-once"`、`"allow-always"` 或 `"deny"`
- `binding`：已批准请求对应的解析后绑定
- `request`：原始请求摘要、detach 提示、发送者 id 和
  会话元数据

此回调仅用于通知。它不会改变谁被允许绑定会话，
并且它会在 core 审批处理完成后运行。

## 提供商运行时 hooks

提供商插件现在分为两层：

- 清单元数据：`providerAuthEnvVars` 用于在运行时加载前进行廉价的环境认证查找，`providerAuthChoices` 用于在运行时加载前为新手引导 / 认证选择标签和 CLI flag 元数据提供廉价支持
- 配置时 hooks：`catalog` / 旧版 `discovery` 以及 `applyConfigDefaults`
- 运行时 hooks：`normalizeModelId`、`normalizeTransport`、
  `normalizeConfig`、
  `applyNativeStreamingUsageCompat`、`resolveConfigApiKey`、
  `resolveSyntheticAuth`、`resolveExternalAuthProfiles`、
  `shouldDeferSyntheticProfileAuth`、
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

OpenClaw 仍拥有通用智能体循环、故障转移、transcript 处理和
工具策略。这些 hooks 是提供商专用行为的扩展 surface，
无需整套自定义推理传输实现。

当某个提供商具有基于环境变量的凭证，并且希望通用认证 / 状态 / 模型选择器路径在不加载插件运行时的情况下看到它们时，请使用清单中的 `providerAuthEnvVars`。当新手引导 / 认证选择 CLI surface 应该在不加载提供商运行时的前提下了解该提供商的 choice id、分组标签和简单的单 flag 认证接线时，请使用清单中的 `providerAuthChoices`。将提供商运行时 `envVars` 保留给面向运维人员的提示，例如新手引导标签或 OAuth
client-id / client-secret 设置环境变量。

### Hook 顺序和使用场景

对于模型 / 提供商插件，OpenClaw 大致按如下顺序调用 hooks。
“何时使用”一栏是快速决策指南。

| #   | Hook                              | What it does                                                                                                   | When to use                                                                                                                                 |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | 在生成 `models.json` 期间将提供商配置发布到 `models.providers`                                                  | 提供商拥有目录或 base URL 默认值                                                                                                            |
| 2   | `applyConfigDefaults`             | 在配置实体化期间应用提供商自有的全局配置默认值                                                                  | 默认值依赖认证模式、环境或提供商模型族语义                                                                                                 |
| --  | _(内置模型查找)_                  | OpenClaw 会先尝试正常的注册表 / 目录路径                                                                        | _(不是插件 hook)_                                                                                                                           |
| 3   | `normalizeModelId`                | 在查找前规范化旧版或预览版 model-id 别名                                                                        | 提供商在规范模型解析前拥有别名清理逻辑                                                                                                     |
| 4   | `normalizeTransport`              | 在通用模型组装前规范化提供商族的 `api` / `baseUrl`                                                              | 提供商拥有同一传输族中自定义 provider id 的传输清理逻辑                                                                                   |
| 5   | `normalizeConfig`                 | 在运行时 / 提供商解析前规范化 `models.providers.<id>`                                                           | 提供商需要将配置清理逻辑与插件放在一起；内置 Google 族辅助工具也会为受支持的 Google 配置条目提供后备兼容清理                              |
| 6   | `applyNativeStreamingUsageCompat` | 对配置提供商应用原生流式用量兼容改写                                                                            | 提供商需要基于端点驱动的原生流式用量元数据修复                                                                                             |
| 7   | `resolveConfigApiKey`             | 在运行时认证加载前为配置提供商解析 env-marker 认证                                                              | 提供商拥有自有的 env-marker API 密钥解析；`amazon-bedrock` 在此处也有内置 AWS env-marker 解析器                                           |
| 8   | `resolveSyntheticAuth`            | 在不持久化明文的情况下暴露本地 / 自托管或配置支持的认证                                                         | 提供商可以使用 synthetic / 本地凭证标记运行                                                                                                |
| 9   | `resolveExternalAuthProfiles`     | 叠加提供商自有的外部认证配置文件；CLI / 应用自有凭证的默认 `persistence` 为 `runtime-only`                     | 提供商可复用外部认证凭证，而无需持久化复制后的刷新令牌                                                                                     |
| 10  | `shouldDeferSyntheticProfileAuth` | 将已存储的 synthetic 配置文件占位符置于 env / 配置支持认证之后                                                  | 提供商存储了不应具有优先级的 synthetic 占位配置文件                                                                                        |
| 11  | `resolveDynamicModel`             | 为尚未进入本地注册表的提供商自有模型 id 提供同步回退                                                            | 提供商接受任意上游模型 id                                                                                                                  |
| 12  | `prepareDynamicModel`             | 异步预热，然后再次运行 `resolveDynamicModel`                                                                    | 提供商在解析未知 id 前需要网络元数据                                                                                                       |
| 13  | `normalizeResolvedModel`          | 在嵌入式 runner 使用已解析模型前做最终改写                                                                      | 提供商需要传输改写，但仍使用 core 传输                                                                                                     |
| 14  | `contributeResolvedModelCompat`   | 为位于另一兼容传输后的提供商模型贡献兼容标志                                                                    | 提供商能在不接管提供商本身的情况下，于代理传输中识别自己的模型                                                                             |
| 15  | `capabilities`                    | 供共享 core 逻辑使用的提供商自有 transcript / 工具元数据                                                        | 提供商需要 transcript / 提供商族怪癖信息                                                                                                   |
| 16  | `normalizeToolSchemas`            | 在嵌入式 runner 看到工具 schema 之前规范化它们                                                                  | 提供商需要传输族 schema 清理                                                                                                               |
| 17  | `inspectToolSchemas`              | 在规范化后暴露提供商自有 schema 诊断信息                                                                        | 提供商希望给出关键字警告，而无需让 core 学习提供商专用规则                                                                                |
| 18  | `resolveReasoningOutputMode`      | 选择原生还是带标签的推理输出契约                                                                                | 提供商需要使用带标签的推理 / 最终输出，而不是原生字段                                                                                      |
| 19  | `prepareExtraParams`              | 在通用流选项包装器之前执行请求参数规范化                                                                        | 提供商需要默认请求参数或提供商专用参数清理                                                                                                 |
| 20  | `createStreamFn`                  | 用自定义传输完全替换正常流路径                                                                                  | 提供商需要自定义线协议，而不仅仅是包装器                                                                                                   |
| 21  | `wrapStreamFn`                    | 在应用完通用包装器后再包裹流函数                                                                                | 提供商需要请求头 / 请求体 / 模型兼容包装器，而不需要自定义传输                                                                            |
| 22  | `resolveTransportTurnState`       | 附加原生的逐轮传输头或元数据                                                                                    | 提供商希望通用传输发送提供商原生轮次身份                                                                                                   |
| 23  | `resolveWebSocketSessionPolicy`   | 附加原生 WebSocket 头或会话冷却策略                                                                             | 提供商希望通用 WS 传输调整会话头或回退策略                                                                                                 |
| 24  | `formatApiKey`                    | 认证配置文件格式化器：已存储配置文件变为运行时 `apiKey` 字符串                                                  | 提供商存储额外认证元数据，并需要自定义运行时令牌形状                                                                                       |
| 25  | `refreshOAuth`                    | 为自定义刷新端点或刷新失败策略覆盖 OAuth 刷新逻辑                                                               | 提供商不适配共享的 `pi-ai` 刷新器                                                                                                          |
| 26  | `buildAuthDoctorHint`             | 在 OAuth 刷新失败时追加修复提示                                                                                 | 提供商需要在刷新失败后给出提供商自有认证修复指引                                                                                           |
| 27  | `matchesContextOverflowError`     | 提供商自有的上下文窗口溢出错误匹配器                                                                            | 提供商有一些通用启发式无法捕捉的原始溢出错误                                                                                               |
| 28  | `classifyFailoverReason`          | 提供商自有的故障转移原因分类                                                                                    | 提供商能将原始 API / 传输错误映射为限流 / 过载等                                                                                           |
| 29  | `isCacheTtlEligible`              | 代理 / 回传提供商的提示词缓存策略                                                                               | 提供商需要代理专用缓存 TTL 门控                                                                                                            |
| 30  | `buildMissingAuthMessage`         | 替换通用缺失认证恢复消息                                                                                        | 提供商需要提供商专用的缺失认证恢复提示                                                                                                     |
| 31  | `suppressBuiltInModel`            | 过时上游模型抑制，并可选给出用户可见错误提示                                                                    | 提供商需要隐藏过时上游条目，或用提供商提示替代                                                                                             |
| 32  | `augmentModelCatalog`             | 在发现后追加 synthetic / 最终目录条目                                                                           | 提供商需要在 `models list` 和选择器中加入 synthetic 的前向兼容条目                                                                         |
| 33  | `isBinaryThinking`                | 为 binary-thinking 提供商提供开 / 关式推理切换                                                                  | 提供商只暴露二元推理开 / 关                                                                                                                |
| 34  | `supportsXHighThinking`           | 为部分模型提供 `xhigh` 推理支持                                                                                 | 提供商希望仅在部分模型上启用 `xhigh`                                                                                                       |
| 35  | `resolveDefaultThinkingLevel`     | 为特定模型族解析默认 `/think` 级别                                                                              | 提供商拥有某个模型族的默认 `/think` 策略                                                                                                   |
| 36  | `isModernModelRef`                | 用于实时配置文件过滤器和 smoke 选择的现代模型匹配器                                                             | 提供商拥有 live / smoke 首选模型匹配逻辑                                                                                                   |
| 37  | `prepareRuntimeAuth`              | 在推理前把已配置凭证交换成实际运行时令牌 / 密钥                                                                 | 提供商需要令牌交换或短期请求凭证                                                                                                           |
| 38  | `resolveUsageAuth`                | 为 `/usage` 和相关状态 surface 解析用量 / 计费凭证                                                              | 提供商需要自定义用量 / 配额令牌解析或不同的用量凭证                                                                                        |
| 39  | `fetchUsageSnapshot`              | 在认证解析后抓取并规范化提供商专用的用量 / 配额快照                                                             | 提供商需要提供商专用用量端点或负载解析器                                                                                                   |
| 40  | `createEmbeddingProvider`         | 为 memory / search 构建提供商自有 embedding 适配器                                                              | Memory embedding 行为应归属于提供商插件                                                                                                    |
| 41  | `buildReplayPolicy`               | 返回一个控制 transcript 处理的 replay 策略                                                                      | 提供商需要自定义 transcript 策略（例如剥离 thinking 块）                                                                                   |
| 42  | `sanitizeReplayHistory`           | 在通用 transcript 清理后重写 replay 历史                                                                        | 提供商需要在共享压缩辅助工具之外执行提供商专用 replay 改写                                                                                 |
| 43  | `validateReplayTurns`             | 在嵌入式 runner 之前，对 replay 轮次做最终校验或重塑                                                            | 提供商传输在通用净化后需要更严格的轮次校验                                                                                                 |
| 44  | `onModelSelected`                 | 运行提供商自有的选择后副作用                                                                                    | 提供商在模型激活时需要遥测或提供商自有状态                                                                                                 |

`normalizeModelId`、`normalizeTransport` 和 `normalizeConfig` 会先检查
匹配到的提供商插件，然后再回退到其他具备 hook 能力的提供商插件，
直到其中某一个确实改变 model id 或 transport / config。这样无需让调用方知道哪个内置插件拥有该改写，也能让
别名 / 兼容提供商 shim 正常工作。如果没有任何提供商 hook
改写受支持的 Google 族配置条目，内置 Google 配置规范化器仍会应用该兼容清理。

如果提供商需要完全自定义的线协议或自定义请求执行器，
那是另一类扩展。这些 hooks 适用于仍运行在 OpenClaw 正常推理循环上的提供商行为。

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
  `resolveDefaultThinkingLevel`、`applyConfigDefaults`、`isModernModelRef`
  和 `wrapStreamFn`，因为它拥有 Claude 4.6 前向兼容、
  提供商族提示、认证修复指引、用量端点集成、
  prompt cache 适用性、具备认证感知的配置默认值、Claude
  默认 / 自适应 thinking 策略，以及 Anthropic 专用的流整形，用于
  beta headers、`/fast` / `serviceTier` 和 `context1m`。
- Anthropic 的 Claude 专用流辅助工具目前保留在内置插件自有的
  公共 `api.ts` / `contract-api.ts` 接缝中。该包 surface
  导出 `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
  `resolveAnthropicFastMode`、`resolveAnthropicServiceTier` 以及更底层的
  Anthropic 包装器构建器，而不是为了某个提供商的 beta-header 规则扩展通用 SDK。
- OpenAI 使用 `resolveDynamicModel`、`normalizeResolvedModel` 和
  `capabilities`，以及 `buildMissingAuthMessage`、`suppressBuiltInModel`、
  `augmentModelCatalog`、`supportsXHighThinking` 和 `isModernModelRef`，
  因为它拥有 GPT-5.4 前向兼容、直接 OpenAI
  `openai-completions` -> `openai-responses` 规范化、具备 Codex 感知的认证
  提示、Spark 抑制、synthetic OpenAI 列表条目，以及 GPT-5 的 thinking /
  live-model 策略；`openai-responses-defaults` 流家族拥有共享的原生 OpenAI Responses 包装器，用于 attribution headers、
  `/fast`/`serviceTier`、文本冗长度、原生 Codex Web 搜索、
  reasoning-compat 负载整形和 Responses 上下文管理。
- OpenRouter 使用 `catalog` 以及 `resolveDynamicModel` 和
  `prepareDynamicModel`，因为该提供商是透传的，可能在
  OpenClaw 的静态目录更新之前暴露新的模型 id；它还使用
  `capabilities`、`wrapStreamFn` 和 `isCacheTtlEligible`，以使
  提供商专用请求头、路由元数据、推理补丁和
  prompt cache 策略不进入 core。它的 replay 策略来自
  `passthrough-gemini` 家族，而 `openrouter-thinking` 流家族
  拥有代理推理注入和对不支持模型 / `auto` 的跳过逻辑。
- GitHub Copilot 使用 `catalog`、`auth`、`resolveDynamicModel` 和
  `capabilities`，以及 `prepareRuntimeAuth` 和 `fetchUsageSnapshot`，
  因为它需要提供商自有的设备登录、模型回退行为、Claude transcript 怪癖、GitHub token -> Copilot token 交换，
  以及提供商自有的用量端点。
- OpenAI Codex 使用 `catalog`、`resolveDynamicModel`、
  `normalizeResolvedModel`、`refreshOAuth` 和 `augmentModelCatalog`，以及
  `prepareExtraParams`、`resolveUsageAuth` 和 `fetchUsageSnapshot`，
  因为它仍运行在 core 的 OpenAI 传输上，但拥有自己的 transport / base URL
  规范化、OAuth 刷新回退策略、默认传输选择、
  synthetic Codex 目录条目和 ChatGPT 用量端点集成；它
  与直接 OpenAI 共用同一个 `openai-responses-defaults` 流家族。
- Google AI Studio 和 Gemini CLI OAuth 使用 `resolveDynamicModel`、
  `buildReplayPolicy`、`sanitizeReplayHistory`、
  `resolveReasoningOutputMode`、`wrapStreamFn` 和 `isModernModelRef`，因为
  `google-gemini` replay 家族拥有 Gemini 3.1 前向兼容回退、
  原生 Gemini replay 校验、bootstrap replay 净化、带标签的
  推理输出模式和现代模型匹配，而
  `google-thinking` 流家族拥有 Gemini thinking 负载规范化；
  Gemini CLI OAuth 还使用 `formatApiKey`、`resolveUsageAuth` 和
  `fetchUsageSnapshot` 来处理令牌格式化、令牌解析和配额端点接线。
- Anthropic Vertex 通过
  `anthropic-by-model` replay 家族使用 `buildReplayPolicy`，
  以便 Claude 专用 replay 清理只作用于 Claude id，
  而不是作用于所有 `anthropic-messages` 传输。
- Amazon Bedrock 使用 `buildReplayPolicy`、`matchesContextOverflowError`、
  `classifyFailoverReason` 和 `resolveDefaultThinkingLevel`，因为它拥有
  适用于 Anthropic-on-Bedrock 流量的 Bedrock 专用限流 / 未就绪 / 上下文溢出错误分类；其 replay 策略仍共享同样的
  仅 Claude 的 `anthropic-by-model` 守卫。
- OpenRouter、Kilocode、Opencode 和 Opencode Go 通过 `buildReplayPolicy`
  使用 `passthrough-gemini` replay 家族，因为它们通过 OpenAI
  兼容传输代理 Gemini 模型，并且需要 Gemini
  thought-signature 净化，而不需要原生 Gemini replay 校验或
  bootstrap 改写。
- MiniMax 通过
  `hybrid-anthropic-openai` replay 家族使用 `buildReplayPolicy`，
  因为同一个提供商同时拥有 Anthropic-message 和 OpenAI 兼容语义；它在
  Anthropic 侧保留仅 Claude 的 thinking 块丢弃，同时将推理
  输出模式重写回原生，而 `minimax-fast-mode` 流家族则在共享流路径上拥有
  fast-mode 模型改写。
- Moonshot 使用 `catalog` 以及 `wrapStreamFn`，因为它仍使用共享
  OpenAI 传输，但需要提供商自有的 thinking 负载规范化；`moonshot-thinking` 流家族会将配置以及 `/think` 状态映射到其
  原生二元 thinking 负载。
- Kilocode 使用 `catalog`、`capabilities`、`wrapStreamFn` 和
  `isCacheTtlEligible`，因为它需要提供商自有的请求头、
  推理负载规范化、Gemini transcript 提示，以及 Anthropic
  cache-TTL 门控；`kilocode-thinking` 流家族会在共享代理流路径上保持 Kilo
  thinking 注入，同时跳过 `kilo/auto` 和其他不支持显式推理负载的代理模型 id。
- Z.AI 使用 `resolveDynamicModel`、`prepareExtraParams`、`wrapStreamFn`、
  `isCacheTtlEligible`、`isBinaryThinking`、`isModernModelRef`、
  `resolveUsageAuth` 和 `fetchUsageSnapshot`，因为它拥有 GLM-5 回退、
  `tool_stream` 默认值、二元 thinking UX、现代模型匹配，
  以及用量认证和配额抓取；`tool-stream-default-on` 流家族将默认开启的
  `tool_stream` 包装器从各提供商的手写胶水层中抽离出来。
- xAI 使用 `normalizeResolvedModel`、`normalizeTransport`、
  `contributeResolvedModelCompat`、`prepareExtraParams`、`wrapStreamFn`、
  `resolveSyntheticAuth`、`resolveDynamicModel` 和 `isModernModelRef`，
  因为它拥有原生 xAI Responses 传输规范化、Grok fast-mode
  别名改写、默认 `tool_stream`、strict-tool / reasoning-payload
  清理、插件自有工具的回退认证复用、前向兼容 Grok
  模型解析，以及 xAI 工具 schema profile、不支持的 schema 关键字、原生 `web_search` 和 HTML entity
  工具调用参数解码等提供商自有兼容补丁。
- Mistral、OpenCode Zen 和 OpenCode Go 仅使用 `capabilities`，以让
  transcript / 工具怪癖逻辑不进入 core。
- 仅目录型内置提供商，如 `byteplus`、`cloudflare-ai-gateway`、
  `huggingface`、`kimi-coding`、`nvidia`、`qianfan`、
  `synthetic`、`together`、`venice`、`vercel-ai-gateway` 和 `volcengine`
  仅使用 `catalog`。
- Qwen 为其文本提供商使用 `catalog`，并为其多模态 surface
  使用共享的媒体理解和视频生成注册。
- MiniMax 和 Xiaomi 使用 `catalog` 加上 usage hooks，
  因为尽管推理仍通过共享传输运行，但它们的 `/usage`
  行为归插件所有。

## 运行时辅助工具

插件可以通过 `api.runtime` 访问部分 core 辅助工具。对于 TTS：

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

- `textToSpeech` 返回适用于文件 / 语音便笺 surface 的普通 core TTS 输出负载。
- 使用 core 的 `messages.tts` 配置和提供商选择逻辑。
- 返回 PCM 音频缓冲区 + 采样率。插件必须为提供商自行重采样 / 编码。
- `listVoices` 对每个提供商来说是可选的。可将它用于提供商自有语音选择器或设置流程。
- 语音列表可包含更丰富的元数据，例如 locale、gender 和 personality tags，以便用于感知提供商的选择器。
- OpenAI 和 ElevenLabs 目前支持电话语音。Microsoft 不支持。

插件也可以通过 `api.registerSpeechProvider(...)` 注册 speech providers。

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

- 将 TTS 策略、回退和回复传递保留在 core 中。
- 使用 speech providers 来承载提供商自有合成行为。
- 旧版 Microsoft `edge` 输入会被规范化到 `microsoft` provider id。
- 首选归属模型是面向公司的：随着 OpenClaw 添加这些
  能力契约，一个提供商插件可以拥有文本、语音、图像和未来媒体提供商。

对于图像 / 音频 / 视频理解，插件应注册一个类型化的
媒体理解提供商，而不是通用键值包：

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
- 将提供商行为保留在提供商插件中。
- 增量扩展应保持类型化：新的可选方法、新的可选
  结果字段、新的可选能力。
- 视频生成也已经遵循相同模式：
  - core 拥有能力契约和运行时辅助工具
  - 提供商插件注册 `api.registerVideoGenerationProvider(...)`
  - 功能 / 渠道插件消费 `api.runtime.videoGeneration.*`

对于媒体理解运行时辅助工具，插件可以调用：

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

对于音频转录，插件可以使用媒体理解运行时，
也可以使用旧版 STT 别名：

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

说明：

- `api.runtime.mediaUnderstanding.*` 是图像 / 音频 / 视频理解的首选共享 surface。
- 使用 core 的媒体理解音频配置（`tools.media.audio`）和提供商回退顺序。
- 当未产生转录输出时返回 `{ text: undefined }`（例如输入被跳过 / 不受支持）。
- `api.runtime.stt.transcribeAudioFile(...)` 仍保留为兼容性别名。

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

- `provider` 和 `model` 是每次运行的可选覆盖项，不会持久化为 session 变更。
- OpenClaw 仅对可信调用者接受这些覆盖字段。
- 对于插件自有回退运行，运维人员必须通过 `plugins.entries.<id>.subagent.allowModelOverride: true` 显式启用。
- 使用 `plugins.entries.<id>.subagent.allowedModels` 可将可信插件限制为特定的规范化 `provider/model` 目标，或使用 `"*"` 来显式允许任意目标。
- 不可信插件的子智能体运行仍可工作，但覆盖请求会被拒绝，而不是静默回退。

对于 Web 搜索，插件可以消费共享运行时辅助工具，而不是
深入智能体工具接线层：

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
`api.registerWebSearchProvider(...)` 注册 Web 搜索提供商。

说明：

- 将提供商选择、凭证解析和共享请求语义保留在 core 中。
- 使用 Web 搜索提供商来承载提供商专用搜索传输。
- `api.runtime.webSearch.*` 是功能 / 渠道插件在不依赖智能体工具包装器的情况下需要搜索行为时的首选共享 surface。

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
- `auth`：必填。使用 `"gateway"` 以要求普通 Gateway 网关认证，或使用 `"plugin"` 以要求插件管理的认证 / webhook 校验。
- `match`：可选。`"exact"`（默认）或 `"prefix"`。
- `replaceExisting`：可选。允许同一插件替换其现有路由注册。
- `handler`：当路由处理了请求时返回 `true`。

说明：

- `api.registerHttpHandler(...)` 已移除，并会导致插件加载错误。请改用 `api.registerHttpRoute(...)`。
- 插件路由必须显式声明 `auth`。
- 除非设置 `replaceExisting: true`，否则精确的 `path + match` 冲突会被拒绝，而且一个插件不能替换另一个插件的路由。
- 不同 `auth` 级别的重叠路由会被拒绝。请仅在相同认证级别下保留 `exact` / `prefix` 的透传链。
- `auth: "plugin"` 路由**不会**自动接收运维人员运行时作用域。它们用于插件自管的 webhook / 签名校验，而不是特权 Gateway 网关辅助调用。
- `auth: "gateway"` 路由运行在 Gateway 网关请求运行时作用域中，但该作用域有意保持保守：
  - 共享密钥 bearer 认证（`gateway.auth.mode = "token"` / `"password"`）会将插件路由运行时作用域固定为 `operator.write`，即使调用方发送了 `x-openclaw-scopes`
  - 受信任的带身份 HTTP 模式（例如 `trusted-proxy` 或私有入口上的 `gateway.auth.mode = "none"`）仅在显式存在该头时才会遵守 `x-openclaw-scopes`
  - 如果这些带身份的插件路由请求中缺少 `x-openclaw-scopes`，运行时作用域会回退为 `operator.write`
- 实用规则：不要假设 gateway-auth 插件路由天然就是隐式管理员 surface。如果你的路由需要仅管理员行为，请要求使用带身份的认证模式，并记录清楚显式 `x-openclaw-scopes` 头契约。

## 插件 SDK 导入路径

在编写插件时，请使用 SDK 子路径，而不是整体式的
`openclaw/plugin-sdk` 导入：

- `openclaw/plugin-sdk/plugin-entry` 用于插件注册原语。
- `openclaw/plugin-sdk/core` 用于通用共享的面向插件契约。
- `openclaw/plugin-sdk/config-schema` 用于根 `openclaw.json` Zod schema
  导出（`OpenClawSchema`）。
- 稳定的渠道原语，例如 `openclaw/plugin-sdk/channel-setup`、
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
  `openclaw/plugin-sdk/webhook-ingress`，用于共享 setup / auth / reply / webhook
  接线。`channel-inbound` 是 debounce、mention 匹配、
  envelope 格式化和入站 envelope 上下文辅助工具的共享归属地。
  `channel-setup` 是狭窄的可选安装 setup 接缝。
  `setup-runtime` 是 `setupEntry` /
  延迟启动使用的运行时安全 setup surface，包括导入安全的 setup patch adapters。
  `setup-adapter-runtime` 是具备环境感知的账户 setup adapter 接缝。
  `setup-tools` 是小型 CLI / archive / docs 辅助工具接缝（`formatCliCommand`、
  `detectBinary`、`extractArchive`、`resolveBrewExecutable`、`formatDocsLink`、
  `CONFIG_DIR`）。
- 领域子路径，如 `openclaw/plugin-sdk/channel-config-helpers`、
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
  `openclaw/plugin-sdk/directory-runtime`，用于共享运行时 / 配置辅助工具。
  `telegram-command-config` 是 Telegram 自定义
  命令规范化 / 校验的狭窄公共接缝，即使内置
  Telegram 契约 surface 暂时不可用，它也仍可用。
  `text-runtime` 是共享的 text / markdown / logging 接缝，包括
  面向 assistant 可见文本剥离、markdown 渲染 / 分块辅助工具、脱敏
  辅助工具、directive-tag 辅助工具和安全文本实用工具。
- 审批专用的渠道接缝应优先在插件上使用一个 `approvalCapability`
  契约。然后 core 会通过该单一能力来读取审批认证、传递、渲染和
  原生路由行为，而不是将审批行为混入不相关的插件字段。
- `openclaw/plugin-sdk/channel-runtime` 已弃用，目前仅作为
  旧插件的兼容 shim 保留。新代码应导入更狭窄的通用原语，
  仓库代码也不应新增对该 shim 的导入。
- 内置扩展内部机制仍保持私有。外部插件应仅使用
  `openclaw/plugin-sdk/*` 子路径。OpenClaw core / test 代码可使用
  插件包根目录下的仓库公共入口点，例如 `index.js`、`api.js`、
  `runtime-api.js`、`setup-entry.js`，以及诸如
  `login-qr-api.js` 之类的狭窄作用域文件。绝不要从 core 或其他扩展中导入插件包的 `src/*`。
- 仓库入口点拆分：
  `<plugin-package-root>/api.js` 是辅助工具 / 类型 barrel，
  `<plugin-package-root>/runtime-api.js` 是仅运行时 barrel，
  `<plugin-package-root>/index.js` 是内置插件入口，
  `<plugin-package-root>/setup-entry.js` 是 setup 插件入口。
- 当前内置提供商示例：
  - Anthropic 使用 `api.js` / `contract-api.js` 提供 Claude 流辅助工具，
    如 `wrapAnthropicProviderStream`、beta-header 辅助工具和 `service_tier`
    解析。
  - OpenAI 使用 `api.js` 提供 provider builder、默认模型辅助工具和
    realtime provider builder。
  - OpenRouter 使用 `api.js` 提供其 provider builder 以及 onboarding / config
    辅助工具，而 `register.runtime.js` 仍可为仓库本地使用重新导出通用
    `plugin-sdk/provider-stream` 辅助工具。
- 由 facade 加载的公共入口点会优先选择活动运行时配置快照；
  如果 OpenClaw 尚未提供运行时快照，则回退到磁盘上的已解析配置文件。
- 通用共享原语仍是首选公共 SDK 契约。仍然存在一小组保留的、
  兼容性用的内置渠道品牌辅助工具接缝。请将这些视为内置维护 /
  兼容性接缝，而不是新的第三方导入目标；新的跨渠道契约仍应落在通用 `plugin-sdk/*` 子路径或插件本地 `api.js` /
  `runtime-api.js` barrel 上。

兼容性说明：

- 新代码应避免使用根 `openclaw/plugin-sdk` barrel。
- 优先使用狭窄且稳定的原语。较新的 setup / pairing / reply /
  feedback / contract / inbound / threading / command / secret-input / webhook / infra /
  allowlist / status / message-tool 子路径，是新的
  内置和外部插件工作的预期契约。
  目标解析 / 匹配应放在 `openclaw/plugin-sdk/channel-targets`。
  Message action 门控和 reaction message-id 辅助工具应放在
  `openclaw/plugin-sdk/channel-actions`。
- 内置扩展专用辅助工具 barrel 默认不稳定。如果某个
  辅助工具只被内置扩展需要，请将其保留在该扩展本地的
  `api.js` 或 `runtime-api.js` 接缝后面，而不是将其提升到
  `openclaw/plugin-sdk/<extension>` 中。
- 新的共享辅助工具接缝应当是通用的，而不是渠道品牌化的。共享目标
  解析属于 `openclaw/plugin-sdk/channel-targets`；渠道专用
  内部机制应保留在对应插件本地的 `api.js` 或 `runtime-api.js`
  接缝后面。
- 像 `image-generation`、
  `media-understanding` 和 `speech` 这样的能力专用子路径之所以存在，是因为内置 / 原生插件今天就在使用它们。它们的存在本身并不意味着每个导出的辅助工具都是长期冻结的外部契约。

## Message 工具 schema

插件应拥有渠道专用的 `describeMessageTool(...)` schema
贡献。请将提供商专用字段保留在插件中，而不要放入共享 core。

对于共享的可移植 schema 片段，请复用通过
`openclaw/plugin-sdk/channel-actions` 导出的通用辅助工具：

- `createMessageToolButtonsSchema()` 用于按钮网格式负载
- `createMessageToolCardSchema()` 用于结构化卡片负载

如果某个 schema 形状只对某一个提供商有意义，
请将它定义在该插件自己的源码中，而不要提升到共享 SDK。

## 渠道目标解析

渠道插件应拥有渠道专用的目标语义。保持共享出站宿主的通用性，
并使用消息适配器 surface 来处理提供商规则：

- `messaging.inferTargetChatType({ to })` 决定标准化目标在目录查找前
  应被视为 `direct`、`group` 还是 `channel`。
- `messaging.targetResolver.looksLikeId(raw, normalized)` 告知 core
  某个输入是否应直接跳到类 id 解析，而不是进行目录搜索。
- `messaging.targetResolver.resolveTarget(...)` 是插件的回退逻辑，
  当 core 在规范化后或目录未命中后需要做最终的提供商自有解析时使用。
- `messaging.resolveOutboundSessionRoute(...)` 在目标解析完成后，
  拥有提供商专用的 session 路由构建逻辑。

推荐拆分如下：

- 对于应在搜索 peers / groups 之前完成的类别判定，使用 `inferTargetChatType`。
- 对于“将其视为显式 / 原生目标 id”这类判断，使用 `looksLikeId`。
- 对于提供商专用的规范化回退，使用 `resolveTarget`，
  而不是把它用于宽泛的目录搜索。
- 将 chat ids、thread ids、JIDs、handles 和 room ids 这类提供商原生 id
  保留在 `target` 值或提供商专用参数中，而不是放进通用 SDK 字段。

## 配置支持的目录

那些从配置中派生目录条目的插件，应将这部分逻辑保留在插件中，
并复用 `openclaw/plugin-sdk/directory-runtime`
中的共享辅助工具。

当某个渠道需要由配置支持的 peers / groups 时，请使用这种方式，例如：

- 由 allowlist 驱动的私信 peers
- 已配置的渠道 / 群组映射
- 按账户划分的静态目录回退

`directory-runtime` 中的共享辅助工具只处理通用操作：

- 查询过滤
- 限制应用
- 去重 / 规范化辅助工具
- 构建 `ChannelDirectoryEntry[]`

渠道专用的账户检查和 id 规范化应保留在插件实现中。

## 提供商目录

提供商插件可以使用
`registerProvider({ catalog: { run(...) { ... } } })` 为推理定义模型目录。

`catalog.run(...)` 返回的形状与 OpenClaw 写入
`models.providers` 的内容相同：

- `{ provider }` 表示一个提供商条目
- `{ providers }` 表示多个提供商条目

当插件拥有提供商专用模型 id、base URL 默认值，
或受认证门控的模型元数据时，请使用 `catalog`。

`catalog.order` 控制插件目录相对于 OpenClaw
内置隐式提供商的合并时机：

- `simple`：普通 API 密钥或环境驱动的提供商
- `profile`：认证配置文件存在时出现的提供商
- `paired`：合成多个相关提供商条目的提供商
- `late`：最后一轮，在其他隐式提供商之后

较晚的提供商在键冲突时获胜，因此插件可以有意用相同的 provider id
覆盖某个内置提供商条目。

兼容性：

- `discovery` 仍可作为旧版别名使用
- 如果同时注册了 `catalog` 和 `discovery`，OpenClaw 会使用 `catalog`

## 只读渠道检查

如果你的插件注册了一个渠道，请优先同时实现
`plugin.config.inspectAccount(cfg, accountId)` 和 `resolveAccount(...)`。

原因：

- `resolveAccount(...)` 是运行时路径。它可以假定凭证
  已完全实体化，并且在必需密钥缺失时快速失败。
- 只读命令路径，例如 `openclaw status`、`openclaw status --all`、
  `openclaw channels status`、`openclaw channels resolve`，以及 doctor / 配置
  修复流程，不应仅为了描述配置就必须实体化运行时凭证。

推荐的 `inspectAccount(...)` 行为：

- 只返回描述性的账户状态。
- 保留 `enabled` 和 `configured`。
- 在相关时包含凭证来源 / 状态字段，例如：
  - `tokenSource`、`tokenStatus`
  - `botTokenSource`、`botTokenStatus`
  - `appTokenSource`、`appTokenStatus`
  - `signingSecretSource`、`signingSecretStatus`
- 你不需要仅为了报告只读可用性而返回原始令牌值。返回
  `tokenStatus: "available"`（以及匹配的来源字段）就足以支持 status 类命令。
- 当凭证通过 SecretRef 配置，但在当前命令路径中不可用时，使用 `configured_unavailable`。

这样只读命令就可以报告“已配置，但在该命令路径中不可用”，
而不会崩溃，也不会错误地将账户报告为未配置。

## Package packs

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

每个条目都会变成一个插件。如果该 pack 列出了多个扩展，则插件 id
会变成 `name/<fileBase>`。

如果你的插件导入了 npm 依赖，请在该目录中安装它们，
以便 `node_modules` 可用（`npm install` / `pnpm install`）。

安全护栏：每个 `openclaw.extensions` 条目在解析符号链接后都必须留在插件
目录内。逃离包目录的条目会被拒绝。

安全说明：`openclaw plugins install` 会使用
`npm install --omit=dev --ignore-scripts` 安装插件依赖
（无生命周期脚本，运行时也不安装 dev dependencies）。请保持插件依赖树为“纯 JS / TS”，并避免需要 `postinstall` 构建的包。

可选：`openclaw.setupEntry` 可指向一个轻量级的仅 setup 模块。
当 OpenClaw 需要为已禁用的渠道插件提供 setup surface，
或者当渠道插件已启用但尚未配置时，它会加载 `setupEntry`
而不是完整插件入口。这样在你的主插件入口还会接线工具、hooks 或其他仅运行时代码时，可以让启动和 setup 更轻量。

可选：`openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
可让渠道插件在 Gateway 网关监听前的启动阶段中，即使该渠道已经配置完成，也使用同样的 `setupEntry` 路径。

仅当 `setupEntry` 能完全覆盖 Gateway 网关开始监听前必须存在的启动 surface 时，才使用此选项。实际而言，这意味着 setup entry
必须注册启动所依赖的每一项渠道自有能力，例如：

- 渠道注册本身
- 任何必须在 Gateway 网关开始监听前可用的 HTTP 路由
- 任何在同一窗口内必须存在的 gateway 方法、工具或服务

如果你的完整入口仍拥有任何所需启动能力，请不要启用此标志。
保持插件使用默认行为，让 OpenClaw 在启动期间加载完整入口。

内置渠道也可以发布仅 setup 的契约 surface 辅助工具，供 core
在完整渠道运行时加载前查询。当前 setup 提升 surface 为：

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

当 core 需要在不加载完整插件入口的情况下，将旧版单账户渠道配置提升到
`channels.<id>.accounts.*` 时，它会使用该 surface。
Matrix 是当前内置示例：当命名账户已存在时，它只会将认证 / bootstrap 键移动到某个已命名的提升账户中，并且它可以保留已配置的非规范默认账户键，而不是始终创建
`accounts.default`。

这些 setup patch adapters 让内置契约 surface 的发现保持懒加载。
导入时保持轻量；提升 surface 只会在首次使用时加载，而不会在模块导入时重新进入内置渠道启动流程。

当这些启动 surface 包含 Gateway 网关 RPC 方法时，请将它们保留在
插件专用前缀下。Core 管理员命名空间（`config.*`、
`exec.approvals.*`、`wizard.*`、`update.*`）仍然保留，并始终解析为
`operator.admin`，即使某个插件请求了更狭窄的作用域。

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

渠道插件可以通过 `openclaw.channel` 宣传 setup / discovery 元数据，
并通过 `openclaw.install` 宣传安装提示。这使 core 目录保持无数据化。

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

除最小示例外，其他有用的 `openclaw.channel` 字段还包括：

- `detailLabel`：用于更丰富目录 / 状态 surface 的次级标签
- `docsLabel`：覆盖文档链接文本
- `preferOver`：此目录条目应优先于的低优先级插件 / 渠道 id
- `selectionDocsPrefix`、`selectionDocsOmitLabel`、`selectionExtras`：选择 surface 的文案控制字段
- `markdownCapable`：将该渠道标记为支持 markdown，以便用于出站格式决策
- `exposure.configured`：设为 `false` 时，在已配置渠道列表 surface 中隐藏该渠道
- `exposure.setup`：设为 `false` 时，在交互式 setup / configure 选择器中隐藏该渠道
- `exposure.docs`：将该渠道标记为内部 / 私有，以供文档导航 surface 使用
- `showConfigured` / `showInSetup`：为兼容性仍接受的旧版别名；优先使用 `exposure`
- `quickstartAllowFrom`：使该渠道接入标准快速开始 `allowFrom` 流程
- `forceAccountBinding`：即使只有一个账户，也要求显式账户绑定
- `preferSessionLookupForAnnounceTarget`：在解析 announce 目标时优先使用 session 查找

OpenClaw 还可以合并**外部渠道目录**（例如某个 MPM
注册表导出）。将 JSON 文件放在以下位置之一：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者将 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）指向一个或多个 JSON 文件（以逗号 / 分号 / `PATH` 分隔）。每个文件都应包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。解析器也接受 `"packages"` 或 `"plugins"` 作为 `"entries"` 键的旧版别名。

## 上下文引擎插件

上下文引擎插件拥有会话上下文的编排职责，包括摄取、组装和压缩。
在你的插件中通过
`api.registerContextEngine(id, factory)` 注册它们，然后用
`plugins.slots.contextEngine` 选择活动引擎。

当你的插件需要替换或扩展默认上下文流水线，而不只是添加
memory search 或 hooks 时，请使用这种方式。

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
已实现，并显式委托它：

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

当插件需要当前 API 无法适配的行为时，不要通过私有深度调用绕过
插件系统。请添加缺失的能力。

推荐顺序：

1. 定义 core 契约
   确定 core 应拥有的共享行为：策略、回退、配置合并、
   生命周期、面向渠道的语义以及运行时辅助工具形状。
2. 添加类型化插件注册 / 运行时 surface
   用最小但有用的类型化能力 surface 扩展 `OpenClawPluginApi` 和 / 或 `api.runtime`。
3. 接入 core + 渠道 / 功能消费者
   渠道和功能插件应通过 core 消费新能力，
   而不是直接导入某个提供商实现。
4. 注册提供商实现
   然后由提供商插件将其后端注册到该能力上。
5. 添加契约覆盖
   添加测试，以便归属和注册形状随时间保持明确。

这正是 OpenClaw 在保持明确主张的同时，又不被某个提供商世界观写死的方式。具体的文件检查清单和完整示例请参阅 [能力扩展手册](/zh-CN/plugins/architecture)。

### 能力检查清单

添加新能力时，通常应一起改动以下 surface：

- `src/<capability>/types.ts` 中的 core 契约类型
- `src/<capability>/runtime.ts` 中的 core runner / 运行时辅助工具
- `src/plugins/types.ts` 中的插件 API 注册 surface
- `src/plugins/registry.ts` 中的插件注册表接线
- 当功能 / 渠道插件需要消费它时，`src/plugins/runtime/*` 中的插件运行时暴露层
- `src/test-utils/plugin-registration.ts` 中的捕获 / 测试辅助工具
- `src/plugins/contracts/registry.ts` 中的归属 / 契约断言
- `docs/` 中的运维人员 / 插件文档

如果其中某个 surface 缺失，通常意味着这个能力尚未完全集成。

### 能力模板

最小模式：

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

契约测试模式：

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

这让规则保持简单：

- core 拥有能力契约 + 编排
- 提供商插件拥有提供商实现
- 功能 / 渠道插件消费运行时辅助工具
- 契约测试让归属保持明确
