---
read_when:
    - Anda perlu mengetahui subpath SDK mana yang harus diimpor dari
    - Anda menginginkan referensi untuk semua metode pendaftaran pada OpenClawPluginApi
    - Anda sedang mencari ekspor SDK tertentu
sidebarTitle: SDK Overview
summary: Peta impor, referensi API pendaftaran, dan arsitektur SDK
title: Ikhtisar Plugin SDK
x-i18n:
    generated_at: "2026-04-08T09:13:46Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e7b420eb0f3faa8916357d52df949f6c9a46f1c843a1e6a0c0b8bb26db6cbff
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Ikhtisar Plugin SDK

Plugin SDK adalah kontrak bertipe antara plugin dan core. Halaman ini adalah
referensi untuk **apa yang harus diimpor** dan **apa yang dapat Anda daftarkan**.

<Tip>
  **Mencari panduan cara melakukannya?**
  - Plugin pertama? Mulai dengan [Getting Started](/id/plugins/building-plugins)
  - Plugin channel? Lihat [Channel Plugins](/id/plugins/sdk-channel-plugins)
  - Plugin provider? Lihat [Provider Plugins](/id/plugins/sdk-provider-plugins)
</Tip>

## Konvensi impor

Selalu impor dari subpath tertentu:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Setiap subpath adalah modul kecil yang berdiri sendiri. Ini menjaga startup tetap cepat dan
mencegah masalah dependensi melingkar. Untuk helper entry/build khusus channel,
utamakan `openclaw/plugin-sdk/channel-core`; gunakan `openclaw/plugin-sdk/core` untuk
permukaan payung yang lebih luas dan helper bersama seperti
`buildChannelConfigSchema`.

Jangan tambahkan atau bergantung pada seam kemudahan bernama provider seperti
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, atau
seam helper bermerek channel. Plugin bawaan harus menyusun subpath
SDK generik di dalam barrel `api.ts` atau `runtime-api.ts` mereka sendiri, dan core
harus menggunakan barrel lokal plugin tersebut atau menambahkan kontrak SDK generik
yang sempit saat kebutuhannya benar-benar lintas channel.

Peta ekspor yang dihasilkan masih memuat sejumlah kecil seam helper plugin bawaan
seperti `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup`, dan `plugin-sdk/matrix*`. Subpath
tersebut hanya ada untuk pemeliharaan dan kompatibilitas plugin bawaan; subpath itu
sengaja tidak dimasukkan dari tabel umum di bawah dan bukan jalur impor yang
direkomendasikan untuk plugin pihak ketiga yang baru.

## Referensi subpath

Subpath yang paling umum digunakan, dikelompokkan berdasarkan tujuan. Daftar lengkap yang dihasilkan
berisi lebih dari 200 subpath ada di `scripts/lib/plugin-sdk-entrypoints.json`.

Subpath helper plugin bawaan yang dicadangkan masih muncul dalam daftar yang dihasilkan itu.
Perlakukan itu sebagai permukaan detail implementasi/kompatibilitas kecuali suatu halaman dokumentasi
secara eksplisit mempromosikannya sebagai publik.

### Entri plugin

| Subpath                     | Ekspor utama                                                                                                                          |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Subpath channel">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Ekspor skema Zod root `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, serta `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Helper wizard setup bersama, prompt allowlist, builder status setup |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Helper multi-akun config/action-gate, helper fallback akun default |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, helper normalisasi account-id |
    | `plugin-sdk/account-resolution` | Helper pencarian akun + fallback default |
    | `plugin-sdk/account-helpers` | Helper sempit untuk daftar akun/tindakan akun |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipe skema config channel |
    | `plugin-sdk/telegram-command-config` | Helper normalisasi/validasi custom command Telegram dengan fallback kontrak bawaan |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Helper rute inbound + builder envelope bersama |
    | `plugin-sdk/inbound-reply-dispatch` | Helper record-and-dispatch inbound bersama |
    | `plugin-sdk/messaging-targets` | Helper parsing/pencocokan target |
    | `plugin-sdk/outbound-media` | Helper pemuatan media outbound bersama |
    | `plugin-sdk/outbound-runtime` | Helper identitas outbound/delegasi pengiriman |
    | `plugin-sdk/thread-bindings-runtime` | Siklus hidup thread-binding dan helper adapter |
    | `plugin-sdk/agent-media-payload` | Builder payload media agent lama |
    | `plugin-sdk/conversation-runtime` | Helper binding percakapan/thread, pairing, dan configured-binding |
    | `plugin-sdk/runtime-config-snapshot` | Helper snapshot config runtime |
    | `plugin-sdk/runtime-group-policy` | Helper resolusi group-policy runtime |
    | `plugin-sdk/channel-status` | Helper snapshot/ringkasan status channel bersama |
    | `plugin-sdk/channel-config-primitives` | Primitive sempit skema config channel |
    | `plugin-sdk/channel-config-writes` | Helper otorisasi penulisan config channel |
    | `plugin-sdk/channel-plugin-common` | Ekspor prelude plugin channel bersama |
    | `plugin-sdk/allowlist-config-edit` | Helper edit/baca config allowlist |
    | `plugin-sdk/group-access` | Helper keputusan akses grup bersama |
    | `plugin-sdk/direct-dm` | Helper auth/guard direct-DM bersama |
    | `plugin-sdk/interactive-runtime` | Helper normalisasi/reduksi payload balasan interaktif |
    | `plugin-sdk/channel-inbound` | Debounce inbound, pencocokan mention, helper kebijakan mention, dan helper envelope |
    | `plugin-sdk/channel-send-result` | Tipe hasil balasan |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Helper parsing/pencocokan target |
    | `plugin-sdk/channel-contract` | Tipe kontrak channel |
    | `plugin-sdk/channel-feedback` | Wiring feedback/reaksi |
    | `plugin-sdk/channel-secret-runtime` | Helper kontrak secret yang sempit seperti `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment`, dan tipe target secret |
  </Accordion>

  <Accordion title="Subpath provider">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Helper setup provider lokal/self-hosted yang terkurasi |
    | `plugin-sdk/self-hosted-provider-setup` | Helper setup provider self-hosted kompatibel OpenAI yang terfokus |
    | `plugin-sdk/cli-backend` | Default backend CLI + konstanta watchdog |
    | `plugin-sdk/provider-auth-runtime` | Helper resolusi API key runtime untuk plugin provider |
    | `plugin-sdk/provider-auth-api-key` | Helper onboarding/penulisan profil API key seperti `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Builder hasil auth OAuth standar |
    | `plugin-sdk/provider-auth-login` | Helper login interaktif bersama untuk plugin provider |
    | `plugin-sdk/provider-env-vars` | Helper pencarian env var auth provider |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder kebijakan replay bersama, helper endpoint provider, dan helper normalisasi model-id seperti `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Helper kapabilitas HTTP/endpoint provider generik |
    | `plugin-sdk/provider-web-fetch-contract` | Helper kontrak config/seleksi web-fetch yang sempit seperti `enablePluginInConfig` dan `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Helper pendaftaran/cache provider web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | Helper config/kredensial web-search yang sempit untuk provider yang tidak memerlukan wiring enable plugin |
    | `plugin-sdk/provider-web-search-contract` | Helper kontrak config/kredensial web-search yang sempit seperti `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`, dan setter/getter kredensial berpencakupan |
    | `plugin-sdk/provider-web-search` | Helper pendaftaran/cache/runtime provider web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pembersihan skema Gemini + diagnostik, dan helper kompatibilitas xAI seperti `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` dan yang serupa |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipe wrapper stream, dan helper wrapper bersama Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Helper patch config onboarding |
    | `plugin-sdk/global-singleton` | Helper singleton/map/cache lokal proses |
  </Accordion>

  <Accordion title="Subpath auth dan keamanan">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, helper registri command, helper otorisasi pengirim |
    | `plugin-sdk/approval-auth-runtime` | Helper resolusi approver dan auth tindakan obrolan yang sama |
    | `plugin-sdk/approval-client-runtime` | Helper profil/filter approval exec native |
    | `plugin-sdk/approval-delivery-runtime` | Adapter kapabilitas/pengiriman approval native |
    | `plugin-sdk/approval-gateway-runtime` | Helper resolusi gateway approval bersama |
    | `plugin-sdk/approval-handler-adapter-runtime` | Helper pemuatan adapter approval native ringan untuk entrypoint channel yang sering dipanggil |
    | `plugin-sdk/approval-handler-runtime` | Helper runtime handler approval yang lebih luas; utamakan seam adapter/gateway yang lebih sempit bila itu sudah cukup |
    | `plugin-sdk/approval-native-runtime` | Helper target approval native + binding akun |
    | `plugin-sdk/approval-reply-runtime` | Helper payload balasan approval exec/plugin |
    | `plugin-sdk/command-auth-native` | Auth command native + helper target sesi native |
    | `plugin-sdk/command-detection` | Helper deteksi command bersama |
    | `plugin-sdk/command-surface` | Helper normalisasi badan command dan permukaan command |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Helper koleksi kontrak secret yang sempit untuk permukaan secret channel/plugin |
    | `plugin-sdk/secret-ref-runtime` | Helper `coerceSecretRef` yang sempit dan helper tipe SecretRef untuk parsing kontrak secret/config |
    | `plugin-sdk/security-runtime` | Helper trust, gating DM, konten eksternal, dan pengumpulan secret bersama |
    | `plugin-sdk/ssrf-policy` | Helper allowlist host dan kebijakan SSRF jaringan privat |
    | `plugin-sdk/ssrf-runtime` | Helper pinned-dispatcher, fetch yang dijaga SSRF, dan kebijakan SSRF |
    | `plugin-sdk/secret-input` | Helper parsing input secret |
    | `plugin-sdk/webhook-ingress` | Helper request/target webhook |
    | `plugin-sdk/webhook-request-guards` | Helper ukuran body/timeout request |
  </Accordion>

  <Accordion title="Subpath runtime dan penyimpanan">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/runtime` | Helper runtime/logging/backup/instal plugin yang luas |
    | `plugin-sdk/runtime-env` | Helper env runtime, logger, timeout, retry, dan backoff yang sempit |
    | `plugin-sdk/channel-runtime-context` | Helper generik untuk pendaftaran dan pencarian konteks runtime channel |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Helper command/hook/http/interaktif plugin bersama |
    | `plugin-sdk/hook-runtime` | Helper pipeline hook webhook/internal bersama |
    | `plugin-sdk/lazy-runtime` | Helper impor/binding runtime lazy seperti `createLazyRuntimeModule`, `createLazyRuntimeMethod`, dan `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Helper eksekusi proses |
    | `plugin-sdk/cli-runtime` | Helper format, tunggu, dan versi CLI |
    | `plugin-sdk/gateway-runtime` | Helper client gateway dan patch status channel |
    | `plugin-sdk/config-runtime` | Helper pemuatan/penulisan config |
    | `plugin-sdk/telegram-command-config` | Normalisasi nama/deskripsi command Telegram dan pemeriksaan duplikat/konflik, bahkan saat permukaan kontrak Telegram bawaan tidak tersedia |
    | `plugin-sdk/approval-runtime` | Helper approval exec/plugin, builder kapabilitas approval, helper auth/profil, helper routing/runtime native |
    | `plugin-sdk/reply-runtime` | Helper runtime inbound/balasan bersama, chunking, dispatch, heartbeat, perencana balasan |
    | `plugin-sdk/reply-dispatch-runtime` | Helper dispatch/finalisasi balasan yang sempit |
    | `plugin-sdk/reply-history` | Helper riwayat balasan jendela pendek bersama seperti `buildHistoryContext`, `recordPendingHistoryEntry`, dan `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Helper chunking teks/markdown yang sempit |
    | `plugin-sdk/session-store-runtime` | Helper path penyimpanan sesi + updated-at |
    | `plugin-sdk/state-paths` | Helper path direktori state/OAuth |
    | `plugin-sdk/routing` | Helper rute/kunci sesi/binding akun seperti `resolveAgentRoute`, `buildAgentSessionKey`, dan `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Helper ringkasan status channel/akun bersama, default state runtime, dan helper metadata isu |
    | `plugin-sdk/target-resolver-runtime` | Helper resolver target bersama |
    | `plugin-sdk/string-normalization-runtime` | Helper normalisasi slug/string |
    | `plugin-sdk/request-url` | Ekstrak URL string dari input mirip fetch/request |
    | `plugin-sdk/run-command` | Runner command bertimer dengan hasil stdout/stderr yang dinormalisasi |
    | `plugin-sdk/param-readers` | Pembaca param umum untuk tool/CLI |
    | `plugin-sdk/tool-payload` | Ekstrak payload yang dinormalisasi dari objek hasil tool |
    | `plugin-sdk/tool-send` | Ekstrak field target pengiriman kanonis dari argumen tool |
    | `plugin-sdk/temp-path` | Helper path unduhan sementara bersama |
    | `plugin-sdk/logging-core` | Helper logger subsistem dan redaksi |
    | `plugin-sdk/markdown-table-runtime` | Helper mode tabel Markdown |
    | `plugin-sdk/json-store` | Helper baca/tulis state JSON kecil |
    | `plugin-sdk/file-lock` | Helper file-lock re-entrant |
    | `plugin-sdk/persistent-dedupe` | Helper cache dedupe berbasis disk |
    | `plugin-sdk/acp-runtime` | Helper ACP runtime/sesi dan reply-dispatch |
    | `plugin-sdk/agent-config-primitives` | Primitive sempit skema config runtime agent |
    | `plugin-sdk/boolean-param` | Pembaca param boolean longgar |
    | `plugin-sdk/dangerous-name-runtime` | Helper resolusi pencocokan nama berbahaya |
    | `plugin-sdk/device-bootstrap` | Helper bootstrap perangkat dan token pairing |
    | `plugin-sdk/extension-shared` | Primitive helper bersama untuk passive-channel, status, dan ambient proxy |
    | `plugin-sdk/models-provider-runtime` | Helper balasan command/provider `/models` |
    | `plugin-sdk/skill-commands-runtime` | Helper daftar skill command |
    | `plugin-sdk/native-command-registry` | Helper registry/build/serialize command native |
    | `plugin-sdk/provider-zai-endpoint` | Helper deteksi endpoint Z.AI |
    | `plugin-sdk/infra-runtime` | Helper event sistem/heartbeat |
    | `plugin-sdk/collection-runtime` | Helper cache kecil yang dibatasi |
    | `plugin-sdk/diagnostic-runtime` | Helper flag dan event diagnostik |
    | `plugin-sdk/error-runtime` | Helper graf error, formatting, klasifikasi error bersama, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Helper fetch terbungkus, proxy, dan pencarian pinned |
    | `plugin-sdk/host-runtime` | Helper normalisasi hostname dan host SCP |
    | `plugin-sdk/retry-runtime` | Helper config retry dan runner retry |
    | `plugin-sdk/agent-runtime` | Helper direktori/identitas/workspace agent |
    | `plugin-sdk/directory-runtime` | Query/dedup direktori berbasis config |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Subpath kapabilitas dan pengujian">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Helper fetch/transform/store media bersama plus builder payload media |
    | `plugin-sdk/media-generation-runtime` | Helper failover media-generation bersama, pemilihan kandidat, dan pesan model yang hilang |
    | `plugin-sdk/media-understanding` | Tipe provider media understanding plus ekspor helper gambar/audio yang menghadap provider |
    | `plugin-sdk/text-runtime` | Helper teks/markdown/logging bersama seperti penghapusan teks yang terlihat oleh asisten, helper render/chunking/tabel markdown, helper redaksi, helper tag arahan, dan utilitas safe-text |
    | `plugin-sdk/text-chunking` | Helper chunking teks outbound |
    | `plugin-sdk/speech` | Tipe provider speech plus ekspor helper arahan, registri, dan validasi yang menghadap provider |
    | `plugin-sdk/speech-core` | Tipe provider speech bersama, registri, arahan, dan helper normalisasi |
    | `plugin-sdk/realtime-transcription` | Tipe provider realtime transcription dan helper registri |
    | `plugin-sdk/realtime-voice` | Tipe provider realtime voice dan helper registri |
    | `plugin-sdk/image-generation` | Tipe provider image generation |
    | `plugin-sdk/image-generation-core` | Tipe image-generation bersama, failover, auth, dan helper registri |
    | `plugin-sdk/music-generation` | Tipe provider/request/result music generation |
    | `plugin-sdk/music-generation-core` | Tipe music-generation bersama, helper failover, pencarian provider, dan parsing model-ref |
    | `plugin-sdk/video-generation` | Tipe provider/request/result video generation |
    | `plugin-sdk/video-generation-core` | Tipe video-generation bersama, helper failover, pencarian provider, dan parsing model-ref |
    | `plugin-sdk/webhook-targets` | Registry target webhook dan helper pemasangan rute |
    | `plugin-sdk/webhook-path` | Helper normalisasi path webhook |
    | `plugin-sdk/web-media` | Helper pemuatan media remote/lokal bersama |
    | `plugin-sdk/zod` | `zod` yang diekspor ulang untuk konsumen plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Subpath memori">
    | Subpath | Ekspor utama |
    | --- | --- |
    | `plugin-sdk/memory-core` | Permukaan helper memory-core bawaan untuk helper manager/config/file/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Fasad runtime indeks/pencarian memori |
    | `plugin-sdk/memory-core-host-engine-foundation` | Ekspor engine fondasi host memori |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Ekspor engine embedding host memori |
    | `plugin-sdk/memory-core-host-engine-qmd` | Ekspor engine QMD host memori |
    | `plugin-sdk/memory-core-host-engine-storage` | Ekspor engine penyimpanan host memori |
    | `plugin-sdk/memory-core-host-multimodal` | Helper multimodal host memori |
    | `plugin-sdk/memory-core-host-query` | Helper query host memori |
    | `plugin-sdk/memory-core-host-secret` | Helper secret host memori |
    | `plugin-sdk/memory-core-host-events` | Helper jurnal event host memori |
    | `plugin-sdk/memory-core-host-status` | Helper status host memori |
    | `plugin-sdk/memory-core-host-runtime-cli` | Helper runtime CLI host memori |
    | `plugin-sdk/memory-core-host-runtime-core` | Helper runtime core host memori |
    | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime host memori |
    | `plugin-sdk/memory-host-core` | Alias netral-vendor untuk helper runtime inti host memori |
    | `plugin-sdk/memory-host-events` | Alias netral-vendor untuk helper jurnal event host memori |
    | `plugin-sdk/memory-host-files` | Alias netral-vendor untuk helper file/runtime host memori |
    | `plugin-sdk/memory-host-markdown` | Helper managed-markdown bersama untuk plugin yang berdekatan dengan memori |
    | `plugin-sdk/memory-host-search` | Fasad runtime memori aktif untuk akses search-manager |
    | `plugin-sdk/memory-host-status` | Alias netral-vendor untuk helper status host memori |
    | `plugin-sdk/memory-lancedb` | Permukaan helper memory-lancedb bawaan |
  </Accordion>

  <Accordion title="Subpath helper bawaan yang dicadangkan">
    | Family | Subpath saat ini | Penggunaan yang dimaksudkan |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Helper dukungan plugin browser bawaan (`browser-support` tetap menjadi barrel kompatibilitas) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Permukaan helper/runtime Matrix bawaan |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Permukaan helper/runtime LINE bawaan |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Permukaan helper IRC bawaan |
    | Helper khusus channel | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Seam kompatibilitas/helper channel bawaan |
    | Helper khusus auth/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Seam helper fitur/plugin bawaan; `plugin-sdk/github-copilot-token` saat ini mengekspor `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken`, dan `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API pendaftaran

Callback `register(api)` menerima objek `OpenClawPluginApi` dengan metode-metode
berikut:

### Pendaftaran kapabilitas

| Method                                           | Apa yang didaftarkan            |
| ------------------------------------------------ | -------------------------------- |
| `api.registerProvider(...)`                      | Inferensi teks (LLM)             |
| `api.registerCliBackend(...)`                    | Backend inferensi CLI lokal      |
| `api.registerChannel(...)`                       | Channel pesan                |
| `api.registerSpeechProvider(...)`                | Sintesis teks-ke-suara / STT   |
| `api.registerRealtimeTranscriptionProvider(...)` | Transkripsi realtime streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sesi suara realtime dupleks   |
| `api.registerMediaUnderstandingProvider(...)`    | Analisis gambar/audio/video       |
| `api.registerImageGenerationProvider(...)`       | Pembuatan gambar                 |
| `api.registerMusicGenerationProvider(...)`       | Pembuatan musik                 |
| `api.registerVideoGenerationProvider(...)`       | Pembuatan video                 |
| `api.registerWebFetchProvider(...)`              | Provider web fetch / scrape      |
| `api.registerWebSearchProvider(...)`             | Pencarian web                       |

### Tools dan command

| Method                          | Apa yang didaftarkan                             |
| ------------------------------- | --------------------------------------------- |
| `api.registerTool(tool, opts?)` | Tool agent (wajib atau `{ optional: true }`) |
| `api.registerCommand(def)`      | Command kustom (melewati LLM)             |

### Infrastruktur

| Method                                         | Apa yang didaftarkan                       |
| ---------------------------------------------- | --------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook event                              |
| `api.registerHttpRoute(params)`                | Endpoint HTTP gateway                   |
| `api.registerGatewayMethod(name, handler)`     | Metode RPC gateway                      |
| `api.registerCli(registrar, opts?)`            | Subcommand CLI                          |
| `api.registerService(service)`                 | Layanan latar belakang                      |
| `api.registerInteractiveHandler(registration)` | Handler interaktif                     |
| `api.registerMemoryPromptSupplement(builder)`  | Bagian prompt aditif yang berdekatan dengan memori |
| `api.registerMemoryCorpusSupplement(adapter)`  | Korpus pencarian/baca memori aditif      |

Namespace admin core yang dicadangkan (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) selalu tetap `operator.admin`, meskipun plugin mencoba menetapkan
cakupan metode gateway yang lebih sempit. Utamakan prefiks khusus plugin untuk
metode yang dimiliki plugin.

### Metadata pendaftaran CLI

`api.registerCli(registrar, opts?)` menerima dua jenis metadata tingkat atas:

- `commands`: root command eksplisit yang dimiliki registrar
- `descriptors`: deskriptor command saat parse yang digunakan untuk bantuan CLI root,
  routing, dan pendaftaran CLI plugin lazy

Jika Anda ingin command plugin tetap dimuat secara lazy di jalur CLI root normal,
sediakan `descriptors` yang mencakup setiap root command tingkat atas yang diekspos oleh
registrar tersebut.

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
        description: "Kelola akun Matrix, verifikasi, perangkat, dan status profil",
        hasSubcommands: true,
      },
    ],
  },
);
```

Gunakan `commands` saja hanya ketika Anda tidak memerlukan pendaftaran CLI root secara lazy.
Jalur kompatibilitas eager tersebut tetap didukung, tetapi tidak memasang
placeholder berbasis descriptor untuk pemuatan lazy saat parse-time.

### Pendaftaran backend CLI

`api.registerCliBackend(...)` memungkinkan plugin memiliki config default untuk backend
CLI AI lokal seperti `codex-cli`.

- `id` backend menjadi prefiks provider dalam model ref seperti `codex-cli/gpt-5`.
- `config` backend menggunakan bentuk yang sama seperti `agents.defaults.cliBackends.<id>`.
- Config pengguna tetap menang. OpenClaw menggabungkan `agents.defaults.cliBackends.<id>` di atas default
  plugin sebelum menjalankan CLI.
- Gunakan `normalizeConfig` saat backend memerlukan penulisan ulang kompatibilitas setelah penggabungan
  (misalnya menormalisasi bentuk flag lama).

### Slot eksklusif

| Method                                     | Apa yang didaftarkan                                                                                                                                         |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Engine konteks (satu aktif pada satu waktu). Callback `assemble()` menerima `availableTools` dan `citationsMode` sehingga engine dapat menyesuaikan penambahan prompt. |
| `api.registerMemoryCapability(capability)` | Kapabilitas memori terpadu                                                                                                                                 |
| `api.registerMemoryPromptSection(builder)` | Builder bagian prompt memori                                                                                                                             |
| `api.registerMemoryFlushPlan(resolver)`    | Resolver rencana flush memori                                                                                                                                |
| `api.registerMemoryRuntime(runtime)`       | Adapter runtime memori                                                                                                                                    |

### Adapter embedding memori

| Method                                         | Apa yang didaftarkan                              |
| ---------------------------------------------- | ---------------------------------------------- |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adapter embedding memori untuk plugin aktif |

- `registerMemoryCapability` adalah API plugin memori eksklusif yang diutamakan.
- `registerMemoryCapability` juga dapat mengekspos `publicArtifacts.listArtifacts(...)`
  sehingga plugin pendamping dapat menggunakan artefak memori yang diekspor melalui
  `openclaw/plugin-sdk/memory-host-core` alih-alih menjangkau tata letak privat
  plugin memori tertentu.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan`, dan
  `registerMemoryRuntime` adalah API plugin memori eksklusif yang kompatibel dengan versi lama.
- `registerMemoryEmbeddingProvider` memungkinkan plugin memori aktif mendaftarkan satu
  atau lebih id adapter embedding (misalnya `openai`, `gemini`, atau id yang ditentukan plugin secara kustom).
- Config pengguna seperti `agents.defaults.memorySearch.provider` dan
  `agents.defaults.memorySearch.fallback` diselesaikan terhadap id adapter yang terdaftar tersebut.

### Event dan siklus hidup

| Method                                       | Fungsinya                  |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook siklus hidup bertipe          |
| `api.onConversationBindingResolved(handler)` | Callback binding percakapan |

### Semantik keputusan hook

- `before_tool_call`: mengembalikan `{ block: true }` bersifat terminal. Setelah handler mana pun menetapkannya, handler dengan prioritas lebih rendah dilewati.
- `before_tool_call`: mengembalikan `{ block: false }` diperlakukan sebagai tidak ada keputusan (sama seperti menghilangkan `block`), bukan sebagai override.
- `before_install`: mengembalikan `{ block: true }` bersifat terminal. Setelah handler mana pun menetapkannya, handler dengan prioritas lebih rendah dilewati.
- `before_install`: mengembalikan `{ block: false }` diperlakukan sebagai tidak ada keputusan (sama seperti menghilangkan `block`), bukan sebagai override.
- `reply_dispatch`: mengembalikan `{ handled: true, ... }` bersifat terminal. Setelah handler mana pun mengklaim dispatch, handler dengan prioritas lebih rendah dan jalur dispatch model default dilewati.
- `message_sending`: mengembalikan `{ cancel: true }` bersifat terminal. Setelah handler mana pun menetapkannya, handler dengan prioritas lebih rendah dilewati.
- `message_sending`: mengembalikan `{ cancel: false }` diperlakukan sebagai tidak ada keputusan (sama seperti menghilangkan `cancel`), bukan sebagai override.

### Field objek API

| Field                    | Type                      | Deskripsi                                                                                 |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------- |
| `api.id`                 | `string`                  | Id plugin                                                                                   |
| `api.name`               | `string`                  | Nama tampilan                                                                                |
| `api.version`            | `string?`                 | Versi plugin (opsional)                                                                   |
| `api.description`        | `string?`                 | Deskripsi plugin (opsional)                                                               |
| `api.source`             | `string`                  | Path sumber plugin                                                                          |
| `api.rootDir`            | `string?`                 | Direktori root plugin (opsional)                                                            |
| `api.config`             | `OpenClawConfig`          | Snapshot config saat ini (snapshot runtime dalam memori yang aktif bila tersedia)                  |
| `api.pluginConfig`       | `Record<string, unknown>` | Config khusus plugin dari `plugins.entries.<id>.config`                                   |
| `api.runtime`            | `PluginRuntime`           | [Helper runtime](/id/plugins/sdk-runtime)                                                     |
| `api.logger`             | `PluginLogger`            | Logger berpencakupan (`debug`, `info`, `warn`, `error`)                                            |
| `api.registrationMode`   | `PluginRegistrationMode`  | Mode pemuatan saat ini; `"setup-runtime"` adalah jendela startup/setup ringan sebelum entri penuh |
| `api.resolvePath(input)` | `(string) => string`      | Menyelesaikan path relatif terhadap root plugin                                                        |

## Konvensi modul internal

Di dalam plugin Anda, gunakan file barrel lokal untuk impor internal:

```
my-plugin/
  api.ts            # Ekspor publik untuk konsumen eksternal
  runtime-api.ts    # Ekspor runtime khusus internal
  index.ts          # Entry point plugin
  setup-entry.ts    # Entri setup ringan saja (opsional)
```

<Warning>
  Jangan pernah mengimpor plugin Anda sendiri melalui `openclaw/plugin-sdk/<your-plugin>`
  dari kode production. Arahkan impor internal melalui `./api.ts` atau
  `./runtime-api.ts`. Path SDK hanya merupakan kontrak eksternal.
</Warning>

Permukaan publik plugin bawaan yang dimuat melalui fasad (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts`, dan file entri publik serupa) kini mengutamakan
snapshot config runtime aktif saat OpenClaw sudah berjalan. Jika snapshot runtime
belum ada, permukaan tersebut akan fallback ke file config di disk yang telah diselesaikan.

Plugin provider juga dapat mengekspos barrel kontrak lokal plugin yang sempit ketika suatu
helper memang khusus provider dan belum cocok ditempatkan dalam subpath SDK generik.
Contoh bawaan saat ini: provider Anthropic menyimpan helper stream Claude
di seam publik `api.ts` / `contract-api.ts` miliknya sendiri alih-alih
mempromosikan logika header beta Anthropic dan `service_tier` ke dalam kontrak
`plugin-sdk/*` generik.

Contoh bawaan lain saat ini:

- `@openclaw/openai-provider`: `api.ts` mengekspor builder provider,
  helper model default, dan builder provider realtime
- `@openclaw/openrouter-provider`: `api.ts` mengekspor builder provider plus
  helper onboarding/config

<Warning>
  Kode production extension juga harus menghindari impor `openclaw/plugin-sdk/<other-plugin>`.
  Jika suatu helper benar-benar dibagikan, promosikan helper tersebut ke subpath SDK netral
  seperti `openclaw/plugin-sdk/speech`, `.../provider-model-shared`, atau
  permukaan berorientasi kapabilitas lainnya alih-alih memasangkan dua plugin secara langsung.
</Warning>

## Terkait

- [Entry Points](/id/plugins/sdk-entrypoints) — opsi `definePluginEntry` dan `defineChannelPluginEntry`
- [Runtime Helpers](/id/plugins/sdk-runtime) — referensi namespace `api.runtime` lengkap
- [Setup and Config](/id/plugins/sdk-setup) — packaging, manifes, skema config
- [Testing](/id/plugins/sdk-testing) — utilitas pengujian dan aturan lint
- [SDK Migration](/id/plugins/sdk-migration) — migrasi dari permukaan yang sudah usang
- [Plugin Internals](/id/plugins/architecture) — arsitektur mendalam dan model kapabilitas
