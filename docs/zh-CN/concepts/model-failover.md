---
read_when:
    - 诊断凭证配置文件轮换、冷却时间或模型回退行为
    - 更新凭证配置文件或模型的故障切换规则
    - 了解会话模型覆盖如何与回退重试交互
summary: OpenClaw 如何轮换凭证配置文件，并在模型之间执行回退
title: 模型故障切换
x-i18n:
    generated_at: "2026-04-06T15:28:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: d88821e229610f236bdab3f798d5e8c173f61a77c01017cc87431126bf465e32
    source_path: concepts/model-failover.md
    workflow: 15
---

# 模型故障切换

OpenClaw 分两个阶段处理失败：

1. 当前提供商内的**凭证配置文件轮换**。
2. 回退到 `agents.defaults.model.fallbacks` 中的下一个模型，即**模型回退**。

本文档说明支撑这些行为的运行时规则和数据。

## 运行时流程

对于一次普通的文本运行，OpenClaw 会按以下顺序评估候选项：

1. 当前选中的会话模型。
2. 按顺序配置的 `agents.defaults.model.fallbacks`。
3. 如果本次运行起始于某个覆盖设置，则最后再使用已配置的主模型。

在每个候选项内部，OpenClaw 会先尝试凭证配置文件故障切换，再进入
下一个模型候选项。

高级别流程如下：

1. 解析当前激活的会话模型和凭证配置文件偏好。
2. 构建模型候选链。
3. 按照凭证配置文件轮换 / 冷却规则尝试当前提供商。
4. 如果该提供商因值得故障切换的错误而耗尽可用项，则移动到下一个
   模型候选项。
5. 在重试开始前持久化选中的回退覆盖，这样其他会话读取方会看到运行器即将使用的同一提供商 / 模型。
6. 如果回退候选项失败，则仅回滚那些由回退拥有的会话覆盖字段，并且仅当它们仍匹配该失败候选项时才回滚。
7. 如果所有候选项都失败，则抛出带有每次尝试详情及最早冷却到期时间（如果已知）的 `FallbackSummaryError`。

这刻意比“保存并恢复整个会话”更窄。回复运行器只会持久化它为回退所拥有的模型选择字段：

- `providerOverride`
- `modelOverride`
- `authProfileOverride`
- `authProfileOverrideSource`
- `authProfileOverrideCompactionCount`

这样可以防止一次失败的回退重试覆盖更新较新的、无关的会话变更，
例如手动 `/model` 更改或在尝试运行期间发生的会话轮换更新。

## 凭证存储（密钥 + OAuth）

OpenClaw 对 API 密钥和 OAuth 令牌都使用**凭证配置文件**。

- 密钥存储在 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`（旧版：`~/.openclaw/agent/auth-profiles.json`）。
- 运行时凭证路由状态存储在 `~/.openclaw/agents/<agentId>/agent/auth-state.json`。
- 配置 `auth.profiles` / `auth.order` **仅用于元数据 + 路由**（不存储密钥）。
- 仅用于旧版导入的 OAuth 文件：`~/.openclaw/credentials/oauth.json`（首次使用时会导入到 `auth-profiles.json`）。

更多细节：[/concepts/oauth](/zh-CN/concepts/oauth)

凭证类型：

- `type: "api_key"` → `{ provider, key }`
- `type: "oauth"` → `{ provider, access, refresh, expires, email? }`（某些提供商还会包含 `projectId` / `enterpriseUrl`）

## 配置文件 ID

OAuth 登录会创建不同的配置文件，以便多个账户可以共存。

- 默认值：当没有可用邮箱时为 `provider:default`。
- 带邮箱的 OAuth：`provider:<email>`（例如 `google-antigravity:user@gmail.com`）。

配置文件位于 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 的 `profiles` 下。

## 轮换顺序

当一个提供商有多个配置文件时，OpenClaw 会按如下方式决定顺序：

1. **显式配置**：`auth.order[provider]`（如果已设置）。
2. **已配置的配置文件**：按提供商过滤后的 `auth.profiles`。
3. **已存储的配置文件**：`auth-profiles.json` 中该提供商对应的条目。

如果没有配置显式顺序，OpenClaw 会使用轮询顺序：

- **主排序键：** 配置文件类型（**OAuth 优先于 API 密钥**）。
- **次排序键：** `usageStats.lastUsed`（越久未使用越靠前，同类型内排序）。
- **处于冷却 / 已禁用的配置文件** 会被移到末尾，并按最早到期时间排序。

### 会话粘性（对缓存更友好）

OpenClaw 会**为每个会话固定所选的凭证配置文件**，以保持提供商缓存处于预热状态。
它**不会**在每次请求时轮换。固定的配置文件会被重复使用，直到：

- 会话被重置（`/new` / `/reset`）
- 一次压缩完成（压缩计数增加）
- 该配置文件处于冷却 / 已禁用状态

通过 `/model …@<profileId>` 进行手动选择会为该会话设置一个**用户覆盖**，
在新会话开始前不会自动轮换。

自动固定的配置文件（由会话路由器选中）被视为一种**偏好**：
它们会被优先尝试，但 OpenClaw 可能会在遇到速率限制 / 超时时轮换到其他配置文件。
用户固定的配置文件会保持锁定在该配置文件；如果它失败且已配置模型回退，
OpenClaw 会移动到下一个模型，而不是切换配置文件。

### 为什么 OAuth 可能“看起来丢了”

如果你对同一个提供商同时拥有一个 OAuth 配置文件和一个 API 密钥配置文件，在未固定时，轮询可能会在不同消息之间切换它们。若要强制使用单一配置文件：

- 使用 `auth.order[provider] = ["provider:profileId"]` 固定，或
- 通过 `/model …` 使用带配置文件覆盖的按会话覆盖（当你的 UI / 聊天界面支持时）。

## 冷却时间

当某个配置文件因凭证 / 速率限制错误（或看起来像速率限制的超时）
而失败时，OpenClaw 会将其标记为冷却中，并切换到下一个配置文件。
这个速率限制分类比单纯的 `429` 更宽：它还包括提供商消息，
例如 `Too many concurrent requests`、`ThrottlingException`、
`concurrency limit reached`、`workers_ai ... quota limit exceeded`、
`throttled`、`resource exhausted`，以及周期性使用窗口限制，
例如 `weekly/monthly limit reached`。
格式 / 无效请求错误（例如 Cloud Code Assist 工具调用 ID
校验失败）也会被视为值得故障切换，并使用相同的冷却时间。
OpenAI 兼容的停止原因错误，例如 `Unhandled stop reason: error`、
`stop reason: error` 和 `reason: error`，会被归类为超时 / 故障切换
信号。
当来源匹配已知瞬态模式时，提供商范围的通用服务器文本也会归入该超时分类。
例如，Anthropic 的裸文本
`An unknown error occurred` 以及带有瞬态服务器文本的 JSON `api_error`
载荷，例如 `internal server error`、`unknown error, 520`、`upstream error`
或 `backend error`，都会被视为值得故障切换的超时。
OpenRouter 特有的通用上游文本，例如裸文本 `Provider returned error`，
只有在提供商上下文确实是 OpenRouter 时才会被视为超时。
通用的内部回退文本，例如 `LLM request failed with an unknown error.`，
则保持保守，不会单独触发故障切换。

速率限制冷却也可以按模型划分范围：

- 当已知失败的模型 ID 时，OpenClaw 会为速率限制失败记录 `cooldownModel`。
- 当冷却限定在不同模型上时，同一提供商上的兄弟模型仍可被尝试。
- 计费 / 已禁用窗口仍会在所有模型上阻止整个配置文件。

冷却时间使用指数退避：

- 1 分钟
- 5 分钟
- 25 分钟
- 1 小时（上限）

状态存储在 `auth-state.json` 的 `usageStats` 下：

```json
{
  "usageStats": {
    "provider:profile": {
      "lastUsed": 1736160000000,
      "cooldownUntil": 1736160600000,
      "errorCount": 2
    }
  }
}
```

## 计费禁用

计费 / 额度失败（例如“insufficient credits” / “credit balance too low”）会被视为值得故障切换，但它们通常不是瞬态错误。OpenClaw 不会设置短暂冷却，而是会将该配置文件标记为**已禁用**（使用更长的退避时间），并轮换到下一个配置文件 / 提供商。

并非每个看起来像计费问题的响应都是 `402`，也并非每个 HTTP `402`
都会归入这里。即使提供商返回的是 `401` 或 `403`，OpenClaw 仍会将明确的计费文本保留在计费分类中，但提供商特定匹配器仍仅限于拥有它们的提供商（例如 OpenRouter 的 `403 Key limit exceeded`）。
与此同时，临时性的 `402` 使用窗口和组织 / 工作区支出限制错误，如果消息看起来可重试（例如 `weekly usage limit exhausted`、`daily limit reached, resets tomorrow` 或 `organization spending limit exceeded`），则会被归类为 `rate_limit`。
这些情况会继续走短冷却 / 故障切换路径，而不是长时间的
计费禁用途径。

状态存储在 `auth-state.json` 中：

```json
{
  "usageStats": {
    "provider:profile": {
      "disabledUntil": 1736178000000,
      "disabledReason": "billing"
    }
  }
}
```

默认值：

- 计费退避从 **5 小时**开始，每次计费失败后翻倍，并在 **24 小时**封顶。
- 如果配置文件在 **24 小时**内未再失败，退避计数器会重置（可配置）。
- 过载重试在模型回退前允许进行 **1 次同提供商配置文件轮换**。
- 过载重试默认使用 **0 毫秒退避**。

## 模型回退

如果某个提供商的所有配置文件都失败，OpenClaw 会移动到
`agents.defaults.model.fallbacks` 中的下一个模型。这适用于凭证失败、速率限制，以及耗尽配置文件轮换后的超时（其他错误不会推进回退）。

过载和速率限制错误的处理比计费冷却更激进。默认情况下，
OpenClaw 允许一次同提供商凭证配置文件重试，然后立即切换到下一个已配置的模型回退，无需等待。
提供商繁忙信号，例如 `ModelNotReadyException`，会归入该过载分类。
你可以使用 `auth.cooldowns.overloadedProfileRotations`、
`auth.cooldowns.overloadedBackoffMs` 和
`auth.cooldowns.rateLimitedProfileRotations` 进行调整。

当一次运行以模型覆盖开始时（hooks 或 CLI），在尝试完任何已配置回退后，
回退仍会以 `agents.defaults.model.primary` 结束。

### 候选链规则

OpenClaw 会根据当前请求的 `provider/model` 与已配置回退构建候选列表。

规则：

- 请求的模型始终排在第一位。
- 显式配置的回退会去重，但不会按模型允许列表过滤。它们被视为运维方的显式意图。
- 如果当前运行已经在同一提供商家族中的某个已配置回退上，OpenClaw 会继续使用完整的已配置链。
- 如果当前运行所在的提供商与配置不同，并且该当前模型尚未包含在已配置回退链中，OpenClaw 不会附加来自其他提供商的无关已配置回退。
- 当运行起始于某个覆盖设置时，已配置的主模型会附加到末尾，这样在较早候选项耗尽后，候选链可以回到正常默认值。

### 哪些错误会推进回退

模型回退会在以下情况继续：

- 凭证失败
- 速率限制和冷却耗尽
- 过载 / 提供商繁忙错误
- 类超时的故障切换错误
- 计费禁用
- `LiveSessionModelSwitchError`，它会被规范化为故障切换路径，这样过时的持久化模型就不会形成外层重试循环
- 当仍有剩余候选项时，其他无法识别的错误

模型回退不会在以下情况继续：

- 不属于超时 / 故障切换形态的显式中止
- 应保留在压缩 / 重试逻辑内部的上下文溢出错误
  （例如 `request_too_large`、`INVALID_ARGUMENT: input exceeds the maximum
number of tokens`、`input token count exceeds the maximum number of input
tokens`、`The input is too long for the model` 或 `ollama error: context
length exceeded`）
- 当没有候选项剩余时的最终未知错误

### 冷却跳过与探测行为

当某个提供商的所有凭证配置文件都已经处于冷却中时，OpenClaw 不会自动永久跳过该提供商。它会针对每个候选项单独决策：

- 持续性的凭证失败会立即跳过整个提供商。
- 计费禁用通常会跳过，但主候选项仍可能在节流条件下被探测，以便无需重启也能恢复。
- 在接近冷却到期时，主候选项可能会被探测，并带有按提供商区分的节流限制。
- 即使存在冷却，同提供商的回退兄弟项在失败看起来是瞬态时（`rate_limit`、`overloaded` 或未知）仍可被尝试。当速率限制是模型范围时，而兄弟模型可能仍可立即恢复，这一点尤其重要。
- 瞬态冷却探测在每次回退运行中每个提供商最多仅允许一次，因此单个提供商不会拖慢跨提供商回退。

## 会话覆盖与实时模型切换

会话模型更改属于共享状态。活动运行器、`/model` 命令、
压缩 / 会话更新，以及实时会话协调逻辑都会读取或写入同一个会话条目的不同部分。

这意味着回退重试必须与实时模型切换协调：

- 只有显式的用户驱动模型更改才会标记待处理的实时切换。这包括 `/model`、`session_status(model=...)` 和 `sessions.patch`。
- 由系统驱动的模型更改，例如回退轮换、心跳覆盖或压缩，不会自行标记待处理的实时切换。
- 在回退重试开始前，回复运行器会将选中的回退覆盖字段持久化到会话条目中。
- 实时会话协调会优先使用持久化的会话覆盖，而不是过时的运行时模型字段。
- 如果回退尝试失败，运行器只会回滚它写入的覆盖字段，并且仅当这些字段仍匹配该失败候选项时才会回滚。

这可以防止经典竞争条件：

1. 主模型失败。
2. 回退候选项在内存中被选中。
3. 会话存储仍显示旧的主模型。
4. 实时会话协调读取了过时的会话状态。
5. 在回退尝试开始前，重试又被拉回旧模型。

持久化的回退覆盖封住了这个窗口，而范围收窄的回滚则能保持更新的手动或运行时会话更改不受影响。

## 可观测性与失败摘要

`runWithModelFallback(...)` 会记录每次尝试的详细信息，以供日志记录和面向用户的冷却消息使用：

- 尝试过的提供商 / 模型
- 原因（`rate_limit`、`overloaded`、`billing`、`auth`、`model_not_found` 以及类似的故障切换原因）
- 可选的状态 / 代码
- 人类可读的错误摘要

当所有候选项都失败时，OpenClaw 会抛出 `FallbackSummaryError`。外层回复运行器可以据此构建更具体的消息，例如“所有模型当前都受到临时速率限制”，并在已知时包含最早的冷却到期时间。

该冷却摘要是模型感知的：

- 对于已尝试的提供商 / 模型链，无关的模型范围速率限制会被忽略
- 如果剩余阻塞是匹配的模型范围速率限制，OpenClaw 会报告仍阻止该模型的最后一个匹配到期时间

## 相关配置

有关以下内容，请参见 [Gateway 网关配置](/zh-CN/gateway/configuration)：

- `auth.profiles` / `auth.order`
- `auth.cooldowns.billingBackoffHours` / `auth.cooldowns.billingBackoffHoursByProvider`
- `auth.cooldowns.billingMaxHours` / `auth.cooldowns.failureWindowHours`
- `auth.cooldowns.overloadedProfileRotations` / `auth.cooldowns.overloadedBackoffMs`
- `auth.cooldowns.rateLimitedProfileRotations`
- `agents.defaults.model.primary` / `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel` 路由

有关更广泛的模型选择与回退概览，请参见 [模型](/zh-CN/concepts/models)。
