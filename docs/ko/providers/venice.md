---
read_when:
    - OpenClaw에서 개인정보 보호 중심 추론을 사용하려는 경우
    - Venice AI 설정 가이드가 필요한 경우
summary: OpenClaw에서 Venice AI의 개인정보 보호 중심 모델 사용하기
title: Venice AI
x-i18n:
    generated_at: "2026-04-05T12:53:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 53313e45e197880feb7e90764ee8fd6bb7f5fd4fe03af46b594201c77fbc8eab
    source_path: providers/venice.md
    workflow: 15
---

# Venice AI (Venice 하이라이트)

**Venice**는 선택적으로 proprietary 모델에 익명화된 액세스를 제공하는, 개인정보 보호 우선 추론을 위한 추천 Venice 설정입니다.

Venice AI는 검열 없는 모델 지원과 익명화된 프록시를 통한 주요 proprietary 모델 액세스를 포함한 개인정보 보호 중심 AI 추론을 제공합니다. 모든 추론은 기본적으로 비공개입니다. 데이터 학습 없음, 로깅 없음.

## OpenClaw에서 Venice를 사용하는 이유

- 오픈 소스 모델을 위한 **비공개 추론**(로깅 없음)
- 필요할 때 사용할 수 있는 **검열 없는 모델**
- 품질이 중요할 때 사용할 수 있는 proprietary 모델(Opus/GPT/Gemini)에 대한 **익명화된 액세스**
- OpenAI 호환 `/v1` 엔드포인트

## 개인정보 보호 모드

Venice는 두 가지 개인정보 보호 수준을 제공합니다. 적절한 모델을 선택하려면 이를 이해하는 것이 중요합니다.

| 모드 | 설명 | 모델 |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| **비공개** | 완전히 비공개입니다. 프롬프트/응답은 **절대 저장되거나 기록되지 않습니다**. 일시적입니다. | Llama, Qwen, DeepSeek, Kimi, MiniMax, Venice Uncensored 등 |
| **익명화** | 메타데이터가 제거된 상태로 Venice를 통해 프록시됩니다. 기반 provider(OpenAI, Anthropic, Google, xAI)는 익명화된 요청을 봅니다. | Claude, GPT, Gemini, Grok |

## 기능

- **개인정보 보호 중심**: "비공개"(완전 비공개)와 "익명화"(프록시) 모드 중에서 선택
- **검열 없는 모델**: 콘텐츠 제한이 없는 모델에 액세스
- **주요 모델 액세스**: Venice의 익명화 프록시를 통해 Claude, GPT, Gemini, Grok 사용
- **OpenAI 호환 API**: 쉬운 통합을 위한 표준 `/v1` 엔드포인트
- **스트리밍**: ✅ 모든 모델에서 지원
- **함수 호출**: ✅ 일부 모델에서 지원(모델 기능 확인)
- **비전**: ✅ 비전 기능이 있는 모델에서 지원
- **엄격한 속도 제한 없음**: 극단적인 사용량에는 공정 사용 제한이 적용될 수 있음

## 설정

### 1. API 키 발급

1. [venice.ai](https://venice.ai)에서 가입합니다
2. **Settings → API Keys → Create new key**로 이동합니다
3. API 키를 복사합니다(형식: `vapi_xxxxxxxxxxxx`)

### 2. OpenClaw 구성

**옵션 A: 환경 변수**

```bash
export VENICE_API_KEY="vapi_xxxxxxxxxxxx"
```

**옵션 B: 대화형 설정(권장)**

```bash
openclaw onboard --auth-choice venice-api-key
```

이렇게 하면 다음이 수행됩니다:

1. API 키를 입력하라는 메시지가 표시됩니다(또는 기존 `VENICE_API_KEY` 사용)
2. 사용 가능한 모든 Venice 모델이 표시됩니다
3. 기본 모델을 선택할 수 있습니다
4. provider가 자동으로 구성됩니다

**옵션 C: 비대화형**

```bash
openclaw onboard --non-interactive \
  --auth-choice venice-api-key \
  --venice-api-key "vapi_xxxxxxxxxxxx"
```

### 3. 설정 확인

```bash
openclaw agent --model venice/kimi-k2-5 --message "안녕하세요, 작동하나요?"
```

## 모델 선택

설정 후 OpenClaw는 사용 가능한 모든 Venice 모델을 표시합니다. 필요에 따라 선택하세요.

- **기본 모델**: 강력한 비공개 reasoning과 비전을 제공하는 `venice/kimi-k2-5`
- **고성능 옵션**: 가장 강력한 익명화 Venice 경로인 `venice/claude-opus-4-6`
- **개인정보 보호**: 완전 비공개 추론을 위해 "비공개" 모델 선택
- **기능**: Venice 프록시를 통해 Claude, GPT, Gemini에 액세스하려면 "익명화" 모델 선택

기본 모델은 언제든지 변경할 수 있습니다:

```bash
openclaw models set venice/kimi-k2-5
openclaw models set venice/claude-opus-4-6
```

사용 가능한 모든 모델 나열:

```bash
openclaw models list | grep venice
```

## `openclaw configure`로 구성하기

1. `openclaw configure`를 실행합니다
2. **Model/auth**를 선택합니다
3. **Venice AI**를 선택합니다

## 어떤 모델을 사용해야 하나요?

| 사용 사례 | 권장 모델 | 이유 |
| -------------------------- | -------------------------------- | -------------------------------------------- |
| **일반 채팅(기본값)** | `kimi-k2-5` | 강력한 비공개 reasoning과 비전 |
| **전반적으로 최고 품질** | `claude-opus-4-6` | 가장 강력한 익명화 Venice 옵션 |
| **개인정보 보호 + 코딩** | `qwen3-coder-480b-a35b-instruct` | 넓은 컨텍스트를 갖춘 비공개 코딩 모델 |
| **비공개 비전** | `kimi-k2-5` | 비공개 모드를 벗어나지 않고 비전 지원 |
| **빠르고 저렴함** | `qwen3-4b` | 경량 reasoning 모델 |
| **복잡한 비공개 작업** | `deepseek-v3.2` | 강력한 reasoning, 단 Venice 도구 지원 없음 |
| **검열 없음** | `venice-uncensored` | 콘텐츠 제한 없음 |

## 사용 가능한 모델(총 41개)

### 비공개 모델(26개) - 완전 비공개, 로깅 없음

| 모델 ID | 이름 | 컨텍스트 | 기능 |
| -------------------------------------- | ----------------------------------- | ------- | -------------------------- |
| `kimi-k2-5`                            | Kimi K2.5                           | 256k    | 기본값, reasoning, 비전 |
| `kimi-k2-thinking`                     | Kimi K2 Thinking                    | 256k    | Reasoning |
| `llama-3.3-70b`                        | Llama 3.3 70B                       | 128k    | 일반 |
| `llama-3.2-3b`                         | Llama 3.2 3B                        | 128k    | 일반 |
| `hermes-3-llama-3.1-405b`              | Hermes 3 Llama 3.1 405B             | 128k    | 일반, 도구 비활성화 |
| `qwen3-235b-a22b-thinking-2507`        | Qwen3 235B Thinking                 | 128k    | Reasoning |
| `qwen3-235b-a22b-instruct-2507`        | Qwen3 235B Instruct                 | 128k    | 일반 |
| `qwen3-coder-480b-a35b-instruct`       | Qwen3 Coder 480B                    | 256k    | 코딩 |
| `qwen3-coder-480b-a35b-instruct-turbo` | Qwen3 Coder 480B Turbo              | 256k    | 코딩 |
| `qwen3-5-35b-a3b`                      | Qwen3.5 35B A3B                     | 256k    | Reasoning, 비전 |
| `qwen3-next-80b`                       | Qwen3 Next 80B                      | 256k    | 일반 |
| `qwen3-vl-235b-a22b`                   | Qwen3 VL 235B (Vision)              | 256k    | 비전 |
| `qwen3-4b`                             | Venice Small (Qwen3 4B)             | 32k     | 빠름, reasoning |
| `deepseek-v3.2`                        | DeepSeek V3.2                       | 160k    | Reasoning, 도구 비활성화 |
| `venice-uncensored`                    | Venice Uncensored (Dolphin-Mistral) | 32k     | 검열 없음, 도구 비활성화 |
| `mistral-31-24b`                       | Venice Medium (Mistral)             | 128k    | 비전 |
| `google-gemma-3-27b-it`                | Google Gemma 3 27B Instruct         | 198k    | 비전 |
| `openai-gpt-oss-120b`                  | OpenAI GPT OSS 120B                 | 128k    | 일반 |
| `nvidia-nemotron-3-nano-30b-a3b`       | NVIDIA Nemotron 3 Nano 30B          | 128k    | 일반 |
| `olafangensan-glm-4.7-flash-heretic`   | GLM 4.7 Flash Heretic               | 128k    | Reasoning |
| `zai-org-glm-4.6`                      | GLM 4.6                             | 198k    | 일반 |
| `zai-org-glm-4.7`                      | GLM 4.7                             | 198k    | Reasoning |
| `zai-org-glm-4.7-flash`                | GLM 4.7 Flash                       | 128k    | Reasoning |
| `zai-org-glm-5`                        | GLM 5                               | 198k    | Reasoning |
| `minimax-m21`                          | MiniMax M2.1                        | 198k    | Reasoning |
| `minimax-m25`                          | MiniMax M2.5                        | 198k    | Reasoning |

### 익명화 모델(15개) - Venice 프록시 경유

| 모델 ID | 이름 | 컨텍스트 | 기능 |
| ------------------------------- | ------------------------------ | ------- | ------------------------- |
| `claude-opus-4-6`               | Claude Opus 4.6 (via Venice)   | 1M      | Reasoning, 비전 |
| `claude-opus-4-5`               | Claude Opus 4.5 (via Venice)   | 198k    | Reasoning, 비전 |
| `claude-sonnet-4-6`             | Claude Sonnet 4.6 (via Venice) | 1M      | Reasoning, 비전 |
| `claude-sonnet-4-5`             | Claude Sonnet 4.5 (via Venice) | 198k    | Reasoning, 비전 |
| `openai-gpt-54`                 | GPT-5.4 (via Venice)           | 1M      | Reasoning, 비전 |
| `openai-gpt-53-codex`           | GPT-5.3 Codex (via Venice)     | 400k    | Reasoning, 비전, 코딩 |
| `openai-gpt-52`                 | GPT-5.2 (via Venice)           | 256k    | Reasoning |
| `openai-gpt-52-codex`           | GPT-5.2 Codex (via Venice)     | 256k    | Reasoning, 비전, 코딩 |
| `openai-gpt-4o-2024-11-20`      | GPT-4o (via Venice)            | 128k    | 비전 |
| `openai-gpt-4o-mini-2024-07-18` | GPT-4o Mini (via Venice)       | 128k    | 비전 |
| `gemini-3-1-pro-preview`        | Gemini 3.1 Pro (via Venice)    | 1M      | Reasoning, 비전 |
| `gemini-3-pro-preview`          | Gemini 3 Pro (via Venice)      | 198k    | Reasoning, 비전 |
| `gemini-3-flash-preview`        | Gemini 3 Flash (via Venice)    | 256k    | Reasoning, 비전 |
| `grok-41-fast`                  | Grok 4.1 Fast (via Venice)     | 1M      | Reasoning, 비전 |
| `grok-code-fast-1`              | Grok Code Fast 1 (via Venice)  | 256k    | Reasoning, 코딩 |

## 모델 검색

`VENICE_API_KEY`가 설정되어 있으면 OpenClaw는 Venice API에서 모델을 자동으로 검색합니다. API에 연결할 수 없으면 정적 카탈로그로 대체합니다.

`/models` 엔드포인트는 공개되어 있어 목록 조회에는 인증이 필요 없지만, 추론에는 유효한 API 키가 필요합니다.

## 스트리밍 및 도구 지원

| 기능 | 지원 |
| -------------------- | ------------------------------------------------------- |
| **스트리밍** | ✅ 모든 모델 |
| **함수 호출** | ✅ 대부분의 모델(API에서 `supportsFunctionCalling` 확인) |
| **비전/이미지** | ✅ "Vision" 기능이 표시된 모델 |
| **JSON 모드** | ✅ `response_format`을 통해 지원 |

## 가격

Venice는 크레딧 기반 시스템을 사용합니다. 현재 요금은 [venice.ai/pricing](https://venice.ai/pricing)에서 확인하세요.

- **비공개 모델**: 일반적으로 더 저렴함
- **익명화 모델**: 직접 API 가격과 유사하며 Venice 수수료가 소액 추가됨

## 비교: Venice와 직접 API

| 항목 | Venice(익명화) | 직접 API |
| ------------ | ----------------------------- | ------------------- |
| **개인정보 보호** | 메타데이터 제거, 익명화 | 계정이 연결됨 |
| **지연 시간** | +10-50ms (프록시) | 직접 연결 |
| **기능** | 대부분의 기능 지원 | 전체 기능 |
| **청구** | Venice 크레딧 | provider 청구 |

## 사용 예시

```bash
# 기본 비공개 모델 사용
openclaw agent --model venice/kimi-k2-5 --message "빠른 상태 확인"

# Venice를 통한 Claude Opus 사용(익명화)
openclaw agent --model venice/claude-opus-4-6 --message "이 작업을 요약해 줘"

# 검열 없는 모델 사용
openclaw agent --model venice/venice-uncensored --message "초안 옵션을 제안해 줘"

# 이미지와 함께 비전 모델 사용
openclaw agent --model venice/qwen3-vl-235b-a22b --message "첨부된 이미지를 검토해 줘"

# 코딩 모델 사용
openclaw agent --model venice/qwen3-coder-480b-a35b-instruct --message "이 함수를 리팩터링해 줘"
```

## 문제 해결

### API 키가 인식되지 않음

```bash
echo $VENICE_API_KEY
openclaw models list | grep venice
```

키가 `vapi_`로 시작하는지 확인하세요.

### 모델을 사용할 수 없음

Venice 모델 카탈로그는 동적으로 업데이트됩니다. 현재 사용 가능한 모델을 보려면 `openclaw models list`를 실행하세요. 일부 모델은 일시적으로 오프라인일 수 있습니다.

### 연결 문제

Venice API는 `https://api.venice.ai/api/v1`에 있습니다. 네트워크에서 HTTPS 연결을 허용하는지 확인하세요.

## 구성 파일 예시

```json5
{
  env: { VENICE_API_KEY: "vapi_..." },
  agents: { defaults: { model: { primary: "venice/kimi-k2-5" } } },
  models: {
    mode: "merge",
    providers: {
      venice: {
        baseUrl: "https://api.venice.ai/api/v1",
        apiKey: "${VENICE_API_KEY}",
        api: "openai-completions",
        models: [
          {
            id: "kimi-k2-5",
            name: "Kimi K2.5",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## 링크

- [Venice AI](https://venice.ai)
- [API 문서](https://docs.venice.ai)
- [가격](https://venice.ai/pricing)
- [상태](https://status.venice.ai)
