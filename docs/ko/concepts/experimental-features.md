---
read_when:
    - '``.experimental`` config 키를 보고 이것이 안정적인지 알고 싶습니다.'
    - 일반 기본값과 혼동하지 않으면서 미리보기 런타임 기능을 사용해 보고 싶습니다.
    - 현재 문서화된 experimental 플래그를 한곳에서 찾고 싶습니다.
summary: OpenClaw에서 experimental 플래그는 무엇을 의미하며 현재 어떤 항목이 문서화되어 있나요?
title: 실험적 기능
x-i18n:
    generated_at: "2026-04-15T14:40:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# 실험적 기능

OpenClaw의 실험적 기능은 **옵트인 미리보기 표면**입니다. 안정적인 기본값이나 오래 유지되는 공개 계약으로 자리 잡기 전에 실제 환경에서의 충분한 검증이 더 필요하기 때문에, 명시적인 플래그 뒤에 숨겨져 있습니다.

이를 일반 config와는 다르게 취급하세요.

- 관련 문서에서 사용해 보라고 안내하지 않는 한 **기본적으로 꺼 둡니다**.
- 안정적인 config보다 **형태와 동작이 더 빠르게 바뀔 수 있음**을 예상하세요.
- 이미 안정적인 경로가 있다면 먼저 그 경로를 우선하세요.
- OpenClaw를 널리 배포하려는 경우, experimental 플래그를 공용 기준 설정에 포함하기 전에 더 작은 환경에서 먼저 테스트하세요.

## 현재 문서화된 플래그

| 표면 | 키 | 이런 경우 사용 | 자세히 보기 |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| 로컬 모델 런타임 | `agents.defaults.experimental.localModelLean` | 더 작거나 더 엄격한 로컬 백엔드가 OpenClaw의 전체 기본 도구 표면을 감당하지 못하는 경우 | [로컬 모델](/ko/gateway/local-models) |
| 메모리 검색 | `agents.defaults.memorySearch.experimental.sessionMemory` | `memory_search`가 이전 세션 대화 기록을 인덱싱하도록 하고, 추가 저장소/인덱싱 비용을 감수할 의향이 있는 경우 | [메모리 config 참조](/ko/reference/memory-config#session-memory-search-experimental) |
| 구조화된 계획 도구 | `tools.experimental.planTool` | 호환되는 런타임과 UI에서 다단계 작업 추적을 위해 구조화된 `update_plan` 도구를 노출하고 싶은 경우 | [Gateway config 참조](/ko/gateway/configuration-reference#toolsexperimental) |

## 로컬 모델 린 모드

`agents.defaults.experimental.localModelLean: true`는 성능이 약한 로컬 모델 환경을 위한 완충 장치입니다. `browser`, `cron`, `message` 같은 무거운 기본 도구를 줄여, 작은 컨텍스트나 더 엄격한 OpenAI 호환 백엔드에서도 프롬프트 형태가 더 작고 덜 취약하도록 만듭니다.

이것은 의도적으로 **일반적인 경로가 아닙니다**. 백엔드가 전체 런타임을 문제없이 처리할 수 있다면, 이 옵션은 끄고 두세요.

## 실험적이라고 해서 숨겨야 하는 것은 아닙니다

기능이 실험적이라면, OpenClaw는 문서와 config 경로 자체에서 이를 분명하게 밝혀야 합니다. 반대로 해서는 안 되는 것은, 미리보기 동작을 안정적으로 보이는 기본 노브에 몰래 섞어 넣고 그것이 정상인 것처럼 가장하는 일입니다. 그렇게 하면 config 표면이 지저분해집니다.
