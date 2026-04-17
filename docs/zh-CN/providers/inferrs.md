---
read_when:
    - 你想让 OpenClaw 连接本地 inferrs 服务器运行
    - 你正在通过 inferrs 提供 Gemma 或其他模型服务
    - 你需要适用于 inferrs 的确切 OpenClaw 兼容标志
summary: 通过 inferrs（兼容 OpenAI 的本地服务器）运行 OpenClaw
title: inferrs
x-i18n:
    generated_at: "2026-04-12T10:12:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: 847dcc131fe51dfe163dcd60075dbfaa664662ea2a5c3986ccb08ddd37e8c31f
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) 可以通过兼容 OpenAI 的 `/v1` API 为本地模型提供服务。OpenClaw 可通过通用的 `openai-completions` 路径与 `inferrs` 配合使用。

目前，最好将 `inferrs` 视为自定义自托管的兼容 OpenAI 后端，而不是专用的 OpenClaw 提供商插件。

## 入门指南

<Steps>
  <Step title="使用模型启动 inferrs">
    ```bash
    inferrs serve google/gemma-4-E2B-it \
      --host 127.0.0.1 \
      --port 8080 \
      --device metal
    ```
  </Step>
  <Step title="验证服务器可达">
    ```bash
    curl http://127.0.0.1:8080/health
    curl http://127.0.0.1:8080/v1/models
    ```
  </Step>
  <Step title="添加一个 OpenClaw 提供商条目">
    添加一个显式的提供商条目，并将你的默认模型指向它。请参阅下方的完整配置示例。
  </Step>
</Steps>

## 完整配置示例

此示例在本地 `inferrs` 服务器上使用 Gemma 4。

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/google/gemma-4-E2B-it" },
      models: {
        "inferrs/google/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "google/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## 高级用法

<AccordionGroup>
  <Accordion title="为什么 requiresStringContent 很重要">
    某些 `inferrs` Chat Completions 路由只接受字符串类型的
    `messages[].content`，不接受结构化的内容片段数组。

    <Warning>
    如果 OpenClaw 运行失败，并出现类似下面的错误：

    ```text
    messages[1].content: invalid type: sequence, expected a string
    ```

    请在你的模型条目中设置 `compat.requiresStringContent: true`。
    </Warning>

    ```json5
    compat: {
      requiresStringContent: true
    }
    ```

    OpenClaw 会在发送请求前，将纯文本内容片段压平为普通字符串。

  </Accordion>

  <Accordion title="Gemma 和工具 schema 的注意事项">
    某些当前的 `inferrs` + Gemma 组合可以接受较小的直接
    `/v1/chat/completions` 请求，但在完整的 OpenClaw 智能体运行时轮次中仍会失败。

    如果发生这种情况，请先尝试这样设置：

    ```json5
    compat: {
      requiresStringContent: true,
      supportsTools: false
    }
    ```

    这会为该模型禁用 OpenClaw 的工具 schema 接口，并可减轻对较严格本地后端的提示词压力。

    如果很小的直接请求仍然能工作，但普通的 OpenClaw 智能体轮次仍持续在 `inferrs` 内部崩溃，那么剩余问题通常是上游模型/服务器行为，而不是 OpenClaw 的传输层。

  </Accordion>

  <Accordion title="手动冒烟测试">
    配置完成后，测试这两层：

    ```bash
    curl http://127.0.0.1:8080/v1/chat/completions \
      -H 'content-type: application/json' \
      -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'
    ```

    ```bash
    openclaw infer model run \
      --model inferrs/google/gemma-4-E2B-it \
      --prompt "What is 2 + 2? Reply with one short sentence." \
      --json
    ```

    如果第一条命令成功而第二条失败，请查看下方的故障排除部分。

  </Accordion>

  <Accordion title="代理式行为">
    `inferrs` 被视为代理式的兼容 OpenAI `/v1` 后端，而不是原生的
    OpenAI 端点。

    - 这里不适用仅限原生 OpenAI 的请求整形
    - 没有 `service_tier`，没有 Responses `store`，没有提示词缓存提示，也没有
      OpenAI 推理兼容负载整形
    - 在自定义 `inferrs` base URL 上，不会注入隐藏的 OpenClaw 归因标头（`originator`、`version`、`User-Agent`）

  </Accordion>
</AccordionGroup>

## 故障排除

<AccordionGroup>
  <Accordion title="curl /v1/models 失败">
    `inferrs` 未运行、不可达，或未绑定到预期的
    host/port。请确认服务器已启动，并正在监听你所配置的地址。
  </Accordion>

  <Accordion title="messages[].content 应为字符串">
    在模型条目中设置 `compat.requiresStringContent: true`。详细信息请参阅上方的
    `requiresStringContent` 部分。
  </Accordion>

  <Accordion title="直接调用 /v1/chat/completions 可以通过，但 openclaw infer model run 失败">
    尝试设置 `compat.supportsTools: false` 以禁用工具 schema 接口。
    请参阅上方 Gemma 工具 schema 注意事项。
  </Accordion>

  <Accordion title="inferrs 在更大的智能体轮次中仍然崩溃">
    如果 OpenClaw 不再出现 schema 错误，但 `inferrs` 在更大的
    智能体轮次中仍然崩溃，请将其视为上游 `inferrs` 或模型的限制。降低
    提示词压力，或切换到其他本地后端或模型。
  </Accordion>
</AccordionGroup>

<Tip>
如需一般帮助，请参阅 [故障排除](/zh-CN/help/troubleshooting) 和 [常见问题](/zh-CN/help/faq)。
</Tip>

## 另请参阅

<CardGroup cols={2}>
  <Card title="本地模型" href="/zh-CN/gateway/local-models" icon="server">
    让 OpenClaw 连接本地模型服务器运行。
  </Card>
  <Card title="Gateway 网关故障排除" href="/zh-CN/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail" icon="wrench">
    调试可通过探测但智能体运行失败的本地兼容 OpenAI 后端。
  </Card>
  <Card title="模型提供商" href="/zh-CN/concepts/model-providers" icon="layers">
    所有提供商、模型引用和故障切换行为的概览。
  </Card>
</CardGroup>
