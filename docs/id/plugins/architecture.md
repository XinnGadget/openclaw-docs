---
read_when:
    - Membangun atau men-debug Plugin OpenClaw native
    - Memahami model kapabilitas plugin atau batas kepemilikan
    - Mengerjakan pipeline pemuatan plugin atau registry
    - Mengimplementasikan hook runtime provider atau Plugin channel
sidebarTitle: Internals
summary: 'Internal Plugin: model kapabilitas, kepemilikan, kontrak, pipeline pemuatan, dan helper runtime'
title: Internal Plugin
x-i18n:
    generated_at: "2026-04-12T23:28:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 37361c1e9d2da57c77358396f19dfc7f749708b66ff68f1bf737d051b5d7675d
    source_path: plugins/architecture.md
    workflow: 15
---

# Internal Plugin

<Info>
  Ini adalah **referensi arsitektur mendalam**. Untuk panduan praktis, lihat:
  - [Instal dan gunakan plugin](/id/tools/plugin) — panduan pengguna
  - [Memulai](/id/plugins/building-plugins) — tutorial plugin pertama
  - [Plugin Channel](/id/plugins/sdk-channel-plugins) — bangun saluran pesan
  - [Plugin Provider](/id/plugins/sdk-provider-plugins) — bangun provider model
  - [Ikhtisar SDK](/id/plugins/sdk-overview) — peta impor dan API pendaftaran
</Info>

Halaman ini membahas arsitektur internal sistem plugin OpenClaw.

## Model kapabilitas publik

Kapabilitas adalah model **plugin native** publik di dalam OpenClaw. Setiap
plugin OpenClaw native mendaftar ke satu atau lebih jenis kapabilitas:

| Kapabilitas           | Metode pendaftaran                             | Contoh plugin                       |
| --------------------- | ---------------------------------------------- | ----------------------------------- |
| Inferensi teks        | `api.registerProvider(...)`                    | `openai`, `anthropic`               |
| Backend inferensi CLI | `api.registerCliBackend(...)`                  | `openai`, `anthropic`               |
| Ucapan                | `api.registerSpeechProvider(...)`              | `elevenlabs`, `microsoft`           |
| Transkripsi realtime  | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                          |
| Suara realtime        | `api.registerRealtimeVoiceProvider(...)`       | `openai`                            |
| Pemahaman media       | `api.registerMediaUnderstandingProvider(...)`  | `openai`, `google`                  |
| Pembuatan gambar      | `api.registerImageGenerationProvider(...)`     | `openai`, `google`, `fal`, `minimax` |
| Pembuatan musik       | `api.registerMusicGenerationProvider(...)`     | `google`, `minimax`                 |
| Pembuatan video       | `api.registerVideoGenerationProvider(...)`     | `qwen`                              |
| Pengambilan web       | `api.registerWebFetchProvider(...)`            | `firecrawl`                         |
| Pencarian web         | `api.registerWebSearchProvider(...)`           | `google`                            |
| Channel / pesan       | `api.registerChannel(...)`                     | `msteams`, `matrix`                 |

Plugin yang mendaftarkan nol kapabilitas tetapi menyediakan hook, tools, atau
layanan adalah plugin **legacy hook-only**. Pola itu masih didukung sepenuhnya.

### Sikap kompatibilitas eksternal

Model kapabilitas sudah mendarat di core dan digunakan oleh plugin
bundled/native saat ini, tetapi kompatibilitas plugin eksternal masih
memerlukan standar yang lebih ketat daripada "sudah diekspor, jadi dibekukan."

Panduan saat ini:

- **plugin eksternal yang sudah ada:** pertahankan integrasi berbasis hook tetap berfungsi; perlakukan
  ini sebagai baseline kompatibilitas
- **plugin bundled/native baru:** utamakan pendaftaran kapabilitas yang eksplisit daripada
  reach-in khusus vendor atau desain hook-only baru
- **plugin eksternal yang mengadopsi pendaftaran kapabilitas:** diperbolehkan, tetapi perlakukan
  surface helper khusus kapabilitas sebagai sesuatu yang masih berkembang kecuali dokumentasi secara eksplisit menandai kontraknya sebagai stabil

Aturan praktis:

- API pendaftaran kapabilitas adalah arah yang dituju
- hook legacy tetap menjadi jalur paling aman tanpa kerusakan untuk plugin eksternal selama
  masa transisi
- subpath helper yang diekspor tidak semuanya setara; utamakan kontrak sempit yang terdokumentasi,
  bukan ekspor helper yang kebetulan ada

### Bentuk plugin

OpenClaw mengklasifikasikan setiap plugin yang dimuat ke dalam sebuah bentuk berdasarkan perilaku
pendaftarannya yang sebenarnya (bukan hanya metadata statis):

- **plain-capability** -- mendaftarkan tepat satu jenis kapabilitas (misalnya
  plugin provider-only seperti `mistral`)
- **hybrid-capability** -- mendaftarkan beberapa jenis kapabilitas (misalnya
  `openai` memiliki inferensi teks, ucapan, pemahaman media, dan
  pembuatan gambar)
- **hook-only** -- hanya mendaftarkan hook (typed atau custom), tanpa kapabilitas,
  tools, perintah, atau layanan
- **non-capability** -- mendaftarkan tools, perintah, layanan, atau route tetapi tidak
  memiliki kapabilitas

Gunakan `openclaw plugins inspect <id>` untuk melihat bentuk plugin dan rincian
kapabilitasnya. Lihat [Referensi CLI](/cli/plugins#inspect) untuk detail.

### Hook legacy

Hook `before_agent_start` tetap didukung sebagai jalur kompatibilitas untuk
plugin hook-only. Plugin legacy di dunia nyata masih bergantung padanya.

Arah ke depan:

- pertahankan agar tetap berfungsi
- dokumentasikan sebagai legacy
- utamakan `before_model_resolve` untuk pekerjaan override model/provider
- utamakan `before_prompt_build` untuk pekerjaan mutasi prompt
- hapus hanya setelah penggunaan nyata menurun dan cakupan fixture membuktikan keamanan migrasi

### Sinyal kompatibilitas

Saat Anda menjalankan `openclaw doctor` atau `openclaw plugins inspect <id>`, Anda mungkin melihat
salah satu label berikut:

| Sinyal                     | Makna                                                       |
| -------------------------- | ----------------------------------------------------------- |
| **config valid**           | Config terurai dengan baik dan plugin berhasil di-resolve   |
| **compatibility advisory** | Plugin menggunakan pola lama yang masih didukung (mis. `hook-only`) |
| **legacy warning**         | Plugin menggunakan `before_agent_start`, yang sudah deprecated |
| **hard error**             | Config tidak valid atau plugin gagal dimuat                 |

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
3. **Pemuatan runtime**
   Plugin OpenClaw native dimuat di dalam proses melalui jiti dan mendaftarkan
   kapabilitas ke registry pusat. Bundle yang kompatibel dinormalisasi menjadi
   record registry tanpa mengimpor kode runtime.
4. **Konsumsi surface**
   Bagian lain OpenClaw membaca registry untuk menampilkan tools, channels, setup provider,
   hooks, route HTTP, perintah CLI, dan layanan.

Untuk CLI plugin secara khusus, discovery perintah root dibagi dalam dua fase:

- metadata waktu parse berasal dari `registerCli(..., { descriptors: [...] })`
- modul CLI plugin yang sebenarnya dapat tetap lazy dan mendaftar pada pemanggilan pertama

Hal itu menjaga kode CLI milik plugin tetap berada di dalam plugin sambil tetap memungkinkan OpenClaw
mencadangkan nama perintah root sebelum parsing.

Batas desain yang penting:

- discovery + validasi config harus bekerja dari **metadata manifest/schema**
  tanpa mengeksekusi kode plugin
- perilaku runtime native berasal dari jalur `register(api)` modul plugin

Pemisahan itu memungkinkan OpenClaw memvalidasi config, menjelaskan plugin yang hilang/dinonaktifkan, dan
membangun petunjuk UI/schema sebelum runtime penuh aktif.

### Plugin channel dan tool pesan bersama

Plugin channel tidak perlu mendaftarkan tool kirim/edit/reaksi terpisah untuk
aksi chat normal. OpenClaw mempertahankan satu tool `message` bersama di core, dan
plugin channel memiliki discovery dan eksekusi khusus channel di baliknya.

Batas saat ini adalah:

- core memiliki host tool `message` bersama, wiring prompt, pembukuan sesi/thread,
  dan dispatch eksekusi
- plugin channel memiliki discovery aksi terlingkup, discovery kapabilitas, dan setiap
  fragmen schema khusus channel
- plugin channel memiliki tata bahasa percakapan sesi khusus provider, seperti
  bagaimana id percakapan mengodekan id thread atau mewarisi dari percakapan induk
- plugin channel mengeksekusi aksi akhir melalui adapter aksinya

Untuk plugin channel, surface SDK-nya adalah
`ChannelMessageActionAdapter.describeMessageTool(...)`. Panggilan discovery terpadu
itu memungkinkan sebuah plugin mengembalikan aksi yang terlihat, kapabilitas, dan kontribusi
schema-nya secara bersamaan agar bagian-bagian itu tidak saling menyimpang.

Core meneruskan scope runtime ke langkah discovery tersebut. Field penting meliputi:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` inbound tepercaya

Hal itu penting untuk plugin yang sensitif terhadap konteks. Sebuah channel dapat menyembunyikan atau menampilkan
aksi pesan berdasarkan akun aktif, room/thread/pesan saat ini, atau
identitas peminta tepercaya tanpa melakukan hardcode cabang khusus channel di
tool `message` milik core.

Inilah sebabnya perubahan routing embedded-runner masih merupakan pekerjaan plugin: runner bertanggung jawab
untuk meneruskan identitas chat/sesi saat ini ke batas discovery plugin sehingga
tool `message` bersama menampilkan surface milik channel yang tepat untuk giliran saat ini.

Untuk helper eksekusi milik channel, plugin bundled harus menyimpan runtime eksekusi
di dalam modul extension milik mereka sendiri. Core tidak lagi memiliki runtime aksi-pesan
Discord, Slack, Telegram, atau WhatsApp di bawah `src/agents/tools`.
Kami tidak menerbitkan subpath `plugin-sdk/*-action-runtime` terpisah, dan plugin
bundled harus mengimpor kode runtime lokal mereka sendiri langsung dari
modul milik extension mereka.

Batas yang sama berlaku pada seam SDK bernama provider secara umum: core tidak
boleh mengimpor convenience barrel khusus channel untuk extension Slack, Discord, Signal,
WhatsApp, atau yang serupa. Jika core membutuhkan suatu perilaku, konsumsi
barrel `api.ts` / `runtime-api.ts` milik plugin bundled itu sendiri atau promosikan kebutuhan tersebut
menjadi kapabilitas generik yang sempit di SDK bersama.

Khusus untuk poll, ada dua jalur eksekusi:

- `outbound.sendPoll` adalah baseline bersama untuk channel yang cocok dengan model
  poll umum
- `actions.handleAction("poll")` adalah jalur yang diutamakan untuk semantik poll khusus channel
  atau parameter poll tambahan

Core sekarang menunda parsing poll bersama sampai setelah dispatch poll plugin menolak
aksi tersebut, sehingga penangan poll milik plugin dapat menerima field poll khusus channel
tanpa diblokir lebih dulu oleh parser poll generik.

Lihat [Pipeline pemuatan](#load-pipeline) untuk urutan startup lengkap.

## Model kepemilikan kapabilitas

OpenClaw memperlakukan plugin native sebagai batas kepemilikan untuk sebuah **perusahaan** atau sebuah
**fitur**, bukan sebagai kumpulan integrasi yang tidak saling terkait.

Artinya:

- plugin perusahaan biasanya harus memiliki seluruh
  surface OpenClaw yang berhadapan dengan perusahaan tersebut
- plugin fitur biasanya harus memiliki seluruh surface fitur yang diperkenalkannya
- channel harus mengonsumsi kapabilitas core bersama alih-alih mengimplementasikan ulang
  perilaku provider secara ad hoc

Contoh:

- plugin bundled `openai` memiliki perilaku model-provider OpenAI dan perilaku OpenAI
  untuk ucapan + realtime-voice + pemahaman media + pembuatan gambar
- plugin bundled `elevenlabs` memiliki perilaku ucapan ElevenLabs
- plugin bundled `microsoft` memiliki perilaku ucapan Microsoft
- plugin bundled `google` memiliki perilaku model-provider Google serta Google
  untuk pemahaman media + pembuatan gambar + pencarian web
- plugin bundled `firecrawl` memiliki perilaku pengambilan web Firecrawl
- plugin bundled `minimax`, `mistral`, `moonshot`, dan `zai` memiliki
  backend pemahaman media mereka
- plugin `qwen` bundled memiliki perilaku text-provider Qwen serta
  pemahaman media dan pembuatan video
- plugin `voice-call` adalah plugin fitur: plugin ini memiliki transport panggilan, tools,
  CLI, route, dan bridging media-stream Twilio, tetapi mengonsumsi kapabilitas bersama untuk ucapan
  serta transkripsi realtime dan suara realtime alih-alih mengimpor plugin vendor secara langsung

Keadaan akhir yang dituju adalah:

- OpenAI berada dalam satu plugin meskipun mencakup model teks, ucapan, gambar, dan
  video di masa depan
- vendor lain dapat melakukan hal yang sama untuk area surface miliknya sendiri
- channel tidak peduli plugin vendor mana yang memiliki provider; mereka mengonsumsi
  kontrak kapabilitas bersama yang diekspos oleh core

Inilah pembedaan utamanya:

- **plugin** = batas kepemilikan
- **capability** = kontrak core yang dapat diimplementasikan atau dikonsumsi oleh beberapa plugin

Jadi, jika OpenClaw menambahkan domain baru seperti video, pertanyaan pertama
bukanlah "provider mana yang harus melakukan hardcode penanganan video?" Pertanyaan
pertama adalah "apa kontrak kapabilitas video di core?"
Setelah kontrak itu ada, plugin vendor
dapat mendaftar ke kontrak tersebut dan plugin channel/fitur dapat mengonsumsinya.

Jika kapabilitas itu belum ada, langkah yang biasanya tepat adalah:

1. definisikan kapabilitas yang belum ada di core
2. ekspos melalui API/runtime plugin dengan cara yang typed
3. hubungkan channel/fitur ke kapabilitas tersebut
4. biarkan plugin vendor mendaftarkan implementasi

Ini menjaga kepemilikan tetap eksplisit sambil menghindari perilaku core yang bergantung pada
satu vendor atau jalur kode satu kali yang khusus plugin.

### Pelapisan kapabilitas

Gunakan model mental ini saat memutuskan di mana kode seharusnya berada:

- **lapisan kapabilitas core**: orkestrasi bersama, kebijakan, fallback, aturan merge
  config, semantik delivery, dan kontrak typed
- **lapisan plugin vendor**: API khusus vendor, auth, katalog model, sintesis ucapan,
  pembuatan gambar, backend video di masa depan, endpoint penggunaan
- **lapisan plugin channel/fitur**: integrasi Slack/Discord/voice-call/dll.
  yang mengonsumsi kapabilitas core dan menampilkannya pada suatu surface

Sebagai contoh, TTS mengikuti bentuk ini:

- core memiliki kebijakan TTS saat balasan, urutan fallback, preferensi, dan delivery channel
- `openai`, `elevenlabs`, dan `microsoft` memiliki implementasi sintesis
- `voice-call` mengonsumsi helper runtime TTS teleponi

Pola yang sama sebaiknya diprioritaskan untuk kapabilitas di masa depan.

### Contoh plugin perusahaan multi-kapabilitas

Sebuah plugin perusahaan seharusnya terasa kohesif dari luar. Jika OpenClaw memiliki kontrak bersama
untuk model, ucapan, transkripsi realtime, suara realtime, pemahaman media,
pembuatan gambar, pembuatan video, pengambilan web, dan pencarian web,
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

Yang penting bukan nama helper yang persis sama. Bentuknya yang penting:

- satu plugin memiliki surface vendor
- core tetap memiliki kontrak kapabilitas
- plugin channel dan fitur mengonsumsi helper `api.runtime.*`, bukan kode vendor
- contract test dapat memastikan bahwa plugin mendaftarkan kapabilitas yang
  diklaim dimilikinya

### Contoh kapabilitas: pemahaman video

OpenClaw sudah memperlakukan pemahaman gambar/audio/video sebagai satu
kapabilitas bersama. Model kepemilikan yang sama berlaku di sana:

1. core mendefinisikan kontrak media-understanding
2. plugin vendor mendaftarkan `describeImage`, `transcribeAudio`, dan
   `describeVideo` sesuai kebutuhan
3. plugin channel dan fitur mengonsumsi perilaku core bersama alih-alih
   menghubungkan langsung ke kode vendor

Hal itu menghindari asumsi video milik satu provider tertanam di core. Plugin memiliki
surface vendor; core memiliki kontrak kapabilitas dan perilaku fallback.

Pembuatan video sudah menggunakan urutan yang sama: core memiliki kontrak
kapabilitas dan helper runtime yang typed, dan plugin vendor mendaftarkan
implementasi `api.registerVideoGenerationProvider(...)` ke kontrak tersebut.

Butuh checklist peluncuran yang konkret? Lihat
[Cookbook Capability](/id/plugins/architecture).

## Kontrak dan enforcement

Surface API plugin sengaja dibuat typed dan dipusatkan di
`OpenClawPluginApi`. Kontrak itu mendefinisikan titik pendaftaran yang didukung dan
helper runtime yang dapat diandalkan oleh suatu plugin.

Mengapa ini penting:

- penulis plugin mendapatkan satu standar internal yang stabil
- core dapat menolak kepemilikan ganda seperti dua plugin yang mendaftarkan id
  provider yang sama
- startup dapat menampilkan diagnostik yang dapat ditindaklanjuti untuk pendaftaran yang tidak valid
- contract test dapat menegakkan kepemilikan plugin bundled dan mencegah drift senyap

Ada dua lapisan enforcement:

1. **enforcement pendaftaran runtime**
   Registry plugin memvalidasi pendaftaran saat plugin dimuat. Contoh:
   id provider duplikat, id provider ucapan duplikat, dan pendaftaran yang tidak valid
   menghasilkan diagnostik plugin alih-alih perilaku tak terdefinisi.
2. **contract test**
   Plugin bundled ditangkap di registry kontrak selama test berjalan sehingga
   OpenClaw dapat memastikan kepemilikan secara eksplisit. Saat ini hal ini digunakan untuk model
   provider, provider ucapan, provider pencarian web, dan kepemilikan pendaftaran bundled.

Efek praktisnya adalah OpenClaw mengetahui, sejak awal, plugin mana yang memiliki surface mana.
Hal itu memungkinkan core dan channel tersusun dengan mulus karena kepemilikan
dideklarasikan, typed, dan dapat diuji, bukan implisit.

### Apa yang seharusnya ada dalam sebuah kontrak

Kontrak plugin yang baik adalah:

- typed
- kecil
- spesifik terhadap kapabilitas
- dimiliki oleh core
- dapat digunakan ulang oleh banyak plugin
- dapat dikonsumsi oleh channel/fitur tanpa pengetahuan vendor

Kontrak plugin yang buruk adalah:

- kebijakan khusus vendor yang tersembunyi di core
- escape hatch plugin satu kali yang melewati registry
- kode channel yang langsung menjangkau implementasi vendor
- objek runtime ad hoc yang bukan bagian dari `OpenClawPluginApi` atau
  `api.runtime`

Jika ragu, naikkan tingkat abstraksinya: definisikan kapabilitas terlebih dahulu, lalu
biarkan plugin terhubung ke dalamnya.

## Model eksekusi

Plugin OpenClaw native berjalan **di dalam proses** dengan Gateway. Plugin ini tidak
di-sandbox. Plugin native yang dimuat memiliki batas kepercayaan tingkat proses yang sama dengan
kode core.

Implikasinya:

- plugin native dapat mendaftarkan tools, network handler, hook, dan layanan
- bug pada plugin native dapat membuat gateway crash atau tidak stabil
- plugin native yang berbahaya setara dengan eksekusi kode arbitrer di dalam
  proses OpenClaw

Bundle yang kompatibel lebih aman secara default karena OpenClaw saat ini memperlakukannya
sebagai paket metadata/konten. Pada rilis saat ini, itu terutama berarti
skills yang dibundel.

Gunakan allowlist dan path install/load yang eksplisit untuk plugin yang tidak dibundel. Perlakukan
plugin workspace sebagai kode saat pengembangan, bukan default produksi.

Untuk nama package workspace yang dibundel, pertahankan id plugin sebagai dasar di
nama npm: `@openclaw/<id>` secara default, atau suffix typed yang disetujui seperti
`-provider`, `-plugin`, `-speech`, `-sandbox`, atau `-media-understanding` ketika
package secara sengaja mengekspos peran plugin yang lebih sempit.

Catatan kepercayaan penting:

- `plugins.allow` mempercayai **id plugin**, bukan provenance sumber.
- Plugin workspace dengan id yang sama seperti plugin bundled sengaja menimpa
  salinan bundled saat plugin workspace itu diaktifkan/masuk allowlist.
- Ini normal dan berguna untuk pengembangan lokal, patch testing, dan hotfix.

## Batas ekspor

OpenClaw mengekspor kapabilitas, bukan convenience implementasi.

Pertahankan pendaftaran kapabilitas tetap publik. Pangkas ekspor helper non-kontrak:

- subpath helper khusus plugin bundled
- subpath plumbing runtime yang tidak dimaksudkan sebagai API publik
- helper convenience khusus vendor
- helper setup/onboarding yang merupakan detail implementasi

Beberapa subpath helper plugin bundled masih tetap ada di peta ekspor SDK yang dihasilkan
demi kompatibilitas dan pemeliharaan plugin bundled. Contoh saat ini termasuk
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, dan beberapa seam `plugin-sdk/matrix*`. Perlakukan itu
sebagai ekspor detail implementasi yang dicadangkan, bukan sebagai pola SDK yang direkomendasikan untuk
plugin pihak ketiga baru.

## Pipeline pemuatan

Saat startup, OpenClaw kira-kira melakukan ini:

1. menemukan root plugin kandidat
2. membaca manifest native atau bundle yang kompatibel serta metadata package
3. menolak kandidat yang tidak aman
4. menormalkan config plugin (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. memutuskan enablement untuk setiap kandidat
6. memuat modul native yang diaktifkan melalui jiti
7. memanggil hook native `register(api)` (atau `activate(api)` — alias legacy) dan mengumpulkan pendaftaran ke dalam registry plugin
8. mengekspos registry ke surface perintah/runtime

<Note>
`activate` adalah alias legacy untuk `register` — loader me-resolve mana pun yang ada (`def.register ?? def.activate`) dan memanggilnya pada titik yang sama. Semua plugin bundled menggunakan `register`; utamakan `register` untuk plugin baru.
</Note>

Gerbang keamanan terjadi **sebelum** eksekusi runtime. Kandidat diblokir
ketika entry keluar dari root plugin, path dapat ditulis oleh semua orang, atau kepemilikan path
terlihat mencurigakan untuk plugin yang tidak dibundel.

### Perilaku manifest-first

Manifest adalah sumber kebenaran control-plane. OpenClaw menggunakannya untuk:

- mengidentifikasi plugin
- menemukan channel/skills/schema config yang dideklarasikan atau kapabilitas bundle
- memvalidasi `plugins.entries.<id>.config`
- menambah label/placeholder Control UI
- menampilkan metadata install/katalog
- mempertahankan deskriptor aktivasi dan setup yang murah tanpa memuat runtime plugin

Untuk plugin native, modul runtime adalah bagian data-plane. Modul ini mendaftarkan
perilaku aktual seperti hook, tools, perintah, atau flow provider.

Blok `activation` dan `setup` manifest yang opsional tetap berada di control plane.
Keduanya adalah deskriptor hanya-metadata untuk perencanaan aktivasi dan discovery setup;
mereka tidak menggantikan pendaftaran runtime, `register(...)`, atau `setupEntry`.
Konsumen aktivasi live pertama sekarang menggunakan petunjuk perintah, channel, dan provider di manifest
untuk mempersempit pemuatan plugin sebelum materialisasi registry yang lebih luas:

- pemuatan CLI dipersempit ke plugin yang memiliki primary command yang diminta
- resolusi setup/plugin channel dipersempit ke plugin yang memiliki id
  channel yang diminta
- resolusi setup/runtime provider eksplisit dipersempit ke plugin yang memiliki
  id provider yang diminta

Discovery setup sekarang mengutamakan id milik descriptor seperti `setup.providers` dan
`setup.cliBackends` untuk mempersempit kandidat plugin sebelum kembali ke
`setup-api` bagi plugin yang masih membutuhkan hook runtime saat setup. Jika lebih dari
satu plugin yang ditemukan mengklaim id provider setup atau backend CLI yang sama setelah dinormalisasi,
lookup setup menolak pemilik yang ambigu tersebut alih-alih bergantung pada urutan discovery.

### Apa yang di-cache oleh loader

OpenClaw menyimpan cache pendek di dalam proses untuk:

- hasil discovery
- data registry manifest
- registry plugin yang dimuat

Cache ini mengurangi startup yang meledak-ledak dan overhead perintah berulang. Cache ini aman
untuk dipikirkan sebagai cache performa berumur pendek, bukan persistensi.

Catatan performa:

- Atur `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` atau
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` untuk menonaktifkan cache ini.
- Sesuaikan jendela cache dengan `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` dan
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Model registry

Plugin yang dimuat tidak langsung memodifikasi global core acak. Mereka mendaftar ke
registry plugin pusat.

Registry melacak:

- record plugin (identitas, sumber, origin, status, diagnostik)
- tools
- hook legacy dan hook typed
- channels
- providers
- handler RPC Gateway
- route HTTP
- registrar CLI
- layanan latar belakang
- perintah milik plugin

Fitur core kemudian membaca dari registry itu alih-alih berbicara langsung dengan
modul plugin. Ini menjaga pemuatan tetap satu arah:

- modul plugin -> pendaftaran ke registry
- runtime core -> konsumsi registry

Pemisahan itu penting untuk maintainability. Artinya sebagian besar surface core hanya
memerlukan satu titik integrasi: "baca registry", bukan "buat special-case untuk setiap modul plugin".

## Callback pengikatan percakapan

Plugin yang mengikat percakapan dapat bereaksi saat suatu persetujuan diselesaikan.

Gunakan `api.onConversationBindingResolved(...)` untuk menerima callback setelah permintaan bind
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
- `binding`: binding yang telah di-resolve untuk permintaan yang disetujui
- `request`: ringkasan permintaan asli, petunjuk detach, id pengirim, dan
  metadata percakapan

Callback ini hanya untuk notifikasi. Callback ini tidak mengubah siapa yang diizinkan untuk mengikat suatu
percakapan, dan dijalankan setelah penanganan persetujuan core selesai.

## Hook runtime provider

Plugin provider kini memiliki dua lapisan:

- metadata manifest: `providerAuthEnvVars` untuk lookup auth provider berbasis env yang murah
  sebelum runtime dimuat, `providerAuthAliases` untuk varian provider yang berbagi
  auth, `channelEnvVars` untuk lookup env/setup channel yang murah sebelum runtime
  dimuat, serta `providerAuthChoices` untuk label onboarding/auth-choice yang murah dan
  metadata flag CLI sebelum runtime dimuat
- hook saat config: `catalog` / `discovery` legacy serta `applyConfigDefaults`
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

OpenClaw tetap memiliki agent loop generik, failover, penanganan transkrip, dan
kebijakan tool. Hook-hook ini adalah surface extension untuk perilaku khusus provider tanpa
memerlukan transport inferensi kustom sepenuhnya.

Gunakan manifest `providerAuthEnvVars` ketika provider memiliki kredensial berbasis env
yang perlu terlihat oleh jalur auth/status/model-picker generik tanpa memuat runtime plugin.
Gunakan manifest `providerAuthAliases` ketika satu id provider harus menggunakan ulang
env vars, profil auth, auth berbasis config, dan pilihan onboarding API key milik id provider lain.
Gunakan manifest `providerAuthChoices` ketika surface CLI onboarding/auth-choice
perlu mengetahui id pilihan provider, label grup, dan wiring auth satu-flag sederhana
tanpa memuat runtime provider. Pertahankan `envVars` runtime provider untuk petunjuk yang berhadapan dengan operator
seperti label onboarding atau variabel setup OAuth client-id/client-secret.

Gunakan manifest `channelEnvVars` ketika sebuah channel memiliki auth atau setup berbasis env
yang perlu terlihat oleh fallback shell-env generik, pemeriksaan config/status, atau prompt setup
tanpa memuat runtime channel.

### Urutan hook dan penggunaan

Untuk plugin model/provider, OpenClaw memanggil hook dalam urutan kasar seperti ini.
Kolom "Kapan digunakan" adalah panduan keputusan cepat.

| #   | Hook                              | Apa fungsinya                                                                                                  | Kapan digunakan                                                                                                                             |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Mempublikasikan config provider ke `models.providers` selama pembuatan `models.json`                           | Provider memiliki katalog atau default base URL                                                                                             |
| 2   | `applyConfigDefaults`             | Menerapkan default config global milik provider selama materialisasi config                                    | Default bergantung pada mode auth, env, atau semantik keluarga model provider                                                               |
| --  | _(lookup model bawaan)_           | OpenClaw mencoba jalur registry/katalog normal terlebih dahulu                                                 | _(bukan hook plugin)_                                                                                                                       |
| 3   | `normalizeModelId`                | Menormalkan alias model-id legacy atau pratinjau sebelum lookup                                                | Provider memiliki pembersihan alias sebelum resolusi model kanonis                                                                          |
| 4   | `normalizeTransport`              | Menormalkan provider-family `api` / `baseUrl` sebelum perakitan model generik                                 | Provider memiliki pembersihan transport untuk id provider kustom dalam keluarga transport yang sama                                         |
| 5   | `normalizeConfig`                 | Menormalkan `models.providers.<id>` sebelum resolusi runtime/provider                                          | Provider memerlukan pembersihan config yang sebaiknya berada bersama plugin; helper keluarga Google yang dibundel juga menjadi backstop untuk entri config Google yang didukung |
| 6   | `applyNativeStreamingUsageCompat` | Menerapkan penulisan ulang kompatibilitas native streaming-usage pada provider config                          | Provider memerlukan perbaikan metadata native streaming usage berbasis endpoint                                                             |
| 7   | `resolveConfigApiKey`             | Me-resolve auth env-marker untuk provider config sebelum pemuatan auth runtime                                 | Provider memiliki resolusi API key env-marker milik provider; `amazon-bedrock` juga memiliki resolver env-marker AWS bawaan di sini       |
| 8   | `resolveSyntheticAuth`            | Menampilkan auth lokal/self-hosted atau berbasis config tanpa mempersistenkan plaintext                        | Provider dapat beroperasi dengan penanda kredensial sintetik/lokal                                                                          |
| 9   | `resolveExternalAuthProfiles`     | Menumpangkan profil auth eksternal milik provider; default `persistence` adalah `runtime-only` untuk kredensial milik CLI/app | Provider menggunakan ulang kredensial auth eksternal tanpa mempersistenkan refresh token yang disalin                                     |
| 10  | `shouldDeferSyntheticProfileAuth` | Menurunkan prioritas placeholder profil sintetik yang tersimpan di bawah auth berbasis env/config             | Provider menyimpan profil placeholder sintetik yang tidak boleh menang dalam prioritas                                                      |
| 11  | `resolveDynamicModel`             | Fallback sinkron untuk model id milik provider yang belum ada di registry lokal                                | Provider menerima model id upstream arbitrer                                                                                                |
| 12  | `prepareDynamicModel`             | Warm-up asinkron, lalu `resolveDynamicModel` dijalankan lagi                                                   | Provider memerlukan metadata jaringan sebelum me-resolve id yang tidak dikenal                                                              |
| 13  | `normalizeResolvedModel`          | Penulisan ulang akhir sebelum embedded runner menggunakan model yang telah di-resolve                          | Provider memerlukan penulisan ulang transport tetapi tetap menggunakan transport core                                                       |
| 14  | `contributeResolvedModelCompat`   | Menyumbangkan flag compat untuk model vendor di balik transport kompatibel lain                                | Provider mengenali modelnya sendiri pada transport proxy tanpa mengambil alih provider                                                      |
| 15  | `capabilities`                    | Metadata transkrip/tooling milik provider yang digunakan oleh logika core bersama                              | Provider memerlukan kekhasan transkrip/keluarga provider                                                                                    |
| 16  | `normalizeToolSchemas`            | Menormalkan schema tool sebelum embedded runner melihatnya                                                     | Provider memerlukan pembersihan schema keluarga transport                                                                                   |
| 17  | `inspectToolSchemas`              | Menampilkan diagnostik schema milik provider setelah normalisasi                                               | Provider menginginkan peringatan keyword tanpa mengajarkan aturan khusus provider ke core                                                  |
| 18  | `resolveReasoningOutputMode`      | Memilih kontrak output reasoning native vs bertag                                                              | Provider memerlukan output reasoning/final bertag alih-alih field native                                                                   |
| 19  | `prepareExtraParams`              | Normalisasi parameter permintaan sebelum wrapper opsi stream generik                                           | Provider memerlukan parameter permintaan default atau pembersihan parameter per provider                                                    |
| 20  | `createStreamFn`                  | Sepenuhnya mengganti jalur stream normal dengan transport kustom                                               | Provider memerlukan protokol wire kustom, bukan sekadar wrapper                                                                            |
| 21  | `wrapStreamFn`                    | Wrapper stream setelah wrapper generik diterapkan                                                              | Provider memerlukan wrapper kompatibilitas header/body/model permintaan tanpa transport kustom                                              |
| 22  | `resolveTransportTurnState`       | Melampirkan header atau metadata transport per-giliran native                                                  | Provider ingin transport generik mengirim identitas giliran native milik provider                                                           |
| 23  | `resolveWebSocketSessionPolicy`   | Melampirkan header WebSocket native atau kebijakan cooldown sesi                                               | Provider ingin transport WS generik menyetel header sesi atau kebijakan fallback                                                           |
| 24  | `formatApiKey`                    | Formatter auth-profile: profil yang tersimpan menjadi string `apiKey` runtime                                  | Provider menyimpan metadata auth tambahan dan memerlukan bentuk token runtime kustom                                                        |
| 25  | `refreshOAuth`                    | Override refresh OAuth untuk endpoint refresh kustom atau kebijakan kegagalan refresh                          | Provider tidak cocok dengan refresher `pi-ai` bersama                                                                                       |
| 26  | `buildAuthDoctorHint`             | Petunjuk perbaikan yang ditambahkan saat refresh OAuth gagal                                                   | Provider memerlukan panduan perbaikan auth milik provider setelah kegagalan refresh                                                        |
| 27  | `matchesContextOverflowError`     | Matcher overflow jendela konteks milik provider                                                                | Provider memiliki error overflow mentah yang tidak terdeteksi oleh heuristik generik                                                       |
| 28  | `classifyFailoverReason`          | Klasifikasi alasan failover milik provider                                                                     | Provider dapat memetakan error API/transport mentah ke rate-limit/overload/dll.                                                            |
| 29  | `isCacheTtlEligible`              | Kebijakan prompt-cache untuk provider proxy/backhaul                                                           | Provider memerlukan gating cache TTL khusus proxy                                                                                           |
| 30  | `buildMissingAuthMessage`         | Pengganti untuk pesan pemulihan missing-auth generik                                                           | Provider memerlukan petunjuk pemulihan missing-auth khusus provider                                                                         |
| 31  | `suppressBuiltInModel`            | Penyembunyian model upstream yang basi plus petunjuk error opsional yang berhadapan dengan pengguna           | Provider perlu menyembunyikan baris upstream yang basi atau menggantinya dengan petunjuk vendor                                             |
| 32  | `augmentModelCatalog`             | Baris katalog sintetik/final yang ditambahkan setelah discovery                                                | Provider memerlukan baris kompatibilitas ke depan sintetik di `models list` dan picker                                                     |
| 33  | `isBinaryThinking`                | Toggle reasoning hidup/mati untuk provider binary-thinking                                                     | Provider hanya mengekspos binary thinking hidup/mati                                                                                        |
| 34  | `supportsXHighThinking`           | Dukungan reasoning `xhigh` untuk model tertentu                                                                | Provider menginginkan `xhigh` hanya pada subset model tertentu                                                                              |
| 35  | `resolveDefaultThinkingLevel`     | Level `/think` default untuk keluarga model tertentu                                                            | Provider memiliki kebijakan `/think` default untuk keluarga model                                                                           |
| 36  | `isModernModelRef`                | Matcher model modern untuk filter live profile dan pemilihan smoke                                             | Provider memiliki pencocokan model pilihan untuk live/smoke                                                                                 |
| 37  | `prepareRuntimeAuth`              | Menukar kredensial yang dikonfigurasi menjadi token/key runtime yang sebenarnya tepat sebelum inferensi        | Provider memerlukan pertukaran token atau kredensial permintaan berumur pendek                                                              |
| 38  | `resolveUsageAuth`                | Me-resolve kredensial penggunaan/penagihan untuk `/usage` dan surface status terkait                           | Provider memerlukan parsing token penggunaan/kuota kustom atau kredensial penggunaan yang berbeda                                          |
| 39  | `fetchUsageSnapshot`              | Mengambil dan menormalkan snapshot penggunaan/kuota khusus provider setelah auth di-resolve                    | Provider memerlukan endpoint penggunaan atau parser payload khusus provider                                                                 |
| 40  | `createEmbeddingProvider`         | Membangun adapter embedding milik provider untuk memory/pencarian                                              | Perilaku embedding memory seharusnya berada bersama plugin provider                                                                         |
| 41  | `buildReplayPolicy`               | Mengembalikan kebijakan replay yang mengontrol penanganan transkrip untuk provider                             | Provider memerlukan kebijakan transkrip kustom (misalnya, penghapusan blok thinking)                                                       |
| 42  | `sanitizeReplayHistory`           | Menulis ulang riwayat replay setelah pembersihan transkrip generik                                             | Provider memerlukan penulisan ulang replay khusus provider di luar helper compaction bersama                                                |
| 43  | `validateReplayTurns`             | Validasi atau pembentukan ulang giliran replay final sebelum embedded runner                                   | Transport provider memerlukan validasi giliran yang lebih ketat setelah sanitasi generik                                                   |
| 44  | `onModelSelected`                 | Menjalankan efek samping pasca-pemilihan milik provider                                                        | Provider memerlukan telemetri atau state milik provider saat sebuah model menjadi aktif                                                    |

`normalizeModelId`, `normalizeTransport`, dan `normalizeConfig` pertama-tama memeriksa
plugin provider yang cocok, lalu berlanjut ke plugin provider lain yang mampu memakai hook
sampai salah satunya benar-benar mengubah model id atau transport/config. Hal itu menjaga
shim alias/compat provider tetap berfungsi tanpa mengharuskan pemanggil mengetahui plugin
bundled mana yang memiliki penulisan ulang tersebut. Jika tidak ada hook provider yang menulis ulang
entri config keluarga Google yang didukung, normalizer config Google bundled tetap menerapkan
pembersihan kompatibilitas tersebut.

Jika provider membutuhkan protokol wire yang sepenuhnya kustom atau eksekutor permintaan kustom,
itu adalah kelas extension yang berbeda. Hook-hook ini diperuntukkan bagi perilaku provider
yang masih berjalan pada inference loop normal OpenClaw.

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
  dan `wrapStreamFn` karena plugin ini memiliki kompatibilitas maju Claude 4.6,
  petunjuk keluarga provider, panduan perbaikan auth, integrasi endpoint penggunaan,
  kelayakan prompt-cache, default config yang sadar auth, kebijakan thinking default/adaptif
  Claude, serta pembentukan stream khusus Anthropic untuk
  beta header, `/fast` / `serviceTier`, dan `context1m`.
- Helper stream khusus Claude milik Anthropic untuk sementara tetap berada di
  seam `api.ts` / `contract-api.ts` publik milik plugin bundled itu sendiri. Surface package
  tersebut mengekspor `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`, dan builder wrapper Anthropic
  tingkat lebih rendah alih-alih memperlebar SDK generik di sekitar aturan beta-header
  milik satu provider.
- OpenAI menggunakan `resolveDynamicModel`, `normalizeResolvedModel`, dan
  `capabilities` serta `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking`, dan `isModernModelRef`
  karena plugin ini memiliki kompatibilitas maju GPT-5.4, normalisasi langsung OpenAI
  dari `openai-completions` -> `openai-responses`, petunjuk auth yang sadar Codex,
  penekanan Spark, baris daftar OpenAI sintetik, dan kebijakan thinking /
  live-model GPT-5; keluarga stream `openai-responses-defaults` memiliki
  wrapper OpenAI Responses native bersama untuk attribution header,
  `/fast`/`serviceTier`, text verbosity, pencarian web native Codex,
  pembentukan payload reasoning-compat, dan manajemen konteks Responses.
- OpenRouter menggunakan `catalog` serta `resolveDynamicModel` dan
  `prepareDynamicModel` karena provider ini bersifat pass-through dan dapat mengekspos
  model id baru sebelum katalog statis OpenClaw diperbarui; plugin ini juga menggunakan
  `capabilities`, `wrapStreamFn`, dan `isCacheTtlEligible` untuk menjaga
  header permintaan khusus provider, metadata routing, patch reasoning, dan
  kebijakan prompt-cache tetap di luar core. Kebijakan replay-nya berasal dari
  keluarga `passthrough-gemini`, sedangkan keluarga stream `openrouter-thinking`
  memiliki injeksi reasoning proxy dan skip untuk model yang tidak didukung / `auto`.
- GitHub Copilot menggunakan `catalog`, `auth`, `resolveDynamicModel`, dan
  `capabilities` serta `prepareRuntimeAuth` dan `fetchUsageSnapshot` karena plugin ini
  membutuhkan login perangkat milik provider, perilaku fallback model, kekhasan transkrip
  Claude, pertukaran token GitHub -> token Copilot, dan endpoint penggunaan milik provider.
- OpenAI Codex menggunakan `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth`, dan `augmentModelCatalog` serta
  `prepareExtraParams`, `resolveUsageAuth`, dan `fetchUsageSnapshot` karena plugin ini
  masih berjalan di transport OpenAI core tetapi memiliki normalisasi
  transport/base URL, kebijakan fallback refresh OAuth, pilihan transport default,
  baris katalog Codex sintetik, dan integrasi endpoint penggunaan ChatGPT; plugin ini
  berbagi keluarga stream `openai-responses-defaults` yang sama dengan OpenAI langsung.
- Google AI Studio dan Gemini CLI OAuth menggunakan `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn`, dan `isModernModelRef` karena keluarga replay
  `google-gemini` memiliki fallback kompatibilitas maju Gemini 3.1,
  validasi replay Gemini native, sanitasi replay bootstrap, mode output reasoning
  bertag, dan pencocokan model modern, sedangkan keluarga stream
  `google-thinking` memiliki normalisasi payload thinking Gemini;
  Gemini CLI OAuth juga menggunakan `formatApiKey`, `resolveUsageAuth`, dan
  `fetchUsageSnapshot` untuk formatting token, parsing token, dan wiring endpoint kuota.
- Anthropic Vertex menggunakan `buildReplayPolicy` melalui
  keluarga replay `anthropic-by-model` sehingga pembersihan replay khusus Claude tetap
  terbatas pada id Claude alih-alih setiap transport `anthropic-messages`.
- Amazon Bedrock menggunakan `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason`, dan `resolveDefaultThinkingLevel` karena plugin ini memiliki
  klasifikasi error throttle/not-ready/context-overflow khusus Bedrock
  untuk lalu lintas Anthropic-on-Bedrock; kebijakan replay-nya tetap berbagi
  guard `anthropic-by-model` yang hanya untuk Claude.
- OpenRouter, Kilocode, Opencode, dan Opencode Go menggunakan `buildReplayPolicy`
  melalui keluarga replay `passthrough-gemini` karena mereka mem-proxy model Gemini
  melalui transport yang kompatibel dengan OpenAI dan memerlukan sanitasi
  thought-signature Gemini tanpa validasi replay Gemini native atau
  penulisan ulang bootstrap.
- MiniMax menggunakan `buildReplayPolicy` melalui
  keluarga replay `hybrid-anthropic-openai` karena satu provider memiliki semantik
  Anthropic-message dan OpenAI-compatible sekaligus; plugin ini tetap menjaga penghapusan
  thinking-block khusus Claude di sisi Anthropic sambil meng-override mode output reasoning
  kembali ke native, dan keluarga stream `minimax-fast-mode` memiliki penulisan ulang model
  fast-mode pada jalur stream bersama.
- Moonshot menggunakan `catalog` serta `wrapStreamFn` karena plugin ini masih menggunakan
  transport OpenAI bersama tetapi memerlukan normalisasi payload thinking milik provider; keluarga
  stream `moonshot-thinking` memetakan config plus state `/think` ke payload binary thinking
  native miliknya.
- Kilocode menggunakan `catalog`, `capabilities`, `wrapStreamFn`, dan
  `isCacheTtlEligible` karena plugin ini memerlukan request header milik provider,
  normalisasi payload reasoning, petunjuk transkrip Gemini, dan gating
  cache-TTL Anthropic; keluarga stream `kilocode-thinking` menjaga injeksi thinking Kilo
  pada jalur stream proxy bersama sambil melewati `kilo/auto` dan
  model id proxy lain yang tidak mendukung payload reasoning eksplisit.
- Z.AI menggunakan `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth`, dan `fetchUsageSnapshot` karena plugin ini memiliki fallback GLM-5,
  default `tool_stream`, UX binary thinking, pencocokan model modern, serta
  auth penggunaan dan pengambilan kuota; keluarga stream `tool-stream-default-on` menjaga
  wrapper `tool_stream` default-on tetap berada di luar glue tulisan tangan per-provider.
- xAI menggunakan `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel`, dan `isModernModelRef`
  karena plugin ini memiliki normalisasi transport Responses xAI native, penulisan ulang alias
  fast-mode Grok, default `tool_stream`, pembersihan strict-tool / reasoning-payload,
  penggunaan ulang auth fallback untuk tools milik plugin, resolusi model Grok
  yang kompatibel ke depan, dan patch compat milik provider seperti profil
  tool-schema xAI, keyword schema yang tidak didukung, `web_search` native, dan dekode argumen
  tool-call HTML-entity.
- Mistral, OpenCode Zen, dan OpenCode Go hanya menggunakan `capabilities` untuk menjaga
  kekhasan transkrip/tooling tetap di luar core.
- Provider bundled yang hanya katalog seperti `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway`, dan `volcengine` hanya menggunakan
  `catalog`.
- Qwen menggunakan `catalog` untuk provider teksnya serta pendaftaran
  pemahaman media dan pembuatan video bersama untuk surface multimodal-nya.
- MiniMax dan Xiaomi menggunakan `catalog` serta hook penggunaan karena perilaku `/usage`
  mereka dimiliki plugin meskipun inferensi masih berjalan melalui transport bersama.

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

- `textToSpeech` mengembalikan payload output TTS core normal untuk surface file/voice-note.
- Menggunakan konfigurasi core `messages.tts` dan pemilihan provider.
- Mengembalikan buffer audio PCM + sample rate. Plugin harus melakukan resample/encode untuk provider.
- `listVoices` bersifat opsional per provider. Gunakan untuk voice picker milik vendor atau flow setup.
- Daftar suara dapat menyertakan metadata yang lebih kaya seperti locale, gender, dan tag personality untuk picker yang sadar provider.
- OpenAI dan ElevenLabs saat ini mendukung teleponi. Microsoft tidak.

Plugin juga dapat mendaftarkan provider ucapan melalui `api.registerSpeechProvider(...)`.

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

- Pertahankan kebijakan TTS, fallback, dan delivery balasan di core.
- Gunakan provider ucapan untuk perilaku sintesis milik vendor.
- Input legacy Microsoft `edge` dinormalkan ke id provider `microsoft`.
- Model kepemilikan yang diutamakan berorientasi perusahaan: satu plugin vendor dapat memiliki
  provider teks, ucapan, gambar, dan media masa depan saat OpenClaw menambahkan
  kontrak kapabilitas tersebut.

Untuk pemahaman gambar/audio/video, plugin mendaftarkan satu provider
media-understanding yang typed alih-alih bag key/value generik:

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

- Pertahankan orkestrasi, fallback, config, dan wiring channel di core.
- Pertahankan perilaku vendor di plugin provider.
- Ekspansi aditif harus tetap typed: metode opsional baru, field hasil opsional
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
- Mengembalikan `{ text: undefined }` ketika tidak ada output transkripsi yang dihasilkan (misalnya input dilewati/tidak didukung).
- `api.runtime.stt.transcribeAudioFile(...)` tetap ada sebagai alias kompatibilitas.

Plugin juga dapat meluncurkan eksekusi subagent latar belakang melalui `api.runtime.subagent`:

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

- `provider` dan `model` adalah override per-eksekusi yang opsional, bukan perubahan sesi yang persisten.
- OpenClaw hanya menghormati field override tersebut untuk pemanggil tepercaya.
- Untuk eksekusi fallback milik plugin, operator harus melakukan opt-in dengan `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Gunakan `plugins.entries.<id>.subagent.allowedModels` untuk membatasi plugin tepercaya ke target `provider/model` kanonis tertentu, atau `"*"` untuk mengizinkan target apa pun secara eksplisit.
- Eksekusi subagent plugin yang tidak tepercaya tetap berfungsi, tetapi permintaan override ditolak alih-alih diam-diam fallback.

Untuk pencarian web, plugin dapat mengonsumsi helper runtime bersama alih-alih
menjangkau wiring tool agen:

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

Plugin juga dapat mendaftarkan provider pencarian web melalui
`api.registerWebSearchProvider(...)`.

Catatan:

- Pertahankan pemilihan provider, resolusi kredensial, dan semantik permintaan bersama di core.
- Gunakan provider pencarian web untuk transport pencarian khusus vendor.
- `api.runtime.webSearch.*` adalah surface bersama yang diutamakan untuk plugin fitur/channel yang membutuhkan perilaku pencarian tanpa bergantung pada wrapper tool agen.

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

- `generate(...)`: menghasilkan gambar menggunakan rantai provider pembuatan gambar yang dikonfigurasi.
- `listProviders(...)`: menampilkan daftar provider pembuatan gambar yang tersedia dan kapabilitasnya.

## Route HTTP Gateway

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

Field route:

- `path`: path route di bawah server HTTP Gateway.
- `auth`: wajib. Gunakan `"gateway"` untuk mewajibkan auth Gateway normal, atau `"plugin"` untuk auth/verifikasi webhook yang dikelola plugin.
- `match`: opsional. `"exact"` (default) atau `"prefix"`.
- `replaceExisting`: opsional. Memungkinkan plugin yang sama mengganti pendaftaran route miliknya sendiri yang sudah ada.
- `handler`: kembalikan `true` ketika route menangani permintaan.

Catatan:

- `api.registerHttpHandler(...)` sudah dihapus dan akan menyebabkan error saat pemuatan plugin. Gunakan `api.registerHttpRoute(...)` sebagai gantinya.
- Route plugin harus mendeklarasikan `auth` secara eksplisit.
- Konflik `path + match` yang persis sama ditolak kecuali `replaceExisting: true`, dan satu plugin tidak dapat mengganti route milik plugin lain.
- Route yang saling tumpang tindih dengan level `auth` berbeda ditolak. Pertahankan rantai fallthrough `exact`/`prefix` hanya pada level auth yang sama.
- Route `auth: "plugin"` **tidak** secara otomatis menerima runtime scope operator. Route ini diperuntukkan bagi webhook/verifikasi tanda tangan yang dikelola plugin, bukan panggilan helper Gateway yang memiliki privilese.
- Route `auth: "gateway"` berjalan di dalam runtime scope permintaan Gateway, tetapi scope itu sengaja konservatif:
  - shared-secret bearer auth (`gateway.auth.mode = "token"` / `"password"`) menjaga runtime scope route plugin tetap terkunci pada `operator.write`, meskipun pemanggil mengirim `x-openclaw-scopes`
  - mode HTTP tepercaya yang membawa identitas (misalnya `trusted-proxy` atau `gateway.auth.mode = "none"` pada ingress privat) hanya menghormati `x-openclaw-scopes` ketika header itu memang ada secara eksplisit
  - jika `x-openclaw-scopes` tidak ada pada permintaan route plugin yang membawa identitas tersebut, runtime scope fallback ke `operator.write`
- Aturan praktis: jangan menganggap route plugin dengan auth Gateway sebagai surface admin implisit. Jika route Anda memerlukan perilaku khusus admin, wajibkan mode auth yang membawa identitas dan dokumentasikan kontrak header `x-openclaw-scopes` yang eksplisit.

## Path impor Plugin SDK

Gunakan subpath SDK alih-alih impor monolitik `openclaw/plugin-sdk` saat
menulis plugin:

- `openclaw/plugin-sdk/plugin-entry` untuk primitif pendaftaran plugin.
- `openclaw/plugin-sdk/core` untuk kontrak generik bersama yang berhadapan dengan plugin.
- `openclaw/plugin-sdk/config-schema` untuk ekspor schema Zod root `openclaw.json`
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
  `openclaw/plugin-sdk/webhook-ingress` untuk wiring
  setup/auth/balasan/webhook bersama. `channel-inbound` adalah rumah bersama
  untuk debounce, mention matching,
  helper inbound mention-policy, pemformatan envelope, dan helper konteks envelope inbound.
  `channel-setup` adalah seam setup narrow optional-install.
  `setup-runtime` adalah surface setup yang aman untuk runtime yang digunakan oleh `setupEntry` /
  startup tertunda, termasuk adapter patch setup yang aman untuk impor.
  `setup-adapter-runtime` adalah seam adapter account-setup yang sadar env.
  `setup-tools` adalah seam helper kecil untuk CLI/arsip/dokumentasi (`formatCliCommand`,
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
  `openclaw/plugin-sdk/directory-runtime` untuk helper runtime/config bersama.
  `telegram-command-config` adalah seam publik sempit untuk normalisasi/validasi custom
  command Telegram dan tetap tersedia meskipun surface kontrak Telegram bundled
  untuk sementara tidak tersedia.
  `text-runtime` adalah seam teks/markdown/logging bersama, termasuk
  penghapusan teks yang terlihat oleh asisten, helper render/chunking markdown, helper redaksi,
  helper directive-tag, dan utilitas safe-text.
- Seam channel khusus approval sebaiknya mengutamakan satu kontrak `approvalCapability`
  pada plugin. Core kemudian membaca auth approval, delivery, render,
  native-routing, dan perilaku lazy native-handler melalui satu kapabilitas itu
  alih-alih mencampurkan perilaku approval ke field plugin yang tidak terkait.
- `openclaw/plugin-sdk/channel-runtime` sudah deprecated dan hanya tersisa sebagai
  shim kompatibilitas untuk plugin lama. Kode baru harus mengimpor primitif generik yang lebih sempit,
  dan kode repo tidak boleh menambahkan impor baru dari shim tersebut.
- Internal extension bundled tetap privat. Plugin eksternal seharusnya hanya menggunakan
  subpath `openclaw/plugin-sdk/*`. Kode core/test OpenClaw dapat menggunakan
  entry point publik repo di bawah root package plugin seperti `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, dan file yang ruang lingkupnya sempit seperti
  `login-qr-api.js`. Jangan pernah mengimpor `src/*` package plugin dari core atau dari
  extension lain.
- Pemisahan entry point repo:
  `<plugin-package-root>/api.js` adalah barrel helper/tipe,
  `<plugin-package-root>/runtime-api.js` adalah barrel khusus runtime,
  `<plugin-package-root>/index.js` adalah entri plugin bundled,
  dan `<plugin-package-root>/setup-entry.js` adalah entri plugin setup.
- Contoh provider bundled saat ini:
  - Anthropic menggunakan `api.js` / `contract-api.js` untuk helper stream Claude seperti
    `wrapAnthropicProviderStream`, helper beta-header, dan parsing `service_tier`.
  - OpenAI menggunakan `api.js` untuk builder provider, helper model default, dan
    builder provider realtime.
  - OpenRouter menggunakan `api.js` untuk builder provider-nya serta helper onboarding/config,
    sementara `register.runtime.js` masih dapat mengekspor ulang helper
    `plugin-sdk/provider-stream` generik untuk penggunaan lokal repo.
- Entry point publik yang dimuat melalui facade mengutamakan snapshot config runtime aktif
  ketika ada, lalu fallback ke file config yang telah di-resolve di disk ketika
  OpenClaw belum menyajikan snapshot runtime.
- Primitif generik bersama tetap menjadi kontrak Plugin SDK publik yang diutamakan. Masih ada
  sekumpulan kecil seam helper bermerek channel bundled yang dicadangkan untuk kompatibilitas.
  Perlakukan itu sebagai seam untuk pemeliharaan/kompatibilitas bundled, bukan target impor pihak ketiga baru; kontrak lintas channel baru tetap harus mendarat pada subpath `plugin-sdk/*` generik atau barrel `api.js` /
  `runtime-api.js` lokal plugin.

Catatan kompatibilitas:

- Hindari barrel root `openclaw/plugin-sdk` untuk kode baru.
- Utamakan primitif stabil yang sempit terlebih dahulu. Subpath setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool yang lebih baru adalah kontrak yang dituju untuk pekerjaan plugin
  bundled dan eksternal yang baru.
  Parsing/matching target seharusnya berada di `openclaw/plugin-sdk/channel-targets`.
  Gate aksi pesan dan helper message-id reaksi seharusnya berada di
  `openclaw/plugin-sdk/channel-actions`.
- Barrel helper khusus extension bundled tidak stabil secara default. Jika sebuah
  helper hanya dibutuhkan oleh extension bundled, simpan di balik seam
  `api.js` atau `runtime-api.js` lokal extension tersebut alih-alih mempromosikannya ke
  `openclaw/plugin-sdk/<extension>`.
- Seam helper bersama yang baru harus generik, bukan bermerek channel. Parsing target bersama
  seharusnya berada di `openclaw/plugin-sdk/channel-targets`; internal khusus channel
  tetap berada di balik seam `api.js` atau `runtime-api.js` lokal plugin yang memilikinya.
- Subpath khusus kapabilitas seperti `image-generation`,
  `media-understanding`, dan `speech` ada karena plugin
  bundled/native menggunakannya saat ini. Keberadaannya sendiri tidak serta-merta berarti setiap helper yang diekspor adalah kontrak eksternal jangka panjang yang dibekukan.

## Schema tool pesan

Plugin seharusnya memiliki kontribusi schema `describeMessageTool(...)` khusus channel.
Simpan field khusus provider di plugin, bukan di core bersama.

Untuk fragmen schema portabel bersama, gunakan kembali helper generik yang diekspor melalui
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` untuk payload gaya grid tombol
- `createMessageToolCardSchema()` untuk payload kartu terstruktur

Jika bentuk schema hanya masuk akal untuk satu provider, definisikan di source
plugin itu sendiri alih-alih mempromosikannya ke SDK bersama.

## Resolusi target channel

Plugin channel seharusnya memiliki semantik target khusus channel. Pertahankan host outbound
bersifat generik dan gunakan surface adapter pesan untuk aturan provider:

- `messaging.inferTargetChatType({ to })` memutuskan apakah target yang telah dinormalisasi
  harus diperlakukan sebagai `direct`, `group`, atau `channel` sebelum lookup direktori.
- `messaging.targetResolver.looksLikeId(raw, normalized)` memberi tahu core apakah sebuah
  input harus langsung melewati ke resolusi mirip-id alih-alih pencarian direktori.
- `messaging.targetResolver.resolveTarget(...)` adalah fallback plugin ketika
  core memerlukan resolusi akhir milik provider setelah normalisasi atau setelah direktori tidak menemukan hasil.
- `messaging.resolveOutboundSessionRoute(...)` memiliki konstruksi route sesi
  khusus provider setelah suatu target di-resolve.

Pemisahan yang direkomendasikan:

- Gunakan `inferTargetChatType` untuk keputusan kategori yang seharusnya terjadi sebelum
  mencari peer/group.
- Gunakan `looksLikeId` untuk pemeriksaan "perlakukan ini sebagai id target eksplisit/native".
- Gunakan `resolveTarget` untuk fallback normalisasi khusus provider, bukan untuk
  pencarian direktori yang luas.
- Simpan id native provider seperti chat id, thread id, JID, handle, dan room
  id di dalam nilai `target` atau parameter khusus provider, bukan di field SDK generik.

## Direktori berbasis config

Plugin yang menurunkan entri direktori dari config seharusnya menyimpan logika itu di
plugin dan menggunakan kembali helper bersama dari
`openclaw/plugin-sdk/directory-runtime`.

Gunakan ini ketika sebuah channel memerlukan peer/group berbasis config seperti:

- peer DM berbasis allowlist
- peta channel/group yang dikonfigurasi
- fallback direktori statis yang diskop per akun

Helper bersama di `directory-runtime` hanya menangani operasi generik:

- pemfilteran query
- penerapan batas
- helper dedupe/normalisasi
- membangun `ChannelDirectoryEntry[]`

Inspeksi akun khusus channel dan normalisasi id harus tetap berada di
implementasi plugin.

## Katalog provider

Plugin provider dapat mendefinisikan katalog model untuk inferensi dengan
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` mengembalikan bentuk yang sama seperti yang ditulis OpenClaw ke
`models.providers`:

- `{ provider }` untuk satu entri provider
- `{ providers }` untuk beberapa entri provider

Gunakan `catalog` ketika plugin memiliki model id khusus provider, default base URL, atau metadata model yang dikendalikan auth.

`catalog.order` mengontrol kapan katalog plugin di-merge relatif terhadap
provider implisit bawaan OpenClaw:

- `simple`: provider biasa berbasis API key atau env
- `profile`: provider yang muncul ketika profil auth ada
- `paired`: provider yang mensintesis beberapa entri provider terkait
- `late`: lintasan terakhir, setelah provider implisit lain

Provider yang datang belakangan menang pada konflik key, sehingga plugin dapat
secara sengaja menimpa entri provider bawaan dengan id provider yang sama.

Kompatibilitas:

- `discovery` tetap berfungsi sebagai alias legacy
- jika `catalog` dan `discovery` sama-sama didaftarkan, OpenClaw menggunakan `catalog`

## Inspeksi channel read-only

Jika plugin Anda mendaftarkan sebuah channel, utamakan implementasi
`plugin.config.inspectAccount(cfg, accountId)` bersama `resolveAccount(...)`.

Alasannya:

- `resolveAccount(...)` adalah jalur runtime. Fungsi ini boleh berasumsi bahwa kredensial
  sudah sepenuhnya dimaterialisasi dan dapat gagal cepat ketika secret yang diperlukan tidak ada.
- Jalur perintah read-only seperti `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`, dan flow doctor/config
  repair seharusnya tidak perlu mematerialisasi kredensial runtime hanya untuk
  mendeskripsikan konfigurasi.

Perilaku `inspectAccount(...)` yang direkomendasikan:

- Hanya kembalikan status akun yang deskriptif.
- Pertahankan `enabled` dan `configured`.
- Sertakan field sumber/status kredensial bila relevan, seperti:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Anda tidak perlu mengembalikan nilai token mentah hanya untuk melaporkan ketersediaan
  read-only. Mengembalikan `tokenStatus: "available"` (dan field sumber yang sesuai)
  sudah cukup untuk perintah bergaya status.
- Gunakan `configured_unavailable` ketika kredensial dikonfigurasi melalui SecretRef tetapi
  tidak tersedia pada jalur perintah saat ini.

Hal ini memungkinkan perintah read-only melaporkan "dikonfigurasi tetapi tidak tersedia di jalur perintah ini"
alih-alih crash atau salah melaporkan akun sebagai tidak dikonfigurasi.

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

Jika plugin Anda mengimpor dependensi npm, pasang dependensi itu di direktori tersebut agar
`node_modules` tersedia (`npm install` / `pnpm install`).

Guardrail keamanan: setiap entri `openclaw.extensions` harus tetap berada di dalam direktori plugin
setelah resolusi symlink. Entri yang keluar dari direktori package akan
ditolak.

Catatan keamanan: `openclaw plugins install` memasang dependensi plugin dengan
`npm install --omit=dev --ignore-scripts` (tanpa lifecycle script, tanpa dev dependencies saat runtime). Pertahankan pohon dependensi plugin tetap "pure JS/TS" dan hindari package yang memerlukan build `postinstall`.

Opsional: `openclaw.setupEntry` dapat menunjuk ke modul ringan khusus setup.
Saat OpenClaw membutuhkan surface setup untuk plugin channel yang dinonaktifkan, atau
ketika plugin channel diaktifkan tetapi masih belum dikonfigurasi, OpenClaw memuat `setupEntry`
alih-alih entri plugin penuh. Hal ini menjaga startup dan setup tetap lebih ringan
ketika entri plugin utama Anda juga menghubungkan tools, hooks, atau kode khusus runtime lainnya.

Opsional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
dapat mengikutsertakan plugin channel ke jalur `setupEntry` yang sama selama fase
startup pra-listen gateway, bahkan ketika channel sudah dikonfigurasi.

Gunakan ini hanya ketika `setupEntry` sepenuhnya mencakup surface startup yang harus ada
sebelum gateway mulai mendengarkan. Dalam praktiknya, itu berarti entri setup
harus mendaftarkan setiap kapabilitas milik channel yang dibutuhkan startup, seperti:

- pendaftaran channel itu sendiri
- setiap route HTTP yang harus tersedia sebelum gateway mulai mendengarkan
- setiap metode Gateway, tool, atau layanan yang harus ada selama jendela yang sama

Jika entri penuh Anda masih memiliki kapabilitas startup yang dibutuhkan, jangan aktifkan
flag ini. Pertahankan plugin pada perilaku default dan biarkan OpenClaw memuat
entri penuh saat startup.

Channel bundled juga dapat menerbitkan helper contract-surface khusus setup yang dapat
dikonsultasikan core sebelum runtime channel penuh dimuat. Surface promosi setup saat ini
adalah:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Core menggunakan surface itu ketika perlu mempromosikan config channel single-account legacy
menjadi `channels.<id>.accounts.*` tanpa memuat entri plugin penuh.
Matrix adalah contoh bundled saat ini: Matrix hanya memindahkan key auth/bootstrap
ke akun hasil promosi bernama ketika akun bernama sudah ada, dan dapat
mempertahankan key default-account non-kanonis yang telah dikonfigurasi alih-alih selalu membuat
`accounts.default`.

Adapter patch setup itu menjaga discovery contract-surface bundled tetap lazy. Waktu impor tetap ringan; surface promosi hanya dimuat saat pertama kali digunakan alih-alih kembali memasuki startup channel bundled saat impor modul.

Ketika surface startup itu mencakup metode RPC Gateway, simpan pada prefix khusus
plugin. Namespace admin core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) tetap dicadangkan dan selalu di-resolve
ke `operator.admin`, bahkan jika sebuah plugin meminta scope yang lebih sempit.

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
petunjuk instalasi melalui `openclaw.install`. Ini menjaga data katalog core tetap bebas data.

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
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
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
- `docsLabel`: menimpa teks tautan untuk tautan dokumentasi
- `preferOver`: id plugin/channel prioritas lebih rendah yang harus dikalahkan oleh entri katalog ini
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: kontrol salinan surface pemilihan
- `markdownCapable`: menandai channel sebagai mampu markdown untuk keputusan pemformatan outbound
- `exposure.configured`: sembunyikan channel dari surface daftar channel yang telah dikonfigurasi ketika diatur ke `false`
- `exposure.setup`: sembunyikan channel dari picker setup/configure interaktif ketika diatur ke `false`
- `exposure.docs`: tandai channel sebagai internal/pribadi untuk surface navigasi dokumentasi
- `showConfigured` / `showInSetup`: alias legacy yang masih diterima demi kompatibilitas; utamakan `exposure`
- `quickstartAllowFrom`: mengikutsertakan channel ke flow `allowFrom` quickstart standar
- `forceAccountBinding`: mengharuskan pengikatan akun eksplisit bahkan ketika hanya ada satu akun
- `preferSessionLookupForAnnounceTarget`: mengutamakan lookup sesi saat me-resolve target announce

OpenClaw juga dapat menggabungkan **katalog channel eksternal** (misalnya, ekspor registry
MPM). Letakkan file JSON di salah satu lokasi berikut:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Atau arahkan `OPENCLAW_PLUGIN_CATALOG_PATHS` (atau `OPENCLAW_MPM_CATALOG_PATHS`) ke
satu atau lebih file JSON (dipisahkan dengan koma/titik koma/`PATH`). Setiap file harus
berisi `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. Parser juga menerima `"packages"` atau `"plugins"` sebagai alias legacy untuk key `"entries"`.

## Plugin context engine

Plugin context engine memiliki orkestrasi konteks sesi untuk ingest, assembly,
dan compaction. Daftarkan dari plugin Anda dengan
`api.registerContextEngine(id, factory)`, lalu pilih engine aktif dengan
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

Jika engine Anda **tidak** memiliki algoritme compaction, tetap implementasikan `compact()`
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

Ketika sebuah plugin membutuhkan perilaku yang tidak cocok dengan API saat ini, jangan melewati
sistem plugin dengan reach-in privat. Tambahkan kapabilitas yang belum ada.

Urutan yang direkomendasikan:

1. definisikan kontrak core
   Tentukan perilaku bersama apa yang harus dimiliki core: kebijakan, fallback, merge config,
   lifecycle, semantik yang berhadapan dengan channel, dan bentuk helper runtime.
2. tambahkan surface pendaftaran/runtime plugin yang typed
   Perluas `OpenClawPluginApi` dan/atau `api.runtime` dengan surface kapabilitas typed
   terkecil yang berguna.
3. hubungkan konsumen core + channel/fitur
   Plugin channel dan fitur harus mengonsumsi kapabilitas baru melalui core,
   bukan dengan mengimpor implementasi vendor secara langsung.
4. daftarkan implementasi vendor
   Plugin vendor kemudian mendaftarkan backend mereka ke kapabilitas tersebut.
5. tambahkan cakupan kontrak
   Tambahkan test agar bentuk kepemilikan dan pendaftaran tetap eksplisit dari waktu ke waktu.

Inilah cara OpenClaw tetap opinionated tanpa menjadi di-hardcode ke worldview
satu provider. Lihat [Cookbook Capability](/id/plugins/architecture)
untuk checklist file yang konkret dan contoh yang sudah dikerjakan.

### Checklist kapabilitas

Saat Anda menambahkan kapabilitas baru, implementasinya biasanya harus menyentuh
surface-surface ini secara bersamaan:

- tipe kontrak core di `src/<capability>/types.ts`
- runner/helper runtime core di `src/<capability>/runtime.ts`
- surface pendaftaran API plugin di `src/plugins/types.ts`
- wiring registry plugin di `src/plugins/registry.ts`
- eksposur runtime plugin di `src/plugins/runtime/*` ketika plugin fitur/channel
  perlu mengonsumsinya
- helper capture/test di `src/test-utils/plugin-registration.ts`
- asersi kepemilikan/kontrak di `src/plugins/contracts/registry.ts`
- dokumentasi operator/plugin di `docs/`

Jika salah satu surface itu hilang, biasanya itu adalah tanda bahwa kapabilitas tersebut
belum terintegrasi sepenuhnya.

### Template kapabilitas

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

Pola contract test:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Itu menjaga aturannya tetap sederhana:

- core memiliki kontrak kapabilitas + orkestrasi
- plugin vendor memiliki implementasi vendor
- plugin fitur/channel mengonsumsi helper runtime
- contract test menjaga kepemilikan tetap eksplisit
