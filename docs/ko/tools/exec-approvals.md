---
read_when:
    - exec 승인 또는 allowlist를 구성하는 경우
    - macOS 앱에서 exec 승인 UX를 구현하는 경우
    - 샌드박스 탈출 프롬프트와 그 영향을 검토하는 경우
summary: Exec 승인, allowlist, 샌드박스 탈출 프롬프트
title: Exec 승인
x-i18n:
    generated_at: "2026-04-05T12:58:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: a1efa3b78efe3ca6246acfb37830b103ede40cc5298dcc7da8e9fbc5f6cc88ef
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Exec 승인

Exec 승인은 샌드박스된 agent가 실제 호스트(`gateway` 또는 `node`)에서 명령을 실행할 수 있게 해 주는 **컴패니언 앱 / 노드 호스트 가드레일**입니다. 일종의 안전 인터록처럼 생각하면 됩니다. 명령은 정책 + allowlist + (선택적) 사용자 승인 모두가 동의할 때만 허용됩니다.
Exec 승인은 tool 정책 및 elevated 게이팅에 **추가로** 적용됩니다(elevated가 `full`로 설정된 경우는 예외이며, 이 경우 승인을 건너뜁니다).
실효 정책은 `tools.exec.*`와 승인 기본값 중 **더 엄격한 쪽**입니다. 승인 필드가 생략되면 `tools.exec` 값이 사용됩니다.
호스트 exec는 해당 머신의 로컬 승인 상태도 사용합니다. `~/.openclaw/exec-approvals.json`에 있는 호스트 로컬
`ask: "always"`는 세션 또는 config 기본값이 `ask: "on-miss"`를 요청하더라도 계속 프롬프트를 표시합니다.
요청된 정책, 호스트 정책 소스 및 실효 결과를 확인하려면 `openclaw approvals get`, `openclaw approvals get --gateway`, 또는
`openclaw approvals get --node <id|name|ip>`를 사용하세요.

컴패니언 앱 UI를 **사용할 수 없는** 경우, 프롬프트가 필요한 모든 요청은
**ask fallback**(기본값: deny)으로 처리됩니다.

## 적용 위치

Exec 승인은 실행 호스트에서 로컬로 강제됩니다:

- **gateway host** → gateway 머신의 `openclaw` 프로세스
- **node host** → 노드 러너(macOS 컴패니언 앱 또는 헤드리스 노드 호스트)

신뢰 모델 참고:

- Gateway 인증을 통과한 호출자는 해당 Gateway의 신뢰된 운영자입니다.
- 페어링된 노드는 그 신뢰된 운영자 권한을 node host까지 확장합니다.
- Exec 승인은 우발적인 실행 위험을 줄여 주지만, 사용자별 인증 경계는 아닙니다.
- 승인된 node-host 실행은 정규화된 실행 컨텍스트를 바인딩합니다: 정규화된 cwd, 정확한 argv, env 바인딩(있는 경우), 고정된 실행 파일 경로(적용 가능한 경우).
- 셸 스크립트 및 직접 인터프리터/런타임 파일 호출의 경우, OpenClaw는 하나의 구체적인 로컬 파일 피연산자도 바인딩하려고 시도합니다. 이 바인딩된 파일이 승인 후 실행 전에 변경되면, 변경된 내용을 실행하는 대신 실행이 거부됩니다.
- 이 파일 바인딩은 의도적으로 최선의 노력 수준이며, 모든 인터프리터/런타임 로더 경로의 완전한 의미 모델은 아닙니다. 승인 모드가 정확히 하나의 구체적인 로컬 파일을 바인딩할 수 없으면, 완전한 커버리지를 가장하는 대신 승인 기반 실행 생성을 거부합니다.

macOS 분리 구조:

- **node host 서비스**는 `system.run`을 로컬 IPC를 통해 **macOS 앱**으로 전달합니다.
- **macOS 앱**은 승인을 강제하고 UI 컨텍스트에서 명령을 실행합니다.

## 설정 및 저장 위치

승인은 실행 호스트의 로컬 JSON 파일에 저장됩니다:

`~/.openclaw/exec-approvals.json`

예시 스키마:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## 무승인 "YOLO" 모드

승인 프롬프트 없이 호스트 exec를 실행하려면 **두 정책 계층 모두** 열어야 합니다:

- OpenClaw config의 요청된 exec 정책(`tools.exec.*`)
- 호스트 로컬 승인 정책(`~/.openclaw/exec-approvals.json`)

이를 명시적으로 더 엄격하게 설정하지 않는 한, 이것이 이제 기본 호스트 동작입니다:

- `tools.exec.security`: `gateway`/`node`에서 `full`
- `tools.exec.ask`: `off`
- 호스트 `askFallback`: `full`

중요한 구분점:

- `tools.exec.host=auto`는 exec가 어디에서 실행될지 선택합니다: 가능한 경우 샌드박스, 아니면 gateway.
- YOLO는 호스트 exec 승인 방식을 선택합니다: `security=full` + `ask=off`.
- `auto`는 샌드박스된 세션에서 gateway 라우팅을 자유롭게 우회할 수 있게 만들지 않습니다. 호출별 `host=node` 요청은 `auto`에서 허용되며, `host=gateway`는 샌드박스 런타임이 활성 상태가 아닐 때만 `auto`에서 허용됩니다. 안정적인 non-auto 기본값이 필요하면 `tools.exec.host`를 설정하거나 `/exec host=...`를 명시적으로 사용하세요.

더 보수적인 설정을 원하면 계층 중 하나를 다시 `allowlist` / `on-miss`
또는 `deny`로 강화하세요.

지속적인 gateway-host "다시 묻지 않음" 설정:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

그런 다음 호스트 승인 파일도 일치하도록 설정하세요:

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

node host의 경우, 대신 해당 노드에 같은 승인 파일을 적용하세요:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

세션 전용 단축키:

- `/exec security=full ask=off`는 현재 세션만 변경합니다.
- `/elevated full`은 해당 세션의 exec 승인도 건너뛰는 비상용 단축키입니다.

호스트 승인 파일이 config보다 더 엄격하면, 더 엄격한 호스트 정책이 여전히 우선합니다.

## 정책 조절 항목

### Security (`exec.security`)

- **deny**: 모든 호스트 exec 요청 차단.
- **allowlist**: allowlist에 있는 명령만 허용.
- **full**: 모든 것 허용(elevated와 동일).

### Ask (`exec.ask`)

- **off**: 절대 프롬프트 표시 안 함.
- **on-miss**: allowlist가 일치하지 않을 때만 프롬프트 표시.
- **always**: 모든 명령에 대해 프롬프트 표시.
- 실효 ask 모드가 `always`이면 `allow-always`의 지속 신뢰도 프롬프트를 억제하지 못합니다.

### Ask fallback (`askFallback`)

프롬프트가 필요하지만 연결 가능한 UI가 없으면 fallback이 다음을 결정합니다:

- **deny**: 차단.
- **allowlist**: allowlist가 일치할 때만 허용.
- **full**: 허용.

### 인라인 인터프리터 eval 강화 (`tools.exec.strictInlineEval`)

`tools.exec.strictInlineEval=true`이면, OpenClaw는 인터프리터 바이너리 자체가 allowlist에 있더라도 인라인 코드 eval 형식을 승인 전용으로 취급합니다.

예시:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

이것은 하나의 안정적인 파일 피연산자에 깔끔하게 매핑되지 않는 인터프리터 로더에 대한 방어 심층화입니다. strict 모드에서는:

- 이러한 명령은 여전히 명시적 승인이 필요합니다.
- `allow-always`는 이들에 대해 새 allowlist 항목을 자동으로 지속 저장하지 않습니다.

## Allowlist (agent별)

Allowlist는 **agent별**입니다. agent가 여러 개 있으면 macOS 앱에서
편집할 agent를 전환하세요. 패턴은 **대소문자를 구분하지 않는 glob 일치**입니다.
패턴은 **바이너리 경로**로 해석되어야 합니다(베이스네임만 있는 항목은 무시됨).
레거시 `agents.default` 항목은 로드 시 `agents.main`으로 마이그레이션됩니다.
`echo ok && pwd` 같은 셸 체인도 여전히 각 최상위 세그먼트가 allowlist 규칙을 충족해야 합니다.

예시:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

각 allowlist 항목은 다음을 추적합니다:

- **id** UI 식별에 사용되는 안정적인 UUID(선택 사항)
- **마지막 사용** 타임스탬프
- **마지막 사용 명령**
- **마지막 해석 경로**

## Skill CLI 자동 허용

**Auto-allow skill CLIs**가 활성화되면, 알려진 Skills에서 참조하는 실행 파일은 노드(macOS node 또는 헤드리스 node host)에서 allowlist에 있는 것으로 취급됩니다. 이는 Gateway RPC를 통해 `skills.bins`를 사용해 skill bin 목록을 가져옵니다. 엄격한 수동 allowlist를 원하면 이 기능을 비활성화하세요.

중요한 신뢰 관련 참고 사항:

- 이것은 수동 경로 allowlist 항목과는 별개의 **암시적 편의 allowlist**입니다.
- Gateway와 node가 같은 신뢰 경계에 있는 신뢰된 운영자 환경을 위한 기능입니다.
- 엄격한 명시적 신뢰가 필요하면 `autoAllowSkills: false`를 유지하고 수동 경로 allowlist 항목만 사용하세요.

## 안전한 바이너리(safe bins, stdin 전용)

`tools.exec.safeBins`는 allowlist 모드에서 **명시적 allowlist 항목 없이도**
실행할 수 있는 **stdin 전용** 바이너리(예: `cut`)의 작은 목록을 정의합니다. Safe bin은
위치 기반 파일 인수와 경로처럼 보이는 토큰을 거부하므로 들어오는 스트림에서만 동작할 수 있습니다.
이를 일반적인 신뢰 목록이 아니라 스트림 필터용 좁은 빠른 경로로 취급하세요.
인터프리터 또는 런타임 바이너리(예: `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`)는 `safeBins`에 **추가하지 마세요**.
명령이 설계상 코드를 평가하거나, 하위 명령을 실행하거나, 파일을 읽을 수 있다면 명시적 allowlist 항목을 선호하고 승인 프롬프트를 활성화된 상태로 유지하세요.
사용자 지정 safe bin은 `tools.exec.safeBinProfiles.<bin>`에 명시적 프로필을 정의해야 합니다.
검증은 argv 형태만으로 결정론적으로 수행되며(호스트 파일 시스템 존재 여부는 확인하지 않음),
이로써 허용/거부 차이에 따른 파일 존재 오라클 동작을 방지합니다.
기본 safe bin의 파일 지향 옵션은 거부됩니다(예: `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Safe bin은 stdin 전용 동작을 깨는 옵션(예: `sort -o/--output/--compress-program` 및 grep 재귀 플래그)에 대해서도
바이너리별 명시적 플래그 정책을 강제합니다.
긴 옵션은 safe-bin 모드에서 fail-closed 방식으로 검증됩니다. 알 수 없는 플래그와 모호한 축약형은 거부됩니다.
safe-bin 프로필별 거부 플래그:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Safe bin은 실행 시 argv 토큰을 **리터럴 텍스트**로 취급하도록 강제합니다(stdin 전용 세그먼트에서는 glob 확장과 `$VARS` 확장 없음). 따라서 `*`나 `$HOME/...` 같은 패턴으로 파일 읽기를 우회 주입할 수 없습니다.
Safe bin은 신뢰된 바이너리 디렉터리(시스템 기본값 + 선택적
`tools.exec.safeBinTrustedDirs`)에서 해석되어야 합니다. `PATH` 항목은 절대 자동 신뢰되지 않습니다.
기본 신뢰 safe-bin 디렉터리는 의도적으로 최소화되어 있습니다: `/bin`, `/usr/bin`.
safe-bin 실행 파일이 패키지 관리자/사용자 경로(예:
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`)에 있다면 이를
`tools.exec.safeBinTrustedDirs`에 명시적으로 추가하세요.
셸 체이닝과 리디렉션은 allowlist 모드에서 자동 허용되지 않습니다.

셸 체이닝(`&&`, `||`, `;`)은 모든 최상위 세그먼트가 allowlist를 충족하면 허용됩니다
(safe bin 또는 skill 자동 허용 포함). 리디렉션은 allowlist 모드에서 여전히 지원되지 않습니다.
명령 치환(`$()` / 백틱)은 allowlist 파싱 중 거부되며, 이중 따옴표 내부도 포함됩니다.
리터럴 `$()` 텍스트가 필요하면 작은따옴표를 사용하세요.
macOS 컴패니언 앱 승인에서 셸 제어 또는 확장 문법
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`)이 포함된 원시 셸 텍스트는
셸 바이너리 자체가 allowlist에 있지 않으면 allowlist miss로 처리됩니다.
셸 래퍼(`bash|sh|zsh ... -c/-lc`)의 경우, 요청 범위 env 재정의는 작은 명시적 allowlist로 축소됩니다
(`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
allowlist 모드에서 allow-always 결정이 내려지면, 알려진 디스패치 래퍼
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`)는 래퍼 경로 대신 내부 실행 파일 경로를 지속 저장합니다.
셸 멀티플렉서(`busybox`, `toybox`)도 셸 applet(`sh`, `ash` 등)에 대해 언래핑되어
멀티플렉서 바이너리 대신 내부 실행 파일이 저장됩니다. 래퍼나 멀티플렉서를 안전하게 언래핑할 수 없으면 allowlist 항목은 자동 저장되지 않습니다.
`python3` 또는 `node` 같은 인터프리터를 allowlist에 넣는 경우, 인라인 eval이 여전히 명시적 승인을 요구하도록 `tools.exec.strictInlineEval=true`를 권장합니다. strict 모드에서 `allow-always`는 무해한 인터프리터/스크립트 호출은 저장할 수 있지만, 인라인 eval 운반자는 자동으로 저장되지 않습니다.

기본 safe bin:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep`와 `sort`는 기본 목록에 없습니다. 이를 선택적으로 활성화하는 경우,
stdin 이외 워크플로에는 명시적 allowlist 항목을 유지하세요.
safe-bin 모드의 `grep`에서는 패턴을 `-e`/`--regexp`로 제공해야 합니다. 위치 기반 패턴 형식은
모호한 위치 인수로 파일 피연산자를 우회 주입할 수 없도록 거부됩니다.

### Safe bin과 allowlist 비교

| 주제 | `tools.exec.safeBins` | Allowlist (`exec-approvals.json`) |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| 목표 | 좁은 stdin 필터 자동 허용 | 특정 실행 파일을 명시적으로 신뢰 |
| 일치 유형 | 실행 파일 이름 + safe-bin argv 정책 | 해석된 실행 파일 경로 glob 패턴 |
| 인수 범위 | safe-bin 프로필 및 리터럴 토큰 규칙으로 제한 | 경로 일치만 검사, 나머지 인수는 사용자의 책임 |
| 일반적 예 | `head`, `tail`, `tr`, `wc` | `jq`, `python3`, `node`, `ffmpeg`, 사용자 지정 CLI |
| 최적 사용처 | 파이프라인의 저위험 텍스트 변환 | 더 광범위한 동작 또는 부작용이 있는 모든 도구 |

구성 위치:

- `safeBins`는 config에서 가져옵니다(`tools.exec.safeBins` 또는 agent별 `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs`는 config에서 가져옵니다(`tools.exec.safeBinTrustedDirs` 또는 agent별 `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles`는 config에서 가져옵니다(`tools.exec.safeBinProfiles` 또는 agent별 `agents.list[].tools.exec.safeBinProfiles`). agent별 프로필 키가 전역 키를 재정의합니다.
- allowlist 항목은 호스트 로컬 `~/.openclaw/exec-approvals.json`의 `agents.<id>.allowlist` 아래에 있습니다(또는 Control UI / `openclaw approvals allowlist ...`를 통해 관리).
- `openclaw security audit`는 인터프리터/런타임 바이너리가 명시적 프로필 없이 `safeBins`에 나타나면 `tools.exec.safe_bins_interpreter_unprofiled` 경고를 표시합니다.
- `openclaw doctor --fix`는 누락된 사용자 지정 `safeBinProfiles.<bin>` 항목을 `{}`로 스캐폴드할 수 있습니다(이후 검토 및 강화 필요). 인터프리터/런타임 바이너리는 자동 스캐폴드되지 않습니다.

사용자 지정 프로필 예시:
__OC_I18N_900004__
`jq`를 `safeBins`에 명시적으로 추가하더라도 OpenClaw는 safe-bin
모드에서 `env` 빌트인을 여전히 거부하므로 `jq -n env`가 명시적 allowlist 경로나 승인 프롬프트 없이 호스트 프로세스 환경을 덤프할 수 없습니다.

## Control UI 편집

**Control UI → Nodes → Exec approvals** 카드에서 기본값, agent별
재정의, allowlist를 편집할 수 있습니다. 범위(기본값 또는 agent)를 선택하고 정책을 조정한 뒤
allowlist 패턴을 추가/제거하고 **Save**를 누르세요. UI는
패턴별 **마지막 사용** 메타데이터를 표시하므로 목록을 깔끔하게 유지할 수 있습니다.

대상 선택기는 **Gateway**(로컬 승인) 또는 **Node**를 선택합니다. 노드는
`system.execApprovals.get/set`을 광고해야 합니다(macOS 앱 또는 헤드리스 node host).
노드가 아직 exec 승인을 광고하지 않으면 해당 노드의 로컬
`~/.openclaw/exec-approvals.json`을 직접 편집하세요.

CLI: `openclaw approvals`는 gateway 또는 node 편집을 지원합니다([Approvals CLI](/cli/approvals) 참조).

## 승인 흐름

프롬프트가 필요할 때 gateway는 운영자 클라이언트로 `exec.approval.requested`를 브로드캐스트합니다.
Control UI와 macOS 앱은 이를 `exec.approval.resolve`로 처리한 다음, gateway가 승인된
요청을 node host로 전달합니다.

`host=node`의 경우 승인 요청에는 정규화된 `systemRunPlan` 페이로드가 포함됩니다. gateway는
승인된 `system.run` 요청을 전달할 때 그 계획을 명령/cwd/세션 컨텍스트의 권위 있는 기준으로 사용합니다.

이는 비동기 승인 지연 시간에서 중요합니다:

- node exec 경로는 먼저 하나의 정규화된 계획을 준비합니다
- 승인 레코드는 그 계획과 해당 바인딩 메타데이터를 저장합니다
- 승인되면 최종 전달되는 `system.run` 호출은 이후 호출자 수정 내용을 신뢰하지 않고 저장된 계획을 재사용합니다
- 승인 요청이 생성된 후 호출자가 `command`, `rawCommand`, `cwd`, `agentId`, 또는
  `sessionKey`를 변경하면 gateway는 이를 승인 불일치로 거부합니다

## 인터프리터/런타임 명령

승인 기반 인터프리터/런타임 실행은 의도적으로 보수적입니다:

- 정확한 argv/cwd/env 컨텍스트는 항상 바인딩됩니다.
- 직접 셸 스크립트 및 직접 런타임 파일 형식은 하나의 구체적인 로컬 파일 스냅샷에 최선의 노력으로 바인딩됩니다.
- 여전히 하나의 직접 로컬 파일로 해석되는 일반적인 패키지 관리자 래퍼 형식(예:
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`)은 바인딩 전에 언래핑됩니다.
- OpenClaw가 인터프리터/런타임 명령에 대해 정확히 하나의 구체적인 로컬 파일을 식별할 수 없으면(예: 패키지 스크립트, eval 형식, 런타임별 로더 체인, 또는 모호한 다중 파일 형식), 의미론적 커버리지를 주장하는 대신 승인 기반 실행을 거부합니다.
- 이러한 워크플로에는 샌드박싱, 별도의 호스트 경계, 또는 운영자가 더 넓은 런타임 의미를 수용하는 명시적 신뢰 allowlist/full 워크플로를 선호하세요.

승인이 필요한 경우 exec tool은 승인 id를 반환하고 즉시 종료합니다. 나중의 시스템 이벤트(`Exec finished` / `Exec denied`)와 이를 연관시키려면 해당 id를 사용하세요. 제한 시간 전에 결정이 도착하지 않으면 요청은 승인 시간 초과로 처리되어 거부 사유로 표시됩니다.

### 후속 전달 동작

승인된 비동기 exec가 완료되면 OpenClaw는 같은 세션으로 후속 `agent` 턴을 보냅니다.

- 유효한 외부 전달 대상이 있으면(전달 가능한 채널 + 대상 `to`), 후속 전달은 해당 채널을 사용합니다.
- 외부 대상이 없는 webchat 전용 또는 내부 세션 흐름에서는 후속 전달이 세션 전용(`deliver: false`)으로 유지됩니다.
- 호출자가 해석 가능한 외부 채널 없이 엄격한 외부 전달을 명시적으로 요청하면 요청은 `INVALID_REQUEST`로 실패합니다.
- `bestEffortDeliver`가 활성화되어 있고 해석 가능한 외부 채널이 없으면 전달은 실패 대신 세션 전용으로 강등됩니다.

확인 대화상자에는 다음이 포함됩니다:

- command + args
- cwd
- agent id
- 해석된 실행 파일 경로
- host + 정책 메타데이터

동작:

- **Allow once** → 지금 실행
- **Always allow** → allowlist에 추가 + 실행
- **Deny** → 차단

## 채팅 채널로의 승인 전달

exec 승인 프롬프트를 모든 채팅 채널(plugin 채널 포함)로 전달하고
`/approve`로 승인할 수 있습니다. 이는 일반적인 outbound 전달 파이프라인을 사용합니다.

구성:
__OC_I18N_900005__
채팅에서 응답:
__OC_I18N_900006__
`/approve` 명령은 exec 승인과 plugin 승인 둘 다 처리합니다. ID가 대기 중인 exec 승인과 일치하지 않으면 자동으로 plugin 승인도 확인합니다.

### Plugin 승인 전달

Plugin 승인 전달은 exec 승인과 같은 전달 파이프라인을 사용하지만, `approvals.plugin` 아래에
별도의 독립 설정을 가집니다. 하나를 활성화하거나 비활성화해도 다른 하나에는 영향이 없습니다.
__OC_I18N_900007__
구성 형태는 `approvals.exec`와 동일합니다: `enabled`, `mode`, `agentFilter`,
`sessionFilter`, `targets`는 모두 같은 방식으로 동작합니다.

공유 대화형 응답을 지원하는 채널은 exec 및
plugin 승인 모두에 대해 동일한 승인 버튼을 렌더링합니다. 공유 대화형 UI가 없는 채널은 `/approve`
지침이 포함된 일반 텍스트로 대체됩니다.

### 모든 채널에서 같은 채팅으로 승인

exec 또는 plugin 승인 요청이 전달 가능한 채팅 표면에서 시작되면, 이제 기본적으로 같은 채팅에서도
`/approve`로 이를 승인할 수 있습니다. 이는 기존 Web UI 및 terminal UI 흐름 외에도
Slack, Matrix, Microsoft Teams 같은 채널에 적용됩니다.

이 공유 텍스트 명령 경로는 해당 대화에 대한 일반 채널 auth 모델을 사용합니다. 원래 채팅이 이미
명령을 보내고 응답을 받을 수 있다면, 승인 요청이 대기 상태를 유지하기 위해
별도의 네이티브 전달 어댑터가 더 이상 필요하지 않습니다.

Discord와 Telegram도 같은 채팅의 `/approve`를 지원하지만, 네이티브 승인 전달이 비활성화되어 있더라도
해당 채널은 여전히 해석된 approver 목록으로 권한 부여를 수행합니다.

Gateway를 직접 호출하는 Telegram 및 기타 네이티브 승인 클라이언트의 경우,
이 fallback은 의도적으로 "승인을 찾을 수 없음" 실패에만 제한됩니다. 실제
exec 승인 거부/오류는 조용히 plugin 승인으로 재시도되지 않습니다.

### 네이티브 승인 전달

일부 채널은 네이티브 승인 클라이언트 역할도 할 수 있습니다. 네이티브 클라이언트는 공유 same-chat `/approve`
흐름 위에 approver DM, 원본 채팅 fanout 및 채널별 대화형 승인 UX를 추가합니다.

네이티브 승인 카드/버튼을 사용할 수 있는 경우, 해당 네이티브 UI가 기본
agent 대상 경로입니다. tool 결과에 채팅 승인을 사용할 수 없거나
수동 승인이 유일한 남은 경로라고 표시되지 않는 한 agent는 중복된 일반 채팅
`/approve` 명령을 추가로 출력해서는 안 됩니다.

일반 모델:

- 호스트 exec 정책은 여전히 exec 승인이 필요한지 결정합니다
- `approvals.exec`는 승인 프롬프트를 다른 채팅 대상으로 전달할지 제어합니다
- `channels.<channel>.execApprovals`는 해당 채널이 네이티브 승인 클라이언트로 동작할지 제어합니다

네이티브 승인 클라이언트는 다음 조건이 모두 참이면 DM 우선 전달을 자동 활성화합니다:

- 채널이 네이티브 승인 전달을 지원함
- 명시적 `execApprovals.approvers` 또는 해당 채널의 문서화된 fallback 소스에서 approver를 해석할 수 있음
- `channels.<channel>.execApprovals.enabled`가 설정되지 않았거나 `"auto"`임

네이티브 승인 클라이언트를 명시적으로 비활성화하려면 `enabled: false`를 설정하세요. approver가 해석될 때 강제로 활성화하려면 `enabled: true`를 설정하세요. 공개 원본 채팅 전달은
`channels.<channel>.execApprovals.target`을 통해 명시적으로 유지됩니다.

FAQ: [채팅 승인을 위해 exec 승인 구성이 두 개인 이유는 무엇인가요?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

이 네이티브 승인 클라이언트는 공유 same-chat `/approve` 흐름과 공유 승인 버튼 위에
DM 라우팅 및 선택적 채널 fanout을 추가합니다.

공유 동작:

- Slack, Matrix, Microsoft Teams 및 유사한 전달 가능한 채팅은 same-chat `/approve`에 대해 일반 채널 auth 모델을 사용합니다
- 네이티브 승인 클라이언트가 자동 활성화되면 기본 네이티브 전달 대상은 approver DM입니다
- Discord 및 Telegram에서는 해석된 approver만 승인 또는 거부할 수 있습니다
- Discord approver는 명시적(`execApprovals.approvers`)이거나 `commands.ownerAllowFrom`에서 추론될 수 있습니다
- Telegram approver는 명시적(`execApprovals.approvers`)이거나 기존 owner config(`allowFrom`, 그리고 지원되는 경우 direct-message `defaultTo`)에서 추론될 수 있습니다
- Slack approver는 명시적(`execApprovals.approvers`)이거나 `commands.ownerAllowFrom`에서 추론될 수 있습니다
- Slack 네이티브 버튼은 승인 id 종류를 보존하므로 `plugin:` id가 두 번째 Slack 로컬 fallback 계층 없이 plugin 승인을 해석할 수 있습니다
- Matrix 네이티브 DM/채널 라우팅은 exec 전용이며, Matrix plugin 승인은 공유 same-chat `/approve`와 선택적 `approvals.plugin` 전달 경로에 머뭅니다
- 요청자는 approver일 필요가 없습니다
- 원래 채팅이 이미 명령과 응답을 지원하면 `/approve`로 직접 승인할 수 있습니다
- 네이티브 Discord 승인 버튼은 승인 id 종류에 따라 라우팅됩니다: `plugin:` id는 바로 plugin 승인으로 가고, 그 외는 모두 exec 승인으로 갑니다
- 네이티브 Telegram 승인 버튼은 `/approve`와 동일한 제한된 exec→plugin fallback을 따릅니다
- 네이티브 `target`이 원본 채팅 전달을 활성화하면 승인 프롬프트에 명령 텍스트가 포함됩니다
- 대기 중인 exec 승인은 기본적으로 30분 후 만료됩니다
- 운영자 UI나 구성된 승인 클라이언트가 요청을 수락할 수 없으면 프롬프트는 `askFallback`으로 대체됩니다

Telegram의 기본값은 approver DM(`target: "dm"`)입니다. 승인 프롬프트도 원래 Telegram 채팅/토픽에 나타나도록 하려면 이를 `channel` 또는 `both`로 전환할 수 있습니다. Telegram 포럼 토픽의 경우 OpenClaw는 승인 프롬프트와 승인 후 후속 메시지 모두에 대해 토픽을 유지합니다.

참조:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS IPC 흐름
__OC_I18N_900008__
보안 참고 사항:

- Unix 소켓 권한 `0600`, 토큰은 `exec-approvals.json`에 저장됩니다.
- 동일 UID 피어 검사.
- 챌린지/응답(nonce + HMAC token + request hash) + 짧은 TTL.

## 시스템 이벤트

Exec 수명 주기는 시스템 메시지로 노출됩니다:

- `Exec running` (명령이 실행 중 알림 임계값을 초과하는 경우에만)
- `Exec finished`
- `Exec denied`

이 메시지들은 노드가 이벤트를 보고한 후 agent의 세션에 게시됩니다.
Gateway-host exec 승인은 명령이 끝날 때(그리고 선택적으로 임계값보다 오래 실행 중일 때) 동일한 수명 주기 이벤트를 발생시킵니다.
승인 게이트가 적용된 exec는 쉬운 상관관계를 위해 승인 id를 이 메시지의 `runId`로 재사용합니다.

## 승인 거부 시 동작

비동기 exec 승인이 거부되면 OpenClaw는 agent가 세션에서
같은 명령의 더 이른 실행 결과를 재사용하지 못하게 합니다. 거부 사유는
사용 가능한 명령 출력이 없다는 명시적 안내와 함께 전달되므로, agent가 새 출력이 있다고 주장하거나 이전에 성공했던 실행의 오래된 결과를 사용해 거부된 명령을 반복하지 못하게 합니다.

## 영향

- **full**은 강력하므로, 가능하면 allowlist를 선호하세요.
- **ask**는 빠른 승인을 허용하면서도 사용자를 루프 안에 유지합니다.
- agent별 allowlist는 한 agent의 승인이 다른 agent로 새어나가는 것을 방지합니다.
- 승인은 **권한 있는 발신자**의 호스트 exec 요청에만 적용됩니다. 권한 없는 발신자는 `/exec`를 실행할 수 없습니다.
- `/exec security=full`은 권한 있는 운영자를 위한 세션 수준 편의 기능이며 설계상 승인을 건너뜁니다.
  호스트 exec를 강제로 차단하려면 승인 security를 `deny`로 설정하거나 tool 정책을 통해 `exec` tool을 거부하세요.

관련 항목:

- [Exec 도구](/tools/exec)
- [Elevated mode](/tools/elevated)
- [Skills](/tools/skills)

## 관련

- [Exec](/tools/exec) — 셸 명령 실행 도구
- [샌드박싱](/ko/gateway/sandboxing) — 샌드박스 모드 및 workspace 액세스
- [보안](/ko/gateway/security) — 보안 모델 및 하드닝
- [샌드박스 vs Tool 정책 vs Elevated](/ko/gateway/sandbox-vs-tool-policy-vs-elevated) — 각각을 언제 사용할지
