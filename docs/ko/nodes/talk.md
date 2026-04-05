---
read_when:
    - macOS/iOS/Android에서 Talk 모드를 구현할 때
    - 음성/TTS/중단 동작을 변경할 때
summary: 'Talk 모드: ElevenLabs TTS를 사용하는 연속 음성 대화'
title: Talk 모드
x-i18n:
    generated_at: "2026-04-05T12:47:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3f10a3e9ee8fc2b4f7a89771d6e7b7373166a51ef9e9aa2d8c5ea67fc0729f9d
    source_path: nodes/talk.md
    workflow: 15
---

# Talk 모드

Talk 모드는 연속 음성 대화 루프입니다:

1. 음성을 듣습니다
2. 전사본을 모델로 보냅니다(메인 세션, `chat.send`)
3. 응답을 기다립니다
4. 구성된 Talk provider(`talk.speak`)를 통해 응답을 말합니다

## 동작(macOS)

- Talk 모드가 활성화되어 있는 동안 **항상 표시되는 오버레이**
- **Listening → Thinking → Speaking** 단계 전환
- **짧은 멈춤**(무음 구간)이 발생하면 현재 전사본이 전송됩니다
- 답장은 **WebChat에 기록됩니다**(직접 입력하는 것과 동일)
- **음성으로 중단**(기본값 켜짐): assistant가 말하는 동안 사용자가 말을 시작하면 재생을 중지하고 다음 프롬프트를 위해 중단 시각을 기록합니다

## 답장의 음성 지시문

assistant는 음성을 제어하기 위해 답장 앞에 **단일 JSON 줄**을 붙일 수 있습니다:

```json
{ "voice": "<voice-id>", "once": true }
```

규칙:

- 첫 번째 비어 있지 않은 줄만 사용
- 알 수 없는 키는 무시
- `once: true`는 현재 답장에만 적용
- `once`가 없으면 해당 음성이 Talk 모드의 새 기본값이 됨
- JSON 줄은 TTS 재생 전에 제거됨

지원되는 키:

- `voice` / `voice_id` / `voiceId`
- `model` / `model_id` / `modelId`
- `speed`, `rate` (WPM), `stability`, `similarity`, `style`, `speakerBoost`
- `seed`, `normalize`, `lang`, `output_format`, `latency_tier`
- `once`

## Config (`~/.openclaw/openclaw.json`)

```json5
{
  talk: {
    voiceId: "elevenlabs_voice_id",
    modelId: "eleven_v3",
    outputFormat: "mp3_44100_128",
    apiKey: "elevenlabs_api_key",
    silenceTimeoutMs: 1500,
    interruptOnSpeech: true,
  },
}
```

기본값:

- `interruptOnSpeech`: true
- `silenceTimeoutMs`: 설정되지 않으면 Talk는 전사본 전송 전 플랫폼 기본 멈춤 구간을 유지합니다(`macOS와 Android에서는 700 ms`, `iOS에서는 900 ms`)
- `voiceId`: `ELEVENLABS_VOICE_ID` / `SAG_VOICE_ID`로 대체됨(API 키를 사용할 수 있으면 첫 번째 ElevenLabs 음성으로도 대체)
- `modelId`: 설정되지 않으면 기본값은 `eleven_v3`
- `apiKey`: `ELEVENLABS_API_KEY`로 대체됨(또는 사용할 수 있으면 gateway 셸 프로필)
- `outputFormat`: 기본값은 macOS/iOS에서 `pcm_44100`, Android에서 `pcm_24000`입니다(MP3 스트리밍을 강제하려면 `mp3_*` 설정)

## macOS UI

- 메뉴 막대 토글: **Talk**
- Config 탭: **Talk Mode** 그룹(voice id + interrupt 토글)
- 오버레이:
  - **Listening**: 마이크 레벨에 따라 구름이 맥동
  - **Thinking**: 가라앉는 애니메이션
  - **Speaking**: 바깥으로 퍼지는 고리
  - 구름 클릭: 말하기 중지
  - X 클릭: Talk 모드 종료

## 참고

- Speech + Microphone 권한이 필요합니다.
- 세션 키 `main`에 대해 `chat.send`를 사용합니다.
- 게이트웨이는 활성 Talk provider를 사용해 `talk.speak`를 통해 Talk 재생을 해석합니다. Android는 해당 RPC를 사용할 수 없을 때만 로컬 시스템 TTS로 대체합니다.
- `eleven_v3`의 `stability`는 `0.0`, `0.5`, `1.0`으로 검증되며, 다른 모델은 `0..1`을 허용합니다.
- `latency_tier`는 설정된 경우 `0..4`로 검증됩니다.
- Android는 저지연 AudioTrack 스트리밍을 위해 `pcm_16000`, `pcm_22050`, `pcm_24000`, `pcm_44100` 출력 형식을 지원합니다.
