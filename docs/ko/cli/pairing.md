---
read_when:
    - pairing 모드 DM을 사용 중이고 발신자를 승인해야 하는 경우
summary: '`openclaw pairing`용 CLI 참조(페어링 요청 승인/목록)'
title: pairing
x-i18n:
    generated_at: "2026-04-05T12:38:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 122a608ef83ec2b1011fdfd1b59b94950a4dcc8b598335b0956e2eedece4958f
    source_path: cli/pairing.md
    workflow: 15
---

# `openclaw pairing`

DM 페어링 요청을 승인하거나 검사합니다(페어링을 지원하는 채널용).

관련 문서:

- 페어링 흐름: [페어링](/channels/pairing)

## 명령

```bash
openclaw pairing list telegram
openclaw pairing list --channel telegram --account work
openclaw pairing list telegram --json

openclaw pairing approve <code>
openclaw pairing approve telegram <code>
openclaw pairing approve --channel telegram --account work <code> --notify
```

## `pairing list`

하나의 채널에 대한 대기 중인 페어링 요청을 나열합니다.

옵션:

- `[channel]`: 위치 기반 채널 ID
- `--channel <channel>`: 명시적 채널 ID
- `--account <accountId>`: 다중 계정 채널용 계정 ID
- `--json`: 기계 판독 가능 출력

참고:

- 여러 페어링 지원 채널이 구성된 경우, 위치 인수 또는 `--channel`을 사용해 채널을 제공해야 합니다.
- 채널 ID가 유효한 한 extension 채널도 허용됩니다.

## `pairing approve`

대기 중인 페어링 코드를 승인하고 해당 발신자를 허용합니다.

사용법:

- `openclaw pairing approve <channel> <code>`
- `openclaw pairing approve --channel <channel> <code>`
- 정확히 하나의 페어링 지원 채널만 구성된 경우 `openclaw pairing approve <code>`

옵션:

- `--channel <channel>`: 명시적 채널 ID
- `--account <accountId>`: 다중 계정 채널용 계정 ID
- `--notify`: 동일한 채널에서 요청자에게 확인 메시지 전송

## 참고

- 채널 입력: 위치 인수로 전달하거나(`pairing list telegram`) `--channel <channel>`을 사용하세요.
- `pairing list`는 다중 계정 채널에 대해 `--account <accountId>`를 지원합니다.
- `pairing approve`는 `--account <accountId>` 및 `--notify`를 지원합니다.
- 하나의 페어링 지원 채널만 구성된 경우 `pairing approve <code>`를 사용할 수 있습니다.
