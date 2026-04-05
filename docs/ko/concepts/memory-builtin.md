---
read_when:
    - 기본 메모리 백엔드를 이해하려고 함
    - 임베딩 provider 또는 하이브리드 검색을 구성하려고 함
summary: 키워드, 벡터 및 하이브리드 검색을 지원하는 기본 SQLite 기반 메모리 백엔드
title: 내장 메모리 엔진
x-i18n:
    generated_at: "2026-04-05T12:39:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 181c40a43332315bf915ff6f395d9d5fd766c889e1a8d1aa525f9ba0198d3367
    source_path: concepts/memory-builtin.md
    workflow: 15
---

# 내장 메모리 엔진

내장 엔진은 기본 메모리 백엔드입니다. 에이전트별 SQLite 데이터베이스에
메모리 인덱스를 저장하며, 시작하는 데 추가 의존성이 필요하지 않습니다.

## 제공 기능

- **키워드 검색**: FTS5 전문 인덱싱(BM25 점수화) 사용.
- **벡터 검색**: 지원되는 모든 provider의 임베딩 사용.
- **하이브리드 검색**: 두 방식을 결합해 최상의 결과 제공.
- **CJK 지원**: 중국어, 일본어, 한국어를 위한 trigram 토큰화.
- **sqlite-vec 가속**: 데이터베이스 내 벡터 쿼리 지원(선택 사항).

## 시작하기

OpenAI, Gemini, Voyage 또는 Mistral용 API 키가 있으면 내장
엔진이 이를 자동 감지하여 벡터 검색을 활성화합니다. 별도 config가 필요 없습니다.

provider를 명시적으로 설정하려면 다음과 같이 하세요.

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
      },
    },
  },
}
```

임베딩 provider가 없으면 키워드 검색만 사용할 수 있습니다.

## 지원되는 임베딩 provider

| Provider | ID        | 자동 감지 | 참고                                |
| -------- | --------- | --------- | ----------------------------------- |
| OpenAI   | `openai`  | 예        | 기본값: `text-embedding-3-small`    |
| Gemini   | `gemini`  | 예        | 멀티모달(이미지 + 오디오) 지원      |
| Voyage   | `voyage`  | 예        |                                     |
| Mistral  | `mistral` | 예        |                                     |
| Ollama   | `ollama`  | 아니요    | 로컬, 명시적으로 설정해야 함        |
| Local    | `local`   | 예(첫 번째) | GGUF 모델, 약 0.6GB 다운로드      |

자동 감지는 API 키를 확인할 수 있는 첫 번째 provider를 위 표의
순서대로 선택합니다. 재정의하려면 `memorySearch.provider`를 설정하세요.

## 인덱싱 동작 방식

OpenClaw는 `MEMORY.md`와 `memory/*.md`를 청크(~400 토큰, 80토큰
중첩)로 인덱싱하고 에이전트별 SQLite 데이터베이스에 저장합니다.

- **인덱스 위치:** `~/.openclaw/memory/<agentId>.sqlite`
- **파일 감시:** 메모리 파일 변경 시 디바운스된 재인덱싱(1.5초)이 트리거됩니다.
- **자동 재인덱싱:** 임베딩 provider, 모델 또는 청킹 config가
  변경되면 전체 인덱스를 자동으로 다시 빌드합니다.
- **온디맨드 재인덱싱:** `openclaw memory index --force`

<Info>
`memorySearch.extraPaths`를 사용하면 workspace 외부의 Markdown 파일도
인덱싱할 수 있습니다. 자세한 내용은
[configuration reference](/reference/memory-config#additional-memory-paths)를 참조하세요.
</Info>

## 사용 시점

내장 엔진은 대부분의 사용자에게 적합한 선택입니다.

- 추가 의존성 없이 바로 사용할 수 있습니다.
- 키워드 검색과 벡터 검색을 모두 잘 처리합니다.
- 모든 임베딩 providers를 지원합니다.
- 하이브리드 검색은 두 검색 접근 방식의 장점을 결합합니다.

리랭킹, 쿼리 확장, 또는 workspace 외부 디렉터리 인덱싱이 필요하다면
[QMD](/concepts/memory-qmd)로 전환하는 것을 고려하세요.

자동 사용자 모델링이 포함된 세션 간 메모리가 필요하다면
[Honcho](/concepts/memory-honcho)를 고려하세요.

## 문제 해결

**메모리 검색이 비활성화되었나요?** `openclaw memory status`를 확인하세요. 감지된 provider가
없다면 하나를 명시적으로 설정하거나 API 키를 추가하세요.

**결과가 오래되었나요?** `openclaw memory index --force`를 실행해 다시 빌드하세요. 감시기가
드물게 일부 변경을 놓칠 수 있습니다.

**sqlite-vec가 로드되지 않나요?** OpenClaw는 자동으로 프로세스 내 코사인 유사도로
폴백합니다. 구체적인 로드 오류는 로그를 확인하세요.

## 구성

임베딩 provider 설정, 하이브리드 검색 튜닝(가중치, MMR, 시간적
감쇠), 배치 인덱싱, 멀티모달 메모리, sqlite-vec, 추가 경로 및 기타
모든 config 옵션은
[Memory configuration reference](/reference/memory-config)를 참조하세요.
