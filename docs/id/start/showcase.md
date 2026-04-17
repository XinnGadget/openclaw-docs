---
description: Real-world OpenClaw projects from the community
read_when:
    - Mencari contoh penggunaan OpenClaw di dunia nyata
    - Memperbarui sorotan proyek komunitas
summary: Proyek dan integrasi buatan komunitas yang didukung oleh OpenClaw
title: Pameran
x-i18n:
    generated_at: "2026-04-15T09:15:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 797d0b85c9eca920240c79d870eb9636216714f3eba871c5ebd0f7f40cf7bbf1
    source_path: start/showcase.md
    workflow: 15
---

<!-- markdownlint-disable MD033 -->

# Pameran

<div className="showcase-hero">
  <p className="showcase-kicker">Dibangun di chat, terminal, browser, dan ruang keluarga</p>
  <p className="showcase-lead">
    Proyek OpenClaw bukan demo main-main. Orang-orang sudah mengirim loop peninjauan PR, aplikasi seluler, otomatisasi rumah,
    sistem suara, devtools, dan alur kerja berat memori dari channel yang sudah mereka gunakan.
  </p>
  <div className="showcase-actions">
    <a href="#videos">Tonton demo</a>
    <a href="#fresh-from-discord">Jelajahi proyek</a>
    <a href="https://discord.gg/clawd">Bagikan punyamu</a>
  </div>
  <div className="showcase-highlights">
    <div className="showcase-highlight">
      <strong>Pembangunan native-chat</strong>
      <span>Telegram, WhatsApp, Discord, Beeper, chat web, dan alur kerja yang mengutamakan terminal.</span>
    </div>
    <div className="showcase-highlight">
      <strong>Otomatisasi nyata</strong>
      <span>Pemesanan, belanja, dukungan, pelaporan, dan kontrol browser tanpa menunggu API.</span>
    </div>
    <div className="showcase-highlight">
      <strong>Lokal + dunia fisik</strong>
      <span>Printer, penyedot debu, kamera, data kesehatan, sistem rumah, dan basis pengetahuan pribadi.</span>
    </div>
  </div>
</div>

<Info>
**Ingin ditampilkan?** Bagikan proyek Anda di [#self-promotion on Discord](https://discord.gg/clawd) atau [tag @openclaw di X](https://x.com/openclaw).
</Info>

<div className="showcase-jump-links">
  <a href="#videos">Video</a>
  <a href="#fresh-from-discord">Terbaru dari Discord</a>
  <a href="#automation-workflows">Otomatisasi</a>
  <a href="#knowledge-memory">Memori</a>
  <a href="#voice-phone">Suara &amp; Telepon</a>
  <a href="#infrastructure-deployment">Infrastruktur</a>
  <a href="#home-hardware">Rumah &amp; Perangkat Keras</a>
  <a href="#community-projects">Komunitas</a>
  <a href="#submit-your-project">Kirim proyek</a>
</div>

<h2 id="videos">Video</h2>

<p className="showcase-section-intro">
  Mulai dari sini jika Anda menginginkan jalur tercepat dari “apa ini?” ke “oke, saya paham.”
</p>

<div className="showcase-video-grid">
  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/SaWSPZoPX34"
        title="OpenClaw: AI self-hosted yang seharusnya menjadi Siri (Penyiapan lengkap)"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Panduan penyiapan lengkap</h3>
    <p>VelvetShark, 28 menit. Instal, onboard, dan dapatkan asisten pertama yang berfungsi dari awal hingga akhir.</p>
    <a href="https://www.youtube.com/watch?v=SaWSPZoPX34">Tonton di YouTube</a>
  </div>

  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/mMSKQvlmFuQ"
        title="Video pameran OpenClaw"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Reel pameran komunitas</h3>
    <p>Tinjauan yang lebih cepat atas proyek, permukaan, dan alur kerja nyata yang dibangun di sekitar OpenClaw.</p>
    <a href="https://www.youtube.com/watch?v=mMSKQvlmFuQ">Tonton di YouTube</a>
  </div>

  <div className="showcase-video-card">
    <div className="showcase-video-shell">
      <iframe
        src="https://www.youtube-nocookie.com/embed/5kkIJNUGFho"
        title="Pameran komunitas OpenClaw"
        loading="lazy"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
      />
    </div>
    <h3>Proyek nyata di lapangan</h3>
    <p>Contoh dari komunitas, mulai dari loop coding native-chat hingga perangkat keras dan otomatisasi pribadi.</p>
    <a href="https://www.youtube.com/watch?v=5kkIJNUGFho">Tonton di YouTube</a>
  </div>
</div>

<h2 id="fresh-from-discord">Terbaru dari Discord</h2>

<p className="showcase-section-intro">
  Sorotan terbaru di bidang coding, devtools, seluler, dan pembangunan produk native-chat.
</p>

<CardGroup cols={2}>

<Card title="Peninjauan PR → Umpan Balik Telegram" icon="code-pull-request" href="https://x.com/i/status/2010878524543131691">
  **@bangnokia** • `review` `github` `telegram`

OpenCode menyelesaikan perubahan → membuka PR → OpenClaw meninjau diff dan membalas di Telegram dengan “saran kecil” plus putusan merge yang jelas (termasuk perbaikan kritis yang harus diterapkan terlebih dahulu).

  <img src="/assets/showcase/pr-review-telegram.jpg" alt="Umpan balik peninjauan PR OpenClaw dikirim di Telegram" />
</Card>

<Card title="Skill Gudang Anggur dalam Hitungan Menit" icon="wine-glass" href="https://x.com/i/status/2010916352454791216">
  **@prades_maxime** • `skills` `local` `csv`

Meminta “Robby” (@openclaw) untuk membuat skill gudang anggur lokal. Ia meminta contoh ekspor CSV + lokasi penyimpanannya, lalu membangun/menguji skill dengan cepat (962 botol dalam contohnya).

  <img src="/assets/showcase/wine-cellar-skill.jpg" alt="OpenClaw membangun skill gudang anggur lokal dari CSV" />
</Card>

<Card title="Autopilot Belanja Tesco" icon="cart-shopping" href="https://x.com/i/status/2009724862470689131">
  **@marchattonhere** • `automation` `browser` `shopping`

Rencana makan mingguan → langganan rutin → pesan slot pengiriman → konfirmasi pesanan. Tanpa API, hanya kontrol browser.

  <img src="/assets/showcase/tesco-shop.jpg" alt="Otomatisasi belanja Tesco melalui chat" />
</Card>

<Card title="SNAG Screenshot-ke-Markdown" icon="scissors" href="https://github.com/am-will/snag">
  **@am-will** • `devtools` `screenshots` `markdown`

Gunakan hotkey pada area layar → visi Gemini → Markdown instan di clipboard Anda.

  <img src="/assets/showcase/snag.png" alt="Tool screenshot-ke-markdown SNAG" />
</Card>

<Card title="UI Agents" icon="window-maximize" href="https://releaseflow.net/kitze/agents-ui">
  **@kitze** • `ui` `skills` `sync`

Aplikasi desktop untuk mengelola skills/perintah di seluruh Agents, Claude, Codex, dan OpenClaw.

  <img src="/assets/showcase/agents-ui.jpg" alt="Aplikasi UI Agents" />
</Card>

<Card title="Catatan Suara Telegram (papla.media)" icon="microphone" href="https://papla.media/docs">
  **Komunitas** • `voice` `tts` `telegram`

Membungkus TTS papla.media dan mengirim hasilnya sebagai catatan suara Telegram (tanpa autoplay yang mengganggu).

  <img src="/assets/showcase/papla-tts.jpg" alt="Output catatan suara Telegram dari TTS" />
</Card>

<Card title="CodexMonitor" icon="eye" href="https://clawhub.ai/odrobnik/codexmonitor">
  **@odrobnik** • `devtools` `codex` `brew`

Helper yang diinstal melalui Homebrew untuk mencantumkan/memeriksa/memantau sesi OpenAI Codex lokal (CLI + VS Code).

  <img src="/assets/showcase/codexmonitor.png" alt="CodexMonitor di ClawHub" />
</Card>

<Card title="Kontrol Printer 3D Bambu" icon="print" href="https://clawhub.ai/tobiasbischoff/bambu-cli">
  **@tobiasbischoff** • `hardware` `3d-printing` `skill`

Mengontrol dan memecahkan masalah printer BambuLab: status, pekerjaan, kamera, AMS, kalibrasi, dan lainnya.

  <img src="/assets/showcase/bambu-cli.png" alt="Skill Bambu CLI di ClawHub" />
</Card>

<Card title="Transportasi Wina (Wiener Linien)" icon="train" href="https://clawhub.ai/hjanuschka/wienerlinien">
  **@hjanuschka** • `travel` `transport` `skill`

Keberangkatan real-time, gangguan, status lift, dan perutean untuk transportasi umum Wina.

  <img src="/assets/showcase/wienerlinien.png" alt="Skill Wiener Linien" />
</Card>

<Card title="Makanan Sekolah ParentPay" icon="utensils">
  **@George5562** • `automation` `browser` `parenting`

Pemesanan makanan sekolah di Inggris secara otomatis melalui ParentPay. Menggunakan koordinat mouse untuk klik sel tabel yang andal.
</Card>

<Card title="Unggah R2 (Kirim File Saya)" icon="cloud-arrow-up" href="https://clawhub.ai/skills/r2-upload">
  **@julianengel** • `files` `r2` `presigned-urls`

Unggah ke Cloudflare R2/S3 dan hasilkan tautan unduhan presigned yang aman. Sempurna untuk instance OpenClaw jarak jauh.
</Card>

<Card title="Aplikasi iOS melalui Telegram" icon="mobile">
  **@coard** • `ios` `xcode` `testflight`

Membangun aplikasi iOS lengkap dengan peta dan perekaman suara, lalu menerapkannya ke TestFlight sepenuhnya melalui chat Telegram.

  <img src="/assets/showcase/ios-testflight.jpg" alt="Aplikasi iOS di TestFlight" />
</Card>

<Card title="Asisten Kesehatan Oura Ring" icon="heart-pulse">
  **@AS** • `health` `oura` `calendar`

Asisten kesehatan AI pribadi yang mengintegrasikan data Oura ring dengan kalender, janji temu, dan jadwal gym.

  <img src="/assets/showcase/oura-health.png" alt="Asisten kesehatan Oura ring" />
</Card>
<Card title="Tim Impian Kev (14+ Agen)" icon="robot" href="https://github.com/adam91holt/orchestrated-ai-articles">
  **@adam91holt** • `multi-agent` `orchestration` `architecture` `manifesto`

14+ agen di bawah satu Gateway dengan orkestrator Opus 4.5 yang mendelegasikan ke pekerja Codex. [Tulisan teknis](https://github.com/adam91holt/orchestrated-ai-articles) yang komprehensif mencakup daftar Dream Team, pemilihan model, sandboxing, Webhook, Heartbeat, dan alur delegasi. [Clawdspace](https://github.com/adam91holt/clawdspace) untuk sandboxing agen. [Posting blog](https://adams-ai-journey.ghost.io/2026-the-year-of-the-orchestrator/).
</Card>

<Card title="CLI Linear" icon="terminal" href="https://github.com/Finesssee/linear-cli">
  **@NessZerra** • `devtools` `linear` `cli` `issues`

CLI untuk Linear yang terintegrasi dengan alur kerja agentic (Claude Code, OpenClaw). Kelola issue, proyek, dan alur kerja dari terminal. PR eksternal pertama berhasil di-merge!
</Card>

<Card title="CLI Beeper" icon="message" href="https://github.com/blqke/beepcli">
  **@jules** • `messaging` `beeper` `cli` `automation`

Membaca, mengirim, dan mengarsipkan pesan melalui Beeper Desktop. Menggunakan API MCP lokal Beeper sehingga agen dapat mengelola semua chat Anda (iMessage, WhatsApp, dll.) di satu tempat.
</Card>

</CardGroup>

<h2 id="automation-workflows">Otomatisasi &amp; Alur Kerja</h2>

<p className="showcase-section-intro">
  Penjadwalan, kontrol browser, loop dukungan, dan sisi produk yang berbunyi “kerjakan saja tugasnya untuk saya”.
</p>

<CardGroup cols={2}>

<Card title="Kontrol Pembersih Udara Winix" icon="wind" href="https://x.com/antonplex/status/2010518442471006253">
  **@antonplex** • `automation` `hardware` `air-quality`

Claude Code menemukan dan mengonfirmasi kontrol pembersih udara, lalu OpenClaw mengambil alih untuk mengelola kualitas udara ruangan.

  <img src="/assets/showcase/winix-air-purifier.jpg" alt="Kontrol pembersih udara Winix melalui OpenClaw" />
</Card>

<Card title="Jepretan Kamera Langit Indah" icon="camera" href="https://x.com/signalgaining/status/2010523120604746151">
  **@signalgaining** • `automation` `camera` `skill` `images`

Dipicu oleh kamera atap: minta OpenClaw mengambil foto langit setiap kali terlihat indah — ia merancang skill dan mengambil fotonya.

  <img src="/assets/showcase/roof-camera-sky.jpg" alt="Jepretan langit dari kamera atap yang diambil oleh OpenClaw" />
</Card>

<Card title="Adegan Briefing Pagi Visual" icon="robot" href="https://x.com/buddyhadry/status/2010005331925954739">
  **@buddyhadry** • `automation` `briefing` `images` `telegram`

Prompt terjadwal menghasilkan satu gambar "adegan" setiap pagi (cuaca, tugas, tanggal, postingan/kutipan favorit) melalui persona OpenClaw.
</Card>

<Card title="Pemesanan Lapangan Padel" icon="calendar-check" href="https://github.com/joshp123/padel-cli">
  **@joshp123** • `automation` `booking` `cli`
  
  Pemeriksa ketersediaan Playtomic + CLI pemesanan. Jangan pernah melewatkan lapangan kosong lagi.
  
  <img src="/assets/showcase/padel-screenshot.jpg" alt="Tangkapan layar padel-cli" />
</Card>

<Card title="Pemasukan Akuntansi" icon="file-invoice-dollar">
  **Komunitas** • `automation` `email` `pdf`
  
  Mengumpulkan PDF dari email, menyiapkan dokumen untuk konsultan pajak. Akuntansi bulanan berjalan otomatis.
</Card>

<Card title="Mode Dev Sofa Nyaman" icon="couch" href="https://davekiss.com">
  **@davekiss** • `telegram` `website` `migration` `astro`

Dibangun ulang seluruh situs pribadi melalui Telegram sambil menonton Netflix — Notion → Astro, 18 postingan dimigrasikan, DNS ke Cloudflare. Tidak pernah membuka laptop.
</Card>

<Card title="Agen Pencarian Kerja" icon="briefcase">
  **@attol8** • `automation` `api` `skill`

Mencari lowongan kerja, mencocokkan dengan kata kunci di CV, dan mengembalikan peluang yang relevan beserta tautannya. Dibangun dalam 30 menit menggunakan API JSearch.
</Card>

<Card title="Pembuat Skill Jira" icon="diagram-project" href="https://x.com/jdrhyne/status/2008336434827002232">
  **@jdrhyne** • `automation` `jira` `skill` `devtools`

OpenClaw terhubung ke Jira, lalu menghasilkan skill baru secara langsung (sebelum tersedia di ClawHub).
</Card>

<Card title="Skill Todoist melalui Telegram" icon="list-check" href="https://x.com/iamsubhrajyoti/status/2009949389884920153">
  **@iamsubhrajyoti** • `automation` `todoist` `skill` `telegram`

Mengotomatiskan tugas Todoist dan membuat OpenClaw menghasilkan skill langsung di chat Telegram.
</Card>

<Card title="Analisis TradingView" icon="chart-line">
  **@bheem1798** • `finance` `browser` `automation`

Masuk ke TradingView melalui otomatisasi browser, mengambil tangkapan layar grafik, dan melakukan analisis teknikal sesuai permintaan. Tidak perlu API—cukup kontrol browser.
</Card>

<Card title="Dukungan Otomatis Slack" icon="slack">
  **@henrymascot** • `slack` `automation` `support`

Memantau channel Slack perusahaan, merespons dengan membantu, dan meneruskan notifikasi ke Telegram. Secara otonom memperbaiki bug produksi di aplikasi yang sudah dideploy tanpa diminta.
</Card>

</CardGroup>

<h2 id="knowledge-memory">Pengetahuan &amp; Memori</h2>

<p className="showcase-section-intro">
  Sistem yang mengindeks, mencari, mengingat, dan bernalar atas pengetahuan pribadi atau tim.
</p>

<CardGroup cols={2}>

<Card title="Pembelajaran Bahasa Mandarin xuezh" icon="language" href="https://github.com/joshp123/xuezh">
  **@joshp123** • `learning` `voice` `skill`
  
  Mesin pembelajaran bahasa Mandarin dengan umpan balik pengucapan dan alur belajar melalui OpenClaw.
  
  <img src="/assets/showcase/xuezh-pronunciation.jpeg" alt="umpan balik pengucapan xuezh" />
</Card>

<Card title="Brankas Memori WhatsApp" icon="vault">
  **Komunitas** • `memory` `transcription` `indexing`
  
  Mengimpor ekspor WhatsApp lengkap, mentranskripsikan 1k+ catatan suara, memeriksa silang dengan log git, dan menghasilkan laporan markdown bertaut.
</Card>

<Card title="Pencarian Semantik Karakeep" icon="magnifying-glass" href="https://github.com/jamesbrooksco/karakeep-semantic-search">
  **@jamesbrooksco** • `search` `vector` `bookmarks`
  
  Menambahkan pencarian vektor ke bookmark Karakeep menggunakan embedding Qdrant + OpenAI/Ollama.
</Card>

<Card title="Memori Inside-Out-2" icon="brain">
  **Komunitas** • `memory` `beliefs` `self-model`
  
  Pengelola memori terpisah yang mengubah file sesi menjadi memori → keyakinan → model diri yang terus berkembang.
</Card>

</CardGroup>

<h2 id="voice-phone">Suara &amp; Telepon</h2>

<p className="showcase-section-intro">
  Titik masuk yang mengutamakan suara, bridge telepon, dan alur kerja berat transkripsi.
</p>

<CardGroup cols={2}>

<Card title="Bridge Telepon Clawdia" icon="phone" href="https://github.com/alejandroOPI/clawdia-bridge">
  **@alejandroOPI** • `voice` `vapi` `bridge`
  
  Bridge HTTP Vapi voice assistant ↔ OpenClaw. Panggilan telepon hampir real-time dengan agen Anda.
</Card>

<Card title="Transkripsi OpenRouter" icon="microphone" href="https://clawhub.ai/obviyus/openrouter-transcribe">
  **@obviyus** • `transcription` `multilingual` `skill`

Transkripsi audio multibahasa melalui OpenRouter (Gemini, dll.). Tersedia di ClawHub.
</Card>

</CardGroup>

<h2 id="infrastructure-deployment">Infrastruktur &amp; Deployment</h2>

<p className="showcase-section-intro">
  Packaging, deployment, dan integrasi yang membuat OpenClaw lebih mudah dijalankan dan diperluas.
</p>

<CardGroup cols={2}>

<Card title="Add-on Home Assistant" icon="home" href="https://github.com/ngutman/openclaw-ha-addon">
  **@ngutman** • `homeassistant` `docker` `raspberry-pi`
  
  Gateway OpenClaw yang berjalan di Home Assistant OS dengan dukungan SSH tunnel dan status persisten.
</Card>

<Card title="Skill Home Assistant" icon="toggle-on" href="https://clawhub.ai/skills/homeassistant">
  **ClawHub** • `homeassistant` `skill` `automation`
  
  Mengontrol dan mengotomatiskan perangkat Home Assistant melalui bahasa alami.
</Card>

<Card title="Packaging Nix" icon="snowflake" href="https://github.com/openclaw/nix-openclaw">
  **@openclaw** • `nix` `packaging` `deployment`
  
  Konfigurasi OpenClaw yang dinixifikasi dengan fitur lengkap untuk deployment yang dapat direproduksi.
</Card>

<Card title="Kalender CalDAV" icon="calendar" href="https://clawhub.ai/skills/caldav-calendar">
  **ClawHub** • `calendar` `caldav` `skill`
  
  Skill kalender menggunakan khal/vdirsyncer. Integrasi kalender self-hosted.
</Card>

</CardGroup>

<h2 id="home-hardware">Rumah &amp; Perangkat Keras</h2>

<p className="showcase-section-intro">
  Sisi dunia fisik OpenClaw: rumah, sensor, kamera, penyedot debu, dan perangkat lainnya.
</p>

<CardGroup cols={2}>

<Card title="Otomatisasi GoHome" icon="house-signal" href="https://github.com/joshp123/gohome">
  **@joshp123** • `home` `nix` `grafana`
  
  Otomatisasi rumah native-Nix dengan OpenClaw sebagai antarmuka, ditambah dashboard Grafana yang indah.
  
  <img src="/assets/showcase/gohome-grafana.png" alt="dashboard Grafana GoHome" />
</Card>

<Card title="Penyedot Debu Roborock" icon="robot" href="https://github.com/joshp123/gohome/tree/main/plugins/roborock">
  **@joshp123** • `vacuum` `iot` `plugin`
  
  Kontrol robot penyedot debu Roborock Anda melalui percakapan alami.
  
  <img src="/assets/showcase/roborock-screenshot.jpg" alt="status Roborock" />
</Card>

</CardGroup>

<h2 id="community-projects">Proyek Komunitas</h2>

<p className="showcase-section-intro">
  Hal-hal yang berkembang melampaui satu alur kerja menjadi produk atau ekosistem yang lebih luas.
</p>

<CardGroup cols={2}>

<Card title="Marketplace StarSwap" icon="star" href="https://star-swap.com/">
  **Komunitas** • `marketplace` `astronomy` `webapp`
  
  Marketplace perlengkapan astronomi lengkap. Dibangun dengan/di sekitar ekosistem OpenClaw.
</Card>

</CardGroup>

---

<h2 id="submit-your-project">Kirim Proyek Anda</h2>

<p className="showcase-section-intro">
  Jika Anda sedang membangun sesuatu yang menarik dengan OpenClaw, kirimkan. Tangkapan layar yang kuat dan hasil yang konkret sangat membantu.
</p>

Punya sesuatu untuk dibagikan? Kami ingin sekali menampilkannya!

<Steps>
  <Step title="Bagikan">
    Posting di [#self-promotion on Discord](https://discord.gg/clawd) atau [tweet @openclaw](https://x.com/openclaw)
  </Step>
  <Step title="Sertakan Detail">
    Beri tahu kami apa fungsinya, tautkan repo/demo, bagikan tangkapan layar jika ada
  </Step>
  <Step title="Tampilkan">
    Kami akan menambahkan proyek-proyek unggulan ke halaman ini
  </Step>
</Steps>
