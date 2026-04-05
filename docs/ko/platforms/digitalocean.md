---
read_when:
    - DigitalOcean에서 OpenClaw를 설정할 때
    - OpenClaw용 저렴한 VPS 호스팅을 찾고 있을 때
summary: DigitalOcean에서 OpenClaw 실행(간단한 유료 VPS 옵션)
title: DigitalOcean (플랫폼)
x-i18n:
    generated_at: "2026-04-05T12:48:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6ee4ad84c421f87064534a4fb433df1f70304502921841ec618318ed862d4092
    source_path: platforms/digitalocean.md
    workflow: 15
---

# DigitalOcean에서 OpenClaw

## 목표

DigitalOcean에서 **월 $6**(또는 예약 요금제로 월 $4)로 지속 실행되는 OpenClaw 게이트웨이를 운영합니다.

월 $0 옵션이 필요하고 ARM + provider별 설정을 감수할 수 있다면 [Oracle Cloud 가이드](/platforms/oracle)를 참조하세요.

## 비용 비교 (2026)

| Provider     | 플랜            | 사양                  | 월 요금      | 참고                                  |
| ------------ | --------------- | --------------------- | ----------- | ------------------------------------- |
| Oracle Cloud | Always Free ARM | 최대 4 OCPU, 24GB RAM | $0          | ARM, 제한된 수용량 / 가입 이슈        |
| Hetzner      | CX22            | 2 vCPU, 4GB RAM       | €3.79 (~$4) | 가장 저렴한 유료 옵션                 |
| DigitalOcean | Basic           | 1 vCPU, 1GB RAM       | $6          | 쉬운 UI, 좋은 문서                    |
| Vultr        | Cloud Compute   | 1 vCPU, 1GB RAM       | $6          | 많은 지역                             |
| Linode       | Nanode          | 1 vCPU, 1GB RAM       | $5          | 현재 Akamai 소속                      |

**Provider 선택 가이드:**

- DigitalOcean: 가장 단순한 UX + 예측 가능한 설정(이 가이드)
- Hetzner: 좋은 가격 대비 성능([Hetzner 가이드](/install/hetzner) 참조)
- Oracle Cloud: 월 $0이 가능하지만 더 까다롭고 ARM 전용([Oracle 가이드](/platforms/oracle) 참조)

---

## 전제 조건

- DigitalOcean 계정([$200 무료 크레딧으로 가입](https://m.do.co/c/signup))
- SSH 키 쌍(또는 비밀번호 인증 사용 의향)
- 약 20분

## 1) Droplet 생성

<Warning>
깨끗한 베이스 이미지(Ubuntu 24.04 LTS)를 사용하세요. 시작 스크립트와 방화벽 기본값을 검토하지 않았다면 서드파티 Marketplace 원클릭 이미지는 피하세요.
</Warning>

1. [DigitalOcean](https://cloud.digitalocean.com/)에 로그인합니다
2. **Create → Droplets**를 클릭합니다
3. 다음을 선택합니다:
   - **Region:** 자신(또는 사용자)과 가장 가까운 지역
   - **Image:** Ubuntu 24.04 LTS
   - **Size:** Basic → Regular → **월 $6** (1 vCPU, 1GB RAM, 25GB SSD)
   - **Authentication:** SSH 키(권장) 또는 비밀번호
4. **Create Droplet**를 클릭합니다
5. IP 주소를 기록합니다

## 2) SSH로 연결

```bash
ssh root@YOUR_DROPLET_IP
```

## 3) OpenClaw 설치

```bash
# 시스템 업데이트
apt update && apt upgrade -y

# Node.js 24 설치
curl -fsSL https://deb.nodesource.com/setup_24.x | bash -
apt install -y nodejs

# OpenClaw 설치
curl -fsSL https://openclaw.ai/install.sh | bash

# 확인
openclaw --version
```

## 4) 온보딩 실행

```bash
openclaw onboard --install-daemon
```

마법사는 다음 항목을 안내합니다:

- 모델 인증(API 키 또는 OAuth)
- 채널 설정(Telegram, WhatsApp, Discord 등)
- 게이트웨이 토큰(자동 생성)
- daemon 설치(systemd)

## 5) 게이트웨이 확인

```bash
# 상태 확인
openclaw status

# 서비스 확인
systemctl --user status openclaw-gateway.service

# 로그 보기
journalctl --user -u openclaw-gateway.service -f
```

## 6) 대시보드 접근

게이트웨이는 기본적으로 loopback에 바인딩됩니다. 제어 UI에 접근하려면:

**옵션 A: SSH 터널(권장)**

```bash
# 로컬 머신에서
ssh -L 18789:localhost:18789 root@YOUR_DROPLET_IP

# 그런 다음 열기: http://localhost:18789
```

**옵션 B: Tailscale Serve (HTTPS, loopback 전용)**

```bash
# droplet에서
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up

# 게이트웨이가 Tailscale Serve를 사용하도록 구성
openclaw config set gateway.tailscale.mode serve
openclaw gateway restart
```

열기: `https://<magicdns>/`

참고:

- Serve는 게이트웨이를 loopback 전용으로 유지하고 제어 UI/WebSocket 트래픽을 Tailscale ID 헤더를 통해 인증합니다(Tailscale 헤더 없는 토큰 없는 인증은 신뢰된 게이트웨이 호스트를 전제로 하며, HTTP API는 해당 Tailscale 헤더를 사용하지 않고 대신 게이트웨이의 일반 HTTP 인증 모드를 따릅니다).
- 명시적인 공유 비밀 자격 증명을 요구하려면 `gateway.auth.allowTailscale: false`로 설정하고 `gateway.auth.mode: "token"` 또는 `"password"`를 사용하세요.

**옵션 C: Tailnet 바인드(Serve 없음)**

```bash
openclaw config set gateway.bind tailnet
openclaw gateway restart
```

열기: `http://<tailscale-ip>:18789` (토큰 필요).

## 7) 채널 연결

### Telegram

```bash
openclaw pairing list telegram
openclaw pairing approve telegram <CODE>
```

### WhatsApp

```bash
openclaw channels login whatsapp
# QR 코드 스캔
```

다른 provider는 [Channels](/channels)를 참조하세요.

---

## 1GB RAM에 대한 최적화

$6 droplet은 RAM이 1GB뿐입니다. 원활하게 실행하려면:

### 스왑 추가(권장)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### 더 가벼운 모델 사용

OOM이 발생한다면 다음을 고려하세요:

- 로컬 모델 대신 API 기반 모델(Claude, GPT) 사용
- `agents.defaults.model.primary`를 더 작은 모델로 설정

### 메모리 모니터링

```bash
free -h
htop
```

---

## 영속성

모든 상태는 다음 위치에 저장됩니다:

- `~/.openclaw/` — `openclaw.json`, 에이전트별 `auth-profiles.json`, 채널/provider 상태, 세션 데이터
- `~/.openclaw/workspace/` — 워크스페이스(SOUL.md, memory 등)

이 항목들은 재부팅 후에도 유지됩니다. 주기적으로 백업하세요:

```bash
openclaw backup create
```

---

## Oracle Cloud 무료 대안

Oracle Cloud는 여기의 어떤 유료 옵션보다도 훨씬 강력한 **Always Free** ARM 인스턴스를 월 $0에 제공합니다.

| 제공 항목          | 사양                  |
| ------------------ | --------------------- |
| **4 OCPU**         | ARM Ampere A1         |
| **24GB RAM**       | 충분하고도 남음       |
| **200GB storage**  | 블록 볼륨             |
| **영구 무료**      | 신용카드 청구 없음    |

**주의 사항:**

- 가입이 까다로울 수 있음(실패하면 다시 시도)
- ARM 아키텍처 — 대부분은 작동하지만 일부 바이너리는 ARM 빌드가 필요함

전체 설정 가이드는 [Oracle Cloud](/platforms/oracle)를 참조하세요. 가입 팁과 등록 과정 문제 해결은 이 [커뮤니티 가이드](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd)를 참조하세요.

---

## 문제 해결

### 게이트웨이가 시작되지 않음

```bash
openclaw gateway status
openclaw doctor --non-interactive
journalctl --user -u openclaw-gateway.service --no-pager -n 50
```

### 포트가 이미 사용 중

```bash
lsof -i :18789
kill <PID>
```

### 메모리 부족

```bash
# 메모리 확인
free -h

# 스왑 추가
# 또는 월 $12 droplet(2GB RAM)로 업그레이드
```

---

## 함께 보기

- [Hetzner 가이드](/install/hetzner) — 더 저렴하고 더 강력함
- [Docker 설치](/install/docker) — 컨테이너화된 설정
- [Tailscale](/gateway/tailscale) — 안전한 원격 접근
- [구성](/gateway/configuration) — 전체 config 참조
