---
read_when:
    - Hangi SDK alt yolundan içe aktarma yapılacağını bilmeniz gerekiyor
    - OpenClawPluginApi üzerindeki tüm kayıt yöntemleri için bir başvuru istiyorsunuz
    - Belirli bir SDK dışa aktarımını arıyorsunuz
sidebarTitle: SDK Overview
summary: İçe aktarma eşlemi, kayıt API başvurusu ve SDK mimarisi
title: Plugin SDK Genel Bakış
x-i18n:
    generated_at: "2026-04-06T08:51:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: acd2887ef52c66b2f234858d812bb04197ecd0bfb3e4f7bf3622f8fdc765acad
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Plugin SDK Genel Bakış

Plugin SDK, plugin'ler ile çekirdek arasındaki türlendirilmiş sözleşmedir. Bu sayfa,
**neyi içe aktaracağınız** ve **neyi kaydedebileceğiniz** için başvurudur.

<Tip>
  **Nasıl yapılır kılavuzu mu arıyorsunuz?**
  - İlk plugin mi? [Başlangıç](/tr/plugins/building-plugins) ile başlayın
  - Kanal plugin'i mi? [Channel Plugins](/tr/plugins/sdk-channel-plugins) sayfasına bakın
  - Sağlayıcı plugin'i mi? [Provider Plugins](/tr/plugins/sdk-provider-plugins) sayfasına bakın
</Tip>

## İçe aktarma kuralı

Her zaman belirli bir alt yoldan içe aktarın:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Her alt yol küçük, kendi içinde tamamlanmış bir modüldür. Bu, başlatmayı hızlı tutar
ve dairesel bağımlılık sorunlarını önler. Kanala özel giriş/oluşturma yardımcıları için,
`openclaw/plugin-sdk/channel-core` yolunu tercih edin; daha geniş şemsiye yüzey ve
`buildChannelConfigSchema` gibi paylaşılan yardımcılar için
`openclaw/plugin-sdk/core` yolunu kullanın.

`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp` gibi
sağlayıcı adlı kolaylık yüzeyleri veya kanal markalı yardımcı yüzeyler
eklemeyin ya da bunlara bağımlı olmayın. Paketlenmiş plugin'ler,
genel SDK alt yollarını kendi `api.ts` veya `runtime-api.ts` varil dosyaları içinde
birleştirmelidir; çekirdek ise ya bu plugin-yerel varil dosyalarını kullanmalı ya da
ihtiyaç gerçekten kanallar arasıysa dar bir genel SDK sözleşmesi eklemelidir.

Oluşturulan dışa aktarma eşlemi hâlâ
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi
küçük bir paketlenmiş plugin yardımcı yüzeyi kümesi içerir. Bu
alt yollar yalnızca paketlenmiş plugin bakımı ve uyumluluğu için vardır;
aşağıdaki ortak tabloda bilinçli olarak yer verilmezler ve yeni üçüncü taraf
plugin'ler için önerilen içe aktarma yolu değildirler.

## Alt yol başvurusu

Amaca göre gruplanmış, en yaygın kullanılan alt yollar. 200'den fazla
alt yolun oluşturulmuş tam listesi `scripts/lib/plugin-sdk-entrypoints.json`
dosyasında bulunur.

Ayrılmış paketlenmiş-plugin yardımcı alt yolları bu oluşturulmuş listede hâlâ görünür.
Bir doküman sayfası bunlardan birini açıkça herkese açık olarak öne çıkarmadıkça,
bunları uygulama ayrıntısı/uyumluluk yüzeyleri olarak değerlendirin.

### Plugin girişi

| Alt yol                     | Ana dışa aktarımlar                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Kanal alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Kök `openclaw.json` Zod şema dışa aktarımı (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları, izin listesi istemleri, kurulum durumu oluşturucuları |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Çoklu hesap yapılandırma/eylem-geçidi yardımcıları, varsayılan hesap geri dönüş yardımcıları |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme yardımcıları |
    | `plugin-sdk/account-resolution` | Hesap arama + varsayılan geri dönüş yardımcıları |
    | `plugin-sdk/account-helpers` | Dar hesap listesi/hesap eylemi yardımcıları |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Kanal yapılandırma şeması türleri |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş sözleşme geri dönüşüyle Telegram özel komut normalleştirme/doğrulama yardımcıları |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Paylaşılan gelen yönlendirme + zarf oluşturucu yardımcıları |
    | `plugin-sdk/inbound-reply-dispatch` | Paylaşılan gelen kayıt ve dağıtım yardımcıları |
    | `plugin-sdk/messaging-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/outbound-media` | Paylaşılan giden medya yükleme yardımcıları |
    | `plugin-sdk/outbound-runtime` | Giden kimlik/gönderim temsilci yardımcıları |
    | `plugin-sdk/thread-bindings-runtime` | İş parçacığı bağlama yaşam döngüsü ve bağdaştırıcı yardımcıları |
    | `plugin-sdk/agent-media-payload` | Eski aracı medya yükü oluşturucusu |
    | `plugin-sdk/conversation-runtime` | Konuşma/iş parçacığı bağlama, eşleştirme ve yapılandırılmış bağlama yardımcıları |
    | `plugin-sdk/runtime-config-snapshot` | Çalışma zamanı yapılandırma anlık görüntü yardımcısı |
    | `plugin-sdk/runtime-group-policy` | Çalışma zamanı grup ilkesi çözümleme yardımcıları |
    | `plugin-sdk/channel-status` | Paylaşılan kanal durum anlık görüntüsü/özet yardımcıları |
    | `plugin-sdk/channel-config-primitives` | Dar kanal yapılandırma şeması ilkel öğeleri |
    | `plugin-sdk/channel-config-writes` | Kanal yapılandırma yazma yetkilendirme yardımcıları |
    | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal plugin başlangıç dışa aktarımları |
    | `plugin-sdk/allowlist-config-edit` | İzin listesi yapılandırma düzenleme/okuma yardımcıları |
    | `plugin-sdk/group-access` | Paylaşılan grup erişim kararı yardımcıları |
    | `plugin-sdk/direct-dm` | Paylaşılan doğrudan DM kimlik doğrulama/koruma yardımcıları |
    | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yükü normalleştirme/indirgeme yardımcıları |
    | `plugin-sdk/channel-inbound` | Debounce, mention eşleştirme, zarf yardımcıları |
    | `plugin-sdk/channel-send-result` | Yanıt sonuç türleri |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Hedef ayrıştırma/eşleştirme yardımcıları |
    | `plugin-sdk/channel-contract` | Kanal sözleşme türleri |
    | `plugin-sdk/channel-feedback` | Geri bildirim/reaksiyon kablolaması |
  </Accordion>

  <Accordion title="Sağlayıcı alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Düzenlenmiş yerel/kendi kendine barındırılan sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/self-hosted-provider-setup` | Odaklanmış OpenAI uyumlu kendi kendine barındırılan sağlayıcı kurulum yardımcıları |
    | `plugin-sdk/provider-auth-runtime` | Sağlayıcı plugin'leri için çalışma zamanı API anahtarı çözümleme yardımcıları |
    | `plugin-sdk/provider-auth-api-key` | API anahtarı ilk kurulum/profil yazma yardımcıları |
    | `plugin-sdk/provider-auth-result` | Standart OAuth kimlik doğrulama-sonucu oluşturucusu |
    | `plugin-sdk/provider-auth-login` | Sağlayıcı plugin'leri için paylaşılan etkileşimli giriş yardımcıları |
    | `plugin-sdk/provider-env-vars` | Sağlayıcı kimlik doğrulama env var arama yardımcıları |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve `normalizeNativeXaiModelId` gibi model kimliği normalleştirme yardımcıları |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Genel sağlayıcı HTTP/uç nokta yetenek yardımcıları |
    | `plugin-sdk/provider-web-fetch` | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
    | `plugin-sdk/provider-web-search` | Web-search sağlayıcı kayıt/önbellek/yapılandırma yardımcıları |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizleme + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` ve benzerleri |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
    | `plugin-sdk/provider-onboard` | İlk katılım yapılandırma yama yardımcıları |
    | `plugin-sdk/global-singleton` | İşlem-yerel singleton/map/önbellek yardımcıları |
  </Accordion>

  <Accordion title="Kimlik doğrulama ve güvenlik alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, komut kayıt defteri yardımcıları, gönderen yetkilendirme yardımcıları |
    | `plugin-sdk/approval-auth-runtime` | Onaylayıcı çözümleme ve aynı sohbet eylem kimlik doğrulama yardımcıları |
    | `plugin-sdk/approval-client-runtime` | Yerel exec onay profili/filtre yardımcıları |
    | `plugin-sdk/approval-delivery-runtime` | Yerel onay yeteneği/teslim bağdaştırıcıları |
    | `plugin-sdk/approval-native-runtime` | Yerel onay hedefi + hesap bağlama yardımcıları |
    | `plugin-sdk/approval-reply-runtime` | Exec/plugin onay yanıt yükü yardımcıları |
    | `plugin-sdk/command-auth-native` | Yerel komut kimlik doğrulama + yerel oturum hedefi yardımcıları |
    | `plugin-sdk/command-detection` | Paylaşılan komut algılama yardımcıları |
    | `plugin-sdk/command-surface` | Komut gövdesi normalleştirme ve komut yüzeyi yardımcıları |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/security-runtime` | Paylaşılan güven, DM geçitleme, dış içerik ve gizli bilgi toplama yardımcıları |
    | `plugin-sdk/ssrf-policy` | Ana makine izin listesi ve özel ağ SSRF ilkesi yardımcıları |
    | `plugin-sdk/ssrf-runtime` | Sabitlenmiş-dispatcher, SSRF korumalı fetch ve SSRF ilkesi yardımcıları |
    | `plugin-sdk/secret-input` | Gizli bilgi girdi ayrıştırma yardımcıları |
    | `plugin-sdk/webhook-ingress` | Webhook istek/hedef yardımcıları |
    | `plugin-sdk/webhook-request-guards` | İstek gövdesi boyutu/zaman aşımı yardımcıları |
  </Accordion>

  <Accordion title="Çalışma zamanı ve depolama alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/runtime` | Geniş çalışma zamanı/günlükleme/yedekleme/plugin kurulum yardımcıları |
    | `plugin-sdk/runtime-env` | Dar çalışma zamanı env, logger, zaman aşımı, yeniden deneme ve backoff yardımcıları |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Paylaşılan plugin komutu/hook/http/etkileşimli yardımcıları |
    | `plugin-sdk/hook-runtime` | Paylaşılan webhook/dahili hook işlem hattı yardımcıları |
    | `plugin-sdk/lazy-runtime` | `createLazyRuntimeModule`, `createLazyRuntimeMethod` ve `createLazyRuntimeSurface` gibi tembel çalışma zamanı içe aktarma/bağlama yardımcıları |
    | `plugin-sdk/process-runtime` | Süreç exec yardımcıları |
    | `plugin-sdk/cli-runtime` | CLI biçimlendirme, bekleme ve sürüm yardımcıları |
    | `plugin-sdk/gateway-runtime` | Gateway istemcisi ve kanal durumu yama yardımcıları |
    | `plugin-sdk/config-runtime` | Yapılandırma yükleme/yazma yardımcıları |
    | `plugin-sdk/telegram-command-config` | Paketlenmiş Telegram sözleşme yüzeyi kullanılamadığında bile Telegram komut adı/açıklaması normalleştirme ve yinelenen/çakışma denetimleri |
    | `plugin-sdk/approval-runtime` | Exec/plugin onay yardımcıları, onay yeteneği oluşturucuları, kimlik doğrulama/profil yardımcıları, yerel yönlendirme/çalışma zamanı yardımcıları |
    | `plugin-sdk/reply-runtime` | Paylaşılan gelen/yanıt çalışma zamanı yardımcıları, parçalama, dağıtım, heartbeat, yanıt planlayıcı |
    | `plugin-sdk/reply-dispatch-runtime` | Dar yanıt dağıtımı/sonlandırma yardımcıları |
    | `plugin-sdk/reply-history` | `buildHistoryContext`, `recordPendingHistoryEntry` ve `clearHistoryEntriesIfEnabled` gibi paylaşılan kısa pencere yanıt geçmişi yardımcıları |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Dar metin/markdown parçalama yardımcıları |
    | `plugin-sdk/session-store-runtime` | Oturum deposu yolu + updated-at yardımcıları |
    | `plugin-sdk/state-paths` | Durum/OAuth dizin yolu yardımcıları |
    | `plugin-sdk/routing` | `resolveAgentRoute`, `buildAgentSessionKey` ve `resolveDefaultAgentBoundAccountId` gibi rota/oturum anahtarı/hesap bağlama yardımcıları |
    | `plugin-sdk/status-helpers` | Paylaşılan kanal/hesap durum özeti yardımcıları, çalışma zamanı durumu varsayılanları ve sorun meta verisi yardımcıları |
    | `plugin-sdk/target-resolver-runtime` | Paylaşılan hedef çözümleyici yardımcıları |
    | `plugin-sdk/string-normalization-runtime` | Slug/dize normalleştirme yardımcıları |
    | `plugin-sdk/request-url` | Fetch/istek benzeri girdilerden dize URL'leri çıkarma |
    | `plugin-sdk/run-command` | Normalize edilmiş stdout/stderr sonuçlarıyla zamanlanmış komut çalıştırıcısı |
    | `plugin-sdk/param-readers` | Ortak araç/CLI parametre okuyucuları |
    | `plugin-sdk/tool-send` | Araç argümanlarından standart gönderim hedefi alanlarını çıkarma |
    | `plugin-sdk/temp-path` | Paylaşılan geçici indirme yolu yardımcıları |
    | `plugin-sdk/logging-core` | Alt sistem logger ve redaksiyon yardımcıları |
    | `plugin-sdk/markdown-table-runtime` | Markdown tablo modu yardımcıları |
    | `plugin-sdk/json-store` | Küçük JSON durum okuma/yazma yardımcıları |
    | `plugin-sdk/file-lock` | Yeniden girişli dosya kilidi yardımcıları |
    | `plugin-sdk/persistent-dedupe` | Disk destekli dedupe önbellek yardımcıları |
    | `plugin-sdk/acp-runtime` | ACP çalışma zamanı/oturum ve yanıt dağıtımı yardımcıları |
    | `plugin-sdk/agent-config-primitives` | Dar aracı çalışma zamanı yapılandırma şeması ilkel öğeleri |
    | `plugin-sdk/boolean-param` | Esnek boolean parametre okuyucusu |
    | `plugin-sdk/dangerous-name-runtime` | Tehlikeli ad eşleştirme çözümleme yardımcıları |
    | `plugin-sdk/device-bootstrap` | Cihaz önyükleme ve eşleştirme belirteci yardımcıları |
    | `plugin-sdk/extension-shared` | Paylaşılan pasif kanal ve durum yardımcısı ilkel öğeleri |
    | `plugin-sdk/models-provider-runtime` | `/models` komutu/sağlayıcı yanıt yardımcıları |
    | `plugin-sdk/skill-commands-runtime` | Skills komut listeleme yardımcıları |
    | `plugin-sdk/native-command-registry` | Yerel komut kayıt defteri/oluşturma/serileştirme yardımcıları |
    | `plugin-sdk/provider-zai-endpoint` | Z.A.I uç nokta algılama yardımcıları |
    | `plugin-sdk/infra-runtime` | Sistem olayı/heartbeat yardımcıları |
    | `plugin-sdk/collection-runtime` | Küçük sınırlı önbellek yardımcıları |
    | `plugin-sdk/diagnostic-runtime` | Tanılama bayrağı ve olay yardımcıları |
    | `plugin-sdk/error-runtime` | Hata grafiği, biçimlendirme, paylaşılan hata sınıflandırma yardımcıları, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Sarmalanmış fetch, proxy ve sabitlenmiş arama yardımcıları |
    | `plugin-sdk/host-runtime` | Ana makine adı ve SCP ana makinesi normalleştirme yardımcıları |
    | `plugin-sdk/retry-runtime` | Yeniden deneme yapılandırması ve yeniden deneme çalıştırıcı yardımcıları |
    | `plugin-sdk/agent-runtime` | Aracı dizini/kimliği/çalışma alanı yardımcıları |
    | `plugin-sdk/directory-runtime` | Yapılandırma destekli dizin sorgusu/dedupe |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Yetenek ve test alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Medya yükü oluşturucularına ek olarak paylaşılan medya fetch/dönüştürme/depolama yardımcıları |
    | `plugin-sdk/media-generation-runtime` | Paylaşılan medya oluşturma failover yardımcıları, aday seçimi ve eksik model mesajlaşması |
    | `plugin-sdk/media-understanding` | Medya anlama sağlayıcı türleri ve sağlayıcı taraflı görsel/ses yardımcı dışa aktarımları |
    | `plugin-sdk/text-runtime` | Asistan tarafından görülebilen metin ayıklama, markdown işleme/parçalama/tablo yardımcıları, redaksiyon yardımcıları, direktif etiketi yardımcıları ve güvenli metin yardımcıları gibi paylaşılan metin/markdown/günlükleme yardımcıları |
    | `plugin-sdk/text-chunking` | Giden metin parçalama yardımcısı |
    | `plugin-sdk/speech` | Konuşma sağlayıcı türleri ve sağlayıcı taraflı direktif, kayıt defteri ve doğrulama yardımcıları |
    | `plugin-sdk/speech-core` | Paylaşılan konuşma sağlayıcı türleri, kayıt defteri, direktif ve normalleştirme yardımcıları |
    | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon sağlayıcı türleri ve kayıt defteri yardımcıları |
    | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses sağlayıcı türleri ve kayıt defteri yardımcıları |
    | `plugin-sdk/image-generation` | Görsel oluşturma sağlayıcı türleri |
    | `plugin-sdk/image-generation-core` | Paylaşılan görsel oluşturma türleri, failover, kimlik doğrulama ve kayıt defteri yardımcıları |
    | `plugin-sdk/music-generation` | Müzik oluşturma sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/music-generation-core` | Paylaşılan müzik oluşturma türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/video-generation` | Video oluşturma sağlayıcı/istek/sonuç türleri |
    | `plugin-sdk/video-generation-core` | Paylaşılan video oluşturma türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
    | `plugin-sdk/webhook-targets` | Webhook hedef kayıt defteri ve rota kurulum yardımcıları |
    | `plugin-sdk/webhook-path` | Webhook yol normalleştirme yardımcıları |
    | `plugin-sdk/web-media` | Paylaşılan uzak/yerel medya yükleme yardımcıları |
    | `plugin-sdk/zod` | Plugin SDK tüketicileri için yeniden dışa aktarılan `zod` |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Bellek alt yolları">
    | Alt yol | Ana dışa aktarımlar |
    | --- | --- |
    | `plugin-sdk/memory-core` | Yönetici/yapılandırma/dosya/CLI yardımcıları için paketlenmiş memory-core yardımcı yüzeyi |
    | `plugin-sdk/memory-core-engine-runtime` | Bellek dizini/arama çalışma zamanı cephesi |
    | `plugin-sdk/memory-core-host-engine-foundation` | Bellek ana makine foundation engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek ana makine embedding engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-qmd` | Bellek ana makine QMD engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-engine-storage` | Bellek ana makine storage engine dışa aktarımları |
    | `plugin-sdk/memory-core-host-multimodal` | Bellek ana makine multimodal yardımcıları |
    | `plugin-sdk/memory-core-host-query` | Bellek ana makine sorgu yardımcıları |
    | `plugin-sdk/memory-core-host-secret` | Bellek ana makine gizli bilgi yardımcıları |
    | `plugin-sdk/memory-core-host-events` | Bellek ana makine olay günlüğü yardımcıları |
    | `plugin-sdk/memory-core-host-status` | Bellek ana makine durum yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-cli` | Bellek ana makine CLI çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-core` | Bellek ana makine çekirdek çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-core-host-runtime-files` | Bellek ana makine dosya/çalışma zamanı yardımcıları |
    | `plugin-sdk/memory-host-core` | Bellek ana makine çekirdek çalışma zamanı yardımcıları için üreticiden bağımsız takma ad |
    | `plugin-sdk/memory-host-events` | Bellek ana makine olay günlüğü yardımcıları için üreticiden bağımsız takma ad |
    | `plugin-sdk/memory-host-files` | Bellek ana makine dosya/çalışma zamanı yardımcıları için üreticiden bağımsız takma ad |
    | `plugin-sdk/memory-host-markdown` | Belleğe bitişik plugin'ler için paylaşılan yönetilen-markdown yardımcıları |
    | `plugin-sdk/memory-host-search` | Arama yöneticisi erişimi için etkin bellek çalışma zamanı cephesi |
    | `plugin-sdk/memory-host-status` | Bellek ana makine durum yardımcıları için üreticiden bağımsız takma ad |
    | `plugin-sdk/memory-lancedb` | Paketlenmiş memory-lancedb yardımcı yüzeyi |
  </Accordion>

  <Accordion title="Ayrılmış paketlenmiş-yardımcı alt yollar">
    | Aile | Geçerli alt yollar | Amaçlanan kullanım |
    | --- | --- | --- |
    | Tarayıcı | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Paketlenmiş tarayıcı plugin desteği yardımcıları (`browser-support` uyumluluk varili olarak kalır) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Paketlenmiş Matrix yardımcı/çalışma zamanı yüzeyi |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Paketlenmiş LINE yardımcı/çalışma zamanı yüzeyi |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Paketlenmiş IRC yardımcı yüzeyi |
    | Kanala özgü yardımcılar | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Paketlenmiş kanal uyumluluk/yardımcı yüzeyleri |
    | Kimlik doğrulama/plugin'e özgü yardımcılar | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Paketlenmiş özellik/plugin yardımcı yüzeyleri; `plugin-sdk/github-copilot-token` şu anda `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` dışa aktarır |
  </Accordion>
</AccordionGroup>

## Kayıt API'si

`register(api)` geri çağrısı, şu yöntemlere sahip bir `OpenClawPluginApi`
nesnesi alır:

### Yetenek kaydı

| Yöntem                                           | Kaydettiği şey                  |
| ------------------------------------------------ | ------------------------------- |
| `api.registerProvider(...)`                      | Metin çıkarımı (LLM)            |
| `api.registerChannel(...)`                       | Mesajlaşma kanalı               |
| `api.registerSpeechProvider(...)`                | Metinden konuşmaya / STT sentezi |
| `api.registerRealtimeTranscriptionProvider(...)` | Akışlı gerçek zamanlı transkripsiyon |
| `api.registerRealtimeVoiceProvider(...)`         | Çift yönlü gerçek zamanlı ses oturumları |
| `api.registerMediaUnderstandingProvider(...)`    | Görsel/ses/video analizi        |
| `api.registerImageGenerationProvider(...)`       | Görsel oluşturma                |
| `api.registerMusicGenerationProvider(...)`       | Müzik oluşturma                 |
| `api.registerVideoGenerationProvider(...)`       | Video oluşturma                 |
| `api.registerWebFetchProvider(...)`              | Web fetch / scrape sağlayıcısı  |
| `api.registerWebSearchProvider(...)`             | Web arama                       |

### Araçlar ve komutlar

| Yöntem                          | Kaydettiği şey                                 |
| ------------------------------- | ---------------------------------------------- |
| `api.registerTool(tool, opts?)` | Aracı aracı (zorunlu veya `{ optional: true }`) |
| `api.registerCommand(def)`      | Özel komut (LLM'yi atlar)                      |

### Altyapı

| Yöntem                                         | Kaydettiği şey                      |
| ---------------------------------------------- | ----------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Olay hook'u                         |
| `api.registerHttpRoute(params)`                | Gateway HTTP uç noktası             |
| `api.registerGatewayMethod(name, handler)`     | Gateway RPC yöntemi                 |
| `api.registerCli(registrar, opts?)`            | CLI alt komutu                      |
| `api.registerService(service)`                 | Arka plan hizmeti                   |
| `api.registerInteractiveHandler(registration)` | Etkileşimli işleyici                |
| `api.registerMemoryPromptSupplement(builder)`  | Eklemeli belleğe bitişik istem bölümü |
| `api.registerMemoryCorpusSupplement(adapter)`  | Eklemeli bellek arama/okuma derlemi |

Ayrılmış çekirdek yönetici ad alanları (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`), bir plugin daha dar bir gateway yöntem kapsamı atamaya çalışsa bile
her zaman `operator.admin` olarak kalır. Plugin sahipli yöntemler için
plugin'e özgü önekleri tercih edin.

### CLI kayıt meta verileri

`api.registerCli(registrar, opts?)`, iki tür üst düzey meta veri kabul eder:

- `commands`: kayıt görevlisinin sahip olduğu açık komut kökleri
- `descriptors`: kök CLI yardımı,
  yönlendirme ve tembel plugin CLI kaydı için ayrıştırma zamanlı komut tanımlayıcıları

Bir plugin komutunun normal kök CLI yolunda tembel yüklenmiş kalmasını istiyorsanız,
bu kayıt görevlisinin açtığı her üst düzey komut kökünü kapsayan `descriptors`
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
        description: "Matrix hesaplarını, doğrulamayı, cihazları ve profil durumunu yönet",
        hasSubcommands: true,
      },
    ],
  },
);
```

Yalnızca `commands` kullanımını, tembel kök CLI kaydına ihtiyaç duymadığınızda
tercih edin. Bu hevesli uyumluluk yolu desteklenmeye devam eder, ancak ayrıştırma zamanı
tembel yükleme için tanımlayıcı destekli yer tutucular kurmaz.

### Ayrıcalıklı yuvalar

| Yöntem                                     | Kaydettiği şey                    |
| ------------------------------------------ | --------------------------------- |
| `api.registerContextEngine(id, factory)`   | Bağlam motoru (aynı anda bir etkin) |
| `api.registerMemoryPromptSection(builder)` | Bellek istem bölümü oluşturucusu  |
| `api.registerMemoryFlushPlan(resolver)`    | Bellek temizleme planı çözümleyicisi |
| `api.registerMemoryRuntime(runtime)`       | Bellek çalışma zamanı bağdaştırıcısı |

### Bellek gömme bağdaştırıcıları

| Yöntem                                         | Kaydettiği şey                                 |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Etkin plugin için bellek gömme bağdaştırıcısı |

- `registerMemoryPromptSection`, `registerMemoryFlushPlan` ve
  `registerMemoryRuntime`, bellek plugin'lerine özeldir.
- `registerMemoryEmbeddingProvider`, etkin bellek plugin'inin bir
  veya daha fazla gömme bağdaştırıcısı kimliği kaydetmesini sağlar
  (örneğin `openai`, `gemini` veya plugin tarafından tanımlanan özel bir kimlik).
- `agents.defaults.memorySearch.provider` ve
  `agents.defaults.memorySearch.fallback` gibi kullanıcı yapılandırmaları
  bu kayıtlı bağdaştırıcı kimliklerine göre çözülür.

### Olaylar ve yaşam döngüsü

| Yöntem                                       | Ne yapar                      |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | Türlendirilmiş yaşam döngüsü hook'u |
| `api.onConversationBindingResolved(handler)` | Konuşma bağlama geri çağrısı  |

### Hook karar anlamları

- `before_tool_call`: `{ block: true }` döndürmek kesindir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_tool_call`: `{ block: false }` döndürmek karar yok olarak değerlendirilir (`block` alanını hiç vermemekle aynıdır), geçersiz kılma olarak değil.
- `before_install`: `{ block: true }` döndürmek kesindir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `before_install`: `{ block: false }` döndürmek karar yok olarak değerlendirilir (`block` alanını hiç vermemekle aynıdır), geçersiz kılma olarak değil.
- `reply_dispatch`: `{ handled: true, ... }` döndürmek kesindir. Herhangi bir işleyici dağıtımı üstlendiğinde, daha düşük öncelikli işleyiciler ve varsayılan model dağıtım yolu atlanır.
- `message_sending`: `{ cancel: true }` döndürmek kesindir. Herhangi bir işleyici bunu ayarladığında, daha düşük öncelikli işleyiciler atlanır.
- `message_sending`: `{ cancel: false }` döndürmek karar yok olarak değerlendirilir (`cancel` alanını hiç vermemekle aynıdır), geçersiz kılma olarak değil.

### API nesne alanları

| Alan                    | Tür                       | Açıklama                                                                                   |
| ----------------------- | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                | `string`                  | Plugin kimliği                                                                             |
| `api.name`              | `string`                  | Görünen ad                                                                                 |
| `api.version`           | `string?`                 | Plugin sürümü (isteğe bağlı)                                                               |
| `api.description`       | `string?`                 | Plugin açıklaması (isteğe bağlı)                                                           |
| `api.source`            | `string`                  | Plugin kaynak yolu                                                                         |
| `api.rootDir`           | `string?`                 | Plugin kök dizini (isteğe bağlı)                                                           |
| `api.config`            | `OpenClawConfig`          | Geçerli yapılandırma anlık görüntüsü (mevcut olduğunda etkin bellek içi çalışma zamanı anlık görüntüsü) |
| `api.pluginConfig`      | `Record<string, unknown>` | `plugins.entries.<id>.config` içindeki plugin'e özgü yapılandırma                         |
| `api.runtime`           | `PluginRuntime`           | [Çalışma zamanı yardımcıları](/tr/plugins/sdk-runtime)                                        |
| `api.logger`            | `PluginLogger`            | Kapsamlı logger (`debug`, `info`, `warn`, `error`)                                         |
| `api.registrationMode`  | `PluginRegistrationMode`  | Geçerli yükleme modu; `"setup-runtime"` tam giriş öncesi hafif başlatma/kurulum penceresidir |
| `api.resolvePath(input)` | `(string) => string`     | Yolu plugin köküne göre çözümleme                                                          |

## Dahili modül kuralı

Plugin'iniz içinde, dahili içe aktarmalar için yerel varil dosyaları kullanın:

```
my-plugin/
  api.ts            # Dış tüketiciler için herkese açık dışa aktarımlar
  runtime-api.ts    # Yalnızca dahili çalışma zamanı dışa aktarımları
  index.ts          # Plugin giriş noktası
  setup-entry.ts    # Yalnızca kurulum için hafif giriş (isteğe bağlı)
```

<Warning>
  Üretim kodunda kendi plugin'inizi `openclaw/plugin-sdk/<your-plugin>`
  üzerinden asla içe aktarmayın. Dahili içe aktarmaları `./api.ts` veya
  `./runtime-api.ts` üzerinden yönlendirin. SDK yolu yalnızca dış sözleşmedir.
</Warning>

Cephe üzerinden yüklenen paketlenmiş plugin herkese açık yüzeyleri (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` ve benzer herkese açık giriş dosyaları), OpenClaw zaten çalışıyorsa
artık etkin çalışma zamanı yapılandırma anlık görüntüsünü tercih eder. Henüz çalışma zamanı
anlık görüntüsü yoksa, diskteki çözümlenmiş yapılandırma dosyasına geri dönerler.

Sağlayıcı plugin'leri ayrıca, bir yardımcı bilinçli olarak sağlayıcıya özgüyse ve henüz
genel bir SDK alt yoluna ait değilse dar bir plugin-yerel sözleşme varili de sunabilir.
Güncel paketlenmiş örnek: Anthropic sağlayıcısı, Anthropic beta-header ve `service_tier`
mantığını genel bir `plugin-sdk/*` sözleşmesine taşımak yerine, Claude akış yardımcılarını
kendi herkese açık `api.ts` / `contract-api.ts` yüzeyinde tutar.

Diğer güncel paketlenmiş örnekler:

- `@openclaw/openai-provider`: `api.ts`, sağlayıcı oluşturucuları,
  varsayılan model yardımcılarını ve gerçek zamanlı sağlayıcı oluşturucularını dışa aktarır
- `@openclaw/openrouter-provider`: `api.ts`, sağlayıcı oluşturucusunu ve
  ilk katılım/yapılandırma yardımcılarını dışa aktarır

<Warning>
  Extension üretim kodu ayrıca `openclaw/plugin-sdk/<other-plugin>`
  içe aktarımlarından da kaçınmalıdır. Bir yardımcı gerçekten paylaşılıyorsa,
  iki plugin'i birbirine bağlamak yerine bunu `openclaw/plugin-sdk/speech`,
  `.../provider-model-shared` veya başka bir yetenek odaklı yüzey gibi
  tarafsız bir SDK alt yoluna taşıyın.
</Warning>

## İlgili

- [Giriş Noktaları](/tr/plugins/sdk-entrypoints) — `definePluginEntry` ve `defineChannelPluginEntry` seçenekleri
- [Çalışma Zamanı Yardımcıları](/tr/plugins/sdk-runtime) — tam `api.runtime` ad alanı başvurusu
- [Kurulum ve Yapılandırma](/tr/plugins/sdk-setup) — paketleme, manifestler, yapılandırma şemaları
- [Test](/tr/plugins/sdk-testing) — test yardımcıları ve lint kuralları
- [SDK Geçişi](/tr/plugins/sdk-migration) — kullanımdan kaldırılmış yüzeylerden geçiş
- [Plugin İç Yapısı](/tr/plugins/architecture) — derin mimari ve yetenek modeli
