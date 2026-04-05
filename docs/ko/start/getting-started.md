---
read_when:
    - 처음부터 처음 설정하는 경우
    - 작동하는 채팅까지 가는 가장 빠른 경로를 원하는 경우
summary: OpenClaw를 설치하고 몇 분 안에 첫 채팅을 시작하세요.
title: 시작하기
x-i18n:
    generated_at: "2026-04-05T10:49:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: c43eee6f0d3f593e3cf0767bfacb3e0ae38f51a2615d594303786ae1d4a6d2c3
    source_path: start/getting-started.md
    workflow: 15
---

# 시작하기

OpenClaw를 설치하고, 온보딩을 실행하고, AI 어시스턴트와 채팅하세요 —
모두 약 5분이면 됩니다. 이 과정을 마치면 실행 중인 Gateway, 구성된 인증,
그리고 작동하는 채팅 세션을 갖추게 됩니다.

## 필요한 것

- **Node.js** — Node 24 권장(Node 22.14+도 지원)
- **모델 제공자의 API 키**(Anthropic, OpenAI, Google 등) — 온보딩 중에 입력하라는 안내가 표시됩니다

<Tip>
`node --version`으로 Node 버전을 확인하세요.
**Windows 사용자:** 네이티브 Windows와 WSL2를 모두 지원합니다. 전체 경험을 위해서는
WSL2가 더 안정적이며 권장됩니다. [Windows](/platforms/windows)를 참조하세요.
Node를 설치해야 하나요? [Node 설정](/install/node)을 참조하세요.
</Tip>

## 빠른 설정

<Steps>
  <Step title="OpenClaw 설치">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="설치 스크립트 프로세스"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        ```powershell
        iwr -useb https://openclaw.ai/install.ps1 | iex
        ```
      </Tab>
    </Tabs>

    <Note>
    다른 설치 방법(Docker, Nix, npm): [설치](/install).
    </Note>

  </Step>
  <Step title="온보딩 실행">
    ```bash
    openclaw onboard --install-daemon
    ```

    이 마법사는 모델 제공자 선택, API 키 설정,
    Gateway 구성 과정을 안내합니다. 약 2분이 걸립니다.

    전체 참조는 [온보딩(CLI)](/start/wizard)를 참조하세요.

  </Step>
  <Step title="Gateway 실행 확인">
    ```bash
    openclaw gateway status
    ```

    Gateway가 포트 18789에서 수신 대기 중인 것이 표시되어야 합니다.

  </Step>
  <Step title="대시보드 열기">
    ```bash
    openclaw dashboard
    ```

    브라우저에서 Control UI가 열립니다. 로드되면 모든 것이 정상적으로 작동하는 것입니다.

  </Step>
  <Step title="첫 메시지 보내기">
    Control UI 채팅에서 메시지를 입력하면 AI 응답을 받을 수 있습니다.

    대신 휴대폰에서 채팅하고 싶으신가요? 설정이 가장 빠른 채널은
    [Telegram](/channels/telegram)입니다(봇 토큰만 있으면 됩니다). 모든 옵션은
    [채널](/channels)을 참조하세요.

  </Step>
</Steps>

<Accordion title="고급: 사용자 지정 Control UI 빌드 마운트">
  현지화되었거나 사용자 지정된 대시보드 빌드를 유지 관리하는 경우,
  빌드된 정적 애셋과 `index.html`이 들어 있는 디렉터리를 가리키도록
  `gateway.controlUi.root`를 설정하세요.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# 빌드된 정적 파일을 해당 디렉터리에 복사하세요.
```

그런 다음 다음과 같이 설정하세요:

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "root": "$HOME/.openclaw/control-ui-custom"
    }
  }
}
```

Gateway를 재시작한 다음 대시보드를 다시 여세요:

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## 다음 단계

<Columns>
  <Card title="채널 연결" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo 등.
  </Card>
  <Card title="페어링 및 안전" href="/channels/pairing" icon="shield">
    누가 에이전트에 메시지를 보낼 수 있는지 제어하세요.
  </Card>
  <Card title="Gateway 구성" href="/gateway/configuration" icon="settings">
    모델, 도구, 샌드박스 및 고급 설정.
  </Card>
  <Card title="도구 둘러보기" href="/tools" icon="wrench">
    브라우저, exec, 웹 검색, Skills, plugins.
  </Card>
</Columns>

<Accordion title="고급: 환경 변수">
  OpenClaw를 서비스 계정으로 실행하거나 사용자 지정 경로를 원한다면:

- `OPENCLAW_HOME` — 내부 경로 해석을 위한 홈 디렉터리
- `OPENCLAW_STATE_DIR` — 상태 디렉터리 재정의
- `OPENCLAW_CONFIG_PATH` — 구성 파일 경로 재정의

전체 참조: [환경 변수](/help/environment).
</Accordion>
