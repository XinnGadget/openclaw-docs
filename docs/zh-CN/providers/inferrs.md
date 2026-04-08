---
read_when:
    - 你想让 OpenClaw 连接本地 inferrs 服务器运行
    - 你正在通过 inferrs 提供 Gemma 或其他模型
    - 你需要 inferrs 对应的精确 OpenClaw 兼容标志
summary: 通过 inferrs（兼容 OpenAI 的本地服务器）运行 OpenClaw
title: inferrs
x-i18n:
    generated_at: "2026-04-08T14:16:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 03b9d5a9935c75fd369068bacb7807a5308cd0bd74303b664227fb664c3a2098
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs) 可以通过兼容 OpenAI 的 `/v1` API 为本地模型提供服务。OpenClaw 可通过通用的 `openai-completions` 路径与 `inferrs` 配合使用。

当前最好将 `inferrs` 视为自定义自托管的兼容 OpenAI 后端，而不是专用的 OpenClaw 提供商插件。

## 快速开始

1. 使用模型启动 `inferrs`。

示例：

```bash
inferrs serve google/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. 验证服务器可访问。

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. 添加一个显式的 OpenClaw 提供商条目，并将你的默认模型指向它。

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

## 为什么 `requiresStringContent` 很重要

某些 `inferrs` Chat Completions 路由仅接受字符串形式的 `messages[].content`，不接受结构化的内容分片数组。

如果 OpenClaw 运行失败，并出现类似这样的错误：

```text
messages[1].content: invalid type: sequence, expected a string
```

请设置：

```json5
compat: {
  requiresStringContent: true
}
```

OpenClaw 会在发送请求前，将纯文本内容分片展平为普通字符串。

## Gemma 与工具 schema 注意事项

某些当前的 `inferrs` + Gemma 组合可以接受较小的直接 `/v1/chat/completions` 请求，但在完整的 OpenClaw 智能体运行时轮次中仍然会失败。

如果出现这种情况，先尝试这样设置：

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

这会为该模型禁用 OpenClaw 的工具 schema 接口，并可减轻对更严格的本地后端造成的提示词压力。

如果较小的直接请求仍然可以工作，但正常的 OpenClaw 智能体轮次继续在 `inferrs` 内部崩溃，那么剩余问题通常是上游模型或服务器行为导致的，而不是 OpenClaw 的传输层问题。

## 手动冒烟测试

配置完成后，同时测试这两层：

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"google/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/google/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

如果第一条命令有效，但第二条失败，请使用下面的故障排除说明。

## 故障排除

- `curl /v1/models` 失败：`inferrs` 未运行、无法访问，或未绑定到预期的主机/端口。
- `messages[].content ... expected a string`：设置 `compat.requiresStringContent: true`。
- 直接的小型 `/v1/chat/completions` 调用通过，但 `openclaw infer model run` 失败：尝试设置 `compat.supportsTools: false`。
- OpenClaw 不再出现 schema 错误，但 `inferrs` 在更大的智能体轮次中仍然崩溃：将其视为上游 `inferrs` 或模型的限制，并减少提示词压力，或切换本地后端/模型。

## 代理式行为

`inferrs` 被视为代理式的兼容 OpenAI `/v1` 后端，而不是原生 OpenAI 端点。

- 原生 OpenAI 专用的请求整形不适用于这里
- 没有 `service_tier`、没有 Responses `store`、没有提示词缓存提示，也没有 OpenAI reasoning 兼容载荷整形
- 在自定义 `inferrs` base URLs 上，不会注入隐藏的 OpenClaw 归因请求头（`originator`、`version`、`User-Agent`）

## 另请参阅

- [本地模型](/zh-CN/gateway/local-models)
- [Gateway 网关故障排除](/zh-CN/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [模型提供商](/zh-CN/concepts/model-providers)
