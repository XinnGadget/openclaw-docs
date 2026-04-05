---
read_when:
    - 시맨틱 메모리를 인덱싱하거나 검색하려고 함
    - 메모리 가용성 또는 인덱싱을 디버그하는 중
    - 회상된 단기 메모리를 `MEMORY.md`로 승격하려고 함
summary: '`openclaw memory`용 CLI 참조(status/index/search/promote)'
title: memory
x-i18n:
    generated_at: "2026-04-05T12:38:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: a89e3a819737bb63521128ae63d9e25b5cd9db35c3ea4606d087a8ad48b41eab
    source_path: cli/memory.md
    workflow: 15
---

# `openclaw memory`

시맨틱 메모리 인덱싱 및 검색을 관리합니다.
활성 메모리 plugin이 제공합니다(기본값: `memory-core`; 비활성화하려면 `plugins.slots.memory = "none"` 설정).

관련 문서:

- 메모리 개념: [Memory](/concepts/memory)
- Plugins: [Plugins](/tools/plugin)

## 예시

```bash
openclaw memory status
openclaw memory status --deep
openclaw memory status --fix
openclaw memory index --force
openclaw memory search "meeting notes"
openclaw memory search --query "deployment" --max-results 20
openclaw memory promote --limit 10 --min-score 0.75
openclaw memory promote --apply
openclaw memory promote --json --min-recall-count 0 --min-unique-queries 0
openclaw memory status --json
openclaw memory status --deep --index
openclaw memory status --deep --index --verbose
openclaw memory status --agent main
openclaw memory index --agent main --verbose
```

## 옵션

`memory status` 및 `memory index`:

- `--agent <id>`: 단일 에이전트로 범위를 제한합니다. 이 옵션이 없으면 이 명령들은 구성된 각 에이전트에 대해 실행되며, 구성된 에이전트 목록이 없으면 기본 에이전트로 폴백합니다.
- `--verbose`: 프로브 및 인덱싱 중 상세 로그를 출력합니다.

`memory status`:

- `--deep`: 벡터 + 임베딩 가용성을 프로브합니다.
- `--index`: 저장소가 dirty 상태이면 재인덱싱을 실행합니다(`--deep` 포함).
- `--fix`: 오래된 recall lock을 복구하고 promotion 메타데이터를 정규화합니다.
- `--json`: JSON 출력을 표시합니다.

`memory index`:

- `--force`: 전체 재인덱싱을 강제로 수행합니다.

`memory search`:

- 쿼리 입력: 위치 인자 `[query]` 또는 `--query <text>` 중 하나를 전달합니다.
- 둘 다 제공되면 `--query`가 우선합니다.
- 둘 다 없으면 명령은 오류와 함께 종료됩니다.
- `--agent <id>`: 단일 에이전트로 범위를 제한합니다(기본값: 기본 에이전트).
- `--max-results <n>`: 반환할 결과 수를 제한합니다.
- `--min-score <n>`: 점수가 낮은 일치 항목을 필터링합니다.
- `--json`: JSON 결과를 출력합니다.

`memory promote`:

단기 메모리 promotion을 미리 보고 적용합니다.

```bash
openclaw memory promote [--apply] [--limit <n>] [--include-promoted]
```

- `--apply` -- promotion을 `MEMORY.md`에 기록합니다(기본값: 미리보기만).
- `--limit <n>` -- 표시할 후보 수를 제한합니다.
- `--include-promoted` -- 이전 주기에서 이미 승격된 항목도 포함합니다.

전체 옵션:

- 가중 recall 신호(`frequency`, `relevance`, `query diversity`, `recency`)를 사용해 `memory/YYYY-MM-DD.md`의 단기 후보를 순위화합니다.
- `memory_search`가 일일 메모리 히트를 반환할 때 캡처된 recall 이벤트를 사용합니다.
- 선택적 자동 dreaming 모드: `plugins.entries.memory-core.config.dreaming.mode`가 `core`, `deep`, 또는 `rem`이면 `memory-core`가 백그라운드에서 promotion을 트리거하는 cron 작업을 자동으로 관리합니다(수동 `openclaw cron add` 불필요).
- `--agent <id>`: 단일 에이전트로 범위를 제한합니다(기본값: 기본 에이전트).
- `--limit <n>`: 반환/적용할 최대 후보 수입니다.
- `--min-score <n>`: 최소 가중 promotion 점수입니다.
- `--min-recall-count <n>`: 후보에 필요한 최소 recall 횟수입니다.
- `--min-unique-queries <n>`: 후보에 필요한 최소 고유 쿼리 수입니다.
- `--apply`: 선택된 후보를 `MEMORY.md`에 추가하고 승격된 것으로 표시합니다.
- `--include-promoted`: 출력에 이미 승격된 후보를 포함합니다.
- `--json`: JSON 출력을 표시합니다.

## Dreaming (실험적)

Dreaming은 메모리를 위한 야간 반영 패스입니다. 시스템이 낮 동안 회상된 내용을 다시 살펴보고 무엇을 장기적으로 유지할 가치가 있는지 판단하기 때문에 "dreaming"이라고 부릅니다.

- 옵트인 기능이며 기본적으로 비활성화되어 있습니다.
- `plugins.entries.memory-core.config.dreaming.mode`로 활성화합니다.
- 채팅에서 `/dreaming off|core|rem|deep`로 모드를 전환할 수 있습니다. 각 모드의 동작을 보려면 `/dreaming`(또는 `/dreaming options`)을 실행하세요.
- 활성화되면 `memory-core`가 관리형 cron 작업을 자동으로 생성하고 유지합니다.
- dreaming은 활성화하되 자동 promotion을 사실상 일시 정지하려면 `dreaming.limit`를 `0`으로 설정하세요.
- 순위화는 가중 신호를 사용합니다: recall 빈도, 검색 관련성, 쿼리 다양성, 시간적 최신성(최근 recall은 시간이 지나며 감쇠함).
- `MEMORY.md`로의 promotion은 품질 임계값을 충족할 때만 일어나므로 장기 메모리는 일회성 세부 정보가 쌓이지 않고 높은 신호를 유지합니다.

기본 모드 프리셋:

- `core`: 매일 `0 3 * * *`, `minScore=0.75`, `minRecallCount=3`, `minUniqueQueries=2`
- `deep`: 12시간마다(`0 */12 * * *`), `minScore=0.8`, `minRecallCount=3`, `minUniqueQueries=3`
- `rem`: 6시간마다(`0 */6 * * *`), `minScore=0.85`, `minRecallCount=4`, `minUniqueQueries=3`

예시:

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

참고:

- `memory index --verbose`는 단계별 세부 정보(provider, 모델, 소스, 배치 활동)를 출력합니다.
- `memory status`에는 `memorySearch.extraPaths`를 통해 구성된 추가 경로가 모두 포함됩니다.
- 실질적으로 활성인 메모리 원격 API 키 필드가 SecretRef로 구성되어 있으면, 이 명령은 활성 gateway 스냅샷에서 해당 값을 확인합니다. gateway를 사용할 수 없으면 명령은 즉시 실패합니다.
- Gateway 버전 불일치 참고: 이 명령 경로에는 `secrets.resolve`를 지원하는 gateway가 필요합니다. 오래된 gateway는 unknown-method 오류를 반환합니다.
- dreaming 주기는 기본적으로 각 모드의 프리셋 일정입니다. `plugins.entries.memory-core.config.dreaming.frequency`를 cron 표현식(예: `0 3 * * *`)으로 설정해 주기를 재정의하고, `timezone`, `limit`, `minScore`, `minRecallCount`, `minUniqueQueries`로 세부 조정할 수 있습니다.
