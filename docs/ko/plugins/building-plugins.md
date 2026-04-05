---
read_when:
    - 새 OpenClaw plugin을 만들고 싶을 때
    - plugin 개발을 위한 빠른 시작이 필요할 때
    - OpenClaw에 새 채널, provider, 도구 또는 기타 기능을 추가할 때
sidebarTitle: Getting Started
summary: 몇 분 만에 첫 OpenClaw plugin 만들기
title: Building Plugins
x-i18n:
    generated_at: "2026-04-05T12:49:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 26e780d3f04270b79d1d8f8076d6c3c5031915043e78fb8174be921c6bdd60c9
    source_path: plugins/building-plugins.md
    workflow: 15
---

# Building Plugins

Plugins는 OpenClaw에 새로운 기능을 추가합니다: 채널, 모델 provider,
speech, 실시간 transcription, 실시간 voice, media 이해, 이미지
생성, 비디오 생성, 웹 fetch, 웹 search, 에이전트 도구 또는
이들의 조합.

plugin을 OpenClaw 리포지토리에 추가할 필요는 없습니다.
[ClawHub](/tools/clawhub) 또는 npm에 게시하고 사용자는
`openclaw plugins install <package-name>`로 설치합니다. OpenClaw는 먼저 ClawHub를 시도하고
자동으로 npm으로 대체합니다.

## 전제 조건

- Node >= 22 및 패키지 관리자(npm 또는 pnpm)
- TypeScript(ESM)에 대한 익숙함
- 리포지토리 내부 plugin의 경우: 리포지토리 클론 및 `pnpm install` 완료

## 어떤 종류의 plugin인가요?

<CardGroup cols={3}>
  <Card title="채널 plugin" icon="messages-square" href="/plugins/sdk-channel-plugins">
    OpenClaw를 메시징 플랫폼(Discord, IRC 등)에 연결
  </Card>
  <Card title="Provider plugin" icon="cpu" href="/plugins/sdk-provider-plugins">
    모델 provider(LLM, 프록시 또는 사용자 지정 엔드포인트) 추가
  </Card>
  <Card title="도구 / hook plugin" icon="wrench">
    에이전트 도구, 이벤트 hook 또는 서비스 등록 — 아래 계속
  </Card>
</CardGroup>

채널 plugin이 선택 사항이며 온보딩/설정 실행 시
설치되지 않았을 수 있다면 `openclaw/plugin-sdk/channel-setup`의
`createOptionalChannelSetupSurface(...)`를 사용하세요. 이는 설치 요구 사항을 광고하고,
plugin이 설치될 때까지 실제 config 기록에서 fail closed하는 설정 adapter + wizard 쌍을 생성합니다.

## 빠른 시작: 도구 plugin

이 단계별 설명에서는 에이전트 도구를 등록하는 최소 plugin을 만듭니다. 채널
및 provider plugins에는 위에 링크된 전용 가이드가 있습니다.

<Steps>
  <Step title="패키지와 manifest 만들기">
    <CodeGroup>
    ```json package.json
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

    ```json openclaw.plugin.json
    {
      "id": "my-plugin",
      "name": "My Plugin",
      "description": "Adds a custom tool to OpenClaw",
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    config가 전혀 없더라도 모든 plugin에는 manifest가 필요합니다.
    전체 스키마는 [Manifest](/plugins/manifest)를 참조하세요. 정식 ClawHub
    게시 스니펫은 `docs/snippets/plugin-publish/`에 있습니다.

  </Step>

  <Step title="진입점 작성">

    ```typescript
    // index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { Type } from "@sinclair/typebox";

    export default definePluginEntry({
      id: "my-plugin",
      name: "My Plugin",
      description: "Adds a custom tool to OpenClaw",
      register(api) {
        api.registerTool({
          name: "my_tool",
          description: "Do a thing",
          parameters: Type.Object({ input: Type.String() }),
          async execute(_id, params) {
            return { content: [{ type: "text", text: `Got: ${params.input}` }] };
          },
        });
      },
    });
    ```

    `definePluginEntry`는 비채널 plugin용입니다. 채널의 경우
    `defineChannelPluginEntry`를 사용하세요 — [Channel Plugins](/plugins/sdk-channel-plugins)를 참조하세요.
    전체 진입점 옵션은 [Entry Points](/plugins/sdk-entrypoints)를 참조하세요.

  </Step>

  <Step title="테스트 및 게시">

    **외부 plugins:** ClawHub로 검증 및 게시한 다음 설치합니다:

    ```bash
    clawhub package publish your-org/your-plugin --dry-run
    clawhub package publish your-org/your-plugin
    openclaw plugins install clawhub:@myorg/openclaw-my-plugin
    ```

    OpenClaw는 `@myorg/openclaw-my-plugin` 같은
    일반 패키지 spec에 대해서도 npm보다 먼저 ClawHub를 확인합니다.

    **리포지토리 내부 plugins:** 번들 plugin 워크스페이스 트리 아래에 두면 자동으로 검색됩니다.

    ```bash
    pnpm test -- <bundled-plugin-root>/my-plugin/
    ```

  </Step>
</Steps>

## Plugin 기능

하나의 plugin은 `api` 객체를 통해 임의 개수의 기능을 등록할 수 있습니다:

| 기능 | 등록 메서드 | 상세 가이드 |
| ---------------------- | ------------------------------------------------ | ------------------------------------------------------------------------------- |
| 텍스트 추론(LLM)   | `api.registerProvider(...)`                      | [Provider Plugins](/plugins/sdk-provider-plugins)                               |
| CLI 추론 백엔드  | `api.registerCliBackend(...)`                    | [CLI Backends](/gateway/cli-backends)                                           |
| 채널 / 메시징    | `api.registerChannel(...)`                       | [Channel Plugins](/plugins/sdk-channel-plugins)                                 |
| Speech (TTS/STT)       | `api.registerSpeechProvider(...)`                | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 실시간 transcription | `api.registerRealtimeTranscriptionProvider(...)` | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 실시간 voice         | `api.registerRealtimeVoiceProvider(...)`         | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| Media 이해    | `api.registerMediaUnderstandingProvider(...)`    | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 이미지 생성       | `api.registerImageGenerationProvider(...)`       | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 비디오 생성       | `api.registerVideoGenerationProvider(...)`       | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 웹 fetch              | `api.registerWebFetchProvider(...)`              | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 웹 search             | `api.registerWebSearchProvider(...)`             | [Provider Plugins](/plugins/sdk-provider-plugins#step-5-add-extra-capabilities) |
| 에이전트 도구            | `api.registerTool(...)`                          | 아래                                                                           |
| 사용자 지정 명령        | `api.registerCommand(...)`                       | [Entry Points](/plugins/sdk-entrypoints)                                        |
| 이벤트 hook            | `api.registerHook(...)`                          | [Entry Points](/plugins/sdk-entrypoints)                                        |
| HTTP 라우트            | `api.registerHttpRoute(...)`                     | [Internals](/plugins/architecture#gateway-http-routes)                          |
| CLI 하위 명령        | `api.registerCli(...)`                           | [Entry Points](/plugins/sdk-entrypoints)                                        |

전체 등록 API는 [SDK Overview](/plugins/sdk-overview#registration-api)를 참조하세요.

plugin이 사용자 지정 게이트웨이 RPC 메서드를 등록하는 경우에는
plugin 전용 접두사에 두세요. 코어 관리자 네임스페이스(`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`)는 예약된 상태로 유지되며
plugin이 더 좁은 범위를 요청하더라도 항상 `operator.admin`으로 해석됩니다.

기억해야 할 hook 가드 의미:

- `before_tool_call`: `{ block: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단시킵니다.
- `before_tool_call`: `{ block: false }`는 결정 없음으로 처리됩니다.
- `before_tool_call`: `{ requireApproval: true }`는 에이전트 실행을 일시 중지하고 exec 승인 오버레이, Telegram 버튼, Discord 상호작용 또는 어느 채널에서든 `/approve` 명령을 통해 사용자 승인을 요청합니다.
- `before_install`: `{ block: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단시킵니다.
- `before_install`: `{ block: false }`는 결정 없음으로 처리됩니다.
- `message_sending`: `{ cancel: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단시킵니다.
- `message_sending`: `{ cancel: false }`는 결정 없음으로 처리됩니다.

`/approve` 명령은 exec 승인과 plugin 승인 모두를 제한된 fallback과 함께 처리합니다. exec 승인 ID를 찾지 못하면 OpenClaw는 동일한 ID를 plugin 승인을 통해 다시 시도합니다. plugin 승인 전달은 config의 `approvals.plugin`을 통해 독립적으로 구성할 수 있습니다.

사용자 지정 승인 플러밍에서 동일한 제한된 fallback 사례를 감지해야 한다면,
승인 만료 문자열을 수동으로 매칭하지 말고 `openclaw/plugin-sdk/error-runtime`의
`isApprovalNotFoundError`를 사용하세요.

자세한 내용은 [SDK Overview hook decision semantics](/plugins/sdk-overview#hook-decision-semantics)를 참조하세요.

## 에이전트 도구 등록

도구는 LLM이 호출할 수 있는 타입 지정 함수입니다. 필수(항상
사용 가능) 또는 선택 사항(사용자 opt-in)으로 만들 수 있습니다:

```typescript
register(api) {
  // 필수 도구 — 항상 사용 가능
  api.registerTool({
    name: "my_tool",
    description: "Do a thing",
    parameters: Type.Object({ input: Type.String() }),
    async execute(_id, params) {
      return { content: [{ type: "text", text: params.input }] };
    },
  });

  // 선택 도구 — 사용자가 허용 목록에 추가해야 함
  api.registerTool(
    {
      name: "workflow_tool",
      description: "Run a workflow",
      parameters: Type.Object({ pipeline: Type.String() }),
      async execute(_id, params) {
        return { content: [{ type: "text", text: params.pipeline }] };
      },
    },
    { optional: true },
  );
}
```

사용자는 config에서 선택 도구를 활성화합니다:

```json5
{
  tools: { allow: ["workflow_tool"] },
}
```

- 도구 이름은 코어 도구와 충돌하면 안 됩니다(충돌 시 건너뜀)
- 부작용이나 추가 바이너리 요구 사항이 있는 도구에는 `optional: true`를 사용하세요
- 사용자는 `tools.allow`에 plugin ID를 추가하여 plugin의 모든 도구를 활성화할 수 있습니다

## import 규칙

항상 집중된 `openclaw/plugin-sdk/<subpath>` 경로에서 import하세요:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";

// 잘못된 예: 단일 루트(monolithic root, deprecated, 추후 제거 예정)
import { ... } from "openclaw/plugin-sdk";
```

전체 하위 경로 참조는 [SDK Overview](/plugins/sdk-overview)를 참조하세요.

plugin 내부에서는 내부 import에 로컬 barrel 파일(`api.ts`, `runtime-api.ts`)을 사용하세요 — 자신의 plugin을 SDK 경로를 통해 import하지 마세요.

provider plugins의 경우 provider 전용 helper는 해당 패키지 루트
barrel에 유지하세요. seam이 진짜로 일반적인 경우에만 예외입니다. 현재 번들 예시:

- Anthropic: Claude 스트림 래퍼 및 `service_tier` / 베타 helper
- OpenAI: provider 빌더, 기본 모델 helper, 실시간 provider
- OpenRouter: provider 빌더 및 onboarding/config helper

helper가 하나의 번들 provider 패키지 내부에서만 유용하다면
`openclaw/plugin-sdk/*`로 승격시키기보다 해당
패키지 루트 seam에 두세요.

생성된 일부 `openclaw/plugin-sdk/<bundled-id>` helper seam은 여전히
번들 plugin 유지관리와 호환성을 위해 존재합니다. 예를 들어
`plugin-sdk/feishu-setup` 또는 `plugin-sdk/zalo-setup`이 있습니다. 이를
새 서드파티 plugin의 기본 패턴이 아니라 예약된 표면으로 취급하세요.

## 제출 전 체크리스트

<Check>**package.json**에 올바른 `openclaw` 메타데이터가 있음</Check>
<Check>**openclaw.plugin.json** manifest가 존재하고 유효함</Check>
<Check>진입점이 `defineChannelPluginEntry` 또는 `definePluginEntry`를 사용함</Check>
<Check>모든 import가 집중된 `plugin-sdk/<subpath>` 경로를 사용함</Check>
<Check>내부 import가 SDK self-import가 아니라 로컬 모듈을 사용함</Check>
<Check>테스트 통과 (`pnpm test -- <bundled-plugin-root>/my-plugin/`)</Check>
<Check>`pnpm check` 통과 (리포지토리 내부 plugins)</Check>

## 베타 릴리스 테스트

1. [openclaw/openclaw](https://github.com/openclaw/openclaw/releases)의 GitHub 릴리스 태그를 주시하고 `Watch` > `Releases`를 통해 구독하세요. 베타 태그는 `v2026.3.N-beta.1`처럼 보입니다. 릴리스 공지를 위해 공식 OpenClaw X 계정 [@openclaw](https://x.com/openclaw)의 알림을 켤 수도 있습니다.
2. 베타 태그가 나타나는 즉시 plugin을 테스트하세요. stable 이전의 창은 보통 몇 시간밖에 되지 않습니다.
3. 테스트 후 `plugin-forum` Discord 채널의 plugin 스레드에 `all good` 또는 무엇이 깨졌는지를 게시하세요. 아직 스레드가 없다면 새로 만드세요.
4. 무언가 깨졌다면 `Beta blocker: <plugin-name> - <summary>` 제목으로 이슈를 열거나 업데이트하고 `beta-blocker` 레이블을 적용하세요. 이슈 링크를 스레드에 넣으세요.
5. `main`에 `fix(<plugin-id>): beta blocker - <summary>` 제목으로 PR을 열고, PR과 Discord 스레드 모두에 이슈를 링크하세요. 기여자는 PR에 레이블을 붙일 수 없으므로 제목이 유지관리자와 자동화를 위한 PR 측 신호입니다. PR이 있는 blocker는 병합되고, 없는 blocker는 그대로 릴리스될 수 있습니다. 유지관리자는 베타 테스트 동안 이 스레드를 모니터링합니다.
6. 아무 말이 없으면 녹색 신호입니다. 시간을 놓쳤다면 수정 사항은 다음 주기에 들어갈 가능성이 큽니다.

## 다음 단계

<CardGroup cols={2}>
  <Card title="Channel Plugins" icon="messages-square" href="/plugins/sdk-channel-plugins">
    메시징 채널 plugin 만들기
  </Card>
  <Card title="Provider Plugins" icon="cpu" href="/plugins/sdk-provider-plugins">
    모델 provider plugin 만들기
  </Card>
  <Card title="SDK Overview" icon="book-open" href="/plugins/sdk-overview">
    import 맵 및 등록 API 참조
  </Card>
  <Card title="Runtime Helpers" icon="settings" href="/plugins/sdk-runtime">
    `api.runtime`를 통한 TTS, search, subagent
  </Card>
  <Card title="Testing" icon="test-tubes" href="/plugins/sdk-testing">
    테스트 유틸리티 및 패턴
  </Card>
  <Card title="Plugin Manifest" icon="file-json" href="/plugins/manifest">
    전체 manifest 스키마 참조
  </Card>
</CardGroup>

## 관련

- [Plugin Architecture](/plugins/architecture) — 내부 아키텍처 심층 설명
- [SDK Overview](/plugins/sdk-overview) — Plugin SDK 참조
- [Manifest](/plugins/manifest) — plugin manifest 형식
- [Channel Plugins](/plugins/sdk-channel-plugins) — 채널 plugin 만들기
- [Provider Plugins](/plugins/sdk-provider-plugins) — provider plugin 만들기
