---
read_when:
    - 특정 온보딩 단계 또는 플래그를 찾는 경우
    - 비대화형 모드로 온보딩을 자동화하는 경우
    - 온보딩 동작을 디버깅하는 경우
sidebarTitle: Onboarding Reference
summary: 'CLI 온보딩 전체 참조: 모든 단계, 플래그, 구성 필드'
title: 온보딩 참조
x-i18n:
    generated_at: "2026-04-05T12:55:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae6c76a31885c0678af2ac71254c5baf08f6de5481f85f6cfdf44d473946fdb8
    source_path: reference/wizard.md
    workflow: 15
---

# 온보딩 참조

이 문서는 `openclaw onboard`의 전체 참조입니다.
상위 수준 개요는 [온보딩(CLI)](/ko/start/wizard)를 참조하세요.

## 흐름 세부 정보(local 모드)

<Steps>
  <Step title="기존 구성 감지">
    - `~/.openclaw/openclaw.json`이 있으면 **Keep / Modify / Reset** 중에서 선택합니다.
    - 온보딩을 다시 실행해도 명시적으로 **Reset**을 선택하지 않는 한
      (또는 `--reset`을 전달하지 않는 한) 아무것도 지워지지 않습니다.
    - CLI `--reset`의 기본값은 `config+creds+sessions`이며, workspace까지
      제거하려면 `--reset-scope full`을 사용하세요.
    - 구성이 잘못되었거나 레거시 키가 포함되어 있으면 마법사는 중단되고,
      계속하기 전에 `openclaw doctor`를 실행하라고 안내합니다.
    - Reset은 `trash`를 사용하며(`rm`은 절대 사용하지 않음), 다음 범위를 제공합니다:
      - Config만
      - Config + 자격 증명 + 세션
      - 전체 Reset(workspace도 제거)
  </Step>
  <Step title="모델/인증">
    - **Anthropic API 키**: `ANTHROPIC_API_KEY`가 있으면 그것을 사용하고, 없으면 키 입력을 요청한 뒤 daemon에서 사용할 수 있도록 저장합니다.
    - **Anthropic Claude CLI**: 온보딩/configure에서 선호되는 Anthropic assistant 선택지입니다. macOS에서는 온보딩이 Keychain 항목 "Claude Code-credentials"를 확인합니다(launchd 시작이 막히지 않도록 "Always Allow" 선택). Linux/Windows에서는 `~/.claude/.credentials.json`이 있으면 이를 재사용하고 모델 선택을 정식 `claude-cli/claude-*` 참조로 전환합니다.
    - **Anthropic setup-token(레거시/수동)**: 온보딩/configure에서 다시 사용할 수 있지만, Anthropic은 OpenClaw 사용자에게 OpenClaw Claude 로그인 경로가 서드파티 harness 사용으로 간주되며 Claude 계정에 **Extra Usage**가 필요하다고 안내했습니다.
    - **OpenAI Code (Codex) 구독(Codex CLI)**: `~/.codex/auth.json`이 있으면 온보딩에서 이를 재사용할 수 있습니다. 재사용된 Codex CLI 자격 증명은 계속 Codex CLI가 관리하며, 만료 시 OpenClaw는 먼저 해당 소스를 다시 읽고, provider가 새로 고칠 수 있으면 자격 증명의 소유권을 가져오지 않고 갱신된 자격 증명을 Codex 저장소에 다시 씁니다.
    - **OpenAI Code (Codex) 구독(OAuth)**: 브라우저 흐름이며 `code#state`를 붙여 넣습니다.
      - 모델이 설정되지 않았거나 `openai/*`인 경우 `agents.defaults.model`을 `openai-codex/gpt-5.4`로 설정합니다.
    - **OpenAI API 키**: `OPENAI_API_KEY`가 있으면 그것을 사용하고, 없으면 키 입력을 요청한 뒤 auth profile에 저장합니다.
      - 모델이 설정되지 않았거나 `openai/*` 또는 `openai-codex/*`인 경우 `agents.defaults.model`을 `openai/gpt-5.4`로 설정합니다.
    - **xAI (Grok) API 키**: `XAI_API_KEY` 입력을 요청하고 xAI를 모델 provider로 구성합니다.
    - **OpenCode**: `OPENCODE_API_KEY`(또는 `OPENCODE_ZEN_API_KEY`, 발급 위치: https://opencode.ai/auth) 입력을 요청하고 Zen 카탈로그 또는 Go 카탈로그를 선택할 수 있게 합니다.
    - **Ollama**: Ollama base URL 입력을 요청하고 **Cloud + Local** 또는 **Local** 모드를 제안하며, 사용 가능한 모델을 검색하고 필요하면 선택한 로컬 모델을 자동으로 pull합니다.
    - 자세한 내용: [Ollama](/providers/ollama)
    - **API 키**: 키를 대신 저장합니다.
    - **Vercel AI Gateway(멀티 모델 프록시)**: `AI_GATEWAY_API_KEY`를 요청합니다.
    - 자세한 내용: [Vercel AI Gateway](/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway**: Account ID, Gateway ID, `CLOUDFLARE_AI_GATEWAY_API_KEY`를 요청합니다.
    - 자세한 내용: [Cloudflare AI Gateway](/ko/providers/cloudflare-ai-gateway)
    - **MiniMax**: 구성이 자동으로 기록되며, 호스팅 기본값은 `MiniMax-M2.7`입니다.
      API 키 설정은 `minimax/...`를 사용하고, OAuth 설정은
      `minimax-portal/...`를 사용합니다.
    - 자세한 내용: [MiniMax](/providers/minimax)
    - **StepFun**: 중국 또는 글로벌 엔드포인트에서 StepFun standard 또는 Step Plan용 구성이 자동으로 기록됩니다.
    - 현재 Standard에는 `step-3.5-flash`가 포함되고, Step Plan에는 `step-3.5-flash-2603`도 포함됩니다.
    - 자세한 내용: [StepFun](/providers/stepfun)
    - **Synthetic(Anthropic 호환)**: `SYNTHETIC_API_KEY`를 요청합니다.
    - 자세한 내용: [Synthetic](/providers/synthetic)
    - **Moonshot (Kimi K2)**: 구성이 자동으로 기록됩니다.
    - **Kimi Coding**: 구성이 자동으로 기록됩니다.
    - 자세한 내용: [Moonshot AI (Kimi + Kimi Coding)](/providers/moonshot)
    - **건너뛰기**: 아직 인증을 구성하지 않습니다.
    - 감지된 옵션에서 기본 모델을 선택하거나(또는 provider/model을 수동 입력), 가능한 provider 스택 내에서 가장 강력한 최신 세대 모델을 선택해 최상의 품질과 더 낮은 프롬프트 인젝션 위험을 확보하세요.
    - 온보딩은 모델 검사를 실행하며, 구성된 모델을 알 수 없거나 인증이 없으면 경고합니다.
    - API 키 저장 모드의 기본값은 평문 auth-profile 값입니다. 대신 env 기반 ref를 저장하려면 `--secret-input-mode ref`를 사용하세요(예: `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Auth profile은 `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`에 있습니다(API 키 + OAuth). `~/.openclaw/credentials/oauth.json`은 레거시 가져오기 전용입니다.
    - 자세한 내용: [/concepts/oauth](/ko/concepts/oauth)
    <Note>
    헤드리스/서버 팁: 브라우저가 있는 머신에서 OAuth를 완료한 다음,
    해당 agent의 `auth-profiles.json`(예:
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` 또는 일치하는
    `$OPENCLAW_STATE_DIR/...` 경로)을 gateway host로 복사하세요. `credentials/oauth.json`은
    레거시 가져오기 소스일 뿐입니다.
    </Note>
  </Step>
  <Step title="Workspace">
    - 기본값은 `~/.openclaw/workspace`입니다(구성 가능).
    - agent bootstrap 의식에 필요한 workspace 파일을 시드합니다.
    - 전체 workspace 레이아웃 + 백업 가이드: [Agent workspace](/ko/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - 포트, bind, 인증 모드, Tailscale 노출.
    - 인증 권장 사항: local loopback에서도 **Token**을 유지하여 로컬 WS 클라이언트에도 인증이 필요하도록 하세요.
    - token 모드에서 대화형 설정은 다음을 제공합니다:
      - **평문 토큰 생성/저장**(기본값)
      - **SecretRef 사용**(선택)
      - 빠른 시작은 온보딩 프로브/대시보드 bootstrap을 위해 `env`, `file`, `exec` provider 전반에서 기존 `gateway.auth.token` SecretRef를 재사용합니다.
      - 해당 SecretRef가 구성되어 있지만 확인할 수 없으면 온보딩은 런타임 인증을 조용히 약화시키는 대신 명확한 수정 메시지와 함께 조기에 실패합니다.
    - password 모드에서도 대화형 설정은 평문 또는 SecretRef 저장을 지원합니다.
    - 비대화형 token SecretRef 경로: `--gateway-token-ref-env <ENV_VAR>`.
      - 온보딩 프로세스 환경에 비어 있지 않은 환경 변수가 필요합니다.
      - `--gateway-token`과 함께 사용할 수 없습니다.
    - 모든 로컬 프로세스를 완전히 신뢰하는 경우에만 인증을 비활성화하세요.
    - non‑loopback bind에는 여전히 인증이 필요합니다.
  </Step>
  <Step title="채널">
    - [WhatsApp](/ko/channels/whatsapp): 선택적 QR 로그인.
    - [Telegram](/ko/channels/telegram): 봇 토큰.
    - [Discord](/ko/channels/discord): 봇 토큰.
    - [Google Chat](/ko/channels/googlechat): 서비스 계정 JSON + webhook audience.
    - [Mattermost](/ko/channels/mattermost) (plugin): 봇 토큰 + base URL.
    - [Signal](/ko/channels/signal): 선택적 `signal-cli` 설치 + 계정 구성.
    - [BlueBubbles](/ko/channels/bluebubbles): **iMessage에 권장**; 서버 URL + 비밀번호 + webhook.
    - [iMessage](/ko/channels/imessage): 레거시 `imsg` CLI 경로 + DB 액세스.
    - DM 보안: 기본값은 pairing입니다. 첫 DM이 코드를 보내며, `openclaw pairing approve <channel> <code>`로 승인하거나 allowlist를 사용하세요.
  </Step>
  <Step title="웹 검색">
    - Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG, Tavily 같은 지원 provider를 선택하거나(또는 건너뛰기) 할 수 있습니다.
    - API 기반 provider는 빠른 설정을 위해 환경 변수 또는 기존 구성을 사용할 수 있고, 키가 필요 없는 provider는 provider별 전제 조건을 사용합니다.
    - `--skip-search`로 건너뜁니다.
    - 나중에 구성: `openclaw configure --section web`.
  </Step>
  <Step title="Daemon 설치">
    - macOS: LaunchAgent
      - 로그인된 사용자 세션이 필요합니다. 헤드리스 환경에서는 사용자 지정 LaunchDaemon을 사용하세요(기본 제공되지 않음).
    - Linux(및 WSL2를 통한 Windows): systemd user unit
      - 온보딩은 로그아웃 후에도 Gateway가 계속 실행되도록 `loginctl enable-linger <user>`를 활성화하려고 시도합니다.
      - sudo를 요청할 수 있습니다(`/var/lib/systemd/linger` 기록). 먼저 sudo 없이 시도합니다.
    - **런타임 선택:** Node(권장, WhatsApp/Telegram에 필요). Bun은 **권장되지 않습니다**.
    - token 인증에 토큰이 필요하고 `gateway.auth.token`이 SecretRef로 관리되는 경우, daemon 설치는 이를 검증하지만 확인된 평문 토큰 값을 supervisor 서비스 환경 메타데이터에 유지하지는 않습니다.
    - token 인증에 토큰이 필요하고 구성된 token SecretRef를 확인할 수 없는 경우, daemon 설치는 실행 가능한 안내와 함께 차단됩니다.
    - `gateway.auth.token`과 `gateway.auth.password`가 모두 구성되어 있고 `gateway.auth.mode`가 설정되지 않은 경우, 모드를 명시적으로 설정할 때까지 daemon 설치가 차단됩니다.
  </Step>
  <Step title="상태 검사">
    - 필요하면 Gateway를 시작하고 `openclaw health`를 실행합니다.
    - 팁: `openclaw status --deep`를 사용하면 상태 출력에 live gateway 상태 프로브가 추가되며, 지원되는 경우 채널 프로브도 포함됩니다(reachable gateway 필요).
  </Step>
  <Step title="Skills(권장)">
    - 사용 가능한 Skills를 읽고 요구 사항을 확인합니다.
    - 노드 관리자 **npm / pnpm** 중 하나를 선택할 수 있습니다(bun은 권장되지 않음).
    - 선택적 종속성을 설치합니다(일부는 macOS에서 Homebrew 사용).
  </Step>
  <Step title="완료">
    - 추가 기능을 위한 iOS/Android/macOS 앱을 포함해 요약 + 다음 단계가 표시됩니다.
  </Step>
</Steps>

<Note>
GUI가 감지되지 않으면 온보딩은 브라우저를 여는 대신 Control UI용 SSH 포트 포워딩 지침을 출력합니다.
Control UI 에셋이 없으면 온보딩이 이를 빌드하려고 시도하며, 대체 수단은 `pnpm ui:build`입니다(UI 종속성을 자동 설치함).
</Note>

## 비대화형 모드

자동화 또는 스크립트용으로 `--non-interactive`를 사용하세요:

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

기계가 읽을 수 있는 요약이 필요하면 `--json`을 추가하세요.

비대화형 모드의 Gateway token SecretRef:

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
`--json`은 **비대화형 모드**를 의미하지 않습니다. 스크립트에서는 `--non-interactive`(및 `--workspace`)를 사용하세요.
</Note>

provider별 명령 예시는 [CLI 자동화](/start/wizard-cli-automation#provider-specific-examples)에 있습니다.
이 참조 페이지는 플래그 의미와 단계 순서를 확인하는 데 사용하세요.

### agent 추가(비대화형)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## Gateway wizard RPC

Gateway는 RPC를 통해 온보딩 흐름을 노출합니다(`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
클라이언트(macOS 앱, Control UI)는 온보딩 로직을 다시 구현하지 않고도 단계를 렌더링할 수 있습니다.

## Signal 설정(signal-cli)

온보딩은 GitHub 릴리스에서 `signal-cli`를 설치할 수 있습니다:

- 적절한 릴리스 에셋을 다운로드합니다.
- 이를 `~/.openclaw/tools/signal-cli/<version>/` 아래에 저장합니다.
- 구성에 `channels.signal.cliPath`를 기록합니다.

참고:

- JVM 빌드에는 **Java 21**이 필요합니다.
- 사용 가능한 경우 네이티브 빌드가 사용됩니다.
- Windows는 WSL2를 사용하며, signal-cli 설치는 WSL 내부에서 Linux 흐름을 따릅니다.

## 마법사가 기록하는 내용

`~/.openclaw/openclaw.json`의 일반적인 필드:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (Minimax를 선택한 경우)
- `tools.profile` (local 온보딩은 설정되지 않은 경우 기본값으로 `"coding"`을 사용하며, 기존의 명시적 값은 유지됨)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (동작 세부 정보: [CLI 설정 참조](/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- 프롬프트 중 선택하면 채널 allowlist(Slack/Discord/Matrix/Microsoft Teams)도 기록됩니다(가능하면 이름을 ID로 확인함).
- `skills.install.nodeManager`
  - `setup --node-manager`는 `npm`, `pnpm`, `bun`을 허용합니다.
  - 수동 구성에서는 `skills.install.nodeManager`를 직접 설정해 여전히 `yarn`을 사용할 수 있습니다.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add`는 `agents.list[]`와 선택적 `bindings`를 기록합니다.

WhatsApp 자격 증명은 `~/.openclaw/credentials/whatsapp/<accountId>/` 아래에 저장됩니다.
세션은 `~/.openclaw/agents/<agentId>/sessions/` 아래에 저장됩니다.

일부 채널은 plugin으로 제공됩니다. 설정 중 하나를 선택하면, 구성하기 전에
온보딩이 해당 plugin 설치(npm 또는 로컬 경로)를 요청합니다.

## 관련 문서

- 온보딩 개요: [온보딩(CLI)](/ko/start/wizard)
- macOS 앱 온보딩: [온보딩](/start/onboarding)
- 구성 참조: [Gateway 구성](/ko/gateway/configuration)
- Provider: [WhatsApp](/ko/channels/whatsapp), [Telegram](/ko/channels/telegram), [Discord](/ko/channels/discord), [Google Chat](/ko/channels/googlechat), [Signal](/ko/channels/signal), [BlueBubbles](/ko/channels/bluebubbles) (iMessage), [iMessage](/ko/channels/imessage) (레거시)
- Skills: [Skills](/tools/skills), [Skills 구성](/tools/skills-config)
