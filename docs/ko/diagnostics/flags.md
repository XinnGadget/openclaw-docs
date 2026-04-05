---
read_when:
    - 전역 로깅 수준을 높이지 않고 대상별 디버그 로그가 필요할 때
    - 지원용으로 하위 시스템별 로그를 수집해야 할 때
summary: 대상별 디버그 로그를 위한 진단 플래그
title: 진단 플래그
x-i18n:
    generated_at: "2026-04-05T12:41:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: daf0eca0e6bd1cbc2c400b2e94e1698709a96b9cdba1a8cf00bd580a61829124
    source_path: diagnostics/flags.md
    workflow: 15
---

# 진단 플래그

진단 플래그를 사용하면 전체에서 verbose 로깅을 켜지 않고도 대상별 디버그 로그를 활성화할 수 있습니다. 플래그는 opt-in이며, 하위 시스템이 이를 확인하지 않으면 아무 효과도 없습니다.

## 동작 방식

- 플래그는 문자열입니다(대소문자 구분 없음).
- config 또는 env 재정의를 통해 플래그를 활성화할 수 있습니다.
- 와일드카드를 지원합니다:
  - `telegram.*`는 `telegram.http`와 일치합니다
  - `*`는 모든 플래그를 활성화합니다

## config를 통한 활성화

```json
{
  "diagnostics": {
    "flags": ["telegram.http"]
  }
}
```

여러 플래그:

```json
{
  "diagnostics": {
    "flags": ["telegram.http", "gateway.*"]
  }
}
```

플래그를 변경한 후 게이트웨이를 다시 시작하세요.

## env 재정의(일회성)

```bash
OPENCLAW_DIAGNOSTICS=telegram.http,telegram.payload
```

모든 플래그 비활성화:

```bash
OPENCLAW_DIAGNOSTICS=0
```

## 로그 위치

플래그는 표준 진단 로그 파일에 로그를 기록합니다. 기본값:

```
/tmp/openclaw/openclaw-YYYY-MM-DD.log
```

`logging.file`을 설정한 경우 해당 경로를 대신 사용합니다. 로그는 JSONL 형식입니다(줄당 JSON 객체 하나). `logging.redactSensitive`에 따른 마스킹은 계속 적용됩니다.

## 로그 추출

가장 최신 로그 파일 선택:

```bash
ls -t /tmp/openclaw/openclaw-*.log | head -n 1
```

Telegram HTTP 진단 필터링:

```bash
rg "telegram http error" /tmp/openclaw/openclaw-*.log
```

또는 재현하면서 tail:

```bash
tail -f /tmp/openclaw/openclaw-$(date +%F).log | rg "telegram http error"
```

원격 게이트웨이의 경우 `openclaw logs --follow`도 사용할 수 있습니다([/cli/logs](/cli/logs) 참조).

## 참고

- `logging.level`이 `warn`보다 높게 설정되어 있으면 이 로그가 억제될 수 있습니다. 기본값 `info`면 괜찮습니다.
- 플래그는 켜 둬도 안전합니다. 특정 하위 시스템의 로그량에만 영향을 줍니다.
- 로그 대상, 수준, 마스킹을 변경하려면 [/logging](/logging)을 사용하세요.
