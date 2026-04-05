---
read_when:
    - 도구 출력으로 인한 컨텍스트 증가를 줄이려는 경우
    - Anthropic 프롬프트 캐시 최적화를 이해하려는 경우
summary: 컨텍스트를 가볍게 유지하고 캐싱 효율을 높이기 위해 오래된 도구 결과를 잘라내기
title: Session Pruning
x-i18n:
    generated_at: "2026-04-05T12:40:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1569a50e0018cca3e3ceefbdddaf093843df50cdf2f7bf62fe925299875cb487
    source_path: concepts/session-pruning.md
    workflow: 15
---

# Session Pruning

Session pruning은 각 LLM 호출 전에 컨텍스트에서 **오래된 도구 결과**를 잘라냅니다. 일반 대화 텍스트를 다시 쓰지 않고도 누적된 도구 출력(exec 결과, 파일 읽기, 검색 결과)으로 인한 컨텍스트 팽창을 줄여줍니다.

<Info>
Pruning은 메모리 내에서만 수행되며, 디스크에 있는 세션 transcript는 수정하지 않습니다.
전체 기록은 항상 보존됩니다.
</Info>

## 왜 중요한가

긴 세션은 컨텍스트 창을 부풀리는 도구 출력을 축적합니다. 이는 비용을 증가시키고 필요 이상으로 빨리 [compaction](/concepts/compaction)을 유발할 수 있습니다.

Pruning은 특히 **Anthropic 프롬프트 캐싱**에 유용합니다. 캐시 TTL이 만료된 후 다음 요청은 전체 프롬프트를 다시 캐시합니다. Pruning은 캐시 쓰기 크기를 줄여 비용을 직접적으로 낮춥니다.

## 작동 방식

1. 캐시 TTL이 만료될 때까지 기다립니다(기본값 5분).
2. 일반 pruning을 위해 오래된 도구 결과를 찾습니다(대화 텍스트는 그대로 둠).
3. 크기가 큰 결과를 **soft-trim**합니다 -- 앞부분과 끝부분을 유지하고 `...`를 삽입합니다.
4. 나머지는 **hard-clear**합니다 -- 플레이스홀더로 대체합니다.
5. 후속 요청이 새 캐시를 재사용하도록 TTL을 재설정합니다.

## 레거시 이미지 정리

OpenClaw는 기록에 원시 이미지 블록을 유지하던 오래된 레거시 세션에 대해 별도의 멱등 정리도 실행합니다.

- 최근의 **완료된 3개 턴**은 바이트 단위로 그대로 보존하여 최근 후속 요청의 프롬프트 캐시 접두사가 안정적으로 유지되도록 합니다.
- `user` 또는 `toolResult` 기록에 있는 오래되고 이미 처리된 이미지 블록은 `[image data removed - already processed by model]`로 대체될 수 있습니다.
- 이는 일반적인 캐시 TTL pruning과는 별개입니다. 이후 턴에서 반복된 이미지 payload가 프롬프트 캐시를 깨뜨리는 일을 막기 위해 존재합니다.

## 스마트 기본값

OpenClaw는 Anthropic 프로필에 대해 pruning을 자동으로 활성화합니다.

| 프로필 유형 | Pruning 활성화 | Heartbeat |
| ------------------------------------------------------- | --------------- | --------- |
| Anthropic OAuth/token auth(Claude CLI 재사용 포함) | 예             | 1시간    |
| API key                                                 | 예             | 30분    |

명시적인 값을 설정하면 OpenClaw는 이를 덮어쓰지 않습니다.

## 활성화 또는 비활성화

Anthropic이 아닌 공급자에 대해서는 pruning이 기본적으로 꺼져 있습니다. 활성화하려면:

```json5
{
  agents: {
    defaults: {
      contextPruning: { mode: "cache-ttl", ttl: "5m" },
    },
  },
}
```

비활성화하려면 `mode: "off"`로 설정하세요.

## Pruning과 compaction 비교

|            | Pruning            | Compaction              |
| ---------- | ------------------ | ----------------------- |
| **무엇을 하는가**   | 도구 결과를 잘라냄 | 대화를 요약함 |
| **저장됨?** | 아니요(요청별)   | 예(transcript에 저장)     |
| **범위**  | 도구 결과만  | 전체 대화     |

이 둘은 서로를 보완합니다 -- pruning은 compaction 주기 사이에서 도구 출력을 가볍게 유지합니다.

## 추가 읽을거리

- [Compaction](/concepts/compaction) -- 요약 기반 컨텍스트 축소
- [Gateway Configuration](/gateway/configuration) -- 모든 pruning config 옵션
  (`contextPruning.*`)
