---
read_when:
    - 你想在 OpenClaw 中使用由 Bedrock Mantle 托管的 OSS 模型
    - 你需要适用于 GPT-OSS、Qwen、Kimi 或 GLM 的 Mantle OpenAI 兼容端点
summary: 使用 Amazon Bedrock Mantle（兼容 OpenAI）模型与 OpenClaw 配合
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-06T00:47:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e5b33ede4067fb7de02a046f3e375cbd2af4bf68e7751c8dd687447f1a78c86
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw 内置了一个 **Amazon Bedrock Mantle** 提供商，可连接到 Mantle 的 OpenAI 兼容端点。Mantle 通过由 Bedrock 基础设施支持的标准 `/v1/chat/completions` 接口提供开源和第三方模型（GPT-OSS、Qwen、Kimi、GLM 及类似模型）。

## OpenClaw 支持的内容

- 提供商：`amazon-bedrock-mantle`
- API：`openai-completions`（兼容 OpenAI）
- 认证：显式 `AWS_BEARER_TOKEN_BEDROCK` 或通过 IAM 凭证链生成 bearer token
- 区域：`AWS_REGION` 或 `AWS_DEFAULT_REGION`（默认：`us-east-1`）

## 自动模型发现

设置 `AWS_BEARER_TOKEN_BEDROCK` 后，OpenClaw 会直接使用它。否则，OpenClaw 会尝试通过 AWS 默认凭证链生成 Mantle bearer token，其中包括共享凭证 / 配置 profile、SSO、web identity，以及实例或任务角色。然后，它会通过查询该区域的 `/v1/models` 端点来发现可用的 Mantle 模型。发现结果会缓存 1 小时，而基于 IAM 派生的 bearer token 会每小时刷新一次。

支持的区域：`us-east-1`、`us-east-2`、`us-west-2`、`ap-northeast-1`、`ap-south-1`、`ap-southeast-3`、`eu-central-1`、`eu-west-1`、`eu-west-2`、`eu-south-1`、`eu-north-1`、`sa-east-1`。

## 新手引导

1. 在 **gateway host** 上选择一种认证方式：

显式 bearer token：

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# 可选（默认为 us-east-1）：
export AWS_REGION="us-west-2"
```

IAM 凭证：

```bash
# 这里可使用任何兼容 AWS SDK 的认证来源，例如：
export AWS_PROFILE="default"
export AWS_REGION="us-west-2"
```

2. 验证模型已被发现：

```bash
openclaw models list
```

已发现的模型会显示在 `amazon-bedrock-mantle` 提供商下。除非你想覆盖默认值，否则不需要额外配置。

## 手动配置

如果你更倾向于使用显式配置而不是自动发现：

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## 注意事项

- 当未设置 `AWS_BEARER_TOKEN_BEDROCK` 时，OpenClaw 可以根据兼容 AWS SDK 的 IAM 凭证为你签发 Mantle bearer token。
- 这个 bearer token 与标准 [Amazon Bedrock](/zh-CN/providers/bedrock) 提供商使用的 `AWS_BEARER_TOKEN_BEDROCK` 相同。
- 对 reasoning 的支持会根据模型 ID 中是否包含 `thinking`、`reasoner` 或 `gpt-oss-120b` 等模式来推断。
- 如果 Mantle 端点不可用或未返回任何模型，则会静默跳过该提供商。
