---
read_when:
    - 메모리 검색 provider 또는 임베딩 모델을 구성하려는 경우
    - QMD 백엔드를 설정하려는 경우
    - 하이브리드 검색, MMR 또는 시간 감쇠를 조정하려는 경우
    - 멀티모달 메모리 인덱싱을 활성화하려는 경우
summary: 메모리 검색, 임베딩 provider, QMD, 하이브리드 검색, 멀티모달 인덱싱을 위한 모든 구성 옵션
title: 메모리 구성 참조
x-i18n:
    generated_at: "2026-04-05T12:54:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: 89e4c9740f71f5a47fc5e163742339362d6b95cb4757650c0c8a095cf3078caa
    source_path: reference/memory-config.md
    workflow: 15
---

# 메모리 구성 참조

이 페이지에는 OpenClaw 메모리 검색을 위한 모든 구성 옵션이 나열되어 있습니다. 개념적 개요는 다음을 참조하세요:

- [메모리 개요](/ko/concepts/memory) -- 메모리의 작동 방식
- [내장 엔진](/ko/concepts/memory-builtin) -- 기본 SQLite 백엔드
- [QMD 엔진](/ko/concepts/memory-qmd) -- 로컬 우선 사이드카
- [메모리 검색](/ko/concepts/memory-search) -- 검색 파이프라인 및 튜닝

별도 언급이 없는 한 모든 메모리 검색 설정은 `openclaw.json`의
`agents.defaults.memorySearch` 아래에 있습니다.

---

## provider 선택

| 키         | 타입      | 기본값         | 설명                                                                         |
| ---------- | --------- | -------------- | ---------------------------------------------------------------------------- |
| `provider` | `string`  | 자동 감지      | 임베딩 어댑터 ID: `openai`, `gemini`, `voyage`, `mistral`, `ollama`, `local` |
| `model`    | `string`  | provider 기본값 | 임베딩 모델 이름                                                             |
| `fallback` | `string`  | `"none"`       | 기본 provider가 실패할 때 사용할 폴백 어댑터 ID                              |
| `enabled`  | `boolean` | `true`         | 메모리 검색 활성화 또는 비활성화                                             |

### 자동 감지 순서

`provider`가 설정되지 않은 경우 OpenClaw는 사용 가능한 첫 번째 항목을 선택합니다:

1. `local` -- `memorySearch.local.modelPath`가 구성되어 있고 파일이 존재하는 경우
2. `openai` -- OpenAI 키를 확인할 수 있는 경우
3. `gemini` -- Gemini 키를 확인할 수 있는 경우
4. `voyage` -- Voyage 키를 확인할 수 있는 경우
5. `mistral` -- Mistral 키를 확인할 수 있는 경우

`ollama`는 지원되지만 자동 감지는 되지 않습니다(명시적으로 설정해야 함).

### API 키 확인

원격 임베딩에는 API 키가 필요합니다. OpenClaw는 다음 위치에서 이를 확인합니다:
인증 프로필, `models.providers.*.apiKey`, 또는 환경 변수.

| Provider | env var                        | 구성 키                           |
| -------- | ------------------------------ | --------------------------------- |
| OpenAI   | `OPENAI_API_KEY`               | `models.providers.openai.apiKey`  |
| Gemini   | `GEMINI_API_KEY`               | `models.providers.google.apiKey`  |
| Voyage   | `VOYAGE_API_KEY`               | `models.providers.voyage.apiKey`  |
| Mistral  | `MISTRAL_API_KEY`              | `models.providers.mistral.apiKey` |
| Ollama   | `OLLAMA_API_KEY` (자리표시자)  | --                                |

Codex OAuth는 채팅/completions만 지원하며 임베딩 요청에는 적용되지 않습니다.

---

## 원격 엔드포인트 구성

사용자 지정 OpenAI 호환 엔드포인트를 사용하거나 provider 기본값을 재정의하려면:

| 키               | 타입     | 설명                                          |
| ---------------- | -------- | --------------------------------------------- |
| `remote.baseUrl` | `string` | 사용자 지정 API 기본 URL                      |
| `remote.apiKey`  | `string` | API 키 재정의                                 |
| `remote.headers` | `object` | 추가 HTTP 헤더(provider 기본값과 병합됨)      |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        remote: {
          baseUrl: "https://api.example.com/v1/",
          apiKey: "YOUR_KEY",
        },
      },
    },
  },
}
```

---

## Gemini 전용 구성

| 키                     | 타입     | 기본값                 | 설명                                       |
| ---------------------- | -------- | ---------------------- | ------------------------------------------ |
| `model`                | `string` | `gemini-embedding-001` | `gemini-embedding-2-preview`도 지원        |
| `outputDimensionality` | `number` | `3072`                 | Embedding 2의 경우: 768, 1536 또는 3072    |

<Warning>
모델 또는 `outputDimensionality`를 변경하면 자동으로 전체 재인덱싱이 수행됩니다.
</Warning>

---

## 로컬 임베딩 구성

| 키                    | 타입     | 기본값                 | 설명                           |
| --------------------- | -------- | ---------------------- | ------------------------------ |
| `local.modelPath`     | `string` | 자동 다운로드          | GGUF 모델 파일 경로            |
| `local.modelCacheDir` | `string` | node-llama-cpp 기본값  | 다운로드된 모델의 캐시 디렉터리 |

기본 모델: `embeddinggemma-300m-qat-Q8_0.gguf`(~0.6 GB, 자동 다운로드).
네이티브 빌드가 필요합니다: `pnpm approve-builds` 후 `pnpm rebuild node-llama-cpp`.

---

## 하이브리드 검색 구성

모두 `memorySearch.query.hybrid` 아래에 있습니다:

| 키                    | 타입      | 기본값  | 설명                              |
| --------------------- | --------- | ------- | --------------------------------- |
| `enabled`             | `boolean` | `true`  | 하이브리드 BM25 + 벡터 검색 활성화 |
| `vectorWeight`        | `number`  | `0.7`   | 벡터 점수 가중치(0-1)             |
| `textWeight`          | `number`  | `0.3`   | BM25 점수 가중치(0-1)             |
| `candidateMultiplier` | `number`  | `4`     | 후보 풀 크기 배수                 |

### MMR (다양성)

| 키            | 타입      | 기본값  | 설명                                 |
| ------------- | --------- | ------- | ------------------------------------ |
| `mmr.enabled` | `boolean` | `false` | MMR 재순위 지정 활성화               |
| `mmr.lambda`  | `number`  | `0.7`   | 0 = 최대 다양성, 1 = 최대 관련성     |

### 시간 감쇠 (최신성)

| 키                           | 타입      | 기본값  | 설명                          |
| ---------------------------- | --------- | ------- | ----------------------------- |
| `temporalDecay.enabled`      | `boolean` | `false` | 최신성 부스트 활성화          |
| `temporalDecay.halfLifeDays` | `number`  | `30`    | N일마다 점수가 절반으로 감소  |

상시 파일(`MEMORY.md`, `memory/` 내 날짜가 없는 파일)은 감쇠되지 않습니다.

### 전체 예시

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        query: {
          hybrid: {
            vectorWeight: 0.7,
            textWeight: 0.3,
            mmr: { enabled: true, lambda: 0.7 },
            temporalDecay: { enabled: true, halfLifeDays: 30 },
          },
        },
      },
    },
  },
}
```

---

## 추가 메모리 경로

| 키           | 타입       | 설명                                |
| ------------ | ---------- | ----------------------------------- |
| `extraPaths` | `string[]` | 인덱싱할 추가 디렉터리 또는 파일    |

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        extraPaths: ["../team-docs", "/srv/shared-notes"],
      },
    },
  },
}
```

경로는 절대 경로이거나 워크스페이스 상대 경로일 수 있습니다. 디렉터리는 `.md`
파일을 찾기 위해 재귀적으로 스캔됩니다. 심볼릭 링크 처리 방식은 활성 백엔드에 따라 다릅니다:
내장 엔진은 심볼릭 링크를 무시하고, QMD는 기본 QMD 스캐너 동작을 따릅니다.

에이전트 범위의 교차 에이전트 transcript 검색에는
`memory.qmd.paths` 대신 `agents.list[].memorySearch.qmd.extraCollections`를 사용하세요.
이 추가 컬렉션은 동일한 `{ path, name, pattern? }` 형태를 따르지만,
에이전트별로 병합되며 경로가 현재 워크스페이스 외부를 가리킬 때 명시적인 공유 이름을
유지할 수 있습니다.
동일한 확인된 경로가 `memory.qmd.paths`와
`memorySearch.qmd.extraCollections` 양쪽에 나타나면, QMD는 첫 번째 항목을 유지하고
중복 항목은 건너뜁니다.

---

## 멀티모달 메모리 (Gemini)

Gemini Embedding 2를 사용하여 Markdown과 함께 이미지와 오디오를 인덱싱합니다:

| 키                        | 타입       | 기본값     | 설명                                      |
| ------------------------- | ---------- | ---------- | ----------------------------------------- |
| `multimodal.enabled`      | `boolean`  | `false`    | 멀티모달 인덱싱 활성화                    |
| `multimodal.modalities`   | `string[]` | --         | `["image"]`, `["audio"]` 또는 `["all"]`   |
| `multimodal.maxFileBytes` | `number`   | `10000000` | 인덱싱할 최대 파일 크기                   |

`extraPaths`의 파일에만 적용됩니다. 기본 메모리 루트는 Markdown 전용으로 유지됩니다.
`gemini-embedding-2-preview`가 필요합니다. `fallback`은 `"none"`이어야 합니다.

지원 형식: `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`, `.heic`, `.heif`
(이미지); `.mp3`, `.wav`, `.ogg`, `.opus`, `.m4a`, `.aac`, `.flac` (오디오).

---

## 임베딩 캐시

| 키                 | 타입      | 기본값  | 설명                              |
| ------------------ | --------- | ------- | --------------------------------- |
| `cache.enabled`    | `boolean` | `false` | SQLite에 청크 임베딩 캐시         |
| `cache.maxEntries` | `number`  | `50000` | 최대 캐시 임베딩 수               |

재인덱싱 또는 transcript 업데이트 중 변경되지 않은 텍스트를 다시 임베딩하는 것을 방지합니다.

---

## 배치 인덱싱

| 키                            | 타입      | 기본값  | 설명                         |
| ----------------------------- | --------- | ------- | ---------------------------- |
| `remote.batch.enabled`        | `boolean` | `false` | 배치 임베딩 API 활성화       |
| `remote.batch.concurrency`    | `number`  | `2`     | 병렬 배치 작업 수            |
| `remote.batch.wait`           | `boolean` | `true`  | 배치 완료까지 대기           |
| `remote.batch.pollIntervalMs` | `number`  | --      | 폴링 간격                    |
| `remote.batch.timeoutMinutes` | `number`  | --      | 배치 타임아웃                |

`openai`, `gemini`, `voyage`에서 사용할 수 있습니다. OpenAI 배치는 일반적으로
대규모 백필에서 가장 빠르고 비용이 가장 저렴합니다.

---

## 세션 메모리 검색 (실험적)

세션 transcript를 인덱싱하고 `memory_search`를 통해 노출합니다:

| 키                              | 타입       | 기본값       | 설명                                        |
| ------------------------------- | ---------- | ------------ | ------------------------------------------- |
| `experimental.sessionMemory`    | `boolean`  | `false`      | 세션 인덱싱 활성화                          |
| `sources`                       | `string[]` | `["memory"]` | transcript를 포함하려면 `"sessions"` 추가   |
| `sync.sessions.deltaBytes`      | `number`   | `100000`     | 재인덱싱을 위한 바이트 임계값               |
| `sync.sessions.deltaMessages`   | `number`   | `50`         | 재인덱싱을 위한 메시지 임계값               |

세션 인덱싱은 옵트인이며 비동기적으로 실행됩니다. 결과가 약간 오래되었을 수 있습니다.
세션 로그는 디스크에 저장되므로 파일시스템 액세스를 신뢰 경계로 취급하세요.

---

## SQLite 벡터 가속 (sqlite-vec)

| 키                           | 타입      | 기본값   | 설명                              |
| ---------------------------- | --------- | -------- | --------------------------------- |
| `store.vector.enabled`       | `boolean` | `true`   | 벡터 쿼리에 sqlite-vec 사용       |
| `store.vector.extensionPath` | `string`  | 번들 포함 | sqlite-vec 경로 재정의            |

sqlite-vec를 사용할 수 없는 경우, OpenClaw는 자동으로 프로세스 내 cosine
similarity로 폴백합니다.

---

## 인덱스 저장소

| 키                    | 타입     | 기본값                                | 설명                                       |
| --------------------- | -------- | ------------------------------------- | ------------------------------------------ |
| `store.path`          | `string` | `~/.openclaw/memory/{agentId}.sqlite` | 인덱스 위치(`{agentId}` 토큰 지원)         |
| `store.fts.tokenizer` | `string` | `unicode61`                           | FTS5 tokenizer(`unicode61` 또는 `trigram`) |

---

## QMD 백엔드 구성

활성화하려면 `memory.backend = "qmd"`로 설정합니다. 모든 QMD 설정은
`memory.qmd` 아래에 있습니다:

| 키                       | 타입      | 기본값   | 설명                                          |
| ------------------------ | --------- | -------- | --------------------------------------------- |
| `command`                | `string`  | `qmd`    | QMD 실행 파일 경로                            |
| `searchMode`             | `string`  | `search` | 검색 명령: `search`, `vsearch`, `query`       |
| `includeDefaultMemory`   | `boolean` | `true`   | `MEMORY.md` + `memory/**/*.md` 자동 인덱싱    |
| `paths[]`                | `array`   | --       | 추가 경로: `{ name, path, pattern? }`         |
| `sessions.enabled`       | `boolean` | `false`  | 세션 transcript 인덱싱                        |
| `sessions.retentionDays` | `number`  | --       | transcript 보존 기간                          |
| `sessions.exportDir`     | `string`  | --       | 내보내기 디렉터리                             |

### 업데이트 일정

| 키                        | 타입      | 기본값   | 설명                                 |
| ------------------------- | --------- | -------- | ------------------------------------ |
| `update.interval`         | `string`  | `5m`     | 새로 고침 간격                       |
| `update.debounceMs`       | `number`  | `15000`  | 파일 변경 디바운스                   |
| `update.onBoot`           | `boolean` | `true`   | 시작 시 새로 고침                    |
| `update.waitForBootSync`  | `boolean` | `false`  | 새로 고침 완료까지 시작 차단         |
| `update.embedInterval`    | `string`  | --       | 별도 임베딩 주기                     |
| `update.commandTimeoutMs` | `number`  | --       | QMD 명령 타임아웃                    |
| `update.updateTimeoutMs`  | `number`  | --       | QMD 업데이트 작업 타임아웃           |
| `update.embedTimeoutMs`   | `number`  | --       | QMD 임베딩 작업 타임아웃             |

### 제한

| 키                        | 타입     | 기본값  | 설명                          |
| ------------------------- | -------- | ------- | ----------------------------- |
| `limits.maxResults`       | `number` | `6`     | 최대 검색 결과 수             |
| `limits.maxSnippetChars`  | `number` | --      | 스니펫 길이 제한              |
| `limits.maxInjectedChars` | `number` | --      | 전체 주입 문자 수 제한        |
| `limits.timeoutMs`        | `number` | `4000`  | 검색 타임아웃                 |

### 범위

어떤 세션이 QMD 검색 결과를 받을 수 있는지 제어합니다.
[`session.sendPolicy`](/ko/gateway/configuration-reference#session)와 동일한 스키마입니다:

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

기본값은 DM 전용입니다. `match.keyPrefix`는 정규화된 세션 키와 일치하고,
`match.rawKeyPrefix`는 `agent:<id>:`를 포함한 원시 키와 일치합니다.

### 인용

`memory.citations`는 모든 백엔드에 적용됩니다:

| 값               | 동작                                                |
| ---------------- | --------------------------------------------------- |
| `auto` (기본값)  | 스니펫에 `Source: <path#line>` 바닥글 포함          |
| `on`             | 항상 바닥글 포함                                    |
| `off`            | 바닥글 생략(경로는 여전히 내부적으로 에이전트에 전달) |

### 전체 QMD 예시

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      includeDefaultMemory: true,
      update: { interval: "5m", debounceMs: 15000 },
      limits: { maxResults: 6, timeoutMs: 4000 },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

---

## Dreaming (실험적)

Dreaming은 `agents.defaults.memorySearch` 아래가 아니라
`plugins.entries.memory-core.config.dreaming` 아래에서 구성합니다. 개념 설명 및 채팅
명령은 [Dreaming](/ko/concepts/memory-dreaming)을 참조하세요.

| 키                 | 타입     | 기본값         | 설명                                      |
| ------------------ | -------- | -------------- | ----------------------------------------- |
| `mode`             | `string` | `"off"`        | 프리셋: `off`, `core`, `rem`, 또는 `deep` |
| `cron`             | `string` | 프리셋 기본값  | 일정용 cron 표현식 재정의                 |
| `timezone`         | `string` | 사용자 시간대  | 일정 평가에 사용할 시간대                 |
| `limit`            | `number` | 프리셋 기본값  | 사이클당 승격할 최대 후보 수              |
| `minScore`         | `number` | 프리셋 기본값  | 승격을 위한 최소 가중 점수                |
| `minRecallCount`   | `number` | 프리셋 기본값  | 최소 recall 횟수 임계값                   |
| `minUniqueQueries` | `number` | 프리셋 기본값  | 최소 고유 쿼리 수 임계값                  |

### 프리셋 기본값

| 모드   | 주기            | minScore | minRecallCount | minUniqueQueries |
| ------ | --------------- | -------- | -------------- | ---------------- |
| `off`  | 비활성화        | --       | --             | --               |
| `core` | 매일 오전 3시   | 0.75     | 3              | 2                |
| `rem`  | 6시간마다       | 0.85     | 4              | 3                |
| `deep` | 12시간마다      | 0.80     | 3              | 3                |

### 예시

```json5
{
  plugins: {
    entries: {
      "memory-core": {
        config: {
          dreaming: {
            mode: "core",
            timezone: "America/New_York",
          },
        },
      },
    },
  },
}
```
