---
read_when:
    - 你想将 Bedrock Mantle 托管的 OSS 模型与 OpenClaw 一起使用
    - 你需要用于 GPT-OSS、Qwen、Kimi 或 GLM 的 Mantle OpenAI 兼容端点
summary: 使用 Amazon Bedrock Mantle（兼容 OpenAI）模型与 OpenClaw
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-05T12:34:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2efe61261fbb430f63be9f5025c0654c44b191dbe96b3eb081d7ccbe78458907
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw 内置了一个 **Amazon Bedrock Mantle** 提供商，可连接到 Mantle 的 OpenAI 兼容端点。Mantle 通过由 Bedrock 基础设施支持的标准 `/v1/chat/completions` 接口托管开源和第三方模型（GPT-OSS、Qwen、Kimi、GLM 等类似模型）。

## OpenClaw 支持的内容

- 提供商：`amazon-bedrock-mantle`
- API：`openai-completions`（兼容 OpenAI）
- 认证：通过 `AWS_BEARER_TOKEN_BEDROCK` 提供 bearer token
- 区域：`AWS_REGION` 或 `AWS_DEFAULT_REGION`（默认：`us-east-1`）

## 自动模型发现

当设置了 `AWS_BEARER_TOKEN_BEDROCK` 后，OpenClaw 会通过查询该区域的 `/v1/models` 端点自动发现可用的 Mantle 模型。发现结果会缓存 1 小时。

支持的区域：`us-east-1`、`us-east-2`、`us-west-2`、`ap-northeast-1`、`ap-south-1`、`ap-southeast-3`、`eu-central-1`、`eu-west-1`、`eu-west-2`、`eu-south-1`、`eu-north-1`、`sa-east-1`。

## 新手引导

1. 在 **gateway host** 上设置 bearer token：

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# 可选（默认使用 us-east-1）：
export AWS_REGION="us-west-2"
```

2. 验证是否已发现模型：

```bash
openclaw models list
```

发现的模型会显示在 `amazon-bedrock-mantle` 提供商下。除非你想覆盖默认值，否则不需要额外配置。

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

## 说明

- Mantle 目前需要 bearer token。仅使用普通 IAM 凭证（实例角色、SSO、访问密钥）而不提供 token 是不够的。
- 这个 bearer token 与标准 [Amazon Bedrock](/zh-CN/providers/bedrock) 提供商使用的 `AWS_BEARER_TOKEN_BEDROCK` 相同。
- 是否支持推理会根据模型 ID 中是否包含诸如 `thinking`、`reasoner` 或 `gpt-oss-120b` 之类的模式来推断。
- 如果 Mantle 端点不可用或未返回任何模型，该提供商会被静默跳过。
