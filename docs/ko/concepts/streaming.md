---
read_when:
    - 채널에서 스트리밍 또는 청킹이 어떻게 동작하는지 설명할 때
    - 블록 스트리밍 또는 채널 청킹 동작을 변경할 때
    - 중복/조기 블록 답장 또는 채널 미리보기 스트리밍을 디버깅할 때
summary: 스트리밍 + 청킹 동작(블록 답장, 채널 미리보기 스트리밍, 모드 매핑)
title: 스트리밍 및 청킹
x-i18n:
    generated_at: "2026-04-05T12:41:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44b0d08c7eafcb32030ef7c8d5719c2ea2d34e4bac5fdad8cc8b3f4e9e9fad97
    source_path: concepts/streaming.md
    workflow: 15
---

# 스트리밍 + 청킹

OpenClaw에는 서로 분리된 두 개의 스트리밍 계층이 있습니다:

- **블록 스트리밍(채널):** assistant가 작성하는 동안 완료된 **블록**을 전송합니다. 이는 일반 채널 메시지이며(토큰 델타 아님).
- **미리보기 스트리밍(Telegram/Discord/Slack):** 생성 중 임시 **미리보기 메시지**를 업데이트합니다.

현재 채널 메시지에는 **진정한 토큰 델타 스트리밍이 없습니다**. 미리보기 스트리밍은 메시지 기반입니다(전송 + 편집/추가).

## 블록 스트리밍(채널 메시지)

블록 스트리밍은 assistant 출력이 준비되는 대로 거친 청크 단위로 전송합니다.

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

범례:

- `text_delta/events`: 모델 스트림 이벤트(비스트리밍 모델에서는 드물 수 있음).
- `chunker`: 최소/최대 경계 + 분할 선호도를 적용하는 `EmbeddedBlockChunker`.
- `channel send`: 실제 발신 메시지(블록 답장).

**제어 항목:**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"`(기본값 꺼짐).
- 채널 재정의: 채널별로 `"on"`/`"off"`를 강제하는 `*.blockStreaming`(및 계정별 변형).
- `agents.defaults.blockStreamingBreak`: `"text_end"` 또는 `"message_end"`.
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`.
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }`(전송 전에 스트리밍된 블록 병합).
- 채널 하드 상한: `*.textChunkLimit`(예: `channels.whatsapp.textChunkLimit`).
- 채널 청크 모드: `*.chunkMode`(`length`가 기본값, `newline`은 길이 기준 청킹 전에 빈 줄(문단 경계)에서 분할).
- Discord 소프트 상한: `channels.discord.maxLinesPerMessage`(기본값 17)는 UI 잘림을 방지하기 위해 긴 답장을 분할합니다.

**경계 의미:**

- `text_end`: chunker가 방출하는 즉시 스트림 블록을 전송하고 각 `text_end`에서 flush합니다.
- `message_end`: assistant 메시지가 끝날 때까지 기다린 뒤 버퍼된 출력을 flush합니다.

`message_end`도 버퍼된 텍스트가 `maxChars`를 초과하면 여전히 chunker를 사용하므로 마지막에 여러 청크를 방출할 수 있습니다.

## 청킹 알고리즘(하한/상한)

블록 청킹은 `EmbeddedBlockChunker`로 구현됩니다:

- **하한:** 버퍼가 `minChars` 이상이 되기 전에는 방출하지 않습니다(강제되는 경우 제외).
- **상한:** 가능하면 `maxChars` 전에 분할합니다. 강제되는 경우 `maxChars`에서 분할합니다.
- **분할 선호도:** `paragraph` → `newline` → `sentence` → `whitespace` → 강제 분할.
- **코드 펜스:** 펜스 내부에서는 절대 분할하지 않습니다. `maxChars`에서 강제 분할될 때는 Markdown 유효성을 유지하기 위해 펜스를 닫고 다시 엽니다.

`maxChars`는 채널 `textChunkLimit`로 제한되므로 채널별 상한을 초과할 수 없습니다.

## 병합(coalescing, 스트리밍된 블록 병합)

블록 스트리밍이 활성화되면 OpenClaw는 **연속된 블록 청크를 병합한 후**
전송할 수 있습니다. 이렇게 하면 진행형 출력을 유지하면서도
“한 줄짜리 스팸”을 줄일 수 있습니다.

- 병합은 flush 전에 **유휴 간격**(`idleMs`)을 기다립니다.
- 버퍼는 `maxChars`로 제한되며, 이를 초과하면 flush됩니다.
- `minChars`는 충분한 텍스트가 누적될 때까지 작은 조각이 전송되지 않도록 합니다
  (최종 flush는 항상 남은 텍스트를 전송).
- 결합자는 `blockStreamingChunk.breakPreference`에서 파생됩니다
  (`paragraph` → `\n\n`, `newline` → `\n`, `sentence` → 공백).
- `*.blockStreamingCoalesce`를 통한 채널 재정의도 사용할 수 있습니다(계정별 config 포함).
- 재정의되지 않은 경우 Signal/Slack/Discord의 기본 coalesce `minChars`는 1500으로 올라갑니다.

## 블록 간 사람 같은 페이싱

블록 스트리밍이 활성화되면 블록 답장 사이에 **무작위 일시 정지**를 추가할 수 있습니다
(첫 번째 블록 이후). 이렇게 하면 여러 버블로 나뉜 응답이
더 자연스럽게 느껴집니다.

- config: `agents.defaults.humanDelay`(에이전트별 재정의: `agents.list[].humanDelay`).
- 모드: `off`(기본값), `natural`(800–2500ms), `custom`(`minMs`/`maxMs`).
- **블록 답장**에만 적용되며, 최종 답장이나 도구 요약에는 적용되지 않습니다.

## "청크로 스트리밍할지 전부 보낼지"

이는 다음에 매핑됩니다:

- **청크 스트리밍:** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"`(작성하면서 전송). Telegram이 아닌 채널은 `*.blockStreaming: true`도 필요합니다.
- **마지막에 전부 스트리밍:** `blockStreamingBreak: "message_end"`(한 번 flush, 매우 길면 여러 청크 가능).
- **블록 스트리밍 없음:** `blockStreamingDefault: "off"`(최종 답장만 전송).

**채널 참고:** 블록 스트리밍은 `*.blockStreaming`이
명시적으로 `true`로 설정되지 않으면 **비활성화**됩니다. 채널은 블록 답장 없이도
실시간 미리보기(`channels.<channel>.streaming`)를 스트리밍할 수 있습니다.

config 위치 참고: `blockStreaming*` 기본값은 루트 config가 아니라
`agents.defaults` 아래에 있습니다.

## 미리보기 스트리밍 모드

정식 키: `channels.<channel>.streaming`

모드:

- `off`: 미리보기 스트리밍 비활성화.
- `partial`: 최신 텍스트로 교체되는 단일 미리보기.
- `block`: 청크/추가 단계로 업데이트되는 미리보기.
- `progress`: 생성 중 진행/상태 미리보기, 완료 시 최종 답변.

### 채널 매핑

| 채널 | `off` | `partial` | `block` | `progress` |
| -------- | ----- | --------- | ------- | ----------------- |
| Telegram | ✅    | ✅        | ✅      | `partial`로 매핑 |
| Discord  | ✅    | ✅        | ✅      | `partial`로 매핑 |
| Slack    | ✅    | ✅        | ✅      | ✅                |

Slack 전용:

- `channels.slack.nativeStreaming`은 `streaming=partial`일 때 Slack 기본 스트리밍 API 호출을 전환합니다(기본값: `true`).

레거시 키 마이그레이션:

- Telegram: `streamMode` + 불리언 `streaming`은 자동으로 `streaming` enum으로 마이그레이션됩니다.
- Discord: `streamMode` + 불리언 `streaming`은 자동으로 `streaming` enum으로 마이그레이션됩니다.
- Slack: `streamMode`는 자동으로 `streaming` enum으로 마이그레이션되며, 불리언 `streaming`은 자동으로 `nativeStreaming`으로 마이그레이션됩니다.

### 런타임 동작

Telegram:

- DM과 그룹/토픽 전반에서 `sendMessage` + `editMessageText` 미리보기 업데이트를 사용합니다.
- Telegram 블록 스트리밍이 명시적으로 활성화된 경우 미리보기 스트리밍은 건너뜁니다(이중 스트리밍 방지).
- `/reasoning stream`은 reasoning을 미리보기에 쓸 수 있습니다.

Discord:

- 전송 + 편집 미리보기 메시지를 사용합니다.
- `block` 모드는 초안 청킹(`draftChunk`)을 사용합니다.
- Discord 블록 스트리밍이 명시적으로 활성화된 경우 미리보기 스트리밍은 건너뜁니다.

Slack:

- `partial`은 사용 가능한 경우 Slack 기본 스트리밍(`chat.startStream`/`append`/`stop`)을 사용할 수 있습니다.
- `block`은 추가형 초안 미리보기를 사용합니다.
- `progress`는 상태 미리보기 텍스트를 사용한 뒤 완료 시 최종 답변을 전송합니다.

## 관련

- [Messages](/concepts/messages) — 메시지 수명 주기 및 전달
- [Retry](/concepts/retry) — 전달 실패 시 재시도 동작
- [Channels](/channels) — 채널별 스트리밍 지원
