---
read_when:
    - 你想在 OpenClaw 中使用 Alibaba Wan 视频生成
    - 你需要为视频生成设置 Model Studio 或 DashScope API 密钥
summary: OpenClaw 中的 Alibaba Model Studio Wan 视频生成
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-05T22:22:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: dca1ddd91e884773c3835eebda2da3da2994f82f940bdd26fe94e55cac149058
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw 内置了一个 `alibaba` 视频生成提供商，用于 Alibaba Model Studio / DashScope 上的 Wan 模型。

- 提供商：`alibaba`
- 首选凭证：`MODELSTUDIO_API_KEY`
- 也接受：`DASHSCOPE_API_KEY`、`QWEN_API_KEY`
- API：DashScope / Model Studio 异步视频生成

## 快速开始

1. 设置 API 密钥：

```bash
openclaw onboard --auth-choice qwen-standard-api-key
```

2. 设置默认视频模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "alibaba/wan2.6-t2v",
      },
    },
  },
}
```

## 内置 Wan 模型

内置的 `alibaba` 提供商当前注册了以下模型：

- `alibaba/wan2.6-t2v`
- `alibaba/wan2.6-i2v`
- `alibaba/wan2.6-r2v`
- `alibaba/wan2.6-r2v-flash`
- `alibaba/wan2.7-r2v`

## 当前限制

- 每次请求最多 **1** 个输出视频
- 最多 **1** 张输入图片
- 最多 **4** 个输入视频
- 最长 **10 秒** 时长
- 支持 `size`、`aspectRatio`、`resolution`、`audio` 和 `watermark`
- 参考图片/视频模式当前要求使用 **远程 http(s) URL**

## 与 Qwen 的关系

内置的 `qwen` 提供商也使用 Alibaba 托管的 DashScope 端点来进行 Wan 视频生成。请使用：

- 当你想使用规范的 Qwen 提供商接口时，使用 `qwen/...`
- 当你想使用供应商直接拥有的 Wan 视频接口时，使用 `alibaba/...`

## 相关内容

- [视频生成](/zh-CN/tools/video-generation)
- [Qwen](/zh-CN/providers/qwen)
- [Qwen / Model Studio](/zh-CN/providers/qwen_modelstudio)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
