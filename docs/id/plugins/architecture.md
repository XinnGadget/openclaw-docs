---
read_when:
    - Membangun atau men-debug plugin OpenClaw native
    - Memahami model kapabilitas plugin atau batas kepemilikan
    - Mengerjakan pipeline pemuatan plugin atau registri
    - Mengimplementasikan hook runtime provider atau plugin channel
sidebarTitle: Internals
summary: 'Internal Plugin: model kapabilitas, kepemilikan, kontrak, pipeline pemuatan, dan helper runtime'
title: Internal Plugin
x-i18n:
    generated_at: "2026-04-15T09:14:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: f86798b5d2b0ad82d2397a52a6c21ed37fe6eee1dd3d124a9e4150c4f630b841
    source_path: plugins/architecture.md
    workflow: 15
---

# Internal Plugin

<Info>
  Ini adalah **referensi arsitektur mendalam**. Untuk panduan praktis, lihat:
  - [Instal dan gunakan plugin](/id/tools/plugin) — panduan pengguna
  - [Memulai](/id/plugins/building-plugins) — tutorial plugin pertama
  - [Plugin Channel](/id/plugins/sdk-channel-plugins) — bangun channel pesan
  - [Plugin Provider](/id/plugins/sdk-provider-plugins) — bangun provider model
  - [Ikhtisar SDK](/id/plugins/sdk-overview) — peta impor dan API pendaftaran
</Info>

Halaman ini membahas arsitektur internal sistem plugin OpenClaw.

## Model kapabilitas publik

Kapabilitas adalah model **plugin native** publik di dalam OpenClaw. Setiap
plugin OpenClaw native mendaftar ke satu atau lebih tipe kapabilitas:

| Kapabilitas          | Metode pendaftaran                             | Contoh plugin                        |
| -------------------- | ---------------------------------------------- | ------------------------------------ |
| Inferensi teks       | `api.registerProvider(...)`                    | `openai`, `anthropic`                |
| Backend inferensi CLI  | `api.registerCliBackend(...)`                | `openai`, `anthropic`                |
| Ucapan               | `api.registerSpeechProvider(...)`              | `elevenlabs`, `microsoft`            |
| Transkripsi realtime | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                           |
| Suara realtime       | `api.registerRealtimeVoiceProvider(...)`       | `openai`                             |
| Pemahaman media      | `api.registerMediaUnderstandingProvider(...)`  | `openai`, `google`                   |
| Pembuatan gambar     | `api.registerImageGenerationProvider(...)`     | `openai`, `google`, `fal`, `minimax` |
| Pembuatan musik      | `api.registerMusicGenerationProvider(...)`     | `google`, `minimax`                  |
| Pembuatan video      | `api.registerVideoGenerationProvider(...)`     | `qwen`                               |
| Pengambilan web      | `api.registerWebFetchProvider(...)`            | `firecrawl`                          |
| Pencarian web        | `api.registerWebSearchProvider(...)`           | `google`                             |
| Channel / pesan      | `api.registerChannel(...)`                     | `msteams`, `matrix`                  |

Plugin yang mendaftarkan nol kapabilitas tetapi menyediakan hook, tool, atau
layanan adalah plugin **legacy hook-only**. Pola itu masih sepenuhnya didukung.

### Sikap kompatibilitas eksternal

Model kapabilitas sudah diterapkan di core dan digunakan oleh plugin
bundled/native saat ini, tetapi kompatibilitas plugin eksternal masih
memerlukan standar yang lebih ketat daripada "ini diekspor, jadi ini dibekukan."

Panduan saat ini:

- **plugin eksternal yang sudah ada:** pertahankan integrasi berbasis hook
  tetap berfungsi; perlakukan ini sebagai baseline kompatibilitas
- **plugin bundled/native baru:** utamakan pendaftaran kapabilitas yang eksplisit daripada
  akses vendor-spesifik ke internal atau desain hook-only baru
- **plugin eksternal yang mengadopsi pendaftaran kapabilitas:** diperbolehkan, tetapi
  perlakukan surface helper khusus kapabilitas sebagai sesuatu yang berkembang
  kecuali dokumentasi secara eksplisit menandai kontrak sebagai stabil

Aturan praktis:

- API pendaftaran kapabilitas adalah arah yang dituju
- hook legacy tetap menjadi jalur paling aman tanpa kerusakan untuk plugin eksternal selama
  masa transisi
- tidak semua subpath helper yang diekspor setara; pilih kontrak sempit yang didokumentasikan,
  bukan ekspor helper insidental

### Bentuk plugin

OpenClaw mengklasifikasikan setiap plugin yang dimuat ke dalam suatu bentuk berdasarkan
perilaku pendaftaran aktualnya (bukan hanya metadata statis):

- **plain-capability** -- mendaftarkan tepat satu tipe kapabilitas (misalnya
  plugin provider-only seperti `mistral`)
- **hybrid-capability** -- mendaftarkan beberapa tipe kapabilitas (misalnya
  `openai` memiliki inferensi teks, ucapan, pemahaman media, dan pembuatan
  gambar)
- **hook-only** -- hanya mendaftarkan hook (tertik atau kustom), tanpa
  kapabilitas, tool, perintah, atau layanan
- **non-capability** -- mendaftarkan tool, perintah, layanan, atau rute tetapi tanpa
  kapabilitas

Gunakan `openclaw plugins inspect <id>` untuk melihat bentuk plugin dan rincian
kapabilitasnya. Lihat [referensi CLI](/cli/plugins#inspect) untuk detail.

### Hook legacy

Hook `before_agent_start` tetap didukung sebagai jalur kompatibilitas untuk
plugin hook-only. Plugin nyata legacy masih bergantung padanya.

Arah ke depan:

- pertahankan agar tetap berfungsi
- dokumentasikan sebagai legacy
- utamakan `before_model_resolve` untuk pekerjaan override model/provider
- utamakan `before_prompt_build` untuk pekerjaan mutasi prompt
- hapus hanya setelah penggunaan nyata menurun dan cakupan fixture membuktikan keamanan migrasi

### Sinyal kompatibilitas

Saat Anda menjalankan `openclaw doctor` atau `openclaw plugins inspect <id>`, Anda mungkin melihat
salah satu label berikut:

| Sinyal                     | Arti                                                          |
| -------------------------- | ------------------------------------------------------------- |
| **config valid**           | Konfigurasi diparse dengan baik dan plugin berhasil di-resolve |
| **compatibility advisory** | Plugin menggunakan pola yang didukung tetapi lebih lama (mis. `hook-only`) |
| **legacy warning**         | Plugin menggunakan `before_agent_start`, yang sudah deprecated |
| **hard error**             | Konfigurasi tidak valid atau plugin gagal dimuat              |

Baik `hook-only` maupun `before_agent_start` tidak akan merusak plugin Anda saat ini --
`hook-only` bersifat advisory, dan `before_agent_start` hanya memicu peringatan. Sinyal-sinyal ini
juga muncul di `openclaw status --all` dan `openclaw plugins doctor`.

## Ikhtisar arsitektur

Sistem plugin OpenClaw memiliki empat lapisan:

1. **Manifest + discovery**
   OpenClaw menemukan kandidat plugin dari path yang dikonfigurasi, root workspace,
   root extension global, dan extension bundled. Discovery membaca manifest native
   `openclaw.plugin.json` serta manifest bundle yang didukung terlebih dahulu.
2. **Enablement + validation**
   Core memutuskan apakah plugin yang ditemukan diaktifkan, dinonaktifkan, diblokir, atau
   dipilih untuk slot eksklusif seperti memory.
3. **Runtime loading**
   Plugin OpenClaw native dimuat in-process melalui jiti dan mendaftarkan
   kapabilitas ke registri pusat. Bundle yang kompatibel dinormalisasi menjadi
   catatan registri tanpa mengimpor kode runtime.
4. **Surface consumption**
   Bagian lain dari OpenClaw membaca registri untuk mengekspos tool, channel, penyiapan provider,
   hook, rute HTTP, perintah CLI, dan layanan.

Untuk CLI plugin secara khusus, discovery perintah root dibagi menjadi dua fase:

- metadata saat parse berasal dari `registerCli(..., { descriptors: [...] })`
- modul CLI plugin yang sebenarnya dapat tetap lazy dan mendaftar pada pemanggilan pertama

Itu menjaga kode CLI milik plugin tetap berada di dalam plugin sambil tetap memungkinkan OpenClaw
mencadangkan nama perintah root sebelum parsing.

Batas desain yang penting:

- discovery + validasi konfigurasi harus bekerja dari **metadata manifest/schema**
  tanpa mengeksekusi kode plugin
- perilaku runtime native berasal dari jalur `register(api)` modul plugin

Pemisahan itu memungkinkan OpenClaw memvalidasi konfigurasi, menjelaskan plugin yang
hilang/dinonaktifkan, dan membangun petunjuk UI/schema sebelum runtime penuh aktif.

### Plugin channel dan tool pesan bersama

Plugin channel tidak perlu mendaftarkan tool kirim/edit/reaksi terpisah untuk
aksi chat normal. OpenClaw mempertahankan satu tool `message` bersama di core, dan
plugin channel memiliki discovery dan eksekusi khusus channel di baliknya.

Batas saat ini adalah:

- core memiliki host tool `message` bersama, wiring prompt, pembukuan sesi/thread,
  dan dispatch eksekusi
- plugin channel memiliki discovery aksi berscope, discovery kapabilitas, dan fragmen
  schema khusus channel
- plugin channel memiliki grammar percakapan sesi khusus provider, seperti
  bagaimana id percakapan mengodekan id thread atau mewarisi dari percakapan induk
- plugin channel mengeksekusi aksi akhir melalui adaptor aksi mereka

Untuk plugin channel, surface SDK-nya adalah
`ChannelMessageActionAdapter.describeMessageTool(...)`. Panggilan discovery terpadu
itu memungkinkan plugin mengembalikan aksi yang terlihat, kapabilitas, dan kontribusi schema
secara bersama agar bagian-bagian itu tidak saling melenceng.

Ketika suatu param message-tool khusus channel membawa sumber media seperti
path lokal atau URL media jarak jauh, plugin juga harus mengembalikan
`mediaSourceParams` dari `describeMessageTool(...)`. Core menggunakan daftar
eksplisit itu untuk menerapkan normalisasi path sandbox dan petunjuk akses media
keluar tanpa meng-hardcode nama param milik plugin.
Utamakan peta berscope aksi di sana, bukan satu daftar datar untuk seluruh channel, agar
param media khusus profil tidak dinormalisasi pada aksi yang tidak terkait seperti
`send`.

Core meneruskan scope runtime ke langkah discovery tersebut. Field penting meliputi:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` inbound tepercaya

Ini penting untuk plugin yang sensitif terhadap konteks. Sebuah channel dapat menyembunyikan atau mengekspos
aksi pesan berdasarkan akun aktif, room/thread/pesan saat ini, atau
identitas peminta tepercaya tanpa meng-hardcode percabangan khusus channel di
tool `message` core.

Inilah sebabnya perubahan routing embedded-runner masih merupakan pekerjaan plugin: runner
bertanggung jawab untuk meneruskan identitas chat/sesi saat ini ke batas
discovery plugin agar tool `message` bersama mengekspos surface milik channel yang tepat
untuk giliran saat ini.

Untuk helper eksekusi milik channel, plugin bundled harus menjaga runtime eksekusi
tetap di dalam modul extension miliknya sendiri. Core tidak lagi memiliki runtime
aksi pesan Discord, Slack, Telegram, atau WhatsApp di bawah `src/agents/tools`.
Kami tidak memublikasikan subpath `plugin-sdk/*-action-runtime` terpisah, dan plugin bundled
harus mengimpor kode runtime lokalnya sendiri secara langsung dari
modul milik extension mereka.

Batas yang sama berlaku pada seam SDK bernama provider secara umum: core tidak boleh
mengimpor barrel kemudahan khusus channel untuk extension Slack, Discord, Signal,
WhatsApp, atau extension serupa. Jika core memerlukan suatu perilaku, maka
konsumsi barrel `api.ts` / `runtime-api.ts` milik plugin bundled itu sendiri atau promosikan kebutuhan tersebut
menjadi kapabilitas generik yang sempit di SDK bersama.

Khusus untuk poll, ada dua jalur eksekusi:

- `outbound.sendPoll` adalah baseline bersama untuk channel yang cocok dengan model
  poll umum
- `actions.handleAction("poll")` adalah jalur yang diutamakan untuk semantik poll khusus channel
  atau param poll tambahan

Core sekarang menunda parsing poll bersama sampai setelah dispatch poll plugin menolak
aksi tersebut, sehingga handler poll milik plugin dapat menerima field poll khusus channel
tanpa lebih dulu dihalangi oleh parser poll generik.

Lihat [Load pipeline](#load-pipeline) untuk urutan startup lengkap.

## Model kepemilikan kapabilitas

OpenClaw memperlakukan plugin native sebagai batas kepemilikan untuk sebuah **perusahaan** atau
sebuah **fitur**, bukan sebagai kumpulan acak integrasi yang tidak terkait.

Artinya:

- plugin perusahaan biasanya harus memiliki semua surface OpenClaw yang
  menghadap perusahaan tersebut
- plugin fitur biasanya harus memiliki seluruh surface fitur yang diperkenalkannya
- channel harus mengonsumsi kapabilitas core bersama alih-alih mengimplementasikan ulang
  perilaku provider secara ad hoc

Contoh:

- plugin `openai` bundled memiliki perilaku model-provider OpenAI dan perilaku
  ucapan + suara realtime + pemahaman media + pembuatan gambar OpenAI
- plugin `elevenlabs` bundled memiliki perilaku ucapan ElevenLabs
- plugin `microsoft` bundled memiliki perilaku ucapan Microsoft
- plugin `google` bundled memiliki perilaku model-provider Google ditambah perilaku
  pemahaman media + pembuatan gambar + pencarian web Google
- plugin `firecrawl` bundled memiliki perilaku pengambilan web Firecrawl
- plugin `minimax`, `mistral`, `moonshot`, dan `zai` bundled memiliki backend
  pemahaman media mereka
- plugin `qwen` bundled memiliki perilaku text-provider Qwen ditambah
  perilaku pemahaman media dan pembuatan video
- plugin `voice-call` adalah plugin fitur: plugin ini memiliki transport panggilan, tool,
  CLI, rute, dan bridging media-stream Twilio, tetapi plugin ini mengonsumsi kapabilitas
  ucapan bersama ditambah transkripsi realtime dan suara realtime alih-alih
  mengimpor plugin vendor secara langsung

Keadaan akhir yang dituju adalah:

- OpenAI berada dalam satu plugin meskipun mencakup model teks, ucapan, gambar, dan
  video di masa depan
- vendor lain dapat melakukan hal yang sama untuk cakupan surface miliknya sendiri
- channel tidak peduli plugin vendor mana yang memiliki provider; mereka mengonsumsi
  kontrak kapabilitas bersama yang diekspos oleh core

Ini adalah perbedaan kuncinya:

- **plugin** = batas kepemilikan
- **capability** = kontrak core yang dapat diimplementasikan atau dikonsumsi oleh beberapa plugin

Jadi jika OpenClaw menambahkan domain baru seperti video, pertanyaan pertama bukanlah
"provider mana yang harus meng-hardcode penanganan video?" Pertanyaan pertama adalah "apa
kontrak kapabilitas video core?" Setelah kontrak itu ada, plugin vendor
dapat mendaftar padanya dan plugin channel/fitur dapat mengonsumsinya.

Jika kapabilitas itu belum ada, langkah yang benar biasanya adalah:

1. definisikan kapabilitas yang belum ada di core
2. ekspos kapabilitas itu melalui API/runtime plugin dengan cara yang tertik
3. hubungkan channel/fitur ke kapabilitas itu
4. biarkan plugin vendor mendaftarkan implementasi

Ini menjaga kepemilikan tetap eksplisit sambil menghindari perilaku core yang bergantung pada
satu vendor atau jalur kode khusus plugin yang sekali pakai.

### Pelapisan kapabilitas

Gunakan model mental ini saat memutuskan di mana kode seharusnya berada:

- **lapisan kapabilitas core**: orkestrasi bersama, kebijakan, fallback, konfigurasi
  aturan merge, semantik pengiriman, dan kontrak bertipe
- **lapisan plugin vendor**: API vendor-spesifik, autentikasi, katalog model, ucapan
  sintesis, pembuatan gambar, backend video masa depan, endpoint penggunaan
- **lapisan plugin channel/fitur**: integrasi Slack/Discord/voice-call/dll.
  yang mengonsumsi kapabilitas core dan menyajikannya pada suatu surface

Sebagai contoh, TTS mengikuti bentuk ini:

- core memiliki kebijakan TTS saat balasan, urutan fallback, preferensi, dan pengiriman channel
- `openai`, `elevenlabs`, dan `microsoft` memiliki implementasi sintesis
- `voice-call` mengonsumsi helper runtime TTS teleponi

Pola yang sama harus diutamakan untuk kapabilitas di masa depan.

### Contoh plugin perusahaan multi-kapabilitas

Plugin perusahaan harus terasa kohesif dari luar. Jika OpenClaw memiliki
kontrak bersama untuk model, ucapan, transkripsi realtime, suara realtime, pemahaman
media, pembuatan gambar, pembuatan video, pengambilan web, dan pencarian web,
sebuah vendor dapat memiliki semua surface-nya di satu tempat:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Yang penting bukanlah nama helper yang persis sama. Bentuknya yang penting:

- satu plugin memiliki surface vendor
- core tetap memiliki kontrak kapabilitas
- channel dan plugin fitur mengonsumsi helper `api.runtime.*`, bukan kode vendor
- pengujian kontrak dapat menegaskan bahwa plugin telah mendaftarkan kapabilitas yang
  diklaimnya sebagai miliknya

### Contoh kapabilitas: pemahaman video

OpenClaw sudah memperlakukan pemahaman gambar/audio/video sebagai satu
kapabilitas bersama. Model kepemilikan yang sama juga berlaku di sana:

1. core mendefinisikan kontrak pemahaman media
2. plugin vendor mendaftarkan `describeImage`, `transcribeAudio`, dan
   `describeVideo` sesuai kebutuhan
3. channel dan plugin fitur mengonsumsi perilaku core bersama alih-alih
   menghubungkan langsung ke kode vendor

Ini menghindari asumsi video milik satu provider tertanam di core. Plugin memiliki
surface vendor; core memiliki kontrak kapabilitas dan perilaku fallback.

Pembuatan video sudah menggunakan urutan yang sama: core memiliki kontrak
kapabilitas bertipe dan helper runtime, dan plugin vendor mendaftarkan
implementasi `api.registerVideoGenerationProvider(...)` terhadapnya.

Butuh checklist rollout yang konkret? Lihat
[Capability Cookbook](/id/plugins/architecture).

## Kontrak dan enforcement

Surface API plugin sengaja dibuat bertipe dan terpusat di
`OpenClawPluginApi`. Kontrak itu mendefinisikan titik pendaftaran yang didukung dan
helper runtime yang dapat diandalkan oleh plugin.

Mengapa ini penting:

- penulis plugin mendapatkan satu standar internal yang stabil
- core dapat menolak kepemilikan ganda seperti dua plugin yang mendaftarkan id
  provider yang sama
- startup dapat menampilkan diagnostik yang dapat ditindaklanjuti untuk pendaftaran
  yang malformed
- pengujian kontrak dapat menegakkan kepemilikan plugin bundled dan mencegah drift diam-diam

Ada dua lapisan enforcement:

1. **enforcement pendaftaran runtime**
   Registri plugin memvalidasi pendaftaran saat plugin dimuat. Contoh:
   id provider ganda, id speech provider ganda, dan pendaftaran
   yang malformed menghasilkan diagnostik plugin alih-alih perilaku yang tidak terdefinisi.
2. **pengujian kontrak**
   Plugin bundled ditangkap dalam registri kontrak selama pengujian berjalan sehingga
   OpenClaw dapat menegaskan kepemilikan secara eksplisit. Saat ini ini digunakan untuk model
   provider, speech provider, web search provider, dan kepemilikan pendaftaran
   bundled.

Efek praktisnya adalah bahwa OpenClaw mengetahui, sejak awal, plugin mana yang memiliki
surface mana. Ini memungkinkan core dan channel tersusun dengan mulus karena kepemilikan
dideklarasikan, bertipe, dan dapat diuji alih-alih implisit.

### Apa yang termasuk dalam sebuah kontrak

Kontrak plugin yang baik adalah:

- bertipe
- kecil
- spesifik terhadap kapabilitas
- dimiliki oleh core
- dapat digunakan ulang oleh beberapa plugin
- dapat dikonsumsi oleh channel/fitur tanpa pengetahuan vendor

Kontrak plugin yang buruk adalah:

- kebijakan vendor-spesifik yang tersembunyi di core
- jalur lolos plugin sekali pakai yang melewati registri
- kode channel yang langsung masuk ke implementasi vendor
- objek runtime ad hoc yang bukan bagian dari `OpenClawPluginApi` atau
  `api.runtime`

Jika ragu, naikkan tingkat abstraksinya: definisikan kapabilitasnya terlebih dahulu, lalu
biarkan plugin terhubung ke sana.

## Model eksekusi

Plugin OpenClaw native berjalan **in-process** dengan Gateway. Plugin ini tidak
disandbox. Plugin native yang dimuat memiliki batas kepercayaan tingkat proses yang sama dengan
kode core.

Implikasinya:

- plugin native dapat mendaftarkan tool, network handler, hook, dan layanan
- bug pada plugin native dapat membuat gateway crash atau tidak stabil
- plugin native yang berbahaya setara dengan eksekusi kode arbitrer di dalam
  proses OpenClaw

Bundle yang kompatibel secara default lebih aman karena OpenClaw saat ini memperlakukannya
sebagai paket metadata/konten. Dalam rilis saat ini, itu terutama berarti
Skills bundled.

Gunakan allowlist dan path instalasi/pemuatan eksplisit untuk plugin non-bundled. Perlakukan
plugin workspace sebagai kode saat pengembangan, bukan default produksi.

Untuk nama paket workspace bundled, pertahankan id plugin tertambat pada nama
npm: `@openclaw/<id>` secara default, atau sufiks bertipe yang disetujui seperti
`-provider`, `-plugin`, `-speech`, `-sandbox`, atau `-media-understanding` ketika
paket tersebut dengan sengaja mengekspos peran plugin yang lebih sempit.

Catatan kepercayaan penting:

- `plugins.allow` mempercayai **id plugin**, bukan asal sumbernya.
- Plugin workspace dengan id yang sama seperti plugin bundled dengan sengaja membayangi
  salinan bundled ketika plugin workspace itu diaktifkan/masuk allowlist.
- Ini normal dan berguna untuk pengembangan lokal, pengujian patch, dan hotfix.

## Batas ekspor

OpenClaw mengekspor kapabilitas, bukan kemudahan implementasi.

Pertahankan pendaftaran kapabilitas sebagai publik. Pangkas ekspor helper non-kontrak:

- subpath helper khusus plugin bundled
- subpath plumbing runtime yang tidak dimaksudkan sebagai API publik
- helper kemudahan vendor-spesifik
- helper penyiapan/onboarding yang merupakan detail implementasi

Beberapa subpath helper plugin bundled masih tetap ada di peta ekspor SDK yang dihasilkan
demi kompatibilitas dan pemeliharaan plugin bundled. Contoh saat ini mencakup
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, dan beberapa seam `plugin-sdk/matrix*`. Perlakukan itu sebagai
ekspor detail implementasi yang dicadangkan, bukan sebagai pola SDK yang direkomendasikan untuk
plugin pihak ketiga baru.

## Pipeline pemuatan

Saat startup, OpenClaw secara garis besar melakukan ini:

1. menemukan root plugin kandidat
2. membaca manifest native atau bundle yang kompatibel dan metadata paket
3. menolak kandidat yang tidak aman
4. menormalisasi konfigurasi plugin (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. memutuskan enablement untuk setiap kandidat
6. memuat modul native yang diaktifkan melalui jiti
7. memanggil hook native `register(api)` (atau `activate(api)` — alias legacy) dan mengumpulkan pendaftaran ke dalam registri plugin
8. mengekspos registri ke surface perintah/runtime

<Note>
`activate` adalah alias legacy untuk `register` — loader me-resolve mana pun yang ada (`def.register ?? def.activate`) dan memanggilnya pada titik yang sama. Semua plugin bundled menggunakan `register`; utamakan `register` untuk plugin baru.
</Note>

Gerbang keamanan terjadi **sebelum** eksekusi runtime. Kandidat diblokir
ketika entry keluar dari root plugin, path dapat ditulisi oleh siapa pun, atau kepemilikan path
terlihat mencurigakan untuk plugin non-bundled.

### Perilaku manifest-first

Manifest adalah source of truth control-plane. OpenClaw menggunakannya untuk:

- mengidentifikasi plugin
- menemukan channel/Skills/schema konfigurasi yang dideklarasikan atau kapabilitas bundle
- memvalidasi `plugins.entries.<id>.config`
- menambah label/placeholder Control UI
- menampilkan metadata instalasi/katalog
- mempertahankan descriptor aktivasi dan penyiapan yang ringan tanpa memuat runtime plugin

Untuk plugin native, modul runtime adalah bagian data-plane. Modul ini mendaftarkan
perilaku aktual seperti hook, tool, perintah, atau alur provider.

Blok `activation` dan `setup` manifest opsional tetap berada di control plane.
Blok ini adalah descriptor metadata saja untuk perencanaan aktivasi dan discovery penyiapan;
blok ini tidak menggantikan pendaftaran runtime, `register(...)`, atau `setupEntry`.
Konsumen aktivasi live pertama sekarang menggunakan petunjuk perintah, channel, dan provider
pada manifest untuk mempersempit pemuatan plugin sebelum materialisasi registri yang lebih luas:

- pemuatan CLI dipersempit ke plugin yang memiliki perintah utama yang diminta
- resolusi setup/plugin channel dipersempit ke plugin yang memiliki id
  channel yang diminta
- resolusi setup/runtime provider eksplisit dipersempit ke plugin yang memiliki
  id provider yang diminta

Discovery setup sekarang mengutamakan id milik descriptor seperti `setup.providers` dan
`setup.cliBackends` untuk mempersempit plugin kandidat sebelum kembali ke
`setup-api` untuk plugin yang masih memerlukan hook runtime saat setup. Jika lebih dari
satu plugin yang ditemukan mengklaim id provider setup atau backend CLI yang sama setelah dinormalisasi,
lookup setup menolak pemilik yang ambigu tersebut alih-alih bergantung pada urutan
discovery.

### Apa yang di-cache oleh loader

OpenClaw menyimpan cache in-process jangka pendek untuk:

- hasil discovery
- data registri manifest
- registri plugin yang dimuat

Cache ini mengurangi startup yang meledak-ledak dan overhead perintah berulang. Cache ini aman
untuk dipahami sebagai cache performa yang berumur pendek, bukan persistensi.

Catatan performa:

- Setel `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` atau
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` untuk menonaktifkan cache ini.
- Sesuaikan jendela cache dengan `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` dan
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Model registri

Plugin yang dimuat tidak langsung memutasi global core acak. Plugin mendaftar ke dalam
registri plugin pusat.

Registri melacak:

- catatan plugin (identitas, sumber, asal, status, diagnostik)
- tool
- hook legacy dan hook bertipe
- channel
- provider
- handler RPC Gateway
- rute HTTP
- registrar CLI
- layanan latar belakang
- perintah milik plugin

Fitur core kemudian membaca dari registri tersebut alih-alih berbicara langsung
dengan modul plugin. Ini menjaga arah pemuatan tetap satu arah:

- modul plugin -> pendaftaran registri
- runtime core -> konsumsi registri

Pemisahan itu penting untuk kemudahan pemeliharaan. Artinya sebagian besar surface core hanya
memerlukan satu titik integrasi: "baca registri", bukan "buat special-case untuk setiap modul plugin".

## Callback pengikatan percakapan

Plugin yang mengikat percakapan dapat bereaksi ketika persetujuan diselesaikan.

Gunakan `api.onConversationBindingResolved(...)` untuk menerima callback setelah sebuah permintaan bind
disetujui atau ditolak:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Field payload callback:

- `status`: `"approved"` atau `"denied"`
- `decision`: `"allow-once"`, `"allow-always"`, atau `"deny"`
- `binding`: binding yang telah diselesaikan untuk permintaan yang disetujui
- `request`: ringkasan permintaan asli, petunjuk detach, id pengirim, dan
  metadata percakapan

Callback ini hanya untuk notifikasi. Callback ini tidak mengubah siapa yang diizinkan untuk mengikat
suatu percakapan, dan callback ini berjalan setelah penanganan persetujuan core selesai.

## Hook runtime provider

Plugin provider sekarang memiliki dua lapisan:

- metadata manifest: `providerAuthEnvVars` untuk lookup auth env provider yang ringan
  sebelum runtime dimuat, `providerAuthAliases` untuk varian provider yang berbagi
  auth, `channelEnvVars` untuk lookup env/setup channel yang ringan sebelum runtime
  dimuat, ditambah `providerAuthChoices` untuk label onboarding/pilihan auth yang ringan dan
  metadata flag CLI sebelum runtime dimuat
- hook saat konfigurasi: `catalog` / `discovery` legacy ditambah `applyConfigDefaults`
- hook runtime: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw tetap memiliki loop agen generik, failover, penanganan transkrip, dan
kebijakan tool. Hook ini adalah surface extension untuk perilaku khusus provider tanpa
memerlukan seluruh transport inferensi kustom.

Gunakan manifest `providerAuthEnvVars` ketika provider memiliki kredensial berbasis env
yang harus dapat dilihat oleh jalur auth/status/model-picker generik tanpa memuat runtime plugin.
Gunakan manifest `providerAuthAliases` ketika satu id provider harus menggunakan ulang
env var, profil auth, auth berbasis konfigurasi, dan pilihan onboarding API-key dari id provider lain.
Gunakan manifest `providerAuthChoices` ketika surface CLI onboarding/pilihan-auth
harus mengetahui id pilihan provider, label grup, dan wiring auth satu-flag sederhana
tanpa memuat runtime provider. Pertahankan `envVars` runtime provider untuk petunjuk yang menghadap operator
seperti label onboarding atau variabel setup OAuth client-id/client-secret.

Gunakan manifest `channelEnvVars` ketika sebuah channel memiliki auth atau setup berbasis env yang
harus dapat dilihat oleh fallback shell-env generik, pemeriksaan config/status, atau prompt setup
tanpa memuat runtime channel.

### Urutan hook dan penggunaannya

Untuk plugin model/provider, OpenClaw memanggil hook dalam urutan kasar ini.
Kolom "When to use" adalah panduan keputusan cepat.

| #   | Hook                              | Apa fungsinya                                                                                                  | Kapan digunakan                                                                                                                             |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Mempublikasikan konfigurasi provider ke `models.providers` selama pembuatan `models.json`                     | Provider memiliki katalog atau default base URL                                                                                             |
| 2   | `applyConfigDefaults`             | Menerapkan default konfigurasi global milik provider selama materialisasi konfigurasi                          | Default bergantung pada mode auth, env, atau semantik keluarga model provider                                                               |
| --  | _(lookup model bawaan)_           | OpenClaw mencoba jalur registri/katalog normal terlebih dahulu                                                | _(bukan hook plugin)_                                                                                                                       |
| 3   | `normalizeModelId`                | Menormalkan alias model-id legacy atau pratinjau sebelum lookup                                                | Provider memiliki pembersihan alias sebelum resolusi model kanonis                                                                          |
| 4   | `normalizeTransport`              | Menormalkan `api` / `baseUrl` keluarga provider sebelum perakitan model generik                                | Provider memiliki pembersihan transport untuk id provider kustom dalam keluarga transport yang sama                                         |
| 5   | `normalizeConfig`                 | Menormalkan `models.providers.<id>` sebelum resolusi runtime/provider                                          | Provider memerlukan pembersihan konfigurasi yang seharusnya berada bersama plugin; helper keluarga Google bundled juga menopang entri konfigurasi Google yang didukung |
| 6   | `applyNativeStreamingUsageCompat` | Menerapkan penulisan ulang kompatibilitas native streaming-usage ke provider konfigurasi                       | Provider memerlukan perbaikan metadata native streaming usage yang digerakkan oleh endpoint                                                 |
| 7   | `resolveConfigApiKey`             | Me-resolve auth penanda env untuk provider konfigurasi sebelum pemuatan auth runtime                           | Provider memiliki resolusi API key penanda env milik provider; `amazon-bedrock` juga memiliki resolver penanda env AWS bawaan di sini     |
| 8   | `resolveSyntheticAuth`            | Menampilkan auth lokal/self-hosted atau auth berbasis konfigurasi tanpa menyimpan plaintext                    | Provider dapat beroperasi dengan penanda kredensial synthetic/lokal                                                                         |
| 9   | `resolveExternalAuthProfiles`     | Melapisi profil auth eksternal milik provider; default `persistence` adalah `runtime-only` untuk kredensial milik CLI/app | Provider menggunakan ulang kredensial auth eksternal tanpa menyimpan refresh token hasil salin                                              |
| 10  | `shouldDeferSyntheticProfileAuth` | Menurunkan prioritas placeholder profil synthetic yang tersimpan di bawah auth berbasis env/konfigurasi       | Provider menyimpan profil placeholder synthetic yang seharusnya tidak menang prioritas                                                      |
| 11  | `resolveDynamicModel`             | Fallback sinkron untuk id model milik provider yang belum ada di registri lokal                                | Provider menerima id model upstream arbitrer                                                                                                |
| 12  | `prepareDynamicModel`             | Warm-up asinkron, lalu `resolveDynamicModel` dijalankan lagi                                                   | Provider memerlukan metadata jaringan sebelum me-resolve id yang tidak dikenal                                                              |
| 13  | `normalizeResolvedModel`          | Penulisan ulang final sebelum embedded runner menggunakan model yang telah di-resolve                          | Provider memerlukan penulisan ulang transport tetapi tetap menggunakan transport core                                                       |
| 14  | `contributeResolvedModelCompat`   | Menyumbangkan flag kompatibilitas untuk model vendor di balik transport kompatibel lain                        | Provider mengenali modelnya sendiri pada transport proksi tanpa mengambil alih provider                                                     |
| 15  | `capabilities`                    | Metadata transkrip/tooling milik provider yang digunakan oleh logika core bersama                              | Provider memerlukan keunikan transkrip/keluarga provider                                                                                    |
| 16  | `normalizeToolSchemas`            | Menormalkan schema tool sebelum embedded runner melihatnya                                                     | Provider memerlukan pembersihan schema keluarga transport                                                                                   |
| 17  | `inspectToolSchemas`              | Menampilkan diagnostik schema milik provider setelah normalisasi                                               | Provider ingin peringatan keyword tanpa mengajarkan aturan provider-spesifik ke core                                                       |
| 18  | `resolveReasoningOutputMode`      | Memilih kontrak output reasoning native vs bertag                                                              | Provider memerlukan output reasoning/final bertag alih-alih field native                                                                   |
| 19  | `prepareExtraParams`              | Normalisasi param permintaan sebelum wrapper opsi stream generik                                               | Provider memerlukan param permintaan default atau pembersihan param per-provider                                                            |
| 20  | `createStreamFn`                  | Sepenuhnya mengganti jalur stream normal dengan transport kustom                                               | Provider memerlukan wire protocol kustom, bukan sekadar wrapper                                                                             |
| 21  | `wrapStreamFn`                    | Wrapper stream setelah wrapper generik diterapkan                                                              | Provider memerlukan wrapper kompatibilitas header/body/model permintaan tanpa transport kustom                                              |
| 22  | `resolveTransportTurnState`       | Melampirkan header atau metadata transport per-turn native                                                     | Provider ingin transport generik mengirim identitas turn native provider                                                                    |
| 23  | `resolveWebSocketSessionPolicy`   | Melampirkan header WebSocket native atau kebijakan cool-down sesi                                              | Provider ingin transport WS generik menyetel header sesi atau kebijakan fallback                                                            |
| 24  | `formatApiKey`                    | Formatter profil auth: profil yang tersimpan menjadi string `apiKey` runtime                                   | Provider menyimpan metadata auth tambahan dan memerlukan bentuk token runtime kustom                                                        |
| 25  | `refreshOAuth`                    | Override refresh OAuth untuk endpoint refresh kustom atau kebijakan kegagalan refresh                          | Provider tidak cocok dengan refresher `pi-ai` bersama                                                                                       |
| 26  | `buildAuthDoctorHint`             | Petunjuk perbaikan yang ditambahkan saat refresh OAuth gagal                                                   | Provider memerlukan panduan perbaikan auth milik provider setelah refresh gagal                                                             |
| 27  | `matchesContextOverflowError`     | Matcher overflow context-window milik provider                                                                 | Provider memiliki error overflow mentah yang akan terlewat oleh heuristik generik                                                           |
| 28  | `classifyFailoverReason`          | Klasifikasi alasan failover milik provider                                                                     | Provider dapat memetakan error API/transport mentah ke rate-limit/overload/dll.                                                            |
| 29  | `isCacheTtlEligible`              | Kebijakan prompt-cache untuk provider proksi/backhaul                                                          | Provider memerlukan pengaturan cache TTL khusus proksi                                                                                      |
| 30  | `buildMissingAuthMessage`         | Pengganti pesan pemulihan missing-auth generik                                                                 | Provider memerlukan petunjuk pemulihan missing-auth yang spesifik untuk provider                                                            |
| 31  | `suppressBuiltInModel`            | Penekanan model upstream usang ditambah petunjuk error opsional yang menghadap pengguna                        | Provider perlu menyembunyikan baris upstream yang usang atau menggantinya dengan petunjuk vendor                                           |
| 32  | `augmentModelCatalog`             | Baris katalog synthetic/final yang ditambahkan setelah discovery                                               | Provider memerlukan baris forward-compat synthetic di `models list` dan picker                                                              |
| 33  | `isBinaryThinking`                | Toggle reasoning hidup/mati untuk provider binary-thinking                                                     | Provider hanya mengekspos binary thinking hidup/mati                                                                                        |
| 34  | `supportsXHighThinking`           | Dukungan reasoning `xhigh` untuk model tertentu                                                                | Provider ingin `xhigh` hanya pada subset model tertentu                                                                                     |
| 35  | `resolveDefaultThinkingLevel`     | Level `/think` default untuk keluarga model tertentu                                                           | Provider memiliki kebijakan `/think` default untuk suatu keluarga model                                                                     |
| 36  | `isModernModelRef`                | Matcher model modern untuk filter profil live dan pemilihan smoke                                              | Provider memiliki pencocokan preferred-model live/smoke                                                                                     |
| 37  | `prepareRuntimeAuth`              | Menukar kredensial yang dikonfigurasi menjadi token/key runtime aktual tepat sebelum inferensi                | Provider memerlukan pertukaran token atau kredensial permintaan berumur pendek                                                              |
| 38  | `resolveUsageAuth`                | Me-resolve kredensial penggunaan/penagihan untuk `/usage` dan surface status terkait                          | Provider memerlukan parsing token penggunaan/kuota kustom atau kredensial penggunaan yang berbeda                                          |
| 39  | `fetchUsageSnapshot`              | Mengambil dan menormalkan snapshot penggunaan/kuota provider-spesifik setelah auth di-resolve                 | Provider memerlukan endpoint penggunaan atau parser payload yang spesifik untuk provider                                                    |
| 40  | `createEmbeddingProvider`         | Membangun adaptor embedding milik provider untuk memory/search                                                 | Perilaku embedding memory harus berada bersama plugin provider                                                                              |
| 41  | `buildReplayPolicy`               | Mengembalikan kebijakan replay yang mengontrol penanganan transkrip untuk provider                            | Provider memerlukan kebijakan transkrip kustom (misalnya, menghapus blok thinking)                                                         |
| 42  | `sanitizeReplayHistory`           | Menulis ulang riwayat replay setelah pembersihan transkrip generik                                            | Provider memerlukan penulisan ulang replay yang spesifik untuk provider di luar helper Compaction bersama                                  |
| 43  | `validateReplayTurns`             | Validasi atau pembentukan ulang replay-turn final sebelum embedded runner                                     | Transport provider memerlukan validasi turn yang lebih ketat setelah sanitasi generik                                                      |
| 44  | `onModelSelected`                 | Menjalankan efek samping pasca-pemilihan milik provider                                                       | Provider memerlukan telemetri atau state milik provider saat sebuah model menjadi aktif                                                    |

`normalizeModelId`, `normalizeTransport`, dan `normalizeConfig` pertama-tama memeriksa
plugin provider yang cocok, lalu melanjutkan ke plugin provider lain yang mampu menggunakan hook
sampai salah satunya benar-benar mengubah model id atau transport/config. Ini menjaga
shim provider alias/kompatibilitas tetap berfungsi tanpa mengharuskan pemanggil mengetahui plugin
bundled mana yang memiliki penulisan ulang tersebut. Jika tidak ada hook provider yang menulis ulang
entri konfigurasi keluarga Google yang didukung, normalizer konfigurasi Google bundled tetap menerapkan
pembersihan kompatibilitas tersebut.

Jika provider memerlukan wire protocol yang sepenuhnya kustom atau eksekutor permintaan kustom,
itu adalah kelas extension yang berbeda. Hook ini ditujukan untuk perilaku provider
yang tetap berjalan pada loop inferensi normal OpenClaw.

### Contoh provider

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Contoh bawaan

- Anthropic menggunakan `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  dan `wrapStreamFn` karena plugin ini memiliki forward-compat Claude 4.6,
  petunjuk keluarga provider, panduan perbaikan auth, integrasi endpoint penggunaan,
  kelayakan prompt-cache, default konfigurasi yang sadar auth, kebijakan thinking
  default/adaptif Claude, dan pembentukan stream khusus Anthropic untuk
  beta header, `/fast` / `serviceTier`, dan `context1m`.
- Helper stream khusus Claude milik Anthropic untuk saat ini tetap berada di
  seam `api.ts` / `contract-api.ts` publik milik plugin bundled itu sendiri. Surface paket
  tersebut mengekspor `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`, dan builder wrapper
  Anthropic tingkat lebih rendah alih-alih memperluas SDK generik di sekitar
  aturan beta-header satu provider.
- OpenAI menggunakan `resolveDynamicModel`, `normalizeResolvedModel`, dan
  `capabilities` ditambah `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, dan `isModernModelRef`
  karena plugin ini memiliki forward-compat GPT-5.4, normalisasi langsung OpenAI
  `openai-completions` -> `openai-responses`, petunjuk auth yang sadar Codex,
  suppressi Spark, baris daftar OpenAI synthetic, dan kebijakan thinking /
  live-model GPT-5; keluarga stream `openai-responses-defaults` memiliki
  wrapper OpenAI Responses native bersama untuk attribution header,
  `/fast`/`serviceTier`, text verbosity, pencarian web native Codex,
  pembentukan payload reasoning-compat, dan manajemen konteks Responses.
- OpenRouter menggunakan `catalog` ditambah `resolveDynamicModel` dan
  `prepareDynamicModel` karena provider ini bersifat pass-through dan dapat mengekspos
  model id baru sebelum katalog statis OpenClaw diperbarui; plugin ini juga menggunakan
  `capabilities`, `wrapStreamFn`, dan `isCacheTtlEligible` untuk menjaga
  header permintaan spesifik provider, metadata routing, patch reasoning, dan
  kebijakan prompt-cache tetap berada di luar core. Kebijakan replay-nya berasal dari
  keluarga `passthrough-gemini`, sedangkan keluarga stream `openrouter-thinking`
  memiliki injeksi reasoning proksi dan skip model yang tidak didukung / `auto`.
- GitHub Copilot menggunakan `catalog`, `auth`, `resolveDynamicModel`, dan
  `capabilities` ditambah `prepareRuntimeAuth` dan `fetchUsageSnapshot` karena plugin ini
  memerlukan device login milik provider, perilaku fallback model, keunikan transkrip Claude,
  pertukaran token GitHub -> token Copilot, dan endpoint penggunaan milik provider.
- OpenAI Codex menggunakan `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, dan `augmentModelCatalog` ditambah
  `prepareExtraParams`, `resolveUsageAuth`, dan `fetchUsageSnapshot` karena plugin ini
  masih berjalan di atas transport OpenAI core tetapi memiliki normalisasi
  transport/base URL, kebijakan fallback refresh OAuth, pilihan transport default,
  baris katalog Codex synthetic, dan integrasi endpoint penggunaan ChatGPT; plugin ini
  berbagi keluarga stream `openai-responses-defaults` yang sama dengan OpenAI langsung.
- Google AI Studio dan Gemini CLI OAuth menggunakan `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, dan `isModernModelRef` karena
  keluarga replay `google-gemini` memiliki fallback forward-compat Gemini 3.1,
  validasi replay Gemini native, sanitasi replay bootstrap, mode output reasoning
  bertag, dan pencocokan model modern, sedangkan keluarga stream
  `google-thinking` memiliki normalisasi payload thinking Gemini;
  Gemini CLI OAuth juga menggunakan `formatApiKey`, `resolveUsageAuth`, dan
  `fetchUsageSnapshot` untuk formatting token, parsing token, dan wiring endpoint
  kuota.
- Anthropic Vertex menggunakan `buildReplayPolicy` melalui
  keluarga replay `anthropic-by-model` sehingga pembersihan replay khusus Claude tetap
  dibatasi pada id Claude alih-alih setiap transport `anthropic-messages`.
- Amazon Bedrock menggunakan `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, dan `resolveDefaultThinkingLevel` karena plugin ini memiliki
  klasifikasi error throttle/not-ready/context-overflow khusus Bedrock
  untuk lalu lintas Anthropic-on-Bedrock; kebijakan replay-nya tetap berbagi
  guard `anthropic-by-model` khusus Claude yang sama.
- OpenRouter, Kilocode, Opencode, dan Opencode Go menggunakan `buildReplayPolicy`
  melalui keluarga replay `passthrough-gemini` karena mereka memproksikan model Gemini
  melalui transport yang kompatibel dengan OpenAI dan memerlukan
  sanitasi thought-signature Gemini tanpa validasi replay Gemini native atau
  penulisan ulang bootstrap.
- MiniMax menggunakan `buildReplayPolicy` melalui
  keluarga replay `hybrid-anthropic-openai` karena satu provider memiliki
  semantik pesan Anthropic dan OpenAI-compatible; plugin ini mempertahankan penghapusan
  blok thinking khusus Claude di sisi Anthropic sambil meng-override mode output reasoning
  kembali ke native, dan keluarga stream `minimax-fast-mode` memiliki penulisan ulang model
  fast-mode pada jalur stream bersama.
- Moonshot menggunakan `catalog` ditambah `wrapStreamFn` karena plugin ini masih menggunakan
  transport OpenAI bersama tetapi memerlukan normalisasi payload thinking milik provider; keluarga
  stream `moonshot-thinking` memetakan konfigurasi ditambah state `/think` ke payload
  binary thinking native-nya.
- Kilocode menggunakan `catalog`, `capabilities`, `wrapStreamFn`, dan
  `isCacheTtlEligible` karena plugin ini memerlukan header permintaan milik provider,
  normalisasi payload reasoning, petunjuk transkrip Gemini, dan pengaturan
  cache-TTL Anthropic; keluarga stream `kilocode-thinking` menjaga injeksi thinking Kilo
  tetap berada pada jalur stream proksi bersama sambil melewati `kilo/auto` dan
  model id proksi lain yang tidak mendukung payload reasoning eksplisit.
- Z.AI menggunakan `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, dan `fetchUsageSnapshot` karena plugin ini memiliki fallback GLM-5,
  default `tool_stream`, UX binary thinking, pencocokan model modern, dan
  pengambilan auth penggunaan + kuota; keluarga stream `tool-stream-default-on` menjaga
  wrapper `tool_stream` default-on tetap berada di luar glue tulisan tangan per-provider.
- xAI menggunakan `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, dan `isModernModelRef`
  karena plugin ini memiliki normalisasi transport xAI Responses native, penulisan ulang alias
  fast-mode Grok, default `tool_stream`, pembersihan strict-tool / payload reasoning,
  penggunaan ulang auth fallback untuk tool milik plugin, resolusi model Grok
  forward-compat, dan patch kompatibilitas milik provider seperti profil
  tool-schema xAI, keyword schema yang tidak didukung, `web_search` native, dan
  decoding argumen tool-call entitas HTML.
- Mistral, OpenCode Zen, dan OpenCode Go hanya menggunakan `capabilities` untuk menjaga
  keunikan transkrip/tooling tetap berada di luar core.
- Provider bundled yang hanya katalog seperti `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, dan `volcengine` menggunakan
  `catalog` saja.
- Qwen menggunakan `catalog` untuk text provider-nya ditambah pendaftaran shared
  media-understanding dan video-generation untuk surface multimodal-nya.
- MiniMax dan Xiaomi menggunakan `catalog` ditambah hook penggunaan karena perilaku `/usage`
  mereka dimiliki plugin meskipun inferensi tetap berjalan melalui transport bersama.

## Helper runtime

Plugin dapat mengakses helper core tertentu melalui `api.runtime`. Untuk TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Catatan:

- `textToSpeech` mengembalikan payload keluaran TTS core normal untuk surface file/catatan suara.
- Menggunakan konfigurasi core `messages.tts` dan pemilihan provider.
- Mengembalikan buffer audio PCM + sample rate. Plugin harus melakukan resample/encode untuk provider.
- `listVoices` bersifat opsional per provider. Gunakan ini untuk voice picker milik vendor atau alur setup.
- Daftar suara dapat mencakup metadata yang lebih kaya seperti locale, gender, dan tag personality untuk picker yang sadar provider.
- OpenAI dan ElevenLabs saat ini mendukung teleponi. Microsoft tidak.

Plugin juga dapat mendaftarkan speech provider melalui `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Catatan:

- Pertahankan kebijakan TTS, fallback, dan pengiriman balasan di core.
- Gunakan speech provider untuk perilaku sintesis milik vendor.
- Input `edge` Microsoft legacy dinormalisasi ke id provider `microsoft`.
- Model kepemilikan yang diutamakan berorientasi perusahaan: satu plugin vendor dapat memiliki
  provider teks, ucapan, gambar, dan media di masa depan saat OpenClaw menambahkan kontrak
  kapabilitas tersebut.

Untuk pemahaman gambar/audio/video, plugin mendaftarkan satu provider
media-understanding bertipe alih-alih bag key/value generik:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Catatan:

- Pertahankan orkestrasi, fallback, konfigurasi, dan wiring channel di core.
- Pertahankan perilaku vendor di plugin provider.
- Ekspansi aditif harus tetap bertipe: metode opsional baru, field hasil opsional
  baru, kapabilitas opsional baru.
- Pembuatan video sudah mengikuti pola yang sama:
  - core memiliki kontrak kapabilitas dan helper runtime
  - plugin vendor mendaftarkan `api.registerVideoGenerationProvider(...)`
  - plugin fitur/channel mengonsumsi `api.runtime.videoGeneration.*`

Untuk helper runtime media-understanding, plugin dapat memanggil:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Untuk transkripsi audio, plugin dapat menggunakan runtime media-understanding
atau alias STT yang lebih lama:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Catatan:

- `api.runtime.mediaUnderstanding.*` adalah surface bersama yang diutamakan untuk
  pemahaman gambar/audio/video.
- Menggunakan konfigurasi audio media-understanding core (`tools.media.audio`) dan urutan fallback provider.
- Mengembalikan `{ text: undefined }` ketika tidak ada keluaran transkripsi yang dihasilkan (misalnya input dilewati/tidak didukung).
- `api.runtime.stt.transcribeAudioFile(...)` tetap ada sebagai alias kompatibilitas.

Plugin juga dapat meluncurkan eksekusi subagen latar belakang melalui `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Catatan:

- `provider` dan `model` adalah override per eksekusi yang opsional, bukan perubahan sesi yang persisten.
- OpenClaw hanya menghormati field override tersebut untuk pemanggil tepercaya.
- Untuk eksekusi fallback milik plugin, operator harus melakukan opt-in dengan `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Gunakan `plugins.entries.<id>.subagent.allowedModels` untuk membatasi plugin tepercaya ke target kanonis `provider/model` tertentu, atau `"*"` untuk secara eksplisit mengizinkan target apa pun.
- Eksekusi subagen plugin yang tidak tepercaya tetap berfungsi, tetapi permintaan override ditolak alih-alih diam-diam fallback.

Untuk pencarian web, plugin dapat mengonsumsi helper runtime bersama alih-alih
masuk ke wiring tool agen:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Plugin juga dapat mendaftarkan web-search provider melalui
`api.registerWebSearchProvider(...)`.

Catatan:

- Pertahankan pemilihan provider, resolusi kredensial, dan semantik permintaan bersama di core.
- Gunakan web-search provider untuk transport pencarian vendor-spesifik.
- `api.runtime.webSearch.*` adalah surface bersama yang diutamakan untuk plugin fitur/channel yang memerlukan perilaku pencarian tanpa bergantung pada wrapper tool agen.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: hasilkan gambar menggunakan rantai provider pembuatan gambar yang dikonfigurasi.
- `listProviders(...)`: daftar provider pembuatan gambar yang tersedia dan kapabilitasnya.

## Rute HTTP Gateway

Plugin dapat mengekspos endpoint HTTP dengan `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Field rute:

- `path`: path rute di bawah server HTTP gateway.
- `auth`: wajib. Gunakan `"gateway"` untuk mewajibkan auth gateway normal, atau `"plugin"` untuk auth/verifikasi webhook yang dikelola plugin.
- `match`: opsional. `"exact"` (default) atau `"prefix"`.
- `replaceExisting`: opsional. Memungkinkan plugin yang sama mengganti pendaftaran rute yang sudah ada miliknya sendiri.
- `handler`: kembalikan `true` saat rute menangani permintaan.

Catatan:

- `api.registerHttpHandler(...)` telah dihapus dan akan menyebabkan error saat pemuatan plugin. Gunakan `api.registerHttpRoute(...)` sebagai gantinya.
- Rute plugin harus mendeklarasikan `auth` secara eksplisit.
- Konflik `path + match` yang persis sama ditolak kecuali `replaceExisting: true`, dan satu plugin tidak dapat mengganti rute plugin lain.
- Rute yang tumpang tindih dengan level `auth` berbeda ditolak. Pertahankan rantai fallthrough `exact`/`prefix` hanya pada level auth yang sama.
- Rute `auth: "plugin"` **tidak** menerima scope runtime operator secara otomatis. Rute ini ditujukan untuk webhook/verifikasi tanda tangan yang dikelola plugin, bukan panggilan helper Gateway berprivileg.
- Rute `auth: "gateway"` berjalan di dalam scope runtime permintaan Gateway, tetapi scope itu sengaja konservatif:
  - auth bearer shared-secret (`gateway.auth.mode = "token"` / `"password"`) menjaga scope runtime rute plugin tetap terkunci pada `operator.write`, bahkan jika pemanggil mengirim `x-openclaw-scopes`
  - mode HTTP tepercaya yang membawa identitas (misalnya `trusted-proxy` atau `gateway.auth.mode = "none"` pada ingress privat) menghormati `x-openclaw-scopes` hanya ketika header tersebut memang ada
  - jika `x-openclaw-scopes` tidak ada pada permintaan rute plugin yang membawa identitas tersebut, scope runtime fallback ke `operator.write`
- Aturan praktis: jangan menganggap rute plugin dengan auth gateway sebagai surface admin implisit. Jika rute Anda memerlukan perilaku khusus admin, wajibkan mode auth yang membawa identitas dan dokumentasikan kontrak header `x-openclaw-scopes` yang eksplisit.

## Path impor Plugin SDK

Gunakan subpath SDK alih-alih impor monolitik `openclaw/plugin-sdk` saat
menulis plugin:

- `openclaw/plugin-sdk/plugin-entry` untuk primitif pendaftaran plugin.
- `openclaw/plugin-sdk/core` untuk kontrak umum bersama yang menghadap plugin.
- `openclaw/plugin-sdk/config-schema` untuk ekspor skema Zod root `openclaw.json`
  (`OpenClawSchema`).
- Primitif channel stabil seperti `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input`, dan
  `openclaw/plugin-sdk/webhook-ingress` untuk wiring setup/auth/balasan/webhook
  bersama. `channel-inbound` adalah rumah bersama untuk debounce, pencocokan mention,
  helper kebijakan mention inbound, pemformatan envelope, dan helper konteks
  envelope inbound.
  `channel-setup` adalah seam setup narrow optional-install.
  `setup-runtime` adalah surface setup yang aman untuk runtime yang digunakan oleh `setupEntry` /
  startup yang ditangguhkan, termasuk adaptor patch setup yang aman untuk impor.
  `setup-adapter-runtime` adalah seam adaptor account-setup yang sadar env.
  `setup-tools` adalah seam helper kecil untuk CLI/arsip/dokumen (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Subpath domain seperti `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store`, dan
  `openclaw/plugin-sdk/directory-runtime` untuk helper runtime/konfigurasi bersama.
  `telegram-command-config` adalah seam publik sempit untuk normalisasi/validasi
  perintah kustom Telegram dan tetap tersedia meskipun surface kontrak Telegram bundled
  untuk sementara tidak tersedia.
  `text-runtime` adalah seam teks/markdown/logging bersama, termasuk
  penghapusan teks yang terlihat oleh asisten, helper render/chunking markdown, helper
  redaksi, helper directive-tag, dan utilitas safe-text.
- Seam channel yang spesifik persetujuan sebaiknya mengutamakan satu kontrak
  `approvalCapability` pada plugin. Core kemudian membaca auth, pengiriman, render,
  native-routing, dan perilaku lazy native-handler persetujuan melalui satu kapabilitas itu
  alih-alih mencampurkan perilaku persetujuan ke field plugin yang tidak terkait.
- `openclaw/plugin-sdk/channel-runtime` sudah deprecated dan hanya tersisa sebagai
  shim kompatibilitas untuk plugin lama. Kode baru sebaiknya mengimpor primitif generik yang lebih sempit,
  dan kode repo tidak boleh menambahkan impor baru terhadap shim tersebut.
- Internal extension bundled tetap privat. Plugin eksternal sebaiknya hanya menggunakan
  subpath `openclaw/plugin-sdk/*`. Kode core/test OpenClaw dapat menggunakan entry point
  publik repo di bawah root paket plugin seperti `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, dan file yang discope sempit seperti
  `login-qr-api.js`. Jangan pernah mengimpor `src/*` dari paket plugin dari core atau dari
  extension lain.
- Pemisahan entry point repo:
  `<plugin-package-root>/api.js` adalah barrel helper/types,
  `<plugin-package-root>/runtime-api.js` adalah barrel khusus runtime,
  `<plugin-package-root>/index.js` adalah entry plugin bundled,
  dan `<plugin-package-root>/setup-entry.js` adalah entry plugin setup.
- Contoh provider bundled saat ini:
  - Anthropic menggunakan `api.js` / `contract-api.js` untuk helper stream Claude seperti
    `wrapAnthropicProviderStream`, helper beta-header, dan parsing `service_tier`.
  - OpenAI menggunakan `api.js` untuk builder provider, helper model default, dan
    builder provider realtime.
  - OpenRouter menggunakan `api.js` untuk builder provider-nya ditambah helper
    onboarding/config, sedangkan `register.runtime.js` masih dapat mengekspor ulang helper
    generik `plugin-sdk/provider-stream` untuk penggunaan lokal repo.
- Entry point publik yang dimuat melalui facade mengutamakan snapshot konfigurasi runtime aktif
  ketika ada, lalu fallback ke file konfigurasi yang di-resolve di disk ketika
  OpenClaw belum menyajikan snapshot runtime.
- Primitif generik bersama tetap menjadi kontrak SDK publik yang diutamakan. Sekumpulan kecil
  seam helper bermerek channel bundled yang dicadangkan untuk kompatibilitas masih ada. Perlakukan itu sebagai
  seam pemeliharaan bundled/kompatibilitas, bukan target impor pihak ketiga yang baru; kontrak lintas-channel baru tetap harus berada pada subpath generik `plugin-sdk/*` atau barrel `api.js` /
  `runtime-api.js` lokal plugin.

Catatan kompatibilitas:

- Hindari barrel root `openclaw/plugin-sdk` untuk kode baru.
- Utamakan primitif stabil yang sempit terlebih dahulu. Subpath setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool yang lebih baru adalah kontrak yang dituju untuk pekerjaan plugin
  bundled dan eksternal yang baru.
  Parsing/pencocokan target berada di `openclaw/plugin-sdk/channel-targets`.
  Gerbang aksi pesan dan helper message-id reaksi berada di
  `openclaw/plugin-sdk/channel-actions`.
- Barrel helper khusus extension bundled tidak stabil secara default. Jika sebuah
  helper hanya dibutuhkan oleh extension bundled, simpan di balik seam
  `api.js` atau `runtime-api.js` lokal extension tersebut alih-alih mempromosikannya ke
  `openclaw/plugin-sdk/<extension>`.
- Seam helper bersama yang baru harus generik, bukan bermerek channel. Parsing target bersama
  berada di `openclaw/plugin-sdk/channel-targets`; internal khusus channel
  tetap berada di balik seam `api.js` atau `runtime-api.js` lokal plugin pemiliknya.
- Subpath spesifik kapabilitas seperti `image-generation`,
  `media-understanding`, dan `speech` ada karena plugin bundled/native
  menggunakannya saat ini. Keberadaannya sendiri tidak berarti setiap helper yang diekspor adalah
  kontrak eksternal jangka panjang yang dibekukan.

## Skema message tool

Plugin sebaiknya memiliki kontribusi skema `describeMessageTool(...)` khusus channel.
Pertahankan field khusus provider di plugin, bukan di core bersama.

Untuk fragmen skema portabel bersama, gunakan ulang helper generik yang diekspor melalui
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` untuk payload gaya grid tombol
- `createMessageToolCardSchema()` untuk payload kartu terstruktur

Jika suatu bentuk skema hanya masuk akal untuk satu provider, definisikan di
source plugin itu sendiri alih-alih mempromosikannya ke SDK bersama.

## Resolusi target channel

Plugin channel sebaiknya memiliki semantik target khusus channel. Pertahankan host
outbound bersama tetap generik dan gunakan surface adaptor pesan untuk aturan provider:

- `messaging.inferTargetChatType({ to })` memutuskan apakah target yang telah dinormalisasi
  harus diperlakukan sebagai `direct`, `group`, atau `channel` sebelum lookup direktori.
- `messaging.targetResolver.looksLikeId(raw, normalized)` memberi tahu core apakah
  suatu input harus langsung dilewatkan ke resolusi mirip-id alih-alih pencarian direktori.
- `messaging.targetResolver.resolveTarget(...)` adalah fallback plugin saat
  core memerlukan resolusi akhir milik provider setelah normalisasi atau setelah
  direktori tidak menemukan hasil.
- `messaging.resolveOutboundSessionRoute(...)` memiliki konstruksi rute sesi
  khusus provider setelah sebuah target di-resolve.

Pemisahan yang direkomendasikan:

- Gunakan `inferTargetChatType` untuk keputusan kategori yang harus terjadi sebelum
  pencarian peer/group.
- Gunakan `looksLikeId` untuk pemeriksaan "perlakukan ini sebagai id target eksplisit/native".
- Gunakan `resolveTarget` untuk fallback normalisasi khusus provider, bukan untuk
  pencarian direktori yang luas.
- Pertahankan id native provider seperti chat id, thread id, JID, handle, dan room
  id di dalam nilai `target` atau param khusus provider, bukan di field SDK generik.

## Direktori berbasis konfigurasi

Plugin yang menurunkan entri direktori dari konfigurasi sebaiknya menjaga logika itu di
plugin dan menggunakan ulang helper bersama dari
`openclaw/plugin-sdk/directory-runtime`.

Gunakan ini ketika sebuah channel memerlukan peer/group berbasis konfigurasi seperti:

- peer DM yang digerakkan allowlist
- peta channel/group yang dikonfigurasi
- fallback direktori statis yang dibatasi akun

Helper bersama di `directory-runtime` hanya menangani operasi generik:

- penyaringan kueri
- penerapan batas
- helper deduplikasi/normalisasi
- membangun `ChannelDirectoryEntry[]`

Pemeriksaan akun dan normalisasi id khusus channel sebaiknya tetap berada di
implementasi plugin.

## Katalog provider

Plugin provider dapat mendefinisikan katalog model untuk inferensi dengan
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` mengembalikan bentuk yang sama yang ditulis OpenClaw ke dalam
`models.providers`:

- `{ provider }` untuk satu entri provider
- `{ providers }` untuk beberapa entri provider

Gunakan `catalog` ketika plugin memiliki model id khusus provider, default base URL,
atau metadata model yang dijaga oleh auth.

`catalog.order` mengontrol kapan katalog plugin digabungkan relatif terhadap provider implisit bawaan OpenClaw:

- `simple`: provider biasa berbasis API key atau env
- `profile`: provider yang muncul ketika profil auth ada
- `paired`: provider yang mensintesis beberapa entri provider yang saling terkait
- `late`: pass terakhir, setelah provider implisit lainnya

Provider yang lebih akhir menang pada benturan key, sehingga plugin dapat dengan sengaja
meng-override entri provider bawaan dengan id provider yang sama.

Kompatibilitas:

- `discovery` tetap berfungsi sebagai alias legacy
- jika `catalog` dan `discovery` sama-sama didaftarkan, OpenClaw menggunakan `catalog`

## Inspeksi channel read-only

Jika plugin Anda mendaftarkan sebuah channel, utamakan mengimplementasikan
`plugin.config.inspectAccount(cfg, accountId)` bersama `resolveAccount(...)`.

Mengapa:

- `resolveAccount(...)` adalah jalur runtime. Jalur ini boleh mengasumsikan kredensial
  telah sepenuhnya dimaterialisasi dan dapat gagal cepat ketika secret yang diperlukan tidak ada.
- Jalur perintah read-only seperti `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`, dan alur perbaikan
  doctor/config tidak seharusnya perlu mematerialisasi kredensial runtime hanya untuk
  mendeskripsikan konfigurasi.

Perilaku `inspectAccount(...)` yang direkomendasikan:

- Hanya kembalikan state akun yang deskriptif.
- Pertahankan `enabled` dan `configured`.
- Sertakan field sumber/status kredensial jika relevan, seperti:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Anda tidak perlu mengembalikan nilai token mentah hanya untuk melaporkan
  ketersediaan read-only. Mengembalikan `tokenStatus: "available"` (dan field sumber
  yang cocok) sudah cukup untuk perintah bergaya status.
- Gunakan `configured_unavailable` ketika sebuah kredensial dikonfigurasi melalui SecretRef tetapi
  tidak tersedia pada jalur perintah saat ini.

Ini memungkinkan perintah read-only melaporkan "configured but unavailable in this command
path" alih-alih crash atau salah melaporkan akun sebagai belum dikonfigurasi.

## Paket pack

Direktori plugin dapat menyertakan `package.json` dengan `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Setiap entri menjadi sebuah plugin. Jika pack mencantumkan beberapa extension, id plugin
menjadi `name/<fileBase>`.

Jika plugin Anda mengimpor dependensi npm, instal dependensi tersebut di direktori itu agar
`node_modules` tersedia (`npm install` / `pnpm install`).

Guardrail keamanan: setiap entri `openclaw.extensions` harus tetap berada di dalam direktori plugin
setelah resolusi symlink. Entri yang keluar dari direktori paket akan
ditolak.

Catatan keamanan: `openclaw plugins install` menginstal dependensi plugin dengan
`npm install --omit=dev --ignore-scripts` (tanpa lifecycle script, tanpa dev dependency saat runtime). Pertahankan tree dependensi plugin
tetap "pure JS/TS" dan hindari paket yang memerlukan build `postinstall`.

Opsional: `openclaw.setupEntry` dapat menunjuk ke modul ringan khusus setup.
Ketika OpenClaw memerlukan surface setup untuk plugin channel yang dinonaktifkan, atau
ketika plugin channel diaktifkan tetapi masih belum dikonfigurasi, OpenClaw memuat `setupEntry`
alih-alih entri plugin penuh. Ini menjaga startup dan setup tetap lebih ringan
ketika entri plugin utama Anda juga mewiring tool, hook, atau kode
khusus runtime lainnya.

Opsional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
dapat mengikutsertakan plugin channel ke jalur `setupEntry` yang sama selama fase
startup pre-listen gateway, bahkan ketika channel sudah dikonfigurasi.

Gunakan ini hanya ketika `setupEntry` sepenuhnya mencakup surface startup yang harus ada
sebelum gateway mulai mendengarkan. Dalam praktiknya, itu berarti entri setup
harus mendaftarkan setiap kapabilitas milik channel yang menjadi dependensi startup, seperti:

- pendaftaran channel itu sendiri
- rute HTTP apa pun yang harus tersedia sebelum gateway mulai mendengarkan
- metode gateway, tool, atau layanan apa pun yang harus ada selama jendela yang sama

Jika entri penuh Anda masih memiliki kapabilitas startup yang diperlukan, jangan aktifkan
flag ini. Pertahankan plugin pada perilaku default dan biarkan OpenClaw memuat
entri penuh saat startup.

Channel bundled juga dapat memublikasikan helper contract-surface khusus setup yang core
dapat konsultasikan sebelum runtime channel penuh dimuat. Surface promosi setup
saat ini adalah:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Core menggunakan surface itu ketika perlu mempromosikan konfigurasi channel legacy akun tunggal
ke `channels.<id>.accounts.*` tanpa memuat entri plugin penuh.
Matrix adalah contoh bundled saat ini: plugin ini hanya memindahkan key auth/bootstrap ke akun
hasil promosi bernama ketika akun bernama sudah ada, dan plugin ini dapat mempertahankan
key default-account non-kanonis yang telah dikonfigurasi alih-alih selalu membuat
`accounts.default`.

Adaptor patch setup tersebut menjaga discovery contract-surface bundled tetap lazy. Waktu impor
tetap ringan; surface promosi hanya dimuat pada penggunaan pertama alih-alih
masuk kembali ke startup channel bundled saat impor modul.

Ketika surface startup tersebut mencakup metode RPC Gateway, pertahankan pada
prefiks spesifik plugin. Namespace admin core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) tetap dicadangkan dan selalu di-resolve
ke `operator.admin`, bahkan jika plugin meminta scope yang lebih sempit.

Contoh:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadata katalog channel

Plugin channel dapat mengiklankan metadata setup/discovery melalui `openclaw.channel` dan
petunjuk instalasi melalui `openclaw.install`. Ini menjaga data katalog core tetap kosong.

Contoh:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Chat self-hosted melalui bot webhook Nextcloud Talk.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Field `openclaw.channel` yang berguna di luar contoh minimal:

- `detailLabel`: label sekunder untuk surface katalog/status yang lebih kaya
- `docsLabel`: override teks tautan untuk tautan dokumen
- `preferOver`: id plugin/channel prioritas lebih rendah yang harus dikalahkan oleh entri katalog ini
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: kontrol copy surface pemilihan
- `markdownCapable`: menandai channel sebagai mampu markdown untuk keputusan pemformatan outbound
- `exposure.configured`: sembunyikan channel dari surface daftar channel yang dikonfigurasi ketika disetel ke `false`
- `exposure.setup`: sembunyikan channel dari picker setup/konfigurasi interaktif ketika disetel ke `false`
- `exposure.docs`: tandai channel sebagai internal/private untuk surface navigasi dokumen
- `showConfigured` / `showInSetup`: alias legacy masih diterima demi kompatibilitas; utamakan `exposure`
- `quickstartAllowFrom`: ikutsertakan channel ke alur `allowFrom` quickstart standar
- `forceAccountBinding`: wajibkan pengikatan akun eksplisit meskipun hanya ada satu akun
- `preferSessionLookupForAnnounceTarget`: utamakan lookup sesi saat me-resolve target announce

OpenClaw juga dapat menggabungkan **katalog channel eksternal** (misalnya, ekspor
registri MPM). Letakkan file JSON di salah satu lokasi berikut:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Atau arahkan `OPENCLAW_PLUGIN_CATALOG_PATHS` (atau `OPENCLAW_MPM_CATALOG_PATHS`) ke
satu atau lebih file JSON (dipisahkan dengan koma/titik koma/`PATH`). Setiap file harus
berisi `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Parser juga menerima `"packages"` atau `"plugins"` sebagai alias legacy untuk key `"entries"`.

## Plugin mesin konteks

Plugin mesin konteks memiliki orkestrasi konteks sesi untuk ingest, assembly,
dan Compaction. Daftarkan dari plugin Anda dengan
`api.registerContextEngine(id, factory)`, lalu pilih mesin aktif dengan
`plugins.slots.contextEngine`.

Gunakan ini ketika plugin Anda perlu mengganti atau memperluas pipeline konteks default
alih-alih hanya menambahkan pencarian memory atau hook.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Jika mesin Anda **tidak** memiliki algoritma Compaction, tetap implementasikan `compact()`
dan delegasikan secara eksplisit:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Menambahkan kapabilitas baru

Ketika sebuah plugin memerlukan perilaku yang tidak sesuai dengan API saat ini, jangan
melewati sistem plugin dengan akses privat ke internal. Tambahkan kapabilitas yang belum ada.

Urutan yang direkomendasikan:

1. definisikan kontrak core
   Putuskan perilaku bersama apa yang harus dimiliki core: kebijakan, fallback, merge konfigurasi,
   lifecycle, semantik yang menghadap channel, dan bentuk helper runtime.
2. tambahkan surface pendaftaran/runtime plugin yang bertipe
   Perluas `OpenClawPluginApi` dan/atau `api.runtime` dengan surface kapabilitas bertipe
   terkecil yang berguna.
3. hubungkan konsumen core + channel/fitur
   Plugin channel dan fitur harus mengonsumsi kapabilitas baru melalui core,
   bukan dengan langsung mengimpor implementasi vendor.
4. daftarkan implementasi vendor
   Plugin vendor kemudian mendaftarkan backend mereka terhadap kapabilitas tersebut.
5. tambahkan cakupan kontrak
   Tambahkan pengujian agar bentuk kepemilikan dan pendaftaran tetap eksplisit seiring waktu.

Inilah cara OpenClaw tetap opinionated tanpa menjadi hardcoded pada worldview satu
provider. Lihat [Capability Cookbook](/id/plugins/architecture)
untuk checklist file konkret dan contoh yang sudah dikerjakan.

### Checklist kapabilitas

Ketika Anda menambahkan kapabilitas baru, implementasinya biasanya harus menyentuh
surface berikut secara bersama:

- tipe kontrak core di `src/<capability>/types.ts`
- helper runner/runtime core di `src/<capability>/runtime.ts`
- surface pendaftaran API plugin di `src/plugins/types.ts`
- wiring registri plugin di `src/plugins/registry.ts`
- eksposur runtime plugin di `src/plugins/runtime/*` ketika plugin fitur/channel
  perlu mengonsumsinya
- helper capture/test di `src/test-utils/plugin-registration.ts`
- assertion kepemilikan/kontrak di `src/plugins/contracts/registry.ts`
- dokumen operator/plugin di `docs/`

Jika salah satu surface tersebut tidak ada, biasanya itu adalah tanda bahwa kapabilitas
tersebut belum sepenuhnya terintegrasi.

### Templat kapabilitas

Pola minimal:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Pola pengujian kontrak:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Ini menjaga aturannya tetap sederhana:

- core memiliki kontrak kapabilitas + orkestrasi
- plugin vendor memiliki implementasi vendor
- plugin fitur/channel mengonsumsi helper runtime
- pengujian kontrak menjaga kepemilikan tetap eksplisit
