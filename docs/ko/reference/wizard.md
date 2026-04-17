---
read_when:
    - 특정 온보딩 단계 또는 플래그 찾기
    - 비대화형 모드로 온보딩 자동화하기
    - 온보딩 동작 디버깅하기
sidebarTitle: Onboarding Reference
summary: 'CLI 온보딩 전체 참조: 모든 단계, 플래그, config 필드'
title: 온보딩 참조
x-i18n:
    generated_at: "2026-04-15T14:40:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# 온보딩 참조

이 문서는 `openclaw onboard`의 전체 참조입니다.
상위 수준 개요는 [온보딩 (CLI)](/ko/start/wizard)를 참조하세요.

## 흐름 세부 정보 (local 모드)

<Steps>
  <Step title="기존 config 감지">
    - `~/.openclaw/openclaw.json`이 있으면 **유지 / 수정 / 초기화**를 선택합니다.
    - 온보딩을 다시 실행해도 명시적으로 **초기화**를 선택하지 않는 한 아무것도 지워지지 않습니다
      (또는 `--reset`을 전달한 경우).
    - CLI `--reset`의 기본값은 `config+creds+sessions`이며, workspace까지 제거하려면 `--reset-scope full`을 사용하세요.
    - config가 유효하지 않거나 레거시 키를 포함하고 있으면, 마법사는 중단되고
      계속하기 전에 `openclaw doctor`를 실행하라고 안내합니다.
    - 초기화는 `trash`를 사용하며(`rm`은 절대 사용하지 않음) 다음 범위를 제공합니다:
      - config만
      - config + 자격 증명 + 세션
      - 전체 초기화 (workspace도 제거)
  </Step>
  <Step title="모델/인증">
    - **Anthropic API 키**: `ANTHROPIC_API_KEY`가 있으면 이를 사용하고, 없으면 키를 요청한 뒤 daemon 사용을 위해 저장합니다.
    - **Anthropic API 키**: 온보딩/configure에서 선호되는 Anthropic 도우미 선택지입니다.
    - **Anthropic setup-token**: 여전히 온보딩/configure에서 사용할 수 있지만, OpenClaw는 이제 가능하면 Claude CLI 재사용을 우선합니다.
    - **OpenAI Code (Codex) 구독 (Codex CLI)**: `~/.codex/auth.json`이 있으면 온보딩에서 이를 재사용할 수 있습니다. 재사용된 Codex CLI 자격 증명은 계속 Codex CLI가 관리합니다. 만료되면 OpenClaw는 먼저 그 소스를 다시 읽고, 제공자가 갱신할 수 있는 경우 자격 증명을 직접 가져오지 않고 갱신된 자격 증명을 Codex 저장소에 다시 기록합니다.
    - **OpenAI Code (Codex) 구독 (OAuth)**: 브라우저 흐름이며 `code#state`를 붙여 넣습니다.
      - 모델이 설정되지 않았거나 `openai/*`인 경우 `agents.defaults.model`을 `openai-codex/gpt-5.4`로 설정합니다.
    - **OpenAI API 키**: `OPENAI_API_KEY`가 있으면 이를 사용하고, 없으면 키를 요청한 뒤 인증 프로필에 저장합니다.
      - 모델이 설정되지 않았거나 `openai/*` 또는 `openai-codex/*`인 경우 `agents.defaults.model`을 `openai/gpt-5.4`로 설정합니다.
    - **xAI (Grok) API 키**: `XAI_API_KEY`를 요청하고 xAI를 모델 제공자로 구성합니다.
    - **OpenCode**: `OPENCODE_API_KEY`(또는 `OPENCODE_ZEN_API_KEY`, 발급처: https://opencode.ai/auth)를 요청하고 Zen 또는 Go 카탈로그를 선택하게 합니다.
    - **Ollama**: 먼저 **Cloud + Local**, **Cloud only**, **Local only**를 제공합니다. `Cloud only`는 `OLLAMA_API_KEY`를 요청하고 `https://ollama.com`을 사용합니다. 호스트 기반 모드는 Ollama 기본 URL을 요청하고, 사용 가능한 모델을 검색하며, 필요할 때 선택한 로컬 모델을 자동으로 pull합니다. `Cloud + Local`은 해당 Ollama 호스트가 cloud 액세스를 위해 로그인되어 있는지도 확인합니다.
    - 자세한 내용: [Ollama](/ko/providers/ollama)
    - **API 키**: 키를 대신 저장합니다.
    - **Vercel AI Gateway (다중 모델 프록시)**: `AI_GATEWAY_API_KEY`를 요청합니다.
    - 자세한 내용: [Vercel AI Gateway](/ko/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID, Gateway ID, `CLOUDFLARE_AI_GATEWAY_API_KEY`를 요청합니다.
    - 자세한 내용: [Cloudflare AI Gateway](/ko/providers/cloudflare-ai-gateway)
    - **MiniMax**: config가 자동으로 작성되며, 호스팅 기본값은 `MiniMax-M2.7`입니다.
      API 키 설정은 `minimax/...`를 사용하고, OAuth 설정은
      `minimax-portal/...`를 사용합니다.
    - 자세한 내용: [MiniMax](/ko/providers/minimax)
    - **StepFun**: 중국 또는 글로벌 엔드포인트에서 StepFun standard 또는 Step Plan용 config가 자동으로 작성됩니다.
    - 현재 Standard에는 `step-3.5-flash`가 포함되며, Step Plan에는 `step-3.5-flash-2603`도 포함됩니다.
    - 자세한 내용: [StepFun](/ko/providers/stepfun)
    - **Synthetic (Anthropic 호환)**: `SYNTHETIC_API_KEY`를 요청합니다.
    - 자세한 내용: [Synthetic](/ko/providers/synthetic)
    - **Moonshot (Kimi K2)**: config가 자동으로 작성됩니다.
    - **Kimi Coding**: config가 자동으로 작성됩니다.
    - 자세한 내용: [Moonshot AI (Kimi + Kimi Coding)](/ko/providers/moonshot)
    - **건너뛰기**: 아직 인증이 구성되지 않습니다.
    - 감지된 옵션에서 기본 모델을 선택합니다(또는 제공자/모델을 수동으로 입력합니다). 최상의 품질과 더 낮은 프롬프트 인젝션 위험을 위해 제공자 스택에서 사용할 수 있는 가장 강력한 최신 세대 모델을 선택하세요.
    - 온보딩은 모델 검사를 실행하고, 구성된 모델을 알 수 없거나 인증이 누락된 경우 경고를 표시합니다.
    - API 키 저장 모드의 기본값은 평문 인증 프로필 값입니다. 대신 env 기반 ref를 저장하려면 `--secret-input-mode ref`를 사용하세요(예: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - 인증 프로필은 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`에 저장됩니다(API 키 + OAuth). `~/.openclaw/credentials/oauth.json`은 레거시 가져오기 전용입니다.
    - 자세한 내용: [/concepts/oauth](/ko/concepts/oauth)
    <Note>
    헤드리스/서버 팁: 브라우저가 있는 장치에서 OAuth를 완료한 다음,
    해당 에이전트의 `auth-profiles.json`(예:
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 또는 대응되는
    `$OPENCLAW_STATE_DIR/...` 경로)을 gateway 호스트로 복사하세요. `credentials/oauth.json`은
    레거시 가져오기 소스일 뿐입니다.
    </Note>
  </Step>
  <Step title="Workspace">
    - 기본값은 `~/.openclaw/workspace`입니다(구성 가능).
    - 에이전트 bootstrap ritual에 필요한 workspace 파일을 시드합니다.
    - 전체 workspace 레이아웃 + 백업 가이드: [Agent workspace](/ko/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - 포트, bind, 인증 모드, Tailscale 노출.
    - 인증 권장 사항: local loopback에서도 **Token**을 유지해 로컬 WS 클라이언트가 인증하도록 하세요.
    - token 모드에서 대화형 설정은 다음을 제공합니다:
      - **평문 token 생성/저장** (기본값)
      - **SecretRef 사용** (선택 사항)
      - 빠른 시작은 온보딩 프로브/대시보드 bootstrap을 위해 `env`, `file`, `exec` 제공자 전반에서 기존 `gateway.auth.token` SecretRef를 재사용합니다.
      - 해당 SecretRef가 구성되어 있지만 확인할 수 없으면, 온보딩은 런타임 인증을 조용히 저하시키는 대신 명확한 수정 메시지와 함께 초기에 실패합니다.
    - password 모드에서 대화형 설정도 평문 또는 SecretRef 저장을 지원합니다.
    - 비대화형 token SecretRef 경로: `--gateway-token-ref-env <ENV_VAR>`.
      - 온보딩 프로세스 환경에 비어 있지 않은 환경 변수가 필요합니다.
      - `--gateway-token`과 함께 사용할 수 없습니다.
    - 모든 로컬 프로세스를 완전히 신뢰하는 경우에만 인증을 비활성화하세요.
    - loopback이 아닌 bind에도 여전히 인증이 필요합니다.
  </Step>
  <Step title="채널">
    - [WhatsApp](/ko/channels/whatsapp): 선택적 QR 로그인.
    - [Telegram](/ko/channels/telegram): 봇 토큰.
    - [Discord](/ko/channels/discord): 봇 토큰.
    - [Google Chat](/ko/channels/googlechat): 서비스 계정 JSON + Webhook audience.
    - [Mattermost](/ko/channels/mattermost) (Plugin): 봇 토큰 + 기본 URL.
    - [Signal](/ko/channels/signal): 선택적 `signal-cli` 설치 + 계정 config.
    - [BlueBubbles](/ko/channels/bluebubbles): **iMessage에 권장**; 서버 URL + 비밀번호 + Webhook.
    - [iMessage](/ko/channels/imessage): 레거시 `imsg` CLI 경로 + DB 액세스.
    - DM 보안: 기본값은 pairing입니다. 첫 DM은 코드를 전송하며, `openclaw pairing approve <channel> <code>`로 승인하거나 허용 목록을 사용할 수 있습니다.
  </Step>
  <Step title="웹 검색">
    - Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG, Tavily 같은 지원 제공자를 선택합니다(또는 건너뜁니다).
    - API 기반 제공자는 빠른 설정을 위해 환경 변수 또는 기존 config를 사용할 수 있으며, 키가 필요 없는 제공자는 각 제공자별 선행 조건을 사용합니다.
    - `--skip-search`로 건너뜁니다.
    - 나중에 구성: `openclaw configure --section web`.
  </Step>
  <Step title="Daemon 설치">
    - macOS: LaunchAgent
      - 로그인된 사용자 세션이 필요합니다. 헤드리스의 경우 사용자 지정 LaunchDaemon을 사용하세요(기본 제공되지 않음).
    - Linux(및 WSL2를 통한 Windows): systemd 사용자 유닛
      - 온보딩은 로그아웃 후에도 Gateway가 계속 실행되도록 `loginctl enable-linger <user>` 활성화를 시도합니다.
      - sudo를 요청할 수 있습니다(`/var/lib/systemd/linger`에 기록). 먼저 sudo 없이 시도합니다.
    - **런타임 선택:** Node(권장, WhatsApp/Telegram에 필요). Bun은 **권장되지 않습니다**.
    - token 인증에 token이 필요하고 `gateway.auth.token`이 SecretRef로 관리되는 경우, daemon 설치는 이를 검증하지만 확인된 평문 token 값을 supervisor 서비스 환경 메타데이터에 유지하지 않습니다.
    - token 인증에 token이 필요하고 구성된 token SecretRef를 확인할 수 없는 경우, daemon 설치는 실행 가능한 안내와 함께 차단됩니다.
    - `gateway.auth.token`과 `gateway.auth.password`가 모두 구성되어 있고 `gateway.auth.mode`가 설정되지 않은 경우, mode를 명시적으로 설정할 때까지 daemon 설치가 차단됩니다.
  </Step>
  <Step title="상태 점검">
    - 필요하면 Gateway를 시작하고 `openclaw health`를 실행합니다.
    - 팁: `openclaw status --deep`는 상태 출력에 실시간 gateway 상태 프로브를 추가하며, 지원되는 경우 채널 프로브도 포함합니다(도달 가능한 gateway 필요).
  </Step>
  <Step title="Skills (권장)">
    - 사용 가능한 Skills를 읽고 요구 사항을 확인합니다.
    - 노드 관리자 **npm / pnpm**을 선택하게 합니다(bun은 권장되지 않음).
    - 선택적 종속성을 설치합니다(일부는 macOS에서 Homebrew 사용).
  </Step>
  <Step title="완료">
    - 추가 기능을 위한 iOS/Android/macOS 앱을 포함해 요약과 다음 단계를 표시합니다.
  </Step>
</Steps>

<Note>
GUI가 감지되지 않으면, 온보딩은 브라우저를 여는 대신 Control UI용 SSH 포트 포워딩 지침을 출력합니다.
Control UI 자산이 없으면 온보딩이 이를 빌드하려 시도하며, 대체 방법은 `pnpm ui:build`입니다(UI 종속성 자동 설치).
</Note>

## 비대화형 모드

온보딩을 자동화하거나 스크립트로 실행하려면 `--non-interactive`를 사용하세요:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

기계가 읽을 수 있는 요약을 원하면 `--json`을 추가하세요.

비대화형 모드에서의 Gateway token SecretRef:

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token`과 `--gateway-token-ref-env`는 함께 사용할 수 없습니다.

<Note>
`--json`은 비대화형 모드를 의미하지 않습니다. 스크립트에서는 `--non-interactive`(및 `--workspace`)를 사용하세요.
</Note>

제공자별 명령 예시는 [CLI 자동화](/ko/start/wizard-cli-automation#provider-specific-examples)에 있습니다.
플래그 의미와 단계 순서는 이 참조 페이지를 사용하세요.

### 에이전트 추가 (비대화형)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

Gateway는 RPC(`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`)를 통해 온보딩 흐름을 노출합니다.
클라이언트(macOS 앱, Control UI)는 온보딩 로직을 다시 구현하지 않고도 단계를 렌더링할 수 있습니다.

## Signal 설정 (signal-cli)

온보딩은 GitHub 릴리스에서 `signal-cli`를 설치할 수 있습니다:

- 적절한 릴리스 자산을 다운로드합니다.
- 이를 `~/.openclaw/tools/signal-cli/<version>/` 아래에 저장합니다.
- config에 `channels.signal.cliPath`를 기록합니다.

참고:

- JVM 빌드에는 **Java 21**이 필요합니다.
- 가능한 경우 네이티브 빌드가 사용됩니다.
- Windows는 WSL2를 사용하며, signal-cli 설치는 WSL 내부에서 Linux 흐름을 따릅니다.

## 마법사가 기록하는 내용

`~/.openclaw/openclaw.json`의 일반적인 필드:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (MiniMax를 선택한 경우)
- `tools.profile` (local 온보딩은 설정되지 않은 경우 기본값으로 `"coding"`을 사용하며, 기존에 명시된 값은 유지됩니다)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (동작 세부 정보: [CLI 설정 참조](/ko/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- 프롬프트에서 선택하면 채널 허용 목록(Slack/Discord/Matrix/Microsoft Teams)도 기록됩니다(가능하면 이름이 ID로 확인됩니다).
- `skills.install.nodeManager`
  - `setup --node-manager`는 `npm`, `pnpm`, `bun`을 받습니다.
  - 수동 config에서는 `skills.install.nodeManager`를 직접 설정하여 여전히 `yarn`을 사용할 수 있습니다.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`는 `agents.list[]`와 선택적 `bindings`를 기록합니다.

WhatsApp 자격 증명은 `~/.openclaw/credentials/whatsapp/<accountId>/` 아래에 저장됩니다.
세션은 `~/.openclaw/agents/<agentId>/sessions/` 아래에 저장됩니다.

일부 채널은 Plugin으로 제공됩니다. 설정 중 하나를 선택하면, 온보딩은 이를 구성하기 전에 설치할 수 있도록 `npm` 또는 로컬 경로를 사용한 설치를 안내합니다.

## 관련 문서

- 온보딩 개요: [온보딩 (CLI)](/ko/start/wizard)
- macOS 앱 온보딩: [온보딩](/ko/start/onboarding)
- config 참조: [Gateway 구성](/ko/gateway/configuration)
- 제공자: [WhatsApp](/ko/channels/whatsapp), [Telegram](/ko/channels/telegram), [Discord](/ko/channels/discord), [Google Chat](/ko/channels/googlechat), [Signal](/ko/channels/signal), [BlueBubbles](/ko/channels/bluebubbles) (iMessage), [iMessage](/ko/channels/imessage) (레거시)
- Skills: [Skills](/ko/tools/skills), [Skills config](/ko/tools/skills-config)
