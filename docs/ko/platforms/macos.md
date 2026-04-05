---
read_when:
    - macOS 앱 기능을 구현하는 경우
    - macOS에서 gateway 수명 주기 또는 node 브리징을 변경하는 경우
summary: OpenClaw macOS 컴패니언 앱(메뉴 막대 + gateway broker)
title: macOS 앱
x-i18n:
    generated_at: "2026-04-05T12:49:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: bfac937e352ede495f60af47edf3b8e5caa5b692ba0ea01d9fb0de9a44bbc135
    source_path: platforms/macos.md
    workflow: 15
---

# OpenClaw macOS 컴패니언(메뉴 막대 + gateway broker)

macOS 앱은 OpenClaw의 **메뉴 막대 컴패니언**입니다. 권한을 소유하고,
로컬에서 Gateway를 관리/연결하며(launchd 또는 수동), macOS
기능을 node로서 에이전트에 노출합니다.

## 수행 기능

- 메뉴 막대에 네이티브 알림과 상태를 표시합니다.
- TCC 프롬프트(Notifications, Accessibility, Screen Recording, Microphone,
  Speech Recognition, Automation/AppleScript)를 소유합니다.
- Gateway를 실행하거나 연결합니다(로컬 또는 원격).
- macOS 전용 도구(Canvas, Camera, Screen Recording, `system.run`)를 노출합니다.
- **remote** 모드에서는 로컬 node host 서비스를 시작하고(launchd), **local** 모드에서는 중지합니다.
- 선택적으로 UI 자동화를 위한 **PeekabooBridge**를 호스팅합니다.
- npm, pnpm 또는 bun을 통해 요청 시 전역 CLI(`openclaw`)를 설치합니다(앱은 npm, 그다음 pnpm, 그다음 bun을 선호하며, Node는 여전히 권장 Gateway 런타임입니다).

## 로컬 vs 원격 모드

- **Local**(기본값): 앱은 실행 중인 로컬 Gateway가 있으면 여기에 연결하고,
  없으면 `openclaw gateway install`을 통해 launchd 서비스를 활성화합니다.
- **Remote**: 앱은 SSH/Tailscale을 통해 Gateway에 연결하며 로컬 프로세스를
  절대 시작하지 않습니다.
  앱은 원격 Gateway가 이 Mac에 도달할 수 있도록 로컬 **node host service**를 시작합니다.
  앱은 Gateway를 자식 프로세스로 생성하지 않습니다.
  이제 Gateway discovery는 원시 tailnet IP보다 Tailscale MagicDNS 이름을 우선 사용하므로,
  tailnet IP가 변경될 때 Mac 앱이 더 안정적으로 복구됩니다.

## Launchd 제어

앱은 `ai.openclaw.gateway`라는 사용자별 LaunchAgent를 관리합니다
(`--profile`/`OPENCLAW_PROFILE`을 사용할 때는 `ai.openclaw.<profile>`, 레거시 `com.openclaw.*`도 여전히 unload됨).

```bash
launchctl kickstart -k gui/$UID/ai.openclaw.gateway
launchctl bootout gui/$UID/ai.openclaw.gateway
```

이름이 있는 profile을 실행하는 경우 label을 `ai.openclaw.<profile>`로 바꾸세요.

LaunchAgent가 설치되지 않았다면 앱에서 활성화하거나
`openclaw gateway install`을 실행하세요.

## Node 기능(mac)

macOS 앱은 자신을 node로 표시합니다. 일반적인 명령:

- Canvas: `canvas.present`, `canvas.navigate`, `canvas.eval`, `canvas.snapshot`, `canvas.a2ui.*`
- Camera: `camera.snap`, `camera.clip`
- Screen: `screen.record`
- System: `system.run`, `system.notify`

Node는 `permissions` 맵을 보고하므로 에이전트가 무엇이 허용되는지 판단할 수 있습니다.

Node 서비스 + 앱 IPC:

- 헤드리스 node host 서비스가 실행 중이면(remote 모드), Gateway WS에 node로 연결합니다.
- `system.run`은 로컬 Unix socket을 통해 macOS 앱(UI/TCC 컨텍스트)에서 실행되며, 프롬프트 + 출력은 앱 내부에 머뭅니다.

다이어그램 (SCI):

```
Gateway -> Node Service (WS)
                 |  IPC (UDS + token + HMAC + TTL)
                 v
             Mac App (UI + TCC + system.run)
```

## Exec 승인 (`system.run`)

`system.run`은 macOS 앱의 **Exec approvals**(Settings → Exec approvals)로 제어됩니다.
보안 + ask + allowlist는 Mac 로컬에 다음 위치로 저장됩니다.

```
~/.openclaw/exec-approvals.json
```

예시:

```json
{
  "version": 1,
  "defaults": {
    "security": "deny",
    "ask": "on-miss"
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "allowlist": [{ "pattern": "/opt/homebrew/bin/rg" }]
    }
  }
}
```

참고:

- `allowlist` 항목은 해석된 바이너리 경로에 대한 glob 패턴입니다.
- 셸 제어 또는 확장 구문(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`)을 포함한 원시 셸 명령 텍스트는 allowlist 미스로 처리되며 명시적 승인(또는 셸 바이너리를 allowlist에 추가)이 필요합니다.
- 프롬프트에서 “Always Allow”를 선택하면 해당 명령이 allowlist에 추가됩니다.
- `system.run` 환경 재정의는 필터링됩니다(`PATH`, `DYLD_*`, `LD_*`, `NODE_OPTIONS`, `PYTHON*`, `PERL*`, `RUBYOPT`, `SHELLOPTS`, `PS4` 제거) 그런 다음 앱의 환경과 병합됩니다.
- 셸 래퍼(`bash|sh|zsh ... -c/-lc`)의 경우, 요청 범위 환경 재정의는 작은 명시적 허용 목록(`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`)으로 축소됩니다.
- allowlist 모드에서 항상 허용 결정이 내려지면 알려진 디스패치 래퍼(`env`, `nice`, `nohup`, `stdbuf`, `timeout`)는 래퍼 경로가 아니라 내부 실행 파일 경로를 저장합니다. 안전하게 언래핑할 수 없으면 allowlist 항목은 자동 저장되지 않습니다.

## 딥 링크

앱은 로컬 작업을 위해 `openclaw://` URL 스킴을 등록합니다.

### `openclaw://agent`

Gateway `agent` 요청을 트리거합니다.
__OC_I18N_900004__
쿼리 매개변수:

- `message` (필수)
- `sessionKey` (선택 사항)
- `thinking` (선택 사항)
- `deliver` / `to` / `channel` (선택 사항)
- `timeoutSeconds` (선택 사항)
- `key` (선택 사항, 무인 모드 키)

안전성:

- `key`가 없으면 앱이 확인을 요청합니다.
- `key`가 없으면 앱은 확인 프롬프트에 짧은 메시지 제한을 적용하고 `deliver` / `to` / `channel`을 무시합니다.
- 유효한 `key`가 있으면 무인 실행됩니다(개인 자동화를 위한 용도).

## 온보딩 흐름(일반적인 경우)

1. **OpenClaw.app**을 설치하고 실행합니다.
2. 권한 체크리스트(TCC 프롬프트)를 완료합니다.
3. **Local** 모드가 활성화되어 있고 Gateway가 실행 중인지 확인합니다.
4. 터미널 액세스가 필요하면 CLI를 설치합니다.

## 상태 디렉터리 위치(macOS)

OpenClaw 상태 디렉터리를 iCloud나 다른 클라우드 동기화 폴더에 두지 마세요.
동기화 기반 경로는 지연을 유발할 수 있으며 세션과 자격 증명에 대해
간헐적인 파일 잠금/동기화 경합을 일으킬 수 있습니다.

다음과 같이 로컬 비동기화 상태 경로를 사용하는 것이 좋습니다.
__OC_I18N_900005__
`openclaw doctor`가 다음 위치 아래의 상태를 감지하면:

- `~/Library/Mobile Documents/com~apple~CloudDocs/...`
- `~/Library/CloudStorage/...`

경고를 표시하고 로컬 경로로 다시 옮길 것을 권장합니다.

## 빌드 및 개발 워크플로(네이티브)

- `cd apps/macos && swift build`
- `swift run OpenClaw` (또는 Xcode)
- 앱 패키징: `scripts/package-mac-app.sh`

## Gateway 연결 디버그(macOS CLI)

앱을 실행하지 않고도 macOS 앱이 사용하는 것과 동일한 Gateway WebSocket 핸드셰이크와 discovery
로직을 테스트하려면 디버그 CLI를 사용하세요.
__OC_I18N_900006__
Connect 옵션:

- `--url <ws://host:port>`: config 재정의
- `--mode <local|remote>`: config에서 해석(기본값: config 또는 local)
- `--probe`: 새 health probe를 강제
- `--timeout <ms>`: 요청 타임아웃(기본값: `15000`)
- `--json`: diffing용 구조화된 출력

Discovery 옵션:

- `--include-local`: “local”로 필터링될 게이트웨이도 포함
- `--timeout <ms>`: 전체 discovery 창(기본값: `2000`)
- `--json`: diffing용 구조화된 출력

팁: Node CLI의 `dns-sd` 기반 discovery와
macOS 앱의 discovery 파이프라인(`local.` + 구성된 wide-area 도메인, 그리고
wide-area 및 Tailscale Serve fallback)이 다른지 보려면
`openclaw gateway discover --json`과 비교해 보세요.

## 원격 연결 배관(SSH 터널)

macOS 앱이 **Remote** 모드로 실행되면 로컬 UI
구성 요소가 원격 Gateway를 localhost처럼 사용할 수 있도록 SSH 터널을 엽니다.

### Control 터널(Gateway WebSocket 포트)

- **목적:** health check, status, Web Chat, config 및 기타 control-plane 호출.
- **로컬 포트:** Gateway 포트(기본값 `18789`), 항상 고정.
- **원격 포트:** 원격 호스트의 동일한 Gateway 포트.
- **동작:** 임의의 로컬 포트 없음. 앱은 기존의 정상 터널을 재사용하거나 필요 시 다시 시작합니다.
- **SSH 형태:** BatchMode + ExitOnForwardFailure + keepalive 옵션이 있는 `ssh -N -L <local>:127.0.0.1:<remote>`.
- **IP 보고:** SSH 터널은 loopback을 사용하므로 gateway는 node
  IP를 `127.0.0.1`로 보게 됩니다. 실제 클라이언트
  IP가 표시되길 원하면 **Direct (ws/wss)** 전송을 사용하세요([macOS remote access](/platforms/mac/remote) 참조).

설정 단계는 [macOS remote access](/platforms/mac/remote)를 참조하세요. 프로토콜
세부 사항은 [Gateway protocol](/gateway/protocol)을 참조하세요.

## 관련 문서

- [Gateway runbook](/gateway)
- [Gateway (macOS)](/platforms/mac/bundled-gateway)
- [macOS permissions](/platforms/mac/permissions)
- [Canvas](/platforms/mac/canvas)
