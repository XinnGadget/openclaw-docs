---
read_when:
    - Yeni bir model provider eklentisi geliştiriyorsunuz
    - OpenClaw'a OpenAI uyumlu bir proxy veya özel bir LLM eklemek istiyorsunuz
    - Provider kimlik doğrulamasını, katalogları ve çalışma zamanı hook'larını anlamanız gerekiyor
sidebarTitle: Provider Plugins
summary: OpenClaw için bir model provider eklentisi geliştirmeye yönelik adım adım kılavuz
title: Provider Eklentileri Geliştirme
x-i18n:
    generated_at: "2026-04-07T08:48:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4da82a353e1bf4fe6dc09e14b8614133ac96565679627de51415926014bd3990
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Provider Eklentileri Geliştirme

Bu kılavuz, OpenClaw'a bir model provider
(LLM) ekleyen bir provider eklentisi geliştirme sürecini adım adım anlatır. Sonunda model kataloğu,
API anahtarı kimlik doğrulaması ve dinamik model çözümlemesi olan bir provider'ınız olacak.

<Info>
  Daha önce hiç OpenClaw eklentisi geliştirmediyseniz, temel paket
  yapısı ve manifesto kurulumu için önce [Getting Started](/tr/plugins/building-plugins) bölümünü okuyun.
</Info>

## Kılavuz

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket ve manifesto">
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

    Manifesto, OpenClaw'ın
    eklenti çalışma zamanınızı yüklemeden kimlik bilgilerini algılayabilmesi için `providerAuthEnvVars` bildirir. `modelSupport` isteğe bağlıdır
    ve çalışma zamanı hook'ları henüz yokken OpenClaw'ın `acme-large` gibi kısa model kimliklerinden
    provider eklentinizi otomatik yüklemesini sağlar. Eğer
    provider'ı ClawHub'da yayımlayacaksanız, `package.json` içindeki bu `openclaw.compat` ve `openclaw.build` alanları
    zorunludur.

  </Step>

  <Step title="Provider'ı kaydetme">
    En az bir provider için `id`, `label`, `auth` ve `catalog` gerekir:

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

    Bu, çalışan bir provider'dır. Kullanıcılar artık
    `openclaw onboard --acme-ai-api-key <key>` çalıştırabilir ve
    modelleri olarak `acme-ai/acme-large` seçebilir.

    Yalnızca API anahtarı
    kimlik doğrulaması ve tek bir katalog destekli çalışma zamanı kaydeden paketlenmiş provider'lar için daha dar kapsamlı
    `defineSingleProviderPluginEntry(...)` yardımcısını tercih edin:

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

    Kimlik doğrulama akışınız onboarding sırasında `models.providers.*`, takma adlar ve
    ajan varsayılan modeli üzerinde de değişiklik yapmayı gerektiriyorsa,
    `openclaw/plugin-sdk/provider-onboard` içindeki ön ayar yardımcılarını kullanın. En dar kapsamlı yardımcılar
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` ve
    `createModelCatalogPresetAppliers(...)` öğeleridir.

    Bir provider'ın yerel uç noktası normal
    `openai-completions` taşımasında akışlı kullanım bloklarını destekliyorsa, provider kimliği denetimlerini
    sabit kodlamak yerine `openclaw/plugin-sdk/provider-catalog-shared` içindeki paylaşılan katalog yardımcılarını tercih edin.
    `supportsNativeStreamingUsageCompat(...)` ve
    `applyProviderNativeStreamingUsageCompat(...)`, desteği
    uç nokta yetenek haritasından algılar; böylece yerel Moonshot/DashScope tarzı uç noktalar da
    eklenti özel bir provider kimliği kullanıyor olsa bile buna katılabilir.

  </Step>

  <Step title="Dinamik model çözümlemesi ekleme">
    Provider'ınız rastgele model kimliklerini kabul ediyorsa (bir proxy veya router gibi),
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

    Çözümleme bir ağ çağrısı gerektiriyorsa, eşzamansız
    ön hazırlık için `prepareDynamicModel` kullanın — tamamlandıktan sonra `resolveDynamicModel` yeniden çalışır.

  </Step>

  <Step title="Çalışma zamanı hook'ları ekleme (gerektikçe)">
    Çoğu provider yalnızca `catalog` + `resolveDynamicModel` gerektirir. Provider'ınızın ihtiyacına göre
    hook'ları kademeli olarak ekleyin.

    Paylaşılan yardımcı oluşturucular artık en yaygın replay/tool-compat
    ailelerini kapsıyor, bu nedenle eklentilerin genellikle her hook'u tek tek
    elle bağlaması gerekmez:

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

    | Aile | Eklediği şey |
    | --- | --- |
    | `openai-compatible` | OpenAI uyumlu taşımalar için paylaşılan OpenAI tarzı replay politikası; tool-call-id temizleme, assistant-first sıralama düzeltmeleri ve taşımanın ihtiyaç duyduğu yerde genel Gemini-turn doğrulaması dahil |
    | `anthropic-by-model` | `modelId` tarafından seçilen Claude farkındalıklı replay politikası; böylece Anthropic-message taşımaları yalnızca çözümlenen model gerçekten bir Claude kimliği olduğunda Claude'a özgü thinking-block temizliği alır |
    | `google-gemini` | Yerel Gemini replay politikası ile bootstrap replay temizliği ve etiketli reasoning-output modu |
    | `passthrough-gemini` | OpenAI uyumlu proxy taşımaları üzerinden çalışan Gemini modelleri için Gemini thought-signature temizliği; yerel Gemini replay doğrulaması veya bootstrap yeniden yazımlarını etkinleştirmez |
    | `hybrid-anthropic-openai` | Tek eklentide Anthropic-message ve OpenAI uyumlu model yüzeylerini karıştıran provider'lar için hibrit politika; isteğe bağlı yalnızca-Claude thinking-block kaldırma davranışı Anthropic tarafıyla sınırlı kalır |

    Gerçek paketlenmiş örnekler:

    - `google` ve `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` ve `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` ve `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` ve `zai`: `openai-compatible`

    Bugün kullanılabilen stream aileleri:

    | Aile | Eklediği şey |
    | --- | --- |
    | `google-thinking` | Paylaşılan stream yolunda Gemini thinking payload normalizasyonu |
    | `kilocode-thinking` | Paylaşılan proxy stream yolunda Kilo reasoning wrapper'ı; `kilo/auto` ve desteklenmeyen proxy reasoning kimlikleri, eklenmiş thinking'i atlar |
    | `moonshot-thinking` | Yapılandırma + `/think` seviyesinden Moonshot ikili native-thinking payload eşlemesi |
    | `minimax-fast-mode` | Paylaşılan stream yolunda MiniMax fast-mode model yeniden yazımı |
    | `openai-responses-defaults` | Paylaşılan yerel OpenAI/Codex Responses wrapper'ları: attribution header'ları, `/fast`/`serviceTier`, metin ayrıntı düzeyi, yerel Codex web search, reasoning-compat payload şekillendirme ve Responses bağlam yönetimi |
    | `openrouter-thinking` | Proxy yolları için OpenRouter reasoning wrapper'ı; desteklenmeyen model/`auto` atlamaları merkezi olarak ele alınır |
    | `tool-stream-default-on` | Açıkça devre dışı bırakılmadıkça tool streaming isteyen Z.AI gibi provider'lar için varsayılan açık `tool_stream` wrapper'ı |

    Gerçek paketlenmiş örnekler:

    - `google` ve `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` ve `minimax-portal`: `minimax-fast-mode`
    - `openai` ve `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared`, replay-family
    enum'unu ve bu ailelerin üzerine kurulduğu paylaşılan yardımcıları da dışa aktarır. Yaygın genel
    dışa aktarımlar şunları içerir:

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

    `openclaw/plugin-sdk/provider-stream`, hem family builder'ı
    hem de bu ailelerin yeniden kullandığı genel wrapper yardımcılarını sunar. Yaygın genel dışa aktarımlar
    şunları içerir:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` ve
      `createCodexNativeWebSearchWrapper(...)` gibi paylaşılan OpenAI/Codex wrapper'ları
    - `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` ve `createMinimaxFastModeWrapper(...)` gibi paylaşılan proxy/provider wrapper'ları

    Bazı stream yardımcıları bilinçli olarak provider yerelinde kalır. Güncel paketlenmiş
    örnek: `@openclaw/anthropic-provider`,
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` ve
    daha düşük seviyeli Anthropic wrapper builder'larını genel `api.ts` /
    `contract-api.ts` arayüzünden dışa aktarır. Bu yardımcılar Anthropic'e özgü kalır çünkü
    Claude OAuth beta işleme ve `context1m` kapılamasını da kodlar.

    Diğer paketlenmiş provider'lar da davranış
    aileler arasında temiz şekilde paylaşılmadığında taşıma-özel wrapper'ları yerel tutar. Güncel örnek: paketlenmiş xAI eklentisi yerel xAI Responses şekillendirmesini
    kendi `wrapStreamFn` içinde tutar; buna `/fast` takma ad yeniden yazımları, varsayılan `tool_stream`,
    desteklenmeyen strict-tool temizliği ve xAI'ye özgü reasoning-payload
    kaldırma dahildir.

    `openclaw/plugin-sdk/provider-tools` şu anda bir paylaşılan
    tool-schema ailesi ile paylaşılan schema/compat yardımcılarını sunar:

    - `ProviderToolCompatFamily`, bugün paylaşılan family envanterini belgeler.
    - `buildProviderToolCompatFamilyHooks("gemini")`, Gemini-güvenli tool schema'lara ihtiyaç duyan provider'lar için Gemini schema
      temizliği + tanılamayı bağlar.
    - `normalizeGeminiToolSchemas(...)` ve `inspectGeminiToolSchemas(...)`,
      alttaki genel Gemini schema yardımcılarıdır.
    - `resolveXaiModelCompatPatch()`, paketlenmiş xAI compat yamasını döndürür:
      `toolSchemaProfile: "xai"`, desteklenmeyen schema anahtar sözcükleri, yerel
      `web_search` desteği ve HTML entity ile kodlanmış tool-call argümanlarının çözülmesi.
    - `applyXaiModelCompat(model)`, aynı xAI compat yamasını
      runner'a ulaşmadan önce çözümlenen modele uygular.

    Gerçek paketlenmiş örnek: xAI eklentisi, bu compat meta verisini
    çekirdekte xAI kurallarını sabit kodlamak yerine provider'ın sahibi olarak tutmak için `normalizeResolvedModel` ile birlikte
    `contributeResolvedModelCompat` kullanır.

    Aynı paket kökü deseni diğer paketlenmiş provider'ları da destekler:

    - `@openclaw/openai-provider`: `api.ts`, provider builder'larını,
      varsayılan model yardımcılarını ve gerçek zamanlı provider builder'larını dışa aktarır
    - `@openclaw/openrouter-provider`: `api.ts`, provider builder'ını
      ve onboarding/yapılandırma yardımcılarını dışa aktarır

    <Tabs>
      <Tab title="Token değişimi">
        Her çıkarım çağrısından önce token değişimi gerektiren provider'lar için:

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
      <Tab title="Özel header'lar">
        Özel istek header'ları veya gövde değişiklikleri gerektiren provider'lar için:

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
      <Tab title="Yerel taşıma kimliği">
        Genel HTTP veya WebSocket taşımalarında yerel istek/oturum header'ları veya meta verileri gereken provider'lar için:

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
        Kullanım/faturalama verilerini açığa çıkaran provider'lar için:

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

    <Accordion title="Kullanılabilir tüm provider hook'ları">
      OpenClaw hook'ları bu sırayla çağırır. Çoğu provider yalnızca 2-3 tanesini kullanır:

      | # | Hook | Ne zaman kullanılır |
      | --- | --- | --- |
      | 1 | `catalog` | Model kataloğu veya base URL varsayılanları |
      | 2 | `applyConfigDefaults` | Yapılandırma somutlaştırması sırasında provider sahipli küresel varsayılanlar |
      | 3 | `normalizeModelId` | Aramadan önce eski/preview model-id takma ad temizliği |
      | 4 | `normalizeTransport` | Genel model derlemesinden önce provider ailesi `api` / `baseUrl` temizliği |
      | 5 | `normalizeConfig` | `models.providers.<id>` yapılandırmasını normalize eder |
      | 6 | `applyNativeStreamingUsageCompat` | Yapılandırma provider'ları için yerel akışlı kullanım uyumluluğu yeniden yazımları |
      | 7 | `resolveConfigApiKey` | Provider sahipli env-marker kimlik doğrulama çözümlemesi |
      | 8 | `resolveSyntheticAuth` | Yerel/self-hosted veya config destekli sentetik kimlik doğrulama |
      | 9 | `shouldDeferSyntheticProfileAuth` | Sentetik saklı profil placeholder'larını env/config kimlik doğrulamasının arkasına alır |
      | 10 | `resolveDynamicModel` | Rastgele upstream model kimliklerini kabul eder |
      | 11 | `prepareDynamicModel` | Çözümlemeden önce eşzamansız meta veri çekme |
      | 12 | `normalizeResolvedModel` | Runner'dan önce taşıma yeniden yazımları |

      Çalışma zamanı geri dönüş notları:

      - `normalizeConfig`, önce eşleşen provider'ı, ardından gerçekten yapılandırmayı değiştiren bir
        hook bulana kadar hook özellikli diğer provider eklentilerini denetler.
        Hiçbir provider hook'u desteklenen bir Google-family yapılandırma girdisini yeniden yazmazsa
        paketlenmiş Google yapılandırma normalizer'ı yine uygulanır.
      - `resolveConfigApiKey`, sunulmuşsa provider hook'unu kullanır. Paketlenmiş
        `amazon-bedrock` yolu burada ayrıca yerleşik bir AWS env-marker çözümleyicisine de sahiptir,
        ancak Bedrock çalışma zamanı kimlik doğrulamasının kendisi hâlâ AWS SDK varsayılan
        zincirini kullanır.
      | 13 | `contributeResolvedModelCompat` | Başka uyumlu bir taşımanın arkasındaki vendor modelleri için uyumluluk bayrakları |
      | 14 | `capabilities` | Eski statik yetenek kümesi; yalnızca uyumluluk için |
      | 15 | `normalizeToolSchemas` | Kayıttan önce provider sahipli tool-schema temizliği |
      | 16 | `inspectToolSchemas` | Provider sahipli tool-schema tanılaması |
      | 17 | `resolveReasoningOutputMode` | Etiketli ve yerel reasoning-output sözleşmesi |
      | 18 | `prepareExtraParams` | Varsayılan istek parametreleri |
      | 19 | `createStreamFn` | Tamamen özel StreamFn taşıması |
      | 20 | `wrapStreamFn` | Normal stream yolunda özel header/gövde wrapper'ları |
      | 21 | `resolveTransportTurnState` | Yerel tur başına header'lar/meta veriler |
      | 22 | `resolveWebSocketSessionPolicy` | Yerel WS oturum header'ları/bekleme süresi |
      | 23 | `formatApiKey` | Özel çalışma zamanı token biçimi |
      | 24 | `refreshOAuth` | Özel OAuth yenileme |
      | 25 | `buildAuthDoctorHint` | Kimlik doğrulama onarım yönlendirmesi |
      | 26 | `matchesContextOverflowError` | Provider sahipli overflow algılama |
      | 27 | `classifyFailoverReason` | Provider sahipli rate-limit/aşırı yük sınıflandırması |
      | 28 | `isCacheTtlEligible` | Prompt cache TTL kapılaması |
      | 29 | `buildMissingAuthMessage` | Özel eksik kimlik doğrulama ipucu |
      | 30 | `suppressBuiltInModel` | Bayat upstream satırlarını gizler |
      | 31 | `augmentModelCatalog` | Sentetik forward-compat satırları |
      | 32 | `isBinaryThinking` | İkili thinking açık/kapalı |
      | 33 | `supportsXHighThinking` | `xhigh` reasoning desteği |
      | 34 | `resolveDefaultThinkingLevel` | Varsayılan `/think` politikası |
      | 35 | `isModernModelRef` | Canlı/smoke model eşleştirmesi |
      | 36 | `prepareRuntimeAuth` | Çıkarımdan önce token değişimi |
      | 37 | `resolveUsageAuth` | Özel kullanım kimlik bilgisi ayrıştırması |
      | 38 | `fetchUsageSnapshot` | Özel kullanım uç noktası |
      | 39 | `createEmbeddingProvider` | Bellek/arama için provider sahipli embedding uyarlayıcısı |
      | 40 | `buildReplayPolicy` | Özel transcript replay/sıkıştırma politikası |
      | 41 | `sanitizeReplayHistory` | Genel temizlemeden sonra provider'a özgü replay yeniden yazımları |
      | 42 | `validateReplayTurns` | Gömülü runner'dan önce katı replay-turn doğrulaması |
      | 43 | `onModelSelected` | Seçim sonrası geri çağırım (örneğin telemetri) |

      Prompt ayarlama notu:

      - `resolveSystemPromptContribution`, bir provider'ın bir model ailesi için cache farkındalıklı
        system prompt yönlendirmesi eklemesini sağlar. Davranış bir provider/model
        ailesine ait olduğunda ve kararlı/dinamik cache ayrımını koruması gerektiğinde
        `before_prompt_build` yerine bunu tercih edin.

      Ayrıntılı açıklamalar ve gerçek dünya örnekleri için bkz.
      [Internals: Provider Runtime Hooks](/tr/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Ek yetenekler ekleme (isteğe bağlı)">
    <a id="step-5-add-extra-capabilities"></a>
    Bir provider eklentisi, metin çıkarımına ek olarak konuşma, gerçek zamanlı transkripsiyon, gerçek zamanlı
    ses, media understanding, image generation, video generation, web fetch
    ve web search kaydedebilir:

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
          generate: {
            maxVideos: 1,
            maxDurationSeconds: 10,
            supportsResolution: true,
          },
          imageToVideo: {
            enabled: true,
            maxVideos: 1,
            maxInputImages: 1,
            maxDurationSeconds: 5,
          },
          videoToVideo: {
            enabled: false,
          },
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

    OpenClaw bunu **hybrid-capability** eklentisi olarak sınıflandırır. Bu,
    şirket eklentileri için önerilen desendir (vendor başına bir eklenti). Bkz.
    [Internals: Capability Ownership](/tr/plugins/architecture#capability-ownership-model).

    Video generation için yukarıda gösterilen mod farkındalıklı yetenek biçimini tercih edin:
    `generate`, `imageToVideo` ve `videoToVideo`. Düz toplu alanlar; örneğin
    `maxInputImages`, `maxInputVideos` ve `maxDurationSeconds`, dönüşüm modu desteğini
    veya devre dışı modları temiz şekilde bildirmek için yeterli değildir.

    Music-generation provider'ları da aynı deseni izlemelidir:
    yalnızca prompt ile üretim için `generate` ve referans görüntü tabanlı
    üretim için `edit`. `maxInputImages`,
    `supportsLyrics` ve `supportsFormat` gibi düz toplu alanlar düzenleme
    desteğini bildirmek için yeterli değildir; beklenen sözleşme açık `generate` / `edit`
    bloklarıdır.

  </Step>

  <Step title="Test">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Provider yapılandırma nesnenizi index.ts veya ayrı bir dosyadan dışa aktarın
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("dinamik modelleri çözümler", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("anahtar mevcut olduğunda katalog döndürür", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("anahtar yoksa null katalog döndürür", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## ClawHub'a yayımlama

Provider eklentileri, diğer tüm dış kod eklentileriyle aynı şekilde yayımlanır:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Burada eski yalnızca-skill yayımlama takma adını kullanmayın; eklenti paketleri
`clawhub package publish` kullanmalıdır.

## Dosya yapısı

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers meta verileri
├── openclaw.plugin.json      # providerAuthEnvVars içeren manifesto
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Testler
    └── usage.ts              # Kullanım uç noktası (isteğe bağlı)
```

## Katalog sırası başvurusu

`catalog.order`, kataloğunuzun yerleşik
provider'lara göre ne zaman birleştirileceğini kontrol eder:

| Sıra      | Ne zaman      | Kullanım durumu                                |
| --------- | ------------- | ---------------------------------------------- |
| `simple`  | İlk geçiş     | Düz API anahtarı provider'ları                 |
| `profile` | `simple` sonrası | Kimlik doğrulama profilleriyle kapılanan provider'lar |
| `paired`  | `profile` sonrası | Birden çok ilişkili girdiyi sentezleme         |
| `late`    | Son geçiş     | Mevcut provider'ları geçersiz kılma (çakışmada kazanır) |

## Sonraki adımlar

- [Channel Plugins](/tr/plugins/sdk-channel-plugins) — eklentiniz ayrıca bir kanal da sağlıyorsa
- [SDK Runtime](/tr/plugins/sdk-runtime) — `api.runtime` yardımcıları (TTS, arama, subagent)
- [SDK Overview](/tr/plugins/sdk-overview) — tam alt yol içe aktarma başvurusu
- [Plugin Internals](/tr/plugins/architecture#provider-runtime-hooks) — hook ayrıntıları ve paketlenmiş örnekler
