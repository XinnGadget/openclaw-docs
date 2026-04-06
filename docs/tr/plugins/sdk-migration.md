---
read_when:
    - OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED uyarısını görüyorsunuz
    - OPENCLAW_EXTENSION_API_DEPRECATED uyarısını görüyorsunuz
    - Bir plugin'i modern plugin mimarisine güncelliyorsunuz
    - Harici bir OpenClaw plugin'ini bakımını yapıyorsunuz
sidebarTitle: Migrate to SDK
summary: Eski geriye dönük uyumluluk katmanından modern plugin SDK'ya geçiş yapın
title: Plugin SDK Geçişi
x-i18n:
    generated_at: "2026-04-06T08:50:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 94f12d1376edd8184714cc4dbea4a88fa8ed652f65e9365ede6176f3bf441b33
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Plugin SDK Geçişi

OpenClaw, geniş bir geriye dönük uyumluluk katmanından odaklı ve belgelenmiş
içe aktarmalara sahip modern bir plugin mimarisine geçti. Plugin'iniz yeni
mimari öncesinde oluşturulduysa, bu kılavuz geçiş yapmanıza yardımcı olur.

## Neler değişiyor

Eski plugin sistemi, plugin'lerin tek bir giriş noktasından ihtiyaç duydukları
her şeyi içe aktarmasına izin veren iki geniş yüzey sağlıyordu:

- **`openclaw/plugin-sdk/compat`** — onlarca yardımcıyı yeniden dışa aktaran
  tek bir içe aktarma. Yeni plugin mimarisi oluşturulurken eski hook tabanlı
  plugin'lerin çalışmaya devam etmesini sağlamak için sunuldu.
- **`openclaw/extension-api`** — plugin'lere gömülü ajan çalıştırıcısı gibi
  ana makine tarafı yardımcılarına doğrudan erişim veren bir köprü.

Bu iki yüzey artık **kullanımdan kaldırıldı**. Çalışma zamanında hâlâ
çalışırlar, ancak yeni plugin'ler bunları kullanmamalıdır ve mevcut
plugin'ler, bir sonraki büyük sürüm bunları kaldırmadan önce geçiş yapmalıdır.

<Warning>
  Geriye dönük uyumluluk katmanı gelecekteki bir büyük sürümde kaldırılacaktır.
  Hâlâ bu yüzeylerden içe aktarma yapan plugin'ler bu gerçekleştiğinde bozulur.
</Warning>

## Bu neden değişti

Eski yaklaşım sorunlara yol açıyordu:

- **Yavaş başlangıç** — tek bir yardımcıyı içe aktarmak onlarca ilgisiz modülü yüklüyordu
- **Döngüsel bağımlılıklar** — geniş yeniden dışa aktarmalar, içe aktarma döngüleri oluşturmayı kolaylaştırıyordu
- **Belirsiz API yüzeyi** — hangi dışa aktarımların kararlı, hangilerinin dahili olduğunu anlamanın bir yolu yoktu

Modern plugin SDK bunu düzeltir: her içe aktarma yolu (`openclaw/plugin-sdk/\<subpath\>`)
net bir amaca ve belgelenmiş sözleşmeye sahip küçük, kendi içinde yeterli bir modüldür.

Paket içi kanallar için eski sağlayıcı kolaylık seam'leri de artık yok. Şu tür
içe aktarmalar: `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
kanal markalı yardımcı seam'leri ve
`openclaw/plugin-sdk/telegram-core`, kararlı plugin sözleşmeleri değil, mono-repo
için özel kısayollardı. Bunun yerine dar kapsamlı genel SDK alt yollarını
kullanın. Paketli plugin çalışma alanı içinde, sağlayıcıya ait yardımcıları o
plugin'in kendi `api.ts` veya `runtime-api.ts` dosyasında tutun.

Mevcut paketli sağlayıcı örnekleri:

- Anthropic, Claude'a özgü akış yardımcılarını kendi `api.ts` /
  `contract-api.ts` seam'inde tutar
- OpenAI, sağlayıcı oluşturucularını, varsayılan model yardımcılarını ve
  gerçek zamanlı sağlayıcı oluşturucularını kendi `api.ts` dosyasında tutar
- OpenRouter, sağlayıcı oluşturucu ve onboarding/config yardımcılarını kendi
  `api.ts` dosyasında tutar

## Nasıl geçiş yapılır

<Steps>
  <Step title="Windows sarmalayıcı fallback davranışını denetleyin">
    Plugin'iniz `openclaw/plugin-sdk/windows-spawn` kullanıyorsa, çözümlenmemiş Windows
    `.cmd`/`.bat` sarmalayıcıları artık siz açıkça
    `allowShellFallback: true` geçmedikçe kapalı şekilde başarısız olur.

    ```typescript
    // Before
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // After
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Only set this for trusted compatibility callers that intentionally
      // accept shell-mediated fallback.
      allowShellFallback: true,
    });
    ```

    Çağıran tarafınız shell fallback davranışına kasıtlı olarak bağlı değilse,
    `allowShellFallback` ayarlamayın ve bunun yerine fırlatılan hatayı ele alın.

  </Step>

  <Step title="Kullanımdan kaldırılmış içe aktarmaları bulun">
    Plugin'inizde kullanımdan kaldırılmış iki yüzeyden herhangi birinden yapılan
    içe aktarmaları arayın:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Odaklı içe aktarmalarla değiştirin">
    Eski yüzeydeki her dışa aktarma, belirli bir modern içe aktarma yoluna eşlenir:

    ```typescript
    // Before (deprecated backwards-compatibility layer)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // After (modern focused imports)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Ana makine tarafı yardımcılar için doğrudan içe aktarma yapmak yerine
    enjekte edilen plugin çalışma zamanını kullanın:

    ```typescript
    // Before (deprecated extension-api bridge)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // After (injected runtime)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Aynı desen diğer eski köprü yardımcıları için de geçerlidir:

    | Eski içe aktarma | Modern eşdeğeri |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | oturum deposu yardımcıları | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Derleyin ve test edin">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## İçe aktarma yolu başvurusu

<Accordion title="Yaygın içe aktarma yolu tablosu">
  | İçe aktarma yolu | Amaç | Temel dışa aktarımlar |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Kanonik plugin giriş yardımcısı | `definePluginEntry` |
  | `plugin-sdk/core` | Kanal giriş tanımları/oluşturucuları için eski şemsiye yeniden dışa aktarma | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Kök config şema dışa aktarımı | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Tek sağlayıcılı giriş yardımcısı | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Odaklı kanal giriş tanımları ve oluşturucuları | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Paylaşılan kurulum sihirbazı yardımcıları | Allowlist istemleri, kurulum durumu oluşturucuları |
  | `plugin-sdk/setup-runtime` | Kurulum zamanı çalışma zamanı yardımcıları | İçe aktarma için güvenli kurulum yama bağdaştırıcıları, arama notu yardımcıları, `promptResolvedAllowFrom`, `splitSetupEntries`, devredilen kurulum proxy'leri |
  | `plugin-sdk/setup-adapter-runtime` | Kurulum bağdaştırıcı yardımcıları | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Kurulum araç yardımcıları | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Çoklu hesap yardımcıları | Hesap listesi/config/eylem kapısı yardımcıları |
  | `plugin-sdk/account-id` | Hesap kimliği yardımcıları | `DEFAULT_ACCOUNT_ID`, hesap kimliği normalleştirme |
  | `plugin-sdk/account-resolution` | Hesap arama yardımcıları | Hesap arama + varsayılan fallback yardımcıları |
  | `plugin-sdk/account-helpers` | Dar kapsamlı hesap yardımcıları | Hesap listesi/hesap eylemi yardımcıları |
  | `plugin-sdk/channel-setup` | Kurulum sihirbazı bağdaştırıcıları | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, ayrıca `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | DM eşleştirme temel bileşenleri | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Yanıt öneki + yazıyor durumu altyapısı | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Config bağdaştırıcı fabrikaları | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Config şeması oluşturucuları | Kanal config şeması türleri |
  | `plugin-sdk/telegram-command-config` | Telegram komut config yardımcıları | Komut adı normalleştirme, açıklama kırpma, tekrar/çakışma doğrulaması |
  | `plugin-sdk/channel-policy` | Grup/DM ilke çözümleme | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Hesap durumu takibi | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Gelen zarf yardımcıları | Paylaşılan rota + zarf oluşturucu yardımcıları |
  | `plugin-sdk/inbound-reply-dispatch` | Gelen yanıt yardımcıları | Paylaşılan kaydet ve dağıt yardımcıları |
  | `plugin-sdk/messaging-targets` | Mesajlaşma hedefi ayrıştırma | Hedef ayrıştırma/eşleştirme yardımcıları |
  | `plugin-sdk/outbound-media` | Giden medya yardımcıları | Paylaşılan giden medya yükleme |
  | `plugin-sdk/outbound-runtime` | Giden çalışma zamanı yardımcıları | Giden kimlik/gönderim delege yardımcıları |
  | `plugin-sdk/thread-bindings-runtime` | Thread-binding yardımcıları | Thread-binding yaşam döngüsü ve bağdaştırıcı yardımcıları |
  | `plugin-sdk/agent-media-payload` | Eski medya payload yardımcıları | Eski alan düzenleri için ajan medya payload oluşturucusu |
  | `plugin-sdk/channel-runtime` | Kullanımdan kaldırılmış uyumluluk shim'i | Yalnızca eski kanal çalışma zamanı yardımcıları |
  | `plugin-sdk/channel-send-result` | Gönderim sonuç türleri | Yanıt sonuç türleri |
  | `plugin-sdk/runtime-store` | Kalıcı plugin depolaması | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Geniş çalışma zamanı yardımcıları | Çalışma zamanı/günlükleme/yedekleme/plugin yükleme yardımcıları |
  | `plugin-sdk/runtime-env` | Dar kapsamlı çalışma zamanı ortam yardımcıları | Logger/çalışma zamanı ortamı, zaman aşımı, retry ve backoff yardımcıları |
  | `plugin-sdk/plugin-runtime` | Paylaşılan plugin çalışma zamanı yardımcıları | Plugin komutları/hook'lar/http/etkileşimli yardımcıları |
  | `plugin-sdk/hook-runtime` | Hook işlem hattı yardımcıları | Paylaşılan webhook/dahili hook işlem hattı yardımcıları |
  | `plugin-sdk/lazy-runtime` | Lazy çalışma zamanı yardımcıları | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Process yardımcıları | Paylaşılan exec yardımcıları |
  | `plugin-sdk/cli-runtime` | CLI çalışma zamanı yardımcıları | Komut biçimlendirme, beklemeler, sürüm yardımcıları |
  | `plugin-sdk/gateway-runtime` | Gateway yardımcıları | Gateway istemcisi ve kanal durumu yama yardımcıları |
  | `plugin-sdk/config-runtime` | Config yardımcıları | Config yükleme/yazma yardımcıları |
  | `plugin-sdk/telegram-command-config` | Telegram komut yardımcıları | Paketli Telegram sözleşme yüzeyi kullanılamadığında fallback açısından kararlı Telegram komut doğrulama yardımcıları |
  | `plugin-sdk/approval-runtime` | Onay istemi yardımcıları | Exec/plugin onay payload'u, onay yeteneği/profil yardımcıları, yerel onay yönlendirme/çalışma zamanı yardımcıları |
  | `plugin-sdk/approval-auth-runtime` | Onay kimlik doğrulama yardımcıları | Onaylayıcı çözümleme, aynı sohbet eylem kimlik doğrulaması |
  | `plugin-sdk/approval-client-runtime` | Onay istemci yardımcıları | Yerel exec onay profili/filtre yardımcıları |
  | `plugin-sdk/approval-delivery-runtime` | Onay teslim yardımcıları | Yerel onay yeteneği/teslim bağdaştırıcıları |
  | `plugin-sdk/approval-native-runtime` | Onay hedef yardımcıları | Yerel onay hedefi/hesap bağlama yardımcıları |
  | `plugin-sdk/approval-reply-runtime` | Onay yanıt yardımcıları | Exec/plugin onay yanıt payload yardımcıları |
  | `plugin-sdk/security-runtime` | Güvenlik yardımcıları | Paylaşılan güven, DM kapılama, external-content ve secret-collection yardımcıları |
  | `plugin-sdk/ssrf-policy` | SSRF ilke yardımcıları | Ana makine allowlist ve özel ağ ilkesi yardımcıları |
  | `plugin-sdk/ssrf-runtime` | SSRF çalışma zamanı yardımcıları | Pinned-dispatcher, guarded fetch, SSRF ilke yardımcıları |
  | `plugin-sdk/collection-runtime` | Sınırlı önbellek yardımcıları | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Tanılama kapılama yardımcıları | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Hata biçimlendirme yardımcıları | `formatUncaughtError`, `isApprovalNotFoundError`, hata grafiği yardımcıları |
  | `plugin-sdk/fetch-runtime` | Sarmalanmış fetch/proxy yardımcıları | `resolveFetch`, proxy yardımcıları |
  | `plugin-sdk/host-runtime` | Ana makine normalleştirme yardımcıları | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Retry yardımcıları | `RetryConfig`, `retryAsync`, ilke çalıştırıcıları |
  | `plugin-sdk/allow-from` | Allowlist biçimlendirme | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Allowlist girdi eşleme | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Komut kapılama ve komut yüzeyi yardımcıları | `resolveControlCommandGate`, gönderici yetkilendirme yardımcıları, komut kayıt yardımcıları |
  | `plugin-sdk/secret-input` | Secret girdi ayrıştırma | Secret girdi yardımcıları |
  | `plugin-sdk/webhook-ingress` | Webhook istek yardımcıları | Webhook hedef yardımcıları |
  | `plugin-sdk/webhook-request-guards` | Webhook gövde koruma yardımcıları | İstek gövdesi okuma/sınır yardımcıları |
  | `plugin-sdk/reply-runtime` | Paylaşılan yanıt çalışma zamanı | Gelen dağıtım, heartbeat, yanıt planlayıcı, parçalama |
  | `plugin-sdk/reply-dispatch-runtime` | Dar kapsamlı yanıt dağıtım yardımcıları | Sonlandırma + sağlayıcı dağıtım yardımcıları |
  | `plugin-sdk/reply-history` | Yanıt geçmişi yardımcıları | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Yanıt referansı planlama | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Yanıt parçalayıcı yardımcıları | Metin/markdown parçalama yardımcıları |
  | `plugin-sdk/session-store-runtime` | Oturum deposu yardımcıları | Depo yolu + updated-at yardımcıları |
  | `plugin-sdk/state-paths` | Durum yolu yardımcıları | Durum ve OAuth dizini yardımcıları |
  | `plugin-sdk/routing` | Yönlendirme/oturum anahtarı yardımcıları | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, oturum anahtarı normalleştirme yardımcıları |
  | `plugin-sdk/status-helpers` | Kanal durumu yardımcıları | Kanal/hesap durum özeti oluşturucuları, çalışma zamanı durum varsayılanları, issue metadata yardımcıları |
  | `plugin-sdk/target-resolver-runtime` | Hedef çözücü yardımcıları | Paylaşılan hedef çözücü yardımcıları |
  | `plugin-sdk/string-normalization-runtime` | Dizge normalleştirme yardımcıları | Slug/dizge normalleştirme yardımcıları |
  | `plugin-sdk/request-url` | İstek URL yardımcıları | İstek benzeri girdilerden dizge URL çıkarma |
  | `plugin-sdk/run-command` | Zamanlı komut yardımcıları | Normalleştirilmiş stdout/stderr ile zamanlı komut çalıştırıcısı |
  | `plugin-sdk/param-readers` | Param okuyucular | Yaygın araç/CLI param okuyucuları |
  | `plugin-sdk/tool-send` | Araç gönderim çıkarımı | Araç argümanlarından kanonik gönderim hedef alanlarını çıkarma |
  | `plugin-sdk/temp-path` | Geçici yol yardımcıları | Paylaşılan geçici indirme yolu yardımcıları |
  | `plugin-sdk/logging-core` | Günlükleme yardımcıları | Alt sistem logger ve redaction yardımcıları |
  | `plugin-sdk/markdown-table-runtime` | Markdown tablo yardımcıları | Markdown tablo modu yardımcıları |
  | `plugin-sdk/reply-payload` | Mesaj yanıt türleri | Yanıt payload türleri |
  | `plugin-sdk/provider-setup` | Düzenlenmiş local/self-hosted sağlayıcı kurulum yardımcıları | Self-hosted sağlayıcı keşfi/config yardımcıları |
  | `plugin-sdk/self-hosted-provider-setup` | Odaklı OpenAI uyumlu self-hosted sağlayıcı kurulum yardımcıları | Aynı self-hosted sağlayıcı keşfi/config yardımcıları |
  | `plugin-sdk/provider-auth-runtime` | Sağlayıcı çalışma zamanı kimlik doğrulama yardımcıları | Çalışma zamanı API anahtarı çözümleme yardımcıları |
  | `plugin-sdk/provider-auth-api-key` | Sağlayıcı API anahtarı kurulum yardımcıları | API anahtarı onboarding/profil yazma yardımcıları |
  | `plugin-sdk/provider-auth-result` | Sağlayıcı auth-result yardımcıları | Standart OAuth auth-result oluşturucusu |
  | `plugin-sdk/provider-auth-login` | Sağlayıcı etkileşimli giriş yardımcıları | Paylaşılan etkileşimli giriş yardımcıları |
  | `plugin-sdk/provider-env-vars` | Sağlayıcı env var yardımcıları | Sağlayıcı kimlik doğrulama env var arama yardımcıları |
  | `plugin-sdk/provider-model-shared` | Paylaşılan sağlayıcı model/yeniden oynatma yardımcıları | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, paylaşılan replay-policy oluşturucuları, sağlayıcı uç nokta yardımcıları ve model kimliği normalleştirme yardımcıları |
  | `plugin-sdk/provider-catalog-shared` | Paylaşılan sağlayıcı katalog yardımcıları | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Sağlayıcı onboarding yamaları | Onboarding config yardımcıları |
  | `plugin-sdk/provider-http` | Sağlayıcı HTTP yardımcıları | Genel sağlayıcı HTTP/uç nokta yeteneği yardımcıları |
  | `plugin-sdk/provider-web-fetch` | Sağlayıcı web-fetch yardımcıları | Web-fetch sağlayıcı kayıt/önbellek yardımcıları |
  | `plugin-sdk/provider-web-search` | Sağlayıcı web-search yardımcıları | Web-search sağlayıcı kayıt/önbellek/config yardımcıları |
  | `plugin-sdk/provider-tools` | Sağlayıcı araç/şema uyumluluk yardımcıları | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, Gemini şema temizleme + tanılama ve `resolveXaiModelCompatPatch` / `applyXaiModelCompat` gibi xAI uyumluluk yardımcıları |
  | `plugin-sdk/provider-usage` | Sağlayıcı kullanım yardımcıları | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage` ve diğer sağlayıcı kullanım yardımcıları |
  | `plugin-sdk/provider-stream` | Sağlayıcı akış sarmalayıcı yardımcıları | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, akış sarmalayıcı türleri ve paylaşılan Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot sarmalayıcı yardımcıları |
  | `plugin-sdk/keyed-async-queue` | Sıralı async kuyruk | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Paylaşılan medya yardımcıları | Medya fetch/dönüştürme/depolama yardımcıları ve medya payload oluşturucuları |
  | `plugin-sdk/media-generation-runtime` | Paylaşılan medya üretim yardımcıları | Görsel/video/müzik üretimi için paylaşılan failover yardımcıları, aday seçimi ve eksik model mesajlaşması |
  | `plugin-sdk/media-understanding` | Media-understanding yardımcıları | Media understanding sağlayıcı türleri ve sağlayıcıya dönük görsel/ses yardımcı dışa aktarımları |
  | `plugin-sdk/text-runtime` | Paylaşılan metin yardımcıları | Asistan tarafından görülebilen metni temizleme, markdown işleme/parçalama/tablo yardımcıları, redaction yardımcıları, directive-tag yardımcıları, safe-text yardımcıları ve ilgili metin/günlükleme yardımcıları |
  | `plugin-sdk/text-chunking` | Metin parçalama yardımcıları | Giden metin parçalama yardımcısı |
  | `plugin-sdk/speech` | Konuşma yardımcıları | Konuşma sağlayıcı türleri ve sağlayıcıya dönük directive, kayıt ve doğrulama yardımcıları |
  | `plugin-sdk/speech-core` | Paylaşılan konuşma çekirdeği | Konuşma sağlayıcı türleri, kayıt, directive'ler, normalleştirme |
  | `plugin-sdk/realtime-transcription` | Gerçek zamanlı transkripsiyon yardımcıları | Sağlayıcı türleri ve kayıt yardımcıları |
  | `plugin-sdk/realtime-voice` | Gerçek zamanlı ses yardımcıları | Sağlayıcı türleri ve kayıt yardımcıları |
  | `plugin-sdk/image-generation-core` | Paylaşılan görsel üretim çekirdeği | Görsel üretim türleri, failover, kimlik doğrulama ve kayıt yardımcıları |
  | `plugin-sdk/music-generation` | Müzik üretim yardımcıları | Müzik üretim sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/music-generation-core` | Paylaşılan müzik üretim çekirdeği | Müzik üretim türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/video-generation` | Video üretim yardımcıları | Video üretim sağlayıcı/istek/sonuç türleri |
  | `plugin-sdk/video-generation-core` | Paylaşılan video üretim çekirdeği | Video üretim türleri, failover yardımcıları, sağlayıcı arama ve model-ref ayrıştırma |
  | `plugin-sdk/interactive-runtime` | Etkileşimli yanıt yardımcıları | Etkileşimli yanıt payload normalleştirme/indirgeme |
  | `plugin-sdk/channel-config-primitives` | Kanal config temel bileşenleri | Dar kapsamlı kanal config-schema temel bileşenleri |
  | `plugin-sdk/channel-config-writes` | Kanal config yazma yardımcıları | Kanal config yazma yetkilendirme yardımcıları |
  | `plugin-sdk/channel-plugin-common` | Paylaşılan kanal prelude'u | Paylaşılan kanal plugin prelude dışa aktarımları |
  | `plugin-sdk/channel-status` | Kanal durumu yardımcıları | Paylaşılan kanal durum anlık görüntü/özet yardımcıları |
  | `plugin-sdk/allowlist-config-edit` | Allowlist config yardımcıları | Allowlist config düzenleme/okuma yardımcıları |
  | `plugin-sdk/group-access` | Grup erişim yardımcıları | Paylaşılan grup erişim karar yardımcıları |
  | `plugin-sdk/direct-dm` | Doğrudan DM yardımcıları | Paylaşılan doğrudan DM kimlik doğrulama/koruma yardımcıları |
  | `plugin-sdk/extension-shared` | Paylaşılan extension yardımcıları | Pasif kanal/durum yardımcı temel bileşenleri |
  | `plugin-sdk/webhook-targets` | Webhook hedef yardımcıları | Webhook hedef kaydı ve rota kurulum yardımcıları |
  | `plugin-sdk/webhook-path` | Webhook yol yardımcıları | Webhook yolu normalleştirme yardımcıları |
  | `plugin-sdk/web-media` | Paylaşılan web medya yardımcıları | Uzak/yerel medya yükleme yardımcıları |
  | `plugin-sdk/zod` | Zod yeniden dışa aktarımı | Plugin SDK tüketicileri için yeniden dışa aktarılan `zod` |
  | `plugin-sdk/memory-core` | Paketli memory-core yardımcıları | Bellek yöneticisi/config/dosya/CLI yardımcı yüzeyi |
  | `plugin-sdk/memory-core-engine-runtime` | Bellek motoru çalışma zamanı cephesi | Bellek indeksleme/arama çalışma zamanı cephesi |
  | `plugin-sdk/memory-core-host-engine-foundation` | Bellek ana makine foundation motoru | Bellek ana makine foundation motoru dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Bellek ana makine embedding motoru | Bellek ana makine embedding motoru dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-qmd` | Bellek ana makine QMD motoru | Bellek ana makine QMD motoru dışa aktarımları |
  | `plugin-sdk/memory-core-host-engine-storage` | Bellek ana makine depolama motoru | Bellek ana makine depolama motoru dışa aktarımları |
  | `plugin-sdk/memory-core-host-multimodal` | Bellek ana makine multimodal yardımcıları | Bellek ana makine multimodal yardımcıları |
  | `plugin-sdk/memory-core-host-query` | Bellek ana makine sorgu yardımcıları | Bellek ana makine sorgu yardımcıları |
  | `plugin-sdk/memory-core-host-secret` | Bellek ana makine secret yardımcıları | Bellek ana makine secret yardımcıları |
  | `plugin-sdk/memory-core-host-events` | Bellek ana makine olay günlüğü yardımcıları | Bellek ana makine olay günlüğü yardımcıları |
  | `plugin-sdk/memory-core-host-status` | Bellek ana makine durum yardımcıları | Bellek ana makine durum yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-cli` | Bellek ana makine CLI çalışma zamanı | Bellek ana makine CLI çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-core` | Bellek ana makine çekirdek çalışma zamanı | Bellek ana makine çekirdek çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-core-host-runtime-files` | Bellek ana makine dosya/çalışma zamanı yardımcıları | Bellek ana makine dosya/çalışma zamanı yardımcıları |
  | `plugin-sdk/memory-host-core` | Bellek ana makine çekirdek çalışma zamanı takma adı | Bellek ana makine çekirdek çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-events` | Bellek ana makine olay günlüğü takma adı | Bellek ana makine olay günlüğü yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-files` | Bellek ana makine dosya/çalışma zamanı takma adı | Bellek ana makine dosya/çalışma zamanı yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-host-markdown` | Yönetilen markdown yardımcıları | Belleğe bitişik plugin'ler için paylaşılan yönetilen markdown yardımcıları |
  | `plugin-sdk/memory-host-search` | Etkin bellek arama cephesi | Lazy etkin bellek search-manager çalışma zamanı cephesi |
  | `plugin-sdk/memory-host-status` | Bellek ana makine durumu takma adı | Bellek ana makine durum yardımcıları için satıcıdan bağımsız takma ad |
  | `plugin-sdk/memory-lancedb` | Paketli memory-lancedb yardımcıları | Memory-lancedb yardımcı yüzeyi |
  | `plugin-sdk/testing` | Test yardımcıları | Test yardımcıları ve mock'lar |
</Accordion>

Bu tablo kasıtlı olarak tam SDK yüzeyi değil, yaygın geçiş alt kümesidir.
200'den fazla giriş noktasının tam listesi
`scripts/lib/plugin-sdk-entrypoints.json` içinde yer alır.

Bu listede hâlâ `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` ve `plugin-sdk/matrix*` gibi bazı paketli plugin yardımcı
seam'leri yer alır. Bunlar paketli plugin bakımı ve uyumluluk için dışa
aktarılmaya devam eder, ancak yaygın geçiş tablosuna kasıtlı olarak dahil
edilmemiştir ve yeni plugin kodu için önerilen hedef değildir.

Aynı kural diğer paketli yardımcı aileleri için de geçerlidir; örneğin:

- tarayıcı desteği yardımcıları: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership` ve `plugin-sdk/voice-call` gibi
  paketli yardımcı/plugin yüzeyleri

`plugin-sdk/github-copilot-token` şu anda dar kapsamlı token-helper
yüzeyi olan `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken` ve `resolveCopilotApiToken` öğelerini dışa aktarır.

Yapılan işe en uygun en dar içe aktarmayı kullanın. Bir dışa aktarma
bulamıyorsanız `src/plugin-sdk/` altındaki kaynağı kontrol edin veya Discord'da sorun.

## Kaldırma zaman çizelgesi

| Ne zaman               | Ne olur                                                                |
| ---------------------- | ---------------------------------------------------------------------- |
| **Şimdi**              | Kullanımdan kaldırılmış yüzeyler çalışma zamanında uyarılar üretir     |
| **Bir sonraki büyük sürüm** | Kullanımdan kaldırılmış yüzeyler kaldırılır; bunları hâlâ kullanan plugin'ler başarısız olur |

Tüm çekirdek plugin'ler zaten geçirilmiştir. Harici plugin'ler bir sonraki büyük
sürümden önce geçiş yapmalıdır.

## Uyarıları geçici olarak bastırma

Geçiş üzerinde çalışırken şu ortam değişkenlerini ayarlayın:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Bu geçici bir kaçış kapağıdır, kalıcı bir çözüm değildir.

## İlgili

- [Başlangıç](/tr/plugins/building-plugins) — ilk plugin'inizi oluşturun
- [SDK Genel Bakış](/tr/plugins/sdk-overview) — alt yollar için tam içe aktarma başvurusu
- [Kanal Plugin'leri](/tr/plugins/sdk-channel-plugins) — kanal plugin'leri oluşturma
- [Sağlayıcı Plugin'leri](/tr/plugins/sdk-provider-plugins) — sağlayıcı plugin'leri oluşturma
- [Plugin İç Yapıları](/tr/plugins/architecture) — mimariye derinlemesine bakış
- [Plugin Manifesti](/tr/plugins/manifest) — manifest şeması başvurusu
