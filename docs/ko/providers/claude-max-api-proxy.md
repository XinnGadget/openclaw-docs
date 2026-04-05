---
read_when:
    - OpenAI 호환 도구와 함께 Claude Max 구독을 사용하려는 경우
    - Claude Code CLI를 래핑하는 로컬 API 서버를 원하는 경우
    - 구독 기반 Anthropic 액세스와 API 키 기반 Anthropic 액세스를 비교 평가하려는 경우
summary: Claude 구독 자격 증명을 OpenAI 호환 엔드포인트로 노출하는 커뮤니티 프록시
title: Claude Max API 프록시
x-i18n:
    generated_at: "2026-04-05T12:51:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2e125a6a46e48371544adf1331137a1db51e93e905b8c44da482cf2fba180a09
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Claude Max API 프록시

**claude-max-api-proxy**는 Claude Max/Pro 구독을 OpenAI 호환 API 엔드포인트로 노출하는 커뮤니티 도구입니다. 이를 통해 OpenAI API 형식을 지원하는 모든 도구에서 구독을 사용할 수 있습니다.

<Warning>
이 경로는 기술적 호환성만을 위한 것입니다. Anthropic은 과거에 Claude Code 외부에서의 일부 구독
사용을 차단한 적이 있습니다. 이를 사용할지 여부는 스스로 판단해야 하며,
이에 의존하기 전에 Anthropic의 현재 약관을 확인해야 합니다.
</Warning>

## 왜 이것을 사용하나요?

| 방식                    | 비용                                                | 적합한 용도                               |
| ----------------------- | --------------------------------------------------- | ----------------------------------------- |
| Anthropic API           | 토큰당 과금 (~입력 $15/M, 출력 $75/M, Opus 기준)    | 프로덕션 앱, 높은 사용량                  |
| Claude Max subscription | 월 $200 정액                                       | 개인 사용, 개발, 무제한 사용              |

Claude Max 구독이 있고 이를 OpenAI 호환 도구와 함께 사용하려는 경우, 이 프록시는 일부 워크플로에서 비용을 줄일 수 있습니다. 프로덕션 사용에서는 여전히 API 키가 더 명확한 정책 경로입니다.

## 작동 방식

```
Your App → claude-max-api-proxy → Claude Code CLI → Anthropic (via subscription)
     (OpenAI format)              (converts format)      (uses your login)
```

프록시는 다음을 수행합니다.

1. `http://localhost:3456/v1/chat/completions`에서 OpenAI 형식 요청을 수락합니다
2. 이를 Claude Code CLI 명령으로 변환합니다
3. 응답을 OpenAI 형식으로 반환합니다(스트리밍 지원)

## 설치

```bash
# Requires Node.js 20+ and Claude Code CLI
npm install -g claude-max-api-proxy

# Verify Claude CLI is authenticated
claude --version
```

## 사용법

### 서버 시작

```bash
claude-max-api
# Server runs at http://localhost:3456
```

### 테스트

```bash
# Health check
curl http://localhost:3456/health

# List models
curl http://localhost:3456/v1/models

# Chat completion
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-opus-4",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

### OpenClaw와 함께 사용

OpenClaw를 사용자 지정 OpenAI 호환 엔드포인트로 프록시를 가리키도록 설정할 수 있습니다.

```json5
{
  env: {
    OPENAI_API_KEY: "not-needed",
    OPENAI_BASE_URL: "http://localhost:3456/v1",
  },
  agents: {
    defaults: {
      model: { primary: "openai/claude-opus-4" },
    },
  },
}
```

이 경로는 다른 사용자 지정 `/v1` 백엔드와 동일한 프록시 스타일의 OpenAI 호환 경로를 사용합니다.

- OpenAI 전용 요청 셰이핑은 적용되지 않습니다
- `service_tier`, Responses `store`, 프롬프트 캐시 힌트, OpenAI 추론 호환 페이로드 셰이핑이 없습니다
- 숨겨진 OpenClaw attribution 헤더(`originator`, `version`, `User-Agent`)는 프록시 URL에 주입되지 않습니다

## 사용 가능한 모델

| Model ID          | 매핑 대상        |
| ----------------- | ---------------- |
| `claude-opus-4`   | Claude Opus 4    |
| `claude-sonnet-4` | Claude Sonnet 4  |
| `claude-haiku-4`  | Claude Haiku 4   |

## macOS에서 자동 시작

프록시를 자동으로 실행하려면 LaunchAgent를 생성하세요.

```bash
cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.claude-max-api</string>
  <key>RunAtLoad</key>
  <true/>
  <key>KeepAlive</key>
  <true/>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/local/bin/node</string>
    <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
  </dict>
</dict>
</plist>
EOF

launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
```

## 링크

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **이슈:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## 참고 사항

- 이것은 **커뮤니티 도구**이며, Anthropic 또는 OpenClaw에서 공식적으로 지원하지 않습니다
- Claude Code CLI 인증이 완료된 활성 Claude Max/Pro 구독이 필요합니다
- 프록시는 로컬에서 실행되며 데이터를 제3자 서버로 전송하지 않습니다
- 스트리밍 응답이 완전히 지원됩니다

## 함께 보기

- [Anthropic provider](/providers/anthropic) - Claude CLI 또는 API 키를 사용하는 기본 OpenClaw 통합
- [OpenAI provider](/providers/openai) - OpenAI/Codex 구독용
