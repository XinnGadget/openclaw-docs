---
read_when:
    - 캐시 유지로 프롬프트 토큰 비용을 줄이려는 경우
    - 멀티 에이전트 설정에서 에이전트별 캐시 동작이 필요한 경우
    - heartbeat와 cache-ttl 프루닝을 함께 조정하는 경우
summary: 프롬프트 캐싱 설정 항목, 병합 순서, 공급자 동작, 튜닝 패턴
title: 프롬프트 캐싱
x-i18n:
    generated_at: "2026-04-05T12:54:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 13d5f3153b6593ae22cd04a6c2540e074cf15df9f1990fc5b7184fe803f4a1bd
    source_path: reference/prompt-caching.md
    workflow: 15
---

# 프롬프트 캐싱

프롬프트 캐싱은 모델 공급자가 매 턴마다 다시 처리하는 대신, 턴 간에 변경되지 않은 프롬프트 접두사(보통 system/developer 지침 및 기타 안정적인 컨텍스트)를 재사용할 수 있음을 의미합니다. OpenClaw는 업스트림 API가 이러한 카운터를 직접 제공할 때 공급자 사용량을 `cacheRead`와 `cacheWrite`로 정규화합니다.

상태 표시 영역은 실시간 세션 스냅샷에 해당 카운터가 없을 때 가장 최근 전사 usage 로그에서 캐시 카운터를 복구할 수도 있으므로, 부분적인 세션 메타데이터 손실 이후에도 `/status`가 캐시 줄을 계속 표시할 수 있습니다. 기존의 0이 아닌 실시간 캐시 값은 여전히 전사 폴백 값보다 우선합니다.

이것이 중요한 이유: 낮은 토큰 비용, 더 빠른 응답, 장기 실행 세션에서 더 예측 가능한 성능을 얻을 수 있습니다. 캐싱이 없으면 대부분의 입력이 바뀌지 않았더라도 반복되는 프롬프트는 매 턴 전체 프롬프트 비용을 지불하게 됩니다.

이 페이지에서는 프롬프트 재사용과 토큰 비용에 영향을 주는 모든 캐시 관련 설정 항목을 다룹니다.

공급자 참조:

- Anthropic 프롬프트 캐싱: [https://platform.claude.com/docs/en/build-with-claude/prompt-caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- OpenAI 프롬프트 캐싱: [https://developers.openai.com/api/docs/guides/prompt-caching](https://developers.openai.com/api/docs/guides/prompt-caching)
- OpenAI API 헤더 및 요청 ID: [https://developers.openai.com/api/reference/overview](https://developers.openai.com/api/reference/overview)
- Anthropic 요청 ID 및 오류: [https://platform.claude.com/docs/en/api/errors](https://platform.claude.com/docs/en/api/errors)

## 주요 설정 항목

### `cacheRetention` (전역 기본값, 모델, 에이전트별)

모든 모델에 대한 전역 기본값으로 캐시 보존을 설정합니다:

```yaml
agents:
  defaults:
    params:
      cacheRetention: "long" # none | short | long
```

모델별로 재정의합니다:

```yaml
agents:
  defaults:
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "short" # none | short | long
```

에이전트별 재정의:

```yaml
agents:
  list:
    - id: "alerts"
      params:
        cacheRetention: "none"
```

구성 병합 순서:

1. `agents.defaults.params` (전역 기본값 — 모든 모델에 적용)
2. `agents.defaults.models["provider/model"].params` (모델별 재정의)
3. `agents.list[].params` (일치하는 에이전트 ID, 키별로 재정의)

### `contextPruning.mode: "cache-ttl"`

캐시 TTL 기간이 지난 오래된 도구 결과 컨텍스트를 제거하여 유휴 상태 이후 요청이 과도하게 큰 히스토리를 다시 캐싱하지 않도록 합니다.

```yaml
agents:
  defaults:
    contextPruning:
      mode: "cache-ttl"
      ttl: "1h"
```

전체 동작은 [세션 프루닝](/ko/concepts/session-pruning)을 참조하세요.

### Heartbeat keep-warm

Heartbeat는 캐시 기간을 따뜻하게 유지하고 유휴 간격 이후 반복적인 캐시 쓰기를 줄일 수 있습니다.

```yaml
agents:
  defaults:
    heartbeat:
      every: "55m"
```

에이전트별 heartbeat는 `agents.list[].heartbeat`에서 지원됩니다.

## 공급자 동작

### Anthropic (직접 API)

- `cacheRetention`이 지원됩니다.
- Anthropic API 키 인증 프로필을 사용할 경우, OpenClaw는 값이 설정되지 않은 Anthropic 모델 참조에 대해 `cacheRetention: "short"`를 기본으로 설정합니다.
- Anthropic 기본 Messages 응답은 `cache_read_input_tokens`와 `cache_creation_input_tokens`를 모두 노출하므로, OpenClaw는 `cacheRead`와 `cacheWrite`를 모두 표시할 수 있습니다.
- 기본 Anthropic 요청에서 `cacheRetention: "short"`는 기본 5분 ephemeral 캐시에 매핑되며, `cacheRetention: "long"`은 직접 `api.anthropic.com` 호스트에서만 1시간 TTL로 업그레이드됩니다.

### OpenAI (직접 API)

- 프롬프트 캐싱은 지원되는 최신 모델에서 자동입니다. OpenClaw는 블록 수준 캐시 마커를 삽입할 필요가 없습니다.
- OpenClaw는 턴 간 캐시 라우팅을 안정적으로 유지하기 위해 `prompt_cache_key`를 사용하고, 직접 OpenAI 호스트에서 `cacheRetention: "long"`이 선택된 경우에만 `prompt_cache_retention: "24h"`를 사용합니다.
- OpenAI 응답은 `usage.prompt_tokens_details.cached_tokens`(또는 Responses API 이벤트의 `input_tokens_details.cached_tokens`)를 통해 캐시된 프롬프트 토큰을 노출합니다. OpenClaw는 이를 `cacheRead`로 매핑합니다.
- OpenAI는 별도의 캐시 쓰기 토큰 카운터를 노출하지 않으므로, 공급자가 캐시를 워밍업하고 있더라도 OpenAI 경로에서는 `cacheWrite`가 `0`으로 유지됩니다.
- OpenAI는 `x-request-id`, `openai-processing-ms`, `x-ratelimit-*`와 같은 유용한 추적 및 속도 제한 헤더를 반환하지만, 캐시 적중 حساب은 헤더가 아니라 usage 페이로드에서 가져와야 합니다.
- 실제로 OpenAI는 Anthropic 스타일의 이동하는 전체 히스토리 재사용보다는 초기 접두사 캐시처럼 동작하는 경우가 많습니다. 안정적인 긴 접두사 텍스트 턴은 현재 실시간 프로브에서 `4864` 캐시 토큰 부근의 고원에 도달할 수 있지만, 도구 사용이 많거나 MCP 스타일 전사에서는 정확히 반복해도 `4608` 캐시 토큰 부근에서 고원에 머무는 경우가 많습니다.

### Anthropic Vertex

- Vertex AI의 Anthropic 모델(`anthropic-vertex/*`)은 직접 Anthropic과 동일한 방식으로 `cacheRetention`을 지원합니다.
- `cacheRetention: "long"`은 Vertex AI 엔드포인트에서 실제 1시간 프롬프트 캐시 TTL에 매핑됩니다.
- `anthropic-vertex`의 기본 캐시 보존은 직접 Anthropic 기본값과 일치합니다.
- Vertex 요청은 경계 인식 캐시 셰이핑을 통해 라우팅되므로 캐시 재사용이 공급자가 실제로 받는 내용과 일치하도록 유지됩니다.

### Amazon Bedrock

- Anthropic Claude 모델 참조(`amazon-bedrock/*anthropic.claude*`)는 명시적인 `cacheRetention` 전달을 지원합니다.
- Anthropic이 아닌 Bedrock 모델은 런타임에 `cacheRetention: "none"`으로 강제됩니다.

### OpenRouter Anthropic 모델

`openrouter/anthropic/*` 모델 참조의 경우, OpenClaw는 요청이 검증된 OpenRouter 경로(`openrouter`의 기본 엔드포인트 또는 `openrouter.ai`로 해석되는 모든 provider/base URL)를 계속 대상으로 하는 경우에만 프롬프트 캐시 재사용을 개선하기 위해 system/developer 프롬프트 블록에 Anthropic `cache_control`을 주입합니다.

모델을 임의의 OpenAI 호환 프록시 URL로 다시 지정하면 OpenClaw는 이러한 OpenRouter 전용 Anthropic 캐시 마커 주입을 중단합니다.

### 기타 공급자

공급자가 이 캐시 모드를 지원하지 않으면 `cacheRetention`은 효과가 없습니다.

### Google Gemini 직접 API

- 직접 Gemini 전송(`api: "google-generative-ai"`)은 업스트림 `cachedContentTokenCount`를 통해 캐시 적중을 보고하며, OpenClaw는 이를 `cacheRead`로 매핑합니다.
- 직접 Gemini 모델에 `cacheRetention`이 설정되면, OpenClaw는 Google AI Studio 실행에서 system 프롬프트용 `cachedContents` 리소스를 자동으로 생성, 재사용, 갱신합니다. 즉, 더 이상 캐시된 콘텐츠 핸들을 수동으로 미리 만들 필요가 없습니다.
- 기존의 Gemini 캐시 콘텐츠 핸들은 계속 `params.cachedContent`(또는 레거시 `params.cached_content`)를 통해 구성된 모델에 전달할 수 있습니다.
- 이는 Anthropic/OpenAI 프롬프트 접두사 캐싱과는 별개입니다. Gemini의 경우 OpenClaw는 요청에 캐시 마커를 주입하는 대신 공급자 기본 `cachedContents` 리소스를 관리합니다.

### Gemini CLI JSON usage

- Gemini CLI JSON 출력도 `stats.cached`를 통해 캐시 적중을 표시할 수 있으며, OpenClaw는 이를 `cacheRead`로 매핑합니다.
- CLI가 직접적인 `stats.input` 값을 생략하면 OpenClaw는 `stats.input_tokens - stats.cached`에서 입력 토큰을 도출합니다.
- 이것은 usage 정규화일 뿐입니다. OpenClaw가 Gemini CLI에 대해 Anthropic/OpenAI 스타일 프롬프트 캐시 마커를 만들고 있다는 의미는 아닙니다.

## 시스템 프롬프트 캐시 경계

OpenClaw는 system 프롬프트를 내부 캐시 접두사 경계로 구분되는 **안정적인 접두사**와 **변동적인 접미사**로 나눕니다. 경계 위의 내용(도구 정의, Skills 메타데이터, 워크스페이스 파일 및 기타 비교적 정적인 컨텍스트)은 턴 간 바이트 단위로 동일하게 유지되도록 정렬됩니다. 경계 아래의 내용(예: `HEARTBEAT.md`, 런타임 타임스탬프 및 기타 턴별 메타데이터)은 캐시된 접두사를 무효화하지 않고 변경될 수 있습니다.

핵심 설계 선택 사항:

- 안정적인 워크스페이스 프로젝트 컨텍스트 파일은 `HEARTBEAT.md`보다 앞에 정렬되므로 heartbeat 변동이 안정적인 접두사를 깨뜨리지 않습니다.
- 경계는 Anthropic 계열, OpenAI 계열, Google, CLI 전송 셰이핑 전반에 적용되므로 지원되는 모든 공급자가 동일한 접두사 안정성의 이점을 얻습니다.
- Codex Responses 및 Anthropic Vertex 요청은 경계 인식 캐시 셰이핑을 통해 라우팅되므로 캐시 재사용이 공급자가 실제로 받는 내용과 일치하도록 유지됩니다.
- system 프롬프트 지문은 정규화됩니다(공백, 줄바꿈, hook이 추가한 컨텍스트, 런타임 기능 순서) so 의미적으로 변경되지 않은 프롬프트가 턴 간 KV/캐시를 공유합니다.

구성 또는 워크스페이스 변경 후 예상치 못한 `cacheWrite` 급증이 보이면, 변경 사항이 캐시 경계 위에 있는지 아래에 있는지 확인하세요. 변동적인 내용을 경계 아래로 이동하거나(또는 안정화하면) 문제가 해결되는 경우가 많습니다.

## OpenClaw 캐시 안정성 보호 장치

OpenClaw는 요청이 공급자에 도달하기 전에 몇 가지 캐시 민감 페이로드 형태도 결정적으로 유지합니다:

- 번들 MCP 도구 카탈로그는 도구 등록 전에 결정적으로 정렬되므로 `listTools()` 순서 변경이 tools 블록을 흔들어 프롬프트 캐시 접두사를 깨뜨리지 않습니다.
- 지속된 이미지 블록이 있는 레거시 세션은 **가장 최근의 완료된 3개 턴**을 그대로 유지합니다. 더 오래된 이미 처리된 이미지 블록은 마커로 대체될 수 있으므로, 이미지가 많은 후속 요청이 오래된 큰 페이로드를 계속 다시 보내지 않습니다.

## 튜닝 패턴

### 혼합 트래픽(권장 기본값)

주 에이전트에는 오래 유지되는 기준 캐시를 두고, 급증형 알림 에이전트에서는 캐싱을 비활성화합니다:

```yaml
agents:
  defaults:
    model:
      primary: "anthropic/claude-opus-4-6"
    models:
      "anthropic/claude-opus-4-6":
        params:
          cacheRetention: "long"
  list:
    - id: "research"
      default: true
      heartbeat:
        every: "55m"
    - id: "alerts"
      params:
        cacheRetention: "none"
```

### 비용 우선 기준선

- 기준 `cacheRetention: "short"`를 설정합니다.
- `contextPruning.mode: "cache-ttl"`을 활성화합니다.
- 따뜻한 캐시가 도움이 되는 에이전트에 대해서만 heartbeat를 TTL보다 낮게 유지합니다.

## 캐시 진단

OpenClaw는 내장 에이전트 실행을 위한 전용 캐시 추적 진단을 제공합니다.

일반 사용자 대상 진단의 경우, `/status` 및 기타 usage 요약은 실시간 세션 항목에 해당 카운터가 없을 때 `cacheRead` / `cacheWrite`의 폴백 소스로 최신 전사 usage 항목을 사용할 수 있습니다.

## 실시간 회귀 테스트

OpenClaw는 반복 접두사, 도구 턴, 이미지 턴, MCP 스타일 도구 전사, Anthropic no-cache 대조군에 대해 하나의 결합된 실시간 캐시 회귀 게이트를 유지합니다.

- `src/agents/live-cache-regression.live.test.ts`
- `src/agents/live-cache-regression-baseline.ts`

다음으로 좁은 실시간 게이트를 실행합니다:

```sh
OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache
```

기준 파일은 가장 최근에 관찰된 실시간 수치와 테스트에서 사용하는 공급자별 회귀 하한을 저장합니다.
러너는 이전 캐시 상태가 현재 회귀 샘플을 오염시키지 않도록 실행마다 새로운 세션 ID와 프롬프트 네임스페이스도 사용합니다.

이 테스트는 의도적으로 공급자 간에 동일한 성공 기준을 사용하지 않습니다.

### Anthropic 실시간 기대값

- `cacheWrite`를 통한 명시적인 워밍업 쓰기를 기대합니다.
- Anthropic 캐시 제어가 대화 전반에서 캐시 중단점을 앞으로 이동시키므로 반복 턴에서 거의 전체 히스토리 재사용을 기대합니다.
- 현재 실시간 단언은 안정적, 도구, 이미지 경로에 대해 여전히 높은 적중률 임곗값을 사용합니다.

### OpenAI 실시간 기대값

- `cacheRead`만 기대합니다. `cacheWrite`는 `0`으로 유지됩니다.
- 반복 턴 캐시 재사용은 Anthropic 스타일의 이동하는 전체 히스토리 재사용이 아니라 공급자별 고원으로 취급합니다.
- 현재 실시간 단언은 `gpt-5.4-mini`에서 관찰된 실시간 동작에서 도출된 보수적인 하한 검사를 사용합니다:
  - 안정적 접두사: `cacheRead >= 4608`, 적중률 `>= 0.90`
  - 도구 전사: `cacheRead >= 4096`, 적중률 `>= 0.85`
  - 이미지 전사: `cacheRead >= 3840`, 적중률 `>= 0.82`
  - MCP 스타일 전사: `cacheRead >= 4096`, 적중률 `>= 0.85`

2026-04-04의 최신 결합 실시간 검증 결과는 다음과 같습니다:

- 안정적 접두사: `cacheRead=4864`, 적중률 `0.966`
- 도구 전사: `cacheRead=4608`, 적중률 `0.896`
- 이미지 전사: `cacheRead=4864`, 적중률 `0.954`
- MCP 스타일 전사: `cacheRead=4608`, 적중률 `0.891`

결합 게이트의 최근 로컬 경과 시간은 약 `88s`였습니다.

단언이 다른 이유:

- Anthropic은 명시적인 캐시 중단점과 이동하는 대화 히스토리 재사용을 노출합니다.
- OpenAI 프롬프트 캐싱도 여전히 정확한 접두사에 민감하지만, 실시간 Responses 트래픽에서 실제로 재사용 가능한 접두사는 전체 프롬프트보다 더 이른 지점에서 고원에 도달할 수 있습니다.
- 따라서 Anthropic과 OpenAI를 단일 공급자 간 백분율 임곗값으로 비교하면 잘못된 회귀가 발생합니다.

### `diagnostics.cacheTrace` 구성

```yaml
diagnostics:
  cacheTrace:
    enabled: true
    filePath: "~/.openclaw/logs/cache-trace.jsonl" # optional
    includeMessages: false # default true
    includePrompt: false # default true
    includeSystem: false # default true
```

기본값:

- `filePath`: `$OPENCLAW_STATE_DIR/logs/cache-trace.jsonl`
- `includeMessages`: `true`
- `includePrompt`: `true`
- `includeSystem`: `true`

### 환경 변수 토글(일회성 디버깅)

- `OPENCLAW_CACHE_TRACE=1`은 캐시 추적을 활성화합니다.
- `OPENCLAW_CACHE_TRACE_FILE=/path/to/cache-trace.jsonl`은 출력 경로를 재정의합니다.
- `OPENCLAW_CACHE_TRACE_MESSAGES=0|1`은 전체 메시지 페이로드 캡처를 전환합니다.
- `OPENCLAW_CACHE_TRACE_PROMPT=0|1`은 프롬프트 텍스트 캡처를 전환합니다.
- `OPENCLAW_CACHE_TRACE_SYSTEM=0|1`은 system 프롬프트 캡처를 전환합니다.

### 확인할 항목

- 캐시 추적 이벤트는 JSONL이며 `session:loaded`, `prompt:before`, `stream:context`, `session:after`와 같은 단계별 스냅샷을 포함합니다.
- 턴별 캐시 토큰 영향은 `cacheRead` 및 `cacheWrite`를 통해 일반 usage 표시 영역에서 확인할 수 있습니다(예: `/usage full` 및 세션 usage 요약).
- Anthropic의 경우 캐싱이 활성화되어 있으면 `cacheRead`와 `cacheWrite` 둘 다 기대할 수 있습니다.
- OpenAI의 경우 캐시 적중 시 `cacheRead`를 기대하고 `cacheWrite`는 `0`으로 유지됩니다. OpenAI는 별도의 캐시 쓰기 토큰 필드를 공개하지 않습니다.
- 요청 추적이 필요하면 캐시 메트릭과 별도로 요청 ID 및 속도 제한 헤더를 기록하세요. OpenClaw의 현재 캐시 추적 출력은 원시 공급자 응답 헤더보다는 프롬프트/세션 형태와 정규화된 토큰 usage에 중점을 둡니다.

## 빠른 문제 해결

- 대부분의 턴에서 `cacheWrite`가 높음: 변동적인 system 프롬프트 입력을 확인하고 모델/공급자가 해당 캐시 설정을 지원하는지 검증하세요.
- Anthropic에서 `cacheWrite`가 높음: 캐시 중단점이 매 요청마다 바뀌는 콘텐츠에 걸리는 경우가 많습니다.
- OpenAI에서 `cacheRead`가 낮음: 안정적인 접두사가 앞쪽에 있는지, 반복 접두사가 최소 1024 토큰인지, 캐시를 공유해야 하는 턴 간에 동일한 `prompt_cache_key`가 재사용되는지 확인하세요.
- `cacheRetention`에 효과가 없음: 모델 키가 `agents.defaults.models["provider/model"]`와 일치하는지 확인하세요.
- 캐시 설정이 있는 Bedrock Nova/Mistral 요청: 런타임에서 `none`으로 강제되는 것이 정상입니다.

관련 문서:

- [Anthropic](/providers/anthropic)
- [토큰 사용량 및 비용](/reference/token-use)
- [세션 프루닝](/ko/concepts/session-pruning)
- [Gateway 구성 참조](/ko/gateway/configuration-reference)
