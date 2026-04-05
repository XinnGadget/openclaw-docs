---
read_when:
    - OpenResponses API를 사용하는 클라이언트를 통합하는 경우
    - item 기반 입력, 클라이언트 tool 호출 또는 SSE 이벤트를 사용하려는 경우
summary: Gateway에서 OpenResponses 호환 `/v1/responses` HTTP 엔드포인트 노출
title: OpenResponses API
x-i18n:
    generated_at: "2026-04-05T12:43:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: b3f2905fe45accf2699de8a561d15311720f249f9229d26550c16577428ea8a9
    source_path: gateway/openresponses-http-api.md
    workflow: 15
---

# OpenResponses API (HTTP)

OpenClaw의 Gateway는 OpenResponses 호환 `POST /v1/responses` 엔드포인트를 제공할 수 있습니다.

이 엔드포인트는 **기본적으로 비활성화**되어 있습니다. 먼저 config에서 활성화하세요.

- `POST /v1/responses`
- Gateway와 같은 포트(WS + HTTP 멀티플렉스): `http://<gateway-host>:<port>/v1/responses`

내부적으로 요청은 일반 Gateway 에이전트 실행(`openclaw agent`와 동일한 코드 경로)으로 처리되므로, 라우팅/권한/config는 Gateway와 일치합니다.

## 인증, 보안 및 라우팅

운영 동작은 [OpenAI Chat Completions](/gateway/openai-http-api)와 일치합니다.

- 일치하는 Gateway HTTP 인증 경로 사용:
  - shared-secret 인증(`gateway.auth.mode="token"` 또는 `"password"`): `Authorization: Bearer <token-or-password>`
  - trusted-proxy 인증(`gateway.auth.mode="trusted-proxy"`): 구성된 non-loopback trusted proxy 소스의 identity-aware proxy 헤더
  - private-ingress open auth (`gateway.auth.mode="none"`): 인증 헤더 없음
- 이 엔드포인트를 gateway 인스턴스에 대한 전체 운영자 액세스로 취급
- shared-secret 인증 모드(`token`, `password`)에서는 더 좁은 bearer 선언 `x-openclaw-scopes` 값을 무시하고 정상적인 전체 운영자 기본값으로 복원
- trusted identity-bearing HTTP 모드(예: trusted proxy auth 또는 private ingress의 `gateway.auth.mode="none"`)에서는 `x-openclaw-scopes`가 존재하면 이를 존중하고, 없으면 정상적인 운영자 기본 범위 집합으로 폴백
- `model: "openclaw"`, `model: "openclaw/default"`, `model: "openclaw/<agentId>"` 또는 `x-openclaw-agent-id`로 에이전트 선택
- 선택된 에이전트의 백엔드 모델을 재정의하려면 `x-openclaw-model` 사용
- 명시적 세션 라우팅에는 `x-openclaw-session-key` 사용
- 기본이 아닌 synthetic ingress 채널 컨텍스트를 원하면 `x-openclaw-message-channel` 사용

인증 매트릭스:

- `gateway.auth.mode="token"` 또는 `"password"` + `Authorization: Bearer ...`
  - 공유 gateway 운영자 시크릿 소유를 증명
  - 더 좁은 `x-openclaw-scopes`는 무시
  - 전체 기본 운영자 범위 집합으로 복원:
    `operator.admin`, `operator.approvals`, `operator.pairing`,
    `operator.read`, `operator.talk.secrets`, `operator.write`
  - 이 엔드포인트의 채팅 턴을 owner-sender 턴으로 취급
- trusted identity-bearing HTTP 모드(예: trusted proxy auth 또는 private ingress의 `gateway.auth.mode="none"`)
  - 헤더가 존재할 때 `x-openclaw-scopes`를 존중
  - 헤더가 없을 때 정상적인 운영자 기본 범위 집합으로 폴백
  - 호출자가 명시적으로 범위를 좁히고 `operator.admin`을 생략한 경우에만 owner 의미를 잃음

이 엔드포인트는 `gateway.http.endpoints.responses.enabled`로 활성화 또는 비활성화할 수 있습니다.

동일한 호환 표면에는 다음도 포함됩니다.

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`

에이전트 대상 모델, `openclaw/default`, embeddings 패스스루, 백엔드 모델 재정의가 어떻게 맞물리는지에 대한 정식 설명은 [OpenAI Chat Completions](/gateway/openai-http-api#agent-first-model-contract) 및 [모델 목록과 에이전트 라우팅](/gateway/openai-http-api#model-list-and-agent-routing)을 참조하세요.

## 세션 동작

기본적으로 이 엔드포인트는 **요청별 무상태**입니다(호출마다 새 세션 키 생성).

요청에 OpenResponses `user` 문자열이 포함되면 Gateway는 여기서 안정적인 세션 키를 파생하므로, 반복 호출이 하나의 에이전트 세션을 공유할 수 있습니다.

## 요청 형태(지원 범위)

요청은 item 기반 입력을 사용하는 OpenResponses API를 따릅니다. 현재 지원 범위:

- `input`: 문자열 또는 item 객체 배열
- `instructions`: 시스템 프롬프트에 병합됨
- `tools`: 클라이언트 tool 정의(function tools)
- `tool_choice`: 클라이언트 tools 필터링 또는 필수화
- `stream`: SSE 스트리밍 활성화
- `max_output_tokens`: best-effort 출력 제한(provider 의존)
- `user`: 안정적인 세션 라우팅

허용되지만 **현재 무시됨**:

- `max_tool_calls`
- `reasoning`
- `metadata`
- `store`
- `truncation`

지원됨:

- `previous_response_id`: 요청이 동일한 에이전트/user/requested-session 범위 안에 있으면 OpenClaw는 이전 응답 세션을 재사용합니다.

## Items (입력)

### `message`

역할: `system`, `developer`, `user`, `assistant`

- `system`과 `developer`는 시스템 프롬프트에 추가됩니다.
- 가장 최근의 `user` 또는 `function_call_output` item이 “현재 메시지”가 됩니다.
- 이전 user/assistant 메시지는 컨텍스트를 위한 기록에 포함됩니다.

### `function_call_output` (턴 기반 tools)

tool 결과를 모델에 다시 보냅니다.

```json
{
  "type": "function_call_output",
  "call_id": "call_123",
  "output": "{\"temperature\": \"72F\"}"
}
```

### `reasoning` 및 `item_reference`

스키마 호환성을 위해 허용되지만 프롬프트를 구성할 때는 무시됩니다.

## Tools (클라이언트 측 function tools)

`tools: [{ type: "function", function: { name, description?, parameters? } }]` 형식으로 tools를 제공합니다.

에이전트가 tool을 호출하기로 결정하면 응답은 `function_call` 출력 item을 반환합니다.
이후 턴을 계속하려면 `function_call_output`이 포함된 후속 요청을 보내면 됩니다.

## 이미지 (`input_image`)

base64 또는 URL 소스를 지원합니다.

```json
{
  "type": "input_image",
  "source": { "type": "url", "url": "https://example.com/image.png" }
}
```

허용 MIME 타입(현재): `image/jpeg`, `image/png`, `image/gif`, `image/webp`, `image/heic`, `image/heif`
최대 크기(현재): 10MB

## 파일 (`input_file`)

base64 또는 URL 소스를 지원합니다.

```json
{
  "type": "input_file",
  "source": {
    "type": "base64",
    "media_type": "text/plain",
    "data": "SGVsbG8gV29ybGQh",
    "filename": "hello.txt"
  }
}
```

허용 MIME 타입(현재): `text/plain`, `text/markdown`, `text/html`, `text/csv`,
`application/json`, `application/pdf`

최대 크기(현재): 5MB

현재 동작:

- 파일 콘텐츠는 사용자 메시지가 아니라 **시스템 프롬프트**에 디코딩되어 추가되므로,
  일시적으로 유지됩니다(세션 기록에 영구 저장되지 않음).
- 디코딩된 파일 텍스트는 추가되기 전에 **신뢰할 수 없는 외부 콘텐츠**로 래핑되므로,
  파일 바이트는 신뢰된 지시가 아니라 데이터로 취급됩니다.
- 주입된 블록은
  `<<<EXTERNAL_UNTRUSTED_CONTENT id="...">>>` /
  `<<<END_EXTERNAL_UNTRUSTED_CONTENT id="...">>>` 같은 명시적 경계 마커를 사용하고
  `Source: External` 메타데이터 줄을 포함합니다.
- 이 파일 입력 경로는 프롬프트 예산을 보존하기 위해 긴 `SECURITY NOTICE:` 배너를 의도적으로 생략하지만,
  경계 마커와 메타데이터는 그대로 유지됩니다.
- PDF는 먼저 텍스트를 파싱합니다. 텍스트가 거의 없으면 첫 페이지들을 이미지로 래스터화하여 모델에 전달하고,
  주입된 파일 블록은 `[PDF content rendered to images]` 플레이스홀더를 사용합니다.

PDF 파싱은 Node 친화적인 `pdfjs-dist` 레거시 빌드(worker 없음)를 사용합니다. 최신 PDF.js 빌드는 브라우저 worker/DOM 전역을 기대하므로 Gateway에서는 사용하지 않습니다.

URL fetch 기본값:

- `files.allowUrl`: `true`
- `images.allowUrl`: `true`
- `maxUrlParts`: `8` (요청당 URL 기반 `input_file` + `input_image` 파트 총합)
- 요청은 보호됩니다(DNS 해석, private IP 차단, 리디렉션 제한, 타임아웃)
- 입력 유형별 선택적 호스트명 허용 목록 지원(`files.urlAllowlist`, `images.urlAllowlist`)
  - 정확한 호스트: `"cdn.example.com"`
  - 와일드카드 하위 도메인: `"*.assets.example.com"` (apex는 매치하지 않음)
  - 빈 허용 목록 또는 생략된 허용 목록은 호스트명 허용 목록 제한이 없음을 의미
- URL 기반 fetch를 완전히 비활성화하려면 `files.allowUrl: false` 및/또는 `images.allowUrl: false`로 설정

## 파일 + 이미지 제한(config)

기본값은 `gateway.http.endpoints.responses` 아래에서 조정할 수 있습니다.

```json5
{
  gateway: {
    http: {
      endpoints: {
        responses: {
          enabled: true,
          maxBodyBytes: 20000000,
          maxUrlParts: 8,
          files: {
            allowUrl: true,
            urlAllowlist: ["cdn.example.com", "*.assets.example.com"],
            allowedMimes: [
              "text/plain",
              "text/markdown",
              "text/html",
              "text/csv",
              "application/json",
              "application/pdf",
            ],
            maxBytes: 5242880,
            maxChars: 200000,
            maxRedirects: 3,
            timeoutMs: 10000,
            pdf: {
              maxPages: 4,
              maxPixels: 4000000,
              minTextChars: 200,
            },
          },
          images: {
            allowUrl: true,
            urlAllowlist: ["images.example.com"],
            allowedMimes: [
              "image/jpeg",
              "image/png",
              "image/gif",
              "image/webp",
              "image/heic",
              "image/heif",
            ],
            maxBytes: 10485760,
            maxRedirects: 3,
            timeoutMs: 10000,
          },
        },
      },
    },
  },
}
```

생략 시 기본값:

- `maxBodyBytes`: 20MB
- `maxUrlParts`: 8
- `files.maxBytes`: 5MB
- `files.maxChars`: 200k
- `files.maxRedirects`: 3
- `files.timeoutMs`: 10s
- `files.pdf.maxPages`: 4
- `files.pdf.maxPixels`: 4,000,000
- `files.pdf.minTextChars`: 200
- `images.maxBytes`: 10MB
- `images.maxRedirects`: 3
- `images.timeoutMs`: 10s
- HEIC/HEIF `input_image` 소스는 허용되며 provider 전달 전에 JPEG로 정규화됩니다.

보안 참고:

- URL 허용 목록은 fetch 전에, 그리고 리디렉션 홉에서도 강제됩니다.
- 호스트명을 허용 목록에 추가하더라도 private/internal IP 차단이 우회되지는 않습니다.
- 인터넷에 노출된 gateway의 경우 앱 수준 가드 외에도 네트워크 egress 제어를 적용하세요.
  자세한 내용은 [보안](/gateway/security)을 참조하세요.

## 스트리밍 (SSE)

`stream: true`를 설정하면 Server-Sent Events (SSE)를 받을 수 있습니다.

- `Content-Type: text/event-stream`
- 각 이벤트 줄은 `event: <type>` 및 `data: <json>` 형식
- 스트림은 `data: [DONE]`으로 종료

현재 출력되는 이벤트 유형:

- `response.created`
- `response.in_progress`
- `response.output_item.added`
- `response.content_part.added`
- `response.output_text.delta`
- `response.output_text.done`
- `response.content_part.done`
- `response.output_item.done`
- `response.completed`
- `response.failed` (오류 시)

## 사용량

기본 provider가 토큰 수를 보고할 때 `usage`가 채워집니다.
OpenClaw는 이러한 카운터가 downstream 상태/세션 표면에 도달하기 전에 일반적인 OpenAI 스타일 별칭(`input_tokens` / `output_tokens`, `prompt_tokens` / `completion_tokens`)을 정규화합니다.

## 오류

오류는 다음과 같은 JSON 객체를 사용합니다.

```json
{ "error": { "message": "...", "type": "invalid_request_error" } }
```

일반적인 사례:

- `401` 인증 누락/무효
- `400` 잘못된 요청 본문
- `405` 잘못된 메서드

## 예시

비스트리밍:

```bash
curl -sS http://127.0.0.1:18789/v1/responses \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "input": "hi"
  }'
```

스트리밍:

```bash
curl -N http://127.0.0.1:18789/v1/responses \
  -H 'Authorization: Bearer YOUR_TOKEN' \
  -H 'Content-Type: application/json' \
  -H 'x-openclaw-agent-id: main' \
  -d '{
    "model": "openclaw",
    "stream": true,
    "input": "hi"
  }'
```
