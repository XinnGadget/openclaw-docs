---
read_when:
    - 메뉴 바 아이콘 동작을 변경하는 경우
summary: macOS용 OpenClaw의 메뉴 바 아이콘 상태 및 애니메이션
title: 메뉴 바 아이콘
x-i18n:
    generated_at: "2026-04-05T12:48:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: a67a6e6bbdc2b611ba365d3be3dd83f9e24025d02366bc35ffcce9f0b121872b
    source_path: platforms/mac/icon.md
    workflow: 15
---

# 메뉴 바 아이콘 상태

작성자: steipete · 업데이트: 2025-12-06 · 범위: macOS 앱 (`apps/macos`)

- **유휴:** 일반 아이콘 애니메이션(깜빡임, 가끔 흔들림).
- **일시 정지:** 상태 항목이 `appearsDisabled`를 사용하며, 움직임이 없습니다.
- **음성 트리거(큰 귀):** 음성 깨우기 감지기가 깨우기 단어를 들으면 `AppState.triggerVoiceEars(ttl: nil)`를 호출하여, 발화를 캡처하는 동안 `earBoostActive=true`를 유지합니다. 귀는 커지고(1.9배), 가독성을 위해 원형 귀 구멍이 생기며, 이후 1초간 무음이면 `stopVoiceEars()`를 통해 원래 상태로 돌아갑니다. 앱 내 음성 파이프라인에서만 실행됩니다.
- **작업 중(agent 실행 중):** `AppState.isWorking=true`는 “꼬리/다리 종종걸음” 미세 동작을 구동합니다. 작업이 진행 중인 동안 다리 흔들림이 빨라지고 약간의 위치 오프셋이 생깁니다. 현재는 WebChat agent 실행 전후로 전환되며, 다른 긴 작업에도 연결할 때 동일한 전환을 추가하세요.

연결 지점

- 음성 깨우기: 런타임/테스터가 트리거 시 `AppState.triggerVoiceEars(ttl: nil)`를 호출하고, 캡처 창과 일치하도록 1초 무음 후 `stopVoiceEars()`를 호출합니다.
- Agent 활동: 작업 구간 전후에 `AppStateStore.shared.setWorking(true/false)`를 설정합니다(WebChat agent 호출에는 이미 적용됨). 애니메이션이 멈춘 채 고정되지 않도록 구간은 짧게 유지하고 `defer` 블록에서 초기화하세요.

도형 및 크기

- 기본 아이콘은 `CritterIconRenderer.makeIcon(blink:legWiggle:earWiggle:earScale:earHoles:)`에서 그려집니다.
- 귀 크기 기본값은 `1.0`이며, 음성 부스트는 전체 프레임을 바꾸지 않고 `earScale=1.9`로 설정하고 `earHoles=true`를 전환합니다(18×18 pt 템플릿 이미지를 36×36 px Retina 백킹 스토어에 렌더링).
- 종종걸음은 작은 수평 흔들림과 함께 최대 약 `1.0`까지 다리 흔들림을 사용하며, 기존 유휴 흔들림에 추가됩니다.

동작 참고

- 귀/작업 중 상태를 위한 외부 CLI/broker 전환은 없습니다. 실수로 과도하게 흔들리는 것을 피하기 위해 앱 자체 신호 내부에만 유지하세요.
- 작업이 멈춰도 아이콘이 빠르게 기본 상태로 돌아오도록 TTL은 짧게 유지하세요(&lt;10초).
