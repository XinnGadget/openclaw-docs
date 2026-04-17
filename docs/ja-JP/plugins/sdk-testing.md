---
read_when:
    - あなたはPluginのテストを書いています
    - Plugin SDKのテストユーティリティが必要です
    - バンドルされたPluginのコントラクトテストを理解したい場合
sidebarTitle: Testing
summary: OpenClaw Pluginのテストユーティリティとパターン
title: Pluginのテスト
x-i18n:
    generated_at: "2026-04-15T19:41:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2f75bd3f3b5ba34b05786e0dd96d493c36db73a1d258998bf589e27e45c0bd09
    source_path: plugins/sdk-testing.md
    workflow: 15
---

# Pluginのテスト

OpenClaw Plugin向けのテストユーティリティ、パターン、およびlint適用に関するリファレンスです。

<Tip>
  **テスト例を探していますか？** ハウツーガイドには実際のテスト例が含まれています:
  [Channel Pluginのテスト](/ja-JP/plugins/sdk-channel-plugins#step-6-test) と
  [Provider Pluginのテスト](/ja-JP/plugins/sdk-provider-plugins#step-6-test)。
</Tip>

## テストユーティリティ

**インポート:** `openclaw/plugin-sdk/testing`

このtestingサブパスは、Plugin作成者向けに絞り込まれた一連のヘルパーをエクスポートします:

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### 利用可能なエクスポート

| Export                                 | 用途                                   |
| -------------------------------------- | -------------------------------------- |
| `installCommonResolveTargetErrorCases` | ターゲット解決のエラーハンドリング向け共有テストケース |
| `shouldAckReaction`                    | チャンネルがackリアクションを追加すべきかどうかを確認 |
| `removeAckReactionAfterReply`          | reply配信後にackリアクションを削除               |

### 型

testingサブパスは、テストファイルで役立つ型も再エクスポートします:

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

## ターゲット解決のテスト

チャンネルのターゲット解決に対する標準的なエラーケースを追加するには、`installCommonResolveTargetErrorCases` を使用します:

```typescript
import { describe } from "vitest";
import { installCommonResolveTargetErrorCases } from "openclaw/plugin-sdk/testing";

describe("my-channel target resolution", () => {
  installCommonResolveTargetErrorCases({
    resolveTarget: ({ to, mode, allowFrom }) => {
      // Your channel's target resolution logic
      return myChannelResolveTarget({ to, mode, allowFrom });
    },
    implicitAllowFrom: ["user1", "user2"],
  });

  // Add channel-specific test cases
  it("should resolve @username targets", () => {
    // ...
  });
});
```

## テストパターン

### Channel Pluginのユニットテスト

```typescript
import { describe, it, expect, vi } from "vitest";

describe("my-channel plugin", () => {
  it("should resolve account from config", () => {
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

  it("should inspect account without materializing secrets", () => {
    const cfg = {
      channels: {
        "my-channel": { token: "test-token" },
      },
    };

    const inspection = myPlugin.setup.inspectAccount(cfg, undefined);
    expect(inspection.configured).toBe(true);
    expect(inspection.tokenStatus).toBe("available");
    // No token value exposed
    expect(inspection).not.toHaveProperty("token");
  });
});
```

### Provider Pluginのユニットテスト

```typescript
import { describe, it, expect } from "vitest";

describe("my-provider plugin", () => {
  it("should resolve dynamic models", () => {
    const model = myProvider.resolveDynamicModel({
      modelId: "custom-model-v2",
      // ... context
    });

    expect(model.id).toBe("custom-model-v2");
    expect(model.provider).toBe("my-provider");
    expect(model.api).toBe("openai-completions");
  });

  it("should return catalog when API key is available", async () => {
    const result = await myProvider.catalog.run({
      resolveProviderApiKey: () => ({ apiKey: "test-key" }),
      // ... context
    });

    expect(result?.provider?.models).toHaveLength(2);
  });
});
```

### Pluginランタイムのモック

`createPluginRuntimeStore` を使用するコードでは、テスト内でランタイムをモックします:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>({
  pluginId: "test-plugin",
  errorMessage: "test runtime not set",
});

// In test setup
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

// After tests
store.clearRuntime();
```

### インスタンスごとのスタブを使ったテスト

プロトタイプの変更よりも、インスタンスごとのスタブを優先してください:

```typescript
// Preferred: per-instance stub
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// Avoid: prototype mutation
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## コントラクトテスト（リポジトリ内Plugin）

バンドルされたPluginには、登録の所有権を検証するコントラクトテストがあります:

```bash
pnpm test -- src/plugins/contracts/
```

これらのテストでは、次の内容を検証します:

- どのPluginがどのProviderを登録するか
- どのPluginがどのspeech providerを登録するか
- 登録形状の正しさ
- ランタイムのコントラクト準拠

### スコープ付きテストの実行

特定のPluginに対して:

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

コントラクトテストのみを実行する場合:

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## lint適用（リポジトリ内Plugin）

リポジトリ内Pluginに対しては、`pnpm check` により3つのルールが適用されます:

1. **モノリシックなルートインポートの禁止** -- `openclaw/plugin-sdk` のルートbarrelは拒否されます
2. **直接の `src/` インポートの禁止** -- Pluginは `../../src/` を直接インポートできません
3. **自己インポートの禁止** -- Pluginは自身の `plugin-sdk/<name>` サブパスをインポートできません

外部Pluginはこれらのlintルールの対象ではありませんが、同じパターンに従うことを推奨します。

## テスト設定

OpenClawは、V8カバレッジしきい値付きのVitestを使用しています。Pluginテストでは次を使用します:

```bash
# Run all tests
pnpm test

# Run specific plugin tests
pnpm test -- <bundled-plugin-root>/my-channel/src/channel.test.ts

# Run with a specific test name filter
pnpm test -- <bundled-plugin-root>/my-channel/ -t "resolves account"

# Run with coverage
pnpm test:coverage
```

ローカル実行でメモリ負荷が発生する場合:

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## 関連

- [SDK Overview](/ja-JP/plugins/sdk-overview) -- インポート規約
- [SDK Channel Plugins](/ja-JP/plugins/sdk-channel-plugins) -- Channel Pluginインターフェース
- [SDK Provider Plugins](/ja-JP/plugins/sdk-provider-plugins) -- Provider Pluginフック
- [Building Plugins](/ja-JP/plugins/building-plugins) -- はじめにガイド
