---
read_when:
    - 처음 접하는 사용자에게 OpenClaw 소개하기
summary: OpenClaw는 모든 OS에서 실행되는 AI 에이전트를 위한 멀티채널 게이트웨이입니다.
title: OpenClaw
x-i18n:
    generated_at: "2026-04-05T10:48:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9c29a8d9fc41a94b650c524bb990106f134345560e6d615dac30e8815afff481
    source_path: index.md
    workflow: 15
---

# OpenClaw 🦞

<p align="center">
    <img
        src="/assets/openclaw-logo-text-dark.png"
        alt="OpenClaw"
        width="500"
        class="dark:hidden"
    />
    <img
        src="/assets/openclaw-logo-text.png"
        alt="OpenClaw"
        width="500"
        class="hidden dark:block"
    />
</p>

> _"EXFOLIATE! EXFOLIATE!"_ — 아마도 우주 바닷가재

<p align="center">
  <strong>Discord, Google Chat, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo 등 전반에서 AI 에이전트를 연결하는 모든 OS용 게이트웨이.</strong><br />
  메시지를 보내면 주머니 속에서 에이전트 응답을 받을 수 있습니다. 내장 채널, 번들 채널 plugins, WebChat, 모바일 노드 전반에서 하나의 Gateway를 실행하세요.
</p>

<Columns>
  <Card title="시작하기" href="/start/getting-started" icon="rocket">
    OpenClaw를 설치하고 몇 분 안에 Gateway를 실행하세요.
  </Card>
  <Card title="온보딩 실행" href="/start/wizard" icon="sparkles">
    `openclaw onboard` 및 페어링 흐름을 포함한 안내형 설정입니다.
  </Card>
  <Card title="Control UI 열기" href="/web/control-ui" icon="layout-dashboard">
    채팅, 구성, 세션을 위한 브라우저 대시보드를 실행하세요.
  </Card>
</Columns>

## OpenClaw란 무엇인가요?

OpenClaw는 **셀프 호스팅 게이트웨이**로, 즐겨 사용하는 채팅 앱과 채널 표면을 — 내장 채널과 Discord, Google Chat, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo 등을 포함한 번들 또는 외부 채널 plugins까지 — Pi와 같은 AI 코딩 에이전트에 연결합니다. 사용자의 머신(또는 서버)에서 단일 Gateway 프로세스를 실행하면, 이것이 메시징 앱과 항상 사용 가능한 AI 어시스턴트 사이의 브리지 역할을 합니다.

**누구를 위한 제품인가요?** 데이터를 계속 통제하고 호스팅 서비스에 의존하지 않으면서, 어디서나 메시지를 보낼 수 있는 개인 AI 어시스턴트를 원하는 개발자와 파워 유저를 위한 제품입니다.

**무엇이 다른가요?**

- **셀프 호스팅**: 내 하드웨어에서, 내 규칙대로 실행
- **멀티채널**: 하나의 Gateway가 내장 채널과 번들 또는 외부 채널 plugins를 동시에 제공
- **에이전트 네이티브**: 도구 사용, 세션, 메모리, 멀티 에이전트 라우팅을 갖춘 코딩 에이전트를 위해 설계
- **오픈 소스**: MIT 라이선스, 커뮤니티 중심

**무엇이 필요한가요?** Node 24(권장) 또는 호환성을 위한 Node 22 LTS (`22.14+`), 선택한 제공자의 API 키, 그리고 5분이면 됩니다. 최상의 품질과 보안을 위해 가장 강력한 최신 세대 모델을 사용하세요.

## 작동 방식

```mermaid
flowchart LR
  A["채팅 앱 + plugins"] --> B["Gateway"]
  B --> C["Pi agent"]
  B --> D["CLI"]
  B --> E["웹 Control UI"]
  B --> F["macOS 앱"]
  B --> G["iOS 및 Android 노드"]
```

Gateway는 세션, 라우팅, 채널 연결을 위한 단일 진실 공급원입니다.

## 주요 기능

<Columns>
  <Card title="멀티채널 게이트웨이" icon="network">
    단일 Gateway 프로세스로 Discord, iMessage, Signal, Slack, Telegram, WhatsApp, WebChat 등을 사용할 수 있습니다.
  </Card>
  <Card title="Plugin 채널" icon="plug">
    번들 plugins는 일반적인 현재 릴리스에서 Matrix, Nostr, Twitch, Zalo 등을 추가합니다.
  </Card>
  <Card title="멀티 에이전트 라우팅" icon="route">
    에이전트, 워크스페이스 또는 발신자별로 격리된 세션을 제공합니다.
  </Card>
  <Card title="미디어 지원" icon="image">
    이미지, 오디오, 문서를 보내고 받을 수 있습니다.
  </Card>
  <Card title="웹 Control UI" icon="monitor">
    채팅, 구성, 세션, 노드를 위한 브라우저 대시보드입니다.
  </Card>
  <Card title="모바일 노드" icon="smartphone">
    Canvas, 카메라, 음성 지원 워크플로를 위해 iOS 및 Android 노드를 페어링합니다.
  </Card>
</Columns>

## 빠른 시작

<Steps>
  <Step title="OpenClaw 설치">
    ```bash
    npm install -g openclaw@latest
    ```
  </Step>
  <Step title="온보딩 및 서비스 설치">
    ```bash
    openclaw onboard --install-daemon
    ```
  </Step>
  <Step title="채팅">
    브라우저에서 Control UI를 열고 메시지를 보내세요:

    ```bash
    openclaw dashboard
    ```

    또는 채널을 연결하고([Telegram](/channels/telegram)이 가장 빠릅니다) 휴대폰에서 채팅하세요.

  </Step>
</Steps>

전체 설치 및 개발 설정이 필요하신가요? [시작하기](/start/getting-started)를 참조하세요.

## 대시보드

Gateway가 시작된 후 브라우저 Control UI를 여세요.

- 로컬 기본값: [http://127.0.0.1:18789/](http://127.0.0.1:18789/)
- 원격 액세스: [웹 표면](/web) 및 [Tailscale](/gateway/tailscale)

<p align="center">
  <img src="/whatsapp-openclaw.jpg" alt="OpenClaw" width="420" />
</p>

## 구성(선택 사항)

구성은 `~/.openclaw/openclaw.json`에 있습니다.

- **아무것도 하지 않으면**, OpenClaw는 발신자별 세션과 함께 RPC 모드의 번들 Pi 바이너리를 사용합니다.
- 더 엄격하게 제한하려면 `channels.whatsapp.allowFrom` 및 (그룹의 경우) 멘션 규칙부터 시작하세요.

예시:

```json5
{
  channels: {
    whatsapp: {
      allowFrom: ["+15555550123"],
      groups: { "*": { requireMention: true } },
    },
  },
  messages: { groupChat: { mentionPatterns: ["@openclaw"] } },
}
```

## 여기서 시작하세요

<Columns>
  <Card title="문서 허브" href="/start/hubs" icon="book-open">
    사용 사례별로 정리된 모든 문서와 가이드입니다.
  </Card>
  <Card title="구성" href="/gateway/configuration" icon="settings">
    핵심 Gateway 설정, 토큰, 제공자 구성입니다.
  </Card>
  <Card title="원격 액세스" href="/gateway/remote" icon="globe">
    SSH 및 tailnet 액세스 패턴입니다.
  </Card>
  <Card title="채널" href="/channels/telegram" icon="message-square">
    Feishu, Microsoft Teams, WhatsApp, Telegram, Discord 등의 채널별 설정입니다.
  </Card>
  <Card title="노드" href="/nodes" icon="smartphone">
    페어링, Canvas, 카메라, 디바이스 작업을 지원하는 iOS 및 Android 노드입니다.
  </Card>
  <Card title="도움말" href="/help" icon="life-buoy">
    일반적인 수정 사항과 문제 해결 시작점입니다.
  </Card>
</Columns>

## 더 알아보기

<Columns>
  <Card title="전체 기능 목록" href="/concepts/features" icon="list">
    완전한 채널, 라우팅, 미디어 기능입니다.
  </Card>
  <Card title="멀티 에이전트 라우팅" href="/concepts/multi-agent" icon="route">
    워크스페이스 격리 및 에이전트별 세션입니다.
  </Card>
  <Card title="보안" href="/gateway/security" icon="shield">
    토큰, 허용 목록, 안전 제어입니다.
  </Card>
  <Card title="문제 해결" href="/gateway/troubleshooting" icon="wrench">
    Gateway 진단 및 일반적인 오류입니다.
  </Card>
  <Card title="소개 및 크레딧" href="/reference/credits" icon="info">
    프로젝트의 기원, 기여자, 라이선스입니다.
  </Card>
</Columns>
