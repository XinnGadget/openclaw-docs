---
read_when:
    - 你想在 OpenClaw 中使用 Qwen
    - 你之前使用过 Qwen OAuth
summary: 通过 OpenClaw 内置的 qwen 提供商使用 Qwen Cloud
title: Qwen
x-i18n:
    generated_at: "2026-04-05T22:23:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: c1e1022a368513fd09474a2c2b8394911787a6bc5e325868da590a3d32446a34
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth 已被移除。** 曾使用 `portal.qwen.ai` 端点的免费层 OAuth 集成
（`qwen-portal`）现已不可用。
背景信息请参阅 [Issue #49557](https://github.com/openclaw/openclaw/issues/49557)。

</Warning>

## 推荐：Qwen Cloud

OpenClaw 现在将 Qwen 视为一等内置提供商，规范 id 为
`qwen`。该内置提供商面向 Qwen Cloud / Alibaba DashScope 和
Coding Plan 端点，并保留旧版 `modelstudio` id 作为兼容性别名。

- 提供商：`qwen`
- 首选环境变量：`QWEN_API_KEY`
- 为兼容性也接受：`MODELSTUDIO_API_KEY`、`DASHSCOPE_API_KEY`
- API 风格：兼容 OpenAI

如果你想使用 `qwen3.6-plus`，建议优先选择**标准版（按量付费）**端点。
Coding Plan 支持可能会落后于公开目录。

```bash
# 全局 Coding Plan 端点
openclaw onboard --auth-choice qwen-api-key

# 中国区 Coding Plan 端点
openclaw onboard --auth-choice qwen-api-key-cn

# 全局标准版（按量付费）端点
openclaw onboard --auth-choice qwen-standard-api-key

# 中国区标准版（按量付费）端点
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

旧版 `modelstudio-*` auth-choice id 和 `modelstudio/...` 模型引用仍然可用，
作为兼容性别名，但新的设置流程应优先使用规范的
`qwen-*` auth-choice id 和 `qwen/...` 模型引用。

完成新手引导后，设置默认模型：

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## 能力规划

`qwen` 扩展正被定位为完整 Qwen
Cloud 能力面的厂商归属位置，而不仅仅是编码/文本模型。

- 文本/聊天模型：现已内置
- 工具调用、结构化输出、思维链：继承自兼容 OpenAI 的传输层
- 图像生成：计划在提供商插件层实现
- 图像/视频理解：现已在标准版端点内置
- 语音/音频：计划在提供商插件层实现
- Memory embeddings/reranking：计划通过 embedding 适配器能力面提供
- 视频生成：现已通过共享视频生成能力内置

## 多模态附加功能

`qwen` 扩展现在还公开了：

- 通过 `qwen-vl-max-latest` 提供视频理解
- 通过以下模型提供 Wan 视频生成：
  - `wan2.6-t2v`（默认）
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

这些多模态能力面使用的是**标准版** DashScope 端点，而不是
Coding Plan 端点。

- 全局/国际版标准版 base URL：`https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- 中国区标准版 base URL：`https://dashscope.aliyuncs.com/compatible-mode/v1`

对于视频生成，OpenClaw 会先将已配置的 Qwen 区域映射到匹配的
DashScope AIGC 主机，然后再提交任务：

- 全局/国际版：`https://dashscope-intl.aliyuncs.com`
- 中国区：`https://dashscope.aliyuncs.com`

这意味着，即使普通的 `models.providers.qwen.baseUrl` 指向
Coding Plan 或标准版 Qwen 主机之一，
视频生成仍会使用正确地区的 DashScope 视频端点。

对于视频生成，请显式设置默认模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

当前内置的 Qwen 视频生成限制：

- 每个请求最多 **1** 个输出视频
- 最多 **1** 张输入图像
- 最多 **4** 个输入视频
- 时长最长 **10 秒**
- 支持 `size`、`aspectRatio`、`resolution`、`audio` 和 `watermark`
- 参考图像/视频模式目前要求使用**远程 http(s) URL**。本地文件路径会被预先拒绝，
  因为 DashScope 视频端点不接受为这些参考上传本地缓冲区。

有关共享工具参数、提供商选择和故障切换行为，请参阅
[视频生成](/zh-CN/tools/video-generation)。

有关端点级细节和兼容性说明，请参阅
[Qwen / Model Studio](/zh-CN/providers/qwen_modelstudio)。
