---
read_when:
    - 在 Hostinger 上设置 OpenClaw
    - 正在寻找适用于 OpenClaw 的托管 VPS
    - 使用 Hostinger 一键安装 OpenClaw
summary: 在 Hostinger 上托管 OpenClaw
title: Hostinger
x-i18n:
    generated_at: "2026-04-13T13:14:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

通过 **一键安装** 托管部署或 **VPS** 安装，在 [Hostinger](https://www.hostinger.com/openclaw) 上运行持久化的 OpenClaw Gateway 网关。

## 前提条件

- Hostinger 账户（[注册](https://www.hostinger.com/openclaw)）
- 大约 5-10 分钟

## 选项 A：一键安装 OpenClaw

最快的入门方式。Hostinger 会处理基础设施、Docker 和自动更新。

<Steps>
  <Step title="购买并启动">
    1. 在 [Hostinger OpenClaw 页面](https://www.hostinger.com/openclaw) 上，选择一个托管 OpenClaw 套餐并完成结账。

    <Note>
    在结账过程中，你可以选择 **Ready-to-Use AI** 积分，这些积分已预先购买，并会立即在 OpenClaw 内集成——无需其他提供商的外部账户或 API 密钥。你可以立刻开始聊天。或者，你也可以在设置过程中提供你自己的 Anthropic、OpenAI、Google Gemini 或 xAI 密钥。
    </Note>

  </Step>

  <Step title="选择一个消息渠道">
    选择一个或多个要连接的渠道：

    - **WhatsApp** —— 扫描设置向导中显示的二维码。
    - **Telegram** —— 粘贴来自 [BotFather](https://t.me/BotFather) 的机器人令牌。

  </Step>

  <Step title="完成安装">
    点击 **Finish** 以部署实例。准备就绪后，可从 hPanel 中的 **OpenClaw Overview** 访问 OpenClaw 仪表板。
  </Step>

</Steps>

## 选项 B：在 VPS 上运行 OpenClaw

对你的服务器拥有更多控制权。Hostinger 会通过 Docker 在你的 VPS 上部署 OpenClaw，而你可通过 hPanel 中的 **Docker Manager** 进行管理。

<Steps>
  <Step title="购买 VPS">
    1. 在 [Hostinger OpenClaw 页面](https://www.hostinger.com/openclaw) 上，选择一个 OpenClaw on VPS 套餐并完成结账。

    <Note>
    你可以在结账过程中选择 **Ready-to-Use AI** 积分——这些积分已预先购买，并会立即在 OpenClaw 内集成，因此你无需任何外部账户或其他提供商的 API 密钥即可开始聊天。
    </Note>

  </Step>

  <Step title="配置 OpenClaw">
    VPS 配置完成后，填写以下配置字段：

    - **Gateway token** —— 自动生成；请保存以便后续使用。
    - **WhatsApp number** —— 带国家区号的你的号码（可选）。
    - **Telegram bot token** —— 来自 [BotFather](https://t.me/BotFather)（可选）。
    - **API keys** —— 仅当你在结账时未选择 Ready-to-Use AI 积分时才需要。

  </Step>

  <Step title="启动 OpenClaw">
    点击 **Deploy**。运行后，在 hPanel 中点击 **Open** 打开 OpenClaw 仪表板。
  </Step>

</Steps>

日志、重启和更新均可直接在 hPanel 的 Docker Manager 界面中管理。要更新，请在 Docker Manager 中点击 **Update**，这将拉取最新镜像。

## 验证你的设置

在你已连接的渠道中向你的助手发送“Hi”。OpenClaw 会回复你，并引导你完成初始偏好设置。

## 故障排除

**仪表板无法加载** —— 等待几分钟，让容器完成配置。检查 hPanel 中 Docker Manager 的日志。

**Docker 容器持续重启** —— 打开 Docker Manager 日志，查看是否存在配置错误（缺少令牌、API 密钥无效）。

**Telegram 机器人没有响应** —— 直接通过 Telegram 将你的配对代码消息发送到 OpenClaw 聊天中，以完成连接。

## 后续步骤

- [渠道](/zh-CN/channels) —— 连接 Telegram、WhatsApp、Discord 等
- [Gateway 网关配置](/zh-CN/gateway/configuration) —— 所有配置选项
