---
read_when:
    - 채널 상태와 최근 세션 수신자에 대한 빠른 진단이 필요할 때
    - 디버깅용으로 붙여넣기 쉬운 “all” 상태 출력이 필요할 때
summary: '`openclaw status`용 CLI 참조(진단, 프로브, 사용량 스냅샷)'
title: status
x-i18n:
    generated_at: "2026-04-05T12:39:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: fbe9d94fbe9938cd946ee6f293b5bd3b464b75e1ade2eacdd851788c3bffe94e
    source_path: cli/status.md
    workflow: 15
---

# `openclaw status`

채널 + 세션 진단.

```bash
openclaw status
openclaw status --all
openclaw status --deep
openclaw status --usage
```

참고:

- `--deep`는 실시간 프로브를 실행합니다(WhatsApp Web + Telegram + Discord + Slack + Signal).
- `--usage`는 정규화된 provider 사용량 기간을 `X% 남음` 형식으로 출력합니다.
- MiniMax의 원시 `usage_percent` / `usagePercent` 필드는 남은 할당량이므로, OpenClaw는 표시 전에 이를 반전합니다. 개수 기반 필드가 있으면 그것이 우선합니다. `model_remains` 응답은 채팅 모델 항목을 우선 사용하고, 필요 시 타임스탬프에서 기간 레이블을 도출하며, 플랜 레이블에 모델 이름을 포함합니다.
- 현재 세션 스냅샷이 희소한 경우, `/status`는 가장 최근 transcript 사용량 로그에서 토큰 및 캐시 카운터를 보완할 수 있습니다. 기존의 0이 아닌 실시간 값은 transcript 대체값보다 계속 우선합니다.
- transcript 대체값은 실시간 세션 항목에 활성 런타임 모델 레이블이 없을 때 이를 복구할 수도 있습니다. 해당 transcript 모델이 선택된 모델과 다르면, status는 선택된 모델 대신 복구된 런타임 모델을 기준으로 컨텍스트 윈도우를 해석합니다.
- 프롬프트 크기 계산에서 session 메타데이터가 없거나 더 작으면 transcript 대체값은 더 큰 프롬프트 지향 합계를 우선 사용하므로, custom provider 세션이 `0` 토큰 표시로 축소되지 않습니다.
- 여러 에이전트가 구성된 경우 출력에는 에이전트별 세션 저장소가 포함됩니다.
- 개요에는 사용 가능한 경우 게이트웨이 + 노드 호스트 서비스 설치/런타임 상태가 포함됩니다.
- 개요에는 업데이트 채널 + git SHA(소스 체크아웃의 경우)가 포함됩니다.
- 업데이트 정보는 개요에 표시되며, 업데이트가 가능하면 status는 `openclaw update`를 실행하라는 힌트를 출력합니다([업데이트](/install/updating) 참조).
- 읽기 전용 status 표면(`status`, `status --json`, `status --all`)은 가능한 경우 대상 config 경로에 대해 지원되는 SecretRef를 해석합니다.
- 지원되는 채널 SecretRef가 구성되어 있지만 현재 명령 경로에서 사용할 수 없는 경우, status는 충돌하지 않고 읽기 전용 상태를 유지하며 저하된 출력을 보고합니다. 사람이 읽는 출력에는 “현재 명령 경로에서 구성된 토큰을 사용할 수 없음” 같은 경고가 표시되고, JSON 출력에는 `secretDiagnostics`가 포함됩니다.
- 명령 로컬 SecretRef 해석이 성공하면 status는 해석된 스냅샷을 우선 사용하고 최종 출력에서 일시적인 “secret unavailable” 채널 마커를 제거합니다.
- `status --all`에는 Secrets 개요 행과, 보고서 생성을 중단하지 않고 secret 진단을 요약하는 진단 섹션(가독성을 위해 잘림)이 포함됩니다.
