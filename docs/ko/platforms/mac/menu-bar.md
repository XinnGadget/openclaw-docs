---
read_when:
    - mac 메뉴 UI 또는 상태 로직을 조정할 때
summary: 메뉴 막대 상태 로직과 사용자에게 표시되는 내용
title: 메뉴 막대
x-i18n:
    generated_at: "2026-04-05T12:48:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8eb73c0e671a76aae4ebb653c65147610bf3e6d3c9c0943d150e292e7761d16d
    source_path: platforms/mac/menu-bar.md
    workflow: 15
---

# 메뉴 막대 상태 로직

## 표시되는 내용

- 현재 에이전트 작업 상태를 메뉴 막대 아이콘과 메뉴의 첫 번째 상태 행에 표시합니다.
- 작업이 활성화되어 있는 동안에는 상태가 숨겨지며, 모든 세션이 idle 상태가 되면 다시 표시됩니다.
- 메뉴의 “Nodes” 블록에는 **device**만 나열됩니다(`node.list`를 통한 페어링된 node). client/presence 항목은 포함되지 않습니다.
- provider 사용량 스냅샷을 사용할 수 있으면 Context 아래에 “Usage” 섹션이 표시됩니다.

## 상태 모델

- 세션: 이벤트는 payload에 `runId`(실행별)와 `sessionKey`를 함께 담아 도착합니다. “main” 세션은 키 `main`이며, 없으면 가장 최근에 업데이트된 세션으로 대체합니다.
- 우선순위: main이 항상 우선합니다. main이 활성 상태이면 그 상태가 즉시 표시됩니다. main이 idle이면 가장 최근에 활성화된 non‑main 세션이 표시됩니다. 활동 도중에는 상태가 왔다 갔다 하지 않으며, 현재 세션이 idle이 되거나 main이 활성화될 때만 전환합니다.
- 활동 종류:
  - `job`: 상위 수준 명령 실행(`state: started|streaming|done|error`)
  - `tool`: `toolName`과 `meta/args`가 포함된 `phase: start|result`

## `IconState` enum (Swift)

- `idle`
- `workingMain(ActivityKind)`
- `workingOther(ActivityKind)`
- `overridden(ActivityKind)` (디버그 재정의)

### `ActivityKind` → glyph

- `exec` → 💻
- `read` → 📄
- `write` → ✍️
- `edit` → 📝
- `attach` → 📎
- 기본값 → 🛠️

### 시각적 매핑

- `idle`: 일반 critter.
- `workingMain`: glyph가 있는 배지, 전체 tint, 다리 “작업 중” 애니메이션.
- `workingOther`: glyph가 있는 배지, 약한 tint, scurry 없음.
- `overridden`: 활동과 관계없이 선택한 glyph/tint를 사용.

## 상태 행 텍스트 (메뉴)

- 작업이 활성 상태일 때: `<Session role> · <activity label>`
  - 예: `Main · exec: pnpm test`, `Other · read: apps/macos/Sources/OpenClaw/AppState.swift`
- idle일 때: 상태 요약으로 대체됩니다.

## 이벤트 수집

- 소스: control-channel `agent` 이벤트(`ControlChannel.handleAgentEvent`)
- 파싱되는 필드:
  - 시작/중지를 위한 `data.state`가 있는 `stream: "job"`
  - `data.phase`, `name`, 선택적 `meta`/`args`가 있는 `stream: "tool"`
- 라벨:
  - `exec`: `args.command`의 첫 번째 줄
  - `read`/`write`: 축약된 경로
  - `edit`: `meta`/diff 개수에서 추론한 변경 종류와 경로
  - 대체값: 도구 이름

## 디버그 재정의

- Settings ▸ Debug ▸ “Icon override” 선택기:
  - `System (auto)` (기본값)
  - `Working: main` (도구 종류별)
  - `Working: other` (도구 종류별)
  - `Idle`
- `@AppStorage("iconOverride")`를 통해 저장되며 `IconState.overridden`에 매핑됩니다.

## 테스트 체크리스트

- main 세션 job 트리거: 아이콘이 즉시 전환되고 상태 행에 main 라벨이 표시되는지 확인
- main이 idle일 때 non‑main 세션 job 트리거: 아이콘/상태에 non‑main이 표시되고 끝날 때까지 안정적으로 유지되는지 확인
- 다른 세션이 활성 상태일 때 main 시작: 아이콘이 즉시 main으로 전환되는지 확인
- 빠른 도구 버스트: 배지가 깜빡이지 않는지 확인(tool result에 대한 TTL 유예)
- 모든 세션이 idle이 되면 상태 행이 다시 나타나는지 확인
