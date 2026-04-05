---
read_when:
    - transcript 형태와 관련된 provider 요청 거부를 디버깅하는 경우
    - transcript 정리 또는 tool-call 복구 로직을 변경하는 경우
    - provider 간 tool-call id 불일치를 조사하는 경우
summary: '참조: provider별 transcript 정리 및 복구 규칙'
title: Transcript Hygiene
x-i18n:
    generated_at: "2026-04-05T12:54:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 217afafb693cf89651e8fa361252f7b5c197feb98d20be4697a83e6dedc0ec3f
    source_path: reference/transcript-hygiene.md
    workflow: 15
---

# Transcript Hygiene (Provider Fixups)

이 문서는 실행 전에 transcript(모델 컨텍스트 구성)에 적용되는 **provider별 수정**을 설명합니다.
이러한 수정은 엄격한 provider 요구 사항을 충족하기 위해 사용되는 **메모리 내**
조정입니다. 이러한 hygiene 단계는 디스크에 저장된 JSONL transcript를 **다시 쓰지**
않습니다. 그러나 별도의 세션 파일 복구 단계에서 세션이 로드되기 전에 잘못된 줄을 제거하여
형식이 잘못된 JSONL 파일을 다시 쓸 수 있습니다. 복구가 발생하면 원본
파일은 세션 파일과 함께 백업됩니다.

범위에는 다음이 포함됩니다.

- Tool call id 정리
- Tool call 입력 검증
- Tool result 페어링 복구
- 턴 검증 / 순서 정리
- thought signature 정리
- 이미지 페이로드 정리
- 사용자 입력 출처 태깅(세션 간 라우팅된 프롬프트용)

transcript 저장 세부 정보가 필요하면 다음을 참조하세요.

- [/reference/session-management-compaction](/reference/session-management-compaction)

---

## 이것이 실행되는 위치

모든 transcript hygiene는 임베디드 러너에 중앙화되어 있습니다.

- 정책 선택: `src/agents/transcript-policy.ts`
- 정리/복구 적용: `src/agents/pi-embedded-runner/google.ts`의 `sanitizeSessionHistory`

이 정책은 `provider`, `modelApi`, `modelId`를 사용해 무엇을 적용할지 결정합니다.

transcript hygiene와는 별도로, 세션 파일은 로드 전에(필요한 경우) 복구됩니다.

- `src/agents/session-file-repair.ts`의 `repairSessionFileIfNeeded`
- `run/attempt.ts` 및 `compact.ts`(임베디드 러너)에서 호출됨

---

## 전역 규칙: 이미지 정리

이미지 페이로드는 크기 제한으로 인한 provider 측 거부를 방지하기 위해 항상 정리됩니다
(과도하게 큰 base64 이미지를 축소/재압축).

이것은 비전 지원 모델에서 이미지 기반 토큰 압력을 제어하는 데도 도움이 됩니다.
최대 이미지 크기가 작을수록 일반적으로 토큰 사용량이 줄어들고, 클수록 세부 정보가 더 보존됩니다.

구현:

- `src/agents/pi-embedded-helpers/images.ts`의 `sanitizeSessionMessagesImages`
- `src/agents/tool-images.ts`의 `sanitizeContentBlocksImages`
- 최대 이미지 변 길이는 `agents.defaults.imageMaxDimensionPx`로 구성할 수 있습니다(기본값: `1200`).

---

## 전역 규칙: 형식이 잘못된 tool call

`input`과 `arguments`가 모두 없는 assistant tool-call 블록은
모델 컨텍스트가 구성되기 전에 제거됩니다. 이렇게 하면 부분적으로 저장된 tool call
(예: rate limit 실패 후)로 인한 provider 거부를 방지할 수 있습니다.

구현:

- `src/agents/session-transcript-repair.ts`의 `sanitizeToolCallInputs`
- `src/agents/pi-embedded-runner/google.ts`의 `sanitizeSessionHistory`에서 적용됨

---

## 전역 규칙: 세션 간 입력 출처

에이전트가 `sessions_send`를 통해 다른 세션으로 프롬프트를 보낼 때(에이전트 간 답장/공지 단계 포함),
OpenClaw는 생성된 사용자 턴을 다음과 함께 저장합니다.

- `message.provenance.kind = "inter_session"`

이 메타데이터는 transcript 추가 시점에 기록되며 역할은 변경하지
않습니다(`role: "user"`는 provider 호환성을 위해 유지됨). transcript 리더는
이를 사용해 라우팅된 내부 프롬프트를 최종 사용자 작성 지침으로 취급하지 않도록 할 수 있습니다.

컨텍스트를 다시 구성하는 동안 OpenClaw는 모델이 이를
외부 최종 사용자 지침과 구별할 수 있도록 메모리 내에서 해당 사용자 턴 앞에 짧은 `[Inter-session message]`
마커도 추가합니다.

---

## Provider 매트릭스(현재 동작)

**OpenAI / OpenAI Codex**

- 이미지 정리만 수행합니다.
- OpenAI Responses/Codex transcript에 대해 고아 reasoning signature(뒤따르는 content 블록이 없는 독립 reasoning 항목)를 제거합니다.
- Tool call id 정리는 하지 않습니다.
- Tool result 페어링 복구는 하지 않습니다.
- 턴 검증 또는 순서 재정리는 하지 않습니다.
- 합성 tool result는 생성하지 않습니다.
- thought signature 제거는 하지 않습니다.

**Google (Generative AI / Gemini CLI / Antigravity)**

- Tool call id 정리: 엄격한 영숫자.
- Tool result 페어링 복구 및 합성 tool result.
- 턴 검증(Gemini 스타일 턴 교대).
- Google 턴 순서 수정(history가 assistant로 시작하면 작은 user bootstrap을 앞에 추가).
- Antigravity Claude: thinking signature를 정규화하고, 서명되지 않은 thinking 블록은 제거합니다.

**Anthropic / Minimax (Anthropic 호환)**

- Tool result 페어링 복구 및 합성 tool result.
- 턴 검증(엄격한 교대를 만족하도록 연속된 user 턴 병합).

**Mistral (model-id 기반 감지 포함)**

- Tool call id 정리: strict9(길이 9의 영숫자).

**OpenRouter Gemini**

- thought signature 정리: base64가 아닌 `thought_signature` 값 제거(base64는 유지).

**그 외 모든 것**

- 이미지 정리만 수행합니다.

---

## 과거 동작(pre-2026.1.22)

2026.1.22 릴리스 이전에는 OpenClaw가 여러 계층의 transcript hygiene를 적용했습니다.

- 모든 컨텍스트 구성에서 실행되는 **transcript-sanitize extension**이 있었고, 다음을 수행할 수 있었습니다.
  - tool use/result 페어링 복구
  - tool call id 정리(`_`/`-`를 유지하는 비엄격 모드 포함)
- 러너도 provider별 정리를 수행했으며, 이로 인해 작업이 중복되었습니다.
- provider 정책 외부에서도 다음과 같은 추가 변경이 발생했습니다.
  - assistant 텍스트를 저장하기 전에 `<final>` 태그 제거
  - 비어 있는 assistant 오류 턴 제거
  - tool call 이후 assistant content 잘라내기

이 복잡성은 provider 간 회귀를 초래했습니다(특히 `openai-responses`
`call_id|fc_id` 페어링). 2026.1.22 정리에서는 extension을 제거하고,
로직을 러너에 중앙화했으며, 이미지 정리 외에는 OpenAI를 **무수정**으로 만들었습니다.
