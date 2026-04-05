---
x-i18n:
    generated_at: "2026-04-05T12:34:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: adff26fa8858af2759b231ea48bfc01f89c110cd9b3774a8f783e282c16f77fb
    source_path: .i18n/README.md
    workflow: 15
---

# OpenClaw 文档 i18n 资源

此文件夹用于存放源文档仓库的翻译配置。

生成的语言目录树和实时翻译记忆现在位于发布仓库中：

- 仓库：`openclaw/docs`
- 本地检出路径：`~/Projects/openclaw-docs`

## 事实来源

- 英文文档在 `openclaw/openclaw` 中编写。
- 源文档目录树位于 `docs/` 下。
- 源仓库不再保留已提交的生成语言目录树，例如 `docs/zh-CN/**`、`docs/ja-JP/**`、`docs/es/**`、`docs/pt-BR/**`、`docs/ko/**`、`docs/de/**`、`docs/fr/**` 或 `docs/ar/**`。

## 端到端流程

1. 在 `openclaw/openclaw` 中编辑英文文档。
2. 推送到 `main`。
3. `openclaw/openclaw/.github/workflows/docs-sync-publish.yml` 会将文档目录树镜像到 `openclaw/docs`。
4. 同步脚本会重写发布仓库中的 `docs/docs.json`，以便即使这些内容不再提交到源仓库，生成的语言选择器区块仍然存在于发布仓库中。
5. `openclaw/docs/.github/workflows/translate-zh-cn.yml` 会每天一次、按需以及在源仓库发布分发后刷新 `docs/zh-CN/**`。
6. `openclaw/docs/.github/workflows/translate-ja-jp.yml` 会以相同方式刷新 `docs/ja-JP/**`。
7. `openclaw/docs/.github/workflows/translate-es.yml`、`translate-pt-br.yml`、`translate-ko.yml`、`translate-de.yml`、`translate-fr.yml` 和 `translate-ar.yml` 会以相同方式刷新 `docs/es/**`、`docs/pt-BR/**`、`docs/ko/**`、`docs/de/**`、`docs/fr/**` 和 `docs/ar/**`。

## 为什么要这样拆分

- 让生成的语言输出不进入主产品仓库。
- 让 Mintlify 使用单一的已发布文档目录树。
- 通过让发布仓库持有生成的语言目录树，保留内置语言切换器。

## 此文件夹中的文件

- `glossary.<lang>.json` — 用作提示指导的首选术语映射。
- `ar-navigation.json`、`de-navigation.json`、`es-navigation.json`、`fr-navigation.json`、`ja-navigation.json`、`ko-navigation.json`、`pt-BR-navigation.json`、`zh-Hans-navigation.json` — 在同步期间重新插入到发布仓库中的 Mintlify 语言选择器区块。
- `<lang>.tm.jsonl` — 以工作流 + 模型 + 文本哈希为键的翻译记忆。

在此仓库中，生成的语言 TM 文件，例如 `docs/.i18n/zh-CN.tm.jsonl`、`docs/.i18n/ja-JP.tm.jsonl`、`docs/.i18n/es.tm.jsonl`、`docs/.i18n/pt-BR.tm.jsonl`、`docs/.i18n/ko.tm.jsonl`、`docs/.i18n/de.tm.jsonl`、`docs/.i18n/fr.tm.jsonl` 和 `docs/.i18n/ar.tm.jsonl`，已明确不再提交。

## 术语表格式

`glossary.<lang>.json` 是一个条目数组：

```json
{
  "source": "troubleshooting",
  "target": "故障排除"
}
```

字段：

- `source`：优先使用的英文（或源）短语。
- `target`：首选的翻译输出。

## 翻译机制

- `scripts/docs-i18n` 仍然负责生成翻译。
- 文档模式会将 `x-i18n.source_hash` 写入每个已翻译页面。
- 每个发布工作流都会通过比较当前英文源哈希与已存储的语言 `x-i18n.source_hash` 来预先计算待处理文件列表。
- 如果待处理数量为 `0`，则会完全跳过高开销的翻译步骤。
- 如果存在待处理文件，工作流只会翻译这些文件。
- 发布工作流会重试模型格式的瞬时失败，但未更改的文件会继续被跳过，因为每次重试都会运行相同的哈希检查。
- 源仓库还会在已发布的 GitHub Release 之后分发 zh-CN、ja-JP、es、pt-BR、ko、de、fr 和 ar 刷新任务，这样发布文档就不必等到每日 cron 才能同步更新。

## 操作说明

- 同步元数据会写入发布仓库中的 `.openclaw-sync/source.json`。
- 源仓库密钥：`OPENCLAW_DOCS_SYNC_TOKEN`
- 发布仓库密钥：`OPENCLAW_DOCS_I18N_OPENAI_API_KEY`
- 如果语言输出看起来已过时，请先检查 `openclaw/docs` 中对应的 `Translate <locale>` 工作流。
