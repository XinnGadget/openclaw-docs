---
read_when:
    - 머신에서 OpenClaw를 제거하려고 할 때
    - 제거 후에도 gateway 서비스가 계속 실행 중일 때
summary: OpenClaw를 완전히 제거하기(CLI, 서비스, 상태, 워크스페이스)
title: 제거
x-i18n:
    generated_at: "2026-04-05T12:47:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 34c7d3e4ad17333439048dfda739fc27db47e7f9e4212fe17db0e4eb3d3ab258
    source_path: install/uninstall.md
    workflow: 15
---

# 제거

두 가지 경로가 있습니다:

- `openclaw`가 아직 설치되어 있으면 **간편 경로**
- CLI는 사라졌지만 서비스가 계속 실행 중이면 **수동 서비스 제거**

## 간편 경로 (CLI가 아직 설치됨)

권장: 내장 제거 프로그램 사용:

```bash
openclaw uninstall
```

비대화형(자동화 / npx):

```bash
openclaw uninstall --all --yes --non-interactive
npx -y openclaw uninstall --all --yes --non-interactive
```

수동 단계(동일한 결과):

1. gateway 서비스 중지:

```bash
openclaw gateway stop
```

2. gateway 서비스 제거(launchd/systemd/schtasks):

```bash
openclaw gateway uninstall
```

3. 상태 + 구성 삭제:

```bash
rm -rf "${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
```

`OPENCLAW_CONFIG_PATH`를 상태 디렉터리 외부의 사용자 지정 위치로 설정했다면 해당 파일도 삭제하세요.

4. 워크스페이스 삭제(선택 사항, 에이전트 파일 제거):

```bash
rm -rf ~/.openclaw/workspace
```

5. CLI 설치 제거(사용한 방법 선택):

```bash
npm rm -g openclaw
pnpm remove -g openclaw
bun remove -g openclaw
```

6. macOS 앱을 설치했다면:

```bash
rm -rf /Applications/OpenClaw.app
```

참고:

- profile(`--profile` / `OPENCLAW_PROFILE`)을 사용했다면 각 상태 디렉터리(기본값 `~/.openclaw-<profile>`)에 대해 3단계를 반복하세요.
- 원격 모드에서는 상태 디렉터리가 **gateway 호스트**에 있으므로, 거기서도 1-4단계를 실행해야 합니다.

## 수동 서비스 제거 (CLI가 설치되어 있지 않음)

gateway 서비스가 계속 실행되지만 `openclaw`가 없는 경우에 사용하세요.

### macOS (launchd)

기본 label은 `ai.openclaw.gateway`입니다(또는 `ai.openclaw.<profile>`; 레거시 `com.openclaw.*`가 남아 있을 수 있음):

```bash
launchctl bootout gui/$UID/ai.openclaw.gateway
rm -f ~/Library/LaunchAgents/ai.openclaw.gateway.plist
```

profile을 사용했다면 label과 plist 이름을 `ai.openclaw.<profile>`로 바꾸세요. 레거시 `com.openclaw.*` plist가 있으면 함께 제거하세요.

### Linux (systemd user unit)

기본 unit 이름은 `openclaw-gateway.service`입니다(또는 `openclaw-gateway-<profile>.service`):

```bash
systemctl --user disable --now openclaw-gateway.service
rm -f ~/.config/systemd/user/openclaw-gateway.service
systemctl --user daemon-reload
```

### Windows (Scheduled Task)

기본 작업 이름은 `OpenClaw Gateway`입니다(또는 `OpenClaw Gateway (<profile>)`).
작업 스크립트는 상태 디렉터리 아래에 있습니다.

```powershell
schtasks /Delete /F /TN "OpenClaw Gateway"
Remove-Item -Force "$env:USERPROFILE\.openclaw\gateway.cmd"
```

profile을 사용했다면 일치하는 작업 이름과 `~\.openclaw-<profile>\gateway.cmd`를 삭제하세요.

## 일반 설치 vs 소스 체크아웃

### 일반 설치 (install.sh / npm / pnpm / bun)

`https://openclaw.ai/install.sh` 또는 `install.ps1`를 사용했다면 CLI는 `npm install -g openclaw@latest`로 설치된 것입니다.
`npm rm -g openclaw`로 제거하세요(또는 해당 방식으로 설치했다면 `pnpm remove -g` / `bun remove -g`).

### 소스 체크아웃 (git clone)

저장소 체크아웃에서 실행 중이라면(`git clone` + `openclaw ...` / `bun run openclaw ...`):

1. 저장소를 삭제하기 **전에** gateway 서비스를 제거하세요(위의 간편 경로 또는 수동 서비스 제거 사용).
2. 저장소 디렉터리를 삭제하세요.
3. 위에 설명된 대로 상태 + 워크스페이스를 제거하세요.
