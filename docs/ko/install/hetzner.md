---
read_when:
    - 클라우드 VPS에서 OpenClaw를 24/7 실행하고 싶은 경우(노트북이 아님)
    - 자신의 VPS에서 프로덕션급 상시 실행 Gateway를 원하는 경우
    - 영속성, 바이너리, 재시작 동작을 완전히 제어하고 싶은 경우
    - Hetzner 또는 유사한 provider에서 Docker로 OpenClaw를 실행 중인 경우
summary: 내구성 있는 상태, 이미지에 포함된 바이너리, 안전한 재시작 동작으로 Hetzner VPS(Docker)에서 OpenClaw Gateway를 24/7 실행
title: Hetzner
x-i18n:
    generated_at: "2026-04-05T12:46:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: d859e4c0943040b022835f320708f879a11eadef70f2816cf0f2824eaaf165ef
    source_path: install/hetzner.md
    workflow: 15
---

# Hetzner에서 OpenClaw 실행하기(Docker, 프로덕션 VPS 가이드)

## 목표

Docker를 사용해 Hetzner VPS에서 지속적인 OpenClaw Gateway를 실행하고, 내구성 있는 상태, 이미지에 포함된 바이너리, 안전한 재시작 동작을 갖추는 것입니다.

“월 약 $5로 OpenClaw를 24/7” 원한다면, 이것이 가장 단순하고 신뢰할 수 있는 설정입니다.
Hetzner 요금은 변동될 수 있으므로, 가장 작은 Debian/Ubuntu VPS를 선택하고 OOM이 발생하면 확장하세요.

보안 모델 알림:

- 모두가 동일한 신뢰 경계 안에 있고 런타임이 비즈니스 전용이라면 회사 공유 agent도 괜찮습니다.
- 엄격한 분리를 유지하세요: 전용 VPS/런타임 + 전용 계정; 해당 호스트에 개인 Apple/Google/browser/password-manager profile을 두지 마세요.
- 사용자가 서로 적대적일 수 있다면 gateway/호스트/OS 사용자별로 분리하세요.

[Security](/gateway/security) 및 [VPS hosting](/vps)을 참조하세요.

## 무엇을 하게 되나요?(쉽게 설명)

- 작은 Linux 서버(Hetzner VPS)를 임대합니다
- Docker를 설치합니다(격리된 앱 런타임)
- Docker에서 OpenClaw Gateway를 시작합니다
- 호스트에 `~/.openclaw` + `~/.openclaw/workspace`를 영속 저장합니다(재시작/재빌드 후에도 유지)
- 노트북에서 SSH 터널을 통해 Control UI에 액세스합니다

마운트된 `~/.openclaw` 상태에는 `openclaw.json`, agent별
`agents/<agentId>/agent/auth-profiles.json`, `.env`가 포함됩니다.

Gateway는 다음 방식으로 액세스할 수 있습니다.

- 노트북에서의 SSH 포트 포워딩
- 직접 포트 노출(방화벽과 토큰을 직접 관리하는 경우)

이 가이드는 Hetzner의 Ubuntu 또는 Debian을 기준으로 합니다.  
다른 Linux VPS를 사용 중이라면 패키지를 그에 맞게 바꾸세요.
일반적인 Docker 흐름은 [Docker](/install/docker)를 참조하세요.

---

## 빠른 경로(숙련된 운영자용)

1. Hetzner VPS 프로비저닝
2. Docker 설치
3. OpenClaw 리포지토리 클론
4. 영속적인 호스트 디렉터리 생성
5. `.env` 및 `docker-compose.yml` 구성
6. 필요한 바이너리를 이미지에 포함
7. `docker compose up -d`
8. 영속성과 Gateway 액세스 확인

---

## 필요한 것

- root 액세스가 가능한 Hetzner VPS
- 노트북에서의 SSH 액세스
- SSH + 복사/붙여넣기에 대한 기본적인 익숙함
- 약 20분
- Docker 및 Docker Compose
- 모델 auth 자격 증명
- 선택적 provider 자격 증명
  - WhatsApp QR
  - Telegram 봇 토큰
  - Gmail OAuth

---

<Steps>
  <Step title="VPS 프로비저닝">
    Hetzner에서 Ubuntu 또는 Debian VPS를 생성하세요.

    root로 접속합니다:

    ```bash
    ssh root@YOUR_VPS_IP
    ```

    이 가이드는 VPS가 상태 유지형이라고 가정합니다.
    이를 일회용 인프라처럼 취급하지 마세요.

  </Step>

  <Step title="Docker 설치(VPS에서)">
    ```bash
    apt-get update
    apt-get install -y git curl ca-certificates
    curl -fsSL https://get.docker.com | sh
    ```

    확인:

    ```bash
    docker --version
    docker compose version
    ```

  </Step>

  <Step title="OpenClaw 리포지토리 클론">
    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    ```

    이 가이드는 바이너리 영속성을 보장하기 위해 커스텀 이미지를 빌드한다고 가정합니다.

  </Step>

  <Step title="영속적인 호스트 디렉터리 생성">
    Docker 컨테이너는 일시적입니다.
    장기 상태는 모두 호스트에 있어야 합니다.

    ```bash
    mkdir -p /root/.openclaw/workspace

    # 컨테이너 사용자(uid 1000)로 소유권 설정:
    chown -R 1000:1000 /root/.openclaw
    ```

  </Step>

  <Step title="환경 변수 구성">
    리포지토리 루트에 `.env`를 만드세요.

    ```bash
    OPENCLAW_IMAGE=openclaw:latest
    OPENCLAW_GATEWAY_TOKEN=change-me-now
    OPENCLAW_GATEWAY_BIND=lan
    OPENCLAW_GATEWAY_PORT=18789

    OPENCLAW_CONFIG_DIR=/root/.openclaw
    OPENCLAW_WORKSPACE_DIR=/root/.openclaw/workspace

    GOG_KEYRING_PASSWORD=change-me-now
    XDG_CONFIG_HOME=/home/node/.openclaw
    ```

    강력한 시크릿 생성:

    ```bash
    openssl rand -hex 32
    ```

    **이 파일을 커밋하지 마세요.**

    이 `.env` 파일은 `OPENCLAW_GATEWAY_TOKEN` 같은 컨테이너/런타임 env용입니다.
    저장된 provider OAuth/API 키 auth는 마운트된
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`에 저장됩니다.

  </Step>

  <Step title="Docker Compose 구성">
    `docker-compose.yml`을 만들거나 업데이트하세요.

    ```yaml
    services:
      openclaw-gateway:
        image: ${OPENCLAW_IMAGE}
        build: .
        restart: unless-stopped
        env_file:
          - .env
        environment:
          - HOME=/home/node
          - NODE_ENV=production
          - TERM=xterm-256color
          - OPENCLAW_GATEWAY_BIND=${OPENCLAW_GATEWAY_BIND}
          - OPENCLAW_GATEWAY_PORT=${OPENCLAW_GATEWAY_PORT}
          - OPENCLAW_GATEWAY_TOKEN=${OPENCLAW_GATEWAY_TOKEN}
          - GOG_KEYRING_PASSWORD=${GOG_KEYRING_PASSWORD}
          - XDG_CONFIG_HOME=${XDG_CONFIG_HOME}
          - PATH=/home/linuxbrew/.linuxbrew/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        volumes:
          - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
          - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
        ports:
          # 권장: VPS에서는 Gateway를 loopback 전용으로 유지하고 SSH 터널로 액세스하세요.
          # 공개적으로 노출하려면 `127.0.0.1:` 접두사를 제거하고 방화벽을 적절히 구성하세요.
          - "127.0.0.1:${OPENCLAW_GATEWAY_PORT}:18789"
        command:
          [
            "node",
            "dist/index.js",
            "gateway",
            "--bind",
            "${OPENCLAW_GATEWAY_BIND}",
            "--port",
            "${OPENCLAW_GATEWAY_PORT}",
            "--allow-unconfigured",
          ]
    ```

    `--allow-unconfigured`는 bootstrap 편의를 위한 것일 뿐이며, 올바른 gateway 구성의 대체 수단은 아닙니다. 여전히 auth(`gateway.auth.token` 또는 password)를 설정하고 배포에 맞는 안전한 bind 설정을 사용하세요.

  </Step>

  <Step title="공유 Docker VM 런타임 단계">
    공통 Docker 호스트 흐름에는 공유 런타임 가이드를 사용하세요.

    - [필요한 바이너리를 이미지에 포함](/install/docker-vm-runtime#bake-required-binaries-into-the-image)
    - [빌드 및 시작](/install/docker-vm-runtime#build-and-launch)
    - [무엇이 어디에 영속되는가](/install/docker-vm-runtime#what-persists-where)
    - [업데이트](/install/docker-vm-runtime#updates)

  </Step>

  <Step title="Hetzner 전용 액세스">
    공유 빌드 및 시작 단계를 마친 후, 노트북에서 터널을 엽니다:

    ```bash
    ssh -N -L 18789:127.0.0.1:18789 root@YOUR_VPS_IP
    ```

    열기:

    `http://127.0.0.1:18789/`

    구성된 공유 시크릿을 붙여넣으세요. 이 가이드는 기본적으로 gateway token을 사용합니다.
    password auth로 변경했다면 대신 해당 password를 사용하세요.

  </Step>
</Steps>

공유 영속성 맵은 [Docker VM Runtime](/install/docker-vm-runtime#what-persists-where)에 있습니다.

## 코드형 인프라(Terraform)

코드형 인프라 워크플로를 선호하는 팀을 위해, 커뮤니티에서 유지 관리하는 Terraform 설정은 다음을 제공합니다.

- 원격 상태 관리가 포함된 모듈형 Terraform 구성
- cloud-init을 통한 자동 프로비저닝
- 배포 스크립트(bootstrap, 배포, 백업/복원)
- 보안 강화(방화벽, UFW, SSH 전용 액세스)
- gateway 액세스를 위한 SSH 터널 구성

**리포지토리:**

- 인프라: [openclaw-terraform-hetzner](https://github.com/andreesg/openclaw-terraform-hetzner)
- Docker 구성: [openclaw-docker-config](https://github.com/andreesg/openclaw-docker-config)

이 접근 방식은 재현 가능한 배포, 버전 관리되는 인프라, 자동화된 재해 복구를 통해 위의 Docker 설정을 보완합니다.

> **참고:** 커뮤니티 유지 관리 항목입니다. 문제나 기여는 위 리포지토리 링크를 참조하세요.

## 다음 단계

- 메시징 채널 설정: [Channels](/channels)
- Gateway 구성: [Gateway configuration](/gateway/configuration)
- OpenClaw 최신 상태 유지: [Updating](/install/updating)
