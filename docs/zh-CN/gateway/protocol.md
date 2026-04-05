---
read_when:
    - 实现或更新 Gateway 网关 WS 客户端
    - 调试协议不匹配或连接失败
    - 重新生成协议 schema / 模型
summary: Gateway 网关 WebSocket 协议：握手、帧、版本控制
title: Gateway 网关协议
x-i18n:
    generated_at: "2026-04-05T22:12:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: c37f5b686562dda3ba3516ac6982ad87b2f01d8148233284e9917099c6e96d87
    source_path: gateway/protocol.md
    workflow: 15
---

# Gateway 网关协议（WebSocket）

Gateway 网关 WS 协议是 OpenClaw 的**单一控制平面 + 节点传输协议**。所有客户端（CLI、Web UI、macOS 应用、iOS / Android 节点、无头节点）都通过 WebSocket 连接，并在握手时声明其**角色**和**作用域**。

## 传输

- WebSocket，带 JSON 负载的文本帧。
- 第一帧**必须**是 `connect` 请求。

## 握手（connect）

Gateway 网关 → 客户端（预连接质询）：

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

客户端 → Gateway 网关：

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway 网关 → 客户端：

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

当签发设备令牌时，`hello-ok` 还会包含：

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

在受信任的 bootstrap 交接期间，`hello-ok.auth` 还可能在 `deviceTokens` 中包含额外的受限角色条目：

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

对于内置的 node / operator bootstrap 流程，主 node 令牌保持为 `scopes: []`，任何交接出去的 operator 令牌都会限制在 bootstrap operator 允许列表内（`operator.approvals`、`operator.read`、`operator.talk.secrets`、`operator.write`）。Bootstrap 作用域检查仍保持角色前缀：operator 条目仅满足 operator 请求，非 operator 角色仍需要其自身角色前缀下的作用域。

### Node 示例

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## 帧格式

- **请求**：`{type:"req", id, method, params}`
- **响应**：`{type:"res", id, ok, payload|error}`
- **事件**：`{type:"event", event, payload, seq?, stateVersion?}`

有副作用的方法需要**幂等键**（见 schema）。

## 角色 + 作用域

### 角色

- `operator` = 控制平面客户端（CLI / UI / 自动化）。
- `node` = 能力宿主（camera / screen / canvas / system.run）。

### 作用域（operator）

常见作用域：

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

带有 `includeSecrets: true` 的 `talk.config` 需要 `operator.talk.secrets`（或 `operator.admin`）。

插件注册的 Gateway 网关 RPC 方法可以请求它们自己的 operator 作用域，但保留的核心管理员前缀（`config.*`、`exec.approvals.*`、`wizard.*`、`update.*`）始终解析为 `operator.admin`。

方法作用域只是第一道门槛。通过 `chat.send` 到达的一些斜杠命令还会叠加更严格的命令级检查。例如，持久化的 `/config set` 和 `/config unset` 写入需要 `operator.admin`。

`node.pair.approve` 在基础方法作用域之上也有额外的审批时作用域检查：

- 无命令请求：`operator.pairing`
- 带非 exec node 命令的请求：`operator.pairing` + `operator.write`
- 包含 `system.run`、`system.run.prepare` 或 `system.which` 的请求：
  `operator.pairing` + `operator.admin`

### caps / commands / permissions（node）

节点在连接时声明能力主张：

- `caps`：高层能力类别。
- `commands`：用于 invoke 的命令允许列表。
- `permissions`：细粒度开关（例如 `screen.record`、`camera.capture`）。

Gateway 网关将这些视为**声明**，并在服务端强制执行允许列表。

## 在线状态

- `system-presence` 返回按设备身份作为键的条目。
- 在线状态条目包含 `deviceId`、`roles` 和 `scopes`，因此 UI 即使在同一设备同时以 **operator** 和 **node** 身份连接时，也能显示为单行。

## 常见 RPC 方法族

本页不是自动生成的完整导出，但公开的 WS 接口比上面的握手 / auth 示例更广。这些是 Gateway 网关当前公开的主要方法族。

`hello-ok.features.methods` 是基于 `src/gateway/server-methods-list.ts` 以及已加载的插件 / 渠道方法导出构建的保守发现列表。请将其视为功能发现，而不是 `src/gateway/server-methods/*.ts` 中每个可调用辅助函数的自动生成完整导出。

### 系统和身份

- `health` 返回缓存的或刚探测到的 gateway 健康快照。
- `status` 返回 `/status` 风格的 gateway 摘要；敏感字段仅对具有 admin 作用域的 operator 客户端返回。
- `gateway.identity.get` 返回 relay 和 pairing 流程使用的 gateway 设备身份。
- `system-presence` 返回当前已连接 operator / node 设备的在线状态快照。
- `system-event` 追加一条系统事件，并可更新 / 广播在线状态上下文。
- `last-heartbeat` 返回最近一次持久化的 heartbeat 事件。
- `set-heartbeats` 切换 gateway 上的 heartbeat 处理。

### 模型和用量

- `models.list` 返回运行时允许的模型目录。
- `usage.status` 返回提供商用量窗口 / 剩余额度摘要。
- `usage.cost` 返回指定日期范围的聚合成本用量摘要。
- `doctor.memory.status` 返回当前默认智能体工作区的向量记忆 / embedding 就绪状态。
- `sessions.usage` 返回按会话划分的用量摘要。
- `sessions.usage.timeseries` 返回单个会话的时间序列用量。
- `sessions.usage.logs` 返回单个会话的用量日志条目。

### 渠道和登录辅助方法

- `channels.status` 返回内置 + 内置插件渠道 / 插件的状态摘要。
- `channels.logout` 在渠道支持登出的情况下，登出特定渠道 / 账号。
- `web.login.start` 为当前支持 QR / Web 登录的 Web 渠道提供商启动 QR / Web 登录流程。
- `web.login.wait` 等待该 QR / Web 登录流程完成，并在成功后启动渠道。
- `push.test` 向已注册的 iOS node 发送测试 APNs 推送。
- `voicewake.get` 返回已存储的唤醒词触发器。
- `voicewake.set` 更新唤醒词触发器并广播变更。

### 消息和日志

- `send` 是面向渠道 / 账号 / 线程目标的直接出站投递 RPC，用于 chat runner 之外的发送。
- `logs.tail` 返回已配置 gateway 文件日志的尾部内容，并带有 cursor / limit 和 max-byte 控制。

### Talk 和 TTS

- `talk.config` 返回生效中的 Talk 配置负载；`includeSecrets` 需要 `operator.talk.secrets`（或 `operator.admin`）。
- `talk.mode` 为 WebChat / Control UI 客户端设置 / 广播当前 Talk 模式状态。
- `talk.speak` 通过当前激活的 Talk speech 提供商合成语音。
- `tts.status` 返回 TTS 启用状态、当前提供商、回退提供商以及提供商配置状态。
- `tts.providers` 返回可见的 TTS 提供商清单。
- `tts.enable` 和 `tts.disable` 切换 TTS 偏好状态。
- `tts.setProvider` 更新首选 TTS 提供商。
- `tts.convert` 执行一次性文本转语音转换。

### Secrets、配置、更新和向导

- `secrets.reload` 重新解析当前生效的 SecretRef，并仅在完全成功时替换运行时 secret 状态。
- `secrets.resolve` 为特定命令 / 目标集合解析命令目标 secret 分配。
- `config.get` 返回当前配置快照和哈希值。
- `config.set` 写入经过校验的配置负载。
- `config.patch` 合并部分配置更新。
- `config.apply` 校验并替换完整配置负载。
- `config.schema` 返回 Control UI 和 CLI 工具使用的实时配置 schema 负载：schema、`uiHints`、版本和生成元数据；当运行时能够加载时，也包含插件 + 渠道 schema 元数据。该 schema 包含从与 UI 相同的标签和帮助文本派生的字段 `title` / `description` 元数据，包括嵌套对象、通配符、数组项，以及在存在匹配字段文档时的 `anyOf` / `oneOf` / `allOf` 组合分支。
- `config.schema.lookup` 返回单个配置路径的路径级查询负载：规范化路径、浅层 schema 节点、匹配的 hint + `hintPath`，以及供 UI / CLI 逐层钻取的直接子项摘要。
  - 查询 schema 节点保留面向用户的文档和常见校验字段：
    `title`、`description`、`type`、`enum`、`const`、`format`、`pattern`、
    数值 / 字符串 / 数组 / 对象边界，以及布尔标志如
    `additionalProperties`、`deprecated`、`readOnly`、`writeOnly`。
  - 子项摘要暴露 `key`、规范化后的 `path`、`type`、`required`、
    `hasChildren`，以及匹配的 `hint` / `hintPath`。
- `update.run` 运行 gateway 更新流程，并仅在更新本身成功后安排重启。
- `wizard.start`、`wizard.next`、`wizard.status` 和 `wizard.cancel` 通过 WS RPC 暴露新手引导向导。

### 现有主要方法族

#### 智能体和工作区辅助方法

- `agents.list` 返回已配置的智能体条目。
- `agents.create`、`agents.update` 和 `agents.delete` 管理智能体记录和工作区连接。
- `agents.files.list`、`agents.files.get` 和 `agents.files.set` 管理为智能体公开的 bootstrap 工作区文件。
- `agent.identity.get` 返回某个智能体或会话的生效 assistant 身份。
- `agent.wait` 等待一次运行完成，并在可用时返回终态快照。

#### 会话控制

- `sessions.list` 返回当前会话索引。
- `sessions.subscribe` 和 `sessions.unsubscribe` 为当前 WS 客户端切换会话变更事件订阅。
- `sessions.messages.subscribe` 和 `sessions.messages.unsubscribe` 为单个会话切换转录 / 消息事件订阅。
- `sessions.preview` 返回指定会话键的受限转录预览。
- `sessions.resolve` 解析或规范化会话目标。
- `sessions.create` 创建新的会话条目。
- `sessions.send` 向现有会话发送消息。
- `sessions.steer` 是面向活动会话的中断并转向变体。
- `sessions.abort` 中止某个会话的活动工作。
- `sessions.patch` 更新会话元数据 / 覆盖项。
- `sessions.reset`、`sessions.delete` 和 `sessions.compact` 执行会话维护。
- `sessions.get` 返回完整存储的会话行。
- chat 执行仍使用 `chat.history`、`chat.send`、`chat.abort` 和
  `chat.inject`。
- `chat.history` 针对 UI 客户端进行了显示归一化：可见文本中的内联指令标签会被移除，纯文本工具调用 XML 负载（包括
  `<tool_call>...</tool_call>`、`<function_call>...</function_call>`、
  `<tool_calls>...</tool_calls>`、`<function_calls>...</function_calls>`，
  以及被截断的工具调用块）和泄漏出的 ASCII / 全角模型控制 token 会被移除，纯静默 token 的 assistant 行（例如精确的 `NO_REPLY` /
  `no_reply`）会被省略，超大行可被占位符替换。

#### 设备配对和设备令牌

- `device.pair.list` 返回待处理和已批准的配对设备。
- `device.pair.approve`、`device.pair.reject` 和 `device.pair.remove` 管理设备配对记录。
- `device.token.rotate` 在已批准的角色和作用域边界内轮换配对设备令牌。
- `device.token.revoke` 撤销配对设备令牌。

#### Node 配对、调用和待处理工作

- `node.pair.request`、`node.pair.list`、`node.pair.approve`、
  `node.pair.reject` 和 `node.pair.verify` 涵盖 node 配对和 bootstrap 验证。
- `node.list` 和 `node.describe` 返回已知 / 已连接的 node 状态。
- `node.rename` 更新已配对 node 标签。
- `node.invoke` 将命令转发到已连接的 node。
- `node.invoke.result` 返回 invoke 请求的结果。
- `node.event` 将 node 发起的事件带回 gateway。
- `node.canvas.capability.refresh` 刷新带作用域的 canvas 能力令牌。
- `node.pending.pull` 和 `node.pending.ack` 是已连接 node 的队列 API。
- `node.pending.enqueue` 和 `node.pending.drain` 管理离线 / 断开连接 node 的持久化待处理工作。

#### 审批方法族

- `exec.approval.request` 和 `exec.approval.resolve` 涵盖一次性 exec 审批请求。
- `exec.approval.waitDecision` 等待一个待处理 exec 审批，并返回最终决定（若超时则返回 `null`）。
- `exec.approvals.get` 和 `exec.approvals.set` 管理 gateway exec 审批策略快照。
- `exec.approvals.node.get` 和 `exec.approvals.node.set` 通过 node relay 命令管理 node 本地 exec 审批策略。
- `plugin.approval.request`、`plugin.approval.waitDecision` 和
  `plugin.approval.resolve` 涵盖插件定义的审批流程。

#### 其他主要方法族

- 自动化：
  - `wake` 安排立即或下一个 heartbeat 的唤醒文本注入
  - `cron.list`、`cron.status`、`cron.add`、`cron.update`、`cron.remove`、
    `cron.run`、`cron.runs`
- Skills / 工具：`skills.*`、`tools.catalog`、`tools.effective`

### 常见事件族

- `chat`：UI chat 更新，例如 `chat.inject` 和其他仅转录的 chat
  事件。
- `session.message` 和 `session.tool`：已订阅会话的转录 / 事件流更新。
- `sessions.changed`：会话索引或元数据已变更。
- `presence`：系统在线状态快照更新。
- `tick`：周期性 keepalive / 存活事件。
- `health`：gateway 健康快照更新。
- `heartbeat`：heartbeat 事件流更新。
- `cron`：cron 运行 / 任务变更事件。
- `shutdown`：gateway 关闭通知。
- `node.pair.requested` / `node.pair.resolved`：node 配对生命周期。
- `node.invoke.request`：node invoke 请求广播。
- `device.pair.requested` / `device.pair.resolved`：配对设备生命周期。
- `voicewake.changed`：唤醒词触发器配置已更改。
- `exec.approval.requested` / `exec.approval.resolved`：exec 审批生命周期。
- `plugin.approval.requested` / `plugin.approval.resolved`：插件审批生命周期。

### Node 辅助方法

- Node 可以调用 `skills.bins` 来获取当前 Skills 可执行文件列表，用于自动允许检查。

### Operator 辅助方法

- Operator 可以调用 `tools.catalog`（`operator.read`）来获取某个智能体的运行时工具目录。响应包括分组工具和来源元数据：
  - `source`：`core` 或 `plugin`
  - `pluginId`：当 `source="plugin"` 时的插件所有者
  - `optional`：插件工具是否为可选
- Operator 可以调用 `tools.effective`（`operator.read`）来获取某个会话的运行时生效工具清单。
  - `sessionKey` 是必填项。
  - gateway 在服务端从会话派生受信任的运行时上下文，而不是接受调用方提供的 auth 或投递上下文。
  - 响应是会话级的，并反映当前活动对话此刻可用的内容，包括 core、plugin 和 channel 工具。
- Operator 可以调用 `skills.status`（`operator.read`）来获取某个智能体可见的技能清单。
  - `agentId` 为可选；省略时读取默认智能体工作区。
  - 响应包括资格、缺失要求、配置检查以及已净化的安装选项，且不会暴露原始 secret 值。
- Operator 可以调用 `skills.search` 和 `skills.detail`（`operator.read`）来获取 ClawHub 发现元数据。
- Operator 可以通过两种模式调用 `skills.install`（`operator.admin`）：
  - ClawHub 模式：`{ source: "clawhub", slug, version?, force? }` 将技能文件夹安装到默认智能体工作区的 `skills/` 目录中。
  - Gateway 网关安装器模式：`{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    在 gateway 主机上运行已声明的 `metadata.openclaw.install` 操作。
- Operator 可以通过两种模式调用 `skills.update`（`operator.admin`）：
  - ClawHub 模式会更新一个已跟踪 slug，或更新默认智能体工作区中所有已跟踪的 ClawHub 安装项。
  - 配置模式会修补 `skills.entries.<skillKey>` 值，例如 `enabled`、
    `apiKey` 和 `env`。

## Exec 审批

- 当 exec 请求需要审批时，gateway 会广播 `exec.approval.requested`。
- Operator 客户端通过调用 `exec.approval.resolve` 来处理（需要 `operator.approvals` 作用域）。
- 对于 `host=node`，`exec.approval.request` 必须包含 `systemRunPlan`（规范的 `argv` / `cwd` / `rawCommand` / 会话元数据）。缺少 `systemRunPlan` 的请求会被拒绝。
- 审批通过后，转发的 `node.invoke system.run` 调用会复用该规范
  `systemRunPlan` 作为权威命令 / cwd / 会话上下文。
- 如果调用方在 prepare 和最终获批的 `system.run` 转发之间篡改了
  `command`、`rawCommand`、`cwd`、`agentId` 或 `sessionKey`，gateway 将拒绝该运行，而不是信任被篡改的负载。

## 智能体投递回退

- `agent` 请求可以包含 `deliver=true` 以请求出站投递。
- `bestEffortDeliver=false` 保持严格行为：无法解析或仅内部可用的投递目标会返回 `INVALID_REQUEST`。
- `bestEffortDeliver=true` 允许在无法解析外部可投递路由时回退为仅会话执行（例如内部 / webchat 会话或含糊的多渠道配置）。

## 版本控制

- `PROTOCOL_VERSION` 位于 `src/gateway/protocol/schema.ts`。
- 客户端发送 `minProtocol` + `maxProtocol`；服务器会拒绝不匹配的情况。
- Schemas + 模型由 TypeBox 定义生成：
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## 认证

- 共享密钥的 gateway 认证使用 `connect.params.auth.token` 或
  `connect.params.auth.password`，具体取决于配置的认证模式。
- 带身份的模式，例如 Tailscale Serve
  （`gateway.auth.allowTailscale: true`）或非 loopback 的
  `gateway.auth.mode: "trusted-proxy"`，会通过请求头而不是 `connect.params.auth.*` 来满足 connect 认证检查。
- 私有入口 `gateway.auth.mode: "none"` 会完全跳过共享密钥 connect 认证；不要在公共 / 不受信任的入口上暴露该模式。
- 配对后，Gateway 网关会签发一个**设备令牌**，其作用域绑定到该连接的角色 + 作用域。它会在 `hello-ok.auth.deviceToken` 中返回，客户端应将其持久化，以便未来连接使用。
- 客户端应在任何成功连接后持久化主 `hello-ok.auth.deviceToken`。
- 使用该**已存储**设备令牌重新连接时，还应复用该令牌已存储的已批准作用域集合。这样可保留已授予的 read / probe / status 访问权限，并避免重新连接时静默收缩为更窄的隐式仅 admin 作用域。
- 正常 connect 认证优先级是：显式共享 token / password 优先，其次是显式 `deviceToken`，再其次是按设备存储的令牌，最后是 bootstrap 令牌。
- 额外的 `hello-ok.auth.deviceTokens` 条目是 bootstrap 交接令牌。仅当连接使用了可信传输（例如 `wss://` 或 loopback / 本地配对）上的 bootstrap 认证时，才应持久化它们。
- 如果客户端提供了**显式** `deviceToken` 或显式 `scopes`，则调用方请求的作用域集合仍是权威的；只有当客户端复用按设备存储的令牌时，才会复用缓存作用域。
- 设备令牌可通过 `device.token.rotate` 和
  `device.token.revoke` 轮换 / 撤销（需要 `operator.pairing` 作用域）。
- 令牌签发 / 轮换始终受限于该设备配对条目中记录的已批准角色集合；轮换令牌不能将设备扩展到配对审批从未授予的角色。
- 对于配对设备令牌会话，除非调用方还具有 `operator.admin`，否则设备管理是自限定的：非 admin 调用方只能移除 / 撤销 / 轮换其**自己的**设备条目。
- `device.token.rotate` 还会根据调用方当前会话作用域检查所请求的 operator 作用域集合。非 admin 调用方不能将令牌轮换为比自己当前持有更宽的 operator 作用域集合。
- 认证失败包含 `error.details.code` 以及恢复提示：
  - `error.details.canRetryWithDeviceToken`（布尔值）
  - `error.details.recommendedNextStep`（`retry_with_device_token`、`update_auth_configuration`、`update_auth_credentials`、`wait_then_retry`、`review_auth_configuration`）
- 客户端对 `AUTH_TOKEN_MISMATCH` 的行为：
  - 受信任客户端可以使用缓存的按设备令牌进行一次受限重试。
  - 如果该次重试失败，客户端应停止自动重连循环，并向操作员显示需要人工干预的指引。

## 设备身份 + 配对

- Node 应包含稳定的设备身份（`device.id`），该身份从密钥对指纹派生。
- Gateway 网关按设备 + 角色签发令牌。
- 新设备 ID 需要配对审批，除非启用了本地自动审批。
- 配对自动审批以直接本地 `local loopback` 连接为中心。
- OpenClaw 还为可信共享密钥辅助流程提供了一条狭窄的后端 / 容器本地自连接路径。
- 同一主机上的 tailnet 或 LAN 连接在配对上仍视为远程，并需要审批。
- 所有 WS 客户端在 `connect` 时都必须包含 `device` 身份（operator + node）。
  Control UI 仅可在以下模式中省略它：
  - `gateway.controlUi.allowInsecureAuth=true`，用于仅限 localhost 的不安全 HTTP 兼容模式。
  - 成功的 `gateway.auth.mode: "trusted-proxy"` operator Control UI 认证。
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true`（破窗应急，严重降低安全性）。
- 所有连接都必须对服务器提供的 `connect.challenge` nonce 进行签名。

### 设备认证迁移诊断

对于仍使用预质询签名行为的旧客户端，`connect` 现在会在 `error.details.code` 下返回 `DEVICE_AUTH_*` 详细代码，并在 `error.details.reason` 中提供稳定的原因。

常见迁移失败：

| 消息 | details.code | details.reason | 含义 |
| --------------------------- | -------------------------------- | ------------------------ | -------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | 客户端省略了 `device.nonce`（或发送了空值）。 |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | 客户端使用了过期 / 错误的 nonce 进行签名。 |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | 签名负载与 v2 负载不匹配。 |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | 签名时间戳超出允许的时钟偏差。 |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id` 与公钥指纹不匹配。 |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | 公钥格式 / 规范化失败。 |

迁移目标：

- 始终等待 `connect.challenge`。
- 对包含服务器 nonce 的 v2 负载进行签名。
- 在 `connect.params.device.nonce` 中发送相同的 nonce。
- 首选签名负载是 `v3`，它除了 device / client / role / scopes / token / nonce 字段外，还绑定了 `platform` 和 `deviceFamily`。
- 为兼容性起见，旧版 `v2` 签名仍然可被接受，但配对设备元数据固定仍会在重连时控制命令策略。

## TLS + 固定

- WS 连接支持 TLS。
- 客户端可以选择固定 gateway 证书指纹（见 `gateway.tls`
  配置，以及 `gateway.remote.tlsFingerprint` 或 CLI `--tls-fingerprint`）。

## 范围

该协议暴露了**完整的 gateway API**（status、channels、models、chat、
agent、sessions、nodes、approvals 等）。确切接口由 `src/gateway/protocol/schema.ts` 中的 TypeBox schemas 定义。
