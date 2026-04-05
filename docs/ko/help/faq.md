---
read_when:
    - 일반적인 설정, 설치, 온보딩 또는 런타임 지원 질문에 답하는 중
    - 더 깊은 디버깅 전에 사용자가 보고한 문제를 분류하는 중
summary: OpenClaw 설정, 구성, 사용에 대한 자주 묻는 질문
title: FAQ
x-i18n:
    generated_at: "2026-04-05T12:49:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0f71dc12f60aceaa1d095aaa4887d59ecf2a53e349d10a3e2f60e464ae48aff6
    source_path: help/faq.md
    workflow: 15
---

# FAQ

실제 환경 설정(로컬 개발, VPS, 다중 에이전트, OAuth/API 키, 모델 failover)을 위한 빠른 답변과 더 깊은 문제 해결입니다. 런타임 진단은 [Troubleshooting](/gateway/troubleshooting)을 참조하세요. 전체 config 참조는 [Configuration](/gateway/configuration)을 참조하세요.

## 문제가 생겼을 때 처음 60초 안에 할 일

1. **빠른 상태 확인(첫 번째 점검)**

   ```bash
   openclaw status
   ```

   빠른 로컬 요약: OS + 업데이트, gateway/service 도달 가능 여부, agents/sessions, provider config + 런타임 문제(gateway에 도달 가능한 경우).

2. **공유하기 안전한 붙여넣기용 보고서**

   ```bash
   openclaw status --all
   ```

   로그 tail이 포함된 읽기 전용 진단(토큰은 redacted 처리됨).

3. **데몬 + 포트 상태**

   ```bash
   openclaw gateway status
   ```

   supervisor 런타임과 RPC 도달 가능 여부, 프로브 대상 URL, 서비스가 사용했을 가능성이 높은 config를 표시합니다.

4. **심층 프로브**

   ```bash
   openclaw status --deep
   ```

   지원되는 경우 채널 프로브를 포함한 라이브 gateway 상태 프로브를 실행합니다
   (도달 가능한 gateway 필요). [Health](/gateway/health)를 참조하세요.

5. **최신 로그 tail 보기**

   ```bash
   openclaw logs --follow
   ```

   RPC가 내려가 있으면 다음으로 폴백하세요.

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   파일 로그는 서비스 로그와 별개입니다. [Logging](/logging)과 [Troubleshooting](/gateway/troubleshooting)을 참조하세요.

6. **doctor 실행(복구)**

   ```bash
   openclaw doctor
   ```

   config/state를 복구/마이그레이션하고 health checks를 실행합니다. [Doctor](/gateway/doctor)를 참조하세요.

7. **Gateway 스냅샷**

   ```bash
   openclaw health --json
   openclaw health --verbose   # 오류 시 대상 URL + config 경로 표시
   ```

   실행 중인 gateway에 전체 스냅샷을 요청합니다(WS 전용). [Health](/gateway/health)를 참조하세요.

## 빠른 시작 및 첫 실행 설정

<AccordionGroup>
  <Accordion title="막혔습니다. 가장 빠르게 벗어나는 방법은 무엇인가요?">
    **당신의 머신을 볼 수 있는** 로컬 AI 에이전트를 사용하세요. 이것이 Discord에서 묻는 것보다 훨씬 효과적입니다.
    대부분의 "막혔다" 사례는 원격 도우미가 직접 확인할 수 없는 **로컬 config 또는 환경 문제**이기 때문입니다.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    이 도구들은 리포지토리를 읽고, 명령을 실행하고, 로그를 검사하며, 머신 수준 설정(PATH, services, permissions, auth 파일)을 고치는 데 도움을 줄 수 있습니다. 해킹 가능한 (git) 설치를 통해 **전체 소스 체크아웃**을 제공하세요.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    이렇게 하면 OpenClaw가 **git 체크아웃에서** 설치되므로 에이전트가 코드 + 문서를 읽고
    현재 실행 중인 정확한 버전을 기준으로 추론할 수 있습니다. 나중에
    `--install-method git` 없이 설치 프로그램을 다시 실행하면 언제든 stable로 돌아갈 수 있습니다.

    팁: 에이전트에게 수정 사항을 **계획하고 감독**하게 하세요(단계별). 그다음
    필요한 명령만 실행하세요. 이렇게 하면 변경이 작고 감사하기 쉬워집니다.

    실제 버그나 수정 사항을 발견했다면 GitHub 이슈를 올리거나 PR을 보내 주세요.
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    다음 명령으로 시작하세요(도움을 요청할 때 출력도 함께 공유).

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    이 명령들이 하는 일:

    - `openclaw status`: gateway/agent 상태 + 기본 config의 빠른 스냅샷
    - `openclaw models status`: provider 인증 + 모델 가용성 확인
    - `openclaw doctor`: 일반적인 config/state 문제 검증 및 복구

    그 외 유용한 CLI 점검: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    빠른 디버그 루프: [문제가 생겼을 때 처음 60초 안에 할 일](#문제가-생겼을-때-처음-60초-안에-할-일).
    설치 문서: [Install](/install), [Installer flags](/install/installer), [Updating](/install/updating).

  </Accordion>

  <Accordion title="Heartbeat가 계속 건너뛰어집니다. skip 이유는 무엇을 의미하나요?">
    일반적인 heartbeat skip 이유:

    - `quiet-hours`: 구성된 active-hours 창 밖
    - `empty-heartbeat-file`: `HEARTBEAT.md`가 존재하지만 빈 내용/헤더뿐인 스캐폴딩만 있음
    - `no-tasks-due`: `HEARTBEAT.md` task mode가 활성화되어 있지만 어떤 작업 간격도 아직 도래하지 않음
    - `alerts-disabled`: heartbeat 표시 기능이 모두 비활성화됨(`showOk`, `showAlerts`, `useIndicator`가 모두 꺼짐)

    task mode에서는 실제 heartbeat 실행이 완료된 뒤에만
    due 타임스탬프가 앞으로 이동합니다. 건너뛴 실행은 작업을 완료된 것으로 표시하지 않습니다.

    문서: [Heartbeat](/gateway/heartbeat), [Automation & Tasks](/automation).

  </Accordion>

  <Accordion title="OpenClaw를 설치하고 설정하는 권장 방법">
    리포지토리에서 권장하는 방법은 소스에서 실행하고 온보딩을 사용하는 것입니다.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    마법사는 UI assets도 자동으로 빌드할 수 있습니다. 온보딩 후에는 보통 포트 **18789**에서 Gateway를 실행합니다.

    소스에서 실행(기여자/개발자):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # 첫 실행 시 UI deps 자동 설치
    openclaw onboard
    ```

    아직 전역 설치가 없다면 `pnpm openclaw onboard`로 실행하세요.

  </Accordion>

  <Accordion title="온보딩 후 대시보드를 어떻게 열 수 있나요?">
    마법사는 온보딩 직후 브라우저에 깨끗한(토큰이 없는) 대시보드 URL을 열고 요약에도 링크를 출력합니다. 그 탭을 열어 두세요. 실행되지 않았다면 동일한 머신에서 출력된 URL을 복사해서 붙여넣으세요.
  </Accordion>

  <Accordion title="localhost와 원격에서 대시보드 인증은 어떻게 하나요?">
    **Localhost(같은 머신):**

    - `http://127.0.0.1:18789/`를 엽니다.
    - 공유 비밀 인증을 요구하면 구성된 토큰 또는 비밀번호를 Control UI 설정에 붙여넣으세요.
    - 토큰 소스: `gateway.auth.token` (또는 `OPENCLAW_GATEWAY_TOKEN`).
    - 비밀번호 소스: `gateway.auth.password` (또는 `OPENCLAW_GATEWAY_PASSWORD`).
    - 아직 공유 비밀이 구성되지 않았다면 `openclaw doctor --generate-gateway-token`으로 토큰을 생성하세요.

    **localhost가 아닌 경우:**

    - **Tailscale Serve** (권장): bind를 loopback으로 유지한 채 `openclaw gateway --tailscale serve`를 실행하고 `https://<magicdns>/`를 엽니다. `gateway.auth.allowTailscale`이 `true`이면 identity 헤더가 Control UI/WebSocket 인증을 충족합니다(공유 비밀을 붙여넣지 않음, 신뢰된 gateway 호스트 가정). HTTP APIs는 private-ingress `none` 또는 trusted-proxy HTTP auth를 의도적으로 사용하지 않는 한 여전히 공유 비밀 인증이 필요합니다.
      같은 클라이언트에서 잘못된 동시 Serve 인증 시도는 failed-auth limiter가 기록하기 전에 직렬화되므로, 두 번째 잘못된 재시도는 이미 `retry later`를 표시할 수 있습니다.
    - **Tailnet bind**: `openclaw gateway --bind tailnet --token "<token>"`을 실행하거나(또는 비밀번호 인증을 구성하고), `http://<tailscale-ip>:18789/`를 연 뒤, 대시보드 설정에 일치하는 공유 비밀을 붙여넣으세요.
    - **Identity-aware reverse proxy**: Gateway를 non-loopback trusted proxy 뒤에 두고 `gateway.auth.mode: "trusted-proxy"`를 구성한 다음, proxy URL을 엽니다.
    - **SSH tunnel**: `ssh -N -L 18789:127.0.0.1:18789 user@host` 후 `http://127.0.0.1:18789/`를 엽니다. 터널을 통해서도 공유 비밀 인증은 여전히 적용되므로, 요청 시 구성된 토큰 또는 비밀번호를 붙여넣으세요.

    bind 모드 및 인증 세부 사항은 [Dashboard](/web/dashboard)와 [Web surfaces](/web)를 참조하세요.

  </Accordion>

  <Accordion title="채팅 승인에 exec approval config가 두 개 있는 이유는 무엇인가요?">
    서로 다른 계층을 제어합니다:

    - `approvals.exec`: 승인 프롬프트를 채팅 대상으로 전달
    - `channels.<channel>.execApprovals`: 해당 채널이 exec 승인의 네이티브 승인 클라이언트로 동작하게 함

    실제 승인 게이트는 여전히 호스트 exec 정책입니다. 채팅 config는 승인
    프롬프트가 어디에 나타나는지, 사람들이 어떻게 응답할 수 있는지만 제어합니다.

    대부분의 설정에서는 **둘 다 필요하지 않습니다**:

    - 채팅이 이미 명령과 응답을 지원한다면, 같은 채팅의 `/approve`가 공유 경로를 통해 동작합니다.
    - 지원되는 네이티브 채널이 approvers를 안전하게 추론할 수 있으면, 이제 OpenClaw는 `channels.<channel>.execApprovals.enabled`가 설정되지 않았거나 `"auto"`일 때 DM 우선 네이티브 승인을 자동으로 활성화합니다.
    - 네이티브 승인 카드/버튼을 사용할 수 있을 때는 그 네이티브 UI가 기본 경로이며, 도구 결과가 채팅 승인을 사용할 수 없다고 하거나 수동 승인이 유일한 경로일 때만 에이전트가 수동 `/approve` 명령을 포함해야 합니다.
    - 프롬프트를 다른 채팅이나 명시적 운영 룸에도 전달해야 할 때만 `approvals.exec`를 사용하세요.
    - 승인 프롬프트를 원래 방/주제로도 다시 게시하려는 경우에만 `channels.<channel>.execApprovals.target: "channel"` 또는 `"both"`를 사용하세요.
    - plugin 승인은 다시 별개입니다. 기본적으로 같은 채팅의 `/approve`를 사용하고, 선택적으로 `approvals.plugin` 전달을 사용하며, 일부 네이티브 채널만 그 위에 plugin-approval-native 처리를 유지합니다.

    짧게 말하면: forwarding은 라우팅용이고, 네이티브 클라이언트 config는 더 풍부한 채널별 UX용입니다.
    [Exec Approvals](/tools/exec-approvals)를 참조하세요.

  </Accordion>

  <Accordion title="어떤 런타임이 필요한가요?">
    Node **>= 22**가 필요합니다. `pnpm`을 권장합니다. Gateway에는 Bun을 **권장하지 않습니다**.
  </Accordion>

  <Accordion title="Raspberry Pi에서 실행되나요?">
    예. Gateway는 가볍습니다. 문서에는 개인 사용 기준으로 **512MB-1GB RAM**, **1 코어**, 약 **500MB**
    디스크면 충분하다고 되어 있으며, **Raspberry Pi 4에서도 실행 가능**하다고 안내합니다.

    로그, 미디어, 다른 services를 위한 여유를 원한다면 **2GB를 권장**하지만
    필수 최소 요구 사항은 아닙니다.

    팁: 작은 Pi/VPS가 Gateway를 호스팅하고, 노트북/휴대폰에서 **nodes**를 페어링해
    로컬 screen/camera/canvas 또는 명령 실행을 사용할 수 있습니다. [Nodes](/nodes)를 참조하세요.

  </Accordion>

  <Accordion title="Raspberry Pi 설치 팁이 있나요?">
    짧게 말하면: 작동하지만 거친 부분이 있을 수 있습니다.

    - **64-bit** OS를 사용하고 Node >= 22를 유지하세요.
    - 로그를 보고 빠르게 업데이트할 수 있도록 **해킹 가능한(git) 설치**를 선호하세요.
    - 채널/skills 없이 시작한 뒤 하나씩 추가하세요.
    - 이상한 바이너리 문제가 생기면 대개 **ARM 호환성** 문제입니다.

    문서: [Linux](/platforms/linux), [Install](/install).

  </Accordion>

  <Accordion title="wake up my friend에서 멈추거나 온보딩이 진행되지 않습니다. 이제 어떻게 하나요?">
    그 화면은 Gateway가 도달 가능하고 인증되어 있어야 동작합니다. TUI도 첫 hatch 시
    "Wake up, my friend!"를 자동 전송합니다. 그 줄이 보이는데 **응답이 없고**
    토큰이 0에 머문다면 에이전트가 전혀 실행되지 않은 것입니다.

    1. Gateway를 재시작하세요:

    ```bash
    openclaw gateway restart
    ```

    2. 상태 + 인증 확인:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. 여전히 멈춘다면 다음을 실행하세요:

    ```bash
    openclaw doctor
    ```

    Gateway가 원격이라면 터널/Tailscale 연결이 살아 있는지, UI가 올바른 Gateway를 가리키는지 확인하세요. [Remote access](/gateway/remote)를 참조하세요.

  </Accordion>

  <Accordion title="온보딩을 다시 하지 않고 설정을 새 머신(Mac mini)으로 옮길 수 있나요?">
    예. **상태 디렉터리**와 **workspace**를 복사한 뒤 Doctor를 한 번 실행하세요. 이렇게 하면
    **두 위치를 모두** 복사하는 한 봇을 "완전히 동일하게" (메모리, 세션 기록, 인증, 채널
    상태 포함) 유지할 수 있습니다:

    1. 새 머신에 OpenClaw를 설치합니다.
    2. 이전 머신의 `$OPENCLAW_STATE_DIR` (기본값: `~/.openclaw`)를 복사합니다.
    3. workspace (기본값: `~/.openclaw/workspace`)를 복사합니다.
    4. `openclaw doctor`를 실행하고 Gateway 서비스를 재시작합니다.

    이렇게 하면 config, auth profiles, WhatsApp 자격 증명, 세션, 메모리가 보존됩니다. 원격
    모드에서는 gateway 호스트가 세션 저장소와 workspace를 소유한다는 점을 기억하세요.

    **중요:** workspace만 GitHub에 commit/push하면
    **메모리 + bootstrap 파일만** 백업되는 것이고, **세션 기록이나 인증은**
    백업되지 않습니다. 그것들은 `~/.openclaw/` 아래(예: `~/.openclaw/agents/<agentId>/sessions/`)에 있습니다.

    관련 문서: [Migrating](/install/migrating), [디스크에서 파일이 저장되는 위치](#디스크에서-파일이-저장되는-위치),
    [Agent workspace](/concepts/agent-workspace), [Doctor](/gateway/doctor),
    [Remote mode](/gateway/remote).

  </Accordion>

  <Accordion title="최신 버전의 변경 사항은 어디서 볼 수 있나요?">
    GitHub changelog를 확인하세요:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    최신 항목이 맨 위에 있습니다. 맨 위 섹션이 **Unreleased**로 표시되어 있으면, 그 아래의 다음 날짜 섹션이 최신 배포 버전입니다. 항목은 **Highlights**, **Changes**, **Fixes**(필요 시 docs/other 섹션 포함)로 묶여 있습니다.

  </Accordion>

  <Accordion title="docs.openclaw.ai에 접근할 수 없습니다(SSL 오류)">
    일부 Comcast/Xfinity 연결에서 Xfinity
    Advanced Security가 `docs.openclaw.ai`를 잘못 차단합니다. 이를 비활성화하거나 `docs.openclaw.ai`를 allowlist에 추가한 뒤 다시 시도하세요.
    여기에서 차단 해제 요청도 도와주세요: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    여전히 사이트에 접속할 수 없다면, 문서는 GitHub에도 미러링되어 있습니다:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="stable과 beta의 차이는 무엇인가요?">
    **Stable**과 **beta**는 별도 코드 라인이 아니라 **npm dist-tags**입니다:

    - `latest` = stable
    - `beta` = 테스트용 초기 빌드

    보통 stable 릴리스는 먼저 **beta**에 올라간 뒤, 명시적
    promotion 단계에서 같은 버전이 `latest`로 이동합니다. 유지관리자는 필요 시
    곧바로 `latest`에 게시할 수도 있습니다. 그래서 promotion 후 beta와 stable이
    **같은 버전**을 가리킬 수도 있습니다.

    변경 사항 보기:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    설치 원라이너와 beta와 dev의 차이는 아래 accordion을 참조하세요.

  </Accordion>

  <Accordion title="beta 버전은 어떻게 설치하나요? beta와 dev의 차이는 무엇인가요?">
    **Beta**는 npm dist-tag `beta`입니다(promotion 후 `latest`와 같을 수 있음).
    **Dev**는 움직이는 `main`의 최신 상태(git)이며, 게시될 경우 npm dist-tag `dev`를 사용합니다.

    원라이너(macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Windows 설치 프로그램(PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    자세한 내용: [Development channels](/install/development-channels) 및 [Installer flags](/install/installer).

  </Accordion>

  <Accordion title="최신 기능을 사용하려면 어떻게 해야 하나요?">
    두 가지 방법이 있습니다:

    1. **Dev 채널(git 체크아웃):**

    ```bash
    openclaw update --channel dev
    ```

    이렇게 하면 `main` 브랜치로 전환되고 소스에서 업데이트됩니다.

    2. **해킹 가능한 설치(설치 사이트에서):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    이렇게 하면 수정 가능한 로컬 리포지토리를 얻게 되고, 이후 git으로 업데이트할 수 있습니다.

    직접 깨끗한 clone을 원한다면 다음을 사용하세요:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    문서: [Update](/cli/update), [Development channels](/install/development-channels),
    [Install](/install).

  </Accordion>

  <Accordion title="설치와 온보딩은 보통 얼마나 걸리나요?">
    대략적인 기준:

    - **설치:** 2-5분
    - **온보딩:** 구성하는 채널/모델 수에 따라 5-15분

    멈춘 경우 [Installer stuck](#빠른-시작-및-첫-실행-설정)과
    [I am stuck](#빠른-시작-및-첫-실행-설정)의 빠른 디버그 루프를 사용하세요.

  </Accordion>

  <Accordion title="설치 프로그램이 멈췄습니다. 더 많은 피드백을 보려면 어떻게 하나요?">
    설치 프로그램을 **verbose 출력**과 함께 다시 실행하세요:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    verbose와 함께 beta 설치:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    해킹 가능한(git) 설치:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Windows (PowerShell) 동등 예시:

    ```powershell
    # install.ps1에는 아직 전용 -Verbose 플래그가 없습니다.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    더 많은 옵션: [Installer flags](/install/installer).

  </Accordion>

  <Accordion title="Windows 설치 중 git not found 또는 openclaw not recognized가 나옵니다">
    Windows에서 흔한 두 가지 문제:

    **1) npm error spawn git / git not found**

    - **Git for Windows**를 설치하고 `git`이 PATH에 있도록 하세요.
    - PowerShell을 닫았다가 다시 열고 설치 프로그램을 다시 실행하세요.

    **2) 설치 후 openclaw is not recognized**

    - npm 전역 bin 폴더가 PATH에 없습니다.
    - 경로 확인:

      ```powershell
      npm config get prefix
      ```

    - 해당 디렉터리를 사용자 PATH에 추가하세요(Windows에서는 `\bin` 접미사 불필요, 대부분 시스템에서 `%AppData%\npm`).
    - PATH를 업데이트한 후 PowerShell을 닫았다가 다시 열세요.

    가장 매끄러운 Windows 설정을 원한다면 네이티브 Windows 대신 **WSL2**를 사용하세요.
    문서: [Windows](/platforms/windows).

  </Accordion>

  <Accordion title="Windows exec 출력에서 중국어가 깨져 보입니다. 어떻게 해야 하나요?">
    이는 보통 네이티브 Windows 셸에서 콘솔 코드 페이지 불일치 문제입니다.

    증상:

    - `system.run`/`exec` 출력에서 중국어가 mojibake로 표시됨
    - 같은 명령이 다른 터미널 프로필에서는 정상적으로 보임

    PowerShell에서 빠른 해결 방법:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    그런 다음 Gateway를 재시작하고 명령을 다시 시도하세요:

    ```powershell
    openclaw gateway restart
    ```

    최신 OpenClaw에서도 계속 재현된다면 다음 이슈를 추적/보고하세요:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="문서가 제 질문에 답하지 못했습니다. 더 나은 답을 얻으려면 어떻게 하나요?">
    **해킹 가능한(git) 설치**를 사용해 전체 소스와 문서를 로컬에 둔 뒤,
    _그 폴더에서_ 봇(또는 Claude/Codex)에게 물어보세요. 그러면 리포지토리를 읽고 정확하게 답할 수 있습니다.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    자세한 내용: [Install](/install) 및 [Installer flags](/install/installer).

  </Accordion>

  <Accordion title="Linux에 OpenClaw를 설치하려면 어떻게 하나요?">
    짧게 답하면: Linux 가이드를 따르고 그다음 온보딩을 실행하세요.

    - Linux 빠른 경로 + 서비스 설치: [Linux](/platforms/linux).
    - 전체 안내: [Getting Started](/ko/start/getting-started).
    - 설치 프로그램 + 업데이트: [Install & updates](/install/updating).

  </Accordion>

  <Accordion title="VPS에 OpenClaw를 설치하려면 어떻게 하나요?">
    어떤 Linux VPS에서도 작동합니다. 서버에 설치한 뒤 SSH/Tailscale로 Gateway에 접근하세요.

    가이드: [exe.dev](/install/exe-dev), [Hetzner](/install/hetzner), [Fly.io](/install/fly).
    원격 접근: [Gateway remote](/gateway/remote).

  </Accordion>

  <Accordion title="클라우드/VPS 설치 가이드는 어디에 있나요?">
    일반적인 providers를 모아둔 **호스팅 허브**가 있습니다. 하나를 선택해서 가이드를 따라가세요:

    - [VPS hosting](/vps) (모든 provider를 한곳에서)
    - [Fly.io](/install/fly)
    - [Hetzner](/install/hetzner)
    - [exe.dev](/install/exe-dev)

    클라우드에서의 동작 방식: **Gateway는 서버에서 실행**되고, 당신은
    노트북/휴대폰에서 Control UI(Tailscale/SSH 포함)를 통해 접근합니다. 상태 + workspace는
    서버에 있으므로, 서버를 진실의 원천으로 취급하고 백업하세요.

    클라우드 Gateway에 **nodes**(Mac/iOS/Android/headless)를 페어링하면
    Gateway는 클라우드에 두면서도 로컬 screen/camera/canvas에 접근하거나
    노트북에서 명령을 실행할 수 있습니다.

    허브: [Platforms](/platforms). 원격 접근: [Gateway remote](/gateway/remote).
    Nodes: [Nodes](/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="OpenClaw에 스스로 업데이트하라고 시킬 수 있나요?">
    짧게 답하면: **가능하지만 권장하지는 않습니다**. 업데이트 흐름은
    Gateway를 재시작할 수 있고(활성 세션이 끊김), 깨끗한 git 체크아웃이 필요할 수 있으며,
    확인을 요구할 수도 있습니다. 더 안전한 방법은 운영자가 셸에서 업데이트를 실행하는 것입니다.

    CLI 사용:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    꼭 에이전트에서 자동화해야 한다면:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    문서: [Update](/cli/update), [Updating](/install/updating).

  </Accordion>

  <Accordion title="온보딩은 실제로 무엇을 하나요?">
    `openclaw onboard`는 권장되는 설정 경로입니다. **로컬 모드**에서 다음을 안내합니다:

    - **모델/인증 설정**(provider OAuth, Claude CLI 재사용, API 키 지원, LM Studio 같은 로컬 모델 옵션 포함)
    - **Workspace** 위치 + bootstrap 파일
    - **Gateway 설정**(bind/port/auth/tailscale)
    - **채널**(WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage 및 QQ Bot 같은 번들 채널 plugins)
    - **데몬 설치**(macOS의 LaunchAgent, Linux/WSL2의 systemd user unit)
    - **Health checks** 및 **skills** 선택

    또한 구성된 모델이 알 수 없거나 인증이 없으면 경고를 표시합니다.

  </Accordion>

  <Accordion title="이걸 실행하려면 Claude나 OpenAI 구독이 필요한가요?">
    아니요. OpenClaw는 **API 키**(Anthropic/OpenAI/기타)나
    **로컬 전용 모델**로 실행할 수 있으므로 데이터가 디바이스에 머물 수 있습니다. 구독(Claude
    Pro/Max 또는 OpenAI Codex)은 해당 providers를 인증하는 **선택적** 방법일 뿐입니다.

    Anthropic의 공개 CLI 문서를 기준으로, Claude Code CLI fallback은 로컬의
    사용자 관리 자동화에는 허용될 가능성이 높다고 봅니다. 다만,
    Anthropic의 third-party harness 정책은 외부 제품에서의
    구독 기반 사용에 대해 충분한 모호성을 만들기 때문에, 우리는 이를
    프로덕션 용도로 권장하지 않습니다. 또한 Anthropic은 **2026년 4월 4일
    오후 12:00 PT / 오후 8:00 BST**에 OpenClaw 사용자들에게
    **OpenClaw** Claude-login 경로가 third-party harness 사용으로 간주되며, 이제
    구독과 별도로 청구되는 **Extra Usage**가 필요하다고 알렸습니다. OpenAI Codex OAuth는
    OpenClaw 같은 외부 도구에서 명시적으로 지원됩니다.

    OpenClaw는 그 외에도 다음과 같은 호스팅형 구독 스타일 옵션을 지원합니다:
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan**,
    **Z.AI / GLM Coding Plan**.

    문서: [Anthropic](/providers/anthropic), [OpenAI](/providers/openai),
    [Qwen Cloud](/providers/qwen),
    [MiniMax](/providers/minimax), [GLM Models](/providers/glm),
    [Local models](/gateway/local-models), [Models](/concepts/models).

  </Accordion>

  <Accordion title="API 키 없이 Claude Max 구독을 사용할 수 있나요?">
    예. gateway 호스트의 로컬 **Claude CLI** 로그인으로 가능합니다.

    Claude Pro/Max 구독에는 **API 키가 포함되지 않으므로**, OpenClaw에서는 Claude CLI
    재사용이 로컬 fallback 경로입니다. Anthropic의 공개 CLI 문서를 기준으로
    Claude Code CLI fallback은 로컬의 사용자 관리 자동화에는 허용될 가능성이 높다고 봅니다.
    다만 Anthropic의 third-party harness
    정책은 외부 제품에서의 구독 기반 사용에 대해 충분한 모호성을 만들기 때문에
    프로덕션 용도로는 권장하지 않습니다. 우리는
    대신 Anthropic API 키를 권장합니다.

  </Accordion>

  <Accordion title="Claude 구독 인증(Claude Pro 또는 Max)을 지원하나요?">
    예. `openclaw models auth login --provider anthropic --method cli --set-default`로
    gateway 호스트의 로컬 **Claude CLI** 로그인을 재사용할 수 있습니다.

    Anthropic setup-token도 레거시/수동 OpenClaw 경로로 다시 사용할 수 있습니다. 이 경우에도 Anthropic의 OpenClaw 전용 과금 안내가 적용되므로, Anthropic이 **Extra Usage**를 요구한다는 점을 염두에 두고 사용하세요. [Anthropic](/providers/anthropic) 및 [OAuth](/concepts/oauth)를 참조하세요.

    중요: Anthropic의 공개 CLI 문서를 기준으로, Claude Code CLI fallback은 로컬의
    사용자 관리 자동화에는 허용될 가능성이 높다고 봅니다. 다만 Anthropic의 third-party harness
    정책은 외부 제품에서의 구독 기반 사용에 대해 충분한 모호성을 만들기 때문에
    프로덕션 용도로는 권장하지 않습니다. 또한 Anthropic은
    **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에 OpenClaw 사용자에게
    **OpenClaw** Claude-login 경로에는
    구독과 별도 청구되는 **Extra Usage**가 필요하다고 알렸습니다.

    프로덕션 또는 다중 사용자 워크로드에는 Anthropic API 키 인증이
    더 안전하고 권장되는 선택입니다. OpenClaw에서 다른 구독 스타일의 호스팅 옵션을 원한다면
    [OpenAI](/providers/openai), [Qwen / Model
    Cloud](/providers/qwen), [MiniMax](/providers/minimax), [GLM Models](/providers/glm)를 참조하세요.

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Anthropic에서 HTTP 429 rate_limit_error가 보이는 이유는 무엇인가요?">
이는 현재 창에서 **Anthropic 할당량/속도 제한**이 소진되었다는 뜻입니다. **Claude CLI**를
사용 중이라면 창이 리셋될 때까지 기다리거나 요금제를 업그레이드하세요. **Anthropic API 키**를
사용 중이라면 Anthropic Console에서
사용량/과금을 확인하고 필요하면 한도를 높이세요.

    메시지가 구체적으로 다음과 같다면:
    `Extra usage is required for long context requests`, 요청이
    Anthropic의 1M context beta(`context1m: true`)를 사용하려 한다는 뜻입니다. 이 기능은
    장문 컨텍스트 과금(API 키 과금 또는
    Extra Usage가 활성화된 OpenClaw Claude-login 경로)에 적합한
    자격 증명에서만 작동합니다.

    팁: provider가 rate-limited 상태여도 OpenClaw가 계속 응답할 수 있도록 **fallback model**을 설정하세요.
    [Models](/cli/models), [OAuth](/concepts/oauth),
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context)를 참조하세요.

  </Accordion>

  <Accordion title="AWS Bedrock을 지원하나요?">
    예. OpenClaw에는 번들된 **Amazon Bedrock (Converse)** provider가 있습니다. AWS env 마커가 있으면 OpenClaw가 streaming/text Bedrock 카탈로그를 자동으로 검색하여 암시적 `amazon-bedrock` provider로 병합할 수 있습니다. 그렇지 않다면 `plugins.entries.amazon-bedrock.config.discovery.enabled`를 명시적으로 활성화하거나 수동 provider 항목을 추가할 수 있습니다. [Amazon Bedrock](/providers/bedrock) 및 [Model providers](/providers/models)를 참조하세요. 관리형 키 흐름을 선호한다면 Bedrock 앞단의 OpenAI 호환 proxy도 유효한 선택지입니다.
  </Accordion>

  <Accordion title="Codex 인증은 어떻게 동작하나요?">
    OpenClaw는 OAuth(ChatGPT 로그인)를 통해 **OpenAI Code (Codex)**를 지원합니다. 온보딩에서 OAuth 흐름을 실행할 수 있으며, 적절한 경우 기본 모델을 `openai-codex/gpt-5.4`로 설정합니다. [Model providers](/concepts/model-providers) 및 [Onboarding (CLI)](/ko/start/wizard)를 참조하세요.
  </Accordion>

  <Accordion title="OpenAI 구독 인증(Codex OAuth)을 지원하나요?">
    예. OpenClaw는 **OpenAI Code (Codex) 구독 OAuth**를 완전히 지원합니다.
    OpenAI는 OpenClaw 같은 외부 도구/워크플로에서 구독 OAuth 사용을 명시적으로 허용합니다.
    온보딩이 OAuth 흐름을 실행해 줄 수 있습니다.

    [OAuth](/concepts/oauth), [Model providers](/concepts/model-providers), [Onboarding (CLI)](/ko/start/wizard)를 참조하세요.

  </Accordion>

  <Accordion title="Gemini CLI OAuth는 어떻게 설정하나요?">
    Gemini CLI는 `openclaw.json`에 client id 또는 secret을 넣는 방식이 아니라 **plugin auth flow**를 사용합니다.

    단계:

    1. `gemini`가 `PATH`에 있도록 Gemini CLI를 로컬에 설치
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. plugin 활성화: `openclaw plugins enable google`
    3. 로그인: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. 로그인 후 기본 모델: `google-gemini-cli/gemini-3.1-pro-preview`
    5. 요청이 실패하면 gateway 호스트에 `GOOGLE_CLOUD_PROJECT` 또는 `GOOGLE_CLOUD_PROJECT_ID`를 설정

    이렇게 하면 OAuth 토큰이 gateway 호스트의 auth profiles에 저장됩니다. 자세한 내용: [Model providers](/concepts/model-providers).

  </Accordion>

  <Accordion title="가벼운 잡담용으로 로컬 모델을 써도 괜찮나요?">
    보통은 아닙니다. OpenClaw는 큰 컨텍스트 + 강한 안전성이 필요하며, 작은 카드에서는 잘림과 누수가 발생합니다. 꼭 써야 한다면 로컬에서 실행 가능한 **가장 큰** 모델 빌드(LM Studio)를 사용하고 [/gateway/local-models](/gateway/local-models)를 확인하세요. 더 작거나 quantized된 모델은 prompt injection 위험을 높입니다 - [Security](/gateway/security)를 참조하세요.
  </Accordion>

  <Accordion title="호스팅된 모델 트래픽을 특정 리전에 유지하려면 어떻게 해야 하나요?">
    리전이 고정된 엔드포인트를 선택하세요. OpenRouter는 MiniMax, Kimi, GLM에 대해 미국 호스팅 옵션을 제공하므로, 리전 내에 데이터를 유지하려면 미국 호스팅 변형을 선택하세요. 선택한 리전 provider를 유지하면서도 Anthropic/OpenAI를 함께 나열하려면 `models.mode: "merge"`를 사용해 fallbacks를 계속 사용할 수 있습니다.
  </Accordion>

  <Accordion title="이걸 설치하려면 Mac Mini를 사야 하나요?">
    아니요. OpenClaw는 macOS 또는 Linux(Windows는 WSL2 경유)에서 실행됩니다. Mac mini는 선택 사항입니다.
    항상 켜진 호스트로 Mac mini를 구매하는 사람도 있지만, 작은 VPS, 홈 서버, Raspberry Pi급 장치도 작동합니다.

    **macOS 전용 도구**가 필요할 때만 Mac이 필요합니다. iMessage는 [BlueBubbles](/channels/bluebubbles) 사용을 권장합니다 - BlueBubbles 서버는 어떤 Mac에서도 실행되며, Gateway는 Linux나 다른 곳에서 실행할 수 있습니다. 다른 macOS 전용 도구가 필요하다면 Gateway를 Mac에서 실행하거나 macOS node를 페어링하세요.

    문서: [BlueBubbles](/channels/bluebubbles), [Nodes](/nodes), [Mac remote mode](/platforms/mac/remote).

  </Accordion>

  <Accordion title="iMessage 지원에 Mac mini가 필요한가요?">
    Messages에 로그인된 **어떤 macOS 기기든** 필요합니다. Mac mini일 필요는 없습니다.
    iMessage에는 **[BlueBubbles](/channels/bluebubbles)**를 권장합니다. BlueBubbles 서버는 macOS에서 실행되고, Gateway는 Linux나 다른 곳에서 실행할 수 있습니다.

    일반적인 설정:

    - Gateway는 Linux/VPS에서 실행하고, BlueBubbles 서버는 Messages에 로그인된 Mac에서 실행.
    - 가장 단순한 단일 머신 설정을 원하면 모든 것을 Mac에서 실행.

    문서: [BlueBubbles](/channels/bluebubbles), [Nodes](/nodes),
    [Mac remote mode](/platforms/mac/remote).

  </Accordion>

  <Accordion title="OpenClaw 실행용으로 Mac mini를 사면 MacBook Pro에서 연결할 수 있나요?">
    예. **Mac mini가 Gateway를 실행**하고, MacBook Pro는
    **node**(companion device)로 연결할 수 있습니다. nodes는 Gateway를 실행하지 않으며 -
    해당 기기에서 screen/camera/canvas와 `system.run` 같은 추가 기능을 제공합니다.

    일반적인 패턴:

    - Gateway는 Mac mini에서 실행(항상 켜짐).
    - MacBook Pro는 macOS 앱이나 node host를 실행하고 Gateway에 페어링.
    - 확인은 `openclaw nodes status` / `openclaw nodes list`.

    문서: [Nodes](/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Bun을 써도 되나요?">
    Bun은 **권장하지 않습니다**. 특히 WhatsApp과 Telegram에서 런타임 버그가 보입니다.
    안정적인 gateway에는 **Node**를 사용하세요.

    그래도 Bun을 실험하고 싶다면, WhatsApp/Telegram이 없는 비프로덕션 gateway에서만 사용하세요.

  </Accordion>

  <Accordion title="Telegram: allowFrom에는 무엇이 들어가나요?">
    `channels.telegram.allowFrom`은 **사람 사용자의 Telegram user ID**(숫자)입니다. 봇 username이 아닙니다.

    온보딩은 `@username` 입력을 받아 숫자 ID로 확인할 수 있지만, OpenClaw 인증은 숫자 ID만 사용합니다.

    더 안전한 방법(서드파티 봇 없음):

    - 봇에 DM을 보낸 뒤 `openclaw logs --follow`를 실행하고 `from.id`를 읽으세요.

    공식 Bot API:

    - 봇에 DM을 보낸 뒤 `https://api.telegram.org/bot<bot_token>/getUpdates`를 호출하고 `message.from.id`를 읽으세요.

    서드파티(프라이버시 낮음):

    - `@userinfobot` 또는 `@getidsbot`에 DM.

    [/channels/telegram](/channels/telegram#access-control-and-activation)을 참조하세요.

  </Accordion>

  <Accordion title="한 WhatsApp 번호를 여러 사람이 서로 다른 OpenClaw 인스턴스로 사용할 수 있나요?">
    예. **다중 에이전트 라우팅**으로 가능합니다. 각 발신자의 WhatsApp **DM**(peer `kind: "direct"`, 발신자 E.164 예: `+15551234567`)을 서로 다른 `agentId`에 바인딩하면 각 사람이 자기만의 workspace와 session store를 갖게 됩니다. 응답은 여전히 **같은 WhatsApp account**에서 오며, DM 액세스 제어(`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`)는 WhatsApp account 전체에 대해 전역입니다. [Multi-Agent Routing](/concepts/multi-agent) 및 [WhatsApp](/channels/whatsapp)을 참조하세요.
  </Accordion>

  <Accordion title='빠른 채팅용 에이전트와 코딩용 Opus 에이전트를 따로 운영할 수 있나요?'>
    예. 다중 에이전트 라우팅을 사용하세요. 각 에이전트에 서로 다른 기본 모델을 주고, 그다음 수신 경로(provider account 또는 특정 peers)를 각 에이전트에 바인딩하면 됩니다. 예시 config는 [Multi-Agent Routing](/concepts/multi-agent)에 있습니다. [Models](/concepts/models) 및 [Configuration](/gateway/configuration)도 참조하세요.
  </Accordion>

  <Accordion title="Linux에서 Homebrew가 작동하나요?">
    예. Homebrew는 Linux(Linuxbrew)를 지원합니다. 빠른 설정:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    systemd를 통해 OpenClaw를 실행하는 경우, 서비스 PATH에 `/home/linuxbrew/.linuxbrew/bin`(또는 brew prefix)이 포함되어 있어야 `brew`로 설치한 도구가 non-login shell에서도 확인됩니다.
    최근 빌드는 Linux systemd services에서 일반적인 사용자 bin dirs(예: `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`)도 미리 prepend하며, 설정된 경우 `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR`, `FNM_DIR`도 존중합니다.

  </Accordion>

  <Accordion title="해킹 가능한 git 설치와 npm install의 차이는 무엇인가요?">
    - **해킹 가능한(git) 설치:** 전체 소스 체크아웃, 수정 가능, 기여자에게 가장 적합.
      로컬에서 빌드하고 코드/문서를 패치할 수 있습니다.
    - **npm install:** 전역 CLI 설치, 리포지토리 없음, "그냥 실행"에 가장 적합.
      업데이트는 npm dist-tags에서 옵니다.

    문서: [Getting started](/ko/start/getting-started), [Updating](/install/updating).

  </Accordion>

  <Accordion title="나중에 npm 설치와 git 설치 사이를 전환할 수 있나요?">
    예. 다른 방식으로 설치한 뒤 Doctor를 실행해 gateway 서비스가 새 entrypoint를 가리키게 하세요.
    이렇게 해도 **데이터는 삭제되지 않습니다** - OpenClaw 코드 설치만 바뀝니다. 상태
    (`~/.openclaw`)와 workspace(`~/.openclaw/workspace`)는 그대로 유지됩니다.

    npm에서 git로:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    git에서 npm으로:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor는 gateway service entrypoint 불일치를 감지하고 현재 설치와 일치하도록 서비스 config를 다시 쓰도록 제안합니다(자동화에서는 `--repair` 사용).

    백업 팁: [Backup strategy](#디스크에서-파일이-저장되는-위치)를 참조하세요.

  </Accordion>

  <Accordion title="Gateway는 노트북에서 실행하는 게 좋나요, VPS에서 실행하는 게 좋나요?">
    짧게 답하면: **24/7 신뢰성이 중요하다면 VPS를 쓰세요**. 가장 마찰이 적은 환경이 좋고 절전/재시작을 감수할 수 있다면 로컬에서 실행하세요.

    **노트북(로컬 Gateway)**

    - **장점:** 서버 비용 없음, 로컬 파일 직접 접근, 보이는 브라우저 창.
    - **단점:** 절전/네트워크 끊김 = 연결 끊김, OS 업데이트/재부팅으로 중단, 깨어 있어야 함.

    **VPS / 클라우드**

    - **장점:** 항상 켜짐, 안정적인 네트워크, 노트북 절전 문제 없음, 계속 실행 유지가 쉬움.
    - **단점:** 보통 headless로 실행(스크린샷 사용), 원격 파일 접근만 가능, 업데이트 시 SSH 필요.

    **OpenClaw 관련 참고:** WhatsApp/Telegram/Slack/Mattermost/Discord는 모두 VPS에서 잘 동작합니다. 실제 차이는 **headless browser** 대 보이는 창 정도입니다. [Browser](/tools/browser)를 참조하세요.

    **권장 기본값:** 이전에 gateway 연결 끊김을 겪었다면 VPS. Mac을 적극적으로 사용하고 있고 로컬 파일 접근이나 보이는 브라우저로 UI 자동화를 원한다면 로컬도 매우 좋습니다.

  </Accordion>

  <Accordion title="OpenClaw를 전용 머신에서 실행하는 것이 얼마나 중요한가요?">
    필수는 아니지만, **신뢰성과 격리를 위해 권장**됩니다.

    - **전용 호스트(VPS/Mac mini/Pi):** 항상 켜짐, 절전/재부팅 중단이 적음, 권한이 더 깔끔함, 계속 실행 유지가 쉬움.
    - **공유 노트북/데스크톱:** 테스트와 적극적 사용에는 충분하지만, 머신이 절전하거나 업데이트될 때 중단을 예상해야 합니다.

    두 장점을 모두 원한다면 Gateway는 전용 호스트에 두고 노트북은 로컬 screen/camera/exec 도구용 **node**로 페어링하세요. [Nodes](/nodes)를 참조하세요.
    보안 가이드는 [Security](/gateway/security)를 읽어보세요.

  </Accordion>

  <Accordion title="최소 VPS 요구 사항과 권장 OS는 무엇인가요?">
    OpenClaw는 가볍습니다. 기본 Gateway + 채팅 채널 하나 기준:

    - **절대 최소:** 1 vCPU, 1GB RAM, 약 500MB 디스크.
    - **권장:** 여유 공간(logs, media, 여러 채널)을 위해 1-2 vCPU, 2GB RAM 이상. Node 도구와 browser 자동화는 리소스를 많이 쓸 수 있습니다.

    OS는 **Ubuntu LTS**(또는 최신 Debian/Ubuntu)를 사용하세요. Linux 설치 경로는 그 환경에서 가장 잘 검증되어 있습니다.

    문서: [Linux](/platforms/linux), [VPS hosting](/vps).

  </Accordion>

  <Accordion title="VM에서 OpenClaw를 실행할 수 있나요? 요구 사항은 무엇인가요?">
    예. VM은 VPS와 동일하게 취급하세요. 항상 켜져 있고, 도달 가능해야 하며,
    Gateway와 활성화한 채널을 처리할 충분한 RAM이 있어야 합니다.

    기본 가이드:

    - **절대 최소:** 1 vCPU, 1GB RAM.
    - **권장:** 여러 채널, browser 자동화, media 도구를 실행한다면 2GB RAM 이상.
    - **OS:** Ubuntu LTS 또는 다른 최신 Debian/Ubuntu.

    Windows라면 **WSL2가 가장 쉬운 VM 스타일 설정**이며 도구 호환성도 가장 좋습니다.
    [Windows](/platforms/windows), [VPS hosting](/vps)를 참조하세요.
    VM에서 macOS를 실행하는 경우 [macOS VM](/install/macos-vm)을 참조하세요.

  </Accordion>
</AccordionGroup>

## OpenClaw란 무엇인가요?

<AccordionGroup>
  <Accordion title="OpenClaw를 한 문단으로 설명하면?">
    OpenClaw는 자신의 디바이스에서 실행하는 개인 AI 비서입니다. 이미 사용하는 메시징 표면(WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat 및 QQ Bot 같은 번들 채널 plugins)에서 응답하며, 지원되는 플랫폼에서는 voice + 라이브 Canvas도 제공합니다. **Gateway**는 항상 켜져 있는 컨트롤 플레인이며, 어시스턴트가 실제 제품입니다.
  </Accordion>

  <Accordion title="가치 제안">
    OpenClaw는 단순한 "Claude wrapper"가 아닙니다. **로컬 우선 컨트롤 플레인**으로서
    자신이 원하는 하드웨어에서 강력한 어시스턴트를 실행하고,
    이미 쓰는 채팅 앱에서 접근할 수 있으며,
    상태 있는 세션, 메모리, 도구를 제공하면서도 워크플로 제어권을 호스팅 SaaS에 넘기지 않습니다.

    핵심 특징:

    - **당신의 디바이스, 당신의 데이터:** Gateway를 원하는 곳(Mac, Linux, VPS)에 실행하고
      workspace + 세션 기록을 로컬에 유지.
    - **웹 샌드박스가 아닌 실제 채널:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage 등,
      그리고 지원되는 플랫폼의 모바일 voice 및 Canvas.
    - **모델 독립적:** Anthropic, OpenAI, MiniMax, OpenRouter 등을 에이전트별 라우팅과
      failover와 함께 사용.
    - **로컬 전용 옵션:** 원한다면 로컬 모델을 실행해 **모든 데이터를 디바이스에 둘 수 있음**.
    - **다중 에이전트 라우팅:** 채널, account, 작업별로 별도 에이전트를 두고 각자 자신의
      workspace와 기본값을 가짐.
    - **오픈 소스 + 해킹 가능:** vendor lock-in 없이 직접 검사, 확장, self-host 가능.

    문서: [Gateway](/gateway), [Channels](/channels), [Multi-agent](/concepts/multi-agent),
    [Memory](/concepts/memory).

  </Accordion>

  <Accordion title="방금 설정했습니다. 먼저 무엇을 해보면 좋을까요?">
    좋은 첫 프로젝트 예시:

    - 웹사이트 만들기(WordPress, Shopify 또는 간단한 정적 사이트).
    - 모바일 앱 프로토타입 만들기(개요, 화면, API 계획).
    - 파일과 폴더 정리(정리, 이름 규칙, 태깅).
    - Gmail 연결 후 요약이나 follow up 자동화.

    큰 작업도 처리할 수 있지만, 단계를 나누고
    병렬 작업에는 sub agents를 사용할 때 가장 잘 동작합니다.

  </Accordion>

  <Accordion title="OpenClaw의 일상적인 상위 5가지 사용 사례는 무엇인가요?">
    일상적인 승리는 보통 다음과 같습니다:

    - **개인 브리핑:** 받은편지함, 일정, 관심 있는 뉴스 요약.
    - **리서치와 초안 작성:** 빠른 조사, 요약, 이메일이나 문서의 초안.
    - **리마인더와 후속 작업:** cron 또는 heartbeat 기반 nudges와 체크리스트.
    - **브라우저 자동화:** 폼 채우기, 데이터 수집, 반복적인 웹 작업.
    - **기기 간 조정:** 휴대폰에서 작업을 보내고, Gateway가 서버에서 실행한 뒤, 결과를 채팅으로 돌려받기.

  </Accordion>

  <Accordion title="OpenClaw로 SaaS의 리드 생성, 아웃리치, 광고, 블로그를 도울 수 있나요?">
    **조사, 적합성 판단, 초안 작성**에는 예입니다. 사이트를 스캔하고, 짧은 후보 목록을 만들고,
    잠재 고객을 요약하고, 아웃리치나 광고 문구 초안을 작성할 수 있습니다.

    **아웃리치나 광고 집행**에는 사람이 중간에 있어야 합니다. 스팸을 피하고, 현지 법률과
    플랫폼 정책을 따르며, 발송 전 모든 내용을 검토하세요. 가장 안전한 패턴은
    OpenClaw가 초안을 작성하고 당신이 승인하는 것입니다.

    문서: [Security](/gateway/security).

  </Accordion>

  <Accordion title="웹 개발에서 Claude Code와 비교한 장점은 무엇인가요?">
    OpenClaw는 IDE 대체제가 아니라 **개인 비서**이자 조정 계층입니다.
    리포지토리 안에서 가장 빠른 직접 코딩 루프가 필요하면 Claude Code나 Codex를 사용하세요. 지속적인 메모리, 크로스 디바이스 접근, 도구 오케스트레이션이 필요하면 OpenClaw를 사용하세요.

    장점:

    - 세션 전반에 걸친 **지속적인 메모리 + workspace**
    - **다중 플랫폼 접근**(WhatsApp, Telegram, TUI, WebChat)
    - **도구 오케스트레이션**(browser, files, scheduling, hooks)
    - **항상 켜진 Gateway**(VPS에서 실행하고 어디서나 상호작용)
    - 로컬 browser/screen/camera/exec를 위한 **Nodes**

    쇼케이스: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills 및 자동화

<AccordionGroup>
  <Accordion title="리포지토리를 dirty 상태로 유지하지 않고 skills를 커스터마이즈하려면 어떻게 하나요?">
    리포지토리 사본을 직접 편집하는 대신 관리형 override를 사용하세요. 변경 사항은 `~/.openclaw/skills/<name>/SKILL.md`에 두거나(`~/.openclaw/openclaw.json`의 `skills.load.extraDirs`로 폴더를 추가해도 됨) 관리하세요. 우선순위는 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` 이므로, 관리형 override는 git을 건드리지 않고도 bundled skills보다 우선합니다. skill을 전역으로 설치하되 일부 agents에게만 보이게 하려면 공유 사본은 `~/.openclaw/skills`에 두고 `agents.defaults.skills`와 `agents.list[].skills`로 가시성을 제어하세요. upstream에 기여할 가치가 있는 수정만 리포지토리에 두고 PR로 보내세요.
  </Accordion>

  <Accordion title="커스텀 폴더에서 skills를 로드할 수 있나요?">
    예. `~/.openclaw/openclaw.json`의 `skills.load.extraDirs`를 통해 추가 디렉터리를 넣을 수 있습니다(가장 낮은 우선순위). 기본 우선순위는 `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bundled → `skills.load.extraDirs` 입니다. `clawhub` 설치는 기본적으로 `./skills`에 설치되며, OpenClaw는 다음 세션에서 이를 `<workspace>/skills`로 취급합니다. 특정 agents에게만 보이게 하려면 `agents.defaults.skills` 또는 `agents.list[].skills`와 함께 사용하세요.
  </Accordion>

  <Accordion title="작업별로 다른 모델을 사용하려면 어떻게 하나요?">
    현재 지원되는 패턴은 다음과 같습니다:

    - **Cron jobs**: 격리된 작업에 작업별 `model` override 설정
    - **Sub-agents**: 서로 다른 기본 모델을 가진 별도 에이전트로 작업 라우팅
    - **온디맨드 전환**: 현재 세션 모델을 언제든 `/model`로 전환

    [Cron jobs](/automation/cron-jobs), [Multi-Agent Routing](/concepts/multi-agent), [Slash commands](/tools/slash-commands)를 참조하세요.

  </Accordion>

  <Accordion title="무거운 작업을 하는 동안 봇이 멈춥니다. 어떻게 분산하나요?">
    길거나 병렬인 작업에는 **sub-agents**를 사용하세요. Sub-agents는 자체 세션에서 실행되며,
    요약을 반환하고, 메인 채팅이 계속 응답하도록 유지합니다.

    봇에게 "이 작업을 위해 sub-agent를 생성해 줘"라고 하거나 `/subagents`를 사용하세요.
    채팅에서 `/status`를 사용하면 지금 Gateway가 무엇을 하고 있는지(그리고 바쁜지)를 볼 수 있습니다.

    토큰 팁: 긴 작업과 sub-agents는 모두 토큰을 소비합니다. 비용이 걱정된다면
    `agents.defaults.subagents.model`을 통해 sub-agents용 더 저렴한 모델을 설정하세요.

    문서: [Sub-agents](/tools/subagents), [Background Tasks](/automation/tasks).

  </Accordion>

  <Accordion title="Discord에서 스레드 바인딩된 subagent 세션은 어떻게 동작하나요?">
    thread bindings를 사용하세요. Discord 스레드를 subagent 또는 세션 대상에 바인딩하여, 그 스레드의 후속 메시지가 그 바인딩된 세션에 계속 머물게 할 수 있습니다.

    기본 흐름:

    - `sessions_spawn`을 `thread: true`(그리고 선택적으로 지속 follow-up을 위한 `mode: "session"`)와 함께 실행.
    - 또는 `/focus <target>`으로 수동 바인딩.
    - `/agents`로 바인딩 상태 검사.
    - `/session idle <duration|off>` 및 `/session max-age <duration|off>`로 자동 unfocus 제어.
    - `/unfocus`로 스레드 분리.

    필요한 config:

    - 전역 기본값: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Discord 재정의: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - 생성 시 자동 바인드: `channels.discord.threadBindings.spawnSubagentSessions: true` 설정.

    문서: [Sub-agents](/tools/subagents), [Discord](/channels/discord), [Configuration Reference](/gateway/configuration-reference), [Slash commands](/tools/slash-commands).

  </Accordion>

  <Accordion title="subagent가 끝났는데 완료 업데이트가 잘못된 곳으로 가거나 게시되지 않았습니다. 무엇을 확인해야 하나요?">
    먼저 확인된 requester 경로를 확인하세요:

    - completion-mode subagent 전달은 존재할 경우 바인딩된 스레드나 대화 경로를 우선합니다.
    - completion origin에 채널만 있는 경우, OpenClaw는 requester 세션의 저장된 경로(`lastChannel` / `lastTo` / `lastAccountId`)로 폴백하므로 직접 전달이 여전히 성공할 수 있습니다.
    - 바인딩된 경로나 사용할 수 있는 저장 경로가 모두 없으면 직접 전달이 실패하고, 즉시 채팅에 게시하는 대신 queued session delivery로 폴백할 수 있습니다.
    - 유효하지 않거나 오래된 대상은 여전히 queue fallback 또는 최종 전달 실패를 유발할 수 있습니다.
    - 자식의 마지막 표시 가능한 assistant 응답이 정확히 `NO_REPLY` / `no_reply`, 또는 정확히 `ANNOUNCE_SKIP`라면, OpenClaw는 오래된 진행 상황을 게시하는 대신 announce를 의도적으로 억제합니다.
    - 자식이 tool call만 실행한 뒤 타임아웃되면, announce는 원시 도구 출력을 재생하는 대신 짧은 부분 진행 요약으로 축약될 수 있습니다.

    디버그:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    문서: [Sub-agents](/tools/subagents), [Background Tasks](/automation/tasks), [Session Tools](/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron 또는 리마인더가 실행되지 않습니다. 무엇을 확인해야 하나요?">
    Cron은 Gateway 프로세스 내부에서 실행됩니다. Gateway가 계속 실행 중이 아니면
    예약 작업은 실행되지 않습니다.

    체크리스트:

    - cron이 활성화되어 있는지(`cron.enabled`)와 `OPENCLAW_SKIP_CRON`이 설정되지 않았는지 확인.
    - Gateway가 24/7 실행 중인지 확인(절전/재시작 없음).
    - 작업의 시간대 설정 확인(`--tz` 대 호스트 시간대).

    디버그:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    문서: [Cron jobs](/automation/cron-jobs), [Automation & Tasks](/automation).

  </Accordion>

  <Accordion title="Cron이 실행되었지만 채널로 아무것도 보내지지 않았습니다. 왜 그런가요?">
    먼저 전달 모드를 확인하세요:

    - `--no-deliver` / `delivery.mode: "none"`이면 외부 메시지는 예상되지 않습니다.
    - announce 대상(`channel` / `to`)이 없거나 유효하지 않으면 러너가 아웃바운드 전달을 건너뜁니다.
    - 채널 인증 실패(`unauthorized`, `Forbidden`)는 러너가 전달을 시도했지만 자격 증명이 막았다는 뜻입니다.
    - 조용한 격리 결과(`NO_REPLY` / `no_reply`만 존재)는 의도적으로 전달 불가로 처리되므로, 러너는 queued fallback delivery도 억제합니다.

    격리 cron 작업에서는 러너가 최종 전달을 소유합니다. 에이전트는 러너가 보낼 일반 텍스트 요약을 반환해야 합니다. `--no-deliver`는
    그 결과를 내부에만 유지하며, message tool로
    에이전트가 직접 보내게 하지는 않습니다.

    디버그:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    문서: [Cron jobs](/automation/cron-jobs), [Background Tasks](/automation/tasks).

  </Accordion>

  <Accordion title="격리된 cron 실행이 왜 모델을 바꾸거나 한 번 재시도했나요?">
    보통은 중복 스케줄링이 아니라 라이브 모델 전환 경로입니다.

    격리 cron은 활성 실행이 `LiveSessionModelSwitchError`를 던질 때 런타임 모델 handoff를 저장하고 재시도할 수 있습니다. 재시도는 전환된
    provider/model을 유지하며, 전환에 새 auth profile override가 포함되어 있었다면 cron은
    재시도 전에 그것도 저장합니다.

    관련 선택 규칙:

    - 해당되는 경우 Gmail hook 모델 override가 먼저 우선.
    - 그다음 작업별 `model`.
    - 그다음 저장된 cron-session 모델 override.
    - 그다음 일반 agent/default 모델 선택.

    재시도 루프는 제한됩니다. 초기 시도 + 2회의 switch retry 이후에는
    cron이 무한 루프 대신 중단합니다.

    디버그:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    문서: [Cron jobs](/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Linux에서 skills는 어떻게 설치하나요?">
    네이티브 `openclaw skills` 명령을 사용하거나 skills를 workspace에 넣으세요. macOS Skills UI는 Linux에서 사용할 수 없습니다.
    skills 탐색: [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    네이티브 `openclaw skills install`은 활성 workspace의 `skills/`
    디렉터리에 기록합니다. 별도의 `clawhub` CLI는 자신의 skills를 게시하거나
    동기화하고 싶을 때만 설치하세요. 여러 agents 간 공유 설치를 원하면
    skill을 `~/.openclaw/skills` 아래에 두고,
    어떤 agents가 볼 수 있을지 제한하려면 `agents.defaults.skills` 또는
    `agents.list[].skills`를 사용하세요.

  </Accordion>

  <Accordion title="OpenClaw가 백그라운드에서 예약 작업이나 연속 작업을 실행할 수 있나요?">
    예. Gateway 스케줄러를 사용하세요:

    - **Cron jobs**: 예약 또는 반복 작업(재시작 후에도 유지).
    - **Heartbeat**: "main session" 주기적 확인.
    - **Isolated jobs**: 요약을 게시하거나 채팅으로 전달하는 자율 에이전트.

    문서: [Cron jobs](/automation/cron-jobs), [Automation & Tasks](/automation),
    [Heartbeat](/gateway/heartbeat).

  </Accordion>

  <Accordion title="Linux에서 Apple macOS 전용 skills를 실행할 수 있나요?">
    직접적으로는 불가능합니다. macOS skills는 `metadata.openclaw.os`와 필요한 바이너리로 게이팅되며, skills는 **Gateway 호스트**에서 적격할 때만 시스템 프롬프트에 나타납니다. Linux에서는 `darwin` 전용 skills(`apple-notes`, `apple-reminders`, `things-mac` 등)는 게이팅을 재정의하지 않으면 로드되지 않습니다.

    지원되는 패턴은 세 가지입니다:

    **옵션 A - Mac에서 Gateway 실행(가장 단순).**
    macOS 바이너리가 존재하는 곳에서 Gateway를 실행하고, Linux에서는 [remote mode](#gateway-포트가-이미-실행-중이고-remote-mode를-사용하는-경우) 또는 Tailscale로 연결하세요. Gateway 호스트가 macOS이므로 skills가 정상적으로 로드됩니다.

    **옵션 B - macOS node 사용(SSH 없음).**
    Gateway는 Linux에서 실행하고, macOS node(menubar 앱)를 페어링한 뒤 **Node Run Commands**를 "Always Ask" 또는 "Always Allow"로 설정하세요. 필요한 바이너리가 node에 있으면 OpenClaw는 macOS 전용 skills를 적격한 것으로 취급할 수 있습니다. 에이전트는 `nodes` 도구를 통해 해당 skills를 실행합니다. "Always Ask"를 선택한 경우 프롬프트에서 "Always Allow"를 승인하면 그 명령이 allowlist에 추가됩니다.

    **옵션 C - SSH로 macOS 바이너리 프록시(고급).**
    Gateway는 Linux에 두고, 필요한 CLI 바이너리가 Mac에서 실행되는 SSH wrapper로 확인되게 하세요. 그런 다음 skill을 Linux에서도 허용하도록 override하면 적격 상태를 유지할 수 있습니다.

    1. 바이너리용 SSH wrapper를 만듭니다(예: Apple Notes용 `memo`):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. wrapper를 Linux 호스트의 `PATH`에 넣습니다(예: `~/bin/memo`).
    3. skill 메타데이터를 override하여 Linux를 허용합니다(workspace 또는 `~/.openclaw/skills`):

       ```markdown
       ---
       name: apple-notes
       description: Manage Apple Notes via the memo CLI on macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. 새 세션을 시작해 skills 스냅샷을 새로 고칩니다.

  </Accordion>

  <Accordion title="Notion 또는 HeyGen 통합이 있나요?">
    현재 내장되어 있지는 않습니다.

    옵션:

    - **Custom skill / plugin:** 안정적인 API 접근에 가장 적합(Notion/HeyGen 모두 API 보유).
    - **Browser 자동화:** 코드 없이 가능하지만 더 느리고 깨지기 쉽습니다.

    클라이언트별 컨텍스트(에이전시 워크플로)를 유지하려면 단순한 패턴은 다음과 같습니다:

    - 클라이언트당 Notion 페이지 하나(컨텍스트 + 선호도 + 현재 작업).
    - 세션 시작 시 에이전트에게 해당 페이지를 가져오라고 요청.

    네이티브 통합이 필요하면 기능 요청을 열거나
    해당 API를 대상으로 하는 skill을 만들어 보세요.

    skills 설치:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    네이티브 설치는 활성 workspace의 `skills/` 디렉터리에 들어갑니다. 여러 agents가 공유하는 skills는 `~/.openclaw/skills/<name>/SKILL.md`에 두세요. 일부 agents만 공유 설치를 보게 하려면 `agents.defaults.skills` 또는 `agents.list[].skills`를 구성하세요. 일부 skills는 Homebrew로 설치된 바이너리를 기대하는데, Linux에서는 Linuxbrew를 의미합니다(위 Homebrew Linux FAQ 항목 참조). [Skills](/tools/skills), [Skills config](/tools/skills-config), [ClawHub](/tools/clawhub)를 참조하세요.

  </Accordion>

  <Accordion title="이미 로그인된 Chrome을 OpenClaw에서 사용하려면 어떻게 하나요?">
    Chrome DevTools MCP를 통해 연결되는 내장 `user` browser profile을 사용하세요:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    커스텀 이름을 원한다면 명시적인 MCP profile을 만드세요:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    이 경로는 호스트 로컬 전용입니다. Gateway가 다른 곳에서 실행된다면 browser 머신에서 node host를 실행하거나 원격 CDP를 사용하세요.

    `existing-session` / `user`의 현재 제한:

    - 동작은 CSS-selector 기반이 아니라 ref 기반
    - 업로드는 `ref` / `inputRef`가 필요하고 현재 한 번에 하나의 파일만 지원
    - `responsebody`, PDF 내보내기, 다운로드 가로채기, batch actions는 여전히 관리형 browser 또는 raw CDP profile이 필요

  </Accordion>
</AccordionGroup>

## 샌드박싱 및 메모리

<AccordionGroup>
  <Accordion title="전용 샌드박싱 문서가 있나요?">
    예. [Sandboxing](/gateway/sandboxing)을 참조하세요. Docker 전용 설정(전체 gateway를 Docker에서 실행하거나 sandbox images 설정)은 [Docker](/install/docker)를 참조하세요.
  </Accordion>

  <Accordion title="Docker가 제한적으로 느껴집니다. 전체 기능을 활성화하려면 어떻게 하나요?">
    기본 이미지는 보안 우선이며 `node` 사용자로 실행되므로
    시스템 패키지, Homebrew, 번들 browser가 포함되지 않습니다. 더 완전한 설정을 원한다면:

    - 캐시가 유지되도록 `/home/node`를 `OPENCLAW_HOME_VOLUME`으로 영속화.
    - `OPENCLAW_DOCKER_APT_PACKAGES`로 시스템 deps를 이미지에 bake.
    - 번들 CLI로 Playwright browsers 설치:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - `PLAYWRIGHT_BROWSERS_PATH`를 설정하고 해당 경로를 영속화.

    문서: [Docker](/install/docker), [Browser](/tools/browser).

  </Accordion>

  <Accordion title="한 에이전트로 DM은 개인용으로 두고 그룹은 공개/샌드박스 처리할 수 있나요?">
    예 - 비공개 트래픽이 **DMs**이고 공개 트래픽이 **groups**라면 가능합니다.

    `agents.defaults.sandbox.mode: "non-main"`을 사용하면 그룹/채널 세션(non-main keys)은 Docker에서 실행되고, 메인 DM 세션은 호스트에서 유지됩니다. 그다음 `tools.sandbox.tools`로 샌드박스 세션에서 사용할 도구를 제한하세요.

    설정 안내 + 예시 config: [Groups: personal DMs + public groups](/channels/groups#pattern-personal-dms-public-groups-single-agent)

    핵심 config 참조: [Gateway configuration](/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="호스트 폴더를 샌드박스에 bind하려면 어떻게 하나요?">
    `agents.defaults.sandbox.docker.binds`를 `["host:path:mode"]`로 설정하세요(예: `"/home/user/src:/src:ro"`). 전역 + 에이전트별 binds는 병합되며, `scope: "shared"`일 때는 에이전트별 binds가 무시됩니다. 민감한 내용에는 `:ro`를 사용하고, binds는 샌드박스 파일 시스템 벽을 우회한다는 점을 기억하세요.

    OpenClaw는 정규화된 경로와 가장 깊은 기존 상위 경로를 통해 확인된 canonical 경로 둘 다를 기준으로 bind source를 검증합니다. 즉 마지막 경로 세그먼트가 아직 존재하지 않더라도 symlink-parent escape는 fail closed 처리되며, symlink 확인 후에도 allowed-root 검사는 계속 적용됩니다.

    예시와 안전 참고 사항은 [Sandboxing](/gateway/sandboxing#custom-bind-mounts) 및 [Sandbox vs Tool Policy vs Elevated](/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check)를 참조하세요.

  </Accordion>

  <Accordion title="메모리는 어떻게 동작하나요?">
    OpenClaw 메모리는 에이전트 workspace의 Markdown 파일일 뿐입니다:

    - 일일 노트는 `memory/YYYY-MM-DD.md`
    - 선별된 장기 노트는 `MEMORY.md`(main/private 세션 전용)

    OpenClaw는 또한 자동 compaction 전에
    모델에게 내구성 있는 노트를 기록하도록 상기시키는 **조용한 pre-compaction memory flush**를 실행합니다. 이 작업은 workspace에 쓰기가 가능할 때만 실행되며
    (읽기 전용 샌드박스에서는 건너뜀). [Memory](/concepts/memory)를 참조하세요.

  </Accordion>

  <Accordion title="메모리가 자꾸 잊어버립니다. 어떻게 고정하나요?">
    봇에게 **그 사실을 메모리에 쓰라고** 요청하세요. 장기 노트는 `MEMORY.md`에,
    단기 컨텍스트는 `memory/YYYY-MM-DD.md`에 들어가야 합니다.

    이 부분은 아직 개선 중입니다. 모델에게 메모리를 저장하라고 상기시키는 것이 도움이 되며,
    모델은 무엇을 해야 하는지 알고 있습니다. 계속 잊는다면 Gateway가 매번 동일한
    workspace를 사용하고 있는지 확인하세요.

    문서: [Memory](/concepts/memory), [Agent workspace](/concepts/agent-workspace).

  </Accordion>

  <Accordion title="메모리는 영구적으로 유지되나요? 한계는 무엇인가요?">
    메모리 파일은 디스크에 저장되고 삭제할 때까지 유지됩니다. 한계는 모델이 아니라
    저장 공간입니다. 다만 **세션 컨텍스트**는 여전히 모델의
    컨텍스트 창에 제한되므로 긴 대화는 compact 또는 truncate될 수 있습니다. 그래서
    memory search가 존재합니다 - 관련 부분만 다시 컨텍스트로 가져옵니다.

    문서: [Memory](/concepts/memory), [Context](/concepts/context).

  </Accordion>

  <Accordion title="시맨틱 메모리 검색에는 OpenAI API 키가 꼭 필요한가요?">
    **OpenAI embeddings**를 사용할 때만 필요합니다. Codex OAuth는 chat/completions만 다루며
    embeddings 접근 권한은 제공하지 않으므로, **Codex로 로그인해도(OAuth든
    Codex CLI 로그인든)** 시맨틱 메모리 검색에는 도움이 되지 않습니다. OpenAI embeddings에는
    여전히 실제 API 키(`OPENAI_API_KEY` 또는 `models.providers.openai.apiKey`)가 필요합니다.

    provider를 명시적으로 설정하지 않으면 OpenClaw는 API 키를
    확인할 수 있을 때 자동으로 provider를 선택합니다(auth profiles, `models.providers.*.apiKey`, 또는 env vars).
    OpenAI 키를 확인할 수 있으면 OpenAI를 우선하고, 그렇지 않으면 Gemini,
    그다음 Voyage, 그다음 Mistral 순입니다. 원격 키를 사용할 수 없으면
    구성할 때까지 memory search는 비활성화 상태로 유지됩니다. 로컬 모델 경로가
    구성되어 있고 존재하면 OpenClaw는
    `local`을 우선합니다. Ollama는 `memorySearch.provider = "ollama"`를
    명시적으로 설정했을 때 지원됩니다.

    완전히 로컬에 머물고 싶다면 `memorySearch.provider = "local"`(그리고 선택적으로
    `memorySearch.fallback = "none"`)을 설정하세요. Gemini embeddings를 원한다면
    `memorySearch.provider = "gemini"`를 설정하고 `GEMINI_API_KEY`(또는
    `memorySearch.remote.apiKey`)를 제공하세요. 우리는 **OpenAI, Gemini, Voyage, Mistral, Ollama, 또는 local** 임베딩
    모델을 지원합니다 - 설정 세부 사항은 [Memory](/concepts/memory)를 참조하세요.

  </Accordion>
</AccordionGroup>

## 디스크에서 파일이 저장되는 위치

<AccordionGroup>
  <Accordion title="OpenClaw와 함께 사용하는 모든 데이터가 로컬에 저장되나요?">
    아니요 - **OpenClaw의 상태는 로컬**이지만, **외부 서비스는 당신이 보내는 내용을 여전히 볼 수 있습니다**.

    - **기본적으로 로컬:** sessions, memory 파일, config, workspace는 Gateway 호스트에 저장됩니다
      (`~/.openclaw` + workspace 디렉터리).
    - **필연적으로 원격:** 모델 providers(Anthropic/OpenAI 등)에게 보내는 메시지는
      해당 API로 전송되고, 채팅 플랫폼(WhatsApp/Telegram/Slack 등)은 메시지 데이터를
      자체 서버에 저장합니다.
    - **흔적은 스스로 제어:** 로컬 모델을 사용하면 프롬프트는 자신의 머신에 남지만, 채널
      트래픽은 여전히 해당 채널의 서버를 거칩니다.

    관련 문서: [Agent workspace](/concepts/agent-workspace), [Memory](/concepts/memory).

  </Accordion>

  <Accordion title="OpenClaw는 데이터를 어디에 저장하나요?">
    모든 것은 `$OPENCLAW_STATE_DIR`(기본값: `~/.openclaw`) 아래에 있습니다:

    | 경로                                                            | 용도                                                               |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | 메인 config (JSON5)                                                |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | 레거시 OAuth import (처음 사용 시 auth profiles로 복사됨)          |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Auth profiles (OAuth, API keys, 선택적 `keyRef`/`tokenRef` 포함)   |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | `file` SecretRef providers용 선택적 파일 기반 secret payload       |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | 레거시 호환 파일(정적 `api_key` 항목 scrubbed 처리됨)              |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | Provider 상태(예: `whatsapp/<accountId>/creds.json`)               |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | 에이전트별 상태(agentDir + sessions)                               |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | 대화 기록 및 상태(에이전트별)                                      |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | 세션 메타데이터(에이전트별)                                        |

    레거시 단일 에이전트 경로: `~/.openclaw/agent/*` (`openclaw doctor`가 마이그레이션).

    **Workspace**(`AGENTS.md`, 메모리 파일, skills 등)는 별도로 관리되며 `agents.defaults.workspace`로 구성합니다(기본값: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="AGENTS.md / SOUL.md / USER.md / MEMORY.md는 어디에 있어야 하나요?">
    이 파일들은 `~/.openclaw`가 아니라 **에이전트 workspace**에 있어야 합니다.

    - **Workspace(에이전트별)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md`(또는 `MEMORY.md`가 없을 때 레거시 fallback인 `memory.md`),
      `memory/YYYY-MM-DD.md`, 선택적 `HEARTBEAT.md`.
    - **상태 디렉터리(`~/.openclaw`)**: config, channel/provider 상태, auth profiles, sessions, logs,
      공유 skills(`~/.openclaw/skills`).

    기본 workspace는 `~/.openclaw/workspace`이며, 다음으로 구성할 수 있습니다:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    재시작 후 봇이 "잊어버린다"면 Gateway가 매번 동일한
    workspace를 사용하고 있는지 확인하세요(그리고 원격 모드에서는 **gateway 호스트의**
    workspace를 사용하지, 로컬 노트북의 workspace를 사용하는 것이 아니라는 점을 기억하세요).

    팁: 지속적인 동작이나 선호 사항을 원한다면 채팅 기록에 의존하지 말고
    봇에게 **AGENTS.md 또는 MEMORY.md에 쓰도록** 요청하세요.

    [Agent workspace](/concepts/agent-workspace) 및 [Memory](/concepts/memory)를 참조하세요.

  </Accordion>

  <Accordion title="권장 백업 전략">
    **에이전트 workspace**는 **비공개** git 리포지토리에 두고
    비공개 장소(예: GitHub private)에 백업하세요. 이렇게 하면 메모리 + AGENTS/SOUL/USER
    파일이 보존되고, 나중에 어시스턴트의 "마음"을 복원할 수 있습니다.

    `~/.openclaw` 아래의 내용(자격 증명, 세션, 토큰, 암호화된 secret payload)은 **절대 커밋하지 마세요**.
    전체 복원이 필요하다면 workspace와 state directory를
    각각 별도로 백업하세요(위의 마이그레이션 질문 참조).

    문서: [Agent workspace](/concepts/agent-workspace).

  </Accordion>

  <Accordion title="OpenClaw를 완전히 제거하려면 어떻게 하나요?">
    전용 가이드를 참조하세요: [Uninstall](/install/uninstall).
  </Accordion>

  <Accordion title="에이전트가 workspace 밖에서 작업할 수 있나요?">
    예. workspace는 하드 샌드박스가 아니라 **기본 cwd**이자 메모리 기준점입니다.
    상대 경로는 workspace 내부에서 해석되지만, 샌드박싱이 활성화되지 않으면 절대 경로는
    호스트의 다른 위치에도 접근할 수 있습니다. 격리가 필요하다면
    [`agents.defaults.sandbox`](/gateway/sandboxing) 또는 에이전트별 sandbox 설정을 사용하세요. 리포지토리를 기본 작업 디렉터리로 쓰고 싶다면 해당 에이전트의
    `workspace`를 리포지토리 루트로 지정하세요. OpenClaw 리포지토리는 단지 소스 코드일 뿐이므로,
    의도적으로 그 안에서 작업시키려는 경우가 아니라면 workspace는 별도로 두세요.

    예시(리포지토리를 기본 cwd로 사용):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Remote mode에서는 session store가 어디에 있나요?">
    세션 상태는 **gateway 호스트**가 소유합니다. remote mode라면 중요한 session store는 로컬 노트북이 아니라 원격 머신에 있습니다. [Session management](/concepts/session)를 참조하세요.
  </Accordion>
</AccordionGroup>

## Config 기본

<AccordionGroup>
  <Accordion title="config 형식은 무엇이며 어디에 있나요?">
    OpenClaw는 `$OPENCLAW_CONFIG_PATH`(기본값: `~/.openclaw/openclaw.json`)에서 선택적 **JSON5** config를 읽습니다:

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    파일이 없으면 안전한 기본값(기본 workspace `~/.openclaw/workspace` 포함)을 사용합니다.

  </Accordion>

  <Accordion title='gateway.bind: "lan"(또는 "tailnet")을 설정했더니 아무것도 수신하지 않거나 UI가 unauthorized라고 나옵니다'>
    non-loopback bind에는 **유효한 gateway auth 경로**가 필요합니다. 실제로는 다음 중 하나를 의미합니다:

    - 공유 비밀 인증: token 또는 password
    - 올바르게 구성된 non-loopback identity-aware reverse proxy 뒤의 `gateway.auth.mode: "trusted-proxy"`

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    참고:

    - `gateway.remote.token` / `.password`만으로는 로컬 gateway auth가 활성화되지 않습니다.
    - 로컬 호출 경로는 `gateway.auth.*`가 비어 있을 때만 `gateway.remote.*`를 fallback으로 사용할 수 있습니다.
    - password auth를 사용하려면 `gateway.auth.mode: "password"`와 `gateway.auth.password`(또는 `OPENCLAW_GATEWAY_PASSWORD`)를 설정하세요.
    - `gateway.auth.token` / `gateway.auth.password`가 SecretRef로 명시적으로 구성되었지만 확인되지 않으면, 확인은 fail closed 처리됩니다(원격 fallback으로 가려지지 않음).
    - 공유 비밀 Control UI 설정은 `connect.params.auth.token` 또는 `connect.params.auth.password`(앱/UI 설정에 저장됨)로 인증합니다. Tailscale Serve나 `trusted-proxy` 같은 identity-bearing 모드는 대신 요청 헤더를 사용합니다. URL에 공유 비밀을 넣지 마세요.
    - `gateway.auth.mode: "trusted-proxy"`에서는 같은 호스트의 loopback reverse proxy는 여전히 trusted-proxy auth를 충족하지 않습니다. trusted proxy는 구성된 non-loopback 소스여야 합니다.

  </Accordion>

  <Accordion title="왜 이제 localhost에서도 token이 필요한가요?">
    OpenClaw는 loopback을 포함해 기본적으로 gateway auth를 강제합니다. 일반적인 기본 경로에서는 token auth를 의미합니다. 명시적인 auth 경로가 구성되지 않으면 gateway 시작 시 token mode로 확인되고 자동 생성되어 `gateway.auth.token`에 저장되므로, **로컬 WS 클라이언트도 인증해야 합니다**. 이는 다른 로컬 프로세스가 Gateway를 호출하는 것을 막습니다.

    다른 auth 경로를 선호한다면 명시적으로 password mode(또는 non-loopback identity-aware reverse proxy용 `trusted-proxy`)를 선택할 수 있습니다. **정말로** 열린 loopback을 원한다면 config에서 `gateway.auth.mode: "none"`을 명시적으로 설정하세요. Doctor는 언제든 토큰을 생성할 수 있습니다: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="config를 바꾼 뒤 재시작해야 하나요?">
    Gateway는 config를 감시하며 hot-reload를 지원합니다:

    - `gateway.reload.mode: "hybrid"` (기본값): 안전한 변경은 hot-apply, 중요한 변경은 재시작
    - `hot`, `restart`, `off`도 지원

  </Accordion>

  <Accordion title="재미있는 CLI 태그라인을 끄려면 어떻게 하나요?">
    config에서 `cli.banner.taglineMode`를 설정하세요:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: 태그라인 텍스트를 숨기되 배너 제목/버전 줄은 유지.
    - `default`: 항상 `All your chats, one OpenClaw.` 사용.
    - `random`: 순환하는 재미있는/계절성 태그라인(기본 동작).
    - 배너 전체를 보이지 않게 하려면 env `OPENCLAW_HIDE_BANNER=1`을 설정하세요.

  </Accordion>

  <Accordion title="web search(및 web fetch)는 어떻게 활성화하나요?">
    `web_fetch`는 API 키 없이도 동작합니다. `web_search`는 선택한
    provider에 따라 달라집니다:

    - Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity, Tavily 같은 API 기반 provider는 일반적인 API 키 설정이 필요합니다.
    - Ollama Web Search는 키가 필요 없지만 구성된 Ollama 호스트를 사용하며 `ollama signin`이 필요합니다.
    - DuckDuckGo는 키가 필요 없지만 비공식 HTML 기반 통합입니다.
    - SearXNG는 키 없는/self-hosted 방식이며 `SEARXNG_BASE_URL` 또는 `plugins.entries.searxng.config.webSearch.baseUrl`을 구성하세요.

    **권장:** `openclaw configure --section web`을 실행해 provider를 선택하세요.
    환경 변수 대안:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` 또는 `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, 또는 `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` 또는 `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // 선택 사항; 자동 감지를 원하면 생략
            },
          },
        },
    }
    ```

    provider별 web-search config는 이제 `plugins.entries.<plugin>.config.webSearch.*` 아래에 있습니다.
    레거시 `tools.web.search.*` provider 경로는 호환성을 위해 잠시 동안 계속 로드되지만, 새 config에는 사용하지 말아야 합니다.
    Firecrawl web-fetch fallback config는 `plugins.entries.firecrawl.config.webFetch.*` 아래에 있습니다.

    참고:

    - allowlists를 사용한다면 `web_search`/`web_fetch`/`x_search` 또는 `group:web`를 추가하세요.
    - `web_fetch`는 기본적으로 활성화되어 있습니다(명시적으로 비활성화하지 않은 한).
    - `tools.web.fetch.provider`를 생략하면 OpenClaw는 사용 가능한 자격 증명에서 준비된 첫 번째 fetch fallback provider를 자동 감지합니다. 현재 bundled provider는 Firecrawl입니다.
    - 데몬은 `~/.openclaw/.env`(또는 서비스 환경)에서 env vars를 읽습니다.

    문서: [Web tools](/tools/web).

  </Accordion>

  <Accordion title="config.apply가 config를 지워버렸습니다. 어떻게 복구하고 방지하나요?">
    `config.apply`는 **전체 config를 교체**합니다. 부분 객체를 보내면 다른 모든 내용이 제거됩니다.

    복구:

    - 백업(git 또는 복사해 둔 `~/.openclaw/openclaw.json`)에서 복원.
    - 백업이 없다면 `openclaw doctor`를 다시 실행하고 채널/모델을 재구성.
    - 예상치 못한 일이었다면 버그를 제보하고 마지막으로 알고 있는 config나 백업을 포함.
    - 로컬 coding agent는 로그나 기록에서 작동하는 config를 재구성할 수 있는 경우가 많습니다.

    방지:

    - 작은 변경에는 `openclaw config set` 사용.
    - 대화형 편집에는 `openclaw configure` 사용.
    - 정확한 경로나 field 형태가 확실하지 않다면 먼저 `config.schema.lookup` 사용. 드릴다운을 위한 얕은 스키마 노드와 직접 자식 요약을 반환합니다.
    - 부분 RPC 편집에는 `config.patch` 사용, `config.apply`는 전체 config 교체에만 사용.
    - 에이전트 실행에서 owner-only `gateway` tool을 사용 중이라면, 이 도구는 여전히 `tools.exec.ask` / `tools.exec.security`에 대한 쓰기(같은 보호된 exec 경로로 정규화되는 레거시 `tools.bash.*` 별칭 포함)를 거부합니다.

    문서: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/gateway/doctor).

  </Accordion>

  <Accordion title="중앙 Gateway와 디바이스별 전문 workers를 함께 운영하려면 어떻게 하나요?">
    일반적인 패턴은 **하나의 Gateway**(예: Raspberry Pi)와 **nodes** 및 **agents**입니다:

    - **Gateway(중앙):** channels(Signal/WhatsApp), routing, sessions를 소유.
    - **Nodes(디바이스):** Macs/iOS/Android가 주변 장치로 연결되어 로컬 도구(`system.run`, `canvas`, `camera`)를 노출.
    - **Agents(workers):** 특수 역할(예: "Hetzner ops", "Personal data")용 별도 두뇌/workspaces.
    - **Sub-agents:** 메인 agent에서 병렬 작업이 필요할 때 백그라운드 작업 생성.
    - **TUI:** Gateway에 연결해 agents/sessions 전환.

    문서: [Nodes](/nodes), [Remote access](/gateway/remote), [Multi-Agent Routing](/concepts/multi-agent), [Sub-agents](/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="OpenClaw browser는 headless로 실행할 수 있나요?">
    예. config 옵션입니다:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    기본값은 `false`(headful)입니다. Headless는 일부 사이트에서 anti-bot 검사를 더 잘 유발할 수 있습니다. [Browser](/tools/browser)를 참조하세요.

    Headless는 **같은 Chromium 엔진**을 사용하며 대부분의 자동화(폼, 클릭, 스크래핑, 로그인)에 동작합니다. 주요 차이점:

    - 보이는 브라우저 창이 없음(시각적 확인이 필요하면 스크린샷 사용).
    - 일부 사이트는 headless 모드의 자동화에 더 엄격합니다(CAPTCHAs, anti-bot).
      예를 들어 X/Twitter는 headless 세션을 자주 차단합니다.

  </Accordion>

  <Accordion title="브라우저 제어에 Brave를 사용하려면 어떻게 하나요?">
    `browser.executablePath`를 Brave 바이너리(또는 다른 Chromium 기반 브라우저)로 설정하고 Gateway를 재시작하세요.
    전체 config 예시는 [Browser](/tools/browser#use-brave-or-another-chromium-based-browser)를 참조하세요.
  </Accordion>
</AccordionGroup>

## 원격 gateways 및 nodes

<AccordionGroup>
  <Accordion title="Telegram, gateway, nodes 사이에서 명령은 어떻게 전달되나요?">
    Telegram 메시지는 **gateway**가 처리합니다. gateway가 agent를 실행한 다음,
    node 도구가 필요할 때만 **Gateway WebSocket**을 통해 nodes를 호출합니다:

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    nodes는 inbound provider 트래픽을 보지 않으며, node RPC 호출만 받습니다.

  </Accordion>

  <Accordion title="Gateway가 원격에 있을 때 에이전트가 제 컴퓨터에 접근하려면 어떻게 하나요?">
    짧게 답하면: **컴퓨터를 node로 페어링하세요**. Gateway는 다른 곳에서 실행되지만,
    Gateway WebSocket을 통해 로컬 머신의 `node.*` 도구(screen, camera, system)를 호출할 수 있습니다.

    일반적인 설정:

    1. 항상 켜진 호스트(VPS/홈 서버)에서 Gateway 실행.
    2. Gateway 호스트와 컴퓨터를 같은 tailnet에 둠.
    3. Gateway WS에 도달 가능한지 확인(tailnet bind 또는 SSH tunnel).
    4. macOS 앱을 로컬에서 열고 **Remote over SSH** 모드(또는 직접 tailnet)로 연결하여
       node로 등록되게 함.
    5. Gateway에서 node 승인:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    별도의 TCP bridge는 필요 없습니다. nodes는 Gateway WebSocket으로 연결됩니다.

    보안 참고: macOS node를 페어링하면 그 머신에서 `system.run`이 가능해집니다. 신뢰하는 디바이스만
    페어링하고 [Security](/gateway/security)를 검토하세요.

    문서: [Nodes](/nodes), [Gateway protocol](/gateway/protocol), [macOS remote mode](/platforms/mac/remote), [Security](/gateway/security).

  </Accordion>

  <Accordion title="Tailscale은 연결되었지만 응답이 없습니다. 이제 어떻게 하나요?">
    기본 사항 확인:

    - Gateway 실행 중인지: `openclaw gateway status`
    - Gateway 상태: `openclaw status`
    - 채널 상태: `openclaw channels status`

    그다음 인증과 라우팅 확인:

    - Tailscale Serve를 사용한다면 `gateway.auth.allowTailscale`이 올바르게 설정되어 있는지 확인.
    - SSH tunnel로 연결한다면 로컬 터널이 살아 있고 올바른 포트를 가리키는지 확인.
    - allowlists(DM 또는 group)에 자신의 account가 포함되어 있는지 확인.

    문서: [Tailscale](/gateway/tailscale), [Remote access](/gateway/remote), [Channels](/channels).

  </Accordion>

  <Accordion title="두 OpenClaw 인스턴스(local + VPS)가 서로 대화할 수 있나요?">
    예. 내장된 "bot-to-bot" bridge는 없지만, 몇 가지
    신뢰할 수 있는 방식으로 연결할 수 있습니다:

    **가장 단순한 방법:** 두 봇이 모두 접근 가능한 일반 채팅 채널(Telegram/Slack/WhatsApp)을 사용하세요.
    Bot A가 Bot B에 메시지를 보내고, Bot B가 평소처럼 응답하게 하면 됩니다.

    **CLI bridge(범용):** 다른 Gateway에
    `openclaw agent --message ... --deliver`를 호출하는 스크립트를 실행해, 다른 봇이 듣고 있는 채팅을 대상으로 하세요. 한 봇이 원격 VPS에 있다면
    SSH/Tailscale을 통해 그 원격 Gateway를 가리키도록 CLI를 설정하세요([Remote access](/gateway/remote) 참조).

    예시 패턴(대상 Gateway에 도달 가능한 머신에서 실행):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    팁: 두 봇이 무한 루프에 빠지지 않도록 가드레일을 추가하세요(mention-only, 채널
    allowlists, 또는 "bot 메시지에는 응답하지 않기" 규칙).

    문서: [Remote access](/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/tools/agent-send).

  </Accordion>

  <Accordion title="여러 에이전트를 위해 VPS를 따로 여러 개 써야 하나요?">
    아니요. 하나의 Gateway가 여러 에이전트를 호스팅할 수 있으며, 각 에이전트는 자체 workspace, 모델 기본값,
    라우팅을 가집니다. 이것이 일반적인 설정이며,
    에이전트당 VPS 하나를 운영하는 것보다 훨씬 저렴하고 단순합니다.

    하드 격리(보안 경계)나
    공유하고 싶지 않은 매우 다른 configs가 필요한 경우에만 별도 VPS를 사용하세요. 그렇지 않다면 Gateway 하나를 유지하고
    여러 agents 또는 sub-agents를 사용하세요.

  </Accordion>

  <Accordion title="VPS에서 SSH를 쓰는 대신 개인 노트북에 node를 쓰는 이점이 있나요?">
    예 - nodes는 원격 Gateway에서 노트북에 접근하는 일급 방식이며,
    셸 접근 이상을 제공합니다. Gateway는 macOS/Linux(Windows는 WSL2)에서 실행되며
    가볍기 때문에(작은 VPS나 Raspberry Pi급 장치면 충분하고, 4GB RAM이면 넉넉함),
    항상 켜진 호스트 + 노트북을 node로 사용하는 설정이 일반적입니다.

    - **인바운드 SSH 불필요.** Nodes는 Gateway WebSocket으로 밖으로 연결되고 device pairing을 사용합니다.
    - **더 안전한 실행 제어.** `system.run`은 노트북의 node allowlists/approvals로 보호됩니다.
    - **더 많은 디바이스 도구.** Nodes는 `system.run` 외에도 `canvas`, `camera`, `screen`을 노출합니다.
    - **로컬 browser 자동화.** Gateway는 VPS에 두고, 노트북의 node host를 통해 로컬 Chrome을 실행하거나, Chrome MCP를 통해 호스트의 로컬 Chrome에 연결할 수 있습니다.

    SSH는 일시적인 셸 접근에는 괜찮지만, 지속적인 에이전트 워크플로와
    디바이스 자동화에는 nodes가 더 단순합니다.

    문서: [Nodes](/nodes), [Nodes CLI](/cli/nodes), [Browser](/tools/browser).

  </Accordion>

  <Accordion title="nodes가 gateway 서비스를 실행하나요?">
    아니요. 의도적으로 격리된 profiles를 실행하는 경우가 아니라면 호스트당 **하나의 gateway**만 실행해야 합니다([Multiple gateways](/gateway/multiple-gateways) 참조). nodes는 gateway에 연결되는 주변 장치(iOS/Android nodes 또는 menubar 앱의 macOS "node mode")입니다. headless node hosts와 CLI 제어는 [Node host CLI](/cli/node)를 참조하세요.

    `gateway`, `discovery`, `canvasHost` 변경에는 전체 재시작이 필요합니다.

  </Accordion>

  <Accordion title="config를 적용하는 API / RPC 방식이 있나요?">
    예.

    - `config.schema.lookup`: 쓰기 전에 config 서브트리 하나와 해당 얕은 schema 노드, 일치하는 UI 힌트, 직접 자식 요약을 검사
    - `config.get`: 현재 스냅샷 + hash 가져오기
    - `config.patch`: 안전한 부분 업데이트(대부분의 RPC 편집에 권장)
    - `config.apply`: 전체 config를 검증 + 교체한 뒤 재시작
    - owner-only `gateway` runtime tool은 여전히 `tools.exec.ask` / `tools.exec.security` 재작성은 거부합니다. 레거시 `tools.bash.*` 별칭도 같은 보호된 exec 경로로 정규화됩니다

  </Accordion>

  <Accordion title="첫 설치를 위한 최소한의 합리적 config">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    이 설정은 workspace를 지정하고 누가 봇을 트리거할 수 있는지 제한합니다.

  </Accordion>

  <Accordion title="VPS에 Tailscale을 설정하고 Mac에서 연결하려면 어떻게 하나요?">
    최소 단계:

    1. **VPS에 설치 + 로그인**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Mac에 설치 + 로그인**
       - Tailscale 앱을 사용해 같은 tailnet에 로그인하세요.
    3. **MagicDNS 활성화(권장)**
       - Tailscale 관리자 콘솔에서 MagicDNS를 활성화해 VPS에 안정적인 이름을 부여하세요.
    4. **tailnet hostname 사용**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    SSH 없이 Control UI를 사용하려면 VPS에서 Tailscale Serve를 사용하세요:

    ```bash
    openclaw gateway --tailscale serve
    ```

    이렇게 하면 gateway는 loopback에 bind된 채 유지되고, Tailscale을 통해 HTTPS로 노출됩니다. [Tailscale](/gateway/tailscale)을 참조하세요.

  </Accordion>

  <Accordion title="원격 Gateway(Tailscale Serve)에 Mac node를 연결하려면 어떻게 하나요?">
    Serve는 **Gateway Control UI + WS**를 노출합니다. Nodes는 같은 Gateway WS 엔드포인트로 연결합니다.

    권장 설정:

    1. **VPS와 Mac이 같은 tailnet에 있는지 확인**.
    2. **macOS 앱을 Remote mode로 사용**(SSH 대상은 tailnet hostname이 될 수 있음).
       앱이 Gateway 포트를 터널링하고 node로 연결합니다.
    3. gateway에서 node를 승인:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    문서: [Gateway protocol](/gateway/protocol), [Discovery](/gateway/discovery), [macOS remote mode](/platforms/mac/remote).

  </Accordion>

  <Accordion title="두 번째 노트북에는 별도 설치를 해야 하나요, 아니면 node만 추가하면 되나요?">
    두 번째 노트북에서 **로컬 도구**(screen/camera/exec)만 필요하다면
    **node**로 추가하세요. 이렇게 하면 Gateway는 하나만 유지되고 중복 config를 피할 수 있습니다. 로컬 node 도구는
    현재 macOS 전용이지만, 다른 OS로도 확장할 계획입니다.

    완전히 분리된 봇이 두 개 필요할 때만 두 번째 Gateway를 설치하세요.

    문서: [Nodes](/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Env vars 및 .env 로드

<AccordionGroup>
  <Accordion title="OpenClaw는 환경 변수를 어떻게 로드하나요?">
    OpenClaw는 부모 프로세스(셸, launchd/systemd, CI 등)에서 env vars를 읽고, 추가로 다음도 로드합니다:

    - 현재 작업 디렉터리의 `.env`
    - `~/.openclaw/.env`(즉 `$OPENCLAW_STATE_DIR/.env`)의 전역 fallback `.env`

    두 `.env` 파일 모두 기존 env vars를 덮어쓰지 않습니다.

    config에 인라인 env vars도 정의할 수 있습니다(프로세스 env에 없을 때만 적용):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    전체 우선순위와 소스는 [/environment](/help/environment)를 참조하세요.

  </Accordion>

  <Accordion title="서비스로 Gateway를 시작했더니 env vars가 사라졌습니다. 어떻게 하나요?">
    흔한 해결책 두 가지:

    1. `~/.openclaw/.env`에 누락된 키를 넣어 서비스가 셸 env를 상속하지 않아도 읽히게 하세요.
    2. 셸 가져오기 활성화(옵트인 편의 기능):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    이렇게 하면 로그인 셸을 실행하고 예상되는 누락 키만 가져옵니다(절대 덮어쓰지 않음). 동등한 env var:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='COPILOT_GITHUB_TOKEN을 설정했는데 models status에 "Shell env: off."가 보입니다. 왜 그런가요?'>
    `openclaw models status`는 **shell env import**가 활성화되어 있는지 보고합니다. "Shell env: off"는
    env vars가 없다는 뜻이 아니라, OpenClaw가 로그인 셸을 자동 로드하지 않는다는 뜻입니다.

    Gateway가 서비스로 실행되면 셸
    환경을 상속하지 않습니다. 다음 중 하나로 해결하세요:

    1. `~/.openclaw/.env`에 토큰을 넣기:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. 또는 shell import 활성화(`env.shellEnv.enabled: true`).
    3. 또는 config `env` 블록에 추가(누락 시에만 적용).

    그다음 gateway를 재시작하고 다시 확인하세요:

    ```bash
    openclaw models status
    ```

    Copilot 토큰은 `COPILOT_GITHUB_TOKEN`(또는 `GH_TOKEN` / `GITHUB_TOKEN`)에서 읽습니다.
    [/concepts/model-providers](/concepts/model-providers) 및 [/environment](/help/environment)를 참조하세요.

  </Accordion>
</AccordionGroup>

## 세션 및 여러 채팅

<AccordionGroup>
  <Accordion title="새 대화를 시작하려면 어떻게 하나요?">
    `/new` 또는 `/reset`을 단독 메시지로 보내세요. [Session management](/concepts/session)를 참조하세요.
  </Accordion>

  <Accordion title="/new를 한 번도 보내지 않으면 세션이 자동으로 리셋되나요?">
    세션은 `session.idleMinutes` 후 만료되게 할 수 있지만, 이 기능은 **기본적으로 비활성화**되어 있습니다(기본값 **0**).
    활성화하려면 양수 값을 설정하세요. 활성화된 경우, 유휴 시간 이후의 **다음**
    메시지가 해당 채팅 키에 대해 새 세션 id를 시작합니다.
    이 과정은 기록을 삭제하지 않고 새 세션만 시작합니다.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="OpenClaw 인스턴스 팀(CEO 한 명과 여러 agents)을 만들 수 있나요?">
    예. **다중 에이전트 라우팅**과 **sub-agents**로 가능합니다. 하나의 coordinator
    agent와 각자 자신의 workspaces와 모델을 가진 여러 worker agents를 만들 수 있습니다.

    다만 이는 **재미있는 실험**에 가깝습니다. 토큰을 많이 사용하고,
    봇 하나에서 여러 세션을 쓰는 것보다 비효율적인 경우가 많습니다. 우리가
    일반적으로 상정하는 모델은 하나의 봇과, 병렬 작업을 위한 여러 세션입니다. 필요하면
    그 봇이 sub-agents를 생성할 수도 있습니다.

    문서: [Multi-agent routing](/concepts/multi-agent), [Sub-agents](/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="작업 중간에 컨텍스트가 잘렸습니다. 어떻게 방지하나요?">
    세션 컨텍스트는 모델 창 크기에 제한됩니다. 긴 채팅, 큰 도구 출력, 많은
    파일은 compaction 또는 truncation을 유발할 수 있습니다.

    도움이 되는 방법:

    - 봇에게 현재 상태를 요약하고 파일에 쓰라고 요청.
    - 긴 작업 전에는 `/compact`, 주제 전환 시에는 `/new` 사용.
    - 중요한 컨텍스트는 workspace에 두고 봇에게 다시 읽게 하기.
    - 긴 작업 또는 병렬 작업에는 sub-agents를 사용해 메인 채팅을 더 작게 유지.
    - 이런 일이 자주 일어나면 더 큰 컨텍스트 창을 가진 모델 선택.

  </Accordion>

  <Accordion title="설치는 유지한 채 OpenClaw를 완전히 초기화하려면 어떻게 하나요?">
    reset 명령을 사용하세요:

    ```bash
    openclaw reset
    ```

    비대화형 전체 reset:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    그다음 다시 설정:

    ```bash
    openclaw onboard --install-daemon
    ```

    참고:

    - 온보딩은 기존 config를 발견하면 **Reset** 옵션도 제공합니다. [Onboarding (CLI)](/ko/start/wizard)를 참조하세요.
    - profiles(`--profile` / `OPENCLAW_PROFILE`)를 사용했다면 각 state dir(기본값 `~/.openclaw-<profile>`)도 reset하세요.
    - 개발용 reset: `openclaw gateway --dev --reset` (dev 전용; dev config + credentials + sessions + workspace 삭제).

  </Accordion>

  <Accordion title='context too large 오류가 발생합니다. 어떻게 reset 또는 compact하나요?'>
    다음 중 하나를 사용하세요:

    - **Compact** (대화를 유지하지만 오래된 턴을 요약):

      ```
      /compact
      ```

      또는 요약을 안내하려면 `/compact <instructions>` 사용.

    - **Reset** (같은 채팅 키에 대해 새 세션 ID):

      ```
      /new
      /reset
      ```

    계속 발생한다면:

    - 오래된 도구 출력을 다듬기 위해 **session pruning**(`agents.defaults.contextPruning`)을 활성화하거나 조정.
    - 더 큰 context window를 가진 모델 사용.

    문서: [Compaction](/concepts/compaction), [Session pruning](/concepts/session-pruning), [Session management](/concepts/session).

  </Accordion>

  <Accordion title='왜 "LLM request rejected: messages.content.tool_use.input field required"가 보이나요?'>
    이는 provider 검증 오류입니다: 모델이 필수 `input` 없이 `tool_use` 블록을 출력한 것입니다. 보통 세션 기록이 오래되었거나 손상되었음을 의미합니다(대개 긴 스레드 이후나 도구/스키마 변경 후).

    해결: `/new`를 사용해 새 세션을 시작하세요(단독 메시지).

  </Accordion>

  <Accordion title="왜 30분마다 heartbeat 메시지를 받나요?">
    Heartbeat는 기본적으로 **30분**마다 실행됩니다(**OAuth 인증 사용 시 1시간**). 조정하거나 비활성화할 수 있습니다:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // 또는 비활성화하려면 "0m"
          },
        },
      },
    }
    ```

    `HEARTBEAT.md`가 존재하지만 사실상 비어 있다면(빈 줄과 `# Heading` 같은 markdown
    headers만 있는 경우), OpenClaw는 API 호출을 아끼기 위해 heartbeat 실행을 건너뜁니다.
    파일이 없어도 heartbeat는 실행되며 모델이 무엇을 할지 결정합니다.

    에이전트별 override는 `agents.list[].heartbeat`를 사용합니다. 문서: [Heartbeat](/gateway/heartbeat).

  </Accordion>

  <Accordion title='WhatsApp 그룹에 "bot account"를 추가해야 하나요?'>
    아니요. OpenClaw는 **당신 자신의 account**에서 실행되므로, 당신이 그룹에 있다면 OpenClaw도 그 그룹을 볼 수 있습니다.
    기본적으로 그룹 응답은 발신자를 허용할 때까지 차단됩니다(`groupPolicy: "allowlist"`).

    그룹에서 **당신만** 봇을 트리거할 수 있게 하려면:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="WhatsApp 그룹의 JID는 어떻게 얻나요?">
    옵션 1(가장 빠름): 로그를 tail한 상태에서 그룹에 테스트 메시지를 보내세요:

    ```bash
    openclaw logs --follow --json
    ```

    `@g.us`로 끝나는 `chatId`(또는 `from`)를 찾으세요. 예:
    `1234567890-1234567890@g.us`.

    옵션 2(이미 구성/allowlist된 경우): config에서 그룹 나열:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    문서: [WhatsApp](/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="왜 그룹에서 OpenClaw가 응답하지 않나요?">
    흔한 원인 두 가지:

    - mention 게이팅이 켜져 있음(기본값). 봇을 @mention하거나 `mentionPatterns`와 일치해야 함.
    - `channels.whatsapp.groups`를 `"*"` 없이 구성했고 해당 그룹이 allowlist에 없음.

    [Groups](/channels/groups) 및 [Group messages](/channels/group-messages)를 참조하세요.

  </Accordion>

  <Accordion title="groups/threads는 DMs와 컨텍스트를 공유하나요?">
    기본적으로 direct chats는 main session으로 축약됩니다. groups/channels는 각자의 session key를 가지며, Telegram topics / Discord threads는 별도의 세션입니다. [Groups](/channels/groups) 및 [Group messages](/channels/group-messages)를 참조하세요.
  </Accordion>

  <Accordion title="workspace와 agent는 몇 개까지 만들 수 있나요?">
    하드 제한은 없습니다. 수십 개(심지어 수백 개)도 괜찮지만 다음은 주의하세요:

    - **디스크 증가:** sessions + transcripts는 `~/.openclaw/agents/<agentId>/sessions/` 아래에 저장됩니다.
    - **토큰 비용:** 에이전트가 많을수록 동시 모델 사용량이 늘어납니다.
    - **운영 오버헤드:** 에이전트별 auth profiles, workspaces, channel routing.

    팁:

    - 에이전트당 **활성** workspace 하나를 유지하세요(`agents.defaults.workspace`).
    - 디스크가 커지면 오래된 세션(JSONL 또는 저장소 항목)을 정리하세요.
    - `openclaw doctor`를 사용하면 stray workspaces와 profile 불일치를 확인할 수 있습니다.

  </Accordion>

  <Accordion title="여러 봇이나 채팅을 동시에 실행할 수 있나요(Slack)? 어떻게 설정해야 하나요?">
    예. **다중 에이전트 라우팅**을 사용해 여러 격리 에이전트를 실행하고 수신 메시지를
    channel/account/peer 기준으로 라우팅하세요. Slack은 채널로 지원되며 특정 agent에 바인딩할 수 있습니다.

    브라우저 접근은 강력하지만 "사람이 할 수 있는 모든 것"을 의미하지는 않습니다 -
    anti-bot, CAPTCHAs, MFA는 여전히 자동화를 막을 수 있습니다. 가장 신뢰할 수 있는 browser 제어를 위해서는
    호스트의 로컬 Chrome MCP를 사용하거나, 실제 browser를 실행하는 머신의 CDP를 사용하세요.

    모범 설정:

    - 항상 켜진 Gateway 호스트(VPS/Mac mini).
    - 역할별 agent 하나씩(bindings).
    - 해당 agents에 바인딩된 Slack channel(s).
    - 필요 시 Chrome MCP 또는 node를 통한 로컬 browser.

    문서: [Multi-Agent Routing](/concepts/multi-agent), [Slack](/channels/slack),
    [Browser](/tools/browser), [Nodes](/nodes).

  </Accordion>
</AccordionGroup>

## 모델: 기본값, 선택, 별칭, 전환

<AccordionGroup>
  <Accordion title='기본 모델(default model)이란 무엇인가요?'>
    OpenClaw의 기본 모델은 다음에 설정한 값입니다:

    ```
    agents.defaults.model.primary
    ```

    모델은 `provider/model` 형식으로 참조합니다(예: `openai/gpt-5.4`). provider를 생략하면 OpenClaw는 먼저 alias를 시도하고, 그다음 그 정확한 모델 id에 대한 고유한 configured-provider 일치를 시도한 후, 마지막으로 폐지 예정인 호환 경로로 구성된 기본 provider로 폴백합니다. 해당 provider가 더 이상 구성된 기본 모델을 노출하지 않으면, 제거된 오래된 provider 기본값을 보여주는 대신 첫 번째 구성된 provider/model로 폴백합니다. 그래도 **명시적으로** `provider/model`을 설정하는 것이 좋습니다.

  </Accordion>

  <Accordion title="어떤 모델을 추천하나요?">
    **권장 기본값:** provider 스택에서 사용할 수 있는 가장 강력한 최신 세대 모델을 사용하세요.
    **도구가 활성화되었거나 신뢰되지 않은 입력을 다루는 에이전트:** 비용보다 모델 성능을 우선하세요.
    **일상적/저위험 채팅:** 더 저렴한 fallback 모델을 사용하고 agent 역할별로 라우팅하세요.

    MiniMax 전용 문서: [MiniMax](/providers/minimax) 및
    [Local models](/gateway/local-models).

    경험 법칙: 위험도가 높은 작업에는 **감당 가능한 가장 좋은 모델**을 사용하고,
    일상 채팅이나 요약에는 더 저렴한 모델을 사용하세요. 모델은 agent별로 라우팅할 수 있으며 긴 작업은 sub-agents로
    병렬화할 수 있습니다(each sub-agent는 토큰을 소비). [Models](/concepts/models) 및
    [Sub-agents](/tools/subagents)를 참조하세요.

    강한 경고: 더 약하거나 과도하게 quantized된 모델은 prompt
    injection과 안전하지 않은 동작에 더 취약합니다. [Security](/gateway/security)를 참조하세요.

    추가 맥락: [Models](/concepts/models).

  </Accordion>

  <Accordion title="config를 지우지 않고 모델을 바꾸려면 어떻게 하나요?">
    **모델 명령**을 사용하거나 **model** 필드만 편집하세요. 전체 config 교체는 피하세요.

    안전한 방법:

    - 채팅에서 `/model` (빠른 세션별 전환)
    - `openclaw models set ...` (모델 config만 업데이트)
    - `openclaw configure --section model` (대화형)
    - `~/.openclaw/openclaw.json`의 `agents.defaults.model` 편집

    전체 config를 교체할 의도가 아니라면 부분 객체로 `config.apply`를 사용하지 마세요.
    RPC 편집에는 먼저 `config.schema.lookup`로 검사하고 `config.patch`를 우선 사용하세요. lookup 페이로드는 정규화된 경로, 얕은 schema 문서/제약, 직접 자식 요약을 제공합니다.
    부분 업데이트용입니다.
    실수로 config를 덮어썼다면 백업에서 복원하거나 `openclaw doctor`를 다시 실행해 복구하세요.

    문서: [Models](/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/gateway/doctor).

  </Accordion>

  <Accordion title="self-hosted 모델(llama.cpp, vLLM, Ollama)을 사용할 수 있나요?">
    예. 로컬 모델에는 Ollama가 가장 쉬운 경로입니다.

    가장 빠른 설정:

    1. `https://ollama.com/download`에서 Ollama 설치
    2. `ollama pull glm-4.7-flash` 같은 로컬 모델 pull
    3. 클라우드 모델도 사용하려면 `ollama signin`
    4. `openclaw onboard` 실행 후 `Ollama` 선택
    5. `Local` 또는 `Cloud + Local` 선택

    참고:

    - `Cloud + Local`은 클라우드 모델과 로컬 Ollama 모델을 모두 제공합니다
    - `kimi-k2.5:cloud` 같은 클라우드 모델은 로컬 pull이 필요 없습니다
    - 수동 전환에는 `openclaw models list`와 `openclaw models set ollama/<model>` 사용

    보안 참고: 더 작거나 heavily quantized된 모델은 prompt
    injection에 더 취약합니다. 도구를 사용할 수 있는 봇에는 **큰 모델**을 강력히 권장합니다.
    그래도 작은 모델을 쓰고 싶다면 샌드박싱과 엄격한 도구 allowlists를 활성화하세요.

    문서: [Ollama](/providers/ollama), [Local models](/gateway/local-models),
    [Model providers](/concepts/model-providers), [Security](/gateway/security),
    [Sandboxing](/gateway/sandboxing).

  </Accordion>

  <Accordion title="OpenClaw, Flawd, Krill은 어떤 모델을 사용하나요?">
    - 이 배포들은 서로 다를 수 있고 시간에 따라 변할 수 있으며, 고정된 provider 추천은 없습니다.
    - 각 gateway의 현재 런타임 설정은 `openclaw models status`로 확인하세요.
    - 보안에 민감하거나 도구가 활성화된 agents에는 가장 강력한 최신 세대 모델을 사용하세요.
  </Accordion>

  <Accordion title="재시작 없이 즉시 모델을 전환하려면 어떻게 하나요?">
    단독 메시지로 `/model` 명령을 사용하세요:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    이들은 내장 alias입니다. 커스텀 alias는 `agents.defaults.models`를 통해 추가할 수 있습니다.

    사용 가능한 모델은 `/model`, `/model list`, `/model status`로 볼 수 있습니다.

    `/model`(및 `/model list`)은 간단한 번호 선택기를 표시합니다. 번호로 선택할 수 있습니다:

    ```
    /model 3
    ```

    provider에 대해 특정 auth profile을 세션 단위로 강제할 수도 있습니다:

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    팁: `/model status`는 어떤 agent가 활성 상태인지, 어떤 `auth-profiles.json` 파일을 사용 중인지, 그리고 어떤 auth profile이 다음에 시도될지를 보여줍니다.
    또한 구성된 provider endpoint(`baseUrl`)와 API mode(`api`)도 사용 가능한 경우 표시합니다.

    **@profile로 설정한 profile 고정을 어떻게 해제하나요?**

    `@profile` 접미사 없이 `/model`을 다시 실행하세요:

    ```
    /model anthropic/claude-opus-4-6
    ```

    기본값으로 돌아가려면 `/model`에서 기본 모델을 선택하세요(또는 `/model <default provider/model>` 전송).
    활성 auth profile은 `/model status`로 확인하세요.

  </Accordion>

  <Accordion title="일상 작업에는 GPT 5.2를 쓰고 코딩에는 Codex 5.3을 쓸 수 있나요?">
    예. 하나를 기본값으로 두고 필요할 때 전환하세요:

    - **빠른 전환(세션별):** 일상 작업에는 `/model gpt-5.4`, Codex OAuth 기반 코딩에는 `/model openai-codex/gpt-5.4`.
    - **기본값 + 전환:** `agents.defaults.model.primary`를 `openai/gpt-5.4`로 설정한 뒤 코딩할 때 `openai-codex/gpt-5.4`로 전환(또는 반대로).
    - **Sub-agents:** 코딩 작업은 다른 기본 모델을 가진 sub-agents로 라우팅.

    [Models](/concepts/models) 및 [Slash commands](/tools/slash-commands)를 참조하세요.

  </Accordion>

  <Accordion title='왜 "Model ... is not allowed"가 나오고 응답이 없나요?'>
    `agents.defaults.models`가 설정되어 있으면 `/model`과 모든
    세션 override의 **allowlist**가 됩니다. 그 목록에 없는 모델을 고르면 다음이 반환됩니다:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    이 오류는 일반 응답 **대신** 반환됩니다. 해결 방법: 해당 모델을
    `agents.defaults.models`에 추가하거나, allowlist를 제거하거나, `/model list`에서 선택하세요.

  </Accordion>

  <Accordion title='왜 "Unknown model: minimax/MiniMax-M2.7"가 보이나요?'>
    이는 **provider가 구성되지 않았기 때문**입니다(MiniMax provider config나 auth
    profile을 찾지 못함), 그래서 모델을 확인할 수 없습니다.

    해결 체크리스트:

    1. 현재 OpenClaw 릴리스로 업그레이드하거나 소스의 `main`에서 실행한 뒤 gateway를 재시작.
    2. MiniMax가 구성되어 있는지 확인(마법사 또는 JSON), 또는 MiniMax auth가
       env/auth profiles에 존재하여 일치하는 provider가 주입될 수 있는지 확인
       (`minimax`용 `MINIMAX_API_KEY`, `minimax-portal`용 `MINIMAX_OAUTH_TOKEN` 또는 저장된 MiniMax
       OAuth).
    3. 인증 경로에 맞는 정확한 모델 id(대소문자 구분)를 사용:
       API 키 설정에는 `minimax/MiniMax-M2.7` 또는 `minimax/MiniMax-M2.7-highspeed`,
       OAuth 설정에는 `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed`.
    4. 다음 실행:

       ```bash
       openclaw models list
       ```

       그리고 목록에서 선택하세요(또는 채팅에서 `/model list`).

    [MiniMax](/providers/minimax) 및 [Models](/concepts/models)를 참조하세요.

  </Accordion>

  <Accordion title="MiniMax를 기본값으로 하고 복잡한 작업에는 OpenAI를 쓸 수 있나요?">
    예. **MiniMax를 기본값**으로 두고 필요할 때 **세션별로** 모델을 전환하세요.
    Fallbacks는 **오류용**이지 "어려운 작업"용이 아니므로, `/model`이나 별도 agent를 사용하세요.

    **옵션 A: 세션별 전환**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    그다음:

    ```
    /model gpt
    ```

    **옵션 B: 별도 agents**

    - Agent A 기본값: MiniMax
    - Agent B 기본값: OpenAI
    - agent별 라우팅 또는 `/agent`로 전환

    문서: [Models](/concepts/models), [Multi-Agent Routing](/concepts/multi-agent), [MiniMax](/providers/minimax), [OpenAI](/providers/openai).

  </Accordion>

  <Accordion title="opus / sonnet / gpt는 내장 단축어인가요?">
    예. OpenClaw는 몇 가지 기본 shorthand를 제공합니다(`agents.defaults.models`에 모델이 존재할 때만 적용):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    같은 이름으로 자신만의 alias를 설정하면 당신의 값이 우선합니다.

  </Accordion>

  <Accordion title="모델 단축어(alias)는 어떻게 정의/재정의하나요?">
    Aliases는 `agents.defaults.models.<modelId>.alias`에서 옵니다. 예:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    그다음 `/model sonnet`(또는 지원되는 경우 `/<alias>`)이 해당 모델 ID로 확인됩니다.

  </Accordion>

  <Accordion title="OpenRouter나 z.ai 같은 다른 providers의 모델은 어떻게 추가하나요?">
    OpenRouter(토큰당 과금, 다양한 모델):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    z.ai(GLM 모델):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    provider/model을 참조했는데 필요한 provider 키가 없으면 런타임 인증 오류가 발생합니다(예: `No API key found for provider "zai"`).

    **새 agent를 추가한 뒤 "No API key found for provider"가 나옵니다**

    보통 **새 agent**의 auth store가 비어 있다는 뜻입니다. Auth는 에이전트별이며 다음에 저장됩니다:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    해결 방법:

    - `openclaw agents add <id>`를 실행하고 마법사에서 auth를 구성.
    - 또는 main agent의 `agentDir`에 있는 `auth-profiles.json`을 새 agent의 `agentDir`로 복사.

    에이전트 간 `agentDir`를 재사용하지 마세요. auth/session 충돌을 일으킵니다.

  </Accordion>
</AccordionGroup>

## 모델 failover 및 "All models failed"

<AccordionGroup>
  <Accordion title="failover는 어떻게 동작하나요?">
    Failover는 두 단계로 일어납니다:

    1. 같은 provider 안에서 **auth profile rotation**.
    2. `agents.defaults.model.fallbacks`의 다음 모델로 **model fallback**.

    실패하는 profiles에는 cooldown이 적용되므로(지수 backoff), provider가 rate-limited 상태이거나 일시적으로 실패해도 OpenClaw는 계속 응답할 수 있습니다.

    rate-limit 버킷에는 단순한 `429` 응답 외의 것도 포함됩니다. OpenClaw는
    `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted`, 주기적
    usage-window limits(`weekly/monthly limit reached`) 같은 메시지도 failover-worthy한
    rate limit로 취급합니다.

    일부 과금처럼 보이는 응