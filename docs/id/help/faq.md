---
read_when:
    - Menjawab pertanyaan dukungan umum tentang penyiapan, instalasi, onboarding, atau runtime
    - Menyaring masalah yang dilaporkan pengguna sebelum debugging lebih mendalam
summary: Pertanyaan yang sering diajukan tentang penyiapan, konfigurasi, dan penggunaan OpenClaw
title: Tanya Jawab Umum
x-i18n:
    generated_at: "2026-04-12T23:28:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# Tanya Jawab Umum

Jawaban cepat plus pemecahan masalah yang lebih mendalam untuk penyiapan dunia nyata (dev lokal, VPS, multi-agent, OAuth/kunci API, failover model). Untuk diagnostik runtime, lihat [Pemecahan Masalah](/id/gateway/troubleshooting). Untuk referensi config lengkap, lihat [Konfigurasi](/id/gateway/configuration).

## 60 detik pertama jika ada yang rusak

1. **Status cepat (pemeriksaan pertama)**

   ```bash
   openclaw status
   ```

   Ringkasan lokal cepat: OS + pembaruan, keterjangkauan gateway/service, agen/sesi, config penyedia + masalah runtime (saat gateway dapat dijangkau).

2. **Laporan yang aman untuk dibagikan**

   ```bash
   openclaw status --all
   ```

   Diagnosis hanya-baca dengan ekor log (token disamarkan).

3. **Status daemon + port**

   ```bash
   openclaw gateway status
   ```

   Menampilkan runtime supervisor vs keterjangkauan RPC, URL target probe, dan config mana yang kemungkinan digunakan service.

4. **Probe mendalam**

   ```bash
   openclaw status --deep
   ```

   Menjalankan probe kesehatan gateway langsung, termasuk probe channel saat didukung
   (memerlukan gateway yang dapat dijangkau). Lihat [Health](/id/gateway/health).

5. **Ikuti log terbaru**

   ```bash
   openclaw logs --follow
   ```

   Jika RPC tidak aktif, gunakan fallback ke:

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Log file terpisah dari log service; lihat [Logging](/id/logging) dan [Pemecahan Masalah](/id/gateway/troubleshooting).

6. **Jalankan doctor (perbaikan)**

   ```bash
   openclaw doctor
   ```

   Memperbaiki/memigrasikan config/state + menjalankan pemeriksaan kesehatan. Lihat [Doctor](/id/gateway/doctor).

7. **Snapshot Gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # menampilkan URL target + path config saat terjadi error
   ```

   Meminta snapshot lengkap dari gateway yang sedang berjalan (khusus WS). Lihat [Health](/id/gateway/health).

## Mulai cepat dan penyiapan saat pertama kali dijalankan

<AccordionGroup>
  <Accordion title="Saya buntu, cara tercepat agar tidak buntu lagi">
    Gunakan agen AI lokal yang dapat **melihat mesin Anda**. Itu jauh lebih efektif daripada bertanya
    di Discord, karena kebanyakan kasus "saya buntu" adalah **masalah config atau lingkungan lokal** yang
    tidak dapat diperiksa oleh pembantu jarak jauh.

    - **Claude Code**: [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex**: [https://openai.com/codex/](https://openai.com/codex/)

    Alat-alat ini dapat membaca repo, menjalankan perintah, memeriksa log, dan membantu memperbaiki
    penyiapan tingkat mesin Anda (PATH, service, izin, file auth). Berikan **checkout source lengkap**
    melalui instalasi hackable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Ini menginstal OpenClaw **dari checkout git**, sehingga agen dapat membaca kode + docs dan
    menalar versi persis yang Anda jalankan. Anda selalu dapat beralih kembali ke stable nanti
    dengan menjalankan ulang installer tanpa `--install-method git`.

    Tip: minta agen untuk **merencanakan dan mengawasi** perbaikannya (langkah demi langkah), lalu jalankan hanya
    perintah yang diperlukan. Itu menjaga perubahan tetap kecil dan lebih mudah diaudit.

    Jika Anda menemukan bug atau perbaikan nyata, silakan buat issue GitHub atau kirim PR:
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Mulailah dengan perintah-perintah ini (bagikan output saat meminta bantuan):

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Fungsinya:

    - `openclaw status`: snapshot cepat kesehatan gateway/agen + config dasar.
    - `openclaw models status`: memeriksa auth penyedia + ketersediaan model.
    - `openclaw doctor`: memvalidasi dan memperbaiki masalah config/state umum.

    Pemeriksaan CLI berguna lainnya: `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Loop debug cepat: [60 detik pertama jika ada yang rusak](#first-60-seconds-if-something-is-broken).
    Docs instalasi: [Install](/id/install), [Flag installer](/id/install/installer), [Updating](/id/install/updating).

  </Accordion>

  <Accordion title="Heartbeat terus dilewati. Apa arti alasan dilewati itu?">
    Alasan umum Heartbeat dilewati:

    - `quiet-hours`: di luar jendela active-hours yang dikonfigurasi
    - `empty-heartbeat-file`: `HEARTBEAT.md` ada tetapi hanya berisi kerangka kosong/header saja
    - `no-tasks-due`: mode tugas `HEARTBEAT.md` aktif tetapi belum ada interval tugas yang jatuh tempo
    - `alerts-disabled`: semua visibilitas heartbeat dinonaktifkan (`showOk`, `showAlerts`, dan `useIndicator` semuanya mati)

    Dalam mode tugas, stempel waktu jatuh tempo hanya dimajukan setelah proses heartbeat nyata
    selesai. Proses yang dilewati tidak menandai tugas sebagai selesai.

    Docs: [Heartbeat](/id/gateway/heartbeat), [Automation & Tasks](/id/automation).

  </Accordion>

  <Accordion title="Cara yang direkomendasikan untuk menginstal dan menyiapkan OpenClaw">
    Repo merekomendasikan menjalankan dari source dan menggunakan onboarding:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    Wizard juga dapat membangun aset UI secara otomatis. Setelah onboarding, Anda biasanya menjalankan Gateway di port **18789**.

    Dari source (kontributor/dev):

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # otomatis menginstal dependensi UI saat pertama kali dijalankan
    openclaw onboard
    ```

    Jika Anda belum memiliki instalasi global, jalankan melalui `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Bagaimana cara membuka dasbor setelah onboarding?">
    Wizard membuka browser Anda dengan URL dasbor yang bersih (tanpa token) tepat setelah onboarding dan juga mencetak tautannya dalam ringkasan. Biarkan tab itu tetap terbuka; jika tidak terbuka otomatis, salin/tempel URL yang dicetak pada mesin yang sama.
  </Accordion>

  <Accordion title="Bagaimana cara mengautentikasi dasbor di localhost vs remote?">
    **Localhost (mesin yang sama):**

    - Buka `http://127.0.0.1:18789/`.
    - Jika meminta auth shared-secret, tempel token atau kata sandi yang dikonfigurasi ke pengaturan Control UI.
    - Sumber token: `gateway.auth.token` (atau `OPENCLAW_GATEWAY_TOKEN`).
    - Sumber kata sandi: `gateway.auth.password` (atau `OPENCLAW_GATEWAY_PASSWORD`).
    - Jika belum ada shared secret yang dikonfigurasi, buat token dengan `openclaw doctor --generate-gateway-token`.

    **Bukan di localhost:**

    - **Tailscale Serve** (disarankan): tetap gunakan bind loopback, jalankan `openclaw gateway --tailscale serve`, buka `https://<magicdns>/`. Jika `gateway.auth.allowTailscale` bernilai `true`, header identitas memenuhi auth Control UI/WebSocket (tanpa menempelkan shared secret, dengan asumsi host gateway tepercaya); API HTTP tetap memerlukan auth shared-secret kecuali Anda sengaja menggunakan private-ingress `none` atau auth HTTP trusted-proxy.
      Upaya auth Serve serentak yang buruk dari klien yang sama diserialkan sebelum pembatas auth gagal mencatatnya, jadi percobaan ulang buruk kedua sudah bisa menampilkan `retry later`.
    - **Bind tailnet**: jalankan `openclaw gateway --bind tailnet --token "<token>"` (atau konfigurasikan auth kata sandi), buka `http://<tailscale-ip>:18789/`, lalu tempel shared secret yang sesuai di pengaturan dasbor.
    - **Reverse proxy berbasis identitas**: biarkan Gateway berada di belakang trusted proxy non-loopback, konfigurasikan `gateway.auth.mode: "trusted-proxy"`, lalu buka URL proxy.
    - **Tunnel SSH**: `ssh -N -L 18789:127.0.0.1:18789 user@host` lalu buka `http://127.0.0.1:18789/`. Auth shared-secret tetap berlaku melalui tunnel; tempel token atau kata sandi yang dikonfigurasi jika diminta.

    Lihat [Dashboard](/web/dashboard) dan [Permukaan web](/web) untuk mode bind dan detail auth.

  </Accordion>

  <Accordion title="Mengapa ada dua config persetujuan exec untuk persetujuan chat?">
    Keduanya mengendalikan lapisan yang berbeda:

    - `approvals.exec`: meneruskan prompt persetujuan ke tujuan chat
    - `channels.<channel>.execApprovals`: membuat channel itu bertindak sebagai klien persetujuan native untuk persetujuan exec

    Kebijakan exec host tetap merupakan gerbang persetujuan yang sebenarnya. Config chat hanya mengendalikan ke mana
    prompt persetujuan muncul dan bagaimana orang dapat menjawabnya.

    Dalam kebanyakan penyiapan, Anda **tidak** memerlukan keduanya:

    - Jika chat sudah mendukung perintah dan balasan, `/approve` pada chat yang sama bekerja melalui jalur bersama.
    - Jika channel native yang didukung dapat menyimpulkan approver dengan aman, OpenClaw kini otomatis mengaktifkan persetujuan native DM-first saat `channels.<channel>.execApprovals.enabled` tidak disetel atau bernilai `"auto"`.
    - Saat kartu/tombol persetujuan native tersedia, UI native itu adalah jalur utama; agen hanya boleh menyertakan perintah manual `/approve` jika hasil tool menyatakan persetujuan chat tidak tersedia atau persetujuan manual adalah satu-satunya jalur.
    - Gunakan `approvals.exec` hanya jika prompt juga harus diteruskan ke chat lain atau ruang ops eksplisit.
    - Gunakan `channels.<channel>.execApprovals.target: "channel"` atau `"both"` hanya jika Anda secara eksplisit ingin prompt persetujuan diposting kembali ke room/topic asal.
    - Persetujuan Plugin terpisah lagi: default-nya menggunakan `/approve` pada chat yang sama, penerusan `approvals.plugin` opsional, dan hanya beberapa channel native yang tetap menambahkan penanganan native persetujuan Plugin di atasnya.

    Versi singkat: penerusan adalah untuk routing, config klien native adalah untuk UX spesifik channel yang lebih kaya.
    Lihat [Persetujuan Exec](/id/tools/exec-approvals).

  </Accordion>

  <Accordion title="Runtime apa yang saya perlukan?">
    Node **>= 22** diperlukan. `pnpm` direkomendasikan. Bun **tidak direkomendasikan** untuk Gateway.
  </Accordion>

  <Accordion title="Apakah ini berjalan di Raspberry Pi?">
    Ya. Gateway ringan - docs mencantumkan **512MB-1GB RAM**, **1 core**, dan sekitar **500MB**
    disk sebagai cukup untuk penggunaan pribadi, dan mencatat bahwa **Raspberry Pi 4 dapat menjalankannya**.

    Jika Anda ingin ruang tambahan (log, media, service lain), **2GB direkomendasikan**, tetapi itu
    bukan minimum yang keras.

    Tip: Pi/VPS kecil dapat meng-host Gateway, dan Anda dapat memasangkan **Node** pada laptop/ponsel Anda untuk
    layar/kamera/canvas lokal atau eksekusi perintah. Lihat [Nodes](/id/nodes).

  </Accordion>

  <Accordion title="Ada tips untuk instalasi Raspberry Pi?">
    Versi singkat: ini berjalan, tetapi bersiaplah menghadapi beberapa kendala.

    - Gunakan OS **64-bit** dan pertahankan Node >= 22.
    - Pilih **instalasi hackable (git)** agar Anda dapat melihat log dan memperbarui dengan cepat.
    - Mulailah tanpa channel/Skills, lalu tambahkan satu per satu.
    - Jika Anda mengalami masalah biner yang aneh, biasanya itu masalah **kompatibilitas ARM**.

    Docs: [Linux](/id/platforms/linux), [Install](/id/install).

  </Accordion>

  <Accordion title="Ini macet di wake up my friend / onboarding tidak mau hatch. Sekarang apa?">
    Layar itu bergantung pada Gateway yang dapat dijangkau dan terautentikasi. TUI juga mengirim
    "Wake up, my friend!" secara otomatis saat hatch pertama. Jika Anda melihat baris itu dengan **tanpa balasan**
    dan token tetap 0, agen tidak pernah berjalan.

    1. Mulai ulang Gateway:

    ```bash
    openclaw gateway restart
    ```

    2. Periksa status + auth:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Jika masih macet, jalankan:

    ```bash
    openclaw doctor
    ```

    Jika Gateway berada di remote, pastikan koneksi tunnel/Tailscale aktif dan UI
    diarahkan ke Gateway yang benar. Lihat [Akses jarak jauh](/id/gateway/remote).

  </Accordion>

  <Accordion title="Bisakah saya memigrasikan penyiapan saya ke mesin baru (Mac mini) tanpa mengulang onboarding?">
    Ya. Salin **direktori state** dan **workspace**, lalu jalankan Doctor sekali. Ini
    menjaga bot Anda "tetap persis sama" (memori, riwayat sesi, auth, dan
    state channel) selama Anda menyalin **kedua** lokasi:

    1. Instal OpenClaw di mesin baru.
    2. Salin `$OPENCLAW_STATE_DIR` (default: `~/.openclaw`) dari mesin lama.
    3. Salin workspace Anda (default: `~/.openclaw/workspace`).
    4. Jalankan `openclaw doctor` dan mulai ulang service Gateway.

    Itu mempertahankan config, profil auth, kredensial WhatsApp, sesi, dan memori. Jika Anda berada dalam
    mode remote, ingat bahwa host gateway memiliki penyimpanan sesi dan workspace.

    **Penting:** jika Anda hanya commit/push workspace Anda ke GitHub, Anda sedang mencadangkan
    **memori + file bootstrap**, tetapi **bukan** riwayat sesi atau auth. Data tersebut berada
    di bawah `~/.openclaw/` (misalnya `~/.openclaw/agents/<agentId>/sessions/`).

    Terkait: [Migrasi](/id/install/migrating), [Lokasi penyimpanan di disk](#where-things-live-on-disk),
    [Workspace agen](/id/concepts/agent-workspace), [Doctor](/id/gateway/doctor),
    [Mode remote](/id/gateway/remote).

  </Accordion>

  <Accordion title="Di mana saya bisa melihat apa yang baru di versi terbaru?">
    Periksa changelog GitHub:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Entri terbaru berada di bagian atas. Jika bagian teratas diberi tanda **Unreleased**, bagian bertanggal berikutnya
    adalah versi terbaru yang sudah dirilis. Entri dikelompokkan berdasarkan **Sorotan**, **Perubahan**, dan
    **Perbaikan** (ditambah bagian docs/lainnya bila diperlukan).

  </Accordion>

  <Accordion title="Tidak dapat mengakses docs.openclaw.ai (error SSL)">
    Beberapa koneksi Comcast/Xfinity secara keliru memblokir `docs.openclaw.ai` melalui Xfinity
    Advanced Security. Nonaktifkan fitur tersebut atau tambahkan `docs.openclaw.ai` ke allowlist, lalu coba lagi.
    Tolong bantu kami membuka blokirnya dengan melaporkannya di sini: [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Jika Anda tetap tidak bisa mengakses situs tersebut, docs dicerminkan di GitHub:
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Perbedaan antara stable dan beta">
    **Stable** dan **beta** adalah **npm dist-tag**, bukan jalur kode yang terpisah:

    - `latest` = stable
    - `beta` = build awal untuk pengujian

    Biasanya, rilis stable masuk ke **beta** terlebih dahulu, lalu langkah promosi
    eksplisit memindahkan versi yang sama itu ke `latest`. Maintainer juga dapat
    memublikasikan langsung ke `latest` bila diperlukan. Itulah sebabnya beta dan stable dapat
    menunjuk ke **versi yang sama** setelah promosi.

    Lihat apa yang berubah:
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Untuk one-liner instalasi dan perbedaan antara beta dan dev, lihat accordion di bawah.

  </Accordion>

  <Accordion title="Bagaimana cara menginstal versi beta dan apa perbedaan antara beta dan dev?">
    **Beta** adalah npm dist-tag `beta` (dapat sama dengan `latest` setelah promosi).
    **Dev** adalah head bergerak dari `main` (git); saat dipublikasikan, ia menggunakan npm dist-tag `dev`.

    One-liner (macOS/Linux):

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Installer Windows (PowerShell):
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Detail lebih lanjut: [Saluran pengembangan](/id/install/development-channels) dan [Flag installer](/id/install/installer).

  </Accordion>

  <Accordion title="Bagaimana cara mencoba versi terbaru?">
    Ada dua opsi:

    1. **Saluran dev (checkout git):**

    ```bash
    openclaw update --channel dev
    ```

    Ini akan beralih ke branch `main` dan memperbarui dari source.

    2. **Instalasi hackable (dari situs installer):**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Itu memberi Anda repo lokal yang bisa Anda edit, lalu perbarui melalui git.

    Jika Anda lebih suka clone bersih secara manual, gunakan:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Docs: [Update](/cli/update), [Saluran pengembangan](/id/install/development-channels),
    [Install](/id/install).

  </Accordion>

  <Accordion title="Berapa lama instalasi dan onboarding biasanya berlangsung?">
    Perkiraan kasar:

    - **Instalasi:** 2-5 menit
    - **Onboarding:** 5-15 menit tergantung berapa banyak channel/model yang Anda konfigurasi

    Jika macet, gunakan [Installer macet](#quick-start-and-first-run-setup)
    dan loop debug cepat di [Saya buntu](#quick-start-and-first-run-setup).

  </Accordion>

  <Accordion title="Installer macet? Bagaimana cara mendapatkan umpan balik yang lebih banyak?">
    Jalankan ulang installer dengan **output verbose**:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Instalasi beta dengan verbose:

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Untuk instalasi hackable (git):

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Ekuivalen Windows (PowerShell):

    ```powershell
    # install.ps1 belum memiliki flag -Verbose khusus.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Opsi lainnya: [Flag installer](/id/install/installer).

  </Accordion>

  <Accordion title="Instalasi Windows mengatakan git tidak ditemukan atau openclaw tidak dikenali">
    Dua masalah umum di Windows:

    **1) npm error spawn git / git tidak ditemukan**

    - Instal **Git for Windows** dan pastikan `git` ada di PATH Anda.
    - Tutup dan buka kembali PowerShell, lalu jalankan ulang installer.

    **2) openclaw tidak dikenali setelah instalasi**

    - Folder bin global npm Anda tidak ada di PATH.
    - Periksa path-nya:

      ```powershell
      npm config get prefix
      ```

    - Tambahkan direktori tersebut ke PATH pengguna Anda (tidak perlu akhiran `\bin` di Windows; pada kebanyakan sistem itu adalah `%AppData%\npm`).
    - Tutup dan buka kembali PowerShell setelah memperbarui PATH.

    Jika Anda menginginkan penyiapan Windows yang paling lancar, gunakan **WSL2** alih-alih Windows native.
    Docs: [Windows](/id/platforms/windows).

  </Accordion>

  <Accordion title="Output exec Windows menampilkan teks Mandarin yang rusak - apa yang harus saya lakukan?">
    Ini biasanya merupakan ketidakcocokan code page konsol pada shell Windows native.

    Gejala:

    - Output `system.run`/`exec` menampilkan bahasa Mandarin sebagai mojibake
    - Perintah yang sama terlihat baik-baik saja di profil terminal lain

    Solusi cepat di PowerShell:

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Lalu mulai ulang Gateway dan coba lagi perintah Anda:

    ```powershell
    openclaw gateway restart
    ```

    Jika Anda masih dapat mereproduksi ini di OpenClaw terbaru, lacak/laporkan di:

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="Docs tidak menjawab pertanyaan saya - bagaimana cara mendapatkan jawaban yang lebih baik?">
    Gunakan **instalasi hackable (git)** agar Anda memiliki source dan docs lengkap secara lokal, lalu tanyakan
    kepada bot Anda (atau Claude/Codex) _dari folder itu_ sehingga ia dapat membaca repo dan menjawab dengan tepat.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Detail lebih lanjut: [Install](/id/install) dan [Flag installer](/id/install/installer).

  </Accordion>

  <Accordion title="Bagaimana cara menginstal OpenClaw di Linux?">
    Jawaban singkat: ikuti panduan Linux, lalu jalankan onboarding.

    - Jalur cepat Linux + instalasi service: [Linux](/id/platforms/linux).
    - Panduan lengkap: [Memulai](/id/start/getting-started).
    - Installer + pembaruan: [Instalasi & pembaruan](/id/install/updating).

  </Accordion>

  <Accordion title="Bagaimana cara menginstal OpenClaw di VPS?">
    VPS Linux apa pun bisa digunakan. Instal di server, lalu gunakan SSH/Tailscale untuk mengakses Gateway.

    Panduan: [exe.dev](/id/install/exe-dev), [Hetzner](/id/install/hetzner), [Fly.io](/id/install/fly).
    Akses jarak jauh: [Gateway remote](/id/gateway/remote).

  </Accordion>

  <Accordion title="Di mana panduan instalasi cloud/VPS?">
    Kami menyediakan **pusat hosting** dengan penyedia umum. Pilih salah satu dan ikuti panduannya:

    - [Hosting VPS](/id/vps) (semua penyedia di satu tempat)
    - [Fly.io](/id/install/fly)
    - [Hetzner](/id/install/hetzner)
    - [exe.dev](/id/install/exe-dev)

    Cara kerjanya di cloud: **Gateway berjalan di server**, dan Anda mengaksesnya
    dari laptop/ponsel melalui Control UI (atau Tailscale/SSH). State + workspace Anda
    berada di server, jadi perlakukan host tersebut sebagai sumber kebenaran dan buat cadangannya.

    Anda dapat memasangkan **Node** (Mac/iOS/Android/headless) ke Gateway cloud tersebut untuk mengakses
    layar/kamera/canvas lokal atau menjalankan perintah di laptop Anda sambil tetap mempertahankan
    Gateway di cloud.

    Pusat: [Platforms](/id/platforms). Akses jarak jauh: [Gateway remote](/id/gateway/remote).
    Nodes: [Nodes](/id/nodes), [CLI Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Bisakah saya meminta OpenClaw memperbarui dirinya sendiri?">
    Jawaban singkat: **bisa, tetapi tidak disarankan**. Alur pembaruan dapat memulai ulang
    Gateway (yang memutus sesi aktif), mungkin memerlukan checkout git yang bersih, dan
    dapat meminta konfirmasi. Lebih aman: jalankan pembaruan dari shell sebagai operator.

    Gunakan CLI:

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Jika Anda harus mengotomatiskannya dari agen:

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Docs: [Update](/cli/update), [Updating](/id/install/updating).

  </Accordion>

  <Accordion title="Sebenarnya onboarding melakukan apa?">
    `openclaw onboard` adalah jalur penyiapan yang direkomendasikan. Dalam **mode lokal** ia memandu Anda melalui:

    - **Penyiapan model/auth** (OAuth penyedia, kunci API, setup-token Anthropic, ditambah opsi model lokal seperti LM Studio)
    - Lokasi **workspace** + file bootstrap
    - **Pengaturan Gateway** (bind/port/auth/tailscale)
    - **Channels** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, ditambah Plugin channel bawaan seperti QQ Bot)
    - **Instalasi daemon** (LaunchAgent di macOS; unit pengguna systemd di Linux/WSL2)
    - **Pemeriksaan kesehatan** dan pemilihan **Skills**

    Fitur ini juga memberi peringatan jika model yang Anda konfigurasi tidak dikenal atau auth-nya tidak ada.

  </Accordion>

  <Accordion title="Apakah saya perlu langganan Claude atau OpenAI untuk menjalankan ini?">
    Tidak. Anda dapat menjalankan OpenClaw dengan **kunci API** (Anthropic/OpenAI/lainnya) atau dengan
    **model lokal saja** sehingga data Anda tetap berada di perangkat Anda. Langganan (Claude
    Pro/Max atau OpenAI Codex) adalah cara opsional untuk mengautentikasi penyedia tersebut.

    Untuk Anthropic di OpenClaw, pembagian praktisnya adalah:

    - **Kunci API Anthropic**: penagihan API Anthropic normal
    - **Claude CLI / auth langganan Claude di OpenClaw**: staf Anthropic
      memberi tahu kami bahwa penggunaan ini diizinkan kembali, dan OpenClaw memperlakukan penggunaan `claude -p`
      sebagai penggunaan yang disetujui untuk integrasi ini kecuali Anthropic menerbitkan kebijakan
      baru

    Untuk host gateway yang berjalan lama, kunci API Anthropic tetap merupakan penyiapan yang
    lebih dapat diprediksi. OAuth OpenAI Codex didukung secara eksplisit untuk
    tool eksternal seperti OpenClaw.

    OpenClaw juga mendukung opsi bergaya langganan hosted lainnya termasuk
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan**, dan
    **Z.AI / GLM Coding Plan**.

    Docs: [Anthropic](/id/providers/anthropic), [OpenAI](/id/providers/openai),
    [Qwen Cloud](/id/providers/qwen),
    [MiniMax](/id/providers/minimax), [GLM Models](/id/providers/glm),
    [Model lokal](/id/gateway/local-models), [Models](/id/concepts/models).

  </Accordion>

  <Accordion title="Bisakah saya menggunakan langganan Claude Max tanpa kunci API?">
    Ya.

    Staf Anthropic memberi tahu kami bahwa penggunaan Claude CLI ala OpenClaw diizinkan kembali, jadi
    OpenClaw memperlakukan auth langganan Claude dan penggunaan `claude -p` sebagai penggunaan yang disetujui
    untuk integrasi ini kecuali Anthropic menerbitkan kebijakan baru. Jika Anda menginginkan
    penyiapan sisi server yang paling dapat diprediksi, gunakan kunci API Anthropic sebagai gantinya.

  </Accordion>

  <Accordion title="Apakah Anda mendukung auth langganan Claude (Claude Pro atau Max)?">
    Ya.

    Staf Anthropic memberi tahu kami bahwa penggunaan ini diizinkan kembali, jadi OpenClaw memperlakukan
    penggunaan ulang Claude CLI dan penggunaan `claude -p` sebagai penggunaan yang disetujui untuk integrasi ini
    kecuali Anthropic menerbitkan kebijakan baru.

    Setup-token Anthropic masih tersedia sebagai jalur token OpenClaw yang didukung, tetapi OpenClaw kini lebih memilih penggunaan ulang Claude CLI dan `claude -p` saat tersedia.
    Untuk workload produksi atau multi-pengguna, auth kunci API Anthropic tetap merupakan
    pilihan yang lebih aman dan lebih dapat diprediksi. Jika Anda menginginkan opsi hosted bergaya langganan lain
    di OpenClaw, lihat [OpenAI](/id/providers/openai), [Qwen / Model
    Cloud](/id/providers/qwen), [MiniMax](/id/providers/minimax), dan [GLM
    Models](/id/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Mengapa saya melihat HTTP 429 rate_limit_error dari Anthropic?">
Itu berarti **kuota/batas laju Anthropic** Anda habis untuk jendela saat ini. Jika Anda
menggunakan **Claude CLI**, tunggu hingga jendela direset atau tingkatkan paket Anda. Jika Anda
menggunakan **kunci API Anthropic**, periksa Anthropic Console
untuk penggunaan/penagihan dan naikkan batas sesuai kebutuhan.

    Jika pesannya secara spesifik adalah:
    `Extra usage is required for long context requests`, permintaan tersebut mencoba menggunakan
    beta konteks 1M milik Anthropic (`context1m: true`). Itu hanya berfungsi ketika
    kredensial Anda memenuhi syarat untuk penagihan konteks panjang (penagihan kunci API atau
    jalur Claude-login OpenClaw dengan Extra Usage diaktifkan).

    Tip: tetapkan **model fallback** agar OpenClaw dapat terus membalas saat penyedia terkena pembatasan laju.
    Lihat [Models](/cli/models), [OAuth](/id/concepts/oauth), dan
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/id/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="Apakah AWS Bedrock didukung?">
    Ya. OpenClaw memiliki penyedia **Amazon Bedrock (Converse)** bawaan. Dengan penanda env AWS yang ada, OpenClaw dapat menemukan katalog Bedrock streaming/teks secara otomatis dan menggabungkannya sebagai penyedia implisit `amazon-bedrock`; jika tidak, Anda dapat secara eksplisit mengaktifkan `plugins.entries.amazon-bedrock.config.discovery.enabled` atau menambahkan entri penyedia manual. Lihat [Amazon Bedrock](/id/providers/bedrock) dan [Penyedia model](/id/providers/models). Jika Anda lebih memilih alur kunci terkelola, proxy kompatibel OpenAI di depan Bedrock tetap merupakan opsi yang valid.
  </Accordion>

  <Accordion title="Bagaimana cara kerja auth Codex?">
    OpenClaw mendukung **OpenAI Code (Codex)** melalui OAuth (masuk ChatGPT). Onboarding dapat menjalankan alur OAuth dan akan menetapkan model default ke `openai-codex/gpt-5.4` bila sesuai. Lihat [Penyedia model](/id/concepts/model-providers) dan [Onboarding (CLI)](/id/start/wizard).
  </Accordion>

  <Accordion title="Mengapa ChatGPT GPT-5.4 tidak membuka akses ke openai/gpt-5.4 di OpenClaw?">
    OpenClaw memperlakukan kedua jalur tersebut secara terpisah:

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = API Platform OpenAI langsung

    Di OpenClaw, masuk ChatGPT/Codex dihubungkan ke rute `openai-codex/*`,
    bukan ke rute `openai/*` langsung. Jika Anda menginginkan jalur API langsung di
    OpenClaw, tetapkan `OPENAI_API_KEY` (atau config penyedia OpenAI yang setara).
    Jika Anda menginginkan masuk ChatGPT/Codex di OpenClaw, gunakan `openai-codex/*`.

  </Accordion>

  <Accordion title="Mengapa batas OAuth Codex bisa berbeda dari web ChatGPT?">
    `openai-codex/*` menggunakan rute OAuth Codex, dan jendela kuota yang dapat digunakannya
    dikelola OpenAI dan bergantung pada paket. Dalam praktiknya, batas tersebut bisa berbeda dari
    pengalaman situs/aplikasi ChatGPT, bahkan ketika keduanya terhubung ke akun yang sama.

    OpenClaw dapat menampilkan jendela penggunaan/kuota penyedia yang saat ini terlihat di
    `openclaw models status`, tetapi tidak merekayasa atau menormalkan hak ChatGPT-web
    menjadi akses API langsung. Jika Anda menginginkan jalur penagihan/batas Platform OpenAI langsung,
    gunakan `openai/*` dengan kunci API.

  </Accordion>

  <Accordion title="Apakah Anda mendukung auth langganan OpenAI (OAuth Codex)?">
    Ya. OpenClaw sepenuhnya mendukung **OAuth langganan OpenAI Code (Codex)**.
    OpenAI secara eksplisit mengizinkan penggunaan OAuth langganan dalam tool/alur kerja eksternal
    seperti OpenClaw. Onboarding dapat menjalankan alur OAuth untuk Anda.

    Lihat [OAuth](/id/concepts/oauth), [Penyedia model](/id/concepts/model-providers), dan [Onboarding (CLI)](/id/start/wizard).

  </Accordion>

  <Accordion title="Bagaimana cara menyiapkan OAuth Gemini CLI?">
    Gemini CLI menggunakan **alur auth Plugin**, bukan client id atau secret di `openclaw.json`.

    Langkah-langkah:

    1. Instal Gemini CLI secara lokal agar `gemini` ada di `PATH`
       - Homebrew: `brew install gemini-cli`
       - npm: `npm install -g @google/gemini-cli`
    2. Aktifkan Plugin: `openclaw plugins enable google`
    3. Login: `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Model default setelah login: `google-gemini-cli/gemini-3-flash-preview`
    5. Jika permintaan gagal, tetapkan `GOOGLE_CLOUD_PROJECT` atau `GOOGLE_CLOUD_PROJECT_ID` pada host gateway

    Ini menyimpan token OAuth dalam profil auth pada host gateway. Detail: [Penyedia model](/id/concepts/model-providers).

  </Accordion>

  <Accordion title="Apakah model lokal cukup baik untuk chat santai?">
    Biasanya tidak. OpenClaw memerlukan konteks besar + keamanan yang kuat; kartu kecil mudah terpotong dan bocor. Jika terpaksa, jalankan build model **terbesar** yang bisa Anda jalankan secara lokal (LM Studio) dan lihat [/gateway/local-models](/id/gateway/local-models). Model yang lebih kecil/terkuantisasi meningkatkan risiko injeksi prompt - lihat [Security](/id/gateway/security).
  </Accordion>

  <Accordion title="Bagaimana cara menjaga lalu lintas model hosted tetap di wilayah tertentu?">
    Pilih endpoint yang dipatok ke wilayah. OpenRouter menyediakan opsi yang di-host di AS untuk MiniMax, Kimi, dan GLM; pilih varian yang di-host di AS untuk menjaga data tetap di wilayah tersebut. Anda tetap dapat mencantumkan Anthropic/OpenAI bersama ini dengan menggunakan `models.mode: "merge"` agar fallback tetap tersedia sambil tetap menghormati penyedia regional yang Anda pilih.
  </Accordion>

  <Accordion title="Apakah saya harus membeli Mac Mini untuk menginstal ini?">
    Tidak. OpenClaw berjalan di macOS atau Linux (Windows melalui WSL2). Mac mini bersifat opsional - beberapa orang
    membelinya sebagai host yang selalu aktif, tetapi VPS kecil, server rumahan, atau perangkat kelas Raspberry Pi juga bisa.

    Anda hanya memerlukan Mac **untuk tool khusus macOS**. Untuk iMessage, gunakan [BlueBubbles](/id/channels/bluebubbles) (disarankan) - server BlueBubbles berjalan di Mac apa pun, dan Gateway dapat berjalan di Linux atau di tempat lain. Jika Anda menginginkan tool khusus macOS lainnya, jalankan Gateway di Mac atau pasangkan Node macOS.

    Docs: [BlueBubbles](/id/channels/bluebubbles), [Nodes](/id/nodes), [Mode remote Mac](/id/platforms/mac/remote).

  </Accordion>

  <Accordion title="Apakah saya memerlukan Mac mini untuk dukungan iMessage?">
    Anda memerlukan **perangkat macOS** yang masuk ke Messages. Itu **tidak** harus Mac mini -
    Mac apa pun bisa. **Gunakan [BlueBubbles](/id/channels/bluebubbles)** (disarankan) untuk iMessage - server BlueBubbles berjalan di macOS, sedangkan Gateway dapat berjalan di Linux atau di tempat lain.

    Penyiapan umum:

    - Jalankan Gateway di Linux/VPS, dan jalankan server BlueBubbles di Mac apa pun yang masuk ke Messages.
    - Jalankan semuanya di Mac jika Anda menginginkan penyiapan satu mesin yang paling sederhana.

    Docs: [BlueBubbles](/id/channels/bluebubbles), [Nodes](/id/nodes),
    [Mode remote Mac](/id/platforms/mac/remote).

  </Accordion>

  <Accordion title="Jika saya membeli Mac mini untuk menjalankan OpenClaw, apakah saya bisa menghubungkannya ke MacBook Pro saya?">
    Ya. **Mac mini dapat menjalankan Gateway**, dan MacBook Pro Anda dapat terhubung sebagai
    **Node** (perangkat pendamping). Node tidak menjalankan Gateway - mereka menyediakan
    kemampuan tambahan seperti layar/kamera/canvas dan `system.run` pada perangkat tersebut.

    Pola umum:

    - Gateway di Mac mini (selalu aktif).
    - MacBook Pro menjalankan app macOS atau host node dan dipasangkan ke Gateway.
    - Gunakan `openclaw nodes status` / `openclaw nodes list` untuk melihatnya.

    Docs: [Nodes](/id/nodes), [CLI Nodes](/cli/nodes).

  </Accordion>

  <Accordion title="Bisakah saya menggunakan Bun?">
    Bun **tidak direkomendasikan**. Kami melihat bug runtime, terutama dengan WhatsApp dan Telegram.
    Gunakan **Node** untuk gateway yang stabil.

    Jika Anda tetap ingin bereksperimen dengan Bun, lakukan itu pada gateway non-produksi
    tanpa WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram: apa yang dimasukkan ke allowFrom?">
    `channels.telegram.allowFrom` adalah **ID pengguna Telegram milik manusia pengirim** (numerik). Itu bukan username bot.

    Onboarding menerima input `@username` dan menyelesaikannya menjadi ID numerik, tetapi otorisasi OpenClaw hanya menggunakan ID numerik.

    Lebih aman (tanpa bot pihak ketiga):

    - DM bot Anda, lalu jalankan `openclaw logs --follow` dan baca `from.id`.

    Bot API resmi:

    - DM bot Anda, lalu panggil `https://api.telegram.org/bot<bot_token>/getUpdates` dan baca `message.from.id`.

    Pihak ketiga (kurang privat):

    - DM `@userinfobot` atau `@getidsbot`.

    Lihat [/channels/telegram](/id/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Bisakah beberapa orang menggunakan satu nomor WhatsApp dengan instance OpenClaw yang berbeda?">
    Ya, melalui **routing multi-agent**. Kaitkan setiap **DM** WhatsApp pengirim (peer `kind: "direct"`, pengirim E.164 seperti `+15551234567`) ke `agentId` yang berbeda, sehingga setiap orang mendapatkan workspace dan penyimpanan sesi mereka sendiri. Balasan tetap dikirim dari **akun WhatsApp yang sama**, dan kontrol akses DM (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) bersifat global per akun WhatsApp. Lihat [Routing Multi-Agent](/id/concepts/multi-agent) dan [WhatsApp](/id/channels/whatsapp).
  </Accordion>

  <Accordion title='Bisakah saya menjalankan agen "chat cepat" dan agen "Opus untuk coding"?'>
    Ya. Gunakan routing multi-agent: beri setiap agen model defaultnya sendiri, lalu kaitkan rute masuk (akun penyedia atau peer tertentu) ke masing-masing agen. Contoh config ada di [Routing Multi-Agent](/id/concepts/multi-agent). Lihat juga [Models](/id/concepts/models) dan [Konfigurasi](/id/gateway/configuration).
  </Accordion>

  <Accordion title="Apakah Homebrew berfungsi di Linux?">
    Ya. Homebrew mendukung Linux (Linuxbrew). Penyiapan cepat:

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Jika Anda menjalankan OpenClaw melalui systemd, pastikan PATH service menyertakan `/home/linuxbrew/.linuxbrew/bin` (atau prefix brew Anda) agar tool yang diinstal `brew` dapat diselesaikan dalam shell non-login.
    Build terbaru juga menambahkan direktori bin pengguna umum di awal pada service Linux systemd (misalnya `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) dan menghormati `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR`, dan `FNM_DIR` saat disetel.

  </Accordion>

  <Accordion title="Perbedaan antara instalasi git hackable dan npm install">
    - **Instalasi git hackable:** checkout source lengkap, dapat diedit, paling cocok untuk kontributor.
      Anda menjalankan build secara lokal dan dapat menambal kode/docs.
    - **npm install:** instalasi CLI global, tanpa repo, paling cocok untuk "langsung jalankan."
      Pembaruan berasal dari npm dist-tag.

    Docs: [Memulai](/id/start/getting-started), [Updating](/id/install/updating).

  </Accordion>

  <Accordion title="Bisakah saya beralih antara instalasi npm dan git nanti?">
    Ya. Instal varian lainnya, lalu jalankan Doctor agar service gateway mengarah ke entrypoint yang baru.
    Ini **tidak menghapus data Anda** - hanya mengubah instalasi kode OpenClaw. State Anda
    (`~/.openclaw`) dan workspace (`~/.openclaw/workspace`) tetap tidak tersentuh.

    Dari npm ke git:

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    Dari git ke npm:

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor mendeteksi ketidakcocokan entrypoint service gateway dan menawarkan untuk menulis ulang config service agar sesuai dengan instalasi saat ini (gunakan `--repair` dalam otomatisasi).

    Tip cadangan: lihat [Strategi cadangan](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="Haruskah saya menjalankan Gateway di laptop atau VPS?">
    Jawaban singkat: **jika Anda menginginkan keandalan 24/7, gunakan VPS**. Jika Anda ingin
    hambatan paling rendah dan tidak masalah dengan sleep/restart, jalankan secara lokal.

    **Laptop (Gateway lokal)**

    - **Kelebihan:** tidak ada biaya server, akses langsung ke file lokal, jendela browser langsung.
    - **Kekurangan:** sleep/jaringan terputus = koneksi terputus, pembaruan/reboot OS mengganggu, harus tetap aktif.

    **VPS / cloud**

    - **Kelebihan:** selalu aktif, jaringan stabil, tidak ada masalah sleep laptop, lebih mudah dijaga tetap berjalan.
    - **Kekurangan:** sering berjalan headless (gunakan screenshot), akses file hanya jarak jauh, Anda harus SSH untuk pembaruan.

    **Catatan khusus OpenClaw:** WhatsApp/Telegram/Slack/Mattermost/Discord semuanya berfungsi baik dari VPS. Satu-satunya trade-off nyata adalah **browser headless** vs jendela yang terlihat. Lihat [Browser](/id/tools/browser).

    **Default yang direkomendasikan:** VPS jika Anda pernah mengalami gateway terputus sebelumnya. Lokal sangat cocok saat Anda aktif menggunakan Mac dan ingin akses file lokal atau otomatisasi UI dengan browser yang terlihat.

  </Accordion>

  <Accordion title="Seberapa penting menjalankan OpenClaw di mesin khusus?">
    Tidak wajib, tetapi **disarankan untuk keandalan dan isolasi**.

    - **Host khusus (VPS/Mac mini/Pi):** selalu aktif, gangguan karena sleep/reboot lebih sedikit, izin lebih bersih, lebih mudah dijaga tetap berjalan.
    - **Laptop/desktop bersama:** tetap sepenuhnya layak untuk pengujian dan penggunaan aktif, tetapi siap menghadapi jeda saat mesin sleep atau diperbarui.

    Jika Anda menginginkan yang terbaik dari keduanya, simpan Gateway di host khusus dan pasangkan laptop Anda sebagai **Node** untuk tool layar/kamera/exec lokal. Lihat [Nodes](/id/nodes).
    Untuk panduan keamanan, baca [Security](/id/gateway/security).

  </Accordion>

  <Accordion title="Apa persyaratan minimum VPS dan OS yang direkomendasikan?">
    OpenClaw ringan. Untuk Gateway dasar + satu channel chat:

    - **Minimum absolut:** 1 vCPU, 1GB RAM, ~500MB disk.
    - **Direkomendasikan:** 1-2 vCPU, RAM 2GB atau lebih untuk ruang tambahan (log, media, beberapa channel). Tool Node dan otomatisasi browser dapat membutuhkan banyak sumber daya.

    OS: gunakan **Ubuntu LTS** (atau Debian/Ubuntu modern apa pun). Jalur instalasi Linux paling banyak diuji di sana.

    Docs: [Linux](/id/platforms/linux), [Hosting VPS](/id/vps).

  </Accordion>

  <Accordion title="Bisakah saya menjalankan OpenClaw di VM dan apa persyaratannya?">
    Ya. Perlakukan VM sama seperti VPS: VM harus selalu aktif, dapat dijangkau, dan memiliki cukup
    RAM untuk Gateway serta channel apa pun yang Anda aktifkan.

    Panduan dasar:

    - **Minimum absolut:** 1 vCPU, 1GB RAM.
    - **Direkomendasikan:** RAM 2GB atau lebih jika Anda menjalankan beberapa channel, otomatisasi browser, atau tool media.
    - **OS:** Ubuntu LTS atau Debian/Ubuntu modern lainnya.

    Jika Anda menggunakan Windows, **WSL2 adalah penyiapan bergaya VM yang paling mudah** dan memiliki kompatibilitas
    tool terbaik. Lihat [Windows](/id/platforms/windows), [Hosting VPS](/id/vps).
    Jika Anda menjalankan macOS di VM, lihat [VM macOS](/id/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Apa itu OpenClaw?

<AccordionGroup>
  <Accordion title="Apa itu OpenClaw, dalam satu paragraf?">
    OpenClaw adalah asisten AI pribadi yang Anda jalankan di perangkat Anda sendiri. Ia membalas di permukaan pesan yang sudah Anda gunakan (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat, dan Plugin channel bawaan seperti QQ Bot) dan juga dapat melakukan suara + Canvas langsung di platform yang didukung. **Gateway** adalah control plane yang selalu aktif; asisten adalah produknya.
  </Accordion>

  <Accordion title="Proposisi nilai">
    OpenClaw bukan "sekadar pembungkus Claude." Ini adalah **control plane yang local-first** yang memungkinkan Anda menjalankan
    asisten yang andal di **perangkat keras Anda sendiri**, dapat diakses dari aplikasi chat yang sudah Anda gunakan, dengan
    sesi stateful, memori, dan tool - tanpa menyerahkan kendali alur kerja Anda ke
    SaaS hosted.

    Sorotan:

    - **Perangkat Anda, data Anda:** jalankan Gateway di mana pun Anda mau (Mac, Linux, VPS) dan simpan
      workspace + riwayat sesi secara lokal.
    - **Channel nyata, bukan sandbox web:** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/dll,
      plus suara mobile dan Canvas di platform yang didukung.
    - **Model-agnostik:** gunakan Anthropic, OpenAI, MiniMax, OpenRouter, dll., dengan routing per agen
      dan failover.
    - **Opsi lokal saja:** jalankan model lokal sehingga **semua data dapat tetap berada di perangkat Anda** jika Anda mau.
    - **Routing multi-agent:** agen terpisah per channel, akun, atau tugas, masing-masing dengan
      workspace dan defaultnya sendiri.
    - **Open source dan dapat diutak-atik:** periksa, perluas, dan self-host tanpa vendor lock-in.

    Docs: [Gateway](/id/gateway), [Channels](/id/channels), [Multi-agent](/id/concepts/multi-agent),
    [Memory](/id/concepts/memory).

  </Accordion>

  <Accordion title="Saya baru saja menyiapkannya - apa yang harus saya lakukan terlebih dahulu?">
    Proyek awal yang bagus:

    - Membangun situs web (WordPress, Shopify, atau situs statis sederhana).
    - Membuat prototipe app mobile (garis besar, layar, rencana API).
    - Menata file dan folder (pembersihan, penamaan, penandaan).
    - Menghubungkan Gmail dan mengotomatiskan ringkasan atau tindak lanjut.

    Ini dapat menangani tugas besar, tetapi bekerja paling baik saat Anda membaginya ke dalam beberapa fase dan
    menggunakan sub-agent untuk pekerjaan paralel.

  </Accordion>

  <Accordion title="Apa lima kasus penggunaan sehari-hari teratas untuk OpenClaw?">
    Manfaat sehari-hari biasanya terlihat seperti ini:

    - **Ringkasan pribadi:** ringkasan kotak masuk, kalender, dan berita yang Anda pedulikan.
    - **Riset dan penyusunan:** riset cepat, ringkasan, dan draf pertama untuk email atau docs.
    - **Pengingat dan tindak lanjut:** dorongan dan checklist yang digerakkan Cron atau Heartbeat.
    - **Otomatisasi browser:** mengisi formulir, mengumpulkan data, dan mengulang tugas web.
    - **Koordinasi lintas perangkat:** kirim tugas dari ponsel Anda, biarkan Gateway menjalankannya di server, dan terima hasilnya kembali di chat.

  </Accordion>

  <Accordion title="Bisakah OpenClaw membantu lead gen, outreach, iklan, dan blog untuk SaaS?">
    Ya untuk **riset, kualifikasi, dan penyusunan**. Fitur ini dapat memindai situs, membuat shortlist,
    merangkum prospek, dan menulis draf outreach atau copy iklan.

    Untuk **outreach atau penayangan iklan**, libatkan manusia dalam loop. Hindari spam, patuhi hukum lokal dan
    kebijakan platform, dan tinjau apa pun sebelum dikirim. Pola paling aman adalah membiarkan
    OpenClaw menyusun draf dan Anda yang menyetujuinya.

    Docs: [Security](/id/gateway/security).

  </Accordion>

  <Accordion title="Apa kelebihannya dibanding Claude Code untuk pengembangan web?">
    OpenClaw adalah **asisten pribadi** dan lapisan koordinasi, bukan pengganti IDE. Gunakan
    Claude Code atau Codex untuk loop coding langsung tercepat di dalam repo. Gunakan OpenClaw ketika Anda
    menginginkan memori yang tahan lama, akses lintas perangkat, dan orkestrasi tool.

    Kelebihan:

    - **Memori + workspace persisten** antar sesi
    - **Akses multi-platform** (WhatsApp, Telegram, TUI, WebChat)
    - **Orkestrasi tool** (browser, file, penjadwalan, hook)
    - **Gateway yang selalu aktif** (jalankan di VPS, berinteraksi dari mana saja)
    - **Nodes** untuk browser/layar/kamera/exec lokal

    Showcase: [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills dan otomatisasi

<AccordionGroup>
  <Accordion title="Bagaimana cara menyesuaikan Skills tanpa membuat repo tetap kotor?">
    Gunakan override terkelola alih-alih mengedit salinan repo. Letakkan perubahan Anda di `~/.openclaw/skills/<name>/SKILL.md` (atau tambahkan folder melalui `skills.load.extraDirs` di `~/.openclaw/openclaw.json`). Prioritasnya adalah `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bawaan → `skills.load.extraDirs`, jadi override terkelola tetap menang atas Skills bawaan tanpa menyentuh git. Jika Anda memerlukan skill yang terinstal secara global tetapi hanya terlihat oleh beberapa agen, simpan salinan bersama di `~/.openclaw/skills` dan kendalikan visibilitas dengan `agents.defaults.skills` dan `agents.list[].skills`. Hanya edit yang layak di-upstream yang seharusnya berada di repo dan dikirim sebagai PR.
  </Accordion>

  <Accordion title="Bisakah saya memuat Skills dari folder khusus?">
    Ya. Tambahkan direktori tambahan melalui `skills.load.extraDirs` di `~/.openclaw/openclaw.json` (prioritas terendah). Prioritas default adalah `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → bawaan → `skills.load.extraDirs`. `clawhub` menginstal ke `./skills` secara default, yang diperlakukan OpenClaw sebagai `<workspace>/skills` pada sesi berikutnya. Jika skill tersebut hanya boleh terlihat oleh agen tertentu, pasangkan itu dengan `agents.defaults.skills` atau `agents.list[].skills`.
  </Accordion>

  <Accordion title="Bagaimana saya dapat menggunakan model yang berbeda untuk tugas yang berbeda?">
    Saat ini pola yang didukung adalah:

    - **Pekerjaan Cron**: pekerjaan terisolasi dapat menetapkan override `model` per pekerjaan.
    - **Sub-agent**: rute tugas ke agen terpisah dengan model default yang berbeda.
    - **Peralihan sesuai permintaan**: gunakan `/model` untuk mengubah model sesi saat ini kapan saja.

    Lihat [Pekerjaan Cron](/id/automation/cron-jobs), [Routing Multi-Agent](/id/concepts/multi-agent), dan [Perintah slash](/id/tools/slash-commands).

  </Accordion>

  <Accordion title="Bot membeku saat melakukan pekerjaan berat. Bagaimana cara memindahkan beban itu?">
    Gunakan **sub-agent** untuk tugas yang panjang atau paralel. Sub-agent berjalan dalam sesi mereka sendiri,
    mengembalikan ringkasan, dan menjaga chat utama Anda tetap responsif.

    Minta bot Anda untuk "spawn sub-agent untuk tugas ini" atau gunakan `/subagents`.
    Gunakan `/status` di chat untuk melihat apa yang sedang dilakukan Gateway saat ini (dan apakah sedang sibuk).

    Tip token: tugas panjang dan sub-agent sama-sama mengonsumsi token. Jika biaya menjadi perhatian, tetapkan
    model yang lebih murah untuk sub-agent melalui `agents.defaults.subagents.model`.

    Docs: [Sub-agent](/id/tools/subagents), [Tugas Latar Belakang](/id/automation/tasks).

  </Accordion>

  <Accordion title="Bagaimana sesi subagent yang terikat ke thread bekerja di Discord?">
    Gunakan pengikatan thread. Anda dapat mengikat thread Discord ke target subagent atau sesi agar pesan tindak lanjut di thread tersebut tetap berada pada sesi yang terikat itu.

    Alur dasar:

    - Spawn dengan `sessions_spawn` menggunakan `thread: true` (dan opsional `mode: "session"` untuk tindak lanjut persisten).
    - Atau ikat secara manual dengan `/focus <target>`.
    - Gunakan `/agents` untuk memeriksa status pengikatan.
    - Gunakan `/session idle <duration|off>` dan `/session max-age <duration|off>` untuk mengontrol pelepasan fokus otomatis.
    - Gunakan `/unfocus` untuk melepaskan thread.

    Config yang diperlukan:

    - Default global: `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Override Discord: `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Ikat otomatis saat spawn: tetapkan `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Docs: [Sub-agent](/id/tools/subagents), [Discord](/id/channels/discord), [Referensi Konfigurasi](/id/gateway/configuration-reference), [Perintah slash](/id/tools/slash-commands).

  </Accordion>

  <Accordion title="Sub-agent selesai, tetapi pembaruan penyelesaian dikirim ke tempat yang salah atau tidak pernah diposting. Apa yang harus saya periksa?">
    Periksa rute peminta yang telah diselesaikan terlebih dahulu:

    - Pengiriman sub-agent mode completion lebih memilih thread atau rute percakapan yang terikat jika ada.
    - Jika asal completion hanya membawa channel, OpenClaw akan fallback ke rute tersimpan sesi peminta (`lastChannel` / `lastTo` / `lastAccountId`) agar pengiriman langsung tetap dapat berhasil.
    - Jika tidak ada rute terikat maupun rute tersimpan yang dapat digunakan, pengiriman langsung dapat gagal dan hasilnya akan fallback ke pengiriman sesi antrean alih-alih langsung diposting ke chat.
    - Target yang tidak valid atau usang tetap dapat memaksa fallback antrean atau kegagalan pengiriman akhir.
    - Jika balasan asisten terakhir yang terlihat dari child adalah token senyap persis `NO_REPLY` / `no_reply`, atau persis `ANNOUNCE_SKIP`, OpenClaw sengaja menekan pengumuman alih-alih memposting progres lama yang basi.
    - Jika child kehabisan waktu setelah hanya melakukan pemanggilan tool, pengumuman dapat merangkum itu menjadi ringkasan progres parsial singkat alih-alih memutar ulang output tool mentah.

    Debug:

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Docs: [Sub-agent](/id/tools/subagents), [Tugas Latar Belakang](/id/automation/tasks), [Tool Sesi](/id/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron atau pengingat tidak berjalan. Apa yang harus saya periksa?">
    Cron berjalan di dalam proses Gateway. Jika Gateway tidak berjalan terus-menerus,
    pekerjaan terjadwal tidak akan berjalan.

    Checklist:

    - Pastikan cron diaktifkan (`cron.enabled`) dan `OPENCLAW_SKIP_CRON` tidak disetel.
    - Periksa bahwa Gateway berjalan 24/7 (tanpa sleep/restart).
    - Verifikasi pengaturan zona waktu untuk pekerjaan (`--tz` vs zona waktu host).

    Debug:

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Docs: [Pekerjaan Cron](/id/automation/cron-jobs), [Otomatisasi & Tugas](/id/automation).

  </Accordion>

  <Accordion title="Cron berjalan, tetapi tidak ada yang dikirim ke channel. Mengapa?">
    Periksa mode pengiriman terlebih dahulu:

    - `--no-deliver` / `delivery.mode: "none"` berarti tidak ada pesan eksternal yang diharapkan.
    - Target pengumuman yang hilang atau tidak valid (`channel` / `to`) berarti runner melewati pengiriman keluar.
    - Kegagalan auth channel (`unauthorized`, `Forbidden`) berarti runner mencoba mengirim, tetapi kredensial memblokirnya.
    - Hasil terisolasi yang senyap (`NO_REPLY` / `no_reply` saja) diperlakukan sebagai sengaja tidak dapat dikirim, jadi runner juga menekan pengiriman fallback antrean.

    Untuk pekerjaan cron terisolasi, runner memiliki pengiriman akhir. Agen diharapkan
    mengembalikan ringkasan teks biasa agar runner dapat mengirimkannya. `--no-deliver` menjaga
    hasil itu tetap internal; itu tidak membuat agen dapat mengirim langsung dengan
    tool pesan sebagai gantinya.

    Debug:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Docs: [Pekerjaan Cron](/id/automation/cron-jobs), [Tugas Latar Belakang](/id/automation/tasks).

  </Accordion>

  <Accordion title="Mengapa eksekusi cron terisolasi beralih model atau mencoba ulang sekali?">
    Itu biasanya merupakan jalur peralihan model langsung, bukan penjadwalan ganda.

    Cron terisolasi dapat mempertahankan handoff model runtime dan mencoba ulang ketika
    eksekusi aktif melempar `LiveSessionModelSwitchError`. Percobaan ulang mempertahankan
    penyedia/model yang sudah dialihkan, dan jika peralihan tersebut membawa override profil auth baru, cron
    juga mempertahankannya sebelum mencoba ulang.

    Aturan pemilihan terkait:

    - Override model hook Gmail menang lebih dulu jika berlaku.
    - Lalu `model` per pekerjaan.
    - Lalu override model sesi cron tersimpan apa pun.
    - Lalu pemilihan model agen/default normal.

    Loop percobaan ulang dibatasi. Setelah percobaan awal ditambah 2 percobaan ulang peralihan,
    cron dibatalkan alih-alih berulang tanpa henti.

    Debug:

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Docs: [Pekerjaan Cron](/id/automation/cron-jobs), [CLI cron](/cli/cron).

  </Accordion>

  <Accordion title="Bagaimana cara menginstal Skills di Linux?">
    Gunakan perintah `openclaw skills` native atau letakkan Skills ke workspace Anda. UI Skills macOS tidak tersedia di Linux.
    Jelajahi Skills di [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    `openclaw skills install` native menulis ke direktori `skills/` workspace aktif.
    Instal CLI `clawhub` terpisah hanya jika Anda ingin memublikasikan atau
    menyinkronkan skill Anda sendiri. Untuk instalasi bersama lintas agen, letakkan skill di bawah
    `~/.openclaw/skills` dan gunakan `agents.defaults.skills` atau
    `agents.list[].skills` jika Anda ingin mempersempit agen mana yang dapat melihatnya.

  </Accordion>

  <Accordion title="Bisakah OpenClaw menjalankan tugas sesuai jadwal atau terus-menerus di latar belakang?">
    Ya. Gunakan penjadwal Gateway:

    - **Pekerjaan Cron** untuk tugas terjadwal atau berulang (bertahan setelah restart).
    - **Heartbeat** untuk pemeriksaan berkala "sesi utama".
    - **Pekerjaan terisolasi** untuk agen otonom yang memposting ringkasan atau mengirim ke chat.

    Docs: [Pekerjaan Cron](/id/automation/cron-jobs), [Otomatisasi & Tugas](/id/automation),
    [Heartbeat](/id/gateway/heartbeat).

  </Accordion>

  <Accordion title="Bisakah saya menjalankan Skills Apple khusus macOS dari Linux?">
    Tidak secara langsung. Skills macOS dibatasi oleh `metadata.openclaw.os` plus biner yang diperlukan, dan Skills hanya muncul di prompt sistem ketika memenuhi syarat di **host Gateway**. Di Linux, Skills khusus `darwin` (seperti `apple-notes`, `apple-reminders`, `things-mac`) tidak akan dimuat kecuali Anda mengganti pembatasannya.

    Anda memiliki tiga pola yang didukung:

    **Opsi A - jalankan Gateway di Mac (paling sederhana).**
    Jalankan Gateway di tempat biner macOS tersedia, lalu hubungkan dari Linux dalam [mode remote](#gateway-ports-already-running-and-remote-mode) atau melalui Tailscale. Skills dimuat secara normal karena host Gateway adalah macOS.

    **Opsi B - gunakan Node macOS (tanpa SSH).**
    Jalankan Gateway di Linux, pasangkan Node macOS (app menubar), dan setel **Node Run Commands** ke "Always Ask" atau "Always Allow" di Mac. OpenClaw dapat memperlakukan Skills khusus macOS sebagai memenuhi syarat ketika biner yang diperlukan ada di Node. Agen menjalankan Skills tersebut melalui tool `nodes`. Jika Anda memilih "Always Ask", menyetujui "Always Allow" dalam prompt akan menambahkan perintah tersebut ke allowlist.

    **Opsi C - proksikan biner macOS melalui SSH (lanjutan).**
    Biarkan Gateway tetap di Linux, tetapi buat biner CLI yang diperlukan diselesaikan ke wrapper SSH yang berjalan di Mac. Lalu override skill agar mengizinkan Linux sehingga tetap memenuhi syarat.

    1. Buat wrapper SSH untuk biner tersebut (contoh: `memo` untuk Apple Notes):

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Letakkan wrapper di `PATH` pada host Linux (misalnya `~/bin/memo`).
    3. Override metadata skill (workspace atau `~/.openclaw/skills`) agar mengizinkan Linux:

       ```markdown
       ---
       name: apple-notes
       description: Kelola Apple Notes melalui CLI memo di macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Mulai sesi baru agar snapshot Skills disegarkan.

  </Accordion>

  <Accordion title="Apakah Anda memiliki integrasi Notion atau HeyGen?">
    Belum bawaan saat ini.

    Opsi:

    - **Skill / Plugin kustom:** paling baik untuk akses API yang andal (Notion/HeyGen sama-sama memiliki API).
    - **Otomatisasi browser:** berfungsi tanpa kode tetapi lebih lambat dan lebih rapuh.

    Jika Anda ingin mempertahankan konteks per klien (alur kerja agensi), pola sederhananya adalah:

    - Satu halaman Notion per klien (konteks + preferensi + pekerjaan aktif).
    - Minta agen mengambil halaman itu di awal sesi.

    Jika Anda menginginkan integrasi native, buka permintaan fitur atau bangun skill
    yang menargetkan API tersebut.

    Instal Skills:

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Instalasi native masuk ke direktori `skills/` workspace aktif. Untuk Skills bersama lintas agen, tempatkan di `~/.openclaw/skills/<name>/SKILL.md`. Jika hanya beberapa agen yang boleh melihat instalasi bersama, konfigurasikan `agents.defaults.skills` atau `agents.list[].skills`. Beberapa Skills mengharapkan biner yang diinstal melalui Homebrew; di Linux itu berarti Linuxbrew (lihat entri FAQ Homebrew Linux di atas). Lihat [Skills](/id/tools/skills), [Config Skills](/id/tools/skills-config), dan [ClawHub](/id/tools/clawhub).

  </Accordion>

  <Accordion title="Bagaimana cara menggunakan Chrome yang sudah login milik saya dengan OpenClaw?">
    Gunakan profil browser bawaan `user`, yang terhubung melalui Chrome DevTools MCP:

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Jika Anda menginginkan nama kustom, buat profil MCP eksplisit:

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Jalur ini bersifat lokal terhadap host. Jika Gateway berjalan di tempat lain, jalankan host node pada mesin browser atau gunakan CDP remote.

    Batas saat ini pada `existing-session` / `user`:

    - tindakan berbasis ref, bukan berbasis pemilih CSS
    - upload memerlukan `ref` / `inputRef` dan saat ini hanya mendukung satu file dalam satu waktu
    - `responsebody`, ekspor PDF, intersepsi unduhan, dan tindakan batch masih memerlukan browser terkelola atau profil CDP mentah

  </Accordion>
</AccordionGroup>

## Sandboxing dan memori

<AccordionGroup>
  <Accordion title="Apakah ada docs khusus sandboxing?">
    Ya. Lihat [Sandboxing](/id/gateway/sandboxing). Untuk penyiapan khusus Docker (Gateway penuh di Docker atau image sandbox), lihat [Docker](/id/install/docker).
  </Accordion>

  <Accordion title="Docker terasa terbatas - bagaimana cara mengaktifkan fitur lengkap?">
    Image default mengutamakan keamanan dan berjalan sebagai pengguna `node`, sehingga tidak
    menyertakan paket sistem, Homebrew, atau browser bawaan. Untuk penyiapan yang lebih lengkap:

    - Pertahankan `/home/node` dengan `OPENCLAW_HOME_VOLUME` agar cache tetap tersimpan.
    - Masukkan dependensi sistem ke dalam image dengan `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Instal browser Playwright melalui CLI bawaan:
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Tetapkan `PLAYWRIGHT_BROWSERS_PATH` dan pastikan path tersebut dipertahankan.

    Docs: [Docker](/id/install/docker), [Browser](/id/tools/browser).

  </Accordion>

  <Accordion title="Bisakah saya menjaga DM tetap pribadi tetapi membuat grup menjadi publik/tersandbox dengan satu agen?">
    Ya - jika lalu lintas privat Anda adalah **DM** dan lalu lintas publik Anda adalah **grup**.

    Gunakan `agents.defaults.sandbox.mode: "non-main"` agar sesi grup/channel (kunci non-utama) berjalan di Docker, sementara sesi DM utama tetap di host. Lalu batasi tool apa yang tersedia dalam sesi tersandbox melalui `tools.sandbox.tools`.

    Panduan penyiapan + contoh config: [Grup: DM pribadi + grup publik](/id/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Referensi config utama: [Konfigurasi Gateway](/id/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Bagaimana cara mengikat folder host ke dalam sandbox?">
    Tetapkan `agents.defaults.sandbox.docker.binds` ke `["host:path:mode"]` (misalnya `"/home/user/src:/src:ro"`). Pengikatan global + per agen digabungkan; pengikatan per agen diabaikan saat `scope: "shared"`. Gunakan `:ro` untuk apa pun yang sensitif dan ingat bahwa pengikatan melewati batas filesystem sandbox.

    OpenClaw memvalidasi sumber bind terhadap path yang dinormalisasi dan path kanonis yang diselesaikan melalui leluhur terdalam yang sudah ada. Itu berarti escape parent symlink tetap gagal dalam mode fail-closed bahkan ketika segmen path terakhir belum ada, dan pemeriksaan root yang diizinkan tetap berlaku setelah resolusi symlink.

    Lihat [Sandboxing](/id/gateway/sandboxing#custom-bind-mounts) dan [Sandbox vs Tool Policy vs Elevated](/id/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) untuk contoh dan catatan keamanan.

  </Accordion>

  <Accordion title="Bagaimana cara kerja memori?">
    Memori OpenClaw hanyalah file Markdown di workspace agen:

    - Catatan harian di `memory/YYYY-MM-DD.md`
    - Catatan jangka panjang yang dikurasi di `MEMORY.md` (hanya sesi utama/pribadi)

    OpenClaw juga menjalankan **flush memori senyap sebelum Compaction** untuk mengingatkan model
    agar menulis catatan yang tahan lama sebelum auto-Compaction. Ini hanya berjalan saat workspace
    dapat ditulisi (sandbox baca-saja melewatinya). Lihat [Memori](/id/concepts/memory).

  </Accordion>

  <Accordion title="Memori terus melupakan hal-hal. Bagaimana cara membuatnya melekat?">
    Minta bot untuk **menulis fakta itu ke memori**. Catatan jangka panjang sebaiknya masuk ke `MEMORY.md`,
    konteks jangka pendek masuk ke `memory/YYYY-MM-DD.md`.

    Ini masih merupakan area yang terus kami tingkatkan. Akan membantu untuk mengingatkan model agar menyimpan memori;
    model akan tahu apa yang harus dilakukan. Jika tetap lupa, verifikasi bahwa Gateway menggunakan
    workspace yang sama pada setiap eksekusi.

    Docs: [Memori](/id/concepts/memory), [Workspace agen](/id/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Apakah memori bertahan selamanya? Apa batasnya?">
    File memori tersimpan di disk dan bertahan sampai Anda menghapusnya. Batasnya adalah
    penyimpanan Anda, bukan modelnya. **Konteks sesi** tetap dibatasi oleh jendela konteks
    model, sehingga percakapan panjang dapat mengalami Compaction atau pemotongan. Itulah sebabnya
    pencarian memori ada - fitur ini hanya menarik kembali bagian yang relevan ke dalam konteks.

    Docs: [Memori](/id/concepts/memory), [Konteks](/id/concepts/context).

  </Accordion>

  <Accordion title="Apakah pencarian memori semantik memerlukan kunci API OpenAI?">
    Hanya jika Anda menggunakan **embedding OpenAI**. OAuth Codex mencakup chat/completions dan
    **tidak** memberikan akses embedding, jadi **masuk dengan Codex (OAuth atau
    login CLI Codex)** tidak membantu untuk pencarian memori semantik. Embedding OpenAI
    tetap memerlukan kunci API nyata (`OPENAI_API_KEY` atau `models.providers.openai.apiKey`).

    Jika Anda tidak menetapkan penyedia secara eksplisit, OpenClaw akan memilih penyedia secara otomatis ketika
    ia dapat menyelesaikan kunci API (profil auth, `models.providers.*.apiKey`, atau env vars).
    OpenClaw akan memprioritaskan OpenAI jika kunci OpenAI dapat diselesaikan, jika tidak maka Gemini jika kunci Gemini
    dapat diselesaikan, lalu Voyage, lalu Mistral. Jika tidak ada kunci remote yang tersedia, pencarian memori
    tetap dinonaktifkan sampai Anda mengonfigurasinya. Jika Anda memiliki path model lokal
    yang dikonfigurasi dan tersedia, OpenClaw
    memprioritaskan `local`. Ollama didukung saat Anda secara eksplisit menetapkan
    `memorySearch.provider = "ollama"`.

    Jika Anda lebih suka tetap lokal, tetapkan `memorySearch.provider = "local"` (dan opsional
    `memorySearch.fallback = "none"`). Jika Anda menginginkan embedding Gemini, tetapkan
    `memorySearch.provider = "gemini"` dan sediakan `GEMINI_API_KEY` (atau
    `memorySearch.remote.apiKey`). Kami mendukung model embedding **OpenAI, Gemini, Voyage, Mistral, Ollama, atau local**
    - lihat [Memori](/id/concepts/memory) untuk detail penyiapannya.

  </Accordion>
</AccordionGroup>

## Lokasi penyimpanan di disk

<AccordionGroup>
  <Accordion title="Apakah semua data yang digunakan dengan OpenClaw disimpan secara lokal?">
    Tidak - **state OpenClaw bersifat lokal**, tetapi **layanan eksternal tetap melihat apa yang Anda kirimkan kepada mereka**.

    - **Lokal secara default:** sesi, file memori, config, dan workspace berada di host Gateway
      (`~/.openclaw` + direktori workspace Anda).
    - **Remote karena kebutuhan:** pesan yang Anda kirim ke penyedia model (Anthropic/OpenAI/dll.) dikirim ke
      API mereka, dan platform chat (WhatsApp/Telegram/Slack/dll.) menyimpan data pesan di
      server mereka.
    - **Anda mengendalikan jejaknya:** menggunakan model lokal menjaga prompt tetap di mesin Anda, tetapi lalu lintas
      channel tetap melewati server channel tersebut.

    Terkait: [Workspace agen](/id/concepts/agent-workspace), [Memori](/id/concepts/memory).

  </Accordion>

  <Accordion title="Di mana OpenClaw menyimpan datanya?">
    Semuanya berada di bawah `$OPENCLAW_STATE_DIR` (default: `~/.openclaw`):

    | Path                                                            | Tujuan                                                             |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Config utama (JSON5)                                               |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Impor OAuth lama (disalin ke profil auth saat pertama kali digunakan) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Profil auth (OAuth, kunci API, dan `keyRef`/`tokenRef` opsional)   |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Payload secret berbasis file opsional untuk penyedia SecretRef `file` |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | File kompatibilitas lama (entri `api_key` statis telah dibersihkan) |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | State penyedia (mis. `whatsapp/<accountId>/creds.json`)            |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | State per agen (agentDir + sesi)                                   |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Riwayat percakapan & state (per agen)                              |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Metadata sesi (per agen)                                           |

    Path single-agent lama: `~/.openclaw/agent/*` (dimigrasikan oleh `openclaw doctor`).

    **Workspace** Anda (`AGENTS.md`, file memori, Skills, dll.) terpisah dan dikonfigurasi melalui `agents.defaults.workspace` (default: `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Di mana AGENTS.md / SOUL.md / USER.md / MEMORY.md seharusnya berada?">
    File-file ini berada di **workspace agen**, bukan `~/.openclaw`.

    - **Workspace (per agen)**: `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (atau fallback lama `memory.md` saat `MEMORY.md` tidak ada),
      `memory/YYYY-MM-DD.md`, `HEARTBEAT.md` opsional.
    - **Direktori state (`~/.openclaw`)**: config, state channel/penyedia, profil auth, sesi, log,
      dan Skills bersama (`~/.openclaw/skills`).

    Workspace default adalah `~/.openclaw/workspace`, dapat dikonfigurasi melalui:

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Jika bot "lupa" setelah restart, pastikan Gateway menggunakan
    workspace yang sama pada setiap peluncuran (dan ingat: mode remote menggunakan **workspace milik host gateway**,
    bukan laptop lokal Anda).

    Tip: jika Anda menginginkan perilaku atau preferensi yang tahan lama, minta bot untuk **menuliskannya ke dalam
    AGENTS.md atau MEMORY.md** alih-alih bergantung pada riwayat chat.

    Lihat [Workspace agen](/id/concepts/agent-workspace) dan [Memori](/id/concepts/memory).

  </Accordion>

  <Accordion title="Strategi cadangan yang direkomendasikan">
    Simpan **workspace agen** Anda dalam repo git **privat** dan cadangkan di tempat
    yang privat (misalnya GitHub private). Ini menangkap memori + file AGENTS/SOUL/USER
    dan memungkinkan Anda memulihkan "pikiran" asisten nanti.

    **Jangan** commit apa pun di bawah `~/.openclaw` (kredensial, sesi, token, atau payload secret terenkripsi).
    Jika Anda memerlukan pemulihan penuh, cadangkan workspace dan direktori state
    secara terpisah (lihat pertanyaan migrasi di atas).

    Docs: [Workspace agen](/id/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Bagaimana cara menghapus OpenClaw sepenuhnya?">
    Lihat panduan khusus: [Uninstall](/id/install/uninstall).
  </Accordion>

  <Accordion title="Bisakah agen bekerja di luar workspace?">
    Ya. Workspace adalah **cwd default** dan jangkar memori, bukan sandbox keras.
    Path relatif diselesaikan di dalam workspace, tetapi path absolut dapat mengakses
    lokasi host lain kecuali sandboxing diaktifkan. Jika Anda memerlukan isolasi, gunakan
    [`agents.defaults.sandbox`](/id/gateway/sandboxing) atau pengaturan sandbox per agen. Jika Anda
    ingin repo menjadi direktori kerja default, arahkan `workspace`
    agen itu ke root repo. Repo OpenClaw hanyalah source code; simpan
    workspace terpisah kecuali Anda memang sengaja ingin agen bekerja di dalamnya.

    Contoh (repo sebagai cwd default):

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Mode remote: di mana penyimpanan sesi?">
    State sesi dimiliki oleh **host gateway**. Jika Anda berada dalam mode remote, penyimpanan sesi yang penting bagi Anda berada di mesin remote, bukan di laptop lokal Anda. Lihat [Manajemen sesi](/id/concepts/session).
  </Accordion>
</AccordionGroup>

## Dasar-dasar config

<AccordionGroup>
  <Accordion title="Apa format config-nya? Di mana lokasinya?">
    OpenClaw membaca config **JSON5** opsional dari `$OPENCLAW_CONFIG_PATH` (default: `~/.openclaw/openclaw.json`):

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Jika file tidak ada, OpenClaw menggunakan default yang cukup aman (termasuk workspace default `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='Saya menetapkan gateway.bind: "lan" (atau "tailnet") dan sekarang tidak ada yang mendengarkan / UI mengatakan unauthorized'>
    Bind non-loopback **memerlukan jalur auth gateway yang valid**. Dalam praktiknya itu berarti:

    - auth shared-secret: token atau kata sandi
    - `gateway.auth.mode: "trusted-proxy"` di belakang reverse proxy sadar identitas non-loopback yang dikonfigurasi dengan benar

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Catatan:

    - `gateway.remote.token` / `.password` **tidak** mengaktifkan auth gateway lokal dengan sendirinya.
    - Jalur pemanggilan lokal dapat menggunakan `gateway.remote.*` sebagai fallback hanya ketika `gateway.auth.*` tidak disetel.
    - Untuk auth kata sandi, tetapkan `gateway.auth.mode: "password"` plus `gateway.auth.password` (atau `OPENCLAW_GATEWAY_PASSWORD`) sebagai gantinya.
    - Jika `gateway.auth.token` / `gateway.auth.password` secara eksplisit dikonfigurasi melalui SecretRef dan tidak dapat diselesaikan, resolusi gagal dalam mode fail-closed (tidak ada fallback remote yang menutupi).
    - Penyiapan shared-secret Control UI mengautentikasi melalui `connect.params.auth.token` atau `connect.params.auth.password` (disimpan di pengaturan app/UI). Mode pembawa identitas seperti Tailscale Serve atau `trusted-proxy` menggunakan header permintaan sebagai gantinya. Hindari menaruh shared secret di URL.
    - Dengan `gateway.auth.mode: "trusted-proxy"`, reverse proxy loopback pada host yang sama tetap **tidak** memenuhi auth trusted-proxy. Trusted proxy harus berupa sumber non-loopback yang dikonfigurasi.

  </Accordion>

  <Accordion title="Mengapa sekarang saya memerlukan token di localhost?">
    OpenClaw memberlakukan auth gateway secara default, termasuk loopback. Pada jalur default normal, itu berarti auth token: jika tidak ada jalur auth eksplisit yang dikonfigurasi, startup gateway akan diselesaikan ke mode token dan otomatis menghasilkan token, lalu menyimpannya ke `gateway.auth.token`, jadi **klien WS lokal harus mengautentikasi**. Ini memblokir proses lokal lain untuk memanggil Gateway.

    Jika Anda lebih memilih jalur auth yang berbeda, Anda dapat secara eksplisit memilih mode kata sandi (atau, untuk reverse proxy sadar identitas non-loopback, `trusted-proxy`). Jika Anda **benar-benar** menginginkan loopback terbuka, tetapkan `gateway.auth.mode: "none"` secara eksplisit di config Anda. Doctor dapat membuat token untuk Anda kapan saja: `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Apakah saya harus restart setelah mengubah config?">
    Gateway memantau config dan mendukung hot-reload:

    - `gateway.reload.mode: "hybrid"` (default): menerapkan hot-apply untuk perubahan yang aman, restart untuk perubahan yang kritis
    - `hot`, `restart`, `off` juga didukung

  </Accordion>

  <Accordion title="Bagaimana cara menonaktifkan tagline CLI yang lucu?">
    Tetapkan `cli.banner.taglineMode` di config:

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off`: menyembunyikan teks tagline tetapi tetap menampilkan baris judul/versi banner.
    - `default`: selalu menggunakan `All your chats, one OpenClaw.`.
    - `random`: tagline lucu/musiman yang bergilir (perilaku default).
    - Jika Anda tidak menginginkan banner sama sekali, tetapkan env `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Bagaimana cara mengaktifkan pencarian web (dan pengambilan web)?">
    `web_fetch` berfungsi tanpa kunci API. `web_search` bergantung pada
    penyedia yang Anda pilih:

    - Penyedia berbasis API seperti Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity, dan Tavily memerlukan penyiapan kunci API normal mereka.
    - Ollama Web Search tidak memerlukan kunci, tetapi menggunakan host Ollama yang Anda konfigurasikan dan memerlukan `ollama signin`.
    - DuckDuckGo tidak memerlukan kunci, tetapi merupakan integrasi tidak resmi berbasis HTML.
    - SearXNG tidak memerlukan kunci/dapat di-self-host; konfigurasikan `SEARXNG_BASE_URL` atau `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Direkomendasikan:** jalankan `openclaw configure --section web` dan pilih penyedia.
    Alternatif env:

    - Brave: `BRAVE_API_KEY`
    - Exa: `EXA_API_KEY`
    - Firecrawl: `FIRECRAWL_API_KEY`
    - Gemini: `GEMINI_API_KEY`
    - Grok: `XAI_API_KEY`
    - Kimi: `KIMI_API_KEY` atau `MOONSHOT_API_KEY`
    - MiniMax Search: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, atau `MINIMAX_API_KEY`
    - Perplexity: `PERPLEXITY_API_KEY` atau `OPENROUTER_API_KEY`
    - SearXNG: `SEARXNG_BASE_URL`
    - Tavily: `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // opsional; hilangkan untuk auto-detect
            },
          },
        },
    }
    ```

    Config pencarian web khusus penyedia kini berada di bawah `plugins.entries.<plugin>.config.webSearch.*`.
    Path penyedia lama `tools.web.search.*` masih dimuat sementara untuk kompatibilitas, tetapi tidak boleh digunakan untuk config baru.
    Config fallback pengambilan web Firecrawl berada di bawah `plugins.entries.firecrawl.config.webFetch.*`.

    Catatan:

    - Jika Anda menggunakan allowlist, tambahkan `web_search`/`web_fetch`/`x_search` atau `group:web`.
    - `web_fetch` aktif secara default (kecuali dinonaktifkan secara eksplisit).
    - Jika `tools.web.fetch.provider` dihilangkan, OpenClaw otomatis mendeteksi penyedia fallback pengambilan pertama yang siap dari kredensial yang tersedia. Saat ini penyedia bawaannya adalah Firecrawl.
    - Daemon membaca env vars dari `~/.openclaw/.env` (atau lingkungan service).

    Docs: [Tool web](/id/tools/web).

  </Accordion>

  <Accordion title="config.apply menghapus config saya. Bagaimana cara memulihkannya dan menghindari hal ini?">
    `config.apply` menggantikan **seluruh config**. Jika Anda mengirim objek parsial, semua hal
    lainnya akan dihapus.

    Pemulihan:

    - Pulihkan dari cadangan (git atau salinan `~/.openclaw/openclaw.json`).
    - Jika Anda tidak memiliki cadangan, jalankan ulang `openclaw doctor` dan konfigurasikan ulang channel/model.
    - Jika ini tidak terduga, buat bug dan sertakan config terakhir yang Anda ketahui atau cadangan apa pun.
    - Agen coding lokal sering kali dapat merekonstruksi config yang berfungsi dari log atau riwayat.

    Cara menghindarinya:

    - Gunakan `openclaw config set` untuk perubahan kecil.
    - Gunakan `openclaw configure` untuk pengeditan interaktif.
    - Gunakan `config.schema.lookup` terlebih dahulu saat Anda tidak yakin dengan path persis atau bentuk field; fitur ini mengembalikan node schema dangkal plus ringkasan child langsung untuk penelusuran lebih lanjut.
    - Gunakan `config.patch` untuk edit RPC parsial; simpan `config.apply` hanya untuk penggantian config penuh.
    - Jika Anda menggunakan tool `gateway` khusus owner dari eksekusi agen, tool itu tetap akan menolak penulisan ke `tools.exec.ask` / `tools.exec.security` (termasuk alias lama `tools.bash.*` yang dinormalisasi ke path exec terlindungi yang sama).

    Docs: [Config](/cli/config), [Configure](/cli/configure), [Doctor](/id/gateway/doctor).

  </Accordion>

  <Accordion title="Bagaimana cara menjalankan Gateway pusat dengan worker khusus di berbagai perangkat?">
    Pola yang umum adalah **satu Gateway** (mis. Raspberry Pi) plus **Node** dan **agen**:

    - **Gateway (pusat):** memiliki channel (Signal/WhatsApp), routing, dan sesi.
    - **Nodes (perangkat):** Mac/iOS/Android terhubung sebagai periferal dan mengekspos tool lokal (`system.run`, `canvas`, `camera`).
    - **Agen (worker):** otak/workspace terpisah untuk peran khusus (mis. "Hetzner ops", "Data pribadi").
    - **Sub-agent:** memunculkan pekerjaan latar belakang dari agen utama saat Anda menginginkan paralelisme.
    - **TUI:** terhubung ke Gateway dan berpindah agen/sesi.

    Docs: [Nodes](/id/nodes), [Akses jarak jauh](/id/gateway/remote), [Routing Multi-Agent](/id/concepts/multi-agent), [Sub-agent](/id/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Bisakah browser OpenClaw berjalan headless?">
    Ya. Ini adalah opsi config:

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    Default-nya adalah `false` (headful). Headless lebih mungkin memicu pemeriksaan anti-bot di beberapa situs. Lihat [Browser](/id/tools/browser).

    Headless menggunakan **engine Chromium yang sama** dan berfungsi untuk sebagian besar otomatisasi (formulir, klik, scraping, login). Perbedaan utamanya:

    - Tidak ada jendela browser yang terlihat (gunakan screenshot jika Anda memerlukan visual).
    - Beberapa situs lebih ketat terhadap otomatisasi dalam mode headless (CAPTCHA, anti-bot).
      Misalnya, X/Twitter sering memblokir sesi headless.

  </Accordion>

  <Accordion title="Bagaimana cara menggunakan Brave untuk kontrol browser?">
    Tetapkan `browser.executablePath` ke biner Brave Anda (atau browser berbasis Chromium lainnya) dan restart Gateway.
    Lihat contoh config lengkap di [Browser](/id/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Gateway remote dan Node

<AccordionGroup>
  <Accordion title="Bagaimana perintah dipropagasikan antara Telegram, gateway, dan Node?">
    Pesan Telegram ditangani oleh **gateway**. Gateway menjalankan agen dan
    baru kemudian memanggil Node melalui **Gateway WebSocket** ketika tool node diperlukan:

    Telegram → Gateway → Agen → `node.*` → Node → Gateway → Telegram

    Node tidak melihat lalu lintas penyedia yang masuk; mereka hanya menerima panggilan RPC node.

  </Accordion>

  <Accordion title="Bagaimana agen saya dapat mengakses komputer saya jika Gateway di-host secara remote?">
    Jawaban singkat: **pasangkan komputer Anda sebagai Node**. Gateway berjalan di tempat lain, tetapi dapat
    memanggil tool `node.*` (layar, kamera, sistem) pada mesin lokal Anda melalui Gateway WebSocket.

    Penyiapan umum:

    1. Jalankan Gateway di host yang selalu aktif (VPS/server rumahan).
    2. Masukkan host Gateway + komputer Anda ke tailnet yang sama.
    3. Pastikan WS Gateway dapat dijangkau (bind tailnet atau tunnel SSH).
    4. Buka app macOS secara lokal dan hubungkan dalam mode **Remote over SSH** (atau tailnet langsung)
       agar dapat terdaftar sebagai Node.
    5. Setujui Node di Gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Tidak diperlukan bridge TCP terpisah; Node terhubung melalui Gateway WebSocket.

    Pengingat keamanan: memasangkan Node macOS memungkinkan `system.run` pada mesin itu. Pasangkan hanya
    perangkat yang Anda percayai, dan tinjau [Security](/id/gateway/security).

    Docs: [Nodes](/id/nodes), [Protokol Gateway](/id/gateway/protocol), [Mode remote macOS](/id/platforms/mac/remote), [Security](/id/gateway/security).

  </Accordion>

  <Accordion title="Tailscale terhubung tetapi saya tidak mendapat balasan. Sekarang apa?">
    Periksa dasar-dasarnya:

    - Gateway berjalan: `openclaw gateway status`
    - Kesehatan Gateway: `openclaw status`
    - Kesehatan channel: `openclaw channels status`

    Lalu verifikasi auth dan routing:

    - Jika Anda menggunakan Tailscale Serve, pastikan `gateway.auth.allowTailscale` disetel dengan benar.
    - Jika Anda terhubung melalui tunnel SSH, pastikan tunnel lokal aktif dan mengarah ke port yang benar.
    - Pastikan allowlist Anda (DM atau grup) mencakup akun Anda.

    Docs: [Tailscale](/id/gateway/tailscale), [Akses jarak jauh](/id/gateway/remote), [Channels](/id/channels).

  </Accordion>

  <Accordion title="Bisakah dua instance OpenClaw saling berbicara (lokal + VPS)?">
    Ya. Tidak ada bridge "bot-ke-bot" bawaan, tetapi Anda dapat menghubungkannya dengan beberapa
    cara yang andal:

    **Paling sederhana:** gunakan channel chat normal yang dapat diakses kedua bot (Telegram/Slack/WhatsApp).
    Minta Bot A mengirim pesan ke Bot B, lalu biarkan Bot B membalas seperti biasa.

    **Bridge CLI (generik):** jalankan skrip yang memanggil Gateway lain dengan
    `openclaw agent --message ... --deliver`, menargetkan chat tempat bot lain tersebut
    mendengarkan. Jika salah satu bot berada di VPS remote, arahkan CLI Anda ke Gateway remote itu
    melalui SSH/Tailscale (lihat [Akses jarak jauh](/id/gateway/remote)).

    Contoh pola (jalankan dari mesin yang dapat menjangkau Gateway target):

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Tip: tambahkan guardrail agar kedua bot tidak berulang tanpa henti (khusus mention, channel
    allowlist, atau aturan "jangan balas pesan bot").

    Docs: [Akses jarak jauh](/id/gateway/remote), [CLI Agen](/cli/agent), [Pengiriman agen](/id/tools/agent-send).

  </Accordion>

  <Accordion title="Apakah saya memerlukan VPS terpisah untuk beberapa agen?">
    Tidak. Satu Gateway dapat meng-host beberapa agen, masing-masing dengan workspace, model default,
    dan routingnya sendiri. Itulah penyiapan normal dan jauh lebih murah serta lebih sederhana daripada menjalankan
    satu VPS per agen.

    Gunakan VPS terpisah hanya jika Anda memerlukan isolasi keras (batas keamanan) atau
    config yang sangat berbeda yang tidak ingin Anda bagikan. Jika tidak, cukup gunakan satu Gateway dan
    beberapa agen atau sub-agent.

  </Accordion>

  <Accordion title="Apakah ada manfaat menggunakan Node di laptop pribadi saya alih-alih SSH dari VPS?">
    Ya - Node adalah cara kelas satu untuk menjangkau laptop Anda dari Gateway remote, dan mereka
    membuka lebih dari sekadar akses shell. Gateway berjalan di macOS/Linux (Windows via WSL2) dan
    ringan (VPS kecil atau perangkat kelas Raspberry Pi sudah cukup; RAM 4 GB sudah lebih dari cukup), jadi penyiapan
    umum adalah host yang selalu aktif ditambah laptop Anda sebagai Node.

    - **Tidak perlu SSH masuk.** Node terhubung keluar ke Gateway WebSocket dan menggunakan pairing perangkat.
    - **Kontrol eksekusi yang lebih aman.** `system.run` dibatasi oleh allowlist/persetujuan node di laptop tersebut.
    - **Lebih banyak tool perangkat.** Node mengekspos `canvas`, `camera`, dan `screen` selain `system.run`.
    - **Otomatisasi browser lokal.** Simpan Gateway di VPS, tetapi jalankan Chrome secara lokal melalui host node di laptop, atau hubungkan ke Chrome lokal di host melalui Chrome MCP.

    SSH baik untuk akses shell ad-hoc, tetapi Node lebih sederhana untuk alur kerja agen yang berkelanjutan dan
    otomatisasi perangkat.

    Docs: [Nodes](/id/nodes), [CLI Nodes](/cli/nodes), [Browser](/id/tools/browser).

  </Accordion>

  <Accordion title="Apakah Node menjalankan service gateway?">
    Tidak. Hanya **satu gateway** yang seharusnya berjalan per host kecuali Anda sengaja menjalankan profil terisolasi (lihat [Beberapa gateway](/id/gateway/multiple-gateways)). Node adalah periferal yang terhubung
    ke gateway (Node iOS/Android, atau "mode node" macOS di app menubar). Untuk host Node headless
    dan kontrol CLI, lihat [CLI host Node](/cli/node).

    Restart penuh diperlukan untuk perubahan `gateway`, `discovery`, dan `canvasHost`.

  </Accordion>

  <Accordion title="Apakah ada cara API / RPC untuk menerapkan config?">
    Ya.

    - `config.schema.lookup`: periksa satu subtree config dengan node schema dangkal, petunjuk UI yang cocok, dan ringkasan child langsung sebelum menulis
    - `config.get`: ambil snapshot + hash saat ini
    - `config.patch`: pembaruan parsial yang aman (disarankan untuk sebagian besar edit RPC); hot-reload bila memungkinkan dan restart bila diperlukan
    - `config.apply`: validasi + ganti seluruh config; hot-reload bila memungkinkan dan restart bila diperlukan
    - Tool runtime `gateway` khusus owner tetap menolak penulisan ulang `tools.exec.ask` / `tools.exec.security`; alias lama `tools.bash.*` dinormalisasi ke path exec terlindungi yang sama

  </Accordion>

  <Accordion title="Config minimal yang masuk akal untuk instalasi pertama">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Ini menetapkan workspace Anda dan membatasi siapa yang dapat memicu bot.

  </Accordion>

  <Accordion title="Bagaimana cara menyiapkan Tailscale di VPS dan terhubung dari Mac saya?">
    Langkah minimal:

    1. **Instal + login di VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Instal + login di Mac Anda**
       - Gunakan app Tailscale dan masuk ke tailnet yang sama.
    3. **Aktifkan MagicDNS (disarankan)**
       - Di konsol admin Tailscale, aktifkan MagicDNS agar VPS memiliki nama yang stabil.
    4. **Gunakan hostname tailnet**
       - SSH: `ssh user@your-vps.tailnet-xxxx.ts.net`
       - Gateway WS: `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Jika Anda menginginkan Control UI tanpa SSH, gunakan Tailscale Serve di VPS:

    ```bash
    openclaw gateway --tailscale serve
    ```

    Ini menjaga gateway tetap terikat ke loopback dan mengekspos HTTPS melalui Tailscale. Lihat [Tailscale](/id/gateway/tailscale).

  </Accordion>

  <Accordion title="Bagaimana cara menghubungkan Node Mac ke Gateway remote (Tailscale Serve)?">
    Serve mengekspos **Gateway Control UI + WS**. Node terhubung melalui endpoint WS Gateway yang sama.

    Penyiapan yang disarankan:

    1. **Pastikan VPS + Mac berada di tailnet yang sama**.
    2. **Gunakan app macOS dalam mode Remote** (target SSH dapat berupa hostname tailnet).
       App akan membuat tunnel untuk port Gateway dan terhubung sebagai Node.
    3. **Setujui Node** di gateway:

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Docs: [Protokol Gateway](/id/gateway/protocol), [Discovery](/id/gateway/discovery), [Mode remote macOS](/id/platforms/mac/remote).

  </Accordion>

  <Accordion title="Haruskah saya menginstal di laptop kedua atau cukup menambahkan Node?">
    Jika Anda hanya membutuhkan **tool lokal** (layar/kamera/exec) di laptop kedua, tambahkan sebagai
    **Node**. Itu mempertahankan satu Gateway dan menghindari duplikasi config. Tool Node lokal
    saat ini hanya khusus macOS, tetapi kami berencana memperluasnya ke OS lain.

    Instal Gateway kedua hanya ketika Anda memerlukan **isolasi keras** atau dua bot yang sepenuhnya terpisah.

    Docs: [Nodes](/id/nodes), [CLI Nodes](/cli/nodes), [Beberapa gateway](/id/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Env vars dan pemuatan .env

<AccordionGroup>
  <Accordion title="Bagaimana OpenClaw memuat env vars?">
    OpenClaw membaca env vars dari proses induk (shell, launchd/systemd, CI, dll.) dan juga memuat:

    - `.env` dari direktori kerja saat ini
    - fallback `.env` global dari `~/.openclaw/.env` (alias `$OPENCLAW_STATE_DIR/.env`)

    Kedua file `.env` tidak menggantikan env vars yang sudah ada.

    Anda juga dapat mendefinisikan env vars inline di config (hanya diterapkan jika tidak ada di env proses):

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Lihat [/environment](/id/help/environment) untuk prioritas penuh dan sumber-sumbernya.

  </Accordion>

  <Accordion title="Saya memulai Gateway melalui service dan env vars saya hilang. Sekarang apa?">
    Dua perbaikan umum:

    1. Letakkan kunci yang hilang di `~/.openclaw/.env` agar tetap diambil meskipun service tidak mewarisi env shell Anda.
    2. Aktifkan impor shell (kemudahan opsional):

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Ini menjalankan shell login Anda dan hanya mengimpor kunci yang diharapkan tetapi belum ada (tidak pernah mengganti). Ekuivalen env var:
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='Saya menetapkan COPILOT_GITHUB_TOKEN, tetapi models status menampilkan "Shell env: off." Mengapa?'>
    `openclaw models status` melaporkan apakah **impor env shell** diaktifkan. "Shell env: off"
    **tidak** berarti env vars Anda hilang - itu hanya berarti OpenClaw tidak akan memuat
    shell login Anda secara otomatis.

    Jika Gateway berjalan sebagai service (launchd/systemd), Gateway tidak akan mewarisi
    lingkungan shell Anda. Perbaiki dengan salah satu cara berikut:

    1. Letakkan token di `~/.openclaw/.env`:

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Atau aktifkan impor shell (`env.shellEnv.enabled: true`).
    3. Atau tambahkan ke blok `env` config Anda (hanya berlaku jika belum ada).

    Lalu restart gateway dan periksa ulang:

    ```bash
    openclaw models status
    ```

    Token Copilot dibaca dari `COPILOT_GITHUB_TOKEN` (juga `GH_TOKEN` / `GITHUB_TOKEN`).
    Lihat [/concepts/model-providers](/id/concepts/model-providers) dan [/environment](/id/help/environment).

  </Accordion>
</AccordionGroup>

## Sesi dan beberapa chat

<AccordionGroup>
  <Accordion title="Bagaimana cara memulai percakapan baru?">
    Kirim `/new` atau `/reset` sebagai pesan mandiri. Lihat [Manajemen sesi](/id/concepts/session).
  </Accordion>

  <Accordion title="Apakah sesi direset secara otomatis jika saya tidak pernah mengirim /new?">
    Sesi dapat kedaluwarsa setelah `session.idleMinutes`, tetapi ini **dinonaktifkan secara default** (default **0**).
    Tetapkan nilainya ke bilangan positif untuk mengaktifkan kedaluwarsa idle. Saat diaktifkan, pesan **berikutnya**
    setelah periode idle akan memulai ID sesi baru untuk kunci chat tersebut.
    Ini tidak menghapus transkrip - hanya memulai sesi baru.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Apakah ada cara untuk membuat tim instance OpenClaw (satu CEO dan banyak agen)?">
    Ya, melalui **routing multi-agent** dan **sub-agent**. Anda dapat membuat satu agen
    koordinator dan beberapa agen worker dengan workspace dan model mereka sendiri.

    Meski demikian, ini sebaiknya dipandang sebagai **eksperimen yang menyenangkan**. Ini memakan banyak token dan sering
    kurang efisien dibanding menggunakan satu bot dengan sesi terpisah. Model tipikal yang kami
    bayangkan adalah satu bot yang Anda ajak bicara, dengan sesi berbeda untuk pekerjaan paralel. Bot itu
    juga dapat memunculkan sub-agent saat diperlukan.

    Docs: [Routing multi-agent](/id/concepts/multi-agent), [Sub-agent](/id/tools/subagents), [CLI Agen](/cli/agents).

  </Accordion>

  <Accordion title="Mengapa konteks terpotong di tengah tugas? Bagaimana cara mencegahnya?">
    Konteks sesi dibatasi oleh jendela model. Chat panjang, output tool besar, atau banyak
    file dapat memicu Compaction atau pemotongan.

    Yang membantu:

    - Minta bot merangkum state saat ini dan menuliskannya ke file.
    - Gunakan `/compact` sebelum tugas panjang, dan `/new` saat berganti topik.
    - Simpan konteks penting di workspace dan minta bot membacanya kembali.
    - Gunakan sub-agent untuk pekerjaan panjang atau paralel agar chat utama tetap lebih kecil.
    - Pilih model dengan jendela konteks lebih besar jika ini sering terjadi.

  </Accordion>

  <Accordion title="Bagaimana cara mereset OpenClaw sepenuhnya tetapi tetap mempertahankan instalasinya?">
    Gunakan perintah reset:

    ```bash
    openclaw reset
    ```

    Reset penuh non-interaktif:

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Lalu jalankan ulang penyiapan:

    ```bash
    openclaw onboard --install-daemon
    ```

    Catatan:

    - Onboarding juga menawarkan **Reset** jika mendeteksi config yang sudah ada. Lihat [Onboarding (CLI)](/id/start/wizard).
    - Jika Anda menggunakan profil (`--profile` / `OPENCLAW_PROFILE`), reset setiap direktori state (default-nya `~/.openclaw-<profile>`).
    - Reset dev: `openclaw gateway --dev --reset` (khusus dev; menghapus config dev + kredensial + sesi + workspace).

  </Accordion>

  <Accordion title='Saya mendapatkan error "context too large" - bagaimana cara mereset atau melakukan compact?'>
    Gunakan salah satu dari ini:

    - **Compact** (mempertahankan percakapan tetapi merangkum giliran yang lebih lama):

      ```
      /compact
      ```

      atau `/compact <instructions>` untuk memandu ringkasan.

    - **Reset** (ID sesi baru untuk kunci chat yang sama):

      ```
      /new
      /reset
      ```

    Jika ini terus terjadi:

    - Aktifkan atau sesuaikan **pruning sesi** (`agents.defaults.contextPruning`) untuk memangkas output tool lama.
    - Gunakan model dengan jendela konteks lebih besar.

    Docs: [Compaction](/id/concepts/compaction), [Pruning sesi](/id/concepts/session-pruning), [Manajemen sesi](/id/concepts/session).

  </Accordion>

  <Accordion title='Mengapa saya melihat "LLM request rejected: messages.content.tool_use.input field required"?'>
    Ini adalah error validasi penyedia: model mengeluarkan blok `tool_use` tanpa
    `input` yang diperlukan. Biasanya ini berarti riwayat sesi sudah basi atau rusak (sering setelah thread panjang
    atau perubahan tool/schema).

    Perbaikan: mulai sesi baru dengan `/new` (pesan mandiri).

  </Accordion>

  <Accordion title="Mengapa saya mendapat pesan heartbeat setiap 30 menit?">
    Heartbeat berjalan setiap **30m** secara default (**1h** saat menggunakan auth OAuth). Sesuaikan atau nonaktifkan:

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // atau "0m" untuk menonaktifkan
          },
        },
      },
    }
    ```

    Jika `HEARTBEAT.md` ada tetapi secara efektif kosong (hanya baris kosong dan header
    markdown seperti `# Heading`), OpenClaw melewati eksekusi heartbeat untuk menghemat panggilan API.
    Jika file tidak ada, heartbeat tetap berjalan dan model memutuskan apa yang harus dilakukan.

    Override per agen menggunakan `agents.list[].heartbeat`. Docs: [Heartbeat](/id/gateway/heartbeat).

  </Accordion>

  <Accordion title='Apakah saya perlu menambahkan "akun bot" ke grup WhatsApp?'>
    Tidak. OpenClaw berjalan di **akun Anda sendiri**, jadi jika Anda berada di grup, OpenClaw dapat melihatnya.
    Secara default, balasan grup diblokir sampai Anda mengizinkan pengirim (`groupPolicy: "allowlist"`).

    Jika Anda ingin hanya **Anda** yang dapat memicu balasan grup:

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Bagaimana cara mendapatkan JID grup WhatsApp?">
    Opsi 1 (tercepat): ikuti log dan kirim pesan uji di grup:

    ```bash
    openclaw logs --follow --json
    ```

    Cari `chatId` (atau `from`) yang berakhiran `@g.us`, seperti:
    `1234567890-1234567890@g.us`.

    Opsi 2 (jika sudah dikonfigurasi/di-allowlist): daftar grup dari config:

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Docs: [WhatsApp](/id/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Mengapa OpenClaw tidak membalas di grup?">
    Dua penyebab umum:

    - Pembatasan mention aktif (default). Anda harus @mention bot (atau cocok dengan `mentionPatterns`).
    - Anda mengonfigurasi `channels.whatsapp.groups` tanpa `"*"` dan grup tersebut tidak ada di allowlist.

    Lihat [Grup](/id/channels/groups) dan [Pesan grup](/id/channels/group-messages).

  </Accordion>

  <Accordion title="Apakah grup/thread berbagi konteks dengan DM?">
    Chat langsung digabungkan ke sesi utama secara default. Grup/channel memiliki kunci sesi mereka sendiri, dan topik Telegram / thread Discord adalah sesi yang terpisah. Lihat [Grup](/id/channels/groups) dan [Pesan grup](/id/channels/group-messages).
  </Accordion>

  <Accordion title="Berapa banyak workspace dan agen yang bisa saya buat?">
    Tidak ada batas keras. Puluhan (bahkan ratusan) tidak masalah, tetapi perhatikan:

    - **Pertumbuhan disk:** sesi + transkrip berada di bawah `~/.openclaw/agents/<agentId>/sessions/`.
    - **Biaya token:** lebih banyak agen berarti lebih banyak penggunaan model secara bersamaan.
    - **Beban operasional:** profil auth, workspace, dan routing channel per agen.

    Tip:

    - Pertahankan satu workspace **aktif** per agen (`agents.defaults.workspace`).
    - Pangkas sesi lama (hapus entri JSONL atau store) jika disk bertambah.
    - Gunakan `openclaw doctor` untuk menemukan workspace liar dan ketidakcocokan profil.

  </Accordion>

  <Accordion title="Bisakah saya menjalankan beberapa bot atau chat pada saat yang sama (Slack), dan bagaimana saya harus menyiapkannya?">
    Ya. Gunakan **Routing Multi-Agent** untuk menjalankan beberapa agen terisolasi dan merutekan pesan masuk berdasarkan
    channel/akun/peer. Slack didukung sebagai channel dan dapat diikat ke agen tertentu.

    Akses browser sangat kuat tetapi bukan berarti "bisa melakukan apa pun yang bisa dilakukan manusia" - anti-bot, CAPTCHA, dan MFA tetap
    dapat memblokir otomatisasi. Untuk kontrol browser yang paling andal, gunakan Chrome MCP lokal di host,
    atau gunakan CDP di mesin yang benar-benar menjalankan browser.

    Penyiapan praktik terbaik:

    - Host Gateway yang selalu aktif (VPS/Mac mini).
    - Satu agen per peran (binding).
    - Channel Slack yang diikat ke agen-agen tersebut.
    - Browser lokal melalui Chrome MCP atau Node saat diperlukan.

    Docs: [Routing Multi-Agent](/id/concepts/multi-agent), [Slack](/id/channels/slack),
    [Browser](/id/tools/browser), [Nodes](/id/nodes).

  </Accordion>
</AccordionGroup>

## Model: default, pemilihan, alias, peralihan

<AccordionGroup>
  <Accordion title='Apa itu "model default"?'>
    Model default OpenClaw adalah apa pun yang Anda tetapkan sebagai:

    ```
    agents.defaults.model.primary
    ```

    Model dirujuk sebagai `provider/model` (contoh: `openai/gpt-5.4`). Jika Anda menghilangkan provider, OpenClaw pertama-tama mencoba alias, lalu kecocokan provider yang dikonfigurasi secara unik untuk model id yang persis sama, dan baru setelah itu kembali ke provider default yang dikonfigurasi sebagai jalur kompatibilitas lama. Jika provider tersebut tidak lagi mengekspos model default yang dikonfigurasi, OpenClaw akan fallback ke provider/model pertama yang dikonfigurasi alih-alih menampilkan default provider yang usang dan sudah dihapus. Anda tetap harus **secara eksplisit** menetapkan `provider/model`.

  </Accordion>

  <Accordion title="Model apa yang Anda rekomendasikan?">
    **Default yang direkomendasikan:** gunakan model generasi terbaru terkuat yang tersedia di stack penyedia Anda.
    **Untuk agen dengan tool aktif atau input tak tepercaya:** prioritaskan kekuatan model dibanding biaya.
    **Untuk chat rutin/berisiko rendah:** gunakan model fallback yang lebih murah dan rute berdasarkan peran agen.

    MiniMax memiliki docs tersendiri: [MiniMax](/id/providers/minimax) dan
    [Model lokal](/id/gateway/local-models).

    Aturan praktis: gunakan **model terbaik yang sanggup Anda bayar** untuk pekerjaan berisiko tinggi, dan model yang lebih murah
    untuk chat rutin atau ringkasan. Anda dapat merutekan model per agen dan menggunakan sub-agent untuk
    memparalelkan tugas panjang (setiap sub-agent mengonsumsi token). Lihat [Models](/id/concepts/models) dan
    [Sub-agent](/id/tools/subagents).

    Peringatan keras: model yang lebih lemah/terlalu dikuantisasi lebih rentan terhadap injeksi prompt
    dan perilaku tidak aman. Lihat [Security](/id/gateway/security).

    Konteks lebih lanjut: [Models](/id/concepts/models).

  </Accordion>

  <Accordion title="Bagaimana cara mengganti model tanpa menghapus config saya?">
    Gunakan **perintah model** atau edit hanya field **model**. Hindari penggantian config penuh.

    Opsi aman:

    - `/model` di chat (cepat, per sesi)
    - `openclaw models set ...` (hanya memperbarui config model)
    - `openclaw configure --section model` (interaktif)
    - edit `agents.defaults.model` di `~/.openclaw/openclaw.json`

    Hindari `config.apply` dengan objek parsial kecuali Anda memang ingin mengganti seluruh config.
    Untuk edit RPC, periksa dulu dengan `config.schema.lookup` dan lebih pilih `config.patch`. Payload lookup memberi Anda path yang dinormalisasi, docs/kendala schema dangkal, dan ringkasan child langsung
    untuk pembaruan parsial.
    Jika Anda memang menimpa config, pulihkan dari cadangan atau jalankan ulang `openclaw doctor` untuk memperbaikinya.

    Docs: [Models](/id/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/id/gateway/doctor).

  </Accordion>

  <Accordion title="Bisakah saya menggunakan model self-hosted (llama.cpp, vLLM, Ollama)?">
    Ya. Ollama adalah jalur termudah untuk model lokal.

    Penyiapan tercepat:

    1. Instal Ollama dari `https://ollama.com/download`
    2. Tarik model lokal seperti `ollama pull gemma4`
    3. Jika Anda juga menginginkan model cloud, jalankan `ollama signin`
    4. Jalankan `openclaw onboard` dan pilih `Ollama`
    5. Pilih `Local` atau `Cloud + Local`

    Catatan:

    - `Cloud + Local` memberi Anda model cloud plus model Ollama lokal Anda
    - model cloud seperti `kimi-k2.5:cloud` tidak memerlukan penarikan lokal
    - untuk peralihan manual, gunakan `openclaw models list` dan `openclaw models set ollama/<model>`

    Catatan keamanan: model yang lebih kecil atau sangat dikuantisasi lebih rentan terhadap injeksi prompt.
    Kami sangat merekomendasikan **model besar** untuk bot apa pun yang dapat menggunakan tool.
    Jika Anda tetap menginginkan model kecil, aktifkan sandboxing dan allowlist tool yang ketat.

    Docs: [Ollama](/id/providers/ollama), [Model lokal](/id/gateway/local-models),
    [Penyedia model](/id/concepts/model-providers), [Security](/id/gateway/security),
    [Sandboxing](/id/gateway/sandboxing).

  </Accordion>

  <Accordion title="Model apa yang digunakan OpenClaw, Flawd, dan Krill?">
    - Deployment ini bisa berbeda dan dapat berubah seiring waktu; tidak ada rekomendasi provider yang tetap.
    - Periksa pengaturan runtime saat ini di setiap gateway dengan `openclaw models status`.
    - Untuk agen yang sensitif terhadap keamanan/menggunakan tool, gunakan model generasi terbaru terkuat yang tersedia.
  </Accordion>

  <Accordion title="Bagaimana cara mengganti model dengan cepat (tanpa restart)?">
    Gunakan perintah `/model` sebagai pesan mandiri:

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Ini adalah alias bawaan. Alias kustom dapat ditambahkan melalui `agents.defaults.models`.

    Anda dapat menampilkan model yang tersedia dengan `/model`, `/model list`, atau `/model status`.

    `/model` (dan `/model list`) menampilkan pemilih ringkas bernomor. Pilih berdasarkan nomor:

    ```
    /model 3
    ```

    Anda juga dapat memaksa profil auth tertentu untuk provider tersebut (per sesi):

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Tip: `/model status` menampilkan agen mana yang aktif, file `auth-profiles.json` mana yang sedang digunakan, dan profil auth mana yang akan dicoba berikutnya.
    Fitur ini juga menampilkan endpoint provider yang dikonfigurasi (`baseUrl`) dan mode API (`api`) bila tersedia.

    **Bagaimana cara melepas pin profil yang saya tetapkan dengan @profile?**

    Jalankan ulang `/model` **tanpa** akhiran `@profile`:

    ```
    /model anthropic/claude-opus-4-6
    ```

    Jika Anda ingin kembali ke default, pilih dari `/model` (atau kirim `/model <provider/model default>`).
    Gunakan `/model status` untuk memastikan profil auth mana yang aktif.

  </Accordion>

  <Accordion title="Bisakah saya menggunakan GPT 5.2 untuk tugas harian dan Codex 5.3 untuk coding?">
    Ya. Tetapkan salah satu sebagai default dan ganti sesuai kebutuhan:

    - **Peralihan cepat (per sesi):** `/model gpt-5.4` untuk tugas harian, `/model openai-codex/gpt-5.4` untuk coding dengan OAuth Codex.
    - **Default + ganti:** tetapkan `agents.defaults.model.primary` ke `openai/gpt-5.4`, lalu ganti ke `openai-codex/gpt-5.4` saat coding (atau sebaliknya).
    - **Sub-agent:** rute tugas coding ke sub-agent dengan model default yang berbeda.

    Lihat [Models](/id/concepts/models) dan [Perintah slash](/id/tools/slash-commands).

  </Accordion>

  <Accordion title="Bagaimana cara mengonfigurasi mode cepat untuk GPT 5.4?">
    Gunakan toggle sesi atau default config:

    - **Per sesi:** kirim `/fast on` saat sesi menggunakan `openai/gpt-5.4` atau `openai-codex/gpt-5.4`.
    - **Default per model:** tetapkan `agents.defaults.models["openai/gpt-5.4"].params.fastMode` ke `true`.
    - **OAuth Codex juga:** jika Anda juga menggunakan `openai-codex/gpt-5.4`, tetapkan flag yang sama di sana.

    Contoh:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    Untuk OpenAI, mode cepat dipetakan ke `service_tier = "priority"` pada permintaan Responses native yang didukung. Override sesi `/fast` mengalahkan default config.

    Lihat [Thinking and fast mode](/id/tools/thinking) dan [Mode cepat OpenAI](/id/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Mengapa saya melihat "Model ... is not allowed" lalu tidak ada balasan?'>
    Jika `agents.defaults.models` disetel, itu menjadi **allowlist** untuk `/model` dan semua
    override sesi. Memilih model yang tidak ada di daftar itu akan mengembalikan:

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Error itu dikembalikan **sebagai pengganti** balasan normal. Perbaikan: tambahkan model tersebut ke
    `agents.defaults.models`, hapus allowlist, atau pilih model dari `/model list`.

  </Accordion>

  <Accordion title='Mengapa saya melihat "Unknown model: minimax/MiniMax-M2.7"?'>
    Ini berarti **provider belum dikonfigurasi** (tidak ditemukan config provider MiniMax atau
    profil auth), sehingga model tidak dapat diselesaikan.

    Checklist perbaikan:

    1. Upgrade ke rilis OpenClaw saat ini (atau jalankan dari source `main`), lalu restart gateway.
    2. Pastikan MiniMax dikonfigurasi (wizard atau JSON), atau auth MiniMax
       ada di env/profil auth sehingga provider yang cocok dapat disuntikkan
       (`MINIMAX_API_KEY` untuk `minimax`, `MINIMAX_OAUTH_TOKEN` atau MiniMax
       OAuth tersimpan untuk `minimax-portal`).
    3. Gunakan model id yang persis sama (case-sensitive) untuk jalur auth Anda:
       `minimax/MiniMax-M2.7` atau `minimax/MiniMax-M2.7-highspeed` untuk penyiapan
       kunci API, atau `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` untuk penyiapan OAuth.
    4. Jalankan:

       ```bash
       openclaw models list
       ```

       dan pilih dari daftar (atau `/model list` di chat).

    Lihat [MiniMax](/id/providers/minimax) dan [Models](/id/concepts/models).

  </Accordion>

  <Accordion title="Bisakah saya menggunakan MiniMax sebagai default dan OpenAI untuk tugas kompleks?">
    Ya. Gunakan **MiniMax sebagai default** dan ganti model **per sesi** saat diperlukan.
    Fallback digunakan untuk **error**, bukan "tugas sulit," jadi gunakan `/model` atau agen terpisah.

    **Opsi A: ganti per sesi**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Lalu:

    ```
    /model gpt
    ```

    **Opsi B: agen terpisah**

    - Default Agen A: MiniMax
    - Default Agen B: OpenAI
    - Rute berdasarkan agen atau gunakan `/agent` untuk berpindah

    Docs: [Models](/id/concepts/models), [Routing Multi-Agent](/id/concepts/multi-agent), [MiniMax](/id/providers/minimax), [OpenAI](/id/providers/openai).

  </Accordion>

  <Accordion title="Apakah `opus` / `sonnet` / `gpt` merupakan shortcut bawaan?">
    Ya. OpenClaw menyediakan beberapa singkatan default (hanya diterapkan ketika model tersebut ada di `agents.defaults.models`):

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Jika Anda menetapkan alias Anda sendiri dengan nama yang sama, nilai Anda yang akan digunakan.

  </Accordion>

  <Accordion title="Bagaimana cara mendefinisikan/override shortcut model (alias)?">
    Alias berasal dari `agents.defaults.models.<modelId>.alias`. Contoh:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Lalu `/model sonnet` (atau `/<alias>` saat didukung) akan diselesaikan ke model ID tersebut.

  </Accordion>

  <Accordion title="Bagaimana cara menambahkan model dari provider lain seperti OpenRouter atau Z.AI?">
    OpenRouter (bayar per token; banyak model):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (model GLM):

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    Jika Anda merujuk `provider/model` tetapi kunci provider yang diperlukan tidak ada, Anda akan mendapatkan error auth runtime (misalnya `No API key found for provider "zai"`).

    **No API key found for provider setelah menambahkan agen baru**

    Ini biasanya berarti **agen baru** memiliki penyimpanan auth yang kosong. Auth bersifat per agen dan
    disimpan di:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    Opsi perbaikan:

    - Jalankan `openclaw agents add <id>` dan konfigurasikan auth selama wizard.
    - Atau salin `auth-profiles.json` dari `agentDir` agen utama ke `agentDir` agen baru.

    **Jangan** menggunakan ulang `agentDir` di beberapa agen; hal itu menyebabkan benturan auth/sesi.

  </Accordion>
</AccordionGroup>

## Failover model dan "All models failed"

<AccordionGroup>
  <Accordion title="Bagaimana cara kerja failover?">
    Failover terjadi dalam dua tahap:

    1. **Rotasi profil auth** dalam provider yang sama.
    2. **Fallback model** ke model berikutnya di `agents.defaults.model.fallbacks`.

    Cooldown diterapkan pada profil yang gagal (exponential backoff), sehingga OpenClaw dapat terus merespons bahkan saat provider terkena rate limit atau gagal sementara.

    Bucket rate limit mencakup lebih dari sekadar respons `429`. OpenClaw
    juga memperlakukan pesan seperti `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted`, dan batas
    jendela penggunaan berkala (`weekly/monthly limit reached`) sebagai
    rate limit yang layak untuk failover.

    Beberapa respons yang tampak seperti penagihan bukan `402`, dan beberapa respons HTTP `402`
    juga tetap berada dalam bucket sementara itu. Jika provider mengembalikan
    teks penagihan eksplisit pada `401` atau `403`, OpenClaw tetap dapat menyimpannya
    di jalur penagihan, tetapi pencocok teks khusus provider tetap dibatasi pada
    provider yang memilikinya (misalnya OpenRouter `Key limit exceeded`). Jika pesan `402`
    justru tampak seperti jendela penggunaan yang dapat dicoba ulang atau
    batas pengeluaran organisasi/workspace (`daily limit reached, resets tomorrow`,
    `organization spending limit exceeded`), OpenClaw memperlakukannya sebagai
    `rate_limit`, bukan penonaktifan penagihan jangka panjang.

    Error luapan konteks berbeda: signature seperti
    `request_too_large`, `input exceeds the maximum number of tokens`,
    `input token count exceeds the maximum number of input tokens`,
    `input is too long for the model`, atau `ollama error: context length
    exceeded` tetap berada di jalur Compaction/percobaan ulang alih-alih memajukan model
    fallback.

    Teks error server generik sengaja dibuat lebih sempit daripada "apa pun yang
    mengandung unknown/error". OpenClaw memang memperlakukan bentuk sementara yang dibatasi provider
    seperti Anthropic `An unknown error occurred` polos, OpenRouter polos
    `Provider returned error`, error stop-reason seperti `Unhandled stop reason:
    error`, payload JSON `api_error` dengan teks server sementara
    (`internal server error`, `unknown error, 520`, `upstream error`, `backend
    error`), dan error provider sibuk seperti `ModelNotReadyException` sebagai
    sinyal timeout/kelebihan beban yang layak untuk failover ketika konteks provider
    cocok.
    Teks fallback internal generik seperti `LLM request failed with an unknown
    error.` tetap konservatif dan tidak memicu model fallback dengan sendirinya.

  </Accordion>

  <Accordion title='Apa arti "No credentials found for profile anthropic:default"?'>
    Itu berarti sistem mencoba menggunakan ID profil auth `anthropic:default`, tetapi tidak dapat menemukan kredensial untuk profil tersebut di penyimpanan auth yang diharapkan.

    **Checklist perbaikan:**

    - **Pastikan lokasi profil auth** (path baru vs lama)
      - Saat ini: `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - Lama: `~/.openclaw/agent/*` (dimigrasikan oleh `openclaw doctor`)
    - **Pastikan env var Anda dimuat oleh Gateway**
      - Jika Anda menetapkan `ANTHROPIC_API_KEY` di shell tetapi menjalankan Gateway melalui systemd/launchd, env tersebut mungkin tidak diwarisi. Letakkan di `~/.openclaw/.env` atau aktifkan `env.shellEnv`.
    - **Pastikan Anda mengedit agen yang benar**
      - Penyiapan multi-agent berarti bisa ada beberapa file `auth-profiles.json`.
    - **Lakukan pemeriksaan dasar status model/auth**
      - Gunakan `openclaw models status` untuk melihat model yang dikonfigurasi dan apakah provider telah diautentikasi.

    **Checklist perbaikan untuk "No credentials found for profile anthropic"**

    Ini berarti eksekusi dipin ke profil auth Anthropic, tetapi Gateway
    tidak dapat menemukannya di penyimpanan auth.

    - **Gunakan Claude CLI**
      - Jalankan `openclaw models auth login --provider anthropic --method cli --set-default` di host gateway.
    - **Jika Anda ingin menggunakan kunci API sebagai gantinya**
      - Letakkan `ANTHROPIC_API_KEY` di `~/.openclaw/.env` pada **host gateway**.
      - Hapus urutan pin apa pun yang memaksa profil yang hilang:

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **Pastikan Anda menjalankan perintah di host gateway**
      - Dalam mode remote, profil auth berada di mesin gateway, bukan laptop Anda.

  </Accordion>

  <Accordion title="Mengapa OpenClaw juga mencoba Google Gemini lalu gagal?">
    Jika config model Anda menyertakan Google Gemini sebagai fallback (atau Anda beralih ke shorthand Gemini), OpenClaw akan mencobanya selama fallback model. Jika Anda belum mengonfigurasi kredensial Google, Anda akan melihat `No API key found for provider "google"`.

    Perbaikan: sediakan auth Google, atau hapus/hindari model Google di `agents.defaults.model.fallbacks` / alias agar fallback tidak diarahkan ke sana.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    Penyebab: riwayat sesi berisi **blok thinking tanpa signature** (sering dari
    aliran yang dibatalkan/parsial). Google Antigravity memerlukan signature untuk blok thinking.

    Perbaikan: OpenClaw sekarang menghapus blok thinking tanpa signature untuk Claude Google Antigravity. Jika masih muncul, mulai **sesi baru** atau tetapkan `/thinking off` untuk agen tersebut.

  </Accordion>
</AccordionGroup>

## Profil auth: apa itu dan bagaimana mengelolanya

Terkait: [/concepts/oauth](/id/concepts/oauth) (alur OAuth, penyimpanan token, pola multi-akun)

<AccordionGroup>
  <Accordion title="Apa itu profil auth?">
    Profil auth adalah catatan kredensial bernama (OAuth atau kunci API) yang terkait dengan provider. Profil disimpan di:

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="Apa contoh ID profil yang umum?">
    OpenClaw menggunakan ID berawalan provider seperti:

    - `anthropic:default` (umum ketika tidak ada identitas email)
    - `anthropic:<email>` untuk identitas OAuth
    - ID kustom yang Anda pilih (misalnya `anthropic:work`)

  </Accordion>

  <Accordion title="Bisakah saya mengontrol profil auth mana yang dicoba lebih dulu?">
    Ya. Config mendukung metadata opsional untuk profil dan pengurutan per provider (`auth.order.<provider>`). Ini **tidak** menyimpan secret; ini memetakan ID ke provider/mode dan menetapkan urutan rotasi.

    OpenClaw dapat melewati profil untuk sementara jika profil tersebut berada dalam **cooldown** singkat (rate limit/timeout/kegagalan auth) atau status **disabled** yang lebih lama (penagihan/kredit tidak cukup). Untuk memeriksanya, jalankan `openclaw models status --json` dan periksa `auth.unusableProfiles`. Penyesuaian: `auth.cooldowns.billingBackoffHours*`.

    Cooldown rate limit dapat dibatasi ke model. Profil yang sedang cooldown
    untuk satu model masih dapat digunakan untuk model saudara pada provider yang sama,
    sedangkan jendela penagihan/disabled tetap memblokir seluruh profil.

    Anda juga dapat menetapkan override urutan **per agen** (disimpan di `auth-state.json` agen tersebut) melalui CLI:

    ```bash
    # Default ke agen default yang dikonfigurasi (hilangkan --agent)
    openclaw models auth order get --provider anthropic

    # Kunci rotasi ke satu profil saja (hanya coba yang ini)
    openclaw models auth order set --provider anthropic anthropic:default

    # Atau tetapkan urutan eksplisit (fallback dalam provider)
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # Hapus override (kembali ke config auth.order / round-robin)
    openclaw models auth order clear --provider anthropic
    ```

    Untuk menargetkan agen tertentu:

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    Untuk memverifikasi apa yang benar-benar akan dicoba, gunakan:

    ```bash
    openclaw models status --probe
    ```

    Jika profil tersimpan tidak disertakan dalam urutan eksplisit, probe akan melaporkan
    `excluded_by_auth_order` untuk profil tersebut alih-alih mencobanya secara diam-diam.

  </Accordion>

  <Accordion title="Apa perbedaan OAuth dan kunci API?">
    OpenClaw mendukung keduanya:

    - **OAuth** sering memanfaatkan akses langganan (jika berlaku).
    - **Kunci API** menggunakan penagihan bayar per token.

    Wizard secara eksplisit mendukung Anthropic Claude CLI, OAuth OpenAI Codex, dan kunci API.

  </Accordion>
</AccordionGroup>

## Gateway: port, "already running", dan mode remote

<AccordionGroup>
  <Accordion title="Port apa yang digunakan Gateway?">
    `gateway.port` mengontrol satu port termultipleks untuk WebSocket + HTTP (Control UI, hook, dll.).

    Prioritas:

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > default 18789
    ```

  </Accordion>

  <Accordion title='Mengapa openclaw gateway status mengatakan "Runtime: running" tetapi "RPC probe: failed"?'>
    Karena "running" adalah pandangan **supervisor** (launchd/systemd/schtasks). Probe RPC adalah CLI yang benar-benar terhubung ke gateway WebSocket dan memanggil `status`.

    Gunakan `openclaw gateway status` dan percayai baris-baris ini:

    - `Probe target:` (URL yang benar-benar digunakan probe)
    - `Listening:` (apa yang benar-benar terikat pada port)
    - `Last gateway error:` (akar penyebab umum ketika proses hidup tetapi port tidak mendengarkan)

  </Accordion>

  <Accordion title='Mengapa openclaw gateway status menampilkan "Config (cli)" dan "Config (service)" berbeda?'>
    Anda sedang mengedit satu file config sementara service menjalankan file config lain (sering kali karena ketidakcocokan `--profile` / `OPENCLAW_STATE_DIR`).

    Perbaikan:

    ```bash
    openclaw gateway install --force
    ```

    Jalankan itu dari `--profile` / lingkungan yang sama yang ingin Anda gunakan untuk service.

  </Accordion>

  <Accordion title='Apa arti "another gateway instance is already listening"?'>
    OpenClaw memberlakukan kunci runtime dengan langsung mengikat listener WebSocket saat startup (default `ws://127.0.0.1:18789`). Jika pengikatan gagal dengan `EADDRINUSE`, OpenClaw melempar `GatewayLockError` yang menunjukkan instance lain sudah mendengarkan.

    Perbaikan: hentikan instance lain, kosongkan port, atau jalankan dengan `openclaw gateway --port <port>`.

  </Accordion>

  <Accordion title="Bagaimana cara menjalankan OpenClaw dalam mode remote (klien terhubung ke Gateway di tempat lain)?">
    Tetapkan `gateway.mode: "remote"` dan arahkan ke URL WebSocket remote, opsional dengan kredensial remote shared-secret:

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    Catatan:

    - `openclaw gateway` hanya mulai saat `gateway.mode` adalah `local` (atau Anda melewatkan flag override).
    - App macOS memantau file config dan beralih mode secara langsung saat nilai-nilai ini berubah.
    - `gateway.remote.token` / `.password` hanyalah kredensial remote sisi klien; keduanya tidak mengaktifkan auth gateway lokal dengan sendirinya.

  </Accordion>

  <Accordion title='Control UI mengatakan "unauthorized" (atau terus menyambung ulang). Sekarang apa?'>
    Jalur auth gateway Anda dan metode auth UI tidak cocok.

    Fakta (dari kode):

    - Control UI menyimpan token di `sessionStorage` untuk sesi tab browser saat ini dan URL gateway yang dipilih, sehingga refresh di tab yang sama tetap berfungsi tanpa memulihkan persistensi token `localStorage` jangka panjang.
    - Pada `AUTH_TOKEN_MISMATCH`, klien tepercaya dapat mencoba satu percobaan ulang terbatas dengan token perangkat yang di-cache ketika gateway mengembalikan petunjuk percobaan ulang (`canRetryWithDeviceToken=true`, `recommendedNextStep=retry_with_device_token`).
    - Percobaan ulang token cache itu sekarang menggunakan kembali scope yang disetujui dan disimpan bersama token perangkat tersebut. Pemanggil `deviceToken` eksplisit / `scopes` eksplisit tetap mempertahankan set scope yang diminta alih-alih mewarisi scope cache.
    - Di luar jalur percobaan ulang itu, prioritas auth koneksi adalah token/kata sandi bersama eksplisit terlebih dahulu, lalu `deviceToken` eksplisit, lalu token perangkat tersimpan, lalu token bootstrap.
    - Pemeriksaan scope token bootstrap memiliki awalan role. Allowlist operator bootstrap bawaan hanya memenuhi permintaan operator; Node atau role non-operator lainnya tetap memerlukan scope di bawah awalan role mereka sendiri.

    Perbaikan:

    - Paling cepat: `openclaw dashboard` (mencetak + menyalin URL dasbor, mencoba membukanya; menampilkan petunjuk SSH jika headless).
    - Jika Anda belum memiliki token: `openclaw doctor --generate-gateway-token`.
    - Jika remote, buat tunnel dulu: `ssh -N -L 18789:127.0.0.1:18789 user@host` lalu buka `http://127.0.0.1:18789/`.
    - Mode shared-secret: tetapkan `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` atau `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`, lalu tempel secret yang cocok di pengaturan Control UI.
    - Mode Tailscale Serve: pastikan `gateway.auth.allowTailscale` diaktifkan dan Anda membuka URL Serve, bukan URL loopback/tailnet mentah yang melewati header identitas Tailscale.
    - Mode trusted-proxy: pastikan Anda datang melalui proxy sadar identitas non-loopback yang dikonfigurasi, bukan proxy loopback host yang sama atau URL gateway mentah.
    - Jika ketidakcocokan tetap ada setelah satu kali percobaan ulang, putar/setujui ulang token perangkat yang dipasangkan:
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - Jika panggilan rotate tersebut mengatakan ditolak, periksa dua hal:
      - sesi perangkat yang dipasangkan hanya dapat memutar **perangkat mereka sendiri** kecuali mereka juga memiliki `operator.admin`
      - nilai `--scope` eksplisit tidak boleh melebihi scope operator pemanggil saat ini
    - Masih macet? Jalankan `openclaw status --all` dan ikuti [Pemecahan Masalah](/id/gateway/troubleshooting). Lihat [Dashboard](/web/dashboard) untuk detail auth.

  </Accordion>

  <Accordion title="Saya menetapkan gateway.bind tailnet tetapi tidak dapat bind dan tidak ada yang mendengarkan">
    Bind `tailnet` memilih IP Tailscale dari antarmuka jaringan Anda (100.64.0.0/10). Jika mesin tidak berada di Tailscale (atau antarmukanya mati), tidak ada alamat untuk di-bind.

    Perbaikan:

    - Jalankan Tailscale di host tersebut (agar memiliki alamat 100.x), atau
    - Beralih ke `gateway.bind: "loopback"` / `"lan"`.

    Catatan: `tailnet` bersifat eksplisit. `auto` lebih memilih loopback; gunakan `gateway.bind: "tailnet"` ketika Anda menginginkan bind khusus tailnet.

  </Accordion>

  <Accordion title="Bisakah saya menjalankan beberapa Gateway pada host yang sama?">
    Biasanya tidak - satu Gateway dapat menjalankan beberapa channel pesan dan agen. Gunakan beberapa Gateway hanya ketika Anda memerlukan redundansi (mis.: bot penyelamat) atau isolasi keras.

    Ya, tetapi Anda harus mengisolasi:

    - `OPENCLAW_CONFIG_PATH` (config per instance)
    - `OPENCLAW_STATE_DIR` (state per instance)
    - `agents.defaults.workspace` (isolasi workspace)
    - `gateway.port` (port unik)

    Penyiapan cepat (disarankan):

    - Gunakan `openclaw --profile <name> ...` per instance (otomatis membuat `~/.openclaw-<name>`).
    - Tetapkan `gateway.port` yang unik di setiap config profil (atau lewati `--port` untuk eksekusi manual).
    - Instal service per profil: `openclaw --profile <name> gateway install`.

    Profil juga menambahkan akhiran pada nama service (`ai.openclaw.<profile>`; lama: `com.openclaw.*`, `openclaw-gateway-<profile>.service`, `OpenClaw Gateway (<profile>)`).
    Panduan lengkap: [Beberapa gateway](/id/gateway/multiple-gateways).

  </Accordion>

  <Accordion title='Apa arti "invalid handshake" / code 1008?'>
    Gateway adalah **server WebSocket**, dan mengharapkan pesan pertama
    berupa frame `connect`. Jika menerima hal lain, koneksi akan ditutup
    dengan **code 1008** (pelanggaran kebijakan).

    Penyebab umum:

    - Anda membuka URL **HTTP** di browser (`http://...`) alih-alih klien WS.
    - Anda menggunakan port atau path yang salah.
    - Proxy atau tunnel menghapus header auth atau mengirim permintaan non-Gateway.

    Perbaikan cepat:

    1. Gunakan URL WS: `ws://<host>:18789` (atau `wss://...` jika HTTPS).
    2. Jangan buka port WS di tab browser biasa.
    3. Jika auth aktif, sertakan token/kata sandi di frame `connect`.

    Jika Anda menggunakan CLI atau TUI, URL-nya akan terlihat seperti ini:

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    Detail protokol: [Protokol Gateway](/id/gateway/protocol).

  </Accordion>
</AccordionGroup>

## Logging dan debugging

<AccordionGroup>
  <Accordion title="Di mana log berada?">
    Log file (terstruktur):

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    Anda dapat menetapkan path stabil melalui `logging.file`. Tingkat log file dikendalikan oleh `logging.level`. Verbositas konsol dikendalikan oleh `--verbose` dan `logging.consoleLevel`.

    Ekor log tercepat:

    ```bash
    openclaw logs --follow
    ```

    Log service/supervisor (saat gateway berjalan melalui launchd/systemd):

    - macOS: `$OPENCLAW_STATE_DIR/logs/gateway.log` dan `gateway.err.log` (default: `~/.openclaw/logs/...`; profil menggunakan `~/.openclaw-<profile>/logs/...`)
    - Linux: `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows: `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    Lihat [Pemecahan Masalah](/id/gateway/troubleshooting) untuk lebih lanjut.

  </Accordion>

  <Accordion title="Bagaimana cara memulai/menghentikan/memulai ulang service Gateway?">
    Gunakan helper gateway:

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    Jika Anda menjalankan gateway secara manual, `openclaw gateway --force` dapat mengambil kembali port. Lihat [Gateway](/id/gateway).

  </Accordion>

  <Accordion title="Saya menutup terminal di Windows - bagaimana cara memulai ulang OpenClaw?">
    Ada **dua mode instalasi Windows**:

    **1) WSL2 (disarankan):** Gateway berjalan di dalam Linux.

    Buka PowerShell, masuk ke WSL, lalu mulai ulang:

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    Jika Anda tidak pernah menginstal service, jalankan di foreground:

    ```bash
    openclaw gateway run
    ```

    **2) Windows native (tidak direkomendasikan):** Gateway berjalan langsung di Windows.

    Buka PowerShell dan jalankan:

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    Jika Anda menjalankannya secara manual (tanpa service), gunakan:

    ```powershell
    openclaw gateway run
    ```

    Docs: [Windows (WSL2)](/id/platforms/windows), [Runbook service Gateway](/id/gateway).

  </Accordion>

  <Accordion title="Gateway aktif tetapi balasan tidak pernah datang. Apa yang harus saya periksa?">
    Mulailah dengan pemeriksaan kesehatan cepat:

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    Penyebab umum:

    - Auth model tidak dimuat di **host gateway** (periksa `models status`).
    - Pairing/allowlist channel memblokir balasan (periksa config channel + log).
    - WebChat/Dashboard terbuka tanpa token yang benar.

    Jika Anda remote, pastikan koneksi tunnel/Tailscale aktif dan
    Gateway WebSocket dapat dijangkau.

    Docs: [Channels](/id/channels), [Pemecahan Masalah](/id/gateway/troubleshooting), [Akses jarak jauh](/id/gateway/remote).

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason" - sekarang apa?'>
    Ini biasanya berarti UI kehilangan koneksi WebSocket. Periksa:

    1. Apakah Gateway berjalan? `openclaw gateway status`
    2. Apakah Gateway sehat? `openclaw status`
    3. Apakah UI memiliki token yang benar? `openclaw dashboard`
    4. Jika remote, apakah tautan tunnel/Tailscale aktif?

    Lalu ikuti log:

    ```bash
    openclaw logs --follow
    ```

    Docs: [Dashboard](/web/dashboard), [Akses jarak jauh](/id/gateway/remote), [Pemecahan Masalah](/id/gateway/troubleshooting).

  </Accordion>

  <Accordion title="setMyCommands Telegram gagal. Apa yang harus saya periksa?">
    Mulailah dengan log dan status channel:

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    Lalu cocokkan error-nya:

    - `BOT_COMMANDS_TOO_MUCH`: menu Telegram memiliki terlalu banyak entri. OpenClaw sudah memangkas ke batas Telegram dan mencoba lagi dengan perintah yang lebih sedikit, tetapi beberapa entri menu masih perlu dihapus. Kurangi perintah plugin/skill/kustom, atau nonaktifkan `channels.telegram.commands.native` jika Anda tidak memerlukan menu.
    - `TypeError: fetch failed`, `Network request for 'setMyCommands' failed!`, atau error jaringan serupa: jika Anda berada di VPS atau di belakang proxy, pastikan HTTPS keluar diizinkan dan DNS berfungsi untuk `api.telegram.org`.

    Jika Gateway bersifat remote, pastikan Anda melihat log di host Gateway.

    Docs: [Telegram](/id/channels/telegram), [Pemecahan masalah channel](/id/channels/troubleshooting).

  </Accordion>

  <Accordion title="TUI tidak menampilkan output. Apa yang harus saya periksa?">
    Pertama, pastikan Gateway dapat dijangkau dan agen dapat berjalan:

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    Di TUI, gunakan `/status` untuk melihat state saat ini. Jika Anda mengharapkan balasan di
    channel chat, pastikan pengiriman diaktifkan (`/deliver on`).

    Docs: [TUI](/web/tui), [Perintah slash](/id/tools/slash-commands).

  </Accordion>

  <Accordion title="Bagaimana cara menghentikan sepenuhnya lalu memulai Gateway?">
    Jika Anda menginstal service:

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    Ini menghentikan/memulai **service yang diawasi** (launchd di macOS, systemd di Linux).
    Gunakan ini saat Gateway berjalan di latar belakang sebagai daemon.

    Jika Anda menjalankan di foreground, hentikan dengan Ctrl-C, lalu:

    ```bash
    openclaw gateway run
    ```

    Docs: [Runbook service Gateway](/id/gateway).

  </Accordion>

  <Accordion title="ELI5: openclaw gateway restart vs openclaw gateway">
    - `openclaw gateway restart`: memulai ulang **service latar belakang** (launchd/systemd).
    - `openclaw gateway`: menjalankan gateway **di foreground** untuk sesi terminal ini.

    Jika Anda telah menginstal service, gunakan perintah gateway. Gunakan `openclaw gateway` saat
    Anda menginginkan eksekusi foreground satu kali.

  </Accordion>

  <Accordion title="Cara tercepat untuk mendapatkan detail lebih banyak saat sesuatu gagal">
    Mulai Gateway dengan `--verbose` untuk mendapatkan detail konsol yang lebih banyak. Lalu periksa file log untuk auth channel, routing model, dan error RPC.
  </Accordion>
</AccordionGroup>

## Media dan lampiran

<AccordionGroup>
  <Accordion title="Skill saya menghasilkan gambar/PDF, tetapi tidak ada yang dikirim">
    Lampiran keluar dari agen harus menyertakan baris `MEDIA:<path-or-url>` (pada baris tersendiri). Lihat [Penyiapan asisten OpenClaw](/id/start/openclaw) dan [Pengiriman agen](/id/tools/agent-send).

    Pengiriman CLI:

    ```bash
    openclaw message send --target +15555550123 --message "Ini dia" --media /path/to/file.png
    ```

    Periksa juga:

    - Channel target mendukung media keluar dan tidak diblokir oleh allowlist.
    - File berada dalam batas ukuran provider (gambar diubah ukurannya hingga maksimum 2048px).
    - `tools.fs.workspaceOnly=true` membuat pengiriman path lokal tetap terbatas pada workspace, temp/media-store, dan file yang divalidasi sandbox.
    - `tools.fs.workspaceOnly=false` memungkinkan `MEDIA:` mengirim file lokal host yang sudah dapat dibaca agen, tetapi hanya untuk media plus tipe dokumen aman (gambar, audio, video, PDF, dan dokumen Office). File teks biasa dan file mirip secret tetap diblokir.

    Lihat [Images](/id/nodes/images).

  </Accordion>
</AccordionGroup>

## Keamanan dan kontrol akses

<AccordionGroup>
  <Accordion title="Apakah aman mengekspos OpenClaw ke DM masuk?">
    Perlakukan DM masuk sebagai input tak tepercaya. Default dirancang untuk mengurangi risiko:

    - Perilaku default pada channel yang mendukung DM adalah **pairing**:
      - Pengirim yang tidak dikenal menerima kode pairing; bot tidak memproses pesan mereka.
      - Setujui dengan: `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - Permintaan tertunda dibatasi hingga **3 per channel**; periksa `openclaw pairing list --channel <channel> [--account <id>]` jika kode tidak sampai.
    - Membuka DM secara publik memerlukan opt-in eksplisit (`dmPolicy: "open"` dan allowlist `"*"`).

    Jalankan `openclaw doctor` untuk menampilkan kebijakan DM yang berisiko.

  </Accordion>

  <Accordion title="Apakah injeksi prompt hanya menjadi perhatian untuk bot publik?">
    Tidak. Injeksi prompt berkaitan dengan **konten tak tepercaya**, bukan hanya siapa yang bisa DM bot.
    Jika asisten Anda membaca konten eksternal (pencarian/pengambilan web, halaman browser, email,
    docs, lampiran, log yang ditempel), konten itu dapat berisi instruksi yang mencoba
    membajak model. Ini dapat terjadi bahkan jika **Anda adalah satu-satunya pengirim**.

    Risiko terbesar muncul saat tool diaktifkan: model dapat ditipu untuk
    mengekstrak konteks atau memanggil tool atas nama Anda. Kurangi radius dampaknya dengan:

    - menggunakan agen "pembaca" yang baca-saja atau tanpa tool untuk merangkum konten tak tepercaya
    - menjaga `web_search` / `web_fetch` / `browser` tetap nonaktif untuk agen yang menggunakan tool
    - memperlakukan teks file/dokumen yang didekodekan juga sebagai tidak tepercaya: OpenResponses
      `input_file` dan ekstraksi lampiran media sama-sama membungkus teks yang diekstrak dalam
      penanda batas konten eksternal yang eksplisit alih-alih meneruskan teks file mentah
    - sandboxing dan allowlist tool yang ketat

    Detail: [Security](/id/gateway/security).

  </Accordion>

  <Accordion title="Haruskah bot saya memiliki email, akun GitHub, atau nomor telepon sendiri?">
    Ya, untuk sebagian besar penyiapan. Mengisolasi bot dengan akun dan nomor telepon terpisah
    mengurangi radius dampak jika terjadi sesuatu yang salah. Ini juga memudahkan untuk memutar
    kredensial atau mencabut akses tanpa memengaruhi akun pribadi Anda.

    Mulailah dari yang kecil. Berikan akses hanya ke tool dan akun yang benar-benar Anda perlukan, lalu perluas
    nanti jika diperlukan.

    Docs: [Security](/id/gateway/security), [Pairing](/id/channels/pairing).

  </Accordion>

  <Accordion title="Bisakah saya memberinya otonomi atas pesan teks saya dan apakah itu aman?">
    Kami **tidak** merekomendasikan otonomi penuh atas pesan pribadi Anda. Pola yang paling aman adalah:

    - Pertahankan DM dalam **mode pairing** atau allowlist yang ketat.
    - Gunakan **nomor atau akun terpisah** jika Anda ingin bot mengirim pesan atas nama Anda.
    - Biarkan bot membuat draf, lalu **setujui sebelum mengirim**.

    Jika Anda ingin bereksperimen, lakukan itu pada akun khusus dan tetap jaga isolasinya. Lihat
    [Security](/id/gateway/security).

  </Accordion>

  <Accordion title="Bisakah saya menggunakan model yang lebih murah untuk tugas asisten pribadi?">
    Ya, **jika** agen hanya untuk chat dan input-nya tepercaya. Tier yang lebih kecil
    lebih rentan terhadap pembajakan instruksi, jadi hindari untuk agen yang menggunakan tool
    atau saat membaca konten tak tepercaya. Jika Anda harus menggunakan model yang lebih kecil, kunci
    tool dan jalankan di dalam sandbox. Lihat [Security](/id/gateway/security).
  </Accordion>

  <Accordion title="Saya menjalankan /start di Telegram tetapi tidak mendapatkan kode pairing">
    Kode pairing dikirim **hanya** ketika pengirim yang tidak dikenal mengirim pesan ke bot dan
    `dmPolicy: "pairing"` diaktifkan. `/start` saja tidak menghasilkan kode.

    Periksa permintaan yang tertunda:

    ```bash
    openclaw pairing list telegram
    ```

    Jika Anda menginginkan akses segera, tambahkan ID pengirim Anda ke allowlist atau tetapkan `dmPolicy: "open"`
    untuk akun tersebut.

  </Accordion>

  <Accordion title="WhatsApp: apakah OpenClaw akan mengirim pesan ke kontak saya? Bagaimana cara kerja pairing?">
    Tidak. Kebijakan DM WhatsApp default adalah **pairing**. Pengirim yang tidak dikenal hanya mendapatkan kode pairing dan pesan mereka **tidak diproses**. OpenClaw hanya membalas chat yang diterimanya atau pengiriman eksplisit yang Anda picu.

    Setujui pairing dengan:

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    Daftar permintaan yang tertunda:

    ```bash
    openclaw pairing list whatsapp
    ```

    Prompt nomor telepon wizard: itu digunakan untuk menetapkan **allowlist/pemilik** Anda sehingga DM Anda sendiri diizinkan. Itu tidak digunakan untuk pengiriman otomatis. Jika Anda menjalankan dengan nomor WhatsApp pribadi Anda, gunakan nomor tersebut dan aktifkan `channels.whatsapp.selfChatMode`.

  </Accordion>
</AccordionGroup>

## Perintah chat, membatalkan tugas, dan "tidak mau berhenti"

<AccordionGroup>
  <Accordion title="Bagaimana cara menghentikan pesan sistem internal agar tidak muncul di chat?">
    Sebagian besar pesan internal atau tool hanya muncul ketika **verbose**, **trace**, atau **reasoning** diaktifkan
    untuk sesi tersebut.

    Perbaiki di chat tempat Anda melihatnya:

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    Jika masih berisik, periksa pengaturan sesi di Control UI dan tetapkan verbose
    ke **inherit**. Pastikan juga Anda tidak menggunakan profil bot dengan `verboseDefault` yang disetel
    ke `on` di config.

    Docs: [Thinking and verbose](/id/tools/thinking), [Security](/id/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="Bagaimana cara menghentikan/membatalkan tugas yang sedang berjalan?">
    Kirim salah satu dari ini **sebagai pesan mandiri** (tanpa slash):

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    Ini adalah pemicu pembatalan (bukan perintah slash).

    Untuk proses latar belakang (dari tool exec), Anda dapat meminta agen menjalankan:

    ```
    process action:kill sessionId:XXX
    ```

    Ikhtisar perintah slash: lihat [Perintah slash](/id/tools/slash-commands).

    Sebagian besar perintah harus dikirim sebagai pesan **mandiri** yang dimulai dengan `/`, tetapi beberapa shortcut (seperti `/status`) juga berfungsi inline untuk pengirim yang ada di allowlist.

  </Accordion>

  <Accordion title='Bagaimana cara mengirim pesan Discord dari Telegram? ("Cross-context messaging denied")'>
    OpenClaw memblokir pengiriman pesan **lintas provider** secara default. Jika pemanggilan tool
    terikat ke Telegram, tool itu tidak akan mengirim ke Discord kecuali Anda mengizinkannya secara eksplisit.

    Aktifkan pengiriman pesan lintas provider untuk agen:

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    Restart gateway setelah mengedit config.

  </Accordion>

  <Accordion title='Mengapa terasa seperti bot "mengabaikan" pesan yang datang beruntun dengan cepat?'>
    Mode antrean mengontrol bagaimana pesan baru berinteraksi dengan eksekusi yang sedang berlangsung. Gunakan `/queue` untuk mengubah mode:

    - `steer` - pesan baru mengarahkan ulang tugas saat ini
    - `followup` - jalankan pesan satu per satu
    - `collect` - kumpulkan pesan dan balas sekali (default)
    - `steer-backlog` - arahkan sekarang, lalu proses backlog
    - `interrupt` - batalkan eksekusi saat ini dan mulai baru

    Anda dapat menambahkan opsi seperti `debounce:2s cap:25 drop:summarize` untuk mode followup.

  </Accordion>
</AccordionGroup>

## Lain-lain

<AccordionGroup>
  <Accordion title='Apa model default untuk Anthropic dengan kunci API?'>
    Di OpenClaw, kredensial dan pemilihan model terpisah. Menetapkan `ANTHROPIC_API_KEY` (atau menyimpan kunci API Anthropic dalam profil auth) mengaktifkan autentikasi, tetapi model default sebenarnya adalah apa pun yang Anda konfigurasikan di `agents.defaults.model.primary` (misalnya, `anthropic/claude-sonnet-4-6` atau `anthropic/claude-opus-4-6`). Jika Anda melihat `No credentials found for profile "anthropic:default"`, itu berarti Gateway tidak dapat menemukan kredensial Anthropic di `auth-profiles.json` yang diharapkan untuk agen yang sedang berjalan.
  </Accordion>
</AccordionGroup>

---

Masih buntu? Tanya di [Discord](https://discord.com/invite/clawd) atau buka [diskusi GitHub](https://github.com/openclaw/openclaw/discussions).
