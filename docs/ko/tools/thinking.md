---
read_when:
    - 사고, fast-mode, 또는 verbose 지시문 파싱이나 기본값을 조정하는 경우
summary: /think, /fast, /verbose 및 추론 표시를 위한 지시문 구문
title: 사고 수준
x-i18n:
    generated_at: "2026-04-05T12:58:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: f60aeb6ab4c7ce858f725f589f54184b29d8c91994d18c8deafa75179b9a62cb
    source_path: tools/thinking.md
    workflow: 15
---

# 사고 수준 (/think 지시문)

## 하는 일

- 모든 수신 본문에서 인라인 지시문 사용 가능: `/t <level>`, `/think:<level>`, 또는 `/thinking <level>`.
- 수준(별칭):
  `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink” (최대 예산)
  - xhigh → “ultrathink+” (GPT-5.2 + Codex 모델 전용)
  - adaptive → 제공자가 관리하는 적응형 추론 예산(Anthropic Claude 4.6 모델 패밀리에서 지원)
  - `x-high`, `x_high`, `extra-high`, `extra high`, `extra_high`는 `xhigh`로 매핑됩니다.
  - `highest`, `max`는 `high`로 매핑됩니다.
- 제공자 참고:
  - Anthropic Claude 4.6 모델은 명시적인 사고 수준이 설정되지 않으면 기본값으로 `adaptive`를 사용합니다.
  - Anthropic 호환 스트리밍 경로의 MiniMax (`minimax/*`)는 모델 params 또는 요청 params에서 사고를 명시적으로 설정하지 않으면 기본값으로 `thinking: { type: "disabled" }`를 사용합니다. 이는 MiniMax의 비기본 Anthropic 스트림 형식에서 `reasoning_content` 델타가 새는 것을 방지합니다.
  - Z.AI (`zai/*`)는 이진 사고(`on`/`off`)만 지원합니다. `off`가 아닌 모든 수준은 `on`으로 처리됩니다(`low`로 매핑).
  - Moonshot (`moonshot/*`)은 `/think off`를 `thinking: { type: "disabled" }`로, `off`가 아닌 모든 수준을 `thinking: { type: "enabled" }`로 매핑합니다. 사고가 활성화되면 Moonshot은 `tool_choice`로 `auto|none`만 허용하므로 OpenClaw는 호환되지 않는 값을 `auto`로 정규화합니다.

## 확인 순서

1. 메시지의 인라인 지시문(해당 메시지에만 적용).
2. 세션 재정의(지시문만 있는 메시지를 보내 설정).
3. 에이전트별 기본값(config의 `agents.list[].thinkingDefault`).
4. 전역 기본값(config의 `agents.defaults.thinkingDefault`).
5. 폴백: Anthropic Claude 4.6 모델은 `adaptive`, 다른 추론 가능 모델은 `low`, 그 외는 `off`.

## 세션 기본값 설정

- **지시문만** 있는 메시지를 보내세요(공백 허용). 예: `/think:medium` 또는 `/t high`.
- 이는 현재 세션에 유지됩니다(기본적으로 발신자별). `/think:off` 또는 세션 유휴 초기화로 해제됩니다.
- 확인 응답이 전송됩니다(`Thinking level set to high.` / `Thinking disabled.`). 수준이 잘못된 경우(예: `/thinking big`) 명령은 힌트와 함께 거부되고 세션 상태는 변경되지 않습니다.
- 현재 사고 수준을 보려면 인수 없이 `/think`(또는 `/think:`)를 보내세요.

## 에이전트별 적용

- **임베디드 Pi**: 확인된 수준이 인프로세스 Pi 에이전트 런타임에 전달됩니다.

## Fast 모드 (/fast)

- 수준: `on|off`.
- 지시문만 있는 메시지는 세션 fast-mode 재정의를 전환하고 `Fast mode enabled.` / `Fast mode disabled.`를 응답합니다.
- 현재 유효 fast-mode 상태를 보려면 모드 없이 `/fast`(또는 `/fast status`)를 보내세요.
- OpenClaw는 다음 순서로 fast 모드를 확인합니다:
  1. 인라인/지시문 전용 `/fast on|off`
  2. 세션 재정의
  3. 에이전트별 기본값(`agents.list[].fastModeDefault`)
  4. 모델별 config: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. 폴백: `off`
- `openai/*`의 경우 fast 모드는 지원되는 Responses 요청에 `service_tier=priority`를 보내는 방식으로 OpenAI 우선 처리에 매핑됩니다.
- `openai-codex/*`의 경우 fast 모드는 Codex Responses에 같은 `service_tier=priority` 플래그를 보냅니다. OpenClaw는 두 인증 경로 모두에서 하나의 공용 `/fast` 토글을 유지합니다.
- `api.anthropic.com`으로 전송되는 OAuth 인증 트래픽을 포함한 직접 공개 `anthropic/*` 요청의 경우 fast 모드는 Anthropic 서비스 티어에 매핑됩니다: `/fast on`은 `service_tier=auto`, `/fast off`는 `service_tier=standard_only`를 설정합니다.
- Anthropic 호환 경로의 `minimax/*`에서는 `/fast on`(또는 `params.fastMode: true`)이 `MiniMax-M2.7`을 `MiniMax-M2.7-highspeed`로 다시 씁니다.
- 둘 다 설정된 경우 명시적인 Anthropic `serviceTier` / `service_tier` 모델 params가 fast-mode 기본값보다 우선합니다. OpenClaw는 여전히 Anthropic이 아닌 프록시 기본 URL에는 Anthropic service-tier 주입을 건너뜁니다.

## Verbose 지시문 (/verbose 또는 /v)

- 수준: `on` (최소) | `full` | `off` (기본값).
- 지시문만 있는 메시지는 세션 verbose를 전환하고 `Verbose logging enabled.` / `Verbose logging disabled.`를 응답합니다. 잘못된 수준은 상태 변경 없이 힌트를 반환합니다.
- `/verbose off`는 명시적인 세션 재정의를 저장합니다. Sessions UI에서 `inherit`를 선택해 해제하세요.
- 인라인 지시문은 해당 메시지에만 영향을 주며, 그렇지 않은 경우 세션/전역 기본값이 적용됩니다.
- 현재 verbose 수준을 보려면 인수 없이 `/verbose`(또는 `/verbose:`)를 보내세요.
- verbose가 켜져 있으면 구조화된 도구 결과를 내는 에이전트(Pi, 기타 JSON 에이전트)는 각 도구 호출을 자체 메타데이터 전용 메시지로 다시 보냅니다. 가능한 경우 `<emoji> <tool-name>: <arg>`(경로/명령) 접두사가 붙습니다. 이러한 도구 요약은 스트리밍 델타가 아니라 각 도구가 시작되는 즉시 별도 버블로 전송됩니다.
- 도구 실패 요약은 일반 모드에서도 계속 보이지만, verbose가 `on` 또는 `full`이 아니면 원시 오류 세부 정보 접미사는 숨겨집니다.
- verbose가 `full`이면 도구 출력도 완료 후 전달됩니다(별도 버블, 안전한 길이로 잘림). 실행 중에 `/verbose on|full|off`를 전환하면 이후 도구 버블은 새 설정을 따릅니다.

## 추론 표시 (/reasoning)

- 수준: `on|off|stream`.
- 지시문만 있는 메시지는 응답에 사고 블록을 표시할지 전환합니다.
- 활성화되면 추론은 `Reasoning:` 접두사가 붙은 **별도 메시지**로 전송됩니다.
- `stream`(Telegram 전용): 응답 생성 중 Telegram 초안 버블에 추론을 스트리밍한 뒤, 최종 답변은 추론 없이 전송합니다.
- 별칭: `/reason`.
- 현재 추론 수준을 보려면 인수 없이 `/reasoning`(또는 `/reasoning:`)을 보내세요.
- 확인 순서: 인라인 지시문, 세션 재정의, 에이전트별 기본값(`agents.list[].reasoningDefault`), 폴백(`off`).

## 관련 문서

- 상승 모드 문서는 [상승 모드](/tools/elevated)에 있습니다.

## 하트비트

- 하트비트 프로브 본문은 구성된 하트비트 프롬프트입니다(기본값: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`). 하트비트 메시지의 인라인 지시문도 평소처럼 적용되지만(단, 하트비트에서 세션 기본값 변경은 피하세요).
- 하트비트 전달은 기본적으로 최종 페이로드만 사용합니다. 별도의 `Reasoning:` 메시지도 보내려면(가능한 경우) `agents.defaults.heartbeat.includeReasoning: true` 또는 에이전트별 `agents.list[].heartbeat.includeReasoning: true`를 설정하세요.

## 웹 채팅 UI

- 웹 채팅 사고 선택기는 페이지가 로드될 때 수신 세션 저장소/config의 세션 저장 수준을 반영합니다.
- 다른 수준을 선택하면 `sessions.patch`를 통해 세션 재정의를 즉시 기록합니다. 다음 전송까지 기다리지 않으며 일회성 `thinkingOnce` 재정의도 아닙니다.
- 첫 번째 옵션은 항상 `Default (<resolved level>)`이며, 확인된 기본값은 활성 세션 모델에서 옵니다: Anthropic/Bedrock의 Claude 4.6은 `adaptive`, 다른 추론 가능 모델은 `low`, 그 외는 `off`.
- 선택기는 계속 제공자 인식 상태를 유지합니다:
  - 대부분의 제공자는 `off | minimal | low | medium | high | adaptive`를 표시합니다
  - Z.AI는 이진 `off | on`을 표시합니다
- `/think:<level>`도 계속 동작하며 같은 저장된 세션 수준을 업데이트하므로 채팅 지시문과 선택기가 동기화된 상태를 유지합니다.
