---
read_when:
    - OpenClaw에서 Anthropic 모델을 사용하려는 경우
    - 게이트웨이 호스트에서 Claude CLI 구독 인증을 재사용하려는 경우
summary: API 키 또는 Claude CLI를 사용해 OpenClaw에서 Anthropic Claude를 사용합니다
title: Anthropic
x-i18n:
    generated_at: "2026-04-05T12:52:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 80f2b614eba4563093522e5157848fc54a16770a2fae69f17c54f1b9bfff624f
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic는 **Claude** 모델 제품군을 개발하며 API를 통해 액세스를 제공합니다.
OpenClaw에서는 새로운 Anthropic 설정에 API 키 또는 로컬 Claude CLI
백엔드를 사용해야 합니다. 이미 구성된 기존 레거시 Anthropic 토큰 프로필은
런타임에서 계속 존중됩니다.

<Warning>
Anthropic의 공개 Claude Code 문서는 `claude -p` 같은 비대화형 CLI
사용법을 명시적으로 문서화하고 있습니다. 해당 문서를 바탕으로 볼 때, 로컬에서
사용자가 관리하는 Claude Code CLI 폴백은 허용될 가능성이 높다고 판단합니다.

이와는 별도로, Anthropic는 **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에
OpenClaw 사용자에게 **OpenClaw가 서드파티 harness로 간주된다**고 알렸습니다.
그들의 명시된 정책에 따르면, OpenClaw가 구동하는 Claude 로그인 트래픽은 더 이상
포함된 Claude 구독 풀을 사용하지 않으며 대신 **Extra Usage**
(사용량 기반 과금, 구독과 별도 청구)가 필요합니다.

이 정책 구분은 **OpenClaw가 구동하는 Claude CLI 재사용**에 관한 것이지,
자신의 터미널에서 직접 `claude`를 실행하는 것에 대한 것은 아닙니다. 다만,
Anthropic의 서드파티 harness 정책은 외부 제품에서의 구독 기반 사용에 대해
여전히 충분한 모호성을 남기고 있으므로, 저희는 이 경로를 프로덕션용으로 권장하지 않습니다.

Anthropic의 현재 공개 문서:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

가장 명확한 과금 경로를 원한다면 Anthropic API 키를 사용하세요.
OpenClaw는 또한 [OpenAI
Codex](/providers/openai), [Qwen Cloud Coding Plan](/providers/qwen),
[MiniMax Coding Plan](/providers/minimax), [Z.AI / GLM Coding
Plan](/providers/glm)을 포함한 다른 구독형 옵션도 지원합니다.
</Warning>

## 옵션 A: Anthropic API 키

**가장 적합한 경우:** 표준 API 액세스 및 사용량 기반 과금.
Anthropic Console에서 API 키를 생성하세요.

### CLI 설정

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Claude CLI 구성 스니펫

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## thinking 기본값 (Claude 4.6)

- Anthropic Claude 4.6 모델은 명시적인 thinking 수준이 설정되지 않은 경우 OpenClaw에서 기본적으로 `adaptive` thinking을 사용합니다.
- 메시지별로 (`/think:<level>`) 또는 모델 params에서 재정의할 수 있습니다:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- 관련 Anthropic 문서:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Fast mode (Anthropic API)

OpenClaw의 공용 `/fast` 토글은 API 키 및 OAuth 인증 요청을 포함해 `api.anthropic.com`으로 전송되는 직접적인 공개 Anthropic 트래픽도 지원합니다.

- `/fast on`은 `service_tier: "auto"`에 매핑됩니다
- `/fast off`는 `service_tier: "standard_only"`에 매핑됩니다
- 구성 기본값:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

중요한 제한 사항:

- OpenClaw는 직접적인 `api.anthropic.com` 요청에 대해서만 Anthropic 서비스 티어를 주입합니다. `anthropic/*`를 프록시 또는 게이트웨이를 통해 라우팅하는 경우 `/fast`는 `service_tier`를 변경하지 않습니다.
- 명시적인 Anthropic `serviceTier` 또는 `service_tier` 모델 params가 설정되어 있으면 둘 다 설정된 경우 `/fast` 기본값보다 우선합니다.
- Anthropic는 응답의 `usage.service_tier` 아래에 실제 티어를 보고합니다. Priority Tier 용량이 없는 계정에서는 `service_tier: "auto"`가 여전히 `standard`로 해석될 수 있습니다.

## 프롬프트 캐싱 (Anthropic API)

OpenClaw는 Anthropic의 프롬프트 캐싱 기능을 지원합니다. 이것은 **API 전용**이며, 레거시 Anthropic 토큰 인증은 캐시 설정을 존중하지 않습니다.

### 구성

모델 구성에서 `cacheRetention` 파라미터를 사용하세요:

| 값      | 캐시 기간 | 설명                     |
| ------- | --------- | ------------------------ |
| `none`  | 캐싱 없음 | 프롬프트 캐싱 비활성화   |
| `short` | 5분       | API Key 인증의 기본값    |
| `long`  | 1시간     | 확장 캐시                |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### 기본값

Anthropic API Key 인증을 사용하는 경우, OpenClaw는 모든 Anthropic 모델에 대해 자동으로 `cacheRetention: "short"`(5분 캐시)를 적용합니다. 구성에서 `cacheRetention`을 명시적으로 설정하여 이를 재정의할 수 있습니다.

### 에이전트별 cacheRetention 재정의

모델 수준 params를 기준선으로 사용한 다음, `agents.list[].params`를 통해 특정 에이전트를 재정의하세요.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // 대부분의 에이전트에 대한 기준선
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // 이 에이전트에만 적용되는 재정의
    ],
  },
}
```

캐시 관련 params의 구성 병합 순서:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (`id`가 일치할 때 키별로 재정의)

이렇게 하면 동일한 모델을 사용하는 한 에이전트는 장시간 캐시를 유지하고, 다른 에이전트는 급증하거나 재사용이 적은 트래픽에서 쓰기 비용을 피하기 위해 캐싱을 비활성화할 수 있습니다.

### Bedrock Claude 참고 사항

- Bedrock의 Anthropic Claude 모델(`amazon-bedrock/*anthropic.claude*`)은 구성된 경우 `cacheRetention` 전달을 허용합니다.
- Anthropic가 아닌 Bedrock 모델은 런타임에서 강제로 `cacheRetention: "none"`이 적용됩니다.
- Anthropic API 키 스마트 기본값은 명시적인 값이 설정되지 않은 경우 Claude-on-Bedrock 모델 참조에도 `cacheRetention: "short"`를 기본 적용합니다.

## 1M 컨텍스트 윈도우 (Anthropic beta)

Anthropic의 1M 컨텍스트 윈도우는 beta 게이트가 적용됩니다. OpenClaw에서는
지원되는 Opus/Sonnet 모델별로 `params.context1m: true`를 설정해 이를 활성화합니다.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw는 이를 Anthropic 요청의 `anthropic-beta: context-1m-2025-08-07`로
매핑합니다.

이 기능은 해당 모델에 대해 `params.context1m`이 명시적으로 `true`로 설정된 경우에만
활성화됩니다.

요구 사항: Anthropic가 해당 자격 증명에서 긴 컨텍스트 사용을 허용해야 합니다
(일반적으로 API 키 과금 또는 Extra Usage가 활성화된 OpenClaw의 Claude 로그인 경로 /
레거시 토큰 인증). 그렇지 않으면 Anthropic는 다음을 반환합니다:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

참고: Anthropic는 현재 레거시 Anthropic 토큰 인증(`sk-ant-oat-*`)을 사용할 때
`context-1m-*` beta 요청을 거부합니다. 이 레거시 인증 모드에서
`context1m: true`를 구성하면, OpenClaw는 경고를 기록하고
필수 OAuth betas는 유지하면서 context1m beta
헤더를 건너뛰어 표준 컨텍스트 윈도우로 폴백합니다.

## 옵션 B: 메시지 provider로 Claude CLI 사용

**가장 적합한 경우:** Claude CLI가 이미 설치되어 있고 로그인된 단일 사용자
게이트웨이 호스트에서, 권장되는 프로덕션 경로가 아닌 로컬 폴백으로 사용할 때.

과금 참고: Anthropic의 공개 CLI 문서를 바탕으로, 로컬에서 사용자가 관리하는 자동화를 위한 Claude Code CLI 폴백은 허용될 가능성이 높다고 판단합니다. 다만,
Anthropic의 서드파티 harness 정책은 외부 제품에서의 구독 기반 사용에 대해
충분한 모호성을 만들기 때문에, 저희는 프로덕션용으로 이를 권장하지 않습니다.
Anthropic는 또한 OpenClaw 사용자에게 **OpenClaw가 구동하는** Claude
CLI 사용은 서드파티 harness 트래픽으로 처리되며, **2026년 4월 4일
오후 12:00 PT / 오후 8:00 PM BST**부터 포함된 Claude 구독 한도 대신
**Extra Usage**가 필요하다고 알렸습니다.

이 경로는 Anthropic API를 직접 호출하는 대신 모델 추론에 로컬 `claude` 바이너리를 사용합니다. OpenClaw는 이를 다음과 같은 모델 참조를 가진 **CLI backend provider**로 취급합니다:

- `claude-cli/claude-sonnet-4-6`
- `claude-cli/claude-opus-4-6`

작동 방식:

1. OpenClaw는 **게이트웨이 호스트**에서 `claude -p --output-format stream-json --include-partial-messages ...`
   를 실행하고 stdin을 통해 프롬프트를 전송합니다.
2. 첫 번째 턴에서는 `--session-id <uuid>`를 전송합니다.
3. 후속 턴에서는 저장된 Claude 세션을 `--resume <sessionId>`로 재사용합니다.
4. 채팅 메시지는 여전히 일반 OpenClaw 메시지 파이프라인을 거치지만,
   실제 모델 응답은 Claude CLI가 생성합니다.

### 요구 사항

- 게이트웨이 호스트에 Claude CLI가 설치되어 있고 PATH에서 사용할 수 있거나,
  절대 명령 경로로 구성되어 있어야 합니다.
- Claude CLI가 동일한 호스트에서 이미 인증되어 있어야 합니다:

```bash
claude auth status
```

- 구성에서 `claude-cli/...` 또는 `claude-cli` backend config를 명시적으로 참조하면 OpenClaw는 게이트웨이 시작 시 번들된 Anthropic plugin을 자동으로 로드합니다.

### 구성 스니펫

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "claude-cli/claude-sonnet-4-6",
      },
      models: {
        "claude-cli/claude-sonnet-4-6": {},
      },
      sandbox: { mode: "off" },
    },
  },
}
```

게이트웨이 호스트 PATH에 `claude` 바이너리가 없는 경우:

```json5
{
  agents: {
    defaults: {
      cliBackends: {
        "claude-cli": {
          command: "/opt/homebrew/bin/claude",
        },
      },
    },
  },
}
```

### 제공되는 기능

- 로컬 CLI에서 Claude 구독 인증 재사용(런타임에 읽고, 저장되지는 않음)
- 일반적인 OpenClaw 메시지/세션 라우팅
- 턴 간 Claude CLI 세션 연속성(인증 변경 시 무효화됨)
- loopback MCP bridge를 통해 Claude CLI에 노출되는 게이트웨이 도구
- 라이브 partial-message 진행 상황이 포함된 JSONL 스트리밍

### Anthropic 인증에서 Claude CLI로 마이그레이션

현재 레거시 토큰 프로필 또는 API 키와 함께 `anthropic/...`를 사용 중이고
동일한 게이트웨이 호스트를 Claude CLI로 전환하려는 경우, OpenClaw는 이를 일반적인
provider-auth 마이그레이션 경로로 지원합니다.

사전 요구 사항:

- OpenClaw를 실행하는 **동일한 게이트웨이 호스트**에 Claude CLI 설치
- 해당 위치에서 Claude CLI에 이미 로그인됨: `claude auth login`

그런 다음 다음을 실행하세요:

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

또는 onboarding에서:

```bash
openclaw onboard --auth-choice anthropic-cli
```

대화형 `openclaw onboard` 및 `openclaw configure`는 이제 **Anthropic
Claude CLI**를 먼저, **Anthropic API key**를 두 번째로 우선합니다.

이 작업이 수행하는 내용:

- Claude CLI가 게이트웨이 호스트에서 이미 로그인되어 있는지 확인
- 기본 모델을 `claude-cli/...`로 전환
- `anthropic/claude-opus-4-6` 같은 Anthropic 기본 모델 폴백을
  `claude-cli/claude-opus-4-6`로 다시 작성
- `agents.defaults.models`에 일치하는 `claude-cli/...` 항목 추가

빠른 확인:

```bash
openclaw models status
```

해결된 기본 모델이 `claude-cli/...` 아래에 표시되어야 합니다.

수행하지 **않는** 작업:

- 기존 Anthropic 인증 프로필 삭제
- 기본 default
  model/allowlist 경로 외부의 오래된 `anthropic/...` config 참조를 모두 제거

따라서 롤백은 간단합니다. 필요하면 기본 모델을 다시 `anthropic/...`로 변경하면 됩니다.

### 중요한 제한 사항

- 이것은 **Anthropic API provider**가 아닙니다. 로컬 CLI 런타임입니다.
- OpenClaw는 tool call을 직접 주입하지 않습니다. Claude CLI는 loopback MCP bridge를 통해 게이트웨이 도구를 받습니다(`bundleMcp: true`, 기본값).
- Claude CLI는 JSONL(`stream-json` 및
  `--include-partial-messages`)을 통해 응답을 스트리밍합니다. 프롬프트는 argv가 아니라 stdin을 통해 전송됩니다.
- 인증은 라이브 Claude CLI 자격 증명에서 런타임에 읽어 오며 OpenClaw 프로필에 저장되지
  않습니다. 비대화형 컨텍스트에서는 키체인 프롬프트가 억제됩니다.
- 세션 재사용은 `cliSessionBinding` 메타데이터를 통해 추적됩니다. Claude CLI
  로그인 상태가 변경되면(재로그인, 토큰 교체) 저장된 세션이
  무효화되고 새로운 세션이 시작됩니다.
- 공유된 다중 사용자 과금 설정이 아니라 개인 게이트웨이 호스트에 가장 적합합니다.

자세한 내용: [/gateway/cli-backends](/ko/gateway/cli-backends)

## 참고

- Anthropic의 공개 Claude Code 문서는 여전히
  `claude -p` 같은 직접 CLI 사용을 문서화하고 있습니다. 저희는 로컬에서 사용자가 관리하는 폴백은 허용될 가능성이 높다고 판단하지만,
  Anthropic가 OpenClaw 사용자에게 보낸 별도 안내에 따르면 **OpenClaw**
  Claude 로그인 경로는 서드파티 harness 사용으로 간주되며 **Extra Usage**
  (구독과 별도로 청구되는 사용량 기반 과금)가 필요합니다. 프로덕션에서는 대신
  Anthropic API 키를 권장합니다.
- Anthropic setup-token은 이제 OpenClaw에서 다시 레거시/수동 경로로 사용할 수 있습니다. Anthropic의 OpenClaw 관련 과금 안내는 여전히 적용되므로, 이 경로에는 Anthropic가 **Extra Usage**를 요구한다는 전제로 사용하세요.
- 인증 세부 정보 및 재사용 규칙은 [/concepts/oauth](/ko/concepts/oauth)에 있습니다.

## 문제 해결

**401 오류 / 토큰이 갑자기 유효하지 않음**

- 레거시 Anthropic 토큰 인증은 만료되거나 취소될 수 있습니다.
- 새로 설정하는 경우, Anthropic API 키 또는 게이트웨이 호스트의 로컬 Claude CLI 경로로 마이그레이션하세요.

**provider "anthropic"에 대한 API 키를 찾을 수 없음**

- 인증은 **에이전트별**입니다. 새 에이전트는 메인 에이전트의 키를 상속하지 않습니다.
- 해당 에이전트에 대해 onboarding을 다시 실행하거나, 게이트웨이
  호스트에서 API 키를 구성한 다음 `openclaw models status`로 확인하세요.

**프로필 `anthropic:default`에 대한 자격 증명을 찾을 수 없음**

- `openclaw models status`를 실행해 어떤 인증 프로필이 활성 상태인지 확인하세요.
- onboarding을 다시 실행하거나, 해당 프로필 경로에 API 키 또는 Claude CLI를 구성하세요.

**사용 가능한 인증 프로필이 없음(모두 cooldown/unavailable 상태)**

- `auth.unusableProfiles`는 `openclaw models status --json`에서 확인하세요.
- Anthropic rate-limit cooldown은 모델 범위일 수 있으므로, 현재 모델이 cooldown 중이어도 같은 Anthropic
  모델 계열의 다른 모델은 여전히 사용 가능할 수 있습니다.
- 다른 Anthropic 프로필을 추가하거나 cooldown이 끝날 때까지 기다리세요.

더 보기: [/gateway/troubleshooting](/ko/gateway/troubleshooting) 및 [/help/faq](/ko/help/faq).
