---
read_when:
    - 원격으로(SSH 없이) 게이트웨이 로그를 tail해야 할 때
    - 도구용 JSON 로그 줄이 필요할 때
summary: '`openclaw logs`용 CLI 참조(RPC를 통한 게이트웨이 로그 tail)'
title: logs
x-i18n:
    generated_at: "2026-04-05T12:38:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 238a52e31a9a332cab513ced049e92d032b03c50376895ce57dffa2ee7d1e4b4
    source_path: cli/logs.md
    workflow: 15
---

# `openclaw logs`

RPC를 통해 게이트웨이 파일 로그를 tail합니다(원격 모드에서 동작).

관련 문서:

- 로깅 개요: [로깅](/logging)
- 게이트웨이 CLI: [gateway](/cli/gateway)

## 옵션

- `--limit <n>`: 반환할 최대 로그 줄 수(기본값 `200`)
- `--max-bytes <n>`: 로그 파일에서 읽을 최대 바이트 수(기본값 `250000`)
- `--follow`: 로그 스트림을 계속 따라감
- `--interval <ms>`: follow 중 폴링 간격(기본값 `1000`)
- `--json`: 줄 단위 JSON 이벤트 출력
- `--plain`: 스타일 서식 없는 일반 텍스트 출력
- `--no-color`: ANSI 색상 비활성화
- `--local-time`: 타임스탬프를 로컬 시간대로 렌더링

## 공통 게이트웨이 RPC 옵션

`openclaw logs`는 표준 게이트웨이 클라이언트 플래그도 지원합니다:

- `--url <url>`: 게이트웨이 WebSocket URL
- `--token <token>`: 게이트웨이 토큰
- `--timeout <ms>`: 타임아웃(ms, 기본값 `30000`)
- `--expect-final`: 게이트웨이 호출이 agent 기반일 때 최종 응답 대기

`--url`을 전달하면 CLI는 config 또는 환경 자격 증명을 자동 적용하지 않습니다. 대상 게이트웨이에 인증이 필요하면 `--token`을 명시적으로 포함하세요.

## 예시

```bash
openclaw logs
openclaw logs --follow
openclaw logs --follow --interval 2000
openclaw logs --limit 500 --max-bytes 500000
openclaw logs --json
openclaw logs --plain
openclaw logs --no-color
openclaw logs --limit 500
openclaw logs --local-time
openclaw logs --follow --local-time
openclaw logs --url ws://127.0.0.1:18789 --token "$OPENCLAW_GATEWAY_TOKEN"
```

## 참고

- 타임스탬프를 로컬 시간대로 렌더링하려면 `--local-time`을 사용하세요.
- local loopback 게이트웨이가 페어링을 요청하면 `openclaw logs`는 자동으로 구성된 로컬 로그 파일로 대체합니다. 명시적인 `--url` 대상은 이 대체 동작을 사용하지 않습니다.
