---
read_when:
    - CLI 온보딩 실행 또는 구성 시
    - 새 머신 설정 시
sidebarTitle: 'Onboarding: CLI'
summary: 'CLI 온보딩: gateway, workspace, channels, Skills를 위한 안내형 설정'
title: 온보딩 (CLI)
x-i18n:
    generated_at: "2026-04-05T10:49:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 81e33fb4f8be30e7c2c6e0024bf9bdcf48583ca58eaf5fff5afd37a1cd628523
    source_path: start/wizard.md
    workflow: 15
---

# 온보딩 (CLI)

CLI 온보딩은 macOS,
Linux 또는 Windows(WSL2 경유, 강력 권장)에서 OpenClaw를 설정하는 **권장** 방식입니다.
하나의 안내형 흐름 안에서 로컬 Gateway 또는 원격 Gateway 연결과 채널, Skills,
워크스페이스 기본값을 구성합니다.

```bash
openclaw onboard
```

<Info>
가장 빠른 첫 채팅: Control UI를 여세요(채널 설정 불필요). `openclaw dashboard`를 실행하고 브라우저에서 채팅하세요. 문서: [대시보드](/web/dashboard).
</Info>

나중에 다시 구성하려면:

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json`은 비대화형 모드를 의미하지 않습니다. 스크립트에서는 `--non-interactive`를 사용하세요.
</Note>

<Tip>
CLI 온보딩에는 Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG, Tavily 등의 제공자를 선택할 수 있는 웹 검색 단계가 포함됩니다. 일부 제공자는
API 키가 필요하지만, 다른 제공자는 키가 필요하지 않습니다. 나중에
`openclaw configure --section web`로도 이를 구성할 수 있습니다. 문서: [웹 도구](/tools/web).
</Tip>

## QuickStart 대 Advanced

온보딩은 **QuickStart**(기본값)와 **Advanced**(전체 제어) 중에서 시작합니다.

<Tabs>
  <Tab title="QuickStart (기본값)">
    - 로컬 게이트웨이 (loopback)
    - 워크스페이스 기본값(또는 기존 워크스페이스)
    - Gateway 포트 **18789**
    - Gateway 인증 **Token**(loopback에서도 자동 생성)
    - 새 로컬 설정의 기본 도구 정책: `tools.profile: "coding"`(기존 명시적 프로필은 유지됨)
    - 기본 DM 격리: 로컬 온보딩은 설정되지 않은 경우 `session.dmScope: "per-channel-peer"`를 기록합니다. 자세한 내용: [CLI 설정 참조](/start/wizard-cli-reference#outputs-and-internals)
    - Tailscale 노출 **끔**
    - Telegram + WhatsApp DM 기본값은 **allowlist**(전화번호를 묻는 메시지가 표시됨)
  </Tab>
  <Tab title="Advanced (전체 제어)">
    - 모든 단계(모드, 워크스페이스, gateway, 채널, daemon, Skills)를 노출합니다.
  </Tab>
</Tabs>

## 온보딩이 구성하는 항목

**로컬 모드(기본값)**는 다음 단계를 안내합니다:

1. **모델/인증** — 지원되는 모든 제공자/인증 흐름(API 키, OAuth 또는 제공자별 수동 인증 포함)과 Custom Provider
   (OpenAI 호환, Anthropic 호환 또는 Unknown 자동 감지)를 선택합니다. 기본 모델을 선택하세요.
   보안 참고: 이 에이전트가 도구를 실행하거나 webhook/hooks 콘텐츠를 처리할 경우, 가능한 가장 강력한 최신 세대 모델을 사용하고 도구 정책을 엄격하게 유지하세요. 더 약하거나 오래된 등급은 프롬프트 인젝션에 더 취약합니다.
   비대화형 실행에서는 `--secret-input-mode ref`가 일반 텍스트 API 키 값 대신 환경 변수 기반 ref를 인증 프로필에 저장합니다.
   비대화형 `ref` 모드에서는 제공자 환경 변수가 설정되어 있어야 하며, 해당 환경 변수 없이 인라인 키 플래그를 전달하면 즉시 실패합니다.
   대화형 실행에서는 보안 참조 모드를 선택하면 저장 전에 빠른 사전 검증과 함께 환경 변수 또는 구성된 제공자 ref(`file` 또는 `exec`)를 가리킬 수 있습니다.
   Anthropic의 경우 대화형 onboarding/configure는 로컬 대체 수단으로 **Anthropic Claude CLI**를, 권장 프로덕션 경로로 **Anthropic API key**를 제공합니다. Anthropic setup-token도 Anthropic의 OpenClaw 전용 **Extra Usage** 과금 기대와 함께 레거시/수동 OpenClaw 경로로 다시 사용할 수 있습니다.
2. **워크스페이스** — 에이전트 파일의 위치(기본값 `~/.openclaw/workspace`). 부트스트랩 파일을 시드합니다.
3. **Gateway** — 포트, bind 주소, 인증 모드, Tailscale 노출.
   대화형 token 모드에서는 기본 일반 텍스트 token 저장소를 선택하거나 SecretRef를 선택할 수 있습니다.
   비대화형 token SecretRef 경로: `--gateway-token-ref-env <ENV_VAR>`.
4. **채널** — BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp 등과 같은 내장 및 번들 채팅 채널.
5. **Daemon** — LaunchAgent(macOS), systemd 사용자 유닛(Linux/WSL2) 또는 사용자별 Startup-folder 대체 경로가 있는 네이티브 Windows Scheduled Task를 설치합니다.
   token 인증에 token이 필요하고 `gateway.auth.token`이 SecretRef로 관리되는 경우, daemon 설치는 이를 검증하지만 확인된 token을 supervisor 서비스 환경 메타데이터에 유지하지는 않습니다.
   token 인증에 token이 필요하고 구성된 token SecretRef를 확인할 수 없는 경우, daemon 설치는 실행 가능한 안내와 함께 차단됩니다.
   `gateway.auth.token`과 `gateway.auth.password`가 모두 구성되어 있고 `gateway.auth.mode`가 설정되지 않은 경우, mode를 명시적으로 설정할 때까지 daemon 설치가 차단됩니다.
6. **상태 확인** — Gateway를 시작하고 실행 중인지 확인합니다.
7. **Skills** — 권장 Skills 및 선택적 종속성을 설치합니다.

<Note>
온보딩을 다시 실행해도 **Reset**을 명시적으로 선택하지 않는 한(또는 `--reset`을 전달하지 않는 한) 어떤 것도 지워지지 않습니다.
CLI `--reset`의 기본 대상은 config, credentials, sessions이며, workspace까지 포함하려면 `--reset-scope full`을 사용하세요.
config가 유효하지 않거나 레거시 키를 포함하고 있으면, 온보딩은 먼저 `openclaw doctor`를 실행하라고 안내합니다.
</Note>

**원격 모드**는 로컬 클라이언트가 다른 곳의 Gateway에 연결하도록만 구성합니다.
원격 호스트에는 아무것도 설치하거나 변경하지 않습니다.

## 다른 에이전트 추가

`openclaw agents add <name>`를 사용하면 자체 워크스페이스,
세션, 인증 프로필을 가진 별도의 에이전트를 만들 수 있습니다. `--workspace` 없이 실행하면 온보딩이 시작됩니다.

설정되는 항목:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

참고:

- 기본 워크스페이스는 `~/.openclaw/workspace-<agentId>` 형식을 따릅니다.
- 인바운드 메시지를 라우팅하려면 `bindings`를 추가하세요(온보딩에서 이 작업을 수행할 수 있음).
- 비대화형 플래그: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## 전체 참조

자세한 단계별 설명과 config 출력은
[CLI 설정 참조](/start/wizard-cli-reference)를 참조하세요.
비대화형 예시는 [CLI 자동화](/start/wizard-cli-automation)를 참조하세요.
RPC 세부 정보를 포함한 더 깊은 기술 참조는
[온보딩 참조](/reference/wizard)를 참조하세요.

## 관련 문서

- CLI 명령 참조: [`openclaw onboard`](/cli/onboard)
- 온보딩 개요: [온보딩 개요](/start/onboarding-overview)
- macOS 앱 온보딩: [온보딩](/start/onboarding)
- 에이전트 첫 실행 의식: [에이전트 부트스트래핑](/start/bootstrapping)
