---
read_when:
    - 查找公开发布渠道定义
    - 查找版本命名和发布节奏
summary: 公开发布渠道、版本命名和发布节奏
title: 发布策略
x-i18n:
    generated_at: "2026-04-12T22:00:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: dffc1ee5fdbb20bd1bf4b3f817d497fc0d87f70ed6c669d324fea66dc01d0b0b
    source_path: reference/RELEASING.md
    workflow: 15
---

# 发布策略

OpenClaw 有三个公开发布通道：

- stable：带标签的发布版本，默认发布到 npm `beta`，或在明确要求时发布到 npm `latest`
- beta：预发布标签，发布到 npm `beta`
- dev：持续更新的 `main` 头部版本

## 版本命名

- Stable 发布版本：`YYYY.M.D`
  - Git 标签：`vYYYY.M.D`
- Stable 修正版发布版本：`YYYY.M.D-N`
  - Git 标签：`vYYYY.M.D-N`
- Beta 预发布版本：`YYYY.M.D-beta.N`
  - Git 标签：`vYYYY.M.D-beta.N`
- 月份和日期不要补零
- `latest` 表示当前已提升为正式版的 stable npm 发布版本
- `beta` 表示当前 beta 安装目标
- Stable 和 stable 修正版发布默认发布到 npm `beta`；发布操作人员可以明确指定目标为 `latest`，或者稍后再提升一个经过验证的 beta 构建版本
- 每个 OpenClaw 发布都会同时交付 npm 包和 macOS 应用

## 发布节奏

- 发布采用 beta 优先流程
- 只有在最新 beta 通过验证后，才会跟进 stable
- 详细的发布流程、审批、凭证和恢复说明仅供维护者查看

## 发布前检查

- 在运行 `pnpm release:check` 之前先运行 `pnpm build && pnpm ui:build`，以便为打包验证步骤准备预期的 `dist/*` 发布产物和 Control UI bundle
- 每次带标签发布前都要运行 `pnpm release:check`
- 现在，发布检查会在单独的手动工作流中运行：
  `OpenClaw Release Checks`
- 这样拆分是有意为之：让真正的 npm 发布路径保持简短、确定且聚焦产物，同时把较慢的实时检查放在独立通道中，避免其拖慢或阻塞发布
- 发布检查必须从 `main` 工作流引用发起，这样工作流逻辑和密钥才能保持为规范来源
- 该工作流接受现有发布标签，或当前完整的 40 字符 `main` 提交 SHA
- 在提交 SHA 模式下，它只接受当前 `origin/main` 的 HEAD；如果要验证更早的发布提交，请使用发布标签
- `OpenClaw NPM Release` 的仅验证预检查也接受当前完整的 40 字符 `main` 提交 SHA，而不要求已推送的标签
- 该 SHA 路径仅用于验证，不能提升为真实发布
- 在 SHA 模式下，工作流仅为了包元数据检查而合成 `v<package.json version>`；真实发布仍然需要真实的发布标签
- 这两个工作流都将真实发布和提升路径保留在 GitHub 托管的运行器上，而不修改状态的验证路径则可以使用更大的 Blacksmith Linux 运行器
- 该工作流会运行
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  并使用 `OPENAI_API_KEY` 和 `ANTHROPIC_API_KEY` 两个工作流密钥
- npm 发布预检查不再等待单独的发布检查通道
- 在批准前运行 `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  （或匹配的 beta/修正标签）
- npm 发布后，运行
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  （或匹配的 beta/修正版本），以在一个全新的临时前缀中验证已发布的注册表安装路径
- 维护者发布自动化现在采用“先预检查，再提升”：
  - 真实的 npm 发布必须通过成功的 npm `preflight_run_id`
  - stable npm 发布默认目标为 `beta`
  - stable npm 发布可以通过工作流输入明确指定目标为 `latest`
  - stable npm 从 `beta` 提升到 `latest` 仍然作为受信任的 `OpenClaw NPM Release` 工作流中的显式手动模式提供
  - 该提升模式仍然需要 `npm-release` 环境中的有效 `NPM_TOKEN`，因为 npm `dist-tag` 管理独立于受信任发布
  - 公开的 `macOS Release` 仅用于验证
  - 真实的私有 mac 发布必须通过成功的私有 mac
    `preflight_run_id` 和 `validate_run_id`
  - 真实发布路径会提升已准备好的产物，而不是再次重新构建它们
- 对于像 `YYYY.M.D-N` 这样的 stable 修正版发布，发布后验证器还会检查从 `YYYY.M.D` 到 `YYYY.M.D-N` 的同一临时前缀升级路径，这样发布修正就不会悄悄让较旧的全局安装仍停留在基础 stable 载荷上
- npm 发布预检查默认失败关闭，除非 tarball 同时包含
  `dist/control-ui/index.html` 和非空的 `dist/control-ui/assets/` 载荷，以避免再次发布一个空的浏览器仪表板
- 如果发布工作涉及 CI 规划、扩展时间清单或扩展测试矩阵，请在批准前根据 `.github/workflows/ci.yml` 重新生成并审查由规划器负责的 `checks-node-extensions` 工作流矩阵输出，以确保发布说明不会描述过时的 CI 布局
- Stable macOS 发布就绪状态还包括更新器相关表面：
  - GitHub 发布最终必须包含打包后的 `.zip`、`.dmg` 和 `.dSYM.zip`
  - 发布后，`main` 上的 `appcast.xml` 必须指向新的 stable zip
  - 打包后的应用必须保持非调试 bundle id、非空 Sparkle feed URL，以及不低于该发布版本规范 Sparkle 构建下限的 `CFBundleVersion`

## NPM 工作流输入

`OpenClaw NPM Release` 接受以下由操作人员控制的输入：

- `tag`：必填的发布标签，例如 `v2026.4.2`、`v2026.4.2-1` 或
  `v2026.4.2-beta.1`；当 `preflight_only=true` 时，它也可以是当前完整的
  40 字符 `main` 提交 SHA，用于仅验证的预检查
- `preflight_only`：`true` 表示仅验证/构建/打包，`false` 表示真实发布路径
- `preflight_run_id`：真实发布路径必填，这样工作流就会复用成功预检查运行中准备好的 tarball
- `npm_dist_tag`：发布路径的 npm 目标标签；默认为 `beta`
- `promote_beta_to_latest`：`true` 表示跳过发布，并将已发布的 stable `beta` 构建移到 `latest`

`OpenClaw Release Checks` 接受以下由操作人员控制的输入：

- `ref`：用于验证的现有发布标签，或当前完整的 40 字符 `main` 提交
  SHA

规则：

- Stable 和修正标签可以发布到 `beta` 或 `latest`
- Beta 预发布标签只能发布到 `beta`
- 仅当 `preflight_only=true` 时才允许输入完整提交 SHA
- 发布检查的提交 SHA 模式也要求是当前 `origin/main` HEAD
- 真实发布路径必须使用与预检查相同的 `npm_dist_tag`；工作流会在继续发布前验证该元数据
- 提升模式必须使用 stable 或修正标签、`preflight_only=false`、
  空的 `preflight_run_id`，以及 `npm_dist_tag=beta`
- 提升模式还要求 `npm-release`
  环境中有有效的 `NPM_TOKEN`，因为 `npm dist-tag add` 仍然需要常规 npm 身份验证

## Stable npm 发布顺序

在切一个 stable npm 发布时：

1. 运行 `OpenClaw NPM Release`，设置 `preflight_only=true`
   - 在标签尚不存在时，你可以使用当前完整的 `main` 提交 SHA，对预检查工作流执行一次仅验证的试运行
2. 在常规的 beta 优先流程中选择 `npm_dist_tag=beta`，只有在你有意直接发布 stable 时才选择 `latest`
3. 单独运行 `OpenClaw Release Checks`，使用相同标签，或者在你希望获得实时提示缓存覆盖时使用当前完整的 `main` 提交 SHA
   - 这样单独拆分是有意为之，因此在不重新把长时间运行或不稳定检查耦合回发布工作流的前提下，实时覆盖仍然可用
4. 保存成功的 `preflight_run_id`
5. 再次运行 `OpenClaw NPM Release`，设置 `preflight_only=false`，并使用相同的
   `tag`、相同的 `npm_dist_tag` 以及已保存的 `preflight_run_id`
6. 如果该发布先落在 `beta`，之后当你想把这个已发布的构建移动到 `latest` 时，使用相同的 stable `tag`、`promote_beta_to_latest=true`、`preflight_only=false`、空的 `preflight_run_id` 和 `npm_dist_tag=beta` 再运行一次 `OpenClaw NPM Release`

提升模式仍然需要 `npm-release` 环境审批，以及该环境中的有效 `NPM_TOKEN`。

这样既能让直接发布路径保持文档化，也能让 beta 优先的提升路径对操作人员清晰可见。

## 公开参考

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

维护者会使用私有发布文档
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
作为实际运行手册。
