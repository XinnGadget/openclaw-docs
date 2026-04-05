---
read_when:
    - 새 모델 제공자 플러그인을 빌드하고 있습니다
    - OpenClaw에 OpenAI 호환 프록시 또는 커스텀 LLM을 추가하려고 합니다
    - 제공자 인증, 카탈로그, 런타임 훅을 이해해야 합니다
sidebarTitle: Provider Plugins
summary: OpenClaw용 모델 제공자 플러그인을 빌드하는 단계별 가이드
title: 제공자 플러그인 빌드하기
x-i18n:
    generated_at: "2026-04-05T12:52:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: e781e5fc436b2189b9f8cc63e7611f49df1fd2526604a0596a0631f49729b085
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# 제공자 플러그인 빌드하기

이 가이드는 OpenClaw에 모델 제공자(LLM)를 추가하는 제공자 플러그인을
빌드하는 과정을 안내합니다. 이 가이드를 마치면 모델 카탈로그,
API 키 인증, 동적 모델 해석이 포함된 제공자를 갖추게 됩니다.

<Info>
  아직 OpenClaw 플러그인을 한 번도 빌드해본 적이 없다면, 먼저
  기본 패키지 구조와 매니페스트 설정을 위해
  [시작하기](/ko/plugins/building-plugins)를 읽어보세요.
</Info>

## 단계별 안내

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="패키지와 매니페스트">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    매니페스트는 `providerAuthEnvVars`를 선언하여 OpenClaw가
    플러그인 런타임을 로드하지 않고도 자격 증명을 감지할 수 있게 합니다.
    `modelSupport`는 선택 사항이며, 런타임 훅이 존재하기 전에
    `acme-large` 같은 축약 모델 ID로부터 OpenClaw가 제공자 플러그인을
    자동 로드할 수 있게 해줍니다. 제공자를 ClawHub에 게시하는 경우
    `package.json`의 `openclaw.compat` 및 `openclaw.build` 필드는
    필수입니다.

  </Step>

  <Step title="제공자 등록">
    최소한의 제공자에는 `id`, `label`, `auth`, `catalog`가 필요합니다:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    이것으로 동작하는 제공자가 완성됩니다. 이제 사용자는
    `openclaw onboard --acme-ai-api-key <key>`를 실행하고
    모델로 `acme-ai/acme-large`를 선택할 수 있습니다.

    API 키 인증과 단일 카탈로그 기반 런타임을 사용하는
    텍스트 제공자 하나만 등록하는 번들 제공자의 경우,
    더 좁은 범위의 `defineSingleProviderPluginEntry(...)`
    헬퍼를 사용하는 것이 좋습니다:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    인증 흐름에서 온보딩 중 `models.providers.*`, 별칭, 에이전트 기본 모델도
    함께 패치해야 하는 경우, `openclaw/plugin-sdk/provider-onboard`의
    프리셋 헬퍼를 사용하세요. 가장 좁은 범위의 헬퍼는
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)`,
    `createModelCatalogPresetAppliers(...)`입니다.

    제공자의 네이티브 엔드포인트가 일반적인 `openai-completions`
    전송에서 스트리밍된 usage 블록을 지원하는 경우, 제공자 ID 확인을
    하드코딩하는 대신
    `openclaw/plugin-sdk/provider-catalog-shared`의 공유 카탈로그 헬퍼를
    사용하는 것이 좋습니다.
    `supportsNativeStreamingUsageCompat(...)`와
    `applyProviderNativeStreamingUsageCompat(...)`는 엔드포인트 기능 맵에서
    지원 여부를 감지하므로, 플러그인이 커스텀 제공자 ID를 사용하더라도
    Moonshot/DashScope 스타일의 네이티브 엔드포인트는 여전히 옵트인할 수
    있습니다.

  </Step>

  <Step title="동적 모델 해석 추가">
    제공자가 임의의 모델 ID를 허용하는 경우(예: 프록시나 라우터),
    `resolveDynamicModel`을 추가하세요:

    ```typescript
    api.registerProvider({
      // ... 위의 id, label, auth, catalog

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    해석에 네트워크 호출이 필요하다면 비동기 워밍업을 위해
    `prepareDynamicModel`을 사용하세요. 완료 후 `resolveDynamicModel`이
    다시 실행됩니다.

  </Step>

  <Step title="런타임 훅 추가(필요한 경우)">
    대부분의 제공자는 `catalog` + `resolveDynamicModel`만 필요합니다.
    제공자에 필요한 만큼 훅을 점진적으로 추가하세요.

    이제 공유 헬퍼 빌더가 가장 일반적인 replay/tool-compat 계열을
    지원하므로, 플러그인은 보통 각 훅을 하나씩 직접 연결할 필요가 없습니다:

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    현재 사용할 수 있는 replay 계열:

    | 계열 | 연결되는 기능 |
    | --- | --- |
    | `openai-compatible` | OpenAI 호환 전송을 위한 공유 OpenAI 스타일 replay 정책으로, tool-call-id 정리, assistant 우선 순서 수정, 그리고 전송 계층에 필요할 때의 일반 Gemini 턴 검증을 포함합니다 |
    | `anthropic-by-model` | `modelId`로 선택되는 Claude 인지 replay 정책으로, Anthropic 메시지 전송은 실제로 해석된 모델이 Claude ID일 때만 Claude 전용 thinking 블록 정리를 적용합니다 |
    | `google-gemini` | 네이티브 Gemini replay 정책과 bootstrap replay 정리, 태그 기반 reasoning-output 모드 |
    | `passthrough-gemini` | OpenAI 호환 프록시 전송을 통해 실행되는 Gemini 모델용 Gemini thought-signature 정리입니다. 네이티브 Gemini replay 검증이나 bootstrap 재작성은 활성화하지 않습니다 |
    | `hybrid-anthropic-openai` | 하나의 플러그인에서 Anthropic 메시지와 OpenAI 호환 모델 표면을 혼합하는 제공자를 위한 하이브리드 정책입니다. 선택적인 Claude 전용 thinking 블록 제거는 Anthropic 측에만 적용됩니다 |

    실제 번들 예시:

    - `google` 및 `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode`, `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` 및 `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai`, `zai`: `openai-compatible`

    현재 사용할 수 있는 stream 계열:

    | 계열 | 연결되는 기능 |
    | --- | --- |
    | `google-thinking` | 공유 stream 경로에서의 Gemini thinking 페이로드 정규화 |
    | `kilocode-thinking` | 공유 프록시 stream 경로에서의 Kilo reasoning 래퍼로, `kilo/auto` 및 지원되지 않는 프록시 reasoning ID는 주입된 thinking을 건너뜁니다 |
    | `moonshot-thinking` | config + `/think` 수준에서 Moonshot 바이너리 native-thinking 페이로드 매핑 |
    | `minimax-fast-mode` | 공유 stream 경로에서의 MiniMax fast-mode 모델 재작성 |
    | `openai-responses-defaults` | 네이티브 OpenAI/Codex Responses용 공유 래퍼: attribution 헤더, `/fast`/`serviceTier`, 텍스트 verbosity, 네이티브 Codex 웹 검색, reasoning-compat 페이로드 형태 조정, Responses 컨텍스트 관리 |
    | `openrouter-thinking` | 프록시 라우트를 위한 OpenRouter reasoning 래퍼로, 지원되지 않는 모델/`auto` 건너뛰기를 중앙에서 처리합니다 |
    | `tool-stream-default-on` | 명시적으로 비활성화되지 않는 한 도구 스트리밍을 원하며 Z.AI 같은 제공자를 위한 기본 활성 `tool_stream` 래퍼 |

    실제 번들 예시:

    - `google` 및 `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` 및 `minimax-portal`: `minimax-fast-mode`
    - `openai` 및 `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared`는 replay 계열 enum과
    그 계열이 기반으로 하는 공유 헬퍼도 함께 내보냅니다. 일반적인 공개 export는
    다음과 같습니다:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)`,
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)` 같은
      공유 replay 빌더
    - `sanitizeGoogleGeminiReplayHistory(...)`,
      `resolveTaggedReasoningOutputMode()` 같은
      Gemini replay 헬퍼
    - `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)`,
      `normalizeNativeXaiModelId(...)` 같은
      엔드포인트/모델 헬퍼

    `openclaw/plugin-sdk/provider-stream`는 계열 빌더와
    그 계열이 재사용하는 공개 래퍼 헬퍼를 모두 노출합니다. 일반적인 공개 export는
    다음과 같습니다:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)`,
      `createCodexNativeWebSearchWrapper(...)` 같은
      공유 OpenAI/Codex 래퍼
    - `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)`,
      `createMinimaxFastModeWrapper(...)` 같은
      공유 프록시/제공자 래퍼

    일부 stream 헬퍼는 의도적으로 제공자 로컬에 남겨둡니다. 현재 번들
    예시: `@openclaw/anthropic-provider`는
    공개 `api.ts` / `contract-api.ts` 경계를 통해
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`,
    그리고 더 낮은 수준의 Anthropic 래퍼 빌더를 export합니다.
    이 헬퍼는 Claude OAuth 베타 처리와 `context1m` 게이팅도 함께 인코딩하므로
    Anthropic 전용으로 유지됩니다.

    다른 번들 제공자도 동작이 계열 간에 깔끔하게 공유되지 않을 때는
    전송별 래퍼를 로컬에 유지합니다. 현재 예시: 번들 xAI 플러그인은
    네이티브 xAI Responses 형태 조정을 자체 `wrapStreamFn` 안에 유지하며,
    여기에는 `/fast` 별칭 재작성, 기본 `tool_stream`,
    지원되지 않는 strict-tool 정리, xAI 전용 reasoning 페이로드
    제거가 포함됩니다.

    `openclaw/plugin-sdk/provider-tools`는 현재 하나의 공유
    tool-schema 계열과 공유 schema/compat 헬퍼를 제공합니다:

    - `ProviderToolCompatFamily`는 현재 공유 계열 목록을 문서화합니다.
    - `buildProviderToolCompatFamilyHooks("gemini")`는
      Gemini 안전 도구 스키마가 필요한 제공자를 위해 Gemini 스키마
      정리 + 진단을 연결합니다.
    - `normalizeGeminiToolSchemas(...)`와 `inspectGeminiToolSchemas(...)`는
      기반이 되는 공개 Gemini 스키마 헬퍼입니다.
    - `resolveXaiModelCompatPatch()`는 번들 xAI compat 패치를 반환합니다:
      `toolSchemaProfile: "xai"`, 지원되지 않는 스키마 키워드, 네이티브
      `web_search` 지원, HTML 엔터티 tool-call 인자 디코딩.
    - `applyXaiModelCompat(model)`는 동일한 xAI compat 패치를
      해석된 모델에 적용한 뒤 runner로 전달합니다.

    실제 번들 예시: xAI 플러그인은 `normalizeResolvedModel`과
    `contributeResolvedModelCompat`를 사용하여 compat 메타데이터를
    코어에 xAI 규칙을 하드코딩하는 대신 제공자가 소유하도록 유지합니다.

    동일한 패키지 루트 패턴은 다른 번들 제공자에도 사용됩니다:

    - `@openclaw/openai-provider`: `api.ts`는 제공자 빌더,
      기본 모델 헬퍼, realtime 제공자 빌더를 export합니다
    - `@openclaw/openrouter-provider`: `api.ts`는 제공자 빌더와
      온보딩/config 헬퍼를 export합니다

    <Tabs>
      <Tab title="토큰 교환">
        각 추론 호출 전에 토큰 교환이 필요한 제공자의 경우:

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="커스텀 헤더">
        커스텀 요청 헤더 또는 본문 수정이 필요한 제공자의 경우:

        ```typescript
        // wrapStreamFn은 ctx.streamFn에서 파생된 StreamFn을 반환합니다
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="네이티브 전송 식별">
        일반 HTTP 또는 WebSocket 전송에서 네이티브 요청/세션 헤더 또는
        메타데이터가 필요한 제공자의 경우:

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="사용량 및 과금">
        사용량/과금 데이터를 노출하는 제공자의 경우:

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="사용 가능한 모든 제공자 훅">
      OpenClaw는 이 순서로 훅을 호출합니다. 대부분의 제공자는 2-3개만 사용합니다:

      | # | Hook | 사용 시점 |
      | --- | --- | --- |
      | 1 | `catalog` | 모델 카탈로그 또는 기본 base URL |
      | 2 | `applyConfigDefaults` | config 구체화 중 제공자 소유의 전역 기본값 |
      | 3 | `normalizeModelId` | 조회 전 레거시/프리뷰 모델 ID 별칭 정리 |
      | 4 | `normalizeTransport` | 일반 모델 조립 전 제공자 계열 `api` / `baseUrl` 정리 |
      | 5 | `normalizeConfig` | `models.providers.<id>` config 정규화 |
      | 6 | `applyNativeStreamingUsageCompat` | config 제공자용 네이티브 스트리밍 사용량 compat 재작성 |
      | 7 | `resolveConfigApiKey` | 제공자 소유의 env-marker 인증 해석 |
      | 8 | `resolveSyntheticAuth` | 로컬/셀프호스팅 또는 config 기반 synthetic 인증 |
      | 9 | `shouldDeferSyntheticProfileAuth` | env/config 인증 뒤로 synthetic 저장 프로필 플레이스홀더를 낮춤 |
      | 10 | `resolveDynamicModel` | 임의의 업스트림 모델 ID 허용 |
      | 11 | `prepareDynamicModel` | 해석 전 비동기 메타데이터 가져오기 |
      | 12 | `normalizeResolvedModel` | runner 전송 전 전송 재작성 |

    런타임 폴백 참고:

    - `normalizeConfig`는 먼저 일치하는 제공자를 확인한 다음,
      실제로 config를 변경하는 훅 지원 제공자 플러그인을 차례로 확인합니다.
      어떤 제공자 훅도 지원되는 Google 계열 config 항목을 재작성하지 않으면,
      번들 Google config 정규화기가 계속 적용됩니다.
    - `resolveConfigApiKey`는 노출되어 있으면 제공자 훅을 사용합니다.
      번들 `amazon-bedrock` 경로에는
      Bedrock 런타임 인증 자체는 여전히 AWS SDK 기본 체인을 사용하더라도,
      여기에서 내장 AWS env-marker 해석기가 있습니다.
      | 13 | `contributeResolvedModelCompat` | 다른 호환 전송 뒤에 있는 벤더 모델용 compat 플래그 |
      | 14 | `capabilities` | 레거시 정적 capability bag, 호환성 전용 |
      | 15 | `normalizeToolSchemas` | 등록 전 제공자 소유의 tool-schema 정리 |
      | 16 | `inspectToolSchemas` | 제공자 소유의 tool-schema 진단 |
      | 17 | `resolveReasoningOutputMode` | 태그 기반 대 네이티브 reasoning-output 계약 |
      | 18 | `prepareExtraParams` | 기본 요청 params |
      | 19 | `createStreamFn` | 완전히 커스텀 StreamFn 전송 |
      | 20 | `wrapStreamFn` | 일반 stream 경로의 커스텀 헤더/본문 래퍼 |
      | 21 | `resolveTransportTurnState` | 네이티브 턴별 헤더/메타데이터 |
      | 22 | `resolveWebSocketSessionPolicy` | 네이티브 WS 세션 헤더/쿨다운 |
      | 23 | `formatApiKey` | 커스텀 런타임 토큰 형태 |
      | 24 | `refreshOAuth` | 커스텀 OAuth 갱신 |
      | 25 | `buildAuthDoctorHint` | 인증 복구 안내 |
      | 26 | `matchesContextOverflowError` | 제공자 소유의 오버플로 감지 |
      | 27 | `classifyFailoverReason` | 제공자 소유의 rate-limit/overload 분류 |
      | 28 | `isCacheTtlEligible` | 프롬프트 캐시 TTL 게이팅 |
      | 29 | `buildMissingAuthMessage` | 커스텀 누락 인증 안내 |
      | 30 | `suppressBuiltInModel` | 오래된 업스트림 행 숨기기 |
      | 31 | `augmentModelCatalog` | synthetic forward-compat 행 |
      | 32 | `isBinaryThinking` | 바이너리 thinking on/off |
      | 33 | `supportsXHighThinking` | `xhigh` reasoning 지원 |
      | 34 | `resolveDefaultThinkingLevel` | 기본 `/think` 정책 |
      | 35 | `isModernModelRef` | 라이브/스모크 모델 일치 |
      | 36 | `prepareRuntimeAuth` | 추론 전 토큰 교환 |
      | 37 | `resolveUsageAuth` | 커스텀 사용량 자격 증명 파싱 |
      | 38 | `fetchUsageSnapshot` | 커스텀 사용량 엔드포인트 |
      | 39 | `createEmbeddingProvider` | 메모리/검색용 제공자 소유 임베딩 어댑터 |
      | 40 | `buildReplayPolicy` | 커스텀 transcript replay/compaction 정책 |
      | 41 | `sanitizeReplayHistory` | 일반 정리 이후 제공자별 replay 재작성 |
      | 42 | `validateReplayTurns` | 임베디드 runner 전 엄격한 replay-turn 검증 |
      | 43 | `onModelSelected` | 선택 후 콜백(예: 텔레메트리) |

      자세한 설명과 실제 예시는
      [내부 구조: 제공자 런타임 훅](/plugins/architecture#provider-runtime-hooks)을
      참고하세요.
    </Accordion>

  </Step>

  <Step title="추가 기능 더하기(선택 사항)">
    <a id="step-5-add-extra-capabilities"></a>
    제공자 플러그인은 텍스트 추론과 함께 음성, 실시간 전사, 실시간
    음성, 미디어 이해, 이미지 생성, 비디오 생성, 웹 가져오기,
    웹 검색을 등록할 수 있습니다:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          maxVideos: 1,
          maxDurationSeconds: 10,
          supportsResolution: true,
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Fetch pages through Acme's rendering backend.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Fetch a page through Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw는 이를 **하이브리드 기능** 플러그인으로 분류합니다.
    이것이 회사용 플러그인에 권장되는 패턴입니다(벤더당 플러그인 하나).
    [내부 구조: 기능 소유권](/plugins/architecture#capability-ownership-model)을
    참고하세요.

  </Step>

  <Step title="테스트">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // 제공자 config 객체를 index.ts 또는 별도 파일에서 export하세요
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("동적 모델을 해석한다", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("키가 있으면 카탈로그를 반환한다", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("키가 없으면 null 카탈로그를 반환한다", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## ClawHub에 게시

제공자 플러그인은 다른 외부 코드 플러그인과 동일한 방식으로 게시합니다:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

여기에서는 레거시 skill 전용 게시 별칭을 사용하지 마세요.
플러그인 패키지는 `clawhub package publish`를 사용해야 합니다.

## 파일 구조

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers 메타데이터
├── openclaw.plugin.json      # providerAuthEnvVars가 포함된 매니페스트
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # 테스트
    └── usage.ts              # 사용량 엔드포인트(선택 사항)
```

## 카탈로그 순서 참고

`catalog.order`는 내장 제공자와 비교해 카탈로그가 언제 병합되는지 제어합니다:

| 순서 | 시점 | 사용 사례 |
| --------- | ------------- | ----------------------------------------------- |
| `simple`  | 첫 번째 패스 | 일반 API 키 제공자 |
| `profile` | simple 이후 | 인증 프로필에 의해 제한되는 제공자 |
| `paired`  | profile 이후 | 여러 관련 항목을 합성 |
| `late`    | 마지막 패스 | 기존 제공자를 덮어씀(충돌 시 우선) |

## 다음 단계

- [채널 플러그인](/ko/plugins/sdk-channel-plugins) — 플러그인이 채널도 제공하는 경우
- [SDK 런타임](/ko/plugins/sdk-runtime) — `api.runtime` 헬퍼(TTS, 검색, subagent)
- [SDK 개요](/plugins/sdk-overview) — 전체 서브패스 import 참고 자료
- [플러그인 내부 구조](/plugins/architecture#provider-runtime-hooks) — 훅 세부 사항과 번들 예시
