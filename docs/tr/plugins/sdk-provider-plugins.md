---
read_when:
    - Yeni bir model provider plugin’i oluşturuyorsunuz
    - OpenClaw’a OpenAI uyumlu bir proxy veya özel LLM eklemek istiyorsunuz
    - Provider auth, kataloglar ve çalışma zamanı hook’larını anlamanız gerekiyor
sidebarTitle: Provider Plugins
summary: OpenClaw için model provider plugin’i oluşturma adım adım kılavuzu
title: Provider Plugin’leri Oluşturma
x-i18n:
    generated_at: "2026-04-06T03:11:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 69500f46aa2cfdfe16e85b0ed9ee3c0032074be46f2d9c9d2940d18ae1095f47
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Provider Plugin’leri Oluşturma

Bu kılavuz, OpenClaw’a bir model provider (LLM) ekleyen bir provider plugin’i oluşturma sürecini anlatır. Sonunda model kataloğu, API anahtarı auth’u ve dinamik model çözümlemesi olan bir provider’ınız olacak.

<Info>
  Daha önce hiç OpenClaw plugin’i oluşturmadıysanız, temel paket yapısı ve
  manifest kurulumu için önce [Başlangıç](/tr/plugins/building-plugins)
  belgesini okuyun.
</Info>

## İzlenecek yol

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket ve manifest">
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

    Manifest, OpenClaw’un plugin çalışma zamanınızı yüklemeden kimlik
    bilgilerini algılayabilmesi için `providerAuthEnvVars` tanımlar.
    `modelSupport` isteğe bağlıdır ve çalışma zamanı hook’ları henüz mevcut
    olmadan önce OpenClaw’un `acme-large` gibi kısa model kimliklerinden
    provider plugin’inizi otomatik yüklemesine olanak tanır. Provider’ı
    ClawHub üzerinde yayımlarsanız, `package.json` içindeki bu
    `openclaw.compat` ve `openclaw.build` alanları zorunludur.

  </Step>

  <Step title="Provider’ı kaydet">
    En küçük çalışan bir provider için `id`, `label`, `auth` ve `catalog` gerekir:

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

    Bu çalışan bir provider’dır. Kullanıcılar artık
    `openclaw onboard --acme-ai-api-key <key>` çalıştırabilir ve
    modelleri olarak `acme-ai/acme-large` seçebilir.

    Yalnızca API anahtarı auth’u ve katalog destekli tek bir çalışma zamanı ile
    tek bir metin provider’ı kaydeden paketlenmiş provider’larda, daha dar
    `defineSingleProviderPluginEntry(...)` yardımcı işlevini tercih edin:

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

    Auth akışınız onboarding sırasında `models.providers.*`, takma adlar ve
    agent varsayılan modelini de düzeltmek zorundaysa,
    `openclaw/plugin-sdk/provider-onboard` içindeki ön ayar yardımcı
    işlevlerini kullanın. En dar yardımcılar
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` ve
    `createModelCatalogPresetAppliers(...)` işlevleridir.

    Bir provider’ın yerel endpoint’i normal `openai-completions` taşınmasında
    akışlı kullanım bloklarını destekliyorsa, provider kimliği denetimlerini
    sabit kodlamak yerine `openclaw/plugin-sdk/provider-catalog-shared`
    içindeki paylaşılan katalog yardımcı işlevlerini tercih edin.
    `supportsNativeStreamingUsageCompat(...)` ve
    `applyProviderNativeStreamingUsageCompat(...)`, desteği endpoint yetenek
    haritasından algılar; böylece özel bir provider kimliği kullanan bir
    plugin’de bile yerel Moonshot/DashScope tarzı endpoint’ler katılabilir.

  </Step>

  <Step title="Dinamik model çözümlemesi ekle">
    Provider’ınız keyfi model kimliklerini kabul ediyorsa (bir proxy veya router gibi),
    `resolveDynamicModel` ekleyin:

    ```typescript
    api.registerProvider({
      // ... yukarıdaki id, label, auth, catalog

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

    Çözümleme için ağ çağrısı gerekiyorsa, eşzamansız ön ısıtma için
    `prepareDynamicModel` kullanın — tamamlandıktan sonra `resolveDynamicModel`
    yeniden çalışır.

  </Step>

  <Step title="Çalışma zamanı hook’ları ekle (gerektiğinde)">
    Çoğu provider için yalnızca `catalog` + `resolveDynamicModel` gerekir.
    Provider’ınız gerektirdikçe hook’ları kademeli olarak ekleyin.

    Paylaşılan yardımcı oluşturucular artık en yaygın replay/tool-compat
    ailelerini kapsıyor, bu yüzden plugin’lerin genelde her hook’u tek tek elle
    bağlaması gerekmez:

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

    Bugün kullanılabilen replay aileleri:

    | Family | Sağladığı bağlantılar |
    | --- | --- |
    | `openai-compatible` | OpenAI uyumlu taşımalar için paylaşılan OpenAI tarzı replay ilkesi; tool-call-id temizleme, assistant-first sıralama düzeltmeleri ve taşımada gerektiğinde genel Gemini-turn doğrulaması dahil |
    | `anthropic-by-model` | `modelId` üzerinden seçilen Claude farkındalıklı replay ilkesi; böylece Anthropic-message taşımaları, çözümlenen model gerçekten bir Claude kimliğiyse yalnızca Claude’a özgü thinking-block temizliğini alır |
    | `google-gemini` | Yerel Gemini replay ilkesi artı bootstrap replay temizliği ve etiketli reasoning-output kipi |
    | `passthrough-gemini` | OpenAI uyumlu proxy taşımaları üzerinden çalışan Gemini modelleri için Gemini thought-signature temizliği; yerel Gemini replay doğrulamasını veya bootstrap yeniden yazımlarını etkinleştirmez |
    | `hybrid-anthropic-openai` | Tek bir plugin içinde Anthropic-message ve OpenAI uyumlu model yüzeylerini karıştıran provider’lar için hibrit ilke; isteğe bağlı yalnızca-Claude thinking-block düşürme, Anthropic tarafıyla sınırlı kalır |

    Gerçek paketlenmiş örnekler:

    - `google`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` ve `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` ve `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` ve `zai`: `openai-compatible`

    Bugün kullanılabilen stream aileleri:

    | Family | Sağladığı bağlantılar |
    | --- | --- |
    | `google-thinking` | Paylaşılan akış yolunda Gemini thinking payload normalizasyonu |
    | `kilocode-thinking` | Paylaşılan proxy akış yolunda Kilo reasoning wrapper’ı; `kilo/auto` ve desteklenmeyen proxy reasoning kimlikleri enjekte edilen thinking’i atlar |
    | `moonshot-thinking` | Config + `/think` düzeyinden Moonshot ikili native-thinking payload eşlemesi |
    | `minimax-fast-mode` | Paylaşılan akış yolunda MiniMax fast-mode model yeniden yazımı |
    | `openai-responses-defaults` | Paylaşılan yerel OpenAI/Codex Responses wrapper’ları: attribution headers, `/fast`/`serviceTier`, metin ayrıntı düzeyi, yerel Codex web search, reasoning-compat payload şekillendirme ve Responses bağlam yönetimi |
    | `openrouter-thinking` | Proxy yolları için OpenRouter reasoning wrapper’ı; desteklenmeyen model/`auto` atlamaları merkezi olarak işlenir |
    | `tool-stream-default-on` | Z.AI gibi, açıkça devre dışı bırakılmadığı sürece tool streaming isteyen provider’lar için varsayılan açık `tool_stream` wrapper’ı |

    Gerçek paketlenmiş örnekler:

    - `google`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` ve `minimax-portal`: `minimax-fast-mode`
    - `openai` ve `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared`, replay-family enum’unu ve bu
    ailelerin üzerine kurulduğu paylaşılan yardımcı işlevleri de dışa aktarır.
    Yaygın ortak dışa aktarımlar şunlardır:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` ve
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)` gibi paylaşılan replay oluşturucuları
    - `sanitizeGoogleGeminiReplayHistory(...)`
      ve `resolveTaggedReasoningOutputMode()` gibi Gemini replay yardımcıları
    - `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` ve
      `normalizeNativeXaiModelId(...)` gibi endpoint/model yardımcıları

    `openclaw/plugin-sdk/provider-stream`, hem aile oluşturucusunu hem de bu
    ailelerin yeniden kullandığı ortak wrapper yardımcı işlevlerini dışa aktarır.
    Yaygın ortak dışa aktarımlar şunlardır:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` ve
      `createCodexNativeWebSearchWrapper(...)` gibi paylaşılan OpenAI/Codex wrapper’ları
    - `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` ve `createMinimaxFastModeWrapper(...)` gibi
      paylaşılan proxy/provider wrapper’ları

    Bazı stream yardımcıları bilerek provider-local kalır. Mevcut paketlenmiş
    örnek: `@openclaw/anthropic-provider`,
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve daha alt düzey
    Anthropic wrapper oluşturucularını ortak `api.ts` /
    `contract-api.ts` seam’inden dışa aktarır. Bu yardımcılar
    Anthropic’e özgü kalır çünkü Claude OAuth beta işleme ve `context1m`
    kapılamasını da kodlarlar.

    Diğer paketlenmiş provider’lar da davranış aileler arasında temiz şekilde
    paylaşılamadığında transport’a özgü wrapper’ları yerel tutar. Mevcut örnek:
    paketlenmiş xAI plugin’i, `/fast` takma ad yeniden yazımları, varsayılan
    `tool_stream`, desteklenmeyen strict-tool temizliği ve xAI’ye özgü
    reasoning-payload kaldırma dahil olmak üzere yerel xAI Responses
    şekillendirmesini kendi `wrapStreamFn` içinde tutar.

    `openclaw/plugin-sdk/provider-tools` şu anda bir paylaşılan tool-schema
    ailesi artı paylaşılan schema/compat yardımcıları sunar:

    - `ProviderToolCompatFamily`, bugün paylaşılan aile envanterini belgelendirir.
    - `buildProviderToolCompatFamilyHooks("gemini")`, Gemini-safe tool schema’lara ihtiyaç duyan provider’lar için Gemini schema temizliği + diagnostics bağlar.
    - `normalizeGeminiToolSchemas(...)` ve `inspectGeminiToolSchemas(...)`, temel ortak Gemini schema yardımcılarıdır.
    - `resolveXaiModelCompatPatch()`, paketlenmiş xAI compat düzeltmesini döndürür:
      `toolSchemaProfile: "xai"`, desteklenmeyen schema anahtar sözcükleri, yerel
      `web_search` desteği ve HTML entity ile kodlanmış tool-call argümanı çözme.
    - `applyXaiModelCompat(model)`, aynı xAI compat düzeltmesini, runner’a ulaşmadan önce çözümlenen modele uygular.

    Gerçek paketlenmiş örnek: xAI plugin’i, bu compat meta verisini çekirdek
    içinde xAI kurallarını sabit kodlamak yerine provider’a ait tutmak için
    `normalizeResolvedModel` ile `contributeResolvedModelCompat` kullanır.

    Aynı paket-kök deseni başka paketlenmiş provider’ları da destekler:

    - `@openclaw/openai-provider`: `api.ts`, provider oluşturucuları,
      default-model yardımcıları ve realtime provider oluşturucularını dışa aktarır
    - `@openclaw/openrouter-provider`: `api.ts`, provider oluşturucusunu
      artı onboarding/config yardımcılarını dışa aktarır

    <Tabs>
      <Tab title="Token exchange">
        Her inference çağrısından önce token exchange gerektiren provider’lar için:

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
      <Tab title="Özel başlıklar">
        Özel istek başlıkları veya body değişiklikleri gerektiren provider’lar için:

        ```typescript
        // wrapStreamFn, ctx.streamFn'den türetilmiş bir StreamFn döndürür
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
      <Tab title="Yerel transport kimliği">
        Genel HTTP veya WebSocket transport’ları üzerinde yerel istek/oturum
        başlıkları veya meta veriler gerektiren provider’lar için:

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
      <Tab title="Kullanım ve faturalama">
        Kullanım/faturalama verileri sunan provider’lar için:

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

    <Accordion title="Kullanılabilir tüm provider hook’ları">
      OpenClaw hook’ları bu sırayla çağırır. Çoğu provider yalnızca 2-3 tanesini kullanır:

      | # | Hook | Ne zaman kullanılmalı |
      | --- | --- | --- |
      | 1 | `catalog` | Model kataloğu veya base URL varsayılanları |
      | 2 | `applyConfigDefaults` | Config somutlaştırması sırasında provider’a ait global varsayılanlar |
      | 3 | `normalizeModelId` | Aramadan önce eski/preview model-id takma ad temizliği |
      | 4 | `normalizeTransport` | Genel model derlemesinden önce provider-family `api` / `baseUrl` temizliği |
      | 5 | `normalizeConfig` | `models.providers.<id>` config’ini normalize et |
      | 6 | `applyNativeStreamingUsageCompat` | Config provider’ları için yerel streaming-usage compat yeniden yazımları |
      | 7 | `resolveConfigApiKey` | Provider’a ait env-marker auth çözümlemesi |
      | 8 | `resolveSyntheticAuth` | Yerel/self-hosted veya config destekli synthetic auth |
      | 9 | `shouldDeferSyntheticProfileAuth` | Synthetic depolanmış profil yer tutucularını env/config auth’un arkasına düşür |
      | 10 | `resolveDynamicModel` | Keyfi upstream model kimliklerini kabul et |
      | 11 | `prepareDynamicModel` | Çözümlemeden önce eşzamansız meta veri getirme |
      | 12 | `normalizeResolvedModel` | Runner’dan önce transport yeniden yazımları |

    Çalışma zamanı geri dönüş notları:

    - `normalizeConfig`, önce eşleşen provider’ı, sonra config gerçekten
      değişene kadar diğer hook-capable provider plugin’lerini denetler.
      Hiçbir provider hook’u desteklenen bir Google-family config girdisini
      yeniden yazmazsa, paketlenmiş Google config normalizer yine uygulanır.
    - `resolveConfigApiKey`, açığa çıkarıldığında provider hook’unu kullanır.
      Paketlenmiş `amazon-bedrock` yolu da burada yerleşik bir AWS env-marker
      çözümleyiciye sahiptir; Bedrock çalışma zamanı auth’u yine de AWS SDK
      varsayılan zincirini kullanıyor olsa bile.
      | 13 | `contributeResolvedModelCompat` | Başka uyumlu bir transport arkasındaki vendor modelleri için compat bayrakları |
      | 14 | `capabilities` | Eski statik capability paketi; yalnızca uyumluluk için |
      | 15 | `normalizeToolSchemas` | Kayıttan önce provider’a ait tool-schema temizliği |
      | 16 | `inspectToolSchemas` | Provider’a ait tool-schema diagnostics |
      | 17 | `resolveReasoningOutputMode` | Etiketli ve yerel reasoning-output sözleşmesi |
      | 18 | `prepareExtraParams` | Varsayılan istek parametreleri |
      | 19 | `createStreamFn` | Tamamen özel StreamFn transport’u |
      | 20 | `wrapStreamFn` | Normal akış yolunda özel başlık/body wrapper’ları |
      | 21 | `resolveTransportTurnState` | Yerel tur başına başlıklar/meta veriler |
      | 22 | `resolveWebSocketSessionPolicy` | Yerel WS oturum başlıkları/cool-down |
      | 23 | `formatApiKey` | Özel çalışma zamanı token biçimi |
      | 24 | `refreshOAuth` | Özel OAuth yenileme |
      | 25 | `buildAuthDoctorHint` | Auth onarım rehberliği |
      | 26 | `matchesContextOverflowError` | Provider’a ait overflow algılama |
      | 27 | `classifyFailoverReason` | Provider’a ait rate-limit/aşırı yük sınıflandırması |
      | 28 | `isCacheTtlEligible` | Prompt cache TTL kapılaması |
      | 29 | `buildMissingAuthMessage` | Özel missing-auth ipucu |
      | 30 | `suppressBuiltInModel` | Eski upstream satırlarını gizle |
      | 31 | `augmentModelCatalog` | Synthetic ileri uyumluluk satırları |
      | 32 | `isBinaryThinking` | İkili thinking açık/kapalı |
      | 33 | `supportsXHighThinking` | `xhigh` reasoning desteği |
      | 34 | `resolveDefaultThinkingLevel` | Varsayılan `/think` ilkesi |
      | 35 | `isModernModelRef` | Live/smoke model eşleştirme |
      | 36 | `prepareRuntimeAuth` | Inference öncesi token exchange |
      | 37 | `resolveUsageAuth` | Özel kullanım kimlik bilgisi ayrıştırma |
      | 38 | `fetchUsageSnapshot` | Özel kullanım endpoint’i |
      | 39 | `createEmbeddingProvider` | Bellek/arama için provider’a ait embedding bağdaştırıcısı |
      | 40 | `buildReplayPolicy` | Özel transcript replay/compaction ilkesi |
      | 41 | `sanitizeReplayHistory` | Genel temizlemeden sonra provider’a özgü replay yeniden yazımları |
      | 42 | `validateReplayTurns` | Embedded runner’dan önce katı replay-turn doğrulaması |
      | 43 | `onModelSelected` | Seçim sonrası callback (ör. telemetry) |

      Prompt ince ayar notu:

      - `resolveSystemPromptContribution`, bir provider’ın bir model ailesi için
        cache farkındalıklı sistem komutu yönlendirmesi enjekte etmesine olanak
        tanır. Davranış tek bir provider/model ailesine aitse ve kararlı/dinamik
        cache ayrımını koruması gerekiyorsa, `before_prompt_build` yerine bunu tercih edin.

      Ayrıntılı açıklamalar ve gerçek dünyadan örnekler için bkz.
      [İç Yapılar: Provider Runtime Hooks](/tr/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Ek yetenekler ekle (isteğe bağlı)">
    <a id="step-5-add-extra-capabilities"></a>
    Bir provider plugin’i, metin inference’ına ek olarak konuşma, gerçek zamanlı
    transcription, gerçek zamanlı voice, medya anlama, görsel oluşturma, video
    oluşturma, web fetch ve web search kaydedebilir:

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

    OpenClaw bunu bir **hybrid-capability** plugin’i olarak sınıflandırır. Bu,
    şirket plugin’leri için önerilen desendir (vendor başına bir plugin). Bkz.
    [İç Yapılar: Capability Ownership](/tr/plugins/architecture#capability-ownership-model).

  </Step>

  <Step title="Test et">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Provider config nesnenizi index.ts dosyasından veya özel bir dosyadan dışa aktarın
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## ClawHub üzerinde yayımla

Provider plugin’leri, diğer tüm harici kod plugin’leriyle aynı şekilde yayımlanır:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Burada eski, yalnızca skill için olan publish takma adını kullanmayın; plugin paketleri
`clawhub package publish` kullanmalıdır.

## Dosya yapısı

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers meta verileri
├── openclaw.plugin.json      # providerAuthEnvVars içeren manifest
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Testler
    └── usage.ts              # Usage endpoint’i (isteğe bağlı)
```

## Catalog order başvurusu

`catalog.order`, kataloğunuzun yerleşik provider’lara göre ne zaman birleştirileceğini denetler:

| Order     | Zamanlama     | Kullanım durumu                                |
| --------- | ------------- | ---------------------------------------------- |
| `simple`  | İlk geçiş     | Düz API anahtarlı provider’lar                 |
| `profile` | `simple` sonrası | Auth profilleriyle kapılanan provider’lar   |
| `paired`  | `profile` sonrası | Birden fazla ilişkili girdiyi sentezle     |
| `late`    | Son geçiş     | Mevcut provider’ları geçersiz kıl (çakışmada kazanır) |

## Sonraki adımlar

- [Channel Plugins](/tr/plugins/sdk-channel-plugins) — plugin’iniz aynı zamanda bir channel da sağlıyorsa
- [SDK Runtime](/tr/plugins/sdk-runtime) — `api.runtime` yardımcıları (TTS, search, subagent)
- [SDK Overview](/tr/plugins/sdk-overview) — tam alt yol import başvurusu
- [Plugin Internals](/tr/plugins/architecture#provider-runtime-hooks) — hook ayrıntıları ve paketlenmiş örnekler
