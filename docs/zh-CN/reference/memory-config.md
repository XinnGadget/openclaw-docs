---
read_when:
    - 你想配置内存搜索提供商或嵌入模型
    - 你想设置 QMD 后端
    - 你想调优混合搜索、MMR 或时间衰减
    - 你想启用多模态内存索引
summary: 内存搜索、嵌入提供商、QMD、混合搜索和多模态索引的所有配置项
title: 内存配置参考
x-i18n:
    generated_at: "2026-04-05T23:00:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 24dcdca7e2c29f27e61b0ed076574d6b473832f839cba2cc0c0d57e2ac17c196
    source_path: reference/memory-config.md
    workflow: 15
---

# 内存配置参考

本页列出了 OpenClaw 内存搜索的每一个配置项。有关概念概览，请参见：

- [内存概览](/zh-CN/concepts/memory) -- 内存的工作方式
- [内置引擎](/zh-CN/concepts/memory-builtin) -- 默认的 SQLite 后端
- [QMD 引擎](/zh-CN/concepts/memory-qmd) -- 本地优先的 sidecar
- [内存搜索](/zh-CN/concepts/memory-search) -- 搜索流水线和调优

除非另有说明，所有内存搜索设置都位于 `openclaw.json` 中的
`agents.defaults.memorySearch` 下。

---

## 提供商选择

| Key        | Type      | Default          | Description                                                                      |
| ---------- | --------- | ---------------- | -------------------------------------------------------------------------------- |
| `provider` | `string`  | 自动检测         | 嵌入适配器 ID：`openai`、`gemini`、`voyage`、`mistral`、`ollama`、`local` |
| `model`    | `string`  | 提供商默认值     | 嵌入模型名称                                                             |
| `fallback` | `string`  | `"none"`         | 当主适配器失败时使用的回退适配器 ID                                       |
| `enabled`  | `boolean` | `true`           | 启用或禁用内存搜索                                                  |

### 自动检测顺序

当未设置 `provider` 时，OpenClaw 会选择第一个可用项：

1. `local` -- 如果已配置 `memorySearch.local.modelPath` 且文件存在。
2. `openai` -- 如果可以解析到 OpenAI 密钥。
3. `gemini` -- 如果可以解析到 Gemini 密钥。
4. `voyage` -- 如果可以解析到 Voyage 密钥。
5. `mistral` -- 如果可以解析到 Mistral 密钥。

支持 `ollama`，但不会自动检测（请显式设置）。

### API 密钥解析

远程嵌入需要 API 密钥。OpenClaw 会从以下位置解析：
auth 配置文件、`models.providers.*.apiKey` 或环境变量。

| Provider | Env var                        | Config key                        |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Ollama   | `OLLAMA_API_KEY` （占位符）    | --                                |

Codex OAuth 仅覆盖 chat/completions，不满足嵌入请求。

---

## 远程端点配置

用于自定义兼容 OpenAI 的端点或覆盖提供商默认值：

| Key              | Type     | Description                                        |
| ---------------- | -------- | -------------------------------------------------- |
| `remote.baseUrl` | `string` | 自定义 API 基础 URL                                |
| `remote.apiKey`  | `string` | 覆盖 API 密钥                                   |
| `remote.headers` | `object` | 额外的 HTTP 标头（与提供商默认值合并） |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Gemini 专用配置

| Key                    | Type     | Default                | Description                                |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | 也支持 `gemini-embedding-2-preview` |
| `outputDimensionality` | `number` | `3072`                 | 对于 Embedding 2：768、1536 或 3072        |

<Warning>
更改模型或 `outputDimensionality` 会触发自动完整重建索引。
</Warning>

---

## 本地嵌入配置

| Key                   | Type     | Default                | Description                     |
| --------------------- | -------- | ---------------------- | ------------------------------- |
| `local.modelPath`     | `string` | 自动下载        | GGUF 模型文件路径         |
| `local.modelCacheDir` | `string` | `node-llama-cpp` 默认值 | 已下载模型的缓存目录 |

默认模型：`embeddinggemma-300m-qat-Q8_0.gguf`（约 0.6 GB，自动下载）。
需要原生构建：`pnpm approve-builds`，然后执行 `pnpm rebuild node-llama-cpp`。

---

## 混合搜索配置

全部位于 `memorySearch.query.hybrid` 下：

| Key                   | Type      | Default | Description                        |
| --------------------- | --------- | ------- | ---------------------------------- |
| `enabled`             | `boolean` | `true`  | 启用混合 BM25 + 向量搜索 |
| `vectorWeight`        | `number`  | `0.7`   | 向量评分权重（0-1）     |
| `textWeight`          | `number`  | `0.3`   | BM25 评分权重（0-1）       |
| `candidateMultiplier` | `number`  | `4`     | 候选池大小乘数     |

### MMR（多样性）

| Key           | Type      | Default | Description                          |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | 启用 MMR 重排序                |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = 最大多样性，1 = 最大相关性 |

### 时间衰减（新近性）

| Key                          | Type      | Default | Description               |
| ---------------------------- | --------- | ------- | ------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | 启用新近性提升      |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | 每隔 N 天分数减半 |

常青文件（`MEMORY.md`、`memory/` 中无日期的文件）永远不会衰减。

### 完整示例

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## 额外内存路径

| Key          | Type       | Description                              |
| ------------ | ---------- | ---------------------------------------- |
| `extraPaths` | `string[]` | 要索引的额外目录或文件 |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

路径可以是绝对路径，也可以是相对于工作区的路径。目录会递归扫描
`.md` 文件。符号链接的处理取决于当前后端：
内置引擎会忽略符号链接，而 QMD 会遵循底层 QMD
扫描器的行为。

对于按智能体范围进行的跨智能体转录搜索，请使用
`agents.list[].memorySearch.qmd.extraCollections`，而不是 `memory.qmd.paths`。
这些额外集合遵循相同的 `{ path, name, pattern? }` 结构，但
它们会按智能体合并，并且当路径指向当前工作区之外时，
可以保留显式共享名称。
如果同一个解析后的路径同时出现在 `memory.qmd.paths` 和
`memorySearch.qmd.extraCollections` 中，QMD 会保留第一个条目并跳过
重复项。

---

## 多模态内存（Gemini）

使用 Gemini Embedding 2 将图片和音频与 Markdown 一起编入索引：

| Key                       | Type       | Default    | Description                            |
| ------------------------- | ---------- | ---------- | -------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | 启用多模态索引             |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`、`["audio"]` 或 `["all"]` |
| `multimodal.maxFileBytes` | `number`   | `10000000` | 用于索引的最大文件大小             |

仅适用于 `extraPaths` 中的文件。默认内存根目录仍仅支持 Markdown。
需要 `gemini-embedding-2-preview`。`fallback` 必须为 `"none"`。

支持的格式：`.jpg`、`.jpeg`、`.png`、`.webp`、`.gif`、`.heic`、`.heif`
（图片）；`.mp3`、`.wav`、`.ogg`、`.opus`、`.m4a`、`.aac`、`.flac`（音频）。

---

## 嵌入缓存

| Key                | Type      | Default | Description                      |
| ------------------ | --------- | ------- | -------------------------------- |
| `cache.enabled`    | `boolean` | `false` | 在 SQLite 中缓存分块嵌入 |
| `cache.maxEntries` | `number`  | `50000` | 最大缓存嵌入数量            |

可防止在重建索引或转录更新期间对未更改文本重复生成嵌入。

---

## 批量索引

| Key                           | Type      | Default | Description                |
| ----------------------------- | --------- | ------- | -------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | 启用批量嵌入 API |
| `remote.batch.concurrency`    | `number`  | `2`     | 并行批处理作业        |
| `remote.batch.wait`           | `boolean` | `true`  | 等待批处理完成  |
| `remote.batch.pollIntervalMs` | `number`  | --      | 轮询间隔              |
| `remote.batch.timeoutMinutes` | `number`  | --      | 批处理超时时间              |

适用于 `openai`、`gemini` 和 `voyage`。OpenAI 批处理通常
在大规模回填时最快且最便宜。

---

## 会话内存搜索（实验性）

为会话转录建立索引，并通过 `memory_search` 暴露：

| Key                           | Type       | Default      | Description                             |
| ----------------------------- | ---------- | ------------ | --------------------------------------- |
| `experimental.sessionMemory`  | `boolean`  | `false`      | 启用会话索引                 |
| `sources`                     | `string[]` | `["memory"]` | 添加 `"sessions"` 以包含转录 |
| `sync.sessions.deltaBytes`    | `number`   | `100000`     | 重新索引的字节阈值              |
| `sync.sessions.deltaMessages` | `number`   | `50`         | 重新索引的消息阈值           |

会话索引为选择启用，并以异步方式运行。结果可能会略有
滞后。会话日志存储在磁盘上，因此请将文件系统访问视为信任
边界。

---

## SQLite 向量加速（sqlite-vec）

| Key                          | Type      | Default | Description                       |
| ---------------------------- | --------- | ------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`  | 对向量查询使用 sqlite-vec |
| `store.vector.extensionPath` | `string`  | 内置 | 覆盖 sqlite-vec 路径          |

当 sqlite-vec 不可用时，OpenClaw 会自动回退到进程内余弦
相似度计算。

---

## 索引存储

| Key                   | Type     | Default                               | Description                                 |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------- |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | 索引位置（支持 `{agentId}` 令牌） |
| `store.fts.tokenizer` | `string` | `unicode61`                           | FTS5 分词器（`unicode61` 或 `trigram`）   |

---

## QMD 后端配置

设置 `memory.backend = "qmd"` 以启用。所有 QMD 设置都位于
`memory.qmd` 下：

| Key                      | Type      | Default  | Description                                  |
| ------------------------ | --------- | -------- | -------------------------------------------- |
| `command`                | `string`  | `qmd`    | QMD 可执行文件路径                          |
| `searchMode`             | `string`  | `search` | 搜索命令：`search`、`vsearch`、`query` |
| `includeDefaultMemory`   | `boolean` | `true`   | 自动索引 `MEMORY.md` + `memory/**/*.md`    |
| `paths[]`                | `array`   | --       | 额外路径：`{ name, path, pattern? }`      |
| `sessions.enabled`       | `boolean` | `false`  | 索引会话转录                    |
| `sessions.retentionDays` | `number`  | --       | 转录保留期                         |
| `sessions.exportDir`     | `string`  | --       | 导出目录                             |

### 更新计划

| Key                       | Type      | Default | Description                           |
| ------------------------- | --------- | ------- | ------------------------------------- |
| `update.interval`         | `string`  | `5m`    | 刷新间隔                      |
| `update.debounceMs`       | `number`  | `15000` | 文件变更去抖时间                 |
| `update.onBoot`           | `boolean` | `true`  | 启动时刷新                    |
| `update.waitForBootSync`  | `boolean` | `false` | 在刷新完成前阻塞启动 |
| `update.embedInterval`    | `string`  | --      | 单独的嵌入执行频率                |
| `update.commandTimeoutMs` | `number`  | --      | QMD 命令超时时间              |
| `update.updateTimeoutMs`  | `number`  | --      | QMD 更新操作超时时间     |
| `update.embedTimeoutMs`   | `number`  | --      | QMD 嵌入操作超时时间      |

### 限制

| Key                       | Type     | Default | Description                |
| ------------------------- | -------- | ------- | -------------------------- |
| `limits.maxResults`       | `number` | `6`     | 最大搜索结果数         |
| `limits.maxSnippetChars`  | `number` | --      | 限制摘要长度       |
| `limits.maxInjectedChars` | `number` | --      | 限制注入的总字符数 |
| `limits.timeoutMs`        | `number` | `4000`  | 搜索超时时间             |

### 范围

控制哪些会话可以接收 QMD 搜索结果。结构与
[`session.sendPolicy`](/zh-CN/gateway/configuration-reference#session) 相同：

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

默认仅限私信。`match.keyPrefix` 匹配规范化后的会话键；
`match.rawKeyPrefix` 匹配包含 `agent:<id>:` 的原始键。

### 引用

`memory.citations` 适用于所有后端：

| Value            | Behavior                                            |
| ---------------- | --------------------------------------------------- |
| `auto` （默认） | 在摘要中包含 `Source: <path#line>` 页脚    |
| `on`             | 始终包含页脚                               |
| `off`            | 省略页脚（路径仍会在内部传递给智能体） |

### 完整 QMD 示例

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming（实验性）

Dreaming 配置位于 `plugins.entries.memory-core.config.dreaming` 下，
而不是 `agents.defaults.memorySearch`。Dreaming 使用三个协同
阶段（light、deep、REM），每个阶段都有自己的计划和配置。有关
概念细节和聊天命令，请参见 [Dreaming](/zh-CN/concepts/dreaming)。

### 全局设置

| Key                       | Type      | Default    | Description                                                  |
| ------------------------- | --------- | ---------- | ------------------------------------------------------------ |
| `enabled`                 | `boolean` | `true`     | 所有阶段的总开关                                 |
| `timezone`                | `string`  | 未设置      | 用于计划评估和 Dreaming 日期分桶的时区 |
| `verboseLogging`          | `boolean` | `false`    | 输出详细的逐次运行 Dreaming 日志                          |
| `storage.mode`            | `string`  | `"inline"` | 内联 `DREAMS.md`、单独报告或两者都写入                |
| `storage.separateReports` | `boolean` | `false`    | 为每个阶段写入单独的报告文件                        |

### Light 阶段（`phases.light`）

扫描最近的轨迹、去重，并在启用内联存储时将候选项暂存到 `DREAMS.md` 中。
**不会**写入 `MEMORY.md`。

| Key                | Type       | Default                         | Description                 |
| ------------------ | ---------- | ------------------------------- | --------------------------- |
| `enabled`          | `boolean`  | `true`                          | 启用 light 阶段          |
| `cron`             | `string`   | `0 */6 * * *`                   | 计划（每 6 小时一次）    |
| `lookbackDays`     | `number`   | `2`                             | 要扫描的轨迹天数      |
| `limit`            | `number`   | `100`                           | 要暂存的最大候选数     |
| `dedupeSimilarity` | `number`   | `0.9`                           | 去重的 Jaccard 阈值 |
| `sources`          | `string[]` | `["daily","sessions","recall"]` | 数据源                |

### Deep 阶段（`phases.deep`）

将合格候选项提升到 `MEMORY.md` 中。**唯一**会写入持久事实的阶段。
也负责在内存内容稀少时进行恢复。

| Key                   | Type       | Default                                         | Description                          |
| --------------------- | ---------- | ----------------------------------------------- | ------------------------------------ |
| `enabled`             | `boolean`  | `true`                                          | 启用 deep 阶段                    |
| `cron`                | `string`   | `0 3 * * *`                                     | 计划（每天凌晨 3 点）             |
| `limit`               | `number`   | `10`                                            | 每个周期最大提升候选数  |
| `minScore`            | `number`   | `0.8`                                           | 提升所需的最低加权分数 |
| `minRecallCount`      | `number`   | `3`                                             | 最低 recall 次数阈值       |
| `minUniqueQueries`    | `number`   | `3`                                             | 最低不同查询数         |
| `recencyHalfLifeDays` | `number`   | `14`                                            | 新近性分数减半所需天数      |
| `maxAgeDays`          | `number`   | `30`                                            | 可提升的每日笔记最大时长     |
| `sources`             | `string[]` | `["daily","memory","sessions","logs","recall"]` | 数据源                         |

#### Deep 恢复（`phases.deep.recovery`）

| Key                      | Type      | Default | Description                                |
| ------------------------ | --------- | ------- | ------------------------------------------ |
| `enabled`                | `boolean` | `true`  | 启用自动恢复                  |
| `triggerBelowHealth`     | `number`  | `0.35`  | 触发恢复的健康分数阈值 |
| `lookbackDays`           | `number`  | `30`    | 向前查找恢复材料的时间范围 |
| `maxRecoveredCandidates` | `number`  | `20`    | 每次运行最大恢复候选数          |
| `minRecoveryConfidence`  | `number`  | `0.9`   | 恢复候选项的最低置信度 |
| `autoWriteMinConfidence` | `number`  | `0.97`  | 自动写入阈值（跳过人工审核）  |

### REM 阶段（`phases.rem`）

在启用内联存储时，将主题、反思和模式注释写入 `DREAMS.md`。
**不会**写入 `MEMORY.md`。

| Key                  | Type       | Default                     | Description                        |
| -------------------- | ---------- | --------------------------- | ---------------------------------- |
| `enabled`            | `boolean`  | `true`                      | 启用 REM 阶段                   |
| `cron`               | `string`   | `0 5 * * 0`                 | 计划（每周日凌晨 5 点）     |
| `lookbackDays`       | `number`   | `7`                         | 要反思的材料天数     |
| `limit`              | `number`   | `10`                        | 要写入的最大模式或主题数    |
| `minPatternStrength` | `number`   | `0.75`                      | 最低标签共现强度 |
| `sources`            | `string[]` | `["memory","daily","deep"]` | 用于反思的数据源        |

### 执行覆盖

每个阶段都接受一个 `execution` 块。还有一个全局
`execution.defaults` 块，供各阶段继承。

| Key               | Type     | Default      | Description                    |
| ----------------- | -------- | ------------ | ------------------------------ |
| `speed`           | `string` | `"balanced"` | `fast`、`balanced` 或 `slow`  |
| `thinking`        | `string` | `"medium"`   | `low`、`medium` 或 `high`     |
| `budget`          | `string` | `"medium"`   | `cheap`、`medium` 或 `expensive` |
| `model`           | `string` | 未设置        | 覆盖此阶段使用的模型  |
| `maxOutputTokens` | `number` | 未设置        | 限制输出 token              |
| `temperature`     | `number` | 未设置        | 采样温度（0-2）     |
| `timeoutMs`       | `number` | 未设置        | 阶段超时时间（毫秒）  |

### 示例

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            enabled: true,
            timezone: "America/New_York",
            phases: {
              light: { cron: "0 */4 * * *", lookbackDays: 3 },
              deep: { minScore: 0.85, recencyHalfLifeDays: 21 },
              rem: { lookbackDays: 14 },
            },
          },
        },
      },
    },
  },
}
```
