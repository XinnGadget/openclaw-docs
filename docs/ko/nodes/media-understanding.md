---
read_when:
    - 미디어 이해 기능을 설계하거나 리팩터링할 때
    - 수신 오디오/비디오/이미지 전처리를 조정할 때
summary: provider + CLI 대체 경로를 포함한 수신 이미지/오디오/비디오 이해(선택 사항)
title: 미디어 이해
x-i18n:
    generated_at: "2026-04-05T12:48:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: fe36bd42250d48d12f4ff549e8644afa7be8e42ee51f8aff4f21f81b7ff060f4
    source_path: nodes/media-understanding.md
    workflow: 15
---

# 미디어 이해 - 수신 (2026-01-17)

OpenClaw는 응답 파이프라인이 실행되기 전에 **수신 미디어**(이미지/오디오/비디오)를 **요약**할 수 있습니다. 로컬 도구나 provider 키를 사용할 수 있을 때 이를 자동 감지하며, 비활성화하거나 사용자 지정할 수도 있습니다. 이해 기능이 꺼져 있더라도 모델은 평소처럼 원본 파일/URL을 받습니다.

벤더별 미디어 동작은 벤더 plugin이 등록하고, OpenClaw
코어는 공통 `tools.media` config, 대체 순서, 응답 파이프라인 통합을 담당합니다.

## 목표

- 선택 사항: 더 빠른 라우팅 + 더 나은 명령 파싱을 위해 수신 미디어를 짧은 텍스트로 사전 소화
- 원본 미디어 전달은 항상 모델에 그대로 유지
- **provider API**와 **CLI 대체 경로** 지원
- 오류/크기/시간 초과 시 순서가 있는 대체를 포함해 여러 모델 허용

## 상위 수준 동작

1. 수신 첨부 파일을 수집합니다 (`MediaPaths`, `MediaUrls`, `MediaTypes`).
2. 활성화된 각 capability(이미지/오디오/비디오)에 대해 정책에 따라 첨부 파일을 선택합니다(기본값: **첫 번째**).
3. 첫 번째 적격 모델 항목을 선택합니다(크기 + capability + auth).
4. 모델이 실패하거나 미디어가 너무 크면 **다음 항목으로 대체**합니다.
5. 성공하면:
   - `Body`는 `[Image]`, `[Audio]`, `[Video]` 블록이 됩니다.
   - 오디오는 `{{Transcript}}`를 설정하며, 명령 파싱은 캡션 텍스트가 있으면 그것을 사용하고, 없으면 transcript를 사용합니다.
   - 캡션은 블록 안에서 `User text:`로 보존됩니다.

이해가 실패하거나 비활성화되어도 **응답 흐름은 계속 진행**되며, 원래 본문 + 첨부 파일을 사용합니다.

## 구성 개요

`tools.media`는 **공유 모델**과 capability별 재정의를 지원합니다:

- `tools.media.models`: 공유 모델 목록(`capabilities`로 게이팅 가능)
- `tools.media.image` / `tools.media.audio` / `tools.media.video`:
  - 기본값 (`prompt`, `maxChars`, `maxBytes`, `timeoutSeconds`, `language`)
  - provider 재정의 (`baseUrl`, `headers`, `providerOptions`)
  - `tools.media.audio.providerOptions.deepgram`을 통한 Deepgram 오디오 옵션
  - 오디오 transcript echo 제어 (`echoTranscript`, 기본값 `false`; `echoFormat`)
  - 선택적 **capability별 `models` 목록** (공유 모델보다 우선)
  - `attachments` 정책 (`mode`, `maxAttachments`, `prefer`)
  - `scope` (채널/chatType/세션 키 기준 선택적 게이팅)
- `tools.media.concurrency`: 최대 동시 capability 실행 수(기본값 **2**)

```json5
{
  tools: {
    media: {
      models: [
        /* shared list */
      ],
      image: {
        /* optional overrides */
      },
      audio: {
        /* optional overrides */
        echoTranscript: true,
        echoFormat: '📝 "{transcript}"',
      },
      video: {
        /* optional overrides */
      },
    },
  },
}
```

### 모델 항목

각 `models[]` 항목은 **provider** 또는 **CLI**일 수 있습니다:

```json5
{
  type: "provider", // default if omitted
  provider: "openai",
  model: "gpt-5.4-mini",
  prompt: "Describe the image in <= 500 chars.",
  maxChars: 500,
  maxBytes: 10485760,
  timeoutSeconds: 60,
  capabilities: ["image"], // optional, used for multi‑modal entries
  profile: "vision-profile",
  preferredProfile: "vision-fallback",
}
```

```json5
{
  type: "cli",
  command: "gemini",
  args: [
    "-m",
    "gemini-3-flash",
    "--allowed-tools",
    "read_file",
    "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
  ],
  maxChars: 500,
  maxBytes: 52428800,
  timeoutSeconds: 120,
  capabilities: ["video", "image"],
}
```

CLI 템플릿은 다음도 사용할 수 있습니다:

- `{{MediaDir}}` (미디어 파일이 있는 디렉터리)
- `{{OutputDir}}` (이 실행을 위해 생성된 scratch 디렉터리)
- `{{OutputBase}}` (확장자 없는 scratch 파일 기본 경로)

## 기본값과 제한

권장 기본값:

- `maxChars`: 이미지/비디오는 **500** (짧고 명령 친화적)
- `maxChars`: 오디오는 **미설정** (제한을 설정하지 않으면 전체 transcript)
- `maxBytes`:
  - 이미지: **10MB**
  - 오디오: **20MB**
  - 비디오: **50MB**

규칙:

- 미디어가 `maxBytes`를 초과하면 해당 모델은 건너뛰고 **다음 모델을 시도**합니다.
- **1024바이트**보다 작은 오디오 파일은 비어 있거나 손상된 것으로 간주되어 provider/CLI 전사 전에 건너뜁니다.
- 모델이 `maxChars`보다 많은 내용을 반환하면 출력이 잘립니다.
- `prompt` 기본값은 단순한 “Describe the {media}.”에 `maxChars` 안내를 더한 형태입니다(이미지/비디오 전용).
- 활성 기본 이미지 모델이 이미 네이티브 vision을 지원하면 OpenClaw는
  `[Image]` 요약 블록을 건너뛰고 대신 원본 이미지를 모델에 전달합니다.
- `<capability>.enabled: true`이지만 구성된 모델이 없으면 OpenClaw는
  해당 provider가 capability를 지원할 때 **활성 응답 모델**을 시도합니다.

### 미디어 이해 자동 감지(기본값)

`tools.media.<capability>.enabled`가 명시적으로 `false`로 설정되지 않았고
구성된 모델도 없으면, OpenClaw는 다음 순서로 자동 감지하고 **처음 동작하는 옵션에서 중단**합니다:

1. provider가 capability를 지원할 때 **활성 응답 모델**
2. **`agents.defaults.imageModel`**의 primary/fallback ref (이미지 전용)
3. **로컬 CLI** (오디오 전용, 설치된 경우)
   - `sherpa-onnx-offline` (`SHERPA_ONNX_MODEL_DIR`에 encoder/decoder/joiner/tokens 필요)
   - `whisper-cli` (`whisper-cpp`; `WHISPER_CPP_MODEL` 또는 번들 tiny 모델 사용)
   - `whisper` (Python CLI; 모델 자동 다운로드)
4. `read_many_files`를 사용하는 **Gemini CLI** (`gemini`)
5. **Provider auth**
   - capability를 지원하는 구성된 `models.providers.*` 항목은
     번들 대체 순서보다 먼저 시도됩니다.
   - image-capable 모델을 가진 이미지 전용 config provider는
     번들 벤더 plugin이 아니더라도 미디어 이해용으로 자동 등록됩니다.
   - 번들 대체 순서:
     - 오디오: OpenAI → Groq → Deepgram → Google → Mistral
     - 이미지: OpenAI → Anthropic → Google → MiniMax → MiniMax Portal → Z.AI
     - 비디오: Google → Qwen → Moonshot

자동 감지를 비활성화하려면 다음과 같이 설정하세요:

```json5
{
  tools: {
    media: {
      audio: {
        enabled: false,
      },
    },
  },
}
```

참고: 바이너리 감지는 macOS/Linux/Windows 전반에서 best-effort로 수행됩니다. CLI가 `PATH`에 있어야 하며(`~`는 확장됨), 또는 전체 명령 경로를 가진 명시적 CLI 모델을 설정하세요.

### 프록시 환경 지원(provider 모델)

provider 기반 **오디오** 및 **비디오** 미디어 이해가 활성화되면, OpenClaw는
provider HTTP 호출에 대해 표준 아웃바운드 프록시 환경 변수를 따릅니다:

- `HTTPS_PROXY`
- `HTTP_PROXY`
- `https_proxy`
- `http_proxy`

프록시 env var가 설정되지 않으면 미디어 이해는 직접 egress를 사용합니다.
프록시 값 형식이 잘못되면 OpenClaw는 경고를 기록하고 직접 fetch로 대체합니다.

## Capabilities(선택 사항)

`capabilities`를 설정하면 해당 항목은 지정된 미디어 유형에 대해서만 실행됩니다. 공유
목록의 경우 OpenClaw는 기본값을 추론할 수 있습니다:

- `openai`, `anthropic`, `minimax`: **이미지**
- `minimax-portal`: **이미지**
- `moonshot`: **이미지 + 비디오**
- `openrouter`: **이미지**
- `google` (Gemini API): **이미지 + 오디오 + 비디오**
- `qwen`: **이미지 + 비디오**
- `mistral`: **오디오**
- `zai`: **이미지**
- `groq`: **오디오**
- `deepgram`: **오디오**
- image-capable 모델을 가진 모든 `models.providers.<id>.models[]` 카탈로그:
  **이미지**

CLI 항목은 예기치 않은 일치를 피하기 위해 **`capabilities`를 명시적으로 설정**하세요.
`capabilities`를 생략하면, 해당 항목은 자신이 나타난 목록에서 적격으로 간주됩니다.

## Provider 지원 매트릭스(OpenClaw 통합)

| Capability | Provider 통합                                                                       | 참고                                                                                                                                    |
| ---------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 이미지     | OpenAI, OpenRouter, Anthropic, Google, MiniMax, Moonshot, Qwen, Z.AI, config providers | 벤더 plugin이 이미지 지원을 등록합니다. MiniMax와 MiniMax OAuth는 모두 `MiniMax-VL-01`을 사용하며, image-capable config provider는 자동 등록됩니다. |
| 오디오     | OpenAI, Groq, Deepgram, Google, Mistral                                             | provider 전사(Whisper/Deepgram/Gemini/Voxtral).                                                                                         |
| 비디오     | Google, Qwen, Moonshot                                                              | 벤더 plugin을 통한 provider 비디오 이해, Qwen 비디오 이해는 Standard DashScope 엔드포인트 사용.                                       |

MiniMax 참고:

- `minimax`와 `minimax-portal` 이미지 이해는 plugin 소유의
  `MiniMax-VL-01` 미디어 provider에서 옵니다.
- 번들 MiniMax 텍스트 카탈로그는 여전히 텍스트 전용으로 시작하며,
  명시적인 `models.providers.minimax` 항목이 image-capable M2.7 chat ref를 구체화합니다.

## 모델 선택 가이드

- 품질과 안전성이 중요할 때는 각 미디어 capability에 대해 사용 가능한 가장 강력한 최신 세대 모델을 선호하세요.
- 신뢰할 수 없는 입력을 처리하는 도구 활성 agent의 경우, 오래되었거나 약한 미디어 모델은 피하세요.
- 가용성을 위해 capability별로 적어도 하나의 대체를 유지하세요(고품질 모델 + 더 빠르고 저렴한 모델).
- CLI 대체 경로(`whisper-cli`, `whisper`, `gemini`)는 provider API를 사용할 수 없을 때 유용합니다.
- `parakeet-mlx` 참고: `--output-dir`과 함께 사용할 때 출력 형식이 `txt`(또는 미지정)라면 OpenClaw는 `<output-dir>/<media-basename>.txt`를 읽습니다. `txt`가 아닌 형식은 stdout으로 대체됩니다.

## 첨부 파일 정책

capability별 `attachments`는 어떤 첨부 파일을 처리할지 제어합니다:

- `mode`: `first` (기본값) 또는 `all`
- `maxAttachments`: 처리할 최대 개수(기본값 **1**)
- `prefer`: `first`, `last`, `path`, `url`

`mode: "all"`일 때 출력은 `[Image 1/2]`, `[Audio 2/2]` 등으로 레이블됩니다.

파일 첨부 파일 추출 동작:

- 추출된 파일 텍스트는 미디어 프롬프트에 추가되기 전에 **신뢰할 수 없는 외부 콘텐츠**로 감싸집니다.
- 주입된 블록은
  `<<<EXTERNAL_UNTRUSTED_CONTENT id="...">>>` /
  `<<<END_EXTERNAL_UNTRUSTED_CONTENT id="...">>>` 같은 명시적 경계 마커를 사용하고,
  `Source: External` 메타데이터 줄을 포함합니다.
- 이 첨부 파일 추출 경로는 미디어 프롬프트가 비대해지는 것을 피하기 위해
  긴 `SECURITY NOTICE:` 배너를 의도적으로 생략합니다. 대신 경계 마커와 메타데이터는 그대로 유지됩니다.
- 파일에 추출 가능한 텍스트가 없으면 OpenClaw는 `[No extractable text]`를 주입합니다.
- PDF가 이 경로에서 렌더링된 페이지 이미지로 대체될 경우, 미디어 프롬프트는
  `[PDF content rendered to images; images not forwarded to model]`
  플레이스홀더를 유지합니다. 이 첨부 파일 추출 단계는 렌더링된 PDF 이미지가 아니라 텍스트 블록을 전달하기 때문입니다.

## 구성 예시

### 1) 공유 모델 목록 + 재정의

```json5
{
  tools: {
    media: {
      models: [
        { provider: "openai", model: "gpt-5.4-mini", capabilities: ["image"] },
        {
          provider: "google",
          model: "gemini-3-flash-preview",
          capabilities: ["image", "audio", "video"],
        },
        {
          type: "cli",
          command: "gemini",
          args: [
            "-m",
            "gemini-3-flash",
            "--allowed-tools",
            "read_file",
            "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
          ],
          capabilities: ["image", "video"],
        },
      ],
      audio: {
        attachments: { mode: "all", maxAttachments: 2 },
      },
      video: {
        maxChars: 500,
      },
    },
  },
}
```

### 2) 오디오 + 비디오만 사용(이미지 끔)

```json5
{
  tools: {
    media: {
      audio: {
        enabled: true,
        models: [
          { provider: "openai", model: "gpt-4o-mini-transcribe" },
          {
            type: "cli",
            command: "whisper",
            args: ["--model", "base", "{{MediaPath}}"],
          },
        ],
      },
      video: {
        enabled: true,
        maxChars: 500,
        models: [
          { provider: "google", model: "gemini-3-flash-preview" },
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m",
              "gemini-3-flash",
              "--allowed-tools",
              "read_file",
              "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
            ],
          },
        ],
      },
    },
  },
}
```

### 3) 선택적 이미지 이해

```json5
{
  tools: {
    media: {
      image: {
        enabled: true,
        maxBytes: 10485760,
        maxChars: 500,
        models: [
          { provider: "openai", model: "gpt-5.4-mini" },
          { provider: "anthropic", model: "claude-opus-4-6" },
          {
            type: "cli",
            command: "gemini",
            args: [
              "-m",
              "gemini-3-flash",
              "--allowed-tools",
              "read_file",
              "Read the media at {{MediaPath}} and describe it in <= {{MaxChars}} characters.",
            ],
          },
        ],
      },
    },
  },
}
```

### 4) 멀티모달 단일 항목(명시적 capabilities)

```json5
{
  tools: {
    media: {
      image: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      audio: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
      video: {
        models: [
          {
            provider: "google",
            model: "gemini-3.1-pro-preview",
            capabilities: ["image", "video", "audio"],
          },
        ],
      },
    },
  },
}
```

## 상태 출력

미디어 이해가 실행되면 `/status`에 짧은 요약 줄이 포함됩니다:

```
📎 Media: image ok (openai/gpt-5.4-mini) · audio skipped (maxBytes)
```

이는 capability별 결과와, 해당되는 경우 선택된 provider/model을 보여 줍니다.

## 참고

- 이해 기능은 **best-effort**입니다. 오류가 응답을 막지는 않습니다.
- 이해 기능이 비활성화되어 있어도 첨부 파일은 여전히 모델에 전달됩니다.
- `scope`를 사용해 이해 기능이 실행되는 위치를 제한하세요(예: DM에서만).

## 관련 문서

- [Configuration](/gateway/configuration)
- [이미지 및 미디어 지원](/nodes/images)
