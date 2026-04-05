---
read_when:
    - Moonshot K2(Moonshot Open Platform)와 Kimi Coding 설정 차이를 알고 싶은 경우
    - 분리된 엔드포인트, 키, 모델 참조를 이해해야 하는 경우
    - 각 provider에 대한 복사/붙여넣기용 구성을 원하는 경우
summary: Moonshot K2와 Kimi Coding 구성하기(분리된 provider + 키)
title: Moonshot AI
x-i18n:
    generated_at: "2026-04-05T12:52:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: a80c71ef432b778e296bd60b7d9ec7c72d025d13fd9bdae474b3d58436d15695
    source_path: providers/moonshot.md
    workflow: 15
---

# Moonshot AI (Kimi)

Moonshot은 OpenAI 호환 엔드포인트를 갖춘 Kimi API를 제공합니다. provider를 구성하고 기본 모델을 `moonshot/kimi-k2.5`로 설정하거나, `kimi/kimi-code`를 사용하여 Kimi Coding을 사용할 수 있습니다.

현재 Kimi K2 모델 ID:

[//]: # "moonshot-kimi-k2-ids:start"

- `kimi-k2.5`
- `kimi-k2-thinking`
- `kimi-k2-thinking-turbo`
- `kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-ids:end"

```bash
openclaw onboard --auth-choice moonshot-api-key
# 또는
openclaw onboard --auth-choice moonshot-api-key-cn
```

Kimi Coding:

```bash
openclaw onboard --auth-choice kimi-code-api-key
```

참고: Moonshot과 Kimi Coding은 별도의 provider입니다. 키는 서로 호환되지 않고, 엔드포인트도 다르며, 모델 참조도 다릅니다(Moonshot은 `moonshot/...`를 사용하고, Kimi Coding은 `kimi/...`를 사용합니다).

Kimi 웹 검색도 Moonshot 플러그인을 사용합니다:

```bash
openclaw configure --section web
```

웹 검색 섹션에서 **Kimi**를 선택하여 `plugins.entries.moonshot.config.webSearch.*`를 저장하세요.

## 구성 스니펫(Moonshot API)

```json5
{
  env: { MOONSHOT_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "moonshot/kimi-k2.5" },
      models: {
        // moonshot-kimi-k2-aliases:start
        "moonshot/kimi-k2.5": { alias: "Kimi K2.5" },
        "moonshot/kimi-k2-thinking": { alias: "Kimi K2 Thinking" },
        "moonshot/kimi-k2-thinking-turbo": { alias: "Kimi K2 Thinking Turbo" },
        "moonshot/kimi-k2-turbo": { alias: "Kimi K2 Turbo" },
        // moonshot-kimi-k2-aliases:end
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [
          // moonshot-kimi-k2-models:start
          {
            id: "kimi-k2.5",
            name: "Kimi K2.5",
            reasoning: false,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-thinking",
            name: "Kimi K2 Thinking",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-thinking-turbo",
            name: "Kimi K2 Thinking Turbo",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 262144,
            maxTokens: 262144,
          },
          {
            id: "kimi-k2-turbo",
            name: "Kimi K2 Turbo",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 256000,
            maxTokens: 16384,
          },
          // moonshot-kimi-k2-models:end
        ],
      },
    },
  },
}
```

## Kimi Coding

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "kimi/kimi-code" },
      models: {
        "kimi/kimi-code": { alias: "Kimi" },
      },
    },
  },
}
```

## Kimi 웹 검색

OpenClaw는 Moonshot 웹 검색을 기반으로 하는 `web_search` provider로 **Kimi**도 함께 제공합니다.

대화형 설정에서는 다음을 물을 수 있습니다:

- Moonshot API 리전:
  - `https://api.moonshot.ai/v1`
  - `https://api.moonshot.cn/v1`
- 기본 Kimi 웹 검색 모델(기본값: `kimi-k2.5`)

구성은 `plugins.entries.moonshot.config.webSearch` 아래에 있습니다:

```json5
{
  plugins: {
    entries: {
      moonshot: {
        config: {
          webSearch: {
            apiKey: "sk-...", // 또는 KIMI_API_KEY / MOONSHOT_API_KEY 사용
            baseUrl: "https://api.moonshot.ai/v1",
            model: "kimi-k2.5",
          },
        },
      },
    },
  },
  tools: {
    web: {
      search: {
        provider: "kimi",
      },
    },
  },
}
```

## 참고

- Moonshot 모델 참조는 `moonshot/<modelId>`를 사용합니다. Kimi Coding 모델 참조는 `kimi/<modelId>`를 사용합니다.
- 현재 Kimi Coding 기본 모델 참조는 `kimi/kimi-code`입니다. 이전의 `kimi/k2p5`도 호환성 모델 ID로 계속 허용됩니다.
- Kimi 웹 검색은 `KIMI_API_KEY` 또는 `MOONSHOT_API_KEY`를 사용하며, 기본값은 `https://api.moonshot.ai/v1`과 모델 `kimi-k2.5`입니다.
- 네이티브 Moonshot 엔드포인트(`https://api.moonshot.ai/v1` 및 `https://api.moonshot.cn/v1`)는 공유 `openai-completions` 전송에서 스트리밍 사용 호환성을 제공한다고 명시합니다. 이제 OpenClaw는 이를 엔드포인트 기능에 따라 판단하므로, 동일한 네이티브 Moonshot 호스트를 대상으로 하는 호환되는 사용자 지정 provider ID도 같은 스트리밍 사용 동작을 상속합니다.
- 필요하면 `models.providers`에서 가격 및 컨텍스트 메타데이터를 재정의하세요.
- Moonshot이 모델에 대해 다른 컨텍스트 한도를 게시하는 경우 `contextWindow`를 그에 맞게 조정하세요.
- 국제 엔드포인트에는 `https://api.moonshot.ai/v1`를 사용하고, 중국 엔드포인트에는 `https://api.moonshot.cn/v1`를 사용하세요.
- 온보딩 선택지:
  - `https://api.moonshot.ai/v1`용 `moonshot-api-key`
  - `https://api.moonshot.cn/v1`용 `moonshot-api-key-cn`

## 네이티브 thinking 모드(Moonshot)

Moonshot Kimi는 이진 네이티브 thinking을 지원합니다:

- `thinking: { type: "enabled" }`
- `thinking: { type: "disabled" }`

`agents.defaults.models.<provider/model>.params`를 통해 모델별로 구성하세요:

```json5
{
  agents: {
    defaults: {
      models: {
        "moonshot/kimi-k2.5": {
          params: {
            thinking: { type: "disabled" },
          },
        },
      },
    },
  },
}
```

OpenClaw는 Moonshot에 대해 런타임 `/think` 수준도 다음과 같이 매핑합니다:

- `/think off` -> `thinking.type=disabled`
- off가 아닌 모든 thinking 수준 -> `thinking.type=enabled`

Moonshot thinking이 활성화되면 `tool_choice`는 `auto` 또는 `none`이어야 합니다. OpenClaw는 호환성을 위해 호환되지 않는 `tool_choice` 값을 `auto`로 정규화합니다.
