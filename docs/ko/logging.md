---
read_when:
    - 초보자 친화적인 로깅 개요가 필요한 경우
    - 로그 수준 또는 형식을 구성하려는 경우
    - 문제 해결 중 빠르게 로그를 찾아야 하는 경우
summary: '로깅 개요: 파일 로그, 콘솔 출력, CLI tailing, Control UI'
title: 로깅 개요
x-i18n:
    generated_at: "2026-04-05T12:48:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3a5e3800b7c5128602d05d5a35df4f88c373cfbe9397cca7e7154fff56a7f7ef
    source_path: logging.md
    workflow: 15
---

# 로깅

OpenClaw에는 두 가지 주요 로그 표면이 있습니다:

- Gateway가 기록하는 **파일 로그**(JSON lines)
- 터미널과 Gateway Debug UI에 표시되는 **콘솔 출력**

Control UI의 **Logs** 탭은 gateway 파일 로그를 tail합니다. 이 페이지에서는
로그가 어디에 저장되는지, 어떻게 읽는지, 로그 수준과 형식을 어떻게 구성하는지 설명합니다.

## 로그 위치

기본적으로 Gateway는 다음 위치에 롤링 로그 파일을 기록합니다:

`/tmp/openclaw/openclaw-YYYY-MM-DD.log`

날짜는 gateway 호스트의 로컬 시간대를 사용합니다.

이는 `~/.openclaw/openclaw.json`에서 재정의할 수 있습니다:

```json
{
  "logging": {
    "file": "/path/to/openclaw.log"
  }
}
```

## 로그 읽는 방법

### CLI: 실시간 tail(권장)

CLI를 사용해 RPC를 통해 gateway 로그 파일을 tail하세요:

```bash
openclaw logs --follow
```

유용한 현재 옵션:

- `--local-time`: 타임스탬프를 로컬 시간대로 렌더링
- `--url <url>` / `--token <token>` / `--timeout <ms>`: 표준 Gateway RPC 플래그
- `--expect-final`: agent 기반 RPC 최종 응답 대기 플래그(공유 클라이언트 계층을 통해 여기서도 허용됨)

출력 모드:

- **TTY 세션**: 보기 좋은 색상과 구조를 갖춘 로그 줄
- **비-TTY 세션**: 일반 텍스트
- `--json`: 줄 구분 JSON(줄당 하나의 로그 이벤트)
- `--plain`: TTY 세션에서 일반 텍스트 강제
- `--no-color`: ANSI 색상 비활성화

명시적인 `--url`을 전달하면 CLI는 config 또는
환경 자격 증명을 자동 적용하지 않으므로, 대상 Gateway가
인증을 요구하면 `--token`을 직접 포함하세요.

JSON 모드에서 CLI는 `type` 태그가 있는 객체를 출력합니다:

- `meta`: 스트림 메타데이터(파일, 커서, 크기)
- `log`: 파싱된 로그 항목
- `notice`: 잘림/회전 힌트
- `raw`: 파싱되지 않은 원시 로그 줄

로컬 loopback Gateway가 페어링을 요구하면 `openclaw logs`는
구성된 로컬 로그 파일로 자동 대체됩니다. 명시적인 `--url` 대상에는
이 대체가 적용되지 않습니다.

Gateway에 연결할 수 없으면 CLI는 다음을 실행하라는 짧은 힌트를 출력합니다:

```bash
openclaw doctor
```

### Control UI(웹)

Control UI의 **Logs** 탭은 `logs.tail`을 사용해 같은 파일을 tail합니다.
여는 방법은 [/web/control-ui](/web/control-ui)를 참조하세요.

### 채널 전용 로그

채널 활동(WhatsApp/Telegram 등)만 필터링하려면 다음을 사용하세요:

```bash
openclaw channels logs --channel whatsapp
```

## 로그 형식

### 파일 로그(JSONL)

로그 파일의 각 줄은 JSON 객체입니다. CLI와 Control UI는 이
항목들을 파싱하여 구조화된 출력(시간, 수준, subsystem, 메시지)을 렌더링합니다.

### 콘솔 출력

콘솔 로그는 **TTY 인식형**이며 가독성을 위해 형식이 지정됩니다:

- subsystem 접두사(예: `gateway/channels/whatsapp`)
- 수준 색상(info/warn/error)
- 선택적인 compact 또는 JSON 모드

콘솔 형식은 `logging.consoleStyle`로 제어합니다.

### Gateway WebSocket 로그

`openclaw gateway`에는 RPC 트래픽용 WebSocket 프로토콜 로깅도 있습니다:

- 일반 모드: 중요한 결과만 표시(오류, 파싱 오류, 느린 호출)
- `--verbose`: 모든 요청/응답 트래픽 표시
- `--ws-log auto|compact|full`: 상세 렌더링 스타일 선택
- `--compact`: `--ws-log compact`의 별칭

예시:

```bash
openclaw gateway
openclaw gateway --verbose --ws-log compact
openclaw gateway --verbose --ws-log full
```

## 로깅 구성

모든 로깅 구성은 `~/.openclaw/openclaw.json`의 `logging` 아래에 있습니다.

```json
{
  "logging": {
    "level": "info",
    "file": "/tmp/openclaw/openclaw-YYYY-MM-DD.log",
    "consoleLevel": "info",
    "consoleStyle": "pretty",
    "redactSensitive": "tools",
    "redactPatterns": ["sk-.*"]
  }
}
```

### 로그 수준

- `logging.level`: **파일 로그**(JSONL) 수준
- `logging.consoleLevel`: **콘솔** 상세 수준

둘 다 **`OPENCLAW_LOG_LEVEL`** 환경 변수로 재정의할 수 있습니다(예: `OPENCLAW_LOG_LEVEL=debug`). 환경 변수는 config 파일보다 우선하므로 `openclaw.json`을 편집하지 않고도 한 번의 실행에 대해 상세 수준을 높일 수 있습니다. 또한 전역 CLI 옵션 **`--log-level <level>`**(예: `openclaw --log-level debug gateway run`)을 전달할 수도 있으며, 이 경우 해당 명령에 대해 환경 변수보다 우선합니다.

`--verbose`는 콘솔 출력과 WS 로그 상세 수준에만 영향을 주며, 파일 로그 수준은 바꾸지 않습니다.

### 콘솔 스타일

`logging.consoleStyle`:

- `pretty`: 사람이 읽기 쉬운 형식, 색상 포함, 타임스탬프 포함
- `compact`: 더 압축된 출력(긴 세션에 적합)
- `json`: 줄마다 JSON(로그 처리기용)

### redaction

도구 요약은 콘솔에 출력되기 전에 민감한 토큰을 redaction할 수 있습니다:

- `logging.redactSensitive`: `off` | `tools` (기본값: `tools`)
- `logging.redactPatterns`: 기본 세트를 재정의할 regex 문자열 목록

Redaction은 **콘솔 출력에만** 적용되며 파일 로그는 변경하지 않습니다.

## 진단 + OpenTelemetry

진단은 모델 실행 **및**
메시지 흐름 텔레메트리(webhooks, 큐잉, 세션 상태)를 위한 구조화된 기계 판독 가능 이벤트입니다. 이것은 로그를 대체하지 않으며, 메트릭, trace, 기타 익스포터에 데이터를 공급하기 위해 존재합니다.

진단 이벤트는 프로세스 내에서 발생하지만, 익스포터는 진단 + 해당 익스포터 plugin이 활성화된 경우에만 연결됩니다.

### OpenTelemetry와 OTLP의 차이

- **OpenTelemetry (OTel)**: trace, metrics, logs를 위한 데이터 모델 + SDK
- **OTLP**: OTel 데이터를 collector/backend로 내보내는 데 사용하는 wire protocol
- OpenClaw는 현재 **OTLP/HTTP (protobuf)**를 통해 내보냅니다

### 내보내는 신호

- **Metrics**: counters + histograms(토큰 사용량, 메시지 흐름, 큐잉)
- **Traces**: 모델 사용 + webhook/메시지 처리용 span
- **Logs**: `diagnostics.otel.logs`가 활성화되면 OTLP를 통해 내보냅니다. 로그
  양이 많을 수 있으므로 `logging.level`과 익스포터 필터를 고려하세요.

### 진단 이벤트 카탈로그

모델 사용:

- `model.usage`: tokens, cost, duration, context, provider/model/channel, session ids

메시지 흐름:

- `webhook.received`: 채널별 webhook 인그레스
- `webhook.processed`: 처리된 webhook + duration
- `webhook.error`: webhook 핸들러 오류
- `message.queued`: 처리용으로 큐에 들어간 메시지
- `message.processed`: 결과 + duration + 선택적 error

큐 + 세션:

- `queue.lane.enqueue`: 명령 큐 lane enqueue + depth
- `queue.lane.dequeue`: 명령 큐 lane dequeue + wait time
- `session.state`: 세션 상태 전이 + 이유
- `session.stuck`: 세션 정체 경고 + 경과 시간
- `run.attempt`: 실행 재시도/시도 메타데이터
- `diagnostic.heartbeat`: 집계 카운터(webhooks/queue/session)

### 진단 활성화(익스포터 없음)

plugin 또는 사용자 지정 sink에서 진단 이벤트를 사용 가능하게 하려면 다음을 사용하세요:

```json
{
  "diagnostics": {
    "enabled": true
  }
}
```

### Diagnostics 플래그(대상 지정 로그)

`logging.level`을 올리지 않고도 대상이 명확한 추가 디버그 로그를 켜려면 플래그를 사용하세요.
플래그는 대소문자를 구분하지 않으며 와일드카드를 지원합니다(예: `telegram.*` 또는 `*`).

```json
{
  "diagnostics": {
    "flags": ["telegram.http"]
  }
}
```

환경 변수 재정의(일회성):

```
OPENCLAW_DIAGNOSTICS=telegram.http,telegram.payload
```

참고:

- 플래그 로그는 표준 로그 파일(`logging.file`과 동일)로 갑니다.
- 출력은 여전히 `logging.redactSensitive`에 따라 redaction됩니다.
- 전체 가이드: [/diagnostics/flags](/diagnostics/flags).

### OpenTelemetry로 내보내기

진단은 `diagnostics-otel` plugin(OTLP/HTTP)을 통해 내보낼 수 있습니다. 이는 OTLP/HTTP를 수용하는 어떤 OpenTelemetry collector/backend와도 함께 사용할 수 있습니다.

```json
{
  "plugins": {
    "allow": ["diagnostics-otel"],
    "entries": {
      "diagnostics-otel": {
        "enabled": true
      }
    }
  },
  "diagnostics": {
    "enabled": true,
    "otel": {
      "enabled": true,
      "endpoint": "http://otel-collector:4318",
      "protocol": "http/protobuf",
      "serviceName": "openclaw-gateway",
      "traces": true,
      "metrics": true,
      "logs": true,
      "sampleRate": 0.2,
      "flushIntervalMs": 60000
    }
  }
}
```

참고:

- `openclaw plugins enable diagnostics-otel`로도 plugin을 활성화할 수 있습니다.
- `protocol`은 현재 `http/protobuf`만 지원합니다. `grpc`는 무시됩니다.
- Metrics에는 토큰 사용량, 비용, 컨텍스트 크기, 실행 시간, 메시지 흐름
  카운터/히스토그램(webhooks, 큐잉, 세션 상태, 큐 깊이/대기 시간)이 포함됩니다.
- traces/metrics는 `traces` / `metrics`로 켜고 끌 수 있습니다(기본값: 켜짐). Trace에는
  모델 사용 span과, 활성화된 경우 webhook/메시지 처리 span이 포함됩니다.
- collector에 인증이 필요하면 `headers`를 설정하세요.
- 지원되는 환경 변수: `OTEL_EXPORTER_OTLP_ENDPOINT`,
  `OTEL_SERVICE_NAME`, `OTEL_EXPORTER_OTLP_PROTOCOL`.

### 내보내는 metrics(이름 + 유형)

모델 사용:

- `openclaw.tokens` (counter, attrs: `openclaw.token`, `openclaw.channel`,
  `openclaw.provider`, `openclaw.model`)
- `openclaw.cost.usd` (counter, attrs: `openclaw.channel`, `openclaw.provider`,
  `openclaw.model`)
- `openclaw.run.duration_ms` (histogram, attrs: `openclaw.channel`,
  `openclaw.provider`, `openclaw.model`)
- `openclaw.context.tokens` (histogram, attrs: `openclaw.context`,
  `openclaw.channel`, `openclaw.provider`, `openclaw.model`)

메시지 흐름:

- `openclaw.webhook.received` (counter, attrs: `openclaw.channel`,
  `openclaw.webhook`)
- `openclaw.webhook.error` (counter, attrs: `openclaw.channel`,
  `openclaw.webhook`)
- `openclaw.webhook.duration_ms` (histogram, attrs: `openclaw.channel`,
  `openclaw.webhook`)
- `openclaw.message.queued` (counter, attrs: `openclaw.channel`,
  `openclaw.source`)
- `openclaw.message.processed` (counter, attrs: `openclaw.channel`,
  `openclaw.outcome`)
- `openclaw.message.duration_ms` (histogram, attrs: `openclaw.channel`,
  `openclaw.outcome`)

큐 + 세션:

- `openclaw.queue.lane.enqueue` (counter, attrs: `openclaw.lane`)
- `openclaw.queue.lane.dequeue` (counter, attrs: `openclaw.lane`)
- `openclaw.queue.depth` (histogram, attrs: `openclaw.lane` 또는
  `openclaw.channel=heartbeat`)
- `openclaw.queue.wait_ms` (histogram, attrs: `openclaw.lane`)
- `openclaw.session.state` (counter, attrs: `openclaw.state`, `openclaw.reason`)
- `openclaw.session.stuck` (counter, attrs: `openclaw.state`)
- `openclaw.session.stuck_age_ms` (histogram, attrs: `openclaw.state`)
- `openclaw.run.attempt` (counter, attrs: `openclaw.attempt`)

### 내보내는 span(이름 + 주요 속성)

- `openclaw.model.usage`
  - `openclaw.channel`, `openclaw.provider`, `openclaw.model`
  - `openclaw.sessionKey`, `openclaw.sessionId`
  - `openclaw.tokens.*` (input/output/cache_read/cache_write/total)
- `openclaw.webhook.processed`
  - `openclaw.channel`, `openclaw.webhook`, `openclaw.chatId`
- `openclaw.webhook.error`
  - `openclaw.channel`, `openclaw.webhook`, `openclaw.chatId`,
    `openclaw.error`
- `openclaw.message.processed`
  - `openclaw.channel`, `openclaw.outcome`, `openclaw.chatId`,
    `openclaw.messageId`, `openclaw.sessionKey`, `openclaw.sessionId`,
    `openclaw.reason`
- `openclaw.session.stuck`
  - `openclaw.state`, `openclaw.ageMs`, `openclaw.queueDepth`,
    `openclaw.sessionKey`, `openclaw.sessionId`

### 샘플링 + flush

- Trace 샘플링: `diagnostics.otel.sampleRate` (0.0–1.0, 루트 span만)
- Metric 내보내기 간격: `diagnostics.otel.flushIntervalMs` (최소 1000ms)

### 프로토콜 참고

- OTLP/HTTP 엔드포인트는 `diagnostics.otel.endpoint` 또는
  `OTEL_EXPORTER_OTLP_ENDPOINT`로 설정할 수 있습니다.
- 엔드포인트에 이미 `/v1/traces` 또는 `/v1/metrics`가 포함되어 있으면 그대로 사용합니다.
- 엔드포인트에 이미 `/v1/logs`가 포함되어 있으면 logs에도 그대로 사용합니다.
- `diagnostics.otel.logs`는 메인 logger 출력에 대한 OTLP 로그 내보내기를 활성화합니다.

### 로그 내보내기 동작

- OTLP 로그는 `logging.file`에 기록되는 것과 동일한 구조화된 레코드를 사용합니다.
- `logging.level`(파일 로그 수준)을 따릅니다. 콘솔 redaction은 OTLP 로그에는 적용되지 않습니다.
- 로그 양이 많은 설치에서는 OTLP collector 측 샘플링/필터링을 선호하세요.

## 문제 해결 팁

- **Gateway에 연결할 수 없나요?** 먼저 `openclaw doctor`를 실행하세요.
- **로그가 비어 있나요?** Gateway가 실행 중이며 `logging.file`에 있는 파일 경로에 기록하고 있는지 확인하세요.
- **더 자세한 정보가 필요하나요?** `logging.level`을 `debug` 또는 `trace`로 설정하고 다시 시도하세요.

## 관련 문서

- [Gateway Logging Internals](/gateway/logging) — WS 로그 스타일, subsystem 접두사, 콘솔 캡처
- [Diagnostics](/gateway/configuration-reference#diagnostics) — OpenTelemetry 내보내기 및 캐시 trace config
