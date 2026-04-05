---
read_when:
    - 접근 범위나 자동화를 넓히는 기능을 추가할 때
summary: 셸 접근 권한이 있는 AI gateway 실행을 위한 보안 고려 사항 및 위협 모델
title: 보안
x-i18n:
    generated_at: "2026-04-05T12:47:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 223deb798774952f8d0208e761e163708a322045cf4ca3df181689442ef6fcfb
    source_path: gateway/security/index.md
    workflow: 15
---

# 보안

<Warning>
**개인 비서 신뢰 모델:** 이 가이드는 gateway당 하나의 신뢰된 운영자 경계(단일 사용자/개인 비서 모델)를 가정합니다.
OpenClaw는 하나의 에이전트/gateway를 여러 적대적 사용자가 공유하는 환경에서 적대적인 멀티테넌트 보안 경계가 **아닙니다**.
혼합 신뢰 또는 적대적 사용자 운영이 필요하다면 신뢰 경계를 분리하세요(별도의 gateway + 자격 증명, 가능하면 별도의 OS 사용자/호스트도 권장).
</Warning>

**이 페이지에서 다루는 내용:** [신뢰 모델](#scope-first-personal-assistant-security-model) | [빠른 감사](#quick-check-openclaw-security-audit) | [강화된 기본 설정](#hardened-baseline-in-60-seconds) | [DM 접근 모델](#dm-access-model-pairing--allowlist--open--disabled) | [구성 강화](#configuration-hardening-examples) | [사고 대응](#incident-response)

## 먼저 범위를 정하기: 개인 비서 보안 모델

OpenClaw 보안 가이드는 **개인 비서** 배포를 가정합니다. 즉, 잠재적으로 여러 에이전트가 있더라도 하나의 신뢰된 운영자 경계만 있습니다.

- 지원되는 보안 상태: gateway당 하나의 사용자/신뢰 경계(각 경계마다 별도 OS 사용자/호스트/VPS 권장)
- 지원되지 않는 보안 경계: 상호 신뢰하지 않거나 적대적인 사용자가 하나의 공유 gateway/에이전트를 함께 사용하는 경우
- 적대적 사용자 격리가 필요하다면 신뢰 경계별로 분리하세요(별도의 gateway + 자격 증명, 이상적으로는 별도의 OS 사용자/호스트)
- 여러 신뢰하지 않는 사용자가 하나의 도구 활성화 에이전트에 메시지를 보낼 수 있다면, 그 사용자들은 해당 에이전트에 대해 동일한 위임된 도구 권한을 공유하는 것으로 간주해야 합니다.

이 페이지는 **그 모델 내부에서**의 강화를 설명합니다. 하나의 공유 gateway에서 적대적인 멀티테넌트 격리를 주장하지는 않습니다.

## 빠른 확인: `openclaw security audit`

참고: [정형 검증(보안 모델)](/security/formal-verification)

특히 구성을 변경하거나 네트워크 표면을 노출한 후에는 정기적으로 실행하세요:

```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
openclaw security audit --json
```

`security audit --fix`는 의도적으로 범위가 좁습니다. 일반적인 개방형 그룹
정책을 allowlist로 바꾸고, `logging.redactSensitive: "tools"`를 복원하며,
상태/구성/include 파일 권한을 강화하고, Windows에서는 POSIX `chmod` 대신
Windows ACL 재설정을 사용합니다.

일반적인 실수 항목(Gateway 인증 노출, 브라우저 제어 노출, elevated allowlist, 파일시스템 권한, 느슨한 exec 승인, 개방 채널 도구 노출)을 표시합니다.

OpenClaw는 제품이자 실험이기도 합니다. 실제 메시징 표면과 실제 도구에 최전선 모델 동작을 연결하고 있기 때문입니다. **“완벽하게 안전한” 설정은 없습니다.** 목표는 다음을 의식적으로 설계하는 것입니다:

- 누가 봇과 대화할 수 있는가
- 봇이 어디에서 행동할 수 있는가
- 봇이 무엇에 접근할 수 있는가

작동하는 가장 작은 접근 권한으로 시작하고, 확신이 생길수록 점진적으로 넓히세요.

### 배포 및 호스트 신뢰

OpenClaw는 호스트와 구성 경계가 신뢰된다고 가정합니다:

- 누군가가 Gateway 호스트 상태/구성(`~/.openclaw`와 `openclaw.json` 포함)을 수정할 수 있다면, 그 사람은 신뢰된 운영자로 간주해야 합니다.
- 하나의 Gateway를 여러 상호 신뢰하지 않거나 적대적인 운영자가 함께 실행하는 것은 **권장되는 설정이 아닙니다**.
- 혼합 신뢰 팀의 경우 별도의 gateway로 신뢰 경계를 나누세요(최소한 별도의 OS 사용자/호스트 권장).
- 권장 기본값: 머신/호스트(또는 VPS)당 한 명의 사용자, 그 사용자용 gateway 하나, 그리고 그 gateway 안의 하나 이상의 에이전트.
- 하나의 Gateway 인스턴스 안에서 인증된 운영자 접근은 사용자별 테넌트 역할이 아니라 신뢰된 제어 평면 역할입니다.
- 세션 식별자(`sessionKey`, 세션 ID, 라벨)는 권한 토큰이 아니라 라우팅 선택자입니다.
- 여러 사람이 하나의 도구 활성화 에이전트에 메시지를 보낼 수 있다면, 그들 각각은 동일한 권한 집합을 조작할 수 있습니다. 사용자별 세션/메모리 격리는 프라이버시에 도움이 되지만, 공유 에이전트를 사용자별 호스트 권한 경계로 바꾸지는 못합니다.

### 공유 Slack 워크스페이스: 실제 위험

“Slack의 الجميع가 봇에 메시지를 보낼 수 있다”면, 핵심 위험은 위임된 도구 권한입니다:

- 허용된 모든 발신자는 에이전트 정책 범위 내에서 도구 호출(`exec`, 브라우저, 네트워크/파일 도구)을 유도할 수 있습니다.
- 한 발신자의 프롬프트/콘텐츠 인젝션이 공유 상태, 장치 또는 출력에 영향을 미치는 작업을 유발할 수 있습니다.
- 하나의 공유 에이전트가 민감한 자격 증명/파일을 가지고 있다면, 허용된 모든 발신자가 도구 사용을 통해 유출을 유도할 가능성이 있습니다.

팀 워크플로에는 최소 도구만 가진 별도의 에이전트/gateway를 사용하고, 개인 데이터 에이전트는 비공개로 유지하세요.

### 회사 공유 에이전트: 허용 가능한 패턴

해당 에이전트를 사용하는 모든 사람이 같은 신뢰 경계(예: 하나의 회사 팀)에 있고, 에이전트가 엄격하게 업무 범위로 제한되어 있다면 허용 가능합니다.

- 전용 머신/VM/컨테이너에서 실행하세요.
- 전용 OS 사용자 + 전용 브라우저/프로필/계정을 해당 런타임에 사용하세요.
- 그 런타임을 개인 Apple/Google 계정이나 개인 비밀번호 관리자/브라우저 프로필에 로그인시키지 마세요.

개인 신원과 회사 신원을 같은 런타임에서 혼합하면 분리가 무너지고 개인 데이터 노출 위험이 증가합니다.

## Gateway와 node 신뢰 개념

Gateway와 node는 서로 다른 역할을 가진 하나의 운영자 신뢰 도메인으로 취급하세요:

- **Gateway**는 제어 평면 및 정책 표면입니다(`gateway.auth`, 도구 정책, 라우팅).
- **Node**는 해당 Gateway에 페어링된 원격 실행 표면입니다(명령, 장치 동작, 호스트 로컬 기능).
- Gateway에 인증된 호출자는 Gateway 범위에서 신뢰됩니다. 페어링 후 node 작업은 해당 node에서의 신뢰된 운영자 작업입니다.
- `sessionKey`는 라우팅/컨텍스트 선택용이지 사용자별 인증이 아닙니다.
- Exec 승인(allowlist + ask)은 운영자 의도에 대한 가드레일이지 적대적 멀티테넌트 격리가 아닙니다.
- 신뢰된 단일 운영자 설정을 위한 OpenClaw의 제품 기본값은 `gateway`/`node`에서 호스트 exec를 승인 프롬프트 없이 허용하는 것입니다(`security="full"`, `ask="off"`, 별도로 강화하지 않는 한). 이는 의도된 UX 기본값이며, 그 자체로 취약점이 아닙니다.
- Exec 승인은 정확한 요청 컨텍스트와 best-effort 직접 로컬 파일 피연산자에 바인딩됩니다. 모든 런타임/인터프리터 로더 경로를 의미론적으로 모델링하지는 않습니다. 강한 경계가 필요하면 샌드박싱과 호스트 격리를 사용하세요.

적대적 사용자 격리가 필요하면 OS 사용자/호스트 단위로 신뢰 경계를 분리하고 별도의 gateway를 실행하세요.

## 신뢰 경계 매트릭스

위험을 분류할 때 빠르게 참고할 수 있는 모델입니다:

| 경계 또는 제어 | 의미 | 흔한 오해 |
| --------------------------------------------------------- | ------------------------------------------------- | ----------------------------------------------------------------------------- |
| `gateway.auth` (token/password/trusted-proxy/device auth) | gateway API에 대한 호출자 인증 | “보안이 되려면 모든 프레임에 사용자별 메시지 서명이 필요하다” |
| `sessionKey` | 컨텍스트/세션 선택용 라우팅 키 | “세션 키는 사용자 인증 경계다” |
| 프롬프트/콘텐츠 가드레일 | 모델 악용 위험 감소 | “프롬프트 인젝션만으로 인증 우회가 증명된다” |
| `canvas.eval` / browser evaluate | 활성화 시 의도된 운영자 기능 | “모든 JS eval primitive는 이 신뢰 모델에서 자동으로 취약점이다” |
| 로컬 TUI `!` 셸 | 명시적인 운영자 트리거 로컬 실행 | “로컬 셸 편의 명령은 원격 인젝션이다” |
| Node 페어링 및 node 명령 | 페어링된 장치에 대한 운영자 수준 원격 실행 | “원격 장치 제어는 기본적으로 신뢰되지 않는 사용자 접근으로 취급해야 한다” |

## 설계상 취약점이 아닌 것들

다음 패턴은 자주 보고되지만, 실제 경계 우회가 입증되지 않으면 보통 조치 없음으로 종료됩니다:

- 정책/auth/sandbox 우회 없이 프롬프트 인젝션만으로 이루어진 체인
- 하나의 공유 호스트/구성에서 적대적 멀티테넌트 운영을 가정하는 주장
- 공유 gateway 설정에서 정상적인 운영자 읽기 경로(예: `sessions.list`/`sessions.preview`/`chat.history`)를 IDOR로 분류하는 주장
- localhost 전용 배포에서의 지적(예: loopback 전용 gateway에 대한 HSTS)
- 이 저장소에 존재하지 않는 인바운드 경로에 대한 Discord inbound webhook 서명 관련 보고
- node pairing 메타데이터를 `system.run`에 대한 숨겨진 두 번째 per-command 승인 계층으로 보는 보고. 실제 실행 경계는 gateway의 전역 node 명령 정책 + node 자체의 exec 승인입니다.
- `sessionKey`를 인증 토큰으로 간주하는 “per-user authorization 누락” 지적

## 연구자 사전 점검 체크리스트

GHSA를 열기 전에 다음을 모두 확인하세요:

1. 재현이 최신 `main` 또는 최신 릴리스에서 여전히 동작한다.
2. 보고서에 정확한 코드 경로(`file`, 함수, 라인 범위)와 테스트한 버전/커밋이 포함되어 있다.
3. 영향이 문서화된 신뢰 경계를 넘는다(프롬프트 인젝션만이 아님).
4. 주장이 [Out of Scope](https://github.com/openclaw/openclaw/blob/main/SECURITY.md#out-of-scope)에 포함되어 있지 않다.
5. 기존 advisory에 중복이 없는지 확인했다(해당 시 정식 GHSA 재사용).
6. 배포 가정이 명확하다(loopback/local vs 노출, 신뢰된 vs 신뢰되지 않는 운영자).

## 60초 만에 강화된 기본 설정

먼저 이 기본 설정을 사용하고, 이후 신뢰된 에이전트별로 도구를 선택적으로 다시 활성화하세요:

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    auth: { mode: "token", token: "replace-with-long-random-token" },
  },
  session: {
    dmScope: "per-channel-peer",
  },
  tools: {
    profile: "messaging",
    deny: ["group:automation", "group:runtime", "group:fs", "sessions_spawn", "sessions_send"],
    fs: { workspaceOnly: true },
    exec: { security: "deny", ask: "always" },
    elevated: { enabled: false },
  },
  channels: {
    whatsapp: { dmPolicy: "pairing", groups: { "*": { requireMention: true } } },
  },
}
```

이렇게 하면 Gateway를 local 전용으로 유지하고, DM을 격리하며, 기본적으로 제어 평면/런타임 도구를 비활성화합니다.

## 공유 inbox 빠른 규칙

둘 이상의 사람이 봇에 DM을 보낼 수 있다면:

- `session.dmScope: "per-channel-peer"`로 설정하세요(멀티 계정 채널이라면 `"per-account-channel-peer"`).
- `dmPolicy: "pairing"` 또는 엄격한 allowlist를 유지하세요.
- 공유 DM과 광범위한 도구 접근을 절대 결합하지 마세요.
- 이는 협업/공유 inbox를 강화해 주지만, 사용자가 호스트/구성 쓰기 접근을 공유하는 경우 적대적 공동 테넌트 격리를 위해 설계된 것은 아닙니다.

## 컨텍스트 가시성 모델

OpenClaw는 두 가지 개념을 분리합니다:

- **트리거 권한**: 누가 에이전트를 트리거할 수 있는가(`dmPolicy`, `groupPolicy`, allowlist, mention gate)
- **컨텍스트 가시성**: 어떤 보조 컨텍스트가 모델 입력에 주입되는가(답장 본문, 인용 텍스트, 스레드 기록, 전달 메타데이터)

Allowlists는 트리거와 명령 권한을 제어합니다. `contextVisibility` 설정은 보조 컨텍스트(인용 답장, 스레드 루트, 가져온 기록)를 활성 allowlist 검사에 따라 어떻게 필터링할지 제어합니다:

- `contextVisibility: "all"`(기본값): 보조 컨텍스트를 받은 그대로 유지
- `contextVisibility: "allowlist"`: 활성 allowlist 검사로 허용된 발신자만 보조 컨텍스트에 포함
- `contextVisibility: "allowlist_quote"`: `allowlist`처럼 동작하지만 하나의 명시적 인용 답장은 유지

`contextVisibility`는 채널별 또는 룸/대화별로 설정하세요. 설정 세부 사항은 [Group Chats](/channels/groups#context-visibility)를 참조하세요.

Advisory 분류 가이드:

- “모델이 allowlist에 없는 발신자의 인용 또는 기록 텍스트를 볼 수 있다”는 주장만으로는 인증 또는 sandbox 경계 우회가 아니라 `contextVisibility`로 다룰 수 있는 강화 이슈입니다.
- 보안 영향이 있다고 보려면, 보고서는 여전히 인증, 정책, sandbox, 승인 또는 다른 문서화된 경계 우회를 입증해야 합니다.

## 감사가 확인하는 항목(상위 수준)

- **인바운드 접근**(DM 정책, 그룹 정책, allowlist): 낯선 사람이 봇을 트리거할 수 있는가?
- **도구 폭발 반경**(elevated 도구 + 개방된 방): 프롬프트 인젝션이 셸/파일/네트워크 작업으로 이어질 수 있는가?
- **Exec 승인 드리프트**(`security=full`, `autoAllowSkills`, `strictInlineEval` 없는 인터프리터 allowlist): 호스트 exec 가드레일이 여전히 의도대로 작동하는가?
  - `security="full"`은 광범위한 상태 경고이지 버그의 증거가 아닙니다. 이는 신뢰된 개인 비서 설정을 위한 선택된 기본값이며, 위협 모델에서 승인 또는 allowlist 가드레일이 필요할 때만 강화하세요.
- **네트워크 노출**(Gateway bind/auth, Tailscale Serve/Funnel, 약하거나 짧은 인증 토큰)
- **브라우저 제어 노출**(원격 node, relay 포트, 원격 CDP 엔드포인트)
- **로컬 디스크 위생**(권한, 심볼릭 링크, config include, “동기화 폴더” 경로)
- **Plugins**(명시적 allowlist 없이 확장이 존재)
- **정책 드리프트/오구성**(sandbox Docker 설정이 있지만 sandbox mode가 꺼져 있음; 일치가 정확한 명령 이름에만 적용되고 셸 텍스트는 보지 않기 때문에 `gateway.nodes.denyCommands` 패턴이 효과가 없음(예: `system.run`); 위험한 `gateway.nodes.allowCommands` 항목; 전역 `tools.profile="minimal"`이 에이전트별 profile로 재정의됨; 확장 plugin 도구가 느슨한 도구 정책 아래 도달 가능)
- **런타임 기대 드리프트**(예: 암묵적 exec가 여전히 `sandbox`라고 가정하지만 `tools.exec.host` 기본값이 이제 `auto`인 경우, 또는 sandbox mode가 꺼진 상태에서 `tools.exec.host="sandbox"`를 명시적으로 설정한 경우)
- **모델 위생**(구성된 모델이 레거시처럼 보일 경우 경고, 강제 차단은 아님)

`--deep`를 사용하면 OpenClaw는 best-effort 실시간 Gateway 프로브도 시도합니다.

## 자격 증명 저장소 맵

접근 감사를 하거나 무엇을 백업할지 결정할 때 참고하세요:

- **WhatsApp**: `~/.openclaw/credentials/whatsapp/<accountId>/creds.json`
- **Telegram bot token**: config/env 또는 `channels.telegram.tokenFile`(일반 파일만 허용, 심볼릭 링크 거부)
- **Discord bot token**: config/env 또는 SecretRef(env/file/exec provider)
- **Slack 토큰**: config/env (`channels.slack.*`)
- **페어링 allowlist**:
  - `~/.openclaw/credentials/<channel>-allowFrom.json`(기본 계정)
  - `~/.openclaw/credentials/<channel>-<accountId>-allowFrom.json`(비기본 계정)
- **모델 인증 프로필**: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- **파일 기반 비밀 페이로드(선택 사항)**: `~/.openclaw/secrets.json`
- **레거시 OAuth 가져오기**: `~/.openclaw/credentials/oauth.json`

## 보안 감사 체크리스트

감사 결과에 항목이 표시되면 다음 우선순위로 처리하세요:

1. **“open” + 도구 활성화 조합**: 먼저 DM/그룹을 잠그고(페어링/allowlist), 그다음 도구 정책/sandboxing을 강화하세요.
2. **공용 네트워크 노출**(LAN bind, Funnel, 인증 없음): 즉시 수정하세요.
3. **브라우저 제어 원격 노출**: 운영자 접근처럼 취급하세요(tailnet 전용, 의도적 node 페어링, 공용 노출 회피).
4. **권한**: 상태/구성/자격 증명/인증 파일이 그룹/전체 읽기 가능하지 않도록 하세요.
5. **Plugins/확장**: 명시적으로 신뢰하는 것만 로드하세요.
6. **모델 선택**: 도구가 있는 봇에는 최신, 지시 강화형 모델을 우선하세요.

## 보안 감사 용어집

실제 배포에서 가장 자주 보게 되는 고신호 `checkId` 값들입니다(전체 목록은 아님):

| `checkId` | 심각도 | 중요한 이유 | 주요 수정 키/경로 | 자동 수정 |
| ------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------- | -------- |
| `fs.state_dir.perms_world_writable` | critical | 다른 사용자/프로세스가 전체 OpenClaw 상태를 수정할 수 있음 | `~/.openclaw`의 파일시스템 권한 | yes |
| `fs.state_dir.perms_group_writable` | warn | 그룹 사용자가 전체 OpenClaw 상태를 수정할 수 있음 | `~/.openclaw`의 파일시스템 권한 | yes |
| `fs.state_dir.perms_readable` | warn | 상태 디렉터리를 다른 사람이 읽을 수 있음 | `~/.openclaw`의 파일시스템 권한 | yes |
| `fs.state_dir.symlink` | warn | 상태 디렉터리 대상이 다른 신뢰 경계가 됨 | 상태 디렉터리 파일시스템 레이아웃 | no |
| `fs.config.perms_writable` | critical | 다른 사람이 인증/도구 정책/구성을 변경할 수 있음 | `~/.openclaw/openclaw.json`의 파일시스템 권한 | yes |
| `fs.config.symlink` | warn | 구성 대상이 다른 신뢰 경계가 됨 | 구성 파일 파일시스템 레이아웃 | no |
| `fs.config.perms_group_readable` | warn | 그룹 사용자가 구성 토큰/설정을 읽을 수 있음 | 구성 파일 파일시스템 권한 | yes |
| `fs.config.perms_world_readable` | critical | 구성에서 토큰/설정이 노출될 수 있음 | 구성 파일 파일시스템 권한 | yes |
| `fs.config_include.perms_writable` | critical | 구성 include 파일을 다른 사람이 수정할 수 있음 | `openclaw.json`에서 참조하는 include 파일 권한 | yes |
| `fs.config_include.perms_group_readable` | warn | 그룹 사용자가 포함된 비밀/설정을 읽을 수 있음 | `openclaw.json`에서 참조하는 include 파일 권한 | yes |
| `fs.config_include.perms_world_readable` | critical | 포함된 비밀/설정이 전체 읽기 가능함 | `openclaw.json`에서 참조하는 include 파일 권한 | yes |
| `fs.auth_profiles.perms_writable` | critical | 다른 사람이 저장된 모델 자격 증명을 주입 또는 교체할 수 있음 | `agents/<agentId>/agent/auth-profiles.json` 권한 | yes |
| `fs.auth_profiles.perms_readable` | warn | 다른 사람이 API 키와 OAuth 토큰을 읽을 수 있음 | `agents/<agentId>/agent/auth-profiles.json` 권한 | yes |
| `fs.credentials_dir.perms_writable` | critical | 다른 사람이 채널 페어링/자격 증명 상태를 수정할 수 있음 | `~/.openclaw/credentials`의 파일시스템 권한 | yes |
| `fs.credentials_dir.perms_readable` | warn | 다른 사람이 채널 자격 증명 상태를 읽을 수 있음 | `~/.openclaw/credentials`의 파일시스템 권한 | yes |
| `fs.sessions_store.perms_readable` | warn | 다른 사람이 세션 transcript/메타데이터를 읽을 수 있음 | 세션 저장소 권한 | yes |
| `fs.log_file.perms_readable` | warn | 다른 사람이 redaction되었지만 여전히 민감한 로그를 읽을 수 있음 | gateway 로그 파일 권한 | yes |
| `fs.synced_dir` | warn | iCloud/Dropbox/Drive의 상태/구성은 토큰/transcript 노출 범위를 넓힘 | config/state를 동기화 폴더 밖으로 이동 | no |
| `gateway.bind_no_auth` | critical | 인증 없이 원격 bind | `gateway.bind`, `gateway.auth.*` | no |
| `gateway.loopback_no_auth` | critical | reverse-proxied loopback이 인증되지 않게 될 수 있음 | `gateway.auth.*`, 프록시 설정 | no |
| `gateway.trusted_proxies_missing` | warn | reverse-proxy 헤더가 있지만 신뢰되지 않음 | `gateway.trustedProxies` | no |
| `gateway.http.no_auth` | warn/critical | `auth.mode="none"`인 상태에서 Gateway HTTP API 접근 가능 | `gateway.auth.mode`, `gateway.http.endpoints.*` | no |
| `gateway.http.session_key_override_enabled` | info | HTTP API 호출자가 `sessionKey`를 재정의할 수 있음 | `gateway.http.allowSessionKeyOverride` | no |
| `gateway.tools_invoke_http.dangerous_allow` | warn/critical | HTTP API를 통해 위험한 도구를 다시 활성화 | `gateway.tools.allow` | no |
| `gateway.nodes.allow_commands_dangerous` | warn/critical | 고영향 node 명령 활성화(카메라/화면/연락처/캘린더/SMS) | `gateway.nodes.allowCommands` | no |
| `gateway.nodes.deny_commands_ineffective` | warn | 패턴형 deny 항목이 셸 텍스트나 그룹과 일치하지 않음 | `gateway.nodes.denyCommands` | no |
| `gateway.tailscale_funnel` | critical | 공용 인터넷 노출 | `gateway.tailscale.mode` | no |
| `gateway.tailscale_serve` | info | Tailscale Serve를 통한 tailnet 노출이 활성화됨 | `gateway.tailscale.mode` | no |
| `gateway.control_ui.allowed_origins_required` | critical | non-loopback Control UI에 명시적 브라우저 origin allowlist가 없음 | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.allowed_origins_wildcard` | warn/critical | `allowedOrigins=["*"]`는 브라우저 origin allowlist를 비활성화함 | `gateway.controlUi.allowedOrigins` | no |
| `gateway.control_ui.host_header_origin_fallback` | warn/critical | Host-header origin fallback 활성화(DNS rebinding 강화 저하) | `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback` | no |
| `gateway.control_ui.insecure_auth` | warn | insecure-auth 호환 토글이 활성화됨 | `gateway.controlUi.allowInsecureAuth` | no |
| `gateway.control_ui.device_auth_disabled` | critical | 장치 신원 확인이 비활성화됨 | `gateway.controlUi.dangerouslyDisableDeviceAuth` | no |
| `gateway.real_ip_fallback_enabled` | warn/critical | `X-Real-IP` 대체를 신뢰하면 프록시 오구성 시 source-IP spoofing 가능 | `gateway.allowRealIpFallback`, `gateway.trustedProxies` | no |
| `gateway.token_too_short` | warn | 짧은 공유 토큰은 brute force가 쉬움 | `gateway.auth.token` | no |
| `gateway.auth_no_rate_limit` | warn | 인증이 노출되었지만 rate limiting이 없으면 brute-force 위험 증가 | `gateway.auth.rateLimit` | no |
| `gateway.trusted_proxy_auth` | critical | proxy 신원이 이제 인증 경계가 됨 | `gateway.auth.mode="trusted-proxy"` | no |
| `gateway.trusted_proxy_no_proxies` | critical | trusted-proxy auth인데 trusted proxy IP가 없음 | `gateway.trustedProxies` | no |
| `gateway.trusted_proxy_no_user_header` | critical | trusted-proxy auth가 사용자 신원을 안전하게 해석할 수 없음 | `gateway.auth.trustedProxy.userHeader` | no |
| `gateway.trusted_proxy_no_allowlist` | warn | trusted-proxy auth가 인증된 모든 업스트림 사용자를 허용함 | `gateway.auth.trustedProxy.allowUsers` | no |
| `gateway.probe_auth_secretref_unavailable` | warn | deep probe가 이 명령 경로에서 auth SecretRef를 해석하지 못함 | deep-probe auth source / SecretRef availability | no |
| `gateway.probe_failed` | warn/critical | live Gateway probe 실패 | gateway reachability/auth | no |
| `discovery.mdns_full_mode` | warn/critical | mDNS full mode가 로컬 네트워크에 `cliPath`/`sshPort` 메타데이터를 광고함 | `discovery.mdns.mode`, `gateway.bind` | no |
| `config.insecure_or_dangerous_flags` | warn | insecure/dangerous 디버그 플래그가 활성화됨 | 여러 키(세부 내용 참조) | no |
| `config.secrets.gateway_password_in_config` | warn | gateway 비밀번호가 config에 직접 저장됨 | `gateway.auth.password` | no |
| `config.secrets.hooks_token_in_config` | warn | hook bearer token이 config에 직접 저장됨 | `hooks.token` | no |
| `hooks.token_reuse_gateway_token` | critical | hook ingress token이 Gateway auth도 해제함 | `hooks.token`, `gateway.auth.token` | no |
| `hooks.token_too_short` | warn | hook ingress brute force가 쉬움 | `hooks.token` | no |
| `hooks.default_session_key_unset` | warn | hook agent run이 생성된 per-request 세션으로 퍼져 나감 | `hooks.defaultSessionKey` | no |
| `hooks.allowed_agent_ids_unrestricted` | warn/critical | 인증된 hook 호출자가 모든 구성된 에이전트로 라우팅 가능 | `hooks.allowedAgentIds` | no |
| `hooks.request_session_key_enabled` | warn/critical | 외부 호출자가 sessionKey를 선택할 수 있음 | `hooks.allowRequestSessionKey` | no |
| `hooks.request_session_key_prefixes_missing` | warn/critical | 외부 session key 형태에 제한이 없음 | `hooks.allowedSessionKeyPrefixes` | no |
| `hooks.path_root` | critical | hook path가 `/`여서 ingress 충돌/오라우팅이 쉬움 | `hooks.path` | no |
| `hooks.installs_unpinned_npm_specs` | warn | hook 설치 기록이 불변 npm spec에 고정되지 않음 | hook install metadata | no |
| `hooks.installs_missing_integrity` | warn | hook 설치 기록에 integrity 메타데이터가 없음 | hook install metadata | no |
| `hooks.installs_version_drift` | warn | hook 설치 기록이 설치된 패키지와 어긋남 | hook install metadata | no |
| `logging.redact_off` | warn | 민감한 값이 로그/상태에 노출됨 | `logging.redactSensitive` | yes |
| `browser.control_invalid_config` | warn | 브라우저 제어 구성이 런타임 전에 유효하지 않음 | `browser.*` | no |
| `browser.control_no_auth` | critical | 인증 없이 브라우저 제어 노출 | `gateway.auth.*` | no |
| `browser.remote_cdp_http` | warn | plain HTTP 원격 CDP는 전송 암호화가 없음 | 브라우저 프로필 `cdpUrl` | no |
| `browser.remote_cdp_private_host` | warn | 원격 CDP가 private/internal 호스트를 대상으로 함 | 브라우저 프로필 `cdpUrl`, `browser.ssrfPolicy.*` | no |
| `sandbox.docker_config_mode_off` | warn | sandbox Docker 구성이 있지만 비활성 상태 | `agents.*.sandbox.mode` | no |
| `sandbox.bind_mount_non_absolute` | warn | 상대 bind mount는 예측 불가능하게 해석될 수 있음 | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_bind_mount` | critical | sandbox bind mount가 차단된 시스템, 자격 증명, Docker socket 경로를 대상으로 함 | `agents.*.sandbox.docker.binds[]` | no |
| `sandbox.dangerous_network_mode` | critical | sandbox Docker network가 `host` 또는 `container:*` namespace join 모드를 사용함 | `agents.*.sandbox.docker.network` | no |
| `sandbox.dangerous_seccomp_profile` | critical | sandbox seccomp profile이 컨테이너 격리를 약화함 | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.dangerous_apparmor_profile` | critical | sandbox AppArmor profile이 컨테이너 격리를 약화함 | `agents.*.sandbox.docker.securityOpt` | no |
| `sandbox.browser_cdp_bridge_unrestricted` | warn | sandbox browser bridge가 source-range 제한 없이 노출됨 | `sandbox.browser.cdpSourceRange` | no |
| `sandbox.browser_container.non_loopback_publish` | critical | 기존 browser 컨테이너가 non-loopback 인터페이스에 CDP를 publish함 | browser sandbox container publish config | no |
| `sandbox.browser_container.hash_label_missing` | warn | 기존 browser 컨테이너가 현재 config-hash label보다 이전 것임 | `openclaw sandbox recreate --browser --all` | no |
| `sandbox.browser_container.hash_epoch_stale` | warn | 기존 browser 컨테이너가 현재 browser config epoch보다 이전 것임 | `openclaw sandbox recreate --browser --all` | no |
| `tools.exec.host_sandbox_no_sandbox_defaults` | warn | `exec host=sandbox`는 sandbox가 꺼져 있으면 fail closed함 | `tools.exec.host`, `agents.defaults.sandbox.mode` | no |
| `tools.exec.host_sandbox_no_sandbox_agents` | warn | 에이전트별 `exec host=sandbox`는 sandbox가 꺼져 있으면 fail closed함 | `agents.list[].tools.exec.host`, `agents.list[].sandbox.mode` | no |
| `tools.exec.security_full_configured` | warn/critical | 호스트 exec가 `security="full"`로 실행 중 | `tools.exec.security`, `agents.list[].tools.exec.security` | no |
| `tools.exec.auto_allow_skills_enabled` | warn | exec 승인이 Skill bin을 암묵적으로 신뢰함 | `~/.openclaw/exec-approvals.json` | no |
| `tools.exec.allowlist_interpreter_without_strict_inline_eval` | warn | 인터프리터 allowlist가 강제 재승인 없이 inline eval을 허용함 | `tools.exec.strictInlineEval`, `agents.list[].tools.exec.strictInlineEval`, exec approvals allowlist | no |
| `tools.exec.safe_bins_interpreter_unprofiled` | warn | `safeBins`의 인터프리터/런타임 bin이 명시적 profile 없이 exec 위험을 넓힘 | `tools.exec.safeBins`, `tools.exec.safeBinProfiles`, `agents.list[].tools.exec.*` | no |
| `tools.exec.safe_bins_broad_behavior` | warn | `safeBins`의 넓은 동작 도구가 저위험 stdin-filter 신뢰 모델을 약화함 | `tools.exec.safeBins`, `agents.list[].tools.exec.safeBins` | no |
| `tools.exec.safe_bin_trusted_dirs_risky` | warn | `safeBinTrustedDirs`에 변경 가능하거나 위험한 디렉터리가 포함됨 | `tools.exec.safeBinTrustedDirs`, `agents.list[].tools.exec.safeBinTrustedDirs` | no |
| `skills.workspace.symlink_escape` | warn | 워크스페이스 `skills/**/SKILL.md`가 워크스페이스 루트 밖으로 해석됨(심볼릭 링크 체인 드리프트) | 워크스페이스 `skills/**` 파일시스템 상태 | no |
| `plugins.extensions_no_allowlist` | warn | 명시적 plugin allowlist 없이 확장이 설치됨 | `plugins.allowlist` | no |
| `plugins.installs_unpinned_npm_specs` | warn | plugin 설치 기록이 불변 npm spec에 고정되지 않음 | plugin install metadata | no |
| `plugins.installs_missing_integrity` | warn | plugin 설치 기록에 integrity 메타데이터가 없음 | plugin install metadata | no |
| `plugins.installs_version_drift` | warn | plugin 설치 기록이 설치된 패키지와 어긋남 | plugin install metadata | no |
| `plugins.code_safety` | warn/critical | plugin 코드 스캔에서 의심스럽거나 위험한 패턴 발견 | plugin 코드 / 설치 소스 | no |
| `plugins.code_safety.entry_path` | warn | plugin entry path가 숨김 또는 `node_modules` 위치를 가리킴 | plugin manifest `entry` | no |
| `plugins.code_safety.entry_escape` | critical | plugin entry가 plugin 디렉터리 밖으로 벗어남 | plugin manifest `entry` | no |
| `plugins.code_safety.scan_failed` | warn | plugin 코드 스캔을 완료할 수 없음 | plugin extension path / scan environment | no |
| `skills.code_safety` | warn/critical | Skill 설치 메타데이터/코드에 의심스럽거나 위험한 패턴이 있음 | Skill 설치 소스 | no |
| `skills.code_safety.scan_failed` | warn | Skill 코드 스캔을 완료할 수 없음 | Skill scan environment | no |
| `security.exposure.open_channels_with_exec` | warn/critical | 공유/공개 룸이 exec 활성화 에이전트에 접근 가능 | `channels.*.dmPolicy`, `channels.*.groupPolicy`, `tools.exec.*`, `agents.list[].tools.exec.*` | no |
| `security.exposure.open_groups_with_elevated` | critical | open group + elevated 도구는 고영향 프롬프트 인젝션 경로를 만듦 | `channels.*.groupPolicy`, `tools.elevated.*` | no |
| `security.exposure.open_groups_with_runtime_or_fs` | critical/warn | open group이 sandbox/workspace 가드 없이 명령/파일 도구에 접근 가능 | `channels.*.groupPolicy`, `tools.profile/deny`, `tools.fs.workspaceOnly`, `agents.*.sandbox.mode` | no |
| `security.trust_model.multi_user_heuristic` | warn | 구성이 multi-user처럼 보이지만 gateway 신뢰 모델은 개인 비서임 | 신뢰 경계 분리, 또는 공유 사용자 강화(`sandbox.mode`, tool deny/workspace scoping) | no |
| `tools.profile_minimal_overridden` | warn | 에이전트 재정의가 전역 minimal profile을 우회함 | `agents.list[].tools.profile` | no |
| `plugins.tools_reachable_permissive_policy` | warn | 느슨한 정책에서 확장 도구에 도달 가능 | `tools.profile` + tool allow/deny | no |
| `models.legacy` | warn | 레거시 모델 패밀리가 여전히 구성됨 | 모델 선택 | no |
| `models.weak_tier` | warn | 구성된 모델이 현재 권장 티어보다 낮음 | 모델 선택 | no |
| `models.small_params` | critical/info | 작은 모델 + 안전하지 않은 도구 표면은 인젝션 위험을 높임 | 모델 선택 + sandbox/tool policy | no |
| `summary.attack_surface` | info | 인증, 채널, 도구, 노출 상태의 롤업 요약 | 여러 키(세부 내용 참조) | no |

## HTTP를 통한 Control UI

Control UI는 장치 신원을 생성하기 위해 **보안 컨텍스트**(HTTPS 또는 localhost)가 필요합니다.
`gateway.controlUi.allowInsecureAuth`는 로컬 호환 토글입니다:

- localhost에서는 페이지가 비보안 HTTP로 로드될 때 장치 신원 없이도 Control UI 인증을 허용합니다.
- 페어링 검사를 우회하지는 않습니다.
- 원격(non-localhost) 장치 신원 요구 사항을 완화하지도 않습니다.

HTTPS(Tailscale Serve) 또는 `127.0.0.1`에서 UI를 여는 것을 권장합니다.

비상 상황에서만 `gateway.controlUi.dangerouslyDisableDeviceAuth`를 사용해 장치 신원 검사를 완전히 비활성화할 수 있습니다. 이는 심각한 보안 저하이므로, 적극적으로 디버깅 중이고 빠르게 되돌릴 수 있을 때만 사용하세요.

이러한 dangerous 플래그와 별도로, 성공적인 `gateway.auth.mode: "trusted-proxy"`는 장치 신원 없이도 **운영자** Control UI 세션을 허용할 수 있습니다. 이는 의도된 auth-mode 동작이지 `allowInsecureAuth` 지름길이 아니며, node-role Control UI 세션으로 확장되지도 않습니다.

`openclaw security audit`는 이 설정이 활성화되면 경고합니다.

## insecure 또는 dangerous 플래그 요약

`openclaw security audit`는 알려진 insecure/dangerous 디버그 스위치가 활성화되면
`config.insecure_or_dangerous_flags`를 포함합니다. 현재 이 검사는 다음을 집계합니다:

- `gateway.controlUi.allowInsecureAuth=true`
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`
- `gateway.controlUi.dangerouslyDisableDeviceAuth=true`
- `hooks.gmail.allowUnsafeExternalContent=true`
- `hooks.mappings[<index>].allowUnsafeExternalContent=true`
- `tools.exec.applyPatch.workspaceOnly=false`
- `plugins.entries.acpx.config.permissionMode=approve-all`

OpenClaw config schema에 정의된 전체 `dangerous*` / `dangerously*` 구성 키:

- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback`
- `gateway.controlUi.dangerouslyDisableDeviceAuth`
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork`
- `channels.discord.dangerouslyAllowNameMatching`
- `channels.discord.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.slack.dangerouslyAllowNameMatching`
- `channels.slack.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.googlechat.dangerouslyAllowNameMatching`
- `channels.googlechat.accounts.<accountId>.dangerouslyAllowNameMatching`
- `channels.msteams.dangerouslyAllowNameMatching`
- `channels.synology-chat.dangerouslyAllowNameMatching` (extension channel)
- `channels.synology-chat.accounts.<accountId>.dangerouslyAllowNameMatching` (extension channel)
- `channels.synology-chat.dangerouslyAllowInheritedWebhookPath` (extension channel)
- `channels.zalouser.dangerouslyAllowNameMatching` (extension channel)
- `channels.zalouser.accounts.<accountId>.dangerouslyAllowNameMatching` (extension channel)
- `channels.irc.dangerouslyAllowNameMatching` (extension channel)
- `channels.irc.accounts.<accountId>.dangerouslyAllowNameMatching` (extension channel)
- `channels.mattermost.dangerouslyAllowNameMatching` (extension channel)
- `channels.mattermost.accounts.<accountId>.dangerouslyAllowNameMatching` (extension channel)
- `channels.telegram.network.dangerouslyAllowPrivateNetwork`
- `channels.telegram.accounts.<accountId>.network.dangerouslyAllowPrivateNetwork`
- `agents.defaults.sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.defaults.sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowReservedContainerTargets`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowExternalBindSources`
- `agents.list[<index>].sandbox.docker.dangerouslyAllowContainerNamespaceJoin`

## Reverse Proxy 구성

Gateway를 reverse proxy(nginx, Caddy, Traefik 등) 뒤에서 실행한다면,
올바른 forwarded-client IP 처리를 위해 `gateway.trustedProxies`를 구성하세요.

Gateway는 **trustedProxies에 없는** 주소로부터 프록시 헤더를 감지하면 해당 연결을 로컬 클라이언트로 취급하지 않습니다. gateway auth가 비활성화되어 있다면 그 연결은 거부됩니다. 이는 프록시된 연결이 localhost에서 온 것처럼 보이면서 자동 신뢰를 받는 인증 우회를 방지합니다.

`gateway.trustedProxies`는 `gateway.auth.mode: "trusted-proxy"`에도 사용되지만, 그 인증 모드는 더 엄격합니다:

- trusted-proxy auth는 **loopback-source proxy에서 fail closed**합니다
- 같은 호스트의 loopback reverse proxy는 여전히 `gateway.trustedProxies`를 사용해 local client 감지 및 forwarded IP 처리를 할 수 있습니다
- 같은 호스트의 loopback reverse proxy에는 `gateway.auth.mode: "trusted-proxy"` 대신 token/password auth를 사용하세요

```yaml
gateway:
  trustedProxies:
    - "10.0.0.1" # reverse proxy IP
  # Optional. Default false.
  # Only enable if your proxy cannot provide X-Forwarded-For.
  allowRealIpFallback: false
  auth:
    mode: password
    password: ${OPENCLAW_GATEWAY_PASSWORD}
```

`trustedProxies`가 구성되면 Gateway는 `X-Forwarded-For`를 사용해 클라이언트 IP를 결정합니다. `gateway.allowRealIpFallback: true`를 명시적으로 설정하지 않는 한 `X-Real-IP`는 기본적으로 무시됩니다.

좋은 reverse proxy 동작(들어오는 전달 헤더 덮어쓰기):

```nginx
proxy_set_header X-Forwarded-For $remote_addr;
proxy_set_header X-Real-IP $remote_addr;
```

나쁜 reverse proxy 동작(신뢰되지 않은 전달 헤더 추가/보존):

```nginx
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
```

## HSTS 및 origin 참고

- OpenClaw gateway는 local/loopback 우선입니다. reverse proxy에서 TLS를 종료한다면, 해당 프록시 앞 HTTPS 도메인에서 HSTS를 설정하세요.
- gateway 자체가 HTTPS를 종료한다면 `gateway.http.securityHeaders.strictTransportSecurity`를 설정해 OpenClaw 응답에서 HSTS 헤더를 보낼 수 있습니다.
- 자세한 배포 가이드는 [Trusted Proxy Auth](/gateway/trusted-proxy-auth#tls-termination-and-hsts)에 있습니다.
- non-loopback Control UI 배포에는 기본적으로 `gateway.controlUi.allowedOrigins`가 필요합니다.
- `gateway.controlUi.allowedOrigins: ["*"]`는 강화된 기본값이 아니라 명시적 전체 허용 브라우저 origin 정책입니다. 엄격히 통제된 로컬 테스트가 아니라면 피하세요.
- loopback에서의 브라우저 origin 인증 실패도 일반 loopback 예외가 활성화되어 있더라도 여전히 rate limit가 적용되지만, lockout 키는 하나의 공유 localhost 버킷이 아니라 정규화된 `Origin` 값별로 범위가 지정됩니다.
- `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true`는 Host-header origin fallback 모드를 활성화합니다. 운영자가 선택한 위험한 정책으로 취급하세요.
- DNS rebinding과 proxy-host header 동작은 배포 강화 이슈로 취급하세요. `trustedProxies`를 엄격하게 유지하고 gateway를 공용 인터넷에 직접 노출하지 마세요.

## 로컬 세션 로그는 디스크에 저장됩니다

OpenClaw는 세션 transcript를 디스크의 `~/.openclaw/agents/<agentId>/sessions/*.jsonl` 아래에 저장합니다.
이것은 세션 연속성과(선택적으로) 세션 메모리 인덱싱을 위해 필요하지만,
동시에 **파일시스템 접근 권한이 있는 모든 프로세스/사용자가 해당 로그를 읽을 수 있다**는 뜻이기도 합니다.
디스크 접근을 신뢰 경계로 취급하고 `~/.openclaw` 권한을 엄격히 제한하세요(아래 감사 섹션 참조). 에이전트 간 더 강한 격리가 필요하면 별도의 OS 사용자 또는 별도의 호스트에서 실행하세요.

## Node 실행 (`system.run`)

macOS node가 페어링되어 있으면 Gateway는 해당 node에서 `system.run`을 호출할 수 있습니다. 이는 Mac에 대한 **원격 코드 실행**입니다:

- node 페어링(승인 + 토큰)이 필요합니다.
- Gateway node 페어링은 per-command 승인 표면이 아닙니다. 이는 node 신원/신뢰 및 토큰 발급을 설정합니다.
- Gateway는 `gateway.nodes.allowCommands` / `denyCommands`를 통해 거친 전역 node 명령 정책을 적용합니다.
- Mac에서는 **Settings → Exec approvals**(security + ask + allowlist)로 제어합니다.
- node별 `system.run` 정책은 node 자체의 exec approval 파일(`exec.approvals.node.*`)이며, 이는 gateway의 전역 명령 ID 정책보다 더 엄격하거나 더 느슨할 수 있습니다.
- `security="full"` 및 `ask="off"`로 실행되는 node는 기본 신뢰 운영자 모델을 따르고 있는 것입니다. 배포에서 더 엄격한 승인 또는 allowlist가 명시적으로 필요하지 않다면 이는 예상된 동작으로 취급하세요.
- 승인 모드는 정확한 요청 컨텍스트와, 가능할 경우 하나의 구체적인 로컬 스크립트/파일 피연산자에 바인딩됩니다. OpenClaw가 인터프리터/런타임 명령에 대해 정확히 하나의 직접 로컬 파일을 식별할 수 없으면, 전체 의미론적 범위를 약속하는 대신 승인 기반 실행은 거부됩니다.
- `host=node`의 경우 승인 기반 실행은 canonical prepared
  `systemRunPlan`도 저장합니다. 이후 승인된 전달은 그 저장된 plan을 재사용하며,
  gateway 검증은 승인 요청 생성 후 호출자가 command/cwd/session 컨텍스트를 수정하는 것을 거부합니다.
- 원격 실행을 원하지 않는다면 security를 **deny**로 설정하고 해당 Mac의 node 페어링을 제거하세요.

분류 시 이 구분이 중요합니다:

- 다시 연결된 페어링 node가 다른 명령 목록을 광고하는 것만으로는, Gateway 전역 정책과 node의 로컬 exec approval이 실제 실행 경계를 계속 강제한다면 그 자체로 취약점이 아닙니다.
- node pairing 메타데이터를 두 번째 숨겨진 per-command 승인 계층으로 보는 보고는 보통 보안 경계 우회가 아니라 정책/UX 혼동입니다.

## 동적 Skills (watcher / 원격 nodes)

OpenClaw는 세션 도중 Skills 목록을 새로고침할 수 있습니다:

- **Skills watcher**: `SKILL.md` 변경 사항이 다음 에이전트 턴에서 Skills 스냅샷을 업데이트할 수 있습니다.
- **원격 nodes**: macOS node 연결 시 macOS 전용 Skills가 사용 가능해질 수 있습니다(bin probing 기준).

Skill 폴더는 **신뢰된 코드**로 취급하고 누가 이를 수정할 수 있는지 제한하세요.

## 위협 모델

AI 비서는 다음을 할 수 있습니다:

- 임의 셸 명령 실행
- 파일 읽기/쓰기
- 네트워크 서비스 접근
- WhatsApp 접근 권한이 있다면 누구에게나 메시지 전송

사용자에게 메시지를 보내는 사람들은 다음을 시도할 수 있습니다:

- AI를 속여 나쁜 일을 하게 만들기
- 사용자 데이터를 얻기 위한 사회공학
- 인프라 세부 정보 탐색

## 핵심 개념: 지능보다 먼저 접근 제어

여기서 대부분의 실패는 정교한 익스플로잇이 아닙니다. “누군가 봇에 메시지를 보냈고, 봇이 그 요청을 수행했다”에 가깝습니다.

OpenClaw의 입장:

- **정체성 우선:** 누가 봇과 대화할 수 있는지 결정(DM 페어링 / allowlist / 명시적 “open”)
- **범위 다음:** 봇이 어디에서 행동할 수 있는지 결정(그룹 allowlist + mention gating, 도구, sandboxing, 장치 권한)
- **모델은 마지막:** 모델은 조작될 수 있다고 가정하고, 조작의 폭발 반경이 제한되도록 설계

## 명령 권한 모델

슬래시 명령과 지시문은 **권한 있는 발신자**에게만 적용됩니다. 권한은
채널 allowlist/페어링과 `commands.useAccessGroups`에서 파생됩니다([Configuration](/gateway/configuration)
및 [Slash commands](/tools/slash-commands) 참조). 채널 allowlist가 비어 있거나 `"*"`를 포함하면,
해당 채널의 명령은 사실상 개방됩니다.

`/exec`는 권한 있는 운영자를 위한 세션 전용 편의 기능입니다. 구성 파일을 쓰거나
다른 세션을 변경하지는 않습니다.

## 제어 평면 도구 위험

두 개의 내장 도구는 영구적인 제어 평면 변경을 만들 수 있습니다:

- `gateway`는 `config.schema.lookup` / `config.get`으로 구성을 검사할 수 있고, `config.apply`, `config.patch`, `update.run`으로 영구 변경을 만들 수 있습니다.
- `cron`은 원래 채팅/작업이 끝난 뒤에도 계속 실행되는 예약 작업을 만들 수 있습니다.

소유자 전용 `gateway` 런타임 도구는 여전히
`tools.exec.ask` 또는 `tools.exec.security`를 다시 쓰는 것을 거부합니다. 레거시 `tools.bash.*` 별칭도
쓰기 전에 같은 보호된 exec 경로로 정규화됩니다.

신뢰되지 않는 콘텐츠를 처리하는 에이전트/표면에서는 기본적으로 다음을 거부하세요:

```json5
{
  tools: {
    deny: ["gateway", "cron", "sessions_spawn", "sessions_send"],
  },
}
```

`commands.restart=false`는 재시작 동작만 막습니다. `gateway` config/update 동작은 비활성화하지 않습니다.

## Plugins/확장

Plugins는 Gateway와 **같은 프로세스 안에서** 실행됩니다. 신뢰된 코드로 취급하세요:

- 신뢰하는 소스의 plugin만 설치하세요.
- 명시적인 `plugins.allow` allowlist를 선호하세요.
- 활성화 전에 plugin 구성을 검토하세요.
- plugin 변경 후 Gateway를 재시작하세요.
- plugins를 설치하거나 업데이트하는 경우(`openclaw plugins install <package>`, `openclaw plugins update <id>`), 신뢰되지 않는 코드를 실행하는 것처럼 취급하세요:
  - 설치 경로는 활성 plugin 설치 루트 아래의 plugin별 디렉터리입니다.
  - OpenClaw는 설치/업데이트 전에 내장 dangerous-code 스캔을 실행합니다. `critical` 결과는 기본적으로 차단합니다.
  - OpenClaw는 `npm pack`을 사용한 뒤 해당 디렉터리에서 `npm install --omit=dev`를 실행합니다(npm lifecycle script는 설치 중 코드를 실행할 수 있음).
  - 버전 고정 exact 버전(`@scope/pkg@1.2.3`)을 선호하고, 활성화 전에 디스크에 압축 해제된 코드를 검사하세요.
  - `--dangerously-force-unsafe-install`은 plugin 설치/업데이트 흐름에서 내장 스캔 오탐에 대한 비상 탈출용입니다. plugin `before_install` hook 정책 차단이나 scan failure를 우회하지는 않습니다.
  - Gateway 기반 Skill 의존성 설치도 동일한 dangerous/suspicious 구분을 따릅니다. 내장 `critical` 결과는 호출자가 명시적으로 `dangerouslyForceUnsafeInstall`을 설정하지 않는 한 차단되며, suspicious 결과는 경고만 합니다. `openclaw skills install`은 여전히 별도의 ClawHub Skill 다운로드/설치 흐름입니다.

자세한 내용: [Plugins](/tools/plugin)

## DM 접근 모델 (pairing / allowlist / open / disabled)

현재 DM을 지원하는 모든 채널은 메시지가 처리되기 **전에** 인바운드 DM을 제어하는 DM 정책(`dmPolicy` 또는 `*.dm.policy`)을 지원합니다:

- `pairing`(기본값): 알 수 없는 발신자는 짧은 페어링 코드를 받고, 승인되기 전까지 봇은 그 메시지를 무시합니다. 코드는 1시간 후 만료되며, 반복되는 DM은 새 요청이 생성되기 전까지 코드를 다시 보내지 않습니다. 대기 요청은 기본적으로 **채널당 3개**로 제한됩니다.
- `allowlist`: 알 수 없는 발신자는 차단됩니다(페어링 핸드셰이크 없음).
- `open`: 누구나 DM 가능(공개). 채널 allowlist에 `"*"`가 포함되어야 합니다(**명시적 opt-in 필요**).
- `disabled`: 인바운드 DM을 완전히 무시합니다.

CLI를 통한 승인:

```bash
openclaw pairing list <channel>
openclaw pairing approve <channel> <code>
```

세부 사항 + 디스크 파일: [Pairing](/channels/pairing)

## DM 세션 격리 (multi-user 모드)

기본적으로 OpenClaw는 **모든 DM을 메인 세션으로 라우팅**하므로 비서가 장치와 채널 전반에서 연속성을 가집니다. 그러나 **여러 사람**이 봇에 DM할 수 있다면(open DMs 또는 다중 인원 allowlist), DM 세션을 격리하는 것을 고려하세요:

```json5
{
  session: { dmScope: "per-channel-peer" },
}
```

이렇게 하면 그룹 채팅은 계속 격리하면서도 사용자 간 컨텍스트 유출을 막을 수 있습니다.

이것은 메시징 컨텍스트 경계이지 호스트 관리자 경계가 아닙니다. 사용자가 상호 적대적이고 같은 Gateway 호스트/구성을 공유한다면, 신뢰 경계별로 별도의 gateway를 실행하세요.

### Secure DM 모드 (권장)

위 스니펫을 **Secure DM 모드**로 취급하세요:

- 기본값: `session.dmScope: "main"`(모든 DM이 연속성을 위해 하나의 세션을 공유)
- 로컬 CLI 온보딩 기본값: 설정되지 않은 경우 `session.dmScope: "per-channel-peer"`를 기록함(기존 명시적 값은 유지)
- Secure DM 모드: `session.dmScope: "per-channel-peer"`(각 채널+발신자 쌍이 격리된 DM 컨텍스트를 가짐)
- 크로스 채널 피어 격리: `session.dmScope: "per-peer"`(각 발신자가 같은 유형의 모든 채널에서 하나의 세션을 가짐)

같은 채널에서 여러 계정을 실행한다면 `per-account-channel-peer`를 사용하세요. 같은 사람이 여러 채널에서 연락한다면 `session.identityLinks`를 사용해 تلك DM 세션을 하나의 정규 신원으로 합치세요. [Session Management](/concepts/session) 및 [Configuration](/gateway/configuration)을 참조하세요.

## Allowlists (DM + 그룹) - 용어

OpenClaw에는 “누가 나를 트리거할 수 있는가?”에 대한 두 개의 별도 계층이 있습니다:

- **DM allowlist** (`allowFrom` / `channels.discord.allowFrom` / `channels.slack.allowFrom`; 레거시: `channels.discord.dm.allowFrom`, `channels.slack.dm.allowFrom`): 누가 직접 메시지에서 봇과 대화할 수 있는가.
  - `dmPolicy="pairing"`이면 승인은 `~/.openclaw/credentials/` 아래의 계정 범위 pairing allowlist 저장소에 기록되며(기본 계정은 `<channel>-allowFrom.json`, 비기본 계정은 `<channel>-<accountId>-allowFrom.json`), config allowlist와 병합됩니다.
- **그룹 allowlist** (채널별): 봇이 어떤 그룹/채널/guild에서 메시지를 아예 받을지.
  - 일반적인 패턴:
    - `channels.whatsapp.groups`, `channels.telegram.groups`, `channels.imessage.groups`: `requireMention` 같은 그룹별 기본값; 설정되면 그룹 allowlist 역할도 함(전체 허용 동작을 유지하려면 `"*"` 포함)
    - `groupPolicy="allowlist"` + `groupAllowFrom`: 그룹 세션 **내부에서** 누가 봇을 트리거할 수 있는지 제한(WhatsApp/Telegram/Signal/iMessage/Microsoft Teams)
    - `channels.discord.guilds` / `channels.slack.channels`: 표면별 allowlist + 멘션 기본값
  - 그룹 검사는 이 순서로 실행됩니다: 먼저 `groupPolicy`/그룹 allowlist, 그다음 mention/reply activation.
  - 봇 메시지에 답장하는 것(암묵적 멘션)은 `groupAllowFrom` 같은 발신자 allowlist를 우회하지 않습니다.
  - **보안 참고:** `dmPolicy="open"`과 `groupPolicy="open"`은 최후의 수단 설정으로 취급하세요. 모든 방 멤버를 완전히 신뢰하지 않는 한 거의 사용하지 말고, pairing + allowlist를 우선하세요.

자세한 내용: [Configuration](/gateway/configuration) 및 [Groups](/channels/groups)

## 프롬프트 인젝션(무엇이고, 왜 중요한가)

프롬프트 인젝션은 공격자가 모델을 조작해 안전하지 않은 일을 하게 만드는 메시지를 만드는 것입니다(“지시를 무시하라”, “파일시스템을 덤프하라”, “이 링크를 따라가서 명령을 실행하라” 등).

강한 시스템 프롬프트가 있더라도 **프롬프트 인젝션은 해결되지 않았습니다**. 시스템 프롬프트 가드레일은 소프트 가이드일 뿐이며, 실제 강제력은 도구 정책, exec 승인, sandboxing, 채널 allowlist에서 나옵니다(그리고 운영자는 설계상 이를 비활성화할 수 있습니다). 실제로 도움이 되는 것은:

- 인바운드 DM을 잠그기(pairing/allowlist)
- 그룹에서는 mention gating을 선호하고, 공개 방에서 “항상 켜져 있는” 봇을 피하기
- 링크, 첨부 파일, 붙여넣은 지시문을 기본적으로 적대적인 것으로 취급하기
- 민감한 도구 실행은 sandbox에서 수행하고, 비밀은 에이전트가 접근 가능한 파일시스템 밖에 두기
- 참고: sandboxing은 opt-in입니다. sandbox 모드가 꺼져 있으면 암묵적 `host=auto`는 gateway 호스트로 해석됩니다. 명시적 `host=sandbox`는 sandbox 런타임이 없기 때문에 여전히 fail closed합니다. 이 동작을 config에서 명시하려면 `host=gateway`를 설정하세요.
- 고위험 도구(`exec`, `browser`, `web_fetch`, `web_search`)는 신뢰된 에이전트 또는 명시적 allowlist에만 제한하기
- 인터프리터(`python`, `node`, `ruby`, `perl`, `php`, `lua`, `osascript`)를 allowlist에 넣는 경우 `tools.exec.strictInlineEval`을 활성화하여 inline eval 형식도 명시적 승인을 요구하게 하기
- **모델 선택이 중요:** 오래되거나 작은 레거시 모델은 프롬프트 인젝션과 도구 오용에 훨씬 덜 강합니다. 도구 활성화 에이전트에는 가장 강력한 최신 세대 instruction-hardened 모델을 사용하세요.

다음과 같은 신호는 신뢰하지 마세요:

- “이 파일/URL을 읽고 적힌 대로 정확히 수행해.”
- “시스템 프롬프트나 안전 규칙을 무시해.”
- “숨겨진 지침이나 도구 출력을 공개해.”
- “`~/.openclaw`나 로그 전체 내용을 붙여넣어.”

## unsafe external content 우회 플래그

OpenClaw에는 외부 콘텐츠 안전 래핑을 비활성화하는 명시적 우회 플래그가 있습니다:

- `hooks.mappings[].allowUnsafeExternalContent`
- `hooks.gmail.allowUnsafeExternalContent`
- Cron 페이로드 필드 `allowUnsafeExternalContent`

가이드:

- 프로덕션에서는 설정하지 않거나 false로 유지하세요.
- 매우 제한된 디버깅 용도로만 일시적으로 활성화하세요.
- 활성화한다면 해당 에이전트를 격리하세요(sandbox + minimal 도구 + 전용 세션 네임스페이스).

Hooks 위험 참고:

- Hook 페이로드는 사용자가 제어하는 시스템에서 전달되더라도 신뢰되지 않는 콘텐츠입니다(메일/문서/웹 콘텐츠는 프롬프트 인젝션을 담을 수 있음).
- 약한 모델 티어는 이 위험을 증가시킵니다. hook 기반 자동화에는 강력한 최신 모델 티어를 선호하고, `tools.profile: "messaging"` 또는 그보다 더 엄격한 도구 정책을 유지하며, 가능하면 sandboxing도 사용하세요.

### 프롬프트 인젝션은 공개 DM이 없어도 발생할 수 있습니다

봇에 메시지를 보낼 수 있는 사람이 **오직 본인뿐**이라 해도, 봇이 읽는 **신뢰되지 않는 콘텐츠**(웹 검색/가져오기 결과, 브라우저 페이지, 이메일, 문서, 첨부 파일, 붙여넣은 로그/코드)를 통해 프롬프트 인젝션은 여전히 발생할 수 있습니다. 즉, 발신자만이 위협 표면이 아니라 **콘텐츠 자체**가 적대적 지시를 담고 있을 수 있습니다.

도구가 활성화된 경우 일반적인 위험은 컨텍스트 유출 또는 도구 호출 트리거입니다. 폭발 반경을 줄이려면:

- 신뢰되지 않는 콘텐츠를 요약하는 읽기 전용 또는 도구 비활성화 **reader agent**를 사용하고, 그 요약만 메인 에이전트에 전달하세요.
- 필요하지 않다면 도구 활성화 에이전트에서 `web_search` / `web_fetch` / `browser`를 꺼두세요.
- OpenResponses URL 입력(`input_file` / `input_image`)의 경우
  `gateway.http.endpoints.responses.files.urlAllowlist`와
  `gateway.http.endpoints.responses.images.urlAllowlist`를 엄격하게 설정하고
  `maxUrlParts`를 낮게 유지하세요. 빈 allowlist는 설정되지 않은 것으로 간주되므로,
  URL 가져오기를 완전히 비활성화하려면 `files.allowUrl: false` / `images.allowUrl: false`를 사용하세요.
- OpenResponses 파일 입력의 경우 디코드된 `input_file` 텍스트도 여전히
  **신뢰되지 않는 외부 콘텐츠**로 주입됩니다. Gateway가 로컬에서 디코드했다는 이유만으로
  파일 텍스트를 신뢰할 수 있다고 생각하지 마세요. 이 주입 블록은 여전히
  긴 `SECURITY NOTICE:` 배너는 생략하더라도 명시적인
  `<<<EXTERNAL_UNTRUSTED_CONTENT ...>>>` 경계 마커와 `Source: External`
  메타데이터를 포함합니다.
- 첨부 문서에서 텍스트를 추출하여 미디어 프롬프트에 추가하기 전에
  media-understanding이 텍스트를 추출하는 경우에도 동일한 marker 기반 래핑이 적용됩니다.
- 신뢰되지 않는 입력을 다루는 모든 에이전트에는 sandboxing과 엄격한 도구 allowlist를 활성화하세요.
- 비밀은 프롬프트에 넣지 말고 gateway 호스트의 env/config를 통해 전달하세요.

### 모델 강도(보안 참고)

프롬프트 인젝션 저항성은 모델 티어마다 **균일하지 않습니다**. 더 작고 저렴한 모델일수록, 특히 적대적 프롬프트 아래에서 도구 오용과 지시 탈취에 더 취약한 경향이 있습니다.

<Warning>
도구 활성화 에이전트나 신뢰되지 않는 콘텐츠를 읽는 에이전트에서는 오래되거나 작은 모델의 프롬프트 인젝션 위험이 지나치게 높을 수 있습니다. 그런 작업에는 약한 모델 티어를 사용하지 마세요.
</Warning>

권장 사항:

- 도구를 실행하거나 파일/네트워크에 접근할 수 있는 모든 봇에는 **최신 세대의 최고 티어 모델**을 사용하세요.
- 도구 활성화 에이전트나 신뢰되지 않는 inbox에는 **오래되거나 약하거나 작은 티어**를 사용하지 마세요. 프롬프트 인젝션 위험이 너무 큽니다.
- 작은 모델을 반드시 사용해야 한다면 **폭발 반경을 줄이세요**(읽기 전용 도구, 강한 sandboxing, 최소 파일시스템 접근, 엄격한 allowlist).
- 작은 모델을 사용할 때는 **모든 세션에 sandboxing을 활성화**하고, 입력이 엄격히 통제되지 않는 한 **web_search/web_fetch/browser를 비활성화**하세요.
- 신뢰된 입력과 도구가 없는 채팅 전용 개인 비서라면 작은 모델도 보통 괜찮습니다.

<a id="reasoning-verbose-output-in-groups"></a>

## 그룹에서의 Reasoning 및 verbose 출력

`/reasoning`과 `/verbose`는 공개 채널에 의도되지 않은 내부 reasoning 또는 도구 출력을 노출할 수 있습니다. 그룹 환경에서는 이를 **디버그 전용**으로 취급하고 명시적으로 필요하지 않다면 꺼두세요.

가이드:

- 공개 방에서는 `/reasoning`과 `/verbose`를 꺼두세요.
- 활성화한다면 신뢰된 DM 또는 엄격히 통제된 방에서만 하세요.
- 기억하세요: verbose 출력에는 도구 인수, URL, 모델이 본 데이터가 포함될 수 있습니다.

## 구성 강화(예시)

### 0) 파일 권한

Gateway 호스트에서 config + state를 비공개로 유지하세요:

- `~/.openclaw/openclaw.json`: `600`(사용자 읽기/쓰기만)
- `~/.openclaw`: `700`(사용자만)

`openclaw doctor`는 이러한 권한 문제를 경고하고 강화 제안을 할 수 있습니다.

### 0.4) 네트워크 노출(bind + port + firewall)

Gateway는 하나의 포트에서 **WebSocket + HTTP**를 다중화합니다:

- 기본값: `18789`
- Config/플래그/env: `gateway.port`, `--port`, `OPENCLAW_GATEWAY_PORT`

이 HTTP 표면에는 Control UI와 canvas host도 포함됩니다:

- Control UI(SPA assets) (기본 base path `/`)
- Canvas host: `/__openclaw__/canvas/` 및 `/__openclaw__/a2ui/` (임의 HTML/JS, 신뢰되지 않는 콘텐츠로 취급)

일반 브라우저에서 canvas 콘텐츠를 로드한다면, 다른 신뢰되지 않는 웹 페이지처럼 취급하세요:

- canvas host를 신뢰되지 않는 네트워크/사용자에게 노출하지 마세요.
- 의미를 완전히 이해하지 못하는 한, canvas 콘텐츠가 권한 있는 웹 표면과 같은 origin을 공유하도록 하지 마세요.

Bind 모드는 Gateway가 어디서 리스닝할지 제어합니다:

- `gateway.bind: "loopback"`(기본값): 로컬 클라이언트만 연결 가능
- non-loopback bind(`"lan"`, `"tailnet"`, `"custom"`)는 공격 표면을 확장합니다. gateway auth(공유 token/password 또는 올바르게 구성된 non-loopback trusted proxy) 및 실제 firewall과 함께만 사용하세요.

실전 규칙:

- LAN bind보다 Tailscale Serve를 선호하세요(Serve는 Gateway를 loopback에 유지하고, 접근은 Tailscale이 처리).
- LAN에 bind해야 한다면 포트를 엄격한 source IP allowlist로 firewall하세요. 광범위하게 port-forward하지 마세요.
- `0.0.0.0`에 인증 없이 Gateway를 노출하지 마세요.

### 0.4.1) Docker 포트 publish + UFW (`DOCKER-USER`)

VPS에서 Docker로 OpenClaw를 실행한다면, publish된 컨테이너 포트
(`-p HOST:CONTAINER` 또는 Compose `ports:`)는 호스트 `INPUT` 규칙만이 아니라
Docker forwarding chain을 통해 라우팅된다는 점을 기억하세요.

Docker 트래픽을 firewall 정책과 일치시키려면
`DOCKER-USER`에서 규칙을 강제하세요(이 체인은 Docker 자체 accept 규칙보다 먼저 평가됨).
많은 최신 배포판에서 `iptables`/`ip6tables`는 `iptables-nft` 프런트엔드를 사용하며,
여전히 nftables 백엔드에 이러한 규칙을 적용합니다.

최소 allowlist 예시(IPv4):

```bash
# /etc/ufw/after.rules (append as its own *filter section)
*filter
:DOCKER-USER - [0:0]
-A DOCKER-USER -m conntrack --ctstate ESTABLISHED,RELATED -j RETURN
-A DOCKER-USER -s 127.0.0.0/8 -j RETURN
-A DOCKER-USER -s 10.0.0.0/8 -j RETURN
-A DOCKER-USER -s 172.16.0.0/12 -j RETURN
-A DOCKER-USER -s 192.168.0.0/16 -j RETURN
-A DOCKER-USER -s 100.64.0.0/10 -j RETURN
-A DOCKER-USER -p tcp --dport 80 -j RETURN
-A DOCKER-USER -p tcp --dport 443 -j RETURN
-A DOCKER-USER -m conntrack --ctstate NEW -j DROP
-A DOCKER-USER -j RETURN
COMMIT
```

IPv6에는 별도의 테이블이 있습니다. Docker IPv6가 활성화되어 있다면
`/etc/ufw/after6.rules`에 일치하는 정책도 추가하세요.

문서 스니펫에 `eth0` 같은 인터페이스 이름을 하드코딩하지 마세요. 인터페이스 이름은
VPS 이미지마다 다르며(`ens3`, `enp*` 등), 불일치하면 deny 규칙이 의도치 않게 건너뛰어질 수 있습니다.

리로드 후 빠른 검증:

```bash
ufw reload
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
nmap -sT -p 1-65535 <public-ip> --open
```

외부에서 보이는 포트는 의도적으로 노출한 것만이어야 합니다(대부분의 설정에서는
SSH + reverse proxy 포트).

### 0.4.2) mDNS/Bonjour discovery (정보 노출)

Gateway는 로컬 장치 discovery를 위해 mDNS(`_openclaw-gw._tcp`, 포트 5353)로 자신의 존재를 브로드캐스트합니다. full 모드에서는 운영 세부 정보를 노출할 수 있는 TXT 레코드도 포함됩니다:

- `cliPath`: CLI 바이너리의 전체 파일시스템 경로(사용자 이름 및 설치 위치 노출)
- `sshPort`: 호스트의 SSH 사용 가능 여부 광고
- `displayName`, `lanHost`: 호스트명 정보

**운영 보안 고려 사항:** 인프라 세부 정보를 브로드캐스트하면 로컬 네트워크의 누구에게나 정찰이 쉬워집니다. 파일시스템 경로나 SSH 사용 가능 여부 같은 “무해해 보이는” 정보도 공격자가 환경을 매핑하는 데 도움을 줍니다.

**권장 사항:**

1. **minimal 모드**(기본값, 노출된 gateway에 권장): 민감한 필드를 mDNS 브로드캐스트에서 제외합니다:

   ```json5
   {
     discovery: {
       mdns: { mode: "minimal" },
     },
   }
   ```

2. 로컬 장치 discovery가 필요 없다면 **완전히 비활성화**하세요:

   ```json5
   {
     discovery: {
       mdns: { mode: "off" },
     },
   }
   ```

3. **full 모드**(opt-in): TXT 레코드에 `cliPath` + `sshPort`를 포함합니다:

   ```json5
   {
     discovery: {
       mdns: { mode: "full" },
     },
   }
   ```

4. **환경 변수**(대안): config 변경 없이 mDNS를 비활성화하려면 `OPENCLAW_DISABLE_BONJOUR=1`을 설정하세요.

minimal 모드에서도 Gateway는 장치 discovery에 충분한 정보(`role`, `gatewayPort`, `transport`)를 계속 브로드캐스트하지만, `cliPath`와 `sshPort`는 제외합니다. CLI 경로 정보가 필요한 앱은 인증된 WebSocket 연결을 통해 이를 가져올 수 있습니다.

### 0.5) Gateway WebSocket 잠그기 (local auth)

Gateway auth는 기본적으로 **필수**입니다. 유효한 gateway auth 경로가 구성되지 않으면
Gateway는 WebSocket 연결을 거부합니다(fail‑closed).

온보딩은 기본적으로 token을 생성하므로(loopback이라도)
로컬 클라이언트도 인증해야 합니다.

**모든** WS 클라이언트가 인증하게 하려면 token을 설정하세요:

```json5
{
  gateway: {
    auth: { mode: "token", token: "your-token" },
  },
}
```

Doctor가 이를 생성해 줄 수 있습니다: `openclaw doctor --generate-gateway-token`.

참고: `gateway.remote.token` / `.password`는 클라이언트 자격 증명 소스입니다.
이 값만으로는 로컬 WS 접근을 보호하지 **않습니다**.
로컬 호출 경로는 `gateway.auth.*`가 설정되지 않은 경우에만 `gateway.remote.*`를 fallback으로 사용할 수 있습니다.
`gateway.auth.token` / `gateway.auth.password`가
SecretRef로 명시적으로 구성되어 있고 해석되지 않으면, 해석은 fail closed합니다(원격 fallback이 이를 가리지 않음).
선택 사항: `wss://` 사용 시 `gateway.remote.tlsFingerprint`로 원격 TLS를 pin할 수 있습니다.
plaintext `ws://`는 기본적으로 loopback 전용입니다. 신뢰된 private-network
경로에 대해서만, 비상 수단으로 클라이언트 프로세스에서 `OPENCLAW_ALLOW_INSECURE_PRIVATE_WS=1`을 설정하세요.

로컬 장치 페어링:

- 같은 호스트 클라이언트를 원활하게 하기 위해, 직접 local loopback 연결에 대해서는 장치 페어링이 자동 승인됩니다.
- OpenClaw는 또한
  신뢰된 shared-secret helper 흐름을 위한 제한적인 backend/container-local self-connect 경로를 가지고 있습니다.
- tailnet 및 LAN 연결은 같은 호스트의 tailnet bind를 포함해 원격으로 간주되며 여전히 승인이 필요합니다.

인증 모드:

- `gateway.auth.mode: "token"`: 공유 bearer token(대부분의 설정에 권장)
- `gateway.auth.mode: "password"`: 비밀번호 인증(env를 통한 설정 권장: `OPENCLAW_GATEWAY_PASSWORD`)
- `gateway.auth.mode: "trusted-proxy"`: identity-aware reverse proxy가 사용자를 인증하고 헤더로 신원을 전달하도록 신뢰([Trusted Proxy Auth](/gateway/trusted-proxy-auth) 참조)

교체 체크리스트(token/password):

1. 새 비밀 생성/설정(`gateway.auth.token` 또는 `OPENCLAW_GATEWAY_PASSWORD`)
2. Gateway 재시작(또는 macOS 앱이 Gateway를 감독한다면 앱 재시작)
3. Gateway를 호출하는 모든 머신에서 원격 클라이언트 비밀 갱신(`gateway.remote.token` / `.password`)
4. 이전 자격 증명으로 더 이상 연결할 수 없는지 확인

### 0.6) Tailscale Serve identity headers

`gateway.auth.allowTailscale`이 `true`일 때(Serve의 기본값), OpenClaw는
Control UI/WebSocket 인증을 위해 Tailscale Serve identity header(`tailscale-user-login`)를 허용합니다. OpenClaw는
로컬 Tailscale daemon(`tailscale whois`)을 통해 `x-forwarded-for` 주소를 해석하고 이를 해당 헤더와 일치시켜 신원을 검증합니다. 이 동작은 loopback에 도달하고 `x-forwarded-for`, `x-forwarded-proto`, `x-forwarded-host`가 Tailscale에 의해 주입된 요청에만 적용됩니다.
이 비동기 identity check 경로에서는 동일한 `{scope, ip}`에 대한 실패한 시도가 limiter가 실패를 기록하기 전에 직렬화됩니다. 따라서 한 Serve 클라이언트의 잘못된 동시 재시도는 두 번의 단순 불일치처럼 경쟁하지 않고 두 번째 시도에서 즉시 잠금이 걸릴 수 있습니다.
HTTP API 엔드포인트(예: `/v1/*`, `/tools/invoke`, `/api/channels/*`)는 Tailscale identity-header auth를 사용하지 않습니다. 이들은 여전히 gateway의 구성된 HTTP auth 모드를 따릅니다.

중요한 경계 참고:

- Gateway HTTP bearer auth는 사실상 전체 운영자 접근입니다.
- `/v1/chat/completions`, `/v1/responses`, `/api/channels/*`를 호출할 수 있는 자격 증명은 해당 gateway에 대한 전체 접근 운영자 비밀로 취급하세요.
- OpenAI 호환 HTTP 표면에서는 공유 비밀 bearer auth가 전체 기본 운영자 scope(`operator.admin`, `operator.approvals`, `operator.pairing`, `operator.read`, `operator.talk.secrets`, `operator.write`)와 에이전트 턴의 owner 의미를 복원합니다. 더 좁은 `x-openclaw-scopes` 값은 이 shared-secret 경로를 축소하지 못합니다.
- HTTP에서 per-request scope 의미는 요청이 trusted proxy auth나 private ingress의 `gateway.auth.mode="none"` 같은 신원 기반 모드에서 온 경우에만 적용됩니다.
- 그러한 신원 기반 모드에서는 `x-openclaw-scopes`를 생략하면 일반 운영자 기본 scope 집합으로 fallback합니다. 더 좁은 scope 집합이 필요하면 헤더를 명시적으로 보내세요.
- `/tools/invoke`도 동일한 shared-secret 규칙을 따릅니다. token/password bearer auth는 여기서도 전체 운영자 접근으로 취급되며, 신원 기반 모드는 여전히 선언된 scope를 존중합니다.
- 신뢰되지 않는 호출자와 이러한 자격 증명을 공유하지 마세요. 신뢰 경계별로 별도의 gateway를 선호하세요.

**신뢰 가정:** tokenless Serve auth는 gateway 호스트가 신뢰된다고 가정합니다.
이를 적대적인 같은 호스트 프로세스에 대한 보호로 취급하지 마세요. gateway 호스트에서 신뢰되지 않는
로컬 코드가 실행될 수 있다면 `gateway.auth.allowTailscale`을 비활성화하고
`gateway.auth.mode: "token"` 또는
`"password"`로 명시적인 shared-secret auth를 요구하세요.

**보안 규칙:** 자신의 reverse proxy에서 이러한 헤더를 전달하지 마세요. Gateway 앞에서 TLS를 종료하거나 프록시를 사용한다면
`gateway.auth.allowTailscale`을 비활성화하고
공유 비밀 auth(`gateway.auth.mode:
"token"` 또는 `"password"`) 또는 [Trusted Proxy Auth](/gateway/trusted-proxy-auth)를 사용하세요.

Trusted proxies:

- Gateway 앞에서 TLS를 종료한다면 프록시 IP를 `gateway.trustedProxies`에 설정하세요.
- OpenClaw는 local pairing 검사와 HTTP auth/local 검사를 위한 클라이언트 IP를 결정하기 위해 해당 IP의 `x-forwarded-for`(또는 `x-real-ip`)를 신뢰합니다.
- 프록시가 `x-forwarded-for`를 **덮어쓰고**, Gateway 포트에 대한 직접 접근을 차단하도록 하세요.

참고: [Tailscale](/gateway/tailscale) 및 [Web overview](/web)

### 0.6.1) node host를 통한 브라우저 제어(권장)

Gateway는 원격에 있지만 브라우저는 다른 머신에서 실행된다면, 브라우저 머신에서 **node host**를 실행하고 Gateway가 브라우저 작업을 프록시하도록 하세요([Browser tool](/tools/browser) 참조). node 페어링은 관리자 접근처럼 취급하세요.

권장 패턴:

- Gateway와 node host를 같은 tailnet(Tailscale) 안에 두세요.
- node는 의도적으로 페어링하고, 필요하지 않다면 브라우저 프록시 라우팅을 비활성화하세요.

피해야 할 것:

- relay/control 포트를 LAN 또는 공용 인터넷에 노출하기
- 브라우저 제어 엔드포인트에 Tailscale Funnel 사용하기(공용 노출)

### 0.7) 디스크의 비밀 정보(민감 데이터)

`~/.openclaw/`(또는 `$OPENCLAW_STATE_DIR/`) 아래의 모든 것은 비밀 또는 개인 데이터를 포함할 수 있다고 가정하세요:

- `openclaw.json`: config에 token(gateway, remote gateway), provider 설정, allowlist가 포함될 수 있음
- `credentials/**`: 채널 자격 증명(예: WhatsApp creds), pairing allowlist, legacy OAuth 가져오기
- `agents/<agentId>/agent/auth-profiles.json`: API 키, token profile, OAuth 토큰, 선택적인 `keyRef`/`tokenRef`
- `secrets.json`(선택 사항): `file` SecretRef provider에서 사용하는 파일 기반 비밀 페이로드(`secrets.providers`)
- `agents/<agentId>/agent/auth.json`: 레거시 호환 파일. 정적 `api_key` 항목은 발견 시 제거됩니다.
- `agents/<agentId>/sessions/**`: 개인 메시지 및 도구 출력을 포함할 수 있는 세션 transcript(`*.jsonl`) + 라우팅 메타데이터(`sessions.json`)
- 번들 plugin 패키지: 설치된 plugins(및 그 `node_modules/`)
- `sandboxes/**`: 도구 sandbox 워크스페이스; sandbox 안에서 읽고 쓴 파일 복사본이 쌓일 수 있음

강화 팁:

- 권한을 엄격히 유지하세요(디렉터리 `700`, 파일 `600`)
- gateway 호스트에 전체 디스크 암호화를 사용하세요
- 호스트를 공유한다면 Gateway용 전용 OS 사용자 계정을 선호하세요

### 0.8) 로그 + transcript (redaction + 보존)

접근 제어가 올바르더라도 로그와 transcript는 민감한 정보를 유출할 수 있습니다:

- Gateway 로그에는 도구 요약, 오류, URL이 포함될 수 있습니다.
- 세션 transcript에는 붙여넣은 비밀, 파일 내용, 명령 출력, 링크가 포함될 수 있습니다.

권장 사항:

- 도구 요약 redaction을 유지하세요(`logging.redactSensitive: "tools"`; 기본값)
- `logging.redactPatterns`를 통해 환경별 사용자 정의 패턴(token, hostnames, 내부 URL)을 추가하세요
- 진단을 공유할 때는 raw logs보다 `openclaw status --all`(붙여넣기 친화적, 비밀 redaction됨)를 선호하세요
- 장기 보존이 필요하지 않다면 오래된 세션 transcript와 로그 파일을 정리하세요

자세한 내용: [Logging](/gateway/logging)

### 1) DM: 기본값은 pairing

```json5
{
  channels: { whatsapp: { dmPolicy: "pairing" } },
}
```

### 2) 그룹: 어디서나 멘션 필요

```json
{
  "channels": {
    "whatsapp": {
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "groupChat": { "mentionPatterns": ["@openclaw", "@mybot"] }
      }
    ]
  }
}
```

그룹 채팅에서는 명시적으로 멘션될 때만 응답하세요.

### 3) 별도 번호 사용 (WhatsApp, Signal, Telegram)

전화번호 기반 채널에서는 개인 번호와 AI 번호를 분리하는 것을 고려하세요:

- 개인 번호: 개인 대화는 비공개 유지
- 봇 번호: AI가 처리하며, 적절한 경계를 설정

### 4) 읽기 전용 모드 (sandbox + 도구 사용)

다음을 조합해 읽기 전용 profile을 만들 수 있습니다:

- `agents.defaults.sandbox.workspaceAccess: "ro"`(또는 워크스페이스 접근이 전혀 없게 하려면 `"none"`)
- `write`, `edit`, `apply_patch`, `exec`, `process` 등을 차단하는 도구 allow/deny 목록

추가 강화 옵션:

- `tools.exec.applyPatch.workspaceOnly: true`(기본값): sandboxing이 꺼져 있어도 `apply_patch`가 워크스페이스 디렉터리 밖에 쓰거나 삭제하지 못하게 합니다. `apply_patch`가 워크스페이스 밖 파일을 건드리게 하려는 경우에만 `false`로 설정하세요.
- `tools.fs.workspaceOnly: true`(선택 사항): `read`/`write`/`edit`/`apply_patch` 경로와 네이티브 프롬프트 이미지 자동 로드 경로를 워크스페이스 디렉터리로 제한합니다(현재 절대 경로를 허용하고 있고 하나의 가드레일을 원할 때 유용).
- 파일시스템 루트를 좁게 유지하세요. 에이전트 워크스페이스/샌드박스 워크스페이스에 홈 디렉터리 같은 광범위한 루트를 사용하지 마세요. 넓은 루트는 민감한 로컬 파일(예: `~/.openclaw` 아래의 상태/구성)을 파일시스템 도구에 노출할 수 있습니다.

### 5) 안전한 기본 설정 (복사/붙여넣기)

Gateway를 비공개로 유지하고, DM pairing을 요구하며, 항상 켜진 그룹 봇을 피하는 “안전한 기본” config 예시:

```json5
{
  gateway: {
    mode: "local",
    bind: "loopback",
    port: 18789,
    auth: { mode: "token", token: "your-long-random-token" },
  },
  channels: {
    whatsapp: {
      dmPolicy: "pairing",
      groups: { "*": { requireMention: true } },
    },
  },
}
```

더 “기본적으로 안전한” 도구 실행도 원한다면 sandbox + 위험한 도구 deny를 non-owner 에이전트에 추가하세요(아래 “에이전트별 접근 프로필” 예시 참조).

채팅 기반 에이전트 턴에 대한 내장 기본값: non-owner 발신자는 `cron` 또는 `gateway` 도구를 사용할 수 없습니다.

## Sandboxing (권장)

전용 문서: [Sandboxing](/gateway/sandboxing)

서로 보완적인 두 가지 접근 방식이 있습니다:

- **전체 Gateway를 Docker에서 실행**(컨테이너 경계): [Docker](/install/docker)
- **도구 sandbox** (`agents.defaults.sandbox`, 호스트 gateway + Docker 격리 도구): [Sandboxing](/gateway/sandboxing)

참고: 에이전트 간 교차 접근을 막으려면 `agents.defaults.sandbox.scope`를 `"agent"`(기본값)
또는 더 엄격한 세션별 격리를 위한 `"session"`으로 유지하세요. `scope: "shared"`는
하나의 컨테이너/워크스페이스를 공유합니다.

sandbox 내부의 에이전트 워크스페이스 접근도 고려하세요:

- `agents.defaults.sandbox.workspaceAccess: "none"`(기본값)은 에이전트 워크스페이스 접근을 막으며, 도구는 `~/.openclaw/sandboxes` 아래 sandbox 워크스페이스에서 실행됩니다
- `agents.defaults.sandbox.workspaceAccess: "ro"`는 에이전트 워크스페이스를 `/agent`에 읽기 전용으로 마운트합니다(`write`/`edit`/`apply_patch` 비활성화)
- `agents.defaults.sandbox.workspaceAccess: "rw"`는 에이전트 워크스페이스를 `/workspace`에 읽기/쓰기 마운트합니다
- 추가 `sandbox.docker.binds`는 정규화 및 canonicalization된 source path에 대해 검증됩니다. 부모 심볼릭 링크 트릭과 canonical home alias도 `/etc`, `/var/run`, 또는 OS 홈 아래 자격 증명 디렉터리 같은 차단된 루트로 해석되면 여전히 fail closed합니다.

중요: `tools.elevated`는 sandbox 밖에서 exec를 실행하는 전역 기본 탈출구입니다. 실제 호스트는 기본적으로 `gateway`, exec 대상이 `node`로 구성된 경우에는 `node`입니다. `tools.elevated.allowFrom`은 엄격하게 유지하고 낯선 사람에게 활성화하지 마세요. 에이전트별 `agents.list[].tools.elevated`로 추가 제한도 가능합니다. [Elevated Mode](/tools/elevated)를 참조하세요.

### 하위 에이전트 위임 가드레일

세션 도구를 허용한다면, 위임된 하위 에이전트 실행도 또 하나의 경계 결정으로 취급하세요:

- 에이전트가 실제로 위임이 필요하지 않다면 `sessions_spawn`을 거부하세요.
- `agents.defaults.subagents.allowAgents`와 에이전트별 `agents.list[].subagents.allowAgents` 재정의를 알려진 안전한 대상 에이전트로 제한하세요.
- sandbox를 유지해야 하는 워크플로에서는 `sessions_spawn`을 `sandbox: "require"`로 호출하세요(기본값은 `inherit`).
- `sandbox: "require"`는 대상 자식 런타임이 sandbox되지 않은 경우 빠르게 실패합니다.

## 브라우저 제어 위험

브라우저 제어를 활성화하면 모델이 실제 브라우저를 조작할 수 있게 됩니다.
그 브라우저 프로필에 이미 로그인된 세션이 있다면, 모델은 해당 계정과 데이터에
접근할 수 있습니다. 브라우저 프로필은 **민감한 상태**로 취급하세요:

- 에이전트용 전용 프로필을 선호하세요(기본 `openclaw` 프로필).
- 에이전트를 개인 일상용 프로필에 연결하지 마세요.
- sandbox된 에이전트에는 신뢰하지 않는 한 호스트 브라우저 제어를 비활성화하세요.
- 독립형 loopback 브라우저 제어 API는 shared-secret auth만 허용합니다
  (gateway token bearer auth 또는 gateway password). trusted-proxy 또는 Tailscale Serve identity header는 사용하지 않습니다.
- 브라우저 다운로드는 신뢰되지 않는 입력으로 취급하세요. 격리된 다운로드 디렉터리를 선호하세요.
- 가능하면 에이전트 프로필에서 브라우저 sync/비밀번호 관리자를 비활성화하세요(폭발 반경 감소).
- 원격 gateway의 경우 “브라우저 제어”는 해당 프로필이 접근할 수 있는 모든 것에 대한 “운영자 접근”과 동등하다고 가정하세요.
- Gateway와 node host는 tailnet 전용으로 유지하고, 브라우저 제어 포트를 LAN이나 공용 인터넷에 노출하지 마세요.
- 필요하지 않다면 브라우저 프록시 라우팅을 비활성화하세요(`gateway.nodes.browser.mode="off"`).
- Chrome MCP existing-session 모드는 **더 안전하지 않습니다**. 해당 호스트 Chrome 프로필이 접근 가능한 곳에서 사용자처럼 동작할 수 있습니다.

### 브라우저 SSRF 정책 (신뢰된 네트워크 기본값)

OpenClaw의 브라우저 네트워크 정책은 기본적으로 신뢰된 운영자 모델을 따릅니다. 명시적으로 비활성화하지 않는 한 private/internal 대상은 허용됩니다.

- 기본값: `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: true` (설정되지 않았을 때 암묵적 적용)
- 레거시 별칭: `browser.ssrfPolicy.allowPrivateNetwork`도 호환성을 위해 계속 허용됨
- 엄격 모드: private/internal/special-use 대상을 기본적으로 차단하려면 `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork: false`로 설정
- 엄격 모드에서는 `hostnameAllowlist`(예: `*.example.com`)와 `allowedHostnames`(정확한 호스트 예외, `localhost` 같은 차단된 이름 포함)를 명시적 예외로 사용
- 리디렉션 기반 피벗을 줄이기 위해 네비게이션 전 검사와, 네비게이션 후 최종 `http(s)` URL에 대한 best-effort 재검사가 수행됨

엄격 정책 예시:

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"],
    },
  },
}
```

## 에이전트별 접근 프로필 (multi-agent)

멀티 에이전트 라우팅에서는 각 에이전트가 자체 sandbox + 도구 정책을 가질 수 있습니다.
이를 사용해 에이전트별로 **전체 접근**, **읽기 전용**, **접근 없음**을 설정하세요.
전체 세부 사항과 우선순위 규칙은 [Multi-Agent Sandbox & Tools](/tools/multi-agent-sandbox-tools)를
참조하세요.

일반적인 사용 사례:

- Personal 에이전트: 전체 접근, sandbox 없음
- 가족/업무 에이전트: sandbox + 읽기 전용 도구
- 공개 에이전트: sandbox + 파일시스템/셸 도구 없음

### 예시: 전체 접근 (sandbox 없음)

```json5
{
  agents: {
    list: [
      {
        id: "personal",
        workspace: "~/.openclaw/workspace-personal",
        sandbox: { mode: "off" },
      },
    ],
  },
}
```

### 예시: 읽기 전용 도구 + 읽기 전용 워크스페이스

```json5
{
  agents: {
    list: [
      {
        id: "family",
        workspace: "~/.openclaw/workspace-family",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "ro",
        },
        tools: {
          allow: ["read"],
          deny: ["write", "edit", "apply_patch", "exec", "process", "browser"],
        },
      },
    ],
  },
}
```

### 예시: 파일시스템/셸 접근 없음 (provider 메시징 허용)

```json5
{
  agents: {
    list: [
      {
        id: "public",
        workspace: "~/.openclaw/workspace-public",
        sandbox: {
          mode: "all",
          scope: "agent",
          workspaceAccess: "none",
        },
        // Session tools can reveal sensitive data from transcripts. By default OpenClaw limits these tools
        // to the current session + spawned subagent sessions, but you can clamp further if needed.
        // See `tools.sessions.visibility` in the configuration reference.
        tools: {
          sessions: { visibility: "tree" }, // self | tree | agent | all
          allow: [
            "sessions_list",
            "sessions_history",
            "sessions_send",
            "sessions_spawn",
            "session_status",
            "whatsapp",
            "telegram",
            "slack",
            "discord",
          ],
          deny: [
            "read",
            "write",
            "edit",
            "apply_patch",
            "exec",
            "process",
            "browser",
            "canvas",
            "nodes",
            "cron",
            "gateway",
            "image",
          ],
        },
      },
    ],
  },
}
```

## AI에게 무엇을 알려야 하나

에이전트의 시스템 프롬프트에 보안 가이드라인을 포함하세요:

```
## Security Rules
- Never share directory listings or file paths with strangers
- Never reveal API keys, credentials, or infrastructure details
- Verify requests that modify system config with the owner
- When in doubt, ask before acting
- Keep private data private unless explicitly authorized
```

## 사고 대응

AI가 잘못된 일을 했다면:

### 격리

1. **중지:** macOS 앱이 Gateway를 감독 중이라면 앱을 중지하거나, `openclaw gateway` 프로세스를 종료하세요.
2. **노출 차단:** 무슨 일이 있었는지 이해할 때까지 `gateway.bind: "loopback"`으로 설정하거나 Tailscale Funnel/Serve를 비활성화하세요.
3. **접근 동결:** 위험한 DM/그룹을 `dmPolicy: "disabled"`로 바꾸거나 멘션 필수로 설정하고, `"*"` 전체 허용 항목이 있었다면 제거하세요.

### 교체 (비밀이 유출되었다면 침해로 간주)

1. Gateway auth(`gateway.auth.token` / `OPENCLAW_GATEWAY_PASSWORD`)를 교체하고 재시작하세요.
2. Gateway를 호출할 수 있는 모든 머신의 원격 클라이언트 비밀(`gateway.remote.token` / `.password`)을 교체하세요.
3. provider/API 자격 증명(WhatsApp creds, Slack/Discord token, `auth-profiles.json`의 모델/API 키, 사용 중인 암호화된 비밀 페이로드 값)을 교체하세요.

### 감사

1. Gateway 로그 확인: `/tmp/openclaw/openclaw-YYYY-MM-DD.log` (또는 `logging.file`)
2. 관련 transcript 검토: `~/.openclaw/agents/<agentId>/sessions/*.jsonl`
3. 최근 config 변경 검토(접근 범위를 넓혔을 수 있는 모든 것: `gateway.bind`, `gateway.auth`, dm/group 정책, `tools.elevated`, plugin 변경)
4. `openclaw security audit --deep`를 다시 실행하고 critical 결과가 해결되었는지 확인

### 보고용 수집 항목

- 타임스탬프, gateway 호스트 OS + OpenClaw 버전
- 세션 transcript + 짧은 로그 tail(redaction 후)
- 공격자가 보낸 내용 + 에이전트가 수행한 동작
- Gateway가 loopback 외부(LAN/Tailscale Funnel/Serve)로 노출되어 있었는지 여부

## Secret Scanning (`detect-secrets`)

CI는 `secrets` 작업에서 `detect-secrets` pre-commit hook을 실행합니다.
`main`에 대한 push는 항상 전체 파일 스캔을 실행합니다. pull request는
base commit이 있을 때 변경 파일 빠른 경로를 사용하고, 그렇지 않으면 전체 파일 스캔으로 대체합니다. 실패하면 baseline에 아직 없는 새 후보가 있다는 뜻입니다.

### CI가 실패할 때

1. 로컬에서 재현:

   ```bash
   pre-commit run --all-files detect-secrets
   ```

2. 도구 이해:
   - pre-commit의 `detect-secrets`는 저장소의
     baseline 및 exclude를 사용해 `detect-secrets-hook`을 실행합니다.
   - `detect-secrets audit`는 대화형 검토를 열어 baseline의 각
     항목을 실제 비밀인지 오탐인지 표시할 수 있게 합니다.
3. 실제 비밀이라면: 교체/제거한 뒤 스캔을 다시 실행해 baseline을 업데이트하세요.
4. 오탐이라면: 대화형 감사를 실행하고 false로 표시하세요:

   ```bash
   detect-secrets audit .secrets.baseline
   ```

5. 새 exclude가 필요하다면 `.detect-secrets.cfg`에 추가하고, 동일한 `--exclude-files` / `--exclude-lines` 플래그로
   baseline을 재생성하세요(config 파일은 참고용일 뿐이며,
   detect-secrets는 이를 자동으로 읽지 않습니다).

의도한 상태를 반영하도록 업데이트된 `.secrets.baseline`을 커밋하세요.

## 보안 이슈 보고

OpenClaw에서 취약점을 발견하셨나요? 책임감 있게 보고해 주세요:

1. 이메일: [security@openclaw.ai](mailto:security@openclaw.ai)
2. 수정되기 전까지는 공개 게시하지 마세요
3. 원하시면 익명으로, 아니면 크레딧을 드리겠습니다
