---
read_when:
    - definePluginEntry 또는 defineChannelPluginEntry의 정확한 타입 시그니처가 필요한 경우
    - 등록 모드(full vs setup vs CLI metadata)를 이해하려는 경우
    - 엔트리포인트 옵션을 찾는 경우
sidebarTitle: Entry Points
summary: definePluginEntry, defineChannelPluginEntry, defineSetupPluginEntry 참조
title: Plugin 엔트리포인트
x-i18n:
    generated_at: "2026-04-05T12:50:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 799dbfe71e681dd8ba929a7a631dfe745c3c5c69530126fea2f9c137b120f51f
    source_path: plugins/sdk-entrypoints.md
    workflow: 15
---

# Plugin 엔트리포인트

모든 plugin은 기본 엔트리 객체를 내보냅니다. SDK는 이를 만들기 위한 세 가지 도우미를 제공합니다.

<Tip>
  **단계별 가이드를 찾고 있나요?** [Channel Plugins](/plugins/sdk-channel-plugins)
  또는 [Provider Plugins](/plugins/sdk-provider-plugins)의 단계별 가이드를 참조하세요.
</Tip>

## `definePluginEntry`

**Import:** `openclaw/plugin-sdk/plugin-entry`

provider plugins, tool plugins, hook plugins 및 메시징 채널이 **아닌**
모든 것에 사용합니다.

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Short summary",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
  },
});
```

| 필드 | 타입 | 필수 | 기본값 |
| -------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id` | `string` | 예 | — |
| `name` | `string` | 예 | — |
| `description` | `string` | 예 | — |
| `kind` | `string` | 아니요 | — |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | 아니요 | 빈 객체 스키마 |
| `register` | `(api: OpenClawPluginApi) => void` | 예 | — |

- `id`는 `openclaw.plugin.json` manifest와 일치해야 합니다.
- `kind`는 `"memory"` 또는 `"context-engine"` 같은 배타적 슬롯에 사용됩니다.
- `configSchema`는 지연 평가를 위한 함수일 수 있습니다.
- OpenClaw는 첫 접근 시 해당 스키마를 해석하고 메모이즈하므로, 비용이 큰 스키마 빌더도 한 번만 실행됩니다.

## `defineChannelPluginEntry`

**Import:** `openclaw/plugin-sdk/channel-core`

채널 전용 wiring과 함께 `definePluginEntry`를 감쌉니다. 자동으로
`api.registerChannel({ plugin })`를 호출하고, 선택적 root-help CLI metadata seam을 노출하며, 등록 모드에 따라 `registerFull`을 제어합니다.

```typescript
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineChannelPluginEntry({
  id: "my-channel",
  name: "My Channel",
  description: "Short summary",
  plugin: myChannelPlugin,
  setRuntime: setMyRuntime,
  registerCliMetadata(api) {
    api.registerCli(/* ... */);
  },
  registerFull(api) {
    api.registerGatewayMethod(/* ... */);
  },
});
```

| 필드 | 타입 | 필수 | 기본값 |
| --------------------- | ---------------------------------------------------------------- | -------- | ------------------- |
| `id` | `string` | 예 | — |
| `name` | `string` | 예 | — |
| `description` | `string` | 예 | — |
| `plugin` | `ChannelPlugin` | 예 | — |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | 아니요 | 빈 객체 스키마 |
| `setRuntime` | `(runtime: PluginRuntime) => void` | 아니요 | — |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void` | 아니요 | — |
| `registerFull` | `(api: OpenClawPluginApi) => void` | 아니요 | — |

- `setRuntime`은 등록 중 호출되므로 런타임 참조를 저장할 수 있습니다(보통 `createPluginRuntimeStore` 사용). CLI metadata 캡처 중에는 건너뜁니다.
- `registerCliMetadata`는 `api.registrationMode === "cli-metadata"`와 `api.registrationMode === "full"` 모두에서 실행됩니다.
  이를 채널 소유 CLI descriptor의 정식 위치로 사용하면 root help는 비활성 로딩 상태를 유지하면서, 일반 CLI 명령 등록은 전체 plugin 로드와 호환되게 할 수 있습니다.
- `registerFull`은 `api.registrationMode === "full"`일 때만 실행됩니다. setup-only 로딩에서는 건너뜁니다.
- `definePluginEntry`와 마찬가지로 `configSchema`는 지연 팩토리일 수 있으며 OpenClaw는 첫 접근 시 해석된 스키마를 메모이즈합니다.
- plugin 소유 root CLI 명령의 경우, 명령이 root CLI parse tree에서 사라지지 않으면서 lazy-load 상태를 유지하길 원하면 `api.registerCli(..., { descriptors: [...] })`를 우선 사용하세요. 채널 plugins의 경우, 해당 descriptors는 `registerCliMetadata(...)`에서 등록하고 `registerFull(...)`은 런타임 전용 작업에 집중시키는 것이 좋습니다.
- `registerFull(...)`이 gateway RPC 메서드도 등록한다면, plugin 전용 접두사 아래에 유지하세요. 예약된 핵심 admin namespace (`config.*`, `exec.approvals.*`, `wizard.*`, `update.*`)는 항상 `operator.admin`으로 강제됩니다.

## `defineSetupPluginEntry`

**Import:** `openclaw/plugin-sdk/channel-core`

가벼운 `setup-entry.ts` 파일용입니다. 런타임이나 CLI wiring 없이 `{ plugin }`만 반환합니다.

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

OpenClaw는 채널이 비활성, 미구성 또는 지연 로딩이 활성화된 경우 전체 엔트리 대신 이를 로드합니다. 이것이 중요한 시점은 [Setup and Config](/plugins/sdk-setup#setup-entry)를 참조하세요.

실제로는 `defineSetupPluginEntry(...)`를 다음과 같은 좁은 setup helper 패밀리와 함께 사용하세요.

- import-safe setup patch adapter, lookup-note 출력, `promptResolvedAllowFrom`, `splitSetupEntries`, delegated setup proxy 같은 런타임 안전 setup 도우미를 위한 `openclaw/plugin-sdk/setup-runtime`
- 선택적 설치 setup 표면을 위한 `openclaw/plugin-sdk/channel-setup`
- setup/install CLI/archive/docs 도우미를 위한 `openclaw/plugin-sdk/setup-tools`

무거운 SDK, CLI 등록, 장기 실행 런타임 서비스는 full entry에 두세요.

## 등록 모드

`api.registrationMode`는 plugin이 어떻게 로드되었는지를 알려줍니다.

| 모드 | 시점 | 등록할 내용 |
| ----------------- | --------------------------------- | ----------------------------------------------------------------------------------------- |
| `"full"` | 일반 gateway 시작 | 모든 것 |
| `"setup-only"` | 비활성/미구성 채널 | 채널 등록만 |
| `"setup-runtime"` | 런타임을 사용할 수 있는 setup 흐름 | 채널 등록 + full entry가 로드되기 전에 필요한 가벼운 런타임만 |
| `"cli-metadata"` | root help / CLI metadata 캡처 | CLI descriptors만 |

`defineChannelPluginEntry`는 이 분리를 자동으로 처리합니다. 채널에 대해 `definePluginEntry`를 직접 사용하는 경우, 직접 모드를 확인하세요.

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // 무거운 런타임 전용 등록
  api.registerService(/* ... */);
}
```

`"setup-runtime"`은 full bundled 채널 런타임에 다시 진입하지 않으면서 setup-only 시작 표면이 존재해야 하는 구간으로 취급하세요.
잘 맞는 항목은 채널 등록, setup-safe HTTP routes, setup-safe gateway methods, delegated setup helpers입니다. 무거운 백그라운드 서비스, CLI registrars, provider/client SDK bootstrap은 여전히 `"full"`에 속합니다.

특히 CLI registrars의 경우:

- registrar가 하나 이상의 root 명령을 소유하고, 첫 호출 시 OpenClaw가 실제 CLI 모듈을 lazy-load하기를 원한다면 `descriptors`를 사용하세요
- 해당 descriptors가 registrar가 노출하는 모든 top-level 명령 root를 포함하도록 하세요
- 즉시 로드되는 호환성 경로에는 `commands`만 사용하세요

## Plugin 형태

OpenClaw는 로드된 plugins를 등록 동작에 따라 분류합니다.

| 형태 | 설명 |
| --------------------- | -------------------------------------------------- |
| **plain-capability** | 하나의 capability 유형만 가짐(예: provider 전용) |
| **hybrid-capability** | 여러 capability 유형을 가짐(예: provider + speech) |
| **hook-only** | capabilities 없이 hooks만 가짐 |
| **non-capability** | capabilities는 없고 tools/commands/services만 가짐 |

plugin 형태를 보려면 `openclaw plugins inspect <id>`를 사용하세요.

## 관련 문서

- [SDK 개요](/plugins/sdk-overview) — 등록 API 및 subpath 참조
- [런타임 도우미](/plugins/sdk-runtime) — `api.runtime` 및 `createPluginRuntimeStore`
- [Setup and Config](/plugins/sdk-setup) — manifest, setup entry, 지연 로딩
- [Channel Plugins](/plugins/sdk-channel-plugins) — `ChannelPlugin` 객체 빌드
- [Provider Plugins](/plugins/sdk-provider-plugins) — provider 등록 및 hooks
