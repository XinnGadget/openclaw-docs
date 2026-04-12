---
read_when:
    - Menjalankan pengujian secara lokal atau di CI
    - Menambahkan regresi untuk bug model/provider
    - Men-debug perilaku gateway + agen
summary: 'Kit pengujian: suite unit/e2e/live, runner Docker, dan cakupan setiap pengujian'
title: Pengujian
x-i18n:
    generated_at: "2026-04-12T23:28:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: a66ea672c386094ab4a8035a082c8a85d508a14301ad44b628d2a10d9cec3a52
    source_path: help/testing.md
    workflow: 15
---

# Pengujian

OpenClaw memiliki tiga suite Vitest (unit/integrasi, e2e, live) dan sejumlah kecil runner Docker.

Dokumen ini adalah panduan “bagaimana kami menguji”:

- Apa yang dicakup oleh setiap suite (dan apa yang dengan sengaja _tidak_ dicakup)
- Perintah mana yang dijalankan untuk alur kerja umum (lokal, pra-push, debugging)
- Bagaimana pengujian live menemukan kredensial dan memilih model/provider
- Cara menambahkan regresi untuk masalah model/provider di dunia nyata

## Mulai cepat

Sebagian besar hari:

- Gate penuh (diharapkan sebelum push): `pnpm build && pnpm check && pnpm test`
- Eksekusi suite penuh lokal yang lebih cepat pada mesin yang lapang: `pnpm test:max`
- Loop watch Vitest langsung: `pnpm test:watch`
- Penargetan berkas langsung kini juga merutekan path extension/channel: `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts`
- Utamakan eksekusi tertarget terlebih dahulu saat Anda sedang mengiterasi satu kegagalan.
- Situs QA berbasis Docker: `pnpm qa:lab:up`
- Jalur QA berbasis VM Linux: `pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline`

Saat Anda menyentuh pengujian atau ingin keyakinan tambahan:

- Gate cakupan: `pnpm test:coverage`
- Suite E2E: `pnpm test:e2e`

Saat men-debug provider/model nyata (memerlukan kredensial nyata):

- Suite live (probe model + alat/gambar gateway): `pnpm test:live`
- Targetkan satu berkas live secara senyap: `pnpm test:live -- src/agents/models.profiles.live.test.ts`

Tips: saat Anda hanya membutuhkan satu kasus yang gagal, utamakan mempersempit pengujian live melalui env var allowlist yang dijelaskan di bawah.

## Runner khusus QA

Perintah-perintah ini berada di samping suite pengujian utama saat Anda membutuhkan realisme qa-lab:

- `pnpm openclaw qa suite`
  - Menjalankan skenario QA berbasis repo langsung pada host.
  - Menjalankan beberapa skenario terpilih secara paralel secara default dengan worker gateway yang terisolasi, hingga 64 worker atau jumlah skenario yang dipilih. Gunakan `--concurrency <count>` untuk menyetel jumlah worker, atau `--concurrency 1` untuk jalur serial yang lebih lama.
- `pnpm openclaw qa suite --runner multipass`
  - Menjalankan suite QA yang sama di dalam VM Linux Multipass sekali pakai.
  - Mempertahankan perilaku pemilihan skenario yang sama seperti `qa suite` pada host.
  - Menggunakan kembali flag pemilihan provider/model yang sama seperti `qa suite`.
  - Eksekusi live meneruskan input autentikasi QA yang didukung dan praktis untuk guest:
    kunci provider berbasis env, path konfigurasi provider live QA, dan `CODEX_HOME` bila ada.
  - Direktori output harus tetap berada di bawah root repo agar guest dapat menulis balik melalui workspace yang ter-mount.
  - Menulis laporan + ringkasan QA normal serta log Multipass di bawah
    `.artifacts/qa-e2e/...`.
- `pnpm qa:lab:up`
  - Memulai situs QA berbasis Docker untuk pekerjaan QA gaya operator.
- `pnpm openclaw qa matrix`
  - Menjalankan jalur QA live Matrix terhadap homeserver Tuwunel berbasis Docker sekali pakai.
  - Menyediakan tiga pengguna Matrix sementara (`driver`, `sut`, `observer`) plus satu room privat, lalu memulai child gateway QA dengan Plugin Matrix nyata sebagai transport SUT.
  - Secara default menggunakan image Tuwunel stabil yang dipin `ghcr.io/matrix-construct/tuwunel:v1.5.1`. Timpa dengan `OPENCLAW_QA_MATRIX_TUWUNEL_IMAGE` saat Anda perlu menguji image yang berbeda.
  - Menulis laporan QA Matrix, ringkasan, dan artefak observed-events di bawah `.artifacts/qa-e2e/...`.
- `pnpm openclaw qa telegram`
  - Menjalankan jalur QA live Telegram terhadap grup privat nyata menggunakan token bot driver dan SUT dari env.
  - Memerlukan `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`, dan `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`. ID grup harus berupa chat id Telegram numerik.
  - Memerlukan dua bot yang berbeda dalam grup privat yang sama, dengan bot SUT mengekspos username Telegram.
  - Untuk observasi bot-ke-bot yang stabil, aktifkan Bot-to-Bot Communication Mode di `@BotFather` untuk kedua bot dan pastikan bot driver dapat mengamati lalu lintas bot grup.
  - Menulis laporan QA Telegram, ringkasan, dan artefak observed-messages di bawah `.artifacts/qa-e2e/...`.

Jalur transport live berbagi satu kontrak standar agar transport baru tidak menyimpang:

`qa-channel` tetap menjadi suite QA sintetis yang luas dan bukan bagian dari matriks cakupan transport live.

| Jalur    | Canary | Penyaringan mention | Blok allowlist | Balasan tingkat atas | Lanjutkan setelah restart | Tindak lanjut thread | Isolasi thread | Observasi reaction | Perintah help |
| -------- | ------ | ------------------- | -------------- | -------------------- | ------------------------- | -------------------- | -------------- | ------------------ | ------------- |
| Matrix   | x      | x                   | x              | x                    | x                         | x                    | x              | x                  |               |
| Telegram | x      |                     |                |                      |                           |                      |                |                    | x             |

### Menambahkan channel ke QA

Menambahkan channel ke sistem QA markdown memerlukan tepat dua hal:

1. Adapter transport untuk channel tersebut.
2. Paket skenario yang menjalankan kontrak channel.

Jangan tambahkan runner QA khusus channel ketika runner bersama `qa-lab` dapat
menangani alurnya.

`qa-lab` memiliki mekanisme bersama:

- startup dan teardown suite
- konkurensi worker
- penulisan artefak
- pembuatan laporan
- eksekusi skenario
- alias kompatibilitas untuk skenario `qa-channel` yang lebih lama

Adapter channel memiliki kontrak transport:

- bagaimana gateway dikonfigurasi untuk transport tersebut
- bagaimana kesiapan diperiksa
- bagaimana peristiwa masuk disuntikkan
- bagaimana pesan keluar diamati
- bagaimana transkrip dan status transport ternormalisasi diekspos
- bagaimana tindakan berbasis transport dijalankan
- bagaimana reset atau pembersihan khusus transport ditangani

Batas adopsi minimum untuk channel baru adalah:

1. Implementasikan adapter transport pada seam `qa-lab` bersama.
2. Daftarkan adapter di registri transport.
3. Simpan mekanisme khusus transport di dalam adapter atau harness channel.
4. Tulis atau adaptasi skenario markdown di bawah `qa/scenarios/`.
5. Gunakan helper skenario generik untuk skenario baru.
6. Pertahankan alias kompatibilitas yang ada tetap berfungsi kecuali repo sedang melakukan migrasi yang disengaja.

Aturan keputusannya ketat:

- Jika perilaku dapat diekspresikan sekali di `qa-lab`, letakkan di `qa-lab`.
- Jika perilaku bergantung pada satu transport channel, simpan di adapter atau harness Plugin tersebut.
- Jika sebuah skenario memerlukan kemampuan baru yang dapat digunakan oleh lebih dari satu channel, tambahkan helper generik alih-alih cabang khusus channel di `suite.ts`.
- Jika suatu perilaku hanya bermakna untuk satu transport, pertahankan skenario tetap khusus transport dan nyatakan itu secara eksplisit dalam kontrak skenario.

Nama helper generik yang diutamakan untuk skenario baru adalah:

- `waitForTransportReady`
- `waitForChannelReady`
- `injectInboundMessage`
- `injectOutboundMessage`
- `waitForTransportOutboundMessage`
- `waitForChannelOutboundMessage`
- `waitForNoTransportOutbound`
- `getTransportSnapshot`
- `readTransportMessage`
- `readTransportTranscript`
- `formatTransportTranscript`
- `resetTransport`

Alias kompatibilitas tetap tersedia untuk skenario yang ada, termasuk:

- `waitForQaChannelReady`
- `waitForOutboundMessage`
- `waitForNoOutbound`
- `formatConversationTranscript`
- `resetBus`

Pekerjaan channel baru sebaiknya menggunakan nama helper generik.
Alias kompatibilitas ada untuk menghindari migrasi flag day, bukan sebagai model untuk
penulisan skenario baru.

## Suite pengujian (apa yang berjalan di mana)

Anggap suite sebagai “realisme yang meningkat” (dan peningkatan flaky/biaya):

### Unit / integrasi (default)

- Perintah: `pnpm test`
- Konfigurasi: sepuluh eksekusi shard berurutan (`vitest.full-*.config.ts`) di atas project Vitest terbatas yang sudah ada
- Berkas: inventaris core/unit di bawah `src/**/*.test.ts`, `packages/**/*.test.ts`, `test/**/*.test.ts`, dan pengujian node `ui` yang di-whitelist yang dicakup oleh `vitest.unit.config.ts`
- Cakupan:
  - Pengujian unit murni
  - Pengujian integrasi in-process (autentikasi gateway, routing, tooling, parsing, config)
  - Regresi deterministik untuk bug yang diketahui
- Ekspektasi:
  - Berjalan di CI
  - Tidak memerlukan kunci nyata
  - Harus cepat dan stabil
- Catatan project:
  - `pnpm test` tanpa target kini menjalankan sebelas konfigurasi shard yang lebih kecil (`core-unit-src`, `core-unit-security`, `core-unit-ui`, `core-unit-support`, `core-support-boundary`, `core-contracts`, `core-bundled`, `core-runtime`, `agentic`, `auto-reply`, `extensions`) alih-alih satu proses root-project native yang besar. Ini memangkas puncak RSS pada mesin yang sedang terbebani dan mencegah pekerjaan auto-reply/extension membuat suite lain yang tidak terkait kelaparan sumber daya.
  - `pnpm test --watch` tetap menggunakan graf project native root `vitest.config.ts`, karena loop watch multi-shard tidak praktis.
  - `pnpm test`, `pnpm test:watch`, dan `pnpm test:perf:imports` merutekan target berkas/direktori eksplisit melalui jalur terbatas terlebih dahulu, sehingga `pnpm test extensions/discord/src/monitor/message-handler.preflight.test.ts` tidak perlu membayar biaya startup penuh root project.
  - `pnpm test:changed` memperluas path git yang berubah ke jalur terbatas yang sama ketika diff hanya menyentuh berkas source/test yang dapat dirutekan; edit config/setup tetap fallback ke eksekusi ulang root-project yang luas.
  - Pengujian unit ringan impor dari agents, commands, plugins, helper auto-reply, `plugin-sdk`, dan area utilitas murni serupa dirutekan melalui jalur `unit-fast`, yang melewati `test/setup-openclaw-runtime.ts`; berkas yang stateful/runtime-berat tetap berada di jalur yang ada.
  - Sejumlah berkas source helper `plugin-sdk` dan `commands` yang dipilih juga memetakan eksekusi mode-changed ke pengujian saudara eksplisit di jalur ringan tersebut, sehingga edit helper tidak memicu eksekusi ulang seluruh suite berat untuk direktori itu.
  - `auto-reply` kini memiliki tiga bucket khusus: helper core tingkat atas, pengujian integrasi `reply.*` tingkat atas, dan subtree `src/auto-reply/reply/**`. Ini menjaga pekerjaan harness reply terberat tetap terpisah dari pengujian status/chunk/token yang murah.
- Catatan runner tersemat:
  - Saat Anda mengubah input penemuan message-tool atau konteks runtime Compaction,
    pertahankan kedua tingkat cakupan.
  - Tambahkan regresi helper yang terfokus untuk batas routing/normalisasi murni.
  - Juga pertahankan suite integrasi runner tersemat tetap sehat:
    `src/agents/pi-embedded-runner/compact.hooks.test.ts`,
    `src/agents/pi-embedded-runner/run.overflow-compaction.test.ts`, dan
    `src/agents/pi-embedded-runner/run.overflow-compaction.loop.test.ts`.
  - Suite tersebut memverifikasi bahwa id terbatas dan perilaku Compaction tetap mengalir
    melalui jalur nyata `run.ts` / `compact.ts`; pengujian helper saja bukan
    pengganti yang memadai untuk jalur integrasi tersebut.
- Catatan pool:
  - Konfigurasi dasar Vitest kini default ke `threads`.
  - Konfigurasi Vitest bersama juga menetapkan `isolate: false` dan menggunakan runner non-isolated di seluruh root projects, config e2e, dan live.
  - Jalur UI root mempertahankan setup dan optimizer `jsdom`, tetapi kini juga berjalan pada runner non-isolated bersama.
  - Setiap shard `pnpm test` mewarisi default `threads` + `isolate: false` yang sama dari konfigurasi Vitest bersama.
  - Launcher bersama `scripts/run-vitest.mjs` kini juga menambahkan `--no-maglev` untuk proses child Node Vitest secara default untuk mengurangi churn kompilasi V8 selama eksekusi lokal besar. Setel `OPENCLAW_VITEST_ENABLE_MAGLEV=1` jika Anda perlu membandingkannya dengan perilaku V8 bawaan.
- Catatan iterasi lokal cepat:
  - `pnpm test:changed` merutekan melalui jalur terbatas ketika path yang berubah dipetakan dengan bersih ke suite yang lebih kecil.
  - `pnpm test:max` dan `pnpm test:changed:max` mempertahankan perilaku routing yang sama, hanya dengan batas worker yang lebih tinggi.
  - Auto-scaling worker lokal sekarang sengaja lebih konservatif dan juga mundur ketika rata-rata beban host sudah tinggi, sehingga beberapa eksekusi Vitest bersamaan secara default menimbulkan dampak yang lebih kecil.
  - Konfigurasi dasar Vitest menandai project/berkas config sebagai `forceRerunTriggers` sehingga eksekusi ulang mode-changed tetap benar saat wiring pengujian berubah.
  - Konfigurasi tersebut mempertahankan `OPENCLAW_VITEST_FS_MODULE_CACHE` tetap aktif pada host yang didukung; setel `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/abs/path` jika Anda menginginkan satu lokasi cache eksplisit untuk profiling langsung.
- Catatan debug performa:
  - `pnpm test:perf:imports` mengaktifkan pelaporan durasi impor Vitest beserta output rincian impor.
  - `pnpm test:perf:imports:changed` membatasi tampilan profiling yang sama ke berkas yang berubah sejak `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` membandingkan `test:changed` yang dirutekan dengan jalur native root-project untuk diff yang sudah di-commit itu dan mencetak wall time plus RSS maksimum macOS.
- `pnpm test:perf:changed:bench -- --worktree` membenchmark tree kotor saat ini dengan merutekan daftar berkas yang berubah melalui `scripts/test-projects.mjs` dan konfigurasi root Vitest.
  - `pnpm test:perf:profile:main` menulis profil CPU main-thread untuk overhead startup dan transformasi Vitest/Vite.
  - `pnpm test:perf:profile:runner` menulis profil CPU+heap runner untuk suite unit dengan paralelisme berkas dinonaktifkan.

### E2E (smoke gateway)

- Perintah: `pnpm test:e2e`
- Konfigurasi: `vitest.e2e.config.ts`
- Berkas: `src/**/*.e2e.test.ts`, `test/**/*.e2e.test.ts`
- Default runtime:
  - Menggunakan Vitest `threads` dengan `isolate: false`, sesuai dengan bagian repo lainnya.
  - Menggunakan worker adaptif (CI: hingga 2, lokal: 1 secara default).
  - Berjalan dalam mode senyap secara default untuk mengurangi overhead I/O konsol.
- Override yang berguna:
  - `OPENCLAW_E2E_WORKERS=<n>` untuk memaksa jumlah worker (dibatasi hingga 16).
  - `OPENCLAW_E2E_VERBOSE=1` untuk mengaktifkan kembali output konsol verbose.
- Cakupan:
  - Perilaku end-to-end gateway multi-instance
  - Surface WebSocket/HTTP, pairing Node, dan jaringan yang lebih berat
- Ekspektasi:
  - Berjalan di CI (saat diaktifkan di pipeline)
  - Tidak memerlukan kunci nyata
  - Lebih banyak bagian bergerak dibanding pengujian unit (bisa lebih lambat)

### E2E: smoke backend OpenShell

- Perintah: `pnpm test:e2e:openshell`
- Berkas: `test/openshell-sandbox.e2e.test.ts`
- Cakupan:
  - Memulai gateway OpenShell terisolasi pada host melalui Docker
  - Membuat sandbox dari Dockerfile lokal sementara
  - Menjalankan backend OpenShell milik OpenClaw melalui `sandbox ssh-config` + SSH exec nyata
  - Memverifikasi perilaku filesystem remote-canonical melalui bridge fs sandbox
- Ekspektasi:
  - Hanya opt-in; bukan bagian dari eksekusi default `pnpm test:e2e`
  - Memerlukan CLI `openshell` lokal plus daemon Docker yang berfungsi
  - Menggunakan `HOME` / `XDG_CONFIG_HOME` terisolasi, lalu menghancurkan gateway pengujian dan sandbox
- Override yang berguna:
  - `OPENCLAW_E2E_OPENSHELL=1` untuk mengaktifkan pengujian saat menjalankan suite e2e yang lebih luas secara manual
  - `OPENCLAW_E2E_OPENSHELL_COMMAND=/path/to/openshell` untuk menunjuk ke biner CLI atau wrapper script non-default

### Live (provider nyata + model nyata)

- Perintah: `pnpm test:live`
- Konfigurasi: `vitest.live.config.ts`
- Berkas: `src/**/*.live.test.ts`
- Default: **diaktifkan** oleh `pnpm test:live` (menetapkan `OPENCLAW_LIVE_TEST=1`)
- Cakupan:
  - “Apakah provider/model ini benar-benar bekerja _hari ini_ dengan kredensial nyata?”
  - Menangkap perubahan format provider, kekhasan pemanggilan alat, masalah autentikasi, dan perilaku rate limit
- Ekspektasi:
  - Secara desain tidak stabil untuk CI (jaringan nyata, kebijakan provider nyata, kuota, outage)
  - Menghabiskan biaya / menggunakan rate limit
  - Utamakan menjalankan subset yang dipersempit, bukan “semuanya”
- Eksekusi live melakukan source `~/.profile` untuk mengambil API key yang hilang.
- Secara default, eksekusi live tetap mengisolasi `HOME` dan menyalin materi config/auth ke home pengujian sementara sehingga fixture unit tidak dapat mengubah `~/.openclaw` Anda yang nyata.
- Setel `OPENCLAW_LIVE_USE_REAL_HOME=1` hanya saat Anda memang sengaja perlu pengujian live menggunakan direktori home nyata Anda.
- `pnpm test:live` kini default ke mode yang lebih senyap: tetap mempertahankan output progres `[live] ...`, tetapi menekan notifikasi `~/.profile` tambahan dan membisukan log bootstrap gateway/obrolan Bonjour. Setel `OPENCLAW_LIVE_TEST_QUIET=0` jika Anda ingin log startup penuh kembali.
- Rotasi API key (khusus provider): setel `*_API_KEYS` dengan format koma/titik koma atau `*_API_KEY_1`, `*_API_KEY_2` (misalnya `OPENAI_API_KEYS`, `ANTHROPIC_API_KEYS`, `GEMINI_API_KEYS`) atau override per-live melalui `OPENCLAW_LIVE_*_KEY`; pengujian akan mencoba ulang pada respons rate limit.
- Output progres/Heartbeat:
  - Suite live kini memancarkan baris progres ke stderr sehingga pemanggilan provider yang lama tampak tetap aktif bahkan saat penangkapan konsol Vitest sedang senyap.
  - `vitest.live.config.ts` menonaktifkan intersepsi konsol Vitest sehingga baris progres provider/gateway mengalir segera selama eksekusi live.
  - Atur Heartbeat model langsung dengan `OPENCLAW_LIVE_HEARTBEAT_MS`.
  - Atur Heartbeat gateway/probe dengan `OPENCLAW_LIVE_GATEWAY_HEARTBEAT_MS`.

## Suite mana yang sebaiknya saya jalankan?

Gunakan tabel keputusan ini:

- Mengedit logika/pengujian: jalankan `pnpm test` (dan `pnpm test:coverage` jika Anda mengubah banyak hal)
- Menyentuh jaringan gateway / protokol WS / pairing: tambahkan `pnpm test:e2e`
- Men-debug “bot saya mati” / kegagalan khusus provider / pemanggilan alat: jalankan `pnpm test:live` yang dipersempit

## Live: sweep kapabilitas Node Android

- Pengujian: `src/gateway/android-node.capabilities.live.test.ts`
- Script: `pnpm android:test:integration`
- Tujuan: memanggil **setiap perintah yang saat ini diiklankan** oleh Node Android yang terhubung dan menegaskan perilaku kontrak perintah.
- Cakupan:
  - Setup prasyarat/manual (suite tidak memasang/menjalankan/melakukan pairing aplikasi).
  - Validasi `node.invoke` gateway per perintah untuk Node Android yang dipilih.
- Pra-setup yang diwajibkan:
  - Aplikasi Android sudah terhubung + dipairing ke gateway.
  - Aplikasi tetap berada di foreground.
  - Izin/persetujuan capture diberikan untuk kapabilitas yang Anda harapkan lolos.
- Override target opsional:
  - `OPENCLAW_ANDROID_NODE_ID` atau `OPENCLAW_ANDROID_NODE_NAME`.
  - `OPENCLAW_ANDROID_GATEWAY_URL` / `OPENCLAW_ANDROID_GATEWAY_TOKEN` / `OPENCLAW_ANDROID_GATEWAY_PASSWORD`.
- Detail setup Android lengkap: [Android App](/id/platforms/android)

## Live: smoke model (kunci profil)

Pengujian live dibagi menjadi dua lapisan agar kita dapat mengisolasi kegagalan:

- “Model langsung” memberi tahu kita apakah provider/model dapat menjawab sama sekali dengan kunci yang diberikan.
- “Smoke gateway” memberi tahu kita apakah pipeline penuh gateway+agen bekerja untuk model tersebut (sesi, riwayat, alat, kebijakan sandbox, dll.).

### Lapisan 1: penyelesaian model langsung (tanpa gateway)

- Pengujian: `src/agents/models.profiles.live.test.ts`
- Tujuan:
  - Menginventarisasi model yang ditemukan
  - Menggunakan `getApiKeyForModel` untuk memilih model yang Anda miliki kredensialnya
  - Menjalankan completion kecil per model (dan regresi tertarget bila diperlukan)
- Cara mengaktifkan:
  - `pnpm test:live` (atau `OPENCLAW_LIVE_TEST=1` jika memanggil Vitest secara langsung)
- Setel `OPENCLAW_LIVE_MODELS=modern` (atau `all`, alias untuk modern) untuk benar-benar menjalankan suite ini; jika tidak, suite akan dilewati agar `pnpm test:live` tetap fokus pada smoke gateway
- Cara memilih model:
  - `OPENCLAW_LIVE_MODELS=modern` untuk menjalankan allowlist modern (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_MODELS=all` adalah alias untuk allowlist modern
  - atau `OPENCLAW_LIVE_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,..."` (allowlist dipisahkan koma)
  - Sweep modern/all secara default menggunakan batas high-signal yang dikurasi; setel `OPENCLAW_LIVE_MAX_MODELS=0` untuk sweep modern yang menyeluruh atau angka positif untuk batas yang lebih kecil.
- Cara memilih provider:
  - `OPENCLAW_LIVE_PROVIDERS="google,google-antigravity,google-gemini-cli"` (allowlist dipisahkan koma)
- Asal kunci:
  - Secara default: profile store dan fallback env
  - Setel `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` untuk memaksa hanya **profile store**
- Alasan ini ada:
  - Memisahkan “API provider rusak / kunci tidak valid” dari “pipeline agen gateway rusak”
  - Menampung regresi kecil dan terisolasi (contoh: replay penalaran OpenAI Responses/Codex Responses + alur pemanggilan alat)

### Lapisan 2: smoke gateway + agen dev (apa yang sebenarnya dilakukan `@openclaw`)

- Pengujian: `src/gateway/gateway-models.profiles.live.test.ts`
- Tujuan:
  - Menyalakan gateway in-process
  - Membuat/menambal sesi `agent:dev:*` (override model per eksekusi)
  - Mengiterasi model-dengan-kunci dan menegaskan:
    - respons yang “bermakna” (tanpa alat)
    - pemanggilan alat nyata berfungsi (probe read)
    - probe alat tambahan opsional (probe exec+read)
    - jalur regresi OpenAI (hanya-pemanggilan-alat → tindak lanjut) tetap berfungsi
- Detail probe (agar Anda dapat menjelaskan kegagalan dengan cepat):
  - probe `read`: pengujian menulis berkas nonce di workspace lalu meminta agen untuk `read` berkas tersebut dan menggaungkan nonce kembali.
  - probe `exec+read`: pengujian meminta agen untuk menulis nonce ke berkas sementara lewat `exec`, lalu membacanya kembali lewat `read`.
  - probe gambar: pengujian melampirkan PNG yang dihasilkan (kucing + kode acak) dan mengharapkan model mengembalikan `cat <CODE>`.
  - Referensi implementasi: `src/gateway/gateway-models.profiles.live.test.ts` dan `src/gateway/live-image-probe.ts`.
- Cara mengaktifkan:
  - `pnpm test:live` (atau `OPENCLAW_LIVE_TEST=1` jika memanggil Vitest secara langsung)
- Cara memilih model:
  - Default: allowlist modern (Opus/Sonnet 4.6+, GPT-5.x + Codex, Gemini 3, GLM 4.7, MiniMax M2.7, Grok 4)
  - `OPENCLAW_LIVE_GATEWAY_MODELS=all` adalah alias untuk allowlist modern
  - Atau setel `OPENCLAW_LIVE_GATEWAY_MODELS="provider/model"` (atau daftar dipisahkan koma) untuk mempersempit
  - Sweep gateway modern/all secara default menggunakan batas high-signal yang dikurasi; setel `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=0` untuk sweep modern yang menyeluruh atau angka positif untuk batas yang lebih kecil.
- Cara memilih provider (hindari “semua OpenRouter”):
  - `OPENCLAW_LIVE_GATEWAY_PROVIDERS="google,google-antigravity,google-gemini-cli,openai,anthropic,zai,minimax"` (allowlist dipisahkan koma)
- Probe alat + gambar selalu aktif dalam pengujian live ini:
  - probe `read` + probe `exec+read` (stress alat)
  - probe gambar berjalan saat model mengiklankan dukungan input gambar
  - Alur (tingkat tinggi):
    - Pengujian menghasilkan PNG kecil dengan “CAT” + kode acak (`src/gateway/live-image-probe.ts`)
    - Mengirimkannya melalui `agent` `attachments: [{ mimeType: "image/png", content: "<base64>" }]`
    - Gateway mem-parsing lampiran ke `images[]` (`src/gateway/server-methods/agent.ts` + `src/gateway/chat-attachments.ts`)
    - Agen tersemat meneruskan pesan pengguna multimodal ke model
    - Penegasan: balasan berisi `cat` + kodenya (toleransi OCR: kesalahan kecil diperbolehkan)

Tips: untuk melihat apa yang dapat Anda uji di mesin Anda (dan id `provider/model` yang tepat), jalankan:

```bash
openclaw models list
openclaw models list --json
```

## Live: smoke backend CLI (Claude, Codex, Gemini, atau CLI lokal lain)

- Pengujian: `src/gateway/gateway-cli-backend.live.test.ts`
- Tujuan: memvalidasi pipeline Gateway + agen menggunakan backend CLI lokal, tanpa menyentuh config default Anda.
- Default smoke khusus backend berada bersama definisi `cli-backend.ts` milik extension pemiliknya.
- Aktifkan:
  - `pnpm test:live` (atau `OPENCLAW_LIVE_TEST=1` jika memanggil Vitest secara langsung)
  - `OPENCLAW_LIVE_CLI_BACKEND=1`
- Default:
  - Provider/model default: `claude-cli/claude-sonnet-4-6`
  - Perilaku command/args/gambar berasal dari metadata Plugin backend CLI pemiliknya.
- Override (opsional):
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4"`
  - `OPENCLAW_LIVE_CLI_BACKEND_COMMAND="/full/path/to/codex"`
  - `OPENCLAW_LIVE_CLI_BACKEND_ARGS='["exec","--json","--color","never","--sandbox","read-only","--skip-git-repo-check"]'`
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_PROBE=1` untuk mengirim lampiran gambar nyata (path disuntikkan ke prompt).
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_ARG="--image"` untuk meneruskan path berkas gambar sebagai argumen CLI alih-alih injeksi prompt.
  - `OPENCLAW_LIVE_CLI_BACKEND_IMAGE_MODE="repeat"` (atau `"list"`) untuk mengontrol bagaimana argumen gambar diteruskan saat `IMAGE_ARG` disetel.
  - `OPENCLAW_LIVE_CLI_BACKEND_RESUME_PROBE=1` untuk mengirim giliran kedua dan memvalidasi alur resume.
  - `OPENCLAW_LIVE_CLI_BACKEND_MODEL_SWITCH_PROBE=0` untuk menonaktifkan probe kontinuitas sesi yang sama Claude Sonnet -> Opus default (setel ke `1` untuk memaksanya aktif saat model yang dipilih mendukung target perpindahan).

Contoh:

```bash
OPENCLAW_LIVE_CLI_BACKEND=1 \
  OPENCLAW_LIVE_CLI_BACKEND_MODEL="codex-cli/gpt-5.4" \
  pnpm test:live src/gateway/gateway-cli-backend.live.test.ts
```

Resep Docker:

```bash
pnpm test:docker:live-cli-backend
```

Resep Docker provider tunggal:

```bash
pnpm test:docker:live-cli-backend:claude
pnpm test:docker:live-cli-backend:claude-subscription
pnpm test:docker:live-cli-backend:codex
pnpm test:docker:live-cli-backend:gemini
```

Catatan:

- Runner Docker berada di `scripts/test-live-cli-backend-docker.sh`.
- Runner ini menjalankan smoke CLI-backend live di dalam image Docker repo sebagai pengguna non-root `node`.
- Runner ini menyelesaikan metadata smoke CLI dari extension pemiliknya, lalu memasang paket CLI Linux yang cocok (`@anthropic-ai/claude-code`, `@openai/codex`, atau `@google/gemini-cli`) ke prefix writable yang di-cache di `OPENCLAW_DOCKER_CLI_TOOLS_DIR` (default: `~/.cache/openclaw/docker-cli-tools`).
- `pnpm test:docker:live-cli-backend:claude-subscription` memerlukan OAuth subscription Claude Code portabel melalui `~/.claude/.credentials.json` dengan `claudeAiOauth.subscriptionType` atau `CLAUDE_CODE_OAUTH_TOKEN` dari `claude setup-token`. Runner ini pertama-tama membuktikan `claude -p` langsung di Docker, lalu menjalankan dua giliran Gateway CLI-backend tanpa mempertahankan env API key Anthropic. Jalur subscription ini menonaktifkan probe alat/gambar Claude MCP secara default karena Claude saat ini merutekan penggunaan aplikasi pihak ketiga melalui penagihan extra-usage alih-alih batas paket subscription normal.
- Smoke CLI-backend live sekarang menjalankan alur end-to-end yang sama untuk Claude, Codex, dan Gemini: giliran teks, giliran klasifikasi gambar, lalu pemanggilan alat MCP `cron` yang diverifikasi melalui CLI gateway.
- Smoke default Claude juga menambal sesi dari Sonnet ke Opus dan memverifikasi sesi yang di-resume masih mengingat catatan sebelumnya.

## Live: smoke bind ACP (`/acp spawn ... --bind here`)

- Pengujian: `src/gateway/gateway-acp-bind.live.test.ts`
- Tujuan: memvalidasi alur bind percakapan ACP nyata dengan agen ACP live:
  - kirim `/acp spawn <agent> --bind here`
  - bind percakapan channel-pesan sintetis di tempat
  - kirim tindak lanjut normal pada percakapan yang sama
  - verifikasi tindak lanjut masuk ke transkrip sesi ACP yang terikat
- Aktifkan:
  - `pnpm test:live src/gateway/gateway-acp-bind.live.test.ts`
  - `OPENCLAW_LIVE_ACP_BIND=1`
- Default:
  - Agen ACP di Docker: `claude,codex,gemini`
  - Agen ACP untuk `pnpm test:live ...` langsung: `claude`
  - Channel sintetis: konteks percakapan gaya DM Slack
  - Backend ACP: `acpx`
- Override:
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=claude`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=codex`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT=gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude,codex,gemini`
  - `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND='npx -y @agentclientprotocol/claude-agent-acp@<version>'`
- Catatan:
  - Jalur ini menggunakan surface `chat.send` gateway dengan field originating-route sintetis khusus admin sehingga pengujian dapat melampirkan konteks channel pesan tanpa berpura-pura mengirimkan secara eksternal.
  - Saat `OPENCLAW_LIVE_ACP_BIND_AGENT_COMMAND` tidak disetel, pengujian menggunakan registri agen bawaan Plugin `acpx` tersemat untuk agen harness ACP yang dipilih.

Contoh:

```bash
OPENCLAW_LIVE_ACP_BIND=1 \
  OPENCLAW_LIVE_ACP_BIND_AGENT=claude \
  pnpm test:live src/gateway/gateway-acp-bind.live.test.ts
```

Resep Docker:

```bash
pnpm test:docker:live-acp-bind
```

Resep Docker agen tunggal:

```bash
pnpm test:docker:live-acp-bind:claude
pnpm test:docker:live-acp-bind:codex
pnpm test:docker:live-acp-bind:gemini
```

Catatan Docker:

- Runner Docker berada di `scripts/test-live-acp-bind-docker.sh`.
- Secara default, runner ini menjalankan smoke bind ACP terhadap semua agen CLI live yang didukung secara berurutan: `claude`, `codex`, lalu `gemini`.
- Gunakan `OPENCLAW_LIVE_ACP_BIND_AGENTS=claude`, `OPENCLAW_LIVE_ACP_BIND_AGENTS=codex`, atau `OPENCLAW_LIVE_ACP_BIND_AGENTS=gemini` untuk mempersempit matriks.
- Runner ini melakukan source `~/.profile`, men-stage materi autentikasi CLI yang cocok ke dalam container, memasang `acpx` ke prefix npm writable, lalu memasang CLI live yang diminta (`@anthropic-ai/claude-code`, `@openai/codex`, atau `@google/gemini-cli`) jika belum ada.
- Di dalam Docker, runner menetapkan `OPENCLAW_LIVE_ACP_BIND_ACPX_COMMAND=$HOME/.npm-global/bin/acpx` sehingga acpx mempertahankan env provider dari profile yang di-source tetap tersedia untuk CLI child harness.

## Live: smoke harness app-server Codex

- Tujuan: memvalidasi harness Codex milik Plugin melalui metode gateway
  `agent` normal:
  - muat Plugin `codex` bawaan
  - pilih `OPENCLAW_AGENT_RUNTIME=codex`
  - kirim giliran agen gateway pertama ke `codex/gpt-5.4`
  - kirim giliran kedua ke sesi OpenClaw yang sama dan verifikasi thread app-server
    dapat di-resume
  - jalankan `/codex status` dan `/codex models` melalui jalur perintah gateway yang sama
- Pengujian: `src/gateway/gateway-codex-harness.live.test.ts`
- Aktifkan: `OPENCLAW_LIVE_CODEX_HARNESS=1`
- Model default: `codex/gpt-5.4`
- Probe gambar opsional: `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1`
- Probe MCP/alat opsional: `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1`
- Smoke ini menetapkan `OPENCLAW_AGENT_HARNESS_FALLBACK=none` sehingga harness Codex yang rusak
  tidak bisa lolos dengan diam-diam fallback ke PI.
- Auth: `OPENAI_API_KEY` dari shell/profile, plus opsional salinan
  `~/.codex/auth.json` dan `~/.codex/config.toml`

Resep lokal:

```bash
source ~/.profile
OPENCLAW_LIVE_CODEX_HARNESS=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=1 \
  OPENCLAW_LIVE_CODEX_HARNESS_MODEL=codex/gpt-5.4 \
  pnpm test:live -- src/gateway/gateway-codex-harness.live.test.ts
```

Resep Docker:

```bash
source ~/.profile
pnpm test:docker:live-codex-harness
```

Catatan Docker:

- Runner Docker berada di `scripts/test-live-codex-harness-docker.sh`.
- Runner ini melakukan source `~/.profile` yang di-mount, meneruskan `OPENAI_API_KEY`, menyalin berkas auth CLI Codex saat ada, memasang `@openai/codex` ke prefix npm writable yang di-mount, men-stage source tree, lalu hanya menjalankan pengujian live Codex-harness.
- Docker mengaktifkan probe gambar dan MCP/alat secara default. Setel
  `OPENCLAW_LIVE_CODEX_HARNESS_IMAGE_PROBE=0` atau
  `OPENCLAW_LIVE_CODEX_HARNESS_MCP_PROBE=0` saat Anda membutuhkan eksekusi debug yang lebih sempit.
- Docker juga mengekspor `OPENCLAW_AGENT_HARNESS_FALLBACK=none`, sesuai dengan konfigurasi pengujian live sehingga fallback `openai-codex/*` atau PI tidak dapat menyembunyikan regresi harness Codex.

### Resep live yang direkomendasikan

Allowlist yang sempit dan eksplisit adalah yang paling cepat dan paling tidak flaky:

- Model tunggal, langsung (tanpa gateway):
  - `OPENCLAW_LIVE_MODELS="openai/gpt-5.4" pnpm test:live src/agents/models.profiles.live.test.ts`

- Model tunggal, smoke gateway:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Pemanggilan alat di beberapa provider:
  - `OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3-flash-preview,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

- Fokus Google (API key Gemini + Antigravity):
  - Gemini (API key): `OPENCLAW_LIVE_GATEWAY_MODELS="google/gemini-3-flash-preview" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`
  - Antigravity (OAuth): `OPENCLAW_LIVE_GATEWAY_MODELS="google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-pro-high" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

Catatan:

- `google/...` menggunakan API Gemini (API key).
- `google-antigravity/...` menggunakan bridge OAuth Antigravity (endpoint agen gaya Cloud Code Assist).
- `google-gemini-cli/...` menggunakan Gemini CLI lokal di mesin Anda (autentikasi terpisah + kekhasan tooling).
- API Gemini vs Gemini CLI:
  - API: OpenClaw memanggil API Gemini hosted milik Google melalui HTTP (API key / auth profil); inilah yang dimaksud sebagian besar pengguna dengan “Gemini”.
  - CLI: OpenClaw melakukan shell out ke biner `gemini` lokal; ia memiliki autentikasinya sendiri dan dapat berperilaku berbeda (dukungan streaming/alat/perbedaan versi).

## Live: matriks model (apa yang kami cakup)

Tidak ada “daftar model CI” yang tetap (live bersifat opt-in), tetapi berikut adalah model **yang direkomendasikan** untuk dicakup secara rutin pada mesin dev dengan kunci.

### Set smoke modern (pemanggilan alat + gambar)

Ini adalah eksekusi “model umum” yang kami harapkan tetap berfungsi:

- OpenAI (non-Codex): `openai/gpt-5.4` (opsional: `openai/gpt-5.4-mini`)
- OpenAI Codex: `openai-codex/gpt-5.4`
- Anthropic: `anthropic/claude-opus-4-6` (atau `anthropic/claude-sonnet-4-6`)
- Google (API Gemini): `google/gemini-3.1-pro-preview` dan `google/gemini-3-flash-preview` (hindari model Gemini 2.x yang lebih lama)
- Google (Antigravity): `google-antigravity/claude-opus-4-6-thinking` dan `google-antigravity/gemini-3-flash`
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Jalankan smoke gateway dengan alat + gambar:
`OPENCLAW_LIVE_GATEWAY_MODELS="openai/gpt-5.4,openai-codex/gpt-5.4,anthropic/claude-opus-4-6,google/gemini-3.1-pro-preview,google/gemini-3-flash-preview,google-antigravity/claude-opus-4-6-thinking,google-antigravity/gemini-3-flash,zai/glm-4.7,minimax/MiniMax-M2.7" pnpm test:live src/gateway/gateway-models.profiles.live.test.ts`

### Baseline: pemanggilan alat (Read + Exec opsional)

Pilih setidaknya satu per keluarga provider:

- OpenAI: `openai/gpt-5.4` (atau `openai/gpt-5.4-mini`)
- Anthropic: `anthropic/claude-opus-4-6` (atau `anthropic/claude-sonnet-4-6`)
- Google: `google/gemini-3-flash-preview` (atau `google/gemini-3.1-pro-preview`)
- Z.AI (GLM): `zai/glm-4.7`
- MiniMax: `minimax/MiniMax-M2.7`

Cakupan tambahan opsional (bagus untuk dimiliki):

- xAI: `xai/grok-4` (atau yang terbaru tersedia)
- Mistral: `mistral/`… (pilih satu model berkemampuan “tools” yang Anda aktifkan)
- Cerebras: `cerebras/`… (jika Anda memiliki akses)
- LM Studio: `lmstudio/`… (lokal; pemanggilan alat bergantung pada mode API)

### Vision: pengiriman gambar (lampiran → pesan multimodal)

Sertakan setidaknya satu model berkemampuan gambar dalam `OPENCLAW_LIVE_GATEWAY_MODELS` (varian Claude/Gemini/OpenAI yang mendukung vision, dll.) untuk menjalankan probe gambar.

### Aggregator / gateway alternatif

Jika Anda mengaktifkan kunci, kami juga mendukung pengujian melalui:

- OpenRouter: `openrouter/...` (ratusan model; gunakan `openclaw models scan` untuk menemukan kandidat yang mendukung alat+gambar)
- OpenCode: `opencode/...` untuk Zen dan `opencode-go/...` untuk Go (auth melalui `OPENCODE_API_KEY` / `OPENCODE_ZEN_API_KEY`)

Lebih banyak provider yang dapat Anda sertakan dalam matriks live (jika Anda memiliki kredensial/config):

- Bawaan: `openai`, `openai-codex`, `anthropic`, `google`, `google-vertex`, `google-antigravity`, `google-gemini-cli`, `zai`, `openrouter`, `opencode`, `opencode-go`, `xai`, `groq`, `cerebras`, `mistral`, `github-copilot`
- Melalui `models.providers` (endpoint kustom): `minimax` (cloud/API), plus proxy yang kompatibel dengan OpenAI/Anthropic apa pun (LM Studio, vLLM, LiteLLM, dll.)

Tips: jangan mencoba meng-hardcode “semua model” di dokumen. Daftar otoritatif adalah apa pun yang dikembalikan `discoverModels(...)` di mesin Anda + kunci apa pun yang tersedia.

## Kredensial (jangan pernah commit)

Pengujian live menemukan kredensial dengan cara yang sama seperti CLI. Implikasi praktisnya:

- Jika CLI berfungsi, pengujian live seharusnya menemukan kunci yang sama.
- Jika pengujian live mengatakan “no creds”, debug dengan cara yang sama seperti Anda men-debug `openclaw models list` / pemilihan model.

- Profil auth per agen: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (inilah yang dimaksud dengan “profile keys” dalam pengujian live)
- Config: `~/.openclaw/openclaw.json` (atau `OPENCLAW_CONFIG_PATH`)
- Direktori state lama: `~/.openclaw/credentials/` (disalin ke home live yang di-stage saat ada, tetapi bukan store utama profile-key)
- Eksekusi lokal live secara default menyalin config aktif, berkas `auth-profiles.json` per agen, `credentials/` lama, dan direktori auth CLI eksternal yang didukung ke home pengujian sementara; home live yang di-stage melewati `workspace/` dan `sandboxes/`, dan override path `agents.*.workspace` / `agentDir` dihapus sehingga probe tetap berada di luar workspace host nyata Anda.

Jika Anda ingin mengandalkan kunci env (misalnya diekspor di `~/.profile`), jalankan pengujian lokal setelah `source ~/.profile`, atau gunakan runner Docker di bawah (mereka dapat me-mount `~/.profile` ke dalam container).

## Live Deepgram (transkripsi audio)

- Pengujian: `src/media-understanding/providers/deepgram/audio.live.test.ts`
- Aktifkan: `DEEPGRAM_API_KEY=... DEEPGRAM_LIVE_TEST=1 pnpm test:live src/media-understanding/providers/deepgram/audio.live.test.ts`

## Live BytePlus coding plan

- Pengujian: `src/agents/byteplus.live.test.ts`
- Aktifkan: `BYTEPLUS_API_KEY=... BYTEPLUS_LIVE_TEST=1 pnpm test:live src/agents/byteplus.live.test.ts`
- Override model opsional: `BYTEPLUS_CODING_MODEL=ark-code-latest`

## Live media workflow ComfyUI

- Pengujian: `extensions/comfy/comfy.live.test.ts`
- Aktifkan: `OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts`
- Cakupan:
  - Menjalankan jalur gambar, video, dan `music_generate` comfy bawaan
  - Melewati setiap kapabilitas kecuali `models.providers.comfy.<capability>` dikonfigurasi
  - Berguna setelah mengubah pengiriman workflow comfy, polling, unduhan, atau pendaftaran Plugin

## Live pembuatan gambar

- Pengujian: `src/image-generation/runtime.live.test.ts`
- Perintah: `pnpm test:live src/image-generation/runtime.live.test.ts`
- Harness: `pnpm test:live:media image`
- Cakupan:
  - Menginventarisasi setiap Plugin provider pembuatan gambar yang terdaftar
  - Memuat env var provider yang hilang dari shell login Anda (`~/.profile`) sebelum probing
  - Secara default menggunakan API key live/env sebelum profil auth yang tersimpan, sehingga kunci pengujian basi di `auth-profiles.json` tidak menutupi kredensial shell nyata
  - Melewati provider tanpa auth/profil/model yang dapat digunakan
  - Menjalankan varian pembuatan gambar bawaan melalui kapabilitas runtime bersama:
    - `google:flash-generate`
    - `google:pro-generate`
    - `google:pro-edit`
    - `openai:default-generate`
- Provider bawaan saat ini yang dicakup:
  - `openai`
  - `google`
- Penyempitan opsional:
  - `OPENCLAW_LIVE_IMAGE_GENERATION_PROVIDERS="openai,google"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_MODELS="openai/gpt-image-1,google/gemini-3.1-flash-image-preview"`
  - `OPENCLAW_LIVE_IMAGE_GENERATION_CASES="google:flash-generate,google:pro-edit"`
- Perilaku auth opsional:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` untuk memaksa auth profile-store dan mengabaikan override yang hanya dari env

## Live pembuatan musik

- Pengujian: `extensions/music-generation-providers.live.test.ts`
- Aktifkan: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/music-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media music`
- Cakupan:
  - Menjalankan jalur provider pembuatan musik bawaan bersama
  - Saat ini mencakup Google dan MiniMax
  - Memuat env var provider dari shell login Anda (`~/.profile`) sebelum probing
  - Secara default menggunakan API key live/env sebelum profil auth yang tersimpan, sehingga kunci pengujian basi di `auth-profiles.json` tidak menutupi kredensial shell nyata
  - Melewati provider tanpa auth/profil/model yang dapat digunakan
  - Menjalankan kedua mode runtime yang dideklarasikan saat tersedia:
    - `generate` dengan input prompt saja
    - `edit` saat provider mendeklarasikan `capabilities.edit.enabled`
  - Cakupan jalur bersama saat ini:
    - `google`: `generate`, `edit`
    - `minimax`: `generate`
    - `comfy`: berkas live Comfy terpisah, bukan sweep bersama ini
- Penyempitan opsional:
  - `OPENCLAW_LIVE_MUSIC_GENERATION_PROVIDERS="google,minimax"`
  - `OPENCLAW_LIVE_MUSIC_GENERATION_MODELS="google/lyria-3-clip-preview,minimax/music-2.5+"`
- Perilaku auth opsional:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` untuk memaksa auth profile-store dan mengabaikan override yang hanya dari env

## Live pembuatan video

- Pengujian: `extensions/video-generation-providers.live.test.ts`
- Aktifkan: `OPENCLAW_LIVE_TEST=1 pnpm test:live -- extensions/video-generation-providers.live.test.ts`
- Harness: `pnpm test:live:media video`
- Cakupan:
  - Menjalankan jalur provider pembuatan video bawaan bersama
  - Memuat env var provider dari shell login Anda (`~/.profile`) sebelum probing
  - Secara default menggunakan API key live/env sebelum profil auth yang tersimpan, sehingga kunci pengujian basi di `auth-profiles.json` tidak menutupi kredensial shell nyata
  - Melewati provider tanpa auth/profil/model yang dapat digunakan
  - Menjalankan kedua mode runtime yang dideklarasikan saat tersedia:
    - `generate` dengan input prompt saja
    - `imageToVideo` saat provider mendeklarasikan `capabilities.imageToVideo.enabled` dan provider/model terpilih menerima input gambar lokal berbasis buffer dalam sweep bersama
    - `videoToVideo` saat provider mendeklarasikan `capabilities.videoToVideo.enabled` dan provider/model terpilih menerima input video lokal berbasis buffer dalam sweep bersama
  - Provider `imageToVideo` yang saat ini dideklarasikan tetapi dilewati dalam sweep bersama:
    - `vydra` karena `veo3` bawaan hanya teks dan `kling` bawaan memerlukan URL gambar jarak jauh
  - Cakupan Vydra khusus provider:
    - `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_VYDRA_VIDEO=1 pnpm test:live -- extensions/vydra/vydra.live.test.ts`
    - berkas itu menjalankan `veo3` text-to-video plus jalur `kling` yang secara default menggunakan fixture URL gambar jarak jauh
  - Cakupan live `videoToVideo` saat ini:
    - `runway` hanya ketika model yang dipilih adalah `runway/gen4_aleph`
  - Provider `videoToVideo` yang saat ini dideklarasikan tetapi dilewati dalam sweep bersama:
    - `alibaba`, `qwen`, `xai` karena jalur tersebut saat ini memerlukan URL referensi `http(s)` / MP4 jarak jauh
    - `google` karena jalur Gemini/Veo bersama saat ini menggunakan input lokal berbasis buffer dan jalur itu tidak diterima dalam sweep bersama
    - `openai` karena jalur bersama saat ini tidak memiliki jaminan akses inpaint/remix video khusus org
- Penyempitan opsional:
  - `OPENCLAW_LIVE_VIDEO_GENERATION_PROVIDERS="google,openai,runway"`
  - `OPENCLAW_LIVE_VIDEO_GENERATION_MODELS="google/veo-3.1-fast-generate-preview,openai/sora-2,runway/gen4_aleph"`
- Perilaku auth opsional:
  - `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` untuk memaksa auth profile-store dan mengabaikan override yang hanya dari env

## Harness live media

- Perintah: `pnpm test:live:media`
- Tujuan:
  - Menjalankan suite live gambar, musik, dan video bersama melalui satu entrypoint native repo
  - Memuat otomatis env var provider yang hilang dari `~/.profile`
  - Secara default otomatis mempersempit setiap suite ke provider yang saat ini memiliki auth yang dapat digunakan
  - Menggunakan kembali `scripts/test-live.mjs`, sehingga perilaku Heartbeat dan mode senyap tetap konsisten
- Contoh:
  - `pnpm test:live:media`
  - `pnpm test:live:media image video --providers openai,google,minimax`
  - `pnpm test:live:media video --video-providers openai,runway --all-providers`
  - `pnpm test:live:media music --quiet`

## Runner Docker (opsional untuk pemeriksaan "berfungsi di Linux")

Runner Docker ini terbagi menjadi dua kelompok:

- Runner live-model: `test:docker:live-models` dan `test:docker:live-gateway` hanya menjalankan berkas live profile-key yang cocok di dalam image Docker repo (`src/agents/models.profiles.live.test.ts` dan `src/gateway/gateway-models.profiles.live.test.ts`), sambil me-mount direktori config dan workspace lokal Anda (serta melakukan source `~/.profile` jika di-mount). Entrypoint lokal yang cocok adalah `test:live:models-profiles` dan `test:live:gateway-profiles`.
- Runner live Docker secara default menggunakan batas smoke yang lebih kecil agar sweep Docker penuh tetap praktis:
  `test:docker:live-models` secara default menetapkan `OPENCLAW_LIVE_MAX_MODELS=12`, dan
  `test:docker:live-gateway` secara default menetapkan `OPENCLAW_LIVE_GATEWAY_SMOKE=1`,
  `OPENCLAW_LIVE_GATEWAY_MAX_MODELS=8`,
  `OPENCLAW_LIVE_GATEWAY_STEP_TIMEOUT_MS=45000`, dan
  `OPENCLAW_LIVE_GATEWAY_MODEL_TIMEOUT_MS=90000`. Timpa env var tersebut saat Anda
  secara eksplisit menginginkan pemindaian menyeluruh yang lebih besar.
- `test:docker:all` membangun image Docker live sekali melalui `test:docker:live-build`, lalu menggunakannya kembali untuk dua jalur Docker live tersebut.
- Runner smoke container: `test:docker:openwebui`, `test:docker:onboard`, `test:docker:gateway-network`, `test:docker:mcp-channels`, dan `test:docker:plugins` menyalakan satu atau lebih container nyata dan memverifikasi jalur integrasi tingkat lebih tinggi.

Runner Docker live-model juga hanya bind-mount home auth CLI yang diperlukan (atau semua yang didukung ketika eksekusi tidak dipersempit), lalu menyalinnya ke home container sebelum eksekusi sehingga OAuth CLI eksternal dapat menyegarkan token tanpa mengubah store auth host:

- Model langsung: `pnpm test:docker:live-models` (script: `scripts/test-live-models-docker.sh`)
- Smoke bind ACP: `pnpm test:docker:live-acp-bind` (script: `scripts/test-live-acp-bind-docker.sh`)
- Smoke backend CLI: `pnpm test:docker:live-cli-backend` (script: `scripts/test-live-cli-backend-docker.sh`)
- Smoke harness app-server Codex: `pnpm test:docker:live-codex-harness` (script: `scripts/test-live-codex-harness-docker.sh`)
- Gateway + agen dev: `pnpm test:docker:live-gateway` (script: `scripts/test-live-gateway-models-docker.sh`)
- Smoke live Open WebUI: `pnpm test:docker:openwebui` (script: `scripts/e2e/openwebui-docker.sh`)
- Wizard onboarding (TTY, scaffolding penuh): `pnpm test:docker:onboard` (script: `scripts/e2e/onboard-docker.sh`)
- Jaringan gateway (dua container, auth WS + health): `pnpm test:docker:gateway-network` (script: `scripts/e2e/gateway-network-docker.sh`)
- Bridge channel MCP (Gateway seeded + bridge stdio + smoke notification-frame Claude mentah): `pnpm test:docker:mcp-channels` (script: `scripts/e2e/mcp-channels-docker.sh`)
- Plugins (smoke install + alias `/plugin` + semantik restart bundel Claude): `pnpm test:docker:plugins` (script: `scripts/e2e/plugins-docker.sh`)

Runner Docker live-model juga me-mount checkout saat ini sebagai read-only dan
men-stage-nya ke workdir sementara di dalam container. Ini menjaga image runtime
tetap ramping sambil tetap menjalankan Vitest terhadap source/config lokal Anda yang persis.
Langkah staging ini melewati cache lokal besar dan output build aplikasi seperti
`.pnpm-store`, `.worktrees`, `__openclaw_vitest__`, serta direktori output `.build`
lokal aplikasi atau Gradle sehingga eksekusi live Docker tidak menghabiskan beberapa menit untuk menyalin
artefak khusus mesin.
Runner ini juga menetapkan `OPENCLAW_SKIP_CHANNELS=1` sehingga probe live gateway tidak memulai
worker channel Telegram/Discord/dll. nyata di dalam container.
`test:docker:live-models` tetap menjalankan `pnpm test:live`, jadi teruskan juga
`OPENCLAW_LIVE_GATEWAY_*` saat Anda perlu mempersempit atau mengecualikan cakupan live
gateway dari jalur Docker tersebut.
`test:docker:openwebui` adalah smoke kompatibilitas tingkat lebih tinggi: ia memulai
container gateway OpenClaw dengan endpoint HTTP yang kompatibel dengan OpenAI diaktifkan,
memulai container Open WebUI yang dipin terhadap gateway tersebut, masuk melalui
Open WebUI, memverifikasi `/api/models` mengekspos `openclaw/default`, lalu mengirim
permintaan chat nyata melalui proxy `/api/chat/completions` milik Open WebUI.
Eksekusi pertama dapat terasa lebih lambat karena Docker mungkin perlu menarik
image Open WebUI dan Open WebUI mungkin perlu menyelesaikan setup cold-start miliknya.
Jalur ini mengharapkan kunci model live yang dapat digunakan, dan `OPENCLAW_PROFILE_FILE`
(`~/.profile` secara default) adalah cara utama untuk menyediakannya dalam eksekusi yang didockerisasi.
Eksekusi yang berhasil mencetak payload JSON kecil seperti `{ "ok": true, "model":
"openclaw/default", ... }`.
`test:docker:mcp-channels` sengaja dibuat deterministik dan tidak memerlukan
akun Telegram, Discord, atau iMessage nyata. Ia menyalakan container Gateway yang telah di-seed,
memulai container kedua yang menjalankan `openclaw mcp serve`, lalu
memverifikasi penemuan percakapan yang dirutekan, pembacaan transkrip, metadata lampiran,
perilaku antrean peristiwa live, routing pengiriman keluar, dan notifikasi gaya Claude tentang channel +
izin melalui bridge MCP stdio nyata. Pemeriksaan notifikasi
memeriksa frame MCP stdio mentah secara langsung sehingga smoke memvalidasi apa yang sebenarnya dipancarkan
oleh bridge, bukan hanya apa yang kebetulan diekspos oleh SDK klien tertentu.

Smoke thread plain-language ACP manual (bukan CI):

- `bun scripts/dev/discord-acp-plain-language-smoke.ts --channel <discord-channel-id> ...`
- Pertahankan script ini untuk alur kerja regresi/debug. Script ini mungkin diperlukan lagi untuk validasi routing thread ACP, jadi jangan hapus.

Env var yang berguna:

- `OPENCLAW_CONFIG_DIR=...` (default: `~/.openclaw`) di-mount ke `/home/node/.openclaw`
- `OPENCLAW_WORKSPACE_DIR=...` (default: `~/.openclaw/workspace`) di-mount ke `/home/node/.openclaw/workspace`
- `OPENCLAW_PROFILE_FILE=...` (default: `~/.profile`) di-mount ke `/home/node/.profile` dan di-source sebelum menjalankan pengujian
- `OPENCLAW_DOCKER_CLI_TOOLS_DIR=...` (default: `~/.cache/openclaw/docker-cli-tools`) di-mount ke `/home/node/.npm-global` untuk instalasi CLI yang di-cache di dalam Docker
- Direktori/berkas auth CLI eksternal di bawah `$HOME` di-mount read-only di bawah `/host-auth...`, lalu disalin ke `/home/node/...` sebelum pengujian dimulai
  - Direktori default: `.minimax`
  - Berkas default: `~/.codex/auth.json`, `~/.codex/config.toml`, `.claude.json`, `~/.claude/.credentials.json`, `~/.claude/settings.json`, `~/.claude/settings.local.json`
  - Eksekusi provider yang dipersempit hanya me-mount direktori/berkas yang diperlukan yang diinferensikan dari `OPENCLAW_LIVE_PROVIDERS` / `OPENCLAW_LIVE_GATEWAY_PROVIDERS`
  - Timpa secara manual dengan `OPENCLAW_DOCKER_AUTH_DIRS=all`, `OPENCLAW_DOCKER_AUTH_DIRS=none`, atau daftar dipisahkan koma seperti `OPENCLAW_DOCKER_AUTH_DIRS=.claude,.codex`
- `OPENCLAW_LIVE_GATEWAY_MODELS=...` / `OPENCLAW_LIVE_MODELS=...` untuk mempersempit eksekusi
- `OPENCLAW_LIVE_GATEWAY_PROVIDERS=...` / `OPENCLAW_LIVE_PROVIDERS=...` untuk memfilter provider di dalam container
- `OPENCLAW_SKIP_DOCKER_BUILD=1` untuk menggunakan ulang image `openclaw:local-live` yang sudah ada pada eksekusi ulang yang tidak memerlukan rebuild
- `OPENCLAW_LIVE_REQUIRE_PROFILE_KEYS=1` untuk memastikan kredensial berasal dari profile store (bukan env)
- `OPENCLAW_OPENWEBUI_MODEL=...` untuk memilih model yang diekspos oleh gateway bagi smoke Open WebUI
- `OPENCLAW_OPENWEBUI_PROMPT=...` untuk menimpa prompt pemeriksaan nonce yang digunakan oleh smoke Open WebUI
- `OPENWEBUI_IMAGE=...` untuk menimpa tag image Open WebUI yang dipin

## Sanity docs

Jalankan pemeriksaan docs setelah edit dokumen: `pnpm check:docs`.
Jalankan validasi anchor Mintlify penuh saat Anda juga membutuhkan pemeriksaan heading di dalam halaman: `pnpm docs:check-links:anchors`.

## Regresi offline (aman untuk CI)

Ini adalah regresi “pipeline nyata” tanpa provider nyata:

- Pemanggilan alat gateway (mock OpenAI, gateway + loop agen nyata): `src/gateway/gateway.test.ts` (kasus: "runs a mock OpenAI tool call end-to-end via gateway agent loop")
- Wizard gateway (WS `wizard.start`/`wizard.next`, menulis config + auth yang ditegakkan): `src/gateway/gateway.test.ts` (kasus: "runs wizard over ws and writes auth token config")

## Evals keandalan agen (Skills)

Kami sudah memiliki beberapa pengujian aman-CI yang berperilaku seperti “evals keandalan agen”:

- Pemanggilan alat mock melalui gateway + loop agen nyata (`src/gateway/gateway.test.ts`).
- Alur wizard end-to-end yang memvalidasi wiring sesi dan efek config (`src/gateway/gateway.test.ts`).

Apa yang masih kurang untuk Skills (lihat [Skills](/id/tools/skills)):

- **Pengambilan keputusan:** saat Skills terdaftar dalam prompt, apakah agen memilih skill yang tepat (atau menghindari yang tidak relevan)?
- **Kepatuhan:** apakah agen membaca `SKILL.md` sebelum digunakan dan mengikuti langkah/argumen yang diwajibkan?
- **Kontrak alur kerja:** skenario multi-giliran yang menegaskan urutan alat, carryover riwayat sesi, dan batas sandbox.

Evals di masa depan sebaiknya tetap deterministik terlebih dahulu:

- Runner skenario menggunakan provider mock untuk menegaskan pemanggilan alat + urutannya, pembacaan berkas skill, dan wiring sesi.
- Suite kecil skenario yang berfokus pada skill (gunakan vs hindari, gating, injeksi prompt).
- Evals live opsional (opt-in, digating env) hanya setelah suite aman-CI tersedia.

## Pengujian kontrak (bentuk Plugin dan channel)

Pengujian kontrak memverifikasi bahwa setiap Plugin dan channel yang terdaftar sesuai dengan
kontrak antarmukanya. Pengujian ini mengiterasi semua Plugin yang ditemukan dan menjalankan
suite penegasan bentuk dan perilaku. Jalur unit default `pnpm test` sengaja
melewati berkas seam dan smoke bersama ini; jalankan perintah kontrak secara eksplisit
saat Anda menyentuh surface channel atau provider bersama.

### Perintah

- Semua kontrak: `pnpm test:contracts`
- Hanya kontrak channel: `pnpm test:contracts:channels`
- Hanya kontrak provider: `pnpm test:contracts:plugins`

### Kontrak channel

Terletak di `src/channels/plugins/contracts/*.contract.test.ts`:

- **plugin** - Bentuk Plugin dasar (id, nama, kapabilitas)
- **setup** - Kontrak wizard setup
- **session-binding** - Perilaku binding sesi
- **outbound-payload** - Struktur payload pesan
- **inbound** - Penanganan pesan masuk
- **actions** - Handler tindakan channel
- **threading** - Penanganan ID thread
- **directory** - API direktori/roster
- **group-policy** - Penegakan kebijakan grup

### Kontrak status provider

Terletak di `src/plugins/contracts/*.contract.test.ts`.

- **status** - Probe status channel
- **registry** - Bentuk registri Plugin

### Kontrak provider

Terletak di `src/plugins/contracts/*.contract.test.ts`:

- **auth** - Kontrak alur auth
- **auth-choice** - Pilihan/seleksi auth
- **catalog** - API katalog model
- **discovery** - Penemuan Plugin
- **loader** - Pemuatan Plugin
- **runtime** - Runtime provider
- **shape** - Bentuk/antarmuka Plugin
- **wizard** - Wizard setup

### Kapan dijalankan

- Setelah mengubah ekspor atau subpath `plugin-sdk`
- Setelah menambahkan atau memodifikasi Plugin channel atau provider
- Setelah merombak registrasi atau penemuan Plugin

Pengujian kontrak berjalan di CI dan tidak memerlukan API key nyata.

## Menambahkan regresi (panduan)

Saat Anda memperbaiki masalah provider/model yang ditemukan di live:

- Tambahkan regresi aman-CI jika memungkinkan (provider mock/stub, atau tangkap transformasi bentuk permintaan yang persis)
- Jika masalah itu secara inheren hanya-live (rate limit, kebijakan auth), pertahankan pengujian live tetap sempit dan opt-in melalui env var
- Utamakan menargetkan lapisan terkecil yang menangkap bug:
  - bug konversi/replay permintaan provider → pengujian model langsung
  - bug pipeline sesi/riwayat/alat gateway → smoke live gateway atau pengujian mock gateway aman-CI
- Guardrail traversal SecretRef:
  - `src/secrets/exec-secret-ref-id-parity.test.ts` menurunkan satu target sampel per kelas SecretRef dari metadata registri (`listSecretTargetRegistryEntries()`), lalu menegaskan bahwa id exec segmen traversal ditolak.
  - Jika Anda menambahkan keluarga target SecretRef `includeInPlan` baru di `src/secrets/target-registry-data.ts`, perbarui `classifyTargetClass` dalam pengujian itu. Pengujian ini sengaja gagal pada id target yang tidak terklasifikasi sehingga kelas baru tidak bisa dilewati secara diam-diam.
