---
read_when:
    - 构建或调试原生 OpenClaw 插件时
    - 了解插件能力模型或归属边界时
    - 处理插件加载流水线或注册表时
    - 实现提供商运行时钩子或渠道插件时
sidebarTitle: Internals
summary: Plugin 内部机制：能力模型、归属关系、契约、加载流水线和运行时辅助函数
title: Plugin 内部机制
x-i18n:
    generated_at: "2026-04-05T18:16:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 70424e2745e6e289aa2e7ff899d33bea4b04f5c18bd3f73de38287f788bd939b
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin 内部机制

<Info>
  这是**深度架构参考**。如需实用指南，请参阅：
  - [安装并使用插件](/zh-CN/tools/plugin) — 用户指南
  - [入门指南](/zh-CN/plugins/building-plugins) — 第一个插件教程
  - [渠道插件](/zh-CN/plugins/sdk-channel-plugins) — 构建一个消息渠道
  - [提供商插件](/zh-CN/plugins/sdk-provider-plugins) — 构建一个模型提供商
  - [SDK 概览](/zh-CN/plugins/sdk-overview) — 导入映射与注册 API
</Info>

本页面介绍 OpenClaw 插件系统的内部架构。

## 公共能力模型

能力是 OpenClaw 内部公开的**原生插件**模型。每个原生 OpenClaw 插件都会针对一种或多种能力类型进行注册：

| 能力 | 注册方法 | 示例插件 |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| 文本推理 | `api.registerProvider(...)` | `openai`, `anthropic` |
| 语音 | `api.registerSpeechProvider(...)` | `elevenlabs`, `microsoft` |
| 实时转录 | `api.registerRealtimeTranscriptionProvider(...)` | `openai` |
| 实时语音 | `api.registerRealtimeVoiceProvider(...)` | `openai` |
| 媒体理解 | `api.registerMediaUnderstandingProvider(...)` | `openai`, `google` |
| 图像生成 | `api.registerImageGenerationProvider(...)` | `openai`, `google`, `fal`, `minimax` |
| 视频生成 | `api.registerVideoGenerationProvider(...)` | `qwen` |
| Web 抓取 | `api.registerWebFetchProvider(...)` | `firecrawl` |
| Web 搜索 | `api.registerWebSearchProvider(...)` | `google` |
| 渠道 / 消息 | `api.registerChannel(...)` | `msteams`, `matrix` |

如果某个插件注册了零个能力，但提供了 hooks、工具或服务，那么它就是一个**仅 legacy hook** 插件。该模式仍然得到完全支持。

### 对外兼容性立场

能力模型已经在 core 中落地，并且如今已被内置/原生插件使用，但外部插件的兼容性仍需要比“它已导出，因此它已冻结”更严格的标准。

当前指导原则：

- **现有外部插件：** 保持基于 hook 的集成可用；将其视为兼容性基线
- **新的内置/原生插件：** 优先使用显式能力注册，而不是面向特定厂商的深度接入或新的仅 hook 设计
- **采用能力注册的外部插件：** 允许，但除非文档明确将某个契约标记为稳定，否则应将能力专用辅助接口视为仍在演进

实践规则：

- 能力注册 API 是预期的发展方向
- 在过渡期间，legacy hook 仍然是对外部插件最安全、最不易破坏的路径
- 并非所有导出的辅助子路径都同等稳定；优先使用有文档说明的狭义契约，而不是偶然暴露的辅助导出

### Plugin 形态

OpenClaw 会根据每个已加载插件的实际注册行为来判定其形态（而不仅仅是静态元数据）：

- **plain-capability** -- 恰好注册一种能力类型（例如仅提供商插件 `mistral`）
- **hybrid-capability** -- 注册多种能力类型（例如 `openai` 同时拥有文本推理、语音、媒体理解和图像生成）
- **hook-only** -- 只注册 hooks（类型化或自定义），不注册能力、工具、命令或服务
- **non-capability** -- 注册工具、命令、服务或路由，但不注册任何能力

使用 `openclaw plugins inspect <id>` 可查看插件的形态及能力拆分详情。详见 [CLI 参考](/cli/plugins#inspect)。

### Legacy hooks

`before_agent_start` hook 仍然作为仅 hook 插件的兼容路径受到支持。现实中的 legacy 插件仍然依赖它。

方向如下：

- 保持其可用
- 将其记录为 legacy
- 对于模型/提供商覆盖工作，优先使用 `before_model_resolve`
- 对于提示词变更工作，优先使用 `before_prompt_build`
- 仅在真实使用量下降且 fixture 覆盖验证迁移安全之后再移除

### 兼容性信号

当你运行 `openclaw doctor` 或 `openclaw plugins inspect <id>` 时，可能会看到以下标签之一：

| 信号 | 含义 |
| -------------------------- | ------------------------------------------------------------ |
| **config valid** | 配置解析正常，插件可成功解析 |
| **compatibility advisory** | 插件使用了受支持但较旧的模式（例如 `hook-only`） |
| **legacy warning** | 插件使用了已弃用的 `before_agent_start` |
| **hard error** | 配置无效，或插件加载失败 |

目前，`hook-only` 和 `before_agent_start` 都不会导致你的插件损坏——`hook-only` 只是提示信息，而 `before_agent_start` 只会触发警告。这些信号也会显示在 `openclaw status --all` 和 `openclaw plugins doctor` 中。

## 架构概览

OpenClaw 的插件系统分为四层：

1. **清单 + 发现**
   OpenClaw 会从已配置路径、工作区根目录、全局扩展根目录和内置扩展中查找候选插件。发现阶段会优先读取原生 `openclaw.plugin.json` 清单以及受支持 bundle 的清单。
2. **启用 + 校验**
   Core 决定已发现插件是启用、禁用、阻止，还是被选入某个独占槽位（例如 memory）。
3. **运行时加载**
   原生 OpenClaw 插件通过 jiti 在进程内加载，并将能力注册到中央注册表中。兼容 bundle 会被标准化为注册表记录，而无需导入运行时代码。
4. **接口消费**
   OpenClaw 的其他部分读取该注册表，以暴露工具、渠道、提供商设置、hooks、HTTP 路由、CLI 命令和服务。

对于插件 CLI，根命令发现被拆分为两个阶段：

- 解析阶段元数据来自 `registerCli(..., { descriptors: [...] })`
- 真正的插件 CLI 模块可以保持惰性，并在首次调用时再注册

这样可以让插件自有的 CLI 代码保留在插件内部，同时仍让 OpenClaw 在解析前预留根命令名称。

重要的设计边界：

- 发现 + 配置校验应基于**清单/模式元数据**完成，而无需执行插件代码
- 原生运行时行为来自插件模块的 `register(api)` 路径

这种拆分使 OpenClaw 能在完整运行时尚未激活前，就完成配置校验、解释缺失/禁用的插件，并构建 UI/模式提示。

### 渠道插件与共享消息工具

渠道插件在普通聊天操作中，无需分别注册独立的发送/编辑/反应工具。OpenClaw 在 core 中保留了一个共享的 `message` 工具，而渠道插件负责其背后的渠道专属发现与执行。

当前边界如下：

- core 拥有共享 `message` 工具宿主、提示词接线、会话/线程记录和执行分发
- 渠道插件拥有作用域动作发现、能力发现以及任何渠道专属模式片段
- 渠道插件拥有提供商专属的会话对话语法，例如对话 id 如何编码线程 id，或如何从父对话继承
- 渠道插件通过其动作适配器执行最终动作

对于渠道插件，SDK 接口是
`ChannelMessageActionAdapter.describeMessageTool(...)`。这个统一的发现调用允许插件一起返回其可见动作、能力和模式贡献，从而避免这些部分发生漂移。

Core 会将运行时作用域传入该发现步骤。重要字段包括：

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- 受信任的入站 `requesterSenderId`

这对于上下文敏感型插件很重要。渠道可以根据当前活跃账号、当前房间/线程/消息，或受信任的请求者身份来隐藏或暴露消息动作，而无需在 core 的 `message` 工具中硬编码渠道专属分支。

这也是为什么嵌入式运行器路由变更仍属于插件工作：运行器负责将当前聊天/会话身份转发到插件发现边界，以便共享的 `message` 工具为当前轮次暴露正确的渠道自有接口。

对于渠道自有的执行辅助函数，内置插件应将执行运行时保留在其自身扩展模块内。Core 不再拥有位于 `src/agents/tools` 下的 Discord、Slack、Telegram 或 WhatsApp 消息动作运行时。我们不会发布单独的 `plugin-sdk/*-action-runtime` 子路径，内置插件应直接从其扩展自有模块导入本地运行时代码。

同样的边界也适用于一般意义上的提供商命名 SDK 接缝：core 不应导入面向 Slack、Discord、Signal、WhatsApp 或类似扩展的渠道专用便捷 barrel。如果 core 需要某种行为，要么消费内置插件自身的 `api.ts` / `runtime-api.ts` barrel，要么将该需求提升为共享 SDK 中一个狭义通用能力。

对于投票，当前有两条执行路径：

- `outbound.sendPoll` 是适用于符合通用投票模型的渠道的共享基线
- `actions.handleAction("poll")` 是处理渠道专属投票语义或额外投票参数的首选路径

现在，只有在插件投票分发拒绝该动作之后，core 才会延迟执行共享投票解析，因此插件自有的投票处理器可以接受渠道专属投票字段，而不会先被通用投票解析器拦住。

完整启动顺序请参阅[加载流水线](#load-pipeline)。

## 能力归属模型

OpenClaw 将一个原生插件视为某个**公司**或某项**功能**的归属边界，而不是各种无关集成的杂物袋。

这意味着：

- 一个公司插件通常应拥有该公司面向 OpenClaw 的所有接口
- 一个功能插件通常应拥有它引入的完整功能接口
- 渠道应消费共享的 core 能力，而不是临时重写提供商行为

例如：

- 内置 `openai` 插件拥有 OpenAI 模型提供商行为，以及 OpenAI 的语音 + 实时语音 + 媒体理解 + 图像生成行为
- 内置 `elevenlabs` 插件拥有 ElevenLabs 语音行为
- 内置 `microsoft` 插件拥有 Microsoft 语音行为
- 内置 `google` 插件拥有 Google 模型提供商行为，以及 Google 的媒体理解 + 图像生成 + Web 搜索行为
- 内置 `firecrawl` 插件拥有 Firecrawl Web 抓取行为
- 内置 `minimax`、`mistral`、`moonshot` 和 `zai` 插件拥有其媒体理解后端
- 内置 `qwen` 插件拥有 Qwen 文本提供商行为，以及媒体理解和视频生成行为
- `voice-call` 插件是一个功能插件：它拥有通话传输、工具、CLI、路由和 Twilio 媒体流桥接，但它消费共享的语音以及实时转录和实时语音能力，而不是直接导入厂商插件

预期的最终状态是：

- OpenAI 即使同时涵盖文本模型、语音、图像以及未来的视频，也应位于同一个插件中
- 其他厂商也可以对自己的接口范围采取同样方式
- 渠道不关心哪个厂商插件拥有该提供商；它们消费的是 core 暴露的共享能力契约

这是关键区别：

- **plugin** = 归属边界
- **capability** = 多个插件都可实现或消费的 core 契约

因此，如果 OpenClaw 新增了视频这样的领域，第一个问题不应是“哪个提供商应该硬编码视频处理？”而应是“core 的视频能力契约是什么？”一旦该契约存在，厂商插件就可以针对它进行注册，而渠道/功能插件也可以消费它。

如果该能力还不存在，通常正确的做法是：

1. 在 core 中定义缺失的能力
2. 通过插件 API/运行时以类型化方式暴露它
3. 让渠道/功能围绕该能力接线
4. 让厂商插件注册实现

这样可以保持归属明确，同时避免 core 行为依赖于某一个厂商或一次性的插件专用代码路径。

### 能力分层

在决定代码归属位置时，可使用如下心智模型：

- **core 能力层**：共享编排、策略、回退、配置合并规则、交付语义和类型化契约
- **厂商插件层**：厂商专属 API、认证、模型目录、语音合成、图像生成、未来视频后端、用量端点
- **渠道/功能插件层**：Slack/Discord/voice-call 等集成，消费 core 能力并将其呈现在某个界面上

例如，TTS 遵循如下结构：

- core 拥有回复阶段 TTS 策略、回退顺序、偏好和渠道交付
- `openai`、`elevenlabs` 和 `microsoft` 拥有合成实现
- `voice-call` 消费电话 TTS 运行时辅助函数

未来的能力也应优先采用相同模式。

### 多能力公司插件示例

一个公司插件在外部看起来应当是连贯的。如果 OpenClaw 对模型、语音、实时转录、实时语音、媒体理解、图像生成、视频生成、Web 抓取和 Web 搜索都有共享契约，那么一个厂商就可以在一个地方拥有其所有接口：

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
      // 认证/模型目录/运行时钩子
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // 厂商语音配置——直接实现 SpeechProviderPlugin 接口
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
        // 凭证 + 抓取逻辑
      }),
    );
  },
};

export default plugin;
```

关键不在于辅助函数的准确名称，而在于这种结构：

- 一个插件拥有该厂商的接口
- core 仍然拥有能力契约
- 渠道和功能插件消费 `api.runtime.*` 辅助函数，而不是厂商代码
- 契约测试可以断言该插件已注册它声称拥有的能力

### 能力示例：视频理解

OpenClaw 已经将图像/音频/视频理解视为一个共享能力。相同的归属模型也适用于这里：

1. core 定义媒体理解契约
2. 厂商插件按需注册 `describeImage`、`transcribeAudio` 和 `describeVideo`
3. 渠道和功能插件消费共享 core 行为，而不是直接接入厂商代码

这样可以避免把某一家提供商的视频假设固化进 core。插件拥有厂商接口；core 拥有能力契约和回退行为。

视频生成也已遵循同样流程：core 拥有类型化能力契约和运行时辅助函数，厂商插件针对其注册 `api.registerVideoGenerationProvider(...)` 实现。

需要具体的发布清单吗？请参阅[能力扩展手册](/zh-CN/plugins/architecture)。

## 契约与强制执行

插件 API 接口被有意设计为类型化且集中于 `OpenClawPluginApi`。该契约定义了受支持的注册点，以及插件可依赖的运行时辅助函数。

这很重要，因为：

- 插件作者获得一个稳定的内部标准
- core 可以拒绝重复归属，例如两个插件注册相同提供商 id
- 启动时可以为格式错误的注册提供可执行的诊断信息
- 契约测试可以强制内置插件归属，并防止无声漂移

强制执行分为两层：

1. **运行时注册强制执行**
   插件注册表会在插件加载时验证注册内容。例如：重复的 provider id、重复的 speech provider id，以及格式错误的注册，都会生成插件诊断信息，而不是导致未定义行为。
2. **契约测试**
   在测试运行期间，内置插件会被捕获到契约注册表中，这样 OpenClaw 就能显式断言归属关系。目前这用于模型提供商、语音提供商、Web 搜索提供商以及内置注册归属。

实际效果是，OpenClaw 能够预先知道哪个插件拥有哪个接口。这使得 core 和渠道可以无缝组合，因为归属关系是声明式、类型化并可测试的，而不是隐式的。

### 什么适合作为契约

好的插件契约应当是：

- 类型化
- 小而精
- 面向特定能力
- 由 core 拥有
- 可被多个插件复用
- 可在无需厂商知识的情况下被渠道/功能消费

不好的插件契约则是：

- 隐藏在 core 中的厂商专属策略
- 绕过注册表的一次性插件逃生口
- 渠道代码直接深入某个厂商实现
- 不属于 `OpenClawPluginApi` 或 `api.runtime` 的临时运行时对象

如有疑问，请提升抽象层级：先定义能力，再让插件接入。

## 执行模型

原生 OpenClaw 插件与 Gateway 网关**在同一进程中**运行。它们不在沙箱隔离中。已加载的原生插件与 core 代码具有相同的进程级信任边界。

这意味着：

- 原生插件可以注册工具、网络处理器、hooks 和服务
- 原生插件中的 bug 可能导致网关崩溃或不稳定
- 恶意原生插件等同于在 OpenClaw 进程内执行任意代码

兼容 bundle 默认更安全，因为 OpenClaw 当前将它们视为元数据/内容包。在当前版本中，这主要意味着内置 Skills。

对于非内置插件，应使用 allowlist 和显式安装/加载路径。将工作区插件视为开发期代码，而不是生产默认项。

对于内置工作区包名，应让插件 id 锚定在 npm 名称中：默认使用 `@openclaw/<id>`，或使用批准的类型化后缀，例如 `-provider`、`-plugin`、`-speech`、`-sandbox` 或 `-media-understanding`，前提是该包有意暴露更窄的插件角色。

重要信任说明：

- `plugins.allow` 信任的是**插件 id**，而不是来源证明。
- 若某个工作区插件与内置插件使用相同 id，那么当该工作区插件被启用/加入 allowlist 时，它会有意覆盖内置副本。
- 这是正常且有用的，适用于本地开发、补丁测试和热修复。

## 导出边界

OpenClaw 导出的是能力，而不是实现便捷层。

应保持能力注册为公共接口，同时收紧非契约辅助导出：

- 内置插件专属辅助子路径
- 无意作为公共 API 的运行时管线子路径
- 厂商专属便捷辅助函数
- 属于实现细节的 setup / onboarding 辅助函数

出于兼容性和内置插件维护需求，部分内置插件辅助子路径仍保留在生成的 SDK 导出映射中。当前示例包括
`plugin-sdk/feishu`、`plugin-sdk/feishu-setup`、`plugin-sdk/zalo`、
`plugin-sdk/zalo-setup` 以及若干 `plugin-sdk/matrix*` 接缝。应将它们视为保留的实现细节导出，而不是推荐给新的第三方插件使用的 SDK 模式。

## 加载流水线

启动时，OpenClaw 大致会执行以下步骤：

1. 发现候选插件根目录
2. 读取原生或兼容 bundle 的清单与包元数据
3. 拒绝不安全候选项
4. 规范化插件配置（`plugins.enabled`、`allow`、`deny`、`entries`、
   `slots`、`load.paths`）
5. 决定每个候选项的启用状态
6. 通过 jiti 加载已启用的原生模块
7. 调用原生 `register(api)`（或 `activate(api)`——一个 legacy 别名）hook，并将注册内容收集到插件注册表中
8. 将注册表暴露给命令/运行时接口

<Note>
`activate` 是 `register` 的 legacy 别名——加载器会解析存在的那个（`def.register ?? def.activate`），并在同一时机调用它。所有内置插件都使用 `register`；新插件应优先使用 `register`。
</Note>

安全门禁发生在**运行时执行之前**。当入口逃逸出插件根目录、路径对所有人可写，或对于非内置插件而言路径归属看起来可疑时，候选项会被阻止。

### Manifest-first 行为

清单是控制平面的事实来源。OpenClaw 使用它来：

- 识别插件
- 发现声明的渠道/Skills/配置模式或 bundle 能力
- 校验 `plugins.entries.<id>.config`
- 增强 Control UI 标签/占位符
- 显示安装/目录元数据

对于原生插件，运行时模块是数据平面部分。它负责注册实际行为，例如 hooks、工具、命令或提供商流程。

### 加载器会缓存什么

OpenClaw 为以下内容保留短期进程内缓存：

- 发现结果
- 清单注册表数据
- 已加载的插件注册表

这些缓存可减少突发启动开销和重复命令负担。你可以将它们视为短生命周期的性能缓存，而不是持久化机制。

性能说明：

- 设置 `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` 或
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` 可禁用这些缓存。
- 可通过 `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` 和
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` 调整缓存窗口。

## 注册表模型

已加载插件不会直接修改各种随机的 core 全局状态。它们会注册到中央插件注册表中。

注册表跟踪：

- 插件记录（身份、来源、源头、状态、诊断）
- 工具
- legacy hooks 和类型化 hooks
- 渠道
- 提供商
- Gateway 网关 RPC 处理器
- HTTP 路由
- CLI 注册器
- 后台服务
- 插件自有命令

之后，core 功能会从该注册表中读取，而不是直接与插件模块对话。这样可保持单向加载：

- 插件模块 -> 注册表注册
- core 运行时 -> 注册表消费

这种分离对可维护性非常重要。它意味着大多数 core 接口只需要一个集成点：“读取注册表”，而不是“为每个插件模块写特殊分支”。

## 会话绑定回调

绑定会话的插件可以在审批结果解析后作出响应。

使用 `api.onConversationBindingResolved(...)` 可在绑定请求被批准或拒绝后接收回调：

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // 现在该插件 + 会话已存在一个绑定。
        console.log(event.binding?.conversationId);
        return;
      }

      // 请求被拒绝；清理本地待处理状态。
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

回调负载字段：

- `status`：`"approved"` 或 `"denied"`
- `decision`：`"allow-once"`、`"allow-always"` 或 `"deny"`
- `binding`：用于已批准请求的已解析绑定
- `request`：原始请求摘要、分离提示、发送者 id 和会话元数据

此回调仅用于通知。它不会改变谁被允许绑定会话，并且会在 core 完成审批处理之后运行。

## 提供商运行时钩子

提供商插件现在分为两层：

- 清单元数据：`providerAuthEnvVars` 用于在运行时加载前进行低成本环境认证查找，`providerAuthChoices` 用于在运行时加载前提供低成本的新手引导/认证选项标签和 CLI flag 元数据
- 配置阶段 hooks：`catalog` / legacy `discovery` 以及 `applyConfigDefaults`
- 运行时 hooks：`normalizeModelId`、`normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`、`resolveConfigApiKey`,
  `resolveSyntheticAuth`、`shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`、`prepareDynamicModel`、`normalizeResolvedModel`,
  `contributeResolvedModelCompat`、`capabilities`,
  `normalizeToolSchemas`、`inspectToolSchemas`,
  `resolveReasoningOutputMode`、`prepareExtraParams`、`createStreamFn`,
  `wrapStreamFn`、`resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`、`formatApiKey`、`refreshOAuth`,
  `buildAuthDoctorHint`、`matchesContextOverflowError`,
  `classifyFailoverReason`、`isCacheTtlEligible`,
  `buildMissingAuthMessage`、`suppressBuiltInModel`、`augmentModelCatalog`,
  `isBinaryThinking`、`supportsXHighThinking`,
  `resolveDefaultThinkingLevel`、`isModernModelRef`、`prepareRuntimeAuth`,
  `resolveUsageAuth`、`fetchUsageSnapshot`、`createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`、`validateReplayTurns`、`onModelSelected`

OpenClaw 仍然拥有通用智能体循环、故障切换、转录处理和工具策略。这些 hooks 是提供商专属行为的扩展接口，而无需实现完整的自定义推理传输层。

当提供商具有基于环境变量的凭证，且通用认证/状态/模型选择器路径需要在不加载插件运行时的前提下识别它们时，请使用清单中的 `providerAuthEnvVars`。当新手引导/认证选择 CLI 接口需要在不加载提供商运行时的前提下了解该提供商的 choice id、分组标签和简单的单 flag 认证接线时，请使用清单中的 `providerAuthChoices`。将提供商运行时的 `envVars` 保留给面向运维者的提示，例如新手引导标签或 OAuth client id / client secret 设置环境变量。

### Hook 顺序与使用方式

对于模型/提供商插件，OpenClaw 大致按以下顺序调用 hooks。
“何时使用”列是快速决策指南。

| #   | Hook | 作用 | 何时使用 |
| --- | --------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog` | 在生成 `models.json` 期间将提供商配置发布到 `models.providers` 中 | 提供商拥有目录或 base URL 默认值时 |
| 2   | `applyConfigDefaults` | 在配置实体化期间应用提供商自有的全局配置默认值 | 默认值依赖认证模式、环境或提供商模型族语义时 |
| --  | _(built-in model lookup)_ | OpenClaw 会先尝试常规注册表/目录路径 | _(不是插件 hook)_ |
| 3   | `normalizeModelId` | 在查找前规范化 legacy 或预览版 model-id 别名 | 提供商在规范模型解析前拥有别名清理逻辑时 |
| 4   | `normalizeTransport` | 在通用模型组装前规范化提供商族的 `api` / `baseUrl` | 提供商在同一传输族内拥有自定义 provider id 的传输清理逻辑时 |
| 5   | `normalizeConfig` | 在运行时/提供商解析前规范化 `models.providers.<id>` | 提供商需要将配置清理逻辑保留在插件中；内置 Google 系辅助函数也会为受支持的 Google 配置项兜底 |
| 6   | `applyNativeStreamingUsageCompat` | 将原生流式用量兼容重写应用到配置提供商 | 提供商需要基于端点的原生流式用量元数据修复时 |
| 7   | `resolveConfigApiKey` | 在运行时认证加载前，为配置提供商解析 env-marker 认证 | 提供商拥有自有的 env-marker API key 解析逻辑；`amazon-bedrock` 在这里也有内置 AWS env-marker 解析器 |
| 8   | `resolveSyntheticAuth` | 在不持久化明文的前提下暴露本地/自托管或配置支持的认证 | 提供商可以使用合成/本地凭证标记运行时 |
| 9   | `shouldDeferSyntheticProfileAuth` | 让存储的合成 profile 占位符优先级低于环境/配置支持的认证 | 提供商存储了不应抢占优先级的合成占位 profile 时 |
| 10  | `resolveDynamicModel` | 针对尚未在本地注册表中的提供商自有 model id 执行同步回退 | 提供商接受任意上游 model id 时 |
| 11  | `prepareDynamicModel` | 异步预热，然后再次运行 `resolveDynamicModel` | 提供商需要先获取网络元数据才能解析未知 id 时 |
| 12  | `normalizeResolvedModel` | 在嵌入式运行器使用已解析模型前做最终重写 | 提供商需要传输重写，但仍使用 core 传输时 |
| 13  | `contributeResolvedModelCompat` | 为另一兼容传输背后的厂商模型补充兼容标记 | 提供商能在代理传输上识别自己的模型，而无需接管该提供商时 |
| 14  | `capabilities` | 提供商自有的转录/工具元数据，供共享 core 逻辑使用 | 提供商有转录或提供商族专属差异时 |
| 15  | `normalizeToolSchemas` | 在嵌入式运行器看到工具模式前进行规范化 | 提供商需要传输族的模式清理逻辑时 |
| 16  | `inspectToolSchemas` | 在规范化后暴露提供商自有的模式诊断信息 | 提供商希望给出关键字警告，而无需让 core 理解提供商专属规则 |
| 17  | `resolveReasoningOutputMode` | 选择原生还是标签化的推理输出契约 | 提供商需要标签化推理/最终输出，而不是原生字段时 |
| 18  | `prepareExtraParams` | 在通用流式选项包装器之前进行请求参数规范化 | 提供商需要默认请求参数或按提供商清理参数时 |
| 19  | `createStreamFn` | 用自定义传输完全替代普通流路径 | 提供商需要自定义线协议，而不只是一个包装器时 |
| 20  | `wrapStreamFn` | 在通用包装器应用后包装流函数 | 提供商需要请求头/请求体/模型兼容包装器，而无需自定义传输时 |
| 21  | `resolveTransportTurnState` | 附加原生的每轮传输请求头或元数据 | 提供商希望通用传输发送其原生轮次身份信息时 |
| 22  | `resolveWebSocketSessionPolicy` | 附加原生 WebSocket 请求头或会话冷却策略 | 提供商希望通用 WS 传输调整会话请求头或回退策略时 |
| 23  | `formatApiKey` | 认证 profile 格式化器：将存储的 profile 转换为运行时 `apiKey` 字符串 | 提供商存储额外认证元数据并需要自定义运行时 token 形态时 |
| 24  | `refreshOAuth` | 覆盖 OAuth 刷新逻辑以支持自定义刷新端点或刷新失败策略 | 提供商不适配共享的 `pi-ai` 刷新器时 |
| 25  | `buildAuthDoctorHint` | 在 OAuth 刷新失败时附加修复提示 | 提供商需要在刷新失败后提供其自有认证修复指导时 |
| 26  | `matchesContextOverflowError` | 提供商自有的上下文窗口溢出错误匹配器 | 提供商有原始溢出错误，而通用启发式无法识别时 |
| 27  | `classifyFailoverReason` | 提供商自有的故障切换原因分类 | 提供商可以将原始 API/传输错误映射为限流/过载等类型时 |
| 28  | `isCacheTtlEligible` | 面向代理/回程提供商的提示词缓存策略 | 提供商需要代理专属的缓存 TTL 门控时 |
| 29  | `buildMissingAuthMessage` | 替换通用缺失认证恢复消息 | 提供商需要专属的缺失认证恢复提示时 |
| 30  | `suppressBuiltInModel` | 过时上游模型隐藏，可附带面向用户的错误提示 | 提供商需要隐藏过时上游目录项，或用厂商提示替换它们时 |
| 31  | `augmentModelCatalog` | 在发现后追加合成/最终目录项 | 提供商需要在 `models list` 和选择器中追加合成的前向兼容目录项时 |
| 32  | `isBinaryThinking` | 面向二元 thinking 提供商的开/关推理切换 | 提供商只暴露二元 thinking 开/关时 |
| 33  | `supportsXHighThinking` | 为选定模型提供 `xhigh` 推理支持 | 提供商只希望在某些模型上启用 `xhigh` 时 |
| 34  | `resolveDefaultThinkingLevel` | 为特定模型族解析默认 `/think` 等级 | 提供商拥有某个模型族的默认 `/think` 策略时 |
| 35  | `isModernModelRef` | 用于 live profile 过滤和 smoke 选择的现代模型匹配器 | 提供商拥有 live/smoke 首选模型匹配逻辑时 |
| 36  | `prepareRuntimeAuth` | 在推理前将已配置凭证交换为实际运行时 token/key | 提供商需要 token 交换或短期请求凭证时 |
| 37  | `resolveUsageAuth` | 为 `/usage` 及相关状态接口解析用量/计费凭证 | 提供商需要自定义用量/配额 token 解析或使用不同的用量凭证时 |
| 38  | `fetchUsageSnapshot` | 在认证解析后获取并规范化提供商专属的用量/配额快照 | 提供商需要提供商专属用量端点或负载解析器时 |
| 39  | `createEmbeddingProvider` | 为 memory/search 构建提供商自有的 embedding 适配器 | memory embedding 行为应归属于提供商插件 |
| 40  | `buildReplayPolicy` | 返回控制该提供商转录处理的 replay 策略 | 提供商需要自定义转录策略（例如剥离 thinking 块）时 |
| 41  | `sanitizeReplayHistory` | 在通用转录清理后重写 replay 历史 | 提供商需要超出共享压缩辅助函数范围的专属 replay 重写时 |
| 42  | `validateReplayTurns` | 在嵌入式运行器之前对 replay turn 做最终校验或重塑 | 提供商传输需要在通用清理后执行更严格的轮次校验时 |
| 43  | `onModelSelected` | 在模型变为活跃后运行提供商自有的后置副作用 | 提供商需要在模型选定时执行遥测或其自有状态逻辑时 |

`normalizeModelId`、`normalizeTransport` 和 `normalizeConfig` 会先检查匹配到的提供商插件，然后继续尝试其他具备相应 hook 能力的提供商插件，直到某个插件实际修改 model id 或 transport/config。这样可以让别名/兼容提供商 shim 正常工作，而无需调用方知道哪个内置插件拥有该重写逻辑。如果没有任何提供商 hook 重写受支持的 Google 系配置项，内置 Google 配置规范化器仍会执行兼容性清理。

如果提供商需要完全自定义的线协议或自定义请求执行器，那属于另一类扩展。这些 hooks 适用于仍运行在 OpenClaw 常规推理循环上的提供商行为。

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
  提供商族提示、认证修复指导、用量端点集成、
  提示词缓存资格、考虑认证状态的配置默认值、Claude 的
  默认/自适应 thinking 策略，以及针对 beta headers、`/fast` / `serviceTier`
  和 `context1m` 的 Anthropic 专属流包装。
- Anthropic 的 Claude 专属流辅助函数目前仍保留在该内置插件自己的
  公共 `api.ts` / `contract-api.ts` 接缝中。该包接口导出了
  `wrapAnthropicProviderStream`、`resolveAnthropicBetas`、
  `resolveAnthropicFastMode`、`resolveAnthropicServiceTier` 以及更底层的
  Anthropic wrapper builder，而没有为了单一提供商的 beta-header 规则去扩大通用 SDK。
- OpenAI 使用 `resolveDynamicModel`、`normalizeResolvedModel` 和
  `capabilities`，以及 `buildMissingAuthMessage`、`suppressBuiltInModel`、
  `augmentModelCatalog`、`supportsXHighThinking` 和 `isModernModelRef`，
  因为它拥有 GPT-5.4 前向兼容、直接的 OpenAI
  `openai-completions` -> `openai-responses` 规范化、面向 Codex 的认证
  提示、Spark 抑制、合成 OpenAI 目录项，以及 GPT-5 的 thinking /
  live-model 策略；`openai-responses-defaults` 流族则拥有共享的原生 OpenAI Responses 包装器，用于 attribution headers、
  `/fast`/`serviceTier`、文本冗长度、原生 Codex Web 搜索、
  reasoning-compat 负载整形，以及 Responses 上下文管理。
- OpenRouter 使用 `catalog` 以及 `resolveDynamicModel` 和
  `prepareDynamicModel`，因为该提供商是透传型的，可能会在 OpenClaw 的静态目录更新前就暴露新的
  model id；它还使用 `capabilities`、`wrapStreamFn` 和 `isCacheTtlEligible`
  来让提供商专属请求头、路由元数据、推理补丁和
  提示词缓存策略留在 core 之外。其 replay 策略来自
  `passthrough-gemini` 族，而 `openrouter-thinking` 流族
  则拥有代理推理注入与不支持模型 / `auto` 跳过逻辑。
- GitHub Copilot 使用 `catalog`、`auth`、`resolveDynamicModel` 和
  `capabilities`，以及 `prepareRuntimeAuth` 和 `fetchUsageSnapshot`，因为它
  需要提供商自有的设备登录、模型回退行为、Claude 转录差异、
  GitHub token -> Copilot token 交换，以及提供商自有的用量端点。
- OpenAI Codex 使用 `catalog`、`resolveDynamicModel`、
  `normalizeResolvedModel`、`refreshOAuth` 和 `augmentModelCatalog`，以及
  `prepareExtraParams`、`resolveUsageAuth` 和 `fetchUsageSnapshot`，因为它
  仍运行在 core OpenAI 传输之上，但拥有其传输/base URL 规范化、
  OAuth 刷新回退策略、默认传输选择、合成 Codex 目录项，以及 ChatGPT 用量端点集成；它与直接 OpenAI 共享同一个
  `openai-responses-defaults` 流族。
- Google AI Studio 和 Gemini CLI OAuth 使用 `resolveDynamicModel`、
  `buildReplayPolicy`、`sanitizeReplayHistory`、
  `resolveReasoningOutputMode`、`wrapStreamFn` 和 `isModernModelRef`，因为
  `google-gemini` replay 族拥有 Gemini 3.1 前向兼容回退、
  原生 Gemini replay 校验、bootstrap replay 清理、标签化
  推理输出模式，以及现代模型匹配，而
  `google-thinking` 流族拥有 Gemini thinking 负载规范化；
  Gemini CLI OAuth 还使用 `formatApiKey`、`resolveUsageAuth` 和
  `fetchUsageSnapshot` 来处理 token 格式化、token 解析和配额端点接线。
- Anthropic Vertex 通过
  `anthropic-by-model` replay 族使用 `buildReplayPolicy`，使 Claude 专属 replay 清理仅作用于 Claude id，而非所有 `anthropic-messages` 传输。
- Amazon Bedrock 使用 `buildReplayPolicy`、`matchesContextOverflowError`、
  `classifyFailoverReason` 和 `resolveDefaultThinkingLevel`，因为它拥有
  Bedrock 专属的限流/未就绪/上下文溢出错误分类逻辑，
  用于 Anthropic-on-Bedrock 流量；它的 replay 策略仍共享同一个仅 Claude 的
  `anthropic-by-model` 防护。
- OpenRouter、Kilocode、Opencode 和 Opencode Go 通过 `passthrough-gemini` replay 族使用 `buildReplayPolicy`，
  因为它们通过 OpenAI 兼容传输代理 Gemini 模型，并需要 Gemini
  thought-signature 清理，而不需要原生 Gemini replay 校验或
  bootstrap 重写。
- MiniMax 通过
  `hybrid-anthropic-openai` replay 族使用 `buildReplayPolicy`，因为一个提供商同时拥有 Anthropic-message 和 OpenAI 兼容语义；它在 Anthropic 侧保留仅 Claude 的
  thinking 块丢弃逻辑，同时将推理输出模式重新覆盖为原生，而
  `minimax-fast-mode` 流族则在共享流路径上拥有 fast-mode 模型重写。
- Moonshot 使用 `catalog` 以及 `wrapStreamFn`，因为它仍使用共享的
  OpenAI 传输，但需要提供商自有的 thinking 负载规范化；而
  `moonshot-thinking` 流族会将配置和 `/think` 状态映射为其
  原生二元 thinking 负载。
- Kilocode 使用 `catalog`、`capabilities`、`wrapStreamFn` 和
  `isCacheTtlEligible`，因为它需要提供商自有的请求头、
  推理负载规范化、Gemini 转录提示和 Anthropic
  缓存 TTL 门控；`kilocode-thinking` 流族会在共享代理流路径上保持 Kilo thinking 注入，同时跳过 `kilo/auto` 和
  其他不支持显式推理负载的代理 model id。
- Z.AI 使用 `resolveDynamicModel`、`prepareExtraParams`、`wrapStreamFn`、
  `isCacheTtlEligible`、`isBinaryThinking`、`isModernModelRef`、
  `resolveUsageAuth` 和 `fetchUsageSnapshot`，因为它拥有 GLM-5 回退、
  `tool_stream` 默认值、二元 thinking 用户体验、现代模型匹配，以及
  用量认证 + 配额获取；`tool-stream-default-on` 流族则让默认开启的
  `tool_stream` 包装器不必写成每个提供商手写的胶水代码。
- xAI 使用 `normalizeResolvedModel`、`normalizeTransport`、
  `contributeResolvedModelCompat`、`prepareExtraParams`、`wrapStreamFn`、
  `resolveSyntheticAuth`、`resolveDynamicModel` 和 `isModernModelRef`，
  因为它拥有原生 xAI Responses 传输规范化、Grok fast-mode
  别名重写、默认 `tool_stream`、严格工具 / 推理负载
  清理、用于插件自有工具的回退认证复用、前向兼容的 Grok
  模型解析，以及提供商自有兼容补丁，例如 xAI 工具模式
  配置、不支持的模式关键字、原生 `web_search`，以及 HTML 实体
  工具调用参数解码。
- Mistral、OpenCode Zen 和 OpenCode Go 仅使用 `capabilities`，以便将
  转录/工具差异保留在 core 之外。
- 仅目录型的内置提供商，如 `byteplus`、`cloudflare-ai-gateway`、
  `huggingface`、`kimi-coding`、`nvidia`、`qianfan`、
  `synthetic`、`together`、`venice`、`vercel-ai-gateway` 和 `volcengine`，
  仅使用 `catalog`。
- Qwen 为其文本提供商使用 `catalog`，并为其多模态接口注册共享的媒体理解和
  视频生成能力。
- MiniMax 和 Xiaomi 使用 `catalog` 以及用量 hooks，因为尽管推理仍通过共享传输执行，但其 `/usage`
  行为归插件所有。

## 运行时辅助函数

插件可以通过 `api.runtime` 访问部分 core 辅助函数。对于 TTS：

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

- `textToSpeech` 返回用于文件/语音笔记界面的标准 core TTS 输出负载。
- 使用 core `messages.tts` 配置和提供商选择逻辑。
- 返回 PCM 音频缓冲区 + 采样率。插件必须为提供商执行重采样/编码。
- `listVoices` 对每个提供商而言是可选的。可将其用于厂商自有语音选择器或设置流程。
- 语音列表可包含更丰富的元数据，例如 locale、gender 和 personality tags，供提供商感知型选择器使用。
- 当前 OpenAI 和 ElevenLabs 支持电话场景。Microsoft 不支持。

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
- legacy Microsoft `edge` 输入会被规范化为 `microsoft` provider id。
- 首选归属模型是按公司组织：随着 OpenClaw 增加这些能力契约，一个厂商插件可以同时拥有
  文本、语音、图像和未来的媒体提供商。

对于图像/音频/视频理解，插件应注册一个类型化的
媒体理解提供商，而不是泛化的 key/value 包：

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

- 将编排、回退、配置和渠道接线保留在 core。
- 将厂商行为保留在提供商插件中。
- 增量扩展应保持类型化：新增可选方法、新增可选结果字段、新增可选能力。
- 视频生成已经遵循相同模式：
  - core 拥有能力契约和运行时辅助函数
  - 厂商插件注册 `api.registerVideoGenerationProvider(...)`
  - 功能/渠道插件消费 `api.runtime.videoGeneration.*`

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

对于音频转录，插件既可以使用媒体理解运行时，也可以使用旧的 STT 别名：

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // 当 MIME 无法可靠推断时可选：
  mime: "audio/ogg",
});
```

说明：

- `api.runtime.mediaUnderstanding.*` 是图像/音频/视频理解的首选共享接口。
- 使用 core 媒体理解音频配置（`tools.media.audio`）和提供商回退顺序。
- 当未生成转录输出时（例如输入被跳过/不受支持），返回 `{ text: undefined }`。
- `api.runtime.stt.transcribeAudioFile(...)` 仍保留为兼容别名。

插件还可以通过 `api.runtime.subagent` 发起后台子智能体运行：

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

- `provider` 和 `model` 是可选的单次运行覆盖项，不会持久改变会话设置。
- OpenClaw 仅对受信任调用方接受这些覆盖字段。
- 对于插件自有回退运行，运维者必须通过 `plugins.entries.<id>.subagent.allowModelOverride: true` 显式启用。
- 使用 `plugins.entries.<id>.subagent.allowedModels` 可将受信任插件限制为特定规范 `provider/model` 目标，或设为 `"*"` 以显式允许任意目标。
- 不受信任的插件子智能体运行仍然可用，但覆盖请求会被拒绝，而不是静默回退。

对于 Web 搜索，插件可以消费共享运行时辅助函数，而不是
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
`api.registerWebSearchProvider(...)` 注册 Web 搜索提供商。

说明：

- 将提供商选择、凭证解析和共享请求语义保留在 core 中。
- 使用 Web 搜索提供商承载厂商专属搜索传输。
- `api.runtime.webSearch.*` 是功能/渠道插件在需要搜索行为而不依赖智能体工具包装器时的首选共享接口。

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
- `auth`：必填。使用 `"gateway"` 表示需要常规 Gateway 网关认证，或使用 `"plugin"` 表示由插件管理认证/webhook 校验。
- `match`：可选。`"exact"`（默认）或 `"prefix"`。
- `replaceExisting`：可选。允许同一插件替换自己已有的路由注册。
- `handler`：当路由处理了请求时返回 `true`。

说明：

- `api.registerHttpHandler(...)` 已被移除，并会导致插件加载错误。请改用 `api.registerHttpRoute(...)`。
- 插件路由必须显式声明 `auth`。
- 除非设置 `replaceExisting: true`，否则精确的 `path + match` 冲突会被拒绝，而且一个插件不能替换另一个插件的路由。
- 具有不同 `auth` 级别的重叠路由会被拒绝。请仅在相同认证级别内保留 `exact`/`prefix` 的贯穿链。
- `auth: "plugin"` 路由**不会**自动获得运维者运行时作用域。它们用于插件自主管理的 webhook/签名校验，而不是特权 Gateway 网关辅助调用。
- `auth: "gateway"` 路由会在 Gateway 网关请求运行时作用域内运行，但该作用域被有意设计为保守：
  - 共享密钥 bearer 认证（`gateway.auth.mode = "token"` / `"password"`）会将插件路由运行时作用域固定为 `operator.write`，即使调用方发送了 `x-openclaw-scopes`
  - 受信任的身份承载型 HTTP 模式（例如 `trusted-proxy`，或私有入口上的 `gateway.auth.mode = "none"`）仅在显式存在该请求头时才会遵循 `x-openclaw-scopes`
  - 如果这些身份承载型插件路由请求中缺少 `x-openclaw-scopes`，运行时作用域会回退为 `operator.write`
- 实践规则：不要假设一个使用 gateway-auth 的插件路由天然就是管理员接口。如果你的路由需要仅管理员可用的行为，请要求使用身份承载型认证模式，并记录显式的 `x-openclaw-scopes` 请求头契约。

## Plugin SDK 导入路径

在编写插件时，请使用 SDK 子路径，而不是单体式的 `openclaw/plugin-sdk` 导入：

- `openclaw/plugin-sdk/plugin-entry` 用于插件注册原语。
- `openclaw/plugin-sdk/core` 用于通用共享的面向插件契约。
- `openclaw/plugin-sdk/config-schema` 用于根级 `openclaw.json` Zod 模式导出（`OpenClawSchema`）。
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
  `openclaw/plugin-sdk/webhook-ingress`，用于共享的设置/认证/回复/webhook
  接线。`channel-inbound` 是 debounce、mention 匹配、
  envelope 格式化和入站 envelope 上下文辅助函数的共享归属路径。
  `channel-setup` 是狭义的可选安装 setup 接缝。
  `setup-runtime` 是 `setupEntry` /
  延迟启动所使用的运行时安全 setup 接口，包括导入安全的 setup patch 适配器。
  `setup-adapter-runtime` 是感知环境的账号 setup 适配器接缝。
  `setup-tools` 是小型 CLI/归档/文档辅助函数接缝（`formatCliCommand`、
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
  `openclaw/plugin-sdk/directory-runtime`，用于共享的运行时/配置辅助函数。
  `telegram-command-config` 是 Telegram 自定义命令规范化/校验的狭义公共接缝，即使内置 Telegram 契约接口暂时不可用，它也仍然可用。
  `text-runtime` 是共享的文本/Markdown/日志接缝，包括
  assistant 可见文本剥离、Markdown 渲染/分块辅助函数、脱敏
  辅助函数、directive-tag 辅助函数和安全文本工具。
- 审批专用渠道接缝应优先使用插件上的单个 `approvalCapability`
  契约。然后 core 会通过该单一能力读取审批认证、交付、渲染和
  原生路由行为，而不是将审批行为混入不相关的插件字段。
- `openclaw/plugin-sdk/channel-runtime` 已弃用，仅作为旧插件的兼容 shim 保留。新代码应改为导入更狭义的通用原语，仓库代码也不应新增对该 shim 的导入。
- 内置扩展内部实现仍为私有。外部插件应仅使用 `openclaw/plugin-sdk/*` 子路径。OpenClaw core / 测试代码可以使用插件包根目录下的仓库公共入口点，例如 `index.js`、`api.js`、
  `runtime-api.js`、`setup-entry.js` 以及狭义文件如
  `login-qr-api.js`。绝不可从 core 或其他扩展中导入某个插件包的 `src/*`。
- 仓库入口点拆分：
  `<plugin-package-root>/api.js` 是辅助函数/类型 barrel，
  `<plugin-package-root>/runtime-api.js` 是仅运行时 barrel，
  `<plugin-package-root>/index.js` 是内置插件入口，
  `<plugin-package-root>/setup-entry.js` 是 setup 插件入口。
- 当前内置提供商示例：
  - Anthropic 使用 `api.js` / `contract-api.js` 提供 Claude 流辅助函数，例如
    `wrapAnthropicProviderStream`、beta-header 辅助函数和 `service_tier`
    解析。
  - OpenAI 使用 `api.js` 提供 provider builder、默认模型辅助函数和
    realtime provider builder。
  - OpenRouter 使用 `api.js` 提供其 provider builder 以及 onboarding/config
    辅助函数，而 `register.runtime.js` 仍可以为仓库本地用途重新导出通用
    `plugin-sdk/provider-stream` 辅助函数。
- Facade 加载的公共入口点会优先使用当前活跃的运行时配置快照；
  如果 OpenClaw 尚未提供运行时快照，则回退到磁盘上的已解析配置文件。
- 通用共享原语仍是首选的公共 SDK 契约。当前仍保留一小组
  面向内置渠道品牌的兼容辅助接缝。应将它们视为内置维护/兼容接缝，而不是新的第三方导入目标；新的跨渠道契约仍应落在
  通用 `plugin-sdk/*` 子路径或插件本地的 `api.js` /
  `runtime-api.js` barrel 上。

兼容性说明：

- 新代码应避免使用根级 `openclaw/plugin-sdk` barrel。
- 优先使用狭义稳定原语。较新的 setup / pairing / reply /
  feedback / contract / inbound / threading / command / secret-input / webhook / infra /
  allowlist / status / message-tool 子路径，是新的
  内置和外部插件工作的预期契约。
  目标解析/匹配应放在 `openclaw/plugin-sdk/channel-targets`。
  消息动作门控和 reaction message-id 辅助函数应放在
  `openclaw/plugin-sdk/channel-actions`。
- 内置扩展专属辅助 barrel 默认不稳定。如果某个
  辅助函数只被某个内置扩展需要，请将它保留在该扩展本地的
  `api.js` 或 `runtime-api.js` 接缝后，而不是提升到
  `openclaw/plugin-sdk/<extension>`。
- 新的共享辅助接缝应当是通用的，而不是带渠道品牌的。共享目标
  解析应放在 `openclaw/plugin-sdk/channel-targets`；渠道专属
  内部实现应保留在所属插件的本地 `api.js` 或 `runtime-api.js`
  接缝后。
- `image-generation`、
  `media-understanding` 和 `speech` 这样的能力专用子路径之所以存在，
  是因为内置/原生插件今天确实在使用它们。但它们的存在本身并不意味着每个导出的辅助函数都是长期冻结的外部契约。

## 消息工具模式

插件应拥有渠道专属的 `describeMessageTool(...)` 模式
贡献。请将提供商专属字段保留在插件中，而不是放入共享 core。

对于可共享的可移植模式片段，请复用通过
`openclaw/plugin-sdk/channel-actions` 导出的通用辅助函数：

- `createMessageToolButtonsSchema()` 用于按钮网格风格负载
- `createMessageToolCardSchema()` 用于结构化卡片负载

如果某种模式形状只适用于某一个提供商，请将其定义在该插件自己的
源代码中，而不是提升到共享 SDK 中。

## 渠道目标解析

渠道插件应拥有渠道专属的目标语义。请让共享 outbound host 保持通用，并通过消息适配器接口处理提供商规则：

- `messaging.inferTargetChatType({ to })` 决定规范化目标在目录查找前
  应被视为 `direct`、`group` 还是 `channel`。
- `messaging.targetResolver.looksLikeId(raw, normalized)` 告诉 core
  某个输入是否应跳过目录搜索，直接走类 id 解析。
- `messaging.targetResolver.resolveTarget(...)` 是当 core 在规范化后或目录未命中后需要最终提供商自有解析时的插件回退。
- `messaging.resolveOutboundSessionRoute(...)` 在目标解析完成后拥有提供商专属的会话路由构造逻辑。

建议拆分如下：

- 对于应在搜索 peers/groups 之前执行的类别判定，使用 `inferTargetChatType`。
- 对于“将其视为显式/原生目标 id”的判断，使用 `looksLikeId`。
- 将 `resolveTarget` 用于提供商专属的规范化回退，而不是广泛的目录搜索。
- 将提供商原生 id，例如 chat id、thread id、JID、handle 和 room id，保留在 `target` 值或提供商专属参数中，而不是放入通用 SDK 字段。

## 基于配置的目录

从配置派生目录项的插件应将该逻辑保留在插件内，并复用
`openclaw/plugin-sdk/directory-runtime` 中的共享辅助函数。

当渠道需要以下基于配置的 peers/groups 时，请使用此方式：

- 由 allowlist 驱动的私信 peers
- 已配置的渠道/群组映射
- 按账号划分的静态目录回退

`directory-runtime` 中的共享辅助函数仅处理通用操作：

- 查询过滤
- limit 应用
- 去重/规范化辅助函数
- 构建 `ChannelDirectoryEntry[]`

渠道专属的账号检查和 id 规范化应保留在插件实现中。

## 提供商目录

提供商插件可以通过
`registerProvider({ catalog: { run(...) { ... } } })` 为推理定义模型目录。

`catalog.run(...)` 返回的结构与 OpenClaw 写入
`models.providers` 的形状一致：

- `{ provider }` 用于一个 provider 项
- `{ providers }` 用于多个 provider 项

当插件拥有提供商专属 model id、base URL 默认值或受认证控制的模型元数据时，请使用 `catalog`。

`catalog.order` 控制插件目录相对于 OpenClaw 内置隐式提供商的合并时机：

- `simple`：普通 API key 或环境驱动的提供商
- `profile`：存在 auth profiles 时出现的提供商
- `paired`：合成多个相关 provider 项的提供商
- `late`：最后一轮，在其他隐式提供商之后

发生 key 冲突时，后出现的 provider 获胜，因此插件可以有意覆盖具有相同 provider id 的内置 provider 项。

兼容性：

- `discovery` 仍然可作为 legacy 别名使用
- 如果同时注册了 `catalog` 和 `discovery`，OpenClaw 会使用 `catalog`

## 只读渠道检查

如果你的插件注册了一个渠道，建议在实现 `resolveAccount(...)` 的同时，也实现
`plugin.config.inspectAccount(cfg, accountId)`。

原因：

- `resolveAccount(...)` 是运行时路径。它可以假定凭证已完全实体化，并在缺少必要 Secret 时快速失败。
- `openclaw status`、`openclaw status --all`、
  `openclaw channels status`、`openclaw channels resolve` 以及 Doctor、配置修复流程等只读命令路径，不应仅为了描述配置就去实体化运行时凭证。

推荐的 `inspectAccount(...)` 行为：

- 只返回描述性的账号状态。
- 保留 `enabled` 和 `configured`。
- 在相关时包含凭证来源/状态字段，例如：
  - `tokenSource`、`tokenStatus`
  - `botTokenSource`、`botTokenStatus`
  - `appTokenSource`、`appTokenStatus`
  - `signingSecretSource`、`signingSecretStatus`
- 你无需为了报告只读可用性而返回原始 token 值。只返回 `tokenStatus: "available"`（以及匹配的来源字段）就足以支持状态类命令。
- 当凭证通过 SecretRef 配置、但在当前命令路径中不可用时，请使用 `configured_unavailable`。

这样可让只读命令报告“已配置，但在该命令路径中不可用”，而不是崩溃或错误地报告该账号未配置。

## 包集合

插件目录可以包含带有 `openclaw.extensions` 的 `package.json`：

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

每个条目都会成为一个插件。如果该 pack 列出多个扩展，则插件 id
会变为 `name/<fileBase>`。

如果你的插件导入 npm 依赖，请在该目录中安装它们，
以确保 `node_modules` 可用（`npm install` / `pnpm install`）。

安全护栏：每个 `openclaw.extensions` 条目在解析符号链接后都必须仍位于插件
目录内。任何逃逸出包目录的条目都会被拒绝。

安全说明：`openclaw plugins install` 会使用
`npm install --omit=dev --ignore-scripts` 安装插件依赖
（不运行生命周期脚本，运行时不安装 dev dependencies）。请保持插件依赖树为“纯 JS/TS”，并避免依赖需要 `postinstall` 构建的包。

可选：`openclaw.setupEntry` 可指向一个轻量级的仅 setup 模块。
当 OpenClaw 需要为一个已禁用的渠道插件提供 setup 接口，或者
某个渠道插件已启用但尚未完成配置时，它会加载 `setupEntry`，
而不是完整插件入口。这样可以让启动和 setup 更轻量，
特别是在你的主插件入口还会接线工具、hooks 或其他仅运行时代码时。

可选：`openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
允许渠道插件在 Gateway 网关预监听启动阶段也选择走同一个 `setupEntry` 路径，即使该渠道已经配置完成。

仅当 `setupEntry` 已完整覆盖 Gateway 网关开始监听前必须存在的启动接口时才应使用此选项。实际而言，这意味着 setup entry
必须注册启动所依赖的所有渠道自有能力，例如：

- 渠道注册本身
- 任何必须在 Gateway 网关开始监听前可用的 HTTP 路由
- 在同一阶段必须存在的任何 Gateway 网关方法、工具或服务

如果你的完整入口仍拥有任何必需的启动能力，请不要启用此标志。
保留默认行为，让 OpenClaw 在启动期间加载完整入口。

内置渠道还可以发布仅 setup 的契约接口辅助函数，以便 core 在完整渠道运行时加载前进行查询。当前的 setup 提升接口为：

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

当 core 需要在不加载完整插件入口的情况下，将 legacy 单账号渠道配置提升到
`channels.<id>.accounts.*` 时，会使用这套接口。Matrix 是当前的内置示例：当已存在命名账号时，它只会将认证/bootstrap 键迁移到某个被提升的命名账号中，并且可以保留一个已配置的非规范默认账号键，而不是总是创建
`accounts.default`。

这些 setup patch 适配器让内置契约接口发现保持惰性。导入时开销保持较轻；提升接口只会在首次使用时加载，而不会在模块导入时重新进入内置渠道启动流程。

当这些启动接口包含 Gateway 网关 RPC 方法时，请将它们保留在
插件专属前缀下。Core 管理员命名空间（`config.*`、
`exec.approvals.*`、`wizard.*`、`update.*`）仍被保留，并且始终解析为 `operator.admin`，即使某个插件请求更窄的作用域也是如此。

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

渠道插件可以通过 `openclaw.channel` 声明 setup / 发现元数据，并通过 `openclaw.install` 声明安装提示。这让 core 保持无目录数据。

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

除最小示例外，有用的 `openclaw.channel` 字段还包括：

- `detailLabel`：用于更丰富目录/状态界面的次级标签
- `docsLabel`：覆盖文档链接文本
- `preferOver`：该目录项应优先于的较低优先级插件/渠道 id
- `selectionDocsPrefix`、`selectionDocsOmitLabel`、`selectionExtras`：选择界面的文案控制
- `markdownCapable`：将该渠道标记为支持 Markdown，以便出站格式化决策
- `showConfigured`：设为 `false` 时，在已配置渠道列表界面中隐藏该渠道
- `quickstartAllowFrom`：让该渠道接入标准快速开始 `allowFrom` 流程
- `forceAccountBinding`：即使只存在一个账号，也要求显式账号绑定
- `preferSessionLookupForAnnounceTarget`：在解析公告目标时优先使用会话查找

OpenClaw 还可以合并**外部渠道目录**（例如某个 MPM
注册表导出）。将 JSON 文件放在以下任一位置：

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

或者将 `OPENCLAW_PLUGIN_CATALOG_PATHS`（或 `OPENCLAW_MPM_CATALOG_PATHS`）指向一个或多个 JSON 文件（使用逗号/分号/`PATH` 分隔）。每个文件应包含 `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`。解析器也接受 `"packages"` 或 `"plugins"` 作为 `"entries"` 键的 legacy 别名。

## 上下文引擎插件

上下文引擎插件拥有会话上下文编排逻辑，包括摄取、组装和压缩。请在你的插件中通过
`api.registerContextEngine(id, factory)` 注册它们，然后使用
`plugins.slots.contextEngine` 选择活跃引擎。

当你的插件需要替换或扩展默认上下文流水线，而不仅仅是添加 memory 搜索或 hooks 时，请使用此方式。

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

如果你的引擎**并不**拥有压缩算法，请保持 `compact()`
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

当某个插件需要当前 API 无法表达的行为时，不要通过私有深度接入来绕过插件系统。请添加缺失的能力。

推荐顺序：

1. 定义 core 契约
   明确哪些共享行为应由 core 拥有：策略、回退、配置合并、
   生命周期、面向渠道的语义以及运行时辅助函数形态。
2. 添加类型化插件注册/运行时接口
   用最小但有用的类型化能力接口扩展 `OpenClawPluginApi` 和/或 `api.runtime`。
3. 接线 core + 渠道/功能消费者
   渠道和功能插件应通过 core 消费该新能力，
   而不是直接导入某个厂商实现。
4. 注册厂商实现
   然后由厂商插件针对该能力注册其后端实现。
5. 添加契约覆盖
   添加测试，以便归属关系和注册形态能长期保持明确。

这就是 OpenClaw 如何在保持明确产品立场的同时，不被某家
提供商的世界观硬编码。具体文件清单和完整示例请参阅[能力扩展手册](/zh-CN/plugins/architecture)。

### 能力清单

当你添加一个新能力时，实现通常应同时覆盖以下接口：

- `src/<capability>/types.ts` 中的 core 契约类型
- `src/<capability>/runtime.ts` 中的 core 运行器/运行时辅助函数
- `src/plugins/types.ts` 中的插件 API 注册接口
- `src/plugins/registry.ts` 中的插件注册表接线
- 当功能/渠道插件需要消费它时，位于 `src/plugins/runtime/*` 的插件运行时暴露层
- `src/test-utils/plugin-registration.ts` 中的捕获/测试辅助函数
- `src/plugins/contracts/registry.ts` 中的归属/契约断言
- `docs/` 中面向运维者/插件作者的文档

如果这些接口中有某一个缺失，通常说明该能力还没有被完整集成。

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

// 面向功能/渠道插件的共享运行时辅助函数
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
- 厂商插件拥有厂商实现
- 功能/渠道插件消费运行时辅助函数
- 契约测试让归属关系保持明确
