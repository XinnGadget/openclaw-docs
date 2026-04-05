---
read_when:
    - 메모리가 어떻게 작동하는지 이해하고 싶은 경우
    - 어떤 메모리 파일에 기록해야 하는지 알고 싶은 경우
summary: OpenClaw가 세션 간에 정보를 기억하는 방법
title: 메모리 개요
x-i18n:
    generated_at: "2026-04-05T12:40:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 89fbd20cf2bcdf461a9e311ee0ff43b5f69d9953519656eecd419b4a419256f8
    source_path: concepts/memory.md
    workflow: 15
---

# 메모리 개요

OpenClaw는 에이전트의 워크스페이스에 **일반 Markdown 파일**을 작성하여 정보를 기억합니다.
모델은 디스크에 저장된 것만 "기억"하며, 숨겨진 상태는 없습니다.

## 작동 방식

에이전트에는 메모리를 저장할 수 있는 두 곳이 있습니다.

- **`MEMORY.md`** -- 장기 메모리. 지속되는 사실, 선호 사항, 결정 사항입니다.
  모든 DM 세션 시작 시 로드됩니다.
- **`memory/YYYY-MM-DD.md`** -- 일일 메모. 진행 중인 컨텍스트와 관찰 내용을 담습니다.
  오늘과 어제의 메모는 자동으로 로드됩니다.

이 파일들은 에이전트 워크스페이스(기본값 `~/.openclaw/workspace`)에 있습니다.

<Tip>
에이전트가 어떤 것을 기억하길 원한다면 그냥 요청하세요: "내가 TypeScript를
선호한다고 기억해." 그러면 적절한 파일에 기록합니다.
</Tip>

## 메모리 도구

에이전트에는 메모리 작업을 위한 두 가지 도구가 있습니다.

- **`memory_search`** -- 원래 표현과 말이 달라도
  의미 기반 검색으로 관련 메모를 찾습니다.
- **`memory_get`** -- 특정 메모리 파일 또는 줄 범위를 읽습니다.

두 도구 모두 활성 메모리 plugin(기본값: `memory-core`)에서 제공됩니다.

## 메모리 검색

임베딩 provider가 구성되어 있으면 `memory_search`는 **하이브리드
검색**을 사용합니다. 즉, 벡터 유사도(의미적 의미)와 키워드 일치
(ID나 코드 심볼 같은 정확한 용어)를 결합합니다. 지원되는 provider의 API key만 있으면
별도 설정 없이 바로 동작합니다.

<Info>
OpenClaw는 사용 가능한 API key를 바탕으로 임베딩 provider를 자동 감지합니다.
OpenAI, Gemini, Voyage, 또는 Mistral key가 구성되어 있으면 메모리 검색이
자동으로 활성화됩니다.
</Info>

검색 작동 방식, 튜닝 옵션, provider 설정에 대한 자세한 내용은
[Memory Search](/concepts/memory-search)를 참조하세요.

## 메모리 백엔드

<CardGroup cols={3}>
<Card title="내장(기본값)" icon="database" href="/concepts/memory-builtin">
SQLite 기반입니다. 키워드 검색, 벡터 유사도, 하이브리드 검색을 별도
종속성 없이 바로 사용할 수 있습니다.
</Card>
<Card title="QMD" icon="search" href="/concepts/memory-qmd">
재순위화, 쿼리 확장, 워크스페이스 외부 디렉터리 인덱싱 기능을 제공하는
로컬 우선 사이드카입니다.
</Card>
<Card title="Honcho" icon="brain" href="/concepts/memory-honcho">
사용자 모델링, 의미 검색, 다중 에이전트 인식을 제공하는
AI 네이티브 세션 간 메모리입니다. plugin 설치가 필요합니다.
</Card>
</CardGroup>

## 자동 메모리 플러시

[압축](/concepts/compaction)이 대화를 요약하기 전에 OpenClaw는
에이전트에게 중요한 컨텍스트를 메모리 파일에 저장하라고 상기시키는
자동 무음 턴을 실행합니다. 이것은 기본적으로 활성화되어 있으므로 별도 구성이 필요 없습니다.

<Tip>
메모리 플러시는 압축 중 컨텍스트 손실을 방지합니다. 대화 안에 중요한 사실이
아직 파일에 기록되지 않았다면, 요약이 일어나기 전에 자동으로 저장됩니다.
</Tip>

## Dreaming (experimental)

Dreaming은 메모리를 위한 선택적 백그라운드 통합 패스입니다. 일일 파일
(`memory/YYYY-MM-DD.md`)의 단기 회상을 다시 검토하고 점수를 매긴 뒤,
조건을 충족한 항목만 장기 메모리(`MEMORY.md`)로 승격합니다.

이는 장기 메모리의 신호 대 잡음비를 높게 유지하도록 설계되었습니다.

- **옵트인 방식**: 기본적으로 비활성화되어 있습니다.
- **예약 실행**: 활성화되면 `memory-core`가 반복 작업을 자동으로
  관리합니다.
- **임계값 적용**: 승격은 점수, 회상 빈도, 쿼리
  다양성 게이트를 통과해야 합니다.

모드 동작(`off`, `core`, `rem`, `deep`), 점수 신호, 튜닝 옵션에 대해서는
[Dreaming (experimental)](/concepts/memory-dreaming)을 참조하세요.

## CLI

```bash
openclaw memory status          # 인덱스 상태 및 provider 확인
openclaw memory search "query"  # 명령줄에서 검색
openclaw memory index --force   # 인덱스 다시 빌드
```

## 추가 읽을거리

- [Builtin Memory Engine](/concepts/memory-builtin) -- 기본 SQLite 백엔드
- [QMD Memory Engine](/concepts/memory-qmd) -- 고급 로컬 우선 사이드카
- [Honcho Memory](/concepts/memory-honcho) -- AI 네이티브 세션 간 메모리
- [Memory Search](/concepts/memory-search) -- 검색 파이프라인, provider, 튜닝
- [Dreaming (experimental)](/concepts/memory-dreaming) -- 단기 회상에서
  장기 메모리로의 백그라운드 승격
- [Memory configuration reference](/reference/memory-config) -- 모든 config 옵션
- [Compaction](/concepts/compaction) -- 압축이 메모리와 상호작용하는 방식
