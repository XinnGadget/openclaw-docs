---
read_when:
    - mac 디버그 빌드를 빌드하거나 서명하는 경우
summary: 패키징 스크립트가 생성한 macOS 디버그 빌드용 서명 단계
title: macOS 서명
x-i18n:
    generated_at: "2026-04-05T12:49:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7b16d726549cf6dc34dc9c60e14d8041426ebc0699ab59628aca1d094380334a
    source_path: platforms/mac/signing.md
    workflow: 15
---

# mac 서명(디버그 빌드)

이 앱은 보통 [`scripts/package-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-app.sh)에서 빌드되며, 현재 이 스크립트는 다음을 수행합니다:

- 안정적인 디버그 번들 식별자 설정: `ai.openclaw.mac.debug`
- 해당 번들 ID로 Info.plist를 기록함(`BUNDLE_ID=...`로 재정의 가능)
- [`scripts/codesign-mac-app.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/codesign-mac-app.sh)를 호출하여 메인 바이너리와 앱 번들을 서명하므로, macOS가 각 리빌드를 동일한 서명된 번들로 인식하고 TCC 권한(알림, 손쉬운 사용, 화면 기록, 마이크, 음성)을 유지합니다. 안정적인 권한 유지를 위해 실제 서명 identity를 사용하세요. ad-hoc는 선택적 opt-in이며 취약합니다([macOS permissions](/platforms/mac/permissions) 참조).
- 기본적으로 `CODESIGN_TIMESTAMP=auto`를 사용함. 이는 Developer ID 서명에 대해 신뢰된 타임스탬프를 활성화합니다. 타임스탬프를 건너뛰려면 `CODESIGN_TIMESTAMP=off`로 설정하세요(오프라인 디버그 빌드).
- 빌드 메타데이터를 Info.plist에 주입함: `OpenClawBuildTimestamp`(UTC)와 `OpenClawGitCommit`(짧은 해시)로 About 패널에서 빌드, git, 디버그/릴리스 채널을 표시할 수 있게 함.
- **패키징은 기본적으로 Node 24를 사용함**: 이 스크립트는 TS 빌드와 Control UI 빌드를 실행합니다. 호환성을 위해 Node 22 LTS(현재 `22.14+`)도 계속 지원됩니다.
- 환경 변수에서 `SIGN_IDENTITY`를 읽음. 셸 rc에 `export SIGN_IDENTITY="Apple Development: Your Name (TEAMID)"`(또는 Developer ID Application 인증서)를 추가하면 항상 해당 인증서로 서명할 수 있습니다. ad-hoc 서명은 `ALLOW_ADHOC_SIGNING=1` 또는 `SIGN_IDENTITY="-"`로 명시적으로 opt-in해야 합니다(권한 테스트에는 권장되지 않음).
- 서명 후 Team ID 감사를 실행하며, 앱 번들 내부의 어떤 Mach-O라도 다른 Team ID로 서명되어 있으면 실패합니다. 이를 우회하려면 `SKIP_TEAM_ID_CHECK=1`을 설정하세요.

## 사용법

```bash
# 저장소 루트에서
scripts/package-mac-app.sh               # identity를 자동 선택; 없으면 오류
SIGN_IDENTITY="Developer ID Application: Your Name" scripts/package-mac-app.sh   # 실제 인증서
ALLOW_ADHOC_SIGNING=1 scripts/package-mac-app.sh    # ad-hoc (권한이 유지되지 않음)
SIGN_IDENTITY="-" scripts/package-mac-app.sh        # 명시적 ad-hoc (동일한 주의 사항)
DISABLE_LIBRARY_VALIDATION=1 scripts/package-mac-app.sh   # 개발 전용 Sparkle Team ID 불일치 우회책
```

### Ad-hoc 서명 참고

`SIGN_IDENTITY="-"`(ad-hoc)로 서명할 때, 스크립트는 자동으로 **Hardened Runtime**(`--options runtime`)을 비활성화합니다. 이는 앱이 동일한 Team ID를 공유하지 않는 내장 프레임워크(예: Sparkle)를 로드하려 할 때 충돌을 방지하기 위해 필요합니다. Ad-hoc 서명은 또한 TCC 권한 지속성을 깨뜨립니다. 복구 단계는 [macOS permissions](/platforms/mac/permissions)를 참조하세요.

## About용 빌드 메타데이터

`package-mac-app.sh`는 번들에 다음을 기록합니다:

- `OpenClawBuildTimestamp`: 패키징 시점의 ISO8601 UTC
- `OpenClawGitCommit`: 짧은 git 해시(없으면 `unknown`)

About 탭은 이 키를 읽어 버전, 빌드 날짜, git 커밋, 디버그 빌드 여부(`#if DEBUG`를 통해)를 표시합니다. 코드 변경 후 이 값을 갱신하려면 패키저를 다시 실행하세요.

## 이유

TCC 권한은 번들 식별자와 코드 서명 모두에 연결됩니다. UUID가 바뀌는 서명되지 않은 디버그 빌드 때문에 macOS가 리빌드할 때마다 권한 부여를 잊는 문제가 있었습니다. 바이너리를 서명하고(기본값은 ad-hoc) 고정된 번들 ID/경로(`dist/OpenClaw.app`)를 유지하면 빌드 간 권한이 유지되며, 이는 VibeTunnel 접근 방식과 일치합니다.
