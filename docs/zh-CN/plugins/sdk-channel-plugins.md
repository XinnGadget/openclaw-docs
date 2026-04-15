---
read_when:
    - 你正在构建一个新的消息渠道插件
    - 你想将 OpenClaw 连接到一个消息平台
    - 你需要理解 `ChannelPlugin` 适配器接口
sidebarTitle: Channel Plugins
summary: 为 OpenClaw 构建消息渠道插件的分步指南
title: 构建渠道插件
x-i18n:
    generated_at: "2026-04-15T16:36:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 80e47e61d1e47738361692522b79aff276544446c58a7b41afe5296635dfad4b
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# 构建渠道插件

本指南将带你逐步构建一个渠道插件，把 OpenClaw 连接到某个消息平台。完成后，你将拥有一个可用的渠道，具备私信安全、配对、回复线程以及出站消息能力。

<Info>
  如果你之前还没有构建过任何 OpenClaw 插件，请先阅读 [入门指南](/zh-CN/plugins/building-plugins)，了解基础包结构和清单设置。
</Info>

## 渠道插件如何工作

渠道插件不需要自己的发送/编辑/反应工具。OpenClaw 在核心中保留了一个共享的 `message` 工具。你的插件负责：

- **配置** —— 账号解析和设置向导
- **安全** —— 私信策略和允许列表
- **配对** —— 私信批准流程
- **会话语法** —— 提供商特定的会话 id 如何映射到基础聊天、线程 id 和父级回退
- **出站** —— 向平台发送文本、媒体和投票
- **线程处理** —— 如何对回复进行线程关联

核心负责共享的消息工具、提示词接线、外层会话键形状、通用的 `:thread:` 记录以及分发。

如果你的渠道添加了会携带媒体来源的消息工具参数，请通过 `describeMessageTool(...).mediaSourceParams` 暴露这些参数名。核心使用这个显式列表来进行沙箱路径规范化和出站媒体访问策略控制，因此插件不需要为提供商特定的头像、附件或封面图参数添加共享核心特例。
更推荐返回一个按 action 键控的映射，例如
`{ "set-profile": ["avatarUrl", "avatarPath"] }`，这样无关的 action 就不会继承另一个 action 的媒体参数。对于有意在所有暴露 action 之间共享的参数，扁平数组仍然可用。

如果你的平台会在会话 id 中存储额外作用域，请在插件中使用 `messaging.resolveSessionConversation(...)` 来处理这部分解析。这是把 `rawId` 映射为基础会话 id、可选线程 id、显式 `baseConversationId` 以及任何 `parentConversationCandidates` 的规范钩子。
当你返回 `parentConversationCandidates` 时，请保持它们按从最窄父级到最宽/基础会话的顺序排列。

如果内置插件在渠道注册表启动之前也需要进行同样的解析，还可以暴露一个顶层 `session-key-api.ts` 文件，并导出匹配的 `resolveSessionConversation(...)`。只有在运行时插件注册表尚不可用时，核心才会使用这个可安全引导的接口。

`messaging.resolveParentConversationCandidates(...)` 仍然可作为旧版兼容回退使用，适用于插件只需要在通用/原始 id 之上添加父级回退的情况。如果两个钩子都存在，核心会优先使用 `resolveSessionConversation(...).parentConversationCandidates`，只有当规范钩子省略它们时，才回退到 `resolveParentConversationCandidates(...)`。

## 批准与渠道能力

大多数渠道插件不需要编写与批准专门相关的代码。

- 核心负责同一聊天中的 `/approve`、共享批准按钮载荷，以及通用回退投递。
- 当渠道需要批准相关行为时，优先在渠道插件上使用单个 `approvalCapability` 对象。
- `ChannelPlugin.approvals` 已被移除。请把批准投递/原生/渲染/认证相关信息放到 `approvalCapability` 中。
- `plugin.auth` 仅用于登录/登出；核心不再从该对象读取批准认证钩子。
- `approvalCapability.authorizeActorAction` 和 `approvalCapability.getActionAvailabilityState` 是规范的批准认证接口。
- 对于同一聊天中的批准认证可用性，请使用 `approvalCapability.getActionAvailabilityState`。
- 如果你的渠道暴露原生 exec 批准，请在发起界面/原生客户端状态与同一聊天批准认证不同时，使用 `approvalCapability.getExecInitiatingSurfaceState`。核心使用这个 exec 专用钩子来区分 `enabled` 与 `disabled`，判断发起渠道是否支持原生 exec 批准，并在原生客户端回退指引中包含该渠道。`createApproverRestrictedNativeApprovalCapability(...)` 已为常见场景填充好这部分。
- 对于渠道特定的载荷生命周期行为，例如隐藏重复的本地批准提示或在投递前发送“正在输入”指示，请使用 `outbound.shouldSuppressLocalPayloadPrompt` 或 `outbound.beforeDeliverPayload`。
- 仅在原生批准路由或回退抑制时使用 `approvalCapability.delivery`。
- 对于渠道自有的原生批准事实，请使用 `approvalCapability.nativeRuntime`。在高频渠道入口点上，请通过 `createLazyChannelApprovalNativeRuntimeAdapter(...)` 保持其懒加载，这样它可以按需导入你的运行时模块，同时仍允许核心组装批准生命周期。
- 仅当某个渠道确实需要自定义批准载荷而不是使用共享渲染器时，才使用 `approvalCapability.render`。
- 当渠道希望禁用路径中的回复准确说明启用原生 exec 批准所需的配置开关时，请使用 `approvalCapability.describeExecApprovalSetup`。该钩子接收 `{ channel, channelLabel, accountId }`；具名账号渠道应渲染账号作用域路径，例如 `channels.<channel>.accounts.<id>.execApprovals.*`，而不是顶层默认值。
- 如果某个渠道能从现有配置中推断出稳定的、类似所有者的私信身份，请使用 `openclaw/plugin-sdk/approval-runtime` 中的 `createResolvedApproverActionAuthAdapter` 来限制同一聊天中的 `/approve`，而无需向核心添加批准专用逻辑。
- 如果某个渠道需要原生批准投递，请让渠道代码聚焦于目标规范化以及传输/展示事实。使用 `openclaw/plugin-sdk/approval-runtime` 中的 `createChannelExecApprovalProfile`、`createChannelNativeOriginTargetResolver`、`createChannelApproverDmTargetResolver` 和 `createApproverRestrictedNativeApprovalCapability`。把渠道特定事实放在 `approvalCapability.nativeRuntime` 后面，最好通过 `createChannelApprovalNativeRuntimeAdapter(...)` 或 `createLazyChannelApprovalNativeRuntimeAdapter(...)`，这样核心就可以组装处理器，并负责请求过滤、路由、去重、过期、Gateway 网关订阅以及“已路由到别处”的通知。`nativeRuntime` 被拆分为几个更小的接口：
- `availability` —— 账号是否已配置，以及某个请求是否应被处理
- `presentation` —— 将共享的批准视图模型映射为待处理/已解决/已过期的原生载荷或最终 action
- `transport` —— 准备目标并发送/更新/删除原生批准消息
- `interactions` —— 原生按钮或反应的可选 bind/unbind/clear-action 钩子
- `observe` —— 可选的投递诊断钩子
- 如果渠道需要运行时自有对象，例如客户端、令牌、Bolt 应用或 webhook 接收器，请通过 `openclaw/plugin-sdk/channel-runtime-context` 注册它们。通用的运行时上下文注册表让核心能够基于渠道启动状态引导能力驱动的处理器，而无需添加批准专用的包装胶水代码。
- 只有在能力驱动接口还不够表达需求时，才使用更底层的 `createChannelApprovalHandler` 或 `createChannelNativeApprovalRuntime`。
- 原生批准渠道必须通过这些辅助工具同时传递 `accountId` 和 `approvalKind`。`accountId` 可让多账号批准策略限定在正确的机器人账号范围内，而 `approvalKind` 可让渠道在不在核心中硬编码分支的情况下区分 exec 与插件批准行为。
- 核心现在也负责批准重路由通知。渠道插件不应再从 `createChannelNativeApprovalRuntime` 发送自己的“批准已发送到私信/另一个渠道”跟进消息；相反，请通过共享批准能力辅助工具暴露准确的来源 + 批准者私信路由，并让核心在向发起聊天回发任何通知之前聚合实际投递结果。
- 在端到端流程中保留已投递批准 id 的 kind。原生客户端不应根据渠道本地状态去猜测或重写 exec 与插件批准的路由。
- 不同的批准 kind 可以有意暴露不同的原生界面。
  当前内置示例：
  - Slack 对 exec 和插件 id 都保留了原生批准路由。
  - Matrix 对 exec 和插件批准使用相同的原生私信/渠道路由与反应 UX，同时仍允许认证按批准 kind 区分。
- `createApproverRestrictedNativeApprovalAdapter` 仍然作为兼容包装器存在，但新代码应优先使用能力构建器，并在插件上暴露 `approvalCapability`。

对于高频渠道入口点，当你只需要这一族中的某一部分时，优先使用更窄的运行时子路径：

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

同样地，当你不需要更宽泛的总接口时，优先选择 `openclaw/plugin-sdk/setup-runtime`、`openclaw/plugin-sdk/setup-adapter-runtime`、`openclaw/plugin-sdk/reply-runtime`、`openclaw/plugin-sdk/reply-dispatch-runtime`、`openclaw/plugin-sdk/reply-reference` 和 `openclaw/plugin-sdk/reply-chunking`。

对于设置，具体来说：

- `openclaw/plugin-sdk/setup-runtime` 包含运行时安全的设置辅助工具：
  可安全导入的设置补丁适配器（`createPatchedAccountSetupAdapter`、`createEnvPatchedAccountSetupAdapter`、`createSetupInputPresenceValidator`）、查找说明输出、`promptResolvedAllowFrom`、`splitSetupEntries`，以及委托设置代理构建器
- `openclaw/plugin-sdk/setup-adapter-runtime` 是 `createEnvPatchedAccountSetupAdapter` 所使用的窄型环境感知适配器接口
- `openclaw/plugin-sdk/channel-setup` 包含可选安装设置构建器，以及一些设置安全的基础能力：
  `createOptionalChannelSetupSurface`、`createOptionalChannelSetupAdapter`、

如果你的渠道支持由环境变量驱动的设置或认证，并且通用启动/配置流程需要在运行时加载前知道这些环境变量名称，请在插件清单中通过 `channelEnvVars` 声明它们。渠道运行时的 `envVars` 或本地常量应仅用于面向操作者的文案。
`createOptionalChannelSetupWizard`、`DEFAULT_ACCOUNT_ID`、`createTopLevelChannelDmPolicy`、`setSetupChannelEnabled`，以及
`splitSetupEntries`

- 只有当你还需要更重型的共享设置/配置辅助工具，例如 `moveSingleAccountChannelSectionToDefaultAccount(...)` 时，才使用更宽泛的 `openclaw/plugin-sdk/setup` 接口

如果你的渠道只想在设置界面中提示“请先安装这个插件”，优先使用 `createOptionalChannelSetupSurface(...)`。生成的适配器/向导会在配置写入和最终完成时默认拒绝，并在校验、完成以及文档链接文案中复用同一条“需要安装”的消息。

对于其他高频渠道路径，也应优先使用窄型辅助工具，而不是更宽泛的旧版接口：

- `openclaw/plugin-sdk/account-core`、
  `openclaw/plugin-sdk/account-id`、
  `openclaw/plugin-sdk/account-resolution` 和
  `openclaw/plugin-sdk/account-helpers`，用于多账号配置和默认账号回退
- `openclaw/plugin-sdk/inbound-envelope` 和
  `openclaw/plugin-sdk/inbound-reply-dispatch`，用于入站路由/信封以及记录与分发接线
- `openclaw/plugin-sdk/messaging-targets`，用于目标解析/匹配
- `openclaw/plugin-sdk/outbound-media` 和
  `openclaw/plugin-sdk/outbound-runtime`，用于媒体加载以及出站身份/发送委托
- `openclaw/plugin-sdk/thread-bindings-runtime`，用于线程绑定生命周期和适配器注册
- 仅当仍需要旧版智能体/媒体载荷字段布局时，才使用 `openclaw/plugin-sdk/agent-media-payload`
- `openclaw/plugin-sdk/telegram-command-config`，用于 Telegram 自定义命令规范化、重复/冲突校验，以及具备稳定回退行为的命令配置契约

仅支持认证的渠道通常可以停留在默认路径：核心处理批准，而插件只需暴露出站/认证能力。像 Matrix、Slack、Telegram 以及自定义聊天传输这类原生批准渠道，应使用共享的原生辅助工具，而不是自行实现批准生命周期。

## 入站提及策略

请将入站提及处理拆分为两层：

- 插件自有的证据收集
- 共享的策略评估

共享层请使用 `openclaw/plugin-sdk/channel-inbound`。

适合放在插件本地逻辑中的内容：

- 回复机器人检测
- 引用机器人检测
- 线程参与检查
- 服务/系统消息排除
- 用于证明机器人参与的平台原生缓存

适合使用共享辅助工具的内容：

- `requireMention`
- 显式提及结果
- 隐式提及允许列表
- 命令绕过
- 最终跳过决策

推荐流程：

1. 计算本地提及事实。
2. 将这些事实传给 `resolveInboundMentionDecision({ facts, policy })`。
3. 在你的入站门控中使用 `decision.effectiveWasMentioned`、`decision.shouldBypassMention` 和 `decision.shouldSkip`。

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions` 为已经依赖运行时注入的内置渠道插件暴露了同一组共享提及辅助工具：

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

较旧的 `resolveMentionGating*` 辅助工具仍保留在 `openclaw/plugin-sdk/channel-inbound` 中，但仅作为兼容性导出。新代码应使用 `resolveInboundMentionDecision({ facts, policy })`。

## 演练

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="包和清单">
    创建标准插件文件。`package.json` 中的 `channel` 字段决定了这是一个渠道插件。完整的包元数据接口请参见 [插件设置和配置](/zh-CN/plugins/sdk-setup#openclaw-channel)：

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "将 OpenClaw 连接到 Acme Chat。"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat 渠道插件",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="构建渠道插件对象">
    `ChannelPlugin` 接口有许多可选的适配器接口。请从最小集合开始——`id` 和 `setup`——并按需添加适配器。

    创建 `src/channel.ts`：

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // 你的平台 API 客户端

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // 私信安全：谁可以给机器人发消息
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // 配对：新私信联系人的批准流程
      pairing: {
        text: {
          idLabel: "Acme Chat 用户名",
          message: "发送此验证码以验证你的身份：",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // 线程处理：回复如何投递
      threading: { topLevelReplyToMode: "reply" },

      // 出站：向平台发送消息
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="`createChatChannelPlugin` 为你做了什么">
      你无需手动实现底层适配器接口，而是传入声明式选项，由构建器进行组合：

      | 选项 | 接线内容 |
      | --- | --- |
      | `security.dm` | 基于配置字段的作用域私信安全解析器 |
      | `pairing.text` | 基于文本验证码交换的私信配对流程 |
      | `threading` | reply-to 模式解析器（固定、账号作用域或自定义） |
      | `outbound.attachedResults` | 返回结果元数据（消息 ID）的发送函数 |

      如果你需要完全控制，也可以直接传入原始适配器对象，而不是这些声明式选项。
    </Accordion>

  </Step>

  <Step title="接线入口点">
    创建 `index.ts`：

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat 管理");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat 管理",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    请把渠道自有的 CLI 描述符放在 `registerCliMetadata(...)` 中，这样 OpenClaw 就能在不激活完整渠道运行时的情况下，在根帮助信息中显示它们；而正常完整加载时，仍会拾取相同的描述符用于真实命令注册。
    `registerFull(...)` 应保留给仅运行时需要的工作。
    如果 `registerFull(...)` 注册 Gateway 网关 RPC 方法，请使用插件特定前缀。核心管理命名空间（`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）始终保留，并始终解析为 `operator.admin`。
    `defineChannelPluginEntry` 会自动处理注册模式拆分。所有选项请参见 [入口点](/zh-CN/plugins/sdk-entrypoints#definechannelpluginentry)。

  </Step>

  <Step title="添加设置入口">
    创建 `setup-entry.ts`，用于在新手引导期间进行轻量加载：

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    当渠道被禁用或尚未配置时，OpenClaw 会加载它，而不是完整入口点。
    这样可避免在设置流程中拉入沉重的运行时代码。详情请参见 [设置和配置](/zh-CN/plugins/sdk-setup#setup-entry)。

    将设置安全导出拆分到 sidecar 模块中的内置工作区渠道，如果还需要显式的设置期运行时 setter，也可以使用 `openclaw/plugin-sdk/channel-entry-contract` 中的 `defineBundledChannelSetupEntry(...)`。

  </Step>

  <Step title="处理入站消息">
    你的插件需要从平台接收消息并转发给 OpenClaw。典型模式是使用一个 webhook 来验证请求，并通过你的渠道入站处理器进行分发：

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // 插件自管认证（你需要自己验证签名）
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // 你的入站处理器会把消息分发给 OpenClaw。
          // 具体接线方式取决于你的平台 SDK —
          // 真实示例请参考内置的 Microsoft Teams 或 Google Chat 插件包。
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      入站消息处理是渠道特定的。每个渠道插件都拥有自己的入站流水线。请查看内置渠道插件
      （例如 Microsoft Teams 或 Google Chat 插件包）了解真实模式。
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="测试">
编写同目录测试文件 `src/channel.test.ts`：

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    关于共享测试辅助工具，请参见 [测试](/zh-CN/plugins/sdk-testing)。

  </Step>
</Steps>

## 文件结构

```
<bundled-plugin-root>/acme-chat/
├── package.json              # openclaw.channel 元数据
├── openclaw.plugin.json      # 带配置 schema 的清单
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # 公共导出（可选）
├── runtime-api.ts            # 内部运行时导出（可选）
└── src/
    ├── channel.ts            # 通过 createChatChannelPlugin 定义的 ChannelPlugin
    ├── channel.test.ts       # 测试
    ├── client.ts             # 平台 API 客户端
    └── runtime.ts            # 运行时存储（如需要）
```

## 高级主题

<CardGroup cols={2}>
  <Card title="线程处理选项" icon="git-branch" href="/zh-CN/plugins/sdk-entrypoints#registration-mode">
    固定、账号作用域或自定义回复模式
  </Card>
  <Card title="消息工具集成" icon="puzzle" href="/zh-CN/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool 和 action 发现
  </Card>
  <Card title="目标解析" icon="crosshair" href="/zh-CN/plugins/architecture#channel-target-resolution">
    inferTargetChatType、looksLikeId、resolveTarget
  </Card>
  <Card title="运行时辅助工具" icon="settings" href="/zh-CN/plugins/sdk-runtime">
    通过 api.runtime 使用 TTS、STT、媒体、子智能体
  </Card>
</CardGroup>

<Note>
一些内置辅助接口仍然存在，用于内置插件维护和兼容性。
它们并不是新渠道插件的推荐模式；除非你正在直接维护该内置插件家族，否则应优先使用通用 SDK 接口中的 channel/setup/reply/runtime 子路径。
</Note>

## 后续步骤

- [提供商插件](/zh-CN/plugins/sdk-provider-plugins) —— 如果你的插件也提供模型
- [SDK 概览](/zh-CN/plugins/sdk-overview) —— 完整的子路径导入参考
- [插件 SDK 测试](/zh-CN/plugins/sdk-testing) —— 测试工具和契约测试
- [插件清单](/zh-CN/plugins/manifest) —— 完整清单 schema
