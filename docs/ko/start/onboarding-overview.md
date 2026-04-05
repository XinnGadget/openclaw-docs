---
read_when:
    - 온보딩 경로를 선택하는 경우
    - 새 환경을 설정하는 경우
sidebarTitle: Onboarding Overview
summary: OpenClaw 온보딩 옵션과 흐름 개요
title: 온보딩 개요
x-i18n:
    generated_at: "2026-04-05T12:55:17Z"
    model: gpt-5.4
    provider: openai
    source_hash: 374697c1dbe0c3871c43164076fbed7119ef032f4a40d0f6e421051f914806e5
    source_path: start/onboarding-overview.md
    workflow: 15
---

# 온보딩 개요

OpenClaw에는 두 가지 온보딩 경로가 있습니다. 둘 다 인증, Gateway, 그리고
선택적 채팅 채널을 구성하지만, 설정과 상호작용하는 방식만 다릅니다.

## 어떤 경로를 사용해야 하나요?

|                | CLI 온보딩                              | macOS 앱 온보딩           |
| -------------- | --------------------------------------- | ------------------------- |
| **플랫폼**     | macOS, Linux, Windows (네이티브 또는 WSL2) | macOS 전용              |
| **인터페이스** | 터미널 마법사                           | 앱 내 안내형 UI           |
| **적합한 용도**| 서버, 헤드리스, 전체 제어               | 데스크톱 Mac, 시각적 설정 |
| **자동화**     | 스크립트용 `--non-interactive` 지원     | 수동만 가능               |
| **명령어**     | `openclaw onboard`                      | 앱 실행                   |

대부분의 사용자는 **CLI 온보딩**으로 시작하는 것이 좋습니다. 어디서나 작동하며
가장 많은 제어권을 제공합니다.

## 온보딩이 구성하는 항목

어느 경로를 선택하든 온보딩은 다음을 설정합니다.

1. **모델 provider 및 인증** — 선택한 provider를 위한 API 키, OAuth 또는 설정 토큰
2. **워크스페이스** — 에이전트 파일, 부트스트랩 템플릿, 메모리를 위한 디렉터리
3. **Gateway** — 포트, 바인드 주소, 인증 모드
4. **채널**(선택 사항) — BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams,
   Telegram, WhatsApp 등과 같은 내장 및 번들 채팅 채널
5. **데몬**(선택 사항) — Gateway가 자동으로 시작되도록 하는 백그라운드 서비스

## CLI 온보딩

아무 터미널에서나 실행하세요.

```bash
openclaw onboard
```

백그라운드 서비스도 한 번에 설치하려면 `--install-daemon`을 추가하세요.

전체 참조: [Onboarding (CLI)](/ko/start/wizard)
CLI 명령 문서: [`openclaw onboard`](/cli/onboard)

## macOS 앱 온보딩

OpenClaw 앱을 여세요. 첫 실행 마법사가 동일한 단계를
시각적 인터페이스로 안내합니다.

전체 참조: [Onboarding (macOS App)](/start/onboarding)

## 사용자 지정 또는 목록에 없는 provider

사용 중인 provider가 온보딩 목록에 없다면 **Custom Provider**를 선택하고
다음을 입력하세요.

- API 호환 모드(OpenAI 호환, Anthropic 호환 또는 자동 감지)
- 기본 URL 및 API 키
- 모델 ID와 선택적 별칭

여러 개의 사용자 지정 엔드포인트를 함께 사용할 수 있으며, 각각 고유한 엔드포인트 ID를 가집니다.
