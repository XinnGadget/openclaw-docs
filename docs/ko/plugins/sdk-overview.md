---
read_when:
    - 어느 SDK 하위 경로에서 임포트해야 하는지 알아야 할 때
    - OpenClawPluginApi의 모든 등록 메서드에 대한 참조가 필요할 때
    - 특정 SDK export를 찾고 있을 때
sidebarTitle: SDK Overview
summary: 임포트 맵, 등록 API 참조 및 SDK 아키텍처
title: Plugin SDK 개요
x-i18n:
    generated_at: "2026-04-05T12:53:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0d7d8b6add0623766d36e81588ae783b525357b2f5245c38c8e2b07c5fc1d2b5
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK 개요

plugin SDK는 플러그인과 코어 사이의 타입 지정된 계약입니다. 이 페이지는
**무엇을 임포트해야 하는지**와 **무엇을 등록할 수 있는지**에 대한 참조입니다.

<Tip>
  **방법 안내를 찾고 계신가요?**
  - 첫 번째 플러그인인가요? [시작하기](/ko/plugins/building-plugins)부터 시작하세요
  - 채널 플러그인인가요? [채널 플러그인](/ko/plugins/sdk-channel-plugins)을 참고하세요
  - 프로바이더 플러그인인가요? [프로바이더 플러그인](/plugins/sdk-provider-plugins)을 참고하세요
</Tip>

## 임포트 규칙

항상 특정 하위 경로에서 임포트하세요:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

각 하위 경로는 작고 독립적인 모듈입니다. 이렇게 하면 시작 속도가 빨라지고
순환 의존성 문제를 방지할 수 있습니다. 채널별 엔트리/빌드 헬퍼의 경우
`openclaw/plugin-sdk/channel-core`를 우선 사용하고, 더 넓은 우산형 표면과
`buildChannelConfigSchema` 같은 공용 헬퍼에는 `openclaw/plugin-sdk/core`를
사용하세요.

`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` 같은
프로바이더 이름이 붙은 편의 seam이나 채널 브랜드 헬퍼 seam을 추가하거나
의존하지 마세요. 번들 플러그인은 자체 `api.ts` 또는 `runtime-api.ts`
barrel 내부에서 일반적인 SDK 하위 경로를 조합해야 하며, 코어는 해당 필요가
정말로 채널 간 공통인 경우에만 그 플러그인 로컬 barrel을 사용하거나
좁은 범위의 일반 SDK 계약을 추가해야 합니다.

생성된 export 맵에는 여전히 `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup`, `plugin-sdk/matrix*` 같은
소수의 번들 플러그인 헬퍼 seam이 포함되어 있습니다. 이러한 하위 경로는
번들 플러그인 유지 관리와 호환성을 위해서만 존재하며, 아래의 공통 표에서는
의도적으로 제외되어 있고 새 서드파티 플러그인에 권장되는 임포트 경로가
아닙니다.

## 하위 경로 참조

용도별로 그룹화한, 가장 자주 사용되는 하위 경로입니다. 생성된 전체 목록
200개 이상의 하위 경로는 `scripts/lib/plugin-sdk-entrypoints.json`에
있습니다.

예약된 번들 플러그인 헬퍼 하위 경로는 여전히 생성된 목록에 표시됩니다.
문서 페이지에서 명시적으로 공개용으로 안내하지 않는 한, 이를 구현 세부 사항/
호환성 표면으로 취급하세요.

### 플러그인 엔트리

| 하위 경로                  | 주요 export                                                                                                                           |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="채널 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | 루트 `openclaw.json` Zod 스키마 export (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, 그리고 `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | 공용 설정 마법사 헬퍼, allowlist 프롬프트, 설정 상태 빌더 |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | 다중 계정 config/action-gate 헬퍼, 기본 계정 폴백 헬퍼 |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, account-id 정규화 헬퍼 |
    | `plugin-sdk/account-resolution` | 계정 조회 + 기본값 폴백 헬퍼 |
    | `plugin-sdk/account-helpers` | 좁은 범위의 account-list/account-action 헬퍼 |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | 채널 config 스키마 타입 |
    | `plugin-sdk/telegram-command-config` | 번들 계약 폴백이 포함된 Telegram 사용자 지정 명령 정규화/검증 헬퍼 |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | 공용 인바운드 라우트 + 엔벌로프 빌더 헬퍼 |
    | `plugin-sdk/inbound-reply-dispatch` | 공용 인바운드 기록 및 디스패치 헬퍼 |
    | `plugin-sdk/messaging-targets` | 대상 파싱/매칭 헬퍼 |
    | `plugin-sdk/outbound-media` | 공용 아웃바운드 미디어 로딩 헬퍼 |
    | `plugin-sdk/outbound-runtime` | 아웃바운드 identity/send delegate 헬퍼 |
    | `plugin-sdk/thread-bindings-runtime` | 스레드 바인딩 수명 주기 및 어댑터 헬퍼 |
    | `plugin-sdk/agent-media-payload` | 레거시 에이전트 미디어 페이로드 빌더 |
    | `plugin-sdk/conversation-runtime` | 대화/스레드 바인딩, 페어링 및 구성된 바인딩 헬퍼 |
    | `plugin-sdk/runtime-config-snapshot` | 런타임 config 스냅샷 헬퍼 |
    | `plugin-sdk/runtime-group-policy` | 런타임 그룹 정책 해결 헬퍼 |
    | `plugin-sdk/channel-status` | 공용 채널 상태 스냅샷/요약 헬퍼 |
    | `plugin-sdk/channel-config-primitives` | 좁은 범위의 채널 config-schema 프리미티브 |
    | `plugin-sdk/channel-config-writes` | 채널 config 쓰기 권한 부여 헬퍼 |
    | `plugin-sdk/channel-plugin-common` | 공용 채널 플러그인 프렐류드 export |
    | `plugin-sdk/allowlist-config-edit` | allowlist config 편집/읽기 헬퍼 |
    | `plugin-sdk/group-access` | 공용 그룹 액세스 결정 헬퍼 |
    | `plugin-sdk/direct-dm` | 공용 직접 DM auth/guard 헬퍼 |
    | `plugin-sdk/interactive-runtime` | 대화형 응답 페이로드 정규화/축소 헬퍼 |
    | `plugin-sdk/channel-inbound` | 디바운스, 멘션 매칭, 엔벌로프 헬퍼 |
    | `plugin-sdk/channel-send-result` | 응답 결과 타입 |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | 대상 파싱/매칭 헬퍼 |
    | `plugin-sdk/channel-contract` | 채널 계약 타입 |
    | `plugin-sdk/channel-feedback` | 피드백/리액션 연결 |
  </Accordion>

  <Accordion title="프로바이더 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | 선별된 로컬/셀프 호스팅 프로바이더 설정 헬퍼 |
    | `plugin-sdk/self-hosted-provider-setup` | OpenAI 호환 셀프 호스팅 프로바이더 설정에 초점을 맞춘 헬퍼 |
    | `plugin-sdk/cli-backend` | CLI 백엔드 기본값 + watchdog 상수 |
    | `plugin-sdk/provider-auth-runtime` | 프로바이더 플러그인을 위한 런타임 API 키 해결 헬퍼 |
    | `plugin-sdk/provider-auth-api-key` | API 키 온보딩/프로필 쓰기 헬퍼 |
    | `plugin-sdk/provider-auth-result` | 표준 OAuth auth-result 빌더 |
    | `plugin-sdk/provider-auth-login` | 프로바이더 플러그인을 위한 공용 대화형 로그인 헬퍼 |
    | `plugin-sdk/provider-env-vars` | 프로바이더 auth env-var 조회 헬퍼 |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, 공용 replay-policy 빌더, provider-endpoint 헬퍼, 그리고 `normalizeNativeXaiModelId` 같은 model-id 정규화 헬퍼 |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | 일반 프로바이더 HTTP/엔드포인트 기능 헬퍼 |
    | `plugin-sdk/provider-web-fetch` | 웹 fetch 프로바이더 등록/캐시 헬퍼 |
    | `plugin-sdk/provider-web-search` | 웹 검색 프로바이더 등록/캐시/config 헬퍼 |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini 스키마 정리 + 진단, 그리고 `resolveXaiModelCompatPatch` / `applyXaiModelCompat` 같은 xAI 호환성 헬퍼 |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` 및 유사 항목 |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, 스트림 래퍼 타입, 그리고 공용 Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot 래퍼 헬퍼 |
    | `plugin-sdk/provider-onboard` | 온보딩 config 패치 헬퍼 |
    | `plugin-sdk/global-singleton` | 프로세스 로컬 singleton/map/cache 헬퍼 |
  </Accordion>

  <Accordion title="인증 및 보안 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, 명령 레지스트리 헬퍼, 발신자 권한 부여 헬퍼 |
    | `plugin-sdk/approval-auth-runtime` | 승인자 해결 및 동일 채팅 action-auth 헬퍼 |
    | `plugin-sdk/approval-client-runtime` | 네이티브 exec 승인 프로필/필터 헬퍼 |
    | `plugin-sdk/approval-delivery-runtime` | 네이티브 승인 기능/전달 어댑터 |
    | `plugin-sdk/approval-native-runtime` | 네이티브 승인 대상 + account-binding 헬퍼 |
    | `plugin-sdk/approval-reply-runtime` | exec/plugin 승인 응답 페이로드 헬퍼 |
    | `plugin-sdk/command-auth-native` | 네이티브 명령 auth + 네이티브 session-target 헬퍼 |
    | `plugin-sdk/command-detection` | 공용 명령 감지 헬퍼 |
    | `plugin-sdk/command-surface` | command-body 정규화 및 command-surface 헬퍼 |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | 공용 신뢰, DM 게이팅, 외부 콘텐츠 및 비밀 수집 헬퍼 |
    | `plugin-sdk/ssrf-policy` | 호스트 allowlist 및 사설 네트워크 SSRF 정책 헬퍼 |
    | `plugin-sdk/ssrf-runtime` | pinned-dispatcher, SSRF 보호 fetch 및 SSRF 정책 헬퍼 |
    | `plugin-sdk/secret-input` | 비밀 입력 파싱 헬퍼 |
    | `plugin-sdk/webhook-ingress` | 웹훅 요청/대상 헬퍼 |
    | `plugin-sdk/webhook-request-guards` | 요청 본문 크기/타임아웃 헬퍼 |
  </Accordion>

  <Accordion title="런타임 및 저장소 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/runtime` | 광범위한 런타임/로깅/백업/플러그인 설치 헬퍼 |
    | `plugin-sdk/runtime-env` | 좁은 범위의 런타임 env, 로거, 타임아웃, 재시도 및 백오프 헬퍼 |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | 공용 플러그인 명령/hook/http/interactive 헬퍼 |
    | `plugin-sdk/hook-runtime` | 공용 웹훅/내부 hook 파이프라인 헬퍼 |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeSurface` 같은 지연 런타임 임포트/바인딩 헬퍼 |
    | `plugin-sdk/process-runtime` | 프로세스 exec 헬퍼 |
    | `plugin-sdk/cli-runtime` | CLI 포맷팅, 대기 및 버전 헬퍼 |
    | `plugin-sdk/gateway-runtime` | 게이트웨이 클라이언트 및 채널 상태 패치 헬퍼 |
    | `plugin-sdk/config-runtime` | config 로드/쓰기 헬퍼 |
    | `plugin-sdk/telegram-command-config` | 번들 Telegram 계약 표면을 사용할 수 없는 경우에도 Telegram 명령 이름/설명 정규화 및 중복/충돌 검사 |
    | `plugin-sdk/approval-runtime` | exec/plugin 승인 헬퍼, 승인 기능 빌더, auth/profile 헬퍼, 네이티브 라우팅/런타임 헬퍼 |
    | `plugin-sdk/reply-runtime` | 공용 인바운드/응답 런타임 헬퍼, 청킹, 디스패치, 하트비트, 응답 플래너 |
    | `plugin-sdk/reply-dispatch-runtime` | 좁은 범위의 응답 디스패치/finalize 헬퍼 |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` 같은 공용 짧은 기간 응답 기록 헬퍼 |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | 좁은 범위의 텍스트/markdown 청킹 헬퍼 |
    | `plugin-sdk/session-store-runtime` | 세션 저장소 경로 + updated-at 헬퍼 |
    | `plugin-sdk/state-paths` | 상태/OAuth 디렉터리 경로 헬퍼 |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId` 같은 라우트/세션 키/계정 바인딩 헬퍼 |
    | `plugin-sdk/status-helpers` | 공용 채널/계정 상태 요약 헬퍼, 런타임 상태 기본값 및 이슈 메타데이터 헬퍼 |
    | `plugin-sdk/target-resolver-runtime` | 공용 대상 해결 헬퍼 |
    | `plugin-sdk/string-normalization-runtime` | 슬러그/문자열 정규화 헬퍼 |
    | `plugin-sdk/request-url` | fetch/request 유사 입력에서 문자열 URL 추출 |
    | `plugin-sdk/run-command` | 정규화된 stdout/stderr 결과를 포함한 시간 제한 명령 실행기 |
    | `plugin-sdk/param-readers` | 공통 tool/CLI 파라미터 리더 |
    | `plugin-sdk/tool-send` | 도구 인수에서 표준 send 대상 필드 추출 |
    | `plugin-sdk/temp-path` | 공용 임시 다운로드 경로 헬퍼 |
    | `plugin-sdk/logging-core` | 서브시스템 로거 및 리덕션 헬퍼 |
    | `plugin-sdk/markdown-table-runtime` | Markdown 표 모드 헬퍼 |
    | `plugin-sdk/json-store` | 작은 JSON 상태 읽기/쓰기 헬퍼 |
    | `plugin-sdk/file-lock` | 재진입 가능한 파일 잠금 헬퍼 |
    | `plugin-sdk/persistent-dedupe` | 디스크 기반 중복 제거 캐시 헬퍼 |
    | `plugin-sdk/acp-runtime` | ACP 런타임/세션 헬퍼 |
    | `plugin-sdk/agent-config-primitives` | 좁은 범위의 에이전트 런타임 config-schema 프리미티브 |
    | `plugin-sdk/boolean-param` | 느슨한 boolean 파라미터 리더 |
    | `plugin-sdk/dangerous-name-runtime` | 위험한 이름 매칭 해결 헬퍼 |
    | `plugin-sdk/device-bootstrap` | 디바이스 부트스트랩 및 페어링 토큰 헬퍼 |
    | `plugin-sdk/extension-shared` | 공용 수동 채널 및 상태 헬퍼 프리미티브 |
    | `plugin-sdk/models-provider-runtime` | `/models` 명령/프로바이더 응답 헬퍼 |
    | `plugin-sdk/skill-commands-runtime` | Skills 명령 목록 헬퍼 |
    | `plugin-sdk/native-command-registry` | 네이티브 명령 레지스트리/빌드/직렬화 헬퍼 |
    | `plugin-sdk/provider-zai-endpoint` | Z.AI 엔드포인트 감지 헬퍼 |
    | `plugin-sdk/infra-runtime` | 시스템 이벤트/하트비트 헬퍼 |
    | `plugin-sdk/collection-runtime` | 작은 범위 제한 캐시 헬퍼 |
    | `plugin-sdk/diagnostic-runtime` | 진단 플래그 및 이벤트 헬퍼 |
    | `plugin-sdk/error-runtime` | 오류 그래프, 포맷팅, 공용 오류 분류 헬퍼, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | 래핑된 fetch, 프록시 및 pinned lookup 헬퍼 |
    | `plugin-sdk/host-runtime` | 호스트명 및 SCP 호스트 정규화 헬퍼 |
    | `plugin-sdk/retry-runtime` | 재시도 config 및 재시도 실행기 헬퍼 |
    | `plugin-sdk/agent-runtime` | 에이전트 디렉터리/ID/워크스페이스 헬퍼 |
    | `plugin-sdk/directory-runtime` | config 기반 디렉터리 조회/중복 제거 |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="기능 및 테스트 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/media-runtime` | 미디어 페이로드 빌더를 포함한 공용 미디어 fetch/transform/store 헬퍼 |
    | `plugin-sdk/media-understanding` | 미디어 이해 프로바이더 타입과 프로바이더용 이미지/오디오 헬퍼 export |
    | `plugin-sdk/text-runtime` | assistant-visible-text 제거, markdown 렌더링/청킹/표 헬퍼, 리덕션 헬퍼, directive-tag 헬퍼 및 safe-text 유틸리티 같은 공용 텍스트/markdown/로깅 헬퍼 |
    | `plugin-sdk/text-chunking` | 아웃바운드 텍스트 청킹 헬퍼 |
    | `plugin-sdk/speech` | 음성 프로바이더 타입과 프로바이더용 directive, registry 및 검증 헬퍼 |
    | `plugin-sdk/speech-core` | 공용 음성 프로바이더 타입, registry, directive 및 정규화 헬퍼 |
    | `plugin-sdk/realtime-transcription` | 실시간 전사 프로바이더 타입 및 레지스트리 헬퍼 |
    | `plugin-sdk/realtime-voice` | 실시간 음성 프로바이더 타입 및 레지스트리 헬퍼 |
    | `plugin-sdk/image-generation` | 이미지 생성 프로바이더 타입 |
    | `plugin-sdk/image-generation-core` | 공용 이미지 생성 타입, 페일오버, auth 및 registry 헬퍼 |
    | `plugin-sdk/video-generation` | 비디오 생성 프로바이더/요청/결과 타입 |
    | `plugin-sdk/video-generation-core` | 공용 비디오 생성 타입, 페일오버 헬퍼, 프로바이더 조회 및 model-ref 파싱 |
    | `plugin-sdk/webhook-targets` | 웹훅 대상 레지스트리 및 route-install 헬퍼 |
    | `plugin-sdk/webhook-path` | 웹훅 경로 정규화 헬퍼 |
    | `plugin-sdk/web-media` | 공용 원격/로컬 미디어 로딩 헬퍼 |
    | `plugin-sdk/zod` | plugin SDK 소비자를 위해 재export된 `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="메모리 하위 경로">
    | 하위 경로 | 주요 export |
    | --- | --- |
    | `plugin-sdk/memory-core` | manager/config/file/CLI 헬퍼를 위한 번들 memory-core 헬퍼 표면 |
    | `plugin-sdk/memory-core-engine-runtime` | 메모리 인덱스/검색 런타임 파사드 |
    | `plugin-sdk/memory-core-host-engine-foundation` | 메모리 호스트 기반 엔진 export |
    | `plugin-sdk/memory-core-host-engine-embeddings` | 메모리 호스트 임베딩 엔진 export |
    | `plugin-sdk/memory-core-host-engine-qmd` | 메모리 호스트 QMD 엔진 export |
    | `plugin-sdk/memory-core-host-engine-storage` | 메모리 호스트 저장소 엔진 export |
    | `plugin-sdk/memory-core-host-multimodal` | 메모리 호스트 멀티모달 헬퍼 |
    | `plugin-sdk/memory-core-host-query` | 메모리 호스트 쿼리 헬퍼 |
    | `plugin-sdk/memory-core-host-secret` | 메모리 호스트 비밀 헬퍼 |
    | `plugin-sdk/memory-core-host-status` | 메모리 호스트 상태 헬퍼 |
    | `plugin-sdk/memory-core-host-runtime-cli` | 메모리 호스트 CLI 런타임 헬퍼 |
    | `plugin-sdk/memory-core-host-runtime-core` | 메모리 호스트 코어 런타임 헬퍼 |
    | `plugin-sdk/memory-core-host-runtime-files` | 메모리 호스트 파일/런타임 헬퍼 |
    | `plugin-sdk/memory-lancedb` | 번들 memory-lancedb 헬퍼 표면 |
  </Accordion>

  <Accordion title="예약된 번들 헬퍼 하위 경로">
    | 계열 | 현재 하위 경로 | 의도된 용도 |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-config-support`, `plugin-sdk/browser-support` | 번들 browser 플러그인 지원 헬퍼 |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | 번들 Matrix 헬퍼/런타임 표면 |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | 번들 LINE 헬퍼/런타임 표면 |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | 번들 IRC 헬퍼 표면 |
    | 채널별 헬퍼 | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | 번들 채널 호환성/헬퍼 seam |
    | 인증/플러그인별 헬퍼 | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | 번들 기능/플러그인 헬퍼 seam; `plugin-sdk/github-copilot-token`은 현재 `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, `resolveCopilotApiToken`을 export합니다 |
  </Accordion>
</AccordionGroup>

## 등록 API

`register(api)` 콜백은 다음 메서드를 가진 `OpenClawPluginApi` 객체를
받습니다:

### 기능 등록

| 메서드                                           | 등록하는 항목                  |
| ------------------------------------------------ | ----------------------------- |
| `api.registerProvider(...)`                      | 텍스트 추론 (LLM)             |
| `api.registerCliBackend(...)`                    | 로컬 CLI 추론 백엔드          |
| `api.registerChannel(...)`                       | 메시징 채널                   |
| `api.registerSpeechProvider(...)`                | 텍스트 음성 변환 / STT 합성   |
| `api.registerRealtimeTranscriptionProvider(...)` | 스트리밍 실시간 전사          |
| `api.registerRealtimeVoiceProvider(...)`         | 양방향 실시간 음성 세션       |
| `api.registerMediaUnderstandingProvider(...)`    | 이미지/오디오/비디오 분석     |
| `api.registerImageGenerationProvider(...)`       | 이미지 생성                   |
| `api.registerVideoGenerationProvider(...)`       | 비디오 생성                   |
| `api.registerWebFetchProvider(...)`              | 웹 fetch / 스크래핑 프로바이더 |
| `api.registerWebSearchProvider(...)`             | 웹 검색                       |

### 도구 및 명령

| 메서드                          | 등록하는 항목                               |
| ------------------------------- | ------------------------------------------- |
| `api.registerTool(tool, opts?)` | 에이전트 도구 (필수 또는 `{ optional: true }`) |
| `api.registerCommand(def)`      | 사용자 지정 명령 (LLM 우회)                 |

### 인프라

| 메서드                                         | 등록하는 항목         |
| ---------------------------------------------- | -------------------- |
| `api.registerHook(events, handler, opts?)`     | 이벤트 hook          |
| `api.registerHttpRoute(params)`                | 게이트웨이 HTTP 엔드포인트 |
| `api.registerGatewayMethod(name, handler)`     | 게이트웨이 RPC 메서드 |
| `api.registerCli(registrar, opts?)`            | CLI 하위 명령        |
| `api.registerService(service)`                 | 백그라운드 서비스     |
| `api.registerInteractiveHandler(registration)` | 대화형 핸들러         |

예약된 코어 관리자 네임스페이스(`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`)는 플러그인이 더 좁은 게이트웨이 메서드 범위를 지정하려고 해도
항상 `operator.admin`으로 유지됩니다. 플러그인 소유 메서드에는
플러그인별 접두사를 사용하는 것이 좋습니다.

### CLI 등록 메타데이터

`api.registerCli(registrar, opts?)`는 두 종류의 최상위 메타데이터를 받습니다:

- `commands`: registrar가 소유한 명시적 명령 루트
- `descriptors`: 루트 CLI 도움말, 라우팅 및 지연 플러그인 CLI 등록에
  사용되는 파싱 시점 명령 디스크립터

플러그인 명령을 일반 루트 CLI 경로에서 지연 로드 상태로 유지하려면,
해당 registrar가 노출하는 모든 최상위 명령 루트를 포괄하는 `descriptors`를
제공하세요.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Matrix 계정, 검증, 디바이스 및 프로필 상태 관리",
        hasSubcommands: true,
      },
    ],
  },
);
```

일반 루트 CLI 등록에 지연 로딩이 필요하지 않은 경우에만 `commands`를
단독으로 사용하세요. 이 eager 호환성 경로는 계속 지원되지만, 파싱 시점
지연 로딩을 위한 descriptor 기반 플레이스홀더는 설치하지 않습니다.

### CLI 백엔드 등록

`api.registerCliBackend(...)`는 플러그인이 `claude-cli` 또는 `codex-cli`
같은 로컬 AI CLI 백엔드의 기본 config를 소유하도록 합니다.

- 백엔드 `id`는 `claude-cli/opus` 같은 model ref에서 프로바이더 접두사가 됩니다.
- 백엔드 `config`는 `agents.defaults.cliBackends.<id>`와 같은 형태를 사용합니다.
- 사용자 config가 여전히 우선합니다. OpenClaw는 CLI를 실행하기 전에
  `agents.defaults.cliBackends.<id>`를 플러그인 기본값 위에 병합합니다.
- 병합 후 백엔드에 호환성 재작성(예: 이전 플래그 형식 정규화)이 필요한 경우
  `normalizeConfig`를 사용하세요.

### 배타적 슬롯

| 메서드                                     | 등록하는 항목                       |
| ------------------------------------------ | ---------------------------------- |
| `api.registerContextEngine(id, factory)`   | 컨텍스트 엔진 (한 번에 하나만 활성) |
| `api.registerMemoryPromptSection(builder)` | 메모리 프롬프트 섹션 빌더          |
| `api.registerMemoryFlushPlan(resolver)`    | 메모리 flush 계획 해결기           |
| `api.registerMemoryRuntime(runtime)`       | 메모리 런타임 어댑터               |

### 메모리 임베딩 어댑터

| 메서드                                         | 등록하는 항목                                  |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | 활성 플러그인을 위한 메모리 임베딩 어댑터      |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan`, 그리고
  `registerMemoryRuntime`은 메모리 플러그인 전용입니다.
- `registerMemoryEmbeddingProvider`를 사용하면 활성 메모리 플러그인이
  하나 이상의 임베딩 어댑터 ID(예: `openai`, `gemini`, 또는 사용자 정의
  플러그인 ID)를 등록할 수 있습니다.
- `agents.defaults.memorySearch.provider` 및
  `agents.defaults.memorySearch.fallback` 같은 사용자 config는 등록된
  해당 어댑터 ID에 대해 해결됩니다.

### 이벤트 및 수명 주기

| 메서드                                       | 수행하는 작업              |
| -------------------------------------------- | ------------------------- |
| `api.on(hookName, handler, opts?)`           | 타입 지정된 수명 주기 hook |
| `api.onConversationBindingResolved(handler)` | 대화 바인딩 콜백          |

### Hook 결정 의미론

- `before_tool_call`: `{ block: true }`를 반환하면 최종 결정입니다. 어떤 핸들러든 이를 설정하면 더 낮은 우선순위의 핸들러는 건너뜁니다.
- `before_tool_call`: `{ block: false }`를 반환하면 결정 없음으로 처리됩니다(`block`을 생략한 것과 동일하며), override가 아닙니다.
- `before_install`: `{ block: true }`를 반환하면 최종 결정입니다. 어떤 핸들러든 이를 설정하면 더 낮은 우선순위의 핸들러는 건너뜁니다.
- `before_install`: `{ block: false }`를 반환하면 결정 없음으로 처리됩니다(`block`을 생략한 것과 동일하며), override가 아닙니다.
- `message_sending`: `{ cancel: true }`를 반환하면 최종 결정입니다. 어떤 핸들러든 이를 설정하면 더 낮은 우선순위의 핸들러는 건너뜁니다.
- `message_sending`: `{ cancel: false }`를 반환하면 결정 없음으로 처리됩니다(`cancel`을 생략한 것과 동일하며), override가 아닙니다.

### API 객체 필드

| 필드                     | 타입                      | 설명                                                                                         |
| ------------------------ | ------------------------- | -------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | 플러그인 ID                                                                                  |
| `api.name`               | `string`                  | 표시 이름                                                                                     |
| `api.version`            | `string?`                 | 플러그인 버전 (선택 사항)                                                                     |
| `api.description`        | `string?`                 | 플러그인 설명 (선택 사항)                                                                     |
| `api.source`             | `string`                  | 플러그인 소스 경로                                                                            |
| `api.rootDir`            | `string?`                 | 플러그인 루트 디렉터리 (선택 사항)                                                            |
| `api.config`             | `OpenClawConfig`          | 현재 config 스냅샷 (사용 가능한 경우 활성 인메모리 런타임 스냅샷)                            |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config`의 플러그인별 config                                            |
| `api.runtime`            | `PluginRuntime`           | [런타임 헬퍼](/ko/plugins/sdk-runtime)                                                           |
| `api.logger`             | `PluginLogger`            | 범위 지정 로거 (`debug`, `info`, `warn`, `error`)                                            |
| `api.registrationMode`   | `PluginRegistrationMode`  | 현재 로드 모드; `"setup-runtime"`은 가벼운 전체 엔트리 전 시작/설정 창입니다                  |
| `api.resolvePath(input)` | `(string) => string`      | 플러그인 루트를 기준으로 경로 해결                                                            |

## 내부 모듈 규칙

플러그인 내부에서는 내부 임포트를 위해 로컬 barrel 파일을 사용하세요:

```
my-plugin/
  api.ts            # 외부 소비자를 위한 공개 export
  runtime-api.ts    # 내부 전용 런타임 export
  index.ts          # 플러그인 엔트리 포인트
  setup-entry.ts    # 가벼운 설정 전용 엔트리 (선택 사항)
```

<Warning>
  프로덕션 코드에서 `openclaw/plugin-sdk/<your-plugin>`을 통해 자신의
  플러그인을 임포트하지 마세요. 내부 임포트는 `./api.ts` 또는
  `./runtime-api.ts`를 통해 처리하세요. SDK 경로는 외부 계약 전용입니다.
</Warning>

파사드로 로드되는 번들 플러그인 공개 표면(`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` 및 유사한 공개 엔트리 파일)은 이제 OpenClaw가
이미 실행 중인 경우 활성 런타임 config 스냅샷을 우선 사용합니다. 아직
런타임 스냅샷이 없으면 디스크에서 해결된 config 파일로 폴백합니다.

프로바이더 플러그인은 헬퍼가 의도적으로 프로바이더별이며 아직 일반적인 SDK
하위 경로에 속하지 않는 경우, 좁은 범위의 플러그인 로컬 계약 barrel을
노출할 수도 있습니다. 현재 번들 예시: Anthropic 프로바이더는 Anthropic
beta-header 및 `service_tier` 로직을 일반적인 `plugin-sdk/*` 계약으로
승격하는 대신, Claude 스트림 헬퍼를 자체 공개 `api.ts` /
`contract-api.ts` seam에 유지합니다.

다른 현재 번들 예시는 다음과 같습니다:

- `@openclaw/openai-provider`: `api.ts`는 프로바이더 빌더,
  기본 모델 헬퍼 및 실시간 프로바이더 빌더를 export합니다
- `@openclaw/openrouter-provider`: `api.ts`는 프로바이더 빌더와
  온보딩/config 헬퍼를 export합니다

<Warning>
  확장 프로덕션 코드도 `openclaw/plugin-sdk/<other-plugin>` 임포트를
  피해야 합니다. 헬퍼가 정말 공유되어야 한다면, 두 플러그인을 결합하는 대신
  `openclaw/plugin-sdk/speech`, `.../provider-model-shared` 또는 다른
  기능 지향 표면 같은 중립적인 SDK 하위 경로로 승격하세요.
</Warning>

## 관련 내용

- [엔트리 포인트](/ko/plugins/sdk-entrypoints) — `definePluginEntry` 및 `defineChannelPluginEntry` 옵션
- [런타임 헬퍼](/ko/plugins/sdk-runtime) — 전체 `api.runtime` 네임스페이스 참조
- [설정 및 config](/ko/plugins/sdk-setup) — 패키징, 매니페스트, config 스키마
- [테스트](/ko/plugins/sdk-testing) — 테스트 유틸리티 및 lint 규칙
- [SDK 마이그레이션](/ko/plugins/sdk-migration) — 사용 중단된 표면에서 마이그레이션
- [플러그인 내부 구조](/plugins/architecture) — 심층 아키텍처 및 기능 모델
