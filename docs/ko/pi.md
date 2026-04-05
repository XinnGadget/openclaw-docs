---
read_when:
    - OpenClaw의 Pi SDK 통합 설계를 이해하는 경우
    - Pi용 에이전트 세션 수명 주기, 도구 또는 provider 연결을 수정하는 경우
summary: OpenClaw의 임베디드 Pi 에이전트 통합 및 세션 수명 주기 아키텍처
title: Pi 통합 아키텍처
x-i18n:
    generated_at: "2026-04-05T12:48:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 596de5fbb1430008698079f211db200e02ca8485547550fd81571a459c4c83c7
    source_path: pi.md
    workflow: 15
---

# Pi 통합 아키텍처

이 문서는 OpenClaw가 AI 에이전트 기능을 구동하기 위해 [pi-coding-agent](https://github.com/badlogic/pi-mono/tree/main/packages/coding-agent) 및 그 형제 패키지(`pi-ai`, `pi-agent-core`, `pi-tui`)와 어떻게 통합되는지 설명합니다.

## 개요

OpenClaw는 Pi SDK를 사용해 메시징 gateway 아키텍처 안에 AI 코딩 에이전트를 임베드합니다. Pi를 하위 프로세스로 생성하거나 RPC 모드를 사용하는 대신, OpenClaw는 `createAgentSession()`을 통해 Pi의 `AgentSession`을 직접 import하고 인스턴스화합니다. 이 임베디드 접근 방식은 다음을 제공합니다.

- 세션 수명 주기 및 이벤트 처리에 대한 완전한 제어
- 사용자 지정 도구 주입(메시징, 샌드박스, 채널별 작업)
- 채널/컨텍스트별 시스템 프롬프트 사용자 지정
- 브랜칭/compaction 지원이 포함된 세션 영속성
- failover를 포함한 다중 계정 auth profile 순환
- provider에 독립적인 모델 전환

## 패키지 종속성

```json
{
  "@mariozechner/pi-agent-core": "0.64.0",
  "@mariozechner/pi-ai": "0.64.0",
  "@mariozechner/pi-coding-agent": "0.64.0",
  "@mariozechner/pi-tui": "0.64.0"
}
```

| Package           | 용도                                                                                                |
| ----------------- | ------------------------------------------------------------------------------------------------------ |
| `pi-ai`           | 핵심 LLM 추상화: `Model`, `streamSimple`, 메시지 타입, provider API                           |
| `pi-agent-core`   | 에이전트 루프, 도구 실행, `AgentMessage` 타입                                                       |
| `pi-coding-agent` | 고수준 SDK: `createAgentSession`, `SessionManager`, `AuthStorage`, `ModelRegistry`, 내장 도구 |
| `pi-tui`          | 터미널 UI 컴포넌트(OpenClaw의 로컬 TUI 모드에서 사용)                                             |

## 파일 구조

```
src/agents/
├── pi-embedded-runner.ts          # pi-embedded-runner/에서 다시 내보내기
├── pi-embedded-runner/
│   ├── run.ts                     # 메인 진입점: runEmbeddedPiAgent()
│   ├── run/
│   │   ├── attempt.ts             # 세션 설정을 포함한 단일 시도 로직
│   │   ├── params.ts              # RunEmbeddedPiAgentParams 타입
│   │   ├── payloads.ts            # 실행 결과에서 응답 payload 생성
│   │   ├── images.ts              # 비전 모델 이미지 주입
│   │   └── types.ts               # EmbeddedRunAttemptResult
│   ├── abort.ts                   # 중단 오류 감지
│   ├── cache-ttl.ts               # 컨텍스트 정리를 위한 캐시 TTL 추적
│   ├── compact.ts                 # 수동/자동 compaction 로직
│   ├── extensions.ts              # 임베디드 실행용 Pi 확장 로드
│   ├── extra-params.ts            # provider별 스트림 파라미터
│   ├── google.ts                  # Google/Gemini 턴 순서 수정
│   ├── history.ts                 # 기록 제한(DM vs 그룹)
│   ├── lanes.ts                   # 세션/전역 명령 레인
│   ├── logger.ts                  # 서브시스템 로거
│   ├── model.ts                   # ModelRegistry를 통한 모델 해석
│   ├── runs.ts                    # 활성 실행 추적, 중단, 큐
│   ├── sandbox-info.ts            # 시스템 프롬프트용 샌드박스 정보
│   ├── session-manager-cache.ts   # SessionManager 인스턴스 캐싱
│   ├── session-manager-init.ts    # 세션 파일 초기화
│   ├── system-prompt.ts           # 시스템 프롬프트 빌더
│   ├── tool-split.ts              # 도구를 builtIn vs custom으로 분리
│   ├── types.ts                   # EmbeddedPiAgentMeta, EmbeddedPiRunResult
│   └── utils.ts                   # ThinkLevel 매핑, 오류 설명
├── pi-embedded-subscribe.ts       # 세션 이벤트 구독/디스패치
├── pi-embedded-subscribe.types.ts # SubscribeEmbeddedPiSessionParams
├── pi-embedded-subscribe.handlers.ts # 이벤트 핸들러 팩토리
├── pi-embedded-subscribe.handlers.lifecycle.ts
├── pi-embedded-subscribe.handlers.types.ts
├── pi-embedded-block-chunker.ts   # 스트리밍 블록 응답 청킹
├── pi-embedded-messaging.ts       # 메시징 도구 sent 추적
├── pi-embedded-helpers.ts         # 오류 분류, 턴 검증
├── pi-embedded-helpers/           # 도우미 모듈
├── pi-embedded-utils.ts           # 서식 유틸리티
├── pi-tools.ts                    # createOpenClawCodingTools()
├── pi-tools.abort.ts              # 도구용 AbortSignal 래핑
├── pi-tools.policy.ts             # 도구 허용 목록/거부 목록 정책
├── pi-tools.read.ts               # Read 도구 사용자 지정
├── pi-tools.schema.ts             # 도구 스키마 정규화
├── pi-tools.types.ts              # AnyAgentTool 타입 별칭
├── pi-tool-definition-adapter.ts  # AgentTool -> ToolDefinition 어댑터
├── pi-settings.ts                 # 설정 재정의
├── pi-hooks/                      # 사용자 지정 Pi hook
│   ├── compaction-safeguard.ts    # Safeguard 확장
│   ├── compaction-safeguard-runtime.ts
│   ├── context-pruning.ts         # 캐시 TTL 기반 컨텍스트 정리 확장
│   └── context-pruning/
├── model-auth.ts                  # Auth profile 해석
├── auth-profiles.ts               # Profile 저장소, cooldown, failover
├── model-selection.ts             # 기본 모델 해석
├── models-config.ts               # models.json 생성
├── model-catalog.ts               # 모델 카탈로그 캐시
├── context-window-guard.ts        # 컨텍스트 창 검증
├── failover-error.ts              # FailoverError 클래스
├── defaults.ts                    # DEFAULT_PROVIDER, DEFAULT_MODEL
├── system-prompt.ts               # buildAgentSystemPrompt()
├── system-prompt-params.ts        # 시스템 프롬프트 파라미터 해석
├── system-prompt-report.ts        # 디버그 보고서 생성
├── tool-summaries.ts              # 도구 설명 요약
├── tool-policy.ts                 # 도구 정책 해석
├── transcript-policy.ts           # transcript 검증 정책
├── skills.ts                      # Skill 스냅샷/프롬프트 빌드
├── skills/                        # Skill 서브시스템
├── sandbox.ts                     # 샌드박스 컨텍스트 해석
├── sandbox/                       # 샌드박스 서브시스템
├── channel-tools.ts               # 채널별 도구 주입
├── openclaw-tools.ts              # OpenClaw 전용 도구
├── bash-tools.ts                  # exec/process 도구
├── apply-patch.ts                 # apply_patch 도구(OpenAI)
├── tools/                         # 개별 도구 구현
│   ├── browser-tool.ts
│   ├── canvas-tool.ts
│   ├── cron-tool.ts
│   ├── gateway-tool.ts
│   ├── image-tool.ts
│   ├── message-tool.ts
│   ├── nodes-tool.ts
│   ├── session*.ts
│   ├── web-*.ts
│   └── ...
└── ...
```

채널별 메시지 작업 런타임은 이제 `src/agents/tools` 아래가 아니라 plugin 소유 확장
디렉터리에 위치합니다. 예를 들면 다음과 같습니다.

- Discord plugin 작업 런타임 파일
- Slack plugin 작업 런타임 파일
- Telegram plugin 작업 런타임 파일
- WhatsApp plugin 작업 런타임 파일

## 핵심 통합 흐름

### 1. 임베디드 에이전트 실행

메인 진입점은 `pi-embedded-runner/run.ts`의 `runEmbeddedPiAgent()`입니다.

```typescript
import { runEmbeddedPiAgent } from "./agents/pi-embedded-runner.js";

const result = await runEmbeddedPiAgent({
  sessionId: "user-123",
  sessionKey: "main:whatsapp:+1234567890",
  sessionFile: "/path/to/session.jsonl",
  workspaceDir: "/path/to/workspace",
  config: openclawConfig,
  prompt: "Hello, how are you?",
  provider: "anthropic",
  model: "claude-sonnet-4-6",
  timeoutMs: 120_000,
  runId: "run-abc",
  onBlockReply: async (payload) => {
    await sendToChannel(payload.text, payload.mediaUrls);
  },
});
```

### 2. 세션 생성

`runEmbeddedPiAgent()`가 호출하는 `runEmbeddedAttempt()` 내부에서 Pi SDK가 사용됩니다.

```typescript
import {
  createAgentSession,
  DefaultResourceLoader,
  SessionManager,
  SettingsManager,
} from "@mariozechner/pi-coding-agent";

const resourceLoader = new DefaultResourceLoader({
  cwd: resolvedWorkspace,
  agentDir,
  settingsManager,
  additionalExtensionPaths,
});
await resourceLoader.reload();

const { session } = await createAgentSession({
  cwd: resolvedWorkspace,
  agentDir,
  authStorage: params.authStorage,
  modelRegistry: params.modelRegistry,
  model: params.model,
  thinkingLevel: mapThinkingLevel(params.thinkLevel),
  tools: builtInTools,
  customTools: allCustomTools,
  sessionManager,
  settingsManager,
  resourceLoader,
});

applySystemPromptOverrideToSession(session, systemPromptOverride);
```

### 3. 이벤트 구독

`subscribeEmbeddedPiSession()`은 Pi의 `AgentSession` 이벤트를 구독합니다.

```typescript
const subscription = subscribeEmbeddedPiSession({
  session: activeSession,
  runId: params.runId,
  verboseLevel: params.verboseLevel,
  reasoningMode: params.reasoningLevel,
  toolResultFormat: params.toolResultFormat,
  onToolResult: params.onToolResult,
  onReasoningStream: params.onReasoningStream,
  onBlockReply: params.onBlockReply,
  onPartialReply: params.onPartialReply,
  onAgentEvent: params.onAgentEvent,
});
```

처리되는 이벤트는 다음과 같습니다.

- `message_start` / `message_end` / `message_update` (스트리밍 텍스트/thinking)
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`
- `turn_start` / `turn_end`
- `agent_start` / `agent_end`
- `auto_compaction_start` / `auto_compaction_end`

### 4. 프롬프팅

설정 후 세션에 프롬프트가 전달됩니다.

```typescript
await session.prompt(effectivePrompt, { images: imageResult.images });
```

SDK가 전체 에이전트 루프를 처리합니다: LLM 전송, 도구 호출 실행, 응답 스트리밍.

이미지 주입은 프롬프트 로컬입니다. OpenClaw는 현재 프롬프트에서 이미지 ref를 로드하고
해당 턴에만 `images`를 통해 전달합니다. 이전 기록 턴을 다시 스캔해
이미지 payload를 재주입하지는 않습니다.

## 도구 아키텍처

### 도구 파이프라인

1. **기본 도구**: Pi의 `codingTools` (`read`, `bash`, `edit`, `write`)
2. **사용자 지정 대체**: OpenClaw는 `bash`를 `exec`/`process`로 대체하고, 샌드박스용 `read`/`edit`/`write`를 사용자 지정함
3. **OpenClaw 도구**: 메시징, browser, canvas, sessions, cron, gateway 등
4. **채널 도구**: Discord/Telegram/Slack/WhatsApp 전용 작업 도구
5. **정책 필터링**: 도구가 profile, provider, agent, 그룹, 샌드박스 정책에 따라 필터링됨
6. **스키마 정규화**: Gemini/OpenAI 특이사항에 맞게 스키마 정리
7. **AbortSignal 래핑**: 도구가 abort signal을 준수하도록 래핑

### 도구 정의 어댑터

pi-agent-core의 `AgentTool`은 pi-coding-agent의 `ToolDefinition`과 `execute` 시그니처가 다릅니다. `pi-tool-definition-adapter.ts`의 어댑터가 이를 연결합니다.

```typescript
export function toToolDefinitions(tools: AnyAgentTool[]): ToolDefinition[] {
  return tools.map((tool) => ({
    name: tool.name,
    label: tool.label ?? name,
    description: tool.description ?? "",
    parameters: tool.parameters,
    execute: async (toolCallId, params, onUpdate, _ctx, signal) => {
      // pi-coding-agent 시그니처는 pi-agent-core와 다름
      return await tool.execute(toolCallId, params, signal, onUpdate);
    },
  }));
}
```

### 도구 분리 전략

`splitSdkTools()`는 모든 도구를 `customTools`로 전달합니다.

```typescript
export function splitSdkTools(options: { tools: AnyAgentTool[]; sandboxEnabled: boolean }) {
  return {
    builtInTools: [], // 비어 있음. 모든 것을 재정의함
    customTools: toToolDefinitions(options.tools),
  };
}
```

이렇게 하면 OpenClaw의 정책 필터링, 샌드박스 통합, 확장 도구 집합이 provider 전반에서 일관되게 유지됩니다.

## 시스템 프롬프트 구성

시스템 프롬프트는 `buildAgentSystemPrompt()` (`system-prompt.ts`)에서 빌드됩니다. Tooling, Tool Call Style, Safety guardrails, OpenClaw CLI 참조, Skills, Docs, Workspace, Sandbox, Messaging, Reply Tags, Voice, Silent Replies, Heartbeats, Runtime metadata, 그리고 활성화된 경우 Memory와 Reactions, 선택적 컨텍스트 파일 및 추가 시스템 프롬프트 내용을 포함하는 전체 프롬프트를 조립합니다. 하위 에이전트에 사용되는 최소 프롬프트 모드에서는 섹션이 잘립니다.

프롬프트는 세션 생성 후 `applySystemPromptOverrideToSession()`을 통해 적용됩니다.

```typescript
const systemPromptOverride = createSystemPromptOverride(appendPrompt);
applySystemPromptOverrideToSession(session, systemPromptOverride);
```

## 세션 관리

### 세션 파일

세션은 트리 구조(id/parentId 연결)를 가진 JSONL 파일입니다. Pi의 `SessionManager`가 영속성을 처리합니다.

```typescript
const sessionManager = SessionManager.open(params.sessionFile);
```

OpenClaw는 도구 결과 안전성을 위해 이를 `guardSessionManager()`로 감쌉니다.

### 세션 캐싱

`session-manager-cache.ts`는 반복적인 파일 파싱을 피하기 위해 SessionManager 인스턴스를 캐싱합니다.

```typescript
await prewarmSessionFile(params.sessionFile);
sessionManager = SessionManager.open(params.sessionFile);
trackSessionManagerAccess(params.sessionFile);
```

### 기록 제한

`limitHistoryTurns()`는 채널 유형(DM vs 그룹)에 따라 대화 기록을 잘라냅니다.

### Compaction

컨텍스트 오버플로 시 자동 compaction이 트리거됩니다. 일반적인 오버플로 시그니처는
`request_too_large`, `context length exceeded`, `input exceeds the
maximum number of tokens`, `input token count exceeds the maximum number of
input tokens`, `input is too long for the model`, `ollama error: context
length exceeded`입니다. `compactEmbeddedPiSessionDirect()`가 수동
compaction을 처리합니다.

```typescript
const compactResult = await compactEmbeddedPiSessionDirect({
  sessionId, sessionFile, provider, model, ...
});
```

## 인증 및 모델 해석

### Auth profile

OpenClaw는 provider별 여러 API key가 포함된 auth profile 저장소를 유지합니다.

```typescript
const authStore = ensureAuthProfileStore(agentDir, { allowKeychainPrompt: false });
const profileOrder = resolveAuthProfileOrder({ cfg, store: authStore, provider, preferredProfile });
```

실패 시 profile은 cooldown 추적과 함께 순환됩니다.

```typescript
await markAuthProfileFailure({ store, profileId, reason, cfg, agentDir });
const rotated = await advanceAuthProfile();
```

### 모델 해석

```typescript
import { resolveModel } from "./pi-embedded-runner/model.js";

const { model, error, authStorage, modelRegistry } = resolveModel(
  provider,
  modelId,
  agentDir,
  config,
);

// Pi의 ModelRegistry와 AuthStorage 사용
authStorage.setRuntimeApiKey(model.provider, apiKeyInfo.apiKey);
```

### Failover

구성되어 있을 때 `FailoverError`가 모델 fallback을 트리거합니다.

```typescript
if (fallbackConfigured && isFailoverErrorMessage(errorText)) {
  throw new FailoverError(errorText, {
    reason: promptFailoverReason ?? "unknown",
    provider,
    model: modelId,
    profileId,
    status: resolveFailoverStatus(promptFailoverReason),
  });
}
```

## Pi 확장

OpenClaw는 특수 동작을 위해 사용자 지정 Pi 확장을 로드합니다.

### Compaction Safeguard

`src/agents/pi-hooks/compaction-safeguard.ts`는 적응형 토큰 예산 책정과 도구 실패 및 파일 작업 요약을 포함한 compaction 가드레일을 추가합니다.

```typescript
if (resolveCompactionMode(params.cfg) === "safeguard") {
  setCompactionSafeguardRuntime(params.sessionManager, { maxHistoryShare });
  paths.push(resolvePiExtensionPath("compaction-safeguard"));
}
```

### 컨텍스트 정리

`src/agents/pi-hooks/context-pruning.ts`는 캐시 TTL 기반 컨텍스트 정리를 구현합니다.

```typescript
if (cfg?.agents?.defaults?.contextPruning?.mode === "cache-ttl") {
  setContextPruningRuntime(params.sessionManager, {
    settings,
    contextWindowTokens,
    isToolPrunable,
    lastCacheTouchAt,
  });
  paths.push(resolvePiExtensionPath("context-pruning"));
}
```

## 스트리밍 및 블록 응답

### 블록 청킹

`EmbeddedBlockChunker`는 스트리밍 텍스트를 개별 응답 블록으로 관리합니다.

```typescript
const blockChunker = blockChunking ? new EmbeddedBlockChunker(blockChunking) : null;
```

### Thinking/최종 태그 제거

스트리밍 출력은 `<think>`/`<thinking>` 블록을 제거하고 `<final>` 내용을 추출하도록 처리됩니다.

```typescript
const stripBlockTags = (text: string, state: { thinking: boolean; final: boolean }) => {
  // <think>...</think> 내용 제거
  // enforceFinalTag가 있으면 <final>...</final> 내용만 반환
};
```

### 응답 directive

`[[media:url]]`, `[[voice]]`, `[[reply:id]]` 같은 응답 directive가 파싱 및 추출됩니다.

```typescript
const { text: cleanedText, mediaUrls, audioAsVoice, replyToId } = consumeReplyDirectives(chunk);
```

## 오류 처리

### 오류 분류

`pi-embedded-helpers.ts`는 적절한 처리를 위해 오류를 분류합니다.

```typescript
isContextOverflowError(errorText)     // 컨텍스트가 너무 큼
isCompactionFailureError(errorText)   // Compaction 실패
isAuthAssistantError(lastAssistant)   // 인증 실패
isRateLimitAssistantError(...)        // rate limit 도달
isFailoverAssistantError(...)         // failover해야 함
classifyFailoverReason(errorText)     // "auth" | "rate_limit" | "quota" | "timeout" | ...
```

### Thinking 수준 fallback

thinking 수준이 지원되지 않으면 fallback이 적용됩니다.

```typescript
const fallbackThinking = pickFallbackThinkingLevel({
  message: errorText,
  attempted: attemptedThinking,
});
if (fallbackThinking) {
  thinkLevel = fallbackThinking;
  continue;
}
```

## 샌드박스 통합

샌드박스 모드가 활성화되면 도구와 경로가 제한됩니다.

```typescript
const sandbox = await resolveSandboxContext({
  config: params.config,
  sessionKey: sandboxSessionKey,
  workspaceDir: resolvedWorkspace,
});

if (sandboxRoot) {
  // 샌드박스 read/edit/write 도구 사용
  // Exec는 컨테이너 안에서 실행
  // Browser는 bridge URL 사용
}
```

## Provider별 처리

### Anthropic

- 거부 마법 문자열 제거
- 연속 역할에 대한 턴 검증
- Claude Code 파라미터 호환성

### Google/Gemini

- plugin 소유 도구 스키마 정리

### OpenAI

- Codex 모델용 `apply_patch` 도구
- thinking 수준 강등 처리

## TUI 통합

OpenClaw는 Pi-tui 컴포넌트를 직접 사용하는 로컬 TUI 모드도 제공합니다.

```typescript
// src/tui/tui.ts
import { ... } from "@mariozechner/pi-tui";
```

이는 Pi의 네이티브 모드와 유사한 대화형 터미널 경험을 제공합니다.

## Pi CLI와의 주요 차이점

| 측면          | Pi CLI                  | OpenClaw Embedded                                                                              |
| --------------- | ----------------------- | ---------------------------------------------------------------------------------------------- |
| 호출 방식      | `pi` 명령 / RPC      | `createAgentSession()`를 통한 SDK                                                                 |
| 도구           | 기본 코딩 도구    | 사용자 지정 OpenClaw 도구 모음                                                                     |
| 시스템 프롬프트   | `AGENTS.md` + 프롬프트     | 채널/컨텍스트별 동적 프롬프트                                                                    |
| 세션 저장소 | `~/.pi/agent/sessions/` | `~/.openclaw/agents/<agentId>/sessions/` (또는 `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`) |
| 인증            | 단일 자격 증명       | 순환을 포함한 다중 profile                                                                    |
| 확장      | 디스크에서 로드        | 프로그래밍 방식 + 디스크 경로                                                                      |
| 이벤트 처리  | TUI 렌더링           | 콜백 기반 (`onBlockReply` 등)                                                            |

## 향후 고려 사항

잠재적 재작업이 가능한 영역:

1. **도구 시그니처 정렬**: 현재는 pi-agent-core와 pi-coding-agent 시그니처 사이를 어댑트하고 있음
2. **Session manager 래핑**: `guardSessionManager`는 안전성을 더하지만 복잡성도 증가시킴
3. **확장 로딩**: Pi의 `ResourceLoader`를 더 직접적으로 사용할 수 있음
4. **스트리밍 핸들러 복잡성**: `subscribeEmbeddedPiSession`가 많이 커졌음
5. **Provider 특이사항**: Pi가 잠재적으로 처리할 수 있을 정도로 많은 provider별 코드 경로가 존재함

## 테스트

Pi 통합 커버리지는 다음 테스트 모음에 걸쳐 있습니다.

- `src/agents/pi-*.test.ts`
- `src/agents/pi-auth-json.test.ts`
- `src/agents/pi-embedded-*.test.ts`
- `src/agents/pi-embedded-helpers*.test.ts`
- `src/agents/pi-embedded-runner*.test.ts`
- `src/agents/pi-embedded-runner/**/*.test.ts`
- `src/agents/pi-embedded-subscribe*.test.ts`
- `src/agents/pi-tools*.test.ts`
- `src/agents/pi-tool-definition-adapter*.test.ts`
- `src/agents/pi-settings.test.ts`
- `src/agents/pi-hooks/**/*.test.ts`

실시간/옵트인:

- `src/agents/pi-embedded-runner-extraparams.live.test.ts` (`OPENCLAW_LIVE_TEST=1`로 활성화)

현재 실행 명령은 [Pi Development Workflow](/pi-dev)를 참조하세요.
