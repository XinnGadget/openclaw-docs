---
read_when:
    - 답장에 텍스트 음성 변환을 활성화할 때
    - TTS 제공자나 제한을 구성할 때
    - '`/tts` 명령을 사용할 때'
summary: 발신 답장용 텍스트 음성 변환(TTS)
title: 텍스트 음성 변환
x-i18n:
    generated_at: "2026-04-08T05:56:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e0fbcaf61282733c134f682e05a71f94d2169c03a85131ce9ad233c71a1e533
    source_path: tools/tts.md
    workflow: 15
---

# 텍스트 음성 변환(TTS)

OpenClaw는 ElevenLabs, Microsoft, MiniMax 또는 OpenAI를 사용해 발신 답장을 오디오로 변환할 수 있습니다.
이 기능은 OpenClaw가 오디오를 보낼 수 있는 모든 곳에서 작동합니다.

## 지원 서비스

- **ElevenLabs**(주 제공자 또는 대체 제공자)
- **Microsoft**(주 제공자 또는 대체 제공자, 현재 번들 구현은 `node-edge-tts` 사용)
- **MiniMax**(주 제공자 또는 대체 제공자, T2A v2 API 사용)
- **OpenAI**(주 제공자 또는 대체 제공자, 요약에도 사용)

### Microsoft 음성 참고 사항

번들된 Microsoft 음성 제공자는 현재 `node-edge-tts` 라이브러리를 통해
Microsoft Edge의 온라인 신경망 TTS 서비스를 사용합니다. 이는 호스팅된
서비스이며(로컬 아님), Microsoft 엔드포인트를 사용하고, API 키가 필요하지
않습니다. `node-edge-tts`는 음성 구성 옵션과 출력 형식을 제공하지만,
모든 옵션이 서비스에서 지원되는 것은 아닙니다. `edge`를 사용하는 레거시
구성과 directive 입력도 계속 작동하며 `microsoft`로 정규화됩니다.

이 경로는 공개 웹 서비스이며 게시된 SLA나 할당량이 없으므로,
best-effort로 취급해야 합니다. 보장된 제한과 지원이 필요하다면 OpenAI
또는 ElevenLabs를 사용하세요.

## 선택적 키

OpenAI, ElevenLabs 또는 MiniMax를 사용하려면:

- `ELEVENLABS_API_KEY`(또는 `XI_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

Microsoft 음성은 API 키가 **필요하지 않습니다**.

여러 제공자가 구성되어 있으면, 선택된 제공자를 먼저 사용하고 나머지는 대체 옵션으로 사용합니다.
자동 요약은 구성된 `summaryModel`(또는 `agents.defaults.model.primary`)을 사용하므로,
요약을 활성화했다면 해당 제공자도 인증되어 있어야 합니다.

## 서비스 링크

- [OpenAI Text-to-Speech guide](https://platform.openai.com/docs/guides/text-to-speech)
- [OpenAI Audio API reference](https://platform.openai.com/docs/api-reference/audio)
- [ElevenLabs Text to Speech](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [ElevenLabs Authentication](https://elevenlabs.io/docs/api-reference/authentication)
- [MiniMax T2A v2 API](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Microsoft Speech output formats](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## 기본으로 활성화되어 있나요?

아니요. 자동 TTS는 기본적으로 **비활성화**되어 있습니다. 구성에서
`messages.tts.auto`로 활성화하거나, 로컬에서 `/tts on`으로 활성화하세요.

`messages.tts.provider`가 설정되지 않은 경우, OpenClaw는 레지스트리 자동 선택 순서에서
구성된 첫 번째 음성 제공자를 선택합니다.

## 구성

TTS 구성은 `openclaw.json`의 `messages.tts` 아래에 있습니다.
전체 스키마는 [Gateway configuration](/ko/gateway/configuration)에 있습니다.

### 최소 구성(활성화 + 제공자)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI 주 제공자 + ElevenLabs 대체 제공자

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft 주 제공자(API 키 없음)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax 주 제공자

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### Microsoft 음성 비활성화

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### 사용자 지정 제한 + prefs 경로

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### 수신 음성 메시지 뒤에만 오디오로 답장

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### 긴 답장에 대한 자동 요약 비활성화

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

그다음 실행:

```
/tts summary off
```

### 필드 참고 사항

- `auto`: 자동 TTS 모드(`off`, `always`, `inbound`, `tagged`).
  - `inbound`는 수신 음성 메시지 뒤에만 오디오를 보냅니다.
  - `tagged`는 답장에 `[[tts]]` 태그가 포함될 때만 오디오를 보냅니다.
- `enabled`: 레거시 토글(`doctor`가 이를 `auto`로 마이그레이션).
- `mode`: `"final"`(기본값) 또는 `"all"`(도구/블록 답장 포함).
- `provider`: `"elevenlabs"`, `"microsoft"`, `"minimax"`, `"openai"` 같은 음성 제공자 ID(대체는 자동).
- `provider`가 **설정되지 않은** 경우, OpenClaw는 레지스트리 자동 선택 순서에서 구성된 첫 번째 음성 제공자를 사용합니다.
- 레거시 `provider: "edge"`도 계속 작동하며 `microsoft`로 정규화됩니다.
- `summaryModel`: 자동 요약용 선택적 저비용 모델, 기본값은 `agents.defaults.model.primary`.
  - `provider/model` 또는 구성된 모델 별칭을 허용합니다.
- `modelOverrides`: 모델이 TTS directive를 내보내도록 허용합니다(기본적으로 활성화).
  - `allowProvider` 기본값은 `false`입니다(제공자 전환은 opt-in).
- `providers.<id>`: 음성 제공자 ID를 키로 하는 제공자 소유 설정.
- 레거시 직접 제공자 블록(`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`)은 로드 시 `messages.tts.providers.<id>`로 자동 마이그레이션됩니다.
- `maxTextLength`: TTS 입력의 하드 상한(문자 수). 초과하면 `/tts audio`는 실패합니다.
- `timeoutMs`: 요청 타임아웃(ms).
- `prefsPath`: 로컬 prefs JSON 경로 재정의(provider/limit/summary).
- `apiKey` 값은 env vars(`ELEVENLABS_API_KEY`/`XI_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`)로 대체될 수 있습니다.
- `providers.elevenlabs.baseUrl`: ElevenLabs API 기본 URL 재정의.
- `providers.openai.baseUrl`: OpenAI TTS 엔드포인트 재정의.
  - 확인 순서: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - 기본값이 아닌 값은 OpenAI 호환 TTS 엔드포인트로 취급되므로, 사용자 지정 모델 및 음성 이름을 허용합니다.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0`(1.0 = 보통)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: 2글자 ISO 639-1(예: `en`, `de`)
- `providers.elevenlabs.seed`: 정수 `0..4294967295`(best-effort 결정성)
- `providers.minimax.baseUrl`: MiniMax API 기본 URL 재정의(기본값 `https://api.minimax.io`, env: `MINIMAX_API_HOST`).
- `providers.minimax.model`: TTS 모델(기본값 `speech-2.8-hd`, env: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: 음성 식별자(기본값 `English_expressive_narrator`, env: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: 재생 속도 `0.5..2.0`(기본값 1.0).
- `providers.minimax.vol`: 볼륨 `(0, 10]`(기본값 1.0, 0보다 커야 함).
- `providers.minimax.pitch`: 피치 이동 `-12..12`(기본값 0).
- `providers.microsoft.enabled`: Microsoft 음성 사용 허용(기본값 `true`, API 키 없음).
- `providers.microsoft.voice`: Microsoft 신경망 음성 이름(예: `en-US-MichelleNeural`).
- `providers.microsoft.lang`: 언어 코드(예: `en-US`).
- `providers.microsoft.outputFormat`: Microsoft 출력 형식(예: `audio-24khz-48kbitrate-mono-mp3`).
  - 유효한 값은 Microsoft Speech output formats를 참조하세요. 번들된 Edge 기반 전송에서 모든 형식을 지원하는 것은 아닙니다.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: 퍼센트 문자열(예: `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: 오디오 파일과 함께 JSON 자막을 기록합니다.
- `providers.microsoft.proxy`: Microsoft 음성 요청용 프록시 URL.
- `providers.microsoft.timeoutMs`: 요청 타임아웃 재정의(ms).
- `edge.*`: 동일한 Microsoft 설정에 대한 레거시 별칭.

## 모델 기반 재정의(기본적으로 활성화)

기본적으로 모델은 단일 답장에 대해 TTS directive를 내보낼 수 **있습니다**.
`messages.tts.auto`가 `tagged`일 때는 오디오를 트리거하려면 이러한 directive가 필요합니다.

활성화되면 모델은 단일 답장의 음성을 재정의하기 위해 `[[tts:...]]` directive를 내보낼 수 있고,
선택적으로 `[[tts:text]]...[[/tts:text]]` 블록을 사용해
표현 태그(웃음, 노래 신호 등)를 제공할 수 있습니다. 이러한 내용은
오디오에만 나타나야 합니다.

`provider=...` directive는 `modelOverrides.allowProvider: true`가 아니면 무시됩니다.

답장 payload 예시:

```
Here you go.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](laughs) Read the song once more.[[/tts:text]]
```

사용 가능한 directive 키(활성화된 경우):

- `provider`(등록된 음성 제공자 ID, 예: `openai`, `elevenlabs`, `minimax`, `microsoft`; `allowProvider: true` 필요)
- `voice`(OpenAI 음성) 또는 `voiceId`(ElevenLabs / MiniMax)
- `model`(OpenAI TTS 모델, ElevenLabs 모델 ID 또는 MiniMax 모델)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume`(MiniMax 볼륨, 0-10)
- `pitch`(MiniMax 피치, -12 ~ 12)
- `applyTextNormalization`(`auto|on|off`)
- `languageCode`(ISO 639-1)
- `seed`

모든 모델 재정의 비활성화:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

선택적 allowlist(제공자 전환을 활성화하면서 다른 설정은 구성 가능하게 유지):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## 사용자별 기본 설정

슬래시 명령은 로컬 재정의를 `prefsPath`에 기록합니다(기본값:
`~/.openclaw/settings/tts.json`, `OPENCLAW_TTS_PREFS` 또는
`messages.tts.prefsPath`로 재정의 가능).

저장되는 필드:

- `enabled`
- `provider`
- `maxLength`(요약 임계값, 기본값 1500자)
- `summarize`(기본값 `true`)

이 값들은 해당 호스트의 `messages.tts.*`를 재정의합니다.

## 출력 형식(고정)

- **Feishu / Matrix / Telegram / WhatsApp**: Opus 음성 메시지(ElevenLabs의 `opus_48000_64`, OpenAI의 `opus`).
  - 48kHz / 64kbps는 음성 메시지에 적합한 절충안입니다.
- **기타 채널**: MP3(ElevenLabs의 `mp3_44100_128`, OpenAI의 `mp3`).
  - 44.1kHz / 128kbps는 음성 명료도를 위한 기본 균형입니다.
- **MiniMax**: MP3(`speech-2.8-hd` 모델, 32kHz 샘플링 속도). 음성 노트 형식은 기본 지원되지 않으므로, Opus 음성 메시지가 반드시 필요하면 OpenAI 또는 ElevenLabs를 사용하세요.
- **Microsoft**: `microsoft.outputFormat` 사용(기본값 `audio-24khz-48kbitrate-mono-mp3`).
  - 번들된 전송은 `outputFormat`을 허용하지만, 모든 형식을 서비스에서 사용할 수 있는 것은 아닙니다.
  - 출력 형식 값은 Microsoft Speech output formats를 따릅니다(Ogg/WebM Opus 포함).
  - Telegram `sendVoice`는 OGG/MP3/M4A를 허용합니다. Opus 음성 메시지가 반드시 필요하면 OpenAI/ElevenLabs를 사용하세요.
  - 구성된 Microsoft 출력 형식이 실패하면 OpenClaw는 MP3로 재시도합니다.

OpenAI/ElevenLabs 출력 형식은 채널별로 고정됩니다(위 참조).

## 자동 TTS 동작

활성화되면 OpenClaw는 다음과 같이 동작합니다.

- 답장에 이미 미디어 또는 `MEDIA:` directive가 포함되어 있으면 TTS를 건너뜁니다.
- 매우 짧은 답장(< 10자)은 건너뜁니다.
- 활성화된 경우 긴 답장을 `agents.defaults.model.primary`(또는 `summaryModel`)를 사용해 요약합니다.
- 생성된 오디오를 답장에 첨부합니다.

답장이 `maxLength`를 초과하고 요약이 비활성화되어 있거나(또는
요약 모델에 대한 API 키가 없는 경우), 오디오는
건너뛰고 일반 텍스트 답장을 보냅니다.

## 흐름도

```
Reply -> TTS enabled?
  no  -> send text
  yes -> has media / MEDIA: / short?
          yes -> send text
          no  -> length > limit?
                   no  -> TTS -> attach audio
                   yes -> summary enabled?
                            no  -> send text
                            yes -> summarize (summaryModel or agents.defaults.model.primary)
                                      -> TTS -> attach audio
```

## 슬래시 명령 사용법

명령은 하나뿐입니다: `/tts`.
활성화 세부 정보는 [Slash commands](/ko/tools/slash-commands)를 참조하세요.

Discord 참고: `/tts`는 Discord 기본 명령이므로, OpenClaw는
그곳에서 `/voice`를 네이티브 명령으로 등록합니다. 텍스트 `/tts ...`도 계속 작동합니다.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

참고 사항:

- 명령에는 인증된 발신자가 필요합니다(allowlist/owner 규칙이 계속 적용됨).
- `commands.text` 또는 네이티브 명령 등록이 활성화되어 있어야 합니다.
- 구성 `messages.tts.auto`는 `off|always|inbound|tagged`를 허용합니다.
- `/tts on`은 로컬 TTS 기본 설정을 `always`로 기록하고, `/tts off`는 `off`로 기록합니다.
- `inbound` 또는 `tagged` 기본값을 원하면 구성을 사용하세요.
- `limit`과 `summary`는 메인 구성이 아니라 로컬 prefs에 저장됩니다.
- `/tts audio`는 일회성 오디오 답장을 생성합니다(TTS를 켜지 않음).
- `/tts status`에는 최신 시도에 대한 대체 가시성이 포함됩니다.
  - 성공적인 대체: `Fallback: <primary> -> <used>` + `Attempts: ...`
  - 실패: `Error: ...` + `Attempts: ...`
  - 자세한 진단: `Attempt details: provider:outcome(reasonCode) latency`
- OpenAI 및 ElevenLabs API 실패는 이제 파싱된 제공자 오류 상세 정보와 요청 ID(제공자가 반환한 경우)를 포함하며, 이는 TTS 오류/로그에 표시됩니다.

## 에이전트 도구

`tts` 도구는 텍스트를 음성으로 변환하고
답장 전달을 위한 오디오 첨부 파일을 반환합니다. 채널이 Feishu, Matrix, Telegram 또는 WhatsApp인 경우,
오디오는 파일 첨부가 아니라 음성 메시지로 전달됩니다.

## Gateway RPC

Gateway 메서드:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
