---
read_when:
    - OpenClaw를 기본 macOS 환경과 분리해 실행하려는 경우
    - 샌드박스에서 iMessage 통합(BlueBubbles)을 사용하려는 경우
    - 복제 가능한 초기화 가능한 macOS 환경을 원하는 경우
    - 로컬 macOS VM 옵션과 호스팅 macOS VM 옵션을 비교하려는 경우
summary: 격리 또는 iMessage가 필요할 때 샌드박스된 macOS VM(로컬 또는 호스팅)에서 OpenClaw 실행
title: macOS VM
x-i18n:
    generated_at: "2026-04-05T12:46:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1f7c5691fd2686418ee25f2c38b1f9badd511daeef2906d21ad30fb523b013f
    source_path: install/macos-vm.md
    workflow: 15
---

# macOS VM에서 OpenClaw 실행하기(샌드박싱)

## 권장 기본값(대부분의 사용자)

- 상시 실행 Gateway와 저렴한 비용을 원한다면 **소형 Linux VPS**를 사용하세요. [VPS hosting](/vps)을 참조하세요.
- 브라우저 자동화를 위한 **residential IP**와 완전한 제어를 원한다면 **전용 하드웨어**(Mac mini 또는 Linux 박스)를 사용하세요. 많은 사이트가 데이터센터 IP를 차단하므로 로컬 브라우징이 더 잘 동작하는 경우가 많습니다.
- **하이브리드:** 저렴한 VPS에 Gateway를 두고, 브라우저/UI 자동화가 필요할 때 Mac을 **node**로 연결하세요. [Nodes](/nodes) 및 [Gateway remote](/gateway/remote)를 참조하세요.

macOS 전용 기능(iMessage/BlueBubbles)이 꼭 필요하거나, 일상적으로 사용하는 Mac과 엄격히 격리하고 싶을 때 macOS VM을 사용하세요.

## macOS VM 옵션

### Apple Silicon Mac에서 로컬 VM 실행(Lume)

[Lume](https://cua.ai/docs/lume)를 사용해 기존 Apple Silicon Mac에서 샌드박스된 macOS VM 안에 OpenClaw를 실행할 수 있습니다.

이 방식의 장점:

- 완전히 격리된 macOS 환경(호스트는 깨끗하게 유지)
- BlueBubbles를 통한 iMessage 지원(Linux/Windows에서는 불가능)
- VM 복제로 즉시 초기화 가능
- 추가 하드웨어나 클라우드 비용 없음

### 호스팅 Mac 제공업체(클라우드)

클라우드에서 macOS를 원한다면 호스팅 Mac 제공업체도 사용할 수 있습니다:

- [MacStadium](https://www.macstadium.com/) (호스팅 Mac)
- 다른 호스팅 Mac 벤더도 동작합니다. 해당 VM + SSH 문서를 따르세요.

macOS VM에 SSH로 접근할 수 있게 되면 아래 6단계부터 계속 진행하세요.

---

## 빠른 경로(Lume, 숙련 사용자용)

1. Lume 설치
2. `lume create openclaw --os macos --ipsw latest`
3. Setup Assistant 완료, Remote Login(SSH) 활성화
4. `lume run openclaw --no-display`
5. SSH 접속, OpenClaw 설치, 채널 구성
6. 완료

---

## 필요한 것(Lume)

- Apple Silicon Mac (M1/M2/M3/M4)
- 호스트에 macOS Sequoia 이상
- VM당 약 60 GB 여유 디스크 공간
- 약 20분

---

## 1) Lume 설치

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/trycua/cua/main/libs/lume/scripts/install.sh)"
```

`~/.local/bin`이 PATH에 없다면:

```bash
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.zshrc && source ~/.zshrc
```

확인:

```bash
lume --version
```

문서: [Lume Installation](https://cua.ai/docs/lume/guide/getting-started/installation)

---

## 2) macOS VM 만들기

```bash
lume create openclaw --os macos --ipsw latest
```

이 명령은 macOS를 다운로드하고 VM을 생성합니다. VNC 창이 자동으로 열립니다.

참고: 다운로드는 연결 속도에 따라 시간이 걸릴 수 있습니다.

---

## 3) Setup Assistant 완료

VNC 창에서:

1. 언어와 지역 선택
2. Apple ID 건너뛰기(나중에 iMessage가 필요하면 로그인)
3. 사용자 계정 생성(사용자 이름과 비밀번호를 기억해 두세요)
4. 선택적 기능은 모두 건너뛰기

설정이 완료되면 SSH를 활성화하세요:

1. System Settings → General → Sharing 열기
2. "Remote Login" 활성화

---

## 4) VM IP 주소 가져오기

```bash
lume get openclaw
```

IP 주소(보통 `192.168.64.x`)를 확인하세요.

---

## 5) VM에 SSH 접속

```bash
ssh youruser@192.168.64.X
```

`youruser`는 생성한 계정으로, IP는 VM의 실제 IP로 바꾸세요.

---

## 6) OpenClaw 설치

VM 안에서:

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

온보딩 프롬프트에 따라 모델 공급자(Anthropic, OpenAI 등)를 설정하세요.

---

## 7) 채널 구성

config 파일을 편집하세요:

```bash
nano ~/.openclaw/openclaw.json
```

채널 추가:

```json5
{
  channels: {
    whatsapp: {
      dmPolicy: "allowlist",
      allowFrom: ["+15551234567"],
    },
    telegram: {
      botToken: "YOUR_BOT_TOKEN",
    },
  },
}
```

그런 다음 WhatsApp에 로그인(QR 스캔):

```bash
openclaw channels login
```

---

## 8) 헤드리스로 VM 실행

VM을 중지한 뒤 디스플레이 없이 다시 시작하세요:

```bash
lume stop openclaw
lume run openclaw --no-display
```

VM은 백그라운드에서 실행됩니다. OpenClaw daemon이 gateway를 계속 실행합니다.

상태 확인:

```bash
ssh youruser@192.168.64.X "openclaw status"
```

---

## 보너스: iMessage 통합

이것이 macOS에서 실행할 때의 핵심 기능입니다. [BlueBubbles](https://bluebubbles.app)를 사용해 OpenClaw에 iMessage를 추가하세요.

VM 안에서:

1. bluebubbles.app에서 BlueBubbles 다운로드
2. Apple ID로 로그인
3. Web API를 활성화하고 비밀번호 설정
4. BlueBubbles webhook이 gateway를 가리키도록 설정(예: `https://your-gateway-host:3000/bluebubbles-webhook?password=<password>`)

OpenClaw config에 추가:

```json5
{
  channels: {
    bluebubbles: {
      serverUrl: "http://localhost:1234",
      password: "your-api-password",
      webhookPath: "/bluebubbles-webhook",
    },
  },
}
```

gateway를 재시작하세요. 이제 agent가 iMessage를 송수신할 수 있습니다.

전체 설정 세부 정보: [BlueBubbles channel](/channels/bluebubbles)

---

## 골든 이미지 저장

추가 사용자 지정 전에 깨끗한 상태를 스냅샷으로 저장하세요:

```bash
lume stop openclaw
lume clone openclaw openclaw-golden
```

언제든지 초기화:

```bash
lume stop openclaw && lume delete openclaw
lume clone openclaw-golden openclaw
lume run openclaw --no-display
```

---

## 24/7 실행

VM을 계속 실행하려면:

- Mac을 전원에 연결해 두기
- System Settings → Energy Saver에서 잠자기 비활성화
- 필요하면 `caffeinate` 사용

진짜 상시 실행이 필요하다면 전용 Mac mini 또는 소형 VPS를 고려하세요. [VPS hosting](/vps)을 참조하세요.

---

## 문제 해결

| 문제 | 해결 방법 |
| ------------------------ | ---------------------------------------------------------------------------------- |
| VM에 SSH 접속 불가 | VM의 System Settings에서 "Remote Login"이 활성화되어 있는지 확인 |
| VM IP가 표시되지 않음 | VM이 완전히 부팅될 때까지 기다린 뒤 `lume get openclaw`를 다시 실행 |
| `lume` 명령을 찾을 수 없음 | `~/.local/bin`을 PATH에 추가 |
| WhatsApp QR이 스캔되지 않음 | `openclaw channels login`을 실행할 때 호스트가 아니라 VM에 로그인되어 있는지 확인 |

---

## 관련 문서

- [VPS hosting](/vps)
- [Nodes](/nodes)
- [Gateway remote](/gateway/remote)
- [BlueBubbles channel](/channels/bluebubbles)
- [Lume Quickstart](https://cua.ai/docs/lume/guide/getting-started/quickstart)
- [Lume CLI Reference](https://cua.ai/docs/lume/reference/cli-reference)
- [Unattended VM Setup](https://cua.ai/docs/lume/guide/fundamentals/unattended-setup) (고급)
- [Docker Sandboxing](/install/docker) (대체 격리 접근 방식)
