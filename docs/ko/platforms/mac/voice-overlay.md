---
read_when:
    - voice overlay 동작을 조정하는 경우
summary: wake-word와 push-to-talk가 겹칠 때의 voice overlay 수명 주기
title: Voice Overlay
x-i18n:
    generated_at: "2026-04-05T12:49:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1efcc26ec05d2f421cb2cf462077d002381995b338d00db77d5fdba9b8d938b6
    source_path: platforms/mac/voice-overlay.md
    workflow: 15
---

# Voice Overlay 수명 주기 (macOS)

대상: macOS 앱 기여자. 목표: wake-word와 push-to-talk가 겹칠 때 voice overlay 동작을 예측 가능하게 유지하는 것.

## 현재 의도

- wake-word로 overlay가 이미 표시된 상태에서 사용자가 핫키를 누르면, 핫키 세션은 텍스트를 초기화하지 않고 기존 텍스트를 _채택_합니다. 핫키를 누르고 있는 동안 overlay는 계속 표시됩니다. 사용자가 손을 떼면: 다듬은 텍스트가 있으면 전송하고, 없으면 닫습니다.
- wake-word만 사용할 때는 무음 시 자동 전송이 계속되고, push-to-talk는 손을 떼는 즉시 전송됩니다.

## 구현됨 (2025년 12월 9일)

- Overlay 세션은 이제 캡처(wake-word 또는 push-to-talk)마다 토큰을 가집니다. 토큰이 일치하지 않으면 partial/final/send/dismiss/level 업데이트를 버려 오래된 콜백을 방지합니다.
- Push-to-talk는 표시 중인 overlay 텍스트를 접두사로 채택합니다(즉, wake overlay가 올라와 있는 동안 핫키를 누르면 기존 텍스트를 유지한 채 새 음성을 이어붙입니다). 현재 텍스트로 폴백하기 전에 최종 transcript를 최대 1.5초까지 기다립니다.
- Chime/overlay 로깅은 `voicewake.overlay`, `voicewake.ptt`, `voicewake.chime` 카테고리에서 `info` 수준으로 출력됩니다(세션 시작, partial, final, send, dismiss, chime 사유).

## 다음 단계

1. **VoiceSessionCoordinator (actor)**
   - 한 번에 정확히 하나의 `VoiceSession`만 소유
   - API (토큰 기반): `beginWakeCapture`, `beginPushToTalk`, `updatePartial`, `endCapture`, `cancel`, `applyCooldown`
   - 오래된 토큰을 가진 콜백은 버림(오래된 recognizer가 overlay를 다시 여는 것 방지)
2. **VoiceSession (모델)**
   - 필드: `token`, `source` (`wakeWord|pushToTalk`), committed/volatile text, chime 플래그, 타이머(auto-send, idle), `overlayMode` (`display|editing|sending`), cooldown deadline
3. **Overlay 바인딩**
   - `VoiceSessionPublisher` (`ObservableObject`)가 활성 세션을 SwiftUI에 미러링
   - `VoiceWakeOverlayView`는 publisher를 통해서만 렌더링되며, 전역 singleton을 직접 변경하지 않음
   - Overlay 사용자 작업(`sendNow`, `dismiss`, `edit`)은 세션 토큰과 함께 coordinator로 콜백
4. **통합 전송 경로**
   - `endCapture` 시: 다듬은 텍스트가 비어 있으면 닫기, 아니면 `performSend(session:)` (send chime을 한 번 재생하고 전달한 뒤 닫기)
   - Push-to-talk: 지연 없음, wake-word: auto-send를 위한 선택적 지연
   - Push-to-talk가 끝난 뒤 짧은 cooldown을 wake 런타임에 적용해 wake-word가 즉시 다시 트리거되지 않도록 함
5. **로깅**
   - Coordinator는 subsystem `ai.openclaw`, categories `voicewake.overlay` 및 `voicewake.chime`에서 `.info` 로그를 출력
   - 핵심 이벤트: `session_started`, `adopted_by_push_to_talk`, `partial`, `finalized`, `send`, `dismiss`, `cancel`, `cooldown`

## 디버깅 체크리스트

- 고정된 overlay를 재현하면서 로그를 스트리밍:

  ```bash
  sudo log stream --predicate 'subsystem == "ai.openclaw" AND category CONTAINS "voicewake"' --level info --style compact
  ```

- 활성 세션 토큰이 하나뿐인지 확인하세요. 오래된 콜백은 coordinator가 버려야 합니다.
- push-to-talk release가 항상 활성 토큰과 함께 `endCapture`를 호출하는지 확인하세요. 텍스트가 비어 있으면 chime이나 send 없이 `dismiss`가 예상됩니다.

## 마이그레이션 단계(권장)

1. `VoiceSessionCoordinator`, `VoiceSession`, `VoiceSessionPublisher` 추가
2. `VoiceWakeRuntime`이 `VoiceWakeOverlayController`를 직접 건드리지 않고 세션을 생성/업데이트/종료하도록 리팩터링
3. `VoicePushToTalk`이 기존 세션을 채택하고 release 시 `endCapture`를 호출하도록 리팩터링. 런타임 cooldown 적용
4. `VoiceWakeOverlayController`를 publisher에 연결하고 runtime/PTT에서의 직접 호출 제거
5. 세션 채택, cooldown, 빈 텍스트 dismiss에 대한 통합 테스트 추가
