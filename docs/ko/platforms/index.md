---
read_when:
    - OS 지원이나 설치 경로를 찾고 있을 때
    - Gateway를 어디에서 실행할지 결정할 때
summary: 플랫폼 지원 개요(Gateway + 컴패니언 앱)
title: 플랫폼
x-i18n:
    generated_at: "2026-04-05T12:48:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: d5be4743fd39eca426d65db940f04f3a8fc3ff2c5e10b0e82bc55fc35a7d1399
    source_path: platforms/index.md
    workflow: 15
---

# 플랫폼

OpenClaw 코어는 TypeScript로 작성되었습니다. **Node가 권장 런타임**입니다.
Bun은 Gateway에 권장되지 않습니다(WhatsApp/Telegram 버그 때문).

macOS용 컴패니언 앱(메뉴 막대 앱)과 모바일 노드(iOS/Android)용 컴패니언 앱이 있습니다. Windows와
Linux용 컴패니언 앱도 계획되어 있지만, Gateway는 오늘 이미 완전히 지원됩니다.
Windows용 네이티브 컴패니언 앱도 계획되어 있으며, Gateway는 WSL2를 통해 실행하는 것이 권장됩니다.

## OS 선택

- macOS: [macOS](/platforms/macos)
- iOS: [iOS](/platforms/ios)
- Android: [Android](/platforms/android)
- Windows: [Windows](/platforms/windows)
- Linux: [Linux](/platforms/linux)

## VPS 및 호스팅

- VPS 허브: [VPS hosting](/vps)
- Fly.io: [Fly.io](/install/fly)
- Hetzner (Docker): [Hetzner](/install/hetzner)
- GCP (Compute Engine): [GCP](/install/gcp)
- Azure (Linux VM): [Azure](/install/azure)
- exe.dev (VM + HTTPS proxy): [exe.dev](/install/exe-dev)

## 공통 링크

- 설치 가이드: [Getting Started](/ko/start/getting-started)
- Gateway 운영 가이드: [Gateway](/gateway)
- Gateway 구성: [Configuration](/gateway/configuration)
- 서비스 상태: `openclaw gateway status`

## Gateway 서비스 설치 (CLI)

다음 중 하나를 사용하세요(모두 지원됨):

- Wizard (권장): `openclaw onboard --install-daemon`
- 직접 실행: `openclaw gateway install`
- Configure 흐름: `openclaw configure` → **Gateway service** 선택
- 복구/마이그레이션: `openclaw doctor` (서비스 설치 또는 수정 제안)

서비스 대상은 OS에 따라 다릅니다:

- macOS: LaunchAgent (`ai.openclaw.gateway` 또는 `ai.openclaw.<profile>`; 레거시 `com.openclaw.*`)
- Linux/WSL2: systemd user service (`openclaw-gateway[-<profile>].service`)
- Native Windows: Scheduled Task (`OpenClaw Gateway` 또는 `OpenClaw Gateway (<profile>)`), 작업 생성이 거부되면 사용자별 Startup-folder 로그인 항목으로 대체
