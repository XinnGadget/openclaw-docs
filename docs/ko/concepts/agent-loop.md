---
read_when:
    - 에이전트 루프 또는 수명 주기 이벤트에 대한 정확한 단계별 설명이 필요함
summary: 에이전트 루프 수명 주기, 스트림 및 wait 의미론
title: Agent Loop
x-i18n:
    generated_at: "2026-04-05T12:39:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8e562e63c494881e9c345efcb93c5f972d69aaec61445afc3d4ad026b2d26883
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Agent Loop (OpenClaw)

에이전트 루프는 에이전트의 전체 “실제” 실행입니다: 입력 수집 → 컨텍스트 조립 → 모델 추론 →
도구 실행 → 응답 스트리밍 → 영속화. 이는 메시지를 동작과 최종 응답으로
변환하면서 세션 상태의 일관성을 유지하는 권위 있는 경로입니다.

OpenClaw에서 루프는 세션당 하나의 직렬화된 실행이며, 모델이 생각하고, 도구를 호출하고, 출력을 스트리밍할 때
수명 주기 및 스트림 이벤트를 발생시킵니다. 이 문서는 그 실제 루프가
엔드 투 엔드로 어떻게 연결되어 있는지 설명합니다.

## 진입점

- Gateway RPC: `agent` 및 `agent.wait`.
- CLI: `agent` 명령.

## 작동 방식(상위 수준)

1. `agent` RPC가 매개변수를 검증하고, 세션(sessionKey/sessionId)을 확인하고, 세션 메타데이터를 저장한 다음, 즉시 `{ runId, acceptedAt }`를 반환합니다.
2. `agentCommand`가 에이전트를 실행합니다:
   - 모델 + thinking/verbose 기본값 확인
   - Skills 스냅샷 로드
   - `runEmbeddedPiAgent` 호출(pi-agent-core 런타임)
   - 임베디드 루프가 수명 주기 종료/오류를 발생시키지 않으면 **lifecycle end/error** 발생
3. `runEmbeddedPiAgent`:
   - 세션별 + 전역 큐를 통해 실행을 직렬화
   - 모델 + 인증 프로필을 확인하고 pi 세션 빌드
   - pi 이벤트를 구독하고 assistant/tool 델타 스트리밍
   - 타임아웃 강제 적용 -> 초과 시 실행 중단
   - 페이로드 + 사용량 메타데이터 반환
4. `subscribeEmbeddedPiSession`이 pi-agent-core 이벤트를 OpenClaw `agent` 스트림으로 브리지합니다:
   - 도구 이벤트 => `stream: "tool"`
   - assistant 델타 => `stream: "assistant"`
   - 수명 주기 이벤트 => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait`는 `waitForAgentRun`을 사용합니다:
   - `runId`에 대한 **lifecycle end/error** 대기
   - `{ status: ok|error|timeout, startedAt, endedAt, error? }` 반환

## 큐잉 + 동시성

- 실행은 세션 키(세션 레인)별로 직렬화되며 선택적으로 전역 레인을 통과합니다.
- 이를 통해 도구/세션 경쟁 상태를 방지하고 세션 기록의 일관성을 유지합니다.
- 메시징 채널은 이 레인 시스템에 연결되는 큐 모드(collect/steer/followup)를 선택할 수 있습니다.
  자세한 내용은 [Command Queue](/concepts/queue)를 참조하세요.

## 세션 + workspace 준비

- workspace가 확인 및 생성되며, 샌드박스 실행은 샌드박스 workspace 루트로 리디렉션될 수 있습니다.
- Skills가 로드되거나(또는 스냅샷에서 재사용되며) env와 프롬프트에 주입됩니다.
- bootstrap/context 파일이 확인되어 시스템 프롬프트 보고서에 주입됩니다.
- 세션 쓰기 잠금이 획득되며, 스트리밍 전에 `SessionManager`가 열리고 준비됩니다.

## 프롬프트 조립 + 시스템 프롬프트

- 시스템 프롬프트는 OpenClaw의 기본 프롬프트, skills 프롬프트, bootstrap 컨텍스트, 실행별 재정의로 구성됩니다.
- 모델별 제한과 compaction reserve 토큰이 강제 적용됩니다.
- 모델이 실제로 보는 내용은 [System prompt](/concepts/system-prompt)를 참조하세요.

## Hook 지점(가로챌 수 있는 위치)

OpenClaw에는 두 가지 hook 시스템이 있습니다.

- **내부 hooks**(Gateway hooks): 명령 및 수명 주기 이벤트를 위한 이벤트 기반 스크립트.
- **Plugin hooks**: 에이전트/도구 수명 주기와 gateway 파이프라인 내부의 확장 지점.

### 내부 hooks (Gateway hooks)

- **`agent:bootstrap`**: 시스템 프롬프트가 최종 확정되기 전에 bootstrap 파일을 빌드하는 동안 실행됩니다.
  bootstrap 컨텍스트 파일을 추가/제거할 때 사용합니다.
- **명령 hooks**: `/new`, `/reset`, `/stop` 및 기타 명령 이벤트(Hooks 문서 참조).

설정 및 예시는 [Hooks](/automation/hooks)를 참조하세요.

### Plugin hooks (에이전트 + gateway 수명 주기)

이들은 에이전트 루프 또는 gateway 파이프라인 내부에서 실행됩니다.

- **`before_model_resolve`**: 모델 확인 전에 세션 사전 단계(`messages` 없음)에서 실행되어 provider/model을 결정적으로 재정의합니다.
- **`before_prompt_build`**: 세션 로드 후(`messages` 포함) 실행되어 프롬프트 제출 전에 `prependContext`, `systemPrompt`, `prependSystemContext`, 또는 `appendSystemContext`를 주입합니다. 턴별 동적 텍스트에는 `prependContext`를 사용하고, 시스템 프롬프트 공간에 들어가야 하는 안정적인 안내에는 system-context 필드를 사용하세요.
- **`before_agent_start`**: 레거시 호환성 hook으로 어느 단계에서든 실행될 수 있습니다. 위의 명시적 hooks를 우선 사용하세요.
- **`before_agent_reply`**: 인라인 동작 후 및 LLM 호출 전에 실행되며, plugin이 해당 턴을 점유하고 합성 응답을 반환하거나 턴 전체를 완전히 무음 처리할 수 있게 합니다.
- **`agent_end`**: 완료 후 최종 메시지 목록과 실행 메타데이터를 검사합니다.
- **`before_compaction` / `after_compaction`**: compaction 주기를 관찰하거나 주석을 추가합니다.
- **`before_tool_call` / `after_tool_call`**: 도구 매개변수/결과를 가로챕니다.
- **`before_install`**: 내장 스캔 결과를 검사하고 skill 또는 plugin 설치를 선택적으로 차단합니다.
- **`tool_result_persist`**: 도구 결과가 세션 기록에 기록되기 전에 동기적으로 변환합니다.
- **`message_received` / `message_sending` / `message_sent`**: 수신 + 발신 메시지 hooks.
- **`session_start` / `session_end`**: 세션 수명 주기 경계.
- **`gateway_start` / `gateway_stop`**: gateway 수명 주기 이벤트.

발신/도구 가드에 대한 hook 결정 규칙:

- `before_tool_call`: `{ block: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단합니다.
- `before_tool_call`: `{ block: false }`는 no-op이며 이전 block을 해제하지 않습니다.
- `before_install`: `{ block: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단합니다.
- `before_install`: `{ block: false }`는 no-op이며 이전 block을 해제하지 않습니다.
- `message_sending`: `{ cancel: true }`는 최종 결정이며 더 낮은 우선순위 핸들러를 중단합니다.
- `message_sending`: `{ cancel: false }`는 no-op이며 이전 cancel을 해제하지 않습니다.

hook API 및 등록 세부 사항은 [Plugin hooks](/plugins/architecture#provider-runtime-hooks)를 참조하세요.

## 스트리밍 + 부분 응답

- Assistant 델타는 pi-agent-core에서 스트리밍되며 `assistant` 이벤트로 발생합니다.
- Block streaming은 `text_end` 또는 `message_end`에서 부분 응답을 발생시킬 수 있습니다.
- Reasoning streaming은 별도 스트림 또는 block reply로 발생할 수 있습니다.
- 청크 분할 및 block reply 동작은 [Streaming](/concepts/streaming)을 참조하세요.

## 도구 실행 + 메시징 도구

- 도구 시작/업데이트/종료 이벤트는 `tool` 스트림에서 발생합니다.
- 도구 결과는 기록/발생 전에 크기와 이미지 페이로드 기준으로 정리됩니다.
- 메시징 도구 전송은 중복 assistant 확인 메시지를 억제하기 위해 추적됩니다.

## 응답 형태 조정 + 억제

- 최종 페이로드는 다음으로 조립됩니다:
  - assistant 텍스트(및 선택적 reasoning)
  - 인라인 도구 요약(verbose + 허용 시)
  - 모델 오류 시 assistant 오류 텍스트
- 정확히 `NO_REPLY` / `no_reply`인 무응답 토큰은 발신
  페이로드에서 필터링됩니다.
- 메시징 도구 중복은 최종 페이로드 목록에서 제거됩니다.
- 렌더링 가능한 페이로드가 남지 않았고 도구 오류가 발생한 경우,
  폴백 도구 오류 응답이 발생합니다
  (단, 메시징 도구가 이미 사용자에게 보이는 응답을 보낸 경우는 제외).

## Compaction + 재시도

- 자동 compaction은 `compaction` 스트림 이벤트를 발생시키고 재시도를 트리거할 수 있습니다.
- 재시도 시 중복 출력을 피하기 위해 메모리 내 버퍼와 도구 요약이 재설정됩니다.
- compaction 파이프라인은 [Compaction](/concepts/compaction)을 참조하세요.

## 이벤트 스트림(현재)

- `lifecycle`: `subscribeEmbeddedPiSession`에서 발생(그리고 폴백으로 `agentCommand`에서도 발생)
- `assistant`: pi-agent-core의 스트리밍 델타
- `tool`: pi-agent-core의 스트리밍 도구 이벤트

## 채팅 채널 처리

- Assistant 델타는 채팅 `delta` 메시지로 버퍼링됩니다.
- 채팅 `final`은 **lifecycle end/error**에서 발생합니다.

## 타임아웃

- `agent.wait` 기본값: 30초(wait만 해당). `timeoutMs` 매개변수로 재정의 가능.
- 에이전트 런타임: `agents.defaults.timeoutSeconds` 기본값 172800초(48시간); `runEmbeddedPiAgent`의 중단 타이머에서 강제 적용.

## 조기 종료될 수 있는 위치

- 에이전트 타임아웃(중단)
- AbortSignal(취소)
- Gateway 연결 해제 또는 RPC 타임아웃
- `agent.wait` 타임아웃(wait만 해당, 에이전트를 중지하지는 않음)

## 관련 문서

- [Tools](/tools) — 사용 가능한 에이전트 도구
- [Hooks](/automation/hooks) — 에이전트 수명 주기 이벤트에 의해 트리거되는 이벤트 기반 스크립트
- [Compaction](/concepts/compaction) — 긴 대화가 요약되는 방식
- [Exec Approvals](/tools/exec-approvals) — 셸 명령에 대한 승인 게이트
- [Thinking](/tools/thinking) — thinking/reasoning 수준 구성
