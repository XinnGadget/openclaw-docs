---
read_when:
    - 你想在 OpenClaw 中使用 GLM 模型
    - 你需要了解模型命名约定和设置方式
summary: GLM 模型家族概览 + 如何在 OpenClaw 中使用它
title: GLM（智谱）
x-i18n:
    generated_at: "2026-04-12T10:43:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: b38f0896c900fae3cf3458ff99938d73fa46973a057d1dd373ae960cb7d2e9b5
    source_path: providers/glm.md
    workflow: 15
---

# GLM 模型

GLM 是一个**模型家族**（不是公司），可通过 Z.AI 平台使用。在 OpenClaw 中，GLM
模型通过 `zai` 提供商访问，模型 ID 例如 `zai/glm-5`。

## 入门指南

<Steps>
  <Step title="选择一种凭证方式并运行新手引导">
    选择与你的 Z.AI 套餐和地区匹配的新手引导选项：

    | 凭证选项 | 最适合 |
    | ----------- | -------- |
    | `zai-api-key` | 通用 API 密钥设置，支持端点自动检测 |
    | `zai-coding-global` | Coding Plan 用户（全球） |
    | `zai-coding-cn` | Coding Plan 用户（中国地区） |
    | `zai-global` | 通用 API（全球） |
    | `zai-cn` | 通用 API（中国地区） |

    ```bash
    # 示例：通用自动检测
    openclaw onboard --auth-choice zai-api-key

    # 示例：Coding Plan 全球版
    openclaw onboard --auth-choice zai-coding-global
    ```

  </Step>
  <Step title="将 GLM 设为默认模型">
    ```bash
    openclaw config set agents.defaults.model.primary "zai/glm-5.1"
    ```
  </Step>
  <Step title="验证模型是否可用">
    ```bash
    openclaw models list --provider zai
    ```
  </Step>
</Steps>

## 配置示例

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

<Tip>
`zai-api-key` 会让 OpenClaw 根据密钥自动检测匹配的 Z.AI 端点，
并自动应用正确的基础 URL。如果你想强制使用特定的 Coding Plan 或通用 API 端点，
请使用显式地区选项。
</Tip>

## 内置 GLM 模型

OpenClaw 目前为内置 `zai` 提供商预置了这些 GLM 引用：

| 模型           | 模型            |
| --------------- | ---------------- |
| `glm-5.1`       | `glm-4.7`        |
| `glm-5`         | `glm-4.7-flash`  |
| `glm-5-turbo`   | `glm-4.7-flashx` |
| `glm-5v-turbo`  | `glm-4.6`        |
| `glm-4.5`       | `glm-4.6v`       |
| `glm-4.5-air`   |                  |
| `glm-4.5-flash` |                  |
| `glm-4.5v`      |                  |

<Note>
默认的内置模型引用是 `zai/glm-5.1`。GLM 版本和可用性
可能会变化；请查看 Z.AI 的文档以获取最新信息。
</Note>

## 高级说明

<AccordionGroup>
  <Accordion title="端点自动检测">
    当你使用 `zai-api-key` 凭证选项时，OpenClaw 会检查密钥格式，
    以确定正确的 Z.AI 基础 URL。显式地区选项
    （`zai-coding-global`、`zai-coding-cn`、`zai-global`、`zai-cn`）会覆盖
    自动检测并直接固定端点。
  </Accordion>

  <Accordion title="提供商详情">
    GLM 模型由 `zai` 运行时提供商提供。有关完整的提供商
    配置、地区端点和其他功能，请参阅
    [Z.AI 提供商文档](/zh-CN/providers/zai)。
  </Accordion>
</AccordionGroup>

## 相关内容

<CardGroup cols={2}>
  <Card title="Z.AI 提供商" href="/zh-CN/providers/zai" icon="server">
    完整的 Z.AI 提供商配置和地区端点。
  </Card>
  <Card title="模型选择" href="/zh-CN/concepts/model-providers" icon="layers">
    选择提供商、模型引用和故障转移行为。
  </Card>
</CardGroup>
