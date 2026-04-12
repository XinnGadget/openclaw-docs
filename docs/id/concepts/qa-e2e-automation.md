---
read_when:
    - Memperluas qa-lab atau qa-channel
    - Menambahkan skenario QA yang didukung repo
    - Membangun otomatisasi QA dengan realisme lebih tinggi di sekitar dasbor Gateway
summary: Bentuk otomatisasi QA privat untuk qa-lab, qa-channel, skenario berseed, dan laporan protokol
title: Otomatisasi QA E2E
x-i18n:
    generated_at: "2026-04-12T23:28:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: b9fe27dc049823d5e3eb7ae1eac6aad21ed9e917425611fb1dbcb28ab9210d5e
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Otomatisasi QA E2E

Stack QA privat ditujukan untuk menguji OpenClaw dengan cara yang lebih realistis dan menyerupai channel dibandingkan yang bisa dilakukan oleh satu unit test.

Komponen saat ini:

- `extensions/qa-channel`: channel pesan sintetis dengan permukaan DM, channel, thread, reaksi, edit, dan hapus.
- `extensions/qa-lab`: UI debugger dan bus QA untuk mengamati transkrip, menyuntikkan pesan masuk, dan mengekspor laporan Markdown.
- `qa/`: aset seed yang didukung repo untuk tugas awal dan skenario QA dasar.

Alur operator QA saat ini berupa situs QA dua panel:

- Kiri: dasbor Gateway (Control UI) dengan agen.
- Kanan: QA Lab, menampilkan transkrip bergaya Slack dan rencana skenario.

Jalankan dengan:

```bash
pnpm qa:lab:up
```

Perintah itu membangun situs QA, memulai lane Gateway berbasis Docker, dan menampilkan halaman QA Lab tempat operator atau loop otomatisasi dapat memberi agen misi QA, mengamati perilaku channel nyata, dan mencatat apa yang berhasil, gagal, atau tetap terblokir.

Untuk iterasi UI QA Lab yang lebih cepat tanpa membangun ulang image Docker setiap kali, mulai stack dengan bundle QA Lab yang di-bind mount:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` menjaga layanan Docker tetap berjalan pada image yang telah dibangun sebelumnya dan melakukan bind-mount `extensions/qa-lab/web/dist` ke dalam kontainer `qa-lab`. `qa:lab:watch` membangun ulang bundle tersebut saat ada perubahan, dan browser akan memuat ulang secara otomatis ketika hash aset QA Lab berubah.

Untuk lane smoke Matrix dengan transport nyata, jalankan:

```bash
pnpm openclaw qa matrix
```

Lane tersebut menyediakan homeserver Tuwunel sekali pakai di Docker, mendaftarkan pengguna driver, SUT, dan observer sementara, membuat satu room privat, lalu menjalankan Plugin Matrix nyata di dalam child Gateway QA. Lane transport langsung menjaga config child tetap dibatasi pada transport yang sedang diuji, sehingga Matrix berjalan tanpa `qa-channel` di config child.

Untuk lane smoke Telegram dengan transport nyata, jalankan:

```bash
pnpm openclaw qa telegram
```

Lane tersebut menargetkan satu grup Telegram privat nyata alih-alih menyediakan server sekali pakai. Lane ini memerlukan `OPENCLAW_QA_TELEGRAM_GROUP_ID`, `OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN`, dan `OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, serta dua bot berbeda di grup privat yang sama. Bot SUT harus memiliki username Telegram, dan observasi bot-ke-bot bekerja paling baik ketika kedua bot mengaktifkan Bot-to-Bot Communication Mode di `@BotFather`.

Lane transport langsung sekarang berbagi satu kontrak yang lebih kecil alih-alih masing-masing membuat bentuk daftar skenarionya sendiri:

`qa-channel` tetap menjadi suite perilaku produk sintetis yang luas dan bukan bagian dari matriks cakupan transport langsung.

| Lane     | Canary | Penyaringan mention | Blok allowlist | Balasan tingkat atas | Lanjut setelah restart | Tindak lanjut thread | Isolasi thread | Observasi reaksi | Perintah help |
| -------- | ------ | ------------------- | -------------- | -------------------- | ---------------------- | -------------------- | -------------- | ---------------- | ------------- |
| Matrix   | x      | x                   | x              | x                    | x                      | x                    | x              | x                |               |
| Telegram | x      |                     |                |                      |                        |                      |                |                  | x             |

Ini menjaga `qa-channel` sebagai suite perilaku produk yang luas, sementara Matrix, Telegram, dan transport langsung mendatang berbagi satu checklist kontrak transport yang eksplisit.

Untuk lane VM Linux sekali pakai tanpa membawa Docker ke dalam jalur QA, jalankan:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Ini akan mem-boot guest Multipass baru, menginstal dependensi, membangun OpenClaw di dalam guest, menjalankan `qa suite`, lalu menyalin laporan dan ringkasan QA normal kembali ke `.artifacts/qa-e2e/...` di host.
Perintah ini menggunakan perilaku pemilihan skenario yang sama seperti `qa suite` di host.
Eksekusi suite di host dan Multipass menjalankan beberapa skenario terpilih secara paralel dengan worker Gateway yang terisolasi secara default, hingga 64 worker atau sebanyak jumlah skenario yang dipilih. Gunakan `--concurrency <count>` untuk menyesuaikan jumlah worker, atau `--concurrency 1` untuk eksekusi serial.
Eksekusi langsung meneruskan input auth QA yang didukung dan praktis untuk guest: kunci provider berbasis env, path config provider langsung QA, dan `CODEX_HOME` jika ada. Pertahankan `--output-dir` di bawah root repo agar guest dapat menulis kembali melalui workspace yang di-mount.

## Seed yang didukung repo

Aset seed berada di `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Aset ini sengaja disimpan di git agar rencana QA terlihat oleh manusia maupun agen.

`qa-lab` harus tetap menjadi runner Markdown generik. Setiap file Markdown skenario adalah sumber kebenaran untuk satu eksekusi pengujian dan harus mendefinisikan:

- metadata skenario
- referensi dokumen dan kode
- persyaratan Plugin opsional
- patch config Gateway opsional
- `qa-flow` yang dapat dieksekusi

Daftar dasar harus tetap cukup luas untuk mencakup:

- chat DM dan channel
- perilaku thread
- siklus hidup aksi pesan
- callback Cron
- recall memori
- pergantian model
- handoff subagen
- pembacaan repo dan pembacaan dokumen
- satu tugas build kecil seperti Lobster Invaders

## Adaptor transport

`qa-lab` memiliki seam generik untuk skenario QA Markdown.
`qa-channel` adalah adaptor pertama pada seam tersebut, tetapi target desainnya lebih luas:
channel nyata atau sintetis di masa mendatang harus terhubung ke runner suite yang sama alih-alih menambahkan runner QA khusus transport.

Pada tingkat arsitektur, pembagiannya adalah:

- `qa-lab` memiliki eksekusi skenario generik, konkurensi worker, penulisan artefak, dan pelaporan.
- adaptor transport memiliki config Gateway, kesiapan, observasi masuk dan keluar, aksi transport, dan status transport ternormalisasi.
- file skenario Markdown di bawah `qa/scenarios/` mendefinisikan eksekusi pengujian; `qa-lab` menyediakan permukaan runtime yang dapat digunakan kembali untuk mengeksekusinya.

Panduan adopsi untuk maintainer bagi adaptor channel baru tersedia di
[Testing](/id/help/testing#adding-a-channel-to-qa).

## Pelaporan

`qa-lab` mengekspor laporan protokol Markdown dari timeline bus yang diamati.
Laporan tersebut harus menjawab:

- Apa yang berhasil
- Apa yang gagal
- Apa yang tetap terblokir
- Skenario tindak lanjut apa yang layak ditambahkan

Untuk pemeriksaan karakter dan gaya, jalankan skenario yang sama di beberapa ref model langsung dan tulis laporan Markdown yang dinilai:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

Perintah ini menjalankan child process Gateway QA lokal, bukan Docker. Skenario evaluasi karakter harus menetapkan persona melalui `SOUL.md`, lalu menjalankan giliran pengguna biasa seperti chat, bantuan workspace, dan tugas file kecil. Model kandidat tidak boleh diberi tahu bahwa model tersebut sedang dievaluasi. Perintah ini mempertahankan setiap transkrip lengkap, mencatat statistik dasar eksekusi, lalu meminta model judge dalam mode cepat dengan penalaran `xhigh` untuk memberi peringkat eksekusi berdasarkan kealamian, vibe, dan humor.
Gunakan `--blind-judge-models` saat membandingkan provider: prompt judge tetap menerima setiap transkrip dan status eksekusi, tetapi ref kandidat diganti dengan label netral seperti `candidate-01`; laporan memetakan kembali peringkat ke ref nyata setelah parsing.
Eksekusi kandidat secara default menggunakan thinking `high`, dengan `xhigh` untuk model OpenAI yang mendukungnya. Override kandidat tertentu secara inline dengan
`--model provider/model,thinking=<level>`. `--thinking <level>` tetap menetapkan fallback global, dan bentuk lama `--model-thinking <provider/model=level>` dipertahankan untuk kompatibilitas.
Ref kandidat OpenAI secara default menggunakan mode cepat agar pemrosesan prioritas digunakan jika provider mendukungnya. Tambahkan `,fast`, `,no-fast`, atau `,fast=false` secara inline ketika satu kandidat atau judge memerlukan override. Berikan `--fast` hanya jika Anda ingin memaksa mode cepat aktif untuk setiap model kandidat. Durasi kandidat dan judge dicatat dalam laporan untuk analisis benchmark, tetapi prompt judge secara eksplisit menyatakan agar tidak memberi peringkat berdasarkan kecepatan.
Eksekusi model kandidat dan judge keduanya secara default menggunakan konkurensi 16. Turunkan
`--concurrency` atau `--judge-concurrency` ketika batas provider atau tekanan Gateway lokal membuat eksekusi terlalu berisik.
Saat tidak ada kandidat `--model` yang diberikan, evaluasi karakter secara default menggunakan
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5`, dan
`google/gemini-3.1-pro-preview` saat tidak ada `--model` yang diberikan.
Saat tidak ada `--judge-model` yang diberikan, judge secara default menggunakan
`openai/gpt-5.4,thinking=xhigh,fast` dan
`anthropic/claude-opus-4-6,thinking=high`.

## Dokumen terkait

- [Testing](/id/help/testing)
- [QA Channel](/id/channels/qa-channel)
- [Dashboard](/web/dashboard)
