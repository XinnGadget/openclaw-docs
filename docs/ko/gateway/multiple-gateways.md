---
read_when:
    - 같은 머신에서 둘 이상의 Gateway를 실행하는 경우
    - Gateway별로 격리된 config/상태/포트가 필요한 경우
summary: 한 호스트에서 여러 OpenClaw Gateway 실행(격리, 포트 및 프로필)
title: 여러 Gateway
x-i18n:
    generated_at: "2026-04-05T12:42:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 061f204bf56b28c6bd0e2c9aee6c561a8a162ca219060117fea4d3a007f01899
    source_path: gateway/multiple-gateways.md
    workflow: 15
---

# 여러 Gateway(같은 호스트)

대부분의 설정에서는 하나의 Gateway를 사용하는 것이 좋습니다. 하나의 Gateway로 여러 메시징 연결과 agent를 처리할 수 있기 때문입니다. 더 강한 격리 또는 이중화(예: 구조용 봇)가 필요하다면, 프로필/포트를 분리한 별도 Gateway를 실행하세요.

## 격리 체크리스트(필수)

- `OPENCLAW_CONFIG_PATH` — 인스턴스별 config 파일
- `OPENCLAW_STATE_DIR` — 인스턴스별 세션, 자격 증명, 캐시
- `agents.defaults.workspace` — 인스턴스별 workspace 루트
- `gateway.port` (또는 `--port`) — 인스턴스별 고유 포트
- 파생 포트(browser/canvas)는 겹치지 않아야 함

이들이 공유되면 config 경합과 포트 충돌이 발생합니다.

## 권장: 프로필(`--profile`)

프로필은 `OPENCLAW_STATE_DIR` + `OPENCLAW_CONFIG_PATH`를 자동으로 범위 지정하고 서비스 이름에 접미사를 붙입니다.

```bash
# main
openclaw --profile main setup
openclaw --profile main gateway --port 18789

# rescue
openclaw --profile rescue setup
openclaw --profile rescue gateway --port 19001
```

프로필별 서비스:

```bash
openclaw --profile main gateway install
openclaw --profile rescue gateway install
```

## 구조용 봇 가이드

같은 호스트에서 다음을 각각 따로 갖는 두 번째 Gateway를 실행하세요:

- profile/config
- 상태 디렉터리
- workspace
- 기본 포트(및 파생 포트)

이렇게 하면 주 봇이 다운되었을 때 구조용 봇이 이를 디버깅하거나 config 변경을 적용할 수 있도록 주 봇과 구조용 봇이 격리됩니다.

포트 간격: 기본 포트 사이에 최소 20개 포트를 비워 두어 파생 browser/canvas/CDP 포트가 절대 충돌하지 않도록 하세요.

### 설치 방법(구조용 봇)

```bash
# Main bot (existing or fresh, without --profile param)
# Runs on port 18789 + Chrome CDC/Canvas/... Ports
openclaw onboard
openclaw gateway install

# Rescue bot (isolated profile + ports)
openclaw --profile rescue onboard
# Notes:
# - workspace name will be postfixed with -rescue per default
# - Port should be at least 18789 + 20 Ports,
#   better choose completely different base port, like 19789,
# - rest of the onboarding is the same as normal

# To install the service (if not happened automatically during setup)
openclaw --profile rescue gateway install
```

## 포트 매핑(파생)

기본 포트 = `gateway.port` (또는 `OPENCLAW_GATEWAY_PORT` / `--port`).

- browser control 서비스 포트 = 기본 포트 + 2 (loopback 전용)
- canvas host는 Gateway HTTP 서버에서 제공됨 (`gateway.port`와 같은 포트)
- Browser profile CDP 포트는 `browser.controlPort + 9 .. + 108` 범위에서 자동 할당됨

config 또는 env에서 이들 중 하나라도 재정의하면, 인스턴스별로 고유하게 유지해야 합니다.

## Browser/CDP 참고(흔한 함정)

- 여러 인스턴스에서 `browser.cdpUrl`을 같은 값으로 고정하지 **마세요**.
- 각 인스턴스는 자체 browser control 포트와 CDP 범위가 필요합니다(gateway 포트에서 파생됨).
- 명시적 CDP 포트가 필요하면 인스턴스별로 `browser.profiles.<name>.cdpPort`를 설정하세요.
- 원격 Chrome은 `browser.profiles.<name>.cdpUrl`을 사용하세요(프로필별, 인스턴스별).

## 수동 env 예시

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/main.json \
OPENCLAW_STATE_DIR=~/.openclaw-main \
openclaw gateway --port 18789

OPENCLAW_CONFIG_PATH=~/.openclaw/rescue.json \
OPENCLAW_STATE_DIR=~/.openclaw-rescue \
openclaw gateway --port 19001
```

## 빠른 확인

```bash
openclaw --profile main gateway status --deep
openclaw --profile rescue gateway status --deep
openclaw --profile rescue gateway probe
openclaw --profile main status
openclaw --profile rescue status
openclaw --profile rescue browser status
```

해석:

- `gateway status --deep`는 이전 설치에서 남아 있는 오래된 launchd/systemd/schtasks 서비스를 찾는 데 도움이 됩니다.
- `multiple reachable gateways detected` 같은 `gateway probe` 경고 문구는 의도적으로 둘 이상의 격리된 gateway를 실행할 때만 정상입니다.
