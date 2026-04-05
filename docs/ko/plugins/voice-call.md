---
read_when:
    - OpenClaw에서 아웃바운드 음성 통화를 발신하려는 경우
    - voice-call 플러그인을 구성하거나 개발하는 경우
summary: 'Voice Call 플러그인: Twilio/Telnyx/Plivo를 통한 아웃바운드 + 인바운드 통화(플러그인 설치 + 구성 + CLI)'
title: Voice Call 플러그인
x-i18n:
    generated_at: "2026-04-05T12:51:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e6d10c9fde6ce1f51637af285edc0c710e9cb7702231c0a91b527b721eaddc1
    source_path: plugins/voice-call.md
    workflow: 15
---

# Voice Call (플러그인)

플러그인을 통한 OpenClaw용 음성 통화입니다. 아웃바운드 알림과
인바운드 정책이 적용된 다중 턴 대화를 지원합니다.

현재 provider:

- `twilio` (Programmable Voice + Media Streams)
- `telnyx` (Call Control v2)
- `plivo` (Voice API + XML transfer + GetInput speech)
- `mock` (개발용/네트워크 없음)

빠른 개념 정리:

- 플러그인 설치
- Gateway 재시작
- `plugins.entries.voice-call.config` 아래에 구성
- `openclaw voicecall ...` 또는 `voice_call` 도구 사용

## 실행 위치(로컬 vs 원격)

Voice Call 플러그인은 **Gateway 프로세스 내부에서** 실행됩니다.

원격 Gateway를 사용하는 경우, **Gateway가 실행 중인 머신**에 플러그인을 설치/구성한 뒤 Gateway를 재시작하여 로드하세요.

## 설치

### 옵션 A: npm에서 설치(권장)

```bash
openclaw plugins install @openclaw/voice-call
```

이후 Gateway를 재시작하세요.

### 옵션 B: 로컬 폴더에서 설치(개발용, 복사 없음)

```bash
PLUGIN_SRC=./path/to/local/voice-call-plugin
openclaw plugins install "$PLUGIN_SRC"
cd "$PLUGIN_SRC" && pnpm install
```

이후 Gateway를 재시작하세요.

## 구성

`plugins.entries.voice-call.config` 아래에 config를 설정하세요.

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        enabled: true,
        config: {
          provider: "twilio", // 또는 "telnyx" | "plivo" | "mock"
          fromNumber: "+15550001234",
          toNumber: "+15550005678",

          twilio: {
            accountSid: "ACxxxxxxxx",
            authToken: "...",
          },

          telnyx: {
            apiKey: "...",
            connectionId: "...",
            // Telnyx Mission Control Portal의 Telnyx webhook 공개 키
            // (Base64 문자열; TELNYX_PUBLIC_KEY로도 설정 가능).
            publicKey: "...",
          },

          plivo: {
            authId: "MAxxxxxxxxxxxxxxxxxxxx",
            authToken: "...",
          },

          // Webhook 서버
          serve: {
            port: 3334,
            path: "/voice/webhook",
          },

          // Webhook 보안(터널/프록시에 권장)
          webhookSecurity: {
            allowedHosts: ["voice.example.com"],
            trustedProxyIPs: ["100.64.0.1"],
          },

          // 공개 노출(하나 선택)
          // publicUrl: "https://example.ngrok.app/voice/webhook",
          // tunnel: { provider: "ngrok" },
          // tailscale: { mode: "funnel", path: "/voice/webhook" }

          outbound: {
            defaultMode: "notify", // notify | conversation
          },

          streaming: {
            enabled: true,
            provider: "openai", // 선택 사항; 설정하지 않으면 첫 번째로 등록된 realtime transcription provider
            streamPath: "/voice/stream",
            providers: {
              openai: {
                apiKey: "sk-...", // OPENAI_API_KEY가 설정된 경우 선택 사항
                model: "gpt-4o-transcribe",
                silenceDurationMs: 800,
                vadThreshold: 0.5,
              },
            },
            preStartTimeoutMs: 5000,
            maxPendingConnections: 32,
            maxPendingConnectionsPerIp: 4,
            maxConnections: 128,
          },
        },
      },
    },
  },
}
```

참고:

- Twilio/Telnyx는 **공개적으로 접근 가능한** webhook URL이 필요합니다.
- Plivo는 **공개적으로 접근 가능한** webhook URL이 필요합니다.
- `mock`은 로컬 개발용 provider입니다(네트워크 호출 없음).
- 오래된 config에서 여전히 `provider: "log"`, `twilio.from`, 또는 레거시 `streaming.*` OpenAI 키를 사용한다면 `openclaw doctor --fix`를 실행해 재작성하세요.
- Telnyx는 `skipSignatureVerification`이 true가 아닌 한 `telnyx.publicKey`(또는 `TELNYX_PUBLIC_KEY`)가 필요합니다.
- `skipSignatureVerification`은 로컬 테스트 전용입니다.
- ngrok free tier를 사용하는 경우 정확한 ngrok URL로 `publicUrl`을 설정하세요. 서명 검증은 항상 강제됩니다.
- `tunnel.allowNgrokFreeTierLoopbackBypass: true`는 `tunnel.provider="ngrok"`이고 `serve.bind`가 loopback(ngrok 로컬 에이전트)일 때 **서명이 유효하지 않은** Twilio webhook을 허용합니다. 로컬 개발 전용으로 사용하세요.
- ngrok free tier URL은 변경되거나 interstitial 동작이 추가될 수 있습니다. `publicUrl`이 바뀌면 Twilio 서명 검증이 실패합니다. 프로덕션에서는 안정적인 도메인 또는 Tailscale funnel을 권장합니다.
- 스트리밍 보안 기본값:
  - `streaming.preStartTimeoutMs`는 유효한 `start` 프레임을 보내지 않는 소켓을 닫습니다.
- `streaming.maxPendingConnections`는 인증되지 않은 pre-start 소켓의 총 개수를 제한합니다.
- `streaming.maxPendingConnectionsPerIp`는 소스 IP당 인증되지 않은 pre-start 소켓 수를 제한합니다.
- `streaming.maxConnections`는 열려 있는 미디어 스트림 소켓의 총 수(pending + active)를 제한합니다.
- 런타임 fallback은 현재도 해당 오래된 voice-call 키를 받아들이지만, 재작성 경로는 `openclaw doctor --fix`이며 호환 shim은 임시입니다.

## 스트리밍 전사

`streaming`은 실시간 통화 오디오용 realtime transcription provider를 선택합니다.

현재 런타임 동작:

- `streaming.provider`는 선택 사항입니다. 설정하지 않으면 Voice Call은 첫 번째
  등록된 realtime transcription provider를 사용합니다.
- 현재 번들 provider는 번들 `openai`
  플러그인에 의해 등록되는 OpenAI입니다.
- provider 소유의 원시 config는 `streaming.providers.<providerId>` 아래에 위치합니다.
- `streaming.provider`가 등록되지 않은 provider를 가리키거나, realtime
  transcription provider가 전혀 등록되지 않은 경우, Voice Call은 경고를 로그에 남기고
  플러그인 전체를 실패시키는 대신 미디어 스트리밍을 건너뜁니다.

OpenAI 스트리밍 전사 기본값:

- API 키: `streaming.providers.openai.apiKey` 또는 `OPENAI_API_KEY`
- model: `gpt-4o-transcribe`
- `silenceDurationMs`: `800`
- `vadThreshold`: `0.5`

예시:

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          streaming: {
            enabled: true,
            provider: "openai",
            streamPath: "/voice/stream",
            providers: {
              openai: {
                apiKey: "sk-...", // OPENAI_API_KEY가 설정된 경우 선택 사항
                model: "gpt-4o-transcribe",
                silenceDurationMs: 800,
                vadThreshold: 0.5,
              },
            },
          },
        },
      },
    },
  },
}
```

레거시 키는 여전히 `openclaw doctor --fix`에 의해 자동 마이그레이션됩니다.

- `streaming.sttProvider` → `streaming.provider`
- `streaming.openaiApiKey` → `streaming.providers.openai.apiKey`
- `streaming.sttModel` → `streaming.providers.openai.model`
- `streaming.silenceDurationMs` → `streaming.providers.openai.silenceDurationMs`
- `streaming.vadThreshold` → `streaming.providers.openai.vadThreshold`

## 오래된 통화 정리기

종료 webhook을 받지 못한 통화를 종료하려면
`staleCallReaperSeconds`를 사용하세요
(예: 완료되지 않는 notify 모드 통화). 기본값은 `0`
(비활성화)입니다.

권장 범위:

- **프로덕션:** notify 스타일 흐름에는 `120`–`300`초.
- 정상 통화가
  끝날 수 있도록 이 값을 **`maxDurationSeconds`보다 높게** 유지하세요. 좋은 시작점은 `maxDurationSeconds + 30–60`초입니다.

예시:

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          maxDurationSeconds: 300,
          staleCallReaperSeconds: 360,
        },
      },
    },
  },
}
```

## Webhook 보안

프록시 또는 터널이 Gateway 앞에 있는 경우, 플러그인은 서명 검증을 위해
공개 URL을 재구성합니다. 다음 옵션은 어떤 전달 헤더를 신뢰할지 제어합니다.

`webhookSecurity.allowedHosts`는 전달 헤더의 호스트 허용 목록입니다.

`webhookSecurity.trustForwardingHeaders`는 허용 목록 없이 전달 헤더를 신뢰합니다.

`webhookSecurity.trustedProxyIPs`는 요청의
원격 IP가 목록과 일치할 때만 전달 헤더를 신뢰합니다.

Webhook 재전송 방지는 Twilio와 Plivo에서 활성화됩니다. 재전송된 유효한 webhook
요청은 승인되지만 부작용은 건너뜁니다.

Twilio 대화 턴은 `<Gather>` callback에 턴별 토큰을 포함하므로
오래되었거나 재전송된 음성 callback은 더 새로운 대기 중 transcript 턴을 만족시킬 수 없습니다.

provider에 필요한 서명 헤더가 누락된
인증되지 않은 webhook 요청은 본문을 읽기 전에 거부됩니다.

voice-call webhook은 서명 검증 전
공유 pre-auth 본문 프로필(64 KB / 5초)과 IP별 in-flight 제한을 사용합니다.

안정적인 공개 호스트를 사용하는 예시:

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          publicUrl: "https://voice.example.com/voice/webhook",
          webhookSecurity: {
            allowedHosts: ["voice.example.com"],
          },
        },
      },
    },
  },
}
```

## 통화용 TTS

Voice Call은 통화 중
스트리밍 음성을 위해 core `messages.tts` 구성을 사용합니다. 플러그인 config 아래에서
**동일한 형식**으로 이를 재정의할 수 있으며, `messages.tts`와 깊은 병합됩니다.

```json5
{
  tts: {
    provider: "elevenlabs",
    providers: {
      elevenlabs: {
        voiceId: "pMsXgVXv3BLzUgSXRplE",
        modelId: "eleven_multilingual_v2",
      },
    },
  },
}
```

참고:

- 플러그인 config 내부의 레거시 `tts.<provider>` 키(`openai`, `elevenlabs`, `microsoft`, `edge`)는 로드 시 `tts.providers.<provider>`로 자동 마이그레이션됩니다. 커밋된 config에서는 `providers` 형식을 사용하는 것이 좋습니다.
- **Microsoft speech는 음성 통화에서 무시됩니다**(전화 오디오는 PCM이 필요하지만, 현재 Microsoft 전송 계층은 전화용 PCM 출력을 제공하지 않음).
- Twilio 미디어 스트리밍이 활성화되어 있으면 core TTS가 사용되고, 그렇지 않으면 통화는 provider 네이티브 음성으로 fallback됩니다.
- Twilio 미디어 스트림이 이미 활성 상태라면 Voice Call은 TwiML `<Say>`로 fallback되지 않습니다. 그 상태에서 전화용 TTS를 사용할 수 없으면 두 재생 경로를 섞는 대신 재생 요청이 실패합니다.
- 전화용 TTS가 보조 provider로 fallback될 때, Voice Call은 디버깅을 위해 provider 체인(`from`, `to`, `attempts`)과 함께 경고를 로그에 남깁니다.

### 추가 예시

core TTS만 사용(재정의 없음):

```json5
{
  messages: {
    tts: {
      provider: "openai",
      providers: {
        openai: { voice: "alloy" },
      },
    },
  },
}
```

통화에만 ElevenLabs로 재정의(core 기본값은 다른 곳에서 유지):

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          tts: {
            provider: "elevenlabs",
            providers: {
              elevenlabs: {
                apiKey: "elevenlabs_key",
                voiceId: "pMsXgVXv3BLzUgSXRplE",
                modelId: "eleven_multilingual_v2",
              },
            },
          },
        },
      },
    },
  },
}
```

통화용 OpenAI 모델만 재정의(깊은 병합 예시):

```json5
{
  plugins: {
    entries: {
      "voice-call": {
        config: {
          tts: {
            providers: {
              openai: {
                model: "gpt-4o-mini-tts",
                voice: "marin",
              },
            },
          },
        },
      },
    },
  },
}
```

## 인바운드 통화

인바운드 정책의 기본값은 `disabled`입니다. 인바운드 통화를 활성화하려면 다음을 설정하세요.

```json5
{
  inboundPolicy: "allowlist",
  allowFrom: ["+15550001234"],
  inboundGreeting: "Hello! How can I help?",
}
```

`inboundPolicy: "allowlist"`는 낮은 보증 수준의 caller-ID 필터입니다. 플러그인은
provider가 제공한 `From` 값을 정규화하여 `allowFrom`과 비교합니다.
Webhook 검증은 provider 전달과 payload 무결성을 인증하지만,
PSTN/VoIP 발신 번호의 소유권을 증명하지는 않습니다. `allowFrom`은
강한 발신자 ID가 아니라 caller-ID 필터링으로 취급하세요.

자동 응답은 에이전트 시스템을 사용합니다. 다음으로 조정할 수 있습니다.

- `responseModel`
- `responseSystemPrompt`
- `responseTimeoutMs`

### 음성 출력 계약

자동 응답의 경우 Voice Call은 시스템 프롬프트에 엄격한 음성 출력 계약을 추가합니다.

- `{"spoken":"..."}`

그런 다음 Voice Call은 음성 텍스트를 방어적으로 추출합니다.

- reasoning/error 콘텐츠로 표시된 payload는 무시합니다.
- 직접 JSON, fenced JSON 또는 인라인 `"spoken"` 키를 파싱합니다.
- 일반 텍스트로 fallback하고 계획/메타로 보이는 도입 문단은 제거합니다.

이렇게 하면 음성 재생이 발신자 대상 텍스트에 집중되고, 계획 텍스트가 오디오로 유출되는 것을 방지할 수 있습니다.

### 대화 시작 동작

아웃바운드 `conversation` 통화의 경우 첫 메시지 처리 동작은 실시간 재생 상태에 연결됩니다.

- 바지인 큐 비우기와 자동 응답은 초기 인사말이 실제로 재생 중일 때만 억제됩니다.
- 초기 재생에 실패하면 통화는 `listening` 상태로 돌아가고 초기 메시지는 재시도를 위해 대기열에 남습니다.
- Twilio 스트리밍의 초기 재생은 추가 지연 없이 스트림 연결 시 시작됩니다.

### Twilio 스트림 연결 해제 유예

Twilio 미디어 스트림이 연결 해제되면 Voice Call은 통화를 자동 종료하기 전에 `2000ms`를 기다립니다.

- 이 시간 안에 스트림이 다시 연결되면 자동 종료는 취소됩니다.
- 유예 기간 후에도 스트림이 다시 등록되지 않으면, 활성 상태에 멈춘 통화를 방지하기 위해 통화를 종료합니다.

## CLI

```bash
openclaw voicecall call --to "+15555550123" --message "Hello from OpenClaw"
openclaw voicecall start --to "+15555550123"   # call의 별칭
openclaw voicecall continue --call-id <id> --message "Any questions?"
openclaw voicecall speak --call-id <id> --message "One moment"
openclaw voicecall end --call-id <id>
openclaw voicecall status --call-id <id>
openclaw voicecall tail
openclaw voicecall latency                     # 로그에서 턴 지연 시간 요약
openclaw voicecall expose --mode funnel
```

`latency`는 기본 voice-call 저장소 경로의 `calls.jsonl`을 읽습니다.
다른 로그를 가리키려면 `--file <path>`를 사용하고, 마지막 N개 레코드만 분석하려면 `--last <n>`을 사용하세요(기본값 200). 출력에는 턴 지연 시간과 listen-wait 시간의 p50/p90/p99가 포함됩니다.

## 에이전트 도구

도구 이름: `voice_call`

작업:

- `initiate_call` (message, to?, mode?)
- `continue_call` (callId, message)
- `speak_to_user` (callId, message)
- `end_call` (callId)
- `get_status` (callId)

이 리포지토리는 `skills/voice-call/SKILL.md`에 일치하는 skill 문서도 제공합니다.

## Gateway RPC

- `voicecall.initiate` (`to?`, `message`, `mode?`)
- `voicecall.continue` (`callId`, `message`)
- `voicecall.speak` (`callId`, `message`)
- `voicecall.end` (`callId`)
- `voicecall.status` (`callId`)
