---
read_when:
    - macOS Skills 설정 UI를 업데이트하는 경우
    - Skills 게이팅 또는 설치 동작을 변경하는 경우
summary: macOS Skills 설정 UI 및 Gateway 기반 상태
title: Skills (macOS)
x-i18n:
    generated_at: "2026-04-05T12:48:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7ffd6744646d2c8770fa12a5e511f84a40b5ece67181139250ec4cc4301b49b8
    source_path: platforms/mac/skills.md
    workflow: 15
---

# Skills (macOS)

macOS 앱은 OpenClaw Skills를 게이트웨이를 통해 표시하며, 로컬에서 Skills를 파싱하지 않습니다.

## 데이터 소스

- `skills.status`(게이트웨이)는 모든 Skills와 적격성, 누락된 요구 사항을 반환합니다
  (번들 Skills에 대한 허용 목록 차단 포함).
- 요구 사항은 각 `SKILL.md`의 `metadata.openclaw.requires`에서 파생됩니다.

## 설치 작업

- `metadata.openclaw.install`은 설치 옵션(brew/node/go/uv)을 정의합니다.
- 앱은 `skills.install`을 호출해 게이트웨이 호스트에서 installer를 실행합니다.
- 내장된 dangerous-code `critical` 결과는 기본적으로 `skills.install`을 차단합니다. 의심스러운 결과는 여전히 경고만 표시합니다. dangerous override는 게이트웨이 요청에 존재하지만, 기본 앱 흐름은 실패 시 닫힘 방식을 유지합니다.
- 모든 설치 옵션이 `download`인 경우, 게이트웨이는 모든 다운로드
  선택지를 표시합니다.
- 그렇지 않으면, 게이트웨이는 현재
  설치 기본 설정과 호스트 바이너리를 사용해 하나의 선호 installer를 선택합니다:
  `skills.install.preferBrew`가 활성화되어 있고 `brew`가 존재하면 Homebrew를 우선하고, 그다음 `uv`, 그다음
  `skills.install.nodeManager`에 구성된 node manager, 이후
  `go` 또는 `download` 같은 fallback을 사용합니다.
- Node 설치 라벨은 `yarn`을 포함하여 구성된 node manager를 반영합니다.

## Env/API keys

- 앱은 키를 `~/.openclaw/openclaw.json`의 `skills.entries.<skillKey>` 아래에 저장합니다.
- `skills.update`는 `enabled`, `apiKey`, `env`를 패치합니다.

## 원격 모드

- 설치 + config 업데이트는 로컬 Mac이 아니라 게이트웨이 호스트에서 이루어집니다.
