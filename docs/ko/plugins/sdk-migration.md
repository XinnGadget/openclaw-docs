---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED 경고가 표시됨
    - OPENCLAW_EXTENSION_API_DEPRECATED 경고가 표시됨
    - plugin을 최신 plugin 아키텍처로 업데이트하는 중
    - 외부 OpenClaw plugin을 유지보수하는 중
sidebarTitle: Migrate to SDK
summary: 레거시 하위 호환성 계층에서 최신 plugin SDK로 마이그레이션
title: Plugin SDK Migration
x-i18n:
    generated_at: "2026-04-05T12:50:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: c420b8d7de17aee16c5aa67e3a88da5750f0d84b07dd541f061081080e081196
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK Migration

OpenClaw는 넓은 범위의 하위 호환성 계층에서 집중적이고 문서화된 import를 사용하는 최신 plugin
아키텍처로 이동했습니다. 새 아키텍처 이전에 plugin을 만들었다면
이 가이드를 통해 마이그레이션할 수 있습니다.

## 무엇이 바뀌고 있나요

이전 plugin 시스템은 plugin이 단일 진입점에서
필요한 모든 것을 import할 수 있도록 하는 두 개의 매우 넓은 표면을 제공했습니다.

- **`openclaw/plugin-sdk/compat`** — 수십 개의
  helper를 재export하는 단일 import. 새 plugin 아키텍처가 구축되는 동안
  이전 hook 기반 plugins가 계속 동작하게 하기 위해 도입되었습니다.
- **`openclaw/extension-api`** — plugin이 임베디드 agent runner 같은
  호스트 측 helper에 직접 접근할 수 있게 해 주는 브리지.

이 두 표면은 이제 모두 **deprecated**되었습니다. 런타임에서는 여전히 동작하지만, 새
plugins는 이를 사용해서는 안 되며, 기존 plugins는 다음 major release에서 제거되기 전에 마이그레이션해야 합니다.

<Warning>
  하위 호환성 계층은 향후 major release에서 제거될 예정입니다.
  이 표면에서 여전히 import하는 plugins는 그 시점에 동작이 깨집니다.
</Warning>

## 왜 이렇게 바뀌었나요

기존 접근 방식은 여러 문제를 일으켰습니다:

- **느린 시작 속도** — helper 하나를 import하면 관련 없는 수십 개의 모듈이 로드됨
- **순환 의존성** — 광범위한 재export 때문에 import cycle을 쉽게 만들 수 있었음
- **불분명한 API 표면** — 어떤 export가 안정적인지, 어떤 것이 내부용인지 구분할 수 없었음

최신 plugin SDK는 이를 해결합니다: 각 import 경로(`openclaw/plugin-sdk/\<subpath\>`)는
명확한 목적과 문서화된 계약을 가진 작고 독립적인 모듈입니다.

번들 채널용 레거시 provider 편의 seam도 제거되었습니다. `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
채널 브랜드 helper seams,
`openclaw/plugin-sdk/telegram-core` 같은 import는
안정적인 plugin 계약이 아니라 private mono-repo 단축 경로였습니다. 대신 좁고 일반적인 SDK subpath를 사용하세요. 번들 plugin workspace 내부에서는 provider가 소유하는 helper를 해당 plugin의
자체 `api.ts` 또는 `runtime-api.ts`에 두세요.

현재 번들 provider 예시:

- Anthropic은 Claude 전용 stream helper를 자체 `api.ts` /
  `contract-api.ts` seam에 유지
- OpenAI는 provider builder, default-model helper, realtime provider
  builder를 자체 `api.ts`에 유지
- OpenRouter는 provider builder와 onboarding/config helper를 자체
  `api.ts`에 유지

## 마이그레이션 방법

<Steps>
  <Step title="Windows wrapper fallback 동작 감사">
    plugin이 `openclaw/plugin-sdk/windows-spawn`을 사용한다면, 확인되지 않은 Windows
    `.cmd`/`.bat` wrapper는 이제 명시적으로
    `allowShellFallback: true`를 전달하지 않는 한 fail closed 처리됩니다.

    ```typescript
    // 이전
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // 이후
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // 셸을 통한 fallback을 의도적으로 허용하는 신뢰된
      // 호환성 호출자에서만 이것을 설정하세요.
      allowShellFallback: true,
    });
    ```

    호출자가 의도적으로 shell fallback에 의존하지 않는다면
    `allowShellFallback`을 설정하지 말고 대신 발생한 오류를 처리하세요.

  </Step>

  <Step title="deprecated import 찾기">
    plugin에서 deprecated된 두 표면 중 하나를 import하는 부분을 검색하세요:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="집중된 import로 교체">
    이전 표면의 각 export는 특정 최신 import 경로에 매핑됩니다:

    ```typescript
    // 이전 (deprecated 하위 호환성 계층)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // 이후 (최신 집중 import)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    호스트 측 helper의 경우 직접 import하지 말고
    주입된 plugin runtime을 사용하세요:

    ```typescript
    // 이전 (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // 이후 (주입된 runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    같은 패턴이 다른 레거시 bridge helper에도 적용됩니다:

    | 이전 import | 최신 대응 |
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

## Import 경로 참조

<Accordion title="일반적인 import 경로 표">
  | Import 경로 | 목적 | 주요 exports |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | 표준 plugin entry helper | `definePluginEntry` |
  | `plugin-sdk/core` | 채널 entry 정의/빌더를 위한 레거시 umbrella 재export | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | 루트 config schema export | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | 단일 provider entry helper | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | 집중된 채널 entry 정의 및 빌더 | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | 공유 setup wizard helper | Allowlist prompts, setup status builders |
  | `plugin-sdk/setup-runtime` | setup 시점 runtime helper | Import-safe setup patch adapters, lookup-note helpers, `promptResolvedAllowFrom`, `splitSetupEntries`, delegated setup proxies |
  | `plugin-sdk/setup-adapter-runtime` | setup adapter helper | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | setup 도구 helper | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | 다중 account helper | Account list/config/action-gate helpers |
  | `plugin-sdk/account-id` | account-id helper | `DEFAULT_ACCOUNT_ID`, account-id normalization |
  | `plugin-sdk/account-resolution` | account lookup helper | Account lookup + default-fallback helpers |
  | `plugin-sdk/account-helpers` | 좁은 범위 account helper | Account list/account-action helpers |
  | `plugin-sdk/channel-setup` | setup wizard adapter | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, plus `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM pairing 기본 요소 | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | 응답 접두사 + typing 연결 | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Config adapter factory | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Config schema builder | Channel config schema types |
  | `plugin-sdk/telegram-command-config` | Telegram 명령 config helper | Command-name normalization, description trimming, duplicate/conflict validation |
  | `plugin-sdk/channel-policy` | 그룹/DM 정책 확인 | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | account 상태 추적 | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | 수신 envelope helper | Shared route + envelope builder helpers |
  | `plugin-sdk/inbound-reply-dispatch` | 수신 응답 helper | Shared record-and-dispatch helpers |
  | `plugin-sdk/messaging-targets` | 메시징 대상 파싱 | Target parsing/matching helpers |
  | `plugin-sdk/outbound-media` | 발신 미디어 helper | Shared outbound media loading |
  | `plugin-sdk/outbound-runtime` | 발신 runtime helper | Outbound identity/send delegate helpers |
  | `plugin-sdk/thread-bindings-runtime` | thread-binding helper | Thread-binding lifecycle and adapter helpers |
  | `plugin-sdk/agent-media-payload` | 레거시 미디어 payload helper | Legacy field layout용 agent media payload builder |
  | `plugin-sdk/channel-runtime` | deprecated 호환성 shim | 레거시 channel runtime utilities 전용 |
  | `plugin-sdk/channel-send-result` | send 결과 타입 | Reply result types |
  | `plugin-sdk/runtime-store` | 영구 plugin 저장소 | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | 광범위한 runtime helper | Runtime/logging/backup/plugin-install helpers |
  | `plugin-sdk/runtime-env` | 좁은 범위 runtime env helper | Logger/runtime env, timeout, retry, and backoff helpers |
  | `plugin-sdk/plugin-runtime` | 공유 plugin runtime helper | Plugin commands/hooks/http/interactive helpers |
  | `plugin-sdk/hook-runtime` | hook pipeline helper | Shared webhook/internal hook pipeline helpers |
  | `plugin-sdk/lazy-runtime` | lazy runtime helper | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | 프로세스 helper | Shared exec helpers |
  | `plugin-sdk/cli-runtime` | CLI runtime helper | Command formatting, waits, version helpers |
  | `plugin-sdk/gateway-runtime` | Gateway helper | Gateway client and channel-status patch helpers |
  | `plugin-sdk/config-runtime` | Config helper | Config load/write helpers |
  | `plugin-sdk/telegram-command-config` | Telegram 명령 helper | 번들 Telegram 계약 표면을 사용할 수 없을 때의 fallback-stable Telegram command validation helpers |
  | `plugin-sdk/approval-runtime` | 승인 프롬프트 helper | Exec/plugin approval payload, approval capability/profile helpers, native approval routing/runtime helpers |
  | `plugin-sdk/approval-auth-runtime` | 승인 인증 helper | Approver resolution, same-chat action auth |
  | `plugin-sdk/approval-client-runtime` | 승인 클라이언트 helper | Native exec approval profile/filter helpers |
  | `plugin-sdk/approval-delivery-runtime` | 승인 전달 helper | Native approval capability/delivery adapters |
  | `plugin-sdk/approval-native-runtime` | 승인 대상 helper | Native approval target/account binding helpers |
  | `plugin-sdk/approval-reply-runtime` | 승인 응답 helper | Exec/plugin approval reply payload helpers |
  | `plugin-sdk/security-runtime` | 보안 helper | Shared trust, DM gating, external-content, and secret-collection helpers |
  | `plugin-sdk/ssrf-policy` | SSRF 정책 helper | Host allowlist and private-network policy helpers |
  | `plugin-sdk/ssrf-runtime` | SSRF runtime helper | Pinned-dispatcher, guarded fetch, SSRF policy helpers |
  | `plugin-sdk/collection-runtime` | 제한된 캐시 helper | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | 진단 게이팅 helper | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | 오류 형식화 helper | `formatUncaughtError`, `isApprovalNotFoundError`, error graph helpers |
  | `plugin-sdk/fetch-runtime` | 래핑된 fetch/proxy helper | `resolveFetch`, proxy helpers |
  | `plugin-sdk/host-runtime` | 호스트 normalization helper | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | retry helper | `RetryConfig`, `retryAsync`, policy runners |
  | `plugin-sdk/allow-from` | Allowlist 형식화 | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist 입력 매핑 | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | 명령 게이팅 및 command-surface helper | `resolveControlCommandGate`, sender-authorization helpers, command registry helpers |
  | `plugin-sdk/secret-input` | secret 입력 파싱 | Secret input helpers |
  | `plugin-sdk/webhook-ingress` | webhook 요청 helper | Webhook target utilities |
  | `plugin-sdk/webhook-request-guards` | webhook 본문 가드 helper | Request body read/limit helpers |
  | `plugin-sdk/reply-runtime` | 공유 reply runtime | Inbound dispatch, heartbeat, reply planner, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | 좁은 범위 reply dispatch helper | Finalize + provider dispatch helpers |
  | `plugin-sdk/reply-history` | reply-history helper | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | reply reference 계획 | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | reply chunk helper | Text/markdown chunking helpers |
  | `plugin-sdk/session-store-runtime` | session store helper | Store path + updated-at helpers |
  | `plugin-sdk/state-paths` | 상태 경로 helper | State and OAuth dir helpers |
  | `plugin-sdk/routing` | 라우팅/session-key helper | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, session-key normalization helpers |
  | `plugin-sdk/status-helpers` | 채널 상태 helper | Channel/account status summary builders, runtime-state defaults, issue metadata helpers |
  | `plugin-sdk/target-resolver-runtime` | target resolver helper | Shared target resolver helpers |
  | `plugin-sdk/string-normalization-runtime` | 문자열 normalization helper | Slug/string normalization helpers |
  | `plugin-sdk/request-url` | 요청 URL helper | request-like 입력에서 문자열 URL 추출 |
  | `plugin-sdk/run-command` | 시간 제한 명령 helper | Timed command runner with normalized stdout/stderr |
  | `plugin-sdk/param-readers` | 매개변수 reader | Common tool/CLI param readers |
  | `plugin-sdk/tool-send` | 도구 send 추출 | 도구 args에서 표준 send target field 추출 |
  | `plugin-sdk/temp-path` | 임시 경로 helper | Shared temp-download path helpers |
  | `plugin-sdk/logging-core` | 로깅 helper | Subsystem logger and redaction helpers |
  | `plugin-sdk/markdown-table-runtime` | markdown-table helper | Markdown table mode helpers |
  | `plugin-sdk/reply-payload` | 메시지 reply 타입 | Reply payload types |
  | `plugin-sdk/provider-setup` | 선별된 로컬/self-hosted provider setup helper | Self-hosted provider discovery/config helpers |
  | `plugin-sdk/self-hosted-provider-setup` | 집중된 OpenAI-compatible self-hosted provider setup helper | Same self-hosted provider discovery/config helpers |
  | `plugin-sdk/provider-auth-runtime` | provider runtime auth helper | Runtime API-key resolution helpers |
  | `plugin-sdk/provider-auth-api-key` | provider API-key setup helper | API-key onboarding/profile-write helpers |
  | `plugin-sdk/provider-auth-result` | provider auth-result helper | Standard OAuth auth-result builder |
  | `plugin-sdk/provider-auth-login` | provider 대화형 login helper | Shared interactive login helpers |
  | `plugin-sdk/provider-env-vars` | provider env-var helper | Provider auth env-var lookup helpers |
  | `plugin-sdk/provider-model-shared` | 공유 provider model/replay helper | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, shared replay-policy builders, provider-endpoint helpers, and model-id normalization helpers |
  | `plugin-sdk/provider-catalog-shared` | 공유 provider catalog helper | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | provider onboarding patch | Onboarding config helpers |
  | `plugin-sdk/provider-http` | provider HTTP helper | Generic provider HTTP/endpoint capability helpers |
  | `plugin-sdk/provider-web-fetch` | provider web-fetch helper | Web-fetch provider registration/cache helpers |
  | `plugin-sdk/provider-web-search` | provider web-search helper | Web-search provider registration/cache/config helpers |
  | `plugin-sdk/provider-tools` | provider tool/schema compat helper | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini schema cleanup + diagnostics, and xAI compat helpers such as `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | provider 사용량 helper | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`, and other provider usage helpers |
  | `plugin-sdk/provider-stream` | provider stream wrapper helper | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper types, and shared Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper helpers |
  | `plugin-sdk/keyed-async-queue` | 순서가 보장된 async 큐 | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | 공유 미디어 helper | Media fetch/transform/store helpers plus media payload builders |
  | `plugin-sdk/media-understanding` | media-understanding helper | Media understanding provider types plus provider-facing image/audio helper exports |
  | `plugin-sdk/text-runtime` | 공유 텍스트 helper | Assistant-visible-text stripping, markdown render/chunking/table helpers, redaction helpers, directive-tag helpers, safe-text utilities, and related text/logging helpers |
  | `plugin-sdk/text-chunking` | 텍스트 chunking helper | Outbound text chunking helper |
  | `plugin-sdk/speech` | 음성 helper | Speech provider types plus provider-facing directive, registry, and validation helpers |
  | `plugin-sdk/speech-core` | 공유 speech core | Speech provider types, registry, directives, normalization |
  | `plugin-sdk/realtime-transcription` | realtime transcription helper | Provider types and registry helpers |
  | `plugin-sdk/realtime-voice` | realtime voice helper | Provider types and registry helpers |
  | `plugin-sdk/image-generation-core` | 공유 이미지 생성 core | Image-generation types, failover, auth, and registry helpers |
  | `plugin-sdk/video-generation` | 비디오 생성 helper | Video-generation provider/request/result types |
  | `plugin-sdk/video-generation-core` | 공유 비디오 생성 core | Video-generation types, failover helpers, provider lookup, and model-ref parsing |
  | `plugin-sdk/interactive-runtime` | 인터랙티브 reply helper | Interactive reply payload normalization/reduction |
  | `plugin-sdk/channel-config-primitives` | channel config 기본 요소 | Narrow channel config-schema primitives |
  | `plugin-sdk/channel-config-writes` | channel config-write helper | Channel config-write authorization helpers |
  | `plugin-sdk/channel-plugin-common` | 공유 channel prelude | Shared channel plugin prelude exports |
  | `plugin-sdk/channel-status` | channel 상태 helper | Shared channel status snapshot/summary helpers |
  | `plugin-sdk/allowlist-config-edit` | allowlist config helper | Allowlist config edit/read helpers |
  | `plugin-sdk/group-access` | 그룹 접근 helper | Shared group-access decision helpers |
  | `plugin-sdk/direct-dm` | direct-DM helper | Shared direct-DM auth/guard helpers |
  | `plugin-sdk/extension-shared` | 공유 extension helper | Passive-channel/status helper primitives |
  | `plugin-sdk/webhook-targets` | webhook target helper | Webhook target registry and route-install helpers |
  | `plugin-sdk/webhook-path` | webhook 경로 helper | Webhook path normalization helpers |
  | `plugin-sdk/web-media` | 공유 웹 미디어 helper | Remote/local media loading helpers |
  | `plugin-sdk/zod` | Zod 재export | plugin SDK 소비자를 위한 재export된 `zod` |
  | `plugin-sdk/memory-core` | 번들 memory-core helper | Memory manager/config/file/CLI helper surface |
  | `plugin-sdk/memory-core-engine-runtime` | memory engine runtime facade | Memory index/search runtime facade |
  | `plugin-sdk/memory-core-host-engine-foundation` | memory host foundation engine | Memory host foundation engine exports |
  | `plugin-sdk/memory-core-host-engine-embeddings` | memory host embedding engine | Memory host embedding engine exports |
  | `plugin-sdk/memory-core-host-engine-qmd` | memory host QMD engine | Memory host QMD engine exports |
  | `plugin-sdk/memory-core-host-engine-storage` | memory host storage engine | Memory host storage engine exports |
  | `plugin-sdk/memory-core-host-multimodal` | memory host multimodal helper | Memory host multimodal helpers |
  | `plugin-sdk/memory-core-host-query` | memory host query helper | Memory host query helpers |
  | `plugin-sdk/memory-core-host-secret` | memory host secret helper | Memory host secret helpers |
  | `plugin-sdk/memory-core-host-status` | memory host status helper | Memory host status helpers |
  | `plugin-sdk/memory-core-host-runtime-cli` | memory host CLI runtime | Memory host CLI runtime helpers |
  | `plugin-sdk/memory-core-host-runtime-core` | memory host core runtime | Memory host core runtime helpers |
  | `plugin-sdk/memory-core-host-runtime-files` | memory host file/runtime helper | Memory host file/runtime helpers |
  | `plugin-sdk/memory-lancedb` | 번들 memory-lancedb helper | Memory-lancedb helper surface |
  | `plugin-sdk/testing` | 테스트 유틸리티 | Test helpers and mocks |
</Accordion>

이 표는 전체 SDK
표면이 아니라 의도적으로 일반적인 마이그레이션 하위 집합만 담고 있습니다. 200개가 넘는 전체 entrypoint 목록은
`scripts/lib/plugin-sdk-entrypoints.json`에 있습니다.

그 목록에는 여전히
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, `plugin-sdk/matrix*` 같은 일부 번들 plugin helper seam도 포함됩니다. 이들은
번들 plugin 유지보수와 호환성을 위해 계속 export되지만, 의도적으로
일반 마이그레이션 표에서는 제외되어 있으며 새 plugin 코드의
권장 대상은 아닙니다.

같은 규칙은 다른 번들 helper 계열에도 적용됩니다:

- browser 지원 helper: `plugin-sdk/browser-config-support`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- 번들 helper/plugin 표면: `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token`은 현재 좁은 범위의 token-helper
표면인 `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken`, `resolveCopilotApiToken`을 노출합니다.

작업에 맞는 가장 좁은 import를 사용하세요. export를 찾을 수 없다면
`src/plugin-sdk/`의 소스를 확인하거나 Discord에서 물어보세요.

## 제거 일정

| 시점                   | 발생하는 일                                                            |
| ---------------------- | ---------------------------------------------------------------------- |
| **지금**               | deprecated 표면이 런타임 경고를 출력함                                 |
| **다음 major release** | deprecated 표면이 제거되며, 여전히 사용 중인 plugins는 실패함          |

모든 core plugins는 이미 마이그레이션되었습니다. 외부 plugins는
다음 major release 전에 마이그레이션해야 합니다.

## 경고를 일시적으로 숨기기

마이그레이션 작업 중에는 다음 환경 변수를 설정하세요:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

이것은 영구적인 해결책이 아니라 임시 탈출구입니다.

## 관련 문서

- [Getting Started](/plugins/building-plugins) — 첫 plugin 만들기
- [SDK Overview](/plugins/sdk-overview) — 전체 subpath import 참조
- [Channel Plugins](/plugins/sdk-channel-plugins) — channel plugins 만들기
- [Provider Plugins](/plugins/sdk-provider-plugins) — provider plugins 만들기
- [Plugin Internals](/plugins/architecture) — 아키텍처 심화 설명
- [Plugin Manifest](/plugins/manifest) — manifest schema 참조
