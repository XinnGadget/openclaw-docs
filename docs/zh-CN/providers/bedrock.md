---
read_when:
    - 你想在 OpenClaw 中使用 Amazon Bedrock 模型
    - 你需要为模型调用设置 AWS 凭证和区域
summary: 使用 Amazon Bedrock（Converse API）模型与 OpenClaw
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-05T12:34:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: a751824b679a9340db714ee5227e8d153f38f6c199ca900458a4ec092b4efe54
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw 可以通过 pi‑ai 的 **Bedrock Converse** 流式传输 provider 使用 **Amazon Bedrock** 模型。Bedrock 认证使用 **AWS SDK 默认凭证链**，而不是 API 密钥。

## pi-ai 支持的内容

- provider：`amazon-bedrock`
- API：`bedrock-converse-stream`
- 认证：AWS 凭证（环境变量、共享配置或实例角色）
- 区域：`AWS_REGION` 或 `AWS_DEFAULT_REGION`（默认：`us-east-1`）

## 自动模型发现

OpenClaw 可以自动发现支持**流式传输**和**文本输出**的 Bedrock 模型。发现过程使用 `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`，结果会被缓存（默认：1 小时）。

隐式 provider 的启用方式：

- 如果 `plugins.entries.amazon-bedrock.config.discovery.enabled` 为 `true`，OpenClaw 即使在没有 AWS 环境标记的情况下也会尝试发现。
- 如果 `plugins.entries.amazon-bedrock.config.discovery.enabled` 未设置，OpenClaw 只有在检测到以下 AWS 认证标记之一时，才会自动添加隐式 Bedrock provider：
  `AWS_BEARER_TOKEN_BEDROCK`、`AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY`，或 `AWS_PROFILE`。
- 实际的 Bedrock 运行时认证路径仍使用 AWS SDK 默认凭证链，因此即使发现流程需要通过 `enabled: true` 显式启用，共享配置、SSO 和 IMDS 实例角色认证仍然可以工作。

配置选项位于 `plugins.entries.amazon-bedrock.config.discovery` 下：

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          discovery: {
            enabled: true,
            region: "us-east-1",
            providerFilter: ["anthropic", "amazon"],
            refreshInterval: 3600,
            defaultContextWindow: 32000,
            defaultMaxTokens: 4096,
          },
        },
      },
    },
  },
}
```

说明：

- `enabled` 默认使用自动模式。在自动模式下，OpenClaw 只有在检测到受支持的 AWS 环境标记时，才会启用隐式 Bedrock provider。
- `region` 默认为 `AWS_REGION` 或 `AWS_DEFAULT_REGION`，然后回退到 `us-east-1`。
- `providerFilter` 匹配 Bedrock provider 名称（例如 `anthropic`）。
- `refreshInterval` 的单位为秒；设置为 `0` 可禁用缓存。
- `defaultContextWindow`（默认：`32000`）和 `defaultMaxTokens`（默认：`4096`）用于已发现的模型（如果你知道模型限制，可覆盖这些值）。
- 对于显式的 `models.providers["amazon-bedrock"]` 条目，OpenClaw 仍然可以从 AWS 环境标记（如 `AWS_BEARER_TOKEN_BEDROCK`）中提前解析 Bedrock 环境标记认证，而无需强制加载完整运行时认证。实际的模型调用认证路径仍使用 AWS SDK 默认凭证链。

## 新手引导

1. 确保 **Gateway 网关主机**上可用 AWS 凭证：

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# 可选：
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# 可选（Bedrock API 密钥 / bearer token）：
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. 向你的配置中添加一个 Bedrock provider 和模型（不需要 `apiKey`）：

```json5
{
  models: {
    providers: {
      "amazon-bedrock": {
        baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
        api: "bedrock-converse-stream",
        auth: "aws-sdk",
        models: [
          {
            id: "us.anthropic.claude-opus-4-6-v1:0",
            name: "Claude Opus 4.6（Bedrock）",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
    },
  },
}
```

## EC2 实例角色

当 OpenClaw 运行在附加了 IAM 角色的 EC2 实例上时，AWS SDK 可以使用实例元数据服务（IMDS）进行认证。对于 Bedrock 模型发现，除非你显式设置 `plugins.entries.amazon-bedrock.config.discovery.enabled: true`，否则 OpenClaw 只会通过 AWS 环境标记自动启用隐式 provider。

针对由 IMDS 支持的主机，推荐设置如下：

- 将 `plugins.entries.amazon-bedrock.config.discovery.enabled` 设置为 `true`。
- 设置 `plugins.entries.amazon-bedrock.config.discovery.region`（或导出 `AWS_REGION`）。
- **不**需要伪造 API 密钥。
- 只有在你特别希望为自动模式或状态显示提供环境标记时，才需要 `AWS_PROFILE=default`。

```bash
# 推荐：显式启用发现并设置区域
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 可选：如果你想在不显式启用的情况下使用自动模式，可添加一个环境标记
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

EC2 实例角色所需的 **IAM 权限**：

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels`（用于自动发现）
- `bedrock:ListInferenceProfiles`（用于推理配置文件发现）

或者附加托管策略 `AmazonBedrockFullAccess`。

## 快速设置（AWS 路径）

```bash
# 1. 创建 IAM 角色和实例配置文件
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. 附加到你的 EC2 实例
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. 在 EC2 实例上显式启用发现
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. 可选：如果你想在不显式启用的情况下使用自动模式，可添加一个环境标记
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. 验证模型是否已发现
openclaw models list
```

## 推理配置文件

OpenClaw 在发现基础模型的同时，也会发现**区域性和全局推理配置文件**。当某个配置文件映射到已知基础模型时，该配置文件会继承该模型的能力（上下文窗口、最大 token 数、推理、视觉），并会自动注入正确的 Bedrock 请求区域。这意味着跨区域 Claude 配置文件无需手动覆盖 provider 也能正常工作。

推理配置文件 ID 的形式可能是 `us.anthropic.claude-opus-4-6-v1:0`（区域性）或 `anthropic.claude-opus-4-6-v1:0`（全局）。如果其底层模型已包含在发现结果中，该配置文件会继承其完整能力集；否则会应用安全默认值。

无需额外配置。只要启用了发现并且 IAM 主体具有 `bedrock:ListInferenceProfiles` 权限，配置文件就会和基础模型一起显示在 `openclaw models list` 中。

## 说明

- Bedrock 要求你在 AWS 账户 / 区域中启用**模型访问权限**。
- 自动发现需要 `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles` 权限。
- 如果你依赖自动模式，请在 Gateway 网关主机上设置一个受支持的 AWS 认证环境标记。如果你更倾向于使用无环境标记的 IMDS / 共享配置认证，请设置 `plugins.entries.amazon-bedrock.config.discovery.enabled: true`。
- OpenClaw 按以下顺序显示凭证来源：`AWS_BEARER_TOKEN_BEDROCK`，然后是 `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`，然后是 `AWS_PROFILE`，最后是默认 AWS SDK 凭证链。
- 推理支持取决于具体模型；请查看 Bedrock 模型卡以了解当前能力。
- 如果你更喜欢托管密钥流程，也可以在 Bedrock 前面放置一个兼容 OpenAI 的代理，并将其作为 OpenAI provider 进行配置。

## Guardrails

你可以通过在 `amazon-bedrock` 插件配置中添加一个 `guardrail` 对象，将 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 应用于所有 Bedrock 模型调用。Guardrails 可让你强制执行内容过滤、主题拒绝、词语过滤、敏感信息过滤和上下文基础校验。

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          guardrail: {
            guardrailIdentifier: "abc123", // guardrail ID or full ARN
            guardrailVersion: "1", // version number or "DRAFT"
            streamProcessingMode: "sync", // optional: "sync" or "async"
            trace: "enabled", // optional: "enabled", "disabled", or "enabled_full"
          },
        },
      },
    },
  },
}
```

- `guardrailIdentifier`（必填）接受 guardrail ID（例如 `abc123`）或完整 ARN（例如 `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`）。
- `guardrailVersion`（必填）指定要使用的已发布版本，或使用 `"DRAFT"` 表示工作草稿。
- `streamProcessingMode`（可选）控制在流式传输期间，guardrail 评估是同步运行（`"sync"`）还是异步运行（`"async"`）。如果省略，Bedrock 将使用其默认行为。
- `trace`（可选）在 API 响应中启用 guardrail 跟踪输出。调试时设置为 `"enabled"` 或 `"enabled_full"`；生产环境中省略或设置为 `"disabled"`。

Gateway 网关使用的 IAM 主体除标准调用权限外，还必须具有 `bedrock:ApplyGuardrail` 权限。
