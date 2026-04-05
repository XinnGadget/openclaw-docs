---
read_when:
    - OpenClaw를 QQ에 연결하려는 경우
    - QQ Bot 자격 증명 설정이 필요한 경우
    - QQ Bot 그룹 또는 개인 채팅 지원을 사용하려는 경우
summary: QQ Bot 설정, 구성 및 사용법
title: QQ Bot
x-i18n:
    generated_at: "2026-04-05T12:36:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 0e58fb7b07c59ecbf80a1276368c4a007b45d84e296ed40cffe9845e0953696c
    source_path: channels/qqbot.md
    workflow: 15
---

# QQ Bot

QQ Bot은 공식 QQ Bot API(WebSocket gateway)를 통해 OpenClaw에 연결됩니다. 이 plugin은 풍부한 미디어(이미지, 음성, 비디오, 파일)와 함께 C2C 개인 채팅, 그룹 @메시지, 길드 채널 메시지를 지원합니다.

상태: 번들 plugin. 다이렉트 메시지, 그룹 채팅, 길드 채널 및 미디어가 지원됩니다. 반응과 스레드는 지원되지 않습니다.

## 번들 plugin

현재 OpenClaw 릴리스에는 QQ Bot이 번들로 포함되어 있으므로 일반 패키지형 빌드에서는 별도의 `openclaw plugins install` 단계가 필요하지 않습니다.

## 설정

1. [QQ Open Platform](https://q.qq.com/)으로 이동해 휴대폰 QQ로 QR 코드를 스캔하여 등록/로그인합니다.
2. **Create Bot**을 클릭해 새 QQ 봇을 만듭니다.
3. 봇 설정 페이지에서 **AppID**와 **AppSecret**을 찾아 복사합니다.

> AppSecret은 평문으로 저장되지 않으므로 저장하지 않고 페이지를 나가면 새로 다시 생성해야 합니다.

4. 채널을 추가합니다.

```bash
openclaw channels add --channel qqbot --token "AppID:AppSecret"
```

5. Gateway를 재시작합니다.

대화형 설정 경로:

```bash
openclaw channels add
openclaw configure --section channels
```

## 구성

최소 config:

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "YOUR_APP_ID",
      clientSecret: "YOUR_APP_SECRET",
    },
  },
}
```

기본 계정 환경 변수:

- `QQBOT_APP_ID`
- `QQBOT_CLIENT_SECRET`

파일 기반 AppSecret:

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "YOUR_APP_ID",
      clientSecretFile: "/path/to/qqbot-secret.txt",
    },
  },
}
```

참고:

- 환경 변수 대체는 기본 QQ Bot 계정에만 적용됩니다.
- `openclaw channels add --channel qqbot --token-file ...`는 AppSecret만 제공합니다. AppID는 이미 config 또는 `QQBOT_APP_ID`에 설정되어 있어야 합니다.
- `clientSecret`은 평문 문자열뿐 아니라 SecretRef 입력도 허용합니다.

### 다중 계정 설정

하나의 OpenClaw 인스턴스에서 여러 QQ 봇을 실행합니다.

```json5
{
  channels: {
    qqbot: {
      enabled: true,
      appId: "111111111",
      clientSecret: "secret-of-bot-1",
      accounts: {
        bot2: {
          enabled: true,
          appId: "222222222",
          clientSecret: "secret-of-bot-2",
        },
      },
    },
  },
}
```

각 계정은 자체 WebSocket 연결을 시작하며 독립적인 토큰 캐시를 유지합니다(`appId`별로 격리됨).

CLI로 두 번째 봇 추가:

```bash
openclaw channels add --channel qqbot --account bot2 --token "222222222:secret-of-bot-2"
```

### 음성(STT / TTS)

STT와 TTS는 우선순위 대체를 포함한 2단계 구성을 지원합니다.

| 설정 | plugin별 | 프레임워크 대체 |
| ------- | -------------------- | ----------------------------- |
| STT     | `channels.qqbot.stt` | `tools.media.audio.models[0]` |
| TTS     | `channels.qqbot.tts` | `messages.tts`                |

```json5
{
  channels: {
    qqbot: {
      stt: {
        provider: "your-provider",
        model: "your-stt-model",
      },
      tts: {
        provider: "your-provider",
        model: "your-tts-model",
        voice: "your-voice",
      },
    },
  },
}
```

비활성화하려면 둘 중 하나에 `enabled: false`를 설정하세요.

아웃바운드 오디오 업로드/트랜스코드 동작은 `channels.qqbot.audioFormatPolicy`로도 조정할 수 있습니다.

- `sttDirectFormats`
- `uploadDirectFormats`
- `transcodeEnabled`

## 대상 형식

| 형식 | 설명 |
| -------------------------- | ------------------ |
| `qqbot:c2c:OPENID`         | 개인 채팅(C2C) |
| `qqbot:group:GROUP_OPENID` | 그룹 채팅 |
| `qqbot:channel:CHANNEL_ID` | 길드 채널 |

> 각 봇은 자체 사용자 OpenID 집합을 가집니다. Bot A가 받은 OpenID는 Bot B를 통해 메시지를 보내는 데 **사용할 수 없습니다**.

## 슬래시 명령

AI 큐보다 먼저 가로채는 내장 명령:

| 명령 | 설명 |
| -------------- | ------------------------------------ |
| `/bot-ping`    | 지연 시간 테스트 |
| `/bot-version` | OpenClaw 프레임워크 버전 표시 |
| `/bot-help`    | 모든 명령 나열 |
| `/bot-upgrade` | QQBot 업그레이드 가이드 링크 표시 |
| `/bot-logs`    | 최근 gateway 로그를 파일로 내보내기 |

사용법 도움말을 보려면 아무 명령에나 `?`를 추가하세요(예: `/bot-upgrade ?`).

## 문제 해결

- **봇이 "gone to Mars"라고 응답함:** 자격 증명이 구성되지 않았거나 Gateway가 시작되지 않았습니다.
- **인바운드 메시지가 없음:** `appId`와 `clientSecret`이 올바른지, 그리고 봇이 QQ Open Platform에서 활성화되어 있는지 확인하세요.
- **`--token-file`로 설정했는데도 여전히 미구성으로 표시됨:** `--token-file`은 AppSecret만 설정합니다. 여전히 config 또는 `QQBOT_APP_ID`에 `appId`가 필요합니다.
- **사전 발송 메시지가 도착하지 않음:** 사용자가 최근 상호작용하지 않았다면 QQ가 봇이 시작한 메시지를 차단할 수 있습니다.
- **음성이 전사되지 않음:** STT가 구성되어 있고 공급자에 연결할 수 있는지 확인하세요.
