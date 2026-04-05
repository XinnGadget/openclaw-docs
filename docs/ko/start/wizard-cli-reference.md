---
read_when:
    - '`openclaw onboard`의 자세한 동작이 필요한 경우'
    - 온보딩 결과를 디버깅하거나 온보딩 클라이언트를 통합하는 경우
sidebarTitle: CLI reference
summary: CLI 설정 흐름, 인증/모델 설정, 출력, 내부 동작에 대한 완전한 참조
title: CLI 설정 참조
x-i18n:
    generated_at: "2026-04-05T12:56:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ec4e685e3237e450d11c45826c2bb34b82c0bba1162335f8fbb07f51ba00a70
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# CLI 설정 참조

이 페이지는 `openclaw onboard`의 전체 참조입니다.
짧은 가이드는 [온보딩(CLI)](/ko/start/wizard)를 참조하세요.

## 마법사가 수행하는 작업

local 모드(기본값)는 다음 항목을 안내합니다:

- 모델 및 인증 설정(OpenAI Code 구독 OAuth, Anthropic Claude CLI 또는 API 키, 그리고 MiniMax, GLM, Ollama, Moonshot, StepFun, AI Gateway 옵션)
- Workspace 위치 및 bootstrap 파일
- Gateway 설정(포트, bind, auth, tailscale)
- 채널 및 provider(Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles 및 기타 번들 채널 plugin)
- daemon 설치(LaunchAgent, systemd user unit 또는 네이티브 Windows Scheduled Task와 Startup-folder 대체 방식)
- 상태 검사
- Skills 설정

remote 모드는 이 머신이 다른 곳의 gateway에 연결하도록 구성합니다.
원격 호스트에 아무것도 설치하거나 수정하지 않습니다.

## local 흐름 세부 정보

<Steps>
  <Step title="기존 구성 감지">
    - `~/.openclaw/openclaw.json`이 있으면 Keep, Modify 또는 Reset을 선택합니다.
    - 마법사를 다시 실행해도 명시적으로 Reset을 선택하지 않는 한(또는 `--reset`을 전달하지 않는 한) 아무것도 지워지지 않습니다.
    - CLI `--reset`의 기본값은 `config+creds+sessions`이며, workspace까지 제거하려면 `--reset-scope full`을 사용하세요.
    - 구성이 잘못되었거나 레거시 키가 포함되어 있으면 마법사는 중단되고 계속하기 전에 `openclaw doctor`를 실행하라고 안내합니다.
    - Reset은 `trash`를 사용하며 다음 범위를 제공합니다:
      - Config만
      - Config + credentials + sessions
      - 전체 Reset(workspace도 제거)
  </Step>
  <Step title="모델 및 인증">
    - 전체 옵션 매트릭스는 [인증 및 모델 옵션](#auth-and-model-options)에 있습니다.
  </Step>
  <Step title="Workspace">
    - 기본값은 `~/.openclaw/workspace`입니다(구성 가능).
    - 첫 실행 bootstrap 의식에 필요한 workspace 파일을 시드합니다.
    - Workspace 레이아웃: [Agent workspace](/ko/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - 포트, bind, auth 모드 및 tailscale 노출을 입력받습니다.
    - 권장 사항: local loopback에서도 token auth를 활성화된 상태로 유지하여 로컬 WS 클라이언트에도 인증이 필요하도록 하세요.
    - token 모드에서 대화형 설정은 다음을 제공합니다:
      - **평문 토큰 생성/저장**(기본값)
      - **SecretRef 사용**(선택)
    - password 모드에서도 대화형 설정은 평문 또는 SecretRef 저장을 지원합니다.
    - 비대화형 token SecretRef 경로: `--gateway-token-ref-env <ENV_VAR>`.
      - 온보딩 프로세스 환경에 비어 있지 않은 환경 변수가 필요합니다.
      - `--gateway-token`과 함께 사용할 수 없습니다.
    - 모든 로컬 프로세스를 완전히 신뢰하는 경우에만 auth를 비활성화하세요.
    - non-loopback bind에는 여전히 auth가 필요합니다.
  </Step>
  <Step title="채널">
    - [WhatsApp](/ko/channels/whatsapp): 선택적 QR 로그인
    - [Telegram](/ko/channels/telegram): 봇 토큰
    - [Discord](/ko/channels/discord): 봇 토큰
    - [Google Chat](/ko/channels/googlechat): 서비스 계정 JSON + webhook audience
    - [Mattermost](/ko/channels/mattermost): 봇 토큰 + base URL
    - [Signal](/ko/channels/signal): 선택적 `signal-cli` 설치 + 계정 구성
    - [BlueBubbles](/ko/channels/bluebubbles): iMessage에 권장됨; 서버 URL + 비밀번호 + webhook
    - [iMessage](/ko/channels/imessage): 레거시 `imsg` CLI 경로 + DB 액세스
    - DM 보안: 기본값은 pairing입니다. 첫 DM이 코드를 보내며,
      `openclaw pairing approve <channel> <code>`로 승인하거나 allowlist를 사용하세요.
  </Step>
  <Step title="Daemon 설치">
    - macOS: LaunchAgent
      - 로그인된 사용자 세션이 필요합니다. 헤드리스 환경에서는 사용자 지정 LaunchDaemon을 사용하세요(기본 제공되지 않음).
    - Linux 및 WSL2를 통한 Windows: systemd user unit
      - 마법사는 로그아웃 후에도 gateway가 계속 실행되도록 `loginctl enable-linger <user>`를 시도합니다.
      - sudo를 요청할 수 있습니다(`/var/lib/systemd/linger`에 기록). 먼저 sudo 없이 시도합니다.
    - 네이티브 Windows: 먼저 Scheduled Task
      - 작업 생성이 거부되면 OpenClaw는 사용자별 Startup-folder 로그인 항목으로 대체하고 gateway를 즉시 시작합니다.
      - Scheduled Task가 더 나은 supervisor 상태를 제공하므로 여전히 선호됩니다.
    - 런타임 선택: Node(권장; WhatsApp 및 Telegram에 필요). Bun은 권장되지 않습니다.
  </Step>
  <Step title="상태 검사">
    - 필요하면 gateway를 시작하고 `openclaw health`를 실행합니다.
    - `openclaw status --deep`는 상태 출력에 live gateway 상태 프로브를 추가하며, 지원되는 경우 채널 프로브도 포함합니다.
  </Step>
  <Step title="Skills">
    - 사용 가능한 Skills를 읽고 요구 사항을 확인합니다.
    - node manager로 npm, pnpm 또는 bun을 선택할 수 있습니다.
    - 선택적 종속성을 설치합니다(일부는 macOS에서 Homebrew를 사용).
  </Step>
  <Step title="완료">
    - iOS, Android, macOS 앱 옵션을 포함한 요약과 다음 단계가 표시됩니다.
  </Step>
</Steps>

<Note>
GUI가 감지되지 않으면 마법사는 브라우저를 여는 대신 Control UI용 SSH 포트 포워딩 지침을 출력합니다.
Control UI 에셋이 없으면 마법사가 이를 빌드하려고 시도하며, 대체 수단은 `pnpm ui:build`입니다(UI 종속성을 자동 설치함).
</Note>

## remote 모드 세부 정보

remote 모드는 이 머신이 다른 곳의 gateway에 연결하도록 구성합니다.

<Info>
remote 모드는 원격 호스트에 아무것도 설치하거나 수정하지 않습니다.
</Info>

설정하는 항목:

- 원격 gateway URL (`ws://...`)
- 원격 gateway auth가 필요한 경우 토큰(권장)

<Note>
- gateway가 loopback 전용이면 SSH 터널링 또는 tailnet을 사용하세요.
- 검색 힌트:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## 인증 및 모델 옵션

<AccordionGroup>
  <Accordion title="Anthropic API 키">
    `ANTHROPIC_API_KEY`가 있으면 그것을 사용하고, 없으면 키 입력을 요청한 뒤 daemon에서 사용할 수 있도록 저장합니다.
  </Accordion>
  <Accordion title="Anthropic Claude CLI">
    gateway host에서 로컬 Claude CLI 로그인을 재사용하고 모델 선택을
    정식 `claude-cli/claude-*` 참조로 전환합니다.

    이것은 `openclaw onboard` 및
    `openclaw configure`에서 사용할 수 있는 local 대체 경로입니다. 운영 환경에서는 Anthropic API 키를 권장합니다.

    - macOS: Keychain 항목 "Claude Code-credentials" 확인
    - Linux 및 Windows: `~/.claude/.credentials.json`이 있으면 재사용

    macOS에서는 launchd 시작이 차단되지 않도록 "Always Allow"를 선택하세요.

  </Accordion>
  <Accordion title="OpenAI Code 구독(Codex CLI 재사용)">
    `~/.codex/auth.json`이 있으면 마법사가 이를 재사용할 수 있습니다.
    재사용된 Codex CLI 자격 증명은 계속 Codex CLI가 관리합니다. 만료 시 OpenClaw는
    먼저 해당 소스를 다시 읽고, provider가 새로 고칠 수 있으면
    소유권을 가져오지 않고 갱신된 자격 증명을 Codex 저장소에 다시 기록합니다.
  </Accordion>
  <Accordion title="OpenAI Code 구독(OAuth)">
    브라우저 흐름이며 `code#state`를 붙여 넣습니다.

    모델이 설정되지 않았거나 `openai/*`인 경우 `agents.defaults.model`을 `openai-codex/gpt-5.4`로 설정합니다.

  </Accordion>
  <Accordion title="OpenAI API 키">
    `OPENAI_API_KEY`가 있으면 그것을 사용하고, 없으면 키 입력을 요청한 뒤 자격 증명을 auth profile에 저장합니다.

    모델이 설정되지 않았거나 `openai/*` 또는 `openai-codex/*`인 경우 `agents.defaults.model`을 `openai/gpt-5.4`로 설정합니다.

  </Accordion>
  <Accordion title="xAI (Grok) API 키">
    `XAI_API_KEY`를 입력받고 xAI를 모델 provider로 구성합니다.
  </Accordion>
  <Accordion title="OpenCode">
    `OPENCODE_API_KEY`(또는 `OPENCODE_ZEN_API_KEY`)를 입력받고 Zen 또는 Go 카탈로그를 선택할 수 있습니다.
    설정 URL: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API 키(일반)">
    키를 대신 저장합니다.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    `AI_GATEWAY_API_KEY`를 입력받습니다.
    자세한 내용: [Vercel AI Gateway](/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    account ID, gateway ID, `CLOUDFLARE_AI_GATEWAY_API_KEY`를 입력받습니다.
    자세한 내용: [Cloudflare AI Gateway](/ko/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    구성이 자동으로 기록됩니다. 호스팅 기본값은 `MiniMax-M2.7`이며, API 키 설정은
    `minimax/...`, OAuth 설정은 `minimax-portal/...`를 사용합니다.
    자세한 내용: [MiniMax](/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    중국 또는 글로벌 엔드포인트에서 StepFun standard 또는 Step Plan용 구성이 자동으로 기록됩니다.
    현재 Standard에는 `step-3.5-flash`가 포함되고, Step Plan에는 `step-3.5-flash-2603`도 포함됩니다.
    자세한 내용: [StepFun](/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (Anthropic 호환)">
    `SYNTHETIC_API_KEY`를 입력받습니다.
    자세한 내용: [Synthetic](/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud 및 local 오픈 모델)">
    base URL(기본값 `http://127.0.0.1:11434`)을 입력받은 다음 Cloud + Local 또는 Local 모드를 제안합니다.
    사용 가능한 모델을 검색하고 기본값을 제안합니다.
    자세한 내용: [Ollama](/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot 및 Kimi Coding">
    Moonshot(Kimi K2) 및 Kimi Coding 구성은 자동으로 기록됩니다.
    자세한 내용: [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot).
  </Accordion>
  <Accordion title="사용자 지정 provider">
    OpenAI 호환 및 Anthropic 호환 엔드포인트에서 동작합니다.

    대화형 온보딩은 다른 provider API 키 흐름과 동일한 API 키 저장 선택지를 지원합니다:
    - **지금 API 키 붙여넣기**(평문)
    - **비밀 참조 사용**(env ref 또는 구성된 provider ref, 사전 검증 포함)

    비대화형 플래그:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (선택 사항, 없으면 `CUSTOM_API_KEY` 사용)
    - `--custom-provider-id` (선택 사항)
    - `--custom-compatibility <openai|anthropic>` (선택 사항, 기본값 `openai`)

  </Accordion>
  <Accordion title="건너뛰기">
    auth를 구성하지 않은 상태로 둡니다.
  </Accordion>
</AccordionGroup>

모델 동작:

- 감지된 옵션에서 기본 모델을 선택하거나, provider와 모델을 수동으로 입력합니다.
- 온보딩이 provider auth 선택에서 시작되면 모델 선택기는 자동으로
  해당 provider를 우선시합니다. Volcengine 및 BytePlus의 경우 같은 우선순위가
  해당 coding-plan 변형(`volcengine-plan/*`,
  `byteplus-plan/*`)에도 적용됩니다.
- 이 선호 provider 필터가 비게 되면 선택기는 모델이 전혀 보이지 않도록 하지 않고 전체 카탈로그로 대체합니다.
- 마법사는 모델 검사를 실행하며, 구성된 모델을 알 수 없거나 auth가 없으면 경고합니다.

자격 증명 및 profile 경로:

- Auth profile(API 키 + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 레거시 OAuth 가져오기: `~/.openclaw/credentials/oauth.json`

자격 증명 저장 모드:

- 기본 온보딩 동작은 API 키를 auth profile에 평문 값으로 저장합니다.
- `--secret-input-mode ref`는 평문 키 저장 대신 참조 모드를 활성화합니다.
  대화형 설정에서는 다음 중 하나를 선택할 수 있습니다:
  - 환경 변수 ref(예: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - 구성된 provider ref(`file` 또는 `exec`)와 provider 별칭 + id
- 대화형 참조 모드는 저장 전에 빠른 사전 검증을 수행합니다.
  - Env ref: 변수 이름 및 현재 온보딩 환경에서 비어 있지 않은 값인지 검증합니다.
  - Provider ref: provider 구성 및 요청된 id를 확인합니다.
  - 사전 검증에 실패하면 온보딩은 오류를 표시하고 다시 시도할 수 있게 합니다.
- 비대화형 모드에서 `--secret-input-mode ref`는 env 기반 전용입니다.
  - 온보딩 프로세스 환경에 provider 환경 변수를 설정하세요.
  - 인라인 키 플래그(예: `--openai-api-key`)는 해당 환경 변수가 설정되어 있어야 하며, 그렇지 않으면 온보딩이 즉시 실패합니다.
  - 사용자 지정 provider의 경우 비대화형 `ref` 모드는 `models.providers.<id>.apiKey`를 `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`로 저장합니다.
  - 이 사용자 지정 provider 경우에서 `--custom-api-key`를 사용하려면 `CUSTOM_API_KEY`가 설정되어 있어야 하며, 그렇지 않으면 온보딩이 즉시 실패합니다.
- Gateway auth 자격 증명은 대화형 설정에서 평문 및 SecretRef 선택을 지원합니다:
  - Token 모드: **평문 토큰 생성/저장**(기본값) 또는 **SecretRef 사용**.
  - Password 모드: 평문 또는 SecretRef.
- 비대화형 token SecretRef 경로: `--gateway-token-ref-env <ENV_VAR>`.
- 기존 평문 설정은 변경 없이 계속 동작합니다.

<Note>
헤드리스 및 서버 팁: 브라우저가 있는 머신에서 OAuth를 완료한 다음
해당 agent의 `auth-profiles.json`(예:
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 또는 일치하는
`$OPENCLAW_STATE_DIR/...` 경로)을 gateway host로 복사하세요. `credentials/oauth.json`은
레거시 가져오기 소스일 뿐입니다.
</Note>

## 출력 및 내부 동작

`~/.openclaw/openclaw.json`의 일반적인 필드:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax를 선택한 경우)
- `tools.profile` (local 온보딩은 설정되지 않은 경우 기본값으로 `"coding"`을 사용하며, 기존의 명시적 값은 유지됨)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (local 온보딩은 설정되지 않은 경우 이를 기본값 `per-channel-peer`로 설정하며, 기존의 명시적 값은 유지됨)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- 프롬프트 중 선택하면 채널 allowlist(Slack, Discord, Matrix, Microsoft Teams)도 기록됩니다(가능하면 이름을 ID로 확인함)
- `skills.install.nodeManager`
  - `setup --node-manager` 플래그는 `npm`, `pnpm`, `bun`을 허용합니다.
  - 수동 구성에서는 나중에 여전히 `skills.install.nodeManager: "yarn"`을 설정할 수 있습니다.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`는 `agents.list[]`와 선택적 `bindings`를 기록합니다.

WhatsApp 자격 증명은 `~/.openclaw/credentials/whatsapp/<accountId>/` 아래에 저장됩니다.
세션은 `~/.openclaw/agents/<agentId>/sessions/` 아래에 저장됩니다.

<Note>
일부 채널은 plugin으로 제공됩니다. 설정 중 선택하면 마법사는
채널 구성을 하기 전에 plugin 설치(npm 또는 로컬 경로)를 요청합니다.
</Note>

Gateway wizard RPC:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

클라이언트(macOS 앱 및 Control UI)는 온보딩 로직을 다시 구현하지 않고도 단계를 렌더링할 수 있습니다.

Signal 설정 동작:

- 적절한 릴리스 에셋을 다운로드합니다
- 이를 `~/.openclaw/tools/signal-cli/<version>/` 아래에 저장합니다
- 구성에 `channels.signal.cliPath`를 기록합니다
- JVM 빌드에는 Java 21이 필요합니다
- 사용 가능한 경우 네이티브 빌드가 사용됩니다
- Windows는 WSL2를 사용하며 WSL 내부에서 Linux signal-cli 흐름을 따릅니다

## 관련 문서

- 온보딩 허브: [온보딩(CLI)](/ko/start/wizard)
- 자동화 및 스크립트: [CLI 자동화](/start/wizard-cli-automation)
- 명령 참조: [`openclaw onboard`](/cli/onboard)
