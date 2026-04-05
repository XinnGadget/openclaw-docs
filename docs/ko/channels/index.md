---
read_when:
    - OpenClaw용 채팅 채널을 선택하려는 경우
    - 지원되는 메시징 플랫폼의 빠른 개요가 필요한 경우
summary: OpenClaw가 연결할 수 있는 메시징 플랫폼
title: 채팅 채널
x-i18n:
    generated_at: "2026-04-05T12:35:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: 246ee6f16aebe751241f00102bb435978ed21f6158385aff5d8e222e30567416
    source_path: channels/index.md
    workflow: 15
---

# 채팅 채널

OpenClaw는 이미 사용 중인 어떤 채팅 앱에서든 사용자와 대화할 수 있습니다. 각 채널은 Gateway를 통해 연결됩니다.
텍스트는 모든 곳에서 지원되며, 미디어와 반응 지원은 채널마다 다릅니다.

## 지원되는 채널

- [BlueBubbles](/channels/bluebubbles) — **iMessage에 권장**; 전체 기능 지원이 포함된 BlueBubbles macOS 서버 REST API를 사용합니다(번들 plugin; 수정, 전송 취소, 효과, 반응, 그룹 관리 — 수정은 현재 macOS 26 Tahoe에서 작동하지 않음).
- [Discord](/channels/discord) — Discord Bot API + Gateway; 서버, 채널, DM을 지원합니다.
- [Feishu](/channels/feishu) — WebSocket을 통한 Feishu/Lark 봇(번들 plugin).
- [Google Chat](/channels/googlechat) — HTTP 웹훅을 통한 Google Chat API 앱.
- [iMessage (legacy)](/channels/imessage) — imsg CLI를 통한 레거시 macOS 통합(지원 중단 예정, 새 설정에는 BlueBubbles 사용).
- [IRC](/channels/irc) — 전통적인 IRC 서버; 페어링/허용 목록 제어가 포함된 채널 + DM.
- [LINE](/channels/line) — LINE Messaging API 봇(번들 plugin).
- [Matrix](/channels/matrix) — Matrix 프로토콜(번들 plugin).
- [Mattermost](/channels/mattermost) — Bot API + WebSocket; 채널, 그룹, DM(번들 plugin).
- [Microsoft Teams](/channels/msteams) — Bot Framework; 엔터프라이즈 지원(번들 plugin).
- [Nextcloud Talk](/channels/nextcloud-talk) — Nextcloud Talk를 통한 셀프 호스팅 채팅(번들 plugin).
- [Nostr](/channels/nostr) — NIP-04를 통한 분산형 DM(번들 plugin).
- [QQ Bot](/channels/qqbot) — QQ Bot API; 개인 채팅, 그룹 채팅, 리치 미디어(번들 plugin).
- [Signal](/channels/signal) — signal-cli; 개인정보 보호 중심.
- [Slack](/channels/slack) — Bolt SDK; 워크스페이스 앱.
- [Synology Chat](/channels/synology-chat) — 송신+수신 웹훅을 통한 Synology NAS Chat(번들 plugin).
- [Telegram](/channels/telegram) — grammY를 통한 Bot API; 그룹을 지원합니다.
- [Tlon](/channels/tlon) — Urbit 기반 메신저(번들 plugin).
- [Twitch](/channels/twitch) — IRC 연결을 통한 Twitch 채팅(번들 plugin).
- [Voice Call](/plugins/voice-call) — Plivo 또는 Twilio를 통한 전화 통신(plugin, 별도 설치).
- [WebChat](/web/webchat) — WebSocket을 통한 Gateway WebChat UI.
- [WeChat](https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin) — QR 로그인을 통한 Tencent iLink Bot plugin; 개인 채팅만 지원.
- [WhatsApp](/channels/whatsapp) — 가장 대중적임; Baileys를 사용하며 QR 페어링이 필요합니다.
- [Zalo](/channels/zalo) — Zalo Bot API; 베트남에서 인기 있는 메신저(번들 plugin).
- [Zalo Personal](/channels/zalouser) — QR 로그인을 통한 Zalo 개인 계정(번들 plugin).

## 참고

- 채널은 동시에 실행할 수 있습니다. 여러 개를 구성하면 OpenClaw가 채팅별로 라우팅합니다.
- 가장 빠른 설정은 보통 **Telegram**입니다(간단한 봇 토큰). WhatsApp는 QR 페어링이 필요하며 디스크에 더 많은 상태를 저장합니다.
- 그룹 동작은 채널마다 다릅니다. [Groups](/channels/groups)를 참조하세요.
- 안전을 위해 DM 페어링과 허용 목록이 강제 적용됩니다. [Security](/gateway/security)를 참조하세요.
- 문제 해결: [Channel troubleshooting](/channels/troubleshooting).
- 모델 provider는 별도로 문서화되어 있습니다. [Model Providers](/providers/models)를 참조하세요.
