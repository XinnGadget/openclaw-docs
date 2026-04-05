---
read_when:
    - Gmail Pub/Sub 이벤트를 OpenClaw에 연결하려는 경우
    - webhook 도우미 명령을 사용하려는 경우
summary: '`openclaw webhooks`용 CLI 참조(webhook 도우미 + Gmail Pub/Sub)'
title: webhooks
x-i18n:
    generated_at: "2026-04-05T12:39:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2b22ce879c3a94557be57919b4d2b3e92ff4d41fbae7bc88d2ab07cd4bbeac83
    source_path: cli/webhooks.md
    workflow: 15
---

# `openclaw webhooks`

webhook 도우미 및 통합(Gmail Pub/Sub, webhook 도우미).

관련 문서:

- Webhooks: [Webhooks](/automation/cron-jobs#webhooks)
- Gmail Pub/Sub: [Gmail Pub/Sub](/automation/cron-jobs#gmail-pubsub-integration)

## Gmail

```bash
openclaw webhooks gmail setup --account you@example.com
openclaw webhooks gmail run
```

### `webhooks gmail setup`

Gmail watch, Pub/Sub, OpenClaw webhook 전달을 구성합니다.

필수:

- `--account <email>`

옵션:

- `--project <id>`
- `--topic <name>`
- `--subscription <name>`
- `--label <label>`
- `--hook-url <url>`
- `--hook-token <token>`
- `--push-token <token>`
- `--bind <host>`
- `--port <port>`
- `--path <path>`
- `--include-body`
- `--max-bytes <n>`
- `--renew-minutes <n>`
- `--tailscale <funnel|serve|off>`
- `--tailscale-path <path>`
- `--tailscale-target <target>`
- `--push-endpoint <url>`
- `--json`

예시:

```bash
openclaw webhooks gmail setup --account you@example.com
openclaw webhooks gmail setup --account you@example.com --project my-gcp-project --json
openclaw webhooks gmail setup --account you@example.com --hook-url https://gateway.example.com/hooks/gmail
```

### `webhooks gmail run`

`gog watch serve`와 watch 자동 갱신 루프를 실행합니다.

옵션:

- `--account <email>`
- `--topic <topic>`
- `--subscription <name>`
- `--label <label>`
- `--hook-url <url>`
- `--hook-token <token>`
- `--push-token <token>`
- `--bind <host>`
- `--port <port>`
- `--path <path>`
- `--include-body`
- `--max-bytes <n>`
- `--renew-minutes <n>`
- `--tailscale <funnel|serve|off>`
- `--tailscale-path <path>`
- `--tailscale-target <target>`

예시:

```bash
openclaw webhooks gmail run --account you@example.com
```

전체 설정 흐름과 운영 세부 정보는 [Gmail Pub/Sub 문서](/automation/cron-jobs#gmail-pubsub-integration)를 참조하세요.
