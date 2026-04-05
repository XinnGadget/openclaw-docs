---
read_when:
    - 모델 인증 또는 OAuth 만료를 디버깅하는 경우
    - 인증 또는 자격 증명 저장소를 문서화하는 경우
summary: '모델 인증: OAuth, API 키, Claude CLI 재사용'
title: 인증
x-i18n:
    generated_at: "2026-04-05T12:41:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1c0ceee7d10fe8d10345f32889b63425d81773f3a08d8ecd3fd88d965b207ddc
    source_path: gateway/authentication.md
    workflow: 15
---

# 인증 (모델 provider)

<Note>
이 페이지는 **모델 provider** 인증(API 키, OAuth, Claude CLI 재사용)을 다룹니다. **gateway 연결** 인증(token, password, trusted-proxy)은 [Configuration](/gateway/configuration) 및 [Trusted Proxy Auth](/gateway/trusted-proxy-auth)를 참조하세요.
</Note>

OpenClaw는 모델 provider에 대해 OAuth와 API 키를 지원합니다. 항상 켜져 있는 gateway
호스트에서는 일반적으로 API 키가 가장 예측 가능한 옵션입니다. 구독/OAuth
흐름도 provider 계정 모델과 일치하면 지원됩니다.

전체 OAuth 흐름과 저장소
레이아웃은 [/concepts/oauth](/concepts/oauth)를 참조하세요.
SecretRef 기반 인증(`env`/`file`/`exec` provider)은 [Secrets Management](/gateway/secrets)를 참조하세요.
`models status --probe`에서 사용하는 자격 증명 적격성/이유 코드 규칙은
[Auth Credential Semantics](/auth-credential-semantics)를 참조하세요.

## 권장 설정(API 키, 모든 provider)

오래 실행되는 gateway를 운영하는 경우, 선택한
provider의 API 키로 시작하세요.
Anthropic의 경우 특히 API 키 인증이 안전한 경로입니다. Claude CLI 재사용은
다른 지원되는 구독형 설정 경로입니다.

1. provider 콘솔에서 API 키를 만드세요.
2. 이를 **gateway 호스트**(`openclaw gateway`를 실행하는 머신)에 설정하세요.

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Gateway가 systemd/launchd 아래에서 실행되는 경우, 데몬이 읽을 수 있도록
   `~/.openclaw/.env`에 키를 넣는 것을 권장합니다.

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

그런 다음 데몬을 재시작(또는 Gateway 프로세스를 재시작)하고 다시 확인하세요.

```bash
openclaw models status
openclaw doctor
```

환경 변수를 직접 관리하고 싶지 않다면, onboarding에서
데몬 사용을 위한 API 키를 저장할 수 있습니다: `openclaw onboard`.

환경 상속(`env.shellEnv`,
`~/.openclaw/.env`, systemd/launchd)에 대한 자세한 내용은 [Help](/help)를 참조하세요.

## Anthropic: 레거시 토큰 호환성

Anthropic setup-token 인증은 여전히 OpenClaw에서
레거시/수동 경로로 사용할 수 있습니다. Anthropic의 공개 Claude Code 문서는 여전히 직접적인
Claude Code 터미널 사용을 Claude 플랜 아래에서 다루지만, Anthropic은 별도로
OpenClaw 사용자에게 **OpenClaw** Claude 로그인 경로가 서드파티
harness 사용으로 간주되며 구독과 별도로 청구되는 **Extra Usage**가 필요하다고
알렸습니다.

가장 명확한 설정 경로는 Anthropic API 키를 사용하거나 gateway 호스트에서
Claude CLI로 마이그레이션하는 것입니다.

수동 토큰 입력(모든 provider, `auth-profiles.json` 기록 + config 업데이트):

```bash
openclaw models auth paste-token --provider openrouter
```

정적 자격 증명에는 auth profile ref도 지원됩니다.

- `api_key` 자격 증명은 `keyRef: { source, provider, id }`를 사용할 수 있습니다
- `token` 자격 증명은 `tokenRef: { source, provider, id }`를 사용할 수 있습니다
- OAuth 모드 profile은 SecretRef 자격 증명을 지원하지 않습니다. `auth.profiles.<id>.mode`가 `"oauth"`로 설정되어 있으면 해당 profile에 대한 SecretRef 기반 `keyRef`/`tokenRef` 입력은 거부됩니다.

자동화 친화적 검사(만료/누락 시 종료 코드 `1`, 곧 만료 시 `2`):

```bash
openclaw models status --check
```

라이브 인증 프로브:

```bash
openclaw models status --probe
```

참고:

- 프로브 행은 auth profile, env 자격 증명, 또는 `models.json`에서 올 수 있습니다.
- 명시적 `auth.order.<provider>`에 저장된 profile이 빠져 있으면, 프로브는
  해당 profile을 시도하는 대신 `excluded_by_auth_order`를 보고합니다.
- 인증은 존재하지만 OpenClaw가 해당 provider에 대해 프로브 가능한 모델 후보를 확인할 수 없으면,
  프로브는 `status: no_model`을 보고합니다.
- rate-limit 쿨다운은 모델 범위일 수 있습니다. 한
  모델에 대해 쿨다운 중인 profile이라도 같은 provider의 다른 모델에는 여전히 사용할 수 있습니다.

선택적 ops 스크립트(systemd/Termux)는 여기 문서화되어 있습니다:
[Auth monitoring scripts](/help/scripts#auth-monitoring-scripts)

## Anthropic: Claude CLI 마이그레이션

Claude CLI가 이미 gateway 호스트에 설치되어 로그인되어 있다면,
기존 Anthropic 설정을 CLI 백엔드로 전환할 수 있습니다. 이는 해당
호스트의 로컬 Claude CLI 로그인을 재사용하기 위한 지원되는 OpenClaw 마이그레이션 경로입니다.

사전 요구 사항:

- gateway 호스트에 `claude` 설치
- `claude auth login`으로 해당 위치에서 Claude CLI에 이미 로그인됨

```bash
openclaw models auth login --provider anthropic --method cli --set-default
```

이 작업은 롤백을 위해 기존 Anthropic auth profile은 유지하지만,
기본 모델 선택을 `claude-cli/...`로 바꾸고 일치하는 Claude CLI
허용 목록 항목을 `agents.defaults.models` 아래에 추가합니다.

확인:

```bash
openclaw models status
```

온보딩 바로가기:

```bash
openclaw onboard --auth-choice anthropic-cli
```

대화형 `openclaw onboard`와 `openclaw configure`는 Anthropic에 대해 여전히 Claude CLI를
우선하지만, Anthropic setup-token도 다시
레거시/수동 경로로 제공되며 Extra Usage 청구를 전제로 사용해야 합니다.

## 모델 인증 상태 확인

```bash
openclaw models status
openclaw doctor
```

## API 키 순환 동작(gateway)

일부 provider는 API 호출이 provider rate limit에
도달했을 때 대체 키로 요청을 재시도하는 것을 지원합니다.

- 우선순위 순서:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (단일 재정의)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Google provider는 추가 fallback으로 `GOOGLE_API_KEY`도 포함합니다.
- 동일한 키 목록은 사용 전에 중복 제거됩니다.
- OpenClaw는 rate-limit 오류에 대해서만 다음 키로 재시도합니다(예:
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many concurrent
requests`, `ThrottlingException`, `concurrency limit reached`, 또는
  `workers_ai ... quota limit exceeded`).
- rate-limit가 아닌 오류는 대체 키로 재시도하지 않습니다.
- 모든 키가 실패하면 마지막 시도의 최종 오류가 반환됩니다.

## 사용할 자격 증명 제어

### 세션별(채팅 명령)

현재 세션에 특정 provider 자격 증명을 고정하려면 `/model <alias-or-id>@<profileId>`를 사용하세요(예시 profile id: `anthropic:default`, `anthropic:work`).

간단한 선택기에는 `/model`(또는 `/model list`)을 사용하고, 전체 보기에는 `/model status`를 사용하세요(후보 + 다음 auth profile, 그리고 구성된 경우 provider 엔드포인트 세부 정보 포함).

### agent별(CLI 재정의)

agent에 대한 명시적 auth profile 순서 재정의를 설정합니다(해당 agent의 `auth-profiles.json`에 저장됨).

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

특정 agent를 대상으로 하려면 `--agent <id>`를 사용하고, 구성된 기본 agent를 사용하려면 생략하세요.
순서 문제를 디버깅할 때 `openclaw models status --probe`는 생략된
저장 profile을 조용히 건너뛰는 대신 `excluded_by_auth_order`로 표시합니다.
쿨다운 문제를 디버깅할 때는 rate-limit 쿨다운이
전체 provider profile이 아니라 하나의 모델 id에 묶여 있을 수 있다는 점을 기억하세요.

## 문제 해결

### "No credentials found"

Anthropic profile이 없으면, 해당 설정을 **gateway 호스트**에서 Claude CLI 또는 API
키로 마이그레이션한 다음 다시 확인하세요.

```bash
openclaw models status
```

### 토큰이 곧 만료되거나 이미 만료됨

어떤 profile이 곧 만료되는지 확인하려면 `openclaw models status`를 실행하세요. 레거시
Anthropic 토큰 profile이 없거나 만료되었다면, 해당 설정을 Claude CLI
또는 API 키로 마이그레이션하세요.

## Claude CLI 요구 사항

Anthropic Claude CLI 재사용 경로에만 필요합니다.

- Claude Code CLI 설치됨(`claude` 명령 사용 가능)
