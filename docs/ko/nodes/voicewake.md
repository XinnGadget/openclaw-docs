---
read_when:
    - 음성 웨이크 워드 동작 또는 기본값을 변경하는 경우
    - 웨이크 워드 동기화가 필요한 새 노드 플랫폼을 추가하는 경우
summary: 전역 음성 웨이크 워드(Gateway 소유)와 노드 간 동기화 방식
title: Voice Wake
x-i18n:
    generated_at: "2026-04-05T12:47:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: a80e0cf7f68a3d48ff79af0ffb3058a7a0ecebd2cdbaad20b9ff53bc2b39dc84
    source_path: nodes/voicewake.md
    workflow: 15
---

# Voice Wake (전역 웨이크 워드)

OpenClaw는 **웨이크 워드**를 **Gateway**가 소유하는 단일 전역 목록으로 취급합니다.

- **노드별 사용자 지정 웨이크 워드는 없습니다**.
- **어떤 노드/앱 UI에서도** 목록을 편집할 수 있으며, 변경 사항은 Gateway에 의해 저장되고 모두에게 브로드캐스트됩니다.
- macOS와 iOS는 로컬 **Voice Wake 활성화/비활성화** 토글을 유지합니다(로컬 UX와 권한이 다름).
- Android는 현재 Voice Wake를 꺼 둔 상태이며 Voice 탭에서 수동 마이크 흐름을 사용합니다.

## 저장소(Gateway 호스트)

웨이크 워드는 게이트웨이 머신의 다음 위치에 저장됩니다.

- `~/.openclaw/settings/voicewake.json`

형식:

```json
{ "triggers": ["openclaw", "claude", "computer"], "updatedAtMs": 1730000000000 }
```

## 프로토콜

### 메서드

- `voicewake.get` → `{ triggers: string[] }`
- `voicewake.set` (params `{ triggers: string[] }`) → `{ triggers: string[] }`

참고:

- 트리거는 정규화됩니다(앞뒤 공백 제거, 빈 값 삭제). 빈 목록은 기본값으로 대체됩니다.
- 안전을 위해 제한이 적용됩니다(개수/길이 상한).

### 이벤트

- `voicewake.changed` payload `{ triggers: string[] }`

수신 대상:

- 모든 WebSocket 클라이언트(macOS 앱, WebChat 등)
- 연결된 모든 노드(iOS/Android), 그리고 노드 연결 시 초기 “현재 상태” 푸시로도 전달됨

## 클라이언트 동작

### macOS 앱

- 전역 목록을 사용해 `VoiceWakeRuntime` 트리거를 게이트합니다.
- Voice Wake 설정에서 “Trigger words”를 편집하면 `voicewake.set`을 호출한 다음, 다른 클라이언트와의 동기화를 위해 브로드캐스트에 의존합니다.

### iOS node

- 전역 목록을 `VoiceWakeManager` 트리거 감지에 사용합니다.
- Settings에서 Wake Words를 편집하면(`Gateway WS`를 통해) `voicewake.set`을 호출하고, 로컬 웨이크 워드 감지도 계속 반응하도록 유지합니다.

### Android node

- Voice Wake는 현재 Android 런타임/Settings에서 비활성화되어 있습니다.
- Android 음성은 웨이크 워드 트리거 대신 Voice 탭에서 수동 마이크 캡처를 사용합니다.
