---
read_when:
    - 你正在为一个插件编写测试
    - 你需要来自插件 SDK 的测试工具
    - 你想了解内置插件的契约测试
sidebarTitle: Testing
summary: OpenClaw 插件的测试工具和模式
title: 插件测试
x-i18n:
    generated_at: "2026-04-15T16:36:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2f75bd3f3b5ba34b05786e0dd96d493c36db73a1d258998bf589e27e45c0bd09
    source_path: plugins/sdk-testing.md
    workflow: 15
---

# 插件测试

OpenClaw 插件的测试工具、模式和 lint 强制规则参考。

<Tip>
  **在找测试示例吗？** 操作指南中包含了完整的测试示例：
  [渠道插件测试](/zh-CN/plugins/sdk-channel-plugins#step-6-test) 和
  [提供商插件测试](/zh-CN/plugins/sdk-provider-plugins#step-6-test)。
</Tip>

## 测试工具

**导入：** `openclaw/plugin-sdk/testing`

`testing` 子路径为插件作者导出了一组精简的辅助工具：

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### 可用导出

| 导出                                   | 用途                           |
| -------------------------------------- | ------------------------------ |
| `installCommonResolveTargetErrorCases` | 目标解析错误处理的共享测试用例 |
| `shouldAckReaction`                    | 检查渠道是否应添加确认反应     |
| `removeAckReactionAfterReply`          | 在回复发送后移除确认反应       |

### 类型

`testing` 子路径还会重新导出一些对测试文件有用的类型：

```typescript
import type {
  ChannelAccountSnapshot,
  ChannelGatewayContext,
  OpenClawConfig,
  PluginRuntime,
  RuntimeEnv,
  MockFn,
} from "openclaw/plugin-sdk/testing";
```

## 测试目标解析

使用 `installCommonResolveTargetErrorCases` 为渠道目标解析添加标准错误用例：

```typescript
import { describe } from "vitest";
import { installCommonResolveTargetErrorCases } from "openclaw/plugin-sdk/testing";

describe("my-channel 目标解析", () => {
  installCommonResolveTargetErrorCases({
    resolveTarget: ({ to, mode, allowFrom }) => {
      // 你的渠道目标解析逻辑
      return myChannelResolveTarget({ to, mode, allowFrom });
    },
    implicitAllowFrom: ["user1", "user2"],
  });

  // 添加渠道特定的测试用例
  it("应该解析 @username 目标", () => {
    // ...
  });
});
```

## 测试模式

### 对渠道插件进行单元测试

```typescript
import { describe, it, expect, vi } from "vitest";

describe("my-channel 插件", () => {
  it("应该从配置中解析账户", () => {
    const cfg = {
      channels: {
        "my-channel": {
          token: "test-token",
          allowFrom: ["user1"],
        },
      },
    };

    const account = myPlugin.setup.resolveAccount(cfg, undefined);
    expect(account.token).toBe("test-token");
  });

  it("应该在不实体化密钥的情况下检查账户", () => {
    const cfg = {
      channels: {
        "my-channel": { token: "test-token" },
      },
    };

    const inspection = myPlugin.setup.inspectAccount(cfg, undefined);
    expect(inspection.configured).toBe(true);
    expect(inspection.tokenStatus).toBe("available");
    // 不暴露 token 值
    expect(inspection).not.toHaveProperty("token");
  });
});
```

### 对提供商插件进行单元测试

```typescript
import { describe, it, expect } from "vitest";

describe("my-provider 插件", () => {
  it("应该解析动态模型", () => {
    const model = myProvider.resolveDynamicModel({
      modelId: "custom-model-v2",
      // ... context
    });

    expect(model.id).toBe("custom-model-v2");
    expect(model.provider).toBe("my-provider");
    expect(model.api).toBe("openai-completions");
  });

  it("当 API 密钥可用时应该返回目录", async () => {
    const result = await myProvider.catalog.run({
      resolveProviderApiKey: () => ({ apiKey: "test-key" }),
      // ... context
    });

    expect(result?.provider?.models).toHaveLength(2);
  });
});
```

### Mock 插件运行时

对于使用 `createPluginRuntimeStore` 的代码，请在测试中 mock 运行时：

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>({
  pluginId: "test-plugin",
  errorMessage: "test runtime not set",
});

// 在测试设置中
const mockRuntime = {
  agent: {
    resolveAgentDir: vi.fn().mockReturnValue("/tmp/agent"),
    // ... other mocks
  },
  config: {
    loadConfig: vi.fn(),
    writeConfigFile: vi.fn(),
  },
  // ... other namespaces
} as unknown as PluginRuntime;

store.setRuntime(mockRuntime);

// 测试后
store.clearRuntime();
```

### 使用按实例 stub 进行测试

优先使用按实例 stub，而不是修改原型：

```typescript
// 推荐：按实例 stub
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// 避免：修改原型
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## 契约测试（仓库内插件）

内置插件带有契约测试，用于验证注册归属：

```bash
pnpm test -- src/plugins/contracts/
```

这些测试会断言：

- 哪些插件注册了哪些提供商
- 哪些插件注册了哪些语音提供商
- 注册形状是否正确
- 运行时契约是否合规

### 运行范围化测试

针对某个特定插件：

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

仅运行契约测试：

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## Lint 强制规则（仓库内插件）

`pnpm check` 会对仓库内插件强制执行三条规则：

1. **禁止使用单体根导入** —— 不允许使用 `openclaw/plugin-sdk` 根 barrel
2. **禁止直接导入 `src/`** —— 插件不能直接导入 `../../src/`
3. **禁止自导入** —— 插件不能导入它们自己的 `plugin-sdk/<name>` 子路径

外部插件不受这些 lint 规则约束，但仍建议遵循相同模式。

## 测试配置

OpenClaw 使用带有 V8 覆盖率阈值的 Vitest。对于插件测试：

```bash
# 运行所有测试
pnpm test

# 运行特定插件测试
pnpm test -- <bundled-plugin-root>/my-channel/src/channel.test.ts

# 使用特定测试名称过滤运行
pnpm test -- <bundled-plugin-root>/my-channel/ -t "resolves account"

# 运行并生成覆盖率
pnpm test:coverage
```

如果本地运行导致内存压力：

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## 相关内容

- [SDK 概览](/zh-CN/plugins/sdk-overview) -- 导入约定
- [渠道插件 SDK](/zh-CN/plugins/sdk-channel-plugins) -- 渠道插件接口
- [提供商插件 SDK](/zh-CN/plugins/sdk-provider-plugins) -- 提供商插件钩子
- [构建插件](/zh-CN/plugins/building-plugins) -- 入门指南
