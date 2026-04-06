---
read_when:
    - 在 OpenClaw 中设置 Matrix
    - 配置 Matrix E2EE 和验证
summary: Matrix 支持状态、设置和配置示例
title: Matrix
x-i18n:
    generated_at: "2026-04-06T01:18:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e2d84c08d7d5b96db14b914e54f08d25334401cdd92eb890bc8dfb37b0ca2dc
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix 是 OpenClaw 的 Matrix 内置渠道插件。
它使用官方 `matrix-js-sdk`，并支持私信、房间、线程、媒体、回应、投票、位置和 E2EE。

## 内置插件

Matrix 作为内置插件随当前的 OpenClaw 版本一起发布，因此普通的打包构建不需要单独安装。

如果你使用的是较旧的构建版本，或是不包含 Matrix 的自定义安装，请手动安装：

从 npm 安装：

```bash
openclaw plugins install @openclaw/matrix
```

从本地检出目录安装：

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

有关插件行为和安装规则，请参阅 [插件](/zh-CN/tools/plugin)。

## 设置

1. 确保 Matrix 插件可用。
   - 当前打包的 OpenClaw 版本已内置该插件。
   - 较旧/自定义安装可以使用上面的命令手动添加。
2. 在你的 homeserver 上创建一个 Matrix 账号。
3. 使用以下任一方式配置 `channels.matrix`：
   - `homeserver` + `accessToken`，或
   - `homeserver` + `userId` + `password`。
4. 重启 Gateway 网关。
5. 与机器人开始私信，或邀请它进入房间。

交互式设置路径：

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix 向导实际会询问以下内容：

- homeserver URL
- 认证方式：access token 或密码
- 仅当你选择密码认证时才需要用户 ID
- 可选设备名称
- 是否启用 E2EE
- 是否立即配置 Matrix 房间访问

需要注意的向导行为：

- 如果所选账号已存在 Matrix 认证环境变量，且该账号尚未在配置中保存认证信息，向导会提供一个环境变量快捷方式，并且只为该账号写入 `enabled: true`。
- 当你以交互方式添加另一个 Matrix 账号时，输入的账号名称会被规范化为配置和环境变量中使用的账号 ID。例如，`Ops Bot` 会变成 `ops-bot`。
- 私信 allowlist 提示可立即接受完整的 `@user:server` 值。显示名称仅在实时目录查找找到唯一精确匹配时有效；否则向导会要求你使用完整的 Matrix ID 重试。
- 房间 allowlist 提示可直接接受房间 ID 和别名。它们也可以实时解析已加入房间的名称，但无法解析的名称在设置期间只会按输入原样保留，之后会被运行时 allowlist 解析忽略。优先使用 `!room:server` 或 `#alias:server`。
- 运行时的房间/会话身份使用稳定的 Matrix 房间 ID。房间声明的别名仅用作查找输入，不用作长期会话键或稳定的群组身份。
- 如需在保存前解析房间名称，请使用 `openclaw channels resolve --channel matrix "Project Room"`。

基于 token 的最小设置：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

基于密码的设置（登录后会缓存 token）：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix 会将缓存的凭证存储在 `~/.openclaw/credentials/matrix/` 中。
默认账号使用 `credentials.json`；命名账号使用 `credentials-<account>.json`。
当这里存在缓存凭证时，即使当前认证信息未直接在配置中设置，OpenClaw 也会在设置、Doctor 和渠道状态发现中将 Matrix 视为已配置。

对应的环境变量（当未设置配置键时使用）：

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

对于非默认账号，请使用按账号作用域区分的环境变量：

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

账号 `ops` 的示例：

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

对于规范化后的账号 ID `ops-bot`，请使用：

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix 会对账号 ID 中的标点符号进行转义，以避免带作用域的环境变量发生冲突。
例如，`-` 会变成 `_X2D_`，因此 `ops-prod` 会映射为 `MATRIX_OPS_X2D_PROD_*`。

只有当这些认证环境变量已经存在，且所选账号尚未在配置中保存 Matrix 认证信息时，交互式向导才会提供环境变量快捷方式。

## 配置示例

这是一个实用的基线配置，启用了私信配对、房间 allowlist 和 E2EE：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

## 流式预览

Matrix 回复流式传输为可选启用。

当你希望 OpenClaw 发送一条实时预览回复、在模型生成文本时原地编辑该预览，并在回复完成后将其最终定稿时，请将 `channels.matrix.streaming` 设置为 `"partial"`：

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` 是默认值。OpenClaw 会等待最终回复并只发送一次。
- `streaming: "partial"` 会为当前助手块创建一条可编辑的预览消息，使用普通 Matrix 文本消息。这会保留 Matrix 传统的“预览优先”通知行为，因此标准客户端可能会在第一次流式预览文本出现时通知，而不是在最终完成的块发送时通知。
- `streaming: "quiet"` 会为当前助手块创建一条可编辑的静默预览通知。只有在你同时为最终定稿的预览编辑配置了接收者推送规则时，才应使用此选项。
- `blockStreaming: true` 启用单独的 Matrix 进度消息。启用预览流式传输时，Matrix 会保留当前块的实时草稿，并将已完成的块保留为单独消息。
- 当启用预览流式传输且 `blockStreaming` 为关闭时，Matrix 会原地编辑实时草稿，并在块或轮次结束时将同一事件定稿。
- 如果预览内容已无法容纳在单个 Matrix 事件中，OpenClaw 会停止预览流式传输，并回退到普通最终发送。
- 媒体回复仍会正常发送附件。如果过期预览无法再安全复用，OpenClaw 会先将其 redact，然后再发送最终媒体回复。
- 预览编辑会产生额外的 Matrix API 调用。如果你希望采用最保守的速率限制行为，请保持关闭流式传输。

`blockStreaming` 本身不会启用草稿预览。
如需预览编辑，请使用 `streaming: "partial"` 或 `streaming: "quiet"`；仅当你还希望已完成的助手块保留为单独进度消息时，再加上 `blockStreaming: true`。

如果你需要标准 Matrix 通知而不配置自定义推送规则，请使用 `streaming: "partial"` 以获得“预览优先”行为，或者保持 `streaming` 关闭以仅发送最终结果。对于 `streaming: "off"`：

- `blockStreaming: true` 会将每个已完成块作为普通可通知的 Matrix 消息发送。
- `blockStreaming: false` 只会将最终完成的回复作为普通可通知的 Matrix 消息发送。

### 自托管静默最终预览的推送规则

如果你运行自己的 Matrix 基础设施，并希望静默预览仅在某个块或最终回复完成时才通知，请设置 `streaming: "quiet"`，并为最终定稿的预览编辑添加每用户推送规则。

这通常是接收用户的设置，而不是 homeserver 级别的全局配置变更：

开始前的快速对应关系：

- 接收用户 = 应收到通知的人
- 机器人用户 = 发送回复的 OpenClaw Matrix 账号
- 对下方 API 调用使用接收用户的 access token
- 在推送规则中，将 `sender` 与机器人用户的完整 MXID 匹配

1. 配置 OpenClaw 使用静默预览：

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. 确保接收账号已经能收到普通 Matrix 推送通知。静默预览规则仅在该用户已有正常工作的推送器/设备时才有效。

3. 获取接收用户的 access token。
   - 使用接收用户的 token，而不是机器人的 token。
   - 复用现有客户端会话 token 通常是最简单的方式。
   - 如果你需要创建一个新的 token，可以通过标准 Matrix Client-Server API 登录：

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. 验证接收账号是否已经有推送器：

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

如果此命令返回没有活动的推送器/设备，请先修复普通 Matrix 通知，再添加下面的 OpenClaw 规则。

OpenClaw 会用以下内容标记最终定稿的纯文本预览编辑：

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. 为每个需要接收这些通知的接收账号创建一个 override 推送规则：

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

运行该命令前，请替换以下值：

- `https://matrix.example.org`：你的 homeserver 基础 URL
- `$USER_ACCESS_TOKEN`：接收用户的 access token
- `openclaw-finalized-preview-botname`：对此接收用户中该机器人唯一的规则 ID
- `@bot:example.org`：你的 OpenClaw Matrix 机器人 MXID，而不是接收用户的 MXID

多机器人设置的重要说明：

- 推送规则按 `ruleId` 键控。对同一规则 ID 重新执行 `PUT` 会更新该规则。
- 如果同一接收用户需要为多个 OpenClaw Matrix 机器人账号通知，请为每个机器人创建一条规则，并为每个 sender 匹配使用唯一规则 ID。
- 一个简单的模式是 `openclaw-finalized-preview-<botname>`，例如 `openclaw-finalized-preview-ops` 或 `openclaw-finalized-preview-support`。

该规则会针对事件发送者进行评估：

- 使用接收用户的 token 进行认证
- 将 `sender` 与 OpenClaw 机器人 MXID 进行匹配

6. 验证规则是否存在：

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. 测试一条流式回复。在静默模式下，房间中应显示一条静默草稿预览，并在块或轮次完成时仅在最终原地编辑时通知一次。

如果你之后需要移除该规则，请使用接收用户的 token 删除相同的规则 ID：

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

说明：

- 请使用接收用户的 access token 创建规则，而不是机器人的 token。
- 新建的用户自定义 `override` 规则会插入到默认抑制规则之前，因此不需要额外的排序参数。
- 这只会影响 OpenClaw 能安全原地定稿的纯文本预览编辑。媒体回退和过期预览回退仍使用普通 Matrix 发送方式。
- 如果 `GET /_matrix/client/v3/pushers` 显示没有推送器，说明该用户尚未为此账号/设备配置可用的 Matrix 推送。

#### Synapse

对于 Synapse，通常只需要上面的设置即可：

- finalized OpenClaw 预览通知不需要特殊的 `homeserver.yaml` 变更。
- 如果你的 Synapse 部署已经能够发送普通 Matrix 推送通知，那么上面的用户 token + `pushrules` 调用就是主要设置步骤。
- 如果你在反向代理或 workers 后面运行 Synapse，请确保 `/_matrix/client/.../pushrules/` 能正确到达 Synapse。
- 如果你运行 Synapse workers，请确保 pushers 状态健康。推送发送由主进程或 `synapse.app.pusher` / 已配置的 pusher workers 处理。

#### Tuwunel

对于 Tuwunel，请使用与上面相同的设置流程和 push-rule API 调用：

- finalized preview 标记本身不需要 Tuwunel 特有配置。
- 如果该用户的普通 Matrix 通知已经可用，那么上面的用户 token + `pushrules` 调用就是主要设置步骤。
- 如果用户在另一台设备活跃时通知似乎消失，请检查是否启用了 `suppress_push_when_active`。Tuwunel 在 2025 年 9 月 12 日发布的 Tuwunel 1.4.2 中新增了此选项，它会在某台设备处于活跃状态时，有意抑制向其他设备推送通知。

## 加密和验证

在加密（E2EE）房间中，出站图片事件使用 `thumbnail_file`，因此图片预览会与完整附件一起加密。未加密房间仍使用普通的 `thumbnail_url`。无需任何配置——插件会自动检测 E2EE 状态。

### Bot 到 Bot 房间

默认情况下，来自其他已配置 OpenClaw Matrix 账号的 Matrix 消息会被忽略。

当你确实希望启用智能体之间的 Matrix 通信时，请使用 `allowBots`：

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` 会在允许的房间和私信中接受来自其他已配置 Matrix 机器人账号的消息。
- `allowBots: "mentions"` 仅在这些消息在房间中明确提及此机器人时接受。私信仍然允许。
- `groups.<room>.allowBots` 会覆盖该房间的账号级设置。
- OpenClaw 仍会忽略来自同一 Matrix 用户 ID 的消息，以避免自回复循环。
- Matrix 在这里不提供原生 bot 标记；OpenClaw 将“由 bot 发出的”定义为“由此 OpenClaw Gateway 网关上另一个已配置 Matrix 账号发送”。

在共享房间中启用 bot-to-bot 流量时，请使用严格的房间 allowlist 和提及要求。

启用加密：

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

检查验证状态：

```bash
openclaw matrix verify status
```

详细状态（完整诊断）：

```bash
openclaw matrix verify status --verbose
```

在机器可读输出中包含已存储的恢复密钥：

```bash
openclaw matrix verify status --include-recovery-key --json
```

引导 cross-signing 和验证状态：

```bash
openclaw matrix verify bootstrap
```

多账号支持：使用 `channels.matrix.accounts` 配置每个账号的凭证和可选 `name`。共享模式请参阅 [配置参考](/zh-CN/gateway/configuration-reference#multi-account-all-channels)。

详细引导诊断：

```bash
openclaw matrix verify bootstrap --verbose
```

在引导前强制执行全新的 cross-signing 身份重置：

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

使用恢复密钥验证此设备：

```bash
openclaw matrix verify device "<your-recovery-key>"
```

详细设备验证信息：

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

检查房间密钥备份健康状态：

```bash
openclaw matrix verify backup status
```

详细备份健康诊断：

```bash
openclaw matrix verify backup status --verbose
```

从服务器备份恢复房间密钥：

```bash
openclaw matrix verify backup restore
```

详细恢复诊断：

```bash
openclaw matrix verify backup restore --verbose
```

删除当前服务器备份并创建新的备份基线。如果已存储的备份密钥无法被干净地加载，此重置还可以重建秘密存储，以便后续冷启动能够加载新的备份密钥：

```bash
openclaw matrix verify backup reset --yes
```

所有 `verify` 命令默认都很简洁（包括安静的内部 SDK 日志），仅在使用 `--verbose` 时显示详细诊断。
脚本化使用时，请使用 `--json` 获取完整的机器可读输出。

在多账号设置中，Matrix CLI 命令会使用隐式的 Matrix 默认账号，除非你传入 `--account <id>`。
如果你配置了多个命名账号，请先设置 `channels.matrix.defaultAccount`，否则这些隐式 CLI 操作将停止并要求你显式选择一个账号。
每当你希望验证或设备操作明确针对某个命名账号时，请使用 `--account`：

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

当某个命名账号的加密被禁用或不可用时，Matrix 警告和验证错误会指向该账号的配置键，例如 `channels.matrix.accounts.assistant.encryption`。

### “已验证” 的含义

只有当这个 Matrix 设备已被你自己的 cross-signing 身份验证时，OpenClaw 才会将其视为已验证。
实际上，`openclaw matrix verify status --verbose` 会显示三个信任信号：

- `Locally trusted`：此设备仅被当前客户端信任
- `Cross-signing verified`：SDK 报告该设备已通过 cross-signing 验证
- `Signed by owner`：该设备已由你自己的 self-signing 密钥签名

只有在存在 cross-signing 验证或 owner-signing 时，`Verified by owner` 才会变为 `yes`。
仅有本地信任还不足以让 OpenClaw 将该设备视为完全已验证。

### bootstrap 的作用

`openclaw matrix verify bootstrap` 是用于加密 Matrix 账号的修复和设置命令。
它会按顺序执行以下所有操作：

- 引导秘密存储，并尽可能复用现有恢复密钥
- 引导 cross-signing 并上传缺失的公开 cross-signing 密钥
- 尝试标记并 cross-sign 当前设备
- 如果尚不存在服务器端房间密钥备份，则创建一个新的备份

如果 homeserver 要求交互式认证才能上传 cross-signing 密钥，OpenClaw 会先尝试无认证上传，然后使用 `m.login.dummy`，最后在配置了 `channels.matrix.password` 时尝试 `m.login.password`。

仅当你明确希望丢弃当前 cross-signing 身份并创建新身份时，才使用 `--force-reset-cross-signing`。

如果你明确希望丢弃当前房间密钥备份，并为未来消息建立新的备份基线，请使用 `openclaw matrix verify backup reset --yes`。
只有在你接受旧的、无法恢复的加密历史将继续不可用，并且接受 OpenClaw 可能在当前备份秘密无法安全加载时重建秘密存储的情况下，才这样做。

### 新的备份基线

如果你希望未来的加密消息继续正常工作，并接受丢失无法恢复的旧历史，请按顺序运行以下命令：

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

当你希望明确针对某个命名 Matrix 账号时，请为每个命令添加 `--account <id>`。

### 启动行为

当 `encryption: true` 时，Matrix 默认将 `startupVerification` 设为 `"if-unverified"`。
启动时，如果此设备仍未验证，Matrix 会在另一个 Matrix 客户端中请求自我验证，在已有待处理请求时跳过重复请求，并在重启后重试前应用本地冷却时间。
默认情况下，失败的请求尝试会比成功创建请求更早重试。
如果你想禁用自动启动请求，请设置 `startupVerification: "off"`；如果你希望缩短或延长重试窗口，请调整 `startupVerificationCooldownHours`。

启动时还会自动执行一次保守的加密 bootstrap 检查。
该检查会优先尝试复用当前秘密存储和 cross-signing 身份，并避免重置 cross-signing，除非你运行显式的 bootstrap 修复流程。

如果启动时发现 bootstrap 状态损坏，且已配置 `channels.matrix.password`，OpenClaw 可以尝试更严格的修复路径。
如果当前设备已经由 owner 签名，OpenClaw 会保留该身份，而不会自动重置。

从之前公开的 Matrix 插件升级：

- OpenClaw 会在可能时自动复用同一个 Matrix 账号、access token 和设备身份。
- 在执行任何可操作的 Matrix 迁移变更之前，OpenClaw 会在 `~/Backups/openclaw-migrations/` 下创建或复用一个恢复快照。
- 如果你使用多个 Matrix 账号，请在从旧的平面存储布局升级前设置 `channels.matrix.defaultAccount`，这样 OpenClaw 才知道应将共享的旧状态分配给哪个账号。
- 如果之前的插件曾在本地存储 Matrix 房间密钥备份解密密钥，启动或 `openclaw doctor --fix` 会自动将其导入新的恢复密钥流程。
- 如果在准备迁移后 Matrix access token 发生变化，启动现在会扫描同级 token-hash 存储根目录中待恢复的旧状态，然后才会放弃自动备份恢复。
- 如果同一账号、homeserver 和用户之后再次更换 Matrix access token，OpenClaw 现在会优先复用最完整的现有 token-hash 存储根目录，而不是从空的 Matrix 状态目录开始。
- 在下次 Gateway 网关启动时，已备份的房间密钥会自动恢复到新的加密存储中。
- 如果旧插件存在从未备份过的仅本地房间密钥，OpenClaw 会明确警告。由于这些密钥无法从之前的 rust crypto store 中自动导出，因此某些旧的加密历史在手动恢复之前可能仍不可用。
- 完整升级流程、限制、恢复命令和常见迁移消息，请参阅 [Matrix 迁移](/zh-CN/install/migrating-matrix)。

加密的运行时状态按账号、用户和 token-hash 根目录组织，路径位于
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`。
该目录会在相关功能启用时包含同步存储（`bot-storage.json`）、加密存储（`crypto/`）、
恢复密钥文件（`recovery-key.json`）、IndexedDB 快照（`crypto-idb-snapshot.json`）、
线程绑定（`thread-bindings.json`）以及启动验证状态（`startup-verification.json`）。
当 token 变化但账号身份保持不变时，OpenClaw 会为该 account/homeserver/user 元组复用最佳现有根目录，因此先前的同步状态、加密状态、线程绑定和启动验证状态仍然可见。

### Node 加密存储模型

此插件中的 Matrix E2EE 在 Node 中使用官方 `matrix-js-sdk` Rust 加密路径。
当你希望加密状态在重启后保留时，该路径需要基于 IndexedDB 的持久化。

OpenClaw 目前在 Node 中通过以下方式提供此能力：

- 使用 `fake-indexeddb` 作为 SDK 所需的 IndexedDB API shim
- 在 `initRustCrypto` 之前，从 `crypto-idb-snapshot.json` 恢复 Rust 加密 IndexedDB 内容
- 在初始化后以及运行期间，将更新后的 IndexedDB 内容持久化回 `crypto-idb-snapshot.json`
- 通过建议性文件锁，针对 `crypto-idb-snapshot.json` 串行化快照恢复和持久化，以避免 Gateway 网关运行时持久化与 CLI 维护对同一快照文件发生竞争

这属于兼容性/存储层处理，而不是自定义加密实现。
快照文件属于敏感运行时状态，并以严格的文件权限存储。
在 OpenClaw 的安全模型下，Gateway 网关主机和本地 OpenClaw 状态目录本身已经处于受信任的操作边界内，因此这主要是一个运行可靠性问题，而不是一个单独的远程信任边界问题。

计划中的改进：

- 为持久化 Matrix 密钥材料添加 SecretRef 支持，以便恢复密钥和相关存储加密秘密可从 OpenClaw secrets provider 获取，而不仅限于本地文件

## 资料管理

使用以下命令更新所选账号的 Matrix 自身资料：

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

当你希望明确针对某个命名 Matrix 账号时，请添加 `--account <id>`。

Matrix 可直接接受 `mxc://` 头像 URL。当你传入 `http://` 或 `https://` 头像 URL 时，OpenClaw 会先将其上传到 Matrix，然后把解析得到的 `mxc://` URL 回写到 `channels.matrix.avatarUrl`（或所选账号的覆盖配置）中。

## 自动验证通知

Matrix 现在会将验证生命周期通知直接发布到严格的私信验证房间中，作为 `m.notice` 消息。
这包括：

- 验证请求通知
- 验证就绪通知（带明确的“通过表情符号验证”指引）
- 验证开始和完成通知
- SAS 详情（表情符号和十进制），在可用时显示

来自其他 Matrix 客户端的传入验证请求会被 OpenClaw 跟踪并自动接受。
对于自我验证流程，当表情符号验证可用时，OpenClaw 也会自动启动 SAS 流程并确认自己这一侧。
对于来自其他 Matrix 用户/设备的验证请求，OpenClaw 会自动接受请求，然后等待 SAS 流程正常继续。
你仍然需要在你的 Matrix 客户端中比对表情符号或十进制 SAS，并在那里确认“它们匹配”，才能完成验证。

OpenClaw 不会盲目自动接受自发起的重复流程。当已有待处理的自我验证请求时，启动过程会跳过创建新请求。

验证协议/系统通知不会转发到智能体聊天管线，因此不会产生 `NO_REPLY`。

### 设备清理

旧的由 OpenClaw 管理的 Matrix 设备可能会在账号中累积，使加密房间的信任状态更难判断。
使用以下命令列出它们：

```bash
openclaw matrix devices list
```

使用以下命令移除陈旧的由 OpenClaw 管理的设备：

```bash
openclaw matrix devices prune-stale
```

### 直接房间修复

如果私信状态不同步，OpenClaw 可能会留下过期的 `m.direct` 映射，使其指向旧的单人房间而不是当前有效的私信。使用以下命令检查某个对方当前映射：

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

使用以下命令修复：

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修复会将 Matrix 特定逻辑保留在插件内部：

- 它会优先选择已经映射在 `m.direct` 中的严格 1:1 私信
- 否则会回退到与该用户当前已加入的任意严格 1:1 私信
- 如果不存在健康的私信，则会创建一个新的 direct room，并重写 `m.direct` 指向它

修复流程不会自动删除旧房间。它只会选择健康的私信并更新映射，以便新的 Matrix 发送、验证通知和其他私信流程再次指向正确的房间。

## 线程

Matrix 同时支持自动回复和 message-tool 发送的原生 Matrix 线程。

- `dm.sessionScope: "per-user"`（默认）会让 Matrix 私信路由保持按发送者作用域，因此多个私信房间在解析为同一对方时可以共享一个会话。
- `dm.sessionScope: "per-room"` 会将每个 Matrix 私信房间隔离为各自的会话键，同时仍使用普通的私信认证和 allowlist 检查。
- 显式的 Matrix 对话绑定仍优先于 `dm.sessionScope`，因此已绑定的房间和线程会保留其选定的目标会话。
- `threadReplies: "off"` 会保持回复在顶层，并让传入的线程消息继续使用父会话。
- `threadReplies: "inbound"` 仅当传入消息已经位于该线程中时，才在线程内回复。
- `threadReplies: "always"` 会将房间回复保持在线程中，并以触发消息为根，从第一条触发消息开始，通过匹配的线程作用域会话路由该对话。
- `dm.threadReplies` 仅覆盖私信的顶层设置。例如，你可以保持房间线程隔离，同时让私信保持扁平。
- 传入的线程消息会将线程根消息作为额外的智能体上下文包含进去。
- Message-tool 发送现在会在目标是同一房间或同一私信用户目标时，自动继承当前 Matrix 线程，除非显式提供了 `threadId`。
- 仅当当前会话元数据能证明是同一 Matrix 账号上的同一私信对方时，才会触发同会话私信用户目标复用；否则 OpenClaw 会回退到普通的用户作用域路由。
- 当 OpenClaw 发现某个 Matrix 私信房间与同一共享 Matrix 私信会话上的另一个私信房间发生冲突时，如果启用了线程绑定和 `dm.sessionScope` 提示，它会在该房间中发布一次性 `m.notice`，并提供 `/focus` 逃生入口。
- Matrix 支持运行时线程绑定。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age` 以及线程绑定的 `/acp spawn` 现在都可在 Matrix 房间和私信中使用。
- 顶层 Matrix 房间/私信中的 `/focus` 会在 `threadBindings.spawnSubagentSessions=true` 时创建一个新的 Matrix 线程，并将其绑定到目标会话。
- 在现有 Matrix 线程中运行 `/focus` 或 `/acp spawn --thread here`，则会改为绑定当前线程。

## ACP 对话绑定

Matrix 房间、私信以及现有 Matrix 线程都可以转变为持久的 ACP 工作区，而无需改变聊天界面。

适合操作员的快速流程：

- 在你希望继续使用的 Matrix 私信、房间或现有线程中运行 `/acp spawn codex --bind here`。
- 在顶层 Matrix 私信或房间中，当前私信/房间会继续作为聊天界面，后续消息会路由到新创建的 ACP 会话。
- 在现有 Matrix 线程内部，`--bind here` 会将当前线程原地绑定。
- `/new` 和 `/reset` 会原地重置同一个已绑定 ACP 会话。
- `/acp close` 会关闭 ACP 会话并移除绑定。

说明：

- `--bind here` 不会创建子 Matrix 线程。
- `threadBindings.spawnAcpSessions` 仅在 `/acp spawn --thread auto|here` 时需要，因为此时 OpenClaw 需要创建或绑定一个子 Matrix 线程。

### 线程绑定配置

Matrix 会继承 `session.threadBindings` 的全局默认值，也支持每渠道覆盖：

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix 线程绑定的生成标志为可选启用：

- 设置 `threadBindings.spawnSubagentSessions: true` 以允许顶层 `/focus` 创建并绑定新的 Matrix 线程。
- 设置 `threadBindings.spawnAcpSessions: true` 以允许 `/acp spawn --thread auto|here` 将 ACP 会话绑定到 Matrix 线程。

## 回应

Matrix 支持出站回应操作、入站回应通知和入站确认回应。

- 出站回应工具由 `channels["matrix"].actions.reactions` 控制。
- `react` 会向指定的 Matrix 事件添加回应。
- `reactions` 会列出指定 Matrix 事件当前的回应摘要。
- `emoji=""` 会移除机器人账号在该事件上的所有自身回应。
- `remove: true` 只会移除机器人账号对该表情符号的回应。

确认回应使用标准的 OpenClaw 解析顺序：

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- 智能体身份 emoji 回退

确认回应作用域按以下顺序解析：

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

回应通知模式按以下顺序解析：

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- 默认值：`own`

当前行为：

- `reactionNotifications: "own"` 会在新增的 `m.reaction` 事件指向由机器人发布的 Matrix 消息时，将其转发。
- `reactionNotifications: "off"` 会禁用回应系统事件。
- 回应移除仍不会被合成为系统事件，因为 Matrix 将其表现为 redaction，而不是独立的 `m.reaction` 移除事件。

## 历史上下文

- `channels.matrix.historyLimit` 控制当 Matrix 房间消息触发智能体时，作为 `InboundHistory` 包含多少最近房间消息。
- 它会回退到 `messages.groupChat.historyLimit`。设置为 `0` 可禁用。
- Matrix 房间历史仅限房间。私信仍使用普通会话历史。
- Matrix 房间历史为“待处理消息”模式：OpenClaw 会缓冲尚未触发回复的房间消息，然后在提及或其他触发到来时对该窗口进行快照。
- 当前触发消息不会包含在 `InboundHistory` 中；它会保留在该轮的主入站正文中。
- 对同一 Matrix 事件的重试会复用原始历史快照，而不会向前漂移到更新的房间消息。

## 上下文可见性

Matrix 支持共享的 `contextVisibility` 控制，用于补充房间上下文，例如获取到的回复文本、线程根消息和待处理历史。

- `contextVisibility: "all"` 是默认值。补充上下文会按接收时原样保留。
- `contextVisibility: "allowlist"` 会根据当前房间/用户 allowlist 检查，将补充上下文过滤为仅允许的发送者。
- `contextVisibility: "allowlist_quote"` 的行为与 `allowlist` 相同，但仍会保留一条显式引用的回复。

此设置影响的是补充上下文的可见性，而不是入站消息本身是否可以触发回复。
触发授权仍由 `groupPolicy`、`groups`、`groupAllowFrom` 和私信策略设置决定。

## 私信和房间策略示例

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

有关提及门控和 allowlist 行为，请参阅 [群组](/zh-CN/channels/groups)。

Matrix 私信的配对示例：

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

如果某个尚未批准的 Matrix 用户在获批前持续向你发送消息，OpenClaw 会复用同一个待处理配对码，并可能在短暂冷却后再次发送提醒回复，而不是生成新的配对码。

有关共享的私信配对流程和存储布局，请参阅 [配对](/zh-CN/channels/pairing)。

## Exec 审批

Matrix 可以作为某个 Matrix 账号的 exec 审批客户端。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（可选；会回退到 `channels.matrix.dm.allowFrom`）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`，默认值：`dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

审批人必须是 Matrix 用户 ID，例如 `@owner:example.org`。当 `enabled` 未设置或为 `"auto"`，且至少能解析出一个审批人时，Matrix 会自动启用原生 exec 审批，这些审批人可来自 `execApprovals.approvers` 或 `channels.matrix.dm.allowFrom`。设置 `enabled: false` 可显式禁用 Matrix 作为原生审批客户端。否则，审批请求会回退到其他已配置的审批路径或 exec 审批回退策略。

Matrix 原生路由目前仅适用于 exec：

- `channels.matrix.execApprovals.*` 仅控制 exec 审批的原生私信/渠道路由。
- 插件审批仍使用共享的同聊天 `/approve`，以及任何已配置的 `approvals.plugin` 转发。
- 当 Matrix 能安全推断审批人时，仍可复用 `channels.matrix.dm.allowFrom` 用于插件审批授权，但不会公开单独的原生插件审批私信/渠道扇出路径。

发送规则：

- `target: "dm"` 会将审批提示发送到审批人的私信
- `target: "channel"` 会将提示发送回原始 Matrix 房间或私信
- `target: "both"` 会同时发送到审批人的私信和原始 Matrix 房间或私信

Matrix 审批提示会在主审批消息上预置回应快捷方式：

- `✅` = 允许一次
- `❌` = 拒绝
- `♾️` = 始终允许（前提是当前生效的 exec 策略允许该决定）

审批人可以对此消息添加回应，或使用回退斜杠命令：`/approve <id> allow-once`、`/approve <id> allow-always` 或 `/approve <id> deny`。

只有已解析出的审批人才能批准或拒绝。渠道发送会包含命令文本，因此仅应在受信任的房间中启用 `channel` 或 `both`。

Matrix 审批提示会复用共享核心审批规划器。Matrix 特有的原生表面仅用于 exec 审批的传输：房间/私信路由，以及消息发送/更新/删除行为。

每账号覆盖：

- `channels.matrix.accounts.<account>.execApprovals`

相关文档：[Exec 审批](/zh-CN/tools/exec-approvals)

## 多账号示例

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

顶层 `channels.matrix` 值会作为命名账号的默认值，除非某个账号显式覆盖。
你可以使用 `groups.<room>.account`（或旧版 `rooms.<room>.account`）将继承的房间条目限定到某个 Matrix 账号。
没有 `account` 的条目会在所有 Matrix 账号之间共享，而带有 `account: "default"` 的条目在默认账号直接配置在顶层 `channels.matrix.*` 时也仍然有效。
部分共享认证默认值本身不会创建单独的隐式默认账号。只有当该默认账号拥有新的认证信息（`homeserver` + `accessToken`，或 `homeserver` + `userId` 和 `password`）时，OpenClaw 才会合成顶层 `default` 账号；命名账号仍然可以在稍后缓存凭证满足认证时，通过 `homeserver` + `userId` 保持可发现。
如果 Matrix 已经恰好有一个命名账号，或者 `defaultAccount` 指向现有的命名账号键，那么单账号到多账号的修复/设置升级会保留该账号，而不是创建新的 `accounts.default` 条目。只有 Matrix 认证/bootstrap 键会移动到升级后的账号中；共享的发送策略键仍保留在顶层。
当你希望 OpenClaw 在隐式路由、探测和 CLI 操作中优先使用某个命名 Matrix 账号时，请设置 `defaultAccount`。
如果你配置了多个命名账号，请设置 `defaultAccount`，或者在依赖隐式账号选择的 CLI 命令中传入 `--account <id>`。
当你希望对单个命令覆盖该隐式选择时，请对 `openclaw matrix verify ...` 和 `openclaw matrix devices ...` 传入 `--account <id>`。

## 私有/LAN homeserver

默认情况下，除非你按账号显式选择加入，否则 OpenClaw 会阻止连接私有/内部 Matrix homeserver，以提供 SSRF 保护。

如果你的 homeserver 运行在 localhost、LAN/Tailscale IP 或内部主机名上，请为该 Matrix 账号启用 `allowPrivateNetwork`：

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI 设置示例：

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

此选择加入仅允许受信任的私有/内部目标。像
`http://matrix.example.org:8008` 这样的公共明文 homeserver 仍然会被阻止。只要可能，请优先使用 `https://`。

## 代理 Matrix 流量

如果你的 Matrix 部署需要显式的出站 HTTP(S) 代理，请设置 `channels.matrix.proxy`：

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

命名账号可以使用 `channels.matrix.accounts.<id>.proxy` 覆盖顶层默认值。
OpenClaw 会对运行时 Matrix 流量和账号状态探测使用相同的代理设置。

## 目标解析

无论 OpenClaw 在何处要求你提供房间或用户目标，Matrix 都接受以下目标形式：

- 用户：`@user:server`、`user:@user:server` 或 `matrix:user:@user:server`
- 房间：`!room:server`、`room:!room:server` 或 `matrix:room:!room:server`
- 别名：`#alias:server`、`channel:#alias:server` 或 `matrix:channel:#alias:server`

实时目录查找使用已登录的 Matrix 账号：

- 用户查找会查询该 homeserver 上的 Matrix 用户目录。
- 房间查找会直接接受显式房间 ID 和别名，然后回退到搜索该账号已加入的房间名称。
- 已加入房间名称查找是尽力而为的。如果房间名称无法解析为 ID 或别名，运行时 allowlist 解析会忽略它。

## 配置参考

- `enabled`：启用或禁用该渠道。
- `name`：账号的可选标签。
- `defaultAccount`：配置多个 Matrix 账号时的首选账号 ID。
- `homeserver`：homeserver URL，例如 `https://matrix.example.org`。
- `allowPrivateNetwork`：允许该 Matrix 账号连接到私有/内部 homeserver。当 homeserver 解析到 `localhost`、LAN/Tailscale IP 或内部主机（如 `matrix-synapse`）时，请启用此项。
- `proxy`：Matrix 流量的可选 HTTP(S) 代理 URL。命名账号可使用自己的 `proxy` 覆盖顶层默认值。
- `userId`：完整 Matrix 用户 ID，例如 `@bot:example.org`。
- `accessToken`：基于 token 的认证 access token。`channels.matrix.accessToken` 和 `channels.matrix.accounts.<id>.accessToken` 支持明文值和 SecretRef 值，适用于 env/file/exec providers。参阅 [Secrets Management](/zh-CN/gateway/secrets)。
- `password`：用于基于密码登录的密码。支持明文值和 SecretRef 值。
- `deviceId`：显式 Matrix 设备 ID。
- `deviceName`：密码登录使用的设备显示名称。
- `avatarUrl`：用于资料同步和 `set-profile` 更新的已存储自身头像 URL。
- `initialSyncLimit`：启动同步事件限制。
- `encryption`：启用 E2EE。
- `allowlistOnly`：对私信和房间强制仅 allowlist 行为。
- `allowBots`：允许来自其他已配置 OpenClaw Matrix 账号的消息（`true` 或 `"mentions"`）。
- `groupPolicy`：`open`、`allowlist` 或 `disabled`。
- `contextVisibility`：补充房间上下文可见性模式（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`：房间流量的用户 ID allowlist。
- `groupAllowFrom` 条目应为完整 Matrix 用户 ID。无法解析的名称会在运行时被忽略。
- `historyLimit`：作为群组历史上下文包含的最大房间消息数。会回退到 `messages.groupChat.historyLimit`。设置 `0` 可禁用。
- `replyToMode`：`off`、`first` 或 `all`。
- `markdown`：出站 Matrix 文本的可选 Markdown 渲染配置。
- `streaming`：`off`（默认）、`partial`、`quiet`、`true` 或 `false`。`partial` 和 `true` 会启用预览优先的草稿更新，并使用普通 Matrix 文本消息。`quiet` 会为自托管推送规则设置使用非通知预览通知。
- `blockStreaming`：`true` 会在草稿预览流式传输处于活动状态时，为已完成的助手块启用单独进度消息。
- `threadReplies`：`off`、`inbound` 或 `always`。
- `threadBindings`：线程绑定会话路由和生命周期的每渠道覆盖。
- `startupVerification`：启动时自动自我验证请求模式（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`：自动启动验证请求的重试前冷却时间。
- `textChunkLimit`：出站消息分块大小。
- `chunkMode`：`length` 或 `newline`。
- `responsePrefix`：出站回复的可选消息前缀。
- `ackReaction`：此渠道/账号的可选确认回应覆盖。
- `ackReactionScope`：可选确认回应作用域覆盖（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`：入站回应通知模式（`own`、`off`）。
- `mediaMaxMb`：Matrix 媒体处理的媒体大小上限（MB）。适用于出站发送和入站媒体处理。
- `autoJoin`：邀请自动加入策略（`always`、`allowlist`、`off`）。默认值：`off`。
- `autoJoinAllowlist`：当 `autoJoin` 为 `allowlist` 时允许的房间/别名。别名条目会在处理邀请时解析为房间 ID；OpenClaw 不信任被邀请房间声明的别名状态。
- `dm`：私信策略块（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.allowFrom` 条目应为完整 Matrix 用户 ID，除非你已经通过实时目录查找完成解析。
- `dm.sessionScope`：`per-user`（默认）或 `per-room`。如果你希望每个 Matrix 私信房间都保留独立上下文，即使对方是同一个人，也请使用 `per-room`。
- `dm.threadReplies`：仅私信用线程策略覆盖（`off`、`inbound`、`always`）。它会覆盖顶层 `threadReplies` 设置，影响私信中的回复位置和会话隔离。
- `execApprovals`：Matrix 原生 exec 审批发送（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`：允许审批 exec 请求的 Matrix 用户 ID。当 `dm.allowFrom` 已标识审批人时可省略。
- `execApprovals.target`：`dm | channel | both`（默认值：`dm`）。
- `accounts`：每账号命名覆盖。顶层 `channels.matrix` 值会作为这些条目的默认值。
- `groups`：每房间策略映射。优先使用房间 ID 或别名；无法解析的房间名称会在运行时被忽略。会话/群组身份在解析后使用稳定的房间 ID，而人类可读标签仍来自房间名称。
- `groups.<room>.account`：在多账号设置中，将某个继承的房间条目限制到特定 Matrix 账号。
- `groups.<room>.allowBots`：已配置 bot 发送者的房间级覆盖（`true` 或 `"mentions"`）。
- `groups.<room>.users`：每房间发送者 allowlist。
- `groups.<room>.tools`：每房间工具允许/拒绝覆盖。
- `groups.<room>.autoReply`：房间级提及门控覆盖。`true` 会禁用该房间的提及要求；`false` 会重新强制启用。
- `groups.<room>.skills`：可选的房间级技能过滤器。
- `groups.<room>.systemPrompt`：可选的房间级 system prompt 片段。
- `rooms`：`groups` 的旧版别名。
- `actions`：每操作工具门控（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 相关

- [渠道概览](/zh-CN/channels) — 所有支持的渠道
- [配对](/zh-CN/channels/pairing) — 私信认证和配对流程
- [群组](/zh-CN/channels/groups) — 群聊行为和提及门控
- [渠道路由](/zh-CN/channels/channel-routing) — 消息的会话路由
- [安全](/zh-CN/gateway/security) — 访问模型和加固
