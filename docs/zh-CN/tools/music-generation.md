---
read_when:
    - 通过智能体生成音乐或音频
    - 配置插件提供的音乐生成工具
    - 了解 `music_generate` 工具参数
summary: 使用插件提供的工具（例如 ComfyUI 工作流）生成音乐或音频
title: 音乐生成
x-i18n:
    generated_at: "2026-04-06T00:47:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 625fe7cd03f88541104d21da12dc318344e8d82fd2ec0bf1f7c0fb817dd14c62
    source_path: tools/music-generation.md
    workflow: 15
---

# 音乐生成

当某个插件注册了音乐生成功能时，`music_generate` 工具允许智能体创建音频文件。

内置的 `comfy` 插件当前通过工作流配置的 ComfyUI 图提供 `music_generate`。

## 快速开始

1. 使用工作流 JSON 以及提示词/输出节点配置 `models.providers.comfy.music`。
2. 如果你使用 Comfy Cloud，请设置 `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY`。
3. 让智能体生成音乐，或直接调用该工具。

示例：

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

## 工具参数

| 参数 | 类型 | 描述 |
| ---------- | ------ | --------------------------------------------------- |
| `prompt`   | string | 音乐或音频生成提示词 |
| `action`   | string | `"generate"`（默认）或 `"list"` |
| `model`    | string | 提供商/模型覆盖。当前为 `comfy/workflow` |
| `filename` | string | 已保存音频文件的输出文件名提示 |

## 当前提供商支持

| 提供商 | 模型 | 说明 |
| -------- | ---------- | ------------------------------- |
| ComfyUI  | `workflow` | 由工作流定义的音乐或音频 |

## 实时测试

内置 ComfyUI 音乐路径的选择启用式实时覆盖：

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

如果这些部分已完成配置，该实时文件还涵盖 comfy 图像和视频工作流。

## 相关内容

- [ComfyUI](/providers/comfy)
- [工具概览](/zh-CN/tools)
