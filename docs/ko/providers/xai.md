---
read_when:
    - OpenClaw에서 Grok 모델을 사용하려는 경우
    - xAI 인증 또는 모델 ID를 구성하는 경우
summary: OpenClaw에서 xAI Grok 모델 사용
title: xAI
x-i18n:
    generated_at: "2026-04-05T12:53:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: d11f27b48c69eed6324595977bca3506c7709424eef64cc73899f8d049148b82
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw는 Grok 모델용 번들 `xai` 공급자 plugin을 제공합니다.

## 설정

1. xAI 콘솔에서 API 키를 생성합니다.
2. `XAI_API_KEY`를 설정하거나 다음을 실행합니다:

```bash
openclaw onboard --auth-choice xai-api-key
```

3. 다음과 같은 모델을 선택합니다:

```json5
{
  agents: { defaults: { model: { primary: "xai/grok-4" } } },
}
```

이제 OpenClaw는 번들 xAI 전송 방식으로 xAI Responses API를 사용합니다. 동일한 `XAI_API_KEY`는 Grok 기반 `web_search`, 기본 제공 `x_search`, 원격 `code_execution`에도 사용할 수 있습니다.
`plugins.entries.xai.config.webSearch.apiKey` 아래에 xAI 키를 저장하면 번들 xAI 모델 공급자도 해당 키를 폴백으로 재사용합니다.
`code_execution` 튜닝은 `plugins.entries.xai.config.codeExecution` 아래에 있습니다.

## 현재 번들 모델 카탈로그

이제 OpenClaw에는 다음 xAI 모델 계열이 기본 포함됩니다:

- `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`
- `grok-4`, `grok-4-0709`
- `grok-4-fast`, `grok-4-fast-non-reasoning`
- `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`
- `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning`
- `grok-code-fast-1`

이 plugin은 동일한 API 형태를 따르는 더 새로운 `grok-4*` 및 `grok-code-fast*` ID도 포워드 해석합니다.

고속 모델 참고 사항:

- `grok-4-fast`, `grok-4-1-fast`, `grok-4.20-beta-*` 변형은 현재 번들 카탈로그에서 이미지 기능을 지원하는 Grok 참조입니다.
- `/fast on` 또는 `agents.defaults.models["xai/<model>"].params.fastMode: true`는 기본 xAI 요청을 다음과 같이 다시 씁니다:
  - `grok-3` -> `grok-3-fast`
  - `grok-3-mini` -> `grok-3-mini-fast`
  - `grok-4` -> `grok-4-fast`
  - `grok-4-0709` -> `grok-4-fast`

레거시 호환성 별칭은 여전히 정식 번들 ID로 정규화됩니다. 예를 들면 다음과 같습니다:

- `grok-4-fast-reasoning` -> `grok-4-fast`
- `grok-4-1-fast-reasoning` -> `grok-4-1-fast`
- `grok-4.20-reasoning` -> `grok-4.20-beta-latest-reasoning`
- `grok-4.20-non-reasoning` -> `grok-4.20-beta-latest-non-reasoning`

## 웹 검색

번들 `grok` 웹 검색 공급자도 `XAI_API_KEY`를 사용합니다:

```bash
openclaw config set tools.web.search.provider grok
```

## 알려진 제한 사항

- 현재 인증은 API 키만 지원합니다. OpenClaw에는 아직 xAI OAuth/디바이스 코드 흐름이 없습니다.
- `grok-4.20-multi-agent-experimental-beta-0304`는 표준 OpenClaw xAI 전송 방식과 다른 업스트림 API 표면이 필요하므로 일반 xAI 공급자 경로에서 지원되지 않습니다.

## 참고 사항

- OpenClaw는 공유 러너 경로에서 xAI 전용 도구 스키마 및 도구 호출 호환성 수정을 자동으로 적용합니다.
- 기본 xAI 요청은 기본적으로 `tool_stream: true`를 사용합니다. 이를 비활성화하려면 `agents.defaults.models["xai/<model>"].params.tool_stream`을 `false`로 설정하세요.
- 번들 xAI 래퍼는 기본 xAI 요청을 보내기 전에 지원되지 않는 엄격한 도구 스키마 플래그와 추론 페이로드 키를 제거합니다.
- `web_search`, `x_search`, `code_execution`은 OpenClaw 도구로 노출됩니다. OpenClaw는 모든 채팅 턴에 모든 기본 도구를 붙이는 대신, 각 도구 요청 안에서 필요한 특정 xAI 기본 기능만 활성화합니다.
- `x_search`와 `code_execution`은 코어 모델 런타임에 하드코딩된 것이 아니라 번들 xAI plugin이 소유합니다.
- `code_execution`은 로컬 [`exec`](/tools/exec)가 아니라 원격 xAI 샌드박스 실행입니다.
- 더 넓은 공급자 개요는 [모델 공급자](/providers/index)를 참조하세요.
