---
read_when:
    - Menambahkan otomatisasi browser yang dikendalikan agen
    - Men-debug mengapa openclaw mengganggu Chrome Anda sendiri
    - Menerapkan pengaturan browser + siklus hidup di aplikasi macOS
summary: Layanan kontrol browser terintegrasi + perintah aksi
title: Browser (dikelola OpenClaw)
x-i18n:
    generated_at: "2026-04-14T09:14:20Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae9ef725f544d4236d229f498c7187871c69bd18d31069b30a7e67fac53166a2
    source_path: tools/browser.md
    workflow: 15
---

# Browser (dikelola openclaw)

OpenClaw dapat menjalankan **profil Chrome/Brave/Edge/Chromium khusus** yang dikendalikan oleh agen.
Ini terisolasi dari browser pribadi Anda dan dikelola melalui layanan kontrol lokal kecil
di dalam Gateway (hanya loopback).

Tampilan untuk pemula:

- Anggap ini sebagai **browser terpisah, khusus agen**.
- Profil `openclaw` **tidak** menyentuh profil browser pribadi Anda.
- Agen dapat **membuka tab, membaca halaman, mengeklik, dan mengetik** di jalur yang aman.
- Profil bawaan `user` terhubung ke sesi Chrome nyata Anda yang sudah login melalui Chrome MCP.

## Yang Anda dapatkan

- Profil browser terpisah bernama **openclaw** (aksen oranye secara default).
- Kontrol tab yang deterministik (daftar/buka/fokus/tutup).
- Aksi agen (klik/ketik/seret/pilih), snapshot, screenshot, PDF.
- Dukungan multi-profil opsional (`openclaw`, `work`, `remote`, ...).

Browser ini **bukan** browser harian Anda. Ini adalah permukaan yang aman dan terisolasi untuk
otomatisasi dan verifikasi agen.

## Mulai cepat

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Jika Anda mendapatkan “Browser dinonaktifkan”, aktifkan di konfigurasi (lihat di bawah) dan mulai ulang
Gateway.

Jika `openclaw browser` sama sekali tidak ada, atau agen mengatakan alat browser
tidak tersedia, langsung ke [Perintah atau alat browser tidak ada](/id/tools/browser#missing-browser-command-or-tool).

## Kontrol Plugin

Alat `browser` default sekarang adalah Plugin bawaan yang dikirim dalam keadaan aktif
secara default. Artinya Anda dapat menonaktifkan atau menggantinya tanpa menghapus sisa
sistem plugin OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Nonaktifkan Plugin bawaan sebelum memasang Plugin lain yang menyediakan
nama alat `browser` yang sama. Pengalaman browser default memerlukan keduanya:

- `plugins.entries.browser.enabled` tidak dinonaktifkan
- `browser.enabled=true`

Jika Anda hanya mematikan Plugin, CLI browser bawaan (`openclaw browser`),
metode gateway (`browser.request`), alat agen, dan layanan kontrol browser default
semuanya hilang bersama. Konfigurasi `browser.*` Anda tetap utuh agar dapat digunakan ulang oleh
Plugin pengganti.

Plugin browser bawaan kini juga memiliki implementasi runtime browser.
Core hanya menyimpan helper Plugin SDK bersama serta re-export kompatibilitas untuk
jalur import internal lama. Dalam praktiknya, menghapus atau mengganti paket Plugin browser
akan menghapus rangkaian fitur browser alih-alih meninggalkan runtime kedua yang masih dimiliki
core.

Perubahan konfigurasi browser tetap memerlukan restart Gateway agar Plugin bawaan
dapat mendaftarkan ulang layanan browser-nya dengan pengaturan baru.

## Perintah atau alat browser tidak ada

Jika `openclaw browser` tiba-tiba menjadi perintah yang tidak dikenal setelah upgrade, atau
agen melaporkan bahwa alat browser hilang, penyebab paling umum adalah daftar
`plugins.allow` yang terlalu ketat dan tidak menyertakan `browser`.

Contoh konfigurasi yang rusak:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Perbaiki dengan menambahkan `browser` ke allowlist Plugin:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Catatan penting:

- `browser.enabled=true` saja tidak cukup ketika `plugins.allow` disetel.
- `plugins.entries.browser.enabled=true` saja juga tidak cukup ketika `plugins.allow` disetel.
- `tools.alsoAllow: ["browser"]` **tidak** memuat Plugin browser bawaan. Itu hanya menyesuaikan kebijakan alat setelah Plugin sudah dimuat.
- Jika Anda tidak membutuhkan allowlist Plugin yang ketat, menghapus `plugins.allow` juga mengembalikan perilaku browser bawaan default.

Gejala umum:

- `openclaw browser` adalah perintah yang tidak dikenal.
- `browser.request` tidak ada.
- Agen melaporkan alat browser tidak tersedia atau hilang.

## Profil: `openclaw` vs `user`

- `openclaw`: browser terkelola dan terisolasi (tidak memerlukan ekstensi).
- `user`: profil attach Chrome MCP bawaan untuk sesi **Chrome asli Anda yang sudah login**.

Untuk pemanggilan alat browser agen:

- Default: gunakan browser `openclaw` yang terisolasi.
- Gunakan `profile="user"` jika sesi login yang sudah ada penting dan pengguna
  sedang berada di depan komputer untuk mengeklik/menyetujui prompt attach apa pun.
- `profile` adalah override eksplisit saat Anda menginginkan mode browser tertentu.

Setel `browser.defaultProfile: "openclaw"` jika Anda ingin mode terkelola secara default.

## Konfigurasi

Pengaturan browser berada di `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // default: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // ikut serta hanya untuk akses jaringan privat tepercaya
      // allowPrivateNetwork: true, // alias lama
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // override profil tunggal lama
    remoteCdpTimeoutMs: 1500, // timeout HTTP CDP jarak jauh (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // timeout handshake WebSocket CDP jarak jauh (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Catatan:

- Layanan kontrol browser melakukan bind ke loopback pada port yang diturunkan dari `gateway.port`
  (default: `18791`, yaitu gateway + 2).
- Jika Anda meng-override port Gateway (`gateway.port` atau `OPENCLAW_GATEWAY_PORT`),
  port browser turunan akan bergeser agar tetap berada dalam “keluarga” yang sama.
- `cdpUrl` secara default mengarah ke port CDP lokal terkelola saat tidak disetel.
- `remoteCdpTimeoutMs` berlaku untuk pemeriksaan keterjangkauan CDP jarak jauh (non-loopback).
- `remoteCdpHandshakeTimeoutMs` berlaku untuk pemeriksaan keterjangkauan handshake WebSocket CDP jarak jauh.
- Navigasi browser/buka-tab dilindungi SSRF sebelum navigasi dan diperiksa ulang sebisa mungkin pada URL akhir `http(s)` setelah navigasi.
- Dalam mode SSRF ketat, discovery/probe endpoint CDP jarak jauh (`cdpUrl`, termasuk lookup `/json/version`) juga diperiksa.
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` dinonaktifkan secara default. Setel ke `true` hanya jika Anda memang memercayai akses browser ke jaringan privat.
- `browser.ssrfPolicy.allowPrivateNetwork` tetap didukung sebagai alias lama untuk kompatibilitas.
- `attachOnly: true` berarti “jangan pernah meluncurkan browser lokal; hanya attach jika browser sudah berjalan.”
- `color` + `color` per profil memberi warna UI browser agar Anda dapat melihat profil mana yang aktif.
- Profil default adalah `openclaw` (browser mandiri yang dikelola OpenClaw). Gunakan `defaultProfile: "user"` untuk memilih browser pengguna yang sudah login.
- Urutan deteksi otomatis: browser default sistem jika berbasis Chromium; jika tidak, Chrome → Brave → Edge → Chromium → Chrome Canary.
- Profil `openclaw` lokal otomatis menetapkan `cdpPort`/`cdpUrl` — setel itu hanya untuk CDP jarak jauh.
- `driver: "existing-session"` menggunakan Chrome DevTools MCP, bukan CDP mentah. Jangan
  setel `cdpUrl` untuk driver tersebut.
- Setel `browser.profiles.<name>.userDataDir` saat profil existing-session
  harus attach ke profil pengguna Chromium non-default seperti Brave atau Edge.

## Gunakan Brave (atau browser berbasis Chromium lainnya)

Jika browser **default sistem** Anda berbasis Chromium (Chrome/Brave/Edge/dll),
OpenClaw akan menggunakannya secara otomatis. Setel `browser.executablePath` untuk meng-override
deteksi otomatis:

Contoh CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Kontrol lokal vs jarak jauh

- **Kontrol lokal (default):** Gateway memulai layanan kontrol loopback dan dapat meluncurkan browser lokal.
- **Kontrol jarak jauh (host node):** jalankan host node di mesin yang memiliki browser; Gateway mem-proxy aksi browser ke sana.
- **CDP jarak jauh:** setel `browser.profiles.<name>.cdpUrl` (atau `browser.cdpUrl`) untuk
  attach ke browser berbasis Chromium jarak jauh. Dalam kasus ini, OpenClaw tidak akan meluncurkan browser lokal.

Perilaku penghentian berbeda menurut mode profil:

- profil lokal terkelola: `openclaw browser stop` menghentikan proses browser yang
  diluncurkan oleh OpenClaw
- profil attach-only dan CDP jarak jauh: `openclaw browser stop` menutup sesi
  kontrol aktif dan melepaskan override emulasi Playwright/CDP (viewport,
  skema warna, lokal, zona waktu, mode offline, dan status serupa), meskipun
  tidak ada proses browser yang diluncurkan oleh OpenClaw

URL CDP jarak jauh dapat menyertakan autentikasi:

- Token query (mis. `https://provider.example?token=<token>`)
- HTTP Basic auth (mis. `https://user:pass@provider.example`)

OpenClaw mempertahankan autentikasi saat memanggil endpoint `/json/*` dan saat terhubung
ke WebSocket CDP. Gunakan environment variable atau pengelola secret untuk
token alih-alih meng-commit-nya ke file konfigurasi.

## Proksi browser node (default tanpa konfigurasi)

Jika Anda menjalankan **host node** di mesin yang memiliki browser Anda, OpenClaw dapat
secara otomatis merutekan pemanggilan alat browser ke node tersebut tanpa konfigurasi browser tambahan.
Ini adalah jalur default untuk Gateway jarak jauh.

Catatan:

- Host node mengekspos server kontrol browser lokalnya melalui **perintah proxy**.
- Profil berasal dari konfigurasi `browser.profiles` milik node itu sendiri (sama seperti lokal).
- `nodeHost.browserProxy.allowProfiles` bersifat opsional. Biarkan kosong untuk perilaku lama/default: semua profil yang dikonfigurasi tetap dapat dijangkau melalui proksi, termasuk rute buat/hapus profil.
- Jika Anda menyetel `nodeHost.browserProxy.allowProfiles`, OpenClaw memperlakukannya sebagai batas least-privilege: hanya profil yang di-allowlist yang dapat ditargetkan, dan rute buat/hapus profil persisten diblokir pada permukaan proksi.
- Nonaktifkan jika Anda tidak menginginkannya:
  - Pada node: `nodeHost.browserProxy.enabled=false`
  - Pada gateway: `gateway.nodes.browser.mode="off"`

## Browserless (CDP jarak jauh terhosting)

[Browserless](https://browserless.io) adalah layanan Chromium terhosting yang mengekspos
URL koneksi CDP melalui HTTPS dan WebSocket. OpenClaw dapat menggunakan salah satu bentuk tersebut, tetapi
untuk profil browser jarak jauh, opsi paling sederhana adalah URL WebSocket langsung
dari dokumentasi koneksi Browserless.

Contoh:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Catatan:

- Ganti `<BROWSERLESS_API_KEY>` dengan token Browserless Anda yang sebenarnya.
- Pilih endpoint region yang sesuai dengan akun Browserless Anda (lihat dokumentasi mereka).
- Jika Browserless memberi Anda URL dasar HTTPS, Anda dapat mengubahnya menjadi
  `wss://` untuk koneksi CDP langsung atau tetap menggunakan URL HTTPS dan membiarkan OpenClaw
  menemukan `/json/version`.

## Penyedia CDP WebSocket langsung

Beberapa layanan browser terhosting mengekspos endpoint **WebSocket langsung** alih-alih
discovery CDP berbasis HTTP standar (`/json/version`). OpenClaw mendukung keduanya:

- **Endpoint HTTP(S)** — OpenClaw memanggil `/json/version` untuk menemukan
  URL debugger WebSocket, lalu terhubung.
- **Endpoint WebSocket** (`ws://` / `wss://`) — OpenClaw terhubung secara langsung,
  melewati `/json/version`. Gunakan ini untuk layanan seperti
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com), atau penyedia apa pun yang memberi Anda
  URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) adalah platform cloud untuk menjalankan
browser headless dengan pemecahan CAPTCHA bawaan, mode stealth, dan proxy
residensial.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Catatan:

- [Daftar](https://www.browserbase.com/sign-up) dan salin **API Key**
  Anda dari [dashboard Overview](https://www.browserbase.com/overview).
- Ganti `<BROWSERBASE_API_KEY>` dengan API key Browserbase Anda yang sebenarnya.
- Browserbase otomatis membuat sesi browser saat terhubung ke WebSocket, jadi tidak
  diperlukan langkah pembuatan sesi manual.
- Tingkat gratis memungkinkan satu sesi bersamaan dan satu jam browser per bulan.
  Lihat [harga](https://www.browserbase.com/pricing) untuk batas paket berbayar.
- Lihat [dokumentasi Browserbase](https://docs.browserbase.com) untuk referensi API
  lengkap, panduan SDK, dan contoh integrasi.

## Keamanan

Ide utama:

- Kontrol browser hanya loopback; akses mengalir melalui autentikasi Gateway atau pairing node.
- API HTTP browser loopback mandiri hanya menggunakan **autentikasi shared-secret**:
  autentikasi bearer token gateway, `x-openclaw-password`, atau HTTP Basic auth dengan
  kata sandi gateway yang dikonfigurasi.
- Header identitas Tailscale Serve dan `gateway.auth.mode: "trusted-proxy"`
  **tidak** mengautentikasi API browser loopback mandiri ini.
- Jika kontrol browser diaktifkan dan tidak ada autentikasi shared-secret yang dikonfigurasi, OpenClaw
  otomatis membuat `gateway.auth.token` saat startup dan menyimpannya ke konfigurasi.
- OpenClaw **tidak** otomatis membuat token tersebut ketika `gateway.auth.mode` sudah
  `password`, `none`, atau `trusted-proxy`.
- Simpan Gateway dan host node apa pun di jaringan privat (Tailscale); hindari eksposur publik.
- Perlakukan URL/token CDP jarak jauh sebagai secret; gunakan environment variable atau pengelola secret.

Tips CDP jarak jauh:

- Gunakan endpoint terenkripsi (HTTPS atau WSS) dan token berumur pendek jika memungkinkan.
- Hindari menyematkan token berumur panjang langsung di file konfigurasi.

## Profil (multi-browser)

OpenClaw mendukung beberapa profil bernama (konfigurasi routing). Profil dapat berupa:

- **dikelola openclaw**: instance browser berbasis Chromium khusus dengan direktori data pengguna + port CDP-nya sendiri
- **jarak jauh**: URL CDP eksplisit (browser berbasis Chromium yang berjalan di tempat lain)
- **sesi yang sudah ada**: profil Chrome Anda yang sudah ada melalui koneksi otomatis Chrome DevTools MCP

Default:

- Profil `openclaw` dibuat otomatis jika tidak ada.
- Profil `user` bawaan tersedia untuk attach existing-session Chrome MCP.
- Profil existing-session bersifat opt-in di luar `user`; buat dengan `--driver existing-session`.
- Port CDP lokal dialokasikan dari **18800–18899** secara default.
- Menghapus profil akan memindahkan direktori data lokalnya ke Trash.

Semua endpoint kontrol menerima `?profile=<name>`; CLI menggunakan `--browser-profile`.

## Existing-session melalui Chrome DevTools MCP

OpenClaw juga dapat attach ke profil browser berbasis Chromium yang sedang berjalan melalui
server MCP Chrome DevTools resmi. Ini menggunakan kembali tab dan status login
yang sudah terbuka di profil browser tersebut.

Latar belakang resmi dan referensi penyiapan:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Profil bawaan:

- `user`

Opsional: buat profil existing-session kustom Anda sendiri jika Anda menginginkan
nama, warna, atau direktori data browser yang berbeda.

Perilaku default:

- Profil `user` bawaan menggunakan koneksi otomatis Chrome MCP, yang menargetkan
  profil Google Chrome lokal default.

Gunakan `userDataDir` untuk Brave, Edge, Chromium, atau profil Chrome non-default:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Lalu pada browser yang sesuai:

1. Buka halaman inspect browser tersebut untuk remote debugging.
2. Aktifkan remote debugging.
3. Biarkan browser tetap berjalan dan setujui prompt koneksi saat OpenClaw melakukan attach.

Halaman inspect umum:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Uji smoke attach langsung:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Seperti apa hasil yang berhasil:

- `status` menampilkan `driver: existing-session`
- `status` menampilkan `transport: chrome-mcp`
- `status` menampilkan `running: true`
- `tabs` menampilkan tab browser Anda yang sudah terbuka
- `snapshot` mengembalikan ref dari tab live yang dipilih

Yang perlu diperiksa jika attach tidak berfungsi:

- browser berbasis Chromium target memiliki versi `144+`
- remote debugging diaktifkan pada halaman inspect browser tersebut
- browser menampilkan prompt persetujuan attach dan Anda menerimanya
- `openclaw doctor` memigrasikan konfigurasi browser lama berbasis ekstensi dan memeriksa bahwa
  Chrome terpasang secara lokal untuk profil default auto-connect, tetapi tidak dapat
  mengaktifkan remote debugging di sisi browser untuk Anda

Penggunaan agen:

- Gunakan `profile="user"` saat Anda memerlukan status browser pengguna yang sudah login.
- Jika Anda menggunakan profil existing-session kustom, kirim nama profil eksplisit tersebut.
- Pilih mode ini hanya ketika pengguna berada di depan komputer untuk menyetujui prompt
  attach.
- Gateway atau host node dapat menjalankan `npx chrome-devtools-mcp@latest --autoConnect`

Catatan:

- Jalur ini berisiko lebih tinggi dibanding profil `openclaw` yang terisolasi karena dapat
  bertindak di dalam sesi browser Anda yang sudah login.
- OpenClaw tidak meluncurkan browser untuk driver ini; ia hanya attach ke
  sesi yang sudah ada.
- OpenClaw menggunakan alur resmi Chrome DevTools MCP `--autoConnect` di sini. Jika
  `userDataDir` disetel, OpenClaw meneruskannya untuk menargetkan direktori data pengguna
  Chromium eksplisit tersebut.
- Screenshot existing-session mendukung tangkapan halaman dan tangkapan elemen `--ref`
  dari snapshot, tetapi tidak mendukung selector CSS `--element`.
- Screenshot halaman existing-session berfungsi tanpa Playwright melalui Chrome MCP.
  Screenshot elemen berbasis ref (`--ref`) juga berfungsi di sana, tetapi `--full-page`
  tidak dapat digabungkan dengan `--ref` atau `--element`.
- Aksi existing-session masih lebih terbatas dibanding jalur browser terkelola:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag`, dan `select` memerlukan
    ref snapshot alih-alih selector CSS
  - `click` hanya mendukung tombol kiri (tanpa override tombol atau modifier)
  - `type` tidak mendukung `slowly=true`; gunakan `fill` atau `press`
  - `press` tidak mendukung `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill`, dan `evaluate` tidak
    mendukung override timeout per panggilan
  - `select` saat ini hanya mendukung satu nilai
- Existing-session `wait --url` mendukung pola exact, substring, dan glob
  seperti driver browser lainnya. `wait --load networkidle` belum didukung.
- Hook upload existing-session memerlukan `ref` atau `inputRef`, mendukung satu file
  per kali, dan tidak mendukung penargetan CSS `element`.
- Hook dialog existing-session tidak mendukung override timeout.
- Beberapa fitur masih memerlukan jalur browser terkelola, termasuk aksi
  batch, ekspor PDF, intersepsi unduhan, dan `responsebody`.
- Existing-session bersifat host-local. Jika Chrome berada di mesin lain atau
  namespace jaringan yang berbeda, gunakan CDP jarak jauh atau host node.

## Jaminan isolasi

- **Direktori data pengguna khusus**: tidak pernah menyentuh profil browser pribadi Anda.
- **Port khusus**: menghindari `9222` untuk mencegah benturan dengan alur kerja pengembangan.
- **Kontrol tab yang deterministik**: targetkan tab berdasarkan `targetId`, bukan “tab terakhir”.

## Pemilihan browser

Saat meluncurkan secara lokal, OpenClaw memilih yang pertama tersedia:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Anda dapat meng-override dengan `browser.executablePath`.

Platform:

- macOS: memeriksa `/Applications` dan `~/Applications`.
- Linux: mencari `google-chrome`, `brave`, `microsoft-edge`, `chromium`, dan sebagainya.
- Windows: memeriksa lokasi instalasi umum.

## API kontrol (opsional)

Hanya untuk integrasi lokal, Gateway mengekspos API HTTP loopback kecil:

- Status/start/stop: `GET /`, `POST /start`, `POST /stop`
- Tab: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/screenshot: `GET /snapshot`, `POST /screenshot`
- Aksi: `POST /navigate`, `POST /act`
- Hook: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Unduhan: `POST /download`, `POST /wait/download`
- Debugging: `GET /console`, `POST /pdf`
- Debugging: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Jaringan: `POST /response/body`
- Status: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Status: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Pengaturan: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Semua endpoint menerima `?profile=<name>`.

Jika autentikasi gateway shared-secret dikonfigurasi, rute HTTP browser juga memerlukan autentikasi:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` atau HTTP Basic auth dengan kata sandi tersebut

Catatan:

- API browser loopback mandiri ini **tidak** menggunakan trusted-proxy atau
  header identitas Tailscale Serve.
- Jika `gateway.auth.mode` adalah `none` atau `trusted-proxy`, rute browser loopback
  ini tidak mewarisi mode pembawa identitas tersebut; biarkan tetap hanya loopback.

### Kontrak error `/act`

`POST /act` menggunakan respons error terstruktur untuk validasi tingkat rute dan
kegagalan kebijakan:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Nilai `code` saat ini:

- `ACT_KIND_REQUIRED` (HTTP 400): `kind` hilang atau tidak dikenali.
- `ACT_INVALID_REQUEST` (HTTP 400): payload aksi gagal dinormalisasi atau divalidasi.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): `selector` digunakan dengan jenis aksi yang tidak didukung.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (atau `wait --fn`) dinonaktifkan oleh konfigurasi.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): `targetId` tingkat atas atau batch bertentangan dengan target permintaan.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): aksi tidak didukung untuk profil existing-session.

Kegagalan runtime lainnya mungkin masih mengembalikan `{ "error": "<message>" }` tanpa
field `code`.

### Persyaratan Playwright

Beberapa fitur (navigate/act/snapshot AI/snapshot role, screenshot elemen,
PDF) memerlukan Playwright. Jika Playwright belum terpasang, endpoint tersebut mengembalikan
error 501 yang jelas.

Yang masih berfungsi tanpa Playwright:

- Snapshot ARIA
- Screenshot halaman untuk browser `openclaw` terkelola ketika tersedia WebSocket
  CDP per tab
- Screenshot halaman untuk profil `existing-session` / Chrome MCP
- Screenshot existing-session berbasis ref (`--ref`) dari output snapshot

Yang masih memerlukan Playwright:

- `navigate`
- `act`
- Snapshot AI / snapshot role
- Screenshot elemen selector CSS (`--element`)
- Ekspor PDF browser penuh

Screenshot elemen juga menolak `--full-page`; rute mengembalikan `fullPage is
not supported for element screenshots`.

Jika Anda melihat `Playwright is not available in this gateway build`, instal paket
Playwright penuh (bukan `playwright-core`) dan mulai ulang gateway, atau instal ulang
OpenClaw dengan dukungan browser.

#### Instalasi Playwright di Docker

Jika Gateway Anda berjalan di Docker, hindari `npx playwright` (konflik override npm).
Gunakan CLI bawaan sebagai gantinya:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Untuk mempertahankan unduhan browser, setel `PLAYWRIGHT_BROWSERS_PATH` (misalnya,
`/home/node/.cache/ms-playwright`) dan pastikan `/home/node` dipertahankan melalui
`OPENCLAW_HOME_VOLUME` atau bind mount. Lihat [Docker](/id/install/docker).

## Cara kerjanya (internal)

Alur tingkat tinggi:

- Sebuah **server kontrol** kecil menerima permintaan HTTP.
- Server ini terhubung ke browser berbasis Chromium (Chrome/Brave/Edge/Chromium) melalui **CDP**.
- Untuk aksi lanjutan (klik/ketik/snapshot/PDF), server ini menggunakan **Playwright** di atas
  CDP.
- Saat Playwright tidak ada, hanya operasi non-Playwright yang tersedia.

Desain ini menjaga agen tetap berada pada antarmuka yang stabil dan deterministik sambil memungkinkan
Anda menukar browser dan profil lokal/jarak jauh.

## Referensi cepat CLI

Semua perintah menerima `--browser-profile <name>` untuk menargetkan profil tertentu.
Semua perintah juga menerima `--json` untuk output yang dapat dibaca mesin (payload stabil).

Dasar-dasar:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Inspeksi:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Catatan siklus hidup:

- Untuk profil attach-only dan CDP jarak jauh, `openclaw browser stop` tetap merupakan
  perintah pembersihan yang tepat setelah pengujian. Perintah ini menutup sesi kontrol aktif dan
  menghapus override emulasi sementara alih-alih mematikan browser
  dasarnya.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Aksi:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Status:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Catatan:

- `upload` dan `dialog` adalah panggilan **arming**; jalankan keduanya sebelum klik/press
  yang memicu chooser/dialog.
- Jalur output unduhan dan trace dibatasi ke root temp OpenClaw:
  - trace: `/tmp/openclaw` (fallback: `${os.tmpdir()}/openclaw`)
  - unduhan: `/tmp/openclaw/downloads` (fallback: `${os.tmpdir()}/openclaw/downloads`)
- Jalur upload dibatasi ke root upload temp OpenClaw:
  - upload: `/tmp/openclaw/uploads` (fallback: `${os.tmpdir()}/openclaw/uploads`)
- `upload` juga dapat menyetel input file secara langsung melalui `--input-ref` atau `--element`.
- `snapshot`:
  - `--format ai` (default saat Playwright terpasang): mengembalikan snapshot AI dengan ref numerik (`aria-ref="<n>"`).
  - `--format aria`: mengembalikan pohon aksesibilitas (tanpa ref; hanya untuk inspeksi).
  - `--efficient` (atau `--mode efficient`): preset snapshot role ringkas (interactive + compact + depth + maxChars lebih rendah).
  - Default konfigurasi (hanya tool/CLI): setel `browser.snapshotDefaults.mode: "efficient"` untuk menggunakan snapshot efisien saat pemanggil tidak memberikan mode (lihat [Konfigurasi Gateway](/id/gateway/configuration-reference#browser)).
  - Opsi snapshot role (`--interactive`, `--compact`, `--depth`, `--selector`) memaksa snapshot berbasis role dengan ref seperti `ref=e12`.
  - `--frame "<iframe selector>"` membatasi snapshot role ke sebuah iframe (dipasangkan dengan ref role seperti `e12`).
  - `--interactive` menghasilkan daftar datar elemen interaktif yang mudah dipilih (terbaik untuk menjalankan aksi).
  - `--labels` menambahkan screenshot hanya viewport dengan label ref di atasnya (mencetak `MEDIA:<path>`).
- `click`/`type`/dll memerlukan `ref` dari `snapshot` (baik numerik `12` maupun ref role `e12`).
  Selector CSS memang sengaja tidak didukung untuk aksi.

## Snapshot dan ref

OpenClaw mendukung dua gaya “snapshot”:

- **Snapshot AI (ref numerik)**: `openclaw browser snapshot` (default; `--format ai`)
  - Output: snapshot teks yang menyertakan ref numerik.
  - Aksi: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Secara internal, ref diselesaikan melalui `aria-ref` milik Playwright.

- **Snapshot role (ref role seperti `e12`)**: `openclaw browser snapshot --interactive` (atau `--compact`, `--depth`, `--selector`, `--frame`)
  - Output: daftar/pohon berbasis role dengan `[ref=e12]` (dan `[nth=1]` opsional).
  - Aksi: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Secara internal, ref diselesaikan melalui `getByRole(...)` (ditambah `nth()` untuk duplikasi).
  - Tambahkan `--labels` untuk menyertakan screenshot viewport dengan label `e12` yang dioverlay.

Perilaku ref:

- Ref **tidak stabil di seluruh navigasi**; jika sesuatu gagal, jalankan ulang `snapshot` dan gunakan ref baru.
- Jika snapshot role diambil dengan `--frame`, ref role dibatasi ke iframe tersebut sampai snapshot role berikutnya.

## Peningkatan wait

Anda dapat menunggu lebih dari sekadar waktu/teks:

- Tunggu URL (glob didukung oleh Playwright):
  - `openclaw browser wait --url "**/dash"`
- Tunggu status load:
  - `openclaw browser wait --load networkidle`
- Tunggu predikat JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Tunggu selector menjadi terlihat:
  - `openclaw browser wait "#main"`

Ini dapat digabungkan:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Alur kerja debug

Saat sebuah aksi gagal (mis. “not visible”, “strict mode violation”, “covered”):

1. `openclaw browser snapshot --interactive`
2. Gunakan `click <ref>` / `type <ref>` (utamakan ref role dalam mode interaktif)
3. Jika masih gagal: `openclaw browser highlight <ref>` untuk melihat target Playwright
4. Jika perilaku halaman aneh:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Untuk debug mendalam: rekam trace:
   - `openclaw browser trace start`
   - reproduksi masalah
   - `openclaw browser trace stop` (mencetak `TRACE:<path>`)

## Output JSON

`--json` ditujukan untuk scripting dan tooling terstruktur.

Contoh:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Snapshot role dalam JSON menyertakan `refs` plus blok `stats` kecil (lines/chars/refs/interactive) sehingga tool dapat menalar ukuran dan kepadatan payload.

## Pengaturan status dan environment

Ini berguna untuk alur kerja “buat situs berperilaku seperti X”:

- Cookie: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Header: `set headers --headers-json '{"X-Debug":"1"}'` (versi lama `set headers --json '{"X-Debug":"1"}'` tetap didukung)
- HTTP basic auth: `set credentials user pass` (atau `--clear`)
- Geolokasi: `set geo <lat> <lon> --origin "https://example.com"` (atau `--clear`)
- Media: `set media dark|light|no-preference|none`
- Zona waktu / lokal: `set timezone ...`, `set locale ...`
- Perangkat / viewport:
  - `set device "iPhone 14"` (preset perangkat Playwright)
  - `set viewport 1280 720`

## Keamanan & privasi

- Profil browser openclaw dapat berisi sesi yang sudah login; perlakukan sebagai sesuatu yang sensitif.
- `browser act kind=evaluate` / `openclaw browser evaluate` dan `wait --fn`
  mengeksekusi JavaScript arbitrer dalam konteks halaman. Injeksi prompt dapat mengarahkan
  hal ini. Nonaktifkan dengan `browser.evaluateEnabled=false` jika Anda tidak membutuhkannya.
- Untuk login dan catatan anti-bot (X/Twitter, dll.), lihat [Login browser + posting X/Twitter](/id/tools/browser-login).
- Jaga agar Gateway/host node tetap privat (hanya loopback atau tailnet).
- Endpoint CDP jarak jauh sangat kuat; tunnel-kan dan lindungi endpoint tersebut.

Contoh mode ketat (blokir tujuan privat/internal secara default):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // exact allow opsional
    },
  },
}
```

## Pemecahan masalah

Untuk masalah khusus Linux (terutama snap Chromium), lihat
[Pemecahan masalah browser](/id/tools/browser-linux-troubleshooting).

Untuk setup host terpisah WSL2 Gateway + Windows Chrome, lihat
[Pemecahan masalah WSL2 + Windows + remote Chrome CDP](/id/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

### Kegagalan startup CDP vs blokir SSRF navigasi

Ini adalah kelas kegagalan yang berbeda dan masing-masing mengarah ke jalur kode yang berbeda.

- **Kegagalan startup atau kesiapan CDP** berarti OpenClaw tidak dapat memastikan bahwa control plane browser sehat.
- **Blokir SSRF navigasi** berarti control plane browser sehat, tetapi target navigasi halaman ditolak oleh kebijakan.

Contoh umum:

- Kegagalan startup atau kesiapan CDP:
  - `Chrome CDP websocket for profile "openclaw" is not reachable after start`
  - `Remote CDP for profile "<name>" is not reachable at <cdpUrl>`
- Blokir SSRF navigasi:
  - alur `open`, `navigate`, snapshot, atau pembukaan tab gagal dengan error kebijakan browser/jaringan sementara `start` dan `tabs` tetap berfungsi

Gunakan urutan minimal ini untuk membedakan keduanya:

```bash
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw open https://example.com
```

Cara membaca hasilnya:

- Jika `start` gagal dengan `not reachable after start`, pecahkan masalah kesiapan CDP terlebih dahulu.
- Jika `start` berhasil tetapi `tabs` gagal, control plane masih tidak sehat. Perlakukan ini sebagai masalah keterjangkauan CDP, bukan masalah navigasi halaman.
- Jika `start` dan `tabs` berhasil tetapi `open` atau `navigate` gagal, control plane browser aktif dan kegagalannya ada pada kebijakan navigasi atau halaman target.
- Jika `start`, `tabs`, dan `open` semuanya berhasil, jalur kontrol browser terkelola dasar dalam kondisi sehat.

Detail perilaku penting:

- Konfigurasi browser secara default menggunakan objek kebijakan SSRF fail-closed bahkan ketika Anda tidak mengonfigurasi `browser.ssrfPolicy`.
- Untuk profil terkelola `openclaw` loopback lokal, pemeriksaan kesehatan CDP sengaja melewati penegakan keterjangkauan SSRF browser untuk control plane lokal milik OpenClaw sendiri.
- Perlindungan navigasi bersifat terpisah. Hasil `start` atau `tabs` yang berhasil tidak berarti target `open` atau `navigate` berikutnya diizinkan.

Panduan keamanan:

- **Jangan** melonggarkan kebijakan SSRF browser secara default.
- Utamakan pengecualian host yang sempit seperti `hostnameAllowlist` atau `allowedHostnames` dibanding akses jaringan privat yang luas.
- Gunakan `dangerouslyAllowPrivateNetwork: true` hanya di lingkungan yang memang tepercaya, saat akses browser ke jaringan privat diperlukan dan sudah ditinjau.

Contoh: navigasi diblokir, control plane sehat

- `start` berhasil
- `tabs` berhasil
- `open http://internal.example` gagal

Itu biasanya berarti startup browser baik-baik saja dan target navigasi perlu ditinjau kebijakannya.

Contoh: startup diblokir sebelum navigasi relevan

- `start` gagal dengan `not reachable after start`
- `tabs` juga gagal atau tidak dapat dijalankan

Itu mengarah ke peluncuran browser atau keterjangkauan CDP, bukan masalah allowlist URL halaman.

## Alat agen + cara kontrol bekerja

Agen mendapatkan **satu alat** untuk otomatisasi browser:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Pemetaan kerjanya:

- `browser snapshot` mengembalikan pohon UI yang stabil (AI atau ARIA).
- `browser act` menggunakan ID `ref` dari snapshot untuk klik/ketik/seret/pilih.
- `browser screenshot` menangkap piksel (halaman penuh atau elemen).
- `browser` menerima:
  - `profile` untuk memilih profil browser bernama (openclaw, chrome, atau CDP jarak jauh).
  - `target` (`sandbox` | `host` | `node`) untuk memilih lokasi browser berada.
  - Dalam sesi tersandbox, `target: "host"` memerlukan `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Jika `target` dihilangkan: sesi tersandbox default ke `sandbox`, sesi non-sandbox default ke `host`.
  - Jika node yang mampu menjalankan browser terhubung, alat dapat otomatis diarahkan ke node tersebut kecuali Anda menetapkan `target="host"` atau `target="node"`.

Ini menjaga agen tetap deterministik dan menghindari selector yang rapuh.

## Terkait

- [Gambaran Umum Tools](/id/tools) — semua alat agen yang tersedia
- [Sandboxing](/id/gateway/sandboxing) — kontrol browser di lingkungan tersandbox
- [Keamanan](/id/gateway/security) — risiko dan penguatan kontrol browser
