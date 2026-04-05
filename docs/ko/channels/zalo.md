---
read_when:
    - Zalo 기능 또는 웹훅 작업 중
summary: Zalo 봇 지원 상태, 기능 및 구성
title: Zalo
x-i18n:
    generated_at: "2026-04-05T12:37:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: ab94642ba28e79605b67586af8f71c18bc10e0af60343a7df508e6823b6f4119
    source_path: channels/zalo.md
    workflow: 15
---

# Zalo (Bot API)

상태: 실험적입니다. DM이 지원됩니다. 아래 [Capabilities](#capabilities) 섹션은 현재 Marketplace 봇 동작을 반영합니다.

## 번들 plugin

Zalo는 현재 OpenClaw 릴리스에 번들 plugin으로 포함되어 있으므로, 일반적인 패키지 빌드에서는 별도 설치가 필요하지 않습니다.

이전 빌드 또는 Zalo가 제외된 커스텀 설치를 사용 중이라면 수동으로 설치하세요.

- CLI로 설치: `openclaw plugins install @openclaw/zalo`
- 또는 소스 체크아웃에서 설치: `openclaw plugins install ./path/to/local/zalo-plugin`
- 자세한 내용: [Plugins](/tools/plugin)

## 빠른 설정(초보자용)

1. Zalo plugin을 사용할 수 있는지 확인하세요.
   - 현재 패키지된 OpenClaw 릴리스에는 이미 번들로 포함되어 있습니다.
   - 이전/커스텀 설치에서는 위 명령으로 수동 추가할 수 있습니다.
2. 토큰을 설정하세요.
   - Env: `ZALO_BOT_TOKEN=...`
   - 또는 config: `channels.zalo.accounts.default.botToken: "..."`.
3. gateway를 재시작하세요(또는 설정을 완료하세요).
4. DM 액세스는 기본적으로 페어링이며, 첫 접촉 시 페어링 코드를 승인해야 합니다.

최소 config:

```json5
{
  channels: {
    zalo: {
      enabled: true,
      accounts: {
        default: {
          botToken: "12345689:abc-xyz",
          dmPolicy: "pairing",
        },
      },
    },
  },
}
```

## 개요

Zalo는 베트남 중심의 메시징 앱이며, Bot API를 통해 Gateway가 1:1 대화용 봇을 실행할 수 있습니다.
Zalo로의 결정적 라우팅이 필요한 지원 또는 알림에 적합합니다.

이 페이지는 **Zalo Bot Creator / Marketplace bots**에 대한 현재 OpenClaw 동작을 반영합니다.
**Zalo Official Account (OA) bots**는 다른 Zalo 제품 표면이며 동작이 다를 수 있습니다.

- Gateway가 소유하는 Zalo Bot API 채널입니다.
- 결정적 라우팅: 응답은 다시 Zalo로 돌아가며, 모델이 채널을 선택하지 않습니다.
- DM은 에이전트의 메인 세션을 공유합니다.
- 아래 [Capabilities](#capabilities) 섹션은 현재 Marketplace 봇 지원 범위를 보여줍니다.

## 설정(빠른 경로)

### 1) 봇 토큰 만들기(Zalo Bot Platform)

1. [https://bot.zaloplatforms.com](https://bot.zaloplatforms.com)으로 이동해 로그인합니다.
2. 새 봇을 만들고 설정을 구성합니다.
3. 전체 봇 토큰(보통 `numeric_id:secret`)을 복사합니다. Marketplace 봇의 경우, 실제 런타임에서 사용할 수 있는 토큰은 생성 후 봇 환영 메시지에 표시될 수 있습니다.

### 2) 토큰 구성(env 또는 config)

예시:

```json5
{
  channels: {
    zalo: {
      enabled: true,
      accounts: {
        default: {
          botToken: "12345689:abc-xyz",
          dmPolicy: "pairing",
        },
      },
    },
  },
}
```

나중에 그룹을 사용할 수 있는 Zalo 봇 표면으로 이동하면 `groupPolicy` 및 `groupAllowFrom` 같은 그룹별 config를 명시적으로 추가할 수 있습니다. 현재 Marketplace 봇 동작은 [Capabilities](#capabilities)를 참조하세요.

Env 옵션: `ZALO_BOT_TOKEN=...` (기본 계정에서만 작동).

다중 계정 지원: `channels.zalo.accounts`를 사용해 계정별 토큰과 선택적 `name`을 설정합니다.

3. gateway를 재시작하세요. 토큰이 확인되면(env 또는 config) Zalo가 시작됩니다.
4. DM 액세스의 기본값은 페어링입니다. 봇에 처음 연락할 때 코드를 승인하세요.

## 작동 방식(동작)

- 수신 메시지는 미디어 플레이스홀더가 포함된 공유 채널 엔벌로프로 정규화됩니다.
- 응답은 항상 동일한 Zalo 채팅으로 다시 라우팅됩니다.
- 기본값은 long-polling이며, `channels.zalo.webhookUrl`을 사용하면 webhook 모드를 사용할 수 있습니다.

## 제한 사항

- 발신 텍스트는 2000자로 분할됩니다(Zalo API 제한).
- 미디어 다운로드/업로드는 `channels.zalo.mediaMaxMb`(기본값 5)로 제한됩니다.
- 2000자 제한으로 인해 스트리밍의 유용성이 낮아서 기본적으로 스트리밍은 차단됩니다.

## 액세스 제어(DM)

### DM 액세스

- 기본값: `channels.zalo.dmPolicy = "pairing"`. 알 수 없는 발신자는 페어링 코드를 받으며, 승인되기 전까지 메시지는 무시됩니다(코드는 1시간 후 만료).
- 승인 방법:
  - `openclaw pairing list zalo`
  - `openclaw pairing approve zalo <CODE>`
- 페어링은 기본 토큰 교환 방식입니다. 자세한 내용: [Pairing](/channels/pairing)
- `channels.zalo.allowFrom`은 숫자 사용자 ID를 받습니다(사용자 이름 조회는 제공되지 않음).

## 액세스 제어(Groups)

**Zalo Bot Creator / Marketplace bots**의 경우, 실제로는 봇을 그룹에 아예 추가할 수 없었기 때문에 그룹 지원을 사용할 수 없었습니다.

즉, 아래 그룹 관련 config 키는 스키마에 존재하지만 Marketplace 봇에서는 사용할 수 없었습니다.

- `channels.zalo.groupPolicy`는 그룹 수신 처리를 제어합니다: `open | allowlist | disabled`.
- `channels.zalo.groupAllowFrom`은 그룹에서 어떤 발신자 ID가 봇을 트리거할 수 있는지 제한합니다.
- `groupAllowFrom`이 설정되지 않으면, Zalo는 발신자 검사에 `allowFrom`으로 폴백합니다.
- 런타임 참고: `channels.zalo`가 완전히 누락된 경우에도 안전을 위해 런타임은 여전히 `groupPolicy="allowlist"`로 폴백합니다.

그룹 액세스를 봇 표면에서 사용할 수 있을 때의 그룹 정책 값은 다음과 같습니다.

- `groupPolicy: "disabled"` — 모든 그룹 메시지를 차단합니다.
- `groupPolicy: "open"` — 모든 그룹 멤버를 허용합니다(mention 게이트 적용).
- `groupPolicy: "allowlist"` — fail-closed 기본값이며, 허용된 발신자만 수락합니다.

다른 Zalo 봇 제품 표면을 사용 중이고 실제로 작동하는 그룹 동작을 확인했다면, Marketplace 봇 흐름과 같다고 가정하지 말고 별도로 문서화하세요.

## Long-polling vs webhook

- 기본값: long-polling(공개 URL 불필요).
- Webhook 모드: `channels.zalo.webhookUrl` 및 `channels.zalo.webhookSecret`를 설정하세요.
  - webhook secret은 8~256자여야 합니다.
  - webhook URL은 HTTPS를 사용해야 합니다.
  - Zalo는 검증을 위해 `X-Bot-Api-Secret-Token` 헤더와 함께 이벤트를 보냅니다.
  - Gateway HTTP는 `channels.zalo.webhookPath`에서 webhook 요청을 처리합니다(기본값: webhook URL 경로).
  - 요청은 `Content-Type: application/json`(또는 `+json` 미디어 타입)을 사용해야 합니다.
  - 중복 이벤트(`event_name + message_id`)는 짧은 재생 방지 창 동안 무시됩니다.
  - 버스트 트래픽은 경로/소스별로 속도 제한되며 HTTP 429를 반환할 수 있습니다.

**참고:** Zalo API 문서에 따라 getUpdates(polling)와 webhook은 동시에 사용할 수 없습니다.

## 지원되는 메시지 유형

빠른 지원 현황은 [Capabilities](#capabilities)를 참조하세요. 아래 참고 사항은 동작에 추가 컨텍스트가 필요한 부분을 보완합니다.

- **텍스트 메시지**: 2000자 분할과 함께 완전 지원.
- **텍스트 내 일반 URL**: 일반 텍스트 입력처럼 동작합니다.
- **링크 미리보기 / 리치 링크 카드**: [Capabilities](#capabilities)의 Marketplace 봇 상태를 참조하세요. 안정적으로 응답을 트리거하지 못했습니다.
- **이미지 메시지**: [Capabilities](#capabilities)의 Marketplace 봇 상태를 참조하세요. 수신 이미지 처리는 신뢰할 수 없었습니다(최종 응답 없이 타이핑 표시만 나타남).
- **스티커**: [Capabilities](#capabilities)의 Marketplace 봇 상태를 참조하세요.
- **음성 메모 / 오디오 파일 / 비디오 / 일반 파일 첨부**: [Capabilities](#capabilities)의 Marketplace 봇 상태를 참조하세요.
- **지원되지 않는 유형**: 기록됩니다(예: 보호된 사용자의 메시지).

## Capabilities

이 표는 OpenClaw에서의 현재 **Zalo Bot Creator / Marketplace bot** 동작을 요약합니다.

| 기능                        | 상태                                    |
| --------------------------- | --------------------------------------- |
| 다이렉트 메시지             | ✅ 지원됨                               |
| Groups                      | ❌ Marketplace 봇에서는 사용 불가       |
| 미디어(수신 이미지)         | ⚠️ 제한적 / 환경에서 확인 필요          |
| 미디어(발신 이미지)         | ⚠️ Marketplace 봇에서 재테스트 안 됨    |
| 텍스트 내 일반 URL          | ✅ 지원됨                               |
| 링크 미리보기               | ⚠️ Marketplace 봇에서는 신뢰하기 어려움 |
| Reactions                   | ❌ 지원되지 않음                        |
| 스티커                      | ⚠️ Marketplace 봇에서는 에이전트 응답 없음 |
| 음성 메모 / 오디오 / 비디오 | ⚠️ Marketplace 봇에서는 에이전트 응답 없음 |
| 파일 첨부                   | ⚠️ Marketplace 봇에서는 에이전트 응답 없음 |
| Threads                     | ❌ 지원되지 않음                        |
| Polls                       | ❌ 지원되지 않음                        |
| Native commands             | ❌ 지원되지 않음                        |
| Streaming                   | ⚠️ 차단됨(2000자 제한)                  |

## 전달 대상(CLI/cron)

- 대화 ID를 대상으로 사용하세요.
- 예시: `openclaw message send --channel zalo --target 123456789 --message "hi"`.

## 문제 해결

**봇이 응답하지 않음:**

- 토큰이 유효한지 확인하세요: `openclaw channels status --probe`
- 발신자가 승인되었는지 확인하세요(페어링 또는 allowFrom)
- gateway 로그를 확인하세요: `openclaw logs --follow`

**Webhook이 이벤트를 수신하지 않음:**

- webhook URL이 HTTPS를 사용하는지 확인하세요
- secret token이 8~256자인지 확인하세요
- 구성된 경로에서 gateway HTTP 엔드포인트에 도달할 수 있는지 확인하세요
- getUpdates polling이 실행 중이 아닌지 확인하세요(둘은 동시에 사용할 수 없음)

## 구성 참조(Zalo)

전체 구성: [Configuration](/gateway/configuration)

평면 최상위 키(`channels.zalo.botToken`, `channels.zalo.dmPolicy` 등)는 레거시 단일 계정 축약형입니다. 새 config에는 `channels.zalo.accounts.<id>.*`를 권장합니다. 두 형식 모두 스키마에 존재하므로 여기서 계속 문서화합니다.

Provider 옵션:

- `channels.zalo.enabled`: 채널 시작 활성화/비활성화.
- `channels.zalo.botToken`: Zalo Bot Platform의 봇 토큰.
- `channels.zalo.tokenFile`: 일반 파일 경로에서 토큰을 읽습니다. 심볼릭 링크는 거부됩니다.
- `channels.zalo.dmPolicy`: `pairing | allowlist | open | disabled` (기본값: pairing).
- `channels.zalo.allowFrom`: DM allowlist(사용자 ID). `open`에는 `"*"`가 필요합니다. 마법사는 숫자 ID를 요청합니다.
- `channels.zalo.groupPolicy`: `open | allowlist | disabled` (기본값: allowlist). config에는 존재하며, 현재 Marketplace 봇 동작은 [Capabilities](#capabilities) 및 [Access control (Groups)](#access-control-groups)를 참조하세요.
- `channels.zalo.groupAllowFrom`: 그룹 발신자 allowlist(사용자 ID). 설정되지 않으면 `allowFrom`으로 폴백합니다.
- `channels.zalo.mediaMaxMb`: 수신/발신 미디어 상한(MB, 기본값 5).
- `channels.zalo.webhookUrl`: webhook 모드 활성화(HTTPS 필수).
- `channels.zalo.webhookSecret`: webhook secret(8~256자).
- `channels.zalo.webhookPath`: gateway HTTP 서버의 webhook 경로.
- `channels.zalo.proxy`: API 요청용 프록시 URL.

다중 계정 옵션:

- `channels.zalo.accounts.<id>.botToken`: 계정별 토큰.
- `channels.zalo.accounts.<id>.tokenFile`: 계정별 일반 토큰 파일. 심볼릭 링크는 거부됩니다.
- `channels.zalo.accounts.<id>.name`: 표시 이름.
- `channels.zalo.accounts.<id>.enabled`: 계정 활성화/비활성화.
- `channels.zalo.accounts.<id>.dmPolicy`: 계정별 DM 정책.
- `channels.zalo.accounts.<id>.allowFrom`: 계정별 allowlist.
- `channels.zalo.accounts.<id>.groupPolicy`: 계정별 그룹 정책. config에는 존재하며, 현재 Marketplace 봇 동작은 [Capabilities](#capabilities) 및 [Access control (Groups)](#access-control-groups)를 참조하세요.
- `channels.zalo.accounts.<id>.groupAllowFrom`: 계정별 그룹 발신자 allowlist.
- `channels.zalo.accounts.<id>.webhookUrl`: 계정별 webhook URL.
- `channels.zalo.accounts.<id>.webhookSecret`: 계정별 webhook secret.
- `channels.zalo.accounts.<id>.webhookPath`: 계정별 webhook 경로.
- `channels.zalo.accounts.<id>.proxy`: 계정별 프록시 URL.

## 관련 문서

- [Channels Overview](/channels) — 지원되는 모든 채널
- [Pairing](/channels/pairing) — DM 인증 및 페어링 흐름
- [Groups](/channels/groups) — 그룹 채팅 동작 및 mention 게이팅
- [Channel Routing](/channels/channel-routing) — 메시지의 세션 라우팅
- [Security](/gateway/security) — 액세스 모델 및 강화
