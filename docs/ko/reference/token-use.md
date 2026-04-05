---
read_when:
    - 토큰 사용량, 비용 또는 컨텍스트 윈도우를 설명하려는 경우
    - 컨텍스트 증가 또는 compaction 동작을 디버깅하려는 경우
summary: OpenClaw가 프롬프트 컨텍스트를 구성하고 토큰 사용량 및 비용을 보고하는 방식
title: 토큰 사용량 및 비용
x-i18n:
    generated_at: "2026-04-05T12:55:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14e7a0ac0311298cf1484d663799a3f5a9687dd5afc9702233e983aba1979f1d
    source_path: reference/token-use.md
    workflow: 15
---

# 토큰 사용량 및 비용

OpenClaw는 문자 수가 아니라 **토큰**을 추적합니다. 토큰은 모델마다 다르지만,
대부분의 OpenAI 스타일 모델은 영어 텍스트 기준으로 평균적으로 토큰당 약 4자를 사용합니다.

## 시스템 프롬프트가 구성되는 방식

OpenClaw는 실행할 때마다 자체 시스템 프롬프트를 조립합니다. 여기에는 다음이 포함됩니다:

- 도구 목록 + 짧은 설명
- Skills 목록(메타데이터만 포함되며, 지침은 필요할 때 `read`로 로드됨)
- 자체 업데이트 지침
- 워크스페이스 + bootstrap 파일(`AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`, 새로 추가된 경우 `BOOTSTRAP.md`, 그리고 존재하는 경우 `MEMORY.md` 또는 소문자 폴백인 `memory.md`). 큰 파일은 `agents.defaults.bootstrapMaxChars`(기본값: 20000)로 잘리며, 전체 bootstrap 주입은 `agents.defaults.bootstrapTotalMaxChars`(기본값: 150000)로 제한됩니다. `memory/*.md` 파일은 메모리 도구를 통해 필요 시 로드되며 자동 주입되지 않습니다.
- 시간(UTC + 사용자 시간대)
- 응답 태그 + heartbeat 동작
- 런타임 메타데이터(호스트/OS/모델/thinking)

전체 세부 구성은 [시스템 프롬프트](/ko/concepts/system-prompt)를 참조하세요.

## 컨텍스트 윈도우에 포함되는 항목

모델이 받는 모든 항목은 컨텍스트 제한에 포함됩니다:

- 시스템 프롬프트(위에 나열된 모든 섹션)
- 대화 기록(사용자 + assistant 메시지)
- tool call 및 tool 결과
- 첨부 파일/transcript(이미지, 오디오, 파일)
- compaction 요약 및 가지치기 산출물
- provider 래퍼 또는 안전 헤더(보이지 않더라도 집계됨)

이미지의 경우, OpenClaw는 provider 호출 전에 transcript/tool 이미지 페이로드를 다운스케일합니다.
이를 조정하려면 `agents.defaults.imageMaxDimensionPx`(기본값: `1200`)를 사용하세요:

- 더 낮은 값은 일반적으로 비전 토큰 사용량과 페이로드 크기를 줄입니다.
- 더 높은 값은 OCR/UI 중심 스크린샷에서 더 많은 시각적 세부 정보를 유지합니다.

실제로 무엇이 포함되는지(주입된 파일별, 도구, Skills, 시스템 프롬프트 크기별) 자세히 보려면 `/context list` 또는 `/context detail`을 사용하세요. [Context](/ko/concepts/context)를 참조하세요.

## 현재 토큰 사용량을 보는 방법

채팅에서 다음 명령을 사용하세요:

- `/status` → 세션 모델, 컨텍스트 사용량,
  마지막 응답의 입력/출력 토큰, **예상 비용**(API 키 전용)을 보여 주는 **이모지 중심 상태 카드**
- `/usage off|tokens|full` → 모든 응답에 **응답별 사용량 바닥글**을 추가합니다.
  - 세션별로 유지됩니다(`responseUsage`로 저장됨).
  - OAuth 인증에서는 **비용이 숨겨집니다**(토큰만 표시).
- `/usage cost` → OpenClaw 세션 로그를 기반으로 로컬 비용 요약을 표시합니다.

기타 표면:

- **TUI/Web TUI:** `/status` + `/usage` 지원
- **CLI:** `openclaw status --usage` 및 `openclaw channels list`는
  정규화된 provider 할당량 윈도우(`X% left`, 응답별 비용 아님)를 표시합니다.
  현재 사용량 윈도우 provider: Anthropic, GitHub Copilot, Gemini CLI,
  OpenAI Codex, MiniMax, Xiaomi, z.ai.

사용량 표면은 표시 전에 공통 provider 고유 필드 별칭을 정규화합니다.
OpenAI 계열 Responses 트래픽의 경우, 여기에는 `input_tokens` /
`output_tokens`와 `prompt_tokens` / `completion_tokens`가 모두 포함되므로 전송별
필드 이름 차이가 `/status`, `/usage`, 세션 요약에 영향을 주지 않습니다.
Gemini CLI JSON 사용량도 정규화됩니다. 응답 텍스트는 `response`에서 가져오며,
CLI가 명시적인 `stats.input` 필드를 생략한 경우 `stats.cached`는 `cacheRead`로 매핑되고
`stats.input_tokens - stats.cached`가 사용됩니다.
네이티브 OpenAI 계열 Responses 트래픽의 경우에도 WebSocket/SSE 사용량 별칭이
같은 방식으로 정규화되며, `total_tokens`가 없거나 `0`이면 총합은 정규화된 입력 + 출력으로 폴백합니다.
현재 세션 스냅샷에 정보가 부족한 경우, `/status` 및 `session_status`는
가장 최근 transcript 사용량 로그에서 토큰/캐시 카운터와 활성 런타임 모델 레이블을 복구할 수도 있습니다.
기존의 0이 아닌 실시간 값은 여전히 transcript 폴백 값보다 우선하며,
저장된 총합이 없거나 더 작을 때는 더 큰 프롬프트 중심 transcript 총합이 우선될 수 있습니다.
provider 할당량 윈도우를 위한 사용량 인증은 가능한 경우 provider별 훅에서 가져오며,
그렇지 않으면 OpenClaw는 인증 프로필, env 또는 config의 일치하는 OAuth/API 키 자격 증명으로 폴백합니다.

## 비용 추정(표시되는 경우)

비용은 모델 가격 구성에서 추정됩니다:

```
models.providers.<provider>.models[].cost
```

이는 `input`, `output`, `cacheRead`, `cacheWrite`에 대한 **100만 토큰당 USD**입니다.
가격 정보가 없으면 OpenClaw는 토큰만 표시합니다. OAuth 토큰에는 달러 비용이 표시되지 않습니다.

## 캐시 TTL 및 가지치기 영향

provider 프롬프트 캐싱은 캐시 TTL 윈도우 내에서만 적용됩니다. OpenClaw는
선택적으로 **cache-ttl pruning**을 실행할 수 있습니다. 캐시 TTL이
만료되면 세션을 가지치기하고 캐시 윈도우를 재설정하여, 이후 요청이 전체 기록을
다시 캐시하는 대신 새로 캐시된 컨텍스트를 재사용할 수 있게 합니다. 이렇게 하면
세션이 TTL을 넘겨 유휴 상태가 된 경우 캐시 쓰기 비용을 낮게 유지할 수 있습니다.

이 기능은 [Gateway configuration](/ko/gateway/configuration)에서 구성할 수 있으며,
동작 세부 사항은 [세션 가지치기](/ko/concepts/session-pruning)에서 확인할 수 있습니다.

Heartbeat는 유휴 구간 동안 캐시를 **따뜻한 상태**로 유지할 수 있습니다. 모델 캐시 TTL이
`1h`라면, heartbeat 간격을 그보다 약간 짧게(예: `55m`) 설정하여 전체 프롬프트를
다시 캐시하지 않게 함으로써 캐시 쓰기 비용을 줄일 수 있습니다.

다중 에이전트 설정에서는 하나의 공유 모델 config를 유지하면서
`agents.list[].params.cacheRetention`으로 에이전트별 캐시 동작을 조정할 수 있습니다.

세부 옵션별 전체 가이드는 [프롬프트 캐싱](/reference/prompt-caching)을 참조하세요.

Anthropic API 가격의 경우, cache read는 input
토큰보다 훨씬 저렴한 반면 cache write는 더 높은 배수로 과금됩니다. 최신 요금과 TTL 배수는 Anthropic의
프롬프트 캐싱 가격 문서를 참조하세요:
[https://docs.anthropic.com/docs/build-with-claude/prompt-caching](https://docs.anthropic.com/docs/build-with-claude/prompt-caching)

### 예시: heartbeat로 1시간 캐시를 따뜻하게 유지

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
    heartbeat:
      every: "55m"
```

### 예시: 에이전트별 캐시 전략을 사용하는 혼합 트래픽

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long" # 대부분의 에이전트를 위한 기본 기준선
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m" # 심층 세션을 위해 긴 캐시를 따뜻하게 유지
    - id: "alerts"
      params:
        cacheRetention: "none" # 급증형 알림에서는 캐시 쓰기 방지
```

`agents.list[].params`는 선택한 모델의 `params` 위에 병합되므로,
다른 모델 기본값은 그대로 상속하면서 `cacheRetention`만 재정의할 수 있습니다.

### 예시: Anthropic 1M 컨텍스트 beta 헤더 활성화

Anthropic의 1M 컨텍스트 윈도우는 현재 beta 게이트가 적용됩니다. OpenClaw는
지원되는 Opus 또는 Sonnet 모델에서 `context1m`을 활성화하면 필요한
`anthropic-beta` 값을 주입할 수 있습니다.

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          context1m: true
```

이 설정은 Anthropic의 `context-1m-2025-08-07` beta 헤더로 매핑됩니다.

이 기능은 해당 모델 항목에 `context1m: true`가 설정된 경우에만 적용됩니다.

요구 사항: 자격 증명은 긴 컨텍스트 사용이 가능해야 합니다(API 키
과금 또는 Extra Usage가 활성화된 OpenClaw의 Claude 로그인 경로). 그렇지 않으면
Anthropic는
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`로 응답합니다.

Anthropic를 OAuth/구독 토큰(`sk-ant-oat-*`)으로 인증하는 경우,
Anthropic가 현재 이 조합을 HTTP 401로 거부하므로 OpenClaw는 `context-1m-*`
beta 헤더를 건너뜁니다.

## 토큰 부담을 줄이기 위한 팁

- `/compact`를 사용해 긴 세션을 요약하세요.
- 워크플로에서 큰 tool 출력을 잘라내세요.
- 스크린샷이 많은 세션에서는 `agents.defaults.imageMaxDimensionPx`를 낮추세요.
- Skill 설명은 짧게 유지하세요(Skill 목록이 프롬프트에 주입됨).
- 장황하고 탐색적인 작업에는 더 작은 모델을 선호하세요.

정확한 Skill 목록 오버헤드 계산식은 [Skills](/tools/skills)를 참조하세요.
