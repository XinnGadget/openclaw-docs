---
read_when:
    - 메시지 CLI 작업을 추가하거나 수정하는 경우
    - 아웃바운드 채널 동작을 변경하는 경우
summary: '`openclaw message`용 CLI 참조(전송 + 채널 작업)'
title: message
x-i18n:
    generated_at: "2026-04-05T12:38:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: b70f36189d028d59db25cd8b39d7c67883eaea71bea2358ee6314eec6cd2fa51
    source_path: cli/message.md
    workflow: 15
---

# `openclaw message`

메시지 전송 및 채널 작업을 위한 단일 아웃바운드 명령입니다
(Discord/Google Chat/iMessage/Matrix/Mattermost (plugin)/Microsoft Teams/Signal/Slack/Telegram/WhatsApp).

## 사용법

```
openclaw message <subcommand> [flags]
```

채널 선택:

- 둘 이상의 채널이 구성된 경우 `--channel`이 필요합니다.
- 정확히 하나의 채널만 구성된 경우 해당 채널이 기본값이 됩니다.
- 값: `discord|googlechat|imessage|matrix|mattermost|msteams|signal|slack|telegram|whatsapp` (Mattermost는 plugin 필요)

대상 형식(`--target`):

- WhatsApp: E.164 또는 그룹 JID
- Telegram: chat id 또는 `@username`
- Discord: `channel:<id>` 또는 `user:<id>` (또는 `<@id>` 멘션; 원시 숫자 id는 채널로 처리됨)
- Google Chat: `spaces/<spaceId>` 또는 `users/<userId>`
- Slack: `channel:<id>` 또는 `user:<id>` (원시 channel id 허용)
- Mattermost (plugin): `channel:<id>`, `user:<id>`, 또는 `@username` (접두사 없는 id는 채널로 처리됨)
- Signal: `+E.164`, `group:<id>`, `signal:+E.164`, `signal:group:<id>`, 또는 `username:<name>`/`u:<name>`
- iMessage: handle, `chat_id:<id>`, `chat_guid:<guid>`, 또는 `chat_identifier:<id>`
- Matrix: `@user:server`, `!room:server`, 또는 `#alias:server`
- Microsoft Teams: conversation id (`19:...@thread.tacv2`) 또는 `conversation:<id>` 또는 `user:<aad-object-id>`

이름 조회:

- 지원되는 provider(Discord/Slack 등)의 경우 `Help` 또는 `#help` 같은 채널 이름은 디렉터리 캐시를 통해 확인됩니다.
- 캐시 미스가 발생하면 provider가 지원하는 경우 OpenClaw가 실시간 디렉터리 조회를 시도합니다.

## 공통 플래그

- `--channel <name>`
- `--account <id>`
- `--target <dest>` (send/poll/read 등용 대상 채널 또는 사용자)
- `--targets <name>` (반복 가능, broadcast 전용)
- `--json`
- `--dry-run`
- `--verbose`

## SecretRef 동작

- `openclaw message`는 선택한 작업을 실행하기 전에 지원되는 채널 SecretRef를 해석합니다.
- 가능할 때 해석 범위는 활성 작업 대상에 맞춰 제한됩니다.
  - `--channel`이 설정된 경우(또는 `discord:...` 같은 접두사 대상에서 추론된 경우) 채널 범위
  - `--account`가 설정된 경우 계정 범위(채널 전역 + 선택한 계정 표면)
  - `--account`를 생략하면 OpenClaw는 `default` 계정 SecretRef 범위를 강제하지 않습니다
- 관련 없는 채널의 미해결 SecretRef는 대상 지정된 메시지 작업을 차단하지 않습니다.
- 선택한 채널/계정 SecretRef가 해석되지 않으면 해당 작업에 대해 명령은 실패 시 닫힘 방식으로 처리됩니다.

## 작업

### 코어

- `send`
  - 채널: WhatsApp/Telegram/Discord/Google Chat/Slack/Mattermost (plugin)/Signal/iMessage/Matrix/Microsoft Teams
  - 필수: `--target`, 그리고 `--message` 또는 `--media`
  - 선택 사항: `--media`, `--interactive`, `--buttons`, `--components`, `--card`, `--reply-to`, `--thread-id`, `--gif-playback`, `--force-document`, `--silent`
  - 공유 interactive payload: 지원되는 경우 `--interactive`는 채널 네이티브 interactive JSON payload를 전송합니다
  - Telegram 전용: `--buttons` (`channels.telegram.capabilities.inlineButtons`가 이를 허용해야 함)
  - Telegram 전용: `--force-document` (Telegram 압축을 피하기 위해 이미지와 GIF를 document로 전송)
  - Telegram 전용: `--thread-id` (포럼 topic id)
  - Slack 전용: `--thread-id` (thread timestamp, `--reply-to`는 동일한 필드 사용)
  - Discord 전용: `--components` JSON payload
  - Adaptive-card 채널: 지원되는 경우 `--card` JSON payload
  - Telegram + Discord: `--silent`
  - WhatsApp 전용: `--gif-playback`

- `poll`
  - 채널: WhatsApp/Telegram/Discord/Matrix/Microsoft Teams
  - 필수: `--target`, `--poll-question`, `--poll-option` (반복)
  - 선택 사항: `--poll-multi`
  - Discord 전용: `--poll-duration-hours`, `--silent`, `--message`
  - Telegram 전용: `--poll-duration-seconds` (5-600), `--silent`, `--poll-anonymous` / `--poll-public`, `--thread-id`

- `react`
  - 채널: Discord/Google Chat/Slack/Telegram/WhatsApp/Signal/Matrix
  - 필수: `--message-id`, `--target`
  - 선택 사항: `--emoji`, `--remove`, `--participant`, `--from-me`, `--target-author`, `--target-author-uuid`
  - 참고: `--remove`에는 `--emoji`가 필요합니다(지원되는 경우 자신의 반응을 지우려면 `--emoji`를 생략, /tools/reactions 참조)
  - WhatsApp 전용: `--participant`, `--from-me`
  - Signal 그룹 반응: `--target-author` 또는 `--target-author-uuid` 필요

- `reactions`
  - 채널: Discord/Google Chat/Slack/Matrix
  - 필수: `--message-id`, `--target`
  - 선택 사항: `--limit`

- `read`
  - 채널: Discord/Slack/Matrix
  - 필수: `--target`
  - 선택 사항: `--limit`, `--before`, `--after`
  - Discord 전용: `--around`

- `edit`
  - 채널: Discord/Slack/Matrix
  - 필수: `--message-id`, `--message`, `--target`

- `delete`
  - 채널: Discord/Slack/Telegram/Matrix
  - 필수: `--message-id`, `--target`

- `pin` / `unpin`
  - 채널: Discord/Slack/Matrix
  - 필수: `--message-id`, `--target`

- `pins` (목록)
  - 채널: Discord/Slack/Matrix
  - 필수: `--target`

- `permissions`
  - 채널: Discord/Matrix
  - 필수: `--target`
  - Matrix 전용: Matrix 암호화가 활성화되고 verification 작업이 허용된 경우 사용 가능

- `search`
  - 채널: Discord
  - 필수: `--guild-id`, `--query`
  - 선택 사항: `--channel-id`, `--channel-ids` (반복), `--author-id`, `--author-ids` (반복), `--limit`

### 스레드

- `thread create`
  - 채널: Discord
  - 필수: `--thread-name`, `--target` (channel id)
  - 선택 사항: `--message-id`, `--message`, `--auto-archive-min`

- `thread list`
  - 채널: Discord
  - 필수: `--guild-id`
  - 선택 사항: `--channel-id`, `--include-archived`, `--before`, `--limit`

- `thread reply`
  - 채널: Discord
  - 필수: `--target` (thread id), `--message`
  - 선택 사항: `--media`, `--reply-to`

### 이모지

- `emoji list`
  - Discord: `--guild-id`
  - Slack: 추가 플래그 없음

- `emoji upload`
  - 채널: Discord
  - 필수: `--guild-id`, `--emoji-name`, `--media`
  - 선택 사항: `--role-ids` (반복)

### 스티커

- `sticker send`
  - 채널: Discord
  - 필수: `--target`, `--sticker-id` (반복)
  - 선택 사항: `--message`

- `sticker upload`
  - 채널: Discord
  - 필수: `--guild-id`, `--sticker-name`, `--sticker-desc`, `--sticker-tags`, `--media`

### 역할 / 채널 / 멤버 / 음성

- `role info` (Discord): `--guild-id`
- `role add` / `role remove` (Discord): `--guild-id`, `--user-id`, `--role-id`
- `channel info` (Discord): `--target`
- `channel list` (Discord): `--guild-id`
- `member info` (Discord/Slack): `--user-id` (+ Discord의 경우 `--guild-id`)
- `voice status` (Discord): `--guild-id`, `--user-id`

### 이벤트

- `event list` (Discord): `--guild-id`
- `event create` (Discord): `--guild-id`, `--event-name`, `--start-time`
  - 선택 사항: `--end-time`, `--desc`, `--channel-id`, `--location`, `--event-type`

### moderation (Discord)

- `timeout`: `--guild-id`, `--user-id` (선택 사항 `--duration-min` 또는 `--until`, 둘 다 생략하면 timeout 해제)
- `kick`: `--guild-id`, `--user-id` (+ `--reason`)
- `ban`: `--guild-id`, `--user-id` (+ `--delete-days`, `--reason`)
  - `timeout`도 `--reason`을 지원합니다

### broadcast

- `broadcast`
  - 채널: 구성된 모든 채널, 모든 provider를 대상으로 하려면 `--channel all` 사용
  - 필수: `--targets <target...>`
  - 선택 사항: `--message`, `--media`, `--dry-run`

## 예시

Discord 응답 전송:

```
openclaw message send --channel discord \
  --target channel:123 --message "hi" --reply-to 456
```

components가 포함된 Discord 메시지 전송:

```
openclaw message send --channel discord \
  --target channel:123 --message "Choose:" \
  --components '{"text":"Choose a path","blocks":[{"type":"actions","buttons":[{"label":"Approve","style":"success"},{"label":"Decline","style":"danger"}]}]}'
```

전체 스키마는 [Discord components](/channels/discord#interactive-components)를 참조하세요.

공유 interactive payload 전송:

```bash
openclaw message send --channel googlechat --target spaces/AAA... \
  --message "Choose:" \
  --interactive '{"text":"Choose a path","blocks":[{"type":"actions","buttons":[{"label":"Approve"},{"label":"Decline"}]}]}'
```

Discord Poll 생성:

```
openclaw message poll --channel discord \
  --target channel:123 \
  --poll-question "Snack?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-multi --poll-duration-hours 48
```

Telegram Poll 생성(2분 후 자동 종료):

```
openclaw message poll --channel telegram \
  --target @mychat \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi \
  --poll-duration-seconds 120 --silent
```

Teams proactive 메시지 전송:

```
openclaw message send --channel msteams \
  --target conversation:19:abc@thread.tacv2 --message "hi"
```

Teams Poll 생성:

```
openclaw message poll --channel msteams \
  --target conversation:19:abc@thread.tacv2 \
  --poll-question "Lunch?" \
  --poll-option Pizza --poll-option Sushi
```

Slack에서 반응 추가:

```
openclaw message react --channel slack \
  --target C123 --message-id 456 --emoji "✅"
```

Signal 그룹에서 반응 추가:

```
openclaw message react --channel signal \
  --target signal:group:abc123 --message-id 1737630212345 \
  --emoji "✅" --target-author-uuid 123e4567-e89b-12d3-a456-426614174000
```

Telegram inline button 전송:

```
openclaw message send --channel telegram --target @mychat --message "Choose:" \
  --buttons '[ [{"text":"Yes","callback_data":"cmd:yes"}], [{"text":"No","callback_data":"cmd:no"}] ]'
```

Teams Adaptive Card 전송:

```bash
openclaw message send --channel msteams \
  --target conversation:19:abc@thread.tacv2 \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Status update"}]}'
```

압축을 피하기 위해 Telegram 이미지를 document로 전송:

```bash
openclaw message send --channel telegram --target @mychat \
  --media ./diagram.png --force-document
```
