---
read_when:
    - 你正在构建一个 OpenClaw 插件
    - 你需要发布插件配置 schema，或调试插件校验错误
summary: 插件清单 + JSON Schema 要求（严格配置校验）
title: 插件清单
x-i18n:
    generated_at: "2026-04-06T00:20:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 89a940d54bd18bf60368addd09aeef47d53ca9b07714397e1c43083e01aac6b6
    source_path: plugins/manifest.md
    workflow: 15
---

# 插件清单（`openclaw.plugin.json`）

本页仅适用于**原生 OpenClaw 插件清单**。

关于兼容的 bundle 布局，请参阅 [插件包](/zh-CN/plugins/bundles)。

兼容的 bundle 格式使用不同的清单文件：

- Codex bundle：`.codex-plugin/plugin.json`
- Claude bundle：`.claude-plugin/plugin.json` 或不带清单的默认 Claude 组件布局
- Cursor bundle：`.cursor-plugin/plugin.json`

OpenClaw 也会自动检测这些 bundle 布局，但它们不会按照这里介绍的 `openclaw.plugin.json` schema 进行校验。

对于兼容 bundle，当布局符合 OpenClaw 运行时预期时，OpenClaw 当前会读取 bundle 元数据，以及声明的 skill 根目录、Claude 命令根目录、Claude bundle `settings.json` 默认值、Claude bundle LSP 默认值，以及受支持的 hook 包。

每个原生 OpenClaw 插件**都必须**在**插件根目录**中提供一个 `openclaw.plugin.json` 文件。OpenClaw 使用这个清单在**不执行插件代码的情况下**校验配置。缺失或无效的清单会被视为插件错误，并阻止配置校验。

完整的插件系统指南请参阅：[插件](/zh-CN/tools/plugin)。
关于原生能力模型和当前外部兼容性指南，请参阅：
[能力模型](/zh-CN/plugins/architecture#public-capability-model)。

## 这个文件的作用

`openclaw.plugin.json` 是 OpenClaw 在加载你的插件代码之前读取的元数据。

请将它用于：

- 插件标识
- 配置校验
- 无需启动插件运行时即可获取的凭证和新手引导元数据
- 应在插件运行时加载前解析的别名和自动启用元数据
- 应在运行时加载前自动激活插件的简写模型家族归属元数据
- 用于内置兼容接线和契约覆盖的静态能力归属快照
- 无需加载运行时即可合并到目录和校验表面的渠道专用配置元数据
- 配置 UI 提示

不要将它用于：

- 注册运行时行为
- 声明代码入口点
- npm 安装元数据

这些内容应放在你的插件代码和 `package.json` 中。

## 最小示例

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## 完整示例

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "OpenRouter provider plugin",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## 顶层字段参考

| Field                               | Required | Type                             | 含义                                                                                                                                       |
| ----------------------------------- | -------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | 是       | `string`                         | 规范插件 id。这是在 `plugins.entries.<id>` 中使用的 id。                                                                                  |
| `configSchema`                      | 是       | `object`                         | 此插件配置的内联 JSON Schema。                                                                                                             |
| `enabledByDefault`                  | 否       | `true`                           | 将某个内置插件标记为默认启用。省略它，或将其设为任何非 `true` 的值，都会让该插件默认保持禁用。                                           |
| `legacyPluginIds`                   | 否       | `string[]`                       | 会规范化到此规范插件 id 的旧版 id。                                                                                                        |
| `autoEnableWhenConfiguredProviders` | 否       | `string[]`                       | 当凭证、配置或模型引用提到这些提供商 id 时，应自动启用此插件。                                                                             |
| `kind`                              | 否       | `"memory"` \| `"context-engine"` | 声明一个供 `plugins.slots.*` 使用的独占插件类型。                                                                                         |
| `channels`                          | 否       | `string[]`                       | 此插件拥有的渠道 id。用于发现和配置校验。                                                                                                  |
| `providers`                         | 否       | `string[]`                       | 此插件拥有的提供商 id。                                                                                                                    |
| `modelSupport`                      | 否       | `object`                         | 由清单拥有的简写模型家族元数据，用于在运行时之前自动加载插件。                                                                             |
| `providerAuthEnvVars`               | 否       | `Record<string, string[]>`       | 无需加载插件代码即可由 OpenClaw 检查的轻量提供商凭证环境变量元数据。                                                                       |
| `providerAuthChoices`               | 否       | `object[]`                       | 供新手引导选择器、首选提供商解析和简单 CLI flag 接线使用的轻量凭证选项元数据。                                                            |
| `contracts`                         | 否       | `object`                         | 用于语音、实时转写、实时语音、媒体理解、图像生成、视频生成、网页抓取、Web 搜索 和工具归属的静态内置能力快照。                           |
| `channelConfigs`                    | 否       | `Record<string, object>`         | 由清单拥有的渠道配置元数据，在运行时加载前合并到发现和校验表面中。                                                                         |
| `skills`                            | 否       | `string[]`                       | 要加载的 Skills 目录，相对于插件根目录。                                                                                                   |
| `name`                              | 否       | `string`                         | 人类可读的插件名称。                                                                                                                       |
| `description`                       | 否       | `string`                         | 在插件相关表面中显示的简短摘要。                                                                                                           |
| `version`                           | 否       | `string`                         | 信息性插件版本。                                                                                                                           |
| `uiHints`                           | 否       | `Record<string, object>`         | 配置字段的 UI 标签、占位符和敏感性提示。                                                                                                   |

## `providerAuthChoices` 参考

每个 `providerAuthChoices` 条目描述一个新手引导或凭证选择项。
OpenClaw 会在提供商运行时加载前读取它。

| Field                 | Required | Type                                            | 含义                                                                                     |
| --------------------- | -------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `provider`            | 是       | `string`                                        | 此选项所属的提供商 id。                                                                  |
| `method`              | 是       | `string`                                        | 要分派到的凭证方法 id。                                                                  |
| `choiceId`            | 是       | `string`                                        | 供新手引导和 CLI 流程使用的稳定凭证选项 id。                                             |
| `choiceLabel`         | 否       | `string`                                        | 面向用户的标签。如果省略，OpenClaw 会回退到 `choiceId`。                                 |
| `choiceHint`          | 否       | `string`                                        | 选择器的简短帮助文本。                                                                   |
| `assistantPriority`   | 否       | `number`                                        | 在由智能体驱动的交互式选择器中，数值越小排序越靠前。                                     |
| `assistantVisibility` | 否       | `"visible"` \| `"manual-only"`                  | 在智能体选择器中隐藏该选项，但仍允许在手动 CLI 选择中使用。                              |
| `deprecatedChoiceIds` | 否       | `string[]`                                      | 应将用户重定向到当前替代选项的旧版 choice id。                                           |
| `groupId`             | 否       | `string`                                        | 用于对相关选项进行分组的可选组 id。                                                      |
| `groupLabel`          | 否       | `string`                                        | 该分组的面向用户标签。                                                                   |
| `groupHint`           | 否       | `string`                                        | 该分组的简短帮助文本。                                                                   |
| `optionKey`           | 否       | `string`                                        | 用于简单单 flag 凭证流程的内部选项键名。                                                 |
| `cliFlag`             | 否       | `string`                                        | CLI flag 名称，例如 `--openrouter-api-key`。                                             |
| `cliOption`           | 否       | `string`                                        | 完整的 CLI 选项形态，例如 `--openrouter-api-key <key>`。                                 |
| `cliDescription`      | 否       | `string`                                        | 用于 CLI 帮助信息中的说明。                                                              |
| `onboardingScopes`    | 否       | `Array<"text-inference" \| "image-generation">` | 该选项应出现在哪些新手引导表面中。如果省略，默认值为 `["text-inference"]`。              |

## `uiHints` 参考

`uiHints` 是从配置字段名映射到小型渲染提示的映射表。

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

每个字段提示可以包含：

| Field         | Type       | 含义                       |
| ------------- | ---------- | -------------------------- |
| `label`       | `string`   | 面向用户的字段标签。       |
| `help`        | `string`   | 简短帮助文本。             |
| `tags`        | `string[]` | 可选的 UI 标签。           |
| `advanced`    | `boolean`  | 将该字段标记为高级字段。   |
| `sensitive`   | `boolean`  | 将该字段标记为密钥或敏感。 |
| `placeholder` | `string`   | 表单输入的占位文本。       |

## `contracts` 参考

仅将 `contracts` 用于 OpenClaw 可在不导入插件运行时的情况下读取的静态能力归属元数据。

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

每个列表都是可选的：

| Field                            | Type       | 含义                                           |
| -------------------------------- | ---------- | ---------------------------------------------- |
| `speechProviders`                | `string[]` | 此插件拥有的语音提供商 id。                    |
| `realtimeTranscriptionProviders` | `string[]` | 此插件拥有的实时转写提供商 id。                |
| `realtimeVoiceProviders`         | `string[]` | 此插件拥有的实时语音提供商 id。                |
| `mediaUnderstandingProviders`    | `string[]` | 此插件拥有的媒体理解提供商 id。                |
| `imageGenerationProviders`       | `string[]` | 此插件拥有的图像生成提供商 id。                |
| `videoGenerationProviders`       | `string[]` | 此插件拥有的视频生成提供商 id。                |
| `webFetchProviders`              | `string[]` | 此插件拥有的网页抓取提供商 id。                |
| `webSearchProviders`             | `string[]` | 此插件拥有的 Web 搜索 提供商 id。              |
| `tools`                          | `string[]` | 此插件为内置契约检查拥有的智能体工具名称。     |

## `channelConfigs` 参考

当渠道插件在运行时加载前需要轻量配置元数据时，请使用 `channelConfigs`。

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

每个渠道条目可以包含：

| Field         | Type                     | 含义                                                                                   |
| ------------- | ------------------------ | -------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` 的 JSON Schema。每个声明的渠道配置条目都必须提供。                    |
| `uiHints`     | `Record<string, object>` | 该渠道配置部分可选的 UI 标签 / 占位符 / 敏感性提示。                                  |
| `label`       | `string`                 | 当运行时元数据尚未准备好时，合并到选择器和检查表面中的渠道标签。                      |
| `description` | `string`                 | 用于检查和目录表面的简短渠道描述。                                                    |
| `preferOver`  | `string[]`               | 在选择表面中，此渠道应优先于的旧版或较低优先级插件 id。                               |

## `modelSupport` 参考

如果 OpenClaw 应在插件运行时加载前，根据 `gpt-5.4` 或 `claude-sonnet-4.6` 这样的简写模型 id 推断你的提供商插件，请使用 `modelSupport`。

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw 会按以下优先级处理：

- 显式 `provider/model` 引用使用所属 `providers` 清单元数据
- `modelPatterns` 优先于 `modelPrefixes`
- 如果一个非内置插件和一个内置插件都匹配，则非内置插件胜出
- 其余歧义会被忽略，直到用户或配置显式指定提供商

字段：

| Field           | Type       | 含义                                                                             |
| --------------- | ---------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | 使用 `startsWith` 针对简写模型 id 进行匹配的前缀。                               |
| `modelPatterns` | `string[]` | 在移除 profile 后缀后，针对简写模型 id 进行匹配的正则表达式源码。                |

旧版顶层能力键已弃用。请使用 `openclaw doctor --fix` 将 `speechProviders`、`realtimeTranscriptionProviders`、`realtimeVoiceProviders`、`mediaUnderstandingProviders`、`imageGenerationProviders`、`videoGenerationProviders`、`webFetchProviders` 和 `webSearchProviders` 移动到 `contracts` 下；普通清单加载不再将这些顶层字段视为能力归属。

## 清单与 `package.json` 的区别

这两个文件承担不同的职责：

| File                   | 用途                                                                                                                           |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.plugin.json` | 发现、配置校验、凭证选项元数据，以及必须在插件代码运行前存在的 UI 提示                                                         |
| `package.json`         | npm 元数据、依赖安装，以及用于入口点、安装门控、设置或目录元数据的 `openclaw` 配置块                                         |

如果你不确定某段元数据应放在哪里，请使用以下规则：

- 如果 OpenClaw 必须在加载插件代码之前知道它，就把它放在 `openclaw.plugin.json` 中
- 如果它与打包、入口文件或 npm 安装行为有关，就把它放在 `package.json` 中

### 影响发现的 `package.json` 字段

某些运行时前的插件元数据有意放在 `package.json` 的 `openclaw` 配置块下，而不是 `openclaw.plugin.json` 中。

重要示例：

| Field                                                             | 含义                                                                                                                                         |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | 声明原生插件入口点。                                                                                                                         |
| `openclaw.setupEntry`                                             | 轻量的仅设置入口点，用于新手引导和延迟渠道启动期间。                                                                                         |
| `openclaw.channel`                                                | 轻量渠道目录元数据，例如标签、文档路径、别名和选择文案。                                                                                     |
| `openclaw.channel.configuredState`                                | 轻量已配置状态检查器元数据，可在不加载完整渠道运行时的情况下回答“是否已存在仅基于环境变量的设置？”。                                       |
| `openclaw.channel.persistedAuthState`                             | 轻量持久化凭证状态检查器元数据，可在不加载完整渠道运行时的情况下回答“是否已有任何已登录状态？”。                                           |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | 用于内置插件和外部发布插件的安装 / 更新提示。                                                                                                 |
| `openclaw.install.defaultChoice`                                  | 当存在多个安装来源时的首选安装路径。                                                                                                         |
| `openclaw.install.minHostVersion`                                 | 最低支持的 OpenClaw 主机版本，使用类似 `>=2026.3.22` 的 semver 下限。                                                                        |
| `openclaw.install.allowInvalidConfigRecovery`                     | 当配置无效时，允许一个范围很窄的内置插件重新安装恢复路径。                                                                                   |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 允许在启动期间，先加载仅设置渠道表面，再加载完整渠道插件。                                                                                   |

`openclaw.install.minHostVersion` 会在安装期间和清单注册表加载期间强制执行。无效值会被拒绝；较新但有效的值会让旧主机跳过该插件。

`openclaw.install.allowInvalidConfigRecovery` 的范围被有意限制得很窄。它不会让任意损坏的配置变得可安装。当前它只允许安装流程从特定的陈旧内置插件升级失败中恢复，例如缺失的内置插件路径，或该内置插件对应的陈旧 `channels.<id>` 条目。无关的配置错误仍会阻止安装，并引导操作员使用 `openclaw doctor --fix`。

`openclaw.channel.persistedAuthState` 是一个小型检查器模块的包元数据：

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

当设置、Doctor 或已配置状态流程需要在完整渠道插件加载前进行轻量的是 / 否凭证探测时，请使用它。目标导出应是一个仅读取持久化状态的小函数；不要通过完整渠道运行时 barrel 暴露它。

`openclaw.channel.configuredState` 对轻量仅环境变量已配置检查采用相同的结构：

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

当某个渠道可以根据环境变量或其他微小的非运行时输入回答已配置状态时，请使用它。如果检查需要完整配置解析或真实渠道运行时，请将该逻辑保留在插件 `config.hasConfiguredState` hook 中。

## JSON Schema 要求

- **每个插件都必须提供一个 JSON Schema**，即使它不接受任何配置。
- 可以接受空 schema（例如 `{ "type": "object", "additionalProperties": false }`）。
- Schema 会在配置读取 / 写入时校验，而不是在运行时校验。

## 校验行为

- 未知的 `channels.*` 键会被视为**错误**，除非该渠道 id 已由某个插件清单声明。
- `plugins.entries.<id>`、`plugins.allow`、`plugins.deny` 和 `plugins.slots.*` 必须引用**可发现的**插件 id。未知 id 会被视为**错误**。
- 如果插件已安装，但其清单或 schema 损坏或缺失，校验会失败，Doctor 会报告该插件错误。
- 如果插件配置存在，但插件处于**禁用**状态，则配置会被保留，并且 Doctor + 日志中会显示**警告**。

完整的 `plugins.*` schema 请参阅 [配置参考](/zh-CN/gateway/configuration)。

## 注意事项

- 对于**原生 OpenClaw 插件**，清单是**必需的**，包括本地文件系统加载。
- 运行时仍会单独加载插件模块；清单仅用于发现 + 校验。
- 原生清单使用 JSON5 解析，因此支持注释、尾随逗号和未加引号的键，只要最终值仍然是一个对象即可。
- 清单加载器只会读取文档中说明的清单字段。避免在这里添加自定义顶层键。
- `providerAuthEnvVars` 是用于凭证探测、环境变量标记校验以及类似提供商凭证表面的轻量元数据路径，这些表面不应为了检查环境变量名而启动插件运行时。
- `providerAuthChoices` 是在提供商运行时加载前，用于凭证选项选择器、`--auth-choice` 解析、首选提供商映射以及简单新手引导 CLI flag 注册的轻量元数据路径。对于需要提供商代码的运行时向导元数据，请参阅
  [提供商运行时 hooks](/zh-CN/plugins/architecture#provider-runtime-hooks)。
- 独占插件类型通过 `plugins.slots.*` 进行选择。
  - `kind: "memory"` 通过 `plugins.slots.memory` 选择。
  - `kind: "context-engine"` 通过 `plugins.slots.contextEngine` 选择
    （默认值：内置 `legacy`）。
- 当插件不需要它们时，可以省略 `channels`、`providers` 和 `skills`。
- 如果你的插件依赖原生模块，请记录构建步骤以及任何包管理器允许列表要求（例如 pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`）。

## 相关内容

- [构建插件](/zh-CN/plugins/building-plugins) — 插件快速开始
- [插件架构](/zh-CN/plugins/architecture) — 内部架构
- [SDK 概览](/zh-CN/plugins/sdk-overview) — 插件 SDK 参考
