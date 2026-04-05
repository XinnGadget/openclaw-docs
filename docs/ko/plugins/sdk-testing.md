---
read_when:
    - plugin 테스트를 작성할 때
    - plugin SDK의 테스트 유틸리티가 필요할 때
    - 번들 plugins의 계약 테스트를 이해하려고 할 때
sidebarTitle: Testing
summary: OpenClaw plugins를 위한 테스트 유틸리티와 패턴
title: Plugin 테스트
x-i18n:
    generated_at: "2026-04-05T12:50:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2e95ed58ed180feadad17bb5138bd09e3b45f1f3ecdff4e2fba4874bb80099fe
    source_path: plugins/sdk-testing.md
    workflow: 15
---

# Plugin 테스트

OpenClaw
plugins를 위한 테스트 유틸리티, 패턴 및 lint 강제 적용에 대한 참조입니다.

<Tip>
  **테스트 예제가 필요하신가요?** 단계별 가이드에는 실제 테스트 예제가 포함되어 있습니다:
  [Channel plugin tests](/plugins/sdk-channel-plugins#step-6-test) 및
  [Provider plugin tests](/plugins/sdk-provider-plugins#step-6-test).
</Tip>

## 테스트 유틸리티

**import:** `openclaw/plugin-sdk/testing`

testing 하위 경로는 plugin 작성자를 위한 좁은 범위의 헬퍼 세트를 내보냅니다:

```typescript
import {
  installCommonResolveTargetErrorCases,
  shouldAckReaction,
  removeAckReactionAfterReply,
} from "openclaw/plugin-sdk/testing";
```

### 사용 가능한 export

| Export | 용도 |
| -------------------------------------- | ------------------------------------------------------ |
| `installCommonResolveTargetErrorCases` | 대상 해석 오류 처리를 위한 공통 테스트 케이스 |
| `shouldAckReaction`                    | 채널이 ack reaction을 추가해야 하는지 확인 |
| `removeAckReactionAfterReply`          | 답장 전달 후 ack reaction 제거 |

### 타입

testing 하위 경로는 테스트 파일에 유용한 타입도 다시 export합니다:

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

## 대상 해석 테스트

채널 대상 해석에 대한 표준 오류 케이스를 추가하려면
`installCommonResolveTargetErrorCases`를 사용하세요:

```typescript
import { describe } from "vitest";
import { installCommonResolveTargetErrorCases } from "openclaw/plugin-sdk/testing";

describe("my-channel target resolution", () => {
  installCommonResolveTargetErrorCases({
    resolveTarget: ({ to, mode, allowFrom }) => {
      // 해당 채널의 대상 해석 로직
      return myChannelResolveTarget({ to, mode, allowFrom });
    },
    implicitAllowFrom: ["user1", "user2"],
  });

  // 채널별 테스트 케이스 추가
  it("should resolve @username targets", () => {
    // ...
  });
});
```

## 테스트 패턴

### 채널 plugin 단위 테스트

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
    // token 값은 노출되지 않음
    expect(inspection).not.toHaveProperty("token");
  });
});
```

### provider plugin 단위 테스트

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

### plugin 런타임 mocking

`createPluginRuntimeStore`를 사용하는 코드의 경우 테스트에서 런타임을 mock하세요:

```typescript
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
import type { PluginRuntime } from "openclaw/plugin-sdk/runtime-store";

const store = createPluginRuntimeStore<PluginRuntime>("test runtime not set");

// 테스트 설정에서
const mockRuntime = {
  agent: {
    resolveAgentDir: vi.fn().mockReturnValue("/tmp/agent"),
    // ... 다른 mock
  },
  config: {
    loadConfig: vi.fn(),
    writeConfigFile: vi.fn(),
  },
  // ... 다른 네임스페이스
} as unknown as PluginRuntime;

store.setRuntime(mockRuntime);

// 테스트 후
store.clearRuntime();
```

### 인스턴스별 stub를 사용한 테스트

프로토타입 변형보다 인스턴스별 stub를 우선하세요:

```typescript
// 권장: 인스턴스별 stub
const client = new MyChannelClient();
client.sendMessage = vi.fn().mockResolvedValue({ id: "msg-1" });

// 피할 것: 프로토타입 변형
// MyChannelClient.prototype.sendMessage = vi.fn();
```

## 계약 테스트(리포지토리 내부 plugins)

번들 plugins에는 등록 소유권을 검증하는 계약 테스트가 있습니다:

```bash
pnpm test -- src/plugins/contracts/
```

이 테스트는 다음을 검증합니다:

- 어떤 plugins가 어떤 provider를 등록하는지
- 어떤 plugins가 어떤 speech provider를 등록하는지
- 등록 형태의 정확성
- 런타임 계약 준수

### 범위 지정 테스트 실행

특정 plugin에 대해:

```bash
pnpm test -- <bundled-plugin-root>/my-channel/
```

계약 테스트만 실행:

```bash
pnpm test -- src/plugins/contracts/shape.contract.test.ts
pnpm test -- src/plugins/contracts/auth.contract.test.ts
pnpm test -- src/plugins/contracts/runtime.contract.test.ts
```

## lint 강제 적용(리포지토리 내부 plugins)

리포지토리 내부 plugins에는 `pnpm check`를 통해 세 가지 규칙이 강제됩니다:

1. **단일 루트 import 금지** -- `openclaw/plugin-sdk` 루트 barrel은 거부됨
2. **직접 `src/` import 금지** -- plugins는 `../../src/`를 직접 import할 수 없음
3. **self-import 금지** -- plugins는 자신의 `plugin-sdk/<name>` 하위 경로를 import할 수 없음

외부 plugins에는 이 lint 규칙이 적용되지 않지만, 동일한
패턴을 따르는 것이 권장됩니다.

## 테스트 구성

OpenClaw는 V8 커버리지 임계값이 있는 Vitest를 사용합니다. plugin 테스트의 경우:

```bash
# 모든 테스트 실행
pnpm test

# 특정 plugin 테스트 실행
pnpm test -- <bundled-plugin-root>/my-channel/src/channel.test.ts

# 특정 테스트 이름 필터와 함께 실행
pnpm test -- <bundled-plugin-root>/my-channel/ -t "resolves account"

# 커버리지와 함께 실행
pnpm test:coverage
```

로컬 실행에서 메모리 압박이 발생한다면:

```bash
OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test
```

## 관련

- [SDK Overview](/plugins/sdk-overview) -- import 규칙
- [SDK Channel Plugins](/plugins/sdk-channel-plugins) -- 채널 plugin 인터페이스
- [SDK Provider Plugins](/plugins/sdk-provider-plugins) -- provider plugin hook
- [Building Plugins](/plugins/building-plugins) -- 시작 가이드
