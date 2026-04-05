---
read_when:
    - 새 머신을 설정하는 경우
    - '"최신 + 최고"를 원하지만 개인 설정은 망가뜨리고 싶지 않은 경우'
summary: OpenClaw를 위한 고급 설정 및 개발 워크플로
title: 설정
x-i18n:
    generated_at: "2026-04-05T12:55:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: be4e280dde7f3a224345ca557ef2fb35a9c9db8520454ff63794ac6f8d4e71e7
    source_path: start/setup.md
    workflow: 15
---

# 설정

<Note>
처음 설정하는 경우 [Getting Started](/ko/start/getting-started)부터 시작하세요.
온보딩 세부 사항은 [Onboarding (CLI)](/ko/start/wizard)를 참조하세요.
</Note>

## 요약

- **사용자별 맞춤 설정은 리포지토리 밖에 있습니다:** `~/.openclaw/workspace`(워크스페이스) + `~/.openclaw/openclaw.json`(구성).
- **안정적인 워크플로:** macOS 앱을 설치하고, 번들된 Gateway를 실행하게 둡니다.
- **최첨단 워크플로:** `pnpm gateway:watch`로 직접 Gateway를 실행한 다음, macOS 앱이 로컬 모드에서 연결되게 둡니다.

## 사전 요구 사항(소스에서)

- Node 24 권장(Node 22 LTS, 현재 `22.14+`, 역시 지원됨)
- `pnpm` 권장(또는 의도적으로 [Bun workflow](/ko/install/bun)를 사용하는 경우 Bun)
- Docker(선택 사항; 컨테이너화된 설정/e2e에만 필요 — [Docker](/ko/install/docker) 참조)

## 맞춤 설정 전략(업데이트가 문제를 일으키지 않도록)

“나에게 100% 맞춤”이면서 _동시에_ 업데이트도 쉽게 하고 싶다면, 사용자 정의는 다음 위치에 유지하세요.

- **구성:** `~/.openclaw/openclaw.json` (JSON/JSON5 유사 형식)
- **워크스페이스:** `~/.openclaw/workspace` (skills, 프롬프트, 메모리; 비공개 git 리포지토리로 만드는 것을 권장)

한 번만 부트스트랩하세요.

```bash
openclaw setup
```

이 리포지토리 내부에서는 로컬 CLI 엔트리를 사용하세요.

```bash
openclaw setup
```

아직 전역 설치가 없다면 `pnpm openclaw setup`으로 실행하세요(Bun workflow를 사용하는 경우 `bun run openclaw setup`).

## 이 리포지토리에서 Gateway 실행

`pnpm build` 후에는 패키지된 CLI를 직접 실행할 수 있습니다.

```bash
node openclaw.mjs gateway --port 18789 --verbose
```

## 안정적인 워크플로(macOS 앱 우선)

1. **OpenClaw.app**을 설치하고 실행합니다(메뉴 막대).
2. 온보딩/권한 체크리스트(TCC 프롬프트)를 완료합니다.
3. Gateway가 **Local**로 설정되어 실행 중인지 확인합니다(앱이 관리함).
4. 표면을 연결합니다(예: WhatsApp).

```bash
openclaw channels login
```

5. 상태를 점검합니다.

```bash
openclaw health
```

빌드에서 온보딩을 사용할 수 없는 경우:

- `openclaw setup`을 실행한 다음 `openclaw channels login`을 실행하고, 그다음 Gateway를 수동으로 시작하세요(`openclaw gateway`).

## 최첨단 워크플로(터미널에서 Gateway 실행)

목표: TypeScript Gateway를 작업하고, 핫 리로드를 얻고, macOS 앱 UI는 계속 연결된 상태로 유지합니다.

### 0) (선택 사항) macOS 앱도 소스에서 실행

macOS 앱도 최신 개발 상태로 사용하고 싶다면 다음을 실행하세요.

```bash
./scripts/restart-mac.sh
```

### 1) 개발용 Gateway 시작

```bash
pnpm install
pnpm gateway:watch
```

`gateway:watch`는 Gateway를 watch 모드로 실행하고, 관련 소스,
구성, 번들된 플러그인 메타데이터가 변경되면 다시 로드합니다.

의도적으로 Bun workflow를 사용하는 경우, 동등한 명령은 다음과 같습니다.

```bash
bun install
bun run gateway:watch
```

### 2) 실행 중인 Gateway에 macOS 앱 연결

**OpenClaw.app**에서:

- 연결 모드: **Local**
  앱이 구성된 포트에서 실행 중인 Gateway에 연결됩니다.

### 3) 확인

- 앱 내 Gateway 상태에 **“Using existing gateway …”**가 표시되어야 합니다
- 또는 CLI로 확인:

```bash
openclaw health
```

### 흔한 함정

- **잘못된 포트:** Gateway WS 기본값은 `ws://127.0.0.1:18789`입니다. 앱과 CLI가 같은 포트를 사용하도록 유지하세요.
- **상태가 저장되는 위치:**
  - 채널/provider 상태: `~/.openclaw/credentials/`
  - 모델 인증 프로필: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
  - 세션: `~/.openclaw/agents/<agentId>/sessions/`
  - 로그: `/tmp/openclaw/`

## 자격 증명 저장소 맵

인증을 디버깅하거나 무엇을 백업할지 결정할 때 이것을 사용하세요.

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram bot token**: config/env 또는 `channels.telegram.tokenFile`(일반 파일만 허용; 심볼릭 링크는 거부됨)
- **Discord bot token**: config/env 또는 SecretRef(env/file/exec providers)
- **Slack 토큰**: config/env (`channels.slack.*`)
- **페어링 허용 목록**:
  - `~/.openclaw/credentials/<channel>-allowFrom.json` (기본 계정)
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json` (비기본 계정)
- **모델 인증 프로필**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **파일 기반 secrets payload(선택 사항)**: `~/.openclaw/secrets.json`
- **레거시 OAuth 가져오기**: `~/.openclaw/credentials/oauth.json`
  자세한 내용: [Security](/ko/gateway/security#credential-storage-map).

## 업데이트(설정을 망가뜨리지 않고)

- `~/.openclaw/workspace`와 `~/.openclaw/`를 “내 것”으로 유지하세요. 개인 프롬프트/구성을 `openclaw` 리포지토리에 넣지 마세요.
- 소스 업데이트: `git pull` + 선택한 패키지 관리자 설치 단계(기본값은 `pnpm install`, Bun workflow는 `bun install`) + 계속해서 일치하는 `gateway:watch` 명령을 사용하세요.

## Linux(systemd 사용자 서비스)

Linux 설치는 systemd **사용자** 서비스를 사용합니다. 기본적으로 systemd는 로그아웃/유휴 시 사용자
서비스를 중지하므로 Gateway도 종료됩니다. 온보딩은 사용자를 위해 lingering을 활성화하려고 시도합니다(sudo를 요청할 수 있음). 여전히 꺼져 있다면 다음을 실행하세요.

```bash
sudo loginctl enable-linger $USER
```

항상 켜져 있어야 하거나 다중 사용자 서버라면, **사용자** 서비스 대신 **시스템** 서비스를 고려하세요
(lingering 불필요). systemd 관련 참고 사항은 [Gateway runbook](/ko/gateway)을 참조하세요.

## 관련 문서

- [Gateway runbook](/ko/gateway) (플래그, 감독, 포트)
- [Gateway configuration](/ko/gateway/configuration) (구성 스키마 + 예시)
- [Discord](/ko/channels/discord) 및 [Telegram](/ko/channels/telegram) (reply 태그 + replyToMode 설정)
- [OpenClaw assistant setup](/start/openclaw)
- [macOS app](/ko/platforms/macos) (gateway 수명 주기)
