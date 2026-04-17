---
read_when:
    - 사고, fast 모드 또는 verbose 지시문 파싱이나 기본값 조정
summary: '`/think`, `/fast`, `/verbose`, `/trace` 및 추론 가시성을 위한 지시문 구문'
title: 사고 수준
x-i18n:
    generated_at: "2026-04-17T06:01:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1cb44a7bf75546e5a8c3204e12f3297221449b881161d173dea4983da3921649
    source_path: tools/thinking.md
    workflow: 15
---

# 사고 수준 (/think 지시문)

## 기능

- 모든 수신 본문에서 사용할 수 있는 인라인 지시문: `/t <level>`, `/think:<level>`, 또는 `/thinking <level>`.
- 수준(별칭):
  `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink” (최대 예산)
  - xhigh → “ultrathink+” (GPT-5.2 + Codex 모델 및 Anthropic Claude Opus 4.7 effort)
  - adaptive → 제공자 관리형 적응형 사고(Anthropic Claude 4.6 및 Opus 4.7에서 지원)
  - `x-high`, `x_high`, `extra-high`, `extra high`, `extra_high`는 `xhigh`로 매핑됩니다.
  - `highest`, `max`는 `high`로 매핑됩니다.
- 제공자 참고 사항:
  - Anthropic Claude 4.6 모델은 명시적인 사고 수준이 설정되지 않은 경우 기본값으로 `adaptive`를 사용합니다.
  - Anthropic Claude Opus 4.7은 기본적으로 적응형 사고를 사용하지 않습니다. 명시적으로 사고 수준을 설정하지 않으면 API effort 기본값은 제공자가 관리합니다.
  - Anthropic Claude Opus 4.7은 `/think xhigh`를 적응형 사고와 `output_config.effort: "xhigh"`로 매핑합니다. `/think`는 사고 지시문이고 `xhigh`는 Opus 4.7의 effort 설정이기 때문입니다.
  - Anthropic 호환 스트리밍 경로의 MiniMax (`minimax/*`)는 모델 파라미터나 요청 파라미터에서 사고를 명시적으로 설정하지 않은 경우 기본값으로 `thinking: { type: "disabled" }`를 사용합니다. 이는 MiniMax의 비네이티브 Anthropic 스트림 형식에서 `reasoning_content` 델타가 노출되는 것을 방지합니다.
  - Z.AI (`zai/*`)는 이진 사고(`on`/`off`)만 지원합니다. `off`가 아닌 모든 수준은 `on`으로 처리됩니다(`low`로 매핑).
  - Moonshot (`moonshot/*`)은 `/think off`를 `thinking: { type: "disabled" }`로 매핑하고, `off`가 아닌 모든 수준을 `thinking: { type: "enabled" }`로 매핑합니다. 사고가 활성화되면 Moonshot은 `tool_choice`로 `auto|none`만 허용하므로, OpenClaw는 호환되지 않는 값을 `auto`로 정규화합니다.

## 확인 순서

1. 메시지의 인라인 지시문(해당 메시지에만 적용).
2. 세션 재정의(지시문만 포함된 메시지를 보내 설정).
3. 에이전트별 기본값(설정의 `agents.list[].thinkingDefault`).
4. 전역 기본값(설정의 `agents.defaults.thinkingDefault`).
5. 대체값: Anthropic Claude 4.6 모델은 `adaptive`, Anthropic Claude Opus 4.7은 명시적으로 구성되지 않은 경우 `off`, 그 외 추론 가능한 모델은 `low`, 그 외에는 `off`.

## 세션 기본값 설정

- 지시문만 **단독으로** 포함된 메시지를 보내세요(공백 허용). 예: `/think:medium` 또는 `/t high`.
- 이 설정은 현재 세션에 유지됩니다(기본적으로 발신자별). `/think:off` 또는 세션 유휴 초기화로 해제됩니다.
- 확인 응답이 전송됩니다(`Thinking level set to high.` / `Thinking disabled.`). 수준이 잘못된 경우(예: `/thinking big`) 명령이 거부되며 힌트가 반환되고, 세션 상태는 변경되지 않습니다.
- 현재 사고 수준을 보려면 인자 없이 `/think`(또는 `/think:`)를 보내세요.

## 에이전트별 적용

- **내장형 Pi**: 확인된 수준이 프로세스 내 Pi 에이전트 런타임으로 전달됩니다.

## Fast 모드 (/fast)

- 수준: `on|off`.
- 지시문만 포함된 메시지는 세션 fast-mode 재정의를 전환하고 `Fast mode enabled.` / `Fast mode disabled.`로 응답합니다.
- 현재 유효한 fast-mode 상태를 보려면 모드 없이 `/fast`(또는 `/fast status`)를 보내세요.
- OpenClaw는 다음 순서로 fast mode를 확인합니다:
  1. 인라인/지시문 전용 `/fast on|off`
  2. 세션 재정의
  3. 에이전트별 기본값(`agents.list[].fastModeDefault`)
  4. 모델별 설정: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. 대체값: `off`
- `openai/*`의 경우 fast mode는 지원되는 Responses 요청에 `service_tier=priority`를 전송하여 OpenAI 우선 처리로 매핑됩니다.
- `openai-codex/*`의 경우 fast mode는 Codex Responses에도 동일한 `service_tier=priority` 플래그를 전송합니다. OpenClaw는 두 인증 경로 모두에서 하나의 공유 `/fast` 토글을 유지합니다.
- 직접적인 공개 `anthropic/*` 요청( `api.anthropic.com` 으로 전송되는 OAuth 인증 트래픽 포함)의 경우 fast mode는 Anthropic 서비스 티어로 매핑됩니다. `/fast on`은 `service_tier=auto`, `/fast off`는 `service_tier=standard_only`를 설정합니다.
- Anthropic 호환 경로의 `minimax/*`에서 `/fast on`(또는 `params.fastMode: true`)은 `MiniMax-M2.7`을 `MiniMax-M2.7-highspeed`로 다시 작성합니다.
- 명시적인 Anthropic `serviceTier` / `service_tier` 모델 파라미터가 둘 다 설정된 경우 fast-mode 기본값보다 우선합니다. OpenClaw는 Anthropic이 아닌 프록시 base URL에 대해서는 여전히 Anthropic 서비스 티어 주입을 건너뜁니다.

## Verbose 지시문 (/verbose 또는 /v)

- 수준: `on` (최소) | `full` | `off` (기본값).
- 지시문만 포함된 메시지는 세션 verbose를 전환하고 `Verbose logging enabled.` / `Verbose logging disabled.`로 응답합니다. 잘못된 수준은 상태를 변경하지 않고 힌트를 반환합니다.
- `/verbose off`는 명시적인 세션 재정의를 저장합니다. Sessions UI에서 `inherit`를 선택해 해제할 수 있습니다.
- 인라인 지시문은 해당 메시지에만 영향을 주며, 그 외에는 세션/전역 기본값이 적용됩니다.
- 현재 verbose 수준을 보려면 인자 없이 `/verbose`(또는 `/verbose:`)를 보내세요.
- verbose가 켜져 있으면 구조화된 도구 결과를 내보내는 에이전트(Pi, 기타 JSON 에이전트)는 각 도구 호출을 별도의 메타데이터 전용 메시지로 다시 보냅니다. 가능하면 `<emoji> <tool-name>: <arg>` 형식의 접두사(path/command)가 붙습니다. 이러한 도구 요약은 각 도구가 시작되자마자 전송되며(별도 버블), 스트리밍 델타로 전송되지는 않습니다.
- 도구 실패 요약은 일반 모드에서도 계속 표시되지만, 원시 오류 세부 접미사는 verbose가 `on` 또는 `full`일 때만 표시됩니다.
- verbose가 `full`이면 완료 후 도구 출력도 전달됩니다(별도 버블, 안전한 길이로 잘림). 실행 중에 `/verbose on|full|off`를 전환하면 이후 도구 버블은 새 설정을 따릅니다.

## Plugin 추적 지시문 (/trace)

- 수준: `on` | `off` (기본값).
- 지시문만 포함된 메시지는 세션 Plugin trace 출력을 전환하고 `Plugin trace enabled.` / `Plugin trace disabled.`로 응답합니다.
- 인라인 지시문은 해당 메시지에만 영향을 주며, 그 외에는 세션/전역 기본값이 적용됩니다.
- 현재 trace 수준을 보려면 인자 없이 `/trace`(또는 `/trace:`)를 보내세요.
- `/trace`는 `/verbose`보다 범위가 좁습니다. Active Memory 디버그 요약과 같은 Plugin 소유 trace/debug 줄만 노출합니다.
- 추적 줄은 `/status`에 나타날 수 있으며, 일반 어시스턴트 응답 뒤에 후속 진단 메시지로도 나타날 수 있습니다.

## 추론 가시성 (/reasoning)

- 수준: `on|off|stream`.
- 지시문만 포함된 메시지는 응답에서 사고 블록을 표시할지 여부를 전환합니다.
- 활성화되면 추론은 `Reasoning:` 접두사가 붙은 **별도 메시지**로 전송됩니다.
- `stream`(Telegram 전용): 응답 생성 중에 Telegram 초안 버블에 추론을 스트리밍한 다음, 추론 없이 최종 답변을 전송합니다.
- 별칭: `/reason`.
- 현재 추론 수준을 보려면 인자 없이 `/reasoning`(또는 `/reasoning:`)을 보내세요.
- 확인 순서: 인라인 지시문, 그다음 세션 재정의, 그다음 에이전트별 기본값(`agents.list[].reasoningDefault`), 그다음 대체값(`off`).

## 관련 항목

- Elevated mode 문서는 [Elevated mode](/ko/tools/elevated)에 있습니다.

## Heartbeat

- Heartbeat probe 본문은 구성된 heartbeat 프롬프트입니다(기본값: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`). heartbeat 메시지의 인라인 지시문은 평소처럼 적용되지만(heartbeat에서 세션 기본값을 변경하지 않는 것이 좋습니다).
- Heartbeat 전달은 기본적으로 최종 페이로드만 보냅니다. 별도의 `Reasoning:` 메시지도 함께 보내려면(사용 가능한 경우) `agents.defaults.heartbeat.includeReasoning: true` 또는 에이전트별 `agents.list[].heartbeat.includeReasoning: true`를 설정하세요.

## 웹 채팅 UI

- 웹 채팅 사고 선택기는 페이지가 로드될 때 수신 세션 저장소/설정에 저장된 세션 수준을 그대로 반영합니다.
- 다른 수준을 선택하면 `sessions.patch`를 통해 세션 재정의가 즉시 기록됩니다. 다음 전송까지 기다리지 않으며, 일회성 `thinkingOnce` 재정의도 아닙니다.
- 첫 번째 옵션은 항상 `Default (<resolved level>)`이며, 확인된 기본값은 활성 세션 모델에서 가져옵니다. Anthropic의 Claude 4.6은 `adaptive`, Anthropic Claude Opus 4.7은 구성되지 않은 경우 `off`, 그 외 추론 가능한 모델은 `low`, 그 외에는 `off`입니다.
- 선택기는 계속 제공자 인식 상태를 유지합니다:
  - 대부분의 제공자는 `off | minimal | low | medium | high | adaptive`를 표시합니다.
  - Anthropic Claude Opus 4.7은 `off | minimal | low | medium | high | xhigh | adaptive`를 표시합니다.
  - Z.AI는 이진값 `off | on`을 표시합니다.
- `/think:<level>`도 계속 동작하며 동일하게 저장된 세션 수준을 업데이트하므로, 채팅 지시문과 선택기는 동기화된 상태를 유지합니다.
