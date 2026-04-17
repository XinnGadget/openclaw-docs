---
read_when:
    - Mencari definisi kanal rilis publik
    - Mencari penamaan versi dan ritme rilis
summary: Kanal rilis publik, penamaan versi, dan ritme rilis
title: Kebijakan Rilis
x-i18n:
    generated_at: "2026-04-15T09:14:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88724307269ab783a9fbf8a0540fea198d8a3add68457f4e64d5707114fa518c
    source_path: reference/RELEASING.md
    workflow: 15
---

# Kebijakan Rilis

OpenClaw memiliki tiga jalur rilis publik:

- stable: rilis bertag yang dipublikasikan ke npm `beta` secara default, atau ke npm `latest` jika diminta secara eksplisit
- beta: tag prarilis yang dipublikasikan ke npm `beta`
- dev: head bergerak dari `main`

## Penamaan versi

- Versi rilis stable: `YYYY.M.D`
  - Git tag: `vYYYY.M.D`
- Versi rilis koreksi stable: `YYYY.M.D-N`
  - Git tag: `vYYYY.M.D-N`
- Versi prarilis beta: `YYYY.M.D-beta.N`
  - Git tag: `vYYYY.M.D-beta.N`
- Jangan tambahkan nol di depan bulan atau hari
- `latest` berarti rilis npm stable yang dipromosikan saat ini
- `beta` berarti target instalasi beta saat ini
- Rilis stable dan rilis koreksi stable dipublikasikan ke npm `beta` secara default; operator rilis dapat menargetkan `latest` secara eksplisit, atau mempromosikan build beta yang telah diverifikasi nanti
- Setiap rilis OpenClaw mengirimkan paket npm dan aplikasi macOS secara bersamaan

## Ritme rilis

- Rilis bergerak beta-terlebih-dahulu
- Stable menyusul hanya setelah beta terbaru divalidasi
- Prosedur rilis terperinci, persetujuan, kredensial, dan catatan pemulihan hanya untuk maintainer

## Pra-pemeriksaan rilis

- Jalankan `pnpm build && pnpm ui:build` sebelum `pnpm release:check` agar artefak rilis `dist/*` yang diharapkan dan bundle UI Control tersedia untuk langkah validasi pack
- Jalankan `pnpm release:check` sebelum setiap rilis bertag
- Pemeriksaan rilis sekarang berjalan dalam workflow manual terpisah:
  `OpenClaw Release Checks`
- Validasi runtime instalasi dan upgrade lintas OS dikirim dari workflow pemanggil privat
  `openclaw/releases-private/.github/workflows/openclaw-cross-os-release-checks.yml`,
  yang memanggil workflow publik yang dapat digunakan ulang
  `.github/workflows/openclaw-cross-os-release-checks-reusable.yml`
- Pemisahan ini disengaja: pertahankan jalur rilis npm yang sebenarnya tetap singkat,
  deterministik, dan berfokus pada artefak, sementara pemeriksaan live yang lebih lambat tetap berada di jalurnya sendiri agar tidak menunda atau memblokir publish
- Pemeriksaan rilis harus dikirim dari ref workflow `main` agar logika workflow dan secret tetap kanonis
- Workflow itu menerima tag rilis yang sudah ada atau SHA commit `main` 40 karakter penuh saat ini
- Dalam mode commit-SHA, workflow itu hanya menerima HEAD `origin/main` saat ini; gunakan tag rilis untuk commit rilis yang lebih lama
- Pra-pemeriksaan khusus validasi `OpenClaw NPM Release` juga menerima SHA commit `main` 40 karakter penuh saat ini tanpa memerlukan tag yang sudah didorong
- Jalur SHA tersebut hanya untuk validasi dan tidak dapat dipromosikan menjadi publish nyata
- Dalam mode SHA, workflow mensintesis `v<package.json version>` hanya untuk pemeriksaan metadata paket; publish nyata tetap memerlukan tag rilis yang nyata
- Kedua workflow mempertahankan jalur publish dan promosi nyata pada GitHub-hosted runners, sementara jalur validasi yang tidak memodifikasi dapat menggunakan Blacksmith Linux runners yang lebih besar
- Workflow itu menjalankan
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  menggunakan kedua secret workflow `OPENAI_API_KEY` dan `ANTHROPIC_API_KEY`
- Pra-pemeriksaan rilis npm tidak lagi menunggu jalur pemeriksaan rilis yang terpisah
- Jalankan `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (atau tag beta/koreksi yang sesuai) sebelum persetujuan
- Setelah npm publish, jalankan
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (atau versi beta/koreksi yang sesuai) untuk memverifikasi jalur instalasi registry yang dipublikasikan dalam temp prefix baru
- Otomatisasi rilis maintainer sekarang menggunakan preflight-then-promote:
  - publish npm nyata harus melewati npm `preflight_run_id` yang berhasil
  - rilis npm stable secara default menuju `beta`
  - publish npm stable dapat menargetkan `latest` secara eksplisit melalui input workflow
  - mutasi npm dist-tag berbasis token sekarang berada di
    `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
    demi keamanan, karena `npm dist-tag add` masih memerlukan `NPM_TOKEN` sementara repo publik mempertahankan publish khusus OIDC
  - `macOS Release` publik hanya untuk validasi
  - publish mac privat yang nyata harus melewati `preflight_run_id` dan `validate_run_id` mac privat yang berhasil
  - jalur publish nyata mempromosikan artefak yang sudah disiapkan alih-alih membangunnya lagi
- Untuk rilis koreksi stable seperti `YYYY.M.D-N`, verifier pascapublish juga memeriksa jalur upgrade temp-prefix yang sama dari `YYYY.M.D` ke `YYYY.M.D-N` agar koreksi rilis tidak diam-diam membuat instalasi global lama tetap berada pada payload stable dasar
- Pra-pemeriksaan rilis npm gagal secara fail-closed kecuali tarball menyertakan `dist/control-ui/index.html` dan payload `dist/control-ui/assets/` yang tidak kosong agar kita tidak mengirimkan dashboard browser kosong lagi
- `pnpm test:install:smoke` juga menegakkan anggaran `unpackedSize` npm pack pada tarball pembaruan kandidat, sehingga installer e2e menangkap pembengkakan pack yang tidak disengaja sebelum jalur publish rilis
- Jika pekerjaan rilis menyentuh perencanaan CI, manifest waktu ekstensi, atau matriks pengujian ekstensi, regenerasikan dan tinjau output matriks workflow `checks-node-extensions` milik planner dari `.github/workflows/ci.yml` sebelum persetujuan agar catatan rilis tidak menjelaskan tata letak CI yang kedaluwarsa
- Kesiapan rilis stable macOS juga mencakup permukaan updater:
  - GitHub release harus berakhir dengan `.zip`, `.dmg`, dan `.dSYM.zip` yang sudah dipaketkan
  - `appcast.xml` pada `main` harus menunjuk ke zip stable baru setelah publish
  - aplikasi yang dipaketkan harus mempertahankan bundle id non-debug, URL feed Sparkle yang tidak kosong, dan `CFBundleVersion` pada atau di atas batas build Sparkle kanonis untuk versi rilis tersebut

## Input workflow NPM

`OpenClaw NPM Release` menerima input yang dikendalikan operator berikut:

- `tag`: tag rilis yang wajib seperti `v2026.4.2`, `v2026.4.2-1`, atau
  `v2026.4.2-beta.1`; ketika `preflight_only=true`, ini juga dapat berupa
  SHA commit `main` 40 karakter penuh saat ini untuk pra-pemeriksaan khusus validasi
- `preflight_only`: `true` untuk validasi/build/package saja, `false` untuk
  jalur publish nyata
- `preflight_run_id`: wajib pada jalur publish nyata agar workflow menggunakan kembali tarball yang sudah disiapkan dari run pra-pemeriksaan yang berhasil
- `npm_dist_tag`: tag target npm untuk jalur publish; defaultnya `beta`

`OpenClaw Release Checks` menerima input yang dikendalikan operator berikut:

- `ref`: tag rilis yang sudah ada atau SHA commit `main` 40 karakter penuh saat ini untuk divalidasi

Aturan:

- Tag stable dan koreksi dapat dipublikasikan ke `beta` atau `latest`
- Tag prarilis beta hanya dapat dipublikasikan ke `beta`
- Input SHA commit penuh hanya diizinkan ketika `preflight_only=true`
- Mode commit-SHA pemeriksaan rilis juga memerlukan HEAD `origin/main` saat ini
- Jalur publish nyata harus menggunakan `npm_dist_tag` yang sama seperti saat pra-pemeriksaan; workflow memverifikasi metadata tersebut sebelum publish dilanjutkan

## Urutan rilis npm stable

Saat membuat rilis npm stable:

1. Jalankan `OpenClaw NPM Release` dengan `preflight_only=true`
   - Sebelum tag ada, Anda dapat menggunakan SHA commit `main` penuh saat ini untuk uji kering khusus validasi dari workflow pra-pemeriksaan
2. Pilih `npm_dist_tag=beta` untuk alur beta-terlebih-dahulu normal, atau `latest` hanya ketika Anda memang ingin publish stable langsung
3. Jalankan `OpenClaw Release Checks` secara terpisah dengan tag yang sama atau
   SHA `main` penuh saat ini ketika Anda menginginkan cakupan cache prompt live
   - Ini dipisahkan dengan sengaja agar cakupan live tetap tersedia tanpa
     menghubungkan kembali pemeriksaan yang berjalan lama atau tidak stabil ke workflow publish
4. Simpan `preflight_run_id` yang berhasil
5. Jalankan `OpenClaw NPM Release` lagi dengan `preflight_only=false`, `tag` yang sama, `npm_dist_tag` yang sama, dan `preflight_run_id` yang disimpan
6. Jika rilis mendarat di `beta`, gunakan workflow privat
   `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
   untuk mempromosikan versi stable tersebut dari `beta` ke `latest`
7. Jika rilis sengaja dipublikasikan langsung ke `latest` dan `beta`
   harus segera mengikuti build stable yang sama, gunakan workflow privat yang sama untuk mengarahkan kedua dist-tag ke versi stable tersebut, atau biarkan sinkronisasi self-healing terjadwalnya memindahkan `beta` nanti

Mutasi dist-tag berada di repo privat demi keamanan karena masih
memerlukan `NPM_TOKEN`, sementara repo publik mempertahankan publish khusus OIDC.

Ini menjaga agar jalur publish langsung dan jalur promosi beta-terlebih-dahulu tetap
terdokumentasi dan terlihat oleh operator.

## Referensi publik

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`.github/workflows/openclaw-cross-os-release-checks-reusable.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-cross-os-release-checks-reusable.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainer menggunakan dokumen rilis privat di
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
untuk runbook yang sebenarnya.
