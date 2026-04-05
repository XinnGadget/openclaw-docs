---
read_when:
    - 어떤 env vars가 어떤 순서로 로드되는지 알아야 하는 경우
    - Gateway에서 누락된 API 키를 디버깅하는 경우
    - provider 인증 또는 배포 환경을 문서화하는 경우
summary: OpenClaw가 환경 변수를 로드하는 위치와 우선순위
title: 환경 변수
x-i18n:
    generated_at: "2026-04-05T12:44:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: a80aea69ca2ffe19a4e93140f05dd81fd576955562ff9913135d38a685a0353c
    source_path: help/environment.md
    workflow: 15
---

# 환경 변수

OpenClaw는 여러 소스에서 환경 변수를 가져옵니다. 규칙은 **기존 값을 절대 덮어쓰지 않는 것**입니다.

## 우선순위(높음 → 낮음)

1. **프로세스 환경**(Gateway 프로세스가 부모 셸/데몬에서 이미 받은 값)
2. **현재 작업 디렉터리의 `.env`** (dotenv 기본값, 덮어쓰지 않음)
3. `~/.openclaw/.env`의 **전역 `.env`** (즉 `$OPENCLAW_STATE_DIR/.env`, 덮어쓰지 않음)
4. `~/.openclaw/openclaw.json`의 **config `env` 블록** (값이 없을 때만 적용)
5. **선택적 login-shell import** (`env.shellEnv.enabled` 또는 `OPENCLAW_LOAD_SHELL_ENV=1`), 예상 키가 없을 때만 적용

Ubuntu 새 설치에서 기본 상태 디렉터리를 사용하는 경우, OpenClaw는 전역 `.env` 뒤에 `~/.config/openclaw/gateway.env`도 호환성 폴백으로 취급합니다. 두 파일이 모두 존재하고 값이 다르면, OpenClaw는 `~/.openclaw/.env`를 유지하고 경고를 출력합니다.

config 파일 자체가 완전히 없으면 4단계는 건너뛰며, shell import는 활성화되어 있으면 계속 실행됩니다.

## Config `env` 블록

인라인 env vars를 설정하는 두 가지 동등한 방법이 있습니다(둘 다 덮어쓰지 않음).

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: {
      GROQ_API_KEY: "gsk-...",
    },
  },
}
```

## Shell env import

`env.shellEnv`는 login shell을 실행하고 **누락된** 예상 키만 가져옵니다.

```json5
{
  env: {
    shellEnv: {
      enabled: true,
      timeoutMs: 15000,
    },
  },
}
```

동등한 env vars:

- `OPENCLAW_LOAD_SHELL_ENV=1`
- `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`

## 런타임 주입 env vars

OpenClaw는 생성된 자식 프로세스에 컨텍스트 마커도 주입합니다.

- `OPENCLAW_SHELL=exec`: `exec` tool을 통해 실행되는 명령에 설정
- `OPENCLAW_SHELL=acp`: ACP 런타임 백엔드 프로세스 생성 시 설정(예: `acpx`)
- `OPENCLAW_SHELL=acp-client`: `openclaw acp client`가 ACP 브리지 프로세스를 생성할 때 설정
- `OPENCLAW_SHELL=tui-local`: 로컬 TUI `!` 셸 명령에 설정

이들은 런타임 마커이며(사용자 config에 필수 아님), 컨텍스트별 규칙을 적용하기 위한 셸/프로필 로직에서 사용할 수 있습니다.

## UI env vars

- `OPENCLAW_THEME=light`: 터미널 배경이 밝을 때 밝은 TUI 팔레트를 강제
- `OPENCLAW_THEME=dark`: 어두운 TUI 팔레트를 강제
- `COLORFGBG`: 터미널이 이를 내보내면 OpenClaw는 배경색 힌트를 사용해 TUI 팔레트를 자동 선택

## Config에서 env var 치환

config 문자열 값에서 `${VAR_NAME}` 문법을 사용해 env vars를 직접 참조할 수 있습니다.

```json5
{
  models: {
    providers: {
      "vercel-gateway": {
        apiKey: "${VERCEL_GATEWAY_API_KEY}",
      },
    },
  },
}
```

전체 세부 정보는 [구성: Env var 치환](/gateway/configuration-reference#env-var-substitution)을 참조하세요.

## Secret refs vs `${ENV}` 문자열

OpenClaw는 env 기반 패턴 두 가지를 지원합니다.

- config 값에서의 `${VAR}` 문자열 치환
- secrets refs를 지원하는 필드용 SecretRef 객체 (`{ source: "env", provider: "default", id: "VAR" }`)

둘 다 활성화 시점에 프로세스 env에서 해석됩니다. SecretRef 세부 정보는 [Secrets 관리](/gateway/secrets)에 문서화되어 있습니다.

## 경로 관련 env vars

| 변수 | 용도 |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCLAW_HOME` | 모든 내부 경로 해석(`~/.openclaw/`, agent 디렉터리, 세션, 자격 증명)에 사용되는 홈 디렉터리를 재정의합니다. 전용 서비스 사용자로 OpenClaw를 실행할 때 유용합니다. |
| `OPENCLAW_STATE_DIR` | 상태 디렉터리 재정의(기본값 `~/.openclaw`) |
| `OPENCLAW_CONFIG_PATH` | config 파일 경로 재정의(기본값 `~/.openclaw/openclaw.json`) |

## 로깅

| 변수 | 용도 |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `OPENCLAW_LOG_LEVEL` | 파일 및 콘솔 모두의 로그 레벨을 재정의합니다(예: `debug`, `trace`). config의 `logging.level` 및 `logging.consoleLevel`보다 우선합니다. 잘못된 값은 경고와 함께 무시됩니다. |

### `OPENCLAW_HOME`

설정되면 `OPENCLAW_HOME`은 모든 내부 경로 해석에서 시스템 홈 디렉터리(`$HOME` / `os.homedir()`)를 대체합니다. 이를 통해 헤드리스 서비스 계정에 대한 완전한 파일시스템 격리가 가능합니다.

**우선순위:** `OPENCLAW_HOME` > `$HOME` > `USERPROFILE` > `os.homedir()`

**예시** (macOS LaunchDaemon):

```xml
<key>EnvironmentVariables</key>
<dict>
  <key>OPENCLAW_HOME</key>
  <string>/Users/user</string>
</dict>
```

`OPENCLAW_HOME`은 틸드 경로(예: `~/svc`)로도 설정할 수 있으며, 사용 전에 `$HOME`을 기준으로 확장됩니다.

## nvm 사용자: `web_fetch` TLS 실패

Node.js를 시스템 패키지 관리자가 아니라 **nvm**으로 설치한 경우, 내장 `fetch()`는 nvm에 번들된 CA 저장소를 사용하며, 여기에 최신 루트 CA(ISRG Root X1/X2 for Let's Encrypt, DigiCert Global Root G2 등)가 없을 수 있습니다. 이 경우 대부분의 HTTPS 사이트에서 `web_fetch`가 `"fetch failed"`로 실패합니다.

Linux에서는 OpenClaw가 nvm을 자동 감지하고 실제 시작 환경에 수정 사항을 적용합니다.

- `openclaw gateway install`은 `NODE_EXTRA_CA_CERTS`를 systemd 서비스 환경에 기록합니다
- `openclaw` CLI 엔트리포인트는 Node 시작 전에 `NODE_EXTRA_CA_CERTS`를 설정한 상태로 자신을 다시 실행합니다

**수동 수정(이전 버전 또는 직접 `node ...` 실행용):**

OpenClaw를 시작하기 전에 변수를 export하세요.

```bash
export NODE_EXTRA_CA_CERTS=/etc/ssl/certs/ca-certificates.crt
openclaw gateway run
```

이 변수는 `~/.openclaw/.env`에만 써 두는 방식에 의존하지 마세요. Node는 프로세스 시작 시 `NODE_EXTRA_CA_CERTS`를 읽습니다.

## 관련 문서

- [Gateway 구성](/gateway/configuration)
- [FAQ: env vars 및 .env 로딩](/help/faq#env-vars-and-env-loading)
- [모델 개요](/concepts/models)
