---
read_when:
    - Hangi SDK alt yolundan içe aktarma yapmanız gerektiğini bilmeniz gerekiyor
    - OpenClawPluginApi üzerindeki tüm kayıt yöntemleri için bir başvuru istiyorsunuz
    - Belirli bir SDK dışa aktarımını arıyorsunuz
sidebarTitle: SDK Overview
summary: İçe aktarma eşlemesi, kayıt API başvurusu ve SDK mimarisi
title: Plugin SDK Genel Bakış
x-i18n:
    generated_at: "2026-04-06T03:11:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: d801641f26f39dc21490d2a69a337ff1affb147141360916b8b58a267e9f822a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK Genel Bakış

Plugin SDK, eklentiler ile çekirdek arasındaki türlendirilmiş sözleşmedir. Bu sayfa,
**neyin içe aktarılacağı** ve **neleri kaydedebileceğiniz** için başvurudur.

<Tip>
  **Nasıl yapılır kılavuzu mu arıyorsunuz?**
  - İlk eklenti mi? [Başlarken](/tr/plugins/building-plugins) ile başlayın
  - Kanal eklentisi mi? [Kanal Eklentileri](/tr/plugins/sdk-channel-plugins) bölümüne bakın
  - Sağlayıcı eklentisi mi? [Sağlayıcı Eklentileri](/tr/plugins/sdk-provider-plugins) bölümüne bakın
</Tip>

## İçe aktarma kuralı

Her zaman belirli bir alt yoldan içe aktarın:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Her alt yol küçük, kendi içinde yeterli bir modüldür. Bu, başlangıcı hızlı tutar ve
döngüsel bağımlılık sorunlarını önler. Kanala özgü giriş/oluşturma yardımcıları için
`openclaw/plugin-sdk/channel-core` yolunu tercih edin; daha geniş şemsiye yüzeyi ve
`buildChannelConfigSchema` gibi paylaşılan yardımcılar için
`openclaw/plugin-sdk/core` yolunu kullanın.

`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` veya
kanal markalı yardımcı yüzeyler gibi sağlayıcı adlı kolaylık yolları eklemeyin ya da bunlara bağlı kalmayın.
Paketlenmiş eklentiler, genel
SDK alt yollarını kendi `api.ts` veya `runtime-api.ts` barrel dosyaları içinde birleştirmelidir ve çekirdek
ya bu eklenti yerel barrel dosyalarını kullanmalı ya da ihtiyaç gerçekten kanallar arasıysa
dar bir genel SDK sözleşmesi eklemelidir.

Oluşturulan dışa aktarma eşlemesi hâlâ `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi
küçük bir paketlenmiş eklenti yardımcı yüzeyi kümesi içerir. Bu
alt yollar yalnızca paketlenmiş eklenti bakımı ve uyumluluk içindir; aşağıdaki ortak tabloda kasıtlı olarak
yer almazlar ve yeni üçüncü taraf eklentiler için önerilen
içe aktarma yolu değildirler.

## Alt yol başvurusu

En yaygın kullanılan alt yollar, amaçlarına göre gruplandırılmıştır. 200'den fazla alt yolun
oluşturulmuş tam listesi `scripts/lib/plugin-sdk-entrypoints.json` içinde bulunur.

Ayrılmış paketlenmiş eklenti yardımcı alt yolları bu oluşturulmuş listede görünmeye devam eder.
Bir belge sayfası birini açıkça genel olarak öne çıkarmadıkça, bunları uygulama ayrıntısı/uyumluluk yüzeyleri olarak değerlendirin.

### Eklenti girişi

| Alt yol                    | Temel dışa aktarımlar                                                                                                                  |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`  | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`          | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema` | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                     |

<AccordionGroup>
  <Accordion title="Kanal alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Kök `openclaw.json` Zod şeması dışa aktarımı (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları, izin listesi istemleri, kurulum durumu oluşturucuları |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Çok hesaplı yapılandırma/eylem kapısı yardımcıları, varsayılan hesap geri dönüş yardımcıları |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalizasyon yardımcıları |
    | `plugin-sdk/account-resolution` | Hesap arama + varsayılan geri dönüş yardımcıları |
    | `plugin-sdk/account-helpers` | Dar hesap listesi/hesap eylemi yardımcıları |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Kanal yapılandırma şeması türleri |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş sözleşme geri dönüşüyle Telegram özel komut normalizasyonu/doğrulama yardımcıları |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Paylaşılan gelen yönlendirme + zarf oluşturucu yardımcıları |
    | `plugin-sdk/inbound-reply-dispatch` | Paylaşılan gelen kayıt etme ve dağıtım yardımcıları |
    | `plugin-sdk/messaging-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/outbound-media` | Paylaşılan giden medya yükleme yardımcıları |
    | `plugin-sdk/outbound-runtime` | Giden kimlik/gönderme temsilci yardımcıları |
    | `plugin-sdk/thread-bindings-runtime` | İş parçacığı bağlama yaşam döngüsü ve bağdaştırıcı yardımcıları |
    | `plugin-sdk/agent-media-payload` | Eski aracı medya yükü oluşturucu |
    | `plugin-sdk/conversation-runtime` | Konuşma/iş parçacığı bağlama, eşleştirme ve yapılandırılmış bağlama yardımcıları |
    | `plugin-sdk/runtime-config-snapshot` | Çalışma zamanı yapılandırma anlık görüntüsü yardımcısı |
    | `plugin-sdk/runtime-group-policy` | Çalışma zamanı grup ilkesi çözümleme yardımcıları |
    | `plugin-sdk/channel-status` | Paylaşılan kanal durum anlık görüntüsü/özet yardımcıları |
    | `plugin-sdk/channel-config-primitives` | Dar kanal yapılandırma-şeması ilkelleri |
    | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yetkilendirme yardımcıları |
    | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal eklentisi başlangıç dışa aktarımları |
    | `plugin-sdk/allowlist-config-edit` | İzin listesi yapılandırma düzenleme/okuma yardımcıları |
    | `plugin-sdk/group-access` | Paylaşılan grup erişimi karar yardımcıları |
    | `plugin-sdk/direct-dm` | Paylaşılan doğrudan DM kimlik doğrulama/koruma yardımcıları |
    | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yükü normalizasyonu/indirgeme yardımcıları |
    | `plugin-sdk/channel-inbound` | Debounce, mention eşleştirme, zarf yardımcıları |
    | `plugin-sdk/channel-send-result` | Yanıt sonuç türleri |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/channel-contract` | Kanal sözleşmesi türleri |
    | `plugin-sdk/channel-feedback` | Geri bildirim/tepki bağlantısı |
  </Accordion>

  <Accordion title="Sağlayıcı alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Seçilmiş yerel/kendi barındırılan sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/self-hosted-provider-setup` | Odaklı OpenAI uyumlu kendi barındırılan sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/provider-auth-runtime` | Sağlayıcı eklentileri için çalışma zamanı API anahtarı çözümleme yardımcıları |
    | `plugin-sdk/provider-auth-api-key` | API anahtarı başlangıcı/profil yazma yardımcıları |
    | `plugin-sdk/provider-auth-result` | Standart OAuth kimlik doğrulama sonucu oluşturucusu |
    | `plugin-sdk/provider-auth-login` | Sağlayıcı eklentileri için paylaşılan etkileşimli giriş yardımcıları |
    | `plugin-sdk/provider-env-vars` | Sağlayıcı kimlik doğrulama ortam değişkeni arama yardımcıları |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan yeniden oynatma ilkesi oluşturucuları, sağlayıcı uç nokta yardımcıları ve `normalizeNativeXaiModelId` gibi model kimliği normalizasyon yardımcıları |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Genel sağlayıcı HTTP/uç nokta yetenek yardımcıları |
    | `plugin-sdk/provider-web-fetch` | Web-fetch sağlayıcı kaydı/önbellek yardımcıları |
    | `plugin-sdk/provider-web-search` | Web arama sağlayıcı kaydı/önbellek/yapılandırma yardımcıları |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizliği + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` ve benzerleri |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
    | `plugin-sdk/provider-onboard` | Başlangıç yapılandırması yama yardımcıları |
    | `plugin-sdk/global-singleton` | İşlem yerel singleton/eşleme/önbellek yardımcıları |
  </Accordion>

  <Accordion title="Kimlik doğrulama ve güvenlik alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, komut kayıt yardımcıları, gönderen yetkilendirme yardımcıları |
    | `plugin-sdk/approval-auth-runtime` | Onaylayan çözümleme ve aynı sohbet eylem kimlik doğrulama yardımcıları |
    | `plugin-sdk/approval-client-runtime` | Yerel exec onay profili/filtre yardımcıları |
    | `plugin-sdk/approval-delivery-runtime` | Yerel onay yeteneği/teslim bağdaştırıcıları |
    | `plugin-sdk/approval-native-runtime` | Yerel onay hedefi + hesap bağlama yardımcıları |
    | `plugin-sdk/approval-reply-runtime` | Exec/eklenti onay yanıt yükü yardımcıları |
    | `plugin-sdk/command-auth-native` | Yerel komut kimlik doğrulama + yerel oturum hedefi yardımcıları |
    | `plugin-sdk/command-detection` | Paylaşılan komut algılama yardımcıları |
    | `plugin-sdk/command-surface` | Komut gövdesi normalizasyonu ve komut yüzeyi yardımcıları |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Paylaşılan güven, DM geçitleme, dış içerik ve gizli bilgi toplama yardımcıları |
    | `plugin-sdk/ssrf-policy` | Ana makine izin listesi ve özel ağ SSRF ilkesi yardımcıları |
    | `plugin-sdk/ssrf-runtime` | Sabitlenmiş dağıtıcı, SSRF korumalı fetch ve SSRF ilkesi yardımcıları |
    | `plugin-sdk/secret-input` | Gizli bilgi girdisi ayrıştırma yardımcıları |
    | `plugin-sdk/webhook-ingress` | Webhook istek/hedef yardımcıları |
    | `plugin-sdk/webhook-request-guards` | İstek gövdesi boyutu/zaman aşımı yardımcıları |
  </Accordion>

  <Accordion title="Çalışma zamanı ve depolama alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/runtime` | Geniş çalışma zamanı/günlükleme/yedekleme/eklenti kurulum yardımcıları |
    | `plugin-sdk/runtime-env` | Dar çalışma zamanı ortamı, günlükleyici, zaman aşımı, yeniden deneme ve backoff yardımcıları |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Paylaşılan eklenti komutu/kanca/http/etkileşimli yardımcıları |
    | `plugin-sdk/hook-runtime` | Paylaşılan webhook/dahili kanca hattı yardımcıları |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod` ve `createLazyRuntimeSurface` gibi tembel çalışma zamanı içe aktarma/bağlama yardımcıları |
    | `plugin-sdk/process-runtime` | Süreç exec yardımcıları |
    | `plugin-sdk/cli-runtime` | CLI biçimlendirme, bekleme ve sürüm yardımcıları |
    | `plugin-sdk/gateway-runtime` | Gateway istemcisi ve kanal durumu yama yardımcıları |
    | `plugin-sdk/config-runtime` | Yapılandırma yükleme/yazma yardımcıları |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş Telegram sözleşme yüzeyi kullanılamasa bile Telegram komut adı/açıklama normalizasyonu ve yinelenen/çakışma denetimleri |
    | `plugin-sdk/approval-runtime` | Exec/eklenti onay yardımcıları, onay yeteneği oluşturucuları, kimlik doğrulama/profil yardımcıları, yerel yönlendirme/çalışma zamanı yardımcıları |
    | `plugin-sdk/reply-runtime` | Paylaşılan gelen/yanıt çalışma zamanı yardımcıları, parçalama, dağıtım, heartbeat, yanıt planlayıcı |
    | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dağıtımı/sonlandırma yardımcıları |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry` ve `clearHistoryEntriesIfEnabled` gibi paylaşılan kısa pencere yanıt geçmişi yardımcıları |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Dar metin/markdown parçalama yardımcıları |
    | `plugin-sdk/session-store-runtime` | Oturum deposu yolu + güncellenme zamanı yardımcıları |
    | `plugin-sdk/state-paths` | Durum/OAuth dizin yolu yardımcıları |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey` ve `resolveDefaultAgentBoundAccountId` gibi yönlendirme/oturum anahtarı/hesap bağlama yardımcıları |
    | `plugin-sdk/status-helpers` | Paylaşılan kanal/hesap durumu özeti yardımcıları, çalışma zamanı durumu varsayılanları ve sorun meta verisi yardımcıları |
    | `plugin-sdk/target-resolver-runtime` | Paylaşılan hedef çözücü yardımcıları |
    | `plugin-sdk/string-normalization-runtime` | Slug/dize normalizasyon yardımcıları |
    | `plugin-sdk/request-url` | Fetch/istek benzeri girdilerden dize URL'leri çıkarma |
    | `plugin-sdk/run-command` | Normalize stdout/stderr sonuçları ile zamanlı komut çalıştırıcı |
    | `plugin-sdk/param-readers` | Yaygın araç/CLI parametre okuyucuları |
    | `plugin-sdk/tool-send` | Araç argümanlarından standart gönderim hedefi alanlarını çıkarma |
    | `plugin-sdk/temp-path` | Paylaşılan geçici indirme yolu yardımcıları |
    | `plugin-sdk/logging-core` | Alt sistem günlükleyicisi ve sansürleme yardımcıları |
    | `plugin-sdk/markdown-table-runtime` | Markdown tablo kipi yardımcıları |
    | `plugin-sdk/json-store` | Küçük JSON durumu okuma/yazma yardımcıları |
    | `plugin-sdk/file-lock` | Yeniden girişli dosya kilidi yardımcıları |
    | `plugin-sdk/persistent-dedupe` | Disk destekli tekilleştirme önbelleği yardımcıları |
    | `plugin-sdk/acp-runtime` | ACP çalışma zamanı/oturum ve yanıt dağıtım yardımcıları |
    | `plugin-sdk/agent-config-primitives` | Dar aracı çalışma zamanı yapılandırma-şeması ilkelleri |
    | `plugin-sdk/boolean-param` | Esnek boolean parametre okuyucusu |
    | `plugin-sdk/dangerous-name-runtime` | Tehlikeli ad eşleştirme çözümleme yardımcıları |
    | `plugin-sdk/device-bootstrap` | Cihaz bootstrap ve eşleştirme belirteci yardımcıları |
    | `plugin-sdk/extension-shared` | Paylaşılan pasif kanal ve durum yardımcı ilkelleri |
    | `plugin-sdk/models-provider-runtime` | `/models` komutu/sağlayıcı yanıt yardımcıları |
    | `plugin-sdk/skill-commands-runtime` | Skill komut listeleme yardımcıları |
    | `plugin-sdk/native-command-registry` | Yerel komut kaydı/oluşturma/serileştirme yardımcıları |
    | `plugin-sdk/provider-zai-endpoint` | Z.AI uç nokta algılama yardımcıları |
    | `plugin-sdk/infra-runtime` | Sistem olayı/heartbeat yardımcıları |
    | `plugin-sdk/collection-runtime` | Küçük sınırlı önbellek yardımcıları |
    | `plugin-sdk/diagnostic-runtime` | Tanılama bayrağı ve olay yardımcıları |
    | `plugin-sdk/error-runtime` | Hata grafiği, biçimlendirme, paylaşılan hata sınıflandırma yardımcıları, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Sarılmış fetch, proxy ve sabitlenmiş arama yardımcıları |
    | `plugin-sdk/host-runtime` | Ana makine adı ve SCP ana makine normalizasyon yardımcıları |
    | `plugin-sdk/retry-runtime` | Yeniden deneme yapılandırması ve yeniden deneme çalıştırıcı yardımcıları |
    | `plugin-sdk/agent-runtime` | Aracı dizini/kimlik/çalışma alanı yardımcıları |
    | `plugin-sdk/directory-runtime` | Yapılandırma destekli dizin sorgulama/tekilleştirme |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Yetenek ve test alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Medya yükü oluşturucularına ek olarak paylaşılan medya getirme/dönüştürme/depolama yardımcıları |
    | `plugin-sdk/media-understanding` | Medya anlama sağlayıcı türleri ile sağlayıcıya dönük görsel/ses yardımcı dışa aktarımları |
    | `plugin-sdk/text-runtime` | Aracıya görünür metin temizleme, markdown işleme/parçalama/tablo yardımcıları, sansürleme yardımcıları, yönerge etiketi yardımcıları ve güvenli metin yardımcıları gibi paylaşılan metin/markdown/günlükleme yardımcıları |
    | `plugin-sdk/text-chunking` | Giden metin parçalama yardımcısı |
    | `plugin-sdk/speech` | Konuşma sağlayıcı türleri ile sağlayıcıya dönük yönerge, kayıt ve doğrulama yardımcıları |
    | `plugin-sdk/speech-core` | Paylaşılan konuşma sağlayıcı türleri, kayıt, yönerge ve normalizasyon yardımcıları |
    | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon sağlayıcı türleri ve kayıt yardımcıları |
    | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses sağlayıcı türleri ve kayıt yardımcıları |
    | `plugin-sdk/image-generation` | Görsel üretimi sağlayıcı türleri |
    | `plugin-sdk/image-generation-core` | Paylaşılan görsel üretimi türleri, geri dönüş, kimlik doğrulama ve kayıt yardımcıları |
    | `plugin-sdk/music-generation` | Müzik üretimi sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/music-generation-core` | Paylaşılan müzik üretimi türleri, geri dönüş yardımcıları, sağlayıcı arama ve model başvurusu ayrıştırma |
    | `plugin-sdk/video-generation` | Video üretimi sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/video-generation-core` | Paylaşılan video üretimi türleri, geri dönüş yardımcıları, sağlayıcı arama ve model başvurusu ayrıştırma |
    | `plugin-sdk/webhook-targets` | Webhook hedef kaydı ve rota kurulum yardımcıları |
    | `plugin-sdk/webhook-path` | Webhook yolu normalizasyon yardımcıları |
    | `plugin-sdk/web-media` | Paylaşılan uzak/yerel medya yükleme yardımcıları |
    | `plugin-sdk/zod` | Plugin SDK kullanıcıları için yeniden dışa aktarılmış `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Bellek alt yolları">
    | Alt yol | Temel dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/memory-core` | Yönetici/yapılandırma/dosya/CLI yardımcıları için paketlenmiş memory-core yardımcı yüzeyi |
    | `plugin-sdk/memory-core-engine-runtime` | Bellek dizini/arama çalışma zamanı cephesi |
    | `plugin-sdk/memory-core-host-engine-foundation` | Bellek ana makine temel motoru dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek ana makine gömme motoru dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-qmd` | Bellek ana makine QMD motoru dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-storage` | Bellek ana makine depolama motoru dışa aktarımları |
    | `plugin-sdk/memory-core-host-multimodal` | Bellek ana makine çok modlu yardımcıları |
    | `plugin-sdk/memory-core-host-query` | Bellek ana makine sorgu yardımcıları |
    | `plugin-sdk/memory-core-host-secret` | Bellek ana makine gizli bilgi yardımcıları |
    | `plugin-sdk/memory-core-host-status` | Bellek ana makine durum yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-cli` | Bellek ana makine CLI çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-core` | Bellek ana makine çekirdek çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-files` | Bellek ana makine dosya/çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-lancedb` | Paketlenmiş memory-lancedb yardımcı yüzeyi |
  </Accordion>

  <Accordion title="Ayrılmış paketlenmiş yardımcı alt yolları">
    | Aile | Geçerli alt yollar | Amaçlanan kullanım |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Paketlenmiş browser eklentisi destek yardımcıları (`browser-support` uyumluluk barrel'i olarak kalır) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Paketlenmiş Matrix yardımcı/çalışma zamanı yüzeyi |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Paketlenmiş LINE yardımcı/çalışma zamanı yüzeyi |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Paketlenmiş IRC yardımcı yüzeyi |
    | Kanala özgü yardımcılar | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Paketlenmiş kanal uyumluluğu/yardımcı yüzeyleri |
    | Kimlik doğrulama/eklentiye özgü yardımcılar | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Paketlenmiş özellik/eklenti yardımcı yüzeyleri; `plugin-sdk/github-copilot-token` şu anda `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` dışa aktarımlarını içerir |
  </Accordion>
</AccordionGroup>

## Kayıt API'si

`register(api)` geri çağırımı, şu yöntemlere sahip bir `OpenClawPluginApi` nesnesi alır:

### Yetenek kaydı

| Yöntem                                           | Kaydettiği şey                |
| ------------------------------------------------ | ----------------------------- |
| `api.registerProvider(...)`                      | Metin çıkarımı (LLM)          |
| `api.registerChannel(...)`                       | Mesajlaşma kanalı             |
| `api.registerSpeechProvider(...)`                | Metinden konuşmaya / STT sentezi |
| `api.registerRealtimeTranscriptionProvider(...)` | Akışlı gerçek zamanlı transkripsiyon |
| `api.registerRealtimeVoiceProvider(...)`         | Çift yönlü gerçek zamanlı ses oturumları |
| `api.registerMediaUnderstandingProvider(...)`    | Görsel/ses/video analizi      |
| `api.registerImageGenerationProvider(...)`       | Görsel üretimi                |
| `api.registerMusicGenerationProvider(...)`       | Müzik üretimi                 |
| `api.registerVideoGenerationProvider(...)`       | Video üretimi                 |
| `api.registerWebFetchProvider(...)`              | Web fetch / scrape sağlayıcısı |
| `api.registerWebSearchProvider(...)`             | Web arama                     |

### Araçlar ve komutlar

| Yöntem                          | Kaydettiği şey                               |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Aracı aracı (zorunlu veya `{ optional: true }`) |
| `api.registerCommand(def)`      | Özel komut (LLM'yi atlar)                    |

### Altyapı

| Yöntem                                         | Kaydettiği şey         |
| ---------------------------------------------- | ---------------------- |
| `api.registerHook(events, handler, opts?)`     | Olay kancası           |
| `api.registerHttpRoute(params)`                | Gateway HTTP uç noktası |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC yöntemi    |
| `api.registerCli(registrar, opts?)`            | CLI alt komutu         |
| `api.registerService(service)`                 | Arka plan hizmeti      |
| `api.registerInteractiveHandler(registration)` | Etkileşimli işleyici   |

Ayrılmış çekirdek yönetici ad alanları (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) bir eklenti daha dar bir gateway yöntem kapsamı atamaya çalışsa bile her zaman
`operator.admin` olarak kalır. Eklentiye ait yöntemler için
eklentiye özgü önekleri tercih edin.

### CLI kayıt meta verisi

`api.registerCli(registrar, opts?)`, iki tür üst düzey meta veri kabul eder:

- `commands`: kayıtçının sahip olduğu açık komut kökleri
- `descriptors`: kök CLI yardımı, yönlendirme ve tembel eklenti CLI kaydı için
  ayrıştırma zamanındaki komut tanımlayıcıları

Bir eklenti komutunun normal kök CLI yolunda tembel yüklemeli kalmasını istiyorsanız,
o kayıtçının açığa çıkardığı her üst düzey komut kökünü kapsayan `descriptors`
sağlayın.

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

`commands` tek başına yalnızca normal kök CLI'de tembel kayıt gerekmediğinde kullanılmalıdır.
Bu hevesli uyumluluk yolu desteklenmeye devam eder, ancak ayrıştırma zamanında tembel yükleme için
tanımlayıcı destekli yer tutucular kurmaz.

### Özel yuvalar

| Yöntem                                     | Kaydettiği şey                        |
| ------------------------------------------ | ------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Bağlam motoru (aynı anda bir etkin)   |
| `api.registerMemoryPromptSection(builder)` | Bellek prompt bölümü oluşturucusu     |
| `api.registerMemoryFlushPlan(resolver)`    | Bellek temizleme planı çözücüsü       |
| `api.registerMemoryRuntime(runtime)`       | Bellek çalışma zamanı bağdaştırıcısı  |

### Bellek gömme bağdaştırıcıları

| Yöntem                                         | Kaydettiği şey                                  |
| ---------------------------------------------- | ----------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Etkin eklenti için bellek gömme bağdaştırıcısı |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` ve
  `registerMemoryRuntime`, bellek eklentilerine özeldir.
- `registerMemoryEmbeddingProvider`, etkin bellek eklentisinin bir
  veya daha fazla gömme bağdaştırıcısı kimliği kaydetmesine izin verir (örneğin `openai`, `gemini` veya
  eklenti tanımlı özel bir kimlik).
- `agents.defaults.memorySearch.provider` ve
  `agents.defaults.memorySearch.fallback` gibi kullanıcı yapılandırmaları,
  kaydedilmiş bu bağdaştırıcı kimliklerine göre çözülür.

### Olaylar ve yaşam döngüsü

| Yöntem                                       | Ne yaptığı                   |
| -------------------------------------------- | ---------------------------- |
| `api.on(hookName, handler, opts?)`           | Türlendirilmiş yaşam döngüsü kancası |
| `api.onConversationBindingResolved(handler)` | Konuşma bağlama geri çağırımı |

### Kanca karar anlambilimi

- `before_tool_call`: `{ block: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında daha düşük öncelikli işleyiciler atlanır.
- `before_tool_call`: `{ block: false }` döndürmek karar verilmemiş sayılır (`block` değerini hiç vermemekle aynıdır), geçersiz kılma sayılmaz.
- `before_install`: `{ block: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında daha düşük öncelikli işleyiciler atlanır.
- `before_install`: `{ block: false }` döndürmek karar verilmemiş sayılır (`block` değerini hiç vermemekle aynıdır), geçersiz kılma sayılmaz.
- `reply_dispatch`: `{ handled: true, ... }` döndürmek sonlandırıcıdır. Herhangi bir işleyici dağıtımı üstlendiğinde daha düşük öncelikli işleyiciler ve varsayılan model dağıtım yolu atlanır.
- `message_sending`: `{ cancel: true }` döndürmek sonlandırıcıdır. Herhangi bir işleyici bunu ayarladığında daha düşük öncelikli işleyiciler atlanır.
- `message_sending`: `{ cancel: false }` döndürmek karar verilmemiş sayılır (`cancel` değerini hiç vermemekle aynıdır), geçersiz kılma sayılmaz.

### API nesnesi alanları

| Alan                    | Tür                       | Açıklama                                                                                       |
| ----------------------- | ------------------------- | ---------------------------------------------------------------------------------------------- |
| `api.id`                | `string`                  | Eklenti kimliği                                                                                 |
| `api.name`              | `string`                  | Görünen ad                                                                                      |
| `api.version`           | `string?`                 | Eklenti sürümü (isteğe bağlı)                                                                  |
| `api.description`       | `string?`                 | Eklenti açıklaması (isteğe bağlı)                                                              |
| `api.source`            | `string`                  | Eklenti kaynak yolu                                                                            |
| `api.rootDir`           | `string?`                 | Eklenti kök dizini (isteğe bağlı)                                                              |
| `api.config`            | `OpenClawConfig`          | Geçerli yapılandırma anlık görüntüsü (varsa etkin bellek içi çalışma zamanı anlık görüntüsü)  |
| `api.pluginConfig`      | `Record<string, unknown>` | `plugins.entries.<id>.config` içinden eklentiye özgü yapılandırma                              |
| `api.runtime`           | `PluginRuntime`           | [Çalışma zamanı yardımcıları](/tr/plugins/sdk-runtime)                                            |
| `api.logger`            | `PluginLogger`            | Kapsamlı günlükleyici (`debug`, `info`, `warn`, `error`)                                       |
| `api.registrationMode`  | `PluginRegistrationMode`  | Geçerli yükleme kipi; `"setup-runtime"` hafif, tam giriş öncesi başlangıç/kurulum penceresidir |
| `api.resolvePath(input)` | `(string) => string`     | Yolu eklenti köküne göre çözümle                                                               |

## Dahili modül kuralı

Eklentiniz içinde dahili içe aktarımlar için yerel barrel dosyaları kullanın:

```
my-plugin/
  api.ts            # Harici tüketiciler için genel dışa aktarımlar
  runtime-api.ts    # Yalnızca dahili çalışma zamanı dışa aktarımları
  index.ts          # Eklenti giriş noktası
  setup-entry.ts    # Yalnızca kurulum için hafif giriş (isteğe bağlı)
```

<Warning>
  Kendi eklentinizi üretim kodunda asla `openclaw/plugin-sdk/<your-plugin>`
  üzerinden içe aktarmayın. Dahili içe aktarımları `./api.ts` veya
  `./runtime-api.ts` üzerinden yönlendirin. SDK yolu yalnızca harici sözleşmedir.
</Warning>

Cephe üzerinden yüklenen paketlenmiş eklenti genel yüzeyleri (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` ve benzeri genel giriş dosyaları), OpenClaw zaten çalışıyorsa artık
etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder. Henüz çalışma zamanı anlık görüntüsü yoksa,
diskteki çözülmüş yapılandırma dosyasına geri dönerler.

Sağlayıcı eklentileri ayrıca, bir yardımcı kasıtlı olarak sağlayıcıya özgüyse ve henüz
genel bir SDK alt yoluna ait değilse dar bir eklenti yerel sözleşme barrel'i de sunabilir.
Mevcut paketlenmiş örnek: Anthropic sağlayıcısı, Anthropic beta-header ve `service_tier` mantığını genel bir
`plugin-sdk/*` sözleşmesine yükseltmek yerine Claude akış yardımcılarını kendi genel
`api.ts` / `contract-api.ts` yüzeyinde tutar.

Diğer mevcut paketlenmiş örnekler:

- `@openclaw/openai-provider`: `api.ts`, sağlayıcı oluşturucuları,
  varsayılan model yardımcıları ve gerçek zamanlı sağlayıcı oluşturucuları dışa aktarır
- `@openclaw/openrouter-provider`: `api.ts`, sağlayıcı oluşturucusuna ek olarak
  başlangıç/yapılandırma yardımcılarını dışa aktarır

<Warning>
  Uzantı üretim kodu ayrıca `openclaw/plugin-sdk/<other-plugin>`
  içe aktarımlarından da kaçınmalıdır. Bir yardımcı gerçekten paylaşılıyorsa, iki eklentiyi birbirine bağlamak yerine
  bunu `openclaw/plugin-sdk/speech`, `.../provider-model-shared` veya başka
  bir yetenek odaklı yüzey gibi tarafsız bir SDK alt yoluna yükseltin.
</Warning>

## İlgili

- [Giriş Noktaları](/tr/plugins/sdk-entrypoints) — `definePluginEntry` ve `defineChannelPluginEntry` seçenekleri
- [Çalışma Zamanı Yardımcıları](/tr/plugins/sdk-runtime) — tam `api.runtime` ad alanı başvurusu
- [Kurulum ve Yapılandırma](/tr/plugins/sdk-setup) — paketleme, manifestler, yapılandırma şemaları
- [Test](/tr/plugins/sdk-testing) — test yardımcıları ve lint kuralları
- [SDK Geçişi](/tr/plugins/sdk-migration) — kullanımdan kaldırılmış yüzeylerden geçiş
- [Plugin İç Yapısı](/tr/plugins/architecture) — derin mimari ve yetenek modeli
