---
read_when:
    - Android 노드를 페어링하거나 다시 연결하는 경우
    - Android gateway 검색 또는 인증을 디버깅하는 경우
    - 클라이언트 간 채팅 기록 동등성을 확인하는 경우
summary: 'Android 앱(노드): 연결 런북 + Connect/Chat/Voice/Canvas 명령 표면'
title: Android 앱
x-i18n:
    generated_at: "2026-04-05T12:48:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2223891afc3aa34af4aaf5410b4f1c6aebcf24bab68a6c47dd9832882d5260db
    source_path: platforms/android.md
    workflow: 15
---

# Android 앱 (노드)

> **참고:** Android 앱은 아직 공개 릴리스되지 않았습니다. 소스 코드는 `apps/android` 아래의 [OpenClaw repository](https://github.com/openclaw/openclaw)에서 사용할 수 있습니다. Java 17과 Android SDK를 사용해 직접 빌드할 수 있습니다(`./gradlew :app:assemblePlayDebug`). 빌드 지침은 [apps/android/README.md](https://github.com/openclaw/openclaw/blob/main/apps/android/README.md)를 참조하세요.

## 지원 개요

- 역할: 컴패니언 노드 앱(Android는 Gateway를 호스팅하지 않음)
- Gateway 필요 여부: 예(macOS, Linux 또는 WSL2를 통한 Windows에서 실행)
- 설치: [Getting Started](/ko/start/getting-started) + [Pairing](/channels/pairing)
- Gateway: [Runbook](/gateway) + [Configuration](/gateway/configuration)
  - 프로토콜: [Gateway protocol](/gateway/protocol) (노드 + 제어 평면)

## 시스템 제어

시스템 제어(`launchd`/`systemd`)는 Gateway 호스트에 있습니다. [Gateway](/gateway)를 참조하세요.

## 연결 런북

Android 노드 앱 ⇄ (mDNS/NSD + WebSocket) ⇄ **Gateway**

Android는 Gateway WebSocket에 직접 연결하며 디바이스 페어링(`role: node`)을 사용합니다.

Tailscale 또는 공용 호스트의 경우 Android는 보안 엔드포인트를 요구합니다.

- 권장: `https://<magicdns>` / `wss://<magicdns>`를 사용하는 Tailscale Serve / Funnel
- 지원됨: 실제 TLS 엔드포인트가 있는 다른 `wss://` Gateway URL
- 평문 `ws://`는 private LAN 주소 / `.local` 호스트와 `localhost`, `127.0.0.1`, Android 에뮬레이터 브리지(`10.0.2.2`)에서 계속 지원됩니다

### 사전 요구 사항

- “마스터” 머신에서 Gateway를 실행할 수 있어야 합니다.
- Android 디바이스/에뮬레이터가 gateway WebSocket에 도달할 수 있어야 합니다.
  - 같은 LAN에서 mDNS/NSD 사용, **또는**
  - Wide-Area Bonjour / 유니캐스트 DNS-SD를 사용하는 동일한 Tailscale tailnet 사용(아래 참조), **또는**
  - 수동 gateway host/port 입력(폴백)
- tailnet/public 모바일 페어링은 원시 tailnet IP `ws://` 엔드포인트를 사용하지 않습니다. 대신 Tailscale Serve 또는 다른 `wss://` URL을 사용하세요.
- gateway 머신에서 `CLI` (`openclaw`)를 실행할 수 있어야 합니다(또는 SSH를 통해).

### 1) Gateway 시작

```bash
openclaw gateway --port 18789 --verbose
```

로그에서 다음과 같은 메시지가 보이는지 확인하세요.

- `listening on ws://0.0.0.0:18789`

Tailscale을 통한 원격 Android 액세스에는 원시 tailnet bind 대신 Serve/Funnel을 권장합니다.

```bash
openclaw gateway --tailscale serve
```

이렇게 하면 Android에 보안 `wss://` / `https://` 엔드포인트가 제공됩니다. 일반적인 `gateway.bind: "tailnet"` 구성만으로는 TLS를 별도로 종료하지 않는 한 최초 원격 Android 페어링에 충분하지 않습니다.

### 2) 검색 확인(선택 사항)

gateway 머신에서:

```bash
dns-sd -B _openclaw-gw._tcp local.
```

추가 디버깅 참고: [Bonjour](/gateway/bonjour)

광역 검색 도메인도 구성했다면 다음과 비교하세요.

```bash
openclaw gateway discover --json
```

이 명령은 `local.`과 구성된 광역 도메인을 한 번에 보여 주며 TXT 전용 힌트 대신 해석된 서비스 엔드포인트를 사용합니다.

#### Tailnet (Vienna ⇄ London) 검색 via 유니캐스트 DNS-SD

Android NSD/mDNS 검색은 네트워크를 넘지 않습니다. Android 노드와 gateway가 서로 다른 네트워크에 있지만 Tailscale로 연결되어 있다면 Wide-Area Bonjour / 유니캐스트 DNS-SD를 대신 사용하세요.

검색만으로는 tailnet/public Android 페어링에 충분하지 않습니다. 검색된 경로는 여전히 보안 엔드포인트(`wss://` 또는 Tailscale Serve)가 필요합니다.

1. gateway 호스트에 DNS-SD 존(예: `openclaw.internal.`)을 설정하고 `_openclaw-gw._tcp` 레코드를 게시합니다.
2. 해당 DNS 서버를 가리키도록 선택한 도메인에 대해 Tailscale split DNS를 구성합니다.

자세한 내용과 CoreDNS 예시는 [Bonjour](/gateway/bonjour)를 참조하세요.

### 3) Android에서 연결

Android 앱에서:

- 앱은 **포그라운드 서비스**(지속 알림)를 통해 gateway 연결을 유지합니다.
- **Connect** 탭을 엽니다.
- **Setup Code** 또는 **Manual** 모드를 사용합니다.
- 검색이 차단되면 **Advanced controls**에서 수동 host/port를 사용하세요. private LAN 호스트에서는 `ws://`가 여전히 작동합니다. Tailscale/public 호스트에서는 TLS를 켜고 `wss://` / Tailscale Serve 엔드포인트를 사용하세요.

첫 번째 페어링에 성공하면 Android는 실행 시 자동으로 다시 연결합니다.

- 수동 엔드포인트(활성화된 경우), 그렇지 않으면
- 마지막으로 검색된 gateway(best-effort)

### 4) 페어링 승인 (CLI)

gateway 머신에서:

```bash
openclaw devices list
openclaw devices approve <requestId>
openclaw devices reject <requestId>
```

페어링 세부 정보: [Pairing](/channels/pairing)

### 5) 노드 연결 확인

- 노드 상태로 확인:

  ```bash
  openclaw nodes status
  ```

- Gateway를 통해 확인:

  ```bash
  openclaw gateway call node.list --params "{}"
  ```

### 6) 채팅 + 기록

Android Chat 탭은 세션 선택을 지원합니다(기본 `main`, 그리고 다른 기존 세션들).

- 기록: `chat.history` (표시용으로 정규화됨. 인라인 지시 태그는 표시 텍스트에서 제거되고, 일반 텍스트 tool-call XML payload(` <tool_call>...</tool_call>`, `<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>`, 잘린 tool-call 블록 포함)와 유출된 ASCII/전각 모델 제어 토큰이 제거되며, 정확히 `NO_REPLY` / `no_reply`인 순수 무음 토큰 assistant 행은 생략되고, 너무 큰 행은 플레이스홀더로 대체될 수 있음)
- 전송: `chat.send`
- 푸시 업데이트(best-effort): `chat.subscribe` → `event:"chat"`

### 7) Canvas + camera

#### Gateway Canvas Host (웹 콘텐츠에 권장)

에이전트가 디스크에서 편집할 수 있는 실제 HTML/CSS/JS를 노드에 표시하려면 노드가 Gateway canvas host를 가리키도록 설정하세요.

참고: 노드는 Gateway HTTP 서버(기본 `gateway.port`, 기본값 `18789`와 동일한 포트)에서 canvas를 로드합니다.

1. gateway 호스트에 `~/.openclaw/workspace/canvas/index.html`을 만듭니다.

2. 노드를 해당 위치로 이동시킵니다(LAN):

```bash
openclaw nodes invoke --node "<Android Node>" --command canvas.navigate --params '{"url":"http://<gateway-hostname>.local:18789/__openclaw__/canvas/"}'
```

Tailnet(선택 사항): 두 디바이스가 모두 Tailscale에 있으면 `.local` 대신 MagicDNS 이름 또는 tailnet IP를 사용하세요. 예: `http://<gateway-magicdns>:18789/__openclaw__/canvas/`

이 서버는 HTML에 live-reload 클라이언트를 주입하고 파일 변경 시 다시 로드합니다.
A2UI 호스트는 `http://<gateway-host>:18789/__openclaw__/a2ui/`에 있습니다.

Canvas 명령(포그라운드 전용):

- `canvas.eval`, `canvas.snapshot`, `canvas.navigate` (기본 scaffold로 돌아가려면 `{"url":""}` 또는 `{"url":"/"}` 사용). `canvas.snapshot`은 `{ format, base64 }`를 반환합니다(기본 `format="jpeg"`).
- A2UI: `canvas.a2ui.push`, `canvas.a2ui.reset` (`canvas.a2ui.pushJSONL` 레거시 별칭)

Camera 명령(포그라운드 전용, 권한 제어됨):

- `camera.snap` (jpg)
- `camera.clip` (mp4)

파라미터와 CLI 도우미는 [Camera node](/nodes/camera)를 참조하세요.

### 8) Voice + 확장된 Android 명령 표면

- Voice: Android는 Voice 탭에서 transcript 캡처와 `talk.speak` 재생을 포함한 단일 mic on/off 흐름을 사용합니다. `talk.speak`를 사용할 수 없을 때만 로컬 시스템 TTS를 사용합니다. 앱이 포그라운드를 벗어나면 Voice는 중지됩니다.
- Voice wake/talk-mode 토글은 현재 Android UX/런타임에서 제거되었습니다.
- 추가 Android 명령 패밀리(사용 가능 여부는 디바이스 + 권한에 따라 다름):
  - `device.status`, `device.info`, `device.permissions`, `device.health`
  - `notifications.list`, `notifications.actions` (아래 [알림 전달](#알림-전달) 참조)
  - `photos.latest`
  - `contacts.search`, `contacts.add`
  - `calendar.events`, `calendar.add`
  - `callLog.search`
  - `sms.search`
  - `motion.activity`, `motion.pedometer`

## Assistant 진입점

Android는 시스템 assistant 트리거(Google Assistant)를 통해 OpenClaw를 실행하는 것을 지원합니다. 구성된 경우 홈 버튼을 길게 누르거나 "Hey Google, ask OpenClaw..."라고 말하면 앱이 열리고 프롬프트가 채팅 작성기에 전달됩니다.

이는 앱 매니페스트에 선언된 Android **App Actions** 메타데이터를 사용합니다. gateway 쪽에서 추가 구성이 필요하지 않습니다. assistant intent는 전적으로 Android 앱에서 처리되어 일반 채팅 메시지로 전달됩니다.

<Note>
App Actions의 사용 가능 여부는 디바이스, Google Play Services 버전, 사용자가 OpenClaw를 기본 assistant 앱으로 설정했는지 여부에 따라 달라집니다.
</Note>

## 알림 전달

Android는 디바이스 알림을 이벤트로 gateway에 전달할 수 있습니다. 여러 제어 항목을 사용해 어떤 알림을 언제 전달할지 범위를 지정할 수 있습니다.

| 키 | 타입 | 설명 |
| -------------------------------- | -------------- | ------------------------------------------------------------------------------------------------- |
| `notifications.allowPackages` | string[] | 이러한 패키지 이름의 알림만 전달합니다. 설정되면 다른 모든 패키지는 무시됩니다. |
| `notifications.denyPackages` | string[] | 이러한 패키지 이름의 알림은 절대 전달하지 않습니다. `allowPackages` 이후에 적용됩니다. |
| `notifications.quietHours.start` | string (HH:mm) | quiet hours 창의 시작 시간(로컬 디바이스 시간). 이 시간 동안 알림은 억제됩니다. |
| `notifications.quietHours.end` | string (HH:mm) | quiet hours 창의 종료 시간 |
| `notifications.rateLimit` | number | 패키지별 분당 최대 전달 알림 수. 초과 알림은 삭제됩니다. |

알림 picker도 전달된 알림 이벤트에 대해 더 안전한 동작을 사용하여 민감한 시스템 알림이 실수로 전달되는 일을 방지합니다.

예시 구성:

```json5
{
  notifications: {
    allowPackages: ["com.slack", "com.whatsapp"],
    denyPackages: ["com.android.systemui"],
    quietHours: {
      start: "22:00",
      end: "07:00",
    },
    rateLimit: 5,
  },
}
```

<Note>
알림 전달에는 Android Notification Listener 권한이 필요합니다. 앱은 설정 중 이 권한을 요청합니다.
</Note>
