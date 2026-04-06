---
read_when:
    - 配对或重新连接 iOS 节点时
    - 从源码运行 iOS 应用时
    - 调试 Gateway 网关发现或 canvas 命令时
summary: iOS 节点应用：连接到 Gateway 网关、配对、canvas 和故障排除
title: iOS 应用
x-i18n:
    generated_at: "2026-04-06T15:29:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3e0a6e33e72d4c9f1f17ef70a1b67bae9ebe4a2dca16677ea6b28d0ddac1b4e
    source_path: platforms/ios.md
    workflow: 15
---

# iOS 应用（节点）

可用性：内部预览。iOS 应用尚未公开发布。

## 它的作用

- 通过 WebSocket 连接到 Gateway 网关（LAN 或 tailnet）。
- 提供节点能力：Canvas、屏幕快照、相机采集、位置、对讲模式、语音唤醒。
- 接收 `node.invoke` 命令并上报节点状态事件。

## 要求

- Gateway 网关运行在另一台设备上（macOS、Linux，或通过 WSL2 运行的 Windows）。
- 网络路径：
  - 通过 Bonjour 处于同一 LAN，**或**
  - 通过 tailnet 使用单播 DNS-SD（示例域名：`openclaw.internal.`），**或**
  - 手动输入主机/端口（回退方案）。

## 快速开始（配对 + 连接）

1. 启动 Gateway 网关：

```bash
openclaw gateway --port 18789
```

2. 在 iOS 应用中，打开 Settings 并选择一个已发现的 Gateway 网关（或者启用 Manual Host 并输入主机/端口）。

3. 在 Gateway 网关主机上批准配对请求：

```bash
openclaw devices list
openclaw devices approve <requestId>
```

如果应用在认证详情（角色/scopes/公钥）变更后重试配对，
之前待处理的请求会被新请求取代，并创建新的 `requestId`。
请在批准前再次运行 `openclaw devices list`。

4. 验证连接：

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## 官方构建使用基于 relay 的推送

官方发布的 iOS 构建会使用外部推送 relay，而不是将原始 APNs
token 直接发布到 Gateway 网关。

Gateway 网关侧要求：

```json5
{
  gateway: {
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
        },
      },
    },
  },
}
```

流程工作方式：

- iOS 应用使用 App Attest 和应用收据向 relay 注册。
- relay 返回一个不透明的 relay handle 以及一个按注册范围授予的发送许可。
- iOS 应用会获取已配对 Gateway 网关的身份，并将其包含在 relay 注册中，因此这个基于 relay 的注册会委托给该特定 Gateway 网关。
- 应用通过 `push.apns.register` 将该基于 relay 的注册转发给已配对的 Gateway 网关。
- Gateway 网关将使用这个已存储的 relay handle 来执行 `push.test`、后台唤醒和唤醒提示。
- Gateway 网关的 relay 基础 URL 必须与官方/TestFlight iOS 构建中固化的 relay URL 一致。
- 如果应用之后连接到不同的 Gateway 网关，或者连接到使用不同 relay 基础 URL 的构建，它会刷新 relay 注册，而不是复用旧绑定。

对于这一路径，Gateway 网关**不**需要：

- 不需要全局部署级 relay token。
- 对于官方/TestFlight 的 relay 转发发送，不需要直接 APNs key。

预期的操作流程：

1. 安装官方/TestFlight iOS 构建。
2. 在 Gateway 网关上设置 `gateway.push.apns.relay.baseUrl`。
3. 将应用与 Gateway 网关配对，并让它完成连接。
4. 当应用已经拿到 APNs token、operator 会话已连接且 relay 注册成功后，它会自动发布 `push.apns.register`。
5. 之后，`push.test`、重连唤醒和唤醒提示就可以使用这个已存储的基于 relay 的注册。

兼容性说明：

- `OPENCLAW_APNS_RELAY_BASE_URL` 仍可作为 Gateway 网关的临时环境变量覆盖项使用。

## 认证与信任流程

之所以引入 relay，是为了强制执行两个“在官方 iOS 构建上直接由 Gateway 网关连接 APNs 无法提供”的约束：

- 只有通过 Apple 分发的真实 OpenClaw iOS 构建才能使用托管 relay。
- Gateway 网关只能为与该特定 Gateway 网关配对过的 iOS 设备发送基于 relay 的推送。

逐跳说明：

1. `iOS app -> gateway`
   - 应用首先通过正常的 Gateway 网关认证流程与 Gateway 网关配对。
   - 这会给应用一个已认证的节点会话以及一个已认证的 operator 会话。
   - operator 会话用于调用 `gateway.identity.get`。

2. `iOS app -> relay`
   - 应用通过 HTTPS 调用 relay 注册端点。
   - 注册内容包括 App Attest 证明和应用收据。
   - relay 会验证 bundle ID、App Attest 证明和 Apple 收据，并要求使用官方/生产分发路径。
   - 这就是为什么本地 Xcode/dev 构建无法使用托管 relay。虽然本地构建可以签名，但它不满足 relay 所要求的官方 Apple 分发证明。

3. `gateway identity delegation`
   - 在 relay 注册前，应用会通过 `gateway.identity.get` 获取已配对 Gateway 网关的身份。
   - 应用会将这个 Gateway 网关身份包含到 relay 注册负载中。
   - relay 返回一个 relay handle 和一个按注册范围授予的发送许可，这些都被委托给该 Gateway 网关身份。

4. `gateway -> relay`
   - Gateway 网关会存储来自 `push.apns.register` 的 relay handle 和发送许可。
   - 在执行 `push.test`、重连唤醒和唤醒提示时，Gateway 网关会使用它自己的设备身份对发送请求签名。
   - relay 会依据注册时委托的 Gateway 网关身份，同时验证已存储的发送许可和 Gateway 网关签名。
   - 即使其他 Gateway 网关设法拿到了这个 handle，也不能复用该已存储注册。

5. `relay -> APNs`
   - relay 持有生产 APNs 凭证以及官方构建的原始 APNs token。
   - 对于基于 relay 的官方构建，Gateway 网关永远不会存储原始 APNs token。
   - relay 代表已配对的 Gateway 网关向 APNs 发送最终推送。

为什么要这样设计：

- 让生产 APNs 凭证不落到用户 Gateway 网关上。
- 避免在 Gateway 网关上存储官方构建的原始 APNs token。
- 仅允许官方/TestFlight OpenClaw 构建使用托管 relay。
- 防止某个 Gateway 网关向属于另一个 Gateway 网关的 iOS 设备发送唤醒推送。

本地/手动构建仍然使用直连 APNs。如果你在不使用 relay 的情况下测试这些构建，
Gateway 网关仍然需要直连 APNs 凭证：

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

这些是 Gateway 网关主机运行时环境变量，不是 Fastlane 设置。`apps/ios/fastlane/.env` 只存储
App Store Connect / TestFlight 认证信息，例如 `ASC_KEY_ID` 和 `ASC_ISSUER_ID`；它不会为本地 iOS 构建配置
直连 APNs 投递。

推荐的 Gateway 网关主机存储方式：

```bash
mkdir -p ~/.openclaw/credentials/apns
chmod 700 ~/.openclaw/credentials/apns
mv /path/to/AuthKey_KEYID.p8 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
chmod 600 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
export OPENCLAW_APNS_PRIVATE_KEY_PATH="$HOME/.openclaw/credentials/apns/AuthKey_KEYID.p8"
```

不要提交 `.p8` 文件，也不要将它放在仓库检出目录下。

## 发现路径

### Bonjour（LAN）

iOS 应用会在 `local.` 上浏览 `_openclaw-gw._tcp`，并在已配置时浏览同一个
广域 DNS-SD 发现域。同一 LAN 上的 Gateway 网关会通过 `local.` 自动出现；
跨网络发现则可以使用已配置的广域域名，而无需更改 beacon 类型。

### Tailnet（跨网络）

如果 mDNS 被阻止，请使用单播 DNS-SD 区域（选择一个域名；例如：
`openclaw.internal.`）和 Tailscale split DNS。
CoreDNS 示例请参见 [Bonjour](/zh-CN/gateway/bonjour)。

### 手动主机/端口

在 Settings 中启用 **Manual Host**，然后输入 Gateway 网关主机 + 端口（默认 `18789`）。

## Canvas + A2UI

iOS 节点会渲染一个 WKWebView canvas。使用 `node.invoke` 来驱动它：

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

说明：

- Gateway 网关 canvas host 提供 `/__openclaw__/canvas/` 和 `/__openclaw__/a2ui/`。
- 它由 Gateway 网关 HTTP 服务器提供（与 `gateway.port` 使用同一个端口，默认 `18789`）。
- 当广播了 canvas host URL 时，iOS 节点会在连接后自动跳转到 A2UI。
- 使用 `canvas.navigate` 和 `{"url":""}` 可返回内置脚手架。

### Canvas eval / snapshot

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## 语音唤醒 + 对讲模式

- 语音唤醒和对讲模式可在 Settings 中启用。
- iOS 可能会暂停后台音频；当应用不处于活动状态时，语音功能应视为尽力而为。

## 常见错误

- `NODE_BACKGROUND_UNAVAILABLE`：请将 iOS 应用切到前台（canvas/相机/屏幕命令需要前台状态）。
- `A2UI_HOST_NOT_CONFIGURED`：Gateway 网关没有广播 canvas host URL；请检查 [Gateway 配置](/zh-CN/gateway/configuration) 中的 `canvasHost`。
- 配对提示始终不出现：运行 `openclaw devices list` 并手动批准。
- 重装后重连失败：Keychain 配对 token 已被清除；请重新配对节点。

## 相关文档

- [配对](/zh-CN/channels/pairing)
- [设备发现](/zh-CN/gateway/discovery)
- [Bonjour](/zh-CN/gateway/bonjour)
