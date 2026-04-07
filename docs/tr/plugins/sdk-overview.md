---
read_when:
    - Hangi SDK alt yolundan import yapılacağını bilmeniz gerekiyor
    - OpenClawPluginApi üzerindeki tüm kayıt yöntemleri için bir başvuru istiyorsunuz
    - Belirli bir SDK dışa aktarımını arıyorsunuz
sidebarTitle: SDK Overview
summary: Import eşlemi, kayıt API başvurusu ve SDK mimarisi
title: Plugin SDK Genel Bakış
x-i18n:
    generated_at: "2026-04-07T08:48:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6ba11d1708a117f3872a09fd0bebb0481d36b89b473aec861192e8c2745ef727
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK Genel Bakış

Plugin SDK, plugin'ler ile çekirdek arasındaki türlendirilmiş sözleşmedir. Bu sayfa,
**neyi import edeceğiniz** ve **neleri kaydedebileceğiniz** için başvurudur.

<Tip>
  **Nasıl yapılır kılavuzu mu arıyorsunuz?**
  - İlk plugin mi? [Getting Started](/tr/plugins/building-plugins) ile başlayın
  - Kanal plugin'i mi? Bkz. [Channel Plugins](/tr/plugins/sdk-channel-plugins)
  - Sağlayıcı plugin'i mi? Bkz. [Provider Plugins](/tr/plugins/sdk-provider-plugins)
</Tip>

## Import kuralı

Her zaman belirli bir alt yoldan import edin:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Her alt yol küçük, kendi içinde yeterli bir modüldür. Bu, başlangıcı hızlı tutar ve
döngüsel bağımlılık sorunlarını önler. Kanala özgü giriş/derleme yardımcıları için
`openclaw/plugin-sdk/channel-core` kullanmayı tercih edin; daha geniş şemsiye yüzey ve
`buildChannelConfigSchema` gibi paylaşılan yardımcılar için `openclaw/plugin-sdk/core` yolunu koruyun.

`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` gibi sağlayıcı adlı kolaylık yüzeylerini
veya kanal markalı yardımcı yüzeyleri eklemeyin ya da bunlara bağımlı olmayın. Birlikte gelen plugin'ler,
genel SDK alt yollarını kendi `api.ts` veya `runtime-api.ts` barrel dosyaları içinde birleştirmelidir ve çekirdek
ya bu plugin'e yerel barrel dosyalarını kullanmalı ya da ihtiyaç gerçekten kanallar arasıysa dar bir genel SDK
sözleşmesi eklemelidir.

Üretilen export eşlemi hâlâ `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi küçük bir grup birlikte gelen plugin yardımcı
yüzeyi içerir. Bu alt yollar yalnızca birlikte gelen plugin bakımı ve uyumluluğu için vardır;
aşağıdaki ortak tabloda bilerek yer verilmemiştir ve yeni üçüncü taraf plugin'ler için önerilen
import yolu değildir.

## Alt yol başvurusu

Amaca göre gruplandırılmış, en sık kullanılan alt yollar. 200+ alt yol içeren üretilmiş tam liste
`scripts/lib/plugin-sdk-entrypoints.json` içinde yer alır.

Ayrılmış birlikte gelen plugin yardımcı alt yolları hâlâ bu üretilmiş listede görünür.
Bir doküman sayfası bunlardan birini açıkça genel olarak öne çıkarmıyorsa, bunları uygulama ayrıntısı/uyumluluk yüzeyi olarak değerlendirin.

### Plugin girişi

| Alt yol                     | Temel dışa aktarımlar                                                                                                                 |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Kanal alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Kök `openclaw.json` Zod şeması dışa aktarımı (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları, allowlist istemleri, kurulum durumu oluşturucuları |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Çoklu hesap yapılandırması/eylem geçidi yardımcıları, varsayılan hesap fallback yardımcıları |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalizasyon yardımcıları |
    | `plugin-sdk/account-resolution` | Hesap arama + varsayılan fallback yardımcıları |
    | `plugin-sdk/account-helpers` | Dar hesap listesi/hesap eylemi yardımcıları |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Kanal yapılandırma şeması türleri |
    | `plugin-sdk/telegram-command-config` | Birlikte gelen sözleşme fallback'i ile Telegram özel komut normalizasyonu/doğrulama yardımcıları |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Paylaşılan gelen yönlendirme + envelope oluşturucu yardımcıları |
    | `plugin-sdk/inbound-reply-dispatch` | Paylaşılan gelen kaydetme ve dağıtım yardımcıları |
    | `plugin-sdk/messaging-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/outbound-media` | Paylaşılan giden medya yükleme yardımcıları |
    | `plugin-sdk/outbound-runtime` | Giden kimlik/gönderim temsilcisi yardımcıları |
    | `plugin-sdk/thread-bindings-runtime` | İş parçacığı bağlama yaşam döngüsü ve bağdaştırıcı yardımcıları |
    | `plugin-sdk/agent-media-payload` | Eski ajan medya payload oluşturucusu |
    | `plugin-sdk/conversation-runtime` | Konuşma/iş parçacığı bağlama, pairing ve yapılandırılmış bağlama yardımcıları |
    | `plugin-sdk/runtime-config-snapshot` | Çalışma zamanı yapılandırma anlık görüntüsü yardımcısı |
    | `plugin-sdk/runtime-group-policy` | Çalışma zamanı grup politikası çözümleme yardımcıları |
    | `plugin-sdk/channel-status` | Paylaşılan kanal durum anlık görüntüsü/özet yardımcıları |
    | `plugin-sdk/channel-config-primitives` | Dar kanal yapılandırma şeması temel türleri |
    | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yetkilendirme yardımcıları |
    | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal plugin prelude dışa aktarımları |
    | `plugin-sdk/allowlist-config-edit` | Allowlist yapılandırma düzenleme/okuma yardımcıları |
    | `plugin-sdk/group-access` | Paylaşılan grup erişim kararı yardımcıları |
    | `plugin-sdk/direct-dm` | Paylaşılan doğrudan DM auth/koruma yardımcıları |
    | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt payload normalizasyonu/indirgeme yardımcıları |
    | `plugin-sdk/channel-inbound` | Gelen debounce, mention eşleştirme, mention-policy yardımcıları ve envelope yardımcıları |
    | `plugin-sdk/channel-send-result` | Yanıt sonuç türleri |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/channel-contract` | Kanal sözleşmesi türleri |
    | `plugin-sdk/channel-feedback` | Geri bildirim/tepki bağlantısı |
    | `plugin-sdk/channel-secret-runtime` | `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` gibi dar secret sözleşmesi yardımcıları ve secret hedef türleri |
  </Accordion>

  <Accordion title="Sağlayıcı alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Seçilmiş yerel/self-hosted sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/self-hosted-provider-setup` | Odaklanmış OpenAI uyumlu self-hosted sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/cli-backend` | CLI backend varsayılanları + watchdog sabitleri |
    | `plugin-sdk/provider-auth-runtime` | Sağlayıcı plugin'leri için çalışma zamanı API anahtarı çözümleme yardımcıları |
    | `plugin-sdk/provider-auth-api-key` | `upsertApiKeyProfile` gibi API anahtarı onboarding/profil yazma yardımcıları |
    | `plugin-sdk/provider-auth-result` | Standart OAuth auth-result oluşturucusu |
    | `plugin-sdk/provider-auth-login` | Sağlayıcı plugin'leri için paylaşılan etkileşimli giriş yardımcıları |
    | `plugin-sdk/provider-env-vars` | Sağlayıcı auth env-var arama yardımcıları |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve `normalizeNativeXaiModelId` gibi model kimliği normalizasyon yardımcıları |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Genel sağlayıcı HTTP/uç nokta yeteneği yardımcıları |
    | `plugin-sdk/provider-web-fetch-contract` | `enablePluginInConfig` ve `WebFetchProviderPlugin` gibi dar web-fetch yapılandırma/seçim sözleşmesi yardımcıları |
    | `plugin-sdk/provider-web-fetch` | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
    | `plugin-sdk/provider-web-search-contract` | `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` ve kapsamlı kimlik bilgisi ayarlayıcıları/alıcıları gibi dar web-search yapılandırma/kimlik bilgisi sözleşmesi yardımcıları |
    | `plugin-sdk/provider-web-search` | Web-search sağlayıcı kayıt/önbellek/çalışma zamanı yardımcıları |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizleme + tanılamalar ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` ve benzerleri |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
    | `plugin-sdk/provider-onboard` | Onboarding yapılandırma yama yardımcıları |
    | `plugin-sdk/global-singleton` | İşlem yerel singleton/map/önbellek yardımcıları |
  </Accordion>

  <Accordion title="Kimlik doğrulama ve güvenlik alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, komut kayıt yardımcıları, gönderici yetkilendirme yardımcıları |
    | `plugin-sdk/approval-auth-runtime` | Onaylayıcı çözümleme ve aynı sohbet action-auth yardımcıları |
    | `plugin-sdk/approval-client-runtime` | Yerel exec approval profil/filtre yardımcıları |
    | `plugin-sdk/approval-delivery-runtime` | Yerel approval yeteneği/teslim bağdaştırıcıları |
    | `plugin-sdk/approval-native-runtime` | Yerel approval hedefi + hesap bağlama yardımcıları |
    | `plugin-sdk/approval-reply-runtime` | Exec/plugin approval yanıt payload yardımcıları |
    | `plugin-sdk/command-auth-native` | Yerel komut auth'u + yerel oturum hedefi yardımcıları |
    | `plugin-sdk/command-detection` | Paylaşılan komut algılama yardımcıları |
    | `plugin-sdk/command-surface` | Komut gövdesi normalizasyonu ve komut yüzeyi yardımcıları |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Kanal/plugin secret yüzeyleri için dar secret sözleşmesi toplama yardımcıları |
    | `plugin-sdk/secret-ref-runtime` | Secret sözleşmesi/yapılandırma ayrıştırması için dar `coerceSecretRef` ve SecretRef türlendirme yardımcıları |
    | `plugin-sdk/security-runtime` | Paylaşılan güven, DM geçidi, harici içerik ve secret toplama yardımcıları |
    | `plugin-sdk/ssrf-policy` | Host allowlist ve özel ağ SSRF ilkesi yardımcıları |
    | `plugin-sdk/ssrf-runtime` | Pinned-dispatcher, SSRF korumalı fetch ve SSRF ilkesi yardımcıları |
    | `plugin-sdk/secret-input` | Secret girdi ayrıştırma yardımcıları |
    | `plugin-sdk/webhook-ingress` | Webhook istek/hedef yardımcıları |
    | `plugin-sdk/webhook-request-guards` | İstek gövdesi boyutu/zaman aşımı yardımcıları |
  </Accordion>

  <Accordion title="Çalışma zamanı ve depolama alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/runtime` | Geniş çalışma zamanı/günlükleme/yedekleme/plugin kurulum yardımcıları |
    | `plugin-sdk/runtime-env` | Dar çalışma zamanı env, logger, zaman aşımı, yeniden deneme ve backoff yardımcıları |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Paylaşılan plugin komutu/hook/http/etkileşimli yardımcılar |
    | `plugin-sdk/hook-runtime` | Paylaşılan webhook/dahili hook işlem hattı yardımcıları |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod` ve `createLazyRuntimeSurface` gibi lazy çalışma zamanı import/bağlama yardımcıları |
    | `plugin-sdk/process-runtime` | Process exec yardımcıları |
    | `plugin-sdk/cli-runtime` | CLI biçimlendirme, bekleme ve sürüm yardımcıları |
    | `plugin-sdk/gateway-runtime` | Gateway istemcisi ve kanal-durum yama yardımcıları |
    | `plugin-sdk/config-runtime` | Yapılandırma yükleme/yazma yardımcıları |
    | `plugin-sdk/telegram-command-config` | Birlikte gelen Telegram sözleşme yüzeyi kullanılamadığında bile Telegram komut adı/açıklama normalizasyonu ve kopya/çakışma kontrolleri |
    | `plugin-sdk/approval-runtime` | Exec/plugin approval yardımcıları, approval-yeteneği oluşturucuları, auth/profil yardımcıları, yerel yönlendirme/çalışma zamanı yardımcıları |
    | `plugin-sdk/reply-runtime` | Paylaşılan gelen/yanıt çalışma zamanı yardımcıları, bölme, dağıtım, heartbeat, yanıt planlayıcı |
    | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dağıtımı/sonlandırma yardımcıları |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry` ve `clearHistoryEntriesIfEnabled` gibi paylaşılan kısa pencere reply-history yardımcıları |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Dar metin/markdown bölme yardımcıları |
    | `plugin-sdk/session-store-runtime` | Oturum deposu yolu + updated-at yardımcıları |
    | `plugin-sdk/state-paths` | Durum/OAuth dizin yolu yardımcıları |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey` ve `resolveDefaultAgentBoundAccountId` gibi rota/oturum anahtarı/hesap bağlama yardımcıları |
    | `plugin-sdk/status-helpers` | Paylaşılan kanal/hesap durum özeti yardımcıları, çalışma zamanı durumu varsayılanları ve issue meta veri yardımcıları |
    | `plugin-sdk/target-resolver-runtime` | Paylaşılan hedef çözümleyici yardımcıları |
    | `plugin-sdk/string-normalization-runtime` | Slug/dize normalizasyon yardımcıları |
    | `plugin-sdk/request-url` | Fetch/istek benzeri girdilerden dize URL'leri çıkarma |
    | `plugin-sdk/run-command` | Normalize edilmiş stdout/stderr sonuçlarıyla zamanlanmış komut çalıştırıcısı |
    | `plugin-sdk/param-readers` | Ortak araç/CLI parametre okuyucuları |
    | `plugin-sdk/tool-send` | Araç argümanlarından kanonik gönderim hedefi alanlarını çıkarma |
    | `plugin-sdk/temp-path` | Paylaşılan geçici indirme yolu yardımcıları |
    | `plugin-sdk/logging-core` | Alt sistem logger ve redaction yardımcıları |
    | `plugin-sdk/markdown-table-runtime` | Markdown tablo modu yardımcıları |
    | `plugin-sdk/json-store` | Küçük JSON durum okuma/yazma yardımcıları |
    | `plugin-sdk/file-lock` | Yeniden girişli dosya kilidi yardımcıları |
    | `plugin-sdk/persistent-dedupe` | Disk destekli yinelenen kaldırma önbelleği yardımcıları |
    | `plugin-sdk/acp-runtime` | ACP çalışma zamanı/oturum ve yanıt dağıtımı yardımcıları |
    | `plugin-sdk/agent-config-primitives` | Dar ajan çalışma zamanı yapılandırma şeması temel türleri |
    | `plugin-sdk/boolean-param` | Gevşek boolean parametre okuyucusu |
    | `plugin-sdk/dangerous-name-runtime` | Tehlikeli ad eşleştirme çözümleme yardımcıları |
    | `plugin-sdk/device-bootstrap` | Cihaz bootstrap ve pairing belirteci yardımcıları |
    | `plugin-sdk/extension-shared` | Paylaşılan pasif kanal, durum ve ortam proxy yardımcı temel türleri |
    | `plugin-sdk/models-provider-runtime` | `/models` komutu/sağlayıcı yanıt yardımcıları |
    | `plugin-sdk/skill-commands-runtime` | Skill komut listeleme yardımcıları |
    | `plugin-sdk/native-command-registry` | Yerel komut kayıt/derleme/serileştirme yardımcıları |
    | `plugin-sdk/provider-zai-endpoint` | Z.AI uç nokta algılama yardımcıları |
    | `plugin-sdk/infra-runtime` | Sistem olayı/heartbeat yardımcıları |
    | `plugin-sdk/collection-runtime` | Küçük sınırlı önbellek yardımcıları |
    | `plugin-sdk/diagnostic-runtime` | Tanılama bayrağı ve olay yardımcıları |
    | `plugin-sdk/error-runtime` | Hata grafiği, biçimlendirme, paylaşılan hata sınıflandırma yardımcıları, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Sarılmış fetch, proxy ve pinned arama yardımcıları |
    | `plugin-sdk/host-runtime` | Hostname ve SCP host normalizasyon yardımcıları |
    | `plugin-sdk/retry-runtime` | Yeniden deneme yapılandırması ve yeniden deneme çalıştırıcısı yardımcıları |
    | `plugin-sdk/agent-runtime` | Ajan dizini/kimlik/çalışma alanı yardımcıları |
    | `plugin-sdk/directory-runtime` | Yapılandırma destekli dizin sorgusu/yinelenen kaldırma |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Yetenek ve test alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Medya payload oluşturucularıyla birlikte paylaşılan medya getirme/dönüştürme/depolama yardımcıları |
    | `plugin-sdk/media-generation-runtime` | Paylaşılan medya üretimi failover yardımcıları, aday seçimi ve eksik model mesajlaşması |
    | `plugin-sdk/media-understanding` | Medya anlama sağlayıcı türleri ve sağlayıcıya dönük görsel/ses yardımcı dışa aktarımları |
    | `plugin-sdk/text-runtime` | Yardımcı tarafından görünür metin kaldırma, markdown render/bölme/tablo yardımcıları, redaction yardımcıları, directive-tag yardımcıları ve güvenli metin yardımcıları gibi paylaşılan metin/markdown/günlükleme yardımcıları |
    | `plugin-sdk/text-chunking` | Giden metin bölme yardımcısı |
    | `plugin-sdk/speech` | Konuşma sağlayıcı türleri ve sağlayıcıya dönük directive, registry ve doğrulama yardımcıları |
    | `plugin-sdk/speech-core` | Paylaşılan konuşma sağlayıcı türleri, registry, directive ve normalizasyon yardımcıları |
    | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon sağlayıcı türleri ve registry yardımcıları |
    | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses sağlayıcı türleri ve registry yardımcıları |
    | `plugin-sdk/image-generation` | Görsel üretimi sağlayıcı türleri |
    | `plugin-sdk/image-generation-core` | Paylaşılan görsel üretimi türleri, failover, auth ve registry yardımcıları |
    | `plugin-sdk/music-generation` | Müzik üretimi sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/music-generation-core` | Paylaşılan müzik üretimi türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/video-generation` | Video üretimi sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/video-generation-core` | Paylaşılan video üretimi türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/webhook-targets` | Webhook hedef registry ve rota kurulum yardımcıları |
    | `plugin-sdk/webhook-path` | Webhook yolu normalizasyon yardımcıları |
    | `plugin-sdk/web-media` | Paylaşılan uzak/yerel medya yükleme yardımcıları |
    | `plugin-sdk/zod` | Plugin SDK tüketicileri için yeniden dışa aktarılan `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Bellek alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/memory-core` | Manager/config/file/CLI yardımcıları için birlikte gelen memory-core yardımcı yüzeyi |
    | `plugin-sdk/memory-core-engine-runtime` | Bellek index/search çalışma zamanı cephesi |
    | `plugin-sdk/memory-core-host-engine-foundation` | Bellek host foundation engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek host embedding engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-qmd` | Bellek host QMD engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-storage` | Bellek host storage engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-multimodal` | Bellek host multimodal yardımcıları |
    | `plugin-sdk/memory-core-host-query` | Bellek host query yardımcıları |
    | `plugin-sdk/memory-core-host-secret` | Bellek host secret yardımcıları |
    | `plugin-sdk/memory-core-host-events` | Bellek host olay günlüğü yardımcıları |
    | `plugin-sdk/memory-core-host-status` | Bellek host durum yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-cli` | Bellek host CLI çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-core` | Bellek host çekirdek çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-files` | Bellek host dosya/çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-host-core` | Bellek host çekirdek çalışma zamanı yardımcıları için üretici bağımsız takma ad |
    | `plugin-sdk/memory-host-events` | Bellek host olay günlüğü yardımcıları için üretici bağımsız takma ad |
    | `plugin-sdk/memory-host-files` | Bellek host dosya/çalışma zamanı yardımcıları için üretici bağımsız takma ad |
    | `plugin-sdk/memory-host-markdown` | Belleğe komşu plugin'ler için paylaşılan yönetilen markdown yardımcıları |
    | `plugin-sdk/memory-host-search` | Search-manager erişimi için etkin bellek çalışma zamanı cephesi |
    | `plugin-sdk/memory-host-status` | Bellek host durum yardımcıları için üretici bağımsız takma ad |
    | `plugin-sdk/memory-lancedb` | Birlikte gelen memory-lancedb yardımcı yüzeyi |
  </Accordion>

  <Accordion title="Ayrılmış birlikte gelen yardımcı alt yolları">
    | Aile | Geçerli alt yollar | Amaçlanan kullanım |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Birlikte gelen browser plugin destek yardımcıları (`browser-support` uyumluluk barrel'i olmaya devam eder) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Birlikte gelen Matrix yardımcı/çalışma zamanı yüzeyi |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Birlikte gelen LINE yardımcı/çalışma zamanı yüzeyi |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Birlikte gelen IRC yardımcı yüzeyi |
    | Kanala özgü yardımcılar | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Birlikte gelen kanal uyumluluk/yardımcı yüzeyleri |
    | Auth/plugin'e özgü yardımcılar | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Birlikte gelen özellik/plugin yardımcı yüzeyleri; `plugin-sdk/github-copilot-token` şu anda `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` dışa aktarımlarını içerir |
  </Accordion>
</AccordionGroup>

## Kayıt API'si

`register(api)` geri çağrısı, aşağıdaki yöntemlere sahip bir `OpenClawPluginApi` nesnesi alır:

### Yetenek kaydı

| Yöntem                                           | Ne kaydeder                     |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Metin çıkarımı (LLM)             |
| `api.registerCliBackend(...)`                    | Yerel CLI çıkarım arka ucu       |
| `api.registerChannel(...)`                       | Mesajlaşma kanalı                |
| `api.registerSpeechProvider(...)`                | Metinden konuşmaya / STT sentezi |
| `api.registerRealtimeTranscriptionProvider(...)` | Akışlı gerçek zamanlı transkripsiyon |
| `api.registerRealtimeVoiceProvider(...)`         | Çift yönlü gerçek zamanlı ses oturumları |
| `api.registerMediaUnderstandingProvider(...)`    | Görsel/ses/video analizi         |
| `api.registerImageGenerationProvider(...)`       | Görsel üretimi                   |
| `api.registerMusicGenerationProvider(...)`       | Müzik üretimi                    |
| `api.registerVideoGenerationProvider(...)`       | Video üretimi                    |
| `api.registerWebFetchProvider(...)`              | Web getirme / scrape sağlayıcısı |
| `api.registerWebSearchProvider(...)`             | Web araması                      |

### Araçlar ve komutlar

| Yöntem                          | Ne kaydeder                                  |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Ajan aracı (zorunlu veya `{ optional: true }`) |
| `api.registerCommand(def)`      | Özel komut (LLM'yi atlar)                    |

### Altyapı

| Yöntem                                         | Ne kaydeder                    |
| ---------------------------------------------- | ------------------------------ |
| `api.registerHook(events, handler, opts?)`     | Olay hook'u                    |
| `api.registerHttpRoute(params)`                | Gateway HTTP uç noktası        |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC yöntemi            |
| `api.registerCli(registrar, opts?)`            | CLI alt komutu                 |
| `api.registerService(service)`                 | Arka plan hizmeti              |
| `api.registerInteractiveHandler(registration)` | Etkileşimli işleyici           |
| `api.registerMemoryPromptSupplement(builder)`  | Eklemeli bellek komşusu prompt bölümü |
| `api.registerMemoryCorpusSupplement(adapter)`  | Eklemeli bellek arama/okuma corpus'u |

Ayrılmış çekirdek yönetici ad alanları (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) bir plugin daha dar bir gateway yöntem kapsamı atamaya çalışsa bile her zaman
`operator.admin` olarak kalır. Plugin'e ait yöntemler için plugin'e özgü önekler tercih edin.

### CLI kayıt meta verisi

`api.registerCli(registrar, opts?)` iki tür üst düzey meta veri kabul eder:

- `commands`: registrar'ın sahip olduğu açık komut kökleri
- `descriptors`: kök CLI yardımı, yönlendirme ve lazy plugin CLI kaydı için ayrıştırma zamanlı komut tanımlayıcıları

Bir plugin komutunun normal kök CLI yolunda lazy-loaded kalmasını istiyorsanız,
o registrar tarafından açığa çıkarılan her üst düzey komut kökünü kapsayan `descriptors` sağlayın.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Matrix hesaplarını, doğrulamayı, cihazları ve profil durumunu yönet",
        hasSubcommands: true,
      },
    ],
  },
);
```

`commands` alanını tek başına yalnızca lazy kök CLI kaydına ihtiyacınız yoksa kullanın.
Bu eager uyumluluk yolu desteklenmeye devam eder, ancak ayrıştırma zamanlı lazy yükleme için
descriptor destekli yer tutucular kurmaz.

### CLI backend kaydı

`api.registerCliBackend(...)`, bir plugin'in `codex-cli` gibi yerel bir
AI CLI backend'i için varsayılan yapılandırmaya sahip olmasını sağlar.

- Backend `id`, `codex-cli/gpt-5` gibi model başvurularında sağlayıcı öneki olur.
- Backend `config`, `agents.defaults.cliBackends.<id>` ile aynı şekli kullanır.
- Kullanıcı yapılandırması yine kazanır. OpenClaw, CLI'ı çalıştırmadan önce `agents.defaults.cliBackends.<id>` değerini
  plugin varsayılanı üzerine birleştirir.
- Bir backend birleştirme sonrasında uyumluluk yeniden yazımları gerektiriyorsa
  `normalizeConfig` kullanın (örneğin eski bayrak biçimlerini normalleştirmek için).

### Ayrıcalıklı yuvalar

| Yöntem                                     | Ne kaydeder                         |
| ------------------------------------------ | ----------------------------------- |
| `api.registerContextEngine(id, factory)`   | Bağlam motoru (aynı anda bir etkin) |
| `api.registerMemoryCapability(capability)` | Birleşik bellek yeteneği            |
| `api.registerMemoryPromptSection(builder)` | Bellek prompt bölümü oluşturucusu   |
| `api.registerMemoryFlushPlan(resolver)`    | Bellek flush planı çözümleyicisi    |
| `api.registerMemoryRuntime(runtime)`       | Bellek çalışma zamanı bağdaştırıcısı |

### Bellek embedding bağdaştırıcıları

| Yöntem                                         | Ne kaydeder                                      |
| ---------------------------------------------- | ------------------------------------------------ |
| `api.registerMemoryEmbeddingProvider(adapter)` | Etkin plugin için bellek embedding bağdaştırıcısı |

- `registerMemoryCapability`, tercih edilen ayrıcalıklı bellek-plugin API'sidir.
- `registerMemoryCapability`, eşlik eden plugin'lerin dışa aktarılan bellek artifact'lerini
  belirli bir bellek plugin'inin özel düzenine erişmeden `openclaw/plugin-sdk/memory-host-core` üzerinden tüketebilmesi için
  `publicArtifacts.listArtifacts(...)` da sunabilir.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` ve
  `registerMemoryRuntime`, eski uyumluluğu koruyan ayrıcalıklı bellek-plugin API'leridir.
- `registerMemoryEmbeddingProvider`, etkin bellek plugin'inin bir
  veya daha fazla embedding bağdaştırıcı kimliği kaydetmesini sağlar (örneğin `openai`, `gemini` veya plugin tarafından tanımlanan özel bir kimlik).
- `agents.defaults.memorySearch.provider` ve
  `agents.defaults.memorySearch.fallback` gibi kullanıcı yapılandırmaları bu kayıtlı
  bağdaştırıcı kimliklerine göre çözülür.

### Olaylar ve yaşam döngüsü

| Yöntem                                       | Ne yapar                    |
| -------------------------------------------- | --------------------------- |
| `api.on(hookName, handler, opts?)`           | Türlendirilmiş yaşam döngüsü hook'u |
| `api.onConversationBindingResolved(handler)` | Konuşma bağlama geri çağrısı |

### Hook karar semantiği

- `before_tool_call`: `{ block: true }` döndürmek terminaldir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_tool_call`: `{ block: false }` döndürmek, geçersiz kılma olarak değil, karar yokmuş gibi değerlendirilir (`block` alanını atlamakla aynıdır).
- `before_install`: `{ block: true }` döndürmek terminaldir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_install`: `{ block: false }` döndürmek, geçersiz kılma olarak değil, karar yokmuş gibi değerlendirilir (`block` alanını atlamakla aynıdır).
- `reply_dispatch`: `{ handled: true, ... }` döndürmek terminaldir. Herhangi bir işleyici dağıtımı üstlendiğinde, daha düşük öncelikli işleyiciler ve varsayılan model dağıtım yolu atlanır.
- `message_sending`: `{ cancel: true }` döndürmek terminaldir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `message_sending`: `{ cancel: false }` döndürmek, geçersiz kılma olarak değil, karar yokmuş gibi değerlendirilir (`cancel` alanını atlamakla aynıdır).

### API nesne alanları

| Alan                    | Tür                       | Açıklama                                                                                   |
| ----------------------- | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                | `string`                  | Plugin kimliği                                                                             |
| `api.name`              | `string`                  | Görünen ad                                                                                 |
| `api.version`           | `string?`                 | Plugin sürümü (isteğe bağlı)                                                               |
| `api.description`       | `string?`                 | Plugin açıklaması (isteğe bağlı)                                                           |
| `api.source`            | `string`                  | Plugin kaynak yolu                                                                         |
| `api.rootDir`           | `string?`                 | Plugin kök dizini (isteğe bağlı)                                                           |
| `api.config`            | `OpenClawConfig`          | Geçerli yapılandırma anlık görüntüsü (varsa etkin bellek içi çalışma zamanı anlık görüntüsü) |
| `api.pluginConfig`      | `Record<string, unknown>` | `plugins.entries.<id>.config` içinden plugin'e özgü yapılandırma                           |
| `api.runtime`           | `PluginRuntime`           | [Çalışma zamanı yardımcıları](/tr/plugins/sdk-runtime)                                        |
| `api.logger`            | `PluginLogger`            | Kapsamlı logger (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`  | `PluginRegistrationMode`  | Geçerli yükleme modu; `"setup-runtime"` hafif tam giriş öncesi başlatma/kurulum penceresidir |
| `api.resolvePath(input)`| `(string) => string`      | Yolu plugin köküne göre çözümle                                                            |

## Dahili modül kuralı

Plugin'inizin içinde, dahili import'lar için yerel barrel dosyaları kullanın:

```
my-plugin/
  api.ts            # Harici tüketiciler için genel dışa aktarımlar
  runtime-api.ts    # Yalnızca dahili çalışma zamanı dışa aktarımları
  index.ts          # Plugin giriş noktası
  setup-entry.ts    # Hafif yalnızca kurulum girişi (isteğe bağlı)
```

<Warning>
  Üretim kodunda kendi plugin'inizi asla `openclaw/plugin-sdk/<your-plugin>`
  üzerinden import etmeyin. Dahili import'ları `./api.ts` veya
  `./runtime-api.ts` üzerinden yönlendirin. SDK yolu yalnızca harici sözleşmedir.
</Warning>

Facade ile yüklenen birlikte gelen plugin genel yüzeyleri (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` ve benzeri genel giriş dosyaları), OpenClaw zaten çalışıyorsa artık
etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder. Henüz bir çalışma zamanı
anlık görüntüsü yoksa, diskte çözümlenmiş yapılandırma dosyasına fallback yaparlar.

Sağlayıcı plugin'leri ayrıca, bir yardımcı kasıtlı olarak sağlayıcıya özgüyse ve henüz genel bir SDK
alt yoluna ait değilse, dar bir plugin'e yerel sözleşme barrel'i de açığa çıkarabilir.
Güncel birlikte gelen örnek: Anthropic sağlayıcısı Claude
akış yardımcılarını ve `service_tier` mantığını genel bir
`plugin-sdk/*` sözleşmesine taşımak yerine kendi genel `api.ts` / `contract-api.ts` yüzeyinde tutar.

Diğer güncel birlikte gelen örnekler:

- `@openclaw/openai-provider`: `api.ts`, sağlayıcı oluşturucuları,
  varsayılan model yardımcılarını ve gerçek zamanlı sağlayıcı oluşturucularını dışa aktarır
- `@openclaw/openrouter-provider`: `api.ts`, sağlayıcı oluşturucu ile
  onboarding/config yardımcılarını dışa aktarır

<Warning>
  Extension üretim kodu ayrıca `openclaw/plugin-sdk/<other-plugin>`
  import'larından da kaçınmalıdır. Bir yardımcı gerçekten paylaşılıyorsa, iki plugin'i birbirine bağlamak yerine
  onu `openclaw/plugin-sdk/speech`, `.../provider-model-shared` veya başka
  yetenek odaklı bir yüzey gibi nötr bir SDK alt yoluna taşıyın.
</Warning>

## İlgili

- [Entry Points](/tr/plugins/sdk-entrypoints) — `definePluginEntry` ve `defineChannelPluginEntry` seçenekleri
- [Runtime Helpers](/tr/plugins/sdk-runtime) — tam `api.runtime` ad alanı başvurusu
- [Setup and Config](/tr/plugins/sdk-setup) — paketleme, manifest'ler, yapılandırma şemaları
- [Testing](/tr/plugins/sdk-testing) — test yardımcıları ve lint kuralları
- [SDK Migration](/tr/plugins/sdk-migration) — kullanımdan kaldırılmış yüzeylerden geçiş
- [Plugin Internals](/tr/plugins/architecture) — derin mimari ve yetenek modeli
