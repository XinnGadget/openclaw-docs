---
read_when:
    - Linux 서버 또는 클라우드 VPS에서 Gateway를 실행하려는 경우
    - 호스팅 가이드의 빠른 개요가 필요한 경우
    - OpenClaw를 위한 일반적인 Linux 서버 튜닝이 필요한 경우
sidebarTitle: Linux Server
summary: Linux 서버 또는 클라우드 VPS에서 OpenClaw 실행 — 제공자 선택기, 아키텍처, 튜닝
title: Linux 서버
x-i18n:
    generated_at: "2026-04-05T12:58:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7f2f26bbc116841a29055850ed5f491231554b90539bcbf91a6b519875d494fb
    source_path: vps.md
    workflow: 15
---

# Linux 서버

어떤 Linux 서버나 클라우드 VPS에서든 OpenClaw Gateway를 실행할 수 있습니다. 이 페이지는
제공자 선택, 클라우드 배포 방식 설명, 그리고 어디에나 적용되는 일반적인 Linux
튜닝을 다룹니다.

## 제공자 선택

<CardGroup cols={2}>
  <Card title="Railway" href="/ko/install/railway">원클릭, 브라우저 설정</Card>
  <Card title="Northflank" href="/ko/install/northflank">원클릭, 브라우저 설정</Card>
  <Card title="DigitalOcean" href="/ko/install/digitalocean">간단한 유료 VPS</Card>
  <Card title="Oracle Cloud" href="/ko/install/oracle">Always Free ARM 티어</Card>
  <Card title="Fly.io" href="/ko/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/ko/install/hetzner">Hetzner VPS의 Docker</Card>
  <Card title="GCP" href="/ko/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/ko/install/azure">Linux VM</Card>
  <Card title="exe.dev" href="/ko/install/exe-dev">HTTPS 프록시가 있는 VM</Card>
  <Card title="Raspberry Pi" href="/ko/install/raspberry-pi">ARM 자체 호스팅</Card>
</CardGroup>

**AWS (EC2 / Lightsail / free tier)**도 잘 작동합니다.
커뮤니티 비디오 안내는 다음에서 볼 수 있습니다:
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(커뮤니티 리소스 -- 더 이상 제공되지 않을 수 있음).

## 클라우드 설정 작동 방식

- **Gateway는 VPS에서 실행**되며 상태와 워크스페이스를 소유합니다.
- **Control UI** 또는 **Tailscale/SSH**를 통해 노트북이나 휴대폰에서 연결합니다.
- VPS를 단일 기준 원본으로 취급하고 상태와 워크스페이스를 정기적으로 **백업**하세요.
- 기본 보안 설정: Gateway를 loopback에 유지하고 SSH 터널 또는 Tailscale Serve를 통해 액세스하세요.
  `lan` 또는 `tailnet`에 바인딩하는 경우 `gateway.auth.token` 또는 `gateway.auth.password`를 요구하세요.

관련 페이지: [Gateway 원격 액세스](/ko/gateway/remote), [플랫폼 허브](/ko/platforms).

## VPS에서 공유 회사 에이전트 실행

모든 사용자가 동일한 신뢰 경계 안에 있고 에이전트가 업무 전용이라면, 팀을 위해 단일 에이전트를 실행하는 것은 유효한 설정입니다.

- 전용 런타임(VPS/VM/컨테이너 + 전용 OS 사용자/계정)에 유지하세요.
- 해당 런타임을 개인 Apple/Google 계정이나 개인 브라우저/비밀번호 관리자 프로필에 로그인하지 마세요.
- 사용자가 서로에게 적대적일 수 있다면 gateway/host/OS 사용자 기준으로 분리하세요.

보안 모델 세부 정보: [보안](/ko/gateway/security).

## VPS에서 노드 사용

Gateway는 클라우드에 두고 로컬 장치
(Mac/iOS/Android/headless)에서 **nodes**를 페어링할 수 있습니다. Nodes는 Gateway가 클라우드에 머무는 동안 로컬 화면/카메라/canvas와 `system.run`
기능을 제공합니다.

문서: [Nodes](/ko/nodes), [Nodes CLI](/cli/nodes).

## 소형 VM 및 ARM 호스트용 시작 튜닝

저전력 VM(또는 ARM 호스트)에서 CLI 명령이 느리게 느껴진다면 Node의 module compile cache를 활성화하세요:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE`는 반복 명령의 시작 시간을 개선합니다.
- `OPENCLAW_NO_RESPAWN=1`은 자체 재시작 경로에서 발생하는 추가 시작 오버헤드를 피합니다.
- 첫 번째 명령 실행은 캐시를 워밍업하고, 이후 실행은 더 빨라집니다.
- Raspberry Pi 관련 세부 사항은 [Raspberry Pi](/ko/install/raspberry-pi)를 참고하세요.

### systemd 튜닝 체크리스트(선택 사항)

`systemd`를 사용하는 VM 호스트의 경우 다음을 고려하세요:

- 안정적인 시작 경로를 위한 서비스 환경 변수 추가:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- 재시작 동작을 명시적으로 유지:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- 무작위 I/O 콜드 스타트 페널티를 줄이기 위해 상태/캐시 경로에는 SSD 기반 디스크를 권장합니다.

표준 `openclaw onboard --install-daemon` 경로의 경우 사용자 유닛을 편집하세요:

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

의도적으로 시스템 유닛을 설치한 경우에는
`sudo systemctl edit openclaw-gateway.service`를 통해
`openclaw-gateway.service`를 편집하세요.

`Restart=` 정책이 자동 복구에 도움이 되는 방식:
[systemd can automate service recovery](https://www.redhat.com/en/blog/systemd-automate-recovery).
