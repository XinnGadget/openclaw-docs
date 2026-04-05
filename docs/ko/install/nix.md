---
read_when:
    - 재현 가능하고 롤백 가능한 설치를 원하는 경우
    - 이미 Nix/NixOS/Home Manager를 사용 중인 경우
    - 모든 것을 고정하고 선언적으로 관리하려는 경우
summary: Nix로 OpenClaw를 선언적으로 설치하기
title: Nix
x-i18n:
    generated_at: "2026-04-05T12:46:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 14e1e73533db1350d82d3a786092b4328121a082dfeeedee7c7574021dada546
    source_path: install/nix.md
    workflow: 15
---

# Nix 설치

배터리 포함형 Home Manager 모듈인 **[nix-openclaw](https://github.com/openclaw/nix-openclaw)**로 OpenClaw를 선언적으로 설치하세요.

<Info>
Nix 설치의 기준 정보는 [nix-openclaw](https://github.com/openclaw/nix-openclaw) 저장소입니다. 이 페이지는 빠른 개요입니다.
</Info>

## 제공되는 것

- Gateway + macOS 앱 + 도구(whisper, spotify, cameras) -- 모두 고정됨
- 재부팅 후에도 유지되는 Launchd 서비스
- 선언적 config를 사용하는 plugin 시스템
- 즉시 롤백: `home-manager switch --rollback`

## 빠른 시작

<Steps>
  <Step title="Determinate Nix 설치">
    Nix가 아직 설치되지 않았다면 [Determinate Nix installer](https://github.com/DeterminateSystems/nix-installer) 안내를 따르세요.
  </Step>
  <Step title="로컬 flake 만들기">
    nix-openclaw 저장소의 agent-first 템플릿을 사용하세요:
    ```bash
    mkdir -p ~/code/openclaw-local
    # nix-openclaw repo에서 templates/agent-first/flake.nix 복사
    ```
  </Step>
  <Step title="secrets 구성">
    메시징 봇 토큰과 모델 공급자 API 키를 설정하세요. `~/.secrets/`의 일반 파일로도 충분합니다.
  </Step>
  <Step title="템플릿 플레이스홀더 채우고 적용">
    ```bash
    home-manager switch
    ```
  </Step>
  <Step title="확인">
    launchd 서비스가 실행 중인지, 봇이 메시지에 응답하는지 확인하세요.
  </Step>
</Steps>

전체 모듈 옵션과 예시는 [nix-openclaw README](https://github.com/openclaw/nix-openclaw)를 참조하세요.

## Nix 모드 런타임 동작

`OPENCLAW_NIX_MODE=1`이 설정되면(`nix-openclaw`에서 자동 설정됨), OpenClaw는 자동 설치 흐름을 비활성화하는 결정적 모드로 들어갑니다.

수동으로도 설정할 수 있습니다:

```bash
export OPENCLAW_NIX_MODE=1
```

macOS에서는 GUI 앱이 셸 환경 변수를 자동으로 상속하지 않습니다. 대신 defaults를 통해 Nix 모드를 활성화하세요:

```bash
defaults write ai.openclaw.mac openclaw.nixMode -bool true
```

### Nix 모드에서 바뀌는 점

- 자동 설치 및 자기 변경 흐름이 비활성화됨
- 누락된 의존성은 Nix 전용 해결 메시지로 표시됨
- UI에 읽기 전용 Nix 모드 배너가 표시됨

### Config 및 상태 경로

OpenClaw는 `OPENCLAW_CONFIG_PATH`에서 JSON5 config를 읽고, 변경 가능한 데이터는 `OPENCLAW_STATE_DIR`에 저장합니다. Nix에서 실행할 때는 런타임 상태와 config가 불변 스토어 밖에 유지되도록 이를 Nix가 관리하는 위치로 명시적으로 설정하세요.

| 변수 | 기본값 |
| ---------------------- | --------------------------------------- |
| `OPENCLAW_HOME`        | `HOME` / `USERPROFILE` / `os.homedir()` |
| `OPENCLAW_STATE_DIR`   | `~/.openclaw`                           |
| `OPENCLAW_CONFIG_PATH` | `$OPENCLAW_STATE_DIR/openclaw.json`     |

## 관련 문서

- [nix-openclaw](https://github.com/openclaw/nix-openclaw) -- 전체 설정 가이드
- [Wizard](/ko/start/wizard) -- 비-Nix CLI 설정
- [Docker](/install/docker) -- 컨테이너 기반 설정
