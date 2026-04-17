---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED 경고가 표시됩니다
    - OPENCLAW_EXTENSION_API_DEPRECATED 경고가 표시됩니다
    - Plugin을 최신 plugin 아키텍처로 업데이트하고 있습니다
    - 외부 OpenClaw Plugin을 유지 관리하고 있습니다
sidebarTitle: Migrate to SDK
summary: 레거시 하위 호환성 레이어에서 최신 Plugin SDK로 마이그레이션하세요
title: Plugin SDK 마이그레이션
x-i18n:
    generated_at: "2026-04-17T06:00:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: f0283f949eec358a12a0709db846cde2a1509f28e5c60db6e563cb8a540b979d
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK 마이그레이션

OpenClaw는 광범위한 하위 호환성 레이어에서, 목적이 분명하고 문서화된 import를 사용하는 최신 plugin 아키텍처로 전환했습니다. 플러그인이 새 아키텍처 이전에 만들어졌다면, 이 가이드가 마이그레이션에 도움이 됩니다.

## 변경되는 내용

기존 plugin 시스템은 플러그인이 단일 진입점에서 필요한 모든 것을 import할 수 있도록 하는 두 개의 매우 광범위한 표면을 제공했습니다.

- **`openclaw/plugin-sdk/compat`** — 수십 개의 헬퍼를 재수출하던 단일 import입니다. 새 plugin 아키텍처가 구축되는 동안 오래된 hook 기반 플러그인을 계속 동작하게 유지하기 위해 도입되었습니다.
- **`openclaw/extension-api`** — 임베디드 agent runner 같은 호스트 측 헬퍼에 플러그인이 직접 접근할 수 있게 해주던 브리지입니다.

이 두 표면은 이제 모두 **deprecated** 되었습니다. 런타임에서는 여전히 동작하지만, 새 플러그인은 이를 사용하면 안 되며 기존 플러그인은 다음 major release에서 제거되기 전에 마이그레이션해야 합니다.

<Warning>
  하위 호환성 레이어는 향후 major release에서 제거될 예정입니다.
  여전히 이 표면들에서 import하는 Plugin은 그 시점에 중단됩니다.
</Warning>

## 왜 변경되었나요?

기존 접근 방식은 다음과 같은 문제를 일으켰습니다.

- **느린 시작 속도** — 하나의 헬퍼를 import해도 관련 없는 수십 개의 모듈이 함께 로드되었습니다
- **순환 의존성** — 광범위한 재수출 때문에 import cycle이 쉽게 생겼습니다
- **불명확한 API 표면** — 어떤 export가 안정적인지, 어떤 것이 내부용인지 구분할 방법이 없었습니다

최신 Plugin SDK는 이를 해결합니다. 각 import 경로(`openclaw/plugin-sdk/\<subpath\>`)는 목적이 명확하고 문서화된 계약을 가진 작고 독립적인 모듈입니다.

번들 채널용 레거시 provider 편의 seam도 제거되었습니다. `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`, `openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, 채널 브랜드 헬퍼 seam, 그리고 `openclaw/plugin-sdk/telegram-core` 같은 import는 안정적인 plugin 계약이 아니라 비공개 mono-repo 지름길이었습니다. 대신 좁고 범용적인 SDK subpath를 사용하세요. 번들 plugin workspace 내부에서는 provider 소유 헬퍼를 해당 plugin의 `api.ts` 또는 `runtime-api.ts` 안에 유지하세요.

현재 번들 provider 예시는 다음과 같습니다.

- Anthropic은 Claude 전용 stream 헬퍼를 자체 `api.ts` / `contract-api.ts` seam에 유지합니다
- OpenAI는 provider builder, 기본 model 헬퍼, realtime provider builder를 자체 `api.ts`에 유지합니다
- OpenRouter는 provider builder와 onboarding/config 헬퍼를 자체 `api.ts`에 유지합니다

## 마이그레이션 방법

<Steps>
  <Step title="승인 네이티브 핸들러를 capability fact로 마이그레이션">
    승인 기능을 지원하는 channel plugin은 이제 `approvalCapability.nativeRuntime`과 공유 runtime-context registry를 통해 네이티브 승인 동작을 노출합니다.

    주요 변경 사항:

    - `approvalCapability.handler.loadRuntime(...)`을
      `approvalCapability.nativeRuntime`으로 교체합니다
    - 승인 전용 auth/delivery를 레거시 `plugin.auth` /
      `plugin.approvals` wiring에서 분리해 `approvalCapability`로 옮깁니다
    - `ChannelPlugin.approvals`는 공개 channel-plugin
      계약에서 제거되었습니다. delivery/native/render 필드를 `approvalCapability`로 옮기세요
    - `plugin.auth`는 channel login/logout 흐름에만 계속 사용됩니다. 그 안의 승인 auth
      hook은 더 이상 core에서 읽지 않습니다
    - 클라이언트, 토큰, Bolt
      app 같은 channel 소유 runtime 객체는 `openclaw/plugin-sdk/channel-runtime-context`를 통해 등록합니다
    - 네이티브 승인 핸들러에서 plugin 소유 reroute notice를 보내지 마세요.
      이제 core가 실제 delivery 결과를 바탕으로 routed-elsewhere notice를 담당합니다
    - `channelRuntime`을 `createChannelManager(...)`에 전달할 때는
      실제 `createPluginRuntime().channel` 표면을 제공하세요. 부분적인 stub은 거부됩니다.

    현재 approval capability
    레이아웃은 `/plugins/sdk-channel-plugins`를 참조하세요.

  </Step>

  <Step title="Windows wrapper fallback 동작 감사">
    플러그인이 `openclaw/plugin-sdk/windows-spawn`을 사용한다면,
    이제 확인되지 않은 Windows `.cmd`/`.bat` wrapper는 `allowShellFallback: true`를
    명시적으로 전달하지 않는 한 fail closed 됩니다.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // 신뢰할 수 있는 호환성 호출자 중 의도적으로
      // shell 매개 fallback을 허용하는 경우에만 이것을 설정하세요.
      allowShellFallback: true,
    });
    ```

    호출자가 shell fallback에 의도적으로 의존하지 않는다면,
    `allowShellFallback`을 설정하지 말고 대신 throw된 오류를 처리하세요.

  </Step>

  <Step title="deprecated import 찾기">
    플러그인에서 deprecated 표면 두 곳 중 하나로부터의 import를 검색하세요.

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="집중된 import로 교체">
    기존 표면의 각 export는 특정한 최신 import 경로에 대응됩니다.

    ```typescript
    // Before (deprecated 하위 호환성 레이어)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (최신 집중형 import)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    호스트 측 헬퍼의 경우 직접 import하는 대신 주입된 plugin runtime을 사용하세요.

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (주입된 runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    같은 패턴이 다른 레거시 bridge 헬퍼에도 적용됩니다.

    | Old import | 최신 동등 항목 |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | session store helpers | `api.runtime.agent.session.*` |

  </Step>

  <Step title="빌드 및 테스트">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## import 경로 참조

  <Accordion title="공통 import 경로 표">
  | Import path | 용도 | 주요 export |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 정식 plugin 엔트리 헬퍼 | `definePluginEntry` |
  | `plugin-sdk/core` | channel 엔트리 정의/빌더용 레거시 umbrella 재수출 | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | 루트 config schema export | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 단일 provider 엔트리 헬퍼 | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 집중된 channel 엔트리 정의 및 빌더 | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 공유 setup wizard 헬퍼 | Allowlist 프롬프트, setup 상태 빌더 |
  | `plugin-sdk/setup-runtime` | setup 시점 runtime 헬퍼 | Import-safe setup patch adapter, lookup-note 헬퍼, `promptResolvedAllowFrom`, `splitSetupEntries`, delegated setup proxy |
  | `plugin-sdk/setup-adapter-runtime` | setup adapter 헬퍼 | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | setup tooling 헬퍼 | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | 다중 account 헬퍼 | account 목록/config/action-gate 헬퍼 |
  | `plugin-sdk/account-id` | account-id 헬퍼 | `DEFAULT_ACCOUNT_ID`, account-id 정규화 |
  | `plugin-sdk/account-resolution` | account 조회 헬퍼 | account 조회 + 기본 fallback 헬퍼 |
  | `plugin-sdk/account-helpers` | 좁은 범위의 account 헬퍼 | account 목록/account-action 헬퍼 |
  | `plugin-sdk/channel-setup` | setup wizard adapter | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, 그리고 `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM 페어링 기본 요소 | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | reply 접두사 + typing wiring | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | config adapter 팩토리 | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | config schema 빌더 | channel config schema 타입 |
  | `plugin-sdk/telegram-command-config` | Telegram 명령 config 헬퍼 | 명령 이름 정규화, 설명 잘라내기, 중복/충돌 검증 |
  | `plugin-sdk/channel-policy` | 그룹/DM 정책 확인 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | account 상태 추적 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | inbound envelope 헬퍼 | 공유 route + envelope 빌더 헬퍼 |
  | `plugin-sdk/inbound-reply-dispatch` | inbound reply 헬퍼 | 공유 record-and-dispatch 헬퍼 |
  | `plugin-sdk/messaging-targets` | 메시징 대상 파싱 | 대상 파싱/매칭 헬퍼 |
  | `plugin-sdk/outbound-media` | outbound media 헬퍼 | 공유 outbound media 로딩 |
  | `plugin-sdk/outbound-runtime` | outbound runtime 헬퍼 | outbound identity/send delegate 헬퍼 |
  | `plugin-sdk/thread-bindings-runtime` | thread-binding 헬퍼 | thread-binding lifecycle 및 adapter 헬퍼 |
  | `plugin-sdk/agent-media-payload` | 레거시 media payload 헬퍼 | 레거시 필드 레이아웃용 agent media payload 빌더 |
  | `plugin-sdk/channel-runtime` | deprecated 호환성 shim | 레거시 channel runtime 유틸리티 전용 |
  | `plugin-sdk/channel-send-result` | send 결과 타입 | reply 결과 타입 |
  | `plugin-sdk/runtime-store` | 영구 plugin 저장소 | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 광범위한 runtime 헬퍼 | runtime/logging/backup/plugin-install 헬퍼 |
  | `plugin-sdk/runtime-env` | 좁은 범위의 runtime env 헬퍼 | logger/runtime env, timeout, retry, backoff 헬퍼 |
  | `plugin-sdk/plugin-runtime` | 공유 plugin runtime 헬퍼 | plugin 명령/hooks/http/interactive 헬퍼 |
  | `plugin-sdk/hook-runtime` | hook 파이프라인 헬퍼 | 공유 webhook/internal hook 파이프라인 헬퍼 |
  | `plugin-sdk/lazy-runtime` | lazy runtime 헬퍼 | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | 프로세스 헬퍼 | 공유 exec 헬퍼 |
  | `plugin-sdk/cli-runtime` | CLI runtime 헬퍼 | 명령 포맷팅, wait, 버전 헬퍼 |
  | `plugin-sdk/gateway-runtime` | Gateway 헬퍼 | Gateway 클라이언트 및 channel-status patch 헬퍼 |
  | `plugin-sdk/config-runtime` | config 헬퍼 | config 로드/쓰기 헬퍼 |
  | `plugin-sdk/telegram-command-config` | Telegram 명령 헬퍼 | 번들 Telegram 계약 표면을 사용할 수 없을 때의 fallback-stable Telegram 명령 검증 헬퍼 |
  | `plugin-sdk/approval-runtime` | 승인 프롬프트 헬퍼 | exec/plugin 승인 payload, approval capability/profile 헬퍼, 네이티브 승인 라우팅/runtime 헬퍼 |
  | `plugin-sdk/approval-auth-runtime` | 승인 auth 헬퍼 | approver 확인, same-chat action auth |
  | `plugin-sdk/approval-client-runtime` | 승인 클라이언트 헬퍼 | 네이티브 exec approval profile/filter 헬퍼 |
  | `plugin-sdk/approval-delivery-runtime` | 승인 delivery 헬퍼 | 네이티브 approval capability/delivery adapter |
  | `plugin-sdk/approval-gateway-runtime` | 승인 Gateway 헬퍼 | 공유 approval gateway-resolution 헬퍼 |
  | `plugin-sdk/approval-handler-adapter-runtime` | 승인 adapter 헬퍼 | hot channel 엔트리포인트용 경량 네이티브 approval adapter 로딩 헬퍼 |
  | `plugin-sdk/approval-handler-runtime` | 승인 핸들러 헬퍼 | 더 광범위한 approval handler runtime 헬퍼. adapter/gateway seam만으로 충분하다면 더 좁은 쪽을 우선 사용하세요 |
  | `plugin-sdk/approval-native-runtime` | 승인 대상 헬퍼 | 네이티브 approval 대상/account binding 헬퍼 |
  | `plugin-sdk/approval-reply-runtime` | 승인 reply 헬퍼 | exec/plugin 승인 reply payload 헬퍼 |
  | `plugin-sdk/channel-runtime-context` | channel runtime-context 헬퍼 | 범용 channel runtime-context register/get/watch 헬퍼 |
  | `plugin-sdk/security-runtime` | 보안 헬퍼 | 공유 trust, DM gating, external-content, secret-collection 헬퍼 |
  | `plugin-sdk/ssrf-policy` | SSRF 정책 헬퍼 | 호스트 allowlist 및 private-network 정책 헬퍼 |
  | `plugin-sdk/ssrf-runtime` | SSRF runtime 헬퍼 | pinned-dispatcher, guarded fetch, SSRF 정책 헬퍼 |
  | `plugin-sdk/collection-runtime` | bounded cache 헬퍼 | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 진단 게이팅 헬퍼 | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | 오류 포맷팅 헬퍼 | `formatUncaughtError`, `isApprovalNotFoundError`, 오류 그래프 헬퍼 |
  | `plugin-sdk/fetch-runtime` | 래핑된 fetch/proxy 헬퍼 | `resolveFetch`, proxy 헬퍼 |
  | `plugin-sdk/host-runtime` | 호스트 정규화 헬퍼 | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | retry 헬퍼 | `RetryConfig`, `retryAsync`, 정책 실행기 |
  | `plugin-sdk/allow-from` | Allowlist 포맷팅 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist 입력 매핑 | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | 명령 게이팅 및 명령 표면 헬퍼 | `resolveControlCommandGate`, 발신자 권한 부여 헬퍼, 명령 레지스트리 헬퍼 |
  | `plugin-sdk/command-status` | 명령 상태/help 렌더러 | `buildCommandsMessage`, `buildCommandsMessagePaginated`, `buildHelpMessage` |
  | `plugin-sdk/secret-input` | secret 입력 파싱 | secret 입력 헬퍼 |
  | `plugin-sdk/webhook-ingress` | Webhook 요청 헬퍼 | Webhook 대상 유틸리티 |
  | `plugin-sdk/webhook-request-guards` | Webhook body guard 헬퍼 | 요청 body 읽기/제한 헬퍼 |
  | `plugin-sdk/reply-runtime` | 공유 reply runtime | inbound dispatch, Heartbeat, reply planner, 청킹 |
  | `plugin-sdk/reply-dispatch-runtime` | 좁은 범위의 reply dispatch 헬퍼 | finalize + provider dispatch 헬퍼 |
  | `plugin-sdk/reply-history` | reply-history 헬퍼 | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | reply reference 계획 | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | reply chunk 헬퍼 | 텍스트/markdown 청킹 헬퍼 |
  | `plugin-sdk/session-store-runtime` | 세션 저장소 헬퍼 | 저장소 경로 + updated-at 헬퍼 |
  | `plugin-sdk/state-paths` | 상태 경로 헬퍼 | 상태 및 OAuth 디렉터리 헬퍼 |
  | `plugin-sdk/routing` | 라우팅/세션 키 헬퍼 | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, 세션 키 정규화 헬퍼 |
  | `plugin-sdk/status-helpers` | channel 상태 헬퍼 | channel/account 상태 요약 빌더, runtime-state 기본값, issue 메타데이터 헬퍼 |
  | `plugin-sdk/target-resolver-runtime` | 대상 확인 헬퍼 | 공유 대상 확인 헬퍼 |
  | `plugin-sdk/string-normalization-runtime` | 문자열 정규화 헬퍼 | 슬러그/문자열 정규화 헬퍼 |
  | `plugin-sdk/request-url` | 요청 URL 헬퍼 | request 유사 입력에서 문자열 URL 추출 |
  | `plugin-sdk/run-command` | 시간 제한 명령 헬퍼 | 정규화된 stdout/stderr를 사용하는 시간 제한 명령 실행기 |
  | `plugin-sdk/param-readers` | 파라미터 리더 | 공통 tool/CLI 파라미터 리더 |
  | `plugin-sdk/tool-payload` | tool payload 추출 | tool 결과 객체에서 정규화된 payload 추출 |
  | `plugin-sdk/tool-send` | tool send 추출 | tool 인자에서 정식 send 대상 필드 추출 |
  | `plugin-sdk/temp-path` | 임시 경로 헬퍼 | 공유 temp-download 경로 헬퍼 |
  | `plugin-sdk/logging-core` | 로깅 헬퍼 | subsystem logger 및 redaction 헬퍼 |
  | `plugin-sdk/markdown-table-runtime` | markdown-table 헬퍼 | markdown 표 모드 헬퍼 |
  | `plugin-sdk/reply-payload` | 메시지 reply 타입 | reply payload 타입 |
  | `plugin-sdk/provider-setup` | 엄선된 local/self-hosted provider setup 헬퍼 | self-hosted provider 탐색/config 헬퍼 |
  | `plugin-sdk/self-hosted-provider-setup` | 집중된 OpenAI-compatible self-hosted provider setup 헬퍼 | 동일한 self-hosted provider 탐색/config 헬퍼 |
  | `plugin-sdk/provider-auth-runtime` | provider runtime auth 헬퍼 | runtime API key 확인 헬퍼 |
  | `plugin-sdk/provider-auth-api-key` | provider API key setup 헬퍼 | API key 온보딩/profile-write 헬퍼 |
  | `plugin-sdk/provider-auth-result` | provider auth-result 헬퍼 | 표준 OAuth auth-result 빌더 |
  | `plugin-sdk/provider-auth-login` | provider interactive login 헬퍼 | 공유 interactive login 헬퍼 |
  | `plugin-sdk/provider-env-vars` | provider env-var 헬퍼 | provider auth env-var 조회 헬퍼 |
  | `plugin-sdk/provider-model-shared` | 공유 provider model/replay 헬퍼 | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, 공유 replay-policy 빌더, provider-endpoint 헬퍼, model-id 정규화 헬퍼 |
  | `plugin-sdk/provider-catalog-shared` | 공유 provider catalog 헬퍼 | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | provider 온보딩 패치 | 온보딩 config 헬퍼 |
  | `plugin-sdk/provider-http` | provider HTTP 헬퍼 | 범용 provider HTTP/endpoint capability 헬퍼 |
  | `plugin-sdk/provider-web-fetch` | provider web-fetch 헬퍼 | web-fetch provider 등록/cache 헬퍼 |
  | `plugin-sdk/provider-web-search-config-contract` | provider web-search config 헬퍼 | plugin-enable wiring이 필요 없는 provider를 위한 좁은 범위의 web-search config/credential 헬퍼 |
  | `plugin-sdk/provider-web-search-contract` | provider web-search 계약 헬퍼 | `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`, 범위가 지정된 credential setter/getter 같은 좁은 범위의 web-search config/credential 계약 헬퍼 |
  | `plugin-sdk/provider-web-search` | provider web-search 헬퍼 | web-search provider 등록/cache/runtime 헬퍼 |
  | `plugin-sdk/provider-tools` | provider tool/schema compat 헬퍼 | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schema 정리 + diagnostics, 그리고 `resolveXaiModelCompatPatch` / `applyXaiModelCompat` 같은 xAI compat 헬퍼 |
  | `plugin-sdk/provider-usage` | provider 사용량 헬퍼 | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`, 그리고 기타 provider 사용량 헬퍼 |
  | `plugin-sdk/provider-stream` | provider stream wrapper 헬퍼 | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper 타입, 그리고 공유 Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper 헬퍼 |
  | `plugin-sdk/keyed-async-queue` | 순서가 보장되는 async queue | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 공유 media 헬퍼 | media fetch/transform/store 헬퍼와 media payload 빌더 |
  | `plugin-sdk/media-generation-runtime` | 공유 media-generation 헬퍼 | 이미지/비디오/음악 생성용 공유 failover 헬퍼, candidate 선택, missing-model 메시지 |
  | `plugin-sdk/media-understanding` | media-understanding 헬퍼 | media understanding provider 타입과 provider 대상 image/audio 헬퍼 export |
  | `plugin-sdk/text-runtime` | 공유 text 헬퍼 | assistant-visible-text 제거, markdown 렌더링/청킹/표 헬퍼, redaction 헬퍼, directive-tag 헬퍼, safe-text 유틸리티, 그리고 관련 text/logging 헬퍼 |
  | `plugin-sdk/text-chunking` | 텍스트 청킹 헬퍼 | outbound 텍스트 청킹 헬퍼 |
  | `plugin-sdk/speech` | speech 헬퍼 | speech provider 타입과 provider 대상 directive, registry, validation 헬퍼 |
  | `plugin-sdk/speech-core` | 공유 speech 코어 | speech provider 타입, registry, directive, 정규화 |
  | `plugin-sdk/realtime-transcription` | realtime transcription 헬퍼 | provider 타입과 registry 헬퍼 |
  | `plugin-sdk/realtime-voice` | realtime voice 헬퍼 | provider 타입과 registry 헬퍼 |
  | `plugin-sdk/image-generation-core` | 공유 image-generation 코어 | image-generation 타입, failover, auth, registry 헬퍼 |
  | `plugin-sdk/music-generation` | music-generation 헬퍼 | music-generation provider/request/result 타입 |
  | `plugin-sdk/music-generation-core` | 공유 music-generation 코어 | music-generation 타입, failover 헬퍼, provider 조회, model-ref 파싱 |
  | `plugin-sdk/video-generation` | video-generation 헬퍼 | video-generation provider/request/result 타입 |
  | `plugin-sdk/video-generation-core` | 공유 video-generation 코어 | video-generation 타입, failover 헬퍼, provider 조회, model-ref 파싱 |
  | `plugin-sdk/interactive-runtime` | interactive reply 헬퍼 | interactive reply payload 정규화/축소 |
  | `plugin-sdk/channel-config-primitives` | channel config 기본 요소 | 좁은 범위의 channel config-schema 기본 요소 |
  | `plugin-sdk/channel-config-writes` | channel config-write 헬퍼 | channel config-write 권한 부여 헬퍼 |
  | `plugin-sdk/channel-plugin-common` | 공유 channel prelude | 공유 channel plugin prelude export |
  | `plugin-sdk/channel-status` | channel 상태 헬퍼 | 공유 channel 상태 스냅샷/요약 헬퍼 |
  | `plugin-sdk/allowlist-config-edit` | Allowlist config 헬퍼 | Allowlist config 편집/읽기 헬퍼 |
  | `plugin-sdk/group-access` | 그룹 액세스 헬퍼 | 공유 group-access 결정 헬퍼 |
  | `plugin-sdk/direct-dm` | direct-DM 헬퍼 | 공유 direct-DM auth/guard 헬퍼 |
  | `plugin-sdk/extension-shared` | 공유 extension 헬퍼 | passive-channel/status 및 ambient proxy 헬퍼 기본 요소 |
  | `plugin-sdk/webhook-targets` | Webhook 대상 헬퍼 | Webhook 대상 레지스트리 및 route-install 헬퍼 |
  | `plugin-sdk/webhook-path` | Webhook 경로 헬퍼 | Webhook 경로 정규화 헬퍼 |
  | `plugin-sdk/web-media` | 공유 web media 헬퍼 | remote/local media 로딩 헬퍼 |
  | `plugin-sdk/zod` | Zod 재수출 | Plugin SDK 사용자를 위한 재수출된 `zod` |
  | `plugin-sdk/memory-core` | 번들 memory-core 헬퍼 | 메모리 관리자/config/file/CLI 헬퍼 표면 |
  | `plugin-sdk/memory-core-engine-runtime` | 메모리 엔진 runtime 파사드 | 메모리 index/search runtime 파사드 |
  | `plugin-sdk/memory-core-host-engine-foundation` | 메모리 호스트 foundation 엔진 | 메모리 호스트 foundation 엔진 export |
  | `plugin-sdk/memory-core-host-engine-embeddings` | 메모리 호스트 임베딩 엔진 | 메모리 임베딩 계약, registry 접근, local provider, 범용 batch/remote 헬퍼. 구체적인 remote provider는 해당 plugin에 있습니다 |
  | `plugin-sdk/memory-core-host-engine-qmd` | 메모리 호스트 QMD 엔진 | 메모리 호스트 QMD 엔진 export |
  | `plugin-sdk/memory-core-host-engine-storage` | 메모리 호스트 storage 엔진 | 메모리 호스트 storage 엔진 export |
  | `plugin-sdk/memory-core-host-multimodal` | 메모리 호스트 멀티모달 헬퍼 | 메모리 호스트 멀티모달 헬퍼 |
  | `plugin-sdk/memory-core-host-query` | 메모리 호스트 쿼리 헬퍼 | 메모리 호스트 쿼리 헬퍼 |
  | `plugin-sdk/memory-core-host-secret` | 메모리 호스트 secret 헬퍼 | 메모리 호스트 secret 헬퍼 |
  | `plugin-sdk/memory-core-host-events` | 메모리 호스트 이벤트 저널 헬퍼 | 메모리 호스트 이벤트 저널 헬퍼 |
  | `plugin-sdk/memory-core-host-status` | 메모리 호스트 상태 헬퍼 | 메모리 호스트 상태 헬퍼 |
  | `plugin-sdk/memory-core-host-runtime-cli` | 메모리 호스트 CLI runtime | 메모리 호스트 CLI runtime 헬퍼 |
  | `plugin-sdk/memory-core-host-runtime-core` | 메모리 호스트 코어 runtime | 메모리 호스트 코어 runtime 헬퍼 |
  | `plugin-sdk/memory-core-host-runtime-files` | 메모리 호스트 파일/runtime 헬퍼 | 메모리 호스트 파일/runtime 헬퍼 |
  | `plugin-sdk/memory-host-core` | 메모리 호스트 코어 runtime 별칭 | 메모리 호스트 코어 runtime 헬퍼를 위한 vendor-neutral 별칭 |
  | `plugin-sdk/memory-host-events` | 메모리 호스트 이벤트 저널 별칭 | 메모리 호스트 이벤트 저널 헬퍼를 위한 vendor-neutral 별칭 |
  | `plugin-sdk/memory-host-files` | 메모리 호스트 파일/runtime 별칭 | 메모리 호스트 파일/runtime 헬퍼를 위한 vendor-neutral 별칭 |
  | `plugin-sdk/memory-host-markdown` | 관리형 markdown 헬퍼 | 메모리 인접 plugin용 공유 관리형 markdown 헬퍼 |
  | `plugin-sdk/memory-host-search` | Active Memory 검색 파사드 | lazy Active Memory search-manager runtime 파사드 |
  | `plugin-sdk/memory-host-status` | 메모리 호스트 상태 별칭 | 메모리 호스트 상태 헬퍼를 위한 vendor-neutral 별칭 |
  | `plugin-sdk/memory-lancedb` | 번들 memory-lancedb 헬퍼 | memory-lancedb 헬퍼 표면 |
  | `plugin-sdk/testing` | 테스트 유틸리티 | 테스트 헬퍼 및 mock |
</Accordion>

이 표는 전체 SDK 표면이 아니라, 의도적으로 공통 마이그레이션 하위 집합만 담고 있습니다. 200개가 넘는 전체 엔트리포인트 목록은 `scripts/lib/plugin-sdk-entrypoints.json`에 있습니다.

그 목록에는 여전히 `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`, `plugin-sdk/zalo-setup`, `plugin-sdk/matrix*` 같은 일부 번들 plugin 헬퍼 seam이 포함되어 있습니다. 이들은 번들 plugin 유지보수와 호환성을 위해 계속 export되지만, 공통 마이그레이션 표에서는 의도적으로 제외되어 있으며 새 plugin 코드에 권장되는 대상은 아닙니다.

같은 규칙이 다음과 같은 다른 번들 헬퍼 계열에도 적용됩니다.

- 브라우저 지원 헬퍼: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- 번들 헬퍼/plugin 표면: `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call`

현재 `plugin-sdk/github-copilot-token`은 좁은 범위의 token-helper 표면인 `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, `resolveCopilotApiToken`을 노출합니다.

작업에 맞는 가장 좁은 import를 사용하세요. export를 찾을 수 없다면 `src/plugin-sdk/`의 소스를 확인하거나 Discord에서 문의하세요.

## 제거 일정

| 시점 | 발생하는 일 |
| ---------------------- | ----------------------------------------------------------------------- |
| **현재** | deprecated 표면이 런타임 경고를 출력합니다 |
| **다음 major release** | deprecated 표면이 제거되며, 여전히 이를 사용하는 plugin은 실패합니다 |

모든 core plugin은 이미 마이그레이션되었습니다. 외부 plugin은 다음 major release 전에 마이그레이션해야 합니다.

## 경고를 일시적으로 숨기기

마이그레이션 작업 중에는 다음 환경 변수를 설정하세요.

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

이는 영구적인 해결책이 아니라, 일시적인 우회 수단입니다.

## 관련 문서

- [시작하기](/ko/plugins/building-plugins) — 첫 번째 plugin 만들기
- [SDK 개요](/ko/plugins/sdk-overview) — 전체 subpath import 참조
- [Channel Plugins](/ko/plugins/sdk-channel-plugins) — channel plugin 만들기
- [Provider Plugins](/ko/plugins/sdk-provider-plugins) — provider plugin 만들기
- [Plugin 내부 구조](/ko/plugins/architecture) — 아키텍처 심화 설명
- [Plugin Manifest](/ko/plugins/manifest) — manifest schema 참조
