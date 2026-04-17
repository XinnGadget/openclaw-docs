---
read_when:
    - 你想在 OpenClaw 中使用 Hugging Face Inference
    - 你需要 HF token 环境变量或 CLI 认证选项
summary: Hugging Face Inference 设置（认证 + 模型选择）
title: Hugging Face（Inference）
x-i18n:
    generated_at: "2026-04-12T10:12:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7787fce1acfe81adb5380ab1c7441d661d03c574da07149c037d3b6ba3c8e52a
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face（Inference）

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers) 通过单一路由器 API 提供与 OpenAI 兼容的聊天补全。你只需一个 token，即可访问许多模型（DeepSeek、Llama 等）。OpenClaw 使用 **与 OpenAI 兼容的端点**（仅支持聊天补全）；对于文生图、embeddings 或语音，请直接使用 [HF inference clients](https://huggingface.co/docs/api-inference/quicktour)。

- 提供商：`huggingface`
- 认证：`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`（具备 **Make calls to Inference Providers** 权限的细粒度 token）
- API：与 OpenAI 兼容（`https://router.huggingface.co/v1`）
- 计费：单个 HF token；[定价](https://huggingface.co/docs/inference-providers/pricing) 按提供商费率计算，并提供免费层。

## 入门指南

<Steps>
  <Step title="创建细粒度 token">
    前往 [Hugging Face Settings Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained)，创建一个新的细粒度 token。

    <Warning>
    该 token 必须启用 **Make calls to Inference Providers** 权限，否则 API 请求将被拒绝。
    </Warning>

  </Step>
  <Step title="运行新手引导">
    在提供商下拉菜单中选择 **Hugging Face**，然后在提示时输入你的 API 密钥：

    ```bash
    openclaw onboard --auth-choice huggingface-api-key
    ```

  </Step>
  <Step title="选择默认模型">
    在 **Default Hugging Face model** 下拉菜单中，选择你想要的模型。当你拥有有效 token 时，该列表会从 Inference API 加载；否则会显示内置列表。你的选择将保存为默认模型。

    你也可以稍后在配置中设置或更改默认模型：

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
        },
      },
    }
    ```

  </Step>
  <Step title="验证模型可用">
    ```bash
    openclaw models list --provider huggingface
    ```
  </Step>
</Steps>

### 非交互式设置

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

这会将 `huggingface/deepseek-ai/DeepSeek-R1` 设置为默认模型。

## 模型 ID

模型引用使用 `huggingface/<org>/<model>` 格式（Hub 风格 ID）。以下列表来自 **GET** `https://router.huggingface.co/v1/models`；你的目录中可能包含更多模型。

| 模型 | 引用（添加 `huggingface/` 前缀） |
| ---------------------- | ----------------------------------- |
| DeepSeek R1            | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2          | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B               | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct    | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B              | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct  | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B           | `openai/gpt-oss-120b`               |
| GLM 4.7                | `zai-org/GLM-4.7`                   |
| Kimi K2.5              | `moonshotai/Kimi-K2.5`              |

<Tip>
你可以在任意模型 ID 后附加 `:fastest` 或 `:cheapest`。可在 [Inference Provider settings](https://hf.co/settings/inference-providers) 中设置默认顺序；完整列表请参阅 [Inference Providers](https://huggingface.co/docs/inference-providers) 和 **GET** `https://router.huggingface.co/v1/models`。
</Tip>

## 高级细节

<AccordionGroup>
  <Accordion title="模型发现与新手引导下拉菜单">
    OpenClaw 通过直接调用 **Inference endpoint** 来发现模型：

    ```bash
    GET https://router.huggingface.co/v1/models
    ```

    （可选：发送 `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` 或 `$HF_TOKEN` 以获取完整列表；某些端点在未认证时仅返回部分结果。）响应采用 OpenAI 风格格式：`{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`。

    当你配置 Hugging Face API 密钥后（通过新手引导、`HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN`），OpenClaw 会使用此 GET 请求来发现可用的聊天补全模型。在**交互式设置**期间，你输入 token 后会看到一个 **Default Hugging Face model** 下拉菜单，该菜单由该列表填充（如果请求失败，则使用内置目录）。在运行时（例如 Gateway 网关启动时），只要存在密钥，OpenClaw 也会再次调用 **GET** `https://router.huggingface.co/v1/models` 来刷新目录。该列表会与内置目录合并（用于上下文窗口和成本等元数据）。如果请求失败或未设置密钥，则仅使用内置目录。

  </Accordion>

  <Accordion title="模型名称、别名和策略后缀">
    - **来自 API 的名称：** 当 API 返回 `name`、`title` 或 `display_name` 时，模型显示名称会**通过 GET /v1/models 填充**；否则会从模型 ID 派生（例如，`deepseek-ai/DeepSeek-R1` 会变为 “DeepSeek R1”）。
    - **覆盖显示名称：** 你可以在配置中为每个模型设置自定义标签，以便它在 CLI 和 UI 中按你想要的方式显示：

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
            "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
          },
        },
      },
    }
    ```

    - **策略后缀：** OpenClaw 内置的 Hugging Face 文档和辅助工具目前将以下两个后缀视为内置策略变体：
      - **`:fastest`** — 最高吞吐量。
      - **`:cheapest`** — 每输出 token 成本最低。

      你可以将这些后缀作为单独条目添加到 `models.providers.huggingface.models` 中，或在 `model.primary` 中使用带后缀的值。你也可以在 [Inference Provider settings](https://hf.co/settings/inference-providers) 中设置默认提供商顺序（不带后缀 = 使用该顺序）。

    - **配置合并：** `models.providers.huggingface.models` 中现有的条目（例如在 `models.json` 中）在配置合并时会被保留。因此，你在那里设置的任何自定义 `name`、`alias` 或模型选项都会被保留。

  </Accordion>

  <Accordion title="环境和守护进程设置">
    如果 Gateway 网关以守护进程方式运行（launchd/systemd），请确保 `HUGGINGFACE_HUB_TOKEN` 或 `HF_TOKEN` 对该进程可用（例如在 `~/.openclaw/.env` 中，或通过 `env.shellEnv`）。

    <Note>
    OpenClaw 同时接受 `HUGGINGFACE_HUB_TOKEN` 和 `HF_TOKEN` 作为环境变量别名。任意一个都可用；如果两者都已设置，则 `HUGGINGFACE_HUB_TOKEN` 优先生效。
    </Note>

  </Accordion>

  <Accordion title="配置：使用 Qwen 作为回退的 DeepSeek R1">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-R1",
            fallbacks: ["huggingface/Qwen/Qwen3-8B"],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="配置：带 cheapest 和 fastest 变体的 Qwen">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen3-8B" },
          models: {
            "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
            "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
            "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="配置：带别名的 DeepSeek + Llama + GPT-OSS">
    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
            fallbacks: [
              "huggingface/meta-llama/Llama-3.3-70B-Instruct",
              "huggingface/openai/gpt-oss-120b",
            ],
          },
          models: {
            "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
            "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
            "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
          },
        },
      },
    }
    ```
  </Accordion>

  <Accordion title="配置：带策略后缀的多个 Qwen 和 DeepSeek">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
          models: {
            "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
            "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
            "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
            "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
          },
        },
      },
    }
    ```
  </Accordion>
</AccordionGroup>

## 相关内容

<CardGroup cols={2}>
  <Card title="模型提供商" href="/zh-CN/concepts/model-providers" icon="layers">
    所有提供商、模型引用和故障转移行为的概览。
  </Card>
  <Card title="模型选择" href="/zh-CN/concepts/models" icon="brain">
    如何选择和配置模型。
  </Card>
  <Card title="Inference Providers 文档" href="https://huggingface.co/docs/inference-providers" icon="book">
    Hugging Face Inference Providers 官方文档。
  </Card>
  <Card title="配置" href="/zh-CN/gateway/configuration" icon="gear">
    完整配置参考。
  </Card>
</CardGroup>
