---
read_when:
    - 새 OpenClaw 에이전트 세션을 시작하는 경우
    - 기본 Skills를 활성화하거나 감사하려는 경우
summary: 개인 비서 설정을 위한 기본 OpenClaw 에이전트 지침과 Skills 목록
title: 기본 AGENTS.md
x-i18n:
    generated_at: "2026-04-05T12:53:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 45990bc4e6fa2e3d80e76207e62ec312c64134bee3bc832a5cae32ca2eda3b61
    source_path: reference/AGENTS.default.md
    workflow: 15
---

# AGENTS.md - OpenClaw 개인 비서 (기본값)

## 첫 실행(권장)

OpenClaw는 에이전트를 위해 전용 워크스페이스 디렉터리를 사용합니다. 기본값: `~/.openclaw/workspace` (`agents.defaults.workspace`를 통해 구성 가능).

1. 워크스페이스를 생성합니다(아직 없으면).

```bash
mkdir -p ~/.openclaw/workspace
```

2. 기본 워크스페이스 템플릿을 워크스페이스에 복사합니다.

```bash
cp docs/reference/templates/AGENTS.md ~/.openclaw/workspace/AGENTS.md
cp docs/reference/templates/SOUL.md ~/.openclaw/workspace/SOUL.md
cp docs/reference/templates/TOOLS.md ~/.openclaw/workspace/TOOLS.md
```

3. 선택 사항: 개인 비서 Skills 목록을 원하면 AGENTS.md를 이 파일로 교체합니다.

```bash
cp docs/reference/AGENTS.default.md ~/.openclaw/workspace/AGENTS.md
```

4. 선택 사항: `agents.defaults.workspace`를 설정하여 다른 워크스페이스를 선택합니다(`~` 지원).

```json5
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
}
```

## 기본 안전 설정

- 디렉터리나 비밀 정보를 채팅에 그대로 덤프하지 마세요.
- 명시적으로 요청받지 않았다면 파괴적인 명령을 실행하지 마세요.
- 외부 메시징 표면으로 부분/스트리밍 응답을 보내지 마세요(최종 응답만 전송).

## 세션 시작(필수)

- `SOUL.md`, `USER.md`, 그리고 `memory/`의 오늘+어제 항목을 읽습니다.
- `MEMORY.md`가 있으면 읽고, `MEMORY.md`가 없을 때만 소문자 `memory.md`로 대체합니다.
- 응답하기 전에 이 작업을 수행합니다.

## Soul(필수)

- `SOUL.md`는 정체성, 어조, 경계를 정의합니다. 최신 상태로 유지하세요.
- `SOUL.md`를 변경했다면 사용자에게 알리세요.
- 당신은 각 세션마다 새로운 인스턴스이며, 연속성은 이 파일들에 있습니다.

## 공유 공간(권장)

- 당신은 사용자의 목소리가 아닙니다. 그룹 채팅이나 공개 채널에서는 특히 주의하세요.
- 개인 데이터, 연락처 정보, 내부 메모를 공유하지 마세요.

## 메모리 시스템(권장)

- 일일 로그: `memory/YYYY-MM-DD.md` (`memory/`가 없으면 생성).
- 장기 메모리: 지속되는 사실, 선호도, 결정은 `MEMORY.md`에 기록합니다.
- 소문자 `memory.md`는 레거시 대체용일 뿐이며, 두 루트 파일을 의도적으로 함께 유지하지 마세요.
- 세션 시작 시 오늘 + 어제 + `MEMORY.md`가 있으면 이를 읽고, 없으면 `memory.md`를 읽습니다.
- 기록할 내용: 결정, 선호도, 제약 조건, 미해결 루프.
- 명시적으로 요청받지 않은 한 비밀 정보는 피하세요.

## 도구 및 Skills

- 도구는 Skills 안에 있습니다. 필요할 때 각 Skill의 `SKILL.md`를 따르세요.
- 환경별 메모는 `TOOLS.md`(Skills용 메모)에 보관하세요.

## 백업 팁(권장)

이 워크스페이스를 Clawd의 “메모리”로 취급한다면, `AGENTS.md`와 메모리 파일이 백업되도록 git 리포지토리로 만드는 것이 좋습니다(가능하면 비공개).

```bash
cd ~/.openclaw/workspace
git init
git add AGENTS.md
git commit -m "Add Clawd workspace"
# Optional: add a private remote + push
```

## OpenClaw가 하는 일

- WhatsApp 게이트웨이 + Pi 코딩 에이전트를 실행하여 비서가 채팅을 읽고/쓰고, 컨텍스트를 가져오고, 호스트 Mac을 통해 Skills를 실행할 수 있게 합니다.
- macOS 앱은 권한(화면 녹화, 알림, 마이크)을 관리하고 번들된 바이너리를 통해 `openclaw` CLI를 노출합니다.
- 직접 채팅은 기본적으로 에이전트의 `main` 세션으로 통합되고, 그룹은 `agent:<agentId>:<channel>:group:<id>`로 격리된 상태를 유지합니다(룸/채널: `agent:<agentId>:<channel>:channel:<id>`). 하트비트는 백그라운드 작업을 계속 활성 상태로 유지합니다.

## 핵심 Skills(Settings → Skills에서 활성화)

- **mcporter** — 외부 Skill 백엔드를 관리하기 위한 도구 서버 런타임/CLI.
- **Peekaboo** — 선택적 AI 비전 분석이 포함된 빠른 macOS 스크린샷.
- **camsnap** — RTSP/ONVIF 보안 카메라에서 프레임, 클립 또는 동작 알림을 캡처합니다.
- **oracle** — 세션 재생 및 브라우저 제어 기능이 있는 OpenAI 지원 에이전트 CLI.
- **eightctl** — 터미널에서 수면을 제어합니다.
- **imsg** — iMessage 및 SMS를 보내고, 읽고, 스트리밍합니다.
- **wacli** — WhatsApp CLI: 동기화, 검색, 전송.
- **discord** — Discord 작업: 반응, 스티커, 투표. `user:<id>` 또는 `channel:<id>` 대상을 사용하세요(숫자만 있는 ID는 모호함).
- **gog** — Google Suite CLI: Gmail, Calendar, Drive, Contacts.
- **spotify-player** — 재생 검색/대기열 추가/제어를 위한 터미널 Spotify 클라이언트.
- **sag** — mac 스타일 say UX를 갖춘 ElevenLabs 음성 기능. 기본적으로 스피커로 스트리밍합니다.
- **Sonos CLI** — 스크립트에서 Sonos 스피커(검색/상태/재생/볼륨/그룹화)를 제어합니다.
- **blucli** — 스크립트에서 BluOS 플레이어를 재생, 그룹화, 자동화합니다.
- **OpenHue CLI** — 장면 및 자동화를 위한 Philips Hue 조명 제어.
- **OpenAI Whisper** — 빠른 받아쓰기 및 음성메일 전사를 위한 로컬 speech-to-text.
- **Gemini CLI** — 빠른 Q&A를 위한 터미널의 Google Gemini 모델.
- **agent-tools** — 자동화 및 헬퍼 스크립트를 위한 유틸리티 툴킷.

## 사용 참고 사항

- 스크립팅에는 `openclaw` CLI를 우선 사용하세요. 권한은 mac 앱이 처리합니다.
- 설치는 Skills 탭에서 실행하세요. 바이너리가 이미 있으면 버튼이 숨겨집니다.
- 하트비트를 활성 상태로 유지하여 비서가 알림을 예약하고, 받은 편지함을 모니터링하고, 카메라 캡처를 트리거할 수 있게 하세요.
- Canvas UI는 네이티브 오버레이와 함께 전체 화면으로 실행됩니다. 중요한 컨트롤을 좌상단/우상단/하단 가장자리에 배치하지 말고, 레이아웃에 명시적인 여백을 추가하며 safe-area insets에 의존하지 마세요.
- 브라우저 기반 검증에는 OpenClaw가 관리하는 Chrome 프로필과 함께 `openclaw browser`(탭/상태/스크린샷)를 사용하세요.
- DOM 검사에는 `openclaw browser eval|query|dom|snapshot`을 사용하세요(기계 출력이 필요하면 `--json`/`--out`도 사용).
- 상호작용에는 `openclaw browser click|type|hover|drag|select|upload|press|wait|navigate|back|evaluate|run`을 사용하세요(click/type에는 snapshot ref가 필요하며, CSS 선택자에는 `evaluate`를 사용).
