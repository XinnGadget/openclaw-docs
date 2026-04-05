---
read_when:
    - 메모리 승격을 자동으로 실행하고 싶을 때
    - dreaming 모드와 임계값을 이해하고 싶을 때
    - MEMORY.md를 오염시키지 않고 통합을 조정하고 싶을 때
summary: 단기 회상에서 장기 메모리로의 백그라운드 승격
title: Dreaming(실험적)
x-i18n:
    generated_at: "2026-04-05T12:39:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: e9dbb29e9b49e940128c4e08c3fd058bb6ebb0148ca214b78008e3d5763ef1ab
    source_path: concepts/memory-dreaming.md
    workflow: 15
---

# Dreaming(실험적)

Dreaming은 `memory-core`의 백그라운드 메모리 통합 단계입니다.

이를 "dreaming"이라고 부르는 이유는 시스템이 하루 동안 떠올랐던 내용을 다시 살펴보고
무엇을 지속적인 컨텍스트로 남길 가치가 있는지 판단하기 때문입니다.

Dreaming은 **실험적**이며, **opt-in**이고, **기본적으로 비활성화**되어 있습니다.

## Dreaming이 하는 일

1. `memory/YYYY-MM-DD.md`에서 `memory_search` 적중으로부터 단기 회상 이벤트를 추적합니다.
2. 가중 신호를 사용해 해당 회상 후보에 점수를 매깁니다.
3. 자격을 충족한 후보만 `MEMORY.md`로 승격합니다.

이렇게 하면 장기 메모리가 일회성 세부 정보가 아니라 지속적이고 반복되는 컨텍스트에 집중할 수 있습니다.

## 승격 신호

Dreaming은 네 가지 신호를 결합합니다:

- **빈도**: 동일한 후보가 얼마나 자주 회상되었는지
- **관련성**: 검색되었을 때 회상 점수가 얼마나 높았는지
- **쿼리 다양성**: 서로 다른 쿼리 의도가 몇 개나 이를 드러냈는지
- **최신성**: 최근 회상에 대한 시간 가중치

승격되려면 하나의 신호만이 아니라 구성된 모든 임계값 게이트를 통과해야 합니다.

### 신호 가중치

| 신호 | 가중치 | 설명 |
| ---- | ------ | ---- |
| 빈도 | 0.35 | 동일한 항목이 얼마나 자주 회상되었는지 |
| 관련성 | 0.35 | 검색되었을 때의 평균 회상 점수 |
| 다양성 | 0.15 | 이를 드러낸 서로 다른 쿼리 의도의 수 |
| 최신성 | 0.15 | 시간 감쇠(14일 반감기) |

## 동작 방식

1. **회상 추적** -- 모든 `memory_search` 적중은 회상 횟수, 점수, 쿼리 해시와 함께 `memory/.dreams/short-term-recall.json`에 기록됩니다.
2. **예약된 점수 계산** -- 구성된 주기에 따라 후보를 가중 신호로 순위화합니다. 모든 임계값 게이트를 동시에 통과해야 합니다.
3. **승격** -- 자격을 충족한 항목은 승격 타임스탬프와 함께 `MEMORY.md`에 추가됩니다.
4. **정리** -- 이미 승격된 항목은 이후 주기에서 제외됩니다. 파일 잠금으로 동시 실행을 방지합니다.

## 모드

`dreaming.mode`는 주기와 기본 임계값을 제어합니다:

| 모드 | 주기 | minScore | minRecallCount | minUniqueQueries |
| ---- | ---- | -------- | -------------- | ---------------- |
| `off` | 비활성화 | -- | -- | -- |
| `core` | 매일 오전 3시 | 0.75 | 3 | 2 |
| `rem` | 6시간마다 | 0.85 | 4 | 3 |
| `deep` | 12시간마다 | 0.80 | 3 | 3 |

## 스케줄링 모델

Dreaming이 활성화되면 `memory-core`가 반복 일정을 자동으로 관리합니다. 이 기능을 위해 cron 작업을 수동으로 만들 필요는 없습니다.

다음과 같은 명시적 재정의로 동작을 조정할 수는 있습니다:

- `dreaming.frequency` (cron 식)
- `dreaming.timezone`
- `dreaming.limit`
- `dreaming.minScore`
- `dreaming.minRecallCount`
- `dreaming.minUniqueQueries`

## 구성

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "mode": "core"
          }
        }
      }
    }
  }
}
```

## 채팅 명령

채팅에서 모드를 전환하고 상태를 확인할 수 있습니다:

```
/dreaming core          # core 모드로 전환(매일 밤)
/dreaming rem           # rem 모드로 전환(6시간마다)
/dreaming deep          # deep 모드로 전환(12시간마다)
/dreaming off           # dreaming 비활성화
/dreaming status        # 현재 config와 주기 표시
/dreaming help          # 모드 가이드 표시
```

## CLI 명령

명령줄에서 승격을 미리 보고 적용할 수 있습니다:

```bash
# 승격 후보 미리보기
openclaw memory promote

# 승격을 MEMORY.md에 적용
openclaw memory promote --apply

# 미리보기 개수 제한
openclaw memory promote --limit 5

# 이미 승격된 항목 포함
openclaw memory promote --include-promoted

# dreaming 상태 확인
openclaw memory status --deep
```

전체 플래그 참조는 [memory CLI](/cli/memory)를 참조하세요.

## Dreams UI

Dreaming이 활성화되면 게이트웨이 사이드바에 **Dreams** 탭이 표시되며,
메모리 통계(단기 개수, 장기 개수, 승격 개수)와 다음 예약 실행 시간이 나타납니다.

## 추가 읽을거리

- [Memory](/concepts/memory)
- [Memory Search](/concepts/memory-search)
- [memory CLI](/cli/memory)
- [Memory configuration reference](/reference/memory-config)
