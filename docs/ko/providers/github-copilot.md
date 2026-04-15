---
read_when:
    - 모델 제공자로 GitHub Copilot을 사용하려고 합니다
    - '`openclaw models auth login-github-copilot` 흐름이 필요합니다'
summary: 디바이스 플로우를 사용해 OpenClaw에서 GitHub Copilot에 로그인합니다
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-15T14:40:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8258fecff22fb73b057de878462941f6eb86d0c5f775c5eac4840e95ba5eccf
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot은 GitHub의 AI 코딩 도우미입니다. GitHub 계정과 요금제에 맞는 Copilot 모델에 액세스할 수 있습니다. OpenClaw는 Copilot을 모델 제공자로 두 가지 방식으로 사용할 수 있습니다.

## OpenClaw에서 Copilot을 사용하는 두 가지 방법

<Tabs>
  <Tab title="내장 제공자 (github-copilot)">
    OpenClaw가 실행될 때 GitHub 토큰을 얻기 위해 기본 디바이스 로그인 흐름을 사용한 다음, 이를 Copilot API 토큰으로 교환합니다. VS Code가 필요하지 않기 때문에 이것이 **기본값**이자 가장 간단한 방법입니다.

    <Steps>
      <Step title="로그인 명령 실행">
        ```bash
        openclaw models auth login-github-copilot
        ```

        URL로 이동하여 일회용 코드를 입력하라는 안내가 표시됩니다. 완료될 때까지 터미널을 열어 두세요.
      </Step>
      <Step title="기본 모델 설정">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        또는 config에서:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Copilot Proxy Plugin (copilot-proxy)">
    로컬 브리지로 **Copilot Proxy** VS Code 확장을 사용합니다. OpenClaw는 프록시의 `/v1` 엔드포인트와 통신하고, 그곳에서 구성한 모델 목록을 사용합니다.

    <Note>
    이미 VS Code에서 Copilot Proxy를 실행 중이거나 이를 통해 라우팅해야 할 때 이 방법을 선택하세요. Plugin을 활성화하고 VS Code 확장이 계속 실행 중이어야 합니다.
    </Note>

  </Tab>
</Tabs>

## 선택적 플래그

| Flag            | 설명                                         |
| --------------- | --------------------------------------------------- |
| `--yes`         | 확인 프롬프트 건너뛰기                        |
| `--set-default` | 제공자가 권장하는 기본 모델도 함께 적용 |

```bash
# 확인 건너뛰기
openclaw models auth login-github-copilot --yes

# 한 번에 로그인하고 기본 모델 설정
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="대화형 TTY 필요">
    디바이스 로그인 흐름에는 대화형 TTY가 필요합니다. 비대화형 스크립트나 CI 파이프라인이 아니라, 터미널에서 직접 실행하세요.
  </Accordion>

  <Accordion title="모델 사용 가능 여부는 요금제에 따라 달라집니다">
    Copilot 모델 사용 가능 여부는 GitHub 요금제에 따라 달라집니다. 모델이 거부되면 다른 ID(예: `github-copilot/gpt-4.1`)를 시도해 보세요.
  </Accordion>

  <Accordion title="전송 방식 선택">
    Claude 모델 ID는 자동으로 Anthropic Messages 전송 방식을 사용합니다. GPT, o-series, Gemini 모델은 OpenAI Responses 전송 방식을 유지합니다. OpenClaw는 모델 ref를 기준으로 올바른 전송 방식을 선택합니다.
  </Accordion>

  <Accordion title="환경 변수 확인 우선순위">
    OpenClaw는 다음 우선순위에 따라 환경 변수에서 Copilot 인증을 확인합니다:

    | Priority | Variable              | Notes                            |
    | -------- | --------------------- | -------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | 가장 높은 우선순위, Copilot 전용 |
    | 2        | `GH_TOKEN`            | GitHub CLI 토큰 (대체 수단)      |
    | 3        | `GITHUB_TOKEN`        | 표준 GitHub 토큰 (가장 낮음)   |

    여러 변수가 설정되어 있으면 OpenClaw는 가장 우선순위가 높은 변수를 사용합니다.
    디바이스 로그인 흐름(`openclaw models auth login-github-copilot`)은
    인증 프로필 저장소에 토큰을 저장하며 모든 환경 변수보다 우선합니다.

  </Accordion>

  <Accordion title="토큰 저장">
    로그인은 GitHub 토큰을 인증 프로필 저장소에 저장하고, OpenClaw가 실행될 때 이를 Copilot API 토큰으로 교환합니다. 토큰을 수동으로 관리할 필요는 없습니다.
  </Accordion>
</AccordionGroup>

<Warning>
대화형 TTY가 필요합니다. 로그인 명령은 헤드리스 스크립트나 CI 작업 내부가 아니라 터미널에서 직접 실행하세요.
</Warning>

## 메모리 검색 임베딩

GitHub Copilot은 [메모리 검색](/ko/concepts/memory-search)을 위한 임베딩 제공자로도 사용할 수 있습니다. Copilot 구독이 있고 로그인한 상태라면, OpenClaw는 별도의 API 키 없이도 이를 임베딩에 사용할 수 있습니다.

### 자동 감지

`memorySearch.provider`가 `"auto"`(기본값)일 때 GitHub Copilot은 우선순위 15로 시도됩니다. 즉, 로컬 임베딩 다음이면서 OpenAI 및 기타 유료 제공자보다 앞섭니다. GitHub 토큰을 사용할 수 있으면 OpenClaw는 Copilot API에서 사용 가능한 임베딩 모델을 찾아 자동으로 가장 적합한 모델을 선택합니다.

### 명시적 config

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "github-copilot",
        // 선택 사항: 자동으로 검색된 모델 재정의
        model: "text-embedding-3-small",
      },
    },
  },
}
```

### 작동 방식

1. OpenClaw가 GitHub 토큰을 확인합니다(환경 변수 또는 인증 프로필에서).
2. 이를 수명이 짧은 Copilot API 토큰으로 교환합니다.
3. Copilot `/models` 엔드포인트를 조회하여 사용 가능한 임베딩 모델을 찾습니다.
4. 가장 적합한 모델을 선택합니다(`text-embedding-3-small` 선호).
5. Copilot `/embeddings` 엔드포인트로 임베딩 요청을 보냅니다.

모델 사용 가능 여부는 GitHub 요금제에 따라 달라집니다. 사용할 수 있는 임베딩 모델이 없으면 OpenClaw는 Copilot을 건너뛰고 다음 제공자를 시도합니다.

## 관련 항목

<CardGroup cols={2}>
  <Card title="모델 선택" href="/ko/concepts/model-providers" icon="layers">
    제공자, 모델 ref, 장애 조치 동작 선택.
  </Card>
  <Card title="OAuth 및 인증" href="/ko/gateway/authentication" icon="key">
    인증 세부 정보와 자격 증명 재사용 규칙.
  </Card>
</CardGroup>
