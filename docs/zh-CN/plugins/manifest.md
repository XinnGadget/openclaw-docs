---
read_when:
    - 你正在构建一个 OpenClaw 插件
    - 你需要发布插件配置 schema，或调试插件校验错误
summary: 插件清单 + JSON schema 要求（严格配置校验）
title: 插件清单
x-i18n:
    generated_at: "2026-04-05T18:14:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8781fcccef80de68036826833ef46d482e399cdad180bfd799dcc96cd1dfc845
    source_path: plugins/manifest.md
    workflow: 15
---

# 插件清单（`openclaw.plugin.json`）

本页仅适用于 **原生 OpenClaw 插件清单**。

关于兼容的 bundle 布局，请参见 [Plugin bundles](/zh-CN/plugins/bundles)。

兼容的 bundle 格式使用不同的清单文件：

- Codex bundle：`.codex-plugin/plugin.json`
- Claude bundle：`.claude-plugin/plugin.json`，或不带清单的默认 Claude 组件
  布局
- Cursor bundle：`.cursor-plugin/plugin.json`

OpenClaw 也会自动检测这些 bundle 布局，但不会按照此处描述的
`openclaw.plugin.json` schema 对它们进行校验。

对于兼容 bundle，OpenClaw 当前会在布局符合 OpenClaw 运行时预期时，
读取 bundle 元数据，以及声明的 skill 根目录、Claude 命令根目录、Claude bundle 的
`settings.json` 默认值、Claude bundle 的 LSP 默认值，以及受支持的 hook pack。

每个原生 OpenClaw 插件**必须**在 **插件根目录** 中提供一个 `openclaw.plugin.json`
文件。OpenClaw 使用该清单在**不执行插件代码的情况下**
校验配置。缺失或无效的清单会被视为
插件错误，并阻止配置校验。

完整的插件系统指南请参见：[Plugins](/zh-CN/tools/plugin)。
关于原生能力模型和当前的外部兼容性指南，请参见：
[Capability model](/zh-CN/plugins/architecture#public-capability-model)。

## 这个文件的作用

`openclaw.plugin.json` 是 OpenClaw 在加载你的
插件代码之前读取的元数据。

它适用于：

- 插件标识
- 配置校验
- 无需启动插件运行时即可使用的认证和新手引导元数据
- 需要在插件运行时加载前解析的别名和自动启用元数据
- 需要在运行时加载前自动激活
  插件的简写模型家族归属元数据
- 用于内置兼容性接线和
  合同覆盖的静态能力归属快照
- 无需加载运行时即可合并到目录和校验
  表面的渠道专用配置元数据
- 配置 UI 提示

不要将它用于：

- 注册运行时行为
- 声明代码入口点
- npm 安装元数据

这些属于你的插件代码和 `package.json`。

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

| 字段                                | 必需 | 类型                             | 含义                                                                                                                                   |
| ----------------------------------- | ---- | -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | 是   | `string`                         | 规范插件 id。这是 `plugins.entries.<id>` 中使用的 id。                                                                                 |
| `configSchema`                      | 是   | `object`                         | 此插件配置的内联 JSON Schema。                                                                                                         |
| `enabledByDefault`                  | 否   | `true`                           | 将某个内置插件标记为默认启用。省略它，或设置为任何非 `true` 的值，则该插件默认禁用。                                                   |
| `legacyPluginIds`                   | 否   | `string[]`                       | 会规范化到这个规范插件 id 的旧版 id。                                                                                                  |
| `autoEnableWhenConfiguredProviders` | 否   | `string[]`                       | 当认证、配置或模型引用提到这些提供商 id 时，应自动启用此插件。                                                                         |
| `kind`                              | 否   | `"memory"` \| `"context-engine"` | 声明一个由 `plugins.slots.*` 使用的互斥插件类型。                                                                                      |
| `channels`                          | 否   | `string[]`                       | 此插件拥有的渠道 id。用于发现和配置校验。                                                                                              |
| `providers`                         | 否   | `string[]`                       | 此插件拥有的提供商 id。                                                                                                                |
| `modelSupport`                      | 否   | `object`                         | 由清单持有的简写模型家族元数据，用于在运行时之前自动加载插件。                                                                         |
| `providerAuthEnvVars`               | 否   | `Record<string, string[]>`       | OpenClaw 可在不加载插件代码的情况下检查的轻量级提供商认证环境变量元数据。                                                              |
| `providerAuthChoices`               | 否   | `object[]`                       | 用于新手引导选择器、首选提供商解析和简单 CLI flag 接线的轻量级认证选项元数据。                                                         |
| `contracts`                         | 否   | `object`                         | 用于语音、实时转录、实时语音、媒体理解、图像生成、视频生成、网页抓取、网页搜索和工具归属的静态内置能力快照。                         |
| `channelConfigs`                    | 否   | `Record<string, object>`         | 由清单持有的渠道配置元数据，在运行时加载前合并到发现和校验表面。                                                                       |
| `skills`                            | 否   | `string[]`                       | 要加载的 skill 目录，相对于插件根目录。                                                                                                |
| `name`                              | 否   | `string`                         | 人类可读的插件名称。                                                                                                                   |
| `description`                       | 否   | `string`                         | 显示在插件相关表面中的简短摘要。                                                                                                       |
| `version`                           | 否   | `string`                         | 仅供参考的插件版本。                                                                                                                   |
| `uiHints`                           | 否   | `Record<string, object>`         | 配置字段的 UI 标签、占位符和敏感性提示。                                                                                               |

## `providerAuthChoices` 参考

每个 `providerAuthChoices` 条目描述一个新手引导或认证选项。
OpenClaw 会在提供商运行时加载之前读取它。

| 字段                  | 必需 | 类型                                            | 含义                                                               |
| --------------------- | ---- | ----------------------------------------------- | ------------------------------------------------------------------ |
| `provider`            | 是   | `string`                                        | 此选项所属的提供商 id。                                            |
| `method`              | 是   | `string`                                        | 要分发到的认证方法 id。                                            |
| `choiceId`            | 是   | `string`                                        | 供新手引导和 CLI 流程使用的稳定认证选项 id。                       |
| `choiceLabel`         | 否   | `string`                                        | 面向用户的标签。如果省略，OpenClaw 会回退到 `choiceId`。           |
| `choiceHint`          | 否   | `string`                                        | 选择器中的简短辅助文本。                                           |
| `assistantPriority`   | 否   | `number`                                        | 数值越小，在由助手驱动的交互式选择器中排序越靠前。                 |
| `assistantVisibility` | 否   | `"visible"` \| `"manual-only"`                  | 在助手选择器中隐藏该选项，但仍允许通过手动 CLI 进行选择。          |
| `deprecatedChoiceIds` | 否   | `string[]`                                      | 应将用户重定向到此替代选项的旧版选项 id。                          |
| `groupId`             | 否   | `string`                                        | 用于对相关选项分组的可选分组 id。                                  |
| `groupLabel`          | 否   | `string`                                        | 该分组的面向用户标签。                                             |
| `groupHint`           | 否   | `string`                                        | 该分组的简短辅助文本。                                             |
| `optionKey`           | 否   | `string`                                        | 用于简单单 flag 认证流程的内部选项键。                             |
| `cliFlag`             | 否   | `string`                                        | CLI flag 名称，例如 `--openrouter-api-key`。                       |
| `cliOption`           | 否   | `string`                                        | 完整 CLI 选项形式，例如 `--openrouter-api-key <key>`。             |
| `cliDescription`      | 否   | `string`                                        | CLI 帮助中使用的描述。                                             |
| `onboardingScopes`    | 否   | `Array<"text-inference" \| "image-generation">` | 该选项应出现在哪些新手引导表面中。如果省略，默认值为 `["text-inference"]`。 |

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

每个字段提示可以包括：

| 字段          | 类型       | 含义                         |
| ------------- | ---------- | ---------------------------- |
| `label`       | `string`   | 面向用户的字段标签。         |
| `help`        | `string`   | 简短辅助文本。               |
| `tags`        | `string[]` | 可选的 UI 标签。             |
| `advanced`    | `boolean`  | 将该字段标记为高级字段。     |
| `sensitive`   | `boolean`  | 将该字段标记为秘密或敏感项。 |
| `placeholder` | `string`   | 表单输入的占位文本。         |

## `contracts` 参考

仅在 `contracts` 中放置 OpenClaw 可在不导入插件运行时的情况下
读取的静态能力归属元数据。

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

| 字段                             | 类型       | 含义                                   |
| -------------------------------- | ---------- | -------------------------------------- |
| `speechProviders`                | `string[]` | 此插件拥有的语音提供商 id。            |
| `realtimeTranscriptionProviders` | `string[]` | 此插件拥有的实时转录提供商 id。        |
| `realtimeVoiceProviders`         | `string[]` | 此插件拥有的实时语音提供商 id。        |
| `mediaUnderstandingProviders`    | `string[]` | 此插件拥有的媒体理解提供商 id。        |
| `imageGenerationProviders`       | `string[]` | 此插件拥有的图像生成提供商 id。        |
| `videoGenerationProviders`       | `string[]` | 此插件拥有的视频生成提供商 id。        |
| `webFetchProviders`              | `string[]` | 此插件拥有的网页抓取提供商 id。        |
| `webSearchProviders`             | `string[]` | 此插件拥有的网页搜索提供商 id。        |
| `tools`                          | `string[]` | 此插件拥有的智能体工具名称，用于内置合同检查。 |

## `channelConfigs` 参考

当渠道插件需要在运行时加载前获得轻量级配置元数据时，请使用 `channelConfigs`。

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

每个渠道条目可以包括：

| 字段          | 类型                     | 含义                                                                 |
| ------------- | ------------------------ | -------------------------------------------------------------------- |
| `schema`      | `object`                 | `channels.<id>` 的 JSON Schema。每个声明的渠道配置条目都必须提供。   |
| `uiHints`     | `Record<string, object>` | 该渠道配置部分的可选 UI 标签/占位符/敏感性提示。                     |
| `label`       | `string`                 | 当运行时元数据尚未准备好时，合并到选择器和检查表面中的渠道标签。     |
| `description` | `string`                 | 用于检查和目录表面的简短渠道描述。                                   |
| `preferOver`  | `string[]`               | 在选择表面中，此渠道应优先于的旧版或较低优先级插件 id。              |

## `modelSupport` 参考

当 OpenClaw 需要从诸如 `gpt-5.4` 或 `claude-sonnet-4.6` 之类的
简写模型 id 中推断你的提供商插件，并且这一过程发生在插件运行时
加载之前时，请使用 `modelSupport`。

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw 按以下优先级应用规则：

- 显式的 `provider/model` 引用使用拥有该提供商的 `providers` 清单元数据
- `modelPatterns` 优先于 `modelPrefixes`
- 如果一个非内置插件和一个内置插件都匹配，则非内置
  插件胜出
- 对于剩余的歧义，在用户或配置明确指定提供商之前会被忽略

字段：

| 字段            | 类型       | 含义                                                                  |
| --------------- | ---------- | --------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | 对简写模型 id 使用 `startsWith` 进行匹配的前缀。                      |
| `modelPatterns` | `string[]` | 在移除配置文件后缀后，对简写模型 id 进行匹配的正则表达式源码。        |

旧版顶层能力键已弃用。使用 `openclaw doctor --fix` 将
`speechProviders`、`realtimeTranscriptionProviders`、
`realtimeVoiceProviders`、`mediaUnderstandingProviders`、
`imageGenerationProviders`、`videoGenerationProviders`、
`webFetchProviders` 和 `webSearchProviders` 移动到 `contracts` 下；普通
清单加载已不再将这些顶层字段视为能力归属。

## 清单与 `package.json` 的区别

这两个文件承担的职责不同：

| 文件                   | 用途                                                                                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | 发现、配置校验、认证选项元数据，以及必须在插件代码运行前就存在的 UI 提示                                                           |
| `package.json`         | npm 元数据、依赖安装，以及用于入口点、安装门控、设置或目录元数据的 `openclaw` 配置块                                              |

如果你不确定某段元数据该放在哪里，请使用这条规则：

- 如果 OpenClaw 必须在加载插件代码之前知道它，就把它放进 `openclaw.plugin.json`
- 如果它与打包、入口文件或 npm 安装行为有关，就把它放进 `package.json`

### 会影响发现的 `package.json` 字段

某些运行前插件元数据有意放在 `package.json` 的
`openclaw` 配置块下，而不是 `openclaw.plugin.json` 中。

重要示例：

| 字段                                                              | 含义                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | 声明原生插件入口点。                                                                  |
| `openclaw.setupEntry`                                             | 轻量级、仅用于设置的入口点，用于新手引导和延迟的渠道启动。                            |
| `openclaw.channel`                                                | 轻量级渠道目录元数据，例如标签、文档路径、别名和选择文案。                            |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | 为内置插件和外部发布插件提供安装/更新提示。                                           |
| `openclaw.install.defaultChoice`                                  | 当有多个安装来源可用时的首选安装路径。                                                |
| `openclaw.install.minHostVersion`                                 | 最低支持的 OpenClaw 主机版本，使用类似 `>=2026.3.22` 的 semver 下限。                 |
| `openclaw.install.allowInvalidConfigRecovery`                     | 当配置无效时，允许狭义的内置插件重装恢复路径。                                        |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | 允许仅设置用的渠道表面在启动时于完整渠道插件之前加载。                                |

`openclaw.install.minHostVersion` 会在安装期间和清单
注册表加载期间强制执行。无效值会被拒绝；有效但更高的值会在旧主机上
跳过该插件。

`openclaw.install.allowInvalidConfigRecovery` 的设计范围刻意很窄。它
不会让任意损坏的配置都变得可安装。目前它只允许安装
流程从特定的陈旧内置插件升级失败中恢复，例如缺失的内置插件路径，
或同一内置插件的陈旧 `channels.<id>` 条目。无关的配置错误仍会阻止安装，
并将操作员引导到 `openclaw doctor --fix`。

## JSON Schema 要求

- **每个插件都必须提供一个 JSON Schema**，即使它不接受任何配置。
- 空 schema 也是可以接受的（例如 `{ "type": "object", "additionalProperties": false }`）。
- Schema 会在配置读取/写入时校验，而不是在运行时校验。

## 校验行为

- 未知的 `channels.*` 键会被视为**错误**，除非该渠道 id 已由
  某个插件清单声明。
- `plugins.entries.<id>`、`plugins.allow`、`plugins.deny` 和 `plugins.slots.*`
  必须引用**可发现的**插件 id。未知 id 会被视为**错误**。
- 如果插件已安装，但其清单或 schema 损坏或缺失，
  校验将失败，Doctor 会报告该插件错误。
- 如果插件配置存在，但插件被**禁用**，配置会被保留，并且
  Doctor + 日志中会显示一条**警告**。

完整的 `plugins.*` schema 请参见 [Configuration reference](/zh-CN/gateway/configuration)。

## 说明

- 清单对于**原生 OpenClaw 插件**是**必需的**，包括本地文件系统加载。
- 运行时仍会单独加载插件模块；清单仅用于
  发现 + 校验。
- 原生清单使用 JSON5 解析，因此只要最终值仍是对象，
  注释、尾随逗号和未加引号的键都是允许的。
- 清单加载器只会读取文档中说明的清单字段。避免在这里添加
  自定义顶层键。
- `providerAuthEnvVars` 是用于认证探测、环境变量标记
  校验以及类似提供商认证表面的轻量级元数据路径，这些场景不应仅为检查环境变量名而启动插件
  运行时。
- `providerAuthChoices` 是用于认证选项选择器、
  `--auth-choice` 解析、首选提供商映射以及在提供商运行时加载前进行简单新手引导
  CLI flag 注册的轻量级元数据路径。对于需要提供商代码的运行时向导
  元数据，请参见
  [Provider runtime hooks](/zh-CN/plugins/architecture#provider-runtime-hooks)。
- 互斥插件类型通过 `plugins.slots.*` 进行选择。
  - `kind: "memory"` 由 `plugins.slots.memory` 选择。
  - `kind: "context-engine"` 由 `plugins.slots.contextEngine`
    选择（默认：内置 `legacy`）。
- 当插件不需要它们时，
  `channels`、`providers` 和 `skills` 可以省略。
- 如果你的插件依赖原生模块，请记录构建步骤以及任何
  包管理器允许列表要求（例如 pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`）。

## 相关内容

- [Building Plugins](/zh-CN/plugins/building-plugins) —— 插件入门指南
- [Plugin Architecture](/zh-CN/plugins/architecture) —— 内部架构
- [SDK Overview](/zh-CN/plugins/sdk-overview) —— 插件 SDK 概览
