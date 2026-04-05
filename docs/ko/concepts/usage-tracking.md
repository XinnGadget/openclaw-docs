---
read_when:
    - provider 사용량/할당량 표시를 연결하는 중
    - 사용량 추적 동작이나 인증 요구 사항을 설명해야 함
summary: 사용량 추적 표시 위치와 자격 증명 요구 사항
title: 사용량 추적
x-i18n:
    generated_at: "2026-04-05T12:41:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62164492c61a8d602e3b73879c13ce3e14ce35964b7f2ffd389a4e6a7ec7e9c0
    source_path: concepts/usage-tracking.md
    workflow: 15
---

# 사용량 추적

## 개요

- provider 사용량/할당량을 해당 provider의 사용량 엔드포인트에서 직접 가져옵니다.
- 비용 추정은 하지 않으며, provider가 보고한 기간만 사용합니다.
- 사람이 읽기 쉬운 상태 출력은 상위 API가 사용된 할당량, 남은 할당량, 또는 원시 카운트만 보고하더라도 `X% left` 형식으로 정규화됩니다.
- 세션 수준 `/status` 및 `session_status`는 라이브 세션 스냅샷이 부족할 때 최신
  기록 사용량 항목으로 폴백할 수 있습니다. 이 폴백은 누락된 토큰/캐시 카운터를 채우고, 활성 런타임
  모델 레이블을 복구할 수 있으며, 세션 메타데이터가 없거나 더 작을 때 더 큰 프롬프트 지향 합계를 우선합니다. 기존의 0이 아닌 라이브 값은 여전히 우선합니다.

## 표시 위치

- 채팅의 `/status`: 세션 토큰 + 예상 비용(API 키 전용)이 포함된 이모지 중심 상태 카드. provider 사용량은 사용 가능한 경우 **현재 모델 provider**에 대해 정규화된 `X% left` 기간으로 표시됩니다.
- 채팅의 `/usage off|tokens|full`: 응답별 사용량 푸터(OAuth는 토큰만 표시).
- 채팅의 `/usage cost`: OpenClaw 세션 로그를 기준으로 집계된 로컬 비용 요약.
- CLI: `openclaw status --usage`는 provider별 전체 세부 내역을 출력합니다.
- CLI: `openclaw channels list`는 동일한 사용량 스냅샷을 provider config와 함께 출력합니다(건너뛰려면 `--no-usage` 사용).
- macOS 메뉴 막대: Context 아래의 “Usage” 섹션(사용 가능한 경우에만).

## Providers + 자격 증명

- **Anthropic (Claude)**: 인증 프로필의 OAuth 토큰.
- **GitHub Copilot**: 인증 프로필의 OAuth 토큰.
- **Gemini CLI**: 인증 프로필의 OAuth 토큰.
  - JSON 사용량은 `stats`로 폴백하며, `stats.cached`는
    `cacheRead`로 정규화됩니다.
- **OpenAI Codex**: 인증 프로필의 OAuth 토큰(accountId가 있으면 사용).
- **MiniMax**: API 키 또는 MiniMax OAuth 인증 프로필. OpenClaw는
  `minimax`, `minimax-cn`, `minimax-portal`을 동일한 MiniMax 할당량
  표면으로 취급하고, 저장된 MiniMax OAuth가 있으면 이를 우선 사용하며, 그렇지 않으면
  `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, 또는 `MINIMAX_API_KEY`로 폴백합니다.
  MiniMax의 원시 `usage_percent` / `usagePercent` 필드는 **남은**
  할당량을 의미하므로, OpenClaw는 표시 전에 이를 반전합니다. 카운트 기반 필드가 있으면
  그것이 우선합니다.
  - coding-plan 기간 레이블은 provider의 시간/분 필드가 있으면 이를 사용하고, 없으면 `start_time` / `end_time` 범위로 폴백합니다.
  - coding-plan 엔드포인트가 `model_remains`를 반환하면, OpenClaw는
    채팅 모델 항목을 우선하고, 명시적인
    `window_hours` / `window_minutes` 필드가 없을 때는 타임스탬프에서 기간 레이블을 도출하며, 계획 레이블에 모델
    이름을 포함합니다.
- **Xiaomi MiMo**: env/config/auth 저장소의 API 키 (`XIAOMI_API_KEY`).
- **z.ai**: env/config/auth 저장소의 API 키.

사용 가능한 provider 사용량 인증을 확인할 수 없으면 사용량은 숨겨집니다. Providers는 plugin별 사용량 인증 로직을 제공할 수 있으며, 그렇지 않으면 OpenClaw는 인증 프로필, 환경 변수, 또는 config에서 일치하는 OAuth/API 키 자격 증명으로 폴백합니다.
