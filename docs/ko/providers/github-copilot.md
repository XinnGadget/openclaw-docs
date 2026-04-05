---
read_when:
    - 모델 공급자로 GitHub Copilot을 사용하려는 경우
    - '`openclaw models auth login-github-copilot` 흐름이 필요한 경우'
summary: 디바이스 플로우를 사용해 OpenClaw에서 GitHub Copilot에 로그인합니다
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-05T12:51:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 92857c119c314e698f922dbdbbc15d21b64d33a25979a2ec0ac1e82e586db6d6
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

## GitHub Copilot이란 무엇인가요?

GitHub Copilot은 GitHub의 AI 코딩 도우미입니다. GitHub 계정과 요금제에 대해 Copilot 모델에 대한 액세스를 제공합니다. OpenClaw는 두 가지 서로 다른 방식으로 Copilot을 모델 공급자로 사용할 수 있습니다.

## OpenClaw에서 Copilot을 사용하는 두 가지 방법

### 1) 내장 GitHub Copilot 공급자 (`github-copilot`)

기본 디바이스 로그인 흐름을 사용해 GitHub 토큰을 얻은 다음, OpenClaw 실행 시 이를 Copilot API 토큰으로 교환합니다. 이것이 **기본값**이며 VS Code가 필요하지 않기 때문에 가장 간단한 방법입니다.

### 2) Copilot Proxy plugin (`copilot-proxy`)

**Copilot Proxy** VS Code 확장을 로컬 브리지로 사용합니다. OpenClaw는 프록시의 `/v1` 엔드포인트와 통신하고, 그곳에서 구성한 모델 목록을 사용합니다. 이미 VS Code에서 Copilot Proxy를 실행 중이거나 이를 통해 라우팅해야 하는 경우 이 방법을 선택하세요. plugin을 활성화하고 VS Code 확장이 계속 실행되도록 유지해야 합니다.

GitHub Copilot을 모델 공급자(`github-copilot`)로 사용하세요. 로그인 명령은 GitHub 디바이스 플로우를 실행하고, 인증 프로필을 저장하며, 해당 프로필을 사용하도록 구성을 업데이트합니다.

## CLI 설정

```bash
openclaw models auth login-github-copilot
```

URL에 방문하여 일회용 코드를 입력하라는 메시지가 표시됩니다. 완료될 때까지 터미널을 열어 두세요.

### 선택적 플래그

```bash
openclaw models auth login-github-copilot --yes
```

공급자의 권장 기본 모델도 한 번에 적용하려면 대신 일반 인증 명령을 사용하세요:

```bash
openclaw models auth login --provider github-copilot --method device --set-default
```

## 기본 모델 설정

```bash
openclaw models set github-copilot/gpt-4o
```

### 구성 스니펫

```json5
{
  agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
}
```

## 참고 사항

- 대화형 TTY가 필요합니다. 터미널에서 직접 실행하세요.
- Copilot 모델 가용성은 요금제에 따라 달라집니다. 모델이 거부되면 다른 ID를 시도하세요(예: `github-copilot/gpt-4.1`).
- Claude 모델 ID는 자동으로 Anthropic Messages 전송 방식을 사용합니다. GPT, o-series, Gemini 모델은 OpenAI Responses 전송 방식을 유지합니다.
- 로그인은 GitHub 토큰을 인증 프로필 저장소에 저장하고, OpenClaw 실행 시 이를 Copilot API 토큰으로 교환합니다.
