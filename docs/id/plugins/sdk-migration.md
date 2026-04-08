---
read_when:
    - Anda melihat peringatan OPENCLAW_PLUGIN_SDK_COMPAT_DEPRECATED
    - Anda melihat peringatan OPENCLAW_EXTENSION_API_DEPRECATED
    - Anda sedang memperbarui plugin ke arsitektur plugin modern
    - Anda memelihara plugin OpenClaw eksternal
sidebarTitle: Migrate to SDK
summary: Migrasikan dari lapisan kompatibilitas mundur lama ke plugin SDK modern
title: Migrasi Plugin SDK
x-i18n:
    generated_at: "2026-04-08T09:13:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: d9a2ce7f5553563516a549ca87e776a6a71e8dd8533a773c5ddbecfae43e7b77
    source_path: plugins/sdk-migration.md
    workflow: 15
---

# Migrasi Plugin SDK

OpenClaw telah beralih dari lapisan kompatibilitas mundur yang luas ke arsitektur
plugin modern dengan impor yang terfokus dan terdokumentasi. Jika plugin Anda
dibangun sebelum arsitektur baru ini, panduan ini membantu Anda bermigrasi.

## Apa yang berubah

Sistem plugin lama menyediakan dua surface yang sangat terbuka yang memungkinkan
plugin mengimpor apa pun yang mereka perlukan dari satu titik masuk:

- **`openclaw/plugin-sdk/compat`** — satu impor yang mengekspor ulang puluhan
  helper. Ini diperkenalkan untuk menjaga plugin berbasis hook lama tetap
  berfungsi saat arsitektur plugin baru sedang dibangun.
- **`openclaw/extension-api`** — sebuah jembatan yang memberi plugin akses
  langsung ke helper sisi host seperti embedded agent runner.

Kedua surface sekarang **deprecated**. Keduanya masih berfungsi saat runtime,
tetapi plugin baru tidak boleh menggunakannya, dan plugin yang sudah ada harus
bermigrasi sebelum rilis mayor berikutnya menghapusnya.

<Warning>
  Lapisan kompatibilitas mundur akan dihapus pada rilis mayor mendatang.
  Plugin yang masih mengimpor dari surface ini akan rusak ketika itu terjadi.
</Warning>

## Mengapa ini berubah

Pendekatan lama menimbulkan masalah:

- **Startup lambat** — mengimpor satu helper memuat puluhan modul yang tidak terkait
- **Dependensi sirkular** — ekspor ulang yang luas memudahkan terbentuknya siklus impor
- **Surface API yang tidak jelas** — tidak ada cara untuk mengetahui ekspor mana yang stabil vs internal

Plugin SDK modern memperbaikinya: setiap path impor (`openclaw/plugin-sdk/\<subpath\>`)
adalah modul kecil yang mandiri dengan tujuan yang jelas dan kontrak yang terdokumentasi.

Seam kenyamanan provider lama untuk channel bawaan juga sudah dihapus. Impor
seperti `openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`,
seam helper berlabel channel, dan
`openclaw/plugin-sdk/telegram-core` adalah pintasan mono-repo privat, bukan
kontrak plugin yang stabil. Gunakan subpath SDK generik yang sempit sebagai gantinya. Di dalam
workspace plugin bawaan, simpan helper milik provider di `api.ts` atau `runtime-api.ts`
milik plugin tersebut.

Contoh provider bawaan saat ini:

- Anthropic menyimpan helper stream khusus Claude di seam `api.ts` /
  `contract-api.ts` miliknya sendiri
- OpenAI menyimpan builder provider, helper model default, dan builder provider
  realtime di `api.ts` miliknya sendiri
- OpenRouter menyimpan builder provider dan helper onboarding/config di
  `api.ts` miliknya sendiri

## Cara bermigrasi

<Steps>
  <Step title="Migrasikan handler native approval ke fakta capability">
    Plugin channel yang mendukung approval sekarang mengekspos perilaku approval native melalui
    `approvalCapability.nativeRuntime` ditambah registry runtime-context bersama.

    Perubahan utama:

    - Ganti `approvalCapability.handler.loadRuntime(...)` dengan
      `approvalCapability.nativeRuntime`
    - Pindahkan auth/pengiriman khusus approval dari wiring lama `plugin.auth` /
      `plugin.approvals` ke `approvalCapability`
    - `ChannelPlugin.approvals` telah dihapus dari kontrak publik
      plugin channel; pindahkan field delivery/native/render ke `approvalCapability`
    - `plugin.auth` tetap dipakai hanya untuk alur login/logout channel; hook auth
      approval di sana tidak lagi dibaca oleh core
    - Daftarkan objek runtime milik channel seperti client, token, atau aplikasi
      Bolt melalui `openclaw/plugin-sdk/channel-runtime-context`
    - Jangan kirim pemberitahuan reroute milik plugin dari handler approval native;
      core sekarang menangani pemberitahuan dialihkan-ke-tempat-lain dari hasil pengiriman yang sebenarnya
    - Saat meneruskan `channelRuntime` ke `createChannelManager(...)`, sediakan
      surface `createPluginRuntime().channel` yang nyata. Stub parsial akan ditolak.

    Lihat `/plugins/sdk-channel-plugins` untuk tata letak capability
    approval saat ini.

  </Step>

  <Step title="Audit perilaku fallback wrapper Windows">
    Jika plugin Anda menggunakan `openclaw/plugin-sdk/windows-spawn`, wrapper
    Windows `.cmd`/`.bat` yang tidak terpecahkan sekarang gagal tertutup kecuali Anda secara eksplisit meneruskan
    `allowShellFallback: true`.

    ```typescript
    // Sebelum
    const program = applyWindowsSpawnProgramPolicy({ candidate });

    // Sesudah
    const program = applyWindowsSpawnProgramPolicy({
      candidate,
      // Hanya setel ini untuk pemanggil kompatibilitas tepercaya yang secara sengaja
      // menerima fallback yang dimediasi shell.
      allowShellFallback: true,
    });
    ```

    Jika pemanggil Anda tidak secara sengaja bergantung pada shell fallback, jangan setel
    `allowShellFallback` dan tangani error yang dilempar sebagai gantinya.

  </Step>

  <Step title="Temukan impor deprecated">
    Cari plugin Anda untuk impor dari salah satu surface deprecated:

    ```bash
    grep -r "plugin-sdk/compat" my-plugin/
    grep -r "openclaw/extension-api" my-plugin/
    ```

  </Step>

  <Step title="Ganti dengan impor yang terfokus">
    Setiap ekspor dari surface lama dipetakan ke path impor modern tertentu:

    ```typescript
    // Sebelum (lapisan kompatibilitas mundur deprecated)
    import {
      createChannelReplyPipeline,
      createPluginRuntimeStore,
      resolveControlCommandGate,
    } from "openclaw/plugin-sdk/compat";

    // Sesudah (impor modern yang terfokus)
    import { createChannelReplyPipeline } from "openclaw/plugin-sdk/channel-reply-pipeline";
    import { createPluginRuntimeStore } from "openclaw/plugin-sdk/runtime-store";
    import { resolveControlCommandGate } from "openclaw/plugin-sdk/command-auth";
    ```

    Untuk helper sisi host, gunakan runtime plugin yang diinjeksi alih-alih mengimpor
    secara langsung:

    ```typescript
    // Sebelum (jembatan extension-api deprecated)
    import { runEmbeddedPiAgent } from "openclaw/extension-api";
    const result = await runEmbeddedPiAgent({ sessionId, prompt });

    // Sesudah (runtime yang diinjeksi)
    const result = await api.runtime.agent.runEmbeddedPiAgent({ sessionId, prompt });
    ```

    Pola yang sama berlaku untuk helper jembatan lama lainnya:

    | Impor lama | Padanan modern |
    | --- | --- |
    | `resolveAgentDir` | `api.runtime.agent.resolveAgentDir` |
    | `resolveAgentWorkspaceDir` | `api.runtime.agent.resolveAgentWorkspaceDir` |
    | `resolveAgentIdentity` | `api.runtime.agent.resolveAgentIdentity` |
    | `resolveThinkingDefault` | `api.runtime.agent.resolveThinkingDefault` |
    | `resolveAgentTimeoutMs` | `api.runtime.agent.resolveAgentTimeoutMs` |
    | `ensureAgentWorkspace` | `api.runtime.agent.ensureAgentWorkspace` |
    | helper session store | `api.runtime.agent.session.*` |

  </Step>

  <Step title="Build dan uji">
    ```bash
    pnpm build
    pnpm test -- my-plugin/
    ```
  </Step>
</Steps>

## Referensi path impor

<Accordion title="Tabel path impor umum">
  | Path impor | Tujuan | Ekspor utama |
  | --- | --- | --- |
  | `plugin-sdk/plugin-entry` | Helper entri plugin kanonis | `definePluginEntry` |
  | `plugin-sdk/core` | Ekspor ulang payung lama untuk definisi/builder entri channel | `defineChannelPluginEntry`, `createChatChannelPlugin` |
  | `plugin-sdk/config-schema` | Ekspor skema config root | `OpenClawSchema` |
  | `plugin-sdk/provider-entry` | Helper entri single-provider | `defineSingleProviderPluginEntry` |
  | `plugin-sdk/channel-core` | Definisi dan builder entri channel yang terfokus | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
  | `plugin-sdk/setup` | Helper wizard setup bersama | Prompt allowlist, builder status setup |
  | `plugin-sdk/setup-runtime` | Helper runtime saat setup | Adapter patch setup yang aman untuk impor, helper catatan lookup, `promptResolvedAllowFrom`, `splitSetupEntries`, proxy setup terdelegasi |
  | `plugin-sdk/setup-adapter-runtime` | Helper adapter setup | `createEnvPatchedAccountSetupAdapter` |
  | `plugin-sdk/setup-tools` | Helper tooling setup | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
  | `plugin-sdk/account-core` | Helper multi-account | Helper daftar/config/action-gate akun |
  | `plugin-sdk/account-id` | Helper account-id | `DEFAULT_ACCOUNT_ID`, normalisasi account-id |
  | `plugin-sdk/account-resolution` | Helper lookup akun | Helper lookup akun + fallback default |
  | `plugin-sdk/account-helpers` | Helper akun yang sempit | Helper daftar akun/action akun |
  | `plugin-sdk/channel-setup` | Adapter wizard setup | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, plus `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
  | `plugin-sdk/channel-pairing` | Primitive pairing DM | `createChannelPairingController` |
  | `plugin-sdk/channel-reply-pipeline` | Wiring prefiks balasan + pengetikan | `createChannelReplyPipeline` |
  | `plugin-sdk/channel-config-helpers` | Factory adapter config | `createHybridChannelConfigAdapter` |
  | `plugin-sdk/channel-config-schema` | Builder skema config | Tipe skema config channel |
  | `plugin-sdk/telegram-command-config` | Helper config perintah Telegram | Normalisasi nama perintah, pemangkasan deskripsi, validasi duplikasi/konflik |
  | `plugin-sdk/channel-policy` | Resolusi kebijakan grup/DM | `resolveChannelGroupRequireMention` |
  | `plugin-sdk/channel-lifecycle` | Pelacakan status akun | `createAccountStatusSink` |
  | `plugin-sdk/inbound-envelope` | Helper envelope inbound | Helper route bersama + builder envelope |
  | `plugin-sdk/inbound-reply-dispatch` | Helper balasan inbound | Helper record-and-dispatch bersama |
  | `plugin-sdk/messaging-targets` | Parsing target pesan | Helper parsing/pencocokan target |
  | `plugin-sdk/outbound-media` | Helper media outbound | Pemuatan media outbound bersama |
  | `plugin-sdk/outbound-runtime` | Helper runtime outbound | Helper identitas/delegasi pengiriman outbound |
  | `plugin-sdk/thread-bindings-runtime` | Helper thread-binding | Lifecycle thread-binding dan helper adapter |
  | `plugin-sdk/agent-media-payload` | Helper payload media lama | Builder payload media agent untuk tata letak field lama |
  | `plugin-sdk/channel-runtime` | Shim kompatibilitas deprecated | Hanya utilitas runtime channel lama |
  | `plugin-sdk/channel-send-result` | Tipe hasil kirim | Tipe hasil balasan |
  | `plugin-sdk/runtime-store` | Penyimpanan plugin persisten | `createPluginRuntimeStore` |
  | `plugin-sdk/runtime` | Helper runtime yang luas | Helper runtime/logging/backup/instalasi plugin |
  | `plugin-sdk/runtime-env` | Helper env runtime yang sempit | Helper logger/runtime env, timeout, retry, dan backoff |
  | `plugin-sdk/plugin-runtime` | Helper runtime plugin bersama | Helper perintah/hook/http/interaktif plugin |
  | `plugin-sdk/hook-runtime` | Helper pipeline hook | Helper pipeline webhook/internal hook bersama |
  | `plugin-sdk/lazy-runtime` | Helper runtime lazy | `createLazyRuntimeModule`, `createLazyRuntimeMethod`, `createLazyRuntimeMethodBinder`, `createLazyRuntimeNamedExport`, `createLazyRuntimeSurface` |
  | `plugin-sdk/process-runtime` | Helper proses | Helper exec bersama |
  | `plugin-sdk/cli-runtime` | Helper runtime CLI | Pemformatan perintah, wait, helper versi |
  | `plugin-sdk/gateway-runtime` | Helper gateway | Helper client gateway dan patch status channel |
  | `plugin-sdk/config-runtime` | Helper config | Helper load/write config |
  | `plugin-sdk/telegram-command-config` | Helper perintah Telegram | Helper validasi perintah Telegram yang stabil-fallback ketika surface kontrak Telegram bawaan tidak tersedia |
  | `plugin-sdk/approval-runtime` | Helper prompt approval | Payload approval exec/plugin, helper capability/profile approval, helper routing/runtime approval native |
  | `plugin-sdk/approval-auth-runtime` | Helper auth approval | Resolusi approver, auth aksi same-chat |
  | `plugin-sdk/approval-client-runtime` | Helper client approval | Helper profile/filter approval exec native |
  | `plugin-sdk/approval-delivery-runtime` | Helper pengiriman approval | Adapter capability/pengiriman approval native |
  | `plugin-sdk/approval-gateway-runtime` | Helper gateway approval | Helper resolusi-gateway approval bersama |
  | `plugin-sdk/approval-handler-adapter-runtime` | Helper adapter approval | Helper pemuatan adapter approval native yang ringan untuk entrypoint channel yang panas |
  | `plugin-sdk/approval-handler-runtime` | Helper handler approval | Helper runtime handler approval yang lebih luas; prioritaskan seam adapter/gateway yang lebih sempit bila itu sudah cukup |
  | `plugin-sdk/approval-native-runtime` | Helper target approval | Helper binding target/akun approval native |
  | `plugin-sdk/approval-reply-runtime` | Helper balasan approval | Helper payload balasan approval exec/plugin |
  | `plugin-sdk/channel-runtime-context` | Helper runtime-context channel | Helper register/get/watch runtime-context channel generik |
  | `plugin-sdk/security-runtime` | Helper keamanan | Helper trust, gating DM, konten eksternal, dan pengumpulan secret bersama |
  | `plugin-sdk/ssrf-policy` | Helper kebijakan SSRF | Helper allowlist host dan kebijakan jaringan privat |
  | `plugin-sdk/ssrf-runtime` | Helper runtime SSRF | Helper pinned-dispatcher, guarded fetch, kebijakan SSRF |
  | `plugin-sdk/collection-runtime` | Helper cache terbatas | `pruneMapToMaxSize` |
  | `plugin-sdk/diagnostic-runtime` | Helper gating diagnostik | `isDiagnosticFlagEnabled`, `isDiagnosticsEnabled` |
  | `plugin-sdk/error-runtime` | Helper pemformatan error | `formatUncaughtError`, `isApprovalNotFoundError`, helper grafik error |
  | `plugin-sdk/fetch-runtime` | Helper wrapped fetch/proxy | `resolveFetch`, helper proxy |
  | `plugin-sdk/host-runtime` | Helper normalisasi host | `normalizeHostname`, `normalizeScpRemoteHost` |
  | `plugin-sdk/retry-runtime` | Helper retry | `RetryConfig`, `retryAsync`, runner kebijakan |
  | `plugin-sdk/allow-from` | Pemformatan allowlist | `formatAllowFromLowercase` |
  | `plugin-sdk/allowlist-resolution` | Pemetaan input allowlist | `mapAllowlistResolutionInputs` |
  | `plugin-sdk/command-auth` | Gating perintah dan helper surface perintah | `resolveControlCommandGate`, helper otorisasi pengirim, helper registry perintah |
  | `plugin-sdk/secret-input` | Parsing input secret | Helper input secret |
  | `plugin-sdk/webhook-ingress` | Helper request webhook | Utilitas target webhook |
  | `plugin-sdk/webhook-request-guards` | Helper guard body webhook | Helper baca/batas body request |
  | `plugin-sdk/reply-runtime` | Runtime balasan bersama | Dispatch inbound, heartbeat, planner balasan, chunking |
  | `plugin-sdk/reply-dispatch-runtime` | Helper dispatch balasan yang sempit | Helper finalisasi + dispatch provider |
  | `plugin-sdk/reply-history` | Helper riwayat balasan | `buildHistoryContext`, `buildPendingHistoryContextFromMap`, `recordPendingHistoryEntry`, `clearHistoryEntriesIfEnabled` |
  | `plugin-sdk/reply-reference` | Perencanaan referensi balasan | `createReplyReferencePlanner` |
  | `plugin-sdk/reply-chunking` | Helper potongan balasan | Helper chunking teks/markdown |
  | `plugin-sdk/session-store-runtime` | Helper session store | Helper path store + updated-at |
  | `plugin-sdk/state-paths` | Helper path state | Helper direktori state dan OAuth |
  | `plugin-sdk/routing` | Helper routing/session-key | `resolveAgentRoute`, `buildAgentSessionKey`, `resolveDefaultAgentBoundAccountId`, helper normalisasi session-key |
  | `plugin-sdk/status-helpers` | Helper status channel | Builder ringkasan status channel/akun, default runtime-state, helper metadata issue |
  | `plugin-sdk/target-resolver-runtime` | Helper target resolver | Helper target resolver bersama |
  | `plugin-sdk/string-normalization-runtime` | Helper normalisasi string | Helper normalisasi slug/string |
  | `plugin-sdk/request-url` | Helper URL request | Mengekstrak URL string dari input mirip request |
  | `plugin-sdk/run-command` | Helper perintah bertempo | Runner perintah bertempo dengan stdout/stderr ternormalisasi |
  | `plugin-sdk/param-readers` | Pembaca parameter | Pembaca parameter tool/CLI umum |
  | `plugin-sdk/tool-payload` | Ekstraksi payload tool | Mengekstrak payload ternormalisasi dari objek hasil tool |
  | `plugin-sdk/tool-send` | Ekstraksi pengiriman tool | Mengekstrak field target kirim kanonis dari argumen tool |
  | `plugin-sdk/temp-path` | Helper path temp | Helper path unduhan sementara bersama |
  | `plugin-sdk/logging-core` | Helper logging | Helper logger subsistem dan redaksi |
  | `plugin-sdk/markdown-table-runtime` | Helper tabel markdown | Helper mode tabel markdown |
  | `plugin-sdk/reply-payload` | Tipe balasan pesan | Tipe payload balasan |
  | `plugin-sdk/provider-setup` | Helper setup provider lokal/self-hosted yang terkurasi | Helper penemuan/config provider self-hosted |
  | `plugin-sdk/self-hosted-provider-setup` | Helper setup provider self-hosted kompatibel OpenAI yang terfokus | Helper penemuan/config provider self-hosted yang sama |
  | `plugin-sdk/provider-auth-runtime` | Helper auth runtime provider | Helper resolusi API key runtime |
  | `plugin-sdk/provider-auth-api-key` | Helper setup API key provider | Helper onboarding/profile-write API key |
  | `plugin-sdk/provider-auth-result` | Helper hasil auth provider | Builder standar hasil auth OAuth |
  | `plugin-sdk/provider-auth-login` | Helper login interaktif provider | Helper login interaktif bersama |
  | `plugin-sdk/provider-env-vars` | Helper env var provider | Helper lookup env var auth provider |
  | `plugin-sdk/provider-model-shared` | Helper model/replay provider bersama | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, builder kebijakan replay bersama, helper endpoint provider, dan helper normalisasi model-id |
  | `plugin-sdk/provider-catalog-shared` | Helper katalog provider bersama | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
  | `plugin-sdk/provider-onboard` | Patch onboarding provider | Helper config onboarding |
  | `plugin-sdk/provider-http` | Helper HTTP provider | Helper kemampuan HTTP/endpoint provider generik |
  | `plugin-sdk/provider-web-fetch` | Helper web-fetch provider | Helper registrasi/cache provider web-fetch |
  | `plugin-sdk/provider-web-search-config-contract` | Helper config web-search provider | Helper config/kredensial web-search yang sempit untuk provider yang tidak memerlukan wiring enable plugin |
  | `plugin-sdk/provider-web-search-contract` | Helper kontrak web-search provider | Helper kontrak config/kredensial web-search yang sempit seperti `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig`, dan setter/getter kredensial terlingkup |
  | `plugin-sdk/provider-web-search` | Helper web-search provider | Helper registrasi/cache/runtime provider web-search |
  | `plugin-sdk/provider-tools` | Helper kompatibilitas tool/skema provider | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, pembersihan skema Gemini + diagnostik, dan helper kompatibilitas xAI seperti `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
  | `plugin-sdk/provider-usage` | Helper penggunaan provider | `fetchClaudeUsage`, `fetchGeminiUsage`, `fetchGithubCopilotUsage`, dan helper penggunaan provider lainnya |
  | `plugin-sdk/provider-stream` | Helper pembungkus stream provider | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipe pembungkus stream, dan helper pembungkus bersama Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
  | `plugin-sdk/keyed-async-queue` | Queue async terurut | `KeyedAsyncQueue` |
  | `plugin-sdk/media-runtime` | Helper media bersama | Helper fetch/transform/store media plus builder payload media |
  | `plugin-sdk/media-generation-runtime` | Helper pembuatan media bersama | Helper failover bersama, pemilihan kandidat, dan pesan model hilang untuk pembuatan gambar/video/musik |
  | `plugin-sdk/media-understanding` | Helper pemahaman media | Tipe provider pemahaman media plus ekspor helper gambar/audio untuk provider |
  | `plugin-sdk/text-runtime` | Helper teks bersama | Penghapusan teks yang terlihat oleh asisten, helper render/chunking/table markdown, helper redaksi, helper tag direktif, utilitas safe-text, dan helper teks/logging terkait |
  | `plugin-sdk/text-chunking` | Helper chunking teks | Helper chunking teks outbound |
  | `plugin-sdk/speech` | Helper speech | Tipe provider speech plus ekspor helper direktif, registry, dan validasi untuk provider |
  | `plugin-sdk/speech-core` | Inti speech bersama | Tipe provider speech, registry, direktif, normalisasi |
  | `plugin-sdk/realtime-transcription` | Helper transkripsi realtime | Tipe provider dan helper registry |
  | `plugin-sdk/realtime-voice` | Helper suara realtime | Tipe provider dan helper registry |
  | `plugin-sdk/image-generation-core` | Inti image-generation bersama | Tipe image-generation, failover, auth, dan helper registry |
  | `plugin-sdk/music-generation` | Helper music-generation | Tipe provider/request/result music-generation |
  | `plugin-sdk/music-generation-core` | Inti music-generation bersama | Tipe music-generation, helper failover, lookup provider, dan parsing model-ref |
  | `plugin-sdk/video-generation` | Helper video-generation | Tipe provider/request/result video-generation |
  | `plugin-sdk/video-generation-core` | Inti video-generation bersama | Tipe video-generation, helper failover, lookup provider, dan parsing model-ref |
  | `plugin-sdk/interactive-runtime` | Helper balasan interaktif | Normalisasi/reduksi payload balasan interaktif |
  | `plugin-sdk/channel-config-primitives` | Primitive config channel | Primitive channel config-schema yang sempit |
  | `plugin-sdk/channel-config-writes` | Helper penulisan config channel | Helper otorisasi penulisan config channel |
  | `plugin-sdk/channel-plugin-common` | Prelude channel bersama | Ekspor prelude plugin channel bersama |
  | `plugin-sdk/channel-status` | Helper status channel | Helper snapshot/ringkasan status channel bersama |
  | `plugin-sdk/allowlist-config-edit` | Helper config allowlist | Helper edit/baca config allowlist |
  | `plugin-sdk/group-access` | Helper akses grup | Helper keputusan akses grup bersama |
  | `plugin-sdk/direct-dm` | Helper DM langsung | Helper auth/guard DM langsung bersama |
  | `plugin-sdk/extension-shared` | Helper extension bersama | Primitive helper passive-channel/status dan ambient proxy |
  | `plugin-sdk/webhook-targets` | Helper target webhook | Registry target webhook dan helper pemasangan route |
  | `plugin-sdk/webhook-path` | Helper path webhook | Helper normalisasi path webhook |
  | `plugin-sdk/web-media` | Helper media web bersama | Helper pemuatan media jarak jauh/lokal |
  | `plugin-sdk/zod` | Ekspor ulang Zod | `zod` yang diekspor ulang untuk konsumen plugin SDK |
  | `plugin-sdk/memory-core` | Helper memory-core bawaan | Surface helper manajer/config/file/CLI memory |
  | `plugin-sdk/memory-core-engine-runtime` | Fasad runtime engine memory | Fasad runtime index/search memory |
  | `plugin-sdk/memory-core-host-engine-foundation` | Engine foundation host memory | Ekspor engine foundation host memory |
  | `plugin-sdk/memory-core-host-engine-embeddings` | Engine embedding host memory | Ekspor engine embedding host memory |
  | `plugin-sdk/memory-core-host-engine-qmd` | Engine QMD host memory | Ekspor engine QMD host memory |
  | `plugin-sdk/memory-core-host-engine-storage` | Engine penyimpanan host memory | Ekspor engine penyimpanan host memory |
  | `plugin-sdk/memory-core-host-multimodal` | Helper multimodal host memory | Helper multimodal host memory |
  | `plugin-sdk/memory-core-host-query` | Helper query host memory | Helper query host memory |
  | `plugin-sdk/memory-core-host-secret` | Helper secret host memory | Helper secret host memory |
  | `plugin-sdk/memory-core-host-events` | Helper jurnal event host memory | Helper jurnal event host memory |
  | `plugin-sdk/memory-core-host-status` | Helper status host memory | Helper status host memory |
  | `plugin-sdk/memory-core-host-runtime-cli` | Runtime CLI host memory | Helper runtime CLI host memory |
  | `plugin-sdk/memory-core-host-runtime-core` | Runtime inti host memory | Helper runtime inti host memory |
  | `plugin-sdk/memory-core-host-runtime-files` | Helper file/runtime host memory | Helper file/runtime host memory |
  | `plugin-sdk/memory-host-core` | Alias runtime inti host memory | Alias netral-vendor untuk helper runtime inti host memory |
  | `plugin-sdk/memory-host-events` | Alias jurnal event host memory | Alias netral-vendor untuk helper jurnal event host memory |
  | `plugin-sdk/memory-host-files` | Alias file/runtime host memory | Alias netral-vendor untuk helper file/runtime host memory |
  | `plugin-sdk/memory-host-markdown` | Helper markdown terkelola | Helper managed-markdown bersama untuk plugin yang berdekatan dengan memory |
  | `plugin-sdk/memory-host-search` | Fasad pencarian memory aktif | Fasad runtime search-manager active-memory lazy |
  | `plugin-sdk/memory-host-status` | Alias status host memory | Alias netral-vendor untuk helper status host memory |
  | `plugin-sdk/memory-lancedb` | Helper memory-lancedb bawaan | Surface helper memory-lancedb |
  | `plugin-sdk/testing` | Utilitas pengujian | Helper pengujian dan mock |
</Accordion>

Tabel ini sengaja merupakan subset migrasi umum, bukan seluruh
surface SDK. Daftar lengkap 200+ entrypoint ada di
`scripts/lib/plugin-sdk-entrypoints.json`.

Daftar itu masih mencakup beberapa seam helper bundled-plugin seperti
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, dan `plugin-sdk/matrix*`. Itu tetap diekspor untuk
pemeliharaan bundled-plugin dan kompatibilitas, tetapi sengaja
dihilangkan dari tabel migrasi umum dan bukan target yang direkomendasikan untuk
kode plugin baru.

Aturan yang sama berlaku untuk keluarga helper bawaan lainnya seperti:

- helper dukungan browser: `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support`
- Matrix: `plugin-sdk/matrix*`
- LINE: `plugin-sdk/line*`
- IRC: `plugin-sdk/irc*`
- surface helper/plugin bawaan seperti `plugin-sdk/googlechat`,
  `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles*`,
  `plugin-sdk/mattermost*`, `plugin-sdk/msteams`,
  `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`,
  `plugin-sdk/twitch`,
  `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`,
  `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`,
  `plugin-sdk/thread-ownership`, dan `plugin-sdk/voice-call`

`plugin-sdk/github-copilot-token` saat ini mengekspos
surface helper token yang sempit `DEFAULT_COPILOT_API_BASE_URL`,
`deriveCopilotApiBaseUrlFromToken`, dan `resolveCopilotApiToken`.

Gunakan impor tersempit yang sesuai dengan pekerjaan Anda. Jika Anda tidak dapat menemukan ekspor,
periksa source di `src/plugin-sdk/` atau tanyakan di Discord.

## Linimasa penghapusan

| Kapan                  | Apa yang terjadi                                                      |
| ---------------------- | --------------------------------------------------------------------- |
| **Sekarang**           | Surface deprecated mengeluarkan peringatan runtime                    |
| **Rilis mayor berikutnya** | Surface deprecated akan dihapus; plugin yang masih menggunakannya akan gagal |

Semua plugin core sudah dimigrasikan. Plugin eksternal sebaiknya bermigrasi
sebelum rilis mayor berikutnya.

## Menyembunyikan peringatan sementara

Setel variabel environment ini saat Anda sedang melakukan migrasi:

```bash
OPENCLAW_SUPPRESS_PLUGIN_SDK_COMPAT_WARNING=1 openclaw gateway run
OPENCLAW_SUPPRESS_EXTENSION_API_WARNING=1 openclaw gateway run
```

Ini adalah celah keluar sementara, bukan solusi permanen.

## Terkait

- [Getting Started](/id/plugins/building-plugins) — bangun plugin pertama Anda
- [SDK Overview](/id/plugins/sdk-overview) — referensi lengkap impor subpath
- [Channel Plugins](/id/plugins/sdk-channel-plugins) — membangun plugin channel
- [Provider Plugins](/id/plugins/sdk-provider-plugins) — membangun plugin provider
- [Plugin Internals](/id/plugins/architecture) — pendalaman arsitektur
- [Plugin Manifest](/id/plugins/manifest) — referensi skema manifest
