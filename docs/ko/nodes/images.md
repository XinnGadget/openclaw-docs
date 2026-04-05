---
read_when:
    - 미디어 파이프라인 또는 첨부 파일을 수정하는 경우
summary: send, gateway, 에이전트 응답을 위한 이미지 및 미디어 처리 규칙
title: 이미지 및 미디어 지원
x-i18n:
    generated_at: "2026-04-05T12:47:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: c3bb372b45a3bae51eae03b41cb22c4cde144675a54ddfd12e01a96132e48a8a
    source_path: nodes/images.md
    workflow: 15
---

# 이미지 및 미디어 지원 (2025-12-05)

WhatsApp 채널은 **Baileys Web**을 통해 실행됩니다. 이 문서는 send, gateway, 에이전트 응답에 대한 현재 미디어 처리 규칙을 정리합니다.

## 목표

- `openclaw message send --media`를 통해 선택적 캡션과 함께 미디어 전송
- 웹 받은편지함의 자동 응답이 텍스트와 함께 미디어를 포함할 수 있도록 허용
- 유형별 제한을 합리적이고 예측 가능하게 유지

## CLI 표면

- `openclaw message send --media <path-or-url> [--message <caption>]`
  - `--media`는 선택 사항이며, 미디어만 보내는 경우 캡션은 비워둘 수 있습니다.
  - `--dry-run`은 해석된 payload를 출력하고, `--json`은 `{ channel, to, messageId, mediaUrl, caption }`을 출력합니다.

## WhatsApp Web 채널 동작

- 입력: 로컬 파일 경로 **또는** HTTP(S) URL
- 흐름: Buffer로 로드하고, 미디어 종류를 감지한 뒤, 올바른 payload를 생성
  - **이미지:** `channels.whatsapp.mediaMaxMb`(기본값: 50 MB)를 목표로 JPEG로 리사이즈 및 재압축(최대 변 길이 2048px)
  - **오디오/음성/비디오:** 16 MB까지 그대로 전달; 오디오는 음성 메모로 전송됨(`ptt: true`)
  - **문서:** 그 외 모든 항목은 100 MB까지 허용되며, 가능하면 파일명을 유지
- WhatsApp GIF 스타일 재생: `gifPlayback: true`가 설정된 MP4를 전송(`CLI: --gif-playback`)하면 모바일 클라이언트에서 인라인 반복 재생됨
- MIME 감지는 magic bytes를 우선하고, 그다음 헤더, 그다음 파일 확장자를 사용
- 캡션은 `--message` 또는 `reply.text`에서 가져오며, 빈 캡션도 허용
- 로깅: non-verbose에서는 `↩️`/`✅`를 표시하고, verbose에서는 크기와 소스 경로/URL 포함

## 자동 응답 파이프라인

- `getReplyFromConfig`는 `{ text?, mediaUrl?, mediaUrls? }`를 반환합니다.
- 미디어가 있으면 웹 sender는 `openclaw message send`와 동일한 파이프라인을 사용해 로컬 경로 또는 URL을 해석합니다.
- 여러 미디어 항목이 제공되면 순차적으로 전송됩니다.

## 명령(Pi)으로 들어오는 인바운드 미디어

- 인바운드 웹 메시지에 미디어가 포함되면 OpenClaw는 이를 임시 파일로 다운로드하고 다음 템플릿 변수를 노출합니다.
  - 인바운드 미디어용 의사 URL인 `{{MediaUrl}}`
  - 명령 실행 전에 기록되는 로컬 임시 경로인 `{{MediaPath}}`
- 세션별 Docker sandbox가 활성화되어 있으면 인바운드 미디어는 sandbox workspace로 복사되며, `MediaPath`/`MediaUrl`은 `media/inbound/<filename>` 같은 상대 경로로 다시 작성됩니다.
- 미디어 이해(`tools.media.*` 또는 공통 `tools.media.models`를 통해 구성된 경우)는 템플릿 처리 전에 실행되며 `[Image]`, `[Audio]`, `[Video]` 블록을 `Body`에 삽입할 수 있습니다.
  - 오디오는 `{{Transcript}}`를 설정하고, 명령 파싱에 transcript를 사용하므로 슬래시 명령이 계속 작동합니다.
  - 비디오 및 이미지 설명은 명령 파싱을 위해 모든 캡션 텍스트를 유지합니다.
  - 활성 기본 이미지 모델이 이미 네이티브 vision을 지원하는 경우, OpenClaw는 `[Image]` 요약 블록을 건너뛰고 원본 이미지를 모델에 직접 전달합니다.
- 기본적으로 첫 번째로 일치하는 이미지/오디오/비디오 첨부 파일만 처리됩니다. 여러 첨부 파일을 처리하려면 `tools.media.<cap>.attachments`를 설정하세요.

## 제한 및 오류

**아웃바운드 전송 제한(WhatsApp web send)**

- 이미지: 재압축 후 `channels.whatsapp.mediaMaxMb`(기본값: 50 MB)까지
- 오디오/음성/비디오: 16 MB 제한, 문서: 100 MB 제한
- 크기가 너무 크거나 읽을 수 없는 미디어 → 로그에 명확한 오류를 남기고 응답은 건너뜀

**미디어 이해 제한(전사/설명)**

- 이미지 기본값: 10 MB (`tools.media.image.maxBytes`)
- 오디오 기본값: 20 MB (`tools.media.audio.maxBytes`)
- 비디오 기본값: 50 MB (`tools.media.video.maxBytes`)
- 크기가 너무 큰 미디어는 이해 단계를 건너뛰지만, 응답은 여전히 원본 본문과 함께 진행됩니다.

## 테스트용 참고

- 이미지/오디오/문서 사례에 대해 send + reply 흐름을 다루기
- 이미지 재압축(크기 제한)과 오디오의 음성 메모 플래그 검증
- 다중 미디어 응답이 순차 전송으로 fan out되는지 확인
