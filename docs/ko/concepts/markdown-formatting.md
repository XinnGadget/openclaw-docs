---
read_when:
    - 아웃바운드 채널의 Markdown 서식 또는 청킹을 변경하는 경우
    - 새 채널 formatter 또는 스타일 매핑을 추가하는 경우
    - 채널 전반의 서식 회귀를 디버그하는 경우
summary: 아웃바운드 채널용 Markdown 서식 파이프라인
title: Markdown 서식
x-i18n:
    generated_at: "2026-04-05T12:39:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3794674e30e265208d14a986ba9bdc4ba52e0cb69c446094f95ca6c674e4566
    source_path: concepts/markdown-formatting.md
    workflow: 15
---

# Markdown 서식

OpenClaw는 아웃바운드 Markdown을 채널별 출력으로 렌더링하기 전에 공통 중간
표현(IR)으로 변환하여 서식을 지정합니다. IR은
스타일/링크 span을 함께 담아 소스 텍스트를 그대로 유지하므로 청킹과 렌더링이
채널 전반에서 일관되게 유지될 수 있습니다.

## 목표

- **일관성:** 한 번 파싱하고, 여러 renderer에서 사용합니다.
- **안전한 청킹:** 렌더링 전에 텍스트를 분할해 인라인 서식이
  청크 사이에서 깨지지 않도록 합니다.
- **채널 적합성:** 같은 IR을 다시 Markdown을 파싱하지 않고 Slack mrkdwn, Telegram HTML, Signal
  스타일 범위로 매핑합니다.

## 파이프라인

1. **Markdown -> IR 파싱**
   - IR은 일반 텍스트와 스타일 span(bold/italic/strike/code/spoiler), 링크 span으로 구성됩니다.
   - 오프셋은 UTF-16 코드 단위이므로 Signal 스타일 범위가 해당 API와 정렬됩니다.
   - 표는 채널이 표 변환을 opt-in한 경우에만 파싱됩니다.
2. **IR 청킹(서식 우선)**
   - 청킹은 렌더링 전에 IR 텍스트에서 수행됩니다.
   - 인라인 서식은 청크 사이에서 분할되지 않으며, span은 청크별로 잘립니다.
3. **채널별 렌더링**
   - **Slack:** mrkdwn 토큰(bold/italic/strike/code), 링크는 `<url|label>`.
   - **Telegram:** HTML 태그(`<b>`, `<i>`, `<s>`, `<code>`, `<pre><code>`, `<a href>`).
   - **Signal:** 일반 텍스트 + `text-style` 범위, 링크는 label이 다를 때 `label (url)`이 됩니다.

## IR 예시

입력 Markdown:

```markdown
Hello **world** — see [docs](https://docs.openclaw.ai).
```

IR(개략도):

```json
{
  "text": "Hello world — see docs.",
  "styles": [{ "start": 6, "end": 11, "style": "bold" }],
  "links": [{ "start": 19, "end": 23, "href": "https://docs.openclaw.ai" }]
}
```

## 사용 위치

- Slack, Telegram, Signal 아웃바운드 어댑터는 IR에서 렌더링합니다.
- 다른 채널(WhatsApp, iMessage, Microsoft Teams, Discord)은 여전히 일반 텍스트 또는
  자체 서식 규칙을 사용하며, 활성화된 경우 Markdown 표 변환은
  청킹 전에 적용됩니다.

## 표 처리

Markdown 표는 채팅 클라이언트마다 일관되게 지원되지 않습니다. 채널별(및 계정별) 변환을 제어하려면
`markdown.tables`를 사용하세요.

- `code`: 표를 코드 블록으로 렌더링합니다(대부분 채널의 기본값).
- `bullets`: 각 행을 글머리표로 변환합니다(Signal + WhatsApp 기본값).
- `off`: 표 파싱 및 변환을 비활성화합니다. 원본 표 텍스트가 그대로 전달됩니다.

Config 키:

```yaml
channels:
  discord:
    markdown:
      tables: code
    accounts:
      work:
        markdown:
          tables: off
```

## 청킹 규칙

- 청크 제한은 채널 어댑터/config에서 가져오며 IR 텍스트에 적용됩니다.
- 코드 펜스는 후행 개행이 포함된 단일 블록으로 보존되어 채널이
  올바르게 렌더링할 수 있도록 합니다.
- 목록 접두사와 인용 블록 접두사는 IR 텍스트의 일부이므로 청킹이
  접두사 중간에서 분할되지 않습니다.
- 인라인 스타일(bold/italic/strike/inline-code/spoiler)은 청크 사이에서 절대 분할되지 않으며,
  renderer는 각 청크 내부에서 스타일을 다시 엽니다.

채널 전반의 청킹 동작에 대해 더 자세히 알아보려면
[Streaming + chunking](/concepts/streaming)을 참조하세요.

## 링크 정책

- **Slack:** `[label](url)` -> `<url|label>`; 원시 URL은 그대로 유지됩니다. 자동 링크
  생성은 중복 링크를 피하기 위해 파싱 중 비활성화됩니다.
- **Telegram:** `[label](url)` -> `<a href="url">label</a>` (HTML parse mode).
- **Signal:** `[label](url)` -> label이 URL과 일치하지 않는 경우 `label (url)`.

## 스포일러

스포일러 마커(`||spoiler||`)는 Signal에서만 파싱되며, সেখানে
SPOILER 스타일 범위로 매핑됩니다. 다른 채널에서는 일반 텍스트로 처리됩니다.

## 채널 formatter를 추가하거나 업데이트하는 방법

1. **한 번만 파싱:** 채널에 적합한
   옵션(autolink, heading style, blockquote prefix)과 함께 공통 `markdownToIR(...)` helper를 사용합니다.
2. **렌더링:** `renderMarkdownWithMarkers(...)`와
   스타일 마커 맵(또는 Signal 스타일 범위)을 사용해 renderer를 구현합니다.
3. **청킹:** 렌더링 전에 `chunkMarkdownIR(...)`를 호출하고 각 청크를 렌더링합니다.
4. **어댑터 연결:** 새 chunker와
   renderer를 사용하도록 채널 아웃바운드 어댑터를 업데이트합니다.
5. **테스트:** format 테스트를 추가 또는 업데이트하고, 해당
   채널이 청킹을 사용하는 경우 아웃바운드 전송 테스트도 추가합니다.

## 흔한 함정

- Slack angle-bracket 토큰(`<@U123>`, `<#C123>`, `<https://...>`)은
  보존되어야 합니다. 원시 HTML은 안전하게 이스케이프하세요.
- Telegram HTML은 깨진 마크업을 피하기 위해 태그 바깥 텍스트를 이스케이프해야 합니다.
- Signal 스타일 범위는 UTF-16 오프셋에 의존하므로 코드 포인트 오프셋을 사용하지 마세요.
- 펜스 코드 블록의 후행 개행을 보존해 닫는 마커가
  별도 줄에 위치하도록 하세요.
