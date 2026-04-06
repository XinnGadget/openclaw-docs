---
read_when:
    - 你想在 OpenClaw 中使用本地 ComfyUI 工作流
    - 你想将 Comfy Cloud 与图像、视频或音乐工作流一起使用
    - 你需要内置 comfy 插件的配置键名
summary: OpenClaw 中 ComfyUI 工作流的图像、视频和音乐生成设置
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T01:07:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: e645f32efdffdf4cd498684f1924bb953a014d3656b48f4b503d64e38c61ba9c
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw 内置了一个 `comfy` 插件，用于执行由工作流驱动的 ComfyUI 运行。

- 提供商：`comfy`
- 模型：`comfy/workflow`
- 共享接口：`image_generate`、`video_generate`、`music_generate`
- 凭证：本地 ComfyUI 无需凭证；Comfy Cloud 使用 `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY`
- API：ComfyUI `/prompt` / `/history` / `/view` 以及 Comfy Cloud `/api/*`

## 支持内容

- 基于工作流 JSON 的图像生成
- 使用 1 张上传参考图像进行图像编辑
- 基于工作流 JSON 的视频生成
- 使用 1 张上传参考图像进行视频生成
- 通过共享 `music_generate` 工具进行音乐或音频生成
- 从已配置节点或所有匹配的输出节点下载输出内容

这个内置插件由工作流驱动，因此 OpenClaw 不会尝试将通用的
`size`、`aspectRatio`、`resolution`、`durationSeconds` 或类 TTS 控制
映射到你的图中。

## 配置布局

Comfy 支持共享的顶层连接设置，以及按能力划分的工作流配置段：

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

共享键名：

- `mode`：`local` 或 `cloud`
- `baseUrl`：本地模式默认值为 `http://127.0.0.1:8188`，云模式默认值为 `https://cloud.comfy.org`
- `apiKey`：可选的内联密钥，可替代环境变量
- `allowPrivateNetwork`：在云模式下允许使用私有网络 / LAN `baseUrl`

位于 `image`、`video` 或 `music` 下的按能力配置键名：

- `workflow` 或 `workflowPath`：必填
- `promptNodeId`：必填
- `promptInputName`：默认值为 `text`
- `outputNodeId`：可选
- `pollIntervalMs`：可选
- `timeoutMs`：可选

图像和视频配置段还支持：

- `inputImageNodeId`：当你传入参考图像时必填
- `inputImageInputName`：默认值为 `image`

## 向后兼容性

现有的顶层图像配置仍然可用：

```json5
{
  models: {
    providers: {
      comfy: {
        workflowPath: "./workflows/flux-api.json",
        promptNodeId: "6",
        outputNodeId: "9",
      },
    },
  },
}
```

OpenClaw 会将这种旧版结构视为图像工作流配置。

## 图像工作流

设置默认图像模型：

```json5
{
  agents: {
    defaults: {
      imageGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

参考图像编辑示例：

```json5
{
  models: {
    providers: {
      comfy: {
        image: {
          workflowPath: "./workflows/edit-api.json",
          promptNodeId: "6",
          inputImageNodeId: "7",
          inputImageInputName: "image",
          outputNodeId: "9",
        },
      },
    },
  },
}
```

## 视频工作流

设置默认视频模型：

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "comfy/workflow",
      },
    },
  },
}
```

Comfy 视频工作流目前通过已配置图支持文生视频和图生视频。
OpenClaw 不会将输入视频传入 Comfy 工作流。

## 音乐工作流

这个内置插件为工作流定义的音频或音乐输出注册了一个音乐生成提供商，
并通过共享 `music_generate` 工具对外提供：

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

使用 `music` 配置段指向你的音频工作流 JSON 和输出节点。

## Comfy Cloud

使用 `mode: "cloud"`，并搭配以下任一方式：

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

云模式仍然使用相同的 `image`、`video` 和 `music` 工作流配置段。

## 实时测试

这个内置插件提供了可选启用的实时覆盖测试：

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

除非已配置对应的 Comfy 工作流配置段，否则实时测试会跳过单独的图像、视频或音乐用例。

## 相关内容

- [图像生成](/zh-CN/tools/image-generation)
- [视频生成](/zh-CN/tools/video-generation)
- [音乐生成](/zh-CN/tools/music-generation)
- [提供商目录](/zh-CN/providers/index)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
