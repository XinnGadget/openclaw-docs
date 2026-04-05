---
read_when:
    - OpenClaw OAuth 전체 흐름을 이해하려는 경우
    - 토큰 무효화 / 로그아웃 문제가 발생한 경우
    - Claude CLI 또는 OAuth 인증 흐름이 필요한 경우
    - 여러 계정 또는 프로필 라우팅을 사용하려는 경우
summary: 'OpenClaw의 OAuth: 토큰 교환, 저장소 및 다중 계정 패턴'
title: OAuth
x-i18n:
    generated_at: "2026-04-05T12:40:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0b364be2182fcf9082834450f39aecc0913c85fb03237eec1228a589d4851dcd
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw는 이를 제공하는 provider에 대해 OAuth를 통한 “subscription auth”를 지원합니다
(특히 **OpenAI Codex (ChatGPT OAuth)**). Anthropic 구독의 경우 새
설정에서는 게이트웨이 호스트에서 로컬 **Claude CLI** 로그인 경로를 사용해야 하지만,
Anthropic은 직접 Claude Code를 사용하는 경우와 OpenClaw의 재사용 경로를 구분합니다.
Anthropic의 공개 Claude Code 문서에는 직접 Claude Code를 사용하는 경우
Claude 구독 한도 내에 머문다고 명시되어 있습니다. 별도로,
Anthropic은 **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에 OpenClaw
사용자에게 OpenClaw가 서드파티 하니스(third-party harness)로 간주되며 이제 해당 트래픽에 대해
**Extra Usage**가 필요하다고 통지했습니다.
OpenAI Codex OAuth는 OpenClaw 같은 외부 도구에서 사용하도록
명시적으로 지원됩니다. 이 페이지에서는 다음을 설명합니다.

프로덕션에서 Anthropic의 경우 API key 인증이 더 안전한 권장 경로입니다.

- OAuth **토큰 교환**이 작동하는 방식(PKCE)
- 토큰이 **저장되는** 위치(및 그 이유)
- **여러 계정**을 처리하는 방법(프로필 + 세션별 재정의)

OpenClaw는 자체 OAuth 또는 API‑key
흐름을 제공하는 **provider plugin**도 지원합니다. 다음으로 실행하세요:

```bash
openclaw models auth login --provider <id>
```

## 토큰 싱크(왜 존재하는가)

OAuth provider는 로그인/갱신 흐름 중에 종종 **새 refresh token**을 발급합니다. 일부 provider(또는 OAuth client)는 같은 사용자/앱에 대해 새 토큰이 발급되면 이전 refresh token을 무효화할 수 있습니다.

실제 증상:

- OpenClaw _및_ Claude Code / Codex CLI로 로그인하면 → 나중에 둘 중 하나가 무작위로 “로그아웃”됩니다

이를 줄이기 위해 OpenClaw는 `auth-profiles.json`을 **토큰 싱크**로 취급합니다.

- 런타임은 **한 곳**에서 자격 증명을 읽습니다
- 여러 프로필을 유지하고 이를 결정적으로 라우팅할 수 있습니다
- Codex CLI 같은 외부 CLI의 자격 증명을 재사용할 때 OpenClaw는
  출처 정보를 포함해 이를 미러링하고 refresh token 자체를 회전시키는 대신 해당 외부 소스를 다시 읽습니다

## 저장소(토큰이 저장되는 위치)

시크릿은 **에이전트별로** 저장됩니다.

- 인증 프로필(OAuth + API keys + 선택적 값 수준 ref): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- 레거시 호환성 파일: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (정적 `api_key` 항목은 발견 시 정리됨)

레거시 import 전용 파일(여전히 지원되지만 주 저장소는 아님):

- `~/.openclaw/credentials/oauth.json` (처음 사용할 때 `auth-profiles.json`으로 가져옴)

위 항목들은 모두 `$OPENCLAW_STATE_DIR`(state dir 재정의)도 따릅니다. 전체 참조: [/gateway/configuration](/gateway/configuration-reference#auth-storage)

정적 secret ref 및 런타임 스냅샷 활성화 동작은 [Secrets Management](/gateway/secrets)를 참조하세요.

## Anthropic 레거시 토큰 호환성

<Warning>
Anthropic의 공개 Claude Code 문서에는 직접 Claude Code를 사용하는 경우
Claude 구독 한도 내에 머문다고 명시되어 있습니다. 별도로 Anthropic은
**2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에 OpenClaw 사용자에게
**OpenClaw가 서드파티 하니스(third-party harness)로 간주된다**고 알렸습니다. 기존 Anthropic 토큰 프로필은 기술적으로는 OpenClaw에서 계속 사용할 수 있지만,
Anthropic은 이제 OpenClaw 경로의 해당 트래픽에 대해 **Extra
Usage**(구독과 별도로 청구되는 종량제)를 요구한다고 밝혔습니다.

Anthropic의 현재 직접-Claude-Code 요금제 문서는 [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
및 [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)을
참조하세요.

OpenClaw에서 다른 subscription 스타일 옵션을 원한다면 [OpenAI
Codex](/providers/openai), [Qwen Cloud Coding
Plan](/providers/qwen), [MiniMax Coding Plan](/providers/minimax),
및 [Z.AI / GLM Coding Plan](/providers/glm)을 참조하세요.
</Warning>

이제 OpenClaw는 Anthropic setup-token을 다시 레거시/수동 경로로 노출합니다.
Anthropic의 OpenClaw 전용 과금 공지는 이 경로에도 여전히 적용되므로,
Anthropic이 OpenClaw 기반 Claude 로그인 트래픽에 대해 **Extra Usage**를 요구한다는 점을
전제로 사용하세요.

## Anthropic Claude CLI 마이그레이션

게이트웨이 호스트에 Claude CLI가 이미 설치되어 있고 로그인되어 있다면,
Anthropic 모델 선택을 로컬 CLI 백엔드로 전환할 수 있습니다. 이는 동일한
호스트에서 로컬 Claude CLI 로그인을 재사용하려는 경우 지원되는 OpenClaw 경로입니다.

사전 요구 사항:

- 게이트웨이 호스트에 `claude` 바이너리가 설치되어 있어야 함
- Claude CLI가 해당 호스트에서 `claude auth login`으로 이미 인증되어 있어야 함

마이그레이션 명령:

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

온보딩 바로가기:

```bash
openclaw onboard --auth-choice anthropic-cli
```

이렇게 하면 롤백을 위해 기존 Anthropic 인증 프로필은 유지되지만, 기본
default-model 경로를 `anthropic/...`에서 `claude-cli/...`로 다시 쓰고, 일치하는
Anthropic Claude fallback도 다시 쓰며, `agents.defaults.models` 아래에
일치하는 `claude-cli/...` 허용 목록 항목을 추가합니다.

확인:

```bash
openclaw models status
```

## OAuth 교환(로그인 작동 방식)

OpenClaw의 대화형 로그인 흐름은 `@mariozechner/pi-ai`에 구현되어 있으며 wizard/command에 연결되어 있습니다.

### Anthropic Claude CLI

흐름 형태:

Claude CLI 경로:

1. 게이트웨이 호스트에서 `claude auth login`으로 로그인
2. `openclaw models auth login --provider anthropic --method cli --set-default` 실행
3. 새 인증 프로필은 저장하지 않고, 모델 선택만 `claude-cli/...`로 전환
4. 롤백을 위해 기존 Anthropic 인증 프로필은 유지

Anthropic의 공개 Claude Code 문서는 `claude` 자체에 대한 이 직접 Claude 구독
로그인 흐름을 설명합니다. OpenClaw는 이 로컬 로그인을 재사용할 수 있지만,
Anthropic은 과금 목적상 OpenClaw가 제어하는 경로를 별도로 서드파티
하니스 사용으로 분류합니다.

대화형 비서 경로:

- `openclaw onboard` / `openclaw configure` → 인증 선택 `anthropic-cli`

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth는 OpenClaw 워크플로를 포함하여 Codex CLI 외부에서 사용하도록 명시적으로 지원됩니다.

흐름 형태(PKCE):

1. PKCE verifier/challenge + 무작위 `state` 생성
2. `https://auth.openai.com/oauth/authorize?...` 열기
3. `http://127.0.0.1:1455/auth/callback`에서 콜백 캡처 시도
4. 콜백 바인딩이 안 되거나 원격/headless 환경이면 리디렉션 URL/code를 붙여넣기
5. `https://auth.openai.com/oauth/token`에서 교환
6. access token에서 `accountId`를 추출하고 `{ access, refresh, expires, accountId }` 저장

wizard 경로는 `openclaw onboard` → 인증 선택 `openai-codex`입니다.

## 갱신 + 만료

프로필은 `expires` 타임스탬프를 저장합니다.

런타임에서:

- `expires`가 미래 시점이면 → 저장된 access token 사용
- 만료되었으면 → refresh 수행(파일 잠금 하에서) 후 저장된 자격 증명 덮어쓰기
- 예외: 재사용된 외부 CLI 자격 증명은 외부에서 계속 관리되며, OpenClaw는
  CLI 인증 저장소를 다시 읽고 복사된 refresh token 자체는 절대 사용하지 않습니다

refresh 흐름은 자동으로 처리되므로 일반적으로 토큰을 수동 관리할 필요는 없습니다.

## 여러 계정(프로필) + 라우팅

두 가지 패턴이 있습니다.

### 1) 권장: 별도 에이전트

“personal”과 “work”가 절대 상호작용하지 않게 하려면, 격리된 에이전트(별도 세션 + 자격 증명 + 워크스페이스)를 사용하세요.

```bash
openclaw agents add work
openclaw agents add personal
```

그런 다음 에이전트별로 인증을 구성하고(wizard), 올바른 에이전트로 채팅을 라우팅하세요.

### 2) 고급: 하나의 에이전트에서 여러 프로필

`auth-profiles.json`은 같은 provider에 대해 여러 profile ID를 지원합니다.

사용할 프로필 선택 방법:

- config 순서(`auth.order`)를 통해 전역적으로
- `/model ...@<profileId>`를 통해 세션별로

예시(세션 재정의):

- `/model Opus@anthropic:work`

어떤 profile ID가 있는지 확인하는 방법:

- `openclaw channels list --json` (`auth[]` 표시)

관련 문서:

- [/concepts/model-failover](/concepts/model-failover) (회전 + 쿨다운 규칙)
- [/tools/slash-commands](/tools/slash-commands) (명령 표면)

## 관련

- [Authentication](/gateway/authentication) — 모델 provider 인증 개요
- [Secrets](/gateway/secrets) — 자격 증명 저장 및 SecretRef
- [Configuration Reference](/gateway/configuration-reference#auth-storage) — 인증 config 키
