---
read_when:
    - voice wake 또는 PTT 경로 작업을 할 때
summary: mac 앱의 Voice wake 및 push-to-talk 모드와 라우팅 세부 사항
title: Voice Wake (macOS)
x-i18n:
    generated_at: "2026-04-05T12:49:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: fed6524a2e1fad5373d34821c920b955a2b5a3fcd9c51cdb97cf4050536602a7
    source_path: platforms/mac/voicewake.md
    workflow: 15
---

# Voice Wake & Push-to-Talk

## 모드

- **Wake-word mode**(기본값): 항상 켜져 있는 Speech 인식기가 트리거 토큰(`swabbleTriggerWords`)을 기다립니다. 일치하면 캡처를 시작하고, 부분 텍스트와 함께 오버레이를 표시하며, 무음 후 자동 전송합니다.
- **Push-to-talk(오른쪽 Option 길게 누르기)**: 오른쪽 Option 키를 길게 눌러 즉시 캡처합니다. 트리거가 필요 없습니다. 누르고 있는 동안 오버레이가 표시되며, 키를 놓으면 짧은 지연 후 텍스트를 조정할 수 있도록 마무리되어 전달됩니다.

## 런타임 동작(wake-word)

- Speech 인식기는 `VoiceWakeRuntime`에 있습니다.
- 트리거는 wake word와 다음 단어 사이에 **의미 있는 멈춤**이 있을 때만 발동합니다(약 0.55초 간격). 오버레이/차임은 명령이 시작되기 전이라도 그 멈춤에서 시작될 수 있습니다.
- 무음 구간: 음성이 이어질 때는 2.0초, 트리거만 들린 경우는 5.0초.
- 하드 스톱: runaway 세션 방지를 위해 120초.
- 세션 간 디바운스: 350ms.
- 오버레이는 `VoiceWakeOverlayController`를 통해 committed/volatile 색상으로 구동됩니다.
- 전송 후 인식기는 다음 트리거를 듣기 위해 깔끔하게 재시작됩니다.

## 수명 주기 불변 조건

- Voice Wake가 활성화되어 있고 권한이 부여되어 있으면 wake-word 인식기는 항상 듣고 있어야 합니다(명시적인 push-to-talk 캡처 중 제외).
- 오버레이 가시성(X 버튼으로 수동 닫기 포함)은 인식기 재개를 절대 막아서는 안 됩니다.

## 오버레이가 고착되는 실패 모드(이전)

이전에는 오버레이가 계속 표시된 채로 멈춘 상태에서 수동으로 닫으면, 런타임의 재시작 시도가 오버레이 가시성 때문에 막히고 후속 재시작도 예약되지 않아 Voice Wake가 “죽은 것처럼” 보일 수 있었습니다.

강화 내용:

- 이제 wake runtime 재시작은 오버레이 가시성에 의해 차단되지 않습니다.
- 오버레이 닫기 완료 시 `VoiceSessionCoordinator`를 통해 `VoiceWakeRuntime.refresh(...)`가 트리거되므로, X 버튼으로 수동 닫아도 항상 다시 듣기를 재개합니다.

## Push-to-talk 세부 사항

- 핫키 감지는 **오른쪽 Option**(`keyCode 61` + `.option`)에 대해 전역 `.flagsChanged` 모니터를 사용합니다. 이벤트는 관찰만 하며 소비하지 않습니다.
- 캡처 파이프라인은 `VoicePushToTalk`에 있습니다. 즉시 Speech를 시작하고, 부분 결과를 오버레이로 스트리밍하며, 키를 놓으면 `VoiceWakeForwarder`를 호출합니다.
- push-to-talk가 시작되면 오디오 탭 충돌을 피하기 위해 wake-word 런타임을 일시 중지하며, 키를 놓으면 자동으로 다시 시작됩니다.
- 권한: Microphone + Speech가 필요합니다. 이벤트를 보려면 Accessibility/Input Monitoring 승인이 필요합니다.
- 외장 키보드: 일부는 오른쪽 Option을 예상대로 노출하지 않을 수 있으므로, 사용자가 누락을 보고하면 대체 단축키를 제공하세요.

## 사용자 대상 설정

- **Voice Wake** 토글: wake-word 런타임을 활성화합니다.
- **Hold Cmd+Fn to talk**: push-to-talk 모니터를 활성화합니다. macOS < 26에서는 비활성화됩니다.
- 언어 및 마이크 선택기, 실시간 레벨 미터, 트리거 단어 테이블, 테스터(로컬 전용, 전달 안 함).
- 마이크 선택기는 장치가 연결 해제되어도 마지막 선택을 유지하고, 연결 해제 힌트를 표시하며, 장치가 돌아올 때까지 일시적으로 시스템 기본값으로 대체합니다.
- **Sounds**: 트리거 감지 시와 전송 시 차임을 재생하며, 기본값은 macOS “Glass” 시스템 사운드입니다. 각 이벤트에 대해 `NSSound`로 로드 가능한 파일(예: MP3/WAV/AIFF)을 선택하거나 **No Sound**를 선택할 수 있습니다.

## 전달 동작

- Voice Wake가 활성화되면 전사본은 활성 게이트웨이/에이전트로 전달됩니다(mac 앱의 나머지 부분과 동일한 로컬/원격 모드 사용).
- 답장은 **마지막으로 사용한 main provider**(WhatsApp/Telegram/Discord/WebChat)로 전달됩니다. 전달이 실패하면 오류가 로그에 기록되며, 실행은 여전히 WebChat/세션 로그를 통해 확인할 수 있습니다.

## 전달 페이로드

- `VoiceWakeForwarder.prefixedTranscript(_:)`는 전송 전에 머신 힌트를 앞에 붙입니다. wake-word와 push-to-talk 경로에서 공유됩니다.

## 빠른 검증

- push-to-talk를 켜고 Cmd+Fn을 길게 누른 상태에서 말한 뒤 놓습니다. 오버레이에 부분 결과가 표시된 다음 전송되어야 합니다.
- 누르고 있는 동안 메뉴 막대 귀 아이콘은 확대된 상태를 유지해야 합니다(`triggerVoiceEars(ttl:nil)` 사용). 놓은 뒤에는 원래대로 돌아갑니다.
