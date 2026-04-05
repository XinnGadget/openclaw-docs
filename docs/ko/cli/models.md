---
read_when:
    - 기본 모델을 변경하거나 provider 인증 상태를 확인하려는 경우
    - 사용 가능한 모델/provider를 스캔하고 인증 프로필을 디버그하려는 경우
summary: '`openclaw models`용 CLI 참조(상태/목록/설정/스캔, 별칭, 대체 모델, 인증)'
title: models
x-i18n:
    generated_at: "2026-04-05T12:38:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 04ba33181d49b6bbf3b5d5fa413aa6b388c9f29fb9d4952055d68c79f7bcfea0
    source_path: cli/models.md
    workflow: 15
---

# `openclaw models`

모델 검색, 스캔 및 구성(기본 모델, 대체 모델, 인증 프로필).

관련 문서:

- Provider + 모델: [Models](/providers/models)
- Provider 인증 설정: [시작하기](/ko/start/getting-started)

## 공통 명령

```bash
openclaw models status
openclaw models list
openclaw models set <model-or-alias>
openclaw models scan
```

`openclaw models status`는 해석된 기본값/대체 모델과 인증 개요를 표시합니다.
provider 사용량 스냅샷을 사용할 수 있는 경우 OAuth/API 키 상태 섹션에는
provider 사용 기간과 할당량 스냅샷이 포함됩니다.
현재 사용 기간 provider: Anthropic, GitHub Copilot, Gemini CLI, OpenAI
Codex, MiniMax, Xiaomi, z.ai. 사용량 인증은 가능한 경우 provider별 훅에서
가져오며, 그렇지 않으면 OpenClaw는 인증 프로필, env 또는 config의
일치하는 OAuth/API 키 자격 증명으로 대체합니다.
구성된 각 provider 프로필에 대해 실시간 인증 프로브를 실행하려면 `--probe`를 추가하세요.
프로브는 실제 요청입니다(토큰을 소비하고 속도 제한을 유발할 수 있음).
구성된 에이전트의 모델/인증 상태를 검사하려면 `--agent <id>`를 사용하세요. 생략하면
명령은 설정된 경우 `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR`를 사용하고, 그렇지 않으면
구성된 기본 에이전트를 사용합니다.
프로브 행은 인증 프로필, env 자격 증명 또는 `models.json`에서 가져올 수 있습니다.

참고:

- `models set <model-or-alias>`는 `provider/model` 또는 별칭을 받습니다.
- 모델 ref는 **첫 번째** `/`를 기준으로 분할하여 파싱합니다. 모델 ID에 `/`가 포함된 경우(OpenRouter 스타일), provider 접두사를 포함하세요(예: `openrouter/moonshotai/kimi-k2`).
- provider를 생략하면 OpenClaw는 먼저 입력을 별칭으로 해석하고, 그다음
  정확한 모델 ID에 대한 고유한 구성 provider 일치 항목으로 해석하며, 그 이후에만
  더 이상 사용되지 않음을 알리는 경고와 함께 구성된 기본 provider로 대체합니다.
  해당 provider가 더 이상 구성된 기본 모델을 제공하지 않는 경우, OpenClaw는
  오래되어 제거된 provider 기본값을 표시하는 대신 첫 번째 구성된 provider/모델로 대체합니다.
- `models status`는 비밀이 아닌 플레이스홀더에 대해 인증 출력에서 비밀처럼 마스킹하지 않고 `marker(<value>)`를 표시할 수 있습니다(예: `OPENAI_API_KEY`, `secretref-managed`, `minimax-oauth`, `oauth:chutes`, `ollama-local`).

### `models status`

옵션:

- `--json`
- `--plain`
- `--check` (종료 코드 1=만료/누락, 2=만료 임박)
- `--probe` (구성된 인증 프로필의 실시간 프로브)
- `--probe-provider <name>` (하나의 provider 프로브)
- `--probe-profile <id>` (반복 또는 쉼표로 구분된 프로필 ID)
- `--probe-timeout <ms>`
- `--probe-concurrency <n>`
- `--probe-max-tokens <n>`
- `--agent <id>` (구성된 에이전트 ID, `OPENCLAW_AGENT_DIR`/`PI_CODING_AGENT_DIR` 재정의)

프로브 상태 버킷:

- `ok`
- `auth`
- `rate_limit`
- `billing`
- `timeout`
- `format`
- `unknown`
- `no_model`

예상되는 프로브 상세/이유 코드 사례:

- `excluded_by_auth_order`: 저장된 프로필은 존재하지만 명시적인
  `auth.order.<provider>`에 포함되지 않아, 프로브는 시도하는 대신
  제외 사실을 보고합니다.
- `missing_credential`, `invalid_expires`, `expired`, `unresolved_ref`:
  프로필은 존재하지만 적격하지 않거나 해석할 수 없습니다.
- `no_model`: provider 인증은 존재하지만, OpenClaw가 해당 provider에 대해
  프로브 가능한 모델 후보를 해석할 수 없었습니다.

## 별칭 + 대체 모델

```bash
openclaw models aliases list
openclaw models fallbacks list
```

## 인증 프로필

```bash
openclaw models auth add
openclaw models auth login --provider <id>
openclaw models auth setup-token --provider <id>
openclaw models auth paste-token
```

`models auth add`는 대화형 인증 도우미입니다. 선택한 provider에 따라
provider 인증 흐름(OAuth/API 키)을 시작하거나 수동 토큰 붙여넣기로 안내할 수 있습니다.

`models auth login`은 provider plugin의 인증 흐름(OAuth/API 키)을 실행합니다.
설치된 provider를 보려면 `openclaw plugins list`를 사용하세요.

예시:

```bash
openclaw models auth login --provider anthropic --method cli --set-default
openclaw models auth login --provider openai-codex --set-default
```

참고:

- `login --provider anthropic --method cli --set-default`는 로컬 Claude
  CLI 로그인을 재사용하고 메인 Anthropic 기본 모델 경로를 정식
  `claude-cli/claude-*` ref로 다시 씁니다.
- `setup-token`과 `paste-token`은 토큰 인증 방법을 노출하는 provider를 위한
  일반적인 토큰 명령으로 유지됩니다.
- `setup-token`은 대화형 TTY가 필요하며 provider의 토큰 인증
  메서드를 실행합니다(해당 provider가 노출하는 경우 기본적으로 그 provider의 `setup-token`
  메서드를 사용).
- `paste-token`은 다른 곳이나 자동화에서 생성된 토큰 문자열을 받습니다.
- `paste-token`은 `--provider`가 필요하고, 토큰 값을 묻는 프롬프트를 표시하며,
  `--profile-id`를 전달하지 않으면 기본 프로필 ID `<provider>:manual`에 기록합니다.
- `paste-token --expires-in <duration>`은 `365d` 또는 `12h` 같은
  상대 기간으로부터 절대 토큰 만료 시점을 저장합니다.
- Anthropic 과금 참고: Anthropic의 공개 CLI 문서를 기준으로 보면 Claude Code CLI 대체 경로는 로컬의 사용자 관리 자동화에는 허용될 가능성이 높다고 판단합니다. 다만, 외부 제품에서 구독 기반 사용에 대한 Anthropic의 서드파티 하니스 정책에는 충분한 모호성이 있어 프로덕션에서는 권장하지 않습니다. 또한 Anthropic은 **2026년 4월 4일 오후 12:00 PT / 오후 8:00 BST**에 OpenClaw 사용자에게 **OpenClaw** Claude 로그인 경로가 서드파티 하니스 사용으로 간주되며, 구독과 별도로 청구되는 **Extra Usage**가 필요하다고 알렸습니다.
- Anthropic `setup-token` / `paste-token`은 레거시/수동 OpenClaw 경로로 다시 사용할 수 있습니다. 이 경로는 Anthropic이 OpenClaw 사용자에게 **Extra Usage**가 필요하다고 안내한 점을 전제로 사용하세요.
