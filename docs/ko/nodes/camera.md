---
read_when:
    - iOS/Android 노드 또는 macOS에서 카메라 캡처를 추가하거나 수정하는 경우
    - 에이전트가 접근 가능한 MEDIA 임시 파일 워크플로를 확장하는 경우
summary: '에이전트 사용을 위한 카메라 캡처(iOS/Android 노드 + macOS 앱): 사진(jpg) 및 짧은 비디오 클립(mp4)'
title: 카메라 캡처
x-i18n:
    generated_at: "2026-04-05T12:47:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 30b1beaac9602ff29733f72b953065f271928743c8fff03191a007e8b965c88d
    source_path: nodes/camera.md
    workflow: 15
---

# 카메라 캡처(에이전트)

OpenClaw는 에이전트 워크플로를 위한 **카메라 캡처**를 지원합니다.

- **iOS node** (Gateway를 통해 페어링): `node.invoke`를 통해 **사진**(`jpg`) 또는 **짧은 비디오 클립**(`mp4`, 선택적 오디오 포함)을 캡처합니다.
- **Android node** (Gateway를 통해 페어링): `node.invoke`를 통해 **사진**(`jpg`) 또는 **짧은 비디오 클립**(`mp4`, 선택적 오디오 포함)을 캡처합니다.
- **macOS app** (Gateway를 통한 node): `node.invoke`를 통해 **사진**(`jpg`) 또는 **짧은 비디오 클립**(`mp4`, 선택적 오디오 포함)을 캡처합니다.

모든 카메라 액세스는 **사용자 제어 설정** 뒤에 게이트됩니다.

## iOS node

### 사용자 설정(기본값 켜짐)

- iOS Settings 탭 → **Camera** → **Allow Camera** (`camera.enabled`)
  - 기본값: **켜짐**(키가 없으면 활성화된 것으로 처리됨).
  - 꺼져 있을 때: `camera.*` 명령은 `CAMERA_DISABLED`를 반환합니다.

### 명령(Gateway `node.invoke`를 통해)

- `camera.list`
  - 응답 payload:
    - `devices`: `{ id, name, position, deviceType }` 배열

- `camera.snap`
  - Params:
    - `facing`: `front|back` (기본값: `front`)
    - `maxWidth`: number (선택 사항, iOS node에서 기본값 `1600`)
    - `quality`: `0..1` (선택 사항, 기본값 `0.9`)
    - `format`: 현재는 `jpg`
    - `delayMs`: number (선택 사항, 기본값 `0`)
    - `deviceId`: string (선택 사항, `camera.list`에서 가져옴)
  - 응답 payload:
    - `format: "jpg"`
    - `base64: "<...>"`
    - `width`, `height`
  - Payload 가드: 사진은 base64 payload를 5 MB 이하로 유지하기 위해 다시 압축됩니다.

- `camera.clip`
  - Params:
    - `facing`: `front|back` (기본값: `front`)
    - `durationMs`: number (기본값 `3000`, 최대 `60000`으로 제한됨)
    - `includeAudio`: boolean (기본값 `true`)
    - `format`: 현재는 `mp4`
    - `deviceId`: string (선택 사항, `camera.list`에서 가져옴)
  - 응답 payload:
    - `format: "mp4"`
    - `base64: "<...>"`
    - `durationMs`
    - `hasAudio`

### 포그라운드 요구 사항

`canvas.*`와 마찬가지로 iOS node는 **포그라운드**에서만 `camera.*` 명령을 허용합니다. 백그라운드 호출은 `NODE_BACKGROUND_UNAVAILABLE`을 반환합니다.

### CLI 도우미(임시 파일 + MEDIA)

첨부파일을 얻는 가장 쉬운 방법은 CLI 도우미를 사용하는 것으로, 디코딩된 미디어를 임시 파일에 기록하고 `MEDIA:<path>`를 출력합니다.

예시:

```bash
openclaw nodes camera snap --node <id>               # 기본값: front + back 모두 (MEDIA 줄 2개)
openclaw nodes camera snap --node <id> --facing front
openclaw nodes camera clip --node <id> --duration 3000
openclaw nodes camera clip --node <id> --no-audio
```

참고:

- `nodes camera snap`의 기본값은 에이전트에 양쪽 시야를 모두 제공하기 위해 **양쪽 방향 모두**입니다.
- 출력 파일은 자체 wrapper를 만들지 않는 한 임시 파일입니다(OS 임시 디렉터리에 생성됨).

## Android node

### Android 사용자 설정(기본값 켜짐)

- Android Settings 시트 → **Camera** → **Allow Camera** (`camera.enabled`)
  - 기본값: **켜짐**(키가 없으면 활성화된 것으로 처리됨).
  - 꺼져 있을 때: `camera.*` 명령은 `CAMERA_DISABLED`를 반환합니다.

### 권한

- Android는 런타임 권한이 필요합니다.
  - `camera.snap` 및 `camera.clip` 모두에 대해 `CAMERA`.
  - `includeAudio=true`인 `camera.clip`에 대해 `RECORD_AUDIO`.

권한이 없으면 앱은 가능한 경우 프롬프트를 표시합니다. 거부되면 `camera.*` 요청은
`*_PERMISSION_REQUIRED` 오류로 실패합니다.

### Android 포그라운드 요구 사항

`canvas.*`와 마찬가지로 Android node는 **포그라운드**에서만 `camera.*` 명령을 허용합니다. 백그라운드 호출은 `NODE_BACKGROUND_UNAVAILABLE`을 반환합니다.

### Android 명령(Gateway `node.invoke`를 통해)

- `camera.list`
  - 응답 payload:
    - `devices`: `{ id, name, position, deviceType }` 배열

### Payload 가드

사진은 base64 payload를 5 MB 이하로 유지하기 위해 다시 압축됩니다.

## macOS app

### 사용자 설정(기본값 꺼짐)

macOS 컴패니언 앱은 체크박스를 제공합니다.

- **Settings → General → Allow Camera** (`openclaw.cameraEnabled`)
  - 기본값: **꺼짐**
  - 꺼져 있을 때: 카메라 요청은 “사용자가 카메라를 비활성화함”을 반환합니다.

### CLI 도우미(node invoke)

macOS node에서 카메라 명령을 호출하려면 메인 `openclaw` CLI를 사용하세요.

예시:

```bash
openclaw nodes camera list --node <id>            # 카메라 id 목록
openclaw nodes camera snap --node <id>            # MEDIA:<path> 출력
openclaw nodes camera snap --node <id> --max-width 1280
openclaw nodes camera snap --node <id> --delay-ms 2000
openclaw nodes camera snap --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --duration 10s          # MEDIA:<path> 출력
openclaw nodes camera clip --node <id> --duration-ms 3000      # MEDIA:<path> 출력(레거시 플래그)
openclaw nodes camera clip --node <id> --device-id <id>
openclaw nodes camera clip --node <id> --no-audio
```

참고:

- `openclaw nodes camera snap`의 기본값은 재정의하지 않는 한 `maxWidth=1600`입니다.
- macOS에서 `camera.snap`은 캡처 전에 워밍업/노출 안정화 후 `delayMs`(기본값 2000ms)를 기다립니다.
- 사진 payload는 base64를 5 MB 이하로 유지하기 위해 다시 압축됩니다.

## 안전 + 실용적 제한

- 카메라와 마이크 액세스는 일반적인 OS 권한 프롬프트를 트리거하며(Info.plist의 usage 문자열도 필요함).
- 비디오 클립은 과도한 node payload(base64 오버헤드 + 메시지 제한)를 피하기 위해 제한됩니다(현재 `<= 60s`).

## macOS 화면 비디오(OS 수준)

_화면_ 비디오(카메라 아님)의 경우 macOS 컴패니언을 사용하세요.

```bash
openclaw nodes screen record --node <id> --duration 10s --fps 15   # MEDIA:<path> 출력
```

참고:

- macOS **Screen Recording** 권한(TCC)이 필요합니다.
