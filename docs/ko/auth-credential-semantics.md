---
read_when:
    - 인증 프로필 해석 또는 자격 증명 라우팅 작업 중
    - 모델 인증 실패 또는 프로필 순서를 디버깅하는 중
summary: 인증 프로필에 대한 정식 자격 증명 적격성 및 해석 의미 체계
title: 인증 자격 증명 의미 체계
x-i18n:
    generated_at: "2026-04-05T12:34:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4cd3e16cd25eb22c5e707311d06a19df1a59747ee3261c2d32c534a245fd7fb
    source_path: auth-credential-semantics.md
    workflow: 15
---

# 인증 자격 증명 의미 체계

이 문서는 다음 전반에서 사용되는 정식 자격 증명 적격성 및 해석 의미 체계를 정의합니다.

- `resolveAuthProfileOrder`
- `resolveApiKeyForProfile`
- `models status --probe`
- `doctor-auth`

목표는 선택 시점 동작과 런타임 동작이 일치하도록 유지하는 것입니다.

## 안정적인 프로브 이유 코드

- `ok`
- `excluded_by_auth_order`
- `missing_credential`
- `invalid_expires`
- `expired`
- `unresolved_ref`
- `no_model`

## 토큰 자격 증명

토큰 자격 증명(`type: "token"`)은 인라인 `token` 및/또는 `tokenRef`를 지원합니다.

### 적격성 규칙

1. `token`과 `tokenRef`가 모두 없으면 토큰 프로필은 부적격입니다.
2. `expires`는 선택 사항입니다.
3. `expires`가 있으면 `0`보다 큰 유한한 숫자여야 합니다.
4. `expires`가 유효하지 않으면(`NaN`, `0`, 음수, 비유한값 또는 잘못된 타입) 프로필은 `invalid_expires`와 함께 부적격입니다.
5. `expires`가 과거 시점이면 프로필은 `expired`와 함께 부적격입니다.
6. `tokenRef`는 `expires` 검사를 우회하지 않습니다.

### 해석 규칙

1. 리졸버 의미 체계는 `expires`에 대해 적격성 의미 체계와 일치합니다.
2. 적격한 프로필의 경우 토큰 자료는 인라인 값 또는 `tokenRef`에서 해석될 수 있습니다.
3. 해석할 수 없는 ref는 `models status --probe` 출력에서 `unresolved_ref`를 생성합니다.

## 명시적 인증 순서 필터링

- 공급자에 대해 `auth.order.<provider>` 또는 인증 저장소 순서 재정의가 설정되면 `models status --probe`는 해당 공급자에 대해 해석된 인증 순서에 남아 있는 프로필 ID만 프로브합니다.
- 해당 공급자에 대한 저장된 프로필이 명시적 순서에서 생략된 경우 나중에 조용히 시도되지 않습니다. 프로브 출력은 이를 `reasonCode: excluded_by_auth_order` 및 세부 정보 `Excluded by auth.order for this provider.`와 함께 보고합니다.

## 프로브 대상 해석

- 프로브 대상은 인증 프로필, 환경 자격 증명 또는 `models.json`에서 올 수 있습니다.
- 공급자에 자격 증명이 있지만 OpenClaw가 해당 공급자에 대해 프로브 가능한 모델 후보를 해석할 수 없으면 `models status --probe`는 `reasonCode: no_model`과 함께 `status: no_model`을 보고합니다.

## OAuth SecretRef 정책 가드

- SecretRef 입력은 정적 자격 증명에만 사용됩니다.
- 프로필 자격 증명이 `type: "oauth"`이면 해당 프로필 자격 증명 자료에 대해 SecretRef 객체는 지원되지 않습니다.
- `auth.profiles.<id>.mode`가 `"oauth"`이면 해당 프로필에 대한 SecretRef 기반 `keyRef`/`tokenRef` 입력은 거부됩니다.
- 위반은 시작/리로드 인증 해석 경로에서 강한 실패로 처리됩니다.

## 레거시 호환 메시지

스크립트 호환성을 위해 프로브 오류는 이 첫 번째 줄을 변경하지 않고 유지합니다.

`Auth profile credentials are missing or expired.`

사람이 이해하기 쉬운 세부 정보와 안정적인 이유 코드는 후속 줄에 추가될 수 있습니다.
