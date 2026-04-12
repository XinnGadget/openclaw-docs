---
read_when:
    - Mencari definisi channel rilis publik
    - Mencari penamaan versi dan cadence
summary: Channel rilis publik, penamaan versi, dan cadence
title: Kebijakan Rilis
x-i18n:
    generated_at: "2026-04-12T23:33:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: dffc1ee5fdbb20bd1bf4b3f817d497fc0d87f70ed6c669d324fea66dc01d0b0b
    source_path: reference/RELEASING.md
    workflow: 15
---

# Kebijakan Rilis

OpenClaw memiliki tiga jalur rilis publik:

- stable: rilis bertag yang dipublikasikan ke npm `beta` secara default, atau ke npm `latest` jika diminta secara eksplisit
- beta: tag prarilis yang dipublikasikan ke npm `beta`
- dev: head `main` yang terus bergerak

## Penamaan versi

- Versi rilis stable: `YYYY.M.D`
  - Git tag: `vYYYY.M.D`
- Versi rilis koreksi stable: `YYYY.M.D-N`
  - Git tag: `vYYYY.M.D-N`
- Versi prarilis beta: `YYYY.M.D-beta.N`
  - Git tag: `vYYYY.M.D-beta.N`
- Jangan tambahkan nol di depan bulan atau hari
- `latest` berarti rilis npm stable yang saat ini dipromosikan
- `beta` berarti target instalasi beta saat ini
- Rilis stable dan rilis koreksi stable dipublikasikan ke npm `beta` secara default; operator rilis dapat menargetkan `latest` secara eksplisit, atau mempromosikan build beta yang sudah tervalidasi nanti
- Setiap rilis OpenClaw mengirimkan paket npm dan aplikasi macOS secara bersamaan

## Ritme rilis

- Rilis bergerak dengan beta terlebih dahulu
- Stable menyusul hanya setelah beta terbaru tervalidasi
- Prosedur rilis terperinci, persetujuan, kredensial, dan catatan pemulihan
  hanya untuk maintainer

## Pemeriksaan awal rilis

- Jalankan `pnpm build && pnpm ui:build` sebelum `pnpm release:check` agar
  artefak rilis `dist/*` yang diharapkan dan bundle Control UI tersedia untuk langkah
  validasi pack
- Jalankan `pnpm release:check` sebelum setiap rilis bertag
- Pemeriksaan rilis sekarang berjalan dalam workflow manual terpisah:
  `OpenClaw Release Checks`
- Pemisahan ini disengaja: jaga jalur rilis npm yang sebenarnya tetap singkat,
  deterministik, dan berfokus pada artefak, sementara pemeriksaan live yang lebih lambat tetap berada di
  jalurnya sendiri agar tidak memperlambat atau memblokir publikasi
- Pemeriksaan rilis harus dijalankan dari ref workflow `main` agar
  logika workflow dan secret tetap kanonis
- Workflow tersebut menerima tag rilis yang sudah ada atau SHA commit `main`
  lengkap 40 karakter saat ini
- Dalam mode commit-SHA, workflow hanya menerima HEAD `origin/main` saat ini; gunakan
  tag rilis untuk commit rilis yang lebih lama
- Pemeriksaan awal khusus validasi `OpenClaw NPM Release` juga menerima SHA commit `main`
  lengkap 40 karakter saat ini tanpa memerlukan tag yang sudah di-push
- Jalur SHA tersebut hanya untuk validasi dan tidak dapat dipromosikan menjadi publikasi nyata
- Dalam mode SHA, workflow mensintesis `v<package.json version>` hanya untuk
  pemeriksaan metadata paket; publikasi nyata tetap memerlukan tag rilis nyata
- Kedua workflow menjaga jalur publikasi dan promosi nyata tetap pada GitHub-hosted
  runner, sementara jalur validasi non-mutasi dapat menggunakan runner Linux
  Blacksmith yang lebih besar
- Workflow tersebut menjalankan
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  menggunakan secret workflow `OPENAI_API_KEY` dan `ANTHROPIC_API_KEY`
- Pemeriksaan awal rilis npm tidak lagi menunggu jalur pemeriksaan rilis terpisah
- Jalankan `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (atau tag beta/koreksi yang sesuai) sebelum persetujuan
- Setelah npm publish, jalankan
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (atau versi beta/koreksi yang sesuai) untuk memverifikasi jalur instalasi registry
  yang dipublikasikan dalam prefix temp yang baru
- Otomasi rilis maintainer sekarang menggunakan preflight-then-promote:
  - npm publish nyata harus lolos `preflight_run_id` npm yang berhasil
  - rilis npm stable default ke `beta`
  - npm publish stable dapat menargetkan `latest` secara eksplisit melalui input workflow
  - promosi npm stable dari `beta` ke `latest` tetap tersedia sebagai mode manual eksplisit pada workflow tepercaya `OpenClaw NPM Release`
  - mode promosi tersebut tetap memerlukan `NPM_TOKEN` yang valid di environment `npm-release` karena pengelolaan npm `dist-tag` terpisah dari trusted publishing
  - `macOS Release` publik hanya untuk validasi
  - publikasi mac privat nyata harus lolos `preflight_run_id` dan `validate_run_id`
    private mac yang berhasil
  - jalur publikasi nyata mempromosikan artefak yang telah disiapkan alih-alih membangunnya
    lagi
- Untuk rilis koreksi stable seperti `YYYY.M.D-N`, verifier pasca-publikasi
  juga memeriksa jalur upgrade prefix temp yang sama dari `YYYY.M.D` ke `YYYY.M.D-N`
  sehingga koreksi rilis tidak dapat secara diam-diam meninggalkan instalasi global lama pada
  payload stable dasar
- Pemeriksaan awal rilis npm gagal secara tertutup kecuali tarball mencakup
  `dist/control-ui/index.html` dan payload `dist/control-ui/assets/` yang tidak kosong
  sehingga kita tidak mengirim dashboard browser kosong lagi
- Jika pekerjaan rilis menyentuh perencanaan CI, manifes waktu extension, atau
  matriks pengujian extension, hasil matriks workflow `checks-node-extensions`
  milik planner dari `.github/workflows/ci.yml` harus diregenerasi dan ditinjau
  sebelum persetujuan agar catatan rilis tidak menggambarkan tata letak CI yang basi
- Kesiapan rilis stable macOS juga mencakup surface updater:
  - rilis GitHub harus berakhir dengan `.zip`, `.dmg`, dan `.dSYM.zip` hasil paket
  - `appcast.xml` di `main` harus menunjuk ke zip stable baru setelah publikasi
  - aplikasi hasil paket harus tetap memiliki bundle id non-debug, URL feed Sparkle
    yang tidak kosong, dan `CFBundleVersion` pada atau di atas batas build Sparkle kanonis
    untuk versi rilis tersebut

## Input workflow NPM

`OpenClaw NPM Release` menerima input yang dikendalikan operator berikut:

- `tag`: tag rilis wajib seperti `v2026.4.2`, `v2026.4.2-1`, atau
  `v2026.4.2-beta.1`; saat `preflight_only=true`, ini juga dapat berupa SHA commit `main`
  lengkap 40 karakter saat ini untuk pemeriksaan awal yang hanya validasi
- `preflight_only`: `true` untuk hanya validasi/build/package, `false` untuk
  jalur publikasi nyata
- `preflight_run_id`: wajib pada jalur publikasi nyata agar workflow menggunakan kembali
  tarball yang sudah disiapkan dari pemeriksaan awal yang berhasil
- `npm_dist_tag`: tag target npm untuk jalur publikasi; default ke `beta`
- `promote_beta_to_latest`: `true` untuk melewati publish dan memindahkan build stable `beta`
  yang sudah dipublikasikan ke `latest`

`OpenClaw Release Checks` menerima input yang dikendalikan operator berikut:

- `ref`: tag rilis yang sudah ada atau SHA commit `main`
  lengkap 40 karakter saat ini yang akan divalidasi

Aturan:

- Tag stable dan koreksi dapat dipublikasikan ke `beta` atau `latest`
- Tag prarilis beta hanya dapat dipublikasikan ke `beta`
- Input SHA commit lengkap hanya diizinkan saat `preflight_only=true`
- Mode commit-SHA pemeriksaan rilis juga mewajibkan HEAD `origin/main` saat ini
- Jalur publikasi nyata harus menggunakan `npm_dist_tag` yang sama dengan yang digunakan selama pemeriksaan awal;
  workflow memverifikasi metadata tersebut sebelum publikasi dilanjutkan
- Mode promosi harus menggunakan tag stable atau koreksi, `preflight_only=false`,
  `preflight_run_id` kosong, dan `npm_dist_tag=beta`
- Mode promosi juga memerlukan `NPM_TOKEN` yang valid di environment `npm-release`
  karena `npm dist-tag add` tetap memerlukan auth npm biasa

## Urutan rilis npm stable

Saat membuat rilis npm stable:

1. Jalankan `OpenClaw NPM Release` dengan `preflight_only=true`
   - Sebelum ada tag, Anda dapat menggunakan SHA commit `main` lengkap saat ini untuk
     dry run validasi saja dari workflow pemeriksaan awal
2. Pilih `npm_dist_tag=beta` untuk alur beta-first normal, atau `latest` hanya
   ketika Anda memang menginginkan publikasi stable langsung
3. Jalankan `OpenClaw Release Checks` secara terpisah dengan tag yang sama atau
   SHA `main` lengkap saat ini ketika Anda menginginkan cakupan live prompt cache
   - Ini dipisahkan dengan sengaja agar cakupan live tetap tersedia tanpa
     menghubungkan kembali pemeriksaan yang berjalan lama atau mudah gagal ke workflow publikasi
4. Simpan `preflight_run_id` yang berhasil
5. Jalankan `OpenClaw NPM Release` lagi dengan `preflight_only=false`, `tag`
   yang sama, `npm_dist_tag` yang sama, dan `preflight_run_id` yang disimpan
6. Jika rilis masuk ke `beta`, jalankan `OpenClaw NPM Release` nanti dengan
   `tag` stable yang sama, `promote_beta_to_latest=true`, `preflight_only=false`,
   `preflight_run_id` kosong, dan `npm_dist_tag=beta` ketika Anda ingin memindahkan
   build yang telah dipublikasikan tersebut ke `latest`

Mode promosi tetap memerlukan persetujuan environment `npm-release` dan
`NPM_TOKEN` yang valid di environment tersebut.

Ini menjaga jalur publikasi langsung dan jalur promosi beta-first tetap
terdokumentasi dan terlihat oleh operator.

## Referensi publik

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainer menggunakan dokumentasi rilis privat di
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
untuk runbook yang sebenarnya.
