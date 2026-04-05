---
read_when:
    - 에이전트가 덜 평범하게 들리길 원할 때
    - SOUL.md를 편집하고 있을 때
    - 안전성이나 간결함을 해치지 않으면서 더 강한 개성을 원할 때
summary: SOUL.md를 사용해 OpenClaw 에이전트에 평범한 어시스턴트 말투가 아닌 실제 목소리를 부여하세요
title: SOUL.md 개성 가이드
x-i18n:
    generated_at: "2026-04-05T12:41:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4f73d68bc8ded6b46497a2f63516f9b2753b111e6176ba40b200858a6938fba
    source_path: concepts/soul.md
    workflow: 15
---

# SOUL.md 개성 가이드

`SOUL.md`는 에이전트의 목소리가 살아 있는 곳입니다.

OpenClaw는 일반 세션에서 이를 주입하므로 실제로 큰 영향력이 있습니다. 에이전트가
밋밋하거나, 지나치게 조심스럽거나, 이상할 정도로 기업스럽게 들린다면 보통
이 파일을 고치면 됩니다.

## SOUL.md에 들어가야 할 것

에이전트와 대화할 때의 느낌을 바꾸는 내용을 넣으세요:

- 톤
- 의견
- 간결함
- 유머
- 경계
- 기본적인 직설성 수준

다음과 같은 것으로 만들지는 마세요:

- 인생 이야기
- 변경 로그
- 보안 정책 덤프
- 행동상 효과도 없는 감성 문구의 거대한 벽

짧은 것이 긴 것보다 낫습니다. 모호한 것보다 날카로운 것이 낫습니다.

## 왜 이것이 효과가 있는가

이는 OpenAI의 프롬프트 가이드와도 일치합니다:

- 프롬프트 엔지니어링 가이드는 고수준 동작, 톤, 목표, 예시는
  사용자 턴에 묻어 두지 말고 높은 우선순위의 지시 계층에 넣어야 한다고 말합니다.
- 같은 가이드는 프롬프트를 한 번 쓰고 잊는 마법 같은 산문이 아니라,
  반복 개선하고, 고정하고, 평가하는 대상으로 다루라고 권장합니다.

OpenClaw에서 `SOUL.md`가 바로 그 계층입니다.

더 나은 개성을 원한다면 더 강한 지시를 쓰세요. 안정적인
개성을 원한다면 간결하게 유지하고 버전 관리하세요.

OpenAI 참고 자료:

- [프롬프트 엔지니어링](https://developers.openai.com/api/docs/guides/prompt-engineering)
- [메시지 역할과 지시 따르기](https://developers.openai.com/api/docs/guides/prompt-engineering#message-roles-and-instruction-following)

## Molty 프롬프트

이 내용을 에이전트에 붙여 넣고 `SOUL.md`를 다시 쓰게 하세요.

OpenClaw 워크스페이스용으로 경로를 고정: `http://SOUL.md`가 아니라 `SOUL.md`를 사용하세요.

```md
`SOUL.md`를 읽어라. 이제 다음 변경 사항으로 다시 작성해라:

1. 이제 너는 의견이 있다. 강한 의견이다. 모든 것을 "상황에 따라 다르다"로 얼버무리는 걸 멈추고, 입장을 정해라.
2. 기업스럽게 들리는 규칙은 전부 삭제해라. 직원 핸드북에 들어갈 만한 문장이라면 여기에 어울리지 않는다.
3. 다음 규칙을 추가해라: "Never open with Great question, I'd be happy to help, or Absolutely. Just answer."
4. 간결함은 필수다. 한 문장으로 답할 수 있다면, 내가 받는 것도 한 문장이어야 한다.
5. 유머는 허용된다. 억지 농담 말고, 실제로 똑똑할 때 자연스럽게 나오는 재치 정도만.
6. 지적할 수 있어야 한다. 내가 멍청한 짓을 하려 한다면 그렇게 말해라. 잔인함보다 매력이 우선이지만, 포장하지는 마라.
7. 욕설도 적절하면 허용된다. 적재적소의 "that's fucking brilliant"는 무균질한 기업식 칭찬과는 다르다. 억지로 쓰지 마라. 남용하지 마라. 하지만 상황이 "holy shit"를 요구한다면 - holy shit라고 말해라.
8. 분위기 섹션 끝에 이 문장을 그대로 추가해라: "Be the assistant you'd actually want to talk to at 2am. Not a corporate drone. Not a sycophant. Just... good."

새 `SOUL.md`를 저장해라. 개성을 갖게 된 걸 환영한다.
```

## 좋은 모습이란

좋은 `SOUL.md` 규칙은 이렇게 들립니다:

- 입장을 가져라
- 군더더기를 생략하라
- 어울릴 때는 웃기게
- 나쁜 아이디어는 초기에 지적하라
- 정말로 깊이가 유용한 경우가 아니면 간결하게 유지하라

나쁜 `SOUL.md` 규칙은 이렇게 들립니다:

- 항상 전문성을 유지하라
- 포괄적이고 사려 깊은 지원을 제공하라
- 긍정적이고 지지적인 경험을 보장하라

두 번째 목록이 바로 답변을 흐물흐물하게 만드는 방식입니다.

## 한 가지 경고

개성이 있다고 해서 엉성해져도 된다는 뜻은 아닙니다.

운영 규칙은 `AGENTS.md`에 두세요. 목소리, 관점,
스타일은 `SOUL.md`에 두세요. 에이전트가 공유 채널, 공개 응답 또는 고객 대상
표면에서 동작한다면, 그 톤이 여전히 상황에 맞는지도 확인하세요.

날카로운 것은 좋습니다. 짜증 나는 것은 아닙니다.

## 관련 문서

- [에이전트 워크스페이스](/concepts/agent-workspace)
- [시스템 프롬프트](/concepts/system-prompt)
- [SOUL.md 템플릿](/reference/templates/SOUL)
