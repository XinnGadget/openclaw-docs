---
read_when:
    - 你想在 OpenClaw 中使用 Amazon Bedrock 模型
    - 你需要先设置 AWS 凭证和区域，才能发起模型调用
summary: 使用 OpenClaw 搭配 Amazon Bedrock（Converse API）模型
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-12T10:03:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88e7e24907ec26af098b648e2eeca32add090a9e381c818693169ab80aeccc47
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw 可以通过 pi-ai 的 **Bedrock Converse** 流式 provider 使用 **Amazon Bedrock** 模型。Bedrock 身份验证使用 **AWS SDK 默认凭证链**，而不是 API key。

| 属性 | 值 |
| -------- | ----------------------------------------------------------- |
| 提供商 | `amazon-bedrock` |
| API | `bedrock-converse-stream` |
| 身份验证 | AWS 凭证（环境变量、共享配置或实例角色） |
| 区域 | `AWS_REGION` 或 `AWS_DEFAULT_REGION`（默认：`us-east-1`） |

## 入门指南

选择你偏好的身份验证方式，并按照设置步骤进行操作。

<Tabs>
  <Tab title="访问密钥 / 环境变量">
    **最适合：** 直接管理 AWS 凭证的开发机器、CI 或主机。

    <Steps>
      <Step title="在 Gateway 网关主机上设置 AWS 凭证">
        ```bash
        export AWS_ACCESS_KEY_ID="AKIA..."
        export AWS_SECRET_ACCESS_KEY="..."
        export AWS_REGION="us-east-1"
        # 可选：
        export AWS_SESSION_TOKEN="..."
        export AWS_PROFILE="your-profile"
        # 可选（Bedrock API key / bearer token）：
        export AWS_BEARER_TOKEN_BEDROCK="..."
        ```
      </Step>
      <Step title="将 Bedrock provider 和模型添加到你的配置中">
        不需要 `apiKey`。请使用 `auth: "aws-sdk"` 配置该 provider：

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
                    name: "Claude Opus 4.6 (Bedrock)",
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
      </Step>
      <Step title="验证模型可用">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Tip>
    使用环境变量标记身份验证（`AWS_ACCESS_KEY_ID`、`AWS_PROFILE` 或 `AWS_BEARER_TOKEN_BEDROCK`）时，OpenClaw 会自动启用隐式 Bedrock provider 以进行模型发现，无需额外配置。
    </Tip>

  </Tab>

  <Tab title="EC2 实例角色（IMDS）">
    **最适合：** 附加了 IAM 角色、并使用实例元数据服务进行身份验证的 EC2 实例。

    <Steps>
      <Step title="显式启用发现">
        使用 IMDS 时，OpenClaw 无法仅通过环境变量标记检测 AWS 身份验证，因此你必须手动启用：

        ```bash
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
        openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1
        ```
      </Step>
      <Step title="可选：添加环境变量标记以启用自动模式">
        如果你还希望基于环境变量标记的自动检测路径生效（例如用于 `openclaw status` 相关界面）：

        ```bash
        export AWS_PROFILE=default
        export AWS_REGION=us-east-1
        ```

        你**不**需要伪造的 API key。
      </Step>
      <Step title="验证模型已被发现">
        ```bash
        openclaw models list
        ```
      </Step>
    </Steps>

    <Warning>
    附加到你的 EC2 实例的 IAM 角色必须具有以下权限：

    - `bedrock:InvokeModel`
    - `bedrock:InvokeModelWithResponseStream`
    - `bedrock:ListFoundationModels`（用于自动发现）
    - `bedrock:ListInferenceProfiles`（用于推理配置文件发现）

    或者附加托管策略 `AmazonBedrockFullAccess`。
    </Warning>

    <Note>
    只有在你明确希望为自动模式或状态界面提供环境变量标记时，才需要设置 `AWS_PROFILE=default`。实际的 Bedrock 运行时身份验证路径使用 AWS SDK 默认链，因此即使没有环境变量标记，IMDS 实例角色身份验证也能工作。
    </Note>

  </Tab>
</Tabs>

## 自动模型发现

OpenClaw 可以自动发现支持 **流式传输** 和 **文本输出** 的 Bedrock 模型。发现过程使用 `bedrock:ListFoundationModels` 和 `bedrock:ListInferenceProfiles`，结果会被缓存（默认：1 小时）。

隐式 provider 的启用方式如下：

- 如果 `plugins.entries.amazon-bedrock.config.discovery.enabled` 为 `true`，即使不存在 AWS 环境变量标记，OpenClaw 也会尝试执行发现。
- 如果 `plugins.entries.amazon-bedrock.config.discovery.enabled` 未设置，OpenClaw 只有在检测到以下 AWS 身份验证标记之一时，才会自动添加隐式 Bedrock provider：`AWS_BEARER_TOKEN_BEDROCK`、`AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`，或 `AWS_PROFILE`。
- 实际的 Bedrock 运行时身份验证路径仍然使用 AWS SDK 默认链，因此即使发现过程需要通过 `enabled: true` 手动启用，共享配置、SSO 和 IMDS 实例角色身份验证仍然可以正常工作。

<Note>
对于显式 `models.providers["amazon-bedrock"]` 条目，OpenClaw 仍然可以从 AWS 环境变量标记（例如 `AWS_BEARER_TOKEN_BEDROCK`）中提前解析 Bedrock 环境变量标记身份验证，而无需强制加载完整的运行时身份验证。实际的模型调用身份验证路径仍然使用 AWS SDK 默认链。
</Note>

<AccordionGroup>
  <Accordion title="发现配置选项">
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

    | 选项 | 默认值 | 描述 |
    | ------ | ------- | ----------- |
    | `enabled` | 自动 | 在自动模式下，OpenClaw 仅在检测到受支持的 AWS 环境变量标记时启用隐式 Bedrock provider。设置为 `true` 可强制执行发现。 |
    | `region` | `AWS_REGION` / `AWS_DEFAULT_REGION` / `us-east-1` | 用于发现 API 调用的 AWS 区域。 |
    | `providerFilter` | （全部） | 匹配 Bedrock provider 名称（例如 `anthropic`、`amazon`）。 |
    | `refreshInterval` | `3600` | 缓存持续时间（秒）。设置为 `0` 可禁用缓存。 |
    | `defaultContextWindow` | `32000` | 用于已发现模型的上下文窗口（如果你知道模型限制，可覆盖此值）。 |
    | `defaultMaxTokens` | `4096` | 用于已发现模型的最大输出 token 数（如果你知道模型限制，可覆盖此值）。 |

  </Accordion>
</AccordionGroup>

## 快速开始（AWS 路径）

本演练将创建一个 IAM 角色、附加 Bedrock 权限、关联实例配置文件，并在 EC2 主机上启用 OpenClaw 发现。

```bash
# 1. Create IAM role and instance profile
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

# 2. Attach to your EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. On the EC2 instance, enable discovery explicitly
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Optional: add an env marker if you want auto mode without explicit enable
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Verify models are discovered
openclaw models list
```

## 高级配置

<AccordionGroup>
  <Accordion title="推理配置文件">
    OpenClaw 会同时发现 **区域性和全局推理配置文件** 以及基础模型。当某个配置文件映射到已知的基础模型时，该配置文件会继承该模型的能力（上下文窗口、最大 token 数、推理、视觉），并且会自动注入正确的 Bedrock 请求区域。这意味着跨区域 Claude 配置文件无需手动覆盖 provider 即可工作。

    推理配置文件 ID 的格式可能是 `us.anthropic.claude-opus-4-6-v1:0`（区域性）或 `anthropic.claude-opus-4-6-v1:0`（全局）。如果其底层模型已出现在发现结果中，该配置文件会继承其完整能力集；否则会应用安全默认值。

    不需要额外配置。只要发现已启用，并且 IAM 主体具有 `bedrock:ListInferenceProfiles` 权限，配置文件就会与基础模型一起出现在 `openclaw models list` 中。

  </Accordion>

  <Accordion title="Guardrails">
    你可以通过向 `amazon-bedrock` 插件配置添加 `guardrail` 对象，将 [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html) 应用于所有 Bedrock 模型调用。Guardrails 可让你强制执行内容过滤、主题拒绝、词语过滤、敏感信息过滤和上下文依据检查。

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

    | 选项 | 必填 | 描述 |
    | ------ | -------- | ----------- |
    | `guardrailIdentifier` | 是 | Guardrail ID（例如 `abc123`）或完整 ARN（例如 `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`）。 |
    | `guardrailVersion` | 是 | 已发布的版本号，或工作草稿的 `"DRAFT"`。 |
    | `streamProcessingMode` | 否 | 流式传输期间 guardrail 评估的 `"sync"` 或 `"async"`。如果省略，Bedrock 将使用其默认值。 |
    | `trace` | 否 | 用于调试时设为 `"enabled"` 或 `"enabled_full"`；在生产环境中请省略或设为 `"disabled"`。 |

    <Warning>
    Gateway 网关使用的 IAM 主体除标准调用权限外，还必须具有 `bedrock:ApplyGuardrail` 权限。
    </Warning>

  </Accordion>

  <Accordion title="用于记忆搜索的 Embeddings">
    Bedrock 也可以作为 [记忆搜索](/zh-CN/concepts/memory-search) 的 embedding provider。该配置与推理 provider 分开设置——请将 `agents.defaults.memorySearch.provider` 设为 `"bedrock"`：

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: {
            provider: "bedrock",
            model: "amazon.titan-embed-text-v2:0", // default
          },
        },
      },
    }
    ```

    Bedrock embeddings 与推理使用相同的 AWS SDK 凭证链（实例角色、SSO、访问密钥、共享配置和 web identity）。不需要 API key。当 `provider` 为 `"auto"` 时，如果该凭证链成功解析，Bedrock 会被自动检测为可用。

    支持的 embedding 模型包括 Amazon Titan Embed（v1、v2）、Amazon Nova
    Embed、Cohere Embed（v3、v4）以及 TwelveLabs Marengo。完整模型列表和维度选项请参阅
    [记忆配置参考 -- Bedrock](/zh-CN/reference/memory-config#bedrock-embedding-config)。

  </Accordion>

  <Accordion title="说明与注意事项">
    - Bedrock 要求你在 AWS 账户/区域中启用**模型访问**。
    - 自动发现需要 `bedrock:ListFoundationModels` 和
      `bedrock:ListInferenceProfiles` 权限。
    - 如果你依赖自动模式，请在 Gateway 网关主机上设置受支持的 AWS 身份验证环境变量标记之一。如果你更倾向于使用无环境变量标记的 IMDS / 共享配置身份验证，请设置
      `plugins.entries.amazon-bedrock.config.discovery.enabled: true`。
    - OpenClaw 会按以下顺序显示凭证来源：`AWS_BEARER_TOKEN_BEDROCK`，
      然后是 `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`，接着是 `AWS_PROFILE`，最后是
      默认 AWS SDK 链。
    - 推理支持取决于具体模型；请查看 Bedrock 模型卡以了解当前能力。
    - 如果你更倾向于托管密钥流程，也可以在 Bedrock 前面放置一个兼容 OpenAI 的
      代理，并将其配置为 OpenAI provider。
  </Accordion>
</AccordionGroup>

## 相关内容

<CardGroup cols={2}>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障转移行为。
  </Card>
  <Card title="记忆搜索" href="/zh-CN/concepts/memory-search" icon="magnifying-glass">
    用于记忆搜索配置的 Bedrock embeddings。
  </Card>
  <Card title="记忆配置参考" href="/zh-CN/reference/memory-config#bedrock-embedding-config" icon="database">
    完整的 Bedrock embedding 模型列表和维度选项。
  </Card>
  <Card title="故障排除" href="/zh-CN/help/troubleshooting" icon="wrench">
    常规故障排除和常见问题。
  </Card>
</CardGroup>
