---
read_when:
    - OpenClaw.app을 패키징할 때
    - macOS gateway launchd 서비스를 디버깅할 때
    - macOS용 gateway CLI를 설치할 때
summary: macOS에서의 Gateway 런타임(외부 launchd 서비스)
title: macOS에서의 Gateway
x-i18n:
    generated_at: "2026-04-05T12:48:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 69e41528b35d69c13608cb9a34b39a7f02e1134204d1b496cbdd191798f39607
    source_path: platforms/mac/bundled-gateway.md
    workflow: 15
---

# macOS에서의 Gateway (외부 launchd)

OpenClaw.app은 더 이상 Node/Bun이나 Gateway 런타임을 번들로 포함하지 않습니다. macOS 앱은 **외부** `openclaw` CLI 설치를 기대하며, Gateway를 자식 프로세스로 시작하지 않고, Gateway를 계속 실행하기 위해 사용자별 launchd 서비스를 관리합니다(또는 이미 실행 중인 로컬 Gateway가 있으면 그것에 연결합니다).

## CLI 설치(로컬 모드에 필수)

Node 24가 Mac의 기본 런타임입니다. 호환성을 위해 Node 22 LTS(현재 `22.14+`)도 계속 동작합니다. 그런 다음 `openclaw`를 전역으로 설치하세요:

```bash
npm install -g openclaw@<version>
```

macOS 앱의 **Install CLI** 버튼은 앱이 내부적으로 사용하는 것과 동일한 전역 설치 흐름을 실행합니다. npm을 먼저 선호하고, 그다음 pnpm, 마지막으로 감지된 패키지 관리자가 그것뿐일 때 bun을 사용합니다. Node는 여전히 권장되는 Gateway 런타임입니다.

## Launchd (LaunchAgent로서의 Gateway)

라벨:

- `ai.openclaw.gateway` (또는 `ai.openclaw.<profile>`; 레거시 `com.openclaw.*`가 남아 있을 수 있음)

Plist 위치(사용자별):

- `~/Library/LaunchAgents/ai.openclaw.gateway.plist`
  (또는 `~/Library/LaunchAgents/ai.openclaw.<profile>.plist`)

관리자:

- macOS 앱은 로컬 모드에서 LaunchAgent 설치/업데이트를 소유합니다.
- CLI로도 설치할 수 있습니다: `openclaw gateway install`.

동작:

- “OpenClaw Active”는 LaunchAgent를 활성화/비활성화합니다.
- 앱을 종료해도 gateway는 중지되지 않습니다(launchd가 계속 유지함).
- 구성된 포트에서 Gateway가 이미 실행 중이면, 앱은 새로 시작하는 대신
  그것에 연결합니다.

로깅:

- launchd stdout/err: `/tmp/openclaw/openclaw-gateway.log`

## 버전 호환성

macOS 앱은 gateway 버전을 자신의 버전과 비교해 확인합니다. 서로
호환되지 않으면 앱 버전에 맞게 전역 CLI를 업데이트하세요.

## 스모크 체크

```bash
openclaw --version

OPENCLAW_SKIP_CHANNELS=1 \
OPENCLAW_SKIP_CANVAS_HOST=1 \
openclaw gateway --port 18999 --bind loopback
```

그런 다음:

```bash
openclaw gateway call health --url ws://127.0.0.1:18999 --timeout 3000
```
