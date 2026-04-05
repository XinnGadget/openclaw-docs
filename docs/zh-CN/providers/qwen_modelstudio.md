---
read_when:
    - 你想了解 Qwen Cloud / Alibaba DashScope 的端点级详细信息
    - 你需要了解 qwen 提供商的环境变量兼容方案
    - 你想使用 Standard（按量付费）或 Coding Plan 端点
summary: 内置 qwen 提供商及其旧版 modelstudio 兼容层的端点详情
title: Qwen / Model Studio
x-i18n:
    generated_at: "2026-04-05T22:23:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: f21bf55e7acf51131027a1c1faf5fa85a00757ee40995ea4e1d24935cd310e24
    source_path: providers/qwen_modelstudio.md
    workflow: 15
---

# Qwen / Model Studio（Alibaba Cloud）

本页说明 OpenClaw 内置 `qwen`
提供商背后的端点映射。该提供商会继续让 `modelstudio` 提供商 id、auth-choice id 和
模型引用作为兼容别名正常工作，同时将 `qwen` 作为规范表面。

<Info>

如果你需要 **`qwen3.6-plus`**，优先选择 **Standard（按量付费）**。Coding
Plan 的可用性可能落后于公开的 Model Studio 目录，并且在某个模型出现在你的套餐支持模型列表之前，
Coding Plan API 可能会拒绝该模型。

</Info>

- 提供商：`qwen`（旧版别名：`modelstudio`）
- 认证：`QWEN_API_KEY`
- 也接受：`MODELSTUDIO_API_KEY`、`DASHSCOPE_API_KEY`
- API：兼容 OpenAI

## 快速开始

### Standard（按量付费）

```bash
# 中国端点
openclaw onboard --auth-choice qwen-standard-api-key-cn

# 全球/国际端点
openclaw onboard --auth-choice qwen-standard-api-key
```

### Coding Plan（订阅制）

```bash
# 中国端点
openclaw onboard --auth-choice qwen-api-key-cn

# 全球/国际端点
openclaw onboard --auth-choice qwen-api-key
```

旧版 `modelstudio-*` auth-choice id 仍可作为兼容别名使用，但
规范的新手引导 id 是上面显示的 `qwen-*` 选项。

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

## 套餐类型和端点

| 套餐 | 区域 | Auth choice | 端点 |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard（按量付费） | 中国 | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1` |
| Standard（按量付费） | 全球 | `qwen-standard-api-key` | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan（订阅制） | 中国 | `qwen-api-key-cn` | `coding.dashscope.aliyuncs.com/v1` |
| Coding Plan（订阅制） | 全球 | `qwen-api-key` | `coding-intl.dashscope.aliyuncs.com/v1` |

该提供商会根据你的 auth choice 自动选择端点。规范
选项使用 `qwen-*` 系列；`modelstudio-*` 仅保留用于兼容。
你可以
在配置中使用自定义 `baseUrl` 进行覆盖。

原生 Model Studio 端点在共享的 `openai-completions` 传输协议上声明支持流式使用兼容性。
OpenClaw 现在会根据端点能力来判断这一点，因此，目标指向相同原生主机的 DashScope 兼容自定义提供商 id
也会继承相同的流式使用行为，而不再
必须特定使用内置 `qwen` 提供商 id。

## 获取你的 API 密钥

- **管理密钥**：[home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **文档**：[docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## 内置目录

OpenClaw 当前内置了以下 Qwen 目录：

| 模型引用 | 输入 | 上下文 | 说明 |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus` | text, image | 1,000,000 | 默认模型 |
| `qwen/qwen3.6-plus` | text, image | 1,000,000 | 需要此模型时优先使用 Standard 端点 |
| `qwen/qwen3-max-2026-01-23` | text | 262,144 | Qwen Max 系列 |
| `qwen/qwen3-coder-next` | text | 262,144 | 编码 |
| `qwen/qwen3-coder-plus` | text | 1,000,000 | 编码 |
| `qwen/MiniMax-M2.5` | text | 1,000,000 | 已启用推理 |
| `qwen/glm-5` | text | 202,752 | GLM |
| `qwen/glm-4.7` | text | 202,752 | GLM |
| `qwen/kimi-k2.5` | text, image | 262,144 | Moonshot AI，经由 Alibaba |

即使某个模型
出现在内置目录中，其可用性仍可能因端点和计费套餐而异。

原生流式传输使用兼容性同时适用于 Coding Plan 主机和
Standard DashScope 兼容主机：

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Qwen 3.6 Plus 可用性

`qwen3.6-plus` 可用于 Standard（按量付费）Model Studio
端点：

- 中国：`dashscope.aliyuncs.com/compatible-mode/v1`
- 全球：`dashscope-intl.aliyuncs.com/compatible-mode/v1`

如果 Coding Plan 端点对
`qwen3.6-plus` 返回“unsupported model”错误，请切换到 Standard（按量付费），而不是继续使用 Coding Plan
端点/密钥组合。

## 环境说明

如果 Gateway 网关以守护进程（launchd/systemd）方式运行，请确保
该进程可以访问 `QWEN_API_KEY`（例如放在
`~/.openclaw/.env` 中，或通过 `env.shellEnv` 提供）。

## Wan 视频生成

Standard DashScope 表面也为内置 Wan 视频生成
提供商提供支持。

你可以通过任一前缀来引用同一个 Wan 系列：

- 规范 Qwen 引用：
  - `qwen/wan2.6-t2v`
  - `qwen/wan2.6-i2v`
  - `qwen/wan2.6-r2v`
  - `qwen/wan2.6-r2v-flash`
  - `qwen/wan2.7-r2v`
- 直接 Alibaba 引用：
  - `alibaba/wan2.6-t2v`
  - `alibaba/wan2.6-i2v`
  - `alibaba/wan2.6-r2v`
  - `alibaba/wan2.6-r2v-flash`
  - `alibaba/wan2.7-r2v`

目前所有 Wan 参考模式都要求图像或
视频参考使用 **远程 http(s) URL**。本地文件路径会在上传前被拒绝，因为
DashScope 视频端点在这些模式下不接受本地缓冲区参考资源。

## 相关内容

- [Qwen](/zh-CN/providers/qwen)
- [Alibaba Model Studio](/providers/alibaba)
- [视频生成](/zh-CN/tools/video-generation)
