---
read_when:
    - plugin에 setup wizard를 추가하는 경우
    - '`setup-entry.ts`와 `index.ts`의 차이를 이해해야 하는 경우'
    - plugin config 스키마 또는 `package.json`의 openclaw 메타데이터를 정의하는 경우
sidebarTitle: Setup and Config
summary: setup wizard, `setup-entry.ts`, config 스키마, `package.json` 메타데이터
title: Plugin Setup 및 Config
x-i18n:
    generated_at: "2026-04-05T12:51:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 68fda27be1c89ea6ba906833113e9190ddd0ab358eb024262fb806746d54f7bf
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Plugin Setup 및 Config

plugin 패키징(`package.json` 메타데이터), manifest
(`openclaw.plugin.json`), setup 엔트리, config 스키마에 대한 참조 문서입니다.

<Tip>
  **단계별 가이드를 찾고 있나요?** how-to 가이드는 패키징을 맥락 속에서 다룹니다:
  [Channel Plugins](/plugins/sdk-channel-plugins#step-1-package-and-manifest) 및
  [Provider Plugins](/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## 패키지 메타데이터

`package.json`에는 plugin 시스템에 plugin이 무엇을 제공하는지 알려주는 `openclaw` 필드가 필요합니다.

**Channel plugin:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Short description of the channel."
    }
  }
}
```

**Provider plugin / ClawHub 게시 기본형:**

```json openclaw-clawhub-package.json
{
  "name": "@myorg/openclaw-my-plugin",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "compat": {
      "pluginApi": ">=2026.3.24-beta.2",
      "minGatewayVersion": "2026.3.24-beta.2"
    },
    "build": {
      "openclawVersion": "2026.3.24-beta.2",
      "pluginSdkVersion": "2026.3.24-beta.2"
    }
  }
}
```

plugin을 외부에서 ClawHub에 게시하는 경우 `compat`와 `build`
필드는 필수입니다. 정식 게시 스니펫은
`docs/snippets/plugin-publish/`에 있습니다.

### `openclaw` 필드

| 필드 | 타입 | 설명 |
| ------------ | ---------- | ------------------------------------------------------------------------------------------------------ |
| `extensions` | `string[]` | 엔트리포인트 파일(패키지 루트 기준 상대 경로) |
| `setupEntry` | `string` | 가벼운 setup-only 엔트리(선택 사항) |
| `channel` | `object` | setup, picker, quickstart, status 표면을 위한 채널 카탈로그 메타데이터 |
| `providers` | `string[]` | 이 plugin이 등록하는 provider ID |
| `install` | `object` | 설치 힌트: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup` | `object` | 시작 동작 플래그 |

### `openclaw.channel`

`openclaw.channel`은 런타임이 로드되기 전 채널 검색 및 setup
표면을 위한 가벼운 패키지 메타데이터입니다.

| 필드 | 타입 | 의미 |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id` | `string` | 정식 채널 ID |
| `label` | `string` | 기본 채널 라벨 |
| `selectionLabel` | `string` | `label`과 달라야 하는 경우의 picker/setup 라벨 |
| `detailLabel` | `string` | 더 풍부한 채널 카탈로그 및 status 표면용 보조 상세 라벨 |
| `docsPath` | `string` | setup 및 선택 링크용 문서 경로 |
| `docsLabel` | `string` | 문서 링크에 사용할 라벨이 채널 ID와 달라야 할 때의 재정의 라벨 |
| `blurb` | `string` | 짧은 온보딩/카탈로그 설명 |
| `order` | `number` | 채널 카탈로그의 정렬 순서 |
| `aliases` | `string[]` | 채널 선택을 위한 추가 조회 별칭 |
| `preferOver` | `string[]` | 이 채널이 우선해야 하는 더 낮은 우선순위 plugin/channel ID |
| `systemImage` | `string` | 채널 UI 카탈로그용 선택적 icon/system-image 이름 |
| `selectionDocsPrefix` | `string` | 선택 표면에서 문서 링크 앞에 붙는 접두 텍스트 |
| `selectionDocsOmitLabel` | `boolean` | 선택 문구에서 라벨이 붙은 문서 링크 대신 문서 경로를 직접 표시 |
| `selectionExtras` | `string[]` | 선택 문구에 추가되는 짧은 문자열 |
| `markdownCapable` | `boolean` | 아웃바운드 서식 결정 시 이 채널이 Markdown 가능함을 표시 |
| `showConfigured` | `boolean` | 구성된 채널 목록 표면에 이 채널을 표시할지 제어 |
| `quickstartAllowFrom` | `boolean` | 이 채널을 표준 quickstart `allowFrom` setup 흐름에 포함 |
| `forceAccountBinding` | `boolean` | 계정이 하나뿐이어도 명시적인 계정 바인딩을 요구 |
| `preferSessionLookupForAnnounceTarget` | `boolean` | 이 채널의 announce target 해석 시 세션 조회를 우선 |

예시:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "quickstartAllowFrom": true
    }
  }
}
```

### `openclaw.install`

`openclaw.install`은 manifest 메타데이터가 아니라 패키지 메타데이터입니다.

| 필드 | 타입 | 의미 |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec` | `string` | install/update 흐름용 정식 npm spec |
| `localPath` | `string` | 로컬 개발 또는 번들 설치 경로 |
| `defaultChoice` | `"npm"` \| `"local"` | 둘 다 가능할 때 선호되는 설치 소스 |
| `minHostVersion` | `string` | `>=x.y.z` 형식의 최소 지원 OpenClaw 버전 |
| `allowInvalidConfigRecovery` | `boolean` | 특정 오래된 config 실패로부터 번들 plugin 재설치 흐름이 복구되도록 허용 |

`minHostVersion`이 설정되면 install과 manifest-registry 로딩 모두 이를 강제합니다. 더 오래된 호스트는 plugin을 건너뛰며, 잘못된 버전 문자열은 거부됩니다.

`allowInvalidConfigRecovery`는 손상된 config에 대한 일반적인 우회가 아닙니다. 이는 좁은 번들 plugin 복구 전용이므로 재설치/setup가 동일한 plugin의 번들 plugin 경로 누락이나 오래된 `channels.<id>` 항목 같은 알려진 업그레이드 잔여물을 복구할 수 있게 합니다. config가 관련 없는 이유로 손상되었다면 install은 여전히 fail closed하며 운영자에게 `openclaw doctor --fix`를 실행하라고 안내합니다.

### 지연된 full load

Channel plugins는 다음과 같이 지연 로딩을 옵트인할 수 있습니다.

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

활성화하면 OpenClaw는 이미 구성된 채널에 대해서도 pre-listen 시작
단계에서는 `setupEntry`만 로드합니다. full entry는 gateway가 listening을 시작한 후 로드됩니다.

<Warning>
  지연 로딩은 `setupEntry`가 gateway가 listening을 시작하기 전에 필요한 모든 것(채널 등록, HTTP routes,
  gateway methods)을 등록할 때만 활성화하세요. full entry가 필요한 시작 capability를 소유하고 있다면 기본 동작을 유지하세요.
</Warning>

setup/full entry가 gateway RPC 메서드도 등록한다면 plugin 전용 접두사 아래에 두세요. 예약된 핵심 admin namespace (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`)는 여전히 core가 소유하며 항상
`operator.admin`으로 해석됩니다.

## Plugin manifest

모든 네이티브 plugin은 패키지 루트에 `openclaw.plugin.json`을 포함해야 합니다.
OpenClaw는 plugin 코드를 실행하지 않고도 config를 검증하기 위해 이것을 사용합니다.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
      }
    }
  }
}
```

channel plugins의 경우 `kind`와 `channels`를 추가하세요.

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

config가 없는 plugin도 반드시 스키마를 포함해야 합니다. 빈 스키마도 유효합니다.

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

전체 스키마 참조는 [Plugin Manifest](/plugins/manifest)를 참조하세요.

## ClawHub 게시

plugin 패키지의 경우 패키지 전용 ClawHub 명령을 사용하세요.

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

레거시 skill-only 게시 별칭은 Skills용입니다. plugin 패키지는 항상
`clawhub package publish`를 사용해야 합니다.

## Setup entry

`setup-entry.ts` 파일은
OpenClaw가 setup 표면(온보딩, config repair, 비활성 채널 검사)만 필요할 때 로드하는 `index.ts`의 가벼운 대안입니다.

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

이렇게 하면 setup 흐름 중 무거운 런타임 코드(crypto 라이브러리, CLI 등록,
백그라운드 서비스)를 로드하지 않아도 됩니다.

**OpenClaw가 full entry 대신 `setupEntry`를 사용하는 경우:**

- 채널이 비활성화되었지만 setup/온보딩 표면이 필요한 경우
- 채널이 활성화되었지만 미구성인 경우
- 지연 로딩이 활성화된 경우 (`deferConfiguredChannelFullLoadUntilAfterListen`)

**`setupEntry`가 반드시 등록해야 하는 것:**

- 채널 plugin 객체 (`defineSetupPluginEntry`를 통해)
- gateway listen 전에 필요한 모든 HTTP routes
- 시작 중 필요한 모든 gateway methods

이러한 시작용 gateway methods도 예약된 핵심 admin
namespace인 `config.*` 또는 `update.*`는 피해야 합니다.

**`setupEntry`에 포함하면 안 되는 것:**

- CLI 등록
- 백그라운드 서비스
- 무거운 런타임 import(crypto, SDKs)
- 시작 후에만 필요한 gateway methods

### 좁은 setup helper import

hot setup-only 경로에서는 setup 표면의 일부만 필요하다면 더 넓은
`plugin-sdk/setup` umbrella 대신 좁은 setup helper seam을 우선 사용하세요.

| import 경로 | 용도 | 주요 exports |
| ---------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime` | `setupEntry` / 지연 채널 시작에서 계속 사용 가능한 setup 시점 런타임 도우미 | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime` | 환경 인식 account setup adapter | `createEnvPatchedAccountSetupAdapter` |
| `plugin-sdk/setup-tools` | setup/install CLI/archive/docs 도우미 | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |

config-patch 도우미인
`moveSingleAccountChannelSectionToDefaultAccount(...)`까지 포함한 전체 공유 setup toolbox가 필요할 때는 더 넓은 `plugin-sdk/setup` seam을 사용하세요.

setup patch adapters는 import 시 hot-path 안전성을 유지합니다. 번들
single-account promotion contract-surface 조회는 지연 방식이므로
`plugin-sdk/setup-runtime`을 import해도 adapter가 실제로 사용되기 전에는 번들 contract-surface 검색을 eagerly 로드하지 않습니다.

### 채널 소유 single-account promotion

채널이 single-account 최상위 config에서
`channels.<id>.accounts.*`로 업그레이드될 때, 기본 공유 동작은 승격된
account 범위 값을 `accounts.default`로 옮기는 것입니다.

번들 채널은 setup
contract surface를 통해 이 promotion을 좁히거나 재정의할 수 있습니다.

- `singleAccountKeysToMove`: 승격된 account로 추가 이동해야 하는
  최상위 키
- `namedAccountPromotionKeys`: 이름 있는 accounts가 이미 존재하면 이 키들만 승격된 account로 이동하고, 공유 정책/전달 키는 채널 루트에 남음
- `resolveSingleAccountPromotionTarget(...)`: 승격된 값을 받을 기존 account를 선택

Matrix가 현재 번들 예시입니다. 이름 있는 Matrix account가 정확히 하나만 존재하거나 `defaultAccount`가 `Ops` 같은 기존 비정규 키를 가리키면, promotion은 새 `accounts.default` 항목을 만드는 대신 해당 account를 유지합니다.

## Config 스키마

plugin config는 manifest의 JSON Schema에 따라 검증됩니다. 사용자는 다음과 같이 plugins를 구성합니다.

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

plugin은 등록 중 이 config를 `api.pluginConfig`로 받습니다.

채널 전용 config의 경우 대신 채널 config 섹션을 사용하세요.

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### 채널 config 스키마 빌드

OpenClaw가 검증하는 `ChannelConfigSchema` 래퍼로
Zod 스키마를 변환하려면 `openclaw/plugin-sdk/core`의 `buildChannelConfigSchema`를 사용하세요.

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## Setup wizards

Channel plugins는 `openclaw onboard`용 대화형 setup wizard를 제공할 수 있습니다.
wizard는 `ChannelPlugin`의 `ChannelSetupWizard` 객체입니다.

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

`ChannelSetupWizard` 타입은 `credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize` 등을 지원합니다.
전체 예시는 번들 plugin 패키지(예: Discord plugin의 `src/channel.setup.ts`)를 참조하세요.

표준적인
`note -> prompt -> parse -> merge -> patch` 흐름만 필요한 DM 허용 목록 프롬프트에는
`openclaw/plugin-sdk/setup`의 공유 setup helpers인 `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)`, `createNestedChannelParsedAllowFromPrompt(...)`를 우선 사용하세요.

라벨, 점수, 선택적 추가 줄만 다른 채널 setup status 블록에는
각 plugin에서 동일한 `status` 객체를 직접 만드는 대신
`openclaw/plugin-sdk/setup`의 `createStandardChannelSetupStatus(...)`를 우선 사용하세요.

특정 컨텍스트에서만 나타나야 하는 선택적 setup 표면에는
`openclaw/plugin-sdk/channel-setup`의 `createOptionalChannelSetupSurface`를 사용하세요.

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// { setupAdapter, setupWizard } 반환
```

`plugin-sdk/channel-setup`은 해당 선택적 설치 표면의 한쪽만 필요할 때를 위해 더 낮은 수준의
`createOptionalChannelSetupAdapter(...)`와
`createOptionalChannelSetupWizard(...)` 빌더도 제공합니다.

생성된 선택적 adapter/wizard는 실제 config 쓰기에서는 fail closed합니다. 이들은 `validateInput`,
`applyAccountConfig`, `finalize` 전반에 걸쳐 하나의 install-required 메시지를 재사용하고, `docsPath`가 설정된 경우 문서 링크를 추가합니다.

바이너리 기반 setup UI에는 동일한 binary/status glue를 각 채널에 복사하는 대신 공유 delegated helpers를 우선 사용하세요.

- 라벨, 힌트, 점수, 바이너리 감지만 다른 status 블록용 `createDetectedBinaryStatus(...)`
- 경로 기반 text input용 `createCliPathTextInput(...)`
- `setupEntry`가 더 무거운 full wizard에 지연 전달해야 할 때의
  `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)`,
  `createDelegatedResolveConfigured(...)`
- `setupEntry`가 `textInputs[*].shouldPrompt` 결정만 위임하면 될 때의
  `createDelegatedTextInputShouldPrompt(...)`

## 게시 및 설치

**외부 plugins:** [ClawHub](/tools/clawhub) 또는 npm에 게시한 뒤 설치:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

OpenClaw는 먼저 ClawHub를 시도하고 자동으로 npm으로 폴백합니다. ClawHub를 명시적으로 강제할 수도 있습니다.

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # ClawHub 전용
```

일치하는 `npm:` 재정의는 없습니다. ClawHub 폴백 뒤 npm 경로를 원한다면 일반 npm package spec을 사용하세요.

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**리포지토리 내 plugins:** 번들 plugin workspace 트리 아래에 두면 빌드 중 자동으로
검색됩니다.

**사용자가 설치할 수 있는 명령:**

```bash
openclaw plugins install <package-name>
```

<Info>
  npm 소스 설치의 경우 `openclaw plugins install`은
  `npm install --ignore-scripts`를 실행합니다(라이프사이클 스크립트 없음). plugin 종속성
  트리는 순수 JS/TS로 유지하고 `postinstall` 빌드가 필요한 패키지는 피하세요.
</Info>

## 관련 문서

- [SDK 엔트리포인트](/plugins/sdk-entrypoints) -- `definePluginEntry`와 `defineChannelPluginEntry`
- [Plugin Manifest](/plugins/manifest) -- 전체 manifest 스키마 참조
- [Building Plugins](/plugins/building-plugins) -- 단계별 시작 가이드
