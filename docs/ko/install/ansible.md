---
read_when:
    - 보안 강화가 포함된 자동 서버 배포를 원할 때
    - VPN 접근이 포함된 방화벽 격리 설정이 필요할 때
    - 원격 Debian/Ubuntu 서버에 배포하는 경우
summary: Ansible, Tailscale VPN, 방화벽 격리를 사용한 자동화되고 강화된 OpenClaw 설치
title: Ansible
x-i18n:
    generated_at: "2026-04-05T12:44:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27433c3b4afa09406052e428be7b1990476067e47ab8abf7145ff9547b37909a
    source_path: install/ansible.md
    workflow: 15
---

# Ansible 설치

보안 우선 아키텍처를 갖춘 자동 설치기 **[openclaw-ansible](https://github.com/openclaw/openclaw-ansible)** 를 사용해 프로덕션 서버에 OpenClaw를 배포하세요.

<Info>
Ansible 배포의 소스 오브 트루스는 [openclaw-ansible](https://github.com/openclaw/openclaw-ansible) 리포지토리입니다. 이 페이지는 빠른 개요입니다.
</Info>

## 전제 조건

| 요구 사항 | 세부 정보 |
| ----------- | --------------------------------------------------------- |
| **OS**      | Debian 11+ 또는 Ubuntu 20.04+                               |
| **접근 권한**  | root 또는 sudo 권한                                   |
| **네트워크** | 패키지 설치를 위한 인터넷 연결              |
| **Ansible** | 2.14+ (빠른 시작 스크립트가 자동 설치) |

## 제공되는 것

- **방화벽 우선 보안** -- UFW + Docker 격리(SSH + Tailscale만 접근 가능)
- **Tailscale VPN** -- 서비스를 공개 노출하지 않는 안전한 원격 접근
- **Docker** -- 격리된 sandbox 컨테이너, localhost 전용 바인딩
- **심층 방어** -- 4계층 보안 아키텍처
- **Systemd 통합** -- 보안 강화와 함께 부팅 시 자동 시작
- **원커맨드 설정** -- 몇 분 내 전체 배포 완료

## 빠른 시작

원커맨드 설치:

```bash
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw-ansible/main/install.sh | bash
```

## 설치되는 항목

Ansible 플레이북은 다음을 설치하고 구성합니다:

1. **Tailscale** -- 안전한 원격 접근을 위한 메시 VPN
2. **UFW 방화벽** -- SSH + Tailscale 포트만 허용
3. **Docker CE + Compose V2** -- 에이전트 sandbox용
4. **Node.js 24 + pnpm** -- 런타임 의존성(Node 22 LTS, 현재 `22.14+`, 계속 지원됨)
5. **OpenClaw** -- 컨테이너화되지 않은 호스트 기반 실행
6. **Systemd 서비스** -- 보안 강화와 함께 자동 시작

<Note>
게이트웨이는 Docker가 아니라 호스트에서 직접 실행되지만, 에이전트 sandbox는 격리를 위해 Docker를 사용합니다. 자세한 내용은 [Sandboxing](/gateway/sandboxing)을 참조하세요.
</Note>

## 설치 후 설정

<Steps>
  <Step title="openclaw 사용자로 전환">
    ```bash
    sudo -i -u openclaw
    ```
  </Step>
  <Step title="온보딩 마법사 실행">
    설치 후 스크립트가 OpenClaw 설정 구성을 안내합니다.
  </Step>
  <Step title="메시징 provider 연결">
    WhatsApp, Telegram, Discord 또는 Signal에 로그인합니다:
    ```bash
    openclaw channels login
    ```
  </Step>
  <Step title="설치 검증">
    ```bash
    sudo systemctl status openclaw
    sudo journalctl -u openclaw -f
    ```
  </Step>
  <Step title="Tailscale에 연결">
    안전한 원격 접근을 위해 VPN mesh에 참여하세요.
  </Step>
</Steps>

### 빠른 명령

```bash
# 서비스 상태 확인
sudo systemctl status openclaw

# 실시간 로그 보기
sudo journalctl -u openclaw -f

# 게이트웨이 재시작
sudo systemctl restart openclaw

# Provider 로그인(openclaw 사용자로 실행)
sudo -i -u openclaw
openclaw channels login
```

## 보안 아키텍처

이 배포는 4계층 방어 모델을 사용합니다:

1. **방화벽(UFW)** -- SSH(22) + Tailscale(41641/udp)만 공개 노출
2. **VPN(Tailscale)** -- 게이트웨이는 VPN mesh를 통해서만 접근 가능
3. **Docker 격리** -- DOCKER-USER iptables 체인이 외부 포트 노출을 방지
4. **Systemd 보안 강화** -- NoNewPrivileges, PrivateTmp, 비특권 사용자

외부 공격 표면 검증:

```bash
nmap -p- YOUR_SERVER_IP
```

포트 22(SSH)만 열려 있어야 합니다. 다른 모든 서비스(게이트웨이, Docker)는 잠겨 있어야 합니다.

Docker는 게이트웨이 자체를 실행하기 위한 것이 아니라 에이전트 sandbox(격리된 도구 실행)를 위해 설치됩니다. sandbox 구성은 [Multi-Agent Sandbox and Tools](/tools/multi-agent-sandbox-tools)를 참조하세요.

## 수동 설치

자동화 대신 수동 제어를 선호하는 경우:

<Steps>
  <Step title="전제 패키지 설치">
    ```bash
    sudo apt update && sudo apt install -y ansible git
    ```
  </Step>
  <Step title="리포지토리 클론">
    ```bash
    git clone https://github.com/openclaw/openclaw-ansible.git
    cd openclaw-ansible
    ```
  </Step>
  <Step title="Ansible 컬렉션 설치">
    ```bash
    ansible-galaxy collection install -r requirements.yml
    ```
  </Step>
  <Step title="플레이북 실행">
    ```bash
    ./run-playbook.sh
    ```

    또는 직접 실행한 뒤 설정 스크립트를 수동 실행할 수 있습니다:
    ```bash
    ansible-playbook playbook.yml --ask-become-pass
    # Then run: /tmp/openclaw-setup.sh
    ```

  </Step>
</Steps>

## 업데이트

Ansible 설치기는 OpenClaw를 수동 업데이트 가능한 상태로 설정합니다. 표준 업데이트 흐름은 [Updating](/install/updating)을 참조하세요.

구성 변경 등으로 Ansible 플레이북을 다시 실행하려면:

```bash
cd openclaw-ansible
./run-playbook.sh
```

이 작업은 idemopotent하며 여러 번 실행해도 안전합니다.

## 문제 해결

<AccordionGroup>
  <Accordion title="방화벽이 연결을 차단합니다">
    - 먼저 Tailscale VPN을 통해 접근 가능한지 확인하세요
    - SSH 접근(포트 22)은 항상 허용됩니다
    - 게이트웨이는 설계상 Tailscale을 통해서만 접근 가능합니다
  </Accordion>
  <Accordion title="서비스가 시작되지 않습니다">
    ```bash
    # 로그 확인
    sudo journalctl -u openclaw -n 100

    # 권한 확인
    sudo ls -la /opt/openclaw

    # 수동 시작 테스트
    sudo -i -u openclaw
    cd ~/openclaw
    openclaw gateway run
    ```

  </Accordion>
  <Accordion title="Docker sandbox 문제">
    ```bash
    # Docker 실행 확인
    sudo systemctl status docker

    # sandbox 이미지 확인
    sudo docker images | grep openclaw-sandbox

    # 이미지가 없으면 sandbox 이미지 빌드
    cd /opt/openclaw/openclaw
    sudo -u openclaw ./scripts/sandbox-setup.sh
    ```

  </Accordion>
  <Accordion title="Provider 로그인 실패">
    `openclaw` 사용자로 실행 중인지 확인하세요:
    ```bash
    sudo -i -u openclaw
    openclaw channels login
    ```
  </Accordion>
</AccordionGroup>

## 고급 구성

자세한 보안 아키텍처 및 문제 해결은 openclaw-ansible 리포지토리를 참조하세요:

- [Security Architecture](https://github.com/openclaw/openclaw-ansible/blob/main/docs/security.md)
- [Technical Details](https://github.com/openclaw/openclaw-ansible/blob/main/docs/architecture.md)
- [Troubleshooting Guide](https://github.com/openclaw/openclaw-ansible/blob/main/docs/troubleshooting.md)

## 관련

- [openclaw-ansible](https://github.com/openclaw/openclaw-ansible) -- 전체 배포 가이드
- [Docker](/install/docker) -- 컨테이너화된 게이트웨이 설정
- [Sandboxing](/gateway/sandboxing) -- 에이전트 sandbox 구성
- [Multi-Agent Sandbox and Tools](/tools/multi-agent-sandbox-tools) -- 에이전트별 격리
