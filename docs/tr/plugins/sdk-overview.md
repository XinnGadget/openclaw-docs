---
read_when:
    - Hangi SDK alt yolundan içe aktarma yapmanız gerektiğini öğrenmeniz gerekiyor
    - OpenClawPluginApi üzerindeki tüm kayıt yöntemleri için bir başvuru istiyorsunuz
    - Belirli bir SDK dışa aktarımını arıyorsunuz
sidebarTitle: SDK Overview
summary: Import map, kayıt API başvurusu ve SDK mimarisi
title: Plugin SDK Genel Bakış
x-i18n:
    generated_at: "2026-04-08T02:17:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: c5a41bd82d165dfbb7fbd6e4528cf322e9133a51efe55fa8518a7a0a626d9d30
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK Genel Bakış

Plugin SDK, plugin'ler ile çekirdek arasındaki türlenmiş sözleşmedir. Bu sayfa,
**neyin içe aktarılacağı** ve **nelerin kaydedilebileceği** için başvurudur.

<Tip>
  **Nasıl yapılır kılavuzu mu arıyorsunuz?**
  - İlk plugin mi? [Başlangıç](/tr/plugins/building-plugins) ile başlayın
  - Kanal plugin'i mi? [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) bölümüne bakın
  - Sağlayıcı plugin'i mi? [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) bölümüne bakın
</Tip>

## İçe aktarma kuralı

Her zaman belirli bir alt yoldan içe aktarın:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Her alt yol küçük, kendi içinde tamamlanmış bir modüldür. Bu, başlangıcın hızlı kalmasını sağlar ve döngüsel bağımlılık sorunlarını önler. Kanala özgü giriş/oluşturma yardımcıları için `openclaw/plugin-sdk/channel-core` tercih edin; daha geniş şemsiye yüzey ve
`buildChannelConfigSchema` gibi paylaşılan yardımcılar için `openclaw/plugin-sdk/core` yolunu kullanın.

`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` veya
kanal markalı yardımcı yüzeyler gibi sağlayıcı adlı kolaylık katmanlarını eklemeyin veya bunlara bağımlı olmayın. Paketlenmiş plugin'ler, kendi `api.ts` veya `runtime-api.ts` barrel dosyalarında genel
SDK alt yollarını birleştirmelidir; çekirdek ise gerçekten kanallar arası bir ihtiyaç olduğunda ya bu plugin'e yerel barrel dosyalarını kullanmalı ya da dar bir genel SDK sözleşmesi eklemelidir.

Üretilen export map hâlâ `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi az sayıda paketlenmiş plugin yardımcı yüzeyi içerir. Bu
alt yollar yalnızca paketlenmiş plugin bakımı ve uyumluluk için vardır; aşağıdaki ortak tabloda bilerek yer verilmemiştir ve yeni üçüncü taraf plugin'leri için önerilen içe aktarma yolu değildir.

## Alt yol başvurusu

En sık kullanılan alt yollar, amaçlarına göre gruplandırılmıştır. 200+ alt yolun
üretilmiş tam listesi `scripts/lib/plugin-sdk-entrypoints.json` içinde bulunur.

Ayrılmış paketlenmiş plugin yardımcı alt yolları bu üretilmiş listede görünmeye devam eder.
Bir doküman sayfası bunlardan birini açıkça genel olarak öne çıkarmadıkça, bunları uygulama ayrıntısı/uyumluluk yüzeyleri olarak değerlendirin.

### Plugin girişi

| Subpath                     | Temel dışa aktarımlar                                                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Kanal alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Kök `openclaw.json` Zod şema dışa aktarımı (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları, allowlist istemleri, kurulum durumu oluşturucuları |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Çok hesaplı yapılandırma/eylem geçidi yardımcıları, varsayılan hesap geri dönüş yardımcıları |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme yardımcıları |
    | `plugin-sdk/account-resolution` | Hesap arama + varsayılan geri dönüş yardımcıları |
    | `plugin-sdk/account-helpers` | Dar hesap listesi/hesap eylemi yardımcıları |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Kanal yapılandırma şeması türleri |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş sözleşme geri dönüşü ile Telegram özel komut normalleştirme/doğrulama yardımcıları |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Paylaşılan inbound route + envelope oluşturucu yardımcıları |
    | `plugin-sdk/inbound-reply-dispatch` | Paylaşılan inbound kayıt ve dispatch yardımcıları |
    | `plugin-sdk/messaging-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/outbound-media` | Paylaşılan outbound medya yükleme yardımcıları |
    | `plugin-sdk/outbound-runtime` | Outbound kimlik/gönderme vekil yardımcıları |
    | `plugin-sdk/thread-bindings-runtime` | Thread-binding yaşam döngüsü ve bağdaştırıcı yardımcıları |
    | `plugin-sdk/agent-media-payload` | Eski agent medya payload oluşturucusu |
    | `plugin-sdk/conversation-runtime` | Konuşma/thread binding, pairing ve yapılandırılmış binding yardımcıları |
    | `plugin-sdk/runtime-config-snapshot` | Çalışma zamanı yapılandırma anlık görüntü yardımcısı |
    | `plugin-sdk/runtime-group-policy` | Çalışma zamanı grup ilkesi çözümleme yardımcıları |
    | `plugin-sdk/channel-status` | Paylaşılan kanal durumu anlık görüntü/özet yardımcıları |
    | `plugin-sdk/channel-config-primitives` | Dar kanal yapılandırma şeması primitive'leri |
    | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yetkilendirme yardımcıları |
    | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal plugin önyüzü dışa aktarımları |
    | `plugin-sdk/allowlist-config-edit` | Allowlist yapılandırma düzenleme/okuma yardımcıları |
    | `plugin-sdk/group-access` | Paylaşılan grup erişim kararı yardımcıları |
    | `plugin-sdk/direct-dm` | Paylaşılan doğrudan DM auth/koruma yardımcıları |
    | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt payload normalleştirme/indirgeme yardımcıları |
    | `plugin-sdk/channel-inbound` | Inbound debounce, mention eşleme, mention-policy yardımcıları ve envelope yardımcıları |
    | `plugin-sdk/channel-send-result` | Yanıt sonuç türleri |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/channel-contract` | Kanal sözleşmesi türleri |
    | `plugin-sdk/channel-feedback` | Geri bildirim/tepki bağlama |
    | `plugin-sdk/channel-secret-runtime` | `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` gibi dar secret-contract yardımcıları ve secret hedef türleri |
  </Accordion>

  <Accordion title="Sağlayıcı alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Düzenlenmiş yerel/self-hosted sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/self-hosted-provider-setup` | Odaklanmış OpenAI uyumlu self-hosted sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/cli-backend` | CLI backend varsayılanları + watchdog sabitleri |
    | `plugin-sdk/provider-auth-runtime` | Sağlayıcı plugin'leri için çalışma zamanı API anahtarı çözümleme yardımcıları |
    | `plugin-sdk/provider-auth-api-key` | `upsertApiKeyProfile` gibi API anahtarı onboarding/profil yazma yardımcıları |
    | `plugin-sdk/provider-auth-result` | Standart OAuth auth-result oluşturucusu |
    | `plugin-sdk/provider-auth-login` | Sağlayıcı plugin'leri için paylaşılan etkileşimli giriş yardımcıları |
    | `plugin-sdk/provider-env-vars` | Sağlayıcı auth env-var arama yardımcıları |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve `normalizeNativeXaiModelId` gibi model kimliği normalleştirme yardımcıları |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Genel sağlayıcı HTTP/uç nokta yetenek yardımcıları |
    | `plugin-sdk/provider-web-fetch-contract` | `enablePluginInConfig` ve `WebFetchProviderPlugin` gibi dar web-fetch yapılandırma/seçim sözleşmesi yardımcıları |
    | `plugin-sdk/provider-web-fetch` | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
    | `plugin-sdk/provider-web-search-contract` | `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` ve kapsamlı kimlik bilgisi ayarlayıcıları/getter'ları gibi dar web-search yapılandırma/kimlik bilgisi sözleşmesi yardımcıları |
    | `plugin-sdk/provider-web-search` | Web-search sağlayıcı kayıt/önbellek/çalışma zamanı yardımcıları |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizleme + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` ve benzerleri |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, stream wrapper türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot wrapper yardımcıları |
    | `plugin-sdk/provider-onboard` | Onboarding yapılandırma yamalama yardımcıları |
    | `plugin-sdk/global-singleton` | Süreç yerel singleton/map/önbellek yardımcıları |
  </Accordion>

  <Accordion title="Auth ve güvenlik alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, komut kayıt yardımcıları, gönderici yetkilendirme yardımcıları |
    | `plugin-sdk/approval-auth-runtime` | Onaylayıcı çözümleme ve aynı sohbet eylem-auth yardımcıları |
    | `plugin-sdk/approval-client-runtime` | Native exec onay profili/filtre yardımcıları |
    | `plugin-sdk/approval-delivery-runtime` | Native onay yeteneği/teslim bağdaştırıcıları |
    | `plugin-sdk/approval-gateway-runtime` | Paylaşılan onay gateway çözümleme yardımcısı |
    | `plugin-sdk/approval-handler-adapter-runtime` | Sıcak kanal giriş noktaları için hafif native onay bağdaştırıcı yükleme yardımcıları |
    | `plugin-sdk/approval-handler-runtime` | Daha geniş onay işleyici çalışma zamanı yardımcıları; dar bağdaştırıcı/gateway yüzeyleri yeterliyse onları tercih edin |
    | `plugin-sdk/approval-native-runtime` | Native onay hedefi + hesap bağlama yardımcıları |
    | `plugin-sdk/approval-reply-runtime` | Exec/plugin onay yanıt payload yardımcıları |
    | `plugin-sdk/command-auth-native` | Native komut auth + native oturum hedef yardımçıları |
    | `plugin-sdk/command-detection` | Paylaşılan komut algılama yardımcıları |
    | `plugin-sdk/command-surface` | Komut gövdesi normalleştirme ve komut yüzeyi yardımcıları |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Kanal/plugin secret yüzeyleri için dar secret-contract toplama yardımcıları |
    | `plugin-sdk/secret-ref-runtime` | Secret-contract/yapılandırma ayrıştırması için dar `coerceSecretRef` ve SecretRef türleme yardımcıları |
    | `plugin-sdk/security-runtime` | Paylaşılan güven, DM geçitleme, harici içerik ve secret toplama yardımcıları |
    | `plugin-sdk/ssrf-policy` | Host allowlist ve private-network SSRF ilkesi yardımcıları |
    | `plugin-sdk/ssrf-runtime` | Pinned-dispatcher, SSRF korumalı fetch ve SSRF ilkesi yardımcıları |
    | `plugin-sdk/secret-input` | Secret giriş ayrıştırma yardımcıları |
    | `plugin-sdk/webhook-ingress` | Webhook istek/hedef yardımcıları |
    | `plugin-sdk/webhook-request-guards` | İstek gövdesi boyutu/zaman aşımı yardımcıları |
  </Accordion>

  <Accordion title="Çalışma zamanı ve depolama alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/runtime` | Geniş çalışma zamanı/günlükleme/yedekleme/plugin kurulum yardımcıları |
    | `plugin-sdk/runtime-env` | Dar çalışma zamanı env, logger, timeout, retry ve backoff yardımcıları |
    | `plugin-sdk/channel-runtime-context` | Genel kanal çalışma zamanı bağlamı kaydı ve arama yardımcıları |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Paylaşılan plugin komutu/hook/http/etkileşimli yardımcıları |
    | `plugin-sdk/hook-runtime` | Paylaşılan webhook/dahili hook pipeline yardımcıları |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod` ve `createLazyRuntimeSurface` gibi tembel çalışma zamanı içe aktarma/bağlama yardımcıları |
    | `plugin-sdk/process-runtime` | Süreç exec yardımcıları |
    | `plugin-sdk/cli-runtime` | CLI biçimlendirme, bekleme ve sürüm yardımcıları |
    | `plugin-sdk/gateway-runtime` | Gateway istemcisi ve kanal durumu yama yardımcıları |
    | `plugin-sdk/config-runtime` | Yapılandırma yükleme/yazma yardımcıları |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş Telegram sözleşme yüzeyi mevcut olmasa bile Telegram komut adı/açıklaması normalleştirme ve yineleme/çakışma kontrolleri |
    | `plugin-sdk/approval-runtime` | Exec/plugin onay yardımcıları, onay yeteneği oluşturucuları, auth/profil yardımcıları, native yönlendirme/çalışma zamanı yardımcıları |
    | `plugin-sdk/reply-runtime` | Paylaşılan inbound/yanıt çalışma zamanı yardımcıları, parçalara ayırma, dispatch, heartbeat, yanıt planlayıcı |
    | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dispatch/finalize yardımcıları |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry` ve `clearHistoryEntriesIfEnabled` gibi paylaşılan kısa pencereli yanıt geçmişi yardımcıları |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Dar metin/markdown parçalara ayırma yardımcıları |
    | `plugin-sdk/session-store-runtime` | Oturum deposu yolu + updated-at yardımcıları |
    | `plugin-sdk/state-paths` | Durum/OAuth dizin yolu yardımcıları |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey` ve `resolveDefaultAgentBoundAccountId` gibi route/oturum anahtarı/hesap bağlama yardımcıları |
    | `plugin-sdk/status-helpers` | Paylaşılan kanal/hesap durumu özeti yardımcıları, çalışma zamanı durumu varsayılanları ve sorun metadata yardımcıları |
    | `plugin-sdk/target-resolver-runtime` | Paylaşılan hedef çözücü yardımcıları |
    | `plugin-sdk/string-normalization-runtime` | Slug/string normalleştirme yardımcıları |
    | `plugin-sdk/request-url` | Fetch/istek benzeri girdilerden string URL çıkarma |
    | `plugin-sdk/run-command` | Normalleştirilmiş stdout/stderr sonuçlarıyla zamanlanmış komut çalıştırıcı |
    | `plugin-sdk/param-readers` | Ortak araç/CLI param okurları |
    | `plugin-sdk/tool-send` | Araç argümanlarından kanonik gönderim hedef alanlarını çıkarma |
    | `plugin-sdk/temp-path` | Paylaşılan geçici indirme yolu yardımcıları |
    | `plugin-sdk/logging-core` | Alt sistem logger ve redaction yardımcıları |
    | `plugin-sdk/markdown-table-runtime` | Markdown tablo kipi yardımcıları |
    | `plugin-sdk/json-store` | Küçük JSON durum okuma/yazma yardımcıları |
    | `plugin-sdk/file-lock` | Yeniden girişli dosya kilidi yardımcıları |
    | `plugin-sdk/persistent-dedupe` | Disk destekli dedupe önbellek yardımcıları |
    | `plugin-sdk/acp-runtime` | ACP çalışma zamanı/oturum ve reply-dispatch yardımcıları |
    | `plugin-sdk/agent-config-primitives` | Dar agent çalışma zamanı yapılandırma şeması primitive'leri |
    | `plugin-sdk/boolean-param` | Gevşek boolean param okuru |
    | `plugin-sdk/dangerous-name-runtime` | Tehlikeli ad eşleme çözümleme yardımcıları |
    | `plugin-sdk/device-bootstrap` | Cihaz bootstrap ve pairing token yardımcıları |
    | `plugin-sdk/extension-shared` | Paylaşılan passive-channel, durum ve ambient proxy yardımcı primitive'leri |
    | `plugin-sdk/models-provider-runtime` | `/models` komutu/sağlayıcı yanıt yardımcıları |
    | `plugin-sdk/skill-commands-runtime` | Skill komutu listeleme yardımcıları |
    | `plugin-sdk/native-command-registry` | Native komut kayıt/oluşturma/serileştirme yardımcıları |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I uç nokta algılama yardımcıları |
    | `plugin-sdk/infra-runtime` | Sistem olayı/heartbeat yardımcıları |
    | `plugin-sdk/collection-runtime` | Küçük sınırlı önbellek yardımcıları |
    | `plugin-sdk/diagnostic-runtime` | Tanılama bayrağı ve olay yardımcıları |
    | `plugin-sdk/error-runtime` | Hata grafiği, biçimlendirme, paylaşılan hata sınıflandırma yardımcıları, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Sarmalanmış fetch, proxy ve pinned lookup yardımcıları |
    | `plugin-sdk/host-runtime` | Hostname ve SCP host normalleştirme yardımcıları |
    | `plugin-sdk/retry-runtime` | Retry yapılandırması ve retry çalıştırıcı yardımcıları |
    | `plugin-sdk/agent-runtime` | Agent dizini/kimlik/çalışma alanı yardımcıları |
    | `plugin-sdk/directory-runtime` | Yapılandırma destekli dizin sorgusu/dedupe |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Yetenek ve test alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Paylaşılan medya fetch/dönüştürme/depolama yardımcıları ve medya payload oluşturucuları |
    | `plugin-sdk/media-generation-runtime` | Paylaşılan medya üretimi failover yardımcıları, aday seçimi ve eksik model mesajları |
    | `plugin-sdk/media-understanding` | Medya anlama sağlayıcı türleri ve sağlayıcıya dönük görsel/ses yardımcı dışa aktarımları |
    | `plugin-sdk/text-runtime` | Asistana görünür metin ayıklama, markdown render/parçalara ayırma/tablo yardımcıları, redaction yardımcıları, directive-tag yardımcıları ve güvenli metin yardımcıları gibi paylaşılan metin/markdown/günlükleme yardımcıları |
    | `plugin-sdk/text-chunking` | Outbound metin parçalara ayırma yardımcısı |
    | `plugin-sdk/speech` | Speech sağlayıcı türleri ve sağlayıcıya dönük directive, registry ve doğrulama yardımcıları |
    | `plugin-sdk/speech-core` | Paylaşılan speech sağlayıcı türleri, registry, directive ve normalleştirme yardımcıları |
    | `plugin-sdk/realtime-transcription` | Realtime transcription sağlayıcı türleri ve registry yardımcıları |
    | `plugin-sdk/realtime-voice` | Realtime voice sağlayıcı türleri ve registry yardımcıları |
    | `plugin-sdk/image-generation` | Image generation sağlayıcı türleri |
    | `plugin-sdk/image-generation-core` | Paylaşılan image-generation türleri, failover, auth ve registry yardımcıları |
    | `plugin-sdk/music-generation` | Music generation sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/music-generation-core` | Paylaşılan music-generation türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/video-generation` | Video generation sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/video-generation-core` | Paylaşılan video-generation türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/webhook-targets` | Webhook hedef kayıt defteri ve route-install yardımcıları |
    | `plugin-sdk/webhook-path` | Webhook yol normalleştirme yardımcıları |
    | `plugin-sdk/web-media` | Paylaşılan uzak/yerel medya yükleme yardımcıları |
    | `plugin-sdk/zod` | Plugin SDK kullanıcıları için yeniden dışa aktarılan `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Bellek alt yolları">
    | Subpath | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/memory-core` | Manager/config/file/CLI yardımcıları için paketlenmiş memory-core yardımcı yüzeyi |
    | `plugin-sdk/memory-core-engine-runtime` | Bellek indeksleme/arama çalışma zamanı cephesi |
    | `plugin-sdk/memory-core-host-engine-foundation` | Bellek host foundation engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek host embedding engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-qmd` | Bellek host QMD engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-storage` | Bellek host storage engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-multimodal` | Bellek host multimodal yardımcıları |
    | `plugin-sdk/memory-core-host-query` | Bellek host sorgu yardımcıları |
    | `plugin-sdk/memory-core-host-secret` | Bellek host secret yardımcıları |
    | `plugin-sdk/memory-core-host-events` | Bellek host olay günlüğü yardımcıları |
    | `plugin-sdk/memory-core-host-status` | Bellek host durum yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-cli` | Bellek host CLI çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-core` | Bellek host çekirdek çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-files` | Bellek host dosya/çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-host-core` | Bellek host çekirdek çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
    | `plugin-sdk/memory-host-events` | Bellek host olay günlüğü yardımcıları için satıcıdan bağımsız takma ad |
    | `plugin-sdk/memory-host-files` | Bellek host dosya/çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
    | `plugin-sdk/memory-host-markdown` | Belleğe bitişik plugin'ler için paylaşılan yönetilen markdown yardımcıları |
    | `plugin-sdk/memory-host-search` | Search-manager erişimi için etkin bellek çalışma zamanı cephesi |
    | `plugin-sdk/memory-host-status` | Bellek host durum yardımcıları için satıcıdan bağımsız takma ad |
    | `plugin-sdk/memory-lancedb` | Paketlenmiş memory-lancedb yardımcı yüzeyi |
  </Accordion>

  <Accordion title="Ayrılmış paketlenmiş yardımcı alt yollar">
    | Family | Mevcut alt yollar | Amaçlanan kullanım |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Paketlenmiş browser plugin destek yardımcıları (`browser-support` uyumluluk barrel'i olarak kalır) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Paketlenmiş Matrix yardımcı/çalışma zamanı yüzeyi |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Paketlenmiş LINE yardımcı/çalışma zamanı yüzeyi |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Paketlenmiş IRC yardımcı yüzeyi |
    | Kanala özgü yardımcılar | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Paketlenmiş kanal uyumluluk/yardımcı yüzeyleri |
    | Auth/plugin'e özgü yardımcılar | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Paketlenmiş özellik/plugin yardımcı yüzeyleri; `plugin-sdk/github-copilot-token` şu anda `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` dışa aktarır |
  </Accordion>
</AccordionGroup>

## Kayıt API'si

`register(api)` callback'i şu yöntemlere sahip bir `OpenClawPluginApi` nesnesi alır:

### Yetenek kaydı

| Method                                           | Ne kaydeder                    |
| ------------------------------------------------ | ------------------------------ |
| `api.registerProvider(...)`                      | Metin çıkarımı (LLM)           |
| `api.registerCliBackend(...)`                    | Yerel CLI çıkarım backend'i    |
| `api.registerChannel(...)`                       | Mesajlaşma kanalı              |
| `api.registerSpeechProvider(...)`                | Metinden konuşmaya / STT sentezi |
| `api.registerRealtimeTranscriptionProvider(...)` | Akış tabanlı realtime transcription |
| `api.registerRealtimeVoiceProvider(...)`         | Çift yönlü realtime voice oturumları |
| `api.registerMediaUnderstandingProvider(...)`    | Görsel/ses/video analizi       |
| `api.registerImageGenerationProvider(...)`       | Görsel üretimi                 |
| `api.registerMusicGenerationProvider(...)`       | Müzik üretimi                  |
| `api.registerVideoGenerationProvider(...)`       | Video üretimi                  |
| `api.registerWebFetchProvider(...)`              | Web fetch / scrape sağlayıcısı |
| `api.registerWebSearchProvider(...)`             | Web araması                    |

### Araçlar ve komutlar

| Method                          | Ne kaydeder                                   |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Agent aracı (zorunlu veya `{ optional: true }`) |
| `api.registerCommand(def)`      | Özel komut (LLM'yi atlar)                     |

### Altyapı

| Method                                         | Ne kaydeder                           |
| ---------------------------------------------- | ------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Olay hook'u                           |
| `api.registerHttpRoute(params)`                | Gateway HTTP uç noktası               |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC yöntemi                   |
| `api.registerCli(registrar, opts?)`            | CLI alt komutu                        |
| `api.registerService(service)`                 | Arka plan hizmeti                     |
| `api.registerInteractiveHandler(registration)` | Etkileşimli işleyici                  |
| `api.registerMemoryPromptSupplement(builder)`  | Toplamsal bellek bitişiği istem bölümü |
| `api.registerMemoryCorpusSupplement(adapter)`  | Toplamsal bellek arama/okuma corpus'u |

Ayrılmış çekirdek yönetici ad alanları (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`), bir plugin daha dar bir gateway method scope atamaya çalışsa bile her zaman `operator.admin` olarak kalır. Plugin'e ait yöntemler için plugin'e özgü önekleri tercih edin.

### CLI kayıt metadata'sı

`api.registerCli(registrar, opts?)` iki tür üst düzey metadata kabul eder:

- `commands`: registrar'a ait açık komut kökleri
- `descriptors`: kök CLI yardımı,
  yönlendirme ve tembel plugin CLI kaydı için ayrıştırma zamanında kullanılan komut açıklayıcıları

Bir plugin komutunun normal kök CLI yolunda tembel yüklenmesini istiyorsanız,
o registrar tarafından sunulan her üst düzey komut kökünü kapsayan `descriptors` sağlayın.

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
        description: "Matrix hesaplarını, doğrulamayı, cihazları ve profil durumunu yönetin",
        hasSubcommands: true,
      },
    ],
  },
);
```

Kök CLI için tembel kayıt gerekmiyorsa yalnızca `commands` kullanın.
Bu hevesli uyumluluk yolu desteklenmeye devam eder, ancak ayrıştırma zamanı tembel yükleme için açıklayıcı destekli yer tutucular kurmaz.

### CLI backend kaydı

`api.registerCliBackend(...)`, bir plugin'in `codex-cli` gibi yerel
AI CLI backend'i için varsayılan yapılandırmaya sahip olmasını sağlar.

- Backend `id`, `codex-cli/gpt-5` gibi model başvurularında sağlayıcı öneki olur.
- Backend `config`, `agents.defaults.cliBackends.<id>` ile aynı şekli kullanır.
- Kullanıcı yapılandırması yine önceliklidir. OpenClaw, CLI'yi çalıştırmadan önce `agents.defaults.cliBackends.<id>` değerini
  plugin varsayılanının üzerine birleştirir.
- Backend'in birleştirmeden sonra uyumluluk yeniden yazımları gerektirdiği durumlarda
  (örneğin eski flag şekillerini normalleştirme) `normalizeConfig` kullanın.

### Özel yuvalar

| Method                                     | Ne kaydeder                         |
| ------------------------------------------ | ----------------------------------- |
| `api.registerContextEngine(id, factory)`   | Bağlam motoru (aynı anda bir etkin) |
| `api.registerMemoryCapability(capability)` | Birleşik bellek yeteneği            |
| `api.registerMemoryPromptSection(builder)` | Bellek istem bölümü oluşturucusu    |
| `api.registerMemoryFlushPlan(resolver)`    | Bellek flush planı çözücüsü         |
| `api.registerMemoryRuntime(runtime)`       | Bellek çalışma zamanı bağdaştırıcısı |

### Bellek embedding bağdaştırıcıları

| Method                                         | Ne kaydeder                                 |
| ---------------------------------------------- | ------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Etkin plugin için bellek embedding bağdaştırıcısı |

- `registerMemoryCapability`, tercih edilen özel bellek-plugin API'sidir.
- `registerMemoryCapability`, eşlik eden plugin'lerin dışa aktarılan bellek artifact'lerini
  belirli bir bellek plugin'inin özel düzenine erişmeden `openclaw/plugin-sdk/memory-host-core` üzerinden tüketebilmesi için `publicArtifacts.listArtifacts(...)`
  de sunabilir.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` ve
  `registerMemoryRuntime`, eskiyle uyumlu özel bellek-plugin API'leridir.
- `registerMemoryEmbeddingProvider`, etkin bellek plugin'inin bir
  veya daha fazla embedding bağdaştırıcı kimliği kaydetmesine izin verir (örneğin `openai`, `gemini` veya plugin tarafından tanımlanan özel bir kimlik).
- `agents.defaults.memorySearch.provider` ve
  `agents.defaults.memorySearch.fallback` gibi kullanıcı yapılandırmaları bu kayıtlı
  bağdaştırıcı kimliklerine göre çözülür.

### Olaylar ve yaşam döngüsü

| Method                                       | Ne yapar                     |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Türlenmiş yaşam döngüsü hook'u |
| `api.onConversationBindingResolved(handler)` | Konuşma binding callback'i   |

### Hook karar semantiği

- `before_tool_call`: `{ block: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_tool_call`: `{ block: false }` döndürmek karar yok olarak değerlendirilir (`block` alanını vermemekle aynı), geçersiz kılma sayılmaz.
- `before_install`: `{ block: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_install`: `{ block: false }` döndürmek karar yok olarak değerlendirilir (`block` alanını vermemekle aynı), geçersiz kılma sayılmaz.
- `reply_dispatch`: `{ handled: true, ... }` döndürmek sonlandırıcıdır. Herhangi bir işleyici dispatch'i sahiplendiğinde, daha düşük öncelikli işleyiciler ve varsayılan model dispatch yolu atlanır.
- `message_sending`: `{ cancel: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `message_sending`: `{ cancel: false }` döndürmek karar yok olarak değerlendirilir (`cancel` alanını vermemekle aynı), geçersiz kılma sayılmaz.

### API nesnesi alanları

| Field                    | Type                      | Açıklama                                                                                   |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | Plugin kimliği                                                                             |
| `api.name`               | `string`                  | Görünen ad                                                                                 |
| `api.version`            | `string?`                 | Plugin sürümü (isteğe bağlı)                                                               |
| `api.description`        | `string?`                 | Plugin açıklaması (isteğe bağlı)                                                           |
| `api.source`             | `string`                  | Plugin kaynak yolu                                                                         |
| `api.rootDir`            | `string?`                 | Plugin kök dizini (isteğe bağlı)                                                           |
| `api.config`             | `OpenClawConfig`          | Geçerli yapılandırma anlık görüntüsü (varsa etkin bellek içi çalışma zamanı anlık görüntüsü) |
| `api.pluginConfig`       | `Record<string, unknown>` | `plugins.entries.<id>.config` altındaki plugin'e özgü yapılandırma                         |
| `api.runtime`            | `PluginRuntime`           | [Çalışma zamanı yardımcıları](/tr/plugins/sdk-runtime)                                        |
| `api.logger`             | `PluginLogger`            | Kapsamlı logger (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`   | `PluginRegistrationMode`  | Geçerli yükleme kipi; `"setup-runtime"` tam giriş öncesi hafif başlangıç/kurulum penceresidir |
| `api.resolvePath(input)` | `(string) => string`      | Plugin köküne göre yolu çözümle                                                            |

## Dahili modül kuralı

Plugin'inizde, dahili içe aktarmalar için yerel barrel dosyaları kullanın:

```
my-plugin/
  api.ts            # Harici tüketiciler için genel dışa aktarımlar
  runtime-api.ts    # Yalnızca dahili çalışma zamanı dışa aktarımları
  index.ts          # Plugin giriş noktası
  setup-entry.ts    # Yalnızca hafif kurulum girişi (isteğe bağlı)
```

<Warning>
  Üretim kodunda kendi plugin'inizi `openclaw/plugin-sdk/<your-plugin>`
  üzerinden asla içe aktarmayın. Dahili içe aktarmaları `./api.ts` veya
  `./runtime-api.ts` üzerinden yönlendirin. SDK yolu yalnızca harici sözleşmedir.
</Warning>

Facade ile yüklenen paketlenmiş plugin genel yüzeyleri (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` ve benzeri genel giriş dosyaları) artık OpenClaw zaten çalışıyorsa etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder. Henüz çalışma zamanı anlık görüntüsü yoksa, disk üzerindeki çözülmüş yapılandırma dosyasına geri dönerler.

Sağlayıcı plugin'leri ayrıca, bir yardımcı kasıtlı olarak sağlayıcıya özgüyse ve henüz genel bir SDK alt yoluna ait değilse, dar bir plugin'e yerel sözleşme barrel dosyası da sunabilir. Güncel paketlenmiş örnek: Anthropic sağlayıcısı, Anthropic beta-header ve `service_tier` mantığını genel bir
`plugin-sdk/*` sözleşmesine yükseltmek yerine Claude stream yardımcılarını kendi genel `api.ts` / `contract-api.ts` yüzeyinde tutar.

Diğer güncel paketlenmiş örnekler:

- `@openclaw/openai-provider`: `api.ts`, sağlayıcı oluşturucularını,
  varsayılan model yardımcılarını ve realtime sağlayıcı oluşturucularını dışa aktarır
- `@openclaw/openrouter-provider`: `api.ts`, sağlayıcı oluşturucusunu ve
  onboarding/yapılandırma yardımcılarını dışa aktarır

<Warning>
  Extension üretim kodu ayrıca `openclaw/plugin-sdk/<other-plugin>`
  içe aktarmalarından da kaçınmalıdır. Bir yardımcı gerçekten paylaşılıyorsa,
  iki plugin'i birbirine bağlamak yerine bunu `openclaw/plugin-sdk/speech`, `.../provider-model-shared` veya başka bir yetenek odaklı yüzey gibi nötr bir SDK alt yoluna yükseltin.
</Warning>

## İlgili

- [Giriş Noktaları](/tr/plugins/sdk-entrypoints) — `definePluginEntry` ve `defineChannelPluginEntry` seçenekleri
- [Çalışma Zamanı Yardımcıları](/tr/plugins/sdk-runtime) — tam `api.runtime` ad alanı başvurusu
- [Kurulum ve Yapılandırma](/tr/plugins/sdk-setup) — paketleme, manifest'ler, yapılandırma şemaları
- [Test](/tr/plugins/sdk-testing) — test yardımcıları ve lint kuralları
- [SDK Geçişi](/tr/plugins/sdk-migration) — kullanımdan kaldırılmış yüzeylerden geçiş
- [Plugin İç Yapısı](/tr/plugins/architecture) — derin mimari ve yetenek modeli
