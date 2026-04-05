---
read_when:
    - 스크립트나 CI에서 온보딩을 자동화하는 경우
    - 특정 프로바이더를 위한 비대화형 예제가 필요한 경우
sidebarTitle: CLI automation
summary: OpenClaw CLI용 스크립트 기반 온보딩 및 에이전트 설정
title: CLI 자동화
x-i18n:
    generated_at: "2026-04-05T12:55:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: a757d58df443e5e71f97417aed20e6a80a63b84f69f7dbf0e093319827d37836
    source_path: start/wizard-cli-automation.md
    workflow: 15
---

# CLI 자동화

`openclaw onboard`를 자동화하려면 `--non-interactive`를 사용하세요.

<Note>
`--json`은 비대화형 모드를 의미하지 않습니다. 스크립트에서는 `--non-interactive`(및 `--workspace`)를 사용하세요.
</Note>

## 기본 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

기계가 읽을 수 있는 요약이 필요하면 `--json`을 추가하세요.

인증 프로필에 일반 텍스트 값 대신 env 기반 ref를 저장하려면 `--secret-input-mode ref`를 사용하세요.
env ref와 구성된 프로바이더 ref(`file` 또는 `exec`) 사이의 대화형 선택은 온보딩 흐름에서 사용할 수 있습니다.

비대화형 `ref` 모드에서는 프로바이더 env var가 프로세스 환경에 설정되어 있어야 합니다.
이제 일치하는 env var 없이 인라인 키 플래그를 전달하면 즉시 실패합니다.

예시:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## 프로바이더별 예시

<AccordionGroup>
  <Accordion title="Anthropic Claude CLI 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice anthropic-cli \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    Claude CLI가 동일한 Gateway 호스트에 이미 설치되어 있고 로그인되어 있어야 합니다.

  </Accordion>
  <Accordion title="Gemini 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice gemini-api-key \
      --gemini-api-key "$GEMINI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Z.AI 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice zai-api-key \
      --zai-api-key "$ZAI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Vercel AI Gateway 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ai-gateway-api-key \
      --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Cloudflare AI Gateway 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice cloudflare-ai-gateway-api-key \
      --cloudflare-ai-gateway-account-id "your-account-id" \
      --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
      --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Moonshot 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice moonshot-api-key \
      --moonshot-api-key "$MOONSHOT_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Mistral 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice mistral-api-key \
      --mistral-api-key "$MISTRAL_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Synthetic 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice synthetic-api-key \
      --synthetic-api-key "$SYNTHETIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="OpenCode 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice opencode-zen \
      --opencode-zen-api-key "$OPENCODE_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
    Go 카탈로그를 사용하려면 `--auth-choice opencode-go --opencode-go-api-key "$OPENCODE_API_KEY"`로 바꾸세요.
  </Accordion>
  <Accordion title="Ollama 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ollama \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="사용자 지정 프로바이더 예시">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --custom-api-key "$CUSTOM_API_KEY" \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    `--custom-api-key`는 선택 사항입니다. 생략하면 온보딩이 `CUSTOM_API_KEY`를 확인합니다.

    ref 모드 변형:

    ```bash
    export CUSTOM_API_KEY="your-key"
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --secret-input-mode ref \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    이 모드에서 온보딩은 `apiKey`를 `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`로 저장합니다.

  </Accordion>
</AccordionGroup>

Anthropic setup-token은 레거시/수동 온보딩 경로로 다시 사용할 수 있습니다.
Anthropic이 OpenClaw 사용자에게 OpenClaw Claude 로그인 경로에는 **Extra Usage**가 필요하다고 안내했다는 점을 전제로 사용하세요. 프로덕션에서는 Anthropic API 키를 우선 사용하세요.

## 다른 에이전트 추가

별도의 워크스페이스, 세션 및 인증 프로필을 가진 별도 에이전트를 만들려면 `openclaw agents add <name>`을 사용하세요. `--workspace` 없이 실행하면 마법사가 시작됩니다.

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

설정되는 항목:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

참고:

- 기본 워크스페이스는 `~/.openclaw/workspace-<agentId>` 형식을 따릅니다.
- 인바운드 메시지를 라우팅하려면 `bindings`를 추가하세요(마법사로 설정 가능).
- 비대화형 플래그: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## 관련 문서

- 온보딩 허브: [온보딩(CLI)](/ko/start/wizard)
- 전체 참조: [CLI 설정 참조](/start/wizard-cli-reference)
- 명령 참조: [`openclaw onboard`](/cli/onboard)
