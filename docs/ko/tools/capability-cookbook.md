---
read_when:
    - 새로운 코어 capability와 플러그인 등록 표면을 추가하고 있습니다
    - 코드가 코어, 벤더 플러그인, 또는 기능 플러그인 중 어디에 속해야 하는지 결정하고 있습니다
    - 채널이나 도구를 위한 새 런타임 헬퍼를 연결하고 있습니다
sidebarTitle: Adding Capabilities
summary: OpenClaw 플러그인 시스템에 새로운 공유 capability를 추가하기 위한 기여자 가이드
title: Capabilities 추가하기(기여자 가이드)
x-i18n:
    generated_at: "2026-04-05T12:56:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 29604d88e6df5205b835d71f3078b6223c58b6294135c3e201756c1bcac33ea3
    source_path: tools/capability-cookbook.md
    workflow: 15
---

# Capabilities 추가하기

<Info>
  이 문서는 OpenClaw 코어 개발자를 위한 **기여자 가이드**입니다. 외부 플러그인을
  빌드하는 경우에는 [플러그인 빌드하기](/ko/plugins/building-plugins)를
  참고하세요.
</Info>

이미지 생성, 비디오 생성, 또는 앞으로의 벤더 지원 기능 영역 같은 새로운 도메인이
OpenClaw에 필요할 때 이 문서를 사용하세요.

규칙은 다음과 같습니다:

- plugin = 소유권 경계
- capability = 공유 코어 계약

즉, 채널이나 도구에 벤더를 직접 연결하는 것부터 시작하면 안 됩니다.
먼저 capability를 정의하세요.

## capability를 만들어야 하는 경우

다음이 모두 참일 때 새로운 capability를 만드세요:

1. 둘 이상의 벤더가 이를 구현할 가능성이 충분히 있음
2. 채널, 도구, 또는 기능 플러그인이 벤더에 신경 쓰지 않고 이를 소비해야 함
3. 폴백, 정책, config, 또는 전달 동작을 코어가 소유해야 함

작업이 벤더 전용이고 아직 공유 계약이 없다면, 멈추고 먼저 계약을
정의하세요.

## 표준 순서

1. 타입이 지정된 코어 계약을 정의합니다.
2. 해당 계약에 대한 플러그인 등록을 추가합니다.
3. 공유 런타임 헬퍼를 추가합니다.
4. 실제 벤더 플러그인 하나를 증거로 연결합니다.
5. 기능/채널 소비자를 런타임 헬퍼로 옮깁니다.
6. 계약 테스트를 추가합니다.
7. 운영자 대상 config와 소유권 모델을 문서화합니다.

## 무엇을 어디에 둘 것인가

코어:

- 요청/응답 타입
- 제공자 레지스트리 + 해석
- 폴백 동작
- 중첩 객체, 와일드카드, 배열 항목, 컴포지션 노드에 전파되는
  `title` / `description` 문서 메타데이터를 포함한 config 스키마
- 런타임 헬퍼 표면

벤더 플러그인:

- 벤더 API 호출
- 벤더 인증 처리
- 벤더별 요청 정규화
- capability 구현 등록

기능/채널 플러그인:

- `api.runtime.*` 또는 일치하는 `plugin-sdk/*-runtime` 헬퍼를 호출
- 벤더 구현을 직접 호출하지 않음

## 파일 체크리스트

새 capability의 경우, 다음 영역을 수정하게 될 가능성이 높습니다:

- `src/<capability>/types.ts`
- `src/<capability>/...registry/runtime.ts`
- `src/plugins/types.ts`
- `src/plugins/registry.ts`
- `src/plugins/captured-registration.ts`
- `src/plugins/contracts/registry.ts`
- `src/plugins/runtime/types-core.ts`
- `src/plugins/runtime/index.ts`
- `src/plugin-sdk/<capability>.ts`
- `src/plugin-sdk/<capability>-runtime.ts`
- 하나 이상의 번들 플러그인 패키지
- config/docs/tests

## 예시: 이미지 생성

이미지 생성은 표준 형태를 따릅니다:

1. 코어가 `ImageGenerationProvider`를 정의합니다
2. 코어가 `registerImageGenerationProvider(...)`를 노출합니다
3. 코어가 `runtime.imageGeneration.generate(...)`를 노출합니다
4. `openai`, `google`, `fal`, `minimax` 플러그인이 벤더 지원 구현을 등록합니다
5. 이후 벤더는 채널/도구를 변경하지 않고 동일한 계약을 등록할 수 있습니다

config 키는 vision-analysis 라우팅과 분리되어 있습니다:

- `agents.defaults.imageModel` = 이미지 분석
- `agents.defaults.imageGenerationModel` = 이미지 생성

폴백과 정책이 명시적으로 유지되도록 이 둘은 분리해서 두세요.

## 검토 체크리스트

새 capability를 배포하기 전에 다음을 확인하세요:

- 어떤 채널/도구도 벤더 코드를 직접 import하지 않음
- 런타임 헬퍼가 공유 경로임
- 적어도 하나의 계약 테스트가 번들 소유권을 검증함
- config 문서에 새 모델/config 키가 명시되어 있음
- 플러그인 문서가 소유권 경계를 설명함

PR이 capability 계층을 건너뛰고 채널/도구에 벤더 동작을 하드코딩한다면,
되돌려 보내고 먼저 계약을 정의하세요.
