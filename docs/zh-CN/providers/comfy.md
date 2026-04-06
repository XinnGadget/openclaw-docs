---
read_when:
    - 你想在 OpenClaw 中使用本地 ComfyUI 工作流
    - 你想使用 Comfy Cloud 进行图像、视频或音乐工作流
    - 你需要内置 comfy 插件的配置键名
summary: OpenClaw 中 ComfyUI 工作流的图像、视频和音乐生成设置
title: ComfyUI
x-i18n:
    generated_at: "2026-04-06T00:47:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: b15d826622787bfc5fec057007495145366c88e36100e7b4923ef581d801e2a3
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw 内置了 `comfy` 插件，用于运行由工作流驱动的 ComfyUI。

- 提供商：`comfy`
- 模型：`comfy/workflow`
- 共享接口：`image_generate`、`video_generate`
- 插件工具：`music_generate`
- 凭证：本地 ComfyUI 不需要；Comfy Cloud 使用 `COMFY_API_KEY` 或 `COMFY_CLOUD_API_KEY`
- API：ComfyUI `/prompt` / `/history` / `/view` 和 Comfy Cloud `/api/*`

## 支持内容

- 通过工作流 JSON 生成图像
- 使用 1 张上传的参考图像编辑图像
- 通过工作流 JSON 生成视频
- 使用 1 张上传的参考图像生成视频
- 通过内置的 `music_generate` 工具生成音乐或音频
- 从已配置的节点或所有匹配的输出节点下载输出内容

该内置插件由工作流驱动，因此 OpenClaw 不会尝试将通用的
`size`、`aspectRatio`、`resolution`、`durationSeconds` 或 TTS 风格的控制项
映射到你的工作流图中。

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
- `baseUrl`：本地模式默认是 `http://127.0.0.1:8188`，云模式默认是 `https://cloud.comfy.org`
- `apiKey`：可选的内联密钥，可替代环境变量
- `allowPrivateNetwork`：在云模式下允许使用私有网络 / 局域网 `baseUrl`

位于 `image`、`video` 或 `music` 下的各能力键名：

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

Comfy 视频工作流目前支持通过已配置的工作流图进行文生视频和图生视频。
OpenClaw 不会将输入视频传入 Comfy 工作流。

## 音乐工作流

该内置插件注册了一个 `music_generate` 工具，用于生成由工作流定义的音频
或音乐输出：

```text
/tool music_generate prompt="Warm ambient synth loop with soft tape texture"
```

使用 `music` 配置段指向你的音频工作流 JSON 和输出节点。

## Comfy Cloud

使用 `mode: "cloud"`，再配合以下任意一种方式：

- `COMFY_API_KEY`
- `COMFY_CLOUD_API_KEY`
- `models.providers.comfy.apiKey`

云模式仍然使用相同的 `image`、`video` 和 `music` 工作流配置段。

## 实时测试

该内置插件提供了可选启用的实时覆盖测试：

```bash
OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
```

如果未配置对应的 Comfy 工作流配置段，实时测试会跳过单独的图像、视频或音乐用例。

## 相关内容

- [图像生成](/zh-CN/tools/image-generation)
- [视频生成](/zh-CN/tools/video-generation)
- [音乐生成](/tools/music-generation)
- [提供商目录](/zh-CN/providers/index)
- [配置参考](/zh-CN/gateway/configuration-reference#agent-defaults)
