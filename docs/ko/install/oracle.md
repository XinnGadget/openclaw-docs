---
read_when:
    - Oracle Cloud에서 OpenClaw를 설정하는 경우
    - OpenClaw용 무료 VPS 호스팅을 찾는 경우
    - 소형 서버에서 OpenClaw를 24/7 실행하려는 경우
summary: Oracle Cloud Always Free ARM 티어에서 OpenClaw 호스팅
title: Oracle Cloud
x-i18n:
    generated_at: "2026-04-05T12:47:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6915f8c428cfcbc215ba6547273df6e7b93212af6590827a3853f15617ba245e
    source_path: install/oracle.md
    workflow: 15
---

# Oracle Cloud

Oracle Cloud의 **Always Free** ARM 티어(최대 4 OCPU, 24 GB RAM, 200 GB 스토리지)를 사용해 OpenClaw Gateway를 무료로 지속 실행하세요.

## 전제 조건

- Oracle Cloud 계정([가입](https://www.oracle.com/cloud/free/)) -- 문제를 겪는 경우 [커뮤니티 가입 가이드](https://gist.github.com/rssnyder/51e3cfedd730e7dd5f4a816143b25dbd) 참조
- Tailscale 계정([tailscale.com](https://tailscale.com)에서 무료)
- SSH 키 쌍
- 약 30분

## 설정

<Steps>
  <Step title="OCI 인스턴스 만들기">
    1. [Oracle Cloud Console](https://cloud.oracle.com/)에 로그인합니다.
    2. **Compute > Instances > Create Instance**로 이동합니다.
    3. 다음과 같이 구성합니다:
       - **이름:** `openclaw`
       - **이미지:** Ubuntu 24.04 (aarch64)
       - **형태:** `VM.Standard.A1.Flex` (Ampere ARM)
       - **OCPU:** 2 (또는 최대 4)
       - **메모리:** 12 GB (또는 최대 24 GB)
       - **부팅 볼륨:** 50 GB (최대 200 GB 무료)
       - **SSH 키:** 공개 키 추가
    4. **Create**를 클릭하고 공인 IP 주소를 기록합니다.

    <Tip>
    인스턴스 생성이 "Out of capacity"로 실패하면 다른 가용성 도메인을 시도하거나 나중에 다시 시도하세요. Free tier 용량은 제한적입니다.
    </Tip>

  </Step>

  <Step title="접속하고 시스템 업데이트">
    ```bash
    ssh ubuntu@YOUR_PUBLIC_IP

    sudo apt update && sudo apt upgrade -y
    sudo apt install -y build-essential
    ```

    `build-essential`은 일부 의존성을 ARM에서 컴파일하는 데 필요합니다.

  </Step>

  <Step title="사용자 및 호스트 이름 구성">
    ```bash
    sudo hostnamectl set-hostname openclaw
    sudo passwd ubuntu
    sudo loginctl enable-linger ubuntu
    ```

    linger를 활성화하면 로그아웃 후에도 사용자 서비스가 계속 실행됩니다.

  </Step>

  <Step title="Tailscale 설치">
    ```bash
    curl -fsSL https://tailscale.com/install.sh | sh
    sudo tailscale up --ssh --hostname=openclaw
    ```

    이제부터는 Tailscale을 통해 접속하세요: `ssh ubuntu@openclaw`.

  </Step>

  <Step title="OpenClaw 설치">
    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    source ~/.bashrc
    ```

    "How do you want to hatch your bot?"라는 프롬프트가 나오면 **Do this later**를 선택하세요.

  </Step>

  <Step title="gateway 구성">
    보안 원격 액세스를 위해 token auth와 Tailscale Serve를 사용하세요.

    ```bash
    openclaw config set gateway.bind loopback
    openclaw config set gateway.auth.mode token
    openclaw doctor --generate-gateway-token
    openclaw config set gateway.tailscale.mode serve
    openclaw config set gateway.trustedProxies '["127.0.0.1"]'

    systemctl --user restart openclaw-gateway.service
    ```

    여기서 `gateway.trustedProxies=["127.0.0.1"]`는 로컬 Tailscale Serve proxy의 전달 IP/로컬 클라이언트 처리를 위한 것입니다. 이것은 **`gateway.auth.mode: "trusted-proxy"`가 아닙니다**. 이 설정에서는 diff viewer 경로가 fail-closed 동작을 유지합니다. 전달된 proxy 헤더 없이 원시 `127.0.0.1` viewer 요청을 보내면 `Diff not found`가 반환될 수 있습니다. 첨부 파일에는 `mode=file` / `mode=both`를 사용하거나, 공유 가능한 viewer 링크가 필요하면 의도적으로 원격 viewer를 활성화하고 `plugins.entries.diffs.config.viewerBaseUrl`(또는 proxy `baseUrl`)을 설정하세요.

  </Step>

  <Step title="VCN 보안 잠그기">
    네트워크 경계에서 Tailscale을 제외한 모든 트래픽을 차단하세요:

    1. OCI Console에서 **Networking > Virtual Cloud Networks**로 이동합니다.
    2. VCN을 클릭한 다음 **Security Lists > Default Security List**로 이동합니다.
    3. `0.0.0.0/0 UDP 41641`(Tailscale)을 제외한 모든 인그레스 규칙을 **제거**합니다.
    4. 기본 이그레스 규칙(모든 아웃바운드 허용)은 유지합니다.

    이렇게 하면 네트워크 경계에서 포트 22의 SSH, HTTP, HTTPS 및 그 외 모든 것이 차단됩니다. 이 시점부터는 Tailscale을 통해서만 연결할 수 있습니다.

  </Step>

  <Step title="확인">
    ```bash
    openclaw --version
    systemctl --user status openclaw-gateway.service
    tailscale serve status
    curl http://localhost:18789
    ```

    tailnet의 어느 장치에서나 Control UI에 접근할 수 있습니다:

    ```
    https://openclaw.<tailnet-name>.ts.net/
    ```

    `<tailnet-name>`은 tailnet 이름으로 바꾸세요(`tailscale status`에서 확인 가능).

  </Step>
</Steps>

## 대체 방법: SSH 터널

Tailscale Serve가 동작하지 않으면 로컬 머신에서 SSH 터널을 사용하세요:

```bash
ssh -L 18789:127.0.0.1:18789 ubuntu@openclaw
```

그런 다음 `http://localhost:18789`를 여세요.

## 문제 해결

**인스턴스 생성 실패("Out of capacity")** -- Free tier ARM 인스턴스는 인기가 많습니다. 다른 가용성 도메인을 시도하거나 사용량이 적은 시간대에 다시 시도하세요.

**Tailscale이 연결되지 않음** -- 다시 인증하려면 `sudo tailscale up --ssh --hostname=openclaw --reset`를 실행하세요.

**Gateway가 시작되지 않음** -- `openclaw doctor --non-interactive`를 실행하고 `journalctl --user -u openclaw-gateway.service -n 50`로 로그를 확인하세요.

**ARM 바이너리 문제** -- 대부분의 npm 패키지는 ARM64에서 동작합니다. 네이티브 바이너리의 경우 `linux-arm64` 또는 `aarch64` 릴리스를 찾으세요. 아키텍처는 `uname -m`으로 확인하세요.

## 다음 단계

- [Channels](/channels) -- Telegram, WhatsApp, Discord 등 연결
- [Gateway configuration](/gateway/configuration) -- 모든 config 옵션
- [Updating](/install/updating) -- OpenClaw를 최신 상태로 유지
