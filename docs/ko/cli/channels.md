---
read_when:
    - 채널 account(WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage/Matrix)를 추가/제거하려고 함
    - 채널 상태를 확인하거나 채널 로그를 실시간으로 보려고 함
summary: '`openclaw channels`용 CLI 참조(accounts, status, login/logout, logs)'
title: channels
x-i18n:
    generated_at: "2026-04-05T12:37:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: d0f558fdb5f6ec54e7fdb7a88e5c24c9d2567174341bd3ea87848bce4cba5d29
    source_path: cli/channels.md
    workflow: 15
---

# `openclaw channels`

Gateway에서 채팅 채널 accounts와 해당 런타임 상태를 관리합니다.

관련 문서:

- 채널 가이드: [Channels](/channels/index)
- Gateway 구성: [Configuration](/gateway/configuration)

## 일반적인 명령

```bash
openclaw channels list
openclaw channels status
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels logs --channel all
```

## 상태 / capabilities / resolve / logs

- `channels status`: `--probe`, `--timeout <ms>`, `--json`
- `channels capabilities`: `--channel <name>`, `--account <id>` (`--channel`과 함께만 사용), `--target <dest>`, `--timeout <ms>`, `--json`
- `channels resolve`: `<entries...>`, `--channel <name>`, `--account <id>`, `--kind <auto|user|group>`, `--json`
- `channels logs`: `--channel <name|all>`, `--lines <n>`, `--json`

`channels status --probe`는 라이브 경로입니다. gateway에 연결할 수 있으면 account별
`probeAccount` 및 선택적 `auditAccount` 검사를 실행하므로 출력에 전송
상태와 함께 `works`, `probe failed`, `audit ok`, `audit failed` 같은 프로브 결과가 포함될 수 있습니다.
gateway에 연결할 수 없으면 `channels status`는 라이브 프로브 출력 대신
config 전용 요약으로 폴백합니다.

## accounts 추가 / 제거

```bash
openclaw channels add --channel telegram --token <bot-token>
openclaw channels add --channel nostr --private-key "$NOSTR_PRIVATE_KEY"
openclaw channels remove --channel telegram --delete
```

팁: `openclaw channels add --help`는 채널별 플래그(token, private key, app token, signal-cli 경로 등)를 표시합니다.

일반적인 비대화형 add 표면은 다음과 같습니다.

- bot-token 채널: `--token`, `--bot-token`, `--app-token`, `--token-file`
- Signal/iMessage 전송 필드: `--signal-number`, `--cli-path`, `--http-url`, `--http-host`, `--http-port`, `--db-path`, `--service`, `--region`
- Google Chat 필드: `--webhook-path`, `--webhook-url`, `--audience-type`, `--audience`
- Matrix 필드: `--homeserver`, `--user-id`, `--access-token`, `--password`, `--device-name`, `--initial-sync-limit`
- Nostr 필드: `--private-key`, `--relay-urls`
- Tlon 필드: `--ship`, `--url`, `--code`, `--group-channels`, `--dm-allowlist`, `--auto-discover-channels`
- 지원되는 경우 기본 account의 env 기반 인증에 사용하는 `--use-env`

플래그 없이 `openclaw channels add`를 실행하면 대화형 마법사가 다음을 물을 수 있습니다.

- 선택한 채널별 account ID
- 해당 accounts의 선택적 표시 이름
- `Bind configured channel accounts to agents now?`

지금 bind를 확인하면, 마법사는 구성된 각 채널 account를 어떤 에이전트가 소유할지 묻고 account 범위 라우팅 바인딩을 기록합니다.

동일한 라우팅 규칙은 나중에 `openclaw agents bindings`, `openclaw agents bind`, `openclaw agents unbind`로도 관리할 수 있습니다([agents](/cli/agents) 참조).

여전히 단일 account 최상위 설정을 사용하는 채널에 비기본 account를 추가하면, OpenClaw는 새 account를 기록하기 전에 account 범위 최상위 값을 해당 채널의 account 맵으로 승격합니다. 대부분의 채널은 이 값을 `channels.<channel>.accounts.default`에 배치하지만, 번들 채널은 대신 기존에 일치하는 승격 account를 유지할 수 있습니다. Matrix가 현재 예시입니다. 이미 하나의 이름 있는 account가 존재하거나 `defaultAccount`가 기존 이름 있는 account를 가리키는 경우, 승격은 새 `accounts.default`를 만드는 대신 해당 account를 유지합니다.

라우팅 동작은 일관되게 유지됩니다.

- 기존 채널 전용 바인딩(`accountId` 없음)은 계속 기본 account와 일치합니다.
- `channels add`는 비대화형 모드에서 바인딩을 자동 생성하거나 재작성하지 않습니다.
- 대화형 설정은 선택적으로 account 범위 바인딩을 추가할 수 있습니다.

config가 이미 혼합 상태(이름 있는 accounts가 있고 최상위 단일 account 값도 여전히 설정됨)였다면, `openclaw doctor --fix`를 실행해 account 범위 값을 해당 채널에 대해 선택된 승격 account로 이동하세요. 대부분의 채널은 `accounts.default`로 승격하며, Matrix는 기존 이름 있는/default 대상을 유지할 수 있습니다.

## login / logout (대화형)

```bash
openclaw channels login --channel whatsapp
openclaw channels logout --channel whatsapp
```

참고:

- `channels login`은 `--verbose`를 지원합니다.
- 지원되는 login 대상이 하나만 구성된 경우 `channels login` / `logout`은 채널을 추론할 수 있습니다.

## 문제 해결

- 광범위한 프로브에는 `openclaw status --deep`를 실행하세요.
- 가이드형 수정에는 `openclaw doctor`를 사용하세요.
- `openclaw channels list`에 `Claude: HTTP 403 ... user:profile`이 출력되면 사용량 스냅샷에 `user:profile` scope가 필요하다는 뜻입니다. `--no-usage`를 사용하거나, claude.ai 세션 키(`CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`)를 제공하거나, Claude CLI를 통해 다시 인증하세요.
- gateway에 연결할 수 없으면 `openclaw channels status`는 config 전용 요약으로 폴백합니다. 지원되는 채널 자격 증명이 SecretRef를 통해 구성되었지만 현재 명령 경로에서 사용할 수 없는 경우, 해당 account를 미구성으로 표시하는 대신 저하된 상태 메모와 함께 구성됨으로 보고합니다.

## Capabilities 프로브

사용 가능한 경우 provider capability 힌트(intents/scopes)와 정적 기능 지원을 가져옵니다.

```bash
openclaw channels capabilities
openclaw channels capabilities --channel discord --target channel:123
```

참고:

- `--channel`은 선택 사항입니다. 생략하면 모든 채널(extensions 포함)을 나열합니다.
- `--account`는 `--channel`과 함께 사용할 때만 유효합니다.
- `--target`은 `channel:<id>` 또는 순수 숫자 채널 ID를 받으며 Discord에만 적용됩니다.
- 프로브는 provider별입니다. Discord intents + 선택적 채널 권한, Slack bot + user scopes, Telegram bot 플래그 + webhook, Signal 데몬 버전, Microsoft Teams 앱 토큰 + Graph roles/scopes(알려진 경우 주석 포함)를 포함합니다. 프로브가 없는 채널은 `Probe: unavailable`을 보고합니다.

## 이름을 ID로 resolve

provider 디렉터리를 사용해 채널/사용자 이름을 ID로 resolve합니다.

```bash
openclaw channels resolve --channel slack "#general" "@jane"
openclaw channels resolve --channel discord "My Server/#support" "@someone"
openclaw channels resolve --channel matrix "Project Room"
```

참고:

- 대상 유형을 강제하려면 `--kind user|group|auto`를 사용하세요.
- 여러 항목이 같은 이름을 공유하는 경우 resolve는 활성 항목을 우선합니다.
- `channels resolve`는 읽기 전용입니다. 선택한 account가 SecretRef를 통해 구성되었지만 현재 명령 경로에서 해당 자격 증명을 사용할 수 없는 경우, 명령은 전체 실행을 중단하는 대신 메모가 포함된 저하된 미해결 결과를 반환합니다.
