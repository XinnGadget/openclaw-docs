---
read_when:
    - 원격 mac 제어를 설정하거나 디버깅할 때
summary: SSH를 통해 원격 OpenClaw gateway를 제어하는 macOS app 흐름
title: 원격 제어
x-i18n:
    generated_at: "2026-04-05T12:49:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: 96e46e603c2275d04596b5d1ae0fb6858bd1a102a727dc13924ffcd9808fdf7e
    source_path: platforms/mac/remote.md
    workflow: 15
---

# 원격 OpenClaw (macOS ⇄ 원격 호스트)

이 흐름을 사용하면 macOS app이 다른 호스트(데스크톱/서버)에서 실행 중인 OpenClaw gateway를 완전한 원격 제어 방식으로 다룰 수 있습니다. 이것은 app의 **Remote over SSH**(원격 실행) 기능입니다. 상태 확인, Voice Wake 전달, Web Chat을 포함한 모든 기능은 _Settings → General_ 의 동일한 원격 SSH 구성을 재사용합니다.

## 모드

- **로컬(이 Mac)**: 모든 것이 노트북에서 실행됩니다. SSH는 사용하지 않습니다.
- **Remote over SSH(기본값)**: OpenClaw 명령이 원격 호스트에서 실행됩니다. mac app은 `-o BatchMode`, 선택한 identity/key, 로컬 포트 포워딩과 함께 SSH 연결을 엽니다.
- **Remote direct (ws/wss)**: SSH 터널이 없습니다. mac app이 gateway URL에 직접 연결합니다(예: Tailscale Serve 또는 공개 HTTPS reverse proxy 경유).

## 원격 전송 방식

원격 모드는 두 가지 전송 방식을 지원합니다:

- **SSH 터널**(기본값): `ssh -N -L ...`을 사용해 gateway 포트를 localhost로 포워딩합니다. 터널이 loopback이기 때문에 gateway는 node의 IP를 `127.0.0.1`로 보게 됩니다.
- **Direct (ws/wss)**: gateway URL에 직접 연결합니다. gateway는 실제 클라이언트 IP를 봅니다.

## 원격 호스트의 전제 조건

1. Node + pnpm을 설치하고 OpenClaw CLI를 빌드/설치합니다 (`pnpm install && pnpm build && pnpm link --global`).
2. 비대화형 셸에서도 `openclaw`가 PATH에 있도록 합니다(필요하면 `/usr/local/bin` 또는 `/opt/homebrew/bin`에 심볼릭 링크).
3. 키 인증으로 SSH를 열어 둡니다. LAN 밖에서 안정적으로 도달할 수 있도록 **Tailscale** IP를 권장합니다.

## macOS app 설정

1. _Settings → General_ 을 엽니다.
2. **OpenClaw runs** 아래에서 **Remote over SSH**를 선택하고 다음을 설정합니다:
   - **Transport**: **SSH tunnel** 또는 **Direct (ws/wss)**.
   - **SSH target**: `user@host` (선택적으로 `:port`).
     - gateway가 같은 LAN에 있고 Bonjour를 광고한다면 발견된 목록에서 선택해 이 필드를 자동 입력할 수 있습니다.
   - **Gateway URL** (Direct 전용): `wss://gateway.example.ts.net` (또는 로컬/LAN의 경우 `ws://...`).
   - **Identity file** (고급): 키 경로.
   - **Project root** (고급): 명령에 사용되는 원격 체크아웃 경로.
   - **CLI path** (고급): 실행 가능한 `openclaw` 엔트리포인트/바이너리의 선택적 경로(광고되면 자동 입력됨).
3. **Test remote**를 누르세요. 성공하면 원격 `openclaw status --json`가 올바르게 실행된다는 뜻입니다. 실패는 보통 PATH/CLI 문제를 의미하며, exit 127은 원격에서 CLI를 찾을 수 없다는 뜻입니다.
4. 상태 확인과 Web Chat은 이제 이 SSH 터널을 통해 자동으로 실행됩니다.

## Web Chat

- **SSH 터널**: Web Chat은 포워딩된 WebSocket control 포트(기본값 18789)를 통해 gateway에 연결합니다.
- **Direct (ws/wss)**: Web Chat은 구성된 gateway URL에 직접 연결합니다.
- 더 이상 별도의 WebChat HTTP 서버는 없습니다.

## 권한

- 원격 호스트는 로컬과 동일한 TCC 승인(Automation, Accessibility, Screen Recording, Microphone, Speech Recognition, Notifications)이 필요합니다. 한 번만 해당 머신에서 onboarding을 실행해 승인하세요.
- Nodes는 `node.list` / `node.describe`를 통해 자신의 권한 상태를 광고하므로 agent가 어떤 기능을 사용할 수 있는지 알 수 있습니다.

## 보안 참고 사항

- 원격 호스트에서는 loopback bind를 선호하고 SSH 또는 Tailscale을 통해 연결하세요.
- SSH 터널링은 엄격한 호스트 키 검사를 사용합니다. 먼저 호스트 키를 신뢰해 `~/.ssh/known_hosts`에 존재하도록 하세요.
- Gateway를 non-loopback 인터페이스에 바인드한다면 유효한 Gateway 인증을 요구하세요: token, password, 또는 `gateway.auth.mode: "trusted-proxy"`를 가진 identity-aware reverse proxy.
- [Security](/gateway/security) 및 [Tailscale](/gateway/tailscale)을 참조하세요.

## WhatsApp 로그인 흐름(원격)

- 원격 호스트에서 `openclaw channels login --verbose`를 실행하세요. 휴대폰의 WhatsApp으로 QR을 스캔합니다.
- 인증이 만료되면 해당 호스트에서 다시 로그인하세요. 상태 확인이 링크 문제를 드러낼 것입니다.

## 문제 해결

- **exit 127 / not found**: 비로그인 셸의 PATH에 `openclaw`가 없습니다. `/etc/paths`, 셸 rc에 추가하거나 `/usr/local/bin`/`/opt/homebrew/bin`에 심볼릭 링크하세요.
- **상태 probe 실패**: SSH 도달 가능 여부, PATH, 그리고 Baileys가 로그인되어 있는지 확인하세요 (`openclaw status --json`).
- **Web Chat이 멈춤**: 원격 호스트에서 gateway가 실행 중인지, 포워딩된 포트가 gateway WS 포트와 일치하는지 확인하세요. UI는 정상적인 WS 연결이 필요합니다.
- **Node IP가 127.0.0.1로 표시됨**: SSH 터널에서는 정상 동작입니다. gateway가 실제 클라이언트 IP를 보게 하려면 **Transport**를 **Direct (ws/wss)**로 전환하세요.
- **Voice Wake**: 원격 모드에서는 트리거 구문이 자동으로 전달되므로 별도의 전달기가 필요하지 않습니다.

## 알림 사운드

스크립트에서 `openclaw`와 `node.invoke`를 사용해 알림별 사운드를 선택하세요. 예:

```bash
openclaw nodes notify --node <id> --title "Ping" --body "Remote gateway ready" --sound Glass
```

이제 app에는 전역 “default sound” 토글이 없습니다. 호출자가 요청별로 사운드(또는 없음)를 선택합니다.
