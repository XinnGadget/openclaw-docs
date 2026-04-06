---
read_when:
    - 在 OpenClaw 中设置 Matrix
    - 配置 Matrix E2EE 和验证
summary: Matrix 支持状态、设置和配置示例
title: Matrix
x-i18n:
    generated_at: "2026-04-06T00:21:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5506f966d78d5f09d597c4850088f8ee1c91cf4d5f6a7b5cade80d89b5bdf1bc
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix 是 OpenClaw 的 Matrix 内置渠道插件。
它使用官方的 `matrix-js-sdk`，并支持私信、房间、线程、媒体、反应、投票、位置和 E2EE。

## 内置插件

Matrix 作为内置插件随当前的 OpenClaw 版本一起提供，因此普通的打包构建不需要单独安装。

如果你使用的是较旧的构建版本，或者使用了排除 Matrix 的自定义安装，请手动安装：

从 npm 安装：

```bash
openclaw plugins install @openclaw/matrix
```

从本地检出安装：

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

有关插件行为和安装规则，请参阅 [Plugins](/zh-CN/tools/plugin)。

## 设置

1. 确保 Matrix 插件可用。
   - 当前打包的 OpenClaw 版本已内置它。
   - 较旧/自定义安装可以使用上面的命令手动添加它。
2. 在你的 homeserver 上创建一个 Matrix 账户。
3. 使用以下任一方式配置 `channels.matrix`：
   - `homeserver` + `accessToken`，或
   - `homeserver` + `userId` + `password`。
4. 重启 Gateway 网关。
5. 与机器人开始私信，或邀请它加入一个房间。

交互式设置路径：

```bash
openclaw channels add
openclaw configure --section channels
```

Matrix 向导实际会询问的内容：

- homeserver URL
- 认证方式：访问令牌或密码
- 仅当你选择密码认证时才需要用户 ID
- 可选设备名称
- 是否启用 E2EE
- 是否现在配置 Matrix 房间访问

需要注意的向导行为：

- 如果所选账户已存在 Matrix 认证环境变量，且该账户尚未在配置中保存认证信息，向导会提供一个环境变量快捷方式，并且只会为该账户写入 `enabled: true`。
- 当你以交互方式添加另一个 Matrix 账户时，输入的账户名称会被规范化为配置和环境变量中使用的账户 ID。例如，`Ops Bot` 会变为 `ops-bot`。
- 私信允许列表提示可立即接受完整的 `@user:server` 值。显示名称仅在实时目录查找找到一个精确匹配时可用；否则向导会要求你使用完整的 Matrix ID 重试。
- 房间允许列表提示可直接接受房间 ID 和别名。它们也可以实时解析已加入房间的名称，但在设置期间无法解析的名称只会按输入原样保留，之后会被运行时允许列表解析忽略。优先使用 `!room:server` 或 `#alias:server`。
- 运行时房间/会话标识使用稳定的 Matrix 房间 ID。房间声明的别名仅用作查找输入，不会作为长期会话键或稳定的群组标识。
- 如需在保存前解析房间名称，请使用 `openclaw channels resolve --channel matrix "Project Room"`。

基于令牌的最小设置：

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

基于密码的设置（登录后会缓存令牌）：

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

Matrix 将缓存的凭证存储在 `~/.openclaw/credentials/matrix/` 中。
默认账户使用 `credentials.json`；命名账户使用 `credentials-<account>.json`。
当那里存在缓存凭证时，即使当前认证未直接在配置中设置，OpenClaw 也会在设置、Doctor 和渠道状态发现中将 Matrix 视为已配置。

环境变量等价项（当未设置配置键时使用）：

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

对于非默认账户，请使用带账户作用域的环境变量：

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

账户 `ops` 的示例：

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

对于规范化账户 ID `ops-bot`，请使用：

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix 会对账户 ID 中的标点进行转义，以避免带作用域的环境变量发生冲突。
例如，`-` 会变为 `_X2D_`，因此 `ops-prod` 会映射为 `MATRIX_OPS_X2D_PROD_*`。

仅当这些认证环境变量已存在，且所选账户尚未在配置中保存 Matrix 认证信息时，交互式向导才会提供环境变量快捷方式。

## 配置示例

这是一个实用的基础配置，启用了私信配对、房间允许列表和 E2EE：

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

当你希望 OpenClaw 发送一条实时预览回复、在模型生成文本时原地编辑该预览，并在回复完成时将其定稿时，请将 `channels.matrix.streaming` 设置为 `"partial"`：

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` 是默认值。OpenClaw 会等待最终回复并一次性发送。
- `streaming: "partial"` 会为当前智能体块创建一条可编辑的预览消息，并使用普通 Matrix 文本消息。这会保留 Matrix 传统的“先预览后通知”行为，因此标准客户端可能会对第一段流式预览文本发出通知，而不是对完成后的内容块发出通知。
- `streaming: "quiet"` 会为当前智能体块创建一条可编辑的静默预览通知。仅当你还为已完成的预览编辑配置了接收者推送规则时，才使用此选项。
- `blockStreaming: true` 会启用单独的 Matrix 进度消息。启用预览流式传输后，Matrix 会保留当前块的实时草稿，并将已完成的块保留为单独消息。
- 当预览流式传输开启且 `blockStreaming` 关闭时，Matrix 会原地编辑实时草稿，并在块或轮次结束时将同一事件定稿。
- 如果预览内容不再适合放入单个 Matrix 事件，OpenClaw 会停止预览流式传输并回退到普通最终发送。
- 媒体回复仍会正常发送附件。如果过期预览无法再安全复用，OpenClaw 会在发送最终媒体回复之前将其删除。
- 预览编辑会产生额外的 Matrix API 调用。如果你希望采用最保守的速率限制行为，请保持关闭流式传输。

`blockStreaming` 本身不会启用草稿预览。
请使用 `streaming: "partial"` 或 `streaming: "quiet"` 进行预览编辑；如果你还希望已完成的智能体块作为单独的进度消息保留可见，再额外添加 `blockStreaming: true`。

如果你需要标准 Matrix 通知而不想配置自定义推送规则，请使用 `streaming: "partial"` 以获得“先预览”行为，或者保持 `streaming` 关闭以仅在最终完成时发送。使用 `streaming: "off"` 时：

- `blockStreaming: true` 会将每个已完成的块作为普通可通知的 Matrix 消息发送。
- `blockStreaming: false` 仅发送最终完成的回复，作为普通可通知的 Matrix 消息。

### 自托管静默定稿预览的推送规则

如果你运行自己的 Matrix 基础设施，并希望静默预览仅在一个块或最终回复完成时才通知，请设置 `streaming: "quiet"`，并为已定稿的预览编辑添加按用户划分的推送规则。

这通常是接收用户侧的设置，而不是 homeserver 全局配置更改：

开始前的快速说明：

- 接收用户 = 应该收到通知的人
- 机器人用户 = 发送回复的 OpenClaw Matrix 账户
- 对以下 API 调用使用接收用户的访问令牌
- 在推送规则中将 `sender` 与机器人用户的完整 MXID 匹配

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

2. 确保接收账户已经可以接收普通 Matrix 推送通知。静默预览规则仅在该用户已有正常工作的推送器/设备时才有效。

3. 获取接收用户的访问令牌。
   - 使用接收用户的令牌，而不是机器人的令牌。
   - 复用现有客户端会话令牌通常最简单。
   - 如果你需要签发一个新的令牌，可以通过标准 Matrix Client-Server API 登录：

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

4. 验证接收账户已经具有推送器：

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

如果这里没有返回活动的推送器/设备，请先修复普通 Matrix 通知，然后再添加下面的 OpenClaw 规则。

OpenClaw 会用以下标记标识已定稿的纯文本预览编辑：

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. 为每个应接收这些通知的接收账户创建一条覆盖推送规则：

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview" \
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

运行命令前请替换以下值：

- `https://matrix.example.org`：你的 homeserver 基础 URL
- `$USER_ACCESS_TOKEN`：接收用户的访问令牌
- `@bot:example.org`：你的 OpenClaw Matrix 机器人 MXID，而不是接收用户的 MXID

该规则会根据事件发送者进行评估：

- 使用接收用户的令牌进行认证
- 将 `sender` 与 OpenClaw 机器人 MXID 匹配

6. 验证该规则是否存在：

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview"
```

7. 测试一条流式回复。在静默模式下，房间应显示一条静默草稿预览，而最终的原地编辑应在块或轮次结束时通知一次。

说明：

- 请使用接收用户的访问令牌创建规则，而不是机器人的令牌。
- 新的用户定义 `override` 规则会插入到默认抑制规则之前，因此不需要额外的排序参数。
- 这仅影响 OpenClaw 可以安全原地定稿的纯文本预览编辑。媒体回退和过期预览回退仍使用普通 Matrix 发送。
- 如果 `GET /_matrix/client/v3/pushers` 显示没有推送器，则该用户尚未为此账户/设备启用正常工作的 Matrix 推送传递。

#### Synapse

对于 Synapse，上述设置通常本身就足够：

- 无需为已定稿的 OpenClaw 预览通知做任何特殊的 `homeserver.yaml` 更改。
- 如果你的 Synapse 部署已经能发送普通 Matrix 推送通知，那么上面的用户令牌 + `pushrules` 调用就是主要设置步骤。
- 如果你在反向代理或 workers 后面运行 Synapse，请确保 `/_matrix/client/.../pushrules/` 能正确到达 Synapse。
- 如果你运行 Synapse workers，请确保 pushers 状态健康。推送传递由主进程或 `synapse.app.pusher` / 已配置的 pusher workers 处理。

#### Tuwunel

对于 Tuwunel，请使用与上方相同的设置流程和 push-rule API 调用：

- 对于已定稿预览标记本身，不需要任何 Tuwunel 特定配置。
- 如果该用户的普通 Matrix 通知已经正常工作，那么上面的用户令牌 + `pushrules` 调用就是主要设置步骤。
- 如果当用户在另一台设备上活跃时通知似乎消失，请检查是否启用了 `suppress_push_when_active`。Tuwunel 在 2025 年 9 月 12 日发布的 Tuwunel 1.4.2 中添加了此选项，它可能会在一台设备处于活跃状态时，有意抑制发送到其他设备的推送。

## 加密和验证

在加密（E2EE）房间中，出站图片事件使用 `thumbnail_file`，因此图片预览会与完整附件一起加密。未加密房间仍使用普通的 `thumbnail_url`。无需配置 —— 插件会自动检测 E2EE 状态。

### 机器人对机器人房间

默认情况下，来自其他已配置 OpenClaw Matrix 账户的 Matrix 消息会被忽略。

当你有意启用智能体之间的 Matrix 通信时，请使用 `allowBots`：

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

- `allowBots: true` 会在允许的房间和私信中接受来自其他已配置 Matrix 机器人账户的消息。
- `allowBots: "mentions"` 仅当这些消息在房间中明确提及此机器人时才接受。私信仍然允许。
- `groups.<room>.allowBots` 会覆盖单个房间的账户级设置。
- OpenClaw 仍会忽略来自同一 Matrix 用户 ID 的消息，以避免自回复循环。
- Matrix 在这里不提供原生机器人标记；OpenClaw 将“机器人撰写”视为“由此 OpenClaw Gateway 网关上的另一个已配置 Matrix 账户发送”。

在共享房间中启用机器人到机器人流量时，请使用严格的房间允许列表和提及要求。

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

引导交叉签名和验证状态：

```bash
openclaw matrix verify bootstrap
```

多账户支持：使用 `channels.matrix.accounts` 配置每个账户的凭证和可选 `name`。共享模式请参阅 [Configuration reference](/zh-CN/gateway/configuration-reference#multi-account-all-channels)。

详细引导诊断：

```bash
openclaw matrix verify bootstrap --verbose
```

在引导前强制执行全新的交叉签名身份重置：

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

删除当前服务器备份并创建全新的备份基线。如果无法干净地加载已存储的备份密钥，此重置还可以重新创建秘密存储，以便未来的冷启动可以加载新的备份密钥：

```bash
openclaw matrix verify backup reset --yes
```

所有 `verify` 命令默认都很简洁（包括安静的内部 SDK 日志），只有在使用 `--verbose` 时才显示详细诊断。
在脚本中使用时，请使用 `--json` 以获取完整的机器可读输出。

在多账户设置中，除非你传递 `--account <id>`，否则 Matrix CLI 命令会使用隐式的 Matrix 默认账户。
如果你配置了多个命名账户，请先设置 `channels.matrix.defaultAccount`，否则这些隐式 CLI 操作将停止并要求你显式选择一个账户。
当你希望验证或设备操作显式针对某个命名账户时，请使用 `--account`：

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

当某个命名账户禁用了加密或加密不可用时，Matrix 警告和验证错误会指向该账户的配置键，例如 `channels.matrix.accounts.assistant.encryption`。

### “已验证”是什么意思

只有当此 Matrix 设备由你自己的交叉签名身份验证后，OpenClaw 才会将其视为已验证。
实际上，`openclaw matrix verify status --verbose` 会暴露三个信任信号：

- `Locally trusted`：此设备仅被当前客户端信任
- `Cross-signing verified`：SDK 报告该设备已通过交叉签名验证
- `Signed by owner`：该设备由你自己的自签名密钥签名

只有在存在交叉签名验证或所有者签名时，`Verified by owner` 才会变为 `yes`。
仅有本地信任不足以让 OpenClaw 将设备视为完全已验证。

### bootstrap 的作用

`openclaw matrix verify bootstrap` 是用于加密 Matrix 账户的修复和设置命令。
它会按顺序完成以下所有操作：

- 引导秘密存储，并在可能时复用现有恢复密钥
- 引导交叉签名并上传缺失的公开交叉签名密钥
- 尝试标记并交叉签名当前设备
- 如果尚不存在，则创建新的服务器端房间密钥备份

如果 homeserver 要求交互式认证以上传交叉签名密钥，OpenClaw 会先尝试不带认证上传，然后尝试 `m.login.dummy`，如果配置了 `channels.matrix.password`，则再尝试 `m.login.password`。

仅当你有意丢弃当前交叉签名身份并创建一个新的身份时，才使用 `--force-reset-cross-signing`。

如果你有意丢弃当前房间密钥备份，并为未来消息开始一个新的备份基线，请使用 `openclaw matrix verify backup reset --yes`。
只有在你接受无法恢复的旧加密历史将继续不可用，并且接受 OpenClaw 可能在当前备份密钥无法安全加载时重新创建秘密存储的情况下，才这样做。

### 全新备份基线

如果你希望未来的加密消息继续正常工作，并接受丢失无法恢复的旧历史，请按顺序运行以下命令：

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

当你希望显式针对某个命名 Matrix 账户时，请为每条命令添加 `--account <id>`。

### 启动行为

当 `encryption: true` 时，Matrix 默认将 `startupVerification` 设置为 `"if-unverified"`。
启动时，如果此设备仍未验证，Matrix 将在另一个 Matrix 客户端中请求自验证，在已有待处理请求时跳过重复请求，并在重启后重试前应用本地冷却时间。
默认情况下，失败的请求尝试会比成功创建请求后更快重试。
将 `startupVerification: "off"` 设置为禁用自动启动请求，或者调整 `startupVerificationCooldownHours` 以获得更短或更长的重试窗口。

启动时还会自动执行一次保守的加密引导流程。
该流程会优先尝试复用当前秘密存储和交叉签名身份，并避免重置交叉签名，除非你运行显式的引导修复流程。

如果启动时发现引导状态损坏，且已配置 `channels.matrix.password`，OpenClaw 可以尝试更严格的修复路径。
如果当前设备已经由所有者签名，OpenClaw 会保留该身份，而不是自动重置它。

从之前公开的 Matrix 插件升级：

- OpenClaw 会在可能的情况下自动复用同一个 Matrix 账户、访问令牌和设备身份。
- 在运行任何可操作的 Matrix 迁移更改之前，OpenClaw 会在 `~/Backups/openclaw-migrations/` 下创建或复用恢复快照。
- 如果你使用多个 Matrix 账户，请在从旧的平面存储布局升级前设置 `channels.matrix.defaultAccount`，这样 OpenClaw 才知道应将共享的旧状态分配给哪个账户。
- 如果之前的插件在本地存储了 Matrix 房间密钥备份解密密钥，启动时或运行 `openclaw doctor --fix` 时会自动将其导入新的恢复密钥流程。
- 如果在准备迁移之后 Matrix 访问令牌发生了变化，启动时现在会扫描同级 token-hash 存储根目录，以查找待恢复的旧状态，然后才会放弃自动备份恢复。
- 如果同一账户、homeserver 和用户的 Matrix 访问令牌之后再次更改，OpenClaw 现在会优先复用最完整的现有 token-hash 存储根目录，而不是从空的 Matrix 状态目录开始。
- 在下一次 Gateway 网关启动时，已备份的房间密钥会自动恢复到新的加密存储中。
- 如果旧插件中存在从未备份过的仅本地房间密钥，OpenClaw 会明确发出警告。由于这些密钥无法从之前的 rust 加密存储中自动导出，因此某些旧的加密历史在手动恢复之前可能仍不可用。
- 完整升级流程、限制、恢复命令和常见迁移消息，请参阅 [Matrix migration](/zh-CN/install/migrating-matrix)。

加密运行时状态按每个账户、每个用户的 token-hash 根目录组织，位于
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/`。
该目录在这些功能被使用时包含同步存储（`bot-storage.json`）、加密存储（`crypto/`）、
恢复密钥文件（`recovery-key.json`）、IndexedDB 快照（`crypto-idb-snapshot.json`）、
线程绑定（`thread-bindings.json`）和启动验证状态（`startup-verification.json`）。
当令牌变化但账户身份保持不变时，OpenClaw 会为该 account/homeserver/user 元组复用最佳的现有根目录，因此先前的同步状态、加密状态、线程绑定和启动验证状态仍然可见。

### Node 加密存储模型

此插件中的 Matrix E2EE 在 Node 中使用官方 `matrix-js-sdk` Rust 加密路径。
当你希望加密状态在重启后仍能保留时，该路径需要基于 IndexedDB 的持久化。

OpenClaw 目前在 Node 中通过以下方式提供该能力：

- 使用 `fake-indexeddb` 作为 SDK 所期望的 IndexedDB API shim
- 在 `initRustCrypto` 之前，从 `crypto-idb-snapshot.json` 恢复 Rust 加密 IndexedDB 内容
- 在初始化之后和运行时，将更新后的 IndexedDB 内容持久化回 `crypto-idb-snapshot.json`
- 使用建议性文件锁对 `crypto-idb-snapshot.json` 的快照恢复和持久化进行串行化，以避免 Gateway 网关运行时持久化与 CLI 维护在同一快照文件上发生竞争

这是兼容性/存储层面的处理，不是自定义加密实现。
该快照文件属于敏感运行时状态，并以严格的文件权限存储。
在 OpenClaw 的安全模型下，Gateway 网关主机和本地 OpenClaw 状态目录已经位于受信任的操作员边界内，因此这主要是一个操作层面的持久性问题，而不是单独的远程信任边界。

计划中的改进：

- 为持久化 Matrix 密钥材料添加 SecretRef 支持，以便恢复密钥和相关的存储加密密钥可以来自 OpenClaw secrets providers，而不仅仅是本地文件

## 配置文件管理

使用以下命令更新所选账户的 Matrix 自身资料：

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

当你希望显式针对某个命名 Matrix 账户时，请添加 `--account <id>`。

Matrix 可直接接受 `mxc://` 头像 URL。当你传入 `http://` 或 `https://` 头像 URL 时，OpenClaw 会先将其上传到 Matrix，然后将解析得到的 `mxc://` URL 回写到 `channels.matrix.avatarUrl`（或所选账户的覆盖项）中。

## 自动验证通知

Matrix 现在会将验证生命周期通知直接作为 `m.notice` 消息发布到严格的私信验证房间中。
这包括：

- 验证请求通知
- 验证就绪通知（带明确的“通过表情符号验证”指引）
- 验证开始和完成通知
- SAS 详情（表情符号和十进制），如可用

来自另一个 Matrix 客户端的传入验证请求会被 OpenClaw 跟踪并自动接受。
对于自验证流程，当表情符号验证可用时，OpenClaw 也会自动启动 SAS 流程并确认自己这一侧。
对于来自另一个 Matrix 用户/设备的验证请求，OpenClaw 会自动接受请求，然后等待 SAS 流程正常继续。
你仍然需要在你的 Matrix 客户端中比对表情符号或十进制 SAS，并在那里确认“它们匹配”，以完成验证。

OpenClaw 不会盲目自动接受自发起的重复流程。若自验证请求已经处于待处理状态，启动时会跳过创建新请求。

验证协议/系统通知不会转发到智能体聊天流水线，因此不会产生 `NO_REPLY`。

### 设备清理

由 OpenClaw 管理的旧 Matrix 设备可能会在账户中不断累积，使加密房间中的信任关系更难判断。
可使用以下命令列出它们：

```bash
openclaw matrix devices list
```

使用以下命令移除过期的 OpenClaw 管理设备：

```bash
openclaw matrix devices prune-stale
```

### 直接房间修复

如果私信状态不同步，OpenClaw 可能会留下过期的 `m.direct` 映射，使其指向旧的单人房间而不是当前的私信。可使用以下命令检查某个对端的当前映射：

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

使用以下命令修复它：

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

修复逻辑将 Matrix 特定逻辑保留在插件内部：

- 它优先选择已经在 `m.direct` 中映射的严格 1:1 私信
- 否则回退到与该用户当前已加入的任意严格 1:1 私信
- 如果不存在健康的私信，则创建一个新的直接房间，并重写 `m.direct` 使其指向该房间

修复流程不会自动删除旧房间。它只会选择健康的私信并更新映射，以便新的 Matrix 发送、验证通知和其他私信流程再次指向正确的房间。

## 线程

Matrix 支持对自动回复和消息工具发送同时使用原生 Matrix 线程。

- `dm.sessionScope: "per-user"`（默认）会让 Matrix 私信路由按发送者范围处理，因此多个私信房间在解析到同一对端时可以共享一个会话。
- `dm.sessionScope: "per-room"` 会将每个 Matrix 私信房间隔离为各自独立的会话键，同时仍使用普通的私信认证和允许列表检查。
- 显式 Matrix 会话绑定仍然优先于 `dm.sessionScope`，因此绑定的房间和线程会保留其选定的目标会话。
- `threadReplies: "off"` 会让回复保持在顶层，并让传入的线程消息继续使用父级会话。
- `threadReplies: "inbound"` 仅当传入消息本来就在该线程中时，才在线程内回复。
- `threadReplies: "always"` 会让房间回复始终保留在线程中，并以触发消息为线程根，从第一条触发消息开始通过匹配的线程范围会话路由该对话。
- `dm.threadReplies` 仅覆盖私信的顶层设置。例如，你可以保持房间线程隔离，同时让私信保持扁平。
- 传入的线程消息会将线程根消息作为额外的智能体上下文。
- 当目标是同一房间或同一私信用户目标时，消息工具发送现在会自动继承当前 Matrix 线程，除非显式提供了 `threadId`。
- 仅当当前会话元数据能证明是同一 Matrix 账户上的同一私信对端时，才会启用同会话私信用户目标复用；否则 OpenClaw 会回退到普通的按用户范围路由。
- 当 OpenClaw 发现某个 Matrix 私信房间与另一个私信房间在同一个共享 Matrix 私信会话上发生冲突时，如果启用了线程绑定且存在 `dm.sessionScope` 提示，它会在该房间发布一条一次性的 `m.notice`，其中包含 `/focus` 逃生入口。
- Matrix 支持运行时线程绑定。`/focus`、`/unfocus`、`/agents`、`/session idle`、`/session max-age` 和线程绑定的 `/acp spawn` 现在都可在 Matrix 房间和私信中使用。
- 当 `threadBindings.spawnSubagentSessions=true` 时，顶层 Matrix 房间/私信中的 `/focus` 会创建一个新的 Matrix 线程，并将其绑定到目标会话。
- 在现有 Matrix 线程内运行 `/focus` 或 `/acp spawn --thread here` 时，则会改为绑定当前线程。

## ACP 会话绑定

Matrix 房间、私信和现有 Matrix 线程都可以转换为持久的 ACP 工作区，而无需更改聊天界面。

面向操作员的快速流程：

- 在你希望继续使用的 Matrix 私信、房间或现有线程中运行 `/acp spawn codex --bind here`。
- 在顶层 Matrix 私信或房间中，当前私信/房间会继续作为聊天界面，后续消息会路由到新生成的 ACP 会话。
- 在现有 Matrix 线程内，`--bind here` 会将当前线程原地绑定。
- `/new` 和 `/reset` 会原地重置同一个已绑定 ACP 会话。
- `/acp close` 会关闭 ACP 会话并移除绑定。

说明：

- `--bind here` 不会创建子 Matrix 线程。
- `threadBindings.spawnAcpSessions` 仅在 `/acp spawn --thread auto|here` 时需要，因为此时 OpenClaw 需要创建或绑定一个子 Matrix 线程。

### 线程绑定配置

Matrix 会继承来自 `session.threadBindings` 的全局默认值，同时也支持按渠道覆盖：

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Matrix 线程绑定的生成标志为可选启用：

- 设置 `threadBindings.spawnSubagentSessions: true` 以允许顶层 `/focus` 创建并绑定新的 Matrix 线程。
- 设置 `threadBindings.spawnAcpSessions: true` 以允许 `/acp spawn --thread auto|here` 将 ACP 会话绑定到 Matrix 线程。

## 反应

Matrix 支持出站反应操作、入站反应通知和入站确认反应。

- 出站反应工具受 `channels["matrix"].actions.reactions` 控制。
- `react` 会向特定 Matrix 事件添加一个反应。
- `reactions` 会列出特定 Matrix 事件当前的反应摘要。
- `emoji=""` 会移除机器人账户在该事件上的所有自有反应。
- `remove: true` 仅移除机器人账户的指定表情反应。

确认反应使用标准的 OpenClaw 解析顺序：

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- 智能体身份表情符号回退

确认反应范围按以下顺序解析：

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

反应通知模式按以下顺序解析：

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- 默认：`own`

当前行为：

- `reactionNotifications: "own"` 会在新增的 `m.reaction` 事件针对机器人撰写的 Matrix 消息时将其转发。
- `reactionNotifications: "off"` 会禁用反应系统事件。
- 反应移除仍不会被合成为系统事件，因为 Matrix 将其表示为删除操作，而不是独立的 `m.reaction` 移除事件。

## 历史上下文

- `channels.matrix.historyLimit` 控制当 Matrix 房间消息触发智能体时，作为 `InboundHistory` 包含多少条最近的房间消息。
- 它会回退到 `messages.groupChat.historyLimit`。设为 `0` 可禁用。
- Matrix 房间历史仅限房间。私信仍使用普通会话历史。
- Matrix 房间历史是待处理式的：OpenClaw 会缓冲尚未触发回复的房间消息，然后在提及或其他触发到来时对该窗口进行快照。
- 当前触发消息不会包含在 `InboundHistory` 中；它会保留在该轮次的主入站正文中。
- 对同一 Matrix 事件的重试会复用原始历史快照，而不是漂移到更新的房间消息。

## 上下文可见性

Matrix 支持共享的 `contextVisibility` 控制，用于补充房间上下文，例如获取到的回复文本、线程根和待处理历史。

- `contextVisibility: "all"` 是默认值。补充上下文会按接收时原样保留。
- `contextVisibility: "allowlist"` 会将补充上下文过滤为通过当前房间/用户允许列表检查的发送者。
- `contextVisibility: "allowlist_quote"` 的行为与 `allowlist` 相同，但仍会保留一条显式引用的回复。

此设置影响的是补充上下文的可见性，而不是入站消息本身是否可以触发回复。
触发授权仍来自 `groupPolicy`、`groups`、`groupAllowFrom` 和私信策略设置。

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

有关提及门控和允许列表行为，请参阅 [Groups](/zh-CN/channels/groups)。

Matrix 私信配对示例：

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

如果一个尚未获批的 Matrix 用户在获批前持续向你发送消息，OpenClaw 会复用同一个待处理配对码，并可能在短暂冷却后再次发送提醒回复，而不是生成新的配对码。

共享的私信配对流程和存储布局请参阅 [Pairing](/zh-CN/channels/pairing)。

## 执行审批

Matrix 可以充当 Matrix 账户的执行审批客户端。

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers`（可选；回退到 `channels.matrix.dm.allowFrom`）
- `channels.matrix.execApprovals.target`（`dm` | `channel` | `both`，默认：`dm`）
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

审批者必须是 Matrix 用户 ID，例如 `@owner:example.org`。当 `enabled` 未设置或为 `"auto"`，且至少能解析出一个审批者时，Matrix 会自动启用原生执行审批，无论该审批者来自 `execApprovals.approvers` 还是 `channels.matrix.dm.allowFrom`。设置 `enabled: false` 可显式禁用 Matrix 作为原生审批客户端。否则，审批请求会回退到其他已配置的审批路由或执行审批回退策略。

当前原生 Matrix 路由仅支持 exec：

- `channels.matrix.execApprovals.*` 仅控制执行审批的原生私信/渠道路由。
- 插件审批仍使用共享的同聊天 `/approve`，以及任何已配置的 `approvals.plugin` 转发。
- 当 Matrix 能安全推断审批者时，它仍可复用 `channels.matrix.dm.allowFrom` 用于插件审批授权，但不会公开单独的原生插件审批私信/渠道分发路径。

发送规则：

- `target: "dm"` 会将审批提示发送到审批者的私信
- `target: "channel"` 会将提示发回原始 Matrix 房间或私信
- `target: "both"` 会同时发送到审批者私信和原始 Matrix 房间或私信

Matrix 审批提示会在主要审批消息上预置反应快捷方式：

- `✅` = 允许一次
- `❌` = 拒绝
- `♾️` = 始终允许（当该决定受当前有效执行策略允许时）

审批者可以对该消息添加反应，也可以使用回退斜杠命令：`/approve <id> allow-once`、`/approve <id> allow-always` 或 `/approve <id> deny`。

只有已解析的审批者才能批准或拒绝。渠道发送会包含命令文本，因此仅在受信任房间中启用 `channel` 或 `both`。

Matrix 审批提示复用共享核心审批规划器。Matrix 特定的原生界面仅作为执行审批的传输层：房间/私信路由以及消息发送/更新/删除行为。

按账户覆盖：

- `channels.matrix.accounts.<account>.execApprovals`

相关文档：[Exec approvals](/zh-CN/tools/exec-approvals)

## 多账户示例

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

顶层 `channels.matrix` 值会作为命名账户的默认值，除非某个账户显式覆盖它们。
你可以使用 `groups.<room>.account`（或旧版 `rooms.<room>.account`）将继承的房间条目限定到某一个 Matrix 账户。
不带 `account` 的条目会在所有 Matrix 账户之间共享，而带有 `account: "default"` 的条目在默认账户直接配置在顶层 `channels.matrix.*` 时仍然有效。
部分共享认证默认值本身不会创建单独的隐式默认账户。只有当该默认账户具有新的认证信息（`homeserver` 加 `accessToken`，或 `homeserver` 加 `userId` 和 `password`）时，OpenClaw 才会合成顶层 `default` 账户；命名账户仍然可以在缓存凭证稍后满足认证时，通过 `homeserver` 加 `userId` 保持可发现。
如果 Matrix 已经恰好有一个命名账户，或者 `defaultAccount` 指向一个现有命名账户键，则从单账户到多账户的修复/设置提升会保留该账户，而不是创建新的 `accounts.default` 条目。只有 Matrix 认证/引导键会移动到这个被提升的账户中；共享发送策略键会保留在顶层。
当你希望 OpenClaw 在隐式路由、探测和 CLI 操作中优先使用某个命名 Matrix 账户时，请设置 `defaultAccount`。
如果你配置了多个命名账户，请设置 `defaultAccount`，或者为依赖隐式账户选择的 CLI 命令传递 `--account <id>`。
当你希望对单个命令覆盖该隐式选择时，请将 `--account <id>` 传给 `openclaw matrix verify ...` 和 `openclaw matrix devices ...`。

## 私有/LAN homeserver

默认情况下，出于 SSRF 防护考虑，OpenClaw 会阻止连接私有/内部 Matrix homeserver，除非你为每个账户显式选择启用。

如果你的 homeserver 运行在 localhost、LAN/Tailscale IP 或内部主机名上，请为该 Matrix 账户启用 `allowPrivateNetwork`：

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

此选择启用仅允许受信任的私有/内部目标。公共明文 homeserver，例如
`http://matrix.example.org:8008`，仍会被阻止。尽可能优先使用 `https://`。

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

命名账户可以使用 `channels.matrix.accounts.<id>.proxy` 覆盖顶层默认值。
OpenClaw 会对运行时 Matrix 流量和账户状态探测使用相同的代理设置。

## 目标解析

在 OpenClaw 任何要求你输入房间或用户目标的地方，Matrix 都接受以下目标形式：

- 用户：`@user:server`、`user:@user:server` 或 `matrix:user:@user:server`
- 房间：`!room:server`、`room:!room:server` 或 `matrix:room:!room:server`
- 别名：`#alias:server`、`channel:#alias:server` 或 `matrix:channel:#alias:server`

实时目录查找使用已登录的 Matrix 账户：

- 用户查找会查询该 homeserver 上的 Matrix 用户目录。
- 房间查找可直接接受显式房间 ID 和别名，然后回退到搜索该账户已加入的房间名称。
- 已加入房间名称查找为尽力而为。如果房间名称无法解析为 ID 或别名，则运行时允许列表解析会忽略它。

## 配置参考

- `enabled`：启用或禁用该渠道。
- `name`：账户的可选标签。
- `defaultAccount`：配置多个 Matrix 账户时的首选账户 ID。
- `homeserver`：homeserver URL，例如 `https://matrix.example.org`。
- `allowPrivateNetwork`：允许此 Matrix 账户连接私有/内部 homeserver。当 homeserver 解析为 `localhost`、LAN/Tailscale IP 或内部主机（如 `matrix-synapse`）时启用此项。
- `proxy`：Matrix 流量的可选 HTTP(S) 代理 URL。命名账户可使用自己的 `proxy` 覆盖顶层默认值。
- `userId`：完整 Matrix 用户 ID，例如 `@bot:example.org`。
- `accessToken`：基于令牌认证的访问令牌。`channels.matrix.accessToken` 和 `channels.matrix.accounts.<id>.accessToken` 在 env/file/exec providers 中都支持明文值和 SecretRef 值。请参阅 [Secrets Management](/zh-CN/gateway/secrets)。
- `password`：用于基于密码登录的密码。支持明文值和 SecretRef 值。
- `deviceId`：显式 Matrix 设备 ID。
- `deviceName`：用于密码登录的设备显示名称。
- `avatarUrl`：用于资料同步和 `set-profile` 更新的已存储自头像 URL。
- `initialSyncLimit`：启动同步事件限制。
- `encryption`：启用 E2EE。
- `allowlistOnly`：强制私信和房间仅使用允许列表行为。
- `allowBots`：允许来自其他已配置 OpenClaw Matrix 账户的消息（`true` 或 `"mentions"`）。
- `groupPolicy`：`open`、`allowlist` 或 `disabled`。
- `contextVisibility`：补充房间上下文可见性模式（`all`、`allowlist`、`allowlist_quote`）。
- `groupAllowFrom`：房间流量的用户 ID 允许列表。
- `groupAllowFrom` 条目应为完整 Matrix 用户 ID。未解析的名称会在运行时被忽略。
- `historyLimit`：作为群组历史上下文包含的最大房间消息数。会回退到 `messages.groupChat.historyLimit`。设为 `0` 可禁用。
- `replyToMode`：`off`、`first` 或 `all`。
- `markdown`：用于出站 Matrix 文本的可选 Markdown 渲染配置。
- `streaming`：`off`（默认）、`partial`、`quiet`、`true` 或 `false`。`partial` 和 `true` 会通过普通 Matrix 文本消息启用“先预览再更新”的草稿更新。`quiet` 则为自托管推送规则设置使用非通知预览通知。
- `blockStreaming`：`true` 会在草稿预览流式传输启用时，为已完成的智能体块启用单独进度消息。
- `threadReplies`：`off`、`inbound` 或 `always`。
- `threadBindings`：线程绑定会话路由和生命周期的按渠道覆盖。
- `startupVerification`：启动时自动自验证请求模式（`if-unverified`、`off`）。
- `startupVerificationCooldownHours`：自动启动验证请求重试前的冷却时间。
- `textChunkLimit`：出站消息分块大小。
- `chunkMode`：`length` 或 `newline`。
- `responsePrefix`：出站回复的可选消息前缀。
- `ackReaction`：此渠道/账户的可选确认反应覆盖。
- `ackReactionScope`：可选确认反应范围覆盖（`group-mentions`、`group-all`、`direct`、`all`、`none`、`off`）。
- `reactionNotifications`：入站反应通知模式（`own`、`off`）。
- `mediaMaxMb`：Matrix 媒体处理的媒体大小上限（MB）。适用于出站发送和入站媒体处理。
- `autoJoin`：邀请自动加入策略（`always`、`allowlist`、`off`）。默认：`off`。
- `autoJoinAllowlist`：当 `autoJoin` 为 `allowlist` 时允许的房间/别名。别名条目会在处理邀请时解析为房间 ID；OpenClaw 不信任被邀请房间声称的别名状态。
- `dm`：私信策略块（`enabled`、`policy`、`allowFrom`、`sessionScope`、`threadReplies`）。
- `dm.allowFrom` 条目应为完整 Matrix 用户 ID，除非你已通过实时目录查找解析过它们。
- `dm.sessionScope`：`per-user`（默认）或 `per-room`。当你希望每个 Matrix 私信房间即使对端相同也保持独立上下文时，请使用 `per-room`。
- `dm.threadReplies`：仅私信的线程策略覆盖（`off`、`inbound`、`always`）。它会覆盖顶层 `threadReplies` 设置，用于私信中的回复位置和会话隔离。
- `execApprovals`：Matrix 原生执行审批发送（`enabled`、`approvers`、`target`、`agentFilter`、`sessionFilter`）。
- `execApprovals.approvers`：允许审批执行请求的 Matrix 用户 ID。当 `dm.allowFrom` 已经标识出审批者时，此项为可选。
- `execApprovals.target`：`dm | channel | both`（默认：`dm`）。
- `accounts`：命名的按账户覆盖。顶层 `channels.matrix` 值会作为这些条目的默认值。
- `groups`：按房间划分的策略映射。优先使用房间 ID 或别名；未解析的房间名称会在运行时被忽略。会话/群组标识在解析后使用稳定的房间 ID，而人类可读标签仍来自房间名称。
- `groups.<room>.account`：在多账户设置中，将某个继承的房间条目限定到特定 Matrix 账户。
- `groups.<room>.allowBots`：针对已配置机器人发送者的房间级覆盖（`true` 或 `"mentions"`）。
- `groups.<room>.users`：按房间划分的发送者允许列表。
- `groups.<room>.tools`：按房间划分的工具允许/拒绝覆盖。
- `groups.<room>.autoReply`：房间级提及门控覆盖。`true` 会禁用该房间的提及要求；`false` 会强制重新开启。
- `groups.<room>.skills`：可选的房间级技能过滤器。
- `groups.<room>.systemPrompt`：可选的房间级系统提示片段。
- `rooms`：`groups` 的旧别名。
- `actions`：按操作划分的工具门控（`messages`、`reactions`、`pins`、`profile`、`memberInfo`、`channelInfo`、`verification`）。

## 相关内容

- [Channels Overview](/zh-CN/channels) — 所有支持的渠道
- [Pairing](/zh-CN/channels/pairing) — 私信认证和配对流程
- [Groups](/zh-CN/channels/groups) — 群聊行为和提及门控
- [Channel Routing](/zh-CN/channels/channel-routing) — 消息的会话路由
- [Security](/zh-CN/gateway/security) — 访问模型和加固
