---
read_when:
    - Microsoft Teams 채널 기능을 작업할 때
summary: Microsoft Teams 봇 지원 상태, 기능 및 구성
title: Microsoft Teams
x-i18n:
    generated_at: "2026-04-05T12:37:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 99fc6e136893ec65dc85d3bc0c0d92134069a2f3b8cb4fcf66c14674399b3eaf
    source_path: channels/msteams.md
    workflow: 15
---

# Microsoft Teams

> "이곳에 들어오는 자여, 모든 희망을 버려라."

업데이트: 2026-01-21

상태: 텍스트 + DM 첨부파일이 지원되며, 채널/그룹 파일 전송에는 `sharePointSiteId` + Graph 권한이 필요합니다([그룹 채팅에서 파일 보내기](#sending-files-in-group-chats) 참조). Polls는 Adaptive Cards를 통해 전송됩니다. 메시지 작업은 파일 우선 전송을 위한 명시적 `upload-file`을 노출합니다.

## 번들 플러그인

Microsoft Teams는 현재 OpenClaw 릴리스에 번들 플러그인으로 포함되어 있으므로,
일반적인 패키지 빌드에서는 별도 설치가 필요하지 않습니다.

이전 빌드이거나 번들 Teams가 제외된 사용자 지정 설치를 사용하는 경우,
수동으로 설치하세요.

```bash
openclaw plugins install @openclaw/msteams
```

로컬 체크아웃(깃 리포지토리에서 실행할 때):

```bash
openclaw plugins install ./path/to/local/msteams-plugin
```

자세한 내용: [Plugins](/tools/plugin)

## 빠른 설정(초보자용)

1. Microsoft Teams 플러그인을 사용할 수 있는지 확인합니다.
   - 현재 패키지형 OpenClaw 릴리스에는 이미 번들로 포함되어 있습니다.
   - 이전/사용자 지정 설치에서는 위 명령으로 수동 추가할 수 있습니다.
2. **Azure Bot**(App ID + client secret + tenant ID)을 생성합니다.
3. 해당 자격 증명으로 OpenClaw를 구성합니다.
4. 공개 URL 또는 터널을 통해 `/api/messages`(기본 포트 3978)를 노출합니다.
5. Teams 앱 패키지를 설치하고 게이트웨이를 시작합니다.

최소 config:

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

참고: 그룹 채팅은 기본적으로 차단됩니다(`channels.msteams.groupPolicy: "allowlist"`). 그룹 응답을 허용하려면 `channels.msteams.groupAllowFrom`을 설정하세요(또는 어떤 멤버든 허용하되 기본적으로 멘션 게이팅이 적용되도록 `groupPolicy: "open"`을 사용하세요).

## 목표

- Teams DM, 그룹 채팅 또는 채널을 통해 OpenClaw와 대화합니다.
- 라우팅을 결정적으로 유지합니다. 응답은 항상 수신된 채널로 돌아갑니다.
- 안전한 채널 동작을 기본값으로 사용합니다(별도 구성하지 않으면 멘션 필요).

## config 쓰기

기본적으로 Microsoft Teams는 `/config set|unset`에 의해 트리거된 config 업데이트 쓰기를 허용합니다(`commands.config: true` 필요).

다음으로 비활성화할 수 있습니다.

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## 액세스 제어(DM + 그룹)

**DM 액세스**

- 기본값: `channels.msteams.dmPolicy = "pairing"`입니다. 알 수 없는 발신자는 승인될 때까지 무시됩니다.
- `channels.msteams.allowFrom`에는 안정적인 AAD object ID를 사용하는 것이 좋습니다.
- UPN/표시 이름은 변경 가능하므로 직접 일치는 기본적으로 비활성화되어 있으며 `channels.msteams.dangerouslyAllowNameMatching: true`일 때만 활성화됩니다.
- 자격 증명이 허용되면 마법사가 Microsoft Graph를 통해 이름을 ID로 확인할 수 있습니다.

**그룹 액세스**

- 기본값: `channels.msteams.groupPolicy = "allowlist"`입니다(`groupAllowFrom`을 추가하지 않으면 차단됨). 설정되지 않았을 때 기본값을 재정의하려면 `channels.defaults.groupPolicy`를 사용하세요.
- `channels.msteams.groupAllowFrom`은 그룹 채팅/채널에서 어떤 발신자가 트리거할 수 있는지 제어합니다(`channels.msteams.allowFrom`으로 대체됨).
- 어떤 멤버든 허용하려면 `groupPolicy: "open"`을 설정하세요(그래도 기본적으로 멘션 게이팅 적용).
- **어떤 채널도 허용하지 않으려면** `channels.msteams.groupPolicy: "disabled"`를 설정하세요.

예시:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**Teams + 채널 허용 목록**

- `channels.msteams.teams` 아래에 팀과 채널을 나열해 그룹/채널 응답 범위를 지정합니다.
- 키에는 안정적인 팀 ID와 채널 conversation ID를 사용해야 합니다.
- `groupPolicy="allowlist"`이고 teams 허용 목록이 있으면 나열된 팀/채널만 허용됩니다(멘션 게이팅 적용).
- 구성 마법사는 `Team/Channel` 항목을 받아 대신 저장해 줍니다.
- 시작 시 OpenClaw는 팀/채널 및 사용자 허용 목록 이름을 ID로 확인하고(Graph 권한이 허용될 때)
  매핑을 로그에 남깁니다. 확인되지 않은 팀/채널 이름은 입력된 그대로 유지되지만, `channels.msteams.dangerouslyAllowNameMatching: true`가 활성화되지 않는 한 기본적으로 라우팅에서는 무시됩니다.

예시:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## 작동 방식

1. Microsoft Teams 플러그인을 사용할 수 있는지 확인합니다.
   - 현재 패키지형 OpenClaw 릴리스에는 이미 번들로 포함되어 있습니다.
   - 이전/사용자 지정 설치에서는 위 명령으로 수동 추가할 수 있습니다.
2. **Azure Bot**(App ID + secret + tenant ID)을 생성합니다.
3. 봇을 참조하고 아래 RSC 권한을 포함하는 **Teams 앱 패키지**를 빌드합니다.
4. Teams 앱을 팀에 업로드/설치합니다(DM용 개인 범위도 가능).
5. `~/.openclaw/openclaw.json`(또는 env vars)에서 `msteams`를 구성하고 게이트웨이를 시작합니다.
6. 게이트웨이는 기본적으로 `/api/messages`에서 Bot Framework 웹훅 트래픽을 수신 대기합니다.

## Azure Bot 설정(사전 요구 사항)

OpenClaw를 구성하기 전에 Azure Bot 리소스를 생성해야 합니다.

### 1단계: Azure Bot 생성

1. [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)으로 이동합니다.
2. **Basics** 탭을 채웁니다.

   | Field              | Value                                                    |
   | ------------------ | -------------------------------------------------------- |
   | **Bot handle**     | 봇 이름(예: `openclaw-msteams`)이며 고유해야 함 |
   | **Subscription**   | Azure 구독 선택                           |
   | **Resource group** | 새로 만들거나 기존 것 사용                               |
   | **Pricing tier**   | 개발/테스트용 **Free**                                 |
   | **Type of App**    | **Single Tenant**(권장 - 아래 참고 참조)         |
   | **Creation type**  | **Create new Microsoft App ID**                          |

> **지원 중단 안내:** 새 멀티 테넌트 봇 생성은 2025-07-31 이후 지원 중단되었습니다. 새 봇에는 **Single Tenant**를 사용하세요.

3. **Review + create** → **Create**를 클릭합니다(약 1~2분 대기)

### 2단계: 자격 증명 가져오기

1. Azure Bot 리소스로 이동 → **Configuration**
2. **Microsoft App ID**를 복사 → 이것이 `appId`입니다
3. **Manage Password**를 클릭 → App Registration으로 이동
4. **Certificates & secrets** → **New client secret** → **Value**를 복사 → 이것이 `appPassword`입니다
5. **Overview**로 이동 → **Directory (tenant) ID**를 복사 → 이것이 `tenantId`입니다

### 3단계: 메시징 엔드포인트 구성

1. Azure Bot → **Configuration**
2. **Messaging endpoint**를 웹훅 URL로 설정합니다.
   - 프로덕션: `https://your-domain.com/api/messages`
   - 로컬 개발: 터널 사용([로컬 개발](#local-development-tunneling) 참조)

### 4단계: Teams 채널 활성화

1. Azure Bot → **Channels**
2. **Microsoft Teams** → Configure → Save를 클릭
3. 서비스 약관에 동의합니다

## 로컬 개발(터널링)

Teams는 `localhost`에 접근할 수 없습니다. 로컬 개발에는 터널을 사용하세요.

**옵션 A: ngrok**

```bash
ngrok http 3978
# https URL을 복사합니다. 예: https://abc123.ngrok.io
# 메시징 엔드포인트를 다음으로 설정: https://abc123.ngrok.io/api/messages
```

**옵션 B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Tailscale funnel URL을 메시징 엔드포인트로 사용하세요
```

## Teams Developer Portal(대안)

manifest ZIP를 수동 생성하는 대신 [Teams Developer Portal](https://dev.teams.microsoft.com/apps)을 사용할 수 있습니다.

1. **+ New app** 클릭
2. 기본 정보(이름, 설명, 개발자 정보) 입력
3. **App features** → **Bot**으로 이동
4. **Enter a bot ID manually**를 선택하고 Azure Bot App ID를 붙여넣기
5. 범위 선택: **Personal**, **Team**, **Group Chat**
6. **Distribute** → **Download app package** 클릭
7. Teams에서 **Apps** → **Manage your apps** → **Upload a custom app** → ZIP 선택

이 방식은 JSON manifest를 직접 편집하는 것보다 더 쉬운 경우가 많습니다.

## 봇 테스트

**옵션 A: Azure Web Chat(먼저 웹훅 확인)**

1. Azure Portal → Azure Bot 리소스 → **Test in Web Chat**
2. 메시지를 전송하면 응답이 보여야 합니다
3. 이를 통해 Teams 설정 전에 웹훅 엔드포인트가 동작하는지 확인할 수 있습니다

**옵션 B: Teams(앱 설치 후)**

1. Teams 앱 설치(사이드로드 또는 조직 카탈로그)
2. Teams에서 봇을 찾고 DM 전송
3. 게이트웨이 로그에서 들어오는 activity 확인

## 설정(최소 텍스트 전용)

1. **Microsoft Teams 플러그인을 사용할 수 있는지 확인**
   - 현재 패키지형 OpenClaw 릴리스에는 이미 번들로 포함되어 있습니다.
   - 이전/사용자 지정 설치에서는 수동으로 추가할 수 있습니다.
     - npm에서: `openclaw plugins install @openclaw/msteams`
     - 로컬 체크아웃에서: `openclaw plugins install ./path/to/local/msteams-plugin`

2. **봇 등록**
   - Azure Bot을 생성하고(위 참조) 다음을 기록합니다.
     - App ID
     - Client secret(App password)
     - Tenant ID(single-tenant)

3. **Teams 앱 manifest**
   - `botId = <App ID>`인 `bot` 항목을 포함합니다.
   - 범위: `personal`, `team`, `groupChat`.
   - `supportsFiles: true`(개인 범위 파일 처리에 필요).
   - RSC 권한(아래)을 추가합니다.
   - 아이콘 생성: `outline.png` (32x32), `color.png` (192x192).
   - 세 파일을 함께 zip으로 묶습니다: `manifest.json`, `outline.png`, `color.png`.

4. **OpenClaw 구성**

   ```json5
   {
     channels: {
       msteams: {
         enabled: true,
         appId: "<APP_ID>",
         appPassword: "<APP_PASSWORD>",
         tenantId: "<TENANT_ID>",
         webhook: { port: 3978, path: "/api/messages" },
       },
     },
   }
   ```

   config 키 대신 환경 변수를 사용할 수도 있습니다.
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`

5. **봇 엔드포인트**
   - Azure Bot Messaging Endpoint를 다음으로 설정합니다.
     - `https://<host>:3978/api/messages`(또는 선택한 path/port).

6. **게이트웨이 실행**
   - 번들 또는 수동 설치된 플러그인을 사용할 수 있고 자격 증명이 포함된 `msteams` config가 존재하면 Teams 채널이 자동으로 시작됩니다.

## 멤버 정보 작업

OpenClaw는 Microsoft Teams용 Graph 기반 `member-info` 작업을 노출하므로 에이전트와 자동화가 Microsoft Graph에서 직접 채널 멤버 정보(표시 이름, 이메일, 역할)를 확인할 수 있습니다.

요구 사항:

- `Member.Read.Group` RSC 권한(권장 manifest에 이미 포함됨)
- 팀 간 조회용: 관리자 동의가 포함된 `User.Read.All` Graph Application 권한

이 작업은 `channels.msteams.actions.memberInfo`로 제어됩니다(기본값: Graph 자격 증명을 사용할 수 있을 때 활성화).

## 기록 컨텍스트

- `channels.msteams.historyLimit`은 프롬프트에 포함할 최근 채널/그룹 메시지 수를 제어합니다.
- `messages.groupChat.historyLimit`로 대체됩니다. `0`으로 설정하면 비활성화됩니다(기본값 50).
- 가져온 스레드 기록은 발신자 허용 목록(`allowFrom` / `groupAllowFrom`)으로 필터링되므로 스레드 컨텍스트 시드는 허용된 발신자의 메시지만 포함합니다.
- 인용된 첨부파일 컨텍스트(`ReplyTo*`에서 파생된 Teams reply HTML)는 현재 수신된 그대로 전달됩니다.
- 즉, 허용 목록은 누가 에이전트를 트리거할 수 있는지를 제어하며, 현재는 특정 보조 컨텍스트 경로만 필터링됩니다.
- DM 기록은 `channels.msteams.dmHistoryLimit`(사용자 턴 수)로 제한할 수 있습니다. 사용자별 재정의: `channels.msteams.dms["<user_id>"].historyLimit`.

## 현재 Teams RSC 권한(Manifest)

다음은 Teams 앱 manifest의 **기존 resourceSpecific 권한**입니다. 이는 앱이 설치된 팀/채팅 내부에서만 적용됩니다.

**채널(팀 범위)의 경우:**

- `ChannelMessage.Read.Group` (Application) - @멘션 없이 모든 채널 메시지 수신
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**그룹 채팅의 경우:**

- `ChatMessage.Read.Chat` (Application) - @멘션 없이 모든 그룹 채팅 메시지 수신

## 예시 Teams Manifest(일부 가림)

필수 필드를 포함한 최소한의 유효한 예시입니다. ID와 URL을 바꿔 사용하세요.

```json5
{
  $schema: "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  manifestVersion: "1.23",
  version: "1.0.0",
  id: "00000000-0000-0000-0000-000000000000",
  name: { short: "OpenClaw" },
  developer: {
    name: "Your Org",
    websiteUrl: "https://example.com",
    privacyUrl: "https://example.com/privacy",
    termsOfUseUrl: "https://example.com/terms",
  },
  description: { short: "OpenClaw in Teams", full: "OpenClaw in Teams" },
  icons: { outline: "outline.png", color: "color.png" },
  accentColor: "#5B6DEF",
  bots: [
    {
      botId: "11111111-1111-1111-1111-111111111111",
      scopes: ["personal", "team", "groupChat"],
      isNotificationOnly: false,
      supportsCalling: false,
      supportsVideo: false,
      supportsFiles: true,
    },
  ],
  webApplicationInfo: {
    id: "11111111-1111-1111-1111-111111111111",
  },
  authorization: {
    permissions: {
      resourceSpecific: [
        { name: "ChannelMessage.Read.Group", type: "Application" },
        { name: "ChannelMessage.Send.Group", type: "Application" },
        { name: "Member.Read.Group", type: "Application" },
        { name: "Owner.Read.Group", type: "Application" },
        { name: "ChannelSettings.Read.Group", type: "Application" },
        { name: "TeamMember.Read.Group", type: "Application" },
        { name: "TeamSettings.Read.Group", type: "Application" },
        { name: "ChatMessage.Read.Chat", type: "Application" },
      ],
    },
  },
}
```

### Manifest 주의 사항(필수 필드)

- `bots[].botId`는 Azure Bot App ID와 **반드시** 일치해야 합니다.
- `webApplicationInfo.id`는 Azure Bot App ID와 **반드시** 일치해야 합니다.
- `bots[].scopes`에는 사용할 표면(`personal`, `team`, `groupChat`)이 포함되어야 합니다.
- `bots[].supportsFiles: true`는 개인 범위 파일 처리에 필요합니다.
- 채널 트래픽을 원한다면 `authorization.permissions.resourceSpecific`에 채널 읽기/보내기가 포함되어야 합니다.

### 기존 앱 업데이트

이미 설치된 Teams 앱을 업데이트하려면(예: RSC 권한 추가):

1. 새 설정으로 `manifest.json`을 업데이트합니다
2. **`version` 필드를 증가**시킵니다(예: `1.0.0` → `1.1.0`)
3. 아이콘과 함께 manifest를 **다시 zip으로 묶습니다**(`manifest.json`, `outline.png`, `color.png`)
4. 새 zip을 업로드합니다.
   - **옵션 A (Teams Admin Center):** Teams Admin Center → Teams apps → Manage apps → 앱 찾기 → Upload new version
   - **옵션 B (Sideload):** Teams → Apps → Manage your apps → Upload a custom app
5. **팀 채널의 경우:** 새 권한이 적용되도록 각 팀에 앱을 다시 설치합니다
6. 캐시된 앱 메타데이터를 지우기 위해 Teams를 **완전히 종료 후 다시 실행**합니다(창만 닫지 말 것)

## 기능: RSC 전용 vs Graph

### **Teams RSC만 사용**하는 경우(앱 설치됨, Graph API 권한 없음)

작동함:

- 채널 메시지 **텍스트** 콘텐츠 읽기.
- 채널 메시지 **텍스트** 콘텐츠 보내기.
- **개인(DM)** 파일 첨부 수신.

작동하지 않음:

- 채널/그룹 **이미지 또는 파일 콘텐츠**(payload에는 HTML stub만 포함됨).
- SharePoint/OneDrive에 저장된 첨부파일 다운로드.
- 메시지 기록 읽기(실시간 웹훅 이벤트 범위 초과).

### **Teams RSC + Microsoft Graph Application 권한** 사용 시

추가됨:

- 호스팅된 콘텐츠 다운로드(메시지에 붙여넣은 이미지).
- SharePoint/OneDrive에 저장된 파일 첨부 다운로드.
- Graph를 통한 채널/채팅 메시지 기록 읽기.

### RSC vs Graph API

| Capability              | RSC Permissions      | Graph API                           |
| ----------------------- | -------------------- | ----------------------------------- |
| **실시간 메시지**  | 예(웹훅을 통해)    | 아니요(폴링만 가능)                   |
| **과거 메시지** | 아니요                   | 예(기록 조회 가능)             |
| **설정 복잡도**    | 앱 manifest만 필요    | 관리자 동의 + 토큰 흐름 필요 |
| **오프라인 동작**       | 아니요(실행 중이어야 함) | 예(언제든 조회 가능)                 |

**요약:** RSC는 실시간 수신용이고, Graph API는 과거 기록 접근용입니다. 오프라인 동안 놓친 메시지를 따라잡으려면 Graph API와 `ChannelMessage.Read.All`이 필요합니다(관리자 동의 필요).

## Graph 기반 미디어 + 기록(채널에 필요)

**채널**에서 이미지/파일이 필요하거나 **메시지 기록**을 가져오려면 Microsoft Graph 권한을 활성화하고 관리자 동의를 받아야 합니다.

1. Entra ID (Azure AD) **App Registration**에서 Microsoft Graph **Application permissions**를 추가합니다.
   - `ChannelMessage.Read.All` (채널 첨부파일 + 기록)
   - `Chat.Read.All` 또는 `ChatMessage.Read.All` (그룹 채팅)
2. 테넌트에 대해 **관리자 동의**를 부여합니다.
3. Teams 앱 **manifest 버전**을 올리고, 다시 업로드한 뒤, **Teams에 앱을 재설치**합니다.
4. 캐시된 앱 메타데이터를 지우기 위해 Teams를 **완전히 종료 후 다시 실행**합니다.

**사용자 멘션을 위한 추가 권한:** 사용자 @멘션은 대화에 있는 사용자에 대해서는 기본적으로 작동합니다. 하지만 현재 대화에 **없는** 사용자를 동적으로 검색하고 멘션하려면 `User.Read.All` (Application) 권한을 추가하고 관리자 동의를 부여하세요.

## 알려진 제한 사항

### 웹훅 시간 초과

Teams는 HTTP 웹훅을 통해 메시지를 전달합니다. 처리가 너무 오래 걸리면(예: 느린 LLM 응답) 다음이 발생할 수 있습니다.

- 게이트웨이 시간 초과
- Teams가 메시지를 재시도함(중복 발생)
- 응답 누락

OpenClaw는 빠르게 응답을 반환하고 적극적으로 답장을 보내 이 문제를 처리하지만, 응답이 매우 느리면 여전히 문제가 발생할 수 있습니다.

### 서식

Teams 마크다운은 Slack이나 Discord보다 제한적입니다.

- 기본 서식은 작동합니다: **굵게**, _기울임_, `code`, 링크
- 복잡한 마크다운(표, 중첩 목록)은 올바르게 렌더링되지 않을 수 있습니다
- Polls 및 임의 카드 전송에는 Adaptive Cards가 지원됩니다(아래 참조)

## 구성

주요 설정(공유 채널 패턴은 `/gateway/configuration` 참조):

- `channels.msteams.enabled`: 채널 활성화/비활성화.
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: 봇 자격 증명.
- `channels.msteams.webhook.port` (기본값 `3978`)
- `channels.msteams.webhook.path` (기본값 `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (기본값: pairing)
- `channels.msteams.allowFrom`: DM 허용 목록(AAD object ID 권장). Graph 액세스를 사용할 수 있을 때 마법사가 설정 중 이름을 ID로 확인합니다.
- `channels.msteams.dangerouslyAllowNameMatching`: 변경 가능한 UPN/표시 이름 일치 및 직접 팀/채널 이름 라우팅을 다시 활성화하는 비상 토글.
- `channels.msteams.textChunkLimit`: 아웃바운드 텍스트 청크 크기.
- `channels.msteams.chunkMode`: `length`(기본값) 또는 `newline`으로, 길이 기준 청킹 전에 빈 줄(문단 경계)에서 분할합니다.
- `channels.msteams.mediaAllowHosts`: 인바운드 첨부파일 호스트 허용 목록(기본값은 Microsoft/Teams 도메인).
- `channels.msteams.mediaAuthAllowHosts`: 미디어 재시도 시 Authorization 헤더를 붙일 호스트 허용 목록(기본값은 Graph + Bot Framework 호스트).
- `channels.msteams.requireMention`: 채널/그룹에서 @멘션 필요 여부(기본값 true).
- `channels.msteams.replyStyle`: `thread | top-level`([응답 스타일](#reply-style-threads-vs-posts) 참조).
- `channels.msteams.teams.<teamId>.replyStyle`: 팀별 재정의.
- `channels.msteams.teams.<teamId>.requireMention`: 팀별 재정의.
- `channels.msteams.teams.<teamId>.tools`: 채널 재정의가 없을 때 사용하는 기본 팀별 도구 정책 재정의(`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.toolsBySender`: 기본 팀별 발신자별 도구 정책 재정의(`"*"` 와일드카드 지원).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: 채널별 재정의.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: 채널별 재정의.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: 채널별 도구 정책 재정의(`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: 채널별 발신자별 도구 정책 재정의(`"*"` 와일드카드 지원).
- `toolsBySender` 키는 명시적 접두사를 사용해야 합니다.
  `id:`, `e164:`, `username:`, `name:` (기존의 접두사 없는 키는 여전히 `id:`로만 매핑됨).
- `channels.msteams.actions.memberInfo`: Graph 기반 멤버 정보 작업 활성화/비활성화(기본값: Graph 자격 증명을 사용할 수 있으면 활성화).
- `channels.msteams.sharePointSiteId`: 그룹 채팅/채널의 파일 업로드용 SharePoint site ID([그룹 채팅에서 파일 보내기](#sending-files-in-group-chats) 참조).

## 라우팅 및 세션

- 세션 키는 표준 에이전트 형식을 따릅니다([/concepts/session](/concepts/session) 참조).
  - 다이렉트 메시지는 기본 세션을 공유합니다(`agent:<agentId>:<mainKey>`).
  - 채널/그룹 메시지는 conversation id를 사용합니다.
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## 응답 스타일: 스레드 vs 게시물

Teams는 최근 동일한 기본 데이터 모델 위에서 두 가지 채널 UI 스타일을 도입했습니다.

| Style                    | Description                                               | 권장 `replyStyle` |
| ------------------------ | --------------------------------------------------------- | ------------------------ |
| **Posts** (클래식)      | 메시지가 카드로 표시되고 그 아래에 스레드 응답이 달림 | `thread` (기본값)       |
| **Threads** (Slack 유사) | 메시지가 더 Slack처럼 선형으로 흐름                   | `top-level`              |

**문제:** Teams API는 채널이 어떤 UI 스타일을 사용하는지 노출하지 않습니다. 잘못된 `replyStyle`을 사용하면 다음과 같습니다.

- Threads 스타일 채널에서 `thread` 사용 → 응답이 어색하게 중첩되어 표시됨
- Posts 스타일 채널에서 `top-level` 사용 → 응답이 스레드 내부가 아니라 별도 최상위 게시물로 표시됨

**해결책:** 채널이 어떻게 설정되어 있는지에 따라 채널별로 `replyStyle`을 구성하세요.

```json5
{
  channels: {
    msteams: {
      replyStyle: "thread",
      teams: {
        "19:abc...@thread.tacv2": {
          channels: {
            "19:xyz...@thread.tacv2": {
              replyStyle: "top-level",
            },
          },
        },
      },
    },
  },
}
```

## 첨부파일 및 이미지

**현재 제한 사항:**

- **DM:** Teams 봇 파일 API를 통해 이미지와 파일 첨부가 동작합니다.
- **채널/그룹:** 첨부파일은 M365 스토리지(SharePoint/OneDrive)에 저장됩니다. 웹훅 payload에는 실제 파일 바이트가 아닌 HTML stub만 포함됩니다. 채널 첨부파일을 다운로드하려면 **Graph API 권한이 필요합니다**.
- 명시적 파일 우선 전송에는 `media` / `filePath` / `path`와 함께 `action=upload-file`을 사용하세요. 선택적 `message`는 함께 전송되는 텍스트/주석이 되며, `filename`은 업로드 이름을 재정의합니다.

Graph 권한이 없으면 이미지가 포함된 채널 메시지는 텍스트 전용으로 수신됩니다(이미지 콘텐츠에는 봇이 접근할 수 없음).
기본적으로 OpenClaw는 Microsoft/Teams 호스트명에서만 미디어를 다운로드합니다. `channels.msteams.mediaAllowHosts`로 재정의하세요(모든 호스트를 허용하려면 `["*"]` 사용).
Authorization 헤더는 `channels.msteams.mediaAuthAllowHosts`에 포함된 호스트에만 첨부됩니다(기본값은 Graph + Bot Framework 호스트). 이 목록은 엄격하게 유지하세요(멀티 테넌트 접미사는 피함).

## 그룹 채팅에서 파일 보내기

봇은 DM에서 FileConsentCard 흐름(기본 제공)을 사용해 파일을 보낼 수 있습니다. 그러나 **그룹 채팅/채널에서 파일 보내기**에는 추가 설정이 필요합니다.

| Context                  | 파일 전송 방식                           | 필요한 설정                                    |
| ------------------------ | -------------------------------------------- | ----------------------------------------------- |
| **DM**                  | FileConsentCard → 사용자가 수락 → 봇이 업로드 | 기본적으로 동작                            |
| **그룹 채팅/채널** | SharePoint에 업로드 → 링크 공유            | `sharePointSiteId` + Graph 권한 필요 |
| **이미지(모든 컨텍스트)** | Base64 인라인 인코딩                        | 기본적으로 동작                            |

### 그룹 채팅에 SharePoint가 필요한 이유

봇에는 개인 OneDrive 드라이브가 없습니다(`/me/drive` Graph API 엔드포인트는 애플리케이션 ID에서 동작하지 않음). 그룹 채팅/채널로 파일을 보내려면 봇이 **SharePoint 사이트**에 업로드하고 공유 링크를 생성해야 합니다.

### 설정

1. Entra ID (Azure AD) → App Registration에서 **Graph API 권한**을 추가합니다.
   - `Sites.ReadWrite.All` (Application) - SharePoint에 파일 업로드
   - `Chat.Read.All` (Application) - 선택 사항, 사용자별 공유 링크 활성화

2. 테넌트에 대해 **관리자 동의**를 부여합니다.

3. **SharePoint site ID 가져오기:**

   ```bash
   # Graph Explorer 또는 유효한 토큰이 포함된 curl 사용:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # 예: "contoso.sharepoint.com/sites/BotFiles" 사이트의 경우
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # 응답에 포함됨: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **OpenClaw 구성:**

   ```json5
   {
     channels: {
       msteams: {
         // ... other config ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### 공유 동작

| Permission                              | 공유 동작                                          |
| --------------------------------------- | --------------------------------------------------------- |
| `Sites.ReadWrite.All`만              | 조직 전체 공유 링크(조직 내 누구나 접근 가능) |
| `Sites.ReadWrite.All` + `Chat.Read.All` | 사용자별 공유 링크(채팅 멤버만 접근 가능)      |

사용자별 공유는 채팅 참여자만 파일에 접근할 수 있으므로 더 안전합니다. `Chat.Read.All` 권한이 없으면 봇은 조직 전체 공유로 대체합니다.

### 대체 동작

| Scenario                                          | 결과                                             |
| ------------------------------------------------- | -------------------------------------------------- |
| 그룹 채팅 + 파일 + `sharePointSiteId` 구성됨 | SharePoint에 업로드, 공유 링크 전송            |
| 그룹 채팅 + 파일 + `sharePointSiteId` 없음         | OneDrive 업로드 시도(실패 가능), 텍스트만 전송 |
| 개인 채팅 + 파일                              | FileConsentCard 흐름(SharePoint 없이 동작)    |
| 모든 컨텍스트 + 이미지                               | Base64 인라인 인코딩(SharePoint 없이 동작)   |

### 파일 저장 위치

업로드된 파일은 구성된 SharePoint 사이트의 기본 문서 라이브러리 내 `/OpenClawShared/` 폴더에 저장됩니다.

## Polls (Adaptive Cards)

OpenClaw는 Teams Polls를 Adaptive Cards로 보냅니다(Teams에는 기본 Poll API가 없음).

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- 투표는 게이트웨이가 `~/.openclaw/msteams-polls.json`에 기록합니다.
- 투표 기록을 위해 게이트웨이는 계속 온라인 상태여야 합니다.
- Polls는 아직 결과 요약을 자동 게시하지 않습니다(필요하면 저장 파일을 확인하세요).

## Adaptive Cards(임의)

`message` 도구 또는 CLI를 사용해 임의의 Adaptive Card JSON을 Teams 사용자나 대화에 보낼 수 있습니다.

`card` 매개변수는 Adaptive Card JSON 객체를 받습니다. `card`가 제공되면 메시지 텍스트는 선택 사항입니다.

**에이전트 도구:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:<id>",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello!" }],
  },
}
```

**CLI:**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

카드 스키마와 예시는 [Adaptive Cards documentation](https://adaptivecards.io/)을 참조하세요. 대상 형식 세부 정보는 아래 [대상 형식](#target-formats)을 참조하세요.

## 대상 형식

MSTeams 대상은 사용자와 대화를 구분하기 위해 접두사를 사용합니다.

| Target type         | Format                           | Example                                             |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| 사용자(ID 기준)        | `user:<aad-object-id>`           | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| 사용자(이름 기준)      | `user:<display-name>`            | `user:John Smith` (Graph API 필요)              |
| 그룹/채널       | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |
| 그룹/채널(raw) | `<conversation-id>`              | `19:abc123...@thread.tacv2` (`@thread`가 포함된 경우) |

**CLI 예시:**

```bash
# ID로 사용자에게 전송
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# 표시 이름으로 사용자에게 전송(Graph API 조회 트리거)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# 그룹 채팅 또는 채널로 전송
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# 대화에 Adaptive Card 전송
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**에이전트 도구 예시:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:John Smith",
  message: "Hello!",
}
```

```json5
{
  action: "send",
  channel: "msteams",
  target: "conversation:19:abc...@thread.tacv2",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello" }],
  },
}
```

참고: `user:` 접두사가 없으면 이름은 기본적으로 그룹/팀 확인으로 처리됩니다. 표시 이름으로 사람을 지정할 때는 항상 `user:`를 사용하세요.

## Proactive messaging

- Proactive 메시지는 사용자가 상호작용한 **이후에만** 가능합니다. 그 시점에 대화 참조를 저장하기 때문입니다.
- `dmPolicy`와 허용 목록 게이팅은 `/gateway/configuration`을 참조하세요.

## 팀 및 채널 ID(흔한 함정)

Teams URL의 `groupId` 쿼리 매개변수는 구성에 사용하는 팀 ID가 **아닙니다**. 대신 URL 경로에서 ID를 추출하세요.

**팀 URL:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    팀 ID(URL 디코딩 필요)
```

**채널 URL:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      채널 ID(URL 디코딩 필요)
```

**config용:**

- 팀 ID = `/team/` 뒤의 경로 세그먼트(URL 디코딩됨, 예: `19:Bk4j...@thread.tacv2`)
- 채널 ID = `/channel/` 뒤의 경로 세그먼트(URL 디코딩됨)
- `groupId` 쿼리 매개변수는 **무시**하세요

## 비공개 채널

봇은 비공개 채널에서 제한적으로 지원됩니다.

| Feature                      | Standard Channels | Private Channels       |
| ---------------------------- | ----------------- | ---------------------- |
| 봇 설치             | 예               | 제한적                |
| 실시간 메시지(웹훅) | 예               | 동작하지 않을 수 있음           |
| RSC 권한              | 예               | 다르게 동작할 수 있음 |
| @mentions                    | 예               | 봇에 접근 가능할 경우   |
| Graph API 기록            | 예               | 예(권한 필요) |

**비공개 채널이 동작하지 않을 때의 우회 방법:**

1. 봇 상호작용에는 표준 채널 사용
2. DM 사용 - 사용자는 항상 봇에 직접 메시지를 보낼 수 있음
3. 과거 접근에는 Graph API 사용(`ChannelMessage.Read.All` 필요)

## 문제 해결

### 일반적인 문제

- **채널에 이미지가 표시되지 않음:** Graph 권한 또는 관리자 동의가 누락되었습니다. Teams 앱을 재설치하고 Teams를 완전히 종료 후 다시 여세요.
- **채널에서 응답 없음:** 기본적으로 멘션이 필요합니다. `channels.msteams.requireMention=false`를 설정하거나 팀/채널별로 구성하세요.
- **버전 불일치(Teams에 이전 manifest가 계속 표시됨):** 앱을 제거 후 다시 추가하고 Teams를 완전히 종료해 새로고침하세요.
- **웹훅에서 401 Unauthorized:** Azure JWT 없이 수동 테스트할 때는 정상입니다. 엔드포인트에 도달했지만 인증에 실패했다는 뜻입니다. 올바른 테스트에는 Azure Web Chat을 사용하세요.

### Manifest 업로드 오류

- **"Icon file cannot be empty":** manifest가 참조하는 아이콘 파일이 0바이트입니다. 유효한 PNG 아이콘을 만드세요(`outline.png`는 32x32, `color.png`는 192x192).
- **"webApplicationInfo.Id already in use":** 앱이 다른 팀/채팅에 아직 설치되어 있습니다. 먼저 찾아 제거하거나 전파를 위해 5~10분 기다리세요.
- **업로드 시 "Something went wrong":** 대신 [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com)을 통해 업로드하고, 브라우저 DevTools(F12) → Network 탭에서 실제 응답 본문 오류를 확인하세요.
- **사이드로드 실패:** "Upload a custom app" 대신 "Upload an app to your org's app catalog"를 시도하세요. 이 방식이 사이드로드 제한을 우회하는 경우가 많습니다.

### RSC 권한이 작동하지 않음

1. `webApplicationInfo.id`가 봇의 App ID와 정확히 일치하는지 확인하세요
2. 앱을 다시 업로드하고 팀/채팅에 재설치하세요
3. 조직 관리자가 RSC 권한을 차단했는지 확인하세요
4. 올바른 범위를 사용 중인지 확인하세요: 팀에는 `ChannelMessage.Read.Group`, 그룹 채팅에는 `ChatMessage.Read.Chat`

## 참고 자료

- [Create Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - Azure Bot 설정 가이드
- [Teams Developer Portal](https://dev.teams.microsoft.com/apps) - Teams 앱 생성/관리
- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Receive channel messages with RSC](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC permissions reference](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams bot file handling](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (채널/그룹에는 Graph 필요)
- [Proactive messaging](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)

## 관련

- [Channels Overview](/channels) — 지원되는 모든 채널
- [Pairing](/channels/pairing) — DM 인증 및 pairing 흐름
- [Groups](/channels/groups) — 그룹 채팅 동작 및 멘션 게이팅
- [Channel Routing](/channels/channel-routing) — 메시지 세션 라우팅
- [Security](/gateway/security) — 액세스 모델 및 보안 강화
