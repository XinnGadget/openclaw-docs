---
read_when:
    - Menggunakan atau mengonfigurasi perintah chat
    - Men-debug routing atau izin perintah
summary: 'Perintah slash: teks vs native, config, dan perintah yang didukung'
title: Perintah slash
x-i18n:
    generated_at: "2026-04-12T23:33:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9ef6f54500fa2ce3b873a8398d6179a0882b8bf6fba38f61146c64671055505e
    source_path: tools/slash-commands.md
    workflow: 15
---

# Perintah slash

Perintah ditangani oleh Gateway. Sebagian besar perintah harus dikirim sebagai pesan **mandiri** yang diawali dengan `/`.
Perintah chat bash khusus host menggunakan `! <cmd>` (dengan `/bash <cmd>` sebagai alias).

Ada dua sistem yang terkait:

- **Perintah**: pesan `/...` mandiri.
- **Directive**: `/think`, `/fast`, `/verbose`, `/trace`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Directive dihapus dari pesan sebelum model melihatnya.
  - Dalam pesan chat normal (bukan pesan yang hanya berisi directive), directive diperlakukan sebagai “petunjuk inline” dan **tidak** menyimpan pengaturan sesi.
  - Dalam pesan yang hanya berisi directive (pesan hanya berisi directive), directive disimpan ke sesi dan membalas dengan pengakuan.
  - Directive hanya diterapkan untuk **pengirim yang berwenang**. Jika `commands.allowFrom` disetel, itu adalah satu-satunya
    allowlist yang digunakan; jika tidak, otorisasi berasal dari allowlist/pairing channel ditambah `commands.useAccessGroups`.
    Pengirim yang tidak berwenang akan melihat directive diperlakukan sebagai teks biasa.

Ada juga beberapa **inline shortcut** (hanya untuk pengirim yang ada dalam allowlist/berwenang): `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Perintah ini dijalankan segera, dihapus sebelum model melihatnya, dan teks yang tersisa melanjutkan flow normal.

## Config

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (default `true`) mengaktifkan parsing `/...` dalam pesan chat.
  - Pada surface tanpa perintah native (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams), perintah teks tetap berfungsi meskipun Anda menyetelnya ke `false`.
- `commands.native` (default `"auto"`) mendaftarkan perintah native.
  - Auto: aktif untuk Discord/Telegram; nonaktif untuk Slack (sampai Anda menambahkan slash command); diabaikan untuk provider tanpa dukungan native.
  - Setel `channels.discord.commands.native`, `channels.telegram.commands.native`, atau `channels.slack.commands.native` untuk override per provider (bool atau `"auto"`).
  - `false` menghapus perintah yang sebelumnya terdaftar di Discord/Telegram saat startup. Perintah Slack dikelola di aplikasi Slack dan tidak dihapus secara otomatis.
- `commands.nativeSkills` (default `"auto"`) mendaftarkan perintah **skill** secara native saat didukung.
  - Auto: aktif untuk Discord/Telegram; nonaktif untuk Slack (Slack memerlukan pembuatan slash command per skill).
  - Setel `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills`, atau `channels.slack.commands.nativeSkills` untuk override per provider (bool atau `"auto"`).
- `commands.bash` (default `false`) mengaktifkan `! <cmd>` untuk menjalankan perintah shell host (`/bash <cmd>` adalah alias; memerlukan allowlist `tools.elevated`).
- `commands.bashForegroundMs` (default `2000`) mengontrol berapa lama bash menunggu sebelum beralih ke mode latar belakang (`0` langsung ke latar belakang).
- `commands.config` (default `false`) mengaktifkan `/config` (membaca/menulis `openclaw.json`).
- `commands.mcp` (default `false`) mengaktifkan `/mcp` (membaca/menulis config MCP yang dikelola OpenClaw di bawah `mcp.servers`).
- `commands.plugins` (default `false`) mengaktifkan `/plugins` (discovery/status plugin plus kontrol install + enable/disable).
- `commands.debug` (default `false`) mengaktifkan `/debug` (override khusus runtime).
- `commands.restart` (default `true`) mengaktifkan `/restart` plus tindakan tool restart gateway.
- `commands.ownerAllowFrom` (opsional) menetapkan allowlist owner eksplisit untuk surface perintah/tool khusus owner. Ini terpisah dari `commands.allowFrom`.
- `commands.ownerDisplay` mengontrol bagaimana id owner muncul di system prompt: `raw` atau `hash`.
- `commands.ownerDisplaySecret` secara opsional menetapkan secret HMAC yang digunakan saat `commands.ownerDisplay="hash"`.
- `commands.allowFrom` (opsional) menetapkan allowlist per provider untuk otorisasi perintah. Ketika dikonfigurasi, ini adalah
  satu-satunya sumber otorisasi untuk perintah dan directive (`commands.useAccessGroups` serta allowlist/pairing channel
  diabaikan). Gunakan `"*"` untuk default global; key khusus provider menimpa default tersebut.
- `commands.useAccessGroups` (default `true`) menegakkan allowlist/kebijakan untuk perintah saat `commands.allowFrom` tidak disetel.

## Daftar perintah

Sumber kebenaran saat ini:

- built-in core berasal dari `src/auto-reply/commands-registry.shared.ts`
- perintah dock yang dihasilkan berasal dari `src/auto-reply/commands-registry.data.ts`
- perintah plugin berasal dari pemanggilan `registerCommand()` plugin
- ketersediaan aktual di gateway Anda tetap bergantung pada flag config, surface channel, dan plugin yang terinstal/diaktifkan

### Perintah built-in core

Perintah built-in yang tersedia saat ini:

- `/new [model]` memulai sesi baru; `/reset` adalah alias reset.
- `/compact [instructions]` melakukan compaction pada konteks sesi. Lihat [/concepts/compaction](/id/concepts/compaction).
- `/stop` membatalkan eksekusi saat ini.
- `/session idle <duration|off>` dan `/session max-age <duration|off>` mengelola kedaluwarsa pengikatan thread.
- `/think <off|minimal|low|medium|high|xhigh>` menetapkan level thinking. Alias: `/thinking`, `/t`.
- `/verbose on|off|full` mengaktifkan/menonaktifkan output verbose. Alias: `/v`.
- `/trace on|off` mengaktifkan/menonaktifkan output trace plugin untuk sesi saat ini.
- `/fast [status|on|off]` menampilkan atau mengatur mode cepat.
- `/reasoning [on|off|stream]` mengaktifkan/menonaktifkan visibilitas reasoning. Alias: `/reason`.
- `/elevated [on|off|ask|full]` mengaktifkan/menonaktifkan mode elevated. Alias: `/elev`.
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` menampilkan atau mengatur default exec.
- `/model [name|#|status]` menampilkan atau mengatur model.
- `/models [provider] [page] [limit=<n>|size=<n>|all]` menampilkan daftar provider atau model untuk suatu provider.
- `/queue <mode>` mengelola perilaku antrean (`steer`, `interrupt`, `followup`, `collect`, `steer-backlog`) plus opsi seperti `debounce:2s cap:25 drop:summarize`.
- `/help` menampilkan ringkasan bantuan singkat.
- `/commands` menampilkan katalog perintah yang dihasilkan.
- `/tools [compact|verbose]` menampilkan apa yang dapat digunakan agen saat ini.
- `/status` menampilkan status runtime, termasuk penggunaan/kuota provider jika tersedia.
- `/tasks` menampilkan daftar tugas latar belakang aktif/terbaru untuk sesi saat ini.
- `/context [list|detail|json]` menjelaskan bagaimana konteks dirakit.
- `/export-session [path]` mengekspor sesi saat ini ke HTML. Alias: `/export`.
- `/whoami` menampilkan id pengirim Anda. Alias: `/id`.
- `/skill <name> [input]` menjalankan skill berdasarkan nama.
- `/allowlist [list|add|remove] ...` mengelola entri allowlist. Hanya teks.
- `/approve <id> <decision>` menyelesaikan prompt persetujuan exec.
- `/btw <question>` mengajukan pertanyaan sampingan tanpa mengubah konteks sesi di masa depan. Lihat [/tools/btw](/id/tools/btw).
- `/subagents list|kill|log|info|send|steer|spawn` mengelola eksekusi sub-agent untuk sesi saat ini.
- `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` mengelola sesi ACP dan opsi runtime.
- `/focus <target>` mengikat thread Discord atau topik/percakapan Telegram saat ini ke target sesi.
- `/unfocus` menghapus pengikatan saat ini.
- `/agents` menampilkan daftar agen yang terikat ke thread untuk sesi saat ini.
- `/kill <id|#|all>` membatalkan satu atau semua sub-agent yang sedang berjalan.
- `/steer <id|#> <message>` mengirim steering ke sub-agent yang sedang berjalan. Alias: `/tell`.
- `/config show|get|set|unset` membaca atau menulis `openclaw.json`. Hanya owner. Memerlukan `commands.config: true`.
- `/mcp show|get|set|unset` membaca atau menulis config server MCP yang dikelola OpenClaw di bawah `mcp.servers`. Hanya owner. Memerlukan `commands.mcp: true`.
- `/plugins list|inspect|show|get|install|enable|disable` memeriksa atau mengubah status plugin. `/plugin` adalah alias. Penulisan hanya untuk owner. Memerlukan `commands.plugins: true`.
- `/debug show|set|unset|reset` mengelola override config khusus runtime. Hanya owner. Memerlukan `commands.debug: true`.
- `/usage off|tokens|full|cost` mengontrol footer penggunaan per-respons atau mencetak ringkasan biaya lokal.
- `/tts on|off|status|provider|limit|summary|audio|help` mengontrol TTS. Lihat [/tools/tts](/id/tools/tts).
- `/restart` memulai ulang OpenClaw saat diaktifkan. Default: aktif; setel `commands.restart: false` untuk menonaktifkannya.
- `/activation mention|always` menetapkan mode aktivasi grup.
- `/send on|off|inherit` menetapkan kebijakan pengiriman. Hanya owner.
- `/bash <command>` menjalankan perintah shell host. Hanya teks. Alias: `! <command>`. Memerlukan `commands.bash: true` plus allowlist `tools.elevated`.
- `!poll [sessionId]` memeriksa pekerjaan bash latar belakang.
- `!stop [sessionId]` menghentikan pekerjaan bash latar belakang.

### Perintah dock yang dihasilkan

Perintah dock dihasilkan dari plugin channel dengan dukungan perintah native. Kumpulan bundled saat ini:

- `/dock-discord` (alias: `/dock_discord`)
- `/dock-mattermost` (alias: `/dock_mattermost`)
- `/dock-slack` (alias: `/dock_slack`)
- `/dock-telegram` (alias: `/dock_telegram`)

### Perintah Plugin yang dibundel

Plugin bundled dapat menambahkan lebih banyak slash command. Perintah bundled saat ini di repo ini:

- `/dreaming [on|off|status|help]` mengaktifkan/menonaktifkan memory Dreaming. Lihat [Dreaming](/id/concepts/dreaming).
- `/pair [qr|status|pending|approve|cleanup|notify]` mengelola flow pairing/setup perangkat. Lihat [Pairing](/id/channels/pairing).
- `/phone status|arm <camera|screen|writes|all> [duration]|disarm` mempersenjatai sementara perintah node ponsel berisiko tinggi.
- `/voice status|list [limit]|set <voiceId|name>` mengelola config suara Talk. Di Discord, nama perintah native adalah `/talkvoice`.
- `/card ...` mengirim preset rich card LINE. Lihat [LINE](/id/channels/line).
- `/codex status|models|threads|resume|compact|review|account|mcp|skills` memeriksa dan mengontrol harness app-server Codex yang dibundel. Lihat [Codex Harness](/id/plugins/codex-harness).
- Perintah khusus QQBot:
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### Perintah skill dinamis

Skill yang dapat dipanggil pengguna juga diekspos sebagai slash command:

- `/skill <name> [input]` selalu berfungsi sebagai entrypoint generik.
- skill juga dapat muncul sebagai perintah langsung seperti `/prose` ketika skill/plugin mendaftarkannya.
- pendaftaran perintah skill native dikontrol oleh `commands.nativeSkills` dan `channels.<provider>.commands.nativeSkills`.

Catatan:

- Perintah menerima `:` opsional di antara perintah dan argumen (misalnya `/think: high`, `/send: on`, `/help:`).
- `/new <model>` menerima alias model, `provider/model`, atau nama provider (pencocokan fuzzy); jika tidak ada yang cocok, teks diperlakukan sebagai isi pesan.
- Untuk rincian penggunaan provider lengkap, gunakan `openclaw status --usage`.
- `/allowlist add|remove` memerlukan `commands.config=true` dan menghormati `configWrites` channel.
- Pada channel multi-akun, `/allowlist --account <id>` yang menargetkan config dan `/config set channels.<provider>.accounts.<id>...` juga menghormati `configWrites` akun target.
- `/usage` mengontrol footer penggunaan per-respons; `/usage cost` mencetak ringkasan biaya lokal dari log sesi OpenClaw.
- `/restart` aktif secara default; setel `commands.restart: false` untuk menonaktifkannya.
- `/plugins install <spec>` menerima spesifikasi plugin yang sama seperti `openclaw plugins install`: path/arsip lokal, package npm, atau `clawhub:<pkg>`.
- `/plugins enable|disable` memperbarui config plugin dan mungkin meminta restart.
- Perintah native khusus Discord: `/vc join|leave|status` mengontrol voice channel (memerlukan `channels.discord.voice` dan perintah native; tidak tersedia sebagai teks).
- Perintah pengikatan thread Discord (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`) memerlukan agar pengikatan thread efektif diaktifkan (`session.threadBindings.enabled` dan/atau `channels.discord.threadBindings.enabled`).
- Referensi perintah ACP dan perilaku runtime: [Agen ACP](/id/tools/acp-agents).
- `/verbose` dimaksudkan untuk debugging dan visibilitas tambahan; biarkan tetap **off** dalam penggunaan normal.
- `/trace` lebih sempit daripada `/verbose`: hanya menampilkan baris trace/debug milik plugin dan menjaga chatter tool verbose normal tetap nonaktif.
- `/fast on|off` menyimpan override sesi. Gunakan opsi `inherit` di UI Sessions untuk menghapusnya dan kembali ke default config.
- `/fast` bersifat khusus provider: OpenAI/OpenAI Codex memetakannya ke `service_tier=priority` pada endpoint Responses native, sementara permintaan Anthropic publik langsung, termasuk lalu lintas yang diautentikasi OAuth yang dikirim ke `api.anthropic.com`, memetakannya ke `service_tier=auto` atau `standard_only`. Lihat [OpenAI](/id/providers/openai) dan [Anthropic](/id/providers/anthropic).
- Ringkasan kegagalan tool tetap ditampilkan jika relevan, tetapi teks kegagalan detail hanya disertakan saat `/verbose` adalah `on` atau `full`.
- `/reasoning`, `/verbose`, dan `/trace` berisiko dalam pengaturan grup: semuanya dapat mengungkap reasoning internal, output tool, atau diagnostik plugin yang tidak Anda maksudkan untuk diekspos. Sebaiknya biarkan nonaktif, terutama di chat grup.
- `/model` langsung menyimpan model sesi yang baru.
- Jika agen sedang idle, eksekusi berikutnya langsung menggunakannya.
- Jika sebuah eksekusi sudah aktif, OpenClaw menandai live switch sebagai tertunda dan hanya memulai ulang ke model baru pada titik retry yang bersih.
- Jika aktivitas tool atau output balasan sudah dimulai, perpindahan tertunda dapat tetap berada dalam antrean sampai kesempatan retry berikutnya atau giliran pengguna berikutnya.
- **Jalur cepat:** pesan yang hanya berisi perintah dari pengirim yang ada dalam allowlist ditangani segera (melewati antrean + model).
- **Pembatasan mention grup:** pesan yang hanya berisi perintah dari pengirim yang ada dalam allowlist melewati persyaratan mention.
- **Inline shortcut (hanya pengirim yang ada dalam allowlist):** perintah tertentu juga berfungsi saat disematkan di dalam pesan normal dan dihapus sebelum model melihat sisa teks.
  - Contoh: `hey /status` memicu balasan status, dan sisa teks melanjutkan flow normal.
- Saat ini: `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- Pesan yang hanya berisi perintah tetapi tidak berwenang diabaikan secara diam-diam, dan token `/...` inline diperlakukan sebagai teks biasa.
- **Perintah skill:** skill `user-invocable` diekspos sebagai slash command. Nama disanitasi menjadi `a-z0-9_` (maks 32 karakter); tabrakan diberi suffix numerik (misalnya `_2`).
  - `/skill <name> [input]` menjalankan skill berdasarkan nama (berguna saat batas perintah native mencegah per-skill command).
  - Secara default, perintah skill diteruskan ke model sebagai permintaan normal.
  - Skill secara opsional dapat mendeklarasikan `command-dispatch: tool` untuk merutekan perintah langsung ke tool (deterministik, tanpa model).
  - Contoh: `/prose` (plugin OpenProse) — lihat [OpenProse](/id/prose).
- **Argumen perintah native:** Discord menggunakan autocomplete untuk opsi dinamis (dan menu tombol saat Anda menghilangkan argumen wajib). Telegram dan Slack menampilkan menu tombol saat sebuah perintah mendukung pilihan dan Anda menghilangkan argumennya.

## `/tools`

`/tools` menjawab pertanyaan runtime, bukan pertanyaan config: **apa yang dapat digunakan agen ini saat ini di
percakapan ini**.

- Default `/tools` ringkas dan dioptimalkan untuk pemindaian cepat.
- `/tools verbose` menambahkan deskripsi singkat.
- Surface perintah native yang mendukung argumen mengekspos sakelar mode yang sama seperti `compact|verbose`.
- Hasilnya diskop ke sesi, jadi mengubah agen, channel, thread, otorisasi pengirim, atau model dapat
  mengubah output.
- `/tools` mencakup tool yang benar-benar dapat dijangkau saat runtime, termasuk tool core, tool plugin yang terhubung, dan tool milik channel.

Untuk mengedit profil dan override, gunakan panel Tools di Control UI atau surface config/katalog alih-alih
memperlakukan `/tools` sebagai katalog statis.

## Surface penggunaan (apa yang tampil di mana)

- **Penggunaan/kuota provider** (contoh: “Claude sisa 80%”) muncul di `/status` untuk provider model saat ini ketika pelacakan penggunaan diaktifkan. OpenClaw menormalkan jendela provider menjadi `% tersisa`; untuk MiniMax, field persentase yang hanya menunjukkan sisa dibalik sebelum ditampilkan, dan respons `model_remains` mengutamakan entri chat-model ditambah label paket yang diberi tag model.
- **Baris token/cache** di `/status` dapat fallback ke entri penggunaan transkrip terbaru ketika snapshot sesi live jarang. Nilai live nonnol yang sudah ada tetap menang, dan fallback transkrip juga dapat memulihkan label model runtime aktif plus total berorientasi prompt yang lebih besar ketika total yang tersimpan hilang atau lebih kecil.
- **Token/biaya per-respons** dikontrol oleh `/usage off|tokens|full` (ditambahkan ke balasan normal).
- `/model status` membahas **model/auth/endpoint**, bukan penggunaan.

## Pemilihan model (`/model`)

`/model` diimplementasikan sebagai directive.

Contoh:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

Catatan:

- `/model` dan `/model list` menampilkan picker ringkas bernomor (keluarga model + provider yang tersedia).
- Di Discord, `/model` dan `/models` membuka picker interaktif dengan dropdown provider dan model plus langkah Submit.
- `/model <#>` memilih dari picker tersebut (dan mengutamakan provider saat ini bila memungkinkan).
- `/model status` menampilkan tampilan detail, termasuk endpoint provider yang dikonfigurasi (`baseUrl`) dan mode API (`api`) jika tersedia.

## Override debug

`/debug` memungkinkan Anda menetapkan override config **khusus runtime** (di memory, bukan di disk). Hanya owner. Nonaktif secara default; aktifkan dengan `commands.debug: true`.

Contoh:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Catatan:

- Override langsung diterapkan ke pembacaan config baru, tetapi **tidak** menulis ke `openclaw.json`.
- Gunakan `/debug reset` untuk menghapus semua override dan kembali ke config di disk.

## Output trace plugin

`/trace` memungkinkan Anda mengaktifkan/menonaktifkan **baris trace/debug milik plugin yang diskop ke sesi** tanpa menyalakan mode verbose penuh.

Contoh:

```text
/trace
/trace on
/trace off
```

Catatan:

- `/trace` tanpa argumen menampilkan status trace sesi saat ini.
- `/trace on` mengaktifkan baris trace plugin untuk sesi saat ini.
- `/trace off` menonaktifkannya kembali.
- Baris trace plugin dapat muncul di `/status` dan sebagai pesan diagnostik tindak lanjut setelah balasan asisten normal.
- `/trace` tidak menggantikan `/debug`; `/debug` tetap mengelola override config khusus runtime.
- `/trace` tidak menggantikan `/verbose`; output tool/status verbose normal tetap milik `/verbose`.

## Pembaruan config

`/config` menulis ke config di disk Anda (`openclaw.json`). Hanya owner. Nonaktif secara default; aktifkan dengan `commands.config: true`.

Contoh:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

Catatan:

- Config divalidasi sebelum ditulis; perubahan yang tidak valid ditolak.
- Pembaruan `/config` tetap ada setelah restart.

## Pembaruan MCP

`/mcp` menulis definisi server MCP yang dikelola OpenClaw di bawah `mcp.servers`. Hanya owner. Nonaktif secara default; aktifkan dengan `commands.mcp: true`.

Contoh:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Catatan:

- `/mcp` menyimpan config di config OpenClaw, bukan pengaturan proyek milik Pi.
- Adapter runtime memutuskan transport mana yang benar-benar dapat dieksekusi.

## Pembaruan plugin

`/plugins` memungkinkan operator memeriksa plugin yang ditemukan dan mengaktifkan/menonaktifkan di config. Flow read-only dapat menggunakan `/plugin` sebagai alias. Nonaktif secara default; aktifkan dengan `commands.plugins: true`.

Contoh:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Catatan:

- `/plugins list` dan `/plugins show` menggunakan discovery plugin nyata terhadap workspace saat ini plus config di disk.
- `/plugins enable|disable` hanya memperbarui config plugin; tidak memasang atau menghapus plugin.
- Setelah perubahan enable/disable, restart gateway untuk menerapkannya.

## Catatan surface

- **Perintah teks** berjalan di sesi chat normal (DM berbagi `main`, grup memiliki sesi sendiri).
- **Perintah native** menggunakan sesi terisolasi:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>` (prefiks dapat dikonfigurasi melalui `channels.slack.slashCommand.sessionPrefix`)
  - Telegram: `telegram:slash:<userId>` (menargetkan sesi chat melalui `CommandTargetSessionKey`)
- **`/stop`** menargetkan sesi chat aktif sehingga dapat membatalkan eksekusi saat ini.
- **Slack:** `channels.slack.slashCommand` masih didukung untuk satu perintah bergaya `/openclaw`. Jika Anda mengaktifkan `commands.native`, Anda harus membuat satu slash command Slack per perintah built-in (nama sama seperti `/help`). Menu argumen perintah untuk Slack dikirim sebagai tombol Block Kit ephemeral.
  - Pengecualian native Slack: daftarkan `/agentstatus` (bukan `/status`) karena Slack mencadangkan `/status`. Teks `/status` tetap berfungsi dalam pesan Slack.

## Pertanyaan sampingan BTW

`/btw` adalah **pertanyaan sampingan** cepat tentang sesi saat ini.

Tidak seperti chat normal:

- menggunakan sesi saat ini sebagai konteks latar belakang,
- berjalan sebagai panggilan satu kali **tanpa tool** yang terpisah,
- tidak mengubah konteks sesi di masa depan,
- tidak ditulis ke riwayat transkrip,
- dikirim sebagai hasil sampingan live alih-alih pesan asisten normal.

Hal itu membuat `/btw` berguna saat Anda menginginkan klarifikasi sementara sementara
tugas utama tetap berjalan.

Contoh:

```text
/btw apa yang sedang kita lakukan sekarang?
```

Lihat [Pertanyaan Sampingan BTW](/id/tools/btw) untuk perilaku lengkap dan detail
UX klien.
