---
read_when:
    - 채널의 연락처/그룹/자기 ID를 조회하려고 할 때
    - 채널 디렉터리 어댑터를 개발하고 있을 때
summary: '`openclaw directory`용 CLI 참조(self, peers, groups)'
title: directory
x-i18n:
    generated_at: "2026-04-05T12:37:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6a81a037e0a33f77c24b1adabbc4be16ed4d03c419873f3cbdd63f2ce84a1064
    source_path: cli/directory.md
    workflow: 15
---

# `openclaw directory`

이를 지원하는 채널에 대한 디렉터리 조회입니다(연락처/peer, 그룹, 그리고 “나”).

## 공통 플래그

- `--channel <name>`: 채널 ID/별칭(여러 채널이 구성된 경우 필수, 하나만 구성된 경우 자동 선택)
- `--account <id>`: 계정 ID(기본값: 채널 기본 계정)
- `--json`: JSON 출력

## 참고

- `directory`는 다른 명령에 붙여 넣을 수 있는 ID를 찾는 데 도움을 주기 위한 것입니다(특히 `openclaw message send --target ...`).
- 많은 채널에서 결과는 라이브 provider 디렉터리가 아니라 구성 기반(allowlist / 구성된 그룹)입니다.
- 기본 출력은 탭으로 구분된 `id`(그리고 경우에 따라 `name`)이며, 스크립트에서는 `--json`을 사용하세요.

## `message send`와 함께 결과 사용하기

```bash
openclaw directory peers list --channel slack --query "U0"
openclaw message send --channel slack --target user:U012ABCDEF --message "hello"
```

## ID 형식(채널별)

- WhatsApp: `+15551234567`(DM), `1234567890-1234567890@g.us`(그룹)
- Telegram: `@username` 또는 숫자 채팅 ID, 그룹은 숫자 ID
- Slack: `user:U…`, `channel:C…`
- Discord: `user:<id>`, `channel:<id>`
- Matrix(plugin): `user:@user:server`, `room:!roomId:server`, 또는 `#alias:server`
- Microsoft Teams(plugin): `user:<id>`, `conversation:<id>`
- Zalo(plugin): 사용자 ID(Bot API)
- Zalo Personal / `zalouser`(plugin): `zca`의 스레드 ID(DM/그룹) (`me`, `friend list`, `group list`)

## 자기 자신("me")

```bash
openclaw directory self --channel zalouser
```

## peers(연락처/사용자)

```bash
openclaw directory peers list --channel zalouser
openclaw directory peers list --channel zalouser --query "name"
openclaw directory peers list --channel zalouser --limit 50
```

## 그룹

```bash
openclaw directory groups list --channel zalouser
openclaw directory groups list --channel zalouser --query "work"
openclaw directory groups members --channel zalouser --group-id <id>
```
